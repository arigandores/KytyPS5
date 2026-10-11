# F47b4 (HPP-819, Red Team): own N4 mutants of the F47a4 classifier (cls_f47a4.py, sha256 abccb9ab...) on the T1 C-imm
# program d88770f91d5d003e. Mutants x1-x10 are the ones of F47b3 (own_n4_f47b3.py, written anew there, not m0-m7 of
# the edition); x11-x16 are new here. Each names the input that must be among the leaves. Every case is read at
# udc None (every live-in SGPR is USER) and udc 0 (the user_data_count of d88770f91d5d003e in the catalog), by the
# letter (class) and by the b5 reading (ROADMAP item 723(b): OTHER_BRS read as OTHER_BR).
# Read only; ASCII only; exits 3 when the lock exists. KYTY_F47A4_BREAK is passed through to cls_f47a4.py.
import importlib.util
import os
import struct
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    print('LOCK present - exit 3')
    sys.exit(3)

CLS = 'C:/kyty/KytyPS5/docs/track-f/f47a4/cls_f47a4.py'
spec = importlib.util.spec_from_file_location('cls_f47a4', CLS)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

H = 'd88770f91d5d003e'
path = None
for arm in sorted(os.listdir(C.GCN_ROOT)):
    p = os.path.join(C.GCN_ROOT, arm, 'ps_%s.bin' % H)
    if os.path.exists(p):
        path = p
        break
b = open(path, 'rb').read()
W = list(struct.unpack('<%dI' % (len(b) // 4), b))
a = C.analyse(W, udc=0)
print('break=%s program %s words %d class %s leaves %s' % (C.BREAK or '-', path.replace(os.sep, '/'), len(W), a['cls'],
                                                           sorted(a['leaves'])))
site = C.lit_site(a, W)
pc = site.pc
has_lit = (W[pc] & 0x1ff) == 255
LITW = W[pc + 1] if has_lit else None
exp_regs = [r for J in a['ins'] if J.exp is not None and J.exp[0] == 0 for r in J.exp[1]]
VEXP = exp_regs[0][1]
print('site pc %d fam %s literal %s exported v%d' % (pc, site.fam, ('0x%08x' % LITW) if has_lit else 'inline', VEXP))

S0, S1 = 100, 101          # own scratch SGPRs (pair 100:101)
SD = 102                   # own select destination
VT = 250                   # own scratch VGPR
WAIT = C.S_WAITCNT_LGKM0


def smem(op, sdst):
    return [(0x3d << 26) | (op << 18) | (sdst << 6) | 0, (0 & 0x1fffff) | (125 << 25)]


def sop2(op, sdst, s0, s1, lit=None):
    return [0x80000000 | (op << 23) | (sdst << 16) | (s1 << 8) | s0] + ([lit] if lit is not None else [])


def sopc(op, s0, s1):
    return [0xBF000000 | (op << 16) | (s1 << 8) | s0]


def sopk(op, sdst, simm):
    return [0xB0000000 | (op << 23) | (sdst << 16) | (simm & 0xffff)]


def sop1(op, sdst, s0, lit=None):
    return [0xBE800000 | (sdst << 16) | (op << 8) | s0] + ([lit] if lit is not None else [])


def sopp(op, simm=0):
    return [0xBF800000 | (op << 16) | (simm & 0xffff)]


def v_mov(vd, src):
    return (0x3f << 25) | (vd << 17) | (0x01 << 9) | src


def site_src(words, src):
    m = list(words)
    m[pc] = (m[pc] & ~0x1ff) | src
    if has_lit:
        m[pc + 1] = C.S_NOP
    return m


def mubuf_load(vdata, srsrc_sgpr=0):
    return [(0x38 << 26) | (0x0c << 18), (0 & 0xff) | (vdata << 8) | ((srsrc_sgpr // 4) << 16) | (128 << 24)]


def mimg(vdata):
    return [(0x3c << 26) | (0x1 << 8), (vdata << 8)]


def ds_read(vdst):
    return [(0x36 << 26) | (0x36 << 18), 0 | (vdst << 24)]


def vop3_cndmask(vd, s0, s1, s2):
    # v_cndmask_b32_e64 (VOP3 op 0x101): vd = s2[lane] ? s1 : s0
    return [(0x35 << 26) | (0x101 << 16) | vd, s0 | (s1 << 9) | (s2 << 18)]


litval = LITW if has_lit else 0x3F800000
cases = []
# --- F47b3 x1-x10 (identical words)
cases.append(('x1_s_cselect_on_s_load', smem(0, S0) + [WAIT] + sopc(0x06, S0, 128) + sop2(0x0a, SD, 255, 128, litval)
              + site_src(W, SD), 'SMEM', False))
cases.append(('x2_s_cselect_b64_on_s_load', smem(0, S0) + [WAIT] + sopc(0x06, S0, 128) + sop2(0x0b, SD, 255, 128, litval)
              + site_src(W, SD), 'SMEM', False))
cases.append(('x3_s_addc_scc_on_s_load', smem(0, S0) + [WAIT] + sopc(0x06, S0, 128) + sop2(0x04, SD, 128, 128)
              + site_src(W, SD), 'SMEM', False))
cases.append(('x4_s_cmov_on_s_load', smem(0, S0) + [WAIT] + sop1(0x03, SD, 128) + sopc(0x06, S0, 128) + sop1(0x05, SD, 255, litval)
              + site_src(W, SD), 'SMEM', False))
cases.append(('x5_s_mov_chain_s_load', smem(0, S0) + [WAIT] + sop1(0x03, SD, S0) + site_src(W, SD), 'SMEM', False))
cases.append(('x6_buffer_load', mubuf_load(VT) + [0xBF8C0000 | 0x3F70] + site_src(W, 256 + VT), 'BUF', False))
cases.append(('x7_image', mimg(VT) + [0xBF8C0000 | 0x3F70] + site_src(W, 256 + VT), 'IMG', False))
cases.append(('x8_exec_and_s_load', smem(1, S0) + [WAIT] + sop2(0x0f, 126, 126, S0) + W, 'SMEM', False))
cases.append(('x9_straight_lds_plus_s_load', smem(0, S0) + [WAIT] + ds_read(VT) + [0xBF8C0000 | 0xC07F]
              + [(0x03 << 25) | (VT << 17) | (VT << 9) | S0] + site_src(W, 256 + VT), 'SMEM', False))
cases.append(('x10_branch_s_load_site_literal', smem(0, S0) + [WAIT] + sopc(0x06, S0, 128) + [0xBF850000 | 0] + W, 'SMEM', False))
# --- new
# x11: s_cselect_b64 builds a lane mask from SCC (s_load), v_cndmask_e64 selects between two literals by that mask
SITE_D = (W[pc] >> 17) & 0xff
_m = site_src(W, 256 + VT)
cases.append(('x11_cselect_b64_mask_cndmask', smem(0, S0) + [WAIT] + sopc(0x06, S0, 128) + sop2(0x0b, SD, 193, 128)
              + [v_mov(VT, 242)] + _m[:pc] + vop3_cndmask(SITE_D, 128, 256 + VT, SD) + _m[pc + 1:], 'SMEM', False))
# x12: s_subb_u32 (op 0x05) borrow = SCC from s_cmp on s_load
cases.append(('x12_s_subb_scc_on_s_load', smem(0, S0) + [WAIT] + sopc(0x06, S0, 128) + sop2(0x05, SD, 128, 128)
              + site_src(W, SD), 'SMEM', False))
# x13: SCC as a source operand (253) of the site itself: v_mov_b32 v, scc after s_cmp on s_load
cases.append(('x13_scc_operand_into_site', smem(0, S0) + [WAIT] + sopc(0x06, S0, 128) + site_src(W, 253), 'SMEM', False))
# x14: s_cmpk_eq_u32 (SOPK 0x0b) on s_load writes SCC, then s_cselect_b32 picks the literal
cases.append(('x14_cmpk_then_cselect', smem(0, S0) + [WAIT] + sopk(0x0b, S0, 0) + sop2(0x0a, SD, 255, 128, litval)
              + site_src(W, SD), 'SMEM', False))
# x15: SCC produced by an SOP2 (s_and_b32 SD, s_load, 1 writes SCC), then s_cselect_b32 picks the literal
cases.append(('x15_sop2_scc_then_cselect', smem(0, S0) + [WAIT] + sop2(0x0e, 103, S0, 129) + sop2(0x0a, SD, 255, 128, litval)
              + site_src(W, SD), 'SMEM', False))
# x16: branch over the only definition of the exported VGPR: on the taken path the live-in VGPR (a real PS input)
# reaches the export; must not be C-imm (V4 boundary [I] of edition 4 s3.1 - class only toward (v)(5))
cases.append(('x16_branch_over_only_def', W[:pc] + smem(0, S0) + [WAIT] + sopc(0x06, S0, 128) + sopp(0x05, 2 if has_lit else 1)
              + W[pc:], 'SMEM', False))

n_bad = 0
for name, words, need, want_cimm in cases:
    for udc in (None, 0):
        r = C.analyse(words, udc=udc)
        caught = (r['cls'] == 'C-imm') if want_cimm else (r['cls'] != 'C-imm' and need in r['leaves'])
        caught5 = (r['b5'] == 'C-imm') if want_cimm else (r['b5'] != 'C-imm' and need in r['leaves'])
        n_bad += (not caught) + (not caught5)
        print('%-32s udc %-4s class %-12s v4 %d b5 %-12s leaves %-46s need %-4s letter %s b5 %s' % (
            name, udc, r['cls'], r['v4'], r['b5'], ','.join(sorted(r['leaves'])), need, 'CAUGHT' if caught else 'MISSED',
            'CAUGHT' if caught5 else 'MISSED'))
r9 = C.analyse(cases[8][1], udc=0)['leaves']
r10 = C.analyse(cases[9][1], udc=0)['leaves']
r10n = C.analyse(cases[9][1], udc=None)['leaves']
print('x9 vs x10 leaves differ udc0 %s udcNone %s; x9 OTHER %s OTHER_BR %s; x10 OTHER %s OTHER_BR %s' % (
    r9 != r10, r9 != r10n, 'OTHER' in r9, 'OTHER_BR' in r9, 'OTHER' in r10, 'OTHER_BR' in r10))
print('missed %d' % n_bad)
print('done')
