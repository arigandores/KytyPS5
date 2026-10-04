# S12b (HPP-495, Red Team): .text of S12 adb0c82f vs FS5 631ff987 OUTSIDE the pipelineCache module region.
# Before RVA LO: delta 0; after RVA HI: delta 368 (len B.text - len A.text). Each differing run is a displacement
# candidate if its length is <= 4; runs > 4 are listed (clustered by 4 KiB) with the nearest public symbol.
import re, struct, sys
import numpy as np

S = sys.argv[1]
LO, HI = 0x881000, 0x8d6000
A = open('C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe', 'rb').read()
B = open('C:/kyty/f287/bin/kyty_emulator_631ff987.exe', 'rb').read()


def text(d):
    pe = struct.unpack_from('<I', d, 0x3c)[0]
    n = struct.unpack_from('<H', d, pe + 6)[0]
    opt = struct.unpack_from('<H', d, pe + 20)[0]
    o = pe + 24 + opt
    for _ in range(n):
        name = d[o:o + 8].rstrip(b'\0').decode()
        vs, va, rs, rp = struct.unpack_from('<IIII', d, o + 8)
        if name == '.text':
            return va, np.frombuffer(d[rp:rp + min(vs, rs)], dtype=np.uint8)
        o += 40


va, ta = text(A)
_, tb = text(B)
D = len(tb) - len(ta)
pubs = []
txt = open(S + '/pub_s12.txt', encoding='utf-8', errors='replace').read()
for m in re.finditer(r"S_PUB32 \[size = \d+\] `([^`]*)`\s+flags = ([^,]*), addr = 0001:(\d+)", txt):
    pubs.append((int(m.group(3)), m.group(1)))
pubs.sort()
offs = np.array([p[0] for p in pubs])


def near(off):
    i = int(np.searchsorted(offs, off, side='right')) - 1
    return '%s +0x%x' % (pubs[i][1][:90], off - pubs[i][0]) if i >= 0 else '(none)'


def runs(a, b, base):
    ne = np.concatenate(([False], a != b, [False])).astype(np.int8)
    dd = np.diff(ne)
    st = np.nonzero(dd == 1)[0]
    en = np.nonzero(dd == -1)[0]
    return [(base + s, e - s) for s, e in zip(st, en)]


lo, hi = LO - va, HI - va
r0 = runs(ta[:lo], tb[:lo], 0)
r1 = runs(ta[hi:], tb[hi + D:hi + D + len(ta) - hi], hi)
for nm, rr in (('before LO (delta 0)', r0), ('after HI (delta %d)' % D, r1)):
    small = [x for x in rr if x[1] <= 4]
    big = [x for x in rr if x[1] > 4]
    print('%s: runs %d, <=4 bytes %d, >4 bytes %d, bytes in >4 runs %d' % (nm, len(rr), len(small), len(big), sum(l for _, l in big)))
    cl = {}
    for o, l in big:
        cl.setdefault(o // 4096, []).append((o, l))
    print('  4 KiB blocks with >4-byte runs: %d' % len(cl))
    for k in sorted(cl)[:30]:
        v = cl[k]
        print('   RVA 0x%x: %d runs, max %d, near %s' % (va + v[0][0], len(v), max(l for _, l in v), near(v[0][0])))
