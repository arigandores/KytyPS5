# elf_probe2.py - S0 (HPP-294): the code pointer of struct Shader is at header+16; counts only.
import json, struct, collections
data = open('C:/kyty/eboot.elf', 'rb').read()
inv = json.load(open('C:/kyty/s288/s0/elf_inventory.json'))['elf']['headers']
c = collections.Counter()
for h in inv:
    off, cs = h['file_offset'], h['code_size']
    delta = struct.unpack_from('<q', data, off + 16)[0]
    if delta == 0:
        c['code ptr 0'] += 1; continue
    tgt = off + 16 + delta
    if tgt < 0 or tgt + cs > len(data):
        c['code ptr out of file'] += 1; continue
    c['code ptr in file'] += 1
    blob = data[tgt:tgt + cs + 512]
    c['OrbShdr within code_size+512'] += (b'OrbShdr' in blob)
    c['s_endpgm aligned within code_size'] += any(data[tgt + i:tgt + i + 4] == b'\x00\x00\x81\xbf' for i in range(0, cs, 4))
    c['all-zero payload'] += (data[tgt:tgt + cs].count(0) == cs)
print(len(inv), dict(c))
print('OrbShdr occurrences in the whole ELF:', data.count(b'OrbShdr'))
