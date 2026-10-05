"""probe602.py - S15r (HPP-602), Red Team: probes on the new code of S15a (no game, files only in the run scratch dir)."""
import importlib.util
import os
import pathlib
import subprocess
import sys

D = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location('es15', 'C:/kyty/s288/s15/enter_scene_s15.py')
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)

RULE = (120000000, 3000, 300000000)


def mk(name, lines, idx=0):
    p = D / name
    p.write_bytes(b''.join(l + b'\n' for l in lines))
    q = D / (name + '.idx')
    q.write_bytes(b''.join(b'%d 0 0.0\n' % i for i in range(idx)))
    return p, q


# P1: a FrameTrace row whose n is torn by an interleaved write
p, q = mk('p1.txt', [b'GuestOut: Level has started: lvl', b'FrameTrace: n=5 dt_us=30000 draws=3000',
                     b'FrameTrace: n=6GuestOut: x dt_us=30000 draws=3000'], 10)
u = E.UHold(p, q, 'lvl', RULE)
try:
    r = u.poll()
    print('P1 UHold.poll on a torn n: no exception, result %r' % (r,))
except Exception as e:  # noqa
    print('P1 UHold.poll on a torn n: EXCEPTION %s: %s' % (type(e).__name__, e))

# P1b: the same line through the scorer's scan (sc_s.scan_s)
spec2 = importlib.util.spec_from_file_location('scs', 'C:/kyty/s288/sc_s.py')
A = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(A)
try:
    s = A.scan_s(str(p))
    print('P1b sc_s.scan_s on the same log: rows %d torn %d' % (len(s['rows']), s['torn']))
except Exception as e:  # noqa
    print('P1b sc_s.scan_s on the same log: EXCEPTION %s: %s' % (type(e).__name__, e))

# P2: the hold loop body - is UHold.poll inside a try in enter_scene_s15.py?
src = open('C:/kyty/s288/s15/enter_scene_s15.py', encoding='ascii').read()
i = src.find('ucause = uh.poll()')
j = src.rfind('try:', 0, i)
k = src.rfind('finally:', 0, i)
print('P2 the first "ucause = uh.poll()" at char %d; the nearest "try:" before it at %d, the nearest "finally:" at %d -> %s' % (
    i, j, k, 'inside the finally: block of the attempt, no own try/except' if k > j else 'inside a try'))

# P3: the 2 999 / 3 000 and 119.999999 / 120 s edges of done() in one object
p, q = mk('p3.txt', [b'GuestOut: Level has started: lvl', b'FrameTrace: n=1 dt_us=1 draws=3000'] +
          [b'FrameTrace: n=%d dt_us=40000000 draws=3000' % (i + 2) for i in range(3)], 2999)
u = E.UHold(p, q, 'lvl', RULE)
print('P3 fi row + 3 x 40 s, 2 999 frames -> %r (shown %d)' % (u.poll(), u.shown()))
with open(q, 'ab') as f:
    f.write(b'2999 0 0.0\n')
print('P3 + 1 frame (3 000) -> %r' % (u.poll(),))

# P4: the plan lines of the 39 tags (sc_s15.py --plan) against section 3 of the seal: the 11th field
seal = open('C:/kyty/s288/pred/14_s.md', encoding='ascii').read()
bad = 0
for t in ['k_%02d' % i for i in range(1, 20)] + ['u_%02d' % i for i in range(1, 20)] + ['w13']:
    out = subprocess.run([sys.executable, 'C:/kyty/s288/s15/sc_s15.py', '--plan', t], capture_output=True, text=True).stdout.strip()
    f = out.split()
    hu = f[10] if len(f) > 10 else None
    want = '120:3000:300' if t.startswith('u_') else '-'
    ln = [l for l in seal.splitlines() if l.strip().startswith('PLAN %s:' % t)]
    has = ln and (('--hold-u 120:3000:300' in ln[0]) == t.startswith('u_'))
    if hu != want or not has:
        bad += 1
        print('P4 MISMATCH', t, out, bool(ln))
print('P4 plan field 11 and the seal PLAN line (--hold-u only on u_NN): 39 tags, mismatches %d' % bad)
