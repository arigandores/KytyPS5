# S12b (HPP-495, Red Team): where does the .text of S12 adb0c82f differ from FS5 631ff987 beyond displacements?
# Window classification (256 bytes): aligned at delta 0 or at delta D = len(B.text) - len(A.text) if >= 70 % of bytes
# match; other windows are "changed". Changed windows are mapped to the nearest preceding public function symbol of
# the S12 PDB (llvm-pdbutil dump -publics; emulator C++ code has no S_*PROC32 records, publics are sparse after LTO).
import re, struct, sys
import numpy as np

S = sys.argv[1]
A_PATH = 'C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe'
B_PATH = 'C:/kyty/f287/bin/kyty_emulator_631ff987.exe'
A = open(A_PATH, 'rb').read()
B = open(B_PATH, 'rb').read()


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
vb, tb = text(B)
D = len(tb) - len(ta)
print('text VA A 0x%x B 0x%x len A %d B %d D %d' % (va, vb, len(ta), len(tb), D))
W = 256
n = (len(ta) // W) * W
eq0 = (ta[:n] == tb[:n]).reshape(-1, W).mean(axis=1)
eqd = (ta[:n] == tb[D:D + n]).reshape(-1, W).mean(axis=1)
cls = np.where(eq0 >= 0.7, 0, np.where(eqd >= 0.7, 1, 2))
# first window where delta-0 alignment stops, last where delta-D alignment starts
first_not0 = int(np.argmax(cls != 0))
last_notd = len(cls) - 1 - int(np.argmax(cls[::-1] != 1))
print('first window not aligned at 0: RVA 0x%x; last window not aligned at D: RVA 0x%x' % (va + first_not0 * W, va + last_notd * W))
print('windows: aligned0 %d alignedD %d changed %d' % ((cls == 0).sum(), (cls == 1).sum(), (cls == 2).sum()))
print('aligned0 windows after first_not0: %d; alignedD windows before first_not0: %d' % ((cls[first_not0:] == 0).sum(), (cls[:first_not0] == 1).sum()))
ch = np.nonzero(cls == 2)[0]
spans = []
for w in ch:
    if spans and w == spans[-1][1] + 1:
        spans[-1][1] = w
    else:
        spans.append([w, w])
print('changed spans: %d' % len(spans))

pubs = []
txt = open(S + '/pub_s12.txt', encoding='utf-8', errors='replace').read()
for m in re.finditer(r"S_PUB32 \[size = \d+\] `([^`]*)`\s+flags = ([^,]*), addr = 0001:(\d+)", txt):
    pubs.append((int(m.group(3)), m.group(1), m.group(2)))
pubs.sort()
offs = np.array([p[0] for p in pubs])


def near(off):
    i = int(np.searchsorted(offs, off, side='right')) - 1
    if i < 0:
        return '(none)'
    return '%s +0x%x' % (pubs[i][1][:110], off - pubs[i][0])


for s, e in spans[:40]:
    print('  changed RVA 0x%x..0x%x (%d B) start near %s' % (va + s * W, va + (e + 1) * W, (e - s + 1) * W, near(s * W)))
pc = [(o, nm) for o, nm, f in pubs if 'PipelineCache' in nm and 'function' in f]
if pc:
    lo, hi = min(o for o, _ in pc), max(o for o, _ in pc)
    print('PipelineCache public functions: %d, RVA 0x%x..0x%x' % (len(pc), va + lo, va + hi))
    inside = sum(1 for s, e in spans if lo - 0x40000 <= s * W <= hi + 0x40000)
    print('changed spans within +-256 KiB of that range: %d of %d' % (inside, len(spans)))
# delta profile in the transition region: best delta among 0..D per 4 KiB block between first_not0 and last_notd
lo_w, hi_w = first_not0, last_notd
blk = 4096
b0 = (lo_w * W) // blk * blk
b1 = min(((hi_w + 1) * W + blk - 1) // blk * blk, n)
print('delta profile (4 KiB blocks) RVA 0x%x..0x%x:' % (va + b0, va + b1))
for off in range(b0, b1, blk):
    a = ta[off:off + blk]
    best = max(range(0, D + 1, 1), key=lambda d: int((a == tb[off + d:off + d + len(a)]).sum()))
    frac = (a == tb[off + best:off + best + len(a)]).mean()
    print('  0x%x best delta %d match %.3f near %s' % (va + off, best, frac, near(off)))
