import re, json, statistics, math, sys
log, rcj = sys.argv[1], sys.argv[2]
rc = json.load(open(rcj)); B = rc['paired_blocks']
want = [b'dispatches', b'rt_kpx', b'rt_att', b'gpu_n', b'lat_us', b'semwait_gpu_us', b'fault_gpu_us']
rows = {}
NN = re.compile(rb'^FrameTrace(?:-x)?: n=(\d+) ')
for l in open(log, 'rb'):
    if l.startswith(b'FrameTrace: ') or l.startswith(b'FrameTrace-x: '):
        n = int(NN.match(l).group(1)); r = rows.setdefault(n, {})
        for k in want:
            m = re.search(rb' ' + k + rb'=(-?\d+)', l)
            if m and k not in r: r[k] = int(m.group(1))
for k in want:
    bm = {b: statistics.fmean(rows[n].get(k, 0) for n in range(1801 + 90*b, 1891 + 90*b)[60:89]) for b in B}
    d = []
    for q in range(0, max(B) + 1, 4):
        if q in bm: d += [bm[q+1] - bm[q], bm[q+2] - bm[q+3]]
    m = statistics.fmean(d); se = statistics.stdev(d) / math.sqrt(len(d)) if statistics.stdev(d) > 0 else 0
    print('%-16s d %.2f t %s' % (k.decode(), m, round(m / se, 2) if se else 'n/a'))
