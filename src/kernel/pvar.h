#ifndef EMULATOR_INCLUDE_EMULATOR_KERNEL_PVAR_H_
#define EMULATOR_INCLUDE_EMULATOR_KERNEL_PVAR_H_

// Track P, P-var iteration 1 (ROADMAP s122 items 276(e)(1), 283(v), 284(v)-(i); design docs/track-p/p12-pvar.md).
// KYTY_PVAR=2 writes the game's step k/60 into six guest cells at the start of the main thread's frame function (marker
// M0: the call of sceKernelGetProcessTimeCounter that returns to base + 0x2a352a). k comes from the emulator's vblanks
// between two M0 with a negative carry. KYTY_PVAR unset or 0 - the old path: the wrappers are not registered, nothing is
// written to guest memory and no line is logged. Any other value - "PVar: refused reason=value", also no wrappers.
// The ASTRO BOT PPSA21564 eboot only: the cells, the marker and the patch bytes are addresses of that image.
//
// The arithmetic part needs only the standard library: the P14 fixture (C:/kyty/p283/p14/test_pvar.cpp) compiles this
// header with KYTY_PVAR_ARITHMETIC_ONLY, without the project configuration.

#ifndef KYTY_PVAR_ARITHMETIC_ONLY
#include "common/abi.h"
#endif

#include <bit>
#include <cstdint>

namespace Libs::LibKernel::PVar {

// Item 284(v): d - vblanks between two M0, c - the carry before (in [-3, 0]).
//   o = d + c;  k = min(max(o, 1), 3);  c' = max(min(0, o - k), -3)
//   lost = max(0, o - k) - vblanks the clamp drops (counter pvar_lost);
//   over = c' - min(0, o - k) - vblanks below -3 the carry drops, i.e. given to the game in excess (counter pvar_over).
// Per step k = d + c - c' - lost + over, so over a window
//   sum k = sum d - sum lost + sum over + c(before the first) - c(after the last).
struct Step {
	uint32_t k    = 1;
	int32_t  c    = 0;
	uint64_t lost = 0;
	uint64_t over = 0;
};

constexpr Step Advance(uint64_t d, int32_t c) {
	// d is a difference of a 64-bit vblank counter; a run shorter than 2^62 vblanks fits int64.
	const int64_t o     = static_cast<int64_t>(d) + c;
	const int64_t k     = o < 1 ? 1 : (o > 3 ? 3 : o);
	const int64_t rest  = o - k;
	const int64_t c_raw = rest < 0 ? rest : 0;
	const int64_t c_new = c_raw < -3 ? -3 : c_raw;
	Step          s;
	s.k    = static_cast<uint32_t>(k);
	s.c    = static_cast<int32_t>(c_new);
	s.lost = static_cast<uint64_t>(rest > 0 ? rest : 0);
	s.over = static_cast<uint64_t>(c_new - c_raw);
	return s;
}

// The step cells for k (the formulas of the game's SetFrameRate 0x34c0, design section 3.3): fps = 60.0 / k;
// cell 1 (base + 0x8fd4040) double fps; cell 2 (base + 0x8fd4048) float (float)(1.0 / fps); cell 3 (base + 0x8fd4050)
// u64 (u64)(1e6 / fps); cell 4 (base + 0x834f34c) and the two static copies (base + 0xe7d65e8, base + 0xeb9ef4c) - the
// same float as cell 2.
struct Cells {
	uint64_t fps_bits = 0; // double
	uint32_t step_f32 = 0; // float
	uint64_t step_us  = 0;
};

inline Cells CellsFor(uint32_t k) {
	const double fps  = 60.0 / static_cast<double>(k);
	const auto   step = static_cast<float>(1.0 / fps);
	Cells        c;
	c.fps_bits = std::bit_cast<uint64_t>(fps);
	c.step_f32 = std::bit_cast<uint32_t>(step);
	c.step_us  = static_cast<uint64_t>(1000000.0 / fps);
	return c;
}

// Guest addresses relative to the main module base.
inline constexpr uint64_t CELL_FPS     = 0x8fd4040;
inline constexpr uint64_t CELL_STEP    = 0x8fd4048;
inline constexpr uint64_t CELL_STEP_US = 0x8fd4050;
inline constexpr uint64_t CELL_LIT     = 0x834f34c;
inline constexpr uint64_t CELL_COPY_A  = 0xe7d65e8;
inline constexpr uint64_t CELL_COPY_B  = 0xeb9ef4c;
inline constexpr uint64_t M0_RETURN    = 0x2a352a;
inline constexpr uint64_t LIMITER      = 0x2a470b;
inline constexpr uint64_t HAVOK        = 0x687375;

// Item 283(v)(6): the 25 bytes of the limiter decoupling and the 4 bytes of the Havok patch the arming requires.
inline constexpr uint8_t LIMITER_BYTES[25] = {0xc5, 0xfb, 0x10, 0x05, 0x1d, 0xdd, 0x0a, 0x08, 0xc5, 0xfb, 0x59, 0x05, 0xb5,
                                              0xc4, 0x0a, 0x08, 0xc5, 0xf2, 0x5a, 0x8d, 0x40, 0xff, 0xff, 0xff, 0x90};
inline constexpr uint8_t HAVOK_BYTES[4]    = {0xe7, 0x90, 0xcb, 0x07};

#ifndef KYTY_PVAR_ARITHMETIC_ONLY

// KYTY_PVAR, read once per process: 0 - unset, empty or "0"; 2 - "2"; -1 - anything else (refused, as 0).
int Mode();

// Registered under fgxnMeTNUtY (sceKernelGetProcessTimeCounter) when Mode() == 2; the same value as
// KernelGetProcessTimeCounter, plus the write at M0 once armed.
uint64_t KYTY_SYSV_ABI GetProcessTimeCounter();

// Once, after the KYTY_POKE block and before the guest entry point: prints "PVar: armed ..." or "PVar: refused ...".
// Nothing at Mode() == 0.
void Arm(uint64_t base);

// Present thread: whether the two publications below are wanted (armed only).
bool Publishing();
// VideoOutDriver::Impl::VblankEnd, after vblank_status.count++ of the first opened handle.
void PublishVblank(uint64_t count);
// FlipQueue::Flip, after flip_status.count++ (the key "n" of the PVar line, = "FrameTrace: n=").
void PublishFlip(uint64_t count);

#endif

} // namespace Libs::LibKernel::PVar

#endif /* EMULATOR_INCLUDE_EMULATOR_KERNEL_PVAR_H_ */
