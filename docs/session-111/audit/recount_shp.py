# Recount of shp111 (audit 111): main estimator rows 10..89, secondary 60..88, full block, levels, K1-K6.
import sys, statistics as st
sys.path.insert(0, 'C:/kyty/s111/audit111')
from abba import load, blocks, diffs, summ, fmt, quick, bmean, val

tag = sys.argv[1] if len(sys.argv) > 1 else 'shp111'
P = load(tag); rows = P['rows']
print('==', tag, 'rows', len(rows), 'GateArm', len(P['gates']))
for lo, hi, first, name in ((10, 90, 2100, 'MAIN 10..89'), (60, 89, 2100, 'SECONDARY 60..88'), (0, 90, 1801, 'FULL 0..89')):
    garm, elig, pairs, mism, rej = blocks(P, lo, hi, first)
    used = sorted({b for p in pairs for b in p})
    exc = sorted(b for b in elig if b not in used)
    print('--', name, 'blocks', len(garm), 'eligible', len(elig), 'pairs', len(pairs), 'arm-mismatch rows', mism,
          'excluded', exc, 'rejected', {k: v for k, v in rej.items()})
    orient = sum(1 for a, b in pairs if garm[a] == 0)
    print('   orientation AB', orient, 'BA', len(pairs) - orient)
    for key in ('dt_us', 'cpu_net_us', 'gpu_busy_us', 'da_walk_us', 'da_queue_us', 'da_take_us', 'da_miss', 'da_hit',
                'da_late', 'draws', 'semwait_us', 'cpu_main_us', 'spin_gpu_us', 'cpu_gpu_us', 'kpx_per_att', 'rt_kpx', 'rt_att',
                'vbl1', 'vbl2', 'vbl3p', 'da_q_free', 'da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_qcall', 'fault_us',
                'prot_us', 'sync_up_kb', 'img_up_kb', 'da_wlag_us'):
        d = diffs(rows, garm, elig, pairs, key)
        if len(d) < 3: continue
        s = summ(d, R=4000 if key != 'dt_us' else 20000)
        print('   d', key.ljust(14), fmt(s))
    # arm levels: median of block means, and pooled mean
    for key in ('dt_us', 'cpu_net_us', 'da_q_free', 'da_guard_busy', 'da_miss', 'da_q_taking', 'da_hint_defer', 'da_hint_torn',
                'da_slot_bad', 'cspfree_hit', 'cspfree_bad', 'cs_sync_new', 'cs_sync_wait', 'draws', 'kpx_per_att', 'vbl1', 'vbl3p'):
        lv = []
        for a in (0, 1):
            bm = [bmean(rows, elig[b], key) for b in used if garm[b] == a]
            bm = [x for x in bm if x is not None]
            tot = sum(val(rows[n], key) or 0 for b in used if garm[b] == a for n in elig[b])
            lv.append('arm%d med %.3f mean %.3f total %.1f' % (a, st.median(bm), sum(bm) / len(bm), tot))
        print('   level', key.ljust(14), ' | '.join(lv))
# all-rows totals from frame 2100
tot = {}
for n, r in rows.items():
    if n < 2100: continue
    for k in ('da_slot_bad', 'cspfree_bad', 'da_hint_torn'):
        tot[k] = tot.get(k, 0) + r.get(k, 0)
    for k in ('cs_sync_new',):
        a = r.get('arm')
        tot[(k, a)] = tot.get((k, a), 0) + r.get(k, 0)
print('totals n>=2100', tot)
print('all rows totals da_slot_bad', sum(r.get('da_slot_bad', 0) for r in rows.values()),
      'cspfree_bad', sum(r.get('cspfree_bad', 0) for r in rows.values()))
