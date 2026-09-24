# Extra checks on shn113: totals, sync-compile per arm, and off-by-one sensitivity of the row index.
import csv, math, statistics
rows = list(csv.DictReader(open('C:/kyty/s113/audit113/final/recount/shn113_rows.csv')))
by = {int(r['n']): r for r in rows}
def iv(x): return 0 if x == '' else int(x)
tot = {k: sum(iv(r['X:' + k]) for r in rows) for k in ['bda_nwould','bda_nmiss','bda_nxthr','bda_nrace','prio_stall','cs_sync_new','cs_sync_wait']}
print('totals all rows', tot)
present = {k: sum(1 for r in rows if r['X:' + k] != '') for k in ['cs_sync_new','bda_nskip']}
print('present', present, 'rows', len(rows))
sync = {0: 0, 1: 0}; nsk0 = 0; nsk0_all = 0
for n, r in by.items():
    if n >= 1801:
        a = int(r['M:arm'])
        if a == 0: nsk0_all += iv(r['X:bda_nskip'])
    if n >= 2100 and n >= 1801:
        sync[int(r['M:arm'])] += iv(r['X:cs_sync_new'])
print('cs_sync_new from 2100 by arm', sync, 'arm0 bda_nskip total (scheduled rows)', nsk0_all)
# row-index sensitivity: shift the block window by s rows
def ana(shift, lo=10, hi=89, key='M:dt_us'):
    ds = []
    for q in range(1, 60):
        m = []
        ok = True
        for i in range(4):
            b = 4 * q + i; first = 1801 + 90 * b + shift
            ns = list(range(first + lo, first + hi + 1))
            if ns[-1] > max(by): ok = False; break
            m.append(statistics.fmean(iv(by[n][key]) for n in ns))
        if not ok: break
        ds += [m[1] - m[0], m[2] - m[3]]
    n = len(ds); mu = statistics.fmean(ds); se = statistics.stdev(ds) / math.sqrt(n)
    return n, round(mu, 2), round(2 * se, 2), round(mu / se, 3)
for s in (-1, 0, 1):
    print('shift', s, 'dt main', ana(s))
print('rows 0..89 (whole block)', ana(0, 0, 89))
