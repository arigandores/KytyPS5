import os, sys, struct, math
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK'); sys.exit(3)
# T313 + T179 model (no game, no GPU): a guest compute DWORD fill writes the same 32-bit word W over the whole
# allocation (multi-word records only when all words equal, dd73d04d ResourceMaterialization.cpp:371-377).
# ours  = ClearImageFromBuffer -> DecodePackedColorClear(fmt, W) with packed1 = 0 (dd73d04d textureCache.cpp:2971,
#         imageInfo.h:550-553 two-argument overload, :436-548 decoder)
# truth = the texel the memory holds: texel bytes = W repeated (texel size 1, 2, 4 or 8 bytes); a 1/2-byte texel
#         holds a byte/half of W that depends on its byte offset, so the surface is uniform only when those parts are equal.
# upstr = 57c97ebd8 + 89792a3bc DecodeColorDwordFill: R16 with unequal halves -> decline, RGBA16F only W == 0.
def half(b):
    s = (b >> 15) & 1; e = (b >> 10) & 31; m = b & 1023
    v = math.ldexp(m, -24) if e == 0 else (float('inf') if (e == 31 and m == 0) else (float('nan') if e == 31 else math.ldexp(m | 1024, e - 25)))
    return -v if s else v
def f32(x):
    return struct.unpack('<f', struct.pack('<I', x))[0]
def ours(fmt, W):
    lo, hi = W & 0xffff, W >> 16
    if fmt == 'R16_SFLOAT': return (half(lo),)
    if fmt == 'R16_UNORM': return (lo / 65535.0,)
    if fmt == 'R16G16_SFLOAT': return (half(lo), half(hi))
    if fmt == 'R16G16B16A16_SFLOAT': return (half(lo), half(hi), half(0), half(0))
    if fmt == 'R16G16B16A16_UNORM': return (lo / 65535.0, hi / 65535.0, 0.0, 0.0)
    if fmt == 'R32G32_SFLOAT': return (f32(W), f32(0))
    if fmt == 'R8_UNORM': return ((W & 0xff) / 255.0,)
    if fmt == 'R8G8_UNORM': return ((W & 0xff) / 255.0, ((W >> 8) & 0xff) / 255.0)
def truth(fmt, W):
    lo, hi = W & 0xffff, W >> 16
    b = [(W >> (8 * i)) & 0xff for i in range(4)]
    if fmt == 'R16_SFLOAT': return 'uniform' if lo == hi else 'NOT uniform (texel = lo or hi by byte offset)', (half(lo),)
    if fmt == 'R16_UNORM': return 'uniform' if lo == hi else 'NOT uniform (texel = lo or hi by byte offset)', (lo / 65535.0,)
    if fmt == 'R16G16_SFLOAT': return 'uniform', (half(lo), half(hi))
    if fmt == 'R16G16B16A16_SFLOAT': return 'uniform', (half(lo), half(hi), half(lo), half(hi))
    if fmt == 'R16G16B16A16_UNORM': return 'uniform', (lo / 65535.0, hi / 65535.0, lo / 65535.0, hi / 65535.0)
    if fmt == 'R32G32_SFLOAT': return 'uniform', (f32(W), f32(W))
    if fmt == 'R8_UNORM': return 'uniform' if len(set(b)) == 1 else 'NOT uniform (texel = byte by offset)', (b[0] / 255.0,)
    if fmt == 'R8G8_UNORM': return 'uniform' if lo == hi else 'NOT uniform (texel = lo or hi by offset)', (b[0] / 255.0, b[1] / 255.0)
def same(a, b):
    return all((x == y) or (x != x and y != y) for x, y in zip(a, b))
FMTS = ['R16_SFLOAT', 'R16_UNORM', 'R16G16_SFLOAT', 'R16G16B16A16_SFLOAT', 'R16G16B16A16_UNORM', 'R32G32_SFLOAT',
        'R8_UNORM', 'R8G8_UNORM']
VALS = [0x00000000, 0x3c003c00, 0x00003c00, 0xffffffff, 0x20202020, 0xfffffff0, 0x3f800000]
wrong = 0
for fmt in FMTS:
    for W in VALS:
        o = ours(fmt, W)
        kind, t = truth(fmt, W)
        ok = kind == 'uniform' and same(o, t)
        wrong += not ok
        print('%-20s W=0x%08x  ours=%s  memory=%s %s  -> %s' % (fmt, W, tuple(round(x, 6) if x == x else 'nan' for x in o), kind,
              tuple(round(x, 6) if x == x else 'nan' for x in t) if kind == 'uniform' else '', 'SAME' if ok else 'DIFFERS'))
print('differing (format, value) pairs:', wrong, 'of', len(FMTS) * len(VALS))
print('DONE')
