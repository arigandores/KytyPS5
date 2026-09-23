from recount import *

mut = load('mut104b')
sh = load('sh104')
K = ['cpu_net_us', 'dt_us', 'a_mut_us', 't_in', 'pl_em_rec_usx', 'pl_em_com_usx', 'spine_us', 'sh_push_us',
     'spine_pref_us', 'pl_prog_hold_us', 'mh_prog_us']
rm = analyse(mut, K)
rs = analyse(sh, K[:2] + ['spine_us', 'sh_push_us'])
L = lambda r, k, a: r['levels'][k][a]
D = lambda r, k: r['diffs'][k]
F, BAR, CTS, WE = 0.30, 3000.0, 3.96, 675.455 + 440.120
cpu_net = L(rs, 'cpu_net_us', 0)
S_lo, S_raw = L(rm, 'a_mut_us', 0), L(rm, 'a_mut_us', 1)
P, P2 = D(rm, 'cpu_net_us')[0], D(rm, 'cpu_net_us')[1]
T_in = L(rm, 't_in', 1)
dI = CTS * T_in / 1000
E_rec, E_com = L(rm, 'pl_em_rec_usx', 1), L(rm, 'pl_em_com_usx', 1)
spine = L(rs, 'spine_us', 0)
T4, T42 = D(rs, 'cpu_net_us')[0], D(rs, 'cpu_net_us')[1]
sh_push = L(rs, 'sh_push_us', 1)
S_now = S_raw - max(P, 0) - dI
S_ctx = S_now - (E_rec + WE)
G = cpu_net - (S_ctx + F * (cpu_net - S_ctx)) - spine - T4
S_nowh = S_raw - max(P + P2, 0) - 2 * dI
S_ctxh = S_nowh - (E_rec + E_com)
T4h = max(0.0, T4 - T42 - sh_push)
Gh = cpu_net - (S_ctxh + F * (cpu_net - S_ctxh)) - spine - T4h
print('cpu_net %.4f S_lo %.4f S_raw %.4f P_mw %.4f 2SE %.4f T_in %.4f dI %.4f' % (cpu_net, S_lo, S_raw, P, P2, T_in, dI))
print('E_rec %.4f E_com %.4f spine %.4f T4 %.4f 2SE %.4f sh_push %.4f' % (E_rec, E_com, spine, T4, T42, sh_push))
print('CENTRAL S_now %.4f S_ctx %.4f G %.4f  -> %s' % (S_now, S_ctx, G, 'PROCEEDS' if G >= BAR else 'CLOSED'))
print('CEILING S_now^ %.4f S_ctx^ %.4f T4^ %.4f G^ %.4f' % (S_nowh, S_ctxh, T4h, Gh))
print('G f=0.39 %.4f' % (cpu_net - (S_ctx + 0.39 * (cpu_net - S_ctx)) - spine - T4))
print('kill T4 %.4f' % ((1 - F) * (cpu_net - S_ctx) - spine - BAR))
# area of arm 0, ratio of sums over kept rows
def area(d, r):
    kp = at = 0
    for b in r['used']:
        if r['arm_of'][b] == 0:
            for n in r['elig'][b]:
                kp += d['merged'][n]['rt_kpx']; at += d['merged'][n]['rt_att']
    return kp / at
am, ash = area(mut, rm), area(sh, rs)
print('area arm0 mut %.4f sh %.4f rel %.4f %%' % (am, ash, 100 * (ash / am - 1)))
print('xrun instrument price %.4f' % (L(rm, 'cpu_net_us', 0) - cpu_net))
# robustness: spine from mut arm0, sensitivity if S from mut104 uses cpu_net of mut arm 0 (same-run)
cpu_net_mut = L(rm, 'cpu_net_us', 0)
G_same = cpu_net_mut - (S_ctx + F * (cpu_net_mut - S_ctx)) - spine - T4
print('G using mut104b arm-0 cpu_net (same run as S) %.4f' % G_same)
# mut104b arming identities (levels)
K2 = ['mw_n', 'mw_expect', 'a_hold_n', 'mh_n', 'mh_disp_n', 'pl_prog_n', 'pl_cs_n', 'dispatches', 'pl_em_n', 'mh_draws',
      'pl_pref_n', 'mh_emit_us']
r2 = analyse(mut, K2)
for a in (0, 1):
    lv = {k: r2['levels'][k][a] for k in K2}
    print('arm', a, 'mw/expect-1 %.5f' % (lv['mw_n'] / lv['mw_expect'] - 1 if lv['mw_expect'] else float('nan')),
          'a_hold_n/(mh_n+mh_disp_n)-1 %.5f' % (lv['a_hold_n'] / (lv['mh_n'] + lv['mh_disp_n']) - 1),
          'pl_prog_n/mh_n-1 %.5f' % (lv['pl_prog_n'] / lv['mh_n'] - 1),
          'pl_cs_n/disp-1 %.5f' % (lv['pl_cs_n'] / lv['dispatches'] - 1),
          'pl_em_n/mh_draws-1 %.5f' % (lv['pl_em_n'] / lv['mh_draws'] - 1), 'pl_pref_n', lv['pl_pref_n'])
# emit chain closure per arm: sum pl_em_* ns /1000 / mh_emit_us, as ratio of kept-row sums
em_keys = [k for k in mut['merged'][5000] if k.startswith('pl_em_') and k.endswith('_ns')]
print('emit keys', em_keys)
for a in (0, 1):
    s_em = sum(kept_sum(mut, r2, a, k) for k in em_keys) / 1000.0
    print('arm', a, 'emit closure (sum ratio) %.4f' % (s_em / kept_sum(mut, r2, a, 'mh_emit_us')))
