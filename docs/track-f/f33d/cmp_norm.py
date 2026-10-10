"""F33d (HPP-745): byte comparison of the F33d clean-worktree build against the F33c copy 2b393af8.
Normalises the worktree path (f33d -> f33c) and the configure-time SDL_REVISION string, then classifies the rest by
PE section. usage: cmp_norm.py <f33c exe> <f33d exe>"""
import struct
import sys
from collections import Counter

BS = bytes([92])
a = open(sys.argv[1], 'rb').read()
b = open(sys.argv[2], 'rb').read()
print('size', len(a), len(b))
d0 = sum(1 for i in range(min(len(a), len(b))) if a[i] != b[i])
print('raw diff bytes', d0)
p1 = b'f287' + BS + b'f33d' + BS
p2 = b'f287/f33d/'
print('path occurrences f33d', b.count(p1) + b.count(p2))
pad = bytes(12) + b'q'
b2 = b.replace(p1, b'f287' + BS + b'f33c' + BS).replace(p2, b'f287/f33c/')
b2 = b2.replace(b'KytyPS5-2026-09-15-6a2987a-1912-g0c57cfed' + pad, b'KytyPS5-2026-09-15-6a2987a-1910-gee9632be' + pad)
d = [i for i in range(len(a)) if a[i] != b2[i]]
print('diff bytes after path + SDL_REVISION normalisation', len(d))
pe = struct.unpack_from('<I', a, 0x3c)[0]
nsec = struct.unpack_from('<H', a, pe + 6)[0]
optsz = struct.unpack_from('<H', a, pe + 20)[0]
opt = pe + 24
so = opt + optsz
secs = []
for k in range(nsec):
    name = a[so + 40 * k:so + 40 * k + 8].rstrip(bytes(1)).decode()
    vs, va, rs, ra = struct.unpack_from('<IIII', a, so + 40 * k + 8)
    secs.append((name, va, vs, ra, rs))


def rva2off(r):
    for n, va, vs, ra, rs in secs:
        if va <= r < va + max(vs, rs):
            return r - va + ra
    return None


def where(o):
    if o < so + 40 * nsec:
        return 'hdr'
    for n, va, vs, ra, rs in secs:
        if ra <= o < ra + rs:
            return n
    return '?'


dbg_rva, dbg_sz = struct.unpack_from('<II', a, opt + 112 + 6 * 8)
dbg_off = rva2off(dbg_rva)
print('PE timestamp offset', hex(pe + 8), 'debug dir off', hex(dbg_off) if dbg_off else None, 'size', dbg_sz)
spans = []
if dbg_off:
    for k in range(dbg_sz // 28):
        e = dbg_off + 28 * k
        typ, sz, rva, ptr = struct.unpack_from('<IIII', a, e + 12)
        spans.append(('dbgentry%d' % k, e, e + 28))
        spans.append(('dbgdata%d_type%d' % (k, typ), ptr, ptr + sz))
spans.append(('pe_timestamp', pe + 8, pe + 12))
spans.append(('pe_checksum', opt + 64, opt + 68))


def cls(i):
    for n, s, e in spans:
        if s <= i < e:
            return n
    return 'other:' + where(i)


c = Counter(cls(i) for i in d)
for k, v in sorted(c.items()):
    print(' ', k, v)
other = [i for i in d if cls(i).startswith('other')]
print('unexplained diff bytes', len(other))
for i in other[:20]:
    print('  ', hex(i), where(i), a[max(0, i - 32):i + 16], b2[max(0, i - 32):i + 16])
