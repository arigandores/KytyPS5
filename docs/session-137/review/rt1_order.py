"""Session 137 step 1 (HPP-251, Red Team): offline rows on the two ABBA logs of session 136 already read (kp136 sealed,
s1s136 smoke) - NOT a re-reading, a design check of the pooling of item 190 (e)(4).  Blocks by GateArm (smk137.blocks_of),
window 10-88 of item 55 (b), pairs (2k, 2k + 1).  Prints: pairs, the order of each pair ((0,1) or (1,0)), the simple
Delta dt_us by order with its SE, the first pair's Delta, and the slope of the arm-0 block means over the block index."""
import hashlib
import math
import sys

sys.path.insert(0, 'C:/kyty/s137')
import smk137 as S  # noqa: E402


def ms(xs):
    n = len(xs)
    if n < 2:
        return (xs[0] if xs else float('nan')), float('nan'), n
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return m, sd / math.sqrt(n), n


print('rt1_order sha256 %s' % hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
for tag in ('kp136', 's1s136'):
    p = S.parse('C:/kyty/s136/log_' + tag + '.txt')
    bl = S.blocks_of(p)
    mean = [None if b['rows'] is None else sum(r['dt_us'] for r in b['rows']) / len(b['rows']) for b in bl]
    pairs = []
    k = 0
    while k + 1 < len(bl):
        x, y = bl[k], bl[k + 1]
        if x['rows'] is not None and y['rows'] is not None and {x['arm'], y['arm']} == {0, 1}:
            d = (mean[k + 1] - mean[k]) if x['arm'] == 0 else (mean[k] - mean[k + 1])
            pairs.append(((x['arm'], y['arm']), d, k))
        k += 2
    o01 = [d for o, d, _ in pairs if o == (0, 1)]
    o10 = [d for o, d, _ in pairs if o == (1, 0)]
    a, b, c = ms([d for _, d, _ in pairs]), ms(o01), ms(o10)
    bal = (b[0] + c[0]) / 2
    bal_se = math.sqrt(b[1] ** 2 + c[1] ** 2) / 2
    a0 = [(i, m) for i, (bb, m) in enumerate(zip(bl, mean)) if m is not None and bb['arm'] == 0]
    n0 = len(a0)
    xm = sum(i for i, _ in a0) / n0
    ym = sum(m for _, m in a0) / n0
    slope = sum((i - xm) * (m - ym) for i, m in a0) / sum((i - xm) ** 2 for i, _ in a0)
    print('%s: blocks %d, pairs %d (order (0,1) %d, (1,0) %d); simple Delta dt_us %.1f +- %.1f (2SE); by order (0,1) %.1f +- %.1f, '
          '(1,0) %.1f +- %.1f; order-balanced %.1f +- %.1f; first pair (block %d, order %s) %.1f; arm-0 block means: first '
          '%.1f, last %.1f, OLS slope %.2f us/block over %d blocks' % (
              tag, len(bl), len(pairs), len(o01), len(o10), a[0], 2 * a[1], b[0], 2 * b[1], c[0], 2 * c[1], bal, 2 * bal_se,
              pairs[0][2], pairs[0][0], pairs[0][1], a0[0][1], a0[-1][1], slope, n0))
print('ALL DONE')
