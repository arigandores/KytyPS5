"""Session 103, M5' scorer, sealed to pred/02_m5p_bench.md (sha256 4035a9b0...) - the DECISIVE seal -
which inherits V-a..V-g, the estimator and the shader set from session 102's pred/01_m5_bench.md
(sha256 cf3c353f...) as amended by pred/02_m5_addendum.md (sha256 ced6d410...) s1, s2, s5.  All three
hashes are verified before anything is scored; any one changed => refusal.

    python C:/kyty/s103/m5p_103.py --plan <plan.json> --bench <bench.json> --equal <equal.json> \
        --capture-log <log_m5cap102b.txt> --out <m5p_103.json>

Derived from m5_102.py by copying and minimal editing (the proven logic is unchanged unless listed
in "Differences from m5_102" below).  Offline only: it never launches the game, never runs RenderDoc,
never re-runs a bench and never overwrites an output.  It is also imported by the qrenderdoc tools
(rd_m5p_equal.py, rd_m5p_bench.py), so it stays Python 3.8 (RenderDoc 1.46's embedded interpreter).

  new s0      X' = median_r S[V2p,r]/S[A,r] over the items that pass V-e for V2p (V2p = "V2'" of the
              seal).  CI_lo(X'-1) > 0.06 => CLOSED (G CLOSED); CI_hi(X'-1) <= 0.06 => PASSES (G's GPU
              side PASSES); overlap => INCONCLUSIVE => ONE extension of 20 rounds, then the POINT over
              all rounds decides (X'-1 > 0.06 => CLOSED, else PASSES), published as "decided at the
              point after extension".  V2p V-e failures carrying more than 40 % of the valid A-arm time
              => M5' NOT DECIDED.
  new s2      arms B, A, V1, V2p (B = the capture's modules, A = KYTY_RECOMPILE no switch, V1 =
              KYTY_RECOMPILE_CBANK=0, V2p = KYTY_RECOMPILE_BDA=1 KYTY_BDA_LEAN=1); the set S1-S10 of
              102 pred/01 s2 unchanged; capture sha256 92a10b3c...; cache snapshot
              C:/kyty/cache_snap/PPSA21564_2db9065a (signature KytySC3:2db9065a); test recompiler
              sha256 e7a15418....
  new s3      V-a..V-g of 102 pred/01 s6 as amended by 102 pred/02 s1, s2, s5, applied to V1 and V2p:
              V-a capture, V-b coverage (>= 7 of 10 items, >= 60 % of 4 508 us), V-c identity
              (exclusion <= 40 % of the present items' A time), V-d median_r S[A]/S[B] in [0.97, 1.03],
              V-e three A replays (repeatable => bit-equal to A1; else <= 2*E), V-f
              `spirv-val --target-env vulkan1.3 --uniform-buffer-standard-layout`, V-g completion.
  new s4      two warm-up fetches with B (discarded); R = 20; round r uses DESIGN[r mod 4], the Williams
              design for four arms [B A V1 V2p], [A V2p B V1], [V1 B V2p A], [V2p V1 A B] (five full
              cycles); extension +20 rounds, same design; the 10-minute fetch rule of 102 pred/01 s5
              (never below 8 rounds) unchanged.  90 % two-sided percentile bootstrap over rounds,
              20 000 resamples, SEED 103, the same resample indices for every statistic.  Reported
              always, never deciding: L = median_r S[V1]/S[A], A/B, every per-item ratio (B/A, V1/A,
              V2p/A), the V-e table, registers, local memory, SASS counts and LDG variants.
  new s5      P1' X'-1 in [0.00, +0.12]; P2' >= 8 present items pass V-e for V2p; P3' L-1 in
              [0.00, +0.05]; P4' X' < X of session 102 (1.4201) on the common items.

Conventions this file fixes because the seals do not spell them out (none of them can move the
verdict towards either branch; each one can only withhold a verdict) - inherited from m5_102:
  * "time" of an item for the V-c / V-e shares = median over the main rounds of its per-round A
    time (V-c: median over rounds of the per-round excluded share).
  * A round counts only when every benched arm was fetched in it.
  * The bootstrap: ONE generator random.Random(103); each of the 20 000 resamples draws R round
    indices with replacement (randrange) and applies the SAME indices to X', L and A/B; the interval
    ends are the 5th / 95th percentiles of the medians, linearly interpolated (numpy 'linear').
  * A missing equality record, a missing variant module, a failed variant build, a replacement not
    in effect, or an equality record not made with three A replays counts as a V-e FAIL of that item
    for that variant.
  * The 40 % rule is decisive for V2p only; the V1 failing share is reported.  If X' has NO item left
    (or a zero denominator in a round) the result is NOT EVALUABLE - no verdict on a missing statistic.
  * The 4-hour rule with whole cycles preferred: see rounds_after_time_rule (a cycle is now 4).

Differences from m5_102 (each can only withhold a verdict or is reporting only):
  * three seals instead of two; the plan must carry all three hashes (IDENTITY);
  * arms B A V1 V2p, one deciding statistic X' (Y, V2s gone), verdict CLOSED / PASSES;
  * V-a additionally requires the bench's capture sha256 to equal the sealed 92a10b3c... (new s2);
  * IDENTITY additionally requires the plan's recompile inputs to be the sealed ones (test recompiler
    sha256 e7a15418..., cache dir = the snapshot, signature prefix KytySC3:2db9065a) - new s2;
  * after the extension a missing value of ANY A-valid item's event fails V-g (m5_102 checked the
    deciding statistics' items only);
  * P1'-P4' replace P1-P4; P4' is computed on the items common to session 102's X (S2-S7, S9, S10)
    and this bench's X' (with the session-102 bench when that set is not the eight).
"""
import argparse
import hashlib
import json
import math
import os
import random
import re
import statistics
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = 'C:/kyty/s103'
PRED = ROOT + '/pred/02_m5p_bench.md'                 # the M5' seal (decisive)
PRED_SHA = '4035a9b0cc6ae89a671706a12731b3e0f21f29c2caa90763f61c0fab4b688a67'
PARENT01 = ROOT + '/prev102/pred/01_m5_bench.md'      # inherited: set, estimator, V-a..V-g
PARENT01_SHA = 'cf3c353f7aaa4a2a16d7b59a61461cf26bef11ddbfffd59206ae95a8b6b33e0a'
PARENT02 = ROOT + '/prev102/pred/02_m5_addendum.md'   # inherited: s1 (V-f), s2 (V-e), s5 (present)
PARENT02_SHA = 'ced6d4103c64b9e5b7c81a3a730cac6d2b04a08486f82cf43642b04a8701f4d3'
SEALS = (('pred', PRED, PRED_SHA), ('parent01', PARENT01, PARENT01_SHA), ('parent02', PARENT02, PARENT02_SHA))
PLAN_SEAL_KEYS = (('pred_sha256', PRED_SHA), ('parent01_sha256', PARENT01_SHA), ('parent02_sha256', PARENT02_SHA))

# new s2: the capture, the cache inputs and the test recompiler
CAPTURE_SHA = '92a10b3cad28064e8b16d08dad074758be0627b66ac081dc2fd42f036dcf416d'
CAPTURE_NAME = 'kyty_1790110985179586_capture.rdc'
SNAPSHOT_DIR = 'C:/kyty/cache_snap/PPSA21564_2db9065a'
SNAPSHOT_MANIFEST = 'C:/kyty/cache_snap/manifest_2db9065a.json'
SIGNATURE_PREFIX = 'KytySC3:2db9065a'
EXE = 'C:/kyty/build/shader_cfg_tests.exe'
EXE_SHA = 'e7a154187c09b74ed83c5276de80605eaade06845bcf2e9510bc5b3b605726c2'

WEIGHTS = {'S1': 1009.1, 'S2': 493.0, 'S3': 473.2, 'S4': 428.9, 'S5': 373.9,
           'S6': 373.5, 'S7': 361.4, 'S8': 359.1, 'S9': 349.9, 'S10': 286.0}
TOTAL_WEIGHT = 4508.0
THRESHOLD = 0.06
MIN_ITEMS = 7
MIN_WEIGHT_SHARE = 0.60
EXCLUSION_MAX = 0.40
NOISE_LO, NOISE_HI = 0.97, 1.03
EQUALITY_FAIL_MAX = 0.40
BOOT_N = 20000
BOOT_SEED = 103
CI_LEVEL = 0.90
ARMS = ('B', 'A', 'V1', 'V2p')
VARIANTS = ('V1', 'V2p')
DECIDING_VARIANT = 'V2p'
ROUNDS_SEALED = 20
ROUNDS_FLOOR = 8
EXT_ROUNDS = 20
A_REPLAYS = 3
REPLAY_PAIRS = ('A1-A2', 'A1-A3', 'A2-A3')
NOISE_FACTOR = 2
VF_DECIDING = ['--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout']
VF_PRED01 = ['--target-env', 'vulkan1.3']
# new s5: the four predictions (no decision weight)
P1_RANGE = (0.00, 0.12)
P2_MIN_PASS = 8
P3_RANGE = (0.00, 0.05)
P4_X102 = 1.4201                         # the sealed number (session 102: 1.420062635295889)
P4_X102_EXACT = 1.420062635295889
P4_ITEMS102 = ('S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S9', 'S10')   # session 102's X items (S1, S8 failed V-e)
PREV102_PLAN = 'C:/kyty/s102/m5/real/plan_m5cap102.json'
PREV102_BENCH = 'C:/kyty/s102/m5/real/bench_m5cap102.json'

# the statistics: name -> (numerator arm, denominator arm)
STATS = (('Xp', 'V2p', 'A'), ('L', 'V1', 'A'), ('A_over_B', 'A', 'B'))
DECIDING_STATS = ('Xp',)
LABEL = {'Xp': "X'", 'L': 'L', 'A_over_B': 'A/B'}

BRANCH = {
    'CLOSED': ("G CLOSED (CI_lo(X'-1) > 0.06): the BDA path as design G would build it costs more than +6 % "
               "on the top PS/CS items.  Not a statement about CPU, P, F or R1."),
    'PASSES': ("G's GPU side PASSES (X'-1 <= 0.06): the next decision becomes a slice prototype of G's CPU "
               "side.  Not a licence for G and nothing about 60 FPS; SRT chasing through BDA, run-time "
               "format decode, every VS/mesh stage and all of G's CPU side are unpriced; the run-time "
               "alignment test is inside the price."),
}


# ---------------------------------------------------------------- the sealed design and R
DESIGN = [('B', 'A', 'V1', 'V2p'), ('A', 'V2p', 'B', 'V1'), ('V1', 'B', 'V2p', 'A'), ('V2p', 'V1', 'A', 'B')]
CYCLE = len(DESIGN)


def design_for(arms):
    """The sealed design filtered to the arms actually benched (mechanics only use a subset)."""
    return [tuple(a for a in seq if a in arms) for seq in DESIGN]


def rounds_after_time_rule(requested, done, fit_total, floor=ROUNDS_FLOOR, cycle=CYCLE):
    """102 pred/01 s5 (unchanged by new s4): once a fetch took longer than 10 min, R drops to the
    largest value that fits a 4-hour bench (fit_total = rounds done + rounds that still fit), never
    below the floor of 8.  Whole cycles (4 rounds) are preferred: a value >= one cycle is rounded DOWN
    to a whole number of cycles (the floor 8 is two cycles).  Rounds already measured are never
    discarded, and R never rises above the request (a mechanics request below 8 stays as requested)."""
    candidate = max(floor, int(fit_total))
    if candidate >= cycle:
        candidate = cycle * (candidate // cycle)
    candidate = max(candidate, int(done))
    return min(int(requested), candidate)


def bench_sequences(arm_names, mechanics, plan_sequences=None):
    """The sequences a bench must use (rd_m5p_bench.py).  Raises ValueError on a plan that overrides
    the design, on an arm outside the sealed set, or - unless mechanics - on any arm set other than
    exactly B, A, V1, V2p."""
    if plan_sequences:
        raise ValueError('a plan may not override the sealed design (new s4)')
    arm_names = list(arm_names)
    unknown = [a for a in arm_names if a not in ARMS]
    if unknown:
        raise ValueError('arms %s are not in the sealed design %s' % (unknown, list(ARMS)))
    if len(set(arm_names)) != len(arm_names):
        raise ValueError('an arm is listed twice: %s' % arm_names)
    if not mechanics and sorted(arm_names) != sorted(ARMS):
        raise ValueError('the sealed bench measures exactly the arms %s, not %s (new s2)' % (list(ARMS), arm_names))
    seqs = design_for(arm_names)
    for seq in seqs:
        if sorted(seq) != sorted(arm_names):
            raise ValueError('design sequence %s does not contain every arm %s exactly once' % (seq, arm_names))
    return seqs


def equal_variants(requested, mechanics):
    """The variants rd_m5p_equal.py compares with A.  Unless mechanics: exactly V1 and V2p (new s3)."""
    requested = [v for v in requested if v]
    unknown = [v for v in requested if v not in VARIANTS]
    if unknown:
        raise ValueError('variants %s are not in the sealed set %s' % (unknown, list(VARIANTS)))
    if not mechanics and sorted(requested) != sorted(VARIANTS):
        raise ValueError('the sealed equality compares exactly %s with A, not %s' % (list(VARIANTS), requested))
    return requested


def capture_sha_problem(sha, mechanics):
    """None, or why a capture sha256 is not the sealed one (new s2).  A mechanics plan may use any."""
    if mechanics:
        return None
    if not sha:
        return 'the capture sha256 was not computed (RD_SHA=0 is for mechanics plans only)'
    if sha != CAPTURE_SHA:
        return 'capture sha256 %s != sealed %s' % (sha, CAPTURE_SHA)
    return None


def plan_seal_problems(plan):
    """Every sealed hash the plan does not carry (the plan must be made under all three seals)."""
    return ['plan %s = %s, sealed %s' % (key, plan.get(key), want)
            for key, want in PLAN_SEAL_KEYS if plan.get(key) != want]


def norm_path(path):
    return str(path or '').replace('\\', '/').rstrip('/').lower()


def input_problems(plan):
    """new s2: the recompile inputs the plan records must be the sealed ones."""
    problems = []
    if plan.get('recompile_exe_sha256') != EXE_SHA:
        problems.append('test recompiler sha256 %s != sealed %s' % (plan.get('recompile_exe_sha256'), EXE_SHA))
    if norm_path(plan.get('recompile_cache_dir')) != norm_path(SNAPSHOT_DIR):
        problems.append('recompile cache dir %s != the snapshot %s' % (plan.get('recompile_cache_dir'), SNAPSHOT_DIR))
    if norm_path(plan.get('cache_dir')) != norm_path(SNAPSHOT_DIR):
        problems.append('plan cache link dir %s != the snapshot %s' % (plan.get('cache_dir'), SNAPSHOT_DIR))
    if not str(plan.get('signature_prefix') or '').startswith(SIGNATURE_PREFIX):
        problems.append('signature prefix %s != %s' % (plan.get('signature_prefix'), SIGNATURE_PREFIX))
    if not str(plan.get('recompile_signature') or '').startswith(SIGNATURE_PREFIX):
        problems.append('recompile signature %s != %s' % (plan.get('recompile_signature'), SIGNATURE_PREFIX))
    return problems


# ---------------------------------------------------------------- seals
def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seal_ok(path, want):
    try:
        return sha256_file(path) == want
    except OSError:
        return False


def seals_ok(pred=PRED, parent01=PARENT01, parent02=PARENT02):
    """All three sealed texts byte-for-byte: the M5' seal and its two session-102 parents."""
    return seal_ok(pred, PRED_SHA) and seal_ok(parent01, PARENT01_SHA) and seal_ok(parent02, PARENT02_SHA)


def _sha_or_none(path):
    try:
        return sha256_file(path)
    except OSError:
        return None


def seal_hashes():
    """sha256 of the three sealed texts, recorded by every tool."""
    return dict((name, dict(path=path, sha256=_sha_or_none(path), want=want)) for name, path, want in SEALS)


def require_seals(log=None):
    """Refuse to run unless all three sealed texts are byte-for-byte the sealed ones (rd tools)."""
    seals = seal_hashes()
    for name, row in seals.items():
        if row['sha256'] != row['want']:
            raise SystemExit('SEALED TEXT CHANGED (%s %s: %s != %s): refusing to run'
                             % (name, row['path'], row['sha256'], row['want']))
    if log is not None:
        log('seals verified: %s' % ', '.join('%s %s' % (k, v['sha256'][:12]) for k, v in seals.items()))
    return seals


# ---------------------------------------------------------------- statistics
def quantile(sorted_values, q):
    """numpy.percentile(..., method='linear') on an already sorted list."""
    n = len(sorted_values)
    if n == 0:
        return None
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_values[lo]
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo)


def joint_bootstrap_ci(series, n_boot=BOOT_N, seed=BOOT_SEED, level=CI_LEVEL):
    """Percentile bootstrap of the median over rounds for several statistics at once, with the SAME
    resample indices for all of them (new s4).  series: {name: [value per round]}, every list over
    the same rounds in the same order.  Returns {name: (lo, hi)}."""
    names = [k for k, v in series.items() if v]
    if not names:
        return {}
    lengths = {len(series[k]) for k in names}
    if len(lengths) != 1:
        raise ValueError('joint bootstrap needs every series over the same rounds: %s' % sorted(lengths))
    n = lengths.pop()
    rng = random.Random(seed)
    meds = {k: [] for k in names}
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        for k in names:
            values = series[k]
            meds[k].append(statistics.median([values[i] for i in idx]))
    tail = (1.0 - level) / 2.0
    out = {}
    for k in names:
        meds[k].sort()
        out[k] = (quantile(meds[k], tail), quantile(meds[k], 1.0 - tail))
    return out


def bootstrap_median_ci(values, n_boot=BOOT_N, seed=BOOT_SEED, level=CI_LEVEL):
    """One statistic alone: identical to joint_bootstrap_ci with a single series."""
    if not values:
        return None, None
    return joint_bootstrap_ci({'v': list(values)}, n_boot, seed, level)['v']


def classify_interval(stats):
    """new s0 on the 90 % interval of X'-1.  stats['Xp']['ci_minus1'] = [lo, hi]."""
    lo, hi = stats['Xp']['ci_minus1']
    if lo > THRESHOLD:
        return 'CLOSED'
    if hi <= THRESHOLD:
        return 'PASSES'
    return 'INCONCLUSIVE'


def classify_points(xp):
    """new s0 after the extension: the point over all rounds decides."""
    return 'CLOSED' if xp - 1.0 > THRESHOLD else 'PASSES'


# ---------------------------------------------------------------- V-e (102 pred/02 s2)
def ve_judge(pairs, n_diff, bit_equal):
    """The amended V-e for one item and one variant.

    pairs    {'A1-A2', 'A1-A3', 'A2-A3'} -> differing bytes between two A replays over the SAME
             outputs the variant is compared on
    n_diff   differing bytes of the variant against A1
    bit_equal the tool's own byte-for-byte equality of the variant and A1
    """
    if not isinstance(pairs, dict) or sorted(pairs) != sorted(REPLAY_PAIRS) or any(
            isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in pairs.values()):
        return {'pass': False, 'kind': None, 'E': None, 'limit': None, 'repeatable': None,
                'reason': 'arm A not replayed three times (102 pred/02 s2)'}
    if isinstance(n_diff, bool) or not isinstance(n_diff, int) or n_diff < 0:
        return {'pass': False, 'kind': None, 'E': None, 'limit': None, 'repeatable': None,
                'reason': 'no differing-byte count for the variant'}
    e = max(pairs.values())
    if e == 0:
        ok = n_diff == 0 and bit_equal is True
        return {'pass': ok, 'kind': 'bit-equal' if ok else None, 'E': 0, 'limit': 0, 'repeatable': True,
                'reason': None if ok else 'repeatable item, outputs differ from A1 (%d bytes)' % n_diff}
    limit = NOISE_FACTOR * e
    ok = n_diff <= limit
    return {'pass': ok, 'kind': 'within replay noise' if ok else None, 'E': e, 'limit': limit,
            'repeatable': False,
            'reason': None if ok else 'replay-nondeterministic item, %d differing bytes > 2*E = %d' % (n_diff, limit)}


def judge_item_variant(equal, item_name, arm):
    """V-e of one item for one variant from an rd_m5p_equal.py record (never trusts its 'pass')."""
    if equal is None:
        return {'pass': False, 'reason': 'no equality file'}
    if equal.get('reference', 'A') != 'A':
        return {'pass': False, 'reason': 'equality reference is %s, not arm A' % equal.get('reference')}
    record = (equal.get('items') or {}).get(item_name)
    if record is None:
        return {'pass': False, 'reason': 'no equality record'}
    if record.get('error'):
        return {'pass': False, 'reason': 'equality error: %s' % record['error']}
    if record.get('reference_replays') != A_REPLAYS:
        return {'pass': False, 'reason': 'arm A replayed %s times, 102 pred/02 s2 needs %d'
                % (record.get('reference_replays'), A_REPLAYS)}
    var = (record.get('variants') or {}).get(arm)
    if var is None:
        return {'pass': False, 'reason': 'no equality record for %s' % arm}
    if var.get('error'):
        return {'pass': False, 'reason': 'equality error: %s' % var['error']}
    verdict = ve_judge(var.get('reference_pair_diff_bytes'), var.get('n_diff_bytes'), var.get('equal'))
    verdict = dict(verdict)
    verdict['n_diff_bytes'] = var.get('n_diff_bytes')
    if var.get('pass') is not None and bool(var.get('pass')) != verdict['pass']:
        verdict['tool_disagrees'] = var.get('pass')
    return verdict


# ---------------------------------------------------------------- bench tables
def rounds_of(bench, phases):
    """{round: {arm: fetch}} for the complete rounds of the given phases."""
    arms = bench.get('arms') or list(ARMS)
    table = {}
    for fetch in bench.get('fetches', []):
        if fetch.get('phase') in phases:
            table.setdefault(fetch['round'], {})[fetch['arm']] = fetch
    return dict((r, row) for r, row in sorted(table.items()) if all(a in row for a in arms))


def item_times(bench, events, rounds):
    """T[arm][round] summed over events; (table, missing) where missing lists None values."""
    index = {e: i for i, e in enumerate(bench['events'])}
    table = {}
    missing = []
    for r, row in rounds.items():
        for arm, fetch in row.items():
            total = 0.0
            for e in events:
                i = index.get(e)
                value = fetch['d'][i] if i is not None else None
                if value is None:
                    missing.append((arm, r, e))
                    continue
                total += value
            table.setdefault(arm, {})[r] = total
    return table, missing


def module_build_failures(bench):
    """{(arm, item)} whose module failed to build."""
    return {(row.get('arm'), row.get('item')) for row in bench.get('build_errors', [])}


def design_violations(bench, rounds, mechanics):
    """Rounds whose fetch order is not DESIGN[r mod 4] (filtered to the benched arms), or whose
    recorded sequence index is wrong or (for a real bench) missing."""
    arms = bench.get('arms') or list(ARMS)
    expected = design_for(arms)
    bad = []
    for r, row in rounds.items():
        order = tuple(f['arm'] for f in sorted(row.values(), key=lambda f: f.get('pos', 0)))
        want = expected[r % len(expected)]
        seq_idx = {f.get('seq_index') for f in row.values()}
        if order != want:
            bad.append(dict(round=r, order=list(order), expected=list(want)))
        elif seq_idx == {None}:
            if not mechanics:
                bad.append(dict(round=r, error='sequence index not recorded'))
        elif seq_idx != {r % len(expected)}:
            bad.append(dict(round=r, error='recorded sequence index %s != %d' % (sorted(seq_idx, key=str), r % len(expected))))
    return bad


def ratio_median(bench, plan_items, items, num, den, rounds):
    """median over the given rounds of sum_items T[num]/sum_items T[den] (None if unavailable)."""
    if not items or not rounds:
        return None
    tables = {}
    for n in items:
        tables[n], miss = item_times(bench, plan_items[n]['events'], rounds)
        if miss:
            return None
    values = []
    for r in sorted(rounds):
        d = sum(tables[n].get(den, {}).get(r, 0.0) for n in items)
        if d <= 0:
            return None
        values.append(sum(tables[n].get(num, {}).get(r, 0.0) for n in items) / d)
    return statistics.median(values)


# ---------------------------------------------------------------- the decision
def decide(plan, bench, equal, final=True, capture_check=None, mechanics=False, prev102=None):
    """The whole sealed computation.  Pure function of its inputs (no I/O).
    prev102: None or {'plan': ..., 'bench': ...} of session 102 (P4' only, no decision weight)."""
    result = dict(controls={}, notes=[], items={}, statistics={}, per_item={}, predictions={})
    controls = result['controls']
    notes = result['notes']
    names = [n for n in plan['items'] if mechanics or n in WEIGHTS]
    weights = {n: (WEIGHTS.get(n, plan['items'][n].get('weight', 0.0) or 0.0)) for n in names}
    benched = list(bench.get('arms') or ARMS)

    # ---- rounds ----
    main_rounds = rounds_of(bench, ('main',))
    ext_rounds = rounds_of(bench, ('extension',))
    result['rounds_main'] = len(main_rounds)
    result['rounds_extension'] = len(ext_rounds)
    rounds_required = bench.get('rounds_requested', ROUNDS_SEALED)
    for decision in bench.get('decisions', []):
        if decision.get('kind') == 'rounds_drop':
            rounds_required = decision['rounds_after']
    result['rounds_required'] = rounds_required

    builds_failed = module_build_failures(bench)
    # present = in the capture (arm-A md5 or translation-cache link, m5p_plan.py, 102 pred/02 s5);
    # only the modules linked by arm A's md5 are summed - a present item without one is wholly excluded.
    present = [n for n in names if plan['items'][n].get('present')]

    # ---- per item tables ----
    T = {}
    Tx = {}
    missing_all = {}
    for n in present:
        item = plan['items'][n]
        T[n], miss = item_times(bench, item['events'], main_rounds)
        Tx[n], miss_x = item_times(bench, item.get('excluded_events', []), main_rounds)
        missing_all[n] = miss + miss_x
    rounds = sorted(main_rounds)

    a_valid = []
    for n in present:
        item = plan['items'][n]
        reasons = []
        if not item.get('modules'):
            reasons.append('no module reproduced by arm A (wholly excluded, V-c)')
        elif not item.get('events'):
            reasons.append('no events')
        if item.get('arm_missing', {}).get('A'):
            reasons.append('arm A module missing for perms %s' % item['arm_missing']['A'])
        if ('A', n) in builds_failed:
            reasons.append('arm A build failed')
        if missing_all[n]:
            reasons.append('%d missing values' % len(missing_all[n]))
        result['items'][n] = dict(weight=weights[n], present=True, included=bool(item.get('modules')),
                                  a_valid=not reasons, a_invalid_reasons=reasons,
                                  modules=len(item['modules']), excluded_modules=len(item.get('excluded_modules', [])),
                                  events=len(item['events']), excluded_events=len(item.get('excluded_events', [])))
        if not reasons:
            a_valid.append(n)
    for n in names:
        if n not in result['items']:
            result['items'][n] = dict(weight=weights[n], present=False)

    def median_over_rounds(arm, n):
        values = [T[n][arm][r] for r in rounds if arm in T[n] and r in T[n][arm]]
        return statistics.median(values) if values else None

    a_time = {n: (median_over_rounds('A', n) or 0.0) if rounds else 0.0 for n in present}

    # ---- V-a capture ----
    va = dict(capture_sha256_bench=bench.get('capture_sha256'), capture_sha256_plan=plan.get('capture_sha256'),
              capture_sha256_sealed=CAPTURE_SHA)
    va['sha_match'] = bool(va['capture_sha256_bench']) and va['capture_sha256_bench'] == va['capture_sha256_plan']
    va['sha_sealed'] = va['capture_sha256_bench'] == CAPTURE_SHA
    va['items_with_module'] = len(present)
    if capture_check is None:
        va['log_checked'] = False
        va['pass'] = None
    else:
        va['log_checked'] = True
        va.update(capture_check)
        va['pass'] = bool(va['sha_match'] and (va['sha_sealed'] or mechanics) and capture_check.get('dma_layout')
                          and capture_check.get('clock_pin') and len(present) >= MIN_ITEMS)
    controls['V-a'] = va

    # ---- V-b coverage ----
    w_present = sum(weights[n] for n in present)
    vb = dict(present=len(present), of=len(names), weight_present=round(w_present, 3),
              weight_share=w_present / TOTAL_WEIGHT if not mechanics else None,
              absent=[n for n in names if n not in present])
    vb['pass'] = (len(present) >= MIN_ITEMS and w_present / TOTAL_WEIGHT >= MIN_WEIGHT_SHARE) if not mechanics else True
    controls['V-b'] = vb

    # ---- V-c identity ----
    shares = []
    for r in rounds:
        excl = sum(Tx[n].get('A', {}).get(r, 0.0) for n in present)
        tot = sum(T[n].get('A', {}).get(r, 0.0) + Tx[n].get('A', {}).get(r, 0.0) for n in present)
        if tot > 0:
            shares.append(excl / tot)
    vc = dict(excluded_share=statistics.median(shares) if shares else None,
              excluded_modules={n: len(plan['items'][n].get('excluded_modules', [])) for n in present},
              cache_link_used=bool(plan.get('cache_link_used')))
    if not plan.get('cache_link_used'):
        notes.append('V-c: the plan had no translation-cache link, so an excluded module could not be '
                     'identified; the excluded share is a lower bound')
    vc['pass'] = vc['excluded_share'] is not None and vc['excluded_share'] <= EXCLUSION_MAX
    controls['V-c'] = vc

    # ---- V-d mechanism noise ----
    def S(arm, items, r):
        return sum(T[n][arm][r] for n in items)

    ratio_ab = [S('A', a_valid, r) / S('B', a_valid, r) for r in rounds
                if a_valid and S('B', a_valid, r) > 0] if 'B' in benched else []
    vd = dict(median_A_over_B=statistics.median(ratio_ab) if ratio_ab else None, band=[NOISE_LO, NOISE_HI])
    vd['pass'] = vd['median_A_over_B'] is not None and NOISE_LO <= vd['median_A_over_B'] <= NOISE_HI
    controls['V-d'] = vd

    # ---- V-e output equality (102 pred/02 s2) ----
    variant_valid = {}
    ve = dict(evaluated=equal is not None, rule='102 pred/02 s2: three A replays; repeatable => bit-equal to A1; '
                                               'otherwise differing bytes vs A1 <= 2*E', judged={})
    total_a = sum(a_time[n] for n in a_valid) if a_valid else 0.0
    for arm in VARIANTS:
        failing = []
        reasons = {}
        noise = []
        judged = {}
        for n in a_valid:
            item = plan['items'][n]
            why = None
            if item.get('arm_missing', {}).get(arm):
                why = 'variant module missing for perms %s' % item['arm_missing'][arm]
            elif (arm, n) in builds_failed:
                why = 'variant build failed'
            else:
                verdict = judge_item_variant(equal, n, arm)
                judged[n] = verdict
                if not verdict['pass']:
                    why = verdict['reason']
                elif verdict.get('kind') == 'within replay noise':
                    noise.append(n)
                if verdict.get('tool_disagrees') is not None:
                    notes.append('V-e %s %s: the equality tool said pass=%s, the scorer judges %s'
                                 % (n, arm, verdict['tool_disagrees'], verdict['pass']))
            if why:
                failing.append(n)
                reasons[n] = why
        share = sum(a_time[n] for n in failing) / total_a if total_a > 0 else None
        variant_valid[arm] = [n for n in a_valid if n not in failing]
        ve[arm] = {'failing': failing, 'reasons': reasons, 'failing_share': share,
                   'passing': len(variant_valid[arm]), 'within_replay_noise': noise,
                   'deciding': arm == DECIDING_VARIANT,
                   'share_within_40pct': share is not None and share <= EQUALITY_FAIL_MAX}
        ve['judged'][arm] = judged
        if arm != DECIDING_VARIANT and share is not None and share > EQUALITY_FAIL_MAX:
            notes.append('V-e: %s fails for %.1f %% of the valid A-arm time (reported; the 40 %% rule decides '
                         'for V2p only)' % (arm, 100.0 * share))
    ve['pass'] = (ve[DECIDING_VARIANT]['share_within_40pct']) if (equal is not None or not a_valid) else None
    ve['nondeterministic_reference'] = sorted({n for arm in VARIANTS for n, v in ve['judged'][arm].items()
                                               if v.get('repeatable') is False}, key=names.index)
    ve['E'] = {n: max([v.get('E') for arm in VARIANTS for m, v in ve['judged'][arm].items()
                       if m == n and v.get('E') is not None] or [None]) for n in a_valid}
    if any(ve[arm]['within_replay_noise'] for arm in VARIANTS):
        notes.append('V-e: passing WITHIN REPLAY NOISE (never "equal"): %s'
                     % '; '.join('%s %s' % (arm, ', '.join(ve[arm]['within_replay_noise']))
                                 for arm in VARIANTS if ve[arm]['within_replay_noise']))
    controls['V-e'] = ve

    # ---- V-f spirv-val (102 pred/02 s1) ----
    validation = plan.get('validation', {})
    paths = sorted({rep['spv_path'] for arm in plan['arms'] if arm['name'] in benched for rep in arm['replacements']})
    bad = [p for p in paths if not validation.get(p, {}).get('ubsl', {}).get('ok')]
    bad_pred01 = [p for p in paths if not (validation.get(p, {}).get('pred01')
                                            or validation.get(p, {}).get('sealed') or {}).get('ok')]
    vf = {'command': 'spirv-val %s <spv>' % ' '.join(VF_DECIDING), 'modules': len(paths), 'failing': bad,
          'failing_pred01_command_reported': len(bad_pred01), 'pass': not bad and bool(paths)}
    controls['V-f'] = vf

    # ---- V-g technical completion ----
    vg = dict(complete=bool(bench.get('complete')) or not final, rounds_main=len(main_rounds),
              rounds_required=rounds_required, rounds_requested=bench.get('rounds_requested'),
              build_errors=len(bench.get('build_errors', [])),
              missing_values=sum(len(missing_all[n]) for n in present))
    reasons = []
    if final and not bench.get('complete'):
        reasons.append('bench not complete')
    if len(main_rounds) < rounds_required:
        reasons.append('%d main rounds < %d required' % (len(main_rounds), rounds_required))
    if not mechanics and bench.get('rounds_requested') != ROUNDS_SEALED:
        reasons.append('rounds requested %s != sealed %d' % (bench.get('rounds_requested'), ROUNDS_SEALED))
    if rounds_required < min(ROUNDS_FLOOR, bench.get('rounds_requested') or ROUNDS_FLOOR):
        reasons.append('rounds dropped below %d' % ROUNDS_FLOOR)
    if vg['build_errors']:
        reasons.append('%d module builds failed' % vg['build_errors'])
    if any(missing_all[n] for n in present):
        reasons.append('a fetch returned no value for an event of an item')
    if bench.get('replacement_check_ok') is not True:
        reasons.append('replacements not shown to be in effect (replacement_check_ok=%s)'
                       % bench.get('replacement_check_ok'))
    if not mechanics and set(benched) != set(ARMS):
        reasons.append('benched arms %s != sealed %s' % (benched, list(ARMS)))
    violations = design_violations(bench, dict(list(main_rounds.items()) + list(ext_rounds.items())), mechanics)
    vg['design_violations'] = violations[:20]
    if violations:
        reasons.append('%d rounds not in the sealed order (new s4)' % len(violations))
    vg['reasons'] = reasons
    vg['pass'] = not reasons
    controls['V-g'] = vg

    # ---- X' (+ L, A/B reported), same resample indices ----
    stat_items = {'Xp': variant_valid[DECIDING_VARIANT],
                  'L': variant_valid['V1'],
                  'A_over_B': a_valid}
    series = {}
    stats = {}
    for name, num, den in STATS:
        items = stat_items[name]
        row = dict(label=LABEL[name], numerator=num, denominator=den, items=items, n_rounds=0,
                   deciding=name in DECIDING_STATS)
        if num not in benched or den not in benched:
            row['unavailable'] = 'arm %s not benched' % (num if num not in benched else den)
        elif not items:
            row['unavailable'] = 'no item left for this ratio (V-e)'
        elif not rounds:
            row['unavailable'] = 'no complete round'
        else:
            dens = [S(den, items, r) for r in rounds]
            if any(d <= 0 for d in dens):
                row['unavailable'] = 'zero denominator in a round'
            else:
                values = [S(num, items, r) / d for r, d in zip(rounds, dens)]
                series[name] = values
                row.update(n_rounds=len(values), ratios=values, point=statistics.median(values))
                row['minus1'] = row['point'] - 1.0
        stats[name] = row
    cis = joint_bootstrap_ci(series) if series else {}
    for name, (lo, hi) in cis.items():
        stats[name]['ci'] = [lo, hi]
        stats[name]['ci_minus1'] = [lo - 1.0, hi - 1.0]
    result['statistics'] = stats
    result['bootstrap'] = dict(resamples=BOOT_N, seed=BOOT_SEED, level=CI_LEVEL, same_indices=sorted(series),
                               rounds=rounds)

    # ---- per item: every arm against A ----
    per_item = {}
    for n in a_valid:
        row = {}
        for num, den in (('B', 'A'), ('V1', 'A'), ('V2p', 'A')):
            if num not in benched or den not in benched:
                continue
            values = [T[n][num][r] / T[n][den][r] for r in rounds if T[n][den][r] > 0]
            row['%s/%s' % (num, den)] = statistics.median(values) if values else None
        row['A_us_median'] = a_time[n]
        row['B_us_median'] = median_over_rounds('B', n) if 'B' in benched else None
        row['V-e'] = dict((arm, ('pass' if n in variant_valid[arm] else 'FAIL') +
                           (' (within replay noise)' if n in ve[arm]['within_replay_noise'] else ''))
                          for arm in VARIANTS)
        per_item[n] = row
    result['per_item'] = per_item

    # ---- validity and verdict ----
    deciding = ['V-a', 'V-b', 'V-c', 'V-d', 'V-e', 'V-f', 'V-g']
    failed = [c for c in deciding if controls[c].get('pass') is False]
    unevaluated = [c for c in deciding if controls[c].get('pass') is None]
    missing_stats = [s for s in DECIDING_STATS if 'ci_minus1' not in stats[s]]
    result['failed_controls'] = failed
    result['unevaluated_controls'] = unevaluated
    statistical = classify_interval(stats) if not missing_stats else None
    result['statistical_classification'] = statistical
    verdict = None
    decided_at = None
    valid_for_verdict = False
    if failed == ['V-e']:
        status = "M5' NOT DECIDED (V2p fails V-e for more than 40 % of the valid A-arm time)"
    elif failed:
        status = 'INVALID'
    elif unevaluated and not (not final and unevaluated == ['V-a']):
        status = 'NOT EVALUABLE (%s not evaluated)' % ', '.join(unevaluated)
    elif missing_stats:
        status = 'NOT EVALUABLE (%s)' % '; '.join('%s: %s' % (LABEL[s], stats[s].get('unavailable')) for s in missing_stats)
    else:
        status = 'VALID'
        valid_for_verdict = True
        verdict = statistical
        decided_at = 'intervals over the %d main rounds' % len(rounds)
        if statistical == 'INCONCLUSIVE' and final:
            if len(ext_rounds) >= EXT_ROUNDS:
                all_rounds = {}
                all_rounds.update(main_rounds)
                all_rounds.update(ext_rounds)
                ext_missing = []
                for n in a_valid:     # V-g: every fetch returns a value for every event of every valid item
                    _, miss = item_times(bench, plan['items'][n]['events'], all_rounds)
                    ext_missing += miss
                points = {}
                for name, num, den in STATS:
                    if name in series:
                        points[name] = ratio_median(bench, plan['items'], stat_items[name], num, den, all_rounds)
                result['extension'] = dict(n_rounds=len(all_rounds), points=points,
                                           minus1=dict((k, (v - 1.0) if v is not None else None)
                                                       for k, v in points.items()),
                                           deciding=list(DECIDING_STATS), missing_values=len(ext_missing))
                if ext_missing or points.get('Xp') is None:
                    status = 'INVALID'
                    failed.append('V-g (extension missing values)')
                    verdict = None
                else:
                    verdict = classify_points(points['Xp'])
                    decided_at = 'decided at the point after extension (%d rounds)' % len(all_rounds)
            else:
                verdict = 'INCONCLUSIVE'
                status = 'EXTENSION REQUIRED (%d of %d extension rounds present)' % (len(ext_rounds), EXT_ROUNDS)
    result['status'] = status
    result['verdict'] = verdict
    result['decided_at'] = decided_at
    result['branch'] = BRANCH.get(verdict)
    # The one extension is owed when a valid bench is INCONCLUSIVE and has not had it.
    result['extend'] = bool(valid_for_verdict and statistical == 'INCONCLUSIVE' and len(ext_rounds) < EXT_ROUNDS)

    # ---- predictions (no decision weight) ----
    def within(value, bounds):
        return None if value is None else (bounds[0] <= value <= bounds[1])

    p = result['predictions']
    xp_m1 = stats['Xp'].get('minus1')
    l_m1 = stats['L'].get('minus1')
    p['P1'] = dict(text="X' - 1 in [0.00, +0.12]", value=xp_m1, hit=within(xp_m1, P1_RANGE))
    passing = len([n for n in present if n in variant_valid[DECIDING_VARIANT]])
    p['P2'] = dict(text='at least 8 of the present items pass V-e for V2p', value=passing,
                   hit=passing >= P2_MIN_PASS if equal is not None else None)
    p['P3'] = dict(text='L - 1 in [0.00, +0.05]', value=l_m1, hit=within(l_m1, P3_RANGE))
    p['P4'] = prediction_p4(bench, plan, stat_items['Xp'], main_rounds, prev102)
    result['module_stats'] = module_stats(plan, present)
    return result


def prediction_p4(bench, plan, xp_items, main_rounds, prev102):
    """P4': X' < X of session 102 (1.4201) on the common items.  Common = session 102's X items
    (S2-S7, S9, S10) that are also X' items here.  Both ratios are taken on the common items: X' from
    this bench's main rounds; X of 102 is the sealed 1.4201 when the common set is those eight,
    else it is recomputed from the session-102 plan and bench (prev102) over their main rounds."""
    common = [n for n in xp_items if n in P4_ITEMS102]
    value = dict(common_items=common, x102_items=list(P4_ITEMS102))
    value['xp_common'] = ratio_median(bench, plan['items'], common, 'V2p', 'A', main_rounds)
    if not common:
        return dict(text="X' < X of session 102 (1.4201) on the common items", value=value, hit=None)
    if sorted(common) == sorted(P4_ITEMS102):
        value['x102_common'] = P4_X102
        value['x102_source'] = 'sealed 1.4201 (session 102, the same eight items)'
    elif prev102 is not None:
        rounds102 = rounds_of(prev102['bench'], ('main',))
        value['x102_common'] = ratio_median(prev102['bench'], prev102['plan']['items'], common, 'V2', 'A', rounds102)
        value['x102_source'] = 'recomputed from the session-102 bench on the common items'
    else:
        value['x102_common'] = None
        value['x102_source'] = 'common set differs from the eight and no session-102 bench was given'
    if prev102 is not None:
        rounds102 = rounds_of(prev102['bench'], ('main',))
        value['x102_eight_recomputed'] = ratio_median(prev102['bench'], prev102['plan']['items'],
                                                      list(P4_ITEMS102), 'V2', 'A', rounds102)
    hit = None
    if value['xp_common'] is not None and value.get('x102_common') is not None:
        hit = value['xp_common'] < value['x102_common']
    return dict(text="X' < X of session 102 (1.4201) on the common items", value=value, hit=hit)


def module_stats(plan, present):
    """Every extra field the plan carried per arm module (registers, SASS, LDG variants...): reported only."""
    out = {}
    for n in present:
        rows = []
        for module in plan['items'][n]['modules']:
            row = dict(perm=module['perm'], orig=module['orig_shader_id'])
            for arm in ('A', 'V1', 'V2p'):
                entry = module.get(arm) or {}
                row[arm] = dict((k, v) for k, v in entry.items() if k not in ('path', 'md5'))
            rows.append(row)
        out[n] = rows
    return out


# ---------------------------------------------------------------- capture log (V-a)
def check_capture_log(path):
    text = Path(path).read_bytes()
    return dict(log=str(path), log_sha256=hashlib.sha256(text).hexdigest(),
                dma_layout=re.search(rb'DmaLayout:\s*mode\s*1\b', text) is not None,
                clock_pin=re.search(rb'GpuClockPin:\s*mode\s*1\b', text) is not None)


# ---------------------------------------------------------------- report
def fmt(value, digits=4):
    if value is None:
        return '-'
    if isinstance(value, float):
        return ('%.' + str(digits) + 'f') % value
    return str(value)


def report(result, out=print):
    out("M5' scorer, sealed to %s (+ parents %s, %s)" % (PRED, PARENT01, PARENT02))
    out('status:  %s' % result['status'])
    out('verdict: %s%s' % (result['verdict'], ('  (%s)' % result['decided_at']) if result.get('decided_at') else ''))
    if result.get('branch'):
        out('branch:  %s' % result['branch'])
    for name, _, _ in STATS:
        st = result['statistics'].get(name, {})
        ci = st.get('ci_minus1') or [None, None]
        out('%-4s%s = median_r S[%s]/S[%s] = %s  (-1 = %s), 90%% CI of -1 [%s, %s], rounds %s, items %s%s'
            % (LABEL[name], ' (deciding)' if name in DECIDING_STATS else ' (reported)', st.get('numerator'),
               st.get('denominator'), fmt(st.get('point')), fmt(st.get('minus1')),
               fmt(ci[0]), fmt(ci[1]), st.get('n_rounds'), st.get('items'),
               ('  UNAVAILABLE: %s' % st['unavailable']) if st.get('unavailable') else ''))
    if result.get('extension'):
        ex = result['extension']
        out('extension: points over all %d rounds: %s' % (ex['n_rounds'],
                                                        ', '.join('%s-1 = %s' % (LABEL.get(k, k), fmt(v))
                                                                  for k, v in ex['minus1'].items())))
    out('controls:')
    for name, control in result['controls'].items():
        detail = dict((k, v) for k, v in control.items() if k not in ('pass', 'judged'))
        text = json.dumps(detail, default=str)
        out('  %-4s %-5s %s' % (name, {True: 'PASS', False: 'FAIL', None: 'n/e'}[control.get('pass')], text[:500]))
    out('items:  item  weight  present  A-valid  A us(med)   B/A     V1/A    V2p/A   V-e V1/V2p')
    for n, item in result['items'].items():
        row = result['per_item'].get(n, {})
        ve = row.get('V-e', {})
        out('        %-4s %7.1f  %-7s  %-7s  %9s  %6s  %6s  %6s  %s' % (
            n, item['weight'], item['present'], item.get('a_valid', '-'), fmt(row.get('A_us_median'), 1),
            fmt(row.get('B/A')), fmt(row.get('V1/A')), fmt(row.get('V2p/A')),
            ' / '.join(ve.get(a, '-') for a in VARIANTS)))
    out('predictions (no decision weight):')
    for name, pred in result['predictions'].items():
        out("  %s' %-5s %s  value=%s" % (name, {True: 'HIT', False: 'MISS', None: 'n/e'}[pred['hit']], pred['text'],
                                          json.dumps(pred['value'], default=str)[:300]))
    for note in result['notes']:
        out('note: %s' % note)


def load_prev102(plan_path, bench_path):
    if not plan_path or not bench_path or not os.path.isfile(plan_path) or not os.path.isfile(bench_path):
        return None, None
    prev = dict(plan=json.loads(Path(plan_path).read_text(encoding='utf-8')),
                bench=json.loads(Path(bench_path).read_text(encoding='utf-8')))
    return prev, dict(plan=plan_path, plan_sha256=sha256_file(plan_path),
                      bench=bench_path, bench_sha256=sha256_file(bench_path))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--bench', required=True)
    parser.add_argument('--equal', default=None)
    parser.add_argument('--capture-log', default=None)
    parser.add_argument('--out', default=None)
    parser.add_argument('--mechanics-only', action='store_true',
                        help='score a mechanics bench (items outside the table, any arms/rounds); never a result')
    parser.add_argument('--prev102-plan', default=PREV102_PLAN, help="session-102 plan for P4' ('' = none)")
    parser.add_argument('--prev102-bench', default=PREV102_BENCH, help="session-102 bench for P4' ('' = none)")
    parser.add_argument('--pred', default=PRED, help=argparse.SUPPRESS)
    parser.add_argument('--parent01', default=PARENT01, help=argparse.SUPPRESS)
    parser.add_argument('--parent02', default=PARENT02, help=argparse.SUPPRESS)
    options = parser.parse_args(argv)
    for label, path, want in (("M5' SEAL", options.pred, PRED_SHA),
                              ('SESSION-102 PARENT pred/01', options.parent01, PARENT01_SHA),
                              ('SESSION-102 PARENT pred/02', options.parent02, PARENT02_SHA)):
        if not seal_ok(path, want):
            print('%s CHANGED OR MISSING (%s): refusing to score' % (label, path))
            return 2
    if options.out and os.path.exists(options.out):
        print('refusing to overwrite %s' % options.out)
        return 2
    plan = json.loads(Path(options.plan).read_text(encoding='utf-8'))
    bench = json.loads(Path(options.bench).read_text(encoding='utf-8'))
    equal = json.loads(Path(options.equal).read_text(encoding='utf-8')) if options.equal else None
    prev102, prev102_files = load_prev102(options.prev102_plan, options.prev102_bench)
    identity = dict(plan_sha256=sha256_file(options.plan), bench_plan_sha256=bench.get('plan_sha256'),
                    equal_plan_sha256=(equal or {}).get('plan_sha256'))
    for key, _ in PLAN_SEAL_KEYS:
        identity['plan_' + key] = plan.get(key)
    identity['seal_problems'] = plan_seal_problems(plan)
    identity['input_problems'] = input_problems(plan) if not options.mechanics_only else []
    identity['files_pass'] = (identity['plan_sha256'] == identity['bench_plan_sha256']
                              and (equal is None or identity['equal_plan_sha256'] == identity['plan_sha256']))
    identity['pass'] = identity['files_pass'] and not identity['seal_problems'] and not identity['input_problems']
    capture_check = check_capture_log(options.capture_log) if options.capture_log else None
    result = decide(plan, bench, equal, final=True, capture_check=capture_check, mechanics=options.mechanics_only,
                    prev102=prev102)
    result['identity'] = identity
    if not identity['pass']:
        result['failed_controls'].append('IDENTITY')
        result['status'] = ('INVALID (plan / bench / equality files do not belong together, the plan was not made '
                            'under all three seals, or its recompile inputs are not the sealed ones)')
        result['verdict'] = None
        result['branch'] = None
    if options.mechanics_only:
        result['status'] = "MECHANICS ONLY - not an M5' result (%s)" % result['status']
        result['verdict'] = None
        result['branch'] = None
    result['seals'] = dict(pred=dict(path=options.pred, sha256=PRED_SHA),
                           parent01=dict(path=options.parent01, sha256=PARENT01_SHA),
                           parent02=dict(path=options.parent02, sha256=PARENT02_SHA))
    result['inputs'] = dict(plan=options.plan, bench=options.bench, equal=options.equal,
                            capture_log=options.capture_log, prev102=prev102_files)
    report(result)
    if options.out:
        Path(options.out).write_text(json.dumps(result, indent=1, default=str), encoding='utf-8')
        print('wrote %s' % options.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
