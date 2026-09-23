"""Audit 108: independent recount of fam108 (no session scorer imported).

Rules re-implemented from reading fam108.py (not importing it): 90-frame blocks from frame 1800 (block b = frames
1801+90b .. 1890+90b), arm per block from GateArm lines (ABBA 0,1,1,0), kept = block frames at index 60..88 (29
frames), all kept frames >= 2100 and present; pairs = whole quartets (b..b+3, b % 4 == 0) -> (b,b+1), (b+2,b+3);
per-pair delta = arm1 block mean - arm0 block mean; cpu_net_us = cpu_gpu_us - spin_gpu_us.
"""
import json
import math
import random
import statistics as st
import sys

VB = 16667.0
TAG = sys.argv[1] if len(sys.argv) > 1 else 'fam108'
d = json.load(open('C:/kyty/s108/audit108/p_%s.json' % TAG))
fr = {int(k): v for k, v in d['frames'].items()}
gate = d['gate']
out = {}

# --- gate blocks
arm_of = {}
gate_ok = True
for i, g in enumerate(gate):
    arm_of[g['block']] = g['arm']
    if not (g['block'] == i and g['frame'] == 1800 + 90 * i and g['arm'] == (0, 1, 1, 0)[i % 4]
            and g['period'] == 90 and g['abba'] == 1 and g['arms'] == 2):
        gate_ok = False
print('gate lines', len(gate), 'pattern ok', gate_ok, 'texts', sorted({g['text'] for g in gate}))

# --- row arm/blk consistency with the frame-range definition
mism = 0
for b, a in arm_of.items():
    for n in range(1801 + 90 * b, 1891 + 90 * b):
        r = fr.get(n)
        if r is not None and ('arm' in r) and (r['arm'] != a or r['blk'] != b):
            mism += 1
print('rows whose arm/blk disagree with the frame-range block:', mism)

CORE = ('dt_us', 'cpu_gpu_us', 'spin_gpu_us', 'arm', 'blk', 'draws', 'gpu_busy_us')


def usable(n):
    r = fr.get(n)
    return r is not None and all(k in r for k in CORE)


def cpu_net(r):
    return r['cpu_gpu_us'] - r['spin_gpu_us']


def select(lo, hi, first=2100):
    elig = {}
    for b in sorted(arm_of):
        exp = list(range(1801 + 90 * b, 1891 + 90 * b))
        if not all(usable(n) for n in exp):
            continue
        kept = exp[lo:hi]
        if min(kept) < first:
            continue
        elig[b] = kept
    pairs = []
    top = max(arm_of)
    for b in range(0, top + 1, 4):
        if all(k in elig for k in range(b, b + 4)):
            pairs += [(b, b + 1), (b + 2, b + 3)]
    return elig, pairs


def bmean(ns, f):
    return st.fmean(f(fr[n]) for n in ns)


FUN = {
    'dt_us': lambda r: r['dt_us'],
    'cpu_net_us': cpu_net,
    'dt_minus_cpu_net': lambda r: r['dt_us'] - cpu_net(r),
    'cpu_gpu_us': lambda r: r['cpu_gpu_us'],
    'spin_gpu_us': lambda r: r['spin_gpu_us'],
    'da_walk_us': lambda r: r['da_walk_us'],
    'da_miss': lambda r: r['da_miss'],
    'draws': lambda r: r['draws'],
    'gpu_busy_us': lambda r: r['gpu_busy_us'],
    'cspfam_skip': lambda r: r['cspfam_skip'],
    'cspfam_look': lambda r: r['cspfam_look'],
    'cspf_have': lambda r: r['cspf_have'],
    'cs_sync_new': lambda r: r['cs_sync_new'],
    'cs_sync_wait': lambda r: r['cs_sync_wait'],
}


def deltas(elig, pairs, f):
    out = []
    for l, rr in pairs:
        a0 = l if arm_of[l] == 0 else rr
        a1 = rr if a0 == l else l
        out.append(bmean(elig[a1], f) - bmean(elig[a0], f))
    return out


def mt(v):
    n = len(v)
    m = st.fmean(v)
    sd = st.stdev(v)
    se = sd / math.sqrt(n)
    return {'n': n, 'mean': m, 'sd': sd, 'se': se, '2se': 2 * se, 't': m / se if se else None,
            'median': st.median(v), 'frac_neg': sum(x < 0 for x in v) / n}


def signflip_p(v, iters=200000, seed=108):
    rnd = random.Random(seed)
    obs = abs(sum(v))
    hits = 0
    for _ in range(iters):
        s = 0.0
        for x in v:
            s += x if rnd.random() < 0.5 else -x
        if abs(s) >= obs - 1e-9:
            hits += 1
    return (hits + 1) / (iters + 1)


def boot_ci(v, iters=100000, seed=1080):
    rnd = random.Random(seed)
    n = len(v)
    ms = sorted(st.fmean(rnd.choice(v) for _ in range(n)) for _ in range(iters))
    return ms[int(0.025 * iters)], ms[int(0.975 * iters)]


def trimmed(v, frac=0.1):
    s = sorted(v)
    k = int(len(s) * frac)
    return st.fmean(s[k:len(s) - k])


def wilcoxon_p(v):
    # normal approximation of the signed-rank test (two-sided), ties by average rank
    a = [(abs(x), 1 if x > 0 else -1) for x in v if x != 0]
    a.sort()
    ranks = [0.0] * len(a)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[j + 1][0] == a[i][0]:
            j += 1
        for k in range(i, j + 1):
            ranks[k] = (i + j) / 2 + 1
        i = j + 1
    wplus = sum(r for r, (_, s) in zip(ranks, a) if s > 0)
    n = len(a)
    mu = n * (n + 1) / 4
    sig = math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    z = (wplus - mu) / sig
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2)))), z


elig, pairs = select(60, 89)
orient = [sum(arm_of[p[0]] == a for p in pairs) for a in (0, 1)]
excluded = sorted(b for b in elig if not any(b in p for p in pairs))
print('primary window [60:89]: eligible blocks', len(elig), 'pairs', len(pairs), 'orientations', orient,
      'eligible-but-unpaired', excluded)
res = {}
for k in FUN:
    try:
        v = deltas(elig, pairs, FUN[k])
    except KeyError:
        continue
    res[k] = mt(v)
    res[k]['values'] = v
for k in ('dt_us', 'cpu_net_us', 'dt_minus_cpu_net', 'da_walk_us', 'da_miss', 'draws', 'gpu_busy_us',
          'cpu_gpu_us', 'spin_gpu_us'):
    s = res[k]
    print('  d %-17s mean %8.1f  2SE %6.1f  t %6.2f  median %8.1f  frac<0 %.3f  sd %.1f' % (
        k, s['mean'], s['2se'], s['t'], s['median'], s['frac_neg'], s['sd']))
v = res['dt_us']['values']
p_perm = signflip_p(v)
ci = boot_ci(v)
wp, wz = wilcoxon_p(v)
print('  dt: sign-flip p %.5f  bootstrap95 [%.1f, %.1f]  10%%-trimmed mean %.1f  wilcoxon p %.4f (z %.2f)' % (
    p_perm, ci[0], ci[1], trimmed(v), wp, wz))
vc = res['cpu_net_us']['values']
print('  cpu_net: sign-flip p %.4f  bootstrap95 [%.1f, %.1f]' % (signflip_p(vc, 50000), *boot_ci(vc, 20000)))
# orientation split
for o in (0, 1):
    vv = [x for x, p in zip(v, pairs) if arm_of[p[0]] == o]
    s = mt(vv)
    print('  orientation first-arm=%d: n %d mean %.1f 2SE %.1f' % (o, s['n'], s['mean'], s['2se']))
# first vs second half of the run
h = len(v) // 2
for name, vv in (('first half', v[:h]), ('second half', v[h:])):
    s = mt(vv)
    print('  %s: n %d mean %.1f 2SE %.1f' % (name, s['n'], s['mean'], s['2se']))
# arm levels (block means) - mean and median
for k in ('dt_us', 'cpu_net_us', 'cspfam_skip', 'cspfam_look', 'cspf_have', 'da_walk_us', 'da_miss'):
    for a in (0, 1):
        bm = [bmean(elig[b], FUN[k]) for p in pairs for b in p if arm_of[b] == a]
        res.setdefault('levels', {}).setdefault(k, {})[a] = (st.fmean(bm), st.median(bm))
    lv = res['levels'][k]
    print('  level %-12s arm0 mean %9.1f median %9.1f | arm1 mean %9.1f median %9.1f' % (
        k, lv[0][0], lv[0][1], lv[1][0], lv[1][1]))

# guard over ALL usable rows from 2100 by the row's own arm
for k in ('cs_sync_new', 'cs_sync_wait', 'cspfam_look', 'cspfam_skip', 'cspf_have', 'cspf_new'):
    s = {a: sum(fr[n].get(k, 0) for n in fr if n >= 2100 and usable(n) and fr[n]['arm'] == a) for a in (0, 1)}
    print('  all rows >=2100 sum %-12s arm0 %d arm1 %d' % (k, s[0], s[1]))
look0 = sum(fr[n]['cspfam_look'] for b in elig for n in elig[b] if arm_of[b] == 0 and any(b in p for p in pairs))
print('  kept arm-0 cspfam_look total', look0)

# --- vblank histograms
def hist(ns):
    h = {}
    for n in ns:
        k = int(round(fr[n]['dt_us'] / VB))
        h[k] = h.get(k, 0) + 1
    return dict(sorted(h.items()))


kept_by_arm = {a: [n for p in pairs for b in p if arm_of[b] == a for n in elig[b]] for a in (0, 1)}
all_by_arm = {a: [n for n in fr if n >= 2100 and usable(n) and fr[n]['arm'] == a] for a in (0, 1)}
for name, groups in (('kept rows', kept_by_arm), ('all rows >= 2100', all_by_arm)):
    print('  vblank histogram (%s):' % name)
    for a in (0, 1):
        h = hist(groups[a])
        tot = sum(h.values())
        mean_dt = st.fmean(fr[n]['dt_us'] for n in groups[a])
        med_dt = st.median(fr[n]['dt_us'] for n in groups[a])
        print('    arm%d n %5d mean dt %.1f median %.1f  ' % (a, tot, mean_dt, med_dt)
              + '  '.join('%dvb %d (%.2f%%)' % (k, c, 100.0 * c / tot) for k, c in h.items()))
    h0, h1 = hist(groups[0]), hist(groups[1])
    t0, t1 = sum(h0.values()), sum(h1.values())
    ev0 = sum(k * c for k, c in h0.items()) / t0
    ev1 = sum(k * c for k, c in h1.items()) / t1
    print('    mean vblanks/frame arm0 %.4f arm1 %.4f -> delta %.4f vb = %.1f us' % (ev0, ev1, ev1 - ev0,
                                                                                   (ev1 - ev0) * VB))
# dt within-vblank residual: dt - k*VB
def resid(ns):
    return st.fmean(fr[n]['dt_us'] - round(fr[n]['dt_us'] / VB) * VB for n in ns)


print('  mean residual dt - k*16667 (kept): arm0 %.1f arm1 %.1f' % (resid(kept_by_arm[0]), resid(kept_by_arm[1])))

# --- paired count of frames per vblank class per pair
cls = {}
for k in (1, 2, 3, 4):
    vals = []
    for l, rr in pairs:
        a0 = l if arm_of[l] == 0 else rr
        a1 = rr if a0 == l else l
        c = lambda b: sum(1 for n in elig[b] if int(round(fr[n]['dt_us'] / VB)) == k)
        vals.append(c(a1) - c(a0))
    s = mt(vals)
    cls[k] = s
    print('  paired d(#frames of %d vblanks per 29-frame block): mean %.3f 2SE %.3f t %.2f' % (
        k, s['mean'], s['2se'], s['t'] if s['t'] is not None else float('nan')))
ge3 = []
for l, rr in pairs:
    a0 = l if arm_of[l] == 0 else rr
    a1 = rr if a0 == l else l
    c = lambda b: sum(1 for n in elig[b] if int(round(fr[n]['dt_us'] / VB)) >= 3)
    ge3.append(c(a1) - c(a0))
s = mt(ge3)
print('  paired d(#frames >= 3 vblanks per block): mean %.3f 2SE %.3f t %.2f' % (s['mean'], s['2se'], s['t']))

# --- window sensitivity
print('  window sensitivity (dt_us):')
for lo, hi in ((60, 89), (0, 90), (0, 89), (30, 89), (45, 90), (60, 90), (10, 90), (0, 60), (30, 60)):
    e, p = select(lo, hi)
    vv = deltas(e, p, FUN['dt_us'])
    s = mt(vv)
    print('    keep [%2d:%2d] pairs %3d  mean %7.1f  2SE %6.1f  t %6.2f  median %7.1f  p_signflip %.4f' % (
        lo, hi, len(p), s['mean'], s['2se'], s['t'], s['median'], signflip_p(vv, 20000)))

json.dump({k: {kk: vv for kk, vv in v.items() if kk != 'values'} if isinstance(v, dict) and 'values' in v else v
           for k, v in res.items()}, open('C:/kyty/s108/audit108/recount108.json', 'w'), indent=1, default=str)
