# F36b (HPP-759): own recount of the F36a set (docs/track-f/f36a/runs/rp_k0*.jsonl) by the members of item 687(e)(1), own code:
# valid <=> all bound_ok, no large outputs, N_null = 0, N(mask,mem) = 0, SP > 0, Npre = 0 for every replaced arm and orig2,
# n_entry = PSInvocations, sens > 0; any negative N in any used field -> not valid. Prints per-event line and the totals. ASCII only.
import json
D = 'C:/kyty/KytyPS5/docs/track-f/f36a/runs/rp_k%s.jsonl'
def T(x):
    if x is None: return None
    return -1 if any(v < 0 for v in x.values()) else sum(x.values())
tot = {'events': 0, 'valid': 0, 'valid_alpha': 0, 'ndiff_pos': 0, 'nt_pos': 0, 'nf_pos': 0, 'g2_ok': 0, 'neg': 0}
for k in '02 03 04 05 06 07 08'.split():
    for line in open(D % k):
        r = json.loads(line)
        f = {}
        f['bound'] = all(r.get('bound_ok_' + a) for a in ('orig', 'def', 'mask', 'mem', 'sens', 'diag', 'orig2')) and not r.get('outputs_not_read_large')
        vals = {'N_null': T(r.get('N_null')), 'refs': T(r.get('N_mask_mem')), 'sens': T(r.get('sens')), 'ndiff': T(r.get('N_diff_mask')),
                'ndiff_mem': T(r.get('N_diff_mem')), 'self': T(r.get('selfcheck'))}
        npre = {a: T(r.get('Npre_' + a)) for a in ('def', 'mask', 'mem', 'sens', 'diag', 'orig2')}
        neg = any(v is None or v < 0 for v in list(vals.values()) + list(npre.values()))
        f['N_null'] = vals['N_null'] == 0
        f['refs'] = vals['refs'] == 0
        f['G3'] = r['SamplesPassed'] > 0
        f['G1'] = all(v == 0 for v in npre.values())
        f['G2'] = r.get('n_entry') == r['PSInvocations']
        f['G4'] = (vals['sens'] or 0) > 0
        f['noneg'] = not neg
        ok = all(f.values())
        tot['events'] += 1; tot['g2_ok'] += f['G2']; tot['neg'] += neg
        if ok:
            tot['valid'] += 1
            tot['valid_alpha'] += r['exec_no'] == 1
            tot['ndiff_pos'] += vals['ndiff'] != 0 or vals['ndiff_mem'] != 0
            cr = vals['self'] == 0
            tot['nt_pos'] += cr and all(x > 0 for x in r['n_t'])
            tot['nf_pos'] += cr and any(x > 0 for x in r['n_f'])
        print('k%s %6d #%d %s %s ndiff %s/%s sens %s n_t %s n_f %s' % (k, r['eid'], r['exec_no'], 'VALID' if ok else 'no', [n for n, v in f.items() if not v],
              vals['ndiff'], vals['ndiff_mem'], vals['sens'], r.get('n_t'), r.get('n_f')))
print(json.dumps(tot, sort_keys=True))
