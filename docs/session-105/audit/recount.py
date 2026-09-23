"""Independent recount (audit 105). Does not import any session scorer.
usage: python recount.py <tag> [--root C:/kyty/s105]
Blocks are taken from the `blk=` field of the main FrameTrace line (not from frame arithmetic),
cross-checked against GateArm lines; kept rows = positions 60..88 of each 90-row block, n >= 2100;
pairs = (4k,4k+1),(4k+2,4k+3) from complete quartets; delta = arm1 block mean - arm0 block mean.
"""
import re, sys, json, math, statistics, collections

root = 'C:/kyty/s105'
tag = sys.argv[1]
if '--root' in sys.argv:
    root = sys.argv[sys.argv.index('--root') + 1]
log = '%s/log_%s.txt' % (root, tag)
stdout = '%s/stdout_%s.txt' % (root, tag)

TOK = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')
main, draw, x = {}, {}, {}
gate = []
markers = collections.Counter()
order = []
MARK = [b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---',
        b'ErrorDeviceLost', b'Unhandled exception:', b'GpuWaitSlow:', b'GpuHangAbort',
        b'AsyncPipelines: skipped draw', b'GpuClockPin: mode', b'RecordThread: started',
        b'GPU checkpoints', b'CtxCheck', b'Recording:']
def scan(line):
    for m in MARK:
        if m in line:
            markers[m.decode()] += 1
    if b'GpuClockPin: mode' in line:
        markers['PIN:' + line.strip()[-40:].decode('utf-8', 'replace')] += 1

with open(log, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace: '):
            d = {k.decode(): int(v) for k, v in TOK.findall(line)}
            main[d['n']] = d; order.append(d['n'])
        elif line.startswith(b'FrameTrace-draw: '):
            d = {k.decode(): int(v) for k, v in TOK.findall(line)}
            draw[d['n']] = d
        elif line.startswith(b'FrameTrace-x: '):
            d = {k.decode(): int(v) for k, v in TOK.findall(line)}
            x[d['n']] = d
        elif line.startswith(b'GateArm:'):
            m = re.match(rb'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)', line.rstrip())
            gate.append(tuple(int(v) for v in m.groups()[:6]) + (m.group(7).decode(),))
        else:
            scan(line)
try:
    with open(stdout, 'rb') as f:
        for line in f:
            scan(line)
except OSError:
    pass

out = {'tag': tag, 'main_rows': len(main), 'draw_rows': len(draw), 'x_rows': len(x),
       'gatearm_lines': len(gate), 'markers': dict(markers)}
out['contiguous'] = order == list(range(min(order), max(order) + 1)) if order else None
# gate consistency
garm = {}
gate_ok = True
for i, (arm, arms, block, frame, period, abba, text) in enumerate(gate):
    garm[block] = (arm, text)
    if block != i or arm != (0, 1, 1, 0)[i % 4] or abba != 1 or arms != 2:
        gate_ok = False
out['gate_abba_ok'] = gate_ok
out['arm_texts'] = sorted({t for a, t in garm.values()}) if garm else []

def row(n):
    r = dict(main[n]); r.update({'d_' + k: v for k, v in draw.get(n, {}).items()})
    r.update({'x_' + k: v for k, v in x.get(n, {}).items()})
    r['cpu_net'] = r['cpu_gpu_us'] - r['d_spin_gpu_us']
    return r

if gate:
    byblk = collections.defaultdict(list)
    for n, d in main.items():
        if 'blk' in d and n in draw and n in x:
            byblk[d['blk']].append(n)
    kept = {}
    arm_mismatch = 0
    for b, ns in byblk.items():
        ns.sort()
        if len(ns) != 90 or ns != list(range(ns[0], ns[0] + 90)):
            continue
        k = ns[60:89]
        if min(k) < 2100:
            continue
        if b not in garm:
            continue
        for n in ns:
            if main[n]['arm'] != garm[b][0]:
                arm_mismatch += 1
        kept[b] = k
    out['arm_mismatch_rows'] = arm_mismatch
    pairs = []
    top = max(kept) if kept else -1
    for q in range(0, top + 1, 4):
        if all(q + i in kept for i in range(4)):
            pairs += [(q, q + 1), (q + 2, q + 3)]
    out['pairs'] = len(pairs)
    out['orient'] = [sum(garm[p[0]][0] == a for p in pairs) for a in (0, 1)]
    keys = ['dt_us', 'cpu_net', 'cpu_gpu_us', 'draws', 'gpu_busy_us', 'd_da_late', 'd_da_miss',
            'd_da_take_us', 'd_da_hit', 'd_rec_n', 'd_spin_gpu_us', 'd_da_walk_us']
    def bm(b, k):
        return statistics.fmean(row(n)[k] for n in kept[b])
    res = {}
    for k in keys:
        ds = []
        for l, r in pairs:
            a0, a1 = (l, r) if garm[l][0] == 0 else (r, l)
            ds.append(bm(a1, k) - bm(a0, k))
        m = statistics.fmean(ds); sd = statistics.stdev(ds); se = sd / math.sqrt(len(ds))
        res[k] = {'mean': round(m, 2), '2se': round(2 * se, 2), 't': round(m / se, 3), 'sd': round(sd, 1),
                  'median': round(statistics.median(ds), 2)}
    out['delta'] = res
    # sensitivity: all 90 rows per block, same pairs
    def bm90(b, k):
        ns = sorted(byblk[b])
        return statistics.fmean(row(n)[k] for n in ns)
    sens = {}
    for k in ('dt_us', 'cpu_net'):
        ds = []
        for l, r in pairs:
            a0, a1 = (l, r) if garm[l][0] == 0 else (r, l)
            ds.append(bm90(a1, k) - bm90(a0, k))
        m = statistics.fmean(ds); se = statistics.stdev(ds) / math.sqrt(len(ds))
        sens[k] = {'mean': round(m, 2), '2se': round(2 * se, 2)}
    out['delta_all90rows'] = sens
    # work split over kept rows
    dr = {a: [row(n)['draws'] for b, k in kept.items() for n in k if garm[b][0] == a and any(b in p for p in pairs)] for a in (0, 1)}
    out['work_split_pct'] = round(100 * (statistics.fmean(dr[1]) / statistics.fmean(dr[0]) - 1), 4)
    # dark keys over all x lines by arm (whole run) and kept rows
    dark = ['mw_n', 'a_hold_us', 'a_mut_us', 'pl_em_n', 'pl_proc_n', 'sh_jobs', 'ctx_chk_n', 'ctx_chk_bad',
            'ctx_midsub', 'ctx_rec_block', 'bf_n', 'gm_ops']
    tot = {k: collections.Counter() for k in dark}
    present = collections.Counter()
    for n, d in x.items():
        a = main.get(n, {}).get('arm', -1)
        for k in dark:
            if k in d:
                present[k] += 1; tot[k][a] += d[k]
    out['dark_present'] = dict(present)
    out['dark_totals_by_arm'] = {k: dict(v) for k, v in tot.items()}
    # walk arming per arm on kept rows
    for a in (0, 1):
        ns = [n for b, k in kept.items() for n in k if garm[b][0] == a and any(b in p for p in pairs)]
        sk = sum(x[n].get('da_wskip', 0) for n in ns); jb = sum(x[n].get('da_wjobs', 0) for n in ns)
        dp = sum(x[n].get('da_wdrop', 0) for n in ns)
        out['walk_arm%d' % a] = {'skip': sk, 'jobs': jb, 'drop': dp,
                                  'walks_per_flip': round(statistics.fmean(draw[n].get('da_walks', 0) for n in ns), 3)}
print(json.dumps(out, indent=1))
