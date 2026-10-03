#include "kernel/pvar.h"

#include "common/emulatorConfig.h"
#include "common/frameStats.h"
#include "common/logging/log.h"
#include "common/threads.h"
#include "kernel/pthread.h"
#include "loader/gamePatchFile.h"

#include <atomic>
#include <chrono>
#include <cinttypes>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <string>

// Track P, P-var iteration 1 - see kernel/pvar.h. Threads: Arm - the loader thread before the guest entry point;
// PublishVblank / PublishFlip - the Present thread; GetProcessTimeCounter - any guest thread, the write only on the
// thread of the first M0 (the writer), so the writer state below is touched by one thread only.

namespace Libs::LibKernel::PVar {

namespace {

namespace FS = Common::FrameStats;

// Zero until armed: the wrapper compares every return address with it, so a refused or unarmed process never writes.
std::atomic<uint64_t> g_m0_ra {0};
std::atomic<uint64_t> g_base {0};
std::atomic<bool>     g_publish {false};
// vblank_status.count of the first opened video-out handle and flip_status.count, published by the Present thread.
std::atomic<uint64_t> g_vb {0};
std::atomic<uint64_t> g_n {0};
// Thread id + 1 of the first M0 (0 - none yet).
std::atomic<int64_t>  g_writer {0};
std::atomic<uint32_t> g_bad_logged {0};
std::atomic<uint32_t> g_foreign_logged {0};
// Item 346(g): KYTY_PVAR_HOLD=1 accepted by Arm (mode 2 armed); set before g_m0_ra, never cleared.
std::atomic<bool>     g_hold {false};
// The time (HostUs) of the vblank in g_vb; g_vb and g_vb_t are published together under the seqlock
// g_vb_seq (odd - a write in progress; the Present thread is the only writer).
std::atomic<uint64_t> g_vb_t {0};
std::atomic<uint64_t> g_vb_seq {0};

// Item 348(v)(1): the one clock of the hold and of the "PVar:" line - the monotonic host clock (steady_clock,
// QueryPerformanceCounter in the MSVC library), us from the process start (the static initialization of this file,
// before main). No lock, no freezes, no guest speed - unlike KernelGetProcessTime.
const std::chrono::steady_clock::time_point g_host_start = std::chrono::steady_clock::now();

uint64_t HostUs() {
	return static_cast<uint64_t>(
	    std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - g_host_start).count());
}

Vblank ReadVblank() {
	for (;;) {
		const uint64_t s1 = g_vb_seq.load(std::memory_order_acquire);
		Vblank         vb;
		vb.v = g_vb.load(std::memory_order_relaxed);
		vb.t = g_vb_t.load(std::memory_order_relaxed);
		std::atomic_thread_fence(std::memory_order_acquire);
		const uint64_t s2 = g_vb_seq.load(std::memory_order_relaxed);
		if ((s1 & 1u) == 0 && s1 == s2) {
			return vb;
		}
	}
}

struct Writer {
	bool     started = false; // the first M0 only remembers v
	bool     written = false; // at least one write (else the expected cells are the image's)
	uint64_t v_prev  = 0;
	int32_t  c       = 0;
	uint32_t k_prev  = 1; // the image's k
	uint64_t w       = 0;
	Cells    last {};
	uint32_t kt      = HOLD_KT_START; // item 346(g): the hold target, used only with g_hold
	uint32_t fit     = 0;
	uint32_t nh      = HOLD_NH_START; // item 373(d)(2): the descent 3 -> 2 constant
	uint32_t left    = 0;             // the lines left of the window after a descent 3 -> 2
};

Writer g_writer_state; // the writer thread only

template <typename T>
T Load(uint64_t address) {
	return *reinterpret_cast<volatile T*>(address);
}

template <typename T>
void Store(uint64_t address, T value) {
	*reinterpret_cast<volatile T*>(address) = value;
}

std::string Hex(uint64_t address, size_t size) {
	static constexpr char digits[] = "0123456789abcdef";
	std::string           text;
	for (size_t i = 0; i < size; i++) {
		const auto byte = Load<uint8_t>(address + i);
		text += digits[byte >> 4u];
		text += digits[byte & 0xfu];
	}
	return text;
}

double FpsOf(uint64_t bits) {
	double fps = 0.0;
	std::memcpy(&fps, &bits, sizeof(fps));
	return fps;
}

void Refuse(const char* reason) {
	FS::Add(FS::Counter::PvarBad, 1);
	LOGF("PVar: refused reason=%s\n", reason);
}

// Item 346(g): KYTY_PVAR_HOLD, read once per process: 0 - unset, empty or "0"; 1 - "1"; -1 - anything else.
int HoldMode() {
	static const int mode = [] {
		const char* value = std::getenv("KYTY_PVAR_HOLD");
		if (value == nullptr || value[0] == '\0' || std::strcmp(value, "0") == 0) {
			return 0;
		}
		return std::strcmp(value, "1") == 0 ? 1 : -1;
	}();
	return mode;
}

// Item 346(g): the hold is refused - one line, no counter, the P23 path goes on (or nothing, without P-var).
void RefuseHold() {
	LOGF("PVar: refused reason=hold\n");
}

// The write at M0 (item 284(v)); the caller is the M0 call of the armed process.
void OnM0() {
	const int64_t self     = static_cast<int64_t>(Common::Thread::GetThreadIdUnique()) + 1;
	int64_t       expected = 0;
	if (!g_writer.compare_exchange_strong(expected, self, std::memory_order_relaxed) && expected != self) {
		FS::Add(FS::Counter::PvarBad, 1);
		if (g_bad_logged.fetch_add(1, std::memory_order_relaxed) < 8) {
			LOGF("PVar: bad reason=thread n=%" PRIu64 "\n", g_n.load(std::memory_order_relaxed));
		}
		return;
	}
	auto&          st = g_writer_state;
	const uint64_t t0 = HostUs();
	Vblank         vb = ReadVblank();
	const uint64_t n  = g_n.load(std::memory_order_relaxed);
	if (!st.started) {
		st.started = true;
		st.v_prev  = vb.v;
		return;
	}
	// Item 346(g)(1), (4): kt = 0 without the hold (no wait); the slack is to the vblank v_prev + kt in both modes.
	const bool     hold    = g_hold.load(std::memory_order_relaxed);
	const uint32_t kt      = hold ? st.kt : 0;
	const uint64_t target  = st.v_prev + kt;
	const int64_t  slack   = VblankTimeUs(vb.t, vb.v, target) - static_cast<int64_t>(t0);
	int64_t        wait_us = 0;
	int64_t        exit_us = 0; // after the target vblank; -1 - the wait ended at the deadline
	if (hold) {
		// Item 348(v)(3): the wait (pvar.h HoldWait) on the host clock; no wait when the target is already reached.
		const HoldWaitResult r = HoldWait(
		    static_cast<int64_t>(t0), vb, target, kt, [] { return static_cast<int64_t>(HostUs()); },
		    [](int64_t us) { Common::Thread::SleepMicro(static_cast<uint32_t>(us)); }, [] { return ReadVblank(); });
		vb      = r.vb;
		wait_us = r.wait_us;
		exit_us = r.exit_us;
	}
	const uint64_t v    = vb.v;
	const uint64_t d    = v - st.v_prev;
	st.v_prev           = v;
	const Step     step = Advance(d, st.c);
	st.c                = step.c;
	// Item 346(g)(2)-(3), item 373(d): up on a late frame, down after HoldDescentN fitting frames (nh at kt 3, 30 at
	// kt 2); the fields: kt - the target of this M0, fit and nh - after this M0 (kt, fit, nh 0 without the hold).
	HoldStep hs;
	hs.kt  = 0;
	hs.fit = 0;
	hs.nh  = 0;
	if (hold) {
		hs      = Hold(HoldState {st.kt, st.fit, st.nh, st.left}, d, slack);
		st.kt   = hs.kt;
		st.fit  = hs.fit;
		st.nh   = hs.nh;
		st.left = hs.left;
	}

	const uint64_t base = g_base.load(std::memory_order_relaxed);

	// `foreign`: before this write, the six cells against what this writer wrote last time (the first write - the four
	// cells against the image; a static copy against 0 or the image float: the game initializes it once from cell 2).
	const Cells    image = CellsFor(1);
	const Cells&   want  = st.written ? st.last : image;
	const auto     fps   = Load<uint64_t>(base + CELL_FPS);
	const auto     s32   = Load<uint32_t>(base + CELL_STEP);
	const auto     sus   = Load<uint64_t>(base + CELL_STEP_US);
	const auto     lit   = Load<uint32_t>(base + CELL_LIT);
	const auto     ca    = Load<uint32_t>(base + CELL_COPY_A);
	const auto     cb    = Load<uint32_t>(base + CELL_COPY_B);
	const auto     copy_ok = [&](uint32_t value) { return value == want.step_f32 || (!st.written && value == 0); };
	if (fps != want.fps_bits || s32 != want.step_f32 || sus != want.step_us || lit != want.step_f32 || !copy_ok(ca) ||
	    !copy_ok(cb)) {
		FS::Add(FS::Counter::PvarForeign, 1);
		if (g_foreign_logged.fetch_add(1, std::memory_order_relaxed) < 8) {
			LOGF("PVar: foreign n=%" PRIu64 " cells=%.3f/%08" PRIx32 "/%" PRIu64 "/%08" PRIx32 "/%08" PRIx32 "/%08" PRIx32
			     "\n",
			     n, FpsOf(fps), s32, sus, lit, ca, cb);
		}
	}

	// Item 283(v)(5): the four cells of design section 3.3 in the order of SetFrameRate, then the two static copies.
	// Volatile aligned stores: one instruction each, in program order.
	const Cells cells = CellsFor(step.k);
	Store<uint64_t>(base + CELL_FPS, cells.fps_bits);
	Store<uint32_t>(base + CELL_STEP, cells.step_f32);
	Store<uint64_t>(base + CELL_STEP_US, cells.step_us);
	Store<uint32_t>(base + CELL_LIT, cells.step_f32);
	Store<uint32_t>(base + CELL_COPY_A, cells.step_f32);
	Store<uint32_t>(base + CELL_COPY_B, cells.step_f32);
	st.last    = cells;
	st.written = true;
	st.w++;

	FS::Add(FS::Counter::PvarW, 1);
	FS::Add(FS::Counter::PvarK, step.k);
	FS::Add(FS::Counter::PvarKraw, d);
	FS::Add(FS::Counter::PvarLost, step.lost);
	FS::Add(FS::Counter::PvarOver, step.over);
	if (step.k != st.k_prev) {
		FS::Add(FS::Counter::PvarChg, 1);
	}
	st.k_prev = step.k;
	// pvar_inupd / pvar_tear / pvar_tail: mode 1 (the write in the flip call) is not implemented (item 283(v)(1)); the
	// mode 2 write is at the frame boundary, ph = 0 by construction, so these counters are never added.

	LOGF("PVar: n=%" PRIu64 " w=%" PRIu64 " d=%" PRIu64 " kraw=%" PRIu64 " c=%d k=%u s_us=%" PRIu64 " vb=%" PRIu64
	     " ph=0 mode=2 kt=%u fit=%u wait_us=%" PRId64 " slack_us=%" PRId64 " late=%u t_us=%" PRIu64 " exit_us=%" PRId64
	     " nh=%u\n",
	     n, st.w, d, d, st.c, step.k, cells.step_us, v, kt, hs.fit, wait_us, slack, hs.late, t0, exit_us, hs.nh);
}

} // namespace

int Mode() {
	static const int mode = [] {
		// Track P, the patch file (loader/gamePatchFile.h, ROADMAP s122 item 333(d)): an applied "pvar 2" is mode 2
		// (an explicit KYTY_PVAR other than "2" refuses the file, so the two never disagree).
		if (Loader::GamePatchFile::PvarOn()) {
			return 2;
		}
		const char* value = std::getenv("KYTY_PVAR");
		if (value == nullptr || value[0] == '\0' || std::strcmp(value, "0") == 0) {
			return 0;
		}
		return std::strcmp(value, "2") == 0 ? 2 : -1;
	}();
	return mode;
}

uint64_t KYTY_SYSV_ABI GetProcessTimeCounter() {
	const auto ra = reinterpret_cast<uint64_t>(__builtin_return_address(0));
	if (ra == g_m0_ra.load(std::memory_order_acquire)) [[unlikely]] {
		OnM0();
	}
	return KernelGetProcessTimeCounter();
}

namespace {

// The P23 arming; true - armed (the "PVar: armed" line printed), the caller publishes g_m0_ra.
bool ArmMode2(uint64_t base) {
	const int mode = Mode();
	if (mode == 0) {
		return false;
	}
	if (mode != 2) {
		Refuse("value");
		return false;
	}
	const Cells image = CellsFor(1);
	if (base == 0 || Load<uint64_t>(base + CELL_FPS) != image.fps_bits ||
	    Load<uint32_t>(base + CELL_STEP) != image.step_f32 || Load<uint64_t>(base + CELL_STEP_US) != image.step_us ||
	    Load<uint32_t>(base + CELL_LIT) != image.step_f32) {
		Refuse("image");
		return false;
	}
	const uint32_t vbl = Config::GetVblankFrequency();
	if (vbl != 60) {
		Refuse("vbl");
		return false;
	}
	if (std::memcmp(reinterpret_cast<const void*>(base + LIMITER), LIMITER_BYTES, sizeof(LIMITER_BYTES)) != 0) {
		Refuse("limiter");
		return false;
	}
	if (std::memcmp(reinterpret_cast<const void*>(base + HAVOK), HAVOK_BYTES, sizeof(HAVOK_BYTES)) != 0) {
		Refuse("havok");
		return false;
	}
	// Probe (design section 3.3): cell 4 lies in a read-only guest segment; write its own value before the armed line.
	Store<uint32_t>(base + CELL_LIT, Load<uint32_t>(base + CELL_LIT));

	g_base.store(base, std::memory_order_relaxed);
	g_publish.store(true, std::memory_order_relaxed);
	LOGF("PVar: armed mode=2 base=0x%" PRIx64 " vbl=%" PRIu32 " cells=%.3f/%08" PRIx32 "/%" PRIu64 "/%08" PRIx32
	     " lim=%s hav=%s\n",
	     base, vbl, FpsOf(Load<uint64_t>(base + CELL_FPS)), Load<uint32_t>(base + CELL_STEP),
	     Load<uint64_t>(base + CELL_STEP_US), Load<uint32_t>(base + CELL_LIT), Hex(base + LIMITER, 25).c_str(),
	     Hex(base + HAVOK, 4).c_str());
	return true;
}

} // namespace

void Arm(uint64_t base) {
	const int  hold  = HoldMode();
	const bool armed = ArmMode2(base);
	if (!armed) {
		// Item 346(g): KYTY_PVAR_HOLD set (any value but 0) without armed mode 2 - one line, nothing else.
		if (hold != 0) {
			RefuseHold();
		}
		return;
	}
	if (hold == 1) {
		g_hold.store(true, std::memory_order_relaxed);
	} else if (hold != 0) {
		RefuseHold();
	}
	// Last: from here the wrapper writes (seq_cst - the stores above are visible to the thread that sees it).
	g_m0_ra.store(base + M0_RETURN);
}

bool Publishing() {
	return g_publish.load(std::memory_order_relaxed);
}

void PublishVblank(uint64_t count) {
	// Item 346(g): the count and its time under the seqlock (the only writer - the Present thread).
	const uint64_t t = HostUs();
	const uint64_t s = g_vb_seq.load(std::memory_order_relaxed);
	g_vb_seq.store(s + 1, std::memory_order_relaxed);
	std::atomic_thread_fence(std::memory_order_release);
	g_vb.store(count, std::memory_order_relaxed);
	g_vb_t.store(t, std::memory_order_relaxed);
	g_vb_seq.store(s + 2, std::memory_order_release);
}

void PublishFlip(uint64_t count) {
	g_n.store(count, std::memory_order_relaxed);
}

} // namespace Libs::LibKernel::PVar
