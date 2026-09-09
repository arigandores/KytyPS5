#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_CACHE_HOSTIMPORT_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_CACHE_HOSTIMPORT_H_

#include "common/common.h"
#include "graphics/host_gpu/vulkanCommon.h"

#include <atomic>
#include <cstdint>
#include <mutex>
#include <vector>

namespace Libs::Graphics {

struct GraphicContext;

// Guest direct memory as Vulkan buffers (VK_EXT_external_memory_host). The kernel keeps one
// writable alias of the whole direct-memory backing (GuestBackingStore); every byte of direct
// memory has a fixed address in it no matter where the guest maps it. The alias is imported in
// fixed chunks (KYTY_HOST_IMPORT_MB, default 512) on first use, each chunk one VkBuffer, so the
// GPU reads texture data straight out of guest pages: no memcpy into a staging ring, and no
// second pass over DRAM (a scene cut of ASTRO BOT moves 600-950 MB; the copy pool and the GPU
// reads of the staging ring shared one laptop memory bus at ~10 GB/s each).
// Importing pins the pages, and the driver holds its device lock for the whole import (20-200
// ms per 512 MB: page commit, page-table population), which stalls the GuestGpu thread's
// submits. So by default every chunk is imported once at start-up, before the guest runs
// (KYTY_HOST_IMPORT_PRELOAD=1; auto when the machine has at least backing + 6 GB of RAM, since
// the whole backing becomes resident and locked). KYTY_HOST_IMPORT_PRELOAD=0: chunks are imported
// on a background thread at first use and the first images in a chunk take the staging path
// (KYTY_HOST_IMPORT_SYNC=1 imports on the caller instead).
// KYTY_HOST_IMPORT=0 turns the import off (the device extension is not enabled either).
class HostImport {
public:
	explicit HostImport(GraphicContext& graphics);
	~HostImport();
	KYTY_CLASS_NO_COPY(HostImport);

	struct Region {
		vk::Buffer buffer;
		uint64_t   offset = 0; // offset in `buffer`
		uint64_t   size   = 0; // bytes available from `offset` (may be less than requested)
	};

	[[nodiscard]] bool Available() const noexcept { return m_available; }
	// The imported buffer holding [backing_offset, backing_offset + size), or as much of it as
	// lies in one chunk. False when the chunk is not imported yet (the import is started) or the
	// import failed; the caller takes the staging path.
	[[nodiscard]] bool Resolve(uint64_t backing_offset, uint64_t size, Region* region);

private:
	enum class State : uint8_t { Empty, Importing, Ready, Failed };

	struct Chunk {
		vk::Buffer       buffer = nullptr;
		vk::DeviceMemory memory = nullptr;
		State            state  = State::Empty;
	};

	void ImportChunk(size_t index);
	void Preload();
	void TouchChunk(size_t index) const;

	GraphicContext&    m_graphics;
	uint64_t           m_base       = 0;
	uint64_t           m_size       = 0;
	uint64_t           m_chunk_size = 0;
	bool               m_available  = false;
	bool               m_sync       = false;
	std::mutex         m_mutex;
	std::atomic<int>   m_in_flight {0};
	std::vector<Chunk> m_chunks;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_CACHE_HOSTIMPORT_H_
