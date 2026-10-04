"""F23a (HPP-578, ROADMAP s122 item 483(e)(1)): own word-level parser of RDNA2 shader programs for B7, plus the static
"does the program write EXEC" sign used for B8.

Independent of the emulator decoder except for the DEFINITION of "implemented": the opcode tables are read from the
source text of VectorAluOps.cpp at the main commit given by --commit (git show), i.e. what the decoder looks up.

Walk (mirrors the CONTRACT of Decoder::DecodeProgram, ShaderDecoder.cpp:440-467, written anew): linear sweep from word 0;
direct branches (SOPP 0x02, 0x04-0x09; SOPK 0x1b/0x1c subvector loop) record forward targets; the walk ends at an
S_ENDPGM (SOPP 0x01) whose next word is not a recorded target; no terminal S_ENDPGM -> 'NO_END'; a merged-stage front
program ends at S_SETPC_B64 s[6:7] (DecodeFrontProgram, ShaderDecoder.cpp:421-438) -> 'FRONT_OK'.
Instruction lengths from the RDNA2 encodings (ISA [I]): SOP* 1 (+1 literal when an ssrc is 255; SOPK 0x15
S_SETREG_IMM32_B32 +1), VOP1/VOP2/VOPC 1 (+1 SDWA 0xF9 / DPP16 0xFA / DPP8 0xE9, 0xEA in src0; +1 literal 255; VOP2
MADMK/MADAK/FMAMK/FMAAK 0x20 0x21 0x2c 0x2d 0x37 0x38 +1 literal), VOP3/VOP3P 2 (+1 literal), VINTRP 1, SMEM/MUBUF/
MTBUF/FLAT/DS/EXP 2, MIMG 2 + NSA dwords (bits 2:1).

Unsupported classes (opcode level, = the four SetUnsupported "... opcode is not implemented" sites of VectorAluOps.cpp
and the VOP3 lookup rules LookupVop3Opcode):
  VOP2 op not in VOP2_OPCODE_LIST; VOP1 op not in VOP1_OPCODE_LIST; VOPC op not in VOPC_OPCODE_LIST (also via SDWA/DPP);
  VOP3: op in VOP3_OPCODE_LIST -> ok; op <= 0xff -> VOPC table; 0x100-0x13f -> VOP2 table minus the aliases
  {0x02, 0x20, 0x21, 0x2c, 0x2d, 0x39, 0x3a}; 0x180-0x1ff -> VOP3_ENCODED_VOP1_OPCODE_LIST; else unsupported.
  Extra (outside the four families, reported apart): VOP3P op not in VOP3P_OPCODE_LIST; VINTRP op > 2; DPP8 in src0
  (DecodeScalarSource has no case for 233/234 -> EXIT in the decoder).
Modifier-level rejects (SDWA/DPP/VOP3 abs-neg-opsel-clamp-omod) are NOT modelled here - the real decoder pass
(KYTY_F23A_DECODE) counts them; the two passes are compared on the per-program VALU histogram.

Usage: python gcn_f23a.py --commit dd7c6b33 --t1 | --eboot | --synthetic   (outputs under C:/kyty/f287/f23a/)
"""
import argparse
import collections
import hashlib
import json
import mmap
import os
import re
import struct
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
OUT = 'C:/kyty/f287/f23a/'
GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
GAME = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/'
GCN_ROOT = 'C:/kyty/s288/s4/gcn'
T1_BASE = 'C:/kyty/s288/s7/t1_base.tsv'
NL = chr(10)
TAB = chr(9)


def lock_exit():
    if os.path.exists(LOCK):
        print('LOCK present - exit 3, nothing written')
        sys.exit(3)


# ---------------------------------------------------------------- tables from the decoder source (definition)
def load_tables(commit):
    src = subprocess.run([GIT, '-C', REPO, 'show', commit + ':src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp'],
                         capture_output=True, check=True).stdout.decode('utf-8')
    tabs = {}
    for name in ('VOP2_OPCODE_LIST', 'VOP1_OPCODE_LIST', 'VOP3_ENCODED_VOP1_OPCODE_LIST', 'VOPC_OPCODE_LIST',
                 'VOP3_OPCODE_LIST', 'VOP3P_OPCODE_LIST'):
        m = re.search(r'\b' + name + r'\[\]\s*=\s*\{(.*?)\n\};', src, re.S)
        if not m:
            raise SystemExit('table not found ' + name)
        ents = re.findall(r'\{\s*0x([0-9a-fA-F]+)u\s*,\s*Opcode::(\w+)', m.group(1))
        tabs[name] = {int(h, 16): n for h, n in ents}
    m = re.search(r'bool IsUnsupportedVop3EncodedVop2Alias\(uint32_t opcode\) \{(.*?)\n\}', src, re.S)
    alias_text = m.group(1)
    m2 = re.search(r'bool IsVop2LiteralMadOpcode\(uint32_t opcode\) \{(.*?)\n\}', src, re.S)
    alias = set(int(x, 16) for x in re.findall(r'0x([0-9a-fA-F]+)u', alias_text + m2.group(1)))
    tabs['VOP3_VOP2_ALIAS_UNSUPPORTED'] = alias
    # sanity: the four SetUnsupported "... opcode is not implemented" sites of the VALU families exist in this source
    sites = re.findall(r'SetUnsupported\(inst, Family::(VOP1|VOP2|VOPC|VOP3|VOP3P|VINTRP), opcode, "(\w+) opcode is not implemented"\)', src)
    tabs['_sites'] = sites
    tabs['_sha'] = hashlib.sha256(src.encode('utf-8')).hexdigest()
    return tabs


# ---------------------------------------------------------------- RDNA2 names [I] (for the report only)
def vopc_name(op):
    grp = op >> 5
    sub = op & 0x1f
    x = 'x' if sub & 0x10 else ''
    k = sub & 0xf
    fl = ['f', 'lt', 'eq', 'le', 'gt', 'lg', 'ge', 'o', 'u', 'nge', 'nlg', 'ngt', 'nle', 'neq', 'nlt', 'tru']
    it = ['f', 'lt', 'eq', 'le', 'gt', 'ne', 'ge', 't']
    if grp == 0:
        return 'v_cmp%s_%s_f32' % (x, fl[k])
    if grp == 1:
        return 'v_cmp%s_%s_f64' % (x, fl[k])
    if grp in (4, 5, 6):
        ty = {4: ('i32', 'i16'), 5: ('i64', 'u16'), 6: ('u32', 'f16')}[grp]
        if k < 8:
            return 'v_cmp%s_%s_%s' % (x, it[k], ty[0])
        if k == 8:
            return 'v_cmp%s_class_%s' % (x, {4: 'f32', 5: 'f64', 6: 'f16'}[grp]) if grp != 6 else 'v_cmp%s_f_f16' % x
        if grp == 6:
            return 'v_cmp%s_%s_f16' % (x, fl[k - 8])
        if k == 15:
            return 'v_cmp%s_class_%s' % (x, {4: 'f16', 5: '?'}[grp])
        return 'v_cmp%s_%s_%s' % (x, it[k - 8], ty[1])
    if grp == 7:
        if k < 8:
            return 'v_cmp%s_%s_u64' % (x, it[k])
        return 'v_cmp%s_%s_f16' % (x, fl[k])
    return 'vopc_0x%02x' % op


VOP2_NAMES = {0x01: 'v_cndmask_b32', 0x02: 'v_dot2c_f32_f16', 0x03: 'v_add_f32', 0x04: 'v_sub_f32', 0x05: 'v_subrev_f32',
              0x06: 'v_fmac_legacy_f32', 0x07: 'v_mul_legacy_f32', 0x08: 'v_mul_f32', 0x09: 'v_mul_i32_i24',
              0x0a: 'v_mul_hi_i32_i24', 0x0b: 'v_mul_u32_u24', 0x0c: 'v_mul_hi_u32_u24', 0x0d: 'v_dot4c_i32_i8',
              0x0f: 'v_min_f32', 0x10: 'v_max_f32', 0x11: 'v_min_i32', 0x12: 'v_max_i32', 0x13: 'v_min_u32',
              0x14: 'v_max_u32', 0x16: 'v_lshrrev_b32', 0x18: 'v_ashrrev_i32', 0x1a: 'v_lshlrev_b32', 0x1b: 'v_and_b32',
              0x1c: 'v_or_b32', 0x1d: 'v_xor_b32', 0x1e: 'v_xnor_b32', 0x1f: 'v_mac_f32', 0x20: 'v_madmk_f32',
              0x21: 'v_madak_f32', 0x25: 'v_add_nc_u32', 0x26: 'v_sub_nc_u32', 0x27: 'v_subrev_nc_u32',
              0x28: 'v_add_co_ci_u32', 0x29: 'v_sub_co_ci_u32', 0x2a: 'v_subrev_co_ci_u32', 0x2b: 'v_fmac_f32',
              0x2c: 'v_fmamk_f32', 0x2d: 'v_fmaak_f32', 0x2f: 'v_cvt_pkrtz_f16_f32', 0x32: 'v_add_f16', 0x33: 'v_sub_f16',
              0x34: 'v_subrev_f16', 0x35: 'v_mul_f16', 0x36: 'v_fmac_f16', 0x37: 'v_fmamk_f16', 0x38: 'v_fmaak_f16',
              0x39: 'v_max_f16', 0x3a: 'v_min_f16', 0x3b: 'v_ldexp_f16', 0x3c: 'v_pk_fmac_f16'}
VOP1_NAMES = {0x00: 'v_nop', 0x01: 'v_mov_b32', 0x02: 'v_readfirstlane_b32', 0x03: 'v_cvt_i32_f64', 0x04: 'v_cvt_f64_i32',
              0x05: 'v_cvt_f32_i32', 0x06: 'v_cvt_f32_u32', 0x07: 'v_cvt_u32_f32', 0x08: 'v_cvt_i32_f32',
              0x0a: 'v_cvt_f16_f32', 0x0b: 'v_cvt_f32_f16', 0x0c: 'v_cvt_rpi_i32_f32', 0x0d: 'v_cvt_flr_i32_f32',
              0x0e: 'v_cvt_off_f32_i4', 0x0f: 'v_cvt_f32_f64', 0x10: 'v_cvt_f64_f32', 0x11: 'v_cvt_f32_ubyte0',
              0x12: 'v_cvt_f32_ubyte1', 0x13: 'v_cvt_f32_ubyte2', 0x14: 'v_cvt_f32_ubyte3', 0x15: 'v_cvt_u32_f64',
              0x16: 'v_cvt_f64_u32', 0x17: 'v_trunc_f64', 0x18: 'v_ceil_f64', 0x19: 'v_rndne_f64', 0x1a: 'v_floor_f64',
              0x1b: 'v_pipeflush', 0x20: 'v_fract_f32', 0x21: 'v_trunc_f32', 0x22: 'v_ceil_f32', 0x23: 'v_rndne_f32',
              0x24: 'v_floor_f32', 0x25: 'v_exp_f32', 0x27: 'v_log_f32', 0x2a: 'v_rcp_f32', 0x2b: 'v_rcp_iflag_f32',
              0x2e: 'v_rsq_f32', 0x2f: 'v_rcp_f64', 0x31: 'v_rsq_f64', 0x33: 'v_sqrt_f32', 0x34: 'v_sqrt_f64',
              0x35: 'v_sin_f32', 0x36: 'v_cos_f32', 0x37: 'v_not_b32', 0x38: 'v_bfrev_b32', 0x39: 'v_ffbh_u32',
              0x3a: 'v_ffbl_b32', 0x3b: 'v_ffbh_i32', 0x3c: 'v_frexp_exp_i32_f64', 0x3d: 'v_frexp_mant_f64',
              0x3e: 'v_fract_f64', 0x3f: 'v_frexp_exp_i32_f32', 0x40: 'v_frexp_mant_f32', 0x41: 'v_clrexcp',
              0x42: 'v_movreld_b32', 0x43: 'v_movrels_b32', 0x44: 'v_movrelsd_b32', 0x48: 'v_movrelsd_2_b32',
              0x50: 'v_cvt_f16_u16', 0x51: 'v_cvt_f16_i16', 0x52: 'v_cvt_u16_f16', 0x53: 'v_cvt_i16_f16',
              0x54: 'v_rcp_f16', 0x55: 'v_sqrt_f16', 0x56: 'v_rsq_f16', 0x57: 'v_log_f16', 0x58: 'v_exp_f16',
              0x59: 'v_frexp_mant_f16', 0x5a: 'v_frexp_exp_i16_f16', 0x5b: 'v_floor_f16', 0x5c: 'v_ceil_f16',
              0x5d: 'v_trunc_f16', 0x5e: 'v_rndne_f16', 0x5f: 'v_fract_f16', 0x60: 'v_sin_f16', 0x61: 'v_cos_f16',
              0x62: 'v_sat_pk_u8_i16', 0x63: 'v_cvt_norm_i16_f16', 0x64: 'v_cvt_norm_u16_f16', 0x65: 'v_swap_b32',
              0x68: 'v_swaprel_b32'}
VOP3_NAMES = {0x140: 'v_mad_legacy_f32', 0x141: 'v_mad_f32', 0x142: 'v_mad_i32_i24', 0x143: 'v_mad_u32_u24',
              0x144: 'v_cubeid_f32', 0x145: 'v_cubesc_f32', 0x146: 'v_cubetc_f32', 0x147: 'v_cubema_f32',
              0x148: 'v_bfe_u32', 0x149: 'v_bfe_i32', 0x14a: 'v_bfi_b32', 0x14b: 'v_fma_f32', 0x14c: 'v_fma_f64',
              0x14d: 'v_lerp_u8', 0x14e: 'v_alignbit_b32', 0x14f: 'v_alignbyte_b32', 0x150: 'v_mullit_f32',
              0x151: 'v_min3_f32', 0x152: 'v_min3_i32', 0x153: 'v_min3_u32', 0x154: 'v_max3_f32', 0x155: 'v_max3_i32',
              0x156: 'v_max3_u32', 0x157: 'v_med3_f32', 0x158: 'v_med3_i32', 0x159: 'v_med3_u32', 0x15a: 'v_sad_u8',
              0x15b: 'v_sad_hi_u8', 0x15c: 'v_sad_u16', 0x15d: 'v_sad_u32', 0x15e: 'v_cvt_pk_u8_f32',
              0x15f: 'v_div_fixup_f32', 0x160: 'v_div_fixup_f64', 0x164: 'v_add_f64', 0x165: 'v_mul_f64',
              0x166: 'v_min_f64', 0x167: 'v_max_f64', 0x168: 'v_ldexp_f64', 0x169: 'v_mul_lo_u32', 0x16a: 'v_mul_hi_u32',
              0x16b: 'v_mul_lo_i32', 0x16c: 'v_mul_hi_i32', 0x16d: 'v_div_scale_f32', 0x16e: 'v_div_scale_f64',
              0x16f: 'v_div_fmas_f32', 0x170: 'v_div_fmas_f64', 0x171: 'v_msad_u8', 0x172: 'v_qsad_pk_u16_u8',
              0x173: 'v_mqsad_pk_u16_u8', 0x174: 'v_trig_preop_f64', 0x175: 'v_mqsad_u32_u8', 0x176: 'v_mad_u64_u32',
              0x177: 'v_mad_i64_i32', 0x178: 'v_xor3_b32', 0x2ff: 'v_lshlrev_b64', 0x300: 'v_lshrrev_b64',
              0x301: 'v_ashrrev_i64', 0x303: 'v_add_nc_u16', 0x304: 'v_sub_nc_u16', 0x305: 'v_mul_lo_u16',
              0x307: 'v_lshrrev_b16', 0x308: 'v_ashrrev_i16', 0x309: 'v_max_u16', 0x30a: 'v_max_i16', 0x30b: 'v_min_u16',
              0x30c: 'v_min_i16', 0x30d: 'v_add_nc_i16', 0x30e: 'v_sub_nc_i16', 0x30f: 'v_add_co_u32',
              0x310: 'v_sub_co_u32', 0x311: 'v_pack_b32_f16', 0x312: 'v_cvt_pknorm_i16_f16', 0x313: 'v_cvt_pknorm_u16_f16',
              0x314: 'v_lshlrev_b16', 0x319: 'v_subrev_co_u32', 0x340: 'v_mad_u32_u16', 0x342: 'v_interp_p1ll_f16',
              0x343: 'v_interp_p1lv_f16', 0x344: 'v_perm_b32', 0x345: 'v_xad_u32', 0x346: 'v_lshl_add_u32',
              0x347: 'v_add_lshl_u32', 0x34b: 'v_fma_f16', 0x351: 'v_min3_f16', 0x352: 'v_min3_i16', 0x353: 'v_min3_u16',
              0x354: 'v_max3_f16', 0x355: 'v_max3_i16', 0x356: 'v_max3_u16', 0x357: 'v_med3_f16', 0x358: 'v_med3_i16',
              0x359: 'v_med3_u16', 0x35a: 'v_interp_p2_f16', 0x35e: 'v_mad_i32_i16', 0x35f: 'v_div_fixup_f16',
              0x360: 'v_readlane_b32', 0x361: 'v_writelane_b32', 0x362: 'v_ldexp_f32', 0x363: 'v_bfm_b32',
              0x364: 'v_bcnt_u32_b32', 0x365: 'v_mbcnt_lo_u32_b32', 0x366: 'v_mbcnt_hi_u32_b32',
              0x368: 'v_cvt_pknorm_i16_f32', 0x369: 'v_cvt_pknorm_u16_f32', 0x36a: 'v_cvt_pk_u16_u32',
              0x36b: 'v_cvt_pk_i16_i32', 0x36d: 'v_add3_u32', 0x36f: 'v_lshl_or_b32', 0x371: 'v_and_or_b32',
              0x372: 'v_or3_b32', 0x373: 'v_mad_u16', 0x375: 'v_mad_i16', 0x376: 'v_sub_nc_i32',
              0x377: 'v_permlane16_b32', 0x378: 'v_permlanex16_b32', 0x37f: 'v_add_nc_i32'}
VOP3P_NAMES = {0x00: 'v_pk_mad_i16', 0x01: 'v_pk_mul_lo_u16', 0x02: 'v_pk_add_i16', 0x03: 'v_pk_sub_i16',
               0x04: 'v_pk_lshlrev_b16', 0x05: 'v_pk_lshrrev_b16', 0x06: 'v_pk_ashrrev_i16', 0x07: 'v_pk_max_i16',
               0x08: 'v_pk_min_i16', 0x09: 'v_pk_mad_u16', 0x0a: 'v_pk_add_u16', 0x0b: 'v_pk_sub_u16',
               0x0c: 'v_pk_max_u16', 0x0d: 'v_pk_min_u16', 0x0e: 'v_pk_fma_f16', 0x0f: 'v_pk_add_f16',
               0x10: 'v_pk_mul_f16', 0x11: 'v_pk_min_f16', 0x12: 'v_pk_max_f16', 0x14: 'v_dot2_i32_i16',
               0x15: 'v_dot2_u32_u16', 0x16: 'v_dot4_i32_i8', 0x17: 'v_dot4_u32_u8', 0x18: 'v_dot8_i32_i4',
               0x19: 'v_dot8_u32_u4', 0x20: 'v_fma_mix_f32', 0x21: 'v_fma_mixlo_f16', 0x22: 'v_fma_mixhi_f16'}


def name_of(fam, op):
    if fam == 'VOP2':
        return VOP2_NAMES.get(op, 'vop2_0x%02x' % op)
    if fam == 'VOP1':
        return VOP1_NAMES.get(op, 'vop1_0x%02x' % op)
    if fam == 'VOPC':
        return vopc_name(op)
    if fam == 'VOP3':
        if op <= 0xff:
            return vopc_name(op) + '_e64'
        if 0x100 <= op <= 0x13f:
            return VOP2_NAMES.get(op - 0x100, 'vop2_0x%02x' % (op - 0x100)) + '_e64'
        if 0x180 <= op <= 0x1ff:
            return VOP1_NAMES.get(op - 0x180, 'vop1_0x%02x' % (op - 0x180)) + '_e64'
        return VOP3_NAMES.get(op, 'vop3_0x%03x' % op)
    if fam == 'VOP3P':
        return VOP3P_NAMES.get(op, 'vop3p_0x%02x' % op)
    return '%s_0x%x' % (fam, op)


# ---------------------------------------------------------------- walk
SAVEEXEC_SOP1 = {0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x37, 0x38, 0x39, 0x3a,
                 0x3c, 0x3d, 0x3e, 0x3f, 0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47}
EXEC_REGS = (126, 127)


def is_cmpx(op):
    return op <= 0xff and (op & 0x10) != 0 and (op >> 5) in (0, 1, 4, 5, 6, 7)


def walk(words):
    """Returns (instructions, status). instruction = (pc_word, fam, op, size, extra dict)."""
    n = len(words)
    i = 0
    targets = set()
    out = []
    while i < n:
        w = words[i]
        size = 1
        ex = {}
        if (w & 0x80000000) == 0:
            sel = (w >> 25) & 0x3f
            if sel == 0x3e:
                fam, op = 'VOPC', (w >> 17) & 0xff
            elif sel == 0x3f:
                fam, op = 'VOP1', (w >> 9) & 0xff
            else:
                fam, op = 'VOP2', sel
            s0 = w & 0x1ff
            if s0 in (0xf9, 0xfa, 0xe9, 0xea):
                size += 1
                ex['mod'] = {0xf9: 'sdwa', 0xfa: 'dpp16', 0xe9: 'dpp8', 0xea: 'dpp8fi'}[s0]
            elif s0 == 255:
                size += 1
            if fam == 'VOP2' and op in (0x20, 0x21, 0x2c, 0x2d, 0x37, 0x38):
                size += 1
            if fam == 'VOP1' and op == 0x02:
                ex['sdst'] = (w >> 17) & 0xff
        elif (w & 0xc0000000) == 0x80000000:
            op7 = (w >> 23) & 0x7f
            if op7 == 0x7d:
                fam, op = 'SOP1', (w >> 8) & 0xff
                if (w & 0xff) == 255:
                    size += 1
                ex['sdst'] = (w >> 16) & 0x7f
            elif op7 == 0x7e:
                fam, op = 'SOPC', (w >> 16) & 0x7f
                if (w & 0xff) == 255 or ((w >> 8) & 0xff) == 255:
                    size += 1
            elif op7 == 0x7f:
                fam, op = 'SOPP', (w >> 16) & 0x7f
                simm = w & 0xffff
                if simm & 0x8000:
                    simm -= 0x10000
                if op in (0x02, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09):
                    t = i + 1 + simm
                    ex['target'] = t
                    if t > i:
                        targets.add(t)
            elif op7 >= 0x60:
                fam, op = 'SOPK', (w >> 23) & 0x1f
                ex['sdst'] = (w >> 16) & 0x7f
                if op == 0x15:
                    size += 1
                if op in (0x1b, 0x1c):
                    simm = w & 0xffff
                    if simm & 0x8000:
                        simm -= 0x10000
                    t = i + 1 + simm
                    ex['target'] = t
                    if t > i:
                        targets.add(t)
            else:
                fam, op = 'SOP2', op7
                if (w & 0xff) == 255 or ((w >> 8) & 0xff) == 255:
                    size += 1
                ex['sdst'] = (w >> 16) & 0x7f
        else:
            enc = w >> 26
            fam = {0x32: 'VINTRP', 0x33: 'VOP3P', 0x35: 'VOP3', 0x36: 'DS', 0x37: 'FLAT', 0x38: 'MUBUF',
                   0x3a: 'MTBUF', 0x3c: 'MIMG', 0x3d: 'SMEM', 0x3e: 'EXP'}.get(enc)
            if fam is None:
                return out, 'BAD_FAMILY@%d' % i
            op = None
            if fam == 'VINTRP':
                op = (w >> 16) & 0x3
            elif fam in ('VOP3', 'VOP3P'):
                size = 2
                if i + 1 >= n:
                    return out, 'TRUNC@%d' % i
                w1 = words[i + 1]
                if 255 in (w1 & 0x1ff, (w1 >> 9) & 0x1ff, (w1 >> 18) & 0x1ff):
                    size = 3
                if fam == 'VOP3':
                    op = (w >> 16) & 0x3ff
                    ex['vdst'] = w & 0xff
                else:
                    op = (w >> 16) & 0x7f
            elif fam == 'MIMG':
                size = 2 + ((w >> 1) & 3)
                op = ((w >> 18) & 0x7f) | ((w & 1) << 7)
            else:
                size = 2
                if fam == 'SMEM':
                    op = (w >> 18) & 0xff
        out.append((i, fam, op, size, ex))
        i += size
        if fam == 'SOPP' and op == 0x01 and i not in targets:
            return out, 'OK'
        if fam == 'SOP1' and op == 0x20 and (w & 0xff) == 6 and not any(t >= i for t in targets):
            # S_SETPC_B64 s[6:7]: end of a merged-stage front program (DecodeFrontProgram, ShaderDecoder.cpp:421-438)
            return out, 'FRONT_OK'
    return out, 'NO_END'


def classify(instrs, tabs):
    """Opcode-level unsupported VALU instructions and the EXEC-writer sign."""
    v2 = tabs['VOP2_OPCODE_LIST']
    v1 = tabs['VOP1_OPCODE_LIST']
    v31 = tabs['VOP3_ENCODED_VOP1_OPCODE_LIST']
    vc = tabs['VOPC_OPCODE_LIST']
    v3 = tabs['VOP3_OPCODE_LIST']
    v3p = tabs['VOP3P_OPCODE_LIST']
    alias = tabs['VOP3_VOP2_ALIAS_UNSUPPORTED']
    unsup = []
    extra = []
    hist = collections.Counter()
    exec_writes = []
    for (pc, fam, op, size, ex) in instrs:
        if fam in ('VOP1', 'VOP2', 'VOPC', 'VOP3', 'VOP3P', 'VINTRP'):
            hist[(fam, op)] += 1
        bad = False
        if fam == 'VOP2':
            bad = op not in v2
        elif fam == 'VOP1':
            bad = op not in v1
        elif fam == 'VOPC':
            bad = op not in vc
        elif fam == 'VOP3':
            if op in v3:
                bad = False
            elif op <= 0xff:
                bad = op not in vc
            elif 0x100 <= op <= 0x13f:
                bad = (op - 0x100) in alias or (op - 0x100) not in v2
            elif 0x180 <= op <= 0x1ff:
                bad = (op - 0x180) not in v31
            else:
                bad = True
        if bad:
            unsup.append((pc, fam, op, name_of(fam, op)))
        if fam == 'VOP3P' and op not in v3p:
            extra.append((pc, 'VOP3P', op, name_of('VOP3P', op)))
        if fam == 'VINTRP' and op > 2:
            extra.append((pc, 'VINTRP', op, 'vintrp_%d' % op))
        if ex.get('mod') in ('dpp8', 'dpp8fi'):
            extra.append((pc, fam, op, 'DPP8 src0 (decoder EXIT)'))
        # EXEC writers
        if fam == 'SOP1' and (op in SAVEEXEC_SOP1 or ex.get('sdst') in EXEC_REGS):
            exec_writes.append((pc, fam, op))
        elif fam in ('SOP2', 'SOPK') and ex.get('sdst') in EXEC_REGS:
            exec_writes.append((pc, fam, op))
        elif fam == 'VOPC' and is_cmpx(op):
            exec_writes.append((pc, fam, op))
        elif fam == 'VOP3' and op <= 0xff and (is_cmpx(op) or ex.get('vdst') in EXEC_REGS):
            exec_writes.append((pc, fam, op))
        elif fam == 'VOP3' and op in (0x360, 0x30f, 0x310, 0x319, 0x176, 0x177) and ex.get('vdst') in EXEC_REGS and op == 0x360:
            exec_writes.append((pc, fam, op))
        elif fam == 'VOP1' and op == 0x02 and ex.get('sdst') in EXEC_REGS:
            exec_writes.append((pc, fam, op))
    return unsup, extra, hist, exec_writes


def words_of(b):
    return list(struct.unpack_from('<%dI' % (len(b) // 4), b, 0))


# ---------------------------------------------------------------- sources
def t1_programs():
    """Unique T1 programs: GCN dumps of the G arms (raw words), keyed by hash16, with stages from the base."""
    import csv
    rows = list(csv.DictReader(open(T1_BASE, encoding='utf-8'), delimiter=TAB))
    stages = collections.defaultdict(set)
    for r in rows:
        stages[r['hash16']].add(r['stage'])
    progs = {}
    for arm in sorted(os.listdir(GCN_ROOT)):
        d = os.path.join(GCN_ROOT, arm)
        for fn in sorted(os.listdir(d)):
            m = re.match(r'^(vs|ps|cs|ms)_([0-9a-f]{16})\.bin$', fn)
            if not m:
                continue
            b = open(os.path.join(d, fn), 'rb').read()
            h = m.group(2)
            sha = hashlib.sha256(b).hexdigest()
            if h in progs:
                if progs[h]['sha'] != sha:
                    progs[h]['conflict'] = True
                progs[h]['arms'].add(arm)
                continue
            progs[h] = dict(hash=h, stage=m.group(1), path=os.path.join(d, fn).replace(os.sep, '/'), sha=sha,
                            words=words_of(b), arms={arm}, base_stages=sorted(stages.get(h, [])))
    return progs, stages


MAGIC = bytes([0x7F, 0x45, 0x4C, 0x46, 2, 1, 1])


def eboot_programs():
    """AMDGPU ELFs (e_machine 0xE0) inside eboot.bin; code = section .shader_text (or .text); key = XXH3-64(.text) (method of
    F11a t1scan_f11a.py elf_programs, re-written)."""
    import xxhash
    path = GAME + 'eboot.bin'
    f = open(path, 'rb')
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    progs = collections.OrderedDict()
    n_elf = 0
    e = mm.find(MAGIC)
    while e != -1:
        if struct.unpack_from('<H', mm, e + 18)[0] == 0xE0:
            try:
                shoff = struct.unpack_from('<Q', mm, e + 0x28)[0]
                shentsize, shnum, shstrndx = struct.unpack_from('<HHH', mm, e + 0x3A)
                secs = []
                for k in range(shnum):
                    b = e + shoff + k * shentsize
                    name, typ, flags, addr, off, size = struct.unpack_from('<IIQQQQ', mm, b)
                    secs.append((name, off, size))
                stroff = e + secs[shstrndx][1]
                for name, off, size in secs:
                    end = mm.find(bytes([0]), stroff + name)
                    if mm[stroff + name:end] in (b'.text', b'.shader_text'):
                        code = bytes(mm[e + off:e + off + size])
                        n_elf += 1
                        h = '%016x' % xxhash.xxh3_64_intdigest(code)
                        if h not in progs:
                            progs[h] = dict(hash=h, elf=e, code=code)
            except (struct.error, IndexError):
                pass
        e = mm.find(MAGIC, e + 1)
    return progs, n_elf


# ---------------------------------------------------------------- main
def run(progs, tabs, tag):
    rows = []
    agg = collections.Counter()
    for h, p in progs.items():
        lock_exit()
        words = p['words'] if 'words' in p else words_of(p['code'])
        instrs, status = walk(words)
        unsup, extra, hist, exw = classify(instrs, tabs)
        end_word = instrs[-1][0] + instrs[-1][3] if instrs else 0
        rows.append(dict(hash=h, stage=p.get('stage', '?'), status=status, words=len(words), walked=end_word,
                         n_inst=len(instrs), unsup=unsup, extra=extra, exec_writes=len(exw),
                         hist={'%s:%x' % k: v for k, v in sorted(hist.items())}))
        agg[status] += 1
    return rows, agg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--commit', required=True)
    ap.add_argument('--t1', action='store_true')
    ap.add_argument('--eboot', action='store_true')
    ap.add_argument('--synthetic', action='store_true')
    a = ap.parse_args()
    lock_exit()
    tabs = load_tables(a.commit)
    print('tables from', a.commit, 'VectorAluOps.cpp sha256', tabs['_sha'][:16], 'sizes',
          {k: len(v) for k, v in tabs.items() if not k.startswith('_')}, 'not-implemented sites', tabs['_sites'])
    if a.synthetic:
        return synthetic(tabs)
    if a.t1:
        progs, stages = t1_programs()
        print('T1 dumps: unique hashes', len(progs), 'conflicts', sum(1 for p in progs.values() if p.get('conflict')),
              'base hashes', len(stages))
        rows, agg = run(progs, tabs, 't1')
        name = 't1'
    else:
        progs, n_elf = eboot_programs()
        print('eboot.bin: AMDGPU ELF .text', n_elf, 'unique', len(progs), 'sha256',
              hashlib.sha256(open(GAME + 'eboot.bin', 'rb').read()).hexdigest()[:16])
        t1p, t1stages = t1_programs()
        # calibration (form of F11a): a T1 dump = the first len(dump) words of the eboot .text with the same hash16
        cal = collections.Counter()
        for h, tp in t1p.items():
            if h not in progs:
                cal['dump_not_in_eboot'] += 1
                continue
            ew = words_of(progs[h]['code'])
            cal['equal' if ew[:len(tp['words'])] == tp['words'] else 'DIFF'] += 1
        print('calibration T1 dumps vs eboot .text prefix:', dict(cal))
        print('T1 base hashes in eboot:', sum(1 for h in t1stages if h in progs), 'of', len(t1stages))
        for h, p in progs.items():
            p['stage'] = ','.join(sorted(t1stages[h])) if h in t1stages else '?'
            p['in_t1'] = h in t1stages
        rows, agg = run(progs, tabs, 'eboot')
        for r in rows:
            r['in_t1'] = progs[r['hash']]['in_t1']
        name = 'eboot'
        un = [r for r in rows if r['unsup']]
        print('eboot programs with unsupported: in T1', sum(1 for r in un if r['in_t1']), 'outside T1',
              sum(1 for r in un if not r['in_t1']))
    lock_exit()
    with open(OUT + 'scan_%s.jsonl' % name, 'w', encoding='utf-8', newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + NL)
    print('walk status', dict(agg))
    n_un = [r for r in rows if r['unsup']]
    n_ex = [r for r in rows if r['extra']]
    print('programs with opcode-level unsupported VOP1/VOP2/VOP3/VOPC:', len(n_un), 'instructions',
          sum(len(r['unsup']) for r in rows))
    byop = collections.Counter((u[1], u[2], u[3]) for r in rows for u in r['unsup'])
    for (fam, op, nm), c in byop.most_common():
        progs_n = sum(1 for r in rows if any(u[1] == fam and u[2] == op for u in r['unsup']))
        print('  UNSUP %s 0x%x %s: %d instr in %d programs' % (fam, op, nm, c, progs_n))
    print('programs with extra (VOP3P / VINTRP / DPP8):', len(n_ex), collections.Counter(e[3] for r in rows for e in r['extra']))
    st = collections.Counter((r['stage'], r['exec_writes'] > 0) for r in rows)
    print('EXEC writers by stage (stage, writes_exec): count', dict(sorted(st.items())))
    tot = collections.Counter()
    for r in rows:
        for k, v in r['hist'].items():
            tot[k] += v
    print('VALU histogram: distinct (family:op)', len(tot), 'instructions', sum(tot.values()))
    for k in ('VOP2:8', 'VOP3:141', 'VOP2:1', 'VOP3:14b'):
        print('  control', k, name_of(k.split(':')[0], int(k.split(':')[1], 16)), tot.get(k, 0), 'instr in',
              sum(1 for r in rows if k in r['hist']), 'programs')
    return 0


def synthetic(tabs):
    """Zero / positive controls on hand-made programs (words in the RDNA2 encodings)."""
    endpgm = 0xBF810000
    v_mul_f32 = (0x08 << 25) | (1 << 17) | (2 << 9) | 256 | 3          # v_mul_f32 v1, v3, v2 (VOP2)
    v_mul_legacy = (0x07 << 25) | (1 << 17) | (2 << 9) | 256 | 3       # VOP2 0x07
    v_fmac_legacy = (0x06 << 25) | (1 << 17) | (2 << 9) | 256 | 3      # VOP2 0x06
    vop3_mul_legacy = [(0x35 << 26) | ((0x100 + 0x07) << 16) | 1, (256 + 3) | ((256 + 2) << 9)]
    s_and_saveexec = 0xBE80247E | 0  # s_and_saveexec_b64 s[0:1], vcc? (SOP1 op 0x24, ssrc 0x7e)
    cases = {
        'zero_clean': [v_mul_f32, v_mul_f32, endpgm],
        'pos_vop2_mul_legacy': [v_mul_f32, v_mul_legacy, endpgm],
        'pos_vop2_fmac_legacy': [v_fmac_legacy, endpgm],
        'pos_vop3_mul_legacy': vop3_mul_legacy + [endpgm],
        'pos_after_branch_dead': [0xBF820001, v_mul_legacy, endpgm],       # s_branch over it: still decoded
        'zero_after_endpgm': [v_mul_f32, endpgm, v_mul_legacy],            # after the terminal S_ENDPGM: not decoded
        'pos_fwd_target_after_endpgm': [0xBF850001, endpgm, v_mul_legacy, endpgm],  # cbranch_scc1 past endpgm
        'exec_writer': [s_and_saveexec, v_mul_f32, endpgm],
    }
    ok = True
    for k, ws in cases.items():
        instrs, status = walk(ws)
        unsup, extra, hist, exw = classify(instrs, tabs)
        expect_un = k.startswith('pos_')
        good = (len(unsup) > 0) == expect_un and status == 'OK'
        if k == 'exec_writer':
            good = good and len(exw) == 1
        ok &= good
        print('%-28s status %-6s unsup %s exec_writes %d -> %s' % (k, status, [(u[1], hex(u[2]), u[3]) for u in unsup],
                                                                  len(exw), 'ok' if good else 'FAIL'))
    print('ALL OK' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
