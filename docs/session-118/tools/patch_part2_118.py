"""Session 118: route A stage 4 part 2 (docs/session-118/designA4_part2.md; ROADMAP 118 items 1-2): the carry term,
a safe spine plan, the slice census (gate "slicecen": K3, K4).  Measurement only; defaults unchanged.
Anchors are whole lines and must match exactly once.  Files are written back with their own line endings (LF here)."""
from pathlib import Path
import sys

SRC = Path('C:/kyty/KytyPS5/src')
DRY = len(sys.argv) > 1 and sys.argv[1] == '--dry'


def patch(rel, edits):
    p = SRC / rel
    raw = p.read_bytes().decode('utf-8')
    crlf = '\r\n' in raw
    s = raw.replace('\r\n', '\n')
    for old, new in edits:
        n = s.count(old)
        if n != 1:
            raise SystemExit(f'{rel}: anchor found {n} times:\n{old[:300]}')
        s = s.replace(old, new)
    if crlf:
        s = s.replace('\n', '\r\n')
    if not DRY:
        p.write_bytes(s.encode('utf-8'))
    print('patched' if not DRY else 'ok (dry)', rel)


# ---------------------------------------------------------------------------------------------- gates.h / gates.cpp
patch('common/gates.h', [(
"""	// LAST row, matching the LAST enum entry before Gate::Count.
	CommitLapMove,      // KYTY_COMMIT_LAP_MOVE,    file name "cbmove"
	Count,
""",
"""	CommitLapMove,      // KYTY_COMMIT_LAP_MOVE,    file name "cbmove"
	// Session 118, MEASUREMENT ONLY (route A stage 4 part 2, docs/session-118/designA4_part2.md): the slice census.
	// Elements, host render-pass starts and the images every element touches are recorded on the GuestGpu thread; at
	// each frame change K3 (element runs between pass starts) and K4 (image overlap of adjacent segments at W = 2 and 4)
	// land in FrameTrace-x.  Read at every element / pass start / image, so it CAN be a schedule arm (a frame is only
	// finished if the gate stayed on from its first element).  Changes nothing that executes.
	// LAST row, matching the LAST enum entry before Gate::Count.
	SliceCensus,        // KYTY_SLICE_CENSUS,       file name "slicecen"
	Count,
""")])
patch('common/gates.cpp', [(
"""    // LAST row, matching the LAST enum entry before Gate::Count.
    {"KYTY_COMMIT_LAP_MOVE", "cbmove", false},
}};
""",
"""    {"KYTY_COMMIT_LAP_MOVE", "cbmove", false},
    // Session 118, measurement only: the slice census of route A stage 4 part 2 (K3 pass runs, K4 image overlap of
    // adjacent segments). Read at every element, so it CAN be a schedule arm.
    // LAST row, matching the LAST enum entry before Gate::Count.
    {"KYTY_SLICE_CENSUS", "slicecen", false},
}};
"""), (
"""    // Session 117, MEASUREMENT ONLY: the shadow spine of route A stage 4 (1 plan, 2 plan + verify). Read once per
    // submission, so it CAN be a schedule arm. LAST row, matching the LAST enum entry before Knob::Count.
""",
"""    // Session 117, MEASUREMENT ONLY: the shadow spine of route A stage 4 (1 plan, 2 plan + verify). Read once per
    // submission, so it CAN be a schedule arm. Session 118: the plan also checks the carry (term C) and is safe (it
    // stops as UNCERTAIN / ABORTED instead of reading a GPU-dirty word or reaching a structural EXIT).
    // LAST row, matching the LAST enum entry before Knob::Count.
""")])
patch('common/gates.h', [(
"""	// draw/dispatch, compared member-wise with the real state when the real processor reaches it (spine_cmp /
	// spine_bad).  Read once per submission and latched into Pm4Execution, so it CAN be a schedule arm.  Never changes
	// what executes.  LAST row, matching the LAST entry of KNOB_DEFINITIONS.
""",
"""	// draw/dispatch, compared member-wise with the real state when the real processor reaches it (spine_cmp /
	// spine_bad).  Read once per submission and latched into Pm4Execution, so it CAN be a schedule arm.  Session 118:
	// every plan first compares the state the previous complete plan of the processor left with the real state (the
	// carry, carry_*); words read early are read only from GPU-clean pages (else the plan stops as UNCERTAIN) and the
	// structural EXIT conditions of the register handlers are checked first (the plan stops as ABORTED).  It does not
	// change what executes, except through a value-level EXIT inside a register handler that the real processor would
	// reach a moment later on the same packet (ROADMAP 117 item 15).  LAST row, matching the LAST entry of
	// KNOB_DEFINITIONS.
""")])

# ---------------------------------------------------------------------------------------------- frameStats.h / videoOut.cpp
patch('common/frameStats.h', [(
"""	SpineCheckNs,            // spine_chk_ns
	Count
};
""",
"""	SpineCheckNs,            // spine_chk_ns
	// Session 118 (knob "spine"): spine_unc plans stopped as UNCERTAIN (a word read early sat on a GPU-dirty page);
	// carry_cmp / carry_bad / carry_skip - the state the previous complete plan of the processor left, compared with
	// the real state at the next plan (SpineCarry: lines) / plans without a complete predecessor.  Raw counts.
	SpineUncertain,          // spine_unc
	CarryCmp,                // carry_cmp
	CarryBad,                // carry_bad
	CarrySkip,               // carry_skip
	// Session 118 (gate "slicecen"): frames finished, their elements, element runs between host render-pass starts,
	// the sum over frames of each frame's largest run, the run histogram (<32 <128 <512 <1024 >=1024), K4 per frame
	// (the max over adjacent segment pairs of |A&B| / min and of the write-crossing share, and the largest segment's
	// share, all in permille, at W = 2 and W = 4, with the frames that could be cut), frames too short in pass starts to
	// cut, image records and the census's own time (raw ns).
	ScFrames,                // sc_frames
	ScElements,              // sc_el
	ScRuns,                  // sc_runs
	K3MaxRun,                // k3_max
	K3Hist0,                 // k3_h0
	K3Hist1,                 // k3_h1
	K3Hist2,                 // k3_h2
	K3Hist3,                 // k3_h3
	K3Hist4,                 // k3_h4
	K4W2N,                   // k4_w2_n
	K4W2Any,                 // k4_w2_any
	K4W2Dep,                 // k4_w2_dep
	K4W2Fmax,                // k4_w2_fmax
	K4W4N,                   // k4_w4_n
	K4W4Any,                 // k4_w4_any
	K4W4Dep,                 // k4_w4_dep
	K4W4Fmax,                // k4_w4_fmax
	K4NoCut,                 // k4_nocut
	ScImages,                // sc_img
	ScNs,                    // sc_ns
	Count
};
""")])
patch('graphics/presentation/videoOut.cpp', [(
"""				    {"spine_chk_ns", FS::Counter::SpineCheckNs, false},
""",
"""				    {"spine_chk_ns", FS::Counter::SpineCheckNs, false},
				    {"spine_unc", FS::Counter::SpineUncertain, false},
				    {"carry_cmp", FS::Counter::CarryCmp, false},
				    {"carry_bad", FS::Counter::CarryBad, false},
				    {"carry_skip", FS::Counter::CarrySkip, false},
				    {"sc_frames", FS::Counter::ScFrames, false},
				    {"sc_el", FS::Counter::ScElements, false},
				    {"sc_runs", FS::Counter::ScRuns, false},
				    {"k3_max", FS::Counter::K3MaxRun, false},
				    {"k3_h0", FS::Counter::K3Hist0, false},
				    {"k3_h1", FS::Counter::K3Hist1, false},
				    {"k3_h2", FS::Counter::K3Hist2, false},
				    {"k3_h3", FS::Counter::K3Hist3, false},
				    {"k3_h4", FS::Counter::K3Hist4, false},
				    {"k4_w2_n", FS::Counter::K4W2N, false},
				    {"k4_w2_any", FS::Counter::K4W2Any, false},
				    {"k4_w2_dep", FS::Counter::K4W2Dep, false},
				    {"k4_w2_fmax", FS::Counter::K4W2Fmax, false},
				    {"k4_w4_n", FS::Counter::K4W4N, false},
				    {"k4_w4_any", FS::Counter::K4W4Any, false},
				    {"k4_w4_dep", FS::Counter::K4W4Dep, false},
				    {"k4_w4_fmax", FS::Counter::K4W4Fmax, false},
				    {"k4_nocut", FS::Counter::K4NoCut, false},
				    {"sc_img", FS::Counter::ScImages, false},
				    {"sc_ns", FS::Counter::ScNs, false},
""")])

# ---------------------------------------------------------------------------------------------- commandProcessor.h
patch('graphics/guest_gpu/command_processor/commandProcessor.h', [(
"""	uint32_t                          m_spine_snap_count = 0;
	uint64_t                          m_spine_plan_id    = 0;
""",
"""	uint32_t                          m_spine_snap_count = 0;
	uint64_t                          m_spine_plan_id    = 0;
	// Session 118, term C: the shadow state is the end state of a plan that ran to completion (not aborted, not
	// uncertain), so the next plan can compare it with the real state before seeding.
	bool                              m_spine_carry_valid = false;
""")])

# ---------------------------------------------------------------------------------------------- graphicsRun.cpp
SAFE = r'''
// Session 118 (ROADMAP 117 item 15, 118 item 2): the structural EXIT conditions of the register handlers the spine calls,
// checked before the call so that the plan stops (ABORTED) instead of ending the process where execution would not.
// Returns 0 safe, 1 abort, 2 uncertain (an indirect register table on a GPU-dirty page).  Value-level
// EXIT_NOT_IMPLEMENTED inside individual register handlers stay a residual risk: the real processor reads the same
// packet a moment later.
static uint32_t SpineNormalizeOffset(uint32_t raw_offset) {
	return raw_offset & ~0x70000000u;
}

static uint32_t SpineRegisterPacketSafety(uint32_t opcode, uint32_t cmd, const uint32_t* body, uint32_t len,
                                          bool context_pushed) {
	const uint32_t num_values = len >= 2u ? len - 2u : 0u;
	switch (opcode) {
		case Pm4::IT_SET_CONTEXT_REG: {
			const auto offset = SpineNormalizeOffset(body[0]);
			if (offset == Pm4::CX_NOP) {
				return 0;
			}
			if (offset >= Pm4::CX_NUM) {
				return 1;
			}
			if (g_hw_ctx_func[offset & (Pm4::CX_NUM - 1)] != nullptr) {
				return 0;
			}
			for (uint32_t i = 0; i < num_values; i++) {
				if (offset + i >= Pm4::CX_NUM || g_hw_ctx_indirect_func[(offset + i) & (Pm4::CX_NUM - 1)] == nullptr) {
					return 1;
				}
			}
			return 0;
		}
		case Pm4::IT_SET_SH_REG: {
			const auto offset = body[0];
			if (offset == Pm4::SH_NOP) {
				return 0;
			}
			if (offset >= Pm4::SH_NUM) {
				return 1;
			}
			if (g_hw_sh_func[offset] != nullptr) {
				return 0;
			}
			if (num_values == 0) {
				return 1;
			}
			for (uint32_t i = 0; i < num_values; i++) {
				if (offset + i >= Pm4::SH_NUM || g_hw_sh_indirect_func[offset + i] == nullptr) {
					return 1;
				}
			}
			return 0;
		}
		case Pm4::IT_SET_UCONFIG_REG:
		case Pm4::IT_SET_UCONFIG_REG_INDEX: {
			if (Gen5::AgcIsInternalDataPacket(cmd, body)) {
				return 0;
			}
			const auto offset =
			    opcode == Pm4::IT_SET_UCONFIG_REG_INDEX ? body[0] & 0x0fffffffu : SpineNormalizeOffset(body[0]);
			if (offset == Pm4::UC_NOP) {
				return 0;
			}
			if (offset >= Pm4::UC_NUM) {
				return 1;
			}
			if (g_hw_uc_func[offset & (Pm4::UC_NUM - 1)] != nullptr) {
				return 0;
			}
			for (uint32_t i = 0; i < num_values; i++) {
				if (offset + i >= Pm4::UC_NUM || g_hw_uc_indirect_func[(offset + i) & (Pm4::UC_NUM - 1)] == nullptr) {
					return 1;
				}
			}
			return 0;
		}
		case Pm4::IT_SET_CONTEXT_REG_INDIRECT:
		case Pm4::IT_SET_SH_REG_INDIRECT:
		case Pm4::IT_SET_UCONFIG_REG_INDIRECT: {
			if (len != 5u) {
				return 1;
			}
			const auto* table =
			    reinterpret_cast<const uint32_t*>((static_cast<uint64_t>(body[0]) & 0xfffffffcu) |
			                                      (static_cast<uint64_t>(body[1]) << 32u));
			const uint32_t count = body[3] & 0x3fffu;
			if (count == 0) {
				return 0;
			}
			if (table == nullptr) {
				return 1;
			}
			if (!LibKernel::Memory::IsGpuClean(reinterpret_cast<uint64_t>(table), uint64_t {count} * 8u)) {
				return 2;
			}
			for (uint32_t i = 0; i < count; i++) {
				const auto raw    = table[2u * i];
				const auto offset = SpineNormalizeOffset(raw);
				if (opcode == Pm4::IT_SET_CONTEXT_REG_INDIRECT) {
					if (offset == Pm4::CX_NOP || raw == 0xffffffffu || offset >= Pm4::CX_NUM) {
						continue;
					}
					if (g_hw_ctx_indirect_func[offset & (Pm4::CX_NUM - 1)] == nullptr) {
						return 1;
					}
				} else if (opcode == Pm4::IT_SET_SH_REG_INDIRECT) {
					if (offset == Pm4::SH_NOP || raw == 0xffffffffu) {
						continue;
					}
					if (offset >= Pm4::SH_NUM || g_hw_sh_indirect_func[offset] == nullptr) {
						return 1;
					}
				} else {
					if (offset == Pm4::UC_NOP) {
						continue;
					}
					if (offset >= Pm4::UC_NUM || g_hw_uc_indirect_func[offset & (Pm4::UC_NUM - 1)] == nullptr) {
						return 1;
					}
				}
			}
			return 0;
		}
		case Pm4::IT_CLEAR_STATE: return cmd == 0xc0001200u && (body[0] & ~0xfu) == 0 ? 0 : 1;
		case Pm4::IT_NUM_INSTANCES: return cmd == 0xc0002f00u ? 0 : 1;
		case Pm4::IT_SET_BASE:
			return len == 4u && (body[0] & 0xfu) == 1u && ((cmd >> 1u) & 0x3u) <= 1u ? 0 : 1;
		case Pm4::IT_NOP: {
			const auto r = KYTY_PM4_R(cmd);
			if (r == Pm4::R_DISPATCH_RESET) {
				return cmd == 0xC0001024u ? 0 : 1;
			}
			if (r == Pm4::R_CONTEXT_STATE) {
				if ((len != 3u && len != 5u) || body[0] > static_cast<uint32_t>(ContextStateOperation::PushClear)) {
					return 1;
				}
				const auto operation = static_cast<ContextStateOperation>(body[0]);
				if ((operation == ContextStateOperation::Push || operation == ContextStateOperation::PushClear) &&
				    context_pushed) {
					return 1;
				}
				if (operation == ContextStateOperation::Pop && !context_pushed) {
					return 1;
				}
			}
			return 0;
		}
		default: return 0;
	}
}
'''

CENSUS = r'''
// Session 118, gate "slicecen" (route A stage 4 part 2, docs/session-118/designA4_part2.md; MEASUREMENT ONLY): the
// slice census, GuestGpu thread only.  A frame is finished when the next frame's first element arrives with the gate
// on; a frame number that jumps (the gate was off in between) discards the partial state instead.
namespace SliceCensus {
namespace {

struct State {
	int                   frame   = -1;
	uint32_t              el      = 0;
	uint32_t              run     = 0;
	uint32_t              max_run = 0;
	uint32_t              runs    = 0;
	uint64_t              hist[5] = {};
	std::vector<uint32_t> starts;
	std::vector<uint64_t> images; // (element << 33) | (image index << 1) | written
};

thread_local State g_census;

bool Armed() {
	return Common::Gates::Enabled(Common::Gates::Gate::SliceCensus) && Common::FrameStats::Enabled() &&
	       GuestGpu::IsGpuThread();
}

void CloseRun(State& s) {
	if (s.run == 0) {
		return;
	}
	s.runs++;
	s.max_run = std::max(s.max_run, s.run);
	const auto bucket = s.run < 32 ? 0 : s.run < 128 ? 1 : s.run < 512 ? 2 : s.run < 1024 ? 3 : 4;
	s.hist[bucket]++;
	s.run = 0;
}

void Reset(State& s, int frame) {
	s.frame   = frame;
	s.el      = 0;
	s.run     = 0;
	s.max_run = 0;
	s.runs    = 0;
	std::fill(std::begin(s.hist), std::end(s.hist), 0);
	s.starts.clear();
	s.images.clear();
}

// K4 at W segments: cut at the pass starts nearest to the equal-element points, then for each adjacent pair the share
// of images both use (any) and of images one writes and the other uses (dep), over the smaller set, in permille.
void SegmentOverlap(const State& s, uint32_t w, Common::FrameStats::Counter n_counter,
                    Common::FrameStats::Counter any_counter, Common::FrameStats::Counter dep_counter,
                    Common::FrameStats::Counter fmax_counter) {
	namespace FS = Common::FrameStats;
	std::vector<uint32_t> cuts;
	uint32_t              previous = 0;
	for (uint32_t k = 1; k < w; k++) {
		const auto target = static_cast<uint32_t>(uint64_t {s.el} * k / w);
		uint32_t   best   = 0;
		uint32_t   best_d = UINT32_MAX;
		for (const auto start: s.starts) {
			if (start > previous && start < s.el) {
				const auto d = start > target ? start - target : target - start;
				if (d < best_d) {
					best_d = d;
					best   = start;
				}
			}
		}
		if (best_d == UINT32_MAX) {
			FS::Add(FS::Counter::K4NoCut, 1);
			return;
		}
		cuts.push_back(best);
		previous = best;
	}
	std::vector<std::vector<uint64_t>> segments(w); // (image index << 1) | written
	for (const auto record: s.images) {
		const auto element = static_cast<uint32_t>(record >> 33u);
		const auto segment = static_cast<size_t>(std::upper_bound(cuts.begin(), cuts.end(), element) - cuts.begin());
		segments[segment].push_back(record & 0x1ffffffffull);
	}
	for (auto& segment: segments) {
		std::sort(segment.begin(), segment.end());
		// One entry an image; written if any of its records was a write (the write record sorts right after the read).
		std::vector<uint64_t> merged;
		for (const auto value: segment) {
			if (!merged.empty() && (merged.back() >> 1u) == (value >> 1u)) {
				merged.back() |= value & 1u;
			} else {
				merged.push_back(value);
			}
		}
		segment.swap(merged);
	}
	uint64_t max_any = 0;
	uint64_t max_dep = 0;
	for (uint32_t i = 0; i + 1 < w; i++) {
		const auto& a      = segments[i];
		const auto& b      = segments[i + 1];
		uint64_t    common = 0;
		uint64_t    dep    = 0;
		size_t      ia     = 0;
		size_t      ib     = 0;
		while (ia < a.size() && ib < b.size()) {
			const auto ka = a[ia] >> 1u;
			const auto kb = b[ib] >> 1u;
			if (ka < kb) {
				ia++;
			} else if (kb < ka) {
				ib++;
			} else {
				common++;
				dep += ((a[ia] | b[ib]) & 1u) != 0 ? 1u : 0u;
				ia++;
				ib++;
			}
		}
		const auto smaller = std::min(a.size(), b.size());
		if (smaller != 0) {
			max_any = std::max(max_any, common * 1000u / smaller);
			max_dep = std::max(max_dep, dep * 1000u / smaller);
		}
	}
	uint32_t largest = 0;
	uint32_t begin   = 0;
	for (uint32_t i = 0; i <= cuts.size(); i++) {
		const auto end = i < cuts.size() ? cuts[i] : s.el;
		largest        = std::max(largest, end - begin);
		begin          = end;
	}
	FS::Add(n_counter, 1);
	FS::Add(any_counter, max_any);
	FS::Add(dep_counter, max_dep);
	FS::Add(fmax_counter, s.el != 0 ? uint64_t {largest} * 1000u / s.el : 0);
}

void FinishFrame(State& s) {
	namespace FS  = Common::FrameStats;
	const auto t0 = FS::NowNs();
	CloseRun(s);
	if (s.el != 0) {
		FS::Add(FS::Counter::ScFrames, 1);
		FS::Add(FS::Counter::ScElements, s.el);
		FS::Add(FS::Counter::ScRuns, s.runs);
		FS::Add(FS::Counter::K3MaxRun, s.max_run);
		FS::Add(FS::Counter::K3Hist0, s.hist[0]);
		FS::Add(FS::Counter::K3Hist1, s.hist[1]);
		FS::Add(FS::Counter::K3Hist2, s.hist[2]);
		FS::Add(FS::Counter::K3Hist3, s.hist[3]);
		FS::Add(FS::Counter::K3Hist4, s.hist[4]);
		FS::Add(FS::Counter::ScImages, s.images.size());
		SegmentOverlap(s, 2, FS::Counter::K4W2N, FS::Counter::K4W2Any, FS::Counter::K4W2Dep, FS::Counter::K4W2Fmax);
		SegmentOverlap(s, 4, FS::Counter::K4W4N, FS::Counter::K4W4Any, FS::Counter::K4W4Dep, FS::Counter::K4W4Fmax);
	}
	FS::Add(FS::Counter::ScNs, FS::NowNs() - t0);
}

} // namespace

void Element(int frame) {
	if (!Armed()) {
		return;
	}
	auto& s = g_census;
	if (frame != s.frame) {
		if (s.frame >= 0 && frame == s.frame + 1) {
			FinishFrame(s);
		}
		Reset(s, frame);
	}
	s.el++;
	s.run++;
}

void PassBegin() {
	if (!Armed()) {
		return;
	}
	auto& s = g_census;
	if (s.el == 0) {
		return;
	}
	// The element that begins the pass belongs to the new run.
	s.run--;
	CloseRun(s);
	s.run = 1;
	s.starts.push_back(s.el - 1);
}

void Image(uint32_t image_index, bool write) {
	if (!Armed()) {
		return;
	}
	auto& s = g_census;
	if (s.el == 0) {
		return;
	}
	s.images.push_back((uint64_t {s.el - 1} << 33u) | (uint64_t {image_index} << 1u) | (write ? 1u : 0u));
}

} // namespace SliceCensus
'''

patch('graphics/guest_gpu/graphicsRun.cpp', [
(
"""#include "graphics/guest_gpu/pm4.h"
""",
"""#include "graphics/guest_gpu/pm4.h"
#include "graphics/guest_gpu/sliceCensus.h"
"""),
(
"""// The processor's own draw registers. m_num_instances is left out on purpose: indirect draws rewrite it from
// GPU-written arguments, which the spine cannot read ahead.
""", SAFE + CENSUS + """
// The processor's own draw registers. m_num_instances is left out on purpose: indirect draws rewrite it from
// GPU-written arguments, which the spine cannot read ahead.
"""),
(
"""	if (verify) {
		execution.m_spine_plan = ++m_spine_plan_id;
		m_spine_snap_count     = 0;
	}

	sp.m_ctx                              = m_ctx;
""",
"""	if (verify) {
		execution.m_spine_plan = ++m_spine_plan_id;
		m_spine_snap_count     = 0;
	}

	// Term C (session 118): before seeding, the state the previous complete plan of this processor left is compared
	// member-wise with the real state now. m_num_instances stays out (indirect draws).
	if (m_spine_carry_valid) {
		uint64_t real_regs[8];
		uint64_t spine_regs[8];
		SpineRegs(real_regs);
		sp.SpineRegs(spine_regs);
		uint32_t parts = 0;
		parts |= sp.m_ctx == m_ctx ? 0u : 1u;
		parts |= sp.m_ucfg == m_ucfg ? 0u : 2u;
		parts |= sp.m_sh_ctx == m_sh_ctx ? 0u : 4u;
		parts |= sp.m_saved_ctx == m_saved_ctx ? 0u : 16u;
		uint32_t reg = 8;
		for (uint32_t i = 0; i < 8; i++) {
			if (real_regs[i] != spine_regs[i]) {
				parts |= 8u;
				reg = i;
				break;
			}
		}
		FS::Add(FS::Counter::CarryCmp, 1);
		if (parts != 0) {
			FS::Add(FS::Counter::CarryBad, 1);
			static std::atomic<uint32_t> carry_log_count {0};
			if (carry_log_count.fetch_add(1, std::memory_order_relaxed) < 40) {
				LOGF("SpineCarry: sub=%" PRIu64 " parts=%s%s%s%s%s reg=%u\\n", m_submit_id, (parts & 1u) != 0 ? "ctx," : "",
				     (parts & 2u) != 0 ? "ucfg," : "", (parts & 4u) != 0 ? "sh," : "", (parts & 8u) != 0 ? "cp," : "",
				     (parts & 16u) != 0 ? "saved," : "", reg);
			}
		}
	} else {
		FS::Add(FS::Counter::CarrySkip, 1);
	}
	m_spine_carry_valid = false;

	sp.m_ctx                              = m_ctx;
"""),
(
"""	uint64_t packets = 0, elements = 0, ibs = 0, branches = 0, conds = 0, preds = 0, pred_waits = 0, indirect = 0;
	bool     aborted = false;
""",
"""	uint64_t packets = 0, elements = 0, ibs = 0, branches = 0, conds = 0, preds = 0, pred_waits = 0, indirect = 0;
	bool     aborted   = false;
	bool     uncertain = false; // session 118: a word read early sat on a GPU-dirty page
	uint32_t stop_op   = 0;
"""),
(
"""		const auto  cmd     = header & ~1u;
		const auto* body    = packet + 1;
		uint32_t    advance = len;
		switch (opcode) {
""",
"""		const auto  cmd     = header & ~1u;
		const auto* body    = packet + 1;
		uint32_t    advance = len;
		// Session 118: the structural EXIT conditions of the handlers the spine calls, checked first.
		if (const auto safety = SpineRegisterPacketSafety(opcode, cmd, body, len, sp.m_context_state_pushed);
		    safety != 0) {
			(safety == 2 ? uncertain : aborted) = true;
			stop_op = opcode;
			break;
		}
		switch (opcode) {
"""),
(
"""				} else if (op == 3u && address_value != 0) {
					const auto value    = *reinterpret_cast<const volatile uint64_t*>(address_value);
""",
"""				} else if (op == 3u && address_value != 0) {
					if (!LibKernel::Memory::IsGpuClean(address_value, 8)) {
						uncertain = true;
						break;
					}
					const auto value    = *reinterpret_cast<const volatile uint64_t*>(address_value);
"""),
(
"""				conds++;
				if (*reinterpret_cast<const volatile uint32_t*>(addr) == 0) {
""",
"""				conds++;
				if (!LibKernel::Memory::IsGpuClean(addr, 4)) {
					uncertain = true;
					break;
				}
				if (*reinterpret_cast<const volatile uint32_t*>(addr) == 0) {
"""),
(
"""					if (nested_dw != 0u && nested == nullptr) {
						aborted = true;
						break;
					}
					cur.offset += len; // `cur` is invalidated by the push below
""",
"""					if (nested_dw != 0u && nested == nullptr) {
						aborted = true;
						break;
					}
					if (nested_dw != 0u &&
					    !LibKernel::Memory::IsGpuClean(reinterpret_cast<uint64_t>(nested), uint64_t {nested_dw} * 4u)) {
						uncertain = true;
						break;
					}
					cur.offset += len; // `cur` is invalidated by the push below
"""),
(
"""					branches++;
					const bool take_then = TestWaitRegMemValue(
""",
"""					branches++;
					if (!LibKernel::Memory::IsGpuClean(compare_addr, 8) ||
					    !LibKernel::Memory::IsGpuClean(reinterpret_cast<uint64_t>(then_buffer), uint64_t {then_dw} * 4u) ||
					    (else_buffer != nullptr && else_dw != 0u &&
					     !LibKernel::Memory::IsGpuClean(reinterpret_cast<uint64_t>(else_buffer), uint64_t {else_dw} * 4u))) {
						uncertain = true;
						break;
					}
					const bool take_then = TestWaitRegMemValue(
"""),
(
"""		if (aborted) {
			break;
		}
		if (advance == 0u || advance > remaining) {
""",
"""		if (aborted || uncertain) {
			break;
		}
		if (advance == 0u || advance > remaining) {
"""),
(
"""	const auto elapsed         = FS::NowNs() - t0;
	execution.m_spine_elements = static_cast<uint32_t>(elements);
	if (aborted) {
""",
"""	const auto elapsed         = FS::NowNs() - t0;
	execution.m_spine_elements = static_cast<uint32_t>(elements);
	m_spine_carry_valid        = !aborted && !uncertain;
	if (uncertain) {
		// A plan that could not read a word ahead is neither compared nor carried.
		execution.m_spine_mode = 0;
		FS::Add(FS::Counter::SpineUncertain, 1);
		static std::atomic<uint32_t> uncertain_log_count {0};
		if (uncertain_log_count.fetch_add(1, std::memory_order_relaxed) < 40) {
			LOGF("SpineUncertain: sub=%" PRIu64 " packets=%" PRIu64 " elements=%" PRIu64 " op=0x%02x\\n", m_submit_id,
			     packets, elements, stop_op);
		}
	}
	if (aborted) {
"""),
(
"""			LOGF("SpineAbort: sub=%" PRIu64 " packets=%" PRIu64 " elements=%" PRIu64 "\\n", m_submit_id, packets,
			     elements);
""",
"""			LOGF("SpineAbort: sub=%" PRIu64 " packets=%" PRIu64 " elements=%" PRIu64 " op=0x%02x\\n", m_submit_id,
			     packets, elements, stop_op);
"""),
(
"""		// Knob "spine" (session 117, mode 2): the real register state before this draw/dispatch against the plan.
		if (execution.m_spine_mode == 2 && SpineIsElement(opcode)) {
			SpineCheck(execution, opcode);
		}
""",
"""		// Knob "spine" (session 117, mode 2): the real register state before this draw/dispatch against the plan;
		// gate "slicecen" (session 118): the element for the slice census.
		if (SpineIsElement(opcode)) {
			if (execution.m_spine_mode == 2) {
				SpineCheck(execution, opcode);
			}
			if (Common::Gates::Enabled(Common::Gates::Gate::SliceCensus)) {
				SliceCensus::Element(m_renderer.GetGpu().GetFrameNum());
			}
		}
"""),
])

# ---------------------------------------------------------------------------------------------- the three census hooks
patch('graphics/host_gpu/renderer/context.cpp', [
(
"""#include "common/gates.h"
""",
"""#include "common/gates.h"
#include "graphics/guest_gpu/sliceCensus.h"
"""),
(
"""	EndRenderingImpl(RenderPassEnd::State, packet);
	Common::FrameStats::Add(Common::FrameStats::Counter::RenderPassBegins, 1);
""",
"""	EndRenderingImpl(RenderPassEnd::State, packet);
	Common::FrameStats::Add(Common::FrameStats::Counter::RenderPassBegins, 1);
	SliceCensus::PassBegin(); // gate "slicecen" (session 118): GuestGpu thread only, nothing when off
"""),
])
patch('graphics/host_gpu/renderer/pipeline/descriptors.cpp', [
(
"""#include "graphics/guest_gpu/hardwareContext.h"
""",
"""#include "graphics/guest_gpu/hardwareContext.h"
#include "graphics/guest_gpu/sliceCensus.h"
"""),
(
"""			images[i] = ResolveTexture(program.info.images[i], snapshot.images[i]);
			BindImage(images[i].image_id,
			          images[i].desc.type == TextureCache::BindingType::Storage,
			          program.info.images[i].atomic);
		}
	}
""",
"""			images[i] = ResolveTexture(program.info.images[i], snapshot.images[i]);
			BindImage(images[i].image_id,
			          images[i].desc.type == TextureCache::BindingType::Storage,
			          program.info.images[i].atomic);
		}
	}
	// Gate "slicecen" (session 118): every image this stage touches, written when bound as storage.
	if (Common::Gates::Enabled(Common::Gates::Gate::SliceCensus)) {
		for (uint32_t i = 0; i < program.info.images.size(); i++) {
			SliceCensus::Image(images[i].image_id.index,
			                   images[i].desc.type == TextureCache::BindingType::Storage);
		}
	}
"""),
])
patch('graphics/host_gpu/renderer/renderDraw.cpp', [
(
"""#include "graphics/guest_gpu/hardwareContext.h"
""",
"""#include "graphics/guest_gpu/hardwareContext.h"
#include "graphics/guest_gpu/sliceCensus.h"
"""),
(
"""	EXIT_IF(state.width == 0 || state.height == 0 || state.num_layers == 0 ||
	        state.width == std::numeric_limits<uint32_t>::max() ||
	        state.height == std::numeric_limits<uint32_t>::max());
	return state;
}
""",
"""	EXIT_IF(state.width == 0 || state.height == 0 || state.num_layers == 0 ||
	        state.width == std::numeric_limits<uint32_t>::max() ||
	        state.height == std::numeric_limits<uint32_t>::max());
	// Gate "slicecen" (session 118): the targets this draw writes.
	if (Common::Gates::Enabled(Common::Gates::Gate::SliceCensus)) {
		for (uint32_t i = 0; i < color_count; i++) {
			SliceCensus::Image(colors[i].image_id.index, true);
		}
		if (depth.image_id) {
			SliceCensus::Image(depth.image_id.index, true);
		}
	}
	return state;
}
"""),
])
print('done')
