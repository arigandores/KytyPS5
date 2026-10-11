# F47a (HPP-802): dt_us of the FrameTrace rows n_start+lo .. n_start+hi (the block window in FrameTrace n), and the
# RenderDoc lines of the log (if any) with the FrameTrace n of the row before each. Data for "frame-locked or time-based".
# Usage: python dtwin_f47a.py <log> <lo> <hi>
import re, sys

RXN = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+) ')
logp, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
start, pend, n = None, False, None
rows, rd = [], []
with open(logp, 'rb') as f:
    for line in f:
        m = RXN.match(line)
        if m:
            n = int(m.group(1))
            if pend:
                start, pend = n, False
            if start is not None and lo <= n - start <= hi:
                rows.append((n - start, int(m.group(2))))
            continue
        if start is None and not pend and b'Level has started:' in line and line.split(b'started:', 1)[1].strip():
            pend = True
        if line.startswith(b'RenderDoc: level started') or line.startswith(b'RenderDoc: auto capture') or \
                line.startswith(b'RenderDoc: captured guest flip'):
            rd.append((n, None if start is None else (n - start if n is not None else None),
                       line.decode('utf-8', 'replace').strip()))
dts = [d for _, d in rows]
print('log %s n_start %s rows %d dt_us min %s max %s mean %.0f' % (logp, start, len(rows), min(dts) if dts else None,
                                                                   max(dts) if dts else None,
                                                                   sum(dts) / len(dts) if dts else 0))
print(' '.join('%d:%d' % r for r in rows))
for r in rd[:40]:
    print('RD n_before %s dn %s | %s' % r)
