"""Session 114, pred/01_ctl114.md (ROADMAP §0.1 "СЕССИЯ 114" items 2, 4, 5): the positive control of knob `titleasync`.
Two Sky Garden entries, 180 s, pinned, KYTY_MAIN_STALL_TEST=3000:3000 (at the 3000th UpdateTitle call the present
thread queues a 3-s sleep on the SDL main thread): ctl114a with titleasync=0 (gates_title0.txt), ctl114b with
titleasync=1 (gates_title1.txt).  The stall window of a run = the first three `FrameTrace: n=` rows after the line
`MainStallTest: queued`.
    PASS           both runs admitted; ctl114a froze (max dt_us of its window >= FREEZE_US and a `MainThreadWait:` line
                   with frame=STALL_FRAME and us >= FREEZE_US); ctl114b did not (max dt_us of its window <= CALM_US, no
                   `GpuWaitSlow`, and a `MainTaskLate:` line with us >= FREEZE_US - the main thread really slept)
    FAIL           both admitted, anything else
    NOT_ADMITTED   an admission term of either run fails
`GpuWaitSlow` is expected in ctl114a (a 3-s wait on the recording tick) and is not a marker there.

    python C:/kyty/s114/ctl114.py [--root C:/kyty/s114] [--out <json>]
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = 'C:/kyty/s114'
TAGS = ('ctl114a', 'ctl114b')
ASYNC = {'ctl114a': 0, 'ctl114b': 1}
PRED = 'C:/kyty/s114/pred/01_ctl114.md'
PRED_SHA = 'ac16a32a31fc2ea4876ae941b205bcc8179cecb845205d2a5a785a40f7b5d76b'   # pred/01_ctl114.md sealed
PRED_BYTES = 4667       # pred/01_ctl114.md sealed
BINARY_SHA = '916f64898a5a31c697ad0d823f0795850acc160cf56271b566e8ae330c7c3b2c'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
STALL_ENV = '3000:3000'
STALL_FRAME = 3000
HOLD_S = 180
MIN_ROWS = 1000
WINDOW = 3
FREEZE_US = 2500000
CALM_US = 500000
MAX_GPU_UTIL = 10.0
FORBIDDEN_ENV = ('KYTY_GATE_SCHEDULE', 'KYTY_GPU_CHECKPOINTS', 'KYTY_REC', 'KYTY_PIPELINE_PRECACHE',
                 'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB', 'KYTY_TITLE_ASYNC')
MARKERS = (b'gpuhangabort', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost', b'std::terminate',
           b'abort()', b'fatal', b'unhandled exception', b'--- error ---', b'asyncpipelines: skipped draw')
MAIN_ROW = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
TRIGGER = b'MainStallTest: frame=%d ms=3000' % STALL_FRAME
QUEUED = b'MainStallTest: queued frame=%d ms=3000' % STALL_FRAME
WAIT_LINE = re.compile(rb'^MainThreadWait: us=(\d+) frame=(\d+) titleasync=(\d+)')
LATE_LINE = re.compile(rb'^MainTaskLate: us=(\d+)')
SLOW = b'GpuWaitSlow:'


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def is_marker(line):
    low = line.lower()
    return any(k in low for k in MARKERS)


def evaluate_run(root, tag):
    out = dict(tag=tag)
    errors = []
    meta_p, log_p = Path(root) / (tag + '.json'), Path(root) / ('log_%s.txt' % tag)
    if not meta_p.is_file() or not log_p.is_file():
        out.update(errors=['INPUTS'])
        return out
    meta = json.loads(meta_p.read_text(encoding='utf-8'))
    env = meta.get('env') or {}
    if meta.get('binary_sha256') != BINARY_SHA:
        errors.append('BINARY')
    pre = meta.get('prereg') or {}
    if pre.get('sha256') != PRED_SHA or pre.get('bytes') != PRED_BYTES:
        errors.append('PREREG')
    if env.get('KYTY_GPU_CLOCK_PIN') != '1':
        errors.append('ENV_PIN')
    if env.get('KYTY_MAIN_STALL_TEST') != STALL_ENV:
        errors.append('ENV_STALL')
    if any(k in env for k in FORBIDDEN_ENV):
        errors.append('ENV_FORBIDDEN')
    gates = ' ' + ' '.join((meta.get('gates') or '').split())
    if not gates.endswith(' titleasync=%d' % ASYNC[tag]) or gates.count(' titleasync=') != 1:
        errors.append('GATES')
    att = meta.get('attempts') or []
    ok_att = [a for a in att if a.get('outcome') == 'ok' and a.get('hold_exit') is None]
    if len(att) != 1 or len(ok_att) != 1 or (att[0].get('hold_s') or 0) < 0.95 * HOLD_S:
        errors.append('ATTEMPT')
    pr = meta.get('pre_run') or {}
    if not isinstance(pr.get('gpu_util_median'), (int, float)) or pr['gpu_util_median'] > MAX_GPU_UTIL:
        errors.append('PRE_RUN')
    pins = pin1 = markers = rows = triggers = queued = slow = 0
    window = []
    after_queued = False
    waits = []
    lates = []
    with open(log_p, 'rb') as f:
        for line in f:
            if line.startswith(b'GpuClockPin:'):
                pins += 1
                pin1 += int(line.startswith(b'GpuClockPin: mode 1'))
            if is_marker(line):
                markers += 1
            if line.startswith(SLOW):
                slow += 1
            if line.startswith(TRIGGER):
                triggers += 1
            if line.startswith(QUEUED):
                queued += 1
                after_queued = True
            m = WAIT_LINE.match(line)
            if m:
                waits.append((int(m.group(1)), int(m.group(2))))
            m = LATE_LINE.match(line)
            if m:
                lates.append(int(m.group(1)))
            m = MAIN_ROW.match(line)
            if m:
                rows += 1
                if after_queued and len(window) < WINDOW:
                    window.append((int(m.group(1)), int(m.group(2))))
    so = Path(root) / ('stdout_%s.txt' % tag)
    if so.is_file():
        with open(so, 'rb') as f:
            for line in f:
                if is_marker(line):
                    markers += 1
    if pins != 1 or pin1 != 1:
        errors.append('PIN_ONCE')
    if markers:
        errors.append('NO_MARKER')
    if rows < MIN_ROWS:
        errors.append('ROWS')
    if triggers != 1 or queued != 1:
        errors.append('TRIGGER')
    if len(window) < WINDOW:
        errors.append('STALL_ROWS')
    stall_waits = [us for us, frame in waits if frame == STALL_FRAME]
    out.update(errors=errors, rows=rows, window=window, max_dt=max((dt for _, dt in window), default=None),
               gpuwaitslow=slow, main_wait_max_us=max(stall_waits, default=0), main_late_max_us=max(lates, default=0),
               main_wait_lines=len(waits), main_late_lines=len(lates))
    return out


def evaluate(root=ROOT, installed_sha=None):
    res = dict(scorer_sha256=sha_file(__file__), pred=PRED, pred_sha256=PRED_SHA)
    errors = []
    if PRED_SHA is None or PRED_BYTES is None:
        errors.append('DRAFT')
    elif not Path(PRED).is_file() or sha_file(PRED) != PRED_SHA or Path(PRED).stat().st_size != PRED_BYTES:
        errors.append('SEAL')
    if installed_sha is None:
        installed_sha = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    if installed_sha != BINARY_SHA:
        errors.append('IDENTITY')
    runs = {tag: evaluate_run(root, tag) for tag in TAGS}
    res.update(errors=errors, runs=runs)
    if errors or any(r['errors'] for r in runs.values()):
        res['verdict'] = 'NOT_ADMITTED'
        return res
    a, b = runs['ctl114a'], runs['ctl114b']
    checks = dict(a_froze=a['max_dt'] >= FREEZE_US,
                  a_waited_main=a['main_wait_max_us'] >= FREEZE_US,
                  b_calm=b['max_dt'] <= CALM_US,
                  b_no_slow=b['gpuwaitslow'] == 0,
                  b_main_slept=b['main_late_max_us'] >= FREEZE_US)
    res['checks'] = checks
    res['verdict'] = 'PASS' if all(checks.values()) else 'FAIL'
    return res


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    res = evaluate(root)
    print('  errors %s' % (res['errors'] or 'none'))
    for tag, r in res['runs'].items():
        print('  %s errors %s rows %s window %s max_dt %s GpuWaitSlow %s MainThreadWait(frame %d) max %s us, '
              'MainTaskLate max %s us' % (tag, r.get('errors') or 'none', r.get('rows'), r.get('window'), r.get('max_dt'),
                                         r.get('gpuwaitslow'), STALL_FRAME, r.get('main_wait_max_us'),
                                         r.get('main_late_max_us')))
    for k, v in (res.get('checks') or {}).items():
        print('  check %-16s %s' % (k, 'PASS' if v else 'FAIL'))
    print('  scorer %s' % res['scorer_sha256'])
    print('VERDICT: %s' % res['verdict'])
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] in ('PASS', 'FAIL') else 1


if __name__ == '__main__':
    sys.exit(main())
