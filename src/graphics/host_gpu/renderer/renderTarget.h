#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERTARGET_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERTARGET_H_

#include "graphics/host_gpu/vulkanCommon.h"

#include <array>
#include <cstdint>

namespace Libs::Graphics {

static constexpr uint32_t RENDER_COLOR_ATTACHMENTS_MAX = 8;

// Why CommandBuffer::EndRendering closed a render pass (KYTY_FRAME_TRACE: FrameTrace-rp counts the
// ends per reason, and the ends followed by a pass on the same targets). The first closer of a
// pass is charged; later closers of the same gap find no pass open. Counter::RpEnd* and
// Counter::RpRestart* (common/frameStats.h) follow this order.
enum class RenderPassEnd : uint8_t {
	State,          // BeginRendering with a different render state
	TargetTransit,  // attachment layout transition (AcquireRenderTargets)
	BindingTransit, // layout transition of a bound image (CommitBindings)
	Gds,            // GDS buffer barrier (CommitBindings)
	ShaderWrite,    // shader-write barrier after a draw with buffer writes
	Dispatch,       // compute dispatch
	BufferUpload,   // CPU -> buffer synchronization
	BufferCopy,     // buffer copy or fill on the GPU (DMA, overlap join, const-bank copy)
	ImageUpload,    // guest -> image upload
	Tiler,          // tiler compute (detile, D16 conversion, BGRA16 swap)
	Clear,          // image clears outside a pass (HTile slice, DCC, ClearImage)
	Sanitize,       // indirect draw argument sanitizer
	Download,       // readbacks and image -> buffer copies
	Submit,         // command buffer end at submit
	Other,
	Count
};

struct RenderAttachment {
	vk::ImageView           image_view    = nullptr;
	vk::ImageLayout         image_layout  = vk::ImageLayout::eUndefined;
	std::array<uint32_t, 4> clear_value   = {};
	bool                    is_clear      = false;
	bool                    has_depth     = false;
	bool                    depth_clear   = false;
	bool                    has_stencil   = false;
	bool                    stencil_clear = false;

	bool operator==(const RenderAttachment&) const = default;
};

struct RenderState {
	std::array<RenderAttachment, RENDER_COLOR_ATTACHMENTS_MAX> color_attachments;
	RenderAttachment                                           depth_stencil_attachment;
	uint32_t                                                   width                 = 0;
	uint32_t                                                   height                = 0;
	uint32_t                                                   num_layers            = 1;
	uint32_t                                                   num_color_attachments = 0;

	bool operator==(const RenderState&) const = default;
};

// Session 71 (gate G-area): the FrameTrace-x bucket of a render pass. Both counter tables are
// contiguous runs of Common::FrameStats::Counter, so a bucket is an offset from their first
// enumerator (PassShape0 / PassExtent0 / PassDraw0 in common/frameStats.h). constexpr, no
// state, no allocation: a pure classifier, not a decision.
[[nodiscard]] inline constexpr uint32_t RenderPassShapeBucket(uint32_t color_attachments) {
	return color_attachments < RENDER_COLOR_ATTACHMENTS_MAX ? color_attachments
	                                                        : RENDER_COLOR_ATTACHMENTS_MAX;
}

// `kpx` is width * height / 1024 of the pass. The edges put the three surfaces this scene is
// known to render each in a bucket of its own: the two rungs of the game's resolution ladder
// (1920x1080 = 2025 kpx -> bucket 3, 2432x1368 = 3249 kpx -> bucket 4; session 70 section 3)
// and the output target (3840x2160 = 8100 kpx -> bucket 6).
[[nodiscard]] inline constexpr uint32_t RenderPassExtentBucket(uint64_t kpx) {
	if (kpx < 128) {
		return 0;
	}
	if (kpx < 512) {
		return 1;
	}
	if (kpx < 1536) {
		return 2;
	}
	if (kpx < 2304) {
		return 3;
	}
	if (kpx < 4096) {
		return 4;
	}
	if (kpx < 7168) {
		return 5;
	}
	if (kpx < 9216) {
		return 6;
	}
	return 7;
}

[[nodiscard]] inline constexpr uint32_t render_sample_count(uint32_t encoded_samples) {
	return encoded_samples <= 3 ? 1u << encoded_samples : 0;
}

[[nodiscard]] inline constexpr vk::SampleCountFlagBits vulkan_sample_count(uint32_t samples) {
	switch (samples) {
		case 1: return vk::SampleCountFlagBits::e1;
		case 2: return vk::SampleCountFlagBits::e2;
		case 4: return vk::SampleCountFlagBits::e4;
		case 8: return vk::SampleCountFlagBits::e8;
		default: return {};
	}
}

enum class TargetViewType : uint8_t { Image2D, Image2DArray, Unsupported };

struct TargetViewInfo {
	TargetViewType type         = TargetViewType::Unsupported;
	uint32_t       base_layer   = 0;
	uint32_t       layer_count  = 0;
	uint32_t       image_layers = 0;
};

inline constexpr TargetViewInfo ResolveTargetViewInfo(uint32_t base_layer, uint32_t last_layer,
                                                      uint32_t draw_layer_offset = 0) {
	if (base_layer > last_layer || draw_layer_offset != 0) {
		return {};
	}
	return {base_layer == last_layer ? TargetViewType::Image2D : TargetViewType::Image2DArray,
	        base_layer, last_layer - base_layer + 1u, last_layer + 1u};
}

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERTARGET_H_
