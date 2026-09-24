import re, sys
# F1 skeptic: all logged guest GPU mappings (direct/flexible 'out_addr/size' blocks and
# MemoryPoolCommit 'addr/len/type/prot' blocks); merge like RangeSet.Add and count 4 MiB
# tracking regions touched by two or more disjoint merged ranges.
p = sys.argv[1]
ra = re.compile(rb'^\s*out_addr\s*=\s*0x([0-9a-fA-F]+)')
rs = re.compile(rb'^\s*size\s*=\s*(0x[0-9a-fA-F]+|\d+)')
rg = re.compile(rb'^\s*gpu_mode\s*=\s*(\w+)')
pa = re.compile(rb'^\s*addr  = 0x([0-9a-fA-F]+)')
pl = re.compile(rb'^\s*len   = 0x([0-9a-fA-F]+)')
pt = re.compile(rb'^\s*type  = 0x')
pp = re.compile(rb'^\s*prot  = 0x([0-9a-fA-F]+)')
maps = []
pools = []
st = None
pst = None
with open(p, 'rb') as f:
    for i, line in enumerate(f):
        m = ra.match(line)
        if m:
            st = [int(m.group(1), 16), None, i]
            continue
        if st is not None:
            m = rs.match(line)
            if m and st[1] is None:
                v = m.group(1)
                st[1] = int(v, 16) if v.startswith(b'0x') else int(v)
                continue
            m = rg.match(line)
            if m:
                if st[1] is not None and m.group(1) != b'NoAccess':
                    maps.append((st[0], st[1], st[2]))
                st = None
                continue
        m = pa.match(line)
        if m:
            pst = [int(m.group(1), 16), None, None, i]
            continue
        if pst is not None:
            m = pl.match(line)
            if m:
                pst[1] = int(m.group(1), 16)
                continue
            if pt.match(line):
                continue
            m = pp.match(line)
            if m and pst[1] is not None:
                pst[2] = int(m.group(1), 16)
                pools.append(tuple(pst))
                pst = None
                continue
            pst = None
print('direct/flex maps (gpu access)', len(maps))
for a, s, i in maps:
    print('  map', hex(a), hex(s), 'line', i)
print('pool commits', len(pools))
gpu_pools = [x for x in pools if x[2] & 0x30]
print('pool commits with GPU prot', len(gpu_pools))
iv = sorted([(a, a + s) for a, s, i in maps] + [(a, a + l) for a, l, pr, i in gpu_pools])
merged = []
for a, b in iv:
    if merged and a <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], b)
    else:
        merged.append([a, b])
print('merged ranges (logged only, unmaps ignored)', len(merged))
R = 4 << 20
owners = {}
for k, (a, b) in enumerate(merged):
    for r in range(a // R, (b - 1) // R + 1):
        owners.setdefault(r, []).append(k)
shared = {r: ks for r, ks in owners.items() if len(ks) > 1}
print('regions shared by >=2 merged ranges', len(shared))
for r, ks in sorted(shared.items())[:40]:
    print(' ', hex(r * R), [(hex(merged[k][0]), hex(merged[k][1] - merged[k][0])) for k in ks])
for a, b in merged[:60]:
    print(' range', hex(a), hex(b - a))
