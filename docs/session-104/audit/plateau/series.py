import sys, statistics, collections
sys.path.insert(0, 'C:/kyty/s104/audit104/plateau')
from parse import parse
V = 1e6 / 60.0
p = sys.argv[1]
step = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
d = parse(p)
rows, order = d['rows'], d['order']
ns = [n for n in order if 'dt_us' in rows[n]]
for i in range(0, len(ns), step):
    sel = [rows[n] for n in ns[i:i + step]]
    dt = [r['dt_us'] for r in sel]
    h = collections.Counter(min(round(x / V), 4) for x in dt)
    cg = sum(r.get('cpu_gpu_us', 0) for r in sel)
    print('%6d..%6d n0=%6d mean=%7.0f med=%7.0f 1v=%5.1f%% 2v=%5.1f%% 3v=%5.1f%% busy=%.3f cpu/fr=%6.0f draws=%5.0f lat=%6.0f gpu=%6.0f' % (
        i, i + len(sel), sel[0]['n'], statistics.fmean(dt), statistics.median(dt), 100 * h[1] / len(dt),
        100 * h[2] / len(dt), 100 * h[3] / len(dt), cg / sum(dt), cg / len(dt),
        statistics.fmean(r.get('draws', 0) for r in sel), statistics.fmean(r.get('lat_us', 0) for r in sel),
        statistics.fmean(r.get('gpu_busy_us', 0) for r in sel)))
