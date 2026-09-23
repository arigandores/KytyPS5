# Independent recount of the M5' bench (session 103), auditor's own code.
# Reads raw bench/plan/equal/find JSON; does NOT import any session scorer.
import json, hashlib, math, os, glob, re, statistics, random, sys

R = 'C:/kyty/s103/m5p/real/'
bench = json.load(open(R + 'bench_m5p103.json'))
plan = json.load(open(R + 'plan_m5p103.json'))
equal = json.load(open(R + 'equal_m5p103.json'))
find = json.load(open(R + 'find_m5p103.json'))
out = []
def P(*a):
    s = ' '.join(str(x) for x in a)
    print(s); out.append(s)

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

P('sha256 bench', sha(R + 'bench_m5p103.json'))
P('sha256 plan ', sha(R + 'plan_m5p103.json'), 'bench says', bench['plan_sha256'], 'equal says', equal['plan_sha256'])
P('sha256 pred02', sha('C:/kyty/s103/pred/02_m5p_bench.md'), 'bench says', bench['pred_sha256'])
P('sha256 pred03', sha('C:/kyty/s103/pred/03_m5p_addendum.md'))

ITEMS = ['S%d' % i for i in range(1, 11)]
STAGE = {'S1': 'cs', 'S2': 'ps', 'S3': 'ps', 'S4': 'ps', 'S5': 'ps', 'S6': 'cs', 'S7': 'cs', 'S8': 'ps', 'S9': 'ps', 'S10': 'ps'}
HASH = {'S1': '56a15431999c5a2d', 'S2': '746c68bba46b2b49', 'S3': '3d705c1b57adec00', 'S4': '2e2ae33a4d374e8f',
        'S5': 'b96c2898f05637df', 'S6': '173677e49330bd65', 'S7': '3276e23cce1be33c', 'S8': '7a46be05e11e081b',
        'S9': 'ca11de665702d6d9', 'S10': 'c924afb0821b68c8'}

# ---- 1. independent item -> module -> events mapping from find + my own md5 of arm-A modules
amd5 = {}
for p in glob.glob('C:/kyty/s103/m5p/spv/*_A.spv'):
    b = os.path.basename(p)
    it = b.split('_')[0]
    amd5.setdefault(it, set()).add(hashlib.md5(open(p, 'rb').read()).hexdigest())
mods_by_item = {it: [] for it in ITEMS}
for mid, m in find['modules'].items():
    for it in ITEMS:
        if m['md5'] in amd5.get(it, ()):
            mods_by_item[it].append((mid, m['stage']))
ev_by_item = {}
for it in ITEMS:
    ids = set(mid for mid, st in mods_by_item[it])
    evs = []
    for e in find['events']:
        key = 'cs' if STAGE[it] == 'cs' else 'ps'
        if e.get(key) in ids:
            evs.append(e['eid'])
    ev_by_item[it] = sorted(evs)
    pe = sorted(plan['items'][it]['events'])
    pm = sorted(m['orig_shader_id'] for m in plan['items'][it]['modules'])
    P('map', it, 'modules(mine)', sorted(ids), 'plan', pm, 'events mine', len(evs), 'plan', len(pe), 'same', evs == pe,
      'last', max(evs) if evs else None, 'plan last', plan['items'][it]['last_event'])
# also: any capture module whose md5 equals an A module of ANY permutation but is not a PS/CS?
# and any module of an item hash with no A match (cannot see hash in find; report md5-only)
allev = sorted(sum(ev_by_item.values(), []))
P('union events', len(allev), 'distinct', len(set(allev)), 'bench events', len(bench['events']),
  'same set', sorted(bench['events']) == allev, 'plan events same', plan['events'] == bench['events'])
# overlap between items
seen = {}
for it in ITEMS:
    for e in ev_by_item[it]:
        if e in seen: P('OVERLAP event', e, seen[e], it)
        seen[e] = it

idx = {e: k for k, e in enumerate(bench['events'])}
item_idx = {it: [idx[e] for e in ev_by_item[it]] for it in ITEMS}

# ---- 2. fetch completeness, design
main = [f for f in bench['fetches'] if f['phase'] == 'main']
other = [f for f in bench['fetches'] if f['phase'] != 'main']
P('fetches', len(bench['fetches']), 'main', len(main), 'other phases', sorted(set(f['phase'] for f in other)))
P('warmup', len(bench['warmup']), [(w['phase'], w['arm'], w['round']) for w in bench['warmup']])
bad = 0; zeros = {}
for f in bench['fetches'] + bench['warmup']:
    d = f['d']
    if len(d) != len(bench['events']) or f['missing']:
        bad += 1
    for k, v in enumerate(d):
        if v is None or not isinstance(v, (int, float)) or math.isnan(v) or math.isinf(v) or v < 0:
            bad += 1
for f in main:
    for it in ITEMS:
        z = sum(1 for k in item_idx[it] if f['d'][k] == 0)
        zeros.setdefault((it, f['arm']), []).append(z)
P('fetches with a missing/invalid value:', bad)
for it in ITEMS:
    P('zero-duration events per fetch', it, {a: (min(zeros[(it, a)]), max(zeros[(it, a)])) for a in ['B', 'A', 'V1', 'V2p']}, 'of', len(item_idx[it]))

SEQ = [['B', 'A', 'V1', 'V2p'], ['A', 'V2p', 'B', 'V1'], ['V1', 'B', 'V2p', 'A'], ['V2p', 'V1', 'A', 'B']]
rounds = sorted(set(f['round'] for f in main))
P('rounds', rounds)
viol = []
for r in rounds:
    fr = sorted([f for f in main if f['round'] == r], key=lambda f: f['t_start'])
    arms = [f['arm'] for f in fr]
    pos = [f['pos'] for f in fr]
    if arms != SEQ[r % 4] or pos != [0, 1, 2, 3] or any(f['seq_index'] != r % 4 for f in fr):
        viol.append((r, arms, pos))
rs = bench['round_sequences']
for x in rs:
    if x['sequence'] != SEQ[x['round'] % 4]: viol.append(('recorded', x))
P('design violations', viol, 'recorded round_sequences', len(rs))
# time ordering: warm-up precedes main
tw = max(w['t_start'] for w in bench['warmup']); tm = min(f['t_start'] for f in main)
P('warm-up before main', tw < tm, 'global t_start monotone in (round,pos)',
  all(a['t_start'] < b['t_start'] for a, b in zip(sorted(main, key=lambda f: (f['round'], f['pos'])), sorted(main, key=lambda f: (f['round'], f['pos']))[1:])))

# ---- 3. T, S
T = {}
for f in main:
    for it in ITEMS:
        T[(f['arm'], it, f['round'])] = sum(f['d'][k] for k in item_idx[it])
def S(arm, r, items):
    return sum(T[(arm, it, r)] for it in items)

# ---- 4. V-e recomputed from resource-level numbers
fail = {'V1': [], 'V2p': []}
for it in ITEMS:
    e = equal['items'][it]
    pairs = e['reference_pair_diff_by_resource']
    tot = [0, 0, 0]
    for pr in pairs:
        if pr.get('deciding', True):
            for k in range(3): tot[k] += pr['pairs'][k]
    E = max(tot)
    rep = (E == 0)
    for v in ['V1', 'V2p']:
        rr = e['variants'][v]
        nd = sum((x['n_diff_bytes'] or 0) for x in rr['resources'] if x.get('deciding', True))
        ok = (nd == 0) if rep else (nd <= 2 * E)
        if rr.get('error'): ok = False
        if not ok: fail[v].append(it)
        P('V-e', it, v, 'E', E, 'repeatable', rep, 'ndiff', nd, 'limit', 2 * E, 'pass(mine)', ok, 'pass(file)', rr['pass'],
          'in_effect', e['in_effect'].get(v, {}).get('ok'))
P('V-e failing (mine):', fail)
valid_v2 = [it for it in ITEMS if it not in fail['V2p']]
valid_v1 = [it for it in ITEMS if it not in fail['V1']]

def med(x):
    return statistics.median(x)
def ratio_series(num, den, items):
    return [S(num, r, items) / S(den, r, items) for r in rounds]

Xs = ratio_series('V2p', 'A', valid_v2)
Ls = ratio_series('V1', 'A', valid_v1)
ABs = ratio_series('A', 'B', ITEMS)
P('items X', valid_v2)
P("X' point %.6f  L point %.6f  A/B point %.6f" % (med(Xs), med(Ls), med(ABs)))
P('X series', ['%.4f' % x for x in Xs])
P('X series min/max', '%.4f %.4f' % (min(Xs), max(Xs)))
# pooled-sum alternative (reported only)
P("X' as ratio of sums over rounds %.6f" % (sum(S('V2p', r, valid_v2) for r in rounds) / sum(S('A', r, valid_v2) for r in rounds)))

# failing share
fs_each = [S('A', r, fail['V2p']) / S('A', r, ITEMS) for r in rounds]
P('failing share V2p: median over rounds %.4f, pooled %.4f, min %.4f max %.4f' % (
    med(fs_each), sum(S('A', r, fail['V2p']) for r in rounds) / sum(S('A', r, ITEMS) for r in rounds), min(fs_each), max(fs_each)))

# per-item medians
for it in ITEMS:
    P('item', it, 'A med us %.1f' % med([T[('A', it, r)] for r in rounds]),
      ' '.join('%s/A %.4f' % (a, med([T[(a, it, r)] / T[('A', it, r)] for r in rounds])) for a in ['B', 'V1', 'V2p']))

# ---- 5. bootstrap (several independent implementations)
n = len(rounds)
def boot(seedgen, label):
    res = {'X': [], 'L': [], 'AB': []}
    for b in range(20000):
        ix = seedgen(n)
        res['X'].append(med([Xs[i] for i in ix]))
        res['L'].append(med([Ls[i] for i in ix]))
        res['AB'].append(med([ABs[i] for i in ix]))
    outd = {}
    for k, v in res.items():
        v.sort()
        # two percentile conventions
        lo = v[int(math.floor(0.05 * (len(v) - 1)))]; hi = v[int(math.ceil(0.95 * (len(v) - 1)))]
        outd[k] = (lo - 1, hi - 1)
    P('bootstrap', label, ' '.join('%s-1 [%.4f, %.4f]' % (k, a, b) for k, (a, b) in outd.items()))
    return outd
rng = random.Random(103)
boot(lambda n: [rng.randrange(n) for _ in range(n)], 'python random.Random(103)')
try:
    import numpy as np
    g = np.random.default_rng(103)
    boot(lambda n: list(g.integers(0, n, n)), 'numpy default_rng(103)')
    rs_ = np.random.RandomState(103)
    boot(lambda n: list(rs_.randint(0, n, n)), 'numpy RandomState(103)')
except Exception as ex:
    P('numpy not available', ex)
rng2 = random.Random(987654)
boot(lambda n: [rng2.randrange(n) for _ in range(n)], 'python random.Random(987654) (seed sensitivity)')

# ---- 6. verdict
P("verdict input: X' point-1 = %.4f" % (med(Xs) - 1))
open('C:/kyty/s103/audit103/recount/m5p_recount.out.txt', 'w').write('\n'.join(out) + '\n')
