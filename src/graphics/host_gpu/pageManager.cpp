#include "graphics/host_gpu/pageManager.h"

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
	std::fputc('\n', stderr);
	std::fflush(stderr);
	std::_Exit(322);
}

class SpinGuard final {
public:
	explicit SpinGuard(std::atomic_flag& lock): m_lock(lock) {
		while (m_lock.test_and_set(std::memory_order_acquire)) {
			std::atomic_signal_fence(std::memory_order_seq_cst);
		}
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
					if (FS::CurrentRole() == FS::ThreadRole::Gpu) {
						AcAddKept(ns, FS::Counter::AcKeptHelpN, FS::Counter::AcKeptHelpNs);
					} else {
						FS::Add(FS::Counter::AcMovedN, 1);
						FS::Add(FS::Counter::AcMovedNs, ns);
						FS::Add(FS::Counter::AcMovedPages, pages);
					}
				} else if (arm != Arm::No && (t_ac_state == AcWritten || t_ac_state == AcMove) &&
				           FS::CurrentRole() == FS::ThreadRole::Gpu) {
					const auto reason = t_ac_state == AcWritten ? AcReasonWr : static_cast<uint8_t>(t_ac_reason);
					switch (reason) {
						case static_cast<uint8_t>(PageManager::ArmCopyReason::Inline):
							AcAddKept(ns, FS::Counter::AcKeptInlN, FS::Counter::AcKeptInlNs);
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
	template <bool track, bool is_read, bool masked>
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

	template <bool track, bool is_read>
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
			UpdateRegionWatchers<track, is_read, false>(*region, region_base, first, last, nullptr,
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
	};

	// What the detector saw under `lock`: pend_now and Perms() of each page it looked at.
	struct AcSnap {
		PageBits                            pend {};
		std::array<uint8_t, REGION_PAGES> perms {};
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
	              uint64_t* chk, uint64_t* bad) {
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
			ApplyGuard apply(region->apply, true, FS::Counter::AcJobWaitNs);
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
			const auto t0  = FS::Enabled() ? FS::NowNs() : 0;
			AcSnap     snap {};
			uint64_t   chk = 0;
			uint64_t   bad = 0;
			AcDetect(*region, region_base, window, true, mode, snap, &chk, &bad);
			if (t0 != 0) {
				FS::Add(FS::Counter::AcChkNs, FS::NowNs() - t0);
			}
			FS::Add(FS::Counter::AcChk, chk);
			FS::Add(FS::Counter::AcBad, bad);
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
		}
		return mode == 3;
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
		op.mode            = 0;
		op.window_count    = 0;
		op.windows_flushed = false;
		op.copies.clear();
		op.areas.clear();
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
			drain_cv.wait(lock, [this] { return inflight.load(std::memory_order_acquire) == 0; });
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
	// The regions holding U bits with their base, in the order they got the first; written and read only on the
	// GuestGpu thread (SkipRun under a latch of 1, CeilRearm).
	std::vector<std::pair<Region*, uint64_t>> unarmed_regions;

	std::unique_ptr<std::atomic<Region*>[]> regions;
	std::vector<std::unique_ptr<Region>>    region_storage;
	std::mutex                              region_mutex;

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
	if (m_previous_state != Impl::AcOutside) {
		return; // nested: the latch of the outer synchronization
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
	Impl::t_ac_state = state;
	Impl::t_ac_mode  = static_cast<uint8_t>(value);
}

PageManager::ArmCopyScope::~ArmCopyScope() {
	if (m_engaged) {
		Impl::t_ac_state = m_previous_state;
		Impl::t_ac_mode  = m_previous_mode;
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

template <bool track, bool is_read>
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
		m_impl->UpdatePageWatchers<track, is_read>(base_addr + first * PAGE_SIZE,
		                                           (last - first) * PAGE_SIZE);
		return;
	}

	auto* region = track ? m_impl->GetOrCreateRegion(base_addr) : m_impl->FindRegion(base_addr);
	if (region == nullptr) {
		Fatal("untracking unknown region 0x%016" PRIx64, base_addr);
	}
	m_impl->UpdateRegionWatchers<track, is_read, true>(*region, base_addr, first, last, &mask);
}

template void PageManager::UpdatePageWatchersForRegion<true, true>(uint64_t, RegionBits&);
template void PageManager::UpdatePageWatchersForRegion<true, false>(uint64_t, RegionBits&);
template void PageManager::UpdatePageWatchersForRegion<false, true>(uint64_t, RegionBits&);
template void PageManager::UpdatePageWatchersForRegion<false, false>(uint64_t, RegionBits&);

} // namespace Libs::Graphics
