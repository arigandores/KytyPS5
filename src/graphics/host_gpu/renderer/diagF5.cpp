#include "graphics/host_gpu/renderer/diagF5.h"

#include "common/envFlag.h"
#include "common/logging/log.h"
#include "graphics/host_gpu/renderer/debug.h"

#include <fmt/format.h>

#include <chrono>
#include <cstdlib>
#include <mutex>

// Track F, F16d (HPP-521): see diagF5.h. Nothing here is reachable with both knobs off except On() (a static read once)
// and the early returns of LogMode / Tick / Service / NoteDraw (F16d2: Service is not even called - graphicsRun.cpp).

namespace Libs::Graphics {

namespace {

template <typename CounterEnum>
struct DiagSet {
	static constexpr uint32_t                         N = static_cast<uint32_t>(CounterEnum::Count);
	std::array<std::atomic<uint64_t>, N>              counters {};
	std::atomic<bool>                                 mode_logged {false};
	// Track F, F16d2: the request of the flip tick (PresentThread -> GuestGpu); the mutex is held only to write or take
	// it, never while the counters are copied - the vblank waits at most for one take.
	std::mutex                                        request_mutex;
	bool                                              has_request   = false;
	uint32_t                                          request_frame = 0;
	uint64_t                                          request_ms    = 0;
	// The state of the line: written only by Service (GuestGpu thread) under print_mutex; read by the test site.
	std::mutex                                        print_mutex;
	uint64_t                                          last_sum   = 0;
	uint64_t                                          last_ms    = 0;
	bool                                              printed    = false;
	uint64_t                                          lines      = 0;
	std::string                                       last_line;
};

// Track F, F16d2: the test site's window hook (nullptr in the emulator; diagF5.h).
DiagF5::WindowHook g_window_hook = nullptr;

template <typename CounterEnum>
using Snapshot = std::array<uint64_t, DiagSet<CounterEnum>::N>;

uint64_t NowMs() {
	return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
	                                 std::chrono::steady_clock::now().time_since_epoch())
	                                 .count());
}

// One copy of all counters (relaxed loads in index order). Track F, F16d2: called only by Service on the GuestGpu
// thread (and by the test site), so it sees exactly the increments of the windows already closed on that thread.
template <typename CounterEnum>
Snapshot<CounterEnum> CopySet(const DiagSet<CounterEnum>& set) {
	Snapshot<CounterEnum> snapshot {};
	for (uint32_t i = 0; i < DiagSet<CounterEnum>::N; i++) {
		snapshot[i] = set.counters[i].load(std::memory_order_relaxed);
	}
	return snapshot;
}

template <typename CounterEnum>
std::string FormatSet(const char* tag, const Snapshot<CounterEnum>& snapshot, const char* const* names, uint32_t frame) {
	std::string line = fmt::format("{}: frame={}", tag, frame);
	for (uint32_t i = 0; i < DiagSet<CounterEnum>::N; i++) {
		line += fmt::format(" {}={}", names[i], snapshot[i]);
	}
	return line;
}

// The flip tick (PresentThread; item 470(v)(1), form (a)): publishes the request only - no counter is read here.
template <typename CounterEnum>
bool PublishSet(bool on, DiagSet<CounterEnum>& set, uint32_t frame, uint64_t now_ms) {
	if (!on) {
		return false;
	}
	std::scoped_lock lock {set.request_mutex};
	set.request_frame = frame;
	set.request_ms    = now_ms;
	set.has_request   = true;
	return true;
}

// The line (item 427(e)) on the GuestGpu thread outside every window: the pending request, one copy of all counters,
// then the condition "a counter grew since the last line and >= 2000 ms passed since it" and the line - both from that
// copy.
template <typename CounterEnum>
bool ServiceSet(bool on, const char* tag, DiagSet<CounterEnum>& set, const char* const* names) {
	if (!on) {
		return false;
	}
	uint32_t frame  = 0;
	uint64_t now_ms = 0;
	{
		std::scoped_lock lock {set.request_mutex};
		if (!set.has_request) {
			return false;
		}
		frame           = set.request_frame;
		now_ms          = set.request_ms;
		set.has_request = false;
	}
	std::scoped_lock lock {set.print_mutex};
	const auto       snapshot = CopySet(set);
	uint64_t         sum      = 0;
	for (const auto value: snapshot) {
		sum += value;
	}
	if (sum == set.last_sum || (set.printed && now_ms - set.last_ms < 2000u)) {
		return false;
	}
	auto line = FormatSet<CounterEnum>(tag, snapshot, names, frame);
	LOGF("%s\n", line.c_str());
	set.last_sum  = sum;
	set.last_ms   = now_ms;
	set.printed   = true;
	set.last_line = std::move(line);
	set.lines++;
	return true;
}

template <typename CounterEnum>
uint64_t LinesSet(DiagSet<CounterEnum>& set) {
	std::scoped_lock lock {set.print_mutex};
	return set.lines;
}

template <typename CounterEnum>
std::string LastLineSet(DiagSet<CounterEnum>& set) {
	std::scoped_lock lock {set.print_mutex};
	return set.last_line;
}

template <typename CounterEnum>
bool LogModeSet(bool on, const char* tag, DiagSet<CounterEnum>& set) {
	if (!on || set.mode_logged.exchange(true, std::memory_order_relaxed)) {
		return false;
	}
	LOGF("%s: mode=1\n", tag);
	return true;
}

DiagSet<DiagF5::Counter>& F5() {
	static DiagSet<DiagF5::Counter> set;
	return set;
}

DiagSet<DiagF6::Counter>& F6() {
	static DiagSet<DiagF6::Counter> set;
	return set;
}

constexpr const char* F5Names[] = {
    "rt_resolves",
    "dcc_rt",
    "rtcheck_meta",
    "dcc_rt_pending",
    "dcc_rt_cleared",
    "dcc_rt_skip_levels",
    "dcc_rt_skip_partial",
    "dcc_rt_skip_decode",
    "dcc_rt_skip_layers",
    "dcc_mat_pending",
    "dcc_mat_cleared",
    "dcc_mat_undecoded",
    "dcc_fce",
    "dcc_fce_image",
    "dcc_fce_no_image",
    "dcc_fill_all",
    "dcc_fill_meta",
    "dcc_fill_clear",
    "dcc_fill_uncompressed",
    "dcc_fill_unknown",
    "dcc_reset_stale",
    "dcc_reset_type",
    "meta_refused_known",
    "meta_cs_tracked",
    "meta_cs_untracked",
    "meta_dma_untracked",
    "meta_dma_noclear",
    "cmask_rt_pending",
    "cmask_rt_cleared",
    "cmask_rt_skip_value",
    "cmask_rt_skip_partial",
    "cmask_rt_skip_decode",
    "cmask_rt_skip_layers",
    "cmask_fce",
    "cmask_fce_noimage",
    "cmask_fce_meta",
    "cmask_fce_msaa",
    "cmask_fce_layout",
    "cmask_fce_nofill",
    "cmask_fce_drawn",
    "cmask_fce_b42",
    "cmask_fce_unapplied",
    "fmask_read",
    "round_unorm",
    "round_float",
    "round_other",
    "ds_unbound",
    "ds_unbound_clear",
    "stereo_writes",
    "stereo_nonzero",
    "zero_disp",
};
static_assert(std::size(F5Names) == static_cast<size_t>(DiagF5::Counter::Count));

constexpr const char* F6Names[] = {
    "draws",   "draws_idx",    "draws_auto",    "draws_ind",     "draws_mesh", "ps_draws",  "s_bound",
    "s_addr0_fmt", "s_addr0_nofmt", "s_mask0_addr", "s_empty", "h_bound", "bound_missing", "bound_extra",
    "w_total", "w_bound",      "w_mask0",       "w_addr0_fmt",   "w_addr0_nofmt", "w_ge8",
};
static_assert(std::size(F6Names) == static_cast<size_t>(DiagF6::Counter::Count));

} // namespace

namespace DiagF5 {

bool On() {
	static const bool on = Common::EnvValueOn(std::getenv("KYTY_DIAG_F5"));
	return on;
}

void Add(Counter counter) {
	const auto index = static_cast<uint32_t>(counter);
	F5().counters[index].fetch_add(1, std::memory_order_relaxed);
	if (g_window_hook != nullptr) [[unlikely]] {
		g_window_hook(5, index); // Track F, F16d2: the test site's tick inside the window (nullptr in the emulator)
	}
}

uint64_t Get(Counter counter) {
	return F5().counters[static_cast<uint32_t>(counter)].load(std::memory_order_relaxed);
}

const char* Name(Counter counter) {
	return F5Names[static_cast<uint32_t>(counter)];
}

bool LogMode() {
	return LogModeSet(On(), "DiagF5", F5());
}

bool Tick(uint32_t frame) {
	if (!On()) {
		return false;
	}
	return TickAt(frame, NowMs());
}

bool TickAt(uint32_t frame, uint64_t now_ms) {
	return PublishSet(On(), F5(), frame, now_ms);
}

bool Service() {
	return ServiceSet(On(), "DiagF5", F5(), F5Names);
}

std::string FormatLine(uint32_t frame) {
	return FormatSet<Counter>("DiagF5", CopySet(F5()), F5Names, frame);
}

uint64_t Lines() {
	return LinesSet(F5());
}

std::string LastLine() {
	return LastLineSet(F5());
}

void SetWindowHook(WindowHook hook) {
	g_window_hook = hook;
}

uint32_t ViewLayerBits(uint32_t first, uint32_t count) {
	if (first >= 32 || count > 32 - first) {
		return UINT32_MAX;
	}
	if (count == 0) {
		return 0;
	}
	return (count >= 32 ? UINT32_MAX : (uint32_t {1} << count) - 1u) << first;
}

FillClass DccFillClassOf(uint32_t fill_value) {
	const auto code = static_cast<uint8_t>(fill_value);
	if (fill_value == static_cast<uint32_t>(code) * 0x01010101u) {
		switch (code) {
			case 0x00:
			case 0x20:
			case 0x40:
			case 0x80:
			case 0xc0: return FillClass::Clear;
			case 0xff: return FillClass::Uncompressed;
			default: break;
		}
	}
	return FillClass::Unknown;
}

void NoteDccFill(uint32_t fill_value) {
	Add(Counter::DccFillMeta);
	switch (DccFillClassOf(fill_value)) {
		case FillClass::Clear: Add(Counter::DccFillClear); break;
		case FillClass::Uncompressed: Add(Counter::DccFillUncompressed); break;
		case FillClass::Unknown: Add(Counter::DccFillUnknown); break;
	}
}

void NoteCsRefusals(const CsRefusals& refusals, uint64_t tracked_address) {
	for (uint32_t i = 0; i < refusals.count && i < CsRefusals::Max; i++) {
		Add(tracked_address != 0 && refusals.addresses[i] == tracked_address ? Counter::MetaCsTracked
		                                                                    : Counter::MetaCsUntracked);
	}
}

void NoteDmaRefusal(uint8_t refusal, uint32_t value) {
	if (refusal == RefusalDcc) {
		Add(DccFillClassOf(value) == FillClass::Clear ? Counter::MetaDmaUntracked : Counter::MetaDmaNoClear);
	} else if (refusal == RefusalCmask) {
		Add(value == 0 ? Counter::MetaDmaUntracked : Counter::MetaDmaNoClear);
	}
}

} // namespace DiagF5

namespace DiagF6 {

bool On() {
	static const bool on = Common::EnvValueOn(std::getenv("KYTY_DIAG_F6"));
	return on;
}

uint64_t Get(Counter counter) {
	return F6().counters[static_cast<uint32_t>(counter)].load(std::memory_order_relaxed);
}

const char* Name(Counter counter) {
	return F6Names[static_cast<uint32_t>(counter)];
}

bool LogMode() {
	return LogModeSet(On(), "DiagF6", F6());
}

bool Tick(uint32_t frame) {
	if (!On()) {
		return false;
	}
	return TickAt(frame, NowMs());
}

bool TickAt(uint32_t frame, uint64_t now_ms) {
	return PublishSet(On(), F6(), frame, now_ms);
}

bool Service() {
	return ServiceSet(On(), "DiagF6", F6(), F6Names);
}

std::string FormatLine(uint32_t frame) {
	return FormatSet<Counter>("DiagF6", CopySet(F6()), F6Names, frame);
}

uint64_t Lines() {
	return LinesSet(F6());
}

std::string LastLine() {
	return LastLineSet(F6());
}

void NoteDraw(const HW::Context& hw, const uint32_t* host_slots, uint32_t host_count, bool ps, const uint32_t* mrt,
              uint32_t mrt_count, DrawKind kind) {
	if (!On()) {
		return;
	}
	constexpr uint32_t                                       N = static_cast<uint32_t>(Counter::Count);
	std::array<uint64_t, N>                                  add {};
	const auto inc = [&add](Counter counter, uint64_t n = 1) { add[static_cast<uint32_t>(counter)] += n; };
	inc(Counter::Draws);
	switch (kind) {
		case DrawKind::Indexed: inc(Counter::DrawsIdx); break;
		case DrawKind::Auto: inc(Counter::DrawsAuto); break;
		case DrawKind::Indirect: inc(Counter::DrawsInd); break;
		case DrawKind::Mesh: inc(Counter::DrawsMesh); break;
	}
	const uint32_t target_mask = hw.GetRenderTargetMask();
	bool           mask_on[8] {};
	bool           base_on[8] {};
	bool           fmt_on[8] {};
	for (uint32_t slot = 0; slot < 8; slot++) {
		const auto& rt = hw.GetRenderTarget(slot);
		mask_on[slot]  = render_target_mask_slot(target_mask, slot) != 0;
		base_on[slot]  = rt.base.addr != 0;
		fmt_on[slot]   = static_cast<uint32_t>(rt.info.format) != 0; // raw CB_COLORn_INFO.FORMAT (pm4Handlers.cpp)
		if (mask_on[slot]) {
			inc(base_on[slot] ? Counter::SBound : fmt_on[slot] ? Counter::SAddr0Fmt : Counter::SAddr0NoFmt);
		} else {
			inc(base_on[slot] ? Counter::SMask0Addr : Counter::SEmpty);
		}
	}
	uint32_t host_mask = 0;
	inc(Counter::HBound, host_count);
	for (uint32_t i = 0; i < host_count; i++) {
		const auto slot = host_slots[i];
		if (slot >= 8 || !(mask_on[slot] && base_on[slot])) {
			inc(Counter::BoundExtra);
		}
		if (slot < 8) {
			host_mask |= 1u << slot;
		}
	}
	for (uint32_t slot = 0; slot < 8; slot++) {
		if (mask_on[slot] && base_on[slot] && (host_mask & (1u << slot)) == 0) {
			inc(Counter::BoundMissing);
		}
	}
	if (ps) {
		inc(Counter::PsDraws);
		for (uint32_t i = 0; i < mrt_count; i++) {
			const auto index = mrt[i];
			inc(Counter::WTotal);
			if (index >= 8) {
				inc(Counter::WGe8);
			} else if (!mask_on[index]) {
				inc(Counter::WMask0);
			} else if (base_on[index]) {
				inc(Counter::WBound);
			} else {
				inc(fmt_on[index] ? Counter::WAddr0Fmt : Counter::WAddr0NoFmt);
			}
		}
	}
	auto& set = F6();
	for (uint32_t i = 0; i < N; i++) {
		if (add[i] != 0) {
			set.counters[i].fetch_add(add[i], std::memory_order_relaxed);
			if (g_window_hook != nullptr) [[unlikely]] {
				g_window_hook(6, i); // Track F, F16d2: the test site's tick inside the window (nullptr in the emulator)
			}
		}
	}
}

} // namespace DiagF6

} // namespace Libs::Graphics
