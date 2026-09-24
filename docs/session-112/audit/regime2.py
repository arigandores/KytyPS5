# BDA-regime indication (audit 112): per run / per ABBA arm, from frame 2100 on (all rows, not only 10..89).
# OLD = bda_scan median > 400 a frame, NEW = < 400. Indication only: builds, configs and days differ between runs.
import pickle, statistics as st
R = pickle.load(open('C:/kyty/s112/audit112/regime.pkl', 'rb'))
S = {(t, g): s for t, g, s in R}
# comparable Sky Garden, pinned, 600 s ABBA arms (shipping-like config; arm label = what differs)
ABBA = [('fam108', 'arm0', 's108 cspfam=0'), ('fam108', 'arm1', 's108 cspfam=4'),
        ('frm109', 'arm0', 's109 cspfree=0'), ('frm109', 'arm1', 's109 cspfree=1'),
        ('shp110', 'arm0', 's110 cspfree=0'), ('shp110', 'arm1', 's110 cspfree=1'),
        ('shp111', 'arm0', 's111 daslot=0 guards'), ('shp111', 'arm1', 's111 daslot=1'),
        ('net112', 'arm0', 's112 daslot=1'), ('net112', 'arm1', 's112 daslot=0 daguard=0')]
OTHER = [('sf108c', 'all', 's108 precache gfx, 300 s'), ('sf108d', 'all', 's108 precache gfx cspfam=4, 300 s'),
         ('vfy109', 'all', 's109 cspfree=2 verify, 300 s'), ('vds111', 'all', 's111 daslot=2 (smemocheck unarmed), 300 s'),
         ('obs111', 'all', 's110 build, plkstat, 300 s')]
VID = [('vid108', 'all', 's108 video'), ('vid108r', 'all', 's108 reverted video'), ('vsh110', 'all', 's110 video'),
       ('vid110', 'all', 's110 video'), ('vid111', 'all', 's111 video'), ('vss111', 'all', 's111 video'),
       ('vid112', 'all', 's112 video'), ('vfm108', 'all', 's108 video?')]


def show(title, lst):
    print('==', title)
    groups = {'OLD': [], 'NEW': []}
    for t, g, lab in lst:
        s = S[(t, g)]
        reg = 'OLD' if s['bda_med'] > 400 else 'NEW'
        groups[reg].append(s)
        print('  %-8s %-5s %-38s %s bda_scan %7.1f  dt %8.1f  cpu_net %8.1f  gpu %8.1f  vbl1 %.3f  q/call %.3f  n %d' % (
            t, g, lab, reg, s['bda_mean'], s['dt_mean'], s['cpu_net'], s['gpu'], s['vbl1'], s['qpc'] or 0, s['n']))
    for reg, v in groups.items():
        if v:
            print('   %s: runs %d  mean dt %.1f  mean cpu_net %.1f  mean vbl1 %.3f' % (
                reg, len(v), st.fmean(x['dt_mean'] for x in v), st.fmean(x['cpu_net'] for x in v),
                st.fmean(x['vbl1'] for x in v)))
    if groups['OLD'] and groups['NEW']:
        print('   OLD - NEW: dt %+.1f  cpu_net %+.1f' % (
            st.fmean(x['dt_mean'] for x in groups['OLD']) - st.fmean(x['dt_mean'] for x in groups['NEW']),
            st.fmean(x['cpu_net'] for x in groups['OLD']) - st.fmean(x['cpu_net'] for x in groups['NEW'])))


show('600 s pinned ABBA arms (Sky Garden)', ABBA)
show('300 s single-config runs', OTHER)
show('120 s recorded videos', VID)
print('== matched pairs (same code at the compared setting, different regime)')
pairs = [(('frm109', 'arm0'), ('shp110', 'arm0'), 'cspfree=0, s109 (OLD) vs s110 (NEW)'),
         (('frm109', 'arm1'), ('shp110', 'arm1'), 'cspfree=1, s109 (OLD) vs s110 (NEW)'),
         (('shp111', 'arm1'), ('net112', 'arm0'), 'daslot=1, 0c8a13f2 (OLD) vs b47b58a9 (NEW)'),
         (('vid110', 'all'), ('vsh110', 'all'), 'video, s110 cspfree=1 (OLD) vs s110 ship candidate (NEW)'),
         (('vid108r', 'all'), ('vid108', 'all'), 'video, s108 reverted (OLD) vs cspfam=4 (NEW)')]
for a, b, lab in pairs:
    sa, sb = S[a], S[b]
    print('  %-58s OLD-NEW dt %+7.1f  cpu_net %+7.1f  gpu %+7.1f  vbl1 %+.3f' % (
        lab, sa['dt_mean'] - sb['dt_mean'], sa['cpu_net'] - sb['cpu_net'], sa['gpu'] - sb['gpu'], sa['vbl1'] - sb['vbl1']))
