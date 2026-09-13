#include "graphics/host_gpu/renderer/pipeline/shaderResourceBarrier.h"

#include "common/assert.h"
#include "common/drawStat.h"
#include "common/frameStats.h"
#include "graphics/shader/shader.h"
#include "graphics/shader/shaderBindings.h"

#include <cstring>

namespace Libs::Graphics {

vk::PipelineStageFlags ShaderPipelineStages(vk::ShaderStageFlags stages) {
	vk::PipelineStageFlags result = {};
	if (stages & vk::ShaderStageFlagBits::eVertex) {
		result |= vk::PipelineStageFlagBits::eVertexShader;
	}
	if (stages & vk::ShaderStageFlagBits::eMeshEXT) {
		result |= vk::PipelineStageFlagBits::eMeshShaderEXT;
	}
	if (stages & vk::ShaderStageFlagBits::eFragment) {
		result |= vk::PipelineStageFlagBits::eFragmentShader;
	}
	if (stages & vk::ShaderStageFlagBits::eCompute) {
		result |= vk::PipelineStageFlagBits::eComputeShader;
	}
	EXIT_IF(!result);
	return result;
}

VulkanMemoryBarrier MakeShaderWriteDependency() {
	VulkanMemoryBarrier barrier {};
	barrier.srcAccessMask = vk::AccessFlagBits::eShaderWrite;
	barrier.dstAccessMask = vk::AccessFlagBits::eShaderRead | vk::AccessFlagBits::eShaderWrite |
	                        vk::AccessFlagBits::eVertexAttributeRead |
	                        vk::AccessFlagBits::eIndexRead | vk::AccessFlagBits::eUniformRead |
	                        vk::AccessFlagBits::eTransferRead | vk::AccessFlagBits::eTransferWrite |
	                        vk::AccessFlagBits::eColorAttachmentRead |
	                        vk::AccessFlagBits::eColorAttachmentWrite;
	return barrier;
}

VulkanMemoryBarrier MakeShaderAccessDependency() {
	VulkanMemoryBarrier barrier {};
	barrier.srcAccessMask = vk::AccessFlagBits::eShaderRead | vk::AccessFlagBits::eShaderWrite;
	barrier.dstAccessMask = vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite;
	return barrier;
}

VulkanMemoryBarrier MakeShaderWriteHazardDependency() {
	VulkanMemoryBarrier barrier {};
	barrier.srcAccessMask = vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite;
	barrier.dstAccessMask = vk::AccessFlagBits::eShaderRead | vk::AccessFlagBits::eShaderWrite;
	return barrier;
}

vk::BufferMemoryBarrier MakeGdsDependency(vk::Buffer buffer) {
	EXIT_IF(buffer == nullptr);

	vk::BufferMemoryBarrier barrier {};
	barrier.srcAccessMask = vk::AccessFlagBits::eHostWrite | vk::AccessFlagBits::eTransferWrite |
	                        vk::AccessFlagBits::eShaderWrite;
	barrier.dstAccessMask = vk::AccessFlagBits::eShaderRead | vk::AccessFlagBits::eShaderWrite;
	barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	barrier.buffer              = buffer;
	barrier.offset              = 0;
	barrier.size                = VK_WHOLE_SIZE;
	return barrier;
}

bool HasShaderBufferWrites(const ShaderStageRuntime& runtime, bool& atomic_only) {
	EXIT_IF(!runtime);
	const auto& program   = *runtime.program;
	const auto& resources = runtime.resources;
	EXIT_IF(resources.buffers.size() != program.info.buffers.size());
	bool has_writes = false;
	for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
		if (!program.info.buffers[i].written) {
			continue;
		}
		const auto& value = resources.buffers[i];
		EXIT_IF(value.dword_count < 4);
		ShaderBufferResource descriptor;
		std::memcpy(descriptor.fields, value.dwords.data(), sizeof(descriptor.fields));
		// A zero stride means byte addressing. For either addressing mode a nonzero record
		// count is exactly the condition for a nonempty descriptor range.
		if (descriptor.Base48() == 0 || descriptor.NumRecords() == 0) {
			continue;
		}
		has_writes = true;
		atomic_only &= program.info.buffers[i].atomic;
	}
	return has_writes;
}

bool HasShaderBufferWrites(const ShaderStageRuntime& runtime) {
	bool atomic_only = true;
	return HasShaderBufferWrites(runtime, atomic_only);
}

void ShaderAccessBarrier(vk::CommandBuffer vk_buffer, vk::PipelineStageFlags source_stages) {
	EXIT_IF(vk_buffer == nullptr || !source_stages);
	const auto barrier = MakeShaderAccessDependency();
	vk_buffer.pipelineBarrier(source_stages, vk::PipelineStageFlagBits::eAllCommands,
	                          vk::DependencyFlags {}, 1, &barrier, 0, nullptr, 0, nullptr);
}

void ShaderWriteHazardBarrier(vk::CommandBuffer      vk_buffer,
                              vk::PipelineStageFlags destination_stages) {
	EXIT_IF(vk_buffer == nullptr || !destination_stages);
	const auto barrier = MakeShaderWriteHazardDependency();
	vk_buffer.pipelineBarrier(vk::PipelineStageFlagBits::eAllCommands, destination_stages,
	                          vk::DependencyFlags {}, 1, &barrier, 0, nullptr, 0, nullptr);
}

vk::PipelineStageFlags FramebufferSpaceStages() noexcept {
	return vk::PipelineStageFlagBits::eFragmentShader |
	       vk::PipelineStageFlagBits::eEarlyFragmentTests |
	       vk::PipelineStageFlagBits::eLateFragmentTests |
	       vk::PipelineStageFlagBits::eColorAttachmentOutput;
}

void ShaderWriteBarrierLocal(vk::CommandBuffer vk_buffer, vk::PipelineStageFlags source_stages) {
	EXIT_IF(vk_buffer == nullptr || !source_stages);
	EXIT_IF(static_cast<bool>(source_stages & ~FramebufferSpaceStages()));
	Common::FrameStats::Add(Common::FrameStats::Counter::ShaderWriteBarriersLocal, 1);
	// Only accesses the fragment stage supports: a wider destination is not allowed here and is
	// covered by the deferred wide barrier issued when the pass closes.
	VulkanMemoryBarrier barrier {};
	barrier.srcAccessMask = vk::AccessFlagBits::eShaderWrite;
	barrier.dstAccessMask = vk::AccessFlagBits::eShaderRead | vk::AccessFlagBits::eShaderWrite;
	vk_buffer.pipelineBarrier(source_stages, vk::PipelineStageFlagBits::eFragmentShader,
	                          vk::DependencyFlagBits::eByRegion, 1, &barrier, 0, nullptr, 0,
	                          nullptr);
}

void ShaderWriteBarrier(vk::CommandBuffer vk_buffer, vk::PipelineStageFlags source_stages) {
	EXIT_IF(vk_buffer == nullptr || !source_stages);
	Common::FrameStats::Add(Common::FrameStats::Counter::ShaderWriteBarriers, 1);
	Common::DrawStat::Cut(Common::DrawStat::EdgeBarrier);
	const auto barrier = MakeShaderWriteDependency();
	vk_buffer.pipelineBarrier(source_stages,
	                          vk::PipelineStageFlagBits::eComputeShader |
	                              vk::PipelineStageFlagBits::eAllGraphics |
	                              vk::PipelineStageFlagBits::eTransfer,
	                          vk::DependencyFlags {}, 1, &barrier, 0, nullptr, 0, nullptr);
}

} // namespace Libs::Graphics
