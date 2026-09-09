#ifndef EMULATOR_SRC_COMMON_PARALLELCOPY_H_
#define EMULATOR_SRC_COMMON_PARALLELCOPY_H_

#include <cstddef>

namespace Common {

// memcpy spread over a small pool of worker threads (the caller participates). A single
// thread copies at ~7 GB/s on this machine; a scene cut of ASTRO BOT uploads 350-875 MB of
// texture data in one frame through the GuestGpu thread. Sizes below the threshold (or when
// the pool is disabled with KYTY_PARALLEL_COPY=0) fall back to std::memcpy.
void ParallelMemcpy(void* dst, const void* src, size_t size);

// Queues the copy to the pool and returns at once (sizes below ASYNC_COPY_MIN_BYTES are copied
// inline). The bytes at dst are complete after the next WaitAsyncCopies(), which CommandScheduler
// calls before every vkQueueSubmit - so a staging region filled this way may be referenced by
// recorded GPU commands right away. The source must stay mapped until then (guest memory read
// through its backing view). KYTY_ASYNC_COPY=0 makes it synchronous.
void AsyncMemcpy(void* dst, const void* src, size_t size);
void WaitAsyncCopies();
[[nodiscard]] size_t PendingAsyncCopies();

constexpr size_t PARALLEL_COPY_MIN_BYTES = 4u << 20u;
constexpr size_t ASYNC_COPY_MIN_BYTES    = 64u << 10u;

} // namespace Common

#endif // EMULATOR_SRC_COMMON_PARALLELCOPY_H_
