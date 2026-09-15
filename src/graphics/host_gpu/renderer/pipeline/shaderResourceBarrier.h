#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_SHADERRESOURCEBARRIER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_SHADERRESOURCEBARRIER_H_

#include "graphics/host_gpu/graphicContext.h"
#include "graphics/shader/recompiler/ir/passes/ResourceMaterialization.h"

namespace Libs::Graphics {

struct ShaderStageRuntime;

vk::ShaderStageFlagBits NativeShaderStage(ShaderType stage);
vk::PipelineStageFlags  ShaderPipelineStages(vk::ShaderStageFlags stages);
VulkanMemoryBarrier     MakeShaderAccessDependency();
VulkanMemoryBarrier     MakeShaderWriteHazardDependency();
VulkanMemoryBarrier     MakeShaderWriteDependency();
vk::BufferMemoryBarrier MakeGdsDependency(vk::Buffer buffer);
bool HasShaderBufferWrites(const ShaderStageRuntime& runtime);
// Same walk, and whether every nonempty written buffer of the stage carries the IR's atomic flag.
// `atomic_only` is left untouched when the stage writes nothing.
bool HasShaderBufferWrites(const ShaderStageRuntime& runtime, bool& atomic_only);
void ShaderAccessBarrier(vk::CommandBuffer vk_buffer, vk::PipelineStageFlags source_stages);
void ShaderWriteHazardBarrier(vk::CommandBuffer      vk_buffer,
                              vk::PipelineStageFlags destination_stages);
void ShaderWriteBarrier(vk::CommandBuffer vk_buffer, vk::PipelineStageFlags source_stages);
// Stages a barrier may name inside a render pass instance started with vkCmdBeginRendering
// (VUID-vkCmdPipelineBarrier-srcStageMask-09556 with VK_KHR_dynamic_rendering_local_read).
[[nodiscard]] vk::PipelineStageFlags FramebufferSpaceStages() noexcept;
// By-region fragment -> fragment form of ShaderWriteBarrier, legal inside a render pass.
void ShaderWriteBarrierLocal(vk::CommandBuffer vk_buffer, vk::PipelineStageFlags source_stages);

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_SHADERRESOURCEBARRIER_H_
