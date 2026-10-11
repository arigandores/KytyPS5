# F40b2 (HPP-786, Red Team): copy of cmp_code_f38b.py (C:/kyty/KytyPS5 docs/track-f/f38b/), the path replacement f40b2 -> f40a2. Was:
"""F38b (HPP-764): code-level comparison of two builds of one tree at different worktree paths. clang-cl derives the
anonymous-namespace hash from the source path; the RTTI type names in .data then have other lengths and every object
after them in .data moves - the RIP-relative displacements into .data in .text and the pointers into .data in .rdata
change. Method: (1) section sizes; (2) .text: every function (from .pdata) that has a differing byte is decoded with
capstone in both binaries; an instruction pair is accepted when the bytes are equal, or when the mnemonic, length and
operand text without the RIP displacement are equal and both RIP targets fall in .data (any shift) or are equal;
(3) .rdata: differing 8-byte aligned qwords are accepted when both are VAs inside .data, differing 4-byte aligned dwords
when both are RVAs inside .data; (4) .pdata equal. Paths f38b -> f38a are replaced before the compare.
usage: cmp_code_f38b.py <f38a exe> <f38b exe>"""
import bisect
import struct
import sys

import capstone

BS = bytes([92])
a = open(sys.argv[1], 'rb').read()
b = open(sys.argv[2], 'rb').read()
b = b.replace(b'f287' + BS + b'f40b2' + BS, b'f287' + BS + b'f40a2' + BS).replace(b'f287/f40b2/', b'f287/f40a2/')


def sections(x):
    pe = struct.unpack_from('<I', x, 0x3c)[0]
    opt = pe + 24
    base = struct.unpack_from('<Q', x, opt + 24)[0]
    nsec = struct.unpack_from('<H', x, pe + 6)[0]
    so = opt + struct.unpack_from('<H', x, pe + 20)[0]
    out = {}
    for k in range(nsec):
        name = x[so + 40 * k:so + 40 * k + 8].rstrip(bytes(1)).decode()
        vs, va, rs, ra = struct.unpack_from('<IIII', x, so + 40 * k + 8)
        out[name] = (va, vs, ra, rs)
    return base, out


base_a, sa = sections(a)
base_b, sb = sections(b)
ok = True
print('image base', hex(base_a), hex(base_b))
for n in sa:
    print('section', n, 'vsize', sa[n][1], sb[n][1], 'rva', hex(sa[n][0]), hex(sb[n][0]))
for n in ('.text', '.rdata', '.pdata'):
    if sa[n][:2] != sb[n][:2] or sa[n][3] != sb[n][3]:  # raw offsets may differ after a resized .data
        print('LAYOUT DIFFERS', n)
        ok = False


def in_data(rva, s):
    va, vs, _, _ = s['.data']
    return va <= rva < va + max(vs, 1)


def sec_bytes(x, s, n):
    va, vs, ra, rs = s[n]
    return x[ra:ra + rs]


# .pdata
pa, pb = sec_bytes(a, sa, '.pdata'), sec_bytes(b, sb, '.pdata')
print('.pdata equal', pa == pb)
ok &= pa == pb
funcs = []
for i in range(0, sa['.pdata'][1] - 11, 12):
    beg, end, _ = struct.unpack_from('<III', pa, i)
    if beg:
        funcs.append((beg, end))
funcs.sort()
# leaf functions have no .pdata entry: the gaps between .pdata functions are decode units too
units = []
prev = sa['.text'][0]
for beg, end in funcs:
    if beg > prev:
        units.append((prev, beg))
    units.append((beg, end))
    prev = max(prev, end)
units.append((prev, sa['.text'][0] + sa['.text'][1]))
print('functions', len(funcs), 'decode units with gaps', len(units))
funcs = units
starts = [f[0] for f in funcs]

# .text
ta, tb = sec_bytes(a, sa, '.text'), sec_bytes(b, sb, '.text')
tva = sa['.text'][0]
CH = 4096
bad_funcs = set()
nodiff_outside = 0
for off in range(0, len(ta), CH):
    if ta[off:off + CH] == tb[off:off + CH]:
        continue
    for j in range(off, min(off + CH, len(ta))):
        if ta[j] != tb[j]:
            rva = tva + j
            k = bisect.bisect_right(starts, rva) - 1
            if k >= 0 and funcs[k][0] <= rva < funcs[k][1]:
                bad_funcs.add(funcs[k])
            else:
                nodiff_outside += 1
print('.text differing functions', len(bad_funcs), 'differing bytes outside any function', nodiff_outside)
ok &= nodiff_outside == 0
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True
acc_eq = acc_rip = 0
rej = []
for beg, end in sorted(bad_funcs):
    ca = ta[beg - tva:end - tva]
    cb = tb[beg - tva:end - tva]
    ia = list(md.disasm(ca, beg))
    ib = list(md.disasm(cb, beg))
    if len(ia) != len(ib) or sum(i.size for i in ia) != len(ca):
        rej.append(('decode', hex(beg), len(ia), len(ib), sum(i.size for i in ia), len(ca)))
        continue
    for x, y in zip(ia, ib):
        if x.bytes == y.bytes:
            acc_eq += 1
            continue
        good = x.mnemonic == y.mnemonic and x.size == y.size
        tx = ty = None
        if good:
            for o in x.operands:
                if o.type == capstone.x86.X86_OP_MEM and o.mem.base == capstone.x86.X86_REG_RIP:
                    tx = x.address + x.size + o.mem.disp
            for o in y.operands:
                if o.type == capstone.x86.X86_OP_MEM and o.mem.base == capstone.x86.X86_REG_RIP:
                    ty = y.address + y.size + o.mem.disp
            good = tx is not None and ty is not None and (tx == ty or (in_data(tx, sa) and in_data(ty, sb)))
            if good:
                # the instruction bytes outside the displacement must be equal
                dpos = x.disp_offset
                good = (x.bytes[:dpos] == y.bytes[:dpos] and x.bytes[dpos + x.disp_size:] == y.bytes[dpos + y.disp_size:])
        if good:
            acc_rip += 1
        else:
            rej.append(('insn', hex(x.address), x.mnemonic, x.op_str, y.op_str))
print('.text instructions in differing functions: equal', acc_eq, 'RIP into .data (accepted)', acc_rip, 'rejected', len(rej))
for r in rej[:20]:
    print('  REJ', r)
ok &= not rej

# .rdata
ra_, rb_ = sec_bytes(a, sa, '.rdata'), sec_bytes(b, sb, '.rdata')
rva0 = sa['.rdata'][0]
q_ok = d_ok = dbg_n = 0
# debug directory (timestamp) and its CodeView record (PDB GUID / age / path): build identity, not code
_pe = struct.unpack_from('<I', a, 0x3c)[0]
_ddir, _dsz = struct.unpack_from('<II', a, _pe + 24 + 112 + 6 * 8)
_ent = [struct.unpack_from('<IIIIHHI', a, 0) for _ in ()]
_off = _ddir - sa['.rdata'][0] + sa['.rdata'][2]
dbg_lo, dbg_hi = _ddir, _ddir + _dsz
for _k in range(_dsz // 28):
    _sz, _rva = struct.unpack_from('<II', a, _off + 28 * _k + 16)
    dbg_lo, dbg_hi = min(dbg_lo, _rva), max(dbg_hi, _rva + _sz)
print('debug directory rva range', hex(dbg_lo), hex(dbg_hi))
r_rej = []
i = 0
diffs = [j for o in range(0, len(ra_), CH) if ra_[o:o + CH] != rb_[o:o + CH]
         for j in range(o, min(o + CH, len(ra_))) if ra_[j] != rb_[j]]
seen = set()
for j in diffs:
    q = j & ~7
    if q in seen:
        continue
    va_ = struct.unpack_from('<Q', ra_, q)[0]
    vb_ = struct.unpack_from('<Q', rb_, q)[0]
    if in_data(va_ - base_a, sa) and in_data(vb_ - base_b, sb):
        seen.add(q)
        q_ok += 1
        continue
    d = j & ~3
    if d in seen:
        continue
    xa = struct.unpack_from('<I', ra_, d)[0]
    xb = struct.unpack_from('<I', rb_, d)[0]
    if in_data(xa, sa) and in_data(xb, sb):
        seen.add(d)
        d_ok += 1
        continue
    seen.add(d)
    if dbg_lo <= rva0 + d < dbg_hi:
        dbg_n += 1
        continue
    r_rej.append((hex(rva0 + d), ra_[d - 16:d + 16], rb_[d - 16:d + 16]))
print('.rdata differing bytes', len(diffs), 'accepted qword VAs into .data', q_ok, 'dword RVAs into .data', d_ok,
      'debug directory / CodeView dwords', dbg_n, 'rejected', len(r_rej))
for r in r_rej[:20]:
    print('  REJ', r)
ok &= not r_rej
print('ALL OK' if ok else 'NOT OK')
