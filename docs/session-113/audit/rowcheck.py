import re, sys
path = sys.argv[1]
start = mid = 0
ns = []
glued = []
with open(path, 'rb') as f:
    for line in f:
        c = line.count(b'FrameTrace-x: n=')
        if not c:
            continue
        if line.startswith(b'FrameTrace-x: n='):
            start += 1
            ns.append(int(re.match(rb'FrameTrace-x: n=(\d+)', line).group(1)))
            c -= 1
        if c:
            mid += c
            if len(glued) < 3:
                i = line.find(b'FrameTrace-x: n=')
                glued.append(line[max(0, i - 120):i + 40])
gaps = [(a, b) for a, b in zip(ns, ns[1:]) if b != a + 1]
print(path, 'at start', start, 'mid-line', mid, 'n range', ns[0], ns[-1], 'gaps', len(gaps), gaps[:5])
print(glued)
