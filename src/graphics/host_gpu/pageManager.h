#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_PAGEMANAGER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_PAGEMANAGER_H_

#include "common/common.h"
#include "graphics/host_gpu/regionDefinitions.h"

#include <memory>

namespace Libs::Graphics {

enum class PageFaultAccess { Read, Write, Execute, Unknown };

class PageManager final {
public:
	PageManager();
	// The owner must stop all PageManager callers before destruction.
	~PageManager();

	KYTY_CLASS_NO_COPY(PageManager);

	[[nodiscard]] uint64_t GetPageSize() const;

	template <bool track>
	void UpdatePageWatchers(uint64_t vaddr, uint64_t size);
	template <bool track, bool is_read = false>
	void UpdatePageWatchersForRegion(uint64_t base_addr, RegionBits& mask);

	// Adds write watchers like UpdatePageWatchers<true>, but the host protection change
	// (VirtualProtect, ~60-100 ns per page, serialized in the kernel) is applied by a worker
	// thread instead of the caller. Tracker state is updated synchronously, so untracking and
	// read-watcher changes stay correct; only the moment the pages become read-only is deferred.
	// A CPU write to such a page before the worker gets to it is not observed, so the caller must
	// DrainDeferredProtection() before the guest can learn that the GPU consumed the data (flip).
	// Falls back to the synchronous path when KYTY_ASYNC_PROTECT=0.
	void UpdatePageWatchersDeferred(uint64_t vaddr, uint64_t size);
	// Waits until every deferred protection change has been applied.
	void DrainDeferredProtection();

private:
	struct Impl;
	std::unique_ptr<Impl> m_impl;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_PAGEMANAGER_H_
