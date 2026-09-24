import re, sys
# Skeptic #2, finding F1: collect guest mappings logged as "out_addr = 0x.. / size = N" and report
# pairs of distinct (non-adjacent) mappings that fall into the same 4 MiB tracking region.
p = sys.argv[1]
R = 4 << 20
maps = []
pend = None
pat_a = re.compile(rb'\bout_addr\s*=\s*0x([0-9a-fA-F]+)')
pat_s = re.compile(rb'^\s*size\s*=\s*(0x[0-9a-fA-F]+|\d+)')
n_lines = 0
with open(p, 'rb') as f:
    for line in f:
        n_lines += 1
        m = pat_a.search(line)
        if m:
            pend = int(m.group(1), 16)
            continue
        if pend is not None:
            m = pat_s.search(line)
            if m:
                maps.append((pend, int(m.group(1), 0)))
                pend = None
print('lines', n_lines, 'maps', len(maps))
# merge like RangeSet (adjacent merge); ignore unmaps (upper bound on distinct ranges)
iv = sorted((a, a + s) for a, s in maps if a != 0 and s != 0 and a < (1 << 40))
merged = []
for a, b in iv:
    if merged and a <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], b)
    else:
        merged.append([a, b])
print('merged ranges', len(merged))
shared = 0
for i in range(1, len(merged)):
    pa, pb = merged[i - 1]
    a, b = merged[i]
    if (pb - 1) // R == a // R:
        shared += 1
        if shared <= 30:
            print('shared region 0x%x: prev [0x%x,0x%x) next [0x%x,0x%x) gap 0x%x' % (a // R * R, pa, pb, a, b, a - pb))
print('pairs sharing a region', shared)
for a, s in maps[:15]:
    print('map 0x%x +0x%x' % (a, s))
