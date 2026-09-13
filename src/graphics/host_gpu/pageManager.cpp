#include "graphics/host_gpu/pageManager.h"

#include "common/alignment.h"
#include "common/frameStats.h"
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
	ApplyGuard(std::atomic_flag& lock, bool engage): m_lock(engage ? &lock : nullptr) {
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
			FS::Add(FS::Counter::ApplyWaitNs, ns);
			if (FS::CurrentRole() == FS::ThreadRole::Gpu) {
				FS::Add(FS::Counter::ApplyWaitGpuNs, ns);
			}
		}
	}
	~ApplyGuard() {
		if (m_lock != nullptr) {
			m_lock->clear(std::memory_order_release);
		}
	}
	KYTY_CLASS_NO_COPY(ApplyGuard);

private:
	std::atomic_flag* m_lock;
};

void ValidateRange(uint64_t vaddr, uint64_t size) {
	if (!GuestRange {vaddr, size}.Valid()) {
		Fatal("invalid range vaddr=0x%016" PRIx64 ", size=0x%016" PRIx64, vaddr, size);
	}
}

} // namespace

struct PageManager::Impl {
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
		// application covering the page clears it. Guarded by `lock`.
		std::array<uint64_t, REGION_PAGES / 64> pending {};
		bool                                    has_pending = false; // any bit set
		bool                                    queued      = false; // sits in the worker queue
	};

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

	void Protect(uint64_t vaddr, uint64_t size, Common::VirtualMemory::Mode mode) noexcept {
		static const bool trap = std::getenv("KYTY_STREAM_TRACE") != nullptr;
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
				}
				if (t_protect_masked) {
					FS::Add(FS::Counter::ProtectMaskedNs, ns);
					FS::Add(FS::Counter::ProtectMaskedCalls, 1);
				}
			}
		}
	}

	static void SetPendingRange(Region& region, size_t first, size_t count, bool value) {
		for (size_t page = first; page < first + count; page++) {
			auto& word = region.pending[page / 64];
			const auto bit = uint64_t {1} << (page % 64);
			if (value) {
				word |= bit;
			} else {
				word &= ~bit;
			}
		}
	}

	// Protects a run of pages under the region lock and marks their host state as current.
	void ProtectRun(Region& region, uint64_t base_addr, size_t first, size_t count,
	                Common::VirtualMemory::Mode perms) {
		Protect(base_addr + first * PAGE_SIZE, count * PAGE_SIZE, perms);
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
		// Order apply -> lock (see Region::apply). Marking pages pending changes no host
		// protection and does not need the apply lock.
		ApplyGuard apply(region.apply, !batch && !defer);
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
					ProtectRun(region, base_addr, static_cast<size_t>(range_begin),
					           static_cast<size_t>(range_bytes / PAGE_SIZE), perms);
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
	static bool TakePendingRun(Region& region, size_t first, size_t last, size_t max_pages,
							   size_t* run_first, size_t* run_pages,
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
			size_t     end        = page + 1;
			while (end < last && end - page < max_pages && IsPending(region, end) &&
				   region.pages[end].Perms() == protection) {
				end++;
			}
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
			ApplyGuard                  apply(region.apply, true);
			size_t                      run_first = 0;
			size_t                      run_pages = 0;
			Common::VirtualMemory::Mode perms     = Common::VirtualMemory::Mode::ReadWrite;
			{
				SpinGuard lock(region.lock);
				if (!TakePendingRun(region, 0, REGION_PAGES, call_pages, &run_first, &run_pages,
									&perms)) {
					break;
				}
			}
			Protect(base_addr + run_first * PAGE_SIZE, run_pages * PAGE_SIZE, perms);
		}
	}

	// Applies the pending runs of [first, last) of one region (a BatchScope flush, or an
	// invalidation making sure a change deferred by another thread is in effect). The spin lock is
	// released before every host call, only the apply lock is held across them. Takes the apply
	// lock even when nothing is pending (Region::apply, R). Returns the number of host calls.
	uint32_t FlushRegion(Region& region, uint64_t base_addr, size_t first, size_t last) {
		ApplyGuard apply(region.apply, true);
		t_protect_masked      = false;
		const auto call_pages = WorkerCallPages();
		uint32_t   runs       = 0;
		uint64_t   pages      = 0;
		for (;;) {
			size_t                      run_first = 0;
			size_t                      run_pages = 0;
			Common::VirtualMemory::Mode perms     = Common::VirtualMemory::Mode::ReadWrite;
			{
				SpinGuard lock(region.lock);
				if (!TakePendingRun(region, first, last, call_pages, &run_first, &run_pages,
									&perms)) {
					break;
				}
			}
			Protect(base_addr + run_first * PAGE_SIZE, run_pages * PAGE_SIZE, perms);
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
								static_cast<size_t>((chunk_end - region_base) / PAGE_SIZE)) != 0) {
					Common::FrameStats::Add(Common::FrameStats::Counter::BatchRefault, 1);
				}
			}
			chunk_begin = chunk_end;
		}
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
			{
				SpinGuard lock(region->lock);
				if (region->has_pending && IsPending(*region, page_index)) {
					continue;
				}
				expected = region->pages[page_index].Perms();
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

static_assert(std::atomic<void*>::is_always_lock_free);

PageManager::PageManager(): m_impl(std::make_unique<Impl>()) {}

PageManager::~PageManager() = default;

uint64_t PageManager::GetPageSize() const {
	return PAGE_SIZE;
}

template <bool track>
void PageManager::UpdatePageWatchers(uint64_t vaddr, uint64_t size) {
	m_impl->UpdatePageWatchers<track, false>(vaddr, size);
}

template void PageManager::UpdatePageWatchers<true>(uint64_t, uint64_t);
template void PageManager::UpdatePageWatchers<false>(uint64_t, uint64_t);

void PageManager::UpdatePageWatchersDeferred(uint64_t vaddr, uint64_t size) {
	m_impl->UpdatePageWatchers<true, false>(vaddr, size, Impl::DeferEnabled());
}

void PageManager::DrainDeferredProtection() {
	m_impl->Drain();
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
										  slot.first, slot.last) == 0) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BatchMerged, 1);
		}
	}
}

void PageManager::FlushProtection(uint64_t vaddr, uint64_t size) {
	m_impl->FlushRange(vaddr, size);
}

void PageManager::VerifyProtection(uint64_t vaddr, uint64_t size) {
	m_impl->Verify(vaddr, size);
}

template <bool track, bool is_read>
void PageManager::UpdatePageWatchersForRegion(uint64_t base_addr, RegionBits& mask) {
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
