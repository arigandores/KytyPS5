"""Session 111: mutation check of shp111.py against test_shp111.py.  Each mutant disables or weakens ONE admission /
decision term, verdict branch, prediction, schema entry, marker, sealed constant, estimator window or refusal of main()
(anchored replace, asserted to match exactly once).  Included: every mutant of mut_shp110.py (ported; the FREE_* arming
mutants replaced by their SLOT_* / DEFAULTS_ON counterparts, H1-H6 by K1-K6, the texts re-anchored on shp111), the
eight shp110 mutants of the session-110 audit (audit110/newmut.py), and the session-111 changes: the MAIN estimator's
window bounds (9 / 10 / 89 / 90 / full block / the old window as main), the secondary window's bounds, the secondary
swapped into the decision and into the predictions, the secondary computed on the main window, the draft-only
--secondary, SLOT_*, DEFAULTS_ON, the eight new schema counters, K1-K6 and the sealed constants.  Each mutant runs the
full fixture suite in its own fixture directory (C:/kyty/s106_stage/shp111/fx_mut/w<k>, removed at the end); a mutant
is KILLED when the suite does not print ALL OK.  The unmutated scorer runs first in the same harness and must print
ALL OK.
    python mut_shp111.py [<workers>]
"""
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path('C:/kyty/s106_stage/shp111')
SCORER = HERE / 'shp111.py'
TEST = HERE / 'test_shp111.py'
MUT = HERE / 'mutants'
FX = HERE / 'fx_mut'
WORKERS = int(sys.argv[1]) if len(sys.argv) > 1 else 16
SRC = SCORER.read_bytes().decode('utf-8')
NL = chr(10)

M = {}


def mutant(name, old, new):
    assert name not in M, name
    M[name] = (old, new)


# ==== ported from mut_shp110.py =======================================================================================
# ---- decision terms and verdict branches ----------------------------------------------------------------------------
mutant('S1_off', "'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,", "'S1_dt_le_-100': True,")
mutant('S1_bar_-50', "dt['mean'] <= SHIP_US,", "dt['mean'] <= SHIP_US + 50,")
mutant('S2_off', "'S2_dt_2se_excludes_0': (dt['mean'] is not None and dt['se'] is not None" + NL
       + "                                 and dt['mean'] + 2 * dt['se'] < 0),", "'S2_dt_2se_excludes_0': True,")
mutant('S2_1se', "and dt['mean'] + 2 * dt['se'] < 0)", "and dt['mean'] + 1 * dt['se'] < 0)")
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
mutant('VIDEO_gate_daslot_off', "' dawalk=1 ' in gates and ' daslot=1 ' in gates,", "' dawalk=1 ' in gates,")
mutant('VIDEO_gate_dawalk_off', "' dawalk=1 ' in gates and ' daslot=1 ' in gates,", "' daslot=1 ' in gates,")
mutant('VIDEO_gate_is_cspfree', "' dawalk=1 ' in gates and ' daslot=1 ' in gates,",
       "' dawalk=1 ' in gates and ' cspfree=1 ' in gates,")
mutant('VIDEO_pin_off', "'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1',", "'pinned': True,")
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
mutant('SHIP_bar_-99', 'SHIP_US = -100.0', 'SHIP_US = -99.0')
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
# ---- arming: SLOT_* ----------------------------------------------------------------------------------------------------
mutant('SLOT_DARK_off', "checks['SLOT_DARK_ARM0'] = free0 == 0", "checks['SLOT_DARK_ARM0'] = True")
mutant('SLOT_DARK_all_arm0_rows', "free0 = kept_total(rows, sel, arms, 0, 'da_q_free')",
       "free0 = sum(r.get('da_q_free', 0) for r in rows.values() if r.get('arm') == 0)")
mutant('SLOT_DARK_reads_arm1', "free0 = kept_total(rows, sel, arms, 0, 'da_q_free')",
       "free0 = kept_total(rows, sel, arms, 1, 'da_q_free')")
mutant('SLOT_ARMED_off', "checks['SLOT_ARMED_ARM1'] = bool((lev[1].get('da_q_free') or 0) >= 1)",
       "checks['SLOT_ARMED_ARM1'] = True")
mutant('SLOT_ARMED_reads_qcall', "checks['SLOT_ARMED_ARM1'] = bool((lev[1].get('da_q_free') or 0) >= 1)",
       "checks['SLOT_ARMED_ARM1'] = bool((lev[1].get('da_qcall') or 0) >= 1)")
mutant('SLOT_ARMED_gt1', "checks['SLOT_ARMED_ARM1'] = bool((lev[1].get('da_q_free') or 0) >= 1)",
       "checks['SLOT_ARMED_ARM1'] = bool((lev[1].get('da_q_free') or 0) > 1)")
mutant('SLOT_ARMED_arm0', "checks['SLOT_ARMED_ARM1'] = bool((lev[1].get('da_q_free') or 0) >= 1)",
       "checks['SLOT_ARMED_ARM1'] = bool((lev[0].get('da_q_free') or 0) >= 1)")
mutant('SLOT_NO_BAD_off', "checks['SLOT_NO_BAD'] = bad == 0", "checks['SLOT_NO_BAD'] = True")
mutant('SLOT_NO_BAD_kept_only', "bad = sum(r.get('da_slot_bad', 0) for r in rows.values())",
       "bad = sum(rows[n].get('da_slot_bad', 0) for n in sel['rows'])")
mutant('SLOT_NO_BAD_reads_chk', "bad = sum(r.get('da_slot_bad', 0) for r in rows.values())",
       "bad = sum(r.get('da_chk_bad', 0) for r in rows.values())")
# ---- arming: DEFAULTS_ON -------------------------------------------------------------------------------------------------
mutant('DEFAULTS_off', "checks['DEFAULTS_ON'] = bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1 and free_bad == 0)",
       "checks['DEFAULTS_ON'] = True")
mutant('DEFAULTS_arm0_unchecked', "bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1 and free_bad == 0)",
       "bool((hits[1] or 0) >= 1 and free_bad == 0)")
mutant('DEFAULTS_arm1_unchecked', "bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1 and free_bad == 0)",
       "bool((hits[0] or 0) >= 1 and free_bad == 0)")
mutant('DEFAULTS_bad_unchecked', "bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1 and free_bad == 0)",
       "bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1)")
mutant('DEFAULTS_gt1', "bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1 and free_bad == 0)",
       "bool((hits[0] or 0) > 1 and (hits[1] or 0) > 1 and free_bad == 0)")
mutant('DEFAULTS_reads_look', "hits = [lev[a].get('cspfree_hit') for a in (0, 1)]",
       "hits = [lev[a].get('cspfree_look') for a in (0, 1)]")
mutant('DEFAULTS_bad_kept_only', "free_bad = sum(r.get('cspfree_bad', 0) for r in rows.values())",
       "free_bad = sum(rows[n].get('cspfree_bad', 0) for n in sel['rows'])")
# ---- the c8235c90 schema: each new counter out of it, one moved to another line -------------------------------------------
for key in ('da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'da_slot_bad', 'da_q_free',
            'da_chk_ok', 'da_chk_bad'):
    mutant('SCHEMA_no_%s' % key, "'%s': 'x'," % key, "")
mutant('SCHEMA_q_free_on_draw', "'da_q_free': 'x',", "'da_q_free': 'draw',")
# ---- the sealed constants ---------------------------------------------------------------------------------------------
mutant('CONST_root_s110', "PRODUCTION_ROOT = 'C:/kyty/s111'", "PRODUCTION_ROOT = 'C:/kyty/s110'")
mutant('CONST_pred_shp110', "PRED = 'C:/kyty/s111/pred/03_shp111.md'", "PRED = 'C:/kyty/s110/pred/03_shp110.md'")
mutant('CONST_pred_sha_prefilled', "PRED_SHA = None          #", "PRED_SHA = '0' * 64     #")
mutant('CONST_binary_b3f7a2c9', "BINARY_SHA = 'c8235c902e08d00782d0cff23528361d194a501ad1899344ca8302c742372a86'",
       "BINARY_SHA = 'b3f7a2c957dd344bfd140fe6d04eb2b95ac9387d01dabf5b7dde42b6765b6a82'")
mutant('CONST_gates_s110', "GATES_FILE = 'C:/kyty/s111/gates_base.txt'", "GATES_FILE = 'C:/kyty/s110/gates_base.txt'")
mutant('CONST_arms_swapped', "ARMS = ('dawalk=1 dawalklead=1 daslot=0', 'dawalk=1 dawalklead=1 daslot=1')",
       "ARMS = ('dawalk=1 dawalklead=1 daslot=1', 'dawalk=1 dawalklead=1 daslot=0')")
mutant('CONST_arms_cspfree', "ARMS = ('dawalk=1 dawalklead=1 daslot=0', 'dawalk=1 dawalklead=1 daslot=1')",
       "ARMS = ('dawalk=1 dawalklead=1 cspfree=0', 'dawalk=1 dawalklead=1 cspfree=1')")
mutant('CONST_schedule_no_start', "SCHEDULE = '90+1800:%s|%s' % ARMS", "SCHEDULE = '90:%s|%s' % ARMS")
# ---- tags and refusal / verdict texts ---------------------------------------------------------------------------------
mutant('TAG_accepts_shp110', "TAG_RE = r'shp111b?(?:_entry1)?'", "TAG_RE = r'(?:shp111|shp110)b?(?:_entry1)?'")
mutant('TAG_accepts_vss111', "TAG_RE = r'shp111b?(?:_entry1)?'", "TAG_RE = r'(?:shp111|vss111)b?(?:_entry1)?'")
mutant('TAG_no_b', "TAG_RE = r'shp111b?(?:_entry1)?'", "TAG_RE = r'shp111(?:_entry1)?'")
mutant('TAG_no_entry1', "TAG_RE = r'shp111b?(?:_entry1)?'", "TAG_RE = r'shp111b?'")
mutant('TAG_search', "        if not re.fullmatch(TAG_RE, o.tag):", "        if not re.search(TAG_RE, o.tag):")
mutant('TAG_msg_old', "(shp111, shp111b, optional _entry1)", "(shp110, shp110b, optional _entry1)")
mutant('GEOM_msg_old', "'--period/--start/--first/--keep/--secondary are --draft only'",
       "'--period/--start/--first/--keep are --draft only'")
mutant('SEAL_msg_old', "size into shp111.py (only --draft", "size into shp110.py (only --draft")
mutant('PENDING_text_old', "nothing ships until vss111 is read", "nothing ships until vsh110 is read")
mutant('VERDICT_na_old', "'KEEP daslot=0 (run not admitted)'", "'KEEP cspfree=0 (run not admitted)'")
mutant('VERDICT_bar_old', "'KEEP daslot=0 (ship rule S1-S2 on mean dt not met)'",
       "'KEEP cspfree=0 (ship rule S1-S2 on mean dt not met)'")
mutant('VERDICT_ship_old', "'SHIP daslot=1 as the new default", "'SHIP cspfree=1 as the new default")
mutant('VERDICT_video_old', "'KEEP daslot=0 (video pass failed)'", "'KEEP cspfree=0 (video pass failed)'")
mutant('SCORER_name_old', "out = {'scorer': 'shp111.py',", "out = {'scorer': 'shp110.py',")
mutant('SUMMARY_name_old', "lines = ['shp111.py %s status=%s seal=%s'", "lines = ['shp110.py %s status=%s seal=%s'")
# ---- the ship bar's edge -----------------------------------------------------------------------------------------------
mutant('S1_strict', "dt['mean'] <= SHIP_US,", "dt['mean'] < SHIP_US,")
# ---- predictions K1-K6 --------------------------------------------------------------------------------------------------
mutant('PRED_K1_named_H1', "add('K1',", "add('H1',")
mutant('PRED_K1_reads_qcall', "lev[1].get('da_q_free'), 800, 1400)", "lev[1].get('da_qcall'), 800, 1400)")
mutant('PRED_K1_band_700', "lev[1].get('da_q_free'), 800, 1400)", "lev[1].get('da_q_free'), 700, 1400)")
mutant('PRED_K1_upper_1300', "lev[1].get('da_q_free'), 800, 1400)", "lev[1].get('da_q_free'), 800, 1300)")
mutant('PRED_K2_arm1', "lev[0].get('da_q_free'), 0, 0)", "lev[1].get('da_q_free'), 0, 0)")
mutant('PRED_K2_upper_10', "lev[0].get('da_q_free'), 0, 0)", "lev[0].get('da_q_free'), 0, 10)")
mutant('PRED_K3_band_-600', "stats['dt_us']['mean'], -400, 0)", "stats['dt_us']['mean'], -600, 0)")
mutant('PRED_K3_upper_-50', "stats['dt_us']['mean'], -400, 0)", "stats['dt_us']['mean'], -400, -50)")
mutant('PRED_K4_bar_-50', "stats['dt_us']['mean'], None, SHIP_US)", "stats['dt_us']['mean'], None, -50.0)")
mutant('PRED_K5_reads_late', "stats['da_miss']['mean'], -40, 40)", "stats['da_late']['mean'], -40, 40)")
mutant('PRED_K5_band_60', "stats['da_miss']['mean'], -40, 40)", "stats['da_miss']['mean'], -60, 60)")
mutant('PRED_K6_bar_10', "lev[1].get('da_guard_busy'), None, 5)", "lev[1].get('da_guard_busy'), None, 10)")
mutant('PRED_K6_reads_taking', "lev[1].get('da_guard_busy'), None, 5)", "lev[1].get('da_q_taking'), None, 5)")
mutant('PRED_K6_arm0', "lev[1].get('da_guard_busy'), None, 5)", "lev[0].get('da_guard_busy'), None, 5)")
mutant('PRED_hit_open_lower', "return v is not None and (lo is None or v >= lo)", "return v is not None and (lo is None or v > lo)")
mutant('PRED_hit_open_upper', "and (hi is None or v <= hi)", "and (hi is None or v < hi)")

MUT.mkdir(exist_ok=True)
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
        path = MUT / ('shp111_%s.py' % name)
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
