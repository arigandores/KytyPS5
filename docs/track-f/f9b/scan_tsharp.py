# F9b: scan a dumped SRT ring buffer for gfx10 image descriptors (T#) whose base lies in [lo, hi).
# usage: python scan_tsharp.py <bin> <lo hex> <hi hex>
import struct, sys, collections

path, lo, hi = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
data = open(path, 'rb').read()
n = len(data) // 4
w = struct.unpack('<%dI' % n, data[:n * 4])
seen = collections.OrderedDict()
for i in range(n - 4):
    w0, w1, w2, w3 = w[i], w[i + 1], w[i + 2], w[i + 3]
    typ = w3 >> 28
    if typ < 8:
        continue
    addr = ((w1 & 0xff) << 40) | (w0 << 8)
    if not (lo <= addr < hi):
        continue
    fmt = (w1 >> 20) & 0x1ff
    width = (((w2 & 0x3fff) << 2) | (w1 >> 30)) + 1
    height = ((w2 >> 14) & 0x3fff) + 1
    sw = (w3 >> 20) & 0x1f
    base_l = (w3 >> 12) & 0xf
    last_l = (w3 >> 16) & 0xf
    dsel = w3 & 0xfff
    if width > 16384 or height > 16384 or dsel == 0:
        continue
    key = (addr, width, height, fmt, sw, base_l, last_l, typ)
    if key not in seen:
        seen[key] = []
    seen[key].append(i * 4)
for k, offs in seen.items():
    addr, width, height, fmt, sw, bl, ll, typ = k
    print('addr=0x%011x %dx%d fmt=%d sw=%d mips=%d..%d type=%d count=%d first_off=%d last_off=%d' % (
        addr, width, height, fmt, sw, bl, ll, typ, len(offs), offs[0], offs[-1]))
