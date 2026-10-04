// F16e (HPP-522, Red Team): model of the DiagF6 snapshot race of KytyPS5 381aa80a, NOT the emulator.
// Writer = NoteDraw (src/graphics/host_gpu/renderer/diagF5.cpp:276-344): per draw one local add[] and then
// fetch_add(relaxed) of every non-zero entry in ascending index order (:338-343).
// Reader = TickSet/FormatSet (:47-67, :37-44): relaxed loads in ascending index order, each followed by a
// std::format + string append (the emulator uses fmt::format), then the printed values are checked against the
// identities of diagF5.h:134-136 and the rule of ROADMAP p.458(d)(3) ("sum of children > parent on any line").
// Two threads as in the emulator: the sites run on the GuestGpu thread, the tick on the PresentThread.
// Usage: race_demo <seconds> <draw_period_ns> <tick_period_us>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <format>
#include <string>
#include <thread>
#include <vector>

enum C : uint32_t {
	Draws, DrawsIdx, DrawsAuto, DrawsInd, DrawsMesh, PsDraws, SBound, SAddr0Fmt, SAddr0NoFmt, SMask0Addr, SEmpty,
	HBound, BoundMissing, BoundExtra, WTotal, WBound, WMask0, WAddr0Fmt, WAddr0NoFmt, WGe8, N
};
static const char* kNames[N] = {"draws", "draws_idx", "draws_auto", "draws_ind", "draws_mesh", "ps_draws",
                                "s_bound", "s_addr0_fmt", "s_addr0_nofmt", "s_mask0_addr", "s_empty", "h_bound",
                                "bound_missing", "bound_extra", "w_total", "w_bound", "w_mask0", "w_addr0_fmt",
                                "w_addr0_nofmt", "w_ge8"};

static std::array<std::atomic<uint64_t>, N> g_counters {};
static std::atomic<bool>                     g_stop {false};

static uint64_t NowNs() {
	return static_cast<uint64_t>(
	    std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch())
	        .count());
}

// One draw of a defect-free path: 2 bound slots with host attachments, 6 empty slots, PS exporting MRT 0 and 1.
static void NoteDraw() {
	std::array<uint64_t, N> add {};
	add[Draws] = 1;
	add[DrawsIdx] = 1;
	add[PsDraws] = 1;
	add[SBound] = 2;
	add[SEmpty] = 6;
	add[HBound] = 2;
	add[WTotal] = 2;
	add[WBound] = 2;
	for (uint32_t i = 0; i < N; i++) {
		if (add[i] != 0) {
			g_counters[i].fetch_add(add[i], std::memory_order_relaxed);
		}
	}
}

int main(int argc, char** argv) {
	const double   seconds   = argc > 1 ? std::atof(argv[1]) : 5.0;
	const uint64_t period_ns = argc > 2 ? std::strtoull(argv[2], nullptr, 10) : 10000;
	const uint64_t tick_us   = argc > 3 ? std::strtoull(argv[3], nullptr, 10) : 1000;
	std::thread    writer([&] {
        uint64_t next = NowNs();
        while (!g_stop.load(std::memory_order_relaxed)) {
            NoteDraw();
            next += period_ns;
            while (NowNs() < next) {
            }
        }
    });
	uint64_t lines = 0, sum_gt_parent = 0, parent_gt_sum = 0, kind_bad = 0, w_bad = 0, h_bad = 0, max_excess = 0;
	const uint64_t end = NowNs() + static_cast<uint64_t>(seconds * 1e9);
	while (NowNs() < end) {
		std::string line = std::format("DiagF6: frame={}", lines);
		std::array<uint64_t, N> v {};
		for (uint32_t i = 0; i < N; i++) {
			v[i] = g_counters[i].load(std::memory_order_relaxed);
			line += std::format(" {}={}", kNames[i], v[i]);
		}
		lines++;
		const uint64_t s_sum = v[SBound] + v[SAddr0Fmt] + v[SAddr0NoFmt] + v[SMask0Addr] + v[SEmpty];
		if (s_sum > 8 * v[Draws]) {
			sum_gt_parent++;
			max_excess = std::max(max_excess, s_sum - 8 * v[Draws]);
		} else if (s_sum < 8 * v[Draws]) {
			parent_gt_sum++;
		}
		if (v[DrawsIdx] + v[DrawsAuto] + v[DrawsInd] + v[DrawsMesh] != v[Draws]) {
			kind_bad++;
		}
		if (v[WTotal] != v[WBound] + v[WMask0] + v[WAddr0Fmt] + v[WAddr0NoFmt] + v[WGe8]) {
			w_bad++;
		}
		if (v[HBound] + v[BoundMissing] != v[SBound] + v[BoundExtra]) {
			h_bad++;
		}
		std::this_thread::sleep_for(std::chrono::microseconds(tick_us));
	}
	g_stop = true;
	writer.join();
	std::printf("race_demo: seconds=%.1f draw_period_ns=%llu tick_us=%llu lines=%llu draws=%llu\n", seconds,
	            (unsigned long long)period_ns, (unsigned long long)tick_us, (unsigned long long)lines,
	            (unsigned long long)g_counters[Draws].load());
	std::printf("race_demo: lines with sum(s_*) > 8*draws=%llu (max excess %llu), sum(s_*) < 8*draws=%llu, "
	            "draws_* != draws=%llu, w identity broken=%llu, h identity broken=%llu\n",
	            (unsigned long long)sum_gt_parent, (unsigned long long)max_excess,
	            (unsigned long long)parent_gt_sum, (unsigned long long)kind_bad, (unsigned long long)w_bad,
	            (unsigned long long)h_bad);
	std::printf("race_demo: per-line rate of 'sum of children > parent' = %.4f\n",
	            lines ? double(sum_gt_parent) / double(lines) : 0.0);
	return 0;
}
