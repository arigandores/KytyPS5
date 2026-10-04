"""F23a (HPP-578, item 483(e)(1)): are there shader programs in the game data outside eboot.bin? Sample probe, read
only: for every file extension under games/PPSA21564-app/data and sce_module, up to 12 files (spread over the sorted
list), the first 8 MiB of each are searched for the ELF64 LE magic with e_machine 0xE0 (AMDGPU) and for the RDNA
S_ENDPGM word 0xBF810000 (a raw program would carry it); also the share of high-entropy files (compressed / packed,
where neither would be visible). Prints per extension: files, sampled, ELF hits, endpgm hits, compressed-looking."""
import collections
import math
import os
import struct
import sys

ROOT = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/'
MAGIC = bytes([0x7F, 0x45, 0x4C, 0x46, 2, 1, 1])
ENDPGM = struct.pack('<I', 0xBF810000)
LOCK = 'C:/kyty/SEALED_RUN.lock'


def entropy(b):
    if not b:
        return 0.0
    c = collections.Counter(b[:65536])
    n = min(len(b), 65536)
    return -sum(v / n * math.log2(v / n) for v in c.values())


files = collections.defaultdict(list)
for sub in ('data', 'sce_module'):
    for d, _, fs in os.walk(ROOT + sub):
        for f in fs:
            ext = f.rsplit('.', 1)[-1].lower() if '.' in f else '(none)'
            files[ext].append(os.path.join(d, f))
tot = collections.Counter()
print('extensions', len(files), 'files', sum(len(v) for v in files.values()))
for ext in sorted(files, key=lambda e: -len(files[e])):
    if os.path.exists(LOCK):
        print('LOCK - exit 3')
        sys.exit(3)
    lst = sorted(files[ext])
    k = min(12, len(lst))
    pick = [lst[int(i * len(lst) / k)] for i in range(k)]
    elf = endp = high = 0
    for fp in pick:
        with open(fp, 'rb') as f:
            b = f.read(8 << 20)
        e = b.find(MAGIC)
        while e != -1:
            if len(b) >= e + 20 and struct.unpack_from('<H', b, e + 18)[0] == 0xE0:
                elf += 1
            e = b.find(MAGIC, e + 1)
        if ENDPGM in b:
            endp += 1
        if entropy(b) > 7.5:
            high += 1
    tot['sampled'] += k
    tot['elf'] += elf
    tot['endpgm_files'] += endp
    print('%-10s files %6d sampled %2d AMDGPU-ELF hits %d files-with-endpgm-word %d high-entropy %d' % (
        ext, len(lst), k, elf, endp, high))
print('total', dict(tot))
