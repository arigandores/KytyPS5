import re, sys
# F1 skeptic: reconstruct logged guest GPU mappings (out_addr/size blocks) and count 4 MiB
# tracking regions shared by two disjoint mapped ranges (after RangeSet-style merging).
p = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 4000000
ra = re.compile(rb'out_addr\s*=\s*0x([0-9a-fA-F]+)')
rs = re.compile(rb'^\s*size\s*=\s*(\d+)')
rg = re.compile(rb'gpu_mode\s*=\s*(\w+)')
maps = []
pend = None
with open(p, 'rb') as f:
    for i, line in enumerate(f):
        if i > limit:
            break
        m = ra.search(line)
        if m:
            pend = [int(m.group(1), 16), None, None]
            continue
        if pend is not None and pend[1] is None:
            m = rs.search(line)
            if m:
                pend[1] = int(m.group(1))
                continue
        if pend is not None and pend[1] is not None:
            m = rg.search(line)
            if m:
                pend[2] = m.group(1).decode()
                maps.append(tuple(pend))
                pend = None
print('logged maps', len(maps))
from collections import Counter
print(Counter(m[2] for m in maps))
# merge (adjacent merge like RangeSet.Add: it->first <= last)
iv = sorted((a, a + s) for a, s, g in maps if s and a < (1 << 40))
merged = []
for a, b in iv:
    if merged and a <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], b)
    else:
        merged.append([a, b])
print('merged ranges', len(merged))
R = 4 << 20
owners = {}
for k, (a, b) in enumerate(merged):
    for r in range(a // R, (b - 1) // R + 1):
        owners.setdefault(r, []).append(k)
shared = {r: ks for r, ks in owners.items() if len(ks) > 1}
print('regions shared by >=2 merged ranges', len(shared))
for r, ks in sorted(shared.items())[:40]:
    print(hex(r * R), [(hex(merged[k][0]), hex(merged[k][1] - merged[k][0])) for k in ks])
