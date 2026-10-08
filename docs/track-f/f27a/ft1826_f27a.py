"""F27a (HPP-690, track F): FrameTrace counters of frame n 1826 of ednn122 against the frames n 1700..1950 (without
1826) - every counter whose value at n 1826 exceeds the maximum of the neighbours, plus the main line of n 1825..1827.
Offline, read-only.  Usage: python ft1826_f27a.py [log]"""
import re
import statistics
import sys

path = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s122/log_ednn122.txt'
F = {}
main = {}
with open(path, 'rb') as f:
    for i, l in enumerate(f):
        if i + 1 < 400000:
            continue
        if i + 1 > 440000:
            break
        s = l.decode('utf-8', 'replace').rstrip()
        m = re.match(r'(FrameTrace(?:-\w+)?): n=(\d+) (.*)', s)
        if not m:
            continue
        n = int(m.group(2))
        d = F.setdefault(n, {})
        for k, v in re.findall(r'(\w+)=(-?\d+)', m.group(3)):
            d[m.group(1) + '.' + k] = int(v)
        if m.group(1) == 'FrameTrace' and 1825 <= n <= 1827:
            main[n] = (i + 1, s[:420])
ns = [n for n in F if 1700 <= n <= 1950 and n != 1826]
print('neighbours', len(ns), 'frames n 1700..1950 without 1826')
for k in F[1826]:
    vals = [F[n].get(k, 0) for n in ns]
    v = F[1826][k]
    if v > max(vals) and v > 0:
        print('EXCEEDS %-34s n1826=%-8d median=%-8g max=%d' % (k, v, statistics.median(vals), max(vals)))
for k in ('FrameTrace.draws', 'FrameTrace.dispatches', 'FrameTrace.gpu_busy_us', 'FrameTrace.cpu_main_us',
          'FrameTrace.submits', 'FrameTrace-draw.p_reads', 'FrameTrace-draw.m_insts'):
    vals = [F[n].get(k, 0) for n in ns]
    print('BELOW/OTHER %-30s n1826=%-8d median=%g' % (k, F[1826][k], statistics.median(vals)))
for n in sorted(main):
    print('LINE', main[n][0], main[n][1])
