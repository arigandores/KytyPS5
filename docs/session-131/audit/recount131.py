# Session 131 audit (HPP-173, Session Auditor): independent recount of the L reading (ROADMAP s122 item 123(zh)(5) with
# items 126(v), 127(k), 128(g), 129(g), 130(b)(7), 131(b)-(v)) over lw1s131..lw6s131 and of the sealed dd131 (item 123(z)(3)-(5),
# 124, 125, 132(g)), from the RAW logs. No code shared with lw131.py, dds131.py, dd131.py, chk_dd131.py (none read or imported);
# port of my own audit129/recount129.py and audit130/recount130b.py.
# Blocks ONLY by 'GateArm:' lines. Row n belongs to the last GateArm with F < n (row n = F of the next GateArm is position 89
# of the leaving block). Position p = n - F - 1. Window 10..88 inclusive (item 55(b)); complete block = rows p 10..88 all present.
import json, math, re, sys
from fractions import Fraction

ROOT = 'C:/kyty/s131/'
KV = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')
GA = re.compile(rb'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(\S*)')
DEATH = (b'--- std::terminate', b'--- abort()', b'--- Error', b'--- Fatal Error', b'GpuHangAbort:', b'ErrorDeviceLost',
         b'VK_ERROR_DEVICE_LOST', b'ReportVulkanFatal', b'AsyncPipelines: skipped draw', b'Unhandled exception')
WLO, WHI = 10, 88


def kv(b):
    return {k.decode(): int(v) for k, v in KV.findall(b)}


def fields(line):
    return dict(re.findall(r'(\w+)=(\S+)', line))


def read_log(path):
    rows = {}          # n -> merged dict of FrameTrace / -draw / -x
    arms = []          # (lineno, arm, narms, block, frame, period, abba, text)
    loss, lossctl, late, lwmode, ovf, torn, death, other = [], [], 0, [], [], 0, [], {}
    quit_line = None
    last_n = None
    with open(path, 'rb') as f:
        for ln, raw in enumerate(f, 1):
            s = raw.lstrip()
            if s.startswith(b'FrameTrace'):
                sp = s.find(b': ')
                d = {k: v for k, v in kv(s[sp + 2:]).items() if k in NEED}
                n = d.get('n')
                if n is None:
                    continue
                r = rows.setdefault(n, {})
                pref = s[:sp].decode()
                r.setdefault('_src', []).append(pref)
                r.update(d)
                if pref == 'FrameTrace':
                    last_n = n
                continue
            if s.startswith(b'GateArm: '):
                m = GA.match(s)
                if not m:
                    raise SystemExit('unparsed GateArm %r' % s[:200])
                arms.append((ln,) + tuple(int(m.group(i)) for i in range(1, 7)) + (m.group(7).decode(),))
                continue
            t = s.decode(errors='replace').rstrip()
            if t.startswith('ArmCopyLoss: '):
                d = fields(t); d['_ln'] = ln; d['_last_n'] = last_n; loss.append(d)
            elif t.startswith('ArmCopyLossCtl: '):
                lossctl.append(fields(t))
            elif t.startswith('ArmCopyLossLate'):
                late += 1
            elif t.startswith('LossWin: mode'):
                lwmode.append(t)
            elif t.startswith('LossWin: overflow'):
                ovf.append(t)
            elif 'ArmCopyClass: TORN' in t:
                torn += 1
            elif t.startswith('Event: quit') and quit_line is None:
                quit_line = ln
            for key in ('ArmCopy: mode', 'ArmCopy: refused', 'DispCeil: mode', 'DispCeil: refused', 'GpuWaitSlow:',
                        'BvhLoopCapTrip:', 'RtSkip: refused', 'ProtCeil:'):
                if key in t:
                    other.setdefault(key, []).append(t[:120])
            if any(k in s for k in DEATH):
                nxt = None
                death.append({'ln': ln, 'text': t[:160]})
    # attach next line for death markers (fileSystem.cpp form, item 133(b)(1))
    if death:
        want = {d['ln'] + 1: d for d in death}
        with open(path, 'rb') as f:
            for ln, raw in enumerate(f, 1):
                if ln in want:
                    want[ln]['next'] = raw.decode(errors='replace').strip()[:200]
                    if len([1 for d in death if 'next' in d]) == len(death):
                        break
    return {'rows': rows, 'arms': arms, 'loss': loss, 'lossctl': lossctl, 'late_lines': late, 'lwmode': lwmode,
            'ovf': ovf, 'torn': torn, 'death': death, 'quit_line': quit_line, 'other': other}


def blocks_of(L):
    """assign every row n > first F to a block; returns list of blocks with rows by position"""
    arms = L['arms']
    rows = L['rows']
    out = []
    for i, a in enumerate(arms):
        F = a[4]
        Fn = arms[i + 1][4] if i + 1 < len(arms) else None
        ns = sorted(n for n in rows if n > F and (Fn is None or n <= Fn))
        pos = {n - F - 1: rows[n] for n in ns}
        comp = all(p in pos for p in range(WLO, WHI + 1)) and (Fn is not None and Fn == F + 90)
        out.append({'i': i, 'block': a[3], 'arm': a[1], 'F': F, 'text': a[7], 'pos': pos, 'complete': comp})
    return out


def mean(v):
    return sum(v) / len(v)


def se(v):
    m = mean(v)
    return math.sqrt(sum((a - m) ** 2 for a in v) / (len(v) - 1)) / math.sqrt(len(v))


def g(r, k):
    return r.get(k, 0)


LWK = ('lw_p8', 'lw_x', 'lw_open', 'lw_xnc', 'lw_xmk', 'lw_p8sync', 'lw_crx', 'lw_crp', 'lw_cdx', 'lw_cdp', 'lw_c3x',
       'lw_c3p', 'lw_late', 'lw_ovf', 'lw_stamp_pages', 'lw_mark_pages', 'lw_sync_pages', 'lw_spin_n', 'lw_spin_ns')
ACK = ('ac_cbm_host', 'ac_cbm_host_d', 'ac_cbm_pend', 'ac_cbm_nosnap', 'ac_cbm_bad', 'ac_cbm_left', 'ac_cbm_stale',
       'ac_cmp_pages', 'ac_cbad')


def identities(r, is_lw4):
    """per-row identities И-L1, И-L2, И-L2', И-L3, И-L4, И-L5 (items 126(b)-(v)); returns list of broken names"""
    bad = []
    H = g(r, 'ac_cbm_host') - g(r, 'ac_cbm_host_d')
    if g(r, 'lw_p8') + g(r, 'lw_x') != H: bad.append('IL1')
    if g(r, 'lw_open') + g(r, 'lw_xnc') + g(r, 'lw_xmk') != g(r, 'lw_x'): bad.append('IL2')
    if g(r, 'lw_p8sync') > g(r, 'lw_p8'): bad.append('IL2p')
    if g(r, 'lw_crx') + g(r, 'lw_crp') > g(r, 'ac_cbm_pend'): bad.append('IL3')
    if g(r, 'lw_cdx') + g(r, 'lw_cdp') > g(r, 'ac_cbm_host_d'): bad.append('IL4')
    if is_lw4:
        if g(r, 'lw_c3x') + g(r, 'lw_c3p') != g(r, 'ac_cbm_bad') + g(r, 'ac_cbm_left'): bad.append('IL5')
    else:
        if g(r, 'lw_c3x') or g(r, 'lw_c3p'): bad.append('IL5')
    return bad


def sums(rowlist, keys):
    return {k: sum(g(r, k) for r in rowlist) for k in keys}


def lw_tag(tag):
    L = read_log(ROOT + 'log_%s.txt' % tag)
    meta = json.load(open(ROOT + '%s.json' % tag, encoding='utf-8'))
    rows = L['rows']
    xrows = {n: r for n, r in rows.items() if 'FrameTrace-x' in r.get('_src', [])}
    missing = sorted(set(k for r in xrows.values() for k in LWK + ACK if k not in r))
    rows_missing_keys = sum(1 for r in xrows.values() if any(k not in r for k in LWK + ACK))
    o = {'tag': tag, 'gates_json': {k: v for k, v in (meta.get('gates') or {}).items()} if isinstance(meta.get('gates'), dict)
         else meta.get('gates'), 'arms_json': meta.get('arms'), 'hold_s': meta.get('hold_s'),
         'x_rows': len(xrows), 'rows_missing_keys': rows_missing_keys, 'missing_keys': missing[:20],
         'gatearm_lines': len(L['arms']), 'loss_lines': len(L['loss']), 'lossctl_lines': len(L['lossctl']),
         'late_lines': L['late_lines'], 'lwmode': L['lwmode'], 'ovf': L['ovf'], 'torn': L['torn'],
         'death': L['death'], 'quit_line': L['quit_line'], 'other': {k: len(v) for k, v in L['other'].items()},
         'armcopy_mode_lines': sorted(set(L['other'].get('ArmCopy: mode', [])))}
    is_lw4 = tag == 'lw4s131'
    broken = {}
    for n, r in xrows.items():
        for b in identities(r, is_lw4):
            broken[b] = broken.get(b, 0) + 1
    o['identity_broken_rows'] = broken
    allx = list(xrows.values())
    o['log_sums'] = sums(allx, LWK + ACK)
    o['log_H'] = o['log_sums']['ac_cbm_host'] - o['log_sums']['ac_cbm_host_d']
    o['log_guards118'] = sum(o['log_sums'][k] for k in ('ac_cbm_nosnap', 'ac_cbm_bad', 'ac_cbm_left', 'ac_cbm_stale'))
    # loss lines by mode/class/xr
    cnt = {}
    for d in L['loss']:
        k = '%s|%s|%s' % (d.get('mode'), d.get('cls'), d.get('xr'))
        cnt[k] = cnt.get(k, 0) + 1
    o['loss_by_mode_cls_xr'] = cnt
    o['X2'] = sum(1 for d in L['loss'] if d.get('mode') == '2' and d.get('cls') == 'X')
    o['X2u'] = sum(1 for d in L['loss'] if d.get('mode') == '2' and d.get('cls') == 'X' and d.get('xr') == 'unk')
    o['X2n'] = o['X2'] - o['X2u']
    o['IL6_late_le_open'] = o['log_sums']['lw_late'] <= o['log_sums']['lw_open']
    o['IL6_lines_eq_min256H'] = len(L['loss']) == min(256, o['log_H'])
    if o['log_H'] <= 256:
        o['IL6_by_class'] = (sum(1 for d in L['loss'] if d.get('cls') == 'P8') == o['log_sums']['lw_p8'] and
                             sum(1 for d in L['loss'] if d.get('cls') == 'X') == o['log_sums']['lw_x'])
    o['IL7_log'] = o['log_sums']['lw_stamp_pages'] >= o['log_sums']['lw_mark_pages'] + o['log_sums']['lw_sync_pages']
    if L['arms']:
        B = blocks_of(L)
        o['blocks'] = len(B); o['complete'] = sum(1 for b in B if b['complete'])
        o['block_texts'] = sorted(set(b['text'] for b in B))
        per = {}
        win = {}
        bda = {}
        il7_bad = 0
        for b in B:
            a = b['text']
            rs = list(b['pos'].values())
            s = sums(rs, LWK + ACK)
            if s['lw_stamp_pages'] < s['lw_mark_pages'] + s['lw_sync_pages']:
                il7_bad += 1
            acc = per.setdefault(a, {k: 0 for k in LWK + ACK}); acc.setdefault('_rows', 0)
            for k in LWK + ACK: acc[k] += s[k]
            acc['_rows'] += len(rs)
            if b['complete']:
                wr = [b['pos'][p] for p in range(WLO, WHI + 1)]
                sw = sums(wr, LWK + ACK)
                acc2 = win.setdefault(a, {k: 0 for k in LWK + ACK}); acc2.setdefault('_rows', 0)
                for k in LWK + ACK: acc2[k] += sw[k]
                acc2['_rows'] += len(wr)
                bd = mean([g(r, 'bda_scan') for r in wr])
                bda.setdefault(a, []).append(bd)
        for dct in (per, win):
            for a, acc in dct.items():
                acc['H'] = acc['ac_cbm_host'] - acc['ac_cbm_host_d']
                acc['guards118'] = acc['ac_cbm_nosnap'] + acc['ac_cbm_bad'] + acc['ac_cbm_left'] + acc['ac_cbm_stale']
        o['per_arm_all_rows'] = per
        o['per_arm_window'] = win
        o['bda_mean_by_arm'] = {a: mean(v) for a, v in bda.items()}
        o['IL7_blocks_bad'] = il7_bad
        # B2: sum lw_x of arm-2 blocks
        o['B2_all'] = per.get('armcopy=2', {}).get('lw_x', 0)
        o['B2_win'] = win.get('armcopy=2', {}).get('lw_x', 0)
        o['rows_before_first_gatearm'] = sum(1 for n in xrows if n <= L['arms'][0][4])
        o['lw_before_first_gatearm'] = sums([r for n, r in xrows.items() if n <= L['arms'][0][4]], ('lw_x', 'lw_p8', 'ac_cbm_host'))
    else:
        bd = [g(r, 'bda_scan') for r in rows.values() if 'bda_scan' in r and r.get('n', 0) > 1800]
        o['bda_mean_after_1800'] = mean(bd) if bd else None
    return o


def L_outcome(T):
    """rule of item 123(zh)(5) with amendments 126(v), 127(k), 128(g), 129(g), 130(b)(7), 132(b)"""
    reasons = []
    lw1, lw2, lw3, lw4, lw5, lw6 = (T[t] for t in ('lw1s131', 'lw2s131', 'lw3s131', 'lw4s131', 'lw5s131', 'lw6s131'))
    arm2 = lambda o: o['per_arm_all_rows'].get('armcopy=2', {})
    arm4 = lambda o: o['per_arm_all_rows'].get('armcopy=4', {})
    alive = all(arm2(o).get('ac_cmp_pages', 0) > 0 and arm4(o).get('ac_cmp_pages', 0) > 0 for o in (lw1, lw2))
    ident = all(not o['identity_broken_rows'] for o in T.values()) and all(o['IL6_late_le_open'] and o['IL6_lines_eq_min256H'] for o in T.values())
    ctl = {'lw3_p8': lw3['log_sums']['lw_p8'] > 0, 'lw4_c3x': lw4['log_sums']['lw_c3x'] > 0,
           'lw6_open': lw6['log_sums']['lw_open'] > 0,
           'CR': arm2(lw1).get('lw_crx', 0) + lw5['log_sums']['lw_crx'] > 0,
           'CD': (arm2(lw1).get('lw_cdx', 0) + lw5['log_sums']['lw_cdx'] > 0) or arm2(lw2).get('lw_cdx', 0) > 0}
    guards = {'g118_at2': [arm2(lw1).get('guards118'), arm2(lw2).get('guards118'), lw3['log_guards118'],
                           lw5['log_guards118'], lw6['log_guards118']],
              'crp_cdp': [o['log_sums']['lw_crp'] + o['log_sums']['lw_cdp'] for o in T.values()],
              'torn': [o['torn'] for o in T.values()]}
    guards_ok = all(v == 0 for v in guards['g118_at2']) and all(v == 0 for v in guards['crp_cdp']) and all(v == 0 for v in guards['torn'])
    dead = [t for t, o in T.items() if o['death']]
    ovf_void = [t for t in ('lw1s131', 'lw2s131', 'lw5s131') for l in T[t]['ovf'] if re.search(r'kind=(cand|block|gen)$', l)]
    X2n = {t: T[t]['X2n'] for t in ('lw1s131', 'lw2s131', 'lw5s131')}
    X2 = {t: T[t]['X2'] for t in ('lw1s131', 'lw2s131', 'lw5s131')}
    B2 = {'lw1s131': lw1['B2_all'], 'lw2s131': lw2['B2_all'], 'lw5s131': lw5['log_sums']['lw_x']}
    H2 = {'lw1s131': arm2(lw1).get('H'), 'lw2s131': arm2(lw2).get('H'), 'lw5s131': lw5['log_H']}
    P8_2 = arm2(lw1).get('lw_p8', 0) + arm2(lw2).get('lw_p8', 0) + lw5['log_sums']['lw_p8']
    live_all = alive and ident and all(ctl.values()) and guards_ok
    if ovf_void:
        out = 'NOT_RESOLVED'; reasons.append('overflow void %s' % ovf_void)
    elif live_all and any(v > 0 for v in X2n.values()):
        out = 'LW_LOSS'
    elif live_all and all(v == 0 for v in X2.values()) and all(v == 0 for v in B2.values()) and P8_2 >= 1 and not dead:
        out = 'LW_P8'
    else:
        out = 'NOT_RESOLVED'
        if sum(H2.values()) == 0: reasons.append('sum H = 0 at armcopy=2 in lw1/lw2/lw5 - nothing to classify')
        if not live_all: reasons.append('liveness/identity/controls/guards failed')
    return {'outcome': out, 'reasons': reasons, 'alive': alive, 'identities_ok': ident, 'controls': ctl, 'guards': guards,
            'guards_ok': guards_ok, 'dead': dead, 'ovf_void': ovf_void, 'X2': X2, 'X2n': X2n, 'B2': B2, 'H2': H2, 'P8_at2': P8_2}


DD_KEYS = ('dt_us', 'draws', 'cpu_gpu_us', 'gpu_busy_us', 'bda_scan', 'mh_disp_us', 'mh_disp_n', 'dc_dose_n', 'dc_dose_ns',
           'dc_refuse', 'dc_offthr', 'dc_n', 'rt_kpx', 'rt_att')
PH = ('dc_ph_pro_ns', 'dc_ph_prog_ns', 'dc_ph_pre_ns', 'dc_ph_pipe_ns', 'dc_ph_prep_ns', 'dc_ph_bda_ns', 'dc_ph_img_ns',
      'dc_ph_buf_ns', 'dc_ph_ind_ns', 'dc_ph_com_ns', 'dc_ph_emit_ns', 'dc_ph_tail_ns', 'dc_ph_early_ns')


def mode_of(avg):
    return 'NEW' if avg <= 300 else ('OLD' if avg >= 600 else 'BETWEEN')


def dd(tag):
    L = read_log(ROOT + 'log_%s.txt' % tag)
    meta = json.load(open(ROOT + '%s.json' % tag, encoding='utf-8'))
    B = blocks_of(L)
    AB = (0, 1, 1, 0)
    TXT = {0: 'dispceil=0', 1: 'dispceil=1'}
    o = {'tag': tag, 'hold_s': meta.get('hold_s'), 'binary_sha256': meta.get('binary_sha256'),
         'gatearm_lines': len(L['arms']), 'death': L['death'], 'quit_line': L['quit_line'],
         'other': {k: len(v) for k, v in L['other'].items()}, 'dispceil_lines': sorted(set(L['other'].get('DispCeil: mode', [])))}
    o['gatearm_bad'] = [i for i, a in enumerate(L['arms'])
                        if a[3] != i or a[4] != 1800 + 90 * i or a[2] != 2 or a[5] != 90 or a[6] != 1 or a[1] != AB[i % 4] or a[7] != TXT[AB[i % 4]]]
    comp = [b for b in B if b['complete']]
    o['blocks'] = len(B); o['complete'] = len(comp)
    o['complete_by_arm'] = {a: sum(1 for b in comp if b['arm'] == a) for a in (0, 1)}
    o['incomplete'] = [(b['i'], b['arm'], max(b['pos']) if b['pos'] else None) for b in B if not b['complete']]
    for b in comp:
        R = [b['pos'][p] for p in range(WLO, WHI + 1)]
        b['R'] = R
        for k in ('dt_us', 'draws', 'cpu_gpu_us', 'gpu_busy_us', 'bda_scan', 'mh_disp_us', 'mh_disp_n'):
            b[k] = mean([g(r, k) for r in R])
        b['mode'] = mode_of(b['bda_scan'])
        for k in PH + ('dc_prot_ns', 'pl_cs_wait_us', 'pl_cs_hold_us', 'mh_pres_wait_us'):
            b[k] = mean([g(r, k) for r in R])
    o['block_modes'] = {m: sum(1 for b in comp if b['mode'] == m) for m in ('NEW', 'OLD', 'BETWEEN')}
    a0 = [b for b in comp if b['arm'] == 0]; a1 = [b for b in comp if b['arm'] == 1]
    sxy = sxx = 0.0
    for b in a0:
        xs = [g(r, 'draws') for r in b['R']]; ys = [g(r, 'dt_us') for r in b['R']]
        mx, my = mean(xs), mean(ys)
        sxy += sum((u - mx) * (w - my) for u, w in zip(xs, ys)); sxx += sum((u - mx) ** 2 for u in xs)
    beta = sxy / sxx
    o['beta'] = beta
    byi = {b['i']: b for b in comp}
    pairs = []
    for k in range(len(B) // 2):
        b0, b1 = byi.get(2 * k), byi.get(2 * k + 1)
        if b0 is None or b1 is None: continue
        z, t = (b0, b1) if b0['arm'] == 0 else (b1, b0)
        md = z['mode'] if z['mode'] == t['mode'] and z['mode'] != 'BETWEEN' else None
        p = {'k': k, 'mode': md}
        for kk in ('dt_us', 'draws', 'cpu_gpu_us', 'gpu_busy_us', 'mh_disp_us') + PH + ('dc_prot_ns', 'pl_cs_hold_us', 'mh_pres_wait_us'):
            p[kk] = t[kk] - z[kk]
        pairs.append(p)
    o['pairs_total'] = len(pairs); o['pairs_outside_mode'] = sum(1 for p in pairs if p['mode'] is None)
    res = {}; reads = {}
    for md in ('NEW', 'OLD'):
        P = [p for p in pairs if p['mode'] == md]
        r = {'pairs': len(P)}
        if len(P) >= 2:
            d = [p['dt_us'] for p in P]; da = [p['dt_us'] - beta * p['draws'] for p in P]
            r.update({'d': mean(d), 'd_2se': 2 * se(d), 'd_adj': mean(da), 'd_adj_2se': 2 * se(da)})
            for kk in ('draws', 'cpu_gpu_us', 'gpu_busy_us', 'mh_disp_us', 'dc_ph_bda_ns', 'dc_prot_ns', 'dc_ph_buf_ns'):
                v = [p[kk] for p in P]; r['d_' + kk] = mean(v); r['d_' + kk + '_2se'] = 2 * se(v)
        if len(P) >= 10:
            lo = min(r['d'] - r['d_2se'], r['d_adj'] - r['d_adj_2se'])
            hi = max(r['d'] + r['d_2se'], r['d_adj'] + r['d_adj_2se'])
            r['lower'] = lo; r['upper'] = hi
            reads[md] = 'OPEN' if lo >= 500 else ('CLOSED' if hi < 500 else 'NR')
            r['read'] = reads[md]
        else:
            r['read'] = 'DEBT'
        res[md] = r
    o['modes'] = res
    if any(v == 'OPEN' for v in reads.values()):
        T = 'K16_OPEN'
    elif reads and all(v == 'CLOSED' for v in reads.values()):
        T = 'K16_CLOSED'
    else:
        T = 'NOT_RESOLVED'
    kpx = {0: 0, 1: 0}; att = {0: 0, 1: 0}
    for b in comp:
        for r in b['R']:
            if g(r, 'rt_att') == 0: continue
            kpx[b['arm']] += g(r, 'rt_kpx'); att[b['arm']] += g(r, 'rt_att')
    m0 = Fraction(kpx[0], att[0]); m1 = Fraction(kpx[1], att[1])
    o['drs'] = {'m0': float(m0), 'm1': float(m1), 'mixed': 100 * abs(m1 - m0) > m0}
    if o['drs']['mixed']: T = 'NOT_RESOLVED'
    o['T'] = T
    # dose delivery on the window of complete arm-1 blocks; arm-0 zero on window 10..88 of every arm-0 block (item 125(a))
    w1 = [r for b in a1 for r in b['R']]
    o['delivery'] = {'rows': len(w1), 'dose_ns': sum(g(r, 'dc_dose_ns') for r in w1),
                     'mh_disp_us': sum(g(r, 'mh_disp_us') for r in w1)}
    o['delivery']['R'] = o['delivery']['dose_ns'] / (o['delivery']['mh_disp_us'] * 1000)
    w0all = [b['pos'][p] for b in B if b['arm'] == 0 for p in range(WLO, WHI + 1) if p in b['pos']]
    o['arm0_window_dose_n'] = {'rows': len(w0all), 'dose_n': sum(g(r, 'dc_dose_n') for r in w0all)}
    o['arm0_edge_dose_n'] = sum(g(b['pos'][p], 'dc_dose_n') for b in B if b['arm'] == 0 for p in list(range(0, 10)) + [89] if p in b['pos'])
    allrows = list(L['rows'].values())
    o['log_dc_refuse'] = sum(g(r, 'dc_refuse') for r in allrows)
    o['log_dc_offthr'] = sum(g(r, 'dc_offthr') for r in allrows)
    o['dose_per_frame_arm1_us'] = sum(g(r, 'dc_dose_ns') for r in w1) / len(w1) / 1000
    o['slope'] = res['NEW']['d'] / o['dose_per_frame_arm1_us'] if res['NEW'].get('d') is not None else None
    # base (item 123(z)(5), 124(a))
    v0 = [g(r, 'dt_us') for b in a0 for r in b['R']]
    o['base'] = {'rows': len(v0), 'blocks': len(a0), 'mean_dt_us': mean(v0), 'speed_pct': 100 * 16667 / mean(v0),
                 'arm1_mean_dt_us': mean([g(r, 'dt_us') for b in a1 for r in b['R']]),
                 'bda_arm0': mean([g(r, 'bda_scan') for b in a0 for r in b['R']]),
                 'bda_arm1': mean([g(r, 'bda_scan') for b in a1 for r in b['R']])}
    lev = {}
    for arm, bl in ((0, a0), (1, a1)):
        R = [r for b in bl for r in b['R']]
        lev[arm] = {k: mean([g(r, k) for r in R]) for k in ('draws', 'cpu_gpu_us', 'gpu_busy_us', 'mh_disp_us', 'mh_disp_n') + PH + ('dc_prot_ns',)}
    o['levels'] = lev
    # T2 per block: G/S in [-0.005, +0.02], S = sum mh_disp_us*1000, P = sum of 13 phases (window of each block)
    t2 = []
    t1bad = 0
    for b in B:
        R = [b['pos'][p] for p in range(WLO, WHI + 1) if p in b['pos']]
        if not R: continue
        S = sum(g(r, 'mh_disp_us') for r in R) * 1000
        P = sum(g(r, k) for r in R for k in PH)
        if S: t2.append((S - P) / S)
        dn = sum(g(r, 'dc_n') for r in R); mn = sum(g(r, 'mh_disp_n') for r in R)
        if abs(dn - mn) > max(2, 0.005 * mn): t1bad += 1
    o['T2_range'] = [min(t2), max(t2)]; o['T2_bad'] = sum(1 for v in t2 if not (-0.005 <= v <= 0.02)); o['T1_bad_blocks'] = t1bad
    o['max_dt_after_1800'] = max(g(r, 'dt_us') for n, r in L['rows'].items() if n > 1800 and 'dt_us' in r)
    return o


NEED = set(LWK + ACK + DD_KEYS + PH + ('n', 'arm', 'blk', 'dc_prot_ns', 'pl_cs_wait_us', 'pl_cs_hold_us',
                                       'mh_pres_wait_us'))

if __name__ == '__main__':
    what = sys.argv[1]
    if what == 'dd':
        R = dd(sys.argv[2])
    elif what == 'lw':
        R = lw_tag(sys.argv[2])
    elif what == 'Lread':
        T = {t: json.load(open(ROOT + 'audit131/recount_%s.json' % t)) for t in
             ('lw1s131', 'lw2s131', 'lw3s131', 'lw4s131', 'lw5s131', 'lw6s131')}
        R = L_outcome(T)
    print(json.dumps(R, ensure_ascii=True, indent=1, default=str))
