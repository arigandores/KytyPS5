# edge135.py - Session Auditor s.135: sensitivity rows of the (d)(3) edge (leave-one-pair-out) and of the dt outlier frame 7445.
# Rows only [I], not a re-reading: the sealed outcome stands. Uses recount135.py (own code).
import math, recount135 as R
P = R.parse('C:/kyty/s135/log_rs135.txt')
m, d, x = P['rows']['m'], P['rows']['d'], P['rows']['x']
arm_text = {'b2reuse=0': 0, 'b2reuse=1': 1}
blk = {}
for b, a in enumerate(P['arms']):
    F = int(a['frame']); arm = arm_text[a['text']]
    rows = []
    ok = True
    for p in range(R.W_LO, R.W_HI + 1):
        n = F + 1 + p
        if n not in m or n not in d or n not in x or any(k not in x[n] for k in R.X_F):
            ok = False; break
        r = dict(m[n]); r.update(d[n]); r.update(x[n]); r['n'] = n; rows.append(r)
    if ok:
        blk[b] = (arm, rows, R.block_level(rows))
pairs = []
for k in range(0, 77, 2):
    if k in blk and k + 1 in blk:
        a, b_ = (blk[k], blk[k + 1]) if blk[k][0] == 0 else (blk[k + 1], blk[k])
        pairs.append((k, a[2], b_[2], a[1], b_[1]))
def ms(v):
    n = len(v); mu = sum(v) / n; sd = math.sqrt(sum((q - mu) ** 2 for q in v) / (n - 1)); return mu, 2 * sd / math.sqrt(n)
def d3(ps):
    dn, s2 = ms([p[2]['pf_rs_sync_n'] - p[1]['pf_rs_sync_n'] for p in ps])
    ds = ms([p[2]['lv_sync'] - p[1]['lv_sync'] for p in ps])[0]; dsl = ms([p[2]['lv_slow7'] - p[1]['lv_slow7'] for p in ps])[0]
    parts = sum(1 for q in R.PARTS5 if (lambda mu_s: mu_s[0] - mu_s[1] > 0)(ms([p[2]['it_' + q] - p[1]['it_' + q] for p in ps])))
    partsraw = sum(1 for q in R.PARTS5 if (lambda mu_s: mu_s[0] - mu_s[1] > 0)(ms([p[2]['itraw_' + q] - p[1]['itraw_' + q] for p in ps])))
    if dn - s2 > 0 and ds >= 0.5 * dsl: o = 'TRANSFER'
    elif -s2 <= dn <= s2 and parts >= 3: o = 'SURCHARGE'
    else: o = 'NOT_RESOLVED'
    return o, dn, s2, parts, partsraw
print('pairs', len(pairs))
o = d3(pairs); print('all pairs: (d)(3) %s  d_sync_n %+.4f 2SE %.4f  parts>0 %d  raw parts>0 %d' % o)
flips = {}
for i in range(len(pairs)):
    r = d3(pairs[:i] + pairs[i + 1:])
    flips[r[0]] = flips.get(r[0], 0) + 1
print('leave-one-pair-out outcomes over %d subsets:' % len(pairs), flips)
# outlier frame 7445
for k, l0, l1, r0, r1 in pairs:
    for arm, rows in ((0, r0), (1, r1)):
        for r in rows:
            if r['n'] == 7445:
                print('frame 7445 in pair', k, 'arm', arm, 'dt_us', r['dt_us'])
                pk = k
dd = [p[2]['dt_us'] - p[1]['dt_us'] for p in pairs]
print('d dt_us all %+.1f +- %.1f' % ms(dd))
print('d dt_us without the pair of frame 7445 %+.1f +- %.1f' % ms([v for p, v in zip(pairs, dd) if p[0] != pk]))
o2 = d3([p for p in pairs if p[0] != pk]); print('(d)(3) without that pair [I]: %s d_sync_n %+.4f 2SE %.4f parts>0 %d raw parts>0 %d' % o2)
