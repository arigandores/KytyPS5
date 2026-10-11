# F44b (HPP-792): classify every differing byte (after the same-length path swap f44b -> f44a) by PE section and by
# class: anonymous-namespace token ?A0x<hex8> (clang-cl hashes it from the source path) or other.
import re, struct, sys
a = open(sys.argv[1], 'rb').read()
b = open(sys.argv[2], 'rb').read()
BS = bytes([92])
for p, q in ((b'kyty' + BS + b'f287' + BS + b'f44b' + BS, b'kyty' + BS + b'f287' + BS + b'f44a' + BS),
             (b'kyty/f287/f44b/', b'kyty/f287/f44a/')):
    b = b.replace(p, q)
off = struct.unpack_from('<I', a, 0x3c)[0]
nsec = struct.unpack_from('<H', a, off + 6)[0]
opt = struct.unpack_from('<H', a, off + 20)[0]
secs = []
for i in range(nsec):
    s = off + 24 + opt + 40 * i
    name = a[s:s + 8].rstrip(b'\0').decode()
    rsz, rptr = struct.unpack_from('<II', a, s + 16)
    secs.append((name, rptr, rptr + rsz))


def sec(i):
    for n, s, e in secs:
        if s <= i < e:
            return n
    return 'header'


anon = set()
for x in (a, b):
    for m in re.finditer(rb'\?A0x[0-9A-F]{8}', x):
        anon.update(range(m.start(), m.end()))
cnt = {}
other = []
for i in range(len(a)):
    if a[i] != b[i]:
        k = (sec(i), 'anon' if i in anon else 'other')
        cnt[k] = cnt.get(k, 0) + 1
        if k[1] == 'other':
            other.append(i)
print('sections', [(n, hex(s), hex(e)) for n, s, e in secs])
for k, v in sorted(cnt.items()):
    print('diff', k, v)
for i in other[:60]:
    print(' other', hex(i), sec(i), a[i - 12:i + 12], b[i - 12:i + 12])
