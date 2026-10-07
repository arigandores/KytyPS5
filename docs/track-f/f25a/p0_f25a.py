"""Track F link F25a (HPP-660): P(0 events) before the data, the stop rule and the lock budget of the F25 series.  ASCII only.

    python p0_f25a.py [--out <txt>]

Fixed p: P(0 in N) = (1 - p)^N; N for P(0) <= 0.05: ceil(ln 0.05 / ln(1 - p)).
Posterior form (uniform prior Beta(1, 1) + the inventory k of n): Beta(1 + k, 1 + n - k); predictive P(0 in N) = B(a, b + N) / B(a, b).
Stop rule of a level (f25a.md s4.4): N_min 5; K >= 3 -> READ; K = 0 at 5 -> go on to 14; K = 0 at 14 -> U2_L; K 1..2 -> go on to K = 3
or 20.  The expected number of tags under p is computed exactly over the binomial paths.
Lock: 7.8 min per tag (F20l3: 35 tags 2026-10-06 21:34:39Z .. 2026-10-07 02:07:41Z = 273.0 min).
"""
import math
import sys

MIN_PER_TAG = 273.0 / 35


def lbeta(a, b):
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def pred0(a, b, n):
    return math.exp(lbeta(a, b + n) - lbeta(a, b))


def stop_dist(p, n_min=5, n_zero=14, n_max=20, k_stop=3):
    """Distribution of (N, outcome) under a fixed p: walk the holds one by one."""
    states = {0: 1.0}            # K -> probability, before hold 1
    res = {}
    for n in range(1, n_max + 1):
        nxt = {}
        for k, pr in states.items():
            for hit, q in ((1, p), (0, 1 - p)):
                if q == 0:
                    continue
                kk = k + hit
                nxt[kk] = nxt.get(kk, 0) + pr * q
        states = {}
        for k, pr in nxt.items():
            if n >= n_min and k >= k_stop:
                res[(n, 'READ')] = res.get((n, 'READ'), 0) + pr
            elif n >= n_zero and k == 0:
                res[(n, 'U2_L')] = res.get((n, 'U2_L'), 0) + pr
            elif n == n_max:
                res[(n, 'U2prime_L')] = res.get((n, 'U2prime_L'), 0) + pr
            else:
                states[k] = states.get(k, 0) + pr
    return res


def main(argv):
    out = ['p0_f25a: fixed p']
    for p in (0.5, 0.4, 0.3, 0.2, 0.15, 0.1, 0.05):
        need = math.ceil(math.log(0.05) / math.log(1 - p))
        out.append('  p %.2f: P(0 | N=5) %.4f  P(0 | N=14) %.4f  P(0 | N=20) %.4f  N for P(0) <= 0.05: %d' % (
            p, (1 - p) ** 5, (1 - p) ** 14, (1 - p) ** 20, need))
    out.append('p0_f25a: posterior predictive (uniform prior + inventory)')
    for name, k, n in (('pot_treasure_cave (B36) 1 of 2', 1, 2), ('bonus_path_maker_mix (B40) 1 of 2', 1, 2),
                       ('both pooled 2 of 4', 2, 4), ('warm entries only 0 of 1 (v144_10)', 0, 1)):
        a, b = 1 + k, 1 + n - k
        out.append('  %s: Beta(%d, %d); P(0 | N=5) %.4f  P(0 | N=14) %.4f  P(0 | N=20) %.4f' % (
            name, a, b, pred0(a, b, 5), pred0(a, b, 14), pred0(a, b, 20)))
    out.append('p0_f25a: stop rule of one level (N_min 5, K=0 -> 14, K 1..2 -> K 3 or 20)')
    for p in (0.5, 0.3, 0.2, 0.1, 0.05, 0.0):
        d = stop_dist(p)
        en = sum(n * q for (n, _), q in d.items())
        po = {}
        for (n, o), q in d.items():
            po[o] = po.get(o, 0) + q
        out.append('  p %.2f: E[N] %.2f; P(READ) %.3f P(U2_L) %.3f P(U2prime_L) %.3f; sum %.6f' % (
            p, en, po.get('READ', 0), po.get('U2_L', 0), po.get('U2prime_L', 0), sum(po.values())))
    out.append('p0_f25a: lock budget (%.1f min per tag)' % MIN_PER_TAG)
    fixed = 2 + 4            # warm-up (cold) tags 2; controls: z0 x 2, PK-BL, PK-CL
    def en(p):
        return sum(n * q for (n, _), q in stop_dist(p).items())
    for name, n_series in (('minimum (p = 0.5, K = 3 at N 5 both levels)', 10), ('expected at p 0.5 both', 2 * en(0.5)),
                           ('expected at p 0.2 both', 2 * en(0.2)), ('expected at p 0.1 both', 2 * en(0.1)),
                           ('K = 0 both levels (U2 at 14)', 28), ('maximum (20 + 20 + repeats 6)', 46)):
        t = (fixed + n_series) * MIN_PER_TAG
        out.append('  %s: tags %.1f -> %.1f min = %.2f h' % (name, fixed + n_series, t, t / 60))
    ok = abs((1 - 0.5) ** 5 - 0.03125) < 1e-12 and math.ceil(math.log(0.05) / math.log(0.8)) == 14
    ok &= abs(pred0(2, 2, 5) - 6.0 / (7 * 8)) < 1e-12
    for p in (0.5, 0.2, 0.0):
        ok &= abs(sum(stop_dist(p).values()) - 1) < 1e-9
    out.append('CHECKS %s' % ('ALL OK' if ok else 'FAILED'))
    txt = '\n'.join(out) + '\n'
    if '--out' in argv:
        open(argv[argv.index('--out') + 1], 'w', encoding='ascii', newline='\n').write(txt)
    sys.stdout.write(txt)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
