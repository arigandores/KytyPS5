"""Session 113, pred/01e_vbn113e.md (from vbn113d.py by make_vbn113e.py - ROADMAP item 17: the same verify run with the
buffer-GC trigger lowered by KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024, a forced OLD regime; vbn113d.py came from vbn113c.py
by make_vbn113d.py): the verify run of knob `bdanarrow` in mode 2 (today's global invalidation of the BDA
region stamps on a buffer registration, plus a check of every region mode 1 would have skipped: bda_nwould, and those
whose dirty ranges overlap a registered buffer and whose write stamp did not move while they were collected:
bda_nmiss; the moved ones are races, bda_nrace), Sky Garden 300 s, pinned, compute precache ON, GC trigger -1024 MiB.
    GO             admitted, BAD == 0 (bda_nrace is information)
    NO_GO          admitted, sum(bda_nmiss) > 0 (mode 1 is closed as built)
    INVESTIGATE    admitted, sum(bda_nmiss) == 0 and sum(bda_nxthr) > 0 (an unknown off-thread registrar: neither GO
                   nor a closing verdict)
    NOT_EVALUABLE  admitted except REGIME: the run started in the NEW BDA regime (few registrations, nothing to check)
    NOT_ADMITTED   any other admission term fails
BAD = sum(bda_nmiss) + sum(bda_nxthr) over ALL FrameTrace-x rows.

    python C:/kyty/s113/vbn113e.py [--tag vbn113k|vbn113l] [--root C:/kyty/s113] [--out <json>]
"""
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = 'C:/kyty/s113'
TAGS = ('vbn113k', 'vbn113l')
PRED = 'C:/kyty/s113/pred/01e_vbn113e.md'
PRED_SHA = 'c082d54a21b3eebec320c25bb6b8048ec9e00d399af0ce6713b50db7ac009442'   # pred/01e_vbn113e.md sealed
PRED_BYTES = 5062       # pred/01e_vbn113e.md sealed
BINARY_SHA = 'cf22e2236613556f046107804e6545d09fba7833fc23c72cde010e06ca395121'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
TAIL = ' bdanarrow=2'
HOLD_S = 300
MIN_ROWS = 5000
REGIME_OLD = 500           # median bda_scan (FrameTrace-draw) over the scene rows
MIN_WOULD = 1000           # sum bda_nwould: the check must have looked at something
MAX_GPU_UTIL = 10.0        # pre_run gpu_util_median of the launcher: nothing else on the GPU before the run
SHIFT_ENV = 'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB'
SHIFT_MB = 1024            # ROADMAP item 17: the buffer-GC trigger lowered by 1024 MiB (a forced OLD regime)
GC_LINE = re.compile(rb'^BufferGc: budget=(\d+) trigger=(\d+) critical=(\d+) shift_mb=(\d+)')
FIELDS_X = ('bda_ginv_reg', 'bda_ginv_map', 'bda_rinv', 'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr',
            'bgc_evict', 'bda_nrace', 'da_q_free', 'cspfree_hit', 'cspfree_bad')
FORBIDDEN_ENV = ('KYTY_GATE_SCHEDULE', 'KYTY_GPU_CHECKPOINTS', 'KYTY_REC', 'KYTY_PIPELINE_PRECACHE')
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
           b'asyncpipelines: skipped draw')
X_ROW = re.compile(rb'^FrameTrace-x: n=(\d+)')
MAIN_ROW = re.compile(rb'^FrameTrace: n=(\d+)')
D_ROW = re.compile(rb'^FrameTrace-draw: n=(\d+)')
FIELD = re.compile(rb' (\w+)=(-?\d+)')
# Sealed predictions: (name, text, value function, low, high)
PREDICTIONS = (
    ('B1', 'BAD == 0', lambda r: r['bad'], 0, 0),
    ('B2', 'bda_scan level in [800, 1400] (the run is OLD)', lambda r: r['level']['bda_scan'], 800, 1400),
    ('B3', 'bda_ginv_reg median over the scene rows in [0.5, 3] a frame (global invalidations by registrations)',
     lambda r: r['level']['bda_ginv_reg'], 0.5, 3.0),
    ('B4', 'bda_nwould median over the scene rows in [800, 1400] a frame (what mode 1 would skip)',
     lambda r: r['level']['bda_nwould'], 800, 1400),
    ('B5', 'bgc_evict median over the scene rows in [0.5, 3] a frame (the buffer GC runs)',
     lambda r: r['level']['bgc_evict'], 0.5, 3.0),
    ('B6', 'sum bda_nrace <= 40 (information: a write between the unlocked and the locked stamp read)',
     lambda r: r['total']['bda_nrace'], None, 40),
)


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def is_marker(line):
    low = line.lower()
    return any(k in low for k in MARKERS)


def evaluate(root=ROOT, tag=TAGS[0], installed_sha=None):
    out = dict(scorer_sha256=sha_file(__file__), pred=PRED, pred_sha256=PRED_SHA, tag=tag)
    errors = []
    if tag not in TAGS:
        errors.append('TAG')
    if PRED_SHA is None or PRED_BYTES is None:
        errors.append('DRAFT')
    elif not Path(PRED).is_file() or sha_file(PRED) != PRED_SHA or Path(PRED).stat().st_size != PRED_BYTES:
        errors.append('SEAL')
    if installed_sha is None:
        installed_sha = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    if installed_sha != BINARY_SHA:
        errors.append('IDENTITY')
    meta_p, log_p = Path(root) / (tag + '.json'), Path(root) / ('log_%s.txt' % tag)
    if not meta_p.is_file() or not log_p.is_file():
        out.update(errors=errors + ['INPUTS'], verdict='NOT_ADMITTED', predictions=[])
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
    if env.get(SHIFT_ENV) != str(SHIFT_MB):
        errors.append('ENV_SHIFT')
    if any(k in env for k in FORBIDDEN_ENV):
        errors.append('ENV_FORBIDDEN')
    gates = ' ' + ' '.join((meta.get('gates') or '').split())
    if not gates.endswith(TAIL) or gates.count(' bdanarrow=') != 1:
        errors.append('GATES')
    att = meta.get('attempts') or []
    ok_att = [a for a in att if a.get('outcome') == 'ok' and a.get('hold_exit') is None]
    if len(att) != 1 or len(ok_att) != 1 or (att[0].get('hold_s') or 0) < 0.95 * HOLD_S:
        errors.append('ATTEMPT')
    stable = ok_att[0].get('stable_frame', 0) if ok_att else 0
    pr = meta.get('pre_run') or {}
    if not isinstance(pr.get('gpu_util_median'), (int, float)) or pr['gpu_util_median'] > MAX_GPU_UTIL:
        errors.append('PRE_RUN')
    pins = pin1 = markers = rows = missing = main_rows = 0
    tot = {k: 0 for k in FIELDS_X}
    scans = []
    scene = {k: [] for k in ('bda_ginv_reg', 'bda_nwould', 'bgc_evict')}
    xns = []
    gc_lines = []
    with open(log_p, 'rb') as f:
        for line in f:
            g = GC_LINE.match(line)
            if g:
                gc_lines.append(tuple(int(x) for x in g.groups()))
            if line.startswith(b'GpuClockPin:'):
                pins += 1
                pin1 += int(line.startswith(b'GpuClockPin: mode 1'))
            if is_marker(line):
                markers += 1
            if MAIN_ROW.match(line):
                main_rows += 1
                continue
            m = X_ROW.match(line)
            if m:
                rows += 1
                xns.append(int(m.group(1)))
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                missing += int(any(k not in d for k in FIELDS_X))
                for k in FIELDS_X:
                    tot[k] += d.get(k, 0)
                if int(m.group(1)) >= stable:
                    for k in scene:
                        scene[k].append(d.get(k, 0))
                continue
            m = D_ROW.match(line)
            if m and int(m.group(1)) >= stable:
                d = dict(FIELD.findall(line[m.end():]))
                if b'bda_scan' in d:
                    scans.append(int(d[b'bda_scan']))
    so = Path(root) / ('stdout_%s.txt' % tag)
    if so.is_file():
        with open(so, 'rb') as f:
            markers += sum(1 for line in f if is_marker(line))
    if pins != 1 or pin1 != 1:
        errors.append('PIN_ONCE')
    if len(gc_lines) != 1 or gc_lines[0][3] != SHIFT_MB or not gc_lines[0][1] < gc_lines[0][2]:
        errors.append('GC_LINE')      # one constructor line: the shift took effect, the trigger stays below critical
    if markers:
        errors.append('NO_MARKER')
    if rows < MIN_ROWS or missing:
        errors.append('ROWS')
    # every flip reported once, in order, and every main row has its x row (a glued or lost row would hide counts)
    if (not xns or any(b - a != 1 for a, b in zip(xns, xns[1:])) or abs(rows - main_rows) > 1):
        errors.append('STREAMS')
    scan_level = statistics.median(scans) if scans else 0
    if tot['bda_ginv_reg'] <= 0 or tot['bda_nwould'] < MIN_WOULD or tot['bda_nskip'] != 0:
        errors.append('ARMED')        # mode 2: global invalidations happen, the check looked, mode 1 never ran
    if tot['da_q_free'] <= 0 or tot['cspfree_hit'] <= 0 or tot['cspfree_bad'] != 0:
        errors.append('DEFAULTS')
    regime_old = scan_level >= REGIME_OLD
    bad = tot['bda_nmiss'] + tot['bda_nxthr']
    per_row = {k: tot[k] / rows if rows else 0.0 for k in FIELDS_X}
    level = {'bda_scan': scan_level}
    level.update({k: (statistics.median(v) if v else 0) for k, v in scene.items()})
    out.update(errors=errors, rows=rows, main_rows=main_rows, total=tot, per_row=per_row, bad=bad,
               regime_old=regime_old, level=level, scan_rows=len(scans), pre_run_gpu_util=pr.get('gpu_util_median'),
               gc_lines=gc_lines)
    if errors:
        out['verdict'] = 'NOT_ADMITTED'
    elif not regime_old:
        out['verdict'] = 'NOT_EVALUABLE'
    elif bad == 0:
        out['verdict'] = 'GO'
    elif tot['bda_nmiss'] == 0:
        out['verdict'] = 'INVESTIGATE'
    else:
        out['verdict'] = 'NO_GO'
    preds = []
    for name, text, fn, low, high in PREDICTIONS:
        try:
            value = fn(out)
        except (KeyError, TypeError, ValueError):
            value = None
        hit = value is not None and (low is None or value >= low) and (high is None or value <= high)
        preds.append(dict(name=name, text=text, value=value, low=low, high=high, hit=hit))
    out['predictions'] = preds
    return out


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    tag = sys.argv[sys.argv.index('--tag') + 1] if '--tag' in sys.argv else TAGS[0]
    res = evaluate(root, tag)
    print('  tag %s  rows %s  scan rows %s  errors %s' % (tag, res.get('rows'), res.get('scan_rows'),
                                                         res['errors'] or 'none'))
    for k in FIELDS_X:
        if 'total' in res:
            print('  %-14s total %12d   per row %10.3f' % (k, res['total'][k], res['per_row'][k]))
    if 'level' in res:
        print('  levels (medians over the scene rows) %s  regime %s' % (res['level'],
                                                                      'OLD' if res['regime_old'] else 'NEW'))
        print('  main rows %s  pre_run gpu util %s' % (res.get('main_rows'), res.get('pre_run_gpu_util')))
        print('  BufferGc lines (budget, trigger, critical, shift_mb) %s' % (res.get('gc_lines'),))
    print('  BAD %s' % res.get('bad'))
    for p in res.get('predictions', []):
        print('  prediction %s %s  value %s  %s' % (p['name'], 'HIT ' if p['hit'] else 'MISS', p['value'], p['text']))
    print('  scorer %s' % res['scorer_sha256'])
    print('VERDICT: %s' % res['verdict'])
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] in ('GO', 'NO_GO', 'NOT_EVALUABLE', 'INVESTIGATE') else 1


if __name__ == '__main__':
    sys.exit(main())
