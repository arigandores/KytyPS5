# F20j3 (HPP-646): part 1 of patch_f20j3.py - diagB32.h / diagB32.cpp core and the Common::Mutex / CondVar primitives.
# Included by patch_f20j3.py (exec); uses edit(path, old, new).

H = 'src/common/diagB32.h'
C = 'src/common/diagB32.cpp'

# ---------------------------------------------------------------------------------------------------- diagB32.h
edit(H, r'''// "previous flip .. flip" (RC1, RC11) and, for a window of dt >= 100 ms, formats the lines DiagB32: / DiagB32-t: /
// DiagB32-w: / DiagB32-c: / DiagB32-x: which the present thread prints at its next flip site (after
// flip_status.count++). Marks: H:<call> (host calls of the emulator, M3), W:<kind> (guest waits and the GuestGpu waits,
// M2/M4); "last signaller" fields are atomics in emulator objects on the host heap (RC10).
''', r'''// "previous flip .. flip" (RC1, RC11) and, for a window of dt >= 100 ms, formats the lines DiagB32: / DiagB32-t: /
// DiagB32-w: / DiagB32-c: / DiagB32-x: which the present thread prints at its next flip site (after
// flip_status.count++). Marks: H:<call> (host calls of the emulator, M3), W:<kind> (guest waits and the GuestGpu waits,
// M2/M4); "last signaller" fields are atomics in emulator objects on the host heap (RC10).
// F20j3 (HPP-646; ROADMAP s122 item 574(g)): W:<kind> also on the host waits of the emulator itself (the kinds from
// EmuMutex on; the inventory - docs/track-f/f20j3/waits_f20j3.py): the contended Common::Mutex::Lock and TrackedMutex
// lock (peer - the owner), the wait loops of the flip queue, GuestGpu, the async submitter, the priority operations
// and the guest HLE calls (one mark over the whole loop; waker - the last signaller kept in the waited object, peer -
// the thread that advances the condition by the code); the M5 thread-list refresh runs on its own thread.
''')

edit(H, r'''enum class Call : uint8_t { None = 0, Present, Acquire, QSubmit, QLock, Drain, SemWait, Protect, Fault, Count };
enum class Wait : uint8_t { None = 0, Cond, Mutex, Sem, PSem, Evf, Eq, Sleep, GpuIdle, GpuRegmem, Count };
''', r'''enum class Call : uint8_t { None = 0, Present, Acquire, QSubmit, QLock, Drain, SemWait, Protect, Fault, Count };
enum class Wait : uint8_t {
	None = 0, Cond, Mutex, Sem, PSem, Evf, Eq, Sleep, GpuIdle, GpuRegmem,
	// F20j3 (item 574(g)(1)): appended after GpuRegmem - the older kinds keep their numbers and names.
	// Host waits of the emulator itself, EmuMutex .. Av (item 574(d): without a waker and a peer - EMU_WAIT:<kind>):
	EmuMutex, GpuWait, GpuCmd, FlipSlot, FlipDone, FlipCancel, FlipReq, VoPace, Relay, FramePool, RecWait, RecIdle,
	ASubIdle, ASubDrain, OpsWait, OpsIdle, PipeWait, PCopy, PmDrain, VmaFlush, RecQueue, MainTask, MainIdle, Spin, Av,
	// waits the guest asked for inside an HLE call (like cond / sem: GUEST_SLEEP:<kind> without a waker and a peer):
	Vblank, Once, Join, Addr, Aio, Fiber, Audio, Ult, Net, Rwlock, Count
};
constexpr uint8_t kFirstEmuWait      = static_cast<uint8_t>(Wait::EmuMutex);
constexpr uint8_t kFirstGuestHleWait = static_cast<uint8_t>(Wait::Vblank);
// F20j3 (item 574(d)): EMU_WAIT kinds.
[[nodiscard]] constexpr bool IsEmuWait(uint8_t kind) {
	return kind >= kFirstEmuWait && kind < kFirstGuestHleWait;
}
// F20j3: a wait whose waker is its peer (the owner at entry): item 550(g)(2)(iv) "mutex - to peer".
[[nodiscard]] constexpr bool MutexLike(uint8_t kind) {
	return kind == static_cast<uint8_t>(Wait::Mutex) || kind == static_cast<uint8_t>(Wait::EmuMutex) ||
	       kind == static_cast<uint8_t>(Wait::Spin) || kind == static_cast<uint8_t>(Wait::Rwlock) ||
	       kind == static_cast<uint8_t>(Wait::Ult);
}
''')

edit(H, r'''// ---- registry (sites) ----
[[nodiscard]] int32_t SelfSlot();                     // slot index + 1 of this thread, registers it lazily (0 = none)
void                  RegisterRole(const char* role); // FrameStats::RegisterCurrentThread (Main, Gpu, Present, Record)
''', r'''// ---- registry (sites) ----
[[nodiscard]] int32_t SelfSlot();                     // slot index + 1 of this thread, registers it lazily (0 = none)
void                  RegisterRole(const char* role); // FrameStats::RegisterCurrentThread (Main, Gpu, Present, Record)
// F20j3 (item 574(g)(2)): the role threads that advance the conditions of the emulator waits - the "peer" of a mark.
// RegisterRole("Present" | "Gpu" | "ASubmit" | "POps" | "Relay" | "Main" | "Record") publishes the slot.
enum class Peer : uint8_t { Present = 0, Gpu, ASubmit, POps, Relay, Main, Record, Count };
[[nodiscard]] int32_t PeerSlot(Peer peer);            // slot + 1 of the role thread, 0 - not registered (yet)
[[nodiscard]] int32_t SelfSlotIfRegistered();         // slot + 1 of this thread if registered, else 0 (never registers)
[[nodiscard]] int32_t SlotOfOsTid(uint32_t os_tid);   // slot + 1 of a registered thread by its OS id, 0 - none
''')

edit(H, r'''// "Last signaller" word: (NowNs >> 10) << 16 | (slot + 1). Kept in emulator objects (host heap) and read by the waiter.
[[nodiscard]] uint64_t PackSig();
[[nodiscard]] int32_t  SigWaker(uint64_t packed, uint64_t since_ns); // slot + 1 if the signal is not older than since
''', r'''// "Last signaller" word: (NowNs >> 10) << 16 | (slot + 1). Kept in emulator objects (host heap) and read by the waiter.
[[nodiscard]] uint64_t PackSig();
[[nodiscard]] int32_t  SigWaker(uint64_t packed, uint64_t since_ns); // slot + 1 if the signal is not older than since
// F20j3 (item 574(g)(2)): PackSig of a registered thread only (an unregistered signaller - slot 0, it is not registered).
[[nodiscard]] uint64_t PackSigIfRegistered();
// F20j3: the last signaller of a std::condition_variable (or any object without its own field) - a side table of
// atomics on the host heap keyed by the object's address (12-bit tag in the word; another object of the same bucket
// evicts - then SignalOf returns 0, the waker is unknown). NoteSignal - before the notify, one test of g_on.
void                   NoteSignalSlow(const void* obj);
[[nodiscard]] uint64_t SignalOf(const void* obj); // packed (as PackSig) or 0
''')

edit(H, r'''	void BeginH(Call call);
	void BeginW(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us);
''', r'''	void BeginH(Call call);
	void BeginW(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us);
	// F20j3 (item 574(g)(1)): BeginW of a REGISTERED thread only (no lazy registration of worker threads); the
	// emulator-wait sites and the primitives use it. A thread without a slot gets no mark.
	void BeginWReg(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us);
''')

edit(H, r'''	// The mutex wait: the waker is the owner at entry (item 550(g)(2)(iv): "mutex - to peer").
	void EndWithPeer(bool timed_out) {
		if (m_active) {
			End(m_peer, timed_out);
		}
	}
''', r'''	// The mutex wait: the waker is the owner at entry (item 550(g)(2)(iv): "mutex - to peer").
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
''')

edit(H, r'''// ---- stand KYTY_TEST_B32 ----
void TestArm();           // window.cpp, the first "Level has started: <name>" line
void TestPresentPoint();  // present site, inside H:present
void TestGpuSleepPoint(); // GuestGpu loop top, outside every mark
''', r'''// ---- stand KYTY_TEST_B32 ----
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
// = the slot of the thread that took it last (stored after each acquisition at =1; a holder is the last taker - the
// window between its acquisition and the store is not covered [I]). KYTY_DIAG_B32=0: lock() is one test of g_on and the
// std lock; try_lock() tests g_on only after a success; unlock() is the std unlock. Not for a mutex used with
// std::condition_variable (that needs std::unique_lock<std::mutex>).
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
			m_owner.store(SelfSlotIfRegistered(), std::memory_order_relaxed);
		}
		return ok;
	}
	void unlock() { m_m.unlock(); }
	void lock_shared() {
		if (g_on) [[unlikely]] {
			if (m_m.try_lock_shared()) {
				return;
			}
			Mark b32;
			b32.BeginWReg(K, this, m_owner.load(std::memory_order_relaxed), 0);
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
			b32.BeginWReg(K, this, m_owner.load(std::memory_order_relaxed), 0);
			m_m.lock();
			b32.EndWithPeer(false);
		}
		m_owner.store(SelfSlotIfRegistered(), std::memory_order_relaxed);
	}

	M                    m_m;
	std::atomic<int32_t> m_owner {0};
};
''')

edit(H, r'''struct WaitRec {
	uint64_t start_ns = 0;
	uint64_t end_ns   = 0;
	uint64_t obj      = 0;
	uint64_t req_us   = 0;
	int32_t  slot1    = 0; // waiting thread, slot + 1
	int32_t  waker1   = 0; // slot + 1, 0 = none
''', r'''struct WaitRec {
	uint64_t start_ns = 0;
	uint64_t end_ns   = 0;
	uint64_t obj      = 0;
	uint64_t req_us   = 0;
	int32_t  slot1    = 0; // waiting thread, slot + 1
	int32_t  waker1   = 0; // slot + 1, 0 = none
	int32_t  peer1    = 0; // F20j3 (item 574(g)(2), (d)): the mark's peer, slot + 1, 0 = none
''')

edit(H, r'''	// Moves every record written since the previous call into out, oldest first. Positions the reader no longer holds
	// (more than kWaitRing behind) are counted in drop. F20j2 (item 552(v)(4), RC4 of F20k): the drain stops at a
	// position whose write has not finished (not started, or in progress) and continues there on the next call; torn
	// counts only a position overwritten by a later lap (before or while it is read).
	void Drain(std::vector<WaitRec>* out, uint64_t* drop, uint64_t* torn);
''', r'''	// Moves every record written since the previous call into out, oldest first. Positions the reader no longer holds
	// (more than kWaitRing behind) are counted in drop. F20j2 (item 552(v)(4), RC4 of F20k): the drain stops at a
	// position whose write has not finished (not started, or in progress) and continues there on the next call; torn
	// counts only a position overwritten by a later lap (before or while it is read). F20j3 (item 554(v)(1), Z1): held
	// (if given) gets + the positions the drain left behind when it stopped (the stopped one and all after it).
	void Drain(std::vector<WaitRec>* out, uint64_t* drop, uint64_t* torn, uint64_t* held = nullptr);
''')

edit(H, r'''		std::atomic<uint64_t> who {0}; // slot1 | waker1 << 20 | kind << 40 | timed_out << 48
	};
''', r'''		std::atomic<uint64_t> who {0}; // slot1 | waker1 << 20 | kind << 40 | timed_out << 48
		std::atomic<uint64_t> peer {0}; // F20j3: peer1
	};
''')

edit(H, r'''	uint64_t req_miss     = 0;
	uint64_t sub_miss     = 0;
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
	} base;
''', r'''	uint64_t req_miss     = 0;
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
''')

edit(H, r'''// kq_us - the cost of the first kernel query of the process (the start probe of the sampler; F20j2, item 552(v)(1)).
[[nodiscard]] std::string HeaderLine(uint32_t ncpu, uint32_t kstate, uint64_t kq_us);

} // namespace Core
''', r'''// kq_us - the cost of the first kernel query of the process (the start probe of the sampler; F20j2, item 552(v)(1)).
[[nodiscard]] std::string HeaderLine(uint32_t ncpu, uint32_t kstate, uint64_t kq_us);

// F20j3 (item 574(g)(4)): a periodic work (the M5 thread-list refresh) on its own thread, so that its cost makes no gap
// of samples on the sampler thread. Start runs work(user) at once and then every period_ns (from the end of the
// previous run); TakeWorkNs returns the time of the runs finished since the previous take (it goes into instr_us of
// the window, as the refresh did on the sampler thread - RC9 unchanged).
class AsyncRefresh {
public:
	using Fn = void (*)(void* user);
	AsyncRefresh() = default;
	~AsyncRefresh();
	AsyncRefresh(const AsyncRefresh&)            = delete;
	AsyncRefresh& operator=(const AsyncRefresh&) = delete;
	void                   Start(Fn work, void* user, uint64_t period_ns);
	void                   Stop(); // tests
	[[nodiscard]] uint64_t TakeWorkNs();
	[[nodiscard]] uint64_t Runs() const { return m_runs.load(std::memory_order_acquire); }

private:
	struct Impl;
	Impl*                 m_impl = nullptr;
	std::atomic<uint64_t> m_work_ns {0};
	std::atomic<uint64_t> m_runs {0};
};

} // namespace Core

// F20j3 (item 574(g)(3)): tests only - the registry and the wait ring as at KYTY_DIAG_B32=1 and g_on = true, without
// the sampler thread; the slot's mark and the drained wait records are read directly.
namespace Test {
void InitRuntime();
bool ReadSlotMark(int32_t slot1, Core::MarkSnap* out);
void DrainWaits(std::vector<Core::WaitRec>* out);
} // namespace Test
''')

# ---------------------------------------------------------------------------------------------------- diagB32.cpp
edit(C, r'''#include <cstdlib>
#include <cstring>
#include <thread>
''', r'''#include <condition_variable>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <thread>
''')

edit(C, r'''const char* WaitName(uint8_t kind) {
	static constexpr const char* names[] = {"-", "cond", "mutex", "sem", "psem", "evf", "eq", "sleep", "gpu_idle", "gpu_regmem"};
	return kind < sizeof(names) / sizeof(names[0]) ? names[kind] : "?";
}
''', r'''const char* WaitName(uint8_t kind) {
	static constexpr const char* names[] = {"-", "cond", "mutex", "sem", "psem", "evf", "eq", "sleep", "gpu_idle", "gpu_regmem",
	                                        // F20j3 (item 574(g)(1)): emulator waits, in the order of enum Wait
	                                        "emu_mutex", "gpu_wait", "gpu_cmd", "flip_slot", "flip_done", "flip_cancel",
	                                        "flip_req", "vo_pace", "relay", "frame_pool", "rec_wait", "rec_idle",
	                                        "asub_idle", "asub_drain", "ops_wait", "ops_idle", "pipe_wait", "pcopy",
	                                        "pm_drain", "vma_flush", "rec_queue", "main_task", "main_idle", "spin", "av",
	                                        "vblank", "once", "join", "addr", "aio", "fiber", "audio", "ult", "net", "rwlock"};
	static_assert(sizeof(names) / sizeof(names[0]) == static_cast<size_t>(Wait::Count));
	return kind < sizeof(names) / sizeof(names[0]) ? names[kind] : "?";
}
''')

edit(C, r'''	x.who.store(static_cast<uint64_t>(static_cast<uint32_t>(rec.slot1) & 0xfffffu) |
	                (static_cast<uint64_t>(static_cast<uint32_t>(rec.waker1) & 0xfffffu) << 20u) |
	                (static_cast<uint64_t>(rec.kind) << 40u) | (static_cast<uint64_t>(rec.timed_out) << 48u),
	            std::memory_order_relaxed);
	x.seq.store(2 * i + 2, std::memory_order_release);
}

void WaitRing::Drain(std::vector<WaitRec>* out, uint64_t* drop, uint64_t* torn) {
''', r'''	x.who.store(static_cast<uint64_t>(static_cast<uint32_t>(rec.slot1) & 0xfffffu) |
	                (static_cast<uint64_t>(static_cast<uint32_t>(rec.waker1) & 0xfffffu) << 20u) |
	                (static_cast<uint64_t>(rec.kind) << 40u) | (static_cast<uint64_t>(rec.timed_out) << 48u),
	            std::memory_order_relaxed);
	x.peer.store(static_cast<uint32_t>(rec.peer1), std::memory_order_relaxed);
	x.seq.store(2 * i + 2, std::memory_order_release);
}

void WaitRing::Drain(std::vector<WaitRec>* out, uint64_t* drop, uint64_t* torn, uint64_t* held) {
''')

edit(C, r'''		if (s1 < want) {
			// F20j2 (RC4): the write of this position has not finished - not started (an older lap's word) or in progress
			// (2 * rpos + 1; the writer may be preempted between Reserve and the final word). Stop here; the next drain
			// (the next flip) continues from this position.
			break;
		}
''', r'''		if (s1 < want) {
			// F20j2 (RC4): the write of this position has not finished - not started (an older lap's word) or in progress
			// (2 * rpos + 1; the writer may be preempted between Reserve and the final word). Stop here; the next drain
			// (the next flip) continues from this position. F20j3 (Z1): the positions left behind - ring_hold.
			if (held != nullptr) {
				*held += w - rpos;
			}
			break;
		}
''')

edit(C, r'''			r.req_us       = x.req.load(std::memory_order_relaxed);
			const auto who = x.who.load(std::memory_order_relaxed);
''', r'''			r.req_us       = x.req.load(std::memory_order_relaxed);
			r.peer1        = static_cast<int32_t>(x.peer.load(std::memory_order_relaxed));
			const auto who = x.who.load(std::memory_order_relaxed);
''')

edit(C, r'''// The -w records printed: the closure (3 steps) of the chain participants first (the present thread, GuestGpu,
// flip_slot, threads with R >= 10 %), then the rest by overlap with the window up to kWLinesCap in all.
''', r'''// The -w records printed: the closure (3 steps) of the chain participants first (the present thread, GuestGpu,
// flip_slot, threads with R >= 10 %), then the rest by overlap with the window up to kWLinesCap in all. F20j3 (item
// 574(d)): the closure follows the waker and the peer of a record.
''')

edit(C, r'''				must.push_back(i);
				add(r.waits[i].waker1);
''', r'''				must.push_back(i);
				add(r.waits[i].waker1);
				add(r.waits[i].peer1);
''')

edit(C, r'''	for (auto i: pick) {
		if (auto* t = RowOf(&r, r.waits[i].waker1); t != nullptr) {
			t->must = true;
		}
	}
''', r'''	for (auto i: pick) {
		if (auto* t = RowOf(&r, r.waits[i].waker1); t != nullptr) {
			t->must = true;
		}
		if (auto* t = RowOf(&r, r.waits[i].peer1); t != nullptr) { // F20j3 (RC2: every waker / peer of the -w records)
			t->must = true;
		}
	}
''')

edit(C, r'''		Append(&out,
		       "DiagB32-w: n=%llu slot=%d tid=%d kind=%s obj=0x%llx start_us=%lld wait_us=%llu overlap_us=%llu waker=%d"
		       " waker_tid=%d req_us=%llu to=%u open=%u\n",
		       n, SlotIndex(w.slot1), GidOf(r, w.slot1), WaitName(w.kind), static_cast<unsigned long long>(w.obj),
		       (static_cast<long long>(w.start_ns) - static_cast<long long>(r.win_start_ns)) / 1000,
		       static_cast<unsigned long long>((w.end_ns - w.start_ns) / 1000u),
		       static_cast<unsigned long long>(Overlap(w, r.win_start_ns, r.win_end_ns) / 1000u), SlotIndex(w.waker1),
		       GidOf(r, w.waker1), static_cast<unsigned long long>(w.req_us), w.timed_out, w.open);
''', r'''		// F20j3 (item 574(d)): the record's peer (slot) and its guest id at the end of the line.
		Append(&out,
		       "DiagB32-w: n=%llu slot=%d tid=%d kind=%s obj=0x%llx start_us=%lld wait_us=%llu overlap_us=%llu waker=%d"
		       " waker_tid=%d req_us=%llu to=%u open=%u peer=%d peer_tid=%d\n",
		       n, SlotIndex(w.slot1), GidOf(r, w.slot1), WaitName(w.kind), static_cast<unsigned long long>(w.obj),
		       (static_cast<long long>(w.start_ns) - static_cast<long long>(r.win_start_ns)) / 1000,
		       static_cast<unsigned long long>((w.end_ns - w.start_ns) / 1000u),
		       static_cast<unsigned long long>(Overlap(w, r.win_start_ns, r.win_end_ns) / 1000u), SlotIndex(w.waker1),
		       GidOf(r, w.waker1), static_cast<unsigned long long>(w.req_us), w.timed_out, w.open, SlotIndex(w.peer1),
		       GidOf(r, w.peer1));
''')

edit(C, r'''	Append(&out,
	       "DiagB32-x: n=%llu slots=%llu slot_full=%llu slot_full_w=%llu torn=%llu torn_w=%llu ring_drop=%llu ring_drop_w=%llu"
	       " sgap_bad=%llu sgap_bad_w=%llu lines_cut=%llu lines_cut_w=%llu req_miss=%llu req_miss_w=%llu sub_miss=%llu"
	       " sub_miss_w=%llu short_stalls=%llu others_cut=%llu w_cut=%llu rep_drop=%llu kq_fail=%llu print_us=%llu gap3p=%u\n",
''', r'''	// F20j3 (item 554(v)(1), Z1): ring_hold / ring_hold_w at the end of the line.
	Append(&out,
	       "DiagB32-x: n=%llu slots=%llu slot_full=%llu slot_full_w=%llu torn=%llu torn_w=%llu ring_drop=%llu ring_drop_w=%llu"
	       " sgap_bad=%llu sgap_bad_w=%llu lines_cut=%llu lines_cut_w=%llu req_miss=%llu req_miss_w=%llu sub_miss=%llu"
	       " sub_miss_w=%llu short_stalls=%llu others_cut=%llu w_cut=%llu rep_drop=%llu kq_fail=%llu print_us=%llu gap3p=%u"
	       " ring_hold=%llu ring_hold_w=%llu\n",
''')

edit(C, r'''	       static_cast<unsigned long long>(counters->kq_fail), static_cast<unsigned long long>(counters->print_us),
	       r.gaps.gap3p);
	return out;
}
''', r'''	       static_cast<unsigned long long>(counters->kq_fail), static_cast<unsigned long long>(counters->print_us),
	       r.gaps.gap3p, static_cast<unsigned long long>(counters->ring_hold), dw(counters->ring_hold, b.ring_hold));
	return out;
}
''')

edit(C, r'''	base.req_miss  = req_miss;
	base.sub_miss  = sub_miss;
}
''', r'''	base.req_miss  = req_miss;
	base.sub_miss  = sub_miss;
	base.ring_hold = ring_hold;
}
''')

edit(C, r'''	return buf;
}

} // namespace Core
''', r'''	return buf;
}

// F20j3 (item 574(g)(4)): the refresher thread. A condition variable only to stop it (tests); the work runs unlocked.
struct AsyncRefresh::Impl {
	std::mutex              mutex;
	std::condition_variable cv;
	bool                    stop = false;
	std::thread             thread;
};

AsyncRefresh::~AsyncRefresh() {
	Stop();
}

void AsyncRefresh::Start(Fn work, void* user, uint64_t period_ns) {
	if (m_impl != nullptr) {
		return;
	}
	m_impl         = new Impl;
	auto* impl     = m_impl;
	impl->thread   = std::thread([this, impl, work, user, period_ns] {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
        using SetThreadDescriptionFn = HRESULT(WINAPI*)(HANDLE, PCWSTR);
        if (HMODULE k32 = GetModuleHandleW(L"kernel32.dll"); k32 != nullptr) {
            if (auto set_fn = reinterpret_cast<SetThreadDescriptionFn>(
                    reinterpret_cast<void*>(GetProcAddress(k32, "SetThreadDescription")));
                set_fn != nullptr) {
                set_fn(GetCurrentThread(), L"DiagB32M5"); // the refresh's CPU is visible in the -c lines
            }
        }
#endif
        for (;;) {
            const auto t0 = FrameStats::NowNs();
            work(user);
            m_work_ns.fetch_add(FrameStats::NowNs() - t0, std::memory_order_acq_rel);
            m_runs.fetch_add(1, std::memory_order_acq_rel);
            std::unique_lock lock(impl->mutex);
            if (impl->cv.wait_for(lock, std::chrono::nanoseconds(period_ns), [impl] { return impl->stop; })) {
                return;
            }
        }
    });
}

void AsyncRefresh::Stop() {
	if (m_impl == nullptr) {
		return;
	}
	{
		std::lock_guard lock(m_impl->mutex);
		m_impl->stop = true;
	}
	m_impl->cv.notify_all();
	if (m_impl->thread.joinable()) {
		m_impl->thread.join();
	}
	delete m_impl;
	m_impl = nullptr;
}

uint64_t AsyncRefresh::TakeWorkNs() {
	return m_work_ns.exchange(0, std::memory_order_acq_rel);
}

} // namespace Core
''')

edit(C, r'''std::atomic<int32_t>  g_vo_slot1 {0};
std::atomic<int32_t>  g_gpu_slot1 {0};
''', r'''std::atomic<int32_t>  g_vo_slot1 {0};
std::atomic<int32_t>  g_gpu_slot1 {0};
// F20j3 (item 574(g)(2)): the slot + 1 of every peer role (RegisterRole).
std::atomic<int32_t>  g_peer_slot1[static_cast<size_t>(Peer::Count)] {};

// F20j3 (item 574(g)(1)): the last signaller side table (std::condition_variable waits). The word: PackSig with the
// 12-bit tag of the object's address in bits 52..63 (the time field (NowNs >> 10) stays below 2^36 for 19 hours of
// process time and bits 52..63 of PackSig are zero; a longer run only loses the tag check - the waker is then unknown
// to the reading at most once per 2^12 objects [I]).
constexpr uint32_t    kSigTab = 4096;
std::atomic<uint64_t> g_sigtab[kSigTab] {};

uint32_t SigBucket(const void* obj) {
	const auto a = reinterpret_cast<uintptr_t>(obj);
	return static_cast<uint32_t>(((a >> 4u) ^ (a >> 16u)) % kSigTab);
}

uint64_t SigTag(const void* obj) {
	const auto a = reinterpret_cast<uintptr_t>(obj);
	return static_cast<uint64_t>(((a >> 3u) ^ (a >> 15u) ^ (a >> 27u)) & 0xfffu);
}
''')

edit(C, r'''		if (std::strcmp(role, "Present") == 0) {
			g_vo_slot1.store(slot1, std::memory_order_release);
		} else if (std::strcmp(role, "Gpu") == 0) {
			g_gpu_slot1.store(slot1, std::memory_order_release);
		}
	}
}
''', r'''		if (std::strcmp(role, "Present") == 0) {
			g_vo_slot1.store(slot1, std::memory_order_release);
		} else if (std::strcmp(role, "Gpu") == 0) {
			g_gpu_slot1.store(slot1, std::memory_order_release);
		}
		// F20j3 (item 574(g)(2)): the peer roles.
		static constexpr const char* peers[] = {"Present", "Gpu", "ASubmit", "POps", "Relay", "Main", "Record"};
		static_assert(sizeof(peers) / sizeof(peers[0]) == static_cast<size_t>(Peer::Count));
		for (size_t i = 0; i < sizeof(peers) / sizeof(peers[0]); i++) {
			if (std::strcmp(role, peers[i]) == 0) {
				g_peer_slot1[i].store(slot1, std::memory_order_release);
			}
		}
	}
}

int32_t PeerSlot(Peer peer) {
	const auto i = static_cast<size_t>(peer);
	return i < static_cast<size_t>(Peer::Count) ? g_peer_slot1[i].load(std::memory_order_acquire) : 0;
}

int32_t SelfSlotIfRegistered() {
	return t_slot1 > 0 ? t_slot1 : 0;
}

int32_t SlotOfOsTid(uint32_t os_tid) {
	if (g_reg == nullptr || os_tid == 0) {
		return 0;
	}
	const auto n = std::min<uint32_t>(g_reg->count.load(std::memory_order_acquire), kSlots);
	for (uint32_t i = 0; i < n; i++) {
		const auto& s = g_reg->slots[i];
		if (s.live.load(std::memory_order_acquire) == 1 && s.os_tid == os_tid) {
			return static_cast<int32_t>(i) + 1;
		}
	}
	return 0;
}
''')

edit(C, r'''int32_t SigWaker(uint64_t packed, uint64_t since_ns) {
	if (packed == 0) {
		return 0;
	}
''', r'''uint64_t PackSigIfRegistered() {
	return ((FrameStats::NowNs() >> 10u) << 16u) | (static_cast<uint64_t>(SelfSlotIfRegistered()) & 0xffffu);
}

void NoteSignalSlow(const void* obj) {
	g_sigtab[SigBucket(obj)].store((PackSigIfRegistered() & ((uint64_t {1} << 52u) - 1u)) | (SigTag(obj) << 52u),
	                               std::memory_order_relaxed);
}

uint64_t SignalOf(const void* obj) {
	const auto v = g_sigtab[SigBucket(obj)].load(std::memory_order_relaxed);
	if (v == 0 || (v >> 52u) != SigTag(obj)) {
		return 0;
	}
	return v & ((uint64_t {1} << 52u) - 1u);
}

int32_t SigWaker(uint64_t packed, uint64_t since_ns) {
	if (packed == 0) {
		return 0;
	}
''')

edit(C, r'''void Mark::EndSlow(int32_t waker_slot1, bool timed_out) {
''', r'''void Mark::BeginWReg(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us) {
	const auto slot1 = SelfSlotIfRegistered();
	if (slot1 <= 0 || g_reg == nullptr) {
		return;
	}
	auto& s      = g_reg->slots[slot1 - 1];
	m_slot       = slot1 - 1;
	m_prev_mark  = s.mark.load(std::memory_order_relaxed);
	m_prev_obj   = s.obj.load(std::memory_order_relaxed);
	m_prev_since = s.since.load(std::memory_order_relaxed);
	m_prev_peer  = s.peer.load(std::memory_order_relaxed);
	m_mark       = Core::MarkWord(State::W, static_cast<uint8_t>(kind));
	m_obj        = reinterpret_cast<uint64_t>(obj);
	m_since      = FrameStats::NowNs();
	m_peer       = peer_slot1;
	m_req_us     = req_us;
	g_reg->WriteMark(m_slot, m_mark, m_obj, m_since, m_peer);
	m_active = true;
}

void Mark::EndSlow(int32_t waker_slot1, bool timed_out) {
''')

edit(C, r'''	rec.slot1     = m_slot + 1;
	rec.waker1    = waker_slot1;
	rec.kind      = static_cast<uint8_t>(m_mark & 0xffu);
	rec.timed_out = timed_out ? 1 : 0;
	g_ring->Push(rec);
}
''', r'''	rec.slot1     = m_slot + 1;
	rec.waker1    = waker_slot1;
	rec.peer1     = m_peer; // F20j3 (item 574(g)(2))
	rec.kind      = static_cast<uint8_t>(m_mark & 0xffu);
	rec.timed_out = timed_out ? 1 : 0;
	g_ring->Push(rec);
}
''')

# ---- sampler: M5 off the sampler thread (item 574(g)(4)), ring_hold (Z1), the record's peer
edit(C, r'''struct M5Ent {
	uint32_t    os_tid  = 0;
	HANDLE      handle  = nullptr;
	std::string name;
	uint64_t    cyc     = 0;
	bool        have    = false;
	uint64_t    last_ns = 0;
	bool        valid   = false;
	bool        seen    = false;
};
''', r'''struct M5Ent {
	uint32_t    os_tid  = 0;
	HANDLE      handle  = nullptr;
	std::string name;
	uint64_t    cyc     = 0;
	bool        have    = false;
	uint64_t    last_ns = 0;
	bool        valid   = false;
	bool        seen    = false;
};

// F20j3 (item 574(g)(4)): the thread list built by the refresher thread (CreateToolhelp32Snapshot, OpenThread, names).
// It owns the handles: a vanished thread's handle goes to the graveyard with the generation of the list that dropped
// it and is closed once the sampler adopted a later generation (the sampler uses only handles of the list it adopted).
struct M5Pub {
	uint32_t    os_tid = 0;
	HANDLE      handle = nullptr;
	std::string name;
};

struct M5Shared {
	std::mutex                                  mutex;    // the published list (the sampler only try_locks it)
	std::vector<M5Pub>                          pub;
	uint64_t                                    pub_gen = 0;
	std::atomic<uint64_t>                       adopted {0}; // the generation the sampler uses
	// refresher thread only:
	std::vector<M5Pub>                          own;
	std::vector<std::pair<uint64_t, HANDLE>>    graveyard;
	uint64_t                                    gen = 0;
	uint32_t                                    pid = 0;
	GetThreadDescriptionFn                      gtd = nullptr;
};
''')

edit(C, r'''	void     KernelQuery();
	bool     KernelLookup(uint32_t tid, uint32_t* state, uint32_t* reason) const;
	void     M5Refresh(uint64_t now);
	void     M5Snapshot();
''', r'''	void     KernelQuery();
	bool     KernelLookup(uint32_t tid, uint32_t* state, uint32_t* reason) const;
	static void M5RefreshWork(void* user); // F20j3: runs on the refresher thread (Core::AsyncRefresh)
	void     M5Adopt();                     // F20j3: the sampler takes the last published list (try_lock only)
	void     M5Snapshot();
''')

edit(C, r'''	std::vector<M5Ent>        m_m5;
	uint64_t                  m_m5_next = 0;
''', r'''	std::vector<M5Ent>        m_m5;
	M5Shared                  m_m5s;          // F20j3 (item 574(g)(4))
	Core::AsyncRefresh        m_m5r;
	uint64_t                  m_m5_gen = 0;   // the generation of m_m5
	uint64_t                  m_ring_hold = 0; // F20j3 (Z1)
''')

edit(C, r'''void Sampler::M5Refresh(uint64_t now) {
	HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
	m_m5_next   = now + 1000000000ull;
	if (snap == INVALID_HANDLE_VALUE) {
		return;
	}
	for (auto& e: m_m5) {
		e.seen = false;
	}
	THREADENTRY32 te {};
	te.dwSize = sizeof(te);
	for (BOOL ok = Thread32First(snap, &te); ok != FALSE; ok = Thread32Next(snap, &te)) {
		if (te.th32OwnerProcessID != m_pid) {
			continue;
		}
		auto it = std::find_if(m_m5.begin(), m_m5.end(), [&](const M5Ent& e) { return e.os_tid == te.th32ThreadID; });
		if (it != m_m5.end()) {
			it->seen = true;
			continue;
		}
		M5Ent e;
		e.os_tid = te.th32ThreadID;
		e.handle = OpenThread(THREAD_QUERY_LIMITED_INFORMATION, FALSE, te.th32ThreadID);
		e.seen   = true;
		if (e.handle == nullptr) {
			continue;
		}
		if (m_gtd != nullptr) {
			PWSTR desc = nullptr;
			if (SUCCEEDED(m_gtd(e.handle, &desc)) && desc != nullptr) {
				char buf[64] {};
				for (size_t i = 0; desc[i] != 0 && i + 1 < sizeof(buf); i++) {
					buf[i] = desc[i] < 128 ? static_cast<char>(desc[i]) : '_';
				}
				e.name = Core::SafeName(buf);
				LocalFree(desc);
			}
		}
		if (e.name.empty() || e.name == "-") {
			e.name = "t" + std::to_string(e.os_tid);
		}
		m_m5.push_back(std::move(e));
	}
	CloseHandle(snap);
	for (auto& e: m_m5) {
		if (!e.seen && e.handle != nullptr) {
			CloseHandle(e.handle);
			e.handle = nullptr;
		}
	}
	m_m5.erase(std::remove_if(m_m5.begin(), m_m5.end(), [](const M5Ent& e) { return e.handle == nullptr; }), m_m5.end());
}
''', r'''// F20j3 (item 574(g)(4)): was Sampler::M5Refresh on the sampler thread (76.7 ms in b32_pp frame 1798 = the gap of
// samples, item 574(a)(6)); now the same enumeration on the refresher thread, published for M5Adopt.
void Sampler::M5RefreshWork(void* user) {
	auto&  m    = *static_cast<M5Shared*>(user);
	HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
	if (snap == INVALID_HANDLE_VALUE) {
		return;
	}
	std::vector<uint32_t> seen;
	THREADENTRY32         te {};
	te.dwSize = sizeof(te);
	for (BOOL ok = Thread32First(snap, &te); ok != FALSE; ok = Thread32Next(snap, &te)) {
		if (te.th32OwnerProcessID != m.pid) {
			continue;
		}
		seen.push_back(te.th32ThreadID);
		auto it = std::find_if(m.own.begin(), m.own.end(), [&](const M5Pub& e) { return e.os_tid == te.th32ThreadID; });
		if (it != m.own.end()) {
			continue;
		}
		M5Pub e;
		e.os_tid = te.th32ThreadID;
		e.handle = OpenThread(THREAD_QUERY_LIMITED_INFORMATION, FALSE, te.th32ThreadID);
		if (e.handle == nullptr) {
			continue;
		}
		if (m.gtd != nullptr) {
			PWSTR desc = nullptr;
			if (SUCCEEDED(m.gtd(e.handle, &desc)) && desc != nullptr) {
				char buf[64] {};
				for (size_t i = 0; desc[i] != 0 && i + 1 < sizeof(buf); i++) {
					buf[i] = desc[i] < 128 ? static_cast<char>(desc[i]) : '_';
				}
				e.name = Core::SafeName(buf);
				LocalFree(desc);
			}
		}
		if (e.name.empty() || e.name == "-") {
			e.name = "t" + std::to_string(e.os_tid);
		}
		m.own.push_back(std::move(e));
	}
	CloseHandle(snap);
	m.gen++;
	for (auto& e: m.own) {
		if (std::find(seen.begin(), seen.end(), e.os_tid) == seen.end()) {
			m.graveyard.emplace_back(m.gen, e.handle); // the sampler may still use it until it adopts gen
			e.handle = nullptr;
		}
	}
	m.own.erase(std::remove_if(m.own.begin(), m.own.end(), [](const M5Pub& e) { return e.handle == nullptr; }), m.own.end());
	{
		std::lock_guard lock(m.mutex);
		m.pub     = m.own;
		m.pub_gen = m.gen;
	}
	const auto adopted = m.adopted.load(std::memory_order_acquire);
	m.graveyard.erase(std::remove_if(m.graveyard.begin(), m.graveyard.end(),
	                                 [&](const std::pair<uint64_t, HANDLE>& g) {
		                                 if (g.first <= adopted) {
			                                 CloseHandle(g.second);
			                                 return true;
		                                 }
		                                 return false;
	                                 }),
	                  m.graveyard.end());
}

void Sampler::M5Adopt() {
	std::unique_lock lock(m_m5s.mutex, std::try_to_lock);
	if (!lock.owns_lock() || m_m5s.pub_gen == m_m5_gen) {
		return;
	}
	std::vector<M5Ent> next;
	next.reserve(m_m5s.pub.size());
	for (const auto& p: m_m5s.pub) {
		M5Ent e;
		e.os_tid = p.os_tid;
		e.handle = p.handle;
		e.name   = p.name;
		auto it  = std::find_if(m_m5.begin(), m_m5.end(), [&](const M5Ent& o) { return o.os_tid == p.os_tid; });
		if (it != m_m5.end()) { // the cycle state continues
			e.cyc     = it->cyc;
			e.have    = it->have;
			e.last_ns = it->last_ns;
			e.valid   = it->valid;
		}
		next.push_back(std::move(e));
	}
	m_m5_gen = m_m5s.pub_gen;
	lock.unlock();
	m_m5 = std::move(next);
	m_m5s.adopted.store(m_m5_gen, std::memory_order_release);
}
''')

edit(C, r'''	m_c.req_miss  = g_req_miss.load(std::memory_order_relaxed);
	m_c.sub_miss  = g_sub_miss.load(std::memory_order_relaxed);
}
''', r'''	m_c.req_miss  = g_req_miss.load(std::memory_order_relaxed);
	m_c.sub_miss  = g_sub_miss.load(std::memory_order_relaxed);
	m_c.ring_hold = m_ring_hold; // F20j3 (Z1)
}
''')

edit(C, r'''			w.slot1    = row.slot1;
			w.waker1   = (m_last_mark[i].mark & 0xffu) == static_cast<uint32_t>(Wait::Mutex) ? m_last_mark[i].peer : 0;
			w.kind     = static_cast<uint8_t>(m_last_mark[i].mark & 0xffu);
''', r'''			w.slot1    = row.slot1;
			// F20j3 (item 574(d)): mutex-like kinds (mutex, emu_mutex, spin) - the waker is the peer; every record - its peer.
			w.waker1   = MutexLike(static_cast<uint8_t>(m_last_mark[i].mark & 0xffu)) ? m_last_mark[i].peer : 0;
			w.peer1    = m_last_mark[i].peer;
			w.kind     = static_cast<uint8_t>(m_last_mark[i].mark & 0xffu);
''')

edit(C, r'''	uint64_t m5r = 0;
	if (t0 >= m_m5_next) {
		M5Refresh(t0);
		m5r = FrameStats::NowNs() - t0; // F20j2 (item 552(e)(3)): the refresh's share of the boundary work
	}
	M5Snapshot();
''', r'''	// F20j3 (item 574(g)(4)): the refresh runs on the refresher thread; its time finished since the previous flip goes
	// into instr_us and m5r_us of the new window as before (RC9; it is no longer sampler time - no gap of samples).
	const uint64_t m5r = m_m5r.TakeWorkNs();
	M5Adopt();
	M5Snapshot();
''')

edit(C, r'''	m_ring_tmp.clear();
	g_ring->Drain(&m_ring_tmp, &m_c.ring_drop, &m_ring_torn);
''', r'''	m_ring_tmp.clear();
	g_ring->Drain(&m_ring_tmp, &m_c.ring_drop, &m_ring_torn, &m_ring_hold);
''')

edit(C, r'''	// The boundary work runs after the flip: it is sampler time inside the new window (RC9 instr_us).
	m_win_extra_ns += FrameStats::NowNs() - t0;
	m_win_m5r_ns += m5r;
}
''', r'''	// The boundary work runs after the flip: it is sampler time inside the new window (RC9 instr_us); F20j3 - plus the
	// refresh time of the refresher thread (m5r, RC9 as before).
	m_win_extra_ns += FrameStats::NowNs() - t0 + m5r;
	m_win_m5r_ns += m5r;
}
''')

edit(C, r'''	m_kmap.reserve(1024);
	if (m_ntq != nullptr) {
''', r'''	m_kmap.reserve(1024);
	// F20j3 (item 574(g)(4)): the thread list is refreshed every 1 s on its own thread (was: on this thread).
	m_m5s.pid = m_pid;
	m_m5s.gtd = m_gtd;
	m_m5r.Start(&Sampler::M5RefreshWork, &m_m5s, 1000000000ull);
	if (m_ntq != nullptr) {
''')

edit(C, r'''void LogHeader() {
''', r'''namespace Test {

void InitRuntime() {
	if (g_reg == nullptr) {
		g_reg  = new Core::Registry;
		g_ring = new Core::WaitRing;
	}
	g_on = true;
}

bool ReadSlotMark(int32_t slot1, Core::MarkSnap* out) {
	return g_reg != nullptr && slot1 > 0 && g_reg->ReadMark(slot1 - 1, out);
}

void DrainWaits(std::vector<Core::WaitRec>* out) {
	uint64_t drop = 0;
	uint64_t torn = 0;
	if (g_ring != nullptr) {
		g_ring->Drain(out, &drop, &torn);
	}
}

} // namespace Test

void LogHeader() {
''')

# ---------------------------------------------------------------------------------------------------- threads
TH = 'src/common/threads.h'
TC = 'src/common/threads.cpp'

edit(TH, r'''	void Lock();
	void Unlock();
	bool TryLock();

	friend class CondVar;

	KYTY_CLASS_NO_COPY(Mutex);

private:
	std::unique_ptr<MutexPrivate> m_mutex;
};
''', r'''	void Lock();
	void Unlock();
	bool TryLock();

	friend class CondVar;

	KYTY_CLASS_NO_COPY(Mutex);

private:
	void LockB32(); // Track F, F20j3 (KYTY_DIAG_B32=1): the acquisition with W:emu_mutex when contended

	std::unique_ptr<MutexPrivate> m_mutex;
};
''')

edit(TH, r'''	void Signal();
	void SignalAll();

	static void SetWaitPollCallback(wait_poll_func_t callback);
''', r'''	void Signal();
	void SignalAll();
	// Track F, F20j3 (KYTY_DIAG_B32): the slot + 1 of the last signaller if it signalled at or after since_ns, else 0.
	[[nodiscard]] int32_t B32Waker(uint64_t since_ns) const;

	static void SetWaitPollCallback(wait_poll_func_t callback);
''')

edit(TC, r'''	~CondVarPrivate() = default;
	KYTY_CLASS_NO_COPY(CondVarPrivate);
	CONDITION_VARIABLE m_cv {};
#else
	std::condition_variable_any m_cv;
#endif
};
''', r'''	~CondVarPrivate() = default;
	KYTY_CLASS_NO_COPY(CondVarPrivate);
	CONDITION_VARIABLE m_cv {};
#else
	std::condition_variable_any m_cv;
#endif
	// Track F, F20j3 (KYTY_DIAG_B32, item 574(g)(2)): DiagB32::PackSigIfRegistered of the last Signal / SignalAll;
	// written only at =1 (host heap; CondVar keeps its size - the field is in the private part).
	std::atomic<uint64_t> b32_sig {0};
};
''')

edit(TC, r'''void Mutex::Lock() {
#ifdef KYTY_WIN_CS
	EnterCriticalSection(&m_mutex->m_cs);
#else
	m_mutex->m_mutex.lock();
#endif
}
''', r'''void Mutex::Lock() {
	if (DiagB32::g_on) [[unlikely]] { // Track F, F20j3 (KYTY_DIAG_B32 W:emu_mutex, item 574(g)(1)): one test at =0
		LockB32();
		return;
	}
#ifdef KYTY_WIN_CS
	EnterCriticalSection(&m_mutex->m_cs);
#else
	m_mutex->m_mutex.lock();
#endif
}

// Track F, F20j3: a contended acquisition of a REGISTERED thread is marked W:emu_mutex; the peer is the owner at entry
// (CRITICAL_SECTION::OwningThread - the owner's thread id, read without the lock: a holder that just released gives a
// stale peer [I]). The waker of the record is the peer (mutex-like, item 550(g)(2)(iv)).
void Mutex::LockB32() {
#ifdef KYTY_WIN_CS
	if (TryEnterCriticalSection(&m_mutex->m_cs) != 0) {
		return;
	}
	const auto      owner = static_cast<uint32_t>(reinterpret_cast<uintptr_t>(m_mutex->m_cs.OwningThread));
	DiagB32::Mark   b32;
	b32.BeginWReg(DiagB32::Wait::EmuMutex, this, DiagB32::SlotOfOsTid(owner), 0);
	EnterCriticalSection(&m_mutex->m_cs);
	b32.EndWithPeer(false);
#else
	if (m_mutex->m_mutex.try_lock()) {
		return;
	}
	DiagB32::Mark b32;
	b32.BeginWReg(DiagB32::Wait::EmuMutex, this, 0, 0);
	m_mutex->m_mutex.lock();
	b32.EndWithPeer(false);
#endif
}
''')

edit(TC, r'''void CondVar::Signal() {
#ifdef KYTY_WIN_CS
''', r'''int32_t CondVar::B32Waker(uint64_t since_ns) const {
	return DiagB32::SigWaker(m_cond_var->b32_sig.load(std::memory_order_relaxed), since_ns);
}

void CondVar::Signal() {
	if (DiagB32::g_on) [[unlikely]] { // Track F, F20j3 (item 574(g)(2)): the last signaller
		m_cond_var->b32_sig.store(DiagB32::PackSigIfRegistered(), std::memory_order_relaxed);
	}
#ifdef KYTY_WIN_CS
''')

edit(TC, r'''void CondVar::SignalAll() {
#ifdef KYTY_WIN_CS
''', r'''void CondVar::SignalAll() {
	if (DiagB32::g_on) [[unlikely]] { // Track F, F20j3 (item 574(g)(2)): the last signaller
		m_cond_var->b32_sig.store(DiagB32::PackSigIfRegistered(), std::memory_order_relaxed);
	}
#ifdef KYTY_WIN_CS
''')
