# Between-run indication of the guards' constant cost (audit 111): shp110 arm 1 (b3f7a2c9, cspfree=1, no guards)
# versus shp111 arm 0 (c8235c90, daslot=0 with guards). Different runs: an indication, not a measurement.
import sys, math, statistics as st
sys.path.insert(0, 'C:/kyty/s111/audit111')
from abba import load, blocks, bmean, val

keys = ('dt_us', 'cpu_net_us', 'cpu_gpu_us', 'gpu_busy_us', 'draws', 'da_walk_us', 'da_queue_us', 'da_take_us', 'da_hit',
        'da_miss', 'da_late', 'semwait_us', 'kpx_per_att', 'vbl1', 'vbl3p', 'sync_up_kb', 'fault_us', 'da_wlag_us', 'cspfree_hit')


def arm_blocks(tag, arm, lo=10, hi=90):
    P = load(tag); garm, elig, pairs, mism, rej = blocks(P, lo, hi, 2100)
    used = sorted({b for p in pairs for b in p})
    return P['rows'], [elig[b] for b in used if garm[b] == arm]


R = {}
for tag, arm in (('shp110', 0), ('shp110', 1), ('shp111', 0), ('shp111', 1)):
    rows, bl = arm_blocks(tag, arm)
    R[(tag, arm)] = {}
    for k in keys:
        bm = [bmean(rows, ns, k) for ns in bl]
        bm = [x for x in bm if x is not None]
        if not bm: continue
        m = sum(bm) / len(bm); se = st.stdev(bm) / math.sqrt(len(bm))
        R[(tag, arm)][k] = (m, se, len(bm))
print('key'.ljust(13), 'shp110 a0 (cspfree0)', 'shp110 a1 (cspfree1)', 'shp111 a0 (daslot0+guards)', 'shp111 a1 (daslot1)',
      '  s111a0 - s110a1 (2SE, block-level, ignores run effects)')
for k in keys:
    line = k.ljust(13)
    for c in (('shp110', 0), ('shp110', 1), ('shp111', 0), ('shp111', 1)):
        v = R[c].get(k)
        line += ('%12.1f' % v[0]) if v else ' ' * 12
    a = R[('shp111', 0)].get(k); b = R[('shp110', 1)].get(k)
    if a and b:
        line += '   %9.1f (%.1f)' % (a[0] - b[0], 2 * math.sqrt(a[1] ** 2 + b[1] ** 2))
    print(line)
