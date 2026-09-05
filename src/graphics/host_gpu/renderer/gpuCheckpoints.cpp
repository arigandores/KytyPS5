#include "graphics/host_gpu/renderer/gpuCheckpoints.h"

#include "common/logging/log.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/cache/streamBuffer.h"
#include "graphics/host_gpu/renderer/commandScheduler.h"

#include <array>
#include <atomic>
#include <cinttypes>
#include <cstdio>
#include <cstring>
#include <vector>

namespace Libs::Graphics {

namespace {

struct CheckpointRecord {
	uint64_t sequence  = 0;
	uint64_t submit_id = 0;
	uint64_t arg4      = 0;
	uint64_t arg5      = 0;
	uint32_t op        = 0;
	uint32_t arg0      = 0;
	uint32_t arg1      = 0;
	uint32_t arg2      = 0;
	uint32_t arg3      = 0;
};

// NV checkpoint markers must stay valid until the queue is inspected after a device loss.
constexpr size_t RingSize = size_t {1} << 17;

std::array<CheckpointRecord, RingSize> g_ring {};
std::atomic<uint64_t>                  g_sequence {0};

// Host-visible breadcrumb buffer. Deliberately never destroyed: it is only created in the debug
// mode and must stay readable while the device loss is being reported.
Buffer*           g_breadcrumbs = nullptr;
constexpr uint64_t BreadcrumbSize = 64;

const char* OpName(uint32_t op) {
	switch (op) {
		case 0: return "DispatchDirect";
		case 1: return "DrawIndex";
		case 2: return "DrawIndexAuto";
		case 3: return "EopWrite";
		case 4: return "EopInterrupt";
		case 5: return "EopWriteBack";
		case 6: return "EopFlip";
		case 7: return "EopWriteBackFlip";
		case 8: return "EopOnlyFlip";
		case 9: return "DrawComplete";
		default: return "Unknown";
	}
}

void Print(const char* stage, const CheckpointRecord& record) {
	// Draws: args=phase,index_count,instance_count,first_instance ps=<hash> vs=<hash>.
	// Dispatches: args=x,y,z,mode ps=<cs hash>.
	LOGF("GpuCheckpoint %s: seq=%" PRIu64 " op=%s(%u) submit=%" PRIu64
	     " args=%u,%u,%u,0x%08x ps=0x%016" PRIx64 " vs=0x%016" PRIx64 "\n",
	     stage, record.sequence, OpName(record.op), record.op, record.submit_id, record.arg0,
	     record.arg1, record.arg2, record.arg3, record.arg4, record.arg5);
	std::printf("GpuCheckpoint %s: seq=%" PRIu64 " op=%s(%u) submit=%" PRIu64
	            " args=%u,%u,%u,0x%08x ps=0x%016" PRIx64 " vs=0x%016" PRIx64 "\n",
	            stage, record.sequence, OpName(record.op), record.op, record.submit_id,
	            record.arg0, record.arg1, record.arg2, record.arg3, record.arg4, record.arg5);
}

} // namespace

void RecordGpuCheckpoint(GraphicContext& graphics, CommandScheduler& scheduler,
                         vk::CommandBuffer command, bool inside_rendering, uint32_t op,
                         uint64_t submit_id, uint32_t arg0, uint32_t arg1, uint32_t arg2,
                         uint32_t arg3, uint64_t arg4, uint64_t arg5) {
	if ((!graphics.gpu_breadcrumbs_enabled && !graphics.diagnostic_checkpoints_enabled) ||
	    command == nullptr) {
		return;
	}
	const auto sequence = g_sequence.fetch_add(1, std::memory_order_relaxed) + 1;
	auto&      record   = g_ring[sequence % RingSize];
	record              = {sequence, submit_id, arg4, arg5, op, arg0, arg1, arg2, arg3};

	// vkCmdUpdateBuffer must be recorded outside a render pass instance.
	if (graphics.gpu_breadcrumbs_enabled && !inside_rendering) {
		if (g_breadcrumbs == nullptr) {
			g_breadcrumbs = new Buffer(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,
			                           BreadcrumbSize);
			SetVulkanObjectNameF(graphics.device, g_breadcrumbs->Handle(), "GPU Breadcrumbs");
		}
		static_assert(sizeof(CheckpointRecord) <= BreadcrumbSize);
		command.updateBuffer(g_breadcrumbs->Handle(), 0, sizeof(record), &record);
	}
	if (graphics.diagnostic_checkpoints_enabled) {
		command.setCheckpointNV(&record);
	}
}

void ReportGpuCheckpoints(GraphicContext& graphics) {
	if (graphics.gpu_breadcrumbs_enabled && g_breadcrumbs != nullptr &&
	    !g_breadcrumbs->Mapped().empty()) {
		g_breadcrumbs->Invalidate(0, BreadcrumbSize);
		CheckpointRecord record {};
		std::memcpy(&record, g_breadcrumbs->Mapped().data(), sizeof(record));
		Print("breadcrumb (last started, never completed)", record);
		const auto latest = g_sequence.load(std::memory_order_relaxed);
		LOGF("GpuCheckpoint: latest recorded seq=%" PRIu64 " (%" PRIu64 " operations recorded after the breadcrumb)\n",
		     latest, latest >= record.sequence ? latest - record.sequence : 0);
		std::printf("GpuCheckpoint: latest recorded seq=%" PRIu64 "\n", latest);
	}

	if (graphics.diagnostic_checkpoints_enabled && graphics.queue != nullptr) {
		uint32_t count = 0;
		graphics.queue.getCheckpointDataNV(&count, nullptr);
		if (count == 0) {
			LOGF("GpuCheckpoint: no NV checkpoint data available\n");
		} else {
			std::vector<vk::CheckpointDataNV> data(count);
			for (auto& entry: data) {
				entry.sType = vk::StructureType::eCheckpointDataNV;
				entry.pNext = nullptr;
			}
			graphics.queue.getCheckpointDataNV(&count, data.data());
			for (uint32_t i = 0; i < count; i++) {
				const auto* marker = static_cast<const CheckpointRecord*>(data[i].pCheckpointMarker);
				const char* stage =
				    data[i].stage == vk::PipelineStageFlagBits::eBottomOfPipe ? "nv bottom-of-pipe"
				    : data[i].stage == vk::PipelineStageFlagBits::eTopOfPipe ? "nv top-of-pipe"
				                                                              : "nv other-stage";
				const bool in_ring = marker >= g_ring.data() && marker < g_ring.data() + g_ring.size();
				if (!in_ring) {
					LOGF("GpuCheckpoint %s: foreign marker %p\n", stage,
					     static_cast<const void*>(marker));
					continue;
				}
				Print(stage, *marker);
			}
		}
	}
	std::fflush(stdout);
}

} // namespace Libs::Graphics
