# FSb (HPP-369): compare own build of 95eec776 with the FSa binary dac02fb9.
# Prints PE timestamps, section sizes, string multiset difference after mapping the worktree path
# fsb -> fsa, and the first difference inside .data.
import re, struct, collections, sys, hashlib

A_PATH = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/fsb/build/install/kyty_emulator.exe'
B_PATH = sys.argv[2] if len(sys.argv) > 2 else 'C:/kyty/f287/bin/kyty_emulator_dac02fb9.exe'
A = open(A_PATH, 'rb').read()
B = open(B_PATH, 'rb').read()
BS = bytes([92])


def secs(d):
    pe = struct.unpack_from('<I', d, 0x3c)[0]
    n = struct.unpack_from('<H', d, pe + 6)[0]
    ts = struct.unpack_from('<I', d, pe + 8)[0]
    opt = struct.unpack_from('<H', d, pe + 20)[0]
    o = pe + 24 + opt
    r = {}
    for _ in range(n):
        name = d[o:o + 8].rstrip(b'\0').decode()
        vs, va, rs, rp = struct.unpack_from('<IIII', d, o + 8)
        r[name] = (vs, va, rs, rp)
        o += 40
    return ts, r


print('A', A_PATH, hashlib.sha256(A).hexdigest(), len(A))
print('B', B_PATH, hashlib.sha256(B).hexdigest(), len(B))
ta, ra = secs(A)
tb, rb = secs(B)
print('timestamp', hex(ta), hex(tb))
for k in ra:
    print('section', k, 'A vsize', hex(ra[k][0]), 'B vsize', hex(rb[k][0]), 'equal' if ra[k][0] == rb[k][0] else 'DIFF')

na = A.replace(b'f287' + BS + b'fsb', b'f287' + BS + b'fsa').replace(b'f287/fsb', b'f287/fsa')
pa_cnt = A.count(b'f287' + BS + b'fsb') + A.count(b'f287/fsb')
pb_cnt = B.count(b'f287' + BS + b'fsa') + B.count(b'f287/fsa')
print('worktree path occurrences A', pa_cnt, 'B', pb_cnt)


def strs(d):
    return collections.Counter(m.group() for m in re.finditer(rb'[\x20-\x7e]{12,}', d))


a = strs(na)
b = strs(B)
oa = a - b
ob = b - a
pa = [s for s in oa if b'kyty' in s.lower() or BS in s or b'/' in s or b'KYTY' in s]
pb = [s for s in ob if b'kyty' in s.lower() or BS in s or b'/' in s or b'KYTY' in s]
print('strings>=12 only A', sum(oa.values()), 'only B', sum(ob.values()), 'path-like only A', len(pa), 'only B', len(pb))
for s in pa[:30]:
    print('  A', oa[s], s[:220])
for s in pb[:30]:
    print('  B', ob[s], s[:220])

# .data first difference
_, _, rsa, rpa = ra['.data']
_, _, rsb, rpb = rb['.data']
da = na[rpa:rpa + rsa]
db = B[rpb:rpb + rsb]
i = next((i for i in range(min(len(da), len(db))) if da[i] != db[i]), None)
print('first .data diff at', hex(i) if i is not None else None)
if i is not None:
    print('  A', da[max(0, i - 48):i + 300])
    print('  B', db[max(0, i - 48):i + 300])
