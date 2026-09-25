# Independent recount of spk118 (audit 118). Own parser; does not import spk118.py.
import re, sys, json, statistics, collections

LOG = 'C:/kyty/s118/log_spk118.txt'
STDOUT = 'C:/kyty/s118/stdout_spk118.txt'
START, PERIOD = 1800, 90
KLO, KHI = 10, 89
ABBA = (0, 1, 1, 0)

kv = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')

main = collections.defaultdict(list)
draw = collections.defaultdict(list)
xl = collections.defaultdict(list)
gatearm = []
gates = []
spine_lines = []
diag = collections.Counter()
diag_examples = {}
DIAG_TOK = [b'SpineMismatch', b'SpineMisalign', b'SpineCarry', b'SpineAbort', b'SpineUncertain', b'Spine:']
MARK = [b'GpuHangAbort', b'GpuWaitSlow', b'GpuMarkerHung', b'ErrorDeviceLost', b'--- Error ---', b'--- Fatal Error ---',
        b'--- std::terminate ---', b'--- abort() ---', b'AsyncPipelines: skipped draw', b'Unhandled exception']
marks = collections.Counter()
nlines = 0
with open(LOG, 'rb') as f:
    for line in f:
        nlines += 1
        for t in DIAG_TOK:
            if t in line:
                diag[t] += 1
                diag_examples.setdefault(t, line[:300])
        for t in MARK:
            if t in line:
                marks[t] += 1
        if line.startswith(b'FrameTrace: n='):
            d = {k.decode(): int(v) for k, v in kv.findall(line)}
            main[d['n']].append(d)
        elif line.startswith(b'FrameTrace-draw: n='):
            d = {k.decode(): int(v) for k, v in kv.findall(line)}
            draw[d['n']].append(d)
        elif line.startswith(b'FrameTrace-x: n='):
            d = {k.decode(): int(v) for k, v in kv.findall(line)}
            xl[d['n']].append(d)
        elif line.startswith(b'GateArm:'):
            gatearm.append(line.rstrip(b'\r\n'))
        elif line.startswith(b'Gate:'):
            gates.append(line.rstrip(b'\r\n'))
        elif line.startswith(b'Spine: mode='):
            spine_lines.append(line.rstrip())

so_marks = collections.Counter()
so_diag = collections.Counter()
with open(STDOUT, 'rb') as f:
    for line in f:
        for t in MARK:
            if t in line: so_marks[t] += 1
        for t in DIAG_TOK:
            if t in line: so_diag[t] += 1

out = {}
out['nlines'] = nlines
out['diag_in_log'] = {k.decode(): v for k, v in diag.items()}
out['diag_examples'] = {k.decode(): v.decode('utf-8', 'replace') for k, v in diag_examples.items()}
out['markers_log'] = {k.decode(): v for k, v in marks.items()}
out['markers_stdout'] = {k.decode(): v for k, v in so_marks.items()}
out['diag_stdout'] = {k.decode(): v for k, v in so_diag.items()}
out['spine_lines'] = [s.decode() for s in spine_lines]

# duplicates
dup = {name: sum(1 for n, l in dd.items() if len(l) > 1) for name, dd in (('main', main), ('draw', draw), ('x', xl))}
out['dup_n'] = dup
out['n_range'] = {name: (min(dd), max(dd), len(dd)) for name, dd in (('main', main), ('draw', draw), ('x', xl))}
# gaps in n
def gaps(dd):
    ks = sorted(dd); g = []
    for a, b in zip(ks, ks[1:]):
        if b != a + 1: g.append((a, b))
    return g
out['gaps'] = {name: gaps(dd)[:20] for name, dd in (('main', main), ('draw', draw), ('x', xl))}

# GateArm parse
ga_re = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
ga = []
bad_ga = []
for l in gatearm:
    m = ga_re.match(l)
    if not m: bad_ga.append(l); continue
    arm, arms, blk, fr, per, abba = map(int, m.groups()[:6])
    ga.append((blk, arm, fr, m.group(7).decode()))
    if arms != 2 or per != 90 or abba != 1 or fr != START + PERIOD * blk or arm != ABBA[blk % 4]:
        bad_ga.append(l)
texts = collections.defaultdict(set)
for blk, arm, fr, t in ga: texts[arm].add(t)
out['gatearm'] = {'n': len(ga), 'bad': [b.decode() for b in bad_ga], 'blocks': (min(g[0] for g in ga), max(g[0] for g in ga)),
                  'consecutive': [g[0] for g in ga] == list(range(len(ga))), 'texts': {k: sorted(v) for k, v in texts.items()}}
arm_of_block = {blk: arm for blk, arm, fr, t in ga}

# Gate lines: check each is at a block start and value = arm's value
armvals = {}
for arm, ts in texts.items():
    t = next(iter(ts))
    armvals[arm] = dict(p.split('=') for p in t.split())
gate_re = re.compile(rb'^Gate: (\w+)=(\d+) frame=(\d+)$')
bad_gate = []
for l in gates:
    m = gate_re.match(l)
    if not m: bad_gate.append(l.decode()); continue
    name, v, fr = m.group(1).decode(), m.group(2).decode(), int(m.group(3))
    if (fr - START) % PERIOD != 0 or fr < START:
        bad_gate.append(l.decode()); continue
    b = (fr - START) // PERIOD
    a = arm_of_block.get(b)
    if a is None or armvals[a].get(name) != v:
        bad_gate.append(l.decode())
out['gate_lines'] = {'n': len(gates), 'bad': bad_gate[:10], 'nbad': len(bad_gate)}

# blocks
NEED_X = ['spine_n', 'spine_ns', 'spine_el', 'spine_abort', 'spine_cmp', 'spine_bad', 'spine_misal', 'spine_unc',
          'carry_cmp', 'carry_bad', 'carry_skip', 'cram_write', 'sc_frames', 'sc_el', 'sc_runs', 'k3_max',
          'k4_w2_n', 'k4_w2_any', 'k4_w2_dep', 'k4_w2_fmax', 'k4_w4_n', 'k4_w4_any', 'k4_w4_dep', 'k4_w4_fmax',
          'k4_nocut', 'sc_ns', 'da_t_n', 'da_t_key_us', 'da_t_prb_us', 'da_t_pfa_us', 'da_t_pfb_us', 'da_t_ver_us',
          'da_t_cpy_us', 'bl_stage_n', 'bl_prep_us', 'bl_img_us', 'bl_buf_us', 'bl_res_us', 'bl_smp_us', 'bl_sd_us',
          'bl_tr_us', 'bl_wr_us', 'bl_em_us', 'mh_pro_us', 'mh_rt_us', 'mh_prog_us', 'mh_bind_us', 'mh_emit_us',
          'mh_tail_us', 'mh_disp_us', 'mh_draws', 'pl_em_vtx_ns', 'pl_em_rt_ns', 'pl_em_pipe_ns', 'pl_em_com_ns',
          'pl_em_rec_ns', 'pl_em_rest_ns', 'pl_em_n']
missing_fields = collections.Counter()
nblocks = max(arm_of_block) + 1
complete = {}
incomplete = {}
for b in range(nblocks):
    a = arm_of_block[b]
    ok = True; why = []
    for i in range(PERIOD):
        n = START + 1 + PERIOD * b + i
        if len(main.get(n, [])) != 1 or len(draw.get(n, [])) != 1 or len(xl.get(n, [])) != 1:
            ok = False; why.append(('count', n)); break
        m = main[n][0]; x = xl[n][0]; d = draw[n][0]
        if m.get('arm') != a or m.get('blk') != b:
            ok = False; why.append(('armblk', n, m.get('arm'), m.get('blk'))); break
        for k in NEED_X:
            if k not in x: missing_fields[k] += 1; ok = False
        for k in ('bda_scan', 'da_take_us'):
            if k not in d: missing_fields['draw.' + k] += 1; ok = False
    if ok: complete[b] = a
    else: incomplete[b] = (a, why[:2])
out['blocks'] = {'n': nblocks, 'complete_P': sum(1 for a in complete.values() if a == 0),
                 'complete_M': sum(1 for a in complete.values() if a == 1), 'incomplete': {str(k): str(v) for k, v in incomplete.items()},
                 'missing_fields': dict(missing_fields)}

# arm/blk labels across ALL frames n>1800: check main arm/blk equal to the block of n
lab_bad = []
for n, ls in main.items():
    if n <= START: continue
    b = (n - START - 1) // PERIOD
    if b in arm_of_block:
        m = ls[0]
        if m.get('blk') != b or m.get('arm') != arm_of_block[b]:
            lab_bad.append((n, m.get('arm'), m.get('blk'), b))
out['label_mismatch_all_n_gt_1800'] = {'n': len(lab_bad), 'first': lab_bad[:10]}

kept = {0: [], 1: []}
for b, a in complete.items():
    for i in range(KLO, KHI):
        n = START + 1 + PERIOD * b + i
        row = {}
        row.update(draw[n][0]); row.update(xl[n][0]); row.update(main[n][0])
        row['_b'] = b
        kept[a].append(row)
out['kept'] = {a: len(v) for a, v in kept.items()}

def mean(rows, k):
    return sum(r[k] for r in rows) / len(rows)

# K5 over every x line with n > START
allx = [l[0] for n, l in xl.items() if n > START]
out['x_lines_after_start'] = len(allx)
raw = {k: sum(x.get(k, 0) for x in allx) for k in ('spine_bad', 'spine_misal', 'cram_write', 'carry_bad', 'spine_abort', 'spine_unc', 'spine_n', 'carry_skip', 'carry_cmp', 'spine_cmp', 'spine_el')}
out['raw_all_after_start'] = raw
P = kept[0]; M = kept[1]
sP = lambda k: sum(r[k] for r in P)
out['P_sums'] = {k: sP(k) for k in ('spine_n', 'spine_cmp', 'spine_el', 'carry_cmp', 'carry_skip', 'carry_bad', 'spine_unc', 'spine_abort', 'draws', 'dispatches')}
out['P_ratios'] = {
    'spine_cmp/spine_el': sP('spine_cmp') / sP('spine_el'),
    'carry_cmp/(spine_n-carry_skip)': sP('carry_cmp') / (sP('spine_n') - sP('carry_skip')),
    'safe (unc+abort)/spine_n': (sP('spine_unc') + sP('spine_abort')) / sP('spine_n'),
    'spine_el/(draws+disp)': sP('spine_el') / (sP('draws') + sP('dispatches')),
}
# K3
k3rows = [r for r in P if r['sc_frames'] == 1]
k3 = [r['k3_max'] / r['sc_el'] for r in k3rows if r['sc_el'] > 0]
out['K3'] = {'n': len(k3), 'median': statistics.median(k3), 'min': min(k3), 'max': max(k3), 'mean': sum(k3) / len(k3)}

def pctl(v, q):  # nearest-rank
    s = sorted(v); import math
    return s[max(0, math.ceil(q * len(s)) - 1)]

for W in (2, 4):
    q = [r for r in P if r['sc_frames'] == 1 and r['k4_w%d_n' % W] == 1]
    dep = [r['k4_w%d_dep' % W] for r in q]
    anyv = [r['k4_w%d_any' % W] for r in q]
    fmax = [r['k4_w%d_fmax' % W] for r in q]
    per_block = collections.defaultdict(list)
    for r in q: per_block[r['_b']].append(r['k4_w%d_dep' % W])
    bm = {b: statistics.median(v) for b, v in sorted(per_block.items())}
    hist = collections.Counter(dep)
    out['K4_W%d' % W] = {'n_qual': len(q), 'share_qual_of_kept': len(q) / len(P), 'median': statistics.median(dep),
                        'median_low': statistics.median_low(dep), 'p90': pctl(dep, 0.9), 'mean': sum(dep) / len(dep),
                        'above300': sum(1 for d in dep if d > 300) / len(dep), 'at_or_above300': sum(1 for d in dep if d >= 300) / len(dep),
                        'any_median': statistics.median(anyv), 'fmax_median': statistics.median(fmax), 'fmax_mean': sum(fmax) / len(fmax),
                        'fmax_p10': pctl(fmax, 0.1), 'fmax_p90': pctl(fmax, 0.9),
                        'block_medians': bm, 'dep_top_values': hist.most_common(8),
                        'n_rows_k4n_not1_in_P_sc1': sum(1 for r in P if r['sc_frames'] == 1 and r['k4_w%d_n' % W] != 1),
                        'k4n_values': dict(collections.Counter(r['k4_w%d_n' % W] for r in P))}
    # fmax per block mode split
    lo = [r['k4_w%d_fmax' % W] for r in q if bm[r['_b']] < (200 if W == 4 else 40)]
    hi = [r['k4_w%d_fmax' % W] for r in q if bm[r['_b']] >= (200 if W == 4 else 40)]
    out['K4_W%d' % W]['fmax_median_lowdep_blocks'] = statistics.median(lo) if lo else None
    out['K4_W%d' % W]['fmax_median_highdep_blocks'] = statistics.median(hi) if hi else None

# sc_frames distribution
scf_all = collections.Counter(x.get('sc_frames', -1) for x in allx)
scf_P_all = collections.Counter()
for n, l in xl.items():
    if n <= START: continue
    b = (n - START - 1) // PERIOD
    if arm_of_block.get(b) == 0:
        scf_P_all[l[0].get('sc_frames', -1)] += 1
scf_kept = collections.Counter(r['sc_frames'] for r in P)
# position within block of sc_frames != 1 in arm P
pos = collections.Counter()
for n, l in xl.items():
    if n <= START: continue
    b = (n - START - 1) // PERIOD
    if arm_of_block.get(b) == 0 and l[0].get('sc_frames') != 1:
        pos[(n - START - 1) % PERIOD] += 1
out['sc_frames'] = {'all_x_after_start': dict(scf_all), 'armP_all_frames': dict(scf_P_all), 'armP_kept': dict(scf_kept),
                    'armP_not1_positions': dict(sorted(pos.items()))}

REP = ['dt_us', 'cpu_gpu_us', 'draws', 'dispatches', 'bda_scan', 'da_take_us', 'spine_n', 'spine_ns', 'spine_el', 'spine_cmp',
       'carry_cmp', 'sc_el', 'k3_max', 'sc_ns', 'da_t_ver_us', 'da_t_pfa_us', 'da_t_cpy_us', 'da_t_key_us', 'da_t_prb_us', 'da_t_pfb_us',
       'bl_prep_us', 'bl_buf_us', 'bl_res_us', 'bl_img_us', 'mh_bind_us', 'mh_prog_us', 'mh_emit_us', 'mh_draws',
       'pl_em_com_ns', 'pl_em_rt_ns', 'pl_em_vtx_ns', 'pl_em_rec_ns', 'pl_em_pipe_ns', 'pl_em_rest_ns', 'da_t_n', 'bl_stage_n', 'pl_em_n']
out['means'] = {a: {k: mean(kept[a], k) for k in REP} for a in (0, 1)}
# M-arm dark checks in P, and P instruments dark in M
out['M_spine_n_sum'] = sum(r['spine_n'] for r in M)
out['M_sc_frames_sum'] = sum(r['sc_frames'] for r in M)
out['P_da_t_n_sum'] = sum(r['da_t_n'] for r in P)
# per-arm block list
out['blocks_P'] = sorted(b for b, a in complete.items() if a == 0)
out['blocks_M'] = sorted(b for b, a in complete.items() if a == 1)
# bda_scan per block (regime)
bs = collections.defaultdict(list)
for a in (0, 1):
    for r in kept[a]: bs[r['_b']].append(r['bda_scan'])
out['bda_scan_block_means_minmax'] = (min(sum(v)/len(v) for v in bs.values()), max(sum(v)/len(v) for v in bs.values()))

json.dump(out, open('C:/kyty/s118/audit118/recount118.json', 'w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
