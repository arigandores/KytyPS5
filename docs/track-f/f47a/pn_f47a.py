# F47a (HPP-802): pairs (FrameTrace n, video present) from the lines that carry "present=<p>" (DiagF5Ev, KYTY_DIAG_F5=1):
# the last FrameTrace row before the line gives n; d = present - n. Also the named "Level has started:" line and n after it.
# The present a site prints is the last one published by the recorder (diagF5.h: "the frame of the site is shown at a
# later present"), so d is an upper bound of the lag of the shown frame, within a frame or two.
# Usage: python pn_f47a.py <log>
import re, sys

RXN = re.compile(rb'^FrameTrace: n=(\d+) ')
RXP = re.compile(rb' present=(\d+) ')
n = None
pairs = []
start = None
pend = False
with open(sys.argv[1], 'rb') as f:
    for line in f:
        m = RXN.match(line)
        if m:
            n = int(m.group(1))
            if pend:
                start, pend = n, False
            continue
        if start is None and not pend and b'Level has started:' in line and line.split(b'started:', 1)[1].strip():
            pend = True
            continue
        if line.startswith(b'DiagF5Ev'):
            m = RXP.search(line)
            if m and n is not None:
                pairs.append((n, int(m.group(1)), line.split(b' ', 2)[1].decode()))
print('named start n', start)
ds = {}
for n_, p, kind in pairs:
    ds.setdefault(p - n_, []).append((n_, p, kind))
for d in sorted(ds):
    v = ds[d]
    print('d=%d count %d n %d..%d kinds %s' % (d, len(v), v[0][0], v[-1][0], sorted(set(k for _, _, k in v))))
