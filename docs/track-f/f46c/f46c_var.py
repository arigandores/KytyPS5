"""Track F link F46c (HPP-800): EXECUTOR VARIANTS of the series reading - written AFTER the seal, report rows only; the sealed scorer
f46c_vid.py is not changed and its rows stay the letter.  Each variant is printed beside the letter for the lead (question in the report).
  A  'hold' of the control (d)(1): the letter-reading of the seal takes every present common to f26s_c<k> and f26s_1; variant A takes only
     presents >= h0, h0 = the smallest present of a dcc_stale line after the entry line of f26s_1 (the present numbering of the video has
     no line of the level entry; the first event after it is the nearest present-stamped line).
  B  alignment by the event's own present: the seal compares the frames of two arms at the SAME present number; the entry of the level
     falls on different presents in different runs (event S<k> at 358 in f26s_1, 371 in f26s_0, 347 in f26s_1b, 340 in f26s_t1), so the
     same present is a different moment of the scene.  Variant B compares arm x at present f + (p_x(e) - p_1(e)) with f26s_1 at f, for V
     (t vs 1), the control (c vs 1, inside the hold of A) and the D numbers (t, 0, 1b vs 1), over W(e) of f26s_1.
usage: python f46c_var.py [--runs D] [--sheets]      -> runs/series/var.json, var.txt (and runs/series/var_sheets/)
ASCII only."""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location('f46c_vid', os.path.join(HERE, 'f46c_vid.py'))
V = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(V)


def shifted(ma, mb, presents, off_a, excl):
    hits, comp, best = [], 0, None
    for p in presents:
        pa = p + off_a
        if pa not in ma or p not in mb:
            continue
        if excl and (ma[pa][1] <= V.DARK or mb[p][1] <= V.DARK):
            continue
        comp += 1
        d = ma[pa][0] - mb[p][0]
        if best is None or d > best[1]:
            best = (p, d)
        if d >= V.THETA:
            hits.append(p)
    return dict(hits=len(hits), first=hits[0] if hits else None, comparable=comp, best=best)


def d_shift(rd, atts, offs, lo, hi, sheets_dir, k):
    base = os.path.dirname(rd)
    idx = dict((a, V.load_idx(os.path.join(base, 'rec_%s.mp4.idx' % t))[0]) for a, t in atts.items())
    rdr = dict((a, V.Reader(os.path.join(base, 'rec_%s.mp4' % t))) for a, t in atts.items())
    rows, keep = [], []
    for p in range(lo, hi + 1):
        q = dict((a, p + offs[a]) for a in atts)
        if any(q[a] not in (idx[a] or {}) for a in atts):
            continue
        fr = dict((a, rdr[a].at(idx[a][q[a]])) for a in atts)
        if any(v is None for v in fr.values()):
            continue
        mask = V.m_mask(fr['t'])
        n = int(mask.sum())
        if n < V.THETA:
            continue
        d0 = V.d_measure(fr['0'], fr['1'], mask)
        d1b = V.d_measure(fr['1b'], fr['1'], mask)
        dark = any(V.mean_of(v) <= V.DARK for v in fr.values())
        rows.append(dict(present=p, mask=n, d0=round(d0, 3), d1b=round(d1b, 3), diff=round(d0 - d1b, 3), cand=d0 - d1b >= V.D_MIN,
                         excluded=dark))
        if sheets_dir is not None:
            keep.append((p, d0 - d1b, dict((a, V.outline(v, mask)) for a, v in fr.items())))
            keep.sort(key=lambda z: -z[1])
            keep = keep[:6]
    for r in rdr.values():
        r.close()
    if sheets_dir is not None:
        for p, dd, fr in keep:
            V.save_sheet(os.path.join(sheets_dir, 'var_ev%d_%d.png' % (k, p)), [fr['t'], fr['0'], fr['1'], fr['1b']],
                         ['t%d aligned p%d' % (k, p), 'f26s_0 aligned', 'f26s_1 p%d' % p, 'f26s_1b aligned d %.1f' % dd])
    return rows


def main(argv):
    rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(V.G, 'runs')
    sheets = '--sheets' in argv
    sd = os.path.join(rd, 'series', 'var_sheets')
    if sheets:
        os.makedirs(sd, exist_ok=True)
    att = dict((b, V.settled(rd, b)) for b in ['f26s_0', 'f26s_1', 'f26s_1b'] + ['f26s_%s%d' % (x, k) for k in (1, 2, 3, 4) for x in 'tc'])
    r1 = att['f26s_1'][1]
    out = dict(arms=dict((b, a[0]) for b, a in att.items()), events=[])
    if r1 is None:
        print('f26s_1 not admitted')
        return 1
    h0 = min(d['present'] for d in r1['rows']['dcc_stale_after']) if r1['rows']['dcc_stale_after'] else None
    out['h0'] = h0
    m = dict((b, V.mtab(rd, a[0]) if a[0] else None) for b, a in att.items())
    for k in (1, 2, 3, 4):
        e1 = V.ev_of(r1, k)
        row = dict(k=k)
        out['events'].append(row)
        if e1 is None or not e1.get('found'):
            row['state'] = 'not found'
            continue
        p1 = e1['present']
        pres = {}
        for b in ('f26s_0', 'f26s_1b', 'f26s_t%d' % k, 'f26s_c%d' % k):
            e = V.ev_of(att[b][1], k) if att[b][1] else None
            pres[b] = e['present'] if e and e.get('found') else None
        row['event_present'] = dict(pres, f26s_1=p1)
        e0 = V.ev_of(att['f26s_0'][1], k)
        pe0 = e0['first_exec'][0]['present'] if e0 and e0.get('first_exec') else att['f26s_0'][1]['idx']['last_present']
        pe1 = e1['first_exec'][0]['present'] if e1.get('first_exec') else r1['idx']['last_present']
        lo, hi = V.window(p1, pe0, pe1)
        row['window_letter'] = [lo, hi]
        mc, mt, m1 = m['f26s_c%d' % k], m['f26s_t%d' % k], m['f26s_1']
        if mc is not None:
            allp = sorted(set(mc) & set(m1))
            holdp = [p for p in allp if h0 is not None and p >= h0]
            row['control_A_hold_same_present'] = V.compare(mc, m1, holdp, True)
            row['control_A_hold_same_present_noexcl'] = V.compare(mc, m1, holdp, False)
            oc = (pres['f26s_c%d' % k] - p1) if pres['f26s_c%d' % k] is not None else 0
            row['control_AB_hold_aligned'] = shifted(mc, m1, holdp, oc, True)
            row['control_magenta_presents'] = [p for p in allp if mc[p][0] >= V.THETA][:20]
            row['control_tint_applied'] = ((att['f26s_c%d' % k][1].get('rows') or {}).get('last_f5') or {}).get('f26_tint_applied')
        if mt is not None:
            ot = (pres['f26s_t%d' % k] - p1) if pres['f26s_t%d' % k] is not None else 0
            row['V_B_aligned'] = shifted(mt, m1, list(range(lo, hi + 1)), ot, True)
            row['V_B_aligned_noexcl'] = shifted(mt, m1, list(range(lo, hi + 1)), ot, False)
            row['t_magenta_presents'] = [p for p in sorted(mt) if mt[p][0] >= V.THETA][:20]
            row['t_tint_applied'] = ((att['f26s_t%d' % k][1].get('rows') or {}).get('last_f5') or {}).get('f26_tint_applied')
            if row['V_B_aligned']['hits'] and att['f26s_1b'][0]:
                offs = {'t': ot, '0': (pres['f26s_0'] or p1) - p1, '1': 0, '1b': (pres['f26s_1b'] or p1) - p1}
                dr = d_shift(rd, {'t': att['f26s_t%d' % k][0], '0': att['f26s_0'][0], '1': att['f26s_1'][0], '1b': att['f26s_1b'][0]}, offs,
                             lo, hi, sd if sheets else None, k)
                row['D_B_rows'] = dr[:40]
                row['D_B_candidates'] = [x['present'] for x in dr if x['cand'] and not x['excluded']]
    os.makedirs(os.path.join(rd, 'series'), exist_ok=True)
    json.dump(out, open(os.path.join(rd, 'series', 'var.json'), 'w', encoding='ascii'), sort_keys=True, indent=1)
    txt = ['F46c executor variants (report rows, not the letter): h0 %s; arms %s' % (h0, out['arms'])]
    for r in out['events']:
        txt.append('S%d %s' % (r['k'], json.dumps(dict((a, b) for a, b in r.items() if a != 'D_B_rows'), sort_keys=True)))
    open(os.path.join(rd, 'series', 'var.txt'), 'w', encoding='ascii', newline='\n').write('\n'.join(txt) + '\n')
    print('\n'.join(txt))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
