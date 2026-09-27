"""Sensitivity of ght123 to the watchdog routine tick that ran inside the sealed run (audit 123, own code).

Frame wall time is reconstructed from the scene-stable instant (ght123.json: launched + stable_s at stable_frame)
plus the cumulative dt_us of the following FrameTrace lines. Pairs whose blocks (pos 0..89) touch the tick interval
(activity log: lease 04:40:07.150Z .. release 04:40:29.783Z, = local UTC+2) widened by MARGIN seconds are dropped and
the estimator of the seal (window 10..87, stratified arm 1) is recomputed. Usage: python tick_sens123.py
"""
import json
import math
import re
from datetime import datetime

LOG = 'C:/kyty/s123/log_ght123.txt'
JS = 'C:/kyty/s123/ght123.json'
TICK = ('2026-09-27T06:40:06.802', '2026-09-27T06:40:29.783')   # routine.run_triggered .. lease_released, local
START, PERIOD = 1800, 90
FIELD = re.compile(rb'(\w+)=(-?\d+)')


def ts(s):
    return datetime.fromisoformat(s).timestamp()


def main():
    js = json.load(open(JS))
    at = js['attempts'][0]
    t_stable = ts(js['launched']) + at['stable_s']
    f_stable = at['stable_frame']
    M, X, arms = {}, {}, []
    with open(LOG, 'rb') as f:
        for line in f:
            if line.startswith(b'GateArm:'):
                arms.append(int(re.search(rb'arm=(\d)', line).group(1)))
            elif line.startswith(b'FrameTrace: '):
                d = {a.decode(): int(b) for a, b in FIELD.findall(line)}
                M[d['n']] = d
            elif line.startswith(b'FrameTrace-x: '):
                d = {a.decode(): int(b) for a, b in FIELD.findall(line)}
                X[d['n']] = d['skc_held']
    wall = {}
    t = t_stable
    for n in sorted(M):
        if n <= f_stable:
            continue
        t += M[n]['dt_us'] / 1e6
        wall[n] = t
    last = max(wall)
    print('reconstructed last frame %d at +%.1f s after stable (hold_s %.1f)' % (last, wall[last] - t_stable,
                                                                                 at['hold_s']))
    t0, t1 = ts(TICK[0]), ts(TICK[1])
    for margin in (0, 5, 15):
        ds = []
        hit = []
        for k in range(len(arms) // 2):
            bs = (2 * k, 2 * k + 1)
            fr = [START + 1 + PERIOD * b + p for b in bs for p in range(90)]
            if not all(n in M and n in X for n in fr):
                continue
            if any(t0 - margin <= wall.get(n, 0) <= t1 + margin for n in fr):
                hit.append(k)
                continue
            est = {}
            for b in bs:
                w = [START + 1 + PERIOD * b + p for p in range(10, 88)]
                if arms[b] == 0:
                    est[0] = sum(M[n]['dt_us'] for n in w) / 78
                else:
                    h = [M[n]['dt_us'] for n in w if X[n] >= 1]
                    o = [M[n]['dt_us'] for n in w if X[n] < 1]
                    est[1] = 0.5 * sum(h) / len(h) + 0.5 * sum(o) / len(o)
            ds.append(est[0] - est[1])
        m = sum(ds) / len(ds)
        se2 = 2 * math.sqrt(sum((x - m) ** 2 for x in ds) / (len(ds) - 1) / len(ds))
        print('margin %2d s: pairs hit by tick %s -> Delta %.1f +- %.1f us (%d pairs)' % (margin, hit, m, se2, len(ds)))


if __name__ == '__main__':
    main()
