# F9a step 1: one streaming pass over the user play log; ASCII output.
import sys, json
p = 'C:/kyty/play/20261002T221534Z/log.txt'
keys = [b'AsyncPipelines: skipped draw', b'BvhLoopCapTrip:', b'CsStall', b'PriorityStall', b'[Vulkan]', b'opcode is not implemented']
flips = []; ft = []; hits = {k.decode(): [] for k in keys}; lvl = []
with open(p, 'rb') as f:
    n = 0
    for line in f:
        n += 1
        if line.startswith(b'\t flipPendingNum'):
            flips.append(n)
        elif line.startswith(b'FrameTrace: '):
            ft.append(n)
        elif b'Level has started' in line:
            lvl.append((n, line[:160].decode('ascii', 'replace').strip()))
        for k in keys:
            if k in line:
                hits[k.decode()].append((n, line[:200].decode('ascii', 'replace').strip()))
json.dump({'lines': n, 'flips': flips, 'frametrace': ft, 'hits': hits, 'lvl': lvl}, open('C:/kyty/f287/f9/scan_log.json', 'w'))
print('lines', n, 'flipPendingNum', len(flips), 'FrameTrace', len(ft), 'level', lvl)
for k, v in hits.items():
    print(k, len(v), v[:3])
