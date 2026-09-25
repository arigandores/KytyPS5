"""Recount the two UNSEALED smokes smk119s / smk119m with the same own parser (recount119.py), draft geometry
(schedule from frame 900, first kept frame >= 1200), to check the numbers disclosed in pred/01_g2_119.md."""
import recount119 as R

R.START, R.FIRST_KEPT_MIN = 900, 1200
runs = {}
for key, tag in (('sh119', 'smk119s'), ('mut119', 'smk119m')):
    rows, lines, dups, other = R.parse('C:/kyty/s119/log_%s.txt' % tag)
    sel, pairs, excl, bad_idx, bad_arm, allb = R.population(rows)
    runs[key] = (rows, sel, pairs)
    print('%s: rows %d selected blocks %d pairs %d excluded %s bad idx %d arm mismatches %d workers %s'
          % (tag, len(rows), len(sel), len(pairs), excl, bad_idx, bad_arm, other['worker']))
g = R.g_terms(runs)
for k in ('cpu_net', 'T2', 'T2_2SE', 'T2_dt', 'T2_dt_2SE', 'S_lo', 'S_raw', 'P_mw', 'P_mw_2SE', 'spine_proxy_mut0',
          'spine_proxy_sh0', 'E_rec', 'E_com', 'S_ctx', 'G2', 'G2^', 'T2_to_bar', 'area_xrun_pct'):
    print('%-18s %10.1f' % (k, g[k]))
for name, ok, info in R.arming(runs):
    print('%-28s %s  %s' % (name, 'PASS' if ok else 'FAIL', info))
