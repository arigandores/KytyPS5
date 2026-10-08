"""FS10c (HPP-686): hand mutations of fs10c_read.py (form of F25m sens_f25m.py) - each one must drop test_fs10c_read.py (rc != 0, no
'ALL OK'); the unmutated copy must pass.  Runs in a temp copy; the reader in place is not touched.  ASCII only.
usage: python sens_fs10c.py"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, 'fs10c_read.py'), encoding='ascii').read()
FW = "('full_waits 0 (%s)' % (None if summ is None else summ['full_waits']), summ is not None and summ['full_waits'] == 0)"
MUT = [
    ('K2_US = 1000000', 'K2_US = 1000001'),
    ('LF_S0_US = 2500000', 'LF_S0_US = 2500001'),
    ('STALL_US = 2900000', 'STALL_US = 2900001'),
    ('WIN_MS = 2000', 'WIN_MS = 1999'),
    ('EXIT_MS = 250', 'EXIT_MS = 249'),
    ('HOLD_STAND_S = 120', 'HOLD_STAND_S = 119'),
    ('HOLD_W_S = 310', 'HOLD_W_S = 309'),
    ('VIDEO_MIN = 3000', 'VIDEO_MIN = 2999'),
    ("draws is not None and draws >= 100", "draws is not None and draws >= 99"),
    ("x['mode'][0][1] < g)", "x['mode'][0][1] <= g + 10**9)"),
    ("x['mode'][0][0].startswith('LogAsync: mode=1 ')", "x['mode'][0][0].startswith('LogAsync: mode=')"),
    ("len(lf1_after), len(lf1)), not lf1_after)", "len(lf1_after), len(lf1)), True)"),
    (chr(10) + ' ' * 18 + FW, chr(10) + ' ' * 18 + FW.replace('== 0)', '>= 0)')),
    (chr(10) + ' ' * 14 + FW, chr(10) + ' ' * 14 + FW.replace('== 0)', '>= 0)')),
    ("all(s['on'] == on for s in sl) and cfg_on == [on])", "cfg_on == [on])"),
    ("p_ok = anchor is not None and bool(sl) and all(s['ln'] > anchor for s in sl)", "p_ok = True"),
    ("x is not None and x['diagb32'] == 0)", "True)"),
    ("i is not None and not ge1)", "i is not None)"),
    ("return s['t0_ms'] - WIN_MS <= t <= s['t1_ms'] + WIN_MS", "return s['t0_ms'] - WIN_MS < t <= s['t1_ms'] + WIN_MS"),
    ("bool(x['b13']) and all(v == 1 for v, l in x['b13'])", "bool(x['b13'])"),
    ("dual = [d for d in x['dual'] if d[0] and g is not None and d[1] < g]", "dual = [d for d in x['dual'] if d[0]]"),
    ("if base != 'fs10_s0':\n            ok = len(x['summary']) == 1", "if False:\n            ok = len(x['summary']) == 1"),
]


def run(src):
    d = tempfile.mkdtemp(prefix='fs10c_sens_')
    try:
        open(os.path.join(d, 'fs10c_read.py'), 'w', encoding='ascii', newline='\n').write(src)
        shutil.copy(os.path.join(HERE, 'test_fs10c_read.py'), d)
        p = subprocess.run([sys.executable, os.path.join(d, 'test_fs10c_read.py')], capture_output=True)
        return p.returncode, b'ALL OK' in p.stdout
    finally:
        shutil.rmtree(d, ignore_errors=True)


ok = True
rc, allok = run(SRC)
print('control unmutated: rc %d ALL OK %s' % (rc, allok))
ok &= rc == 0 and allok
for i, (a, b) in enumerate(MUT):
    if SRC.count(a) != 1:
        print('mutation %d: anchor count %d - BAD' % (i, SRC.count(a)))
        ok = False
        continue
    rc, allok = run(SRC.replace(a, b))
    killed = rc != 0 and not allok
    print('mutation %d %s: %s' % (i, a.strip()[:60].replace(chr(10), ' '), 'killed' if killed else 'SURVIVED'))
    ok &= killed
print('mutations %d' % len(MUT))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
