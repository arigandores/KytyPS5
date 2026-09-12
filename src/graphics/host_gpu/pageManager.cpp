#include "graphics/host_gpu/pageManager.h"

#include "common/alignment.h"
#include "common/frameStats.h"
#include "common/virtualMemory.h"
#include "graphics/host_gpu/regionDefinitions.h"
#include "kernel/memory.h"

#include <algorithm>
#include <array>
#include <atomic>
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
		std::array<PageState, REGION_PAGES> pages;
		// Pages whose host protection may lag behind Perms(): a deferred write-watcher edge
		// (UpdatePageWatchersDeferred) sets the bit, the worker or any synchronous Protect of
		// the page clears it. Guarded by `lock`.
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
	template <bool track, bool is_read, bool masked>
	void UpdateRegionWatchers(Region& region, uint64_t base_addr, size_t first, size_t last,
	                          const RegionBits* mask = nullptr, bool defer = false) {
		bool      enqueue = false;
		t_protect_masked  = masked;
		{
		SpinGuard lock(region.lock);
		auto      perms                 = region.pages[first].Perms();
		uint64_t  range_begin           = 0;
		uint64_t  range_bytes           = 0;
		uint64_t  potential_range_bytes = 0;

		const auto release_pending = [&] {
			if (range_bytes != 0) {
				if (defer) {
					SetPendingRange(region, static_cast<size_t>(range_begin),
					                static_cast<size_t>(range_bytes / PAGE_SIZE), true);
					region.has_pending = true;
					if (!region.queued) {
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

	// Applies the pending runs of one region. Holds the region lock across the VirtualProtect
	// calls (a region is 4 MB, so at most ~100 us) so that no synchronous change of the same
	// pages can be overtaken by a stale protection value.
	void ApplyPending(Region& region, uint64_t base_addr) {
		SpinGuard lock(region.lock);
		region.queued = false;
		if (!region.has_pending) {
			return;
		}
		const auto call_pages = WorkerCallPages();
		size_t     page       = 0;
		while (page < REGION_PAGES) {
			const auto word = region.pending[page / 64];
			if (word == 0) {
				page = (page / 64 + 1) * 64;
				continue;
			}
			if ((word & (uint64_t {1} << (page % 64))) == 0) {
				page++;
				continue;
			}
			const auto perms = region.pages[page].Perms();
			size_t     end   = page + 1;
			while (end < REGION_PAGES && end - page < call_pages &&
			       (region.pending[end / 64] & (uint64_t {1} << (end % 64))) != 0 &&
			       region.pages[end].Perms() == perms) {
				end++;
			}
			while (sync_waiters.load(std::memory_order_acquire) != 0) {
				std::this_thread::yield();
			}
			Protect(base_addr + page * PAGE_SIZE, (end - page) * PAGE_SIZE, perms);
			SetPendingRange(region, page, end - page, false);
			page = end;
		}
		region.has_pending = false;
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
