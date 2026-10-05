"""F20e (HPP-624): manual sensitivity of test_f20e_read.py - each edit of f20e_read.py below must make the suite fail (exit != 0).
Form of F18e sens_f18e.py; the edits run 8 at a time.  usage: python sens_f20e.py   (ASCII only; ends with ALL OK when every edit is
caught)"""
import concurrent.futures
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, 'f20e_read.py'), 'rb').read().decode('utf-8')
print('suite sens_f20e.py sha256 %s target f20e_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(SRC.encode('utf-8')).hexdigest()))
EDITS = [
    ('B2 window low 722', 'B2_LO, B2_HI = 723, 828', 'B2_LO, B2_HI = 722, 828'),
    ('B2 window low 724', 'B2_LO, B2_HI = 723, 828', 'B2_LO, B2_HI = 724, 828'),
    ('B2 window high 829', 'B2_LO, B2_HI = 723, 828', 'B2_LO, B2_HI = 723, 829'),
    ('B2 window high 827', 'B2_LO, B2_HI = 723, 828', 'B2_LO, B2_HI = 723, 827'),
    ('slow threshold > 100 ms', 'SLOW_US = 100000', 'SLOW_US = 100001'),
    ('entry window 10 s + 1 us', 'WIN_US = 10000000', 'WIN_US = 10000001'),
    ('hold 300 s + 1 us', 'HOLD_US = 300000000', 'HOLD_US = 300000001'),
    ('B2 frame ignores the cache save', "if x[6] == 0 and x[7] == 0] if e['warm']", "if x[7] == 0] if e['warm']"),
    ('B2 frame ignores the trip', "if x[6] == 0 and x[7] == 0] if e['warm']", "if x[6] == 0] if e['warm']"),
    ('warm ignores the dump', "e['warm'] = bool(e['window_read'] and e['window_dump'] == 0)", "e['warm'] = bool(e['window_read'])"),
    ('dump counts IR only', "e['window_dump'] = sum(x[4] + x[5] for x in win)", "e['window_dump'] = sum(x[4] for x in win)"),
    ('window read at 827 frames', "e['window_read'] = len(fr) >= B2_HI", "e['window_read'] = len(fr) >= B2_HI - 1"),
    ('cache save is B33 on every binary', "        if pre:\n            return 'B33'", "        if True:\n            return 'B33'"),
    ('prio only is attributed', "UNATTR = ('nothing', 'prio only', 'pcs after S12')", "UNATTR = ('nothing', 'pcs after S12')"),
    ('trip not attributed', "    if trip:\n        return 'B1b'\n    if ir or gcn:", "    if ir or gcn:"),
    ('IR only without indentation', "        if t[:1] == b'%':", "        if line[:1] == b'%':"),
    ('tab-led GCN counted', "        elif line[:1] != b'\\t' and GCN.match(t):", "        elif GCN.match(t):"),
    ('first scene frame draws > 100', "if d and int(d.group(1)) >= 100:", "if d and int(d.group(1)) > 100:"),
    ('quit does not end the scene', "            if state == 1:\n                state = 2\n                r['ended_by'] = 'quit'",
     "            if False:\n                state = 2\n                r['ended_by'] = 'quit'"),
    ('empty level name ends the scene', "            name = line[i + len(LVL):].strip()\n            if name:",
     "            name = line[i + len(LVL):].strip()\n            if True:"),
    ('env check off', "run is not None and all(k in HARN for k in env)", "run is not None"),
    ('first flag wins', "            v = cmd[i + 1] if i + 1 < len(cmd) else ''", "            v = v or (cmd[i + 1] if i + 1 < len(cmd) else '')"),
    ('FS8 not admitted', "BIN_OK = {'2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b': 'FS8 2c9b69b9'}", 'BIN_OK = {}'),
    ('FS7 admitted', "BIN_OK = {'2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b': 'FS8 2c9b69b9'}",
     "BIN_OK = {'2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b': 'FS8 2c9b69b9', '8df61c009fbe6d7fd7f4e7576e89ab1b0989129336a26f6d1cdf8fd778fbffe7': 'FS7'}"),
    ('installed after not checked', "jbin is not None and inst_b == jbin and inst_a == jbin", "jbin is not None and inst_b == jbin"),
    ('prereg not checked', "pre is not None and pre == seal_sha", "True"),
    ('window events not checked', "e is not None and e['minimized'] == 0 and e['recovering'] == 0", "e is not None"),
    ('manifest not checked', "bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')", "True"),
    ('stand not checked', "e is not None and not e['stand']),", "e is not None),"),
    ('N target 29', 'N_TARGET = 30', 'N_TARGET = 29'),
    ('cold counted in B2', "            if e['warm']:\n                tags['warm'] += 1", "            if True:\n                tags['warm'] += 1"),
    ('interference counted', "        if not res['admitted']:\n            tags['interference'] += 1\n            continue",
     "        if not res['admitted']:\n            tags['interference'] += 1"),
    ('hold frame starts after 10 s', "hf = [x for x in fr if x[2] >= SLOW_US and x[3] >= WIN_US]", "hf = [x for x in fr if x[2] >= SLOW_US and x[3] > WIN_US]"),
    ('unattributed counted without hold', "e['unattr'] = sum(1 for x in rows if x['letter'] in UNATTR) if e['hold'] else 0",
     "e['unattr'] = sum(1 for x in rows if x['letter'] in UNATTR)"),
    ('k1s inside the entry window', "e['k1s_after'] = sum(1 for x in fr if x[2] >= K1S_US and x[3] >= WIN_US)",
     "e['k1s_after'] = sum(1 for x in fr if x[2] >= K1S_US)"),
    ('base warm 27', 'BASE = dict(warm=28, b2=0)', 'BASE = dict(warm=27, b2=0)'),
    ('base warm 29', 'BASE = dict(warm=28, b2=0)', 'BASE = dict(warm=29, b2=0)'),
    ('B32 base not zero', "base['b2'], holds=0, unattr=0", "base['b2'], holds=1, unattr=0"),
    ('B32 stop at 28 clean holds', 'B32_HOLDS = 29', 'B32_HOLDS = 28'),
    ('B32 stop at 30 clean holds', 'B32_HOLDS = 29', 'B32_HOLDS = 30'),
    ('(ii) ignores the unattributed hold', "stop_b32 = s['unattr'] >= 1 or ", 'stop_b32 = '),
    ('(ii) on variant F20a', "stop_b32 = s['unattr'] >= 1 or ", "stop_b32 = s['unattr_f20a'] >= 1 or "),
    ('stop needs only (i)', 'need_more=not (stop_b2 and stop_b32)', 'need_more=not stop_b2'),
    ('stop needs only (ii)', 'need_more=not (stop_b2 and stop_b32)', 'need_more=not stop_b32'),
    ('stop on either', 'need_more=not (stop_b2 and stop_b32)', 'need_more=not (stop_b2 or stop_b32)'),
    ('B32 one-sided bound 0.10', '1 - 0.05 ** (1.0 / n)', '1 - 0.10 ** (1.0 / n)'),
    ('tag cap 31', 'TAG_MAX = 30', 'TAG_MAX = 31'),
    ('hold 120 s admitted', "('hold %d s (%s)' % (HOLD_S, (run or {}).get('hold_s')), (run or {}).get('hold_s') == HOLD_S)",
     "('hold %d s (%s)' % (HOLD_S, (run or {}).get('hold_s')), True)"),
]
T = tempfile.mkdtemp(prefix='f20e_sens_')
shutil.copy2(os.path.join(HERE, 'test_f20e_read.py'), os.path.join(T, 'test_f20e_read.py'))


def one(k):
    name, old, new = EDITS[k]
    if SRC.count(old) != 1:
        return name, None, 'ANCHOR count %d' % SRC.count(old)
    d = os.path.join(T, 'e%02d' % k)
    os.makedirs(d)
    shutil.copy2(os.path.join(T, 'test_f20e_read.py'), os.path.join(d, 'test_f20e_read.py'))
    open(os.path.join(d, 'f20e_read.py'), 'wb').write(SRC.replace(old, new).encode('utf-8'))
    p = subprocess.run([sys.executable, os.path.join(d, 'test_f20e_read.py')], capture_output=True, cwd=d)
    nf = [x for x in p.stdout.decode('ascii', 'replace').split('\n') if x.startswith('checks ')]
    return name, p.returncode != 0, nf[-1].strip() if nf else 'no count (rc %d)' % p.returncode


bad = []
try:
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        for name, caught, note in ex.map(one, range(len(EDITS))):
            print('%s %s (%s)' % ('CAUGHT' if caught else 'MISSED' if caught is not None else 'ANCHOR', name, note))
            if not caught:
                bad.append(name)
finally:
    shutil.rmtree(T, ignore_errors=True)
print('edits %d missed %d' % (len(EDITS), len(bad)))
if bad:
    print('MISSED:', bad)
    sys.exit(1)
print('ALL OK')
