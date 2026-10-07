"""F25m seal 2a (item 621): regression of tempo_f25m.py - the 9 W logs of track F with --plan-w yes and their run json must be TEMPO PASS
(limit 200 ms), the same 9 with --plan-w no must be FAIL (limit 100 ms, item 620 unchanged), the V and F25f references PASS with --plan-w
no, the three DISPLAY_OFF interference tags FAIL.  ASCII only; ends with REGRESS PASS / REGRESS FAIL.
usage: python regress_tempo2a_f25m.py"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tempo_f25m as TP  # noqa: E402

F = os.path.dirname(HERE)
print('suite regress_tempo2a_f25m.py sha256 %s target tempo_f25m.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
    hashlib.sha256(open(os.path.join(HERE, 'tempo_f25m.py'), 'rb').read()).hexdigest()))
W = [('fs9c', 'fs9_w'), ('fs8c', 'fs8_w'), ('fs6c', 'fs6_w'), ('fs4c', 'fs4_w'), ('fs2c', 'fs2_w'), ('f24e', 'b13_w'), ('f14g', 'f19_w1'),
     ('f12f', 'f12_w'), ('f10e', 'f10e_w')]
NW = [('fs9c', 'fs9_v'), ('f25f', 'f25_s01'), ('f25f', 'f25_s20'), ('f25f', 'f25_k01'), ('f25f', 'f25_k02'), ('f25f', 'f25_k05'),
      ('f25f', 'f25_z1')]
ok = True
n = 0


def row(name, t, want):
    global ok, n
    n += 1
    good = t['status'] == want
    ok &= good
    fps = '%.2f' % t['fps'] if t['fps'] else '-'
    print('%s %s: TEMPO %s (want %s) limit_ms %d fps %s frames %d (%s)' % ('ok  ' if good else 'FAIL', name, t['status'], want,
                                                                         t['limit_us'] // 1000, fps, t['frames'], t['why']))


for d, tag in W:
    lp = os.path.join(F, d, 'log_%s.txt' % tag)
    jp = os.path.join(F, d, '%s.json' % tag)
    row('%s/%s W plan yes' % (d, tag), TP.tempo(lp, None, plan_w=True, json_path=jp), 'PASS')
    row('%s/%s W plan no, no json' % (d, tag), TP.tempo(lp, None, plan_w=False), 'FAIL')
for d, tag in NW:
    lp = os.path.join(F, d, 'log_%s.txt' % tag)
    jp = os.path.join(F, d, '%s.json' % tag)
    row('%s/%s plan no' % (d, tag), TP.tempo(lp, None, plan_w=False, json_path=jp if os.path.isfile(jp) else None), 'PASS')
for tag in ('b36_s0', 'b36_s1', 'b36_f0'):
    lp = os.path.join(HERE, 'log_%s.txt' % tag)
    rp = os.path.join(HERE, 'runs', '%s.display_off' % tag, 'run.txt')
    jp = os.path.join(HERE, '%s.json' % tag)
    row('f25m/%s (DISPLAY_OFF) plan no' % tag, TP.tempo(lp, rp, plan_w=False, json_path=jp), 'FAIL')
print('rows %d' % n)
print('REGRESS PASS' if ok else 'REGRESS FAIL')
sys.exit(0 if ok else 1)
