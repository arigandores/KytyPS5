# F36b (HPP-759): own replay vs F36a records, per event the fields writes, sens, N_null, N_diff (def/mask), N_orig_def, Npre of
# def/mask/mem/sens/orig2 (sums). Prints differing fields and the totals. ASCII only.
import json, glob
def T(x): return None if x is None else (-1 if any(v < 0 for v in x.values()) else sum(x.values()))
A = {}
for k in '02 03 04 05 06 07 08'.split():
    for l in open('C:/kyty/KytyPS5/docs/track-f/f36a/runs/rp_k%s.jsonl' % k):
        r = json.loads(l); A[r['eid'], k] = r
bad = n = m = 0
for f in ['C:/kyty/f287/f36b/runs/rp_k03.json'] + sorted(glob.glob('C:/kyty/f287/f36b/runs/rpv_k*.json')):
    d = json.load(open(f)); k = d['cap'][-6:-4]
    for r in d['events']:
        a = A[r['eid'], k]; n += 1
        pairs = [('writes', T(r['writes']), T(a['writes'])), ('sens', T(r['N_def_sens']), T(a['sens'])), ('N_null', T(r['N_null']), T(a['N_null'])),
                 ('N_diff', T(r['N_def_mask']), T(a['N_diff_mask'])), ('N_orig_def', T(r['N_orig_def']), T(a['N_orig_def']))]
        pairs += [('Npre_' + x, T(r['Npre_' + x]), T(a['Npre_' + x])) for x in ('def', 'mask', 'mem', 'sens', 'orig2')]
        for p in pairs:
            m += 1
            if p[1] != p[2]:
                bad += 1; print('DIFF', k, r['eid'], p)
print('events %d, fields %d, differing %d' % (n, m, bad))
print('ALL OK' if bad == 0 else 'FAIL')
