"""Audit row: W0+ of sky123 arm 0 on window positions 10..87 (seal) vs 10..88 (ROADMAP p.50(в) text); auditor's own parser."""
import math, re, sys
FIELD = re.compile(rb'(\w+)=(-?\d+)')
M, X, arms = {}, {}, []
with open(sys.argv[1], 'rb') as f:
    for line in f:
        if line.startswith(b'GateArm:'):
            arms.append(dict((a.decode(), b.decode()) for a, b in re.findall(rb'(\w+)=(\S+)', line)))
        elif line.startswith(b'FrameTrace: '):
            d = {a.decode(): int(b) for a, b in FIELD.findall(line)}; M[d['n']] = d
        elif line.startswith(b'FrameTrace-x: '):
            d = {a.decode(): int(b) for a, b in FIELD.findall(line)}; X[d['n']] = d
st, per = int(arms[0]['frame']), int(arms[0]['period'])
fr = lambda b, lo, hi: [st + 1 + per * b + p for p in range(lo, hi + 1)]
ok = lambda b: all(n in M and n in X and M[n]['blk'] == b and M[n]['arm'] == int(arms[b]['arm']) for n in fr(b, 10, 88))
pairs = [(2 * k, 2 * k + 1) for k in range(len(arms) // 2) if ok(2 * k) and ok(2 * k + 1)]
a0 = [b for p in pairs for b in p if int(arms[b]['arm']) == 0]
fx = float(sys.argv[2])
for hi in (87, 88):
    bm = [sum(X[n]['gw_proc_ns'] for n in fr(b, 10, hi)) / 1000.0 / (hi - 9) for b in a0]
    m = sum(bm) / len(bm); se = math.sqrt(sum((x - m) ** 2 for x in bm) / (len(bm) - 1) / len(bm))
    print('window 10..%d: blocks %d W0 %.6f SE %.6f W0+ %.6f  U = W0+ x 0.5 x %.5f = %.2f us' % (
        hi, len(bm), m, se, m + 2 * se, fx, (m + 2 * se) * 0.5 * fx))
