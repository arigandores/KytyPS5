"""Paired arm1-arm0 deltas of FrameTrace-rp render-pass end/restart reasons over the kept rows (frm109, fam108)."""
import math
import pickle
import re
import statistics
import sys

sys.stdout.reconfigure(encoding='utf-8')
TOK = re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')
for tag, root in (('frm109', 'C:/kyty/s109'), ('fam108', 'C:/kyty/s108')):
    P = pickle.load(open('C:/kyty/s109/audit109/pairs_%s.pkl' % tag, 'rb'))
    arms, el, pairs = P['arms'], P['eligible'], P['pairs']
    want = {n: b for b, ns in el.items() for n in ns}
    sums = {}
    with open('%s/log_%s.txt' % (root, tag), 'rb') as f:
        for line in f:
            if not line.startswith(b'FrameTrace-rp: '):
                continue
            t = TOK.findall(line)
            n = int(t[0][1])
            b = want.get(n)
            if b is None:
                continue
            s = sums.setdefault(b, {})
            for k, v in t[1:]:
                s[k.decode()] = s.get(k.decode(), 0) + int(v)
    keys = sorted({k for s in sums.values() for k in s})
    print('==', tag)
    for k in keys:
        ds = []
        for l, r in pairs:
            a0 = l if arms[l] == 0 else r
            a1 = r if a0 == l else l
            ds.append((sums[a1].get(k, 0) - sums[a0].get(k, 0)) / 29.0)
        mu = statistics.fmean(ds)
        sd = statistics.stdev(ds)
        base = statistics.fmean(sums[b].get(k, 0) / 29.0 for b in el if arms[b] == 0 and b in sums)
        if base or mu:
            print('  %-22s arm0 %8.2f  d %+7.3f  t %+6.2f' % (k, base, mu, mu / (sd / math.sqrt(len(ds))) if sd else 0))
