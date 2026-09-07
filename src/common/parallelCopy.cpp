#include "common/parallelCopy.h"

#include <algorithm>
#include <atomic>
#include <condition_variable>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <thread>
#include <vector>

namespace Common {

namespace {

constexpr size_t CHUNK_BYTES = 1u << 20u;

class CopyPool final {
public:
	static CopyPool& Instance() {
		static CopyPool pool;
		return pool;
	}

	[[nodiscard]] bool Enabled() const { return !m_workers.empty(); }

	void Copy(uint8_t* dst, const uint8_t* src, size_t size) {
		const size_t chunks = (size + CHUNK_BYTES - 1) / CHUNK_BYTES;
		{
			std::lock_guard lock(m_mutex);
			m_dst    = dst;
			m_src    = src;
			m_size.store(size, std::memory_order_relaxed);
			m_chunks.store(chunks, std::memory_order_relaxed);
			m_done.store(0, std::memory_order_relaxed);
			m_next.store(0, std::memory_order_release); // publishes dst/src/size/chunks
			m_generation++;
		}
		m_wake.notify_all();
		Work();
		// Wait for the chunks other threads took.
		std::unique_lock lock(m_mutex);
		m_finished.wait(lock, [&] { return m_done.load(std::memory_order_acquire) == chunks; });
	}

private:
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
		uint64_t seen = 0;
		for (;;) {
			{
				std::unique_lock lock(m_mutex);
				m_wake.wait(lock, [&] { return m_stop || m_generation != seen; });
				if (m_stop) {
					return;
				}
				seen = m_generation;
			}
			Work();
		}
	}

	// Takes chunks until none are left; the last finisher signals the caller.
	void Work() {
		for (;;) {
			const auto index  = m_next.fetch_add(1, std::memory_order_acq_rel);
			const auto chunks = m_chunks.load(std::memory_order_relaxed);
			if (index >= chunks) {
				return;
			}
			const auto offset = index * CHUNK_BYTES;
			const auto bytes  = std::min(CHUNK_BYTES, m_size.load(std::memory_order_relaxed) - offset);
			std::memcpy(m_dst + offset, m_src + offset, bytes);
			if (m_done.fetch_add(1, std::memory_order_acq_rel) + 1 == chunks) {
				std::lock_guard lock(m_mutex);
				m_finished.notify_all();
			}
		}
	}

	std::vector<std::thread>  m_workers;
	std::mutex                m_mutex;
	std::condition_variable   m_wake;
	std::condition_variable   m_finished;
	bool                      m_stop       = false;
	uint64_t                  m_generation = 0;
	uint8_t*                  m_dst        = nullptr;
	const uint8_t*            m_src        = nullptr;
	std::atomic<size_t>       m_size {0};
	std::atomic<size_t>       m_chunks {0};
	std::atomic<size_t>       m_next {0};
	std::atomic<size_t>       m_done {0};
};

} // namespace

void ParallelMemcpy(void* dst, const void* src, size_t size) {
	if (size < PARALLEL_COPY_MIN_BYTES || !CopyPool::Instance().Enabled()) {
		std::memcpy(dst, src, size);
		return;
	}
	// One copy at a time (the pool is shared state); callers are the GuestGpu thread today.
	static std::mutex serial;
	std::lock_guard   lock(serial);
	CopyPool::Instance().Copy(static_cast<uint8_t*>(dst), static_cast<const uint8_t*>(src), size);
}

} // namespace Common
