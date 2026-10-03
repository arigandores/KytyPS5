"""f7d_rt1y.py - F7d (HPP-443, Red Team): does the STORED G-buffer (post values of the real replay, not RenderDoc's
reconstructed shader 'out') carry a texture sampled at the interpolated floor UV?

PS 508 samples image_3[0] (tex 12226, BC4) at the same (u, v) as the albedo atlas (ps_508.dis.txt lines 818-824).
Compare post RT1.y (tex 6657) at F1-F6 (rd_f7b_hist.txt) with image_3[0] mip0 at F7b's interpolated UV
(f7b-b39.md 448a53bf line 73-74) and with image_3[0] at (0, 0) (the collapse alternative (b)).
Also prints the AO pass (EID 3277/7146, blend MIN on RT1.b, mask 4) pre/out/post consistency check:
post.b must equal min(out.b, pre.b) up to 1/255 if RenderDoc's 'out' equals the fragment output the pass stored.
"""
import re, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from f7d_uvtex import load_bc4, W

RD = 'C:/kyty/f287/f7b/rd'
UV = {'F1': (0.26880, 0.33179), 'F2': (0.25487, 0.16748), 'F3': (0.32566, 0.24961), 'F4': (0.19199, 0.41921),
      'F5': (0.31359, 0.15714), 'F6': (0.14315, 0.17268)}


def bilinear(img, u, v):
    x = (u % 1.0) * W - 0.5
    y = (v % 1.0) * W - 0.5
    x0, y0 = int(np.floor(x)), int(np.floor(y))
    fx, fy = x - x0, y - y0
    g = lambda xx, yy: float(img[yy % W, xx % W])
    return (g(x0, y0) * (1 - fx) * (1 - fy) + g(x0 + 1, y0) * fx * (1 - fy) + g(x0, y0 + 1) * (1 - fx) * fy +
            g(x0 + 1, y0 + 1) * fx * fy)


def hist():
    t = open(RD + '/rd_f7b_hist.txt', 'rb').read().decode('utf-8', 'replace').split('\n')
    cur = None
    rt1 = {}
    ao = []
    for l in t:
        if l.startswith('-- HIST'):
            m = re.match(r'-- HIST (\S+) .*on tex (\d+) ', l)
            cur = m.groups() if m else None
            continue
        if not cur or cur[1] != '6657':
            continue
        m = re.match(r'\s*eid (\d+) \S+ passed=(\S+) .*pre=\(([^)]*)\) out=\(([^)]*)\) post=\(([^)]*)\)', l)
        if not m:
            continue
        eid = int(m.group(1))
        pre, out, post = [list(map(float, m.group(k).split())) for k in (3, 4, 5)]
        if eid == 950 and m.group(2) == 'True':
            rt1[cur[0]] = (out[1], post[1])
        if eid in (3277, 7146):
            ao.append((cur[0], eid, pre[2], out[2], post[2]))
    return rt1, ao


def main():
    i0, h0 = load_bc4('tex_12226_e950_m0.raw')
    rt1, ao = hist()
    print('image_3[0] 12226 sha256 %s; texel (0,0) = %.4f, bilinear at UV (0,0) = %.4f' % (
        h0[:16], float(i0[0, 0]), bilinear(i0, 0.0, 0.0)))
    xs, ys = [], []
    for p in sorted(UV):
        u, v = UV[p]
        s = bilinear(i0, u, v)
        o, q = rt1[p]
        xs.append(s)
        ys.append(q)
        print('%s UV (%.5f, %.5f): image_3[0] bilinear %.4f | RT1.y draw 950 out %.4f post %.4f | diff post-tex %+.4f' % (
            p, u, v, s, o, q, q - s))
    xs, ys = np.array(xs), np.array(ys)
    r = float(np.corrcoef(xs, ys)[0, 1])
    print('points 6, corr(image_3[0] at UV, post RT1.y) = %.3f, max |post - tex| = %.4f, spread tex %.4f, spread post %.4f' % (
        r, float(np.max(np.abs(ys - xs))), float(xs.max() - xs.min()), float(ys.max() - ys.min())))
    print('== AO pass on RT1.b (blend MIN, mask 4): post vs min(out, pre)')
    bad = 0
    for p, e, pre, out, post in ao:
        exp = min(out, pre)
        ok = abs(post - exp) <= 1.5 / 255
        bad += not ok
        print('  %s eid %d pre %.4f out %.4f post %.4f expected %.4f %s' % (p, e, pre, out, post, exp, 'ok' if ok else 'MISMATCH'))
    print('AO point-events %d, mismatches %d' % (len(ao), bad))
    print('ALL OK')


if __name__ == '__main__':
    main()
