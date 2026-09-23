"""Auditor: distribution of per-row dt and per-pair ddt (reads rc_*.json + log). Own parsing."""
import json, re, sys, statistics, collections
log, rcj = sys.argv[1], sys.argv[2]
rc = json.load(open(rcj))
KV = re.compile(rb' dt_us=(\d+)')
NN = re.compile(rb'^FrameTrace: n=(\d+) ')
dt = {}
with open(log, 'rb') as f:
    for l in f:
        if l.startswith(b'FrameTrace: '):
            dt[int(NN.match(l).group(1))] = int(KV.search(l).group(1))
blocks = rc['paired_blocks']
arm = lambda b: (0, 1, 1, 0)[b % 4]
rows = {b: [dt[n] for n in range(1801 + 90 * b, 1891 + 90 * b)][60:89] for b in blocks}
allrows = [v for b in blocks for v in rows[b]]
h = collections.Counter(min(v // 2000 * 2, 80) for v in allrows)
print('dt histogram (ms bins of 2):', sorted(h.items()))
for a in (0, 1):
    vs = [v for b in blocks if arm(b) == a for v in rows[b]]
    print('arm', a, 'rows', len(vs), 'mean', round(statistics.fmean(vs), 1), 'median', statistics.median(vs),
          '<20ms', sum(v < 20000 for v in vs), '>40ms', sum(v > 40000 for v in vs), 'p10', sorted(vs)[len(vs)//10], 'p90', sorted(vs)[len(vs)*9//10])
pairs = []
for q in range(0, max(blocks) + 1, 4):
    if q in rows:
        pairs += [(q, q + 1), (q + 3, q + 2)]
d = [statistics.fmean(rows[b1]) - statistics.fmean(rows[b0]) for b0, b1 in pairs]
print('pairs', len(d), 'sorted ddt:', [round(x) for x in sorted(d)])
# remove the 5 most negative pairs
s = sorted(d)
for k in (0, 3, 5, 10):
    x = s[k:]
    m = statistics.fmean(x); se = statistics.stdev(x) / len(x) ** 0.5
    print('drop %d most negative: mean %.1f 2SE %.1f t %.2f' % (k, m, 2 * se, m / se))
# sign test
neg = sum(1 for x in d if x < 0); pos = sum(1 for x in d if x > 0)
from math import comb
n = neg + pos
p = sum(comb(n, i) for i in range(0, min(neg, pos) + 1)) / 2 ** n * 2
print('sign test neg %d pos %d two-sided p %.4f' % (neg, pos, p))
# first half vs second half of the run
h1, h2 = d[:len(d)//2], d[len(d)//2:]
print('first-half mean %.1f second-half mean %.1f' % (statistics.fmean(h1), statistics.fmean(h2)))
