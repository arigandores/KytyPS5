"""F36a (HPP-758, ROADMAP s122 item 687(e)(1)-(2)): table of the replay set (runs/rp_k0*.jsonl) by the members of section 0.6 of
f36a.md: RC3 (bound modules, all outputs read), N_null, references equal, G1 (Npre = 0 for def, mask, mem, sens, orig2, diag without
the slot words), G2 (n_entry = PSInvocations), G3 (SamplesPassed > 0), G4 (sens > 0); N_diff; n_t / n_f by site (read when the
self-check is 0). The first failing member in the order RC3, N_null, refs, G3, G1, G2, G4 is named. Output: sum_f36a.out.txt,
sum_f36a.json, tables_f36a.md (markdown table for the report)."""
import json
import sys

D = 'C:/kyty/f287/f36a/'
NL = chr(10)


def tot(d):
    if d is None:
        return None
    if any(v < 0 for v in d.values()):
        return -1
    return sum(d.values())


def nz(d):
    return {k: v for k, v in (d or {}).items() if v != 0}


def main():
    rows, res = [], []
    for k in '02 03 04 05 06 07 08'.split():
        for line in open(D + 'runs/rp_k%s.jsonl' % k):
            r = json.loads(line)
            e = {'snap': 'k' + k, 'eid': r['eid'], 'exec': r['exec_no'], 'PSInv': r['PSInvocations'], 'SP': r['SamplesPassed'],
                 'pre_eid': r.get('pre_eid'), 'group': r.get('group_events')}
            arms = ('orig', 'def', 'mask', 'mem', 'sens', 'diag', 'orig2')
            e['bound_ok'] = all(r.get('bound_ok_' + a) for a in arms)
            e['large'] = r.get('outputs_not_read_large')
            e['writes'] = tot(r.get('writes'))
            e['writes_def'] = tot(r.get('writes_def'))
            e['N_null'] = tot(r.get('N_null'))
            e['N_mask_mem'] = tot(r.get('N_mask_mem'))
            e['Npre'] = {a: tot(r.get('Npre_' + a)) for a in ('def', 'mask', 'mem', 'sens', 'orig2', 'diag')}
            e['n_entry'] = r.get('n_entry')
            e['n_t'], e['n_f'] = r.get('n_t'), r.get('n_f')
            e['selfcheck'] = tot(r.get('selfcheck'))
            e['sens'] = tot(r.get('sens'))
            e['N_diff'] = tot(r.get('N_diff_mask'))
            e['N_diff_mem'] = tot(r.get('N_diff_mem'))
            e['N_orig_def'] = tot(r.get('N_orig_def'))
            e['nz'] = {'writes': nz(r.get('writes')), 'sens': nz(r.get('sens')), 'N_diff': nz(r.get('N_diff_mask')),
                       'Npre_sens': nz(r.get('Npre_sens')), 'Npre_def': nz(r.get('Npre_def')), 'N_null': nz(r.get('N_null'))}
            e['samplers'] = r.get('samplers')
            m = []
            m.append(('RC3', e['bound_ok'] and not e['large']))
            m.append(('N_null', e['N_null'] == 0))
            m.append(('refs', e['N_mask_mem'] == 0))
            m.append(('G3', e['SP'] > 0))
            m.append(('G1', all(v == 0 for v in e['Npre'].values())))
            m.append(('G2', e['n_entry'] == e['PSInv']))
            m.append(('G4', (e['sens'] or 0) > 0))
            e['members'] = dict(m)
            fail = [n for n, ok in m if not ok]
            e['valid'] = not fail
            e['first_fail'] = fail[0] if fail else None
            e['fails'] = fail
            e['counters_read'] = e['selfcheck'] == 0
            res.append(e)
    hdr = '| Снимок | EID | № | PSInv | SP | `pre_eid` | writes (orig / def) | `N_null` | `N(mask,mem)` | `Npre` def/mask/mem/sens/orig2/diag | `n_entry` | Г2 | самопроверка | `sens` | `N_diff` | `n_t` / `n_f` | Годно (непрошедшие члены) |'
    md = [hdr, '|' + '---|' * 17]
    for e in res:
        npre = '/'.join(str(e['Npre'][a]) for a in ('def', 'mask', 'mem', 'sens', 'orig2', 'diag'))
        cnt = '%s / %s' % (e['n_t'], e['n_f']) if e['counters_read'] else '%s / %s (не читаются)' % (e['n_t'], e['n_f'])
        md.append('| %s | %d | %d | %d | %d | %s | %s / %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            e['snap'], e['eid'], e['exec'], e['PSInv'], e['SP'], e['pre_eid'], e['writes'], e['writes_def'], e['N_null'], e['N_mask_mem'],
            npre, e['n_entry'], '✓' if e['members']['G2'] else '✗', e['selfcheck'], e['sens'], e['N_diff'], cnt,
            '**да**' if e['valid'] else 'нет (' + ', '.join(e['fails']) + ')'))
    out = []
    for e in res:
        out.append(json.dumps({k: e[k] for k in ('snap', 'eid', 'exec', 'PSInv', 'SP', 'pre_eid', 'writes', 'writes_def', 'N_null', 'N_mask_mem', 'Npre',
                                                 'n_entry', 'selfcheck', 'sens', 'N_diff', 'N_diff_mem', 'n_t', 'n_f', 'valid', 'fails', 'N_orig_def')}, sort_keys=True))
    valid = [e for e in res if e['valid']]
    out.append('events %d, valid %d, valid with N_diff > 0: %d, valid with n_t > 0 on a site (counters read): %d, with n_t > 0 and n_f > 0: %d' % (
        len(res), len(valid), sum(1 for e in valid if e['N_diff'] != 0),
        sum(1 for e in valid if e['counters_read'] and any(x > 0 for x in e['n_t'])),
        sum(1 for e in valid if e['counters_read'] and any(t > 0 and f > 0 for t, f in zip(e['n_t'], e['n_f'])))))
    from collections import Counter
    out.append('first failing member: %s' % dict(Counter(e['first_fail'] for e in res)))
    out.append('fails by member: %s' % dict(Counter(f for e in res for f in e['fails'])))
    out.append('pre_eid = first event of group - 1, groups of 3 events with an Indirect sub-command: %d of %d' % (
        sum(1 for e in res if e['group'] and len(e['group']) == 3), len(res)))
    json.dump(res, open(D + 'sum_f36a.json', 'w'), indent=1, sort_keys=True)
    open(D + 'sum_f36a.out.txt', 'w', newline=NL).write(NL.join(out) + NL)
    open(D + 'tables_f36a.md', 'w', encoding='utf-8', newline=NL).write(NL.join(md) + NL)
    print(NL.join(out[-4:]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
