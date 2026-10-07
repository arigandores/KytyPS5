# FS8b (HPP-566, Red Team): copy of pediff3.py of F15d as used in FS6b, run as is (only this line added).
# F15d (HPP-515): classify every differing byte of two equal-size PE files:
#  (1) build dir name (argv[3] in A at the byte where B has argv[4]) - __FILE__ strings, PDB path;
#  (2) clang-cl anonymous-namespace tag ?A0x<8 hex> (a hash of the source path) - RTTI/type names;
#  (3) COFF TimeDateStamp, debug-directory TimeDateStamps, RSDS GUID/age (header / debug data);
#  everything else - OTHER, listed with section and context.
import re, struct, sys, collections
a = open(sys.argv[1], 'rb').read(); b = open(sys.argv[2], 'rb').read()
ta, tb = sys.argv[3].encode(), sys.argv[4].encode()
assert len(a) == len(b)
pe = struct.unpack_from('<I', a, 0x3c)[0]; nsec = struct.unpack_from('<H', a, pe + 6)[0]
optsz = struct.unpack_from('<H', a, pe + 20)[0]; opt = pe + 24
secs = []
for i in range(nsec):
    o = opt + optsz + 40 * i
    secs.append((a[o:o + 8].rstrip(b'\0').decode(),) + struct.unpack_from('<IIII', a, o + 8))
def sec_of(off):
    for n, vsz, va, rsz, rp in secs:
        if rp <= off < rp + rsz:
            return n
    return 'header'
masked = set()
for m in re.finditer(rb'\?A0x[0-9A-F]{8}', a):
    if re.fullmatch(rb'\?A0x[0-9A-F]{8}', b[m.start():m.end()]):
        masked.update(range(m.start(), m.end()))
hdr = set(range(pe + 8, pe + 12))
dd = opt + (112 if struct.unpack_from('<H', a, opt)[0] == 0x20b else 96)
dbg_rva, dbg_sz = struct.unpack_from('<II', a, dd + 48)
for n, vsz, va, rsz, rp in secs:
    if va <= dbg_rva < va + vsz:
        dbg_off = rp + dbg_rva - va
for k in range(dbg_sz // 28):
    e = dbg_off + 28 * k
    hdr.update(range(e + 4, e + 8))
    typ, sz, rva, ptr = struct.unpack_from('<IIII', a, e + 12)
    if a[ptr:ptr + 4] == b'RSDS':
        hdr.update(range(ptr + 4, ptr + 24))
    elif typ != 2:
        hdr.update(range(ptr, ptr + sz))  # repro / other debug payloads carry the same hash/stamp
cls = collections.Counter(); other = []
for i in range(len(a)):
    if a[i] == b[i]:
        continue
    if i in hdr:
        cls['(3) header/debug stamp+GUID'] += 1; continue
    if i in masked:
        cls['(2) anon-namespace tag'] += 1; continue
    if any(a[i - k:i - k + len(ta)] == ta and b[i - k:i - k + len(tb)] == tb for k in range(len(ta))):
        cls['(1) build dir name'] += 1; continue
    other.append(i)
secd = collections.Counter(sec_of(i) for i in other)
print('differing bytes', sum(cls.values()) + len(other), dict(cls), 'OTHER', len(other), dict(secd))
for i in other[:30]:
    print('0x%08x %s a=%02x b=%02x ctx_a=%r' % (i, sec_of(i), a[i], b[i], a[max(0, i - 24):i + 8]))
print('VERDICT', 'EXPLAINED' if not other else 'UNEXPLAINED')
