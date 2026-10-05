import json, re, datetime, math
NL = chr(10)
out = []
MAIN = [('f20_v07', 'f20c', [7750]), ('f20_v18', 'f20c', [9198]), ('f20_v21', 'f20c', [2828, 3025, 3108, 3193]), ('f20_v35', 'f20e', [8487])]
P = re.compile(rb'Pthread run begin: ([^,]+), id = (\d+), os_thread_id')
for tag, d, ns in MAIN:
    j = json.load(open('C:/kyty/f287/%s/%s.json' % (d, tag)))
    launched = datetime.datetime.fromisoformat(j['launched'])
    r = json.load(open('C:/kyty/f287/f20g/scan_%s.json' % tag))
    names = {}
    with open('C:/kyty/f287/%s/log_%s.txt' % (d, tag), 'rb') as f:
        for i, line in enumerate(f, 1):
            if b'run begin' in line:
                m = P.search(line)
                if m:
                    names[int(m.group(2))] = m.group(1).decode('ascii', 'replace')
            if i > 600000:
                break
    tids = sorted(set(int(t) for t in r['calls']))
    out.append('%s launched %s (local) env FRAME_TRACE=%s; guest threads with stamped calls in the scene: %s' % (
        tag, j['launched'], j['env'].get('KYTY_FRAME_TRACE'), ', '.join('[%d]=%s(%d)' % (t, names.get(t, '?'), len(r['calls'][str(t)])) for t in tids)))
    rows = [l.split(', ') for l in open('C:/kyty/f287/%s/gpuclk_%s.csv' % (d, tag)).read().splitlines()[1:]]
    for n in ns:
        rec = r['frames'][str(n)]
        ts = [t for _, t, _ in rec['th']] or [max(v.get(k, 0) for v in [rec['prev']] for k in v)]
        end_ms = max(ts)
        wall = launched + datetime.timedelta(milliseconds=end_ms)
        out.append('  n=%d dt_us=%d last stamped call %.3f s -> about %s local (+-1 s, launch second)' % (n, rec['ft']['dt_us'], end_ms / 1000, wall.strftime('%H:%M:%S.%f')[:-3]))
        for row in rows:
            try:
                t = datetime.datetime.strptime(row[0], '%Y/%m/%d %H:%M:%S.%f')
            except Exception:
                continue
            if abs((t - wall).total_seconds()) <= 2.6:
                out.append('    gpuclk ' + ' | '.join(row))
S = json.load(open('C:/kyty/f287/f20g/ana_summary.json'))
out.append('')
out.append('process CPU during the excess: (cpu_proc_us - median) / (dt_us - median), cores; cpu_gpu excess; lat excess')
for s in S:
    r = s['row']
    ex_dt = r['dt_us'][0] - r['dt_us'][1]
    ex_p = r['cpu_proc_us'][0] - r['cpu_proc_us'][1]
    out.append('  %-8s %-6s n=%-5d dt=%7d ex_dt=%7.0f ex_proc=%8.0f cores_in_excess=%6.2f ex_gpu=%7.0f ex_lat=%7.0f ex_semwait=%7.0f ex_submit=%7.0f ex_fault=%7.0f' % (
        s['set'][:7], s['tag'][4:], s['n'], s['dt'], ex_dt, ex_p, ex_p / ex_dt, r['cpu_gpu_us'][0] - r['cpu_gpu_us'][1], r['lat_us'][0] - r['lat_us'][1],
        r['semwait_us'][0] - r['semwait_us'][1], r['submit_us'][0] - r['submit_us'][1], r['fault_us'][0] - r['fault_us'][1]))
# scene-wide: frames 34-60 ms vs normal, cores rate; and the fraction of frames with cores < 2
for tag, d, ns in MAIN:
    r = json.load(open('C:/kyty/f287/f20g/scan_%s.json' % tag))
    c = r['allft_cols']; ix = dict((k, i) for i, k in enumerate(c))
    rows = [x for x in r['allft'] if x[ix['dt_us']] > 0 and x[ix['cpu_proc_us']] >= 0]
    rates = sorted(x[ix['cpu_proc_us']] / x[ix['dt_us']] for x in rows)
    low = [x for x in rows if x[ix['cpu_proc_us']] / x[ix['dt_us']] < 2.5]
    out.append('%s scene frames %d: cores median %.2f p05 %.2f; frames with cores < 2.5: %d (dt of them: %s)' % (
        tag, len(rows), rates[len(rates) // 2], rates[len(rates) // 20], len(low), ','.join(str(x[ix['dt_us']] // 1000) for x in low[:30])))
# P(0) table: pooled 4 of 41 holds (F20c 3/30 accepted + F20e 1/11), Jeffreys Beta(4.5, 37.5)
def lbeta(a, b):
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
a, b = 4.5, 37.5
out.append('')
out.append('P(0 events in N holds): fixed p and posterior Beta(4.5, 37.5) (Jeffreys on 4 of 41)')
for N in (11, 20, 29, 40, 45, 60, 61, 80):
    post = math.exp(lbeta(a, b + N) - lbeta(a, b))
    def pk(p, N, kmax):
        return sum(math.comb(N, k) * p ** k * (1 - p) ** (N - k) for k in range(kmax + 1))
    # posterior P(<=2)
    pp2 = sum(math.comb(N, k) * math.exp(lbeta(a + k, b + N - k) - lbeta(a, b)) for k in range(3))
    out.append('  N=%3d  P0 p=0.10 %.3f  p=0.05 %.3f  p=0.021 %.3f  posterior %.3f | P(<3) p=0.10 %.3f posterior %.3f' % (
        N, 0.9 ** N, 0.95 ** N, 0.979 ** N, post, pk(0.10, N, 2), pp2))
open('C:/kyty/f287/f20g/aux_f20g.txt', 'w').write(NL.join(out) + NL)
print('ok')
