# recount135.py - Session Auditor, s.135 step 8 (HPP-225): independent recount of rs135 (census rbslow in arms
# b2reuse=0|1) and of the smoke conditions s1s135..s3s135. Own code: no import from rs135.py, smk135.py, chk_rs135.py,
# lead/*, step6/*. Reads logs in binary. Formulas are taken from the TEXT of the seal pred/01_rs135.md s.5, 5a, 8 and
# ROADMAP p.166-174, not from the scorer.
# Blocks by GateArm: lines only (never by blk); arm by the TEXT of the GateArm line; row n of block b at position
# p = n - F_b - 1; the row n = F of the next GateArm is position 89 of the OUTGOING block; window p 10..88 inclusive
# (ROADMAP p.55(b)). Pairs (2k, 2k+1) of complete blocks with different arms. BDA mode of a block: mean bda_scan of the
# window, <= 300 NEW, >= 600 OLD (p.40(e)(1)).
import sys, math, json, hashlib, os

W_LO, W_HI = 10, 88
K_CNT, K_NS, DRIFT = 64, 10 ** 8, 5e-4
MAIN_F = ('dt_us', 'draws', 'arm', 'blk')
DRAW_F = ('bda_scan',)
PARTS7 = ('head', 'find', 'touch', 'sync', 'wr', 'rem', 'tail')
PARTS5 = ('find', 'touch', 'sync', 'wr', 'rem')
RS = ('rs_find_ns', 'rs_find_n', 'rs_touch_ns', 'rs_sync_ns', 'rs_wr_ns', 'rs_wr_n', 'rs_rem_ns', 'rs_sync_n', 'rs_sync_noop_n',
      'rs_sync_kb', 'rs_ro_n', 'rs_bf_n', 'rs_bf_would', 'rs_bf_diff', 'rs_bfw_ns', 'rs_refuse', 'rs_head_ns', 'rs_tail_ns',
      'rs_cen_ns', 'rs_bf_xchk', 'rs_bf_xdiff', 'rs_bf_strm', 'rs_disc_n', 'rs_bfw_k', 'rs_bf_race')
B2R = ('b2r_n', 'b2r_hit', 'b2r_chk', 'b2r_bad', 'b2r_path', 'b2r_hit_draw', 'b2r_hit_x', 'b2r_miss_new', 'b2r_miss_gen',
       'b2r_miss_evict', 'b2r_miss_kind', 'b2r_refuse', 'b2r_rst_cpu', 'b2r_rst_cpuw', 'b2r_wrapcur', 'b2r_nomap')
RB2 = ('rb_b2_n', 'rb_b2_would', 'rb_b2_kb', 'rb_b2_chk', 'rb_b2_diff', 'rb_b2_xchk', 'rb_b2_xdiff', 'rb_b2_evict', 'rb_b2_shovf',
       'rb_b2_rst_sub', 'rb_b2_rst_host', 'rb_b2_rst_wait', 'rb_b2_rst_rel', 'rb_b2_rst_wr', 'rb_b2_rst_cond', 'rb_b2_rst_emu',
       'rb_b2_rst_gpuw', 'rb_b2_rst_imgw', 'rb_b2_rst_ring')
CLS = ('stream', 'cbank', 'epoch', 'slow')
RB = tuple('rb_%s_%s' % (k, s) for k in CLS for s in ('ns', 'n')) + (
    'rb_cal_ns', 'rb_cal_n', 'rb_samp_n', 'rb_bpro_ns', 'rb_nupload_ns', 'rb_xprep_ns', 'rb_ximg_ns', 'rb_xbuf_ns', 'rb_head_ns',
    'rb_stage_ns', 'rb_find_ns', 'rb_bda_ns', 'rb_rt_ns', 'rb_tail_ns', 'rb_cls_bad', 'rb_refuse')
X_F = RB + RS + B2R + RB2 + ('mh_bind_us', 'bl_prep_us', 'bl_img_us', 'bl_buf_us', 'gclk_pin', 'rts_xthr', 'rts_acqw', 'rts_refuse')
KINDS = {b'FrameTrace:': ('m', MAIN_F), b'FrameTrace-draw:': ('d', DRAW_F), b'FrameTrace-x:': ('x', X_F)}
MARKERS = (b'--- std::terminate ---', b'--- abort() ---', b'--- Error', b'--- Fatal Error ---', b'GpuHangAbort:', b'ErrorDeviceLost',
           b'VK_ERROR_DEVICE_LOST', b'Unhandled exception')
COUNT_TAGS = (b'GpuWaitSlow:', b'BvhLoopCapTrip:', b'B2ReuseVerify:', b'RbSlowVerify:', b'AsyncPipelines: skipped draw',
              b'[Vulkan][E]', b'[Vulkan][W]', b'RbCen: refused', b'RbSlow: refused', b'B2Reuse: refused', b'RtSkip: refused')
HEADS = (b'B2Reuse: mode', b'RbCen: mode', b'RbSlow: mode', b'RtSkip: mode', b'GpuClockPin: mode')


def parse(path):
    rows = {'m': {}, 'd': {}, 'x': {}}
    xorder, xskip, dups = [], 0, {'m': 0, 'd': 0, 'x': 0}
    arms, heads, cnt = [], {}, {t.decode(): 0 for t in COUNT_TAGS}
    markers, quit_line, vkw, gates_m4 = [], None, {}, []
    h = hashlib.sha256()
    lno = 0
    with open(path, 'rb') as f:
        for ln in f:
            lno += 1
            h.update(ln)
            j = ln.find(b'FrameTrace')
            if j >= 0:
                sp = ln.find(b' ', j)
                key = ln[j:sp]
                if key in KINDS:
                    kind, names = KINDS[key]
                    toks = ln[sp + 1:].split()
                    if not toks or not toks[0].startswith(b'n='):
                        continue
                    n = int(toks[0][2:])
                    want = set(names)
                    d = {}
                    for t in toks[1:]:
                        k, _, v = t.partition(b'=')
                        ks = k.decode('ascii', 'replace')
                        if ks in want:
                            try:
                                d[ks] = int(v)
                            except ValueError:
                                pass
                    if n in rows[kind]:
                        dups[kind] += 1
                    rows[kind][n] = d
                    if kind == 'x':
                        if all(k in d for k in X_F):
                            xorder.append(d)
                        else:
                            xskip += 1
                    continue
            if b'GateArm:' in ln:
                a = {}
                for t in ln[ln.find(b'GateArm:') + 8:].split():
                    k, _, v = t.partition(b'=')
                    a[k.decode()] = v.decode()
                arms.append(a)
                continue
            s = ln.strip()
            for hd in HEADS:
                if hd in ln:
                    heads.setdefault(hd.decode(), []).append(s[s.find(hd):].decode('utf-8', 'replace')[:90])
            for t in COUNT_TAGS:
                if t in ln:
                    cnt[t.decode()] += 1
            if b'm4baton' in ln and b'Gate' in ln and len(gates_m4) < 5:
                gates_m4.append(s.decode('utf-8', 'replace')[:120])
            if b'[Vulkan][W]' in ln:
                q = s[s.find(b'[Vulkan][W]'):]
                key = q[:110].decode('utf-8', 'replace')
                vkw[key] = vkw.get(key, 0) + 1
            if quit_line is None and s == b'Event: quit':
                quit_line = lno
            for mk in MARKERS:
                if mk in ln:
                    markers.append((lno, mk.decode(), s.decode('utf-8', 'replace')[:160]))
                    break
    return dict(rows=rows, xorder=xorder, xskip=xskip, dups=dups, arms=arms, heads=heads, cnt=cnt, markers=markers,
                quit_line=quit_line, vkw=vkw, gates_m4=gates_m4, sha=h.hexdigest(), lines=lno)


# ---------- form (a) of p.168: running residual over ALL FrameTrace-x lines of the tag in log order ----------
def form_a(xs):
    def P(r, k):
        return r['rs_%s_ns' % k]
    ident = {
        'I0': (lambda r: r['rb_slow_ns'] - sum(P(r, k) for k in PARTS7), K_NS),
        'I1': (lambda r: r['rs_sync_n'] + r['rs_sync_noop_n'] - r['rb_slow_n'], K_CNT),
        'I2': (lambda r: r['rs_ro_n'] + r['rs_wr_n'] - r['rb_slow_n'], K_CNT),
    }
    ineq = {
        'N1': (lambda r: r['rs_ro_n'] - r['rs_bf_n'], K_CNT),
        'N2a': (lambda r: r['rs_bf_n'] - r['rs_bf_would'], K_CNT),
        'N2b': (lambda r: r['rs_bf_would'] - r['rs_bf_diff'], K_CNT),
        'N2c': (lambda r: r['rs_bf_would'] - r['rs_bf_race'], K_CNT),
        'N3': (lambda r: r['rb_slow_n'] - r['rs_find_n'], K_CNT),
        'N5': (lambda r: sum(P(r, k) for k in PARTS5) - r['rs_bfw_ns'], K_NS),
        'N6': (lambda r: r['rs_bf_n'] - r['rs_bf_would'] - r['rs_bf_xchk'], K_CNT),
        'N7': (lambda r: r['rs_bf_xchk'] - r['rs_bf_xdiff'], K_CNT),
    }
    out = {}
    for nm, (f, K) in ident.items():
        R, ext = 0, 0
        for r in xs:
            R += f(r)
            if abs(R) > abs(ext):
                ext = R
        out[nm] = dict(ok=bool(xs) and abs(ext) <= K, extreme=ext, last=R, K=K)
    raw = sum(r['rb_slow_ns'] for r in xs)
    out['I0D'] = dict(ok=raw > 0 and abs(out['I0']['last']) <= DRIFT * raw, last=out['I0']['last'], bound=DRIFT * raw, raw=raw)
    for nm, (f, K) in ineq.items():
        R, mn = 0, 0
        for r in xs:
            R += f(r)
            mn = min(mn, R)
        out[nm] = dict(ok=bool(xs) and mn >= -K and R >= -K, min=mn, last=R, K=K)
    out['rb_cls_bad'] = sum(r['rb_cls_bad'] for r in xs)
    out['rs_refuse'] = sum(r['rs_refuse'] for r in xs)
    out['PLACE'] = all(out[k]['ok'] for k in ('I0', 'I0D', 'I1', 'I2')) and out['rb_cls_bad'] == 0 and out['rs_refuse'] == 0
    out['LIVE'] = all(out[k]['ok'] for k in ('I0', 'I0D', 'I1', 'I2', 'N1', 'N2a', 'N2b', 'N2c', 'N3', 'N5', 'N6', 'N7'))
    out['lines'] = len(xs)
    out['sum_rb_slow_n'] = sum(r['rb_slow_n'] for r in xs)
    return out


def ms(v):
    v = [a for a in v if a is not None]
    n = len(v)
    if n == 0:
        return (None, None, 0)
    mu = sum(v) / n
    if n < 2:
        return (mu, None, n)
    sd = math.sqrt(sum((a - mu) ** 2 for a in v) / (n - 1))
    return (mu, sd / math.sqrt(n), n)


# ---------- block levels (seal s.5) ----------
def block_level(rows):
    N = len(rows)
    S = {}
    for k in X_F + MAIN_F + DRAW_F:
        S[k] = sum(r[k] for r in rows)
    L = dict(rows=N, sums=S, dt_us=S['dt_us'] / N, draws=S['draws'] / N, bda_scan=S['bda_scan'] / N,
             mh_bind_us=S['mh_bind_us'] / N, bl_buf_us=S['bl_buf_us'] / N)
    if S['rb_cal_n'] == 0:
        L['c'] = None
        return L
    c = S['rb_cal_ns'] / S['rb_cal_n']
    L['c'] = c
    n_slow = S['rb_slow_n']
    per = lambda tot: tot / (1000.0 * N)
    for p in PARTS7:
        num = 8 * S['rs_%s_ns' % p] - n_slow * c
        L['lv_' + p] = per(num)
        L['it_' + p] = num / n_slow if n_slow else None
        L['itraw_' + p] = 8 * S['rs_%s_ns' % p] / n_slow if n_slow else None
    L['lv_slow7'] = per(8 * S['rb_slow_ns'] - 7 * n_slow * c)
    L['it_slow7'] = (8 * S['rb_slow_ns'] - 7 * n_slow * c) / n_slow if n_slow else None
    L['lv_slow1'] = per(8 * S['rb_slow_ns'] - n_slow * c)
    for K in CLS:
        L['lv_cls_' + K] = per(8 * S['rb_%s_ns' % K] - S['rb_%s_n' % K] * c)
    L['L'] = L['lv_cls_stream'] + L['lv_cls_cbank']
    for K in CLS:
        L['raw_' + K] = per(8 * S['rb_%s_ns' % K])
        L['pf_rb_%s_n' % K] = S['rb_%s_n' % K] / N
    L['raw_L'] = L['raw_stream'] + L['raw_cbank']
    L['lv_epoch'] = L['lv_cls_epoch']
    # R1
    parts_r1 = ((S['bl_prep_us'] - S['rb_xprep_ns'] / 1000.0) + (S['bl_img_us'] - S['rb_ximg_ns'] / 1000.0) +
                (S['bl_buf_us'] - S['rb_xbuf_ns'] / 1000.0) +
                sum(S[k] for k in ('rb_head_ns', 'rb_stage_ns', 'rb_find_ns', 'rb_bda_ns', 'rb_rt_ns', 'rb_tail_ns')) / 1000.0)
    L['R1'] = (S['mh_bind_us'] - parts_r1) / N
    L['R2'] = (S['bl_buf_us'] - sum(8 * S['rb_%s_ns' % K] - S['rb_%s_n' % K] * c for K in CLS) / 1000.0
               - (S['rb_nupload_ns'] + S['rb_bpro_ns']) / 1000.0) / N
    L['lv_cen'] = per(8 * S['rs_cen_ns'] - 2 * S['rb_samp_n'] * c)
    L['R2p'] = L['R2'] - L['lv_cen']
    L['R3'] = L['lv_slow7'] - sum(L['lv_' + p] for p in PARTS7)
    L['R3L'] = L['lv_head'] + L['lv_tail']
    L['U3'] = 8 * (S['rs_bfw_ns'] - c * S['rs_bfw_k']) / (1000.0 * N)
    L['U3raw'] = 8 * S['rs_bfw_ns'] / (1000.0 * N)
    L['bfw_k_pf'] = S['rs_bfw_k'] / N
    for k in ('rs_sync_n', 'rs_sync_noop_n', 'rs_sync_kb', 'rb_slow_n', 'rs_bf_n', 'rs_bf_would', 'rs_wr_n', 'rs_bfw_k', 'rs_ro_n',
              'rs_find_n'):
        L['pf_' + k] = S[k] / N
    return L


def run_abba(P, arm_text, ABBA=(0, 1, 1, 0)):
    m, d, x = P['rows']['m'], P['rows']['d'], P['rows']['x']
    blocks, seq_ok = [], True
    for b, a in enumerate(P['arms']):
        arm = arm_text.get(a.get('text'))
        F = int(a.get('frame', -1))
        if not (int(a.get('block', -1)) == b and F == 1800 + 90 * b and a.get('arms') == '2' and a.get('period') == '90'
                and a.get('abba') == '1' and arm == ABBA[b % 4] and int(a.get('arm', -1)) == arm):
            seq_ok = False
        win, complete = [], True
        for p in range(W_LO, W_HI + 1):
            n = F + 1 + p
            if n not in m or n not in d or n not in x:
                complete = False; break
            mr, dr, xr = m[n], d[n], x[n]
            if any(k not in mr for k in MAIN_F) or any(k not in dr for k in DRAW_F) or any(k not in xr for k in X_F):
                complete = False; break
            if mr['arm'] != arm or mr['blk'] != b:
                complete = False; break
            r = dict(mr); r.update(dr); r.update(xr); r['n'] = n; r['p'] = p
            win.append(r)
        bl = dict(b=b, arm=arm, F=F, complete=complete, rows=win if complete else [])
        if complete:
            bl['lv'] = block_level(win)
            bs = bl['lv']['bda_scan']
            bl['mode'] = 'NEW' if bs <= 300 else ('OLD' if bs >= 600 else 'MID')
        blocks.append(bl)
    comp = [bl for bl in blocks if bl['complete']]
    res = dict(gatearm=len(blocks), complete=len(comp), seq_ok=seq_ok, incomplete=[bl['b'] for bl in blocks if not bl['complete']],
               arm_complete={a: sum(1 for bl in comp if bl['arm'] == a) for a in (0, 1)},
               modes_blocks={a: {mo: sum(1 for bl in comp if bl['arm'] == a and bl['mode'] == mo) for mo in ('NEW', 'OLD', 'MID')}
                             for a in (0, 1)}, modes={})
    byb = {bl['b']: bl for bl in comp}
    pairs = []
    for k in range(0, len(blocks), 2):
        if k in byb and k + 1 in byb and byb[k]['arm'] != byb[k + 1]['arm']:
            p0, p1 = (byb[k], byb[k + 1]) if byb[k]['arm'] == 0 else (byb[k + 1], byb[k])
            if p0['mode'] == p1['mode']:
                pairs.append(dict(k=k, mode=p0['mode'], b0=p0, b1=p1))
    for mode in ('NEW', 'OLD'):
        ps = [p for p in pairs if p['mode'] == mode]
        a0 = [bl for bl in comp if bl['arm'] == 0 and bl['mode'] == mode and bl['lv']['c'] is not None]
        a1 = [bl for bl in comp if bl['arm'] == 1 and bl['mode'] == mode and bl['lv']['c'] is not None]
        R = dict(pairs=len(ps), blocks0=len(a0), blocks1=len(a1))
        if len(ps) < 10:
            R['reading'] = 'DEBT'
            res['modes'][mode] = R
            continue
        lvk = (['lv_' + p for p in PARTS7] + ['it_' + p for p in PARTS7] + ['itraw_' + p for p in PARTS7] +
               ['lv_slow7', 'it_slow7', 'lv_slow1', 'L', 'lv_epoch', 'R1', 'R2', 'R2p', 'R3', 'R3L', 'U3', 'U3raw', 'c', 'mh_bind_us',
                'bl_buf_us', 'dt_us', 'lv_cen', 'bfw_k_pf'] + [k for k in a0[0]['lv'] if k.startswith('pf_')])
        for arm, bls in ((0, a0), (1, a1)):
            R['arm%d' % arm] = {k: ms([bl['lv'][k] for bl in bls]) for k in lvk}
        A0 = R['arm0']
        R['pct'] = {}
        for nm, ph in (('R1', 'mh_bind_us'), ('R2', 'bl_buf_us'), ('R2p', 'bl_buf_us'), ('R3', 'lv_slow7'), ('R3L', 'lv_slow7')):
            R['pct'][nm] = (A0[nm][0], A0[ph][0], 100.0 * A0[nm][0] / A0[ph][0] if A0[ph][0] > 0 else None)
        # U3_e (p.172(b)(2)): m3 = mean of arm-0 block ns/iter of find, touch, rem, only if all three < 0
        m3s = [A0['it_' + p][0] for p in ('find', 'touch', 'rem')]
        R['m3'] = sum(m3s) / 3 if all(v < 0 for v in m3s) else None
        R['c_e'] = A0['c'][0] + R['m3'] if R['m3'] is not None else None
        R['U3e'] = A0['U3'][0] - 8 * R['m3'] * A0['pf_rs_bfw_k'][0] / 1000.0 if R['m3'] is not None else None
        # shares over sums of window rows of complete arm-0 blocks of the mode
        SS = lambda k: sum(bl['lv']['sums'][k] for bl in a0)
        wo = SS('rs_bf_would')
        R['share_diff'] = (SS('rs_bf_diff'), wo, SS('rs_bf_diff') / wo if wo else None)
        R['share_risk'] = (SS('rs_bf_strm'), wo + SS('rs_bf_strm'), SS('rs_bf_strm') / (wo + SS('rs_bf_strm')) if wo + SS('rs_bf_strm') else None)
        R['share_race'] = (SS('rs_bf_race'), wo, SS('rs_bf_race') / wo if wo else None)
        R['share_would'] = (wo, SS('rs_bf_n'), wo / SS('rs_bf_n') if SS('rs_bf_n') else None)
        R['xchk'] = SS('rs_bf_xchk'); R['xdiff'] = SS('rs_bf_xdiff')
        R['check_proven'] = R['xchk'] >= 1000 and R['xdiff'] > 0
        U3 = A0['U3'][0]
        sd, sr = R['share_diff'][2], R['share_risk'][2]
        if (sd is not None and sd > 0.05) or (sr is not None and sr > 0.05):
            r2 = 'B3_CLOSED_RISK'
        elif U3 < 400:
            r2 = 'B3_PARKED'
        elif not R['check_proven']:
            r2 = 'B3_CHECK_NOT_PROVEN'
        elif sd is not None and sr is not None and sd <= 0.01 and sr <= 0.01:
            r2 = 'B3_PASSES'
        else:
            r2 = 'B3_CLOSE_QUESTION'
        R['d2'] = r2
        R['q_timer'] = U3 < 400 <= A0['U3raw'][0]
        # B2 rows: arm1 - arm0 by pairs of the mode (pairs without calibration in either block drop)
        pc = [p for p in ps if p['b0']['lv']['c'] is not None and p['b1']['lv']['c'] is not None]
        R['pairs_cal'] = len(pc)
        rowk = (['L', 'lv_epoch', 'lv_slow7', 'it_slow7', 'pf_rb_slow_n', 'lv_sync', 'pf_rs_sync_n', 'pf_rs_sync_noop_n', 'pf_rs_sync_kb'] +
                ['lv_' + p for p in PARTS7] + ['it_' + p for p in PARTS7] + ['itraw_' + p for p in PARTS7] +
                ['bl_buf_us', 'mh_bind_us', 'dt_us', 'draws', 'c', 'raw_L', 'raw_epoch', 'raw_slow', 'pf_rb_stream_n', 'pf_rb_cbank_n', 'pf_rb_epoch_n'])
        D = {}
        for k in rowk:
            v = [p['b1']['lv'][k] - p['b0']['lv'][k] for p in pc]
            mu, se, n = ms(v)
            D[k] = (mu, 2 * se, n)
        # p.174(c): d_parts minus d_c (two readings: literal = d(it) - d(c); timer-free = d(itraw) = d(it) + d(c))
        for p in PARTS7:
            v = [(p_['b1']['lv']['it_' + p] - p_['b0']['lv']['it_' + p]) - (p_['b1']['lv']['c'] - p_['b0']['lv']['c']) for p_ in pc]
            mu, se, n = ms(v)
            D['it_minus_dc_' + p] = (mu, 2 * se, n)
        R['rows'] = D
        dn, dn2 = D['pf_rs_sync_n'][0], D['pf_rs_sync_n'][1]
        if dn - dn2 > 0 and D['lv_sync'][0] >= 0.5 * D['lv_slow7'][0]:
            r3 = 'B2M_TRANSFER'
        elif -dn2 <= dn <= dn2 and sum(1 for p in PARTS5 if D['it_' + p][0] - D['it_' + p][1] > 0) >= 3:
            r3 = 'B2M_SURCHARGE'
        else:
            r3 = 'B2M_NOT_RESOLVED'
        R['d3'] = r3
        R['d3_parts_pos'] = [p for p in PARTS5 if D['it_' + p][0] - D['it_' + p][1] > 0]
        rr = [r for bl in a0 for r in bl['rows']]
        R['base_dt_arm0_rows'] = sum(r['dt_us'] for r in rr) / len(rr)
        R['arm0_window_rows'] = len(rr)
        # guards re-derived
        R['arm0_b2r_nonzero'] = sum(1 for r in rr for k in B2R if r[k] != 0)
        R['arm1_blocks_hit0'] = sum(1 for bl in a1 if sum(r['b2r_hit'] for r in bl['rows']) == 0)
        R['blocks_dead'] = sum(1 for bl in a0 + a1 if not (bl['lv']['sums']['rb_slow_n'] > 0 and bl['lv']['sums']['rs_bf_n'] > 0
                                                        and bl['lv']['sums']['rb_cal_n'] > 0))
        R['rts_rows'] = sum(1 for bl in a0 + a1 for r in bl['rows'] if r['rts_xthr'] or r['rts_acqw'] or r['rts_refuse'])
        R['gclk'] = (sum(bl['lv']['sums']['gclk_pin'] for bl in a0), sum(bl['lv']['sums']['gclk_pin'] for bl in a1))
        res['modes'][mode] = R
    return res


def smoke(P):
    xs = P['xorder']
    S = {k: sum(r[k] for r in xs) for k in RS + ('rb_slow_n', 'rb_slow_ns', 'rb_cal_n', 'rb_cls_bad', 'rb_refuse')}
    out = dict(x_lines=len(xs), xskip=P['xskip'], sums=S, form=form_a(xs) if xs else None)
    # smoke levels over rows after the stability frame (pseudo, one block): all full rows with n >= 278
    m, d = P['rows']['m'], P['rows']['d']
    rows = []
    x = P['rows']['x']
    for n in sorted(x):
        if n >= 278 and n in m and n in d and all(k in x[n] for k in X_F) and all(k in m[n] for k in ('dt_us', 'draws')) and 'bda_scan' in d[n]:
            r = dict(x[n]); r.update({'dt_us': m[n]['dt_us'], 'draws': m[n]['draws'], 'arm': 0, 'blk': 0, 'bda_scan': d[n]['bda_scan']})
            rows.append(r)
    if rows and sum(r['rb_cal_n'] for r in rows) > 0:
        L = block_level(rows)
        out['lv'] = {k: L[k] for k in ('rows', 'c', 'bda_scan', 'R1', 'R2', 'R2p', 'R3', 'R3L', 'U3', 'U3raw', 'lv_slow7', 'mh_bind_us', 'bl_buf_us')
                     + tuple('it_' + p for p in PARTS7)}
        out['pct'] = {nm: 100.0 * L[nm] / L[ph] for nm, ph in (('R1', 'mh_bind_us'), ('R2', 'bl_buf_us'), ('R2p', 'bl_buf_us'),
                                                                 ('R3', 'lv_slow7'), ('R3L', 'lv_slow7'))}
    return out


def death(P, stdout_path):
    ql = P['quit_line']
    g = [dict(line=l, marker=mk, text=s, after_quit=(ql is not None and l > ql), fs='fileSystem.cpp' in s) for l, mk, s in P['markers']]
    so = []
    if stdout_path and os.path.exists(stdout_path):
        with open(stdout_path, 'rb') as f:
            for i, ln in enumerate(f, 1):
                for mk in MARKERS:
                    if mk in ln:
                        so.append((i, mk.decode(), ln.strip().decode('utf-8', 'replace')[:160])); break
    return dict(log=g, stdout=so, quit_line=ql)


def main():
    base = 'C:/kyty/s135/'
    out = {}
    for tag in sys.argv[1:]:
        P = parse(base + 'log_%s.txt' % tag)
        R = dict(log_sha256=P['sha'], lines=P['lines'], dups=P['dups'], heads=P['heads'], cnt=P['cnt'], gatearm=len(P['arms']),
                 vk_w_classes=sorted(P['vkw'].items()), gates_m4=P['gates_m4'], death=death(P, base + 'stdout_%s.txt' % tag))
        R['smoke'] = smoke(P)
        if P['arms']:
            A = run_abba(P, {'b2reuse=0': 0, 'b2reuse=1': 1})
            R['abba'] = A
        out[tag] = R
        print('==', tag, 'sha', P['sha'][:16], 'lines', P['lines'], flush=True)
    with open(base + 'audit135/recount135_%s.json' % '_'.join(sys.argv[1:]), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, ensure_ascii=False, default=str)


if __name__ == '__main__':
    main()
