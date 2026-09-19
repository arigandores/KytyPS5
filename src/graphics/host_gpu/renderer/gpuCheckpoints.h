#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_GPUCHECKPOINTS_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_GPUCHECKPOINTS_H_

#include "graphics/host_gpu/vulkanCommon.h"

#include <cstdint>

namespace Libs::Graphics {

struct GraphicContext;
class CommandScheduler;
struct SubmitInfo;

// GPU progress markers for attributing a device loss to the draw or dispatch that hung
// (enabled with KYTY_GPU_CHECKPOINTS=1):
//  - breadcrumbs: before every operation vkCmdUpdateBuffer writes its description into a
//    host-visible buffer; the write is ordered after the previous operation by the barriers that
//    already follow each draw/dispatch (and, in this mode, by an extra all-commands barrier and a
//    DrawComplete marker after every draw), so after a device loss the buffer names the operation
//    that started last and never completed. vkCmdUpdateBuffer is illegal inside a render pass
//    instance, so markers recorded while rendering skip the breadcrumb write;
//  - VK_NV_device_diagnostic_checkpoints markers, when the extension is available.
// KYTY_GPU_CHECKPOINTS=nv records only NV markers, without bracketing draw barriers.
// GPU checkpoint data is queried only after DeviceLost, as required by Vulkan.
void RecordGpuCheckpoint(GraphicContext& graphics, CommandScheduler& scheduler,
                         vk::CommandBuffer command, bool inside_rendering, uint32_t op,
                         uint64_t submit_id, uint32_t arg0, uint32_t arg1, uint32_t arg2,
                         uint32_t arg3, uint64_t arg4, uint64_t arg5);
void ReportGpuCheckpoints(GraphicContext& graphics); // = ReportGpuBreadcrumb + ReportNvCheckpoints
// The breadcrumb half: an Invalidate + memcpy of the mapped buffer, safe at any time.
void ReportGpuBreadcrumb(GraphicContext& graphics);
// The NV half: vkGetQueueCheckpointDataNV is valid ONLY after the device was lost.
void ReportNvCheckpoints(GraphicContext& graphics);
// CPU recording history only: safe before device loss. This is not GPU completion data.
void ReportGpuCheckpointHistory();

// KYTY_QUEUE_TRACE: bounded CPU history of queue.submit arguments/results. No GPU
// markers or driver inspection; entries do not prove that the GPU completed a submit.
bool GpuQueueTraceEnabled();
void RecordGpuSubmission(const void* scheduler, vk::Semaphore master, uint64_t tick,
                         const SubmitInfo& submit, bool returned, vk::Result result);
void ReportGpuSubmissionHistory();

// Session 98 (patch_s98b, MEASUREMENT ONLY; C:/kyty/s98/design98/SPEC_patch98.md Part G).
// KYTY_GPU_MARKERS=1 with VK_AMD_buffer_marker: every game draw / dispatch is one op with a
// per-scheduler sequence number seq (u32, from 1).  vkCmdWriteBufferMarkerAMD writes seq into
// top[seq % N] at TOP_OF_PIPE right before the draw/dispatch command and into bot[seq % N] at
// BOTTOM_OF_PIPE right after it (no barrier, no pass break: legal inside a render pass), in one
// host-visible buffer per scheduler (N = 65536 slots each, filled with 0xFFFFFFFF, never
// destroyed).  A CPU op ring (same slot index) keeps what each op was: tick, kind, cs/vs/ps hash,
// args, the bindfloor latch, the real-GDS-barrier flag.  ReportGpuMarkers reads both while the
// process is alive (GpuWaitSlow / GpuHangAbort) and after a device loss, and names the op that
// started and never completed.  KYTY_QUEUE_TRACE=2 fills the CPU ring without GPU markers.
enum class GpuMarkerKind : uint32_t {
	Draw = 1,
	DrawIndexed,
	DrawIndirect,
	DrawIndexedIndirect,
	Mesh,
	Dispatch,
	DispatchIndirect,
};
// buffer == null: no GPU marker for this op (markers off, or KYTY_QUEUE_TRACE=2 only).
// Session 98 (patch_s98c): KYTY_GPU_MARKERS=2 also writes pre[seq % N] (a third array) at
// BOTTOM_OF_PIPE right before the op's command: written only once EVERY command recorded before
// it completed, which TOP_OF_PIPE (written when the command processor reaches it) does not show.
struct GpuMarkerSite {
	vk::Buffer     buffer = nullptr;
	vk::DeviceSize top    = 0;
	vk::DeviceSize bottom = 0;
	vk::DeviceSize pre    = 0;
	uint32_t       seq    = 0;
	bool           pre_on = false;
};
// True when ops are described (markers enabled, or KYTY_QUEUE_TRACE=2).  Written before the
// first command buffer exists, read-only afterwards: the only per-op cost when it is false.
extern bool g_gpu_ops_active;
[[nodiscard]] inline bool GpuOpsActive() noexcept { return g_gpu_ops_active; }
// KYTY_GPU_MARKERS set to anything but "0" (read once).
[[nodiscard]] bool GpuMarkersRequested();
// Device creation: the extension was enabled and vkCmdWriteBufferMarkerAMD loaded (or not).
void GpuMarkersSetEnabled(bool enabled);
// CommandScheduler constructor / destructor (index assignment; storage is allocated lazily).
void GpuMarkersRegisterScheduler(CommandScheduler* scheduler);
void GpuMarkersUnregisterScheduler(CommandScheduler* scheduler);
// Call only when GpuOpsActive(), immediately before the op's draw/dispatch command(s).
[[nodiscard]] GpuMarkerSite GpuMarkerBegin(CommandScheduler& scheduler, GpuMarkerKind kind,
                                           uint64_t submit_id, uint64_t h0, uint64_t h1,
                                           uint32_t a0, uint32_t a1, uint32_t a2,
                                           bool floor_armed);
// CommitBindings' real GDS-barrier branch: the next op of this thread carries gds=1.
void GpuMarkerNoteGds();
// Sink: vk::CommandBuffer (direct path, default dispatcher) or RecordCommandWriter (recpack).
template <typename Sink>
inline void GpuMarkerTop(Sink& sink, const GpuMarkerSite& site) {
	if (site.buffer != nullptr) {
		if (site.pre_on) { // Session 98 (patch_s98c): KYTY_GPU_MARKERS=2 only
			sink.writeBufferMarkerAMD(vk::PipelineStageFlagBits::eBottomOfPipe, site.buffer,
			                          site.pre, site.seq);
		}
		sink.writeBufferMarkerAMD(vk::PipelineStageFlagBits::eTopOfPipe, site.buffer, site.top,
		                          site.seq);
	}
}
template <typename Sink>
inline void GpuMarkerBottom(Sink& sink, const GpuMarkerSite& site) {
	if (site.buffer != nullptr) {
		sink.writeBufferMarkerAMD(vk::PipelineStageFlagBits::eBottomOfPipe, site.buffer,
		                          site.bottom, site.seq);
	}
}
// Every guest flip packet (GuestGpu): gm_unsup, and the positive control gm_ok / gm_bad.
void GpuMarkersFlip();
// tag: "slow", "abort", "lost", "fatal".  Prints to the log and stdout, flushes both.
void ReportGpuMarkers(const char* tag, bool device_lost);

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_GPUCHECKPOINTS_H_
