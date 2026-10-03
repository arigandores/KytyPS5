# F13b: unique non-FrameTrace, non-parameter log lines (digits folded) after level entry, with k of first/last and count.
import re, sys, collections
p = sys.argv[1]; card = int(sys.argv[2])
ent = b'GuestOut: Level has started: ending_boss_after_credit'
fold = re.compile(rb'(0x[0-9a-fA-F]+|\d+)')
k = -1; entered = False
seen = collections.OrderedDict()
gout = []
with open(p, 'rb') as f:
    for l in f:
        if not entered:
            if ent in l: entered = True; k = 0
            continue
        if l.startswith(b'FrameTrace'):
            if l.startswith(b'FrameTrace: n='): k += 1
            continue
        if l.startswith(b'\t') or l.startswith(b'['):
            continue
        if l.startswith(b'GuestOut'):
            if card - 300 <= k:
                gout.append((k, l.rstrip()[:240]))
        key = fold.sub(b'#', l.rstrip())[:160]
        e = seen.get(key)
        if e is None: seen[key] = [k, k, 1, l.rstrip()[:240]]
        else: e[1] = k; e[2] += 1
print('card', card, 'last k', k)
print('=== unique lines with first k >= card-300 (or last k >= card)')
for key, (a, b, n, ex) in seen.items():
    if a >= card - 300 or b >= card:
        print('first %6d last %6d n %7d | %s' % (a, b, n, ex.decode('utf-8', 'replace')))
print('=== GuestOut lines from card-300 (first 200)')
for k_, l in gout[:200]:
    print(k_, l.decode('utf-8', 'replace'))
print('GuestOut total from card-300:', len(gout))
