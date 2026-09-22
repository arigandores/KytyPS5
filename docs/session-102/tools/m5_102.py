"""Session 102, M5 scorer, sealed to pred/01_m5_bench.md (sha256 cf3c353f...) AS AMENDED by the
sealed addendum pred/02_m5_addendum.md (sha256 ced6d410...).  Both hashes are verified before
anything is scored; either one changed => refusal.

    python C:/kyty/s102/m5_102.py --plan <plan.json> --bench <bench.json> --equal <equal.json> \
        --capture-log <log_m5cap102.txt> --out <m5_102.json>

Offline only: it never launches the game, never runs RenderDoc, never re-runs a bench and never
overwrites an output.  Nothing below widens the sealed text:

  pred/01 s2   the ten items and their weights (sum 4 508.0 us/frame)
  pred/01 s5   T[X,i,r] = sum of EventGPUDuration over item i's events, S[X,r] = sum over valid items
  pred/02 s3   X = median_r S[V2,r]/S[A,r], Y = median_r S[V2,r]/S[V2s,r], L = median_r S[V1,r]/S[A,r],
               each with a 90 % percentile bootstrap over rounds (20 000 resamples, seed 102, the SAME
               resample indices for all three):
                 CLOSE-strict     CI_lo(L-1) > 0.06
                 CLOSE-machinery  CI_lo(X-1) > 0.06 and CI_lo(Y-1) > 0.06 (and not strict)
                 NOT CLOSED       (CI_hi(X-1) <= 0.06 or CI_hi(Y-1) <= 0.06) and CI_hi(L-1) <= 0.06
                 INCONCLUSIVE     otherwise => one extension of 20 rounds, then the POINTS over all
                                  rounds decide (L-1 > 0.06 => CLOSE-strict; X-1 > 0.06 and Y-1 > 0.06
                                  => CLOSE-machinery; else NOT CLOSED), published as "decided at the
                                  point after extension".
               X, Y, L, V2s/A, A/B and every per-item ratio of every arm are published always.
  pred/02 s4   five arms B A V1 V2 V2s; the order of round r is DESIGN[r mod 10], DESIGN = the five
               cyclic rotations of [B, A, V1, V2, V2s] (rotation k starts at arm k) FOLLOWED BY their
               reverses in the same rotation order (see design_sequences); R = 20 (two cycles), the
               never-below-8 floor, extension +20 rounds.
  pred/01 s6   V-a capture, V-b coverage (>= 7 of 10 items, >= 60 % of the weight), V-c identity
     + 02 s5   (exclusion <= 40 % of the present items' A-arm time), V-d mechanism noise
               (median_r S[A]/S[B] in [0.97, 1.03]), V-f spirv-val, V-g technical completion.
  pred/02 s2   V-e: arm A replayed three times (A1, A2, A3) with only the item replaced.  Repeatable
               (A1 = A2 = A3 bit for bit) => the variant must be bit-equal to A1; otherwise
               E = max differing bytes between any two A replays and the variant passes iff its
               differing bytes against A1 are <= 2*E, named "within replay noise", never "equal".
               Applied to V1, V2 and V2s.  A failing item leaves THAT variant's sums (numerator and
               denominator); for Y the items failing V-e for V2 OR for V2s leave both sums.  More than
               40 % of the valid A-arm time failing for V2 => V2 INVALID => M5 NOT DECIDED.
  pred/02 s1   V-f is judged with `spirv-val --target-env vulkan1.3 --uniform-buffer-standard-layout`;
               the pred/01 command is reported beside it, never deciding.
  pred/01 s7   P1-P4, reported with no decision weight (P1 against L, P2 against X).

Conventions this file fixes because the seals do not spell them out (none of them can move the
verdict towards either branch; each one can only withhold a verdict):
  * "time" of an item for the V-c / V-e shares = median over the main rounds of its per-round A
    time (V-c: median over rounds of the per-round excluded share).
  * A round counts only when every benched arm was fetched in it.
  * The bootstrap: ONE generator random.Random(102); each of the 20 000 resamples draws R round
    indices with replacement (randrange) and applies the SAME indices to X, Y, L (and to the reported
    V2s/A and A/B); the interval ends are the 5th / 95th percentiles of the medians, linearly
    interpolated (numpy's default 'linear' method).
  * A missing equality record, a missing variant module, a failed variant build, a replacement not
    in effect, or an equality record not made with three A replays counts as a V-e FAIL of that item
    for that variant.
  * The 40 % rule is decisive for V2 only (pred/01 s6, unchanged by pred/02 s2); the V1 and V2s
    failing shares are reported.  If a statistic X, Y or L has NO item left (or a zero denominator in
    a round) the result is NOT EVALUABLE - no verdict is formed on a missing statistic.
  * The 4-hour rule (pred/01 s5) with whole cycles preferred: see rounds_after_time_rule.
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

PRED = 'C:/kyty/s102/pred/01_m5_bench.md'
PRED_SHA = 'cf3c353f7aaa4a2a16d7b59a61461cf26bef11ddbfffd59206ae95a8b6b33e0a'
ADDENDUM = 'C:/kyty/s102/pred/02_m5_addendum.md'
ADDENDUM_SHA = 'ced6d4103c64b9e5b7c81a3a730cac6d2b04a08486f82cf43642b04a8701f4d3'

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
BOOT_SEED = 102
CI_LEVEL = 0.90
ARMS = ('B', 'A', 'V1', 'V2', 'V2s')
VARIANTS = ('V1', 'V2', 'V2s')
ROUNDS_SEALED = 20
ROUNDS_FLOOR = 8
EXT_ROUNDS = 20
A_REPLAYS = 3
REPLAY_PAIRS = ('A1-A2', 'A1-A3', 'A2-A3')
NOISE_FACTOR = 2
VF_DECIDING = ['--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout']
VF_PRED01 = ['--target-env', 'vulkan1.3']
# pred/01 section 7: the four predictions (P2 and P3 read against X / V2 by pred/02 s6)
P1_RANGE = (-0.01, 0.05)
P2_RANGE = (0.02, 0.20)
P4_MIN_PASS = 8

# the statistics: name -> (numerator arm, denominator arm)
STATS = (('X', 'V2', 'A'), ('Y', 'V2', 'V2s'), ('L', 'V1', 'A'), ('V2s_over_A', 'V2s', 'A'),
         ('A_over_B', 'A', 'B'))
DECIDING_STATS = ('X', 'Y', 'L')

MACHINERY_NOTE = ('pred/02 s3: the V2-only BDA machinery a G prototype would first have to replace: '
                  '(i) a 64-bit base, a page-table LDG.E.64 per group, the fits-in-page branch and its '
                  'duplicated per-dword slow path, null-page fault tracking and the fault-buffer store '
                  'at exit; (ii) every V2 data load in a PS item compiles to LDG.E.STRONG.SM (S4 480, '
                  'S8 451, S2 143) while V2s/A loads are weak LDG/LDC.  Reopening G on that ground is a '
                  'decision for the user, recorded in ROADMAP.md first.')
BRANCH = {
    'CLOSE-strict': 'G CLOSED - strict (L crosses: a component every G implementation pays)',
    'CLOSE-machinery': 'G CLOSED - with today\'s BDA machinery (X and Y cross, L does not). ' + MACHINERY_NOTE,
    'NOT CLOSED': ('M5 does not close G; G survives UNLICENSED (not evidence that the price is <= 6 %; '
                   'VS, mesh, SRT chasing, run-time format decode, barriers and uploads unpriced)'),
}


# ---------------------------------------------------------------- the sealed design and R
def design_sequences(arms=ARMS):
    """pred/02 s4: 'the ten sequences formed by the five cyclic rotations of B A V1 V2 V2s and their
    reverses, used in that order'.  Implemented as rotations k = 0..4 (rotation k starts at arms[k])
    followed by the reverses of rotations 0..4.  Every arm stands in every position exactly twice per
    cycle of ten; each arm is immediately preceded only by its two cyclic neighbours (4 times each
    per cycle) - position-balanced, NOT a Williams design for all pairs (that is the sealed text)."""
    arms = tuple(arms)
    rotations = [arms[k:] + arms[:k] for k in range(len(arms))]
    return rotations + [tuple(reversed(seq)) for seq in rotations]


DESIGN = design_sequences(ARMS)
CYCLE = len(DESIGN)


def design_for(arms):
    """The sealed design filtered to the arms actually benched (mechanics only use a subset)."""
    return [tuple(a for a in seq if a in arms) for seq in DESIGN]


def rounds_after_time_rule(requested, done, fit_total, floor=ROUNDS_FLOOR, cycle=CYCLE):
    """pred/01 s5 as amended by pred/02 s4: once a fetch took longer than 10 min, R drops to the
    largest value that fits a 4-hour bench (fit_total = rounds done + rounds that still fit), never
    below the floor of 8.  Whole cycles are preferred: a value >= one cycle (10) is rounded DOWN to a
    whole number of cycles; below one cycle the floor rules (8 or 9 rounds).  Rounds already
    measured are never discarded, and R never rises above the request (a mechanics request below 8
    stays as requested)."""
    candidate = max(floor, int(fit_total))
    if candidate >= cycle:
        candidate = cycle * (candidate // cycle)
    candidate = max(candidate, int(done))
    return min(int(requested), candidate)


# ---------------------------------------------------------------- seals
def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seal_ok(path=PRED, want=PRED_SHA):
    try:
        return sha256_file(path) == want
    except OSError:
        return False


def seals_ok(pred=PRED, addendum=ADDENDUM):
    """Both sealed texts byte-for-byte: pred/01 and its addendum pred/02."""
    return seal_ok(pred, PRED_SHA) and seal_ok(addendum, ADDENDUM_SHA)


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
    resample indices for all of them (pred/02 s3).  series: {name: [value per round]}, every list
    over the same rounds in the same order.  Returns {name: (lo, hi)}."""
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
    """pred/02 s3 on the 90 % intervals of X-1, Y-1, L-1.  stats[name]['ci_minus1'] = [lo, hi]."""
    x_lo, x_hi = stats['X']['ci_minus1']
    y_lo, y_hi = stats['Y']['ci_minus1']
    l_lo, l_hi = stats['L']['ci_minus1']
    if l_lo > THRESHOLD:
        return 'CLOSE-strict'
    if x_lo > THRESHOLD and y_lo > THRESHOLD:
        return 'CLOSE-machinery'
    if (x_hi <= THRESHOLD or y_hi <= THRESHOLD) and l_hi <= THRESHOLD:
        return 'NOT CLOSED'
    return 'INCONCLUSIVE'


def classify_points(x, y, l):
    """pred/02 s3 after the extension: the points over all rounds decide."""
    if l - 1.0 > THRESHOLD:
        return 'CLOSE-strict'
    if x - 1.0 > THRESHOLD and y - 1.0 > THRESHOLD:
        return 'CLOSE-machinery'
    return 'NOT CLOSED'


# ---------------------------------------------------------------- V-e (pred/02 s2)
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
                'reason': 'arm A not replayed three times (pred/02 s2)'}
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
    """V-e of one item for one variant from an rd_m5_equal.py record (never trusts its 'pass')."""
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
        return {'pass': False, 'reason': 'arm A replayed %s times, pred/02 s2 needs %d'
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
    return {r: row for r, row in sorted(table.items()) if all(a in row for a in arms)}


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
    """Rounds whose fetch order is not DESIGN[r mod 10] (filtered to the benched arms), or whose
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


# ---------------------------------------------------------------- the decision
def decide(plan, bench, equal, final=True, capture_check=None, mechanics=False):
    """The whole sealed computation.  Pure function of its inputs (no I/O)."""
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
    # present = in the capture (arm-A md5 or translation-cache link, m5_plan.py, pred/02 s5); only
    # the modules linked by arm A's md5 are summed - a present item without one is wholly excluded.
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
    va = dict(capture_sha256_bench=bench.get('capture_sha256'), capture_sha256_plan=plan.get('capture_sha256'))
    va['sha_match'] = bool(va['capture_sha256_bench']) and va['capture_sha256_bench'] == va['capture_sha256_plan']
    va['items_with_module'] = len(present)
    if capture_check is None:
        va['log_checked'] = False
        va['pass'] = None
    else:
        va['log_checked'] = True
        va.update(capture_check)
        va['pass'] = bool(va['sha_match'] and capture_check.get('dma_layout') and capture_check.get('clock_pin')
                          and len(present) >= MIN_ITEMS)
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

    # ---- V-e output equality (pred/02 s2) ----
    variant_valid = {}
    ve = dict(evaluated=equal is not None, rule='pred/02 s2: three A replays; repeatable => bit-equal to A1; '
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
                   'deciding': arm == 'V2',
                   'share_within_40pct': share is not None and share <= EQUALITY_FAIL_MAX}
        ve['judged'][arm] = judged
        if arm != 'V2' and share is not None and share > EQUALITY_FAIL_MAX:
            notes.append('V-e: %s fails for %.1f %% of the valid A-arm time (reported; the 40 %% rule decides '
                         'for V2 only)' % (arm, 100.0 * share))
    ve['pass'] = (ve['V2']['share_within_40pct']) if (equal is not None or not a_valid) else None
    ve['nondeterministic_reference'] = sorted({n for arm in VARIANTS for n, v in ve['judged'][arm].items()
                                               if v.get('repeatable') is False}, key=names.index)
    ve['E'] = {n: max([v.get('E') for arm in VARIANTS for m, v in ve['judged'][arm].items()
                       if m == n and v.get('E') is not None] or [None]) for n in a_valid}
    if any(ve[arm]['within_replay_noise'] for arm in VARIANTS):
        notes.append('V-e: passing WITHIN REPLAY NOISE (never "equal"): %s'
                     % '; '.join('%s %s' % (arm, ', '.join(ve[arm]['within_replay_noise']))
                                 for arm in VARIANTS if ve[arm]['within_replay_noise']))
    controls['V-e'] = ve

    # ---- V-f spirv-val (pred/02 s1) ----
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
        reasons.append('%d rounds not in the sealed order (pred/02 s4)' % len(violations))
    vg['reasons'] = reasons
    vg['pass'] = not reasons
    controls['V-g'] = vg

    # ---- X, Y, L (+ V2s/A, A/B reported), same resample indices ----
    stat_items = {'X': variant_valid['V2'],
                  'Y': [n for n in variant_valid['V2'] if n in variant_valid['V2s']],
                  'L': variant_valid['V1'],
                  'V2s_over_A': variant_valid['V2s'],
                  'A_over_B': a_valid}
    series = {}
    stats = {}
    for name, num, den in STATS:
        items = stat_items[name]
        row = dict(numerator=num, denominator=den, items=items, n_rounds=0)
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

    # ---- per item: every arm against A, and V2 against V2s ----
    per_item = {}
    for n in a_valid:
        row = {}
        for num, den in (('B', 'A'), ('V1', 'A'), ('V2', 'A'), ('V2s', 'A'), ('V2', 'V2s')):
            if num not in benched or den not in benched:
                continue
            values = [T[n][num][r] / T[n][den][r] for r in rounds if T[n][den][r] > 0]
            row['%s/%s' % (num, den)] = statistics.median(values) if values else None
        row['A_us_median'] = a_time[n]
        row['B_us_median'] = median_over_rounds('B', n) if 'B' in benched else None
        row['V-e'] = {arm: ('pass' if n in variant_valid[arm] else 'FAIL') +
                      (' (within replay noise)' if n in ve[arm]['within_replay_noise'] else '')
                      for arm in VARIANTS}
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
        status = 'V2 INVALID - M5 NOT DECIDED this session'
    elif failed:
        status = 'INVALID'
    elif unevaluated and not (not final and unevaluated == ['V-a']):
        status = 'NOT EVALUABLE (%s not evaluated)' % ', '.join(unevaluated)
    elif missing_stats:
        status = 'NOT EVALUABLE (%s)' % '; '.join('%s: %s' % (s, stats[s].get('unavailable')) for s in missing_stats)
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
                points = {}
                ext_missing = False
                for name in DECIDING_STATS:
                    _, num, den = [s for s in STATS if s[0] == name][0]
                    items = stat_items[name]
                    tables = {}
                    for n in items:
                        tables[n], miss = item_times(bench, plan['items'][n]['events'], all_rounds)
                        if miss:
                            ext_missing = True
                    values = [sum(tables[n][num][r] for n in items) / sum(tables[n][den][r] for n in items)
                              for r in sorted(all_rounds)]
                    points[name] = statistics.median(values)
                result['extension'] = dict(n_rounds=len(all_rounds), points=points,
                                           minus1={k: v - 1.0 for k, v in points.items()})
                if ext_missing:
                    status = 'INVALID'
                    failed.append('V-g (extension missing values)')
                    verdict = None
                else:
                    verdict = classify_points(points['X'], points['Y'], points['L'])
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
    l_m1 = stats['L'].get('minus1')
    x_m1 = stats['X'].get('minus1')
    p['P1'] = dict(text='V1 aggregate Delta (L - 1) in [-0.01, +0.05]', value=l_m1, hit=within(l_m1, P1_RANGE))
    p['P2'] = dict(text='V2 aggregate Delta (X - 1, pred/02 s6) in [+0.02, +0.20]', value=x_m1,
                   hit=within(x_m1, P2_RANGE))
    regs = register_rise(plan, present)
    p['P3'] = dict(text='V2 raises at least one PS item register count above its A count', value=regs,
                   hit=None if regs is None else bool(regs['raised']))
    passing_v2 = len([n for n in present if n in variant_valid['V2']])
    p['P4'] = dict(text='V-e (amended): at least 8 of the present items pass for V2', value=passing_v2,
                   hit=passing_v2 >= P4_MIN_PASS if equal is not None else None)
    result['module_stats'] = module_stats(plan, present)
    return result


def register_rise(plan, present):
    """P3 from register counts carried by the plan (m5_plan.py merges regs.json); None if absent."""
    keys = ('register_count', 'regs', 'registers', 'reg', 'RegisterCount')
    raised = []
    seen = False
    for n in present:
        item = plan['items'][n]
        if item.get('stage') != 'ps':
            continue
        for module in item['modules']:
            a, v2 = module.get('A') or {}, module.get('V2') or {}
            ra = next((a.get(k) for k in keys if a.get(k) is not None), None)
            rv = next((v2.get(k) for k in keys if v2.get(k) is not None), None)
            if ra is None or rv is None:
                continue
            seen = True
            if rv > ra:
                raised.append(dict(item=n, perm=module['perm'], A=ra, V2=rv))
    return dict(raised=raised) if seen else None


def module_stats(plan, present):
    """Every extra field the plan carried per arm module (registers, SASS, ...): reported only."""
    out = {}
    for n in present:
        rows = []
        for module in plan['items'][n]['modules']:
            row = dict(perm=module['perm'], orig=module['orig_shader_id'])
            for arm in ('A', 'V1', 'V2', 'V2s'):
                entry = module.get(arm) or {}
                row[arm] = {k: v for k, v in entry.items() if k not in ('path', 'md5')}
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
    out('M5 scorer, sealed to %s + %s' % (PRED, ADDENDUM))
    out('status:  %s' % result['status'])
    out('verdict: %s%s' % (result['verdict'], ('  (%s)' % result['decided_at']) if result.get('decided_at') else ''))
    if result.get('branch'):
        out('branch:  %s' % result['branch'])
    for name, _, _ in STATS:
        st = result['statistics'].get(name, {})
        ci = st.get('ci_minus1') or [None, None]
        out('%-10s = median_r S[%s]/S[%s] = %s  (-1 = %s), 90%% CI of -1 [%s, %s], rounds %s, items %s%s'
            % (name, st.get('numerator'), st.get('denominator'), fmt(st.get('point')), fmt(st.get('minus1')),
               fmt(ci[0]), fmt(ci[1]), st.get('n_rounds'), st.get('items'),
               ('  UNAVAILABLE: %s' % st['unavailable']) if st.get('unavailable') else ''))
    if result.get('extension'):
        ex = result['extension']
        out('extension: points over all %d rounds: %s' % (ex['n_rounds'],
                                                        ', '.join('%s-1 = %s' % (k, fmt(v)) for k, v in ex['minus1'].items())))
    out('controls:')
    for name, control in result['controls'].items():
        detail = {k: v for k, v in control.items() if k not in ('pass', 'judged')}
        text = json.dumps(detail, default=str)
        out('  %-4s %-5s %s' % (name, {True: 'PASS', False: 'FAIL', None: 'n/e'}[control.get('pass')], text[:500]))
    out('items:  item  weight  present  A-valid  A us(med)   B/A     V1/A    V2/A    V2s/A  V2/V2s  V-e V1/V2/V2s')
    for n, item in result['items'].items():
        row = result['per_item'].get(n, {})
        ve = row.get('V-e', {})
        out('        %-4s %7.1f  %-7s  %-7s  %9s  %6s  %6s  %6s  %6s  %6s  %s' % (
            n, item['weight'], item['present'], item.get('a_valid', '-'), fmt(row.get('A_us_median'), 1),
            fmt(row.get('B/A')), fmt(row.get('V1/A')), fmt(row.get('V2/A')), fmt(row.get('V2s/A')),
            fmt(row.get('V2/V2s')), ' / '.join(ve.get(a, '-') for a in VARIANTS)))
    out('predictions (no decision weight):')
    for name, pred in result['predictions'].items():
        out('  %s %-5s %s  value=%s' % (name, {True: 'HIT', False: 'MISS', None: 'n/e'}[pred['hit']], pred['text'],
                                         json.dumps(pred['value'], default=str)[:200]))
    for note in result['notes']:
        out('note: %s' % note)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--bench', required=True)
    parser.add_argument('--equal', default=None)
    parser.add_argument('--capture-log', default=None)
    parser.add_argument('--out', default=None)
    parser.add_argument('--mechanics-only', action='store_true',
                        help='score a mechanics bench (items outside the table, any arms/rounds); never a result')
    parser.add_argument('--pred', default=PRED, help=argparse.SUPPRESS)
    parser.add_argument('--addendum', default=ADDENDUM, help=argparse.SUPPRESS)
    options = parser.parse_args(argv)
    if not seal_ok(options.pred, PRED_SHA):
        print('SEALED PRE-REGISTRATION CHANGED (%s): refusing to score' % options.pred)
        return 2
    if not seal_ok(options.addendum, ADDENDUM_SHA):
        print('SEALED ADDENDUM CHANGED (%s): refusing to score' % options.addendum)
        return 2
    if options.out and os.path.exists(options.out):
        print('refusing to overwrite %s' % options.out)
        return 2
    plan = json.loads(Path(options.plan).read_text(encoding='utf-8'))
    bench = json.loads(Path(options.bench).read_text(encoding='utf-8'))
    equal = json.loads(Path(options.equal).read_text(encoding='utf-8')) if options.equal else None
    identity = dict(plan_sha256=sha256_file(options.plan), bench_plan_sha256=bench.get('plan_sha256'),
                    equal_plan_sha256=(equal or {}).get('plan_sha256'), plan_pred_sha256=plan.get('pred_sha256'),
                    plan_addendum_sha256=plan.get('addendum_sha256'))
    identity['pass'] = (identity['plan_sha256'] == identity['bench_plan_sha256']
                        and (equal is None or identity['equal_plan_sha256'] == identity['plan_sha256'])
                        and identity['plan_pred_sha256'] == PRED_SHA
                        and identity['plan_addendum_sha256'] == ADDENDUM_SHA)
    capture_check = check_capture_log(options.capture_log) if options.capture_log else None
    result = decide(plan, bench, equal, final=True, capture_check=capture_check, mechanics=options.mechanics_only)
    result['identity'] = identity
    if not identity['pass']:
        result['failed_controls'].append('IDENTITY')
        result['status'] = 'INVALID (plan / bench / equality files do not belong together, or the plan was not made under both seals)'
        result['verdict'] = None
        result['branch'] = None
    if options.mechanics_only:
        result['status'] = 'MECHANICS ONLY - not an M5 result (%s)' % result['status']
        result['verdict'] = None
        result['branch'] = None
    result['seals'] = dict(pred=dict(path=options.pred, sha256=PRED_SHA),
                           addendum=dict(path=options.addendum, sha256=ADDENDUM_SHA))
    result['inputs'] = dict(plan=options.plan, bench=options.bench, equal=options.equal,
                            capture_log=options.capture_log)
    report(result)
    if options.out:
        Path(options.out).write_text(json.dumps(result, indent=1, default=str), encoding='utf-8')
        print('wrote %s' % options.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
