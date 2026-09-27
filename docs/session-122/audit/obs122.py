# -*- coding: utf-8 -*-
"""Session 122 audit: report-only observations on the sealed burn ABBAs (NOT pre-registered, never a verdict input).

Reuses the auditor's own recount122.py (block/pair construction), not map122.py. For every population pair prints the
per-pair B-A difference with 2SE of: dt_us, cpu_gpu_us, (dt_us - cpu_gpu_us), cpu_main_us, semwait_us, rec_spin_us
(-x), and the B-window rows whose burn counter reads 0 or >= 1.5 doses (burn key pairing).
Usage: python obs122.py <tag> [...]
"""
import math
import sys

import recount122 as R


def m2se(v):
    m = sum(v) / len(v)
    s = math.sqrt(sum((a - m) ** 2 for a in v) / (len(v) - 1))
    return m, 2 * s / math.sqrt(len(v))


def obs(tag):
    gates, main, draw, x, lines = R.read(tag)
    period = gates[0][4]
    blocks = []
    for i, g in enumerate(gates):
        arm, frame = g[0], g[3]
        win = list(range(frame + R.OFFSET + R.LO, frame + R.OFFSET + R.HI + 1))
        allrows = [n for n in range(frame + R.OFFSET, frame + R.OFFSET + period) if n in main]
        blocks.append(dict(arm=arm, win=win, allrows=allrows,
                           complete=(i + 1 < len(gates)) and all(n in main for n in win)))
    code = int(gates[1][6].split('=')[1]) // 100000 if gates[1][0] == 1 else int(gates[0][6].split('=')[1]) // 100000
    grp = {1: 'g', 8: 'p'}[code]
    cols = {'dt': lambda n: main[n]['dt_us'], 'cpu_gpu': lambda n: main[n]['cpu_gpu_us'],
            'dt-cpu_gpu': lambda n: main[n]['dt_us'] - main[n]['cpu_gpu_us'],
            'cpu_main': lambda n: main[n]['cpu_main_us'], 'semwait': lambda n: main[n]['semwait_us'],
            'rec_spin': lambda n: x[n].get('rec_spin_us', 0), 'draws': lambda n: main[n]['draws']}
    diffs = {k: [] for k in cols}
    zero, dbl, nb = 0, 0, 0
    for k in range(0, len(blocks) - 1, 2):
        a, b = blocks[k], blocks[k + 1]
        if not (a['complete'] and b['complete']):
            continue
        if any(main[n]['dt_us'] >= 500000 for bb in (a, b) for n in bb['allrows']):
            continue
        A, B = (a, b) if a['arm'] == 0 else (b, a)
        ra = [n for n in A['win'] if main[n]['draws'] > 300]
        rb = [n for n in B['win'] if main[n]['draws'] > 300]
        for c, f in cols.items():
            diffs[c].append(sum(f(n) for n in rb) / len(rb) - sum(f(n) for n in ra) / len(ra))
        for n in rb:
            v = x[n].get('burn_%s_ns' % grp, 0) / 1000.0
            nb += 1
            zero += v == 0
            dbl += v >= 3000
    print('%s (code %d, %d pairs)' % (tag, code, len(diffs['dt'])))
    for c, v in diffs.items():
        m, se = m2se(v)
        print('   d %-11s %+9.1f +- %7.1f' % (c, m, se))
    print('   B-window rows: %d, burn 0: %d, burn >= 1.5 doses: %d' % (nb, zero, dbl))


if __name__ == '__main__':
    for t in sys.argv[1:]:
        obs(t)
