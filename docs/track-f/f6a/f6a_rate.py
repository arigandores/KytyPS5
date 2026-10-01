# F6a (HPP-372): stub calls per shown frame in a log: FrameTrace lines between stub-call lines. usage: f6a_rate.py <log>
import sys, re, collections
rx = re.compile(rb'Unresolved import stub called \[(\d+)\]: .*symbol=([^\[]+)\[AudioPropagation')
frames = 0; per = []; cur = collections.Counter(); started = False; first_ft = None; lvl = None; n = 0; ft_at_first = None; ft_at_last = None; ft_lvl = None
dts = []
with open(sys.argv[1], 'rb') as f:
    for line in f:
        n += 1
        if b'FrameTrace' in line and b'dt_us' in line:
            frames += 1
            if started:
                per.append(cur); cur = collections.Counter()
            m = re.search(rb'dt_us=(\d+)', line)
            if m and started: dts.append(int(m.group(1)))
            continue
        if b'Level has started: timestop_casino' in line: ft_lvl = frames
        m = rx.search(line)
        if m:
            s = m.group(2).decode()
            if s in ('d84otraxt2s',) and not started: started = True; ft_at_first = frames
            if started: cur[s] += 1
            if int(m.group(1)) == 1023: ft_at_last = frames; break
print('FrameTrace lines before level line: %s; at first SourceCreate: %s; at stub call #1023: %s' % (ft_lvl, ft_at_first, ft_at_last))
nfr = len(per)
tot = collections.Counter()
for c in per: tot.update(c)
print('frames between first SourceCreate and call #1023: %d; sum dt_us of them %d us' % (nfr, sum(dts)))
for k, v in tot.items(): print('  %s: %d calls, %.3f per frame' % (k, v, v / max(1, nfr)))
h = collections.Counter(tuple(sorted(c.items())) for c in per)
for k, v in h.most_common(8): print('  %5d frames with %s' % (v, dict(k)))
