#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_MEMORYTRACKER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_MEMORYTRACKER_H_

#include "common/assert.h"
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

	template <typename RangeFunc, typename UploadFunc>
	void ForEachUploadRange(uint64_t vaddr, uint64_t size, bool is_written, RangeFunc&& range_func,
	                        UploadFunc&& upload_func, bool batch_protect = false) {
		static_assert(std::is_nothrow_invocable_v<RangeFunc&, uint64_t, uint64_t>);
		static_assert(std::is_nothrow_invocable_v<UploadFunc&>);
		CheckNotInUploadCallback();
		Iterate<true>(vaddr, size, [](RegionManager*, uint64_t, uint64_t) {});
		const auto* previous_upload_owner = std::exchange(s_upload_owner, this);
		{
			// batch_protect (gate "protbatch", read-only uploads only): the write watchers armed
			// by clearing the CPU-dirty bits are applied after every region lock is released and
			// BEFORE upload_func copies the bytes, so a guest write either precedes the protection
			// and is part of the copy, or faults. Written uploads keep everything under the lock.
			PageManager::BatchScope batch(m_page_manager, batch_protect && !is_written);
			Iterate<false>(vaddr, size, [&](RegionManager* manager, uint64_t offset, uint64_t bytes) {
				manager->lock.lock();
				manager->ForEachModifiedRange<DirtySource::Cpu, true>(manager->GetCpuAddr() + offset,
																	  bytes, range_func);
				if (!is_written) {
					manager->lock.unlock();
				}
			});
			batch.Flush();
			if (!is_written) {
				// Whatever the scope held, and whether or not the gate is on: a page of this range
				// may carry a deferred protection of another caller (the texture cache arms its
				// watchers through the protection worker), and the copy below must not read a page
				// the host still lets the guest write. The scope only covers its first regions.
				Iterate<false>(vaddr, size,
				               [&](RegionManager* manager, uint64_t offset, uint64_t bytes) {
					               m_page_manager.FlushProtection(manager->GetCpuAddr() + offset,
					                                              bytes);
				               });
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
	}

private:
	static constexpr size_t REGION_COUNT = TRACKER_ADDRESS_SIZE / TRACKER_REGION_SIZE;
	inline static thread_local const MemoryTracker* s_upload_owner = nullptr;

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
