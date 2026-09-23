"""Independent recount of dab107 (auditor, no session code imported)."""
import re, math, statistics
from collections import defaultdict, Counter

LOG = 'C:/kyty/s107/log_dab107.txt'
rx = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')
main, drw, xx = {}, {}, {}
arms = []
fat = Counter()
with open(LOG, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace: n='):
            d = dict((k.decode(), int(v)) for k, v in rx.findall(line)); main[d['n']] = d
        elif line.startswith(b'FrameTrace-draw: n='):
            d = dict((k.decode(), int(v)) for k, v in rx.findall(line)); drw[d['n']] = d
        elif line.startswith(b'FrameTrace-x: n='):
            d = dict((k.decode(), int(v)) for k, v in rx.findall(line)); xx[d['n']] = d
        elif line.startswith(b'GateArm:'):
            arms.append(line.strip()[:200])
        else:
            for m in (b'skipped draw', b'GpuHangAbort', b'GpuWaitSlow', b'--- Error', b'--- Fatal', b'terminate', b'abort()',
                      b'DeviceLost', b'Unhandled', b'GpuClockPin', b'RecordThread: started', b'GpuCheckpoint'):
                if m in line:
                    fat[m] += 1
print('rows', len(main), len(drw), len(xx), 'GateArm lines', len(arms), fat)
print(arms[:3], arms[-2:])
# arm by block from GateArm lines: text -> arm index
armtext = {}
for a in arms:
    m = re.search(rb'arm=(\d+) .*block=(\d+) frame=(\d+).*text=(.*)$', a)
    armtext[int(m.group(2))] = (int(m.group(1)), int(m.group(3)), m.group(4))
B = defaultdict(list)
for n, d in main.items():
    if n < 1801:
        continue
    b = (n - 1801) // 90
    idx = (n - 1801) % 90
    if 60 <= idx <= 88:
        B[b].append(n)
FIELDS_X = ['da_qcall', 'da_wjobs']
def val(n, k):
    if k == 'cpu_net_us':
        return main[n]['cpu_gpu_us'] - drw[n]['spin_gpu_us']
    for src in (main, drw, xx):
        if n in src and k in src[n]:
            return src[n][k]
    return None
keys = ['dt_us', 'cpu_net_us', 'cpu_gpu_us', 'da_walk_us', 'da_queue_us', 'da_miss', 'da_late', 'da_take_us', 'da_qcall',
        'draws', 'gpu_busy_us', 'da_hit', 'rec_n']
# check arm field consistency
bad_arm = 0
blockarm = {}
for b, ns in B.items():
    a = set(main[n].get('arm') for n in ns)
    bl = set(main[n].get('blk') for n in ns)
    if len(a) != 1:
        bad_arm += 1
    blockarm[b] = (a.pop() if len(a) == 1 else None, bl)
print('blocks', len(B), 'mixed-arm blocks', bad_arm)
maxb = max(B)
means = {}
for b, ns in B.items():
    if len(ns) != 29 or ns[0] < 2100:
        continue
    means[b] = {k: sum(val(n, k) for n in ns) / len(ns) for k in keys}
    means[b]['arm'] = blockarm[b][0]
pairs = []
for q in range(0, maxb // 4 + 1):
    blks = [4 * q + i for i in range(4)]
    if not all(b in means for b in blks):
        continue
    for p in ((blks[0], blks[1]), (blks[2], blks[3])):
        a, c = means[p[0]], means[p[1]]
        if a['arm'] == c['arm']:
            print('SAME ARM PAIR', p)
            continue
        one, zero = (a, c) if a['arm'] == 1 else (c, a)
        pairs.append({k: one[k] - zero[k] for k in keys} | {'orient': a['arm']})
print('pairs', len(pairs), 'orient', Counter(p['orient'] for p in pairs))
for k in keys:
    xs = [p[k] for p in pairs]
    m = statistics.mean(xs); sd = statistics.stdev(xs); se = sd / math.sqrt(len(xs))
    print('d %-12s mean %9.2f 2SE %8.2f t %6.2f' % (k, m, 2 * se, m / se if se else float('nan')))
a0 = [means[b] for b in means if means[b]['arm'] == 0 and any(b in (4*q+i for i in range(4)) for q in range(maxb//4+1))]
# ratio of da_qcall arms using paired blocks only
used = set()
for q in range(0, maxb // 4 + 1):
    blks = [4 * q + i for i in range(4)]
    if all(b in means for b in blks): used |= set(blks)
for k in ('da_qcall', 'dt_us', 'cpu_net_us', 'da_walk_us', 'da_queue_us'):
    m0 = statistics.mean(means[b][k] for b in used if means[b]['arm'] == 0)
    m1 = statistics.mean(means[b][k] for b in used if means[b]['arm'] == 1)
    print('arm means %-12s %10.2f %10.2f diff %8.2f ratio %.4f' % (k, m0, m1, m1 - m0, m1 / m0 if m0 else float('nan')))
print('used blocks', min(used), max(used), len(used))
# S1/S2
xs = [p['dt_us'] for p in pairs]
m = statistics.mean(xs); se = statistics.stdev(xs) / math.sqrt(len(xs))
print('S1 (<= -100):', m <= -100, 'S2 (m+2SE<0):', m + 2 * se < 0)
# dt quantisation: distribution of dt per arm
for arm in (0, 1):
    vals = [main[n]['dt_us'] for b in used if means[b]['arm'] == arm for n in B[b]]
    buckets = Counter(int(round(v / 16667.0)) for v in vals)
    print('arm', arm, 'n', len(vals), 'vblank buckets', sorted(buckets.items()), 'mean', statistics.mean(vals))
