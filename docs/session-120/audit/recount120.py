# Session 120 audit: INDEPENDENT RECOUNT of cen120 (and the unsealed smoke smk120).
# Written from design120.md sections 2-4 only; shares no code with rpk120.py / spc120.py / smoke120.py.
# usage: python recount120.py <log> [--boot N] [--json out.json]
import re, sys, json, math, random, statistics

NS = 1000.0
BAR = 500.0
B, B_LO, TP, PP, N0, LS, RRESET, ATR = 8.49, 5.0, 12.0, 15.08, 2.0, 5.0, 2.0, 1.2
WIN_LO, WIN_HI = 10, 88          # positions inclusive
DRAWS_MIN = 3000
PERIOD = 90
P_TEXT = 'r1cen=2 r2cen=2 spcen=1 bindlap=1 pathlap=1 mutsite=1'
M_TEXT = 'r1cen=0 r2cen=1 spcen=0 bindlap=1 pathlap=1 mutsite=1'

KV = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')
HEAD = re.compile(rb'^FrameTrace(|-draw|-x): n=(\d+)')
XKEEP = re.compile(r'^(r1_|r2_|sp_|pl_em|bl_|texmemo_|tnull_|mh_emit)')
MAINKEEP = {'dt_us', 'cpu_gpu_us', 'draws', 'arm', 'blk'}
DRAWKEEP = {'tex_hits', 'b_texn', 'bda_scan'}
LINE_TAGS = [b'R1CenMismatch', b'R2Mismatch', b'R2Diverge', b'SpRtMismatch', b'SpTrMismatch',
             b'AsyncPipelines: skipped draw', b'GpuHangAbort', b'GpuWaitSlow', b'ErrorDeviceLost',
             b'--- Error ---', b'--- Fatal Error ---', b'std::terminate', b'abort()']


def parse(path):
    rows = {'': {}, '-draw': {}, '-x': {}}
    dup = {'': 0, '-draw': 0, '-x': 0}
    alltot = {}
    tags = {t.decode(): [] for t in LINE_TAGS}
    arms = []
    last_main = None
    with open(path, 'rb') as f:
        for ln in f:
            for t in LINE_TAGS:
                if t in ln:
                    tags[t.decode()].append(last_main)
            if ln.startswith(b'GateArm:'):
                d = dict((k.decode(), int(v)) for k, v in KV.findall(ln.split(b' text=')[0]))
                d['text'] = ln.split(b' text=', 1)[1].strip().decode()
                arms.append(d)
                continue
            m = HEAD.match(ln)
            if not m:
                continue
            kind = m.group(1).decode()
            n = int(m.group(2))
            kv = KV.findall(ln, m.end())
            if kind == '':
                keep = {k.decode(): int(v) for k, v in kv if k.decode() in MAINKEEP}
                last_main = n
            elif kind == '-draw':
                keep = {k.decode(): int(v) for k, v in kv if k.decode() in DRAWKEEP}
            else:
                keep = {}
                for k, v in kv:
                    k = k.decode()
                    if XKEEP.match(k):
                        keep[k] = int(v)
                        alltot[k] = alltot.get(k, 0) + int(v)
            if n in rows[kind]:
                dup[kind] += 1
            rows[kind][n] = keep
    return rows, dup, alltot, tags, arms


def build(rows, arms):
    """Blocks from GateArm lines: block b rows n = F+1 .. F+90, window positions 10..88 -> n = F+11 .. F+89."""
    blocks = []
    for g in arms:
        F = g['frame']
        arm = 0 if g['text'] == P_TEXT else (1 if g['text'] == M_TEXT else -1)
        assert arm == g['arm'], g
        full = []
        for pos in range(PERIOD):
            n = F + 1 + pos
            mr = rows[''].get(n)
            full.append(n if mr is not None else None)
        win = []
        label_bad = 0
        for pos in range(WIN_LO, WIN_HI + 1):
            n = F + 1 + pos
            mr, dr, xr = rows[''].get(n), rows['-draw'].get(n), rows['-x'].get(n)
            if mr is None or dr is None or xr is None:
                win = None
                break
            if mr['arm'] != arm or mr['blk'] != g['block']:
                label_bad += 1
            r = dict(mr); r.update(dr); r.update(xr); r['n'] = n
            win.append(r)
        # label check over all 90 rows present
        lab_all = sum(1 for n in full if n is not None and (rows[''][n]['arm'] != arm or rows[''][n]['blk'] != g['block']))
        blocks.append(dict(b=g['block'], F=F, arm=arm, win=win, label_bad=label_bad, lab_all=lab_all,
                           nrows=sum(1 for n in full if n is not None)))
    return blocks


class Agg(dict):
    """Sums of every numeric field over a set of rows, plus the row count (len)."""
    def __init__(self, rows=None):
        super().__init__()
        self.nf = 0
        for r in rows or []:
            self.add_row(r)

    def add_row(self, r):
        self.nf += 1
        for k, v in r.items():
            if k != 'n':
                self[k] = self.get(k, 0) + v

    def __add__(self, o):
        a = Agg()
        a.nf = self.nf + o.nf
        for k in set(self) | set(o):
            a[k] = self.get(k, 0) + o.get(k, 0)
        return a

    def __len__(self):
        return self.nf


def agg(rows):
    return rows if isinstance(rows, Agg) else Agg(rows)


def S(rows, k):
    rows = agg(rows)
    return float(rows[k])


def dv(a, b):
    return None if b == 0 else a / b


def r1(rows):
    rows = agg(rows)
    nf = len(rows)
    s = lambda k: S(rows, k)
    t_hit = dv(s('r1_hit_ns'), s('r1_hit_t'))
    t_miss = dv(s('r1_mp_ns'), s('r1_mp'))
    t_fast = dv(s('r1_rbf_ns'), s('r1_rbf_n'))
    t_ham = dv(s('r1_ham_ns'), s('r1_ham_t'))
    mn, mp = s('r1_mn'), s('r1_mp')
    look = s('r1_hn') + s('r1_mn') + s('r1_sn')
    out = dict(nf=nf, t_hit=t_hit, t_miss=t_miss, t_fast=t_fast, t_ham=t_ham, lookups=look / nf)
    for T in ('w4', 'w8', 'd16'):
        W = s('r1_%s_q' % T) * mn / (mn - mp)
        tT = s('r1_%s_pns' % T) / s('r1_%s_p' % T)
        A = W * (tT - t_hit)
        L = 0.0 if T == 'd16' else s('r1_%s_lose' % T) * max(0.0, min(tT, t_miss) - t_hit)
        R = s('r1_%s_rbns' % T) - s('r1_%s_rb' % T) * t_fast
        E = max(0.0, t_ham - t_hit) * s('r1_am_n') * W / mn
        P = 0.0 if T == 'd16' else look * max(0.0, (s('r1_%s_pb_ns' % T) - s('r1_pb0_ns')) / s('r1_pb_n'))
        f = nf * NS
        out[T] = dict(W=W / nf, tT=tT, A=A / f, L=L / f, R=R / f, E=E / f, P=P / f,
                      C=(A - L + R + E - P) / f, CnoE=(A - L + R - P) / f)
    out['argmax'] = max(('w4', 'w8', 'd16'), key=lambda T: out[T]['C'])
    out['C_R1'] = out[out['argmax']]['C']
    return out


def r2(mrows, prows=None):
    mrows = agg(mrows)
    prows = agg(prows) if prows else None
    nf = len(mrows)
    s = lambda k: S(mrows, k)
    z = s('r2_nul_ns') / s('r2_nul_n')
    wrep = s('r2_wr_ns') / s('r2_wr_n')
    woth = s('r2_wo_ns') / s('r2_wo_n')
    st = s('r2_st_ns') / s('r2_st_n')
    Sl, Zl, Ll = s('r2_cl_sl'), s('r2_cl_nul'), s('r2_cl_lod')
    rep = s('r2_rep')
    nonrep = s('r2_stg') - s('r2_noimg') - s('r2_big') - s('r2_odd') - rep
    W = (wrep - z) * rep + (woth - z) * nonrep
    ST = (st - z) * nonrep
    Su, Zu = Sl - s('r2_s_cl_sl'), Zl - s('r2_s_cl_nul')
    Tst = (s('r2_cl_ns') - s('r2_s_cl_ns')) * (Sl + Zl) / (Su + Zu)
    Cup = Tst - B_LO * (Sl + Zl) + RRESET * (Sl + Zl) - W - ST
    Cpt = Tst - ((B + TP) * Sl + (B + N0) * Zl + LS * Ll) - W - ST - ATR * (2 * Sl + Zl)
    Clo = Tst - ((B + TP + PP) * Sl + (B + N0) * Zl + LS * Ll) - W - ST - ATR * (2 * Sl + Zl)
    pc = Tst / (Sl + Zl)
    Cext = Cpt + s('r2_mx_eq') * (pc - B - TP)
    f = nf * NS
    out = dict(nf=nf, z=z, wrep=wrep, woth=woth, st=st, S=Sl / nf, Z=Zl / nf, L=Ll / nf, Tstar=Tst / f,
               W=W / f, ST=ST / f, pc=pc, C_up=Cup / f, C_pt=Cpt / f, C_lo=Clo / f, C_ext=Cext / f)
    if prows:
        sp = lambda k: S(prows, k)
        zp = sp('r2_nul_ns') / sp('r2_nul_n')
        per = (sp('r2_rm_ns') - zp * sp('r2_rm_n')) / sp('r2_rm_sl')
        out['C_rp'] = (per * (Sl + Zl) - W - ST) / f
        out['C_rp_zM'] = ((sp('r2_rm_ns') - z * sp('r2_rm_n')) / sp('r2_rm_sl') * (Sl + Zl) - W - ST) / f
    return out


def spc(prows, mrows, zbar=None):
    prows, mrows = agg(prows), agg(mrows)
    nfp, nfm = len(prows), len(mrows)
    p = lambda k: S(prows, k)
    m = lambda k: S(mrows, k)
    if zbar is None:
        zbar = p('r2_nul_ns') / p('r2_nul_n')
    NA = (p('pl_em_rt_hit_ns') - p('pl_em_spchk_ns') - p('sp_rt_rep_ns') - p('sp_rt_rec_ns')) / nfp / NS
    NB = (p('bl_tr_hit_ns') - p('sp_tr_chk_ns') - p('sp_tr_rep_ns') - p('sp_tr_rec_ns')) / nfp / NS
    ZA = zbar * (2 * p('sp_rt_n') + p('sp_rt_rec')) / nfp / NS
    ZB = zbar * 2 * p('sp_tr_n') / nfp / NS
    dA = m('pl_em_rt_ns') / nfm - p('pl_em_rt_ns') / nfp            # ns a frame, unclamped
    dB = 1000 * (m('bl_tr_us') / nfm - p('bl_tr_us') / nfp)
    dBp = dB + zbar * p('sp_tr_n') / nfp
    rA = p('pl_em_rt_hit_ns') / p('pl_em_rt_ns')
    rB = p('bl_tr_hit_ns') / p('sp_tr_loop_ns')
    TA = max(0.0, dA) * rA / NS
    TB = max(0.0, dBp) * rB / NS
    TB_old = max(0.0, dB) * rB / NS
    return dict(zbar=zbar, G_A=p('pl_em_rt_hit_ns') / nfp / NS, G_B=p('bl_tr_hit_ns') / nfp / NS,
                N_A=NA, N_B=NB, N=NA + NB, Z_A=ZA, Z_B=ZB, Z=ZA + ZB, dA=dA, dB=dB, dBp=dBp, rA=rA, rB=rB,
                TA=TA, TB=TB, NA_up=NA + ZA + TA, NB_up=NB + ZB + TB, N_up=NA + NB + ZA + ZB + TA + TB,
                N_up_noZ=NA + NB + TA + TB, N_up_dB=NA + NB + ZA + ZB + TA + TB_old,
                price_dt=p('dt_us') / nfp - m('dt_us') / nfm, price_cpu=p('cpu_gpu_us') / nfp - m('cpu_gpu_us') / nfm)


def se2(v):
    v = [x for x in v]
    return 2 * statistics.stdev(v) / math.sqrt(len(v))


def verdict(point, upper, s2):
    if point >= BAR:
        return 'OPEN'
    if upper + s2 < BAR:
        return 'CLOSED'
    return 'NOT_OPENED'


def main():
    path = sys.argv[1]
    nboot = int(sys.argv[sys.argv.index('--boot') + 1]) if '--boot' in sys.argv else 0
    rows, dup, alltot, tags, arms = parse(path)
    blocks = build(rows, arms)
    out = dict(log=path, dups=dup, n_main=len(rows['']), n_x=len(rows['-x']), gatearms=len(arms))
    out['blocks'] = [(b['b'], b['arm'], b['F'], b['nrows'], None if b['win'] is None else len(b['win']),
                      b['label_bad'], b['lab_all']) for b in blocks]
    done = {b['b']: b for b in blocks if b['win'] is not None}
    pairs = [(k, k + 1) for k in range(0, len(blocks), 2) if k in done and k + 1 in done]
    out['pairs'] = len(pairs)
    for (a, c) in pairs:
        assert done[a]['arm'] != done[c]['arm']
    est = {k: Agg([r for r in done[k]['win'] if r['draws'] > DRAWS_MIN]) for k in done}
    pP = [a if done[a]['arm'] == 0 else c for a, c in pairs]
    pM = [c if done[a]['arm'] == 0 else a for a, c in pairs]
    P = sum((est[k] for k in pP), Agg())
    M = sum((est[k] for k in pM), Agg())
    Pall = sum((Agg(done[k]['win']) for k in pP), Agg())
    Mall = sum((Agg(done[k]['win']) for k in pM), Agg())
    out['frames'] = dict(P=len(P), M=len(M), Pwin=len(Pall), Mwin=len(Mall))
    unpaired = [k for k in done if not any(k in pr for pr in pairs)]
    out['unpaired_complete'] = unpaired
    # correctness over ALL rows
    keys = ['r1_w4_bad', 'r1_w8_bad', 'r1_d16_bad', 'r1_incl', 'r1_xthr', 'r2_bad', 'r2_bad_key',
            'sp_rt_bad', 'sp_tr_bad', 'sp_rt_race', 'sp_rt_would', 'sp_rt_nt', 'r1_reset'] + \
           sorted(k for k in alltot if k.startswith('r1_w1_'))
    out['all_rows'] = {k: alltot.get(k) for k in keys}
    out['line_tags'] = {k: len(v) for k, v in tags.items()}
    out['skipped_draw_frames'] = tags['AsyncPipelines: skipped draw'][:20]
    # where do r1_reset come from
    rs = [(n, x['r1_reset']) for n, x in rows['-x'].items() if x.get('r1_reset')]
    out['r1_reset_rows'] = rs[:10]
    out['r1_reset_rows_n'] = len(rs)
    # M-arm window zeros
    mz = ['r1_hn', 'r1_mn', 'r1_w4_q', 'r1_w8_q', 'r1_d16_q', 'sp_rt_n', 'sp_tr_n', 'sp_rt_would', 'sp_tr_would',
          'pl_em_rt_hit_ns', 'bl_tr_hit_ns', 'pl_em_spchk_ns', 'r2_rm_sl', 'r2_rm_ns', 'r2_rm_n']
    out['M_zeros'] = {k: S(Mall, k) for k in mz}
    # P-arm arming
    out['P_alive'] = {k: S(Pall, k) / len(Pall) for k in ('r1_hn', 'r2_rm_sl', 'sp_rt_n', 'sp_tr_n', 'r2_stg')}
    # identities (window sums per block, max |residual|)
    def idres(blks, left, right):
        worst = 0
        for k in blks:
            w = Agg(done[k]['win'])
            res = sum(S(w, a) for a in left) - sum(S(w, a) for a in right)
            worst = max(worst, abs(res))
        return worst
    idents = {
        'r1_hn-tex_hits': (pP, ['r1_hn'], ['tex_hits']),
        'r1_mn-(collide+empty)': (pP, ['r1_mn'], ['texmemo_collide', 'texmemo_empty']),
        'r1_sn-stale': (pP, ['r1_sn'], ['texmemo_stale']),
        'b_texn-(hn+mn+sn+tnull)': (pP, ['b_texn'], ['r1_hn', 'r1_mn', 'r1_sn', 'tnull_hit', 'tnull_miss']),
        'r1_pb_n-self_h_n': (pP, ['r1_pb_n'], ['r1_self_h_n']),
        'r2_stg-bl_prep_n P': (pP, ['r2_stg'], ['bl_prep_n']),
        'r2_stg-bl_prep_n M': (pM, ['r2_stg'], ['bl_prep_n']),
        'r2_slots-bl_res_n M': (pM, ['r2_cl_sl', 'r2_cl_nul', 'r2_mx_sl', 'r2_ot_sl'], ['bl_res_n']),
        'r2_rep-(cl+mx) M': (pM, ['r2_rep'], ['r2_cl', 'r2_mx']),
        'r2_wr+wo-nul M': (pM, ['r2_wr_n', 'r2_wo_n'], ['r2_nul_n']),
        'sp_rt_n-pl_em_n P': (pP, ['sp_rt_n'], ['pl_em_n']),
        'sp_rt_n-(would+x_*) P': (pP, ['sp_rt_n'], ['sp_rt_would'] + sorted(k for k in P if k.startswith('sp_rt_x_'))),
        'sp_tr_n-(would+x_*) P': (pP, ['sp_tr_n'], ['sp_tr_would'] + sorted(k for k in P if k.startswith('sp_tr_x_'))),
    }
    out['identities_max_abs_block_residual'] = {k: idres(*v) for k, v in idents.items()}
    # samplers
    out['samplers'] = dict(hit_t_over_hn=S(P, 'r1_hit_t') / S(P, 'r1_hn'), mp_over_mn=S(P, 'r1_mp') / S(P, 'r1_mn'),
                           rbf_over_texfast_ok=None, nul_over_img_stages_M=S(M, 'r2_nul_n') / (S(M, 'r2_stg') - S(M, 'r2_noimg') - S(M, 'r2_big')))
    # point values
    R1 = r1(P)
    R2 = r2(M, P)
    SP = spc(P, M)
    out['R1'], out['R2'], out['SP'] = R1, R2, SP
    out['R_pt'] = R1['C_R1'] + R2['C_pt']
    out['R_up'] = R1['C_R1'] + R2['C_up']
    # per pair
    pp = []
    for a, c in pairs:
        kp = a if done[a]['arm'] == 0 else c
        km = c if kp == a else a
        r1p = r1(est[kp]); r2p = r2(est[km]); spg = spc(est[kp], est[km], SP['zbar']); spo = spc(est[kp], est[km])
        pp.append(dict(pair=(a, c), C_R1_fixed=r1p[R1['argmax']]['C'], C_R1_max=r1p['C_R1'],
                       C_up=r2p['C_up'], C_pt=r2p['C_pt'],
                       N=spg['N'], N_A=spg['N_A'], N_B=spg['N_B'], N_up=spg['N_up'], NA_up=spg['NA_up'],
                       NB_up=spg['NB_up'], N_up_ownz=spo['N_up'], price=spg['price_dt'], price_cpu=spg['price_cpu']))
    col = lambda k: [x[k] for x in pp]
    se = {}
    se['R1'] = se2(col('C_R1_fixed'))
    se['R1_max'] = se2(col('C_R1_max'))
    se['R2_up'] = se2(col('C_up'))
    se['R2_pt'] = se2(col('C_pt'))
    se['R_up'] = se2([x['C_R1_fixed'] + x['C_up'] for x in pp])
    se['R_pt'] = se2([x['C_R1_fixed'] + x['C_pt'] for x in pp])
    for k in ('N', 'N_A', 'N_B', 'N_up', 'NA_up', 'NB_up', 'N_up_ownz', 'price', 'price_cpu'):
        se[k] = se2(col(k))
    out['se2'] = se
    out['price_pairmean'] = statistics.mean(col('price'))
    out['price_cpu_pairmean'] = statistics.mean(col('price_cpu'))
    out['verdicts'] = dict(
        R1=verdict(R1['C_R1'], R1['C_R1'], se['R1']),
        R2=verdict(R2['C_pt'], R2['C_up'], se['R2_up']),
        R=verdict(out['R_pt'], out['R_up'], se['R_up']),
        A=verdict(SP['N_A'], SP['NA_up'], se['NA_up']),
        B=verdict(SP['N_B'], SP['NB_up'], se['NB_up']),
        SP=verdict(SP['N'], SP['N_up'], se['N_up']))
    # bootstrap over pairs (pooled estimator recomputed on resampled pair sets)
    if nboot:
        rnd = random.Random(120)
        k = len(pairs)
        res = dict(C_R1=[], R_pt=[], R_up=[], N=[], N_up=[], N_up_se=[], NA=[], NA_up_se=[], w8_C=[], R1_arg=[])
        for _ in range(nboot):
            idx = [rnd.randrange(k) for _ in range(k)]
            Pb = sum((est[pP[i]] for i in idx), Agg())
            Mb = sum((est[pM[i]] for i in idx), Agg())
            a = r1(Pb); b2 = r2(Mb); c = spc(Pb, Mb)
            res['C_R1'].append(a['C_R1']); res['R1_arg'].append(a['argmax']); res['w8_C'].append(a['w8']['C'])
            res['R_pt'].append(a['C_R1'] + b2['C_pt']); res['R_up'].append(a['C_R1'] + b2['C_up'])
            res['N'].append(c['N']); res['N_up'].append(c['N_up']); res['NA'].append(c['N_A'])
            s_up = se2([pp[i]['N_up'] for i in idx])
            s_aup = se2([pp[i]['NA_up'] for i in idx])
            res['N_up_se'].append(c['N_up'] + s_up)
            res['NA_up_se'].append(c['NA_up'] + s_aup)
        def q(v, p):
            v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]
        bs = {}
        for key, v in res.items():
            if key == 'R1_arg':
                bs[key] = {t: v.count(t) for t in set(v)}
                continue
            bs[key] = dict(mean=statistics.mean(v), sd=statistics.stdev(v), q025=q(v, 0.025), q975=q(v, 0.975),
                           lt500=sum(1 for x in v if x < BAR) / len(v), ge500=sum(1 for x in v if x >= BAR) / len(v))
        out['bootstrap'] = dict(n=nboot, seed=120, **bs)
    out['per_pair'] = pp
    js = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    if js:
        with open(js, 'w') as f:
            json.dump(out, f, indent=1, default=str)
    brief = {k: v for k, v in out.items() if k not in ('per_pair', 'blocks')}
    print(json.dumps(brief, indent=1, default=str))


if __name__ == '__main__':
    main()
