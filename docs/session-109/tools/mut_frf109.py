"""Session 109: mutation check of frf109.py against test_frf109.py.  Each mutant disables or weakens ONE admission /
decision term, verdict branch or refusal of main() (anchored replace, asserted to match exactly once), including the
two audit-108 survivors (ABBA_pattern_unchecked, CPU_NET_no_spin) and every FREE_* term.  Each mutant runs the full
fixture suite in its own fixture directory (C:/kyty/s106_stage/fx_frf109/mut/w<k>); a mutant is KILLED when the
suite does not print ALL OK.  The unmutated scorer runs first in the same harness and must print ALL OK.
    python mut_frf109.py [<workers>]
"""
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path('C:/kyty/s106_stage/frf109')
SCORER = HERE / 'frf109.py'
TEST = HERE / 'test_frf109.py'
MUT = HERE / 'mutants'
FX = Path('C:/kyty/s106_stage/fx_frf109/mut')
WORKERS = int(sys.argv[1]) if len(sys.argv) > 1 else 8
SRC = SCORER.read_bytes().decode('utf-8')
NL = chr(10)

M = {}


def mutant(name, old, new):
    assert name not in M, name
    M[name] = (old, new)


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
mutant('TAG_accepts_fam108', "TAG_RE = r'frf109b?(?:_entry1)?'", "TAG_RE = r'(?:frf109|fam108)b?(?:_entry1)?'")
mutant('GEOM_off', "        if geometry:" + NL + "            print(", "        if False:" + NL + "            print(")
mutant('OUT_exists_off', "        if path.exists():", "        if False:")
mutant('OUT_root_off', "        if not o.draft and not path.as_posix().startswith(PRODUCTION_ROOT + '/'):", "        if False:")

# ---- the reported, never deciding cpu_net (audit-108 survivor 2) ----------------------------------------------------
mutant('CPU_NET_no_spin', "out['cpu_net_us'] = row['cpu_gpu_us'] - row['spin_gpu_us']", "out['cpu_net_us'] = row['cpu_gpu_us']")

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
        path = MUT / ('frf109_%s.py' % name)
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
alive = [n for n in names if results[n] == 'SURVIVED']
crashed = [n for n in names if results[n].startswith('KILLED (suite crashed')]
print('%d mutants: %d killed (%d by a crash of the suite), %d survived' % (len(names), len(names) - len(alive),
                                                                           len(crashed), len(alive)))
print('ALL KILLED' if not alive else 'SURVIVORS: %s' % alive)
sys.exit(0 if not alive else 1)
