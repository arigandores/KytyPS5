import pickle
import statistics
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'C:/kyty/s109/audit109/parsed/%s.pkl'
ORDER = 'ABBAABBA'


def level_frame(d):
    for ln, n, t in d['events']:
        if 'Level has started: underwater' in t:
            return n
    return None


for series in ('ent109', 'ent109b'):
    print('==', series)
    agg = {'A': [], 'B': []}
    for i in range(8):
        tag = '%s_%d' % (series, i + 1)
        arm = ORDER[i]
        d = pickle.load(open(P % tag, 'rb'))
        m, x, dr = d['main'], d['x'], d['draw']
        lf = level_frame(d)
        ev = [n for n, r in sorted(x.items()) if r.get('cs_sync_new', 0) or r.get('cs_sync_wait', 0)]
        ev_dt = [(n, m[n]['dt_us'], m[n].get('cpu_gpu_us'), x[n].get('cs_sync_new', 0), x[n].get('cs_sync_wait', 0)) for n in ev]
        # load window: from level-started frame to +200
        w = [n for n in range(lf, lf + 300) if n in m]
        tot_dt = sum(m[n]['dt_us'] for n in w) / 1e3
        tot_cpu = sum(m[n]['cpu_gpu_us'] for n in w) / 1e3
        new_w = sum(x[n].get('cspf_new', 0) for n in range(lf - 60, lf + 300) if n in x)
        # time from level start to frame with draws >= 3000 (stable scene)
        first_heavy = next((n for n in sorted(m) if n > lf and m[n]['draws'] >= 3000), None)
        t_to_heavy = sum(m[n]['dt_us'] for n in range(lf, first_heavy) if n in m) / 1e3 if first_heavy else None
        pre = [n for n in range(lf - 60, lf) if n in m]
        pre_dt = sum(m[n]['dt_us'] for n in pre) / 1e3
        agg[arm].append((tot_dt, tot_cpu, t_to_heavy, pre_dt))
        print('%-10s %s lvl@%d heavy@%s t(lvl->heavy) %.0f ms  sum dt[lvl,lvl+300) %.0f ms cpu_gpu %.0f ms  pre60 dt %.0f ms  cspf_new(lvl-60..+300) %d' % (
            tag, arm, lf, first_heavy, t_to_heavy or -1, tot_dt, tot_cpu, pre_dt, new_w))
        print('     events (n, dt_us, cpu_gpu_us, new, wait):', ev_dt)
    for a in 'AB':
        v = agg[a]
        print(' arm', a, 'mean t(lvl->heavy) %.0f  mean sum dt300 %.0f  mean cpu300 %.0f  mean pre60 %.0f' % tuple(
            statistics.fmean(z[k] for z in v) for k in (2, 0, 1, 3)))
