#include "common/parallelCopy.h"

#include <algorithm>
#include <atomic>
#include <condition_variable>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <mutex>
#include <thread>
#include <vector>

namespace Common {

namespace {

constexpr size_t CHUNK_BYTES = 1u << 20u;

// A small pool of copy threads with a FIFO of 1 MiB chunks. AsyncMemcpy queues chunks and
// returns; WaitAsyncCopies (called before every vkQueueSubmit) helps with the queue and blocks
// until it is empty. Everything queued is complete when WaitAsyncCopies returns, so a caller
// that needs synchronous semantics (ParallelMemcpy) just queues and waits.
class CopyPool final {
public:
	static CopyPool& Instance() {
		static CopyPool pool;
		return pool;
	}

	[[nodiscard]] bool Enabled() const { return !m_workers.empty(); }

	void Enqueue(uint8_t* dst, const uint8_t* src, size_t size) {
		const size_t chunks = (size + CHUNK_BYTES - 1) / CHUNK_BYTES;
		{
			std::lock_guard lock(m_mutex);
			for (size_t i = 0; i < chunks; i++) {
				const auto offset = i * CHUNK_BYTES;
				m_jobs.push_back({dst + offset, src + offset, std::min(CHUNK_BYTES, size - offset)});
			}
			m_pending.fetch_add(chunks, std::memory_order_acq_rel);
		}
		if (chunks == 1) {
			m_wake.notify_one();
		} else {
			m_wake.notify_all();
		}
	}

	void WaitAll() {
		if (m_pending.load(std::memory_order_acquire) == 0) {
			return;
		}
		// Help with what is left, then wait for chunks other threads are still copying.
		Work();
		std::unique_lock lock(m_mutex);
		m_finished.wait(lock, [&] { return m_pending.load(std::memory_order_acquire) == 0; });
	}

	[[nodiscard]] size_t Pending() const { return m_pending.load(std::memory_order_acquire); }

private:
	struct Job {
		uint8_t*       dst;
		const uint8_t* src;
		size_t         size;
	};

	CopyPool() {
		const char* env = std::getenv("KYTY_PARALLEL_COPY");
		if (env != nullptr && env[0] == '0') {
			return;
		}
		const auto hw      = std::thread::hardware_concurrency();
		const auto workers = std::clamp<unsigned>(hw / 2u, 2u, 7u);
		m_workers.reserve(workers);
		for (unsigned i = 0; i < workers; i++) {
			m_workers.emplace_back([this] { WorkerLoop(); });
		}
	}

	~CopyPool() {
		{
			std::lock_guard lock(m_mutex);
			m_stop = true;
		}
		m_wake.notify_all();
		for (auto& worker: m_workers) {
			worker.join();
		}
	}

	void WorkerLoop() {
		for (;;) {
			{
				std::unique_lock lock(m_mutex);
				m_wake.wait(lock, [&] { return m_stop || !m_jobs.empty(); });
				if (m_stop) {
					return;
				}
			}
			Work();
		}
	}

	// Takes chunks until the queue is empty; the finisher of the last chunk wakes the waiters.
	void Work() {
		for (;;) {
			Job job {};
			{
				std::lock_guard lock(m_mutex);
				if (m_jobs.empty()) {
					return;
				}
				job = m_jobs.front();
				m_jobs.pop_front();
			}
			std::memcpy(job.dst, job.src, job.size);
			if (m_pending.fetch_sub(1, std::memory_order_acq_rel) == 1) {
				std::lock_guard lock(m_mutex);
				m_finished.notify_all();
			}
		}
	}

	std::vector<std::thread> m_workers;
	std::mutex               m_mutex;
	std::condition_variable  m_wake;
	std::condition_variable  m_finished;
	bool                     m_stop = false;
	std::deque<Job>          m_jobs;
	std::atomic<size_t>      m_pending {0};
};

bool AsyncCopyEnabled() {
	static const bool enabled = [] {
		const char* env = std::getenv("KYTY_ASYNC_COPY");
		return env == nullptr || env[0] != '0';
	}();
	return enabled;
}

} // namespace

void ParallelMemcpy(void* dst, const void* src, size_t size) {
	if (size < PARALLEL_COPY_MIN_BYTES || !CopyPool::Instance().Enabled()) {
		std::memcpy(dst, src, size);
		return;
	}
	auto& pool = CopyPool::Instance();
	pool.Enqueue(static_cast<uint8_t*>(dst), static_cast<const uint8_t*>(src), size);
	pool.WaitAll();
}

void AsyncMemcpy(void* dst, const void* src, size_t size) {
	if (size < ASYNC_COPY_MIN_BYTES || !CopyPool::Instance().Enabled()) {
		std::memcpy(dst, src, size);
		return;
	}
	if (!AsyncCopyEnabled()) {
		ParallelMemcpy(dst, src, size);
		return;
	}
	CopyPool::Instance().Enqueue(static_cast<uint8_t*>(dst), static_cast<const uint8_t*>(src),
	                             size);
}

void WaitAsyncCopies() {
	if (CopyPool::Instance().Enabled()) {
		CopyPool::Instance().WaitAll();
	}
}

size_t PendingAsyncCopies() {
	return CopyPool::Instance().Enabled() ? CopyPool::Instance().Pending() : 0;
}

} // namespace Common
