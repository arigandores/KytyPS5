# F47a2 (HPP-807, item 708(b)(9)): is the import / staging witness live in a log of the f47_hi form without the knob?
# Per log: number of FrameTrace-draw lines with the field img_imp, sum of img_imp / img_imp_kb over the run and over the
# title window [n_start + LO, n_start + HI] (n_start - n of the first FrameTrace line after the NAMED 'Level has started:'
# line, F47a section 1.1), sums of stg_img_pool_b + stg_img_in_b of FrameTrace-x lines (raw bytes), the
# 'Vulkan pipeline cache: loaded' lines (path of the driver blob) and the KYTY_HOST_IMPORT / HostImport lines.
# Usage: python imp_f47a2.py <log> [--lo 600] [--hi 950]
import re, sys

logp = sys.argv[1]
a = sys.argv
LO = int(a[a.index('--lo') + 1]) if '--lo' in a else 600
HI = int(a[a.index('--hi') + 1]) if '--hi' in a else 950
RN = re.compile(rb'^FrameTrace: n=(\d+) ')
RD = re.compile(rb'^FrameTrace-draw: n=(\d+) .* img_imp=(\d+) img_imp_kb=(\d+) ')
RX = re.compile(rb'^FrameTrace-x: n=(\d+) .* stg_img_pool_b=(\d+) stg_img_in_b=(\d+) ')
start, pend = None, False
nd = imp = kb = wimp = wkb = 0
nx = sp = si = wsp = wsi = 0
other = []
with open(logp, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace: n='):
            if pend:
                start, pend = int(RN.match(line).group(1)), False
            continue
        if line.startswith(b'FrameTrace-draw:'):
            m = RD.match(line)
            if m:
                n, i, k = int(m.group(1)), int(m.group(2)), int(m.group(3))
                nd += 1; imp += i; kb += k
                if start is not None and start + LO <= n <= start + HI:
                    wimp += i; wkb += k
            continue
        if line.startswith(b'FrameTrace-x:'):
            m = RX.match(line)
            if m:
                n, p, q = int(m.group(1)), int(m.group(2)), int(m.group(3))
                nx += 1; sp += p; si += q
                if start is not None and start + LO <= n <= start + HI:
                    wsp += p; wsi += q
            continue
        if start is None and not pend and b'Level has started:' in line and line.split(b'started:', 1)[1].strip():
            pend = True
            continue
        if (b'Vulkan pipeline cache: loaded' in line or line.startswith(b'HostImport:')) and len(other) < 8:
            other.append(line.decode('utf-8', 'replace').rstrip())
print('log', logp)
print('n_start', start, 'window', LO, HI)
print('draw_lines_with_img_imp', nd, 'img_imp_sum', imp, 'img_imp_kb_sum', kb, 'window_img_imp', wimp, 'window_img_imp_kb', wkb)
print('x_lines_with_stg_img', nx, 'stg_img_pool_b_sum', sp, 'stg_img_in_b_sum', si, 'window_pool_b', wsp, 'window_in_b', wsi)
for o in other:
    print('line', o)
