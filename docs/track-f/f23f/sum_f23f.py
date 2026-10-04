"""F23f (HPP-592, ROADMAP s122 item 498(d), (g)(5)): table by program and event from the replay lines (runs/rp_*.jsonl) with the
validity of item 498(d): valid = RC3 (a) executes (n_entry > 0 or the event writes an output: N_pre_def > 0), (b) bound module
= captured module and def bound = S12 bytes and layout equal (layout_f23f.json), (v) form A >= 1 (sites_f23f.json), (g) all
outputs compared (PS: blend off and write mask f on every bound target - pipeline state of the survey; CS: every read-write
descriptor, ranges > 64 MiB only when the SPIR-V writes nothing there) AND N_null = 0 AND references equal byte for byte.
N_diff = units of def != mask (= def != mem when the references are equal). Site use: n_t > 0 - used for form H; n_t > 0 and n_f > 0
- both forms; n_t = 0 - not used. Program reading of item 498(d)(iii). Output: sum_f23f.out.txt, sum_f23f.json."""
import json
import os
import sys

D = 'C:/kyty/f287/f23f/'
NL = chr(10)
INVALID_G = {'255ce6193a9e7938': 'blend on (target 0-2)', '2e2ae33a4d374e8f': 'blend on', '74bb8628d64f534c': 'blend on',
             'e14edf4a78d1a517': 'blend on (target 3; targets 0-2 write mask 0)', '52276fe1ba080bea': 'write mask 7 (alpha not written)'}
# CS: the bda_pagetable range (512 MiB) is not read; the SPIR-V has no store / atomic into it (wbuf_f23f: stores only to
# fault_buffer, bda_fault_page, lds_dwords) - an output it is not.


def tot(d):
    return sum(v for v in d.values() if v > 0) if isinstance(d, dict) else -1


def neg(d):
    return isinstance(d, dict) and any(v < 0 for v in d.values())


def main():
    layout = json.load(open(D + 'layout_f23f.json'))
    sites = json.load(open(D + 'sites_f23f.json'))
    rows, out = [], []
    progs = {}
    for cap in ('f13', 'k05'):
        p = D + 'runs/rp_%s.jsonl' % cap
        if not os.path.exists(p):
            continue
        for line in open(p):
            r = json.loads(line)
            h = r['prog']
            st = sites[h]['stage']
            dg = r.get('diag') if isinstance(r.get('diag'), dict) else {}
            n_entry = dg.get('n_entry', -1)
            writes = tot(r.get('N_pre_def', {}))
            a_exec = (n_entry > 0) if n_entry >= 0 else (writes > 0)
            b_ok = r.get('bound_is_capture_module') and r.get('bound_ok_def') and r.get('bound_ok_def2') and r.get('bound_ok_mask') and \
                r.get('bound_ok_mem') and layout.get(h, '').startswith('EQUAL')
            v_ok = len(sites[h]['sites']) >= 1
            g_ok = h not in INVALID_G and not neg(r.get('N_def2', {})) and not r.get('build_failed_def')
            n_null = tot(r.get('N_def2', {}))
            refs_eq = tot(r.get('N_mask_vs_mem', {})) == 0
            n_diff = tot(r.get('N_mask', {}))
            n_diff_mem = tot(r.get('N_mem', {}))
            # second null control: where the captured module is the S12 module byte for byte, orig and def are the same SPIR-V
            # in two replays - N(orig, def) != 0 is replay non-determinism too (RC2)
            same_bytes = r.get('bound_sha') == sites[h]['spv_sha']
            n_null2 = tot(r.get('N_orig_def', {})) if same_bytes else 0
            valid = bool(a_exec and b_ok and v_ok and g_ok and n_null == 0 and n_null2 == 0 and refs_eq)
            selfc = tot(dg.get('selfcheck_N', {})) if dg else -1
            nt, nf = dg.get('n_t', []), dg.get('n_f', [])
            use = []
            for k in range(len(nt)):
                use.append('both' if nt[k] > 0 and nf[k] > 0 else ('H' if nt[k] > 0 else 'unused'))
            counters_ok = bool(dg) and dg.get('bound_ok') and n_entry > 0 and selfc == 0
            row = dict(cap=cap, eid=r['eid'], prog=h, stage=st, a=a_exec, b=bool(b_ok), v=v_ok, g=g_ok,
                       g_why=INVALID_G.get(h, ''), n_entry=n_entry, writes=writes, N_null=n_null, refs_equal=refs_eq,
                       N_diff=n_diff, N_diff_mem=n_diff_mem, N_orig_def=tot(r.get('N_orig_def', {})), N_blend=tot(r.get('N_blend', {})), N_sens=tot(r.get('N_sens', {})),
                       valid=valid, N_null2=n_null2, n_t=nt, n_f=nf, use=use, counters_ok=counters_ok, diag_selfcheck=selfc,
                       large_not_read=r.get('outputs_not_read_large', []), outputs=len(r.get('outputs', [])))
            rows.append(row)
            pr = progs.setdefault(h, dict(stage=st, events=0, valid=0, valid_ndiff_pos=0, H=False, both=False))
            pr['events'] += 1
            if valid:
                pr['valid'] += 1
                if n_diff > 0:
                    pr['valid_ndiff_pos'] += 1
                if counters_ok and any(u in ('H', 'both') for u in use):
                    pr['H'] = True
                if counters_ok and any(u == 'both' for u in use):
                    pr['both'] = True
    out.append('cap  eid    prog             st a b v g  entry      writes  Nnull refsEq  Ndiff(mask) Ndiff(mem) orig/def blend   sens  VALID  n_t / n_f by site  [use]  diag-selfcheck')
    for r in rows:
        out.append('%-4s %-6d %s %s %d %d %d %d %10d %8d %6d %-6s %10d %10d %8d %6d %8d %-6s %s / %s %s %d%s' % (
            r['cap'], r['eid'], r['prog'], r['stage'], r['a'], r['b'], r['v'], r['g'], r['n_entry'], r['writes'], r['N_null'],
            r['refs_equal'], r['N_diff'], r['N_diff_mem'], r['N_orig_def'], r['N_blend'], r['N_sens'], 'YES' if r['valid'] else 'no',
            r['n_t'], r['n_f'], r['use'], r['diag_selfcheck'], ('  (g: %s)' % r['g_why']) if r['g_why'] else ''))
    out.append('')
    out.append('per program: events / valid / valid with N_diff > 0 / reading of item 498(d)(iii)')
    cand_ii = False
    any_h = False
    for h, p in sorted(progs.items(), key=lambda x: (x[1]['stage'], x[0])):
        if p['valid_ndiff_pos'] > 0:
            reading = 'N_diff > 0 on a valid event'
            cand_ii = True
        elif p['both']:
            reading = 'not found for both forms'
        elif p['H']:
            reading = 'not found for form H'
        else:
            reading = 'not determined'
        any_h |= p['H'] or p['both']
        p['reading'] = reading
        out.append('  %s %s events %d valid %d ndiff>0 %d -> %s' % (p['stage'], h, p['events'], p['valid'], p['valid_ndiff_pos'], reading))
    cand = '(ii) defect' if cand_ii else ('(iii) NE DEFEKT on the population "not found"' if any_h else '(iv) stage 2 not determined')
    out.append('candidate of item 498(d): %s' % cand)
    open(D + 'sum_f23f.out.txt', 'w', encoding='utf-8', newline=NL).write(NL.join(out) + NL)
    json.dump({'rows': rows, 'programs': progs, 'candidate': cand}, open(D + 'sum_f23f.json', 'w'), indent=1, sort_keys=True)
    print(NL.join(out))


if __name__ == '__main__':
    sys.exit(main())
