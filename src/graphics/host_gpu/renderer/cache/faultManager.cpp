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
#include "graphics/shader/recompiler/frontend/decode/ShaderDecoder.h"

#include <algorithm>
#include <bit>
#include <chrono>
#include <cinttypes>
#include <cstdio>
#include <cstring>
#include <limits>
#include <string>

namespace Libs::Graphics {

namespace {

constexpr size_t MaxPageFaults    = 1024;
constexpr size_t PageFaultAreaSize = MaxPageFaults * sizeof(uint64_t);

namespace LoopCap = ShaderRecompiler::Spirv::Emitter;

// KYTY_BVH_LOOP_CAP counters: LoopTripWords u32 right after the bitmap of CACHING_NUMPAGES bits.
constexpr uint64_t LoopTripOffset = BufferCache::CACHING_NUMPAGES / 8;
constexpr uint64_t LoopTripBytes  = LoopCap::LoopTripWords * sizeof(uint32_t);
static_assert(LoopTripOffset == uint64_t {LoopCap::LoopTripWordBase} * sizeof(uint32_t));
// Track F, F11d (ROADMAP p.376(v)): the KYTY_DIAG_BVHNODES words follow the loop-cap words; the tail, the
// fault buffer and each readback area grow by DiagBytes only at =1.
constexpr uint64_t DiagOffset = LoopTripOffset + LoopTripBytes;
constexpr uint64_t DiagBytes  = LoopCap::DiagWords * sizeof(uint32_t);
static_assert(DiagOffset == uint64_t {LoopCap::DiagWordBase} * sizeof(uint32_t));
static_assert(LoopCap::DiagWords == 64, "faultManager.h keeps 64 diagnostic words");

} // namespace

uint64_t FaultManager::TailOffset() {
	return LoopTripOffset;
}

uint64_t FaultManager::TailBytes() {
	return LoopTripBytes + (ShaderRecompiler::Decoder::DiagBvhNodesEnabled() ? DiagBytes : 0);
}

FaultManager::FaultManager(GraphicContext& graphics, CommandScheduler& scheduler,
                           BufferCache& buffer_cache)
    : m_graphics(graphics), m_scheduler(scheduler), m_buffer_cache(buffer_cache),
      m_fault_buffer(graphics, scheduler, MemoryUsage::DeviceLocal, 0, AllFlags,
                     LoopTripOffset + TailBytes()),
      m_download_buffer(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,
                        MaxPendingFaults * PageFaultAreaSize),
      m_trip_download(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,
                      MaxPendingFaults * TailBytes()) {
	SetVulkanObjectNameF(m_graphics.device, m_fault_buffer.Handle(), "Fault Buffer");
	LOGF("BvhLoopCap: cap=%u token='%s' default_slot0=%d\n", LoopCap::BvhLoopCap(),
	     LoopCap::BvhLoopCapSignatureToken().c_str(), LoopCap::BvhLoopCapSlot(0x380bb9d636390baeull));
	if (ShaderRecompiler::Decoder::DiagBvhNodesEnabled()) {
		LOGF("DiagBvhNodes: mode=1 words=%u tail_bytes=%" PRIu64 "\n", LoopCap::DiagWords, TailBytes());
	}

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
	// Track F, F11d (RC1 of F11b): the same command zeroes the diagnostic words at =1 (DeviceLocal memory
	// starts undefined); the host takes them only from readbacks recorded after this (m_tail_cleared).
	m_fault_buffer.Fill(TailOffset(), TailBytes(), 0);
	m_tail_cleared.store(true, std::memory_order_release);
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
	// Track F, F11d: at KYTY_DIAG_BVHNODES=1 the copy takes the whole tail (one region: loop-cap and
	// diagnostic words) once ClearLoopTripTail has zeroed it; at =0 the tail is LoopTripBytes, as before.
	const bool diag        = ShaderRecompiler::Decoder::DiagBvhNodesEnabled() &&
	                  m_tail_cleared.load(std::memory_order_acquire);
	const auto tail_bytes  = TailBytes();
	const auto trip_offset = m_current_area * tail_bytes;
	if (trips || diag) {
		vk::BufferMemoryBarrier2 tail_barrier {};
		tail_barrier.srcStageMask  = vk::PipelineStageFlagBits2::eAllCommands;
		tail_barrier.srcAccessMask = vk::AccessFlagBits2::eShaderWrite;
		tail_barrier.dstStageMask  = vk::PipelineStageFlagBits2::eCopy;
		tail_barrier.dstAccessMask = vk::AccessFlagBits2::eTransferRead;
		tail_barrier.buffer        = m_fault_buffer.Handle();
		tail_barrier.offset        = LoopTripOffset;
		tail_barrier.size          = tail_bytes;
		vk::BufferMemoryBarrier2 host_barrier {};
		host_barrier.srcStageMask  = vk::PipelineStageFlagBits2::eCopy;
		host_barrier.srcAccessMask = vk::AccessFlagBits2::eTransferWrite;
		host_barrier.dstStageMask  = vk::PipelineStageFlagBits2::eHost;
		host_barrier.dstAccessMask = vk::AccessFlagBits2::eHostRead;
		host_barrier.buffer        = m_trip_download.Handle();
		host_barrier.offset        = trip_offset;
		host_barrier.size          = tail_bytes;
		vk::DependencyInfo tail_dependency {};
		tail_dependency.bufferMemoryBarrierCount = 1;
		tail_dependency.pBufferMemoryBarriers    = &tail_barrier;
		command.pipelineBarrier2(tail_dependency);
		const vk::BufferCopy region {LoopTripOffset, trip_offset, tail_bytes};
		command.copyBuffer(m_fault_buffer.Handle(), m_trip_download.Handle(), 1, &region);
		tail_dependency.pBufferMemoryBarriers = &host_barrier;
		command.pipelineBarrier2(tail_dependency);
	}

	const auto area = m_current_area;
	m_scheduler.DeferOperation([this, mapped, offset, area, trips, diag, trip_offset] {
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
		if (diag) {
			ProcessDiagWords(trip_offset + LoopTripBytes);
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

// Track F, F11d (ROADMAP p.376(v)): KYTY_DIAG_BVHNODES=1, the diagnostic words of one readback. The GPU
// counters are u32 and wrap: each is diffed against its last value modulo 2^32, exact while one interval
// (one readback, a frame with BDA work) adds less than 2^32 - max_step is the largest step seen. The last
// values start at 0, the value the tail holds after ClearLoopTripTail. [DiagOverMax] is a maximum and is
// taken as read. A line - cumulative totals - is printed when something grew, at most every 2 s and 1024
// times per process; a growth within the 2 s is printed by a later readback (m_diag_pending), so only the
// last 2 s before the process ends can go unprinted.
void FaultManager::ProcessDiagWords(uint64_t download_offset) {
	m_trip_download.Invalidate(download_offset, DiagBytes);
	std::array<uint32_t, LoopCap::DiagWords> words {};
	std::memcpy(words.data(), m_trip_download.Mapped().data() + download_offset, DiagBytes);
	for (uint32_t index = 0; index < LoopCap::DiagWords; index++) {
		if (index == LoopCap::DiagOverMax) {
			m_diag_pending |= words[index] != m_diag_last[index];
			m_diag_last[index]  = words[index];
			m_diag_total[index] = words[index];
			continue;
		}
		const uint32_t step = words[index] - m_diag_last[index];
		m_diag_last[index]  = words[index];
		m_diag_total[index] += step;
		m_diag_max_step = std::max<uint64_t>(m_diag_max_step, step);
		m_diag_pending |= step != 0;
	}
	const auto now_ms = static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
	                                              std::chrono::steady_clock::now().time_since_epoch())
	                                              .count());
	if (!m_diag_pending || m_diag_lines >= 1024 ||
	    (m_diag_lines != 0 && now_ms - m_diag_last_log_ms < 2000)) {
		return;
	}
	m_diag_pending     = false;
	m_diag_last_log_ms = now_ms;
	m_diag_lines++;
	const auto& total = m_diag_total;
	uint64_t    lanes = 0;
	for (uint32_t type = 0; type < 8; type++) {
		lanes += total[LoopCap::DiagT0 + type];
	}
	const auto bucket = [&](uint32_t cls, uint32_t index) {
		return total[LoopCap::DiagBuckets + 4 * cls + index];
	};
	LOGF("DiagBvhNodes: lanes=%" PRIu64 " t0=%" PRIu64 " t1=%" PRIu64 " t2=%" PRIu64 " t3=%" PRIu64
	     " t4=%" PRIu64 " t5=%" PRIu64 " t6=%" PRIu64 " t7=%" PRIu64 " size_viol=%" PRIu64
	     " size_off=%" PRIu64 " node64=%" PRIu64 " over_max=%" PRIu64 " b_tri=%" PRIu64 "/%" PRIu64
	     "/%" PRIu64 "/%" PRIu64 " b_box=%" PRIu64 "/%" PRIu64 "/%" PRIu64 "/%" PRIu64 " b_t7=%" PRIu64
	     "/%" PRIu64 "/%" PRIu64 "/%" PRIu64 " traps=%" PRIu64 " trap_lanes=%" PRIu64 " groups=%" PRIu64
	     " max_step=%" PRIu64 "\n",
	     lanes, total[LoopCap::DiagT0 + 0], total[LoopCap::DiagT0 + 1], total[LoopCap::DiagT0 + 2],
	     total[LoopCap::DiagT0 + 3], total[LoopCap::DiagT0 + 4], total[LoopCap::DiagT0 + 5],
	     total[LoopCap::DiagT0 + 6], total[LoopCap::DiagT0 + 7], total[LoopCap::DiagSizeViol],
	     total[LoopCap::DiagSizeOff], total[LoopCap::DiagNode64], total[LoopCap::DiagOverMax],
	     bucket(0, 0), bucket(0, 1), bucket(0, 2), bucket(0, 3), bucket(1, 0), bucket(1, 1), bucket(1, 2),
	     bucket(1, 3), bucket(2, 0), bucket(2, 1), bucket(2, 2), bucket(2, 3), total[LoopCap::DiagTraps],
	     total[LoopCap::DiagTrapLanes], total[LoopCap::DiagGroups], m_diag_max_step);
	std::string slots;
	for (uint32_t slot = 0; slot < LoopCap::DiagSlotCount; slot++) {
		if (total[LoopCap::DiagLanes + slot] != 0) {
			char text[64];
			std::snprintf(text, sizeof(text), " %016" PRIx64 "=%" PRIu64, LoopCap::DiagBvhSlotHash(slot),
			              total[LoopCap::DiagLanes + slot]);
			slots += text;
		}
	}
	LOGF("DiagBvhNodes: slots%s other=%" PRIu64 "\n", slots.c_str(),
	     total[LoopCap::DiagLanes + LoopCap::DiagSlotCount]);
}

} // namespace Libs::Graphics
