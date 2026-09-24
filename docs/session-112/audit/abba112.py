# ABBA statistics (audit 112), independent of the session scorers. Uses pickles made by parse112.py.
import pickle, statistics as st, random, math, sys

PK = 'C:/kyty/s112/audit112/pkl/%s.pkl'


def load(tag):
    return pickle.load(open(PK % tag, 'rb'))


def val(r, key):
    if key == 'cpu_net_us':
        if 'cpu_gpu_us' in r and 'spin_gpu_us' in r: return r['cpu_gpu_us'] - r['spin_gpu_us']
        return None
    if key == 'kpx_per_att':
        return r['rt_kpx'] / r['rt_att'] if r.get('rt_att') else None
    if key == 'vbl1':
        return 1.0 if r['dt_us'] < 25000 else 0.0
    if key == 'vbl2':
        return 1.0 if 25000 <= r['dt_us'] < 41667 else 0.0
    if key == 'vbl3p':
        return 1.0 if r['dt_us'] >= 41667 else 0.0
    if key == 'long50':
        return 1.0 if r['dt_us'] >= 50000 else 0.0
    if key == 'q_per_call':
        return r['da_queue_us'] / r['da_qcall'] if r.get('da_qcall') else None
    return r.get(key)


def blocks(P, lo=10, hi=90, first=2100, period=90, start=1800, byrow=False):
    """Block b = flips start+1+period*b .. start+period*(b+1) (GateArm frame F -> rows F+1..F+period).
    byrow=True assigns rows by their own arm=/blk= fields instead (cross-check)."""
    rows = P['rows']
    garm = {g[0]: g[1] for g in P['gates']}; gfr = {g[0]: g[2] for g in P['gates']}
    elig = {}; mism = 0; rej = {}
    if byrow:
        byblk = {}
        for n in sorted(rows):
            r = rows[n]
            if 'blk' in r and 'arm' in r and 'dt_us' in r:
                byblk.setdefault(r['blk'], []).append(n)
    for b in sorted(garm):
        F = gfr[b]
        exp = byblk.get(b, []) if byrow else list(range(F + 1, F + 1 + period))
        if len(exp) != period or not all(n in rows and 'dt_us' in rows[n] and 'spin_gpu_us' in rows[n]
                                         and 'da_qcall' in rows[n] for n in exp):
            rej[b] = 'incomplete'; continue
        for n in exp:
            if rows[n].get('arm') != garm[b] or rows[n].get('blk') != b: mism += 1
        kept = exp[lo:hi]
        if min(kept) < first: rej[b] = 'early'; continue
        elig[b] = kept
    pairs = []
    for b in range(0, max(garm) + 1, 4):
        q = [b, b + 1, b + 2, b + 3]
        if all(k in elig for k in q):
            pairs += [(b, b + 1), (b + 2, b + 3)]
    return garm, elig, pairs, mism, rej


def bmean(rows, ns, key, cap=None):
    v = [val(rows[n], key) for n in ns]
    v = [x for x in v if x is not None]
    if cap is not None: v = [min(x, cap) for x in v]
    return sum(v) / len(v) if v else None


def diffs(rows, garm, elig, pairs, key, cap=None, lo=None, hi=None):
    d = []
    for a, b in pairs:
        na = elig[a] if lo is None else elig[a][lo:hi]
        nb = elig[b] if lo is None else elig[b][lo:hi]
        ma = bmean(rows, na, key, cap); mb = bmean(rows, nb, key, cap)
        if ma is None or mb is None: continue
        if garm[a] == 1 and garm[b] == 0: d.append(ma - mb)
        elif garm[a] == 0 and garm[b] == 1: d.append(mb - ma)
        else: raise Exception('pair arms')
    return d


def summ(d, seed=1, R=20000):
    n = len(d); m = sum(d) / n; sd = st.stdev(d) if n > 1 else 0.0; se = sd / math.sqrt(n) if n else 0
    rnd = random.Random(seed)
    obs = abs(m); cnt = 0
    for _ in range(R):
        s = sum(x if rnd.random() < 0.5 else -x for x in d) / n
        if abs(s) >= obs - 1e-12: cnt += 1
    bs = []
    for _ in range(5000):
        bs.append(sum(d[rnd.randrange(n)] for _ in range(n)) / n)
    bs.sort()
    return dict(n=n, mean=m, se2=2 * se, t=(m / se if se else float('nan')), median=st.median(d), p=(cnt + 1) / (R + 1),
                boot=(bs[125], bs[4875]))


def fmt(s):
    return 'n %3d mean %9.3f 2SE %8.3f t %7.2f med %9.2f p %.4f boot95 [%.1f, %.1f]' % (
        s['n'], s['mean'], s['se2'], s['t'], s['median'], s['p'], s['boot'][0], s['boot'][1])


def quick(d):
    n = len(d); m = sum(d) / n; se = st.stdev(d) / math.sqrt(n) if n > 1 else float('nan')
    return m, 2 * se, (m / se if se else float('nan'))


def levels(rows, garm, elig, used, key):
    out = {}
    for a in (0, 1):
        ms = [bmean(rows, elig[b], key) for b in used if garm[b] == a]
        ms = [x for x in ms if x is not None]
        out[a] = (st.median(ms) if ms else None, st.fmean(ms) if ms else None)
    return out
