"""Session 106, EXPLORATORY (not a sealed test): per-arm contrast of every numeric field of the
session-104 ABBA run dwk104 (dawalk=0|1, pinned), to find where the +196 us of GuestGpu wall time that
is not GuestGpu CPU goes.  Blocks from blk= (arm from arm=), rows idx 60..88 of each 90-row block
(the sealed convention), quartets ABBA/BAAB -> diff = mean(arm1) - mean(arm0).

    python C:/kyty/s105/explore106_dwk104.py [log] [--top N]
"""
import math
import re
import statistics
import sys

LOG = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'C:/kyty/s104/log_dwk104.txt'
TOP = int(sys.argv[sys.argv.index('--top') + 1]) if '--top' in sys.argv else 60
MAIN = re.compile(rb'^FrameTrace: n=(\d+)')
SUB = re.compile(rb'^(FrameTrace-draw|FrameTrace-x): n=(\d+)')
TAB = re.compile(rb'^(FrameTrace-wait|FrameTrace-submit|FrameTrace-pops|FrameTrace-direct):')
FIELD = re.compile(rb'(\w+)=(-?\d+)')
SITE = re.compile(rb' ([^ =]+)=(\d+)/(\d+)')

rows = {}
last_n = None
with open(LOG, 'rb') as f:
    for line in f:
        m = MAIN.match(line)
        if m:
            n = int(m.group(1))
            d = rows.setdefault(n, {})
            for k, v in FIELD.findall(line[m.end():]):
                d[k.decode()] = int(v)
            last_n = n
            continue
        m = SUB.match(line)
        if m:
            n = int(m.group(2))
            pre = 'd.' if m.group(1) == b'FrameTrace-draw' else 'x.'
            d = rows.setdefault(n, {})
            for k, v in FIELD.findall(line[m.end():]):
                d[pre + k.decode()] = int(v)
            continue
        m = TAB.match(line)
        if m and last_n is not None:
            pre = {b'FrameTrace-wait': 'w.', b'FrameTrace-submit': 's.', b'FrameTrace-pops': 'p.', b'FrameTrace-direct': 'r.'}[m.group(1)]
            d = rows.setdefault(last_n, {})
            for k, us, c in SITE.findall(line[m.end():]):
                d[pre + k.decode() + '_us'] = d.get(pre + k.decode() + '_us', 0) + int(us)
                d[pre + k.decode() + '_n'] = d.get(pre + k.decode() + '_n', 0) + int(c)

# blocks: the dwk104.py convention - block b = frames 1801+90b .. 1890+90b, arm from GateArm,
# kept idx 60..88, a block with a kept frame below 2100 rejected, complete quartets only
gate = {}
with open(LOG, 'rb') as f:
    for line in f:
        m = re.match(rb'^GateArm: arm=(\d+) arms=\d+ block=(\d+) ', line)
        if m:
            gate[int(m.group(2))] = int(m.group(1))
keys = set()
for d in rows.values():
    keys.update(d.keys())
keys -= {'n', 'arm', 'blk'}
bmeans = {}
for b, arm in gate.items():
    exp = list(range(1801 + 90 * b, 1891 + 90 * b))
    if not all(n in rows for n in exp):
        continue
    sel = [rows[n] for n in exp[60:89]]
    if exp[60] < 2100:
        continue
    bmeans[b] = (arm, {k: statistics.mean(x.get(k, 0) for x in sel) for k in keys})
bs = sorted(bmeans)
quart = []
for q in range(min(bs) // 4, max(bs) // 4 + 1):
    ids = [4 * q + i for i in range(4)]
    if not all(i in bmeans for i in ids):
        continue
    arms = [bmeans[i][0] for i in ids]
    if sorted(arms) != [0, 0, 1, 1]:
        continue
    quart.append(ids)
print('rows', len(rows), 'blocks', len(bmeans), 'quartets', len(quart))


def contrast(k):
    ds = []
    for ids in quart:
        a = [bmeans[i][1][k] for i in ids if bmeans[i][0] == 0]
        b = [bmeans[i][1][k] for i in ids if bmeans[i][0] == 1]
        ds.append(statistics.mean(b) - statistics.mean(a))
    m = statistics.mean(ds)
    se = statistics.stdev(ds) / math.sqrt(len(ds)) if len(ds) > 1 else float('nan')
    a0 = statistics.mean(bmeans[i][1][k] for ids in quart for i in ids if bmeans[i][0] == 0)
    return m, se, a0


res = []
for k in sorted(keys):
    m, se, a0 = contrast(k)
    t = m / se if se and se == se and se > 0 else 0.0
    res.append((k, a0, m, se, t))
wanted = ['dt_us', 'cpu_gpu_us', 'd.spin_gpu_us', 'lat_us', 'gpu_busy_us', 'semwait_gpu_us', 'fault_gpu_us',
          'x.prot_spin_gpu_us', 'x.rec_spin_gpu_us', 'x.pb_wait_gpu_us', 'd.as_lock_us', 'd.da_take_us',
          'd.da_walk_us', 'd.da_queue_us', 'd.da_work_us', 'x.da_wlag_us', 'x.da_wjobs', 'draws', 'dispatches',
          'cpu_proc_us', 'cpu_main_us', 'cpu_present_us', 'd.cpu_record_us']
print('%-28s %12s %10s %8s %7s' % ('field', 'arm0 mean', 'd(1-0)', 'SE', 't'))
by = {r[0]: r for r in res}
for k in wanted:
    if k in by:
        r = by[k]
        print('%-28s %12.1f %10.1f %8.1f %7.2f' % r)
print('--- top |t| among *_us / *_ns fields ---')
tim = [r for r in res if abs(r[4]) >= 3 and abs(r[2]) >= 0.5]
for r in sorted(tim, key=lambda r: -abs(r[4]))[:TOP]:
    print('%-28s %12.1f %10.1f %8.1f %7.2f' % r)
