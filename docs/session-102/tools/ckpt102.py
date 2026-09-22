"""Session 102, candidate 1 scorer (the VALUE, not the presence, of KYTY_GPU_CHECKPOINTS), sealed to
pred/04_checkpoints_fix.md.

    python C:/kyty/s102/ckpt102.py ckpt102 --out <json> [--root C:/kyty/s102] [--no-reference]
    python C:/kyty/s102/ckpt102.py <tag> --root <any> --control [--out <json>]   # never decides
    python C:/kyty/s102/ckpt102.py <tag> --root <any> --mechanics-only           # never decides

Offline only: never launches the game, never rebuilds, never overwrites an output (mode 'x'; an
existing --out is refused before any work).  Refuses to score when pred/04 is not byte-for-byte the
sealed text (sha256 c131852e..., 4 221 B).

pred/04 2, on the witness run ckpt102, frames from 2100 to the end of the hold, medians over rows
of the main and draw lines:
  1. 'Vulkan: GPU checkpoints off (KYTY_GPU_CHECKPOINTS=0)' exactly once, no
     'Vulkan: GPU checkpoints mode=' line, no 'diagnostic checkpoints enabled' line;
  2. 'RecordThread: started' >= 1;
  3. median rec_n >= 9 000            (rec_n lives on FrameTrace-draw);
  4. median gpu_busy_us <= 16 000     (FrameTrace main line);
  5. median dt_us <= 40 000           (FrameTrace main line);
  6. no GpuHangAbort, no fatal marker, 'GpuClockPin: mode 1' once.
Any failure => the fix is NOT accepted.

Conventions this file fixes because the seal does not spell them out:
  * "End of the hold": the last main-line frame whose cumulative dt_us, counted from the frame
    after the attempt's stable_frame, stays <= hold_s x 1e6 (meta attempts[0]); the whole-log
    medians are printed beside and never decide.  A row is a frame carrying BOTH the main and the
    draw line in that window; a window without rows fails items 3-5.
  * Line counts are over the log AND the stdout, every line (substring match).
  * "Fatal marker" = the session-101 scorer's set (cen100.FATAL minus GpuHangAbort, which item 6
    names separately): '--- Error ---', '--- Fatal Error ---', '--- std::terminate ---',
    '--- abort() ---', ErrorDeviceLost, 'Unhandled exception:', 'GpuWaitSlow:',
    'AsyncPipelines: skipped draw'.
  * 'GpuClockPin: mode 1' once = exactly one such line and no GpuClockPin line of another mode.
  * The witness protocol of pred/04 1 decides too (same environment string: KYTY_GPU_CHECKPOINTS
    present and '0', KYTY_GPU_CLOCK_PIN=1, KYTY_GPU_MARKERS=0, no schedule, gates_base.txt, one
    attempt, hold 180 s, the prereg is pred/04, the sealed binary 346ba4f6..., and at scoring time
    the installed exe is that binary).  A protocol failure makes the run no witness: NOT accepted.
  * The A arm cm101a (C:/kyty/s101) is scored with the same item code and printed for the report;
    it never decides.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PRODUCTION_ROOT = 'C:/kyty/s102'
PRED = 'C:/kyty/s102/pred/04_checkpoints_fix.md'
PRED_SHA = 'c131852e4b3a5c979ce93d2c4182849b641bcc53ce1f217373926de369e8fe87'
PRED_BYTES = 4221
BINARY_SHA = '346ba4f6448c35cba8677101a1599c6ddd0b907d3ea76015ada692cd3b3dc776'
EXE = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
GATES_FILE = 'C:/kyty/s102/gates_base.txt'
GATES_SHA = '00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8'
REFERENCE = ('C:/kyty/s101', 'cm101a')
FIRST_FRAME = 2100
HOLD = 180
REC_N_MIN = 9000.0
GPU_BUSY_MAX = 16000.0
DT_MAX = 40000.0

OFF_LINE = b'Vulkan: GPU checkpoints off (KYTY_GPU_CHECKPOINTS=0)'
MODE_LINE = b'Vulkan: GPU checkpoints mode='
DIAG_LINE = b'diagnostic checkpoints enabled'
STARTED = b'RecordThread: started'
HANG = b'GpuHangAbort'
FATAL = (b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---',
         b'ErrorDeviceLost', b'Unhandled exception:', b'GpuWaitSlow:',
         b'AsyncPipelines: skipped draw')
RE_PIN = re.compile(rb'GpuClockPin: mode (\d+)')
RE_N = re.compile(rb' n=(\d+)')
MAIN_FIELDS = {b'dt_us': re.compile(rb' dt_us=(-?\d+)'),
               b'gpu_busy_us': re.compile(rb' gpu_busy_us=(-?\d+)')}
DRAW_FIELDS = {b'rec_n': re.compile(rb' rec_n=(-?\d+)')}
ENV_EXPECTED = {'KYTY_GPU_CHECKPOINTS': '0', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0',
                'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_QUEUE_TRACE': '1',
                'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden'}
ENV_PRESENT = ('KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE')


class SealError(RuntimeError):
    pass


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_seal(path=None, want_sha=None, want_bytes=None):
    # Defaults are resolved at CALL time (module globals), never frozen at definition time.
    path = PRED if path is None else path
    want_sha = PRED_SHA if want_sha is None else want_sha
    want_bytes = PRED_BYTES if want_bytes is None else want_bytes
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise SealError('sealed pre-registration unreadable: %s (%s)' % (path, exc))
    got = hashlib.sha256(data).hexdigest()
    if got != want_sha or len(data) != want_bytes:
        raise SealError('SEALED PRE-REGISTRATION CHANGED: %s sha256 %s (%d B), sealed %s (%d B)'
                        % (path, got, len(data), want_sha, want_bytes))
    return got


def new_counts():
    return {'off': 0, 'mode': 0, 'diag': 0, 'started': 0, 'hang': 0, 'fatal': {}, 'pin': {},
            'gatearm': 0, 'off_any': 0}


def scan_markers(line, c):
    if OFF_LINE in line:
        c['off'] += 1
    if b'GPU checkpoints off' in line:
        c['off_any'] += 1
    if MODE_LINE in line:
        c['mode'] += 1
    if DIAG_LINE in line:
        c['diag'] += 1
    if STARTED in line:
        c['started'] += 1
    if HANG in line:
        c['hang'] += 1
    for marker in FATAL:
        if marker in line:
            key = marker.decode()
            c['fatal'][key] = c['fatal'].get(key, 0) + 1
    if b'GpuClockPin:' in line:
        m = RE_PIN.search(line)
        mode = m.group(1).decode() if m else '?'
        c['pin'][mode] = c['pin'].get(mode, 0) + 1
    if line.startswith(b'GateArm:'):
        c['gatearm'] += 1


def read_run(log_path, stdout_path):
    """Streaming: main rows {n: {dt_us, gpu_busy_us}}, draw rows {n: {rec_n}}, main order, counts."""
    main, draw, order, bad = {}, {}, [], []
    counts = new_counts()
    with open(log_path, 'rb') as handle:
        for raw in handle:
            scan_markers(raw, counts)
            if raw.startswith(b'FrameTrace: '):
                table, fields, kind = main, MAIN_FIELDS, 'main'
            elif raw.startswith(b'FrameTrace-draw: '):
                table, fields, kind = draw, DRAW_FIELDS, 'draw'
            else:
                continue
            m = RE_N.search(raw)
            if m is None:
                continue
            n = int(m.group(1))
            row = {}
            for name, rx in fields.items():
                hit = rx.search(raw)
                if hit is None:
                    bad.append((kind, n, name.decode()))
                    row = None
                    break
                row[name.decode()] = int(hit.group(1))
            if row is not None:
                table[n] = row
            if kind == 'main':
                order.append(n)
    if stdout_path is not None and Path(stdout_path).is_file():
        with open(stdout_path, 'rb') as handle:
            for raw in handle:
                scan_markers(raw, counts)
    return main, draw, order, bad, counts


def hold_end(main, order, meta):
    """Last main frame whose cumulative dt from stable_frame+1 is <= hold_s x 1e6."""
    attempts = (meta or {}).get('attempts') or []
    if not attempts or attempts[0].get('stable_frame') is None or not attempts[0].get('hold_s'):
        return None, 'no stable_frame/hold_s in meta: window runs to the last frame'
    stable, hold_s = attempts[0]['stable_frame'], attempts[0]['hold_s']
    cum, end = 0, None
    for n in sorted(main):
        if n <= stable:
            continue
        cum += main[n]['dt_us']
        if cum <= hold_s * 1e6:
            end = n
        else:
            break
    return end, 'stable_frame %d, hold_s %s' % (stable, hold_s)


def median_or_none(values):
    values = list(values)
    return statistics.median(values) if values else None


def items(root, tag):
    """pred/04 2 items 1-6 on one run directory.  Never decides by itself."""
    root = Path(root)
    log = root / ('log_%s.txt' % tag)
    stdout = root / ('stdout_%s.txt' % tag)
    meta_path = root / ('%s.json' % tag)
    res = {'tag': tag, 'root': str(root), 'inputs_missing': []}
    for p in (log,):
        if not p.is_file():
            res['inputs_missing'].append(str(p))
    if res['inputs_missing']:
        res['items'] = {str(i): False for i in range(1, 7)}
        return res, None
    meta = None
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
    res['raw_sha256'] = {'log': sha256_file(log),
                         'stdout': sha256_file(stdout) if stdout.is_file() else None,
                         'meta': sha256_file(meta_path) if meta_path.is_file() else None}
    main, draw, order, bad, c = read_run(log, stdout if stdout.is_file() else None)
    res['counts'] = c
    res['schema_bad'] = [list(x) for x in bad[:20]]
    res['schema_bad_n'] = len(bad)
    end, how = hold_end(main, order, meta)
    last = max(main) if main else None
    res['window'] = {'first': FIRST_FRAME, 'hold_end': end, 'last_main_frame': last, 'how': how}
    stop = end if end is not None else last
    win = [n for n in sorted(main) if FIRST_FRAME <= n <= (stop or -1) and n in draw]
    res['window']['rows'] = len(win)
    res['window']['main_without_draw'] = sum(1 for n in main
                                             if FIRST_FRAME <= n <= (stop or -1) and n not in draw)
    med = {'rec_n': median_or_none(draw[n]['rec_n'] for n in win),
           'gpu_busy_us': median_or_none(main[n]['gpu_busy_us'] for n in win),
           'dt_us': median_or_none(main[n]['dt_us'] for n in win)}
    everything = [n for n in sorted(main) if n >= FIRST_FRAME and n in draw]
    res['medians'] = med
    res['medians_to_end_of_log_reported'] = {
        'rows': len(everything),
        'rec_n': median_or_none(draw[n]['rec_n'] for n in everything),
        'gpu_busy_us': median_or_none(main[n]['gpu_busy_us'] for n in everything),
        'dt_us': median_or_none(main[n]['dt_us'] for n in everything)}
    it = {}
    it['1'] = c['off'] == 1 and c['mode'] == 0 and c['diag'] == 0
    it['2'] = c['started'] >= 1
    it['3'] = med['rec_n'] is not None and med['rec_n'] >= REC_N_MIN
    it['4'] = med['gpu_busy_us'] is not None and med['gpu_busy_us'] <= GPU_BUSY_MAX
    it['5'] = med['dt_us'] is not None and med['dt_us'] <= DT_MAX
    it['6'] = (c['hang'] == 0 and not c['fatal'] and c['pin'].get('1', 0) == 1
               and sum(c['pin'].values()) == 1)
    res['items'] = it
    res['item_text'] = {
        '1': "'GPU checkpoints off (KYTY_GPU_CHECKPOINTS=0)' x%d (need 1), 'mode=' x%d, "
             "'diagnostic checkpoints enabled' x%d (need 0 each)" % (c['off'], c['mode'], c['diag']),
        '2': "'RecordThread: started' x%d (need >= 1)" % c['started'],
        '3': 'median rec_n %s (need >= %d)' % (med['rec_n'], REC_N_MIN),
        '4': 'median gpu_busy_us %s (need <= %d)' % (med['gpu_busy_us'], GPU_BUSY_MAX),
        '5': 'median dt_us %s (need <= %d)' % (med['dt_us'], DT_MAX),
        '6': 'GpuHangAbort x%d, fatal %s, GpuClockPin modes %s (need mode 1 once only)'
             % (c['hang'], c['fatal'] or '{}', c['pin'])}
    return res, meta


def protocol(meta, counts, gates_file=GATES_FILE):
    errors = []
    err = errors.append
    if meta is None:
        return ['no <tag>.json']
    env = meta.get('env') or {}
    kyty = {k: v for k, v in env.items() if k.startswith('KYTY_')}
    for key, value in ENV_EXPECTED.items():
        if kyty.get(key) != value:
            err('env %s=%r, expected %r' % (key, kyty.get(key), value))
    for key in ENV_PRESENT:
        if key not in kyty:
            err('env %s absent' % key)
    extra = sorted(set(kyty) - set(ENV_EXPECTED) - set(ENV_PRESENT))
    if extra:
        err('env carries KYTY_* variables outside the sealed witness launch: %s' % extra)
    if meta.get('schedule'):
        err('meta schedule %r: pred/04 1 runs without a schedule' % meta.get('schedule'))
    if counts.get('gatearm'):
        err('%d GateArm lines in the log: the witness runs without a schedule' % counts['gatearm'])
    try:
        gates_text = ' '.join(Path(gates_file).read_text(encoding='utf-8').split())
        gates_sha = sha256_file(gates_file)
    except OSError:
        gates_text, gates_sha = None, None
    if gates_sha != GATES_SHA:
        err('gates_base.txt sha256 %s, expected %s' % (gates_sha, GATES_SHA))
    if meta.get('gates') != gates_text:
        err('meta gates text is not gates_base.txt')
    prereg = meta.get('prereg') or {}
    if prereg.get('sha256') != PRED_SHA or prereg.get('bytes') != PRED_BYTES:
        err('prereg %r is not pred/04 (%s, %d B)' % (prereg.get('sha256'), PRED_SHA, PRED_BYTES))
    if meta.get('binary_sha256') != BINARY_SHA:
        err('binary %r is not the sealed %s' % (meta.get('binary_sha256'), BINARY_SHA))
    attempts = meta.get('attempts') or []
    if [a.get('label') for a in attempts] != ['attempt 1']:
        err('attempts are %r, expected exactly [attempt 1]' % ([a.get('label') for a in attempts],))
    for a in attempts:
        if a.get('outcome') != 'ok':
            err('attempt outcome %r' % a.get('outcome'))
        if a.get('hold_exit') is not None:
            err('the game ended inside the hold (hold_exit=%r)' % a.get('hold_exit'))
        if (a.get('hold_s') or 0) < HOLD - 5:
            err('hold_s %r below %d' % (a.get('hold_s'), HOLD - 5))
    if meta.get('hold_s') != HOLD:
        err('meta hold_s %r, expected %d' % (meta.get('hold_s'), HOLD))
    return errors


def evaluate(root, tag, control=False, mechanics=False, seal_path=None, gates_file=GATES_FILE,
             reference=None):
    check_seal(seal_path)
    res, meta = items(root, tag)
    out = {'scorer': 'ckpt102.py', 'pred': PRED, 'pred_sha256': PRED_SHA, 'pred_bytes': PRED_BYTES,
           'control': bool(control), 'mechanics_only': bool(mechanics)}
    out.update(res)
    out['protocol_errors'] = protocol(meta, res.get('counts') or {}, gates_file)
    out['binary_sha256'] = (meta or {}).get('binary_sha256')
    failed_items = sorted(k for k, v in res['items'].items() if not v)
    out['failed_items'] = failed_items
    if control:
        out['status'] = 'CONTROL_ONLY'
        out['verdict'] = None
    else:
        ok = not failed_items and not out['protocol_errors'] and not res['inputs_missing']
        if ok and mechanics:
            out['status'] = 'MECHANICS_ONLY'
            out['verdict'] = None
        else:
            out['status'] = 'ACCEPTED' if ok else 'NOT_ACCEPTED'
            out['verdict'] = ('fix ACCEPTED: every line of pred/04 2 holds' if ok else
                              'fix NOT accepted: %s' % ', '.join(
                                  ['item %s' % k for k in failed_items]
                                  + (['protocol'] if out['protocol_errors'] else [])
                                  + (['inputs'] if res['inputs_missing'] else [])))
    if reference is not None:
        ref_res, _ = items(*reference)
        out['reference'] = {'role': 'A arm of pred/04 1, printed for the report, NEVER deciding',
                            'tag': ref_res['tag'], 'root': ref_res['root'],
                            'items': ref_res['items'], 'item_text': ref_res.get('item_text'),
                            'medians': ref_res.get('medians'), 'window': ref_res.get('window'),
                            'counts': ref_res.get('counts')}
    out['does_not_show'] = ('that any truthy value still enables checkpoints; that any other '
                            'converted variable behaves as intended; any speedup (pred/04 3)')
    return out


def summary(out):
    lines = ['ckpt102.py %s (root %s) status=%s' % (out['tag'], out['root'], out['status'])]
    for e in out.get('protocol_errors', []):
        lines.append('  PROTOCOL: %s' % e)
    w = out.get('window') or {}
    lines.append('  window n %s..%s (%s), rows %s, main-without-draw %s'
                 % (w.get('first'), w.get('hold_end'), w.get('how'), w.get('rows'),
                    w.get('main_without_draw')))
    for k in sorted(out['items']):
        lines.append('  item %s [%s] %s' % (k, 'PASS' if out['items'][k] else 'FAIL',
                                           (out.get('item_text') or {}).get(k, '')))
    lines.append('  to end of log (reported): %s' % out.get('medians_to_end_of_log_reported'))
    if out.get('verdict'):
        lines.append('  VERDICT: %s' % out['verdict'])
    ref = out.get('reference')
    if ref:
        lines.append('  reference %s (never deciding): medians %s' % (ref['tag'], ref['medians']))
        for k in sorted(ref['items']):
            lines.append('    ref item %s [%s] %s' % (k, 'PASS' if ref['items'][k] else 'FAIL',
                                                     (ref.get('item_text') or {}).get(k, '')))
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('tag')
    ap.add_argument('--root', default=PRODUCTION_ROOT)
    ap.add_argument('--out')
    ap.add_argument('--control', action='store_true',
                    help='score items on any run for comparison; never decides')
    ap.add_argument('--mechanics-only', action='store_true')
    ap.add_argument('--no-reference', action='store_true')
    ap.add_argument('--json', action='store_true')
    options = ap.parse_args(argv)
    try:
        check_seal()
    except SealError as exc:
        print(str(exc) + ': refusing to score')
        return 2
    free = options.control or options.mechanics_only
    production = Path(options.root).as_posix().rstrip('/') == PRODUCTION_ROOT
    if not free:
        if not production:
            print('production root must be %s (use --control or --mechanics-only elsewhere)'
                  % PRODUCTION_ROOT)
            return 2
        if re.fullmatch(r'ckpt102(?:_entry1)?', options.tag) is None:
            print('tag %r is not the pred/04 witness tag' % options.tag)
            return 2
    if options.out:
        path = Path(options.out)
        if path.exists():
            print('output %s exists: never overwritten' % path)
            return 2
        if not free and not path.as_posix().startswith(PRODUCTION_ROOT + '/'):
            print('output must live under %s' % PRODUCTION_ROOT)
            return 2
    reference = None if (options.no_reference or options.control) else REFERENCE
    try:
        result = evaluate(options.root, options.tag, control=options.control,
                          mechanics=options.mechanics_only, reference=reference)
    except SealError as exc:
        print(str(exc) + ': refusing to score')
        return 2
    if not free:
        exe_sha = sha256_file(EXE) if Path(EXE).is_file() else None
        result['installed_exe_sha256'] = exe_sha
        identity = exe_sha == result.get('binary_sha256') == BINARY_SHA
        result['identity_installed_exe'] = identity
        if not identity:
            result['protocol_errors'].append('IDENTITY: installed exe %s, run %s, sealed %s'
                                             % (exe_sha, result.get('binary_sha256'), BINARY_SHA))
            result['status'] = 'NOT_ACCEPTED'
            result['verdict'] = 'fix NOT accepted: %s' % ', '.join(
                ['item %s' % k for k in result['failed_items']] + ['protocol'])
    print(summary(result))
    text = json.dumps(result, indent=2, sort_keys=True, default=str)
    if options.json:
        print(text)
    if options.out:
        with open(options.out, 'x', encoding='utf-8') as handle:
            handle.write(text + '\n')
        print('wrote %s' % options.out)
    if options.control:
        return 0
    return 0 if result['status'] in ('ACCEPTED', 'MECHANICS_ONLY') else 1


if __name__ == '__main__':
    raise SystemExit(main())
