# F4a2 (HPP-346): extract the Fragment SPIR-V module of PS 5514e10f1a60df83 from the copy of its translation cache file.
# The module length is taken from the size prefix in front of the magic (checked against an instruction walk).
import struct, sys, hashlib
src, dst = sys.argv[1], sys.argv[2]
b = open(src, 'rb').read()
print('file', src, 'size', len(b), 'sha256', hashlib.sha256(b).hexdigest())
MAGIC = 0x07230203
offs = [i for i in range(0, len(b) - 4) if struct.unpack_from('<I', b, i)[0] == MAGIC]
print('magic at', offs)
assert len(offs) == 1, 'expected one module'
o = offs[0]
for k in (4, 8, 12, 16):
    print('prefix word at -%d:' % k, struct.unpack_from('<I', b, o - k)[0], struct.unpack_from('<Q', b, o - k)[0] if k >= 8 else '')
# instruction walk: stop at the first word that does not form a valid instruction
i = o + 20
while i + 4 <= len(b):
    w = struct.unpack_from('<I', b, i)[0]
    wc = w >> 16
    if wc == 0 or i + 4 * wc > len(b):
        break
    i += 4 * wc
walk_words = (i - o) // 4
print('walk words', walk_words)
cand = [struct.unpack_from('<I', b, o - 4)[0], struct.unpack_from('<Q', b, o - 8)[0]]
n = None
for c in cand:
    if c == walk_words:
        n = c
        print('size prefix (words) =', c)
    elif c == walk_words * 4:
        n = c // 4
        print('size prefix (bytes) =', c)
if n is None:
    print('no size prefix matches the walk; using the walk')
    n = walk_words
spv = b[o:o + 4 * n]
open(dst, 'wb').write(spv)
print('wrote', dst, 'words', n, 'sha256', hashlib.sha256(spv).hexdigest())
