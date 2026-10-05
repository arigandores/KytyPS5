import json, statistics as st
NL = chr(10)
S = [('f20_v07', 7750), ('f20_v18', 9198), ('f20_v21', 2828), ('f20_v21', 3025), ('f20_v21', 3108), ('f20_v21', 3193), ('f20_v35', 8487),
     ('f20_v25', 2530), ('f20_v26', 2478), ('f20_v29', 2506), ('f20_v30', 2464), ('f20_v32', 2442), ('f20_v33', 2492), ('f20_v34', 2505)]
T = set(S)
ALWAYS = ['x.gw_idle_ns', 'x.gw_blk_ns', 'x.gw_blk_n', 'x.gw_cmd_ns', 'x.gw_flip_ns', 'x.gw_proc_ns', 'x.gw_idle_n', 'x.flip_rsv_wait_ns', 'x.mh_pres_wait_us',
          'x.a_wait_us', 'x.cs_sync_wait_us', 'x.pb_wait_gpu_us', 'draw.rec_idle_us', 'draw.hostread_wait_us', 'draw.acopy_wait_us', 'submit.wait-flip-done_us', 'wrm_stalls']
def us(k, v):
    return v / 1000.0 if k.endswith('_ns') else float(v)
out = []
for tag, n in S:
    r = json.load(open('C:/kyty/f287/f20g/scan_%s.json' % tag))
    fr = r['frames']
    ok = lambda m: str(m) in fr and (tag, m) not in T and fr[str(m)]['ft'].get('dt_us', 0) < 100000
    nb = [m for m in range(n - 1, n - 15, -1) if ok(m)][:10] + [m for m in range(n + 1, n + 15) if ok(m)][:10]
    f = fr[str(n)]['ft']
    def med(k):
        return st.median([fr[str(m)]['ft'].get(k, 0) for m in nb])
    out.append('%s n=%d dt=%d (median %d)' % (tag, n, f['dt_us'], med('dt_us')))
    out.append('  fixed: ' + '  '.join('%s=%.0f/%.0f' % (k, us(k, f.get(k, 0)), us(k, med(k))) for k in ALWAYS))
    rows = []
    for k, v in f.items():
        if not (k.endswith('_us') or k.endswith('_ns')):
            continue
        m = med(k)
        e = us(k, v) - us(k, m)
        if e >= 10000:
            rows.append((e, k, us(k, v), us(k, m)))
    rows.sort(reverse=True)
    out.append('  time fields with excess >= 10 ms (us): ' + '; '.join('%s %.0f/%.0f' % (k, v, m) for e, k, v, m in rows[:30]))
open('C:/kyty/f287/f20g/time14.txt', 'w').write(NL.join(out) + NL)
print('ok')
