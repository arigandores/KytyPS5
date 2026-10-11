# F47b3 (HPP-817, Red Team): own N4 mutants of the F47a3 classifier on the T1 C-imm program d88770f91d5d003e.
# Mutants are written anew (not the m0-m4 of F47a3); each one names the expected class and the input that must be
# named among the leaves. Read only; ASCII only; exits 3 when the lock exists.
import importlib.util
import os
import struct
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    print('LOCK present - exit 3')
    sys.exit(3)

CLS = 'C:/kyty/KytyPS5/docs/track-f/f47a3/cls_f47a3.py'
spec = importlib.util.spec_from_file_location('cls_f47a3', CLS)
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
a = C.analyse(W, udc=None)
print('program %s words %d class %s leaves %s' % (path.replace(os.sep, '/'), len(W), a['cls'], sorted(a['leaves'])))
for I in a['ins']:
    print('  pc %3d %-6s op %-5s %-24s defs %s srcs %s leaf %s exp %s' % (I.pc, I.fam, str(I.op), I.name, I.defs, I.srcs, I.leaf, I.exp))
site = C.lit_site(a, W)
pc = site.pc
has_lit = (W[pc] & 0x1ff) == 255
LITW = W[pc + 1] if has_lit else None
print('site pc %d fam %s literal %s' % (pc, site.fam, ('0x%08x' % LITW) if has_lit else 'inline'))

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


def sop1(op, sdst, s0, lit=None):
    return [0xBE800000 | (sdst << 16) | (op << 8) | s0] + ([lit] if lit is not None else [])


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


litval = LITW if has_lit else 0x3F800000
cases = []
# x1: scalar select of the literal by SCC from s_cmp on an s_load result (straight program, no branch, no v_cndmask)
cases.append(('x1_s_cselect_on_s_load', smem(0, S0) + [WAIT] + sopc(0x06, S0, 128) + sop2(0x0a, SD, 255, 128, litval)
              + site_src(W, SD), 'SMEM'))
# x2: s_cselect_b64 (op 0x0b) form of x1
cases.append(('x2_s_cselect_b64_on_s_load', smem(0, S0) + [WAIT] + sopc(0x06, S0, 128) + sop2(0x0b, SD, 255, 128, litval)
              + site_src(W, SD), 'SMEM'))
# x3: s_addc_u32 (op 0x04) reads SCC as carry: SD = 0 + 0 + SCC(s_load == 0)
cases.append(('x3_s_addc_scc_on_s_load', smem(0, S0) + [WAIT] + sopc(0x06, S0, 128) + sop2(0x04, SD, 128, 128)
              + site_src(W, SD), 'SMEM'))
# x4: s_cmov_b32 (SOP1 0x05) of a literal under SCC from s_load (control: already modelled, must pass)
cases.append(('x4_s_cmov_on_s_load', smem(0, S0) + [WAIT] + sop1(0x03, SD, 128) + sopc(0x06, S0, 128) + sop1(0x05, SD, 255, litval)
              + site_src(W, SD), 'SMEM'))
# x5: plain SGPR copy chain s_mov_b32 SD, S0 (s_load) -> site
cases.append(('x5_s_mov_chain_s_load', smem(0, S0) + [WAIT] + sop1(0x03, SD, S0) + site_src(W, SD), 'SMEM'))
# x6: VGPR from buffer_load into the site
cases.append(('x6_buffer_load', mubuf_load(VT) + [0xBF8C0000 | 0x3F70] + site_src(W, 256 + VT), 'BUF'))
# x7: image result into the site
cases.append(('x7_image', mimg(VT) + [0xBF8C0000 | 0x3F70] + site_src(W, 256 + VT), 'IMG'))
# x8: exec masked by an s_load_dwordx2 pair before the site (s_and_b64 exec, exec, s[100:101])
cases.append(('x8_exec_and_s_load', smem(1, S0) + [WAIT] + sop2(0x0f, 126, 126, S0) + W, 'SMEM'))
# x9: straight program: s_load + LDS read -> v_add into the site (leaves SMEM + OTHER from LDS, no branch)
cases.append(('x9_straight_lds_plus_s_load', smem(0, S0) + [WAIT] + ds_read(VT) + [0xBF8C0000 | 0xC07F]
              + [(0x03 << 25) | (VT << 17) | (VT << 9) | S0] + site_src(W, 256 + VT), 'SMEM'))
# x10: branch on s_load over nothing harmful, site unchanged: leaves SMEM + OTHER from the live-in VGPR over-approximation
cases.append(('x10_branch_s_load_site_literal', smem(0, S0) + [WAIT] + sopc(0x06, S0, 128) + [0xBF850000 | 0] + W, 'SMEM'))

ok_all = True
for name, words, need in cases:
    r = C.analyse(words, udc=None)
    caught = r['cls'] != 'C-imm' and need in r['leaves']
    print('%-32s class %-12s leaves %-40s control %d need %-5s %s' % (name, r['cls'], ','.join(sorted(r['leaves'])), r['control'], need,
                                                                   'CAUGHT' if caught else 'MISSED'))
print('done')
