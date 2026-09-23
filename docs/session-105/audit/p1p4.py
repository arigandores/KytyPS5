"""Independent recount of P1 (ctx105), P4 (ect105_*), screen (reg105a/b). Own code."""
import re, json, statistics, collections, sys
R = 'C:/kyty/s105'
TOK = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')
BAD = [b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---',
       b'ErrorDeviceLost', b'Unhandled exception', b'GpuWaitSlow:', b'GpuHangAbort', b'CtxCheck',
       b'AsyncPipelines: skipped draw', b'GpuClockPin: mode', b'RecordThread: started', b'DeviceLost']

def load(tag):
    main, x = {}, {}
    mk = collections.Counter(); mids = collections.Counter()
    for path in ('%s/log_%s.txt' % (R, tag), '%s/stdout_%s.txt' % (R, tag)):
        try:
            f = open(path, 'rb')
        except OSError:
            continue
        with f:
            for line in f:
                if line.startswith(b'FrameTrace: '):
                    d = {k.decode(): int(v) for k, v in TOK.findall(line)}; main[d['n']] = d
                elif line.startswith(b'FrameTrace-x: '):
                    d = {k.decode(): int(v) for k, v in TOK.findall(line)}; x[d['n']] = d
                elif line.startswith(b'FrameTrace-submit'):
                    for m in re.finditer(rb'(ctx-mid:[^=\s]+)=', line):
                        mids[m.group(1).decode()] += 1
                else:
                    for b in BAD:
                        if b in line:
                            mk[b.decode()] += 1
    return main, x, mk, mids

out = {}
main, x, mk, mids = load('ctx105')
meta = json.load(open(R + '/ctx105.json', encoding='utf-8'))
stable = meta['attempts'][-1]['stable_frame']
keys = ['ctx_chk_n', 'ctx_chk_bad', 'ctx_midsub', 'ctx_rec_block']
tot = {k: sum(d.get(k, 0) for d in x.values()) for k in keys}
pres = {k: sum(k in d for d in x.values()) for k in keys}
res = {'x_lines': len(x), 'present': pres, 'totals': tot, 'markers': dict(mk), 'ctx_mid_rows': dict(mids),
       'stable_frame': stable}
for label, lo in (('from_stable', stable), ('from_n1000', 1000), ('from_n2100', 2100)):
    ns = [n for n in main if n >= lo and n in x]
    chk = [x[n]['ctx_chk_n'] for n in ns]
    work = [main[n]['draws'] + main[n]['dispatches'] for n in ns]
    ratio = [c / w for c, w in zip(chk, work) if w]
    res[label] = {'flips': len(ns), 'median_chk': statistics.median(chk), 'median_work': statistics.median(work),
                  'flips_chk_lt_work': sum(c < w for c, w in zip(chk, work)),
                  'min_ratio': round(min(ratio), 4), 'median_ratio': round(statistics.median(ratio), 4)}
out['P1'] = res

p4 = []
for i in range(1, 11):
    tag = 'ect105_%02d' % i
    main, x, mk, mids = load(tag)
    m = json.load(open('%s/%s.json' % (R, tag), encoding='utf-8'))
    a = m['attempts']
    p4.append({'tag': tag, 'attempts': [(t['outcome'], t['hold_exit'], t['stable_s']) for t in a],
               'bin': m['binary_sha256'][:8], 'ctxtick2': m['gates'].endswith('ctxtick=2'),
               'chk_n': sum(d.get('ctx_chk_n', 0) for d in x.values()),
               'chk_bad': sum(d.get('ctx_chk_bad', 0) for d in x.values()),
               'midsub': sum(d.get('ctx_midsub', 0) for d in x.values()),
               'rec_block': sum(d.get('ctx_rec_block', 0) for d in x.values()),
               'markers': dict(mk), 'last_n': max(main) if main else None})
out['P4'] = p4

def screen(tag):
    main, x, mk, mids = load(tag)
    ns = sorted(main)
    w = ns[len(ns) // 3: 2 * len(ns) // 3]
    return {'rows': len(ns), 'mid_rows': len(w),
            'cpu_per_draw': sum(main[n]['cpu_gpu_us'] for n in w) / sum(main[n]['draws'] for n in w),
            'mean_dt': statistics.fmean(main[n]['dt_us'] for n in w), 'markers': dict(mk)}
a, b = screen('reg105a'), screen('reg105b')
out['screen'] = {'a': a, 'b': b, 'rel_cpu_per_draw_pct': 100 * (b['cpu_per_draw'] / a['cpu_per_draw'] - 1)}
print(json.dumps(out, indent=1))
