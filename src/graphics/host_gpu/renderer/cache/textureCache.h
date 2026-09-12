#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_TEXTURECACHE_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_TEXTURECACHE_H_

#include "common/abi.h"
#include "common/common.h"
#include "common/lruCache.h"
#include "common/slotVector.h"
#include "graphics/host_gpu/pageManager.h"
#include "graphics/host_gpu/regionManager.h"
#include "graphics/host_gpu/renderer/cache/multiLevelPageTable.h"
#include "graphics/host_gpu/renderer/image/blitHelper.h"
#include "graphics/host_gpu/renderer/image/image.h"
#include "graphics/host_gpu/renderer/image/tiler.h"

#include <map>
#include <string>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace Libs::Graphics {

struct GraphicContext;
class Buffer;
class BufferCache;
class CommandBuffer;
class CommandScheduler;
class RenderExecutor;
struct TextureCacheTestAccess;

class TextureCache {
public:
	enum class BindingType : uint8_t { Texture, Storage, RenderTarget, DepthTarget, VideoOut };

	struct ImageDesc {
		ImageInfo     info;
		ImageViewInfo view_info;
		BindingType   type = BindingType::Texture;
	};

	TextureCache(GraphicContext& graphics, CommandScheduler& scheduler, PageManager& page_manager,
	             BufferCache& buffer_cache);
	~TextureCache();
	KYTY_CLASS_NO_COPY(TextureCache);

	[[nodiscard]] ImageId       FindImage(ImageDesc& desc, bool exact_format = false);
	void                        UpdateImage(ImageId id);
	[[nodiscard]] ImageId       FindImageFromRange(uint64_t address, uint64_t size,
	                                               bool ensure_valid = true);
	[[nodiscard]] vk::ImageView FindTexture(ImageId id, const ImageDesc& desc);
	[[nodiscard]] vk::ImageView FindRenderTarget(ImageId id, const ImageDesc& desc);
	[[nodiscard]] vk::ImageView FindDepthTarget(ImageId id, const ImageDesc& desc);
	[[nodiscard]] Image&        GetImage(ImageId id) {
		auto& image = m_slot_images[id];
		TouchImage(image);
		return image;
	}
	void MarkGpuWritten(ImageId id);

	[[nodiscard]] bool ClearImageFromBuffer(CommandBuffer& command, uint64_t address, uint64_t size,
	                                        uint32_t packed_clear);
	void               InvalidateMemory(uint64_t address, uint64_t size);
	// Debug aid: synchronously reads mip 0 of the image back and writes it to `name`.
	void               DebugDumpImage(ImageId id, const std::string& name);
	void               InvalidateMemoryFromGPU(uint64_t address, uint64_t size);
	[[nodiscard]] bool IsRegionGpuModified(uint64_t address, uint64_t size);

	[[nodiscard]] bool IsMeta(uint64_t address);
	[[nodiscard]] bool IsMetaCleared(uint64_t address, uint32_t slice,
	                                 uint32_t* fill_value = nullptr);
	[[nodiscard]] bool ClearMeta(uint64_t address);
	// Record deferred DCC state while the original guest dispatch writes the metadata.
	void               TrackDccFill(uint64_t address, uint64_t size, uint32_t fill_value);
	// Called after the fill dispatch is recorded: stamps the PendingDcc entry with its write sequence.
	void StampPendingDccFill();
	[[nodiscard]] bool TouchMeta(uint64_t address, uint32_t slice, bool is_clear);
	// A shader binding (T# with META_COMPRESS and a metadata address) may be the only user of a
	// surface that the guest fast-cleared through a metadata fill without ever binding it as a
	// colour target. Promote a PendingDcc fill at that address to DCC state owned by the image so
	// the deferred clear becomes visible to MaterializeDeferredDccClear. Returns true when the
	// image now carries DCC metadata for `metadata_address`.
	[[nodiscard]] bool AdoptPendingDccForTexture(ImageId id, uint64_t metadata_address);
	// The registered colour image that starts at `data_address` and owns (or, for a lone
	// metadata-less candidate, adopts) the DCC allocation at `metadata_address`. Empty when
	// there is no such image or the ownership is ambiguous.
	[[nodiscard]] ImageId FindDccSurfaceImage(uint64_t data_address, uint64_t metadata_address);

	void UnmapMemory(uint64_t address, uint64_t size);
	void ProcessDownloadImages();
	void RunGarbageCollector();

private:
	enum class TransferDirection { Upload, Download };
	struct TextureTransfer;
	struct ImageDownload;

	struct MetaDataInfo {
		// A guest metadata-fill dispatch may initialize DCC before its render target is bound.
		// PendingDcc retains that exact fill until an image binding classifies the address,
		// without exposing an unconfirmed buffer address to the normal metadata heuristics.
		// Keep all surface metadata in one entry so CMask/FMask can be
		// registered beside HTile and DCC without introducing parallel tracking paths.
		enum class Type : uint8_t { PendingDcc, CMask, FMask, HTile, Dcc };

		Type     type       = Type::PendingDcc;
		uint32_t clear_mask = 0;
		uint32_t fill_value = 0xffffffffu;
		uint64_t fill_size  = 0;
		uint64_t fill_seq   = 0; // GPU write sequence of the fill dispatch (PendingDcc)
	};

	struct OverlapResult {
		ImageId image;
		int32_t mip   = -1;
		int32_t layer = -1;
	};

	using ImageIds       = InlinePageOwnerList<ImageId, 16>;
	using ImagePageTable = MultiLevelPageTable<ImageIds, 20, 40, 10>;

	// Callers have validated the nonempty 40-bit range with TryGetPageRange.
	template <typename Func>
	static void ForEachPage(uint64_t address, size_t size, Func&& func) {
		using FuncReturn = typename std::invoke_result<Func, uint64_t>::type;
		static constexpr bool RETURNS_BOOL = std::is_same_v<FuncReturn, bool>;
		const uint64_t page_end = (address + size - 1) >> ImagePageTable::kPageBits;
		for (uint64_t page = address >> ImagePageTable::kPageBits; page <= page_end; ++page) {
			if constexpr (RETURNS_BOOL) {
				if (func(page)) {
					break;
				}
			} else {
				func(page);
			}
		}
	}

	[[nodiscard]] ImageId     InsertImage(const ImageInfo& info);
	[[nodiscard]] ImageId     GetNullImage(const ImageDesc& desc);
	void                      RegisterImage(ImageId id);
	void                      UnregisterImage(ImageId id);
	void                      DeleteImage(ImageId id);
	void                      FreeImage(ImageId id);
	void                      TouchImage(Image& image);
	void                      TrackImage(ImageId id);
	void                      TrackImageHead(ImageId id);
	void                      TrackImageTail(ImageId id);
	void                      UntrackImage(ImageId id);
	void                      UntrackImageHead(ImageId id);
	void                      UntrackImageTail(ImageId id);
	void                      MarkAsMaybeDirty(ImageId id, Image& image);
	void                      TrackImageDownload(ImageId id, Image& image);
	[[nodiscard]] static bool SameBacking(const ImageInfo& cached, const ImageInfo& requested,
	                                      bool exact_format);
	[[nodiscard]] static BindingType UploadBinding(const Image& image);
	[[nodiscard]] bool               SafeToDownload(const Image& image);

	// Caller holds m_lock; it also serializes the per-image query epoch.
	[[nodiscard]] ImageIds      FindImagesInRegion(uint64_t address, uint64_t size,
	                                               bool page_overlap) const;
	[[nodiscard]] OverlapResult ResolveOverlap(const ImageInfo& requested, BindingType binding,
	                                           ImageId cached, ImageId merged);
	[[nodiscard]] ImageId       ResolveDepthOverlap(const ImageInfo& requested, BindingType binding,
	                                                ImageId cached);
	[[nodiscard]] ImageId       ExpandImage(const ImageInfo& info, ImageId source);
	// allow_partial: a sampled bind may leave the deferred top mip levels pending; every other
	// use of the image completes the upload first.
	void                        RefreshImage(ImageId id, bool allow_partial = false);
	void                        PrepareDccClear(ImageId id, const ImageDesc& desc);
	// Caller holds m_lock. A PendingDcc fill that the GPU or CPU has overwritten since (streamed
	// textures fill new mips' metadata and then DMA the real one) must not be adopted as a clear.
	[[nodiscard]] bool          PendingDccFillStale(uint64_t address, const MetaDataInfo& meta,
	                                                uint64_t image_address);
	void                        InitializeImage(ImageId id, bool allow_defer = true);
	[[nodiscard]] TextureTransfer
	BuildTextureTransfer(const Image& image, BindingType binding, TransferDirection direction) const;
	[[nodiscard]] ImageDownload BuildDownload(const Image& image) const;
	// Uploads levels [first_level, first_level + level_count) (everything by default) and
	// returns the guest bytes transferred.
	uint64_t UploadImage(Image& image, vk::Buffer source, uint64_t source_offset,
	                     uint64_t source_size, bool source_is_host, uint32_t first_level = 0,
	                     uint32_t level_count = UINT32_MAX);
	// Deferred mip upload (KYTY_MIP_DEFER, default on). A scene cut uploads 300-450 textures
	// between its draws and the GPU spends most of the frame detiling them; mip 0 alone is 75 %
	// of the bytes. Once a frame has uploaded KYTY_MIP_DEFER_FRAME_MB, a large sampled texture
	// from imported guest memory uploads only its tail: its sampled views clamp the LOD to the
	// resident levels (VK_EXT_image_view_min_lod) and the top levels arrive at a later bind,
	// KYTY_MIP_DEFER_BUDGET_MB per frame. Any other use (storage, target, copy, download)
	// completes the upload first. Returns the number of top levels to leave pending.
	[[nodiscard]] uint32_t DeferrableLevels(const Image& image, bool source_imported) const;
	void                   CompletePendingUpload(Image& image);
	void                   NoteUploadFrame();
	void DownloadImage(Image& image, Buffer& destination, uint64_t destination_offset,
	                   uint64_t destination_size, ImageDownload transfer);
	void DownloadDepth(Image& image, Buffer& destination, uint64_t destination_offset);
	void CommitGpuWrite(Image& image);
	// Caller holds m_lock. Volume layer ranges select depth slices.
	void ClearImage(CommandBuffer& command, ImageId id, const vk::ImageSubresourceRange& range,
	                const vk::ClearValue& clear);
	void PrepareImageCopy(Image& image);
	void RefreshCopySource(ImageId id);
	[[nodiscard]] bool CopyD16(Image& destination, Image& source);
	void               CopyImage(ImageId destination, ImageId source);
	void               AssociateStencil(ImageId depth, GuestRange stencil);
	void CopyImageMip(ImageId destination, ImageId source, uint32_t mip, uint32_t layer);
	void ValidateImageDesc(const ImageDesc& desc) const;

	void               InvalidateCpuAliases(uint64_t address, uint64_t size);
	[[nodiscard]] bool DownloadImageMemory(ImageId id);

	GraphicContext&                                   m_graphics;
	CommandScheduler&                                 m_scheduler;
	TrackingSpinLock                                  m_lock;
	PageManager&                                      m_page_manager;
	BlitHelper                                        m_blit_helper;
	TileManager                                       m_tiler;
	BufferCache&                                      m_buffer_cache;
	uint64_t                                          m_fill_stamp_address = 0;
	uint64_t                                          m_fill_stamp_size    = 0;
	Common::SlotVector<Image>                         m_slot_images;
	ImagePageTable                                    m_image_page_table;
	std::unordered_map<vk::Format, ImageId>           m_null_images;
	Common::LeastRecentlyUsedCache<ImageId, uint64_t> m_lru_cache;
	std::unordered_set<ImageId>                       m_download_images;
	std::map<uint64_t, MetaDataInfo>                  m_surface_metas;
	uint64_t                                          m_total_used_memory  = 0;
	uint64_t                                          m_trigger_gc_memory  = 0;
	uint64_t                                          m_pressure_gc_memory = 1536ull * 1024 * 1024;
	uint64_t         m_critical_gc_memory     = 3ull * 1024 * 1024 * 1024;
	uint64_t         m_gc_tick                = 0;
	mutable uint32_t m_image_query_epoch      = 0;
	bool             m_readback_linear_images = false;
	uint32_t         m_upload_frame           = 0; // flip count of the upload counters below
	uint64_t         m_frame_upload_bytes     = 0; // guest bytes uploaded to images this frame
	uint64_t         m_frame_pending_bytes    = 0; // ... of which deferred top levels

	friend struct TextureCacheTestAccess;
	friend class BufferCache;
	friend class RenderExecutor;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_TEXTURECACHE_H_
