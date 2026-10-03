# F9b: scan a dumped SRT ring buffer for buffer descriptors (V#) whose range overlaps [lo, hi).
# usage: python scan_vsharp.py <bin> <lo hex> <hi hex>
import struct, sys, collections

path, lo, hi = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
data = open(path, 'rb').read()
n = len(data) // 4
w = struct.unpack('<%dI' % n, data[:n * 4])
seen = collections.OrderedDict()
for i in range(n - 4):
    w0, w1, w2, w3 = w[i], w[i + 1], w[i + 2], w[i + 3]
    if (w3 >> 30) != 0:
        continue
    addr = ((w1 & 0xffff) << 32) | w0
    stride = (w1 >> 16) & 0x3fff
    recs = w2
    size = recs * (stride if stride else 1)
    if size == 0 or size > (1 << 32):
        continue
    if addr >= hi or addr + size <= lo:
        continue
    if addr < 0x100000000:
        continue
    key = (addr, stride, recs, w3)
    seen.setdefault(key, []).append(i * 4)
for k, offs in seen.items():
    addr, stride, recs, w3 = k
    print('addr=0x%011x end=0x%011x stride=%d recs=%d w3=%08x count=%d first_off=%d' % (
        addr, addr + recs * (stride if stride else 1), stride, recs, w3, len(offs), offs[0]))
