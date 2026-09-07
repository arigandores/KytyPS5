#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERMEMO_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERMEMO_H_

#include "graphics/guest_gpu/hardwareContext.h"
#include "graphics/host_gpu/renderer/cache/textureCache.h"
#include "graphics/host_gpu/renderer/colorRenderTarget.h"
#include "graphics/host_gpu/renderer/depthRenderTarget.h"
#include "graphics/host_gpu/renderer/image/image.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <vector>

namespace Libs::Graphics {

// FNV-1a over raw bytes. Padding bytes of register structs are stable (the HW context is built
// once and updated field by field), so a byte key can only produce misses, never false hits.
inline uint64_t MemoHashBytes(const void* data, size_t size,
                              uint64_t seed = 0xcbf29ce484222325ull) noexcept {
	const auto* bytes = static_cast<const uint8_t*>(data);
	uint64_t    hash  = seed;
	for (size_t i = 0; i < size; i++) {
		hash ^= bytes[i];
		hash *= 0x100000001b3ull;
	}
	return hash;
}

// Register state that fully determines ResolveRenderDepthTarget's result.
struct DepthTargetMemoKey {
	HW::DepthRenderTarget z;
	HW::RenderControl     rc;
	HW::DepthControl      dc;
	HW::StencilControl    sc;
	HW::StencilMask       sm;
	float                 depth_clear   = 0.0f;
	float                 bounds_min    = 0.0f;
	float                 bounds_max    = 0.0f;
	uint32_t              stencil_clear = 0;
};

// Hot-path memos of the GuestGpu thread. ASTRO BOT binds ~3200 textures and resolves ~530 colour
// targets per frame from a few hundred distinct register/descriptor values; the full resolution
// (tile layouts, validation, texture-cache lookups) costs 0.3-1 us each. Entries are validated
// against the live image (id generation, registration, rebind flag, backing) on every hit.
struct RenderExecutorMemo {
	struct Texture {
		std::array<uint32_t, 8> dwords {};
		uint64_t                resource_key = 0;
		bool                    valid        = false;
		ImageId                 image_id;
		TextureCache::ImageDesc desc;
	};
	struct ColorTarget {
		std::array<uint8_t, sizeof(HW::RenderTarget)> regs {};
		uint64_t                                     extra = 0;
		bool                                         valid = false;
		RenderColorInfo                              info;
	};
	struct DepthTarget {
		std::array<uint8_t, sizeof(DepthTargetMemoKey)> key {};
		bool                                           valid = false;
		RenderDepthInfo                                info;
	};

	static constexpr size_t TextureSlots = 4096;
	static constexpr size_t ColorSlots   = 512;
	static constexpr size_t DepthSlots   = 64;

	std::vector<Texture>     textures {TextureSlots};
	std::vector<ColorTarget> colors {ColorSlots};
	std::vector<DepthTarget> depths {DepthSlots};
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERMEMO_H_
