# Independent recount for vbn113* seal runs. Reads log in binary mode, line by line.
import sys, re, json, statistics
path = sys.argv[1]
stable = int(sys.argv[2]) if len(sys.argv) > 2 else None
XF = ['bda_nwould','bda_nmiss','bda_nxthr','bda_nrace','bda_ginv_reg','bda_ginv_map','bda_rinv','bda_nskip',
      'bgc_evict','prio_unsub','prio_stall','gw_idle_prio','cspfree_hit','cspfree_bad','da_q_free']
DF = ['bda_scan']
MF = ['dt_us','cpu_gpu_us','gpu_busy_us','draws','arm','blk']
tok = re.compile(rb' ([A-Za-z0-9_]+)=(-?\d+)')
def parse(line, want):
    d = {}
    for m in tok.finditer(line):
        k = m.group(1).decode()
        if k in want:
            if k in d:  # duplicate key on a line
                d.setdefault('__dup', []).append(k)
            d[k] = int(m.group(2))
    return d
rows = {'M': {}, 'D': {}, 'X': {}}
dups = {'M': 0, 'D': 0, 'X': 0}
dupkeys = []
gws = []; bgc = []; other = {}
wantM = set(MF+['n']); wantD = set(DF+['n']); wantX = set(XF+['n'])
with open(path, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace: '):
            t, want = 'M', wantM
        elif line.startswith(b'FrameTrace-draw: '):
            t, want = 'D', wantD
        elif line.startswith(b'FrameTrace-x: '):
            t, want = 'X', wantX
        else:
            if b'GpuWaitSlow' in line:
                gws.append(line[:400].decode('latin1').rstrip())
            elif line.startswith(b'BufferGc:'):
                bgc.append(line[:200].decode('latin1').rstrip())
            continue
        d = parse(line, want)
        if '__dup' in d: dupkeys.append((t, d['__dup']))
        n = d.get('n')
        if n in rows[t]: dups[t] += 1
        rows[t][n] = d
out = {'path': path, 'stable_frame': stable}
for t in 'MDX': out['rows_'+t] = len(rows[t]); out['dupn_'+t] = dups[t]
out['dupkeys'] = dupkeys[:5]
for t in 'MDX':
    ks = sorted(rows[t]); out['contig_'+t] = (ks == list(range(ks[0], ks[-1]+1))) if ks else None
out['nsets_equal_MX'] = set(rows['M']) == set(rows['X']); out['nsets_equal_MD'] = set(rows['M']) == set(rows['D'])
out['n_range_M'] = [min(rows['M']), max(rows['M'])] if rows['M'] else None
sums = {k: sum(r.get(k, 0) for r in rows['X'].values()) for k in XF}
present = {k: sum(1 for r in rows['X'].values() if k in r) for k in XF}
out['x_sums_all'] = sums; out['x_present'] = present
if stable is not None:
    sc = [r['bda_scan'] for n, r in rows['D'].items() if n >= stable and 'bda_scan' in r]
    out['scan_rows'] = len(sc)
    out['median_bda_scan_scene'] = statistics.median(sc) if sc else None
    for k in ['bda_ginv_reg','bda_nwould','bgc_evict']:
        v = [r[k] for n, r in rows['X'].items() if n >= stable and k in r]
        out['median_'+k+'_scene'] = statistics.median(v) if v else None
        out['nrows_'+k+'_scene'] = len(v)
    # also median over rows with n > stable
    sc2 = [r['bda_scan'] for n, r in rows['D'].items() if n > stable and 'bda_scan' in r]
    out['median_bda_scan_gt'] = statistics.median(sc2) if sc2 else None
out['GpuWaitSlow_count'] = len(gws); out['GpuWaitSlow_lines'] = gws[:5]
out['BufferGc'] = bgc[:5]
# max dt row
if rows['M']:
    mx = max(rows['M'].items(), key=lambda kv: kv[1].get('dt_us', 0))
    out['max_dt'] = [mx[0], mx[1].get('dt_us')]
print(json.dumps(out, indent=1))
