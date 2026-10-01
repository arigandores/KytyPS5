# F6a (HPP-372): who references a function of eboot.elf: call/jmp rel32, rip-relative lea, 8-byte data words (vtables).
# usage: f6a_callers.py <hex> [<hex>...]
import sys, struct, re, collections
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
elf = Elf('C:/kyty/eboot.elf'); e = elf.data
T = [int(a, 16) for a in sys.argv[1:]]
ts = set(T)
res = collections.defaultdict(list)
for v, o, fs in elf.code_segments():
    seg = e[o:o + fs]
    for m in re.finditer(rb'[\xe8\xe9]', seg):
        i = m.start()
        if i + 5 > fs: continue
        t = v + i + 5 + struct.unpack('<i', seg[i + 1:i + 5])[0]
        if t in ts: res[t].append(('call' if seg[i] == 0xe8 else 'jmp', v + i))
    for m in re.finditer(rb'\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]', seg):
        i = m.start()
        t = v + i + 6 + struct.unpack('<i', seg[i + 2:i + 6])[0]
        if t in ts: res[t].append(('lea', v + i - 1))
for v, o, fs in elf.data_segments():
    seg = e[o:o + fs]
    for t in T:
        for val in (t, t + elf.base):
            pat = struct.pack('<Q', val); k = seg.find(pat)
            while k >= 0:
                if k % 8 == 0: res[t].append(('data', v + k))
                k = seg.find(pat, k + 1)
for t in T:
    print('0x%x: %s' % (t, ' '.join('%s@0x%x' % r for r in res[t]) or 'no references'))
