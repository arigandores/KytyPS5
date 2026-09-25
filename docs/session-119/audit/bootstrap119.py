"""Quartet bootstrap of the sealed central G2 and the ceiling G2^ (no decision weight; the sealed rule is a point rule).
Each run's complete ABBA quartets are resampled with replacement, independently per run; every term is recomputed with
the sealed estimators (levels = median of block means, d = mean of paired differences).  Also: levels over all usable
blocks instead of only the selected ones."""
import random
import recount119 as R

runs = {}
usable = {}
for tag in ('sh119', 'mut119'):
    rows, lines, dups, other = R.parse('C:/kyty/s119/log_%s.txt' % tag)
    sel, pairs, excl, bad_idx, bad_arm, allb = R.population(rows)
    runs[tag] = (rows, sel, pairs)
g0 = R.g_terms(runs)


def resample(sel, rng):
    qs = sorted({b // 4 for b in sel})
    pick = [rng.choice(qs) for _ in qs]
    nsel, npairs = {}, []
    for i, q in enumerate(pick):
        base = 4 * i            # new synthetic quartet index keeps the ABBA positions
        for j in range(4):
            nsel[base + j] = sel[4 * q + j]
        npairs.append((base, base + 1))
        npairs.append((base + 3, base + 2))
    return nsel, npairs


rng = random.Random(119)
Gs, Gc = [], []
N = 2000
for _ in range(N):
    rr = {}
    for tag in ('sh119', 'mut119'):
        rows, sel, pairs = runs[tag]
        nsel, npairs = resample(sel, rng)
        rr[tag] = (rows, nsel, npairs)
    g = R.g_terms(rr)
    Gs.append(g['G2'])
    Gc.append(g['G2^'])
Gs.sort()
Gc.sort()
q = lambda a, p: a[int(p * (len(a) - 1))]
print('sealed G2 %.1f  bootstrap (%d quartet resamples): p2.5 %.1f  p50 %.1f  p97.5 %.1f  max %.1f  share >= 3000: %.4f'
      % (g0['G2'], N, q(Gs, 0.025), q(Gs, 0.5), q(Gs, 0.975), Gs[-1], sum(1 for x in Gs if x >= 3000) / N))
print('ceiling G2^ %.1f  bootstrap: p2.5 %.1f  p50 %.1f  p97.5 %.1f  share < 3000: %.4f'
      % (g0['G2^'], q(Gc, 0.025), q(Gc, 0.5), q(Gc, 0.975), sum(1 for x in Gc if x < 3000) / N))
