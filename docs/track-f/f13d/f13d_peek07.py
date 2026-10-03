# F13d: show context lines around first occurrences of given markers after level entry (binary, streaming).
import sys, collections
p = sys.argv[1]; marks = [m.encode() for m in sys.argv[2].split('|')]; nshow = int(sys.argv[3]); skip = int(sys.argv[4]) if len(sys.argv) > 4 else 0
ent = b'Level has started: non_interactive_credit'
prev = collections.deque(maxlen=6)
entered = False; k = -1; shown = collections.Counter(); seen = collections.Counter()
with open(p, 'rb') as f:
    for l in f:
        if not entered:
            if ent in l: entered = True; k = 0
            continue
        if l.startswith(b'FrameTrace: n='): k += 1
        for m in marks:
            if m in l:
                seen[m] += 1
                if seen[m] > skip and shown[m] < nshow:
                    shown[m] += 1
                    print('==== k', k, 'mark', m.decode())
                    for q in prev: print('  -', q[:220])
                    print('  >', l[:220])
        prev.append(l)
for m in marks: print('count', m.decode(), seen[m])
