# S12b (HPP-495, Red Team): S12 adb0c82f vs FS5 631ff987 by PDB section contributions (llvm-pdbutil dump
# -section-contribs / -publics, dumps made by dumps_s12b.sh into the work dir given as argv[1]).
# data crc = CRC of the object's raw section bytes BEFORE relocation, so equal (size, crc) = equal code whatever the
# final displacements. (1) per (section, module) multisets of (size, crc); (2) .text of module 720
# (pipelineCache.cpp, ThinLTO object): contributions only in S12 / only in FS5; (3) every same-size pair of (2) and
# the libFont pair (module 826): each differing byte run classified by the 4-byte LE window with the smallest
# |A - B|: line+3 (__LINE__ after the +3-line edit), path-4 (string length of the 4-char shorter worktree path),
# disp_far (rip-relative / far call displacement), call_near (e8/e9/0f8x rel32 inside the module), other.
import re, sys, struct, collections

W = sys.argv[1]
EXE_A = 'C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe'
EXE_B = 'C:/kyty/f287/bin/kyty_emulator_631ff987.exe'
rx = re.compile(r'SC\[([^\]]+)\]\s+\| mod = (\d+), (\d{4}):(\d+), size = (\d+), data crc = (\d+)')
ok = True


def load(f):
    per = collections.defaultdict(list)
    for m in rx.finditer(open(f, encoding='utf-8', errors='replace').read()):
        per[(m.group(1).strip()[:8], int(m.group(2)))].append((int(m.group(4)), int(m.group(5)), int(m.group(6))))
    return per


def pubs(f):
    return {int(m.group(2)): m.group(1) for m in re.finditer(
        r"S_PUB32 \[size = \d+\] `([^`]*)`\s+flags = [^,]*, addr = 0001:(\d+)", open(f, encoding='utf-8', errors='replace').read())}


a, b = load(W + '/sc_s12.txt'), load(W + '/sc_fs5.txt')
pa, pb = pubs(W + '/pub_s12.txt'), pubs(W + '/pub_fs5.txt')
print('(1) contributions per section (S12):', dict(collections.Counter(k[0] for k in a)))
diff_text = []
for k in sorted(set(a) | set(b)):
    ca = collections.Counter((s, c) for o, s, c in a.get(k, []))
    cb = collections.Counter((s, c) for o, s, c in b.get(k, []))
    if ca != cb:
        if k[0] == '.text':
            diff_text.append(k[1])
        print('    differs %-8s mod %4d  onlyS12 %3d onlyFS5 %3d' % (k[0], k[1], sum((ca - cb).values()), sum((cb - ca).values())))
print('    .text modules that differ:', diff_text)
ok &= diff_text == [720, 826]


def secs(d):
    pe = struct.unpack_from('<I', d, 0x3c)[0]
    n = struct.unpack_from('<H', d, pe + 6)[0]
    opt = struct.unpack_from('<H', d, pe + 20)[0]
    o = pe + 24 + opt
    for _ in range(n):
        name = d[o:o + 8].rstrip(b'\0').decode()
        vs, va, rs, rp = struct.unpack_from('<IIII', d, o + 8)
        if name == '.text':
            return rp
        o += 40


A = open(EXE_A, 'rb').read()
B = open(EXE_B, 'rb').read()
ra, rb = secs(A), secs(B)


def only(x, y, mod):
    cy = collections.Counter((s, c) for o, s, c in y[('.text', mod)])
    out = []
    for o, s, c in x[('.text', mod)]:
        if cy[(s, c)] > 0:
            cy[(s, c)] -= 1
        else:
            out.append((o, s, c))
    return out


def classify(oa, ob, size):
    x, y = A[ra + oa:ra + oa + size], B[rb + ob:rb + ob + size]
    t = collections.Counter()
    oth = []
    i = 0
    while i < size:
        if x[i] == y[i]:
            i += 1
            continue
        j = i
        while j < size and x[j] != y[j]:
            j += 1
        cands = []
        for s in range(max(0, j - 4), i + 1):
            if s + 4 <= size:
                va_, vb_ = struct.unpack_from('<i', x, s)[0], struct.unpack_from('<i', y, s)[0]
                cands.append((abs(va_ - vb_), va_, vb_, s))
        d, va_, vb_, s = min(cands)
        if va_ - vb_ == 3 and 0 < vb_ < 0x2000:
            t['line+3'] += 1
        elif va_ - vb_ == -4 and 0 < vb_ < 0x1000:
            t['path-4'] += 1
        elif abs(va_) > 0x10000 and d <= 0x2000:
            t['disp_far'] += 1
        elif s > 0 and (x[s - 1] in (0xe8, 0xe9) or (s > 1 and x[s - 2] == 0x0f and 0x80 <= x[s - 1] <= 0x8f)) and d <= 0x2000:
            t['call_near'] += 1
        else:
            t['other'] += 1
            oth.append('0x%x %s / %s' % (0x1000 + oa + i, x[max(0, i - 6):j + 4].hex(), y[max(0, i - 6):j + 4].hex()))
        i = j
    return t, oth


for mod, label in ((720, 'pipelineCache.cpp'), (826, 'libFont.cpp')):
    oa_, ob_ = only(a, b, mod), only(b, a, mod)
    print('(2) .text mod %d (%s): contributions S12 %d FS5 %d; only S12 %d, only FS5 %d' % (
        mod, label, len(a[('.text', mod)]), len(b[('.text', mod)]), len(oa_), len(ob_)))
    xa = [r for r in oa_ if not (r[1] == 46 and mod == 720)]
    extra = [r for r in oa_ if r[1] == 46 and mod == 720]
    for o, s, c in extra:
        print('    S12-only out-of-line 46-byte function RVA 0x%x crc %d' % (0x1000 + o, c))
    tot = collections.Counter()
    for (o1, s1, c1), (o2, s2, c2) in zip(xa, ob_):
        name = pa.get(o1, '(no public)')[:70]
        if s1 != s2:
            print('    size %6d -> %6d  RVA S12 0x%x  %s' % (s2, s1, 0x1000 + o1, name))
            continue
        t, oth = classify(o1, o2, s1)
        tot += t
        if oth:
            print('    OTHER in RVA 0x%x:' % (0x1000 + o1), oth[:5])
    print('    same-size pairs, differing runs by class:', dict(tot))
    ok &= tot['other'] == 0
print('ALL OK' if ok else 'CHECK FAILED')
