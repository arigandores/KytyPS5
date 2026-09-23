"""Auditor: dab106 ddt without the pairs that could hold the 07:27:03 heartbeat (blocks 22-25)."""
import re, statistics, math, json
rc = json.load(open('rc_dab106.json'))
dt = {}
NN = re.compile(rb'^FrameTrace: n=(\d+) ')
with open('C:/kyty/s106/log_dab106.txt', 'rb') as f:
    for l in f:
        if l.startswith(b'FrameTrace: '):
            dt[int(NN.match(l).group(1))] = int(re.search(rb' dt_us=(\d+)', l).group(1))
B = rc['paired_blocks']
bm = {b: statistics.fmean([dt[n] for n in range(1801 + 90*b, 1891 + 90*b)][60:89]) for b in B}
pairs = []
for q in range(0, max(B) + 1, 4):
    if q in bm: pairs += [(q, q+1), (q+3, q+2)]
for drop in ([], [(20, 21), (23, 22), (24, 25), (27, 26)]):
    d = [bm[b1] - bm[b0] for b0, b1 in pairs if (b0, b1) not in drop]
    m = statistics.fmean(d); se = statistics.stdev(d) / math.sqrt(len(d))
    print('dropped', drop, 'n', len(d), 'mean %.1f 2SE %.1f t %.2f' % (m, 2*se, m/se))
# cumulative frames to wall: estimate frame at 07:27:03.9 from stable frame 275 at 07:25:08.3
s = 0.0; n = 275
while s < 115.6e6:
    n += 1; s += dt.get(n, 31000)
print('estimated frame at 07:27:03.9:', n, 'block', (n - 1801) // 90, 'idx', (n - 1801) % 90)
