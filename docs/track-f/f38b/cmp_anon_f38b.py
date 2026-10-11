"""F38b (HPP-764): copy of F33d cmp_anon.py with the paths f33c/f33d -> f38a/f38b; the version strings are equal
(both builds configured on 531d6488). Masks anonymous-namespace tokens (clang-cl hashes the source path), the PE timestamp
and the debug directory data, then counts the remaining differing bytes. Also prints, for any pair, section sizes and the
summed length of the anonymous tokens. usage: cmp_anon_f38b.py <f38a exe> <f38b exe>"""
import re
import struct
import sys

BS = bytes([92])
a = bytearray(open(sys.argv[1], 'rb').read())
b = open(sys.argv[2], 'rb').read()
print('size', len(a), len(b))
npath = b.count(b'f287' + BS + b'f38b' + BS) + b.count(b'f287/f38b/')
print('path occurrences f38b', npath, 'f38a in a', a.count(b'f287' + BS + b'f38a' + BS) + a.count(b'f287/f38a/'))
b = bytearray(b.replace(b'f287' + BS + b'f38b' + BS, b'f287' + BS + b'f38a' + BS).replace(b'f287/f38b/', b'f287/f38a/'))


def sections(x):
    pe = struct.unpack_from('<I', x, 0x3c)[0]
    opt = pe + 24
    nsec = struct.unpack_from('<H', x, pe + 6)[0]
    so = opt + struct.unpack_from('<H', x, pe + 20)[0]
    out = []
    for k in range(nsec):
        name = bytes(x[so + 40 * k:so + 40 * k + 8]).rstrip(bytes(1)).decode()
        vs, va, rs, ra = struct.unpack_from('<IIII', x, so + 40 * k + 8)
        out.append((name, vs, rs))
    return out


def anon_len(x):
    return sum(len(m.group(0)) for m in re.finditer(rb'\?A0x[0-9A-F]+@', bytes(x)))


print('sections a', sections(a))
print('sections b', sections(b))
print('anon token bytes a', anon_len(a), 'b', anon_len(b))
if len(a) != len(b):
    print('SIZE DIFFERS - byte compare not applicable')
    sys.exit(0)


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
nsec = struct.unpack_from('<H', a, pe + 6)[0]
so = opt + struct.unpack_from('<H', a, pe + 20)[0]
for k in range(nsec):
    vs, va, rs, ra = struct.unpack_from('<IIII', a, so + 40 * k + 8)
    if va <= dbg_rva < va + max(vs, rs):
        off = dbg_rva - va + ra
typ, sz, rva, ptr = struct.unpack_from('<IIII', a, off + 12)
print('debug entry type', typ, 'size', sz, 'ptr', hex(ptr))
for x in (a, b):
    x[off:off + 28] = bytes(28)
    x[ptr:ptr + sz] = bytes(sz)
d = [i for i in range(len(a)) if a[i] != b[i]]
print('remaining diff bytes', len(d))
for i in d[:20]:
    print(' ', hex(i), bytes(a[max(0, i - 32):i + 16]), bytes(b[max(0, i - 32):i + 16]))
print('ALL OK' if not d else 'NOT OK')
