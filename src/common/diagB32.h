#ifndef KYTY_COMMON_DIAG_B32_H_
#define KYTY_COMMON_DIAG_B32_H_

// Track F, F20j (HPP-629; ROADMAP s122 item 550, design docs/track-f/f20g.md s2 with RC1-RC15 of
// docs/track-f/f20h-review.md as resolved by item 550(v)). MEASUREMENT ONLY.
//
// KYTY_DIAG_B32 = 1: a sampler thread (THREAD_PRIORITY_HIGHEST, high-resolution waitable timer, period 5 ms) writes the
// state of every registered thread into a per-slot history ring all the time (RC1); at every flip it closes the window
// "previous flip .. flip" (RC1, RC11) and, for a window of dt >= 100 ms, formats the lines DiagB32: / DiagB32-t: /
// DiagB32-w: / DiagB32-c: / DiagB32-x: which the present thread prints at its next flip site (after
// flip_status.count++). Marks: H:<call> (host calls of the emulator, M3), W:<kind> (guest waits and the GuestGpu waits,
// M2/M4); "last signaller" fields are atomics in emulator objects on the host heap (RC10).
// F20j3 (HPP-646; ROADMAP s122 item 574(g)): W:<kind> also on the host waits of the emulator itself (the kinds from
// EmuMutex on; the inventory - docs/track-f/f20j3/waits_f20j3.py): the contended Common::Mutex::Lock and TrackedMutex
// lock (peer - the owner), the wait loops of the flip queue, GuestGpu, the async submitter, the priority operations
// and the guest HLE calls (one mark over the whole loop; waker - the last signaller kept in the waited object, peer -
// the thread that advances the condition by the code); the M5 thread-list refresh runs on its own thread.
// KYTY_DIAG_B32 unset, empty or "0": nothing - no thread, no line; every site tests the global flag g_on once.
// The knob is read ONCE by Init() at the start of Emulator::Run, before the first guest thread (RC10).
//
// KYTY_TEST_B32=<s>:<present|gpusleep>:<ms> (stand, default off, read once by Init): armed by the first guest line
// "Level has started: <non-blank name>"; once, <s> seconds after the arm, the present thread sleeps <ms> inside the
// mark H:present (present) or the GuestGpu thread sleeps <ms> between commands outside every mark (gpusleep).

// F20j4 (HPP-652; ROADMAP s122 item 581(v)): the review fixes of F20k3 - the contended lock under an H mark keeps the H
// mark (RC4), the TrackedMutex owner is cleared at the unlock and a peer is never the waiter itself (RC2), the M5 refresh
// time is charged to the window it ran in (RC3), the kinds vblank / audio / aio / net / emu_join are EMU_WAIT (RC5).

#include <atomic>
#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace Common::DiagB32 {

// ---- global flags (written once by Init before any guest thread; read by the sites) ----
extern bool g_on;            // KYTY_DIAG_B32 == "1"
extern bool g_test_on;       // KYTY_TEST_B32 valid (any mode)
extern bool g_test_gpusleep; // KYTY_TEST_B32 mode gpusleep
extern bool g_present_site;  // g_on || mode present: the one flag of the present site

// ---- constants (ROADMAP item 550: P = 5 ms, print >= 100 ms, wait records >= 10 ms, slots 256, wait ring 4096) ----
constexpr uint64_t kPeriodNs      = 5000000;
constexpr uint64_t kPrintNs       = 100000000;
constexpr uint64_t kShortNs       = 70000000;  // short_stalls: 70 <= dt < 100 ms (reference only)
constexpr uint64_t kWaitRecNs     = 10000000;
constexpr uint64_t kKernelAfterNs = 40000000;  // RC3: kernel thread state only in samples >= 40 ms after the previous flip
// F20j2 (HPP-633; ROADMAP s122 item 552(v)(1), RC1 of F20k): the kernel query schedule - a query of the open window only
// if (its kernel-query time + the last query's cost) <= window / kKqBudgetDiv; an S sample without its own query is
// split by the nearest snapshot of the same window not farther than kKqNearNs (at the window close).
constexpr uint64_t kKqBudgetDiv   = 10;
constexpr uint64_t kKqNearNs      = 60000000;
constexpr uint32_t kSlots         = 256;
constexpr uint32_t kHist          = 512;       // per-slot history ring: 512 samples x 5 ms = 2.56 s (RC1: >= 2 s)
constexpr uint32_t kWaitRing      = 4096;
constexpr uint32_t kOthersCap     = 24;        // RC2: the cap applies only to the non-mandatory -t lines
constexpr uint32_t kMustCap       = 96;        // a mandatory -t line beyond this is cut and counted in lines_cut
constexpr uint32_t kWLinesCap     = 64;
constexpr uint32_t kCLines        = 8;

enum class Call : uint8_t { None = 0, Present, Acquire, QSubmit, QLock, Drain, SemWait, Protect, Fault, Count };
enum class Wait : uint8_t {
	None = 0, Cond, Mutex, Sem, PSem, Evf, Eq, Sleep, GpuIdle, GpuRegmem,
	// F20j3 (item 574(g)(1)): appended after GpuRegmem - the older kinds keep their numbers and names.
	// Host waits of the emulator itself, EmuMutex .. Av (item 574(d): without a waker and a peer - EMU_WAIT:<kind>):
	EmuMutex, GpuWait, GpuCmd, FlipSlot, FlipDone, FlipCancel, FlipReq, VoPace, Relay, FramePool, RecWait, RecIdle,
	ASubIdle, ASubDrain, OpsWait, OpsIdle, PipeWait, PCopy, PmDrain, VmaFlush, RecQueue, MainTask, MainIdle, Spin, Av,
	// waits inside a guest HLE call (F20j3; the class of each - IsEmuWait, F20j4 item 581(v)(5)):
	Vblank, Once, Join, Addr, Aio, Fiber, Audio, Ult, Net, Rwlock,
	// F20j4 (item 581(v)(5), RC5 of F20k3): Common::Thread::Join of an emulator thread (was "join" with PthreadJoin).
	EmuJoin, Count
};
constexpr uint8_t kFirstEmuWait      = static_cast<uint8_t>(Wait::EmuMutex);
constexpr uint8_t kFirstGuestHleWait = static_cast<uint8_t>(Wait::Vblank);
// F20j3 (item 574(d)): EMU_WAIT kinds. F20j4 (item 581(v)(5), RC5 of F20k3): the class is by who clears the wait
// condition. EMU_WAIT - the device emulation, the host I/O or an emulator thread: EmuMutex .. Av, Vblank (the present
// thread counts the vblanks), Audio (the audio device emulation sets the pace), Aio (the emulator runs the request), Net
// (the host network), EmuJoin. GUEST_SLEEP - another guest thread or a deadline the guest asked for: the older kinds
// (cond, mutex, sem, psem, evf, eq, sleep) and Once, Join (PthreadJoin only), Addr, Fiber, Ult, Rwlock.
[[nodiscard]] constexpr bool IsEmuWait(uint8_t kind) {
	return (kind >= kFirstEmuWait && kind < kFirstGuestHleWait) || kind == static_cast<uint8_t>(Wait::Vblank) ||
	       kind == static_cast<uint8_t>(Wait::Audio) || kind == static_cast<uint8_t>(Wait::Aio) ||
	       kind == static_cast<uint8_t>(Wait::Net) || kind == static_cast<uint8_t>(Wait::EmuJoin);
}
// F20j3: a wait whose waker is its peer (the owner at entry): item 550(g)(2)(iv) "mutex - to peer".
[[nodiscard]] constexpr bool MutexLike(uint8_t kind) {
	return kind == static_cast<uint8_t>(Wait::Mutex) || kind == static_cast<uint8_t>(Wait::EmuMutex) ||
	       kind == static_cast<uint8_t>(Wait::Spin) || kind == static_cast<uint8_t>(Wait::Rwlock) ||
	       kind == static_cast<uint8_t>(Wait::Ult);
}
// The partition of one sample of one thread, exactly one (item 550(g)(2)): H > W > R > r > Sr > Sw > S; X - the slot
// was not live in that sample (registered later or exited).
enum class State : uint8_t { X = 0, H, W, R, Rr, Sr, Sw, S, Count };

[[nodiscard]] const char* CallName(uint8_t call);
[[nodiscard]] const char* WaitName(uint8_t kind);
[[nodiscard]] const char* StateName(State state);

// ---- start ----
void Init();       // Emulator::Run, first statement: reads both variables once, starts the sampler at 1
void LogHeader();  // Emulator::Run after the log is up: the line "DiagB32: mode=1 ..." / "TestB32: config ..."

// ---- registry (sites) ----
[[nodiscard]] int32_t SelfSlot();                     // slot index + 1 of this thread, registers it lazily (0 = none)
void                  RegisterRole(const char* role); // FrameStats::RegisterCurrentThread (Main, Gpu, Present, Record)
// F20j3 (item 574(g)(2)): the role threads that advance the conditions of the emulator waits - the "peer" of a mark.
// RegisterRole("Present" | "Gpu" | "ASubmit" | "POps" | "Relay" | "Main" | "Record") publishes the slot.
enum class Peer : uint8_t { Present = 0, Gpu, ASubmit, POps, Relay, Main, Record, Count };
[[nodiscard]] int32_t PeerSlot(Peer peer);            // slot + 1 of the role thread, 0 - not registered (yet)
[[nodiscard]] int32_t SelfSlotIfRegistered();         // slot + 1 of this thread if registered, else 0 (never registers)
[[nodiscard]] int32_t SlotOfOsTid(uint32_t os_tid);   // slot + 1 of a registered thread by its OS id, 0 - none
int32_t               RegisterGuest(int32_t gid, const char* name); // guest thread start; returns slot + 1
void                  Unregister();                   // guest thread cleanup

// "Last signaller" word: (NowNs >> 10) << 16 | (slot + 1). Kept in emulator objects (host heap) and read by the waiter.
[[nodiscard]] uint64_t PackSig();
[[nodiscard]] int32_t  SigWaker(uint64_t packed, uint64_t since_ns); // slot + 1 if the signal is not older than since
// F20j3 (item 574(g)(2)): PackSig of a registered thread only (an unregistered signaller - slot 0, it is not registered).
[[nodiscard]] uint64_t PackSigIfRegistered();
// F20j3: the last signaller of a std::condition_variable (or any object without its own field) - a side table of
// atomics on the host heap keyed by the object's address (12-bit tag in the word; another object of the same bucket
// evicts - then SignalOf returns 0, the waker is unknown). NoteSignal - before the notify, one test of g_on.
void                   NoteSignalSlow(const void* obj);
[[nodiscard]] uint64_t SignalOf(const void* obj); // packed (as PackSig) or 0

// ---- marks ----
class Mark {
public:
	Mark() = default;
	~Mark() {
		if (m_active) {
			EndSlow(0, false);
		}
	}
	Mark(const Mark&)            = delete;
	Mark& operator=(const Mark&) = delete;

	void BeginH(Call call);
	void BeginW(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us);
	// F20j3 (item 574(g)(1)): BeginW of a REGISTERED thread only (no lazy registration of worker threads); the
	// emulator-wait sites and the primitives use it. A thread without a slot gets no mark.
	void BeginWReg(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us);
	// F20j4 (item 581(v)(2), RC2 of F20k3): BeginW / BeginWReg / BeginWLock store a peer equal to the thread's own slot
	// as 0 (a thread does not wait for itself - the peer is unknown).
	// F20j4 (item 581(v)(4), RC4 of F20k3): a contended lock acquisition (Common::Mutex::LockB32, TrackedMutex) - as
	// BeginWReg, but no mark while the slot's current mark is any H:<call> (the H mark already names this wait: H > W of
	// item 550(g)(2); the inputs of RC7 / RC5 of item 550(v) stay as before F20j3).
	void BeginWLock(Wait kind, const void* obj, int32_t peer_slot1);
	// Ends the mark (restores the previous one). For a W mark a wait record is pushed if it lasted >= 10 ms, with the
	// waker (slot + 1, 0 = none) and whether it ended by its timeout. Inline: at KYTY_DIAG_B32=0 (no Begin) a site's End
	// is one test of this stack object's flag, no call.
	void End(int32_t waker_slot1, bool timed_out) {
		if (m_active) {
			EndSlow(waker_slot1, timed_out);
		}
	}
	// The mutex wait: the waker is the owner at entry (item 550(g)(2)(iv): "mutex - to peer").
	void EndWithPeer(bool timed_out) {
		if (m_active) {
			End(m_peer, timed_out);
		}
	}
	// F20j3: ends a wait on obj with the waker from the side table (NoteSignal of obj); at =0 one test of the flag.
	void EndSig(const void* obj, bool timed_out = false) {
		if (m_active) {
			EndSlow(SigWaker(SignalOf(obj), m_since), timed_out);
		}
	}

	[[nodiscard]] bool     Active() const { return m_active; }
	[[nodiscard]] uint64_t SinceNs() const { return m_since; }

private:
	void EndSlow(int32_t waker_slot1, bool timed_out);

	bool     m_active     = false;
	int32_t  m_slot       = -1;
	uint32_t m_prev_mark  = 0;
	uint64_t m_prev_obj   = 0;
	uint64_t m_prev_since = 0;
	int32_t  m_prev_peer  = 0;
	uint32_t m_mark       = 0;
	uint64_t m_obj        = 0;
	uint64_t m_since      = 0;
	int32_t  m_peer       = 0;
	uint64_t m_req_us     = 0;
};

// ---- GuestGpu and flip bookkeeping (sites) ----
void                  NoteSubmit(uint64_t seq);            // GuestGpu::Enqueue, the submitting (guest) thread
void                  NoteCurrentSubmission(uint64_t seq); // GuestGpu::ThreadRun, the popped submission
[[nodiscard]] int32_t LastSubmitWaker(uint64_t since_ns);  // waker of W:gpu_idle (RC5(v))
void                  NoteFlipRequest(uint64_t request_id, bool cpu_source); // ReserveFlipRequest, after OK
void OnFlip(uint64_t n, uint64_t request_id, uint64_t reserve_host_ns); // present thread, after flip_status.count++

// ---- stand KYTY_TEST_B32 ----
void TestArm();           // window.cpp, the first "Level has started: <name>" line
void TestPresentPoint();  // present site, inside H:present
void TestGpuSleepPoint(); // GuestGpu loop top, outside every mark

// F20j3 (item 574(g)(1)): the last signaller of obj for a std::condition_variable wait (one test of g_on).
inline void NoteSignal(const void* obj) {
	if (g_on) [[unlikely]] {
		NoteSignalSlow(obj);
	}
}

// F20j3 (item 574(g)(1)): a std mutex type whose CONTENDED acquisition is marked W:<K> (default emu_mutex) with the peer
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
};

// =====================================================================================================================
// Core: pure parts, unit-tested without the game (tests/DiagB32Tests.cpp, target diag_b32_tests).
// =====================================================================================================================
namespace Core {

[[nodiscard]] constexpr uint32_t MarkWord(State state, uint8_t kind) {
	return (static_cast<uint32_t>(state) << 8u) | kind;
}
[[nodiscard]] constexpr uint16_t Code(State state, uint8_t kind) {
	return static_cast<uint16_t>((static_cast<uint32_t>(state) << 8u) | kind);
}
[[nodiscard]] constexpr State CodeState(uint16_t code) {
	return static_cast<State>(code >> 8u);
}
[[nodiscard]] constexpr uint8_t CodeKind(uint16_t code) {
	return static_cast<uint8_t>(code & 0xffu);
}

// Kernel thread state (KTHREAD_STATE of SYSTEM_THREAD_INFORMATION.ThreadState): Ready 1, Running 2, Standby 3,
// Transition 6, DeferredReady 7 -> "ready / waits for a processor" (Sr); Waiting 5, GateWaitObsolete 8,
// WaitingForProcessOutSwap 9 -> "waits" (Sw:<WaitReason>); anything else -> S.
[[nodiscard]] bool KernelReady(uint32_t thread_state);
[[nodiscard]] bool KernelWaiting(uint32_t thread_state);

// One sample of one live thread. mark - the slot's mark word (0 = none, MarkWord(H|W, kind)); cpu_ns - CPU of the
// thread since its previous sample (QueryThreadCycleTime converted like FrameStats::ThreadCpuNs, RC4); interval_ns -
// time since the previous sample; kq - the kernel state of this sample is known (RC3).
// H > W > R (cpu >= 50 % of the interval) > r (cpu > 0) > Sr > Sw > S.
[[nodiscard]] uint16_t Classify(uint32_t mark, uint64_t cpu_ns, uint64_t interval_ns, bool kq, uint32_t kthread_state,
                                uint32_t kwait_reason);

struct Agg {
	uint32_t st[static_cast<size_t>(State::Count)] {};
	uint32_t h[static_cast<size_t>(Call::Count)] {};
	uint32_t w[static_cast<size_t>(Wait::Count)] {};
	uint32_t swr[64] {}; // Sw by WaitReason (63 = 63 and above)
	void     Add(uint16_t code);
	[[nodiscard]] uint32_t Total() const; // I1: X + R + r + Sr + S + sum(Sw) + sum(W) + sum(H) - one per sample
	[[nodiscard]] uint32_t SumH() const;
	[[nodiscard]] uint32_t SumW() const;
	[[nodiscard]] uint32_t SumSw() const;
};

struct GapStats {
	uint32_t samples     = 0;
	uint64_t sgap_max_ns = 0; // over [win_start, t_1, ..., t_n, win_end] (RC1: the window from the previous flip)
	uint32_t gap3p       = 0; // gaps > 3 P (RC12)
	bool     i2_ok       = true; // I2': samples >= floor(window / (2 P))
	bool     monotonic   = true;
};
// t - the sample times inside (win_start, win_end], in the order they were taken.
[[nodiscard]] GapStats Gaps(const uint64_t* t, size_t n, uint64_t win_start, uint64_t win_end, uint64_t period_ns);

// F20j2 (item 552(v)(1), RC1 of F20k): the kernel query schedule of the sampler. A sample queries the kernel thread
// state only if >= kKernelAfterNs passed since the previous flip and (the kernel-query time of the open window + the
// cost of the last query) <= (time since the previous flip) / kKqBudgetDiv. The first query of the process (no last
// cost yet) - at the first sample >= kKernelAfterNs. The start probe of Run (kstate) does not enter the schedule.
struct KqSchedule {
	uint64_t win_start  = 0; // the previous flip (0 - no flip yet: no query)
	uint64_t win_kq_ns  = 0; // kernel-query time inside the open window
	uint64_t last_kq_ns = 0; // the cost of the last query (0 - none yet)
	[[nodiscard]] bool Due(uint64_t now_ns) const;
	void               Done(uint64_t cost_ns);
	// The window closed at flip_ns; carried_kq_ns - kernel-query time of samples already after flip_ns.
	void NewWindow(uint64_t flip_ns, uint64_t carried_kq_ns);
};

// F20j2 (item 552(v)(1), RC1(b) of F20k): the absolute sample period. The next sample begins P after the BEGIN of the
// previous one; a sample (with the boundary work after it) longer than P is followed at once - no catch-up of the
// missed periods, the kernel query does not stretch the step.
[[nodiscard]] uint64_t NextBegin(uint64_t begin_ns, uint64_t now_ns);

// F20j2 (item 552(v)(1)): for the n samples of one window (t - sample times, oldest first; kq[i] - sample i has its own
// kernel snapshot taken at kq_t[i]) out[i] = i for a sample with its own snapshot; otherwise the index of the sample
// whose snapshot is nearest in time to t[i] and not farther than max_ns (ties - the earlier one), or -1.
void NearestSnapshot(const uint64_t* t, const uint8_t* kq, const uint64_t* kq_t, size_t n, uint64_t max_ns,
                     int32_t* out);

// The window's samples in the history ring (RC1, RC11: the window is (start, end], start = the previous flip).
// t / cost / kq - ring arrays of size hist, hpos - samples taken so far (the newest is hpos - 1). idx receives the ring
// positions (absolute sample numbers) oldest first; instr_ns = extra_ns + sum(cost) of the window's samples (RC9);
// exhausted - the ring no longer holds the window start (a ring_drop).
void WindowSamples(const uint64_t* t, const uint64_t* cost, const uint8_t* kq, uint64_t hpos, uint32_t hist,
                   uint64_t start, uint64_t end, uint64_t extra_ns, std::vector<uint64_t>* idx, uint64_t* instr_ns,
                   uint32_t* kq_n, bool* exhausted);

// I3: other_us = sys_busy_us - proc_us (signed by definition).
[[nodiscard]] int64_t OtherUs(uint64_t sys_busy_us, uint64_t proc_us);

// The name in a line: [A-Za-z0-9_.-] kept, everything else -> '_', at most 31 characters, empty -> "-" (RC13: a name
// can neither start with '%' nor carry a marker of the F20c reader such as "Vulkan pipeline cache: saved").
[[nodiscard]] std::string SafeName(const char* name);

// ---- registry ----
struct alignas(64) Slot {
	std::atomic<uint32_t> seq {0};   // seqlock word: odd while the owner writes the mark
	std::atomic<uint32_t> mark {0};  // MarkWord(H|W, kind), 0 = none
	std::atomic<uint64_t> obj {0};
	std::atomic<uint64_t> since {0}; // ns (FrameStats::NowNs)
	std::atomic<int32_t>  peer {0};  // slot + 1 (mutex owner at entry), 0 = none
	std::atomic<uint32_t> live {0};  // 0 empty, 1 live, 2 exited
	// Static after `live` is published (release); the guest fields may be set once more by RegisterGuest.
	std::atomic<int32_t>  gid {0};
	uint32_t              os_tid = 0;
	void*                 handle = nullptr;
	char                  role[12] {};
	char                  name[32] {};
};

struct MarkSnap {
	uint32_t mark  = 0;
	uint64_t obj   = 0;
	uint64_t since = 0;
	int32_t  peer  = 0;
};

class Registry {
public:
	// Returns the slot index or -1 (the registry is full: slot_full + 1).
	int32_t Allocate(uint32_t os_tid, void* handle, const char* role, const char* name, int32_t gid);
	// Owner-only write of the mark under the seqlock.
	void WriteMark(int32_t idx, uint32_t mark, uint64_t obj, uint64_t since, int32_t peer);
	// Reader: 3 attempts; a torn read after them returns false and counts torn + 1.
	bool ReadMark(int32_t idx, MarkSnap* out);

	Slot                  slots[kSlots];
	std::atomic<uint32_t> count {0};
	std::atomic<uint64_t> slot_full {0};
	std::atomic<uint64_t> torn {0};
};

// ---- wait ring (multi-producer, one reader) ----
struct WaitRec {
	uint64_t start_ns = 0;
	uint64_t end_ns   = 0;
	uint64_t obj      = 0;
	uint64_t req_us   = 0;
	int32_t  slot1    = 0; // waiting thread, slot + 1
	int32_t  waker1   = 0; // slot + 1, 0 = none
	int32_t  peer1    = 0; // F20j3 (item 574(g)(2), (d)): the mark's peer, slot + 1, 0 = none
	uint8_t  kind     = 0;
	uint8_t  timed_out = 0;
	uint8_t  open     = 0; // a W mark still active at the window end (not from the ring)
};

class WaitRing {
public:
	void Push(const WaitRec& rec); // = Write(Reserve(), rec)
	// F20j2 (RC4 of F20k): the two halves of Push - the position, then the record (a writer can be preempted between).
	uint64_t Reserve();
	void     Write(uint64_t i, const WaitRec& rec);
	// Moves every record written since the previous call into out, oldest first. Positions the reader no longer holds
	// (more than kWaitRing behind) are counted in drop. F20j2 (item 552(v)(4), RC4 of F20k): the drain stops at a
	// position whose write has not finished (not started, or in progress) and continues there on the next call; torn
	// counts only a position overwritten by a later lap (before or while it is read). F20j3 (item 554(v)(1), Z1): held
	// (if given) gets + the positions the drain left behind when it stopped (the stopped one and all after it).
	void Drain(std::vector<WaitRec>* out, uint64_t* drop, uint64_t* torn, uint64_t* held = nullptr);

	struct alignas(64) Entry {
		std::atomic<uint64_t> seq {0}; // 2 * index + 1 while written, 2 * index + 2 when complete
		std::atomic<uint64_t> start {0};
		std::atomic<uint64_t> end {0};
		std::atomic<uint64_t> obj {0};
		std::atomic<uint64_t> req {0};
		std::atomic<uint64_t> who {0}; // slot1 | waker1 << 20 | kind << 40 | timed_out << 48
		std::atomic<uint64_t> peer {0}; // F20j3: peer1
	};
	Entry                 e[kWaitRing];
	std::atomic<uint64_t> wpos {0};
	uint64_t              rpos = 0;
};

// ---- one closed window -> text ----
struct ThreadRow {
	int32_t     slot1     = 0;
	int32_t     gid       = 0;
	uint32_t    os_tid    = 0;
	std::string name;
	std::string role;
	Agg         agg;
	int64_t     cpu_us    = -1;
	MarkSnap    last;          // the last mark seen in the window (0 = none)
	bool        must      = false;
};

struct CpuRow {
	uint32_t    os_tid = 0;
	int32_t     slot1  = 0;
	std::string name;
	uint64_t    cpu_us = 0;
};

struct Counters {
	uint64_t slots        = 0;
	uint64_t slot_full    = 0;
	uint64_t torn         = 0;
	uint64_t ring_drop    = 0;
	uint64_t sgap_bad     = 0;
	uint64_t lines_cut    = 0;
	uint64_t short_stalls = 0;
	uint64_t others_cut   = 0;
	uint64_t w_cut        = 0;
	uint64_t rep_drop     = 0;
	uint64_t kq_fail      = 0;
	uint64_t print_us     = 0; // wall of the previous report's print on the present thread (reference)
	// F20j2 (item 552(v)(7), RC7 of F20k): a flip whose request entry (ring of 64) / submission entry (ring of 1024) was
	// overwritten before it was read.
	uint64_t req_miss     = 0;
	uint64_t sub_miss     = 0;
	// F20j3 (item 554(v)(1), Z1 of F20k2): wait-ring positions a drain left behind (an unfinished write stopped it).
	uint64_t ring_hold    = 0;
	// F20j2 (item 552(v)(3), RC3 of F20k): the zero invariants at the previous window close; Format prints
	// <name>_w = value - base (the increment over the window) next to the cumulative value. Rebase at every close.
	struct Base {
		uint64_t slot_full = 0;
		uint64_t torn      = 0;
		uint64_t ring_drop = 0;
		uint64_t sgap_bad  = 0;
		uint64_t lines_cut = 0;
		uint64_t req_miss  = 0;
		uint64_t sub_miss  = 0;
		uint64_t ring_hold = 0;
	} base;
	void Rebase();
};

struct Report {
	uint64_t n            = 0;
	uint64_t dt_us        = 0;
	uint64_t win_start_ns = 0;
	uint64_t win_end_ns   = 0;
	uint64_t instr_us     = 0;
	GapStats gaps;
	uint32_t kstate       = 0; // 1 - NtQuerySystemInformation(SystemProcessInformation) available
	uint32_t kq           = 0; // samples of the window with the kernel state
	uint32_t kq_n         = 0; // F20j2 (item 552(v)(1)): kernel queries in the window
	uint64_t kq_us        = 0; // F20j2: their time (inside instr_us too)
	uint64_t m5r_us       = 0; // F20j2 (item 552(e)(3)): the thread-list refresh (CreateToolhelp32Snapshot) in the window (inside instr_us)
	uint64_t proc_us      = 0;
	uint64_t sys_busy_us  = 0;
	uint64_t sys_idle_us  = 0;
	uint32_t ncpu         = 0;
	uint32_t snap_ok      = 1; // M1 / M5 taken at this window's own boundaries
	uint64_t snap_lag_us  = 0; // sampler processing time - flip time
	int32_t  flip_slot1   = 0;
	int32_t  flip_gid     = 0;
	uint32_t flip_src     = 0; // 1 cpu (VideoOutSubmitFlip), 2 gpu (flip packet), 0 unknown
	uint64_t lat_us       = 0;
	int32_t  vo_slot1     = 0;
	int32_t  gpu_slot1    = 0;
	std::vector<ThreadRow> threads;
	std::vector<WaitRec>   waits; // overlapping the window (ring records + open marks)
	std::vector<CpuRow>    cpu;   // M5, all threads of the process (top kCLines printed)
	uint32_t               gap3p_total = 0;
};

// Mandatory -t lines (RC2): the present thread, GuestGpu, flip_slot, every waiting thread / waker / peer of the
// window's -w records, every thread with R >= 10 % of the window samples; F20j2 (item 552(v)(5), RC5 of F20k): the async
// submitter (role ASubmit) in a window where it has at least one H:qlock / H:qsubmit sample. Sets ThreadRow::must.
void MarkMandatory(Report* report);

// Formats the lines (RC13: every line starts at column 0 with "DiagB32", no leading '%', no hexadecimal first field).
// Updates counters: lines_cut (mandatory beyond kMustCap), others_cut (non-mandatory beyond kOthersCap), w_cut,
// sgap_bad (I2' or non-monotonic samples).
[[nodiscard]] std::string Format(Report* report, Counters* counters);

// kq_us - the cost of the first kernel query of the process (the start probe of the sampler; F20j2, item 552(v)(1)).
[[nodiscard]] std::string HeaderLine(uint32_t ncpu, uint32_t kstate, uint64_t kq_us);

// F20j3 (item 574(g)(4)): a periodic work (the M5 thread-list refresh) on its own thread, so that its cost makes no gap
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
};

// F20j4 (item 581(v)(3), RC3 of F20k3): the M5 refresh time charged to the window it ran in. Add - the runs taken at a
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

// F20j3 (item 574(g)(3)): tests only - the registry and the wait ring as at KYTY_DIAG_B32=1 and g_on = true, without
// the sampler thread; the slot's mark and the drained wait records are read directly.
namespace Test {
void InitRuntime();
bool ReadSlotMark(int32_t slot1, Core::MarkSnap* out);
void DrainWaits(std::vector<Core::WaitRec>* out);
} // namespace Test

} // namespace Common::DiagB32

#endif /* KYTY_COMMON_DIAG_B32_H_ */
