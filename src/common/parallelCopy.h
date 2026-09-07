#ifndef EMULATOR_SRC_COMMON_PARALLELCOPY_H_
#define EMULATOR_SRC_COMMON_PARALLELCOPY_H_

#include <cstddef>

namespace Common {

// memcpy spread over a small pool of worker threads (the caller participates). A single
// thread copies at ~7 GB/s on this machine; a scene cut of ASTRO BOT uploads 350-875 MB of
// texture data in one frame through the GuestGpu thread. Sizes below the threshold (or when
// the pool is disabled with KYTY_PARALLEL_COPY=0) fall back to std::memcpy.
void ParallelMemcpy(void* dst, const void* src, size_t size);

constexpr size_t PARALLEL_COPY_MIN_BYTES = 4u << 20u;

} // namespace Common

#endif // EMULATOR_SRC_COMMON_PARALLELCOPY_H_
