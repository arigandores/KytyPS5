# F26a (HPP-688): references to an address: rip-relative lea/mov in code, raw qword in file (incl. RELA addends)
import sys, struct, re
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
elf = Elf(sys.argv[1]); e = elf.data
for a in sys.argv[2:]:
    t = int(a, 16)
    for v, off, fs in elf.code_segments():
        code = e[off:off + fs]
        for m in re.finditer(rb'[\x48\x4c][\x8d\x8b][\x05\x0d\x15\x1d\x25\x2d\x35\x3d]', code):
            i = m.start()
            if v + i + 7 + struct.unpack('<i', code[i + 3:i + 7])[0] == t:
                print('rip-ref at 0x%x -> 0x%x (%s)' % (v + i, t, code[i:i + 7].hex()))
    q = struct.pack('<Q', t)
    for m in re.finditer(re.escape(q), e):
        print('qword 0x%x at file off 0x%x' % (t, m.start()), 'ctx', e[m.start() - 16:m.start() + 16].hex())
