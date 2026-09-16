#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_GPUDIRTYGEN_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_GPUDIRTYGEN_H_

#include <atomic>
#include <cstdint>

namespace Libs::Graphics::GpuDirtyGen {

// Session 74, W8. A monotonic witness for "something that was GPU-clean has become GPU-dirty".
//
// It exists so that a table of GPU-CLEAN page verdicts could outlive the call that built it, the
// way ShaderReadCache's live table outlives it under Memory::BackingMapEpoch. IsGpuCleanRange
// (kernel/memory.cpp) reads the guest map, BufferCache::HasGpuDirtyBytes and
// TextureCache::IsRegionGpuModified and nothing else, so two witnesses cover the whole predicate:
// the backing map epoch for the map half and this counter for the GPU-dirty half. (It also reads
// g_gpu_resources and IsGpuThread; both are answered by the call being on GuestGpu at all, which
// is the only thread that stores a clean verdict.)
//
// Bumped ONLY on real clean -> dirty transitions, and only AFTER the state change is in place:
// inside Image::MarkGpuModified when the flag was false, and at the one m_gpu_modified_ranges.Add
// when the covered set actually grew. Measured on base74a: 44.8 bumps a frame against 8 700 clean
// tables built, i.e. 0.515 %. The naive form that bumps on every CALL is refuted by the same run -
// renderDraw.cpp:812 alone fires 17 376 times a frame, 2.00 times per table - and must never be
// written.
//
// The dirty -> clean direction (RangeSet::Subtract, Image::ClearGpuModified) deliberately does NOT
// bump: it can only make a cached CLEAN verdict more true.
//
// Relaxed throughout. Every mutation site runs on GuestGpu inside the render mutex and the only
// reader today is on the same thread; the atomic is here so that a future off-thread reader is not
// a data race. Such a reader would want release/acquire, which is why the bump is ordered after the
// state change at both sites.

inline constinit std::atomic<uint64_t> g_generation {1};

inline void Bump() noexcept {
	g_generation.fetch_add(1, std::memory_order_relaxed);
}

[[nodiscard]] inline uint64_t Read() noexcept {
	return g_generation.load(std::memory_order_relaxed);
}

} // namespace Libs::Graphics::GpuDirtyGen

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_GPUDIRTYGEN_H_
