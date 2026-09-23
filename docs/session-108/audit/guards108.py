"""Audit 108: guard counters over whole logs (sync compiles, prefetch have/new, family look/skip), by phase."""
import json
import sys

for tag in sys.argv[1:]:
    d = json.load(open('C:/kyty/s108/audit108/p_%s.json' % tag))
    fr = {int(k): v for k, v in d['frames'].items()}
    ns = sorted(fr)
    keys = ('cs_sync_new', 'cs_sync_wait', 'cspf_have', 'cspf_new', 'cspfam_look', 'cspfam_skip', 'dispatches')
    tot = {k: sum(fr[n].get(k, 0) for n in ns) for k in keys}
    missing = {k: sum(1 for n in ns if k not in fr[n]) for k in keys}
    print('==', tag, 'rows', len(ns), 'n', ns[0], '..', ns[-1])
    print('  totals', tot)
    print('  rows missing field', missing)
    # first rows where each counter is non-zero
    for k in ('cs_sync_new', 'cs_sync_wait', 'cspf_new', 'cspfam_skip', 'cspfam_look'):
        nz = [n for n in ns if fr[n].get(k, 0)]
        print('  %-12s nonzero rows %5d first %s last %s' % (k, len(nz), nz[:5], nz[-3:]))
    # phases: split by dispatches level / draws; print per 500-frame windows the sums
    step = 1000
    print('  window     dt_ms_mean draws cspf_have cspf_new look skip sync_new sync_wait')
    for w in range(ns[0], ns[-1] + 1, step):
        rows = [fr[n] for n in range(w, w + step) if n in fr]
        if not rows:
            continue
        s = lambda k: sum(r.get(k, 0) for r in rows)
        print('  %5d-%5d %8.1f %6.0f %8d %6d %6d %6d %4d %4d' % (
            w, w + step - 1, s('dt_us') / len(rows) / 1000, s('draws') / len(rows), s('cspf_have'), s('cspf_new'),
            s('cspfam_look'), s('cspfam_skip'), s('cs_sync_new'), s('cs_sync_wait')))
