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

#include <atomic>
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
namespace DiagF5 {
struct CmuEvent;   // Track F, F16k (diagF5.h)
struct StaleProbe; // Track F, F16k (diagF5.h)
enum class F26Site : uint8_t; // Track F, F46a (diagF5.h)
} // namespace DiagF5
namespace DiagF5Id {
struct MetaSnap; // Track F, F16k (diagF5.h)
struct DccMiss;  // Track F, F16k (diagF5.h)
} // namespace DiagF5Id

class TextureCache {
public:
	enum class BindingType : uint8_t { Texture, Storage, RenderTarget, DepthTarget, VideoOut };

	struct ImageDesc {
		ImageInfo     info;
		ImageViewInfo view_info;
		BindingType   type = BindingType::Texture;
		uint32_t      source_first_level = 0;
		uint64_t      source_size = 0; // zero means the full logical footprint
	};

	TextureCache(GraphicContext& graphics, CommandScheduler& scheduler, PageManager& page_manager,
	             BufferCache& buffer_cache);
	~TextureCache();
	KYTY_CLASS_NO_COPY(TextureCache);

	[[nodiscard]] ImageId       FindImage(ImageDesc& desc, bool exact_format = false);
	void ConfigureImageSource(ImageId id, const ImageDesc& desc);
	void                        UpdateImage(ImageId id);
	[[nodiscard]] ImageId       FindImageFromRange(uint64_t address, uint64_t size,
	                                               bool ensure_valid = true);
	// Session 71, candidate C3 (counters only, no decision changed): the guest fast-clear
	// REGISTERS of a binding, as pm4Handlers decoded them into HW::RenderTarget and
	// HW::RenderControl - read BEFORE ResolveRenderColorTarget turns them into an
	// ImageMetadataKind and before its width%1024 / height%1024 guard can drop a CMASK fast
	// clear. The texture cache cannot reach the register file, so the binding hands the bits
	// over. guest_clear_regs = 0 keeps every existing caller unchanged.
	static constexpr uint32_t kRegColorFastClear = 1u << 0u; // CB_COLOR*_INFO.FAST_CLEAR
	static constexpr uint32_t kRegColorCmaskAddr = 1u << 1u; // CB_COLOR*_CMASK_BASE != 0
	static constexpr uint32_t kRegColorDccEnable = 1u << 2u; // CB_COLOR*_INFO.DCC_ENABLE
	static constexpr uint32_t kRegColorDccAddr   = 1u << 3u; // CB_COLOR*_DCC_BASE != 0
	static constexpr uint32_t kRegColorDccKey    = 1u << 4u; // DCC_CONTROL.KEY_CLEAR_ENABLE
	static constexpr uint32_t kRegDepthClear     = 1u << 5u; // DB_RENDER_CONTROL.DEPTH_CLEAR
	static constexpr uint32_t kRegStencilClear   = 1u << 6u; // ... STENCIL_CLEAR, as resolved

	[[nodiscard]] vk::ImageView FindTexture(ImageId id, const ImageDesc& desc);
	// Track F, F9e2b (KYTY_FIX_B42, ROADMAP s122 item 353(g)(1)): `fce_materialize` - the acquisition of the
	// fast-clear-eliminate register scan RenderExecutor::MaterializeBoundTargetDccClears (descriptors.cpp), the only
	// caller that passes true. Every other acquisition is a draw-path colour target and stamps the image with the B42
	// sequence (m_b42_draw_seq); the flag changes nothing else.
	// Track F, F16k (KYTY_FIX_F5CMU, ROADMAP s122 item 492(v)): `fce_materialize` also tells PrepareCmaskClear that this is
	// the FCE acquisition (the only one where KYTY_FIX_F5CMU decides); `f5cmu` (non-null only with KYTY_DIAG_F5, from
	// the FCE scan) receives that call's decision for the event line.
	[[nodiscard]] vk::ImageView FindRenderTarget(ImageId id, const ImageDesc& desc,
	                                             uint32_t guest_clear_regs = 0,
	                                             bool     fce_materialize  = false,
	                                             DiagF5::CmuEvent* f5cmu   = nullptr);
	[[nodiscard]] vk::ImageView FindDepthTarget(ImageId id, const ImageDesc& desc,
	                                            uint32_t guest_clear_regs = 0);
	// Gate "rtfast": see m_meta_epoch.
	[[nodiscard]] uint64_t MetaEpoch() const noexcept {
		return m_meta_epoch.load(std::memory_order_relaxed);
	}
	// Gate "rtfast": the image record AssociateStencil left for this stencil range (the one whose
	// data address is the range's, as AssociateStencil selects it), or none.
	[[nodiscard]] ImageId FindStencilAssociation(GuestRange stencil);
	// Session 64 (shadowResolve.h): the reads a memo-hit sampled bind makes on its image, taken
	// under m_lock and answered without touching anything. `has_view`/`fast_stamp`: the memo slot
	// holds a recorded view for this stamp (gate "texfast"); `eligible`: sampled, no DCC, not a
	// dynamic storage binding - the conditions of the recorded-view path.
	struct ShadowImageQuery {
		ImageId           id;
		GuestRange        data;
		vk::Extent3D      extent;
		ImageSubresources resources;
		uint32_t          source_first_level = 0;
		uint64_t          source_size        = 0;
		uint32_t          fast_stamp         = 0;
		bool              has_view           = false;
		bool              eligible           = false;
	};
	// Gone: the id is not allocated. Stale: the memo checks fail (registration, rebind, stencil,
	// backing). Slow: not eligible for the recorded view. View: eligible, but FindTexture would
	// run (no recorded view, stamp moved, pending levels, source not settled). Fast: the recorded
	// view would be taken as it is.
	enum class ShadowImageAnswer : uint8_t { Gone, Stale, Slow, View, Fast };
	[[nodiscard]] ShadowImageAnswer ShadowProbe(const ShadowImageQuery& query);
	[[nodiscard]] Image&        GetImage(ImageId id) {
		auto& image = m_slot_images[id];
		TouchImage(image);
		return image;
	}
	// Track F, F47g (HPP-824): the image without the LRU touch of GetImage (KYTY_DIAG_F47DT reads only).
	[[nodiscard]] const Image& PeekImage(ImageId id) const { return m_slot_images[id]; }
	void MarkGpuWritten(ImageId id);

	[[nodiscard]] bool ClearImageFromBuffer(CommandBuffer& command, uint64_t address, uint64_t size,
	                                        uint32_t packed_clear);
	void               InvalidateMemory(uint64_t address, uint64_t size);
	// Debug aid: synchronously reads mip 0 of the image back and writes it to `name`.
	void               DebugDumpImage(ImageId id, const std::string& name);
	void               InvalidateMemoryFromGPU(uint64_t address, uint64_t size);
	[[nodiscard]] bool IsRegionGpuModified(uint64_t address, uint64_t size);

	[[nodiscard]] bool IsMeta(uint64_t address);
	// Track F, F9e2 (KYTY_FIX_B42, ROADMAP s122 item 351(v)(1)): a read-only copy of the metadata entry at `address`,
	// taken under m_lock. Nothing is inserted, bumped, stamped or consumed - the answer is the same with and without
	// the fix. `pending`: the entry is a PendingDcc fill (TrackDccFill) no image binding has classified yet; `cmask`:
	// a binding classified it as CMASK (PrepareCmaskClear). F9e2b (item 353(g)(1)), in the same acquisition:
	// `b42_fill_seq` - the B42 sequence of the last fill that set fill_value at `address`; `b42_draw_seq` - that of
	// the last draw-path FindRenderTarget of `image` (0: none since the image was created). Drawn after the fill
	// <=> b42_draw_seq > b42_fill_seq.
	struct MetaFillQuery {
		bool     found        = false;
		bool     pending      = false;
		bool     cmask        = false;
		uint32_t clear_mask   = 0;
		uint32_t fill_value   = 0xffffffffu;
		uint64_t fill_size    = 0;
		uint64_t b42_fill_seq = 0;
		uint64_t b42_draw_seq = 0;
	};
	[[nodiscard]] MetaFillQuery QueryMetaFill(uint64_t address, ImageId image);
	// Cleared layers of one surface in a single acquisition (bit per layer, 0 when the address
	// is not a finished metadata clear). IsMetaCleared answers the same question one layer at a
	// time and is kept for the callers that only look at a single layer.
	[[nodiscard]] uint32_t MetaClearMask(uint64_t address, uint32_t* fill_value);
	[[nodiscard]] bool IsMetaCleared(uint64_t address, uint32_t slice,
	                                 uint32_t* fill_value = nullptr);
	// Track F, F16d (KYTY_DIAG_F5): `f5_refusal` (optional) receives the kind of a refusal of a PendingDcc / Dcc / CMask
	// address (DiagF5::RefusalDcc / RefusalCmask), only with the knob on; the answer does not depend on it.
	// Track F, F16k (KYTY_DIAG_F5ID): `f5id_snap` (optional) receives the refused entry in the same branch, under m_lock.
	[[nodiscard]] bool ClearMeta(uint64_t address, uint8_t* f5_refusal = nullptr,
	                             DiagF5Id::MetaSnap* f5id_snap = nullptr);
	// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)): a read-only copy of the entry at `address` taken under m_lock (Absent
	// when there is none); nothing is inserted, bumped or consumed.
	void F5IdMetaSnap(uint64_t address, DiagF5Id::MetaSnap* out);
	// Record deferred DCC state while the original guest dispatch writes the metadata.
	// This merge kept our PendingDcc tracking instead of upstream's content-based
	// MaterializeDccClear (437e69e/01df42a), so this call is the ONLY producer of PendingDcc
	// entries: it must stay wired to the compute metadata-fill path in renderCompute.cpp, on the
	// branch where ClearImageFromBuffer declines the fill. Without it PrepareDccClear,
	// AdoptPendingDccForTexture, FindDccSurfaceImage and RenderExecutor's
	// MaterializeDeferredDccClear / MaterializeBoundTargetDccClears are all dead code and DCC
	// fast clears are never materialized (ASTRO BOT: the "crowd silhouette" flashes come back).
	void               TrackDccFill(uint64_t address, uint64_t size, uint32_t fill_value);
	// Called after the fill dispatch is recorded: stamps the PendingDcc entry with its write sequence.
	void StampPendingDccFill();
	// Track F, F16k2 (KYTY_DIAG_F5ID, RC3, ROADMAP s122 item 496(b)(3)): called at the end of DispatchDirect (its
	// F5IdCsHolder): a fill stamp TrackDccFill left and StampPendingDccFill has not taken (the dispatch returned before
	// it) counts stamp_late once; the stamp itself is unchanged. Nothing without DiagF5Id::On().
	void F5IdNoteStampLate();
	[[nodiscard]] bool TouchMeta(uint64_t address, uint32_t slice, bool is_clear);
	// A shader binding (T# with META_COMPRESS and a metadata address) may be the only user of a
	// surface that the guest fast-cleared through a metadata fill without ever binding it as a
	// colour target. Promote a PendingDcc fill at that address to DCC state owned by the image so
	// the deferred clear becomes visible to MaterializeDeferredDccClear. Returns true when the
	// image now carries DCC metadata for `metadata_address`.
	// Track F, F16k (KYTY_DIAG_F5ID): `f5id_miss` (optional) receives the reason of a false answer (DiagF5Id::Miss).
	[[nodiscard]] bool AdoptPendingDccForTexture(ImageId id, uint64_t metadata_address,
	                                             DiagF5Id::DccMiss* f5id_miss = nullptr);
	// Track F, F16o2 (KYTY_FIX_F26, RC1 of F16p, ROADMAP s122 item 507(b)(2)-(3)) and Track F, F46a (HPP-798, item
	// 702(e)(2)-(3), RC5 of F45b): the mark M1 of a kept fill keyed by the METADATA ADDRESS (diagF5.h, DccApplyLine) -
	// set under m_lock by the reporting F26Scope (F26MarkLocked), removed by the execution of the fill at that address
	// by any image (F26ExecLocked / F26Exec), reported once on a MaterializeDeferredDccClear of the address that clears
	// nothing (F26Declined), dropped by a new fill, an erase or a retype of the entry (F26DropLocked); and the armed
	// events of the line f26_first_exec (F26ArmFirstExecLocked; KYTY_DIAG_F5ID), fired by the same execution hook.
	// *Locked - the caller holds m_lock; F26Exec / F26Declined / F26HasMark take it themselves (as MetaClearMask;
	// RenderExecutor::MaterializeDeferredDccClear holds no texture cache lock), and not at all while nothing is stored
	// (the counts). No mark exists with KYTY_FIX_F26 = 0 or KYTY_DIAG_F5 = 0; no armed event without KYTY_DIAG_F5ID.
	struct F26Deferred {
		uint64_t n        = 0; // the event number of the dcc_stale line that set the mark
		uint64_t image    = 0; // image / dcc of that line
		uint64_t dcc      = 0;
		bool     declined = false; // Track F, F46a: the declined line of this mark was printed
	};
	void F26MarkLocked(uint64_t address, const F26Deferred& mark);
	void F26ArmFirstExecLocked(uint64_t address, uint64_t n);
	// `layers` - the clear-mask bits of `address` the execution took 1 -> 0 (called only when != 0).
	void F26ExecLocked(uint64_t address, uint64_t image_address, DiagF5::F26Site site, uint32_t layers);
	void F26Exec(uint64_t address, uint64_t image_address, DiagF5::F26Site site, uint32_t layers);
	void F26Declined(uint64_t address, uint64_t image_address, uint32_t layers);
	void F26DropLocked(uint64_t address, DiagF5::F26Site site, uint32_t layers);
	[[nodiscard]] bool F26HasMarkLocked(uint64_t address) const;
	[[nodiscard]] bool F26HasMark(uint64_t address);
	// The registered colour image that starts at `data_address` and owns (or, for a lone
	// metadata-less candidate, adopts) the DCC allocation at `metadata_address`. Empty when
	// there is no such image or the ownership is ambiguous.
	// Track F, F16k (KYTY_DIAG_F5ID): `f5id_miss` (optional) receives the reason of an empty answer (DiagF5Id::Miss).
	[[nodiscard]] ImageId FindDccSurfaceImage(uint64_t data_address, uint64_t metadata_address,
	                                          DiagF5Id::DccMiss* f5id_miss = nullptr);

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
		// Track F, F9e2b (KYTY_FIX_B42, ROADMAP s122 item 353(g)(1)): m_b42_seq at the last TrackDccFill that set
		// fill_value. Read only by QueryMetaFill.
		uint64_t b42_fill_seq = 0;
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
	void                      FreeImage(ImageId id, const char* reason = "unknown", uint32_t line = 0);
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
	// Track F, F16k (item 492(v)): `fce` - the FCE acquisition (FindRenderTarget's fce_materialize); `f5cmu` - see
	// FindRenderTarget.
	void                        PrepareCmaskClear(ImageId id, const ImageDesc& desc, bool fce = false,
	                                              DiagF5::CmuEvent* f5cmu = nullptr);
	// Caller holds m_lock (IsMetaCleared / MetaClearMask take it themselves and the
	// TrackingSpinLock EXITs on recursion). Session 71, C3 premise: is there an unconsumed
	// metadata FILL - the state PrepareDccClear / PrepareCmaskClear act on - for a bound layer?
	// Deliberately NOT the register state; the two are counted apart and never conflated.
	[[nodiscard]] bool          MetaFillPendingLocked(const ImageDesc& desc) const;
	// Caller holds m_lock. A PendingDcc fill that the GPU or CPU has overwritten since (streamed
	// textures fill new mips' metadata and then DMA the real one) must not be adopted as a clear.
	// Track F, F16k (item 492(v)(2)): `f5_probe` (nullptr - the old call exactly) - see DiagF5::StaleProbe; the answer
	// changes only with f5_probe->exact_decides (KYTY_FIX_F5CMU at the FCE acquisition; Track F, F16o: KYTY_FIX_F26 at
	// PrepareDccClear and AdoptPendingDccForTexture).
	[[nodiscard]] bool          PendingDccFillStale(uint64_t address, const MetaDataInfo& meta,
	                                                uint64_t image_address, DiagF5::StaleProbe* f5_probe = nullptr);
	void                        InitializeImage(ImageId id, bool allow_defer = true);
	[[nodiscard]] TextureTransfer
	BuildTextureTransfer(const Image& image, BindingType binding, TransferDirection direction) const;
	[[nodiscard]] TextureTransfer BuildTextureTransfer(const ImageInfo& info, uint32_t native_samples,
	    BindingType binding, TransferDirection direction) const;
	void ConstrainSampledSource(ImageDesc& desc) const;
	void ConfigureImageSourceUnlocked(ImageId id, const ImageDesc& desc);
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
	void ClearImage(CommandBuffer& command, ImageId id, vk::Format format,
	                const vk::ImageSubresourceRange& range, const vk::ClearValue& clear);
	void PrepareImageCopy(ImageId id);
	void RestoreFullImageSource(ImageId id);
	void RefreshCopySource(ImageId id);
	[[nodiscard]] bool CopyD16(Image& destination, Image& source);
	void               CopyImage(ImageId destination, ImageId source);
	void               AssociateStencil(ImageId depth, GuestRange stencil);
	void CopyImageMip(ImageId destination, ImageId source, uint32_t mip, uint32_t layer);
	void ValidateImageDesc(const ImageDesc& desc) const;

	void               InvalidateCpuAliases(uint64_t address, uint64_t size);
	// Gate "texfaulthint": false when no image is registered on the pages of the range.
	[[nodiscard]] bool MayHaveImages(uint64_t address, uint64_t size) const noexcept;
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
	// Track F, F16k (KYTY_DIAG_F5ID): the last fill of any entry type, stamped for DiagF5Id::NoteFillSeq (wr_after).
	uint64_t                                          m_f5id_stamp_address = 0;
	uint64_t                                          m_f5id_stamp_size    = 0;
	bool                                              m_f5id_stamp_late    = false; // F16k2: stamp_late counted
	Common::SlotVector<Image>                         m_slot_images;
	ImagePageTable                                    m_image_page_table;
	// Gate "texfaulthint": images per page of m_image_page_table. Written under m_lock (raised
	// before an image is added to a page, lowered after it is removed), read without it.
	std::unique_ptr<std::atomic<uint32_t>[]> m_image_page_hint =
	    std::make_unique<std::atomic<uint32_t>[]>(ImagePageTable::kPageCount);
	std::unordered_map<vk::Format, ImageId>           m_null_images;
	Common::LeastRecentlyUsedCache<ImageId, uint64_t> m_lru_cache;
	std::unordered_set<ImageId>                       m_download_images;
	std::map<uint64_t, MetaDataInfo>                  m_surface_metas;
	// Gate "rtfast": moves on every change of m_surface_metas (entries, types, fills, clear
	// masks). A recorded target view is only reused while it is unchanged, so the DCC / CMASK /
	// HTile work FindRenderTarget / FindDepthTarget would do is never skipped past a change.
	std::atomic<uint64_t>                             m_meta_epoch {0};
	void BumpMetaEpoch() noexcept { m_meta_epoch.fetch_add(1, std::memory_order_relaxed); }
	// Track F, F9e2b (KYTY_FIX_B42, ROADMAP s122 item 353(g)(1)), under m_lock: one monotonic sequence. TrackDccFill
	// writes it into MetaDataInfo::b42_fill_seq, a draw-path FindRenderTarget into m_b42_draw_seq[id] (erased in
	// DeleteImage, so a recycled slot id starts unstamped). Read only by QueryMetaFill: no Vulkan value, no metadata
	// state and no epoch depends on them, with KYTY_FIX_B42 on or off.
	uint64_t                                          m_b42_seq = 0;
	std::unordered_map<ImageId, uint64_t>             m_b42_draw_seq;
	// Track F, F46a (item 702(e)(2)-(3)): the marks M1 by metadata address and the armed f26_first_exec events (event
	// numbers by metadata address), under m_lock; their numbers - written under m_lock, read without it by the fast
	// paths (0: the lock is not taken).
	std::unordered_map<uint64_t, F26Deferred>         m_f26_marks;
	std::atomic<uint32_t>                             m_f26_marks_count {0};
	std::unordered_map<uint64_t, std::vector<uint64_t>> m_f26_first;
	std::atomic<uint32_t>                             m_f26_first_count {0};
	uint64_t                                          m_total_used_memory  = 0;
	uint64_t                                          m_trigger_gc_memory  = 0;
	uint64_t                                          m_pressure_gc_memory = 1536ull * 1024 * 1024;
	uint64_t         m_critical_gc_memory     = 3ull * 1024 * 1024 * 1024;
	uint64_t         m_gc_tick                = 0;
	// TouchImage counters (FrameTrace-x texlru_n / texlru_rep), flushed by RunGarbageCollector.
	uint64_t         m_lru_touch_calls        = 0;
	uint64_t         m_lru_touch_repeats      = 0;
	mutable uint32_t m_image_query_epoch      = 0;
	bool             m_readback_linear_images = false;
	uint32_t         m_upload_frame           = 0; // flip count of the upload counters below
	uint64_t         m_frame_upload_bytes     = 0; // guest bytes uploaded to images this frame
	uint64_t         m_frame_pending_bytes    = 0; // ... of which deferred top levels

	friend struct TextureCacheTestAccess;
	friend class BufferCache;
	friend class RenderExecutor;
	friend struct SkcCensus;
};

// Session 72, measurement only (KYTY_CLEAR_TRACE): the outcome the last ClearImageFromBuffer on
// this thread took - "ok", "none", "ambig", "decode" or "invalid". Written at every exit of that
// function, read only by the BufferFillTrace print. Never changes a decision.
const char* TextureCacheLastClearOutcome();

// Session 123, knob "skipceil" = 2: the correctness census (MEASUREMENT ONLY; docs/session-123/design123.md s.3 with
// ROADMAP s122 items 28-33).  GuestGpu thread only (no lock).  Every entry point is called only while the census is
// latched (Common::SkipCeil::t_mode >= 2) - the call sites test that first - except the scopes, which test it inline.
struct SkcCensus {
	// Session 124, knob "skipceil" = 3 (ROADMAP s122 item 47(e)): subresources a site knows - aspects 1 colour, 2 depth,
	// 4 stencil; lmask != 0: the layers of the mask (by / yc unused).  A W3 stamped outside every SubScope closes the keys
	// of its image without a writer (skc3_w3_nw).
	struct Sub {
		uint32_t bl    = 0;
		uint32_t lc    = 0;
		uint32_t by    = 0;
		uint32_t yc    = 0;
		uint32_t lmask = 0;
		uint8_t  asp   = 0;
	};
	static uint8_t AspBits(vk::ImageAspectFlags aspects) noexcept {
		return static_cast<uint8_t>(((aspects & vk::ImageAspectFlagBits::eColor) ? 1u : 0u) |
		                            ((aspects & vk::ImageAspectFlagBits::eDepth) ? 2u : 0u) |
		                            ((aspects & vk::ImageAspectFlagBits::eStencil) ? 4u : 0u));
	}
	// One census operation (s.3.1): an R / K draw from the renderer entry (D from the skip site on), a CS dispatch.  Drops
	// the W2 stamps it never applied and books skc_x1_draw / _cs / _pass and skc_wpasses at the end.  Does not nest.
	class OpScope {
	public:
		// Session 124: census3 = armed only by the closure census (the DMA operation M, design124.md s.3.2).
		OpScope(TextureCache& cache, uint8_t kind, bool draw, bool census3 = false) noexcept {
			if (Common::SkipCeil::t_mode >= (census3 ? 3u : 2u)) [[unlikely]] {
				m_armed = SkcCensus::OpBegin(kind, draw);
				m_cache = &cache;
				m_draw  = draw;
			}
		}
		~OpScope() {
			if (m_armed) [[unlikely]] {
				SkcCensus::OpEnd(*m_cache, m_draw);
			}
		}
		KYTY_CLASS_NO_COPY(OpScope);

	private:
		TextureCache* m_cache = nullptr;
		bool          m_armed = false;
		bool          m_draw  = false;
	};
	// [P3] An image-to-image copy whose source carries D / T hands its label to the destination (a carry, not a stamp:
	// no stamp counter moves); the W3 stamp of the destination is suppressed while the scope lives.
	class CarryScope {
	public:
		CarryScope(Image& destination, const Image& source) noexcept {
			if (Common::SkipCeil::t_w3) [[unlikely]] {
				m_armed = SkcCensus::Carry(destination, source);
			}
		}
		~CarryScope() {
			if (m_armed) [[unlikely]] {
				Common::SkipCeil::t_carry = false;
			}
		}
		KYTY_CLASS_NO_COPY(CarryScope);

	private:
		bool m_armed = false;
	};

	[[nodiscard]] static bool OpBegin(uint8_t kind, bool draw) noexcept;
	static void                OpEnd(TextureCache& cache, bool draw) noexcept;
	[[nodiscard]] static bool Carry(Image& destination, const Image& source) noexcept;
	// The skip site of a draw of a skippable frame: K -> D, skc_c_dd.
	static void SkipSiteD() noexcept;
	// The PS of the running draw: skc_whash of its D stamps.
	static void SetDrawPs(uint64_t ps_hash) noexcept;
	// RebindImages: every non-null image binding is a read; a storage binding also queues a W2 stamp.  stage: 0 vs,
	// 1 ps, 2 cs.
	static void ReadImage(TextureCache& cache, ImageId id, bool storage, uint64_t shader_hash, uint32_t stage);
	// DepthStencilCopy: the source read, before the W3 stamp of the destination ([N3]).  Session 124 (mode 3, ROADMAP
	// s122 item 47(e)): the graph reads the copied subresources `sub` only.
	static void ReadDepthCopySource(TextureCache& cache, ImageId id, const Sub& sub);
	// The tail of AcquireRenderTargets: the attachment read (skc_x1_att), then the W1 stamp when the draw writes it.
	static void Attachment(TextureCache& cache, ImageId id, bool writes);
	// NativeStorageBuffer after the null return (ROADMAP s122 item 33(a)): every slot is a read; a written slot also
	// queues a W2 stamp.
	// Session 124 (mode 3, ROADMAP s122 item 47(g)): g3_late - the graph read comes later, from G3ReadBufferLate after
	// ObtainBuffer (a texel binding: SynchronizeBufferFromImage writes the range first).
	static void ReadBuffer(BufferCache& buffers, uint64_t vaddr, uint64_t size, bool written, bool g3_late = false);
	// The indirect arguments an executed operation reads on the GPU path ([N2]).
	static void ReadIndirectArgs(BufferCache& buffers, uint64_t vaddr, uint64_t size);
	// An executed operation with uses_dma at the PrepareBda sites ([RC11], [N8]).
	static void NoteDma(BufferCache& buffers);
	// After the operation's last read ([N1]): the queued W2 stamps.
	static void ApplyW2(TextureCache& cache, BufferCache& buffers);
	// UploadImage: the label follows the guest memory the image receives ([N5]).  Any thread (skc_w_xthr off GuestGpu).
	// Session 124 (mode 3): levels [first_level, first_level + level_count) are a lazy write of site "upload" [RC1].
	static void Upload(BufferCache& buffers, Image& image, uint32_t first_level, uint32_t level_count);
	// DownloadImageMemory: an image with a D / T label goes to guest memory (skc_r_i_*).
	static void DownloadRead(const Image& image);
	// The flip boundary of a census frame: SkcX1Reader / SkcCpuRead / SkcCpRead lines every 600 census frames.
	static void FrameDump(BufferCache& buffers);
	// MarkGpuModified.
	static void StampW3(Image& image) noexcept;

	// -----------------------------------------------------------------------------------------------------------------
	// Session 124, knob "skipceil" = 3: the closure census (MEASUREMENT ONLY; docs/session-124/design124.md rev 2 with
	// ROADMAP s122 items 43-44).  GuestGpu thread only (G3PendAdd: any thread); every entry point is called only while
	// t_mode == 3 - the call sites or the scopes test it first.
	// The sites of lazy writes [RC1] (line Skc3Lazy): upload, the three image-to-image copies P3, the materialization of a
	// deferred clear (an Lt-only write, not a write event), and any other W3 while a sampled binding resolves (w3r).
	enum LazySite : uint8_t {
		LazyNone   = 0,
		LazyUpload = 1,
		LazyP3a    = 2, // CopyImage
		LazyP3b    = 3, // CopyImageMip
		LazyP3c    = 4, // ResolveDepthOverlap (MS depth reinterpretation)
		LazyMat    = 5, // the materialization of a deferred clear, on every path (ROADMAP s122 item 47(b))
		LazyW3r    = 6, // a sampled binding resolving
	};
	// W3 stamps inside the scope are the lazy write of its site (upload and P3 record their write explicitly and swallow
	// the stamps); scopes nest, the innermost wins.
	class LazyScope {
	public:
		explicit LazyScope(uint8_t site, bool on = true) noexcept {
			if (on && Common::SkipCeil::t_mode == 3) [[unlikely]] {
				m_armed = true;
				m_prev  = LazyEnter(site);
			}
		}
		~LazyScope() {
			if (m_armed) [[unlikely]] {
				LazyLeave(m_prev);
			}
		}
		KYTY_CLASS_NO_COPY(LazyScope);

	private:
		bool    m_armed = false;
		uint8_t m_prev  = LazyNone;
	};
	// The subresources the W3 stamps inside the scope write (ROADMAP s122 item 47(e)); scopes nest, the innermost wins.
	class SubScope {
	public:
		explicit SubScope(const Sub& sub) noexcept {
			if (Common::SkipCeil::t_mode == 3) [[unlikely]] {
				m_armed   = true;
				m_prev_on = SubEnter(sub, m_prev);
			}
		}
		~SubScope() {
			if (m_armed) [[unlikely]] {
				SubLeave(m_prev_on, m_prev);
			}
		}
		KYTY_CLASS_NO_COPY(SubScope);

	private:
		bool m_armed   = false;
		bool m_prev_on = false;
		Sub  m_prev {};
	};
	// RenderContext::RunGarbageCollector of a marked frame (s.5.4): its wall minus the pauses inside.
	class GcSpan {
	public:
		GcSpan() noexcept {
			if (Common::SkipCeil::t_mode == 3 && Common::SkipCeil::t_skip) [[unlikely]] {
				m_on  = true;
				m_win = Common::SkipCeil::t_p_win & Common::SkipCeil::PWinGc; // item 50(a): the probe window
				Common::SkipCeil::t_p_win |= Common::SkipCeil::PWinGc;
				m_p  = Common::SkipCeil::t_p_ns;
				m_n  = Common::SkipCeil::t_p_n;
				m_t0 = Common::FrameStats::NowNs();
			}
		}
		~GcSpan() {
			if (m_on) [[unlikely]] {
				GcDone(m_t0, m_p, m_n);
				Common::SkipCeil::t_p_win = (Common::SkipCeil::t_p_win & ~Common::SkipCeil::PWinGc) | m_win;
			}
		}
		KYTY_CLASS_NO_COPY(GcSpan);

	private:
		bool     m_on  = false;
		uint32_t m_win = 0;
		uint64_t m_t0  = 0;
		uint64_t m_p   = 0;
		uint64_t m_n   = 0;
	};
	// GuestGpu::Process of a marked frame (s.5.6, skc3_fr_*): armed exactly when the WallSpan gw_proc is
	// (KYTY_GPU_WALL=1); booked to the frame open at its start.
	class ProcSpan {
	public:
		ProcSpan() noexcept {
			if (Common::SkipCeil::t_mode == 3 && Common::SkipCeil::t_skip && Common::FrameStats::GpuWallOn() &&
			    Common::FrameStats::Enabled()) [[unlikely]] {
				m_on    = true;
				m_frame = Common::SkipCeil::t_gframe;
				m_p     = Common::SkipCeil::t_p_ns;
				m_n     = Common::SkipCeil::t_p_n;
				m_t0    = Common::FrameStats::NowNs();
			}
		}
		~ProcSpan() {
			if (m_on) [[unlikely]] {
				ProcDone(m_frame, m_t0, m_p, m_n);
			}
		}
		KYTY_CLASS_NO_COPY(ProcSpan);

	private:
		bool     m_on    = false;
		uint32_t m_frame = 0;
		uint64_t m_t0    = 0;
		uint64_t m_p     = 0;
		uint64_t m_n     = 0;
	};
	static uint8_t LazyEnter(uint8_t site) noexcept;
	static void    LazyLeave(uint8_t prev) noexcept;
	static void    GcDone(uint64_t t0, uint64_t p0, uint64_t n0) noexcept;
	static void    ProcDone(uint32_t frame, uint64_t t0, uint64_t p0, uint64_t n0) noexcept;
	static bool    SubEnter(const Sub& sub, Sub& prev) noexcept;
	static void    SubLeave(bool prev_on, const Sub& prev) noexcept;
	// SkipCeilFlipBoundary: the end of a mode-3 frame (poll bit, finalization, calibration), then the latch.
	static void G3FrameEnd();
	static void G3Latch(bool edge);
	// RebindImages: the read of a binding's view (storage: also a pending W2 write of it).
	static void G3ReadView(TextureCache& cache, ImageId id, const ImageViewInfo& view, bool storage, uint64_t shader_hash,
	                       uint32_t stage);
	// AcquireRenderTargets: an attachment read by the pipeline state (aspects 1 colour, 2 depth, 4 stencil), then its
	// pending W1 write.
	static void G3Attachment(TextureCache& cache, ImageId id, const ImageViewInfo& view, uint8_t write_aspects,
	                         uint8_t read_aspects);
	// A D draw returned after its skip site without work (flag empty, [RC13]).
	static void G3Empty() noexcept;
	// A stage of the running operation has info.uses_dma (the epoch, s.3.3.3 with ROADMAP s122 item 44(d)).
	static void G3Dma() noexcept;
	// A GDS binding of a draw / dispatch: no offset and size (skc3_gds_unk), a possible write of the whole GDS.
	static void G3GdsAccess(uint64_t gds_size);
	// DMA (M): FillBuffer / CopyBuffer.
	static void G3DmaWrite(uint64_t vaddr, uint64_t size, bool gds);
	static void G3DmaCopy(uint64_t dst, uint64_t src, uint64_t size, bool dst_gds, bool src_gds);
	// Writes with no writer: CP [RC3], CPU of the guest, an image download to guest memory.
	static void G3CpWrite(uint64_t vaddr, uint64_t size);
	static void G3CpuWrite(uint64_t vaddr, uint64_t size);
	static void G3Download(const Image& image);
	// The pending CPU erase list (s.3.5): added by a guest thread, removed by the erase command on GuestGpu.
	[[nodiscard]] static uint64_t G3PendAdd(uint64_t vaddr, uint64_t size);
	static void                   G3PendDone(uint64_t id);
	// Seeds (s.3.5).
	static void G3CpuSeed(uint64_t vaddr, uint64_t size);
	static void G3CpSeed(uint64_t vaddr, uint64_t size);
	static void G3GdsSeed(uint64_t offset, uint64_t size);
	static void G3PrefSeed(uint64_t vaddr, uint64_t size);
	static void G3Flip(Image& image);
	// P3 copies: mip = UINT32_MAX - the whole source to the whole destination; else source level 0 to level `mip`
	// from layer `layer` on (CopyImageMip).
	static void G3Copy(uint8_t site, Image& destination, Image& source, uint32_t mip, uint32_t layer);
	// Logical clears [RC2] (under TextureCache::m_lock).
	static void G3MetaClear(TextureCache& cache, uint64_t address);
	static void G3MetaFill(TextureCache& cache, uint64_t address, uint32_t clear_mask, bool pending);
	static void G3MetaAdopt(Image& image, uint64_t address);
	// ROADMAP s122 item 47(v): an image linked to a metadata surface with a nonzero clear mask after the clear event
	// (PrepareDccClear, PrepareCmaskClear, FindDepthTarget); seeded - a clear state with no clear event (HTILE seed).
	static void G3MetaLate(Image& image, uint64_t address, uint32_t mask, bool seeded);
	// ROADMAP s122 item 47(g): SynchronizeBufferFromImage writes guest range [vaddr, +size) with no writer.
	static void G3SyncImg(uint64_t vaddr, uint64_t size);
	// ROADMAP s122 item 47(g): the graph read of a texel buffer binding, after its ObtainBuffer (see ReadBuffer).
	static void G3ReadBufferLate(uint64_t vaddr, uint64_t size, bool written);
	// ROADMAP s122 item 47(a): the W1 writes AcquireRenderTargets queued, after every image read of the draw.
	static void G3ApplyAttach();
	// ROADMAP s122 item 47(e), N4: a read of the subresources `sub` of an image by the running operation.
	static void G3ReadSub(TextureCache& cache, ImageId id, const Sub& sub);
	// ROADMAP s122 item 47(b): the HTILE clear materialized at a target acquisition (load-op or explicit clear) - no
	// write event, an Lt write of the trigger on the depth of the view.
	static void G3MatDepth(TextureCache& cache, ImageId id, const ImageViewInfo& view);
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_TEXTURECACHE_H_
