#include "graphics/host_gpu/memoryTracker.h"

#include "common/alignment.h"
#include "common/assert.h"

namespace Libs::Graphics {

static_assert(std::atomic<void*>::is_always_lock_free);

MemoryTracker::MemoryTracker(PageManager& page_manager): m_page_manager(page_manager) {
	m_regions = std::make_unique<std::atomic<RegionManager*>[]>(REGION_COUNT);
	const MemoryTracker* expected = nullptr;
	s_primary.compare_exchange_strong(expected, this, std::memory_order_acq_rel);
}

MemoryTracker::~MemoryTracker() {
	const MemoryTracker* self = this;
	s_primary.compare_exchange_strong(self, nullptr, std::memory_order_acq_rel);
}

#if KYTY_BUILD == KYTY_BUILD_DEBUG
void MemoryTracker::ValidateGpuDirtyPages(const RangeSet& dirty, uint64_t vaddr, uint64_t size,
                                          const char* operation) const noexcept {
	if (!GuestRange {vaddr, size}.Valid() || (vaddr & (TRACKER_PAGE_SIZE - 1)) != 0 ||
	    (size & (TRACKER_PAGE_SIZE - 1)) != 0) {
		EXIT("MemoryTracker: invalid dirty-page validation range\n");
	}
	for (auto page = vaddr; page < vaddr + size; page += TRACKER_PAGE_SIZE) {
		if (!dirty.Intersects(page, TRACKER_PAGE_SIZE)) {
			EXIT("MemoryTracker: GPU-dirty tracker page has no dirty bytes, operation=%s "
			     "addr=0x%016" PRIx64 "\n",
			     operation, page);
		}
	}
}

void MemoryTracker::ValidateGpuDirtyOwnership(const RangeSet& dirty, uint64_t vaddr, uint64_t size,
                                              const char* operation) {
	ValidateRange(vaddr, size);
	const auto begin = Common::AlignDown(vaddr, TRACKER_PAGE_SIZE);
	const auto end   = Common::AlignUp(vaddr + size, TRACKER_PAGE_SIZE);
	for (auto page = begin; page < end; page += TRACKER_PAGE_SIZE) {
		const bool has_dirty_bytes = dirty.Intersects(page, TRACKER_PAGE_SIZE);
		if (IsRegionGpuModified(page, TRACKER_PAGE_SIZE) != has_dirty_bytes) {
			EXIT("MemoryTracker: tracker and byte ownership disagree, operation=%s "
			     "addr=0x%016" PRIx64 "\n",
			     operation, page);
		}
	}
}
#endif

void MemoryTracker::ValidateRange(uint64_t vaddr, uint64_t size) {
	if (!GuestRange {vaddr, size}.Valid()) {
		EXIT("invalid memory tracker range\n");
	}
}

RegionManager* MemoryTracker::GetOrCreateRegion(uint64_t index) {
	if (auto* manager = m_regions[index].load(std::memory_order_acquire); manager != nullptr) {
		return manager;
	}
	std::lock_guard lock(m_region_mutex);
	if (auto* manager = m_regions[index].load(std::memory_order_acquire); manager != nullptr) {
		return manager;
	}
	auto  manager = std::make_unique<RegionManager>(m_page_manager, index * TRACKER_REGION_SIZE, m_cpu_epoch);
	auto* ptr     = manager.get();
	m_region_storage.push_back(std::move(manager));
	m_regions[index].store(ptr, std::memory_order_release);
	return ptr;
}

bool MemoryTracker::IsRegionCpuModified(uint64_t vaddr, uint64_t size) {
	CheckNotInUploadCallback();
	return Iterate<true>(vaddr, size, [](RegionManager* manager, uint64_t offset, uint64_t bytes) {
		std::scoped_lock lock(manager->lock);
		return manager->IsModified<DirtySource::Cpu>(offset, bytes);
	});
}

bool MemoryTracker::IsRegionGpuModified(uint64_t vaddr, uint64_t size) {
	CheckNotInUploadCallback();
	return Iterate<false>(vaddr, size, [](RegionManager* manager, uint64_t offset, uint64_t bytes) {
		std::scoped_lock lock(manager->lock);
		return manager->IsModified<DirtySource::Gpu>(offset, bytes);
	});
}

bool MemoryTracker::IsRegionCpuModifiedAndGpuClean(uint64_t vaddr, uint64_t size) {
	CheckNotInUploadCallback();
	bool cpu_dirty = false;
	const bool gpu_dirty = Iterate<true>(vaddr, size, [&](RegionManager* manager, uint64_t offset, uint64_t bytes) {
		std::scoped_lock lock(manager->lock);
		if (manager->IsModified<DirtySource::Gpu>(offset, bytes)) return true;
		cpu_dirty |= manager->IsModified<DirtySource::Cpu>(offset, bytes);
		return false;
	});
	return cpu_dirty && !gpu_dirty;
}

bool MemoryTracker::IsRegionGpuModifiedFast(uint64_t vaddr, uint64_t size) {
	CheckNotInUploadCallback();
	return Iterate<false>(vaddr, size,
	                      [](RegionManager* manager, uint64_t offset, uint64_t bytes) {
		                      return manager->IsModifiedRelaxed<DirtySource::Gpu>(offset, bytes);
	                      });
}

bool MemoryTracker::IsRegionCpuModifiedAndGpuCleanFast(uint64_t vaddr, uint64_t size) {
	CheckNotInUploadCallback();
	ValidateRange(vaddr, size);
	// Same answer as the locked query, without creating the regions it walks: a region that
	// does not exist yet is CPU-dirty and has no GPU-owned bytes (that is exactly the state
	// the locked query would have created, RegionManager fills m_cpu_dirty on construction
	// and issues no protection call).
	bool     cpu_dirty = false;
	bool     untracked = false;
	uint64_t remaining = size;
	uint64_t index     = vaddr / TRACKER_REGION_SIZE;
	uint64_t offset    = vaddr % TRACKER_REGION_SIZE;
	while (remaining != 0) {
		const auto bytes   = std::min(TRACKER_REGION_SIZE - offset, remaining);
		auto*      manager = m_regions[index].load(std::memory_order_acquire);
		if (manager == nullptr) {
			untracked = true;
		} else {
			if (manager->IsModifiedRelaxed<DirtySource::Gpu>(offset, bytes)) {
				return false;
			}
			cpu_dirty |= manager->IsModifiedRelaxed<DirtySource::Cpu>(offset, bytes);
		}
		remaining -= bytes;
		offset = 0;
		index++;
	}
	return cpu_dirty || untracked;
}

bool MemoryTracker::IsRegionCpuCleanFast(uint64_t vaddr, uint64_t size) {
	CheckNotInUploadCallback();
	ValidateRange(vaddr, size);
	uint64_t remaining = size;
	uint64_t index     = vaddr / TRACKER_REGION_SIZE;
	uint64_t offset    = vaddr % TRACKER_REGION_SIZE;
	while (remaining != 0) {
		const auto bytes   = std::min(TRACKER_REGION_SIZE - offset, remaining);
		auto*      manager = m_regions[index].load(std::memory_order_acquire);
		// A missing region is CPU-dirty by definition, and the locked path would create it.
		if (manager == nullptr || manager->IsModifiedRelaxed<DirtySource::Cpu>(offset, bytes)) {
			return false;
		}
		remaining -= bytes;
		offset = 0;
		index++;
	}
	return true;
}

void MemoryTracker::CollectCpuModifiedRanges(uint64_t vaddr, uint64_t size,
                                            std::vector<GuestRange>& ranges) {
	CheckNotInUploadCallback();
	ValidateRange(vaddr, size);
	ranges.clear();
	const auto end = vaddr + size;
	const auto append = [&](uint64_t address, uint64_t bytes) noexcept {
		const auto first = std::max(address, vaddr);
		const auto last = std::min(address + bytes, end);
		if (first >= last) return;
		if (!ranges.empty() && ranges.back().End() == first) {
			ranges.back().size += last - first;
		} else {
			ranges.push_back({first, last - first});
		}
	};
	for (auto cursor = vaddr; cursor < end;) {
		const auto index = cursor / TRACKER_REGION_SIZE;
		const auto bytes = std::min(end - cursor, TRACKER_REGION_SIZE - cursor % TRACKER_REGION_SIZE);
		auto* manager = m_regions[index].load(std::memory_order_acquire);
		if (manager == nullptr) {
			append(cursor, bytes);
		} else {
			std::scoped_lock lock(manager->lock);
			manager->ForEachModifiedRange<DirtySource::Cpu, false>(cursor, bytes, append);
		}
		cursor += bytes;
	}
}

void MemoryTracker::MarkRegionAsCpuModified(uint64_t vaddr, uint64_t size) {
	CheckNotInUploadCallback();
	Iterate<true>(vaddr, size, [](RegionManager* manager, uint64_t offset, uint64_t bytes) {
		std::scoped_lock lock(manager->lock);
		manager->ChangeState<DirtySource::Cpu, true>(manager->GetCpuAddr() + offset, bytes);
	});
}

void MemoryTracker::MarkRegionAsGpuModified(uint64_t vaddr, uint64_t size) {
	CheckNotInUploadCallback();
	Iterate<true>(vaddr, size, [](RegionManager* manager, uint64_t offset, uint64_t bytes) {
		std::scoped_lock lock(manager->lock);
		manager->ChangeState<DirtySource::Gpu, true>(manager->GetCpuAddr() + offset, bytes);
	});
}

void MemoryTracker::UnmarkRegionAsGpuModified(uint64_t vaddr, uint64_t size) {
	CheckNotInUploadCallback();
	Iterate<false>(vaddr, size, [](RegionManager* manager, uint64_t offset, uint64_t bytes) {
		std::scoped_lock lock(manager->lock);
		manager->ChangeState<DirtySource::Gpu, false>(manager->GetCpuAddr() + offset, bytes);
	});
}

void MemoryTracker::MarkRegionAsStaleReadable(uint64_t vaddr, uint64_t size) {
	CheckNotInUploadCallback();
	Iterate<false>(vaddr, size, [](RegionManager* manager, uint64_t offset, uint64_t bytes) {
		std::scoped_lock lock(manager->lock);
		manager->MarkStaleReadable(manager->GetCpuAddr() + offset, bytes);
	});
}

void MemoryTracker::UntrackMemory(uint64_t vaddr, uint64_t size) {
	CheckNotInUploadCallback();
	std::vector<RegionManager*> managers;
	managers.reserve((vaddr % TRACKER_REGION_SIZE + size + TRACKER_REGION_SIZE - 1) /
	                 TRACKER_REGION_SIZE);
	Iterate<false>(vaddr, size, [&](RegionManager* manager, uint64_t, uint64_t) {
		managers.push_back(manager);
	});

	std::vector<std::unique_lock<TrackingSpinLock>> locks;
	locks.reserve(managers.size());
	for (auto* manager: managers) {
		locks.emplace_back(manager->lock);
	}
	if (Iterate<false>(vaddr, size, [](RegionManager* manager, uint64_t offset, uint64_t bytes) {
		    return manager->IsModified<DirtySource::Gpu>(offset, bytes);
	    })) {
		EXIT("cannot untrack GPU-dirty memory\n");
	}
	Iterate<false>(vaddr, size, [](RegionManager* manager, uint64_t offset, uint64_t bytes) {
		manager->ChangeState<DirtySource::Cpu, true>(manager->GetCpuAddr() + offset, bytes);
	});
}

} // namespace Libs::Graphics
