"""Session 125 audit (HPP-77): does the g2_119 print cpu_net 30 252.517 equal the arm-0 mean of sh119 on window
60..88 (g2_119 rule, s119 audit MAJOR 1)?  Own code via recount125.parse."""
import statistics, recount125 as rc
for tag in rc.LOGS:
    path, _ = rc.LOGS[tag]
    rows, blocks = rc.parse(path)
    arm_of = {b: a for a, b, fr, p in blocks}
    geom = {b: (fr, p) for a, b, fr, p in blocks}
    for lo, hi in ((60, 88), (10, 88)):
        win = {b: list(range(fr + 1, fr + p + 1))[lo:hi + 1] for b, (fr, p) in geom.items()
               if all(n in rows for n in range(fr + 1, fr + p + 1))}
        elig = {b: ns for b, ns in win.items() if min(ns) >= rc.FIRST_FRAME}
        used = set()
        for q in range(0, max(geom) + 1, 4):
            if all(k in elig for k in range(q, q + 4)):
                used.update(range(q, q + 4))
        sel = [rows[n] for b in sorted(used) if arm_of[b] == 0 for n in elig[b]]
        print(tag, 'window %d..%d' % (lo, hi), 'blocks', len([b for b in used if arm_of[b] == 0]), 'rows', len(sel),
              'cpu_net mean %.3f' % statistics.fmean(r['cpu_gpu_us'] - r['spin_gpu_us'] for r in sel))

# g2_119 level = median over the arm's selected blocks of per-block means (arm_levels); recompute that statistic
print('-- median of block means (the g2_119 level statistic)')
for tag in rc.LOGS:
    path, _ = rc.LOGS[tag]
    rows, blocks = rc.parse(path)
    arm_of = {b: a for a, b, fr, p in blocks}
    geom = {b: (fr, p) for a, b, fr, p in blocks}
    for lo, hi in ((60, 88), (10, 88)):
        win = {b: list(range(fr + 1, fr + p + 1))[lo:hi + 1] for b, (fr, p) in geom.items()
               if all(n in rows for n in range(fr + 1, fr + p + 1))}
        elig = {b: ns for b, ns in win.items() if min(ns) >= rc.FIRST_FRAME}
        used = set()
        for q in range(0, max(geom) + 1, 4):
            if all(k in elig for k in range(q, q + 4)):
                used.update(range(q, q + 4))
        bm = [statistics.fmean(rows[n]['cpu_gpu_us'] - rows[n]['spin_gpu_us'] for n in elig[b])
              for b in sorted(used) if arm_of[b] == 0]
        print(tag, 'window %d..%d' % (lo, hi), 'median of %d block means %.3f' % (len(bm), statistics.median(bm)))
