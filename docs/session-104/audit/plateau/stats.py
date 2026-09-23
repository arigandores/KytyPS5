import sys, statistics, collections
sys.path.insert(0, 'C:/kyty/s104/audit104/plateau')
from parse import parse
V = 1e6 / 60.0


def window(rows, order, lo=1 / 3, hi=2 / 3):
    ns = [n for n in order if 'dt_us' in rows[n]]
    a, b = int(len(ns) * lo), int(len(ns) * hi)
    return [rows[n] for n in ns[a:b]]


def summ(sel, label=''):
    dt = [r['dt_us'] for r in sel]
    if not dt:
        return None
    hist = collections.Counter(min(round(d / V), 5) for d in dt)
    n = len(dt)
    cg = sum(r.get('cpu_gpu_us', 0) for r in sel)
    sp = sum(r.get('spin_gpu_us', 0) for r in sel)
    sdt = sum(dt)
    wfd = sum(r.get('wfd_us', 0) for r in sel)
    wfdn = sum(r.get('wfd_n', 0) for r in sel)
    lat = [r.get('lat_us', 0) for r in sel]
    out = dict(n=n, mean=sdt / n, med=statistics.median(dt),
               h={k: round(100 * v / n, 1) for k, v in sorted(hist.items())},
               busy=cg / sdt, net=(cg - sp) / sdt, spin_fr=sp / n, cpu_fr=cg / n,
               idle_fr=(sdt - cg) / n, lat_mean=statistics.fmean(lat), lat_med=statistics.median(lat),
               wfd_fr=wfd / n, wfdn_fr=wfdn / n,
               draws=statistics.fmean(r.get('draws', 0) for r in sel),
               gpu=statistics.fmean(r.get('gpu_busy_us', 0) for r in sel))
    return out


def fmt(o):
    return ('n=%5d mean=%8.1f med=%8.1f vbl%%=%s busy=%.4f net=%.4f cpu/fr=%.0f idle/fr=%.0f spin/fr=%.0f '
            'lat=%.0f/%.0f wfd_us/fr=%.1f wfd_n/fr=%.2f draws=%.0f gpu=%.0f') % (
        o['n'], o['mean'], o['med'], o['h'], o['busy'], o['net'], o['cpu_fr'], o['idle_fr'], o['spin_fr'],
        o['lat_mean'], o['lat_med'], o['wfd_fr'], o['wfdn_fr'], o['draws'], o['gpu'])


if __name__ == '__main__':
    for p in sys.argv[1:]:
        d = parse(p)
        rows, order = d['rows'], d['order']
        print(p)
        print('  mid-third', fmt(summ(window(rows, order))))
        print('  whole    ', fmt(summ(window(rows, order, 0.0, 1.0))))
        # sliding thirds
        for lo in (0.0, 0.33, 0.66):
            s = summ(window(rows, order, lo, lo + 0.34))
            print('  %.2f-%.2f' % (lo, lo + .34), fmt(s))
