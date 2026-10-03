# FS4b (HPP-471, Red Team): port of my FS3b fullcmp_fs3b.py to FS4 (B = 31cbfee8, paths fs4/fs4b -> fs4/fs4a). Was:
# FS3b (HPP-448, Red Team): every differing byte run of the whole file A (own build) vs B (540c035a), each run named by
# the PE region it falls into; after mapping the SDL revision string of A onto that of B and zeroing the PE timestamp,
# the files must be equal byte for byte (prints ALL OK) - that is: the only differences are the timestamp and that string.
import struct, hashlib
A = open('C:/kyty/f287/fs4/fs4b/build/install/kyty_emulator.exe', 'rb').read()
B = open('C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe', 'rb').read()
pe = struct.unpack_from('<I', A, 0x3c)[0]
n = struct.unpack_from('<H', A, pe + 6)[0]
opt = struct.unpack_from('<H', A, pe + 20)[0]
o = pe + 24 + opt
secs = []
for _ in range(n):
    name = A[o:o + 8].rstrip(b'\0').decode()
    vs, va, rs, rp = struct.unpack_from('<IIII', A, o + 8)
    secs.append((name, rp, rp + rs))
    o += 40


def where(off):
    if off == pe + 8:
        return 'PE TimeDateStamp'
    for nm, a, b in secs:
        if a <= off < b:
            return nm
    return 'header/other'


runs = []
i = 0
while i < len(A):
    if A[i] != B[i]:
        j = i
        while j < len(A) and A[j] != B[j]:
            j += 1
        runs.append((i, j - i))
        i = j
    else:
        i += 1
print('sizes', len(A), len(B), 'differing runs', len(runs))
for s, l in runs[:20]:
    print('  run off 0x%x len %d region %s A %r B %r' % (s, l, where(s), A[max(0, s - 24):s + l + 8], B[max(0, s - 24):s + l + 8]))
sa = b'SDL-KytyPS5-2026-09-15-6a2987a-1874-g3d0e46da'
sb = b'SDL-KytyPS5-2026-09-15-6a2987a-1873-g92d11340'
print('SDL string count A', A.count(sa), 'B', B.count(sb))
BS = bytes([92])
# worktree path of the build tree (same length): fs3b -> fs3a (the first run forgot this mapping and printed FAILED)
A2 = bytearray(A.replace(sa, sb).replace(b'fs4' + BS + b'fs4b', b'fs4' + BS + b'fs4a').replace(b'fs4/fs4b', b'fs4/fs4a'))
B2 = bytearray(B)
for x in (A2, B2):
    x[pe + 8:pe + 12] = b'\0\0\0\0'
res = []
i = 0
while i < len(A2):
    if A2[i] != B2[i]:
        j = i
        while j < len(A2) and A2[j] != B2[j]:
            j += 1
        res.append((i, j - i))
        i = j
    else:
        i += 1
print('residual runs after mapping', len(res))
for s, l in res[:20]:
    print('  residual off 0x%x len %d region %s A %r B %r' % (s, l, where(s), bytes(A2[max(0, s - 32):s + l + 16]), bytes(B2[max(0, s - 32):s + l + 16])))
eq = bytes(A2) == bytes(B2)
print('equal after SDL string mapping and timestamp zeroing:', eq, hashlib.sha256(bytes(A2)).hexdigest()[:16], hashlib.sha256(bytes(B2)).hexdigest()[:16])
print('FULLCMP', 'ALL OK' if eq and A.count(sa) == 1 and B.count(sb) == 1 else 'FAILED')
