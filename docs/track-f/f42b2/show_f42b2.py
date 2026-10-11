# F42b2 (HPP-806): print the first non-accepted instruction pairs of given .text units (rva hex) and the raw bytes of given
# file offsets of both files. Usage: show_f42b2.py <A> <B> u:<rva>,... o:<off>,...
import re
import struct
import sys

import capstone

a = open(sys.argv[1], 'rb').read()
b = open(sys.argv[2], 'rb').read()
p = struct.unpack_from('<I', a, 0x3c)[0]
base = struct.unpack_from('<Q', a, p + 24 + 24)[0]
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
for arg in sys.argv[3:]:
    kind, vals = arg.split(':', 1)
    for v in vals.split(','):
        x = int(v, 16) if kind == 'u' else int(v)
        if kind == 'u':
            off = x - 0x1000 + 0x400
            ia = list(md.disasm(a[off:off + 400], base + x))
            ib = list(md.disasm(b[off:off + 400], base + x))
            shown = 0
            for s, t in zip(ia, ib):
                if s.bytes != t.bytes:
                    print('u %x  A %x %s %s | B %s %s' % (x, s.address, s.mnemonic, s.op_str, t.mnemonic, t.op_str))
                    shown += 1
                    if shown >= 4:
                        break
        else:
            print('o %d A %s' % (x, a[x - 16:x + 32].hex()))
            print('o %d B %s' % (x, b[x - 16:x + 32].hex()))
