# F12a (HPP-474): CPU reference of the hardware answer of IMAGE_BVH_INTERSECT_RAY on a triangle node,
# node types 0..3 (and 6/7), by the first source GPURT b89f22aa (2022-09-28):
#   src/shaders/IntersectCommon.hlsl:677-754  image_bvh64_intersect_ray_base (software path of the HW op);
#                                             :725 triangle branch for IsTriangleNode (Common.hlsl:595-597: type <= 3)
#   src/shaders/IntersectCommon.hlsl:205-226  FetchTriangleFromNode -> CalcTriangleVertexOffsets(nodeType)
#   src/shaders/Common.hlsl:322-352           CalcTriangleVertexOffsets: 0 (V0,V1,V2) 1 (V1,V3,V2) 2 (V2,V3,V4) 3 (V2,V4,V0)
#   src/gpurtCpuUtils.h:223-230               V0..V4 at 0/12/24/36/48, triangle ID at 60, node 64 bytes
#   src/shaders/IntersectCommon.hlsl:592-626  fast_intersect_triangle (miss -> x = +inf, y = 1.0 at :624-625)
#   src/shaders/IntersectCommon.hlsl:632-652  SwizzleBarycentrics (byte 8*nodeType of the triangle ID, :650-651)
#   src/shaders/IntersectCommon.hlsl:746-749  user node (6, 7): "HW returns -1"
# Descriptor triangle_return_mode = 1 ("Return IJ", Mesa radv_nir_rt_common.c:583), as the game sets it.
# Prints the GPU-test table (expected dwords for KYTY_FIX_F10=1 and =0) and self-checks; ALL OK at the end.
import sys
import numpy as np

F = np.float32
INF_BITS = 0x7f800000
ONE_BITS = 0x3f800000
NEG1 = 0xffffffff


def bits(x):
    return int(np.array([x], dtype=np.float32).view(np.uint32)[0])


# ---- the node: a fan of 4 triangles around V2 (all coordinates small integers -> every product and
# sum below is exact in float32, so FMA contraction or evaluation order cannot change a bit).
V = [
    (0, -8, 1),   # V0 south
    (8, 0, 2),    # V1 east
    (0, 0, 0),    # V2 centre
    (0, 8, 3),    # V3 north
    (-8, 0, 4),   # V4 west
]
# triangle ID bytes: type0 rot0 (I=1,J=2) 0x09, type1 rot1 (I=2,J=0) 0x02, type2 rot2 (I=0,J=1) 0x04,
# type3 rot0 0x09 (WriteTriangleIdField, gpurtCpuUtils.h:256-265: I=(rot+1)%3, J=(rot+2)%3)
TRI_ID = 0x09 | (0x02 << 8) | (0x04 << 16) | (0x09 << 24)
MAPPING = {0: (0, 1, 2), 1: (1, 3, 2), 2: (2, 3, 4), 3: (2, 4, 0)}
# ray origins (z = -4, direction +z): inside the quadrant of each type (hit) and the opposite one (miss)
HIT_XY = {0: (2, -2), 1: (2, 2), 2: (-2, 2), 3: (-2, -2)}
MISS_XY = {0: (-2, 2), 1: (-2, -2), 2: (2, -2), 3: (2, 2)}
DIR = (0, 0, 1)

ok = True
checks = []


def check(name, cond):
    global ok
    checks.append((name, bool(cond)))
    ok &= bool(cond)


def sub(a, b, t):
    return tuple(t(a[i]) - t(b[i]) for i in range(3))


def cross(a, b, t):
    return (t(a[1]) * t(b[2]) - t(a[2]) * t(b[1]),
            t(a[2]) * t(b[0]) - t(a[0]) * t(b[2]),
            t(a[0]) * t(b[1]) - t(a[1]) * t(b[0]))


def dot(a, b, t):
    return t(a[0]) * t(b[0]) + (t(a[1]) * t(b[1]) + t(a[2]) * t(b[2]))


def fast_intersect_triangle(origin, direction, v1, v2, v3, t):
    e1 = sub(v2, v1, t)
    e2 = sub(v3, v1, t)
    e3 = sub(origin, v1, t)
    s1 = cross(direction, e2, t)
    s2 = cross(e3, e1, t)
    x = dot(e2, s2, t)
    y = dot(s1, e1, t)
    z = dot(e3, s1, t)
    w = dot(direction, s2, t)
    tt = x / y
    u = z / y
    v = w / y
    missed = (u < 0) or (u > 1) or (v < 0) or (u + v > 1) or (tt < 0)
    inter = [e1, e2, e3, s1, s2, (x, y, z, w)]
    if missed:
        x = t(np.inf)
        y = t(1.0)
    return [x, y, z, w], missed, inter


def hw_answer(node_type, origin, t=F):
    # the hardware answer by GPURT b89f22aa for one node of the test layout
    if node_type in (4, 5):
        raise ValueError('box nodes are not part of this table')
    if node_type >= 6:
        return [NEG1] * 4, None, None
    a, b, c = (V[i] for i in MAPPING[node_type])
    res, missed, inter = fast_intersect_triangle(origin, DIR, a, b, c, t)
    baryc = [res[1] - res[2] - res[3], res[2], res[3]]
    shift = 8 * node_type
    i_src = (TRI_ID >> (shift + 0)) % 4
    j_src = (TRI_ID >> (shift + 2)) % 4
    out = [res[0], res[1], baryc[i_src], baryc[j_src]]
    return [bits(F(x)) for x in out], missed, inter


def emu_fix0_answer(node_type, origin):
    # the emulator now (KYTY_FIX_F10 absent): types 0-1 triangle, 2,3,6,7 -> 0xffffffff x4
    # (cdf8bf9c spirvEmitterMemory.cpp:2232, :2417-2426; Memory.cpp:889, :1053-1059)
    if node_type in (0, 1):
        return hw_answer(node_type, origin)[0]
    return [NEG1] * 4


rows = []
for k in range(4):
    for kind, xy in (('hit', HIT_XY[k]), ('miss', MISS_XY[k])):
        origin = (xy[0], xy[1], -4)
        exp1, missed, inter = hw_answer(k, origin)
        # exactness: the same computation in float64 gives the same values (no rounding anywhere)
        _, missed64, inter64 = hw_answer(k, origin, t=float)
        flat32 = [float(v) for grp in inter for v in grp]
        flat64 = [float(v) for grp in inter64 for v in grp]
        check('exact f32==f64 type%d %s' % (k, kind), flat32 == flat64 and missed == missed64)
        check('integer intermediates < 2^24 type%d %s' % (k, kind),
              all(abs(v) < 2 ** 24 and v == int(v) for v in flat64))
        check('%s as designed type%d' % (kind, k), missed == (kind == 'miss'))
        exp0 = emu_fix0_answer(k, origin)
        rows.append((k, kind, origin, exp1, exp0))
        # sensitivity: any other type's vertex mapping on the same ray gives another answer
        for other in range(4):
            if other == k:
                continue
            a, b, c = (V[i] for i in MAPPING[other])
            res_o, missed_o, _ = fast_intersect_triangle(origin, DIR, a, b, c, F)
            baryc_o = [res_o[1] - res_o[2] - res_o[3], res_o[2], res_o[3]]
            shift = 8 * k
            alt = [bits(F(x)) for x in (res_o[0], res_o[1], baryc_o[(TRI_ID >> shift) % 4],
                                        baryc_o[(TRI_ID >> (shift + 2)) % 4])]
            check('mapping of type%d on ray type%d %s differs' % (other, k, kind), alt != exp1)
for k in (6, 7):
    origin = (2, -2, -4)
    exp1 = hw_answer(k, origin)[0]
    rows.append((k, 'any', origin, exp1, emu_fix0_answer(k, origin)))
    check('type%d -1 x4 at both values' % k, exp1 == [NEG1] * 4)

# triangle-ID byte sensitivity: reading byte 0 for every type (a bug class) changes the answer of type 1..3 hits
for k in (1, 2):
    origin = (HIT_XY[k][0], HIT_XY[k][1], -4)
    a, b, c = (V[i] for i in MAPPING[k])
    res, _, _ = fast_intersect_triangle(origin, DIR, a, b, c, F)
    baryc = [res[1] - res[2] - res[3], res[2], res[3]]
    wrong = [bits(F(x)) for x in (res[0], res[1], baryc[TRI_ID % 4], baryc[(TRI_ID >> 2) % 4])]
    check('ID byte of type0 used for type%d hit differs' % k, wrong != hw_answer(k, origin)[0])

# =0 vs =1: equal for 0,1,6,7; differ for 2,3 (the negative control of the test)
for k, kind, origin, e1, e0 in rows:
    if k in (2, 3):
        check('=0 differs from =1 type%d %s' % (k, kind), e1 != e0)
    else:
        check('=0 equals =1 type%d %s' % (k, kind), e1 == e0)

print('# node: V0..V4 (dwords 0..14) =', V, ' triangle ID (dword 15) = 0x%08x' % TRI_ID)
print('# ray: origin (x, y, -4), direction (0, 0, 1); inverse direction and extent unused by triangles')
print('type\tcase\torigin\tKYTY_FIX_F10=1 (first source)\tKYTY_FIX_F10=0 (emulator now)')
for k, kind, origin, e1, e0 in rows:
    print('%d\t%s\t%s\t%s\t%s' % (k, kind, origin, ' '.join('%08x' % x for x in e1), ' '.join('%08x' % x for x in e0)))

# what the game does with the emulator answer 0xffffffff x4 at the leaf site (pc 0x48c..0x4bc)
print('# game accept logic at pc 0x474 for v0 = 0xffffffff (emulator answer on types 2-3):')
v0 = NEG1
hit = v0 != INF_BITS
sign = v0 >> 31
t_is_nan = True  # NaN * rcp(NaN)
for flag24 in (0, 1):
    for bit25 in (0, 1):
        gt = False if t_is_nan else None   # V_CMP_GT_F32 with NaN -> false
        a = (bit25 == sign) and hit and not flag24
        s30 = hit and bool(flag24)
        accept = (not gt) and (a or s30)
        print('#   instance bit24=%d bit25=%d -> hitmask=%d accepted=%d (best t := NaN if accepted)' % (
            flag24, bit25, hit, accept))
check('emulator -1 is not the HW miss encoding', hit)

for name, good in checks:
    if not good:
        print('FAIL', name)
print('checks %d, failed %d' % (len(checks), sum(1 for _, g in checks if not g)))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
