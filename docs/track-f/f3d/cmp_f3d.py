# F3d (HPP-342): information for the lead (not a gate, not sealed): mean dt_us after the first scene frame, K2, K3 hold count,
# fault pairs and BvhLoopCapTrip of the reference logs, by the same reader functions (sc142 derive + f3d_read helpers).
import os, sys
sys.path.insert(0, 'C:/kyty/f287/f3d')
import f3d_read as R
sc = R.load()
REFS = (('v142', 'C:/kyty/s142/log_v142.txt', R.SKY), ('w142', 'C:/kyty/s142/log_w142.txt', R.SKY),
        ('f2c_a', 'C:/kyty/f287/f2c/log_f2c_a.txt', R.SKY), ('f2c_b', 'C:/kyty/f287/f2c/log_f2c_b.txt', R.SKY),
        ('c142_02', 'C:/kyty/s142/log_c142_02.txt', R.BH), ('c142_09', 'C:/kyty/s142/log_c142_09.txt', R.VW))
for tag, p, lv in REFS:
    if not os.path.isfile(p):
        print(tag, 'missing'); continue
    log = sc.scan(p)
    d = sc.derive(log, lv)
    ex = R.scan_extra(p)
    pages, pairs, lows = R.fault_members(ex['faults'])
    md = R.mean_dt(sc, log, d)
    hf = R.hold_frames(sc, log, d)
    print('%-8s %-25s hold %.1f s mean dt %s K2 %d K3 window %d K3 hold %s pairs %d lows %d trips %d pages %d' % (
        tag, lv, d['dt_after_first_us'] / 1e6, '%.0f' % md if md else None, len(d['k2']), len(d['k3w']),
        len(hf) if hf is not None else None, len(pairs), len(lows), len(log['bvh']), len(pages)))
