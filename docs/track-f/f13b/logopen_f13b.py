# F13b: file opens ("\t path = ...") after the level entry of a f13a log: count, last k, histogram per 60 rows, last 25.
import re, sys, collections
p = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f13a/log_f13_k.txt'
ent = b'GuestOut: Level has started: ending_boss_after_credit'
k = -1; entered = False; opens = []
with open(p, 'rb') as f:
    for l in f:
        if not entered:
            if ent in l: entered = True; k = 0
            continue
        if l.startswith(b'FrameTrace: n='): k += 1; continue
        if re.match(rb'^\t\s*path\s*=', l): opens.append((k, l.strip()[:200]))
print('opens after entry', len(opens), 'first k', opens[0][0] if opens else None, 'last k', opens[-1][0] if opens else None, 'rows', k)
c = collections.Counter(kk // 60 for kk, _ in opens)
print('opens per 60 rows (bucket: n):', sorted(c.items()))
for kk, s in opens[-25:]: print(kk, s.decode('utf-8', 'replace'))
