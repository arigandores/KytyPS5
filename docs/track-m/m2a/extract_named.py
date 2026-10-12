"""M2a (HPP-838, ROADMAP s122 item 756(v)(1)(ii)): extract the GCN code of the named programs of the game - the AMDGPU
ELF of eboot.bin / sce_module whose .text XXH3-64 = the program hash (method of docs/track-f/f11a/t1scan_f11a.py) - into
<out>/<hash>.bin with sha256. Usage: python extract_named.py <out dir> <hash16> [...]. Lock and STOP checked."""
import hashlib
import mmap
import os
import struct
import sys

import xxhash

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
GAME = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/'
MAGIC = bytes([0x7F, 0x45, 0x4C, 0x46, 2, 1, 1])


def elf_programs(path):
    f = open(path, 'rb')
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    e = mm.find(MAGIC)
    while e != -1:
        if struct.unpack_from('<H', mm, e + 18)[0] == 0xE0:
            secs = []
            try:
                shoff = struct.unpack_from('<Q', mm, e + 0x28)[0]
                shentsize, shnum, shstrndx = struct.unpack_from('<HHH', mm, e + 0x3A)
                for k in range(shnum):
                    b = e + shoff + k * shentsize
                    name, typ, flags, addr, off, size = struct.unpack_from('<IIQQQQ', mm, b)
                    secs.append((name, typ, off, size))
            except struct.error:
                secs = []
            if secs and shstrndx < len(secs):
                stroff = e + secs[shstrndx][2]
                for name, typ, off, size in secs:
                    end = mm.find(bytes([0]), stroff + name)
                    nm = mm[stroff + name:end].decode('latin1')
                    if nm in ('.text', '.shader_text'):
                        code = bytes(mm[e + off:e + off + size])
                        yield os.path.basename(path), e, code
        e = mm.find(MAGIC, e + 1)


def main():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        return 3
    out = sys.argv[1]
    want = {int(h, 16): h for h in sys.argv[2:]}
    os.makedirs(out, exist_ok=True)
    files = [GAME + 'eboot.bin']
    mod = GAME + 'sce_module/'
    if os.path.isdir(mod):
        files += [mod + x for x in sorted(os.listdir(mod)) if x.lower().endswith(('.prx', '.sprx', '.elf'))]
    found = {}
    for fp in files:
        for src, elf, code in elf_programs(fp):
            h = xxhash.xxh3_64_intdigest(code)
            if h in want and want[h] not in found:
                p = '%s/%s.bin' % (out, want[h])
                open(p, 'wb').write(code)
                found[want[h]] = (src, elf, len(code), hashlib.sha256(code).hexdigest())
    for h in sys.argv[2:]:
        if h in found:
            src, elf, n, s = found[h]
            print('%s %s elf@0x%x bytes %d sha256 %s' % (h, src, elf, n, s))
        else:
            print('%s NOT FOUND' % h)
    return 0 if len(found) == len(want) else 1


if __name__ == '__main__':
    sys.exit(main())
