from recount import *
sh = load('sh104'); rs = analyse(sh, ['cpu_net_us'])
for a in (0, 1):
    print('sh104 arm', a, {k: kept_sum(sh, rs, a, k) for k in ('sh_jobs', 'sh_drop', 'a_hold_us', 'a_mut_us', 'mw_n', 'pl_em_n', 'pl_proc_n', 'pl_prog_n', 'da_wjobs', 'gm_ops', 'bf_n')})
print('sh104 work %', 100 * (retained_mean(sh, rs, 1, 'draws') / retained_mean(sh, rs, 0, 'draws') - 1))
mu = load('mut104b'); rm = analyse(mu, ['cpu_net_us'])
for a in (0, 1):
    print('mut104b arm', a, {k: kept_sum(mu, rm, a, k) for k in ('mw_n', 'sh_jobs', 'da_wjobs', 'gm_ops', 'bf_n')})
print('mut104b work %', 100 * (retained_mean(mu, rm, 1, 'draws') / retained_mean(mu, rm, 0, 'draws') - 1))
# mut104 (invalid) - where did the skipped draws land relative to the kept rows
m0 = load('mut104'); r0 = analyse(m0, ['cpu_net_us', 'dt_us'])
print('mut104 pairs', r0['pairs'], 'dt at n 2325..2332', [m0['merged'][n]['dt_us'] for n in range(2325, 2333)])
blk = [b for b, ns in r0['elig'].items() if 2328 in ns or 2330 in ns]
print('mut104 block holding n 2328/2330 (kept):', blk, 'arm', [r0['arm_of'][b] for b in blk], 'P_mw (invalid run) %s' % fmt(r0['diffs']['cpu_net_us'][:3]))
