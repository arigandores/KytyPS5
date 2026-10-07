#!/usr/bin/env python3
"""F25a RC1 (HPP-660, Probe Designer): do the chains of the F20l3 reader reach the two places where a -w record may be cut by
kWLinesCap (f2307b02:src/common/diagB32.cpp:422 PickWaits: the closure is 3 iterations from vo / GuestGpu / flip / R >= 10 % threads
via waker1 / peer1; the rest is cut beyond 64)?
  E1  the 4th thread of a chain (step index 3): its records are outside the 3-iteration closure;
  E2  a thread reached by 'tpeer' (the -t peer of a mutex wait): the -t peer is not added to the closure set.
For every DiagB32 window of the given logs, the chain of the reader (its own function chain(), copy of e8ea0a57:docs/track-f/f20l3/
b32_read.py) from flip_slot and from vo_slot; a visit of E1 / E2 with the dominant state W and 0 printed records of that slot and kind
in a window whose w_cut grew (w_cut_d > 0) is 'EXPOSED' (the class there may come from a cut record).
Usage: edge_f25a.py <reader copy dir> <out.txt> <log> [<log> ...]"""
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import b32_read as R  # noqa: E402


def main():
    out, logs = sys.argv[2], sys.argv[3:]
    lines = []
    tot = dict(windows=0, chains=0, e1=0, e2=0, exposed=0, hows={})
    for p in logs:
        tag = re.sub(r'^.*log_|\.txt$', '', p)
        r = R.scan_b32(p)
        diag = r['diag']
        prev_wcut = 0
        for n in sorted(diag):
            d = diag[n]
            if d['hdr'] is None or d['x'] is None:
                continue
            wcut = R.num(d['x'].get('w_cut'), 0) or 0
            wcut_d = wcut - prev_wcut
            prev_wcut = wcut
            tot['windows'] += 1
            for hk in ('flip_slot', 'vo_slot'):
                holder = d['hdr'].get(hk)
                if holder is None or holder < 0:
                    continue
                steps = []
                cls, fam, path, role, note = R.chain(d, holder, dict(gbusy=None), dict(gbusy=None), 0, steps)
                tot['chains'] += 1
                for i, s in enumerate(steps):
                    tot['hows'][s['how']] = tot['hows'].get(s['how'], 0) + 1
                    e1 = i == 3
                    e2 = s['how'] == 'tpeer'
                    if not (e1 or e2):
                        continue
                    tot['e1' if e1 else 'e2'] += 1
                    row = dict((t['slot'], t) for t in d['t']).get(s['slot'])
                    st, x = R.dominant(row, d['hdr']['samples']) if row else (None, None)
                    recs = [w for w in d['w'] if w.get('slot') == s['slot'] and w.get('kind') == x] if st == 'W' else []
                    exposed = st == 'W' and not recs and wcut_d > 0
                    tot['exposed'] += exposed
                    lines.append('%s n %d holder %s: step %d via %s, state %s:%s, printed records %d, w_cut_d %d%s; class %s; path %s' % (
                        tag, n, hk, i, s['how'], st, x, len(recs), wcut_d, ' EXPOSED' if exposed else '', cls, ' | '.join(path)))
    lines.insert(0, 'windows %d, chains %d (flip_slot and vo_slot), steps by how %s; E1 visits %d, E2 visits %d, EXPOSED %d' % (
        tot['windows'], tot['chains'], sorted(tot['hows'].items()), tot['e1'], tot['e2'], tot['exposed']))
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:40]))


if __name__ == '__main__':
    main()
