#ifndef GRAPHICS_GUEST_GPU_SLICE_CENSUS_H
#define GRAPHICS_GUEST_GPU_SLICE_CENSUS_H

#include <cstdint>

// Session 118, gate "slicecen" (route A stage 4 part 2, docs/session-118/designA4_part2.md; MEASUREMENT ONLY): the
// census of how a frame could be cut into slices.  Elements (draw/dispatch packets) are counted in
// CommandProcessor::ProcessPm4Range, host render-pass starts in CommandBuffer::BeginRenderingImpl, and the images every
// element touches in PrepareBindings (written = storage) and AcquireRenderTargets (written).  At each frame change the
// GuestGpu thread computes K3 (element runs between pass starts) and K4 (image overlap of adjacent segments at W = 2 and
// W = 4) into FrameTrace-x counters.  Every call does nothing unless the gate is on, frame tracing is enabled and the
// caller is the GuestGpu thread.  Implemented in graphicsRun.cpp.
namespace Libs::Graphics::SliceCensus {

void Element(int frame);
void PassBegin();
void Image(uint32_t image_index, bool write);

} // namespace Libs::Graphics::SliceCensus

#endif // GRAPHICS_GUEST_GPU_SLICE_CENSUS_H
