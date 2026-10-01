# elf_probe5.py - S0 (HPP-294): GCN payloads in the flat ELF by the marker 0xBEEB03FF (shader.cpp GetBinaryInfo):
# ShaderBinaryInfo at code + (code[1] + 1) * 8 bytes; hash = hash1 << 32 | hash0 (ShaderComputeHash).  How many of
# the hashes are the hashes of the translation-cache sources of snap0?  Counts only; no game bytes are written.
import struct, os, collections
data = open('C:/kyty/eboot.elf', 'rb').read()
M = struct.pack('<I', 0xBEEB03FF)
names = [f for f in os.listdir('C:/kyty/s288/snap0/ShaderCache_PPSA21564') if f[:2] in ('vs', 'ps', 'cs')]
cache = collections.defaultdict(set)
for f in names:
    cache[f[:2]].add(f.split('_')[1])
allc = set().union(*cache.values())
c = collections.Counter(); hs = set(); sig = collections.Counter(); types = collections.Counter(); lens = []
i = data.find(M)
while i >= 0:
    if i % 4 == 0 and i + 8 <= len(data):
        n = struct.unpack_from('<I', data, i + 4)[0]
        bi = i + (n + 1) * 8
        if 0 < n < 0x40000 and bi + 28 <= len(data):
            s = data[bi:bi + 7]
            sig[s if all(32 <= b < 127 for b in s) else b'<bin>'] += 1
            bits, = struct.unpack_from('<I', data, bi + 8)
            h0, h1 = struct.unpack_from('<II', data, bi + 16)
            h = '%016x' % ((h1 << 32) | h0)
            c['with binary info'] += 1
            if h != '0' * 16:
                hs.add(h); types[(bits >> 2) & 15] += 1; lens.append(bits >> 8)
        else:
            c['n out of range'] += 1
    i = data.find(M, i + 1)
print(dict(c)); print('signatures', dict(sig))
print('unique nonzero hashes in ELF payloads', len(hs), 'by info.type', dict(sorted(types.items())))
print('snap0 cache: unique hashes', len(allc), {k: len(v) for k, v in cache.items()})
print('snap0 cache hashes found among ELF payload hashes: %d of %d' % (len(allc & hs), len(allc)),
      {k: '%d/%d' % (len(v & hs), len(v)) for k, v in cache.items()})
if lens:
    lens.sort(); print('info.length bytes min/med/max', lens[0], lens[len(lens) // 2], lens[-1])
