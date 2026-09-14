#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_COLORRENDERTARGET_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_COLORRENDERTARGET_H_

#include "graphics/guest_gpu/gpu_defs.h"
#include "graphics/host_gpu/renderer/cache/textureCache.h"
#include "graphics/host_gpu/renderer/renderTarget.h"
#include "graphics/host_gpu/vulkanCommon.h"

#include <algorithm>
#include <cstdint>

namespace Libs::Graphics {

struct RenderColorInfo {
	// Discovery keeps guest image information but can remap the view into a larger cache image.
	TextureCache::ImageDesc         desc;
	ImageId                         image_id;
	uint32_t                        target_slot      = 0;
	uint32_t                        guest_mip_level   = 0;
	uint32_t                        guest_array_layer = 0;
	Prospero::ColorComponentMapping export_mapping;
	// Gate "rtfast": the RenderExecutorMemo colour slot this info was copied from and that slot's
	// version then (UINT32_MAX: none). A hit on the same slot at the same version skips the copy.
	uint32_t                        memo_slot    = UINT32_MAX;
	uint32_t                        memo_version = 0;

	[[nodiscard]] vk::Extent2D Extent() const {
		return {std::max(desc.info.extent.width >> guest_mip_level, 1u),
		        std::max(desc.info.extent.height >> guest_mip_level, 1u)};
	}
};

// Fixed DCC clear codes (0x00, 0x40, 0x80, 0xc0) encode a constant colour without the CB clear
// word registers. The host clear value is only well defined for these formats.
[[nodiscard]] bool DccFixedClearSupported(vk::Format format);
// Decodes a DCC clear code into a host clear value. Returns false for the register-backed code
// (0x20), unrecognized codes and formats without fixed-clear support.
[[nodiscard]] bool DecodeFixedDccClear(vk::Format format, uint8_t code, vk::ClearColorValue& clear);

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_COLORRENDERTARGET_H_
