# Cross-run INDICATION only (audit 112): kept rows 10..89 of ABBA blocks from frame 2100, per arm.
import sys, statistics as st
sys.path.insert(0, 'C:/kyty/s112/audit112')
from abba112 import load, blocks, bmean, levels

KEYS = ('dt_us', 'cpu_net_us', 'gpu_busy_us', 'draws', 'da_walk_us', 'da_queue_us', 'da_qcall', 'q_per_call',
        'da_take_us', 'da_hit', 'da_miss', 'da_late', 'da_busy', 'da_q', 'da_nohint', 'da_work_us', 'srt_miss',
        'bda_scan', 'kpx_per_att', 'vbl1', 'semwait_us', 'cpu_record_us', 'da_wlag_us', 'pmemo_hit', 'faults',
        'da_unused', 'da_hint_defer')
RUNS = (('fam108', 'cspfam 0', 'cspfam 4'), ('frm109', 'cspfree 0', 'cspfree 1'), ('shp110', 'cspfree 0', 'cspfree 1'),
        ('shp111', 'daslot 0 (guards)', 'daslot 1'), ('net112', 'daslot 1', 'daslot 0 guard 0'))
tab = {}
for tag, a0, a1 in RUNS:
    P = load(tag); rows = P['rows']
    garm, elig, pairs, mism, rej = blocks(P)
    used = sorted({b for p in pairs for b in p})
    for a, lab in ((0, a0), (1, a1)):
        tab[(tag, a)] = (lab, {k: st.fmean([m for m in (bmean(rows, elig[b], k) for b in used if garm[b] == a)
                                            if m is not None] or [float('nan')]) for k in KEYS}, len(pairs))
cols = [(t, a) for t, _, _ in RUNS for a in (0, 1)]
print('%-14s' % 'key' + ''.join('%16s' % ('%s/%d' % (t, a)) for t, a in cols))
print('%-14s' % 'label' + ''.join('%16s' % tab[c][0][:15] for c in cols))
for k in KEYS:
    print('%-14s' % k + ''.join('%16.3f' % tab[c][1][k] for c in cols))
