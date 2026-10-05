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
// KYTY_DIAG_B32 unset, empty or "0": nothing - no thread, no line; every site tests the global flag g_on once.
// The knob is read ONCE by Init() at the start of Emulator::Run, before the first guest thread (RC10).
//
// KYTY_TEST_B32=<s>:<present|gpusleep>:<ms> (stand, default off, read once by Init): armed by the first guest line
// "Level has started: <non-blank name>"; once, <s> seconds after the arm, the present thread sleeps <ms> inside the
// mark H:present (present) or the GuestGpu thread sleeps <ms> between commands outside every mark (gpusleep).

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
constexpr uint32_t kSlots         = 256;
constexpr uint32_t kHist          = 512;       // per-slot history ring: 512 samples x 5 ms = 2.56 s (RC1: >= 2 s)
constexpr uint32_t kWaitRing      = 4096;
constexpr uint32_t kOthersCap     = 24;        // RC2: the cap applies only to the non-mandatory -t lines
constexpr uint32_t kMustCap       = 96;        // a mandatory -t line beyond this is cut and counted in lines_cut
constexpr uint32_t kWLinesCap     = 64;
constexpr uint32_t kCLines        = 8;

enum class Call : uint8_t { None = 0, Present, Acquire, QSubmit, QLock, Drain, SemWait, Protect, Fault, Count };
enum class Wait : uint8_t { None = 0, Cond, Mutex, Sem, PSem, Evf, Eq, Sleep, GpuIdle, GpuRegmem, Count };
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
int32_t               RegisterGuest(int32_t gid, const char* name); // guest thread start; returns slot + 1
void                  Unregister();                   // guest thread cleanup

// "Last signaller" word: (NowNs >> 10) << 16 | (slot + 1). Kept in emulator objects (host heap) and read by the waiter.
[[nodiscard]] uint64_t PackSig();
[[nodiscard]] int32_t  SigWaker(uint64_t packed, uint64_t since_ns); // slot + 1 if the signal is not older than since

// ---- marks ----
class Mark {
public:
	Mark() = default;
	~Mark() {
		if (m_active) {
			End(0, false);
		}
	}
	Mark(const Mark&)            = delete;
	Mark& operator=(const Mark&) = delete;

	void BeginH(Call call);
	void BeginW(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us);
	// Ends the mark (restores the previous one). For a W mark a wait record is pushed if it lasted >= 10 ms, with the
	// waker (slot + 1, 0 = none) and whether it ended by its timeout.
	void End(int32_t waker_slot1, bool timed_out);
	// The mutex wait: the waker is the owner at entry (item 550(g)(2)(iv): "mutex - to peer").
	void EndWithPeer(bool timed_out) {
		if (m_active) {
			End(m_peer, timed_out);
		}
	}

	[[nodiscard]] bool     Active() const { return m_active; }
	[[nodiscard]] uint64_t SinceNs() const { return m_since; }

private:
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
	uint8_t  kind     = 0;
	uint8_t  timed_out = 0;
	uint8_t  open     = 0; // a W mark still active at the window end (not from the ring)
};

class WaitRing {
public:
	void Push(const WaitRec& rec);
	// Moves every record written since the previous call into out; records overwritten before this call are counted in
	// drop, records whose write did not settle after 3 attempts in torn.
	void Drain(std::vector<WaitRec>* out, uint64_t* drop, uint64_t* torn);

	struct alignas(64) Entry {
		std::atomic<uint64_t> seq {0}; // 2 * index + 1 while written, 2 * index + 2 when complete
		std::atomic<uint64_t> start {0};
		std::atomic<uint64_t> end {0};
		std::atomic<uint64_t> obj {0};
		std::atomic<uint64_t> req {0};
		std::atomic<uint64_t> who {0}; // slot1 | waker1 << 20 | kind << 40 | timed_out << 48
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
// window's -w records, every thread with R >= 10 % of the window samples. Sets ThreadRow::must.
void MarkMandatory(Report* report);

// Formats the lines (RC13: every line starts at column 0 with "DiagB32", no leading '%', no hexadecimal first field).
// Updates counters: lines_cut (mandatory beyond kMustCap), others_cut (non-mandatory beyond kOthersCap), w_cut,
// sgap_bad (I2' or non-monotonic samples).
[[nodiscard]] std::string Format(Report* report, Counters* counters);

[[nodiscard]] std::string HeaderLine(uint32_t ncpu, uint32_t kstate);

} // namespace Core

} // namespace Common::DiagB32

#endif /* KYTY_COMMON_DIAG_B32_H_ */
