from recount import *
d = load('dwk104')
res = analyse(d, ['cpu_net_us', 'dt_us'])
for a in (0, 1):
    print('arm', a, {k: kept_sum(d, res, a, k) for k in ('da_wjobs', 'da_wskip', 'da_wdrop', 'mw_n', 'a_hold_us', 'a_mut_us', 'pl_em_n', 'pl_proc_n', 'sh_jobs', 'gm_ops', 'bf_n', 'bf_disp', 'bf_skip')})
    print('  retained mean draws', retained_mean(d, res, a, 'draws'))
w0 = retained_mean(d, res, 0, 'draws'); w1 = retained_mean(d, res, 1, 'draws')
print('work split %', 100 * (w1 / w0 - 1))
s = kept_sum(d, res, 1, 'da_wskip'); j = kept_sum(d, res, 1, 'da_wjobs'); dr = kept_sum(d, res, 1, 'da_wdrop')
print('identity skip/(jobs+drop)-1', s / (j + dr) - 1)
# robustness
for lo, hi in ((0, 89), (30, 88), (60, 88)):
    r = analyse(d, ['cpu_net_us', 'dt_us'], lo, hi)
    print('idx', lo, hi, {k: fmt(v[:3]) for k, v in r['diffs'].items()})
# per-pair lists: halves, median, sign
res = analyse(d, ['cpu_net_us', 'dt_us'])
for key in ('cpu_net_us', 'dt_us'):
    diffs = []
    for p in res['pairlist']:
        b1 = [b for b in p if res['arm_of'][b] == 1][0]; b0 = [b for b in p if res['arm_of'][b] == 0][0]
        diffs.append(block_mean(d, res['elig'][b1], key) - block_mean(d, res['elig'][b0], key))
    h = len(diffs) // 2
    neg = sum(1 for x in diffs if x < 0)
    print(key, 'median pair', '%.4f' % st.median(diffs), 'neg', neg, '/', len(diffs),
          'first half %.4f second half %.4f' % (st.mean(diffs[:h]), st.mean(diffs[h:])),
          'orient AB-first %.4f BA %.4f' % (st.mean(diffs[0::2]), st.mean(diffs[1::2])))
