"""F23g (HPP-593, Red Team): own recount of the F23f replay lines (C:/kyty/f287/f23f/runs/rp_f13.jsonl, rp_k05.jsonl) - not the
F23f scorer. (1) validity by ROADMAP s122 item 498(d) + F23f's second null control, with ANY negative N of any arm = not valid;
(2) per-program reading of 498(d)(iii); (3) events whose diag counter storage (buffer, offset, element) is shared with an EARLIER
event of the same program in the same capture (the F23f diag 'before' is read without the replacement, so the earlier execution's
atomics land in 'after'); (4) events whose own outputs do not change in def (writes = N(pre, def) = 0); (5) the own-repeat files
of F23g (rp_f13_1082.json, rp_k05_83214.json, rp_k05_be4c_c.json): own SamplesPassed / PSInvocations / CSInvocations against F23f
n_entry, and n_entry(event) - n_entry(previous event sharing the storage). Output: recount_f23g.out.txt. ASCII only."""
import json
import os

F = 'C:/kyty/f287/f23f/runs/'
G = 'C:/kyty/f287/f23g/runs/'
NL = chr(10)
INVALID_G = {'255ce6193a9e7938', '2e2ae33a4d374e8f', '74bb8628d64f534c', 'e14edf4a78d1a517', '52276fe1ba080bea'}
out = []


def tot(d):
    return sum(d.values()) if isinstance(d, dict) else None


def anyneg(d):
    return isinstance(d, dict) and any(v < 0 for v in d.values())


sites = json.load(open('C:/kyty/f287/f23f/sites_f23f.json'))
layout = json.load(open('C:/kyty/f287/f23f/layout_f23f.json'))
rows = []
for cap in ('f13', 'k05'):
    for line in open(F + 'rp_%s.jsonl' % cap):
        rows.append((cap, json.loads(line)))
rows.sort(key=lambda x: (x[0], x[1]['eid']))
negs = 0
valid = {}
prog_read = {}
seen_store = {}
for cap, r in rows:
    h = r['prog']
    dg = r['diag'] if isinstance(r.get('diag'), dict) else {}
    fields = ['N_def2', 'N_mask', 'N_mem', 'N_mask_vs_mem', 'N_orig_def', 'N_pre_def', 'N_sens', 'N_blend']
    neg = [k for k in fields if anyneg(r.get(k))]
    negs += len(neg)
    same_bytes = r.get('bound_sha') == sites[h]['spv_sha']
    n_null = tot(r.get('N_def2'))
    n_null2 = tot(r.get('N_orig_def')) if same_bytes else 0
    refs_eq = tot(r.get('N_mask_vs_mem')) == 0
    n_diff = tot(r.get('N_mask'))
    b_ok = all(r.get(k) for k in ('bound_is_capture_module', 'bound_ok_def', 'bound_ok_def2', 'bound_ok_mask', 'bound_ok_mem')) and \
        layout.get(h, '').startswith('EQUAL')
    n_entry = dg.get('n_entry', -1)
    writes = tot(r.get('N_pre_def'))
    a = n_entry > 0 if n_entry >= 0 else (writes or 0) > 0
    v = bool(a and b_ok and h not in INVALID_G and not neg and n_null == 0 and n_null2 == 0 and refs_eq)
    key = (cap, dg.get('buffer'), dg.get('off'), dg.get('elem'), dg.get('base_word')) if dg else None
    shared = seen_store.get((h, key)) if key else None
    if key:
        seen_store.setdefault((h, key), r['eid'])
    valid[(cap, r['eid'])] = v
    nt = dg.get('n_t', [])
    if v:
        p = prog_read.setdefault(h, {'valid': 0, 'ndiff': 0, 'H': 0, 'both': 0, 'H_own': 0})
        p['valid'] += 1
        p['ndiff'] += 1 if n_diff else 0
        selfc = tot(dg.get('selfcheck_N')) if dg else None
        cok = bool(dg) and dg.get('bound_ok') and n_entry > 0 and selfc == 0
        if cok and any(x > 0 for x in nt):
            p['H'] += 1
            if shared is None and writes:
                p['H_own'] += 1
    out.append('%s %6d %s valid=%d writes=%s n_entry=%s n_t=%s shared_storage_with_earlier_eid=%s neg=%s' % (
        cap, r['eid'], h, v, writes, n_entry, nt, shared, neg))
out.append('negative N fields in all lines: %d' % negs)
out.append('valid events: %d' % sum(valid.values()))
for h, p in sorted(prog_read.items()):
    out.append('program %s: valid %d, valid with N_diff>0 %d, valid with counters ok and n_t>0 %d, of them with writes>0 and own counter storage %d' % (
        h, p['valid'], p['ndiff'], p['H'], p['H_own']))
# own repeat
for fn in ('rp_f13_1082.json', 'rp_k05_83214.json', 'rp_k05_be4c_c.json'):
    j = json.load(open(G + fn))
    cnt = {c['eid']: c['counters'] for c in j.get('counters', [])}
    for e in j['events']:
        c = cnt.get(e['eid'], {}).get('orig', {})
        ws = e.get('N_writes_def')
        out.append('own %s eid %d: SamplesPassed %s PSInvocations %s CSInvocations %s; writes(def) %s; N(def,sens) %s; Npre(orig,sens) %s' % (
            fn, e['eid'], c.get('7'), c.get('12'), c.get('13'), tot(ws), tot(e.get('N_def_sens')), tot(e.get('Npre_orig_sens'))))
# n_entry arithmetic for the be4c pairs sharing storage
f23 = {(cap, r['eid']): r for cap, r in rows}
for a, b, own in ((83214, 83338, 99), (122326, 122458, 48)):
    ea, eb = f23[('k05', a)]['diag'], f23[('k05', b)]['diag']
    out.append('be4c %d -> %d: storage %s/%s vs %s/%s; n_entry %d + own PSInvocations %d = %d (F23f %d) %s; n_t[0] %d + %d = %d (F23f %d) %s' % (
        a, b, ea['buffer'], ea['off'], eb['buffer'], eb['off'], ea['n_entry'], own, ea['n_entry'] + own, eb['n_entry'],
        'EQUAL' if ea['n_entry'] + own == eb['n_entry'] else 'DIFF', ea['n_t'][0], own, ea['n_t'][0] + own, eb['n_t'][0],
        'EQUAL' if ea['n_t'][0] + own == eb['n_t'][0] else 'DIFF'))
open('C:/kyty/f287/f23g/recount_f23g.out.txt', 'w', newline=NL).write(NL.join(out) + NL)
print(NL.join(out[-16:]))
