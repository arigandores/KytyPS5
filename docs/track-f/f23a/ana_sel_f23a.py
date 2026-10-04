"""F23a (HPP-578): reads sel_<variant>.jsonl (+ .status.jsonl) of run_f23a.py seldiag and prints the B8 census:
rows and programs (unique hash16) with surviving exec selects by stage, level (top / nested), control depth, and the
driver form (A, B); the reference PS 0xe197e307a5f2cb39 per variant. Stage numbers: from the status file (stage text
of t1_base). Usage: python ana_sel_f23a.py normal [nowqm predoff ...]"""
import collections
import json
import sys

D = 'C:/kyty/f287/f23a/'
REF = 'e197e307a5f2cb39'


def load(variant):
    st = {}
    for line in open(D + 'sel_%s.status.jsonl' % variant, encoding='utf-8'):
        r = json.loads(line)
        st[r['id']] = r
    sel = {}
    for line in open(D + 'sel_%s.jsonl' % variant, encoding='utf-8'):
        r = json.loads(line)
        sel[(r['hash'], r['perm'], r['gcn'])] = r
    return st, sel


def main(variants):
    for v in variants:
        st, sel = load(v)
        ok = [r for r in st.values() if r['rc'] == 0]
        stage_of = {r['hash']: r['stage'] for r in st.values()}
        rows = list(sel.values())
        print('=== variant', v, ': status rows', len(st), 'rc0', len(ok), '; diag lines', len(rows),
              '; rc0 rows by stage', dict(collections.Counter(r['stage'] for r in ok)))
        by = collections.defaultdict(lambda: collections.Counter())
        progs = collections.defaultdict(lambda: collections.defaultdict(set))
        depth = collections.Counter()
        for r in rows:
            s = stage_of.get(r['hash'], '?')
            by[s]['rows'] += 1
            progs[s]['all'].add(r['hash'])
            if r['survive'] > 0:
                by[s]['rows_survive'] += 1
                progs[s]['survive'].add(r['hash'])
            if r['top'] > 0:
                progs[s]['top'].add(r['hash'])
            if r['nested'] > 0:
                progs[s]['nested'].add(r['hash'])
            if r['formA'] > 0:
                progs[s]['formA'].add(r['hash'])
            if r['formB'] > 0:
                progs[s]['formB'].add(r['hash'])
            by[s]['selects_created'] += r['created']
            by[s]['selects_survive'] += r['survive']
            by[s]['top'] += r['top']
            by[s]['nested'] += r['nested']
            for it in r['items']:
                depth[(s, it['lvl'], it['depth'])] += 1
        for s in sorted(by):
            c = by[s]
            p = progs[s]
            print('  stage %s: rows %d (survive %d); programs %d, with surviving selects %d (top %d, nested %d); '
                  'driver form A %d, B %d; selects created %d, surviving %d (top %d, nested %d)' % (
                      s, c['rows'], c['rows_survive'], len(p['all']), len(p['survive']), len(p['top']),
                      len(p['nested']), len(p['formA']), len(p['formB']), c['selects_created'], c['selects_survive'],
                      c['top'], c['nested']))
            if p['formA']:
                print('    form A programs:', sorted(p['formA']))
            if p['formB']:
                print('    form B programs:', sorted(p['formB']))
        dd = collections.defaultdict(collections.Counter)
        for (s, lvl, d), n in depth.items():
            dd[(s, lvl)][d] += n
        for k in sorted(dd):
            print('  depth histogram (items listed) %s %s: %s' % (k[0], k[1], dict(sorted(dd[k].items()))))
        ref = [r for r in rows if r['hash'] == REF]
        for r in ref:
            print('  REF %s perm %d: created %d survive %d top %d nested %d formA %d formB %d' % (
                REF, r['perm'], r['created'], r['survive'], r['top'], r['nested'], r['formA'], r['formB']))
            for it in r['items']:
                if it['A']:
                    print('     A item', it)
        if not ref:
            print('  REF', REF, 'no diag line')


if __name__ == '__main__':
    main(sys.argv[1:] or ['normal'])
