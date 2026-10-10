# F36b (HPP-759): table of the own replay (runs/rp_k03.json - 3 events, all arms incl. diag; runs/rpv_k*.json - 11 more valid
# events of F36a, arms without diag). Per event: N_null; G1 by outputs (Npre of every replaced arm and orig2) and by inputs
# (Nin of def, mask, sens, orig2: PS and VS read-only resources and constant blocks); G4 sens; N_diff def/mask, def/mem; refs
# mask/mem; RC4(b) sens = mask_inv = mem_inv and != def; m3 (mask with a select error at %5011) != mask; m1' (before at eid - 1)
# and the counters' mutants m2 / m2' (rp_k03 only, from the raw slot words). Any negative N -> named. ASCII only.
import json, glob
G = 'C:/kyty/f287/f36b/runs/'
def T(x):
    if x is None: return None
    return -1 if any(v < 0 for v in x.values()) else sum(x.values())
rows = []
for f in [G + 'rp_k03.json'] + sorted(glob.glob(G + 'rpv_k*.json')):
    d = json.load(open(f))
    for r in d['events']:
        arms = [k[9:] for k in r if k.startswith('bound_ok_')]
        e = {'cap': d['cap'][-7:-4], 'eid': r['eid'], 'no': r['exec_no'], 'SP': r['SamplesPassed'], 'PSInv': r['PSInvocations'],
             'bound_ok': all(r['bound_ok_' + a] for a in arms), 'arms': len(arms), 'N_null': T(r.get('N_null')), 'writes': T(r.get('writes')),
             'Npre': {a: T(r.get('Npre_' + a)) for a in arms if a != 'orig'},
             'Nin': {a: T(r.get('Nin_' + a)) for a in ('def', 'mask', 'sens', 'orig2')},
             'Nin_nz': sorted(set(k.split('|')[0] for a in ('def', 'mask', 'sens', 'orig2') for k, v in (r.get('Nin_' + a) or {}).items() if v)),
             'n_inputs': len(r['inputs']), 'large': r['large'],
             'sens': T(r.get('N_def_sens')), 'N_diff': T(r.get('N_def_mask')), 'N_diff_mem': T(r.get('N_def_mem')), 'refs': T(r.get('N_mask_mem')),
             'inv_eq_sens': (T(r.get('N_sens_mask_inv')), T(r.get('N_sens_mem_inv'))), 'inv_vs_def': (T(r.get('N_def_mask_inv')), T(r.get('N_def_mem_inv'))),
             'm3': T(r.get('N_mask_m3')), 'm1p_Nem1_sens': T(r.get('Nem1_sens')), 'm1p_em1_eq_post': T(r.get('Nem1_vs_pre_orig')) == T(r.get('writes'))}
        if 'slots_post_diag' in r:
            b, a, o = r['slots_pre_diag'], r['slots_post_diag'], r['slots_pre_orig']
            e['n_entry'] = a[6] - b[6]; e['m2_raw'] = a[6]; e['m2p_vs_orig_pre'] = a[6] - o[6]
            e['slots_game'] = r['slots_pre_orig']; e['selfcheck'] = T(r.get('selfcheck'))
        rows.append(e)
        g1 = all(v == 0 for v in e['Npre'].values()); g1in = all(v == 0 for v in e['Nin'].values())
        print('%s %6d #%d SP %4d | arms %d bound %s | N_null %s | G1 out %s in %s %s | sens %s | N_diff %s/%s refs %s | RC4b inv=sens %s inv-def %s | m3 %s | m1p %s/%s%s' % (
            e['cap'], e['eid'], e['no'], e['SP'], e['arms'], e['bound_ok'], e['N_null'], 'ok' if g1 else e['Npre'], 'ok' if g1in else e['Nin'], e['Nin_nz'] or '',
            e['sens'], e['N_diff'], e['N_diff_mem'], e['refs'], e['inv_eq_sens'], e['inv_vs_def'], e['m3'], e['m1p_Nem1_sens'], e['m1p_em1_eq_post'],
            ' | n_entry %d (PSInv %d) m2 raw %d m2p %d slots-game %s self %s' % (e['n_entry'], e['PSInv'], e['m2_raw'], e['m2p_vs_orig_pre'], e['slots_game'], e['selfcheck']) if 'n_entry' in e else ''))
json.dump(rows, open('C:/kyty/f287/f36b/sum_f36b.json', 'w'), indent=0, sort_keys=True)
