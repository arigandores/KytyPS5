# elf_probe3.py - S0 (HPP-294): is the GCN payload right after the AGC header (header + header_size) with the marker
# 0xBEEB03FF (shader.cpp GetBinaryInfo) and a nonzero ShaderBinaryInfo hash?  Counts and hash-set sizes only.
import json, struct, collections, os
data = open('C:/kyty/eboot.elf', 'rb').read()
inv = json.load(open('C:/kyty/s288/s0/elf_inventory.json'))['elf']['headers']
c = collections.Counter(); hashes = collections.defaultdict(set); sizes = []
MARK = struct.pack('<I', 0xBEEB03FF)
for h in inv:
    off, hs, cs, ty = h['file_offset'], h['header_size'], h['code_size'], h['type']
    tgt = off + hs
    if tgt + cs > len(data):
        c['out of file'] += 1; continue
    if data[tgt:tgt + 4] == MARK:
        c['marker at header+header_size'] += 1
        n = struct.unpack_from('<I', data, tgt + 4)[0]
        bi = tgt + (n + 1) * 8
        if bi + 28 <= tgt + cs + 64:
            sig = data[bi:bi + 7]
            c['OrbShdr at binary info'] += (sig == b'OrbShdr')
        end = any(data[tgt + i:tgt + i + 4] == b'\x00\x00\x81\xbf' for i in range(0, cs, 4))
        c['s_endpgm inside code_size'] += end
        import hashlib
        hashes[ty].add(hashlib.sha256(data[tgt:tgt + cs]).hexdigest())
        sizes.append(cs)
    else:
        c['no marker'] += 1
        # search the marker in the 256 bytes after the header start
        j = data.find(MARK, off, off + hs + 256)
        c['marker within header+256'] += (j >= 0)
print(len(inv), dict(c))
print('unique payloads by binary type', {k: len(v) for k, v in sorted(hashes.items())}, 'total', sum(len(v) for v in hashes.values()))
if sizes:
    sizes.sort(); print('code_size bytes min/med/max/sum', sizes[0], sizes[len(sizes) // 2], sizes[-1], sum(sizes))
# cross-check with the translation cache file names of snap0: <stage>_<hash16>_<key16>.bin
names = [f for f in os.listdir('C:/kyty/s288/snap0/ShaderCache_PPSA21564') if f[:2] in ('vs', 'ps', 'cs')]
print('snap0 cache sources', len(names), 'unique hashes', len(set(f.split('_')[1] for f in names)))
