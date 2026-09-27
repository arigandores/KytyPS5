# recount126.py - independent recount of the s126 sealed run k3c126 (Session Auditor, HPP-91).
# No code shared with k3c126.py: own tokenizer, own block builder (GateArm lines only, never blk),
# window positions 10..88 inclusive (item 55(b)), level = mean of window rows, SE over block means (n-1).
import re, sys, math, json, hashlib

LOG = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s126/log_k3c126.txt'
import os
W_LO, W_HI = int(os.environ.get('RC_WLO', 10)), int(os.environ.get('RC_WHI', 88))
KV = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')
ARM_TEXT = {0: b'rk3cen=0 pathlap=0 mutsite=0', 1: b'rk3cen=1 pathlap=1 mutsite=1'}
ABBA = (0, 1, 1, 0)

main, drw, xx = {}, {}, {}
dups = {'main': 0, 'draw': 0, 'x': 0}
gatearms = []
counts = {'mode1': 0, 'mode_other': 0, 'refused': 0, 'skipped': 0, 'death': 0}
DEATH = [b'--- std::terminate ---', b'--- abort() ---', b'--- Error ---', b'--- Fatal Error ---',
         b'GpuHangAbort:', b'ErrorDeviceLost', b'VK_ERROR_DEVICE_LOST', b'Unhandled exception']

def kv(line):
    return {k.decode(): int(v) for k, v in KV.findall(line)}

with open(LOG, 'rb') as f:
    for line in f:
        i = line.find(b'FrameTrace')
        if i >= 0:
            s = line[i:]
            if s.startswith(b'FrameTrace: n='):
                d, tgt, key = kv(s), main, 'main'
            elif s.startswith(b'FrameTrace-draw: n='):
                d, tgt, key = kv(s), drw, 'draw'
            elif s.startswith(b'FrameTrace-x: n='):
                d, tgt, key = kv(s), xx, 'x'
            else:
                continue
            n = d['n']
            if n in tgt:
                dups[key] += 1
            tgt[n] = d
            continue
        if b'GateArm:' in line:
            s = line[line.find(b'GateArm:'):].rstrip(b'\r\n')
            t = s.split(b'text=', 1)[1] if b'text=' in s else b''
            gatearms.append((kv(s.split(b'text=')[0]), t))
        elif b'Rk3Census:' in line:
            if b'refused' in line:
                counts['refused'] += 1
            elif b'mode 1' in line:
                counts['mode1'] += 1
            elif b'mode' in line:
                counts['mode_other'] += 1
        elif b'AsyncPipelines: skipped draw' in line:
            counts['skipped'] += 1
        else:
            for m in DEATH:
                if m in line:
                    counts['death'] += 1
                    break

# blocks strictly from GateArm lines
blocks = []
bad_arm = 0
for g, t in gatearms:
    b = g['block']
    arm = g['arm']
    if g['frame'] != 1800 + 90 * b or g['period'] != 90 or g['abba'] != 1 or g['arms'] != 2 \
            or arm != ABBA[b % 4] or t != ARM_TEXT[arm]:
        bad_arm += 1
    blocks.append((b, arm, g['frame']))

def mean(v):
    return sum(v) / len(v)

def se(v):
    k = len(v)
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (k - 1)) / math.sqrt(k)

full = []
arm_mismatch = 0
for b, arm, fr in blocks:
    rows = []
    ok = True
    for p in range(W_LO, W_HI + 1):
        n = fr + 1 + p
        if n not in main or n not in drw or n not in xx:
            ok = False
            break
        if main[n].get('arm') != arm or main[n].get('blk') != b:
            arm_mismatch += 1
        rows.append(n)
    if ok:
        bda = mean([drw[n]['bda_scan'] for n in rows])
        reg = 'NEW' if bda <= 300 else ('OLD' if bda >= 600 else 'MID')
        full.append((b, arm, rows, reg, bda))

out = {'log': LOG, 'gatearm_lines': len(gatearms), 'bad_gatearm': bad_arm, 'arm_blk_mismatch_rows': arm_mismatch,
       'dups': dups, 'counts': counts, 'full_blocks': len(full),
       'full_B': sum(1 for x in full if x[1] == 0), 'full_C': sum(1 for x in full if x[1] == 1),
       'incomplete': [b for b, _, _ in blocks if b not in {x[0] for x in full}],
       'regimes': {r: sum(1 for x in full if x[3] == r) for r in ('NEW', 'OLD', 'MID')},
       'bda_block_mean_range': [min(x[4] for x in full), max(x[4] for x in full)]}

# reading R per regime (item 63(v)/64(g)): T = rk3_rt_r_ns + rk3_res_r_ns + rk3_res_x_ns per row
def T(n):
    x = xx[n]
    return x['rk3_rt_r_ns'] + x['rk3_res_r_ns'] + x['rk3_res_x_ns']

R = {}
for reg in ('NEW', 'OLD'):
    cb = [x for x in full if x[1] == 1 and x[3] == reg]
    if not cb:
        continue
    allrows = [T(n) / 1000.0 for x in cb for n in x[2]]
    bm = [mean([T(n) / 1000.0 for n in x[2]]) for x in cb]
    lvl = mean(allrows)
    if len(cb) >= 4:
        r = lvl + 2 * se(bm)
    else:
        r = max(bm)
    bms = sorted(bm)
    med = bms[len(bms) // 2] if len(bms) % 2 else 0.5 * (bms[len(bms) // 2 - 1] + bms[len(bms) // 2])
    R[reg] = {'R': r, 'mean_rows': lvl, 'se': se(bm), 'median_block_means': med, 'blocks': len(cb),
              'rows': len(allrows), 'block_mean_min': min(bm), 'block_mean_max': max(bm)}
out['R'] = R
out['R_K3_plus'] = max(v['R'] for v in R.values())
out['verdict'] = 'K3_CLOSED' if out['R_K3_plus'] < 500 else 'K3_NOT_CLOSED'

# T0 alone and a few per-row rows over all C full blocks
cb = [x for x in full if x[1] == 1]
rowsC = [n for x in cb for n in x[2]]
def rowmean_x(field):
    return mean([xx[n][field] for n in rowsC])
out['C_rows_us'] = {f: rowmean_x(f) / 1000.0 for f in
                    ('rk3_rt_ns', 'rk3_rt_r_ns', 'rk3_res_ns', 'rk3_res_r_ns', 'rk3_res_x_ns', 'pl_em_rt_ns', 'pl_em_rk3_ns')}
out['C_rows_n'] = {f: rowmean_x(f) for f in ('rk3_n', 'rk3_w', 'rk3_xw', 'rk3_rec0', 'rk3_xid', 'rk3_xctx', 'rk3_ovf')}
t0bm = [mean([xx[n]['rk3_rt_r_ns'] / 1000.0 for n in x[2]]) for x in cb]
out['T0_alone'] = mean([xx[n]['rk3_rt_r_ns'] / 1000.0 for n in rowsC]) + 2 * se(t0bm)

# guards on EVERY C window row (complete or not)
g = {'rk3_nt': 0, 'rk3_xthr': 0, 'rk3_acqw': 0}
for b, arm, fr in blocks:
    if arm != 1:
        continue
    for p in range(W_LO, W_HI + 1):
        n = fr + 1 + p
        if n in xx:
            for k in g:
                g[k] += 1 if xx[n].get(k, 0) != 0 else 0
out['guard_nonzero_rows'] = g

# zero control B window rows: every rk3_* and pl_em_rk3_ns and rk3_c5_max_ns == 0
zb = 0
for x in full:
    if x[1] != 0:
        continue
    for n in x[2]:
        if any(v != 0 for k, v in xx[n].items() if k.startswith('rk3_')) or xx[n].get('pl_em_rk3_ns', 0) != 0 \
                or main[n].get('rk3_c5_max_ns', 0) != 0:
            zb += 1
out['zero_B_bad_rows'] = zb

# identities T1, T4 on window sums of each C block (own tolerance: Tol_n 256, Tol_ns 256*max c5 of pos 10/88)
fails = []
maxd = {'T1': 0, 'T4a': 0, 'T4b': 0, 'T5': 0}
share = []
for x in cb:
    S = lambda f: sum(xx[n][f] for n in x[2])
    tol_ns = 256 * max(main[x[2][0]]['rk3_c5_max_ns'], main[x[2][-1]]['rk3_c5_max_ns'])
    d1 = S('rk3_n') - (S('rk3_rec0') + S('rk3_xw') + S('rk3_w'))
    d4a = S('rk3_rt_ns') - S('pl_em_rt_ns')
    d4b = S('rk3_n') - S('pl_em_n')
    d5 = S('rk3_c4_n') - (S('rk3_n') + S('rk3_res_x_n'))
    for k, v in (('T1', d1), ('T4a', d4a), ('T4b', d4b), ('T5', d5)):
        maxd[k] = max(maxd[k], abs(v))
    if abs(d1) > 256 or abs(d4b) > 256 or abs(d5) > 256 or abs(d4a) > tol_ns:
        fails.append(x[0])
    pl = sum(S(f) for f in ('pl_em_vtx_ns', 'pl_em_rt_ns', 'pl_em_pipe_ns', 'pl_em_com_ns', 'pl_em_rec_ns',
                            'pl_em_rest_ns', 'pl_em_rk3_ns'))
    share.append(pl / (S('mh_emit_us') * 1000.0))
out['T_fail_blocks'] = fails
out['T_max_abs'] = maxd
out['chain_share_min_max'] = [min(share), max(share)]

# base (item 62(zh)(5)): mean dt_us of B window rows
bb = [x for x in full if x[1] == 0]
out['base_dt_us'] = mean([main[n]['dt_us'] for x in bb for n in x[2]])
out['base_blocks'] = len(bb)
out['base_regimes'] = {r: sum(1 for x in bb if x[3] == r) for r in ('NEW', 'OLD', 'MID')}
out['game_speed_base'] = 16667.0 / out['base_dt_us']

# ABBA pairs (2k, 2k+1) of full blocks: C - B
byb = {x[0]: x for x in full}
def pair_delta(field, src=main):
    d = []
    for k in range(0, max(byb) + 1, 2):
        if k in byb and k + 1 in byb:
            a, c = byb[k], byb[k + 1]
            mb = mean([src[n][field] for n in (a[2] if a[1] == 0 else c[2])])
            mc = mean([src[n][field] for n in (c[2] if c[1] == 1 else a[2])])
            d.append(mc - mb)
    return mean(d), 2 * se(d), len(d)
out['cost_C_minus_B'] = {f: pair_delta(f) for f in ('dt_us', 'cpu_gpu_us', 'draws', 'gpu_busy_us')}

h = hashlib.sha256()
with open(LOG, 'rb') as f:
    for chunk in iter(lambda: f.read(1 << 22), b''):
        h.update(chunk)
out['log_sha256'] = h.hexdigest()
print(json.dumps(out, indent=1, ensure_ascii=True))
