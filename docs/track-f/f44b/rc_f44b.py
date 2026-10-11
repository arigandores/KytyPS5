# F44b (HPP-792, Red Team): own recount of an F29 stand output dir (f29_0.tsv, f29_1.tsv and .tsv.log), written
# without the F44a reader. Members by the letter of ROADMAP s122 item 698(d)(1) with item 701(b)(2):
#   G1: raw > 1023 at E1 O1 O7 D1 L; one-bit arms raw = B; D1 1024 <= raw <= 1058.
#   G2: stored = 1023 at B >= 1024; stored = B at S1 S2.
#   P0 (=0): O1 out_area 77 (low 1, page 76), O7 out_buf 77 (exit 77), E1 out_area 1, L low >= 1; lines FixF29: 0.
#   P1 (=1): out_area = out_buf = low = exit = 0 everywhere; read = 1023 where raw > 1023; overflow lines =
#            min(32, overflow repetitions).
#   H: S0-S2 sorted sha =1 = =0 = expected; E1 O1 D1 h_inproc = 1 at =1; extra = dup = 0 both modes.
#   Z: map_left, nb_touched, raw_hi = 0.
# Also: read at =0 = raw (the =0 path reads the counter as is) - separates a code fault of =0 from a dead stand.
# Usage: python rc_f44b.py <dir> <R>   ; last line ALL OK / FAIL; prints per-member bad/total.
import sys

d, R = sys.argv[1], int(sys.argv[2])
OVER = ('E1', 'O1', 'O7', 'D1', 'L')
ONE = ('S1', 'S2', 'E1', 'O1', 'O7', 'L')
B = {'S0': 0, 'S1': 1000, 'S2': 1023, 'E1': 1024, 'O1': 1100, 'O7': 1100, 'D1': 1120, 'L': 1100}


def rows(k):
    t = open('%s/f29_%d.tsv' % (d, k), encoding='utf-8').read().splitlines()
    h = t[0].split('\t')
    out = []
    for l in t[1:]:
        if l:
            r = dict(zip(h, l.split('\t')))
            for c in r:
                if c not in ('arm', 'h_sha', 'exp_sha'):
                    r[c] = int(r[c])
            out.append(r)
    return out


def lines(k):
    s = open('%s/f29_%d.tsv.log' % (d, k), 'rb').read().decode('utf-8', 'replace')
    return [l[l.find('FixF29:'):].strip() for l in s.splitlines() if 'FixF29:' in l]


res = []


def m(name, bad, tot):
    res.append(bad == 0 and tot > 0)
    print('%-44s %s bad=%d of %d' % (name, 'PASS' if res[-1] else 'FAIL', bad, tot))


D = {k: rows(k) for k in (0, 1)}
for k in (0, 1):
    rr = D[k]
    m('[%d] rows = R*8, each (rep,arm) once' % k, abs(len(rr) - 8 * R) + (len({(r['rep'], r['arm']) for r in rr}) != 8 * R), 1)
    m('[%d] Z map_left/nb_touched/raw_hi' % k, sum(r['map_left'] + r['nb_touched'] + r['raw_hi'] != 0 for r in rr), len(rr))
    m('[%d] extra = dup = 0' % k, sum(r['extra'] + r['dup'] != 0 for r in rr), len(rr))
    g1 = [r for r in rr if r['arm'] in OVER or r['arm'] in ONE]
    m('[%d] G1' % k, sum((r['arm'] in OVER and r['raw'] <= 1023) or (r['arm'] in ONE and r['raw'] != B[r['arm']]) or
                       (r['arm'] == 'D1' and not 1024 <= r['raw'] <= 1058) for r in g1), len(g1))
    g2 = [r for r in rr if B[r['arm']] >= 1024 or r['arm'] in ('S1', 'S2')]
    m('[%d] G2' % k, sum(r['stored'] != (1023 if B[r['arm']] >= 1024 else B[r['arm']]) for r in g2), len(g2))
    m('[%d] read_vis = read, classes sum = out_area' % k,
      sum(r['read_vis'] != r['read'] or r['cls_zero'] + r['cls_low'] + r['cls_page'] + r['cls_exit'] != r['out_area']
          for r in rr), len(rr))
    ll = lines(k)
    if k == 0:
        m('[0] read = raw (=0 path unchanged)', sum(r['read'] != r['raw'] for r in rr), len(rr))
        p0 = 0
        n0 = 0
        for r in rr:
            a = r['arm']
            if a == 'O1':
                p0 += not (r['out_area'] == 77 and r['cls_low'] == 1 and r['cls_page'] == 76 and r['out_buf'] == 0)
            elif a == 'O7':
                p0 += not (r['out_area'] == 77 and r['out_buf'] == 77 and r['cls_exit'] == 77)
            elif a == 'E1':
                p0 += not (r['out_area'] == 1 and r['cls_low'] == 1)
            elif a == 'L':
                p0 += not (r['cls_low'] >= 1)
            else:
                continue
            n0 += 1
        m('[0] P0', p0, n0)
        m('[0] FixF29 lines = 0 (got %d)' % len(ll), len(ll), 1)
    else:
        m('[1] P1 out_area/out_buf/low/exit/zero/page = 0',
          sum(r['out_area'] + r['out_buf'] + r['cls_low'] + r['cls_exit'] + r['cls_zero'] + r['cls_page'] != 0 for r in rr), len(rr))
        m('[1] read = min(raw, 1023)', sum(r['read'] != min(r['raw'], 1023) for r in rr), len(rr))
        nover = sum(r['raw'] > 1023 for r in rr)
        ov = [l for l in ll if l.startswith('FixF29: overflow')]
        m('[1] overflow lines = min(32, %d) (got %d), other 0' % (nover, len(ov)),
          abs(len(ov) - min(32, nover)) + (len(ll) - len(ov)), 1)
        m('[1] overflow lines read=1023, total 1..n',
          sum(('read=1023' not in l) or (' total=%d' % (i + 1)) not in l for i, l in enumerate(ov)), max(1, len(ov)))
by = {k: {(r['rep'], r['arm']): r for r in D[k]} for k in (0, 1)}
h = 0
n = 0
for (rep, a), r1 in by[1].items():
    r0 = by[0].get((rep, a))
    if a in ('S0', 'S1', 'S2'):
        n += 1
        h += not (r0 and r1['h_sha'] == r0['h_sha'] == r1['exp_sha'] == r0['exp_sha'])
    if a in ('E1', 'O1', 'D1'):
        n += 1
        h += r1['h_inproc'] != 1
m('H', h, n)
print('ALL OK' if all(res) else 'FAIL')
