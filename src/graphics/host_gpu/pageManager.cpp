#include "graphics/host_gpu/pageManager.h"
#include "common/diagB32.h" // Track F, F20j3 (KYTY_DIAG_B32, ROADMAP s122 item 574(g))

#include "common/alignment.h"
#include "common/drawStat.h"
#include "common/envFlag.h"
#include "common/frameStats.h"
#include "common/gates.h"
#include "common/logging/log.h"
#include "common/parallelCopy.h"
#include "common/virtualMemory.h"
#include "graphics/host_gpu/regionDefinitions.h"
#include "kernel/memory.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <condition_variable>
#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <memory>
#include <mutex>
#include <new>
#include <thread>
#include <vector>

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#undef min
#undef max
#else
#include <unistd.h>
#endif

namespace Libs::Graphics {
namespace {

constexpr uint64_t PAGE_SIZE    = TRACKER_PAGE_SIZE;
constexpr uint64_t REGION_SIZE  = TRACKER_REGION_SIZE;
constexpr uint64_t ADDRESS_SIZE = TRACKER_ADDRESS_SIZE;
constexpr uint64_t REGION_COUNT = ADDRESS_SIZE / REGION_SIZE;

constexpr uint64_t REGION_PAGES = REGION_SIZE / PAGE_SIZE;

[[noreturn]] void FailFast(const char* reason = nullptr) noexcept {
	std::fputs("PageManager fail-fast: ", stderr);
	std::fputs(reason != nullptr ? reason : "invalid page state", stderr);
	std::fputc('\n', stderr);
	std::fflush(stderr);
	Log::DrainForExit(); // Track F, F25k (KYTY_FIX_B36): the async log queue to the file; no-op at =0
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	TerminateProcess(GetCurrentProcess(), static_cast<UINT>(EXCEPTION_NONCONTINUABLE_EXCEPTION));
#endif
	std::_Exit(322);
}

[[noreturn]] void Fatal(const char* format, ...) {
	std::fputs("PageManager fatal: ", stderr);
	va_list args;
	va_start(args, format);
	std::vfprintf(stderr, format, args);
	va_end(args);
	Log::DrainForExit(); // Track F, F25k (KYTY_FIX_B36): the async log queue to the file; no-op at =0
	std::fputc('\n', stderr);
	std::fflush(stderr);
	std::_Exit(322);
}

class SpinGuard final {
public:
	explicit SpinGuard(std::atomic_flag& lock): m_lock(lock) {
		// Track F, F20j3 (KYTY_DIAG_B32 W:spin, item 574(g)(1)): a contended spin of a registered thread (no owner field).
		Common::DiagB32::Mark b32;
		while (m_lock.test_and_set(std::memory_order_acquire)) {
			if (Common::DiagB32::g_on && !b32.Active()) [[unlikely]] {
				b32.BeginWReg(Common::DiagB32::Wait::Spin, &lock, 0, 0);
			}
			std::atomic_signal_fence(std::memory_order_seq_cst);
		}
		b32.End(0, false);
	}
	~SpinGuard() { m_lock.clear(std::memory_order_release); }
	KYTY_CLASS_NO_COPY(SpinGuard);

private:
	std::atomic_flag& m_lock;
};

// The apply lock of a region (see Region::apply). It is held across VirtualProtect, so a waiter
// pauses and after a while yields instead of spinning hot; the wait is counted (pb_wait_us).
class ApplyGuard final {
public:
	// `site`, `extra` and `extra_gpu` (GuestGpu thread only) also receive the wait; Counter::Count
	// is none. Only a contended acquisition under KYTY_FRAME_TRACE touches them or m_wait_ns: the
	// uncontended path is the single test_and_set it was.
	ApplyGuard(std::atomic_flag& lock, bool engage,
	           Common::FrameStats::Counter site      = Common::FrameStats::Counter::Count,
	           Common::FrameStats::Counter extra     = Common::FrameStats::Counter::Count,
	           Common::FrameStats::Counter extra_gpu = Common::FrameStats::Counter::Count)
	    : m_lock(engage ? &lock : nullptr) {
		if (m_lock == nullptr || !m_lock->test_and_set(std::memory_order_acquire)) {
			return;
		}
		namespace FS  = Common::FrameStats;
		const auto t0 = FS::Enabled() ? FS::NowNs() : 0;
		uint32_t   spins = 0;
		// Track F, F20j3 (KYTY_DIAG_B32 W:spin, item 574(g)(1)): the apply lock is held across VirtualProtect.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::Spin, &lock, 0, 0);
		}
		do {
			while (m_lock->test(std::memory_order_relaxed)) {
				if (spins < 4096) {
					spins++;
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
					YieldProcessor();
#else
					std::this_thread::yield();
#endif
				} else {
					std::this_thread::yield();
				}
			}
		} while (m_lock->test_and_set(std::memory_order_acquire));
		b32.End(0, false);
		if (t0 != 0) {
			const auto ns = FS::NowNs() - t0;
			m_wait_ns     = ns;
			FS::Add(FS::Counter::ApplyWaitNs, ns);
			if (site != FS::Counter::Count) {
				FS::Add(site, ns);
			}
			if (extra != FS::Counter::Count) {
				FS::Add(extra, ns);
			}
			if (FS::CurrentRole() == FS::ThreadRole::Gpu) {
				FS::Add(FS::Counter::ApplyWaitGpuNs, ns);
				if (extra_gpu != FS::Counter::Count) {
					FS::Add(extra_gpu, ns);
				}
			}
		}
	}
	~ApplyGuard() {
		if (m_lock != nullptr) {
			m_lock->clear(std::memory_order_release);
		}
	}
	KYTY_CLASS_NO_COPY(ApplyGuard);

	// The contended wait in ns; 0 when uncontended or without KYTY_FRAME_TRACE.
	[[nodiscard]] uint64_t WaitedNs() const noexcept { return m_wait_ns; }

private:
	std::atomic_flag* m_lock;
	uint64_t          m_wait_ns = 0;
};

void ValidateRange(uint64_t vaddr, uint64_t size) {
	if (!GuestRange {vaddr, size}.Valid()) {
		Fatal("invalid range vaddr=0x%016" PRIx64 ", size=0x%016" PRIx64, vaddr, size);
	}
}

// Session 131, knob "lwin" (track L, DIAGNOSTIC; docs/session-131/lw131.md rev 1 with ROADMAP s122 items 123(zh), 126, 127):
// the page stamps of the classifier of the H events of armcopy (why=host dk=0). One generation G: every stamp and every
// moment of a chunk takes it by a seq_cst fetch_add, so the order of two takes is the order of the holds they sit in. Per
// page, in a block of its 4 MiB region allocated outside every lock (LwEnsureBlock): the clear word c0 << 30 | delta << 22
// | mode code << 20 | op (delta = c1 - c0, 255 = not known yet) and its clock, written by the operation that cleared the
// CPU-dirty bit, under RegionManager::lock; the mark word m << 30 | kind << 29 | mode code << 20 | op (kind 0 pending, 1
// sync) and its clock, written under region.lock right after the mark. Mode code: armcopy 2 -> 1, 3 -> 2, 4 -> 3; 0 = no
// stamp. The words keep 34 bits of a generation; from G >= 2^34 on nothing is stamped or classified (kind=gen, 127(l)).
constexpr uint64_t LW_GEN_LIMIT    = uint64_t {1} << 34u;
constexpr uint64_t LW_DELTA_NONE   = 255;
constexpr uint64_t LW_T_POLL_NS    = 3'000'000; // T_poll (item 126(a), (g))
constexpr uint64_t LW_SPIN_NS      = 1'000'000; // D_spin, lwin=2 (item 126(g))
constexpr uint64_t LW_SPIN_X_NS    = 6'000'000; // D_spin_x = 2 T_poll, lwin=3 (item 126(v), (g))
constexpr size_t   LW_FLIGHT_SLOTS = 64;        // chunks in flight (item 126(g))
constexpr size_t   LW_OPEN_SLOTS   = 64;        // open events (item 126(g))
constexpr size_t   LW_CAND_MAX     = 257;       // candidates of one chunk, 1 MiB / 4 KiB + 1 (item 126(g))
constexpr uint32_t LW_LOSS_LINES   = 256;       // ArmCopyLoss: per process (item 126(g))
constexpr uint32_t LW_LATE_LINES   = 64;        // ArmCopyLossLate: per process
constexpr uint32_t LW_CTL_LINES    = 64;        // ArmCopyLossCtl: per kind per process
constexpr size_t   LW_LATE_BUFFER  = 16;        // late lines one pass keeps until its locks are released (item 127(zh))
constexpr size_t   LW_BLOCKS       = TRACKER_ADDRESS_SIZE / TRACKER_REGION_SIZE;

struct LwPage {
	std::atomic<uint64_t> clr {0};
	std::atomic<uint64_t> clr_ns {0};
	std::atomic<uint64_t> pend {0};
	std::atomic<uint64_t> pend_ns {0};
};
static_assert(sizeof(LwPage) == 32);
struct LwBlock {
	std::array<LwPage, TRACKER_REGION_PAGES> pages {};
};
// Published with release, read with acquire; an empty pointer reads "no stamp" (item 127(l)(2)). Never freed.
std::atomic<LwBlock*> g_lw_blocks[LW_BLOCKS];
std::atomic<uint64_t> g_lw_gen {1};
std::atomic<uint32_t> g_lw_op {1};
// The latest latch of lwin of any operation (ArmCopyScope): the chunks and their checks read it (lw131.md s.9).
std::atomic<uint32_t> g_lw {0};
// Chunks in flight at lwin >= 2 (the spin of the P8 / X control meets them): first page << 32 | pages, 0 = free.
std::atomic<uint64_t> g_lw_flight[LW_FLIGHT_SLOTS];
std::atomic<uint32_t> g_lw_flight_n {0};
// Open events (lw_open) waiting for a late mark of their O3 (lw_late): page | 2 when published, 1 while written, 0 free.
struct LwOpenSlot {
	std::atomic<uint64_t> page {0};
	std::atomic<uint64_t> info {0}; // op | chunk mode << 20
	std::atomic<uint64_t> k_ns {0};
};
LwOpenSlot            g_lw_open[LW_OPEN_SLOTS];
std::atomic<uint32_t> g_lw_open_n {0};
// Overflow kinds seen and logged: one LossWin: overflow line per kind per process (item 127(z)), written only where no lock
// is held.
enum : uint32_t { LwOvfInflight, LwOvfOpen, LwOvfCand, LwOvfBlock, LwOvfGen, LwOvfKinds };
std::atomic<uint32_t> g_lw_ovf_seen {0};
std::atomic<uint32_t> g_lw_ovf_logged {0};

// The lwin of this thread's ArmCopyScope latch (read by ForEachUploadRange at armcopy 2..4 only), and the operation of the
// GuestGpu thread between LwOpBegin and LwAfterPass: its number (20 bits), mode code (0 = no operation) and lwin.
thread_local uint32_t t_ac_lw   = 0;
thread_local uint32_t t_lw_op   = 0;
thread_local uint32_t t_lw_code = 0;
thread_local uint32_t t_lw_val  = 0;
// The in-flight slot of the chunk this thread copies (lwin >= 2), -1 = none.
thread_local int32_t t_lw_flight = -1;

// A candidate of the chunk this thread checks (lw131.md s.2.1, s.2.4, s.5 with item 127(a), (g), (e)): the event page, the
// moments of THE hold S_k of its batch, then the words the poll read last and its state.
enum : uint8_t { LwKindH = 1, LwKindC3, LwKindCr, LwKindCd };
// LwStUnk (item 130(b)(1)): the window of this candidate is not resolvable by the words - a word overwritten or a delta
// never written.
enum : uint8_t { LwStWaitDelta = 1, LwStWaitMark, LwStP8, LwStP8s, LwStNc, LwStMk, LwStOpen, LwStUnk };
struct LwCand {
	uint64_t page    = 0;
	uint64_t take    = 0; // g_take of the chunk
	uint64_t h       = 0; // g_h, g_k, g_rel, rel_ns and the clock of g_k of this candidate's hold S_k (item 127(g))
	uint64_t k       = 0;
	uint64_t rel     = 0;
	uint64_t rel_ns  = 0;
	uint64_t k_ns    = 0;
	uint64_t clr     = 0; // the words and clocks of the latest read
	uint64_t pend    = 0;
	uint64_t clr_ns  = 0;
	uint64_t pend_ns = 0;
	uint64_t c1      = 0; // (a) known: c0 + delta of the clear of O3
	uint32_t pin     = 0; // CR: the operation of the clear word of the snapshot S_k
	uint32_t o3      = 0; // (a) known: the operation of that clear
	uint32_t mode    = 0; // the chunk's mode
	uint8_t  kind    = 0;
	uint8_t  perms   = 0; // Perms() in S_k
	uint8_t  state   = 0;
	bool     a       = false;
};
struct LwCandList {
	size_t                          n = 0;
	std::array<LwCand, LW_CAND_MAX> c {};
};
thread_local LwCandList* t_lw_cands = nullptr;
struct LwLate {
	uint64_t page = 0;
	int64_t  dt   = 0;
	uint32_t mode = 0;
	uint32_t op   = 0;
};
struct LwLateBuffer {
	uint32_t                           n = 0;
	std::array<LwLate, LW_LATE_BUFFER> e {};
};
thread_local LwLateBuffer t_lw_late {};

[[nodiscard]] constexpr uint64_t LwModeCode(uint32_t mode) noexcept {
	return mode == 2 ? 1 : mode == 3 ? 2 : mode == 4 ? 3 : 0;
}
[[nodiscard]] constexpr uint64_t LwGen(uint64_t word) noexcept {
	return word >> 30u;
}
[[nodiscard]] constexpr uint64_t LwDelta(uint64_t word) noexcept {
	return (word >> 22u) & 0xffu;
}
[[nodiscard]] constexpr uint32_t LwKindOf(uint64_t word) noexcept {
	return static_cast<uint32_t>((word >> 29u) & 1u);
}
[[nodiscard]] constexpr uint64_t LwCode(uint64_t word) noexcept {
	return (word >> 20u) & 3u;
}
[[nodiscard]] constexpr uint32_t LwOp(uint64_t word) noexcept {
	return static_cast<uint32_t>(word & 0xfffffu);
}

[[nodiscard]] uint64_t LwTake() noexcept {
	return g_lw_gen.fetch_add(1, std::memory_order_seq_cst);
}

// Any thread, any lock: the counter and the kind; the line waits for LwOverflowLog.
void LwOverflowNote(uint32_t kind) noexcept {
	Common::FrameStats::Add(Common::FrameStats::Counter::LwOvf, 1);
	g_lw_ovf_seen.fetch_or(1u << kind, std::memory_order_relaxed);
}

// No lock held.
void LwOverflowLog() {
	static constexpr const char* names[LwOvfKinds] = {"inflight", "open", "cand", "block", "gen"};
	const auto seen = g_lw_ovf_seen.load(std::memory_order_relaxed);
	if ((seen & ~g_lw_ovf_logged.load(std::memory_order_relaxed)) == 0) {
		return;
	}
	for (uint32_t kind = 0; kind < LwOvfKinds; kind++) {
		const auto bit = 1u << kind;
		if ((seen & bit) != 0 && (g_lw_ovf_logged.fetch_or(bit, std::memory_order_relaxed) & bit) == 0) {
			LOGF("LossWin: overflow kind=%s\n", names[kind]);
		}
	}
}

[[nodiscard]] LwBlock* LwBlockOf(uint64_t vaddr) noexcept {
	const auto index = vaddr / TRACKER_REGION_SIZE;
	return index < LW_BLOCKS ? g_lw_blocks[index].load(std::memory_order_acquire) : nullptr;
}

void LwFlightLeave() noexcept {
	if (t_lw_flight >= 0) {
		g_lw_flight[t_lw_flight].store(0, std::memory_order_release);
		g_lw_flight_n.fetch_sub(1, std::memory_order_relaxed);
		t_lw_flight = -1;
	}
}

// The chunk [vaddr, vaddr + size) of this thread is in flight (lwin >= 2, L9 with item 127(v)).
void LwFlightEnter(uint64_t vaddr, uint64_t size) noexcept {
	LwFlightLeave(); // a chunk of this thread whose check never ran
	const auto first = vaddr / TRACKER_PAGE_SIZE;
	const auto pages = (vaddr + size + TRACKER_PAGE_SIZE - 1) / TRACKER_PAGE_SIZE - first;
	const auto value = first << 32u | (pages & 0xffffffffu);
	for (size_t slot = 0; slot < LW_FLIGHT_SLOTS; slot++) {
		uint64_t expected = 0;
		if (g_lw_flight[slot].compare_exchange_strong(expected, value, std::memory_order_acq_rel)) {
			g_lw_flight_n.fetch_add(1, std::memory_order_relaxed);
			t_lw_flight = static_cast<int32_t>(slot);
			return;
		}
	}
	LwOverflowNote(LwOvfInflight);
}

// Some chunk in flight meets the pages [first, last) (global page numbers).
[[nodiscard]] bool LwFlightMeets(uint64_t first, uint64_t last) noexcept {
	for (size_t slot = 0; slot < LW_FLIGHT_SLOTS; slot++) {
		const auto value = g_lw_flight[slot].load(std::memory_order_relaxed);
		if (value != 0) {
			const auto begin = value >> 32u;
			const auto end   = begin + (value & 0xffffffffu);
			if (begin < last && first < end) {
				return true;
			}
		}
	}
	return false;
}

// Under region.lock of the run (UpdateRegionWatchers<.., lw = true>, L8): the open events of the operation `op` on the
// pages [lo, hi) got their mark late - lw_late and the local buffer only, no line (item 127(zh)).
void LwLateScan(uint64_t lo, uint64_t hi, uint32_t op, uint64_t mark_ns) noexcept {
	for (auto& slot: g_lw_open) {
		auto value = slot.page.load(std::memory_order_acquire);
		if ((value & 2u) == 0) {
			continue;
		}
		const auto page = value & ~uint64_t {3};
		if (page < lo || page >= hi) {
			continue;
		}
		const auto info = slot.info.load(std::memory_order_relaxed);
		const auto k_ns = slot.k_ns.load(std::memory_order_relaxed);
		if (LwOp(info) != op || !slot.page.compare_exchange_strong(value, 0, std::memory_order_acq_rel)) {
			continue;
		}
		g_lw_open_n.fetch_sub(1, std::memory_order_relaxed);
		Common::FrameStats::Add(Common::FrameStats::Counter::LwLate, 1);
		auto& buffer = t_lw_late;
		if (buffer.n < LW_LATE_BUFFER) {
			buffer.e[buffer.n++] = {page, static_cast<int64_t>(mark_ns - k_ns), static_cast<uint32_t>((info >> 20u) & 7u), op};
		}
	}
}

// Under region.lock (L8, item 126(b)): the mark words of a run just marked pending (kind 0) or armed synchronously (kind
// 1) by the operation of this thread, then the late check of the open events. Atomics, the clock and the scan only.
void LwStampMark(uint64_t base_addr, size_t first, size_t count, uint32_t kind) noexcept {
	namespace FS = Common::FrameStats;
	if (t_lw_code == 0 || count == 0) {
		return;
	}
	auto* block = LwBlockOf(base_addr);
	if (block == nullptr) {
		return; // no block (lw_ovf at LwEnsureBlock): no stamp
	}
	const auto m = LwTake();
	if (m >= LW_GEN_LIMIT) {
		LwOverflowNote(LwOvfGen);
		return;
	}
	const auto     ns   = FS::NowNs();
	const uint64_t word = m << 30u | uint64_t {kind} << 29u | uint64_t {t_lw_code} << 20u | t_lw_op;
	for (size_t page = first; page < first + count && page < TRACKER_REGION_PAGES; page++) {
		auto& stamp = block->pages[page];
		stamp.pend_ns.store(ns, std::memory_order_relaxed);
		stamp.pend.store(word, std::memory_order_release); // item 127(a)
	}
	FS::Add(kind == 0 ? FS::Counter::LwMarkPages : FS::Counter::LwSyncPages, count);
	if (g_lw_open_n.load(std::memory_order_relaxed) != 0) {
		LwLateScan(base_addr + first * TRACKER_PAGE_SIZE, base_addr + (first + count) * TRACKER_PAGE_SIZE, t_lw_op, ns);
	}
}

// No lock held: the ArmCopyLossLate lines the marks of this thread found.
void LwLateFlush() {
	auto& buffer = t_lw_late;
	static std::atomic<uint32_t> logged {0};
	for (uint32_t index = 0; index < buffer.n; index++) {
		const auto& late = buffer.e[index];
		if (logged.load(std::memory_order_relaxed) < LW_LATE_LINES &&
		    logged.fetch_add(1, std::memory_order_relaxed) < LW_LATE_LINES) {
			LOGF("ArmCopyLossLate: page=0x%016llx mode=%u clr_op=%u pend_op=%u dt_ns=%lld\n",
			     static_cast<unsigned long long>(late.page), static_cast<unsigned>(late.mode), static_cast<unsigned>(late.op),
			     static_cast<unsigned>(late.op), static_cast<long long>(late.dt));
		}
	}
	buffer.n = 0;
}

// An lw_open event waits for a late mark of its O3 (row lw_late, lw131.md s.5.3). False when the table is full.
[[nodiscard]] bool LwOpenInsert(uint64_t page, uint32_t op, uint32_t mode, uint64_t k_ns) noexcept {
	for (auto& slot: g_lw_open) {
		uint64_t expected = 0;
		if (slot.page.compare_exchange_strong(expected, 1, std::memory_order_acquire)) {
			slot.info.store(uint64_t {op} | uint64_t {mode} << 20u, std::memory_order_relaxed);
			slot.k_ns.store(k_ns, std::memory_order_relaxed);
			slot.page.store(page | 2u, std::memory_order_release);
			g_lw_open_n.fetch_add(1, std::memory_order_relaxed);
			return true;
		}
	}
	return false;
}

// CR (lw131.md s.2.1, s.6.2): the words of the snapshot S_k hold a clear inside (g_take, g_h) and, of the same operation, a
// mark taken before g_k.
[[nodiscard]] constexpr bool LwCrSnapshot(uint64_t clr, uint64_t pend, uint64_t take, uint64_t h, uint64_t k) noexcept {
	if (LwCode(clr) == 0 || LwCode(pend) == 0 || LwOp(pend) != LwOp(clr)) {
		return false;
	}
	const auto c0    = LwGen(clr);
	const auto delta = LwDelta(clr);
	return c0 > take && c0 < h && delta != LW_DELTA_NONE && c0 + delta < h && LwGen(pend) < k;
}

// One read of the words of a candidate (after g_rel of its hold).
void LwRead(LwCand& c) noexcept {
	auto* block = LwBlockOf(c.page);
	if (block == nullptr) {
		c.clr = c.pend = c.clr_ns = c.pend_ns = 0;
		return;
	}
	const auto& stamp = block->pages[(c.page % TRACKER_REGION_SIZE) / TRACKER_PAGE_SIZE];
	c.pend    = stamp.pend.load(std::memory_order_acquire);
	c.pend_ns = stamp.pend_ns.load(std::memory_order_relaxed);
	c.clr     = stamp.clr.load(std::memory_order_relaxed);
	c.clr_ns  = stamp.clr_ns.load(std::memory_order_relaxed);
}

// The class of a candidate from the words read last, or what it still waits for (lw131.md s.2.4 with item 127(a)). A read
// showing no (a) is final: a clear inside (g_take, g_h) wrote its word before its c1 < g_h, so any read after g_h sees that
// word or a later clear's. Only a clear with c0 in the window and delta 255 waits for its delta; only (a) without a mark
// taken after c1 waits for the mark. A later clear over the word (c0 >= g_h; or, with (a), a clear after c1 of O3 in the
// read that would give LwStMk) is LwStUnk, not a class (item 130(b)(2), (4)).
[[nodiscard]] uint8_t LwDecide(LwCand& c) noexcept {
	if (!c.a) {
		const auto code = LwCode(c.clr);
		const auto c0   = LwGen(c.clr);
		if (code == 0 || c0 <= c.take) {
			return LwStNc; // no clear in the window (an earlier one)
		}
		if (c0 >= c.h) {
			return LwStUnk; // a later clear over the word (item 130(b)(2))
		}
		if (c.kind == LwKindCr && LwOp(c.clr) != c.pin) {
			return LwStNc; // CR: the operation pinned by the snapshot S_k
		}
		if (c.kind != LwKindC3 && code != 1 && code != 3) {
			return LwStNc; // (g): O3 latched 2 or 4 (C3 without it, s.2.1)
		}
		const auto delta = LwDelta(c.clr);
		if (delta == LW_DELTA_NONE) {
			return LwStWaitDelta;
		}
		if (c0 + delta >= c.h) {
			return LwStNc;
		}
		c.a  = true;
		c.o3 = LwOp(c.clr);
		c.c1 = c0 + delta;
	}
	if (LwCode(c.pend) == 0 || LwGen(c.pend) <= c.c1) {
		return LwStWaitMark;
	}
	if (LwOp(c.pend) != c.o3 || LwGen(c.pend) < c.k) {
		return LwGen(c.clr) > c.c1 ? LwStUnk : LwStMk; // item 130(b)(4)
	}
	return LwKindOf(c.pend) != 0 ? LwStP8s : LwStP8;
}

// A candidate the list could not hold is X (kind=cand).
void LwCountX(uint8_t kind, Libs::Graphics::PageManager::ArmCopyClassCounts& out) noexcept {
	switch (kind) {
		case LwKindH:
			out.lw_x++;
			out.lw_xnc++;
			break;
		case LwKindC3: out.lw_c3x++; break;
		case LwKindCr: out.lw_crx++; break;
		default: out.lw_cdx++; break;
	}
}

} // namespace

struct PageManager::Impl {
	// Session 128, knob "protceil": whether a host protection change arms a write watcher, and from where - ONE predicate
	// (ROADMAP s122 item 89(z)): the synchronous run of UpdateRegionWatchers<true, false> to read-only (Sync), or a run
	// to read-only a flush applies (Scope - the flush of a BatchScope, Range - any other; a deferred read-only change is
	// always a write-watcher edge: read-watcher changes never defer). It decides the skip at a latch of 1 and pc_elig_*
	// at a latch of 0. Session 129, knob "armcopy": Job - every host call of a pool chunk (ArmCopyChunk, design129.md rev 2
	// s.3 C5); never in pc_elig_*, moved off GuestGpu (ac_moved_*) or kept as help on it (ac_kept_help_*).
	enum class Arm : uint8_t { No, Sync, Scope, Range, Job };
	// The latch of the thread's innermost ArmCopyScope (t_ac_state; the value 1..4 in t_ac_mode).
	static constexpr uint8_t AcOutside     = 0; // no ArmCopyScope open
	static constexpr uint8_t AcZero        = 1; // latched 0: the previous path (ac_op0)
	static constexpr uint8_t AcRefused     = 2; // latched >= 1 and refused: the path of 0
	static constexpr uint8_t AcWrittenNull = 3; // a written synchronization latched 4: the path of 0, nothing kept
	static constexpr uint8_t AcNull        = 4; // latched 4, read-only: the path of 0, its chunks run the detector
	static constexpr uint8_t AcWritten     = 5; // a written synchronization latched 1..3: the path of 0, ac_kept_wr_*
	static constexpr uint8_t AcMove        = 6; // latched 1..3, read-only: the move
	// The latch of the thread's innermost CeilScope (t_ceil_state).
	static constexpr uint8_t CeilOutside = 0; // no CeilScope open
	static constexpr uint8_t CeilZero    = 1; // latched 0: the previous path, pc_elig_* counted
	static constexpr uint8_t CeilSkip    = 2; // latched 1: armings skipped
	static constexpr uint8_t CeilRefused = 3; // latched 1 or 2 and refused: the path of 0, nothing counted as eligible
	static constexpr uint8_t CeilDose    = 4; // latched 2: the path of 0, pc_elig_* counted, each eligible call dosed

	struct PageState {
		uint8_t write_watchers  : 7 = 0;
		uint8_t access_watchers : 1 = 0;

		[[nodiscard]] Common::VirtualMemory::Mode Perms() const noexcept {
			if (access_watchers != 0) {
				return Common::VirtualMemory::Mode::NoAccess;
			}
			if (write_watchers != 0) {
				return Common::VirtualMemory::Mode::Read;
			}
			return Common::VirtualMemory::Mode::ReadWrite;
		}

		template <int delta, bool is_read>
		uint32_t AddDelta(uint64_t address) {
			static_assert(delta >= -1 && delta <= 1);
			if constexpr (is_read) {
				if constexpr (delta == 1) {
					if (access_watchers != 0) {
						Fatal("read-watcher overflow at 0x%016" PRIx64, address);
					}
					return ++access_watchers;
				} else if constexpr (delta == -1) {
					if (access_watchers == 0) {
						Fatal("read-watcher underflow at 0x%016" PRIx64, address);
					}
					return --access_watchers;
				} else {
					return access_watchers;
				}
			} else {
				if constexpr (delta == 1) {
					if (write_watchers == 0x7f) {
						Fatal("write-watcher overflow at 0x%016" PRIx64, address);
					}
					return ++write_watchers;
				} else if constexpr (delta == -1) {
					if (write_watchers == 0) {
						Fatal("write-watcher underflow at 0x%016" PRIx64, address);
					}
					return --write_watchers;
				} else {
					return write_watchers;
				}
			}
		}
	};
	static_assert(sizeof(PageState) == 1);

	struct Region {
		std::atomic_flag                    lock = ATOMIC_FLAG_INIT;
		// The apply lock. INVARIANT (P): every host protection change of a page of this region
		// is made while `apply` is held, with a value read from `pages` (under `lock`) inside
		// that same hold. Holds never overlap, so the host protection of a page is the value of
		// the latest completed application, and no application can be overtaken by an older
		// value. (Q): a change of `pages` that alters Perms() of a page either happens inside an
		// application covering the page (synchronous path, apply held first) or sets the page's
		// pending bit; a pending bit is cleared only inside an application that covers the page
		// and reads its value after clearing it. (R): a BatchScope flushes its window before its
		// thread relies on the protection, and a flush takes `apply` even when it finds nothing
		// pending, so an application another thread already took out of `pending` completes
		// first. Hence when a flush returns, the host protection of each page of its window
		// reflects `pages` at a moment no earlier than the flusher's own changes.
		// Why no guest write is lost (gate "protbatch"): SynchronizeBuffer clears the CPU-dirty
		// bits and adds its write watcher under the region lock, and copies the bytes only after
		// its flush returned. By (R) the page is read-only from that point unless a later change
		// made it writable - and the only change that removes a buffer's write watcher is
		// ChangeState<Cpu, true>, which marks the page CPU-dirty in the same critical section, so
		// the next synchronization uploads it. A write that lands before the protection is in
		// effect precedes the copy and is part of it. Switching the gate is safe at any moment:
		// the synchronous path always takes `apply`, and a scope opened while the gate was on
		// still flushes what it deferred. Order: apply -> lock.
		std::atomic_flag                    apply = ATOMIC_FLAG_INIT;
		std::array<PageState, REGION_PAGES> pages;
		// Pages whose host protection may lag behind Perms(): a deferred write-watcher edge
		// (UpdatePageWatchersDeferred) or a batched one (BatchScope) sets the bit, and any
		// application covering the page clears it. Written under `lock`, through std::atomic_ref:
		// FlushBlocker (gate "applyskip") reads the words without it.
		std::array<uint64_t, REGION_PAGES / 64> pending {};
		bool                                    has_pending = false; // any bit set
		bool                                    queued      = false; // sits in the worker queue
		// The run the holder of `apply` took out of `pending` and is applying now:
		// first | last << 16 | protection << 32, 0 when none. Published under `lock` before the bits
		// are cleared (TakePendingRun) and withdrawn after the host call returned, before `apply` is
		// released (ApplyPending, FlushRegion). `apply` is exclusive, so this one run is every
		// application in flight on the region. Read without any lock by FlushBlocker.
		std::atomic<uint64_t>                   applying_run {0};
		// Session 128, knob "protceil" (design128.md s.5.1; ROADMAP s122 item 89(k): after applying_run, at the end, so
		// no field above moves). U: a page whose read-only arming was skipped - the host may still let the guest write
		// it. Read and written only under `apply` (a skip, an application, the re-arm pass, Verify). `has_unarmed`: some
		// bit was set since the last re-arm pass (it stays set while applications clear the bits); `unarmed_listed`: the
		// region is in Impl::unarmed_regions.
		std::array<uint64_t, REGION_PAGES / 64> unarmed {};
		bool                                    has_unarmed    = false;
		bool                                    unarmed_listed = false;
	};
	// Item 89(k): 1176 bytes before session 128 (applying_run ends at 1176), 1312 with the three fields above.
	static_assert(sizeof(Region) == 1312);

	Impl() {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
		SYSTEM_INFO info {};
		GetSystemInfo(&info);
		if (info.dwPageSize != PAGE_SIZE) {
			Fatal("unsupported host page size 0x%08" PRIx32,
			      static_cast<uint32_t>(info.dwPageSize));
		}
#elif defined(__APPLE__)
		// Under Rosetta the host page size is 4 KB, matching TRACKER_PAGE_SIZE.
		if (static_cast<uint64_t>(getpagesize()) != PAGE_SIZE) {
			Fatal("unsupported host page size 0x%08" PRIx32, static_cast<uint32_t>(getpagesize()));
		}
#else
		const auto host_page_size = ::sysconf(_SC_PAGESIZE);
		if (host_page_size < 0 || static_cast<uint64_t>(host_page_size) != PAGE_SIZE) {
			Fatal("unsupported host page size %ld", static_cast<long>(host_page_size));
		}
#endif
		regions = std::make_unique<std::atomic<Region*>[]>(REGION_COUNT);
	}

	~Impl() {
		StopWorker();
		for (const auto& region: region_storage) {
			SpinGuard lock(region->lock);
			for (auto& page: region->pages) {
				if (page.write_watchers != 0 || page.access_watchers != 0) {
					FailFast("PageManager destroyed with live page state");
				}
			}
		}
	}

	Region* FindRegion(uint64_t vaddr) const noexcept {
		return vaddr < ADDRESS_SIZE ? regions[vaddr / REGION_SIZE].load(std::memory_order_acquire)
		                            : nullptr;
	}

	Region* GetOrCreateRegion(uint64_t vaddr) {
		const auto index = vaddr / REGION_SIZE;
		if (auto* region = regions[index].load(std::memory_order_acquire); region != nullptr) {
			return region;
		}
		std::lock_guard lock(region_mutex);
		if (auto* region = regions[index].load(std::memory_order_acquire); region != nullptr) {
			return region;
		}
		auto  region = std::make_unique<Region>();
		auto* ptr    = region.get();
		region_storage.push_back(std::move(region));
		regions[index].store(ptr, std::memory_order_release);
		return ptr;
	}

	void Protect(uint64_t vaddr, uint64_t size, Common::VirtualMemory::Mode mode, Arm arm = Arm::No) noexcept {
		static const bool trap = Common::EnvFlagOn("KYTY_STREAM_TRACE");
		if (trap && mode != Common::VirtualMemory::Mode::ReadWrite &&
		    Libs::LibKernel::Memory::OverlapsGuestStack(vaddr, size)) {
			static std::atomic<int> logged {0};
			if (logged.fetch_add(1) < 16) {
				std::fprintf(stderr, "StackProtect: addr=0x%016llx size=0x%llx mode=0x%x tid=%lu\n",
				             static_cast<unsigned long long>(vaddr), static_cast<unsigned long long>(size),
				             static_cast<unsigned>(mode), static_cast<unsigned long>(GetCurrentThreadId()));
				void* frames[24] = {};
				const auto n = static_cast<int>(CaptureStackBackTrace(0, 24, frames, nullptr));
				const auto image_base = reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));
				for (int i = 0; i < n; i++) {
					const auto address = reinterpret_cast<uintptr_t>(frames[i]);
					std::fprintf(stderr, "  frame[%d]=0x%016llx image+0x%llx\n", i,
					             static_cast<unsigned long long>(address),
					             static_cast<unsigned long long>(address >= image_base ? address - image_base : 0));
				}
				std::fflush(stderr);
			}
		}
		namespace FS  = Common::FrameStats;
		const auto t0 = FS::Enabled() ? FS::NowNs() : 0;
		// The kernel serializes protection changes without fairness: a thread issuing them back
		// to back starves everyone else for milliseconds. Synchronous callers (GuestGpu thread,
		// fault handlers) announce themselves and the worker pauses between its calls.
		if (!t_protect_worker) {
			sync_waiters.fetch_add(1, std::memory_order_acq_rel);
		}
		if (!Libs::LibKernel::Memory::ProtectGuestHostMemory(vaddr, size, mode)) {
			Fatal("address-space protection failed at 0x%016" PRIx64 ", mode=0x%08" PRIx32, vaddr,
			      static_cast<uint32_t>(mode));
		}
		if (!t_protect_worker) {
			sync_waiters.fetch_sub(1, std::memory_order_acq_rel);
		}
		if (t0 != 0) {
			const bool worker = t_protect_worker;
			const auto ns     = FS::NowNs() - t0;
			const auto pages  = size / PAGE_SIZE;
			FS::Add(worker ? FS::Counter::ProtectWorkerNs : FS::Counter::ProtectNs, ns);
			FS::Add(worker ? FS::Counter::ProtectWorkerPages : FS::Counter::ProtectPages, pages);
			if (!worker) {
				FS::Add(FS::Counter::ProtectCalls, 1);
				switch (mode) {
					case Common::VirtualMemory::Mode::Read:
						FS::Add(FS::Counter::ProtectRoCalls, 1);
						FS::Add(FS::Counter::ProtectRoPages, pages);
						break;
					case Common::VirtualMemory::Mode::NoAccess:
						FS::Add(FS::Counter::ProtectNaCalls, 1);
						FS::Add(FS::Counter::ProtectNaPages, pages);
						break;
					default:
						FS::Add(FS::Counter::ProtectRwNs, ns);
						FS::Add(FS::Counter::ProtectRwPages, pages);
						break;
				}
				if (PageManager::SpinHeld::Depth() != 0) {
					FS::Add(FS::Counter::ProtectSpinNs, ns);
					FS::Add(FS::Counter::ProtectSpinCalls, 1);
					FS::Add(FS::Counter::ProtectSpinPages, pages);
					if (FS::CurrentRole() == FS::ThreadRole::Gpu) {
						FS::Add(FS::Counter::ProtectSpinGpuNs, ns);
						FS::Add(FS::Counter::ProtectSpinGpuCalls, 1);
						FS::Add(FS::Counter::ProtectSpinGpuPages, pages);
					}
				}
				if (FS::CurrentRole() == FS::ThreadRole::Gpu) {
					FS::Add(FS::Counter::ProtectGpuNs, ns);
					FS::Add(FS::Counter::ProtectGpuCalls, 1);
					FS::Add(FS::Counter::ProtectGpuPages, pages);
					// Session 128, knob "protceil" (s.7.1): the same calls by mode (T1, T2), and the armings a latch of 1
					// would have skipped (pc_elig_*, item 89(z): the predicate of the skip, passed down as `arm`).
					switch (mode) {
						case Common::VirtualMemory::Mode::Read:
							FS::Add(FS::Counter::ProtGpuRoNs, ns);
							FS::Add(FS::Counter::ProtGpuRoN, 1);
							FS::Add(FS::Counter::ProtGpuRoPages, pages);
							break;
						case Common::VirtualMemory::Mode::NoAccess:
							FS::Add(FS::Counter::ProtGpuNaNs, ns);
							FS::Add(FS::Counter::ProtGpuNaN, 1);
							break;
						default:
							FS::Add(FS::Counter::ProtGpuRwNs, ns);
							FS::Add(FS::Counter::ProtGpuRwN, 1);
							break;
					}
					if (arm != Arm::No && arm != Arm::Job && (t_ceil_state == CeilZero || t_ceil_state == CeilDose)) {
						FS::Add(FS::Counter::PcEligNs, ns);
						FS::Add(FS::Counter::PcEligN, 1);
						FS::Add(FS::Counter::PcEligPages, pages);
						if (arm == Arm::Scope) {
							FS::Add(FS::Counter::PcEligScopeN, 1);
						} else if (arm == Arm::Range) {
							FS::Add(FS::Counter::PcEligRngN, 1);
						}
						if (t_ceil_state == CeilDose) [[unlikely]] {
							// Value 2 (ROADMAP s122 item 93(g)(1)): the call is made; the thread spins once more for its
							// duration by the same clock, still under the locks the call was made under (the counters
							// above hold the call alone).
							const auto d0 = FS::NowNs();
							auto       d1 = d0;
							while (d1 - d0 < ns) {
								YieldProcessor();
								d1 = FS::NowNs();
							}
							FS::Add(FS::Counter::PcDoseN, 1);
							FS::Add(FS::Counter::PcDoseNs, d1 - d0);
						}
					}
				}
				// Session 129, knob "armcopy" (design129.md rev 2 s.9.1, C6): a chunk's call is moved off GuestGpu and help on
				// it; a GuestGpu arming inside a latch of 1..3 is kept, by its reason. At 0 and 4 no Arm::Job is passed and the
				// latch is neither AcWritten nor AcMove, so nothing here is counted.
				if (arm == Arm::Job) {
					// Session 130, knob "acinline" (I7): an inline-class chunk's call is also ai_help_* / ai_moved_*.
					if (FS::CurrentRole() == FS::ThreadRole::Gpu) {
						AcAddKept(ns, FS::Counter::AcKeptHelpN, FS::Counter::AcKeptHelpNs);
						if (t_ai_chunk) {
							FS::Add(FS::Counter::AiHelpN, 1);
							FS::Add(FS::Counter::AiHelpNs, ns);
						}
					} else {
						FS::Add(FS::Counter::AcMovedN, 1);
						FS::Add(FS::Counter::AcMovedNs, ns);
						FS::Add(FS::Counter::AcMovedPages, pages);
						if (t_ai_chunk) {
							FS::Add(FS::Counter::AiMovedN, 1);
							FS::Add(FS::Counter::AiMovedNs, ns);
							FS::Add(FS::Counter::AiMovedPages, pages);
						}
					}
				} else if (arm != Arm::No && (t_ac_state == AcWritten || t_ac_state == AcMove) &&
				           FS::CurrentRole() == FS::ThreadRole::Gpu) {
					const auto reason = t_ac_state == AcWritten ? AcReasonWr : static_cast<uint8_t>(t_ac_reason);
					switch (reason) {
						case static_cast<uint8_t>(PageManager::ArmCopyReason::Inline):
							AcAddKept(ns, FS::Counter::AcKeptInlN, FS::Counter::AcKeptInlNs);
							break;
						// Session 130, knob "acinline" (I7, I7'): an inline copy of an operation with
						// acinline=1 left on GuestGpu - the same ac_kept_inl_* as Inline, and its ai_* row
						// by reason.
						case static_cast<uint8_t>(PageManager::ArmCopyReason::InlNowin):
							AcAddKept(ns, FS::Counter::AcKeptInlN, FS::Counter::AcKeptInlNs);
							AiAddKept(ns, FS::Counter::AiKeptNowinN, FS::Counter::AiKeptNowinNs);
							break;
						case static_cast<uint8_t>(PageManager::ArmCopyReason::InlNomap):
							AcAddKept(ns, FS::Counter::AcKeptInlN, FS::Counter::AcKeptInlNs);
							AiAddKept(ns, FS::Counter::AiKeptNomapN, FS::Counter::AiKeptNomapNs);
							break;
						case static_cast<uint8_t>(PageManager::ArmCopyReason::InlBig):
							AcAddKept(ns, FS::Counter::AcKeptInlN, FS::Counter::AcKeptInlNs);
							FS::Add(FS::Counter::AiKeptBigN, 1);
							FS::Add(FS::Counter::AiKeptBigNs, ns);
							break;
						case static_cast<uint8_t>(PageManager::ArmCopyReason::Gap):
							AcAddKept(ns, FS::Counter::AcKeptGapN, FS::Counter::AcKeptGapNs);
							break;
						case static_cast<uint8_t>(PageManager::ArmCopyReason::Tmp):
							AcAddKept(ns, FS::Counter::AcKeptTmpN, FS::Counter::AcKeptTmpNs);
							break;
						case AcReasonWr: AcAddKept(ns, FS::Counter::AcKeptWrN, FS::Counter::AcKeptWrNs); break;
						default: AcAddKept(ns, FS::Counter::AcKeptFullN, FS::Counter::AcKeptFullNs); break;
					}
				}
				if (t_protect_masked) {
					FS::Add(FS::Counter::ProtectMaskedNs, ns);
					FS::Add(FS::Counter::ProtectMaskedCalls, 1);
				}
				if (t_pass != nullptr) {
					// pb2_vp*: which calls of this dirty-range pass phase 2 would merge away.
					t_pass->NoteProtect(vaddr, size, static_cast<uint32_t>(mode));
				}
			}
		}
	}

	static void SetPendingRange(Region& region, size_t first, size_t count, bool value) {
		for (size_t page = first; page < first + count; page++) {
			// Writers hold `lock`, so the read-modify-write need not be atomic; std::atomic_ref only
			// for the lock-free reads of FlushBlocker.
			std::atomic_ref<uint64_t> word(region.pending[page / 64]);
			const auto                bit  = uint64_t {1} << (page % 64);
			const auto                bits = word.load(std::memory_order_relaxed);
			word.store(value ? (bits | bit) : (bits & ~bit), std::memory_order_relaxed);
		}
	}

	// Protects a run of pages under the region lock and marks their host state as current.
	// Session 128, knob "protceil": `arming` - the run arms a write watcher (Arm::Sync, item 89(z)); at a latch of 1 its
	// host call is skipped and its pages are marked unarmed, everything else is done as at 0.
	void ProtectRun(Region& region, uint64_t base_addr, size_t first, size_t count,
	                Common::VirtualMemory::Mode perms, bool arming) {
		if (arming && t_ceil_state == CeilSkip) [[unlikely]] {
			SkipRun(region, base_addr, first, count, Arm::Sync);
		} else {
			Protect(base_addr + first * PAGE_SIZE, count * PAGE_SIZE, perms, arming ? Arm::Sync : Arm::No);
			if (region.has_unarmed) {
				ClearUnarmed(region, first, count);
			}
		}
		if (region.has_pending) {
			SetPendingRange(region, first, count, false);
		}
	}

	// `defer`: instead of protecting the runs now, mark them pending and hand the region to the
	// worker (only for adding write watchers; see PageManager::UpdatePageWatchersDeferred).
	// Gate "protbatch": inside an enabled BatchScope of this manager a write-watcher change
	// also only marks its runs pending, and the scope applies them (FlushRegion).
	// Session 131, knob "lwin" (L8): `lw` - the pass of an operation with lwin >= 1; each run it marks pending or arms
	// synchronously gets its mark stamps in the same hold of `lock` (LwStampMark). The instantiations of false are the text
	// of session 130.
	template <bool track, bool is_read, bool masked, bool lw = false>
	void UpdateRegionWatchers(Region& region, uint64_t base_addr, size_t first, size_t last,
	                          const RegionBits* mask = nullptr, bool defer = false) {
		bool      enqueue = false;
		t_protect_masked  = masked;
		PageManager::BatchScope::Slot* slot = nullptr;
		if constexpr (!is_read) {
			if (!defer && t_batch != nullptr && t_batch->m_manager.m_impl.get() == this) {
				slot = ReserveSlot(*t_batch, region, base_addr);
			}
		}
		const bool batch         = slot != nullptr;
		uint64_t   batched_pages = 0;
		bool       protected_any = false; // pb_sync_noprot
		// Order apply -> lock (see Region::apply). Marking pages pending changes no host
		// protection and does not need the apply lock.
		ApplyGuard apply(region.apply, !batch && !defer, Common::FrameStats::Counter::ApplyWaitSyncNs);
		{
		SpinGuard lock(region.lock);
		auto      perms                 = region.pages[first].Perms();
		uint64_t  range_begin           = 0;
		uint64_t  range_bytes           = 0;
		uint64_t  potential_range_bytes = 0;

		const auto release_pending = [&] {
			if (range_bytes != 0) {
				if (defer || batch) {
					const auto run_first = static_cast<size_t>(range_begin);
					const auto run_pages = static_cast<size_t>(range_bytes / PAGE_SIZE);
					SetPendingRange(region, run_first, run_pages, true);
					if constexpr (lw) {
						LwStampMark(base_addr, run_first, run_pages, 0);
					}
					region.has_pending = true;
					if (batch) {
						ExtendSlot(*slot, run_first, run_first + run_pages);
						batched_pages += run_pages;
					} else if (!region.queued) {
						region.queued = true;
						enqueue       = true;
					}
				} else {
					protected_any = true;
					ProtectRun(region, base_addr, static_cast<size_t>(range_begin),
					           static_cast<size_t>(range_bytes / PAGE_SIZE), perms,
					           track && !is_read && perms == Common::VirtualMemory::Mode::Read);
					if constexpr (lw) {
						if (track && !is_read && perms == Common::VirtualMemory::Mode::Read) {
							LwStampMark(base_addr, static_cast<size_t>(range_begin),
							            static_cast<size_t>(range_bytes / PAGE_SIZE), 1); // sync (item 126(b))
						}
					}
				}
				range_bytes           = 0;
				potential_range_bytes = 0;
			}
		};

		for (size_t page_index = first; page_index < last; page_index++) {
			auto&      page    = region.pages[page_index];
			const auto address = base_addr + page_index * PAGE_SIZE;
			const bool update  = !masked || mask->Get(page_index);

			const auto old_perms = page.Perms();
			const auto new_count = update ? page.AddDelta<track ? 1 : -1, is_read>(address)
			                              : page.AddDelta<0, is_read>(address);
			const auto new_perms = page.Perms();

			if (new_perms != perms) [[unlikely]] {
				release_pending();
				perms = new_perms;
			} else if (range_bytes != 0) {
				potential_range_bytes += PAGE_SIZE;
			}

			if (!update) {
				continue;
			}
			if (batch && region.has_pending && IsPending(region, page_index)) {
				// This caller's watcher lands on a page whose host protection still lags (a
				// deferred change of another caller): the scope's flush must cover it too.
				ExtendSlot(*slot, page_index, page_index + 1);
			}

			const bool watcher_edge = (track && new_count == 1) || (!track && new_count == 0);
			if (watcher_edge && old_perms != new_perms) {
				if (range_bytes == 0) {
					range_begin           = page_index;
					potential_range_bytes = PAGE_SIZE;
				}
				range_bytes = potential_range_bytes;
			}
		}

		release_pending();
		}
		if (!batch && !defer && !protected_any) {
			// pb_sync_noprot: the apply lock was taken and no page changed Perms() - the ceiling of
			// taking it only when an edge exists (A2b, not implemented).
			Common::FrameStats::Add(Common::FrameStats::Counter::ApplySyncNoProtect, 1);
			Common::FrameStats::Add(Common::FrameStats::Counter::ApplySyncNoProtectWaitNs,
			                        apply.WaitedNs());
		}
		if (batched_pages != 0) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BatchPages, batched_pages);
		}
		if (enqueue) {
			EnqueueRegion(&region, base_addr);
		}
	}

	template <bool track, bool is_read, bool lw = false>
	void UpdatePageWatchers(uint64_t vaddr, uint64_t size, bool defer = false) {
		ValidateRange(vaddr, size);
		const auto begin = Common::AlignDown(vaddr, PAGE_SIZE);
		const auto end   = Common::AlignUp(vaddr + size, PAGE_SIZE);
		for (auto chunk_begin = begin; chunk_begin < end;) {
			const auto chunk_end = std::min(end, Common::AlignUp(chunk_begin + 1, REGION_SIZE));
			const auto region_base = Common::AlignDown(chunk_begin, REGION_SIZE);
			auto*      region = track ? GetOrCreateRegion(chunk_begin) : FindRegion(chunk_begin);
			if (region == nullptr) {
				Fatal("untracking unknown page 0x%016" PRIx64, chunk_begin);
			}
			const auto first = static_cast<size_t>((chunk_begin - region_base) / PAGE_SIZE);
			const auto last  = static_cast<size_t>((chunk_end - region_base) / PAGE_SIZE);
			UpdateRegionWatchers<track, is_read, false, lw>(*region, region_base, first, last, nullptr,
			                                            defer);
			chunk_begin = chunk_end;
		}
	}

	// --- knob "protceil" (session 128) ------------------------------------------------------------

	// The mask of `count` bits from bit `bit` of a word (count 1..64, bit + count <= 64).
	static uint64_t BitRun(size_t bit, size_t count) noexcept {
		return (count == 64 ? ~uint64_t {0} : (uint64_t {1} << count) - 1u) << bit;
	}

	// A skipped arming (latch 1, GuestGpu thread, `apply` held): U on the run, the region listed for the re-arm pass.
	void SkipRun(Region& region, uint64_t base_addr, size_t first, size_t count, Arm arm) {
		namespace FS = Common::FrameStats;
		uint64_t set = 0;
		for (size_t page = first; page < first + count;) {
			const auto bit  = page % 64;
			const auto n    = std::min<size_t>(64 - bit, first + count - page);
			auto&      word = region.unarmed[page / 64];
			const auto mask = BitRun(bit, n);
			set += static_cast<uint64_t>(std::popcount(mask & ~word));
			word |= mask;
			page += n;
		}
		region.has_unarmed = true;
		if (!region.unarmed_listed) {
			region.unarmed_listed = true;
			unarmed_regions.emplace_back(&region, base_addr);
		}
		FS::Add(FS::Counter::PcSkipN, 1);
		FS::Add(FS::Counter::PcSkipPages, count);
		if (arm == Arm::Scope) {
			FS::Add(FS::Counter::PcSkipScopeN, 1);
		} else if (arm == Arm::Range) {
			FS::Add(FS::Counter::PcSkipRngN, 1);
		}
		FS::Add(FS::Counter::PcUSet, set);
		FS::Add(FS::Counter::PcULive, set);
	}

	// An application of [first, first + count) completed (any thread, `apply` held): its pages carry Perms() on the host
	// again, so their U bits go - pc_u_clr, or pc_rearm_pages and pc_rearm_decl inside the re-arm pass of this thread.
	// Every U bit 1 -> 0 is counted exactly once (item 89(zh)).
	static void ClearUnarmed(Region& region, size_t first, size_t count) {
		namespace FS     = Common::FrameStats;
		uint64_t cleared = 0;
		for (size_t page = first; page < first + count;) {
			const auto bit  = page % 64;
			const auto n    = std::min<size_t>(64 - bit, first + count - page);
			auto&      word = region.unarmed[page / 64];
			const auto mask = BitRun(bit, n);
			cleared += static_cast<uint64_t>(std::popcount(mask & word));
			word &= ~mask;
			page += n;
		}
		if (cleared == 0) {
			return;
		}
		if (t_ceil_rearm) {
			FS::Add(FS::Counter::PcRearmPages, cleared);
			FS::Add(FS::Counter::PcRearmDecl, cleared);
		} else {
			FS::Add(FS::Counter::PcUClr, cleared);
		}
		FS::Add(FS::Counter::PcULive, uint64_t {0} - cleared);
	}

	// The re-arm pass (PageManager::CeilRearm), GuestGpu thread, no lock held on entry.
	void CeilRearm(void* context, PageManager::DeclareFunc declare) {
		if (unarmed_regions.empty()) {
			return;
		}
		namespace FS  = Common::FrameStats;
		const auto t0 = FS::Enabled() ? FS::NowNs() : 0;
		struct Run {
			uint64_t vaddr;
			uint64_t size;
		};
		uint64_t pend      = 0;
		uint64_t odd       = 0;
		uint64_t decl      = 0;
		uint64_t run_count = 0;
		// Under `apply` and `lock` of one region: the U bit of a pending page goes (its application writes Perms()), the
		// U bit of a page not read-only on the tracker goes as pc_rearm_odd; every other U page joins a run of `out`
		// (runs never cross a region) and keeps its bit when `keep`.
		const auto sweep = [&](Region& region, uint64_t base_addr, bool keep, std::vector<Run>& out) {
			for (size_t word = 0; word < region.unarmed.size(); word++) {
				auto bits = region.unarmed[word];
				while (bits != 0) {
					const auto bit  = static_cast<size_t>(std::countr_zero(bits));
					const auto mask = uint64_t {1} << bit;
					bits &= bits - 1u;
					const auto page = word * 64 + bit;
					if (region.has_pending && IsPending(region, page)) {
						region.unarmed[word] &= ~mask;
						pend++;
						continue;
					}
					if (region.pages[page].Perms() != Common::VirtualMemory::Mode::Read) {
						region.unarmed[word] &= ~mask;
						odd++;
						continue;
					}
					if (!keep) {
						region.unarmed[word] &= ~mask;
					}
					const auto vaddr = base_addr + page * PAGE_SIZE;
					if (!out.empty() && out.back().vaddr + out.back().size == vaddr && vaddr % REGION_SIZE != 0) {
						out.back().size += PAGE_SIZE;
					} else {
						out.push_back({vaddr, PAGE_SIZE});
					}
				}
			}
		};
		// 1. The runs to declare, their bits kept: until an application covers a page, P' needs its mark.
		std::vector<Run> runs;
		for (const auto& [region, base_addr]: unarmed_regions) {
			ApplyGuard apply(region->apply, true);
			SpinGuard  lock(region->lock);
			sweep(*region, base_addr, true, runs);
		}
		// 2. The declaration, with no lock held (item 89(v)(1)): the standard guest-write notification of both caches
		//    flushes GPU data first, marks the pages CPU-dirty and drops the watchers; the next synchronization at 0
		//    uploads and arms them. An application it makes on this thread clears U as pc_rearm_decl.
		t_ceil_rearm = true;
		for (const auto& run: runs) {
			declare(context, run.vaddr, run.size);
		}
		t_ceil_rearm = false;
		run_count += runs.size();
		// 3. The fallback: what the declaration left read-only on the tracker (another watcher, an unmapped range) is
		//    protected read-only in the same apply hold that read it (Region::apply, P); every U bit goes.
		std::vector<Run> rest;
		for (const auto& [region, base_addr]: unarmed_regions) {
			ApplyGuard apply(region->apply, true);
			rest.clear();
			{
				SpinGuard lock(region->lock);
				sweep(*region, base_addr, false, rest);
				region->has_unarmed    = false;
				region->unarmed_listed = false;
			}
			for (const auto& run: rest) {
				Protect(run.vaddr, run.size, Common::VirtualMemory::Mode::Read);
				decl += run.size / PAGE_SIZE;
			}
			run_count += rest.size();
		}
		unarmed_regions.clear();
		FS::Add(FS::Counter::PcRearmN, 1);
		FS::Add(FS::Counter::PcRearmRuns, run_count);
		FS::Add(FS::Counter::PcRearmPages, pend + odd + decl);
		FS::Add(FS::Counter::PcRearmDecl, decl);
		FS::Add(FS::Counter::PcRearmPend, pend);
		FS::Add(FS::Counter::PcRearmOdd, odd);
		FS::Add(FS::Counter::PcULive, uint64_t {0} - (pend + odd + decl));
		if (t0 != 0) {
			FS::Add(FS::Counter::PcRearmNs, FS::NowNs() - t0);
		}
	}

	// --- deferred host protection -------------------------------------------------------------

	static bool DeferEnabled() {
		static const bool enabled = [] {
			const char* value = std::getenv("KYTY_ASYNC_PROTECT");
			return value == nullptr || std::atoi(value) != 0;
		}();
		return enabled;
	}

	struct QueuedRegion {
		Region*  region;
		uint64_t base_addr;
	};

	void EnqueueRegion(Region* region, uint64_t base_addr) {
		{
			std::lock_guard lock(queue_mutex);
			if (!worker_started) {
				worker_started = true;
				worker         = std::thread([this] { WorkerThread(); });
			}
			queue.push_back({region, base_addr});
			inflight.fetch_add(1, std::memory_order_acq_rel);
		}
		queue_cv.notify_one();
	}

	[[nodiscard]] static bool IsPending(const Region& region, size_t page) {
		return ((region.pending[page / 64] >> (page % 64)) & 1u) != 0;
	}

	// Gate "applyskip": why FlushRegion of [first, last) would have to take the apply lock, read
	// without any lock. 0 - nothing: no page of the window is pending and no run of it is in
	// flight; 1 - a pending page; 2 - an in-flight run with ReadWrite intersects the window; 3 - an
	// in-flight run with another protection does.
	// Why 0 is safe (Region::apply, R): TakePendingRun publishes a run in `applying_run` (seq_cst)
	// before it clears the bits, and the run is withdrawn only after its host call returned, with
	// `apply` still held. The bits are read first and `applying_run` second, so a bit seen clear was
	// cleared either by a run still visible below or by one whose change is in effect. The
	// synchronous path (ProtectRun) clears its bits only after its host call. A change a caller
	// built on was made under a lock the caller took afterwards, so its bit is visible here; a
	// bit set after the read belongs to a change the caller could not observe - its author
	// flushes it (BatchScope) or the worker applies it before the flip.
	[[nodiscard]] static int FlushBlocker(Region& region, size_t first, size_t last) noexcept {
		last = std::min(last, static_cast<size_t>(REGION_PAGES));
		if (first >= last) {
			return 0;
		}
		const auto first_word = first / 64;
		const auto last_word  = (last - 1) / 64;
		for (size_t word = first_word; word <= last_word; word++) {
			auto bits = std::atomic_ref<uint64_t>(region.pending[word]).load(std::memory_order_acquire);
			if (word == first_word) {
				bits &= ~uint64_t {0} << (first % 64);
			}
			if (word == last_word && last % 64 != 0) {
				bits &= (uint64_t {1} << (last % 64)) - 1u;
			}
			if (bits != 0) {
				return 1;
			}
		}
		const auto run       = region.applying_run.load(std::memory_order_acquire);
		const auto run_first = static_cast<size_t>(run & 0xffffu);
		const auto run_last  = static_cast<size_t>((run >> 16u) & 0xffffu);
		if (run_first >= run_last || run_last <= first || run_first >= last) {
			return 0;
		}
		const auto protection = static_cast<Common::VirtualMemory::Mode>(static_cast<uint32_t>(run >> 32u));
		return protection == Common::VirtualMemory::Mode::ReadWrite ? 2 : 3;
	}

	static PageManager::BatchScope::Slot* ReserveSlot(PageManager::BatchScope& scope, Region& region,
													  uint64_t base_addr) {
		for (uint32_t index = 0; index < scope.m_count; index++) {
			if (scope.m_slots[index].region == &region) {
				return &scope.m_slots[index];
			}
		}
		if (scope.m_count == PageManager::BatchScope::Capacity) {
			return nullptr; // full: this change stays synchronous
		}
		auto& slot = scope.m_slots[scope.m_count++];
		slot       = {&region, base_addr, UINT32_MAX, 0};
		return &slot;
	}

	static void ExtendSlot(PageManager::BatchScope::Slot& slot, size_t first, size_t last) {
		slot.first = std::min(slot.first, static_cast<uint32_t>(first));
		slot.last  = std::max(slot.last, static_cast<uint32_t>(last));
	}

	// Under region.lock: takes the first pending run of [first, last) - consecutive pending pages
	// with the same host protection, at most max_pages - and clears its bits. The protection is
	// read here, inside the caller's apply hold (Region::apply). False if the window has none.
	// `swallow_gaps` (gate "protbatch2"): the run may also cover pages that are not pending, as long
	// as their Perms() equals the run's protection and that protection is not ReadWrite. Such a page
	// is protected exactly as Perms() says (Region::apply, P), so re-applying its own value changes
	// nothing, and a page whose Perms() is not ReadWrite carries a watcher, i.e. it is mapped and was
	// protected successfully before - the host call cannot fail on it. This is what turns the runs of
	// a whole pass into one call per region. The run never reaches past its last pending page, so it
	// touches nothing beyond what the caller's window already covers.
	static bool TakePendingRun(Region& region, size_t first, size_t last, size_t max_pages,
							   bool swallow_gaps, size_t* run_first, size_t* run_pages,
							   Common::VirtualMemory::Mode* perms) {
		if (!region.has_pending) {
			return false;
		}
		last = std::min(last, static_cast<size_t>(REGION_PAGES));
		for (size_t page = first; page < last;) {
			const auto word = region.pending[page / 64] >> (page % 64);
			if (word == 0) {
				page = (page / 64 + 1) * 64;
				continue;
			}
			page += static_cast<size_t>(std::countr_zero(word));
			if (page >= last) {
				break;
			}
			const auto protection = region.pages[page].Perms();
			const bool swallow = swallow_gaps && protection != Common::VirtualMemory::Mode::ReadWrite;
			size_t     end     = page + 1;
			size_t     taken   = end; // one past the last pending page of the run
			uint64_t   gaps    = 0;
			while (end < last && end - page < max_pages &&
				   region.pages[end].Perms() == protection) {
				const bool pending = IsPending(region, end);
				if (!pending && !swallow) {
					break;
				}
				end++;
				if (pending) {
					taken = end;
				} else {
					gaps++;
				}
			}
			gaps -= end - taken; // trailing swallowed pages are dropped again
			end = taken;
			if (gaps != 0) {
				Common::FrameStats::Add(Common::FrameStats::Counter::PassGapRuns, 1);
				Common::FrameStats::Add(Common::FrameStats::Counter::PassGapPages, gaps);
			}
			if (region.applying_run.load(std::memory_order_relaxed) != 0) {
				// pb_inflight_bad: the previous run of an application was never withdrawn.
				Common::FrameStats::Add(Common::FrameStats::Counter::ApplyInflightBad, 1);
			}
			// Visible before the bits are cleared and until the host call returned (FlushBlocker,
			// KeepApplied). The fence orders the relaxed clears below after the store: a reader
			// that sees a bit clear and no run in flight sees an application that completed.
			region.applying_run.store(static_cast<uint64_t>(page) | (static_cast<uint64_t>(end) << 16u) |
			                          (uint64_t {static_cast<uint32_t>(protection)} << 32u),
			                      std::memory_order_seq_cst);
			std::atomic_thread_fence(std::memory_order_release);
			SetPendingRange(region, page, end - page, false);
			*run_first = page;
			*run_pages = end - page;
			*perms     = protection;
			return true;
		}
		if (std::all_of(region.pending.begin(), region.pending.end(),
						[](uint64_t word) { return word == 0; })) {
			region.has_pending = false;
		}
		return false;
	}

	// Applies the pending runs of one region on the worker, one run per apply hold: the value of
	// each run is read inside that hold (Region::apply), so a synchronous change or a flush of the
	// same pages can neither be overtaken by a stale value nor overtake one. Between runs the
	// worker holds nothing and yields to synchronous callers (before: it held the spin lock of the
	// region across all its calls and yielded inside it).
	void ApplyPending(Region& region, uint64_t base_addr) {
		{
			SpinGuard lock(region.lock);
			region.queued = false;
			if (!region.has_pending) {
				return;
			}
		}
		const auto call_pages = WorkerCallPages();
		for (;;) {
			while (sync_waiters.load(std::memory_order_acquire) != 0) {
				std::this_thread::yield();
			}
			ApplyGuard                  apply(region.apply, true, Common::FrameStats::Counter::ApplyWaitWorkerNs);
			size_t                      run_first = 0;
			size_t                      run_pages = 0;
			Common::VirtualMemory::Mode perms     = Common::VirtualMemory::Mode::ReadWrite;
			{
				SpinGuard lock(region.lock);
				if (!TakePendingRun(region, 0, REGION_PAGES, call_pages, false, &run_first,
									&run_pages, &perms)) {
					break;
				}
			}
			Protect(base_addr + run_first * PAGE_SIZE, run_pages * PAGE_SIZE, perms);
			if (region.has_unarmed) {
				ClearUnarmed(region, run_first, run_pages); // knob "protceil": U goes with the application
			}
			region.applying_run.store(0, std::memory_order_release); // before `apply` is released
		}
	}

	// Applies the pending runs of [first, last) of one region (a BatchScope flush, or an
	// invalidation making sure a change deferred by another thread is in effect). The spin lock is
	// released before every host call, only the apply lock is held across them. Takes the apply
	// lock even when nothing is pending (Region::apply, R) - unless gate "applyskip" is on and
	// FlushBlocker finds nothing to wait for. `site` receives the apply-lock wait. Returns the
	// number of host calls.
	uint32_t FlushRegion(Region& region, uint64_t base_addr, size_t first, size_t last,
	                     Common::FrameStats::Counter site) {
		namespace FS = Common::FrameStats;
		// With the gate off the lock-free answer is computed only for the counters (trace runs).
		const bool skip    = Common::Gates::Enabled(Common::Gates::Gate::ApplySkip);
		int        blocker = -1;
		if (skip || FS::Enabled()) {
			blocker = FlushBlocker(region, first, last);
			if (blocker == 0) {
				FS::Add(FS::Counter::ApplySkipWould, 1);
				if (skip) {
					FS::Add(FS::Counter::ApplySkips, 1);
					return 0;
				}
			} else if (blocker == 2) {
				FS::Add(FS::Counter::ApplySkipBlockRw, 1);
			} else if (blocker == 3) {
				FS::Add(FS::Counter::ApplySkipBlockRo, 1);
			}
		}
		const bool would = blocker == 0;
		ApplyGuard apply(region.apply, true, site,
		                 would ? FS::Counter::ApplySkipWouldWaitNs : FS::Counter::Count,
		                 would ? FS::Counter::ApplySkipWouldWaitGpuNs : FS::Counter::Count);
		t_protect_masked      = false;
		const auto call_pages = WorkerCallPages();
		// Gate "protbatch2": a flush of a whole pass finds the pending runs of several buffers in one
		// region; letting a run cover the already read-only pages between them makes it one host call.
		// Only the flushes of the pass itself: every other flush (fault handler, protection worker,
		// texture invalidation) carries the runs of one caller, where swallowing only widens the
		// host call and makes pb2_gap* count someone else's pages. Without "protbatch" nothing is
		// deferred on this path anyway, so the pass owning its flush is not enough on its own.
		const bool swallow_gaps = t_pass != nullptr && t_pass->m_owns_flush &&
		                          Common::Gates::Enabled(Common::Gates::Gate::ProtectBatch);
		uint32_t   runs       = 0;
		uint64_t   pages      = 0;
		for (;;) {
			size_t                      run_first = 0;
			size_t                      run_pages = 0;
			Common::VirtualMemory::Mode perms     = Common::VirtualMemory::Mode::ReadWrite;
			{
				SpinGuard lock(region.lock);
				if (!TakePendingRun(region, first, last, call_pages, swallow_gaps, &run_first,
									&run_pages, &perms)) {
					break;
				}
			}
			// Session 128, knob "protceil": a run to read-only is an arming (item 89(z)); at a latch of 1 it is skipped and
			// its pages marked unarmed - its pending bits are gone and it is withdrawn as after a host call.
			const auto arm = perms != Common::VirtualMemory::Mode::Read ? Arm::No
							 : site == FS::Counter::ApplyWaitScopeNs    ? Arm::Scope
																		 : Arm::Range;
			if (arm != Arm::No && t_ceil_state == CeilSkip) [[unlikely]] {
				SkipRun(region, base_addr, run_first, run_pages, arm);
				region.applying_run.store(0, std::memory_order_release); // before `apply` is released
				continue;
			}
			Protect(base_addr + run_first * PAGE_SIZE, run_pages * PAGE_SIZE, perms, arm);
			if (region.has_unarmed) {
				ClearUnarmed(region, run_first, run_pages);
			}
			region.applying_run.store(0, std::memory_order_release); // before `apply` is released
			runs++;
			pages += run_pages;
		}
		if (runs != 0) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BatchRuns, runs);
			Common::FrameStats::Add(Common::FrameStats::Counter::BatchKb, pages * (PAGE_SIZE / 1024u));
		}
		return runs;
	}

	void FlushRange(uint64_t vaddr, uint64_t size) {
		ValidateRange(vaddr, size);
		const auto begin = Common::AlignDown(vaddr, PAGE_SIZE);
		const auto end   = Common::AlignUp(vaddr + size, PAGE_SIZE);
		for (auto chunk_begin = begin; chunk_begin < end;) {
			const auto chunk_end   = std::min(end, Common::AlignUp(chunk_begin + 1, REGION_SIZE));
			const auto region_base = Common::AlignDown(chunk_begin, REGION_SIZE);
			if (auto* region = FindRegion(chunk_begin); region != nullptr) {
				Common::FrameStats::Add(Common::FrameStats::Counter::BatchInvalidateFlushes, 1);
				if (FlushRegion(*region, region_base,
								static_cast<size_t>((chunk_begin - region_base) / PAGE_SIZE),
								static_cast<size_t>((chunk_end - region_base) / PAGE_SIZE),
								Common::FrameStats::Counter::ApplyWaitRangeNs) != 0) {
					Common::FrameStats::Add(Common::FrameStats::Counter::BatchRefault, 1);
				}
			}
			chunk_begin = chunk_end;
		}
	}

	// --- knob "armcopy" (session 129, docs/session-129/design129.md rev 2) ---------------------------------------------

	static constexpr uint8_t AcReasonWr = 0xff; // the reason of a written synchronization (not an ArmCopyReason)

	// Session 130, knob "acinline": ai_kept_* and one of its reason rows.
	static void AiAddKept(uint64_t ns, Common::FrameStats::Counter n, Common::FrameStats::Counter n_ns) {
		namespace FS = Common::FrameStats;
		FS::Add(FS::Counter::AiKeptN, 1);
		FS::Add(FS::Counter::AiKeptNs, ns);
		FS::Add(n, 1);
		FS::Add(n_ns, ns);
	}

	static void AcAddKept(uint64_t ns, Common::FrameStats::Counter n, Common::FrameStats::Counter n_ns) {
		namespace FS = Common::FrameStats;
		FS::Add(FS::Counter::AcKeptN, 1);
		FS::Add(FS::Counter::AcKeptNs, ns);
		FS::Add(n, 1);
		FS::Add(n_ns, ns);
	}

	// The pages of one region as bits.
	using PageBits = std::array<uint64_t, REGION_PAGES / 64>;

	static void BitsSet(PageBits& bits, size_t first, size_t last) noexcept {
		for (size_t page = first; page < last;) {
			const auto bit = page % 64;
			const auto n   = std::min<size_t>(64 - bit, last - page);
			bits[page / 64] |= BitRun(bit, n);
			page += n;
		}
	}

	[[nodiscard]] static bool BitsTest(const PageBits& bits, size_t page) noexcept {
		return ((bits[page / 64] >> (page % 64)) & 1u) != 0;
	}

	[[nodiscard]] static uint64_t BitsCount(const PageBits& bits) noexcept {
		uint64_t count = 0;
		for (const auto word: bits) {
			count += static_cast<uint64_t>(std::popcount(word));
		}
		return count;
	}

	// func(first, last) for every run of set bits, ascending.
	template <typename Func>
	static void BitsRuns(const PageBits& bits, Func&& func) {
		size_t page = 0;
		while (page < REGION_PAGES) {
			const auto word = bits[page / 64] >> (page % 64);
			if (word == 0) {
				page = (page / 64 + 1) * 64;
				continue;
			}
			page += static_cast<size_t>(std::countr_zero(word));
			size_t end = page + 1;
			while (end < REGION_PAGES && BitsTest(bits, end)) {
				end++;
			}
			func(page, end);
			page = end;
		}
	}

	// The operation of this thread between ArmCopyBegin and ArmCopyFinish (GuestGpu thread only).
	struct AcWindow {
		Region*  region;
		uint64_t base;
		uint32_t first;
		uint32_t last;
	};
	struct AcCopy {
		uint64_t vaddr;
		uint64_t size;
		bool     pooled;
	};
	struct AcArea {
		Region*  region;
		uint64_t base;
		PageBits win;    // handed-over windows
		PageBits pooled; // pages of pooled copies (their chunks arm them)
		PageBits own;    // pages of inline / temporary copies (GuestGpu armed them before reading)
	};
	struct AcOp {
		uint32_t                                                 mode         = 0;
		uint32_t                                                 window_count = 0;
		std::array<AcWindow, PageManager::BatchScope::Capacity> windows {};
		bool                                                     windows_flushed = false;
		std::vector<AcCopy>                                      copies;
		std::vector<AcArea>                                      areas;
		// Session 130, knob "acinline" (I1'', I2', I3', I11): the flag of this operation (written with every mode, cleared by
		// AcFinish) and the inline copies put in the batch and not yet enqueued.
		bool                                                     ai_inline  = false;
		uint32_t                                                 ai_pending = 0;
	};

	// What the detector saw under `lock`: pend_now and Perms() of each page it looked at.
	struct AcSnap {
		PageBits                            pend {};
		std::array<uint8_t, REGION_PAGES> perms {};
	};

	// Session 130, ac_cbad attribution (docs/session-130/cbad130.md rev 2 s.2.3, s.4 C2/C3): the snapshot S_a of the chunk
	// this thread copies, from its AcChunk (2/3/4) to the end of its check - key {vaddr, size, mode}, the first region of the
	// chunk and the chunk's window in it, J (pending at the start of the hold), T (taken), St (taken with the bit still set in
	// the hold of the take), Pa (pending in the detector's snapshot, window only), Ba (bad in it). `multi`: the chunk met a
	// second region (its pages have no snapshot - R1 nosnap).
	struct AcCls {
		bool     valid  = false;
		bool     multi  = false;
		uint32_t mode   = 0;
		uint64_t vaddr  = 0;
		uint64_t size   = 0;
		Region*  region = nullptr;
		uint64_t base   = 0;
		size_t   first  = 0;
		size_t   last   = 0;
		PageBits j {};
		PageBits t {};
		PageBits st {};
		PageBits pa {};
		PageBits ba {};
		// Session 131, knob "lwin" (L9): the latch of lwin the chunk read (0 = no classifier) and g_take.
		uint32_t lw      = 0;
		uint64_t lw_take = 0;
	};

	class AcReasonScope final {
	public:
		explicit AcReasonScope(PageManager::ArmCopyReason reason) noexcept: m_previous(t_ac_reason) {
			t_ac_reason = reason;
		}
		~AcReasonScope() { t_ac_reason = m_previous; }
		KYTY_CLASS_NO_COPY(AcReasonScope);

	private:
		PageManager::ArmCopyReason m_previous;
	};

	// The refusal of a latch of `value` >= 1 (s.8.2), nullptr if none; `bit` names it for the one-time log line.
	static const char* AcRefusal(uint32_t value, uint32_t* bit) {
		namespace G  = Common::Gates;
		namespace FS = Common::FrameStats;
		// F2 (codereview129, ROADMAP s122 item 103(b)): the latch of this synchronization's CeilScope (opened right before
		// ArmCopyScope, same engage), not a second read of the knob - an arm switching protceil between the two latches
		// cannot mix a skip or a dose with the move inside one operation.
		if (t_ceil_state != CeilOutside && t_ceil_state != CeilZero) {
			*bit = 8;
			return "protceil";
		}
		if (G::Enabled(G::Gate::ArmDefer)) {
			*bit = 9;
			return "armdefer";
		}
		if (G::Enabled(G::Gate::ProtectBatchPass) && G::Enabled(G::Gate::ProtectBatch)) {
			*bit = 10;
			return "protbatch2";
		}
		if (!G::Enabled(G::Gate::ProtectBatch)) {
			*bit = 11;
			return "protbatch0";
		}
		if (!Common::AsyncCopyOn()) {
			*bit = 12;
			return "asynccopy";
		}
		if (!Common::CopyPoolEnabled()) {
			*bit = 13;
			return "nopool";
		}
		if (!DeferEnabled()) {
			*bit = 14;
			return "asyncprotect";
		}
		if (G::Value(G::Knob::BufImport) != 0) {
			*bit = 15;
			return "bufimp";
		}
		if (value >= 2 && !FS::Enabled()) {
			*bit = 16;
			return "notrace";
		}
		return nullptr;
	}

	// The state-only detector (s.7.1), under the `apply` hold of `region` the caller holds - no application of the region
	// is in flight and the host of its pages is frozen. For the pages of `mask`: under `lock` the snapshot watched /
	// pend_now / Perms(); then, `lock` released, VirtualQuery once per homogeneous host run of the pages watched and not
	// pending. bad = watched && !pend_now && host writable; chk = watched && !pend_now. The caller's bookkeeping (what it
	// took, what it applied) is not an input.
	void AcDetect(Region& region, uint64_t base_addr, const PageBits& mask, bool job, uint32_t mode, AcSnap& snap,
	              uint64_t* chk, uint64_t* bad, PageBits* bad_bits = nullptr) {
		PageBits candidates {};
		{
			SpinGuard lock(region.lock);
			for (size_t word = 0; word < mask.size(); word++) {
				auto bits = mask[word];
				while (bits != 0) {
					const auto bit  = static_cast<size_t>(std::countr_zero(bits));
					const auto flag = uint64_t {1} << bit;
					bits &= bits - 1u;
					const auto  page  = word * 64 + bit;
					const auto& state = region.pages[page];
					snap.perms[page]  = static_cast<uint8_t>(state.Perms());
					if (IsPending(region, page)) {
						snap.pend[word] |= flag;
					} else if (state.write_watchers != 0 || state.access_watchers != 0) {
						candidates[word] |= flag;
					}
				}
			}
		}
		*chk += BitsCount(candidates);
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
		uint64_t host_end = 0; // one past the last byte the previous answer covered
		bool     host_w   = false;
		uint32_t protect  = 0;
		BitsRuns(candidates, [&](size_t first, size_t last) {
			for (size_t page = first; page < last; page++) {
				const auto vaddr = base_addr + page * PAGE_SIZE;
				if (vaddr >= host_end) {
					MEMORY_BASIC_INFORMATION info {};
					if (VirtualQuery(reinterpret_cast<LPCVOID>(vaddr), &info, sizeof(info)) == 0) {
						host_w   = false;
						protect  = 0;
						host_end = vaddr + PAGE_SIZE;
					} else {
						protect  = static_cast<uint32_t>(info.Protect & 0xffu);
						host_w   = info.State == MEM_COMMIT &&
						         (protect == PAGE_READWRITE || protect == PAGE_WRITECOPY ||
						          protect == PAGE_EXECUTE_READWRITE || protect == PAGE_EXECUTE_WRITECOPY);
						// The answer holds from BaseAddress (the page of vaddr) for RegionSize bytes.
						host_end = reinterpret_cast<uint64_t>(info.BaseAddress) + info.RegionSize;
					}
				}
				if (host_w) {
					(*bad)++;
					if (bad_bits != nullptr) { // ac_cbad attribution (cbad130.md rev 2 s.4 C1): Ba of the snapshot S_a
						BitsSet(*bad_bits, page, page + 1);
					}
					static std::atomic<uint32_t> logged {0};
					if (logged.fetch_add(1, std::memory_order_relaxed) < 40) {
						LOGF("ArmCopyVerify: MISMATCH br=%s addr=0x%016llx perms=%u pend=0 host=0x%x mode=%u\n",
						     job ? "job" : "gpu", static_cast<unsigned long long>(vaddr),
						     static_cast<unsigned>(snap.perms[page]), static_cast<unsigned>(protect),
						     static_cast<unsigned>(mode));
					}
				}
			}
		});
#else
		(void)base_addr;
		(void)job;
		(void)mode;
		(void)bad;
		(void)bad_bits;
#endif
	}

	// The host protection of one page for a LEFT line (host=): the low byte of Protect from VirtualQuery, 0 when the query
	// fails, the page is not committed, or off Windows. Called under the caller's `apply` hold (the host is frozen).
	static uint32_t AcHostProtect(uint64_t vaddr) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
		MEMORY_BASIC_INFORMATION info {};
		if (VirtualQuery(reinterpret_cast<LPCVOID>(vaddr), &info, sizeof(info)) == 0 || info.State != MEM_COMMIT) {
			return 0;
		}
		return static_cast<uint32_t>(info.Protect & 0xffu);
#else
		(void)vaddr;
		return 0;
#endif
	}

	// ArmCopyVerify: LEFT - one line per run of `left` with the same Perms() in the snapshot, the same host protection
	// (host=) and, for a chunk, the same membership in the pages it took (rm=; `taken` null on the GuestGpu branch: rm=-)
	// and the same freshness of the mark (remark=1: a page the chunk took whose pending bit read clear in the hold of that
	// take - pending again only by a mark made after the take; remark=0: not taken, or taken with its bit still set - `stale`;
	// remark=- on the GuestGpu branch) (ROADMAP s122 items 101(b), 105(b)(3)). At most 40 lines per process.
	static void AcLogLeft(const PageBits& left, const AcSnap& snap, const PageBits* taken, const PageBits* stale,
	                      uint64_t base_addr, bool job, uint32_t mode) {
		static std::atomic<uint32_t> logged {0};
		if (logged.load(std::memory_order_relaxed) >= 40) {
			return;
		}
		const auto key = [&](size_t page) {
			const bool rm     = taken != nullptr && BitsTest(*taken, page);
			const bool remark = rm && stale != nullptr && !BitsTest(*stale, page);
			return (rm ? 1u : 0u) | (remark ? 2u : 0u);
		};
		BitsRuns(left, [&](size_t first, size_t last) {
			for (size_t page = first; page < last;) {
				if (logged.load(std::memory_order_relaxed) >= 40) {
					return;
				}
				const auto perms = snap.perms[page];
				const auto k     = key(page);
				const auto host  = AcHostProtect(base_addr + page * PAGE_SIZE);
				size_t     end   = page + 1;
				while (end < last && snap.perms[end] == perms && key(end) == k &&
				       AcHostProtect(base_addr + end * PAGE_SIZE) == host) {
					end++;
				}
				if (logged.fetch_add(1, std::memory_order_relaxed) < 40) {
					LOGF("ArmCopyVerify: LEFT br=%s addr=0x%016llx pages=%u perms=%u rm=%s remark=%s host=0x%x mode=%u\n",
					     job ? "job" : "gpu", static_cast<unsigned long long>(base_addr + page * PAGE_SIZE),
					     static_cast<unsigned>(end - page), static_cast<unsigned>(perms),
					     taken == nullptr ? "-" : ((k & 1u) != 0 ? "1" : "0"),
					     taken == nullptr ? "-" : ((k & 2u) != 0 ? "1" : "0"), static_cast<unsigned>(host),
					     static_cast<unsigned>(mode));
				}
				page = end;
			}
		});
	}

	// Session 130, ac_jstale (ROADMAP s122 item 105(b)(3)): under `lock`, IN THE HOLD of the TakePendingRun that took the
	// run [run_first, run_first + run_pages) - the pages of the run whose pending bit still reads set go to `stale`. Every
	// writer of a pending bit holds `lock` (SetPendingRange: UpdateRegionWatchers, ProtectRun, TakePendingRun), so a page
	// whose bit reads clear here and set in a later snapshot was marked again after the take (a fresh mark), and a page
	// whose bit still reads set here was never cleared by the take - an arming the chunk took and cannot apply. The stamp
	// is the chunk's own local bits: only chunks latched at 2/3 call this; the marking code and the paths of 0 and 1 are
	// untouched.
	static void AcStampTake(const Region& region, size_t run_first, size_t run_pages, PageBits& stale) noexcept {
		for (size_t page = run_first; page < run_first + run_pages && page < REGION_PAGES; page++) {
			if (IsPending(region, page)) {
				stale[page / 64] |= uint64_t {1} << (page % 64);
			}
		}
	}

	// Under `apply` (the caller holds it): the host call of a run TakePendingRun took, then the withdrawal - the body of
	// FlushRegion. A chunk passes Arm::Job for every call (s.3 C5); a GuestGpu flush passes Arm::Range for a run to
	// read-only, as FlushRegion does.
	void AcApplyTaken(Region& region, uint64_t base_addr, size_t run_first, size_t run_pages,
	                  Common::VirtualMemory::Mode perms, Arm arm_read) {
		const auto arm = arm_read == Arm::Job                           ? Arm::Job
		                 : perms == Common::VirtualMemory::Mode::Read ? arm_read
		                                                              : Arm::No;
		Protect(base_addr + run_first * PAGE_SIZE, run_pages * PAGE_SIZE, perms, arm);
		if (region.has_unarmed) {
			ClearUnarmed(region, run_first, run_pages);
		}
		region.applying_run.store(0, std::memory_order_release); // before `apply` is released
	}

	// Under `apply`: every pending run of [first, last) applied (the loop of FlushRegion); the pages taken go to `taken`
	// (may be null), the runs not to Read to `other` (may be null). Returns the runs applied. `stamp` (a chunk at 2 only):
	// each take is read back in its own `lock` hold into `stale` (AcStampTake); the instantiation of 1 is the code of s.129.
	template <bool stamp = false>
	uint32_t AcApplyRuns(Region& region, uint64_t base_addr, size_t first, size_t last, Arm arm_read, PageBits* taken,
	                     uint64_t* other, PageBits* stale = nullptr) {
		const auto call_pages = WorkerCallPages();
		uint32_t   runs       = 0;
		for (;;) {
			size_t                      run_first = 0;
			size_t                      run_pages = 0;
			Common::VirtualMemory::Mode perms     = Common::VirtualMemory::Mode::ReadWrite;
			{
				SpinGuard lock(region.lock);
				if (!TakePendingRun(region, first, last, call_pages, false, &run_first, &run_pages, &perms)) {
					break;
				}
				if constexpr (stamp) {
					AcStampTake(region, run_first, run_pages, *stale);
				}
			}
			if (taken != nullptr) {
				BitsSet(*taken, run_first, run_first + run_pages);
			}
			AcApplyTaken(region, base_addr, run_first, run_pages, perms, arm_read);
			if (other != nullptr && perms != Common::VirtualMemory::Mode::Read) {
				(*other)++;
			}
			runs++;
		}
		return runs;
	}

	// A pool chunk (s.7.4), any thread: per region of [vaddr, vaddr + size) one `apply` hold. 1 - every pending run of its
	// pages applied; 2 - the same, then the detector and the debt (ac_jleft, ac_jremark); 3 - the first run taken, the
	// detector, the copy of the chunk's bytes of this region, the run applied, the rest applied; 4 - the detector only.
	// Returns true when it copied the chunk (3).
	bool AcChunk(uint64_t vaddr, uint64_t size, uint32_t mode, uint8_t* dst, const uint8_t* src) {
		namespace FS = Common::FrameStats;
		// F4 (codereview129, ROADMAP s122 item 103(b)): a masked UpdateRegionWatchers of this thread (GuestGpu helping the
		// pool) does not leak into the protect_masked_* rows of the chunk's calls - as FlushRegion.
		t_protect_masked = false;
		if (size == 0 || mode < 1 || mode > 4) {
			return false; // nothing to arm: the caller copies
		}
		// F3 (codereview129, ROADMAP s122 item 103(b)): a range the tracker never hands out fails loudly, as FlushRange ->
		// ValidateRange does at 0, instead of being copied without its arming.
		ValidateRange(vaddr, size);
		const auto begin = Common::AlignDown(vaddr, PAGE_SIZE);
		const auto end   = Common::AlignUp(vaddr + size, PAGE_SIZE);
		uint32_t   runs  = 0;
		uint64_t   other = 0;
		bool       cls_stored = false; // ac_cbad attribution: the snapshot S_a of the first region is stored
		for (auto chunk_begin = begin; chunk_begin < end;) {
			const auto chunk_end   = std::min(end, Common::AlignUp(chunk_begin + 1, REGION_SIZE));
			const auto region_base = Common::AlignDown(chunk_begin, REGION_SIZE);
			const auto first       = static_cast<size_t>((chunk_begin - region_base) / PAGE_SIZE);
			const auto last        = static_cast<size_t>((chunk_end - region_base) / PAGE_SIZE);
			// The bytes of the chunk inside this region (value 3 copies them in this region's hold).
			const auto byte_begin = std::max(vaddr, chunk_begin);
			const auto byte_end   = std::min(vaddr + size, chunk_end);
			auto*      region     = FindRegion(chunk_begin);
			if (region == nullptr) {
				// Never watched: nothing pending, nothing watched.
				if (mode == 3) {
					std::memcpy(dst + (byte_begin - vaddr), src + (byte_begin - vaddr),
					            static_cast<size_t>(byte_end - byte_begin));
				}
				chunk_begin = chunk_end;
				continue;
			}
			ApplyGuard apply(region->apply, true, FS::Counter::AcJobWaitNs,
			                 t_ai_chunk ? FS::Counter::AiJobWaitNs : FS::Counter::Count);
			if (mode == 1) {
				runs += AcApplyRuns(*region, region_base, first, last, Arm::Job, nullptr, &other);
				chunk_begin = chunk_end;
				continue;
			}
			PageBits window {};
			BitsSet(window, first, last);
			PageBits j {}; // J: the pages pending at the start of the hold
			{
				SpinGuard lock(region->lock);
				for (size_t page = first; page < last; page++) {
					if (IsPending(*region, page)) {
						j[page / 64] |= uint64_t {1} << (page % 64);
					}
				}
			}
			PageBits                    taken {};
			PageBits                    stale {}; // pages of `taken` whose bit still read set in the hold of the take
			size_t                      run_first = 0;
			size_t                      run_pages = 0;
			Common::VirtualMemory::Mode perms     = Common::VirtualMemory::Mode::ReadWrite;
			bool                        took      = false;
			if (mode == 2) {
				runs += AcApplyRuns<true>(*region, region_base, first, last, Arm::Job, &taken, &other, &stale);
			} else if (mode == 3) {
				// Taken by the mechanism's own function: bits cleared, applying_run published, no host call yet.
				SpinGuard lock(region->lock);
				took = TakePendingRun(*region, first, last, WorkerCallPages(), false, &run_first, &run_pages, &perms);
				if (took) {
					BitsSet(taken, run_first, run_first + run_pages);
					AcStampTake(*region, run_first, run_pages, stale);
				}
			}
			// Session 131, knob "lwin" (lw131.md rev 1 L9 with item 127(v)): in the first region of the chunk, right after the
			// takes and under this `apply` hold - at lwin >= 2 the chunk is in flight (the control spins meet it), then g_take.
			uint32_t lw      = 0;
			uint64_t lw_take = 0;
			if (!cls_stored) {
				lw = g_lw.load(std::memory_order_relaxed);
				if (lw != 0) {
					if (lw >= 2) {
						LwFlightEnter(vaddr, size);
					}
					lw_take = LwTake();
				}
			}
			const auto t0  = FS::Enabled() ? FS::NowNs() : 0;
			AcSnap     snap {};
			uint64_t   chk = 0;
			uint64_t   bad = 0;
			PageBits   bad_bits {}; // ac_cbad attribution: Ba of the snapshot S_a
			AcDetect(*region, region_base, window, true, mode, snap, &chk, &bad, &bad_bits);
			if (t0 != 0) {
				FS::Add(FS::Counter::AcChkNs, FS::NowNs() - t0);
			}
			FS::Add(FS::Counter::AcChk, chk);
			FS::Add(FS::Counter::AcBad, bad);
			if (t_ai_chunk) {
				FS::Add(FS::Counter::AiChk, chk);
				FS::Add(FS::Counter::AiBad, bad);
			}
			PageBits left {};
			PageBits remark {};
			PageBits stuck {}; // taken, pending in the snapshot, never cleared by the take
			for (size_t word = 0; word < left.size(); word++) {
				left[word]   = (mode == 4 ? window[word] : j[word]) & snap.pend[word];
				remark[word] = left[word] & taken[word];
				stuck[word]  = remark[word] & stale[word];
			}
			const auto jleft = BitsCount(left);
			FS::Add(FS::Counter::AcJleft, jleft);
			FS::Add(FS::Counter::AcJremark, BitsCount(remark));
			// ac_jstale (ROADMAP s122 item 105(b)(3)): of them, the pages without a fresh mark whose Perms() in the snapshot
			// is not ReadWrite - an arming the chunk took, left pending and did not apply. A strict guard at 2.
			uint64_t jstale = 0;
			BitsRuns(stuck, [&](size_t stuck_first, size_t stuck_last) {
				for (size_t page = stuck_first; page < stuck_last; page++) {
					if (snap.perms[page] != static_cast<uint8_t>(Common::VirtualMemory::Mode::ReadWrite)) {
						jstale++;
					}
				}
			});
			FS::Add(FS::Counter::AcJstale, jstale);
			// Session 130, ac_cbad attribution (cbad130.md rev 2 s.4 C2(c)): the snapshot S_a of this chunk for its check - the
			// first region of the chunk only; a second one marks `multi` and its pages classify as R1. The check clears it.
			if (!cls_stored) {
				cls_stored  = true;
				auto& cls   = t_ac_cls;
				cls.multi   = false;
				cls.mode    = mode;
				cls.vaddr   = vaddr;
				cls.size    = size;
				cls.region  = region;
				cls.base    = region_base;
				cls.first   = first;
				cls.last    = last;
				cls.j       = j;
				cls.t       = taken;
				cls.st      = stale;
				for (size_t word = 0; word < cls.pa.size(); word++) {
					cls.pa[word] = window[word] & snap.pend[word];
				}
				cls.ba      = bad_bits;
				cls.lw      = lw;
				cls.lw_take = lw_take;
				cls.valid   = true;
			} else {
				t_ac_cls.multi = true;
			}
			if (t_ai_chunk) {
				FS::Add(FS::Counter::AiJleft, jleft);
				FS::Add(FS::Counter::AiJstale, jstale);
			}
			if (mode == 2 && jleft != 0) {
				AcLogLeft(left, snap, &taken, &stale, region_base, true, mode);
			}
			if (mode == 3) {
				std::memcpy(dst + (byte_begin - vaddr), src + (byte_begin - vaddr),
				            static_cast<size_t>(byte_end - byte_begin));
				if (took) {
					AcApplyTaken(*region, region_base, run_first, run_pages, perms, Arm::Job);
					if (perms != Common::VirtualMemory::Mode::Read) {
						other++;
					}
					runs++;
				}
				runs += AcApplyRuns(*region, region_base, first, last, Arm::Job, &taken, &other);
			}
			chunk_begin = chunk_end;
		}
		if (other != 0) {
			FS::Add(FS::Counter::AcJobOtherN, other);
		}
		if (runs == 0 && mode != 4) {
			FS::Add(FS::Counter::AcJobNowork, 1);
			if (t_ai_chunk) {
				FS::Add(FS::Counter::AiNowork, 1);
			}
		}
		return mode == 3;
	}

	// Session 130, ac_cbad attribution (docs/session-130/cbad130.md rev 2 s.4 C4, s.4.1, s.4.2; ROADMAP s122 items 116(d),
	// 117(e), 118(b)-(g), 119(b)-(c)): a batch of the event pages of one chunk (n <= 64), on the thread that checked it, no
	// lock held on entry. R1 - no snapshot S_a of this chunk for the page; R2..R6 - the bits of S_a. Then one `apply` hold of
	// the chunk's region (S_k): under `lock` Pk, Perms() and the first CPU-dirty read (dk before); `lock` released,
	// VirtualQuery once per page (prot_k, Wk); an acquire fence and the second CPU-dirty read (dk after); dk = before || after
	// (item 119(b)); `apply` released. Pages without R1..R6: R7 Pk, R8 !Pk && Wk (host_d when dk), else E by prot_k. Adds
	// only ac_cls_*, the CONTENT lines and the histogram; the class counts go to `out`, the caller adds them in the order of I0.
	void AcClassify(uint64_t vaddr, uint64_t size, uint32_t mode, const uint64_t* events, size_t n,
	                PageManager::ArmCopyDirtyFunc dirty, void* dirty_context, PageManager::ArmCopyClassCounts& out) {
		namespace FS = Common::FrameStats;
		constexpr size_t batch = PageManager::ArmCopyClassBatch;
		static_assert(REGION_PAGES <= 65536);
		if (n == 0) {
			return;
		}
		n                  = std::min(n, batch);
		const auto  t0     = FS::Enabled() ? FS::NowNs() : 0;
		const auto& cls    = t_ac_cls;
		const bool snap_ok = cls.valid && cls.region != nullptr && cls.vaddr == vaddr && cls.size == size && cls.mode == mode;
		// why: 0 nosnap, 1 bad, 2 left, 3 stale, 4 remark, 5 new, 6 pend, 7 host (class M); 8 ro, 9 na, 10 oth (class E).
		static constexpr const char* why_names[] = {"nosnap", "bad",  "left", "stale", "remark", "new",
		                                            "pend",   "host", "ro",   "na",    "oth"};
		constexpr uint8_t why_sk   = 0xffu; // decided by the snapshot S_k
		constexpr uint8_t f_sk     = 1u;    // the page has S_a (and gets S_k)
		constexpr uint8_t f_pk     = 2u;
		constexpr uint8_t f_wk     = 4u;
		constexpr uint8_t f_dk     = 8u;
		constexpr uint8_t f_ro     = 16u;
		constexpr uint8_t f_na     = 32u;
		constexpr uint8_t f_dkb    = 64u; // dk before alone (session 131, knob "lwin": CD)
		std::array<uint16_t, batch> index {};
		std::array<uint8_t, batch>  why {};
		std::array<uint8_t, batch>  flags {};
		std::array<uint8_t, batch>  perms {};
		std::array<uint8_t, batch>  prot {};
		bool                        any_sk = false;
		for (size_t i = 0; i < n; i++) {
			if (!snap_ok || FindRegion(events[i]) != cls.region) {
				continue; // R1
			}
			const auto page = static_cast<size_t>((events[i] - cls.base) / PAGE_SIZE);
			if (page < cls.first || page >= cls.last) {
				continue; // R1
			}
			index[i] = static_cast<uint16_t>(page);
			flags[i] = f_sk;
			any_sk   = true;
			if (BitsTest(cls.ba, page)) {
				why[i] = 1;
			} else if (!BitsTest(cls.pa, page)) {
				why[i] = why_sk;
			} else if (!BitsTest(cls.j, page)) {
				why[i] = 5;
			} else if (!BitsTest(cls.t, page)) {
				why[i] = 2;
			} else {
				why[i] = BitsTest(cls.st, page) ? 3 : 4;
			}
		}
		// Session 131, knob "lwin" (lw131.md rev 1 L10 with item 127(g), (e)): the moments of this hold S_k - g_h before its
		// `apply`, the words of each page and g_k (with its clock) last in its `lock`, g_rel and its clock right after `apply`.
		const bool                   lw_on     = cls.lw != 0;
		uint64_t                     lw_h      = 0;
		uint64_t                     lw_k      = 0;
		uint64_t                     lw_k_ns   = 0;
		uint64_t                     lw_rel    = 0;
		uint64_t                     lw_rel_ns = 0;
		std::array<uint64_t, batch> lw_clr {};
		std::array<uint64_t, batch> lw_pend {};
		uint64_t queries = 0;
		if (any_sk) {
			auto& region = *cls.region;
			if (lw_on) {
				lw_h = LwTake();
			}
			ApplyGuard apply(region.apply, true, FS::Counter::AcClsWaitNs);
			{
				SpinGuard lock(region.lock);
				for (size_t i = 0; i < n; i++) {
					if ((flags[i] & f_sk) == 0) {
						continue;
					}
					if (IsPending(region, index[i])) {
						flags[i] |= f_pk;
					}
					perms[i] = static_cast<uint8_t>(region.pages[index[i]].Perms());
					if (dirty(dirty_context, events[i])) { // dk before (item 119(b))
						flags[i] |= f_dk | f_dkb;
					}
					if (lw_on) {
						if (const auto* block = LwBlockOf(events[i]); block != nullptr) {
							const auto& stamp = block->pages[(events[i] % TRACKER_REGION_SIZE) / TRACKER_PAGE_SIZE];
							lw_pend[i]        = stamp.pend.load(std::memory_order_acquire);
							lw_clr[i]         = stamp.clr.load(std::memory_order_relaxed);
						}
					}
				}
				if (lw_on) {
					lw_k    = LwTake(); // g_k: last in this hold of `lock`
					lw_k_ns = FS::NowNs();
				}
			}
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
			for (size_t i = 0; i < n; i++) {
				if ((flags[i] & f_sk) == 0) {
					continue;
				}
				queries++;
				MEMORY_BASIC_INFORMATION info {};
				if (VirtualQuery(reinterpret_cast<LPCVOID>(events[i]), &info, sizeof(info)) == 0) {
					continue; // oth
				}
				const auto protect = static_cast<uint32_t>(info.Protect & 0xffu);
				prot[i]            = static_cast<uint8_t>(protect);
				if (info.State != MEM_COMMIT) {
					continue; // oth
				}
				if (protect == PAGE_READWRITE || protect == PAGE_WRITECOPY || protect == PAGE_EXECUTE_READWRITE ||
				    protect == PAGE_EXECUTE_WRITECOPY) {
					flags[i] |= f_wk;
				} else if (protect == PAGE_READONLY || protect == PAGE_EXECUTE_READ) {
					flags[i] |= f_ro;
				} else if (protect == PAGE_NOACCESS) {
					flags[i] |= f_na;
				}
			}
#endif
			// dk after VirtualQuery, in the same hold (item 118(c)); the fence as before the event's own read.
			std::atomic_thread_fence(std::memory_order_acquire);
			for (size_t i = 0; i < n; i++) {
				if ((flags[i] & f_sk) != 0 && dirty(dirty_context, events[i])) { // dk after
					flags[i] |= f_dk;
				}
			}
		}
		if (any_sk && lw_on) {
			lw_rel    = LwTake(); // g_rel: right after the release of `apply` (the end of the block above)
			lw_rel_ns = FS::NowNs();
		}
		// CONTENT limits: 40 per (mode 2/3/4, class M/E) per process (item 117(e)); the events why=host dk=0 (H) under their
		// own 40 per chunk mode, not spending the (mode, class) limit (item 119(c)).
		static std::array<std::atomic<uint32_t>, 6> logged {};
		static std::array<std::atomic<uint32_t>, 3> logged_h {};
		for (size_t i = 0; i < n; i++) {
			const auto f = flags[i];
			if (why[i] == why_sk) {
				why[i] = (f & f_pk) != 0 ? 6 : (f & f_wk) != 0 ? 7 : (f & f_ro) != 0 ? 8 : (f & f_na) != 0 ? 9 : 10;
			}
			const bool m  = why[i] <= 7;
			const bool dk = (f & f_dk) != 0;
			switch (why[i]) {
				case 0: out.nosnap++; break;
				case 1: out.bad++; break;
				case 2: out.left++; break;
				case 3: out.stale++; break;
				case 4: out.remark++; break;
				case 5: out.fresh++; break;
				case 6: out.pend++; break;
				case 7:
					out.host++;
					if (dk) {
						out.host_d++;
					}
					break;
				case 8: out.ro++; break;
				case 9: out.na++; break;
				default: out.oth++; break;
			}
			if (m) {
				out.m++;
			} else {
				out.e++;
			}
			// Session 131, knob "lwin" (lw131.md rev 1 s.2.1, L10 with items 126, 127(g)): H (R8, dk = 0), CD (R8, dk before
			// = 1), C3 (R2/R3 of a chunk of 3) and CR (R7 whose snapshot S_k holds the mark of the operation that cleared the
			// bit in the window) go to the list of this chunk with the moments of THIS hold; ArmCopyLossResolve decides them.
			if (lw_on && (f & f_sk) != 0) {
				uint8_t kind = 0;
				if (why[i] == 7) {
					kind = (f & f_dkb) != 0 ? LwKindCd : !dk ? LwKindH : 0;
				} else if (mode == 3 && (why[i] == 1 || why[i] == 2)) {
					kind = LwKindC3;
				} else if (why[i] == 6 && LwCrSnapshot(lw_clr[i], lw_pend[i], cls.lw_take, lw_h, lw_k)) {
					kind = LwKindCr;
				}
				if (kind != 0) {
					auto*& list = t_lw_cands;
					if (list == nullptr) {
						list = new (std::nothrow) LwCandList();
					}
					if (list == nullptr || list->n >= LW_CAND_MAX) {
						LwOverflowNote(LwOvfCand);
						LwCountX(kind, out);
					} else {
						auto& c  = list->c[list->n++];
						c        = LwCand {};
						c.page   = events[i];
						c.take   = cls.lw_take;
						c.h      = lw_h;
						c.k      = lw_k;
						c.rel    = lw_rel;
						c.rel_ns = lw_rel_ns;
						c.k_ns   = lw_k_ns;
						c.pin    = LwOp(lw_clr[i]);
						c.mode   = mode;
						c.kind   = kind;
						c.perms  = perms[i];
						out.lw_n++;
					}
				}
			}
			FS::AcHistNote(events[i], mode, m);
			if (mode < 2 || mode > 4) {
				continue;
			}
			const bool h    = why[i] == 7 && !dk;
			auto&      slot = h ? logged_h[mode - 2] : logged[(mode - 2) * 2 + (m ? 0 : 1)];
			if (slot.load(std::memory_order_relaxed) >= 40 || slot.fetch_add(1, std::memory_order_relaxed) >= 40) {
				continue;
			}
			if ((f & f_sk) == 0) {
				LOGF("ArmCopyVerify: CONTENT addr=0x%016llx mode=%u class=M why=nosnap j=- tk=- st=- pa=- ba=- pk=- perms=- "
				     "host=- dk=-\n",
				     static_cast<unsigned long long>(events[i]), static_cast<unsigned>(mode));
			} else {
				const auto page = static_cast<size_t>(index[i]);
				LOGF("ArmCopyVerify: CONTENT addr=0x%016llx mode=%u class=%s why=%s j=%u tk=%u st=%u pa=%u ba=%u pk=%u "
				     "perms=%u host=0x%x dk=%u\n",
				     static_cast<unsigned long long>(events[i]), static_cast<unsigned>(mode), m ? "M" : "E",
				     why_names[why[i]], BitsTest(cls.j, page) ? 1u : 0u, BitsTest(cls.t, page) ? 1u : 0u,
				     BitsTest(cls.st, page) ? 1u : 0u, BitsTest(cls.pa, page) ? 1u : 0u, BitsTest(cls.ba, page) ? 1u : 0u,
				     (f & f_pk) != 0 ? 1u : 0u, static_cast<unsigned>(perms[i]), static_cast<unsigned>(prot[i]),
				     dk ? 1u : 0u);
			}
		}
		if (any_sk) {
			FS::Add(FS::Counter::AcClsN, 1);
			FS::Add(FS::Counter::AcClsVq, queries);
		}
		if (t0 != 0) {
			FS::Add(FS::Counter::AcClsNs, FS::NowNs() - t0);
		}
		if (lw_on) {
			LwOverflowLog();
		}
	}

	// Value 3 (s.7.5, ROADMAP s122 item 101(g)): a GuestGpu flush of [first, last) of one region in the order take -> check
	// -> apply - one hold: the first pending run taken, the detector over the flush range, its host call, the rest as
	// FlushRegion applies it.
	void AcFlushChecked(Region& region, uint64_t base_addr, size_t first, size_t last) {
		namespace FS = Common::FrameStats;
		t_protect_masked = false; // F4 (codereview129, ROADMAP s122 item 103(b)), as FlushRegion
		ApplyGuard                  apply(region.apply, true, FS::Counter::ApplyWaitRangeNs);
		size_t                      run_first = 0;
		size_t                      run_pages = 0;
		Common::VirtualMemory::Mode perms     = Common::VirtualMemory::Mode::ReadWrite;
		bool                        took      = false;
		{
			SpinGuard lock(region.lock);
			took = TakePendingRun(region, first, last, WorkerCallPages(), false, &run_first, &run_pages, &perms);
		}
		PageBits range {};
		BitsSet(range, first, last);
		const auto t0  = FS::Enabled() ? FS::NowNs() : 0;
		AcSnap     snap {};
		uint64_t   chk = 0;
		uint64_t   bad = 0;
		AcDetect(region, base_addr, range, false, 3, snap, &chk, &bad);
		if (t0 != 0) {
			FS::Add(FS::Counter::AcGchkNs, FS::NowNs() - t0);
		}
		FS::Add(FS::Counter::AcGchk, chk);
		FS::Add(FS::Counter::AcGbad, bad);
		if (took) {
			AcApplyTaken(region, base_addr, run_first, run_pages, perms, Arm::Range);
		}
		AcApplyRuns(region, base_addr, first, last, Arm::Range, nullptr, nullptr);
	}

	// A GuestGpu flush of a byte range at 1..3: FlushRange (the range flush of 0), or at 3 take -> check -> apply.
	void AcFlushRange(uint64_t vaddr, uint64_t size, bool checked) {
		if (!checked) {
			FlushRange(vaddr, size);
			return;
		}
		ValidateRange(vaddr, size);
		const auto begin = Common::AlignDown(vaddr, PAGE_SIZE);
		const auto end   = Common::AlignUp(vaddr + size, PAGE_SIZE);
		for (auto chunk_begin = begin; chunk_begin < end;) {
			const auto chunk_end   = std::min(end, Common::AlignUp(chunk_begin + 1, REGION_SIZE));
			const auto region_base = Common::AlignDown(chunk_begin, REGION_SIZE);
			if (auto* region = FindRegion(chunk_begin); region != nullptr) {
				AcFlushChecked(*region, region_base, static_cast<size_t>((chunk_begin - region_base) / PAGE_SIZE),
				               static_cast<size_t>((chunk_end - region_base) / PAGE_SIZE));
			}
			chunk_begin = chunk_end;
		}
	}

	// The GuestGpu flush of one window slice [first, last) at 1..3 (the rest of the windows, the temporary buffer).
	void AcFlushWindow(Region& region, uint64_t base_addr, size_t first, size_t last, uint32_t mode) {
		if (mode == 3) {
			AcFlushChecked(region, base_addr, first, last);
		} else {
			FlushRegion(region, base_addr, first, last, Common::FrameStats::Counter::ApplyWaitRangeNs);
		}
	}

	AcArea& AcAreaOf(AcOp& op, Region* region, uint64_t base_addr) {
		for (auto& area: op.areas) {
			if (area.region == region) {
				return area;
			}
		}
		op.areas.push_back({region, base_addr, {}, {}, {}});
		return op.areas.back();
	}

	// ArmCopyFinish: right after upload_func, GuestGpu thread, no lock held (read-only: every RegionManager::lock was
	// released before upload_func). Never waits for the pool or the GPU.
	void AcFinish() {
		namespace FS = Common::FrameStats;
		auto&      op   = t_ac_op;
		const auto mode = op.mode;
		// Session 130, knob "acinline" (I11, RC2): a batched copy never enqueued is already in `pooled` and would drop out of
		// the rest of the windows and of G_own - stop loudly, never clear.
		if (op.ai_pending != 0) {
			Fatal("acinline: inline batch not enqueued at ArmCopyFinish (pending=%u)", static_cast<unsigned>(op.ai_pending));
		}
		if (mode >= 1 && mode <= 3) {
			op.areas.clear();
			for (uint32_t index = 0; index < op.window_count; index++) {
				const auto& window = op.windows[index];
				BitsSet(AcAreaOf(op, window.region, window.base).win, window.first, window.last);
			}
			for (const auto& copy: op.copies) {
				if (!GuestRange {copy.vaddr, copy.size}.Valid()) {
					continue;
				}
				const auto begin = Common::AlignDown(copy.vaddr, PAGE_SIZE);
				const auto end   = Common::AlignUp(copy.vaddr + copy.size, PAGE_SIZE);
				for (auto chunk_begin = begin; chunk_begin < end;) {
					const auto chunk_end   = std::min(end, Common::AlignUp(chunk_begin + 1, REGION_SIZE));
					const auto region_base = Common::AlignDown(chunk_begin, REGION_SIZE);
					if (auto* region = FindRegion(chunk_begin); region != nullptr) {
						auto& area = AcAreaOf(op, region, region_base);
						BitsSet(copy.pooled ? area.pooled : area.own,
						        static_cast<size_t>((chunk_begin - region_base) / PAGE_SIZE),
						        static_cast<size_t>((chunk_end - region_base) / PAGE_SIZE));
					}
					chunk_begin = chunk_end;
				}
			}
			// 1. The rest of the windows (s.2.2, RC7): window pages outside every copy - the pooled ones are armed by their
			//    chunks, the inline ones were armed before their copy.
			if (!op.windows_flushed) {
				AcReasonScope reason(PageManager::ArmCopyReason::Gap);
				for (auto& area: op.areas) {
					PageBits gap {};
					for (size_t word = 0; word < gap.size(); word++) {
						gap[word] = area.win[word] & ~area.pooled[word] & ~area.own[word];
					}
					BitsRuns(gap, [&](size_t first, size_t last) { AcFlushWindow(*area.region, area.base, first, last, mode); });
				}
			}
			// 2. ac_orphan (RC7, B12): windows handed over with no copy - applied by step 1 all the same.
			if (op.copies.empty()) {
				bool any = false;
				for (uint32_t index = 0; index < op.window_count; index++) {
					any = any || op.windows[index].first < op.windows[index].last;
				}
				if (any) {
					FS::Add(FS::Counter::AcOrphan, 1);
				}
			}
			// 3. At 2/3 the GuestGpu-branch detector (s.7.5): the last action of the operation, per region of G, in its
			//    own apply hold. G = windows | every copy; G_own = (windows - pooled) | own copies.
			if (mode >= 2) {
				for (auto& area: op.areas) {
					PageBits g {};
					PageBits g_own {};
					for (size_t word = 0; word < g.size(); word++) {
						g[word]     = area.win[word] | area.pooled[word] | area.own[word];
						g_own[word] = (area.win[word] & ~area.pooled[word]) | area.own[word];
					}
					ApplyGuard apply(area.region->apply, true, FS::Counter::ApplyWaitRangeNs);
					const auto t0  = FS::Enabled() ? FS::NowNs() : 0;
					AcSnap     snap {};
					uint64_t   chk = 0;
					uint64_t   bad = 0;
					AcDetect(*area.region, area.base, g, false, mode, snap, &chk, &bad);
					if (t0 != 0) {
						FS::Add(FS::Counter::AcGchkNs, FS::NowNs() - t0);
					}
					FS::Add(FS::Counter::AcGchk, chk);
					FS::Add(FS::Counter::AcGbad, bad);
					PageBits left {};
					for (size_t word = 0; word < left.size(); word++) {
						left[word] = g_own[word] & snap.pend[word];
					}
					const auto gjleft = BitsCount(left);
					FS::Add(FS::Counter::AcGjleft, gjleft);
					if (mode == 2 && gjleft != 0) {
						AcLogLeft(left, snap, nullptr, nullptr, area.base, false, mode);
					}
				}
			}
		}
		// Session 130, knob "acinline" (I11, RC1): the GuestGpu wall of the operation, latch to here, in both values.
		if (mode >= 1 && mode <= 3 && t_ai_op_t0 != 0) {
			FS::Add(FS::Counter::AiOpNs, FS::NowNs() - t_ai_op_t0);
			FS::Add(FS::Counter::AiOpN, 1);
			t_ai_op_t0 = 0;
		}
		op.mode            = 0;
		op.window_count    = 0;
		op.windows_flushed = false;
		op.copies.clear();
		op.areas.clear();
		op.ai_inline = false;
	}

	// Gate "pbcheck". Holds the apply lock (no application in flight) and skips pending pages,
	// whose host protection may lag by design; any other difference breaks Region::apply (P).
	// Pages that were never watched keep the protection of their mapping: an expected ReadWrite
	// that reads back otherwise is counted apart (pb_bad_rw) and may be such a page.
	void Verify(uint64_t vaddr, uint64_t size) {
		if (!GuestRange {vaddr, size}.Valid()) {
			return;
		}
		const auto begin = Common::AlignDown(vaddr, PAGE_SIZE);
		const auto last  = Common::AlignDown(vaddr + size - 1, PAGE_SIZE);
		// A moving sample rather than the two ends of the range: a buffer covers hundreds of
		// pages and the interesting ones are in the middle.
		static std::atomic<uint64_t>  probe_seq {0};
		const auto                    page_count = (last - begin) / PAGE_SIZE + 1;
		const auto                    middle =
		    begin + (probe_seq.fetch_add(1, std::memory_order_relaxed) % page_count) * PAGE_SIZE;
		const std::array<uint64_t, 3> probes {begin, middle, last};
		for (size_t probe = 0; probe < probes.size(); probe++) {
			const auto page = probes[probe];
			if (probe != 0 && page == probes[probe - 1]) {
				continue;
			}
			auto* region = FindRegion(page);
			if (region == nullptr) {
				continue;
			}
			const auto page_index = static_cast<size_t>((page % REGION_SIZE) / PAGE_SIZE);
			ApplyGuard apply(region->apply, true);
			auto       expected = Common::VirtualMemory::Mode::ReadWrite;
			bool       unarmed  = false; // knob "protceil"
			{
				SpinGuard lock(region->lock);
				if (region->has_pending && IsPending(*region, page_index)) {
					continue;
				}
				expected = region->pages[page_index].Perms();
				unarmed  = region->has_unarmed && ((region->unarmed[page_index / 64] >> (page_index % 64)) & 1u) != 0;
			}
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
			MEMORY_BASIC_INFORMATION info {};
			if (VirtualQuery(reinterpret_cast<LPCVOID>(page), &info, sizeof(info)) == 0 ||
				info.State != MEM_COMMIT) {
				continue;
			}
			const auto protect  = static_cast<uint32_t>(info.Protect & 0xffu);
			const bool writable = protect == PAGE_READWRITE || protect == PAGE_WRITECOPY ||
								  protect == PAGE_EXECUTE_READWRITE ||
								  protect == PAGE_EXECUTE_WRITECOPY;
			const bool readable = writable || protect == PAGE_READONLY || protect == PAGE_EXECUTE_READ;
			Common::FrameStats::Add(Common::FrameStats::Counter::BatchChecks, 1);
			if (unarmed) [[unlikely]] {
				// Session 128, knob "protceil" (s.5.4, item 89(d)): a U page is writable or read-only on the host (P');
				// pb_bad and pb_bad_rw keep their meaning for the pages without U.
				if (writable) {
					Common::FrameStats::Add(Common::FrameStats::Counter::PcVfyU, 1);
				} else if (readable) {
					Common::FrameStats::Add(Common::FrameStats::Counter::PcVfyURo, 1);
				} else {
					Common::FrameStats::Add(Common::FrameStats::Counter::PcVfyUNa, 1);
					static std::atomic<uint32_t> logged_u {0};
					if (logged_u.fetch_add(1, std::memory_order_relaxed) < 32) {
						std::fprintf(stderr, "PbCheck: MISMATCH addr=0x%016llx expected=%u protect=0x%x unarmed=1\n",
									 static_cast<unsigned long long>(page), static_cast<unsigned>(expected),
									 static_cast<unsigned>(protect));
						std::fflush(stderr);
					}
				}
				continue;
			}
			bool lost_write = false;
			bool other      = false;
			switch (expected) {
				case Common::VirtualMemory::Mode::Read:
					lost_write = writable;
					other      = !readable;
					break;
				case Common::VirtualMemory::Mode::NoAccess:
					lost_write = writable;
					other      = readable && !writable;
					break;
				default: other = !writable; break;
			}
			if (lost_write) {
				Common::FrameStats::Add(Common::FrameStats::Counter::BatchCheckBad, 1);
			}
			if (other) {
				Common::FrameStats::Add(Common::FrameStats::Counter::BatchCheckBadRw, 1);
			}
			if (lost_write || other) {
				static std::atomic<uint32_t> logged {0};
				if (logged.fetch_add(1, std::memory_order_relaxed) < 32) {
					std::fprintf(stderr, "PbCheck: MISMATCH addr=0x%016llx expected=%u protect=0x%x tid=%lu\n",
								 static_cast<unsigned long long>(page),
								 static_cast<unsigned>(expected), static_cast<unsigned>(protect),
								 static_cast<unsigned long>(GetCurrentThreadId()));
					std::fflush(stderr);
				}
			}
#endif
		}
	}

	void WorkerThread() {
		t_protect_worker = true;
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
		SetThreadDescription(GetCurrentThread(), L"KytyPageProtect");
#endif
		for (;;) {
			QueuedRegion item {};
			{
				std::unique_lock lock(queue_mutex);
				queue_cv.wait(lock, [this] { return worker_stop || !queue.empty(); });
				if (queue.empty()) {
					return;
				}
				item = queue.front();
				queue.pop_front();
			}
			ApplyPending(*item.region, item.base_addr);
			if (inflight.fetch_sub(1, std::memory_order_acq_rel) == 1) {
				std::lock_guard lock(queue_mutex);
				Common::DiagB32::NoteSignal(&drain_cv); // Track F, F20j3
				drain_cv.notify_all();
			}
		}
	}

	void Drain() {
		if (inflight.load(std::memory_order_acquire) == 0) {
			return;
		}
		namespace FS = Common::FrameStats;
		const auto t0 = FS::Enabled() ? FS::NowNs() : 0;
		{
			std::unique_lock lock(queue_mutex);
			// Track F, F20j3 (KYTY_DIAG_B32 W:pm_drain, item 574(g)(1)): the caller waits for the protect workers.
			Common::DiagB32::Mark b32;
			if (Common::DiagB32::g_on) [[unlikely]] {
				b32.BeginWReg(Common::DiagB32::Wait::PmDrain, this, 0, 0);
			}
			drain_cv.wait(lock, [this] { return inflight.load(std::memory_order_acquire) == 0; });
			b32.EndSig(&drain_cv);
		}
		if (t0 != 0) {
			FS::Add(FS::Counter::ProtectDrainNs, FS::NowNs() - t0);
			FS::Add(FS::Counter::ProtectDrains, 1);
		}
	}

	void StopWorker() {
		{
			std::lock_guard lock(queue_mutex);
			if (!worker_started) {
				return;
			}
			worker_stop = true;
		}
		queue_cv.notify_all();
		worker.join();
	}

	// Worker calls are capped (KYTY_ASYNC_PROTECT_KB, default 256 KB) so that a synchronous caller
	// queued behind one in the kernel waits tens of microseconds, not the whole region: on a scene
	// cut the GuestGpu thread still issues ~500 buffer-cache protections while the worker runs.
	// Measured on the crowd cut: 4 MB calls starve them (15 ms), 64 KB calls make the worker 3x
	// slower (72 ms, flip drains appear) and the sync share worse (11 ms); 256 KB: 19-23 / 5-8 ms.
	static size_t WorkerCallPages() {
		static const size_t pages = [] {
			const char* value = std::getenv("KYTY_ASYNC_PROTECT_KB");
			const auto  kb    = value != nullptr ? std::strtoull(value, nullptr, 10) : uint64_t {256};
			return static_cast<size_t>(std::max<uint64_t>(kb * 1024u / PAGE_SIZE, 1u));
		}();
		return pages;
	}

	static thread_local bool t_protect_worker;
	std::atomic<uint32_t>    sync_waiters {0};
	static thread_local bool t_protect_masked;
	// The open BatchScope of this thread (gate "protbatch"), innermost first.
	static thread_local PageManager::BatchScope* t_batch;
	// The open PassScope of this thread (gate "protbatch2"), innermost first.
	static thread_local PageManager::PassScope* t_pass;
	// Session 128, knob "protceil": the latch of this thread's innermost CeilScope (Ceil*), and whether the thread is
	// inside the re-arm pass (its applications clear U as pc_rearm_decl; a CeilScope opened in it latches 0).
	static thread_local uint8_t t_ceil_state;
	static thread_local bool    t_ceil_rearm;
	// Session 129, knob "armcopy": the latch of this thread's innermost ArmCopyScope (Ac*) and its value, the reason of the
	// GuestGpu flush in progress (ac_kept_*), and the operation between ArmCopyBegin and ArmCopyFinish.
	static thread_local uint8_t                    t_ac_state;
	static thread_local uint8_t                    t_ac_mode;
	static thread_local PageManager::ArmCopyReason t_ac_reason;
	static thread_local AcOp                       t_ac_op;
	// Session 130, ac_cbad attribution (cbad130.md rev 2 s.4 C3): the snapshot S_a of the chunk this thread copies.
	static thread_local AcCls                      t_ac_cls;
	// Session 130, knob "acinline": the flag latched by this thread's outer ArmCopyScope (0/1), the start of the wall of its
	// operation (ai_op_ns, 0 = not measuring), and whether this thread runs an inline-class chunk right now (I6).
	static thread_local uint8_t  t_ai_state;
	static thread_local uint64_t t_ai_op_t0;
	static thread_local bool     t_ai_chunk;
	// The regions holding U bits with their base, in the order they got the first; written and read only on the
	// GuestGpu thread (SkipRun under a latch of 1, CeilRearm).
	std::vector<std::pair<Region*, uint64_t>> unarmed_regions;

	std::unique_ptr<std::atomic<Region*>[]> regions;
	std::vector<std::unique_ptr<Region>>    region_storage;
	Common::DiagB32::TrackedMutex<std::mutex>                              region_mutex; // Track F, F20j3 (KYTY_DIAG_B32 W:emu_mutex, ROADMAP s122 item 574(g)(1))

	std::mutex               queue_mutex;
	std::condition_variable  queue_cv;
	std::condition_variable  drain_cv;
	std::deque<QueuedRegion> queue;
	std::atomic<uint32_t>    inflight {0}; // queued + being applied
	std::thread              worker;
	bool                     worker_started = false;
	bool                     worker_stop    = false;
};

thread_local bool PageManager::Impl::t_protect_worker = false;
thread_local bool PageManager::Impl::t_protect_masked = false;
thread_local PageManager::BatchScope* PageManager::Impl::t_batch = nullptr;
thread_local PageManager::PassScope*  PageManager::Impl::t_pass  = nullptr;
thread_local uint8_t                  PageManager::Impl::t_ceil_state = PageManager::Impl::CeilOutside;
thread_local bool                     PageManager::Impl::t_ceil_rearm = false;
thread_local uint8_t                    PageManager::Impl::t_ac_state  = PageManager::Impl::AcOutside;
thread_local uint8_t                    PageManager::Impl::t_ac_mode   = 0;
thread_local PageManager::ArmCopyReason PageManager::Impl::t_ac_reason = PageManager::ArmCopyReason::Full;
thread_local PageManager::Impl::AcOp    PageManager::Impl::t_ac_op {};
thread_local PageManager::Impl::AcCls   PageManager::Impl::t_ac_cls {};
thread_local uint8_t                    PageManager::Impl::t_ai_state = 0;
thread_local uint64_t                   PageManager::Impl::t_ai_op_t0 = 0;
thread_local bool                       PageManager::Impl::t_ai_chunk = false;

static_assert(std::atomic<void*>::is_always_lock_free);

PageManager::PageManager(): m_impl(std::make_unique<Impl>()) {}

PageManager::~PageManager() = default;

uint64_t PageManager::GetPageSize() const {
	return PAGE_SIZE;
}

template <bool track>
void PageManager::UpdatePageWatchers(uint64_t vaddr, uint64_t size) {
	Common::DrawStat::Mark(Common::DrawStat::Prot);
	m_impl->UpdatePageWatchers<track, false>(vaddr, size);
}

template void PageManager::UpdatePageWatchers<true>(uint64_t, uint64_t);
template void PageManager::UpdatePageWatchers<false>(uint64_t, uint64_t);

void PageManager::UpdatePageWatchersDeferred(uint64_t vaddr, uint64_t size) {
	Common::DrawStat::Mark(Common::DrawStat::Prot);
	m_impl->UpdatePageWatchers<true, false>(vaddr, size, Impl::DeferEnabled());
}

void PageManager::DrainDeferredProtection() {
	m_impl->Drain();
}

bool PageManager::DeferEnabled() {
	return Impl::DeferEnabled();
}

void PageManager::UpdatePageWatchersForRegionDeferred(uint64_t base_addr, RegionBits& mask) {
	Common::DrawStat::Mark(Common::DrawStat::Prot);
	if (base_addr % REGION_SIZE != 0 || base_addr >= ADDRESS_SIZE ||
	    REGION_SIZE > ADDRESS_SIZE - base_addr) {
		Fatal("invalid tracking region base 0x%016" PRIx64, base_addr);
	}
	const auto start_range = mask.FirstRange();
	const auto end_range   = mask.LastRange();
	if (start_range.first == REGION_PAGES) {
		FailFast("empty region watcher mask");
	}
	const auto first = start_range.first;
	const auto last  = end_range.second;
	const bool defer = Impl::DeferEnabled();
	if (start_range.second == end_range.second) {
		m_impl->UpdatePageWatchers<true, false>(base_addr + first * PAGE_SIZE,
		                                        (last - first) * PAGE_SIZE, defer);
		return;
	}
	auto* region = m_impl->GetOrCreateRegion(base_addr);
	m_impl->UpdateRegionWatchers<true, false, true>(*region, base_addr, first, last, &mask, defer);
}

void PageManager::KeepApplied(uint64_t base_addr, RegionBits& mask) {
	auto* region = m_impl->FindRegion(base_addr);
	if (region == nullptr) {
		mask.Clear(); // never watched: protected as mapped, i.e. writable
		return;
	}
	// Bits first, the run in flight second (FlushBlocker): a bit seen clear was cleared by a run
	// still visible below or by one whose host call has returned.
	const RegionBits requested = mask;
	for (const auto [first, last]: requested) {
		for (size_t page = first; page < last; page++) {
			const auto word =
			    std::atomic_ref<uint64_t>(region->pending[page / 64]).load(std::memory_order_acquire);
			if (((word >> (page % 64)) & 1u) != 0) {
				mask.Unset(page);
			}
		}
	}
	const auto run       = region->applying_run.load(std::memory_order_acquire);
	const auto run_first = static_cast<size_t>(run & 0xffffu);
	const auto run_last  = static_cast<size_t>((run >> 16u) & 0xffffu);
	for (size_t page = run_first; page < run_last && page < REGION_PAGES; page++) {
		mask.Unset(page);
	}
}

bool PageManager::IsHostWritable(uint64_t vaddr) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	MEMORY_BASIC_INFORMATION info {};
	if (VirtualQuery(reinterpret_cast<LPCVOID>(vaddr), &info, sizeof(info)) == 0 ||
	    info.State != MEM_COMMIT) {
		return false;
	}
	const auto protect = static_cast<uint32_t>(info.Protect & 0xffu);
	return protect == PAGE_READWRITE || protect == PAGE_WRITECOPY ||
	       protect == PAGE_EXECUTE_READWRITE || protect == PAGE_EXECUTE_WRITECOPY;
#else
	(void)vaddr;
	return false;
#endif
}

PageManager::BatchScope::BatchScope(PageManager& manager, bool enabled) noexcept
	: m_manager(manager), m_enabled(enabled) {
	if (m_enabled) {
		m_previous    = Impl::t_batch;
		Impl::t_batch = this;
	}
}

PageManager::BatchScope::~BatchScope() {
	if (m_enabled) {
		Flush();
		Impl::t_batch = m_previous;
	}
}

void PageManager::BatchScope::Flush() noexcept {
	const auto count = m_count;
	m_count          = 0;
	for (uint32_t index = 0; index < count; index++) {
		const auto slot = m_slots[index];
		if (slot.first >= slot.last) {
			continue; // the scope deferred nothing into this region
		}
		Common::FrameStats::Add(Common::FrameStats::Counter::BatchFlushes, 1);
		if (m_manager.m_impl->FlushRegion(*static_cast<Impl::Region*>(slot.region), slot.base,
										  slot.first, slot.last,
										  Common::FrameStats::Counter::ApplyWaitScopeNs) == 0) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BatchMerged, 1);
		}
	}
}

void PageManager::BatchScope::Handover() noexcept {
	auto& op = Impl::t_ac_op;
	for (uint32_t index = 0; index < m_count; index++) {
		const auto& slot = m_slots[index];
		if (slot.first >= slot.last || op.window_count == Capacity) {
			continue; // the scope deferred nothing into this region (a window count above Capacity cannot happen)
		}
		op.windows[op.window_count++] = {static_cast<Impl::Region*>(slot.region), slot.base, slot.first, slot.last};
	}
	m_count = 0;
}

PageManager::PassScope::PassScope(PageManager& manager, bool owns_flush) noexcept
	: m_manager(manager), m_owns_flush(owns_flush) {
	m_previous     = Impl::t_pass;
	Impl::t_pass   = this;
}

PageManager::PassScope::~PassScope() {
	if (m_owns_flush) {
		Flush(); // a pass that already flushed leaves nothing here; a path that forgot is covered
	}
	Impl::t_pass = m_previous;
}

void PageManager::PassScope::Note(uint64_t vaddr, uint64_t size) {
	if (!m_owns_flush && !Common::FrameStats::Enabled()) {
		// With the gate off this scope flushes nothing, and the only thing left to do here is the
		// pb2_reg ceiling count: without the counters the pass must not pay for the walk at all.
		return;
	}
	if (!GuestRange {vaddr, size}.Valid()) {
		return;
	}
	auto       begin = Common::AlignDown(vaddr, PAGE_SIZE);
	const auto end   = Common::AlignUp(vaddr + size, PAGE_SIZE);
	while (begin < end) {
		const auto base  = Common::AlignDown(begin, REGION_SIZE);
		const auto chunk = std::min(end, base + REGION_SIZE);
		uint32_t   index = 0;
		for (; index < m_count; index++) {
			if (m_windows[index].base == base) {
				break;
			}
		}
		if (index == m_count) {
			Common::FrameStats::Add(Common::FrameStats::Counter::PassRegions, 1);
			if (m_count < Capacity) {
				m_windows[m_count++] = {base, begin, chunk};
				begin                = chunk;
				continue;
			}
			// Full. Nothing may be closed here, and nothing may be flushed here: Note runs BEFORE
			// the pages of its range are armed, so a window flushed now has nothing pending yet -
			// a protection another caller left deferred on those pages (the texture cache arms its
			// watchers through the protection worker) would stay unapplied, the pages would stay
			// writable on the host with their CPU-dirty bits already taken, and a guest write into
			// them would be lost. One range can cover more regions than Capacity by itself, so
			// dropping a window is not a corner case. A window may span several regions instead -
			// FlushProtection walks every region of its range - so the chunk joins the window that
			// has to stretch the least for it and Flush() keeps covering everything that was noted.
			uint32_t best = 0;
			uint64_t cost = UINT64_MAX;
			for (uint32_t i = 0; i < m_count; i++) {
				const auto added = (std::max(m_windows[i].end, chunk) -
				                    std::min(m_windows[i].begin, begin)) -
				                   (m_windows[i].end - m_windows[i].begin);
				if (added < cost) {
					cost = added;
					best = i;
				}
			}
			index = best;
		}
		m_windows[index].begin = std::min(m_windows[index].begin, begin);
		m_windows[index].end   = std::max(m_windows[index].end, chunk);
		begin                  = chunk;
	}
}

void PageManager::PassScope::Flush() {
	const auto count = m_count;
	m_count          = 0;
	for (uint32_t index = 0; index < count; index++) {
		const auto& window = m_windows[index];
		m_manager.FlushProtection(window.begin, window.end - window.begin);
	}
}

void PageManager::PassScope::NoteProtect(uint64_t vaddr, uint64_t size, uint32_t mode) noexcept {
	namespace FS = Common::FrameStats;
	FS::Add(FS::Counter::PassProtectCalls, 1);
	FS::Add(FS::Counter::PassProtectPages, size / PAGE_SIZE);
	const auto base = Common::AlignDown(vaddr, REGION_SIZE);
	if (m_last_seen && m_last_base == base && m_last_mode == mode) {
		// Phase 2 applies one merged run per region per pass: a call continuing the previous one
		// disappears into it, and one with a gap in between disappears as well once the run may
		// swallow the pages there (they carry that protection already).
		FS::Add(vaddr == m_last_end ? FS::Counter::PassProtectAdjacent : FS::Counter::PassProtectNear,
		        1);
	}
	m_last_seen = true;
	m_last_base = base;
	m_last_end  = vaddr + size;
	m_last_mode = mode;
}

PageManager::CeilScope::CeilScope(bool engage) noexcept {
	namespace FS = Common::FrameStats;
	namespace G  = Common::Gates;
	if (!engage) {
		if (FS::Enabled() && G::Value(G::Knob::ProtCeiling) != 0) {
			FS::Add(FS::Counter::PcOffThr, 1);
		}
		return;
	}
	m_engaged  = true;
	m_previous = Impl::t_ceil_state;
	if (m_previous != Impl::CeilOutside) {
		return; // nested: the latch of the outer synchronization
	}
	// The only read of the knob for this synchronization; the refusals are read only at 1 (s.4.3).
	const auto value = Impl::t_ceil_rearm ? 0u : G::Value(G::Knob::ProtCeiling);
	auto       state = Impl::CeilZero;
	if (value == 1) {
		static std::atomic<uint32_t> logged {0};
		const char*                  reason = nullptr;
		uint32_t                     bit    = 0;
		if (G::Enabled(G::Gate::ArmDefer)) {
			reason = "armdefer";
			bit    = 1;
		} else if (G::Enabled(G::Gate::ProtectBatchPass) && G::Enabled(G::Gate::ProtectBatch)) {
			reason = "protbatch2";
			bit    = 2;
		}
		if (reason != nullptr) {
			state = Impl::CeilRefused;
			FS::Add(FS::Counter::PcRefuse, 1);
		} else {
			state = Impl::CeilSkip;
		}
		if ((logged.fetch_or(1u << bit, std::memory_order_relaxed) & (1u << bit)) == 0) {
			if (reason != nullptr) {
				LOGF("ProtCeil: refused reason=%s\n", reason);
			} else {
				LOGF("ProtCeil: mode 1\n");
			}
		}
	} else if (value == 2) {
		// Value 2, the dose (ROADMAP s122 item 93(g)(1)): the path of 0, and each eligible GuestGpu call spins once more
		// for its duration by the clock of Protect - which runs only under Enabled(); without it the value is refused.
		static std::atomic<uint32_t> logged {0};
		const bool                   clock = FS::Enabled();
		const uint32_t               bit   = clock ? 1u : 2u;
		if (clock) {
			state = Impl::CeilDose;
		} else {
			state = Impl::CeilRefused;
			FS::Add(FS::Counter::PcRefuse, 1);
		}
		if ((logged.fetch_or(bit, std::memory_order_relaxed) & bit) == 0) {
			if (clock) {
				LOGF("ProtCeil: mode 2\n");
			} else {
				LOGF("ProtCeil: refused reason=noclock\n");
			}
		}
	}
	FS::Add(state == Impl::CeilSkip ? FS::Counter::PcOp1 : FS::Counter::PcOp0, 1);
	Impl::t_ceil_state = state;
}

PageManager::CeilScope::~CeilScope() {
	if (m_engaged) {
		Impl::t_ceil_state = m_previous;
	}
}

PageManager::ArmCopyScope::ArmCopyScope(bool engage, bool is_written) noexcept {
	namespace FS = Common::FrameStats;
	namespace G  = Common::Gates;
	if (!engage) {
		if (FS::Enabled() && G::Value(G::Knob::ArmInCopy) != 0) {
			FS::Add(FS::Counter::AcOffThr, 1);
		}
		return;
	}
	m_engaged        = true;
	m_previous_state = Impl::t_ac_state;
	m_previous_mode  = Impl::t_ac_mode;
	m_previous_ai    = Impl::t_ai_state;
	if (m_previous_state != Impl::AcOutside) {
		return; // nested: the latch of the outer synchronization (acinline is neither read nor touched - I1')
	}
	// The only read of the knob for this synchronization; the refusals are read only at >= 1 (s.8.2).
	const auto value = std::min<uint32_t>(G::Value(G::Knob::ArmInCopy), 4);
	auto       state = Impl::AcZero;
	if (value == 0) {
		FS::Add(FS::Counter::AcOp0, 1);
	} else {
		static std::atomic<uint32_t> logged {0};
		uint32_t                     bit    = value;
		const char*                  reason = Impl::AcRefusal(value, &bit);
		if (reason != nullptr) {
			state = Impl::AcRefused;
			FS::Add(FS::Counter::AcRefuse, 1);
		} else if (is_written) {
			state = value == 4 ? Impl::AcWrittenNull : Impl::AcWritten;
		} else {
			state = value == 4 ? Impl::AcNull : Impl::AcMove;
			FS::Add(FS::Counter::AcN, 1);
		}
		if ((logged.fetch_or(1u << bit, std::memory_order_relaxed) & (1u << bit)) == 0) {
			if (reason != nullptr) {
				LOGF("ArmCopy: refused reason=%s\n", reason);
			} else {
				LOGF("ArmCopy: mode %u\n", static_cast<unsigned>(value));
			}
		}
	}
	// Session 130, knob "acinline" (I1, I1'): read once, only when armcopy was read >= 1 (at 0 never - item 107(g)).
	if (value != 0) {
		const auto inl = std::min<uint32_t>(G::Value(G::Knob::ArmInline), 1);
		if (state == Impl::AcMove) {
			if (inl == 1) {
				Impl::t_ai_state = 1;
				FS::Add(FS::Counter::AiN, 1);
				static std::atomic<bool> logged_ai {false};
				if (!logged_ai.exchange(true, std::memory_order_relaxed)) {
					LOGF("ArmInline: mode 1\n");
				}
			}
			// The wall of the operation (ai_op_ns, RC1), in both values: from here to the end of AcFinish.
			Impl::t_ai_op_t0 = FS::Enabled() ? FS::NowNs() : 0;
		} else if (inl == 1) {
			FS::Add(FS::Counter::AiIdle, 1); // armcopy 4, a refusal or a written synchronization
		}
	}
	// Session 131, knob "lwin" (lw131.md rev 1 L2 with ROADMAP s122 items 126(v), 127(v)): read once, only when armcopy was
	// read 2..4 and latched read-only (AcMove / AcNull) - never at 0/1, a refusal or a written synchronization. The latch of
	// this operation (t_ac_lw) and of the process (g_lw, read by the chunks and their checks).
	if (value >= 2 && (state == Impl::AcMove || state == Impl::AcNull)) {
		const auto lw = std::min<uint32_t>(G::Value(G::Knob::LossWin), 3);
		t_ac_lw       = lw;
		g_lw.store(lw, std::memory_order_relaxed);
		if (lw != 0) {
			static std::atomic<bool> logged_lw {false};
			if (!logged_lw.exchange(true, std::memory_order_relaxed)) {
				LOGF("LossWin: mode %u\n", static_cast<unsigned>(lw));
			}
		}
	}
	Impl::t_ac_state = state;
	Impl::t_ac_mode  = static_cast<uint8_t>(value);
}

PageManager::ArmCopyScope::~ArmCopyScope() {
	if (m_engaged) {
		if (m_previous_state == Impl::AcOutside) {
			Impl::t_ai_op_t0 = 0; // an operation that never reached AcFinish is not counted (I1')
		}
		Impl::t_ac_state = m_previous_state;
		Impl::t_ac_mode  = m_previous_mode;
		Impl::t_ai_state = m_previous_ai;
	}
}

uint32_t PageManager::ArmCopyBegin() noexcept {
	if (Impl::t_ac_op.mode != 0) {
		// F1 (codereview129, ROADMAP s122 item 103(b)): an operation is already open on this thread (a ForEachUploadRange of
		// another tracker inside upload_func). Overwriting it would drop the outer windows and turn the outer inline
		// armings off - a lost guest write; stop loudly instead.
		Fatal("armcopy: an operation is already open on this thread (mode=%u)", static_cast<unsigned>(Impl::t_ac_op.mode));
	}
	const auto state = Impl::t_ac_state;
	if (state != Impl::AcMove && state != Impl::AcNull) {
		return 0;
	}
	auto& op           = Impl::t_ac_op;
	op.mode            = Impl::t_ac_mode;
	op.window_count    = 0;
	op.windows_flushed = false;
	op.copies.clear();
	// Session 130, knob "acinline" (I1'', RC8): written with every mode (0 at 4), cleared by AcFinish.
	op.ai_inline  = state == Impl::AcMove && Impl::t_ai_state == 1;
	op.ai_pending = 0;
	return op.mode;
}

uint32_t PageManager::ArmCopyOpMode() noexcept {
	return Impl::t_ac_op.mode;
}

void PageManager::ArmCopyNoteCopy(uint64_t vaddr, uint64_t size, bool pooled) {
	auto& op = Impl::t_ac_op;
	if (op.mode >= 1 && op.mode <= 3) {
		op.copies.push_back({vaddr, size, pooled});
	}
}

void PageManager::ArmCopyFlush(uint64_t vaddr, uint64_t size, ArmCopyReason reason) {
	const auto mode = Impl::t_ac_op.mode;
	if (mode < 1 || mode > 3) {
		return;
	}
	Impl::AcReasonScope scope(reason);
	m_impl->AcFlushRange(vaddr, size, mode == 3);
}

void PageManager::ArmCopyFlushWindows() {
	auto&      op   = Impl::t_ac_op;
	const auto mode = op.mode;
	if (mode < 1 || mode > 3) {
		return;
	}
	Impl::AcReasonScope scope(ArmCopyReason::Tmp);
	for (uint32_t index = 0; index < op.window_count; index++) {
		const auto& window = op.windows[index];
		m_impl->AcFlushWindow(*window.region, window.base, window.first, window.last, mode);
	}
	op.windows_flushed = true;
}

void PageManager::ArmCopyFinish() {
	m_impl->AcFinish();
}

bool PageManager::ArmCopyChunk(void* context, uint64_t vaddr, size_t size, uint32_t mode, uint8_t* dst,
                               const uint8_t* src) {
	return static_cast<PageManager*>(context)->m_impl->AcChunk(vaddr, size, mode, dst, src);
}

void PageManager::ArmCopyClassify(uint64_t vaddr, uint64_t size, uint32_t mode, const uint64_t* pages, size_t n,
                                  ArmCopyDirtyFunc dirty, void* dirty_context, ArmCopyClassCounts* counts) {
	m_impl->AcClassify(vaddr, size, mode, pages, n, dirty, dirty_context, *counts);
}

void PageManager::ArmCopyClassDone() noexcept {
	auto& cls = Impl::t_ac_cls;
	cls.valid = false;
	// Session 131, knob "lwin" (L15): the chunk is no longer in flight; candidates left unresolved are dropped.
	if (cls.lw != 0) {
		if (cls.lw >= 2) {
			LwFlightLeave();
		}
		if (t_lw_cands != nullptr) {
			t_lw_cands->n = 0;
		}
		cls.lw = 0;
	}
}

uint32_t PageManager::ArmCopyLossWin() noexcept {
	return t_ac_lw;
}

void PageManager::LwOpBegin(uint32_t arm_copy, uint32_t lw) noexcept {
	t_lw_op   = g_lw_op.fetch_add(1, std::memory_order_relaxed) & 0xfffffu;
	t_lw_code = static_cast<uint32_t>(LwModeCode(arm_copy));
	t_lw_val  = lw;
}

void PageManager::LwEnsureBlock(uint64_t region_base) noexcept {
	const auto index = region_base / TRACKER_REGION_SIZE;
	if (index >= LW_BLOCKS || g_lw_blocks[index].load(std::memory_order_acquire) != nullptr) {
		return;
	}
	auto* block = new (std::nothrow) LwBlock();
	if (block == nullptr) {
		LwOverflowNote(LwOvfBlock);
		LwOverflowLog();
		return;
	}
	LwBlock* expected = nullptr;
	if (!g_lw_blocks[index].compare_exchange_strong(expected, block, std::memory_order_acq_rel)) {
		delete block;
	}
}

uint64_t PageManager::LwClearBegin() noexcept {
	if (t_lw_code == 0) {
		return 0;
	}
	const auto c0 = LwTake();
	if (c0 >= LW_GEN_LIMIT) {
		LwOverflowNote(LwOvfGen);
		return 0;
	}
	return c0;
}

void PageManager::LwClearEnd(uint64_t region_base, const RegionBits& mask, uint64_t c0) noexcept {
	namespace FS = Common::FrameStats;
	auto* block = LwBlockOf(region_base);
	if (c0 == 0 || block == nullptr) {
		return;
	}
	// Item 127(a): the clear words (delta 255 - c1 not known yet) BEFORE c1, so a hold S_k whose g_h follows c1 sees them.
	const uint64_t tag = uint64_t {t_lw_code} << 20u | t_lw_op;
	const uint64_t w0  = c0 << 30u | LW_DELTA_NONE << 22u | tag;
	uint64_t       pages = 0;
	for (const auto [first, last]: mask) {
		for (size_t page = first; page < last; page++) {
			block->pages[page].clr.store(w0, std::memory_order_relaxed);
		}
		pages += last - first;
	}
	const auto c1     = LwTake();
	const auto clr_ns = FS::NowNs();
	const auto delta  = std::min<uint64_t>(c1 - c0, LW_DELTA_NONE);
	const auto w1     = c0 << 30u | delta << 22u | tag;
	for (const auto [first, last]: mask) {
		for (size_t page = first; page < last; page++) {
			auto& stamp = block->pages[page];
			stamp.clr_ns.store(clr_ns, std::memory_order_relaxed);
			stamp.clr.store(w1, std::memory_order_relaxed);
		}
	}
	FS::Add(FS::Counter::LwStampN, 1);
	FS::Add(FS::Counter::LwStampPages, pages);
	// The P8 / X control (lw131.md s.6.1 with items 126(v), 127(v)): at lwin 2 / 3 a pass whose cleared pages meet a chunk
	// in flight spins 1 / 6 ms here - after the bits and the words, before the marks - holding RegionManager::lock only.
	if (t_lw_val >= 2 && g_lw_flight_n.load(std::memory_order_relaxed) != 0) {
		const auto base_page = region_base / TRACKER_PAGE_SIZE;
		if (LwFlightMeets(base_page + mask.FirstRange().first, base_page + mask.LastRange().second)) {
			const auto length = t_lw_val == 2 ? LW_SPIN_NS : LW_SPIN_X_NS;
			const auto s0     = FS::NowNs();
			auto       s1     = s0;
			while (s0 != 0 && s1 - s0 < length) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
				YieldProcessor();
#else
				std::this_thread::yield();
#endif
				s1 = FS::NowNs();
			}
			FS::Add(FS::Counter::LwSpinN, 1);
			FS::Add(FS::Counter::LwSpinNs, s1 - s0);
		}
	}
}

void PageManager::LwAfterPass() noexcept {
	t_lw_code = 0;
	t_lw_val  = 0;
	LwLateFlush();
	LwOverflowLog();
}

void PageManager::ArmCopyLossResolve(ArmCopyClassCounts* counts) {
	namespace FS = Common::FrameStats;
	auto& out  = *counts;
	auto* list = t_lw_cands;
	out.lw_n   = 0;
	if (list == nullptr || list->n == 0) {
		LwOverflowLog();
		return;
	}
	const auto n       = list->n;
	size_t     waiting = 0;
	const auto waits   = [](uint8_t state) { return state == LwStWaitDelta || state == LwStWaitMark; };
	std::atomic_thread_fence(std::memory_order_acquire);
	for (size_t i = 0; i < n; i++) {
		auto& c = list->c[i];
		if (c.rel >= LW_GEN_LIMIT) {
			LwOverflowNote(LwOvfGen); // item 127(l)(1): loudly, never a wrapped comparison
			c.state = LwStNc;
			continue;
		}
		LwRead(c);
		c.state = LwDecide(c);
		waiting += waits(c.state) ? 1 : 0;
	}
	if (waiting != 0) {
		// The poll (lw131.md s.5.2 with items 126(a), 127(e)): no lock held; each candidate until rel_ns of its own hold +
		// T_poll. At the deadline a wait for the delta is LwStUnk (lw_xnc, item 130(b)(3)), a wait for the mark is lw_open.
		const auto t0 = FS::NowNs();
		FS::Add(FS::Counter::LwPollN, 1);
		while (waiting != 0) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
			YieldProcessor();
#else
			std::this_thread::yield();
#endif
			std::atomic_thread_fence(std::memory_order_acquire);
			const auto now = FS::NowNs();
			for (size_t i = 0; i < n; i++) {
				auto& c = list->c[i];
				if (!waits(c.state)) {
					continue;
				}
				if (now == 0 || now >= c.rel_ns + LW_T_POLL_NS) {
					c.state = c.state == LwStWaitDelta ? LwStUnk : LwStOpen;
				} else {
					LwRead(c);
					c.state = LwDecide(c);
				}
				waiting -= waits(c.state) ? 0 : 1;
			}
		}
		if (t0 != 0) {
			FS::Add(FS::Counter::LwPollNs, FS::NowNs() - t0);
		}
	}
	static std::atomic<uint32_t>                logged {0};
	static std::array<std::atomic<uint32_t>, 3> logged_ctl {};
	for (size_t i = 0; i < n; i++) {
		auto&      c  = list->c[i];
		const bool p8 = c.state == LwStP8 || c.state == LwStP8s;
		switch (c.kind) {
			case LwKindH:
				if (p8) {
					out.lw_p8++;
					out.lw_p8sync += c.state == LwStP8s ? 1 : 0;
				} else {
					out.lw_x++;
					out.lw_open += c.state == LwStOpen ? 1 : 0;
					out.lw_xnc += c.state == LwStNc || (c.state == LwStUnk && !c.a) ? 1 : 0; // item 130(b)(5)
					out.lw_xmk += c.state == LwStMk || (c.state == LwStUnk && c.a) ? 1 : 0;
				}
				break;
			case LwKindC3: (p8 ? out.lw_c3p : out.lw_c3x)++; break;
			case LwKindCr: (p8 ? out.lw_crp : out.lw_crx)++; break;
			default: (p8 ? out.lw_cdp : out.lw_cdx)++; break;
		}
		if (c.kind == LwKindH && c.state == LwStOpen && !LwOpenInsert(c.page, c.o3, c.mode, c.k_ns)) {
			LwOverflowNote(LwOvfOpen);
		}
		auto& slot = c.kind == LwKindH ? logged : logged_ctl[c.kind - LwKindC3];
		const auto limit = c.kind == LwKindH ? LW_LOSS_LINES : LW_CTL_LINES;
		if (slot.load(std::memory_order_relaxed) >= limit || slot.fetch_add(1, std::memory_order_relaxed) >= limit) {
			continue;
		}
		char clr_op[16]  = "-";
		char pend_op[16] = "-";
		char dt[32]      = "-";
		if (LwCode(c.clr) != 0) {
			std::snprintf(clr_op, sizeof(clr_op), "%u", static_cast<unsigned>(LwOp(c.clr)));
		}
		if (LwCode(c.pend) != 0) {
			std::snprintf(pend_op, sizeof(pend_op), "%u", static_cast<unsigned>(LwOp(c.pend)));
			std::snprintf(dt, sizeof(dt), "%lld", static_cast<long long>(c.pend_ns - c.k_ns));
		} else if (LwCode(c.clr) != 0) {
			std::snprintf(dt, sizeof(dt), "%lld", static_cast<long long>(c.clr_ns - c.k_ns));
		}
		if (c.kind == LwKindH) {
			static constexpr const char* reasons[] = {"-", "-", "-", "p8", "p8s", "nc", "mk", "open", "unk"};
			LOGF("ArmCopyLoss: page=0x%016llx mode=%u cls=%s clr_op=%s pend_op=%s dt_ns=%s xr=%s perms=%u\n",
			     static_cast<unsigned long long>(c.page), static_cast<unsigned>(c.mode), p8 ? "P8" : "X", clr_op, pend_op,
			     dt, reasons[c.state], static_cast<unsigned>(c.perms));
		} else {
			static constexpr const char* kinds[] = {"-", "-", "c3", "cr", "cd"};
			LOGF("ArmCopyLossCtl: page=0x%016llx mode=%u kind=%s cls=%s clr_op=%s pend_op=%s dt_ns=%s\n",
			     static_cast<unsigned long long>(c.page), static_cast<unsigned>(c.mode), kinds[c.kind], p8 ? "P8" : "X",
			     clr_op, pend_op, dt);
		}
	}
	list->n = 0;
	LwOverflowLog();
}

bool PageManager::ArmCopyInlineOn() noexcept {
	return Impl::t_ac_op.ai_inline;
}

bool PageManager::ArmCopyInlineWindow(uint64_t vaddr, uint64_t size) noexcept {
	const auto& op  = Impl::t_ac_op;
	const auto  end = vaddr + size;
	for (uint32_t index = 0; index < op.window_count; index++) {
		const auto& window = op.windows[index];
		const auto  first  = window.base + static_cast<uint64_t>(window.first) * PAGE_SIZE;
		const auto  last   = window.base + static_cast<uint64_t>(window.last) * PAGE_SIZE;
		if (vaddr < last && first < end) {
			return true;
		}
	}
	return false;
}

void PageManager::ArmCopyInlineNote(uint64_t vaddr, uint64_t size) noexcept {
	namespace FS = Common::FrameStats;
	Impl::t_ac_op.ai_pending++;
	FS::Add(FS::Counter::AiJobs, 1);
	FS::Add(FS::Counter::AiB, size);
	const auto pages = (Common::AlignUp(vaddr + size, PAGE_SIZE) - Common::AlignDown(vaddr, PAGE_SIZE)) / PAGE_SIZE;
	FS::Add(FS::Counter::AiPages, pages);
}

void PageManager::ArmCopyInlineEntry(size_t items) noexcept {
	if (items != 0 || Impl::t_ac_op.ai_pending != 0) {
		Fatal("acinline: inline batch not empty on entry (items=%zu pending=%u)", items,
		      static_cast<unsigned>(Impl::t_ac_op.ai_pending));
	}
}

void PageManager::ArmCopyInlineEnqueued(size_t n) noexcept {
	auto& op = Impl::t_ac_op;
	if (n != op.ai_pending) {
		Fatal("acinline: inline batch size mismatch (n=%zu pending=%u)", n, static_cast<unsigned>(op.ai_pending));
	}
	op.ai_pending = 0;
}

bool PageManager::ArmCopyChunkInline(void* context, uint64_t vaddr, size_t size, uint32_t mode, uint8_t* dst,
                                     const uint8_t* src) {
	Impl::t_ai_chunk = true;
	const bool copied = static_cast<PageManager*>(context)->m_impl->AcChunk(vaddr, size, mode, dst, src);
	Impl::t_ai_chunk = false;
	return copied;
}

bool PageManager::HasUnarmed() const noexcept {
	return !m_impl->unarmed_regions.empty();
}

void PageManager::CeilRearm(void* context, DeclareFunc declare) {
	m_impl->CeilRearm(context, declare);
}

void PageManager::FlushProtection(uint64_t vaddr, uint64_t size) {
	m_impl->FlushRange(vaddr, size);
}

void PageManager::VerifyProtection(uint64_t vaddr, uint64_t size) {
	m_impl->Verify(vaddr, size);
}

template <bool track, bool is_read, bool lw>
void PageManager::UpdatePageWatchersForRegion(uint64_t base_addr, RegionBits& mask) {
	Common::DrawStat::Mark(Common::DrawStat::Prot);
	if (base_addr % REGION_SIZE != 0 || base_addr >= ADDRESS_SIZE ||
	    REGION_SIZE > ADDRESS_SIZE - base_addr) {
		Fatal("invalid tracking region base 0x%016" PRIx64, base_addr);
	}

	const auto start_range = mask.FirstRange();
	const auto end_range   = mask.LastRange();
	if (start_range.first == REGION_PAGES) {
		FailFast("empty region watcher mask");
	}
	const auto first = start_range.first;
	const auto last  = end_range.second;
	if (start_range.second == end_range.second) {
		m_impl->UpdatePageWatchers<track, is_read, lw>(base_addr + first * PAGE_SIZE,
		                                               (last - first) * PAGE_SIZE);
		return;
	}

	auto* region = track ? m_impl->GetOrCreateRegion(base_addr) : m_impl->FindRegion(base_addr);
	if (region == nullptr) {
		Fatal("untracking unknown region 0x%016" PRIx64, base_addr);
	}
	m_impl->UpdateRegionWatchers<track, is_read, true, lw>(*region, base_addr, first, last, &mask);
}

template void PageManager::UpdatePageWatchersForRegion<true, true>(uint64_t, RegionBits&);
template void PageManager::UpdatePageWatchersForRegion<true, false>(uint64_t, RegionBits&);
template void PageManager::UpdatePageWatchersForRegion<false, true>(uint64_t, RegionBits&);
template void PageManager::UpdatePageWatchersForRegion<false, false>(uint64_t, RegionBits&);
// Session 131, knob "lwin": the pass of an operation with lwin >= 1 (L7).
template void PageManager::UpdatePageWatchersForRegion<true, false, true>(uint64_t, RegionBits&);

} // namespace Libs::Graphics
