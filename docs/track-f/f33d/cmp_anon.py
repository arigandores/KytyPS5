"""F33d (HPP-745): after cmp_norm.py - masks, in both binaries, every anonymous-namespace token of an RTTI/type name
('?A0x' up to the terminating NUL of that name; clang-cl derives the hash from the source file path) and the PE
timestamp / debug directory data, then counts the remaining differing bytes. usage: cmp_anon.py <f33c exe> <f33d exe>"""
import re
import struct
import sys

BS = bytes([92])
a = bytearray(open(sys.argv[1], 'rb').read())
b = open(sys.argv[2], 'rb').read()
pad = bytes(12) + b'q'
b = b.replace(b'f287' + BS + b'f33d' + BS, b'f287' + BS + b'f33c' + BS).replace(b'f287/f33d/', b'f287/f33c/')
b = bytearray(b.replace(b'KytyPS5-2026-09-15-6a2987a-1912-g0c57cfed' + pad,
                        b'KytyPS5-2026-09-15-6a2987a-1910-gee9632be' + pad))


def mask_anon(x):
    n = 0
    for m in re.finditer(rb'\?A0x[0-9A-F]+@', bytes(x)):
        s = m.start()
        e = bytes(x).find(bytes(1), s)
        x[s:e] = bytes(e - s)
        n += 1
    return n


print('anon tokens', mask_anon(a), mask_anon(b))
pe = struct.unpack_from('<I', a, 0x3c)[0]
opt = pe + 24
for x in (a, b):
    x[pe + 8:pe + 12] = bytes(4)
dbg_rva, dbg_sz = struct.unpack_from('<II', a, opt + 112 + 6 * 8)
# debug directory entry and its data (CodeView GUID/age) - located by cmp_norm.py at 0x14d189c, size 28
nsec = struct.unpack_from('<H', a, pe + 6)[0]
so = opt + struct.unpack_from('<H', a, pe + 20)[0]
for k in range(nsec):
    vs, va, rs, ra = struct.unpack_from('<IIII', a, so + 40 * k + 8)
    if va <= dbg_rva < va + max(vs, rs):
        off = dbg_rva - va + ra
typ, sz, rva, ptr = struct.unpack_from('<IIII', a, off + 12)  # read once, before masking a
print('debug entry type', typ, 'size', sz, 'ptr', hex(ptr))
for x in (a, b):
    x[off:off + 28] = bytes(28)
    x[ptr:ptr + sz] = bytes(sz)
d = [i for i in range(len(a)) if a[i] != b[i]]
print('remaining diff bytes', len(d))
for i in d[:20]:
    print(' ', hex(i), bytes(a[max(0, i - 32):i + 16]), bytes(b[max(0, i - 32):i + 16]))
print('ALL OK' if not d else 'NOT OK')
