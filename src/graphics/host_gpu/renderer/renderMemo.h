#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERMEMO_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERMEMO_H_

#include "graphics/guest_gpu/hardwareContext.h"
#include "graphics/host_gpu/renderer/cache/textureCache.h"
#include "graphics/host_gpu/renderer/colorRenderTarget.h"
#include "graphics/host_gpu/renderer/depthRenderTarget.h"
#include "graphics/host_gpu/renderer/image/image.h"
#include "graphics/host_gpu/renderer/renderMemo8.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <xxhash.h>

namespace Libs::Graphics {

inline bool FastRenderMemoEnabled() noexcept {
	static const bool enabled = [] {
		const auto* value = std::getenv("KYTY_RENDER_MEMO_FAST");
		return value == nullptr || value[0] != '0';
	}();
	return enabled;
}

// Transient lookup hash only; persisted shader/pipeline keys do not use this helper.
// Register keys are compared byte for byte after hashing, including their padding.
inline uint64_t MemoHashBytes(const void* data, size_t size,
                              uint64_t seed = 0xcbf29ce484222325ull) noexcept {
	if (FastRenderMemoEnabled()) {
		return XXH3_64bits_withSeed(data, size, seed);
	}
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
		// Moves whenever the slot is filled or invalidated: a TextureBinding remembers it, so a
		// slot rewritten later in the same draw is not mistaken for the one it was resolved from.
		uint32_t                version    = 0;
		// Gate "texfast": FindTexture's view for (image_id, desc), valid while the image's
		// bind_stamp still equals fast_stamp (RebindImages).
		uint32_t                fast_stamp = 0;
		vk::ImageView           fast_view  = nullptr;
	};
	// Gate "texmemo2": tag of each slot for the two-way lookup; neighbours form a set.
	struct TextureWay {
		uint64_t hash = 0; // MemoHashBytes of the slot key when it was filled
		uint64_t use  = 0; // texture_clock at the last fill or hit, 0 = never filled
	};
	// Session 121, knob "texmemo8" (renderMemo8.h): the SAME `textures` entries as 512 sets x 8 ways, entry index =
	// set * 8 + way, so memo_index < TextureSlots and every reader of memo_index / memo_version keeps indexing a real
	// entry.  Invariant: texture_sets8[s].use[w] != 0 <=> textures[s * 8 + w].valid, and then the tag is the high 32
	// bits of the memo hash of the key the entry holds.
	using TextureSet8 = TexMemo8Set;
	// texmemo8 >= 2 (VERIFY, never timed): the key a DIRECT memo (index memo_hash % TextureSlots) would hold now, so a
	// hit the direct memo would have missed ("gained") is recognised and checked against a fresh full resolution.
	struct TextureDirectKey {
		uint64_t                resource_key = 0;
		std::array<uint32_t, 8> dwords {};
		ImageId                 image_id;
		bool                    valid = false;
	};
	// Gate "texmemo2": resource key by ImageResource address. The 64 key bytes are compared on
	// every use, so the answer does not depend on the object staying where it was.
	struct ResourceKey {
		const void*             resource = nullptr;
		std::array<uint64_t, 8> words {};
		uint64_t                key = 0;
	};
	struct ColorTarget {
		std::array<uint8_t, sizeof(HW::RenderTarget)> regs {};
		uint64_t                                     extra = 0;
		bool                                         valid = false;
		// Gate "rtfast": moves with every store; the info copied out remembers it (memo_version).
		uint32_t                                     version = 0;
		RenderColorInfo                              info;
	};
	struct DepthTarget {
		std::array<uint8_t, sizeof(DepthTargetMemoKey)> key {};
		bool                                           valid   = false;
		uint32_t                                       version = 0; // gate "rtfast", as above
		RenderDepthInfo                                info;
	};

	// Session 83, gate "bindpack" (PLAN_82_bind.md item 1): the answer to a null T# is a pure
	// function of (numeric class, storage, native depth compare) - at most nine values in the
	// whole run - so it is kept by key and not looked up. Validated on every hit against the
	// live slot, which is more than GetNullImage does with m_null_images.
	struct NullTexture {
		bool                    valid = false;
		ImageId                 image_id;
		TextureCache::ImageDesc desc;
	};
	static constexpr size_t NullTextureSlots = 9;

	static constexpr size_t TextureSlots = 4096;
	static constexpr size_t TextureWays8 = TexMemo8Ways;  // knob "texmemo8"
	static constexpr size_t TextureSets8 = TexMemo8Sets;  // 512
	static_assert(TextureSlots == TexMemo8Slots && TextureWays8 * TextureSets8 == TextureSlots);
	static constexpr size_t ResourceKeySlots = 1024;
	static constexpr size_t ColorSlots   = 512;
	static constexpr size_t DepthSlots   = 64;

	std::vector<Texture>     textures {TextureSlots};
	// Session 121, knob "texmemo8": the effective value the entries are laid out for (0 direct, 1-3 8-way), the LRU
	// clock of texture_sets8 (renormalised before it wraps), the xorshift32 state of the texmemo8 >= 2 samplers (RC3;
	// never 0), the 512 set lines inline (32 KiB, zero = every way empty; never read at texmemo8 = 0) and the direct
	// shadow (texmemo8 >= 2 only, allocated by the mode switch, else empty).
	uint32_t                 texture_mode    = 0;
	uint32_t                 texture8_clock  = 0;
	uint32_t                 texture8_sample = 0x9E3779B9u;
	std::array<TextureSet8, TextureSets8> texture_sets8 {};
	std::vector<TextureDirectKey>         texture8_direct;
	std::vector<TextureWay>  texture_ways {TextureSlots};
	uint64_t                 texture_clock = 0;
	std::vector<ResourceKey> resource_keys {ResourceKeySlots};
	std::vector<ColorTarget> colors {ColorSlots};
	std::vector<DepthTarget> depths {DepthSlots};
	std::array<NullTexture, NullTextureSlots> null_textures {};
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERMEMO_H_
