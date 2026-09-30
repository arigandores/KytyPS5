# Minimal RDNA2 (gfx10) disassembler: names scalar formats from the ISA opcode tables
# (RDNA2 ISA guide, 13.1 Scalar ALU and Control Formats, 13.2 SMEM); vector formats by encoding and length.
import sys, struct
SOP2 = {0:'s_add_u32',1:'s_sub_u32',2:'s_add_i32',3:'s_sub_i32',4:'s_addc_u32',5:'s_subb_u32',6:'s_min_i32',7:'s_min_u32',8:'s_max_i32',9:'s_max_u32',10:'s_cselect_b32',11:'s_cselect_b64',14:'s_and_b32',15:'s_and_b64',16:'s_or_b32',17:'s_or_b64',18:'s_xor_b32',19:'s_xor_b64',20:'s_andn2_b32',21:'s_andn2_b64',22:'s_orn2_b32',23:'s_orn2_b64',24:'s_nand_b32',25:'s_nand_b64',26:'s_nor_b32',27:'s_nor_b64',28:'s_xnor_b32',29:'s_xnor_b64',30:'s_lshl_b32',31:'s_lshl_b64',32:'s_lshr_b32',33:'s_lshr_b64',34:'s_ashr_i32',35:'s_ashr_i64',36:'s_bfm_b32',37:'s_bfm_b64',38:'s_mul_i32',39:'s_bfe_u32',40:'s_bfe_i32',41:'s_bfe_u64',42:'s_bfe_i64',44:'s_absdiff_i32',46:'s_lshl1_add_u32',47:'s_lshl2_add_u32',48:'s_lshl3_add_u32',49:'s_lshl4_add_u32',50:'s_pack_ll_b32_b16',51:'s_pack_lh_b32_b16',52:'s_pack_hh_b32_b16',53:'s_mul_hi_u32',54:'s_mul_hi_i32'}
SOPK = {0:'s_movk_i32',1:'s_version',2:'s_cmovk_i32',3:'s_cmpk_eq_i32',4:'s_cmpk_lg_i32',5:'s_cmpk_gt_i32',6:'s_cmpk_ge_i32',7:'s_cmpk_lt_i32',8:'s_cmpk_le_i32',9:'s_cmpk_eq_u32',10:'s_cmpk_lg_u32',11:'s_cmpk_gt_u32',12:'s_cmpk_ge_u32',13:'s_cmpk_lt_u32',14:'s_cmpk_le_u32',15:'s_addk_i32',16:'s_mulk_i32',18:'s_getreg_b32',19:'s_setreg_b32',21:'s_setreg_imm32_b32',22:'s_call_b64',23:'s_waitcnt_vscnt',24:'s_waitcnt_vmcnt',25:'s_waitcnt_expcnt',26:'s_waitcnt_lgkmcnt',27:'s_subvector_loop_begin',28:'s_subvector_loop_end'}
SOP1 = {3:'s_mov_b32',4:'s_mov_b64',5:'s_cmov_b32',6:'s_cmov_b64',7:'s_not_b32',8:'s_not_b64',9:'s_wqm_b32',10:'s_wqm_b64',11:'s_brev_b32',12:'s_brev_b64',13:'s_bcnt0_i32_b32',14:'s_bcnt0_i32_b64',15:'s_bcnt1_i32_b32',16:'s_bcnt1_i32_b64',17:'s_ff0_i32_b32',18:'s_ff0_i32_b64',19:'s_ff1_i32_b32',20:'s_ff1_i32_b64',21:'s_flbit_i32_b32',22:'s_flbit_i32_b64',23:'s_flbit_i32',24:'s_flbit_i32_i64',25:'s_sext_i32_i8',26:'s_sext_i32_i16',27:'s_bitset0_b32',28:'s_bitset0_b64',29:'s_bitset1_b32',30:'s_bitset1_b64',31:'s_getpc_b64',32:'s_setpc_b64',33:'s_swappc_b64',34:'s_rfe_b64',36:'s_and_saveexec_b64',37:'s_or_saveexec_b64',38:'s_xor_saveexec_b64',39:'s_andn2_saveexec_b64',40:'s_orn2_saveexec_b64',41:'s_nand_saveexec_b64',42:'s_nor_saveexec_b64',43:'s_xnor_saveexec_b64',44:'s_quadmask_b32',45:'s_quadmask_b64',46:'s_movrels_b32',47:'s_movrels_b64',48:'s_movreld_b32',49:'s_movreld_b64',52:'s_abs_i32',55:'s_andn1_saveexec_b64',56:'s_orn1_saveexec_b64',57:'s_andn1_wrexec_b64',58:'s_andn2_wrexec_b64',59:'s_bitreplicate_b64_b32',60:'s_and_saveexec_b32',61:'s_or_saveexec_b32',62:'s_xor_saveexec_b32',63:'s_andn2_saveexec_b32',64:'s_orn2_saveexec_b32',65:'s_nand_saveexec_b32',66:'s_nor_saveexec_b32',67:'s_xnor_saveexec_b32',68:'s_andn1_saveexec_b32',69:'s_orn1_saveexec_b32',70:'s_andn1_wrexec_b32',71:'s_andn2_wrexec_b32',73:'s_movrelsd_2_b32'}
SOPC = {0:'s_cmp_eq_i32',1:'s_cmp_lg_i32',2:'s_cmp_gt_i32',3:'s_cmp_ge_i32',4:'s_cmp_lt_i32',5:'s_cmp_le_i32',6:'s_cmp_eq_u32',7:'s_cmp_lg_u32',8:'s_cmp_gt_u32',9:'s_cmp_ge_u32',10:'s_cmp_lt_u32',11:'s_cmp_le_u32',12:'s_bitcmp0_b32',13:'s_bitcmp1_b32',14:'s_bitcmp0_b64',15:'s_bitcmp1_b64',18:'s_cmp_eq_u64',19:'s_cmp_lg_u64'}
SOPP = {0:'s_nop',1:'s_endpgm',2:'s_branch',3:'s_wakeup',4:'s_cbranch_scc0',5:'s_cbranch_scc1',6:'s_cbranch_vccz',7:'s_cbranch_vccnz',8:'s_cbranch_execz',9:'s_cbranch_execnz',10:'s_barrier',11:'s_setkill',12:'s_waitcnt',13:'s_sethalt',14:'s_sleep',15:'s_setprio',16:'s_sendmsg',17:'s_sendmsghalt',18:'s_trap',19:'s_icache_inv',27:'s_endpgm_saved',31:'s_code_end',32:'s_inst_prefetch',33:'s_clause',35:'s_waitcnt_depctr',36:'s_round_mode',37:'s_denorm_mode'}
SMEM = {0:'s_load_dword',1:'s_load_dwordx2',2:'s_load_dwordx4',3:'s_load_dwordx8',4:'s_load_dwordx16',8:'s_buffer_load_dword',9:'s_buffer_load_dwordx2',10:'s_buffer_load_dwordx4',11:'s_buffer_load_dwordx8',12:'s_buffer_load_dwordx16',31:'s_gl1_inv',32:'s_dcache_inv',36:'s_memtime',37:'s_memrealtime'}

def sop(v, lit):
    if v < 106: return 's%d' % v
    n = {106:'vcc_lo',107:'vcc_hi',124:'m0',125:'null',126:'exec_lo',127:'exec_hi',253:'scc',255:'lit(0x%x)' % (lit if lit is not None else 0)}
    if v in n: return n[v]
    if 128 <= v <= 192: return str(v - 128)
    if 193 <= v <= 208: return str(-(v - 192))
    fl = {240:'0.5',241:'-0.5',242:'1.0',243:'-1.0',244:'2.0',245:'-2.0',246:'4.0',247:'-4.0',248:'1/(2pi)'}
    if v in fl: return fl[v]
    if 256 <= v <= 511: return 'v%d' % (v - 256)
    return '?%d' % v

def dis(words):
    out = []
    i = 0
    n = len(words)
    while i < n:
        w = words[i]
        pc = i * 4
        size = 1
        text = ''
        top9 = w >> 23
        if top9 == 0x17D:  # SOP1
            op = (w >> 8) & 0xff; s0 = w & 0xff; d = (w >> 16) & 0x7f
            lit = words[i + 1] if s0 == 255 and i + 1 < n else None
            size += 1 if s0 == 255 else 0
            text = '%s %s, %s' % (SOP1.get(op, 'sop1_%d' % op), sop(d, None), sop(s0, lit))
        elif top9 == 0x17E:  # SOPC
            op = (w >> 16) & 0x7f; s0 = w & 0xff; s1 = (w >> 8) & 0xff
            lit = words[i + 1] if 255 in (s0, s1) and i + 1 < n else None
            size += 1 if 255 in (s0, s1) else 0
            text = '%s %s, %s' % (SOPC.get(op, 'sopc_%d' % op), sop(s0, lit), sop(s1, lit))
        elif top9 == 0x17F:  # SOPP
            op = (w >> 16) & 0x7f; imm = w & 0xffff
            simm = imm - 0x10000 if imm & 0x8000 else imm
            name = SOPP.get(op, 'sopp_%d' % op)
            if name in ('s_branch',) or name.startswith('s_cbranch'):
                text = '%s 0x%x' % (name, pc + 4 + simm * 4)
            else:
                text = '%s 0x%x' % (name, imm)
        elif (w >> 28) == 0xB:  # SOPK
            op = (w >> 23) & 0x1f; d = (w >> 16) & 0x7f; imm = w & 0xffff
            simm = imm - 0x10000 if imm & 0x8000 else imm
            name = SOPK.get(op, 'sopk_%d' % op)
            if op == 21: size += 1
            if name == 's_call_b64':
                text = '%s %s, 0x%x' % (name, sop(d, None), pc + 4 + simm * 4)
            else:
                text = '%s %s, 0x%x' % (name, sop(d, None), imm)
        elif (w >> 30) == 0x2:  # SOP2
            op = (w >> 23) & 0x7f; d = (w >> 16) & 0x7f; s0 = w & 0xff; s1 = (w >> 8) & 0xff
            lit = words[i + 1] if 255 in (s0, s1) and i + 1 < n else None
            size += 1 if 255 in (s0, s1) else 0
            text = '%s %s, %s, %s' % (SOP2.get(op, 'sop2_%d' % op), sop(d, None), sop(s0, lit), sop(s1, lit))
        elif (w >> 26) == 0x3D:  # SMEM
            w1 = words[i + 1] if i + 1 < n else 0
            op = (w >> 18) & 0xff; sdata = (w >> 6) & 0x7f; sbase = (w & 0x3f) * 2
            off = w1 & 0x1fffff; soff = (w1 >> 25) & 0x7f
            size = 2
            text = '%s s%d, s[%d:%d], off=0x%x soff=%s' % (SMEM.get(op, 'smem_%d' % op), sdata, sbase, sbase + 1, off, sop(soff, None))
        elif (w >> 25) == 0x3E:  # VOPC
            op = (w >> 17) & 0xff; s0 = w & 0x1ff; v1 = (w >> 9) & 0xff
            lit = words[i + 1] if s0 == 255 and i + 1 < n else None
            size += 1 if s0 == 255 else 0
            if s0 in (0xF9, 0xFA, 0xE9): size += 1
            text = 'vopc_%d(0x%x) vcc, %s, v%d' % (op, op, sop(s0, lit), v1)
        elif (w >> 25) == 0x3F:  # VOP1
            op = (w >> 9) & 0xff; s0 = w & 0x1ff; d = (w >> 17) & 0xff
            lit = words[i + 1] if s0 == 255 and i + 1 < n else None
            size += 1 if s0 == 255 else 0
            if s0 in (0xF9, 0xFA, 0xE9): size += 1
            text = 'vop1_%d v%d, %s' % (op, d, sop(s0, lit))
        elif (w >> 31) == 0:  # VOP2
            op = (w >> 25) & 0x3f; s0 = w & 0x1ff; v1 = (w >> 9) & 0xff; d = (w >> 17) & 0xff
            lit = words[i + 1] if (s0 == 255 or op in (0x2c, 0x2d, 0x37, 0x38)) and i + 1 < n else None
            size += 1 if (s0 == 255 or op in (0x2c, 0x2d, 0x37, 0x38)) else 0
            if s0 in (0xF9, 0xFA, 0xE9): size += 1
            text = 'vop2_%d v%d, %s, v%d' % (op, d, sop(s0, lit), v1)
        else:
            enc = w >> 26
            names = {0x35:'vop3', 0x33:'vop3p', 0x32:'vintrp', 0x36:'ds', 0x38:'mubuf', 0x3a:'mtbuf', 0x3c:'mimg', 0x3e:'exp', 0x37:'flat'}
            nm = names.get(enc, 'enc_%x' % enc)
            if nm == 'vintrp':
                size = 1
            else:
                size = 2
            if nm in ('vop3', 'vop3p') and i + 1 < n:
                w1 = words[i + 1]
                srcs = [w1 & 0x1ff, (w1 >> 9) & 0x1ff, (w1 >> 18) & 0x1ff]
                if 255 in srcs: size = 3
                op = (w >> 16) & 0x3ff
                d = w & 0xff
                sdst = (w >> 8) & 0x7f
                lit = words[i + 2] if size == 3 else None
                text = '%s_%d(0x%x) d=v%d/sdst=%s, %s' % (nm, op, op, d, sop(sdst, None), ', '.join(sop(x, lit) for x in srcs))
            elif nm == 'mimg' and i + 1 < n:
                nsa = (w >> 1) & 3
                size = 2 + nsa
                text = 'mimg op=%d' % ((w >> 18) & 0x7f | ((w >> 25) & 1) << 7)
            else:
                text = nm
        out.append((pc, words[i:i + size], text))
        i += size
    return out

if __name__ == '__main__':
    data = open(sys.argv[1], 'rb').read()
    words = list(struct.unpack('<%dI' % (len(data) // 4), data))
    lo = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3], 0) if len(sys.argv) > 3 else len(words) * 4
    for pc, ws, text in dis(words):
        if lo <= pc < hi:
            print('%06x: %-28s %s' % (pc, ' '.join('%08x' % x for x in ws), text))
