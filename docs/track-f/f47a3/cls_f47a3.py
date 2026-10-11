# F47a3 (HPP-816, ROADMAP s122 item 718(g)(1)-(5)): own classifier of the colour export of a pixel program (RDNA2
# words) and the negative control N4 of the classifier. Read only; ASCII only; exits 3 when C:/kyty/SEALED_RUN.lock
# exists. Instruction lengths and families - walk() of docs/track-f/f23a/gcn_f23a.py (F23a, calibrated 331 of 331);
# operand fields are decoded here anew (RDNA2 encodings [I]).
#
# Class of the value exported to MRT<t> (EXP target t, all enabled channels together):
#   leaves of the backward slice of the exported VGPRs, data AND control:
#     LIT     literal word (src 255, VOP2 MADMK/MADAK K, SOPK simm16) or inline constant (128-208, 240-248), NULL (125)
#     USER    live-in SGPR below user_data_count (unknown count: every live-in SGPR)        -> C-buf
#     SMEM    s_load / s_buffer_load result                                                -> C-buf
#     BUF     MUBUF / MTBUF / FLAT / GLOBAL result                                         -> C-buf
#     INTERP  VINTRP / v_interp_*_f16 (vertex attribute)                                   -> C-buf
#     IMG     MIMG result                                                                  -> T
#     VID     (stage vs only) live-in VGPR = vertex / instance index of the draw packet            -> C-buf
#     COV     live-in EXEC (coverage at wave start; checked by the blend/coverage member)  -> neutral
#     OTHER   live-in VGPR (barycentrics, FragCoord), live-in SGPR above user data, LDS, lds_direct, TTMP, M0,
#             apertures, s_getpc / s_getreg / s_memtime, unknown encodings                -> "undetermined"
#   class: C-imm iff leaves <= {LIT, COV}; else T if IMG (every other input of the set is printed and also needs the
#   member M2); else "undetermined" if OTHER; else C-buf.
# Reaching definitions: straight-line program (no conditional branch, no backward branch, no EXEC writer) - the last
# certain definition of the register before the use (exact; over-approximated extra registers of a multi-register
# destination are weak and do not end the search), live-in when there is none; otherwise every earlier definition AND
# the live-in value (and every later one when a backward branch exists). SCC / VCC / EXEC / M0 always: every
# definition anywhere (a wrongly listed SCC writer cannot hide the true one), the live-in value only when no
# definition precedes the use in program order (the start value of SCC / VCC is not an input of the emulator).
# Control dependence (item 718(g)(1)): with any conditional branch or EXEC writer, the conditions (SCC for
# s_cbranch_scc*, VCC for s_cbranch_vcc*, EXEC for s_cbranch_exec* and every EXEC writer's sources) are added to the
# slice; the condition of v_cndmask (VCC or src2) is a data source.
#
# Usage:
#   python cls_f47a3.py prog <gcn .bin> [--udc N] [--mrt T] [--stage vs]  class of one export (VS position: --mrt 12 --stage vs)
#   python cls_f47a3.py n4 [--commit C] [--out FILE]               N4 offline on the T1 corpus (PS dumps)
#   python cls_f47a3.py n4prog <gcn .bin> [--udc N]                N4 on one program (F47e: D_b)
#   python cls_f47a3.py fixtures                                   synthetic programs with known classes
import collections
import hashlib
import importlib.util
import os
import re
import struct
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    print('LOCK present - exit 3')
    sys.exit(3)

GCN_F23A = 'C:/kyty/KytyPS5/docs/track-f/f23a/gcn_f23a.py'
_spec = importlib.util.spec_from_file_location('gcn_f23a', GCN_F23A)
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

GCN_ROOT = 'C:/kyty/s288/s4/gcn'
CATALOG = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19'

CBUF = {'USER', 'SMEM', 'BUF', 'INTERP', 'VID'}
NEUTRAL = {'LIT', 'COV'}


# ---------------------------------------------------------------- operands
def opnd(code, nxt=None):
    """9-bit source operand -> ('reg', name) | ('leaf', LEAF). nxt = following word for SDWA/DPP."""
    if code >= 256:
        return ('reg', ('v', code - 256))
    if code <= 105:
        return ('reg', ('s', code))
    if code in (106, 107):
        return ('reg', 'vcc')
    if code in (126, 127):
        return ('reg', 'exec')
    if code == 124:
        return ('reg', 'm0')
    if code == 125 or 128 <= code <= 208 or 240 <= code <= 248 or code == 255:
        return ('leaf', 'LIT')
    if code == 251:
        return ('reg', 'vcc')
    if code == 252:
        return ('reg', 'exec')
    if code == 253:
        return ('reg', 'scc')
    return ('leaf', 'OTHER')  # 108-123 TTMP, 235-239 apertures, 254 lds_direct, other


def vsrc0(w, words, pc):
    """src0 of VOP1/VOP2/VOPC including SDWA (0xf9) / DPP (0xfa, 0xe9, 0xea): the real source is in the next word."""
    s0 = w & 0x1ff
    if s0 in (0xf9, 0xfa, 0xe9, 0xea):
        x = words[pc + 1]
        if s0 == 0xf9 and (x >> 23) & 1:
            return [opnd(x & 0xff)]
        return [opnd(256 + (x & 0xff))]
    return [opnd(s0)]


WIDE_DST = re.compile(r'^(v_(add|mul|min|max|ldexp|fma|div_fixup|div_fmas|div_scale|trig_preop)_f64|v_(trunc|ceil|rndne|floor|'
                      r'fract|rcp|rsq|sqrt|frexp_mant)_f64|v_cvt_f64_\w+|v_(lshlrev|lshrrev|ashrrev)_[bi]64|v_mad_[ui]64_[ui]32)')


def vregs(base, n):
    return [('v', base + i) for i in range(n)]


def sregs(base, n):
    out = []
    for i in range(n):
        c = base + i
        r = opnd(c)
        if r[0] == 'reg':
            out.append(r[1])
    return out


class Ins:
    __slots__ = ('pc', 'fam', 'op', 'name', 'defs', 'srcs', 'leaf', 'kind', 'cond', 'target', 'exp', 'weak')

    def __init__(self, pc, fam, op, name):
        self.pc, self.fam, self.op, self.name = pc, fam, op, name
        self.defs, self.srcs, self.leaf, self.kind, self.cond, self.target, self.exp = [], [], None, None, None, None, None
        self.weak = set()


SMEM_COUNT = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 8: 1, 9: 2, 10: 4, 11: 8, 12: 16}
SOPK_CMP = set(range(3, 15))
SCC_SOP1_NO = {0x03, 0x04, 0x05, 0x06}  # s_mov_b32/b64, s_cmov_b32/b64 do not write SCC (cmov reads it)


def decode(words):
    instrs, status = G.walk(words)
    out = []
    for (pc, fam, op, size, ex) in instrs:
        w = words[pc]
        I = Ins(pc, fam, op, G.name_of(fam, op) if fam in ('VOP1', 'VOP2', 'VOPC', 'VOP3', 'VOP3P') else '%s_%s' % (fam, op))
        if fam == 'VOP1':
            I.defs = [('v', (w >> 17) & 0xff)]
            I.srcs = vsrc0(w, words, pc)
            if op == 0x02:  # v_readfirstlane_b32 -> SGPR
                I.defs = sregs((w >> 17) & 0xff, 1)
            if I.name in ('v_movreld_b32', 'v_movrels_b32', 'v_movrelsd_b32', 'v_movrelsd_2_b32', 'v_swap_b32', 'v_swaprel_b32'):
                I.srcs.append(('leaf', 'OTHER'))
            if WIDE_DST.match(I.name):
                I.defs = vregs((w >> 17) & 0xff, 2)
        elif fam == 'VOP2':
            d = (w >> 17) & 0xff
            I.defs = [('v', d)]
            I.srcs = vsrc0(w, words, pc) + [opnd(256 + ((w >> 9) & 0xff))]
            if op == 0x01 or op in (0x28, 0x29, 0x2a):  # v_cndmask_b32 condition / carry-in
                I.srcs.append(('reg', 'vcc'))
            if op in (0x28, 0x29, 0x2a):
                I.defs.append('vcc')
            if op in (0x06, 0x1f, 0x2b, 0x36, 0x3c):  # accumulators read their destination
                I.srcs.append(('reg', ('v', d)))
            if op in (0x20, 0x21, 0x2c, 0x2d, 0x37, 0x38):
                I.srcs.append(('leaf', 'LIT'))
        elif fam == 'VOPC':
            I.srcs = vsrc0(w, words, pc) + [opnd(256 + ((w >> 9) & 0xff))]
            I.defs = ['exec'] if G.is_cmpx(op) else ['vcc']
        elif fam in ('VOP3', 'VOP3P'):
            w1 = words[pc + 1]
            s0, s1, s2 = w1 & 0x1ff, (w1 >> 9) & 0x1ff, (w1 >> 18) & 0x1ff
            vd = w & 0xff
            if fam == 'VOP3' and op <= 0xff:  # VOPC in VOP3: SGPR destination
                I.srcs = [opnd(s0), opnd(s1)]
                I.defs = sregs(vd, 2) + (['exec'] if G.is_cmpx(op) else [])
            elif fam == 'VOP3' and op in (0x342, 0x343, 0x35a):
                I.defs = [('v', vd)]
                I.leaf = 'INTERP'
            elif fam == 'VOP3' and 0x180 <= op <= 0x1ff:
                I.defs = vregs(vd, 2) if WIDE_DST.match(I.name) else [('v', vd)]
                I.srcs = [opnd(s0)]
            elif fam == 'VOP3' and 0x100 <= op <= 0x13f:
                I.defs = [('v', vd)]
                I.srcs = [opnd(s0), opnd(s1)]
                if op - 0x100 in (0x01, 0x28, 0x29, 0x2a):  # cndmask condition / carry-in in src2
                    I.srcs.append(opnd(s2))
                if op - 0x100 in (0x28, 0x29, 0x2a):
                    I.defs += sregs((w >> 8) & 0x7f, 2)
                if op - 0x100 in (0x06, 0x1f, 0x2b, 0x36, 0x3c):
                    I.srcs.append(('reg', ('v', vd)))
            else:
                I.defs = vregs(vd, 2) if WIDE_DST.match(I.name) else [('v', vd)]
                I.srcs = [opnd(s0), opnd(s1), opnd(s2)]  # unused src2 adds a spurious source: over-approximation
                if fam == 'VOP3' and op in (0x30f, 0x310, 0x319, 0x16d, 0x16e, 0x176, 0x177):
                    I.defs += sregs((w >> 8) & 0x7f, 2)
                if fam == 'VOP3' and op == 0x360:  # v_readlane_b32 -> SGPR
                    I.defs = sregs(vd, 1)
                if fam == 'VOP3' and op in (0x377, 0x378):
                    I.srcs.append(('leaf', 'OTHER'))
            if size == 3:
                I.srcs.append(('leaf', 'LIT'))
        elif fam == 'VINTRP':
            I.defs = [('v', (w >> 18) & 0xff)]
            I.leaf = 'INTERP'
        elif fam == 'SOP2':
            I.defs = sregs((w >> 16) & 0x7f, 2) + ['scc']
            I.srcs = [opnd(w & 0xff), opnd((w >> 8) & 0xff), opnd((w & 0xff) + 1 if (w & 0xff) < 105 else 125),
                      opnd(((w >> 8) & 0xff) + 1 if ((w >> 8) & 0xff) < 105 else 125)]
            if op in (0x30, 0x31):  # s_cselect reads SCC
                I.srcs.append(('reg', 'scc'))
        elif fam == 'SOPK':
            sd = (w >> 16) & 0x7f
            if op in SOPK_CMP:
                I.defs = ['scc']
                I.srcs = [opnd(sd), ('leaf', 'LIT')]
            elif op == 0x00:
                I.defs = sregs(sd, 1)
                I.srcs = [('leaf', 'LIT')]
            elif op in (0x02, 0x0f, 0x10):  # cmovk / addk / mulk read the destination
                I.defs = sregs(sd, 1) + (['scc'] if op == 0x0f else [])
                I.srcs = [opnd(sd), ('leaf', 'LIT')] + ([('reg', 'scc')] if op == 0x02 else [])
            else:
                I.defs = sregs(sd, 1)
                I.srcs = [('leaf', 'OTHER')]
        elif fam == 'SOP1':
            sd = (w >> 16) & 0x7f
            s0 = w & 0xff
            I.defs = sregs(sd, 2) + ([] if op in SCC_SOP1_NO else ['scc'])
            I.srcs = [opnd(s0), opnd(s0 + 1 if s0 < 105 else 125)]
            if op in (0x05, 0x06):
                I.srcs.append(('reg', 'scc'))
            if op in G.SAVEEXEC_SOP1:
                I.defs.append('exec')
                I.srcs.append(('reg', 'exec'))
            if op in (0x1f, 0x20, 0x21, 0x22, 0x2f, 0x30, 0x31, 0x32):  # getpc, setpc, swappc, rfe, movrel*: not data
                I.srcs.append(('leaf', 'OTHER'))
        elif fam == 'SOPC':
            I.defs = ['scc']
            I.srcs = [opnd(w & 0xff), opnd((w >> 8) & 0xff)]
        elif fam == 'SOPP':
            if op in (0x04, 0x05):
                I.kind, I.cond = 'cbr', 'scc'
            elif op in (0x06, 0x07):
                I.kind, I.cond = 'cbr', 'vcc'
            elif op in (0x08, 0x09):
                I.kind, I.cond = 'cbr', 'exec'
            elif op == 0x02:
                I.kind = 'br'
            I.target = ex.get('target')
        elif fam == 'SMEM':
            n = SMEM_COUNT.get(op)
            sd = (w >> 6) & 0x7f
            if n is None:
                I.defs = sregs(sd, 2)
                I.leaf = 'OTHER'
            else:
                I.defs = sregs(sd, n)
                I.leaf = 'SMEM'
        elif fam in ('MUBUF', 'MTBUF'):
            I.defs = vregs((words[pc + 1] >> 8) & 0xff, 4)
            I.leaf = 'BUF'
        elif fam == 'FLAT':
            I.defs = vregs((words[pc + 1] >> 24) & 0xff, 4)
            I.leaf = 'BUF'
        elif fam == 'DS':
            I.defs = vregs((words[pc + 1] >> 24) & 0xff, 4)
            I.leaf = 'OTHER'
        elif fam == 'MIMG':
            I.defs = vregs((words[pc + 1] >> 8) & 0xff, 4)
            I.leaf = 'IMG'
        elif fam == 'EXP':
            w1 = words[pc + 1]
            en = w & 0xf
            compr = (w >> 10) & 1
            srcs = [w1 & 0xff, (w1 >> 8) & 0xff, (w1 >> 16) & 0xff, (w1 >> 24) & 0xff]
            if compr:
                used = [srcs[0]] * (en & 3 != 0) + [srcs[1]] * (en & 0xc != 0)
            else:
                used = [srcs[i] for i in range(4) if en >> i & 1]
            I.exp = ((w >> 4) & 0x3f, [('v', v) for v in used])
        # Only the first register of a multi-register destination is a certain definition (SMEM: count from the op);
        # the others may be over-approximated widths and never end the search for the reaching definition.
        regs = [d for d in I.defs if d not in GLOBAL_REGS]
        if fam != 'SMEM' and len(regs) > 1:
            I.weak = set(regs[1:])
        out.append(I)
    return out, status


# ---------------------------------------------------------------- slice
def live_leaf(reg, udc, stage='ps'):
    if reg == 'exec':
        return 'COV'
    if isinstance(reg, tuple) and reg[0] == 's':
        return 'USER' if (udc is None or reg[1] < udc) else 'OTHER'
    if isinstance(reg, tuple) and reg[0] == 'v' and stage == 'vs':
        return 'VID'  # vertex / instance index of the draw packet (index buffer or auto index) -> C-buf
    return 'OTHER'


GLOBAL_REGS = ('scc', 'vcc', 'exec', 'm0')
# Mutants of the classifier itself (power of N4): KYTY_F47A3_BREAK=noctl - no control roots and no v_cndmask condition;
# =smemlit - an s_load result counted as a literal; =userlit - a user-data SGPR counted as a literal. N4 must report
# DEAD under each.
BREAK = os.environ.get('KYTY_F47A3_BREAK', '')


def analyse(words, udc=None, mrt=0, stage='ps'):
    """Returns dict(status, class, leaves, n_exp, control, straight)."""
    ins, status = decode(words)
    if status != 'OK':
        return dict(status=status, cls='undetermined', leaves={'OTHER'}, n_exp=0, control=False, straight=False)
    defs = collections.defaultdict(list)
    for k, I in enumerate(ins):
        for r in I.defs:
            defs[r].append(k)
    back = any(I.target is not None and I.target <= I.pc for I in ins)
    cbr = [I for I in ins if I.kind == 'cbr']
    exec_w = defs.get('exec', [])
    straight = not back and not cbr and not exec_w
    leaves = set()
    seen = set()
    work = []
    exps = [(k, I) for k, I in enumerate(ins) if I.exp is not None and I.exp[0] == mrt]
    for k, I in exps:
        for r in I.exp[1]:
            work.append((r, k))
    if not straight and BREAK != 'noctl':
        for I_k, I in enumerate(ins):
            if I.kind == 'cbr':
                work.append((I.cond, I_k))
        for k in exec_w:
            for kind, x in ins[k].srcs:
                if kind == 'leaf':
                    leaves.add(x)
                else:
                    work.append((x, k))
    while work:
        r, k = work.pop()
        if (r, k) in seen:
            continue
        seen.add((r, k))
        ds = defs.get(r, [])
        if r in GLOBAL_REGS:
            reach = list(ds)
            live = not any(d < k for d in ds)
        elif straight:
            reach = []
            live = True
            for d in reversed([d for d in ds if d < k]):
                reach.append(d)
                if r not in ins[d].weak:
                    live = False
                    break
        else:
            reach = [d for d in ds if d < k] + ([d for d in ds if d >= k] if back else [])
            live = True
        if live:
            lf = live_leaf(r, udc, stage)
            leaves.add('LIT' if (BREAK == 'userlit' and lf == 'USER') else lf)
        for d in reach:
            D = ins[d]
            if D.leaf:
                leaves.add('LIT' if (BREAK == 'smemlit' and D.leaf == 'SMEM') else D.leaf)
            for kind, x in D.srcs:
                if BREAK == 'noctl' and x == 'vcc' and D.name.startswith('v_cndmask'):
                    continue
                if kind == 'leaf':
                    leaves.add(x)
                else:
                    work.append((x, d))
    if not exps:
        cls = 'no_export'
    elif leaves <= NEUTRAL:
        cls = 'C-imm'
    elif 'OTHER' in leaves and 'IMG' not in leaves:
        cls = 'undetermined'
    elif 'IMG' in leaves:
        cls = 'T'
    elif leaves & CBUF:
        cls = 'C-buf'
    else:
        cls = 'undetermined'
    return dict(status=status, cls=cls, leaves=leaves, n_exp=len(exps), control=not straight, straight=straight, ins=ins)


# ---------------------------------------------------------------- N4 mutants (item 718(g)(5))
SK = 104           # scratch SGPR for the inserted load
VT = 255           # scratch VGPR
S_NOP = 0xBF800000
S_WAITCNT_LGKM0 = 0xBF8C0000 | 0xC07F


def s_load_dword(sdst, sbase=0, offset=0):
    return [(0x3d << 26) | (0 << 18) | (sdst << 6) | (sbase >> 1), (offset & 0x1fffff) | (125 << 25)]


def v_mov(vd, src):
    return (0x3f << 25) | (vd << 17) | (0x01 << 9) | src


def lit_site(a, words):
    """First instruction of the MRT0 slice that is VOP1 v_mov_b32 / VOP2 (not MADMK-like) with src0 LIT, defining an
    exported or sliced VGPR; returns (pc, size) or None."""
    ins = a['ins']
    for I in ins:
        if I.fam in ('VOP1', 'VOP2') and (words[I.pc] & 0x1ff) in set(range(128, 209)) | set(range(240, 249)) | {255}:
            if I.fam == 'VOP1' and I.op != 0x01:
                continue
            if I.fam == 'VOP2' and I.op in (0x20, 0x21, 0x2c, 0x2d, 0x37, 0x38):
                continue
            return I
    return None


def mutants(words, a):
    """Returns {name: (words, expected_c_imm)} or {} when the program has no literal site of the right form."""
    I = lit_site(a, words)
    if I is None:
        return {}
    w = list(words)
    pc = I.pc
    has_lit = (w[pc] & 0x1ff) == 255
    exp_regs = [r for k, J in enumerate(a['ins']) if J.exp is not None and J.exp[0] == 0 for r in J.exp[1]]
    vexp = exp_regs[0][1]
    pre = s_load_dword(SK) + [S_WAITCNT_LGKM0]
    out = {}
    # m0: only a load into an unused SGPR is prepended - the class must stay C-imm (the mutation harness itself)
    out['m0_load_unused'] = (pre + w, True)
    # m1: the literal source of the site replaced by the loaded SGPR (data from s_load)
    m = list(w)
    m[pc] = (m[pc] & ~0x1ff) | SK
    if has_lit:
        m[pc + 1] = S_NOP
    out['m1_literal_from_s_load'] = (pre + m, False)
    # m4: the literal source of the site replaced by user-data SGPR s0 (push data of the emulator), no load inserted;
    # read with user_data_count >= 1 (item 718(g)(2): user-SGPR -> C-buf)
    u = list(w)
    u[pc] = (u[pc] & ~0x1ff) | 0
    if has_lit:
        u[pc + 1] = S_NOP
    out['m4_literal_from_user_sgpr'] = (u, False)
    # m2: branch on the loaded value over a second literal move into the exported VGPR (control dependence only)
    br = [0xBF000000 | (0x06 << 16) | (128 << 8) | SK,            # s_cmp_eq_u32 s104, 0
          0xBF800000 | (0x05 << 16) | 2,                          # s_cbranch_scc1 +2
          v_mov(vexp, 255), 0x3F800000]                           # v_mov_b32 v<exp>, 1.0 (literal)
    out['m2_branch_on_s_load'] = (pre + br + w, False)
    # m3: the site becomes v_cndmask_b32 with VCC = (s104 == 0); both values literals (condition data only)
    cm = list(w)
    if I.fam == 'VOP1':
        d = (cm[pc] >> 17) & 0xff
        cm[pc] = (0x01 << 25) | (d << 17) | (VT << 9) | (cm[pc] & 0x1ff)
        vcmp = [(0x35 << 26) | (0xc2 << 16) | 106, (128 << 9) | SK]  # v_cmp_eq_u32_e64 vcc, s104, 0
        out['m3_cndmask_on_s_load'] = (pre + vcmp + [v_mov(VT, 242)] + cm, False)
    return out


# ---------------------------------------------------------------- fixtures
def fx():
    ok = True
    EXP = lambda en, t, v0, v1=0, v2=0, v3=0: [(0x3e << 26) | (1 << 11) | (t << 4) | en, v0 | (v1 << 8) | (v2 << 16) | (v3 << 24)]
    END = [0xBF810000]
    cases = {
        'lit': ([v_mov(0, 255), 0x3F800000, v_mov(1, 128)] + EXP(3, 0, 0, 1) + END, 'C-imm'),
        'user': ([v_mov(0, 2)] + EXP(1, 0, 0) + END, 'C-buf'),
        'smem': (s_load_dword(8) + [S_WAITCNT_LGKM0, v_mov(0, 8)] + EXP(1, 0, 0) + END, 'C-buf'),
        'vin': (EXP(1, 0, 3) + END, 'undetermined'),
        'shadow': ([v_mov(0, 2), v_mov(0, 128)] + EXP(1, 0, 0) + END, 'C-imm'),
        'mrt1_only': ([v_mov(0, 128), v_mov(1, 2)] + EXP(1, 0, 0) + EXP(1, 1, 1) + END, 'C-imm'),
        # s_mov_b32 s4, 1.0 over-defines s5 (pair): the read of user s5 must still see the live-in value
        'weak_pair': ([0xBE800000 | (2 << 16) | (0x03 << 8) | 242, v_mov(0, 3)] + EXP(1, 0, 0) + END, 'C-buf'),
        'cbuf_other': (s_load_dword(8) + [S_WAITCNT_LGKM0, (0x08 << 25) | (0 << 17) | (3 << 9) | 8] + EXP(1, 0, 0) + END,
                       'undetermined'),
        'img': ([(0x3c << 26) | (0xf << 8), (0 << 8)] + EXP(1, 0, 0) + END, 'T'),
        'interp': ([(0x32 << 26) | (0 << 18)] + EXP(1, 0, 0) + END, 'C-buf'),
    }
    for name, (words, want) in cases.items():
        a = analyse(words, udc=4)
        good = a['cls'] == want
        ok &= good
        print('fixture %-10s class %-12s want %-12s leaves %s %s' % (name, a['cls'], want, sorted(a['leaves']), 'ok' if good else 'BAD'))
    # mutants on the 'lit' fixture
    words = cases['lit'][0]
    a = analyse(words, udc=4)
    for mname, (mw, want_cimm) in mutants(words, a).items():
        need = 'USER' if mname.startswith('m4') else 'SMEM'
        b = analyse(mw, udc=4)
        good = (b['cls'] == 'C-imm') if want_cimm else (b['cls'] != 'C-imm' and need in b['leaves'])
        ok &= good
        print('fixture mutant %-24s class %-12s leaves %s %s' % (mname, b['cls'], sorted(b['leaves']), 'ok' if good else 'BAD'))
    print('ALL OK' if ok else 'FAIL')
    return ok


# ---------------------------------------------------------------- N4
def udc_index():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import cat_f47a3 as C
    out = {}
    for f in C.catalog(CATALOG):
        if f['ok'] and os.path.basename(f['path']).startswith('ps_'):
            out.setdefault(f['hash'], set()).add(f['udc'])
    return out


def n4_one(words, udc, tag, lines):
    a = analyse(words, udc=udc)
    lines.append('%s orig class %s leaves %s control %d' % (tag, a['cls'], ','.join(sorted(a['leaves'])), a['control']))
    if a['cls'] != 'C-imm':
        return None
    ms = mutants(words, a)
    if not ms:
        lines.append('%s no literal site of the mutant form' % tag)
        return None
    res = {}
    for mname, (mw, want_cimm) in ms.items():
        need = 'USER' if mname.startswith('m4') else 'SMEM'
        b = analyse(mw, udc=max(udc or 0, 1) if need == 'USER' else udc)
        # not C-imm AND the inserted input is named among the inputs (item 718(g)(1)-(2): class by that input)
        good = (b['cls'] == 'C-imm') if want_cimm else (b['cls'] != 'C-imm' and need in b['leaves'])
        res[mname] = good
        lines.append('%s %s class %s leaves %s expect %s %s' % (tag, mname, b['cls'], ','.join(sorted(b['leaves'])),
                                                              'C-imm' if want_cimm else 'not C-imm with ' + need, 'ok' if good else 'DEAD'))
    return res


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    udc = int(sys.argv[sys.argv.index('--udc') + 1]) if '--udc' in sys.argv else None
    if mode == 'fixtures':
        return 0 if fx() else 1
    if mode in ('prog', 'n4prog'):
        b = open(sys.argv[2], 'rb').read()
        words = list(struct.unpack('<%dI' % (len(b) // 4), b))
        if mode == 'prog':
            mrt = int(sys.argv[sys.argv.index('--mrt') + 1]) if '--mrt' in sys.argv else 0
            stage = sys.argv[sys.argv.index('--stage') + 1] if '--stage' in sys.argv else 'ps'
            a = analyse(words, udc=udc, mrt=mrt, stage=stage)
            print('class %s leaves %s exports %d control %d status %s' % (a['cls'], sorted(a['leaves']), a['n_exp'], a['control'], a['status']))
            return 0
        lines = []
        res = n4_one(words, udc, os.path.basename(sys.argv[2]), lines)
        print(chr(10).join(lines))
        alive = res is not None and all(res.values())
        print('N4 %s' % ('ALIVE' if alive else ('NOT_APPLICABLE' if res is None else 'DEAD')))
        return 0 if alive else 1
    if mode == 'n4':
        if not fx() and '--skip-fixtures' not in sys.argv:
            print('fixtures FAIL - N4 not run')
            return 1
        udcs = udc_index()
        progs = {}
        for arm in sorted(os.listdir(GCN_ROOT)):
            d = os.path.join(GCN_ROOT, arm)
            for fn in sorted(os.listdir(d)):
                m = re.match(r'^ps_([0-9a-f]{16})\.bin$', fn)
                if m and m.group(1) not in progs:
                    progs[m.group(1)] = os.path.join(d, fn).replace(os.sep, '/')
        lines = []
        dist = collections.Counter()
        cimm = []
        for h, path in sorted(progs.items()):
            b = open(path, 'rb').read()
            words = list(struct.unpack('<%dI' % (len(b) // 4), b))
            u = udcs.get(h)
            u1 = min(u) if u else None
            a = analyse(words, udc=u1)
            dist[a['cls']] += 1
            lines.append('prog %s udc %s class %s leaves %s control %d sha %s' % (
                h, sorted(u) if u else '-', a['cls'], ','.join(sorted(a['leaves'])), a['control'],
                hashlib.sha256(b).hexdigest()[:16]))
            if a['cls'] == 'C-imm':
                cimm.append((h, words, u1))
        lines.append('T1 PS programs %d classes %s' % (len(progs), sorted(dist.items())))
        vsd = collections.Counter()
        vss = {}
        for arm in sorted(os.listdir(GCN_ROOT)):
            d = os.path.join(GCN_ROOT, arm)
            for fn in sorted(os.listdir(d)):
                m = re.match(r'^vs_([0-9a-f]{16})\.bin$', fn)
                if m and m.group(1) not in vss:
                    vss[m.group(1)] = os.path.join(d, fn)
        for h, path in sorted(vss.items()):
            b = open(path, 'rb').read()
            a = analyse(list(struct.unpack('<%dI' % (len(b) // 4), b)), mrt=12, stage='vs')
            vsd[a['cls']] += 1
        lines.append('T1 VS programs %d POS0 classes %s (reference for the coverage member)' % (len(vss), sorted(vsd.items())))
        tested = 0
        dead = 0
        for h, words, u1 in cimm:
            res = n4_one(words, u1, 'n4 ' + h, lines)
            if res is None:
                continue
            tested += 1
            dead += not all(res.values())
        lines.append('N4: C-imm programs %d, with a literal site %d, classifier dead on %d' % (len(cimm), tested, dead))
        ok = tested >= 1 and dead == 0 and dist['T'] >= 1
        lines.append('ALL OK' if ok else 'FAIL')
        text = chr(10).join(lines) + chr(10)
        if '--out' in sys.argv:
            open(sys.argv[sys.argv.index('--out') + 1], 'w', encoding='ascii', newline='\n').write(text)
        print(text[-3000:])
        return 0 if ok else 1
    print('usage: prog|n4|n4prog|fixtures')
    return 2


if __name__ == '__main__':
    sys.exit(main())
