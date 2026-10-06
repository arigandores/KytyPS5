#!/usr/bin/env python3
"""F20j4 (HPP-652; ROADMAP s122 item 581(v)(1)-(5), (d)): the review fixes RC1-RC5 of F20k3 for KYTY_DIAG_B32 on the
F20j3 code (worktree base 9db7938b).

    python patch_f20j4.py <worktree root> [--check]

Operations (anchors are WHOLE lines compared after strip(); every anchor must be unique unless a count is given):
  replace_range(file, first, last, new) - lines first .. the first `last` after it -> new
  replace_line(file, old, new, count)   - the line(s) old -> new (exactly count occurrences)
  insert_before(file, anchor, new)      - new before the anchor line
New text is written with leading TABS; if the first replaced / anchor line is indented with spaces only, every leading
tab of the new text becomes 4 spaces. CRLF files are handled (\r removed before the search and put back). LF out.
--check: applies to memory only and verifies that every operation's result is present (idempotence check of a patched
tree: exit 0 and ALL OK if the tree already carries every new text).
"""
import os
import sys

ROOT = sys.argv[1].rstrip('/\\')
CHECK = '--check' in sys.argv

OPS = []


def op(kind, path, *args):
    OPS.append((kind, path) + args)


# =====================================================================================================================
# src/common/diagB32.h
# =====================================================================================================================
H = 'src/common/diagB32.h'

op('insert_before', H, '#include <atomic>', '''// F20j4 (HPP-652; ROADMAP s122 item 581(v)): the review fixes of F20k3 - the contended lock under an H mark keeps the H
// mark (RC4), the TrackedMutex owner is cleared at the unlock and a peer is never the waiter itself (RC2), the M5 refresh
// time is charged to the window it ran in (RC3), the kinds vblank / audio / aio / net / emu_join are EMU_WAIT (RC5).

''')

op('replace_range', H,
   '// waits the guest asked for inside an HLE call (like cond / sem: GUEST_SLEEP:<kind> without a waker and a peer):',
   'Vblank, Once, Join, Addr, Aio, Fiber, Audio, Ult, Net, Rwlock, Count',
   '''	// waits inside a guest HLE call (F20j3; the class of each - IsEmuWait, F20j4 item 581(v)(5)):
	Vblank, Once, Join, Addr, Aio, Fiber, Audio, Ult, Net, Rwlock,
	// F20j4 (item 581(v)(5), RC5 of F20k3): Common::Thread::Join of an emulator thread (was "join" with PthreadJoin).
	EmuJoin, Count
''')

op('replace_range', H, '// F20j3 (item 574(d)): EMU_WAIT kinds.', '}',
   '''// F20j3 (item 574(d)): EMU_WAIT kinds. F20j4 (item 581(v)(5), RC5 of F20k3): the class is by who clears the wait
// condition. EMU_WAIT - the device emulation, the host I/O or an emulator thread: EmuMutex .. Av, Vblank (the present
// thread counts the vblanks), Audio (the audio device emulation sets the pace), Aio (the emulator runs the request), Net
// (the host network), EmuJoin. GUEST_SLEEP - another guest thread or a deadline the guest asked for: the older kinds
// (cond, mutex, sem, psem, evf, eq, sleep) and Once, Join (PthreadJoin only), Addr, Fiber, Ult, Rwlock.
[[nodiscard]] constexpr bool IsEmuWait(uint8_t kind) {
	return (kind >= kFirstEmuWait && kind < kFirstGuestHleWait) || kind == static_cast<uint8_t>(Wait::Vblank) ||
	       kind == static_cast<uint8_t>(Wait::Audio) || kind == static_cast<uint8_t>(Wait::Aio) ||
	       kind == static_cast<uint8_t>(Wait::Net) || kind == static_cast<uint8_t>(Wait::EmuJoin);
}
''')

op('replace_range', H, 'void BeginWReg(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us);',
   'void BeginWReg(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us);',
   '''	void BeginWReg(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us);
	// F20j4 (item 581(v)(2), RC2 of F20k3): BeginW / BeginWReg / BeginWLock store a peer equal to the thread's own slot
	// as 0 (a thread does not wait for itself - the peer is unknown).
	// F20j4 (item 581(v)(4), RC4 of F20k3): a contended lock acquisition (Common::Mutex::LockB32, TrackedMutex) - as
	// BeginWReg, but no mark while the slot's current mark is any H:<call> (the H mark already names this wait: H > W of
	// item 550(g)(2); the inputs of RC7 / RC5 of item 550(v) stay as before F20j3).
	void BeginWLock(Wait kind, const void* obj, int32_t peer_slot1);
''')

op('replace_range', H,
   '// F20j3 (item 574(g)(1)): a std mutex type whose CONTENDED acquisition is marked W:<K> (default emu_mutex) with the peer',
   'std::atomic<int32_t> m_owner {0};',
   '''// F20j3 (item 574(g)(1)): a std mutex type whose CONTENDED acquisition is marked W:<K> (default emu_mutex) with the peer
// = the slot of the thread that holds it exclusively (stored after each acquisition at =1). KYTY_DIAG_B32=0: lock() is
// one test of g_on and the std lock; try_lock() tests g_on only after a success; unlock() is one test of g_on and the
// std unlock. Not for a mutex used with std::condition_variable (that needs std::unique_lock<std::mutex>).
// F20j4 (item 581(v)(2), RC2 of F20k3): at =1 the owner is cleared before the unlock (a recursive mutex - at the last
// unlock of the holder), so the peer of a waiter is the current exclusive holder or 0: a writer that waits for readers
// (lock_shared does not set the owner) or a holder that has not stored itself yet - peer 0 (EMU_WAIT:emu_mutex by item
// 574(d)); never a released holder, never the waiter itself (an own-slot peer is stored as 0).
// F20j4 (item 581(v)(4), RC4 of F20k3): no W mark under an active H:<call> of the slot (Mark::BeginWLock).
template <class M, Wait K = Wait::EmuMutex>
class TrackedMutex {
public:
	TrackedMutex()                               = default;
	TrackedMutex(const TrackedMutex&)            = delete;
	TrackedMutex& operator=(const TrackedMutex&) = delete;

	void lock() {
		if (g_on) [[unlikely]] {
			LockSlow();
			return;
		}
		m_m.lock();
	}
	bool try_lock() {
		const bool ok = m_m.try_lock();
		if (ok && g_on) [[unlikely]] {
			TakeOwner();
		}
		return ok;
	}
	void unlock() {
		if (g_on) [[unlikely]] {
			ReleaseOwner();
		}
		m_m.unlock();
	}
	void lock_shared() {
		if (g_on) [[unlikely]] {
			if (m_m.try_lock_shared()) {
				return;
			}
			Mark b32;
			b32.BeginWLock(K, this, m_owner.load(std::memory_order_relaxed));
			m_m.lock_shared();
			b32.EndWithPeer(false);
			return;
		}
		m_m.lock_shared();
	}
	bool try_lock_shared() { return m_m.try_lock_shared(); }
	void unlock_shared() { m_m.unlock_shared(); }

private:
	void LockSlow() {
		if (!m_m.try_lock()) {
			Mark b32;
			b32.BeginWLock(K, this, m_owner.load(std::memory_order_relaxed));
			m_m.lock();
			b32.EndWithPeer(false);
		}
		TakeOwner();
	}
	// F20j4: m_depth is touched only by the exclusive holder (under the lock); > 1 only for a recursive mutex. An
	// acquisition made at =0 (no depth) is released like the last one: the owner is cleared.
	void TakeOwner() {
		if (m_depth++ == 0) {
			m_owner.store(SelfSlotIfRegistered(), std::memory_order_relaxed);
		}
	}
	void ReleaseOwner() {
		if (m_depth > 1) {
			m_depth--;
			return;
		}
		m_depth = 0;
		m_owner.store(0, std::memory_order_relaxed);
	}

	M                    m_m;
	std::atomic<int32_t> m_owner {0};
	int32_t              m_depth = 0;
''')

op('replace_range', H,
   '// F20j3 (item 574(g)(4)): a periodic work (the M5 thread-list refresh) on its own thread, so that its cost makes no gap',
   'std::atomic<uint64_t> m_runs {0};',
   '''// F20j3 (item 574(g)(4)): a periodic work (the M5 thread-list refresh) on its own thread, so that its cost makes no gap
// of samples on the sampler thread. Start runs work(user) at once and then every period_ns (from the end of the
// previous run); TakeWorkNs returns the time of the runs finished since the previous take (tests).
// F20j4 (item 581(v)(3), RC3 of F20k3): every run's [begin, end] is kept (a ring of kRuns, one writer - the refresher
// thread, one reader); TakeRuns moves the runs finished since the previous take, CurrentBegin is the begin of the run
// in progress (0 - none). The sampler reads CurrentBegin BEFORE TakeRuns (a finished run with that begin is the same
// run) and charges the runs to the windows they ran in (M5Charge).
class AsyncRefresh {
public:
	using Fn = void (*)(void* user);
	struct Run {
		uint64_t begin_ns = 0;
		uint64_t end_ns   = 0;
	};
	static constexpr uint32_t kRuns = 64;
	AsyncRefresh() = default;
	~AsyncRefresh();
	AsyncRefresh(const AsyncRefresh&)            = delete;
	AsyncRefresh& operator=(const AsyncRefresh&) = delete;
	void                   Start(Fn work, void* user, uint64_t period_ns);
	void                   Stop(); // tests
	[[nodiscard]] uint64_t TakeWorkNs();
	[[nodiscard]] uint64_t Runs() const { return m_runs.load(std::memory_order_acquire); }
	void                   TakeRuns(std::vector<Run>* out); // the reader
	[[nodiscard]] uint64_t CurrentBegin() const { return m_cur_begin.load(std::memory_order_acquire); }
	[[nodiscard]] uint64_t LostRuns() const { return m_lost; } // runs overwritten before their take (the reader's count)
	void                   PushRun(uint64_t begin_ns, uint64_t end_ns); // the writer: the refresher thread (and tests)

private:
	struct RunEnt {
		std::atomic<uint64_t> seq {0}; // 2 * index + 1 while written, 2 * index + 2 when complete
		std::atomic<uint64_t> begin {0};
		std::atomic<uint64_t> end {0};
	};
	struct Impl;
	Impl*                 m_impl = nullptr;
	std::atomic<uint64_t> m_work_ns {0};
	std::atomic<uint64_t> m_runs {0};
	std::atomic<uint64_t> m_cur_begin {0};
	RunEnt                m_ring[kRuns];
	std::atomic<uint64_t> m_wpos {0};
	uint64_t              m_rpos = 0;
	uint64_t              m_lost = 0;
''')

op('replace_range', H, '} // namespace Core', '} // namespace Core',
   '''// F20j4 (item 581(v)(3), RC3 of F20k3): the M5 refresh time charged to the window it ran in. Add - the runs taken at a
// flip (finished, oldest first) and the begin of the run in progress read before the take (0 - none); Window(start,
// end) - the overlap of the finished runs and of the running one (it lasts at least until end) with (start, end];
// Prune(from) - drops the finished runs that end at or before from. The windows close in order, so a run that crosses
// a flip is split: the part up to the flip goes to the closed window k, the rest to k + 1.
class M5Charge {
public:
	void                   Add(const std::vector<AsyncRefresh::Run>& runs, uint64_t cur_begin);
	[[nodiscard]] uint64_t Window(uint64_t start, uint64_t end) const;
	void                   Prune(uint64_t from);
	[[nodiscard]] size_t   Pending() const { return m_runs.size(); }

private:
	std::vector<AsyncRefresh::Run> m_runs;
	uint64_t                       m_cur = 0;
};

} // namespace Core
''')

# =====================================================================================================================
# src/common/diagB32.cpp
# =====================================================================================================================
C = 'src/common/diagB32.cpp'

op('replace_line', C,
   '"vblank", "once", "join", "addr", "aio", "fiber", "audio", "ult", "net", "rwlock"};',
   '''	                                        "vblank", "once", "join", "addr", "aio", "fiber", "audio", "ult", "net", "rwlock",
	                                        // F20j4 (item 581(v)(5)): Common::Thread::Join
	                                        "emu_join"};''', 1)

op('replace_range', C, 'work(user);', 'm_runs.fetch_add(1, std::memory_order_acq_rel);',
   '''			m_cur_begin.store(t0, std::memory_order_release); // F20j4 (RC3 of F20k3): the run in progress
			work(user);
			const auto t1 = FrameStats::NowNs();
			m_work_ns.fetch_add(t1 - t0, std::memory_order_acq_rel);
			PushRun(t0, t1);
			m_cur_begin.store(0, std::memory_order_release);
			m_runs.fetch_add(1, std::memory_order_acq_rel);
''')

op('replace_range', C, 'uint64_t AsyncRefresh::TakeWorkNs() {', '}',
   '''uint64_t AsyncRefresh::TakeWorkNs() {
	return m_work_ns.exchange(0, std::memory_order_acq_rel);
}

// F20j4 (item 581(v)(3), RC3 of F20k3): one writer (the refresher thread) - a per-entry sequence word, as WaitRing.
void AsyncRefresh::PushRun(uint64_t begin_ns, uint64_t end_ns) {
	const auto i = m_wpos.load(std::memory_order_relaxed);
	auto&      e = m_ring[i % kRuns];
	e.seq.store(2 * i + 1, std::memory_order_release);
	e.begin.store(begin_ns, std::memory_order_relaxed);
	e.end.store(end_ns, std::memory_order_relaxed);
	e.seq.store(2 * i + 2, std::memory_order_release);
	m_wpos.store(i + 1, std::memory_order_release);
}

void AsyncRefresh::TakeRuns(std::vector<Run>* out) {
	const auto w = m_wpos.load(std::memory_order_acquire);
	if (w - m_rpos > kRuns) {
		m_lost += w - m_rpos - kRuns;
		m_rpos = w - kRuns;
	}
	for (; m_rpos < w; m_rpos++) {
		auto&      e  = m_ring[m_rpos % kRuns];
		const auto s0 = e.seq.load(std::memory_order_acquire);
		Run        r;
		r.begin_ns = e.begin.load(std::memory_order_relaxed);
		r.end_ns   = e.end.load(std::memory_order_relaxed);
		std::atomic_thread_fence(std::memory_order_acquire);
		const auto s1 = e.seq.load(std::memory_order_relaxed);
		if (s0 != 2 * m_rpos + 2 || s1 != s0) {
			m_lost++; // overwritten by a later lap before or while it was read
			continue;
		}
		out->push_back(r);
	}
}

void M5Charge::Add(const std::vector<AsyncRefresh::Run>& runs, uint64_t cur_begin) {
	m_cur = cur_begin;
	for (const auto& r: runs) {
		if (cur_begin != 0 && r.begin_ns == cur_begin) {
			m_cur = 0; // the run seen in progress finished before the take - the same run
		}
		m_runs.push_back(r);
	}
}

uint64_t M5Charge::Window(uint64_t start, uint64_t end) const {
	uint64_t sum = 0;
	for (const auto& r: m_runs) {
		const auto b = std::max(r.begin_ns, start);
		const auto e = std::min(r.end_ns, end);
		sum += e > b ? e - b : 0;
	}
	if (m_cur != 0) {
		const auto b = std::max(m_cur, start);
		sum += end > b ? end - b : 0;
	}
	return sum;
}

void M5Charge::Prune(uint64_t from) {
	m_runs.erase(std::remove_if(m_runs.begin(), m_runs.end(), [from](const AsyncRefresh::Run& r) { return r.end_ns <= from; }),
	             m_runs.end());
}
''')

op('replace_line', C, 'm_peer       = peer_slot1;',
   '	m_peer       = peer_slot1 == slot1 ? 0 : peer_slot1; // F20j4 (RC2 of F20k3): never the thread itself', 2)

op('insert_before', C, 'void Mark::EndSlow(int32_t waker_slot1, bool timed_out) {',
   '''// F20j4 (item 581(v)(4), RC4 of F20k3): the slot's mark is written only by this thread - the load is exact.
void Mark::BeginWLock(Wait kind, const void* obj, int32_t peer_slot1) {
	const auto slot1 = SelfSlotIfRegistered();
	if (slot1 <= 0 || g_reg == nullptr) {
		return;
	}
	if ((g_reg->slots[slot1 - 1].mark.load(std::memory_order_relaxed) >> 8u) == static_cast<uint32_t>(State::H)) {
		return;
	}
	BeginWReg(kind, obj, peer_slot1, 0);
}

''')

op('replace_line', C, 'uint64_t                  m_win_m5r_ns = 0;',
   '''	Core::M5Charge            m_m5c;          // F20j4 (item 581(v)(3), RC3 of F20k3)
	std::vector<Core::AsyncRefresh::Run> m_m5_runs;''', 1)

op('replace_range', C, 'const uint64_t extra = m_win_extra_ns + print_ns; // F20j2 RC6: the report print inside this window',
   'm_win_m5r_ns         = 0;',
   '''	// F20j4 (item 581(v)(3), RC3 of F20k3): the M5 refresh time inside (start, flip_ns] - this window's own (RC9).
	const uint64_t m5r   = m_m5c.Window(start, flip_ns);
	const uint64_t extra = m_win_extra_ns + print_ns + m5r; // F20j2 RC6: the report print inside this window
	m_win_start          = flip_ns;
	m_win_extra_ns       = 0;
''')

op('replace_range', C,
   '// F20j3 (item 574(g)(4)): the refresh runs on the refresher thread; its time finished since the previous flip goes',
   'const uint64_t m5r = m_m5r.TakeWorkNs();',
   '''	// F20j3 (item 574(g)(4)): the refresh runs on the refresher thread (no gap of samples). F20j4 (item 581(v)(3), RC3 of
	// F20k3): its runs are charged to the windows they ran in - the begin of the run in progress first, then the finished
	// runs; CloseWindow takes the overlap with its own window.
	const uint64_t m5_cur = m_m5r.CurrentBegin();
	m_m5_runs.clear();
	m_m5r.TakeRuns(&m_m5_runs);
	m_m5c.Add(m_m5_runs, m5_cur);
''')

op('replace_range', C,
   '// The boundary work runs after the flip: it is sampler time inside the new window (RC9 instr_us); F20j3 - plus the',
   'm_win_m5r_ns += m5r;',
   '''	// The boundary work runs after the flip: it is sampler time inside the new window (RC9 instr_us). F20j4: the M5
	// refresh time is charged by CloseWindow; the finished runs that end before the open window are dropped.
	m_win_extra_ns += FrameStats::NowNs() - t0;
	m_m5c.Prune(m_win_start);
''')

# =====================================================================================================================
# src/common/threads.cpp
# =====================================================================================================================
T = 'src/common/threads.cpp'

op('replace_range', T, '// Track F, F20j3 (KYTY_DIAG_B32 W:join, item 574(g)(1)).', 'b32.BeginWReg(DiagB32::Wait::Join, this, 0, 0);',
   '''	// Track F, F20j3 (KYTY_DIAG_B32, item 574(g)(1)); F20j4 (item 581(v)(5), RC5 of F20k3): W:emu_join - an emulator
	// thread (PthreadJoin keeps W:join).
	DiagB32::Mark b32;
	if (DiagB32::g_on) [[unlikely]] {
		b32.BeginWReg(DiagB32::Wait::EmuJoin, this, 0, 0);
''')

op('replace_line', T, '// stale peer [I]). The waker of the record is the peer (mutex-like, item 550(g)(2)(iv)).',
   '''// stale peer [I]). The waker of the record is the peer (mutex-like, item 550(g)(2)(iv)).
// F20j4 (item 581(v)(4), RC4 of F20k3): BeginWLock - no W:emu_mutex while the slot's mark is any H:<call> (H:qlock around
// the queue mutex, H:present, ...): the H mark stays the sample's state.''', 1)

op('replace_line', T, 'b32.BeginWReg(DiagB32::Wait::EmuMutex, this, DiagB32::SlotOfOsTid(owner), 0);',
   '	b32.BeginWLock(DiagB32::Wait::EmuMutex, this, DiagB32::SlotOfOsTid(owner));', 1)
op('replace_line', T, 'b32.BeginWReg(DiagB32::Wait::EmuMutex, this, 0, 0);',
   '	b32.BeginWLock(DiagB32::Wait::EmuMutex, this, 0);', 1)

# =====================================================================================================================
# src/graphics/host_gpu/renderer/commandRecorder.cpp - RC1
# =====================================================================================================================
R = 'src/graphics/host_gpu/renderer/commandRecorder.cpp'

op('replace_range', R, 'EXIT_IF(bytes == 0 || (bytes % RecordAlign) != 0 ||', 'for (;;) {',
   '''	EXIT_IF(bytes == 0 || (bytes % RecordAlign) != 0 ||
	        static_cast<uint64_t>(bytes) > m_capacity / 2u);
	// Track F, F20j4 (KYTY_DIAG_B32 W:rec_wait, item 581(v)(1), RC1 of F20k3): one mark over the whole retry loop - begun
	// at the first pass that finds the arena full, ended before the return (as Drain); the WaitSlice waits and the work
	// between them stay W of one record.
	Common::DiagB32::Mark b32;
	for (;;) {
''')

op('replace_range', R, '// Track F, F20j3 (KYTY_DIAG_B32 W:rec_wait, item 574(g)(1)): the producer waits for the record thread.',
   'b32.EndSig(&m_progress);',
   '''				// Track F, F20j3 (KYTY_DIAG_B32 W:rec_wait, item 574(g)(1)): the producer waits for the record thread.
				if (Common::DiagB32::g_on && !b32.Active()) [[unlikely]] {
					b32.BeginWReg(Common::DiagB32::Wait::RecWait, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Record), 0);
				}
				m_progress.wait_for(lock, WaitSlice, [this, head, want] {
					const auto in_use = head - m_tail.load(std::memory_order_acquire);
					return m_capacity - in_use >= want;
				});
''')

op('replace_line', R, 'return m_data.get() + index;',
   '''		b32.EndSig(&m_progress); // F20j4 (RC1): the end of the whole retry loop (one test of the flag at =0)
		return m_data.get() + index;''', 1)


# =====================================================================================================================
# tests/DiagB32Tests.cpp
# =====================================================================================================================
X = 'tests/DiagB32Tests.cpp'

op('replace_line', X, '// runtime cases run last: Test::InitRuntime turns g_on on for the rest of the process.',
   '''// runtime cases run last: Test::InitRuntime turns g_on on for the rest of the process.
// F20j4 (HPP-652; ROADMAP s122 item 581(v), (d)): plus the kind partition by who clears the wait (RC5), the M5 refresh
// charged to the window it ran in (RC3, model and the run ring), a writer waiting for readers and an own-slot peer
// (RC2), a contended lock inside H:qlock / H:present (RC4).''', 1)

op('insert_before', X, '#include <string>', '#include <shared_mutex>\n')

op('replace_range', X, 'CHECK(std::string(WaitName(static_cast<uint8_t>(Wait::Rwlock))) == "rwlock");',
   'CHECK(!IsEmuWait(static_cast<uint8_t>(Wait::Vblank)) && !IsEmuWait(static_cast<uint8_t>(Wait::Cond)));',
   '''	CHECK(std::string(WaitName(static_cast<uint8_t>(Wait::Rwlock))) == "rwlock");
	// F20j4 (item 581(v)(5)): emu_join appended after rwlock; join keeps its number and name (PthreadJoin only).
	CHECK(static_cast<uint8_t>(Wait::EmuJoin) == static_cast<uint8_t>(Wait::Rwlock) + 1);
	CHECK(static_cast<uint8_t>(Wait::Count) == static_cast<uint8_t>(Wait::EmuJoin) + 1);
	CHECK(std::string(WaitName(static_cast<uint8_t>(Wait::EmuJoin))) == "emu_join");
	CHECK(std::string(WaitName(static_cast<uint8_t>(Wait::Join))) == "join");
	// F20j4 (item 581(v)(5)): EMU_WAIT - EmuMutex .. Av and vblank, audio, aio, net, emu_join; GUEST_SLEEP - the rest.
	const std::vector<std::string> emu_hle = {"vblank", "audio", "aio", "net", "emu_join"};
	const std::vector<std::string> guest   = {"cond", "mutex", "sem",   "psem", "evf",   "eq",  "sleep", "gpu_idle",
	                                          "gpu_regmem", "once", "join", "addr", "fiber", "ult", "rwlock"};
	uint32_t n_emu = 0;
	for (uint8_t k = 1; k < static_cast<uint8_t>(Wait::Count); k++) {
		const std::string n   = WaitName(k);
		const bool        emu = (k >= static_cast<uint8_t>(Wait::EmuMutex) && k <= static_cast<uint8_t>(Wait::Av)) ||
		                 std::find(emu_hle.begin(), emu_hle.end(), n) != emu_hle.end();
		CHECK(IsEmuWait(k) == emu);
		CHECK(emu != (std::find(guest.begin(), guest.end(), n) != guest.end())); // each kind in exactly one class
		n_emu += emu ? 1 : 0;
	}
	CHECK(n_emu == 25 + 5);
	CHECK(!IsEmuWait(static_cast<uint8_t>(Wait::Cond)) && !IsEmuWait(static_cast<uint8_t>(Wait::Join)));
	CHECK(IsEmuWait(static_cast<uint8_t>(Wait::Vblank)) && IsEmuWait(static_cast<uint8_t>(Wait::EmuJoin)));
	CHECK(!IsEmuWait(0) && !IsEmuWait(static_cast<uint8_t>(Wait::Count)));
''')

op('insert_before', X, 'int main() {', r'''// ---------------------------------------------------------------------------------------------------------------------
// F20j4 (HPP-652; ROADMAP s122 item 581(v))
// ---------------------------------------------------------------------------------------------------------------------
struct RunProbe {
	std::atomic<bool> in_work {false};
	std::atomic<bool> release {false};
};

static void ProbeWork(void* user) {
	auto* p = static_cast<RunProbe*>(user);
	p->in_work.store(true);
	while (!p->release.load()) {
		std::this_thread::yield();
	}
}

static void TestM5Charge() {
	Case("F20j4 (3), RC3 of F20k3: the M5 refresh time is charged to the window it ran in (model; the run ring)");
	const uint64_t ms = 1000000;
	// The RC3 scenario: window k = (1000, 1150] ms (a 150 ms frame), k+1 = (1150, 1270] ms; a 76.7 ms refresh.
	const uint64_t s0 = 1000 * ms;
	const uint64_t f1 = 1150 * ms;
	const uint64_t f2 = 1270 * ms;
	{
		M5Charge c; // a run entirely inside k, taken at the flip of k: m5r(k) = its cost, m5r(k+1) = 0
		c.Add({{s0 + 40 * ms, s0 + 40 * ms + 76700000}}, 0);
		CHECK(c.Window(s0, f1) == 76700000);
		c.Prune(f1);
		c.Add({}, 0);
		CHECK(c.Window(f1, f2) == 0 && c.Pending() == 0);
	}
	{
		M5Charge c; // a run across the flip of k, finished before the take: split by the overlap
		c.Add({{f1 - 30 * ms, f1 + 50 * ms}}, 0);
		CHECK(c.Window(s0, f1) == 30 * ms);
		c.Prune(f1);
		CHECK(c.Pending() == 1);
		c.Add({}, 0);
		CHECK(c.Window(f1, f2) == 50 * ms);
		c.Prune(f2);
		CHECK(c.Pending() == 0);
	}
	{
		M5Charge       c; // a run in progress at the take of k, finished before the take of k+1: k gets its part only once
		const uint64_t b = f1 - 30 * ms;
		c.Add({}, b);
		CHECK(c.Window(s0, f1) == 30 * ms);
		c.Prune(f1);
		c.Add({{b, f1 + 50 * ms}}, 0);
		CHECK(c.Window(f1, f2) == 50 * ms);
	}
	{
		M5Charge       c; // the run seen in progress finished before the take: counted once
		const uint64_t b = s0 + 20 * ms;
		c.Add({{b, b + 10 * ms}}, b);
		CHECK(c.Window(s0, f1) == 10 * ms);
	}
	{
		M5Charge c; // two windows closed at one take (a batch): a run over both and a later one
		c.Add({{s0 + 100 * ms, f1 + 20 * ms}, {f1 + 60 * ms, f1 + 70 * ms}}, 0);
		CHECK(c.Window(s0, f1) == 50 * ms);
		CHECK(c.Window(f1, f2) == 30 * ms);
		c.Prune(f2);
		CHECK(c.Pending() == 0);
	}
	// The run ring of AsyncRefresh: CurrentBegin while a run is in progress, the run with [begin, end] after it.
	RunProbe     probe;
	AsyncRefresh ar;
	ar.Start(&ProbeWork, &probe, 1000000000ull);
	while (!probe.in_work.load()) {
		std::this_thread::yield();
	}
	const auto                     cur = ar.CurrentBegin();
	std::vector<AsyncRefresh::Run> runs;
	ar.TakeRuns(&runs);
	CHECK(cur != 0 && runs.empty());
	std::this_thread::sleep_for(std::chrono::milliseconds(5));
	probe.release.store(true);
	while (ar.Runs() < 1) {
		std::this_thread::yield();
	}
	ar.TakeRuns(&runs);
	CHECK(runs.size() == 1 && runs[0].begin_ns == cur && runs[0].end_ns >= cur + 4 * ms);
	CHECK(ar.CurrentBegin() == 0);
	ar.Stop();
	AsyncRefresh lap; // more than kRuns runs before a take: the oldest are counted as lost
	for (uint64_t i = 0; i < AsyncRefresh::kRuns + 6; i++) {
		lap.PushRun(i * 10 + 1, i * 10 + 5);
	}
	std::vector<AsyncRefresh::Run> got;
	lap.TakeRuns(&got);
	CHECK(got.size() == AsyncRefresh::kRuns && lap.LostRuns() == 6 && !got.empty() && got[0].begin_ns == 61);
	std::printf("  m5 charge: run in progress begin=%llu, taken runs=%zu, ring lost=%llu\n", static_cast<unsigned long long>(cur),
	            runs.size(), static_cast<unsigned long long>(lap.LostRuns()));
}

static void TestPeerSelfRuntime() {
	Case("F20j4 (2), RC2 of F20k3: a writer waiting for two readers - peer 0; an own-slot peer is stored as 0");
	Test::InitRuntime();
	TrackedMutex<std::shared_mutex> sm;
	std::atomic<int32_t>            x_slot {0};
	std::atomic<int32_t>            self_peer {-1};
	std::atomic<int>                readers {0};
	std::atomic<bool>               x_first {false};
	std::atomic<bool>               writer_waits {false};
	std::thread                     x([&] {
		RegisterRole("TestX");
		x_slot.store(SelfSlotIfRegistered());
		sm.lock(); // X is the last exclusive holder; before F20j4 its slot stayed in the owner field after the unlock
		sm.unlock();
		x_first.store(true);
		while (readers.load() < 2) {
			std::this_thread::yield();
		}
		writer_waits.store(true);
		sm.lock(); // waits for the two readers (lock_shared does not set the owner)
		sm.unlock();
		Mark self; // a mark given the thread's own slot as the peer
		self.BeginWReg(Wait::GpuWait, &sm, SelfSlotIfRegistered(), 0);
		MarkSnap s;
		if (Test::ReadSlotMark(SelfSlotIfRegistered(), &s)) {
			self_peer.store(s.peer);
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(20));
		self.End(0, false);
	});
	const auto reader = [&](const char* role) {
		RegisterRole(role);
		while (!x_first.load()) {
			std::this_thread::yield();
		}
		sm.lock_shared();
		readers.fetch_add(1);
		while (!writer_waits.load()) {
			std::this_thread::yield();
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(40));
		sm.unlock_shared();
	};
	std::thread r1([&] { reader("TestR1"); });
	std::thread r2([&] { reader("TestR2"); });
	x.join();
	r1.join();
	r2.join();
	const auto recs = RecordsOf(x_slot.load());
	std::printf("  peer: records=%zu self_peer=%d\n", recs.size(), self_peer.load());
	CHECK(self_peer.load() == 0);
	CHECK(recs.size() == 2);
	if (recs.size() == 2) {
		CHECK(recs[0].kind == static_cast<uint8_t>(Wait::EmuMutex) && recs[0].obj == reinterpret_cast<uint64_t>(&sm));
		CHECK(recs[0].peer1 == 0 && recs[0].waker1 == 0);
		CHECK(recs[0].end_ns - recs[0].start_ns >= 20000000);
		CHECK(recs[1].kind == static_cast<uint8_t>(Wait::GpuWait) && recs[1].peer1 == 0);
	}
	for (const auto& r: recs) {
		CHECK(r.peer1 != x_slot.load() && r.waker1 != x_slot.load()); // no record names the waiter itself
	}
}

static void TestLockUnderHRuntime() {
	Case("F20j4 (4), RC4 of F20k3: a contended lock inside H:qlock / H:present keeps the H mark; without H - W:emu_mutex");
	Test::InitRuntime();
	Common::Mutex            m;
	TrackedMutex<std::mutex> tm;
	// B: 1 - waits for m inside H:qlock, 2 - waits for tm inside H:present, 3 - waits for m without an H mark, 4 - done.
	std::atomic<int>     stage {0};
	std::atomic<bool>    a_holds {false};
	std::atomic<bool>    b_mid {false};
	std::atomic<bool>    a_again {false};
	std::atomic<int32_t> a_slot {0};
	std::atomic<int32_t> b_slot {0};
	std::thread          a([&] {
		RegisterRole("TestHA");
		a_slot.store(SelfSlotIfRegistered());
		m.Lock();
		tm.lock();
		a_holds.store(true);
		while (stage.load() < 1) {
			std::this_thread::yield();
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(40));
		m.Unlock();
		while (stage.load() < 2) {
			std::this_thread::yield();
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(40));
		tm.unlock();
		while (!b_mid.load()) {
			std::this_thread::yield();
		}
		m.Lock();
		a_again.store(true);
		while (stage.load() < 3) {
			std::this_thread::yield();
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(40));
		m.Unlock();
	});
	std::thread b([&] {
		RegisterRole("TestHB");
		b_slot.store(SelfSlotIfRegistered());
		while (!a_holds.load()) {
			std::this_thread::yield();
		}
		{
			Mark h;
			h.BeginH(Call::QLock);
			stage.store(1);
			m.Lock();
			m.Unlock();
			h.End(0, false);
		}
		{
			Mark h;
			h.BeginH(Call::Present);
			stage.store(2);
			tm.lock();
			tm.unlock();
			h.End(0, false);
		}
		b_mid.store(true);
		while (!a_again.load()) {
			std::this_thread::yield();
		}
		stage.store(3);
		m.Lock();
		m.Unlock();
		stage.store(4);
	});
	// Samples of B's slot every 1 ms by the clock; a sample counts only if the stage did not change around it.
	uint32_t h_ok[4] {};
	uint32_t w_n[4] {};
	uint32_t w_emu[4] {};
	while (b_slot.load() == 0 || stage.load() == 0) {
		std::this_thread::yield();
	}
	auto next = std::chrono::steady_clock::now();
	while (stage.load() != 4) {
		const int s0 = stage.load();
		MarkSnap  snap;
		const bool got = Test::ReadSlotMark(b_slot.load(), &snap);
		const int s1 = stage.load();
		if (got && s0 == s1 && s0 >= 1 && s0 <= 3) {
			const auto st   = static_cast<State>(snap.mark >> 8u);
			const auto kind = static_cast<uint8_t>(snap.mark & 0xffu);
			const auto want = s0 == 1 ? static_cast<uint8_t>(Call::QLock) : static_cast<uint8_t>(Call::Present);
			h_ok[s0] += st == State::H && kind == want ? 1 : 0;
			w_n[s0] += st == State::W ? 1 : 0;
			w_emu[s0] += st == State::W && kind == static_cast<uint8_t>(Wait::EmuMutex) ? 1 : 0;
		}
		next += std::chrono::milliseconds(1);
		while (std::chrono::steady_clock::now() < next && stage.load() != 4) {
			std::this_thread::yield();
		}
	}
	a.join();
	b.join();
	const auto recs = RecordsOf(b_slot.load());
	std::printf("  under H: qlock H=%u W=%u; present H=%u W=%u; no H W:emu_mutex=%u W=%u; records=%zu\n", h_ok[1], w_n[1],
	            h_ok[2], w_n[2], w_emu[3], w_n[3], recs.size());
	CHECK(h_ok[1] >= 10 && w_n[1] == 0); // inside H:qlock the samples stay H:qlock
	CHECK(h_ok[2] >= 10 && w_n[2] == 0); // inside H:present the samples stay H:present
	CHECK(w_emu[3] >= 10);               // the control without an H mark: W:emu_mutex
	CHECK(recs.size() == 1);             // only the wait without an H mark is a record
	if (recs.size() == 1) {
		CHECK(recs[0].kind == static_cast<uint8_t>(Wait::EmuMutex) && recs[0].obj == reinterpret_cast<uint64_t>(&m));
		CHECK(recs[0].peer1 == a_slot.load() && recs[0].waker1 == a_slot.load());
		CHECK(recs[0].end_ns - recs[0].start_ns >= 20000000);
	}
}

''')

op('replace_line', X, 'TestM5Async();', '''	TestM5Async();
	TestM5Charge();''', 1)
op('replace_line', X, 'TestEmuMutexRuntime();', '''	TestEmuMutexRuntime();
	TestPeerSelfRuntime();
	TestLockUnderHRuntime();''', 1)


# =====================================================================================================================
def load(path):
    raw = open(os.path.join(ROOT, path), 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    return text.split('\n'), crlf


def indent(new, ref_line):
    lines = new.rstrip('\n').split('\n')
    pre = ref_line[:len(ref_line) - len(ref_line.lstrip())]
    if '\t' not in pre and pre.startswith(' '):
        out = []
        for l in lines:
            n = len(l) - len(l.lstrip('\t'))
            out.append('    ' * n + l[n:])
        return out
    return lines


def find(lines, anchor, start=0):
    a = anchor.strip()
    return [i for i in range(start, len(lines)) if lines[i].strip() == a]


files = {}
ok = True
for o in OPS:
    kind, path = o[0], o[1]
    if path not in files:
        files[path] = load(path)
    lines, crlf = files[path]
    if kind == 'replace_range':
        first, last, new = o[2], o[3], o[4]
        hits = find(lines, first)
        if len(hits) != 1:
            if CHECK:
                print('check: %s range %r -> %d hits (patched?)' % (path, first[:60], len(hits)))
                continue
            print('FAIL %s: first anchor %r hits %d' % (path, first[:80], len(hits)))
            ok = False
            continue
        i = hits[0]
        j = next((k for k in range(i, len(lines)) if lines[k].strip() == last.strip()), None)
        if j is None:
            print('FAIL %s: last anchor %r not found after %d' % (path, last[:80], i + 1))
            ok = False
            continue
        nl = indent(new, lines[i])
        lines[i:j + 1] = nl
        print('ok   %s replace_range %d-%d -> %d lines' % (path, i + 1, j + 1, len(nl)))
    elif kind == 'replace_line':
        old, new, count = o[2], o[3], o[4]
        hits = find(lines, old)
        if len(hits) != count:
            print('%s %s: line %r hits %d != %d' % ('check:' if CHECK else 'FAIL', path, old[:80], len(hits), count))
            ok = ok and CHECK
            continue
        for i in reversed(hits):
            lines[i:i + 1] = indent(new, lines[i])
        print('ok   %s replace_line x%d at %s' % (path, count, ','.join(str(h + 1) for h in hits)))
    elif kind == 'insert_before':
        anchor, new = o[2], o[3]
        hits = find(lines, anchor)
        if len(hits) != 1:
            print('FAIL %s: anchor %r hits %d' % (path, anchor[:80], len(hits)))
            ok = False
            continue
        i = hits[0]
        nl = new.rstrip('\n').split('\n') + ([''] if new.endswith('\n\n') else [])
        nl = indent('\n'.join(nl), lines[i]) if nl else nl
        if new.endswith('\n\n'):
            nl = nl + ['']
        lines[i:i] = nl
        print('ok   %s insert_before %d (+%d)' % (path, i + 1, len(nl)))
    files[path] = (lines, crlf)

if not ok:
    print('FAILED (nothing written)')
    sys.exit(1)
if CHECK:
    print('check only: nothing written')
    sys.exit(0)
for path, (lines, crlf) in files.items():
    data = '\n'.join(lines)
    open(os.path.join(ROOT, path), 'wb').write(data.encode('utf-8'))
    print('written %s%s' % (path, ' (was CRLF, now LF)' if crlf else ''))
print('ALL OK')
