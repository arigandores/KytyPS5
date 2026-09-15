#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_SHADOWRESOLVE_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_SHADOWRESOLVE_H_

#include "graphics/host_gpu/renderer/cache/bufferCache.h"
#include "graphics/host_gpu/renderer/cache/textureCache.h"

#include <array>
#include <cstdint>

namespace Libs::Graphics {

class RenderContext;

// Session 64, measurements E4 and E6 of docs/parallel-draw-path.md before M2 (C4):
//  - knob "shadowresolve" = K (KYTY_SHADOW_RESOLVE, default 0): K worker threads repeat the
//    read-only part of every graphics draw's binding resolution - the memo-hit checks of the
//    sampled images and the epoch / memo answers of the storage buffers - and throw the result
//    away. What the sweep measures is the tax those readers put on the GuestGpu thread (cache
//    lines they share with it, TextureCache::m_lock, the tracker's region locks): E4 of the plan.
//  - gate "shadowinline" (KYTY_SHADOW_INLINE, default 0): the same reads run once more on the
//    GuestGpu thread itself, right after PrepareGraphicsBindings. The CPU per draw it adds is the
//    gross cost of the read-only resolution on the critical path - the most M2 could take off it
//    (E6: the "compute twice, discard the second" coefficient).
// The job carries what the draw resolved (image ids, the desc fields the checks read, the memo
// view stamp, buffer ids and ranges), never pointers into the draw's own storage. A worker reads
// the texture cache under its lock (TextureCache::ShadowProbe) and the buffer cache without one
// (BufferCache::ShadowProbe, the cache has none - a measurement, not a production path).
namespace ShadowResolve {

struct BufferQuery {
	uint64_t address = 0;
	uint64_t size    = 0;
	BufferId id;
	bool     written = false;
};

constexpr uint32_t MaxImages  = 48;
constexpr uint32_t MaxBuffers = 48;

struct Job {
	RenderContext* context      = nullptr;
	uint32_t       image_count  = 0;
	uint32_t       buffer_count = 0;
	std::array<TextureCache::ShadowImageQuery, MaxImages> images {};
	std::array<BufferQuery, MaxBuffers>                   buffers {};
};

// The reads of one draw; counts into FrameTrace-x (sh_*). inline_run: charged to sh_inline_us
// instead of sh_us.
void Run(const Job& job, bool inline_run);
// GuestGpu thread: hands the job to the workers (starts them on the first call with the knob
// set). False when the ring is full (the job is dropped, counted as sh_drop).
bool Push(const Job& job);
// Joins the workers (RenderContext destruction).
void Stop();

} // namespace ShadowResolve

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_SHADOWRESOLVE_H_
