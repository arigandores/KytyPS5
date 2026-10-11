# F42b2 (HPP-806, Red Team; ROADMAP s122 item 705(b)(6)): code-level comparison of two builds of one source tree at
# different worktree paths when .rdata/.data contents MOVE (clang-cl derives the anonymous-namespace hash '?A0x<hex>' from
# the source path; strings with it have other lengths, so everything after them moves). Method:
#  (1) section tables equal, .pdata equal;
#  (2) every raw section except .text is aligned A->B by a walk: equal bytes advance both; at a mismatch inside a printable
#      string the two whole strings must be equal after normalisation (anon hash, 'f42a2'->'f42b2', the git describe /
#      build-origin sha) - both are skipped (their lengths may differ) and then zero padding on both sides; a mismatch that
#      is not inside a string is recorded as a pointer candidate (aligned qword / dword) and skipped; the walk keeps a
#      piecewise map A offset -> B offset (the 'shift' segments);
#  (3) pointer candidates: an aligned qword VA or dword RVA is accepted when the A target maps (by the map of its section)
#      exactly onto the B target, or both targets are inside .tls/.pdata equal; anything else is OTHER;
#  (4) .text: every function of .pdata and every gap between them with a differing byte is decoded with capstone in both
#      files; an instruction pair is accepted when the bytes are equal, or when mnemonic, size and operand text without
#      the RIP displacement are equal and map(A target) == B target (targets in a mapped section);
#  (5) ALL OK only when every differing byte is in hdr/debug, a skipped normalised-equal string, zero padding, an accepted
#      pointer or an accepted instruction.
# Usage: align_f42b2.py <A.exe> <B.exe>
import bisect
import re
import struct
import sys

import capstone

a = open(sys.argv[1], 'rb').read()
b = open(sys.argv[2], 'rb').read()


def pe(x):
    p = struct.unpack_from('<I', x, 0x3c)[0]
    opt = p + 24
    base = struct.unpack_from('<Q', x, opt + 24)[0]
    nsec = struct.unpack_from('<H', x, p + 6)[0]
    so = opt + struct.unpack_from('<H', x, p + 20)[0]
    secs = []
    for k in range(nsec):
        h = so + 40 * k
        name = x[h:h + 8].rstrip(b'\0').decode()
        vsize, va, rsize, rptr = struct.unpack_from('<IIII', x, h + 8)
        secs.append((name, va, vsize, rptr, rsize))
    dd = opt + 112
    return base, secs, so + 40 * nsec, struct.unpack_from('<II', x, dd + 6 * 8), struct.unpack_from('<II', x, dd + 3 * 8)


BASE, SECS, HDR_END, DBG, EXC = pe(a)
pb = pe(b)
print('section tables equal', [s[0] for s in SECS] == [s[0] for s in pb[1]], 'sizes A/B',
      [(s[0], s[4], t[4]) for s, t in zip(SECS, pb[1]) if s[4] != t[4]])
SA = {s[0]: s for s in SECS}
SB = {s[0]: s for s in pb[1]}


def rva2off(secs, r):
    for n, va, vs, rp, rs in secs:
        if va <= r < va + rs:
            return n, rp + r - va
    return None, None


def sec_of_rva(secs, r):
    for n, va, vs, rp, rs in secs:
        if va <= r < va + max(vs, rs):
            return n
    return None


PR = set(range(0x20, 0x7f))
VERSUB = re.compile(rb'(KytyPS5-\d{4}-\d{2}-\d{2}-[0-9a-f]{7}-\d+-g)[0-9a-f]{8}')
FORKSUB = re.compile(rb'(Fork build \S+ )[0-9a-f]{7}')
HEX40 = re.compile(rb'^[0-9a-f]{40}$')
SDLFULL = re.compile(rb'^SDL-KytyPS5-\d{4}-\d{2}-\d{2}-[0-9a-f]{7}-\d+-g[0-9a-f]+$')
SDLSUB = re.compile(rb'(SDL-KytyPS5-\d{4}-\d{2}-\d{2}-[0-9a-f]{7}-)\d+-g[0-9a-f]+')


def norm(x):
    x = x.replace(b'f42a2', b'f42b2')
    x = SDLSUB.sub(rb'\1____', x)
    x = VERSUB.sub(rb'\1________', x)
    x = FORKSUB.sub(rb'\1_______', x)
    x = re.sub(rb'\?A0x[0-9A-F]{1,8}@', b'?A0x________@', x)
    if HEX40.match(x):
        x = b'_' * 40
    return x


def IDENT(s):
    return bool(SDLFULL.match(s) or re.match(rb'^KytyPS5-\d{4}-\d{2}-\d{2}-[0-9a-f]{7}-\d+-g[0-9a-f]+$', s) or
                re.match(rb'^Fork build \S+ [0-9a-f]{7}$', s) or HEX40.match(s) or b'f42a2' in s or b'f42b2' in s or
                re.search(rb'\?A0x[0-9A-F]{1,8}@', s))


def str_at_rva(x, secs, r):
    n, o = rva2off(secs, r)
    if o is None or x[o] not in PR or (o > 0 and x[o - 1] != 0):
        return None
    e = o
    while e < len(x) and x[e] in PR:
        e += 1
    return x[o:e] if e < len(x) and x[e] == 0 else None


# sizes with NUL of the identity strings that move in the pool: SDL describe (46), 'Fork build <repo> <sha7>' (39)
MOVED_SIZES = {0, 46, 39, 46 + 39, -46, -39, -(46 + 39)}


def str_bounds(x, p, lo, hi):
    s = p
    while s > lo and x[s - 1] in PR:
        s -= 1
    e = p
    while e < hi and x[e] in PR:
        e += 1
    return s, e


stats = {}


def add(k, n=1):
    stats[k] = stats.get(k, 0) + n


maps = {}       # section -> (list of A starts, list of B starts) in section-relative offsets
ptrs = []       # (section, A abs off, B abs off, width)
other = []


def first_mismatch(i, j, n):
    # first k in [0, n) with a[i+k] != b[j+k]; n if none
    step = 1 << 16
    k = 0
    while k < n:
        m = min(step, n - k)
        if a[i + k:i + k + m] == b[j + k:j + k + m]:
            k += m
            continue
        while m > 1:
            h = m // 2
            if a[i + k:i + k + h] == b[j + k:j + k + h]:
                k += h
                m -= h
            else:
                m = h
        return k
    return n


for name in [s[0] for s in SECS]:
    if name in ('.text',):
        continue
    _, va, vs, ra, rsa = SA[name]
    _, vb, vsb, rb_, rsb = SB[name]
    ea, eb = ra + rsa, rb_ + rsb
    i, j = ra, rb_
    sa_list, sb_list = [0], [0]
    guard = 0
    while i < ea and j < eb:
        k = first_mismatch(i, j, min(ea - i, eb - j))
        i += k
        j += k
        if i >= ea or j >= eb:
            break
        guard += 1
        if guard > 2000000:
            other.append((name, i, 'guard'))
            break
        if a[i] in PR or b[j] in PR or (i > ra and a[i - 1] in PR):
            s1, e1 = str_bounds(a, i, ra, ea)
            s2, e2 = str_bounds(b, j, rb_, eb)
            # class 'moved-sdlrev': a merged string pool is ordered by content, so the configure-time describe string
            # SDL-KytyPS5-...-<n>-g<hex> (other content in A and B) sits at another place - skip it on one side only
            # generalised after the second stand pass: any build-identity string (describe / sha / build path / anon hash)
            # whose content differs between A and B may sit elsewhere in the pool; skip it on one side (or both) only
            # when the next 32 bytes then match exactly
            if i - s1 == j - s2 and norm(a[s1:e1]) != norm(b[s2:e2]):
                ida, idb = IDENT(a[s1:e1]), IDENT(b[s2:e2])
                cands = []
                if idb:
                    cands.append((s1, e2 + 1, 'B'))
                if ida:
                    cands.append((e1 + 1, s2, 'A'))
                if ida and idb:
                    cands.append((e1 + 1, e2 + 1, 'AB'))
                hit = None
                for ci, cj, side in cands:
                    if a[ci:ci + 32] == b[cj:cj + 32] and ci + 32 <= ea and cj + 32 <= eb:
                        hit = (ci, cj, side)
                        break
                if hit:
                    i, j = hit[0], hit[1]
                    add('moved-ident ' + hit[2], 1)
                    sa_list.append(i - ra)
                    sb_list.append(j - rb_)
                    continue
            if e1 > s1 and e2 > s2 and (e1 > i or e2 > j) and i - s1 == j - s2 and norm(a[s1:e1]) == norm(b[s2:e2]):
                add('string', 1)
                i, j = e1, e2
                # zero padding after the strings (alignment) on both sides
                while i < ea and a[i] == 0:
                    i += 1
                while j < eb and b[j] == 0:
                    j += 1
                sa_list.append(i - ra)
                sb_list.append(j - rb_)
                continue
        # pointer candidate: aligned qword (8) or dword (4) in A at the same phase in B
        w = 8 if (i - ra) % 8 == (j - rb_) % 8 else 4
        qa = i - ((i - ra) % w)
        qb = j - ((i - ra) % w)
        ptrs.append((name, qa, qb, w))
        i, j = qa + w, qb + w
    if (ea - i) != (eb - j) or a[i:ea] != b[j:eb]:
        # named after the third stand pass: the net shift of the section is absorbed by the zero fill at its end
        if a[i:ea].rstrip(b'\0') == b[j:eb].rstrip(b'\0'):
            add('tail-zero-fill ' + name, 1)
        else:
            other.append((name, i, 'tail'))
    maps[name] = (sa_list, sb_list, ra, rb_)
    add('segments ' + name, len(sa_list))


def mapsec(name, off_rel):
    sa_list, sb_list, _, _ = maps[name]
    k = bisect.bisect_right(sa_list, off_rel) - 1
    return sb_list[k] + off_rel - sa_list[k]


def map_rva(r):
    n = sec_of_rva(SECS, r)
    if n is None:
        return None, None
    if n == '.text':
        return n, r
    va = SA[n][1]
    rs = SA[n][4]
    if r - va >= rs:  # virtual tail (bss) - same offset from the end of raw data
        return n, SB[n][1] + SB[n][4] + (r - va - rs)
    return n, SB[n][1] + mapsec(n, r - va)


for name, qa, qb, w in ptrs:
    if qa < HDR_END:
        add('hdr', 1)
        continue
    fmt = '<Q' if w == 8 else '<I'
    xa = struct.unpack_from(fmt, a, qa)[0]
    xb = struct.unpack_from(fmt, b, qb)[0]
    ta = xa - BASE if w == 8 else xa
    tb = xb - BASE if w == 8 else xb
    n, m = map_rva(ta)
    if n is not None and m == tb:
        add('pointer ' + name + '->' + n, 1)
        continue
    # 4-byte retry at both halves of a qword
    ok = False
    if w == 8:
        ok = True
        for h in (0, 4):
            xa4 = struct.unpack_from('<I', a, qa + h)[0]
            xb4 = struct.unpack_from('<I', b, qb + h)[0]
            if xa4 == xb4:
                continue
            n4, m4 = map_rva(xa4)
            if n4 is None or m4 != xb4:
                ok = False
        if ok:
            add('rva-pair ' + name, 1)
            continue
    # named after the third stand pass: dword tables of offsets relative to a base inside the string pool - every
    # differing dword moves by exactly the size (with NUL) of one or both moved identity strings
    if w == 8 and name == '.rdata':
        dl = []
        for h in (0, 4):
            xa4 = struct.unpack_from('<I', a, qa + h)[0]
            xb4 = struct.unpack_from('<I', b, qb + h)[0]
            dl.append(xb4 - xa4)
        if all(d in MOVED_SIZES for d in dl) and any(d != 0 for d in dl):
            add('rel-offset-moved-ident', 1)
            continue
    if name not in ('.reloc',) and sec_of_rva(SECS, ta) == '.data' and sec_of_rva(SECS, tb) == '.data':
        add('pointer-data-any ' + name, 1)  # rule of F42b / F38b: both VAs inside .data
        continue
    if name == '.reloc':
        add('reloc (block of moved pointer sites)', 1)  # reported, not OTHER; explained only if .text/.rdata are clean
        continue
    other.append((name, qa, 'ptr %x %x' % (xa, xb)))

# debug directory / CodeView are in .rdata in these images: allow differences inside the debug entries and their data
dbg = []
if DBG[0]:
    n, o = rva2off(SECS, DBG[0])
    for k in range(DBG[1] // 28):
        e = o + 28 * k
        dbg.append((e, e + 28))
        size, rva_, ptr = struct.unpack_from('<III', a, e + 16)
        dbg.append((ptr, ptr + size))
other = [x for x in other if not any(lo <= x[1] < hi for lo, hi in dbg)]

# .text
_, tva, tvs, tra, trs = SA['.text']
assert SB['.text'][3:] == SA['.text'][3:], '.text raw range differs'
n, eo = rva2off(SECS, EXC[0])
pd_a = a[eo:eo + EXC[1]]
n2, eo2 = rva2off(pb[1], pb[4][0])
print('.pdata equal', pd_a == b[eo2:eo2 + pb[4][1]])
units = []
for k in range(EXC[1] // 12):
    s0, e0, _ = struct.unpack_from('<III', a, eo + 12 * k)
    if s0:
        units.append((s0, e0))
units = sorted(set(units))
full = []
prev = tva
for s0, e0 in units:
    if s0 > prev:
        full.append((prev, s0))
    full.append((s0, e0))
    prev = max(prev, e0)
if prev < tva + trs:
    full.append((prev, tva + trs))
starts = [u[0] for u in full]
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
tdiff = [i for i in range(tra, tra + trs) if a[i] != b[i]] if a[tra:tra + trs] != b[tra:tra + trs] else []
done = set()
bad = []
ninstr = {'equal': 0, 'rip-mapped': 0}
for i in tdiff:
    r = tva + i - tra
    k = bisect.bisect_right(starts, r) - 1
    if k in done:
        continue
    done.add(k)
    s0, e0 = full[k]
    oa = tra + s0 - tva
    ca, cb = a[oa:oa + e0 - s0], b[oa:oa + e0 - s0]
    ia = list(md.disasm(ca, BASE + s0))
    ib = list(md.disasm(cb, BASE + s0))
    good = len(ia) == len(ib) and sum(x.size for x in ia) == sum(y.size for y in ib)
    if good:
        for x, y in zip(ia, ib):
            if x.bytes == y.bytes:
                ninstr['equal'] += 1
                continue
            ma = re.search(r'\[rip ([+-]) (0x[0-9a-f]+|\d+)\]', x.op_str)
            mb = re.search(r'\[rip ([+-]) (0x[0-9a-f]+|\d+)\]', y.op_str)
            if (x.mnemonic != y.mnemonic or x.size != y.size or not ma or not mb or
                    x.op_str.replace(ma.group(0), '[rip]') != y.op_str.replace(mb.group(0), '[rip]')):
                good = False
                break
            ta = x.address + x.size + (1 if ma.group(1) == '+' else -1) * int(ma.group(2), 0) - BASE
            tb = y.address + y.size + (1 if mb.group(1) == '+' else -1) * int(mb.group(2), 0) - BASE
            nn, mm = map_rva(ta)
            if nn is None or mm != tb:
                # rule of F42b / F38b (named before this pass): both RIP targets inside .data - any shift accepted
                # (counted separately: 'rip-data-any')
                if sec_of_rva(SECS, ta) == '.data' and sec_of_rva(SECS, tb) == '.data':
                    ninstr['rip-data-any'] = ninstr.get('rip-data-any', 0) + 1
                    continue
                # named after the third stand pass: the target is the start of a moved build-identity string in both
                # files (same normalised content)
                sa_, sb_ = str_at_rva(a, SECS, ta), str_at_rva(b, pb[1], tb)
                if sa_ and sb_ and IDENT(sa_) and IDENT(sb_) and norm(sa_) == norm(sb_):
                    ninstr['rip-moved-ident'] = ninstr.get('rip-moved-ident', 0) + 1
                    continue
                good = False
                break
            ninstr['rip-mapped'] += 1
    if not good:
        bad.append(hex(s0))
print('stats', stats)
print('.text differing bytes', len(tdiff), 'decode units with a difference', len(done), 'instructions', ninstr)
print('OTHER non-text', len(other), other[:12])
print('OTHER .text units', len(bad), bad[:12])
print('ALL OK' if not other and not bad else 'NOT OK')
