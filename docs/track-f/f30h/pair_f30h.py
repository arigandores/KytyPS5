# F30h (HPP-718, Probe Designer): pairing of rts_bad_rx with rts_xb_ser frame by frame in the F30f c3 logs.  Read only.
# Per frame d = rx - ser; histogram of d; frames sets {rx>0}, {ser>0}; the running sum D(n) (bounded = pairing within a
# frame or across one boundary); share of rx explained as ser (min(rx, ser) summed over frames) and with a lag of one frame.
# Usage: python pair_f30h.py <log dir> <tag>...
import re
import sys

KV = re.compile(rb'(rts_(?:bad_rx|xb_ser|xb_meta|bad_b|bad|pb|xa_rec|xb_ids|xb_bound|xb_pass))=(\d+)')
NRE = re.compile(rb'FrameTrace-x: n=(\d+)')
for tag in sys.argv[2:]:
    rows = []
    with open('%s/log_%s.txt' % (sys.argv[1], tag), 'rb') as f:
        for line in f:
            if line.startswith(b'FrameTrace-x:') and b'rts_' in line:
                d = {k.decode(): int(v) for k, v in KV.findall(line)}
                rows.append((int(NRE.match(line).group(1)), d.get('rts_bad_rx', 0), d.get('rts_xb_ser', 0),
                             d.get('rts_xb_meta', 0)))
    rx = sum(r[1] for r in rows)
    ser = sum(r[2] for r in rows)
    hist = {}
    D = 0
    Dmax = Dmin = 0
    same = 0
    for i, (n, a, b, m) in enumerate(rows):
        hist[a - b] = hist.get(a - b, 0) + 1
        D += a - b
        Dmax = max(Dmax, D)
        Dmin = min(Dmin, D)
        same += min(a, b)
    # lag: ser of frame i+1 paired with the leftover rx of frame i
    lag = 0
    for i in range(len(rows) - 1):
        left = rows[i][1] - min(rows[i][1], rows[i][2])
        extra = rows[i + 1][2] - min(rows[i + 1][1], rows[i + 1][2])
        lag += min(left, extra)
    fr = {r[0] for r in rows if r[1] > 0}
    fs = {r[0] for r in rows if r[2] > 0}
    top = sorted(hist.items(), key=lambda x: -x[1])[:6]
    print('%s frames=%d rx=%d ser=%d ser/rx=%.4f same_frame=%d (%.4f of ser) lag1=%d frames_rx=%d frames_ser=%d '
          'only_rx=%d only_ser=%d D_end=%d D_max=%d D_min=%d hist(d)=%s'
          % (tag, len(rows), rx, ser, ser / rx if rx else 0, same, same / ser if ser else 0, lag, len(fr), len(fs),
             len(fr - fs), len(fs - fr), D, Dmax, Dmin, top))
print('ALL OK')
