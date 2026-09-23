import math
import pickle
import statistics
import sys

sys.stdout.reconfigure(encoding='utf-8')
res = {}
for tag in ('frm109', 'fam108'):
    d = pickle.load(open('C:/kyty/s109/audit109/parsed/%s.pkl' % tag, 'rb'))
    P = pickle.load(open('C:/kyty/s109/audit109/pairs_%s.pkl' % tag, 'rb'))
    arms, el, pairs = P['arms'], P['eligible'], P['pairs']
    bs, bc = d['blocksum'], d['blockcnt']
    fields = set()
    for (kind, b), s in bs.items():
        fields |= {(kind, k) for k in s}
    out = {}
    for kind, k in fields:
        if k == 'n':
            continue
        ds = []
        ok = True
        for l, r in pairs:
            a0 = l if arms[l] == 0 else r
            a1 = r if a0 == l else l
            s0, s1 = bs.get((kind, a0), {}), bs.get((kind, a1), {})
            if k not in s0 or k not in s1:
                ok = False
                break
            ds.append(s1[k] / bc[(kind, a1)] - s0[k] / bc[(kind, a0)])
        if not ok or len(ds) < 10:
            continue
        mu = statistics.fmean(ds)
        sd = statistics.stdev(ds)
        base = statistics.fmean(bs[(kind, b)][k] / bc[(kind, b)] for b in el if arms[b] == 0 and (kind, b) in bs and k in bs[(kind, b)])
        t = mu / (sd / math.sqrt(len(ds))) if sd > 0 else (0.0 if mu == 0 else math.copysign(99999, mu))
        out[(kind, k)] = (mu, t, base)
    res[tag] = out

a, b = res['frm109'], res['fam108']
common = sorted(set(a) & set(b), key=lambda k: -abs(a[k][1]))
print('%-6s %-26s %12s %8s %12s | %12s %8s' % ('kind', 'field', 'frm109 d', 't', 'arm0 level', 'fam108 d', 't'))
for k in common:
    if abs(a[k][1]) >= 3 or abs(b[k][1]) >= 3:
        if abs(a[k][1]) > 5000 or abs(b[k][1]) > 5000:
            flag = ' (arming)'
        else:
            flag = ''
        print('%-6s %-26s %12.2f %8.2f %12.1f | %12.2f %8.2f%s' % (k[0], k[1], a[k][0], a[k][1], a[k][2], b[k][0], b[k][1], flag))
