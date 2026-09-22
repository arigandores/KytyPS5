"""Parent check: L and V2s/A over the eight V2-valid items (S2-S7, S9, S10), own code."""
import json
import random
import statistics

R = 'C:/kyty/s102/m5/real/'
bench = json.load(open(R + 'bench_m5cap102.json'))
plan = json.load(open(R + 'plan_m5cap102.json'))
idx = {e: i for i, e in enumerate(bench['events'])}
first = bench['fetches'][0]
print('fetch keys', sorted(first.keys()))
dkey = 'd' if 'd' in first else [k for k, v in first.items() if isinstance(v, list) and len(v) == len(bench['events'])][0]
EIGHT = ['S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S9', 'S10']
TEN = ['S%d' % i for i in range(1, 11)]
ev = {it: [idx[e] for e in plan['items'][it]['events']] for it in TEN}
rounds = {}
for f in bench['fetches']:
    rounds.setdefault(f['round'], {})[f['arm']] = f[dkey]


def S(d, items):
    return sum(d[i] for it in items for i in ev[it])


def stat(num, den, items):
    rs = sorted(rounds)
    per = [S(rounds[r][num], items) / S(rounds[r][den], items) for r in rs]
    med = statistics.median(per)
    rng = random.Random(102)
    boots = []
    for _ in range(20000):
        s = [per[rng.randrange(len(per))] for _ in per]
        boots.append(statistics.median(s))
    boots.sort()
    return med, boots[int(0.05 * len(boots))] - 1, boots[int(0.95 * len(boots)) - 1] - 1


for name, (num, den) in {'X': ('V2', 'A'), 'Y': ('V2', 'V2s'), 'L': ('V1', 'A'), 'V2s/A': ('V2s', 'A')}.items():
    for label, items in (('eight', EIGHT), ('ten', TEN)):
        m, lo, hi = stat(num, den, items)
        print('%-6s %-5s %.4f  CI(-1) [%.4f, %.4f]' % (name, label, m, lo, hi))
