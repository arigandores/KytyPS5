# F13b: histogram of HLE calls (lines "[tid][time] lib::func()") per window around the card end of a f13a log.
import re, sys, collections
p = sys.argv[1]
ent = b'GuestOut: Level has started: ending_boss_after_credit'
rx = re.compile(rb'^\[(\d+)\]\[(\d\d:\d\d:\d\d\.\d+)\] ([\w:]+)\(\)')
k = -1; draws = []; lines_k = []
entered = False
hist = collections.defaultdict(collections.Counter)
first_seen = {}
card = None; run = 0; hi = 0
other = collections.defaultdict(list)
with open(p, 'rb') as f:
    for i, l in enumerate(f):
        if not entered:
            if ent in l:
                entered = True; k = 0
            continue
        if l.startswith(b'FrameTrace: n='):
            k += 1
            m = re.search(rb' draws=(\d+)', l)
            d = int(m.group(1)) if m else -1
            if card is None:
                if d >= 300: hi += 1
                elif hi >= 90 and d < 100:
                    # variant: series >= 600 rows with draws < 100 checked later; record candidate
                    card = k
                else:
                    if d < 100: hi = 0 if hi < 90 else hi
            continue
        m = rx.match(l)
        if m:
            fn = m.group(3).decode()
            if card is None: w = 'A_before_card'
            elif k < card + 600: w = 'B_card..+600'
            else: w = 'C_after+600'
            hist[w][fn] += 1
            if fn not in first_seen: first_seen[fn] = (k, w)
        else:
            low = l.lower()
            if card is not None and (b'error' in low or b'not implemented' in low or b'unknown' in low or b'warning' in low or b'stub' in low or b'fail' in low):
                s = l[:200]
                if len(other[s]) < 3: other[s].append(k)
print('card_end_k', card, 'last_k', k)
allf = set()
for w in hist: allf |= set(hist[w])
nb = max(1, card or 1); 
for fn in sorted(allf, key=lambda x: -(hist['C_after+600'][x])):
    a = hist['A_before_card'][fn]; b = hist['B_card..+600'][fn]; c = hist['C_after+600'][fn]
    print('%-60s before %7d  card..+600 %7d  after %8d  first_k %s' % (fn, a, b, c, first_seen[fn]))
print('--- error-ish lines after card end (first 3 k each)')
for s, ks in list(other.items())[:80]:
    print(ks, s)
