# Independent ABBA recount for shn113 from the extracted CSV.
import csv, math, statistics, json, sys
rows = list(csv.DictReader(open('C:/kyty/s113/audit113/final/recount/shn113_rows.csv')))
def iv(x): return None if x == '' else int(x)
by = {int(r['n']): r for r in rows}
N0, P, START = 1800, 90, 2100
nmax = max(by)
def block_rows(b):
    first = N0 + 1 + P * b          # rows carry blk shifted: block b = n in [1801+90b, 1890+90b]
    ns = list(range(first, first + P))
    if ns[-1] > nmax: return None
    for n in ns: assert int(by[n]['M:blk']) == b, (b, n)
    return ns
def field(r, k):
    if k == 'cpu_net_us': return iv(r['M:cpu_gpu_us']) - iv(r['D:spin_gpu_us'])
    for p in ('M:', 'D:', 'X:'):
        if p + k in r and r[p + k] != '': return iv(r[p + k])
    raise KeyError(k)
ARM = [0, 1, 1, 0]
def analyse(lo, hi, key):
    ds = []; orient = [0, 0]; used = []
    q = 0
    while True:
        bl = [block_rows(4 * q + i) for i in range(4)]
        if bl[0] is None: break
        if any(b is None for b in bl): break
        if (N0 + 1 + P * 4 * q) < START:      # quartet starts before the analysis start -> partial, excluded
            q += 1; continue
        m = []
        for i in range(4):
            sel = bl[i][lo:hi + 1]
            m.append(statistics.fmean(field(by[n], key) for n in sel))
            assert all(int(by[n]['M:arm']) == ARM[i] for n in bl[i])
        ds.append(m[1] - m[0]); orient[0] += 1
        ds.append(m[2] - m[3]); orient[1] += 1
        used += [4 * q + i for i in range(4)]
        q += 1
    n = len(ds); mean = statistics.fmean(ds); sd = statistics.stdev(ds); se = sd / math.sqrt(n)
    return {'n': n, 'mean': mean, 'sd': sd, 'se': se, '2se': 2 * se, 't': mean / se, 'orient': orient,
            'blocks': len(used), 'first_block': used[0], 'last_block': used[-1]}
def levels(key, lo=10, hi=89):
    lv = {0: [], 1: []}
    q = 1
    while True:
        bl = [block_rows(4 * q + i) for i in range(4)]
        if any(b is None for b in bl): break
        for i in range(4):
            lv[ARM[i]].append(statistics.fmean(field(by[n], key) for n in bl[i][lo:hi + 1]))
        q += 1
    return {a: statistics.median(v) for a, v in lv.items()}, {a: len(v) for a, v in lv.items()}
out = {}
for k in ['dt_us', 'cpu_net_us', 'gpu_busy_us', 'da_miss', 'da_take_us', 'draws', 'rec_n']:
    out['main_' + k] = analyse(10, 89, k)
for k in ['dt_us', 'cpu_net_us']:
    out['secondary_' + k] = analyse(60, 88, k)
for k in ['bda_scan', 'bda_nskip', 'dt_us', 'gpu_busy_us', 'rec_n', 'bda_ginv_reg', 'bgc_evict']:
    out['level_' + k] = levels(k)
json.dump(out, open('C:/kyty/s113/audit113/final/recount/abba_shn113.json', 'w'), indent=1)
for k, v in out.items():
    if k.startswith('main') or k.startswith('secondary'):
        print(f"{k:24s} n {v['n']} mean {v['mean']:.3f} sd {v['sd']:.3f} 2SE {v['2se']:.3f} t {v['t']:.3f} orient {v['orient']} blocks {v['blocks']} [{v['first_block']}..{v['last_block']}]")
    else:
        print(k, v)
