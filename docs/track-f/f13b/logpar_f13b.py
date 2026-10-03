# F13b: parameter-line keys ("\t key = value") per window: before card end, card..+600 rows, after; plus path-like values after card end.
import re, sys, collections
p = sys.argv[1]; card = int(sys.argv[2])
ent = b'GuestOut: Level has started: ending_boss_after_credit'
rk = re.compile(rb'^\t\s*([A-Za-z_][\w ]*?)\s*[=:]')
k = -1; entered = False
h = collections.defaultdict(collections.Counter)
paths = collections.OrderedDict()
with open(p, 'rb') as f:
    for l in f:
        if not entered:
            if ent in l: entered = True; k = 0
            continue
        if l.startswith(b'FrameTrace: n='):
            k += 1; continue
        if not l.startswith(b'\t'):
            continue
        m = rk.match(l)
        key = m.group(1).decode() if m else '?'
        w = 'A' if k < card else ('B' if k < card + 600 else 'C')
        h[w][key] += 1
        if k >= card - 60 and (b'/' in l or b'.' in l and b'0x' not in l):
            s = l.strip()[:200]
            if s not in paths: paths[s] = k
na = card; nb = 600; nc = max(1, k - card - 600)
print('card', card, 'last', k, 'rows A', na, 'B', nb, 'C', nc)
keys = set(h['A']) | set(h['B']) | set(h['C'])
for key in sorted(keys, key=lambda x: -(h['A'][x] + h['B'][x] + h['C'][x])):
    a, b, c = h['A'][key], h['B'][key], h['C'][key]
    print('%-36s A %8d (%.2f/row)  B %7d (%.2f/row)  C %8d (%.2f/row)' % (key, a, a / na, b, b / nb, c, c / nc))
print('=== path-like param values from card-60')
for s, kk in list(paths.items())[:200]:
    print(kk, s.decode('utf-8', 'replace'))
