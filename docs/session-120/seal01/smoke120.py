"""Session 120: UNSEALED smoke summary of a r1cen/r2cen/spcen run (draft arithmetic of design120.md; not a scorer).

    python smoke120.py <tag>        (reads C:/kyty/s120/log_<tag>.txt)
Rows: FrameTrace main / -draw / -x joined by n=; arm/blk from the main line; window = positions 10..88 of each block,
draws > 3000.  Prints per-arm window means of the counters the formulas read, the identities, the correctness
counters over ALL rows, and the draft ceilings.
"""
import re
import sys
from collections import defaultdict

TAG = sys.argv[1] if len(sys.argv) > 1 else 'smk120'
PATH = 'C:/kyty/s120/log_%s.txt' % TAG
KV = re.compile(rb'([A-Za-z0-9_]+)=(-?[0-9]+(?:\.[0-9]+)?)')
rows = defaultdict(dict)
order = []
mismatch = defaultdict(int)
with open(PATH, 'rb') as f:
    for line in f:
        for tag in (b'R1CenMismatch', b'R2Mismatch', b'R2MismatchKey', b'SpRtMismatch', b'SpTrMismatch', b'R2Diverge'):
            if tag in line:
                mismatch[tag.decode()] += 1
        for pre, kind in ((b'FrameTrace: ', 'm'), (b'FrameTrace-draw: ', 'd'), (b'FrameTrace-x: ', 'x')):
            i = line.find(pre)
            if i < 0:
                continue
            kv = {k.decode(): float(v) for k, v in KV.findall(line[i + len(pre):])}
            n = int(kv.get('n', -1))
            if kind == 'm':
                order.append(n)
            for k, v in kv.items():
                rows[n][k] = v
            break

by_blk = defaultdict(list)
for n in order:
    r = rows[n]
    if 'blk' in r and 'arm' in r:
        by_blk[int(r['blk'])].append(n)
win = {0: [], 1: []}
allrows = {0: [], 1: []}
for b, ns in by_blk.items():
    for pos, n in enumerate(ns):
        r = rows[n]
        a = int(r['arm'])
        if a not in win:
            continue
        allrows[a].append(r)
        if 10 <= pos <= 88 and r.get('draws', 0) > 3000:
            win[a].append(r)


def S(a, k):
    return sum(r.get(k, 0.0) for r in win[a])


def M(a, k):
    return S(a, k) / max(1, len(win[a]))


def ALL(a, k):
    return sum(r.get(k, 0.0) for r in allrows[a])


P, Mm = 0, 1
print('tag', TAG, 'blocks', len(by_blk), 'window frames P', len(win[P]), 'M', len(win[Mm]))
print('mismatch lines', dict(mismatch))
for a, name in ((P, 'P'), (Mm, 'M')):
    print('--- arm', name, 'dt_us %.1f cpu_gpu_us %.1f draws %.1f bda_scan %.1f' % (
        M(a, 'dt_us'), M(a, 'cpu_gpu_us'), M(a, 'draws'), M(a, 'bda_scan')))
bad_keys = ['r1_w4_bad', 'r1_w8_bad', 'r1_d16_bad', 'r1_w1_bad', 'r1_incl', 'r1_xthr', 'r2_bad', 'r2_bad_key',
            'sp_rt_bad', 'sp_tr_bad', 'sp_rt_race']
print('correctness over ALL rows P:', {k: ALL(P, k) for k in bad_keys})
print('correctness over ALL rows M:', {k: ALL(Mm, k) for k in bad_keys})
w1 = [k for k in rows[order[-1]].keys() if k.startswith('r1_w1_')]
print('w1 control over ALL P rows:', {k: ALL(P, k) for k in w1})
# arming: M window zeros
mz = {k: S(Mm, k) for k in ('r1_hn', 'r1_mn', 'sp_rt_n', 'sp_tr_n', 'r2_rm_sl', 'pl_em_rt_hit_ns')}
print('M-window arm leak (must be 0):', mz, ' r2_stg M', M(Mm, 'r2_stg'))

# identities (window means)
print('R1 identities P: r1_hn %.1f tex_hits %.1f | r1_mn %.1f collide+empty %.1f | r1_sn %.1f stale %.1f | b_texn %.1f sum %.1f' % (
    M(P, 'r1_hn'), M(P, 'tex_hits'), M(P, 'r1_mn'), M(P, 'texmemo_collide') + M(P, 'texmemo_empty'), M(P, 'r1_sn'),
    M(P, 'texmemo_stale'), M(P, 'b_texn'), M(P, 'r1_hn') + M(P, 'r1_mn') + M(P, 'r1_sn') + M(P, 'tnull_hit') + M(P, 'tnull_miss')))
print('R1 samplers: hit_t/hn %.4f mp/mn %.4f rbf_n/texfast_ok %.4f self/(all) %.4f pb_n %.1f self_h_n %.1f' % (
    S(P, 'r1_hit_t') / max(1, S(P, 'r1_hn')), S(P, 'r1_mp') / max(1, S(P, 'r1_mn')),
    S(P, 'r1_rbf_n') / max(1, S(P, 'texfast_ok')),
    (S(P, 'r1_self_h_n') + S(P, 'r1_self_m_n') + S(P, 'r1_self_s_n')) / max(1, S(P, 'r1_hn') + S(P, 'r1_mn') + S(P, 'r1_sn')),
    M(P, 'r1_pb_n'), M(P, 'r1_self_h_n')))
for a, name in ((Mm, 'M'), (P, 'P')):
    print('R2 %s: stg %.1f bl_prep_n %.1f | ns partition %.1f vs 1000*bl_res_us %.1f | slot partition %.1f vs bl_res_n %.1f | rep %.1f cl+mx %.1f' % (
        name, M(a, 'r2_stg'), M(a, 'bl_prep_n'), M(a, 'r2_cl_ns') + M(a, 'r2_mx_ns') + M(a, 'r2_ot_ns'),
        1000 * M(a, 'bl_res_us'), M(a, 'r2_cl_sl') + M(a, 'r2_cl_nul') + M(a, 'r2_mx_sl') + M(a, 'r2_ot_sl'),
        M(a, 'bl_res_n'), M(a, 'r2_rep'), M(a, 'r2_cl') + M(a, 'r2_mx')))
print('SP P: sp_rt_n %.1f pl_em_n %.1f would %.1f | reasons %.1f | sp_tr_n %.1f would %.1f reasons %.1f' % (
    M(P, 'sp_rt_n'), M(P, 'pl_em_n'), M(P, 'sp_rt_would'),
    M(P, 'sp_rt_would') + sum(M(P, 'sp_rt_x_' + x) for x in ('memo', 'cfg', 'dclr', 'meta', 'ids', 'live', 'ser', 'bound', 'dsmp', 'pass')),
    M(P, 'sp_tr_n'), M(P, 'sp_tr_would'),
    M(P, 'sp_tr_would') + sum(M(P, 'sp_tr_x_' + x) for x in ('big', 'memo', 'meta', 'shape', 'ser', 'flags'))))
print('SP P reasons rt:', {x: round(M(P, 'sp_rt_x_' + x), 1) for x in ('memo', 'cfg', 'dclr', 'meta', 'ids', 'live', 'ser', 'bound', 'dsmp', 'pass')})
print('SP P reasons tr:', {x: round(M(P, 'sp_tr_x_' + x), 1) for x in ('big', 'memo', 'meta', 'shape', 'ser', 'flags')})

# ---- draft ceilings (window sums; all per frame, us)
NfP, NfM = max(1, len(win[P])), max(1, len(win[Mm]))
t_hit = S(P, 'r1_hit_ns') / max(1, S(P, 'r1_hit_t'))
t_miss = S(P, 'r1_mp_ns') / max(1, S(P, 'r1_mp'))
t_fast = S(P, 'r1_rbf_ns') / max(1, S(P, 'r1_rbf_n'))
t_ham = S(P, 'r1_ham_ns') / max(1, S(P, 'r1_ham_t'))
look = S(P, 'r1_hn') + S(P, 'r1_mn') + S(P, 'r1_sn')
print('R1 t_hit %.1f t_miss %.1f t_fast %.1f t_ham %.1f (ns)' % (t_hit, t_miss, t_fast, t_ham))
best = None
for T in ('w4', 'w8', 'd16'):
    q, p = S(P, 'r1_%s_q' % T), S(P, 'r1_%s_p' % T)
    W = q * S(P, 'r1_mn') / max(1, S(P, 'r1_mn') - S(P, 'r1_mp'))
    tT = S(P, 'r1_%s_pns' % T) / max(1, p)
    A = W * (tT - t_hit)
    L = 0 if T == 'd16' else S(P, 'r1_%s_lose' % T) * max(0, min(tT, t_miss) - t_hit)
    R = S(P, 'r1_%s_rbns' % T) - S(P, 'r1_%s_rb' % T) * t_fast
    E = max(0, t_ham - t_hit) * S(P, 'r1_am_n') * W / max(1, S(P, 'r1_mn'))
    Pp = 0 if T == 'd16' else look * max(0, (S(P, 'r1_%s_pb_ns' % T) - S(P, 'r1_pb0_ns')) / max(1, S(P, 'r1_pb_n')))
    C = (A - L + R + E - Pp) / NfP / 1000
    print('R1 %s: W/f %.1f t_T %.1f A %.1f L %.1f R %.1f E %.1f P %.1f -> C %.1f us (without E %.1f)' % (
        T, W / NfP, tT, A / NfP / 1000, L / NfP / 1000, R / NfP / 1000, E / NfP / 1000, Pp / NfP / 1000, C,
        C - E / NfP / 1000))
    best = C if best is None else max(best, C)
# R2 from M
z = S(Mm, 'r2_nul_ns') / max(1, S(Mm, 'r2_nul_n'))
Sx, Zx, Lx = M(Mm, 'r2_cl_sl'), M(Mm, 'r2_cl_nul'), M(Mm, 'r2_cl_lod')
Su = S(Mm, 'r2_cl_sl') - S(Mm, 'r2_s_cl_sl')
Zu = S(Mm, 'r2_cl_nul') - S(Mm, 'r2_s_cl_nul')
Tstar = (S(Mm, 'r2_cl_ns') - S(Mm, 'r2_s_cl_ns')) / NfM * (Sx + Zx) / max(1e-9, (Su + Zu) / NfM)
wrep = S(Mm, 'r2_wr_ns') / max(1, S(Mm, 'r2_wr_n'))
woth = S(Mm, 'r2_wo_ns') / max(1, S(Mm, 'r2_wo_n'))
nonrep = M(Mm, 'r2_stg') - M(Mm, 'r2_noimg') - M(Mm, 'r2_big') - M(Mm, 'r2_odd') - M(Mm, 'r2_rep')
W2 = (wrep - z) * M(Mm, 'r2_rep') + (woth - z) * nonrep
ST = (S(Mm, 'r2_st_ns') / max(1, S(Mm, 'r2_st_n')) - z) * nonrep
B, Blo, Tp, Pc, N0, LS, Rr, Atr = 8.49, 5.0, 12.0, 15.08, 2.0, 5.0, 2.0, 1.2
Cup = (Tstar - Blo * (Sx + Zx) + Rr * (Sx + Zx) - W2 - ST) / 1000
Cpt = (Tstar - ((B + Tp) * Sx + (B + N0) * Zx + LS * Lx) - W2 - ST - Atr * (2 * Sx + Zx)) / 1000
Clo = (Tstar - ((B + Tp + Pc) * Sx + (B + N0) * Zx + LS * Lx) - W2 - ST - Atr * (2 * Sx + Zx)) / 1000
pc = Tstar / max(1e-9, Sx + Zx)
print('R2 (M): S %.1f Z %.1f L %.1f clean %.1f of stg %.1f | z %.2f w_rep %.2f w_oth %.2f | T* %.1f us p_c %.1f ns | W %.1f ST %.1f us' % (
    Sx, Zx, Lx, M(Mm, 'r2_cl'), M(Mm, 'r2_stg'), z, wrep, woth, Tstar / 1000, pc, W2 / 1000, ST / 1000))
print('R2 C_up %.1f C_pt %.1f C_lo %.1f us | package R_pt %.1f R_up %.1f' % (Cup, Cpt, Clo, best + Cpt, best + Cup))
# SP
zP = S(P, 'r2_nul_ns') / max(1, S(P, 'r2_nul_n'))
NA = (S(P, 'pl_em_rt_hit_ns') - S(P, 'pl_em_spchk_ns') - S(P, 'sp_rt_rep_ns') - S(P, 'sp_rt_rec_ns')) / NfP / 1000
NB = (S(P, 'bl_tr_hit_ns') - S(P, 'sp_tr_chk_ns') - S(P, 'sp_tr_rep_ns') - S(P, 'sp_tr_rec_ns')) / NfP / 1000
dA = M(Mm, 'pl_em_rt_ns') - M(P, 'pl_em_rt_ns')
dB = 1000 * (M(Mm, 'bl_tr_us') - M(P, 'bl_tr_us')) + zP * M(P, 'sp_tr_n')
Zadd = zP * (2 * M(P, 'sp_rt_n') + M(P, 'sp_rt_rec') + 2 * M(P, 'sp_tr_n')) / 1000
Nplus = NA + NB + Zadd + max(0, dA) * M(P, 'pl_em_rt_hit_ns') / max(1, M(P, 'pl_em_rt_ns')) / 1000 + \
    max(0, dB) * M(P, 'bl_tr_hit_ns') / max(1, M(P, 'sp_tr_loop_ns')) / 1000
print('SP: G_A %.1f G_B %.1f | N_A %.1f N_B %.1f N %.1f | z %.2f Z %.1f dA %.1f dB %.1f (ns, unclamped) | N+ %.1f us' % (
    M(P, 'pl_em_rt_hit_ns') / 1000, M(P, 'bl_tr_hit_ns') / 1000, NA, NB, NA + NB, zP, Zadd, dA, dB, Nplus))
print('price P-M: dt_us %.1f cpu_gpu_us %.1f' % (M(P, 'dt_us') - M(Mm, 'dt_us'), M(P, 'cpu_gpu_us') - M(Mm, 'cpu_gpu_us')))
