# F12a (HPP-474): how program 380bb9d636390bae feeds IMAGE_BVH_INTERSECT_RAY and how it decodes the
# hit triangle afterwards. Reads the disassembly C:/kyty/f287/f3a/asm_380b.txt (emulator decoder output,
# F3a), checks every line it relies on by exact text (line number + pc + text), recomputes the per-type
# vertex offsets of the hit-triangle decode at pc 0xcd0..0xd84 and compares them with the GPURT /
# RRA vertex mapping of node types 0..3. Prints ALL OK only if every check passes.
import sys

ASM = 'C:/kyty/f287/f3a/asm_380b.txt'
lines = open(ASM, 'r', encoding='utf-8').read().split(chr(10))

ok = True


def need(lineno, text):
    # lineno is 1-based; the line must start with the exact text
    global ok
    got = lines[lineno - 1]
    good = got.startswith(text)
    print('%s %s:%d  %s' % ('OK  ' if good else 'FAIL', 'asm_380b.txt', lineno, got[:150]))
    ok &= good


print('== (a) the three IMAGE_BVH_INTERSECT_RAY sites')
need(241, '0x00000474: IMAGE_BVH_INTERSECT_RAY v0, v0, s40, s0')
need(280, '0x0000052c: IMAGE_BVH_INTERSECT_RAY v0, v0, s40, s0')
need(458, '0x000008f8: IMAGE_BVH_INTERSECT_RAY v0, v0, s56, s0')

print('== (b) box sites 0x52c / 0x8f8 take only types 4..6: (type - 4) <= 2 unsigned')
need(152, '0x000002c4: S_AND_B32 vcc_lo, s42, 7')
need(153, '0x000002c8: S_ADD_I32 vcc_lo, vcc_lo, -4')
need(154, '0x000002cc: S_CMP_LE_U32 vcc_lo, 2')
need(155, '0x000002d0: S_CBRANCH_SCC1 0x000008d8')
need(456, '0x000008f0: V_MOV_B32 v0, s42')
need(217, '0x0000040c: S_AND_B32 vcc_lo, s32, 7')
need(218, '0x00000410: S_ADD_I32 vcc_lo, vcc_lo, -4')
need(219, '0x00000414: S_CMP_LE_U32 vcc_lo, 2')
need(220, '0x00000418: S_CBRANCH_SCC1 0x0000050c')
need(278, '0x00000524: V_MOV_B32 v0, s32')

print('== (c) leaf site 0x474: pointer = dword loaded from the leaf list in BLAS memory, no arithmetic')
need(189, '0x00000380: S_LSHL_B64 s20, s32, 3')
need(225, '0x0000042c: S_AND_B32 vcc_lo, s32, -5')
need(227, '0x00000434: S_BUFFER_LOAD_DWORD s26, s20, vcc_lo')
need(229, '0x00000440: S_AND_B32 vcc_lo, s26, 7')
need(230, '0x00000444: S_CMP_LG_U32 7, vcc_lo')
need(231, '0x00000448: S_CBRANCH_SCC0 0x00000504')
need(234, '0x00000454: S_BUFFER_LOAD_DWORD s27, s20, vcc_lo')
need(236, '0x00000460: V_MOV_B32 v0, s26')
need(263, '0x000004e4: S_CMP_LT_I32 s27, 0')
need(268, '0x000004f8: S_BUFFER_LOAD_DWORDX2 s26, s20, vcc_lo')
need(269, '0x00000500: S_BRANCH 0x0000045c')
# no instruction between the load of s26 (0x434 / 0x4f8) and the call writes s26 or v0 except V_MOV v0, s26
writes = []
for k in list(range(228, 241)):
    t = lines[k - 1]
    ins = t.split(': ', 1)[1] if ': ' in t else t
    dst = ins.split(' ', 2)[1].rstrip(',') if len(ins.split(' ')) > 1 else ''
    if dst in ('s26', 'v0', 's26:s27'):
        writes.append((k, t[:90]))
print('   writes of s26/v0 between the load and the call:', writes)
ok &= writes == [(236, lines[235][:90])]

print('== (d) result use at the leaf site: miss is t_num == +inf (0x7f800000), t = t_num * rcp(t_denom)')
need(237, '0x00000464: S_BFM_B32 vcc_lo, 8, 23')
need(245, '0x00000494: V_CMP_NE_U32 s32, vcc_lo, v0')
need(243, '0x0000048c: V_LSHRREV_B32 v2, 31, v0')
need(246, '0x0000049c: V_CMP_EQ_U32 vcc_lo, s35, v2')
need(247, '0x000004a0: V_MUL_F32 v0, v0, v1')
need(250, '0x000004ac: V_CMP_GT_F32 s32, v0, v25')
need(252, '0x000004b8: S_NOR_B64 vcc_lo, vcc_lo, s30')
need(253, '0x000004bc: S_NOR_B64 vcc_lo, s32, vcc_lo')
need(211, '0x000003ec: S_AND_B32 s16, vcc_hi, 0x01000000')
need(212, '0x000003f4: S_BFE_U32 s35, vcc_hi, 0x00010019')
bfm = ((1 << 8) - 1) << 23
print('   S_BFM_B32 8, 23 = 0x%08x (+inf)' % bfm)
ok &= bfm == 0x7f800000

print('== (e) hit-triangle decode at 0xcd0..0xd84 (node pointer v14 = s26 of the accepted entry)')
need(260, '0x000004d8: V_MOV_B32 v14, s26')
need(634, '0x00000cd0: V_AND_B32 v17, 7, v14')
need(636, '0x00000cd8: V_ALIGNBYTE_B32 v16, 0, 0x00301818, v14')
need(637, '0x00000ce4: V_ALIGNBYTE_B32 v10, 0, 0x3024240c, v14')
need(639, '0x00000cf8: V_MIN_U32 v17, 2, v17')
need(640, '0x00000cfc: V_LSHLREV_B32 v15, 6, v15')
need(641, '0x00000d00: V_MOV_B32 v14, v16.sdwa(sel=0,sext=0)')
need(642, '0x00000d08: V_MOV_B32 v10, v10.sdwa(sel=0,sext=0)')
need(644, '0x00000d18: V_LSHLREV_B32 v13, 2, v17')
need(645, '0x00000d1c: V_LSHL_ADD_U32 v13, v13, 1, v13')
need(652, '0x00000d48: V_ADD_I32 v9, vcc_lo, v15, v13')
need(653, '0x00000d50: V_ADD_I32 v12, s20, v15, v14')
need(654, '0x00000d58: V_ADD_I32 v15, s22, v15, v10')
need(658, '0x00000d74: FLAT_LOAD_DWORDX3 v9, v9, v10')
need(659, '0x00000d7c: FLAT_LOAD_DWORDX3 v12, v12, v13')
need(660, '0x00000d84: FLAT_LOAD_DWORDX3 v15, v15, v16')


def alignbyte(src0, src1, sel):
    # V_ALIGNBYTE_B32: D = ({S0, S1} >> (8 * S2[1:0]))[31:0]
    v = ((src0 << 32) | src1) >> (8 * (sel & 3))
    return v & 0xffffffff


print('== (f) descriptor dword3 of both levels = size[41:32] | 0x81000000 (type 8, bit 24 triangle_return_mode = 1)')
need(143, '0x00000298: S_OR_B32 s59, vcc_lo, 0x81000000')
need(206, '0x000003d0: S_OR_B32 s43, vcc_lo, 0x81000000')
print('   bit 24 of 0x81000000 = %d' % ((0x81000000 >> 24) & 1))
ok &= ((0x81000000 >> 24) & 1) == 1

print('== (g) output: one 2D IMAGE_STORE at (s16 * 128 + v0, s17) - one texel per thread')
need(2, '0x00000004: V_LSHL_ADD_U32 v24, s16, 7, v0')
need(1916, '0x000027e8: IMAGE_STORE v0, v24, s0, s0 ; dmask=0xf image_dim=2d')
stores = [k + 1 for k, t in enumerate(lines) if 'STORE' in t.upper()]
print('   lines with STORE:', stores)
ok &= stores == [1916]

print('== (h) hit shading samples shadow maps with compare; NaN / inf outputs are zeroed before the store')
need(855, '0x0000114c: image_sample_c_lz v1, v19, s44, s40')
need(1036, '0x0000150c: image_sample_c_lz v9, v12, s64, s60')
need(1903, '0x00002798: V_CMP_CLASS_F32 s8, v7, 3')
need(1911, '0x000027c4: V_CNDMASK_B32 v0, v0, 0, s8')
need(1913, '0x000027d4: V_CNDMASK_B32 v2, v2, 0, s12')

gpurt = {0: (0, 1, 2), 1: (1, 3, 2), 2: (2, 3, 4), 3: (2, 4, 0)}  # GPURT b89f22a Common.hlsl:321-352, RRA triangle_node.cpp:83-99
print('   type | A=12*min(t,2) | B=byte(0x00301818) | C=byte(0x3024240c) | (A,C,B) as vertices | GPURT/RRA')
for t in range(4):
    a = ((min(t, 2) << 2) << 1) + (min(t, 2) << 2)
    b = alignbyte(0, 0x00301818, t) & 0xff
    c = alignbyte(0, 0x3024240c, t) & 0xff
    tri = (a // 12, c // 12, b // 12)
    good = (a % 12 == 0 and b % 12 == 0 and c % 12 == 0 and tri == gpurt[t])
    print('   %d    | %2d            | %2d                 | %2d                 | V%d V%d V%d            | V%d V%d V%d  %s' % (
        t, a, b, c, tri[0], tri[1], tri[2], gpurt[t][0], gpurt[t][1], gpurt[t][2], 'OK' if good else 'FAIL'))
    ok &= good

print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
