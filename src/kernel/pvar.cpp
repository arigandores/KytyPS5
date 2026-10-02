#include "kernel/pvar.h"

#include "common/emulatorConfig.h"
#include "common/frameStats.h"
#include "common/logging/log.h"
#include "common/threads.h"
#include "kernel/pthread.h"

#include <atomic>
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

struct Writer {
	bool     started = false; // the first M0 only remembers v
	bool     written = false; // at least one write (else the expected cells are the image's)
	uint64_t v_prev  = 0;
	int32_t  c       = 0;
	uint32_t k_prev  = 1; // the image's k
	uint64_t w       = 0;
	Cells    last {};
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
	const uint64_t v  = g_vb.load(std::memory_order_acquire);
	const uint64_t n  = g_n.load(std::memory_order_relaxed);
	if (!st.started) {
		st.started = true;
		st.v_prev  = v;
		return;
	}
	const uint64_t d    = v - st.v_prev;
	st.v_prev           = v;
	const Step     step = Advance(d, st.c);
	st.c                = step.c;

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
	     " ph=0 mode=2\n",
	     n, st.w, d, d, st.c, step.k, cells.step_us, v);
}

} // namespace

int Mode() {
	static const int mode = [] {
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

void Arm(uint64_t base) {
	const int mode = Mode();
	if (mode == 0) {
		return;
	}
	if (mode != 2) {
		Refuse("value");
		return;
	}
	const Cells image = CellsFor(1);
	if (base == 0 || Load<uint64_t>(base + CELL_FPS) != image.fps_bits ||
	    Load<uint32_t>(base + CELL_STEP) != image.step_f32 || Load<uint64_t>(base + CELL_STEP_US) != image.step_us ||
	    Load<uint32_t>(base + CELL_LIT) != image.step_f32) {
		Refuse("image");
		return;
	}
	const uint32_t vbl = Config::GetVblankFrequency();
	if (vbl != 60) {
		Refuse("vbl");
		return;
	}
	if (std::memcmp(reinterpret_cast<const void*>(base + LIMITER), LIMITER_BYTES, sizeof(LIMITER_BYTES)) != 0) {
		Refuse("limiter");
		return;
	}
	if (std::memcmp(reinterpret_cast<const void*>(base + HAVOK), HAVOK_BYTES, sizeof(HAVOK_BYTES)) != 0) {
		Refuse("havok");
		return;
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
	// Last: from here the wrapper writes (seq_cst - the stores above are visible to the thread that sees it).
	g_m0_ra.store(base + M0_RETURN);
}

bool Publishing() {
	return g_publish.load(std::memory_order_relaxed);
}

void PublishVblank(uint64_t count) {
	g_vb.store(count, std::memory_order_release);
}

void PublishFlip(uint64_t count) {
	g_n.store(count, std::memory_order_relaxed);
}

} // namespace Libs::LibKernel::PVar
