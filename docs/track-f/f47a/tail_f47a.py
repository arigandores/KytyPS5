# F47a (HPP-802): d_tail = last present of <mp4>.idx - last FrameTrace n of the log; named start n; with --pairs also the
# early d of DiagF5Ev lines (pn_f47a.py logic) for a check of the tail estimator.
# Usage: python tail_f47a.py <log> <idx> [--pairs]
import re, sys

RXN = re.compile(rb'^FrameTrace: n=(\d+) ')
RXP = re.compile(rb' present=(\d+) ')
logp, idxp = sys.argv[1], sys.argv[2]
n = None
start, pend = None, False
early = {}
with open(logp, 'rb') as f:
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
        if '--pairs' in sys.argv and line.startswith(b'DiagF5Ev'):
            m = RXP.search(line)
            if m and n is not None:
                d = int(m.group(1)) - n
                early[d] = early.get(d, 0) + 1
last = None
for ln in open(idxp, encoding='ascii'):
    p = ln.split()
    if len(p) >= 2:
        last = int(p[1])
print('log %s named_start_n %s last_n %s last_present %s d_tail %s early_d %s' % (
    logp, start, n, last, (last - n) if (last is not None and n is not None) else None, early))
