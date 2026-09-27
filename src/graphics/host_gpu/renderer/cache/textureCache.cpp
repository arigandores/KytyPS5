#include "graphics/host_gpu/renderer/cache/textureCache.h"

#include "common/alignment.h"
#include "common/assert.h"
#include "common/drawStat.h"
#include "common/emulatorConfig.h"
#include "common/envFlag.h"
#include "common/frameStats.h"
#include "common/gates.h"
#include "common/gates.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "graphics/guest_gpu/gpu_format.h"
#include "graphics/guest_gpu/tile.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/cache/bufferCache.h"
#include "graphics/host_gpu/renderer/commandScheduler.h"
#include "graphics/host_gpu/renderer/image/imageView.h"
#include "graphics/host_gpu/renderer/image/textureCommon.h"
#include "graphics/host_gpu/renderer/image/tiler.h"
#include "graphics/host_gpu/renderer/render.h"
#include "kernel/memory.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cinttypes>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <limits>
#include <map>
#include <memory>
#include <mutex>
#include <set>
#include <span>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <vulkan/vulkan_format_traits.hpp>

namespace Libs::Graphics {

namespace {

constexpr uint64_t NumFramesBeforeRemoval = 32;

// Wall time of a scope, also in lite frame tracing (a few calls per frame; Scope times only with
// detailed timers).
struct LiteTimer {
	Common::FrameStats::Counter counter;
	uint64_t                    t0 = Common::FrameStats::NowNs();
	~LiteTimer() { Common::FrameStats::Add(counter, Common::FrameStats::NowNs() - t0); }
};

bool WatchImageRange(uint64_t address, uint64_t size) {
	static const uint64_t watched = [] {
		const auto* value = std::getenv("KYTY_IMAGE_WATCH");
		return value == nullptr ? uint64_t {0} : std::strtoull(value, nullptr, 0);
	}();
	return watched != 0 && size != 0 && address <= watched && watched - address < size;
}

void TraceWatchedImage(const char* event, const Image& image, uint64_t address = 0, uint64_t size = 0) {
	if (!WatchImageRange(image.info.data.address, image.info.data.size)) return;
	LOGF("ImageWatch: frame=%u event=%s image=0x%016" PRIx64 " size=0x%" PRIx64
	     " affected=0x%016" PRIx64 "+0x%" PRIx64 " cpu=%u buffer=%u gpu=%u meta=%u:0x%016" PRIx64 "+0x%" PRIx64 "\n",
	     GpuTimeProfiler::Frame(), event, image.info.data.address, image.info.data.size, address, size,
	     image.IsCpuDirty(), image.IsBufferModified(), image.IsGpuModified(),
	     static_cast<uint32_t>(image.info.metadata.kind), image.info.metadata.range.address,
	     image.info.metadata.range.size);
}

void TraceImageLifetime(const char* event, const ImageInfo& info, const char* reason, uint32_t line,
                        uint32_t last_frame = UINT32_MAX) {
	static const bool trace = Common::EnvFlagOn("KYTY_IMAGE_LIFETIME_TRACE");
	static const uint64_t min_bytes = [] {
		const auto* value = std::getenv("KYTY_IMAGE_LIFETIME_MIN_KB");
		return value == nullptr ? uint64_t {1u << 20u} : std::strtoull(value, nullptr, 10) << 10u;
	}();
	if (!trace || info.data.size < min_bytes) return;
	static const uint32_t first_frame = [] {
		const auto* value = std::getenv("KYTY_IMAGE_LIFETIME_FROM");
		return value == nullptr ? 0u : static_cast<uint32_t>(std::strtoul(value, nullptr, 10));
	}();
	const auto frame = GpuTimeProfiler::Frame();
	if (frame < first_frame) return;
	LOGF("ImageLife: event=%s reason=%s line=%u frame=%u guest=0x%016" PRIx64 " bytes=%" PRIu64
	     " w=%u h=%u d=%u mips=%u layers=%u fmt=%u tile=%u pitch=%u bpp=%u last_frame=%u\n",
	     event, reason, line, frame, info.data.address, info.data.size, info.extent.width,
	     info.extent.height, info.extent.depth, info.resources.levels, info.resources.layers,
	     static_cast<uint32_t>(info.pixel_format), static_cast<uint32_t>(info.tile_mode),
	     info.pitch, info.bytes_per_block, last_frame);
}

[[nodiscard]] bool DecodeDccClear(const TextureCache::ImageDesc& desc, uint8_t code,
                                  vk::ClearColorValue& clear) {
	switch (code) {
		case 0x00:
		case 0x20:
		case 0x40:
		case 0x80:
		case 0xc0: break;
		default: return false;
	}
	const auto& metadata = desc.info.metadata;
	const auto  format   = desc.view_info.format;
	if (code == 0x20) {
		// Clear-to-register is a color-buffer operation; the texture pipe cannot decode it.
		return desc.type == TextureCache::BindingType::RenderTarget &&
		       metadata.dcc_clear_register_valid &&
		       DecodePackedColorClear(format, metadata.dcc_clear_word, clear);
	}
	clear = {};
	if (code == 0x00) {
		return true;
	}
	switch (format) {
		case vk::Format::eR8Unorm:
		case vk::Format::eR8G8Unorm:
		case vk::Format::eR8G8B8A8Unorm:
		case vk::Format::eR8G8B8A8Srgb:
		case vk::Format::eB8G8R8A8Unorm:
		case vk::Format::eB8G8R8A8Srgb:
		case vk::Format::eA2B10G10R10UnormPack32:
		case vk::Format::eA2R10G10B10UnormPack32:
		case vk::Format::eR5G6B5UnormPack16:
		case vk::Format::eA1R5G5B5UnormPack16:
		case vk::Format::eR4G4B4A4UnormPack16:
		case vk::Format::eR16Unorm:
		case vk::Format::eR16G16Unorm:
		case vk::Format::eR16G16B16A16Unorm:
		case vk::Format::eR16Sfloat:
		case vk::Format::eR16G16Sfloat:
		case vk::Format::eR16G16B16A16Sfloat:
		case vk::Format::eR32Sfloat:
		case vk::Format::eR32G32Sfloat:
		case vk::Format::eR32G32B32A32Sfloat:
		case vk::Format::eB10G11R11UfloatPack32: break;
		default: return false;
	}
	const float          rgb   = (code & 0x80u) != 0 ? 1.0f : 0.0f;
	const float          alpha = (code & 0x40u) != 0 ? 1.0f : 0.0f;
	std::array<float, 4> channels {rgb, rgb, rgb, alpha};
	if (!metadata.dcc_alpha_msb) {
		std::swap(channels[0], channels[3]);
	}
	// DCC clear decoding clamps missing lanes before applying the format swizzle.
	const auto components = vk::componentCount(format);
	if (components == 1) {
		channels[0] = channels[3];
	} else if (components == 2) {
		channels[1] = channels[3];
	}
	switch (format) {
		case vk::Format::eB8G8R8A8Unorm:
		case vk::Format::eB8G8R8A8Srgb:
		case vk::Format::eA2R10G10B10UnormPack32:
		case vk::Format::eA1R5G5B5UnormPack16:
		case vk::Format::eR5G6B5UnormPack16: std::swap(channels[0], channels[2]); break;
		case vk::Format::eR4G4B4A4UnormPack16:
			std::reverse(channels.begin(), channels.end());
			break;
		default: break;
	}
	clear.float32 = channels;
	return true;
}

// A recorded metadata fill is a dword; the decoder above takes the repeated byte code of a DCC
// key. Callers that hold a fill value validate the repetition here.
[[nodiscard]] bool DecodeDccClearFill(const TextureCache::ImageDesc& desc, uint32_t fill,
                                      vk::ClearColorValue& clear) {
	const auto code = static_cast<uint8_t>(fill);
	if (fill != static_cast<uint32_t>(code) * 0x01010101u) {
		return false;
	}
	return DecodeDccClear(desc, code, clear);
}

[[nodiscard]] const char* BindingTypeName(TextureCache::BindingType type) {
	switch (type) {
		case TextureCache::BindingType::Texture: return "Texture";
		case TextureCache::BindingType::Storage: return "StorageTexture";
		case TextureCache::BindingType::RenderTarget: return "ColorTarget";
		case TextureCache::BindingType::DepthTarget: return "DepthTarget";
		case TextureCache::BindingType::VideoOut: return "VideoOut";
	}
	return "Image";
}

void NameImageBinding(GraphicContext& graphics, Image& image, vk::ImageView view,
                      TextureCache::BindingType type, const ImageViewInfo& view_info) {
	const auto* role = BindingTypeName(type);
	SetVulkanObjectNameF(
	    graphics.device, image.backing.image,
	    "Kyty.{}.Image[guest=0x{:016x} size=0x{:x} extent={}x{}x{} format={} mips={} layers={} "
	    "samples={}]",
	    role, image.info.data.address, image.info.data.size, image.info.extent.width,
	    image.info.extent.height, image.info.extent.depth,
	    static_cast<uint32_t>(image.info.pixel_format), image.info.resources.levels,
	    image.info.resources.layers, image.info.samples);
	SetVulkanObjectNameF(
	    graphics.device, view,
	    "Kyty.{}.View[guest=0x{:016x} format={} aspect=0x{:x} mip={}+{} layer={}+{}]", role,
	    image.info.data.address, static_cast<uint32_t>(view_info.format),
	    static_cast<vk::ImageAspectFlags::MaskType>(view_info.aspect), view_info.base_level,
	    view_info.level_count, view_info.base_layer, view_info.layer_count);
}

[[nodiscard]] std::vector<vk::BufferImageCopy> BuildDepthCopies(const ImageInfo& info,
                                                                uint64_t         slice_stride) {
	std::vector<vk::BufferImageCopy> copies(info.resources.layers);
	for (uint32_t layer = 0; layer < info.resources.layers; ++layer) {
		auto& copy             = copies[layer];
		copy.bufferOffset      = slice_stride * layer;
		copy.bufferRowLength   = info.pitch;
		copy.bufferImageHeight = info.extent.height;
		copy.imageSubresource  = {vk::ImageAspectFlagBits::eDepth, 0, layer, 1};
		copy.imageExtent       = {info.extent.width, info.extent.height, 1};
	}
	return copies;
}

[[nodiscard]] std::vector<GpuTileInfo> BuildDepthTiles(const ImageInfo& info) {
	TileBlockLayout block {};
	EXIT_NOT_IMPLEMENTED(
	    !TileGetBlockLayout(TileBlockFamily::Depth64KB, info.bytes_per_block, block));
	const auto               full_slice_size = info.data.size / info.resources.layers;
	std::vector<GpuTileInfo> tiles;
	tiles.reserve(info.resources.layers);
	for (uint32_t layer = 0; layer < info.resources.layers; ++layer) {
		const auto offset = full_slice_size * layer;
		tiles.push_back({block.family, block.bytes_per_element, offset, full_slice_size, offset,
		                 full_slice_size, 0, info.extent.width, info.extent.height, 1, info.pitch});
		tiles.back().surface_z = layer;
	}
	return tiles;
}

} // namespace

TextureCache::TextureCache(GraphicContext& graphics, CommandScheduler& scheduler,
                           PageManager& page_manager, BufferCache& buffer_cache)
    : m_graphics(graphics), m_scheduler(scheduler), m_page_manager(page_manager),
      m_blit_helper(graphics, scheduler),
      m_tiler(graphics, scheduler, buffer_cache.GetUtilityBuffer(MemoryUsage::Stream)),
      m_buffer_cache(buffer_cache),
      m_readback_linear_images(Config::ReadbackLinearImagesEnabled()) {
	if (m_graphics.CanReportMemoryUsage()) {
		constexpr int64_t GiB = 1024ll * 1024 * 1024;
		const auto        budget =
		    static_cast<int64_t>(std::min<uint64_t>(m_graphics.GetTotalMemoryBudget(), INT64_MAX));
		const auto threshold = std::min<int64_t>(budget, 8 * GiB);
		m_pressure_gc_memory = static_cast<uint64_t>(
		    std::max<int64_t>(std::min(budget - 6 * threshold / 10, budget - GiB), GiB + GiB / 2));
		m_critical_gc_memory = static_cast<uint64_t>(
		    std::max<int64_t>(std::min(budget - 2 * threshold / 10, budget - GiB / 2), 3 * GiB));
		m_trigger_gc_memory = static_cast<uint64_t>(std::max<int64_t>((budget - threshold) / 2, 0));
	}
}

TextureCache::~TextureCache() {
	m_slot_images.ForEach([&](ImageId id, const Image& image) {
		if (image.registered) {
			UnregisterImage(id);
		}
	});
}

bool TextureCache::SameBacking(const ImageInfo& cached, const ImageInfo& requested,
                               bool exact_format) {
	if (cached.data.address != requested.data.address) {
		return false;
	}
	if (cached.data.size != requested.data.size) {
		return false;
	}
	if (cached.extent != requested.extent) {
		return false;
	}
	if (cached.samples != requested.samples) {
		return false;
	}
	if (cached.bytes_per_block != requested.bytes_per_block) {
		return false;
	}
	if (cached.tile_mode != requested.tile_mode) {
		return false;
	}
	if (!ImageViewOps::FormatsCompatible(cached.pixel_format, requested.pixel_format) ||
	    (cached.type != requested.type && requested.extent != vk::Extent3D {1, 1, 1})) {
		return false;
	}
	if (exact_format && cached.pixel_format != requested.pixel_format) {
		return false;
	}
	return true;
}

namespace {

struct MipDeferConfig {
	bool     enabled;
	uint32_t levels;       // top levels left pending
	uint64_t frame_bytes;  // frame upload volume after which uploads defer
	uint64_t min_bytes;    // smallest deferred amount worth a second upload
	uint64_t budget_bytes; // pending bytes completed per frame at sampled binds
	bool     trace;
};

const MipDeferConfig& MipDefer() {
	static const MipDeferConfig config = [] {
		const auto env_u64 = [](const char* name, uint64_t fallback) {
			const char* value = std::getenv(name);
			return value != nullptr ? std::strtoull(value, nullptr, 10) : fallback;
		};
		const char* enabled = std::getenv("KYTY_MIP_DEFER");
		return MipDeferConfig {
		    .enabled = enabled == nullptr || enabled[0] != '0',
		    .levels  = static_cast<uint32_t>(
		        std::clamp<uint64_t>(env_u64("KYTY_MIP_DEFER_LEVELS", 1), 1, 8)),
		    .frame_bytes  = env_u64("KYTY_MIP_DEFER_FRAME_MB", 32) << 20u,
		    .min_bytes    = env_u64("KYTY_MIP_DEFER_MIN_KB", 256) << 10u,
		    .budget_bytes = env_u64("KYTY_MIP_DEFER_BUDGET_MB", 64) << 20u,
		    .trace        = Common::EnvFlagOn("KYTY_MIP_DEFER_TRACE"),
		};
	}();
	return config;
}

void MipDeferTrace(const char* what, const Image& image, uint64_t bytes) {
	if (!MipDefer().trace) {
		return;
	}
	LOGF("MipDefer: %s addr=0x%012" PRIx64 " size_kb=%" PRIu64 " %ux%u levels=%u layers=%u fmt=%u"
	     " pending=%u bytes_kb=%" PRIu64 "\n",
	     what, image.info.data.address, image.info.data.size / 1024u, image.info.extent.width,
	     image.info.extent.height, image.info.resources.levels, image.info.resources.layers,
	     static_cast<uint32_t>(image.info.guest_format), image.pending_levels, bytes / 1024u);
}

} // namespace

TextureCache::BindingType TextureCache::UploadBinding(const Image& image) {
	if (image.info.IsDepth()) {
		if (image.info.tile_mode == Prospero::TileMode::kDepth ||
		    image.info.tile_mode == Prospero::TileMode::kLinear) {
			return BindingType::DepthTarget;
		}
		return BindingType::Texture;
	}
	if (image.usage.render_target) {
		return BindingType::RenderTarget;
	}
	if (image.usage.video_out) {
		return BindingType::VideoOut;
	}
	return image.usage.storage ? BindingType::Storage : BindingType::Texture;
}

bool TextureCache::SafeToDownload(const Image& image) {
	if (!image.SafeToDownload()) {
		return false;
	}
	const auto range = image.info.data;
	return !m_buffer_cache.HasGpuDirtyBytes(range.address, range.size);
}

ImageId TextureCache::InsertImage(const ImageInfo& info) {
	LiteTimer insert_timer {Common::FrameStats::Counter::ImgInsertNs};
	TraceImageLifetime("create", info, __func__, __LINE__);
	Common::FrameStats::Add(Common::FrameStats::Counter::ImgInserts, 1);
	Common::DrawStat::Mark(Common::DrawStat::ImgNew);
	const auto id = m_slot_images.insert(m_graphics, m_scheduler, info);
	if (!info.data.Empty()) {
		RegisterImage(id);
	}
	return id;
}

void TextureCache::RegisterImage(ImageId id) {
	auto& image = m_slot_images[id];
	if (image.registered || image.info.data.Empty()) {
		EXIT("TextureCache: invalid image registration\n");
	}
	ImagePageTable::PageRange pages {};
	if (!ImagePageTable::TryGetPageRange(image.info.data.address, image.info.data.size, pages)) {
		EXIT("TextureCache: image registration is outside the guest address space\n");
	}
	ForEachPage(image.info.data.address, image.info.data.size, [this, id](uint64_t page) {
		// Gate "texfaulthint": raised before the image becomes findable (see InvalidateMemory).
		m_image_page_hint[page].fetch_add(1, std::memory_order_acq_rel);
		m_image_page_table[page].push_back(id);
	});
	image.registered = true;
	image.frame_accessed_last = GpuTimeProfiler::Frame();
	image.lru_id     = m_lru_cache.Insert(id, m_gc_tick);
	image.lru_touch_tick = m_gc_tick;
	m_total_used_memory += image.AccountedSize();
}

void TextureCache::UnregisterImage(ImageId id) {
	auto& image = m_slot_images[id];
	if (!image.registered) {
		return;
	}
	UntrackImage(id);
	ImagePageTable::PageRange pages {};
	if (!ImagePageTable::TryGetPageRange(image.info.data.address, image.info.data.size, pages)) {
		EXIT("TextureCache: registered image is outside the guest address space\n");
	}
	ForEachPage(image.info.data.address, image.info.data.size, [this, id](uint64_t page) {
		auto* owners = m_image_page_table.Find(page);
		if (owners == nullptr || !owners->Erase(id)) {
			EXIT("TextureCache: image missing from page owner index\n");
		}
		m_image_page_hint[page].fetch_sub(1, std::memory_order_acq_rel);
	});
	m_lru_cache.Free(image.lru_id);
	const auto accounted = image.AccountedSize();
	if (accounted > m_total_used_memory) {
		EXIT("TextureCache: image accounting underflow\n");
	}
	m_total_used_memory -= accounted;
	image.registered = false;
}

void TextureCache::DeleteImage(ImageId id) {
	auto* image = m_slot_images.try_get(id);
	if (image == nullptr || !image->registered) {
		return;
	}
	if (!image->depth_id) {
		std::vector<ImageId> associations;
		m_slot_images.ForEach([&](ImageId candidate, const Image& associated) {
			if (associated.depth_id == id) {
				associations.push_back(candidate);
			}
		});
		for (const auto association: associations) {
			FreeImage(association, __func__, __LINE__);
		}
	}
	if (image->IsGpuModified()) {
		EXIT("TextureCache: deleting a GPU-modified image without resolving its contents\n");
	}
	m_download_images.erase(id);
	if (image->info.HasMetadata()) {
		const auto metadata = m_surface_metas.find(image->info.metadata.range.address);
		if (metadata != m_surface_metas.end() &&
		    ((image->info.metadata.kind == ImageMetadataKind::Dcc &&
		      metadata->second.type == MetaDataInfo::Type::Dcc) ||
		     (image->info.metadata.kind == ImageMetadataKind::Cmask &&
		      metadata->second.type == MetaDataInfo::Type::CMask) ||
		     (image->info.metadata.kind == ImageMetadataKind::Htile &&
		      metadata->second.type == MetaDataInfo::Type::HTile))) {
			// A later binding may have reused this address for another metadata type.
			m_surface_metas.erase(metadata);
			BumpMetaEpoch();
		}
	}
	UnregisterImage(id);
	if (m_scheduler.Active()) {
		m_scheduler.DeferOperation([this, id] {
			// Erased once the GPU finished the tick that last used the image.
			if (auto* retired = m_slot_images.try_get(id)) {
				retired->recycle_backing = true;
			}
			m_slot_images.erase(id);
		});
	} else {
		m_slot_images.erase(id);
	}
}

void TextureCache::FreeImage(ImageId id, const char* reason, uint32_t line) {
	LiteTimer free_timer {Common::FrameStats::Counter::ImgFreeNs};
	Common::FrameStats::Add(Common::FrameStats::Counter::ImgFrees, 1);
	Common::DrawStat::Mark(Common::DrawStat::ImgNew);
	auto& image = m_slot_images[id];
	TraceImageLifetime("free", image.info, reason, line, image.frame_accessed_last);
	static const bool state_trace = Common::EnvFlagOn("KYTY_IMAGE_STATE_TRACE");
	if (state_trace && image.info.data.size >= (1u << 20u)) {
		LOGF("ImageStateFree: frame=%u guest=0x%016" PRIx64 " reason=%s gpu=%d cpu=%d maybe=%d buffer=%d metadata=%u\n",
		     GpuTimeProfiler::Frame(), image.info.data.address, reason,
		     image.IsGpuModified(), image.IsDefinitelyCpuDirty(), image.IsMaybeCpuDirty(),
		     image.IsBufferModified(), static_cast<uint32_t>(image.info.metadata.kind));
	}
	if (image.IsGpuModified()) {
		image.ClearGpuModified();
	}
	DeleteImage(id);
}

void TextureCache::TouchImage(Image& image) {
	if (image.registered) {
		// Stored only on change: an equal store still dirties the line.
		if (const auto frame = GpuTimeProfiler::Frame(); image.frame_accessed_last != frame) {
			image.frame_accessed_last = frame;
		}
		m_lru_touch_calls++;
		// A bind touches its image 5-6 times; the LRU node (a separate deque block) is cold and
		// Touch returns on `item.tick >= tick` for all but the first touch of a GC tick. The copy is
		// only ever set to a tick Touch/Insert was called with, so a matching copy proves the item
		// already holds this tick (items are re-inserted at m_gc_tick, which only grows).
		if (image.lru_touch_tick == m_gc_tick) {
			m_lru_touch_repeats++;
			if (Common::Gates::Enabled(Common::Gates::Gate::TexLru)) {
				return;
			}
		} else {
			image.lru_touch_tick = m_gc_tick;
		}
		m_lru_cache.Touch(image.lru_id, m_gc_tick);
	}
}

void TextureCache::MarkAsMaybeDirty(ImageId id, Image& image) {
	image.MarkMaybeCpuDirty();
	if (image.NeedsMaybeCpuHash()) {
		image.SetMaybeCpuHash(image.HashGuestEdges());
	}
	UntrackImage(id);
}

void TextureCache::TrackImage(ImageId id) {
	auto& image = m_slot_images[id];
	if (!image.registered) {
		return;
	}
	const auto image_begin = image.SourceRange().address;
	const auto image_end   = image.SourceRange().End();
	if (image_begin == image.track_addr && image_end == image.track_addr_end) {
		return;
	}
	if (!image.IsTracked()) {
		image.track_addr     = image_begin;
		image.track_addr_end = image_end;
		m_page_manager.UpdatePageWatchersDeferred(image_begin, image_end - image_begin);
		return;
	}
	if (image_begin < image.track_addr) {
		TrackImageHead(id);
	}
	if (image.track_addr_end < image_end) {
		TrackImageTail(id);
	}
}

void TextureCache::TrackImageHead(ImageId id) {
	auto& image = m_slot_images[id];
	if (!image.registered) {
		return;
	}
	const auto image_begin = image.SourceRange().address;
	if (image_begin == image.track_addr) {
		return;
	}
	if (!image.IsTracked() || image_begin > image.track_addr) {
		EXIT("TextureCache: invalid image head tracking range\n");
	}
	const auto size  = image.track_addr - image_begin;
	image.track_addr = image_begin;
	m_page_manager.UpdatePageWatchersDeferred(image_begin, size);
}

void TextureCache::TrackImageTail(ImageId id) {
	auto& image = m_slot_images[id];
	if (!image.registered) {
		return;
	}
	const auto image_end = image.SourceRange().End();
	if (image_end == image.track_addr_end) {
		return;
	}
	if (!image.IsTracked() || image.track_addr_end > image_end) {
		EXIT("TextureCache: invalid image tail tracking range\n");
	}
	const auto address   = image.track_addr_end;
	const auto size      = image_end - address;
	image.track_addr_end = image_end;
	m_page_manager.UpdatePageWatchersDeferred(address, size);
}

void TextureCache::UntrackImage(ImageId id) {
	auto& image = m_slot_images[id];
	if (!image.IsTracked()) {
		return;
	}
	const auto address   = image.track_addr;
	const auto size      = image.track_addr_end - image.track_addr;
	image.bind_stamp.fetch_add(1);
	image.track_addr     = 0;
	image.track_addr_end = 0;
	if (size != 0) {
		PageManager::SpinHeld spin_held; // callers hold m_lock (prot_spin_*)
		m_page_manager.UpdatePageWatchers<false>(address, size);
	}
}

void TextureCache::UntrackImageHead(ImageId id) {
	auto&      image = m_slot_images[id];
	const auto begin = image.info.data.address;
	if (!image.IsTracked() || begin < image.track_addr) {
		return;
	}
	const auto address = Common::AlignDown(begin + TRACKER_PAGE_SIZE, TRACKER_PAGE_SIZE);
	const auto size    = address - begin;
	image.bind_stamp.fetch_add(1);
	image.track_addr   = address;
	if (image.track_addr == image.track_addr_end) {
		MarkAsMaybeDirty(id, image);
	}
	if (size != 0) {
		PageManager::SpinHeld spin_held; // callers hold m_lock (prot_spin_*)
		m_page_manager.UpdatePageWatchers<false>(begin, size);
	}
}

void TextureCache::UntrackImageTail(ImageId id) {
	auto&      image = m_slot_images[id];
	const auto end   = image.info.data.End();
	if (!image.IsTracked() || image.track_addr_end < end) {
		return;
	}
	const auto address   = Common::AlignDown(end, TRACKER_PAGE_SIZE);
	const auto size      = end - address;
	image.bind_stamp.fetch_add(1);
	image.track_addr_end = address;
	if (image.track_addr == image.track_addr_end) {
		MarkAsMaybeDirty(id, image);
	}
	if (size != 0) {
		PageManager::SpinHeld spin_held; // callers hold m_lock (prot_spin_*)
		m_page_manager.UpdatePageWatchers<false>(address, size);
	}
}

void TextureCache::TrackImageDownload(ImageId id, Image& image) {
	if (m_readback_linear_images && !image.info.IsTiled() && !image.info.data.Empty()) {
		if (!image.IsGpuModified()) {
			EXIT("TextureCache: cannot enroll a non-GPU-owned image for download\n");
		}
		m_download_images.insert(id);
	}
}

TextureCache::ImageIds TextureCache::FindImagesInRegion(uint64_t address, uint64_t size,
                                                        bool page_overlap) const {
	ImagePageTable::PageRange pages {};
	if (!ImagePageTable::TryGetPageRange(address, size, pages)) {
		return {};
	}

	uint32_t query_epoch = ++m_image_query_epoch;
	if (query_epoch == 0) {
		m_slot_images.ForEach([](ImageId, const Image& image) { image.query_epoch = 0; });
		query_epoch = ++m_image_query_epoch;
	}

	ImageIds result;
	ForEachPage(address, size, [&](uint64_t page) {
		const auto* owners = m_image_page_table.Find(page);
		if (owners == nullptr) {
			return;
		}
		owners->ForEach([&](ImageId id) {
			auto* image = m_slot_images.try_get(id);
			if (image == nullptr) {
				return;
			}
			if (image->query_epoch == query_epoch) {
				return;
			}
			image->query_epoch = query_epoch;
			if (image->Overlaps(address, size, page_overlap)) {
				result.push_back(id);
			}
		});
	});
	return result;
}

ImageId TextureCache::GetNullImage(const ImageDesc& desc) {
	const auto format = desc.info.pixel_format;
	if (const auto found = m_null_images.find(format); found != m_null_images.end()) {
		return found->second;
	}
	ImageInfo info {};
	info.pixel_format    = desc.info.pixel_format;
	info.guest_format    = desc.info.guest_format;
	info.type            = Prospero::ImageType::kColor2D;
	info.extent          = {1, 1, 1};
	info.resources       = {1, 1};
	info.pitch           = 1;
	info.bytes_per_block = std::max(desc.info.bytes_per_block, 1u);
	info.samples         = 1;
	info.tile_mode       = Prospero::TileMode::kLinear;
	info.mip_layout[0]   = {0, info.bytes_per_block, 1, 1};
	const auto id        = InsertImage(info);
	m_null_images.emplace(format, id);
	return id;
}

void TextureCache::ValidateImageDesc(const ImageDesc& desc) const {
	ImageOps::Validate(desc.info);
	if (desc.view_info.format == vk::Format::eUndefined || desc.view_info.level_count == 0 ||
	    desc.view_info.layer_count == 0 ||
	    desc.view_info.base_level >= desc.info.resources.levels ||
	    desc.view_info.level_count > desc.info.resources.levels - desc.view_info.base_level ||
	    (!desc.info.IsVolume() &&
	     (desc.view_info.base_layer >= desc.info.resources.layers ||
	      desc.view_info.layer_count > desc.info.resources.layers - desc.view_info.base_layer))) {
		EXIT("TextureCache: invalid image view description\n");
	}
	if (desc.type == BindingType::DepthTarget && !IsSupportedDepthTargetFormat(desc.info)) {
		EXIT("TextureCache: unsupported depth image description\n");
	}
	if (desc.type == BindingType::VideoOut && !IsSupportedVideoOutFormat(desc.info)) {
		EXIT("TextureCache: unsupported video-out image description\n");
	}
	if (desc.type == BindingType::VideoOut &&
	    desc.info.metadata.compression == VideoOutCompression::Unsupported) {
		EXIT("TextureCache: unsupported compressed video-out description\n");
	}
}

void TextureCache::RestoreFullImageSource(ImageId id) {
	auto& image = m_slot_images[id];
	if (image.source_first_level == 0) return;
	ImageDesc full;
	full.info = image.info;
	ConfigureImageSourceUnlocked(id, full);
	InitializeImage(id, false);
}

void TextureCache::PrepareImageCopy(ImageId id) {
	RestoreFullImageSource(id);
	auto& image = m_slot_images[id];
	CompletePendingUpload(image);
	if (image.IsCpuDirty()) {
		image.RefreshComplete();
	}
}

void TextureCache::RefreshCopySource(ImageId id) {
	RestoreFullImageSource(id);
	auto& image = m_slot_images[id];
	RefreshImage(id);
	if (image.IsDefinitelyCpuDirty()) {
		EXIT("TextureCache: image copy source remained CPU-dirty after refresh\n");
	}
}

bool TextureCache::CopyD16(Image& destination, Image& source) {
	const bool source_depth      = source.info.IsDepth();
	const bool destination_depth = destination.info.IsDepth();
	if (source_depth == destination_depth) {
		return false;
	}
	auto&      depth          = source_depth ? source : destination;
	auto&      color          = source_depth ? destination : source;
	const auto transfer_bytes = DepthAspectTransferBytes(depth.backing.format);
	if (depth.info.bytes_per_block != sizeof(uint16_t) ||
	    color.info.bytes_per_block != sizeof(uint16_t) || transfer_bytes != sizeof(uint32_t)) {
		return false;
	}
	EXIT_IF(source.backing.samples != 1 || destination.backing.samples != 1 ||
	        source.info.resources.levels != 1 || destination.info.resources.levels != 1 ||
	        source.info.extent != destination.info.extent ||
	        source.info.resources.layers != destination.info.resources.layers);

	const auto     layers = depth.info.resources.layers;
	const uint64_t depth_slice =
	    static_cast<uint64_t>(depth.info.pitch) * depth.info.extent.height * transfer_bytes;
	const uint64_t color_slice =
	    static_cast<uint64_t>(color.info.pitch) * color.info.extent.height * sizeof(uint16_t);
	EXIT_IF(layers == 0 || depth_slice > UINT64_MAX / layers || color_slice > UINT64_MAX / layers);
	const auto                       depth_size = depth_slice * layers;
	const auto                       color_size = color_slice * layers;
	std::vector<vk::BufferImageCopy> depth_copies(layers);
	std::vector<vk::BufferImageCopy> color_copies(layers);
	for (uint32_t layer = 0; layer < layers; layer++) {
		depth_copies[layer].bufferOffset      = depth_slice * layer;
		depth_copies[layer].bufferRowLength   = depth.info.pitch;
		depth_copies[layer].bufferImageHeight = depth.info.extent.height;
		depth_copies[layer].imageSubresource  = {vk::ImageAspectFlagBits::eDepth, 0, layer, 1};
		depth_copies[layer].imageExtent       = depth.info.extent;
		color_copies[layer].bufferOffset      = color_slice * layer;
		color_copies[layer].bufferRowLength   = color.info.pitch;
		color_copies[layer].bufferImageHeight = color.info.extent.height;
		color_copies[layer].imageSubresource  = {vk::ImageAspectFlagBits::eColor, 0, layer, 1};
		color_copies[layer].imageExtent       = color.info.extent;
	}

	auto                         depth_buffer = m_tiler.GetScratchBuffer(depth_size);
	auto                         color_buffer = m_tiler.GetScratchBuffer(color_size);
	const TileManager::D16Layout promote_layout {
	    .width               = depth.info.extent.width,
	    .height              = depth.info.extent.height,
	    .layers              = layers,
	    .source_row_stride   = static_cast<uint64_t>(color.info.pitch) * sizeof(uint16_t),
	    .target_row_stride   = static_cast<uint64_t>(depth.info.pitch) * transfer_bytes,
	    .source_slice_stride = color_slice,
	    .target_slice_stride = depth_slice,
	};
	const bool d32 = DepthAspectTransferFormat(depth.backing.format) == vk::Format::eD32Sfloat;
	if (source_depth) {
		source.Download(depth_copies, depth_buffer.buffer, depth_buffer.offset, depth_buffer.size);
		m_tiler.ConvertD16(depth_buffer, color_buffer, TileManager::D16Direction::Demote, d32,
		                   {.width               = promote_layout.width,
		                    .height              = promote_layout.height,
		                    .layers              = promote_layout.layers,
		                    .source_row_stride   = promote_layout.target_row_stride,
		                    .target_row_stride   = promote_layout.source_row_stride,
		                    .source_slice_stride = promote_layout.target_slice_stride,
		                    .target_slice_stride = promote_layout.source_slice_stride});
		destination.Upload(color_copies, color_buffer.buffer, color_buffer.offset,
		                   color_buffer.size);
	} else {
		source.Download(color_copies, color_buffer.buffer, color_buffer.offset, color_buffer.size);
		m_tiler.ConvertD16(color_buffer, depth_buffer, TileManager::D16Direction::Promote, d32,
		                   promote_layout);
		destination.Upload(depth_copies, depth_buffer.buffer, depth_buffer.offset,
		                   depth_buffer.size);
	}
	return true;
}

void TextureCache::CopyImage(ImageId destination_id, ImageId source_id) {
	Common::DrawStat::Mark(Common::DrawStat::ImgNew);
	Common::DrawStat::Cut(Common::DrawStat::EdgeUpload);
	RefreshCopySource(source_id);
	// Session 124, knob "skipceil" = 3 (closure census, [RC1]): the copy is a lazy write of site p3a, recorded below.
	const SkcCensus::LazyScope skc3_lazy(SkcCensus::LazyP3a);
	auto& destination = m_slot_images[destination_id];
	auto& source      = m_slot_images[source_id];
	TrackImage(destination_id);
	if (source.backing.samples != destination.backing.samples) {
		EXIT("TextureCache: cannot issue an unequal-sample image copy\n");
	}
	PrepareImageCopy(destination_id);
	if (source.IsBufferModified()) {
		if (source.info.data == destination.info.data) {
			destination.MarkBufferModified();
		}
		return;
	}
	const bool source_depth = source.info.IsDepth();
	const bool dest_depth   = destination.info.IsDepth();
	const bool direct_copy =
	    source.backing.format == destination.backing.format ||
	    (!source_depth && !dest_depth &&
	     vk::blockSize(source.backing.format) == vk::blockSize(destination.backing.format));
	if (direct_copy) {
		destination.CopyImage(source);
	} else if (!CopyD16(destination, source)) {
		if (source.backing.samples != 1 || destination.backing.samples != 1) {
			EXIT("TextureCache: cross-format multisample image copy is unsupported\n");
		}
		auto& copy_buffer = m_buffer_cache.GetUtilityBuffer(MemoryUsage::DeviceLocal);
		destination.CopyImageWithBuffer(source, copy_buffer);
	}
	if (Common::SkipCeil::t_mode == 3) [[unlikely]] {
		SkcCensus::G3Copy(SkcCensus::LazyP3a, destination, source, UINT32_MAX, 0); // Session 124 ([RC1])
	}
	Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 47(z), N1
	{
		// Session 123, knob "skipceil" = 2 (census, [P3]): the destination takes the source's D / T label.
		const SkcCensus::CarryScope skc_carry(destination, source);
		if (source.IsGpuModified()) {
			destination.MarkGpuModified();
		}
	}
	destination.ClearBufferModified();
}

void TextureCache::CopyImageMip(ImageId destination_id, ImageId source_id, uint32_t mip,
                                uint32_t layer) {
	Common::DrawStat::Mark(Common::DrawStat::ImgNew);
	Common::DrawStat::Cut(Common::DrawStat::EdgeUpload);
	RefreshCopySource(source_id);
	// Session 124, knob "skipceil" = 3 (closure census, [RC1]): the copy is a lazy write of site p3b, recorded below.
	const SkcCensus::LazyScope skc3_lazy(SkcCensus::LazyP3b);
	auto& destination = m_slot_images[destination_id];
	auto& source      = m_slot_images[source_id];
	TrackImage(destination_id);
	if (source.IsBufferModified() || source.backing.samples != destination.backing.samples) {
		EXIT("TextureCache: invalid mip-copy ownership or sample count\n");
	}
	destination.CopyMip(source, mip, layer);
	if (Common::SkipCeil::t_mode == 3) [[unlikely]] {
		SkcCensus::G3Copy(SkcCensus::LazyP3b, destination, source, mip, layer); // Session 124 ([RC1])
	}
	Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 47(z), N1
	// Session 123, knob "skipceil" = 2 (census, [P3]): the destination takes the source's D / T label.
	const SkcCensus::CarryScope skc_carry(destination, source);
	if (source.IsGpuModified()) {
		destination.MarkGpuModified();
	}
}

ImageId TextureCache::ResolveDepthOverlap(const ImageInfo& requested, BindingType binding,
                                          ImageId cached_id) {
	LiteTimer overlap_timer {Common::FrameStats::Counter::ImgOverlapNs};
	auto& cached = m_slot_images[cached_id];
	if (!cached.info.IsDepth() && !requested.IsDepth()) {
		return {};
	}
	const bool stencil_match = requested.HasStencil() == cached.info.HasStencil();
	const bool bpp_match     = requested.bytes_per_block == cached.info.bytes_per_block;
	// PPSA04264
	const bool raw_d16_texture =
	    binding == BindingType::Texture && cached.info.IsDepth() &&
	    cached.info.guest_format == Prospero::BufferFormat::k16UNorm &&
	    requested.guest_format == Prospero::BufferFormat::k16UInt &&
	    requested.pixel_format == vk::Format::eR16Uint && cached.backing.samples == 1 &&
	    requested.samples == 1 && requested.data == cached.info.data &&
	    requested.extent == cached.info.extent && requested.resources == cached.info.resources &&
	    requested.type == cached.info.type && requested.pitch == cached.info.pitch &&
	    requested.tile_mode == cached.info.tile_mode && !requested.HasStencil() &&
	    !cached.info.HasStencil() && !requested.HasMetadata() && !cached.info.HasMetadata();
	// PPSA04264
	const bool retain_cached_layout =
	    requested.samples == 1 && cached.info.samples == 1 && cached.backing.samples == 1 &&
	    requested.bytes_per_block == cached.info.bytes_per_block &&
	    requested.data.address == cached.info.data.address &&
	    requested.data.size < cached.info.data.size && requested.extent == cached.info.extent &&
	    requested.resources.levels == 1 && cached.info.resources.levels == 1 &&
	    requested.resources.layers != 0 && cached.info.resources.layers != 0 &&
	    requested.resources.layers < cached.info.resources.layers &&
	    requested.type == cached.info.type && requested.pitch == cached.info.pitch &&
	    requested.tile_mode == cached.info.tile_mode && requested.mip_layout[0].offset == 0 &&
	    cached.info.mip_layout[0].offset == 0 &&
	    requested.mip_layout[0].size == requested.data.size &&
	    cached.info.mip_layout[0].size == cached.info.data.size &&
	    requested.data.size % requested.resources.layers == 0 &&
	    cached.info.data.size % cached.info.resources.layers == 0 &&
	    requested.data.size / requested.resources.layers ==
	        cached.info.data.size / cached.info.resources.layers &&
	    !requested.HasStencil() && !cached.info.HasStencil() && !requested.HasMetadata() &&
	    !cached.info.HasMetadata();
	bool recreate = cached.info.resources < requested.resources;
	switch (binding) {
		case BindingType::Texture:
			recreate |= requested.IsDepth() && !cached.info.IsDepth();
			recreate |= raw_d16_texture;
			break;
		case BindingType::Storage: recreate |= cached.info.IsDepth(); break;
		case BindingType::RenderTarget: recreate |= cached.info.IsDepth(); break;
		case BindingType::DepthTarget:
			recreate |= !cached.info.IsDepth();
			recreate |= cached.info.IsDepth() && !(stencil_match && bpp_match);
			break;
		case BindingType::VideoOut: recreate |= cached.info.IsDepth(); break;
	}
	if (!recreate) {
		return cached_id;
	}
	RefreshImage(cached_id);
	auto info = requested;
	if (retain_cached_layout) {
		info.data       = cached.info.data;
		info.resources  = cached.info.resources;
		info.mip_layout = cached.info.mip_layout;
	} else {
		info.resources = std::max(requested.resources, cached.info.resources);
	}
	info.htile_clear_mask     = 0;
	const auto replacement_id = InsertImage(info);
	auto&      replacement    = m_slot_images[replacement_id];
	replacement.usage         = cached.usage;
	if (cached.binding.is_bound || cached.binding.is_target) {
		cached.binding.needs_rebind = true;
	}
	if (cached.backing.samples == replacement.backing.samples) {
		const bool copy_supported =
		    cached.backing.samples == 1 || cached.backing.format == replacement.backing.format ||
		    (!cached.info.IsDepth() && !replacement.info.IsDepth() &&
		     ImageViewOps::FormatsCompatible(cached.backing.format, replacement.backing.format));
		if (copy_supported) {
			CopyImage(replacement_id, cached_id);
		} else {
			LOGF_COLOR(Log::Color::BrightYellow,
			           "TextureCache: unsupported cross-format multisample depth copy\n");
		}
	} else if (cached.backing.samples == 1 && replacement.backing.samples > 1 &&
	           replacement.info.IsDepth()) {
		RefreshCopySource(cached_id);
		if (cached.IsBufferModified() || cached.IsDefinitelyCpuDirty()) {
			EXIT("TextureCache: multisample depth conversion source is not native-current\n");
		}
		PrepareImageCopy(replacement_id);
		// Session 124, knob "skipceil" = 3 (closure census, [RC1]): the reinterpretation is a lazy write of site p3c.
		const SkcCensus::LazyScope skc3_lazy(SkcCensus::LazyP3c);
		m_blit_helper.ReinterpretColorAsMsDepth(cached, replacement);
		if (Common::SkipCeil::t_mode == 3) [[unlikely]] {
			SkcCensus::G3Copy(SkcCensus::LazyP3c, replacement, cached, UINT32_MAX, 0);
		}
		Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 47(z), N1
		// Session 123, knob "skipceil" = 2 (census, [P3]): the replacement takes the D / T label of the cached image.
		const SkcCensus::CarryScope skc_carry(replacement, cached);
		CommitGpuWrite(replacement);
	} else {
		LOGF_COLOR(Log::Color::BrightYellow,
		           "TextureCache: unsupported unequal-sample depth overlap copy (%u -> %u)\n",
		           cached.backing.samples, replacement.backing.samples);
	}
	FreeImage(cached_id, __func__, __LINE__);
	return replacement_id;
}

TextureCache::OverlapResult TextureCache::ResolveOverlap(const ImageInfo& requested,
                                                         BindingType binding, ImageId cached_id,
                                                         ImageId merged_id) {
	auto owner = m_slot_images.try_get(cached_id);
	if (owner == nullptr) {
		return {merged_id};
	}
	auto&      cached       = *owner;
	const auto current_tick = m_scheduler.CurrentTick();
	const bool safe_to_delete =
	    current_tick - std::min(current_tick, cached.tick_accessed_last) > NumFramesBeforeRemoval;

	const uint32_t requested_block = requested.bytes_per_block * requested.samples;
	const uint32_t cached_block    = cached.info.bytes_per_block * cached.info.samples;
	if (requested.data.address == cached.info.data.address &&
	    requested.BlockExtent() == cached.info.BlockExtent() && requested_block == cached_block) {
		if (const auto depth_id = ResolveDepthOverlap(requested, binding, cached_id)) {
			return {depth_id};
		}
		if (requested.IsBlock() && !cached.info.IsBlock()) {
			return {ExpandImage(requested, cached_id)};
		}
		if (requested.data.size == cached.info.data.size &&
		    (requested.IsVolume() || cached.info.IsVolume())) {
			return {ExpandImage(requested, cached_id)};
		}
		// Equal pitch does not imply equal mip placement: a changed extent can move
		// a level into or out of the mip tail. These are separate guest layouts.
		if (requested.tile_mode != cached.info.tile_mode ||
		    (requested.resources == cached.info.resources &&
		     requested.mip_layout != cached.info.mip_layout)) {
			if (safe_to_delete) {
				FreeImage(cached_id, __func__, __LINE__);
			}
			return {merged_id};
		}
		// PPSA08394
		if (requested.data.size == cached.info.data.size &&
		    requested.resources == cached.info.resources && requested.type == cached.info.type &&
		    requested.extent.width > cached.info.extent.width &&
		    requested.extent.height >= cached.info.extent.height &&
		    requested.extent.depth >= cached.info.extent.depth &&
		    ImageViewOps::FormatsCompatible(cached.info.pixel_format, requested.pixel_format)) {
			return {ExpandImage(requested, cached_id)};
		}
		if (requested.pixel_format != cached.info.pixel_format ||
		    requested.data.size <= cached.info.data.size) {
			const auto result_id = merged_id ? merged_id : cached_id;
			const auto result    = m_slot_images.try_get(result_id);
			return {result != nullptr && ImageViewOps::FormatsCompatible(result->info.pixel_format,
			                                                             requested.pixel_format)
			            ? result_id
			            : ImageId {}};
		}
		if (requested.type == cached.info.type && requested.resources > cached.info.resources) {
			return {ExpandImage(requested, cached_id)};
		}
		EXIT("TextureCache: unresolvable equal-address image overlap, address=0x%016" PRIx64
		     " requested=%ux%u "
		     "cached=%ux%u requested_size=0x%016" PRIx64 " cached_size=0x%016" PRIx64
		     " type=%u/%u tile=%u/%u\n",
		     requested.data.address, requested.resources.levels, requested.resources.layers,
		     cached.info.resources.levels, cached.info.resources.layers, requested.data.size,
		     cached.info.data.size, static_cast<uint32_t>(requested.type),
		     static_cast<uint32_t>(cached.info.type), static_cast<uint32_t>(requested.tile_mode),
		     static_cast<uint32_t>(cached.info.tile_mode));
	}

	const int32_t requested_mip = requested.MipOf(cached.info);
	if (requested_mip >= 0) {
		const int32_t layer = requested.SliceOf(cached.info, requested_mip);
		return {cached_id, requested_mip, layer};
	}

	const int32_t mip = cached.info.MipOf(requested);
	if (mip >= 0) {
		const int32_t layer = cached.info.SliceOf(requested, mip);
		if (!merged_id) {
			return {ExpandImage(requested, cached_id)};
		}
		cached.binding.needs_rebind |= cached.binding.is_bound || cached.binding.is_target;
		m_slot_images[merged_id].binding.is_target |= cached.binding.is_target;
		CopyImageMip(merged_id, cached_id, static_cast<uint32_t>(mip),
		             static_cast<uint32_t>(layer));
		FreeImage(cached_id, __func__, __LINE__);
		return {merged_id};
	}
	if (requested.data.address >= cached.info.data.address && safe_to_delete) {
		FreeImage(cached_id, __func__, __LINE__);
	}
	return {merged_id};
}

ImageId TextureCache::ExpandImage(const ImageInfo& info, ImageId source_id) {
	RefreshCopySource(source_id);
	const auto expanded_id = InsertImage(info);
	auto&      expanded    = m_slot_images[expanded_id];
	auto&      source      = m_slot_images[source_id];
	expanded.usage         = source.usage;
	if (source.binding.is_bound || source.binding.is_target) {
		source.binding.needs_rebind = true;
	}
	InitializeImage(expanded_id, false);
	const int32_t mip   = source.info.MipOf(info);
	const int32_t layer = source.info.SliceOf(info, mip);
	if (layer >= 0) {
		CopyImageMip(expanded_id, source_id, static_cast<uint32_t>(mip),
		             static_cast<uint32_t>(layer));
	} else {
		CopyImage(expanded_id, source_id);
	}
	FreeImage(source_id, __func__, __LINE__);
	return expanded_id;
}

struct TextureCache::TextureTransfer {
	TextureUploadLayout              layout;
	std::vector<vk::BufferImageCopy> regions;
	std::vector<GpuTileInfo>         tiles;
	bool                             swap_bgra16 = false;
	bool                             valid       = false;

	[[nodiscard]] uint64_t LinearSize() const {
		uint64_t size = 0;
		for (const auto& tile: tiles) {
			size = std::max(size, tile.linear_offset + tile.linear_size);
		}
		return size;
	}
};

struct TextureCache::ImageDownload {
	TextureTransfer texture;
	bool                depth_target = false;
	bool                valid        = false;
};

TextureCache::TextureTransfer
TextureCache::BuildTextureTransfer(const Image& image, BindingType binding,
                                    TransferDirection direction) const {
	return BuildTextureTransfer(image.info, image.backing.samples, binding, direction);
}

TextureCache::TextureTransfer TextureCache::BuildTextureTransfer(const ImageInfo& info,
    uint32_t native_samples, BindingType binding, TransferDirection direction) const {
	const bool  upload           = direction == TransferDirection::Upload;
	const bool  render_target    = binding == BindingType::RenderTarget;
	const bool  video_out        = binding == BindingType::VideoOut;
	auto        format           = info.guest_format;
	uint32_t    layers           = info.TransferLayers();
	bool        volume           = info.IsVolume();
	bool        allow_depth_tile = upload;
	const char* owner            = "TextureCache readback";

	TextureTransfer transfer;
	transfer.swap_bgra16 = info.bgra16 && (!upload || render_target || video_out);
	if (render_target) {
		format = ImageOps::RenderTargetTransferFormat(info.bytes_per_block);
	}
	if (video_out) {
		allow_depth_tile = false;
	} else if (render_target || binding == BindingType::Storage) {
		allow_depth_tile = true;
	}
	if (upload) {
		if ((render_target || video_out) &&
		    (info.resources.layers == 0 || info.data.size % info.resources.layers != 0 ||
		     info.samples != 1 || native_samples != 1)) {
			EXIT("TextureCache: invalid color-attachment upload\n");
		}
		owner = "TextureCache";
		if (render_target) {
			owner = "RenderTarget";
		} else if (binding == BindingType::Storage) {
			owner = "StorageTextureCache";
		} else if (video_out) {
			if (info.metadata.compression != VideoOutCompression::Uncompressed) {
				EXIT("TextureCache: invalid color-attachment upload\n");
			}
			layers = info.resources.layers;
			volume = false;
			owner  = "VideoOut";
		}
	}

	transfer.layout  = TextureCalcUploadLayout(format, info.extent.width, info.extent.height,
	                                       info.resources.levels, layers, info.tile_mode,
	                                       info.data.size, allow_depth_tile, volume, owner);
	transfer.regions = TextureBuildImageCopies(transfer.layout);
	if (info.IsDepth()) {
		for (auto& region: transfer.regions) {
			region.imageSubresource.aspectMask = vk::ImageAspectFlagBits::eDepth;
		}
	}
	if (transfer.layout.surface.description.tile_mode != Prospero::TileMode::kLinear) {
		if (!TextureBuildGpuTileInfos(info.data.size, transfer.regions, transfer.layout,
		                              info.resources.levels, transfer.tiles)) {
			return transfer;
		}
	}
	transfer.valid = true;
	return transfer;
}

void TextureCache::ConstrainSampledSource(ImageDesc& desc) const {
	desc.source_first_level = 0;
	desc.source_size = 0;
	static const bool enabled = [] {
		const auto* value = std::getenv("KYTY_RESIDENT_MIPS");
		return value == nullptr || value[0] != '0';
	}();
	// Keep native dimensions/mip numbering unchanged. For now trim only a packed
	// prefix of a single-layer compressed texture, with an actual min-LOD view.
	const auto& info = desc.info;
	if (!enabled || !m_graphics.image_view_min_lod_enabled || desc.type != BindingType::Texture ||
	    !info.IsBlock() || info.type != Prospero::ImageType::kColor2D || info.resources.layers != 1 ||
	    info.resources.levels <= 1 || info.HasMetadata() || desc.view_info.base_level != 0 ||
	    desc.view_info.min_lod < 256 || desc.view_info.level_count == 0) return;
	const auto first = std::min(desc.view_info.min_lod >> 8u, desc.view_info.level_count - 1u);
	if (first == 0 || first >= info.resources.levels) return;
	const auto transfer = BuildTextureTransfer(info, 1, BindingType::Texture, TransferDirection::Upload);
	if (!transfer.valid || transfer.tiles.size() != transfer.regions.size()) return;
	uint64_t begin = UINT64_MAX, end = 0;
	for (size_t i = 0; i < transfer.tiles.size(); ++i) {
		if (transfer.regions[i].imageSubresource.mipLevel < first) continue;
		const auto& tile = transfer.tiles[i];
		begin = std::min(begin, tile.tiled_offset);
		end = std::max(end, tile.tiled_offset + tile.tiled_size);
	}
	if (begin != 0 || end == 0 || end > info.data.size) return;
	desc.source_first_level = first;
	desc.source_size = end;
}

void TextureCache::ConfigureImageSourceUnlocked(ImageId id, const ImageDesc& desc) {
	auto& image = m_slot_images[id];
	if (!image.info.IsBlock() || image.IsGpuModified()) return;
	const bool same = image.info.data == desc.info.data && image.info.extent == desc.info.extent &&
	                  image.info.resources == desc.info.resources;
	const auto first = same ? desc.source_first_level : 0u;
	const auto size = same && desc.source_size != 0 ? desc.source_size : image.info.data.size;
	// Several bindings in one draw may expose different LOD ranges of the same image.
	if (image.binding.is_bound && first > image.source_first_level) return;
	if (first == image.source_first_level && size == image.SourceRange().size) return;
	Common::DrawStat::Mark(Common::DrawStat::ImgUp);
	if (size != image.SourceRange().size) UntrackImage(id);
	if (first < image.source_first_level) image.MarkBufferModified();
	image.source_first_level = first;
	image.source_size = size;
	if (image.pending_levels <= first) {
		image.pending_levels = 0;
		image.pending_bytes = 0;
	}
	static const bool trace = Common::EnvFlagOn("KYTY_IMAGE_LIFETIME_TRACE");
	if (trace) LOGF("ImageSource: frame=%u guest=0x%016" PRIx64 " first=%u bytes=%" PRIu64 " logical=%" PRIu64 "\n",
	               GpuTimeProfiler::Frame(), image.info.data.address, first, size, image.info.data.size);
}

void TextureCache::ConfigureImageSource(ImageId id, const ImageDesc& desc) {
	const auto& image = m_slot_images[id];
	if (!image.info.IsBlock() || (image.source_first_level == 0 && desc.source_first_level == 0)) return;
	if (image.info.data == desc.info.data && image.info.extent == desc.info.extent &&
	    image.source_first_level == desc.source_first_level &&
	    image.SourceRange().size == (desc.source_size != 0 ? desc.source_size : image.info.data.size)) return;
	std::scoped_lock lock {m_lock};
	ConfigureImageSourceUnlocked(id, desc);
}

TextureCache::ImageDownload TextureCache::BuildDownload(const Image& image) const {
	const auto&  info    = image.info;
	const auto   binding = UploadBinding(image);
	ImageDownload transfer {.depth_target = binding == BindingType::DepthTarget};
	if (info.samples != 1 || image.backing.samples != 1) {
		return transfer;
	}
	if (transfer.depth_target) {
		transfer.valid = IsSupportedDepthPlaneReadback(info) && info.resources.layers != 0 &&
		             info.data.size % info.resources.layers == 0 &&
		             Prospero::NumBytesPerElement(info.guest_format) == info.bytes_per_block;
		return transfer;
	}
	if (info.metadata.compression != VideoOutCompression::Uncompressed) {
		return transfer;
	}
	transfer.texture = BuildTextureTransfer(image, binding, TransferDirection::Download);
	transfer.valid   = transfer.texture.valid;
	return transfer;
}

void TextureCache::DebugDumpImage(ImageId id, const std::string& name) {
	auto* image = m_slot_images.try_get(id);
	if (image == nullptr || image->backing.image == nullptr) {
		LOGF("DumpTex: %s: no backing image\n", name.c_str());
		return;
	}
	const auto& info = image->info;
	const uint64_t size = static_cast<uint64_t>(image->backing.extent.width) *
	                      image->backing.extent.height * std::max<uint32_t>(info.bytes_per_block, 1u);
	vk::BufferImageCopy region {};
	region.bufferOffset     = 0;
	region.bufferRowLength  = 0;
	region.bufferImageHeight = 0;
	region.imageSubresource = {vk::ImageAspectFlagBits::eColor, 0, 0, 1};
	region.imageExtent      = {image->backing.extent.width, image->backing.extent.height, 1};
	Buffer download(m_graphics, m_scheduler, MemoryUsage::Download, 0, AllFlags, size);
	image->Download(std::span<const vk::BufferImageCopy> {&region, 1}, download.Handle(), 0, size);
	m_scheduler.Finish();
	download.Invalidate(0, size);
	if (FILE* f = std::fopen(name.c_str(), "wb"); f != nullptr) {
		std::fwrite(download.Mapped().data(), 1, static_cast<size_t>(size), f);
		std::fclose(f);
	}
	LOGF("DumpTex: wrote %s (image 0x%012" PRIx64 " backing %ux%u vk_format=%d bpb=%u gpu_modified=%d"
	     " cpu_dirty=%d buffer_modified=%d)\n",
	     name.c_str(), info.data.address, image->backing.extent.width, image->backing.extent.height,
	     static_cast<int>(image->backing.format), info.bytes_per_block, image->IsGpuModified() ? 1 : 0,
	     image->IsCpuDirty() ? 1 : 0, image->IsBufferModified() ? 1 : 0);
}

namespace {

// Session 73, C1. One UINT format per tiler element size, and the only five that Vulkan makes
// MANDATORY for STORAGE_IMAGE, SAMPLED_IMAGE and COLOR_ATTACHMENT at once - which matters because
// Image::FindView hands a storage view the image's WHOLE usage set (imageView.cpp:367-371), and
// the image carries eSampled and eColorAttachment as well (image.cpp:60-75). Never eR64Uint /
// eR64G64Uint: they sit in the same compatibility classes (imageView.cpp:236, :247) and have
// neither feature, so the view creation would EXIT. The FormatsCompatible call is the second
// guard, not the first: the first is backing.usage & eStorage, which is what the driver accepted.
[[nodiscard]] vk::Format FuseViewFormat(vk::Format base, uint32_t bytes_per_element) noexcept {
	const auto view = bytes_per_element == 1    ? vk::Format::eR8Uint
	                  : bytes_per_element == 2  ? vk::Format::eR16Uint
	                  : bytes_per_element == 4  ? vk::Format::eR32Uint
	                  : bytes_per_element == 8  ? vk::Format::eR32G32Uint
	                  : bytes_per_element == 16 ? vk::Format::eR32G32B32A32Uint
	                                            : vk::Format::eUndefined;
	return view != vk::Format::eUndefined && ImageViewOps::FormatsCompatible(base, view)
	           ? view
	           : vk::Format::eUndefined;
}

// Every clause is an assumption the fused shader makes about where its texels land. The mip level
// becomes the view's base_level and the array layer becomes the dispatch's z, so a region that is
// not exactly one whole colour (level, layer) starting at the origin cannot be fused.
[[nodiscard]] bool FusableRegions(const std::vector<vk::BufferImageCopy>& regions,
                                  const VulkanImage&                     backing) noexcept {
	for (const auto& region: regions) {
		if (region.imageSubresource.aspectMask != vk::ImageAspectFlagBits::eColor ||
		    region.imageSubresource.layerCount != 1 ||
		    region.imageSubresource.mipLevel >= backing.mip_levels ||
		    region.imageSubresource.baseArrayLayer >= backing.layers ||
		    region.imageOffset.x != 0 || region.imageOffset.y != 0 ||
		    region.imageOffset.z != 0 || region.imageExtent.depth != 1 ||
		    // Non-zero only on the linear path, which never builds tiles; if that ever changed,
		    // tile_info.height would exceed imageExtent.height and the dispatch would write rows
		    // past the bottom of the level (textureCommon.cpp:354-359 against :259).
		    region.bufferImageHeight != 0) {
			return false;
		}
	}
	return true;
}

} // namespace

uint64_t TextureCache::UploadImage(Image& image, vk::Buffer source, uint64_t source_offset,
                                   uint64_t source_size, bool source_is_host,
                                   uint32_t first_level, uint32_t level_count) {
	Common::FrameStats::Scope upload_scope(Common::FrameStats::Counter::ImgUploadNs,
	                                       Common::FrameStats::Counter::ImgUploads);
	Common::DrawStat::Mark(Common::DrawStat::ImgUp);
	Common::DrawStat::Cut(Common::DrawStat::EdgeUpload);
	// Session 124, knob "skipceil" = 3 (closure census, [RC1]): the upload is a lazy write of site "upload"; the stamps
	// of the rest of this call are part of it.
	const SkcCensus::LazyScope skc3_lazy(SkcCensus::LazyUpload);
	// Session 123, knob "skipceil" = 2 (census, [N5]): the image receives guest memory - its label follows that memory.
	if (Common::SkipCeil::t_w3) [[unlikely]] {
		SkcCensus::Upload(m_buffer_cache, image, first_level, level_count);
	}
	Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 48(b), M2 (N1)
	const auto& info    = image.info;
	const auto  binding = UploadBinding(image);
	const bool  partial = first_level != 0 || level_count < info.resources.levels;
	uint64_t    bytes   = info.data.size;
	// Session 72, C1 (measurement only, no decision changes). Can the detile write this image
	// directly instead of a scratch buffer that copyBufferToImage then moves? Two independent
	// conditions, and the four cells below measure their joint distribution. `storage_ok` is the
	// usage the driver ACCEPTED at create time (image.cpp:53-77 grants eStorage exactly to
	// non-block, non-depth, samples == 1 images; :747-757 validates it), so it needs no format
	// list of ours. `detiled` is set in the two branches that call TileManager::Detile.
	const bool storage_ok =
	    static_cast<bool>(image.backing.usage & vk::ImageUsageFlagBits::eStorage);
	bool        detiled = false;
	bool        fused   = false; // session 73, gate "imgfuse"
	// Session 73: the four C1 cells moved out of the `upload` lambda so that the FUSED path, which
	// never calls Image::Upload, counts them too. Without this the session-72 identities
	// sum(c1_*) == img_up and sum(c1_*_kb) == img_up_kb break the moment the gate is armed and
	// check_s71_counters.py FAILs - and by the harness rule no number from that group could then
	// be quoted. `copy_bytes` is what copyBufferToImage moves, or would have moved.
	const auto classify = [&](uint64_t copy_bytes) {
		if (!Common::FrameStats::Enabled()) {
			return;
		}
		using C = Common::FrameStats::Counter;
		const auto cell = (storage_ok && detiled) ? C::C1StorageDetile
		                  : storage_ok            ? C::C1StorageDirect
		                  : detiled               ? C::C1NoStorageDetile
		                                          : C::C1NoStorageDirect;
		const auto step = static_cast<uint32_t>(C::C1StorageDetileKb) -
		                  static_cast<uint32_t>(C::C1StorageDetile);
		const auto index = static_cast<uint32_t>(cell);
		Common::FrameStats::Add(cell, 1);
		// KiB at the increment site, never bytes - the printed micros flag divides by 1000
		// and would be wrong for bytes (session 69's img_skip_kb defect).
		Common::FrameStats::Add(static_cast<C>(index + step), bytes >> 10u);
		Common::FrameStats::Add(static_cast<C>(index + 2 * step), copy_bytes >> 10u);
	};
	const auto  upload  = [&](std::vector<vk::BufferImageCopy>& copies, TileManager::Result linear) {
		for (auto& copy: copies) {
			copy.bufferOffset += linear.offset;
		}
		const bool fusable = storage_ok && detiled;
		image.Upload(copies, linear.buffer, linear.offset, linear.size,
		             linear.buffer != source || source_is_host, fusable);
		classify(linear.size);
		m_scheduler.GpuMark(GpuTimeProfiler::Kind::ImageUpload, 3, info.data.size >> 20u);
	};

	if (binding != BindingType::DepthTarget) {
		auto transfer = BuildTextureTransfer(image, binding, TransferDirection::Upload);
		if (!transfer.valid) {
			EXIT("TextureCache: invalid texture upload: binding=%u addr=0x%016" PRIx64
			     " size=0x%016" PRIx64 " format=%u tile=%u family=%u extent=%ux%ux%u "
			     "pitch=%u levels=%u layers=%u samples=%u\n",
			     static_cast<uint32_t>(binding), info.data.address, info.data.size,
			     static_cast<uint32_t>(info.guest_format), static_cast<uint32_t>(info.tile_mode),
			     static_cast<uint32_t>(transfer.layout.surface.texture.block.family), info.extent.width,
			     info.extent.height, info.extent.depth, info.pitch, info.resources.levels,
			     info.resources.layers, info.samples);
		}
		TileManager::Result linear {source, source_offset, info.data.size};
		uint64_t            linear_size = transfer.LinearSize();
		if (partial) {
			// Keep the regions of the requested levels and their tiles (one per region for a
			// non-volume texture); the linear scratch is rebased to the first kept region.
			EXIT_IF(transfer.tiles.size() != transfer.regions.size() || first_level >= info.resources.levels);
			std::vector<vk::BufferImageCopy> regions;
			std::vector<GpuTileInfo>         tiles;
			uint64_t                         base = UINT64_MAX;
			bytes                                 = 0;
			for (size_t i = 0; i < transfer.regions.size(); i++) {
				const auto level = transfer.regions[i].imageSubresource.mipLevel;
				if (level < first_level || level - first_level >= level_count) {
					continue;
				}
				regions.push_back(transfer.regions[i]);
				tiles.push_back(transfer.tiles[i]);
				base = std::min(base, transfer.tiles[i].linear_offset);
			}
			// Guest bytes of the kept levels (tail mips share a tile block; their tiled_size
			// would overcount).
			for (uint32_t level = first_level;
			     level < std::min<uint32_t>(first_level + level_count, info.resources.levels); level++) {
				bytes += info.mip_layout[level].size;
			}
			bytes = std::min(bytes, info.data.size);
			EXIT_IF(regions.empty());
			linear_size = 0;
			for (size_t i = 0; i < tiles.size(); i++) {
				EXIT_IF(regions[i].bufferOffset != tiles[i].linear_offset);
				tiles[i].linear_offset -= base;
				regions[i].bufferOffset -= base;
				linear_size = std::max(linear_size, tiles[i].linear_offset + tiles[i].linear_size);
			}
			transfer.regions = std::move(regions);
			transfer.tiles   = std::move(tiles);
		}
		// Session 73, C1 (gate "imgfuse"): can this upload's detile write the image itself?
		// The classification runs with the gate OFF as well, so an ordinary base run says what
		// share of session 72's 1241.7 us ceiling the first cut reaches before anything is armed.
		// Each clause is a defect the adversarial read of this session found - see
		// C:/kyty/s73/patch_imgfuse.py for the list and what each one would have broken.
		const auto& tex_layout  = transfer.layout.surface.texture;
		const auto  fuse_format = FuseViewFormat(image.backing.format, info.bytes_per_block);
		const bool  fuse_cell   = storage_ok && !transfer.tiles.empty();
		const bool  fuse_shape =
		    fuse_cell && !transfer.swap_bgra16 && !info.IsVolume() && !info.IsDepth() &&
		    !info.IsBlock() && info.samples == 1 && image.backing.samples == 1 &&
		    image.backing.image_type == vk::ImageType::e2D && tex_layout.texel_width == 1 &&
		    tex_layout.texel_height == 1 &&
		    tex_layout.block.bytes_per_element == info.bytes_per_block &&
		    transfer.tiles.size() == transfer.regions.size() &&
		    FusableRegions(transfer.regions, image.backing);
		const bool fuse_ok = fuse_shape && fuse_format != vk::Format::eUndefined;
		if (fuse_cell && Common::FrameStats::Enabled()) {
			using C = Common::FrameStats::Counter;
			Common::FrameStats::Add(fuse_ok                ? C::C1FuseReady
			                        : transfer.swap_bgra16 ? C::C1FuseSwap
			                        : !fuse_shape          ? C::C1FuseShape
			                                               : C::C1FuseFormat,
			                        1);
			if (fuse_ok) {
				Common::FrameStats::Add(C::C1FuseReadyKb, bytes >> 10u);
				Common::FrameStats::Add(C::C1FuseReadyCopyKb, linear_size >> 10u);
			}
		}
		if (!transfer.tiles.empty()) {
			if (fuse_ok && Common::Gates::Enabled(Common::Gates::Gate::ImageDetileFuse)) {
				m_tiler.DetileToImage(image, fuse_format, source, source_offset, source_size,
				                      linear_size, transfer.tiles, transfer.regions,
				                      source_is_host);
				fused = true;
			} else {
				linear = m_tiler.Detile(source, source_offset, source_size, linear_size,
				                        transfer.tiles, source_is_host);
			}
			detiled = true; // session 72, C1 classification
			Common::FrameStats::Add(Common::FrameStats::Counter::ImgDetileDispatches,
			                        transfer.tiles.size());
			m_scheduler.GpuMark(GpuTimeProfiler::Kind::ImageUpload, 1, info.data.size >> 20u);
		}
		if (fused) {
			// No scratch, no copy: the dispatch already wrote the image. Everything else on this
			// path is counted exactly as the scratch path counts it, so the arms stay comparable.
			classify(linear_size);
			Common::FrameStats::Add(Common::FrameStats::Counter::C1Fused, 1);
			Common::FrameStats::Add(Common::FrameStats::Counter::C1FusedKb, bytes >> 10u);
		} else {
			if (transfer.swap_bgra16) {
				linear = m_tiler.SwapBgra16(linear);
				m_scheduler.GpuMark(GpuTimeProfiler::Kind::ImageUpload, 2, info.data.size >> 20u);
			}
			upload(transfer.regions, linear);
		}
		Common::FrameStats::Add(Common::FrameStats::Counter::ImgCopyRegions, transfer.regions.size());
		Common::FrameStats::Add(Common::FrameStats::Counter::ImgUploadBytes, bytes);
		return bytes;
	}

	EXIT_IF(partial);
	if (info.samples != 1 || image.backing.samples != 1 ||
	    info.resources.layers == 0 || info.data.size % info.resources.layers != 0 ||
	    Prospero::NumBytesPerElement(info.guest_format) != info.bytes_per_block) {
		EXIT("TextureCache: invalid depth upload\n");
	}
	const auto          layers          = info.resources.layers;
	const auto          full_slice_size = info.data.size / layers;
	auto                copies          = BuildDepthCopies(info, full_slice_size);
	TileManager::Result linear {source, source_offset, source_size};
	if (info.IsTiled()) {
		const auto tiles = BuildDepthTiles(info);
		linear = m_tiler.Detile(source, source_offset, info.data.size, info.data.size, tiles,
		                        source_is_host);
		detiled = true; // session 72, C1 classification
	}
	const auto transfer_bytes = DepthAspectTransferBytes(info.pixel_format);
	if (transfer_bytes != info.bytes_per_block) {
		const uint64_t texels_per_slice = static_cast<uint64_t>(info.pitch) * info.extent.height;
		EXIT_NOT_IMPLEMENTED(info.bytes_per_block != sizeof(uint16_t) ||
		                     transfer_bytes != sizeof(uint32_t) || texels_per_slice > UINT32_MAX ||
		                     texels_per_slice > UINT64_MAX / transfer_bytes);
		const uint64_t transfer_slice = texels_per_slice * transfer_bytes;
		EXIT_NOT_IMPLEMENTED(transfer_slice > UINT64_MAX / layers);
		auto promoted = m_tiler.GetScratchBuffer(transfer_slice * layers);
		m_tiler.ConvertD16(
		    linear, promoted, TileManager::D16Direction::Promote,
		    info.pixel_format == vk::Format::eD32SfloatS8Uint,
		    {.width               = info.extent.width,
		     .height              = info.extent.height,
		     .layers              = layers,
		     .source_row_stride   = static_cast<uint64_t>(info.pitch) * sizeof(uint16_t),
		     .target_row_stride   = static_cast<uint64_t>(info.pitch) * sizeof(uint32_t),
		     .source_slice_stride = full_slice_size,
		     .target_slice_stride = transfer_slice});
		linear = promoted;
		for (uint32_t layer = 0; layer < layers; layer++) {
			copies[layer].bufferOffset = transfer_slice * layer;
		}
	}
	upload(copies, linear);
	Common::FrameStats::Add(Common::FrameStats::Counter::ImgUploadBytes, bytes);
	return bytes;
}

void TextureCache::NoteUploadFrame() {
	const auto frame = GpuTimeProfiler::Frame();
	if (frame != m_upload_frame) {
		Common::DrawStat::Mark(Common::DrawStat::Memo);
		m_upload_frame        = frame;
		m_frame_upload_bytes  = 0;
		m_frame_pending_bytes = 0;
	}
}

uint32_t TextureCache::DeferrableLevels(const Image& image, bool source_imported) const {
	const auto& config = MipDefer();
	const auto& info   = image.info;
	if (!config.enabled || !m_graphics.image_view_min_lod_enabled || !source_imported ||
	    m_frame_upload_bytes < config.frame_bytes || UploadBinding(image) != BindingType::Texture ||
	    info.IsDepth() || info.IsVolume() || info.samples != 1 || info.HasMetadata() ||
	    info.bgra16 || info.tile_mode == Prospero::TileMode::kLinear ||
	    info.resources.levels <= config.levels || info.resources.levels > info.mip_layout.size()) {
		return 0;
	}
	uint64_t bytes = 0;
	for (uint32_t level = 0; level < config.levels; level++) {
		bytes += info.mip_layout[level].size;
	}
	return bytes >= config.min_bytes ? config.levels : 0;
}

void TextureCache::CompletePendingUpload(Image& image) {
	if (image.pending_levels == 0) {
		return;
	}
	Common::FrameStats::Scope init_scope(Common::FrameStats::Counter::ImgInitNs);
	const auto source =
	    m_buffer_cache.ObtainBufferForImage(image.SourceRange().address, image.SourceRange().size, true);
	if (source.buffer == nullptr) {
		EXIT("TextureCache: failed to obtain the source of a pending mip upload\n");
	}
	const auto levels    = image.pending_levels;
	image.pending_levels = 0;
	NoteUploadFrame();
	const auto uploaded = UploadImage(image, source.buffer, source.offset, source.size,
	                                  source.host_written, image.source_first_level, levels - image.source_first_level);
	m_frame_upload_bytes += uploaded;
	m_frame_pending_bytes += uploaded;
	image.pending_bytes = 0;
	// Session 71, C1: key 0 = "the whole upload", so that keys 1..6 stay a clean phase
	// namespace. The two-argument overload used to put the size in MiB in the KEY slot, where it
	// collided with the phase keys for every image of 1-6 MiB. GpuTime only; nothing else reads
	// these marks.
	m_scheduler.GpuMark(GpuTimeProfiler::Kind::ImageUpload, 0, image.info.data.size >> 20u);
	Common::FrameStats::Add(Common::FrameStats::Counter::ImgPendingUploads, 1);
	Common::FrameStats::Add(Common::FrameStats::Counter::ImgPendingBytes, uploaded);
	MipDeferTrace("complete", image, uploaded);
}

// Session 71, candidate C3 (counters only, no gate, no decision changed). The upload C3 wants
// to suppress is decided in InitializeImage, far below the binding that caused it, and only
// the BINDING knows whether this is a write target, a sampled read, or the clear path bringing
// in the texels a partial clear will not write. Predicting the upload at the binding would
// diverge whenever RefreshImage resolves a maybe-CPU-dirty hash and flips m_cpu_dirty, which
// removes the image from the population - so the binding publishes a site on a thread-local
// RAII scope and the counting happens below, next to the gate predicate. The attribution is
// then exact by construction, and the prediction error is itself measurable
// (c3_ct_pop - c3_ct_canc - c3_ct_up).
//
// Each scope covers RefreshImage - or, inside ClearImage, InitializeImage - ALONE, never
// PrepareDccClear / PrepareCmaskClear. Those reach ClearImage, whose partial-clear path
// uploads the image itself, and attributing that upload to the binding it happened under
// would feed C3's decision rule with an upload the clear CAUSED.
namespace {

enum class UploadSite : uint8_t { Other, ColorTarget, DepthTarget, StorageImage, Sampled, ClearOp };

struct UploadSiteState {
	UploadSite site       = UploadSite::Other;
	bool       reg_clear  = false; // the guest fast-clear registers of the binding said "clear"
	bool       fill_clear = false; // an unconsumed metadata fill was pending for the bound layers
};

thread_local UploadSiteState t_upload_site {};
// Population uploads performed from inside ClearImage (a partial clear uploads first).
// FindRenderTarget snapshots it across PrepareDccClear / PrepareCmaskClear so that "the clear
// cancelled this upload" never counts a case where the clear CAUSED one instead.
thread_local uint32_t t_clear_caused_uploads = 0;

class UploadSiteScope final {
public:
	UploadSiteScope(UploadSite site, bool reg_clear, bool fill_clear): m_previous(t_upload_site) {
		t_upload_site = UploadSiteState {site, reg_clear, fill_clear};
	}
	~UploadSiteScope() { t_upload_site = m_previous; }
	UploadSiteScope(const UploadSiteScope&)            = delete;
	UploadSiteScope& operator=(const UploadSiteScope&) = delete;

private:
	UploadSiteState m_previous;
};

} // namespace

bool TextureCache::MetaFillPendingLocked(const ImageDesc& desc) const {
	if (desc.info.metadata.kind == ImageMetadataKind::None ||
	    desc.info.metadata.range.address == 0) {
		return false;
	}
	const auto found = m_surface_metas.find(desc.info.metadata.range.address);
	if (found == m_surface_metas.end() || found->second.clear_mask == 0) {
		return false;
	}
	const auto& view = desc.view_info;
	if (view.base_layer >= 32) {
		return false;
	}
	const auto count = std::min(view.layer_count, 32u - view.base_layer);
	const auto mask =
	    count >= 32u ? UINT32_MAX : (((uint32_t {1} << count) - 1u) << view.base_layer);
	return (found->second.clear_mask & mask) != 0;
}

void TextureCache::InitializeImage(ImageId id, bool allow_defer) {
	auto& image = m_slot_images[id];
	if (image.info.data.Empty()) {
		return;
	}
	Common::FrameStats::Scope init_scope(Common::FrameStats::Counter::ImgInitNs);
	TrackImage(id);
	if (image.info.metadata.compression != VideoOutCompression::Uncompressed) {
		if (image.IsCpuDirty()) {
			image.RefreshComplete();
		}
		return;
	}
	if (image.info.samples > 1) {
		return;
	}
	const bool upload = image.IsBufferModified() || image.IsCpuDirty();
	// Session 69, gate "imgskip" (default 0) - MEASUREMENT ONLY, the picture is allowed to break.
	// The ceiling of the guest<->GPU image ping-pong: 95.0 % of the bytes of Sky Garden's ~100 MB
	// of image uploads per frame exist only because a GPU buffer wrote over the guest range
	// (ImgUploadWhy buffer=1 cpu=0; descriptors.cpp:277 -> InvalidateMemoryFromGPU, :2473-2476, which
	// also drops m_gpu_modified). The data never left the GPU, so the whole
	// ObtainBufferForImage + detile + copyBufferToImage round trip is dropped and the image keeps
	// the texels it already holds. The buffer-modified flag must still be cleared: ClearImage,
	// CopyImageMip and ResolveDepthOverlap all EXIT on an image that stayed guest-owned.
	// Session 71, candidate C3: the imgskip predicate WITHOUT the gate, so the counters below
	// size C3 on an ordinary defaults run and still sum to img_skip / img_skip_kb when the gate
	// is on. skip_gpu_stale below is the same boolean it always was - `population && Enabled()`
	// differs from the old chain only in short-circuit order, and every operand is a pure read.
	// One expression, so the counted population and the gated population cannot drift apart.
	const bool population =
	    upload && image.IsBufferModified() && !image.IsCpuDirty() &&
	    image.SourceRange().size >=
	        static_cast<uint64_t>(Common::Gates::Value(Common::Gates::Knob::ImageSkipKb)) * 1024u;
	if (population) {
		namespace FS       = Common::FrameStats;
		// KiB at the increment site, printed with micros = false (the s69 img_skip_kb defect).
		const auto note_kb = image.SourceRange().size / 1024u;
		FS::Add(FS::Counter::C3Population, 1);
		FS::Add(FS::Counter::C3PopulationKb, note_kb);
		switch (t_upload_site.site) {
			case UploadSite::ColorTarget:
				FS::Add(FS::Counter::C3ColorUploads, 1);
				FS::Add(FS::Counter::C3ColorUploadsKb, note_kb);
				if (t_upload_site.reg_clear) {
					FS::Add(FS::Counter::C3ColorUploadsReg, 1);
					FS::Add(FS::Counter::C3ColorUploadsRegKb, note_kb);
				}
				if (t_upload_site.fill_clear) {
					FS::Add(FS::Counter::C3ColorUploadsFill, 1);
					FS::Add(FS::Counter::C3ColorUploadsFillKb, note_kb);
				}
				break;
			case UploadSite::DepthTarget:
				FS::Add(FS::Counter::C3DepthUploads, 1);
				FS::Add(FS::Counter::C3DepthUploadsKb, note_kb);
				if (t_upload_site.reg_clear) {
					FS::Add(FS::Counter::C3DepthUploadsReg, 1);
					FS::Add(FS::Counter::C3DepthUploadsRegKb, note_kb);
				}
				break;
			case UploadSite::StorageImage:
				FS::Add(FS::Counter::C3StorageUploads, 1);
				FS::Add(FS::Counter::C3StorageUploadsKb, note_kb);
				break;
			case UploadSite::Sampled:
				// The pass READS this surface, so C3 must never touch these.
				FS::Add(FS::Counter::C3SampledUploads, 1);
				FS::Add(FS::Counter::C3SampledUploadsKb, note_kb);
				break;
			case UploadSite::ClearOp:
				// An upload the clear CAUSED, not one it cancelled: ClearImage brings the guest
				// contents in before clearing a partial range. Never part of C3's ceiling.
				t_clear_caused_uploads++;
				FS::Add(FS::Counter::C3ClearUploads, 1);
				FS::Add(FS::Counter::C3ClearUploadsKb, note_kb);
				break;
			case UploadSite::Other:
				FS::Add(FS::Counter::C3OtherUploads, 1);
				FS::Add(FS::Counter::C3OtherUploadsKb, note_kb);
				break;
		}
	}
	const bool skip_gpu_stale =
	    population && Common::Gates::Enabled(Common::Gates::Gate::ImageSkipGpuStale);
	if (skip_gpu_stale) {
		// NoteUploadFrame like every other upload path: it is the only place that rolls
		// m_frame_upload_bytes over at a frame boundary, and DeferrableLevels judges the mip-defer
		// budget against it. Without this, a frame in which the gate skipped everything would size
		// that budget from the previous frame's total.
		NoteUploadFrame();
		Common::FrameStats::Add(Common::FrameStats::Counter::ImgSkipped, 1);
		Common::FrameStats::Add(Common::FrameStats::Counter::ImgSkippedKb,
		                        image.SourceRange().size / 1024u);
		image.ClearBufferModified();
	} else if (upload) {
		TraceWatchedImage("upload", image);
		const bool buffer_modified = image.IsBufferModified();
		const bool cpu_definite    = image.IsDefinitelyCpuDirty();
		const bool cpu_maybe       = image.IsMaybeCpuDirty();
		const auto source =
		    m_buffer_cache.ObtainBufferForImage(image.SourceRange().address, image.SourceRange().size);
		if (source.buffer == nullptr) {
			EXIT("TextureCache: failed to obtain image upload source\n");
		}
		static const bool upload_trace = Common::EnvFlagOn("KYTY_IMAGE_UPLOAD_TRACE");
		if (upload_trace) {
			static const uint32_t first_frame = [] {
				const auto* value = std::getenv("KYTY_IMAGE_UPLOAD_FROM");
				return value == nullptr ? 0u : static_cast<uint32_t>(std::strtoul(value, nullptr, 10));
			}();
			const auto frame = GpuTimeProfiler::Frame();
			if (frame >= first_frame) {
				LOGF("ImgUploadWhy: frame=%u id=%u guest=0x%016" PRIx64 " bytes=%" PRIu64
				     " w=%u h=%u mips=%u layers=%u fmt=%u tile=%u buffer=%d cpu=%d maybe=%d"
				     " imported=%d host_written=%d last_frame=%u gpu=%d\n",
				     frame, id.index, image.info.data.address, image.SourceRange().size,
				     image.info.extent.width, image.info.extent.height, image.info.resources.levels,
				     image.info.resources.layers, static_cast<uint32_t>(image.info.pixel_format),
				     static_cast<uint32_t>(image.info.tile_mode), buffer_modified ? 1 : 0,
				     cpu_definite ? 1 : 0, cpu_maybe ? 1 : 0, source.imported ? 1 : 0,
				     source.host_written ? 1 : 0, image.frame_accessed_last,
				     image.IsGpuModified() ? 1 : 0);
			}
		}
		NoteUploadFrame();
		const auto deferred = allow_defer ? DeferrableLevels(image, source.imported) : 0u;
		const auto first_level = std::max(deferred, image.source_first_level);
		const auto uploaded =
		    UploadImage(image, source.buffer, source.offset, source.size, source.host_written,
		                first_level, image.info.resources.levels - first_level);
		m_frame_upload_bytes += uploaded;
		image.pending_levels = deferred > image.source_first_level ? deferred : 0;
		image.pending_bytes  = image.pending_levels != 0 ? image.SourceRange().size - std::min(image.SourceRange().size, uploaded) : 0;
		if (image.pending_levels != 0) {
			Common::FrameStats::Add(Common::FrameStats::Counter::ImgDeferred, 1);
			Common::FrameStats::Add(Common::FrameStats::Counter::ImgDeferredBytes,
			                        image.pending_bytes);
			MipDeferTrace("defer", image, image.pending_bytes);
		}
		// Session 71, C1: key 0, see CompletePendingUpload above.
		m_scheduler.GpuMark(GpuTimeProfiler::Kind::ImageUpload, 0, image.info.data.size >> 20u);
		image.ClearBufferModified();
	}
	if (image.IsCpuDirty()) {
		image.RefreshComplete();
	}
}

void TextureCache::PrepareDccClear(ImageId id, const ImageDesc& desc) {
	if (desc.info.metadata.kind != ImageMetadataKind::Dcc) {
		return;
	}
	auto& image            = m_slot_images[id];
	// Session 124, knob "skipceil" = 3 (closure census, ROADMAP s122 item 47(v)): the image links to this surface now.
	const bool skc3_link   = Common::SkipCeil::t_mode == 3 &&
	                       (image.info.metadata.kind != desc.info.metadata.kind ||
	                        image.info.metadata.range.address != desc.info.metadata.range.address);
	Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 47(z), N1
	image.info.metadata    = desc.info.metadata;
	auto [entry, inserted] = m_surface_metas.try_emplace(
	    desc.info.metadata.range.address, MetaDataInfo {.type = MetaDataInfo::Type::Dcc});
	auto& metadata = entry->second;
	if (inserted) {
		Common::DrawStat::Mark(Common::DrawStat::Meta);
		BumpMetaEpoch();
	}
	// Session 124 (ROADMAP s122 item 48(a), R1): an image already linked to this address also links anew when the
	// entry leaves PendingDcc - the pending fill never closed it (G3MetaFill returns before CloseCandidates).
	const bool skc3_pend = Common::SkipCeil::t_mode == 3 && !inserted &&
	                       metadata.type == MetaDataInfo::Type::PendingDcc;
	if (!inserted && metadata.type == MetaDataInfo::Type::PendingDcc) {
		Common::DrawStat::Mark(Common::DrawStat::Meta);
		BumpMetaEpoch();
		if (PendingDccFillStale(desc.info.metadata.range.address, metadata,
		                        image.info.data.address)) {
			metadata = MetaDataInfo {.type = MetaDataInfo::Type::Dcc};
		}
		metadata.type = MetaDataInfo::Type::Dcc;
	} else if (metadata.type != MetaDataInfo::Type::Dcc) {
		Common::DrawStat::Mark(Common::DrawStat::Meta);
		BumpMetaEpoch();
		// PS5 allocations reuse metadata storage across surface types; the new image defines it.
		static std::atomic<uint32_t> log_count {0};
		if (log_count.fetch_add(1, std::memory_order_relaxed) < 32) {
			LOGF("TextureCache: image 0x%016" PRIx64 " reuses non-DCC metadata 0x%016" PRIx64
			     " (type %u)\n",
			     image.info.data.address, desc.info.metadata.range.address,
			     static_cast<uint32_t>(metadata.type));
		}
		metadata = MetaDataInfo {.type = MetaDataInfo::Type::Dcc};
	}
	// Session 124 (item 47(v)): a late link to a surface with a pending clear - the remembered cleaner closes the image,
	// before the materialization below.
	if ((skc3_link || skc3_pend) && metadata.clear_mask != 0) [[unlikely]] {
		SkcCensus::G3MetaLate(image, desc.info.metadata.range.address, metadata.clear_mask, false);
	}
	if (metadata.clear_mask == 0 || image.info.resources.levels != 1 ||
	    desc.info.metadata.range.size == 0 || metadata.fill_size < desc.info.metadata.range.size) {
		return;
	}
	const auto& view = desc.view_info;
	vk::ClearValue clear {};
	// Upstream ea092a9: a DCC key encodes in the format the binding views the surface through,
	// not in the backing format of the image; ClearImage encodes through that same view below.
	if (!DecodeDccClearFill(desc, metadata.fill_value, clear.color)) {
		return;
	}
	const bool volume_texture = image.info.IsVolume() && view.type == vk::ImageViewType::e3D;
	// TODO(merge): upstream 01df42a indexes the metadata slices with the base layer the
	// descriptor had before FindImage remapped it onto a merged image, while this path runs
	// after the remap and indexes clear_mask with the image layer. TrackDccFill marks every
	// layer of an allocation, so the two agree today; a per-slice fill would need the
	// pre-remap layer threaded down to here.
	const auto first = volume_texture ? 0u : view.base_layer;
	const auto count = volume_texture ? std::max(image.info.extent.depth >> view.base_level, 1u)
	                                  : view.layer_count;
	if (first >= 32 || count > 32 - first) {
		return;
	}
	// The metadata fill covers the complete allocation. Consume each layer only after its
	// native image contents exist; already materialized layers may have been rendered since.
	for (uint32_t layer = first; layer < first + count;) {
		if ((metadata.clear_mask & (1u << layer)) == 0) {
			layer++;
			continue;
		}
		const auto start = layer;
		uint32_t   mask  = 0;
		do {
			mask |= 1u << layer++;
		} while (layer < first + count && (metadata.clear_mask & (1u << layer)) != 0);
		ClearImage(m_scheduler.Current(), id, view.format,
		           {vk::ImageAspectFlagBits::eColor, view.base_level, view.level_count, start,
		            layer - start},
		           clear);
		metadata.clear_mask &= ~mask;
		BumpMetaEpoch();
	}
}

void TextureCache::PrepareCmaskClear(ImageId id, const ImageDesc& desc) {
	static const bool enabled = [] {
		const auto* value = std::getenv("KYTY_CMASK_CLEAR");
		return value == nullptr || value[0] != '0';
	}();
	if (!enabled || desc.info.metadata.kind != ImageMetadataKind::Cmask ||
	    desc.type != BindingType::RenderTarget || desc.info.samples != 1 ||
	    desc.info.resources.levels != 1 || desc.info.IsVolume()) return;
	auto& image = m_slot_images[id];
	// Session 124, knob "skipceil" = 3 (closure census, ROADMAP s122 item 47(v)): the image links to this surface now.
	const bool skc3_link = Common::SkipCeil::t_mode == 3 &&
	                       (image.info.metadata.kind != desc.info.metadata.kind ||
	                        image.info.metadata.range.address != desc.info.metadata.range.address);
	Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 47(z), N1
	image.info.metadata = desc.info.metadata;
	auto [entry, inserted] = m_surface_metas.try_emplace(
	    desc.info.metadata.range.address, MetaDataInfo {.type = MetaDataInfo::Type::CMask});
	auto& metadata = entry->second;
	if (inserted) {
		Common::DrawStat::Mark(Common::DrawStat::Meta);
		BumpMetaEpoch();
	}
	// Session 124 (ROADMAP s122 item 48(a), R1): as in PrepareDccClear - leaving PendingDcc is a link too.
	const bool skc3_pend = Common::SkipCeil::t_mode == 3 && !inserted &&
	                       metadata.type == MetaDataInfo::Type::PendingDcc;
	if (!inserted && metadata.type == MetaDataInfo::Type::PendingDcc) {
		Common::DrawStat::Mark(Common::DrawStat::Meta);
		BumpMetaEpoch();
		if (PendingDccFillStale(desc.info.metadata.range.address, metadata, image.info.data.address)) {
			metadata = MetaDataInfo {};
		}
		metadata.type = MetaDataInfo::Type::CMask;
		if (metadata.fill_value != 0) metadata.clear_mask = 0;
	} else if (metadata.type != MetaDataInfo::Type::CMask) {
		Common::DrawStat::Mark(Common::DrawStat::Meta);
		BumpMetaEpoch();
		metadata = MetaDataInfo {.type = MetaDataInfo::Type::CMask};
	}
	// Session 124 (item 47(v)): a late link to a surface with a pending clear - before the materialization below.
	if ((skc3_link || skc3_pend) && metadata.clear_mask != 0) [[unlikely]] {
		SkcCensus::G3MetaLate(image, desc.info.metadata.range.address, metadata.clear_mask, false);
	}
	if (metadata.fill_value != 0 || metadata.clear_mask == 0 ||
	    desc.info.metadata.range.size == 0 || metadata.fill_size < desc.info.metadata.range.size) return;
	vk::ClearValue clear {};
	if (!DecodePackedColorClear(image.backing.format, desc.info.metadata.cmask_clear_words[0],
	                           desc.info.metadata.cmask_clear_words[1], clear.color)) return;
	const auto& view = desc.view_info;
	if (view.base_level != 0 || view.base_layer >= 32 || view.layer_count > 32 - view.base_layer) return;
	for (uint32_t layer = view.base_layer; layer < view.base_layer + view.layer_count; ++layer) {
		if ((metadata.clear_mask & (1u << layer)) == 0) continue;
		ClearImage(m_scheduler.Current(), id, image.backing.format,
		           {vk::ImageAspectFlagBits::eColor, 0, 1, layer, 1}, clear);
		metadata.clear_mask &= ~(1u << layer);
		BumpMetaEpoch();
		static const bool trace = Common::EnvFlagOn("KYTY_CLEAR_TRACE");
		if (trace) LOGF("CmaskClear: frame=%u image=0x%016" PRIx64 " meta=0x%016" PRIx64
		               " layer=%u words=%08x/%08x\n", GpuTimeProfiler::Frame(), image.info.data.address,
		               desc.info.metadata.range.address, layer, desc.info.metadata.cmask_clear_words[0],
		               desc.info.metadata.cmask_clear_words[1]);
	}
}

void TextureCache::RefreshImage(ImageId id, bool allow_partial) {
	TrackImage(id);
	auto& image = m_slot_images[id];
	if (image.IsMaybeCpuDirty()) {
		Common::DrawStat::Mark(Common::DrawStat::ImgUp);
		const auto hash = image.HashGuestEdges();
		if (image.NeedsMaybeCpuHash()) {
			image.SetMaybeCpuHash(hash);
			if (!allow_partial) {
				CompletePendingUpload(image);
			}
			return;
		}
		(void)image.ResolveMaybeCpuHash(hash);
	}
	bool cpu_dirty = image.IsBufferModified() || image.IsDefinitelyCpuDirty();
	if (image.info.metadata.compression != VideoOutCompression::Uncompressed) {
		if (cpu_dirty) {
			EXIT("TextureCache: compressed guest image refresh is unsupported\n");
		}
		return;
	}
	if (cpu_dirty) {
		InitializeImage(id, allow_partial);
	}
	if (!allow_partial) {
		CompletePendingUpload(image);
	}
}

void TextureCache::AssociateStencil(ImageId depth_id, GuestRange stencil) {
	if (!stencil.Valid()) {
		EXIT("TextureCache: invalid stencil association range\n");
	}
	auto& depth = m_slot_images[depth_id];
	if (!depth.info.IsDepth() || !depth.info.HasStencil()) {
		EXIT("TextureCache: stencil association requires a depth/stencil image\n");
	}

	ImageId association {};
	for (const auto id: FindImagesInRegion(stencil.address, stencil.size, false)) {
		const auto owner = m_slot_images.try_get(id);
		if (owner != nullptr && owner->info.data.address == stencil.address) {
			association = id;
		}
	}
	if (!association) {
		ImageInfo info {};
		info.data   = stencil;
		info.extent = depth.info.extent;
		association = InsertImage(info);
	}
	auto& record = m_slot_images[association];
	TouchImage(record);
	record.depth_id = depth_id;
}

ImageId TextureCache::FindStencilAssociation(GuestRange stencil) {
	if (!stencil.Valid()) {
		return {};
	}
	std::scoped_lock lock {m_lock};
	ImageId          association {};
	for (const auto id: FindImagesInRegion(stencil.address, stencil.size, false)) {
		const auto owner = m_slot_images.try_get(id);
		if (owner != nullptr && owner->info.data.address == stencil.address) {
			association = id;
		}
	}
	return association;
}

ImageId TextureCache::FindImage(ImageDesc& desc, bool exact_format) {
	// Session 68, gate "amut": creates and merges host images.
	Common::FrameStats::MutScope mutate_scope(
	    Common::Gates::Enabled(Common::Gates::Gate::MutateTime));
	auto& command = m_scheduler.Current();
	if (command.IsInvalid()) {
		EXIT("TextureCache: image lookup requires a valid command buffer\n");
	}
	ValidateImageDesc(desc);
	ConstrainSampledSource(desc);
	if (desc.info.data.Empty()) {
		std::scoped_lock lock {m_lock};
		return GetNullImage(desc);
	}
	Common::DrawStat::Mark(Common::DrawStat::TexSlow);

	ImageId result {};
	{
		std::scoped_lock lock {m_lock};
		const auto       candidates =
		    FindImagesInRegion(desc.info.data.address, desc.source_size != 0 ? desc.source_size : desc.info.data.size, false);

		for (const auto id: candidates) {
			const auto& image = m_slot_images[id];
			if (SameBacking(image.info, desc.info, exact_format)) {
				result = id;
			}
		}

		int32_t view_mip   = -1;
		int32_t view_layer = -1;
		if (!result) {
			for (const auto candidate: candidates) {
				view_mip                = -1;
				view_layer              = -1;
				const auto& merged_info = result ? m_slot_images[result].info : desc.info;
				const auto  overlap     = ResolveOverlap(merged_info, desc.type, candidate, result);
				if (overlap.image) {
					result     = overlap.image;
					view_mip   = overlap.mip;
					view_layer = overlap.layer;
				}
			}
		}

		if (result) {
			auto& resolved = m_slot_images[result];
			if (exact_format && resolved.info.pixel_format != desc.info.pixel_format) {
				result = {};
			} else if (resolved.info.resources < desc.info.resources) {
				FreeImage(result, __func__, __LINE__);
				result = {};
			}
		}
		if (!result) {
			result         = InsertImage(desc.info);
			auto& inserted = m_slot_images[result];
			if (m_buffer_cache.HasGpuDirtyBytes(inserted.info.data.address,
			                                    inserted.info.data.size)) {
				inserted.MarkBufferModified();
			}
		}
		auto& image = m_slot_images[result];
		if (desc.type == BindingType::VideoOut &&
		    desc.info.metadata.compression != VideoOutCompression::Uncompressed) {
			const bool guest_dirty = image.IsBufferModified() || image.IsCpuDirty();
			const bool native_current =
			    (image.usage.render_target || image.IsGpuModified()) && !guest_dirty;
			if (!native_current) {
				EXIT("TextureCache: compressed video-out read requires clean native GPU "
				     "contents\n");
			}
		}
		if (view_mip >= 0) {
			desc.view_info.base_level = static_cast<uint32_t>(view_mip);
		}
		if (view_layer >= 0) {
			desc.view_info.base_layer = static_cast<uint32_t>(view_layer);
		}
		image.tick_accessed_last = m_scheduler.CurrentTick();
		ConfigureImageSourceUnlocked(result, desc);
		TouchImage(image);
	}
	return result;
}

void TextureCache::UpdateImage(ImageId id) {
	std::scoped_lock lock {m_lock};
	auto&            image = m_slot_images[id];
	TouchImage(image);
	RefreshImage(id);
}

ImageId TextureCache::FindImageFromRange(uint64_t address, uint64_t size, bool ensure_valid) {
	if (!GuestRange {address, size}.Valid()) {
		return {};
	}
	std::scoped_lock lock {m_lock};
	ImageIds         matches;
	for (const auto id: FindImagesInRegion(address, size, false)) {
		auto owner = m_slot_images.try_get(id);
		if (owner == nullptr || owner->info.data.address != address) {
			continue;
		}
		if (ensure_valid && owner->depth_id) {
			owner = m_slot_images.try_get(owner->depth_id);
		}
		if (owner == nullptr || (ensure_valid && !SafeToDownload(*owner))) {
			continue;
		}
		matches.push_back(id);
	}
	ImageId selected {};
	if (matches.size() == 1) {
		selected = matches.front();
	} else {
		for (const auto id: matches) {
			const auto& image = m_slot_images[id];
			if (image.info.data.size == size) {
				selected = id;
				break;
			}
		}
	}
	if (selected && ensure_valid) {
		const auto owner = m_slot_images.try_get(selected);
		if (owner != nullptr && owner->depth_id) {
			selected = owner->depth_id;
		}
	}
	return selected;
}

TextureCache::ShadowImageAnswer TextureCache::ShadowProbe(const ShadowImageQuery& query) {
	namespace FS  = Common::FrameStats;
	const auto t0 = FS::Enabled() ? FS::NowNs() : 0;
	m_lock.lock();
	if (t0 != 0) {
		FS::Add(FS::Counter::ShadowLockNs, FS::NowNs() - t0);
	}
	std::lock_guard<TrackingSpinLock> guard(m_lock, std::adopt_lock);
	const auto* image = m_slot_images.try_get(query.id);
	if (image == nullptr) {
		return ShadowImageAnswer::Gone;
	}
	// ResolveTextureWith, memo hit.
	if (!image->registered || image->binding.needs_rebind || image->depth_id ||
	    image->info.data != query.data || image->info.extent != query.extent) {
		return ShadowImageAnswer::Stale;
	}
	if (!query.eligible) {
		return ShadowImageAnswer::Slow;
	}
	// RebindImages, gate "texfast".
	if (!query.has_view || image->bind_stamp.load(std::memory_order_acquire) != query.fast_stamp ||
	    image->pending_levels != 0) {
		return ShadowImageAnswer::View;
	}
	// TextureSourceSettled (descriptors.cpp).
	if (image->info.IsBlock() && !image->IsGpuModified()) {
		const bool same = image->info.data == query.data && image->info.extent == query.extent &&
		                  image->info.resources == query.resources;
		const auto first = same ? query.source_first_level : 0u;
		const auto size  = same && query.source_size != 0 ? query.source_size : image->info.data.size;
		const bool settled = (image->binding.is_bound && first > image->source_first_level) ||
		                     (first == image->source_first_level && size == image->SourceRange().size);
		if (!settled) {
			return ShadowImageAnswer::View;
		}
	}
	return ShadowImageAnswer::Fast;
}

vk::ImageView TextureCache::FindTexture(ImageId id, const ImageDesc& desc) {
	Common::FrameStats::Scope view_scope(Common::FrameStats::Counter::BindFindTexNs,
	                                   Common::FrameStats::Counter::BindFindTex);
	// Session 68, gate "amut": everything below mutates - the source configuration, the LRU touch,
	// the DCC clear, the upload of the image, the download tracking and the view cache.
	Common::FrameStats::MutScope mutate_scope(
	    Common::Gates::Enabled(Common::Gates::Gate::MutateTime));
	std::scoped_lock lock {m_lock};
	ConfigureImageSourceUnlocked(id, desc);
	auto&            image = m_slot_images[id];
	TouchImage(image);
	if (!image.info.data.Empty()) {
		Common::DrawStat::Mark(Common::DrawStat::TexSlow);
		if (!image.registered || image.depth_id || image.binding.needs_rebind) {
			EXIT("TextureCache: texture requires rediscovery before final acquisition\n");
		}
	}
	if (desc.type == BindingType::Storage) {
		Common::DrawStat::Mark(Common::DrawStat::GpuWrite);
		// Session 123, knob "skipceil" = 2 (census, W3 (b)): the storage write is counted by W2, not stamped here.
		const Common::SkipCeil::AcqGuard skc_acq;
		image.MarkGpuModified();
	}
	auto view_info = desc.view_info;
	if (!image.info.data.Empty()) {
		{
			// Session 124, knob "skipceil" = 3 (closure census, ROADMAP s122 item 47(b), N12): the materialization of a
			// deferred clear while a binding resolves is no write event (an Lt write of the trigger).
			const SkcCensus::LazyScope skc3_lazy(SkcCensus::LazyMat);
			PrepareDccClear(id, desc);
		}
		{
			// Session 71, candidate C3 (counters only): a storage binding writes the image too, but
			// with scattered texels, so "the pass overwrites it anyway" is far weaker there than
			// for an attachment; a sampled binding READS it and C3 must never touch those. The
			// switch below EXITs on any other binding type, so these two are exhaustive. The scope
			// covers RefreshImage alone - PrepareDccClear above can reach ClearImage, which
			// publishes UploadSite::ClearOp for the upload its partial-clear path performs itself.
			const UploadSiteScope upload_site {desc.type == BindingType::Storage
			                                       ? UploadSite::StorageImage
			                                       : UploadSite::Sampled,
			                                   false, false};
			RefreshImage(id, desc.type == BindingType::Texture);
		}
		if (image.pending_levels != 0) {
			// Sampled bind of a texture whose top levels are still pending: bring them in within
			// the frame budget, otherwise clamp this view's LOD to the resident levels.
			NoteUploadFrame();
			const uint32_t min_lod = image.pending_levels > view_info.base_level
			                             ? image.pending_levels - view_info.base_level
			                             : 0u;
			if (min_lod != 0) {
				if (min_lod >= view_info.level_count ||
				    m_frame_pending_bytes + image.pending_bytes <= MipDefer().budget_bytes) {
					CompletePendingUpload(image);
				} else {
					view_info.min_lod = std::max(view_info.min_lod, min_lod << 8u);
					Common::FrameStats::Add(Common::FrameStats::Counter::ImgMinLodViews, 1);
				}
			}
		}
	}
	switch (desc.type) {
		case BindingType::Texture: break;
		case BindingType::Storage:
			if (!image.info.data.Empty()) {
				const Common::SkipCeil::AcqGuard skc_acq; // Session 123 (census, W3 (b)): W2 counts this write
				CommitGpuWrite(image);
			}
			TrackImageDownload(id, image);
			break;
		default: EXIT("TextureCache: invalid texture binding\n");
	}
	const auto view = image.FindView(view_info);
	NameImageBinding(m_graphics, image, view, desc.type, view_info);
	return view;
}

vk::ImageView TextureCache::FindRenderTarget(ImageId id, const ImageDesc& desc,
                                             uint32_t guest_clear_regs) {
	if (desc.type != BindingType::RenderTarget) {
		EXIT("TextureCache: invalid color-target binding\n");
	}
	std::scoped_lock lock {m_lock};
	auto&            image = m_slot_images[id];
	if (!image.registered || image.depth_id || image.binding.needs_rebind) {
		EXIT("TextureCache: color target requires rediscovery before final acquisition\n");
	}
	TouchImage(image);
	image.MarkGpuModified();
	image.usage.render_target = true;
	// Session 71, candidate C3 (counters only). Observed HERE, before PrepareDccClear and
	// PrepareCmaskClear: when they succeed on a whole image, ClearImage ends in CommitGpuWrite,
	// which drops m_buffer_modified, and the upload this is about to size no longer exists.
	bool     c3_reg_clear = false;
	bool     c3_fill      = false;
	bool     c3_pop       = false;
	uint64_t c3_note_kb   = 0;
	const auto c3_clear_uploads_before = t_clear_caused_uploads;
	if (Common::FrameStats::Enabled()) {
		namespace FS       = Common::FrameStats;
		const bool reg_fc  = (guest_clear_regs & (kRegColorFastClear | kRegColorCmaskAddr)) ==
		                    (kRegColorFastClear | kRegColorCmaskAddr);
		const bool reg_dcc = (guest_clear_regs & (kRegColorDccEnable | kRegColorDccAddr)) ==
		                     (kRegColorDccEnable | kRegColorDccAddr);
		const bool reg_key = reg_dcc && (guest_clear_regs & kRegColorDccKey) != 0;
		const bool kind_ok = desc.info.metadata.kind != ImageMetadataKind::None;
		c3_fill            = MetaFillPendingLocked(desc);
		c3_reg_clear       = reg_fc || reg_key;
		c3_note_kb         = image.SourceRange().size / 1024u;
		c3_pop =
		    image.IsBufferModified() && !image.IsCpuDirty() &&
		    image.SourceRange().size >=
		        static_cast<uint64_t>(Common::Gates::Value(Common::Gates::Knob::ImageSkipKb)) *
		            1024u;
		FS::Add(FS::Counter::C3ColorAcquires, 1);
		if (reg_fc) {
			FS::Add(FS::Counter::C3ColorRegFastClear, 1);
		}
		if (reg_dcc) {
			FS::Add(FS::Counter::C3ColorRegDcc, 1);
		}
		if (reg_key) {
			FS::Add(FS::Counter::C3ColorRegDccKey, 1);
		}
		if (kind_ok) {
			FS::Add(FS::Counter::C3ColorMetaKind, 1);
		}
		if ((reg_fc || reg_dcc) && !kind_ok) {
			// Register-backed clear state that colorRenderTarget.cpp dropped to kind = None - for
			// CMASK that is its width%1024 / height%1024 guard, which no extent of the imgskip
			// population can pass.
			FS::Add(FS::Counter::C3ColorRegDropped, 1);
		}
		if (c3_fill) {
			FS::Add(FS::Counter::C3ColorFillPending, 1);
		}
		if (c3_pop) {
			FS::Add(FS::Counter::C3ColorPop, 1);
			FS::Add(FS::Counter::C3ColorPopKb, c3_note_kb);
		}
	}
	{
		// Session 124, knob "skipceil" = 3 (closure census, ROADMAP s122 item 47(b)): the materialization of a deferred
		// clear at a target acquisition or a fast-clear eliminate is no write event (an Lt write of the trigger).
		const SkcCensus::LazyScope skc3_lazy(SkcCensus::LazyMat);
		PrepareDccClear(id, desc);
		PrepareCmaskClear(id, desc);
	}
	// Those two calls are the ONLY thing between the observation and the upload decision, so an
	// image that left the population here left it because a recognised guest clear cancelled its
	// upload - unless the clear performed the upload itself, which the thread-local counter
	// separates out. NOTHING in the tree reports this number today.
	if (c3_pop && !image.IsBufferModified() &&
	    t_clear_caused_uploads == c3_clear_uploads_before) {
		Common::FrameStats::Add(Common::FrameStats::Counter::C3ColorCancelled, 1);
		Common::FrameStats::Add(Common::FrameStats::Counter::C3ColorCancelledKb, c3_note_kb);
	}
	{
		// The scope covers RefreshImage ALONE - never the two Prepare*Clear calls above.
		const UploadSiteScope upload_site {UploadSite::ColorTarget, c3_reg_clear, c3_fill};
		RefreshImage(id);
	}
	CommitGpuWrite(image);
	TrackImageDownload(id, image);
	const auto view = image.FindView(desc.view_info);
	NameImageBinding(m_graphics, image, view, desc.type, desc.view_info);
	return view;
}

vk::ImageView TextureCache::FindDepthTarget(ImageId id, const ImageDesc& desc,
                                            uint32_t guest_clear_regs) {
	if (desc.type != BindingType::DepthTarget) {
		EXIT("TextureCache: invalid depth-target binding\n");
	}
	std::scoped_lock lock {m_lock};
	auto&            image = m_slot_images[id];
	if (!image.registered || image.depth_id || image.binding.needs_rebind) {
		EXIT("TextureCache: depth target requires rediscovery before final acquisition\n");
	}
	TouchImage(image);
	image.MarkGpuModified();
	image.usage.depth_target = true;
	// Session 71, candidate C3 (counters only): depth is the ONE attachment whose clear the guest
	// states per pass, in DB_RENDER_CONTROL.DEPTH_CLEAR_ENABLE. Colour has no analogue of that
	// register, which is the whole reason C3's premise is in question. No fill reading here: no
	// counter would read it.
	Common::FrameStats::Add(Common::FrameStats::Counter::C3DepthAcquires, 1);
	{
		const UploadSiteScope upload_site {UploadSite::DepthTarget,
		                                   (guest_clear_regs & kRegDepthClear) != 0, false};
		RefreshImage(id);
	}
	if (desc.info.HasMetadata()) {
		// Session 124, knob "skipceil" = 3 (closure census, ROADMAP s122 item 47(v)): a new link of the image to this
		// surface, or a seeded clear state (insertion / type change: no clear event).
		const bool skc3_link = Common::SkipCeil::t_mode == 3 &&
		                       (image.info.metadata.kind != desc.info.metadata.kind ||
		                        image.info.metadata.range.address != desc.info.metadata.range.address);
		Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 47(z), N1
		image.info.metadata = desc.info.metadata;
		auto [metadata, inserted] =
		    m_surface_metas.try_emplace(desc.info.metadata.range.address,
		                                MetaDataInfo {.type       = MetaDataInfo::Type::HTile,
		                                              .clear_mask = image.info.htile_clear_mask});
		bool skc3_seed = inserted;
		if (inserted) {
			BumpMetaEpoch();
		}
		if (!inserted && metadata->second.type != MetaDataInfo::Type::HTile) {
			// PS5 allocations can reuse DCC storage as HTile while the old color image is cached.
			// The depth binding defines the new type; incompatible fill state cannot carry over.
			metadata->second = {.type       = MetaDataInfo::Type::HTile,
			                    .clear_mask = image.info.htile_clear_mask};
			BumpMetaEpoch();
			skc3_seed = true;
		}
		if (Common::SkipCeil::t_mode == 3 && (skc3_link || skc3_seed) && metadata->second.clear_mask != 0) [[unlikely]] {
			SkcCensus::G3MetaLate(image, desc.info.metadata.range.address, metadata->second.clear_mask, skc3_seed);
		}
	}
	CommitGpuWrite(image);
	if (desc.info.HasStencil()) {
		AssociateStencil(id, desc.info.stencil);
	}
	const auto view = image.FindView(desc.view_info);
	NameImageBinding(m_graphics, image, view, desc.type, desc.view_info);
	return view;
}

void TextureCache::MarkGpuWritten(ImageId id) {
	std::scoped_lock lock {m_lock};
	auto&            image = m_slot_images[id];
	if (!image.registered || image.depth_id) {
		EXIT("TextureCache: cannot mark an unavailable image GPU-written\n");
	}
	TrackImage(id);
	CommitGpuWrite(image);
}

void TextureCache::CommitGpuWrite(Image& image) {
	if (image.depth_id || image.backing.image == nullptr) {
		EXIT("TextureCache: stencil association cannot own image contents\n");
	}
	CompletePendingUpload(image);
	image.ClearBufferModified();
	if (image.IsCpuDirty()) {
		image.RefreshComplete();
	}
	image.MarkGpuModified();
}

// Session 70: clr_decode reads 1.000 per frame, so exactly one recognised clear per frame is lost
// in the decoder. Whether that is worth fixing depends on which surface it is, and the counter
// cannot say. Print each distinct format once, at most 16 lines for the whole run.
static void LogClearDecodeFailure(const Image& image, const char* aspect, uint32_t packed_clear,
                                  uint64_t address, uint64_t size) {
	static std::mutex                            seen_mutex;
	static std::vector<std::pair<uint32_t, int>> seen;
	const auto key = static_cast<uint32_t>(image.info.pixel_format);
	{
		std::scoped_lock lock {seen_mutex};
		if (seen.size() >= 16) {
			return;
		}
		for (const auto& entry: seen) {
			if (entry.first == key && entry.second == static_cast<int>(aspect[0])) {
				return;
			}
		}
		seen.emplace_back(key, static_cast<int>(aspect[0]));
	}
	LOGF("ClearDecodeFail: aspect=%s vkformat=%u pixel_format=%u addr=0x%016" PRIx64
	     " size=0x%" PRIx64 " value=0x%08" PRIx32 " extent=%ux%u levels=%u layers=%u tile=%u\n",
	     aspect, static_cast<uint32_t>(image.backing.format),
	     static_cast<uint32_t>(image.info.pixel_format), address, size, packed_clear,
	     image.info.extent.width, image.info.extent.height, image.info.resources.levels,
	     image.backing.layers, static_cast<uint32_t>(image.info.tile_mode));
}

// Session 71: the outcome of the last ClearImageFromBuffer on this thread, for KYTY_CLEAR_TRACE.
// Written at every exit, read only by the trace in renderCompute.cpp. Never changes a decision.
static thread_local const char* g_last_clear_outcome = "invalid";

const char* TextureCacheLastClearOutcome() {
	return g_last_clear_outcome;
}

bool TextureCache::ClearImageFromBuffer(CommandBuffer& command, uint64_t address, uint64_t size,
                                        uint32_t packed_clear) {
	g_last_clear_outcome = "invalid";
	if (command.IsInvalid() || !GuestRange {address, size}.Valid()) {
		EXIT("TextureCache: invalid image clear\n");
	}
	std::scoped_lock     lock {m_lock};
	ImageId              selected {};
	vk::ImageAspectFlags aspect {};
	// Session 70: count the outcome. The four declines below mean different things and want
	// different fixes, so they are counted apart. KiB at the increment site, never through the
	// "micros" print path.
	const auto note_kb = static_cast<uint64_t>(size / 1024u);
	uint64_t   overlap_only = 0;
	for (const auto id: FindImagesInRegion(address, size, false)) {
		auto owner = m_slot_images.try_get(id);
		if (owner == nullptr) {
			continue;
		}
		vk::ImageAspectFlags candidate {};
		ImageId              candidate_id = id;
		if (owner->depth_id && owner->info.data.address == address &&
		    owner->info.data.size == size) {
			candidate    = vk::ImageAspectFlagBits::eStencil;
			candidate_id = owner->depth_id;
			owner        = m_slot_images.try_get(candidate_id);
			if (owner == nullptr || owner->backing.image == nullptr || !owner->info.HasStencil()) {
				continue;
			}
		} else if (!owner->depth_id && owner->info.data.address == address &&
		           owner->info.data.size == size) {
			candidate = owner->info.IsDepth() ? vk::ImageAspectFlagBits::eDepth
			                                  : vk::ImageAspectFlagBits::eColor;
		}
		if (!candidate) {
			overlap_only++;
			continue;
		}
		if (selected && selected != candidate_id) {
			g_last_clear_outcome = "ambig";
			Common::FrameStats::Add(Common::FrameStats::Counter::ClearAmbiguous, 1);
			Common::FrameStats::Add(Common::FrameStats::Counter::ClearAmbiguousKb, note_kb);
			Common::FrameStats::Add(Common::FrameStats::Counter::ClearOverlapOnly, overlap_only);
			return false;
		}
		selected = candidate_id;
		aspect   = candidate;
	}
	if (!selected) {
		g_last_clear_outcome = "none";
		Common::FrameStats::Add(Common::FrameStats::Counter::ClearNoMatch, 1);
		Common::FrameStats::Add(Common::FrameStats::Counter::ClearNoMatchKb, note_kb);
		Common::FrameStats::Add(Common::FrameStats::Counter::ClearOverlapOnly, overlap_only);
		return false;
	}
	auto&          image = m_slot_images[selected];
	vk::ClearValue clear {};
	if (aspect == vk::ImageAspectFlagBits::eColor) {
		if (!DecodePackedColorClear(image.info.pixel_format, packed_clear, clear.color)) {
			g_last_clear_outcome = "decode";
			Common::FrameStats::Add(Common::FrameStats::Counter::ClearDecodeFail, 1);
			LogClearDecodeFailure(image, "color", packed_clear, address, size);
			return false;
		}
	} else {
		uint8_t stencil_clear = 0;
		if ((aspect == vk::ImageAspectFlagBits::eDepth &&
		     !DecodePackedDepthClear(image.info.pixel_format, packed_clear, clear.depthStencil.depth)) ||
		    (aspect == vk::ImageAspectFlagBits::eStencil &&
		     !DecodePackedStencilClear(packed_clear, stencil_clear))) {
			g_last_clear_outcome = "decode";
			Common::FrameStats::Add(Common::FrameStats::Counter::ClearDecodeFail, 1);
			LogClearDecodeFailure(image, aspect == vk::ImageAspectFlagBits::eDepth ? "depth" : "stencil",
			                      packed_clear, address, size);
			return false;
		}
		clear.depthStencil.stencil = stencil_clear;
	}
	ClearImage(command, selected, image.backing.format,
	           {aspect, 0, image.info.resources.levels, 0, image.info.TransferLayers()}, clear);
	g_last_clear_outcome = "ok";
	Common::FrameStats::Add(Common::FrameStats::Counter::ClearConsumed, 1);
	Common::FrameStats::Add(Common::FrameStats::Counter::ClearConsumedKb, note_kb);
	return true;
}

// Session 124, knob "skipceil" = 3 (closure census, ROADMAP s122 item 47(e)): the subresources ClearImage writes; the
// slices of a volume are no keys (its layers are).
static SkcCensus::Sub Skc3ClearSub(const Image& image, const vk::ImageSubresourceRange& range) noexcept {
	const bool volume = image.info.IsVolume();
	return {range.baseMipLevel, range.levelCount, volume ? 0u : range.baseArrayLayer,
	        volume ? UINT32_MAX : range.layerCount, 0u, SkcCensus::AspBits(range.aspectMask)};
}

void TextureCache::ClearImage(CommandBuffer& command, ImageId id, vk::Format format,
                              const vk::ImageSubresourceRange& range, const vk::ClearValue& clear) {
	auto& image = m_slot_images[id];
	TraceWatchedImage("clear", image);
	Common::DrawStat::Mark(Common::DrawStat::ImgUp);
	Common::DrawStat::Cut(Common::DrawStat::EdgeUpload);
	const auto aspects = image.info.IsDepth() ? ImageViewOps::DepthAspectMask(image.backing.format)
	                                          : vk::ImageAspectFlagBits::eColor;
	EXIT_IF(range.baseMipLevel >= image.info.resources.levels);
	const auto layers = image.info.IsVolume()
	                        ? std::max(image.info.extent.depth >> range.baseMipLevel, 1u)
	                        : image.backing.layers;
	EXIT_IF(command.IsInvalid() || image.depth_id || !range.aspectMask || range.levelCount == 0 ||
	        range.levelCount > image.info.resources.levels - range.baseMipLevel ||
	        range.layerCount == 0 || range.baseArrayLayer >= layers ||
	        range.layerCount > layers - range.baseArrayLayer ||
	        (range.aspectMask & aspects) != range.aspectMask);
	const bool full_image = range.aspectMask == aspects && range.baseMipLevel == 0 &&
	                        range.levelCount == image.info.resources.levels &&
	                        range.baseArrayLayer == 0 && range.layerCount == layers;
	TrackImage(id);
	if (!full_image && (image.IsBufferModified() || image.IsCpuDirty())) {
		// Session 71, candidate C3 (counters only): a PARTIAL clear must first bring in the texels
		// it is not going to write, so this upload is CAUSED by the clear. Publishing the site
		// here keeps it out of the colour-target ceiling and out of c3_ct_canc.
		const UploadSiteScope upload_site {UploadSite::ClearOp, false, false};
		InitializeImage(id);
		if (image.info.samples == 1 && (image.IsBufferModified() || image.IsCpuDirty())) {
			EXIT("TextureCache: image clear retained guest ownership\n");
		}
	}
	command.EndRendering(RenderPassEnd::Clear);
	// Transfer clears use the backing format; aliased clears must encode through their view.
	if (format != image.backing.format || (image.info.IsVolume() && !full_image)) {
		EXIT_NOT_IMPLEMENTED(range.aspectMask != vk::ImageAspectFlagBits::eColor ||
		                     range.levelCount != 1);
		ImageViewInfo view {};
		view.format = format;
		view.type   = range.layerCount == 1 ? vk::ImageViewType::e2D : vk::ImageViewType::e2DArray;
		view.base_level  = range.baseMipLevel;
		view.base_layer  = range.baseArrayLayer;
		view.layer_count = range.layerCount;
		view.usage       = vk::ImageUsageFlagBits::eColorAttachment;
		image.Transit(vk::ImageLayout::eColorAttachmentOptimal,
		              vk::AccessFlagBits2::eColorAttachmentWrite, {}, command.Handle());
		vk::RenderingAttachmentInfo attachment {};
		attachment.imageView   = image.FindView(view);
		attachment.imageLayout = vk::ImageLayout::eColorAttachmentOptimal;
		attachment.loadOp      = vk::AttachmentLoadOp::eClear;
		attachment.storeOp     = vk::AttachmentStoreOp::eStore;
		attachment.clearValue  = clear;
		vk::RenderingInfo rendering {};
		rendering.renderArea.extent = {
		    std::max(image.info.extent.width >> range.baseMipLevel, 1u),
		    std::max(image.info.extent.height >> range.baseMipLevel, 1u)};
		rendering.layerCount           = range.layerCount;
		rendering.colorAttachmentCount = 1;
		rendering.pColorAttachments    = &attachment;
		command.Handle().beginRendering(&rendering);
		// Session 72: this pass never reaches CommandBuffer::BeginRenderingImpl, so rp_begin does
		// not count it - and the EndRendering above charged a closure to the census that has no
		// matching opening. One Add per pass; no decision touched.
		Common::FrameStats::Add(Common::FrameStats::Counter::PassAliasClear, 1);
		Common::FrameStats::Add(Common::FrameStats::Counter::PassAliasClearKpx,
		                        static_cast<uint64_t>(rendering.renderArea.extent.width) *
		                            rendering.renderArea.extent.height / 1024U *
		                            rendering.layerCount);
		command.Handle().endRendering();
		const SkcCensus::SubScope skc3_sub(Skc3ClearSub(image, range)); // Session 124 (item 47(e))
		CommitGpuWrite(image);
		return;
	}
	image.Transit(vk::ImageLayout::eTransferDstOptimal, vk::AccessFlagBits2::eTransferWrite, {},
	              command.Handle());
	auto native_range = range;
	if (image.info.IsVolume()) {
		native_range.baseArrayLayer = 0;
		native_range.layerCount     = 1;
	}
	if (range.aspectMask == vk::ImageAspectFlagBits::eColor) {
		command.Handle().clearColorImage(image.backing.image, vk::ImageLayout::eTransferDstOptimal,
		                                 &clear.color, 1, &native_range);
	} else {
		command.Handle().clearDepthStencilImage(image.backing.image,
		                                        vk::ImageLayout::eTransferDstOptimal,
		                                        &clear.depthStencil, 1, &native_range);
	}
	const SkcCensus::SubScope skc3_sub(Skc3ClearSub(image, range)); // Session 124 (item 47(e))
	CommitGpuWrite(image);
}

void TextureCache::InvalidateMemory(uint64_t address, uint64_t size) {
	if (!GuestRange {address, size}.Valid()) {
		EXIT("TextureCache: invalid memory-invalidation range\n");
	}
	// Gate "texfaulthint". Every CPU write fault takes this global lock, and most land on pages
	// without any image (tex_inval_empty). m_image_page_hint[page] counts the images of one page
	// of m_image_page_table: raised under m_lock before an image is added to that page, lowered
	// after it is removed. A lock-free zero therefore means no image was indexed on the page at
	// the moment of the read, which is where a locked call could also have run - before any
	// registration still in flight - and found no candidate (InvalidateCpuAliases walks exactly
	// these pages). A false "zero" cannot happen: a registered image keeps the count above zero
	// until UnregisterImage has untracked it and removed it from the index. A registration in
	// flight is ordered after this call either way; its first upload reads guest memory later.
	// A nonzero hint ("maybe") only costs the lock.
	const bool hint_gate = Common::Gates::Enabled(Common::Gates::Gate::TexFaultHint);
	if ((hint_gate || Common::FrameStats::Enabled()) && !MayHaveImages(address, size)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::TexHintZero, 1);
		if (hint_gate) {
			Common::FrameStats::Add(Common::FrameStats::Counter::TexInvalidations, 1);
			Common::FrameStats::Add(Common::FrameStats::Counter::TexInvalidateEmpty, 1);
			return;
		}
	}
	std::scoped_lock lock {m_lock};
	InvalidateCpuAliases(address, size);
}

void TextureCache::DownloadDepth(Image& image, Buffer& destination, uint64_t destination_offset) {
	Common::DrawStat::Mark(Common::DrawStat::BufUp);
	Common::DrawStat::Cut(Common::DrawStat::EdgeUpload);
	const auto&    info             = image.info;
	const auto     layers           = info.resources.layers;
	const auto     full_slice_size  = info.data.size / layers;
	const auto     transfer_bytes   = DepthAspectTransferBytes(info.pixel_format);
	const uint64_t texels_per_slice = static_cast<uint64_t>(info.pitch) * info.extent.height;
	EXIT_NOT_IMPLEMENTED(transfer_bytes == 0 || texels_per_slice > UINT32_MAX ||
	                     texels_per_slice > UINT64_MAX / transfer_bytes ||
	                     texels_per_slice > UINT64_MAX / info.bytes_per_block);
	const uint64_t transfer_slice = texels_per_slice * transfer_bytes;
	const uint64_t guest_slice    = texels_per_slice * info.bytes_per_block;
	EXIT_NOT_IMPLEMENTED(transfer_slice > UINT64_MAX / layers);
	const uint64_t transfer_size = transfer_slice * layers;
	EXIT_NOT_IMPLEMENTED(guest_slice > full_slice_size);
	auto copies = BuildDepthCopies(info, full_slice_size);
	if (transfer_bytes == info.bytes_per_block) {
		if (!info.IsTiled()) {
			for (auto& copy: copies) {
				copy.bufferOffset += destination_offset;
			}
			image.Download(copies, destination.Handle(), destination_offset, info.data.size);
			return;
		}
		const auto tiles = BuildDepthTiles(info);
		m_tiler.TileImage(image, copies, destination.Handle(), destination_offset, info.data.size,
		                  info.data.size, tiles);
		return;
	}
	EXIT_NOT_IMPLEMENTED(info.bytes_per_block != sizeof(uint16_t) ||
	                     transfer_bytes != sizeof(uint32_t));
	for (uint32_t layer = 0; layer < layers; layer++) {
		copies[layer].bufferOffset = transfer_slice * layer;
	}
	auto host_linear = m_tiler.GetScratchBuffer(transfer_size);
	image.Download(copies, host_linear.buffer, 0, host_linear.size);
	const bool tiled        = info.IsTiled();
	auto       guest_linear = tiled ? m_tiler.GetScratchBuffer(info.data.size)
	                                : TileManager::Result {destination.Handle(), destination_offset,
	                                                       destination.Size() - destination_offset};
	m_tiler.ConvertD16(host_linear, guest_linear, TileManager::D16Direction::Demote,
	                   DepthAspectTransferFormat(info.pixel_format) == vk::Format::eD32Sfloat,
	                   {.width               = info.extent.width,
	                    .height              = info.extent.height,
	                    .layers              = layers,
	                    .source_row_stride   = static_cast<uint64_t>(info.pitch) * sizeof(uint32_t),
	                    .target_row_stride   = static_cast<uint64_t>(info.pitch) * sizeof(uint16_t),
	                    .source_slice_stride = transfer_slice,
	                    .target_slice_stride = full_slice_size});
	if (!tiled) {
		return;
	}
	const auto tiles = BuildDepthTiles(info);
	m_tiler.Tile(guest_linear.buffer, guest_linear.offset, info.data.size, destination.Handle(),
	             destination_offset, info.data.size, tiles);
}

void TextureCache::DownloadImage(Image& image, Buffer& destination, uint64_t destination_offset,
                                     uint64_t destination_size, ImageDownload transfer) {
	Common::DrawStat::Mark(Common::DrawStat::BufUp);
	Common::DrawStat::Cut(Common::DrawStat::EdgeUpload);
	if (!transfer.valid) {
		EXIT("TextureCache: invalid image download transfer\n");
	}
	if (transfer.depth_target) {
		if (destination_size != image.info.data.size) {
			EXIT("TextureCache: partial depth image download is unsupported\n");
		}
		DownloadDepth(image, destination, destination_offset);
		return;
	}

	auto&      texture   = transfer.texture;
	const auto transform = texture.swap_bgra16 ? TileManager::ColorTransform::SwapBgra16
	                                           : TileManager::ColorTransform::None;
	if (texture.tiles.empty()) {
		if (transform == TileManager::ColorTransform::SwapBgra16) {
			auto linear = m_tiler.GetScratchBuffer(destination_size);
			image.Download(texture.regions, linear.buffer, 0, linear.size);
			m_tiler.SwapBgra16(linear,
			                   {destination.Handle(), destination_offset, destination_size});
			return;
		}
		for (auto& copy: texture.regions) {
			copy.bufferOffset += destination_offset;
		}
		image.Download(texture.regions, destination.Handle(), destination_offset, destination_size);
		return;
	}

	m_tiler.TileImage(image, texture.regions, destination.Handle(), destination_offset,
	                  destination_size, texture.LinearSize(), texture.tiles, transform);
}

bool BufferCache::SynchronizeBufferFromImage(Buffer& buffer, uint64_t vaddr, uint64_t size) {
	const auto selected = m_texture_cache.FindImageFromRange(vaddr, size);
	if (!selected) {
		return false;
	}

	std::scoped_lock lock {m_texture_cache.m_lock};
	auto& image = m_texture_cache.m_slot_images[selected];
	// The GPU thread owns image retirement; CPU invalidation can dirty this image after lookup.
	if (!m_texture_cache.SafeToDownload(image)) {
		return false;
	}
	if (!buffer.IsInBounds(image.info.data.address, 1)) {
		return false;
	}
	const auto buf_offset = buffer.Offset(image.info.data.address);
	const auto available  = buffer.Size() - buf_offset;
	uint32_t   levels     = 0;
	uint64_t   copy_size  = 0;
	if (image.info.IsVolume()) {
		// Volume mips contain strided block slices, so a mip's linear span cannot prove that
		// every retained slice fits. Keep volume synchronization whole-image only.
		if (!buffer.IsInBounds(image.info.data.address, image.info.data.size)) {
			return false;
		}
		levels    = image.info.resources.levels;
		copy_size = image.info.data.size;
	} else {
		for (; levels < image.info.resources.levels; ++levels) {
			const auto& mip = image.info.mip_layout[levels];
			if (mip.size == 0 || mip.offset > available || mip.size > available - mip.offset) {
				break;
			}
			copy_size = std::max(copy_size, mip.offset + mip.size);
		}
	}
	if (copy_size == 0) {
		return false;
	}
	auto transfer = m_texture_cache.BuildDownload(image);
	if (!transfer.valid) {
		return false;
	}
	if (transfer.depth_target && copy_size != image.info.data.size) {
		return false;
	}
	if (!transfer.depth_target && levels < image.info.resources.levels) {
		auto& texture = transfer.texture;
		std::erase_if(texture.regions, [levels](const vk::BufferImageCopy& region) {
			return region.imageSubresource.mipLevel >= levels;
		});
		if (texture.regions.empty()) {
			return false;
		}
		if (!texture.tiles.empty()) {
			texture.tiles.clear();
			if (!TextureBuildGpuTileInfos(copy_size, texture.regions, texture.layout, levels,
			                              texture.tiles)) {
				return false;
			}
		}
	}
	// Session 124, knob "skipceil" = 3 (closure census, ROADMAP s122 item 47(g)): the copy writes guest range
	// [address, +copy_size) of the buffer from the image - a write with no writer ("up"), before the graph read of the
	// operation (a texel binding reads it from G3ReadBufferLate, after ObtainBuffer).
	if (Common::SkipCeil::t_mode == 3) [[unlikely]] {
		SkcCensus::G3SyncImg(image.info.data.address, copy_size);
	}
	Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 47(z), N1
	m_texture_cache.DownloadImage(image, buffer, buf_offset, copy_size, std::move(transfer));
	return true;
}

bool TextureCache::DownloadImageMemory(ImageId id) {
	auto& image = m_slot_images[id];
	if (image.depth_id) {
		return false;
	}
	auto transfer = BuildDownload(image);
	if (!transfer.valid || !SafeToDownload(image)) {
		return false;
	}
	// Session 123, knob "skipceil" = 2 (census, s.3.2): the content of a D / T image goes to guest memory.
	if (Common::SkipCeil::t_mode >= 2) [[unlikely]] {
		SkcCensus::DownloadRead(image);
		if (Common::SkipCeil::t_mode == 3) {
			SkcCensus::G3Download(image); // Session 124: a write of guest memory with no writer (s.3.3.2)
		}
	}
	Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 47(z), N1
	const auto range    = image.info.data;
	auto&      download = m_buffer_cache.GetUtilityBuffer(MemoryUsage::Download);
	auto [mapped, offset] =
	    download.Map(range.size, std::max<uint64_t>(image.info.bytes_per_block, 4));
	if (mapped == nullptr) {
		// Session 96, gate "bindfloor" (MEASUREMENT ONLY, ROADMAP.md:1048-1053).  The ceiling
		// stub is licensed to break the PICTURE; it is not licensed to end the RUN, and run
		// bf96a ended here 38 frames after arming.
		// Map returns null in five places and four of them are unreachable on this call, so
		// the cause is not in doubt: Mapped() is non-empty (this ring was mapped thousands of
		// times in the unarmed arm of the same run), NormalizeReservation would need an
		// overflow of an alignment of at most 16, AlignUp likewise, and WaitPendingOperations
		// can only fail with allow_wait = false, which this call does not pass (it defaults to
		// true, streamBuffer.h) - a FULL ring waits, it does not return null.  What is left is
		// `mapped_size > Size()`: the image's guest range is larger than the whole 32 MiB
		// download ring (bufferCache.cpp, m_download_buffer).  Deterministic in the size, not a
		// pressure or pacing effect.
		// It becomes reachable under the floor because the floor halves the frame, the game's
		// DRS answers by raising the resolution (bf96a: rt_kpx/rt_att 2 010 -> 8 040 Kpx,
		// 1080p -> 2160p over 30 frames, 4.00x the area) and a linear colour target - which
		// FindColorTarget enrols for readback through TrackImageDownload, a path the floor
		// keeps - passes 32 MiB.  That is the DRS trap of ROADMAP.md:1062-1065 and the reason
		// knob "bfmode"=3 with "bfburn" exists; bf96a ran bfmode=1 and bf_burn_ns=0.
		// Abandoning the readback removes NO work from the measured path: the download could
		// not be performed at all, and until now the process died in its place.  It leaves the
		// guest with stale bytes for this image, which is a broken picture.  Both callers
		// already handle false - RunGarbageCollector postpones the image (retry_later) and
		// ProcessDownloadImages discards the result.
		// A NONZERO bf_dlskip IS ALSO A VERDICT ON THE RUN: it can only happen when the arms
		// are drawing different areas, so that run's frame numbers are void whatever else the
		// guards say.
		// The EXIT below is kept verbatim for every run without the gate, so a floor-less
		// binary behaves exactly as before.
		// Session 97: STICKY once the floor has armed in this process.  An image the floor
		// could not read back stays GPU-dirty; its retry after the falling edge would reach the
		// EXIT below and end an ABBA run in its base arm.  A nonzero bf_dlskip voids the run
		// either way (comment above), so the skip changes no admitted number.
		// Session 98: mode 0 reads exactly the above; KYTY_BIND_FLOOR_LATCH >= 1 reads the
		// latched op instead of the live gate (descriptors.h, BindFloorDownloadSkip).
		if (BindFloorDownloadSkip()) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorDlSkip, 1);
			Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorDlSkipKb,
			                        range.size >> 10u);
			static std::atomic<uint32_t> floor_dl_logged {0};
			if (floor_dl_logged.fetch_add(1, std::memory_order_relaxed) < 8) {
				LOGF("BindFloor: image readback abandoned, guest range does not fit the download"
				     " ring guest=0x%016" PRIx64 " bytes=%" PRIu64 " ring=%" PRIu64 " tiled=%d"
				     " extent=%ux%u bpb=%u\n",
				     range.address, range.size, download.Size(),
				     image.info.IsTiled() ? 1 : 0, image.info.extent.width,
				     image.info.extent.height, image.info.bytes_per_block);
			}
			return false;
		}
		EXIT("TextureCache: failed to map reusable download buffer\n");
	}
	download.Commit();
	if (!LibKernel::Memory::TryReadBacking(range.address, mapped, range.size)) {
		return false;
	}
	download.Flush(offset, range.size);

	DownloadImage(image, download, offset, range.size, std::move(transfer));
	vk::BufferMemoryBarrier barrier {};
	barrier.srcAccessMask = vk::AccessFlagBits::eMemoryWrite | vk::AccessFlagBits::eTransferWrite |
	                        vk::AccessFlagBits::eShaderWrite;
	barrier.dstAccessMask = vk::AccessFlagBits::eHostRead;
	barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	barrier.buffer              = download.Handle();
	barrier.offset              = offset;
	barrier.size                = range.size;
	m_scheduler.EndRendering(RenderPassEnd::Download);
	m_scheduler.Current().Handle().pipelineBarrier(vk::PipelineStageFlagBits::eAllCommands,
	                                               vk::PipelineStageFlagBits::eHost, {}, 0, nullptr,
	                                               1, &barrier, 0, nullptr);
	m_scheduler.DeferPriorityOperation([&download, range, mapped, offset] {
		download.Invalidate(offset, range.size);
		LibKernel::Memory::WriteBacking(range.address, mapped, range.size);
	});
	return true;
}

void TextureCache::InvalidateMemoryFromGPU(uint64_t address, uint64_t size) {
	if (!GuestRange {address, size}.Valid()) {
		return;
	}
	std::scoped_lock lock {m_lock};
	for (const auto id: FindImagesInRegion(address, size, true)) {
		auto& image = m_slot_images[id];
		if (image.depth_id || !image.Overlaps(address, size)) {
			continue;
		}
		TraceWatchedImage("gpu-invalidate", image, address, size);
		Common::DrawStat::Mark(Common::DrawStat::GpuWrite);
		if (image.IsGpuModified()) {
			image.ClearGpuModified();
		}
		image.MarkBufferModified();
	}
}

bool TextureCache::IsRegionGpuModified(uint64_t address, uint64_t size) {
	if (!GuestRange {address, size}.Valid()) {
		return false;
	}
	// Session 73, W7. This is one of the three parts of IsGpuCleanRange (kernel/memory.cpp:1031),
	// which the M1 witness's clean loop evaluates 15 097 times per frame on the GuestGpu thread,
	// inside the render mutex - and it takes the TrackingSpinLock every time. MayHaveImages reads
	// the atomic m_image_page_hint index without any lock and returns true for anything outside
	// that index, so "no page of this range has an image hint" means FindImagesInRegion below
	// would return an empty list and this function would return false anyway: the short-circuit is
	// the same answer, not a weaker one. Gate "dawitcp".
	Common::FrameStats::Add(Common::FrameStats::Counter::TexGpuModifiedCalls, 1);
	if (Common::Gates::Enabled(Common::Gates::Gate::DrawAheadCleanPage) &&
	    !MayHaveImages(address, size)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::TexGpuModifiedHint, 1);
		return false;
	}
	std::scoped_lock lock {m_lock};
	for (const auto id: FindImagesInRegion(address, size, false)) {
		const auto& image = m_slot_images[id];
		if (!image.depth_id && image.IsGpuModified()) {
			return true;
		}
	}
	return false;
}

bool TextureCache::MayHaveImages(uint64_t address, uint64_t size) const noexcept {
	ImagePageTable::PageRange pages {};
	if (!ImagePageTable::TryGetPageRange(address, size, pages)) {
		return true; // outside the index: leave it to the locked path
	}
	bool found = false;
	ForEachPage(address, size, [&](uint64_t page) {
		found = m_image_page_hint[page].load(std::memory_order_acquire) != 0;
		return found;
	});
	return found;
}

void TextureCache::InvalidateCpuAliases(uint64_t address, uint64_t size) {
	const auto page_begin = Common::AlignDown(address, TRACKER_PAGE_SIZE);
	const auto page_end   = Common::AlignUp(address + size, TRACKER_PAGE_SIZE);
	const auto candidates = FindImagesInRegion(address, size, true);
	Common::FrameStats::Add(Common::FrameStats::Counter::TexInvalidations, 1);
	if (candidates.empty()) {
		Common::FrameStats::Add(Common::FrameStats::Counter::TexInvalidateEmpty, 1);
	}
	for (const auto id: candidates) {
		auto owner = m_slot_images.try_get(id);
		if (owner == nullptr) {
			continue;
		}
		if (owner->Overlaps(address, size)) {
			TraceWatchedImage("cpu-invalidate", *owner, address, size);
			owner->InvalidateCpuWrite(address, size);
			UntrackImage(id);
			continue;
		}
		const auto image_begin = owner->SourceRange().address;
		const auto image_end   = owner->SourceRange().End();
		if (page_end < image_end) {
			UntrackImageHead(id);
		} else if (image_begin < page_begin) {
			UntrackImageTail(id);
		} else {
			MarkAsMaybeDirty(id, *owner);
		}
	}
}

bool TextureCache::IsMeta(uint64_t address) {
	std::scoped_lock lock {m_lock};
	const auto       found = m_surface_metas.find(address);
	return found != m_surface_metas.end() && found->second.type != MetaDataInfo::Type::PendingDcc;
}

uint32_t TextureCache::MetaClearMask(uint64_t address, uint32_t* fill_value) {
	std::scoped_lock lock {m_lock};
	const auto       found = m_surface_metas.find(address);
	if (found == m_surface_metas.end() || found->second.type == MetaDataInfo::Type::PendingDcc) {
		return 0;
	}
	if (fill_value != nullptr) {
		*fill_value = found->second.fill_value;
	}
	return found->second.clear_mask;
}

bool TextureCache::IsMetaCleared(uint64_t address, uint32_t slice, uint32_t* fill_value) {
	std::scoped_lock lock {m_lock};
	const auto       found = m_surface_metas.find(address);
	if (found == m_surface_metas.end() || found->second.type == MetaDataInfo::Type::PendingDcc ||
	    slice >= 32) {
		return false;
	}
	if (fill_value != nullptr) {
		*fill_value = found->second.fill_value;
	}
	return (found->second.clear_mask & (1u << slice)) != 0;
}

bool TextureCache::ClearMeta(uint64_t address) {
	std::scoped_lock lock {m_lock};
	const auto       found = m_surface_metas.find(address);
	if (found == m_surface_metas.end() || found->second.type == MetaDataInfo::Type::PendingDcc ||
	    found->second.type == MetaDataInfo::Type::Dcc || found->second.type == MetaDataInfo::Type::CMask) {
		// DCC and CMASK need a validated fill value and coverage. Keep the legacy operation
		// for FMask/HTile; an arbitrary write must not imply a color fast clear.
		return false;
	}
	Common::DrawStat::Mark(Common::DrawStat::Meta);
	found->second.clear_mask = UINT32_MAX;
	// Session 124, knob "skipceil" = 3 (closure census, [RC2]): a logical clear - a certain write of every candidate.
	if (Common::SkipCeil::t_mode == 3) [[unlikely]] {
		SkcCensus::G3MetaClear(*this, address);
	}
	Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 47(z), N1
	BumpMetaEpoch();
	return true;
}

void TextureCache::TrackDccFill(uint64_t address, uint64_t size, uint32_t fill_value) {
	if (!GuestRange {address, size}.Valid()) {
		EXIT("TextureCache: invalid DCC fill range\n");
	}
	// DCC fills use a repeated byte code. Require all four bytes of the detected dword to agree,
	// and mark only recognized deferred-clear encodings as logically clear.
	const auto dcc_clear_mask = [fill_value] {
		const auto code = static_cast<uint8_t>(fill_value);
		if (fill_value != static_cast<uint32_t>(code) * 0x01010101u) {
			return 0u;
		}
		switch (code) {
			case 0x00:
			case 0x20:
			case 0x40:
			case 0x80:
			case 0xc0: return UINT32_MAX;
			default: return 0u;
		}
	}();
	std::scoped_lock lock {m_lock};
	// The guest dispatch still writes metadata. An unknown address remains PendingDcc until an
	// image descriptor confirms its role; never reinterpret CMask/FMask/HTile as DCC.
	const auto found = m_surface_metas.try_emplace(address).first;
	if (found->second.type == MetaDataInfo::Type::PendingDcc ||
	    found->second.type == MetaDataInfo::Type::Dcc || found->second.type == MetaDataInfo::Type::CMask) {
		found->second.clear_mask = found->second.type == MetaDataInfo::Type::CMask
		    ? (fill_value == 0 ? UINT32_MAX : 0u) : dcc_clear_mask;
		// Session 124, knob "skipceil" = 3 (closure census, [RC2]): a logical clear (PendingDcc: until the adoption).
		if (Common::SkipCeil::t_mode == 3) [[unlikely]] {
			SkcCensus::G3MetaFill(*this, address, found->second.clear_mask,
			                      found->second.type == MetaDataInfo::Type::PendingDcc);
		}
		Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 47(z), N1
		found->second.fill_value = fill_value;
		found->second.fill_size  = size;
		if (found->second.type == MetaDataInfo::Type::PendingDcc) {
			found->second.fill_seq = 0;
			m_fill_stamp_address   = address;
			m_fill_stamp_size      = size;
		}
	}
	BumpMetaEpoch(); // the try_emplace above may have inserted as well
}

void TextureCache::StampPendingDccFill() {
	std::scoped_lock lock {m_lock};
	if (m_fill_stamp_address == 0) {
		return;
	}
	if (auto found = m_surface_metas.find(m_fill_stamp_address);
	    found != m_surface_metas.end() && found->second.type == MetaDataInfo::Type::PendingDcc) {
		found->second.fill_seq =
		    m_buffer_cache.LastGpuWriteSeq(m_fill_stamp_address, m_fill_stamp_size, false);
		BumpMetaEpoch();
	}
	m_fill_stamp_address = 0;
	m_fill_stamp_size    = 0;
}

bool TextureCache::PendingDccFillStale(uint64_t address, const MetaDataInfo& meta,
                                       uint64_t image_address) {
	// A streamed texture's metadata is filled when its mips are allocated and rewritten (DMA of
	// the real metadata, or CPU) before the texture is bound: adopting that fill would clear the
	// whole image for a frame. Only a fill nothing overwrote since is still meaningful.
	static const bool stale_check = [] {
		const char* value = std::getenv("KYTY_DCC_STALE");
		return value == nullptr || value[0] != '0';
	}();
	if (!stale_check || meta.type != MetaDataInfo::Type::PendingDcc || meta.fill_seq == 0) {
		return false;
	}
	const auto last_seq    = m_buffer_cache.LastGpuWriteSeq(address, meta.fill_size, false);
	const bool cpu_written = m_buffer_cache.IsRegionCpuModified(address, meta.fill_size);
	if (last_seq <= meta.fill_seq && !cpu_written) {
		return false;
	}
	static std::atomic<uint32_t> stale_count = 0;
	static const bool dcc_trace_stale = Common::EnvFlagOn("KYTY_DCC_TRACE");
	if (dcc_trace_stale || stale_count++ < 32) {
		LOGF("TextureCache: stale pending DCC fill ignored image=0x%016" PRIx64
		     " dcc=0x%016" PRIx64 " fill=0x%08x size=0x%" PRIx64 " seq=%" PRIu64 " last=%" PRIu64
		     " cpu=%d\n",
		     image_address, address, meta.fill_value, meta.fill_size, meta.fill_seq, last_seq,
		     cpu_written ? 1 : 0);
	}
	return true;
}

ImageId TextureCache::FindDccSurfaceImage(uint64_t data_address, uint64_t metadata_address) {
	if (data_address == 0 || metadata_address == 0) {
		return {};
	}
	ImageId  owner {};
	ImageId  candidate {};
	uint32_t candidates = 0;
	{
		std::scoped_lock lock {m_lock};
		for (const auto id: FindImagesInRegion(data_address, 1, false)) {
			const auto* image = m_slot_images.try_get(id);
			if (image == nullptr || !image->registered || image->info.data.Empty() ||
			    image->info.IsDepth() || image->depth_id ||
			    image->info.data.address != data_address) {
				continue;
			}
			if (image->info.metadata.kind == ImageMetadataKind::Dcc) {
				if (image->info.metadata.range.address == metadata_address) {
					owner = id;
					break;
				}
				continue;
			}
			if (image->info.metadata.kind == ImageMetadataKind::None) {
				candidate = id;
				candidates++;
			}
		}
	}
	if (owner) {
		return owner;
	}
	if (candidates == 1 && AdoptPendingDccForTexture(candidate, metadata_address)) {
		return candidate;
	}
	return {};
}

bool TextureCache::AdoptPendingDccForTexture(ImageId id, uint64_t metadata_address) {
	std::scoped_lock lock {m_lock};
	auto*            image = m_slot_images.try_get(id);
	if (image == nullptr || !image->registered || image->info.data.Empty() ||
	    image->info.IsDepth() || image->depth_id || metadata_address == 0) {
		return false;
	}
	if (image->info.metadata.kind == ImageMetadataKind::Dcc) {
		return image->info.metadata.range.address == metadata_address;
	}
	if (image->info.metadata.kind != ImageMetadataKind::None) {
		return false;
	}
	const auto found = m_surface_metas.find(metadata_address);
	if (found == m_surface_metas.end() || found->second.type != MetaDataInfo::Type::PendingDcc) {
		// Only a fill observed through TrackDccFill proves the address is DCC metadata;
		// never classify an untouched address from a T# alone.
		return false;
	}
	if (PendingDccFillStale(metadata_address, found->second, image->info.data.address)) {
		Common::DrawStat::Mark(Common::DrawStat::Meta);
		m_surface_metas.erase(found);
		BumpMetaEpoch();
		return false;
	}
	Common::DrawStat::Mark(Common::DrawStat::Meta);
	BumpMetaEpoch();
	found->second.type                 = MetaDataInfo::Type::Dcc;
	image->info.metadata.kind          = ImageMetadataKind::Dcc;
	image->info.metadata.range.address = metadata_address;
	// Session 124, knob "skipceil" = 3 (closure census, [RC2], ROADMAP s122 item 44(v)): the PendingDcc clear applies now,
	// with the cleaner remembered at the fill.
	if (Common::SkipCeil::t_mode == 3 && found->second.clear_mask != 0) [[unlikely]] {
		SkcCensus::G3MetaAdopt(*image, metadata_address);
	} else if (found->second.clear_mask != 0) {
		Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 47(z), N1
	}
	static std::atomic<uint32_t> log_count = 0;
	static const bool dcc_trace = Common::EnvFlagOn("KYTY_DCC_TRACE");
	if (dcc_trace || log_count++ < 32) {
		LOGF("TextureCache: adopted pending DCC fill for shader binding image=0x%016" PRIx64
		     " dcc=0x%016" PRIx64 " fill=0x%08x size=0x%" PRIx64 " clear_mask=0x%08x\n",
		     image->info.data.address, metadata_address, found->second.fill_value,
		     found->second.fill_size, found->second.clear_mask);
	}
	return true;
}

bool TextureCache::TouchMeta(uint64_t address, uint32_t slice, bool is_clear) {
	std::scoped_lock lock {m_lock};
	const auto       found = m_surface_metas.find(address);
	if (found == m_surface_metas.end() || found->second.type == MetaDataInfo::Type::PendingDcc ||
	    slice >= 32) {
		return false;
	}
	Common::DrawStat::Mark(Common::DrawStat::Meta);
	if (is_clear) {
		found->second.clear_mask |= 1u << slice;
	} else {
		found->second.clear_mask &= ~(1u << slice);
	}
	BumpMetaEpoch();
	return true;
}

void TextureCache::UnmapMemory(uint64_t address, uint64_t size) {
	if (!GuestRange {address, size}.Valid()) {
		EXIT("TextureCache: invalid unmap range\n");
	}
	std::scoped_lock lock {m_lock};
	const auto       end = address + size;
	for (auto metadata = m_surface_metas.lower_bound(address);
	     metadata != m_surface_metas.end() && metadata->first < end;) {
		metadata = m_surface_metas.erase(metadata);
		BumpMetaEpoch();
	}
	auto images = FindImagesInRegion(address, size, false);
	for (const auto id: images) {
		auto owner = m_slot_images.try_get(id);
		if (owner == nullptr) {
			continue;
		}
		FreeImage(id, __func__, __LINE__);
	}
}

void TextureCache::RunGarbageCollector() {
	std::scoped_lock lock {m_lock};
	// Session 97, gate "bindfloor": the GC runs outside any draw, so it takes the per-op latch
	// itself (descriptors.h).  While it is armed the LRU CLOCK stops as well as the eviction
	// (below): with the clock running, every texture the floor does not touch would be older
	// than the 16-tick age the moment the gate fell.  With the floor off this is the shipped
	// order exactly - the tick is taken first.
	// Session 98: KYTY_BIND_FLOOR_LATCH >= 1 reads without adopting (descriptors.h).
	// Session 99: observe the existing per-CALL age clock; never adopt a latch or change GC.
	static const bool gc_audit = [] {
		const auto* value = std::getenv("KYTY_BIND_FLOOR_GC_AUDIT");
		const bool on = value != nullptr && value[0] == '1' && value[1] == '\0';
		LOGF("BindFloorGcAudit: mode%u\n", on ? 1u : 0u);
		return on;
	}();
	const uint64_t audit_tick_before = gc_audit ? m_gc_tick : 0;
	const bool floor_hold = BindFloorGcHold();
	// Session 123, knob "skipceil" = 1 (MEASUREMENT ONLY, design123.md s.1.6): a skipped frame holds the GC the same way
	// (the clock stops, the non-critical passes are suspended); at critical pressure both run as before.
	const bool skc_hold   = Common::SkipCeil::GcHold();
	// The current submission's counted sticky value is a valid independent SUBSET of hold.
	// Unlike CurrentOp (stale outside operations), it expires with the submission. It does
	// NOT independently prove the base/pending parts of BindFloorGcHold.
	const bool audit_sticky = gc_audit && BindFloorGcAuditSticky();
	const bool audit_expected_hold = gc_audit && (floor_hold || audit_sticky);
	const auto audit_clock = [&](bool critical_override) {
		if (!gc_audit) return;
		using Counter = Common::FrameStats::Counter;
		const uint64_t expected_delta = audit_expected_hold && !critical_override ? 0u : 1u;
		const bool bad = (audit_sticky && !floor_hold) || m_gc_tick < audit_tick_before ||
		                 m_gc_tick - audit_tick_before != expected_delta;
		Common::FrameStats::Add(Counter::BindFloorImgGcChecks, 1);
		Common::FrameStats::Add(Counter::BindFloorImgGcHold,
		                       audit_expected_hold && !critical_override ? 1u : 0u);
		Common::FrameStats::Add(Counter::BindFloorImgGcBad, bad ? 1u : 0u);
		Common::FrameStats::Add(Counter::BindFloorImgGcCritical,
		                       audit_expected_hold && critical_override ? 1u : 0u);
	};
	uint64_t   tick       = floor_hold || skc_hold ? m_gc_tick : m_gc_tick++;
	Common::FrameStats::Add(Common::FrameStats::Counter::TexLruTouches, m_lru_touch_calls);
	Common::FrameStats::Add(Common::FrameStats::Counter::TexLruRepeats, m_lru_touch_repeats);
	m_lru_touch_calls   = 0;
	m_lru_touch_repeats = 0;
	const auto frame = GpuTimeProfiler::Frame();
	static const bool gc_progress = [] {
		const auto* value = std::getenv("KYTY_IMAGE_GC_PROGRESS");
		return value == nullptr || value[0] != '0';
	}();
	static const bool preserve_gpu = [] {
		const auto* value = std::getenv("KYTY_IMAGE_GC_PRESERVE_GPU");
		return value == nullptr || value[0] != '0';
	}();
	static const bool frame_guard = [] {
		const auto* value = std::getenv("KYTY_IMAGE_GC_FRAME_GUARD");
		return value != nullptr && value[0] == '1';
	}();
	static const bool trace = Common::EnvFlagOn("KYTY_IMAGE_GC_TRACE");
	static const uint32_t trace_from = [] {
		const auto* value = std::getenv("KYTY_IMAGE_GC_TRACE_FROM");
		return value == nullptr ? 0u : static_cast<uint32_t>(std::strtoul(value, nullptr, 10));
	}();
	if (m_graphics.CanReportMemoryUsage()) {
		m_total_used_memory = m_graphics.GetDeviceMemoryUsage();
	}
	static const bool memory_trace = Common::EnvFlagOn("KYTY_IMAGE_MEMORY_TRACE");
	static uint32_t last_memory_frame = UINT32_MAX;
	if (memory_trace && frame % 120u == 0 && frame != last_memory_frame) {
		last_memory_frame = frame;
		uint64_t bytes = 0, source_bytes = 0, gpu_bytes = 0, recent_bytes = 0;
		size_t count = 0, gpu_count = 0;
		m_slot_images.ForEach([&](ImageId, const Image& image) {
			if (!image.registered) return;
			++count;
			const auto size = image.AccountedSize();
			bytes += size;
			source_bytes += image.SourceRange().size;
			if (image.IsGpuModified()) { ++gpu_count; gpu_bytes += size; }
			if (static_cast<uint32_t>(frame - image.frame_accessed_last) < 2u) recent_bytes += size;
		});
		LOGF("ImageMemory: frame=%u images=%zu logical_mb=%" PRIu64 " source_mb=%" PRIu64
		     " gpu_images=%zu gpu_mb=%" PRIu64 " recent_mb=%" PRIu64 " usage_mb=%" PRIu64 "\n",
		     frame, count, bytes >> 20u, source_bytes >> 20u, gpu_count, gpu_bytes >> 20u,
		     recent_bytes >> 20u, m_total_used_memory >> 20u);
		m_graphics.LogMemoryBudget();
	}
	if (m_total_used_memory < m_trigger_gc_memory) {
		audit_clock(false);
		return;
	}
	// Session 123, S_live (any value of skipceil): the calls with the aggressive pass allowed.
	if (m_total_used_memory >= m_critical_gc_memory) {
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcGcCrit, 1);
	}
	// Session 97, gate "bindfloor" (MEASUREMENT ONLY): the floor removes every texture
	// resolve and with it every TouchImage, so the age pass below evicted ~1 050 LIVE textures
	// per 30-flip floor block in bf96b, and the first base flip after the gate fell re-created
	// them (921 images, 1.4 GB uploaded, 84 ms).  An ABBA arm must hand the base arm back the
	// cache it found.  While the latch is armed the NON-critical passes are suspended and the
	// clock does not advance (above); at critical pressure the clock advances and both passes
	// run exactly as before.  bf_gc_hold counts the suspended calls that would have collected
	// (usage at or above the trigger) and is 0 whenever the floor is off.
	if (floor_hold || skc_hold) {
		if (m_total_used_memory < m_critical_gc_memory) {
			// skc_gc_hold only when the hold came from skipceil alone (design123.md s.1.6).
			Common::FrameStats::Add(floor_hold ? Common::FrameStats::Counter::BindFloorGcHold
			                                   : Common::FrameStats::Counter::SkcGcHold,
			                        1);
			audit_clock(false);
			return;
		}
		tick = m_gc_tick++;
	}
	// Pressure is sampled before collection mutates accounting, not inferred from age delta.
	audit_clock(m_total_used_memory >= m_critical_gc_memory);
	const auto collect = [&](bool allow_aggressive) {
		bool           pressured  = m_total_used_memory >= m_pressure_gc_memory;
		bool           aggressive = allow_aggressive && m_total_used_memory >= m_critical_gc_memory;
		const uint64_t age       = std::min<uint64_t>(aggressive ? 160 : pressured ? 80 : 16, tick);
		size_t         deletions = aggressive ? 40 : pressured ? 20 : 10;
		std::vector<ImageId> candidates;
		candidates.reserve(deletions);
		// Deleting depth recursively deletes its stencil association, so finish LRU traversal
		// first.
		m_lru_cache.ForEachItemBelow(tick - age, [&](ImageId id) {
			candidates.push_back(id);
			return candidates.size() == deletions;
		});
		for (const auto id: candidates) {
			if (deletions == 0) {
				break;
			}
			--deletions;
			auto owner = m_slot_images.try_get(id);
			if (owner == nullptr || !owner->registered || owner->depth_id) {
				if (gc_progress && owner != nullptr && owner->registered) {
					m_lru_cache.Touch(owner->lru_id, tick);
				}
				continue;
			}
			// A fixed batch of pinned oldest images must not starve every image
			// behind it. Postpone only this GC retry, without changing the real
			// submission/frame of last use. Traversal has already completed.
			const auto retry_later = [&] {
				if (gc_progress) m_lru_cache.Touch(owner->lru_id, tick);
			};
			// GC ticks count completed GPU submissions, not frames. A dense frame can
			// exceed the LRU age before a texture is reused in the next frame. Keep that
			// working set unless critical pressure requires the aggressive pass.
			const bool recent = frame != 0 && static_cast<uint32_t>(frame - owner->frame_accessed_last) < 2u;
			const bool keep = frame_guard && !aggressive && recent;
			if (trace && frame >= trace_from && owner->info.data.size >= (1u << 20u)) {
				static uint32_t logged = 0;
				if (logged++ < 2048) {
					LOGF("ImageGc: frame=%u last_frame=%u tick=%" PRIu64 " keep=%d aggressive=%d guest=0x%016" PRIx64 " bytes=%" PRIu64 " usage=%" PRIu64 "\n",
					     frame, owner->frame_accessed_last, tick, keep ? 1 : 0, aggressive ? 1 : 0,
					     owner->info.data.address, owner->info.data.size, m_total_used_memory);
				}
			}
			if (keep) {
				// The aggressive pass must still see recent images under critical pressure.
				if (m_total_used_memory < m_critical_gc_memory) retry_later();
				continue;
			}
			if (owner->IsGpuModified()) {
				const bool safe = SafeToDownload(*owner);
				// A dirty buffer alias can prevent downloading this image. It does not
				// prove that the buffer contains the image's latest GPU writes. Keep
				// tiled GPU contents until an actual CPU/buffer invalidation supersedes them.
				if (owner->info.IsTiled() && (preserve_gpu ? owner->SafeToDownload() : safe)) {
					static const bool state_trace = Common::EnvFlagOn("KYTY_IMAGE_STATE_TRACE");
					if (state_trace && !safe) {
						LOGF("ImageGcKeepOverlap: frame=%u guest=0x%016" PRIx64 " bytes=%" PRIu64 "\n",
						     frame, owner->info.data.address, owner->info.data.size);
					}
					retry_later();
					continue;
				}
				if (safe && !pressured) {
					retry_later();
					continue;
				}
				if (safe && !DownloadImageMemory(id)) {
					retry_later();
					continue;
				}
			}
			if (audit_expected_hold) {
				// Counts GC root victims, including critical collection; recursive stencil
				// children are not counted twice. Every such cascade has a counted root.
				Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorImgGcEvict, 1);
			}
			FreeImage(id, __func__, __LINE__);
			if (m_total_used_memory < m_critical_gc_memory && aggressive) {
				deletions >>= 2;
				aggressive = false;
			}
			if (m_total_used_memory < m_pressure_gc_memory && pressured) {
				deletions >>= 1;
				pressured = false;
			}
		}
	};
	collect(false);
	if (m_total_used_memory >= m_critical_gc_memory) {
		collect(true);
	}
}

void TextureCache::ProcessDownloadImages() {
	std::scoped_lock lock {m_lock};
	for (const auto id: m_download_images) {
		const auto owner = m_slot_images.try_get(id);
		if (owner != nullptr && owner->registered && owner->IsGpuModified()) {
			(void)DownloadImageMemory(id);
		}
	}
	m_download_images.clear();
}

// ---------------------------------------------------------------------------------------------------------------------
// Session 123, knob "skipceil" = 2: the correctness census (MEASUREMENT ONLY; docs/session-123/design123.md s.3 with
// ROADMAP s122 items 28-33).  Everything below runs on the GuestGpu thread: the image labels and the buffer map have
// no lock.  A label is "live" when its frame is not older than the census epoch.

namespace {

namespace Skc = Common::SkipCeil;

struct SkcW2 {
	bool     image = false;
	ImageId  id {};
	uint64_t vaddr = 0;
	uint64_t size  = 0;
};

// Session 124, knob "skipceil" = 3: a pending node write of the operation (W1 attachments, W2 storage images and written
// buffer slots), applied with the W2 stamps after the operation's last read.
struct Skc3W {
	bool     image = false;
	uint32_t uid   = 0;
	uint32_t bl    = 0;
	uint32_t lc    = 0;
	uint32_t by    = 0;
	uint32_t yc    = 0;
	uint8_t  asp   = 0;
	uint8_t  via   = 0;
	uint64_t addr  = 0;
	uint64_t size  = 0;
};

// The census operation running now (one at a time; OpScope does not nest).
struct SkcOp {
	uint32_t             serial   = 0;
	uint64_t             ps_hash  = 0;
	bool                 dispatch = false;
	bool                 bound    = false; // a draw that reached its W2 point (bindings done): skc_x1_pass
	bool                 x1       = false; // an skc_x1_rd read
	bool                 x0_cs    = false;
	bool                 x0_keep  = false;
	bool                 ia_d     = false;
	bool                 ia_t     = false;
	std::vector<SkcW2>   w2;
	std::vector<ImageId> d_stamped; // D stamps with a known image id (W1, W2): skc_wpass at the end of the operation
	// Session 124, knob "skipceil" = 3.
	uint32_t             node = 0;     // the graph node of this operation in a marked frame, 0 = none
	bool                 dma  = false; // a stage has info.uses_dma (the epoch, s.3.3.3)
	std::vector<Skc3W>   g3w;          // pending node writes
};
thread_local SkcOp    t_skc_op;
thread_local uint32_t t_skc_serial  = 0;
thread_local uint32_t t_skc_x1_pass = UINT32_MAX;
thread_local uint32_t t_skc_frames  = 0;
// ROADMAP s122 item 35(b): the writers of frame N already counted by skc_x1_wd / skc_x1_wp in frame N + 1.
thread_local uint32_t                     t_skc_x1_frame = UINT32_MAX;
thread_local std::unordered_set<uint32_t> t_skc_x1_ops;
thread_local std::unordered_set<uint32_t> t_skc_x1_passes;

struct SkcReader {
	uint32_t stage = 0;
	uint64_t n     = 0;
	bool     selfw = false;
};
thread_local std::unordered_map<uint64_t, SkcReader> t_skc_readers;

bool SkcLive(const Image& image) noexcept {
	return image.skc_wkind != 0 && image.skc_wframe >= Skc::t_epoch;
}

bool SkcLiveDT(const Image& image) noexcept {
	return SkcLive(image) && (image.skc_wkind == Skc::KindD || image.skc_wkind == Skc::KindT);
}

// Executed operations (s.3.3): a dispatch of any frame (CS, T), a draw of a translated frame (R), an operation K.
bool SkcExecuted(uint8_t kind) noexcept {
	return kind == Skc::KindR || kind == Skc::KindK || kind == Skc::KindCS || kind == Skc::KindT;
}

// The kinds a stamp keeps (s.3.1): the writes of undone work.  Any other kind is an executed write and replaces the
// label (W1 / W3); W2 of such an operation leaves a D / T label in place (skc_w_maybe).
bool SkcKeeps(uint8_t kind) noexcept {
	return kind == Skc::KindD || kind == Skc::KindT || kind == Skc::KindK;
}

void SkcClearWriters(Image& image) noexcept {
	image.skc_wops.clear();
	image.skc_wpasses.clear();
	image.skc_wpassid = UINT32_MAX;
	image.skc_wop     = 0;
	image.skc_whash   = 0;
}

// A stamp of this frame.  D keeps the writer statistics of the frame's D draws (each draw once); every other kind
// replaces the label.  Kind 0 (a write outside every census operation) erases it.
void SkcStampImage(Image& image, uint8_t kind, const ImageId* id) {
	const uint32_t now = Skc::t_gframe;
	if (kind == Skc::KindD) {
		if (image.skc_wkind != Skc::KindD || image.skc_wframe != now) {
			SkcClearWriters(image);
		}
		if (image.skc_wop != t_skc_op.serial) {
			// Operations do not nest, so a serial never comes back once another one stamped: the list stays distinct.
			image.skc_wop = t_skc_op.serial;
			image.skc_wops.push_back(t_skc_op.serial);
		}
		image.skc_whash = t_skc_op.ps_hash;
		if (id != nullptr) {
			t_skc_op.d_stamped.push_back(*id);
		}
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcWDi, 1);
	} else {
		SkcClearWriters(image);
		if (kind == Skc::KindT) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcWT, 1);
		} else if (kind == Skc::KindK) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcWK, 1);
		}
	}
	image.skc_wkind  = kind;
	image.skc_wframe = now;
}

// k = 1: a read of an executed operation of frame N + 1 of an image written by D in frame N.
void SkcX1Image(Image& image) {
	Common::FrameStats::Add(Common::FrameStats::Counter::SkcX1Rd, 1);
	t_skc_op.x1 = true;
	if (image.skc_seen != Skc::t_gframe) {
		image.skc_seen = Skc::t_gframe;
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcX1Img, 1);
		// ROADMAP s122 item 35(b): distinct writers of frame N, each once in this frame N + 1 (not writer x image pairs).
		if (t_skc_x1_frame != Skc::t_gframe) {
			t_skc_x1_frame = Skc::t_gframe;
			t_skc_x1_ops.clear();
			t_skc_x1_passes.clear();
		}
		uint64_t wd = 0;
		uint64_t wp = 0;
		for (const auto serial: image.skc_wops) {
			wd += t_skc_x1_ops.insert(serial).second ? 1u : 0u;
		}
		for (const auto pass: image.skc_wpasses) {
			wp += t_skc_x1_passes.insert(pass).second ? 1u : 0u;
		}
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcX1Wd, wd);
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcX1Wp, wp);
	}
}

} // namespace

// =====================================================================================================================
// Session 124, knob "skipceil" = 3: the closure census (MEASUREMENT ONLY; docs/session-124/design124.md rev 2 with
// ROADMAP s122 items 43 and 44).  Every marked GuestGpu frame N owns a graph: its nodes are the operations of N (D, K,
// CS, M) and the transfer nodes T of its lazy writes [RC1]; an edge is a read by a node of N of a key a node of N wrote;
// a seed is an observable read (cpu, cp, gds, next, flip; poll at the finalization).  The need of a node is a 7-bit mask
// over the policies L, b, Lp, Ld, Lt, Lu, Lw (s.3.6); it propagates at the seed, depth-first by mask.  All open marked
// frames are finalized together at the end of the first unmarked frame after them (s.3.8): after it no key has a writer
// of an open frame, and every key map is cleared.  GuestGpu thread only, except the pending CPU erase list (its mutex).

namespace {

namespace G3 {

namespace FS = Common::FrameStats;
using Counter = FS::Counter;

constexpr uint8_t PL   = 1;  // L: the last writer lw, global over the open marked frames [RC5(1)]
constexpr uint8_t PB   = 2;  // b: the writers since the last certain overwrite, per open frame
constexpr uint8_t PLP  = 4;  // Lp: L plus the prefetch windows
constexpr uint8_t PLD  = 8;  // Ld: L plus the uses_dma operations of unmarked frames
constexpr uint8_t PLT  = 16; // Lt: lazy writes and materializations attributed to the trigger [RC1]
constexpr uint8_t PLU  = 32; // Lu: L without the uses_dma epoch cut [RC4]
constexpr uint8_t PLW  = 64; // Lw: the cpu seed window is the 4 KiB page [RC14]
constexpr uint8_t PALL = 127;
// The policies that follow lw under the epoch cut (Lu follows lw without it, Lt follows ltw, b the lists).
constexpr uint8_t PLFAM = PL | PLP | PLD | PLW;
// skc3_lsup: need_L implies all four (s.3.6.2).
constexpr uint8_t PSUP = PLP | PLD | PLU | PLW;

enum Via : uint8_t { ViaNone = 0, ViaW1 = 1, ViaW2 = 2, ViaW3 = 3, ViaM = 4 };
enum Why : uint8_t { WhyNone = 0, WhyW1, WhyW2, WhyW3, WhyLazy, WhyClear, WhyCp, WhyCpu, WhyDl, WhyM };
enum Cause : uint8_t { CNone = 0, CCpu, CCp, CGds, CPoll, CNext, CFlip, CAux };

constexpr uint32_t MaxViewKeys = 256;         // s.3.3.1
constexpr uint32_t CalK        = 256;         // s.5.3
constexpr uint64_t PageBytes   = 4096;        // policy Lw [RC14]
constexpr uint8_t  KindX       = 7;           // the transfer node T [RC1]; Common::SkipCeil::Kind ends at KindM = 6
constexpr uint32_t ListBit     = 0x80000000u; // edge key: a b-list, not a node
constexpr uint32_t ChainLines  = 8;           // s.8.4: self-writer chains per process, and the most frequent pairs
constexpr uint64_t PairsAt     = 300;         // the finalization that prints the most frequent reader-writer pairs

struct Edge {
	uint32_t w    = 0; // the writer node serial, or a b-list index of the reader's frame (list)
	uint32_t len  = 0; // b-list: the prefix length at the read
	uint8_t  mask = 0;
	uint8_t  via  = 0; // the class of the writer's write of the key read (s.8 skc3_via_*)
	bool     list = false;
};

struct Node {
	uint8_t               kind  = 0; // Common::SkipCeil::Kind or KindX; 0 = a placeholder (skc3_bad)
	bool                  timed = false;
	bool                  empty = false;
	bool                  w2    = false;
	uint8_t               need  = 0;
	uint8_t               cause = 0; // the seed class of the first L mark
	uint8_t               via   = 0; // the write class of the first L mark
	uint64_t              w_ns  = 0;
	uint64_t              p_n   = 0;
	uint64_t              ps    = 0;
	std::vector<Edge>     in;
	std::vector<uint64_t> wkeys; // image keys a D node wrote (P2)
};

// A b-list: the writers of one key in one open frame since its last certain overwrite, in write order.  An edge holds a
// prefix; `marked` is the prefix already marked with b, so every writer is marked once.
struct BList {
	std::vector<uint32_t> w;
	uint32_t              marked = 0;
};

struct Frame {
	uint32_t                               frame = 0;
	uint32_t                               base  = 0;
	bool                                   poll  = false;
	std::vector<Node>                      nodes;
	std::vector<BList>                     lists;
	std::unordered_map<uint64_t, uint32_t> emap; // (reader, writer or list) -> index in reader.in
	uint64_t                               wr    = 0;
	uint64_t                               gc_ns = 0;
	uint64_t                               gc_pn = 0;
	uint64_t                               gc_n  = 0;
	uint64_t                               fr_ns = 0;
	uint64_t                               fr_pn = 0;
	std::vector<uint32_t>                  p1;
	std::vector<uint32_t>                  p2;
	std::map<std::tuple<uint64_t, uint64_t, uint32_t>, std::pair<uint64_t, uint32_t>> chains;
};

struct BRef {
	uint32_t frame = 0;
	uint32_t list  = 0;
};

struct KState {
	uint32_t          lw      = 0;
	uint32_t          ltw     = 0;
	uint32_t          ep      = 0;
	uint8_t           lw_via  = 0;
	uint8_t           ltw_via = 0;
	uint8_t           why     = 0;
	std::vector<BRef> bl;
};

struct Seg {
	uint64_t end = 0;
	KState   st;
};

struct Item {
	uint32_t id   = 0;
	uint32_t len  = 0;
	uint8_t  bits = 0;
	uint8_t  via  = 0;
	bool     list = false;
	Frame*   f    = nullptr;
};

struct State {
	std::vector<std::unique_ptr<Frame>>   open;
	Frame*                                cur = nullptr; // the record of the running marked frame
	std::unordered_map<uint64_t, KState>  img;
	std::map<uint64_t, Seg>               buf;
	std::map<uint64_t, Seg>               gds;
	uint32_t                              epoch = 1;
	std::vector<std::pair<uint64_t, uint64_t>> wr_cur;  // node writes of buffers with ep == epoch (Ld)
	std::vector<std::pair<uint64_t, uint64_t>> wr_next; // ... with ep == epoch + 1 (the running uses_dma operation)
	std::unordered_map<uint64_t, uint32_t> clr;         // metadata address -> its cleaner, every type [RC2], item 47(v)
	uint32_t                              uid    = 0;
	uint64_t                              finals = 0;
	bool                                  logged = false;
	std::map<std::tuple<uint64_t, uint64_t, uint32_t>, std::pair<uint64_t, uint8_t>> pairs;
	std::set<std::tuple<uint64_t, uint64_t, uint32_t>>                                self_seen;
	uint32_t                              self_lines = 0;
	std::array<uint64_t, 8>               lazy_n {};
	std::vector<Item>                     stack;
};

State& S() {
	static State s;
	return s;
}

thread_local uint8_t  t_lazy  = 0; // SkcCensus::LazySite of the innermost lazy scope
thread_local bool     t_dwin  = false;
thread_local uint64_t t_dw_t0 = 0;
thread_local uint64_t t_dw_p  = 0;
thread_local uint64_t t_dw_n  = 0;
// ROADMAP s122 item 47(e): the subresources of the innermost SkcCensus::SubScope.
thread_local bool           t_sub_on = false;
thread_local SkcCensus::Sub t_sub {};

std::mutex                                            g_pend_mutex;
std::vector<std::tuple<uint64_t, uint64_t, uint64_t>> g_pend; // id, begin, end
std::atomic<uint32_t>                                 g_pend_n {0};
uint64_t                                              g_pend_id = 0;

uint64_t End(uint64_t a, uint64_t s) noexcept {
	return s > UINT64_MAX - a ? UINT64_MAX : a + s;
}

void Bad() {
	FS::Add(Counter::Skc3Bad, 1);
}

bool PendHit(uint64_t b, uint64_t e) {
	if (g_pend_n.load(std::memory_order_acquire) == 0) {
		return false;
	}
	std::scoped_lock lock {g_pend_mutex};
	for (const auto& [id, pb, pe]: g_pend) {
		if (pb < e && b < pe) {
			return true;
		}
	}
	return false;
}

Frame* FrameOf(uint32_t s) {
	if (s == 0) {
		return nullptr;
	}
	for (auto& f: S().open) {
		if (s >= f->base && s - f->base < f->nodes.size()) {
			return f.get();
		}
	}
	return nullptr;
}

Frame* FrameNo(uint32_t frame) {
	for (auto& f: S().open) {
		if (f->frame == frame) {
			return f.get();
		}
	}
	return nullptr;
}

Node* NodeOf(uint32_t s) {
	Frame* f = FrameOf(s);
	return f != nullptr ? &f->nodes[s - f->base] : nullptr;
}

uint32_t NextSerial() {
	uint32_t s = ++t_skc_serial;
	if (s == 0) {
		s = ++t_skc_serial;
	}
	return s;
}

// A node of the running marked frame; the serials of one frame are contiguous (every serial the frame allocates is a
// node), so the node is nodes[serial - base].
uint32_t NewNode(uint32_t serial, uint8_t kind) {
	Frame* f = S().cur;
	if (f == nullptr || serial == 0) {
		return 0;
	}
	if (f->nodes.empty()) {
		f->base = serial;
	}
	if (serial < f->base || serial - f->base < f->nodes.size()) {
		Bad();
		return 0;
	}
	while (serial - f->base > f->nodes.size()) {
		f->nodes.emplace_back();
		Bad();
	}
	f->nodes.emplace_back();
	f->nodes.back().kind = kind;
	return serial;
}

// The depth-first mark of the items on S().stack; a node continues while an item adds bits to it (s.3.6.2).
void Run(uint8_t cause) {
	auto& st = S().stack;
	while (!st.empty()) {
		const Item it = st.back();
		st.pop_back();
		if (it.list) {
			if (it.f == nullptr || it.id >= it.f->lists.size() || it.len > it.f->lists[it.id].w.size()) {
				Bad(); // a b-list edge off its frame or a prefix longer than its list
				continue;
			}
			auto& l = it.f->lists[it.id];
			for (uint32_t i = l.marked; i < it.len; i++) {
				st.push_back({l.w[i], 0, PB, ViaNone, false, nullptr});
			}
			l.marked = std::max(l.marked, it.len);
			continue;
		}
		Frame* f = FrameOf(it.id);
		if (f == nullptr) {
			Bad(); // an edge or a key on a released node
			continue;
		}
		Node&      nd = f->nodes[it.id - f->base];
		const auto nb = static_cast<uint8_t>(it.bits & ~nd.need);
		if (nb == 0) {
			continue;
		}
		if ((nb & PL) != 0) {
			nd.cause = cause;
			nd.via   = it.via;
		}
		nd.need = static_cast<uint8_t>(nd.need | nb);
		for (const auto& e: nd.in) {
			const auto eb = static_cast<uint8_t>(nb & e.mask);
			if (eb != 0) {
				st.push_back({e.w, e.len, eb, e.via, e.list, f});
			}
		}
	}
}

void Mark(uint32_t id, uint32_t len, uint8_t bits, uint8_t via, bool list, Frame* f, uint8_t cause) {
	auto& st = S().stack;
	st.clear();
	st.push_back({id, len, bits, via, list, f});
	Run(cause);
}

// An edge of reader r (a node of the running frame); a reader that is already needed passes its bits on at once.
void AddEdge(uint32_t r, uint32_t w, uint8_t mask, uint8_t via, bool list, uint32_t len) {
	if (mask == 0 || (!list && r == w)) {
		return;
	}
	Frame* f = FrameOf(r);
	if (f == nullptr) {
		Bad();
		return;
	}
	Node&          rn        = f->nodes[r - f->base];
	const uint64_t key       = (uint64_t {r} << 32u) | (list ? (w | ListBit) : w);
	const auto [it, inserted] = f->emap.try_emplace(key, static_cast<uint32_t>(rn.in.size()));
	if (inserted) {
		rn.in.push_back({w, len, mask, via, list});
	} else {
		auto& e = rn.in[it->second];
		if ((mask & PL) != 0 && (e.mask & PL) == 0) {
			e.via = via;
		}
		e.mask = static_cast<uint8_t>(e.mask | mask);
		e.len  = std::max(e.len, len);
	}
	const auto pass = static_cast<uint8_t>(rn.need & mask);
	if (pass != 0) {
		Mark(w, len, pass, via, list, f, rn.cause);
	}
}

// One read: an edge of `node` (and the Lt edge of the trigger, node2) or a seed of class `cause`.
struct Rd {
	bool     seed   = false;
	uint32_t node   = 0;
	uint8_t  mask   = PALL;
	uint32_t node2  = 0;
	uint8_t  mask2  = 0;
	uint8_t  cause  = CNone;
	bool     buffer = false; // a buffer key: the uses_dma epoch cuts it [RC4]
	bool     p1     = false; // P1: a read by an executed operation of an unmarked frame
	bool     found  = false; // a writer of an open frame under L (epoch equal)
	bool     xmm    = false; // a writer of another marked frame (edge mode): no edge
	uint32_t cut    = 0;     // L writers cut by the epoch
	uint32_t lwr    = 0;     // the L writer found
};

void Give(Rd& rd, Frame* f, uint32_t w, uint8_t m, uint8_t via, bool list, uint32_t len) {
	if (rd.seed) {
		const auto bits = static_cast<uint8_t>(m & rd.mask);
		if (bits != 0) {
			Mark(w, len, bits, via, list, f, rd.cause);
		}
		return;
	}
	AddEdge(rd.node, w, static_cast<uint8_t>(m & rd.mask), via, list, len);
	if (rd.node2 != 0) {
		AddEdge(rd.node2, w, static_cast<uint8_t>(m & rd.mask2), via, list, len);
	}
}

void ReadKey(Rd& rd, const KState& k) {
	auto&      s     = S();
	const bool ep_ok = !rd.buffer || k.ep == s.epoch;
	if (k.lw != 0) {
		Frame* f = FrameOf(k.lw);
		if (f == nullptr) {
			Bad(); // lw on a node of a finalized frame
		} else if (!rd.seed && f != s.cur) {
			rd.xmm = true;
		} else {
			if (ep_ok) {
				rd.found = true;
				rd.lwr   = k.lw;
			} else {
				rd.cut++;
			}
			Give(rd, f, k.lw, static_cast<uint8_t>(PLU | (ep_ok ? PLFAM : 0)), k.lw_via, false, 0);
			if (rd.p1 && ep_ok && (rd.mask & PL) != 0 && f->nodes[k.lw - f->base].kind == Common::SkipCeil::KindD) {
				FS::Add(Counter::Skc3PcN, 1);
				f->p1.push_back(k.lw);
			}
		}
	}
	if (!ep_ok) {
		return; // Lt and b are cut as well; only Lu ignores the epoch
	}
	if (k.ltw != 0) {
		Frame* f = FrameOf(k.ltw);
		if (f == nullptr) {
			Bad();
		} else if (!rd.seed && f != s.cur) {
			rd.xmm = true;
		} else {
			Give(rd, f, k.ltw, PLT, k.ltw_via, false, 0);
		}
	}
	for (const auto& b: k.bl) {
		Frame* f = FrameNo(b.frame);
		if (f == nullptr || b.list >= f->lists.size()) {
			Bad(); // a list of a finalized frame
			continue;
		}
		if (!rd.seed && f != s.cur) {
			rd.xmm = true;
			continue;
		}
		Give(rd, f, b.list, PB, ViaNone, true, static_cast<uint32_t>(f->lists[b.list].w.size()));
	}
}

// The counters of one read under L.
void Finish(const Rd& rd) {
	if (rd.xmm) {
		FS::Add(Counter::Skc3SXmm, 1);
	}
	if (rd.cut != 0 && (rd.mask & PL) != 0) {
		FS::Add(Counter::Skc3DmaCut, rd.cut);
	}
}

// ---- image keys: (uid, mip, layer, aspect) -------------------------------------------------------------------------

struct IR {
	uint32_t uid = 0;
	uint32_t bl  = 0;
	uint32_t lc  = 0;
	uint32_t by  = 0;
	uint32_t yc  = 0;
	uint8_t  asp = 0; // 1 colour, 2 depth, 4 stencil
};

uint8_t ImageAspects(const Image& image) noexcept {
	if (!image.info.IsDepth()) {
		return 1;
	}
	return static_cast<uint8_t>(2u | (image.info.HasStencil() ? 4u : 0u));
}

uint32_t Uid(Image& image) {
	if (image.skc3_uid == 0) {
		image.skc3_uid = ++S().uid;
		if (image.skc3_uid == 0) {
			image.skc3_uid = ++S().uid;
		}
	}
	return image.skc3_uid;
}

IR Clamp(Image& image, uint32_t bl, uint32_t lc, uint32_t by, uint32_t yc, uint8_t asp) {
	const uint32_t levels = std::max(image.info.resources.levels, 1u);
	const uint32_t layers = std::max(image.info.resources.layers, 1u);
	IR             r;
	r.uid = Uid(image);
	if (bl >= levels || by >= layers) {
		return r; // no keys
	}
	r.bl  = bl;
	r.lc  = std::min(lc, levels - bl);
	r.by  = by;
	r.yc  = std::min(yc, layers - by);
	r.asp = static_cast<uint8_t>(asp & ImageAspects(image));
	if (r.asp == 0) {
		r.asp = ImageAspects(image); // a view whose aspect the image has not (a depth image viewed as colour)
	}
	return r;
}

IR Whole(Image& image) {
	return Clamp(image, 0, UINT32_MAX, 0, UINT32_MAX, ImageAspects(image));
}

IR View(Image& image, const ImageViewInfo& view) {
	uint8_t asp = 0;
	asp |= static_cast<bool>(view.aspect & vk::ImageAspectFlagBits::eColor) ? 1u : 0u;
	asp |= static_cast<bool>(view.aspect & vk::ImageAspectFlagBits::eDepth) ? 2u : 0u;
	asp |= static_cast<bool>(view.aspect & vk::ImageAspectFlagBits::eStencil) ? 4u : 0u;
	return Clamp(image, view.base_level, view.level_count, view.base_layer, view.layer_count, asp);
}

// The keys of `sub` (item 47(e)): one range, or one per layer of lmask.
IR SubIR(Image& image, const SkcCensus::Sub& sub) {
	return Clamp(image, sub.bl, sub.lc, sub.by, sub.yc, sub.asp);
}

template <typename F>
void ForSub(Image& image, const SkcCensus::Sub& sub, F&& fn) {
	if (sub.lmask == 0) {
		fn(SubIR(image, sub));
		return;
	}
	for (uint32_t layer = 0; layer < 32; layer++) {
		if (((sub.lmask >> layer) & 1u) != 0) {
			fn(Clamp(image, sub.bl, sub.lc, layer, 1, sub.asp));
		}
	}
}

uint64_t Count(const IR& r) noexcept {
	return uint64_t {r.lc} * r.yc * static_cast<uint64_t>(std::popcount(r.asp));
}

uint64_t Key(uint32_t uid, uint32_t mip, uint32_t layer, uint32_t aspect) noexcept {
	return (uint64_t {uid} << 32u) | (uint64_t {mip & 0xfffu} << 20u) | (uint64_t {layer & 0x3ffffu} << 2u) | aspect;
}

template <typename F>
void ForKeys(const IR& r, F&& fn) {
	for (uint32_t a = 0; a < 3; a++) {
		if (((r.asp >> a) & 1u) == 0) {
			continue;
		}
		for (uint32_t mip = r.bl; mip < r.bl + r.lc; mip++) {
			for (uint32_t layer = r.by; layer < r.by + r.yc; layer++) {
				fn(Key(r.uid, mip, layer, a));
			}
		}
	}
}

void ReadImg(Rd& rd, const IR& r) {
	const uint64_t n = Count(r);
	if (n == 0) {
		return;
	}
	if (n > MaxViewKeys) {
		FS::Add(Counter::Skc3SubDrop, 1);
		return;
	}
	auto& img = S().img;
	if (img.empty()) {
		return;
	}
	ForKeys(r, [&](uint64_t key) {
		const auto it = img.find(key);
		if (it != img.end()) {
			ReadKey(rd, it->second);
		}
	});
}

// ---- interval keys: buffers (guest addresses) and GDS (offsets) ---------------------------------------------------------

void ReadMap(Rd& rd, std::map<uint64_t, Seg>& m, uint64_t addr, uint64_t size) {
	if (size == 0 || m.empty()) {
		return;
	}
	const uint64_t end = End(addr, size);
	auto           it  = m.upper_bound(addr);
	if (it != m.begin()) {
		const auto prev = std::prev(it);
		if (prev->second.end > addr) {
			it = prev;
		}
	}
	for (; it != m.end() && it->first < end; ++it) {
		ReadKey(rd, it->second.st);
	}
}

// Cuts the segment that straddles `at`; the tail gets copies of the b-lists, so an append to one half never reaches the
// other.
void Split(std::map<uint64_t, Seg>& m, uint64_t at) {
	auto it = m.upper_bound(at);
	if (it == m.begin()) {
		return;
	}
	const auto prev = std::prev(it);
	if (prev->first >= at || prev->second.end <= at) {
		return;
	}
	Seg tail {prev->second.end, prev->second.st};
	for (auto& b: tail.st.bl) {
		Frame* f = FrameNo(b.frame);
		if (f == nullptr || b.list >= f->lists.size()) {
			Bad();
			continue;
		}
		BList copy = f->lists[b.list];
		f->lists.push_back(std::move(copy));
		b.list = static_cast<uint32_t>(f->lists.size() - 1);
	}
	prev->second.end = at;
	m.emplace_hint(it, at, std::move(tail));
}

template <typename F>
void WriteMap(std::map<uint64_t, Seg>& m, uint64_t addr, uint64_t size, bool create, F&& fn) {
	if (size == 0 || (!create && m.empty())) {
		return;
	}
	const uint64_t end = End(addr, size);
	Split(m, addr);
	Split(m, end);
	uint64_t pos = addr;
	auto     it  = m.lower_bound(addr);
	while (pos < end) {
		if (it != m.end() && it->first == pos) {
			fn(it->second.st);
			pos = it->second.end;
			++it;
			continue;
		}
		const uint64_t gap = it != m.end() && it->first < end ? it->first : end;
		if (create) {
			const auto added = m.emplace_hint(it, pos, Seg {gap, {}});
			fn(added->second.st);
		}
		pos = gap;
	}
}

// ---- writes -----------------------------------------------------------------------------------------------------------

struct Wr {
	uint32_t w       = 0; // the writer node (0: none - closes the key under L)
	uint32_t lt      = 0; // the writer under Lt (the trigger of a lazy write; otherwise w)
	uint8_t  via     = ViaNone;
	uint8_t  why     = WhyNone;
	bool     certain = false; // a certain full overwrite (b)
	bool     lt_only = false; // the materialization of a deferred clear: a write of policy Lt only
	uint32_t ep      = 0;
	bool     hit     = false; // out: a writer of an open frame was replaced under L
};

void AppendB(KState& k, uint32_t w) {
	Frame* f = FrameOf(w);
	if (f == nullptr) {
		Bad();
		return;
	}
	for (const auto& b: k.bl) {
		if (b.frame == f->frame) {
			if (b.list >= f->lists.size()) {
				Bad();
				return;
			}
			auto& l = f->lists[b.list].w;
			if (l.empty() || l.back() != w) {
				l.push_back(w);
			}
			return;
		}
	}
	f->lists.emplace_back();
	f->lists.back().w.push_back(w);
	k.bl.push_back({f->frame, static_cast<uint32_t>(f->lists.size() - 1)});
}

void WriteKey(Wr& wr, KState& k) {
	if (k.lw != 0 && FrameOf(k.lw) != nullptr) {
		wr.hit = true;
	}
	if (wr.lt_only) {
		k.ltw     = wr.lt;
		k.ltw_via = wr.via;
		return;
	}
	k.lw      = wr.w;
	k.lw_via  = wr.via;
	k.ltw     = wr.lt;
	k.ltw_via = wr.via;
	k.why     = wr.why;
	k.ep      = wr.ep;
	if (wr.certain) {
		k.bl.clear(); // the lists of ALL open frames [RC5(1)]
	}
	if (wr.w != 0) {
		AppendB(k, wr.w);
	}
}

void WriteImg(Wr& wr, const IR& r) {
	if (Count(r) == 0) {
		return;
	}
	auto&      img    = S().img;
	const bool create = wr.lt_only ? wr.lt != 0 : wr.w != 0;
	Node*      nd     = !wr.lt_only && wr.w != 0 ? NodeOf(wr.w) : nullptr;
	if (nd != nullptr && nd->kind != Common::SkipCeil::KindD) {
		nd = nullptr;
	}
	ForKeys(r, [&](uint64_t key) {
		if (create) {
			WriteKey(wr, img[key]);
			if (nd != nullptr) {
				nd->wkeys.push_back(key);
			}
		} else if (!img.empty()) {
			const auto it = img.find(key);
			if (it != img.end()) {
				WriteKey(wr, it->second);
			}
		}
	});
}

void WriteBuf(Wr& wr, std::map<uint64_t, Seg>& m, uint64_t addr, uint64_t size, bool buffer) {
	auto&      s      = S();
	const bool create = wr.w != 0;
	WriteMap(m, addr, size, create, [&](KState& k) { WriteKey(wr, k); });
	if (create && buffer) {
		(wr.ep == s.epoch ? s.wr_cur : s.wr_next).emplace_back(addr, size);
	}
}

// The epoch a write of the running operation carries: after its shift for an operation with uses_dma (ROADMAP s122
// item 44(d)), the current one otherwise.
uint32_t EpOf() noexcept {
	return S().epoch + (t_skc_op.serial != 0 && t_skc_op.dma ? 1u : 0u);
}

void CountWrite(uint32_t w) {
	if (Frame* f = FrameOf(w); f != nullptr) {
		f->wr++;
	}
}

// ---- readers ----------------------------------------------------------------------------------------------------------

// A read of the running operation: an edge of its node in a marked frame; a "next" seed in an unmarked frame while a
// marked frame is open (s.3.5); nothing outside operations.
bool OpReader(Rd& rd) {
	if (t_skc_op.serial == 0) {
		return false;
	}
	if (t_skc_op.node != 0) {
		rd.node = t_skc_op.node;
		return true;
	}
	auto& s = S();
	if (s.cur != nullptr || s.open.empty()) {
		return false;
	}
	rd.seed  = true;
	rd.cause = CNext;
	rd.p1    = true;
	return true;
}

void CountNext(const Rd& rd) {
	if (rd.seed && rd.found && rd.cause == CNext) {
		FS::Add(Counter::Skc3SNext, 1);
	}
}

void ReadBufRange(Rd& rd, uint64_t addr, uint64_t size) {
	rd.buffer = true;
	if (size == 0) {
		return;
	}
	if (PendHit(addr, End(addr, size))) {
		FS::Add(Counter::Skc3SPend, 1);
		return;
	}
	ReadMap(rd, S().buf, addr, size);
	Finish(rd);
}

const char* LazyName(uint8_t site) {
	switch (site) {
		case SkcCensus::LazyUpload: return "upload";
		case SkcCensus::LazyP3a: return "p3a";
		case SkcCensus::LazyP3b: return "p3b";
		case SkcCensus::LazyP3c: return "p3c";
		case SkcCensus::LazyMat: return "mat";
		case SkcCensus::LazyW3r: return "w3r";
		default: return "none";
	}
}

void LazyLog(uint8_t site) {
	auto& s = S();
	if (site >= s.lazy_n.size()) {
		return;
	}
	if (s.lazy_n[site]++ == 0) {
		LOGF("Skc3Lazy: site=%s n=%" PRIu64 "\n", LazyName(site), s.lazy_n[site]);
	}
}

// A lazy write [RC1]: in a marked frame a new transfer node T is the writer (under Lt the trigger operation, or T
// outside operations) and T reads the source (under Lt the trigger does); in an unmarked frame the keys close and the
// source read is a "next" seed while a marked frame is open.
void LazyWrite(uint8_t site, const IR& dst, const IR* src_img, uint64_t src_addr, uint64_t src_size) {
	LazyLog(site);
	auto&          s    = S();
	const uint32_t trig = t_skc_op.node;
	uint32_t       t    = 0;
	if (s.cur != nullptr) {
		t = NewNode(NextSerial(), KindX);
		if (t != 0) {
			FS::Add(Counter::Skc3LazyN, 1);
			if (trig != 0) {
				FS::Add(Counter::Skc3LazyIn, 1);
			}
		}
	}
	Rd   base;
	bool reads = false;
	if (t != 0) {
		base.node = t;
		reads     = true;
		if (trig != 0) {
			base.mask  = static_cast<uint8_t>(PALL & ~PLT);
			base.node2 = trig;
			base.mask2 = PLT;
		}
	} else if (s.cur == nullptr && !s.open.empty()) {
		base.seed  = true;
		base.cause = CNext;
		reads      = true;
	}
	if (reads && src_img != nullptr) {
		Rd rd = base;
		ReadImg(rd, *src_img);
		Finish(rd);
		CountNext(rd);
	}
	if (reads && src_size != 0) {
		Rd rd = base;
		ReadBufRange(rd, src_addr, src_size);
		CountNext(rd);
	}
	Wr wr;
	wr.w       = t;
	wr.lt      = trig != 0 ? trig : t;
	wr.via     = ViaW3;
	wr.why     = WhyLazy;
	wr.certain = true;
	WriteImg(wr, dst);
	CountWrite(t);
}

// ---- entry points used by the census of session 123 ---------------------------------------------------------------------

void WindowBegin() {
	Node* nd = NodeOf(t_skc_op.node);
	if (nd == nullptr) {
		return;
	}
	nd->kind = Common::SkipCeil::KindD;
	t_dwin   = true;
	t_dw_p   = Common::SkipCeil::t_p_ns;
	t_dw_n   = Common::SkipCeil::t_p_n;
	t_dw_t0  = FS::NowNs();
}

void OpEnd(SkcOp& op) {
	if (t_dwin) {
		const uint64_t t = FS::NowNs();
		t_dwin           = false;
		if (Node* nd = NodeOf(op.node); nd != nullptr) {
			const uint64_t w = t - t_dw_t0;
			const uint64_t p = Common::SkipCeil::t_p_ns - t_dw_p;
			nd->w_ns         = w > p ? w - p : 0;
			nd->p_n          = Common::SkipCeil::t_p_n - t_dw_n;
			nd->timed        = true;
		}
	}
	const Common::SkipCeil::Skc3Pause pause;
	if (Node* nd = NodeOf(op.node); nd != nullptr) {
		nd->ps = op.ps_hash;
	}
	if (op.dma) {
		auto& s = S();
		// Ld: an operation of an unmarked frame with uses_dma seeds every buffer range with a writer of an open frame and
		// the current epoch - before its own shift.
		if (s.cur == nullptr && !s.open.empty()) {
			for (const auto& [addr, size]: s.wr_cur) {
				Rd rd;
				rd.seed   = true;
				rd.mask   = PLD;
				rd.cause  = CAux;
				rd.buffer = true;
				ReadMap(rd, s.buf, addr, size);
			}
		}
		s.epoch++;
		FS::Add(Counter::Skc3DmaEp, 1);
		s.wr_cur.swap(s.wr_next);
		s.wr_next.clear();
	}
	op.node = 0;
	op.dma  = false;
	op.g3w.clear();
}

void ApplyWrites(SkcOp& op) {
	const uint32_t w = op.node;
	for (const auto& e: op.g3w) {
		Wr wr;
		wr.w   = w;
		wr.lt  = w;
		wr.via = e.via;
		wr.why = e.via == ViaW1 ? WhyW1 : WhyW2;
		wr.ep  = EpOf();
		if (e.image) {
			WriteImg(wr, IR {e.uid, e.bl, e.lc, e.by, e.yc, e.asp});
		} else {
			WriteBuf(wr, S().buf, e.addr, e.size, true);
		}
		CountWrite(w);
		if (e.via == ViaW2) {
			if (Node* nd = NodeOf(w); nd != nullptr) {
				nd->w2 = true;
			}
		}
	}
	op.g3w.clear();
}

void OpReadBuffer(uint64_t vaddr, uint64_t size, bool written) {
	Rd rd;
	if (OpReader(rd)) {
		ReadBufRange(rd, vaddr, size);
		CountNext(rd);
	}
	if (written) {
		Skc3W e;
		e.via  = ViaW2;
		e.addr = vaddr;
		e.size = size;
		t_skc_op.g3w.push_back(e);
	}
}

// P2 (s.10, ROADMAP s122 items 44(e), 45(a)): an image that gives skc_x1_img to a read of an executed operation of the
// next, unmarked frame - each of its D writers is checked by the keys it wrote that the read covers: a key whose `why`
// is a logical clear or T is excluded (1); a key whose last writer lw is another D node D' of an open marked frame
// requires need_b of D' (2); any other key requires need_b of D (3).  A node is required at most once per writer.
void P2(Image& image, const IR& r) {
	namespace Skc = Common::SkipCeil;
	if (image.skc_wkind != Skc::KindD || image.skc_wframe < Skc::t_epoch || Skc::t_gframe - image.skc_wframe != 1 ||
	    image.skc_seen == Skc::t_gframe) {
		return;
	}
	std::vector<uint64_t> keys;
	ForKeys(r, [&](uint64_t key) { keys.push_back(key); });
	std::sort(keys.begin(), keys.end());
	auto& img = S().img;
	for (const uint32_t serial: image.skc_wops) {
		FS::Add(Counter::Skc3X1cN, 1);
		Frame* f = FrameOf(serial);
		if (f == nullptr) {
			Bad();
			continue;
		}
		const Node&           nd    = f->nodes[serial - f->base];
		bool                  inter = false;
		bool                  self  = false; // a key by (3)
		std::vector<uint32_t> ovr;           // the distinct D' of the keys by (2)
		for (const uint64_t key: nd.wkeys) {
			if (!std::binary_search(keys.begin(), keys.end(), key)) {
				continue;
			}
			inter         = true;
			const auto it = img.find(key);
			if (it == img.end()) {
				self = true;
				continue;
			}
			const KState& k = it->second;
			if (k.why == WhyClear || k.why == WhyLazy) {
				continue;
			}
			if (k.lw != 0 && k.lw != serial) {
				const Node* o = NodeOf(k.lw);
				if (o != nullptr && o->kind == Common::SkipCeil::KindD) {
					if (std::find(ovr.begin(), ovr.end(), k.lw) == ovr.end()) {
						ovr.push_back(k.lw);
					}
					continue;
				}
			}
			self = true;
		}
		if (!inter) {
			FS::Add(Counter::Skc3X1cSub, 1);
			continue;
		}
		if (!self && ovr.empty()) {
			FS::Add(Counter::Skc3X1cClr, 1);
			continue;
		}
		if (!self) {
			FS::Add(Counter::Skc3X1cOvr, 1);
		} else {
			f->p2.push_back(serial); // must have need_b at the finalization
			FS::Add(Counter::Skc3X1cChk, 1);
		}
		for (const uint32_t o: ovr) {
			FrameOf(o)->p2.push_back(o); // D' is open: NodeOf found it
			FS::Add(Counter::Skc3X1cChk, 1);
		}
	}
}

void Chain(uint32_t writer, uint64_t reader_hash, uint32_t stage) {
	if (writer == 0 || reader_hash == 0) {
		return;
	}
	Frame* f = FrameOf(writer);
	if (f == nullptr) {
		return;
	}
	const Node& nd = f->nodes[writer - f->base];
	if (nd.kind != Common::SkipCeil::KindD) {
		return;
	}
	auto& c = f->chains[{reader_hash, nd.ps, stage}];
	c.first++;
	c.second = writer;
}

void ReadRange(Image& image, const IR& r) {
	Rd rd;
	if (!OpReader(rd)) {
		return;
	}
	if (rd.seed && Count(r) <= MaxViewKeys) {
		P2(image, r);
	}
	ReadImg(rd, r);
	Finish(rd);
	CountNext(rd);
}

void Upload(Image& image, uint32_t first_level, uint32_t level_count) {
	const auto range = image.SourceRange();
	const IR   dst   = Clamp(image, first_level, level_count, 0, UINT32_MAX, ImageAspects(image));
	LazyWrite(SkcCensus::LazyUpload, dst, nullptr, range.address, range.size);
}

void StampW3(Image& image) {
	if (t_lazy == SkcCensus::LazyMat) {
		// ROADMAP s122 items 44(b), 47(b): a materialization of a deferred clear, on every path (a target acquisition
		// included), is no write event; under Lt a write of the trigger (none outside operations) - of the materialized
		// subresources when the site knows them.
		LazyLog(SkcCensus::LazyMat);
		Wr wr;
		wr.lt_only = true;
		wr.lt      = t_skc_op.node;
		wr.via     = ViaW3;
		if (t_sub_on) {
			ForSub(image, t_sub, [&wr](const IR& r) { WriteImg(wr, r); });
		} else {
			WriteImg(wr, Whole(image));
		}
		return;
	}
	if (Common::SkipCeil::t_acq) {
		return; // a target acquisition is no certain write: W1 covers it (as in session 123)
	}
	switch (t_lazy) {
		case SkcCensus::LazyUpload:
		case SkcCensus::LazyP3a:
		case SkcCensus::LazyP3b:
		case SkcCensus::LazyP3c: return; // the explicit event of the scope is the write
		case SkcCensus::LazyW3r:
			if (t_sub_on) {
				ForSub(image, t_sub, [](const IR& r) { LazyWrite(SkcCensus::LazyW3r, r, nullptr, 0, 0); });
			} else {
				LazyWrite(SkcCensus::LazyW3r, Whole(image), nullptr, 0, 0);
			}
			return;
		default: break;
	}
	if (!t_sub_on) {
		// ROADMAP s122 item 47(e): a W3 without a known subresource closes the keys of its image without a writer ("up":
		// a writer on keys it did not write would be "down").
		FS::Add(Counter::Skc3W3Nw, 1);
		Wr wr;
		wr.via     = ViaW3;
		wr.why     = WhyW3;
		wr.certain = true;
		WriteImg(wr, Whole(image));
		return;
	}
	const uint32_t w = t_skc_op.node;
	Wr             wr;
	wr.w       = w;
	wr.lt      = w;
	wr.via     = ViaW3;
	wr.why     = WhyW3;
	wr.certain = true;
	ForSub(image, t_sub, [&wr](const IR& r) { WriteImg(wr, r); });
	CountWrite(w);
}

// ---- logical clears [RC2] ---------------------------------------------------------------------------------------------

void CloseImage(Image& image, uint32_t mask, uint32_t w, bool& hit) {
	Wr wr;
	wr.w       = w;
	wr.lt      = w;
	wr.via     = ViaW3;
	wr.why     = WhyClear;
	wr.certain = true;
	const IR r = Whole(image);
	if (mask == UINT32_MAX) {
		WriteImg(wr, r);
	} else {
		for (uint32_t layer = 0; layer < std::min(r.yc, 32u); layer++) {
			if (((mask >> layer) & 1u) != 0) {
				IR one = r;
				one.by = layer;
				one.yc = 1;
				WriteImg(wr, one);
			}
		}
	}
	hit = hit || wr.hit;
	CountWrite(w);
}

// `each` visits every image of the cache (SkcCensus, a friend of TextureCache, supplies it).
template <typename Each>
void CloseCandidates(Each&& each, uint64_t address, uint32_t mask) {
	FS::Add(Counter::Skc3MclrN, 1);
	if (address == 0) {
		return;
	}
	const uint32_t w   = t_skc_op.node;
	bool           hit = false;
	each([&](Image& image) {
		if (image.registered && image.info.metadata.range.address == address) {
			CloseImage(image, mask, w, hit);
		}
	});
	if (hit) {
		FS::Add(Counter::Skc3Mclr, 1);
	}
}

// ROADMAP s122 item 47(v): an image linked to a metadata surface whose clear mask is nonzero after the clear event - the
// cleaner remembered at the address closes it; a cleaner of a finalized frame or an unmarked frame, none remembered, or a
// seeded clear state (HTILE at its insertion, no clear event) close it without a writer ("up").
bool LateLink(Image& image, uint64_t address, uint32_t mask, bool seeded) {
	auto&    s = S();
	uint32_t w = 0;
	if (seeded) {
		s.clr.erase(address);
	} else if (const auto it = s.clr.find(address); it != s.clr.end()) {
		w = FrameOf(it->second) != nullptr ? it->second : 0;
	}
	FS::Add(w != 0 ? Counter::Skc3ClLate : Counter::Skc3ClLateNw, 1);
	bool hit = false;
	CloseImage(image, mask, w, hit);
	return hit;
}

// ---- finalization ---------------------------------------------------------------------------------------------------------

const char* StageName(uint32_t stage) {
	return stage == 1 ? "ps" : stage == 2 ? "cs" : "vs";
}

void Chains(Frame& f) {
	auto& s = S();
	for (const auto& [key, v]: f.chains) {
		const uint32_t serial = v.second;
		if (serial < f.base || serial - f.base >= f.nodes.size()) {
			continue;
		}
		const Node&   nd   = f.nodes[serial - f.base];
		const auto    need = static_cast<uint8_t>(((nd.need & PL) != 0 ? 1u : 0u) | ((nd.need & PB) != 0 ? 2u : 0u));
		auto&         p    = s.pairs[key];
		p.first += v.first;
		p.second = need;
		const auto& [reader, writer, stage] = key;
		if (reader == writer && s.self_lines < ChainLines && s.self_seen.insert(key).second) {
			s.self_lines++;
			LOGF("Skc3Chain: reader=0x%016" PRIx64 " stage=%s writer_ps=0x%016" PRIx64 " need_l=%u need_b=%u k=1\n",
			     reader, StageName(stage), writer, need & 1u, (need >> 1u) & 1u);
		}
	}
	if (s.finals == PairsAt && !s.pairs.empty()) {
		std::vector<std::pair<std::tuple<uint64_t, uint64_t, uint32_t>, std::pair<uint64_t, uint8_t>>> rows(
		    s.pairs.begin(), s.pairs.end());
		std::sort(rows.begin(), rows.end(), [](const auto& a, const auto& b) { return a.second.first > b.second.first; });
		for (size_t i = 0; i < rows.size() && i < ChainLines; i++) {
			const auto& [reader, writer, stage] = rows[i].first;
			const auto need                     = rows[i].second.second;
			LOGF("Skc3Chain: reader=0x%016" PRIx64 " stage=%s writer_ps=0x%016" PRIx64 " need_l=%u need_b=%u k=1 n=%" PRIu64
			     "\n",
			     reader, StageName(stage), writer, need & 1u, (need >> 1u) & 1u, rows[i].second.first);
		}
	}
}

void Finalize(Frame& f) {
	auto& s = S();
	s.finals++;
	FS::Add(Counter::Skc3F, 1);
	if (f.poll) {
		FS::Add(Counter::Skc3Pollf, 1);
	}
	const auto node_at = [&f](uint32_t serial) -> const Node* {
		return serial >= f.base && serial - f.base < f.nodes.size() ? &f.nodes[serial - f.base] : nullptr;
	};
	// P1 and P2 check the propagation, so they come before the poll marks.
	uint64_t pc_bad  = 0;
	uint64_t x1c_bad = 0;
	for (const uint32_t w: f.p1) {
		const Node* nd = node_at(w);
		pc_bad += nd == nullptr || (nd->need & PL) == 0 ? 1u : 0u;
	}
	for (const uint32_t w: f.p2) {
		const Node* nd = node_at(w);
		x1c_bad += nd == nullptr || (nd->need & PB) == 0 ? 1u : 0u;
	}
	Chains(f);
	uint64_t nodes = 0, ed = 0, d = 0, d_empty = 0, need_l = 0, free_l = 0, free_l_empty = 0, need_b = 0, free_b = 0;
	uint64_t lp = 0, ld = 0, lu = 0, lw = 0, lt = 0, nocause = 0, lnb = 0, lsup = 0, w2d = 0, orphan = 0, bad = 0;
	uint64_t wd = 0, pd = 0, wfl = 0, pfl = 0, wfb = 0, pfb = 0;
	std::array<uint64_t, 8> cl {};
	std::array<uint64_t, 5> via {};
	for (auto& nd: f.nodes) {
		if (nd.kind == 0) {
			continue;
		}
		nodes++;
		ed += nd.in.size();
		if (nd.kind == Common::SkipCeil::KindD) {
			// The poll rule (s.3.5, contract of ROADMAP s122 item 40(v)(5)): every D of a poll frame, every policy.
			if (f.poll) {
				if ((nd.need & PL) == 0) {
					nd.cause = CPoll;
					nd.via   = ViaNone;
				}
				nd.need = PALL;
			}
			d++;
			d_empty += nd.empty ? 1u : 0u;
			w2d += nd.w2 ? 1u : 0u;
			if (!nd.timed) {
				orphan++;
			} else {
				wd += nd.w_ns;
				pd += nd.p_n;
			}
			if ((nd.need & PL) != 0) {
				need_l++;
				if (nd.cause >= CCpu && nd.cause <= CFlip) {
					cl[nd.cause]++;
					if (nd.cause != CPoll) {
						if (nd.via >= ViaW1 && nd.via <= ViaM) {
							via[nd.via]++;
						} else {
							bad++;
						}
					}
				} else {
					nocause++;
				}
			} else {
				free_l++;
				free_l_empty += nd.empty ? 1u : 0u;
				if (nd.timed) {
					wfl += nd.w_ns;
					pfl += nd.p_n;
				}
			}
			if ((nd.need & PB) != 0) {
				need_b++;
			} else {
				free_b++;
				if (nd.timed) {
					wfb += nd.w_ns;
					pfb += nd.p_n;
				}
			}
			lp += (nd.need & PLP) != 0 ? 1u : 0u;
			ld += (nd.need & PLD) != 0 ? 1u : 0u;
			lu += (nd.need & PLU) != 0 ? 1u : 0u;
			lw += (nd.need & PLW) != 0 ? 1u : 0u;
			lt += (nd.need & PLT) != 0 ? 1u : 0u;
		}
		if ((nd.need & PL) != 0 && (nd.need & PB) == 0) {
			lnb++;
		}
		if ((nd.need & PL) != 0 && (nd.need & PSUP) != PSUP) {
			lsup++;
		}
	}
	FS::Add(Counter::Skc3D, d);
	FS::Add(Counter::Skc3DEmpty, d_empty);
	FS::Add(Counter::Skc3Nodes, nodes);
	FS::Add(Counter::Skc3Wr, f.wr);
	FS::Add(Counter::Skc3Ed, ed);
	FS::Add(Counter::Skc3NeedL, need_l);
	FS::Add(Counter::Skc3FreeL, free_l);
	FS::Add(Counter::Skc3FreeLEmpty, free_l_empty);
	FS::Add(Counter::Skc3NeedB, need_b);
	FS::Add(Counter::Skc3FreeB, free_b);
	FS::Add(Counter::Skc3NeedLp, lp);
	FS::Add(Counter::Skc3NeedLd, ld);
	FS::Add(Counter::Skc3NeedLu, lu);
	FS::Add(Counter::Skc3NeedLw, lw);
	FS::Add(Counter::Skc3NeedLt, lt);
	FS::Add(Counter::Skc3ClCpu, cl[CCpu]);
	FS::Add(Counter::Skc3ClCp, cl[CCp]);
	FS::Add(Counter::Skc3ClGds, cl[CGds]);
	FS::Add(Counter::Skc3ClPoll, cl[CPoll]);
	FS::Add(Counter::Skc3ClNext, cl[CNext]);
	FS::Add(Counter::Skc3ClFlip, cl[CFlip]);
	FS::Add(Counter::Skc3ViaW1, via[ViaW1]);
	FS::Add(Counter::Skc3ViaW2, via[ViaW2]);
	FS::Add(Counter::Skc3ViaW3, via[ViaW3]);
	FS::Add(Counter::Skc3ViaM, via[ViaM]);
	FS::Add(Counter::Skc3Nocause, nocause);
	FS::Add(Counter::Skc3Lnb, lnb);
	FS::Add(Counter::Skc3Lsup, lsup);
	FS::Add(Counter::Skc3W2d, w2d);
	FS::Add(Counter::Skc3PcBad, pc_bad);
	FS::Add(Counter::Skc3X1cBad, x1c_bad);
	FS::Add(Counter::Skc3Orphan, orphan);
	FS::Add(Counter::Skc3Bad, bad);
	FS::Add(Counter::Skc3WdNs, wd);
	FS::Add(Counter::Skc3PdN, pd);
	FS::Add(Counter::Skc3WfreeLNs, wfl);
	FS::Add(Counter::Skc3PfreeLN, pfl);
	FS::Add(Counter::Skc3WfreeBNs, wfb);
	FS::Add(Counter::Skc3PfreeBN, pfb);
	FS::Add(Counter::Skc3GcNs, f.gc_ns);
	FS::Add(Counter::Skc3GcPn, f.gc_pn);
	FS::Add(Counter::Skc3GcN, f.gc_n);
	FS::Add(Counter::Skc3FrNs, f.fr_ns);
	FS::Add(Counter::Skc3FrPn, f.fr_pn);
}

void Reset() {
	auto& s = S();
	s.open.clear();
	s.cur = nullptr;
	s.img.clear();
	s.buf.clear();
	s.gds.clear();
	s.wr_cur.clear();
	s.wr_next.clear();
	s.clr.clear(); // N11: the cleaners of finalized frames are "none" either way
}

} // namespace G3

} // namespace

uint8_t SkcCensus::LazyEnter(uint8_t site) noexcept {
	const uint8_t prev = G3::t_lazy;
	G3::t_lazy         = site;
	return prev;
}

void SkcCensus::LazyLeave(uint8_t prev) noexcept {
	G3::t_lazy = prev;
}

bool SkcCensus::SubEnter(const Sub& sub, Sub& prev) noexcept {
	const bool on = G3::t_sub_on;
	prev          = G3::t_sub;
	G3::t_sub     = sub;
	G3::t_sub_on  = true;
	return on;
}

void SkcCensus::SubLeave(bool prev_on, const Sub& prev) noexcept {
	G3::t_sub    = prev;
	G3::t_sub_on = prev_on;
}

void SkcCensus::GcDone(uint64_t t0, uint64_t p0, uint64_t n0) noexcept {
	G3::Frame* f = G3::S().cur;
	if (f == nullptr) {
		return;
	}
	const uint64_t w = Common::FrameStats::NowNs() - t0;
	const uint64_t p = Common::SkipCeil::t_p_ns - p0;
	f->gc_ns += w > p ? w - p : 0;
	f->gc_pn += Common::SkipCeil::t_p_n - n0;
	f->gc_n++;
}

void SkcCensus::ProcDone(uint32_t frame, uint64_t t0, uint64_t p0, uint64_t n0) noexcept {
	G3::Frame* f = G3::FrameNo(frame);
	if (f == nullptr) {
		return;
	}
	const uint64_t w = Common::FrameStats::NowNs() - t0;
	const uint64_t p = Common::SkipCeil::t_p_ns - p0;
	f->fr_ns += w > p ? w - p : 0;
	f->fr_pn += Common::SkipCeil::t_p_n - n0;
}

void SkcCensus::G3FrameEnd() {
	namespace FS = Common::FrameStats;
	auto& s = G3::S();
	// s.5.3: K empty pauses between two clock reads, outside every window.
	const uint64_t c0 = FS::NowNs();
	for (uint32_t i = 0; i < G3::CalK; i++) {
		const Common::SkipCeil::Skc3Pause pause;
	}
	const uint64_t c1 = FS::NowNs();
	FS::Add(FS::Counter::Skc3CalNs, c1 - c0);
	FS::Add(FS::Counter::Skc3CalN, G3::CalK);
	if (Common::SkipCeil::t_skip) {
		// [RC5(2)]: the poll bit of this marked frame goes to its record, read only there at the finalization.
		if (s.cur != nullptr) {
			s.cur->poll = Common::SkipCeil::t_lod_ftouch;
		}
		s.cur = nullptr;
		return;
	}
	s.cur = nullptr;
	if (s.open.empty()) {
		return;
	}
	const Common::SkipCeil::Skc3Pause pause;
	if (s.open.size() >= 2) {
		FS::Add(FS::Counter::Skc3Open2, 1);
	}
	for (auto& f: s.open) {
		G3::Finalize(*f);
	}
	G3::Reset(); // no key has a writer of an open frame any more
}

void SkcCensus::G3Latch(bool edge) {
	auto& s = G3::S();
	if (edge) {
		G3::Reset(); // an edge into or out of 3 drops the graph uncounted (s.1.2)
	}
	if (Common::SkipCeil::t_mode != 3) {
		return;
	}
	if (!s.logged) {
		s.logged = true;
		LOGF("Skc3Mode: closure policies=L,b,Lp,Ld,Lu,Lw,Lt pause_k=%u\n", G3::CalK);
	}
	if (Common::SkipCeil::t_skip) {
		s.open.push_back(std::make_unique<G3::Frame>());
		s.cur        = s.open.back().get();
		s.cur->frame = Common::SkipCeil::t_gframe;
	}
}

void SkcCensus::G3ReadView(TextureCache& cache, ImageId id, const ImageViewInfo& view, bool storage, uint64_t shader_hash,
                           uint32_t stage) {
	const Common::SkipCeil::Skc3Pause pause;
	if (t_skc_op.serial == 0) {
		return;
	}
	auto* image = cache.m_slot_images.try_get(id);
	if (image == nullptr) {
		return;
	}
	const G3::IR r = G3::View(*image, view);
	G3::Rd       rd;
	if (G3::OpReader(rd)) {
		if (rd.seed && G3::Count(r) <= G3::MaxViewKeys) {
			G3::P2(*image, r);
		}
		G3::ReadImg(rd, r);
		G3::Finish(rd);
		G3::CountNext(rd);
		if (rd.seed && rd.found) {
			G3::Chain(rd.lwr, shader_hash, stage);
		}
	}
	if (storage) {
		Skc3W e;
		e.image = true;
		e.uid   = r.uid;
		e.bl    = r.bl;
		e.lc    = r.lc;
		e.by    = r.by;
		e.yc    = r.yc;
		e.asp   = r.asp;
		e.via   = G3::ViaW2;
		t_skc_op.g3w.push_back(e);
	}
}

void SkcCensus::G3Attachment(TextureCache& cache, ImageId id, const ImageViewInfo& view, uint8_t write_aspects,
                             uint8_t read_aspects) {
	const Common::SkipCeil::Skc3Pause pause;
	if (t_skc_op.serial == 0) {
		return;
	}
	auto* image = cache.m_slot_images.try_get(id);
	if (image == nullptr) {
		return;
	}
	// An attachment covers every aspect of its format; the pipeline state chooses which are read and written.
	const G3::IR r = G3::Clamp(*image, view.base_level, view.level_count, view.base_layer, view.layer_count,
	                           G3::ImageAspects(*image));
	if (const auto asp = static_cast<uint8_t>(r.asp & read_aspects); asp != 0) {
		G3::IR rr = r;
		rr.asp    = asp;
		G3::Rd rd;
		if (G3::OpReader(rd)) {
			G3::ReadImg(rd, rr);
			G3::Finish(rd);
			G3::CountNext(rd);
		}
	}
	if (const auto asp = static_cast<uint8_t>(r.asp & write_aspects); asp != 0) {
		Skc3W e;
		e.image = true;
		e.uid   = r.uid;
		e.bl    = r.bl;
		e.lc    = r.lc;
		e.by    = r.by;
		e.yc    = r.yc;
		e.asp   = asp;
		e.via   = G3::ViaW1;
		t_skc_op.g3w.push_back(e);
	}
}

void SkcCensus::G3Empty() noexcept {
	if (G3::Node* nd = G3::NodeOf(t_skc_op.node); nd != nullptr) {
		nd->empty = true;
	}
}

void SkcCensus::G3Dma() noexcept {
	if (t_skc_op.serial != 0) {
		t_skc_op.dma = true;
	}
}

void SkcCensus::G3GdsAccess(uint64_t gds_size) {
	const Common::SkipCeil::Skc3Pause pause;
	if (t_skc_op.serial == 0) {
		return;
	}
	// The read has no offset and size: no edge (s.3.3.1).  The binding is writable, so the operation may write any of
	// GDS - a W2 of the whole of it (a version of the class of s.3.1 must assume so).
	Common::FrameStats::Add(Common::FrameStats::Counter::Skc3GdsUnk, 1);
	const uint32_t w = t_skc_op.node;
	G3::Wr         wr;
	wr.w   = w;
	wr.lt  = w;
	wr.via = G3::ViaW2;
	wr.why = G3::WhyW2;
	G3::WriteBuf(wr, G3::S().gds, 0, gds_size, false);
	G3::CountWrite(w);
	if (G3::Node* nd = G3::NodeOf(w); nd != nullptr) {
		nd->w2 = true;
	}
}

void SkcCensus::G3DmaWrite(uint64_t vaddr, uint64_t size, bool gds) {
	const Common::SkipCeil::Skc3Pause pause;
	const uint32_t                    w = t_skc_op.node;
	G3::Wr                            wr;
	wr.w       = w;
	wr.lt      = w;
	wr.via     = G3::ViaM;
	wr.why     = G3::WhyM;
	wr.certain = true;
	wr.ep      = G3::EpOf();
	G3::WriteBuf(wr, gds ? G3::S().gds : G3::S().buf, vaddr, size, !gds);
	G3::CountWrite(w);
}

void SkcCensus::G3DmaCopy(uint64_t dst, uint64_t src, uint64_t size, bool dst_gds, bool src_gds) {
	const Common::SkipCeil::Skc3Pause pause;
	G3::Rd                            rd;
	if (G3::OpReader(rd)) {
		if (src_gds) {
			// [RC11]: in N an edge of the node M on the writers of the GDS range; in an unmarked frame a "next" seed.
			G3::ReadMap(rd, G3::S().gds, src, size);
			G3::Finish(rd);
			if (!rd.seed) {
				Common::FrameStats::Add(Common::FrameStats::Counter::Skc3MGds, 1);
			}
		} else {
			G3::ReadBufRange(rd, src, size);
		}
		G3::CountNext(rd);
	}
	G3DmaWrite(dst, size, dst_gds);
}

void SkcCensus::G3CpWrite(uint64_t vaddr, uint64_t size) {
	const Common::SkipCeil::Skc3Pause pause;
	Common::FrameStats::Add(Common::FrameStats::Counter::Skc3CpwN, 1);
	G3::Wr wr;
	wr.why     = G3::WhyCp;
	wr.certain = true;
	wr.ep      = G3::S().epoch;
	G3::WriteBuf(wr, G3::S().buf, vaddr, size, true);
	if (wr.hit) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Skc3CpwHit, 1);
	}
}

void SkcCensus::G3CpuWrite(uint64_t vaddr, uint64_t size) {
	const Common::SkipCeil::Skc3Pause pause;
	G3::Wr                            wr;
	wr.why     = G3::WhyCpu;
	wr.certain = true;
	wr.ep      = G3::S().epoch;
	G3::WriteBuf(wr, G3::S().buf, vaddr, size, true);
}

void SkcCensus::G3Download(const Image& image) {
	const Common::SkipCeil::Skc3Pause pause;
	G3::Wr                            wr;
	wr.why     = G3::WhyDl;
	wr.certain = true;
	wr.ep      = G3::S().epoch;
	G3::WriteBuf(wr, G3::S().buf, image.info.data.address, image.info.data.size, true);
}

uint64_t SkcCensus::G3PendAdd(uint64_t vaddr, uint64_t size) {
	std::scoped_lock lock {G3::g_pend_mutex};
	const uint64_t   id = ++G3::g_pend_id;
	G3::g_pend.emplace_back(id, vaddr, G3::End(vaddr, size));
	G3::g_pend_n.fetch_add(1, std::memory_order_release);
	return id;
}

void SkcCensus::G3PendDone(uint64_t id) {
	std::scoped_lock lock {G3::g_pend_mutex};
	for (auto it = G3::g_pend.begin(); it != G3::g_pend.end(); ++it) {
		if (std::get<0>(*it) == id) {
			G3::g_pend.erase(it);
			G3::g_pend_n.fetch_sub(1, std::memory_order_release);
			return;
		}
	}
}

void SkcCensus::G3CpuSeed(uint64_t vaddr, uint64_t size) {
	const Common::SkipCeil::Skc3Pause pause;
	auto&                             s = G3::S();
	if (s.open.empty() || size == 0) {
		return;
	}
	// The window of the fault itself [RC14] under every policy but Lw, and its 4 KiB pages under Lw.
	G3::Rd rd;
	rd.seed  = true;
	rd.cause = G3::CCpu;
	rd.mask  = static_cast<uint8_t>(G3::PALL & ~G3::PLW);
	G3::ReadBufRange(rd, vaddr, size);
	if (rd.found) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Skc3SCpu, 1);
	}
	const uint64_t end   = G3::End(vaddr, size);
	const uint64_t pbeg  = vaddr & ~(G3::PageBytes - 1);
	const uint64_t pend  = end > UINT64_MAX - (G3::PageBytes - 1) ? UINT64_MAX : (end + G3::PageBytes - 1) & ~(G3::PageBytes - 1);
	G3::Rd         page;
	page.seed   = true;
	page.cause  = G3::CCpu;
	page.mask   = G3::PLW;
	page.buffer = true;
	if (!G3::PendHit(pbeg, pend)) {
		G3::ReadMap(page, s.buf, pbeg, pend - pbeg);
	} else if (!G3::PendHit(vaddr, end)) {
		// ROADMAP s122 item 47(d): the page meets a pending erase and the window does not - Lw is seeded by the window
		// itself (Lw contains L); when the window meets it too, both are skipped.
		G3::ReadMap(page, s.buf, vaddr, size);
	}
}

void SkcCensus::G3CpSeed(uint64_t vaddr, uint64_t size) {
	const Common::SkipCeil::Skc3Pause pause;
	if (G3::S().open.empty()) {
		return;
	}
	G3::Rd rd;
	rd.seed  = true;
	rd.cause = G3::CCp;
	G3::ReadBufRange(rd, vaddr, size);
	if (rd.found) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Skc3SCp, 1);
	}
}

void SkcCensus::G3GdsSeed(uint64_t offset, uint64_t size) {
	const Common::SkipCeil::Skc3Pause pause;
	if (G3::S().open.empty()) {
		return;
	}
	G3::Rd rd;
	rd.seed  = true;
	rd.cause = G3::CGds;
	G3::ReadMap(rd, G3::S().gds, offset, size);
	G3::Finish(rd);
	if (rd.found) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Skc3SGds, 1);
	}
}

void SkcCensus::G3PrefSeed(uint64_t vaddr, uint64_t size) {
	const Common::SkipCeil::Skc3Pause pause;
	if (G3::S().open.empty()) {
		return;
	}
	G3::Rd rd;
	rd.seed  = true;
	rd.cause = G3::CAux;
	rd.mask  = G3::PLP;
	G3::ReadBufRange(rd, vaddr, size);
	if (rd.found) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Skc3SPref, 1);
	}
}

void SkcCensus::G3Flip(Image& image) {
	const Common::SkipCeil::Skc3Pause pause;
	auto&                             s = G3::S();
	if (s.cur != nullptr) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Skc3SFlipx, 1); // the correct version holds this flip
		return;
	}
	if (s.open.empty()) {
		return;
	}
	G3::Rd rd;
	rd.seed  = true;
	rd.cause = G3::CFlip;
	G3::ReadImg(rd, G3::Whole(image));
	G3::Finish(rd);
	if (rd.found) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Skc3SFlip, 1);
	}
}

void SkcCensus::G3Copy(uint8_t site, Image& destination, Image& source, uint32_t mip, uint32_t layer) {
	const Common::SkipCeil::Skc3Pause pause;
	G3::IR                            dst;
	G3::IR                            src;
	if (mip == UINT32_MAX) {
		dst = G3::Whole(destination);
		src = G3::Whole(source);
	} else {
		// Image::CopyMip: source level 0, all its layers, to level `mip` from layer `layer` on.
		dst = G3::Clamp(destination, mip, 1, layer, UINT32_MAX, G3::ImageAspects(destination));
		src = G3::Clamp(source, 0, 1, 0, UINT32_MAX, G3::ImageAspects(source));
	}
	G3::LazyWrite(site, dst, &src, 0, 0);
}

void SkcCensus::G3MetaClear(TextureCache& cache, uint64_t address) {
	const Common::SkipCeil::Skc3Pause pause;
	if (!Common::SkipCeil::t_gpu) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Skc3Xthr, 1);
		return;
	}
	G3::S().clr[address] = t_skc_op.node; // item 47(v): remembered for a late link of the surface
	G3::CloseCandidates(
	    [&cache](auto&& fn) { cache.m_slot_images.ForEach([&fn](Common::SlotId /*id*/, Image& image) { fn(image); }); },
	    address, UINT32_MAX);
}

void SkcCensus::G3MetaFill(TextureCache& cache, uint64_t address, uint32_t clear_mask, bool pending) {
	const Common::SkipCeil::Skc3Pause pause;
	if (!Common::SkipCeil::t_gpu) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Skc3Xthr, 1);
		return;
	}
	// ROADMAP s122 items 44(v), 47(v): the cleaner is remembered for a late link of the surface (the adoption of a
	// PendingDcc fill among them); a fill that is no clear forgets it.
	if (clear_mask != 0) {
		G3::S().clr[address] = t_skc_op.node;
	} else {
		G3::S().clr.erase(address);
	}
	if (pending) {
		return;
	}
	if (clear_mask != 0) {
		G3::CloseCandidates(
		    [&cache](auto&& fn) { cache.m_slot_images.ForEach([&fn](Common::SlotId /*id*/, Image& image) { fn(image); }); },
		    address, clear_mask);
	}
}

void SkcCensus::G3MetaAdopt(Image& image, uint64_t address) {
	const Common::SkipCeil::Skc3Pause pause;
	if (!Common::SkipCeil::t_gpu) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Skc3Xthr, 1);
		return;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::Skc3MclrN, 1);
	Common::FrameStats::Add(Common::FrameStats::Counter::Skc3MclrPend, 1);
	// A cleaner of a finalized frame is "none" (s.3.3.4); the entry stays for other late links (item 47(v)).
	if (G3::LateLink(image, address, UINT32_MAX, false)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Skc3Mclr, 1);
	}
}

void SkcCensus::G3MetaLate(Image& image, uint64_t address, uint32_t mask, bool seeded) {
	const Common::SkipCeil::Skc3Pause pause;
	if (!Common::SkipCeil::t_gpu) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Skc3Xthr, 1);
		return;
	}
	(void)G3::LateLink(image, address, mask, seeded);
}

void SkcCensus::G3SyncImg(uint64_t vaddr, uint64_t size) {
	const Common::SkipCeil::Skc3Pause pause;
	Common::FrameStats::Add(Common::FrameStats::Counter::Skc3SyncImg, 1);
	G3::Wr wr;
	wr.why     = G3::WhyDl;
	wr.certain = true;
	wr.ep      = G3::S().epoch;
	G3::WriteBuf(wr, G3::S().buf, vaddr, size, true);
}

void SkcCensus::G3ReadBufferLate(uint64_t vaddr, uint64_t size, bool written) {
	const Common::SkipCeil::Skc3Pause pause;
	if (t_skc_op.serial == 0) {
		return; // ROADMAP s122 item 35(g), N2: as ReadBuffer
	}
	G3::OpReadBuffer(vaddr, size, written);
}

void SkcCensus::G3ApplyAttach() {
	const Common::SkipCeil::Skc3Pause pause;
	G3::ApplyWrites(t_skc_op); // the W1 writes; W2 went at ApplyW2 (none on the bindfloor path)
}

void SkcCensus::G3ReadSub(TextureCache& cache, ImageId id, const Sub& sub) {
	const Common::SkipCeil::Skc3Pause pause;
	if (t_skc_op.serial == 0) {
		return;
	}
	auto* image = cache.m_slot_images.try_get(id);
	if (image != nullptr) {
		G3::ReadRange(*image, G3::SubIR(*image, sub));
	}
}

void SkcCensus::G3MatDepth(TextureCache& cache, ImageId id, const ImageViewInfo& view) {
	const Common::SkipCeil::Skc3Pause pause;
	if (t_skc_op.serial == 0) {
		return;
	}
	auto* image = cache.m_slot_images.try_get(id);
	if (image == nullptr) {
		return;
	}
	G3::LazyLog(SkcCensus::LazyMat);
	G3::Wr wr;
	wr.lt_only = true;
	wr.lt      = t_skc_op.node;
	wr.via     = G3::ViaW3;
	G3::WriteImg(wr, G3::Clamp(*image, view.base_level, view.level_count, view.base_layer, view.layer_count, 2));
}

void SkcStampW3(Image& image) noexcept {
	SkcCensus::StampW3(image);
}

void SkcCensus::StampW3(Image& image) noexcept {
	if (!Skc::t_gpu) {
		Skc::NoteOffThreadStamp();
		return;
	}
	if (Skc::t_mode < 2) {
		return;
	}
	const Skc::Skc3Pause skc3_pause;
	if (Skc::t_mode == 3) {
		G3::StampW3(image); // Session 124 (closure census): W3, a lazy write or an Lt-only write
	}
	if (Skc::t_acq || Skc::t_carry) {
		return;
	}
	SkcStampImage(image, Skc::t_kind, nullptr);
}

bool SkcCensus::OpBegin(uint8_t kind, bool draw) noexcept {
	if (Skc::t_kind != 0) {
		return false;
	}
	Skc::t_kind = kind;
	auto& op    = t_skc_op;
	op.serial   = ++t_skc_serial;
	if (op.serial == 0) {
		op.serial = ++t_skc_serial;
	}
	op.ps_hash  = 0;
	op.dispatch = !draw;
	op.bound    = false;
	op.x1       = false;
	op.x0_cs    = false;
	op.x0_keep  = false;
	op.ia_d     = false;
	op.ia_t     = false;
	op.w2.clear();
	op.d_stamped.clear();
	// Session 124, knob "skipceil" = 3: the operation of a marked frame is a node of its graph (s.3.2).
	op.node = 0;
	op.dma  = false;
	op.g3w.clear();
	if (Skc::t_mode == 3 && Skc::t_skip) {
		op.node = G3::NewNode(op.serial, kind);
	}
	return true;
}

void SkcCensus::OpEnd(TextureCache& cache, bool draw) noexcept {
	auto& op = t_skc_op;
	// Session 124, knob "skipceil" = 3: the D window ends here, first (s.5.1); then the node's tail and the epoch.
	if (Skc::t_mode == 3) [[unlikely]] {
		G3::OpEnd(op);
	}
	const Skc::Skc3Pause skc3_pause;
	if (op.x1) {
		if (draw) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcX1Draw, 1);
			if (op.bound && Skc::t_pass != t_skc_x1_pass) {
				t_skc_x1_pass = Skc::t_pass;
				Common::FrameStats::Add(Common::FrameStats::Counter::SkcX1Pass, 1);
			}
		} else {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcX1Cs, 1);
		}
	}
	// skc_wpasses: the host pass of this D draw, once per image and pass (the pass begins after the W1 / W2 stamps).
	for (const auto& id: op.d_stamped) {
		auto* image = cache.m_slot_images.try_get(id);
		if (image == nullptr || image->skc_wkind != Skc::KindD || image->skc_wframe != Skc::t_gframe ||
		    image->skc_wop != op.serial || image->skc_wpassid == Skc::t_pass) {
			continue;
		}
		// Passes only grow (t_pass), so a pass once left never comes back: the list stays distinct.
		image->skc_wpassid = Skc::t_pass;
		image->skc_wpasses.push_back(Skc::t_pass);
	}
	op.w2.clear();
	op.d_stamped.clear();
	op.serial  = 0;
	Skc::t_kind = 0;
}

bool SkcCensus::Carry(Image& destination, const Image& source) noexcept {
	const Skc::Skc3Pause skc3_pause; // Session 124 (s.5.2)
	if (!Skc::t_gpu) {
		Skc::NoteOffThreadStamp();
		return false;
	}
	if (Skc::t_mode < 2 || !SkcLiveDT(source)) {
		return false;
	}
	SkcClearWriters(destination);
	destination.skc_wkind  = source.skc_wkind;
	destination.skc_wframe = source.skc_wframe;
	if (Skc::t_carry) {
		return false;
	}
	Skc::t_carry = true;
	return true;
}

void SkcCensus::SkipSiteD() noexcept {
	if (Skc::t_kind == Skc::KindK) {
		Skc::t_kind = Skc::KindD;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::SkcCDd, 1);
	// Session 124, knob "skipceil" = 3: the node turns D and its window opens - the LAST statement (s.5.1).
	if (Skc::t_mode == 3) {
		G3::WindowBegin();
	}
}

void SkcCensus::SetDrawPs(uint64_t ps_hash) noexcept {
	const Skc::Skc3Pause skc3_pause; // Session 124 (s.5.2)
	t_skc_op.ps_hash = ps_hash;
}

void SkcCensus::ReadImage(TextureCache& cache, ImageId id, bool storage, uint64_t shader_hash, uint32_t stage) {
	const Skc::Skc3Pause skc3_pause;
	if (t_skc_op.serial == 0) {
		return; // ROADMAP s122 item 35(g), N2: outside every census operation - no read, no W2, no kind from t_skc_op
	}
	auto* image = cache.m_slot_images.try_get(id);
	if (image == nullptr) {
		return;
	}
	if (storage) {
		t_skc_op.w2.push_back({true, id, 0, 0});
	}
	if (!SkcLiveDT(*image)) {
		return;
	}
	const uint8_t  op   = Skc::t_kind;
	const bool     exec = SkcExecuted(op);
	const uint32_t k    = Skc::t_gframe - image->skc_wframe;
	if (t_skc_op.dispatch) {
		Skc::t_kind = Skc::KindT; // a dispatch that read D or T writes T (s.3.3)
	}
	if (image->skc_wkind == Skc::KindD) {
		if (t_skc_op.dispatch && k == 0 && Skc::t_skip && !t_skc_op.x0_cs) {
			t_skc_op.x0_cs = true;
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcX0Cs, 1);
		}
		if (exec && k == 1) {
			SkcX1Image(*image);
			auto& reader = t_skc_readers[shader_hash];
			reader.stage = stage;
			reader.n++;
			reader.selfw = reader.selfw || (shader_hash != 0 && shader_hash == image->skc_whash);
		} else if (exec && k >= 2) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcX2Rd, 1);
		}
	} else if (exec) {
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcXtRd, 1);
	}
}

void SkcCensus::ReadDepthCopySource(TextureCache& cache, ImageId id, const Sub& sub) {
	const Skc::Skc3Pause skc3_pause;
	auto* image = cache.m_slot_images.try_get(id);
	// Session 124, knob "skipceil" = 3: the copied subresources of the source are read by the copy (an operation K;
	// ROADMAP s122 item 47(e)).
	if (image != nullptr && Skc::t_mode == 3) {
		G3::ReadRange(*image, G3::SubIR(*image, sub));
	}
	if (image == nullptr || !SkcLiveDT(*image)) {
		return;
	}
	const uint8_t  op = Skc::t_kind;
	const uint32_t k  = Skc::t_gframe - image->skc_wframe;
	if (op == Skc::KindK) {
		// The copy's output derives from undone draws: T, decided before the W3 stamp of the destination (item 29(c)).
		Skc::t_kind = Skc::KindT;
		if (k == 0 && !t_skc_op.x0_keep) {
			t_skc_op.x0_keep = true;
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcX0Keep, 1);
		}
	}
	if (!SkcExecuted(op)) {
		return;
	}
	if (image->skc_wkind == Skc::KindD) {
		if (k == 1) {
			SkcX1Image(*image);
		} else if (k >= 2) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcX2Rd, 1);
		}
	} else {
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcXtRd, 1);
	}
}

void SkcCensus::Attachment(TextureCache& cache, ImageId id, bool writes) {
	const Skc::Skc3Pause skc3_pause;
	auto* image = cache.m_slot_images.try_get(id);
	if (image == nullptr) {
		return;
	}
	const uint8_t kind = Skc::t_kind;
	if (kind == Skc::KindR && SkcLive(*image) && image->skc_wkind == Skc::KindD &&
	    Skc::t_gframe - image->skc_wframe == 1) {
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcX1Att, 1);
	}
	if (writes && (kind == Skc::KindD || kind == Skc::KindR)) {
		SkcStampImage(*image, kind, &id);
	}
}

void SkcCensus::ReadBuffer(BufferCache& buffers, uint64_t vaddr, uint64_t size, bool written, bool g3_late) {
	const Skc::Skc3Pause skc3_pause;
	if (t_skc_op.serial == 0) {
		return; // ROADMAP s122 item 35(g), N2
	}
	if (Skc::t_mode == 3 && !g3_late) {
		G3::OpReadBuffer(vaddr, size, written); // Session 124: an edge / a "next" seed, and a pending W2 write
	}
	if (written) {
		t_skc_op.w2.push_back({false, {}, vaddr, size});
	}
	const auto q = buffers.SkcQueryRange(vaddr, size);
	if (!q.d && !q.t) {
		return;
	}
	const bool exec = SkcExecuted(Skc::t_kind);
	if (t_skc_op.dispatch) {
		Skc::t_kind = Skc::KindT;
	}
	if (t_skc_op.dispatch && q.d_k0 && Skc::t_skip && !t_skc_op.x0_cs) {
		t_skc_op.x0_cs = true;
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcX0Cs, 1);
	}
	if (exec) {
		if (q.d_k1) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcX1Buf, 1);
		}
		if (q.d_k2) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcX2Rd, 1);
		}
		if (q.t) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcXtRd, 1);
		}
	}
}

void SkcCensus::ReadIndirectArgs(BufferCache& buffers, uint64_t vaddr, uint64_t size) {
	const Skc::Skc3Pause skc3_pause;
	if (t_skc_op.serial == 0) {
		return; // ROADMAP s122 item 35(g), N2
	}
	if (Skc::t_mode == 3) {
		G3::OpReadBuffer(vaddr, size, false); // Session 124: the arguments are a read of every operation
	}
	if (!SkcExecuted(Skc::t_kind)) {
		return;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::SkcIa, 1);
	const auto q = buffers.SkcQueryRange(vaddr, size);
	if (q.d && !t_skc_op.ia_d) {
		t_skc_op.ia_d = true;
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcIaD, 1);
	}
	if (q.t && !t_skc_op.ia_t) {
		t_skc_op.ia_t = true;
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcIaT, 1);
	}
	if (t_skc_op.dispatch && (q.d || q.t)) {
		Skc::t_kind = Skc::KindT;
	}
}

void SkcCensus::NoteDma(BufferCache& buffers) {
	const Skc::Skc3Pause skc3_pause;
	if (!SkcExecuted(Skc::t_kind)) {
		return;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::SkcDmaAll, 1);
	if (buffers.SkcDLive(1)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcX1Dma, 1);
	}
	if (t_skc_op.dispatch && Skc::t_skip && buffers.SkcDLive(0)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcX0Dma, 1);
	}
}

void SkcCensus::ApplyW2(TextureCache& cache, BufferCache& buffers) {
	const Skc::Skc3Pause skc3_pause;
	auto&        op   = t_skc_op;
	if (Skc::t_mode == 3) {
		G3::ApplyWrites(op); // Session 124: the operation's pending W1 / W2 node writes, after its last read
	}
	const uint8_t kind = Skc::t_kind;
	const bool    keep = SkcKeeps(kind);
	op.bound           = true;
	for (const auto& entry: op.w2) {
		if (entry.image) {
			auto* image = cache.m_slot_images.try_get(entry.id);
			if (image == nullptr) {
				continue;
			}
			if (keep) {
				SkcStampImage(*image, kind, &entry.id);
			} else if (SkcLiveDT(*image)) {
				Common::FrameStats::Add(Common::FrameStats::Counter::SkcWMaybe, 1);
			}
			continue;
		}
		if (keep) {
			buffers.SkcStampRange(entry.vaddr, entry.size, kind);
			if (kind == Skc::KindD) {
				Common::FrameStats::Add(Common::FrameStats::Counter::SkcWDb, 1);
				Common::FrameStats::Add(Common::FrameStats::Counter::SkcWDbKb, (entry.size + 1023u) / 1024u);
			} else if (kind == Skc::KindT) {
				Common::FrameStats::Add(Common::FrameStats::Counter::SkcWT, 1);
			} else {
				Common::FrameStats::Add(Common::FrameStats::Counter::SkcWK, 1);
			}
		} else {
			const auto q = buffers.SkcQueryRange(entry.vaddr, entry.size);
			if (q.d || q.t) {
				Common::FrameStats::Add(Common::FrameStats::Counter::SkcWMaybe, 1);
			}
		}
	}
	op.w2.clear();
}

void SkcCensus::Upload(BufferCache& buffers, Image& image, uint32_t first_level, uint32_t level_count) {
	if (!Skc::t_gpu) {
		Skc::NoteOffThreadStamp();
		return;
	}
	if (Skc::t_mode < 2) {
		return;
	}
	const Skc::Skc3Pause skc3_pause;
	if (Skc::t_mode == 3) {
		G3::Upload(image, first_level, level_count); // Session 124: a lazy write of site "upload" [RC1]
	}
	// [N5]: the content comes from guest memory.  From a range the map holds as D / T it carries the latest such
	// segment's kind and frame (a carry, not a stamp); otherwise the label is erased.
	const auto range = image.SourceRange();
	SkcClearWriters(image);
	image.skc_wkind = 0;
	if (range.size == 0) {
		return;
	}
	const auto q = buffers.SkcQueryRange(range.address, range.size);
	if (q.last_kind != 0) {
		image.skc_wkind  = q.last_kind;
		image.skc_wframe = q.last_frame;
	}
}

void SkcCensus::DownloadRead(const Image& image) {
	const Skc::Skc3Pause skc3_pause;
	if (!SkcLiveDT(image)) {
		return;
	}
	Common::FrameStats::Add(image.skc_wkind == Skc::KindD ? Common::FrameStats::Counter::SkcRID
	                                                       : Common::FrameStats::Counter::SkcRIT,
	                        1);
}

void SkcCensus::FrameDump(BufferCache& buffers) {
	if (++t_skc_frames < 600) {
		return;
	}
	t_skc_frames = 0;
	std::vector<std::pair<uint64_t, SkcReader>> rows(t_skc_readers.begin(), t_skc_readers.end());
	std::sort(rows.begin(), rows.end(), [](const auto& a, const auto& b) { return a.second.n > b.second.n; });
	static constexpr const char* stages[] = {"vs", "ps", "cs"};
	for (size_t i = 0; i < rows.size() && i < 20; i++) {
		const auto& [hash, row] = rows[i];
		LOGF("SkcX1Reader: stage=%s hash=0x%016" PRIx64 " n=%" PRIu64 " selfw=%u\n", stages[row.stage < 3 ? row.stage : 0],
		     hash, row.n, row.selfw ? 1u : 0u);
	}
	t_skc_readers.clear();
	buffers.SkcDump();
}

} // namespace Libs::Graphics
