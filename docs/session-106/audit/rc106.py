"""Independent recount for session 106 (auditor). No session scorer imported.
python rc106.py <log> <mode: gw|dab|dwk> [--out json]
Convention: GateArm block b -> FrameTrace n in 1801+90b .. 1890+90b; kept idx 60..88; a block whose
first kept frame < 2100 rejected; pairs only in complete quartets 4q..4q+3: (4q,4q+1), (4q+2,4q+3);
per block mean over kept rows; per pair arm1 - arm0.
"""
import json
import math
import re
import statistics
import sys

LOG = sys.argv[1]
MODE = sys.argv[2]
OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None

GA = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
KV = re.compile(rb'([A-Za-z0-9_]+)=(-?\d+)')

WANT_MAIN = {b'dt_us', b'cpu_gpu_us', b'arm', b'blk', b'draws', b'dispatches', b'gpu_busy_us', b'submits'}
WANT_DRAW = {b'spin_gpu_us', b'da_queue_us', b'da_miss', b'da_take_us', b'da_walk_us', b'da_late', b'da_hit'}
WANT_X = {b'pl_prog_wait_us', b'pl_pipe_wait_us', b'pl_cs_wait_us', b'pl_prog_n', b'pl_pipe_n', b'pl_cs_n',
          b'gw_idle_ns', b'gw_blk_ns', b'gw_flip_ns', b'gw_proc_ns', b'gw_cmd_ns', b'gw_idle_n', b'gw_blk_n',
          b'gw_flip_n', b'gw_proc_n', b'gw_cmd_n', b'da_qcall', b'da_wjobs', b'da_wskip', b'da_wdrop',
          b'pl_prog_hold_us', b'pl_pipe_hold_us', b'pl_cs_hold_us', b'rec_spin_gpu_us', b'prot_spin_gpu_us'}

gate = []
rows = {}
dups = {'main': 0, 'draw': 0, 'x': 0}
markers = {'skipped_draw': 0, 'hangabort': 0, 'checkpoint': 0, 'error': 0, 'pin': 0, 'gpuwall': 0,
           'rec_started': 0}
pin_lines = []


def parse(line, want):
    d = {}
    for k, v in KV.findall(line):
        if k in want or k == b'n':
            if k not in d:
                d[k] = int(v)
    return d


with open(LOG, 'rb') as f:
    for line in f:
        line = line.rstrip(b'\r\n')
        if line.startswith(b'GateArm:'):
            m = GA.match(line)
            gate.append(tuple(int(x) for x in m.groups()[:6]) + (m.group(7).decode(),))
        elif line.startswith(b'FrameTrace: '):
            d = parse(line, WANT_MAIN)
            n = d[b'n']
            r = rows.setdefault(n, {})
            if 'dt_us' in r:
                dups['main'] += 1
            r.update({k.decode(): v for k, v in d.items() if k != b'n'})
        elif line.startswith(b'FrameTrace-draw:'):
            d = parse(line, WANT_DRAW)
            n = d[b'n']
            r = rows.setdefault(n, {})
            if 'spin_gpu_us' in r:
                dups['draw'] += 1
            r.update({k.decode(): v for k, v in d.items() if k != b'n'})
        elif line.startswith(b'FrameTrace-x:'):
            d = parse(line, WANT_X)
            n = d[b'n']
            r = rows.setdefault(n, {})
            if '_x' in r:
                dups['x'] += 1
            r['_x'] = 1
            r.update({k.decode(): v for k, v in d.items() if k != b'n'})
        else:
            if b'AsyncPipelines: skipped draw' in line:
                markers['skipped_draw'] += 1
            if b'GpuHangAbort' in line:
                markers['hangabort'] += 1
            if b'GpuCheckpoint' in line or b'GPU checkpoints' in line:
                markers['checkpoint'] += 1
            if line.startswith(b'GpuClockPin:'):
                markers['pin'] += 1
                pin_lines.append(line[:80].decode(errors='replace'))
            if line.startswith(b'GpuWall:'):
                markers['gpuwall'] += 1
            if line.startswith(b'RecordThread: started'):
                markers['rec_started'] += 1
            if b'--- Error ---' in line or b'--- Fatal Error ---' in line or b'std::terminate' in line:
                markers['error'] += 1

# gate sanity
arms = {}
gate_ok = True
for g in gate:
    arm, narms, block, frame, period, abba, text = g
    exp_arm = (0, 1, 1, 0)[block % 4]
    if narms != 2 or period != 90 or abba != 1 or frame != 1800 + 90 * block or arm != exp_arm:
        gate_ok = False
    arms[block] = (arm, text)
texts = {}
for b, (a, t) in arms.items():
    texts.setdefault(a, set()).add(t)

# row arm cross-check
arm_mismatch = 0
eligible = {}
for b in sorted(arms):
    exp = list(range(1801 + 90 * b, 1891 + 90 * b))
    if not all(n in rows and 'dt_us' in rows[n] and 'spin_gpu_us' in rows[n] and '_x' in rows[n] for n in exp):
        continue
    kept = exp[60:89]
    if kept[0] < 2100:
        continue
    for n in kept:
        if rows[n].get('arm') != arms[b][0] or rows[n].get('blk') != b:
            arm_mismatch += 1
    eligible[b] = kept
pairs = []
top = max(arms)
for q in range(0, top + 1, 4):
    quart = [q, q + 1, q + 2, q + 3]
    if all(k in eligible for k in quart):
        pairs.append((q, q + 1))
        pairs.append((q + 3, q + 2))  # (arm0 block, arm1 block)


def val(r, key):
    if key == 'cpu_net_us':
        return r['cpu_gpu_us'] - r['spin_gpu_us']
    if key == 'lock_us':
        return r['pl_prog_wait_us'] + r['pl_pipe_wait_us'] + r['pl_cs_wait_us']
    if key.endswith('_nsus'):
        return r[key[:-5] + '_ns'] / 1000.0
    if key == 'D_us':
        return r['dt_us'] - (r['cpu_gpu_us'] - r['spin_gpu_us'])
    if key == 'R_us':
        D = r['dt_us'] - (r['cpu_gpu_us'] - r['spin_gpu_us'])
        return (D - r['gw_idle_ns'] / 1000.0 - r['gw_blk_ns'] / 1000.0 - r['gw_flip_ns'] / 1000.0
                - (r['pl_prog_wait_us'] + r['pl_pipe_wait_us'] + r['pl_cs_wait_us']))
    if key == 'uncov_us':
        return (r['dt_us'] - (r['gw_idle_ns'] + r['gw_blk_ns'] + r['gw_proc_ns'] + r['gw_cmd_ns']) / 1000.0)
    return r[key]


def bmean(b, key):
    return statistics.fmean(val(rows[n], key) for n in eligible[b])


def stat(key):
    try:
        ds = [bmean(b1, key) - bmean(b0, key) for b0, b1 in pairs]
    except KeyError:
        return None
    m = statistics.fmean(ds)
    sd = statistics.stdev(ds)
    se = sd / math.sqrt(len(ds))
    t = m / se if se > 0 else float('inf')
    s = sorted(ds)
    k = max(1, len(s) // 10)
    trim = statistics.fmean(s[k:-k])
    return {'mean': m, 'se': se, 'two_se': 2 * se, 't': t, 'n': len(ds), 'median': statistics.median(ds),
            'trim10': trim, 'neg': sum(1 for d in ds if d < 0), 'min': s[0], 'max': s[-1]}


def level(key, arm):
    try:
        bs = [b for p in pairs for b in p if arms[b][0] == arm]
        vals = [bmean(b, key) for b in bs]
    except KeyError:
        return None
    return {'mean': statistics.fmean(vals), 'median': statistics.median(vals)}


keys = ['dt_us', 'cpu_net_us', 'cpu_gpu_us', 'spin_gpu_us', 'D_us', 'draws', 'gpu_busy_us', 'da_queue_us',
        'da_miss', 'da_take_us', 'da_walk_us', 'da_late', 'submits']
if MODE == 'gw':
    keys += ['lock_us', 'pl_prog_wait_us', 'pl_pipe_wait_us', 'pl_cs_wait_us', 'pl_prog_n', 'pl_pipe_n', 'pl_cs_n',
             'gw_idle_nsus', 'gw_blk_nsus', 'gw_flip_nsus', 'gw_proc_nsus', 'gw_cmd_nsus', 'R_us', 'uncov_us',
             'gw_proc_n', 'da_qcall', 'rec_spin_gpu_us', 'prot_spin_gpu_us']
if MODE == 'dab':
    keys += ['da_qcall']
if MODE == 'dwk':
    keys += ['rec_spin_gpu_us', 'prot_spin_gpu_us']
res = {'log': LOG, 'gate_lines': len(gate), 'gate_ok': gate_ok, 'texts': {a: sorted(t) for a, t in texts.items()},
       'dups': dups, 'markers': markers, 'pin_lines': pin_lines[:3], 'arm_mismatch_rows': arm_mismatch,
       'eligible_blocks': len(eligible), 'pairs': len(pairs), 'paired_blocks': sorted({b for p in pairs for b in p}),
       'stats': {}, 'levels': {}}
for k in keys:
    s = stat(k)
    if s is None:
        continue
    res['stats'][k] = s
    res['levels'][k] = {0: level(k, 0), 1: level(k, 1)}

print('log', LOG, 'GateArm lines', len(gate), 'gate_ok', gate_ok, 'arm/blk row mismatches', arm_mismatch)
print('texts', res['texts'])
print('dups', dups, 'markers', markers, pin_lines[:2])
pb = res['paired_blocks']
print('eligible blocks', len(eligible), 'pairs', len(pairs), 'paired blocks', pb[0], '..', pb[-1], len(pb))
for k in keys:
    s = res['stats'].get(k)
    if s is None:
        print('%-18s n/a' % k)
        continue
    l0, l1 = res['levels'][k][0], res['levels'][k][1]
    print('%-18s d mean %9.2f 2SE %7.2f t %7.2f | med %8.2f trim10 %8.2f neg %2d/%d | lvl mean %9.1f -> %9.1f  med %9.1f -> %9.1f'
          % (k, s['mean'], s['two_se'], s['t'], s['median'], s['trim10'], s['neg'], s['n'],
             l0['mean'], l1['mean'], l0['median'], l1['median']))
if MODE == 'gw':
    D = res['stats']['D_us']
    print('R0 D reproduced (mean-2SE>0):', D['mean'] - D['two_se'] > 0)
    for k in ['gw_idle_nsus', 'gw_blk_nsus', 'gw_flip_nsus', 'lock_us', 'R_us']:
        s = res['stats'][k]
        print('  NAMED check %-14s mean %8.2f >= D/2 %.2f : %s ; t %.2f >= 3 : %s' % (
            k, s['mean'], D['mean'] / 2, s['mean'] >= D['mean'] / 2, s['t'], s['t'] >= 3))
if MODE == 'dab':
    dt = res['stats']['dt_us']
    print('S1 mean ddt <= -100:', dt['mean'] <= -100, ' S2 mean+2SE<0:', dt['mean'] + dt['two_se'] < 0)
    q = res['levels']['da_qcall']
    print('da_qcall ratio (mean lvl) %.3f (median lvl) %.3f' % (q[1]['mean'] / q[0]['mean'], q[1]['median'] / q[0]['median']))
if OUT:
    json.dump(res, open(OUT, 'w'), indent=1, default=str)
