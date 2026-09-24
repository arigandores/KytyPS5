# Estimator sensitivity of shp111 (audit 111): windows, caps, halves/quarters, in-block profile, vblank decomposition.
import sys, math, statistics as st
sys.path.insert(0, 'C:/kyty/s111/audit111')
from abba import load, blocks, diffs, summ, fmt, quick, bmean

tag = sys.argv[1] if len(sys.argv) > 1 else 'shp111'
P = load(tag); rows = P['rows']
# use the full-block selection (96 pairs) and the main-window pair set (94) separately
gF, eF, pF, _, _ = blocks(P, 0, 90, 1801)
gM, eM, pM, _, _ = blocks(P, 10, 90, 2100)
print('== windows on the main pair set (94 pairs; block rows from the full-block selection)')
common = [p for p in pF if p in pM]
for lo, hi in ((0, 90), (10, 90), (0, 30), (30, 60), (60, 90), (60, 89), (10, 50), (50, 90), (0, 10)):
    d = diffs(rows, gF, eF, common, 'dt_us', lo=lo, hi=hi)
    print('  rows %2d..%2d  %s' % (lo, hi - 1, fmt(summ(d, R=4000))))
print('== caps on the main window')
for cap in (None, 45000, 34500, 25000):
    d = diffs(rows, gM, eM, pM, 'dt_us', cap=cap)
    m, s2, t = quick(d)
    print('  cap %-6s d %.1f 2SE %.1f t %.2f' % (cap, m, s2, t))
d = diffs(rows, gM, eM, pM, 'dt_us')
h = len(d) // 2
print('== halves/quarters of the run (main window)')
print('  first half ', '%.1f 2SE %.1f t %.2f' % quick(d[:h]))
print('  second half', '%.1f 2SE %.1f t %.2f' % quick(d[h:]))
q = len(d) // 4
for i in range(4): print('  quarter %d  %.1f 2SE %.1f t %.2f' % ((i,) + quick(d[i * q:(i + 1) * q])))
# trimmed / winsorized pair diffs
ds = sorted(d); k = int(0.05 * len(ds))
tr = ds[k:len(ds) - k]
print('== 5%%-trimmed mean of pair diffs %.1f (n %d); median %.1f' % (sum(tr) / len(tr), len(tr), st.median(ds)))
# in-block profile: mean dt by position (arm1-arm0) in bins of 10 rows, over the common pair set
print('== in-block profile (arm1 - arm0), bins of 10 rows')
for lo in range(0, 90, 10):
    dd = diffs(rows, gF, eF, common, 'dt_us', lo=lo, hi=lo + 10)
    print('  %2d..%2d  %.1f 2SE %.1f' % ((lo, lo + 9) + quick(dd)[:2]))
# vblank decomposition on the main window: share of 1/2/3+ vblank flips per arm, and the implied dt change
def shares(arm):
    ns = [n for b, ks in eM.items() if gM[b] == arm and any(b in p for p in pM) for n in ks]
    v = [rows[n]['dt_us'] for n in ns]
    c1 = sum(1 for x in v if x < 25000); c2 = sum(1 for x in v if 25000 <= x < 41667); c3 = len(v) - c1 - c2
    m1 = st.mean([x for x in v if x < 25000]) if c1 else 0
    m2 = st.mean([x for x in v if 25000 <= x < 41667]) if c2 else 0
    m3 = st.mean([x for x in v if x >= 41667]) if c3 else 0
    return len(v), c1 / len(v), c2 / len(v), c3 / len(v), m1, m2, m3, st.mean(v)
s0, s1 = shares(0), shares(1)
print('== vblank classes (main window): n, share1, share2, share3+, mean1, mean2, mean3+, mean')
print('  arm0', ['%.4f' % x if isinstance(x, float) else x for x in s0])
print('  arm1', ['%.4f' % x if isinstance(x, float) else x for x in s1])
print('  implied by share shift at arm-0 class means: %.1f us; within-class shifts: %.1f us' % (
    (s1[1] - s0[1]) * s0[4] + (s1[2] - s0[2]) * s0[5] + (s1[3] - s0[3]) * s0[6],
    s1[1] * (s1[4] - s0[4]) + s1[2] * (s1[5] - s0[5]) + s1[3] * (s1[6] - s0[6])))
# long (>=41.7 ms) flips per arm and per in-block third, main window
for arm in (0, 1):
    c = [0, 0, 0]
    for b, ks in eM.items():
        if gM[b] != arm or not any(b in p for p in pM): continue
        for i, n in enumerate(ks):
            if rows[n]['dt_us'] >= 41667: c[min(2, i // 27)] += 1
    print('  arm%d long flips by in-window third %s' % (arm, c))
