# recount133.py - Session Auditor, s.133 step 8 (HPP-199): independent recount of bc133.
# Own code: no import from bc133.py, smk133.py or lead/rc198.py. Reads log_bc133.txt in binary.
# Blocks by GateArm: lines only (never by blk); row n of block b at position p = n - F_b - 1;
# the row n = F of the next GateArm is position 89 of the OUTGOING block; window p 10..88 (ROADMAP p.55(b)).
import sys, re, math, json, hashlib

LOG = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s133/log_bc133.txt'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'C:/kyty/s133/audit133/recount133.json'
W_LO, W_HI = 10, 88

RE_REC = re.compile(rb'(FrameTrace(?:-draw|-x)?): n=(\d+) (.*)$')
RE_ARM = re.compile(rb'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(\S+)')

MAIN_F = ['dt_us', 'arm', 'blk', 'cpu_gpu_us', 'gpu_busy_us', 'semwait_gpu_us', 'draws']
DRAW_F = ['cb_copy', 'cb_copy_gpu', 'bda_scan', 'b_buf', 'bb_find', 'bb_obtain', 'bb_sync', 'bb_upload', 'ob_us', 'bb_n', 'ob_n']
RB1 = ['rb_head_ns', 'rb_stage_ns', 'rb_find_ns', 'rb_find_n', 'rb_bda_ns', 'rb_bda_n', 'rb_bda_scan_n', 'rb_rt_ns', 'rb_tail_ns',
       'rb_xprep_ns', 'rb_ximg_ns', 'rb_xbuf_ns', 'rb_stream_ns', 'rb_stream_n', 'rb_cbank_ns', 'rb_cbank_n', 'rb_epoch_ns',
       'rb_epoch_n', 'rb_slow_ns', 'rb_slow_n', 'rb_samp_n', 'rb_cal_ns', 'rb_cal_n', 'rb_bpro_ns', 'rb_nupload_ns',
       'rb_sync_up_ns', 'rb_sync_wait_ns', 'rb_cls_bad', 'rb_refuse']
RB2 = ['rb_b2_n', 'rb_b2_would', 'rb_b2_kb', 'rb_b2_chk', 'rb_b2_diff', 'rb_b2_xchk', 'rb_b2_xdiff', 'rb_b2_evict', 'rb_b2_shovf']
RST = ['rb_b2_rst_' + c for c in ('sub', 'host', 'wait', 'rel', 'wr', 'cond', 'emu', 'gpuw', 'imgw', 'ring')]
X_F = ['mh_bind_us', 'mh_draws', 'bl_prep_us', 'bl_img_us', 'bl_buf_us', 'bl_buf_n', 'ob_stream', 'ob_stream_us',
       'pb_wait_gpu_us', 'gclk_pin'] + RB1 + RB2 + RST
WANT = {b'FrameTrace': MAIN_F, b'FrameTrace-draw': DRAW_F, b'FrameTrace-x': X_F}


def parse_fields(rest, names):
    d = {}
    for tok in rest.split():
        k, _, v = tok.partition(b'=')
        ks = k.decode('ascii', 'replace')
        if ks in names:
            try:
                d[ks] = int(v)
            except ValueError:
                pass
    return d


rows = {b'FrameTrace': {}, b'FrameTrace-draw': {}, b'FrameTrace-x': {}}
dups = {k: 0 for k in rows}
arms = []
modes = []
tot_refuse = 0
tot_cls_bad = 0
h = hashlib.sha256()
with open(LOG, 'rb') as f:
    for ln in f:
        h.update(ln)
        if b'GateArm:' in ln:
            m = RE_ARM.search(ln)
            if m:
                arms.append(dict(arm=int(m.group(1)), arms=int(m.group(2)), block=int(m.group(3)), frame=int(m.group(4)),
                                 period=int(m.group(5)), abba=int(m.group(6)), text=m.group(7).decode()))
            continue
        if b'RbCen:' in ln:
            modes.append(ln.strip().decode('utf-8', 'replace')[ln.strip().decode('utf-8', 'replace').find('RbCen:'):])
        i = ln.find(b'FrameTrace')
        if i < 0:
            continue
        m = RE_REC.search(ln[i:].rstrip(b'\r\n'))
        if not m:
            continue
        kind, n = m.group(1), int(m.group(2))
        d = parse_fields(m.group(3), WANT[kind])
        if kind == b'FrameTrace-x':
            tot_refuse += d.get('rb_refuse', 0)
            tot_cls_bad += d.get('rb_cls_bad', 0)
        if n in rows[kind]:
            dups[kind] += 1
        rows[kind][n] = d

res = {'log_sha256': h.hexdigest(), 'gatearm_lines': len(arms), 'rbcen_lines': modes, 'dups': {k.decode(): v for k, v in dups.items()},
       'sum_rb_refuse_all': tot_refuse, 'sum_rb_cls_bad_all': tot_cls_bad}

# block table; schedule arm 0 = rbcen=1 = "arm 1" of p.141(v)(4); schedule arm 1 = rbcen=2 = "arm 2"
ABBA = (0, 1, 1, 0)
blocks = []
ok_seq = True
for idx, a in enumerate(arms):
    exp_arm = ABBA[idx % 4]
    exp_text = 'rbcen=1' if exp_arm == 0 else 'rbcen=2'
    if not (a['block'] == idx and a['frame'] == 1800 + 90 * idx and a['arms'] == 2 and a['period'] == 90 and a['abba'] == 1
            and a['arm'] == exp_arm and a['text'] == exp_text):
        ok_seq = False
    F = a['frame']
    win = []
    complete = True
    for p in range(W_LO, W_HI + 1):
        n = F + 1 + p
        mr, dr, xr = rows[b'FrameTrace'].get(n), rows[b'FrameTrace-draw'].get(n), rows[b'FrameTrace-x'].get(n)
        if mr is None or dr is None or xr is None:
            complete = False
            break
        if any(k not in mr for k in MAIN_F) or any(k not in dr for k in DRAW_F) or any(k not in xr for k in X_F):
            complete = False
            break
        if mr['arm'] != a['arm'] or mr['blk'] != idx:
            complete = False
            break
        r = dict(mr)
        r.update(dr)
        r.update(xr)
        r['n'] = n
        r['p'] = p
        win.append(r)
    blocks.append(dict(b=idx, arm=a['arm'], F=F, complete=complete, rows=win if complete else []))
res['gatearm_sequence_ok'] = ok_seq
res['blocks_total'] = len(blocks)
res['blocks_complete'] = sum(1 for b in blocks if b['complete'])
res['incomplete_blocks'] = [b['b'] for b in blocks if not b['complete']]
res['complete_by_arm'] = {str(k): sum(1 for b in blocks if b['complete'] and b['arm'] == k) for k in (0, 1)}


def S(rs, k):
    return sum(r[k] for r in rs)


def block_levels(bl):
    rs = bl['rows']
    N = len(rs)
    us = lambda k: S(rs, k) / N
    ns = lambda k: S(rs, k) / (1000.0 * N)
    cal_n = S(rs, 'rb_cal_n')
    c = S(rs, 'rb_cal_ns') / cal_n if cal_n else float('nan')
    lv = {}
    for K in ('stream', 'cbank', 'epoch', 'slow'):
        lv[K] = (8 * S(rs, 'rb_%s_ns' % K) - S(rs, 'rb_%s_n' % K) * c) / (1000.0 * N)
        lv[K + '_raw8'] = 8 * S(rs, 'rb_%s_ns' % K) / (1000.0 * N)
        lv[K + '_n'] = S(rs, 'rb_%s_n' % K) / N
    L = lv['stream'] + lv['cbank']
    chain = ['rb_head_ns', 'rb_stage_ns', 'rb_find_ns', 'rb_bda_ns', 'rb_rt_ns', 'rb_tail_ns']
    chain_us = {k[:-3]: ns(k) for k in chain}
    x = {k[:-3]: ns(k) for k in ('rb_xprep_ns', 'rb_ximg_ns', 'rb_xbuf_ns')}
    mh = us('mh_bind_us')
    prep, img, buf = us('bl_prep_us'), us('bl_img_us'), us('bl_buf_us')
    R1 = mh - ((prep - x['rb_xprep']) + (img - x['rb_ximg']) + (buf - x['rb_xbuf']) + sum(chain_us.values()))
    R1t = mh - (prep + img + buf + sum(chain_us.values()))
    nup, bpro = ns('rb_nupload_ns'), ns('rb_bpro_ns')
    R2 = buf - (lv['stream'] + lv['cbank'] + lv['epoch'] + lv['slow'] + nup + bpro)
    out = dict(mh_bind=mh, bl_prep=prep, bl_img=img, bl_buf=buf, unsplit=mh - (prep + img + buf), c_ns=c, L=L, R1=R1, R1_text=R1t,
               R2=R2, rb_nupload=nup, rb_bpro=bpro, rb_sync_up=ns('rb_sync_up_ns'), rb_sync_wait=ns('rb_sync_wait_ns'),
               dt_us=us('dt_us'), cpu_gpu_us=us('cpu_gpu_us'), gpu_busy_us=us('gpu_busy_us'), bda_scan=us('bda_scan'),
               draws=us('draws'), bl_buf_n=us('bl_buf_n'), samp8=8 * us('rb_samp_n'), L_raw8=lv['stream_raw8'] + lv['cbank_raw8'])
    out.update(chain_us)
    out.update(x)
    for K in ('stream', 'cbank', 'epoch', 'slow'):
        out['lvl_' + K] = lv[K]
        out['n_' + K] = lv[K + '_n']
    return out


def mean_se(v):
    n = len(v)
    m = sum(v) / n
    if n < 2:
        return m, float('nan')
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return m, sd / math.sqrt(n)


a1 = [b for b in blocks if b['complete'] and b['arm'] == 0]
a2 = [b for b in blocks if b['complete'] and b['arm'] == 1]
L1 = [block_levels(b) for b in a1]
L2 = [block_levels(b) for b in a2]
keys = sorted(L1[0].keys())
res['arm1_levels'] = {k: mean_se([d[k] for d in L1]) for k in keys}
res['arm2_levels'] = {k: mean_se([d[k] for d in L2]) for k in keys}

# row-level identity (p.141(v)(2) at ROW level, averaged over window rows of complete arm-1 blocks, c per block)
rowR1, rowR2 = [], []
for b, lv in zip(a1, L1):
    c = lv['c_ns']
    for r in b['rows']:
        chain = sum(r[k] for k in ('rb_head_ns', 'rb_stage_ns', 'rb_find_ns', 'rb_bda_ns', 'rb_rt_ns', 'rb_tail_ns'))
        r1 = r['mh_bind_us'] * 1000 - ((r['bl_prep_us'] * 1000 - r['rb_xprep_ns']) + (r['bl_img_us'] * 1000 - r['rb_ximg_ns'])
                                       + (r['bl_buf_us'] * 1000 - r['rb_xbuf_ns']) + chain)
        cls = sum(8 * r['rb_%s_ns' % K] - r['rb_%s_n' % K] * c for K in ('stream', 'cbank', 'epoch', 'slow'))
        r2 = r['bl_buf_us'] * 1000 - (cls + r['rb_nupload_ns'] + r['rb_bpro_ns'])
        rowR1.append(r1 / 1000.0)
        rowR2.append(r2 / 1000.0)
res['row_identity'] = dict(rows=len(rowR1), R1_mean=sum(rowR1) / len(rowR1), R2_mean=sum(rowR2) / len(rowR2),
                           R1_rows_over5pct=sum(1 for v in rowR1 if abs(v) > 0.05 * res['arm1_levels']['mh_bind'][0]),
                           R2_rows_over5pct=sum(1 for v in rowR2 if abs(v) > 0.05 * res['arm1_levels']['bl_buf'][0]))
mh1 = res['arm1_levels']['mh_bind'][0]
buf1 = res['arm1_levels']['bl_buf'][0]
R1m = res['arm1_levels']['R1'][0]
R2m = res['arm1_levels']['R2'][0]
res['R1_pct'] = 100 * R1m / mh1
res['R2_pct'] = 100 * R2m / buf1
res['R1_ok'] = 100 * abs(R1m) <= 5 * mh1
res['R2_within5'] = 100 * abs(R2m) <= 5 * buf1

# arm-1 null of B2 counters (window rows)
res['arm1_b2_nonzero'] = sum(1 for b in a1 for r in b['rows'] for k in RB2 + RST if r[k] != 0)

# arm-2 shares, sums over window rows of complete arm-2 blocks
rs2 = [r for b in a2 for r in b['rows']]
T = {k: S(rs2, k) for k in RB2 + RST + ['rb_stream_n', 'cb_copy', 'cb_copy_gpu', 'rb_cbank_n']}
T['rows'] = len(rs2)
ins = T['rb_b2_n'] - T['rb_b2_would']
rst_all = sum(T[k] for k in RST)
trim = rst_all - T['rb_b2_rst_wait'] - T['rb_b2_rst_sub'] - T['rb_b2_rst_emu']
shares = dict(would_n=T['rb_b2_would'] / T['rb_b2_n'], diff_chk=(T['rb_b2_diff'] / T['rb_b2_chk']) if T['rb_b2_chk'] else None,
              xdiff_xchk=(T['rb_b2_xdiff'] / T['rb_b2_xchk']) if T['rb_b2_xchk'] else None, evict_ins=T['rb_b2_evict'] / ins,
              imgw_all=T['rb_b2_rst_imgw'] / rst_all, imgw_trim=T['rb_b2_rst_imgw'] / trim if trim else None,
              denom_text=T['rb_stream_n'] + T['cb_copy'], would_over_text_denom=T['rb_b2_would'] / (T['rb_stream_n'] + T['cb_copy']),
              diff_upper95=3.0 / T['rb_b2_chk'] if T['rb_b2_chk'] and T['rb_b2_diff'] == 0 else None)
per_block_would = [S(b['rows'], 'rb_b2_would') / S(b['rows'], 'rb_b2_n') for b in a2]
shares['would_n_blocks'] = mean_se(per_block_would)
shares['would_n_min_block'] = min(per_block_would)
res['arm2_sums'] = T
res['arm2_shares'] = shares
res['arm2_per_frame'] = {k: T[k] / T['rows'] for k in RB2 + RST}

# member reading p.141(v)(6) with p.146(b) band, p.142(b) B5/B6, p.143(a)+145(a)
L = res['arm1_levels']['L'][0]
lo, hi = L - max(0.0, -R2m), L + max(0.0, R2m)
m1 = 'MET' if lo >= 400 else ('NOT_MET' if hi < 400 else 'UNDECIDED')
ctrl = 'ALIVE' if T['rb_b2_xdiff'] > 0 else ('DEAD' if T['rb_b2_xchk'] >= 1000 else 'NOT_EVALUABLE')
if 2 * T['rb_b2_would'] >= T['rb_b2_n']:
    m2 = 'MET'
else:
    m2 = 'UNDECIDED' if (shares['evict_ins'] > 0.01 or (shares['imgw_trim'] is None) or shares['imgw_trim'] >= 0.10) else 'NOT_MET'
if ctrl != 'ALIVE' or T['rb_b2_chk'] == 0:
    m3 = 'NOT_CHECKED'
elif 100 * T['rb_b2_diff'] <= T['rb_b2_chk']:
    m3 = 'MET'
elif 100 * T['rb_b2_diff'] > 5 * T['rb_b2_chk']:
    m3 = 'CLOSE_RISK'
else:
    m3 = 'BETWEEN'
if m3 == 'CLOSE_RISK':
    outcome = 'B2_CLOSED_RISK'
elif 'NOT_MET' in (m1, m2, m3):
    outcome = 'B2_NOT_PASSES'
elif (m1, m2, m3) == ('MET', 'MET', 'MET'):
    outcome = 'B2_PASSES'
else:
    outcome = 'B2_CLOSE_QUESTION'
res['reading'] = dict(L=L, R2=R2m, lo=lo, hi=hi, member1=m1, control=ctrl, member2=m2, member3=m3, outcome=outcome)

# delta arm2 - arm1 over ABBA pairs (2k, 2k+1) with both complete
lvl_by_b = {b['b']: (b['arm'], block_levels(b)) for b in blocks if b['complete']}
dl = {'dt_us': [], 'mh_bind': [], 'bl_buf': []}
npairs = 0
for k in range(0, len(blocks), 2):
    if k in lvl_by_b and k + 1 in lvl_by_b:
        (aa, la), (ab, lb) = lvl_by_b[k], lvl_by_b[k + 1]
        if aa == ab:
            continue
        l1, l2 = (la, lb) if aa == 0 else (lb, la)
        npairs += 1
        for key in dl:
            dl[key].append(l2[key] - l1[key])
res['delta_pairs'] = npairs
res['delta_2se'] = {k: (mean_se(v)[0], 2 * mean_se(v)[1]) for k, v in dl.items()}

# BDA mode per complete block
res['bda_modes'] = {str(arm): {'NEW': sum(1 for b in blocks if b['complete'] and b['arm'] == arm and block_levels(b)['bda_scan'] <= 300),
                               'OLD': sum(1 for b in blocks if b['complete'] and b['arm'] == arm and block_levels(b)['bda_scan'] >= 600)}
                    for arm in (0, 1)}

# K1 on the sum per arm; trace lite; gclk
for arm, bl in (('1', a1), ('2', a2)):
    rs = [r for b in bl for r in b['rows']]
    diffs = [r['rb_find_n'] - r['mh_draws'] for r in rs]
    cum, mx = 0, 0
    for d in diffs:
        cum += d
        mx = max(mx, abs(cum))
    res['K1_arm' + arm] = dict(sum=sum(diffs), max_cum=mx, bound=1e-4 * S(rs, 'mh_draws'), rows_off=sum(1 for d in diffs if d))
    res['K2_arm' + arm] = (8 * S(rs, 'rb_samp_n') - S(rs, 'bl_buf_n')) / S(rs, 'bl_buf_n')
    res['lite_timers_sum_arm' + arm] = sum(S(rs, k) for k in ('b_buf', 'bb_find', 'bb_obtain', 'bb_sync', 'bb_upload', 'ob_us', 'ob_stream_us'))
    res['gclk_pin_sum_arm' + arm] = S(rs, 'gclk_pin')

# parts of arm 1 >= 400 us/frame (a row for the s.134 selection, not a mechanism)
parts = {k: res['arm1_levels'][k][0] for k in ('bl_prep', 'bl_img', 'bl_buf', 'unsplit', 'rb_head', 'rb_stage', 'rb_find', 'rb_bda',
                                                 'rb_rt', 'rb_tail', 'lvl_stream', 'lvl_cbank', 'lvl_epoch', 'lvl_slow', 'rb_nupload', 'rb_bpro')}
res['arm1_parts_ge400'] = {k: v for k, v in parts.items() if v >= 400}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print(json.dumps({k: res[k] for k in ('log_sha256', 'gatearm_lines', 'blocks_complete', 'incomplete_blocks', 'complete_by_arm',
                                     'gatearm_sequence_ok', 'dups', 'rbcen_lines', 'sum_rb_refuse_all', 'sum_rb_cls_bad_all')},
                 ensure_ascii=False))
A = res['arm1_levels']
for k in ('mh_bind', 'bl_prep', 'bl_img', 'bl_buf', 'unsplit', 'rb_head', 'rb_stage', 'rb_find', 'rb_bda', 'rb_rt', 'rb_tail',
          'rb_xprep', 'rb_ximg', 'rb_xbuf', 'lvl_stream', 'lvl_cbank', 'lvl_epoch', 'lvl_slow', 'rb_nupload', 'rb_bpro',
          'rb_sync_up', 'rb_sync_wait', 'L', 'L_raw8', 'R1', 'R1_text', 'R2', 'c_ns', 'dt_us', 'cpu_gpu_us', 'gpu_busy_us',
          'n_stream', 'n_cbank', 'n_epoch', 'n_slow', 'bl_buf_n', 'samp8', 'draws', 'bda_scan'):
    print('arm1 %-12s %12.3f  se %8.3f' % (k, A[k][0], A[k][1]))
B = res['arm2_levels']
for k in ('mh_bind', 'bl_buf', 'L', 'R2', 'dt_us', 'bda_scan'):
    print('arm2 %-12s %12.3f  se %8.3f' % (k, B[k][0], B[k][1]))
print('R1 %% mh_bind %.3f ok=%s; R2 %% bl_buf %.3f within5=%s; row identity %s' % (res['R1_pct'], res['R1_ok'], res['R2_pct'],
                                                                                  res['R2_within5'], res['row_identity']))
print('arm1 B2 nonzero fields in window rows:', res['arm1_b2_nonzero'])
print('arm2 sums:', T)
print('arm2 shares:', shares)
print('reading:', res['reading'])
print('delta pairs', npairs, res['delta_2se'])
print('bda modes', res['bda_modes'])
for arm in ('1', '2'):
    print('arm', arm, 'K1', res['K1_arm' + arm], 'K2', res['K2_arm' + arm], 'lite timers', res['lite_timers_sum_arm' + arm],
          'gclk_pin', res['gclk_pin_sum_arm' + arm])
print('arm1 parts >= 400:', res['arm1_parts_ge400'])
