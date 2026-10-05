import json, sys, statistics as st
NL = chr(10)
MAIN = [('f20_v07', 7750), ('f20_v18', 9198), ('f20_v21', 2828), ('f20_v21', 3025), ('f20_v21', 3108), ('f20_v21', 3193), ('f20_v35', 8487)]
B5 = [('f20_v25', 2530), ('f20_v26', 2478), ('f20_v29', 2506), ('f20_v30', 2464), ('f20_v32', 2442), ('f20_v33', 2492), ('f20_v34', 2505)]
CORE = ['dt_us', 'lat_us', 'cpu_main_us', 'cpu_gpu_us', 'cpu_present_us', 'cpu_proc_us', 'gpu_busy_us', 'gpu_n', 'semwait_us', 'semwaits',
        'submits', 'submit_us', 'draws', 'dispatches', 'faults', 'fault_us', 'wrm_stalls', 'prios', 'prio_us', 'faults_gpu', 'fault_gpu_us',
        'semwait_gpu_us', 'dmas', 'dma_us', 'gpu_proc', 'gpu_idle', 'gpu_blocked']
cache = {}
def load(tag):
    if tag not in cache:
        cache[tag] = json.load(open('C:/kyty/f287/f20g/scan_%s.json' % tag))
    return cache[tag]
def neigh(r, t, targets):
    fr = r['frames']
    ok = lambda n: str(n) in fr and n not in targets and fr[str(n)]['ft'].get('dt_us', 0) < 100000
    before = [n for n in range(t - 1, t - 15, -1) if ok(n)][:10]
    after = [n for n in range(t + 1, t + 15) if ok(n)][:10]
    return before + after
def tid_gaps(rec, nxt_prev=None):
    # per tid: largest silence touching the interval = max(first call - prev call, consecutive gaps)
    out = {}
    calls = {}
    for tid, t, fn in rec['th']:
        calls.setdefault(str(tid), []).append(t)
    for tid, ts in calls.items():
        p = rec['prev'].get(tid)
        seq = ([p] if p is not None else []) + ts
        g = max([b - a for a, b in zip(seq, seq[1:])] or [0])
        out[tid] = (g, len(ts))
    return out
def report(set_name, items, lines, summ):
    lines.append('=' * 100)
    lines.append('SET ' + set_name)
    for tag, t in items:
        r = load(tag)
        targets = set(n for tg, n in MAIN + B5 if tg == tag)
        fr = r['frames']
        rec = fr[str(t)]
        nb = neigh(r, t, targets)
        lines.append('-' * 100)
        lines.append('%s n=%d  log line %d  neighbours %d: %s' % (tag, t, rec['ln'], len(nb), ','.join(str(x) for x in nb)))
        med = {}
        keys = set(rec['ft'])
        for k in keys:
            vals = [fr[str(n)]['ft'].get(k) for n in nb if fr[str(n)]['ft'].get(k) is not None]
            if vals:
                med[k] = st.median(vals)
        row = {}
        lines.append('  core field: value / median of neighbours / excess')
        for k in CORE:
            v = rec['ft'].get(k)
            if v is None:
                continue
            m = med.get(k, 0)
            row[k] = (v, m)
            lines.append('    %-16s %10d %12.1f %+12.1f' % (k, v, m, v - m))
        dt = rec['ft']['dt_us']; mdt = med['dt_us']
        lines.append('  cores busy (cpu_proc_us/dt_us): frame %.2f, neighbours median %.2f' % (rec['ft']['cpu_proc_us'] / dt,
                     st.median([fr[str(n)]['ft']['cpu_proc_us'] / fr[str(n)]['ft']['dt_us'] for n in nb])))
        # all fields with large relative growth
        big = []
        for k in keys:
            if k in CORE:
                continue
            v = rec['ft'][k]; m = med.get(k, 0)
            if v - m >= 5000 and k.endswith('_us') or (v >= 3 * max(m, 1) and v - m >= 50 and not k.endswith('_us')) or (k.endswith('_us') and v - m >= 5000):
                big.append((v - m, k, v, m))
        big.sort(reverse=True)
        lines.append('  other fields grown (us: excess >= 5000; counts: >= 3x and +50): ' + str(len(big)))
        for e, k, v, m in big[:25]:
            lines.append('    %-34s %10d %12.1f %+12.1f' % (k, v, m, e))
        # interval kinds
        kd = rec['kinds']
        nbk = [fr[str(n)]['kinds'] for n in nb]
        allk = set(kd)
        for x in nbk:
            allk |= set(x)
        diff = []
        for k in sorted(allk):
            v = kd.get(k, 0)
            vals = [x.get(k, 0) for x in nbk]
            mx = max(vals); mn = min(vals); md = st.median(vals)
            if v > mx or v < mn:
                diff.append('    %-50s frame %6d  neighbours min %6d med %8.1f max %6d' % (k[:50], v, mn, md, mx))
        lines.append('  interval lines %d (neighbours median %.1f); line kinds outside the neighbours range: %d' % (rec['iv_lines'],
                     st.median([fr[str(n)]['iv_lines'] for n in nb]), len(diff)))
        lines.extend(diff[:40])
        lines.append('  raw non-argument lines of the interval (%d):' % len(rec['raw']))
        for s in rec['raw'][:20]:
            lines.append('    | ' + s[:200])
        lines.append('  thread calls in the interval:')
        for tid, tt, fn in rec['th']:
            lines.append('    [%s] %d.%03d %s' % (tid, tt // 1000, tt % 1000, fn))
        g = tid_gaps(rec)
        lines.append('  per thread largest silence touching the interval, ms (frame / neighbours median / max):')
        tg = {}
        for tid in sorted(g, key=lambda x: int(x)):
            ng = [tid_gaps(fr[str(n)]).get(tid, (None, 0))[0] for n in nb]
            ng = [x for x in ng if x is not None]
            lines.append('    [%s] %6d  / %8.1f / %6d  calls %d' % (tid, g[tid][0], st.median(ng) if ng else -1, max(ng) if ng else -1, g[tid][1]))
            tg[tid] = (g[tid][0], st.median(ng) if ng else None)
        summ.append(dict(set=set_name, tag=tag, n=t, dt=dt, med_dt=mdt, row=row, gaps=tg, big=[(k, v, m) for e, k, v, m in big[:10]],
                         diff=len(diff), raw=rec['raw'][:10]))
def scene_stats(lines):
    lines.append('=' * 100)
    lines.append('SCENE: frames of the scene up to the last target; rows dt >= 100 ms vs all')
    for tag in sorted(cache):
        r = cache[tag]
        cols = r['allft_cols']
        ix = dict((c, i) for i, c in enumerate(cols))
        rows = [x for x in r['allft'] if x[ix['dt_us']] > 0]
        long_ = [x for x in rows if x[ix['dt_us']] >= 100000]
        lines.append('  %s frames %d, >=100 ms %d: %s' % (tag, len(rows), len(long_), ' '.join('n%d:%d/lat%d/main%d/gpu%d/proc%d' % (
            x[ix['n']], x[ix['dt_us']], x[ix['lat_us']], x[ix['cpu_main_us']], x[ix['cpu_gpu_us']], x[ix['cpu_proc_us']]) for x in long_)))
if __name__ == '__main__':
    lines, summ = [], []
    report('MAIN (7 unattributed B32 frames)', MAIN, lines, summ)
    report('CONTROL B5 (7 frames with IR dump in the interval)', B5, lines, summ)
    scene_stats(lines)
    open('C:/kyty/f287/f20g/ana.txt', 'w').write(NL.join(lines) + NL)
    json.dump(summ, open('C:/kyty/f287/f20g/ana_summary.json', 'w'), indent=1)
    print('ok', len(lines))
