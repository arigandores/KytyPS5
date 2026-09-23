from recount import *
d = load('dwk104')
res = analyse(d, ['dt_us'])
diffs = []
for p in res['pairlist']:
    b1 = [b for b in p if res['arm_of'][b] == 1][0]; b0 = [b for b in p if res['arm_of'][b] == 0][0]
    diffs.append((block_mean(d, res['elig'][b1], 'dt_us') - block_mean(d, res['elig'][b0], 'dt_us'), b0, b1,
                  block_mean(d, res['elig'][b0], 'dt_us'), block_mean(d, res['elig'][b1], 'dt_us')))
s = sorted(diffs)
print('lowest 8', [(round(x[0], 1), x[1], x[2], round(x[3]), round(x[4])) for x in s[:8]])
print('highest 5', [(round(x[0], 1), x[1], x[2]) for x in s[-5:]])
v = [x[0] for x in diffs]
k = int(len(v) * 0.1)
tv = sorted(v)[k:len(v) - k]
print('10%% trimmed mean %.4f' % st.mean(tv))
# per-row dt distribution per arm: fraction of rows > 40 ms
for a in (0, 1):
    rows = [d['merged'][n]['dt_us'] for b in res['used'] if res['arm_of'][b] == a for n in res['elig'][b]]
    rows.sort()
    print('arm', a, 'rows', len(rows), 'median %.1f p90 %.1f p99 %.1f max %d >40ms %d >50ms %d mean %.1f' % (
        st.median(rows), rows[int(.9 * len(rows))], rows[int(.99 * len(rows))], rows[-1],
        sum(1 for x in rows if x > 40000), sum(1 for x in rows if x > 50000), st.mean(rows)))
# block-mean dt distribution
for a in (0, 1):
    bm = sorted(block_mean(d, res['elig'][b], 'dt_us') for b in res['used'] if res['arm_of'][b] == a)
    print('arm', a, 'block means min %.0f med %.0f max %.0f' % (bm[0], st.median(bm), bm[-1]))
