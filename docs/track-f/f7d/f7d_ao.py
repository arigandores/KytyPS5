"""f7d_ao.py - F7d (HPP-443, Red Team): which of RenderDoc's reconstructed shader 'out' and the stored 'post' of the AO pass
(EID 3277 / 7146: PS 259 writes RT1.b of tex 6657 with blend MIN, mask 4) agrees with the AO input tex 6649 (960x540 R8,
dumped by F7b as rd/tex_6649_e3277_m0.raw / _e7146_m0.raw)?

PS 259 (rd/ps_259.rd.txt lines 109-197): coordinate = Select(quad mask, in_param_0.xy, 0); value = tex.r, or 1 - tex.r when
cb == 1 and the mask holds.  Assumption [I]: in_param_0.xy is the screen UV of a full-screen pass, (x + 0.5) / 3840,
(y + 0.5) / 2160; sampler clamp-to-edge, bilinear.  Prints, per point: AO at the screen UV, AO at UV (0, 0) (mask false),
RenderDoc out.b, stored post.b, and which hypothesis explains post = min(pre, value).
"""
import re
import numpy as np

RD = 'C:/kyty/f287/f7b/rd'
PTS = {'F1': (900, 1560), 'F2': (2850, 1440), 'F3': (1920, 2010), 'F4': (450, 1260), 'F5': (3450, 1800), 'F6': (2460, 1170),
       'A1': (1920, 1695), 'U1': (1920, 900), 'R1': (1920, 2100)}
TW, TH = 960, 540


def load(eid):
    a = np.frombuffer(open('%s/tex_6649_e%d_m0.raw' % (RD, eid), 'rb').read(), dtype=np.uint8).reshape(TH, TW)
    return a.astype(np.float64) / 255.0


def bilin(img, u, v):
    x = u * TW - 0.5
    y = v * TH - 0.5
    x0, y0 = int(np.floor(x)), int(np.floor(y))
    fx, fy = x - x0, y - y0
    c = lambda xx, yy: img[min(max(yy, 0), TH - 1), min(max(xx, 0), TW - 1)]
    return (c(x0, y0) * (1 - fx) * (1 - fy) + c(x0 + 1, y0) * fx * (1 - fy) + c(x0, y0 + 1) * (1 - fx) * fy +
            c(x0 + 1, y0 + 1) * fx * fy)


def hist():
    t = open(RD + '/rd_f7b_hist.txt', 'rb').read().decode('utf-8', 'replace').split('\n')
    cur = None
    res = {}
    for l in t:
        if l.startswith('-- HIST'):
            m = re.match(r'-- HIST (\S+) .*on tex (\d+) ', l)
            cur = m.groups() if m else None
            continue
        if not cur or cur[1] != '6657':
            continue
        m = re.match(r'\s*eid (3277|7146) .*pre=\(([^)]*)\) out=\(([^)]*)\) post=\(([^)]*)\)', l)
        if m:
            res[(cur[0], int(m.group(1)))] = tuple(float(m.group(k).split()[2]) for k in (2, 3, 4))
    return res


def main():
    h = hist()
    tol = 1.5 / 255
    n_out = n_post = n_zero = n = 0
    for eid in (3277, 7146):
        img = load(eid)
        z = bilin(img, 0.0, 0.0)
        print('== EID %d: tex 6649 min %.4f max %.4f mean %.4f; AO at UV (0,0) = %.4f' % (eid, img.min(), img.max(), img.mean(), z))
        for p, (x, y) in PTS.items():
            if (p, eid) not in h:
                continue
            pre, out, post = h[(p, eid)]
            s = bilin(img, (x + 0.5) / 3840.0, (y + 0.5) / 2160.0)
            e_screen = min(pre, s)
            e_zero = min(pre, z)
            m_out = abs(out - s) <= 2.5 / 255
            m_post = abs(post - e_screen) <= tol
            m_zero = abs(post - e_zero) <= tol
            n += 1
            n_out += m_out
            n_post += m_post
            n_zero += m_zero
            print('  %s (%4d,%4d) AO@screen %.4f | out %.4f %s | post %.4f vs min(pre,AO@screen) %.4f %s | vs min(pre,AO@0) %.4f %s' % (
                p, x, y, s, out, 'out=AO' if m_out else 'out!=AO', post, e_screen, 'ok' if m_post else 'NO', e_zero,
                'ok' if m_zero else 'NO'))
    print('point-events %d: out = AO@screen %d; post = min(pre, AO@screen) %d; post = min(pre, AO@(0,0)) %d' % (n, n_out, n_post, n_zero))
    print('ALL OK')


if __name__ == '__main__':
    main()
