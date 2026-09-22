#include "graphics/host_gpu/renderer/cache/faultManager.h"

#include "common/frameStats.h"

#include "common/assert.h"
#include "common/logging/log.h"
#include "gpu_tiler_shaders/fault_buffer_process_spv.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/cache/bufferCache.h"
#include "graphics/host_gpu/renderer/commandScheduler.h"
#include "graphics/host_gpu/vulkanCommon.h"
#include "graphics/shader/recompiler/backend/spirv/SpirvEmitter.h"

#include <algorithm>
#include <bit>
#include <cinttypes>
#include <cstring>
#include <limits>

namespace Libs::Graphics {

namespace {

constexpr size_t MaxPageFaults    = 1024;
constexpr size_t PageFaultAreaSize = MaxPageFaults * sizeof(uint64_t);

namespace LoopCap = ShaderRecompiler::Spirv::Emitter;

// KYTY_BVH_LOOP_CAP counters: LoopTripWords u32 right after the bitmap of CACHING_NUMPAGES bits.
constexpr uint64_t LoopTripOffset = BufferCache::CACHING_NUMPAGES / 8;
constexpr uint64_t LoopTripBytes  = LoopCap::LoopTripWords * sizeof(uint32_t);
static_assert(LoopTripOffset == uint64_t {LoopCap::LoopTripWordBase} * sizeof(uint32_t));

} // namespace

FaultManager::FaultManager(GraphicContext& graphics, CommandScheduler& scheduler,
                           BufferCache& buffer_cache)
    : m_graphics(graphics), m_scheduler(scheduler), m_buffer_cache(buffer_cache),
      m_fault_buffer(graphics, scheduler, MemoryUsage::DeviceLocal, 0, AllFlags,
                     LoopTripOffset + LoopTripBytes),
      m_download_buffer(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,
                        MaxPendingFaults * PageFaultAreaSize),
      m_trip_download(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,
                      MaxPendingFaults * LoopTripBytes) {
	SetVulkanObjectNameF(m_graphics.device, m_fault_buffer.Handle(), "Fault Buffer");
	LOGF("BvhLoopCap: cap=%u token='%s' default_slot0=%d\n", LoopCap::BvhLoopCap(),
	     LoopCap::BvhLoopCapSignatureToken().c_str(), LoopCap::BvhLoopCapSlot(0x380bb9d636390baeull));

	const vk::DescriptorSetLayoutBinding bindings[] {
	    {0, vk::DescriptorType::eStorageBuffer, 1, vk::ShaderStageFlagBits::eCompute, nullptr},
	    {1, vk::DescriptorType::eStorageBuffer, 1, vk::ShaderStageFlagBits::eCompute, nullptr},
	};
	vk::DescriptorSetLayoutCreateInfo layout_info {};
	layout_info.flags        = vk::DescriptorSetLayoutCreateFlagBits::ePushDescriptorKHR;
	layout_info.bindingCount = std::size(bindings);
	layout_info.pBindings    = bindings;
	RequireVulkanSuccess(
	    m_graphics.device.createDescriptorSetLayout(&layout_info, nullptr,
	                                                &m_fault_process_desc_layout),
	    "create fault-buffer descriptor layout");

	const auto module = CompileSPV(FAULT_BUFFER_PROCESS_SPV, m_graphics.device);

	vk::PipelineLayoutCreateInfo pipeline_layout_info {};
	pipeline_layout_info.setLayoutCount = 1;
	pipeline_layout_info.pSetLayouts    = &m_fault_process_desc_layout;
	RequireVulkanSuccess(
	    m_graphics.device.createPipelineLayout(&pipeline_layout_info, nullptr,
	                                           &m_fault_process_pipeline_layout),
	    "create fault-buffer pipeline layout");

	vk::PipelineShaderStageCreateInfo stage {};
	stage.stage  = vk::ShaderStageFlagBits::eCompute;
	stage.module = module;
	stage.pName  = "main";
	vk::ComputePipelineCreateInfo pipeline_info {};
	pipeline_info.stage  = stage;
	pipeline_info.layout = m_fault_process_pipeline_layout;
	const auto result = m_graphics.device.createComputePipelines(
	    nullptr, 1, &pipeline_info, nullptr, &m_fault_process_pipeline);
	m_graphics.device.destroyShaderModule(module, nullptr);
	RequireVulkanSuccess(result, "create fault-buffer pipeline");
	SetVulkanObjectNameF(m_graphics.device, m_fault_process_pipeline, "Fault Buffer Parser");
}

FaultManager::~FaultManager() {
	m_graphics.device.destroyPipeline(m_fault_process_pipeline, nullptr);
	m_graphics.device.destroyPipelineLayout(m_fault_process_pipeline_layout, nullptr);
	m_graphics.device.destroyDescriptorSetLayout(m_fault_process_desc_layout, nullptr);
}

void FaultManager::ClearLoopTripTail() {
	m_fault_buffer.Fill(LoopTripOffset, LoopTripBytes, 0);
}

void FaultManager::ProcessFaultBuffer() {
	if (const auto wait_tick = m_fault_areas[m_current_area]; wait_tick != 0) {
		Common::FrameStats::SiteScope site_scope("fault-buffer");
		m_scheduler.Wait(wait_tick);
		m_scheduler.PopPendingOperations();
	}

	const auto offset = m_current_area * PageFaultAreaSize;
	auto*      mapped = m_download_buffer.Mapped().data() + offset;
	std::memset(mapped, 0, PageFaultAreaSize);
	m_download_buffer.Flush(offset, PageFaultAreaSize);

	vk::BufferMemoryBarrier2 pre_barrier {};
	pre_barrier.srcStageMask  = vk::PipelineStageFlagBits2::eAllCommands;
	pre_barrier.srcAccessMask = vk::AccessFlagBits2::eShaderWrite;
	pre_barrier.dstStageMask  = vk::PipelineStageFlagBits2::eComputeShader;
	pre_barrier.dstAccessMask = vk::AccessFlagBits2::eShaderRead;
	pre_barrier.buffer        = m_fault_buffer.Handle();
	pre_barrier.offset        = 0;
	pre_barrier.size           = m_fault_buffer.Size();
	auto post_barrier         = pre_barrier;
	post_barrier.srcStageMask  = vk::PipelineStageFlagBits2::eComputeShader;
	post_barrier.srcAccessMask = vk::AccessFlagBits2::eShaderWrite;
	post_barrier.dstStageMask  = vk::PipelineStageFlagBits2::eAllCommands;
	post_barrier.dstAccessMask = vk::AccessFlagBits2::eShaderWrite;

	const vk::DescriptorBufferInfo infos[] {
	    {m_fault_buffer.Handle(), 0, m_fault_buffer.Size()},
	    {m_download_buffer.Handle(), offset, PageFaultAreaSize},
	};
	std::array<vk::WriteDescriptorSet, 2> writes {};
	for (uint32_t index = 0; index < writes.size(); ++index) {
		writes[index].dstBinding      = index;
		writes[index].descriptorCount = 1;
		writes[index].descriptorType  = vk::DescriptorType::eStorageBuffer;
		writes[index].pBufferInfo     = &infos[index];
	}

	m_scheduler.EndRendering();
	auto command = m_scheduler.Current().Handle();
	vk::DependencyInfo dependency {};
	dependency.dependencyFlags          = vk::DependencyFlagBits::eByRegion;
	dependency.bufferMemoryBarrierCount = 1;
	dependency.pBufferMemoryBarriers    = &pre_barrier;
	command.pipelineBarrier2(dependency);
	command.bindPipeline(vk::PipelineBindPoint::eCompute, m_fault_process_pipeline);
	command.pushDescriptorSetKHR(vk::PipelineBindPoint::eCompute,
	                             m_fault_process_pipeline_layout, 0, writes);
	const auto num_threads    = BufferCache::CACHING_NUMPAGES / 32;
	const auto num_workgroups = (num_threads + 63) / 64;
	command.dispatch(static_cast<uint32_t>(num_workgroups), 1, 1);
	dependency.pBufferMemoryBarriers = &post_barrier;
	command.pipelineBarrier2(dependency);

	// KYTY_BVH_LOOP_CAP: copy the counter tail next to the fault list; the counters only grow,
	// so each readback is diffed against the largest values already seen.
	const bool trips       = LoopCap::BvhLoopCap() != 0;
	const auto trip_offset = m_current_area * LoopTripBytes;
	if (trips) {
		vk::BufferMemoryBarrier2 tail_barrier {};
		tail_barrier.srcStageMask  = vk::PipelineStageFlagBits2::eAllCommands;
		tail_barrier.srcAccessMask = vk::AccessFlagBits2::eShaderWrite;
		tail_barrier.dstStageMask  = vk::PipelineStageFlagBits2::eCopy;
		tail_barrier.dstAccessMask = vk::AccessFlagBits2::eTransferRead;
		tail_barrier.buffer        = m_fault_buffer.Handle();
		tail_barrier.offset        = LoopTripOffset;
		tail_barrier.size          = LoopTripBytes;
		vk::BufferMemoryBarrier2 host_barrier {};
		host_barrier.srcStageMask  = vk::PipelineStageFlagBits2::eCopy;
		host_barrier.srcAccessMask = vk::AccessFlagBits2::eTransferWrite;
		host_barrier.dstStageMask  = vk::PipelineStageFlagBits2::eHost;
		host_barrier.dstAccessMask = vk::AccessFlagBits2::eHostRead;
		host_barrier.buffer        = m_trip_download.Handle();
		host_barrier.offset        = trip_offset;
		host_barrier.size          = LoopTripBytes;
		vk::DependencyInfo tail_dependency {};
		tail_dependency.bufferMemoryBarrierCount = 1;
		tail_dependency.pBufferMemoryBarriers    = &tail_barrier;
		command.pipelineBarrier2(tail_dependency);
		const vk::BufferCopy region {LoopTripOffset, trip_offset, LoopTripBytes};
		command.copyBuffer(m_fault_buffer.Handle(), m_trip_download.Handle(), 1, &region);
		tail_dependency.pBufferMemoryBarriers = &host_barrier;
		command.pipelineBarrier2(tail_dependency);
	}

	const auto area = m_current_area;
	m_scheduler.DeferOperation([this, mapped, offset, area, trips, trip_offset] {
		if (trips) {
			m_trip_download.Invalidate(trip_offset, LoopTripBytes);
			std::array<uint32_t, LoopCap::LoopTripWords> words {};
			std::memcpy(words.data(), m_trip_download.Mapped().data() + trip_offset,
			            LoopTripBytes);
			const auto grown = [&](uint32_t index) {
				const uint32_t delta =
				    words[index] > m_trip_last[index] ? words[index] - m_trip_last[index] : 0;
				m_trip_last[index] = std::max(m_trip_last[index], words[index]);
				return delta;
			};
			const auto trip_delta = grown(0);
			const auto near_delta = grown(1);
			(void)grown(2);
			for (uint32_t slot = 0; slot < LoopCap::LoopTripSlots; slot++) {
				(void)grown(8 + slot);
			}
			Common::FrameStats::Add(Common::FrameStats::Counter::LoopCapTrips, trip_delta);
			Common::FrameStats::Add(Common::FrameStats::Counter::LoopCapNear, near_delta);
			if ((trip_delta != 0 || near_delta != 0) && m_trip_lines < 64) {
				m_trip_lines++;
				LOGF("BvhLoopCapTrip: trips=+%u total=%u near=+%u near_total=%u max_spent=%u "
				     "cap=%u slot0=%u slot1=%u\n",
				     trip_delta, m_trip_last[0], near_delta, m_trip_last[1], m_trip_last[2],
				     LoopCap::BvhLoopCap(), m_trip_last[8], m_trip_last[9]);
			}
		}
		m_download_buffer.Invalidate(offset, PageFaultAreaSize);
		RangeSet    fault_ranges;
		const auto* faults = std::bit_cast<const uint64_t*>(mapped);
		const auto  count  = static_cast<uint32_t>(faults[0]);
		for (uint32_t index = 1; index <= count; ++index) {
			fault_ranges.Add(faults[index], BufferCache::CACHING_PAGESIZE);
			LOGF("Accessed non-GPU cached memory at 0x%016" PRIx64 "\n", faults[index]);
		}
		fault_ranges.ForEach([this](uint64_t start, uint64_t end) {
			EXIT_IF(end - start > std::numeric_limits<uint32_t>::max());
			(void)m_buffer_cache.FindBuffer(start, end - start);
		});
		m_fault_areas[area] = 0;
	});

	m_fault_areas[m_current_area++] = m_scheduler.CurrentTick();
	m_current_area %= MaxPendingFaults;
}

} // namespace Libs::Graphics
