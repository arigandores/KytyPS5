# Audit 112: new mutants of vdg112.py / check112.py / net112.py, run against the session's own fixture suites
# (copies in audit112/rerun, fixture dirs repointed into audit112/rerun). KILLED = the suite does not exit 0.
import subprocess, sys, time
from pathlib import Path

R = Path('C:/kyty/s112/audit112/rerun')
MUT = {
    'vdg112.py': ('test_vdg112.py', [
        ('V1_checked_max', 'if min(ratio) < CHECK_RATIO:', 'if max(ratio) < CHECK_RATIO:'),
        ('V2_d2_low_801', "lambda r: r['level'][1]['da_q_free'], 800, 1400)", "lambda r: r['level'][1]['da_q_free'], 801, 1400)"),
        ('V3_d3_high_1399', "lambda r: r['level'][0]['da_q_noguard'], 800, 1400)", "lambda r: r['level'][0]['da_q_noguard'], 800, 1399)"),
        ('V4_d5_max', "lambda r: min(r['ratio']), CHECK_RATIO, None)", "lambda r: max(r['ratio']), CHECK_RATIO, None)"),
        ('V5_level_max', "level = [{k: median(p[k]) for k in FIELDS} for p in per]", "level = [{k: float(max(p[k] or [0])) for k in FIELDS} for p in per]"),
        ('V6_d4_high_99', "lambda r: r['total']['da_guard_yield'], None, 100)", "lambda r: r['total']['da_guard_yield'], None, 99)"),
        ('V7_position_plus1', 'position[n] = counts.get(blk, 0)', 'position[n] = counts.get(blk, 0) + 1'),
        ('V8_no_identity', "        errors.append('IDENTITY')", "        pass"),
        ('V9_arm_rows_and', "if per[0]['n'] < MIN_MAIN_ROWS or per[1]['n'] < MIN_MAIN_ROWS:", "if per[0]['n'] < MIN_MAIN_ROWS and per[1]['n'] < MIN_MAIN_ROWS:"),
        ('V10_chk_ok_only', "p['chk'] += xrow[n].get('da_chk_ok', 0) + xrow[n].get('da_chk_bad', 0)", "p['chk'] += xrow[n].get('da_chk_ok', 0)"),
    ]),
    'check112.py': ('test_check112.py', [
        ('C1_binary_true', "checks = dict(binary=meta.get('binary_sha256') == BUILD_SHA,", "checks = dict(binary=True,"),
        ('C2_no_waitslow', "b'gpuwaitslow', ", ''),
        ('C3_no_devicelost', "b'errordevicelost',", ''),
        ('C4_no_hangabort', "MARKERS = (b'gpuhangabort', ", 'MARKERS = ('),
        ('C5_stable_gt', 'int(m.group(1)) >= stable', 'int(m.group(1)) > stable'),
        ('C6_frames_first_number', "mf = re.search(r'(\\d+) frames', text)", "mf = re.search(r'(\\d+)', text)"),
        ('C7_glitch_le1', "no_glitch=bool(mg) and int(mg.group(1)) == 0,", "no_glitch=not mg or int(mg.group(1)) == 0,"),
    ]),
    'net112.py': ('test_net112.py', [
        ('N_ship_us_half', 'SHIP_US = 0.0 ', 'SHIP_US = 0.5 '),
        ('N_n1_high_1125', "ratio(lev[1].get('da_queue_us'), lev[1].get('da_qcall')), 0.90, 1.12)", "ratio(lev[1].get('da_queue_us'), lev[1].get('da_qcall')), 0.90, 1.125)"),
        ('N_n7_high_41', "stats['da_miss']['mean'], -40, 40)", "stats['da_miss']['mean'], -40, 41)"),
        ('N_sync_slack_3', 'SYNC_SLACK = 2', 'SYNC_SLACK = 3'),
    ]),
}
only = sys.argv[1:] or list(MUT)
for src_name in only:
    test, muts = MUT[src_name]
    SRC = (R / src_name).read_text(encoding='utf-8')
    for name, old, new in muts:
        n = SRC.count(old)
        if n != 1:
            print('%-24s ANCHOR x%d' % (name, n), flush=True); continue
        path = R / ('mut_%s_%s' % (name, src_name))
        path.write_text(SRC.replace(old, new), encoding='utf-8', newline='\n')
        t0 = time.time()
        args = [sys.executable, str(R / test), str(path)]
        if src_name == 'net112.py':
            args.append(str(R / ('fx_%s' % name)))
        r = subprocess.run(args, capture_output=True, text=True, cwd=str(R))
        dead = r.returncode != 0
        fails = [l.split()[0] for l in r.stdout.splitlines() if l.rstrip().endswith(('FAIL', 'FAIL ')) or ' FAIL ' in l][:6]
        print('%-24s %s  (%.0f s) %s' % (name, 'KILLED' if dead else 'SURVIVED', time.time() - t0, fails), flush=True)
        path.unlink()
        if src_name == 'net112.py':
            import shutil
            shutil.rmtree(R / ('fx_%s' % name), ignore_errors=True)
