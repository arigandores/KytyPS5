#include "common/parallelCopy.h"

#include "common/frameStats.h"
#include "common/gates.h"

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

#if defined(_M_X64) || defined(__x86_64__)
#include <immintrin.h>
#endif

namespace Common {

namespace {

constexpr size_t CHUNK_BYTES = 1u << 20u;

// Session 92, knob "copywake" = 2: how long a worker whose queue ran dry stays runnable
// before it goes back to m_wake.wait.  The BUDGET is in time, not in iterations - the core
// clock of this machine moves, so an iteration budget would be a different spin in every
// run - but SPIN_ITERATION_CAP below is a hard backstop, because a loop whose only exit
// depends on a clock hangs wherever that clock reads 0.
// 20 us is chosen against the price of the thing it removes: the wake is 93.80 % of
// stg_pool_ns at 4.27 us a region, and that is what it costs GuestGpu to bring a SLEEPING
// worker back through the kernel, while a notify_one that finds the worker awake is tens
// of nanoseconds.  So catching ONE region in five repays the 20 us of a worker core with
// 4.27 us off the serial thread - the trade this programme wants, because GuestGpu is the
// thread the frame waits for and the copy workers are not.  The burn has a hard ceiling
// of 20 us x (workers woken) per drain of the pool and it is NOT modelled: stg_spin_ns is
// the measured total and stg_spin_hit the part that caught a queued chunk.
constexpr uint64_t WORKER_SPIN_NS = 20000;

// The clock is kept off the pause loop: the queue is re-read EVERY iteration - that is the
// latency this spin buys - and the deadline only every 16.  A pause is about 140 cycles on
// recent Intel and a few on AMD, so the deadline is overrun by at most about 1 us of 20.
constexpr uint32_t SPIN_CLOCK_EVERY = 16;

// Backstop for the spin, so that it terminates even where NowNs() has no clock to read.
// Sized well above what 20 us of pauses can reach on any plausible core (a pause is a few
// cycles at worst, so 20 us is under ~100k iterations at 5 GHz), which keeps it inert on
// Windows and makes it the only exit elsewhere.
constexpr uint64_t SPIN_ITERATION_CAP = 1u << 20u;

void CpuPause() noexcept {
#if defined(_M_X64) || defined(__x86_64__)
	_mm_pause();
#else
	std::this_thread::yield();
#endif
}

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

	// Session 92, gate "stglap" (measurement only, default 0).  The gate and the queue
	// depth are read BEFORE the first timestamp, so neither the gate read nor the atomic
	// load can land inside a measured interval.  t1 is DELIBERATELY the shared boundary of
	// two adjacent intervals: a second mark there would open a gap belonging to neither,
	// and the two phases would no longer sum to t2 - t0.  The consequence is stated rather
	// than hidden - the price of taking t1 sits inside stg_wake_ns, and by session 88's
	// control C8 a mark followed by dependent work is dearer than one followed by
	// independent work, so stg_wake_ns carries that asymmetry and stg_lock_ns does not.
	// At stglap = 0 this path takes no timestamp, no extra atomic read and no Add.
	// Both callers of AsyncMemcpy arrive here - the buffer uploads of
	// BufferCache::UploadCopies and the image "staging:no-owner" path - and the counters
	// below do NOT separate them.
	void Enqueue(uint8_t* dst, const uint8_t* src, size_t size) {
		const bool     lap   = Gates::Enabled(Gates::Gate::StageLap) && FrameStats::Enabled();
		const uint64_t depth = lap ? static_cast<uint64_t>(Pending()) : 0;
		const uint64_t t0    = lap ? FrameStats::NowNs() : 0;
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
		const uint64_t t1 = lap ? FrameStats::NowNs() : 0;
		// Session 92.  This notify is 93.80 % of the price of the hand-over (173.5 of
		// 185.0 us a frame, 4.27 us a region): it wakes a SLEEPING thread through the
		// kernel, and the pool really is asleep here (stg_q / stg_pool_n = 0.430).  About
		// 28.8 % of the regions carry more than one chunk and took notify_all, which wakes
		// ALL 2-7 workers for at most `chunks` jobs.  Knob "copywake" >= 1 replaces that
		// broadcast with at most one notify_one per chunk.  IT CANNOT LOSE WORK: any single
		// woken worker drains the whole FIFO inside Work(), so the number of wake-ups only
		// decides how much parallelism this enqueue asks for, never whether the queue is
		// served - and the workers that are NOT woken are still in m_wake.wait, whose
		// predicate is re-evaluated under this same mutex on the next notify.
		// The knob is read HERE, on the enqueue, so a schedule can flip it between arms of
		// one run: the branch is chosen per enqueue and nothing about it outlives the call.
		// At copywake = 0 the branch taken is the notify_all this code always took and the
		// chunks == 1 path is untouched in every mode.  What the DEFAULT pays, in full:
		// one relaxed load here on the multi-chunk branch, one more per worker drain in
		// WorkerLoop, and the stglap read above - no clock, no Add, no spin.
		if (chunks == 1) {
			m_wake.notify_one();
		} else if (Gates::Value(Gates::Knob::CopyWake) == 0) {
			m_wake.notify_all();
		} else {
			// max(1, ...) is not decoration: m_wake_workers is 0 when the pool has no
			// threads, and a zero here would publish a job and wake nobody - a real lost
			// wake-up.  That state is unreachable today only because every caller is
			// guarded by Enabled(), which is exactly the kind of invariant that a future
			// caller breaks silently.
			const size_t wake = std::max<size_t>(1, std::min(chunks, m_wake_workers));
			for (size_t i = 0; i < wake; i++) {
				m_wake.notify_one();
			}
		}
		if (lap) {
			const uint64_t t2 = FrameStats::NowNs();
			FrameStats::Add(FrameStats::Counter::StagingLockNs, t1 - t0);
			FrameStats::Add(FrameStats::Counter::StagingWakeNs, t2 - t1);
			// The SAME interval again, split by the branch that was taken.  stg_wake_ns is
			// left whole above, so stg_wake1_ns + stg_waken_ns == stg_wake_ns and
			// stg_wake1_n + stg_waken_n == the enqueues counted here, both by construction.
			if (chunks == 1) {
				FrameStats::Add(FrameStats::Counter::StagingWakeOneNs, t2 - t1);
				FrameStats::Add(FrameStats::Counter::StagingWakeOneCalls, 1);
			} else {
				FrameStats::Add(FrameStats::Counter::StagingWakeManyNs, t2 - t1);
				FrameStats::Add(FrameStats::Counter::StagingWakeManyCalls, 1);
			}
			FrameStats::Add(FrameStats::Counter::StagingQueueDepth, depth);
			FrameStats::Add(FrameStats::Counter::StagingChunks, chunks);
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

	[[nodiscard]] uint64_t Signaled() {
		std::lock_guard lock(m_signal_mutex);
		return m_signaled;
	}

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
		// Only the COUNT is fixed here - the threads are created once.  Knob "copywake"
		// itself is read at every decision (Enqueue and each drain in WorkerLoop) so that
		// a gate schedule can flip it between arms of one run; see m_wake_workers.
		m_wake_workers = static_cast<size_t>(workers);
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
				// THE ONLY PLACE THIS THREAD DECIDES TO SLEEP, in every mode of "copywake".
				// The predicate is evaluated under m_mutex - the mutex Enqueue holds while it
				// pushes - so a job queued at any moment, INCLUDING one queued while this
				// thread was spinning in SpinForWork below, is seen here and the wait returns
				// without blocking.  That is why the spin cannot lose a wake-up: it never
				// sleeps and it never skips this line, it only delays arriving at it.
				m_wake.wait(lock, [&] { return m_stop || !m_jobs.empty(); });
				if (m_stop) {
					return;
				}
			}
			Work();
			// Read per drain, not per process, for the same reason as the notify branch:
			// a schedule must be able to flip it between arms.  Flipping it mid-run is
			// safe because the spin owns no state - a worker that stops spinning simply
			// arrives at the wait above sooner, and one that starts spinning arrives
			// later.  Neither changes what any other thread observes.
			if (Gates::Value(Gates::Knob::CopyWake) >= 2) {
				SpinForWork();
			}
		}
	}

	// Knob "copywake" = 2.  Work() has just emptied the queue; instead of returning to
	// m_wake.wait at once, stay runnable for WORKER_SPIN_NS.  The saving is on the OTHER
	// thread: stg_wake_ns is 93.80 % of the hand-over because notify has to bring a
	// thread back from a kernel wait, and a notify_one that finds this thread awake
	// costs GuestGpu tens of nanoseconds instead of about 4.27 us.
	// IT IS A LATENCY OPTIMISATION AND NOTHING ELSE, and it is built so that it CANNOT
	// change what any other thread observes:
	//   * it pops nothing and copies nothing.  The only shared state it touches is ONE
	//     acquire load of m_pending; m_pending, m_sequence, m_completed, m_done_ahead,
	//     m_requests and m_signaled are never written here, so the timeline-semaphore
	//     path (RequestAsyncCopySignal / Complete / SignalIdle) is unchanged;
	//   * it never decides to sleep.  However it ends, control returns to the wait
	//     above, which re-evaluates the predicate UNDER m_mutex - so a chunk queued
	//     during the spin is served, and a notify that arrived during the spin and
	//     found no waiter has cost nothing;
	//   * shutdown is delayed by at most WORKER_SPIN_NS per worker.  The destructor
	//     sets m_stop under m_mutex and notifies; a spinning worker misses that notify,
	//     then takes the mutex, and the predicate is already true, so it returns;
	//   * WaitAsyncCopies is untouched.  WaitAll still helps with Work() and still
	//     blocks on m_finished until m_pending reads 0, and the finisher of the last
	//     chunk still notifies m_finished from Work() under m_mutex.
	// The exit test is m_pending RISING above the lowest value this spin has seen, not
	// m_pending != 0: completions only lower it and enqueues only raise it, so tracking
	// the running minimum finds a NEW chunk instead of firing immediately whenever some
	// other worker still holds one.  A rise hidden by a simultaneous completion is seen
	// one iteration later or not at all - which costs latency only, because the wait
	// predicate under the lock is the backstop.
	void SpinForWork() {
		const uint64_t start    = FrameStats::NowNs();
		const uint64_t deadline = start + WORKER_SPIN_NS;
		size_t         low      = m_pending.load(std::memory_order_acquire);
		bool           hit      = false;
		uint32_t       n        = 0;
		// The iteration cap is a BACKSTOP, not the budget.  FrameStats::NowNs() is
		// implemented only on Windows and returns a constant 0 everywhere else
		// (frameStats.cpp:197-211), so on any other platform `NowNs() >= deadline` is
		// `0 >= 20000` and never fires: the spin would never end, and the destructor -
		// which sets m_stop but cannot raise m_pending - would hang in join() forever.
		// A time budget that depends on a clock must not be the only way out of a loop.
		uint64_t iterations = 0;
		for (;;) {
			const size_t pending = m_pending.load(std::memory_order_acquire);
			if (pending > low) {
				hit = true;
				break;
			}
			low = pending;
			CpuPause();
			if (++iterations >= SPIN_ITERATION_CAP) {
				break;
			}
			if (++n >= SPIN_CLOCK_EVERY) {
				n = 0;
				if (FrameStats::NowNs() >= deadline) {
					break;
				}
			}
		}
		// The price of the spin, on a worker core.  Gate "stglap" only.  The two clock
		// reads below are the counter's; the loop itself takes one at entry and one per
		// SPIN_CLOCK_EVERY pauses, which is where most of a spin's own cost sits.
		if (Gates::Enabled(Gates::Gate::StageLap) && FrameStats::Enabled()) {
			FrameStats::Add(FrameStats::Counter::StagingSpinNs, FrameStats::NowNs() - start);
			if (hit) {
				FrameStats::Add(FrameStats::Counter::StagingSpinHits, 1);
			}
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
				if (Gates::Enabled(Gates::Gate::AsyncCopyIdleSignal)) {
					SignalIdle();
				}
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

	// Gate "acopyidle": the last queued chunk landed, so publish the completed mark even
	// when no recorded request crossed it. Complete() only signals on a request boundary,
	// which makes the liveness of an already submitted batch depend on the m_requests /
	// m_signaled bookkeeping; a submit whose request did not survive it would wait on the
	// queue for a value the pool never sends again, and every batch behind it - including
	// the presents - stops with it. The mark is a prefix that really landed and it only
	// grows, so an extra signal can never release a batch too early; at most one extra
	// vkSignalSemaphore is issued per drain of the pool.
	void SignalIdle() {
		uint64_t mark = 0;
		{
			std::lock_guard lock(m_mutex);
			if (!m_jobs.empty()) {
				// Queued again while this chunk was copied: the new tail signals instead.
				return;
			}
			mark = m_completed.load(std::memory_order_acquire);
			while (!m_requests.empty() && m_requests.front() <= mark) {
				m_requests.pop_front();
			}
		}
		std::lock_guard lock(m_signal_mutex);
		if (mark > m_signaled) {
			m_signaled = mark;
			for (const auto& s: m_signals) {
				s.signal(mark, s.user);
			}
		}
	}

	std::vector<std::thread> m_workers;
	std::mutex               m_mutex;
	std::condition_variable  m_wake;
	std::condition_variable  m_finished;
	bool                     m_stop = false;
	std::deque<Job>          m_jobs;
	// Session 92: m_pending is polled by up to seven spinning workers at copywake = 2, while
	// m_sequence is WRITTEN by the enqueuing thread inside the critical section that
	// stg_lock_ns measures.  Sharing a cache line would let the spinners invalidate it under
	// the writer and inflate the very counter this change is judged by, so the poll target
	// gets a line of its own.
	alignas(64) std::atomic<size_t> m_pending {0};
	alignas(64) uint64_t     m_sequence = 0;  // next chunk number (m_mutex)
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
	// Knob "copywake" is READ AT EVERY DECISION, not once per process, and this is the
	// whole reason the fix can be measured at all: a value fixed at startup cannot be a
	// schedule arm, the only A/B this programme accepts is the within-run ABBA, and
	// between-run comparisons of cpu/draw are closed (ROADMAP.md section 3).  The read is
	// Gates::Value - one inline relaxed atomic load (gates.h:480) - against a notify that
	// costs 4.27 us, so its price is five orders of magnitude below the thing it selects.
	// Only the worker COUNT is fixed here, because the threads are made once.
	size_t m_wake_workers = 0;
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

uint64_t AsyncCopySignaled() {
	return CopyPool::Instance().Enabled() ? CopyPool::Instance().Signaled() : 0;
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
