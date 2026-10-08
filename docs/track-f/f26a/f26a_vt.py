# F26a (HPP-688): reconstruct pointer tables (vtables) from R_X86_64_RELATIVE relocations: slot -> addend, for slots in [lo, hi)
# usage: f26a_vt.py <eboot.elf> <lo-hex> <hi-hex>
import sys, struct
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
elf = Elf(sys.argv[1]); e = elf.data
lo = int(sys.argv[2], 16); hi = int(sys.argv[3], 16)
phoff = struct.unpack('<Q', e[32:40])[0]; phnum = struct.unpack('<H', e[56:58])[0]
tags = {}
for i in range(phnum):
    t, fl, off, va, pa, fs, ms, al = struct.unpack('<IIQQQQQQ', e[phoff + 56 * i: phoff + 56 * i + 56])
    if t == 2:
        for j in range(0, fs, 16):
            tg, v = struct.unpack('<QQ', e[off + j: off + j + 16])
            if tg == 0: break
            tags.setdefault(tg, v)
RELA, RELASZ = tags[0x7], tags[0x8]
res = {}
for k in range(RELASZ // 24):
    r_off, r_info, r_add = struct.unpack('<QQq', elf.read(RELA + 24 * k, 24))
    if lo <= r_off < hi:
        res[r_off] = (r_info & 0xffffffff, r_add)
for s in sorted(res):
    t, a = res[s]
    print('0x%x  type %d  -> 0x%x' % (s, t, a))
