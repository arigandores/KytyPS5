#include "common/parallelCopy.h"

#include <algorithm>
#include <atomic>
#include <condition_variable>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <mutex>
#include <set>
#include <thread>
#include <vector>

namespace Common {

namespace {

constexpr size_t CHUNK_BYTES = 1u << 20u;

// A small pool of copy threads with a FIFO of 1 MiB chunks. AsyncMemcpy queues chunks and
// returns; WaitAsyncCopies helps with the queue and blocks until it is empty. Everything queued
// is complete when WaitAsyncCopies returns, so a caller that needs synchronous semantics
// (ParallelMemcpy) just queues and waits. Chunks are numbered in queue order and the pool keeps
// the completed low-water mark, so a GPU submit can wait for "everything queued before me"
// through a host-signalled timeline semaphore instead of blocking the GuestGpu thread.
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
				m_jobs.push_back({dst + offset, src + offset, std::min(CHUNK_BYTES, size - offset),
				                  m_sequence++});
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

	[[nodiscard]] uint64_t Sequence() {
		std::lock_guard lock(m_mutex);
		return m_sequence;
	}

	[[nodiscard]] uint64_t Completed() const { return m_completed.load(std::memory_order_acquire); }

	void AddSignal(void (*signal)(uint64_t, void*), void* user) {
		std::lock_guard lock(m_signal_mutex);
		m_signals.push_back({signal, user});
	}

	void RemoveSignal(void (*signal)(uint64_t, void*), void* user) {
		std::lock_guard lock(m_signal_mutex);
		std::erase_if(m_signals, [&](const Signal& s) {
			return s.signal == signal && s.user == user;
		});
	}

	// True if every chunk below `sequence` has already landed; otherwise a signal is issued
	// once the completed mark reaches it.
	bool RequestSignal(uint64_t sequence) {
		std::lock_guard lock(m_mutex);
		if (m_completed.load(std::memory_order_acquire) >= sequence) {
			return true;
		}
		if (m_requests.empty() || m_requests.back() < sequence) {
			m_requests.push_back(sequence);
		}
		return false;
	}

private:
	struct Job {
		uint8_t*       dst;
		const uint8_t* src;
		size_t         size;
		uint64_t       sequence;
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
			Complete(job.sequence);
			if (m_pending.fetch_sub(1, std::memory_order_acq_rel) == 1) {
				std::lock_guard lock(m_mutex);
				m_finished.notify_all();
			}
		}
	}

	// Advances the completed mark (chunks finish out of order across threads) and issues the
	// host signal when the mark crosses a requested value. Signals are serialized under
	// m_signal_mutex so the semaphore only ever sees increasing values.
	void Complete(uint64_t sequence) {
		bool     signal = false;
		uint64_t mark   = 0;
		{
			std::lock_guard lock(m_mutex);
			auto completed = m_completed.load(std::memory_order_relaxed);
			if (sequence == completed) {
				completed++;
				while (!m_done_ahead.empty() && *m_done_ahead.begin() == completed) {
					m_done_ahead.erase(m_done_ahead.begin());
					completed++;
				}
				m_completed.store(completed, std::memory_order_release);
			} else {
				m_done_ahead.insert(sequence);
				return;
			}
			while (!m_requests.empty() && m_requests.front() <= completed) {
				m_requests.pop_front();
				signal = true;
			}
			mark = completed;
		}
		if (signal) {
			std::lock_guard lock(m_signal_mutex);
			if (mark > m_signaled) {
				m_signaled = mark;
				for (const auto& s: m_signals) {
					s.signal(mark, s.user);
				}
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
	uint64_t                 m_sequence = 0;  // next chunk number (m_mutex)
	std::atomic<uint64_t>    m_completed {0}; // every chunk below it has landed
	std::set<uint64_t>       m_done_ahead;    // finished chunks above m_completed (m_mutex)
	std::deque<uint64_t>     m_requests;      // ascending sequence values awaiting a signal
	struct Signal {
		void (*signal)(uint64_t, void*);
		void* user;
	};
	std::mutex          m_signal_mutex;
	std::vector<Signal> m_signals;
	uint64_t            m_signaled = 0;
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

uint64_t AsyncCopySequence() {
	return CopyPool::Instance().Enabled() ? CopyPool::Instance().Sequence() : 0;
}

uint64_t AsyncCopyCompleted() {
	return CopyPool::Instance().Enabled() ? CopyPool::Instance().Completed() : 0;
}

void AddAsyncCopySignal(void (*signal)(uint64_t, void*), void* user) {
	CopyPool::Instance().AddSignal(signal, user);
}

void RemoveAsyncCopySignal(void (*signal)(uint64_t, void*), void* user) {
	CopyPool::Instance().RemoveSignal(signal, user);
}

bool RequestAsyncCopySignal(uint64_t sequence) {
	return !CopyPool::Instance().Enabled() || CopyPool::Instance().RequestSignal(sequence);
}

} // namespace Common
