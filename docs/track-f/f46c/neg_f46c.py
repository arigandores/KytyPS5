"""F46c (HPP-800): the negative control of the fixture suites - hand mutants of f46c_read.py, next_f46c.py and f46c_vid.py (copies under
neg/, outside the seal), each run with its suite; every mutant must make its suite fail (rc != 0).  Prints one row per mutant and ALL OK
when every mutant is caught.  ASCII only.
usage: python neg_f46c.py"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NEG = os.path.join(HERE, 'neg')
os.makedirs(NEG, exist_ok=True)
M = [
    ('m1 F26Tint key compared as text (N1)', 'f46c_read.py', 'test_f46c_read.py',
     "all(t[0] == wm and int(t[1], 16) == wk for t in x['tint'])", "all(t[0] == wm and t[1] == '%016x' % 0 for t in x['tint'])"),
    ('m2 env key compared as text (N1)', 'f46c_read.py', 'test_f46c_read.py',
     "if hexnum(env[key]) is None or hexnum(env[key]) != hexnum(want[key]):", "if env[key] != want[key]:"),
    ('m3 NO_APPLY never', 'f46c_read.py', 'test_f46c_read.py', "no_apply=(cls in MARK and not cl),", "no_apply=False,"),
    ('m4 class layers allowed', 'f46c_read.py', 'test_f46c_read.py',
     "ALLOWED = ('kept_applied', 'kept why=decode', 'kept why=deferred')", "ALLOWED = ('kept_applied', 'kept why=decode', 'kept why=deferred', 'kept why=layers')"),
    ('m5 skipped draw member dead', 'f46c_read.py', 'test_f46c_read.py', "x['skipped'] == 0))", "True))"),
    ('m6 f26_kept = bucket_only identity dropped', 'f46c_read.py', 'test_f46c_read.py', "if fix_on and d['f26_kept'] != d['dcc_stale_bucket_only']:",
     "if False:"),
    ('m7 hold edge > 300 s', 'f46c_read.py', 'test_f46c_read.py', "hold >= HOLD_V_US),", "hold > HOLD_V_US),"),
    ('m8 the 4 keys: fill / size not checked', 'f46c_read.py', 'test_f46c_read.py', "keys_ok = all(e['found'] and e['stale_fill_size_ok'] for e in ev)",
     "keys_ok = all(e['found'] for e in ev)"),
    ('m9 FixF26 at =0 not checked', 'f46c_read.py', 'test_f46c_read.py', "not x['f26_any']))", "True))"),
    ('n1 event rule ignores NO_APPLY', 'next_f46c.py', 'test_next_f46c.py', "        elif e.get('no_apply'):", "        elif False:"),
    ('n2 event rule ignores the class', 'next_f46c.py', 'test_next_f46c.py', "        elif e.get('cls') not in ALLOWED:", "        elif False:"),
    ('n3 budget 150:00 stops', 'next_f46c.py', 'test_next_f46c.py', "    if s > BUDGET_S:\n        return 12", "    if s >= BUDGET_S:\n        return 12"),
    ('n4 _r2 without the lead item', 'next_f46c.py', 'test_next_f46c.py', "if rep != '1' and os.environ.get('F46C_REPEAT_OK') != '1':", "if False:"),
    ('n5 order not enforced', 'next_f46c.py', 'test_next_f46c.py', "        if not settled(rd, t)[0]:", "        if False:"),
    ('v1 theta edge strict', 'f46c_vid.py', 'test_f46c_vid.py', "        if dlt >= THETA:", "        if dlt > THETA:"),
    ('v2 d mean over channels', 'f46c_vid.py', 'test_f46c_vid.py', ".max(axis=2)", ".mean(axis=2)"),
    ('v3 window cap 601', 'f46c_vid.py', 'test_f46c_vid.py', "CAP = 600", "CAP = 601"),
    ('v4 exclusion ignored', 'f46c_vid.py', 'test_f46c_vid.py', "        if excl and (ma[p][1] <= DARK or mb[p][1] <= DARK):", "        if False:"),
    ('v5 candidate edge strict', 'f46c_vid.py', 'test_f46c_vid.py', "cand = d0 - d1b >= D_MIN", "cand = d0 - d1b > D_MIN"),
    ('v6 detector G <= 41', 'f46c_vid.py', 'test_f46c_vid.py', "(fr[:, :, 1] <= 40)", "(fr[:, :, 1] <= 41)"),
]
ok = True
for name, target, suite, a, b in M:
    src = open(os.path.join(HERE, target), encoding='ascii').read()
    if src.count(a) != 1:
        print('%s: ANCHOR count %d - not run' % (name, src.count(a)))
        ok = False
        continue
    p = os.path.join(NEG, '%s_%s' % (name.split()[0], target))
    open(p, 'w', encoding='ascii', newline='\n').write(src.replace(a, b))
    r = subprocess.run([sys.executable, os.path.join(HERE, suite), p], capture_output=True, text=True)
    last = [l for l in r.stdout.splitlines() if l.startswith('checks ')]
    caught = r.returncode != 0
    ok &= caught
    print('%s: rc %d %s %s' % (name, r.returncode, last[-1] if last else (r.stderr.strip().splitlines() or ['-'])[-1][:80],
                               'CAUGHT' if caught else 'NOT CAUGHT'))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
