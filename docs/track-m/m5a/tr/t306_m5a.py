"""M5a (HPP-845): T306 repair reachability (ROADMAP p.762(b),(g)). For every image_sample_*_o of the 4 eboot programs that
carry one (tr_m5a.out.txt), print: stage hints (VINTRP / EXP present -> pixel or vertex; neither -> compute), the
offset VGPR (first address VGPR: NSA word2 byte 0 when NSA dwords > 0, else word1 bits[7:0]; RDNA2 MIMG [I]), the last
linear writer of that VGPR before the sample (VOP1/VOP2/VOP3 vdst; MIMG/MUBUF/DS/FLAT loads also counted), every write of
EXEC (sdst 126/127 of SOP1/SOP2/SOPK, VOPC v_cmpx*) between program start and the sample, and whether an EXEC write lies
between the offset writer and the sample. The hole of p.762(b) needs: the offset written under a partial mask A and the
sample issued under another mask that the translator folds to a constant (non-pixel initial exec = true, or an EXEC
literal such as s_mov_b64 exec, -1). Read-only; refuses to run under C:/kyty/SEALED_RUN.lock.
Usage: python t306_m5a.py > t306_m5a.out.txt"""
import importlib.util, os, struct, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
spec = importlib.util.spec_from_file_location('g', 'C:/kyty/KytyPS5/docs/track-f/f23a/gcn_f23a.py')
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
D = 'C:/kyty/f287/f23a/eboot_text/'
PROGS = ['5a34b303576ee324', 'f47c0c097c598a36', '7b4078750f32db50', 'b912bcf29000558d']
SAMPLE_O = set(range(0x30, 0x40)) | {0x6c, 0x6d, 0x6e, 0x6f}


def vgpr_dst(fam, op, words, pc):
    w = words[pc]
    if fam in ('VOP1', 'VOP2'):
        if fam == 'VOP1' and op == 0x02:   # v_readfirstlane writes an SGPR
            return None
        return (w >> 17) & 0xff
    if fam == 'VOP3':
        if op <= 0xff:                      # VOPC in VOP3 writes an SGPR
            return None
        return w & 0xff
    if fam == 'VOP3P':
        return w & 0xff
    if fam == 'VINTRP':
        return (w >> 18) & 0xff
    if fam in ('MUBUF', 'MTBUF'):
        return (words[pc + 1] >> 8) & 0xff
    if fam == 'MIMG':
        return (words[pc + 1] >> 8) & 0xff
    if fam == 'DS':
        return (words[pc + 1] >> 24) & 0xff
    if fam == 'FLAT':
        return (words[pc + 1] >> 24) & 0xff
    return None


def exec_write(fam, op, words, pc):
    w = words[pc]
    if fam in ('SOP1', 'SOP2', 'SOPK'):
        sd = (w >> 16) & 0x7f
        if sd in (126, 127):
            src = w & 0xff
            lit = words[pc + 1] if src == 255 else None
            return 'exec<-%s src=%d%s' % (fam + '_0x%x' % op, src, (' lit=%08x' % lit) if lit is not None else '')
    if fam == 'VOPC' and g.is_cmpx(op):
        return 'v_cmpx (partial)'
    if fam == 'VOP3' and op <= 0xff and g.is_cmpx(op):
        return 'v_cmpx_e64 (partial)'
    return None


total = 0
for h in PROGS:
    b = open(D + h + '.bin', 'rb').read()
    words = list(struct.unpack_from('<%dI' % (len(b) // 4), b, 0))
    ins, st = g.walk(words)
    fams = set(x[1] for x in ins)
    stage = 'pixel-or-vertex (VINTRP)' if 'VINTRP' in fams else ('has EXP' if 'EXP' in fams else 'compute-like (no VINTRP, no EXP)')
    print('=== %s walk=%s words=%d stage hint: %s' % (h, st, len(words), stage))
    execs = []
    for idx, (pc, fam, op, size, ex) in enumerate(ins):
        e = exec_write(fam, op, words, pc)
        if e:
            execs.append((pc, e))
        if fam == 'MIMG' and op in SAMPLE_O:
            total += 1
            w0, w1 = words[pc], words[pc + 1]
            nsa = (w0 >> 1) & 3
            # address 0 (= the offset of *_O) is word1 bits[7:0] with or without NSA; NSA dwords carry addresses 1.. (RDNA2 [I])
            off_v = w1 & 0xff
            writer = None
            for k in range(idx - 1, -1, -1):
                p2, f2, o2, s2, e2 = ins[k]
                if vgpr_dst(f2, o2, words, p2) == off_v:
                    writer = ins[k]
                    break
            if writer:
                wp = writer[0]
                raw = ' '.join('%08x' % words[wp + j] for j in range(writer[3]))
                wname = g.name_of(writer[1], writer[2]) if writer[1].startswith('VOP') else writer[1]
                between = [x for x in execs if wp < x[0] < pc]
                before = [x for x in execs if x[0] < wp]
                print('  sample pc=%d op=0x%02x nsa=%d offset v%d <- pc=%d %s %s | exec writes before writer: %s | between writer and sample: %s'
                      % (pc, op, nsa, off_v, wp, wname, raw, before[-3:], between))
            else:
                print('  sample pc=%d op=0x%02x offset v%d <- NO WRITER (input VGPR)' % (pc, op, off_v))
print('samples', total)
print('DONE t306_m5a')
