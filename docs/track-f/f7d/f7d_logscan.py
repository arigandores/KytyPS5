"""f7d_logscan.py - F7d (HPP-443, Red Team): count draw/dispatch skip, BVH and stub lines in the logs named by ROADMAP p.366(b)(6).

Patterns are the literal format prefixes of the emulator (renderDraw.cpp:2823, :4050, :4449; renderCompute.cpp:525, :986)
plus BVH / unimplemented markers. Streaming read in binary mode; prints count, first 3 examples (cut to 200 bytes) per pattern.
"""
import sys, hashlib

PATS = [b'Skipping draw with unknown primitive type', b'BindFloor: skipped draw', b'AsyncPipelines: skipped draw',
        b'skipping CS', b'BindFloor: skipped dispatch', b'RtSkip: refused', b'BvhLoopCapTrip', b'Bvh', b'BVH',
        b'ASSERT', b'not implemented', b'NOT IMPLEMENTED', b'Not implemented', b'unsupported', b'Unsupported',
        b'stub', b'STUB', b'Level has started', b'[Vulkan][E]', b'TRAP', b'unknown']


def scan(path):
    cnt = {p: 0 for p in PATS}
    ex = {p: [] for p in PATS}
    h = hashlib.sha256()
    n = 0
    with open(path, 'rb') as f:
        for line in f:
            h.update(line)
            n += 1
            for p in PATS:
                if p in line:
                    cnt[p] += 1
                    if len(ex[p]) < 3:
                        ex[p].append(line[:200].rstrip())
    print('== %s lines %d sha256 %s' % (path, n, h.hexdigest()[:16]))
    for p in PATS:
        print('  %-48s %d' % (p.decode(), cnt[p]))
        for e in ex[p]:
            print('      ' + e.decode('utf-8', 'replace'))


for a in sys.argv[1:]:
    scan(a)
print('ALL OK')
