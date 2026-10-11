# F42b2 (HPP-806, Red Team; ROADMAP s122 item 705(b)(6)): own build of the F42a2 tree (worktree f42b2) against the
# F42a2 copies - every differing byte is put into a named class, everything else is OTHER; ALL OK only when OTHER == 0.
# Classes (named before reading the stand binary, after the emulator pass printed its runs):
#   hdr      - PE header bytes (time stamp / checksum) and the debug directory (PDB GUID / age / time stamp);
#   path     - a printable string that, with 'f42a2' replaced by 'f42b2', is equal in A and B (build/worktree dir);
#   sdlrev   - the string ^SDL-KytyPS5-<date>-<sha7>-<n>-g<hex>$ (git describe at CMake configure time);
#   version  - the string ^KytyPS5-<date>-<sha7>-<n>-g<hex>$ (git describe at build time; F42a2 5ccb1d31, own 607fabaf -
#              equal trees, other commit objects) and a 40-hex git revision string;
#   anon     - a string with '?A0x<hex>' (clang-cl anonymous namespace hash from the source path) in .data;
#   data-move- .data/.rdata qword or dword that is a VA / RVA into .data in both files (objects after the anon strings move);
#   code     - a .text function (from .pdata) where every instruction pair is equal, or has the same mnemonic and operand text
#              without the RIP displacement, and the two RIP targets are either both in .data, or both in .rdata with the
#              same 48 bytes at the target after the path/version normalisation below;
#   rdata-move - .rdata pointers / RVAs to .rdata whose targets hold the same normalised 48 bytes.
# Usage: cmpfn_f42b2.py <A.exe> <B.exe>
import re
import struct
import sys

import capstone

a = open(sys.argv[1], 'rb').read()
b = open(sys.argv[2], 'rb').read()
assert len(a) == len(b), (len(a), len(b))


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
    dbg_rva, dbg_size = struct.unpack_from('<II', x, dd + 6 * 8)
    exc_rva, exc_size = struct.unpack_from('<II', x, dd + 3 * 8)
    return base, secs, so + 40 * nsec, (dbg_rva, dbg_size), (exc_rva, exc_size)


BASE, SECS, HDR_END, DBG, EXC = pe(a)
assert pe(b)[1] == SECS, 'section tables differ'


def sec_of_off(p):
    for n, va, vs, rp, rs in SECS:
        if rp <= p < rp + rs:
            return n
    return 'hdr'


def rva2off(r):
    for n, va, vs, rp, rs in SECS:
        if va <= r < va + rs:
            return rp + r - va
    return None


def off2rva(p):
    for n, va, vs, rp, rs in SECS:
        if rp <= p < rp + rs:
            return va + p - rp
    return None


def sec_of_rva(r):
    for n, va, vs, rp, rs in SECS:
        if va <= r < va + max(vs, rs):
            return n
    return None


PR = set(range(0x20, 0x7f))


def string_at(x, p):
    s = p
    while s > 0 and x[s - 1] in PR:
        s -= 1
    e = p
    while e < len(x) and x[e] in PR:
        e += 1
    return x[s:e]


SDL = re.compile(rb'^SDL-KytyPS5-\d{4}-\d{2}-\d{2}-[0-9a-f]{7}-\d+-g[0-9a-f]+$')
VER = re.compile(rb'^KytyPS5-\d{4}-\d{2}-\d{2}-[0-9a-f]{7}-\d+-g[0-9a-f]+$')
HEX40 = re.compile(rb'^[0-9a-f]{40}$')
# added after the first emulator pass (7 bytes OTHER): the build-origin string 'Fork build <repo> <sha7>' - the same HEAD sha
FORK = re.compile(rb'^Fork build \S+ [0-9a-f]{7}$')
VERSUB = re.compile(rb'(KytyPS5-\d{4}-\d{2}-\d{2}-[0-9a-f]{7}-\d+-g)[0-9a-f]{8}')


def norm(x):
    x = x.replace(b'f42a2', b'f42b2')
    x = VERSUB.sub(rb'\1________', x)
    x = re.sub(rb'\?A0x[0-9A-F]{1,8}@', b'?A0x________@', x)
    return x


# debug directory entries -> raw data ranges (CodeView GUID / age, time stamps)
dbg_ranges = []
if DBG[0]:
    o = rva2off(DBG[0])
    for k in range(DBG[1] // 28):
        e = o + 28 * k
        dbg_ranges.append((e, e + 28))
        size, rva, ptr = struct.unpack_from('<III', a, e + 16)
        dbg_ranges.append((ptr, ptr + size))

diffs = [i for i in range(len(a)) if a[i] != b[i]]
cls = {}
left = []
text_diffs = []
for i in diffs:
    s = sec_of_off(i)
    if i < HDR_END or any(lo <= i < hi for lo, hi in dbg_ranges):
        cls['hdr'] = cls.get('hdr', 0) + 1
        continue
    if s == '.text':
        text_diffs.append(i)
        continue
    sa, sb = string_at(a, i), string_at(b, i)
    if sa and sa.replace(b'f42a2', b'f42b2') == sb and sa != sb:
        cls['path'] = cls.get('path', 0) + 1
        continue
    if SDL.match(sa) and SDL.match(sb):
        cls['sdlrev'] = cls.get('sdlrev', 0) + 1
        continue
    if (VER.match(sa) and VER.match(sb)) or (HEX40.match(sa) and HEX40.match(sb)) or (FORK.match(sa) and FORK.match(sb)):
        cls['version'] = cls.get('version', 0) + 1
        continue
    if b'?A0x' in sa and b'?A0x' in sb and norm(sa) == norm(sb):
        cls['anon'] = cls.get('anon', 0) + 1
        continue
    # pointer / RVA moves
    ok = False
    for w, fmt in ((8, '<Q'), (4, '<I')):
        q = i - (i % w)
        va_, vb_ = struct.unpack_from(fmt, a, q)[0], struct.unpack_from(fmt, b, q)[0]
        ra, rb = (va_ - BASE, vb_ - BASE) if w == 8 else (va_, vb_)
        sa_, sb_ = sec_of_rva(ra), sec_of_rva(rb)
        if sa_ and sa_ == sb_ and sa_ in ('.data', '.rdata'):
            if sa_ == '.data':
                cls['data-move'] = cls.get('data-move', 0) + 1
                ok = True
                break
            oa, ob = rva2off(ra), rva2off(rb)
            if oa is not None and ob is not None and norm(a[oa:oa + 48]) == norm(b[ob:ob + 48]):
                cls['rdata-move'] = cls.get('rdata-move', 0) + 1
                ok = True
                break
    if not ok:
        left.append((s, i))

# .text by function
exc_off = rva2off(EXC[0])
funcs = []
for k in range(EXC[1] // 12):
    s0, e0, _ = struct.unpack_from('<III', a, exc_off + 12 * k)
    if s0:
        funcs.append((s0, e0))
assert a[exc_off:exc_off + EXC[1]] == b[exc_off:exc_off + EXC[1]], '.pdata differs'
funcs.sort()
import bisect
starts = [f[0] for f in funcs]
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = False
bad_funcs = []
done = set()
nfun = 0
for i in text_diffs:
    r = off2rva(i)
    k = bisect.bisect_right(starts, r) - 1
    if k < 0 or not (funcs[k][0] <= r < funcs[k][1]):
        bad_funcs.append(('nofunc', hex(r)))
        continue
    if k in done:
        continue
    done.add(k)
    nfun += 1
    s0, e0 = funcs[k]
    oa = rva2off(s0)
    ca, cb = a[oa:oa + e0 - s0], b[oa:oa + e0 - s0]
    ia, ib = list(md.disasm(ca, BASE + s0)), list(md.disasm(cb, BASE + s0))
    good = len(ia) == len(ib)
    if good:
        for x, y in zip(ia, ib):
            if x.bytes == y.bytes:
                continue
            if x.mnemonic != y.mnemonic or x.size != y.size or 'rip' not in x.op_str:
                good = False
                break
            ma = re.search(r'\[rip ([+-]) (0x[0-9a-f]+|\d+)\]', x.op_str)
            mb = re.search(r'\[rip ([+-]) (0x[0-9a-f]+|\d+)\]', y.op_str)
            if not ma or not mb:
                good = False
                break
            if x.op_str.replace(ma.group(0), '[rip]') != y.op_str.replace(mb.group(0), '[rip]'):
                good = False
                break
            ta = x.address + x.size + (1 if ma.group(1) == '+' else -1) * int(ma.group(2), 0) - BASE
            tb = y.address + y.size + (1 if mb.group(1) == '+' else -1) * int(mb.group(2), 0) - BASE
            sa_, sb_ = sec_of_rva(ta), sec_of_rva(tb)
            if sa_ != sb_:
                good = False
                break
            if sa_ == '.data':
                continue
            if sa_ == '.rdata':
                pa, pb = rva2off(ta), rva2off(tb)
                if norm(a[pa:pa + 48]) == norm(b[pb:pb + 48]):
                    continue
            good = False
            break
    if not good:
        bad_funcs.append(hex(s0))
cls['code(functions)'] = nfun - len(bad_funcs)
print('differing bytes', len(diffs), '.text bytes', len(text_diffs), 'functions with a .text difference', nfun)
print('classes', cls)
print('OTHER non-text', len(left), left[:20])
for s, i in left[:20]:
    print('  ', s, hex(i), string_at(a, i)[:80], string_at(b, i)[:80])
print('OTHER functions', len(bad_funcs), bad_funcs[:20])
print('ALL OK' if not left and not bad_funcs else 'NOT OK')
