#ifndef EMULATOR_SRC_COMMON_PARALLELCOPY_H_
#define EMULATOR_SRC_COMMON_PARALLELCOPY_H_

#include <cstddef>
#include <cstdint>

namespace Common {

// memcpy spread over a small pool of worker threads (the caller participates). A single
// thread copies at ~7 GB/s on this machine; a scene cut of ASTRO BOT uploads 350-875 MB of
// texture data in one frame through the GuestGpu thread. Sizes below the threshold (or when
// the pool is disabled with KYTY_PARALLEL_COPY=0) fall back to std::memcpy.
void ParallelMemcpy(void* dst, const void* src, size_t size);

// Queues the copy to the pool and returns at once (sizes below ASYNC_COPY_MIN_BYTES are copied
// inline). A staging region filled this way may be referenced by recorded GPU commands right
// away: CommandScheduler::Submit makes the queue wait for the chunks queued so far (timeline
// semaphore signalled by the pool, see below), or with KYTY_ASYNC_COPY_GPU_WAIT=0 blocks in
// WaitAsyncCopies() before vkQueueSubmit. The source must stay mapped until the copy landed
// (guest memory read through its backing view). KYTY_ASYNC_COPY=0 makes it synchronous.
void AsyncMemcpy(void* dst, const void* src, size_t size);
void WaitAsyncCopies();
[[nodiscard]] size_t PendingAsyncCopies();

// GPU-side completion of async copies (CommandScheduler::Submit): pool chunks are numbered in
// queue order. AsyncCopySequence() is the number queued so far; AsyncCopyCompleted() the
// low-water mark below which every chunk has landed. A submit that references staging filled by
// chunks < S makes the GPU wait for a timeline semaphore to reach S instead of blocking the
// GuestGpu thread: AddAsyncCopySignal registers a host signal (called from a copy thread with a
// strictly increasing completed mark; every registered signal gets every mark - there is one
// CommandScheduler per RenderContext and the emulator creates two) and RequestAsyncCopySignal(S)
// asks for a signal once the mark reaches S. It returns true when S is already complete (no wait
// needed). RemoveAsyncCopySignal before the semaphore behind a signal is destroyed.
[[nodiscard]] uint64_t AsyncCopySequence();
[[nodiscard]] uint64_t AsyncCopyCompleted();
void                   AddAsyncCopySignal(void (*signal)(uint64_t completed, void* user), void* user);
void                   RemoveAsyncCopySignal(void (*signal)(uint64_t completed, void* user), void* user);
[[nodiscard]] bool     RequestAsyncCopySignal(uint64_t sequence);

constexpr size_t PARALLEL_COPY_MIN_BYTES = 4u << 20u;
constexpr size_t ASYNC_COPY_MIN_BYTES    = 64u << 10u;

} // namespace Common

#endif // EMULATOR_SRC_COMMON_PARALLELCOPY_H_
