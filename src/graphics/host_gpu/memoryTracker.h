#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_MEMORYTRACKER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_MEMORYTRACKER_H_

#include "common/assert.h"
#include "common/gates.h"
#include "graphics/host_gpu/pageManager.h"
#include "graphics/host_gpu/rangeSet.h"
#include "graphics/host_gpu/regionManager.h"

#include <algorithm>
#include <atomic>
#include <memory>
#include <mutex>
#include <type_traits>
#include <utility>
#include <vector>

namespace Libs::Graphics {

class MemoryTracker final {
public:
	explicit MemoryTracker(PageManager& page_manager);
	~MemoryTracker();

	KYTY_CLASS_NO_COPY(MemoryTracker);

	[[nodiscard]] bool IsRegionCpuModified(uint64_t vaddr, uint64_t size);
	[[nodiscard]] uint64_t CpuWriteEpoch() const noexcept {
		return m_cpu_epoch.load(std::memory_order_acquire);
	}
	// Combined write epoch of the regions covering one range: a witness for "no CPU write has
	// been announced to this range since". Zero means the range is not fully tracked, and nothing
	// may be assumed about it. Lock free - each region publishes its epoch under its own lock
	// before the pages become writable, exactly like the global epoch above.
	[[nodiscard]] uint64_t RangeWriteEpoch(uint64_t vaddr, uint64_t size) noexcept {
		ValidateRange(vaddr, size);
		uint64_t mixed     = 0x9e3779b97f4a7c15ull;
		uint64_t remaining = size;
		uint64_t index     = vaddr / TRACKER_REGION_SIZE;
		uint64_t offset    = vaddr % TRACKER_REGION_SIZE;
		while (remaining != 0) {
			const auto bytes   = std::min(TRACKER_REGION_SIZE - offset, remaining);
			auto*      manager = m_regions[index].load(std::memory_order_acquire);
			if (manager == nullptr) {
				return 0; // an untracked region is CPU-dirty by definition
			}
			mixed = (mixed ^ manager->Epoch()) * 0x100000001b3ull;
			remaining -= bytes;
			offset = 0;
			index++;
		}
		return mixed == 0 ? 1 : mixed;
	}
	// Witness for "no CPU write has been announced to this tracking region since": the region's
	// manager together with its write epoch. A region that does not exist yet stamps as
	// {nullptr, 0}; managers are never destroyed, so an equal stamp means the same region with no
	// announcement in between. Lock free - RegionManager publishes the epoch under its own lock
	// before the pages become writable (see BufferCache::SynchronizeBuffersInRange).
	struct RegionStamp {
		const void* manager = nullptr;
		uint64_t    epoch   = 0;
		bool        operator==(const RegionStamp&) const noexcept = default;
	};
	[[nodiscard]] static constexpr size_t RegionCount() noexcept { return REGION_COUNT; }
	[[nodiscard]] RegionStamp RegionWriteStamp(uint64_t index) const noexcept {
		if (index >= REGION_COUNT) {
			return {};
		}
		const auto* manager = m_regions[index].load(std::memory_order_acquire);
		return manager == nullptr ? RegionStamp {} : RegionStamp {manager, manager->Epoch()};
	}
	[[nodiscard]] bool IsRegionGpuModified(uint64_t vaddr, uint64_t size);
	// Combined streaming-read query: some CPU-dirty bytes and no GPU-dirty pages,
	// with a single lock acquisition per tracking region. Does not change ownership.
	[[nodiscard]] bool IsRegionCpuModifiedAndGpuClean(uint64_t vaddr, uint64_t size);
	// Lock-free forms of the two queries above (gate "trackfree", wrapped by BufferCache).
	// GPU-dirty state is moved only by the GuestGpu thread: it is set by
	// ForEachUploadRange(is_written = true) out of BufferCache::SynchronizeBuffer, and cleared
	// by UnmarkRegionAsGpuModified and ForEachDownloadRange<true> (UntrackMemory does not
	// touch it, and MarkRegionAsGpuModified has no caller outside tests). On that thread the
	// GPU
	// half of the answer is exact and "GPU clean while GPU-dirty" - the only unsound answer
	// - cannot happen. The CPU half may miss a bit that a guest thread is announcing right
	// now (InvalidateRegion); the answer then reads "not CPU modified" and the caller falls
	// back to the ordinary buffer path, which re-reads the bits under the lock.
	// Callers must be the GuestGpu thread; this class cannot check that (it is built into
	// targets that have no GuestGpu), BufferCache does.
	[[nodiscard]] bool IsRegionGpuModifiedFast(uint64_t vaddr, uint64_t size);
	[[nodiscard]] bool IsRegionCpuModifiedAndGpuCleanFast(uint64_t vaddr, uint64_t size);
	// Gate "syncfree": every tracking region of the range exists and none of its pages is
	// CPU-dirty, read without the region locks. GuestGpu thread only (BufferCache::SyncFreeSkip
	// checks it and documents why a stale answer is safe).
	[[nodiscard]] bool IsRegionCpuCleanFast(uint64_t vaddr, uint64_t size);
	// The page manager behind this tracker. The buffer cache opens the batch and the pass scope of
	// one dirty-range pass on it (gates "protbatch" / "protbatch2"); nothing else reaches past this.
	[[nodiscard]] PageManager& Pages() noexcept { return m_page_manager; }
	// Gate "protbatch2": applies what another caller left pending on a range, see
	// PageManager::FlushProtection.
	void FlushProtection(uint64_t vaddr, uint64_t size) { m_page_manager.FlushProtection(vaddr, size); }
	// Gate "pbcheck", see PageManager::VerifyProtection.
	void VerifyProtection(uint64_t vaddr, uint64_t size) { m_page_manager.VerifyProtection(vaddr, size); }
	// Snapshot without clearing bits or changing protection. Missing regions are CPU-dirty,
	// just as when a manager is first created. Callers must recheck/upload after releasing locks.
	void CollectCpuModifiedRanges(uint64_t vaddr, uint64_t size, std::vector<GuestRange>& ranges);
	void               MarkRegionAsCpuModified(uint64_t vaddr, uint64_t size);
	void               MarkRegionAsGpuModified(uint64_t vaddr, uint64_t size);
	void               UnmarkRegionAsGpuModified(uint64_t vaddr, uint64_t size);
	void               MarkRegionAsStaleReadable(uint64_t vaddr, uint64_t size);
	void               UntrackMemory(uint64_t vaddr, uint64_t size);
	// Removes protection from a range and flushes GPU-owned data when required.
	// batch_protect (gate "protbatch"): the host protection change of the invalidation is applied
	// after the region lock is released and before on_flush and the return; the flush of the whole
	// range afterwards also waits for (or makes) a change another thread deferred on these pages,
	// so a faulting instruction never resumes on a page that is logically writable while its host
	// protection still lags (see PageManager::Impl::Region::apply).
	template <typename Flush>
	void InvalidateRegion(uint64_t vaddr, uint64_t size, Flush&& on_flush,
						  bool batch_protect = false) noexcept {
		static_assert(std::is_invocable_v<Flush&>);
		CheckNotInUploadCallback();

		Iterate<false>(vaddr, size, [&](RegionManager* manager, uint64_t offset, uint64_t bytes) {
			bool should_flush = false;
			{
			// Its destructor applies what it deferred: after the region lock, before on_flush.
			PageManager::BatchScope batch(m_page_manager, batch_protect);
			should_flush = [&] {
				// Perform both the GPU modification check and CPU state change with the lock in
				// case the GPU thread is racing to mark the page modified. If a flush is needed,
				// on_flush performs the CPU state change.
				std::scoped_lock lock(manager->lock);
				if (manager->IsModified<DirtySource::Gpu>(offset, bytes)) {
					return true;
				}
				manager->ChangeState<DirtySource::Cpu, true>(manager->GetCpuAddr() + offset, bytes);
				return false;
			}();
			}
			if (batch_protect) {
				m_page_manager.FlushProtection(manager->GetCpuAddr() + offset, bytes);
			}
			if (should_flush) {
				on_flush();
			}
		});
	}
	// Knob "faultkb": a CPU write fault at `fault_vaddr` opens, in one host protection change,
	// every page of [window_begin, window_begin + window_size) contiguous with the faulting page
	// that holds no GPU-owned bytes (RegionManager::GpuCleanRunAround), instead of one fault per
	// page. The window holds the fault and lies inside its tracking region (the caller aligns it
	// to a power of two). A GPU-dirty faulting page opens nothing else and flushes as
	// InvalidateRegion(fault_vaddr, 1) does; `on_flush` must read the faulting byte only. The
	// opened pages are ordinary CPU-dirty pages: the next synchronization uploads them and arms
	// their watchers again (ForEachUploadRange), with the copy-after-protection order of any
	// written page. Order of the scope and the lock as in InvalidateRegion.
	template <typename Flush>
	void InvalidateWriteFault(uint64_t fault_vaddr, uint64_t window_begin, uint64_t window_size,
	                          Flush&& on_flush, bool batch_protect = false) noexcept {
		static_assert(std::is_invocable_v<Flush&>);
		CheckNotInUploadCallback();
		auto* manager = WriteFaultManager(fault_vaddr, window_begin, window_size);
		if (manager == nullptr) {
			return; // as InvalidateRegion: no tracking region, no watcher of this tracker
		}
		uint64_t open_begin   = fault_vaddr & ~(TRACKER_PAGE_SIZE - 1);
		uint64_t open_size    = TRACKER_PAGE_SIZE;
		bool     should_flush = false;
		{
			// Destroyed in reverse order: the region lock first, then the scope applies what it
			// deferred - after the lock, before the flush below and before on_flush.
			PageManager::BatchScope batch(m_page_manager, batch_protect);
			std::scoped_lock        lock(manager->lock);
			if (manager->IsModified<DirtySource::Gpu>(fault_vaddr - manager->GetCpuAddr(), 1)) {
				should_flush = true;
			} else {
				uint64_t   armed = 0;
				const auto run   = manager->GpuCleanRunAround(fault_vaddr, window_begin, window_size,
				                                              Common::FrameStats::Enabled() ? &armed : nullptr);
				open_begin       = run.first;
				open_size        = run.second;
				manager->ChangeState<DirtySource::Cpu, true>(open_begin, open_size);
				Common::FrameStats::Add(Common::FrameStats::Counter::FaultWinArmed, armed);
				Common::FrameStats::Add(Common::FrameStats::Counter::FaultWidened,
				                        open_size / TRACKER_PAGE_SIZE - 1u);
			}
		}
		if (batch_protect) {
			m_page_manager.FlushProtection(open_begin, open_size);
		}
		if (should_flush) {
			on_flush();
		}
	}
	// fw_win_armed while the knob is at one page (diagnostic, read only): how many pages
	// InvalidateWriteFault would open beyond the faulting one that are CPU-clean now. 0 for a window
	// outside the tracked address space, a missing region or a GPU-dirty faulting page.
	[[nodiscard]] uint64_t WriteFaultArmedPages(uint64_t fault_vaddr, uint64_t window_begin,
	                                            uint64_t window_size) {
		CheckNotInUploadCallback();
		if (!GuestRange {window_begin, window_size}.Valid()) {
			return 0;
		}
		auto* manager = WriteFaultManager(fault_vaddr, window_begin, window_size);
		if (manager == nullptr) {
			return 0;
		}
		std::scoped_lock lock(manager->lock);
		if (manager->IsModified<DirtySource::Gpu>(fault_vaddr - manager->GetCpuAddr(), 1)) {
			return 0;
		}
		uint64_t armed = 0;
		(void)manager->GpuCleanRunAround(fault_vaddr, window_begin, window_size, &armed);
		return armed;
	}
	// Gate "stkstat" (session 57, A1 ceiling; statistics only), RegionManager::NoteWriteFaultStat for
	// a CPU write fault: 2 this frame, 1 the previous frame, 0 otherwise or without a tracking region.
	// Any thread, from the fault handler: no lock, no allocation.
	[[nodiscard]] uint32_t NoteWriteFaultStat(uint64_t fault_vaddr, uint32_t frame) noexcept {
		if (fault_vaddr >= TRACKER_ADDRESS_SIZE) {
			return 0;
		}
		auto* manager = m_regions[fault_vaddr / TRACKER_REGION_SIZE].load(std::memory_order_acquire);
		return manager == nullptr ? 0 : manager->NoteWriteFaultStat(fault_vaddr, frame);
	}
	// Gate "stkstat": RegionManager::StickyCandidatePages over the regions of a range (missing regions
	// hold none, none is created). GuestGpu thread only.
	[[nodiscard]] uint64_t StickyCandidatePages(uint64_t vaddr, uint64_t size, uint32_t frame, bool any) {
		ValidateRange(vaddr, size);
		uint64_t pages     = 0;
		uint64_t remaining = size;
		uint64_t index     = vaddr / TRACKER_REGION_SIZE;
		uint64_t offset    = vaddr % TRACKER_REGION_SIZE;
		while (remaining != 0) {
			const auto  bytes   = std::min(TRACKER_REGION_SIZE - offset, remaining);
			const auto* manager = m_regions[index].load(std::memory_order_acquire);
			if (manager != nullptr) {
				pages += manager->StickyCandidatePages(manager->GetCpuAddr() + offset, bytes, frame, any);
				if (any && pages != 0) {
					return pages;
				}
			}
			remaining -= bytes;
			offset = 0;
			index++;
		}
		return pages;
	}
#if KYTY_BUILD == KYTY_BUILD_DEBUG
	void ValidateGpuDirtyPages(const RangeSet& dirty, uint64_t vaddr, uint64_t size,
	                           const char* operation) const noexcept;
	void ValidateGpuDirtyOwnership(const RangeSet& dirty, uint64_t vaddr, uint64_t size,
	                               const char* operation);
#else
	void ValidateGpuDirtyPages(const RangeSet&, uint64_t, uint64_t, const char*) const noexcept {}
	void ValidateGpuDirtyOwnership(const RangeSet&, uint64_t, uint64_t, const char*) {}
#endif

	template <bool clear, typename Func>
	void ForEachDownloadRange(uint64_t vaddr, uint64_t size, Func&& func) {
		static_assert(std::is_nothrow_invocable_v<Func&, uint64_t, uint64_t>);
		CheckNotInUploadCallback();
		Iterate<false>(vaddr, size, [&](RegionManager* manager, uint64_t offset, uint64_t bytes) {
			std::scoped_lock lock(manager->lock);
			const auto       address = manager->GetCpuAddr() + offset;
			manager->template ForEachModifiedRange<DirtySource::Gpu, false>(address, bytes, func);
			if constexpr (clear) {
				manager->template ChangeState<DirtySource::Gpu, false>(address, bytes);
			}
		});
	}

	// pass_batch (gate "protbatch2", read-only uploads only): the caller owns both the batch scope
	// and the flush of a whole pass of uploads and copies nothing until that flush returned
	// (BufferCache::SynchronizeBuffersOfDirtyRangesBatched). Opening a scope here would become the
	// innermost one and undo the merge, and flushing here would be one flush per buffer again.
	// Returns true (gate "armdefer") when pages of the range were left CPU-dirty for a later
	// synchronization to settle: the caller must not record the upload as current.
	template <typename RangeFunc, typename UploadFunc>
	bool ForEachUploadRange(uint64_t vaddr, uint64_t size, bool is_written, RangeFunc&& range_func,
	                        UploadFunc&& upload_func, bool batch_protect = false,
	                        const StickyUploadStat* sticky_stat = nullptr, bool pass_batch = false) {
		static_assert(std::is_nothrow_invocable_v<RangeFunc&, uint64_t, uint64_t>);
		static_assert(std::is_nothrow_invocable_v<UploadFunc&>);
		CheckNotInUploadCallback();
		if (pass_batch && is_written) {
			EXIT("upload pass batch on a written range\n");
		}
		// Session 60, gate "armdefer" (read-only uploads outside a pass): the write watchers are
		// armed by the protection worker, see RegionManager::ForEachUploadRangeArmDeferred.
		const bool arm_defer = !is_written && !pass_batch &&
		                       Common::Gates::Enabled(Common::Gates::Gate::ArmDefer) &&
		                       PageManager::DeferEnabled();
		const bool arm_verify =
		    arm_defer && Common::Gates::Enabled(Common::Gates::Gate::ArmDeferCheck);
		bool provisional = false;
		Iterate<true>(vaddr, size, [](RegionManager*, uint64_t, uint64_t) {});
		const auto* previous_upload_owner = std::exchange(s_upload_owner, this);
		{
			// batch_protect (gate "protbatch", read-only uploads only): the write watchers armed
			// by clearing the CPU-dirty bits are applied after every region lock is released and
			// BEFORE upload_func copies the bytes, so a guest write either precedes the protection
			// and is part of the copy, or faults. Written uploads keep everything under the lock.
			PageManager::BatchScope batch(m_page_manager, batch_protect && !is_written && !pass_batch);
			Iterate<false>(vaddr, size, [&](RegionManager* manager, uint64_t offset, uint64_t bytes) {
				manager->lock.lock();
				if (sticky_stat != nullptr && !is_written) {
					// Gate "stkstat": statistics of the pages the call below arms again.
					manager->NoteUploadStat(manager->GetCpuAddr() + offset, bytes, *sticky_stat);
				}
				if (arm_defer) {
					if (manager->ForEachUploadRangeArmDeferred(manager->GetCpuAddr() + offset, bytes,
					                                           arm_verify, range_func)) {
						provisional = true;
					}
				} else {
					manager->ForEachModifiedRange<DirtySource::Cpu, true>(
					    manager->GetCpuAddr() + offset, bytes, range_func);
				}
				if (!is_written) {
					manager->lock.unlock();
				}
			});
			if (!pass_batch) {
				batch.Flush();
				if (!is_written && !arm_defer) {
					// Whatever the scope held, and whether or not the gate is on: a page of this
					// range may carry a deferred protection of another caller (the texture cache
					// arms its watchers through the protection worker), and the copy below must not
					// read a page the host still lets the guest write. The scope only covers its
					// first regions.
					Iterate<false>(vaddr, size,
					               [&](RegionManager* manager, uint64_t offset, uint64_t bytes) {
						               m_page_manager.FlushProtection(manager->GetCpuAddr() + offset,
						                                              bytes);
					               });
				} else if (arm_defer) {
					// A page copied under a lagging protection keeps its dirty bit (whoever's
					// pending change it is) and is copied again once the protection is in effect.
					Common::FrameStats::Add(Common::FrameStats::Counter::ArmFlushSkips, 1);
				}
			}
		}
		upload_func();
		if (is_written) {
			Iterate<false>(vaddr, size,
			               [](RegionManager* manager, uint64_t offset, uint64_t bytes) {
				               manager->template ChangeState<DirtySource::Gpu, true>(
				                   manager->GetCpuAddr() + offset, bytes);
				               manager->lock.unlock();
			               });
		}
		s_upload_owner = previous_upload_owner;
		return provisional;
	}

private:
	static constexpr size_t REGION_COUNT = TRACKER_ADDRESS_SIZE / TRACKER_REGION_SIZE;
	inline static thread_local const MemoryTracker* s_upload_owner = nullptr;

	// The tracking region of a write-fault window, nullptr while it does not exist. The window must
	// hold the faulting address and lie inside one tracking region.
	RegionManager* WriteFaultManager(uint64_t fault_vaddr, uint64_t window_begin, uint64_t window_size) {
		ValidateRange(window_begin, window_size);
		const auto index = window_begin / TRACKER_REGION_SIZE;
		if (fault_vaddr < window_begin || fault_vaddr - window_begin >= window_size ||
		    (window_begin + window_size - 1) / TRACKER_REGION_SIZE != index) {
			EXIT("invalid write-fault window\n");
		}
		return m_regions[index].load(std::memory_order_acquire);
	}

	void CheckNotInUploadCallback() const noexcept {
		if (s_upload_owner == this) {
			EXIT("memory tracker re-entered from upload callback\n");
		}
	}

	template <bool create, typename Func>
	bool Iterate(uint64_t vaddr, uint64_t size, Func&& func) {
		ValidateRange(vaddr, size);
		using Result = std::invoke_result_t<Func, RegionManager*, uint64_t, uint64_t>;
		constexpr bool returns_bool = std::is_same_v<Result, bool>;
		uint64_t       remaining    = size;
		uint64_t       index        = vaddr / TRACKER_REGION_SIZE;
		uint64_t       offset       = vaddr % TRACKER_REGION_SIZE;
		while (remaining != 0) {
			const auto bytes   = std::min(TRACKER_REGION_SIZE - offset, remaining);
			auto*      manager = m_regions[index].load(std::memory_order_acquire);
			if (manager == nullptr && create) {
				manager = GetOrCreateRegion(index);
			}
			if (manager != nullptr) {
				if constexpr (returns_bool) {
					if (func(manager, offset, bytes)) {
						return true;
					}
				} else {
					func(manager, offset, bytes);
				}
			}
			remaining -= bytes;
			offset = 0;
			index++;
		}
		return false;
	}

	static void    ValidateRange(uint64_t vaddr, uint64_t size);
	RegionManager* GetOrCreateRegion(uint64_t index);

	std::unique_ptr<std::atomic<RegionManager*>[]> m_regions;
	std::atomic<uint64_t>                         m_cpu_epoch {1};
	std::vector<std::unique_ptr<RegionManager>>    m_region_storage;
	std::mutex                                     m_region_mutex;
	PageManager&                                   m_page_manager;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_MEMORYTRACKER_H_
