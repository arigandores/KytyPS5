#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_BUFFERCACHE_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_BUFFERCACHE_H_

#include "common/abi.h"
#include "common/common.h"
#include "common/lruCache.h"
#include "common/slotVector.h"
#include "graphics/host_gpu/memoryTracker.h"
#include "graphics/host_gpu/rangeSet.h"
#include "graphics/host_gpu/renderer/cache/faultManager.h"
#include "graphics/host_gpu/renderer/cache/multiLevelPageTable.h"
#include "graphics/host_gpu/renderer/cache/streamBuffer.h"

#include <map>
#include <mutex>
#include <span>
#include <unordered_map>
#include <utility>
#include <vector>

namespace Libs::Graphics {

struct GraphicContext;
class CommandScheduler;
class TextureCache;

using BufferId = Common::SlotId;
inline constexpr BufferId NULL_BUFFER_ID {0};

class BufferCache {
public:
	static constexpr uint32_t CACHING_PAGEBITS  = 14;
	static constexpr uint64_t CACHING_PAGESIZE  = uint64_t {1} << CACHING_PAGEBITS;
	static constexpr uint64_t CACHING_NUMPAGES  = uint64_t {1} << (40 - CACHING_PAGEBITS);
	static constexpr uint64_t BDA_PAGETABLE_SIZE =
	    CACHING_NUMPAGES * sizeof(vk::DeviceAddress);

	BufferCache(GraphicContext& graphics, CommandScheduler& scheduler, PageManager& page_manager,
	            TextureCache& texture_cache);
	~BufferCache();
	KYTY_CLASS_NO_COPY(BufferCache);

	void                   InvalidateMemory(uint64_t vaddr, uint64_t size);
	void                   ReadMemory(uint64_t vaddr, uint64_t size, bool is_write = false);
	[[nodiscard]] Buffer&  GetBuffer(BufferId id) { return m_slot_buffers[id]; }
	[[nodiscard]] BufferId FindBuffer(uint64_t vaddr, uint64_t size);
	[[nodiscard]] std::pair<Buffer*, uint64_t> ObtainBuffer(uint64_t vaddr, uint64_t size,
	                                                        bool     is_written,
	                                                        bool     is_texel_buffer = false,
	                                                        BufferId id              = {});
	[[nodiscard]] StreamBuffer&                GetUtilityBuffer(MemoryUsage usage) noexcept {
		switch (usage) {
			case MemoryUsage::Upload: return m_staging_buffer;
			case MemoryUsage::Stream: return m_stream_buffer;
			case MemoryUsage::Download: return m_download_buffer;
			case MemoryUsage::DeviceLocal: return m_device_buffer;
		}
		EXIT("BufferCache: invalid utility-buffer usage\n");
	}
	[[nodiscard]] const Buffer* GetGdsBuffer() const noexcept { return &m_gds_buffer; }
	[[nodiscard]] Buffer* GetBdaPageTableBuffer() noexcept { return &m_bda_pagetable_buffer; }
	[[nodiscard]] Buffer* GetFaultBuffer() noexcept { return m_fault_manager.GetFaultBuffer(); }
	[[nodiscard]] std::pair<Buffer*, uint64_t> ObtainBufferForImage(uint64_t vaddr, uint64_t size);
	static void TraceImageUpload(uint64_t vaddr, uint64_t size, const char* path);
	void FillBuffer(uint64_t vaddr, uint64_t size, uint32_t value, bool is_gds);
	void CopyBuffer(uint64_t dst_vaddr, uint64_t src_vaddr, uint64_t size, bool dst_gds,
	                bool src_gds);
	// Cache-index and exact dirty-range queries require GPU-thread serialization.
	[[nodiscard]] bool IsRegionRegistered(uint64_t vaddr, uint64_t size);
	[[nodiscard]] bool HasGpuDirtyBytes(uint64_t vaddr, uint64_t size);
	[[nodiscard]] bool IsRegionCpuModified(uint64_t vaddr, uint64_t size);
	[[nodiscard]] bool IsRegionGpuModified(uint64_t vaddr, uint64_t size);
	void               ProcessFaultBuffer();
	void               SynchronizeBuffersInRange(uint64_t vaddr, uint64_t size);
	void               RunGarbageCollector();
	// Records asynchronous downloads of the GPU-dirty parts of regions the CPU keeps reading
	// after the GPU wrote them, so that the next CPU read finds the page clean instead of
	// draining the GPU queue on the GPU thread. Called at the end of every submission slice.
	void PrefetchHotReadbacks();
	// Texture streaming prefetch: file reads queue their destination range (any thread); the GPU
	// thread synchronizes queued ranges into native buffers under a per-frame budget so that the
	// image upload at a scene cut finds a synchronized owner instead of copying guest memory.
	void NoteStreamedRead(uint64_t vaddr, uint64_t size);
	void PrefetchStreamedRanges();
	// Drops every cached buffer intersecting the range (GPU-written bytes are downloaded first) and
	// untracks its pages: used when guest memory becomes a thread stack.
	void DeleteBuffersOverlapping(uint64_t vaddr, uint64_t size);
	// A readback split into the GPU-thread part (record the copies, submit) and the waiting part
	// (done by the guest thread that needs the data), see ReadMemory.
	struct ReadbackPiece {
		uint64_t address = 0;
		uint64_t size    = 0;
		uint64_t offset  = 0; // in the download ring, relative to base_offset
	};
	struct AsyncReadback {
		std::vector<ReadbackPiece> pieces;
		uint8_t*                   mapped      = nullptr;
		uint64_t                   base_offset = 0;
		uint64_t                   tick        = 0;
		uint64_t                   seq         = 0;
	};

private:
	friend struct BufferCacheTestAccess;

	using BufferMap = std::map<uint64_t, BufferId>;
	struct OverlapResult {
		BufferMap::iterator first;
		BufferMap::iterator last;
		uint64_t            begin;
		uint64_t            end;
		bool                has_stream_leap;
	};

	struct DownloadCopy;
	using PageTable = MultiLevelPageTable<BufferId, CACHING_PAGEBITS, 40, 16>;
	static_assert(CACHING_PAGESIZE == (uint64_t {1} << PageTable::kPageBits));
	static constexpr uint64_t               DOWNLOAD_ALIGNMENT = 64;
	[[nodiscard]] static constexpr uint64_t AlignDownload(uint64_t size) noexcept {
		return (size + DOWNLOAD_ALIGNMENT - 1) & ~(DOWNLOAD_ALIGNMENT - 1);
	}
	[[nodiscard]] static std::pair<uint64_t, uint64_t> DownloadEnvelope(const DownloadCopy& copy);
	void WriteDataBuffer(Buffer& buffer, uint64_t address, const void* source, uint64_t size);
	void TouchBuffer(Buffer& buffer);
	[[nodiscard]] OverlapResult ResolveOverlaps(uint64_t vaddr, uint64_t size);
	void JoinOverlap(BufferId new_id, BufferId overlap_id, bool accumulate_stream_score);
	[[nodiscard]] BufferId CreateBuffer(uint64_t vaddr, uint64_t size);
	void                   Register(BufferId id);
	void Unregister(BufferId id);
	template <bool insert>
	void ChangeRegister(BufferId id);
	void DeleteBuffer(BufferId id);
	[[nodiscard]] bool SynchronizeBuffer(Buffer& buffer, uint64_t vaddr, uint64_t size,
	                                     bool is_written, bool is_texel_buffer);
	[[nodiscard]] vk::Buffer UploadCopies(Buffer& buffer, std::span<vk::BufferCopy> copies,
	                                      uint64_t total_size);
	[[nodiscard]] bool SynchronizeBufferFromImage(Buffer& buffer, uint64_t vaddr, uint64_t size);
	void DownloadBufferMemory(std::span<const DownloadCopy> copies);
	void ReadMemoryOnGpu(uint64_t vaddr, uint64_t size, bool is_write);
	[[nodiscard]] AsyncReadback BeginAsyncReadback(uint64_t vaddr, uint64_t size);
	bool                        FinishAsyncReadback(const AsyncReadback& job);
	// GPU thread: make the GPU-dirty pages around a CPU read readable at once (stale data) and
	// schedule the download that brings the completed GPU data in later. See ReadMemory.
	void ServeStaleRead(uint64_t vaddr, uint64_t size);
	void ApplyReadbackPieces(const std::vector<ReadbackPiece>& pieces, const uint8_t* data,
	                         uint64_t seq);

	GraphicContext&                                   m_graphics;
	CommandScheduler&                                 m_scheduler;
	FaultManager                                      m_fault_manager;
	Buffer                                            m_gds_buffer;
	Buffer                                            m_bda_pagetable_buffer;
	Buffer                                            m_bda_null_page;
	bool                                              m_bda_null_page_ready = false;
	Common::SlotVector<Buffer>                        m_slot_buffers;
	Common::LeastRecentlyUsedCache<BufferId, uint64_t> m_lru_cache;
	BufferMap                                         m_buffers;
	PageTable                                         m_page_table;
	RangeSet                                          m_gpu_modified_ranges;
	MemoryTracker                                     m_memory_tracker;
	StreamBuffer                                      m_staging_buffer;
	StreamBuffer                                      m_stream_buffer;
	StreamBuffer                                      m_download_buffer;
	StreamBuffer                                      m_device_buffer;
	TextureCache&                                     m_texture_cache;
	uint64_t                                          m_total_used_memory  = 0;
	uint64_t m_trigger_gc_memory  = 1ull * 1024 * 1024 * 1024;
	uint64_t m_critical_gc_memory = 2ull * 1024 * 1024 * 1024;
	uint64_t m_gc_tick            = 0;

	// Readback prefetch state (PrefetchHotReadbacks). A hot region is the 512 KB window around
	// an address whose CPU read had to drain the GPU; GPU writes are sequence-stamped per 64 KB
	// bucket so a completed prefetch only clears the dirty state when no newer write landed.
	struct HotRegion {
		uint64_t begin          = 0;
		uint64_t end            = 0;
		uint32_t hits           = 0;
		int      last_hit_frame = 0;
		bool     in_flight      = false;
	};
	static constexpr uint32_t HotBucketBits = 16;
	std::unordered_map<uint64_t, HotRegion> m_hot_regions;
	std::unordered_map<uint64_t, uint64_t>  m_bucket_write_seq;
	uint64_t                                m_gpu_write_seq   = 0;
	uint64_t                                m_large_write_seq = 0;
	void                   NoteGpuWrite(uint64_t vaddr, uint64_t size);

 public:
	// Sequence number of the last GPU write to the 64 KB buckets of the range (include_large: also the
	// floor set by any write larger than 16 MB, which is not tracked per bucket).
	[[nodiscard]] uint64_t LastGpuWriteSeq(uint64_t vaddr, uint64_t size, bool include_large = true) const;

 private:

	// Stream prefetch queue (NoteStreamedRead / PrefetchStreamedRanges).
	std::mutex                                     m_streamed_mutex;
	std::vector<std::pair<uint64_t, uint64_t>>     m_streamed_ranges;
	std::vector<std::pair<uint64_t, uint64_t>>     m_streamed_pending;
	int                                            m_streamed_frame    = -1;
	uint64_t                                       m_streamed_spent_ns = 0;
	uint64_t                                       m_prefetch_pending_bytes = 0;
	void                                           ClearPrefetchPending(Buffer& buffer);
	[[nodiscard]] bool IsRegionFullyRegistered(uint64_t vaddr, uint64_t size);
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_BUFFERCACHE_H_
