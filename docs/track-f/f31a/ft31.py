# F31a: per-frame FrameTrace fields after the entry of a scene, for the comparison of the assert log with the same scene on
# T and on the line.  usage: python ft31.py <scene> <out.tsv> <log> [<log> ...]
# Prints per log: frames, the distribution of draws / dispatches / submits / dt over the hold, the same for frames
# [k-300, k) where k = the last frame (assert log) or the frame at the same hold time, and the max over the hold.
import mmap, re, statistics, sys
scene = sys.argv[1].encode()
out = sys.argv[2]
FT = re.compile(rb'\nFrameTrace: n=(\d+) dt_us=(\d+) lat_us=(\d+).*? submits=(\d+).*? semwaits=(\d+) semwait_us=(\d+).*? draws=(\d+).*? dispatches=(\d+).*? faults=(\d+)')
rows = []
def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))] if v else None
with open(out, 'w', encoding='utf-8', newline='\n') as o:
    o.write('log\tn\tt_hold_s\tdt_us\tlat_us\tsubmits\tsemwaits\tsemwait_us\tdraws\tdispatches\tfaults\n')
    for path in sys.argv[3:]:
        f = open(path, 'rb'); m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        e = m.find(b'Level has started: ' + scene)
        fr = []
        t = 0
        for x in FT.finditer(m, e):
            n, dt, lat, sub, sw, swu, dr, di, fa = (int(g) for g in x.groups())
            t += dt
            fr.append((n, t / 1e6, dt, lat, sub, sw, swu, dr, di, fa))
        name = path.rsplit('/', 1)[1]
        for r in fr:
            o.write(name + '\t' + '\t'.join(str(round(v, 3)) if isinstance(v, float) else str(v) for v in r) + '\n')
        dr = [r[7] for r in fr]; di = [r[8] for r in fr]; su = [r[4] for r in fr]; dt = [r[2] for r in fr]
        print('%s frames %d hold %.1f s | draws med %d p99 %d max %d | disp med %d max %d | submits med %d max %d | dt med %d p99 %d max %d'
              % (name, len(fr), fr[-1][1] if fr else 0, q(dr, .5), q(dr, .99), max(dr), q(di, .5), max(di), q(su, .5), max(su), q(dt, .5), q(dt, .99), max(dt)))
        # window ending at hold 151.2 s
        w = [r for r in fr if 141.2 <= r[1] <= 151.2]
        if w:
            print('    window hold 141.2-151.2 s: frames %d draws med %d max %d disp max %d submits max %d dt max %d'
                  % (len(w), q([r[7] for r in w], .5), max(r[7] for r in w), max(r[8] for r in w), max(r[4] for r in w), max(r[2] for r in w)))
        tail = fr[-12:]
        print('    last frames: ' + ' '.join('n%d:d%d/c%d/s%d/%dms' % (r[0], r[7], r[8], r[4], r[2] // 1000) for r in tail))
        m.close(); f.close()
