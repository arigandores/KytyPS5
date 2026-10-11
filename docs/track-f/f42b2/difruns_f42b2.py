# F42b2 (HPP-806, Red Team): all differing byte runs of two equal-size PE files that pediff3r left as OTHER, with the
# printable string around each run (to name the class of every byte). Usage: difruns_f42b2.py <A.exe> <B.exe> [skip .text]
import struct
import sys

a = open(sys.argv[1], 'rb').read()
b = open(sys.argv[2], 'rb').read()
assert len(a) == len(b), (len(a), len(b))


def sections(x):
    pe = struct.unpack_from('<I', x, 0x3c)[0]
    opt = pe + 24
    nsec = struct.unpack_from('<H', x, pe + 6)[0]
    so = opt + struct.unpack_from('<H', x, pe + 20)[0]
    out = []
    for k in range(nsec):
        h = so + 40 * k
        name = x[h:h + 8].rstrip(b'\0').decode()
        rsize, rptr = struct.unpack_from('<II', x, h + 16)
        out.append((name, rptr, rptr + rsize))
    return out


SEC = sections(a)


def sec_of(p):
    for n, s, e in SEC:
        if s <= p < e:
            return n
    return 'hdr'


PR = set(range(0x20, 0x7f))


def string_at(x, p):
    s = p
    while s > 0 and x[s - 1] in PR:
        s -= 1
    e = p
    while e < len(x) and x[e] in PR:
        e += 1
    return x[s:e]


diffs = [i for i in range(len(a)) if a[i] != b[i]]
runs = []
for i in diffs:
    if runs and i - runs[-1][1] <= 16:
        runs[-1][1] = i
    else:
        runs.append([i, i])
by = {}
for s, e in runs:
    by.setdefault(sec_of(s), []).append((s, e))
print('differing bytes', len(diffs), 'runs', len(runs), {k: len(v) for k, v in by.items()})
for name, rs in by.items():
    if name == '.text' and len(sys.argv) > 3:
        continue
    for s, e in rs[:40]:
        n = sum(1 for i in range(s, e + 1) if a[i] != b[i])
        print('%s 0x%08x..0x%08x n=%d A=%r B=%r' % (name, s, e, n, string_at(a, s)[:90], string_at(b, s)[:90]))
