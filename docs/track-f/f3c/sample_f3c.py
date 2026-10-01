# F3c (HPP-341): independent byte check of 5 rows of form_f3b.out.txt in eboot.bin (GFX10 encodings read by hand:
# SOP2 [31:30]=10 op[29:23] sdst[22:16] ssrc1[15:8] ssrc0[7:0]; S_BFE_U64 = 41 (GFX10: S_MUL_I32 38, S_BFE_U32 39, S_BFE_I32 40, S_BFE_U64 41, S_BFE_I64 42); literal 0xff -> next dword.
# SOP1 [31:23]=0x17d sdst[22:16] op[15:8] ssrc0[7:0]; S_BITSET1_B32 = 0x1d (GFX10), inline 31 = 0x9f.
# MIMG dword0 [31:26]=0x3c, opcode = dword0[0]<<7 | dword0[24:18]; IMAGE_BVH_INTERSECT_RAY = 0xe6; dword1 srsrc[20:16] = sgpr/4.
import struct
EB = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/eboot.bin'
f = open(EB, 'rb')
def dw(off):
    f.seek(off); return struct.unpack('<I', f.read(4))[0]
# (program, BFE pc, BFE eboot off, sdst, ssrc0, BITSET pc, BVH pcs, T# first sgpr)
rows = [
 ('380bb9d636390bae', 0x3c8, 0x909d628, 40, 20, 0x400, [0x474, 0x52c], 40),
 ('380bb9d636390bae', 0x284, 0x909d4e4, 56, 18, 0x2b8, [0x8f8], 56),
 ('0af122d5ac62c4c5', 0x2be4, 0xdffd5dc, 16, 8, 0x2c34, [0x2ca4, 0x2d40], 16),
 ('99012529f9a27ba3', 0xd24, 0xe00b004, 4, 2, 0xd58, [0x1510], 4),
 ('092754e7ae8bac9a', 0x1788, 0xe172278, 24, 2, 0x17c0, [0x1e40], 24),
]
ok = True
for prog, pc, off, sdst, src, bpc, bvh, tsg in rows:
    w, lit = dw(off), dw(off + 4)
    bfe = (w >> 30) == 2 and ((w >> 23) & 0x7f) == 41 and ((w >> 16) & 0x7f) == sdst and ((w >> 8) & 0xff) == 0xff and (w & 0xff) == src and lit == 0x00280008
    b = dw(off + bpc - pc)
    bit = (b >> 23) == 0x17d and ((b >> 16) & 0x7f) == sdst + 1 and ((b >> 8) & 0xff) == 0x1d and (b & 0xff) == 0x9f
    res = []
    for p in bvh:
        d0, d1 = dw(off + p - pc), dw(off + p - pc + 4)
        op = ((d0 & 1) << 7) | ((d0 >> 18) & 0x7f)
        res.append((hex(p), (d0 >> 26) == 0x3c and op == 0xe6 and ((d1 >> 16) & 0x1f) * 4 == tsg, hex(d0), hex(d1)))
    good = bfe and bit and all(r[1] for r in res)
    ok &= good
    print(prog, hex(pc), hex(off), 'BFE', bfe, hex(w), hex(lit), 'BITSET1', bit, hex(b), 'BVH', res, 'OK' if good else 'FAIL')
print('ALL OK' if ok else 'SOME FAILED')
