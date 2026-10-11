# F47a4 (HPP-818, ROADMAP s122 item 722(b)-(c)): own classifier of the colour export of a pixel program (RDNA2 words)
# and the negative control N4 of the classifier - edition 4 of cls_f47a3.py (F47a3, item 718(g)(1)-(5)).
# Changes against cls_f47a3.py (sha256 db812c1829e33925...), and only these:
#   (1) RC1 F47b3: SOP2 0x04 s_addc_u32, 0x05 s_subb_u32, 0x0a s_cselect_b32, 0x0b s_cselect_b64 read SCC; the wrong
#       0x30 / 0x31 (s_lshl3_add_u32 / s_lshl4_add_u32) are removed; table SCC_READERS of every SCC reader of the
#       classifier and the mode `scccheck` that compares it with the decoder of the installed binary (FS13 ea6c6e9e);
#       N4 mutants m5 (s_cselect_b32 by SCC from s_load), m6 (s_cselect_b64), m7 (s_addc_u32); classifier mutants
#       nocsel / noaddc / e3scc must be DEAD.
#   (2) RC2 F47b3: leaf OTHER_BR - a live-in VGPR of a pixel program added only by the over-approximation of a program
#       with branches / EXEC writers (an earlier certain definition of the register exists in program order); OTHER
#       stays for every other source (genuine live-in VGPR, LDS, M0, TTMP, unknown encodings, ...). V4 (item 721(e),
#       722(c)): leaves with C-buf / T and OTHER_BR without OTHER -> class by C-buf / T, printed `v4 1`.
# Read only; ASCII only; exits 3 when C:/kyty/SEALED_RUN.lock exists. Instruction lengths and families - walk() of
# docs/track-f/f23a/gcn_f23a.py (F23a, calibrated 331 of 331); operand fields are decoded here anew (RDNA2 [I]).
#
# Class of the value exported to MRT<t> (EXP target t, all enabled channels together):
#   leaves of the backward slice of the exported VGPRs, data AND control:
#     LIT      literal word (src 255, VOP2 MADMK/MADAK K, SOPK simm16) or inline constant (128-208, 240-248), NULL (125)
#     USER     live-in SGPR below user_data_count (unknown count: every live-in SGPR)       -> C-buf
#     SMEM     s_load / s_buffer_load result                                               -> C-buf
#     BUF      MUBUF / MTBUF / FLAT / GLOBAL result                                        -> C-buf
#     INTERP   VINTRP / v_interp_*_f16 (vertex attribute)                                  -> C-buf
#     IMG      MIMG result                                                                 -> T
#     VID      (stage vs only) live-in VGPR = vertex / instance index of the draw packet    -> C-buf
#     COV      live-in EXEC (coverage at wave start; checked by the blend/coverage member) -> neutral
#     OTHER_BR live-in VGPR (stage ps) reached only through the over-approximation of a non-straight program: an
#              earlier certain definition of the register exists in program order        -> V4
#     OTHER_BRS the same for a live-in SGPR above user data (not named by item 722(c)): read as OTHER; the class
#              with it read as OTHER_BR is printed as b5 (question V5 to the lead)
#     OTHER    every other live-in VGPR (barycentrics, FragCoord), live-in SGPR above user data, LDS, lds_direct, TTMP,
#              M0, apertures, s_getpc / s_getreg / s_memtime, unknown encodings           -> "undetermined"
#   class: C-imm iff leaves <= {LIT, COV}; else T if IMG (every other input of the set is printed and also needs the
#   member M2); else "undetermined" if OTHER; else C-buf if any C-buf leaf (v4 = OTHER_BR among the leaves); else
#   "undetermined".
# Reaching definitions: straight-line program (no conditional branch, no backward branch, no EXEC writer) - the last
# certain definition of the register before the use (exact; over-approximated extra registers of a multi-register
# destination are weak and do not end the search), live-in when there is none; otherwise every earlier definition AND
# the live-in value (and every later one when a backward branch exists). SCC / VCC / EXEC / M0 always: every
# definition anywhere, the live-in value only when no definition precedes the use in program order.
# Control dependence (item 718(g)(1)): with any conditional branch or EXEC writer, the conditions (SCC for
# s_cbranch_scc*, VCC for s_cbranch_vcc*, EXEC for s_cbranch_exec* and every EXEC writer's sources) are added to the
# slice; the condition of v_cndmask (VCC or src2) is a data source; SCC read by s_cselect / s_cmov / s_cmovk /
# s_addc / s_subb or by a source operand 253 is a data source.
#
# Usage:
#   python cls_f47a4.py prog <gcn .bin> [--udc N] [--mrt T] [--stage vs]  class of one export (VS position: --mrt 12 --stage vs)
#   python cls_f47a4.py n4 [--out FILE]                            N4 offline on the T1 corpus (PS dumps)
#   python cls_f47a4.py n4prog <gcn .bin> [--udc N]                N4 on one program (F47e: D_b)
#   python cls_f47a4.py fixtures                                   synthetic programs with known classes
#   python cls_f47a4.py scccheck [--commit C]                      SCC reader table vs the decoder at commit C (ea6c6e9e)
#   KYTY_F47A4_BREAK=noctl|smemlit|userlit|nocsel|noaddc|e3scc|nobr   mutants of the classifier itself
import collections
import hashlib
import importlib.util
import os
import re
import struct
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    print('LOCK present - exit 3')
    sys.exit(3)

GCN_F23A = 'C:/kyty/KytyPS5/docs/track-f/f23a/gcn_f23a.py'
_spec = importlib.util.spec_from_file_location('gcn_f23a', GCN_F23A)
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

CAT_F47A3 = 'C:/kyty/KytyPS5/docs/track-f/f47a3/cat_f47a3.py'
GCN_ROOT = 'C:/kyty/s288/s4/gcn'
CATALOG = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19'
REPO = 'C:/kyty/KytyPS5'
DECODE = 'src/graphics/shader/recompiler/frontend/decode/'

CBUF = {'USER', 'SMEM', 'BUF', 'INTERP', 'VID'}
NEUTRAL = {'LIT', 'COV'}

# Mutants of the classifier itself (power of N4 and of the fixtures): noctl - no control roots and no v_cndmask
# condition; smemlit - an s_load result counted as a literal; userlit - a user-data SGPR counted as a literal;
# nocsel - s_cselect_b32/b64 do not read SCC; noaddc - s_addc_u32 / s_subb_u32 do not read SCC; e3scc - the SOP2 SCC
# readers of edition 3 (0x30, 0x31) instead of the true ones; nobr - OTHER_BR not separated from OTHER.
BREAK = os.environ.get('KYTY_F47A4_BREAK', '')

# Every SCC reader of the classifier, by family (item 722(b)(1)); opcode -> RDNA2 name. Source operand 253 (SCC) in
# any scalar or vector source field is a reader as well (opnd()). SOPC and the SOPK compares only write SCC.
SCC_READERS = [
    ('SOP1', 0x05, 'S_CMOV_B32'),
    ('SOP1', 0x06, 'S_CMOV_B64'),
    ('SOP2', 0x04, 'S_ADDC_U32'),
    ('SOP2', 0x05, 'S_SUBB_U32'),
    ('SOP2', 0x0a, 'S_CSELECT_B32'),
    ('SOP2', 0x0b, 'S_CSELECT_B64'),
    ('SOPK', 0x02, 'S_CMOVK_I32'),
    ('SOPP', 0x04, 'S_CBRANCH_SCC0'),
    ('SOPP', 0x05, 'S_CBRANCH_SCC1'),
]
READER_NAME = re.compile(r'^S_(CSELECT|CMOV|CMOVK|ADDC|SUBB|CBRANCH_SCC)')
E3_WRONG = [('SOP2', 0x30, 'S_LSHL3_ADD_U32'), ('SOP2', 0x31, 'S_LSHL4_ADD_U32')]


def sop2_scc_readers():
    if BREAK == 'e3scc':
        return {0x30, 0x31}
    s = {0x04, 0x05, 0x0a, 0x0b}
    if BREAK == 'nocsel':
        s -= {0x0a, 0x0b}
    if BREAK == 'noaddc':
        s -= {0x04, 0x05}
    return s


SOP2_SCC = sop2_scc_readers()


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
            if op in SOP2_SCC:  # s_addc_u32 0x04, s_subb_u32 0x05, s_cselect_b32 0x0a, s_cselect_b64 0x0b read SCC
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


def classify(leaves, n_exp, brs_as_br=False):
    """OTHER_BRS (an over-approximated live-in SGPR above user data) is read as OTHER by the letter of item 722(c);
    brs_as_br=True gives the reference reading as OTHER_BR (question V5 to the lead, field b5)."""
    if not n_exp:
        return 'no_export'
    if leaves <= NEUTRAL:
        return 'C-imm'
    leaves = set(leaves)
    if 'OTHER_BRS' in leaves:
        leaves.discard('OTHER_BRS')
        leaves.add('OTHER_BR' if brs_as_br else 'OTHER')
    if leaves <= NEUTRAL:
        return 'C-imm'
    if 'IMG' in leaves:
        return 'T'
    if 'OTHER' in leaves:
        return 'undetermined'
    if leaves & CBUF:
        return 'C-buf'
    return 'undetermined'


def analyse(words, udc=None, mrt=0, stage='ps'):
    """Returns dict(status, cls, v4, leaves, n_exp, control, straight)."""
    ins, status = decode(words)
    if status != 'OK':
        return dict(status=status, cls='undetermined', v4=0, b5='undetermined', leaves={'OTHER'}, n_exp=0, control=False, straight=False)
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
        br_only = False
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
            # RC2 F47b3: the live-in value is added only by the over-approximation when an earlier certain definition
            # of the register exists in program order (the straight-line rule would have ended the search there)
            br_only = any(d < k and r not in ins[d].weak for d in ds)
        if live:
            lf = live_leaf(r, udc, stage)
            if lf == 'OTHER' and br_only and BREAK != 'nobr':
                lf = 'OTHER_BR' if r[0] == 'v' else 'OTHER_BRS'
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
    cls = classify(leaves, len(exps))
    v4 = int(cls in ('C-buf', 'T') and 'OTHER_BR' in leaves)
    b5 = classify(leaves, len(exps), brs_as_br=True)
    return dict(status=status, cls=cls, v4=v4, b5=b5, leaves=leaves, n_exp=len(exps), control=not straight, straight=straight,
                ins=ins)


# ---------------------------------------------------------------- encoders
SK = 104           # scratch SGPR for the inserted load
SD = 106           # scratch SGPR (even) for the select / carry mutants
VT = 255           # scratch VGPR
S_NOP = 0xBF800000
S_WAITCNT_LGKM0 = 0xBF8C0000 | 0xC07F
S_ENDPGM = 0xBF810000


def s_load_dword(sdst, sbase=0, offset=0):
    return [(0x3d << 26) | (0 << 18) | (sdst << 6) | (sbase >> 1), (offset & 0x1fffff) | (125 << 25)]


def v_mov(vd, src):
    return (0x3f << 25) | (vd << 17) | (0x01 << 9) | src


def sop2(op, sdst, s0, s1, lit=None):
    return [0x80000000 | (op << 23) | (sdst << 16) | (s1 << 8) | s0] + ([lit] if lit is not None else [])


def sop1(op, sdst, s0, lit=None):
    return [0xBE800000 | (sdst << 16) | (op << 8) | s0] + ([lit] if lit is not None else [])


def sopk(op, sdst, simm):
    return [0xB0000000 | (op << 23) | (sdst << 16) | (simm & 0xffff)]


def sopc(op, s0, s1):
    return [0xBF000000 | (op << 16) | (s1 << 8) | s0]


def sopp(op, simm=0):
    return [0xBF800000 | (op << 16) | (simm & 0xffff)]


def ds_read(vdst):
    return [(0x36 << 26) | (0x36 << 18), 0 | (vdst << 24)]


# ---------------------------------------------------------------- N4 mutants (item 718(g)(5), 722(b)(2))
def lit_site(a, words):
    """First instruction of the MRT0 slice that is VOP1 v_mov_b32 / VOP2 (not MADMK-like) with src0 LIT, defining an
    exported or sliced VGPR; returns the instruction or None."""
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
    litval = w[pc + 1] if has_lit else 0x3F800000
    exp_regs = [r for k, J in enumerate(a['ins']) if J.exp is not None and J.exp[0] == 0 for r in J.exp[1]]
    vexp = exp_regs[0][1]
    pre = s_load_dword(SK) + [S_WAITCNT_LGKM0]
    out = {}

    def site(src):
        m = list(w)
        m[pc] = (m[pc] & ~0x1ff) | src
        if has_lit:
            m[pc + 1] = S_NOP
        return m

    # m0: only a load into an unused SGPR is prepended - the class must stay C-imm (the mutation harness itself)
    out['m0_load_unused'] = (pre + w, True)
    # m1: the literal source of the site replaced by the loaded SGPR (data from s_load)
    out['m1_literal_from_s_load'] = (pre + site(SK), False)
    # m4: the literal source of the site replaced by user-data SGPR s0 (push data), no load inserted
    out['m4_literal_from_user_sgpr'] = (site(0), False)
    # m2: branch on the loaded value over a second literal move into the exported VGPR (control dependence only)
    br = sopc(0x06, SK, 128) + sopp(0x05, 2) + [v_mov(vexp, 255), 0x3F800000]
    out['m2_branch_on_s_load'] = (pre + br + w, False)
    # m3: the site becomes v_cndmask_b32 with VCC = (s104 == 0); both values literals (condition data only)
    if I.fam == 'VOP1':
        cm = list(w)
        d = (cm[pc] >> 17) & 0xff
        cm[pc] = (0x01 << 25) | (d << 17) | (VT << 9) | (cm[pc] & 0x1ff)
        vcmp = [(0x35 << 26) | (0xc2 << 16) | 106, (128 << 9) | SK]  # v_cmp_eq_u32_e64 vcc, s104, 0
        out['m3_cndmask_on_s_load'] = (pre + vcmp + [v_mov(VT, 242)] + cm, False)
    # m5: scalar select of the literal by SCC from s_cmp on the loaded value (straight program, RC1 F47b3)
    cmp = sopc(0x06, SK, 128)  # s_cmp_eq_u32 s104, 0
    out['m5_s_cselect_b32_on_s_load'] = (pre + cmp + sop2(0x0a, SD, 255, 128, litval) + site(SD), False)
    # m6: the same with s_cselect_b64
    out['m6_s_cselect_b64_on_s_load'] = (pre + cmp + sop2(0x0b, SD, 255, 128, litval) + site(SD), False)
    # m7: s_addc_u32 s106, 0, 0 = SCC (carry) from s_cmp on the loaded value
    out['m7_s_addc_u32_on_s_load'] = (pre + cmp + sop2(0x04, SD, 128, 128) + site(SD), False)
    return out


def need_of(mname):
    return 'USER' if mname.startswith('m4') else 'SMEM'


# ---------------------------------------------------------------- fixtures
def fx():
    ok = True
    EXP = lambda en, t, v0, v1=0, v2=0, v3=0: [(0x3e << 26) | (1 << 11) | (t << 4) | en, v0 | (v1 << 8) | (v2 << 16) | (v3 << 24)]
    END = [S_ENDPGM]
    L = s_load_dword(8) + [S_WAITCNT_LGKM0]
    CMP = sopc(0x06, 8, 128)  # s_cmp_eq_u32 s8, 0
    LU = s_load_dword(2) + [S_WAITCNT_LGKM0]  # load into s2 (below user_data_count 4: its live-in is USER)
    CMPU = sopc(0x06, 2, 128)  # s_cmp_eq_u32 s2, 0
    # name: (words, class, v4, b5 class, leaf that must be present, leaf that must be absent)
    cases = {
        'lit': ([v_mov(0, 255), 0x3F800000, v_mov(1, 128)] + EXP(3, 0, 0, 1) + END, 'C-imm', 0, 'C-imm', 'LIT', None),
        'user': ([v_mov(0, 2)] + EXP(1, 0, 0) + END, 'C-buf', 0, 'C-buf', 'USER', None),
        'smem': (L + [v_mov(0, 8)] + EXP(1, 0, 0) + END, 'C-buf', 0, 'C-buf', 'SMEM', None),
        'vin': (EXP(1, 0, 3) + END, 'undetermined', 0, 'undetermined', 'OTHER', 'OTHER_BR'),
        'shadow': ([v_mov(0, 2), v_mov(0, 128)] + EXP(1, 0, 0) + END, 'C-imm', 0, 'C-imm', 'LIT', None),
        'mrt1_only': ([v_mov(0, 128), v_mov(1, 2)] + EXP(1, 0, 0) + EXP(1, 1, 1) + END, 'C-imm', 0, 'C-imm', 'LIT', None),
        'weak_pair': (sop1(0x03, 2, 242) + [v_mov(0, 3)] + EXP(1, 0, 0) + END, 'C-buf', 0, 'C-buf', 'USER', None),
        'cbuf_other': (L + [(0x08 << 25) | (0 << 17) | (3 << 9) | 8] + EXP(1, 0, 0) + END, 'undetermined', 0, 'undetermined', 'OTHER',
                       None),
        'img': ([(0x3c << 26) | (0xf << 8), (0 << 8)] + EXP(1, 0, 0) + END, 'T', 0, 'T', 'IMG', None),
        'interp': ([(0x32 << 26) | (0 << 18)] + EXP(1, 0, 0) + END, 'C-buf', 0, 'C-buf', 'INTERP', None),
        # RC1 F47b3: SCC readers (straight programs, no branch, no v_cndmask)
        'cselect32': (L + CMP + sop2(0x0a, 10, 255, 128, 0x3F800000) + [v_mov(0, 10)] + EXP(1, 0, 0) + END, 'C-buf', 0, 'C-buf', 'SMEM',
                      None),
        'cselect64': (L + CMP + sop2(0x0b, 10, 255, 128, 0x3F800000) + [v_mov(0, 10)] + EXP(1, 0, 0) + END, 'C-buf', 0, 'C-buf', 'SMEM',
                      None),
        'addc': (L + CMP + sop2(0x04, 10, 128, 128) + [v_mov(0, 10)] + EXP(1, 0, 0) + END, 'C-buf', 0, 'C-buf', 'SMEM', None),
        'subb': (L + CMP + sop2(0x05, 10, 128, 128) + [v_mov(0, 10)] + EXP(1, 0, 0) + END, 'C-buf', 0, 'C-buf', 'SMEM', None),
        'cmov': (L + sop1(0x03, 10, 128) + CMP + sop1(0x05, 10, 255, 0x3F800000) + [v_mov(0, 10)] + EXP(1, 0, 0) + END,
                 'C-buf', 0, 'C-buf', 'SMEM', None),
        'cmovk': (L + sop1(0x03, 10, 128) + CMP + sopk(0x02, 10, 7) + [v_mov(0, 10)] + EXP(1, 0, 0) + END, 'C-buf', 0, 'C-buf', 'SMEM',
                  None),
        'scc_operand': (L + CMP + sop1(0x03, 10, 253) + [v_mov(0, 10)] + EXP(1, 0, 0) + END, 'C-buf', 0, 'C-buf', 'SMEM', None),
        # 0x30 is s_lshl3_add_u32: no SCC read - a literal stays C-imm even after a compare on a loaded value
        'lshl3add': (L + CMP + sop2(0x30, 10, 255, 128, 0x3F800000) + [v_mov(0, 10)] + EXP(1, 0, 0) + END, 'C-imm', 0, 'C-imm', 'LIT',
                     'SMEM'),
        # RC2 F47b3: x10 form (branch on s_load into a user-range SGPR, site literal) vs x9 form (straight, LDS + s_load)
        'br_smem': (LU + CMPU + sopp(0x05, 0) + [v_mov(0, 255), 0x3F800000] + EXP(1, 0, 0) + END, 'C-buf', 1, 'C-buf', 'OTHER_BR',
                    'OTHER'),
        'lds_smem': (L + ds_read(5) + [S_WAITCNT_LGKM0, (0x03 << 25) | (0 << 17) | (5 << 9) | 8] + EXP(1, 0, 0) + END,
                     'undetermined', 0, 'undetermined', 'OTHER', 'OTHER_BR'),
        # a genuine live-in VGPR (no earlier definition) under a branch stays OTHER
        'br_live_in': (LU + CMPU + sopp(0x05, 0) + EXP(1, 0, 3) + END, 'undetermined', 0, 'undetermined', 'OTHER', 'OTHER_BR'),
        'br_img': (LU + CMPU + sopp(0x05, 0) + [(0x3c << 26) | (0xf << 8), (0 << 8)] + EXP(1, 0, 0) + END, 'T', 1, 'T', 'OTHER_BR',
                   'OTHER'),
        # the same branch on an s_load into an SGPR above user data (s8, udc 4): OTHER_BRS - read as OTHER, b5 C-buf
        'br_smem_hi': (L + CMP + sopp(0x05, 0) + [v_mov(0, 255), 0x3F800000] + EXP(1, 0, 0) + END, 'undetermined', 0, 'C-buf',
                       'OTHER_BRS', 'OTHER'),
    }
    for name, (words, want, want_v4, want_b5, must, must_not) in cases.items():
        a = analyse(words, udc=4)
        good = (a['cls'] == want and a['v4'] == want_v4 and a['b5'] == want_b5 and (must is None or must in a['leaves'])
                and (must_not is None or must_not not in a['leaves']))
        ok &= good
        print('fixture %-12s class %-12s v4 %d b5 %-12s want %-12s v4 %d b5 %-12s leaves %s %s' % (
            name, a['cls'], a['v4'], a['b5'], want, want_v4, want_b5, sorted(a['leaves']), 'ok' if good else 'BAD'))
    words = cases['lit'][0]
    a = analyse(words, udc=4)
    for mname, (mw, want_cimm) in mutants(words, a).items():
        b = analyse(mw, udc=4)
        good = (b['cls'] == 'C-imm') if want_cimm else (b['cls'] != 'C-imm' and need_of(mname) in b['leaves'])
        ok &= good
        print('fixture mutant %-28s class %-12s leaves %s %s' % (mname, b['cls'], sorted(b['leaves']), 'ok' if good else 'BAD'))
    print('ALL OK' if ok else 'FAIL')
    return ok


# ---------------------------------------------------------------- SCC reader table vs the decoder (item 722(b)(1))
def decoder_tables(commit):
    src = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (commit, DECODE + 'ScalarAluOps.cpp')], capture_output=True,
                         check=True).stdout.decode('utf-8')
    tabs = {}
    for fam in ('SOP1', 'SOP2', 'SOPC', 'SOPK', 'SOPP'):
        m = re.search(r'constexpr OpcodeMap %s_OPCODE_LIST\[\] = \{(.*?)\n\};' % fam, src, re.S)
        tabs[fam] = {int(o, 16): n for o, n in re.findall(r'\{0x([0-9a-f]+)u, Opcode::(\w+)\}', m.group(1))}
    sd = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (commit, DECODE + 'ShaderDecoder.cpp')], capture_output=True,
                        check=True).stdout.decode('utf-8')
    return tabs, ('case 253u: operand.kind = OperandKind::Scc; return;' in sd)


def reads_scc(fam, op):
    """Does decode() of one instruction of this family / opcode read SCC (data source or branch condition)?"""
    if fam == 'SOP1':
        words = sop1(op, 10, 128)
    elif fam == 'SOP2':
        words = sop2(op, 10, 128, 128)
    elif fam == 'SOPK':
        words = sopk(op, 10, 0)
    elif fam == 'SOPC':
        words = sopc(op, 8, 128)
    else:
        words = sopp(op, 0)
    ins, status = decode(words + [S_ENDPGM])
    if status != 'OK' or not ins:
        return None
    I = ins[0]
    return ('reg', 'scc') in I.srcs or I.cond == 'scc'


def scccheck(commit):
    ok = True
    tabs, op253 = decoder_tables(commit)
    print('decoder %s %s: SOP1 %d SOP2 %d SOPC %d SOPK %d SOPP %d opcodes; operand 253 -> Scc %s' % (
        commit, DECODE + 'ScalarAluOps.cpp', len(tabs['SOP1']), len(tabs['SOP2']), len(tabs['SOPC']), len(tabs['SOPK']),
        len(tabs['SOPP']), 'yes' if op253 else 'NO'))
    ok &= op253 and opnd(253) == ('reg', 'scc')
    table = {(f, o) for f, o, _ in SCC_READERS}
    for fam, op, name in SCC_READERS:
        dname = tabs[fam].get(op)
        r = reads_scc(fam, op)
        same = dname is None or dname == name
        good = same and r is True
        ok &= good
        print('reader %-4s 0x%02x %-16s decoder %-18s classifier reads SCC %s %s' % (
            fam, op, name, dname or '- (not decoded: UNSUPPORTED)', r, 'ok' if good else 'BAD'))
    for fam, tab in sorted(tabs.items()):
        for op, dname in sorted(tab.items()):
            if READER_NAME.match(dname) and (fam, op) not in table:
                ok = False
                print('decoder reader %s 0x%02x %s missing from SCC_READERS BAD' % (fam, op, dname))
    for fam, op, name in E3_WRONG:
        dname = tabs[fam].get(op)
        r = reads_scc(fam, op)
        good = dname == name and r is False
        ok &= good
        print('edition-3 code %s 0x%02x decoder %-18s classifier reads SCC %s %s' % (fam, op, dname, r, 'ok' if good else 'BAD'))
    spurious = []
    for fam in ('SOP1', 'SOP2', 'SOPK', 'SOPC', 'SOPP'):
        for op, dname in sorted(tabs[fam].items()):
            if (fam, op) in table:
                continue
            r = reads_scc(fam, op)
            if r:
                spurious.append('%s 0x%02x %s' % (fam, op, dname))
    ok &= not spurious
    print('decoder opcodes outside the table that the classifier reads SCC from: %d %s' % (len(spurious), spurious))
    print('ALL OK' if ok else 'FAIL')
    return ok


# ---------------------------------------------------------------- N4
def udc_index():
    spec = importlib.util.spec_from_file_location('cat_f47a3', CAT_F47A3)
    C = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    out = {}
    for f in C.catalog(CATALOG):
        if f['ok'] and os.path.basename(f['path']).startswith('ps_'):
            out.setdefault(f['hash'], set()).add(f['udc'])
    return out


def n4_one(words, udc, tag, lines):
    a = analyse(words, udc=udc)
    lines.append('%s orig class %s v4 %d b5 %s leaves %s control %d' % (tag, a['cls'], a['v4'], a['b5'], ','.join(sorted(a['leaves'])), a['control']))
    if a['cls'] != 'C-imm':
        return None
    ms = mutants(words, a)
    if not ms:
        lines.append('%s no literal site of the mutant form' % tag)
        return None
    res = {}
    for mname, (mw, want_cimm) in ms.items():
        need = need_of(mname)
        b = analyse(mw, udc=max(udc or 0, 1) if need == 'USER' else udc)
        # not C-imm AND the inserted input is named among the inputs (item 718(g)(1)-(2): class by that input)
        good = (b['cls'] == 'C-imm') if want_cimm else (b['cls'] != 'C-imm' and need in b['leaves'])
        res[mname] = good
        lines.append('%s %s class %s v4 %d leaves %s expect %s %s' % (tag, mname, b['cls'], b['v4'], ','.join(sorted(b['leaves'])),
                                                                     'C-imm' if want_cimm else 'not C-imm with ' + need,
                                                                     'ok' if good else 'DEAD'))
    return res


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    udc = int(sys.argv[sys.argv.index('--udc') + 1]) if '--udc' in sys.argv else None
    print('cls_f47a4 break=%s' % (BREAK or '-'))
    if mode == 'fixtures':
        return 0 if fx() else 1
    if mode == 'scccheck':
        commit = sys.argv[sys.argv.index('--commit') + 1] if '--commit' in sys.argv else 'ea6c6e9e'
        return 0 if scccheck(commit) else 1
    if mode in ('prog', 'n4prog'):
        b = open(sys.argv[2], 'rb').read()
        words = list(struct.unpack('<%dI' % (len(b) // 4), b))
        if mode == 'prog':
            mrt = int(sys.argv[sys.argv.index('--mrt') + 1]) if '--mrt' in sys.argv else 0
            stage = sys.argv[sys.argv.index('--stage') + 1] if '--stage' in sys.argv else 'ps'
            a = analyse(words, udc=udc, mrt=mrt, stage=stage)
            print('class %s v4 %d b5 %s leaves %s exports %d control %d status %s' % (a['cls'], a['v4'], a['b5'], sorted(a['leaves']),
                                                                                     a['n_exp'],
                                                                              a['control'], a['status']))
            return 0
        lines = []
        res = n4_one(words, udc, os.path.basename(sys.argv[2]), lines)
        print(chr(10).join(lines))
        alive = res is not None and all(res.values())
        print('N4 %s' % ('ALIVE' if alive else ('NOT_APPLICABLE' if res is None else 'DEAD')))
        return 0 if alive else 1
    if mode == 'n4':
        fx_ok = fx()
        if not fx_ok and '--skip-fixtures' not in sys.argv:
            print('fixtures FAIL - N4 not run')
            print('FAIL')
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
        dist5 = collections.Counter()
        nv4 = 0
        cimm = []
        for h, path in sorted(progs.items()):
            b = open(path, 'rb').read()
            words = list(struct.unpack('<%dI' % (len(b) // 4), b))
            u = udcs.get(h)
            u1 = min(u) if u else None
            a = analyse(words, udc=u1)
            dist[a['cls']] += 1
            dist5[a['b5']] += 1
            nv4 += a['v4']
            lines.append('prog %s udc %s class %s v4 %d b5 %s leaves %s control %d sha %s' % (
                h, sorted(u) if u else '-', a['cls'], a['v4'], a['b5'], ','.join(sorted(a['leaves'])), a['control'],
                hashlib.sha256(b).hexdigest()[:16]))
            if a['cls'] == 'C-imm':
                cimm.append((h, words, u1))
        lines.append('T1 PS programs %d classes %s v4 %d; b5 reading %s' % (len(progs), sorted(dist.items()), nv4,
                                                                          sorted(dist5.items())))
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
        ok = fx_ok and tested >= 1 and dead == 0 and dist['T'] >= 1
        lines.append('ALL OK' if ok else 'FAIL')
        text = chr(10).join(lines) + chr(10)
        if '--out' in sys.argv:
            open(sys.argv[sys.argv.index('--out') + 1], 'w', encoding='ascii', newline='\n').write(text)
        print(text[-3000:])
        return 0 if ok else 1
    print('usage: prog|n4|n4prog|fixtures|scccheck')
    return 2


if __name__ == '__main__':
    sys.exit(main())
