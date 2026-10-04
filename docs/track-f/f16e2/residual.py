# F16e2 (HPP-570, Red Team): copy of the F16e residual.py (HPP-522) - every differing byte of the own clean-worktree build
# vs the F16d2 copy 4ad735ad, by class; build dir class f287\f16d2 / f287\f16e2 (same length). Optional 3rd argument:
# flip one byte of .text in a copy of argv[2] first (negative control).
# Usage: residual.py <own.exe> <ref.exe> [negctl]
import re
import struct
import sys

a = open(sys.argv[1], 'rb').read()
b = bytearray(open(sys.argv[2], 'rb').read())
assert len(a) == len(b), (len(a), len(b))
pe = struct.unpack_from('<I', a, 0x3c)[0]
nsec = struct.unpack_from('<H', a, pe + 6)[0]
osz = struct.unpack_from('<H', a, pe + 20)[0]
secs = []
for i in range(nsec):
    o = pe + 24 + osz + 40 * i
    name = a[o:o + 8].rstrip(b'\0').decode()
    vsz, va, rsz, rp = struct.unpack_from('<IIII', a, o + 8)
    secs.append((name, rp, rsz))


def sec(off):
    for n, rp, rsz in secs:
        if rp <= off < rp + rsz:
            return n
    return 'header'


if len(sys.argv) > 3 and sys.argv[3] == 'negctl':
    text = [s for s in secs if s[0] == '.text'][0]
    off = text[1] + text[2] // 2
    b[off] ^= 0x01
    print('negctl: flipped bit 0 of .text byte at offset', off)
b = bytes(b)

classes = [
    ('anon-namespace tag ?A0x<7|8 hex>@', rb'\?A0x[0-9A-F]{7,8}@'),
    ('build dir f287\\f16[de]2', rb'f287' + re.escape(bytes([92])) + rb'f16[de]2'),
    ('SDL revision string', rb'SDL-KytyPS5-[0-9a-z-]+'),
]
cover = {}
for label, rx in classes:
    for m in re.finditer(rx, a):
        for i in range(m.start(), m.end()):
            cover.setdefault(i, label)
diff = [i for i in range(len(a)) if a[i] != b[i]]
count = {}
other = {}
for i in diff:
    c = cover.get(i)
    if c is None:
        c = 'OTHER ' + sec(i)
        other.setdefault(sec(i), []).append(i)
    count[c] = count.get(c, 0) + 1
print('size', len(a), 'differing bytes', len(diff))
for k in sorted(count):
    print('  %-40s %d' % (k, count[k]))
for s, offs in other.items():
    for i in offs[:8]:
        print('  other %s 0x%08x a=%02x b=%02x ctx=%r' % (s, i, a[i], b[i], a[max(0, i - 16):i + 16]))
text_other = len(other.get('.text', []))
print('VERDICT', '.text differing bytes', text_other)
