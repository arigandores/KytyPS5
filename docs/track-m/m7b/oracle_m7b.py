"""Track M, M7b (HPP-853, ROADMAP s122 items 767(g)(1)-(2), 773(g)(3)): independent oracle of the T306 repair.
Own code (imports nothing from M5a/M5b/M7a scripts):
  1. finds the words of each program in eboot.bin itself (byte search of the program file; count of occurrences);
     writes the words cut from eboot.bin to <out>/eboot_words/<hash16>.bin (input of the test TestMWave1T306EbootPrograms);
  2. own linear GFX10 length decoder: every MIMG IMAGE_SAMPLE*_O / GATHER4*_O; the VGPR of address dword 0; the last
     writer of that VGPR before the sample (linear back scan) - a v_mov_b32 literal / inline constant, or 'other';
     the writes of EXEC between the writer and the sample (lane mask may differ);
  3. the pairs (x, y) of the signed six-bit fields;
  4. own SPIR-V reader: every image instruction of each given module with its image operands - ConstOffset value,
     Offset / ConstOffsets presence - in function order; compared with the GCN pairs in pc order.
Usage: python oracle_m7b.py <out_dir> [<name>=<module.spv> ...]   Exit 3 under the lock."""
import os
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
EBOOT = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/eboot.bin'
PROGRAMS = [
    ('5a34b303576ee324', 'C:/kyty/s288/s4/gcn/g_1/ps_5a34b303576ee324.bin'),
    ('f47c0c097c598a36', 'C:/kyty/s288/s4/gcn/g_1/ps_f47c0c097c598a36.bin'),
    ('7b4078750f32db50', 'C:/kyty/m657/m7a/cs7b/7b4078750f32db50.bin'),
    ('b912bcf29000558d', 'C:/kyty/m657/m7a/cs7b/b912bcf29000558d.bin'),
]
# GFX10 MIMG opcodes with a texel offset (address dword 0): IMAGE_SAMPLE_*_O 0x30-0x3f, IMAGE_GATHER4_*_O 0x50-0x5f,
# sample/gather with derivative-16 / O forms of GFX10.3 (0xa2-0xa7 region) are listed by name if met.
OFFSET_OPS = set(range(0x30, 0x40)) | set(range(0x50, 0x60)) | {0x5e, 0x5f, 0xa3, 0xa7, 0xab, 0xaf, 0xeb, 0xef}


def u32(b, i):
    return int.from_bytes(b[4 * i:4 * i + 4], 'little')


def vsrc_lit(s):
    return s == 255


def inst_size(w, w1):
    """dwords of the instruction at w (own table, GFX10)"""
    if (w >> 23) == 0x17D or (w >> 23) == 0x17E:  # SOP1 / SOPC
        return 1 + (1 if (w & 0xff) == 255 or ((w >> 23) == 0x17E and ((w >> 8) & 0xff) == 255) else 0), 'S'
    if (w >> 23) == 0x17F:  # SOPP
        return 1, 'SOPP'
    if (w >> 28) == 0xB:  # SOPK
        return (2 if ((w >> 23) & 0x1f) == 0x15 else 1), 'S'
    if (w >> 30) == 2:  # SOP2
        return 1 + (1 if (w & 0xff) == 255 or ((w >> 8) & 0xff) == 255 else 0), 'S'
    if (w >> 25) == 0x3F:  # VOP1
        return 1 + (1 if (w & 0x1ff) in (255, 0xF9, 0xFA, 0xE9, 0xEA) else 0), 'VOP1'
    if (w >> 25) == 0x3E:  # VOPC
        return 1 + (1 if (w & 0x1ff) in (255, 0xF9, 0xFA, 0xE9, 0xEA) else 0), 'VOPC'
    if (w >> 31) == 0:  # VOP2
        op = (w >> 25) & 0x3f
        n = 1 + (1 if (w & 0x1ff) in (255, 0xF9, 0xFA, 0xE9, 0xEA) else 0)
        if op in (0x20, 0x21, 0x2c, 0x2d, 0x37, 0x38) and n == 1:  # madmk/madak/fmamk/fmaak + f16 forms: K literal
            n = 2
        return n, 'VOP2'
    top6 = w >> 26
    if top6 == 0x35:  # VOP3 / VOP3B
        s = [w1 & 0x1ff, (w1 >> 9) & 0x1ff, (w1 >> 18) & 0x1ff]
        return 2 + (1 if 255 in s else 0), 'VOP3'
    if top6 == 0x33:  # VOP3P
        s = [w1 & 0x1ff, (w1 >> 9) & 0x1ff, (w1 >> 18) & 0x1ff]
        return 2 + (1 if 255 in s else 0), 'VOP3P'
    if top6 == 0x3C:  # MIMG (NSA: extra address dwords)
        nsa = (w >> 1) & 3
        return 2 + nsa, 'MIMG'
    if top6 in (0x38, 0x3A, 0x32, 0x3D, 0x36, 0x37, 0x3E, 0x3F, 0x31, 0x34, 0x3B):  # MUBUF MTBUF VINTRP? SMEM DS FLAT EXP
        if top6 == 0x32:  # VINTRP (one dword)
            return 1, 'VINTRP'
        return 2, {0x38: 'MUBUF', 0x3A: 'MTBUF', 0x3D: 'SMEM', 0x36: 'DS', 0x37: 'FLAT', 0x3E: 'EXP'}.get(top6, 'X%x' % top6)
    return 1, '?%08x' % w


def decode(words):
    pc = 0
    out = []
    while pc < len(words):
        w = words[pc]
        w1 = words[pc + 1] if pc + 1 < len(words) else 0
        n, fam = inst_size(w, w1)
        out.append((pc, fam, words[pc:pc + n]))
        if fam == 'SOPP' and ((w >> 16) & 0x7f) == 1:  # s_endpgm
            break
        pc += n
    return out


def inline_int(s):
    if 128 <= s <= 192:
        return s - 128
    if 193 <= s <= 208:
        return -(s - 192)
    return None


def vgpr_writer(insts, k, v):
    """last instruction before index k whose VGPR destination is v; returns (pc, text, literal or None)"""
    for j in range(k - 1, -1, -1):
        pc, fam, ws = insts[j]
        w = ws[0]
        if fam == 'VOP1' and ((w >> 17) & 0xff) == v:
            op = (w >> 9) & 0xff
            src = w & 0x1ff
            if op == 1:  # v_mov_b32
                if src == 255:
                    return pc, 'v_mov_b32 v%d, 0x%08x' % (v, ws[1]), ws[1]
                if inline_int(src) is not None:
                    return pc, 'v_mov_b32 v%d, %d' % (v, inline_int(src)), inline_int(src) & 0xffffffff
            return pc, 'VOP1 op 0x%x src 0x%x' % (op, src), None
        if fam == 'VOP2' and ((w >> 17) & 0xff) == v:
            return pc, 'VOP2 op 0x%x' % ((w >> 25) & 0x3f), None
        if fam in ('VOP3', 'VOP3P') and (w & 0xff) == v:
            op = (w >> 16) & 0x3ff
            if fam == 'VOP3' and 0 <= op < 0x100 and ((op >> 7) == 0):  # VOPC promoted: dst is SGPR
                continue
            return pc, '%s op 0x%x' % (fam, op), None
        if fam in ('MIMG', 'MUBUF', 'MTBUF', 'FLAT', 'DS') and fam != 'DS':
            # loads write vdata (word1 bits 15:8); count it as a writer of that range start
            vdata = (ws[1] >> 8) & 0xff
            if fam == 'MIMG':
                dmask = (w >> 8) & 0xf
                cnt = max(1, bin(dmask).count('1'))
            else:
                cnt = 4
            if vdata <= v < vdata + cnt and fam != 'MIMG':
                return pc, '%s load vdata v%d' % (fam, vdata), None
            if fam == 'MIMG' and vdata <= v < vdata + cnt:
                return pc, 'MIMG vdata v%d' % vdata, None
        if fam == 'VINTRP' and ((w >> 18) & 0xff) == v:
            return pc, 'VINTRP', None
    return None, 'no writer', None


def exec_writes(insts, a, b):
    """instructions strictly between indices a and b that may write EXEC"""
    res = []
    for j in range(a + 1, b):
        pc, fam, ws = insts[j]
        w = ws[0]
        if fam == 'S':
            if (w >> 23) == 0x17D and ((w >> 16) & 0x7f) in (126, 127):
                res.append((pc, 'SOP1 op 0x%x -> exec' % ((w >> 8) & 0xff)))
            elif (w >> 23) == 0x17D and ((w >> 8) & 0xff) in set(range(0x24, 0x2c)) | set(range(0x37, 0x3f)):
                res.append((pc, 'SOP1 saveexec op 0x%x' % ((w >> 8) & 0xff)))
            elif (w >> 30) == 2 and ((w >> 16) & 0x7f) in (126, 127):
                res.append((pc, 'SOP2 op 0x%x -> exec' % ((w >> 23) & 0x7f)))
        if fam == 'VOPC' and ((w >> 17) & 0xff) in range(0x10, 0x20) or (fam == 'VOPC' and ((w >> 17) & 0xff) >= 0x90 and (((w >> 17) & 0xff) & 0x10)):
            res.append((pc, 'VOPC op 0x%x (cmpx?)' % ((w >> 17) & 0xff)))
    return res


def six(v):
    v &= 0x3f
    return v - 64 if v & 0x20 else v


def gcn_oracle(words):
    insts = decode(words)
    res = []
    for k, (pc, fam, ws) in enumerate(insts):
        if fam != 'MIMG':
            continue
        op = ((ws[0] >> 18) & 0x7f) | ((ws[0] & 1) << 7)
        if op not in OFFSET_OPS:
            continue
        vaddr0 = ws[1] & 0xff
        wpc, text, lit = vgpr_writer(insts, k, vaddr0)
        wk = next((i for i, x in enumerate(insts) if x[0] == wpc), -1) if wpc is not None else -1
        ex = exec_writes(insts, wk, k) if wk >= 0 else []
        pair = (six(lit), six(lit >> 8), six(lit >> 16)) if lit is not None else None
        res.append(dict(pc=pc, op=op, vaddr0=vaddr0, writer_pc=wpc, writer=text, literal=lit, pair=pair,
                        exec_between=ex))
    first_exec = [(pc, fam, ['%08x' % x for x in ws]) for (pc, fam, ws) in insts[:16]
                  if fam == 'S' and (((ws[0] >> 23) == 0x17D and ((ws[0] >> 16) & 0x7f) == 126))]
    return res, len(insts), first_exec


# ---------------- SPIR-V
IMG_OPS = {87: ('SampleImplicitLod', 5), 88: ('SampleExplicitLod', 5), 89: ('SampleDrefImplicitLod', 6),
           90: ('SampleDrefExplicitLod', 6), 91: ('SampleProjImplicitLod', 5), 92: ('SampleProjExplicitLod', 5),
           93: ('SampleProjDrefImplicitLod', 6), 94: ('SampleProjDrefExplicitLod', 6), 95: ('Fetch', 5),
           96: ('Gather', 6), 97: ('DrefGather', 6), 98: ('Read', 5),
           305: ('SparseSampleImplicitLod', 5), 306: ('SparseSampleExplicitLod', 5), 307: ('SparseSampleDrefImplicitLod', 6),
           308: ('SparseSampleDrefExplicitLod', 6), 311: ('SparseFetch', 5), 312: ('SparseGather', 6),
           313: ('SparseDrefGather', 6)}


def spirv_images(path):
    b = open(path, 'rb').read()
    n = len(b) // 4
    words = [u32(b, i) for i in range(n)]
    assert words[0] == 0x07230203, 'not SPIR-V'
    consts = {}
    comps = {}
    found = []
    i = 5
    while i < n:
        cnt = words[i] >> 16
        op = words[i] & 0xffff
        if cnt == 0:
            raise SystemExit('bad SPIR-V ' + path)
        if op == 43:
            consts[words[i + 2]] = words[i + 3] if cnt >= 4 else None
        elif op == 44:
            comps[words[i + 2]] = words[i + 3:i + cnt]
        elif op in IMG_OPS:
            name, mpos = IMG_OPS[op]
            entry = {'op': name, 'id': words[i + 2], 'co': None, 'offset': False, 'offsets': False}
            if cnt > mpos:
                mask = words[i + mpos]
                at = i + mpos + 1
                for bit, nops in ((0x1, 1), (0x2, 1), (0x4, 2), (0x8, 1), (0x10, 1), (0x20, 1)):
                    if mask & bit:
                        if bit == 0x8:
                            entry['co'] = words[at]
                        if bit == 0x10:
                            entry['offset'] = True
                        if bit == 0x20:
                            entry['offsets'] = True
                        at += nops
            found.append(entry)
        i += cnt

    def val(cid):
        if cid in consts:
            v = consts[cid]
            return (v - (1 << 32) if v & 0x80000000 else v,)
        if cid in comps:
            return tuple(val(c)[0] for c in comps[cid])
        return None
    for e in found:
        e['co_val'] = val(e['co']) if e['co'] is not None else None
    return found


def main():
    if os.path.exists(LOCK):
        print('LOCK present - exit 3')
        return 3
    out = sys.argv[1]
    os.makedirs(out + '/eboot_words', exist_ok=True)
    eb = open(EBOOT, 'rb').read()
    print('eboot.bin bytes', len(eb))
    oracle = {}
    for name, path in PROGRAMS:
        prog = open(path, 'rb').read()
        hits = []
        start = 0
        while True:
            at = eb.find(prog, start)
            if at < 0:
                break
            hits.append(at)
            start = at + 1
        print('program %s file %s dwords %d: found in eboot.bin at %s' % (name, path, len(prog) // 4,
                                                                          ['0x%x' % h for h in hits]))
        if not hits:
            print('FAIL: words not in eboot.bin')
            continue
        cut = eb[hits[0]:hits[0] + len(prog)]
        open('%s/eboot_words/%s.bin' % (out, name), 'wb').write(cut)
        words = [u32(cut, i) for i in range(len(cut) // 4)]
        res, ninst, first_exec = gcn_oracle(words)
        print('  instructions %d, early writes of exec %s' % (ninst, first_exec))
        oracle[name] = res
        for r in res:
            print('  pc %3d op 0x%02x vaddr0 v%d writer pc %s %-28s pair %s exec-between %s' % (
                r['pc'], r['op'], r['vaddr0'], r['writer_pc'], r['writer'],
                r['pair'][:2] if r['pair'] else None, r['exec_between']))
    for arg in sys.argv[2:]:
        name, spv = arg.split('=', 1)
        imgs = spirv_images(spv)
        with_co = [e for e in imgs if e['co'] is not None]
        print('SPIR-V %s %s: image ops %d, ConstOffset %d, Offset %d, ConstOffsets %d' % (
            name, spv, len(imgs), len(with_co), sum(e['offset'] for e in imgs), sum(e['offsets'] for e in imgs)))
        print('  ConstOffset values in function order:', [e['co_val'] for e in with_co])
        key = name.split(':')[0]
        if key in oracle:
            want = [r['pair'][:2] for r in oracle[key]]
            got = [e['co_val'][:2] if e['co_val'] else None for e in with_co]
            print('  GCN pairs in pc order       :', want)
            print('  order match: %s; multiset match: %s; dedup-adjacent match: %s' % (
                got == want, sorted(map(str, got)) == sorted(map(str, want)),
                [g for i, g in enumerate(got) if i == 0 or g != got[i - 1]] == want))
    return 0


if __name__ == '__main__':
    sys.exit(main())
