"""Session99 pred04: direct image-GC audit, then independent settled measurements.

Read-only inputs; JSON on stdout. --out creates a NEW file exclusively. No game launcher.
Period90, keep60..88, complete ABBA quartets: two disjoint, orientation-balanced pairs.
Pilot output contains no B endpoint. Historical pred01/02/03 are never reinterpreted.
"""
import argparse
import contextlib
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys

ROOT = Path('C:/kyty/s99')
sys.path.insert(0, str(ROOT))
import bf99 as OLD
from run_safety99 import failure_marker

PRED = ROOT / 'pred/04_gc_audit.md'
PRED_SHA = 'a93f4b6b1068cb34b06d02301d5c35f09483ef60f546f7669b03e193aeee611b'
BINARY_SHA = '34206e3fe4fb7c887af2901ce6332d63d0ebd715ef95d3a4ff5547654b58355f'
CPU = ('bf_burn_cpu_ns', 'bf_burn_cpu_n', 'bf_burn_cpu_bad', 'bf_burn_probe_ns')
IGC = ('bf_igc_checks', 'bf_igc_hold', 'bf_igc_bad', 'bf_igc_critical', 'bf_igc_evict')
REQUIRED = tuple(dict.fromkeys(OLD.REQUIRED + CPU + IGC + ('arm', 'blk')))
TECH_OLD = ('COUNTERS', 'EDGE', "C1'''", "C2'", 'C4_B', 'DARK_B',
            'LIVE_DARK_RATIO', 'REAL_CLEARS', 'MARKERS_OFF', "C10'''_B")


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def identity(tag):
    named = re.fullmatch(r'(eng99a[456]|eng99c[123]|bf99[ef])(?:_entry([12]))?', tag)
    if named is None:
        raise ValueError('unknown campaign tag or entry suffix (only _entry1/_entry2)')
    tag = named[1]
    match = re.fullmatch(r'eng99([ac])([1-6])', tag)
    if match:
        return 'pilot', match[1], int(match[2])
    if tag in ('bf99e', 'bf99f'):
        return 'measurement', 'a' if tag == 'bf99e' else 'c', None
    raise ValueError('allowed tags: eng99a4..a6, eng99c1..c3, bf99e, bf99f')


def entry_history(tag, root, current):
    match = re.fullmatch(r'(.+)_entry([12])', tag)
    if not match:
        return [], []
    base, count = match[1], int(match[2])
    evidence, errors = [], []
    for index in range(count):
        previous = base + ('_entry%d' % index if index else '')
        paths = [root / (previous + '.json'), root / ('log_' + previous + '.txt'),
                 root / ('stdout_' + previous + '.txt')]
        try:
            old = json.loads(paths[0].read_text(encoding='utf-8'))
            attempts = old.get('attempts') or []
            if len(attempts) != 1 or attempts[0].get('label') != 'attempt 1' or \
                    not isinstance(attempts[0].get('outcome'), str) or attempts[0]['outcome'] == 'ok':
                errors.append('entry predecessor did not fail in its sole attempt: ' + previous)
            with paths[1].open('rb') as handle:
                if any(line.startswith(b'GateArm:') for line in handle):
                    errors.append('entry predecessor reached the schedule: ' + previous)
            for key in ('schedule', 'arms', 'binary_sha256', 'gates', 'hold_s', 'cmdline'):
                if old.get(key) != current.get(key):
                    errors.append('entry retry changed ' + key)
            if (old.get('prereg') or {}).get('sha256') != (current.get('prereg') or {}).get('sha256'):
                errors.append('entry retry changed its rule')
            # Artifact destination may differ; all other KYTY settings, including cache
            # switches and frozen-source identity, must remain identical.
            config = lambda env: {k: v for k, v in (env or {}).items()
                                  if k.startswith('KYTY_') and k != 'KYTY_REC'}
            if config(old.get('env')) != config(current.get('env')):
                errors.append('entry retry changed runtime/cache/source configuration')
            if attempts and (attempts[0].get('pipeline_cache_off', False) !=
                             current.get('attempts', [{}])[0].get('pipeline_cache_off', False)):
                errors.append('entry retry changed pipeline-cache policy')
            evidence.append({'tag': previous, 'raw_sha256': {p.name: sha(p) for p in paths}})
        except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
            errors.append('missing/invalid entry predecessor: ' + str(exc))
    return evidence, errors


def protocol(meta, log, stdout, instrument, phase):
    errors, arms, modes, durations = [], {}, {'latch': set(), 'clear': set(), 'pin': set(), 'cpu': set(), 'igc': set()}, {}
    streams = {}
    env = meta.get('env') or {}
    if any(key.upper() == 'KYTY_IMAGE_LIFETIME_TRACE' for key in env):
        errors.append('ImageLife diagnostic environment present; even value0 enables tracing')
    for key, expected in [('KYTY_BIND_FLOOR_LATCH', '1'), ('KYTY_BIND_FLOOR_CLEAR', '0'),
                          ('KYTY_GPU_CLOCK_PIN', '1'), ('KYTY_GPU_MARKERS', '0'),
                          ('KYTY_GPU_CHECKPOINTS', '0'), ('KYTY_GATE_SCHEDULE_ABBA', '1'),
                          ('KYTY_BIND_FLOOR_CPU', '1'), ('KYTY_BIND_FLOOR_GC_AUDIT', '1'),
                          ('KYTY_FRAME_TRACE', 'lite')]:
        if str(env.get(key)) != expected:
            errors.append('environment ' + key)
    if BINARY_SHA == 'UNSEALED' or str(meta.get('binary_sha256', '')).lower() != BINARY_SHA:
        errors.append('binary SHA mismatch/unsealed')
    if PRED_SHA == 'UNSEALED' or (meta.get('prereg') or {}).get('sha256') != PRED_SHA:
        errors.append('pre-registration SHA mismatch/unsealed')
    try:
        baseline = (ROOT / 'gates_base.txt').read_bytes()
        if hashlib.sha256(baseline).hexdigest() != OLD.GATES_SHA or \
                OLD.tokens(meta.get('gates', '')) != OLD.tokens(baseline.decode()):
            errors.append('baseline gates mismatch')
    except (OSError, ValueError, UnicodeError):
        errors.append('baseline gates missing/unparseable')
    wanted = None
    burn = None
    try:
        schedule = meta['schedule']
        if schedule != env.get('KYTY_GATE_SCHEDULE') or not schedule.startswith('90+1800:'):
            raise ValueError('schedule/env period/start mismatch')
        wanted = [OLD.tokens(x) for x in schedule.split(':', 1)[1].split('|')]
        if len(wanted) != 2 or [OLD.tokens(x) for x in meta['arms']] != wanted:
            raise ValueError('metadata arms mismatch')
        for arm, text in enumerate(wanted):
            if set(text) != {'bindfloor', 'drawahead', 'bfmode', 'bfburn'} or \
                    text['bindfloor'] != arm or text['bfmode'] != 2 or \
                    text['drawahead'] != (0 if instrument == 'c' and arm else 1):
                raise ValueError('wrong arm configuration')
        burn = wanted[0]['bfburn']
        if wanted[1]['bfburn'] != burn or not 0 < burn <= 30000:
            raise ValueError('burn differs between arms or outside (0,30000]')
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        errors.append(str(exc))
    with Path(log).open('rb') as handle:
        for line in handle:
            if b'imagelife' in line.lower():
                errors.append('ImageLife diagnostic output in raw log')
            report = re.match(rb'^FrameTrace(?P<kind>-draw|-x)?: n=(\d+)\b', line)
            if report:
                kind, n = report['kind'] or b'main', int(report[2])
                seen = streams.setdefault(n, set())
                if kind in seen:
                    errors.append('duplicate report stream/frame')
                seen.add(kind)
            if failure_marker(line):
                errors.append('failure marker in raw log')
            for key, pat in [('latch', rb'^BindFloorLatch: mode (\d+)'),
                             ('clear', rb'^BindFloorClear: mode (\d+)'),
                             ('pin', rb'^GpuClockPin: mode (\d+)'),
                             ('cpu', rb'^BindFloorCpu: mode (\d+)'),
                             ('igc', rb'^BindFloorGcAudit: mode\s*(\d+)\b')]:
                match = re.match(pat, line)
                if match:
                    modes[key].add(int(match[1]))
            frame = re.match(rb'^FrameTrace: n=(\d+)\b', line)
            if frame:
                dt = re.search(rb'\bdt_us=(-?\d+)\b', line)
                if dt is None or int(dt[1]) < 0 or int(frame[1]) in durations:
                    errors.append('raw duration missing/negative/duplicate')
                else:
                    durations[int(frame[1])] = int(dt[1])
            if not line.startswith(b'GateArm:'):
                continue
            match = OLD.H.L.GATEARM.fullmatch(line.rstrip(b'\r\n'))
            if match is None:
                errors.append('malformed GateArm'); continue
            arm, count, block, frame, period, abba = map(int, match.groups()[:6])
            if block != len(arms) or (count, period, abba) != (2, 90, 1) or \
                    arm != (0, 1, 1, 0)[block % 4] or frame != 1800 + 90 * block:
                errors.append('actual GateArm sequence/ABBA/period/frame mismatch')
            try:
                text = OLD.tokens(match[7].decode())
                if wanted is None or arm not in (0, 1) or text != wanted[arm]:
                    errors.append('actual GateArm differs from metadata')
            except (ValueError, UnicodeError):
                errors.append('actual GateArm text invalid')
            arms[block] = arm
    if not arms or modes != {'latch': {1}, 'clear': {0}, 'pin': {1}, 'cpu': {1}, 'igc': {1}}:
        errors.append('log mode/pin evidence missing/wrong')
    if not streams or any(parts != {b'main', b'-draw', b'-x'} for parts in streams.values()):
        errors.append('missing main/draw/x report stream')
    if not Path(stdout).is_file():
        errors.append('stdout missing')
    else:
        with Path(stdout).open('rb') as handle:
            for line in handle:
                if failure_marker(line):
                    errors.append('failure marker in stdout')
                if b'imagelife' in line.lower():
                    errors.append('ImageLife diagnostic output in stdout')
    hold = 300 if phase == 'pilot' else 900
    attempts = meta.get('attempts') or []
    if meta.get('hold_s') != hold or [a.get('label') for a in attempts] != ['attempt 1']:
        errors.append('wrong hold/process count; exactly one attempt, no warmup/retry')
    for attempt in attempts:
        actual = attempt.get('hold_s')
        if attempt.get('outcome') != 'ok' or 'hold_exit' not in attempt or attempt['hold_exit'] is not None \
                or not isinstance(actual, (float, int)) or not math.isfinite(actual) or actual < hold - 5:
            errors.append('process survival failed')
    duration_ok, duration = OLD.duration_evidence(meta, durations)
    if not duration_ok:
        errors.append('raw duration contradicts hold')
    return {'errors': sorted(set(errors)), 'arms': arms, 'burn': burn, 'duration': duration}


def select(rows, arms, first=2100):
    """Geometry only, no CPU endpoint. Whole quartets preserve exact AB/BA balance."""
    blocks = {}
    for n, row in sorted(rows.items()):
        if 'blk' in row:
            blocks.setdefault(row['blk'], []).append(n)
    eligible, rejected = {}, {}
    for block, ns in blocks.items():
        if block not in arms:
            rejected[block] = 'orphan'; continue
        expected = list(range(1801 + 90 * block, 1891 + 90 * block))
        scheduled = [n for n in ns if n > 1800]
        if scheduled != expected:
            rejected[block] = 'incomplete block'; continue
        kept = scheduled[60:89]
        if len(kept) != 29 or min(kept) < first:
            rejected[block] = 'outside first-frame window'; continue
        if any(rows[n].get('arm') != arms[block] for n in scheduled):
            rejected[block] = 'arm mismatch'; continue
        eligible[block] = kept
    pairs, excluded = [], []
    for b in range(0, max(arms, default=-1) + 1, 4):
        if all(k in eligible for k in range(b, b + 4)):
            pairs.extend([(b, b + 1), (b + 2, b + 3)])
        else:
            excluded.extend(k for k in range(b, b + 4) if k in eligible)
    chosen = {b: eligible[b] for pair in pairs for b in pair}
    return {'blocks': chosen, 'pairs': pairs, 'excluded_edge_blocks': excluded,
            'rejected_blocks': rejected,
            'internal_incomplete': [b for b, why in rejected.items()
                                    if 0 < b < max(blocks, default=0) and why == 'incomplete block'],
            'rows': [n for b in sorted(chosen) for n in chosen[b]]}


def population(rows, pairs=None, blocks=None):
    groups = [[r for r in rows if r.get('arm') == arm] for arm in (0, 1)]
    if not all(groups):
        return {'valid_data': False}
    def area(rs):
        att = sum(r['rt_att'] for r in rs)
        return sum(r['rt_kpx'] for r in rs) / att if att > 0 else None
    areas = [area(g) for g in groups]
    draws = [statistics.fmean(r['draws'] for r in g) for g in groups]
    if any(v is None or v <= 0 for v in areas + draws):
        return {'valid_data': False}
    out = {'valid_data': True, 'area_split_pct': 100 * (areas[1] / areas[0] - 1),
           'work_pct': 100 * (draws[1] / draws[0] - 1), 'draws_u': draws[0], 'draws_a': draws[1],
           'C5_ratio': abs(draws[1] / draws[0] - 1)}
    if pairs is not None:
        deltas = []
        for left, right in pairs:
            p = [blocks[left], blocks[right]]
            p.sort(key=lambda g: g[0]['arm'])
            a0, a1 = area(p[0]), area(p[1])
            if a0 is None or a1 is None or a0 <= 0:
                out['valid_data'] = False; return out
            deltas.append(100 * (a1 / a0 - 1))
        # Exact legacy within-pair band is 0.5 PERCENT, not a 0.02 ratio.
        out['area_pairs'] = len(deltas)
        out['area_matched'] = sum(abs(x) <= .5 for x in deltas)
        out['area_match_pct'] = 100 * out['area_matched'] / len(deltas) if deltas else 0
        out['pair_area_deltas_pct'] = deltas
    return out


def analyze(rows, arms, instrument, phase):
    missing = sorted({key for row in rows.values() for key in REQUIRED if key not in row})
    selected = select(rows, arms)
    technical = {'FULL_SCHEMA': bool(rows) and not missing}
    technical['INTERNAL_ROWS_COMPLETE'] = not selected['internal_incomplete']
    technical['FULL_ROW_IDENTITY'] = all(r.get('blk') == max(0, (n - 1801) // 90)
        and r.get('blk') in arms and r.get('arm') == arms[r['blk']]
        for n, r in rows.items())
    out = {'technical': technical, 'strict': {}, 'missing': missing, 'selection': selected,
           'metrics': {}}
    if missing or not rows:
        return out
    technical['IGC_NONNEGATIVE'] = all(r[k] >= 0 for r in rows.values() for k in IGC)
    technical['IGC_CHECKS_POSITIVE'] = sum(r['bf_igc_checks'] for r in rows.values()) > 0
    for key in ('bf_igc_bad', 'bf_igc_critical', 'bf_igc_evict'):
        technical[key.upper() + '_ZERO'] = all(r[key] == 0 for r in rows.values())
    technical['IGC_HOLD_EACH_ARMED_BLOCK'] = bool(selected['blocks']) and all(
        sum(rows[n]['bf_igc_hold'] for n in ns) > 0 for b, ns in selected['blocks'].items() if arms[b] == 1)
    out['gc_audit'] = {'whole_log_totals': {k: sum(r[k] for r in rows.values()) for k in IGC},
                       'scope': 'direct image-GC clock/hold audit; not all native allocations'}
    base = OLD.controls(rows, arms, instrument)
    technical.update({key: base['checks'].get(key, False) for key in TECH_OLD})
    if instrument == 'c':
        technical['C4_B_OUT'] = base['checks'].get('C4_B_OUT', False)
    technical['CPU_BAD_ZERO'] = all(r['bf_burn_cpu_bad'] == 0 for r in rows.values())
    technical['CPU_NONNEGATIVE'] = all(r[k] >= 0 for r in rows.values() for k in CPU)
    ts = base['trim']['ts']
    nontransition = [[r for n, r in rows.items() if n >= 2100 and r['blk'] >= 1
                      and r['arm'] == arm and n not in ts] for arm in (0, 1)]
    technical['CPU_BASE_DARK'] = all(sum(r[k] for r in nontransition[0]) <=
                                    .001 * sum(r[k] for r in nontransition[1]) for k in CPU)
    dark_keys = tuple(OLD.R.DARK98) + OLD.LIVE + CPU
    cpu_dark_rows = {n: dict(r, cpu_dark=int(any(r[k] for k in dark_keys))) for n, r in rows.items()}
    bad, multi, _, _ = OLD.H.leak_structure(cpu_dark_rows, sorted(rows), 0, 'cpu_dark',
                                          base['trim']['idx'], base['trim']['e'])
    technical['CPU_DARK_STRUCTURE'] = not bad and not multi
    technical['COMPLETE_PAIRS'] = len(selected['pairs']) >= (10 if phase == 'pilot' else 30)
    counts = [sum(arms[p[0]] == a for p in selected['pairs']) for a in (0, 1)]
    technical['AB_BA_BALANCED'] = counts[0] == counts[1] and counts[0] > 0
    raw_window = [r for n, r in rows.items() if n >= 2100 and r['blk'] >= 1]
    out['reported_raw_population'] = population(raw_window)
    if not selected['rows']:
        return out
    retained = [rows[n] for n in selected['rows']]
    blocks = {b: [rows[n] for n in ns] for b, ns in selected['blocks'].items()}
    a, u = [[r for r in retained if r['arm'] == arm] for arm in (1, 0)]
    s = lambda g, key: sum(r[key] for r in g)
    technical['CPU_ARMED_POSITIVE'] = s(a, 'bf_burn_cpu_ns') > 0 and s(a, 'bf_burn_cpu_n') > 0
    technical['CPU_AGGREGATE'] = s(a, 'bf_burn_cpu_ns') <= 1000 * s(a, 'cpu_gpu_us') + 1000 * len(a)
    technical['C2_SETTLED'] = s(a, 'draws') > 0 and abs(s(a, 'bf_n') / s(a, 'draws') - 1) <= .02 \
        and s(a, 'bf_skip') <= .02 * s(a, 'bf_n') and s(a, 'bf_skip_drop') <= .02 * s(a, 'bf_n')
    dt_a, dt_u = [statistics.fmean(r['dt_us'] for r in g) for g in (a, u)]
    pop = population(retained, selected['pairs'], blocks)
    out['metrics'] = dict(pop, dt_a_us=dt_a, dt_u_us=dt_u, dt_delta_us=dt_u - dt_a,
                          dt_relative=abs(dt_a - dt_u) / dt_u if dt_u > 0 else None,
                          pairs=len(selected['pairs']), rows_per_arm=len(a), orientations=counts,
                          edge_histogram=base['trim']['hist'],
                          armed_cpu_burn_mean_ms=s(a, 'bf_burn_cpu_ns') / len(a) / 1e6,
                          armed_wall_burn_mean_ms=s(a, 'bf_burn_ns') / len(a) / 1e6,
                          cpu_query_cost_indicator_mean_ms=s(a, 'bf_burn_probe_ns') / len(a) / 1e6,
                          cpu_aggregate_rounding_allowance_ns=1000 * len(a))
    strict = out['strict']
    strict['AREA_SPLIT'] = pop['valid_data'] and abs(pop['area_split_pct']) < 1
    strict['AREA_MATCH'] = pop['valid_data'] and pop['area_match_pct'] >= 90
    strict['WORK'] = pop['valid_data'] and abs(pop['work_pct']) < .5
    strict['C5'] = pop['valid_data'] and pop['C5_ratio'] <= .02
    strict['C9'] = dt_u > 0 and abs(dt_a - dt_u) / dt_u <= .03
    cpu_net = lambda r: r['cpu_gpu_us'] - r['spin_gpu_us'] - r['bf_burn_cpu_ns'] / 1000
    technical['C8_CPU'] = statistics.fmean(cpu_net(r) for r in a) < \
        statistics.fmean(r['cpu_gpu_us'] - r['spin_gpu_us'] for r in u)
    if phase == 'measurement':
        armed_blocks = [g for g in blocks.values() if g[0]['arm'] == 1]
        out['endpoints'] = {
            'B_cpu_ms': statistics.median(statistics.fmean(cpu_net(r) for r in g) for g in armed_blocks) / 1000,
            'B_wall_compatibility_ms': statistics.median(statistics.fmean(
                r['cpu_gpu_us'] - r['spin_gpu_us'] - r['bf_burn_ns'] / 1000 for r in g)
                for g in armed_blocks) / 1000,
            'cpu_query_cost_indicator_ms': statistics.median(statistics.fmean(r['bf_burn_probe_ns']
                for r in g) for g in armed_blocks) / 1e6}
        technical['POSITIVE_ENDPOINT'] = math.isfinite(out['endpoints']['B_cpu_ms']) and \
            out['endpoints']['B_cpu_ms'] > 0
    return out


@contextlib.contextmanager
def legacy_state():
    snapshots = [(module, name, copy.deepcopy(getattr(module, name))) for module, names in
                 [(OLD.H, ('DECIDE', '_DESC')),
                  (OLD.H.bf96, ('CONTROLS', 'PREDS', 'SEALED_FAILS')),
                  (OLD.R, ('RESULTS', 'SEALED_PRINTED', 'BF_DARK'))] for name in names]
    try:
        yield
    finally:
        for module, name, value in snapshots:
            current = getattr(module, name)
            current.clear()
            current.update(value) if isinstance(current, dict) else current.extend(value)


def full_reversibility(tag, root, minimum):
    OLD.R.RESULTS.clear(); OLD.R.SEALED_PRINTED.clear()
    find = OLD.R.L.find_log
    OLD.R.L.find_log = lambda t: str(root / ('log_' + t + '.txt'))
    try:
        _, text = OLD.invoke(OLD.R, ['rv98.py', tag, '--root', str(root), '--min-falling', str(minimum), '--dry'])
    finally:
        OLD.R.L.find_log = find
    results = {str(k): ok for k, ok in OLD.R.RESULTS}
    return {k: results.get(k, False) for k in OLD.RV_KEEP}, text


def recommendation(burn, metrics, strict, ordinal, previous=None):
    delta = metrics.get('dt_delta_us')
    if delta is None or metrics.get('dt_relative') is None:
        return {'action': 'INVESTIGATE', 'reason': 'no comparable timing rows'}
    if metrics['dt_relative'] <= .01:
        if all(strict.values()) and strict:
            return {'action': 'LOCK', 'fixed_burn': burn}
        return {'action': 'CAUSAL_TEST', 'reason': 'dt matched; work/area or other strict control failed'}
    if ordinal in (3, 6):
        return {'action': 'CAUSAL_TEST', 'reason': 'three engineering pilots exhausted; task continues with diagnosis'}
    if previous and delta * previous['metrics']['dt_delta_us'] < 0:
        candidate = OLD.round_100((burn + previous['burn']) / 2)
        method = 'sign-flip midpoint'
    else:
        candidate = burn + OLD.round_100(delta)
        method = 'old burn + round100(dt_U-dt_A)'
    if not 0 < candidate <= 30000 or candidate == burn:
        return {'action': 'CAUSAL_TEST', 'reason': 'candidate outside band or no progress; no clamp'}
    return {'action': 'TUNE', 'next_burn': candidate, 'method': method}


def source_check(path, root, meta, instrument, phase, ordinal, burn):
    if phase == 'pilot' and ordinal == (4 if instrument == 'a' else 1):
        return (None, [] if path is None and burn == 17800 else ['fresh branch pilot requires no source and burn17800'])
    if path is None:
        return None, ['pinned preceding pilot artifact required']
    errors = []
    try:
        source = json.loads(Path(path).read_text(encoding='utf-8'))
        env = meta.get('env') or {}
        if env.get('KYTY_SETTLED_SOURCE_SHA256') != sha(path) or env.get('KYTY_SETTLED_SOURCE_TAG') != source['tag']:
            errors.append('source was not pinned in launch metadata')
        if source.get('phase') != 'pilot' or source.get('instrument') != instrument or \
                source.get('status') != 'ENGINEERING_COMPLETE' or source.get('pred_sha256') != PRED_SHA or \
                source.get('binary_sha256') != BINARY_SHA or not all(source.get('technical', {}).values()):
            errors.append('source pilot identity/technical status invalid')
        source_phase, si, so = identity(source['tag'])
        if source_phase != 'pilot' or si != instrument or (phase == 'pilot' and so != ordinal - 1):
            errors.append('source is not the immediate preceding pilot')
        for name, digest in source['raw_sha256'].items():
            if Path(name).name != name or sha(root / name) != digest:
                errors.append('source raw input changed: ' + name)
        if set(source['raw_sha256']) != {source['tag'] + '.json', 'log_' + source['tag'] + '.txt',
                                        'stdout_' + source['tag'] + '.txt'}:
            errors.append('source provenance incomplete')
        decision = source.get('decision') or {}
        expected = decision.get('next_burn') if phase == 'pilot' else decision.get('fixed_burn')
        if decision.get('action') != ('TUNE' if phase == 'pilot' else 'LOCK') or burn != expected:
            errors.append('budget does not follow the frozen pilot decision')
        if errors:
            return source, errors
        predecessor = (source.get('source_artifact') or {}).get('path')
        replay = evaluate(source['tag'], root, Path(predecessor) if predecessor else None)
        if replay.get('status') != 'ENGINEERING_COMPLETE' or any(
                replay.get(key) != source.get(key) for key in ('metrics', 'technical', 'strict', 'decision')):
            errors.append('source pilot does not reproduce from raw under this sealed rule')
        # Artifact JSON stringifies block keys and turns tuple pairs into arrays.
        # Compare the whole selector after the same lossless JSON normalization.
        normalize = lambda value: json.loads(json.dumps(value, allow_nan=False))
        if not isinstance(source.get('selection'), dict) or \
                normalize(replay.get('selection')) != normalize(source.get('selection')):
            errors.append('source selection does not reproduce from raw under this sealed rule')
        return source, errors
    except (OSError, KeyError, ValueError, TypeError) as exc:
        return None, ['source artifact invalid: ' + str(exc)]


def evaluate(tag, root, source_path=None, mechanics=False):
    phase, instrument, ordinal = identity(tag)
    result = {'schema': 'settled99-gc-v1', 'tag': tag, 'phase': phase, 'instrument': instrument,
              'pred_sha256': PRED_SHA, 'binary_sha256': BINARY_SHA,
              'status': 'NOT_MEASUREMENT', 'global_M3': 'GAP unchanged; G/R1 unlicensed', 'errors': []}
    if not mechanics and root.resolve() != ROOT.resolve():
        result['errors'].append('production root must be C:/kyty/s99'); return result
    if not PRED.exists() or sha(PRED) != PRED_SHA or PRED_SHA == 'UNSEALED' or BINARY_SHA == 'UNSEALED':
        result['errors'].append('new rule/binary unsealed or changed')
        if not mechanics:
            return result
    names = [tag + '.json', 'log_' + tag + '.txt', 'stdout_' + tag + '.txt']
    if not all((root / name).is_file() for name in names):
        result['errors'].append('missing metadata/raw/stdout'); return result
    before = {name: sha(root / name) for name in names}
    meta = json.loads((root / names[0]).read_text(encoding='utf-8'))
    if meta.get('tag') != tag:
        result['errors'].append('metadata tag differs from actual input tag')
    history, history_errors = entry_history(tag, root, meta)
    result['entry_history'] = history
    result['errors'].extend(history_errors)
    proto = protocol(meta, root / names[1], root / names[2], instrument, phase)
    result['errors'].extend(proto['errors'])
    result.update(burn=proto['burn'], duration=proto['duration'], raw_sha256=before)
    previous, source_errors = source_check(source_path, root, meta, instrument, phase, ordinal, proto['burn'])
    result['errors'].extend(source_errors)
    if source_path:
        result['source_artifact'] = {'path': str(Path(source_path).resolve()), 'sha256': sha(source_path)}
    rows, _, _ = OLD.H.E84.scan(root / names[1], REQUIRED)
    analysis = analyze(rows, proto['arms'], instrument, phase)
    result.update({k: v for k, v in analysis.items() if k not in ('selection', 'endpoints')})
    result['selection'] = {k: v for k, v in analysis['selection'].items() if k not in ('rows', 'blocks')}
    result['selection']['row_ranges'] = {b: [ns[0], ns[-1]] for b, ns in analysis['selection']['blocks'].items()}
    with legacy_state():
        rv, rv_text = full_reversibility(tag, root, 8 if phase == 'pilot' else 30)
    result['reported_image_birth_proxies'] = {'R' + k: rv.pop(k) for k in ('6', "6'")}
    result['image_birth_proxy_scope'] = 'original image Insert counts, reported only; not specific GC-loss evidence'
    result['technical'].update({'R' + k: ok for k, ok in rv.items()})
    result['reported_full_reversibility'] = rv_text
    # Old controls retain their exact scopes and original FAIL text. No old B/verdict
    # sections are copied into JSON, especially not for engineering pilots.
    with legacy_state():
        old_text, old_controls, raw_area = OLD.legacy(tag, root)
    result['reported_old_controls'] = [line for line in old_text.splitlines()
        if re.search(r'\bC\d', line) and ('PASS' in line or 'FAIL' in line)]
    result['reported_old_area_controls'] = [line for line in old_text.splitlines()
        if re.search(r'\[(?:PASS|FAIL)\].*(?:area split <|pair match >=|work within)', line)]
    result['reported_old_area_verdict'] = raw_area
    result['technical'].update({'OLD_C' + k: old_controls.get(k, False) for k in ("3'", "6'", '7')})
    result['strict']['RETAINED_DATA'] = bool(result['metrics'].get('valid_data'))
    if {name: sha(root / name) for name in names} != before:
        result['errors'].append('raw inputs changed during scoring')
    technical_ok = not result['errors'] and all(result['technical'].values())
    if phase == 'pilot':
        result['decision'] = recommendation(proto['burn'], result['metrics'], result['strict'], ordinal, previous) \
            if technical_ok else {'action': 'INVESTIGATE', 'reason': 'technical/survival failure; fix before another run'}
        if technical_ok and not mechanics:
            result['status'] = 'ENGINEERING_COMPLETE'
    elif technical_ok and all(result['strict'].values()) and not mechanics:
        result['status'] = 'ADMITTED_SETTLED_MEASUREMENT'
        result['endpoints'] = analysis['endpoints']
    if mechanics:
        result['status'] = 'NOT_MEASUREMENT'
        result['errors'].append('mechanics-only; no admitted result or endpoint')
    return result


def combine(a, c):
    valid = all(r.get('status') == 'ADMITTED_SETTLED_MEASUREMENT' for r in (a, c)) and \
        a.get('instrument') == 'a' and c.get('instrument') == 'c'
    if not valid:
        return {'status': 'NO_VERDICT', 'global_M3': 'GAP unchanged; G/R1 unlicensed'}
    values = [r['endpoints']['B_cpu_ms'] for r in (a, c)]
    diagnostic = 'HIGH' if min(values) >= 15.5 else 'LOW' if max(values) <= 11 else 'GAP'
    return {'status': 'DIAGNOSTIC_ONLY', 'diagnostic': diagnostic, 'B_cpu_ms': values,
            'addend_ms': 0, 'bindings_only_measurement_complete': True,
            'global_M3': 'GAP unchanged; no G/R1 closure/licence; route order unchanged'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tag', nargs='?')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--source-json', type=Path)
    parser.add_argument('--mechanics-only', action='store_true')
    parser.add_argument('--combine', nargs=2, metavar=('A_JSON', 'C_JSON'))
    parser.add_argument('--out', type=Path, help='exclusive new JSON output, never overwrite')
    args = parser.parse_args()
    try:
        if args.combine:
            artifacts = [json.loads(Path(path).read_text(encoding='utf-8')) for path in args.combine]
            checked = []
            for artifact in artifacts:
                source = (artifact.get('source_artifact') or {}).get('path')
                checked.append(evaluate(artifact['tag'], args.root, Path(source) if source else None,
                                        args.mechanics_only))
            result = combine(*checked)
        elif args.tag:
            result = evaluate(args.tag, args.root, args.source_json, args.mechanics_only)
        else:
            parser.error('tag or --combine required')
        text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        if args.out:
            if not args.mechanics_only and not args.out.resolve().is_relative_to(ROOT.resolve()):
                raise ValueError('production artifacts must remain under C:/kyty/s99')
            with args.out.open('x', encoding='utf-8') as handle:
                handle.write(text)
        print(text, end='')
        return 0 if result['status'] in ('ENGINEERING_COMPLETE', 'ADMITTED_SETTLED_MEASUREMENT', 'DIAGNOSTIC_ONLY') else 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'NOT_MEASUREMENT', 'errors': [str(exc)]})); return 1


if __name__ == '__main__':
    sys.exit(main())
