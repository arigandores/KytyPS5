import re, sys, statistics, collections
# Skeptic #1 on F1: histogram of post-stable bda_scan in an OLD log, to estimate base, per-rescan size R and k.
path, stable = sys.argv[1], int(sys.argv[2])
R = re.compile(rb'^FrameTrace-draw: n=(\d+).* bda_scan=(\d+) ')
post = []; pre = []; xrows = 0
with open(path, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace-x: n='):
            xrows += 1
            continue
        if not line.startswith(b'FrameTrace-draw: n='):
            continue
        m = R.match(line)
        if not m:
            continue
        n, s = int(m.group(1)), int(m.group(2))
        (post if n >= stable else pre).append(s)
print('xrows', xrows, 'post', len(post), 'pre', len(pre))
lo = [s for s in post if s < 500]
print('k0 frames', len(lo), 'median', statistics.median(lo) if lo else None, 'mean', round(statistics.mean(lo), 2) if lo else None)
for a, b in ((500, 1500), (1500, 2500), (2500, 3500), (3500, 4500), (4500, 10 ** 9)):
    v = [s for s in post if a <= s < b]
    if v:
        print('band', a, b, 'n', len(v), 'median', statistics.median(v), 'mean', round(statistics.mean(v), 1))
base = statistics.median(lo) if lo else 52
k1 = [s for s in post if 500 <= s < 1500]
Rsz = statistics.median(k1) - base if k1 else 1014
ks = collections.Counter(int(round((s - base) / Rsz)) if s > base else 0 for s in post)
print('base', base, 'R', Rsz, 'k histogram', sorted(ks.items()))
tot = len(post)
print('k shares', {k: round(v / tot, 4) for k, v in sorted(ks.items())})
kmean = sum(k * v for k, v in ks.items()) / tot
print('k mean', round(kmean, 4), 'post mean scan', round(statistics.mean(post), 1), 'post median', statistics.median(post))
for marked in (0, 2, 5, 10):
    est_post = statistics.mean(post) - base - kmean * marked
    pre_ex = sum(max(0, s - base) for s in pre)
    pre_ex_nobig = sum(max(0, s - base) for s in pre if s < 5000)
    allrows_hi = (est_post * len(post) + pre_ex) / xrows
    allrows_lo = (est_post * len(post)) / xrows
    print('marked/rescan', marked, 'post nwould est', round(est_post, 1), 'all-rows (pre as scan-base)', round(allrows_hi, 1),
          'all-rows (pre nwould=0)', round(allrows_lo, 1), 'pre no-burst', round((est_post * len(post) + pre_ex_nobig) / xrows, 1))
