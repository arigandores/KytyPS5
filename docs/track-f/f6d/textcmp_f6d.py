# F6d (HPP-376): copy of fsb/textcmp_fsb.py - own build f6d vs F6c d8756dce (p.286(b)(iii)).
# (1) strings multiset after mapping the worktree path fsb->fsa and masking MSVC anonymous-namespace
#     hashes ?A0x########; (2) .text: contiguous differing byte runs and, for each run, the signed
#     difference of the enclosing little-endian 32-bit displacement (the run's 4-byte window ending at the run end).
import re, struct, collections, sys

A = open('C:/kyty/f287/f6d/build/install/kyty_emulator.exe', 'rb').read()
B = open('C:/kyty/f287/bin/kyty_emulator_d8756dce.exe', 'rb').read()
BS = bytes([92])


def secs(d):
    pe = struct.unpack_from('<I', d, 0x3c)[0]
    n = struct.unpack_from('<H', d, pe + 6)[0]
    opt = struct.unpack_from('<H', d, pe + 20)[0]
    o = pe + 24 + opt
    r = {}
    for _ in range(n):
        name = d[o:o + 8].rstrip(b'\0').decode()
        vs, va, rs, rp = struct.unpack_from('<IIII', d, o + 8)
        r[name] = (vs, va, rs, rp)
        o += 40
    return r


ra, rb = secs(A), secs(B)
na = A.replace(b'f287' + BS + b'f6d', b'f287' + BS + b'f6c').replace(b'f287/f6d', b'f287/f6c')
anon = re.compile(rb'\?A0x[0-9A-F]{1,8}')


def strs(d):
    return collections.Counter(anon.sub(b'?A0xXXXXXXXX', m.group()) for m in re.finditer(rb'[\x20-\x7e]{8,}', d))


for sec in ('.rdata', '.data'):
    va = na[ra[sec][3]:ra[sec][3] + ra[sec][2]]
    vb = B[rb[sec][3]:rb[sec][3] + rb[sec][2]]
    a, b = strs(va), strs(vb)
    oa, ob = a - b, b - a
    print(sec, 'strings>=8 total A', sum(a.values()), 'B', sum(b.values()), 'only A', sum(oa.values()), 'only B', sum(ob.values()))
    for s in list(oa)[:10]:
        print('   A', s[:160])
    for s in list(ob)[:10]:
        print('   B', s[:160])
    print(sec, 'anon hashes A', len(set(anon.findall(va))), 'B', len(set(anon.findall(vb))))

ta = A[ra['.text'][3]:ra['.text'][3] + ra['.text'][0]]
tb = B[rb['.text'][3]:rb['.text'][3] + rb['.text'][0]]
assert len(ta) == len(tb)
runs = []
i, n = 0, len(ta)
while i < n:
    if ta[i] != tb[i]:
        j = i
        while j < n and ta[j] != tb[j]:
            j += 1
        runs.append((i, j - i))
        i = j
    else:
        i += 1
lens = collections.Counter(l for _, l in runs)
print('.text bytes', n, 'differing runs', len(runs), 'differing bytes', sum(l for _, l in runs))
print('.text run length histogram', sorted(lens.items()))
deltas = collections.Counter()
for s, l in runs:
    if l > 4:
        deltas['run>4'] += 1
        continue
    # the 4-byte displacement whose high bytes are equal: try windows that cover the run
    best = None
    for st in range(s + l - 4, s + 1):
        if st < 0:
            continue
        x = struct.unpack_from('<i', ta, st)[0]
        y = struct.unpack_from('<i', tb, st)[0]
        dlt = x - y
        if best is None or abs(dlt) < abs(best):
            best = dlt
    deltas[best] += 1
    if best not in (320,) and abs(best) < 16:
        print('  small delta', best, 'at .text+', hex(s), 'len', l, ta[max(0,s-12):s+8].hex(), tb[max(0,s-12):s+8].hex())
print('.text displacement deltas (top 20)', deltas.most_common(20))
print('.text distinct deltas', len(deltas))
