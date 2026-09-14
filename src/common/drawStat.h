#ifndef EMULATOR_SRC_COMMON_DRAWSTAT_H_
#define EMULATOR_SRC_COMMON_DRAWSTAT_H_

#include <atomic>
#include <bit>
#include <cstdint>

// Session 57, E1/E2/E9 (gate "drawstat"): what a draw's resolution mutates, measured before any
// resolution work moves to other threads. The primitives that change shared renderer state call
// Mark with their category; RenderExecutor resets the mask when a draw takes the render mutex,
// shifts it to the tail range at AcquireRenderTargets and counts it when the draw command is
// recorded. Cut notes a hard boundary for the run lengths of E2.
//
// Header-only and free of other symbols: Mark runs inside the page manager (guest fault handlers
// included, where the thread-local needs no TLS guard) and inside the LRU cache template.
namespace Common::DrawStat {

// Hard: a pre-resolver thread must give the draw up.
inline constexpr uint32_t ImgNew   = 1u << 0u;  // host image inserted, freed or copied into another
inline constexpr uint32_t ImgUp    = 1u << 1u;  // image upload/clear, source or maybe-dirty state change
inline constexpr uint32_t Meta     = 1u << 2u;  // DCC/CMASK/HTile metadata state
inline constexpr uint32_t Prot     = 1u << 3u;  // page watchers (host protection)
inline constexpr uint32_t BufNew   = 1u << 4u;  // host buffer created (overlaps joined)
inline constexpr uint32_t BufUp    = 1u << 5u;  // buffer upload, GPU copy or image download into a buffer
inline constexpr uint32_t GpuWrite = 1u << 6u;  // guest memory marked GPU-written
inline constexpr uint32_t ObjNew   = 1u << 7u;  // image view, sampler, program or pipeline created
inline constexpr uint32_t Sync     = 1u << 8u;  // submit, blocking GPU wait, download drain
// Slow: read-only, but off the memo / upload-epoch fast path (under a cache lock).
inline constexpr uint32_t TexSlow  = 1u << 9u;  // FindImage / FindTexture / sampler map
inline constexpr uint32_t BufSlow  = 1u << 10u; // ObtainBuffer through FindBuffer + SynchronizeBuffer
// Deferrable: could be replayed on the critical thread.
inline constexpr uint32_t Lru      = 1u << 11u; // LRU entry moved (first touch in a GC tick)
inline constexpr uint32_t Memo     = 1u << 12u; // texture / render-target memo slot written
inline constexpr uint32_t M1       = 1u << 13u; // DrawAhead slot taken or retired
inline constexpr uint32_t Stream   = 1u << 14u; // stream ring wrapped
// Hard as well: a barrier in the preparation.
inline constexpr uint32_t Barrier  = 1u << 15u; // image transit or GDS barrier issued

inline constexpr uint32_t HardMask  = 0x81ffu;
inline constexpr uint32_t SlowMask  = TexSlow | BufSlow;
inline constexpr uint32_t DeferMask = Lru | Memo | M1 | Stream;

// E2 boundaries.
inline constexpr uint32_t EdgePass     = 1u << 0u; // an open render pass was closed
inline constexpr uint32_t EdgeDispatch = 1u << 1u;
inline constexpr uint32_t EdgeBarrier  = 1u << 2u;
inline constexpr uint32_t EdgeUpload   = 1u << 3u;
inline constexpr uint32_t EdgeSubmit   = 1u << 4u;

inline constinit std::atomic<bool>     g_on {false};
inline constinit thread_local uint32_t t_mask  = 0; // bits [0,16): preparation, [16,32): tail
inline constinit thread_local uint32_t t_shift = 0;
inline constinit thread_local uint32_t t_edges = 0;
// Marks between two counted draws (after a draw command, early exits, dispatches), both zones.
inline constinit thread_local uint32_t t_between = 0;
// Session 61 (item 2 ceiling, always on): draws and dispatches started by this thread. A buffer
// upload that finds it unchanged since the previous upload followed that upload back to back.
inline constinit thread_local uint32_t t_ops = 0;

[[nodiscard]] inline bool On() noexcept {
	return g_on.load(std::memory_order_relaxed);
}

inline void Mark(uint32_t bits) noexcept {
	if (On()) [[unlikely]] {
		t_mask |= bits << t_shift;
	}
}

inline void Cut(uint32_t edges) noexcept {
	if (On()) [[unlikely]] {
		t_edges |= edges;
	}
}

// Histogram bucket of a run length (>= 1): 1 | 2-3 | 4-7 | 8-15 | 16-31 | 32-63 | 64+.
[[nodiscard]] inline constexpr uint32_t RunBucket(uint32_t run) noexcept {
	const auto bucket = static_cast<uint32_t>(std::bit_width(run)) - 1u;
	return bucket < 6u ? bucket : 6u;
}

} // namespace Common::DrawStat

#endif // EMULATOR_SRC_COMMON_DRAWSTAT_H_
