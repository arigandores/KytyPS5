# BDA regime survey (audit 112): per run (and per arm for ABBA runs), bda_scan level vs dt level.
import sys, pickle, statistics as st, math, os
sys.path.insert(0, 'C:/kyty/s112/audit112')
from abba112 import load, val

RUNS = [('fam108', 'ABBA cspfam 0|4, s108 build'), ('sf108a', 's108'), ('sf108b', 's108'),
        ('sf108c', 's108 precache gfx'), ('sf108d', 's108 precache gfx'), ('vfm108', 's108 video?'),
        ('vid108', 's108 video'), ('vid108r', 's108 video'), ('frm109', 'ABBA cspfree 0|1 s109'),
        ('vfy109', 's109 verify cspfree=2'), ('shp110', 'ABBA cspfree 0|1 s110'), ('vid110', 's110 video'),
        ('vsh110', 's110 video'), ('obs111', 's111 obs plkstat'), ('shp111', 'ABBA daslot 0|1 s111'),
        ('vds111', 's111 verify (not armed)'), ('vds111b', 's111 verify smemocheck'), ('vid111', 's111 video'),
        ('vss111', 's111 video'), ('vdg112', 'ABBA verify smemocheck s112'), ('net112', 'ABBA daslot1|0guard0 s112'),
        ('vid112', 's112 video')]


def summarize(rows, ns):
    dt = [rows[n]['dt_us'] for n in ns]
    bs = [rows[n]['bda_scan'] for n in ns if 'bda_scan' in rows[n]]
    qc = sum(rows[n].get('da_qcall', 0) for n in ns); qu = sum(rows[n].get('da_queue_us', 0) for n in ns)
    cn = [val(rows[n], 'cpu_net_us') for n in ns]; cn = [x for x in cn if x is not None]
    gb = [rows[n]['gpu_busy_us'] for n in ns if 'gpu_busy_us' in rows[n]]
    wk = [rows[n].get('da_walk_us', 0) for n in ns]
    v1 = sum(1 for x in dt if x < 25000) / len(dt)
    return dict(n=len(ns), dt_mean=st.fmean(dt), dt_med=st.median(dt), vbl1=v1,
                bda_med=st.median(bs) if bs else None, bda_mean=st.fmean(bs) if bs else None,
                bda_old=sum(1 for x in bs if x > 400) / len(bs) if bs else None,
                qpc=qu / qc if qc else None, cpu_net=st.fmean(cn) if cn else None, gpu=st.fmean(gb) if gb else None,
                walk=st.fmean(wk), qcall=qc / len(ns))


out = []
for tag, note in RUNS:
    if not os.path.exists('C:/kyty/s112/audit112/pkl/%s.pkl' % tag):
        print(tag, 'missing'); continue
    P = load(tag); rows = P['rows']
    ns = sorted(n for n in rows if n >= 2100 and 'dt_us' in rows[n] and 'cpu_gpu_us' in rows[n])
    if not ns:
        print(tag, 'no rows'); continue
    groups = [('all', ns)]
    if P['gates']:
        for a in (0, 1):
            groups.append(('arm%d' % a, [n for n in ns if rows[n].get('arm') == a]))
    for g, sel in groups:
        if not sel: continue
        s = summarize(rows, sel)
        out.append((tag, g, s))
        print('%-8s %-5s %-34s n %5d dt mean %8.1f med %8.1f vbl1 %.3f | bda_scan med %7.1f mean %7.1f OLDfrac %.3f | q/call %s cpu_net %8.1f gpu %8.1f walk %7.1f qcall %6.1f' % (
            tag, g, note, s['n'], s['dt_mean'], s['dt_med'], s['vbl1'], s['bda_med'] or -1, s['bda_mean'] or -1,
            s['bda_old'] if s['bda_old'] is not None else -1, '%.3f' % s['qpc'] if s['qpc'] else '  -  ',
            s['cpu_net'] or -1, s['gpu'] or -1, s['walk'], s['qcall']))
pickle.dump(out, open('C:/kyty/s112/audit112/regime.pkl', 'wb'))
