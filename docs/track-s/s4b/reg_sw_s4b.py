#!/usr/bin/env python3
"""S4b (HPP-349, item 265 (v)(4)): the scorer of seal 03 on the four sw_* logs against score_sw_*.txt of seal 02.
Reads s4b/reg/score_<tag>.s03.txt (python sc_s.py --tag <tag> --json-out s4b/reg/<tag>.s03.json) and s4/score_<tag>.txt;
prints every differing line by number; the only allowed difference is the prereg row of the seal (its name).  The score
files are CRLF (stdout of Windows); lines are compared byte for byte, the CR is stripped only to name the row.  ASCII only."""
import hashlib
import sys

R = 'C:/kyty/s288/'
CR = chr(13)
OLD = '  PASS admit prereg = the seal now (829ac684)'
NEW = '  PASS admit prereg = the seal of its run 02_s.md (item 265 (g)) (829ac684)'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


ok = True
print('reg_sw_s4b sc_s.py sha256 %s' % sha(R + 'sc_s.py'))
for t in ('sw_m1', 'sw_m2', 'sw_m3', 'sw_t1'):
    a = R + 's4/score_%s.txt' % t
    b = R + 's4b/reg/score_%s.s03.txt' % t
    la = open(a, 'rb').read().decode('ascii').split(chr(10))
    lb = open(b, 'rb').read().decode('ascii').split(chr(10))
    diff = [(i + 1, x, y) for i, (x, y) in enumerate(zip(la, lb)) if x != y]
    same_len = len(la) == len(lb)
    named = all(x.rstrip(CR) == OLD and y.rstrip(CR) == NEW for _, x, y in diff)
    print('%s: seal 02 %s sha256 %s (%d lines); seal 03 %s sha256 %s (%d lines); differing lines %s' % (
        t, a, sha(a), len(la), b, sha(b), len(lb), [i for i, _, _ in diff]))
    for i, x, y in diff:
        print('  line %d: seal 02 "%s" -> seal 03 "%s"' % (i, x.strip(), y.strip()))
    ok &= same_len and len(diff) == 1 and named
print('SW REGRESSION: %s' % ('ALL OK (only the prereg row name differs, line 13 of each)' if ok else 'DIVERGENCE'))
sys.exit(0 if ok else 1)
