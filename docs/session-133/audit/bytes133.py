# bytes133.py - Session Auditor s.133: byte-weighted repeat share of arm 2 (a ROW, not a reading of p.141(v)(6)).
# Own code; blocks by GateArm:, window 10..88 (p.55(b)), complete = all three streams present for every window row.
import re, sys
LOG = 'C:/kyty/s133/log_bc133.txt'
RE_REC = re.compile(rb'(FrameTrace(?:-draw|-x)?): n=(\d+) (.*)$')
RE_ARM = re.compile(rb'GateArm: arm=(\d+) arms=2 block=(\d+) frame=(\d+)')
NEED = {b'FrameTrace': {'arm'}, b'FrameTrace-draw': {'cb_copy_kb', 'cb_copy'}, b'FrameTrace-x': {'ob_stream_kb', 'ob_stream', 'rb_b2_kb', 'rb_b2_would', 'rb_b2_n'}}
rows = {k: {} for k in NEED}
arms = []
with open(LOG, 'rb') as f:
    for ln in f:
        if b'GateArm:' in ln:
            m = RE_ARM.search(ln)
            arms.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
            continue
        i = ln.find(b'FrameTrace')
        if i < 0:
            continue
        m = RE_REC.search(ln[i:].rstrip(b'\r\n'))
        if not m:
            continue
        d = {}
        for tok in m.group(3).split():
            k, _, v = tok.partition(b'=')
            if k.decode() in NEED[m.group(1)]:
                d[k.decode()] = int(v)
        rows[m.group(1)][int(m.group(2))] = d
tot = {'arm1': {}, 'arm2': {}}
for arm, b, F in arms:
    ns = [F + 1 + p for p in range(10, 89)]
    if not all(n in rows[k] for n in ns for k in NEED):
        continue
    t = tot['arm1' if arm == 0 else 'arm2']
    for n in ns:
        for k in NEED:
            for fld, v in rows[k][n].items():
                t[fld] = t.get(fld, 0) + v
    t['rows'] = t.get('rows', 0) + len(ns)
for a, t in tot.items():
    r = t['rows']
    print(a, 'rows', r, 'per frame: ob_stream_kb %.1f cb_copy_kb %.1f ob_stream %.1f cb_copy %.1f' % (
        t['ob_stream_kb'] / r, t['cb_copy_kb'] / r, t['ob_stream'] / r, t['cb_copy'] / r))
t = tot['arm2']
allkb = t['ob_stream_kb'] + t['cb_copy_kb']
print('arm2 rb_b2_kb per frame %.1f; byte share of repeats rb_b2_kb/(ob_stream_kb+cb_copy_kb) = %.4f; count share %.4f; mean KB per repeated copy %.3f, per any copy %.3f' % (
    t['rb_b2_kb'] / t['rows'], t['rb_b2_kb'] / allkb, t['rb_b2_would'] / t['rb_b2_n'], t['rb_b2_kb'] / t['rb_b2_would'], allkb / t['rb_b2_n']))
