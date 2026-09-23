"""Auditor: is dab107's Delta cpu_net a consequence of the frame-interval mix (vblank quantisation)?"""
import re, math, statistics
from collections import defaultdict, Counter

LOG = 'C:/kyty/s107/log_dab107.txt'
rx = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')
main, drw = {}, {}
with open(LOG, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace: n='):
            d = dict((k.decode(), int(v)) for k, v in rx.findall(line)); main[d['n']] = d
        elif line.startswith(b'FrameTrace-draw: n='):
            d = dict((k.decode(), int(v)) for k, v in rx.findall(line)); drw[d['n']] = d
B = defaultdict(list)
for n in main:
    if n >= 1801:
        b, i = divmod(n - 1801, 90)
        if 60 <= i <= 88:
            B[b].append(n)
used = [b for b in range(4, 188)]
arm = {b: main[B[b][0]]['arm'] for b in used}
def cn(n): return main[n]['cpu_gpu_us'] - drw[n]['spin_gpu_us']
def vb(n): return int(round(main[n]['dt_us'] / 16667.0))
# per-frame relation cpu_net vs dt
for a in (0, 1):
    fr = [n for b in used if arm[b] == a for n in B[b]]
    for k in (1, 2, 3):
        s = [n for n in fr if vb(n) == k]
        if s:
            print('arm', a, 'vblank', k, 'n', len(s), 'mean dt', round(statistics.mean(main[n]['dt_us'] for n in s)),
                  'mean cpu_net', round(statistics.mean(cn(n) for n in s)), 'mean busy', round(statistics.mean(cn(n) / main[n]['dt_us'] for n in s), 4),
                  'draws', round(statistics.mean(main[n]['draws'] for n in s)))
# OLS slope of cpu_net on dt across all frames
fr = [n for b in used for n in B[b]]
x = [main[n]['dt_us'] for n in fr]; y = [cn(n) for n in fr]
mx, my = statistics.mean(x), statistics.mean(y)
sl = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)
print('slope cpu_net on dt across frames', sl)
# paired within-bucket comparison: per pair, mean cpu_net of 2-vblank frames arm1 - arm0
def pairs():
    for q in range(1, 47):
        bl = [4 * q + i for i in range(4)]
        yield bl[0], bl[1]
        yield bl[2], bl[3]
d2, dmix, dsum = [], [], []
for p in pairs():
    one = p[0] if arm[p[0]] == 1 else p[1]
    zero = p[1] if one == p[0] else p[0]
    def m2(b):
        s = [cn(n) for n in B[b] if vb(n) == 2]
        return statistics.mean(s) if s else None
    a1, a0 = m2(one), m2(zero)
    if a1 is not None and a0 is not None:
        d2.append(a1 - a0)
    c1 = sum(1 for n in B[one] if vb(n) == 1); c0 = sum(1 for n in B[zero] if vb(n) == 1)
    dmix.append(c1 - c0)
    # cpu_net - dt (i.e. idle part) paired
    dsum.append(statistics.mean(main[n]['dt_us'] - cn(n) for n in B[one]) - statistics.mean(main[n]['dt_us'] - cn(n) for n in B[zero]))
def st(v):
    m = statistics.mean(v); se = statistics.stdev(v) / math.sqrt(len(v)); return round(m, 1), round(2 * se, 1), round(m / se, 2), len(v)
print('paired d cpu_net within 2-vblank frames (mean, 2SE, t, n):', st(d2))
print('paired d (#1-vblank frames per 29) :', st(dmix))
print('paired d (dt - cpu_net) i.e. non-CPU part of the interval:', st(dsum))
# busy fraction overall
print('overall busy frac', sum(y) / sum(x))
# per-frame: use the previous frame's vblank? check dt sum over 2 frames

# robustness: paired median, sign count, per-draw CPU
pd, pcd = [], []
for p in pairs():
    one = p[0] if arm[p[0]] == 1 else p[1]
    zero = p[1] if one == p[0] else p[0]
    m = lambda b, k: statistics.mean(main[n][k] for n in B[b])
    pd.append(m(one, 'dt_us') - m(zero, 'dt_us'))
    cpd = lambda b: sum(cn(n) for n in B[b]) / sum(main[n]['draws'] for n in B[b])
    pcd.append(cpd(one) - cpd(zero))
print('paired d dt median', statistics.median(pd), 'positive', sum(1 for v in pd if v > 0), 'of', len(pd))
print('paired d cpu_net per draw (us/draw):', st(pcd), 'rel', statistics.mean(pcd) / 6.1)
