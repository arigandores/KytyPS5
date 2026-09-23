"""Audit 109: independent recount of an ABBA frame-time run (frm109 / fam108) from the parsed raw log.
Rules taken from the scorer text only: GateArm blocks of 90 from frame 1800 (block b covers n = 1801+90b ..
1890+90b), keep offsets 60..88 (29 rows), keep only if all 90 rows exist and first kept n >= 2100, quartets
(b..b+3, b % 4 == 0) all eligible -> pairs (b, b+1), (b+2, b+3); pair delta = arm1 block mean - arm0 block mean.
usage: python recount_frm.py <tag> [arm1_label]
"""
import json
import math
import pickle
import random
import re
import statistics
import sys

sys.stdout.reconfigure(encoding='utf-8')
tag = sys.argv[1]
d = pickle.load(open('C:/kyty/s109/audit109/parsed/%s.pkl' % tag, 'rb'))
main, draw, x = d['main'], d['draw'], d['x']
RE_GA = re.compile(r'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
arms = {}
texts = {}
for ln, n, t in d['events']:
    m = RE_GA.search(t)
    if m:
        a, _, b, fr, per, abba, text = m.groups()
        arms[int(b)] = int(a)
        texts[int(a)] = text.strip()
        assert int(fr) == 1800 + 90 * int(b) and int(per) == 90 and int(abba) == 1
print('blocks', len(arms), 'arm texts', texts)
abba_ok = all(arms[b] == (0, 1, 1, 0)[b % 4] for b in arms)
print('ABBA order ok', abba_ok)


def row(n):
    r = dict(main[n])
    r.update(draw.get(n, {}))
    r.update(x.get(n, {}))
    if 'cpu_gpu_us' in r and 'spin_gpu_us' in r:
        r['cpu_net_us'] = r['cpu_gpu_us'] - r['spin_gpu_us']
    return r


eligible = {}
for b in sorted(arms):
    exp = list(range(1801 + 90 * b, 1891 + 90 * b))
    if not all(n in main and n in draw and n in x for n in exp):
        continue
    kept = exp[60:89]
    if min(kept) < 2100:
        continue
    # row arm/blk consistency
    assert all(main[n]['arm'] == arms[b] and main[n]['blk'] == b for n in kept), b
    eligible[b] = kept
pairs = []
for b in range(0, max(arms) + 1, 4):
    q = [b, b + 1, b + 2, b + 3]
    if all(k in eligible for k in q):
        pairs += [(b, b + 1), (b + 2, b + 3)]
print('eligible', len(eligible), 'pairs', len(pairs), 'orient arm0-first', sum(arms[p[0]] == 0 for p in pairs))

KEYS = ['dt_us', 'cpu_net_us', 'cpu_gpu_us', 'spin_gpu_us', 'gpu_busy_us', 'gpu_n', 'submits', 'submit_us',
        'semwaits', 'semwait_us', 'semwait_gpu_us', 'draws', 'dispatches', 'cpu_main_us', 'cpu_present_us', 'lat_us',
        'da_walk_us', 'da_queue_us', 'da_take_us', 'da_hit', 'da_miss', 'da_late', 'rec_n', 'prios', 'dmas',
        'img_up', 'img_up_kb', 'cspfree_hit', 'cspf_have', 'cs_sync_new', 'cs_sync_wait', 'rec_spin_us',
        'rec_sleep', 'rec_spin_gpu_us', 'rec_sleep_gpu', 'da_wlag_us', 'da_wdepth']


def bmean(b, k):
    v = [row(n).get(k) for n in eligible[b]]
    if any(z is None for z in v):
        return None
    return statistics.fmean(v)


def stats(vals):
    n = len(vals)
    mu = statistics.fmean(vals)
    sd = statistics.stdev(vals)
    se = sd / math.sqrt(n)
    return mu, se, mu / se if se else float('nan')


deltas = {}
for k in KEYS:
    ds = []
    for l, r in pairs:
        a0 = l if arms[l] == 0 else r
        a1 = r if a0 == l else l
        m0, m1 = bmean(a0, k), bmean(a1, k)
        if m0 is None or m1 is None:
            ds = None
            break
        ds.append(m1 - m0)
    if ds:
        deltas[k] = ds
res = {'tag': tag, 'pairs': len(pairs)}
print('%-16s %10s %8s %7s' % ('field', 'mean', '2SE', 't'))
for k, ds in deltas.items():
    mu, se, t = stats(ds)
    res[k] = {'mean': mu, 'se': se, 't': t, 'median': statistics.median(ds)}
    print('%-16s %10.1f %8.1f %7.2f  median %8.1f' % (k, mu, 2 * se, t, statistics.median(ds)))

rng = random.Random(109)
for k in ('dt_us', 'cpu_net_us', 'gpu_busy_us', 'da_walk_us'):
    ds = deltas[k]
    obs = statistics.fmean(ds)
    N = 200000
    cnt = 0
    for _ in range(N):
        s = sum(v if rng.random() < 0.5 else -v for v in ds) / len(ds)
        if abs(s) >= abs(obs) - 1e-12:
            cnt += 1
    p_perm = (cnt + 1) / (N + 1)
    B = 20000
    boots = sorted(statistics.fmean(rng.choices(ds, k=len(ds))) for _ in range(B))
    lo, hi = boots[int(0.025 * B)], boots[int(0.975 * B) - 1]
    # trimmed mean 10 %
    s = sorted(ds)
    tr = statistics.fmean(s[len(s) // 10: len(s) - len(s) // 10])
    # wilcoxon signed-rank normal approx
    nz = [v for v in ds if v != 0]
    ranks = sorted(range(len(nz)), key=lambda i: abs(nz[i]))
    rk = [0.0] * len(nz)
    for pos, i in enumerate(ranks):
        rk[i] = pos + 1
    wplus = sum(rk[i] for i in range(len(nz)) if nz[i] > 0)
    nn = len(nz)
    mu_w = nn * (nn + 1) / 4
    sd_w = math.sqrt(nn * (nn + 1) * (2 * nn + 1) / 24)
    z = (wplus - mu_w) / sd_w
    p_w = math.erfc(abs(z) / math.sqrt(2))
    neg = sum(v < 0 for v in ds)
    res[k].update(p_perm=p_perm, boot95=[lo, hi], trimmed10=tr, wilcoxon_z=z, wilcoxon_p=p_w, neg_pairs=neg)
    print('%s: sign-flip perm p %.4f  bootstrap95 [%.1f, %.1f]  10%%-trimmed %.1f  Wilcoxon z %.2f p %.4f  pairs<0 %d/%d' % (
        k, p_perm, lo, hi, tr, z, p_w, neg, len(ds)))

# leave-one-out influence on dt
ds = deltas['dt_us']
srt = sorted(ds)
print('dt deltas min5', [round(v) for v in srt[:5]], 'max5', [round(v) for v in srt[-5:]])
for drop in (1, 2, 3, 5):
    rem = sorted(ds, key=lambda v: v)[drop:]
    print('drop %d most negative -> mean %.1f' % (drop, statistics.fmean(rem)))

# vblank histogram per arm over kept rows of paired blocks
VB = 1e6 / 60
hist = {0: {}, 1: {}}
tot = {0: 0, 1: 0}
dtsum = {0: 0, 1: 0}
for l, r in pairs:
    for b in (l, r):
        a = arms[b]
        for n in eligible[b]:
            v = max(1, int(round(main[n]['dt_us'] / VB)))
            hist[a][v] = hist[a].get(v, 0) + 1
            tot[a] += 1
            dtsum[a] += main[n]['dt_us']
print('vblank histogram (kept rows of paired blocks):')
for v in sorted(set(hist[0]) | set(hist[1])):
    print('  %d vbl: arm0 %6d (%.3f%%)  arm1 %6d (%.3f%%)' % (v, hist[0].get(v, 0), 100 * hist[0].get(v, 0) / tot[0],
                                                          hist[1].get(v, 0), 100 * hist[1].get(v, 0) / tot[1]))
print('  mean dt arm0 %.1f arm1 %.1f (rows %d/%d)' % (dtsum[0] / tot[0], dtsum[1] / tot[1], tot[0], tot[1]))
res['vblank_hist'] = {str(a): hist[a] for a in (0, 1)}
res['rows'] = tot
# expected dt from histogram shift: (count of 1-vbl frames) etc
json.dump(res, open('C:/kyty/s109/audit109/recount_%s.json' % tag, 'w'), indent=1)
pickle.dump({'deltas': deltas, 'pairs': pairs, 'arms': arms, 'eligible': eligible},
            open('C:/kyty/s109/audit109/pairs_%s.pkl' % tag, 'wb'))
