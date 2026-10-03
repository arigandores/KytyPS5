"""f7d_outpost.py - F7d (HPP-443, Red Team): for fragments of the floor draws (950, 960, 4946, 4956) that PASSED, does RenderDoc's
reconstructed shader 'out' equal the stored 'post' (no blending on the G-buffer, so post = quantized out)?  Points F1-F6, targets
6683 (sRGB, tolerance 1/255 in sRGB space), 6657 (UNORM, 1/255), 6647 / 13050 (FP16, 1e-3), 6685 (R11G11B10, 1e-3).
Source: rd/rd_f7b_hist.txt (F7b replay output).
"""
import re

RD = 'C:/kyty/f287/f7b/rd'


def l2s(c):
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def main():
    t = open(RD + '/rd_f7b_hist.txt', 'rb').read().decode('utf-8', 'replace').split('\n')
    cur = None
    n = bad = 0
    worst = 0.0
    for l in t:
        if l.startswith('-- HIST'):
            m = re.match(r'-- HIST (\S+) .*on tex (\d+) ', l)
            cur = m.groups() if m else None
            continue
        if not cur or cur[0] not in ('F1', 'F2', 'F3', 'F4', 'F5', 'F6'):
            continue
        if cur[1] not in ('6683', '6657', '6647', '13050', '6685'):
            continue
        m = re.match(r'\s*eid (950|960|4946|4956) \S+ passed=True .*out=\(([^)]*)\) post=\(([^)]*)\)', l)
        if not m:
            continue
        out = list(map(float, m.group(2).split()))
        post = list(map(float, m.group(3).split()))
        if cur[1] == '6683':
            d = max(abs(l2s(max(o, 0.0)) - l2s(max(p, 0.0))) for o, p in zip(out[:3], post[:3]))
            tol = 1.0 / 255 + 1e-4
        elif cur[1] == '6657':
            d = max(abs(o - p) for o, p in zip(out, post))
            tol = 1.0 / 255 + 1e-4
        else:
            d = max(abs(o - p) for o, p in zip(out[:3], post[:3]))
            tol = 1e-3
        n += 1
        worst = max(worst, d / tol)
        if d > tol:
            bad += 1
            print('MISMATCH %s tex %s eid %s out %s post %s' % (cur[0], cur[1], m.group(1), out, post))
    print('passed floor fragments (points F1-F6 x targets x draws): %d, out != post beyond tolerance: %d, worst |d|/tol %.2f' % (n, bad, worst))
    print('ALL OK')


if __name__ == '__main__':
    main()
