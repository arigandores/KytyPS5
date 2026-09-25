"""Session 117: route A stage 4 part 1 - knob "spine" (shadow spine plan + verify). Measurement only, default 0.

Design: docs/session-117/designA4_spine.md; ROADMAP 117 items 4-5 (verify by full snapshots and member-wise
equality: clang-cl 19.1.5 has no __builtin_clear_padding).  Anchors are whole lines; every anchor must match once.
"""
from pathlib import Path
import re
import sys

SRC = Path('C:/kyty/KytyPS5/src')
DRY = len(sys.argv) > 1 and sys.argv[1] == '--dry'


def load(rel):
    raw = (SRC / rel).read_bytes().decode('utf-8')
    return raw.replace('\r\n', '\n'), '\r\n' in raw


def store(rel, s, crlf):
    if crlf:
        s = s.replace('\n', '\r\n')
    if not DRY:
        (SRC / rel).write_bytes(s.encode('utf-8'))
    print('patched' if not DRY else 'ok (dry)', rel)


def patch(rel, edits):
    s, crlf = load(rel)
    for old, new in edits:
        n = s.count(old)
        if n != 1:
            raise SystemExit(f'{rel}: anchor found {n} times:\n{old[:200]}')
        s = s.replace(old, new)
    store(rel, s, crlf)


# ---------------------------------------------------------------------------------------------- hardwareContext.h
# Member-wise equality for every register type (61), so the spine's verify can tell a padding-only byte difference
# from a state difference.  The header is outside the shader-translation cache signature (src/generate_version.cmake:
# graphics/shader/**, shaderTranslationCache.cpp, gpu_format.h, gpu_defs.h only).
def patch_hw():
    rel = 'graphics/guest_gpu/hardwareContext.h'
    s, crlf = load(rel)
    lines = s.split('\n')
    inserts = []
    for i, line in enumerate(lines):
        m = re.match(r'^(struct|class) (\w+) \{$', line)
        if not m:
            continue
        depth = 0
        for j in range(i, len(lines)):
            depth += lines[j].count('{') - lines[j].count('}')
            if depth == 0:
                break
        if lines[j] != '};':
            raise SystemExit(f'{rel}: {m.group(2)} does not close with a bare "}};" (line {j + 1})')
        inserts.append((j, m.group(2)))
    if len(inserts) != 61:
        raise SystemExit(f'{rel}: {len(inserts)} types, expected 61')
    for j, name in reversed(inserts):
        lines[j:j] = ['', 'public:',
                      f'\t// Session 117 (knob "spine"): member-wise, so padding bytes never make two states differ.',
                      f'\t[[nodiscard]] bool operator==(const {name}& other) const = default;']
    store(rel, '\n'.join(lines), crlf)


patch_hw()

# ---------------------------------------------------------------------------------------------- gates.h
patch('common/gates.h', [(
"""	// Default 1 from session 115 (seal chk115); before the SDL main loop the title is always posted (session 115).
	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	TitleAsync,       // KYTY_TITLE_ASYNC,        file name "titleasync" (0 wait for the main thread, 1 post)
	Count,
""",
"""	// Default 1 from session 115 (seal chk115); before the SDL main loop the title is always posted (session 115).
	TitleAsync,       // KYTY_TITLE_ASYNC,        file name "titleasync" (0 wait for the main thread, 1 post)
	// Session 117, MEASUREMENT ONLY (route A stage 4, docs/session-117/designA4_spine.md): the shadow spine.  1 = at
	// the start of every submission a second CommandProcessor, seeded from the real one, walks the whole submission
	// through the real register handlers (spine_* counters); 2 = 1 plus a snapshot of the register state before every
	// draw/dispatch, compared member-wise with the real state when the real processor reaches it (spine_cmp /
	// spine_bad).  Read once per submission and latched into Pm4Execution, so it CAN be a schedule arm.  Never changes
	// what executes.  LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	Spine,            // KYTY_SPINE,              file name "spine" (0 off, 1 plan, 2 plan + verify)
	Count,
""")])

# ---------------------------------------------------------------------------------------------- gates.cpp
patch('common/gates.cpp', [(
"""    // presentation-ring fix, kept only if the sealed boot/video check pred/01_chk115.md reads PASS.
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_TITLE_ASYNC", "titleasync", 1, 1},
}};
""",
"""    // presentation-ring fix, kept only if the sealed boot/video check pred/01_chk115.md reads PASS.
    {"KYTY_TITLE_ASYNC", "titleasync", 1, 1},
    // Session 117, MEASUREMENT ONLY: the shadow spine of route A stage 4 (1 plan, 2 plan + verify). Read once per
    // submission, so it CAN be a schedule arm. LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_SPINE", "spine", 0, 2},
}};
""")])

# ---------------------------------------------------------------------------------------------- frameStats.h
patch('common/frameStats.h', [(
"""	PresentOverlap,          // present_overlap
	Count
};
""",
"""	PresentOverlap,          // present_overlap
	// Session 117 (knob "spine", route A stage 4): the shadow spine.  spine_n plans, spine_ns their wall minus the
	// snapshot time (raw ns), spine_pk packets decoded, spine_el draw/dispatch packets planned, spine_ib indirect buffers
	// followed, spine_cf_br 14-dword branches and spine_cf_cond COND_EXEC words evaluated at plan time, spine_cf_pred
	// SET_PREDICATION packets (spine_cf_predw of them with wait_op: the real processor waits for the GPU there, the
	// spine does not), spine_cf_ind indirect draws/dispatches, spine_abort plans that met a packet they cannot follow;
	// at spine=2: spine_cmp compares, spine_bad member-wise mismatches (SpineMismatch: lines), spine_pad compares whose
	// bytes differed only in padding (not a mismatch), spine_misal submissions whose real element count differs from
	// the plan, spine_lost submissions whose snapshots another plan of the same processor replaced (their remaining
	// compares are lost - an instrument limit, not a mismatch), spine_chk_ns snapshot and compare time (raw ns).
	SpineN,                  // spine_n
	SpineNs,                 // spine_ns
	SpinePackets,            // spine_pk
	SpineElements,           // spine_el
	SpineIb,                 // spine_ib
	SpineCfBranch,           // spine_cf_br
	SpineCfCond,             // spine_cf_cond
	SpineCfPred,             // spine_cf_pred
	SpineCfPredWait,         // spine_cf_predw
	SpineCfIndirect,         // spine_cf_ind
	SpineAbort,              // spine_abort
	SpineCmp,                // spine_cmp
	SpineBad,                // spine_bad
	SpineMisalign,           // spine_misal
	SpinePad,                // spine_pad
	SpineLost,               // spine_lost
	SpineCheckNs,            // spine_chk_ns
	Count
};
""")])

# ---------------------------------------------------------------------------------------------- videoOut.cpp
patch('graphics/presentation/videoOut.cpp', [(
"""				    {"present_overlap", FS::Counter::PresentOverlap, false},
				};
""",
"""				    {"present_overlap", FS::Counter::PresentOverlap, false},
				    {"spine_n", FS::Counter::SpineN, false},
				    {"spine_ns", FS::Counter::SpineNs, false},
				    {"spine_pk", FS::Counter::SpinePackets, false},
				    {"spine_el", FS::Counter::SpineElements, false},
				    {"spine_ib", FS::Counter::SpineIb, false},
				    {"spine_cf_br", FS::Counter::SpineCfBranch, false},
				    {"spine_cf_cond", FS::Counter::SpineCfCond, false},
				    {"spine_cf_pred", FS::Counter::SpineCfPred, false},
				    {"spine_cf_predw", FS::Counter::SpineCfPredWait, false},
				    {"spine_cf_ind", FS::Counter::SpineCfIndirect, false},
				    {"spine_abort", FS::Counter::SpineAbort, false},
				    {"spine_cmp", FS::Counter::SpineCmp, false},
				    {"spine_bad", FS::Counter::SpineBad, false},
				    {"spine_misal", FS::Counter::SpineMisalign, false},
				    {"spine_pad", FS::Counter::SpinePad, false},
				    {"spine_lost", FS::Counter::SpineLost, false},
				    {"spine_chk_ns", FS::Counter::SpineCheckNs, false},
				};
""")])

# ---------------------------------------------------------------------------------------------- commandProcessor.h
patch('graphics/guest_gpu/command_processor/commandProcessor.h', [
(
"""#include <cstdint>
#include <span>
#include <vector>
""",
"""#include <cstdint>
#include <memory>
#include <span>
#include <vector>
"""),
(
"""	uint64_t                  m_walk_id       = 0;
	bool                      m_walked_ahead  = false;
};
""",
"""	uint64_t                  m_walk_id       = 0;
	bool                      m_walked_ahead  = false;
	// Session 117, knob "spine" (measurement only): the mode latched when the submission started (0 off, 1 plan,
	// 2 plan + verify), the plan this submission owns (the snapshots live in the processor), the next element the real
	// processor compares, and how many elements the plan saw.
	uint8_t                   m_spine_mode     = 0;
	uint64_t                  m_spine_plan     = 0;
	uint32_t                  m_spine_cursor   = 0;
	uint32_t                  m_spine_elements = 0;
};
"""),
(
"""	void ProcessPm4Baton(Pm4Execution& execution, size_t stop_depth, uint32_t length);
""",
"""	void ProcessPm4Baton(Pm4Execution& execution, size_t stop_depth, uint32_t length);
	// Session 117, knob "spine" (route A stage 4, docs/session-117/designA4_spine.md; measurement only): a second
	// processor, seeded from this one when a submission starts, walks the submission through the real register
	// handlers; at mode 2 the register state before every draw/dispatch is snapshotted by the plan and compared
	// member-wise with the real state before the element's handler runs.
	struct SpineSnap {
		HW::Context    ctx;
		HW::UserConfig ucfg;
		HW::Shader     sh;
		uint64_t       regs[8] = {};
	};
	void SpinePlan(Pm4Execution& execution);
	void SpineCheck(Pm4Execution& execution, uint32_t opcode);
	void SpineFinish(Pm4Execution& execution);
	void SpineRegs(uint64_t* out) const;
"""),
(
"""	uint64_t  m_range_draws                 = 0;
	uint32_t  m_baton_turn                  = 0;
};
""",
"""	uint64_t  m_range_draws                 = 0;
	uint32_t  m_baton_turn                  = 0;
	// Session 117, knob "spine": the shadow processor (created on the first plan; never asked to draw), the snapshots
	// of the latest mode-2 plan (reused, never shrunk) and that plan's number.
	std::unique_ptr<CommandProcessor> m_spine;
	std::vector<SpineSnap>            m_spine_snaps;
	uint32_t                          m_spine_snap_count = 0;
	uint64_t                          m_spine_plan_id    = 0;
};
"""),
])

# ---------------------------------------------------------------------------------------------- graphicsRun.cpp
SPINE_IMPL = r'''
// Session 117, knob "spine" (route A stage 4 part 1, docs/session-117/designA4_spine.md; MEASUREMENT ONLY). The
// spine is the sequential pass route A needs to hand every slice the register state at its start. Here it runs in
// shadow: a second CommandProcessor, seeded from this one when a submission starts, walks the whole submission
// through the SAME register handlers (they touch only the processor they are given), follows indirect buffers and
// evaluates COND_EXEC / branch / predication words itself (their handlers reach the real execution or wait for the
// GPU), and counts draw/dispatch packets. At mode 2 it snapshots its register state before every such packet and the
// real ProcessPm4Range compares the real state with the snapshot before the packet's handler runs: bytes first, then,
// where bytes differ, member by member (padding carries stack garbage on both sides).
static bool SpineIsElement(uint32_t opcode) {
	switch (opcode) {
		case Pm4::IT_DRAW_INDEX_2:
		case Pm4::IT_DRAW_INDEX_OFFSET_2:
		case Pm4::IT_DRAW_INDEX_AUTO:
		case Pm4::IT_DRAW_INDIRECT:
		case Pm4::IT_DRAW_INDEX_INDIRECT:
		case Pm4::IT_DRAW_INDIRECT_MULTI:
		case Pm4::IT_DRAW_INDEX_INDIRECT_MULTI:
		case Pm4::IT_DISPATCH_DRAW_PREAMBLE:
		case Pm4::IT_DISPATCH_DIRECT:
		case Pm4::IT_DISPATCH_INDIRECT: return true;
		default: return false;
	}
}

static bool SpineIsIndirectElement(uint32_t opcode) {
	switch (opcode) {
		case Pm4::IT_DRAW_INDIRECT:
		case Pm4::IT_DRAW_INDEX_INDIRECT:
		case Pm4::IT_DRAW_INDIRECT_MULTI:
		case Pm4::IT_DRAW_INDEX_INDIRECT_MULTI:
		case Pm4::IT_DISPATCH_INDIRECT: return true;
		default: return false;
	}
}

// The processor's own draw registers. m_num_instances is left out on purpose: indirect draws rewrite it from
// GPU-written arguments, which the spine cannot read ahead.
void CommandProcessor::SpineRegs(uint64_t* out) const {
	out[0] = static_cast<uint64_t>(m_user_data_marker);
	out[1] = m_index_type_and_size;
	out[2] = m_index_buffer_size;
	out[3] = m_index_base_addr;
	out[4] = m_draw_indirect_args_base_addr;
	out[5] = m_dispatch_indirect_args_base_addr;
	out[6] = m_predicate_skip ? 1u : 0u;
	out[7] = m_context_state_pushed ? 1u : 0u;
}

void CommandProcessor::SpinePlan(Pm4Execution& execution) {
	namespace FS = Common::FrameStats;
	const auto mode            = Common::Gates::Value(Common::Gates::Knob::Spine);
	execution.m_spine_mode     = static_cast<uint8_t>(mode > 2u ? 2u : mode);
	execution.m_spine_cursor   = 0;
	execution.m_spine_elements = 0;
	execution.m_spine_plan     = 0;
	if (execution.m_spine_mode == 0 || execution.m_buffer_stack.size() != 1) {
		execution.m_spine_mode = 0;
		return;
	}
	if (m_spine == nullptr) {
		m_spine = std::make_unique<CommandProcessor>(m_renderer, m_interrupt_event_id);
		static std::atomic<uint32_t> log_count {0};
		if (log_count.fetch_add(1, std::memory_order_relaxed) == 0) {
			LOGF("Spine: mode=%u snap=%zu ctx=%zu ucfg=%zu sh=%zu\n", static_cast<uint32_t>(mode), sizeof(SpineSnap),
			     sizeof(HW::Context), sizeof(HW::UserConfig), sizeof(HW::Shader));
		}
	}
	auto&      sp      = *m_spine;
	const bool verify  = execution.m_spine_mode == 2;
	const auto t0      = FS::NowNs();
	uint64_t   snap_ns = 0;
	if (verify) {
		execution.m_spine_plan = ++m_spine_plan_id;
		m_spine_snap_count     = 0;
	}

	sp.m_ctx                              = m_ctx;
	sp.m_saved_ctx                        = m_saved_ctx;
	sp.m_context_state_pushed             = m_context_state_pushed;
	sp.m_ucfg                             = m_ucfg;
	sp.m_sh_ctx                           = m_sh_ctx;
	sp.m_user_data_marker                 = m_user_data_marker;
	sp.m_index_type_and_size              = m_index_type_and_size;
	sp.m_index_buffer_size                = m_index_buffer_size;
	sp.m_index_base_addr                  = m_index_base_addr;
	sp.m_draw_indirect_args_base_addr     = m_draw_indirect_args_base_addr;
	sp.m_dispatch_indirect_args_base_addr = m_dispatch_indirect_args_base_addr;
	sp.m_num_instances                    = m_num_instances;
	sp.m_predicate_skip                   = m_predicate_skip;

	struct Cursor {
		std::span<const uint32_t> commands;
		uint32_t                  offset = 0;
	};
	thread_local std::vector<Cursor> stack;
	stack.clear();
	stack.push_back({execution.m_buffer_stack[0].commands, execution.m_buffer_stack[0].offset_dw});
	uint64_t packets = 0, elements = 0, ibs = 0, branches = 0, conds = 0, preds = 0, pred_waits = 0, indirect = 0;
	bool     aborted = false;
	while (!stack.empty()) {
		auto&      cur   = stack.back();
		const auto total = static_cast<uint32_t>(cur.commands.size());
		if (cur.offset >= total) {
			stack.pop_back();
			continue;
		}
		const auto* packet    = cur.commands.data() + cur.offset;
		const auto  remaining = total - cur.offset;
		const auto  header    = packet[0];
		if (header == 0x80000000u) {
			cur.offset++;
			continue;
		}
		const auto len = KYTY_PM4_LEN(header);
		if (remaining < 2u || len > remaining) {
			aborted = true;
			break;
		}
		packets++;
		const auto opcode = (header >> 8u) & 0xffu;
		if ((header & 1u) != 0 && sp.m_predicate_skip) {
			cur.offset += len;
			continue;
		}
		const auto  cmd     = header & ~1u;
		const auto* body    = packet + 1;
		uint32_t    advance = len;
		switch (opcode) {
			case Pm4::IT_SET_CONTEXT_REG:
			case Pm4::IT_SET_SH_REG:
			case Pm4::IT_SET_UCONFIG_REG:
			case Pm4::IT_SET_UCONFIG_REG_INDEX:
			case Pm4::IT_SET_CONTEXT_REG_INDIRECT:
			case Pm4::IT_SET_SH_REG_INDIRECT:
			case Pm4::IT_SET_UCONFIG_REG_INDIRECT:
			case Pm4::IT_CLEAR_STATE:
			case Pm4::IT_SET_BASE:
			case Pm4::IT_INDEX_TYPE:
			case Pm4::IT_INDEX_BASE:
			case Pm4::IT_INDEX_BUFFER_SIZE:
			case Pm4::IT_NUM_INSTANCES:
				// The real handler, on the shadow processor: the register state is reproduced, not re-implemented.
				advance = g_cp_op_func[opcode](sp, cmd, body, remaining, total) + 1u;
				break;
			case Pm4::IT_NOP: {
				const auto r = KYTY_PM4_R(cmd);
				if (r == Pm4::R_CONTEXT_STATE) {
					advance = g_cp_op_func[opcode](sp, cmd, body, remaining, total) + 1u;
				} else if (r == Pm4::R_ZERO && (body[0] & 0xffff0000u) == 0x68750000u) {
					// CpOpMarker: only the two user-data markers are register state; the flips it also carries
					// are not.
					const auto id = body[0] & 0xfffu;
					if (id == 0x4u) {
						sp.m_user_data_marker = HW::UserSgprType::Vsharp;
					} else if (id == 0xdu) {
						sp.m_user_data_marker = HW::UserSgprType::Region;
					}
				}
				break;
			}
			case Pm4::IT_SET_PREDICATION: {
				// SetPredication, without its BufferFlushAndWait: the spine reads the word now.
				preds++;
				const auto payload = len - 1u;
				if (payload < 2u) {
					aborted = true;
					break;
				}
				uint32_t           flags         = 0;
				uint64_t           address_value = 0;
				constexpr uint32_t flags_mask    = 0x00071100u;
				if (payload >= 3u && (body[0] & ~flags_mask) == 0 && body[2] <= 0x0000ffffu) {
					flags         = body[0];
					address_value = (static_cast<uint64_t>(body[2]) << 32u) | (body[1] & 0xfffffff0u);
				} else {
					flags         = body[1];
					address_value = (body[0] & 0xfffffff0u) | (static_cast<uint64_t>(body[1] & 0xffu) << 32u);
				}
				const auto condition = (flags >> 8u) & 0x1u;
				const auto wait_op   = (flags >> 12u) & 0x1u;
				const auto op        = (flags >> 16u) & 0x7u;
				pred_waits += wait_op;
				if (op == 0u) {
					sp.m_predicate_skip = false;
				} else if (op == 3u && address_value != 0) {
					const auto value    = *reinterpret_cast<const volatile uint64_t*>(address_value);
					sp.m_predicate_skip = condition == 0u ? value != 0 : value == 0;
				} else {
					aborted = true;
				}
				break;
			}
			case Pm4::IT_COND_EXEC: {
				const auto payload = len - 1u;
				const auto addr =
				    payload >= 4u ? (static_cast<uint64_t>(body[1]) << 32u) | (body[0] & 0xfffffffcu) : uint64_t {0};
				const auto exec_count = payload >= 4u ? body[3] & 0x3fffu : 0u;
				if (payload < 4u || (body[0] & 0x3u) != 0 || body[2] != 0 || addr == 0 ||
				    payload + exec_count >= remaining) {
					aborted = true;
					break;
				}
				conds++;
				if (*reinterpret_cast<const volatile uint32_t*>(addr) == 0) {
					advance = len + exec_count;
				}
				break;
			}
			case Pm4::IT_INDIRECT_BUFFER: {
				if (len == 4u) {
					const auto* nested =
					    reinterpret_cast<const uint32_t*>(body[0] | (static_cast<uint64_t>(body[1]) << 32u));
					const auto nested_dw = body[2] & 0xfffffu;
					if (nested_dw != 0u && nested == nullptr) {
						aborted = true;
						break;
					}
					cur.offset += len; // `cur` is invalidated by the push below
					if (nested_dw != 0u) {
						ibs++;
						stack.push_back({std::span<const uint32_t>(nested, nested_dw), 0u});
					}
					continue;
				}
				if (len == 14u) {
					const auto compare_addr = (body[1] & 0xfffffff8u) | (static_cast<uint64_t>(body[2]) << 32u);
					const auto mask         = body[3] | (static_cast<uint64_t>(body[4]) << 32u);
					const auto reference    = body[5] | (static_cast<uint64_t>(body[6]) << 32u);
					const auto branch_mode  = body[0] & 0x3u;
					const auto function     = (body[0] >> 8u) & 0x7u;
					const auto* then_buffer = reinterpret_cast<const uint32_t*>(
					    (body[7] & 0xfffffffcu) | (static_cast<uint64_t>(body[8]) << 32u));
					const auto  then_dw     = body[9] & 0xfffffu;
					const auto* else_buffer = reinterpret_cast<const uint32_t*>(
					    (body[10] & 0xfffffffcu) | (static_cast<uint64_t>(body[11]) << 32u));
					const auto else_dw = body[12] & 0xfffffu;
					if (compare_addr == 0 || (branch_mode != 1u && branch_mode != 2u) || function > 6u ||
					    then_buffer == nullptr || then_dw == 0u) {
						aborted = true;
						break;
					}
					branches++;
					const bool take_then = TestWaitRegMemValue(
					    *reinterpret_cast<const volatile uint64_t*>(compare_addr), reference, mask, function);
					cur.offset += len; // `cur` is invalidated by the push below
					if (take_then) {
						stack.push_back({std::span<const uint32_t>(then_buffer, then_dw), 0u});
					} else if (branch_mode == 2u && else_dw != 0u) {
						if (else_buffer == nullptr) {
							aborted = true;
							break;
						}
						stack.push_back({std::span<const uint32_t>(else_buffer, else_dw), 0u});
					}
					continue;
				}
				aborted = true;
				break;
			}
			default:
				if (SpineIsElement(opcode)) {
					elements++;
					indirect += SpineIsIndirectElement(opcode) ? 1u : 0u;
					if (verify) {
						const auto ts = FS::NowNs();
						if (m_spine_snap_count == m_spine_snaps.size()) {
							m_spine_snaps.emplace_back();
						}
						auto& snap = m_spine_snaps[m_spine_snap_count++];
						snap.ctx   = sp.m_ctx;
						snap.ucfg  = sp.m_ucfg;
						snap.sh    = sp.m_sh_ctx;
						sp.SpineRegs(snap.regs);
						snap_ns += FS::NowNs() - ts;
					}
				} else if (g_cp_op_func[opcode] == nullptr) {
					aborted = true;
				}
				break;
		}
		if (aborted) {
			break;
		}
		if (advance == 0u || advance > remaining) {
			aborted = true;
			break;
		}
		cur.offset += advance;
	}
	const auto elapsed         = FS::NowNs() - t0;
	execution.m_spine_elements = static_cast<uint32_t>(elements);
	if (aborted) {
		// An incomplete plan cannot be compared element by element.
		execution.m_spine_mode = 0;
		FS::Add(FS::Counter::SpineAbort, 1);
		static std::atomic<uint32_t> log_count {0};
		if (log_count.fetch_add(1, std::memory_order_relaxed) < 40) {
			LOGF("SpineAbort: sub=%" PRIu64 " packets=%" PRIu64 " elements=%" PRIu64 "\n", m_submit_id, packets,
			     elements);
		}
	}
	FS::Add(FS::Counter::SpineN, 1);
	FS::Add(FS::Counter::SpineNs, elapsed > snap_ns ? elapsed - snap_ns : 0);
	FS::Add(FS::Counter::SpinePackets, packets);
	FS::Add(FS::Counter::SpineElements, elements);
	FS::Add(FS::Counter::SpineIb, ibs);
	FS::Add(FS::Counter::SpineCfBranch, branches);
	FS::Add(FS::Counter::SpineCfCond, conds);
	FS::Add(FS::Counter::SpineCfPred, preds);
	FS::Add(FS::Counter::SpineCfPredWait, pred_waits);
	FS::Add(FS::Counter::SpineCfIndirect, indirect);
	FS::Add(FS::Counter::SpineCheckNs, snap_ns);
}

void CommandProcessor::SpineCheck(Pm4Execution& execution, uint32_t opcode) {
	namespace FS  = Common::FrameStats;
	const auto t0 = FS::NowNs();
	if (execution.m_spine_plan != m_spine_plan_id) {
		// Another submission of this processor planned after this one: its snapshots are gone (instrument limit).
		execution.m_spine_mode = 0;
		FS::Add(FS::Counter::SpineLost, 1);
		return;
	}
	const auto el = execution.m_spine_cursor++;
	FS::Add(FS::Counter::SpineCmp, 1);
	if (el >= m_spine_snap_count) {
		// More real elements than planned: counted once, at SpineFinish.
		FS::Add(FS::Counter::SpineCheckNs, FS::NowNs() - t0);
		return;
	}
	const auto& snap = m_spine_snaps[el];
	uint64_t    regs[8];
	SpineRegs(regs);
	uint32_t   bad  = 0;
	uint32_t   pad  = 0;
	const auto part = [&](const auto& real, const auto& planned, uint32_t bit) {
		if (std::memcmp(&real, &planned, sizeof(real)) == 0) {
			return;
		}
		if (real == planned) {
			pad |= bit;
		} else {
			bad |= bit;
		}
	};
	part(m_ctx, snap.ctx, 1u);
	part(m_ucfg, snap.ucfg, 2u);
	part(m_sh_ctx, snap.sh, 4u);
	if (std::memcmp(regs, snap.regs, sizeof(regs)) != 0) {
		bad |= 8u;
	}
	if (bad != 0) {
		FS::Add(FS::Counter::SpineBad, 1);
		static std::atomic<uint32_t> log_count {0};
		if (log_count.fetch_add(1, std::memory_order_relaxed) < 40) {
			uint32_t reg = 8;
			for (uint32_t i = 0; i < 8; i++) {
				if (regs[i] != snap.regs[i]) {
					reg = i;
					break;
				}
			}
			LOGF("SpineMismatch: sub=%" PRIu64 " el=%u op=0x%02x parts=%s%s%s%s reg=%u\n", m_submit_id, el, opcode,
			     (bad & 1u) != 0 ? "ctx," : "", (bad & 2u) != 0 ? "ucfg," : "", (bad & 4u) != 0 ? "sh," : "",
			     (bad & 8u) != 0 ? "cp," : "", reg);
		}
	} else if (pad != 0) {
		FS::Add(FS::Counter::SpinePad, 1);
	}
	FS::Add(FS::Counter::SpineCheckNs, FS::NowNs() - t0);
}

void CommandProcessor::SpineFinish(Pm4Execution& execution) {
	namespace FS = Common::FrameStats;
	if (execution.m_spine_mode == 2 && execution.m_spine_cursor != execution.m_spine_elements) {
		FS::Add(FS::Counter::SpineMisalign, 1);
		static std::atomic<uint32_t> log_count {0};
		if (log_count.fetch_add(1, std::memory_order_relaxed) < 40) {
			LOGF("SpineMisalign: sub=%" PRIu64 " planned=%u executed=%u\n", m_submit_id, execution.m_spine_elements,
			     execution.m_spine_cursor);
		}
	}
	execution.m_spine_mode = 0;
}

'''

patch('graphics/guest_gpu/graphicsRun.cpp', [
(
"""	if (execution.m_buffer_stack.empty() && !commands.empty()) {
		execution.m_buffer_stack.push_back({commands});
		PrefetchComputePipelines(execution);
	}
""",
"""	if (execution.m_buffer_stack.empty() && !commands.empty()) {
		execution.m_buffer_stack.push_back({commands});
		PrefetchComputePipelines(execution);
		SpinePlan(execution); // knob "spine" (session 117): measurement only, nothing at 0
	}
"""),
(
"""		Common::FrameStats::Add(bucket, 1);
	}
	return execution.m_buffer_stack.empty() ? Pm4ProcessResult::Complete
	                                        : Pm4ProcessResult::Blocked;
}
""",
"""		Common::FrameStats::Add(bucket, 1);
	}
	if (execution.m_spine_mode != 0 && execution.m_buffer_stack.empty()) {
		SpineFinish(execution);
	}
	return execution.m_buffer_stack.empty() ? Pm4ProcessResult::Complete
	                                        : Pm4ProcessResult::Blocked;
}
""" + SPINE_IMPL),
(
"""		auto handler = g_cp_op_func[opcode];

		if (handler == nullptr) {
			const auto offset = total_dw - remaining_dw;
""",
"""		// Knob "spine" (session 117, mode 2): the real register state before this draw/dispatch against the plan.
		if (execution.m_spine_mode == 2 && SpineIsElement(opcode)) {
			SpineCheck(execution, opcode);
		}

		auto handler = g_cp_op_func[opcode];

		if (handler == nullptr) {
			const auto offset = total_dw - remaining_dw;
"""),
])
print('done')
