"""Per presentation-interval class (1/2/3 vblanks): draws, cpu_gpu, busy, lat, in a window.
If GuestGpu processes a continuous stream sliced by the tick, draws per interval scale with dt;
if processing were frame-locked to presentation, draws per interval would be ~one frame each."""
import sys, statistics, collections
sys.path.insert(0, 'C:/kyty/s104/audit104/plateau')
from parse import parse
V = 1e6 / 60.0


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(q * len(v)))]


for spec in sys.argv[1:]:
    p, lo, hi = spec.split(',')
    d = parse(p)
    rows, order = d['rows'], d['order']
    ns = [n for n in order if 'dt_us' in rows[n]]
    a, b = int(len(ns) * float(lo)), int(len(ns) * float(hi))
    sel = [rows[n] for n in ns[a:b]]
    print(p, lo, hi, 'n=%d' % len(sel))
    g = collections.defaultdict(list)
    for r in sel:
        g[min(round(r['dt_us'] / V), 4)].append(r)
    for k in sorted(g):
        rs = g[k]
        if len(rs) < 5:
            continue
        dt = statistics.fmean(r['dt_us'] for r in rs)
        print('  %dv n=%5d dt=%7.0f draws=%6.0f draws/ms=%6.1f cpu=%7.0f busy=%.3f lat mean=%6.0f p95=%6.0f max=%6.0f gpu=%6.0f' % (
            k, len(rs), dt, statistics.fmean(r['draws'] for r in rs),
            statistics.fmean(r['draws'] for r in rs) / dt * 1000, statistics.fmean(r['cpu_gpu_us'] for r in rs),
            sum(r['cpu_gpu_us'] for r in rs) / sum(r['dt_us'] for r in rs),
            statistics.fmean(r['lat_us'] for r in rs), pct([r['lat_us'] for r in rs], .95),
            max(r['lat_us'] for r in rs), statistics.fmean(r['gpu_busy_us'] for r in rs)))
    lat = [r['lat_us'] for r in sel]
    print('  lat p50=%d p90=%d p99=%d max=%d  frac>20ms=%.4f frac>25ms=%.4f' % (
        pct(lat, .5), pct(lat, .9), pct(lat, .99), max(lat), sum(x > 20000 for x in lat) / len(lat),
        sum(x > 25000 for x in lat) / len(lat)))
