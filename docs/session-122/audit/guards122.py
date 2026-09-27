# -*- coding: utf-8 -*-
"""Session 122 audit: the accepted design's guards (design/burn.md items 4, 6, 7, 8 as kept by design122.md) that the
seal pred/01_map122.md loosened or dropped, evaluated on the sealed runs. Report-only; never a verdict input.

  4  B window: burn_<t>_n per frame >= 0.95 and burn_<t>_ns per frame within [0.97 N, 1.03 N + 20 us]  (seal: +-5 %)
  6  coverage in BOTH arms: burn_<t>_seen per frame >= 0.95                                            (seal: B only, > 0)
  7  burn_late <= 1 % of armed frames                                                                  (seal: printed)
  8  DRS step: rt_kpx / rt_att per arm within 2 %                                                      (seal: absent)
     draw-adjusted estimator admitted only when |d draws| < 2SE(d draws)                               (seal: report-only)
Usage: python guards122.py <tag> [...]
"""
import sys

import recount122 as R

N = 2000.0


def guards(tag):
    gates, main, draw, x, lines = R.read(tag)
    period = gates[0][4]
    code = None
    for g in gates:
        if g[0] == 1:
            code = int(g[6].split('=')[1]) // 100000
            break
    t = {1: 'g', 8: 'p'}[code]
    win = {0: [], 1: []}
    armed_rows = []
    for i, g in enumerate(gates[:-1]):
        arm, frame = g[0], g[3]
        rows = [n for n in range(frame + R.OFFSET + R.LO, frame + R.OFFSET + R.HI + 1) if n in main and n in x]
        win[arm] += rows
        if arm == 1:
            armed_rows += [n for n in range(frame + R.OFFSET, frame + R.OFFSET + period) if n in x]
    B = win[1]
    per_n = sum(x[n].get('burn_%s_n' % t, 0) for n in B) / len(B)
    per_ns = sum(x[n].get('burn_%s_ns' % t, 0) for n in B) / len(B) / 1000.0
    cov = {a: sum(1 for n in win[a] if x[n].get('burn_%s_seen' % t, 0) > 0) / len(win[a]) for a in (0, 1)}
    late = sum(x[n].get('burn_late', 0) for n in armed_rows)
    drs = {}
    for a in (0, 1):
        kpx = sum(x[n].get('rt_kpx', 0) for n in win[a])
        att = sum(x[n].get('rt_att', 0) for n in win[a])
        drs[a] = kpx / att if att else None
    drs_rel = (drs[1] / drs[0] - 1) if drs[0] and drs[1] else None
    ok4 = per_n >= 0.95 and 0.97 * N <= per_ns <= 1.03 * N + 20
    ok6 = min(cov.values()) >= 0.95
    ok7 = late <= 0.01 * len(armed_rows)
    ok8 = drs_rel is not None and abs(drs_rel) <= 0.02
    print('%-9s code %d | 4 n/frame %.3f ns/frame %.1f -> %s | 6 seen A %.3f B %.3f -> %s | 7 late %d / %d armed rows '
          '(%.2f %%) -> %s | 8 rt_kpx/rt_att A %s B %s rel %s -> %s' % (
              tag, code, per_n, per_ns, 'ok' if ok4 else 'FAIL', cov[0], cov[1], 'ok' if ok6 else 'FAIL', late,
              len(armed_rows), 100.0 * late / len(armed_rows), 'ok' if ok7 else 'FAIL',
              '%.1f' % drs[0] if drs[0] else None, '%.1f' % drs[1] if drs[1] else None,
              '%+.4f' % drs_rel if drs_rel is not None else None, 'ok' if ok8 else 'FAIL/NA'))


if __name__ == '__main__':
    for tg in sys.argv[1:]:
        guards(tg)
