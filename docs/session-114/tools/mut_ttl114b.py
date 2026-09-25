"""Session 114, seal 02b (ROADMAP s0.1, the session-114 records, item 8): mutation check of ttl114b.py against
test_ttl114b.py, derived from mut_ttl114.py (the draft list: with the two draft-only seal mutants, which apply to this
draft again) by make_ttl114b.py (whole-line anchored replacements).  ttl114b is ttl114 with the arm-1 cap
TITLE_WALL_MAX_NS = 60 000 ns (was 20 000) and P2 <= 60 us (was 20).  Re-anchored on the new values:
TITLE_WALL_MAX_59999 / TITLE_WALL_MAX_60001 / TITLE_WALL_MAX_in_us (60) (were _19999 / _20001 / 20), PRED_P2_arm0,
PRED_P2_hi_59 / PRED_P2_hi_61 (were _hi_19 / _hi_21), PRED_P2_bounded, CONST_pred_shn113 and CONST_pred_ctl114 (on
PRED = pred/02b_ttl114b.md).  Added, ttl114's own values: TITLE_WALL_MAX_20000, PRED_P2_hi_20, CONST_pred_ttl114.
Every other mutant is mut_ttl114.py's, unchanged (347 = 344 + 3).  Paths: C:/kyty/s114/ttl114b_draft.  The
description of mut_ttl114.py follows.

Session 114: mutation check of ttl114.py against test_ttl114.py, derived from session 113's sealed mut_shn113.py by
make_ttl114.py (whole-line anchored replacements).  Each mutant disables or weakens ONE admission / decision term,
verdict branch, prediction, schema entry, marker, sealed constant, estimator window, threshold or refusal of main()
(anchored replace, asserted to match exactly once).  Included: every mutant of mut_shn113.py that still applies
(re-anchored where the text changed: the rule S1 d mean <= +50 / S2 d mean + 2SE <= +200 with its edges, the video
gate text, the sealed constants, tags and texts on ttl114, P1-P7, the quoted size and the claims), and the session-114
changes: TITLE_COUNTED and TITLE_ARMED (off, one arm or one clause dropped, arms swapped, threshold and constant edges,
strict against non-strict, per call against per flip, the main window against all rows, missing levels, other
counters read), the eight new FrameTrace-x counters in the schema (each out, two moved to another line), the GC
trigger shift and the knob out of the launch and the video, S2's own bar, d flip_rsv_wait_ns in the pair keys and the
report, the title / hold / main-task lines as non-markers.  Dropped with the code they mutated (no anchor left):
session 113's REGIME_* / SCAN_arms_swapped, NARROW_*, NO_CHECK_*, NO_XTHR_*, VIDEO_shift_off, ENV_shift_*, the
bda_scan / bda_nskip P1 / P2 / P6 mutants (P2 has no lower bound now), PRED_P4_text_medium and CLAIM_dropped.  The two
draft-only seal mutants (CONST_pred_sha_prefilled, CONST_pred_bytes_prefilled) apply to this draft.  Run by the frozen
mutlib v2 (docs/session-113/mutlib/v2/mutlib.py --control --no-memo); the loop below is the legacy harness: each
mutant runs the full fixture suite in its own fixture directory (C:/kyty/s114/ttl114b_draft/ttl114b/fx_mut/w<k>, removed
at the end); a mutant is KILLED when the suite does not print ALL OK.  The unmutated scorer runs first in the same
harness and must print ALL OK.
    python mut_ttl114b.py [<workers>]
"""
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path('C:/kyty/s114/ttl114b_draft')
SCORER = HERE / 'ttl114b.py'
TEST = HERE / 'test_ttl114b.py'
MUT = HERE / 'ttl114b' / 'mutants'
FX = HERE / 'ttl114b' / 'fx_mut'
WORKERS = int(sys.argv[1]) if len(sys.argv) > 1 else 16
SRC = SCORER.read_bytes().decode('utf-8')
NL = chr(10)

M = {}


def mutant(name, old, new):
    assert name not in M, name
    M[name] = (old, new)


# ==== ported from mut_net112.py (itself from mut_shp111.py / mut_shp110.py) =======================================================================================
# ---- decision terms and verdict branches ----------------------------------------------------------------------------
mutant('S1_off', "'S1_dt_le_+50': dt['mean'] is not None and dt['mean'] <= SHIP_US,", "'S1_dt_le_+50': True,")
mutant('S1_bar_+50', "dt['mean'] <= SHIP_US,", "dt['mean'] <= SHIP_US + 50,")
mutant('S2_off', "'S2_dt_2se_le_+200': (dt['mean']", "'S2_dt_2se_le_+200': True or (dt['mean']")
mutant('S2_1se', "and dt['mean'] + 2 * dt['se'] <= S2_US)", "and dt['mean'] + 1 * dt['se'] <= S2_US)")
mutant('MEASURED_any', "measured = bool(rules) and all(rules.values())", "measured = bool(rules) and any(rules.values())")
mutant('BRANCH_not_admitted_off', "    if not admitted:" + NL, "    if out['draft']:" + NL)
mutant('BRANCH_bar_off', "    elif not measured:", "    elif False:")
mutant('BRANCH_ship_off', "    elif video == 'PASS':", "    elif False:")
mutant('BRANCH_fail_as_ship', "    elif video == 'PASS':", "    elif video != 'ABSENT':")
mutant('BRANCH_fail_as_pending', "    elif video == 'ABSENT':", "    elif True:")
mutant('STATUS_always_admitted', "out['status'] = 'INVALID' if failed else 'ADMITTED'", "out['status'] = 'ADMITTED'")
mutant('STATUS_draft_admitted', "        out['status'] = 'DRAFT'", "        out['status'] = 'ADMITTED'")
mutant('PROTOCOL_not_failing', "        failed.append('protocol')", "        pass")

# ---- the video pass -------------------------------------------------------------------------------------------------
mutant('VIDEO_binary_off', "'binary': meta.get('binary_sha256') == BINARY_SHA,", "'binary': True,")
GATE = "' dawalk=1 ' in gates and ' titleasync=1 ' in gates,"
mutant('VIDEO_gate_title_off', GATE, "' dawalk=1 ' in gates,")
mutant('VIDEO_gate_dawalk_off', GATE, "' titleasync=1 ' in gates,")
mutant('VIDEO_gate_is_arm0', GATE, "' dawalk=1 ' in gates and ' titleasync=0 ' in gates,")
mutant('VIDEO_gate_any_mode', GATE, "' dawalk=1 ' in gates and ' titleasync=' in gates,")
mutant('VIDEO_gate_is_shn113', GATE, "' dawalk=1 ' in gates and ' bdanarrow=1 ' in gates,")
mutant('VIDEO_pin_off', "'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1',", "'pinned': True,")
mutant('VIDEO_shift_required', "        'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1'," + NL,
       "        'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1'," + NL
       + "        'shifted': env.get('KYTY_BUFFER_GC_TRIGGER_SHIFT_MB') == '1024'," + NL)
mutant('ENV_shift_readded', "'KYTY_GPU_MARKERS': '0'}", "'KYTY_GPU_MARKERS': '0', 'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '1024'}")
mutant('ENV_title_in_launch', "'KYTY_GPU_MARKERS': '0'}", "'KYTY_GPU_MARKERS': '0', 'KYTY_TITLE_ASYNC': '1'}")
mutant('VIDEO_recorded_off', "'recorded': bool(env.get('KYTY_REC')),", "'recorded': True,")
mutant('VIDEO_schedule_off', "'no_schedule': not env.get('KYTY_GATE_SCHEDULE'),", "'no_schedule': True,")
mutant('VIDEO_ckpt_off', "'no_checkpoints': 'KYTY_GPU_CHECKPOINTS' not in env,", "'no_checkpoints': True,")
mutant('VIDEO_attempt_exit_off', "                          and all(a.get('hold_exit') is None for a in attempts),",
       "                          and True,")
mutant('VIDEO_attempt_list_off', "[a.get('outcome') for a in attempts] == ['ok']", "all(a.get('outcome') == 'ok' for a in attempts)")
mutant('VIDEO_frames_1000', 'VIDEO_MIN_FRAMES = 3000', 'VIDEO_MIN_FRAMES = 1000')
mutant('VIDEO_glitch_off', "'no_glitch': glitches == 0,", "'no_glitch': True,")

# ---- integrity ------------------------------------------------------------------------------------------------------
mutant('PREREG_off', "integrity['PREREG_PINNED'] = (PRED_SHA is not None", "integrity['PREREG_PINNED'] = True or (PRED_SHA is not None")
mutant('BINARY_off', "integrity['BINARY_SEALED'] = meta.get('binary_sha256') == BINARY_SHA",
       "integrity['BINARY_SEALED'] = True")
mutant('SCHEMA_off', "integrity['SCHEMA'] = not run['bad']", "integrity['SCHEMA'] = True")
mutant('SCHEMA_no_cspfree_moved', "'cspfree_bad': 'x', 'cspfree_moved': 'x',", "'cspfree_bad': 'x',")
mutant('FIELD_ORIGIN_off', "integrity['FIELD_ORIGIN'] = not wrong", "integrity['FIELD_ORIGIN'] = True")
mutant('RAW_CONTIG_off', "integrity['RAW_CONTIGUITY'] = (bool(order)", "integrity['RAW_CONTIGUITY'] = True or (bool(order)")
mutant('DURATION_off', "integrity['DURATION'] = (sum(", "integrity['DURATION'] = True or (sum(")
mutant('GATEARM_off', "integrity['GATEARM'] = ok_gate", "integrity['GATEARM'] = True")
mutant('ABBA_pattern_unchecked', "or g['arm'] != (0, 1, 1, 0)[i % 4] ", "")          # audit-108 survivor 1
mutant('GATEARM_abba_unchecked', "(g['arms'], g['period'], g['abba']) != (2, geo['period'], 1)",
       "(g['arms'], g['period']) != (2, geo['period'])")
mutant('GATEARM_arms_unchecked', "(g['arms'], g['period'], g['abba']) != (2, geo['period'], 1)",
       "(g['period'], g['abba']) != (geo['period'], 1)")
mutant('GATEARM_period_unchecked', "(g['arms'], g['period'], g['abba']) != (2, geo['period'], 1)",
       "(g['arms'], g['abba']) != (2, 1)")
mutant('GATEARM_frame_unchecked', "or g['frame'] != geo['start'] + geo['period'] * i", "or False")
mutant('GATEARM_text_unchecked', "or g['text'] != ARMS[g['arm']]", "or False")
mutant('GATEARM_block_unchecked', "if (g['block'] != i or", "if (False or")
mutant('GATEARM_malformed_ok', "            ok_gate = False" + NL + "            continue", "            continue")
mutant('GATEARM_empty_ok', "ok_gate = bool(gate_blocks)", "ok_gate = True")
mutant('NO_FLOOR_off', "integrity['NO_FLOOR'] = all(", "integrity['NO_FLOOR'] = True or all(")
mutant('NO_FLOOR_first_key', "for k in FLOOR_KEYS)", "for k in FLOOR_KEYS[:1])")
mutant('MARKERS_OFF_off', "integrity['MARKERS_OFF'] = sum(", "integrity['MARKERS_OFF'] = True or sum(")
mutant('NO_RECORDING_off', "integrity['NO_RECORDING'] = counts['recording'] == 0", "integrity['NO_RECORDING'] = True")
mutant('STREAMS_off', "integrity['STREAMS_COMPLETE'] = not missing", "integrity['STREAMS_COMPLETE'] = True")
mutant('ROW_ARMS_off', "integrity['ROW_ARMS'] = all(", "integrity['ROW_ARMS'] = True or all(")
mutant('AB_BA_off', "integrity['AB_BA_BALANCED'] = orient[0] == orient[1] and orient[0] > 0",
       "integrity['AB_BA_BALANCED'] = True")
mutant('IDENTITY_off', "result['integrity']['IDENTITY'] = (exe_sha == result.get('binary_sha256') == BINARY_SHA)",
       "result['integrity']['IDENTITY'] = True")
mutant('IDENTITY_meta_only', "result['integrity']['IDENTITY'] = (exe_sha == result.get('binary_sha256') == BINARY_SHA)",
       "result['integrity']['IDENTITY'] = (result.get('binary_sha256') == BINARY_SHA)")

# ---- controls -------------------------------------------------------------------------------------------------------
mutant('PIN_ONCE_off', "controls['PIN_ONCE'] = pins.get('1', 0) == 1 and sum(pins.values()) == 1",
       "controls['PIN_ONCE'] = True")
mutant('PIN_ONCE_any', "controls['PIN_ONCE'] = pins.get('1', 0) == 1 and sum(pins.values()) == 1",
       "controls['PIN_ONCE'] = pins.get('1', 0) >= 1")
mutant('PIN_ONCE_count_only', "controls['PIN_ONCE'] = pins.get('1', 0) == 1 and sum(pins.values()) == 1",
       "controls['PIN_ONCE'] = sum(pins.values()) == 1")
mutant('REC_TWO_off', "controls['RECORD_THREAD_TWO'] = counts['rec_started'] == 2", "controls['RECORD_THREAD_TWO'] = True")
mutant('CKPT_LINE_off', "controls['NO_CHECKPOINT_LINE'] = (counts['ckpt_lines'] == 0", "controls['NO_CHECKPOINT_LINE'] = True or (counts['ckpt_lines'] == 0")
mutant('CKPT_off_lines_unchecked', "                                      and counts['ckpt_off_lines'] == 0)", "                                      and True)")
mutant('CKPT_diag_unchecked', "counts['ckpt_lines'] == 0 and counts['ckpt_diag'] == 0", "counts['ckpt_lines'] == 0")
mutant('HANG_off', "controls['NO_GPUHANGABORT'] = counts['hang'] == 0", "controls['NO_GPUHANGABORT'] = True")
mutant('FATAL_off', "controls['NO_FATAL_MARKER'] = not counts['fatal']", "controls['NO_FATAL_MARKER'] = True")
mutant('FATAL_no_skipped_draw', "b'AsyncPipelines: skipped draw')", "b'AsyncPipelines: skipped draw XX')")
mutant('FATAL_stdout_unscanned', "                scan_markers(raw, counts)" + NL + "    usable", "                pass" + NL + "    usable")
mutant('ENV_CKPT_off', "controls['ENV_NO_CHECKPOINTS'] = 'KYTY_GPU_CHECKPOINTS' not in env",
       "controls['ENV_NO_CHECKPOINTS'] = True")
mutant('MIN_PAIRS_1', 'MIN_PAIRS = 60', 'MIN_PAIRS = 1')
mutant('BANDS_off', "controls['BANDS'] = all(", "controls['BANDS'] = True or all(")
mutant('BANDS_arm0_only', "for k, (lo, hi) in BANDS.items() for a in (0, 1))", "for k, (lo, hi) in BANDS.items() for a in (0,))")
mutant('WORK_SPLIT_off', "controls['WORK_SPLIT'] = ws['passed']", "controls['WORK_SPLIT'] = True")
mutant('AREA_VERDICT_off', "controls['AREA_VERDICT'] = bool(av.get('valid'))", "controls['AREA_VERDICT'] = True")
mutant('AREA_SELECTED_off', "controls['AREA_SELECTED'] = bool(", "controls['AREA_SELECTED'] = True or bool(")
mutant('ARMING_off', "controls['ARMING'] = arm['passed']", "controls['ARMING'] = True")
mutant('SYNC_off', "controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK", "controls['SYNC_COMPILE'] = True")
mutant('SYNC_slack3', "controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK",
       "controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK + 1")
mutant('SYNC_kept_rows_only',
       "sync = {a: sum(r.get('cs_sync_new', 0) for n, r in rows.items() if n >= geo['first'] and r.get('arm') == a)",
       "sync = {a: sum(rows[n].get('cs_sync_new', 0) for n in sel['rows'] if rows[n].get('arm') == a)")
mutant('SYNC_arm_swapped', "controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK",
       "controls['SYNC_COMPILE'] = sync[0] <= sync[1] + SYNC_SLACK")

# ---- arming sub-checks (the walk checks and INSTRUMENTS_DARK; SLOT_* / DEFAULTS_ON below) ---------------------------
mutant('WALK_ARMED0_off', "checks['WALK_ARMED_ARM0'] = bool(", "checks['WALK_ARMED_ARM0'] = True or bool(")
mutant('WALK_ARMED1_off', "checks['WALK_ARMED_ARM1'] = bool(", "checks['WALK_ARMED_ARM1'] = True or bool(")
mutant('WALK_IDENT_off', "checks['WALK_IDENTITY_ARM%d' % a] = idn is not None and abs(idn) <= ID_TOL",
       "checks['WALK_IDENTITY_ARM%d' % a] = True")
mutant('WALK_DROPS_off', "checks['WALK_DROPS_ARM%d' % a] = bool(po) and dr is not None and dr / po <= DROP_MAX",
       "checks['WALK_DROPS_ARM%d' % a] = True")
mutant('WALKS_SAME_off', "checks['WALKS_SAME'] = rw is not None and abs(rw) <= WALKS_TOL", "checks['WALKS_SAME'] = True")
mutant('DARK_off', "    checks['INSTRUMENTS_DARK'] = dark", "    checks['INSTRUMENTS_DARK'] = True")
mutant('DARK_first_key', "for a in (0, 1) for k in DARK_KEYS)", "for a in (0, 1) for k in DARK_KEYS[:1])")

# ---- protocol -------------------------------------------------------------------------------------------------------
mutant('P_env_expected_off', "        if kyty.get(key) != value:", "        if False:")
mutant('P_env_schedule_off', "    if kyty.get('KYTY_GATE_SCHEDULE') != SCHEDULE:", "    if False:")
mutant('P_meta_schedule_off', "    if (meta.get('schedule') or '') != SCHEDULE:", "    if False:")
mutant('P_present_off', "        if key not in kyty:", "        if False:")
mutant('P_extra_off', "    if extra:", "    if False:")
mutant('P_gates_sha_off', "    if gates_sha != GATES_SHA:", "    if False:")
mutant('P_gates_text_off', "    if meta.get('gates') != gates_text:", "    if False:")
mutant('P_attempt_labels_off', "    if [a.get('label') for a in attempts] != ['attempt 1']:", "    if False:")
mutant('P_attempt_outcome_off', "        if a.get('outcome') != 'ok':", "        if False:")
mutant('P_attempt_exit_off', "        if a.get('hold_exit') is not None:", "        if False:")
mutant('P_attempt_hold_off', "        if (a.get('hold_s') or 0) < HOLD_S - 5:", "        if False:")
mutant('P_meta_hold_off', "    if meta.get('hold_s') != HOLD_S:", "    if False:")

# ---- main(): the seal and the refusals ------------------------------------------------------------------------------
mutant('SEAL_unfilled_ok', "    if want_sha is None or want_bytes is None:", "    if False:")
mutant('SEAL_compare_off', "    if got != want_sha or len(data) != want_bytes:", "    if False:")
mutant('ROOT_off', "        if Path(o.root).as_posix().rstrip('/') != PRODUCTION_ROOT:", "        if False:")
mutant('TAG_off', "        if not re.fullmatch(TAG_RE, o.tag):", "        if False:")
mutant('GEOM_off', "        if geometry:" + NL + "            print(", "        if False:" + NL + "            print(")
mutant('OUT_exists_off', "        if path.exists():", "        if False:")
mutant('OUT_root_off', "        if not o.draft and not path.as_posix().startswith(PRODUCTION_ROOT + '/'):", "        if False:")

# ---- the reported, never deciding cpu_net (audit-108 survivor 2) ----------------------------------------------------
mutant('CPU_NET_no_spin', "out['cpu_net_us'] = row['cpu_gpu_us'] - row['spin_gpu_us']", "out['cpu_net_us'] = row['cpu_gpu_us']")

# ---- the session-109 audit's mutants (audit109/newmut.py) ------------------------------------------------------------
mutant('KEEP_shift1', "kept = expected[lo:hi]", "kept = expected[lo - 1:hi - 1]")
mutant('KEEP_shift_up1', "kept = expected[lo:hi]", "kept = expected[lo + 1:hi + 1]")
mutant('SE_pstdev', "sd = statistics.stdev(values)", "sd = statistics.pstdev(values)")
mutant('LEVEL_mean', "return statistics.median(values) if values else None",
       "return statistics.fmean(values) if values else None")
mutant('FATAL_no_waitslow', " b'GpuWaitSlow:',", "")
mutant('PAIR_step2', "for b in range(0, top + 1, 4):", "for b in range(0, top + 1, 2):")
mutant('PAIR_left_is_arm0', "a0 = left if arms[left] == 0 else right", "a0 = left")
mutant('FIRST_ignored', "if len(kept) != hi - lo or min(kept) < first:", "if len(kept) != hi - lo:")
mutant('DURATION_half', ">= (meta.get('hold_s') or 0))", ">= (meta.get('hold_s') or 0) / 2)")
mutant('WORK_TOL_10x', "WORK_TOL = 0.005", "WORK_TOL = 0.05")
mutant('AREA_TOL_10x',
       "AREA_SPLIT_PCT, AREA_MATCH_PCT, AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 8",
       "AREA_SPLIT_PCT, AREA_MATCH_PCT, AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 5.0, 0.5, 8")
mutant('SYNC_slack_1000', "controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK",
       "controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK + 1000")
mutant('PAIRS_min_60_to_10', "MIN_PAIRS = 60", "MIN_PAIRS = 10")
mutant('BANDS_dt_wide', "BANDS = {'dt_us': (28000.0, 40000.0),", "BANDS = {'dt_us': (1.0, 99000.0),")

# ---- the session-110 audit's shp110 mutants (audit110/newmut.py; shp_keep_full is MAIN_full_block below) --------------
mutant('FIRST_1800', 'PERIOD, START, FIRST_FRAME = 90, 1800, 2100', 'PERIOD, START, FIRST_FRAME = 90, 1800, 1800')
mutant('MIN_PAIRS_6', 'MIN_PAIRS = 60', 'MIN_PAIRS = 6')
mutant('SHIP_bar_+50.5', 'SHIP_US = 50.0', 'SHIP_US = 50.5')
mutant('SHIP_bar_+49.5', 'SHIP_US = 50.0', 'SHIP_US = 49.5')
mutant('SHIP_bar_-100', 'SHIP_US = 50.0', 'SHIP_US = -100.0')             # session 113's bar
mutant('S2_bar_+200.5', 'S2_US = 200.0', 'S2_US = 200.5')
mutant('S2_bar_+199.5', 'S2_US = 200.0', 'S2_US = 199.5')
mutant('S2_bar_0', 'S2_US = 200.0', 'S2_US = 0.0')                        # session 113's S2 edge
mutant('S2_reads_ship_bar', "and dt['mean'] + 2 * dt['se'] <= S2_US)", "and dt['mean'] + 2 * dt['se'] <= SHIP_US)")
mutant('DROP_MAX_half', 'DROP_MAX = 0.05', 'DROP_MAX = 0.5')
mutant('VIDEO_frames_300', 'VIDEO_MIN_FRAMES = 3000', 'VIDEO_MIN_FRAMES = 300')
mutant('WALKS_TOL_half', 'WALKS_TOL = 0.05', 'WALKS_TOL = 0.5')

# ---- markers and the ported schema -----------------------------------------------------------------------------------
mutant('FATAL_no_error', "(b'--- Error ---', ", "(")
mutant('FATAL_csstall', "b'AsyncPipelines: skipped draw')", "b'AsyncPipelines: skipped draw', b'CsStall:')")
mutant('FATAL_slotverify', "b'AsyncPipelines: skipped draw')", "b'AsyncPipelines: skipped draw', b'DaSlotVerify:')")
mutant('SCHEMA_no_cs_sync_new_us', "    'cs_sync_new_us': 'x', 'cs_sync_wait_us': 'x'," + NL,
       "    'cs_sync_wait_us': 'x'," + NL)
mutant('SCHEMA_no_cs_sync_wait_us', "    'cs_sync_new_us': 'x', 'cs_sync_wait_us': 'x'," + NL,
       "    'cs_sync_new_us': 'x'," + NL)
mutant('SCHEMA_new_us_on_draw', "'cs_sync_new_us': 'x',", "'cs_sync_new_us': 'draw',")

# ==== session 111 =====================================================================================================
# ---- the MAIN estimator's window: bounds 9 / 10 / 89 / 90, the full block, the old window as main ---------------------
mutant('MAIN_lo_9', NL + 'KEEP_LO, KEEP_HI = 10, 90', NL + 'KEEP_LO, KEEP_HI = 9, 90')
mutant('MAIN_lo_11', NL + 'KEEP_LO, KEEP_HI = 10, 90', NL + 'KEEP_LO, KEEP_HI = 11, 90')
mutant('MAIN_hi_89', NL + 'KEEP_LO, KEEP_HI = 10, 90', NL + 'KEEP_LO, KEEP_HI = 10, 89')
mutant('MAIN_hi_91', NL + 'KEEP_LO, KEEP_HI = 10, 90', NL + 'KEEP_LO, KEEP_HI = 10, 91')
mutant('MAIN_full_block', NL + 'KEEP_LO, KEEP_HI = 10, 90', NL + 'KEEP_LO, KEEP_HI = 0, 90')
mutant('MAIN_is_old_window', NL + 'KEEP_LO, KEEP_HI = 10, 90', NL + 'KEEP_LO, KEEP_HI = 60, 89')
mutant('MAIN_geo_is_secondary', "    geo = dict(period=PERIOD, start=START, first=FIRST_FRAME, keep=(KEEP_LO, KEEP_HI),",
       "    geo = dict(period=PERIOD, start=START, first=FIRST_FRAME, keep=(SECONDARY_LO, SECONDARY_HI),")
# ---- the secondary window: its bounds, computed on the main window, swapped into the decision / the predictions ------
mutant('SEC_lo_59', NL + 'SECONDARY_LO, SECONDARY_HI = 60, 89', NL + 'SECONDARY_LO, SECONDARY_HI = 59, 89')
mutant('SEC_lo_61', NL + 'SECONDARY_LO, SECONDARY_HI = 60, 89', NL + 'SECONDARY_LO, SECONDARY_HI = 61, 89')
mutant('SEC_hi_88', NL + 'SECONDARY_LO, SECONDARY_HI = 60, 89', NL + 'SECONDARY_LO, SECONDARY_HI = 60, 88')
mutant('SEC_hi_90', NL + 'SECONDARY_LO, SECONDARY_HI = 60, 89', NL + 'SECONDARY_LO, SECONDARY_HI = 60, 90')
mutant('SEC_on_main_window', "geo['first'], geo['secondary'])", "geo['first'], geo['keep'])")
mutant('SEC_swap_into_decision', "    rules = ship_rules(dt)", "    rules = ship_rules(out['secondary']['pair_stats']['dt_us'])")
mutant('SEC_swap_into_predictions', "out['predictions'] = predictions(stats, lev, arm)",
       "out['predictions'] = predictions(out['secondary']['pair_stats'], lev, arm)")
mutant('SEC_rules_dropped', "    out['rules_not_deciding'] = ship_rules(stats['dt_us'])",
       "    out['rules_not_deciding'] = {}")
mutant('GEOM_secondary_dropped', "('keep', o.keep), ('secondary', o.secondary)) if v is not None}",
       "('keep', o.keep)) if v is not None}")
# ---- arming: TITLE_COUNTED (session 114; the pres_title_n level in both arms) ---------------------------------------
TC = "checks['TITLE_COUNTED'] = bool((tn[0] or 0) >= 1 and (tn[1] or 0) >= 1)"
mutant('TITLE_COUNTED_off', TC, "checks['TITLE_COUNTED'] = True")
mutant('TITLE_COUNTED_arm0_unchecked', TC, "checks['TITLE_COUNTED'] = bool((tn[1] or 0) >= 1)")
mutant('TITLE_COUNTED_arm1_unchecked', TC, "checks['TITLE_COUNTED'] = bool((tn[0] or 0) >= 1)")
mutant('TITLE_COUNTED_gt1', TC, "checks['TITLE_COUNTED'] = bool((tn[0] or 0) > 1 and (tn[1] or 0) > 1)")
mutant('TITLE_COUNTED_gt0', TC, "checks['TITLE_COUNTED'] = bool((tn[0] or 0) > 0 and (tn[1] or 0) > 0)")
mutant('TITLE_COUNTED_ge_half', TC, "checks['TITLE_COUNTED'] = bool((tn[0] or 0) >= 0.5 and (tn[1] or 0) >= 0.5)")
mutant('TITLE_COUNTED_none_passes', TC,
       "checks['TITLE_COUNTED'] = (tn[0] is None or tn[0] >= 1) and (tn[1] is None or tn[1] >= 1)")
mutant('TITLE_COUNTED_all_rows', TC, "checks['TITLE_COUNTED'] = all(sum(r.get('pres_title_n', 0) for r in "
       "rows.values() if r.get('arm') == a) >= 1 for a in (0, 1))")
TL = "tn = [lev[a].get('pres_title_n') for a in (0, 1)]"
mutant('TITLE_COUNTED_reads_ns', TL, "tn = [lev[a].get('pres_title_ns') for a in (0, 1)]")
mutant('TITLE_COUNTED_reads_mt', TL, "tn = [lev[a].get('mt_n') for a in (0, 1)]")
mutant('TITLE_COUNTED_reads_rsv', TL, "tn = [lev[a].get('flip_rsv_wait_n') for a in (0, 1)]")
mutant('TITLE_n_arms_swapped', TL, "tn = [lev[a].get('pres_title_n') for a in (1, 0)]")
# ---- arming: TITLE_ARMED (session 114; the per-call wall of UpdateTitle: cap and strictly below arm 0) --------------
mutant('TITLE_ARMED_off', "    checks['TITLE_ARMED'] = (walls[0]", "    checks['TITLE_ARMED'] = True or (walls[0]")
mutant('TITLE_ARMED_cap_unchecked', "walls[1] is not None and walls[1] <= TITLE_WALL_MAX_NS", "walls[1] is not None")
mutant('TITLE_ARMED_cap_strict', "walls[1] <= TITLE_WALL_MAX_NS", "walls[1] < TITLE_WALL_MAX_NS")
mutant('TITLE_ARMED_cap_on_arm0', "walls[1] <= TITLE_WALL_MAX_NS", "walls[0] <= TITLE_WALL_MAX_NS")
mutant('TITLE_ARMED_below_unchecked', "and walls[1] < walls[0])", "and True)")
mutant('TITLE_ARMED_below_le', "and walls[1] < walls[0])", "and walls[1] <= walls[0])")
mutant('TITLE_ARMED_below_ne', "and walls[1] < walls[0])", "and walls[1] != walls[0])")
mutant('TITLE_ARMED_none_passes',
       "checks['TITLE_ARMED'] = (walls[0] is not None and walls[1] is not None and walls[1]",
       "checks['TITLE_ARMED'] = walls[0] is None or walls[1] is None or (walls[1]")
mutant('TITLE_ARMED_all_rows', "    walls = [title_wall_ns(lev[a]) for a in (0, 1)]",
       "    walls = [sum(r.get('pres_title_ns', 0) for r in rows.values() if r.get('arm') == a) / max(1, sum("
       "r.get('pres_title_n', 0) for r in rows.values() if r.get('arm') == a)) for a in (0, 1)]")
mutant('TITLE_walls_swapped', "    walls = [title_wall_ns(lev[a]) for a in (0, 1)]",
       "    walls = [title_wall_ns(lev[a]) for a in (1, 0)]")
mutant('TITLE_WALL_MAX_59999', NL + 'TITLE_WALL_MAX_NS = 60000', NL + 'TITLE_WALL_MAX_NS = 59999')
mutant('TITLE_WALL_MAX_60001', NL + 'TITLE_WALL_MAX_NS = 60000', NL + 'TITLE_WALL_MAX_NS = 60001')
mutant('TITLE_WALL_MAX_in_us', NL + 'TITLE_WALL_MAX_NS = 60000', NL + 'TITLE_WALL_MAX_NS = 60')
mutant('TITLE_WALL_MAX_20000', NL + 'TITLE_WALL_MAX_NS = 60000', NL + 'TITLE_WALL_MAX_NS = 20000')   # ttl114's cap
mutant('TITLE_WALL_raw_ns', "    return ns / calls", "    return ns")
mutant('TITLE_WALL_zero_calls', "    if ns is None or calls is None or calls <= 0:", "    if ns is None or calls is None:")
mutant('TITLE_WALL_ns_unchecked', "    if ns is None or calls is None or calls <= 0:", "    if calls is None or calls <= 0:")
WN = "    ns, calls = level.get('pres_title_ns'), level.get('pres_title_n')"
mutant('TITLE_WALL_reads_mt', WN, "    ns, calls = level.get('mt_age_ns'), level.get('mt_n')")
mutant('TITLE_WALL_reads_hold', WN, "    ns, calls = level.get('flip_hold_ns'), level.get('flip_hold_n')")
mutant('TITLE_WALL_reads_rsv', WN, "    ns, calls = level.get('flip_rsv_wait_ns'), level.get('flip_rsv_wait_n')")
# ---- arming: DEFAULTS_ON (cspfree, re-anchored on the session-113 expression; its daslot parts) ------------------------
DF = "bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1 and free_bad == 0" + NL
mutant('DEFAULTS_off', "checks['DEFAULTS_ON'] = bool(", "checks['DEFAULTS_ON'] = True or bool(")
mutant('DEFAULTS_arm0_unchecked', DF, "bool((hits[1] or 0) >= 1 and free_bad == 0" + NL)
mutant('DEFAULTS_arm1_unchecked', DF, "bool((hits[0] or 0) >= 1 and free_bad == 0" + NL)
mutant('DEFAULTS_bad_unchecked', DF, "bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1" + NL)
mutant('DEFAULTS_gt1', DF, "bool((hits[0] or 0) > 1 and (hits[1] or 0) > 1 and free_bad == 0" + NL)
mutant('DEFAULTS_gt0', DF, "bool((hits[0] or 0) > 0 and (hits[1] or 0) > 0 and free_bad == 0" + NL)
mutant('DEFAULTS_reads_look', "hits = [lev[a].get('cspfree_hit') for a in (0, 1)]",
       "hits = [lev[a].get('cspfree_look') for a in (0, 1)]")
mutant('DEFAULTS_bad_kept_only', "free_bad = sum(r.get('cspfree_bad', 0) for r in rows.values())",
       "free_bad = sum(rows[n].get('cspfree_bad', 0) for n in sel['rows'])")
QF = "and (qfree[0] or 0) >= 1 and (qfree[1] or 0) >= 1 and slot_bad == 0)"
mutant('DEFAULTS_qfree0_unchecked', QF, "and (qfree[1] or 0) >= 1 and slot_bad == 0)")
mutant('DEFAULTS_qfree1_unchecked', QF, "and (qfree[0] or 0) >= 1 and slot_bad == 0)")
mutant('DEFAULTS_slot_bad_unchecked', QF, "and (qfree[0] or 0) >= 1 and (qfree[1] or 0) >= 1)")
mutant('DEFAULTS_qfree_gt1', QF, "and (qfree[0] or 0) > 1 and (qfree[1] or 0) > 1 and slot_bad == 0)")
mutant('DEFAULTS_qfree_gt0', QF, "and (qfree[0] or 0) > 0 and (qfree[1] or 0) > 0 and slot_bad == 0)")
QL = "qfree = [lev[a].get('da_q_free') for a in (0, 1)]"
mutant('DEFAULTS_qfree_reads_qcall', QL, "qfree = [lev[a].get('da_qcall') for a in (0, 1)]")
mutant('DEFAULTS_qfree_all_rows', QL,
       "qfree = [sum(r.get('da_q_free', 0) for r in rows.values() if r.get('arm') == a) for a in (0, 1)]")
SB = "slot_bad = sum(r.get('da_slot_bad', 0) for r in rows.values())"
mutant('DEFAULTS_slot_bad_kept_only', SB, "slot_bad = sum(rows[n].get('da_slot_bad', 0) for n in sel['rows'])")
mutant('DEFAULTS_slot_bad_reads_chk', SB, "slot_bad = sum(r.get('da_chk_bad', 0) for r in rows.values())")
# ---- the 94362eae schema: each daslot / daguard / bdanarrow counter out of it, three moved to another line, bda_scan --
for key in ('da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'da_slot_bad', 'da_q_free',
            'da_chk_ok', 'da_chk_bad', 'da_q_noguard', 'da_guard_yield', 'bda_ginv_reg', 'bda_ginv_map', 'bda_rinv',
            'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict', 'bda_nrace', 'prio_unsub', 'prio_stall',
            'gw_idle_prio', 'pres_title_ns', 'pres_title_n', 'flip_rsv_wait_ns', 'flip_rsv_wait_n', 'flip_hold_ns',
            'flip_hold_n', 'mt_age_ns', 'mt_n'):
    mutant('SCHEMA_no_%s' % key, "'%s': 'x'," % key, "")
mutant('SCHEMA_q_free_on_draw', "'da_q_free': 'x',", "'da_q_free': 'draw',")
mutant('SCHEMA_noguard_on_draw', "'da_q_noguard': 'x',", "'da_q_noguard': 'draw',")
mutant('SCHEMA_nskip_on_draw', "'bda_nskip': 'x',", "'bda_nskip': 'draw',")
mutant('SCHEMA_no_bda_scan', "    'bda_scan': 'draw'," + NL, "")
mutant('SCHEMA_scan_on_x', "'bda_scan': 'draw',", "'bda_scan': 'x',")
mutant('SCHEMA_title_ns_on_draw', "'pres_title_ns': 'x',", "'pres_title_ns': 'draw',")
mutant('SCHEMA_title_n_on_main', "'pres_title_n': 'x',", "'pres_title_n': 'main',")
# ---- the sealed constants ---------------------------------------------------------------------------------------------
mutant('CONST_root_s113', "PRODUCTION_ROOT = 'C:/kyty/s114'", "PRODUCTION_ROOT = 'C:/kyty/s113'")
mutant('CONST_pred_shn113', "PRED = 'C:/kyty/s114/pred/02b_ttl114b.md'", "PRED = 'C:/kyty/s113/pred/02_shn113.md'")
mutant('CONST_pred_ctl114', "PRED = 'C:/kyty/s114/pred/02b_ttl114b.md'", "PRED = 'C:/kyty/s114/pred/01_ctl114.md'")
mutant('CONST_pred_ttl114', "PRED = 'C:/kyty/s114/pred/02b_ttl114b.md'", "PRED = 'C:/kyty/s114/pred/02_ttl114.md'")
# a half-filled seal (CONSTANTS: both None, or a sha256 and a size)
mutant('CONST_pred_sha_prefilled', "PRED_SHA = None          #", "PRED_SHA = '0' * 64     #")
mutant('CONST_pred_bytes_prefilled', "PRED_BYTES = None        #", "PRED_BYTES = 1           #")
mutant('CONST_binary_1678d3f4', "BINARY_SHA = '916f64898a5a31c697ad0d823f0795850acc160cf56271b566e8ae330c7c3b2c'",
       "BINARY_SHA = '1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373'")
mutant('CONST_gates_s113', "GATES_FILE = 'C:/kyty/s114/gates_base.txt'", "GATES_FILE = 'C:/kyty/s113/gates_base.txt'")
ARMS_NOW = "ARMS = ('dawalk=1 dawalklead=1 titleasync=0', 'dawalk=1 dawalklead=1 titleasync=1')"
mutant('CONST_arms_swapped', ARMS_NOW, "ARMS = ('dawalk=1 dawalklead=1 titleasync=1', 'dawalk=1 dawalklead=1 titleasync=0')")
mutant('CONST_arms_shn113', ARMS_NOW,
       "ARMS = ('dawalk=1 dawalklead=1 bdanarrow=0', 'dawalk=1 dawalklead=1 bdanarrow=1')")
mutant('CONST_arms_mode2', ARMS_NOW, "ARMS = ('dawalk=1 dawalklead=1 titleasync=0', 'dawalk=1 dawalklead=1 titleasync=2')")
mutant('CONST_schedule_no_start', "SCHEDULE = '90+1800:%s|%s' % ARMS", "SCHEDULE = '90:%s|%s' % ARMS")
# ---- tags and refusal / verdict texts ---------------------------------------------------------------------------------
TAG_NOW = "TAG_RE = r'ttl114b?(?:_entry1)?'"
mutant('TAG_accepts_shn113', TAG_NOW, "TAG_RE = r'(?:ttl114|shn113)b?(?:_entry1)?'")
mutant('TAG_accepts_vtt114', TAG_NOW, "TAG_RE = r'(?:ttl114|vtt114)b?(?:_entry1)?'")
mutant('TAG_accepts_ctl114', TAG_NOW, "TAG_RE = r'(?:ttl114|ctl114)[ab]?(?:_entry1)?'")
mutant('TAG_no_b', TAG_NOW, "TAG_RE = r'ttl114(?:_entry1)?'")
mutant('TAG_no_entry1', TAG_NOW, "TAG_RE = r'ttl114b?'")
mutant('TAG_search', "        if not re.fullmatch(TAG_RE, o.tag):", "        if not re.search(TAG_RE, o.tag):")
mutant('TAG_msg_old', "(ttl114, ttl114b, optional _entry1)", "(shn113, shn113b, optional _entry1)")
mutant('GEOM_msg_old', "'--period/--start/--first/--keep/--secondary are --draft only'",
       "'--period/--start/--first/--keep are --draft only'")
mutant('SEAL_msg_old', "size into ttl114.py (only --draft", "size into shn113.py (only --draft")
mutant('PENDING_text_old', "nothing ships until vtt114 is read", "nothing ships until vsn113 is read")
mutant('PENDING_name_old', "'SHIP_PENDING_VIDEO (", "'REVERT_PENDING_VIDEO (")
mutant('PENDING_knob_dropped', "(titleasync=1: S1-S2 met;", "(S1-S2 met;")
mutant('VERDICT_na_old', "'KEEP titleasync=0 (run not admitted)'", "'KEEP bdanarrow=0 (run not admitted)'")
mutant('VERDICT_bar_old', "'KEEP titleasync=0 (ship rule S1-S2 on mean dt not met)'",
       "'KEEP bdanarrow=0 (ship rule S1-S2 on mean dt not met)'")
mutant('VERDICT_ship_old', "'SHIP titleasync=1 as the new default", "'SHIP bdanarrow=1 as the new default")
mutant('VERDICT_ship_ctl_dropped', "its video pass is owed; ctl114 must read PASS)'", "its video pass is owed)'")
mutant('VERDICT_video_old', "'KEEP titleasync=0 (video pass failed)'", "'KEEP bdanarrow=0 (video pass failed)'")
mutant('SCORER_name_old', "out = {'scorer': 'ttl114.py',", "out = {'scorer': 'shn113.py',")
mutant('SUMMARY_name_old', "lines = ['ttl114.py %s status=%s seal=%s'", "lines = ['shn113.py %s status=%s seal=%s'")
# ---- the ship bar's edge -----------------------------------------------------------------------------------------------
mutant('S1_strict', "dt['mean'] <= SHIP_US,", "dt['mean'] < SHIP_US,")
# ---- predictions P1-P7 --------------------------------------------------------------------------------------------------
P1 = "us[0], 20, 5000)"
P2 = "us[1], None, 60)"
P3 = "stats['dt_us']['mean'], -500, 100)"
P4 = "stats['dt_us']['mean'], None, 0)"
P5 = "stats['gpu_busy_us']['mean'], -150, 150)"
P6 = "stats['flip_rsv_wait_ns']['mean'], None, 0)"
P7 = "stats['da_miss']['mean'], -40, 40)"
mutant('PRED_P1_named_N1', "add('P1',", "add('N1',")
mutant('PRED_P1_arm1', P1, "us[1], 20, 5000)")
mutant('PRED_P1_lo_19', P1, "us[0], 19, 5000)")
mutant('PRED_P1_lo_21', P1, "us[0], 21, 5000)")
mutant('PRED_P1_hi_4999', P1, "us[0], 20, 4999)")
mutant('PRED_P1_hi_5001', P1, "us[0], 20, 5001)")
mutant('PRED_P1_unbounded_hi', P1, "us[0], 20, None)")
mutant('PRED_P2_arm0', P2, "us[0], None, 60)")
mutant('PRED_P2_hi_59', P2, "us[1], None, 59)")
mutant('PRED_P2_hi_61', P2, "us[1], None, 61)")
mutant('PRED_P2_bounded', P2, "us[1], 1, 60)")
mutant('PRED_P2_hi_20', P2, "us[1], None, 20)")      # ttl114's band
mutant('PRED_wall_in_ns', "w / 1000.0 for w in", "w for w in")
mutant('PRED_wall_raw_level', "(title_wall_ns(lev[0]), title_wall_ns(lev[1]))",
       "(lev[0].get('pres_title_ns'), lev[1].get('pres_title_ns'))")
mutant('PRED_wall_arms_swapped', "(title_wall_ns(lev[0]), title_wall_ns(lev[1]))",
       "(title_wall_ns(lev[1]), title_wall_ns(lev[0]))")
mutant('PRED_P3_lo_-501', P3, "stats['dt_us']['mean'], -501, 100)")
mutant('PRED_P3_lo_-499', P3, "stats['dt_us']['mean'], -499, 100)")
mutant('PRED_P3_hi_99', P3, "stats['dt_us']['mean'], -500, 99)")
mutant('PRED_P3_hi_101', P3, "stats['dt_us']['mean'], -500, 101)")
mutant('PRED_P3_hi_200', P3, "stats['dt_us']['mean'], -500, 200)")      # session 113's upper edge
mutant('PRED_P4_hi_-1', P4, "stats['dt_us']['mean'], None, -1)")
mutant('PRED_P4_hi_1', P4, "stats['dt_us']['mean'], None, 1)")
mutant('PRED_P4_hi_-100', P4, "stats['dt_us']['mean'], None, -100)")    # session 113's bar
mutant('PRED_P4_bounded', P4, "stats['dt_us']['mean'], -500, 0)")
mutant('PRED_P4_sign', P4, "-stats['dt_us']['mean'], None, 0)")
mutant('PRED_P5_reads_draws', P5, "stats['draws']['mean'], -150, 150)")
mutant('PRED_P5_lo_-151', P5, "stats['gpu_busy_us']['mean'], -151, 150)")
mutant('PRED_P5_lo_-149', P5, "stats['gpu_busy_us']['mean'], -149, 150)")
mutant('PRED_P5_hi_149', P5, "stats['gpu_busy_us']['mean'], -150, 149)")
mutant('PRED_P5_hi_151', P5, "stats['gpu_busy_us']['mean'], -150, 151)")
mutant('PRED_P6_level_arm1', P6, "lev[1].get('flip_rsv_wait_ns'), None, 0)")
mutant('PRED_P6_hi_-1', P6, "stats['flip_rsv_wait_ns']['mean'], None, -1)")
mutant('PRED_P6_hi_1', P6, "stats['flip_rsv_wait_ns']['mean'], None, 1)")
mutant('PRED_P6_bounded', P6, "stats['flip_rsv_wait_ns']['mean'], -1000, 0)")
mutant('PRED_P6_sign', P6, "-stats['flip_rsv_wait_ns']['mean'], None, 0)")
mutant('PRED_P6_in_us', P6, "stats['flip_rsv_wait_ns']['mean'] / 1000.0, None, 0)")
mutant('PRED_P6_text_unit', "<= 0 raw ns a flip (the per-row counter", "<= 0 us a flip (the per-row counter")
mutant('PRED_P7_reads_late', P7, "stats['da_late']['mean'], -40, 40)")
mutant('PRED_P7_lo_-41', P7, "stats['da_miss']['mean'], -41, 40)")
mutant('PRED_P7_lo_-39', P7, "stats['da_miss']['mean'], -39, 40)")
mutant('PRED_P7_hi_39', P7, "stats['da_miss']['mean'], -40, 39)")
mutant('PRED_P7_hi_41', P7, "stats['da_miss']['mean'], -40, 41)")
mutant('PRED_hit_open_lower', "return v is not None and (lo is None or v >= lo)", "return v is not None and (lo is None or v > lo)")
mutant('PRED_hit_open_upper', "and (hi is None or v <= hi)", "and (hi is None or v < hi)")

# ==== session 113 =====================================================================================================
# ---- the quoted size (report only) and the added claim ------------------------------------------------------------------
mutant('SIZE_sign', "    return {'mean': dt['mean'], 'two_se'",
       "    return {'mean': -dt['mean'] if dt['mean'] is not None else None, 'two_se'")
mutant('SIZE_1se', "'two_se': 2 * dt['se'] if dt['se'] is not None else None",
       "'two_se': 1 * dt['se'] if dt['se'] is not None else None")
mutant('SIZE_secondary', "    out['reported']['quoted_size'] = quoted_size(dt)",
       "    out['reported']['quoted_size'] = quoted_size(out['secondary']['pair_stats']['dt_us'])")
mutant('SIZE_summary_dropped', "    if size:" + NL, "    if False:" + NL)
mutant('SIZE_label', "SIZE_LABEL = 'titleasync=1 against titleasync=0 of build 916f6489, main estimator'",
       "SIZE_LABEL = 'titleasync=1 against titleasync=0, main estimator'")
mutant('CLAIM_stall_dropped', "'d cpu_net_us alone; that the 3-s stall of session 113 was the title wait (the '",
       "'d cpu_net_us alone; (the '")
mutant('CLAIM_additivity_dropped', "'control proves the knob, not the event); additivity')",
       "'control proves the knob, not the event)')")
mutant('CLAIM_60fps_dropped', "('60 FPS; a game-speed", "('a game-speed")
# ---- the session-111 audit's shp111 mutants (audit111/newmut.py) --------------------------------------------------------
mutant('S2_strict', "and dt['mean'] + 2 * dt['se'] <= S2_US)", "and dt['mean'] + 2 * dt['se'] < S2_US)")
mutant('FATAL_no_unhandled', "b'Unhandled exception:', ", "")
mutant('FATAL_no_devicelost', "b'ErrorDeviceLost', ", "")
mutant('FATAL_no_terminate', "b'--- std::terminate ---', ", "")
mutant('BANDS_gpu_wide', "'gpu_busy_us': (10000.0, 16000.0)}", "'gpu_busy_us': (1000.0, 160000.0)}")
mutant('HOLD_tol_50', "if (a.get('hold_s') or 0) < HOLD_S - 5:", "if (a.get('hold_s') or 0) < HOLD_S - 50:")
mutant('AREA_min_flips_0', "AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 8",
       "AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 0")
mutant('ID_TOL_10x', "ID_TOL = 0.01", "ID_TOL = 0.1")
mutant('VIDEO_frames_strict', "'frames': frames is not None and frames >= VIDEO_MIN_FRAMES,",
       "'frames': frames is not None and frames > VIDEO_MIN_FRAMES,")
mutant('DROPS_loose', "checks['WALK_DROPS_ARM%d' % a] = bool(po) and dr is not None and dr / po <= DROP_MAX",
       "checks['WALK_DROPS_ARM%d' % a] = bool(po) and dr is not None and dr / po <= 1.0")
# (SLOT_DARK_tol5 went with the SLOT_* terms in session 113; SCHEMA_no_q_taking = SCHEMA_no_da_q_taking, not
# repeated)
# ---- the other side of each threshold-edge fixture ----------------------------------------------------------------------
mutant('HOLD_tol_4', "if (a.get('hold_s') or 0) < HOLD_S - 5:", "if (a.get('hold_s') or 0) < HOLD_S - 4:")
mutant('HOLD_le', "if (a.get('hold_s') or 0) < HOLD_S - 5:", "if (a.get('hold_s') or 0) <= HOLD_S - 5:")
mutant('AREA_min_flips_9', "AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 8",
       "AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 9")
mutant('AREA_min_flips_le', "if a0['n'] < min_flips or a1['n'] < min_flips:",
       "if a0['n'] <= min_flips or a1['n'] <= min_flips:")
mutant('ID_TOL_half', "ID_TOL = 0.01", "ID_TOL = 0.005")
mutant('VIDEO_frames_3001', 'VIDEO_MIN_FRAMES = 3000', 'VIDEO_MIN_FRAMES = 3001')

# ==== session 114 =====================================================================================================
# ---- the title / hold / main-task lines are not markers -------------------------------------------------------------
mutant('FATAL_mainthreadwait', "b'AsyncPipelines: skipped draw')",
       "b'AsyncPipelines: skipped draw', b'MainThreadWait:')")
mutant('FATAL_maintasklate', "b'AsyncPipelines: skipped draw')", "b'AsyncPipelines: skipped draw', b'MainTaskLate:')")
mutant('FATAL_fliphold', "b'AsyncPipelines: skipped draw')", "b'AsyncPipelines: skipped draw', b'FlipHold:')")
# ---- d flip_rsv_wait_ns (P6) in the pair keys and the report; the title levels in the report and the summary --------
mutant('PAIR_no_rsv', "'da_walks', 'da_qcall', 'flip_rsv_wait_ns')", "'da_walks', 'da_qcall')")
mutant('REPORTED_rsv_d_dropped', "'gpu_busy_us', 'draws', 'flip_rsv_wait_ns')}", "'gpu_busy_us', 'draws')}")
mutant('REPORTED_title_levels_dropped', "    for k in ('pres_title_ns', 'pres_title_n', 'flip_rsv_wait_ns',",
       "    for k in ('flip_rsv_wait_ns',")
mutant('SUMMARY_title_line', "'  titleasync: pres_title_n levels %s  per-call wall %s ns",
       "'  titleasync: levels %s  per-call wall %s ns")

MUT.mkdir(parents=True, exist_ok=True)
FX.mkdir(parents=True, exist_ok=True)
for name, (old, new) in M.items():
    n = SRC.count(old)
    if n != 1:
        raise SystemExit('mutant %s: anchor found %d times: %r' % (name, n, old[:80]))
    if old == new:
        raise SystemExit('mutant %s changes nothing' % name)


def run(job):
    k, name = job
    if name == 'BASELINE':
        path = SCORER
    else:
        old, new = M[name]
        path = MUT / ('ttl114b_%s.py' % name)
        path.write_bytes(SRC.replace(old, new).encode('utf-8'))
    t0 = time.time()
    r = subprocess.run([sys.executable, '-B', str(TEST), str(path), str(FX / ('w%d' % k))], capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    txt = r.stdout + r.stderr
    (MUT / ('%s.out' % name)).write_text(txt, encoding='utf-8')
    failed = [ln.split()[0] for ln in txt.splitlines() if '  PROBLEMS ' in ln]
    crashed = 'Traceback (most recent call last)' in txt
    if 'ALL OK' in txt and r.returncode == 0:
        verdict = 'SURVIVED'
    elif crashed:
        verdict = 'KILLED (suite crashed: %s)' % txt.strip().splitlines()[-1][:100]
    else:
        verdict = 'KILLED by %s' % failed
    return name, verdict, time.time() - t0


names = list(M)
results = {}
try:
    base = run((0, 'BASELINE'))
    print('%-28s %s  (%.0f s)' % base, flush=True)
    if base[1] != 'SURVIVED':
        raise SystemExit('the unmutated scorer does not pass its own suite in this harness')
    jobs = [(i % WORKERS, n) for i, n in enumerate(names)]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        # one job per worker directory at a time: split the jobs into WORKERS lanes run sequentially inside each lane
        lanes = [[j for j in jobs if j[0] == w] for w in range(WORKERS)]

        def lane(js):
            out = []
            for j in js:
                res = run(j)
                print('%-28s %s  (%.0f s)' % res, flush=True)
                out.append(res)
            return out
        for res_list in ex.map(lane, lanes):
            for name, verdict, _ in res_list:
                results[name] = verdict
finally:
    shutil.rmtree(FX, ignore_errors=True)       # the per-worker fixture copies
alive = [n for n in names if results[n] == 'SURVIVED']
crashed = [n for n in names if results[n].startswith('KILLED (suite crashed')]
only_const = [n for n in names if results[n] == "KILLED by ['CONSTANTS']"]
print('%d mutants: %d killed (%d by a crash of the suite), %d survived' % (len(names), len(names) - len(alive),
                                                                           len(crashed), len(alive)))
print('killed by CONSTANTS alone: %s' % (only_const or 'none'))
print('ALL KILLED' if not alive else 'SURVIVORS: %s' % alive)
sys.exit(0 if not alive else 1)
