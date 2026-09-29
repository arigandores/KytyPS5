# Session 132 audit (HPP-187, Session Auditor): independent recount of the numbers on which the two selection
# verdicts of s132 rest (ROADMAP s122 items 136 and 139): step 1 (K16 selection, levers132.md; census of dd131 arm 0)
# and step 1K (K5 selection, levers132k.md; levels of spk118 / cen120 arm M and dd131 arm 0).
# No code shared with step1/agg.py, step1/reg.py, step1k/agg1k.py, lead/rc136.py, lead/rc1k.py (not imported);
# block logic is a port of my own audit131/recount131.py.
# Blocks ONLY by 'GateArm:' lines. Row n belongs to the last GateArm with F < n (row n = F of the next GateArm is
# position 89 of the leaving block). Position p = n - F - 1. Window 10..88 inclusive (item 55(b)); complete block =
# all rows p 10..88 present AND the next GateArm at F + 90.
import hashlib, json, math, re, sys

KV = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')
GA = re.compile(rb'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
WLO, WHI = 10, 88

K_DD = ('dt_us', 'draws', 'dispatches', 'bda_scan', 'mh_disp_us', 'mh_disp_n', 'dc_n', 'dc_dose_n',
        'dc_ph_pro_ns', 'dc_ph_prog_ns', 'dc_ph_pre_ns', 'dc_ph_pipe_ns', 'dc_ph_prep_ns', 'dc_ph_bda_ns', 'dc_ph_img_ns',
        'dc_ph_buf_ns', 'dc_ph_ind_ns', 'dc_ph_com_ns', 'dc_ph_emit_ns', 'dc_ph_tail_ns', 'dc_ph_early_ns',
        'dc_prot_ns', 'dc_prot_n', 'dc_bda_n', 'dc_ind_n', 'dc_early_n',
        'prot_gpu_ro_ns', 'prot_gpu_ro_n', 'prot_gpu_ro_pages', 'pb2_vp', 'pb2_vp_adj', 'pb2_vp_near',
        'fw_win_armed', 'faults', 'fault_us', 'stg_pool_b', 'stg_pool_ns', 'stg_pool_n', 'acopy_wait_us',
        'pl_cs_hold_us', 'sync_up_kb', 'pb_wait_gpu_us', 'ob_stream_kb', 'bb_n', 'ob_n',
        'mh_bind_us', 'mh_draws', 'b_texn', 'bp_mask', 'texfast_ok', 'texfast_no', 'bpage_hit', 'bpage_miss',
        'smp_miss', 'srt_miss', 'bda_n', 'bda_hit')
K_1K = ('pl_em_com_ns', 'bl_tr_us', 'bl_wr_us', 'bl_em_us', 'rec_pack', 'rec_pack_cs', 'rec_direct', 'ds_ring_n',
        'cpu_record_us', 'rec_spin_us', 'bl_cmt_n', 'mh_bind_us', 'bl_prep_us', 'bl_res_us', 'bl_smp_us', 'bl_sd_us',
        'bl_buf_us', 'bl_img_us', 'bda_scan', 'dt_us', 'bb_n', 'b_texn', 'draws', 'dispatches', 'mh_draws',
        'px_draw_bind_us', 'c_bind', 'd_bind')
NEED = set(K_DD + K_1K + ('n',))


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def read_log(path):
    rows, arms = {}, []
    with open(path, 'rb') as f:
        for raw in f:
            s = raw.lstrip()
            if s.startswith(b'FrameTrace'):
                sp = s.find(b': ')
                d = {k.decode(): int(v) for k, v in KV.findall(s[sp + 2:]) if k.decode() in NEED}
                n = d.get('n')
                if n is None:
                    continue
                rows.setdefault(n, {}).update(d)
            elif s.startswith(b'GateArm: '):
                m = GA.match(s.rstrip())
                if not m:
                    raise SystemExit('unparsed GateArm %r' % s[:200])
                arms.append(tuple(int(m.group(i)) for i in range(1, 7)) + (m.group(7).decode().strip(),))
    return rows, arms


def blocks_of(rows, arms):
    out = []
    for i, a in enumerate(arms):
        F = a[3]
        Fn = arms[i + 1][3] if i + 1 < len(arms) else None
        pos = {}
        hi = Fn if Fn is not None else F + 200
        for n in range(F + 1, hi + 1):
            if n in rows:
                pos[n - F - 1] = rows[n]
        comp = Fn is not None and Fn == F + 90 and all(p in pos for p in range(WLO, WHI + 1))
        out.append({'i': i, 'arm': a[0], 'F': F, 'text': a[6], 'pos': pos, 'complete': comp})
    return out


def g(r, k):
    return r.get(k, 0)


def mean(v):
    return sum(v) / len(v)


def sd(v):
    m = mean(v)
    return math.sqrt(sum((a - m) ** 2 for a in v) / (len(v) - 1))


def pct(v, q):
    s = sorted(v)
    # linear interpolation (numpy default)
    x = (len(s) - 1) * q
    lo = int(math.floor(x)); hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (x - lo)


def corr(x, y):
    mx, my = mean(x), mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x); syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy)


def ols1(x, y):
    mx, my = mean(x), mean(y)
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    return b, my - b * mx


def ols2(x1, x2, y):
    """y = a + b1 x1 + b2 x2 by centred normal equations (2x2, Cramer)"""
    m1, m2, my = mean(x1), mean(x2), mean(y)
    s11 = sum((a - m1) ** 2 for a in x1); s22 = sum((b - m2) ** 2 for b in x2)
    s12 = sum((a - m1) * (b - m2) for a, b in zip(x1, x2))
    s1y = sum((a - m1) * (c - my) for a, c in zip(x1, y)); s2y = sum((b - m2) * (c - my) for b, c in zip(x2, y))
    det = s11 * s22 - s12 * s12
    b1 = (s1y * s22 - s2y * s12) / det; b2 = (s2y * s11 - s1y * s12) / det
    return b1, b2, my - b1 * m1 - b2 * m2


def window_rows(B, text):
    comp = [b for b in B if b['complete'] and b['text'] == text]
    return comp, [b['pos'][p] for b in comp for p in range(WLO, WHI + 1)]


def dd131(path):
    rows, arms = read_log(path)
    B = blocks_of(rows, arms)
    comp0, R = window_rows(B, 'dispceil=0')
    comp1, R1 = window_rows(B, 'dispceil=1')
    o = {'log': path, 'sha256': sha(path), 'gatearm': len(arms), 'blocks_arm0': len(comp0), 'rows_arm0': len(R),
         'blocks_arm1': len(comp1), 'rows_arm1': len(R1),
         'rows_missing_key': {k: sum(1 for r in R if k not in r) for k in K_DD}}
    o['mean_us'] = {k: mean([g(r, k) for r in R]) / (1000.0 if k.endswith('_ns') else 1.0) for k in K_DD}
    o['mean_raw'] = {k: mean([g(r, k) for r in R]) for k in K_DD}
    prot = [g(r, 'dc_prot_ns') for r in R]
    o['bda_on_prot'] = dict(zip(('slope', 'icpt_us'), (lambda b, a: (b, a / 1000))(*ols1(prot, [g(r, 'dc_ph_bda_ns') for r in R]))))
    o['bda_on_prot']['corr'] = corr(prot, [g(r, 'dc_ph_bda_ns') for r in R])
    for ph in ('buf', 'img', 'prep'):
        y = [g(r, 'dc_ph_%s_ns' % ph) for r in R]
        o['%s_on_prot' % ph] = {'corr': corr(prot, y), 'slope': ols1(prot, y)[0]}
    b1, b2, a = ols2([g(r, 'prot_gpu_ro_n') for r in R], [g(r, 'prot_gpu_ro_pages') for r in R], [g(r, 'prot_gpu_ro_ns') for r in R])
    o['ro_cost'] = {'ns_per_call': b1, 'ns_per_page': b2, 'icpt_us': a / 1000}
    pc = [g(r, 'dc_prot_ns') / g(r, 'dc_prot_n') / 1000 for r in R if g(r, 'dc_prot_n') > 0]
    o['dc_prot_per_call_us'] = {'rows': len(pc), 'mean_of_rows': mean(pc), 'median': pct(pc, 0.5), 'p90': pct(pc, 0.9),
                                'ratio_of_sums': sum(prot) / sum(g(r, 'dc_prot_n') for r in R) / 1000}
    o['ro_pages_per_call'] = sum(g(r, 'prot_gpu_ro_pages') for r in R) / sum(g(r, 'prot_gpu_ro_n') for r in R)
    o['dc_bda_n_minmax'] = [min(g(r, 'dc_bda_n') for r in R), max(g(r, 'dc_bda_n') for r in R)]
    buf = [g(r, 'dc_ph_buf_ns') / 1000 for r in R]
    o['buf'] = {'mean': mean(buf), 'sd': sd(buf), 'p10': pct(buf, 0.1), 'p90': pct(buf, 0.9)}
    for k in ('pb_wait_gpu_us', 'stg_pool_n', 'ob_stream_kb', 'bb_n', 'ob_n'):
        o['buf']['corr_' + k] = corr([g(r, k) for r in R], buf)
    o['arm0_bl_pl_em_nonzero_rows'] = None  # filled by caller with raw scan (keys outside NEED)
    return o


def level_1k(path, text):
    rows, arms = read_log(path)
    B = blocks_of(rows, arms)
    comp, R = window_rows(B, text)
    o = {'log': path, 'sha256': sha(path), 'text': text, 'gatearm': len(arms), 'blocks': len(comp), 'rows': len(R),
         'incomplete_or_gap_blocks': sum(1 for b in B if not b['complete']),
         'rows_missing_key': {k: sum(1 for r in R if k not in r) for k in K_1K}}
    m = {k: mean([g(r, k) for r in R]) for k in K_1K}
    m['pl_em_com_us'] = m['pl_em_com_ns'] / 1000
    m['em_rest'] = m['pl_em_com_us'] - m['bl_tr_us'] - m['bl_wr_us'] - m['bl_em_us']
    m['bind_split'] = m['bl_prep_us'] + m['bl_buf_us'] + m['bl_img_us']
    m['bind_rest'] = m['mh_bind_us'] - m['bind_split']
    m['bind_rest_pct'] = 100 * m['bind_rest'] / m['mh_bind_us']
    m['prep_rest'] = m['bl_prep_us'] - m['bl_res_us'] - m['bl_smp_us'] - m['bl_sd_us']
    m['ns_per_commit'] = {k: 1000 * m[k] / m['bl_cmt_n'] for k in ('pl_em_com_us', 'bl_tr_us', 'bl_wr_us', 'bl_em_us', 'em_rest')}
    m['bl_buf_ns_per_slot'] = 1000 * m['bl_buf_us'] / m['bb_n']
    m['shares_pct'] = {k: 100 * m[k] / m['pl_em_com_us'] for k in ('bl_tr_us', 'bl_wr_us', 'bl_em_us', 'em_rest')}
    m['wr_plus_em'] = m['bl_wr_us'] + m['bl_em_us']
    m['rec_pack_total'] = m['rec_pack'] + m['rec_pack_cs']
    m['record_work_us'] = m['cpu_record_us'] - m['rec_spin_us']
    m['spin_share_pct'] = 100 * m['rec_spin_us'] / m['cpu_record_us']
    o['mean'] = m
    return o


def raw_nonzero(path, prefixes, text):
    """count window rows of the given arm text where ANY key starting with a prefix is non-zero (keys outside NEED)"""
    pat = re.compile(rb'\b(' + b'|'.join(re.escape(p.encode()) for p in prefixes) + rb')[A-Za-z0-9_]*=(-?\d+)')
    rows, arms = {}, []
    with open(path, 'rb') as f:
        for raw in f:
            s = raw.lstrip()
            if s.startswith(b'GateArm: '):
                m = GA.match(s.rstrip()); arms.append(tuple(int(m.group(i)) for i in range(1, 7)) + (m.group(7).decode().strip(),))
            elif s.startswith(b'FrameTrace'):
                mn = re.search(rb' n=(\d+)', s)
                if not mn:
                    continue
                n = int(mn.group(1))
                nz = any(int(v) != 0 for _, v in pat.findall(s))
                seen = bool(pat.search(s))
                r = rows.setdefault(n, {'nz': False, 'seen': False})
                r['nz'] |= nz; r['seen'] |= seen; r['n'] = n
    B = blocks_of(rows, arms)
    comp, R = window_rows(B, text)
    return {'rows': len(R), 'rows_with_keys': sum(1 for r in R if r['seen']), 'rows_nonzero': sum(1 for r in R if r['nz'])}


if __name__ == '__main__':
    what = sys.argv[1]
    if what == 'dd131':
        o = dd131('C:/kyty/s131/log_dd131.txt')
        o['arm0_bl_pl_em'] = raw_nonzero('C:/kyty/s131/log_dd131.txt', ('bl_', 'pl_em_'), 'dispceil=0')
    elif what == 'spk118':
        o = level_1k('C:/kyty/s118/log_spk118.txt', 'spine=0 slicecen=0 takelap=1 bindlap=1 pathlap=1 mutsite=1')
    elif what == 'cen120':
        o = level_1k('C:/kyty/s120/log_cen120.txt', 'r1cen=0 r2cen=1 spcen=0 bindlap=1 pathlap=1 mutsite=1')
    print(json.dumps(o, ensure_ascii=True, indent=1))
