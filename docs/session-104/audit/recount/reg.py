from recount import *
for tag in ('reg104', 'ckpt102'):
    d = load(tag)
    ns = sorted(n for n, r in d['merged'].items() if 'dt_us' in r and 'cpu_gpu_us' in r and 'draws' in r)
    N = len(ns)
    for name, (a, b) in (('floor', (N // 3, 2 * N // 3)), ('round', (round(N / 3), round(2 * N / 3)))):
        mid = ns[a:b]
        R = [d['merged'][n] for n in mid]
        dt = st.mean(r['dt_us'] for r in R); cg = st.mean(r['cpu_gpu_us'] for r in R)
        cpd = sum(r['cpu_gpu_us'] for r in R) / sum(r['draws'] for r in R)
        net = st.mean(r['cpu_gpu_us'] - r.get('spin_gpu_us', 0) for r in R)
        print(tag, name, 'N', N, 'n range', mid[0], mid[-1], 'rows', len(mid), 'mean dt %.4f ms cpu_gpu %.4f ms cpu/draw %.4f us cpu_net %.4f ms' % (dt / 1000, cg / 1000, cpd, net / 1000),
              'draws %.1f' % st.mean(r['draws'] for r in R), 'area %.2f' % (sum(r['rt_kpx'] for r in R) / sum(r['rt_att'] for r in R)),
              'dt>100ms', sum(1 for r in R if r['dt_us'] > 100000), 'max dt', max(r['dt_us'] for r in R))
    # rows around the skipped draws
    if tag == 'reg104':
        print('reg104 dt n 2452..2460', [d['merged'][n]['dt_us'] for n in range(2452, 2461)])
