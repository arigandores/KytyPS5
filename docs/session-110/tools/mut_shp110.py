"""Session 110: mutation check of shp110.py against test_shp110.py.  Each mutant disables or weakens ONE admission /
decision term, verdict branch, prediction, schema entry, marker, sealed constant or refusal of main() (anchored
replace, asserted to match exactly once).  Included: every mutant of mut_frf109.py (ported; the tag mutant re-anchored
on shp110), the thirteen frm109/frf109 mutants of the session-109 audit (audit109/newmut.py) - among them its four
survivors KEEP_shift1, SE_pstdev, LEVEL_mean, FATAL_no_waitslow - and the session-110 changes (the two new schema
counters, CsStall not a marker, H1-H6, tag / refusal / verdict texts, the sealed constants).  Each mutant runs the full
fixture suite in its own fixture directory (C:/kyty/s106_stage/fx_shp110/mut/w<k>, removed at the end); a mutant is
KILLED when the suite does not print ALL OK.  The unmutated scorer runs first in the same harness and must print
ALL OK.
    python mut_shp110.py [<workers>]
"""
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path('C:/kyty/s106_stage/shp110')
SCORER = HERE / 'shp110.py'
TEST = HERE / 'test_shp110.py'
MUT = HERE / 'mutants'
FX = Path('C:/kyty/s106_stage/fx_shp110/mut')
WORKERS = int(sys.argv[1]) if len(sys.argv) > 1 else 16
SRC = SCORER.read_bytes().decode('utf-8')
NL = chr(10)

M = {}


def mutant(name, old, new):
    assert name not in M, name
    M[name] = (old, new)


# ==== ported from mut_frf109.py =======================================================================================
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
mutant('VIDEO_gate_cspfree_off', "' dawalk=1 ' in gates and ' cspfree=1 ' in gates,", "' dawalk=1 ' in gates,")
mutant('VIDEO_gate_dawalk_off', "' dawalk=1 ' in gates and ' cspfree=1 ' in gates,", "' cspfree=1 ' in gates,")
mutant('VIDEO_gate_is_fam108s', "' dawalk=1 ' in gates and ' cspfree=1 ' in gates,",
       "' dawalk=1 ' in gates and ' cspfam=4 ' in gates,")
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
mutant('KEEP_all', 'KEEP_LO, KEEP_HI = 60, 89', 'KEEP_LO, KEEP_HI = 0, 90')

# ---- arming sub-checks (FREE_* first) -------------------------------------------------------------------------------
mutant('FREE_DARK_off', "checks['FREE_DARK_ARM0'] = look0 == 0 and hit0 == 0", "checks['FREE_DARK_ARM0'] = True")
mutant('FREE_DARK_no_hit', "checks['FREE_DARK_ARM0'] = look0 == 0 and hit0 == 0", "checks['FREE_DARK_ARM0'] = look0 == 0")
mutant('FREE_DARK_no_look', "checks['FREE_DARK_ARM0'] = look0 == 0 and hit0 == 0", "checks['FREE_DARK_ARM0'] = hit0 == 0")
mutant('FREE_ARMED_off', "checks['FREE_ARMED_ARM1'] = bool((lev[1].get('cspfree_hit') or 0) >= 1)",
       "checks['FREE_ARMED_ARM1'] = True")
mutant('FREE_ARMED_look', "checks['FREE_ARMED_ARM1'] = bool((lev[1].get('cspfree_hit') or 0) >= 1)",
       "checks['FREE_ARMED_ARM1'] = bool((lev[1].get('cspfree_look') or 0) >= 1)")
mutant('FREE_NO_BAD_off', "checks['FREE_NO_BAD'] = bad == 0", "checks['FREE_NO_BAD'] = True")
mutant('FREE_NO_BAD_kept_only', "bad = sum(r.get('cspfree_bad', 0) for r in rows.values())",
       "bad = sum(rows[n].get('cspfree_bad', 0) for n in sel['rows'])")
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
mutant('TAG_accepts_fam108', "TAG_RE = r'shp110b?(?:_entry1)?'", "TAG_RE = r'(?:shp110|fam108)b?(?:_entry1)?'")
mutant('GEOM_off', "        if geometry:" + NL + "            print(", "        if False:" + NL + "            print(")
mutant('OUT_exists_off', "        if path.exists():", "        if False:")
mutant('OUT_root_off', "        if not o.draft and not path.as_posix().startswith(PRODUCTION_ROOT + '/'):", "        if False:")

# ---- the reported, never deciding cpu_net (audit-108 survivor 2) ----------------------------------------------------
mutant('CPU_NET_no_spin', "out['cpu_net_us'] = row['cpu_gpu_us'] - row['spin_gpu_us']", "out['cpu_net_us'] = row['cpu_gpu_us']")

# ==== the session-109 audit's frm109/frf109 mutants (audit109/newmut.py; the first four of this block survived) =======
mutant('KEEP_shift1', "kept = expected[lo:hi]", "kept = expected[lo - 1:hi - 1]")
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

# ==== session 110 =====================================================================================================
# ---- the kept window, the other direction ----------------------------------------------------------------------------
mutant('KEEP_shift_up1', "kept = expected[lo:hi]", "kept = expected[lo + 1:hi + 1]")
# ---- markers: another one dropped; CsStall made a marker ---------------------------------------------------------------
mutant('FATAL_no_error', "(b'--- Error ---', ", "(")
mutant('FATAL_csstall', "b'AsyncPipelines: skipped draw')", "b'AsyncPipelines: skipped draw', b'CsStall:')")
# ---- the b3f7a2c9 schema ----------------------------------------------------------------------------------------------
mutant('SCHEMA_no_cs_sync_new_us', "    'cs_sync_new_us': 'x', 'cs_sync_wait_us': 'x'," + NL,
       "    'cs_sync_wait_us': 'x'," + NL)
mutant('SCHEMA_no_cs_sync_wait_us', "    'cs_sync_new_us': 'x', 'cs_sync_wait_us': 'x'," + NL,
       "    'cs_sync_new_us': 'x'," + NL)
mutant('SCHEMA_new_us_on_draw', "'cs_sync_new_us': 'x',", "'cs_sync_new_us': 'draw',")
# ---- the sealed constants ---------------------------------------------------------------------------------------------
mutant('CONST_root_s109', "PRODUCTION_ROOT = 'C:/kyty/s110'", "PRODUCTION_ROOT = 'C:/kyty/s109'")
mutant('CONST_pred_frf109', "PRED = 'C:/kyty/s110/pred/03_shp110.md'", "PRED = 'C:/kyty/s109/pred/03_frf109.md'")
mutant('CONST_pred_sha_prefilled', "PRED_SHA = None          #", "PRED_SHA = '0' * 64     #")
mutant('CONST_binary_2f593229', "BINARY_SHA = 'b3f7a2c957dd344bfd140fe6d04eb2b95ac9387d01dabf5b7dde42b6765b6a82'",
       "BINARY_SHA = '2f5932296d564b1098831b75a7fc6c8796d3a9ac7e871ea0c3a1c6b0610a4b77'")
mutant('CONST_gates_s109', "GATES_FILE = 'C:/kyty/s110/gates_base.txt'", "GATES_FILE = 'C:/kyty/s109/gates_base.txt'")
mutant('CONST_arms_swapped', "ARMS = ('dawalk=1 dawalklead=1 cspfree=0', 'dawalk=1 dawalklead=1 cspfree=1')",
       "ARMS = ('dawalk=1 dawalklead=1 cspfree=1', 'dawalk=1 dawalklead=1 cspfree=0')")
mutant('CONST_schedule_no_start', "SCHEDULE = '90+1800:%s|%s' % ARMS", "SCHEDULE = '90:%s|%s' % ARMS")
# ---- tags and refusal / verdict texts ---------------------------------------------------------------------------------
mutant('TAG_accepts_frf109', "TAG_RE = r'shp110b?(?:_entry1)?'", "TAG_RE = r'(?:shp110|frf109)b?(?:_entry1)?'")
mutant('TAG_no_b', "TAG_RE = r'shp110b?(?:_entry1)?'", "TAG_RE = r'shp110(?:_entry1)?'")
mutant('TAG_no_entry1', "TAG_RE = r'shp110b?(?:_entry1)?'", "TAG_RE = r'shp110b?'")
mutant('TAG_search', "        if not re.fullmatch(TAG_RE, o.tag):", "        if not re.search(TAG_RE, o.tag):")
mutant('TAG_msg_old', "(shp110, shp110b, optional _entry1)", "(frf109, frf109b, optional _entry1)")
mutant('SEAL_msg_old', "size into shp110.py (only --draft", "size into frf109.py (only --draft")
mutant('PENDING_text_old', "nothing ships until vsh110 is read", "nothing ships until vff109 is read")
mutant('SCORER_name_old', "out = {'scorer': 'shp110.py',", "out = {'scorer': 'frf109.py',")
mutant('SUMMARY_name_old', "lines = ['shp110.py %s status=%s seal=%s'", "lines = ['frf109.py %s status=%s seal=%s'")
# ---- predictions H1-H6 --------------------------------------------------------------------------------------------------
mutant('PRED_H1_named_G1', "add('H1',", "add('G1',")
mutant('PRED_H1_reads_look', "lev[1].get('cspfree_hit'), 200, 270)", "lev[1].get('cspfree_look'), 200, 270)")
mutant('PRED_H1_band_150', "lev[1].get('cspfree_hit'), 200, 270)", "lev[1].get('cspfree_hit'), 150, 270)")
mutant('PRED_H2_bar_60', "lev[1].get('cspf_have'), None, 30)", "lev[1].get('cspf_have'), None, 60)")
mutant('PRED_H3_band', "stats['dt_us']['mean'], -300, 0)", "stats['dt_us']['mean'], -400, 0)")
mutant('PRED_H4_bar_-50', "stats['dt_us']['mean'], None, SHIP_US)", "stats['dt_us']['mean'], None, -50.0)")
mutant('PRED_H5_reads_late', "stats['da_miss']['mean'], -30, 30)", "stats['da_late']['mean'], -30, 30)")
mutant('PRED_H6_old_band', "stats['gpu_busy_us']['mean'], 0, 150)", "stats['gpu_busy_us']['mean'], -50, 150)")
mutant('PRED_H6_upper_100', "stats['gpu_busy_us']['mean'], 0, 150)", "stats['gpu_busy_us']['mean'], 0, 100)")
mutant('PRED_hit_open_lower', "return v is not None and (lo is None or v >= lo)", "return v is not None and (lo is None or v > lo)")

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
        path = MUT / ('shp110_%s.py' % name)
        path.write_bytes(SRC.replace(old, new).encode('utf-8'))
    t0 = time.time()
    r = subprocess.run([sys.executable, str(TEST), str(path), str(FX / ('w%d' % k))], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
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
try:
    base = run((0, 'BASELINE'))
    print('%-28s %s  (%.0f s)' % base, flush=True)
    if base[1] != 'SURVIVED':
        raise SystemExit('the unmutated scorer does not pass its own suite in this harness')
    jobs = [(i % WORKERS, n) for i, n in enumerate(names)]
    results = {}
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
print('%d mutants: %d killed (%d by a crash of the suite), %d survived' % (len(names), len(names) - len(alive),
                                                                           len(crashed), len(alive)))
print('ALL KILLED' if not alive else 'SURVIVORS: %s' % alive)
sys.exit(0 if not alive else 1)
