"""Audit 109: new mutants (not in mut_frf109.py / mut_ent109*.py) run against the session fixture suites.
Mutant scorers are written under C:/kyty/s109/audit109/mut/; the suites write fixtures under C:/kyty/s106_stage/fx_*
(as the session's own harness does).  Sequential (the ent/vfy suites share one fixture dir each)."""
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
R = Path('C:/kyty/s109')
OUT = R / 'audit109' / 'mut'
OUT.mkdir(parents=True, exist_ok=True)
NL = chr(10)

M = [
    # frm109.py / frf109.py
    ('frm109.py', 'test_frf109.py', 'PAIR_step2', "for b in range(0, top + 1, 4):", "for b in range(0, top + 1, 2):"),
    ('frm109.py', 'test_frf109.py', 'PAIR_left_is_arm0', "a0 = left if arms[left] == 0 else right", "a0 = left"),
    ('frm109.py', 'test_frf109.py', 'KEEP_shift1', "kept = expected[lo:hi]", "kept = expected[lo - 1:hi - 1]"),
    ('frm109.py', 'test_frf109.py', 'SE_pstdev', "sd = statistics.stdev(values)", "sd = statistics.pstdev(values)"),
    ('frm109.py', 'test_frf109.py', 'LEVEL_mean', "return statistics.median(values) if values else None",
     "return statistics.fmean(values) if values else None"),
    ('frm109.py', 'test_frf109.py', 'FIRST_ignored', "if len(kept) != hi - lo or min(kept) < first:",
     "if len(kept) != hi - lo:"),
    ('frm109.py', 'test_frf109.py', 'DURATION_half', ">= (meta.get('hold_s') or 0))", ">= (meta.get('hold_s') or 0) / 2)"),
    ('frm109.py', 'test_frf109.py', 'WORK_TOL_10x', "WORK_TOL = 0.005", "WORK_TOL = 0.05"),
    ('frm109.py', 'test_frf109.py', 'AREA_TOL_10x', "AREA_SPLIT_PCT, AREA_MATCH_PCT, AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 8",
     "AREA_SPLIT_PCT, AREA_MATCH_PCT, AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 5.0, 0.5, 8"),
    ('frm109.py', 'test_frf109.py', 'FATAL_no_waitslow', " b'GpuWaitSlow:',", ""),
    ('frm109.py', 'test_frf109.py', 'SYNC_new_plus_wait_ignored_wait', "controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK",
     "controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK + 1000"),
    ('frm109.py', 'test_frf109.py', 'PAIRS_min_60_to_10', "MIN_PAIRS = 60", "MIN_PAIRS = 10"),
    ('frm109.py', 'test_frf109.py', 'BANDS_dt_wide', "BANDS = {'dt_us': (28000.0, 40000.0),", "BANDS = {'dt_us': (1.0, 99000.0),"),
    # ent109.py
    ('ent109.py', 'test_ent109.py', 'E_slack_strict', "elif sb <= sa + SLACK:", "elif sb < sa + SLACK:"),
    ('ent109.py', 'test_ent109.py', 'E_pin_any_mode', "if line.startswith(b'GpuClockPin: mode 1'):", "if line.startswith(b'GpuClockPin:'):"),
    ('ent109.py', 'test_ent109.py', 'E_marker_no_fatal', " b'std::terminate', b'abort()', b'fatal',", " b'std::terminate', b'abort()',"),
    ('ent109.py', 'test_ent109.py', 'E_gates_contains', "if not gates.endswith(' ' + TOKEN[arm]) or", "if (' ' + TOKEN[arm]) not in (' ' + gates + ' ') or"),
    ('ent109.py', 'test_ent109.py', 'E_rows_500', "MIN_ROWS = 1000", "MIN_ROWS = 500"),
    ('ent109.py', 'test_ent109.py', 'E_hold_80pct', "< 0.95 * HOLD_S", "< 0.80 * HOLD_S"),
    ('ent109.py', 'test_ent109.py', 'E_order_dupes_ok', " or len(set(stamps)) != len(stamps)", ""),
    ('ent109.py', 'test_ent109.py', 'E_precache_last_line', "if m and queued is None:", "if m:"),
    # ent109b.py
    ('ent109b.py', 'test_ent109b.py', 'EB_bad_ignored', "if arm == 'B' and (tot['cspfree_hit'] <= 0 or tot['cspfree_bad']):",
     "if arm == 'B' and tot['cspfree_hit'] <= 0:"),
    ('ent109b.py', 'test_ent109b.py', 'EB_A_dark_look_only', "if arm == 'A' and (tot['cspfree_hit'] or tot['cspfree_look']):",
     "if arm == 'A' and tot['cspfree_look']:"),
    ('ent109b.py', 'test_ent109b.py', 'EB_slack_strict', "elif sb <= sa + SLACK:", "elif sb < sa + SLACK:"),
    # vfy109.py
    ('vfy109.py', 'test_vfy109.py', 'V_bar_08', "HIT_BAR = 0.9", "HIT_BAR = 0.8"),
    ('vfy109.py', 'test_vfy109.py', 'V_steady_all', "if n >= STEADY_FROM:", "if n >= 0:"),
    ('vfy109.py', 'test_vfy109.py', 'V_bad_steady_only', "bad = tot['cspfree_bad']", "bad = steady['cspfree_bad']"),
    ('vfy109.py', 'test_vfy109.py', 'V_gates_count', " or gates.count('cspfree=') != 1", ""),
    ('vfy109.py', 'test_vfy109.py', 'V_rows_1000', "MIN_ROWS = 5000", "MIN_ROWS = 1000"),
    ('vfy109.py', 'test_vfy109.py', 'V_moved_ignored_armed', "if tot['cspfree_look'] <= 0:", "if tot['cspfree_look'] < 0:"),
]
res = []
for scorer, test, name, a, b in M:
    src = (R / scorer).read_text(encoding='utf-8')
    c = src.count(a)
    if c != 1:
        print('%-34s anchor count %d - SKIPPED' % (name, c))
        res.append((name, 'SKIP'))
        continue
    mp = OUT / ('%s__%s' % (name, scorer))
    mp.write_text(src.replace(a, b), encoding='utf-8')
    args = [sys.executable, str(R / test), str(mp)]
    if test == 'test_frf109.py':
        args.append('C:/kyty/s106_stage/fx_frf109_audit109')
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=str(R))
    killed = 'ALL OK' not in r.stdout
    fails = [l.split()[0] for l in r.stdout.splitlines() if l.rstrip().endswith('FAIL')][:6]
    print('%-34s %s %s' % (name, 'killed' if killed else 'ALIVE', fails if killed else ''))
    res.append((name, 'killed' if killed else 'ALIVE'))
print('ALIVE:', [n for n, s in res if s == 'ALIVE'])
