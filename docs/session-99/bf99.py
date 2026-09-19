"""Session 99 bindings-only diagnostic. No mode-3 verdict is reused.

Historical bf98 output is reported verbatim, including its mode-2 C4 FAIL.
Admission uses its unchanged C3', C5, C6', C7, fresh T* controls and rv98
C11-C20 on THIS process (and its warmup); no rv98a proof substitution.
--mechanics-only bypasses the new seal solely for offline checks: NEVER ADMITTED.
"""
import argparse
import contextlib
import hashlib
import io
import json
import math
import re
import statistics
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEPS = HERE if (HERE / 'bf98.py').exists() else HERE.parent
sys.path.insert(0, str(DEPS))
import bf98 as H
import rv98 as R
import area_series as AS
import area_verdict as AV
from run_safety99 import failure_marker

PRED = Path('C:/kyty/s99/pred/01_bindings_only.md')
PRED_SHA = '8b816528b78a1730c052d7fdbc414d7b00ef3b9c4df25ab2e7016b23d9d4b14d'
BINARY_SHA = 'ee9cc8ab1f5d25384dedb02a6a6abfca2aa7692585fcaddc74950721afc7a160'
GATES_SHA = '00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8'
LIVE = ('bf_live_ahead', 'bf_live_mat', 'bf_live_memo')
REQUIRED = tuple(dict.fromkeys(H.WANT + tuple(R.DARK98) + tuple(R.EXCLUDED98) + LIVE +
                              H.bf96.OTHER + ('img_new', 'buf_new', 'gm_ops', 'bda_scan')))
KEEP = ("3'", '5', "6'", '7')
RV_KEEP = ('1', '2', "3'", "4'", '5', '6', "6'", '7', "7'", '8')


def tokens(text):
    out = {}
    for token in text.split():
        if '=' not in token:
            raise ValueError('non-assignment in schedule: ' + token)
        k, v = token.split('=', 1)
        if k in out or not re.fullmatch(r'-?\d+', v):
            raise ValueError('duplicate/noninteger schedule token: ' + token)
        out[k] = int(v)
    return out


def protocol(meta, log, instrument, calibration=False, warmup=False):
    """Strict metadata AND actual GateArm proof; missing is never a defaulted success."""
    errors, gates, modes = [], [], {'latch': set(), 'clear': set(), 'pin': set()}
    durations = {}
    env = meta.get('env') or {}
    for key, value in [('KYTY_BIND_FLOOR_LATCH', '1'), ('KYTY_BIND_FLOOR_CLEAR', '0'),
                       ('KYTY_GPU_CLOCK_PIN', '1'), ('KYTY_GATE_SCHEDULE_ABBA', '1'),
                       ('KYTY_FRAME_TRACE', 'lite')]:
        if str(env.get(key)) != value:
            errors.append(key + ' missing/wrong')
    for key in ('KYTY_GPU_MARKERS', 'KYTY_GPU_CHECKPOINTS'):
        if str(env.get(key)) != '0':
            errors.append(key + ' must explicitly be 0')
    if str(meta.get('binary_sha256', '')).lower() != BINARY_SHA:
        errors.append('wrong/missing binary SHA')
    if meta.get('prereg', {}).get('sha256') != PRED_SHA or PRED_SHA == 'UNSEALED':
        errors.append('wrong/missing pre-registration SHA')
    try:
        base = (DEPS / 'gates_base.txt').read_bytes()
        if hashlib.sha256(base).hexdigest() != GATES_SHA or tokens(meta.get('gates', '')) != tokens(base.decode()):
            errors.append('wrong/missing baseline gates')
    except (OSError, ValueError, UnicodeError):
        errors.append('baseline gates unavailable/unparseable')
    schedule = meta.get('schedule')
    requested = None
    try:
        if schedule != env.get('KYTY_GATE_SCHEDULE') or not schedule.startswith('30+1800:'):
            raise ValueError('schedule metadata/env conflict or wrong period/start')
        requested = [tokens(x) for x in schedule.split(':', 1)[1].split('|')]
        if len(requested) != 2:
            raise ValueError('need two arms')
        if not isinstance(meta.get('arms'), list) or len(meta['arms']) != 2 or \
                [tokens(x) for x in meta['arms']] != requested:
            raise ValueError('metadata arms missing or contradict schedule')
        for arm, t in enumerate(requested):
            if set(t) != {'bindfloor', 'bfmode', 'bfburn', 'drawahead'}:
                raise ValueError('unexpected/missing explicit schedule keys')
            if t.get('bindfloor') != arm or t.get('bfmode') != 2:
                raise ValueError('both arms must explicitly request bfmode=2 and bindfloor=0|1')
            if not 0 < t.get('bfburn', 0) <= 30000:
                raise ValueError('burn outside (0,30000]')
            want_da = 0 if instrument == 'c' and arm == 1 else 1
            if t.get('drawahead') != want_da:
                raise ValueError('wrong drawahead for instrument ' + instrument)
        if requested[0]['bfburn'] != requested[1]['bfburn']:
            raise ValueError('burn differs between arms')
        if calibration and requested[0]['bfburn'] != 12000:
            raise ValueError('calibration initial burn must be 12000')
    except (ValueError, AttributeError, KeyError) as exc:
        errors.append(str(exc))
    with open(log, 'rb') as handle:
        for line in handle:
            frame = re.match(rb'^FrameTrace: n=(\d+)\b', line)
            if frame:
                dt = re.search(rb'\bdt_us=(-?\d+)\b', line)
                if dt is None or int(dt[1]) < 0 or int(frame[1]) in durations:
                    errors.append('raw duration row missing/negative/duplicate')
                else:
                    durations[int(frame[1])] = int(dt[1])
            if failure_marker(line):
                errors.append('forbidden hang/slow-wait/abort/fatal marker')
            for key, pattern in [('latch', rb'^BindFloorLatch: mode (\d+)'),
                                 ('clear', rb'^BindFloorClear: mode (\d+)'),
                                 ('pin', rb'^GpuClockPin: mode (\d+)')]:
                match = re.match(pattern, line)
                if match:
                    modes[key].add(int(match[1]))
            if not line.startswith(b'GateArm:'):
                continue
            match = H.L.GATEARM.fullmatch(line.rstrip(b'\r\n'))
            if not match:
                errors.append('malformed GateArm')
                continue
            arm, arms, block, frame, period, abba = map(int, match.groups()[:6])
            try:
                actual = tokens(match[7].decode())
            except (ValueError, UnicodeError) as exc:
                errors.append(str(exc)); continue
            if (arms, period, abba) != (2, 30, 1) or arm != (0, 1, 1, 0)[block % 4]:
                errors.append('actual protocol is not period-30 ABBA')
            if frame != 1800 + 30 * block:
                errors.append('GateArm frame/block mismatch')
            if requested is None or arm not in (0, 1) or actual != requested[arm]:
                errors.append('actual arm text differs from requested metadata')
            gates.append((block, arm))
    log_path = Path(log)
    if not log_path.name.startswith('log_'):
        errors.append('non-canonical raw log path; stdout provenance unknown')
    else:
        stdout_path = log_path.with_name('stdout_' + log_path.name[len('log_'):])
        if not stdout_path.is_file():
            errors.append('missing stdout provenance: ' + str(stdout_path))
        else:
            with stdout_path.open('rb') as handle:
                if any(failure_marker(line) for line in handle):
                    errors.append('forbidden failure marker in stdout: ' + str(stdout_path))
    if modes != {'latch': {1}, 'clear': {0}, 'pin': {1}}:
        errors.append('log latch/clear/pin missing, conflicting or wrong: ' + str(modes))
    if not gates or [b for b, _ in gates] != list(range(len(gates))):
        errors.append('GateArm blocks missing, duplicated, or not ordered from zero')
    wanted_hold = 180 if calibration else 300
    if meta.get('hold_s') != wanted_hold:
        errors.append('wrong requested hold')
    attempts = meta.get('attempts') or []
    expected_labels = ['attempt 1'] if calibration else ['warmup', 'attempt 1']
    if [a.get('label') for a in attempts] != expected_labels:
        errors.append('need exactly ' + str(expected_labels) + ', no retry')
    for a in attempts:
        if a.get('outcome') != 'ok' or 'hold_exit' not in a or a['hold_exit'] is not None \
                or not isinstance(a.get('hold_s'), (int, float)) or a['hold_s'] < wanted_hold - 5:
            errors.append('process did not survive full hold: ' + str(a.get('label')))
    duration_ok, _ = duration_evidence(meta, durations, warmup)
    if not duration_ok:
        errors.append('raw duration contradicts claimed hold or duration proof is missing')
    return sorted(set(errors)), dict(gates)


def duration_evidence(meta, durations, warmup=False):
    label = 'warmup' if warmup else 'attempt 1'
    selected = [a for a in meta.get('attempts', []) if a.get('label') == label]
    if len(selected) != 1 or not durations:
        return False, 'RAW_DURATION: missing attempt or frame durations'
    attempt = selected[0]
    hold = attempt.get('hold_s')
    if not isinstance(hold, (int, float)) or not math.isfinite(hold) or hold <= 0:
        return False, 'RAW_DURATION: invalid hold'
    total = sum(durations.values()) / 1e6
    stable = attempt.get('stable_frame')
    anchored = sum(dt for n, dt in durations.items() if n > stable) / 1e6 \
        if isinstance(stable, int) else None
    # Necessary only: the full raw log includes entry plus hold. No inferred
    # last-frame quantization allowance and no new stable-frame tolerance.
    return total >= hold, 'RAW_DURATION: whole=%.6f claimed=%.6f s; after_stable=%s [reported only]' % \
        (total, hold, 'absent' if anchored is None else '%.6f' % anchored)


def controls(rows, arms, instrument, first=2100):
    """Counter schema and transition integrity cover the whole log; only timing uses first."""
    tr = H.trim_sets(rows, arms)
    full = sorted(rows)
    window = [n for n in sorted(rows) if n >= first and rows[n].get('blk', 0) >= 1]
    a = [rows[n] for n in window if rows[n].get('arm') == 1 and n not in tr['ts']]
    u = [rows[n] for n in window if rows[n].get('arm') == 0 and n not in tr['ts']]
    missing = sorted({k for n in full for k in REQUIRED + ('arm', 'blk') if k not in rows[n]})
    used_blocks = sorted({r['blk'] for r in rows.values() if 'blk' in r})
    internal_missing = set(range(used_blocks[0], used_blocks[-1] + 1)) - set(used_blocks) if used_blocks else set()
    checks = {'COUNTERS': bool(window) and not missing,
              'EDGE': not tr['orphan'] and not tr['mismatch'] and bool(tr['e'])
              and not internal_missing
              and not any(tr['hist'].get(k, 0) for k in ('none', 'other', 'several'))}
    if missing or not a or not u:
        return {'checks': checks, 'missing': missing, 'B': None, 'trim': tr,
                'dt_a': None, 'dt_u': None}
    s = lambda seq, key: sum(r[key] for r in seq)
    sa = s(a, 'bf_n')
    bad, multi, _, _ = H.leak_structure(rows, window, 0, 'bf_n', tr['idx'], tr['e'])
    checks["C1'''"] = sa > 0 and s(u, 'bf_n') <= .001 * sa and not bad and not multi
    checks["C2'"] = sa > 0 and s(a, 'draws') > 0 and \
        abs(sa / s(a, 'draws') - 1) <= .02 and \
        s(a, 'bf_skip') <= .02 * sa and s(a, 'bf_skip_drop') <= .02 * sa
    checks['C4_B'] = s(a, 'bf_mat') == s(a, 'bf_reuse') == 0 and \
        sum(s(a, k) for k in LIVE) > 0
    if instrument == 'c':
        checks['C4_B_OUT'] = s(a, LIVE[0]) == 0 and sum(s(a, k) for k in LIVE[1:]) > 0
    # Fresh counters are only armed by mode2. Apply the SAME union-of-leaking-rows
    # rule as rv98 R4', including all old darkness keys, not one limit per key.
    dark_rows = {n: dict(r, live_dark=int(any(r.get(k, 0) for k in tuple(R.DARK98) + LIVE)))
                 for n, r in rows.items()}
    bad, multi, _, _ = H.leak_structure(dark_rows, full, 0, 'live_dark', tr['idx'], tr['e'])
    checks['DARK_B'] = not bad and not multi
    checks['LIVE_DARK_RATIO'] = all(s(u, k) <= .001 * s(a, k) for k in LIVE)
    checks['REAL_CLEARS'] = all(r.get('bf_clr_skip') == r.get('bf_skip_drop') == 0 for r in rows.values())
    checks['MARKERS_OFF'] = all(r.get('gm_ops') == 0 for r in rows.values())
    net = lambda rs: statistics.fmean(r['cpu_gpu_us'] - r['spin_gpu_us'] -
                                    r['bf_burn_ns'] / 1000 for r in rs)
    checks["C8''_B"] = net(a) < statistics.fmean(r['cpu_gpu_us'] - r['spin_gpu_us'] for r in u)
    dt_a, dt_u = statistics.fmean(r['dt_us'] for r in a), statistics.fmean(r['dt_us'] for r in u)
    checks["C9''_B"] = dt_u > 0 and abs(dt_a - dt_u) / dt_u <= .03
    bad, multi, _, _ = H.leak_structure(rows, window, 0, 'bf_burn_ns', tr['idx'], tr['e'])
    checks["C10'''_B"] = s(a, 'bf_burn_ns') > 0 and not bad and not multi and \
        s(u, 'bf_burn_ns') <= .001 * s(a, 'bf_burn_ns')
    ep = H.block_endpoint(rows, first, 1800, 1, True, tr['ts'])
    checks['PAIRS'] = ep['pairs'] >= 10
    checks['ENDPOINT'] = ep['F'] is not None and math.isfinite(ep['F']) and ep['F'] > 0 and ep['nF'] >= 2
    return {'checks': checks, 'missing': missing, 'B': ep['F'], 'trim': tr,
            'dt_a': dt_a, 'dt_u': dt_u, 'endpoint': ep, 'rows_a': len(a), 'rows_u': len(u)}


def invoke(module, argv):
    saved, sys.argv = sys.argv, argv
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                rc = module.main()
            except SystemExit as exc:
                rc = exc.code if isinstance(exc.code, int) else 1
                if isinstance(exc.code, str):
                    print(exc.code)
    finally:
        sys.argv = saved
    return rc, out.getvalue()


def fresh_area(tag, root):
    """Regenerate criterion 3 from this exact raw log; existing CSVs are never input."""
    with tempfile.TemporaryDirectory(prefix='kyty99_area_') as temp:
        csv_path = Path(temp) / ('area_' + tag + '.csv')
        try:
            rc, extracted = invoke(AS, ['area_series.py', tag, '--root', str(root), '--out', str(csv_path)])
            if rc != 0 or not csv_path.is_file():
                return 'RAW AREA EXTRACTION FAILED\n' + extracted
            _, verdict = invoke(AV, ['area_verdict.py', tag, '--first-frame', '2100', '--csv-root', temp])
            return 'RAW AREA (fresh temporary series; existing CSV ignored)\n' + extracted + verdict
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return 'RAW AREA EXTRACTION FAILED: %s\n' % exc


def legacy(tag, root):
    H.DECIDE.clear()
    H.bf96.CONTROLS.clear()
    raw_area = fresh_area(tag, root)
    old_tool = H.bf96.run_tool
    def tool(script, *args, **kwargs):
        return raw_area if script == 'area_verdict.py' else old_tool(script, *args, **kwargs)
    H.bf96.run_tool = tool
    try:
        _, out = invoke(H, ['bf98.py', tag, '--root', str(root), '--dry'])
    finally:
        H.bf96.run_tool = old_tool
    inherited = {str(k): v for k, v in H.bf96.CONTROLS}
    area = re.search(r'CRITERION 3: (\S+)', out)
    return out, {k: inherited.get(k, False) for k in KEEP}, area[1] if area else 'MISSING'


def reversibility(tag, root):
    R.RESULTS.clear(); R.SEALED_PRINTED.clear()
    old_find = R.L.find_log
    R.L.find_log = lambda t: str(root / ('log_' + t + '.txt'))
    try:
        _, out = invoke(R, ['rv98.py', tag, '--root', str(root), '--min-falling', '30', '--dry'])
    finally:
        R.L.find_log = old_find
    values = {str(k): v for k, v in R.RESULTS}
    return out, {k: values.get(k, False) for k in RV_KEEP}


def round_100(value):
    return (1 if value >= 0 else -1) * int(math.floor(abs(value) / 100 + .5)) * 100


def calibration_artifact(root, tag):
    return root / ('calibration-only-not-measurement_' + tag + '.json')


def calibration_binding(root, instrument, meta):
    """Bind the counted run to the accepted calibration and its unchanged source files."""
    tag = 'cal99' + instrument
    artifact = calibration_artifact(root, tag)
    errors = []
    try:
        data = json.loads(artifact.read_text(encoding='utf-8'))
        if data.get('status') != 'VALID_CALIBRATION_ONLY' or data.get('tag') != tag \
                or data.get('instrument') != instrument or data.get('pred_sha256') != PRED_SHA \
                or data.get('binary_sha256') != BINARY_SHA:
            errors.append('calibration artifact identity/status mismatch')
        for name, key in [(tag + '.json', 'metadata_sha256'), ('log_' + tag + '.txt', 'log_sha256'),
                          ('stdout_' + tag + '.txt', 'stdout_sha256')]:
            if hashlib.sha256((root / name).read_bytes()).hexdigest() != data.get(key):
                errors.append('calibration source changed: ' + name)
        cal_meta = json.loads((root / (tag + '.json')).read_text(encoding='utf-8'))
        pe, pa = protocol(cal_meta, root / ('log_' + tag + '.txt'), instrument, True)
        errors.extend('calibration: ' + x for x in pe)
        rows, _, _ = H.E84.scan(root / ('log_' + tag + '.txt'), REQUIRED)
        result = controls(rows, pa, instrument)
        errors.extend('calibration: ' + key for key, ok in result['checks'].items()
                      if not ok and key != "C9''_B")
        if result['dt_a'] is None or result['dt_u'] is None:
            errors.append('calibration means unavailable')
        else:
            candidate = 12000 + round_100(result['dt_u'] - result['dt_a'])
            if result['dt_a'] != data.get('dt_a_us') or result['dt_u'] != data.get('dt_u_us') \
                    or candidate != data.get('bfburn') or not 0 < candidate <= 30000:
                errors.append('calibration means/formula mismatch')
            actual = [tokens(t)['bfburn'] for t in meta['schedule'].split(':', 1)[1].split('|')]
            if actual != [candidate, candidate]:
                errors.append('measurement burn does not equal its calibration')
        # The saved VALID flag is not trusted alone: replay area, inherited controls and
        # this calibration process's rv98 criteria, without writing/overwriting artifacts.
        _, kept, area = legacy(tag, root)
        if area != 'VALID' or not all(kept.values()):
            errors.append('calibration legacy/area no longer admits source')
        _, rv = reversibility(tag, root)
        if not all(rv.values()):
            errors.append('calibration process reversibility failed')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('missing/invalid calibration artifact: ' + str(exc))
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tag')
    ap.add_argument('--root', type=Path, default=Path('C:/kyty/s99'))
    ap.add_argument('--instrument', choices=('a', 'c'), required=True)
    ap.add_argument('--mechanics-only', action='store_true')
    ap.add_argument('--calibration', action='store_true')
    args = ap.parse_args()
    root, tag = args.root.resolve(), args.tag
    if not args.mechanics_only and root != Path('C:/kyty/s99').resolve():
        print('ADMISSION: NOT ADMITTED (production artifacts belong to C:/kyty/s99)'); return 2
    if not re.fullmatch(r'[A-Za-z0-9_]+', tag):
        ap.error('tag must be a simple name')
    why = []
    got = hashlib.sha256(PRED.read_bytes()).hexdigest() if PRED.exists() else None
    seal_ok = PRED_SHA != 'UNSEALED' and got == PRED_SHA
    print('SEAL read=%s pinned=%s' % (got, PRED_SHA))
    if not seal_ok and not args.mechanics_only:
        print('ADMISSION: NOT ADMITTED (UNSEALED or changed pre-registration)'); return 2
    for path, expected in [(H.PRED98_2, H.PRED98_2_SHA), (R.PRED, R.PRED_SHA),
                           (R.PRED2, R.PRED2_SHA), (R.PRED98, R.PRED98_SHA),
                           (R.PRED01B, R.PRED01B_SHA), (H.bf96.PRED, H.bf96.PRED_SHA)]:
        if not Path(path).exists() or hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected:
            why.append('historical seal changed: ' + str(path))
    log, meta_file = root / ('log_' + tag + '.txt'), root / (tag + '.json')
    if not log.is_file() or not meta_file.is_file():
        print('ADMISSION: NOT ADMITTED (missing local log/metadata)'); return 1
    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except (ValueError, OSError) as exc:
        print('ADMISSION: NOT ADMITTED (invalid metadata: %s)' % exc); return 1
    errors, arms = protocol(meta, log, args.instrument, args.calibration)
    why.extend(errors)
    if not args.calibration and not args.mechanics_only and not errors:
        why.extend(calibration_binding(root, args.instrument, meta))
    rows, _, _ = H.E84.scan(log, REQUIRED)
    print(duration_evidence(meta, {n: r['dt_us'] for n, r in rows.items() if 'dt_us' in r})[1])
    result = controls(rows, arms, args.instrument)
    historical, kept, area = legacy(tag, root)
    if args.calibration:
        if not args.mechanics_only:
            artifact = root / ('calibration-only-not-measurement_' + tag + '_legacy.txt')
            try:
                with artifact.open('x', encoding='utf-8') as handle:
                    handle.write(historical)
            except FileExistsError:
                why.append('calibration artifact exists; refusal to overwrite')
            print('LEGACY full calibration-only artifact: ' + str(artifact))
        print('LEGACY calibration numeric/branch sections suppressed; controls and area follow')
        selected = [line for line in historical.splitlines() if
                    re.search(r'\bC(?:\d|RITERION)|\b(?:PASS|FAIL)\b', line) and
                    not any(x in line for x in ('F_st', 'VERDICT', 'CLOSED', 'PROCEED'))]
    else:
        selected = historical.splitlines()
    for line in selected:
        print('bf98 REPORTED ONLY| ' + line)
    checks = dict(result['checks'])
    checks.update({'inherited C' + k: v for k, v in kept.items()})
    checks['AREA'] = area == 'VALID'
    if args.calibration:
        print('C9 calibration-only: REPORTED, not deciding')
        checks.pop("C9''_B", None)
    for current in [tag] + ([] if args.calibration else [tag + '_warmup']):
        warm_log = root / ('log_' + current + '.txt')
        if not warm_log.exists():
            why.append('missing warmup log: ' + current); continue
        if current != tag:
            pe, pa = protocol(meta, warm_log, args.instrument, False, True)
            why.extend('warmup: ' + x for x in pe)
            wr, _, _ = H.E84.scan(warm_log, REQUIRED)
            print('warmup ' + duration_evidence(meta, {n: r['dt_us'] for n, r in wr.items()
                                                      if 'dt_us' in r}, True)[1])
            wc = controls(wr, pa, args.instrument)
            # Warmup is not a second measurement. Check its new counter identity and
            # boundary integrity; rv98 below checks every survival/reversibility rule.
            for k in ('COUNTERS', 'EDGE', 'C4_B', 'C4_B_OUT', 'DARK_B', 'LIVE_DARK_RATIO',
                      'REAL_CLEARS', 'MARKERS_OFF'):
                if k in wc['checks']:
                    checks['warmup ' + k] = wc['checks'][k]
        rout, rv = reversibility(current, root)
        for line in rout.splitlines():
            print('rv98 THIS PROCESS| ' + line)
        checks.update({current + ' R' + k: v for k, v in rv.items()})
    for key, ok in checks.items():
        print('CONTROL99 %s %s' % (key, 'PASS' if ok else 'FAIL'))
    why.extend(key for key, ok in checks.items() if not ok)
    if result['missing']:
        print('MISSING COUNTERS: ' + ', '.join(result['missing']))
    if 'endpoint' in result:
        print('MATCHED_PAIRS99 %d; edge histogram %s; T* rows %d' %
              (result['endpoint']['pairs'], result['trim']['hist'], len(result['trim']['ts'])))
    if args.calibration and result['dt_a'] is not None:
        delta = result['dt_u'] - result['dt_a']
        candidate = 12000 + round_100(delta)
        print('CALIBRATION dt_U=%.3f dt_A=%.3f delta=%.3f us' %
              (result['dt_u'], result['dt_a'], delta))
        if not 0 < candidate <= 30000:
            why.append('calibrated burn outside (0,30000]; no clamp, STOP')
        if not why:
            print('CALIBRATION_CANDIDATE bfburn=%d (half-away-from-zero; no auto-run)' % candidate)
    if args.mechanics_only:
        why.append('MECHANICS ONLY: not a scoring')
    if why:
        print('ADMISSION: NOT ADMITTED (%s)' % '; '.join(why)); return 1
    if args.calibration:
        artifact = calibration_artifact(root, tag)
        data = {'status': 'VALID_CALIBRATION_ONLY', 'tag': tag, 'instrument': args.instrument,
                'pred_sha256': PRED_SHA, 'binary_sha256': BINARY_SHA,
                'dt_u_us': result['dt_u'], 'dt_a_us': result['dt_a'], 'bfburn': candidate,
                'matched_pairs': result['endpoint']['pairs'],
                'metadata_sha256': hashlib.sha256(meta_file.read_bytes()).hexdigest(),
                'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest(),
                'stdout_sha256': hashlib.sha256((root / ('stdout_' + tag + '.txt')).read_bytes()).hexdigest()}
        try:
            with artifact.open('x', encoding='utf-8') as handle:
                json.dump(data, handle, indent=2); handle.write('\n')
        except FileExistsError:
            print('ADMISSION: NOT ADMITTED (calibration artifact exists; no overwrite)'); return 1
        print('CALIBRATION_ARTIFACT ' + str(artifact))
        print('CALIBRATION: VALID (no F or architecture verdict)')
    else:
        print("B_st'' = %.9f ms" % result['B'])
        print('INSTRUMENT99 = ' + args.instrument)
        print('BINARY99 = ' + meta['binary_sha256'])
        print('ADMISSION: ADMITTED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
