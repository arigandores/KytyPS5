#!/usr/bin/env python3
"""traj113.py -- print a bda_scan trajectory of one or more logs (60-flip window medians) next to
draws / dt_us / buf_new, marking the stable frame and gate-arm starts. Read-only helper for the census.

  python traj113.py <log> [<log> ...] [--win 60] [--from N] [--to N]
"""
import sys
import os
import statistics

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census113 as C  # noqa: E402


def main(argv):
    win = 60
    lo, hi = None, None
    logs = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--win':
            win = int(argv[i + 1]); i += 2; continue
        if a == '--from':
            lo = int(argv[i + 1]); i += 2; continue
        if a == '--to':
            hi = int(argv[i + 1]); i += 2; continue
        logs.append(a); i += 1
    idx = C.json_index()
    for p in logs:
        meta = C.find_meta(p, idx)
        status, segs, mk = C.read_log(p)
        print('== %s status=%s stable=%s (%s) segments=%s gatearm_first=%s levels=%s' % (
            p, status, meta['stable'], meta['stable_src'], [len(s) for s in segs], mk['gatearm_first_frame'],
            mk['levels'][:4]))
        if not segs:
            continue
        rows = segs[-1]
        for s in range(0, len(rows), win):
            w = rows[s:s + win]
            n0 = w[0].get('n')
            if (lo is not None and n0 < lo) or (hi is not None and n0 > hi):
                continue

            def med(k):
                v = [r.get(k) for r in w if r.get(k) is not None]
                return statistics.median(v) if v else None
            b = [r.get('bda_scan') for r in w if r.get('bda_scan') is not None]
            print('n=%6d  bda med=%7s min=%6s max=%6s  draws=%6s dt=%7s buf_new=%5s bufepoch=%7s img_new=%4s arm=%s%s' % (
                n0, med('bda_scan'), min(b) if b else None, max(b) if b else None, med('draws'), med('dt_us'),
                med('buf_new'), med('bufepoch'), med('img_new'), med('arm'),
                '  <- stable' if n0 <= meta['stable'] < n0 + win else ''))


if __name__ == '__main__':
    main(sys.argv[1:])
