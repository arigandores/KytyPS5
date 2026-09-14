#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_REGIONMANAGER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_REGIONMANAGER_H_

#include "common/assert.h"
#include "common/frameStats.h"
#include "graphics/host_gpu/pageManager.h"
#include "graphics/host_gpu/regionDefinitions.h"

#include <atomic>
#include <array>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <mutex>
#include <utility>

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#undef min
#undef max
#elif defined(__APPLE__)
#include <pthread.h>
#elif defined(__linux__)
#include <sys/syscall.h>
#include <unistd.h>
#endif

namespace Libs::Graphics {

class TrackingSpinLock final {
public:
	void lock() noexcept {
		const auto thread = CurrentThread();
		if (m_owner.load(std::memory_order_relaxed) == thread) {
			EXIT("recursive region tracking lock\n");
		}
		if (m_lock.test_and_set(std::memory_order_acquire)) {
			// Contended: spin, and account the wait for KYTY_FRAME_TRACE.
			namespace FS  = Common::FrameStats;
			const auto t0 = FS::Enabled() ? FS::NowNs() : 0;
			static const bool relaxed_spin = [] {
				const auto* value = std::getenv("KYTY_TRACKING_RELAXED_SPIN");
				return value == nullptr || value[0] != '0';
			}();
			while (m_lock.test_and_set(std::memory_order_acquire)) {
				if (m_owner.load(std::memory_order_relaxed) == thread) {
					EXIT("recursive region tracking lock while contended\n");
				}
				if (relaxed_spin) {
					// Wait with shared reads instead of repeatedly invalidating the owner's
					// cache line. The acquire RMW above still grants exclusive ownership.
					while (m_lock.test(std::memory_order_relaxed)) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
						YieldProcessor();
#elif defined(__x86_64__) || defined(__i386__)
						__builtin_ia32_pause();
#elif defined(__aarch64__)
						asm volatile("yield");
#else
						std::atomic_signal_fence(std::memory_order_seq_cst);
#endif
					}
				} else {
					std::atomic_signal_fence(std::memory_order_seq_cst);
				}
			}
			if (t0 != 0) {
				const auto ns = FS::NowNs() - t0;
				FS::Add(FS::Counter::LockSpinNs, ns);
				FS::Add(FS::Counter::LockSpins, 1);
				if (FS::CurrentRole() == FS::ThreadRole::Gpu) {
					FS::Add(FS::Counter::LockSpinGpuNs, ns);
				}
			}
		}
		m_owner.store(thread, std::memory_order_relaxed);
	}
	void unlock() noexcept {
		if (m_owner.load(std::memory_order_relaxed) != CurrentThread()) {
			EXIT("region tracking lock released by non-owner\n");
		}
		m_owner.store(0, std::memory_order_relaxed);
		m_lock.clear(std::memory_order_release);
	}

private:
	static uint32_t CurrentThread() noexcept {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
		return GetCurrentThreadId();
#elif defined(__APPLE__)
		// mach thread port is a nonzero per-thread id (0 is the "no owner" sentinel).
		return static_cast<uint32_t>(pthread_mach_thread_np(pthread_self()));
#elif defined(__linux__)
		static thread_local const uint32_t tid = static_cast<uint32_t>(::syscall(SYS_gettid));
		return tid;
#else
		EXIT("region tracking thread identity is unsupported on this platform\n");
#endif
	}

	std::atomic_flag     m_lock = ATOMIC_FLAG_INIT;
	std::atomic_uint32_t m_owner {0};
};

static_assert(std::atomic_uint32_t::is_always_lock_free);

// Gate "stkstat" (session 57, A1 ceiling; statistics only): what a read-only upload passes to
// RegionManager::NoteUploadStat.
struct StickyUploadStat {
	uint32_t frame = 0;     // flip number of the synchronization (the caller's clock)
	bool     bda   = false; // it runs for the BDA scan of PrepareBda
	// True when an image is indexed on the page (texture page hint): such a page is never sticky.
	bool (*may_have_images)(void* context, uint64_t page) noexcept = nullptr;
	void* context = nullptr;
};
// Frames in a row a page has to be hot to count as a sticky candidate (stk_cand).
inline constexpr uint8_t STICKY_STAT_STREAK = 3;

class RegionManager final {
public:
	RegionManager(PageManager& page_manager, uint64_t cpu_addr, std::atomic<uint64_t>& cpu_epoch)
	    : m_page_manager(page_manager), m_cpu_addr(cpu_addr), m_cpu_epoch(cpu_epoch) {
		if (m_cpu_addr % TRACKER_REGION_SIZE != 0) {
			EXIT("invalid region tracking manager construction\n");
		}
		m_cpu_dirty.Fill();
		m_writable.Fill();
		m_readable.Fill();
		m_armed.Clear();
	}

	KYTY_CLASS_NO_COPY(RegionManager);

	[[nodiscard]] uint64_t GetCpuAddr() const { return m_cpu_addr; }
	// Write epoch of this region only. The global CPU epoch moves on every page fault anywhere
	// in the address space, which makes it useless as a "did this range change" witness; this
	// one moves only when a page of this 4 MiB region is announced as CPU-written.
	[[nodiscard]] uint64_t Epoch() const noexcept {
		return m_epoch.load(std::memory_order_acquire);
	}
	template <DirtySource source>
	[[nodiscard]] bool IsModified(uint64_t offset, uint64_t size) const {
		const auto [start, end] = GetPageRange(m_cpu_addr + offset, size);
		const auto& bits        = GetBits<source>();
		return bits.AnyInRange(start, end);
	}

	// IsModified without holding `lock` (gate "trackfree", see MemoryTracker for the
	// ownership argument that makes each possible stale answer safe). Non-const because the
	// words are read through std::atomic_ref, which does not bind to a const object.
	template <DirtySource source>
	[[nodiscard]] bool IsModifiedRelaxed(uint64_t offset, uint64_t size) {
		const auto [start, end] = GetPageRange(m_cpu_addr + offset, size);
		return GetBits<source>().AnyInRangeRelaxed(start, end);
	}

	template <DirtySource source, bool enable>
	void ChangeState(uint64_t vaddr, uint64_t size) {
		const auto [start, end] = GetPageRange(vaddr, size);
		if constexpr (source == DirtySource::Cpu && enable) {
			if (m_gpu_dirty.AnyInRange(start, end)) {
				EXIT("CPU dirty state conflicts with GPU dirty state\n");
			}
		}
		if constexpr (source == DirtySource::Gpu && enable) {
			// Gate "armdefer": a page uploaded and left dirty for its arming is superseded by
			// the GPU write (its bytes are on the GPU already, as a clean page's would be): the
			// pending arming is applied and withdrawn, and the page is clean before the check.
			if (m_armed.AnyInRange(start, end)) {
				const RegionBits armed(m_armed, start, end);
				SettleArmedSync(start, end);
				for (const auto [first, last]: armed) {
					m_cpu_dirty.UnsetRange(first, last);
				}
			}
			if (m_cpu_dirty.AnyInRange(start, end)) {
				EXIT("GPU dirty state conflicts with CPU dirty state\n");
			}
		}
		auto& bits = GetBits<source>();
		if constexpr (enable) {
			if constexpr (source == DirtySource::Cpu) {
				// m_cpu_dirty is set from guest threads (InvalidateRegion) while the GuestGpu
				// thread may be scanning it without this lock, so every word it touches has to
				// be written atomically. Nothing else writes either map off that thread.
				bits.SetRangeRelaxed(start, end);
				// Gate "armdefer": the pages become writable, so an arming requested for them
				// is withdrawn (the next synchronization copies and requests again).
				m_armed.UnsetRange(start, end);
			} else {
				bits.SetRange(start, end);
			}
		} else {
			bits.UnsetRange(start, end);
			if constexpr (source == DirtySource::Cpu) {
				SettleArmedSync(start, end);
			}
		}
		if constexpr (source == DirtySource::Cpu && enable) {
			// Called with the region lock held, after the bits and before the pages become
			// writable (UpdateProtection below). Bits first, epochs second: a lock-free reader of
			// the bits (gate "syncfree") takes its epoch snapshot before it reads them, so an
			// announcement it missed moves the epochs after that snapshot and the next
			// HasCurrentUpload check fails. A BDA scan observing these epochs still acquires this
			// lock before it reads dirty bits, so the order does not matter to it.
			m_cpu_epoch.fetch_add(1, std::memory_order_release);
			m_epoch.fetch_add(1, std::memory_order_release);
		}
		if constexpr (source == DirtySource::Cpu) {
			UpdateProtection<!enable, false>();
		} else {
			// A new GPU write (or a completed download) ends the stale window of these pages:
			// the next CPU read faults again and is served from the latest completed data.
			m_stale.UnsetRange(start, end);
			UpdateProtection<enable, true>();
		}
	}

	// GPU-dirty pages of [vaddr, vaddr+size) become readable by the CPU without a fault while
	// their GPU writes are still in flight (BufferCache::ServeStaleRead): the CPU observes the
	// last completed GPU data, as it would on hardware, instead of draining the queue.
	void MarkStaleReadable(uint64_t vaddr, uint64_t size) {
		const auto [start, end] = GetPageRange(vaddr, size);
		RegionBits range;
		range.SetRange(start, end);
		range &= m_gpu_dirty;
		if (range.None()) {
			return;
		}
		m_stale |= range;
		UpdateProtection<false, true>();
	}

	// Knob "faultkb" (MemoryTracker::InvalidateWriteFault), under `lock`: the pages of
	// [window_begin, window_begin + window_size) contiguous with the page of `vaddr` that hold no
	// GPU-owned bytes, as {address, size}. The page of `vaddr` must not be GPU-dirty. A GPU-dirty
	// page ends the run, so a CPU-dirty change of the result never meets GPU-owned state (read
	// watchers, stale-readable pages). `armed` receives how many of these pages other than the
	// page of `vaddr` are CPU-clean now, i.e. would gain a dirty bit.
	[[nodiscard]] std::pair<uint64_t, uint64_t> GpuCleanRunAround(uint64_t vaddr, uint64_t window_begin,
	                                                              uint64_t window_size,
	                                                              uint64_t* armed) const {
		const auto [window_first, window_last] = GetPageRange(window_begin, window_size);
		const auto page = static_cast<size_t>((vaddr - m_cpu_addr) / TRACKER_PAGE_SIZE);
		if (vaddr < m_cpu_addr || page < window_first || page >= window_last) {
			EXIT("write-fault page lies outside its window\n");
		}
		size_t first = page;
		size_t last  = page + 1;
		while (first > window_first && !m_gpu_dirty.Get(first - 1)) {
			first--;
		}
		while (last < window_last && !m_gpu_dirty.Get(last)) {
			last++;
		}
		if (armed != nullptr) {
			uint64_t clean = 0;
			for (size_t index = first; index < last; index++) {
				if (index != page && !m_cpu_dirty.Get(index)) {
					clean++;
				}
			}
			*armed = clean;
		}
		return {m_cpu_addr + first * TRACKER_PAGE_SIZE, (last - first) * TRACKER_PAGE_SIZE};
	}

	template <DirtySource source, bool clear, typename Func>
	void ForEachModifiedRange(uint64_t vaddr, uint64_t size, Func&& func) {
		const auto [start, end] = GetPageRange(vaddr, size);
		auto&      bits         = GetBits<source>();
		RegionBits mask(bits, start, end);
		if constexpr (clear) {
			if constexpr (source == DirtySource::Cpu) {
				SettleArmedSync(start, end);
			}
			bits.UnsetRange(start, end);
			if constexpr (source == DirtySource::Cpu) {
				UpdateProtection<true, false>();
			} else {
				m_stale.UnsetRange(start, end);
				UpdateProtection<false, true>();
			}
		}
		for (const auto [first, last]: mask) {
			func(m_cpu_addr + first * TRACKER_PAGE_SIZE, (last - first) * TRACKER_PAGE_SIZE);
		}
	}

	// Session 60, gate "armdefer": a synchronous path is about to clear CPU-dirty bits of
	// [start, end) and relies on the protection being in effect before its caller copies
	// (Region::apply, R). Pages armed through the worker may still lag: their pending changes are
	// applied here, and the arming is withdrawn (the dirty bit goes with it).
	void SettleArmedSync(size_t start, size_t end) {
		if (!m_armed.AnyInRange(start, end)) {
			return;
		}
		for (const auto [first, last]: RegionBits(m_armed, start, end)) {
			m_page_manager.FlushProtection(m_cpu_addr + first * TRACKER_PAGE_SIZE,
			                               (last - first) * TRACKER_PAGE_SIZE);
		}
		m_armed.UnsetRange(start, end);
		Common::FrameStats::Add(Common::FrameStats::Counter::ArmSyncFlushes, 1);
	}

	// Session 60, gate "armdefer": the read-only upload of the CPU-dirty pages of [vaddr, vaddr +
	// size), with their write watchers armed by the protection worker instead of this thread.
	// A dirty page is copied and keeps its dirty bit; its watcher is requested (m_armed) and the
	// worker applies it. A page that is dirty, requested earlier and whose host protection is in
	// effect now (PageManager::KeepApplied) is copied once more and only then loses its dirty bit.
	// Every write that landed before the protection took effect is in one of the two copies, and
	// every later one faults: ChangeState<Cpu, true> withdraws the arming with the fault, so a page
	// with m_armed set has had its watcher since the request. Returns true while pages of the
	// range are still dirty (the caller must not record a current upload).
	template <typename Func>
	bool ForEachUploadRangeArmDeferred(uint64_t vaddr, uint64_t size, bool verify, Func&& func) {
		namespace FS = Common::FrameStats;
		const auto [start, end] = GetPageRange(vaddr, size);
		const RegionBits mask(m_cpu_dirty, start, end);
		if (mask.None()) {
			return false;
		}
		const RegionBits armed_before = mask & m_armed;
		RegionBits       settled      = armed_before;
		if (settled.Any()) {
			m_page_manager.KeepApplied(m_cpu_addr, settled);
		}
		const RegionBits request = mask & ~m_armed;
		uint64_t         settled_pages = 0;
		uint64_t         armed_pages   = 0;
		uint64_t         request_pages = 0;
		for (const auto [first, last]: settled) {
			if (verify && PageManager::IsHostWritable(m_cpu_addr + first * TRACKER_PAGE_SIZE)) {
				FS::Add(FS::Counter::ArmBad, 1);
				static std::atomic<uint32_t> logged {0};
				if (logged.fetch_add(1, std::memory_order_relaxed) < 32) {
					std::fprintf(stderr, "ArmDeferVerify: MISMATCH settled page 0x%016llx is writable\n",
					             static_cast<unsigned long long>(m_cpu_addr + first * TRACKER_PAGE_SIZE));
					std::fflush(stderr);
				}
			}
			m_cpu_dirty.UnsetRange(first, last);
			m_armed.UnsetRange(first, last);
			settled_pages += last - first;
		}
		for (const auto [first, last]: armed_before) {
			armed_pages += last - first;
		}
		for (const auto [first, last]: request) {
			m_armed.SetRange(first, last);
			request_pages += last - first;
		}
		UpdateProtection<true, false>(true);
		FS::Add(FS::Counter::ArmRequestPages, request_pages);
		FS::Add(FS::Counter::ArmSettledPages, settled_pages);
		FS::Add(FS::Counter::ArmWaitPages, armed_pages - settled_pages);
		for (const auto [first, last]: mask) {
			func(m_cpu_addr + first * TRACKER_PAGE_SIZE, (last - first) * TRACKER_PAGE_SIZE);
		}
		const bool provisional = request_pages != 0 || armed_pages != settled_pages;
		if (provisional) {
			// Pages stay dirty without a fault having announced them: the region's write epoch
			// moves so that the BDA dirty-range scan (gate "bdastamp", RegionWriteStamp) and the
			// buffer-request memo (gate "buffast", RangeWriteEpoch) come back for the settling
			// upload instead of skipping the region as unchanged. Not the global CPU epoch: that
			// one witnesses other buffers' uploads and nothing of theirs changed.
			m_epoch.fetch_add(1, std::memory_order_release);
		}
		return provisional;
	}

	// Gate "stkstat" (session 57, A1 ceiling; statistics only). A CPU write fault at `vaddr`, a page
	// of this region: 2 when the page write-faulted earlier in this frame, 1 when in the previous
	// frame, else 0. Any thread, from the fault handler: one relaxed exchange of a stamp allocated
	// with the region, no lock. Concurrent faults of one page may both read "this frame".
	[[nodiscard]] uint32_t NoteWriteFaultStat(uint64_t vaddr, uint32_t frame) noexcept {
		const auto page     = static_cast<size_t>((vaddr - m_cpu_addr) / TRACKER_PAGE_SIZE);
		const auto now      = StickyStamp(frame);
		const auto previous = m_sticky_stat->fault_frame[page].exchange(now, std::memory_order_relaxed);
		if (previous == now) {
			return 2;
		}
		return previous != 0 && static_cast<uint16_t>(now - previous) == 1u ? 1 : 0;
	}

	// Gate "stkstat", under `lock` on the GuestGpu thread, before a read-only upload clears the
	// CPU-dirty bits of [vaddr, vaddr + size): each of those pages gets its write watcher again
	// (stk_arm). A page armed in this or the previous frame already and CPU-dirty again is hot
	// (stk_arm_hot); hot in STICKY_STAT_STREAK frames in a row and without an indexed image it is a
	// candidate a sticky mechanism would keep writable (stk_cand, counted once a frame).
	// stk_vp_save: every armed page of this call is a candidate, so its watcher change would be empty.
	// Changes no dirty bit and no watcher: the stamps and candidate maps are statistics only.
	void NoteUploadStat(uint64_t vaddr, uint64_t size, const StickyUploadStat& stat) {
		namespace FS            = Common::FrameStats;
		const auto [start, end] = GetPageRange(vaddr, size);
		const RegionBits mask(m_cpu_dirty, start, end);
		if (mask.None()) {
			return;
		}
		auto&      pages = *m_sticky_stat;
		const auto now   = StickyStamp(stat.frame);
		if (pages.cand_stamp != now) {
			// First update of this frame in this region: rotate the two maps instead of walking them.
			const bool previous = pages.cand_stamp != 0 && static_cast<uint16_t>(now - pages.cand_stamp) == 1u;
			pages.cand_prev      = previous ? pages.cand_cur : RegionBits {};
			pages.cand_cur       = RegionBits {};
			pages.cand_stamp     = now;
		}
		uint64_t armed          = 0;
		uint64_t hot            = 0;
		uint64_t hot_images     = 0;
		uint64_t distinct       = 0;
		uint64_t candidates     = 0;
		bool     all_candidates = true;
		for (const auto [first, last]: mask) {
			armed += last - first;
			for (size_t page = first; page < last; page++) {
				const auto armed_at  = pages.arm_frame[page];
				pages.arm_frame[page] = now;
				if (armed_at == 0 || (armed_at != now && static_cast<uint16_t>(now - armed_at) != 1u)) {
					all_candidates = false;
					continue;
				}
				// Written, not only re-dirtied: a fault window (knob "faultkb") opens clean neighbours.
				const auto faulted_at = pages.fault_frame[page].load(std::memory_order_relaxed);
				if (faulted_at == 0 || (faulted_at != now && static_cast<uint16_t>(now - faulted_at) != 1u)) {
					all_candidates = false;
					continue;
				}
				hot++;
				const bool images = stat.may_have_images != nullptr &&
				                    stat.may_have_images(stat.context, m_cpu_addr + page * TRACKER_PAGE_SIZE);
				if (images) {
					hot_images++;
				}
				if (pages.hot_frame[page] != now) {
					const auto last_hot   = pages.hot_frame[page];
					const bool in_a_row   = last_hot != 0 && static_cast<uint16_t>(now - last_hot) == 1u;
					const auto run        = pages.streak[page];
					pages.streak[page]    = in_a_row ? (run < 255u ? static_cast<uint8_t>(run + 1u) : run) : uint8_t {1};
					pages.hot_frame[page] = now;
					distinct++;
					if (!images && pages.streak[page] >= STICKY_STAT_STREAK) {
						candidates++;
					}
				}
				if (images || pages.streak[page] < STICKY_STAT_STREAK) {
					all_candidates = false;
					continue;
				}
				pages.cand_cur.Set(page);
			}
		}
		FS::Add(FS::Counter::StickyArmPages, armed);
		if (hot != 0) {
			FS::Add(FS::Counter::StickyArmHot, hot);
			if (stat.bda) {
				FS::Add(FS::Counter::StickyArmHotBda, hot);
			}
			if (hot_images != 0) {
				FS::Add(FS::Counter::StickyArmHotImg, hot_images);
			}
		}
		if (distinct != 0) {
			FS::Add(FS::Counter::StickyHotPages, distinct);
			if (candidates != 0) {
				FS::Add(FS::Counter::StickyCandidates, candidates);
			}
		}
		if (all_candidates) {
			FS::Add(FS::Counter::StickySavedCalls, 1);
		}
	}

	// Gate "stkstat": candidate pages of [vaddr, vaddr + size) in this or the previous frame; with
	// `any`, 1 as soon as there is one. GuestGpu thread only, without `lock`: that thread is the only
	// writer of the candidate maps (NoteUploadStat).
	[[nodiscard]] uint64_t StickyCandidatePages(uint64_t vaddr, uint64_t size, uint32_t frame, bool any) const {
		const auto& pages   = *m_sticky_stat;
		const auto  now     = StickyStamp(frame);
		const bool  current = pages.cand_stamp == now;
		if (!current && (pages.cand_stamp == 0 || static_cast<uint16_t>(now - pages.cand_stamp) != 1u)) {
			return 0;
		}
		const auto [start, end] = GetPageRange(vaddr, size);
		const bool in_current   = pages.cand_cur.AnyInRange(start, end);
		const bool in_previous  = current && pages.cand_prev.AnyInRange(start, end);
		if (!in_current && !in_previous) {
			return 0;
		}
		if (any) {
			return 1;
		}
		const RegionBits live = current ? (pages.cand_cur | pages.cand_prev) : pages.cand_cur;
		uint64_t         count = 0;
		for (const auto [first, last]: RegionBits(live, start, end)) {
			count += last - first;
		}
		return count;
	}

	TrackingSpinLock lock;

private:
	// `defer` (gate "armdefer", write side only): the watchers are added to the page state now
	// and their host protection is applied by the worker. A page in m_armed is read-only although
	// CPU-dirty (ForEachUploadRangeArmDeferred).
	template <bool track, bool is_read>
	void UpdateProtection(bool defer = false) {
		const auto protection = is_read ? (~m_gpu_dirty | m_stale) : (m_cpu_dirty & ~m_armed);
		auto&      previous   = is_read ? m_readable : m_writable;
		auto       mask       = protection ^ previous;
		if (mask.None()) {
			return;
		}
		previous = protection;
		// prot_held_us: every caller of UpdateProtection already holds `lock`, so this scope
		// is exactly the time the region lock stays held across the host protection change
		// (VirtualProtect plus the address-space mutex behind it). Diagnostic, no gate.
		Common::FrameStats::Scope held(Common::FrameStats::Counter::ProtectHeldNs);
		PageManager::SpinHeld    spin_held; // prot_spin_*: `lock` is held across the calls below
		if constexpr (track && !is_read) {
			if (defer) {
				m_page_manager.UpdatePageWatchersForRegionDeferred(m_cpu_addr, mask);
				return;
			}
		}
		m_page_manager.UpdatePageWatchersForRegion<track, is_read>(m_cpu_addr, mask);
	}

	template <DirtySource source>
	RegionBits& GetBits() {
		if constexpr (source == DirtySource::Cpu) {
			return m_cpu_dirty;
		} else {
			return m_gpu_dirty;
		}
	}

	template <DirtySource source>
	const RegionBits& GetBits() const {
		if constexpr (source == DirtySource::Cpu) {
			return m_cpu_dirty;
		} else {
			return m_gpu_dirty;
		}
	}

	[[nodiscard]] std::pair<size_t, size_t> GetPageRange(uint64_t vaddr, uint64_t size) const {
		if (size == 0 || vaddr < m_cpu_addr || vaddr >= m_cpu_addr + TRACKER_REGION_SIZE ||
		    size > m_cpu_addr + TRACKER_REGION_SIZE - vaddr) {
			EXIT("range lies outside its tracking region\n");
		}
		const auto offset = vaddr - m_cpu_addr;
		return {static_cast<size_t>(offset / TRACKER_PAGE_SIZE),
		        static_cast<size_t>((offset + size + TRACKER_PAGE_SIZE - 1) / TRACKER_PAGE_SIZE)};
	}

	PageManager& m_page_manager;
	uint64_t     m_cpu_addr = 0;
	std::atomic<uint64_t>& m_cpu_epoch;
	std::atomic<uint64_t>  m_epoch {1};
	// The dirty maps are read without the lock (IsModifiedRelaxed); give them their own
	// cache lines so those reads do not fight `lock`, which otherwise shares a line with
	// the first words of m_cpu_dirty.
	alignas(64) RegionBits m_cpu_dirty;
	RegionBits   m_gpu_dirty;
	RegionBits   m_stale; // subset of m_gpu_dirty: readable by the CPU while GPU writes are in flight
	RegionBits   m_writable;
	RegionBits   m_readable;
	// Gate "armdefer": subset of m_cpu_dirty whose write watcher was requested through the
	// worker; such a page is read-only in the page state and stays dirty until a later upload
	// finds the protection in effect. Written under `lock` only.
	RegionBits   m_armed;
	// Gate "stkstat" (statistics only). Allocated with the region, so the fault path allocates
	// nothing (fault handlers never create regions). Stamps are StickyStamp(frame), 0 = never.
	// fault_frame: the fault handlers of any thread (relaxed exchange). Everything else: the
	// GuestGpu thread, under `lock` (NoteUploadStat) or without it (StickyCandidatePages).
	struct StickyStatPages {
		std::array<std::atomic<uint16_t>, TRACKER_REGION_PAGES> fault_frame {};
		std::array<uint16_t, TRACKER_REGION_PAGES>              arm_frame {};
		std::array<uint16_t, TRACKER_REGION_PAGES>              hot_frame {};
		std::array<uint8_t, TRACKER_REGION_PAGES>               streak {};
		RegionBits cand_cur;       // candidates of the frame cand_stamp
		RegionBits cand_prev;      // ... of the frame before it
		uint16_t   cand_stamp = 0;
	};
	[[nodiscard]] static constexpr uint16_t StickyStamp(uint32_t frame) noexcept {
		return static_cast<uint16_t>(frame % 0xffffu + 1u);
	}
	std::unique_ptr<StickyStatPages> m_sticky_stat = std::make_unique<StickyStatPages>();
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_REGIONMANAGER_H_
