"""Auditor: sign-flip permutation test and bootstrap CI for dab106/gw106 per-pair ddt (quantized outcome)."""
import re, json, statistics, random, sys
log, rcj = sys.argv[1], sys.argv[2]
rc = json.load(open(rcj)); B = rc['paired_blocks']
dt = {}
NN = re.compile(rb'^FrameTrace: n=(\d+) ')
for l in open(log, 'rb'):
    if l.startswith(b'FrameTrace: '):
        dt[int(NN.match(l).group(1))] = int(re.search(rb' dt_us=(\d+)', l).group(1))
bm = {b: statistics.fmean([dt[n] for n in range(1801 + 90*b, 1891 + 90*b)][60:89]) for b in B}
d = []
for q in range(0, max(B) + 1, 4):
    if q in bm: d += [bm[q+1] - bm[q], bm[q+2] - bm[q+3]]
obs = statistics.fmean(d)
rnd = random.Random(1)
N = 20000
ext = sum(1 for _ in range(N) if abs(statistics.fmean(x if rnd.random() < 0.5 else -x for x in d)) >= abs(obs))
boots = sorted(statistics.fmean(rnd.choice(d) for _ in d) for _ in range(5000))
print(log.split('/')[-1], 'mean %.1f  sign-flip p %.4f  bootstrap 95%% CI [%.1f, %.1f]  P(boot mean > -100) %.3f' % (
    obs, ext / N, boots[125], boots[4874], sum(1 for b in boots if b > -100) / len(boots)))
