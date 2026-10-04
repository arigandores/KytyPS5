"""F15e (HPP-516): manual sensitivity of test_f15e_read.py - each edit of f15e_read.py below must make the suite fail (exit != 0).
usage: python sens_f15e.py   (ASCII only; ends with ALL OK when every edit is caught)"""
import hashlib, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, 'f15e_read.py'), 'rb').read().decode('utf-8')
print('suite sens_f15e.py sha256 %s target f15e_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(SRC.encode('utf-8')).hexdigest()))
EDITS = [
    ('hold threshold 300 s - 1 us', 'HOLD_MIN_US = 300000000', 'HOLD_MIN_US = 299999999'),
    ('video threshold 2999', 'VIDEO_MIN = 3000', 'VIDEO_MIN = 2999'),
    ('frame >= 1 s threshold +1 us', 'K2_US = 1000000', 'K2_US = 1000001'),
    ('FixB4 order vs the first GuestOut ignored', "and (r['guest_first'] is None or r['b4'][0][0] < r['guest_first']))", ')'),
    ('FixB4 mode ignored', 'all(mm == 1 for _, mm in r[\'b4\'])', 'True'),
    ('fatal counted before quit too', "                if r['quit_line'] is not None:\n                    r['fatal_after_quit'] += 1",
     "                r['fatal_after_quit'] += 1"),
    ('m_files line not counted', "                    r['null_after_quit'] += 1", "                    pass"),
    ('killed ignored', "end_ok = att.get('close_killed') is False and att.get('close_rc') is not None",
     "end_ok = att.get('close_rc') is not None"),
    ('other KYTY_FIX_ allowed', "fix_keys == ['KYTY_FIX_B4'] and ", ''),
    ('GAME_PATCH allowed', "and 'KYTY_GAME_PATCH' not in env", ''),
    ('version string ignored', 'return VERSION in open(path, \'rb\').read()', 'return True'),
    ('installed after not checked', 'after_ok=sha_a == WANT', 'after_ok=True'),
    ('manifest always EQUAL', "manifest_ok=bool(mc) and mc.startswith('manifest cmp EQUAL')", 'manifest_ok=True'),
    ('scene change does not end the hold', "if after_entry and r['scene_change_line'] is None:", 'if after_entry:'),
    ('hold_exit ignored', "hold_ok = att.get('outcome') == 'ok' and att.get('hold_exit') is None", "hold_ok = att.get('outcome') == 'ok'"),
    ('minimized not interference', "not res['win'].get('minimized') and ", ''),
    ('stdout death ignored', "death = r['death'] + (sd or [])", "death = r['death']"),
]
T = tempfile.mkdtemp(prefix='f15e_sens_')
bad = []
try:
    for fn in ('test_f15e_read.py',):
        shutil.copy2(os.path.join(HERE, fn), os.path.join(T, fn))
    for name, old, new in EDITS:
        if SRC.count(old) != 1:
            bad.append(name)
            print('ANCHOR %s: count %d' % (name, SRC.count(old)))
            continue
        open(os.path.join(T, 'f15e_read.py'), 'wb').write(SRC.replace(old, new).encode('utf-8'))
        p = subprocess.run([sys.executable, os.path.join(T, 'test_f15e_read.py')], capture_output=True, cwd=T)
        caught = p.returncode != 0
        nf = [x for x in p.stdout.decode('ascii', 'replace').split('\n') if x.startswith('checks ')]
        print('%s %s (%s)' % ('CAUGHT' if caught else 'MISSED', name, nf[-1].strip() if nf else 'no count'))
        if not caught:
            bad.append(name)
finally:
    shutil.rmtree(T, ignore_errors=True)
print('edits %d missed %d' % (len(EDITS), len(bad)))
if bad:
    sys.exit(1)
print('ALL OK')
