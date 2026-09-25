"""Robustness of the sealed G2 (no decision weight): alternative estimators for the level terms and one-term swings.
Uses the own parser recount119.py.  The sealed estimator is the median of block means (session-104 section 3)."""
import statistics
import recount119 as R

runs = {}
for tag in ('sh119', 'mut119'):
    rows, lines, dups, other = R.parse('C:/kyty/s119/log_%s.txt' % tag)
    sel, pairs, excl, bad_idx, bad_arm, allb = R.population(rows)
    runs[tag] = (rows, sel, pairs)
g = R.g_terms(runs)
_, sel_s, pairs_s = runs['sh119']
_, sel_m, pairs_m = runs['mut119']


def lvl_mean(sel, arm, fn):
    return statistics.mean(R.bmean(v, fn) for b, v in sel.items() if R.ABBA[b % 4] == arm)


def G(cpu_net, S_ctx, spine, T2, f=R.F2):
    return cpu_net - (S_ctx + f * (cpu_net - S_ctx)) - spine - T2


amut = lambda r: r['a_mut_us']
draws = lambda r: r['draws']
base = dict(cpu_net=g['cpu_net'], S_ctx=g['S_ctx'], spine=g['spine'], T2=g['T2'])
print('sealed G2 %.1f  (X = cpu_net - S_ctx = %.1f)' % (G(**base), g['cpu_net'] - g['S_ctx']))

# 1. levels as means of block means
cn = lvl_mean(sel_s, 0, R.cpu_net)
sraw = lvl_mean(sel_m, 1, amut)
tin = lvl_mean(sel_m, 1, lambda r: 5 * r['pl_em_n'] + 3 * (r['pl_prog_n'] + r['pl_pipe_n'] + r['pl_cs_n']) + r['a_mut_n'])
erec = lvl_mean(sel_m, 1, lambda r: r['pl_em_rec_ns'] / 1000)
sp = max(lvl_mean(sel_m, 0, lambda r: r['da_walk_us'] - r['da_queue_us']), R.SPINE_FLOOR)
sctx = sraw - max(g['P_mw'], 0) - R.C_TS * tin / 1000 - (erec + R.W_E)
print('levels as MEANS: cpu_net %.1f S_raw %.1f S_ctx %.1f spine %.1f -> G2 %.1f' % (cn, sraw, sctx, sp, G(cn, sctx, sp, g['T2'])))

# 2. S_raw from the paired design: arm-0 level + mean paired difference of a_mut_us
dm, dse, n = R.delta(sel_m, pairs_m, amut)
sraw_p = g['S_lo'] + dm
sctx_p = sraw_p - max(g['P_mw'], 0) - g['dI'] - g['E_move']
print('S_raw = S_lo + d a_mut (%.1f +- %.1f 2SE) = %.1f -> S_ctx %.1f -> G2 %.1f' % (dm, 2 * dse, sraw_p, sctx_p,
      G(g['cpu_net'], sctx_p, g['spine'], g['T2'])))

# 3. S_raw rescaled per draw to the draw level of sh arm 0 (the cpu_net population)
d_m1, d_s0 = R.level(sel_m, 1, draws), R.level(sel_s, 0, draws)
sraw_d = g['S_raw'] * d_s0 / d_m1
sctx_d = sraw_d - max(g['P_mw'], 0) - g['dI'] - g['E_move']
print('draw levels: mut arm1 %.1f, mut arm0 %.1f, sh arm0 %.1f; S_raw rescaled %.1f -> S_ctx %.1f -> G2 %.1f'
      % (d_m1, R.level(sel_m, 0, draws), d_s0, sraw_d, sctx_d, G(g['cpu_net'], sctx_d, g['spine'], g['T2'])))

# 4. the whole cross-run instrument price inside S (instead of dI only)
sctx_x = g['S_ctx'] - (g['xrun_price'] - g['dI'])
print('all of the cross-run price %.1f inside S: S_ctx %.1f -> G2 %.1f' % (g['xrun_price'], sctx_x,
      G(g['cpu_net'], sctx_x, g['spine'], g['T2'])))

# 5. one-term break-even values (what each term would need to be for the central G2 to reach 3 000)
X = g['cpu_net'] - g['S_ctx']
need = R.BAR + g['spine'] + g['T2']
print('break-even: f <= %.4f (1-f >= %.4f); spine <= %.1f; T2 <= %.1f; X >= %.1f (S_ctx <= %.1f, i.e. E_move >= %.1f, W_E >= %.1f)'
      % (1 - need / X, need / X, g['spine'] - (R.BAR - g['G2']), g['T2'] - (R.BAR - g['G2']), need / (1 - R.F2),
         g['cpu_net'] - need / (1 - R.F2), g['S_now'] - (g['cpu_net'] - need / (1 - R.F2)),
         g['S_now'] - (g['cpu_net'] - need / (1 - R.F2)) - g['E_rec']))
print('G2 at f = 0.5 (ideal half cut): %.1f' % G(g['cpu_net'], g['S_ctx'], g['spine'], g['T2'], 0.5))
print('G2 with the spine at its floor 959: %.1f; with no spine: %.1f' % (G(g['cpu_net'], g['S_ctx'], 959.0, g['T2']),
      G(g['cpu_net'], g['S_ctx'], 0.0, g['T2'])))
print('G2 with T2 - 2SE: %.1f; with T2 on dt: %.1f' % (G(g['cpu_net'], g['S_ctx'], g['spine'], g['T2'] - g['T2_2SE']),
      G(g['cpu_net'], g['S_ctx'], g['spine'], g['T2_dt'])))
print('G2 with E_move^ (E_rec + E_com) only: %.1f' % G(g['cpu_net'], g['S_now'] - g['E_move^'], g['spine'], g['T2']))
print('G2 with the ceiling S_ctx^ and central T2: %.1f; central S_ctx and ceiling T2^: %.1f'
      % (G(g['cpu_net'], g['S_ctx^'], g['spine'], g['T2']), G(g['cpu_net'], g['S_ctx'], g['spine'], g['T2^'])))
