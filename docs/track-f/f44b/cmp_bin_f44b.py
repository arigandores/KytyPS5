# F44b (HPP-792): why the sha256 of the own clean build differs from the F44a copy: size, worktree path strings,
# PE header time stamp / checksum, and the byte diff after replacing the own path by the F44a path (same length).
import hashlib, struct, sys
a = open(sys.argv[1], 'rb').read()   # F44a copy
b = open(sys.argv[2], 'rb').read()   # own build
pa, pb = sys.argv[3].encode(), sys.argv[4].encode()
print('sha a', hashlib.sha256(a).hexdigest()[:16], 'size', len(a))
print('sha b', hashlib.sha256(b).hexdigest()[:16], 'size', len(b))
for name, x in (('a', a), ('b', b)):
    for p in (pa, pb, pa.replace(b'/', b'\\'), pb.replace(b'/', b'\\')):
        print(name, p, x.count(p))
def pe(x):
    off = struct.unpack_from('<I', x, 0x3c)[0]
    ts = struct.unpack_from('<I', x, off + 8)[0]
    ck = struct.unpack_from('<I', x, off + 24 + 64)[0]
    return off, ts, ck
print('pe a', pe(a), 'pe b', pe(b))
c = b
for p, q in ((pb, pa), (pb.replace(b'/', b'\\'), pa.replace(b'/', b'\\'))):
    c = c.replace(p, q)
if len(c) != len(a):
    print('len differs after path swap', len(c), len(a)); sys.exit(1)
diff = [i for i in range(len(a)) if a[i] != c[i]]
print('bytes differing after path swap', len(diff))
runs = []
for i in diff:
    if runs and i - runs[-1][1] <= 16:
        runs[-1][1] = i
    else:
        runs.append([i, i])
print('runs', len(runs))
off = struct.unpack_from('<I', a, 0x3c)[0]
for s, e in runs[:20]:
    tag = ''
    if off + 8 <= s <= off + 12: tag = 'PE TimeDateStamp'
    if off + 24 + 64 <= s <= off + 24 + 68: tag = 'PE CheckSum'
    print(hex(s), e - s + 1, a[max(0, s - 8):e + 9][:48], c[max(0, s - 8):e + 9][:48], tag)
