#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DESCRIPTORS_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DESCRIPTORS_H_

#include "common/assert.h"
#include "graphics/host_gpu/renderer/cache/bufferCache.h"
#include "graphics/host_gpu/renderer/cache/textureCache.h"
#include "graphics/host_gpu/renderer/image/image.h"
#include "graphics/host_gpu/vulkanCommon.h"
#include "graphics/shader/recompiler/ir/ShaderIR.h"
#include "graphics/shader/shaderBindings.h"

#include <cstdint>
#include <cstring>
#include <type_traits>
#include <vector>

namespace Libs::Graphics {

struct ShaderStageRuntime;

struct TextureBinding {
	TextureBinding() = default;
	// Session 57, B2a: PrepareBindings builds the binding in its vector element (one ImageDesc copy).
	TextureBinding(ImageId id, const TextureCache::ImageDesc& binding_desc, uint32_t index,
	               uint32_t version)
	    : image_id(id), desc(binding_desc), memo_index(index), memo_version(version) {}

	ImageId                    image_id;
	vk::ImageView              image_view = nullptr;
	TextureCache::ImageDesc    desc;
	vk::ImageLayout            layout = vk::ImageLayout::eUndefined;
	std::vector<vk::ImageView> mip_views;
	// RenderExecutorMemo::textures slot this binding was resolved from, and that slot's version
	// then (UINT32_MAX: none). RebindImages (gate "texfast") reuses the slot's view.
	uint32_t                   memo_index   = UINT32_MAX;
	uint32_t                   memo_version = 0;
};

// Session 93, gate "bdacap" (MEASUREMENT ONLY, pred/01_bdacap.md): the class
// NativeStorageBuffer gave a buffer slot.  Exactly one per slot, first match wins in the
// order below.  Written only while the gate is armed, so every slot of an unarmed run
// stays None; it feeds no value, no decision and no side effect.
enum class BdaCapClass : uint8_t {
	None      = 0,
	Null      = 1,
	Formatted = 2,
	ConstBank = 3,
	Ring      = 4,
	Ok        = 5,
};

struct PreparedBindings {
	struct BufferSource {
		uint64_t address = 0;
		uint64_t size    = 0;
		BufferId id;
	};

	// The draw owns the immutable compiled-program/runtime-snapshot association through commit.
	const ShaderStageRuntime* runtime = nullptr;
	// Keep the resolved guest range through cache preparation; only the host buffer ID may
	// become stale and need resolving again when bindings are rebound.
	std::vector<BufferSource>             buffer_sources;
	std::vector<vk::DescriptorBufferInfo> buffers;
	// Session 93, gate "bdacap" (MEASUREMENT ONLY): buffer_class[i] is the BdaCapClass of
	// buffers[i], pushed beside it by RebindBuffers and read by the dm_buf1_ok census in
	// renderDraw.cpp.  Parallel to buffers by construction (one push_back each, same loop).
	// All None unless the gate is armed.
	std::vector<uint8_t>                  buffer_class;
	std::vector<TextureBinding>           images;
	std::vector<vk::Sampler>              samplers;
	vk::DescriptorBufferInfo              gds {nullptr, 0, VK_WHOLE_SIZE};
	vk::DescriptorBufferInfo              flattened_srt;
	vk::DescriptorBufferInfo              shader_data_buffer;
	std::vector<uint32_t>                 shader_data;
	// Session 82, gate "bindkey" (measurement only): the hash of this stage's binding inputs and
	// whether it equalled the previous draw's.  Both are zero/false unless the gate is on.
	uint64_t                              key     = 0;
	bool                                  key_hit = false;
	// Session 83, gate "bindpack" (PLAN_82_bind.md item 4): which of the three binding kinds
	// the three FindBinding scans of a stage ask about are present in program.bindings, with
	// bit 3 set to mark the mask computed. Written by PrepareBindings, read by FindBuffers,
	// which already takes the same PreparedBindings. Recomputed for every stage of every draw:
	// it is not a cache and has no invalidation source.
	uint32_t                              kind_mask = 0;

	void Reset() {
		// Capacity belongs to the executor; every descriptor belongs to this draw only.
		runtime = nullptr;
		buffer_sources.clear();
		buffers.clear();
		buffer_class.clear();
		images.clear();
		samplers.clear();
		shader_data.clear();
		gds = {nullptr, 0, VK_WHOLE_SIZE};
		flattened_srt = {};
		shader_data_buffer = {};
		key       = 0;
		key_hit   = false;
		kind_mask = 0;
	}
};

[[nodiscard]] vk::DescriptorType
NativeDescriptorType(ShaderRecompiler::IR::DescriptorBindingKind kind);
[[nodiscard]] uint32_t
NativeDescriptorCount(const ShaderRecompiler::IR::DescriptorBinding& binding);
[[nodiscard]] vk::DescriptorImageInfo MakeImageInfo(const TextureBinding& texture,
                                                    uint32_t              element = 0);

template <typename T>
[[nodiscard]] T DecodeNativeDescriptor(const ShaderRecompiler::IR::DescriptorValue& value) {
	static_assert(std::is_trivially_copyable_v<T>);
	static_assert(sizeof(T) % sizeof(uint32_t) == 0);
	T result {};
	EXIT_IF(value.dword_count < sizeof(result) / sizeof(uint32_t));
	std::memcpy(&result, value.dwords.data(), sizeof(result));
	return result;
}

[[nodiscard]] bool IsSupportedDepthTextureEncoding(const ShaderTextureResource& descriptor,
                                                   bool r128 = false);
void ValidateStorageTexture(const ShaderRecompiler::IR::ImageResource& resource,
                            const ShaderTextureResource& descriptor, uint64_t size);

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DESCRIPTORS_H_
