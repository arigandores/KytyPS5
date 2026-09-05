#include "graphics/host_gpu/renderer/indirectArgsSanitizer.h"

#include "common/assert.h"
#include "common/logging/log.h"
#include "gpu_tiler_shaders/dispatch_indirect_sanitize_spv.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/commandScheduler.h"

#include <algorithm>
#include <array>
#include <cinttypes>

namespace Libs::Graphics {

namespace {

struct SanitizeParams {
	uint32_t source_dword;
	uint32_t max_x;
	uint32_t max_y;
	uint32_t max_z;
};

constexpr uint64_t ArgsSize = 3u * sizeof(uint32_t);

} // namespace

IndirectArgsSanitizer::IndirectArgsSanitizer(GraphicContext& graphics, CommandScheduler& scheduler)
    : m_graphics(graphics), m_scheduler(scheduler),
      m_args_buffer(graphics, scheduler, MemoryUsage::DeviceLocal, 0, AllFlags,
                    uint64_t {SlotSize} * SlotCount),
      m_slot_ticks(SlotCount, 0) {
	SetVulkanObjectNameF(m_graphics.device, m_args_buffer.Handle(), "Indirect Args Sanitizer");

	const vk::DescriptorSetLayoutBinding bindings[] {
	    {0, vk::DescriptorType::eStorageBuffer, 1, vk::ShaderStageFlagBits::eCompute, nullptr},
	    {1, vk::DescriptorType::eStorageBuffer, 1, vk::ShaderStageFlagBits::eCompute, nullptr},
	};
	vk::DescriptorSetLayoutCreateInfo layout_info {};
	layout_info.sType        = vk::StructureType::eDescriptorSetLayoutCreateInfo;
	layout_info.flags        = vk::DescriptorSetLayoutCreateFlagBits::ePushDescriptorKHR;
	layout_info.bindingCount = std::size(bindings);
	layout_info.pBindings    = bindings;
	RequireVulkanSuccess(
	    m_graphics.device.createDescriptorSetLayout(&layout_info, nullptr, &m_desc_layout),
	    "create indirect-args sanitizer descriptor layout");

	vk::ShaderModuleCreateInfo module_info {};
	module_info.sType    = vk::StructureType::eShaderModuleCreateInfo;
	module_info.codeSize = std::size(DISPATCH_INDIRECT_SANITIZE_SPV) * sizeof(uint32_t);
	module_info.pCode    = DISPATCH_INDIRECT_SANITIZE_SPV;
	vk::ShaderModule module = nullptr;
	RequireVulkanSuccess(m_graphics.device.createShaderModule(&module_info, nullptr, &module),
	                     "create indirect-args sanitizer shader module");

	vk::PushConstantRange push_range {};
	push_range.stageFlags = vk::ShaderStageFlagBits::eCompute;
	push_range.offset     = 0;
	push_range.size       = sizeof(SanitizeParams);
	vk::PipelineLayoutCreateInfo pipeline_layout_info {};
	pipeline_layout_info.sType                  = vk::StructureType::ePipelineLayoutCreateInfo;
	pipeline_layout_info.setLayoutCount         = 1;
	pipeline_layout_info.pSetLayouts            = &m_desc_layout;
	pipeline_layout_info.pushConstantRangeCount = 1;
	pipeline_layout_info.pPushConstantRanges    = &push_range;
	RequireVulkanSuccess(m_graphics.device.createPipelineLayout(&pipeline_layout_info, nullptr,
	                                                            &m_pipeline_layout),
	                     "create indirect-args sanitizer pipeline layout");

	vk::PipelineShaderStageCreateInfo stage {};
	stage.sType  = vk::StructureType::ePipelineShaderStageCreateInfo;
	stage.stage  = vk::ShaderStageFlagBits::eCompute;
	stage.module = module;
	stage.pName  = "main";
	vk::ComputePipelineCreateInfo pipeline_info {};
	pipeline_info.sType  = vk::StructureType::eComputePipelineCreateInfo;
	pipeline_info.stage  = stage;
	pipeline_info.layout = m_pipeline_layout;
	const auto result =
	    m_graphics.device.createComputePipelines(nullptr, 1, &pipeline_info, nullptr, &m_pipeline);
	m_graphics.device.destroyShaderModule(module, nullptr);
	RequireVulkanSuccess(result, "create indirect-args sanitizer pipeline");
	SetVulkanObjectNameF(m_graphics.device, m_pipeline, "Indirect Args Sanitizer");
}

IndirectArgsSanitizer::~IndirectArgsSanitizer() {
	m_graphics.device.destroyPipeline(m_pipeline, nullptr);
	m_graphics.device.destroyPipelineLayout(m_pipeline_layout, nullptr);
	m_graphics.device.destroyDescriptorSetLayout(m_desc_layout, nullptr);
}

std::pair<vk::Buffer, uint64_t> IndirectArgsSanitizer::Sanitize(vk::CommandBuffer command,
                                                                const Buffer&     source,
                                                                uint64_t          source_offset) {
	EXIT_IF(source_offset + ArgsSize > source.Size());

	// Reuse the ring slot only once the GPU has finished the submission that read it.
	const auto slot = m_next_slot;
	m_next_slot     = (m_next_slot + 1) % SlotCount;
	if (const auto tick = m_slot_ticks[slot]; tick != 0 && !m_scheduler.IsFree(tick)) {
		m_scheduler.Wait(tick);
	}
	m_slot_ticks[slot]     = m_scheduler.CurrentTick();
	const auto slot_offset = uint64_t {slot} * SlotSize;

	const auto& limits = m_graphics.physical_device_properties.limits;
	const auto  alignment =
	    std::max<uint64_t>(limits.minStorageBufferOffsetAlignment, sizeof(uint32_t));
	const auto aligned_offset = source_offset & ~(alignment - 1);
	const auto source_range   = source_offset - aligned_offset + ArgsSize;

	const SanitizeParams params {
	    static_cast<uint32_t>((source_offset - aligned_offset) / sizeof(uint32_t)),
	    limits.maxComputeWorkGroupCount[0],
	    limits.maxComputeWorkGroupCount[1],
	    limits.maxComputeWorkGroupCount[2],
	};

	// The arguments were produced by earlier shaders or transfers; the slot was last read by a
	// previous vkCmdDispatchIndirect.
	VulkanMemoryBarrier before {};
	before.sType         = vk::StructureType::eMemoryBarrier;
	before.srcAccessMask = vk::AccessFlagBits::eShaderWrite | vk::AccessFlagBits::eTransferWrite |
	                       vk::AccessFlagBits::eIndirectCommandRead;
	before.dstAccessMask = vk::AccessFlagBits::eShaderRead | vk::AccessFlagBits::eShaderWrite;
	command.pipelineBarrier(vk::PipelineStageFlagBits::eAllCommands,
	                        vk::PipelineStageFlagBits::eComputeShader, vk::DependencyFlags {}, 1,
	                        &before, 0, nullptr, 0, nullptr);

	const vk::DescriptorBufferInfo infos[] {
	    {source.Handle(), aligned_offset, source_range},
	    {m_args_buffer.Handle(), slot_offset, SlotSize},
	};
	std::array<vk::WriteDescriptorSet, 2> writes {};
	for (uint32_t index = 0; index < writes.size(); ++index) {
		writes[index].sType           = vk::StructureType::eWriteDescriptorSet;
		writes[index].dstBinding      = index;
		writes[index].descriptorCount = 1;
		writes[index].descriptorType  = vk::DescriptorType::eStorageBuffer;
		writes[index].pBufferInfo     = &infos[index];
	}
	command.bindPipeline(vk::PipelineBindPoint::eCompute, m_pipeline);
	command.pushDescriptorSetKHR(vk::PipelineBindPoint::eCompute, m_pipeline_layout, 0, writes);
	command.pushConstants(m_pipeline_layout, vk::ShaderStageFlagBits::eCompute, 0, sizeof(params),
	                      &params);
	command.dispatch(1, 1, 1);

	vk::BufferMemoryBarrier after {};
	after.sType               = vk::StructureType::eBufferMemoryBarrier;
	after.srcAccessMask       = vk::AccessFlagBits::eShaderWrite;
	after.dstAccessMask       = vk::AccessFlagBits::eIndirectCommandRead;
	after.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	after.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	after.buffer              = m_args_buffer.Handle();
	after.offset              = slot_offset;
	after.size                = SlotSize;
	command.pipelineBarrier(vk::PipelineStageFlagBits::eComputeShader,
	                        vk::PipelineStageFlagBits::eDrawIndirect, vk::DependencyFlags {}, 0,
	                        nullptr, 1, &after, 0, nullptr);

	return {m_args_buffer.Handle(), slot_offset};
}

} // namespace Libs::Graphics
