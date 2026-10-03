# FS4b (HPP-471, Red Team): class of EVERY residual run of fullcmp_fs4b.py (fullcmp prints only the first 20):
# A = own build of 3d0e46da, B = 31cbfee8; after the same mapping as fullcmp_fs4b.py (SDL string, worktree path, PE time).
# Classes: 'pe-time' (PE header time), 'debug-dir' (.rdata debug directory time / RSDS GUID / age), 'anon-ns' (a run inside
# a ?A0x<8 hex> anonymous-namespace hash of a decorated name), 'other' (anything else). Prints ALL OK if 'other' == 0.
import struct, re, collections
A = open('C:/kyty/f287/fs4/fs4b/build/install/kyty_emulator.exe', 'rb').read()
B = open('C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe', 'rb').read()
BS = bytes([92])
sa = b'SDL-KytyPS5-2026-09-15-6a2987a-1874-g3d0e46da'
sb = b'SDL-KytyPS5-2026-09-15-6a2987a-1873-g92d11340'
A2 = bytearray(A.replace(sa, sb).replace(b'fs4' + BS + b'fs4b', b'fs4' + BS + b'fs4a').replace(b'fs4/fs4b', b'fs4/fs4a'))
B2 = bytearray(B)
pe = struct.unpack_from('<I', A, 0x3c)[0]
for x in (A2, B2):
    x[pe + 8:pe + 12] = b'\0\0\0\0'
n = struct.unpack_from('<H', A, pe + 6)[0]
opt = struct.unpack_from('<H', A, pe + 20)[0]
o = pe + 24 + opt
secs = []
for _ in range(n):
    name = A[o:o + 8].rstrip(b'\0').decode()
    vs, va, rs, rp = struct.unpack_from('<IIII', A, o + 8)
    secs.append((name, rp, rp + rs))
    o += 40
# debug directory: data directory index 6 of the optional header (PE32+: data dirs start at opt header + 112)
dd_rva, dd_size = struct.unpack_from('<II', A, pe + 24 + 112 + 6 * 8)


def rva2off(rva):
    o2 = pe + 24 + opt
    for _ in range(n):
        vs, va, rs, rp = struct.unpack_from('<IIII', A, o2 + 8)
        if va <= rva < va + max(vs, rs):
            return rva - va + rp
        o2 += 40
    return None


dbg_ranges = []
dd_off = rva2off(dd_rva)
for k in range(dd_size // 28):
    e = dd_off + 28 * k
    dbg_ranges.append((e, e + 28))
    sz, rva_raw, ptr_raw = struct.unpack_from('<III', A, e + 16)
    dbg_ranges.append((ptr_raw, ptr_raw + sz))


def region(off):
    for nm, a, b in secs:
        if a <= off < b:
            return nm
    return 'header/other'


anon = re.compile(rb'\?A0x[0-9A-F]{8}')
runs = []
i = 0
while i < len(A2):
    if A2[i] != B2[i]:
        j = i
        while j < len(A2) and A2[j] != B2[j]:
            j += 1
        runs.append((i, j - i))
        i = j
    else:
        i += 1
cls = collections.Counter()
other = []
for s, l in runs:
    if any(a <= s < b for a, b in dbg_ranges):
        c = 'debug-dir'
    else:
        c = 'other'
        for m in anon.finditer(bytes(A2[max(0, s - 12):s + l + 12])):
            ms = max(0, s - 12) + m.start()
            if ms <= s and s + l <= ms + 12:
                c = 'anon-ns'
                break
    cls[(c, region(s))] += 1
    if c == 'other':
        other.append((s, l, region(s), bytes(A2[max(0, s - 24):s + l + 8]), bytes(B2[max(0, s - 24):s + l + 8])))
print('residual runs', len(runs))
for k, v in sorted(cls.items()):
    print('  class', k[0], 'region', k[1], 'runs', v)
for s, l, r, a, b in other[:20]:
    print('  OTHER off 0x%x len %d %s A %r B %r' % (s, l, r, a, b))
print('RESIDUAL', 'ALL OK' if not other else 'OTHER %d' % len(other))
