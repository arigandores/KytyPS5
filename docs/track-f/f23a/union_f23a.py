"""F23a (HPP-578): B8 census over the union of the S7 A rows (sel_<v>.jsonl) and the C/D extension (sel_<v>_cd.jsonl),
counted by PROGRAM (hash16; a program counts once if any of its translated rows has the property). Writes
b8_forms_<v>.tsv (programs of driver form A / B with their items) and prints the table for the report.
Usage: python union_f23a.py normal predoff"""
import collections
import json
import sys

D = 'C:/kyty/f287/f23a/'
TAB = chr(9)
NL = chr(10)


def load(v):
    stage = {}
    rc0 = collections.defaultdict(set)
    lines = []
    for suf in ('', '_cd'):
        for l in open(D + 'sel_%s%s.status.jsonl' % (v, suf), encoding='utf-8'):
            r = json.loads(l)
            stage[r['hash']] = r['stage']
            if r['rc'] == 0:
                rc0[r['stage']].add(r['hash'])
        for l in open(D + 'sel_%s%s.jsonl' % (v, suf), encoding='utf-8'):
            lines.append(json.loads(l))
    return stage, rc0, lines


def main(vs):
    for v in vs:
        stage, rc0, lines = load(v)
        P = collections.defaultdict(lambda: collections.defaultdict(set))
        items = collections.defaultdict(list)
        sel = collections.Counter()
        dep = collections.defaultdict(collections.Counter)
        for r in lines:
            s = stage.get(r['hash'], '?')
            P[s]['diag'].add(r['hash'])
            sel[(s, 'created')] += r['created']
            sel[(s, 'survive')] += r['survive']
            sel[(s, 'top')] += r['top']
            sel[(s, 'nested')] += r['nested']
            for k in ('survive', 'top', 'nested', 'formA', 'formB'):
                if r[k] > 0:
                    P[s][k].add(r['hash'])
            for it in r['items']:
                dep[(s, it['lvl'])][it['depth']] += 1
                if it['A']:
                    items[r['hash']].append((r['perm'], it['lvl'], it['depth'], it['new'], it['old'], it['B']))
        print('=== %s (program = hash16; rows A + C/D)' % v)
        for s in sorted(P):
            p = P[s]
            print('  %s: translated %d; with surviving exec selects %d (top-level %d, nested %d); driver form A %d, B %d; '
                  'selects created %d -> surviving %d (top %d / nested %d)' % (
                      s, len(rc0[s]), len(p['survive']), len(p['top']), len(p['nested']), len(p['formA']),
                      len(p['formB']), sel[(s, 'created')], sel[(s, 'survive')], sel[(s, 'top')], sel[(s, 'nested')]))
            for lvl in ('top', 'nested'):
                h = dep[(s, lvl)]
                if h:
                    n = sum(h.values())
                    print('     depth (listed items, %s): n %d, depth 0: %d, 1-3: %d, 4-9: %d, >=10: %d, max %d' % (
                        lvl, n, h[0], sum(h[d] for d in (1, 2, 3)), sum(h[d] for d in range(4, 10)),
                        sum(c for d, c in h.items() if d >= 10), max(h)))
        tot_a = set().union(*[P[s]['formA'] for s in P])
        tot_b = set().union(*[P[s]['formB'] for s in P])
        top_a = [h for h in tot_a if any(i[1] == 'top' for i in items[h])]
        print('  total form A programs %d (top-level item in %d: %s), form B %d' % (len(tot_a), len(top_a), sorted(top_a),
                                                                                 len(tot_b)))
        with open(D + 'b8_forms_%s.tsv' % v, 'w', encoding='utf-8', newline=NL) as f:
            f.write(TAB.join(['stage', 'hash16', 'formB', 'items(perm,level,depth,new,old,B)']) + NL)
            for h in sorted(tot_a, key=lambda x: (stage[x], x)):
                f.write(TAB.join([stage[h], h, '1' if h in tot_b else '0',
                                  ';'.join('%d,%s,%d,%s,%s,%d' % i for i in items[h][:12])]) + NL)


if __name__ == '__main__':
    main(sys.argv[1:] or ['normal'])
