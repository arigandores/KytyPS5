import sys, statistics, math, collections
sys.path.insert(0, 'C:/kyty/s104/audit104/plateau')
from parse import parse
V = 1e6 / 60.0


def mt(v):
    m = statistics.fmean(v)
    se = statistics.stdev(v) / math.sqrt(len(v)) if len(v) > 1 else float('nan')
    return m, 2 * se, (m / se if se else float('nan'))


def run(p, period=90, start=1800, first=2100, lo=60, hi=89, label=''):
    d = parse(p)
    rows = d['rows']
    arms = {}
    maxb = max((r.get('blk', -1) for r in rows.values()), default=-1)
    elig = {}
    for b in range(0, maxb + 1):
        exp = list(range(start + 1 + period * b, start + 1 + period * (b + 1)))
        if not all(n in rows and 'dt_us' in rows[n] for n in exp):
            continue
        kept = exp[lo:hi]
        if min(kept) < first:
            continue
        a = collections.Counter(rows[n].get('arm') for n in kept)
        if len(a) != 1:
            continue
        arms[b] = list(a)[0]
        elig[b] = kept
    pairs = []
    for b in range(0, maxb + 1, 4):
        q = list(range(b, b + 4))
        if all(k in elig for k in q):
            pairs += [(b, b + 1), (b + 2, b + 3)]

    def bm(b):
        sel = [rows[n] for n in elig[b]]
        dt = [r['dt_us'] for r in sel]
        o = dict(dt=statistics.fmean(dt), cpu=statistics.fmean(r['cpu_gpu_us'] for r in sel),
                 spin=statistics.fmean(r.get('spin_gpu_us', 0) for r in sel),
                 lat=statistics.fmean(r.get('lat_us', 0) for r in sel),
                 draws=statistics.fmean(r['draws'] for r in sel),
                 gpu=statistics.fmean(r['gpu_busy_us'] for r in sel),
                 v1=sum(1 for x in dt if round(x / V) == 1) / len(dt),
                 v3=sum(1 for x in dt if round(x / V) >= 3) / len(dt),
                 main=statistics.fmean(r.get('cpu_main_us', 0) for r in sel),
                 pres=statistics.fmean(r.get('cpu_present_us', 0) for r in sel),
                 proc=statistics.fmean(r.get('cpu_proc_us', 0) for r in sel))
        o['net'] = o['cpu'] - o['spin']
        o['idle'] = o['dt'] - o['cpu']
        o['busy'] = o['cpu'] / o['dt']
        return o
    M = {b: bm(b) for b in elig}
    print('%s %s pairs=%d' % (label, p, len(pairs)))
    for a in (0, 1):
        bs = [b for b, _ in pairs] + [c for _, c in pairs]
        bs = [b for b in bs if arms[b] == a]
        agg = {k: statistics.fmean(M[b][k] for b in bs) for k in M[bs[0]]}
        print('  arm%d  dt=%8.1f cpu=%8.1f net=%8.1f idle=%7.1f busy=%.4f spin=%5.1f lat=%7.1f v1=%.3f v3=%.3f draws=%.1f gpu=%.0f main=%.0f pres=%.0f proc=%.0f' % (
            a, agg['dt'], agg['cpu'], agg['net'], agg['idle'], agg['busy'], agg['spin'], agg['lat'], agg['v1'], agg['v3'],
            agg['draws'], agg['gpu'], agg['main'], agg['pres'], agg['proc']))
    D = collections.defaultdict(list)
    for x, y in pairs:
        a1, a0 = (x, y) if arms[x] == 1 else (y, x)
        for k in M[x]:
            D[k].append(M[a1][k] - M[a0][k])
    for k in ('dt', 'cpu', 'net', 'spin', 'idle', 'busy', 'lat', 'v1', 'v3', 'draws', 'gpu', 'main', 'pres', 'proc'):
        m, s2, t = mt(D[k])
        print('  d %-6s mean %10.4f  2SE %9.4f  t %6.2f' % (k, m, s2, t))
    # ratio via regression of d dt on d net
    xs, ys = D['net'], D['dt']
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    print('  ratio mean(d dt)/mean(d net) = %.3f ; OLS slope d dt on d net = %.3f ; corr = %.3f' % (
        my / mx, sxy / sxx, sxy / math.sqrt(sxx * sum((y - my) ** 2 for y in ys))))
    return M, arms, pairs


if __name__ == '__main__':
    p = sys.argv[1]
    period = int(sys.argv[2]) if len(sys.argv) > 2 else 90
    lo = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    hi = int(sys.argv[4]) if len(sys.argv) > 4 else 89
    run(p, period=period, lo=lo, hi=hi)
