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
//
// Track P, iteration D1-1 (ROADMAP s122 item 346(g); docs/track-p/p30-hold.md): KYTY_PVAR_HOLD=1 - "cadence with a hold
// at M0", only with mode 2 armed. The writer keeps the target step kt (in [1, 3], 2 at the start) and the counter fit; at
// M0 the main guest thread waits until the vblank counter reaches v_prev + kt; k and the carry are Advance(d, c) as
// before. KYTY_PVAR_HOLD unset or 0 - the P23 path (no wait), the "PVar:" line only gains the K4 fields (kt=0 wait_us=0).
// Any other value, or 1 without armed mode 2 - "PVar: refused reason=hold" once and nothing else.
// Item 348(v) (P30b): all the times of the hold and of the "PVar:" line (the vblank time, M0, the wait, the deadline,
// slack_us, wait_us, exit_us, t_us) are one monotonic host clock in us from the process start, not the guest clock
// (KernelGetProcessTime stands still in the freezes and runs at the guest speed; the vblanks and the sleep are host time).

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

// Item 346(g)(2)-(3): the hold arithmetic. kt, fit - the writer state before this M0; d - vblanks between the two M0
// after the wait; slack_us - the time from this M0 (before the wait) to the vblank v_prev + kt.
//   d > kt (the frame is late)       -> kt = min(d, 3), fit = 0 (up at once; kt 3 stays 3);
//   else slack_us >= 18 667 (fits)  -> fit + 1, else fit = 0;
//        fit reaches 30 and kt > 1   -> kt - 1, fit = 0 (down at most once per 30 frames; at kt 1 fit stays at 30).
inline constexpr uint32_t HOLD_KT_START = 2;
inline constexpr uint32_t HOLD_KT_MAX   = 3;
inline constexpr uint32_t HOLD_FIT_N    = 30;
inline constexpr int64_t  HOLD_SLACK_US = 18667; // 1 vblank + 2 000 us

struct HoldStep {
	uint32_t kt   = HOLD_KT_START;
	uint32_t fit  = 0;
	uint32_t late = 0; // d > kt
	int32_t  move = 0; // +1 kt went up, -1 down, 0 unchanged
};

constexpr HoldStep Hold(uint32_t kt, uint32_t fit, uint64_t d, int64_t slack_us) {
	HoldStep s;
	s.kt  = kt;
	s.fit = fit;
	if (d > kt) {
		s.late = 1;
		s.kt   = d < HOLD_KT_MAX ? static_cast<uint32_t>(d) : HOLD_KT_MAX;
		s.fit  = 0;
		s.move = s.kt > kt ? 1 : 0;
		return s;
	}
	if (slack_us >= HOLD_SLACK_US) {
		s.fit = fit < HOLD_FIT_N ? fit + 1 : HOLD_FIT_N;
	} else {
		s.fit = 0;
	}
	if (s.fit >= HOLD_FIT_N && s.kt > 1) {
		s.kt   = s.kt - 1;
		s.fit  = 0;
		s.move = -1;
	}
	return s;
}

// The emulator time (us) of vblank `target` on the 60 Hz grid (Arm refuses other frequencies) from the last published
// vblank v at time t_v: t_v + (target - v) * 1 000 000 / 60, the quotient truncated toward zero; target may be below v.
constexpr int64_t VblankTimeUs(uint64_t t_v, uint64_t v, uint64_t target) {
	const auto dv = static_cast<int64_t>(target - v);
	return static_cast<int64_t>(t_v) + dv * 1000000 / 60;
}

// The wait at M0 (item 346(g)(1)): a sleep with polling of the published counter (the choice of the implementation).
// Returns 0 when the deadline has passed (the wait ends without the target vblank); otherwise the sleep before the next
// look at the counter: far from the predicted vblank - until HOLD_EARLY_US before it, near or past it - HOLD_POLL_US;
// never past the deadline. The deadline is M0 + kt vblanks + HOLD_CAP_US (vblanks stop at pause and exit).
inline constexpr int64_t HOLD_POLL_US  = 200;
inline constexpr int64_t HOLD_EARLY_US = 1000;
inline constexpr int64_t HOLD_CAP_US   = 50000;

constexpr int64_t HoldSleepUs(int64_t now, int64_t predicted, int64_t deadline) {
	if (now >= deadline) {
		return 0;
	}
	const int64_t rem   = predicted - now;
	int64_t       sleep = rem > HOLD_EARLY_US + HOLD_POLL_US ? rem - HOLD_EARLY_US : HOLD_POLL_US;
	if (sleep > deadline - now) {
		sleep = deadline - now;
	}
	return sleep;
}

// Item 348(v)(3): the wait at M0 as a pure function. vb - the last published vblank (count v, host time t, us);
// t0 - the host time of M0; target = v_prev + kt. now_us() - the host clock, sleep_us(us) - the sleep, read_vblank() -
// the published vblank (the emulator: steady_clock, Common::Thread::SleepMicro, the seqlock read). The target reached at
// M0 - no sleep, wait_us 0, exit_us 0. Otherwise sleep (HoldSleepUs), read the counter, read the clock, until the counter
// reaches the target (exit_us = the exit time minus the predicted time of the target vblank) or HoldSleepUs gives 0 at
// the deadline t0 + kt vblanks + HOLD_CAP_US (exit_us -1). wait_us - the exit time minus t0.
struct Vblank {
	uint64_t v = 0;
	uint64_t t = 0;
};

struct HoldWaitResult {
	Vblank  vb;          // the last read: d = vb.v - v_prev
	int64_t wait_us = 0; // 0 - no wait
	int64_t exit_us = 0; // after the target vblank; -1 - the wait ended at the deadline
};

template <typename NowFn, typename SleepFn, typename ReadFn>
HoldWaitResult HoldWait(int64_t t0, Vblank vb, uint64_t target, uint32_t kt, NowFn now_us, SleepFn sleep_us,
                        ReadFn read_vblank) {
	HoldWaitResult r;
	r.vb = vb;
	if (vb.v >= target) {
		return r;
	}
	const int64_t deadline = t0 + static_cast<int64_t>(kt) * 1000000 / 60 + HOLD_CAP_US;
	int64_t       now      = t0;
	bool          timeout  = false;
	for (;;) {
		const int64_t sleep = HoldSleepUs(now, VblankTimeUs(r.vb.t, r.vb.v, target), deadline);
		if (sleep <= 0) {
			timeout = true;
			break;
		}
		sleep_us(sleep);
		r.vb = read_vblank();
		now  = now_us();
		if (r.vb.v >= target) {
			break;
		}
	}
	r.wait_us = now - t0;
	r.exit_us = timeout ? -1 : now - VblankTimeUs(r.vb.t, r.vb.v, target);
	return r;
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
// VideoOutDriver::Impl::VblankEnd, after vblank_status.count++ of the first opened handle; also stores the time of
// the vblank (the host clock, us from the process start, item 348(v)(1)) for the hold (item 346(g)).
void PublishVblank(uint64_t count);
// FlipQueue::Flip, after flip_status.count++ (the key "n" of the PVar line, = "FrameTrace: n=").
void PublishFlip(uint64_t count);

#endif

} // namespace Libs::LibKernel::PVar

#endif /* EMULATOR_INCLUDE_EMULATOR_KERNEL_PVAR_H_ */
