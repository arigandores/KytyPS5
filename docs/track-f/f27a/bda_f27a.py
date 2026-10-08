"""F27a (HPP-690): bda_scan of the FrameTrace-draw line against dt_us of the main line over the hold of ednn122
(frames > 308): how many frames carry bda_scan >= 900 and their dt.  Offline."""
import re
dt = {}
bda = {}
with open('C:/kyty/s122/log_ednn122.txt', 'rb') as f:
    for l in f:
        m = re.match(rb'FrameTrace: n=(\d+) dt_us=(\d+)', l)
        if m:
            dt[int(m.group(1))] = int(m.group(2))
            continue
        m = re.match(rb'FrameTrace-draw: n=(\d+) .*? bda_scan=(\d+)', l)
        if m:
            bda[int(m.group(1))] = int(m.group(2))
hold = [n for n in dt if n > 308 and n in bda]
big = sorted([(bda[n], n, dt[n]) for n in hold if bda[n] >= 900], reverse=True)
print('hold frames', len(hold), 'with bda_scan >= 900:', len(big))
print('top by bda_scan (bda_scan, n, dt_us):', big[:12])
print('max dt among them excluding 1826:', max([x[2] for x in big if x[1] != 1826] or [0]))
