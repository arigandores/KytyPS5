"""F23c (HPP-587): which side of H is right? CPU model of the reference PS 0xe197e307a5f2cb39 (from its SPIR-V, nearest
filter, target = video size) against the GPU targets of normal and predoff on configuration c01 (noise 3840x2160) and
c03 (grad), plus the historical hypothesis: in predoff the Y sample reads its y coordinate from the U result
(row = floor(U * TH)) - the form described in HANDOFF section 2.1 (sessions 5-10).

Model (all in float32 as the SPIR-V does it; u, v = attribute 0 at the pixel centre, recomputed in float32):
  x = floor(W*u); xc = min(1, (x + 0.5) * (1/W)); even = (x == trunc(0.5*x)*2)
  Y  at (xc, 0.6666666*v);  U at (even ? xc : xc - 1/W, fma(0.3333333, v, 0.6666666)); V at (even ? xc + 1/W : xc, same y)
  nearest texel = floor(coord * size) clamped; out = (R, G, B, 1) through half precision.
Output: ana_f23c.out.txt."""
import os
import subprocess
import sys

import numpy as np

D = 'C:/kyty/f287/f23c/'
W_ = D + 'work/'
lines = []


def log(s):
    print(s, flush=True)
    lines.append(s)


f32 = np.float32


def model(tex, w, h, hyp='ok', uv_from_gpu=None):
    th = h * 3 // 2
    py, px = np.mgrid[0:h, 0:w]
    if uv_from_gpu is None:
        u = ((px.astype(f32) + f32(0.5)) / f32(w)).astype(f32)
        v = ((py.astype(f32) + f32(0.5)) / f32(h)).astype(f32)
    else:
        u, v = uv_from_gpu
    W = f32(w)
    rw = (f32(1) / W).astype(f32)
    x = np.floor((W * u).astype(f32)).astype(f32)
    xc = np.minimum(f32(1), (rw * (x + f32(0.5)).astype(f32)).astype(f32)).astype(f32)
    even = x == (np.trunc((f32(0.5) * x).astype(f32)) * f32(2)).astype(f32)
    yy = (f32(0.666666627) * v).astype(f32)
    yuv = (f32(0.333333313) * v.astype(np.float64) + f32(0.666666627)).astype(f32)  # fma: one rounding
    ucoord = np.where(even, xc, (xc - rw).astype(f32))
    vcoord = np.where(even, (rw + xc).astype(f32), xc)

    def samp(cx, cy):
        col = np.clip(np.floor(cx.astype(np.float64) * w).astype(np.int64), 0, w - 1)
        row = np.clip(np.floor(cy.astype(np.float64) * th).astype(np.int64), 0, th - 1)
        return (tex[row, col].astype(f32) / f32(255)).astype(f32)

    U = samp(ucoord, yuv)
    V = samp(vcoord, yuv)
    if hyp == 'yU':
        Y = samp(xc, U)  # y coordinate of the Y sample replaced by the U result (historical form)
    elif hyp == 'VU':
        Y = samp(V, U)  # and the x coordinate replaced by the V result (second form-A select %306)
    elif hyp == 'yV':
        Y = samp(xc, V)  # y coordinate of the Y sample replaced by the V result
    elif hyp == 'xV':
        Y = samp(V, yy)  # only the x coordinate replaced by V
    else:
        Y = samp(xc, yy)
    yp = (f32(1.16439998) * Y.astype(np.float64) + f32(-0.0727749988)).astype(f32)
    t_u_g = (f32(-0.213300005) * U.astype(np.float64) + f32(0.106650002)).astype(f32)
    t_v_g = (f32(-0.532899976) * V.astype(np.float64) + f32(0.266449988)).astype(f32)
    t_v_r = (f32(1.79270005) * V.astype(np.float64) + f32(-0.896350026)).astype(f32)
    t_u_b = (f32(2.11240005) * U.astype(np.float64) + f32(-1.05620003)).astype(f32)
    R = (yp + t_v_r).astype(f32)
    G = ((yp + t_u_g).astype(f32) + t_v_g).astype(f32)
    B = (yp + t_u_b).astype(f32)
    out = np.stack([R, G, B, np.ones_like(R)], axis=-1).astype(np.float16).astype(f32)
    return out


def run(cfgname, pattern, w, h):
    th = h * 3 // 2
    sys.path.insert(0, D)
    import run_f23c_h
    tex_path, _ = run_f23c_h.make_tex(pattern, w, h)
    tex =np.fromfile(tex_path, dtype=np.uint8).reshape(th, w)
    outs = {}
    args = [D + 'f23c_hrun.exe', '--vs', W_ + 'vs_tri.spv', '--tex', tex_path, '--texw', str(w), '--texh', str(th), '--rtw', str(w),
            '--rth', str(h), '--fmt', '32', '--filter', 'nearest', '--cbw', str(w)]
    for v in ('normal', 'predoff'):
        o = W_ + 'ana_%s_%s.bin' % (cfgname, v)
        args += ['--job', W_ + 'ref_%s.spv' % v, o, '0']
        outs[v] = o
    env = dict(os.environ)
    env['__GL_SHADER_DISK_CACHE'] = '0'
    r = subprocess.run(args, capture_output=True, text=True, env=env, timeout=300)
    assert r.returncode == 0, r.stdout + r.stderr
    gpu = {k: np.fromfile(p, dtype=np.float32).reshape(h, w, 4) for k, p in outs.items()}
    ref = model(tex, w, h)
    bug = model(tex, w, h, hyp='yU')
    models = (('model', ref), ('bug Y@(xc,U)', bug), ('bug Y@(V,U)', model(tex, w, h, hyp='VU')), ('bug Y@(V,y)', model(tex, w, h, hyp='xV')), ('bug Y@(xc,V)', model(tex, w, h, hyp='yV')))
    even_col = (np.arange(w) % 2 == 0)[None, :].repeat(h, axis=0)
    for k in ('normal', 'predoff'):
        g = gpu[k]
        for mname, m in models:
            d = np.abs(g - m).max(axis=-1)
            ok = d <= 2 ** -9
            log('%s %-7s vs %-13s: exact %d, |d| <= 2^-9 %d (even columns %d of %d, odd %d of %d), |d| > 0.05 %d of %d; max |d| %.4f' % (
                cfgname, k, mname, int(np.count_nonzero(d == 0)), int(np.count_nonzero(ok)), int(np.count_nonzero(ok & even_col)),
                int(np.count_nonzero(even_col)), int(np.count_nonzero(ok & ~even_col)), int(np.count_nonzero(~even_col)),
                int(np.count_nonzero(d > 0.05)), w * h, float(d.max())))
    # where normal and predoff differ, per channel
    diff = gpu['normal'] != gpu['predoff']
    log('%s normal != predoff per channel R/G/B/A: %s' % (cfgname, [int(np.count_nonzero(diff[..., c])) for c in range(4)]))
    yy, xx = np.nonzero(np.any(diff, axis=-1))
    for i in list(range(0, len(yy), max(1, len(yy) // 4)))[:4]:
        y0, x0 = int(yy[i]), int(xx[i])
        log('   pixel (%d,%d): normal %s predoff %s model %s bug-model %s' % (
            x0, y0, np.round(gpu['normal'][y0, x0], 4).tolist(), np.round(gpu['predoff'][y0, x0], 4).tolist(),
            np.round(ref[y0, x0], 4).tolist(), np.round(bug[y0, x0], 4).tolist()))
    for p in outs.values():
        os.remove(p)


def main():
    run('c01', 'noise', 3840, 2160)
    run('c03', 'grad', 3840, 2160)
    run('c07', 'noise', 1920, 1080)
    open(D + 'ana_f23c.out.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
