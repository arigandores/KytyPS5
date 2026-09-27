"""Independent recount of the sealed census run cen124 of session 124 (audit, step 9, HPP-64).

Written by the Session Auditor from the TEXT of pred/01_cen124.md (sections 2, 4, 5 G4/G5/G7/G8/G10) only; shares no
code with cen124.py, smk124.py, ref124.py or skc123.py (none is imported or read). The W0+ recount re-parses
C:/kyty/s123/log_sky123.txt with the block rule of the s123 audit (recount123.py, the auditor's own code).

Usage: python recount124.py <log_cen124.txt> <cen124.json> <log_sky123.txt>
"""
import json
import math
import re
import sys

FIELD = re.compile(rb'(\w+)=(-?\d+)')
MAIN, DRAW, X = b'FrameTrace: ', b'FrameTrace-draw: ', b'FrameTrace-x: '
KINDS = (MAIN, DRAW, X)


def parse(path, want_arms=False):
    rows = {k: {} for k in KINDS}
    dup = {k: 0 for k in KINDS}
    arms, skipped = [], []
    with open(path, 'rb') as f:
        for line in f:
            if want_arms and line.startswith(b'GateArm:'):
                arms.append(dict((a.decode(), b.decode()) for a, b in re.findall(rb'(\w+)=(\S+)', line)))
                continue
            if b'AsyncPipelines: skipped draw' in line:
                skipped.append(line[:200])
            for k in KINDS:
                if line.startswith(k):
                    d = {a.decode(): int(b) for a, b in FIELD.findall(line)}
                    n = d.get('n')
                    if n is None:
                        break
                    if n in rows[k]:
                        dup[k] += 1
                    rows[k][n] = d
                    break
    return rows, dup, arms, skipped


def mean(a):
    return sum(a) / len(a)


def sd(a):
    m = mean(a)
    return math.sqrt(sum((x - m) ** 2 for x in a) / (len(a) - 1))


def w0_from_sky123(path):
    """W0 = mean over arm-0 blocks of the block mean of gw_proc_ns/1000, positions 10..87; population = complete pairs."""
    rows, dup, arms, _ = parse(path, want_arms=True)
    M, D, Xr = (rows[k] for k in KINDS)
    start, period = int(arms[0]['frame']), int(arms[0]['period'])
    fr = lambda b, lo, hi: [start + 1 + period * b + p for p in range(lo, hi + 1)]

    def complete(b):
        return all(n in M and n in D and n in Xr and M[n].get('blk') == b and M[n].get('arm') == int(arms[b]['arm'])
                   for n in fr(b, 10, 87))
    pairs = []
    for k in range(len(arms) // 2):
        b0, b1 = 2 * k, 2 * k + 1
        if complete(b0) and complete(b1) and not any(M[n]['dt_us'] >= 500000 for b in (b0, b1) for n in fr(b, 0, 89)
                                                   if n in M):
            pairs.append((b0, b1))
    a0 = [b for p in pairs for b in p if int(arms[b]['arm']) == 0]
    bm = [mean([Xr[n]['gw_proc_ns'] / 1000.0 for n in fr(b, 10, 87)]) for b in a0]
    w0 = mean(bm)
    se = sd(bm) / math.sqrt(len(bm))
    kpx = sum(Xr[n]['rt_kpx'] for b in a0 for n in fr(b, 10, 87))
    att = sum(Xr[n]['rt_att'] for b in a0 for n in fr(b, 10, 87))
    return dict(pairs=len(pairs), blocks=len(a0), W0=w0, SE=se, W0p=w0 + 2 * se, g8base=kpx / att, kpx=kpx, att=att)


def main():
    logp, jsp, skyp = sys.argv[1:4]
    js = json.load(open(jsp, encoding='utf-8'))
    att = js['attempts']
    stable = att[0]['stable_frame']
    rows, dup, _, skipped = parse(logp)
    M, D, Xr = (rows[k] for k in KINDS)
    last = max(M)
    f0 = stable + 10
    win = list(range(f0, last))                     # F0 .. last-1
    comp = [n for n in win if n in M and n in D and n in Xr]
    print('attempts', len(att), 'outcome', att[0]['outcome'], 'stable_frame', stable, 'hold_s', js['hold_s'])
    print('rows main/draw/x', len(M), len(D), len(Xr), 'dups', [dup[k] for k in KINDS], 'last main n', last)
    print('window frames %d..%d: %d frames, %d complete' % (f0, last - 1, len(win), len(comp)))
    assert len(comp) == len(win)
    nb = len(win) // 90
    blocks = [win[90 * i:90 * i + 90] for i in range(nb)]
    print('blocks of 90: %d, tail %d' % (nb, len(win) - 90 * nb))
    S = lambda f, src=Xr, ns=win: sum(src[n][f] for n in ns)

    # --- G7 BDA regime
    bm = [mean([D[n]['bda_scan'] for n in b]) for b in blocks]
    band = lambda v: 'NEW' if v <= 300 else ('OLD' if v >= 600 else 'MIXED')
    print('G7 bda_scan window mean %.1f; blocks min %.1f max %.1f; bands %s' % (
        mean([D[n]['bda_scan'] for n in win]), min(bm), max(bm), sorted(set(band(v) for v in bm))))

    # --- G8 DRS (base recounted from sky123 below)
    r = S('rt_kpx') / S('rt_att')

    # --- core sums
    f = S('skc3_f'); d = S('skc3_d')
    cdf, cf = S('skc_c_df'), S('skc_c_f')
    print('sum skc3_f %d (>= 1600: %s); sum skc3_d %d; c_df/c_f %.4f' % (f, f >= 1600, d, cdf / cf))

    # --- tau_ctx, SE over blocks
    tin_ns, tin_n = S('skc3_tin_ns'), S('skc3_tin_n')
    tau = tin_ns / tin_n
    bv = [sum(Xr[n]['skc3_tin_ns'] for n in b) / sum(Xr[n]['skc3_tin_n'] for n in b)
          for b in blocks if sum(Xr[n]['skc3_tin_n'] for n in b) > 0]
    se = sd(bv) / math.sqrt(len(bv))
    taup = tau + 2 * se
    print('tau_ctx %.4f ns, blocks with probe %d, SE %.4f, tau+ %.4f, 3tau+ %.4f; block range %.3f..%.3f' % (
        tau, len(bv), se, taup, 3 * taup, min(bv), max(bv)))
    finrows = [n for n in win if Xr[n]['skc3_f'] > 0]
    calmax = max(Xr[n]['skc3_cal_ns'] / Xr[n]['skc3_cal_n'] for n in finrows if Xr[n]['skc3_cal_n'] > 0)
    print('G10: rows with finalization %d, without cal %d, without tin %d, max tau^ %.2f ns, sum tin_n %d' % (
        len(finrows), sum(1 for n in finrows if Xr[n]['skc3_cal_n'] == 0),
        sum(1 for n in finrows if Xr[n]['skc3_tin_n'] == 0), calmax, tin_n))

    # --- shares
    wd, pd, gc, gpn = S('skc3_wd_ns'), S('skc3_pd_n'), S('skc3_gc_ns'), S('skc3_gc_pn')
    out = {}
    for X_, fl, wf, pf in (('L', 'skc3_free_l', 'skc3_wfree_l_ns', 'skc3_pfree_l_n'),
                           ('b', 'skc3_free_b', 'skc3_wfree_b_ns', 'skc3_pfree_b_n')):
        fn = S(fl) / d
        num0, pnum = S(wf) + gc, S(pf) + gpn
        den0, pden = wd + gc, pd + gpn
        ft = {}
        for lab, t in (('0', 0.0), ('tau+', taup), ('3tau+', 3 * taup)):
            den = den0 - t * pden
            ft[lab] = (num0 - t * pnum) / den if den > 0 else float('nan')
            ft['den_' + lab] = den
        ftp = min(1.0, max(ft['0'], ft['tau+'], ft['3tau+']))
        fx = max(fn, ftp)
        tzero = den0 / pden
        out[X_] = dict(fn=fn, ft=ft, ftp=ftp, fx=fx, num0=num0, pnum=pnum, den0=den0, pden=pden, tzero=tzero)
        print('%s: f_n %.5f f_t(0) %.5f f_t(tau+) %.5f f_t(3tau+) %.5f; den(ms) %.3f / %.3f / %.3f; f_x+ %.5f;'
              ' den=0 at tau %.2f ns' % (X_, fn, ft['0'], ft['tau+'], ft['3tau+'], ft['den_0'] / 1e6,
                                        ft['den_tau+'] / 1e6, ft['den_3tau+'] / 1e6, fx, tzero))

    sky = w0_from_sky123(skyp)
    print('sky123: pairs %d, arm-0 blocks %d, W0 %.6f, SE %.6f, W0+ %.6f; G8 base %d/%d = %.6f' % (
        sky['pairs'], sky['blocks'], sky['W0'], sky['SE'], sky['W0p'], sky['kpx'], sky['att'], sky['g8base']))
    print('G8 rt_kpx/rt_att %.3f vs base %.6f: %.5f' % (r, sky['g8base'], r / sky['g8base'] - 1))
    q = max(0.5, cdf / cf)
    Mp = sky['W0p'] * q
    L = out['L']
    U = Mp * L['fx']
    print('READING: q+ %.4f, M+ %.1f us, U = %.2f us -> %s' % (q, Mp, U, 'CLOSED' if U < 500 else 'PROTOTYPE_125'))
    print('rows: U_b %.2f; U by the letter 11517 x f_x^L+ %.2f' % (Mp * out['b']['fx'], 11517 * L['fx']))

    # --- sensitivity (audit rows, not the verdict)
    fx_crit = 500.0 / Mp
    # tau at which f_t^L(tau) = fx_crit: (num0 - t pnum) = fx (den0 - t pden)
    tcrit = (L['num0'] - fx_crit * L['den0']) / (L['pnum'] - fx_crit * L['pden'])
    print('SENS: f_x needed for U=500: %.5f (x%.2f of f_x^L+); tau where f_t^L reaches it: %.2f ns (= %.2f x tau+,'
          ' = %.2f x tau_ctx)' % (fx_crit, fx_crit / L['fx'], tcrit, tcrit / taup, tcrit / tau))
    print('SENS: U with W0 (no 2SE) %.2f; U with q = c_df/c_f %.2f; U_b/U_L %.3f' % (
        sky['W0'] * q * L['fx'], sky['W0p'] * (cdf / cf) * L['fx'], out['b']['fx'] / L['fx']))
    # halves of the window
    h = len(win) // 2
    for lab, ns in (('first half', win[:h]), ('second half', win[h:])):
        s = lambda k: sum(Xr[n][k] for n in ns)
        tt = s('skc3_tin_ns') / s('skc3_tin_n')
        num = s('skc3_wfree_l_ns') + s('skc3_gc_ns') - 3 * taup * (s('skc3_pfree_l_n') + s('skc3_gc_pn'))
        den = s('skc3_wd_ns') + s('skc3_gc_ns') - 3 * taup * (s('skc3_pd_n') + s('skc3_gc_pn'))
        print('SENS %s: f_n^L %.5f f_t^L(3tau+) %.5f tau_ctx %.3f' % (lab, s('skc3_free_l') / s('skc3_d'),
                                                                     num / den, tt))
    # per-block f_t^L(3tau+) spread
    fb = []
    for b in blocks:
        s = lambda k: sum(Xr[n][k] for n in b)
        num = s('skc3_wfree_l_ns') + s('skc3_gc_ns') - 3 * taup * (s('skc3_pfree_l_n') + s('skc3_gc_pn'))
        den = s('skc3_wd_ns') + s('skc3_gc_ns') - 3 * taup * (s('skc3_pd_n') + s('skc3_gc_pn'))
        fb.append(num / den)
    print('SENS per-block f_t^L(3tau+): mean %.5f sd %.5f min %.5f max %.5f; 2SE %.5f' % (
        mean(fb), sd(fb), min(fb), max(fb), 2 * sd(fb) / math.sqrt(len(fb))))

    # --- G4/G5 selected checks
    t1_log = sum(Xr[n]['skc_sd'] - Xr[n]['skc_c_dd'] - Xr[n]['skc_keepd'] - Xr[n]['skc_zerod'] for n in Xr)
    t1_win = sum(Xr[n]['skc_sd'] - Xr[n]['skc_c_dd'] - Xr[n]['skc_keepd'] - Xr[n]['skc_zerod'] for n in win)
    alt = sum(1 for i in range(len(win) - 1) if Xr[win[i]]['skc_c_df'] >= 1 and Xr[win[i + 1]]['skc_c_df'] >= 1)
    i7 = [n for n in win if Xr[n]['skc3_f'] == 1 and Xr[n]['skc3_pollf'] == 1]
    i7bad = sum(1 for n in i7 if Xr[n]['skc3_free_l'] or Xr[n]['skc3_free_b'])
    print('T1 log %d window %d; alternation %d/%d; I7prime rows %d bad %d; skc_on-window %d' % (
        t1_log, t1_win, alt, len(win) - 1, len(i7), i7bad, S('skc_on') - len(win)))
    zeros = ('skc_bad skc_xthr skc_refuse skc_w_xthr skc3_xthr skc3_bad skc3_orphan skc3_nocause skc3_lnb skc3_lsup '
             'skc3_pc_bad skc3_x1c_bad skc3_fr_ns skc3_fr_pn skc_skipf skc_skipd skc_mark skc_mark_miss skc_held '
             'skc_gc_hold skc_bgc_hold').split()
    nz = {z: sum(Xr[n].get(z, 0) for n in Xr) for z in zeros}
    print('G5 nonzero:', {k: v for k, v in nz.items() if v} or 'none (all %d zero)' % len(zeros))
    p2i = S('skc3_x1c_n') - S('skc3_x1c_sub') - S('skc3_x1c_clr') - S('skc3_x1c_ovr')
    print('P1 pc_n %d pc_bad %d; P2 x1c_n %d independent %d (%.4f); P4 s_next %d cl_poll %d pollf %d dkeep %d' % (
        S('skc3_pc_n'), S('skc3_pc_bad'), S('skc3_x1c_n'), p2i, p2i / S('skc3_x1c_n'), S('skc3_s_next'),
        S('skc3_cl_poll'), S('skc3_pollf'), S('skc_lod_dkeep')))
    big = max((M[n]['dt_us'], n) for n in M if n >= f0)
    print('G2 largest dt_us from F0 %s; gclk_pin window %d; skipped-draw lines %d' % (big, S('gclk_pin'),
                                                                                      len(skipped)))
    print('mean dt_us (not a speed) %.1f' % mean([M[n]['dt_us'] for n in win]))


if __name__ == '__main__':
    main()
