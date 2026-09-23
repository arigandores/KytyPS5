"""Offline tests of the M5' harness sealed to pred/02_m5p_bench.md (+ the session-102 parents
prev102/pred/01_m5_bench.md and prev102/pred/02_m5_addendum.md): m5p_103.py (scorer), m5p_plan.py
(planner), the pure helpers the qrenderdoc tools take from m5p_103 (design, arm / variant / capture /
seal refusals), and static checks of rd_m5p_equal.py, rd_m5p_bench.py, m5p_run.py.  Synthetic plan /
bench / equality JSON, plus read-only use of session-102 module files (as stand-ins), the session-102
bench (P4') and, when it exists, the real m5p/recompile.json.  No game, no RenderDoc, no build.

    python test_m5p_103.py

A/A must read PASSES; X' = +10 % must read CLOSED; a straddle must be INCONCLUSIVE, owe the
extension, and the extension must then decide at the POINT (CLOSED or PASSES); V2p failures above
40 % of the valid A time must read M5' NOT DECIDED; the amended V-e (three A replays, 2*E) must pass at
2E and fail at 2E+1; the four-arm design must be the sealed Williams design; each of the three seals
changed must be refused; and one MUTATION per control (V-a ... V-g, the file identity, the sealed
inputs) must make exactly that control fail and take the verdict away.
"""
import ast
import copy
import hashlib
import json
import os
import random
import shutil
import struct
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    pass
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import m5p_103 as S  # noqa: E402
import m5p_plan as P  # noqa: E402

ITEMS = [('S1', 'cs'), ('S2', 'ps'), ('S3', 'ps'), ('S4', 'ps'), ('S5', 'ps'),
         ('S6', 'cs'), ('S7', 'cs'), ('S8', 'ps'), ('S9', 'ps'), ('S10', 'ps')]
VARIANT_ARMS = ('A', 'V1', 'V2p')
CAPTURE_OK = {'dma_layout': True, 'clock_pin': True}
# new s4 written out by hand
DESIGN_BY_HAND = [('B', 'A', 'V1', 'V2p'), ('A', 'V2p', 'B', 'V1'), ('V1', 'B', 'V2p', 'A'), ('V2p', 'V1', 'A', 'B')]
REAL_RECOMPILE = 'C:/kyty/s103/m5p/recompile.json'
S102_SPV = 'C:/kyty/s103/m5/spv/S3_3d705c1b57adec00_p0_%s.spv'     # session-102 modules, stand-ins only


def pairs_for(e):
    """Three A-replay pair counts whose maximum is e."""
    return {'A1-A2': e, 'A1-A3': e // 2, 'A2-A3': e // 3}


def plan_header():
    return dict(pred_sha256=S.PRED_SHA, parent01_sha256=S.PARENT01_SHA, parent02_sha256=S.PARENT02_SHA,
                capture_sha256=S.CAPTURE_SHA, recompile_exe_sha256=S.EXE_SHA,
                recompile_cache_dir=S.SNAPSHOT_DIR, cache_dir=S.SNAPSHOT_DIR,
                signature_prefix=S.SIGNATURE_PREFIX, recompile_signature=S.SIGNATURE_PREFIX)


def make(present=None, rounds=20, v2p=1.0, v1=1.0, ab=1.0, noise=0.01, seed=1, excluded_share=0.0,
         ext_rounds=0, ext=None, per_item=None, eq_ndiff=None, nondet=None, wholly_excluded=(), requested=20):
    """A synthetic (plan, bench, equal) triple of the four-arm design.

    Each present item has two events of weight/2 us under arm A; B = A / ab, V1 = A * v1,
    V2p = A * v2p; per_item {(item, arm): factor} overrides; ext {arm: factor} overrides in the
    extension phase; every event gets independent multiplicative noise N(1, noise).  excluded_share
    adds one excluded module per item carrying that share of the item's A time.  An item in
    wholly_excluded is present through the cache link only.  Equality: nondet {item: E} makes the A
    replays differ (max pair = E); eq_ndiff {(item, arm): n} is a variant's differing bytes against A1."""
    rng = random.Random(seed)
    ext = ext or {}
    per_item = per_item or {}
    eq_ndiff = eq_ndiff or {}
    nondet = nondet or {}
    present = [n for n, _ in ITEMS if n not in wholly_excluded] if present is None else present
    plan = dict(plan_header(), cache_link_used=True, items={},
                arms=[dict(name=a, replacements=[]) for a in S.ARMS],
                events=[], validation={}, mechanics=False)
    base = {}
    eid = 100
    for name, stage in ITEMS:
        item = dict(stage=stage, hash=name.lower(), weight=S.WEIGHTS[name], present=name in present,
                    modules=[], excluded_modules=[], events=[], excluded_events=[], arm_missing={})
        if name in wholly_excluded:
            xs = [eid, eid + 1]
            eid += 2
            for x in xs:
                base[x] = S.WEIGHTS[name] / 2.0
            item['present'] = True
            item['excluded_modules'].append(dict(orig_shader_id='ResourceId::w%d' % xs[0], events=xs, link='cache'))
            item['excluded_events'] = xs
            item['last_event'] = None
        elif name in present:
            evs = [eid, eid + 1]
            eid += 2
            for e in evs:
                base[e] = S.WEIGHTS[name] / 2.0
            module = dict(orig_shader_id='ResourceId::%d' % eid, md5='m' * 32, perm=0, events=evs)
            for arm in VARIANT_ARMS:
                path = 'C:/synthetic/%s_%s.spv' % (name, arm)
                module[arm] = dict(path=path, md5='f' * 32)
                plan['validation'][path] = dict(ubsl=dict(ok=True), pred01=dict(ok=stage == 'cs'))
                plan['arms'][S.ARMS.index(arm)]['replacements'].append(
                    dict(orig_shader_id=module['orig_shader_id'], spv_path=path, stage=stage, item=name, perm=0))
            item['modules'].append(module)
            item['events'] = evs
            item['last_event'] = evs[-1]
            if excluded_share > 0:
                x = eid
                eid += 1
                base[x] = S.WEIGHTS[name] * excluded_share / (1.0 - excluded_share)
                item['excluded_modules'].append(dict(orig_shader_id='ResourceId::x%d' % x, events=[x], link='cache'))
                item['excluded_events'] = [x]
        plan['items'][name] = item
    events = sorted(base)
    plan['events'] = events
    default = {'B': 1.0 / ab, 'A': 1.0, 'V1': v1, 'V2p': v2p}

    def factor(arm, item_name, phase):
        f = default[arm]
        if phase == 'extension' and arm in ext:
            f = ext[arm]
        return per_item.get((item_name, arm), f)

    owner = {}
    for name, item in plan['items'].items():
        for e in item['events']:
            owner[e] = (name, True)
        for e in item['excluded_events']:
            owner[e] = (name, False)
    fetches = []
    round_sequences = []
    for phase, first, count in (('main', 0, rounds), ('extension', rounds, ext_rounds)):
        for r in range(first, first + count):
            seq_index = r % 4
            round_sequences.append(dict(round=r, phase=phase, seq_index=seq_index, sequence=list(S.DESIGN[seq_index])))
            for pos, arm in enumerate(S.DESIGN[seq_index]):
                d = []
                for e in events:
                    name, included = owner[e]
                    f = factor(arm, name, phase) if included else (1.0 / ab if arm == 'B' else 1.0)
                    d.append(base[e] * f * rng.gauss(1.0, noise))
                fetches.append(dict(phase=phase, round=r, pos=pos, arm=arm, seq_index=seq_index, d=d, missing=[],
                                    fetch_s=0.5, replace_s=0.1, remove_s=0.1))
    bench = dict(tool='rd_m5p_bench', capture_sha256=S.CAPTURE_SHA, plan_sha256='p' * 64, arms=list(S.ARMS),
                 events=events, rounds_requested=requested, fetches=fetches, round_sequences=round_sequences,
                 build_errors=[], decisions=[], complete=True, rounds_main=rounds, rounds_extension=ext_rounds,
                 replacement_check_ok=True)
    equal = dict(plan_sha256='p' * 64, reference='A', a_replays=3, items={})
    for name in present:
        e = nondet.get(name, 0)
        rec = dict(reference_replays=3, reference_pair_diff_bytes=pairs_for(e), E=e, repeatable=e == 0, variants={})
        for arm in S.VARIANTS:
            n = eq_ndiff.get((name, arm), 0)
            rec['variants'][arm] = dict(equal=n == 0, n_diff_bytes=n, reference_pair_diff_bytes=pairs_for(e),
                                        error=None)
        equal['items'][name] = rec
    return plan, bench, equal


def make_prev102(factor_v2=1.30, items=S.P4_ITEMS102, rounds=20, seed=3):
    """A synthetic session-102 (plan, bench) pair with arms A and V2 (P4' recomputation only)."""
    rng = random.Random(seed)
    plan = dict(items={})
    events = []
    eid = 500
    for name in items:
        plan['items'][name] = dict(events=[eid, eid + 1])
        events += [eid, eid + 1]
        eid += 2
    fetches = []
    for r in range(rounds):
        for pos, arm in enumerate(('A', 'V2')):
            d = [S.WEIGHTS[n] / 2.0 * (factor_v2 if arm == 'V2' else 1.0) * rng.gauss(1.0, 0.005)
                 for n in items for _ in (0, 1)]
            fetches.append(dict(phase='main', round=r, pos=pos, arm=arm, d=d))
    return dict(plan=plan, bench=dict(arms=['A', 'V2'], events=events, fetches=fetches))


def decide(plan, bench, equal, capture=CAPTURE_OK, **kw):
    return S.decide(plan, bench, equal, final=True, capture_check=capture, **kw)


FAILS = []
PASSES = 0


def check(name, condition, detail=''):
    global PASSES
    if condition:
        PASSES += 1
        print('PASS  %s' % name)
    else:
        FAILS.append(name)
        print('FAIL  %s  %s' % (name, detail))


def controls_pass(result):
    return {k: v.get('pass') for k, v in result['controls'].items()}


def ci(result, stat='Xp'):
    return result['statistics'][stat].get('ci_minus1')


def only_fail(result, control):
    cp = controls_pass(result)
    return cp[control] is False and all(v is True for k, v in cp.items() if k != control) \
        and result['verdict'] is None


def raises(fn, *args, **kw):
    try:
        fn(*args, **kw)
    except ValueError:
        return True
    return False


# ------------------------------------------------------------------ statistics primitives
def test_primitives():
    check('quantile linear = numpy', S.quantile([1.0, 2.0, 3.0, 4.0], 0.05) == 1.15
          and abs(S.quantile([1.0, 2.0, 3.0, 4.0], 0.95) - 3.85) < 1e-12)
    check('quantile single', S.quantile([7.0], 0.3) == 7.0)
    rng = random.Random(5)
    values = [rng.gauss(1.05, 0.02) for _ in range(20)]
    other = [rng.gauss(0.98, 0.05) for _ in range(20)]
    a = S.bootstrap_median_ci(values)
    b = S.bootstrap_median_ci(values)
    check('bootstrap reproducible (seed 103)', a == b and S.BOOT_SEED == 103, a)
    check('bootstrap seed is used (103 differs from 102)', S.bootstrap_median_ci(values, n_boot=40, seed=103)
          != S.bootstrap_median_ci(values, n_boot=40, seed=102))
    check('bootstrap default = 20 000 resamples, seed 103',
          a == S.bootstrap_median_ci(values, n_boot=20000, seed=103, level=0.90))
    check('bootstrap interval brackets the median', a[0] <= S.statistics.median(values) <= a[1], a)
    joint = S.joint_bootstrap_ci({'Xp': values, 'L': other, 'A_over_B': list(values)})
    check('joint bootstrap: SAME indices for every statistic (identical series => identical interval)',
          joint['Xp'] == joint['A_over_B'], joint)
    check('joint bootstrap: a statistic alone equals the same statistic in the joint draw',
          joint['Xp'] == a and S.joint_bootstrap_ci({'L': other})['L'] == joint['L'], (joint, a))
    check('joint bootstrap refuses series over different rounds',
          raises(S.joint_bootstrap_ci, {'x': values, 'y': other[:19]}))
    st = lambda lo, hi: {'Xp': {'ci_minus1': [lo, hi]}}  # noqa: E731
    check('classify: CLOSED needs CI_lo(X\'-1) strictly above 0.06',
          S.classify_interval(st(0.0601, 0.2)) == 'CLOSED' and S.classify_interval(st(0.06, 0.2)) == 'INCONCLUSIVE')
    check('classify: PASSES needs CI_hi(X\'-1) <= 0.06 (0.06 itself passes)',
          S.classify_interval(st(-0.1, 0.06)) == 'PASSES' and S.classify_interval(st(0.0, 0.0601)) == 'INCONCLUSIVE')
    check('classify: straddle is INCONCLUSIVE', S.classify_interval(st(0.03, 0.09)) == 'INCONCLUSIVE')
    # (the point is compared as X' - 1.0 > 0.06, m5_102's arithmetic; exactly 1.06 is a float edge:
    # 1.06 - 1.0 = 0.06000000000000005, so the boundary is tested one step either side, as in m5_102)
    check('classify points after extension: X\'-1 > 0.06 => CLOSED, else PASSES',
          S.classify_points(1.0601) == 'CLOSED' and S.classify_points(1.0599) == 'PASSES'
          and S.classify_points(0.9) == 'PASSES' and S.classify_points(1.2) == 'CLOSED')
    check('sealed constants', S.TOTAL_WEIGHT == round(sum(S.WEIGHTS.values()), 6) and S.THRESHOLD == 0.06
          and S.BOOT_N == 20000 and S.BOOT_SEED == 103 and S.CI_LEVEL == 0.90 and S.MIN_ITEMS == 7
          and S.MIN_WEIGHT_SHARE == 0.60 and S.EXCLUSION_MAX == 0.40 and S.EQUALITY_FAIL_MAX == 0.40
          and (S.NOISE_LO, S.NOISE_HI) == (0.97, 1.03) and S.ROUNDS_SEALED == 20 and S.ROUNDS_FLOOR == 8
          and S.EXT_ROUNDS == 20 and S.A_REPLAYS == 3 and S.NOISE_FACTOR == 2
          and S.ARMS == ('B', 'A', 'V1', 'V2p') and S.VARIANTS == ('V1', 'V2p') and S.DECIDING_STATS == ('Xp',)
          and S.VF_DECIDING == ['--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout']
          and S.CAPTURE_SHA == '92a10b3cad28064e8b16d08dad074758be0627b66ac081dc2fd42f036dcf416d'
          and S.EXE_SHA == 'e7a154187c09b74ed83c5276de80605eaade06845bcf2e9510bc5b3b605726c2'
          and S.SNAPSHOT_DIR == 'C:/kyty/cache_snap/PPSA21564_2db9065a' and S.SIGNATURE_PREFIX == 'KytySC3:2db9065a')
    check('the three seal hashes are the sealed ones',
          S.PRED_SHA == '4035a9b0cc6ae89a671706a12731b3e0f21f29c2caa90763f61c0fab4b688a67'
          and S.PARENT01_SHA == 'cf3c353f7aaa4a2a16d7b59a61461cf26bef11ddbfffd59206ae95a8b6b33e0a'
          and S.PARENT02_SHA == 'ced6d4103c64b9e5b7c81a3a730cac6d2b04a08486f82cf43642b04a8701f4d3'
          and S.seals_ok())


# ------------------------------------------------------------------ the sealed four-arm design and R
def test_design():
    check('DESIGN = [B A V1 V2p], [A V2p B V1], [V1 B V2p A], [V2p V1 A B] (new s4)', S.DESIGN == DESIGN_BY_HAND, S.DESIGN)
    positions = {(a, p): 0 for a in S.ARMS for p in range(4)}
    each_once = all(sorted(seq) == sorted(S.ARMS) for seq in S.DESIGN)
    for seq in S.DESIGN:
        for p, a in enumerate(seq):
            positions[(a, p)] += 1
    check('every sequence holds every arm once, every arm in every position exactly once per cycle',
          each_once and set(positions.values()) == {1}, positions)
    follows = {}
    for seq in S.DESIGN:
        for x, y in zip(seq, seq[1:]):
            follows[(x, y)] = follows.get((x, y), 0) + 1
    check('Williams: every ordered pair of distinct arms is adjacent exactly once per cycle (carry-over balanced)',
          len(follows) == 12 and set(follows.values()) == {1}, follows)
    check('a cycle is four rounds; R = 20 is five cycles', S.CYCLE == 4 and S.ROUNDS_SEALED == 5 * S.CYCLE)
    check('round r uses DESIGN[r mod 4]', [S.DESIGN[r % 4] for r in range(8)] == DESIGN_BY_HAND * 2)
    check('design filtered to two arms (mechanics)', S.design_for(['B', 'A']) == [('B', 'A'), ('A', 'B'), ('B', 'A'), ('A', 'B')])
    tr = S.rounds_after_time_rule
    check('time rule: whole cycles of 4 preferred (fit 15 -> 12, fit 25 -> 20 capped, fit 19 -> 16)',
          tr(20, 3, 15) == 12 and tr(20, 3, 25) == 20 and tr(20, 3, 19) == 16)
    check('time rule: the floor 8 (fit 9 -> 8, fit 5 -> 8, fit 0 -> 8)',
          tr(20, 3, 9) == 8 and tr(20, 3, 5) == 8 and tr(20, 1, 0) == 8)
    check('time rule: rounds already measured are kept (done 13, fit 15 -> 13)', tr(20, 13, 15) == 13)
    check('time rule: never above the request (mechanics R = 1 stays 1)', tr(1, 0, 0) == 1 and tr(12, 0, 30) == 12)
    # the bench's refusals (rd_m5p_bench.py calls m5p_103.bench_sequences)
    check('bench: the sealed arm set in any listing order gets the sealed design',
          S.bench_sequences(['B', 'A', 'V1', 'V2p'], False) == DESIGN_BY_HAND
          and S.bench_sequences(['V2p', 'V1', 'A', 'B'], False) == DESIGN_BY_HAND)
    check('MUTATION bench: a real plan with arms B A V1 only is refused', raises(S.bench_sequences, ['B', 'A', 'V1'], False))
    check('MUTATION bench: session 102\'s five arms (V2, V2s) are refused',
          raises(S.bench_sequences, ['B', 'A', 'V1', 'V2', 'V2s'], False)
          and raises(S.bench_sequences, ['B', 'A', 'V1', 'V2'], False))
    check('MUTATION bench: a plan overriding the design is refused',
          raises(S.bench_sequences, ['B', 'A', 'V1', 'V2p'], False, [['B', 'A', 'V1', 'V2p']]))
    check('MUTATION bench: an arm listed twice is refused', raises(S.bench_sequences, ['B', 'A', 'A', 'V2p'], True))
    check('bench: a mechanics plan may restrict the arms (B, A)', S.bench_sequences(['B', 'A'], True)[1] == ('A', 'B'))
    check('equality: exactly V1, V2p on a real plan; a subset only on a mechanics plan',
          S.equal_variants(['V1', 'V2p'], False) == ['V1', 'V2p'] and raises(S.equal_variants, ['V2p'], False)
          and raises(S.equal_variants, ['V1', 'V2', 'V2s'], False) and S.equal_variants(['V2p'], True) == ['V2p'])
    check('capture: the sealed sha256 passes; another, or none, is refused on a real plan',
          S.capture_sha_problem(S.CAPTURE_SHA, False) is None and S.capture_sha_problem('d' * 64, False)
          and S.capture_sha_problem(None, False) and S.capture_sha_problem(None, True) is None)
    plan = plan_header()
    check('plan seal check: a plan with all three hashes passes; one missing is named',
          S.plan_seal_problems(plan) == [] and len(S.plan_seal_problems(dict(plan, parent02_sha256=None))) == 1
          and len(S.plan_seal_problems(dict(plan, pred_sha256=S.PARENT01_SHA))) == 1)


# ------------------------------------------------------------------ the verdicts of new s0
def test_verdicts():
    r = decide(*make())
    check('A/A: every control passes', all(v is True for v in controls_pass(r).values()), controls_pass(r))
    check('A/A: PASSES, decided on the intervals of the 20 main rounds',
          r['verdict'] == 'PASSES' and abs(r['statistics']['Xp']['minus1']) < 0.01
          and r['branch'].startswith("G's GPU side PASSES") and r['decided_at'].startswith('intervals over the 20')
          and not r['extend'], (r['verdict'], ci(r)))
    check("A/A: X', L, A/B published with intervals from the same resample indices",
          all('ci_minus1' in r['statistics'][s] for s in ('Xp', 'L', 'A_over_B'))
          and r['bootstrap']['same_indices'] == sorted(['Xp', 'L', 'A_over_B']) and r['bootstrap']['seed'] == 103)
    r = decide(*make(v2p=1.10))
    check("CLOSED: X' +10 % => CI_lo(X'-1) > 0.06", r['verdict'] == 'CLOSED' and ci(r)[0] > 0.06
          and r['branch'].startswith('G CLOSED'), (r['verdict'], ci(r)))
    r = decide(*make(v2p=1.02))
    check("PASSES: X' +2 % => CI_hi(X'-1) <= 0.06", r['verdict'] == 'PASSES' and ci(r)[1] <= 0.06, (r['verdict'], ci(r)))
    r = decide(*make(v2p=0.95))
    check("PASSES: X' below 1 (V2p faster than A)", r['verdict'] == 'PASSES', r['verdict'])
    r = decide(*make(v1=1.10, v2p=1.0))
    check('L +10 % is reported and never decides (X\' = 1 => PASSES)', r['verdict'] == 'PASSES'
          and ci(r, 'L')[0] > 0.06 and not r['statistics']['L']['deciding'], (r['verdict'], ci(r, 'L')))
    r = decide(*make(v1=1.0, v2p=1.10, ab=1.02))
    check('A/B reported (+2 %), never deciding', abs(r['statistics']['A_over_B']['minus1'] - 0.02) < 0.01
          and r['verdict'] == 'CLOSED')
    straddle = dict(v2p=1.06, noise=0.03, seed=7)
    r = decide(*make(**straddle))
    lo, hi = ci(r)
    check("X' straddles 0.06 => INCONCLUSIVE, EXTENSION REQUIRED, the extension is owed",
          r['statistical_classification'] == 'INCONCLUSIVE' and lo <= 0.06 < hi and r['extend']
          and r['verdict'] == 'INCONCLUSIVE' and r['status'].startswith('EXTENSION REQUIRED'), (lo, hi, r['status']))
    r = decide(*make(ext_rounds=20, ext={'V2p': 1.14}, **straddle))
    check("... extension at X' +14 %: CLOSED at the point, 'decided at the point after extension' (40 rounds)",
          r['verdict'] == 'CLOSED' and 'decided at the point after extension' in r['decided_at']
          and r['extension']['n_rounds'] == 40 and r['extension']['minus1']['Xp'] > 0.06 and not r['extend']
          and r['status'] == 'VALID', (r['verdict'], r.get('extension')))
    r = decide(*make(ext_rounds=20, ext={'V2p': 1.02}, **straddle))
    check("... extension at X' +2 %: PASSES at the point", r['verdict'] == 'PASSES'
          and 'point after extension' in r['decided_at'] and r['extension']['minus1']['Xp'] <= 0.06,
          (r['verdict'], r.get('extension')))
    r = decide(*make(ext_rounds=20, ext={'V2p': 1.06}, **straddle))
    check("... extension that stays on the line: the point decides either way, never INCONCLUSIVE",
          r['verdict'] in ('CLOSED', 'PASSES') and r['verdict'] == S.classify_points(r['extension']['points']['Xp']))
    r = decide(*make(ext_rounds=12, **straddle))
    check('straddle + incomplete extension (12 of 20): no verdict', r['verdict'] == 'INCONCLUSIVE'
          and r['status'].startswith('EXTENSION REQUIRED (12 of 20') and r['extend'])
    p, b, e = make(ext_rounds=20, ext={'V2p': 1.14}, **straddle)
    for f in b['fetches']:
        if f['phase'] == 'extension' and f['round'] == 30 and f['arm'] == 'V1':
            f['d'][0] = None
    r = decide(p, b, e)
    check('MUTATION V-g: a missing value in the extension (even of an arm that does not decide) => INVALID',
          r['verdict'] is None and r['status'] == 'INVALID' and 'V-g (extension missing values)' in r['failed_controls'])
    r = decide(*make(v2p=1.10, ext_rounds=20, ext={'V2p': 1.0}))
    check('a decided interval ignores extension rounds', r['verdict'] == 'CLOSED'
          and r['statistics']['Xp']['n_rounds'] == 20 and 'extension' not in r)
    r = decide(*make(v2p=1.10, v1=1.03, ab=1.01))
    row = r['per_item']['S4']
    check('per-item ratios published (B/A, V1/A, V2p/A) with the V-e table',
          all(row.get(k) is not None for k in ('B/A', 'V1/A', 'V2p/A')) and abs(row['V2p/A'] - 1.10) < 0.02
          and row['V-e'] == {'V1': 'pass', 'V2p': 'pass'}, row)
    r = S.decide(*make(**straddle), final=False)
    check('interim (final=False, no capture log): INCONCLUSIVE owes the extension (what the bench uses)',
          r['extend'] is True and r['controls']['V-a']['pass'] is None and r['status'] == 'VALID')


# ------------------------------------------------------------------ the amended V-e and the 40 % rule
def test_ve():
    j = S.ve_judge
    check('ve_judge: repeatable and bit-equal => pass "bit-equal"', j(pairs_for(0), 0, True)['kind'] == 'bit-equal')
    check('MUTATION V-e: repeatable item, ONE differing byte => fail', j(pairs_for(0), 1, False)['pass'] is False)
    check('ve_judge: repeatable, zero count but not bit-equal => fail', j(pairs_for(0), 0, False)['pass'] is False)
    check('ve_judge: nondeterministic E = 100, 150 bytes => pass within replay noise',
          j(pairs_for(100), 150, False) == {'pass': True, 'kind': 'within replay noise', 'E': 100, 'limit': 200,
                                            'repeatable': False, 'reason': None})
    check('ve_judge: exactly 2E passes', j(pairs_for(100), 200, False)['pass'] is True)
    check('MUTATION V-e: nondeterministic, 2E + 1 bytes => fail', j(pairs_for(100), 201, False)['pass'] is False)
    check('ve_judge: a nondeterministic item equal to A1 is "within replay noise", never "equal"',
          j(pairs_for(100), 0, True)['kind'] == 'within replay noise')
    check('ve_judge: E is the LARGEST pair', j({'A1-A2': 1, 'A1-A3': 2, 'A2-A3': 50}, 100, False)['pass'] is True
          and j({'A1-A2': 1, 'A1-A3': 2, 'A2-A3': 50}, 101, False)['pass'] is False)
    check('MUTATION V-e: only two A replays (one pair) => fail', j({'A1-A2': 5}, 0, True)['pass'] is False)

    r = decide(*make(v2p=1.10, nondet={'S2': 100}, eq_ndiff={('S2', 'V2p'): 200, ('S2', 'V1'): 50}))
    ve = r['controls']['V-e']
    check('nondeterministic item at 2E passes V-e "within replay noise" for V1 and V2p and is summed',
          'S2' in ve['V2p']['within_replay_noise'] and 'S2' in ve['V1']['within_replay_noise']
          and 'S2' in r['statistics']['Xp']['items'] and ve['nondeterministic_reference'] == ['S2']
          and ve['E']['S2'] == 100 and any('WITHIN REPLAY NOISE' in n for n in r['notes']), ve['V2p'])
    r = decide(*make(v2p=1.10, nondet={'S2': 100}, eq_ndiff={('S2', 'V2p'): 201}))
    check("... and at 2E + 1 fails V-e for V2p and leaves X' (both sums) but stays in L",
          'S2' in r['controls']['V-e']['V2p']['failing'] and 'S2' not in r['statistics']['Xp']['items']
          and 'S2' in r['statistics']['L']['items'], r['controls']['V-e']['V2p'])
    r = decide(*make(v2p=1.10, eq_ndiff={('S1', 'V2p'): 9, ('S2', 'V2p'): 9, ('S3', 'V2p'): 9}))
    check("MUTATION V-e: V2p failures above 40 % (S1+S2+S3 = 43.9 %) => M5' NOT DECIDED, no verdict",
          r['controls']['V-e']['pass'] is False and r['verdict'] is None and r['branch'] is None
          and r['status'].startswith("M5' NOT DECIDED") and r['controls']['V-e']['V2p']['failing_share'] > 0.40
          and not r['extend'], (r['status'], r['controls']['V-e']['V2p']))
    check("... X', L are still published on an undecided bench", all('point' in r['statistics'][s] for s in ('Xp', 'L')))
    r = decide(*make(v2p=1.10, eq_ndiff={('S1', 'V2p'): 9, ('S2', 'V2p'): 9}))
    check('V2p failures below 40 % (S1+S2 = 33.3 %) leave the bench decidable (CLOSED on the 8 others)',
          r['controls']['V-e']['pass'] is True and r['verdict'] == 'CLOSED'
          and 0.30 < r['controls']['V-e']['V2p']['failing_share'] < 0.40
          and r['statistics']['Xp']['items'] == ['S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10'])
    r = decide(*make(v2p=1.0, per_item={('S1', 'V2p'): 1.8}, eq_ndiff={('S1', 'V2p'): 9}))
    check("a V2p failure leaves BOTH sums of X': an item 80 % slower but failing V-e does not move X'",
          'S1' not in r['statistics']['Xp']['items'] and abs(r['statistics']['Xp']['minus1']) < 0.01
          and r['verdict'] == 'PASSES', (r['statistics']['Xp'].get('minus1'), r['verdict']))
    r = decide(*make(v2p=1.0, per_item={('S1', 'V2p'): 1.8}))
    check('... and the same item passing V-e is summed (control of the control)', r['verdict'] == 'CLOSED', r['verdict'])
    r = decide(*make(v1=1.10, eq_ndiff={(n, 'V1'): 7 for n, _ in ITEMS[:6]}))
    check('> 40 % failing for V1 is a note, never a failure (the rule decides for V2p only)',
          r['controls']['V-e']['pass'] is True and r['controls']['V-e']['V1']['share_within_40pct'] is False
          and any('V1 fails' in n for n in r['notes']) and r['verdict'] == 'PASSES')
    r = decide(*make(v2p=1.10, eq_ndiff={(n, 'V1'): 7 for n, _ in ITEMS}))
    check('every item failing V1 => L unavailable, the verdict still stands on X\'',
          'unavailable' in r['statistics']['L'] and r['verdict'] == 'CLOSED' and r['predictions']['P3']['hit'] is None)
    p, b, e = make(v2p=1.10)
    for rec in e['items'].values():
        rec['variants']['V2'] = rec['variants'].pop('V2p')
    r = decide(p, b, e)
    check("MUTATION V-e: an equality file of session 102's arm names (V2, not V2p) => V2p fails everywhere => NOT DECIDED",
          r['status'].startswith("M5' NOT DECIDED") and r['controls']['V-e']['V2p']['failing_share'] == 1.0)
    p, b, e = make(v2p=1.10)
    del e['items']['S1']
    r = decide(p, b, e)
    check('a missing equality record counts as a V-e fail of that item for both variants',
          all('S1' in r['controls']['V-e'][a]['failing'] for a in S.VARIANTS))
    p, b, e = make(v2p=1.10)
    del e['items']['S3']['variants']['V1']
    r = decide(p, b, e)
    check('a missing V1 record fails S3 for V1 only', 'S3' in r['controls']['V-e']['V1']['failing']
          and 'S3' not in r['controls']['V-e']['V2p']['failing'])
    p, b, e = make(v2p=1.10)
    e['items']['S2']['reference_replays'] = 2
    r = decide(p, b, e)
    check('MUTATION V-e: an equality record with two A replays fails that item',
          all('S2' in r['controls']['V-e'][a]['failing'] for a in S.VARIANTS)
          and 'replayed 2 times' in r['controls']['V-e']['V2p']['reasons']['S2'])
    p, b, e = make(v2p=1.10)
    e['reference'] = 'B'
    r = decide(p, b, e)
    check('MUTATION V-e: an equality file made against B (diagnostic) is not V-e',
          r['controls']['V-e']['pass'] is False and r['verdict'] is None)
    p, b, e = make(v2p=1.10)
    e['items']['S4']['variants']['V2p']['pass'] = False
    r = decide(p, b, e)
    check("the tool's own pass flag is never trusted; a disagreement is noted",
          'S4' not in r['controls']['V-e']['V2p']['failing'] and any('scorer judges' in n for n in r['notes']))
    p, b, e = make(v2p=1.10)
    e['items']['S5']['error'] = 'reference replacement not in effect at the last event'
    r = decide(p, b, e)
    check('an item-level equality error fails the item for both variants',
          all('S5' in r['controls']['V-e'][a]['failing'] for a in S.VARIANTS))
    p, b, e = make(v2p=1.10)
    p['items']['S6']['arm_missing'] = {'V2p': [0]}
    r = decide(p, b, e)
    check('a missing V2p module fails that item for V2p', 'S6' in r['controls']['V-e']['V2p']['failing']
          and 'missing' in r['controls']['V-e']['V2p']['reasons']['S6'])
    p, b, e = make(v2p=1.10)
    r = S.decide(p, b, None, final=True, capture_check=CAPTURE_OK)
    check('no equality file => V-e not evaluated => no verdict', r['controls']['V-e']['pass'] is None
          and r['verdict'] is None and r['status'].startswith('NOT EVALUABLE'))


# ------------------------------------------------------------------ the other controls, each one alone
def test_controls():
    base = make(v2p=1.10)
    ok = decide(*base)
    check('reference fixture: all seven controls PASS and CLOSED',
          all(v is True for v in controls_pass(ok).values()) and ok['verdict'] == 'CLOSED', controls_pass(ok))
    # V-a
    r = decide(*base, capture={'dma_layout': False, 'clock_pin': True})
    check('MUTATION V-a: no DmaLayout line', only_fail(r, 'V-a'), controls_pass(r))
    r = decide(*base, capture={'dma_layout': True, 'clock_pin': False})
    check('MUTATION V-a: no GpuClockPin line', only_fail(r, 'V-a'), controls_pass(r))
    p, b, e = copy.deepcopy(base)
    b['capture_sha256'] = 'd' * 64
    r = decide(p, b, e)
    check('MUTATION V-a: bench opened another capture than the plan', only_fail(r, 'V-a'), controls_pass(r))
    p, b, e = copy.deepcopy(base)
    b['capture_sha256'] = p['capture_sha256'] = 'd' * 64
    r = decide(p, b, e)
    check('MUTATION V-a: plan and bench agree on a capture that is not the sealed one (new s2)',
          only_fail(r, 'V-a') and r['controls']['V-a']['sha_match'] and not r['controls']['V-a']['sha_sealed'])
    r = decide(*base, capture=None)
    check('V-a not evaluated => no verdict', r['verdict'] is None and r['controls']['V-a']['pass'] is None
          and r['status'].startswith('NOT EVALUABLE'))
    # V-b
    r = decide(*make(v2p=1.10, present=['S1', 'S2', 'S3', 'S4', 'S5', 'S6']))
    cp = controls_pass(r)
    check('MUTATION V-b: 6 of 10 items => V-b FAIL, INVALID', cp['V-b'] is False and r['verdict'] is None
          and r['status'] == 'INVALID', cp)
    r = decide(*make(v2p=1.10, present=['S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10']))
    check('MUTATION V-b: 7 items carrying 56.2 % < 60 % => V-b FAIL',
          r['controls']['V-b']['pass'] is False and abs(r['controls']['V-b']['weight_share'] - 2532.7 / 4508.0) < 1e-9
          and r['verdict'] is None, r['controls']['V-b'])
    r = decide(*make(v2p=1.10, present=['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7']))
    check('7 items carrying 78 %: V-b PASS', r['controls']['V-b']['pass'] is True and r['verdict'] == 'CLOSED')
    # V-c
    r = decide(*make(v2p=1.10, excluded_share=0.45))
    check('MUTATION V-c: 45 % of the A time excluded => V-c FAIL', only_fail(r, 'V-c'), r['controls']['V-c'])
    r = decide(*make(v2p=1.10, wholly_excluded=('S1',)))
    check('an item present only through the cache link counts for V-b and wholly in V-c',
          r['controls']['V-b']['present'] == 10 and not r['items']['S1']['a_valid']
          and abs(r['controls']['V-c']['excluded_share'] - 1009.1 / 4508.0) < 0.01
          and r['controls']['V-c']['pass'] is True and 'S1' not in r['statistics']['Xp']['items']
          and r['verdict'] == 'CLOSED', (r['controls']['V-b'], r['controls']['V-c']))
    r = decide(*make(v2p=1.10, wholly_excluded=('S1', 'S2', 'S3', 'S4')))
    check('MUTATION V-c: four items not reproduced (53.2 % of the time) => V-c FAIL', only_fail(r, 'V-c'))
    r = decide(*make(v2p=1.10, excluded_share=0.30))
    check('30 % excluded: V-c PASS and excluded events never summed', r['controls']['V-c']['pass'] is True
          and abs(r['controls']['V-c']['excluded_share'] - 0.30) < 0.01 and r['verdict'] == 'CLOSED'
          and abs(r['statistics']['Xp']['minus1'] - 0.10) < 0.02)
    # V-d
    r = decide(*make(v2p=1.10, ab=1.05))
    check('MUTATION V-d: A/B = 1.05 => V-d FAIL', only_fail(r, 'V-d'), r['controls']['V-d'])
    r = decide(*make(v2p=1.10, ab=0.96))
    check('MUTATION V-d: A/B = 0.96 => V-d FAIL', only_fail(r, 'V-d'))
    r = decide(*make(v2p=1.10, ab=1.02))
    check('A/B = 1.02: V-d PASS', r['controls']['V-d']['pass'] is True)
    # V-f
    p, b, e = make(v2p=1.10)
    first = sorted(p['validation'])[0]
    p['validation'][first]['ubsl']['ok'] = False
    r = decide(p, b, e)
    check('MUTATION V-f: one module fails the deciding command (--uniform-buffer-standard-layout)',
          only_fail(r, 'V-f'), controls_pass(r))
    p, b, e = make(v2p=1.10)
    for path in p['validation']:
        p['validation'][path]['pred01']['ok'] = False
    r = decide(p, b, e)
    check("failing only 102 pred/01's original command never fails V-f (reported)",
          r['controls']['V-f']['pass'] is True and r['controls']['V-f']['failing_pred01_command_reported'] == 30)
    p, b, e = make(v2p=1.10)
    p['validation'].pop(sorted(p['validation'])[-1])
    r = decide(p, b, e)
    check('MUTATION V-f: a module without a spirv-val result fails V-f', only_fail(r, 'V-f'))
    # V-g
    p, b, e = make(v2p=1.10)
    b['fetches'][5]['d'][0] = None
    r = decide(p, b, e)
    check('MUTATION V-g: a fetch returned no value for an item event', controls_pass(r)['V-g'] is False and r['verdict'] is None)
    p, b, e = make(v2p=1.10)
    b['complete'] = False
    r = decide(p, b, e)
    check('MUTATION V-g: bench not complete', only_fail(r, 'V-g'))
    p, b, e = make(v2p=1.10, rounds=19)
    r = decide(p, b, e)
    check('MUTATION V-g: 19 of 20 rounds', only_fail(r, 'V-g'))
    p, b, e = make(v2p=1.10, rounds=12, requested=12)
    r = decide(p, b, e)
    check("MUTATION V-g: 102 pred/01's R = 12 requested instead of 20", only_fail(r, 'V-g'),
          r['controls']['V-g']['reasons'])
    p, b, e = make(v2p=1.10)
    b['build_errors'] = [dict(arm='V1', item='S1', messages='boom')]
    r = decide(p, b, e)
    check('MUTATION V-g: a module failed to build', controls_pass(r)['V-g'] is False and r['verdict'] is None)
    p, b, e = make(v2p=1.10, rounds=12)
    b['decisions'] = [dict(kind='rounds_drop', rounds_before=20, rounds_after=12)]
    r = decide(p, b, e)
    check('4-hour rule: R dropped to three whole cycles (12) with 12 rounds done passes V-g',
          r['controls']['V-g']['pass'] is True and r['verdict'] == 'CLOSED')
    p, b, e = make(v2p=1.10, rounds=8)
    b['decisions'] = [dict(kind='rounds_drop', rounds_before=20, rounds_after=8)]
    r = decide(p, b, e)
    check('4-hour rule: R dropped to the floor 8 passes V-g', r['controls']['V-g']['pass'] is True)
    p, b, e = make(v2p=1.10, rounds=6)
    b['decisions'] = [dict(kind='rounds_drop', rounds_before=20, rounds_after=6)]
    r = decide(p, b, e)
    check('MUTATION V-g: R dropped below 8', only_fail(r, 'V-g'))
    p, b, e = make(v2p=1.10)
    b['replacement_check_ok'] = False
    r = decide(p, b, e)
    check('MUTATION V-g: a replacement not in effect', only_fail(r, 'V-g'))
    p, b, e = make(v2p=1.10)
    b['fetches'] = [f for f in b['fetches'] if not (f['round'] == 3 and f['arm'] == 'V1')]
    r = decide(p, b, e)
    check('an incomplete round is not counted (19 complete rounds => V-g FAIL)',
          r['rounds_main'] == 19 and only_fail(r, 'V-g'))
    p, b, e = make(v2p=1.10)
    b['arms'] = ['B', 'A', 'V1']
    b['fetches'] = [f for f in b['fetches'] if f['arm'] != 'V2p']
    for f in b['fetches']:
        f['pos'] = S.design_for(b['arms'])[f['round'] % 4].index(f['arm'])
    r = decide(p, b, e)
    check("MUTATION V-g: a three-arm bench (no V2p) => V-g FAIL and X' unavailable",
          controls_pass(r)['V-g'] is False and r['verdict'] is None and 'unavailable' in r['statistics']['Xp'],
          r['controls']['V-g']['reasons'])
    p, b, e = make(v2p=1.10)
    b['arms'] = ['B', 'A', 'V1', 'V2p', 'V2s']
    r = decide(p, b, e)
    check('MUTATION V-g: a bench listing a fifth arm (V2s) => V-g FAIL', controls_pass(r)['V-g'] is False
          and r['verdict'] is None)
    # the design order
    p, b, e = make(v2p=1.10)
    for f in b['fetches']:
        if f['round'] == 3 and f['pos'] in (1, 2):
            f['pos'] = 3 - f['pos']
    r = decide(p, b, e)
    check('MUTATION V-g: round 3 measured out of the sealed order => design violation',
          only_fail(r, 'V-g') and r['controls']['V-g']['design_violations'][0]['round'] == 3)
    p, b, e = make(v2p=1.10)
    for f in b['fetches']:
        if f['round'] == 7:
            f['seq_index'] = 2
    r = decide(p, b, e)
    check('MUTATION V-g: a wrong recorded sequence index', only_fail(r, 'V-g'))
    p, b, e = make(v2p=1.10)
    for f in b['fetches']:
        f.pop('seq_index')
    r = decide(p, b, e)
    check('MUTATION V-g: sequence index not recorded (real bench)', only_fail(r, 'V-g'))
    p, b, e = make(v2p=1.10)
    for f in b['fetches']:          # B A V1 V2p in every round: only rounds r = 0 mod 4 are in order
        f['pos'] = S.ARMS.index(f['arm'])
    r = decide(p, b, e)
    check('MUTATION V-g: the same order every round (not the Williams design) => 15 design violations',
          only_fail(r, 'V-g') and len(r['controls']['V-g']['design_violations']) == 15,
          len(r['controls']['V-g']['design_violations']))
    p, b, e = make(v2p=1.10)
    for f in b['fetches']:          # session 102's cyclic rotations would put round 1 as A V1 V2p B
        if f['round'] == 1:
            f['pos'] = ['A', 'V1', 'V2p', 'B'].index(f['arm'])
    r = decide(p, b, e)
    check('MUTATION V-g: a rotation instead of the Williams sequence in round 1 => violation',
          only_fail(r, 'V-g') and r['controls']['V-g']['design_violations'][0]['round'] == 1)
    p, b, e = make(v2p=1.06, noise=0.03, seed=7, ext_rounds=20, ext={'V2p': 1.14})
    for f in b['fetches']:
        if f['round'] == 25 and f['pos'] in (0, 3):
            f['pos'] = 3 - f['pos']
    r = decide(p, b, e)
    check('MUTATION V-g: an extension round out of order is caught too', controls_pass(r)['V-g'] is False
          and r['verdict'] is None)


# ------------------------------------------------------------------ predictions
def test_predictions():
    r = decide(*make(v2p=1.10, v1=1.02))
    p = r['predictions']
    check("P1' HIT at X' +10 %", p['P1']['hit'] is True)
    check("P2' HIT with 10 items passing V-e for V2p", p['P2']['hit'] is True and p['P2']['value'] == 10)
    check("P3' HIT at L +2 %", p['P3']['hit'] is True)
    check("P4' HIT: X' 1.10 < 1.4201 on the eight common items (the sealed number)",
          p['P4']['hit'] is True and p['P4']['value']['x102_common'] == 1.4201
          and sorted(p['P4']['value']['common_items']) == sorted(S.P4_ITEMS102)
          and abs(p['P4']['value']['xp_common'] - 1.10) < 0.02)
    r = decide(*make(v2p=1.50, v1=0.98, eq_ndiff={('S8', 'V2p'): 1, ('S9', 'V2p'): 1, ('S10', 'V2p'): 1}))
    p = r['predictions']
    check("P1' MISS at +50 %, P2' MISS at 7 passing, P3' MISS at -2 %",
          p['P1']['hit'] is False and p['P2']['hit'] is False and p['P2']['value'] == 7 and p['P3']['hit'] is False)
    check("P4' not evaluable when the common set is not the eight and no session-102 bench is given",
          p['P4']['hit'] is None and p['P4']['value']['x102_common'] is None
          and sorted(p['P4']['value']['common_items']) == ['S2', 'S3', 'S4', 'S5', 'S6', 'S7'])
    prev = make_prev102(1.30)
    r = decide(*make(v2p=1.50, eq_ndiff={('S9', 'V2p'): 1}), prev102=prev)
    p4 = r['predictions']['P4']
    check("P4' with the session-102 bench: X of 102 recomputed on the common seven (1.30) => MISS at 1.50",
          p4['hit'] is False and abs(p4['value']['x102_common'] - 1.30) < 0.01
          and 'recomputed' in p4['value']['x102_source'] and len(p4['value']['common_items']) == 7, p4)
    r = decide(*make(v2p=1.10, eq_ndiff={('S9', 'V2p'): 1}), prev102=prev)
    check("... and HIT at 1.10", r['predictions']['P4']['hit'] is True)
    real_plan = Path(S.PREV102_PLAN)
    real_bench = Path(S.PREV102_BENCH)
    if real_plan.exists() and real_bench.exists():
        prev_real, files = S.load_prev102(str(real_plan), str(real_bench))
        r = decide(*make(v2p=1.10), prev102=prev_real)
        x8 = r['predictions']['P4']['value'].get('x102_eight_recomputed')
        check("P4': the session-102 bench recomputes X = 1.420062635 on its eight items (the scorer's own ratio)",
              x8 is not None and abs(x8 - S.P4_X102_EXACT) < 1e-9 and round(x8, 4) == S.P4_X102, x8)
    else:
        print('SKIP  the session-102 bench is not on disk')


# ------------------------------------------------------------------ the command line: seals, identity, overwrite
def test_cli():
    tmp = Path(tempfile.mkdtemp(prefix='m5p_103_'))
    try:
        plan, bench, equal = make(v2p=1.10)
        (tmp / 'plan.json').write_text(json.dumps(plan))
        sha = S.sha256_file(tmp / 'plan.json')
        bench['plan_sha256'] = sha
        equal['plan_sha256'] = sha
        (tmp / 'bench.json').write_text(json.dumps(bench))
        (tmp / 'equal.json').write_text(json.dumps(equal))
        (tmp / 'log.txt').write_bytes(b'x\nDmaLayout: mode 1\nGpuClockPin: mode 1\n')
        args = ['--plan', str(tmp / 'plan.json'), '--bench', str(tmp / 'bench.json'),
                '--equal', str(tmp / 'equal.json'), '--capture-log', str(tmp / 'log.txt'),
                '--prev102-plan', '', '--prev102-bench', '']
        code = S.main(args + ['--out', str(tmp / 'out.json')])
        out = json.loads((tmp / 'out.json').read_text())
        check('CLI: scores the reference fixture to CLOSED with all three seals recorded',
              code == 0 and out['verdict'] == 'CLOSED' and out['identity']['pass'] is True
              and out['seals']['pred']['sha256'] == S.PRED_SHA and out['seals']['parent01']['sha256'] == S.PARENT01_SHA
              and out['seals']['parent02']['sha256'] == S.PARENT02_SHA, out.get('status'))
        code = S.main(args + ['--out', str(tmp / 'out.json')])
        check('CLI: never overwrites --out', code == 2)
        for which, source in (('pred', S.PRED), ('parent01', S.PARENT01), ('parent02', S.PARENT02)):
            bad = tmp / ('%s_bad.md' % which)
            shutil.copy(source, bad)
            with open(bad, 'ab') as stream:
                stream.write(b' ')
            target = tmp / ('out_bad_%s.json' % which)
            code = S.main(args + ['--out', str(target), '--%s' % which, str(bad)])
            check('MUTATION seal: a changed %s is refused by the scorer' % which, code == 2 and not target.exists())
            good = tmp / ('%s_copy.md' % which)
            shutil.copy(source, good)
            code = S.main(args + ['--out', str(tmp / ('out_good_%s.json' % which)), '--%s' % which, str(good)])
            check('... a byte-identical copy of %s is accepted' % which, code == 0)
            target = tmp / ('out_missing_%s.json' % which)
            code = S.main(args + ['--out', str(target), '--%s' % which, str(tmp / 'does_not_exist.md')])
            check('MUTATION seal: a missing %s is refused' % which, code == 2 and not target.exists())
        bench['plan_sha256'] = 'e' * 64
        (tmp / 'bench_other.json').write_text(json.dumps(bench))
        args2 = list(args)
        args2[3] = str(tmp / 'bench_other.json')
        S.main(args2 + ['--out', str(tmp / 'out4.json')])
        out = json.loads((tmp / 'out4.json').read_text())
        check('MUTATION identity: a bench of another plan is INVALID', out['verdict'] is None
              and 'IDENTITY' in out['failed_controls'] and out['identity']['files_pass'] is False)

        def with_plan(tag, change):
            p2 = copy.deepcopy(plan)
            change(p2)
            (tmp / ('plan_%s.json' % tag)).write_text(json.dumps(p2))
            sha2 = S.sha256_file(tmp / ('plan_%s.json' % tag))
            b2 = dict(bench, plan_sha256=sha2)
            e2 = dict(equal, plan_sha256=sha2)
            (tmp / ('bench_%s.json' % tag)).write_text(json.dumps(b2))
            (tmp / ('equal_%s.json' % tag)).write_text(json.dumps(e2))
            S.main(['--plan', str(tmp / ('plan_%s.json' % tag)), '--bench', str(tmp / ('bench_%s.json' % tag)),
                    '--equal', str(tmp / ('equal_%s.json' % tag)), '--capture-log', str(tmp / 'log.txt'),
                    '--prev102-plan', '', '--prev102-bench', '', '--out', str(tmp / ('out_%s.json' % tag))])
            return json.loads((tmp / ('out_%s.json' % tag)).read_text())

        out = with_plan('noparent', lambda p2: p2.pop('parent02_sha256'))
        check('MUTATION identity: a plan not made under the parent addendum is INVALID', out['verdict'] is None
              and 'IDENTITY' in out['failed_controls'] and out['identity']['seal_problems'])
        out = with_plan('old', lambda p2: p2.update(pred_sha256=S.PARENT01_SHA, addendum_sha256=S.PARENT02_SHA))
        check("MUTATION identity: a session-102 plan (pred_sha256 = 102's pred/01) is INVALID",
              out['verdict'] is None and 'IDENTITY' in out['failed_controls'])
        out = with_plan('exe', lambda p2: p2.update(recompile_exe_sha256='cfe15c6c' + '0' * 56))
        check('MUTATION inputs: modules built by another shader_cfg_tests.exe => INVALID',
              out['verdict'] is None and any('test recompiler' in x for x in out['identity']['input_problems']))
        out = with_plan('cache', lambda p2: p2.update(cache_dir='C:/Users/<user>/OneDrive/Desktop/ps5 em/_ShaderCache/PPSA21564'))
        check('MUTATION inputs: a plan linked against the live _ShaderCache, not the snapshot => INVALID',
              out['verdict'] is None and any('cache link dir' in x for x in out['identity']['input_problems']))
        out = with_plan('snapcase', lambda p2: p2.update(cache_dir='c:\\kyty\\cache_snap\\PPSA21564_2db9065a\\'))
        check('inputs: the snapshot written with backslashes / another case is the same directory',
              out['verdict'] == 'CLOSED' and out['identity']['pass'] is True, out['identity'])
        (tmp / 'log_bad.txt').write_bytes(b'DmaLayout: mode 0\nGpuClockPin: mode 1\n')
        args3 = list(args)
        args3[7] = str(tmp / 'log_bad.txt')
        S.main(args3 + ['--out', str(tmp / 'out5.json')])
        out = json.loads((tmp / 'out5.json').read_text())
        check('MUTATION V-a via the log: DmaLayout mode 0', out['verdict'] is None and out['controls']['V-a']['pass'] is False)
        S.main(args + ['--out', str(tmp / 'out7.json'), '--mechanics-only'])
        out = json.loads((tmp / 'out7.json').read_text())
        check('--mechanics-only never publishes a verdict', out['verdict'] is None and out['branch'] is None
              and out['status'].startswith("MECHANICS ONLY"))
        check('the rd tools\' seal check (m5p_103.require_seals) verifies all three files',
              sorted(S.require_seals()) == ['parent01', 'parent02', 'pred'])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------ the planner
def test_plan():
    tmp = Path(tempfile.mkdtemp(prefix='m5p_plan_'))
    try:
        paths = {arm: S102_SPV % arm for arm in ('A', 'V1', 'V2', 'V2s')}
        if not all(os.path.isfile(p) for p in paths.values()):
            print('SKIP  planner: session-102 stand-in modules missing')
            return
        a_bytes, v1_bytes, v2_bytes, v2s_bytes = (Path(paths[a]).read_bytes() for a in ('A', 'V1', 'V2', 'V2s'))
        md5 = lambda b: hashlib.md5(b).hexdigest()  # noqa: E731
        # synthetic recompile.json in the m5p_recompile.py format; V2 bytes stand in for V2p
        rec = dict(exe_sha256=S.EXE_SHA, cache_dir=S.SNAPSHOT_DIR, signature=S.SIGNATURE_PREFIX,
                   pred_sha256=S.PRED_SHA, arms={'A': {}, 'V1': {'KYTY_RECOMPILE_CBANK': '0'},
                                                 'V2p': {'KYTY_RECOMPILE_BDA': '1', 'KYTY_BDA_LEAN': '1'}},
                   items=[dict(item='S3', stage='ps', hash='3d705c1b57adec00', caches=[dict(
                       cache_id='b519b730d6966fd7', modules=[
                           dict(name='S3_x_p0_A', arm='A', perm=0, spv=paths['A'], md5=md5(a_bytes)),
                           dict(name='S3_x_p0_V1', arm='V1', perm=0, spv=paths['V1'], md5=md5(v1_bytes)),
                           dict(name='S3_x_p0_V2p', arm='V2p', perm=0, spv=paths['V2'], md5=md5(v2_bytes)),
                           dict(name='S3_x_p0_V2s', arm='V2s', perm=0, spv=paths['V2s'], md5=md5(v2s_bytes))])])])
        (tmp / 'recompile.json').write_text(json.dumps(rec))
        cache_dir = tmp / 'cache'
        cache_dir.mkdir()
        blob = b'KytySC3:2db9065aef8b54a24a7d29b3584df9647f61dd95:robust:ftz:cbank\n'
        for spv in (v1_bytes, a_bytes, v2s_bytes):      # index 0 (recompiled, not A), 1 (= A), 2 (never recompiled)
            blob += struct.pack('<I', len(spv) // 4) + spv
        (cache_dir / 'ps_3d705c1b57adec00_b519b730d6966fd7.bin').write_bytes(blob)
        mods = {'ResourceId::1': dict(stage='ps', md5=md5(a_bytes), size=len(a_bytes)),
                'ResourceId::2': dict(stage='ps', md5=md5(v1_bytes), size=len(v1_bytes)),
                'ResourceId::3': dict(stage='ps', md5=md5(v2s_bytes), size=len(v2s_bytes))}
        events = [dict(eid=10, kind='draw', ps='ResourceId::1'), dict(eid=11, kind='draw', ps='ResourceId::2'),
                  dict(eid=12, kind='draw', ps='ResourceId::3'), dict(eid=13, kind='draw', ps='ResourceId::1'),
                  dict(eid=14, kind='dispatch', cs='ResourceId::1')]
        find = dict(complete=True, capture='synthetic', capture_sha256=S.CAPTURE_SHA, modules=mods, events=events)
        (tmp / 'find.json').write_text(json.dumps(find))
        out = tmp / 'plan.json'
        base_args = ['--find', str(tmp / 'find.json'), '--recompile', str(tmp / 'recompile.json'),
                     '--regs', '0', '--layout', '0']
        code = P.main(base_args + ['--out', str(out), '--cache-dir', str(cache_dir), '--items', 'S3'])
        plan = json.loads(out.read_text())
        item = plan['items']['S3']
        arms = {a['name']: a for a in plan['arms']}
        check('plan: four arms B / A / V1 / V2p; the V2s module of an old recompile.json is ignored with a note',
              code == 0 and [a['name'] for a in plan['arms']] == ['B', 'A', 'V1', 'V2p']
              and len(arms['V2p']['replacements']) == 1 and arms['V2p']['replacements'][0]['spv_path'] == paths['V2']
              and arms['V2p']['replacements'][0]['orig_shader_id'] == 'ResourceId::1'
              and any('unknown arm' in n for n in plan['notes']), plan['arms'])
        check('plan: included module events 10 and 13 (a dispatch never counts for a PS), last event 13',
              item['events'] == [10, 13] and item['last_event'] == 13)
        rec_flags = {m['orig_shader_id']: m['recompiled'] for m in item['excluded_modules']}
        check('plan: cache-linked modules no A reproduces are EXCLUDED, flagged recompiled / never recompiled',
              rec_flags == {'ResourceId::2': True, 'ResourceId::3': False}
              and item['excluded_not_recompiled'] == ['ResourceId::3'] and item['excluded_events'] == [11, 12], rec_flags)
        v = plan['validation'][paths['V2']]
        check('plan: V-f deciding command carries --uniform-buffer-standard-layout; 102 pred/01 command reported',
              v['ubsl']['ok'] is True and '--uniform-buffer-standard-layout' in v['ubsl']['cmd']
              and '--uniform-buffer-standard-layout' not in v['pred01']['cmd'], v)
        check('plan: all three seal hashes recorded (pred = the M5\' seal)', S.plan_seal_problems(plan) == []
              and plan['pred_sha256'] == S.PRED_SHA)
        check('plan: the recompile inputs are recorded; a temporary cache dir is named as an input problem',
              plan['recompile_exe_sha256'] == S.EXE_SHA and plan['recompile_cache_dir'] == S.SNAPSHOT_DIR
              and plan['recompile_signature'] == S.SIGNATURE_PREFIX
              and len(plan['input_problems']) == 1 and 'cache link dir' in plan['input_problems'][0]
              and S.input_problems(dict(plan, cache_dir=S.SNAPSHOT_DIR)) == [], plan['input_problems'])
        check('plan: the default --cache-dir is the snapshot', P.DEFAULT_CACHE == S.SNAPSHOT_DIR
              and P.DEFAULT_RECOMPILE.endswith('/m5p/recompile.json'))
        code = P.main(base_args + ['--out', str(out), '--cache-dir', str(cache_dir)])
        check('plan: never overwrites --out', code == 2)
        for which, source in (('pred', S.PRED), ('parent01', S.PARENT01), ('parent02', S.PARENT02)):
            bad = tmp / ('%s_bad.md' % which)
            shutil.copy(source, bad)
            with open(bad, 'ab') as stream:
                stream.write(b'\n')
            target = tmp / ('plan_bad_%s.json' % which)
            code = P.main(base_args + ['--out', str(target), '--no-spirv-val', '--%s' % which, str(bad)])
            check('MUTATION seal: a changed %s is refused by the planner' % which, code == 2 and not target.exists())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if os.path.isfile(REAL_RECOMPILE):
        notes = []
        regs = P.load_side_table(P.DEFAULT_REGS, notes, 'regs.json')
        layout = P.load_side_table(P.DEFAULT_LAYOUT, notes, 'layout_check.json')
        items, header = P.load_recompile(REAL_RECOMPILE, notes, regs, layout)
        perms = [p for i in items.values() for p in i['perms']]
        check('real m5p/recompile.json: 10 items, 16 permutations, every A/V1/V2p module on disk',
              sorted(items) == sorted(n for n, _ in ITEMS) and len(perms) == 16
              and all(p.get(a) and p[a]['exists'] for p in perms for a in P.ARMS), (sorted(items), len(perms), notes))
        check('real m5p/recompile.json: built by the sealed exe from the snapshot (new s2)',
              header.get('exe_sha256') == S.EXE_SHA and S.norm_path(header.get('cache_dir')) == S.norm_path(S.SNAPSHOT_DIR)
              and str(header.get('signature')).startswith(S.SIGNATURE_PREFIX), header)
        if regs:
            s4 = items['S4']['perms'][0]
            check('real regs.json merged: V2p register count and LDG variants carried into the plan (reported only)',
                  s4['V2p'].get('register_count') is not None and isinstance(s4['V2p'].get('ldg_variants'), dict)
                  and s4['V2p'].get('layout_ok') is not None, s4['V2p'].get('ldg_variants'))
    else:
        print('SKIP  real m5p/recompile.json not built yet')


# ------------------------------------------------------------------ the qrenderdoc tools and the wrapper, statically
def test_tools():
    for name in ('m5p_103.py', 'rd_m5p_equal.py', 'rd_m5p_bench.py', 'rd_m5_find.py', 'm5_rdlib.py'):
        source = (HERE / name).read_text(encoding='utf-8')
        try:
            ast.parse(source, filename=name, feature_version=(3, 8))
            ok = True
        except SyntaxError as error:
            ok = error
        check('%s parses as Python 3.8 (qrenderdoc 1.46)' % name, ok is True, ok)
    equal_src = (HERE / 'rd_m5p_equal.py').read_text(encoding='utf-8')
    bench_src = (HERE / 'rd_m5p_bench.py').read_text(encoding='utf-8')
    run_src = (HERE / 'm5p_run.py').read_text(encoding='utf-8')
    check('rd_m5p_equal.py: three seals, plan seals, sealed variants, sealed capture; no session-102 scorer',
          'm5p_103.require_seals' in equal_src and 'm5p_103.plan_seal_problems' in equal_src
          and 'm5p_103.equal_variants' in equal_src and 'm5p_103.capture_sha_problem' in equal_src
          and 'import m5_102' not in equal_src and 'lib.require_seals' not in equal_src)
    check('rd_m5p_bench.py: three seals, sealed arm set / design, sealed capture, m5p_103.decide for the interim',
          'm5p_103.require_seals' in bench_src and 'm5p_103.bench_sequences' in bench_src
          and 'm5p_103.capture_sha_problem' in bench_src and 'm5p_103.decide(' in bench_src
          and 'm5p_103.rounds_after_time_rule' in bench_src and 'import m5_102' not in bench_src
          and 'lib.require_seals' not in bench_src)
    check("m5p_run.py: find -> rd_m5_find.py (unchanged), equal / bench -> the m5p tools, seals from m5p_103",
          "'find': ROOT / 'rd_m5_find.py'" in run_src and "'bench': ROOT / 'rd_m5p_bench.py'" in run_src
          and "'equal': ROOT / 'rd_m5p_equal.py'" in run_src and 'm5p_103.seal_hashes()' in run_src
          and "pred/01_m5_bench.md" not in run_src)
    find_src = (HERE / 'rd_m5_find.py').read_text(encoding='utf-8')
    check('rd_m5_find.py has no arm and no seal dependency (reused unchanged)',
          'require_seals' not in find_src and 'm5_102' not in find_src and 'V2' not in find_src)


def main():
    if not S.seals_ok():
        print('the sealed texts (M5\' seal + the two session-102 parents) do not match: tests refuse to run')
        return 2
    t0 = time.time()
    test_primitives()
    test_design()
    test_verdicts()
    test_ve()
    test_controls()
    test_predictions()
    test_cli()
    test_plan()
    test_tools()
    print()
    print('%d passed, %d failed%s  (%.0f s)' % (PASSES, len(FAILS), (': ' + ', '.join(FAILS)) if FAILS else '',
                                                time.time() - t0))
    return 1 if FAILS else 0


if __name__ == '__main__':
    raise SystemExit(main())
