"""Auditor: D in dwk104 by quartet contrast (46) vs pair contrast (92). Own parsing."""
import re, statistics, math, json
rc = json.load(open('rc_dwk104.json'))
NN = re.compile(rb'^FrameTrace(?:-draw)?: n=(\d+) ')
rows = {}
with open('C:/kyty/s104/log_dwk104.txt', 'rb') as f:
    for l in f:
        if l.startswith(b'FrameTrace: '):
            n = int(NN.match(l).group(1)); r = rows.setdefault(n, {})
            r['dt'] = int(re.search(rb' dt_us=(\d+)', l).group(1)); r['cpu'] = int(re.search(rb' cpu_gpu_us=(\d+)', l).group(1))
        elif l.startswith(b'FrameTrace-draw: '):
            n = int(NN.match(l).group(1)); rows.setdefault(n, {})['spin'] = int(re.search(rb' spin_gpu_us=(\d+)', l).group(1))
B = rc['paired_blocks']
bm = {b: statistics.fmean(rows[n]['dt'] - rows[n]['cpu'] + rows[n]['spin'] for n in range(1801 + 90*b, 1891 + 90*b)[60:89]) for b in B}
qs = [q for q in range(0, max(B) + 1, 4) if q in bm]
dq = [(bm[q+1] + bm[q+2]) / 2 - (bm[q] + bm[q+3]) / 2 for q in qs]
m = statistics.fmean(dq); se = statistics.stdev(dq) / math.sqrt(len(dq))
print('quartets', len(dq), 'D mean %.2f SE %.2f t %.2f' % (m, se, m / se))
dp = []
for q in qs: dp += [bm[q+1] - bm[q], bm[q+2] - bm[q+3]]
m = statistics.fmean(dp); se = statistics.stdev(dp) / math.sqrt(len(dp))
print('pairs', len(dp), 'D mean %.2f SE %.2f t %.2f' % (m, se, m / se))
