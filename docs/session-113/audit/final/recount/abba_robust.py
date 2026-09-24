# Robustness view of the main estimator d (dt_us): outliers, median, trimmed mean, sign count, max dt in kept rows.
import csv, statistics, math
rows = list(csv.DictReader(open('C:/kyty/s113/audit113/final/recount/shn113_rows.csv')))
by = {int(r['n']): r for r in rows}
ds = []; maxdt = (0, 0)
for q in range(1, 50):
    m = []
    for i in range(4):
        b = 4 * q + i; ns = range(1801 + 90 * b + 10, 1801 + 90 * b + 90)
        v = [int(by[n]['M:dt_us']) for n in ns]
        for n in ns:
            if int(by[n]['M:dt_us']) > maxdt[1]: maxdt = (n, int(by[n]['M:dt_us']))
        m.append(statistics.fmean(v))
    ds += [(q, 'AB', m[1] - m[0]), (q, 'BA', m[2] - m[3])]
d = [x[2] for x in ds]
print('n', len(d), 'mean %.2f median %.2f' % (statistics.fmean(d), statistics.median(d)))
s = sorted(d); k = int(0.1 * len(s)); tm = statistics.fmean(s[k:len(s) - k])
print('10%% trimmed mean %.2f' % tm, 'negative', sum(1 for x in d if x < 0), 'of', len(d))
print('extremes', [(q, o, round(v, 1)) for q, o, v in sorted(ds, key=lambda x: x[2])[:3]], [(q, o, round(v, 1)) for q, o, v in sorted(ds, key=lambda x: x[2])[-3:]])
print('max dt in kept rows', maxdt)
ab = [x[2] for x in ds if x[1] == 'AB']; ba = [x[2] for x in ds if x[1] == 'BA']
print('orientation means AB %.2f BA %.2f' % (statistics.fmean(ab), statistics.fmean(ba)))
