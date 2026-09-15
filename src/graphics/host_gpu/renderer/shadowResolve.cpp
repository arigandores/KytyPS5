#include "graphics/host_gpu/renderer/shadowResolve.h"

#include "common/frameStats.h"
#include "common/gates.h"
#include "common/logging/log.h"
#include "graphics/host_gpu/renderer/pipeline/pipelineCache.h"
#include "graphics/host_gpu/renderer/renderContext.h"

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <memory>
#include <mutex>
#include <thread>
#include <vector>

#if defined(_WIN32)
#include <windows.h>
#endif

namespace Libs::Graphics::ShadowResolve {

namespace {

namespace FS = Common::FrameStats;

// Bounded multi-producer / multi-consumer ring (Vyukov): one producer here (the GuestGpu
// thread), K consumers. A consumer copies the used prefix of the job out of its cell before it
// releases the cell, so the producer never overwrites a job that is still being read.
constexpr uint32_t RingSize = 1024;
static_assert((RingSize & (RingSize - 1)) == 0);

struct Cell {
	std::atomic<uint64_t> sequence {0};
	Job                   job;
};

std::unique_ptr<Cell[]>          g_cells;
alignas(64) std::atomic<uint64_t> g_enqueue {0};
alignas(64) std::atomic<uint64_t> g_dequeue {0};
alignas(64) std::atomic<uint32_t> g_sleepers {0};
std::mutex                        g_mutex;   // worker sleep and thread start
std::condition_variable           g_wake;
std::vector<std::thread>          g_threads;
std::atomic<bool>                 g_stop {false};

void CopyJob(Job& to, const Job& from) {
	to.context      = from.context;
	to.image_count  = from.image_count;
	to.buffer_count = from.buffer_count;
	for (uint32_t i = 0; i < from.image_count; i++) {
		to.images[i] = from.images[i];
	}
	for (uint32_t i = 0; i < from.buffer_count; i++) {
		to.buffers[i] = from.buffers[i];
	}
}

bool TryPush(const Job& job) {
	auto pos = g_enqueue.load(std::memory_order_relaxed);
	for (;;) {
		auto&      cell = g_cells[pos & (RingSize - 1)];
		const auto seq  = cell.sequence.load(std::memory_order_acquire);
		const auto diff = static_cast<int64_t>(seq) - static_cast<int64_t>(pos);
		if (diff == 0) {
			if (g_enqueue.compare_exchange_weak(pos, pos + 1, std::memory_order_relaxed)) {
				CopyJob(cell.job, job);
				cell.sequence.store(pos + 1, std::memory_order_release);
				return true;
			}
		} else if (diff < 0) {
			return false; // full
		} else {
			pos = g_enqueue.load(std::memory_order_relaxed);
		}
	}
}

bool TryPop(Job& job) {
	auto pos = g_dequeue.load(std::memory_order_relaxed);
	for (;;) {
		auto&      cell = g_cells[pos & (RingSize - 1)];
		const auto seq  = cell.sequence.load(std::memory_order_acquire);
		const auto diff = static_cast<int64_t>(seq) - static_cast<int64_t>(pos + 1);
		if (diff == 0) {
			if (g_dequeue.compare_exchange_weak(pos, pos + 1, std::memory_order_relaxed)) {
				CopyJob(job, cell.job);
				cell.sequence.store(pos + RingSize, std::memory_order_release);
				return true;
			}
		} else if (diff < 0) {
			return false; // empty
		} else {
			pos = g_dequeue.load(std::memory_order_relaxed);
		}
	}
}

bool Empty() {
	return g_dequeue.load(std::memory_order_acquire) >= g_enqueue.load(std::memory_order_acquire);
}

void Pause() {
#if defined(_WIN32)
	YieldProcessor();
#elif defined(__x86_64__) || defined(__i386__)
	__builtin_ia32_pause();
#else
	std::atomic_signal_fence(std::memory_order_seq_cst);
#endif
}

void Worker(uint32_t index) {
#if defined(_WIN32)
	SetThreadDescription(GetCurrentThread(), L"ShadowResolve");
#endif
	thread_local Job job;
	uint32_t         idle = 0;
	for (;;) {
		if (g_stop.load(std::memory_order_relaxed)) {
			return;
		}
		if (index >= Common::Gates::Value(Common::Gates::Knob::ShadowResolve)) {
			// The knob shrank: this worker is out of the experiment until it grows again.
			std::this_thread::sleep_for(std::chrono::milliseconds(5));
			continue;
		}
		if (TryPop(job)) {
			idle = 0;
			DrawAheadApplyPin(false); // knob "dapin": next to the GuestGpu thread, like M1
			Run(job, false);
			continue;
		}
		// About 0.5 ms of polling, then sleep, as an M1 worker does (a condition variable), so
		// that idle workers do not burn cores and pull the GuestGpu thread's clock down.
		if (++idle < 1024) {
			for (int i = 0; i < 16; i++) {
				Pause();
			}
			continue;
		}
		// Nothing for a while (a frame boundary, a scene without draws): sleep until the
		// producer wakes the sleepers or 1 ms passes.
		std::unique_lock<std::mutex> lock(g_mutex);
		g_sleepers.fetch_add(1, std::memory_order_seq_cst);
		std::atomic_thread_fence(std::memory_order_seq_cst);
		if (Empty() && !g_stop.load(std::memory_order_relaxed)) {
			g_wake.wait_for(lock, std::chrono::milliseconds(1));
		}
		g_sleepers.fetch_sub(1, std::memory_order_seq_cst);
		idle = 512;
	}
}

void Start(uint32_t wanted) {
	std::lock_guard<std::mutex> lock(g_mutex);
	if (g_cells == nullptr) {
		g_cells = std::make_unique<Cell[]>(RingSize);
		for (uint32_t i = 0; i < RingSize; i++) {
			g_cells[i].sequence.store(i, std::memory_order_relaxed);
		}
	}
	while (g_threads.size() < wanted) {
		const auto index = static_cast<uint32_t>(g_threads.size());
		g_threads.emplace_back([index] { Worker(index); });
		LOGF("ShadowResolve: worker %u started\n", index);
	}
}

} // namespace

void Run(const Job& job, bool inline_run) {
	const bool counting = FS::Enabled();
	const auto t0       = counting ? FS::NowNs() : 0;
	const auto mask     = Common::Gates::Value(Common::Gates::Knob::ShadowMask);
	auto&      textures = job.context->GetTextureCache();
	auto&      buffers  = job.context->GetBufferCache();
	uint64_t   gone = 0, stale = 0, slow = 0, view = 0, fast = 0;
	for (uint32_t i = 0; (mask & 1u) != 0 && i < job.image_count; i++) {
		switch (textures.ShadowProbe(job.images[i])) {
			case TextureCache::ShadowImageAnswer::Gone: gone++; break;
			case TextureCache::ShadowImageAnswer::Stale: stale++; break;
			case TextureCache::ShadowImageAnswer::Slow: slow++; break;
			case TextureCache::ShadowImageAnswer::View: view++; break;
			case TextureCache::ShadowImageAnswer::Fast: fast++; break;
		}
	}
	uint64_t none = 0, memo = 0, epoch = 0, stream = 0, bslow = 0, bnew = 0;
	for (uint32_t i = 0; (mask & 2u) != 0 && i < job.buffer_count; i++) {
		const auto& q = job.buffers[i];
		switch (buffers.ShadowProbe(q.address, q.size, q.id, q.written)) {
			case BufferCache::ShadowBufferAnswer::None: none++; break;
			case BufferCache::ShadowBufferAnswer::Fast: memo++; break;
			case BufferCache::ShadowBufferAnswer::Epoch: epoch++; break;
			case BufferCache::ShadowBufferAnswer::Stream: stream++; break;
			case BufferCache::ShadowBufferAnswer::Slow: bslow++; break;
			case BufferCache::ShadowBufferAnswer::New: bnew++; break;
		}
	}
	if (!counting) {
		return;
	}
	FS::Add(FS::Counter::ShadowJobs, 1);
	FS::Add(FS::Counter::ShadowImages, job.image_count);
	FS::Add(FS::Counter::ShadowImgGone, gone);
	FS::Add(FS::Counter::ShadowImgStale, stale);
	FS::Add(FS::Counter::ShadowImgSlow, slow);
	FS::Add(FS::Counter::ShadowImgView, view);
	FS::Add(FS::Counter::ShadowImgFast, fast);
	FS::Add(FS::Counter::ShadowBuffers, job.buffer_count);
	FS::Add(FS::Counter::ShadowBufNone, none);
	FS::Add(FS::Counter::ShadowBufFast, memo);
	FS::Add(FS::Counter::ShadowBufEpoch, epoch);
	FS::Add(FS::Counter::ShadowBufStream, stream);
	FS::Add(FS::Counter::ShadowBufSlow, bslow);
	FS::Add(FS::Counter::ShadowBufNew, bnew);
	FS::Add(inline_run ? FS::Counter::ShadowInlineNs : FS::Counter::ShadowWorkerNs,
	        FS::NowNs() - t0);
}

bool Push(const Job& job) {
	const auto wanted = Common::Gates::Value(Common::Gates::Knob::ShadowResolve);
	if (g_threads.size() < wanted) {
		Start(wanted);
	}
	if (!TryPush(job)) {
		return false;
	}
	// A notify per push is a system call per draw (desert: 420 us a frame, 7 % of the thread,
	// when the workers sleep between draws). Sleepers are woken at most every 64th push; the
	// 1 ms timeout of their wait covers the rest. Latency is not what this experiment measures.
	static uint32_t pushes = 0; // producer thread only
	std::atomic_thread_fence(std::memory_order_seq_cst);
	if ((++pushes & 63u) == 0 && g_sleepers.load(std::memory_order_seq_cst) != 0) {
		std::lock_guard<std::mutex> lock(g_mutex);
		g_wake.notify_all();
		FS::Add(FS::Counter::ShadowWakes, 1);
	}
	return true;
}

void Stop() {
	{
		std::lock_guard<std::mutex> lock(g_mutex);
		g_stop.store(true, std::memory_order_relaxed);
		g_wake.notify_all();
	}
	for (auto& thread: g_threads) {
		if (thread.joinable()) {
			thread.join();
		}
	}
	g_threads.clear();
}

} // namespace Libs::Graphics::ShadowResolve
