"""Independent recount of spn117 (audit lens RECOUNT). Uses parsed117.pkl from parse117.py (own parser).
Does not import spn117.py."""
import pickle, statistics, math, collections, json

D = pickle.load(open('C:/kyty/s117/audit117/recount/parsed117.pkl', 'rb'))
S = D['streams']
MAIN, DRAW, X = S['main'], S['draw'], S['x']
START = 1800
PERIOD = 90
SPINE = ['spine_n', 'spine_ns', 'spine_pk', 'spine_el', 'spine_ib', 'spine_cf_br', 'spine_cf_cond', 'spine_cf_pred',
         'spine_cf_predw', 'spine_cf_ind', 'spine_abort', 'spine_cmp', 'spine_bad', 'spine_misal', 'spine_pad',
         'spine_lost', 'spine_chk_ns', 'cram_write']
res = {}


def arm_of_block(b):
    return 0 if b % 4 in (0, 3) else 1


def pct(v, q):
    v = sorted(v)
    if not v:
        return float('nan')
    k = (len(v) - 1) * q
    f = math.floor(k); c = math.ceil(k)
    return v[f] if f == c else v[f] + (v[c] - v[f]) * (k - f)


# ---------- stream integrity
for name, st in (('main', MAIN), ('draw', DRAW), ('x', X)):
    ns = sorted(k for k in st if k is not None)
    dups = [k for k in ns if len(st[k]) > 1]
    print(f'{name}: frames {len(ns)} min {ns[0]} max {ns[-1]} dups {len(dups)} {dups[:10]}')
    gaps = [(a, b) for a, b in zip(ns, ns[1:]) if b != a + 1]
    print(f'   gaps {len(gaps)} {gaps[:10]}')
    res[f'{name}_frames'] = len(ns); res[f'{name}_dups'] = len(dups); res[f'{name}_gaps'] = gaps[:20]
    o = D['order'][name]
    nonmono = sum(1 for a, b in zip(o, o[1:]) if b is not None and a is not None and b < a)
    print(f'   order non-monotone steps {nonmono}')

# ---------- field presence on x lines
missing = collections.Counter()
for n, lst in X.items():
    if n is None or n <= START:
        continue
    for d in lst:
        for k in SPINE:
            if k not in d:
                missing[k] += 1
print('x lines after 1800 missing spine fields:', dict(missing))
res['x_missing_fields'] = dict(missing)
# any spine field before 1800 non-zero?
pre = collections.Counter()
for n, lst in X.items():
    if n is None or n > START:
        continue
    for d in lst:
        for k in SPINE:
            if d.get(k, 0):
                pre[k] += d[k]
print('spine fields non-zero before/at 1800:', dict(pre))
res['pre1800_nonzero'] = dict(pre)

# ---------- arm/blk on main line vs frame arithmetic
bad_armblk = []
for n, lst in MAIN.items():
    if n is None or n <= START:
        continue
    b = (n - START - 1) // PERIOD
    for d in lst:
        if d.get('blk') != b or d.get('arm') != arm_of_block(b):
            bad_armblk.append((n, d.get('arm'), d.get('blk'), arm_of_block(b), b))
print('main lines n>1800 whose arm=/blk= disagree with (n-1801)//90 and ABBA:', len(bad_armblk), bad_armblk[:10])
res['armblk_mismatch'] = len(bad_armblk)
# also frames <=1800 arm/blk values
pre_ab = collections.Counter((d.get('arm'), d.get('blk')) for n, lst in MAIN.items() if n is not None and n <= START
                             for d in lst)
print('arm/blk on frames <= 1800:', pre_ab.most_common(5))

# ---------- GateArm / Gate lines
gatearm = [o for o in D['other'] if o[1] == 'GateArm:']
gate = [o for o in D['other'] if o[1] == 'Gate:']
import re
ga_ok = True; ga = []
for i, _, ln in gatearm:
    m = re.fullmatch(rb'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(\S+)\r?\n?', ln)
    if not m:
        ga_ok = False; print('malformed GateArm', ln); continue
    arm, arms, blk, fr, per, abba, txt = m.groups()
    arm, arms, blk, fr, per, abba = map(int, (arm, arms, blk, fr, per, abba))
    exp_txt = b'spine=1' if arm == 0 else b'spine=2'
    if not (arms == 2 and per == 90 and abba == 1 and fr == START + PERIOD * blk and arm == arm_of_block(blk)
            and txt == exp_txt):
        ga_ok = False; print('bad GateArm', ln)
    ga.append((blk, arm, fr, i))
blks = [g[0] for g in ga]
print('GateArm lines', len(ga), 'blocks', blks[0], '..', blks[-1], 'consecutive', blks == list(range(len(blks))),
      'all ok', ga_ok)
res['gatearm_n'] = len(ga); res['gatearm_ok'] = ga_ok and blks == list(range(len(blks)))
g_ok = True; gl = []
for i, _, ln in gate:
    m = re.fullmatch(rb'Gate: (\w+)=(\d+) frame=(\d+)\r?\n?', ln)
    if not m:
        g_ok = False; print('malformed Gate', ln); continue
    name, v, fr = m.group(1), int(m.group(2)), int(m.group(3))
    if name != b'spine' or (fr - START) % PERIOD != 0:
        g_ok = False; print('bad Gate', ln); continue
    b = (fr - START) // PERIOD
    if v != (1 if arm_of_block(b) == 0 else 2):
        g_ok = False; print('Gate value wrong', ln)
    gl.append(b)
exp_changes = [0] + [b for b in range(1, len(ga)) if arm_of_block(b) != arm_of_block(b - 1)]
print('Gate lines', len(gl), 'expected change blocks', len(exp_changes), 'match', gl == exp_changes, 'ok', g_ok)
res['gate_n'] = len(gl); res['gate_ok'] = g_ok and gl == exp_changes
# GateArm line position vs FrameTrace line: which FrameTrace main precedes each GateArm?
spine_lines = [o for o in D['other'] if o[1] == 'Spine']
print('Spine lines:', [(o[0], o[2]) for o in spine_lines])
pins = [o for o in D['other'] if o[1] == 'GpuClockPin']
print('GpuClockPin lines:', [(o[0], o[2]) for o in pins])
print('markers log', D['markers'][:5], 'stdout', D['stdout_markers'][:5])

# ---------- blocks
nblocks = len(ga)
blocks = {}
for b in range(nblocks):
    frames = list(range(START + 1 + PERIOD * b, START + 1 + PERIOD * (b + 1)))
    complete_main = all(f in MAIN for f in frames)
    complete_all = all(f in MAIN and f in DRAW and f in X for f in frames)
    single = all(len(MAIN.get(f, [])) == 1 and len(X.get(f, [])) == 1 and len(DRAW.get(f, [])) == 1 for f in frames)
    blocks[b] = dict(arm=arm_of_block(b), complete_main=complete_main, complete_all=complete_all, single=single,
                     frames=frames)
cb = collections.Counter((v['arm'], v['complete_all']) for v in blocks.values())
print('blocks by (arm, complete_all):', dict(cb))
res['complete_blocks'] = {a: sum(1 for v in blocks.values() if v['arm'] == a and v['complete_all']) for a in (0, 1)}
inc = [b for b, v in blocks.items() if not v['complete_all']]
print('incomplete blocks', inc, [(min(f for f in blocks[b]['frames'] if f in MAIN) if any(f in MAIN for f in blocks[b]['frames']) else None,
                                   max((f for f in blocks[b]['frames'] if f in MAIN), default=None)) for b in inc])

# ---------- K5 over every x line after 1800
k5 = collections.Counter()
xl = 0
for n, lst in X.items():
    if n is None or n <= START:
        continue
    for d in lst:
        xl += 1
        for k in SPINE:
            k5[k] += d.get(k, 0)
print('x lines after 1800:', xl)
print('sums over every x line n>1800:', dict(k5))
res['k5_sums_all_x'] = dict(k5); res['x_lines_after_1800'] = xl
# log lines SpineMismatch/SpineMisalign
smm = 0; sma = 0
with open('C:/kyty/s117/log_spn117.txt', 'rb') as f:
    for ln in f:
        if b'SpineMismatch' in ln:
            smm += 1
        if b'SpineMisalign' in ln:
            sma += 1
print('SpineMismatch lines', smm, 'SpineMisalign lines', sma)
res['SpineMismatch_lines'] = smm; res['SpineMisalign_lines'] = sma


# ---------- kept frames per arm
def row(n):
    m = MAIN[n][0]; d = DRAW[n][0]; x = X[n][0]
    r = dict(n=n, dt_us=m['dt_us'], cpu_gpu_us=m['cpu_gpu_us'], draws=m['draws'], dispatches=m['dispatches'],
             da_walk_us=d['da_walk_us'], da_queue_us=d.get('da_queue_us'))
    for k in SPINE:
        r[k] = x[k]
    return r


kept = {0: [], 1: []}
for b, v in blocks.items():
    if not v['complete_all']:
        continue
    for i, f in enumerate(v['frames']):
        if 10 <= i <= 89:
            kept[v['arm']].append(row(f))
means = {}
for a in (0, 1):
    rows = kept[a]
    mm = {k: statistics.fmean(r[k] for r in rows) for k in rows[0] if k != 'n'}
    mm['spine_us'] = mm['spine_ns'] / 1000
    mm['el_over_ops'] = sum(r['spine_el'] for r in rows) / sum(r['draws'] + r['dispatches'] for r in rows)
    mm['cmp_over_el'] = sum(r['spine_cmp'] for r in rows) / sum(r['spine_el'] for r in rows)
    mm['pk_per_plan'] = sum(r['spine_pk'] for r in rows) / sum(r['spine_n'] for r in rows)
    mm['kept_frames'] = len(rows)
    means[a] = mm
    print(f'arm {a}: kept {len(rows)}')
    for k, v in mm.items():
        print(f'   {k} = {v:.4f}')
res['means'] = means

# K1
a0 = kept[0]
k1 = statistics.fmean(r['spine_ns'] for r in a0) / 1000
walker_need = statistics.fmean(r['da_walk_us'] + r['spine_ns'] / 1000 for r in a0)
frame_nospine = statistics.fmean(r['dt_us'] - r['spine_ns'] / 1000 for r in a0)
print(f'K1 spine_us arm0 kept = {k1:.3f}; walker need {walker_need:.3f} vs frame without spine {frame_nospine:.3f} '
      f'(fit {walker_need < frame_nospine})')
res['k1_us'] = k1; res['walker_need'] = walker_need; res['frame_nospine'] = frame_nospine
# K5 ratio over arm1 kept
cmp1 = sum(r['spine_cmp'] for r in kept[1]); el1 = sum(r['spine_el'] for r in kept[1])
print(f'arm1 kept cmp {cmp1} el {el1} ratio {cmp1 / el1:.6f}')
res['cmp1'] = cmp1; res['el1'] = el1

# complete frames > 1800 (all three streams)
cf = [n for n in MAIN if n is not None and n > START and n in X and n in DRAW]
tot = collections.Counter()
for n in cf:
    for k in SPINE:
        tot[k] += X[n][0][k]
print('frames >1800 with all three lines:', len(cf), 'sums:', dict(tot))
res['complete_frames'] = len(cf); res['complete_frame_sums'] = dict(tot)

# distribution of spine_ns in arm 0 kept
v = [r['spine_ns'] / 1000 for r in a0]
dist = dict(mean=statistics.fmean(v), median=statistics.median(v), p10=pct(v, .1), p90=pct(v, .9), p99=pct(v, .99),
            max=max(v), min=min(v), sd=statistics.pstdev(v))
top = sorted(a0, key=lambda r: -r['spine_ns'])[:10]
share_top1pct = sum(sorted(v, reverse=True)[:len(v) // 100]) / sum(v)
print('arm0 kept spine_us distribution:', {k: round(x, 2) for k, x in dist.items()}, 'top1% share', round(share_top1pct, 4))
print('   top frames:', [(r['n'], round(r['spine_ns'] / 1000, 1), r['spine_n'], r['spine_el']) for r in top])
res['arm0_spine_us_dist'] = dist; res['arm0_top1pct_share'] = share_top1pct
# per-block means arm0 spine_us
pb = collections.defaultdict(list)
for b, vv in blocks.items():
    if vv['complete_all'] and vv['arm'] == 0:
        pb[b] = statistics.fmean(X[f][0]['spine_ns'] / 1000 for f in vv['frames'][10:90])
print('arm0 per-block spine_us: min', round(min(pb.values()), 1), 'max', round(max(pb.values()), 1),
      'median', round(statistics.median(pb.values()), 1))
res['arm0_block_spine_us_range'] = (min(pb.values()), max(pb.values()), statistics.median(pb.values()))
# per-frame spine per element / per packet
per_el = [r['spine_ns'] / r['spine_el'] for r in a0 if r['spine_el']]
print('arm0 ns per element median', round(statistics.median(per_el), 1), 'p99', round(pct(per_el, .99), 1))
# arm1 distributions
v1 = [r['spine_ns'] / 1000 for r in kept[1]]
c1 = [r['spine_chk_ns'] / 1000 for r in kept[1]]
print('arm1 spine_us median', round(statistics.median(v1), 1), 'p99', round(pct(v1, .99), 1), 'chk_us median',
      round(statistics.median(c1), 1), 'p99', round(pct(c1, .99), 1))
# dt distributions
for a in (0, 1):
    dt = [r['dt_us'] for r in kept[a]]
    print(f'arm{a} dt mean {statistics.fmean(dt):.1f} median {statistics.median(dt):.1f} p99 {pct(dt, .99):.1f}')
# block-paired dt difference (ABBA pairs: blocks (4k,4k+1,4k+2,4k+3))
bm = {b: statistics.fmean(MAIN[f][0]['dt_us'] for f in vv['frames'][10:90]) for b, vv in blocks.items()
      if vv['complete_all']}
diffs = []
for q in range(0, nblocks, 4):
    bs = [q, q + 1, q + 2, q + 3]
    if all(b in bm for b in bs):
        diffs.append((bm[q + 1] + bm[q + 2]) / 2 - (bm[q] + bm[q + 3]) / 2)
md = statistics.fmean(diffs); se = statistics.stdev(diffs) / math.sqrt(len(diffs))
print(f'ABBA quads {len(diffs)}: dt(arm1) - dt(arm0) = {md:.1f} +- {2 * se:.1f} (2SE)')
res['abba_dt_diff'] = (md, 2 * se, len(diffs))
# spine_n per frame values
cn = collections.Counter(r['spine_n'] for r in a0)
print('arm0 spine_n per-frame values', cn.most_common(6))
ci = collections.Counter(r['spine_cf_ind'] for r in a0 + kept[1])
print('spine_cf_ind per-frame values (both arms kept)', ci.most_common(6))
# arm0 cmp non-zero frames
nz = [(r['n'], r['spine_cmp'], r['spine_chk_ns']) for r in a0 if r['spine_cmp'] or r['spine_chk_ns']]
print('arm0 kept frames with cmp/chk non-zero:', len(nz), nz[:20])
res['arm0_cmp_frames'] = nz
# arm1: frames where cmp != el
d1 = [(r['n'], r['spine_el'], r['spine_cmp']) for r in kept[1] if r['spine_cmp'] != r['spine_el']]
print('arm1 kept frames with cmp != el:', len(d1), d1[:15])
# where excess of cmp over el sits by index within block
idx_ex = collections.Counter()
for b, vv in blocks.items():
    if vv['complete_all'] and vv['arm'] == 1:
        for i, f in enumerate(vv['frames']):
            x = X[f][0]
            idx_ex[i] += x['spine_cmp'] - x['spine_el']
print('arm1 cmp-el by in-block index (non-zero):', {k: v for k, v in sorted(idx_ex.items()) if v})
json.dump(res, open('C:/kyty/s117/audit117/recount/recount117.json', 'w'), indent=1, default=str)
