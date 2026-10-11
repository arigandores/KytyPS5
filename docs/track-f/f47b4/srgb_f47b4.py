# F47b4 (HPP-819, Red Team): readings of section 4.1 of edition 4 (Q0 = export value, Q1 = round(v*255)/255) against
# what an sRGB colour attachment can report as `Shader Out`: E = encoded byte / 255, L = decode(encoded byte) (linear of
# the stored value). Prints, for a literal v, the differences in units of 1/255 and the reading of item 722(g)(1)
# ("not equal" only if the difference under BOTH readings is > 1 LSB). Arithmetic only; ASCII only.
import os
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3')
    sys.exit(3)


def enc(x):
    return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055


def dec(e):
    return e / 12.92 if e <= 0.04045 else ((e + 0.055) / 1.055) ** 2.4


def rd(x):
    return int(x * 255 + 0.5)


band = 0
n = 0
for v in [0.5, 0.9, 0.95, 0.9955] + [k / 10000 for k in range(0, 10001)]:
    q0 = v
    q1 = rd(v) / 255
    e = rd(enc(v)) / 255
    l = dec(e)
    out = []
    for name, s in (('E', e), ('L', l)):
        d0, d1 = abs(s - q0) * 255, abs(s - q1) * 255
        ne = d0 > 1 and d1 > 1
        out.append('%s %.6f d(Q0) %.3f d(Q1) %.3f -> %s' % (name, s, d0, d1, 'NOT_EQUAL' if ne else 'equal/undet'))
        if name == 'L' and ne and v not in (0.5, 0.9, 0.95, 0.9955):
            band += 1
    if v in (0.5, 0.9, 0.95, 0.9955) and n < 4:
        n += 1
        print('v %.4f Q1 %.6f | %s' % (v, q1, ' | '.join(out)))
print('grid 0..1 step 1e-4: literals with NOT_EQUAL against L (decoded-quantized) under both readings: %d of 10001' % band)
print('done')
