#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_GPUCHECKPOINTS_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_GPUCHECKPOINTS_H_

#include "graphics/host_gpu/vulkanCommon.h"

#include <cstdint>

namespace Libs::Graphics {

struct GraphicContext;
class CommandScheduler;

// GPU progress markers for attributing a device loss to the draw or dispatch that hung
// (enabled with KYTY_GPU_CHECKPOINTS=1):
//  - breadcrumbs: before every operation vkCmdUpdateBuffer writes its description into a
//    host-visible buffer; the write is ordered after the previous operation by the barriers that
//    already follow each draw/dispatch (and, in this mode, by an extra all-commands barrier and a
//    DrawComplete marker after every draw), so after a device loss the buffer names the operation
//    that started last and never completed. vkCmdUpdateBuffer is illegal inside a render pass
//    instance, so markers recorded while rendering skip the breadcrumb write;
//  - VK_NV_device_diagnostic_checkpoints markers, when the extension is available.
void RecordGpuCheckpoint(GraphicContext& graphics, CommandScheduler& scheduler,
                         vk::CommandBuffer command, bool inside_rendering, uint32_t op,
                         uint64_t submit_id, uint32_t arg0, uint32_t arg1, uint32_t arg2,
                         uint32_t arg3, uint64_t arg4, uint64_t arg5);
void ReportGpuCheckpoints(GraphicContext& graphics);

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_GPUCHECKPOINTS_H_
