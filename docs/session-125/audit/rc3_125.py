"""Session 125 audit (HPP-77): RC3 draft artefact of review125b re-done on the corrected population (GateArm blocks,
g2_119 rule, window 10..88 p.55(b)) and on the rows125 reproduction.  Own code; imports only recount125 (audit's).
A6 formula of design125 rev 2 s3.1 with D_N = a * cpu_net_N (no real delay in any frame):
  artefact = mean_N max(0, a*cpu_net_N - (M - W2-)),  M - W2- = 21 637.7 us (g2_119 print)."""
import statistics
import recount125 as rc

M_MINUS_W2 = 26767.8 - 5130.1


def pop(tag):
    path, excl = rc.LOGS[tag]
    rows, blocks = rc.parse(path)
    arm_of = {b: a for a, b, fr, p in blocks}
    geom = {b: (fr, p) for a, b, fr, p in blocks}
    win = {}
    for b, (fr, p) in geom.items():
        ns = list(range(fr + 1, fr + p + 1))
        if all(n in rows for n in ns):
            win[b] = ns[rc.WIN_LO:rc.WIN_HI + 1]
    elig = {b: ns for b, ns in win.items() if min(ns) >= rc.FIRST_FRAME}
    used = set()
    for q in range(0, max(geom) + 1, 4):
        if all(k in elig for k in range(q, q + 4)):
            used.update(range(q, q + 4))
    G = [rows[n] for b in sorted(used) if arm_of[b] == 0 for n in elig[b]]
    grp = {}
    for n, r in rows.items():
        if 'blk' in r and 'arm' in r:
            grp.setdefault(r['blk'], []).append(n)
    R = []
    for b, ns in grp.items():
        if b in excl:
            continue
        ns.sort()
        R += [rows[n] for i, n in enumerate(ns) if rows[n]['arm'] == 0 and rc.WIN_LO <= i <= rc.WIN_HI
              and all(k in rows[n] for k in rc.NEED)]
    return G, R


for tag in rc.LOGS:
    G, R = pop(tag)
    for name, sel in (('G corrected', G), ('R rows125', R)):
        c = [r['cpu_gpu_us'] - r['spin_gpu_us'] for r in sel]
        arts = []
        for a in (0.5, 0.555):
            arts.append(statistics.fmean(max(0.0, a * x - M_MINUS_W2) for x in c))
        share = sum(1 for x in c if x > M_MINUS_W2 / 0.5) / len(c)
        print('%-6s %-12s rows %d cpu_net min %.0f med %.0f mean %.0f max %.0f | artefact a=0.5 %.1f a=0.555 %.1f'
              ' | share cpu_net > %.0f: %.2f %%' % (tag, name, len(c), min(c), statistics.median(c),
                                                    statistics.fmean(c), max(c), arts[0], arts[1],
                                                    M_MINUS_W2 / 0.5, 100 * share))
