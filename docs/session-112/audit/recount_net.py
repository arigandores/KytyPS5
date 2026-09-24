# Recount of net112 (audit 112): main estimator, secondary, full block, robustness, levels, N1-N7.
import sys, statistics as st
sys.path.insert(0, 'C:/kyty/s112/audit112')
from abba112 import *

tag = sys.argv[1] if len(sys.argv) > 1 else 'net112'
P = load(tag); rows = P['rows']
print('tag', tag, 'rows', len(rows), 'gatearm', len(P['gates']))
arms_txt = {}
for g in P['gates']:
    arms_txt.setdefault(g[1], set()).add(g[6])
print('arm texts', {a: sorted(t) for a, t in arms_txt.items()})
print('abba/period/arms', sorted({(g[3], g[4], g[5]) for g in P['gates']}))
# block orientation check
seq = [g[1] for g in sorted(P['gates'])]
print('first 16 arms', seq[:16], 'count', len(seq))
for byrow in (False, True):
    garm, elig, pairs, mism, rej = blocks(P, byrow=byrow)
    print('byrow', byrow, 'eligible', len(elig), 'pairs', len(pairs), 'row arm/blk mismatches', mism, 'rejected', rej)
garm, elig, pairs, mism, rej = blocks(P)
used = sorted({b for p in pairs for b in p})
orient = [(garm[a], garm[b]) for a, b in pairs]
print('orientations', {o: orient.count(o) for o in set(orient)})
print('markers', {k.decode(): v for k, v in P['counts'].items() if v})
KEYS = ('dt_us', 'cpu_net_us', 'cpu_gpu_us', 'spin_gpu_us', 'gpu_busy_us', 'draws', 'dispatches', 'rec_n', 'da_walk_us',
        'da_queue_us', 'da_qcall', 'q_per_call', 'da_take_us', 'da_hit', 'da_miss', 'da_late', 'da_stale', 'da_busy',
        'da_walks', 'da_q', 'da_nohint', 'da_present', 'da_work_us', 'bda_scan', 'bda_n', 'srt_miss', 'img_up_kb',
        'kpx_per_att', 'vbl1', 'vbl2', 'vbl3p', 'long50', 'cpu_main_us', 'semwait_us', 'lat_us', 'faults', 'fault_us',
        'da_q_free', 'da_q_noguard', 'da_guard_yield', 'da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn',
        'cspfree_hit', 'cs_sync_new', 'cs_sync_wait', 'da_wjobs', 'da_wlag_us', 'da_wdepth', 'pl_wq_hold_ns',
        'pl_wq_hold_n', 'da_unused', 'prot_us', 'cpu_record_us', 'pmemo_hit')
print('\n== main estimator rows 10..89: d = arm1 - arm0 (arm1 = daslot0 daguard0), levels median(mean) of block means')
for k in KEYS:
    d = diffs(rows, garm, elig, pairs, k)
    if len(d) < 2:
        continue
    lv = levels(rows, garm, elig, used, k)
    m, se2, t = quick(d)
    print('%-15s d %10.3f 2SE %8.3f t %7.2f | arm0 med %11.3f mean %11.3f | arm1 med %11.3f mean %11.3f' % (
        k, m, se2, t, lv[0][0], lv[0][1], lv[1][0], lv[1][1]))
print('\nfull stats dt_us  ', fmt(summ(diffs(rows, garm, elig, pairs, 'dt_us'))))
print('full stats cpu_net', fmt(summ(diffs(rows, garm, elig, pairs, 'cpu_net_us'))))
# N1/N2 as the seal defines: level da_queue_us / level da_qcall (median of block means)
lq = levels(rows, garm, elig, used, 'da_queue_us'); lc = levels(rows, garm, elig, used, 'da_qcall')
print('N1 arm1 per call %.4f (median ratio), mean-based %.4f' % (lq[1][0] / lc[1][0], lq[1][1] / lc[1][1]))
print('N2 arm0 per call %.4f (median ratio), mean-based %.4f' % (lq[0][0] / lc[0][0], lq[0][1] / lc[0][1]))
# secondary, 60..88 (kept index 50..79 of the 10..89 window -> block index 60..88)
g2, e2, p2, _, _ = blocks(P, lo=60, hi=89)
for k in ('dt_us', 'cpu_net_us'):
    print('secondary 60..88 %-10s' % k, fmt(summ(diffs(rows, g2, e2, p2, k))), 'pairs', len(p2))
g3, e3, p3, _, _ = blocks(P, lo=0, hi=90)
for k in ('dt_us', 'cpu_net_us', 'gpu_busy_us'):
    print('full block 0..89 %-10s' % k, fmt(summ(diffs(rows, g3, e3, p3, k))), 'pairs', len(p3))
# thirds of the run (by pair order)
d = diffs(rows, garm, elig, pairs, 'dt_us')
n3 = len(d) // 3
for i in range(3):
    part = d[i * n3:(i + 1) * n3] if i < 2 else d[2 * n3:]
    print('third %d dt' % (i + 1), '%.1f 2SE %.1f t %.2f n %d' % (quick(part) + (len(part),)))
# capped flips
for cap in (41667, 50000, 60000):
    print('capped dt at %d' % cap, fmt(summ(diffs(rows, garm, elig, pairs, 'dt_us', cap=cap))))
# medians of per-block medians
def bmed(ns, key):
    return st.median([val(rows[n], key) for n in ns])
dm = []
for a, b in pairs:
    x = bmed(elig[a], 'dt_us'); y = bmed(elig[b], 'dt_us')
    dm.append(x - y if garm[a] == 1 else y - x)
print('block-median dt d', '%.1f 2SE %.1f t %.2f' % quick(dm))
# long-flip distribution per arm (kept rows)
for a in (0, 1):
    vs = [rows[n]['dt_us'] for b in used if garm[b] == a for n in elig[b]]
    vs.sort()
    N = len(vs)
    def q(p): return vs[min(N - 1, int(p * N))]
    print('arm %d rows %d mean %.1f p10 %d p50 %d p90 %d p99 %d max %d  >=41667 %.4f  >=50000 %.4f  >=66667 %.4f  <25000 %.4f' % (
        a, N, sum(vs) / N, q(.1), q(.5), q(.9), q(.99), vs[-1], sum(v >= 41667 for v in vs) / N,
        sum(v >= 50000 for v in vs) / N, sum(v >= 66667 for v in vs) / N, sum(v < 25000 for v in vs) / N))
# pair-level outliers
ds = sorted(d)
print('pair d dt min/max', ds[:3], ds[-3:])
print('pairs with d<0', sum(x < 0 for x in d), 'of', len(d))
# trimmed mean (10%)
k = len(ds) // 10
print('10%% trimmed mean %.1f' % (sum(ds[k:len(ds) - k]) / (len(ds) - 2 * k)))
