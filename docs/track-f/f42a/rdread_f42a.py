"""F42a (HPP-779, ROADMAP s122 item 694(g)(3)): reading of the replay arm - members R0, K', K, P3', P3 per EID from
replay/rd_e<eid>.txt (lines of rd_f42a.py: 'eid E round r arm X p0_nonzero n word W nz [...] img H'). No verdict: the
table R1-R6 is read by the lead (F42d). Arms: o (no substitution), z (snapshot module substituted by its own words),
a (z through RewriteFaultOr), op = o' (FS12 module), ap = a' (o' through RewriteFaultOr).
Usage: python rdread_f42a.py [eid ...]  (default 128281 44806 84820). Prints ALL OK when every file parses with
N = 20 per arm and the nz list carries only word 32824 or nothing."""
import re
import sys
from collections import Counter, OrderedDict

D = 'C:/kyty/f287/f42a/replay'
ARMS = ('op', 'ap', 'o', 'z', 'a')
NAME = {'op': "o'", 'ap': "a'", 'o': 'o', 'z': 'z', 'a': 'a'}
RX = re.compile(r"\] eid (\d+) round (\d+) arm (\w+) p0_nonzero (\d+) word ([0-9a-f]{8}) nz (\[.*\]) img ([0-9a-f]+)$")


def read(eid):
    rows = []
    bad = 0
    for line in open('%s/rd_e%s.txt' % (D, eid), encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        if ' arm ' not in line:
            continue
        m = RX.search(line)
        if not m:
            bad += 1
            continue
        e, r, arm, p0, w, nz, img = m.groups()
        words = re.findall(r"\((\d+), '", nz)
        rows.append(dict(eid=int(e), round=int(r), arm=arm, p0=int(p0), word=int(w, 16), nzw=set(int(x) for x in words),
                         img=img))
    return rows, bad


def main():
    eids = sys.argv[1:] or ['128281', '44806', '84820']
    ok = True
    for eid in eids:
        rows, bad = read(eid)
        print('== EID %s: replays %d, unparsed arm lines %d' % (eid, len(rows), bad))
        ok &= bad == 0
        per = OrderedDict((a, [r for r in rows if r['arm'] == a]) for a in ARMS)
        for a in ARMS:
            rs = per[a]
            vals = Counter('%08x' % r['word'] for r in rs)
            imgs = Counter(r['img'] for r in rs)
            p0 = sum(1 for r in rs if r['p0'] != 0)
            other = sum(1 for r in rs if r['nzw'] - {32824})
            print('  arm %-2s N %2d  p0_nonzero>0 %d  words-other-than-32824 %d  word32824 %s  img %s' % (
                NAME[a], len(rs), p0, other, dict(sorted(vals.items())), dict(sorted(imgs.items()))))
            ok &= len(rs) == 20 and other == 0
        r0 = all(r['p0'] == 0 for r in rows)
        dv = {a: set(r['word'] for r in per[a]) for a in ARMS}
        di = {a: set(r['img'] for r in per[a]) for a in ARMS}
        kp = len(dv['op']) >= 2
        k = len(dv['z']) >= 2

        def p3(arm, base):
            orall = 0
            for x in dv[base] | dv[arm]:
                orall |= x
            one = len(dv[arm]) == 1
            return one and next(iter(dv[arm])) == orall and di[arm] <= di[base], orall

        p3p, orp = p3('ap', 'op')
        p3s, ors = p3('a', 'z')
        print("  R0 (buffer 138 zero at EID-1 in every replay): %s" % ('yes' if r0 else 'NO'))
        print("  K' (o' >= 2 distinct values of word 32824): %s (%d distinct)" % ('alive' if kp else 'dead', len(dv['op'])))
        print("  K  (z  >= 2 distinct values of word 32824): %s (%d distinct)" % ('alive' if k else 'dead', len(dv['z'])))
        print("  P3' (a' one value = OR of o' and a' values %08x, img(a') in img(o')): %s" % (orp, 'yes' if p3p else 'NO'))
        print("  P3  (a  one value = OR of z  and a  values %08x, img(a)  in img(z)):  %s" % (ors, 'yes' if p3s else 'NO'))
        print("  o (no substitution) distinct values %d; img(o) == img(z): %s; img(o') == img(a'): %s" % (
            len(dv['o']), di['o'] == di['z'], di['op'] == di['ap']))
    print('ALL OK' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


main()
