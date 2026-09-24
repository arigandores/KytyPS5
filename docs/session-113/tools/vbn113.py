"""Session 113, pred/01_vbn113.md: the verify run of knob `bdanarrow` in mode 2 (today's global invalidation of the BDA
region stamps on a buffer registration, plus a check of every region mode 1 would have skipped: bda_nwould, and those
whose dirty ranges overlap a registered buffer: bda_nmiss), Sky Garden 300 s, pinned, compute precache ON.  Written
fresh for session 113 (the admission terms follow vds111b.py / vdg112.py).
    GO             admitted, BAD == 0
    NO_GO          admitted, BAD > 0 (mode 1 is closed as built)
    NOT_EVALUABLE  admitted except REGIME: the run started in the NEW BDA regime (few registrations, nothing to check)
    NOT_ADMITTED   any other admission term fails
BAD = sum(bda_nmiss) + sum(bda_nxthr) over ALL FrameTrace-x rows.

    python C:/kyty/s113/vbn113.py [--tag vbn113|vbn113b] [--root C:/kyty/s113] [--out <json>]
"""
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = 'C:/kyty/s113'
TAGS = ('vbn113', 'vbn113b')
PRED = 'C:/kyty/s113/pred/01_vbn113.md'
PRED_SHA = 'e6b7b397f04f8ac110fb97c54ac6467abc0cefa7578da7a01aeb19e9d1509ba5'   # pred/01_vbn113.md sealed
PRED_BYTES = 3443       # pred/01_vbn113.md sealed
BINARY_SHA = '94362eae5e28fa68c6a9d5ed921510a1fb1caa2868b0aa220099ba333df4da92'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
TAIL = ' bdanarrow=2'
HOLD_S = 300
MIN_ROWS = 5000
REGIME_OLD = 500           # median bda_scan (FrameTrace-draw) over the scene rows
MIN_WOULD = 1000           # sum bda_nwould: the check must have looked at something
FIELDS_X = ('bda_ginv_reg', 'bda_ginv_map', 'bda_rinv', 'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr',
            'bgc_evict', 'da_q_free', 'cspfree_hit', 'cspfree_bad')
FORBIDDEN_ENV = ('KYTY_GATE_SCHEDULE', 'KYTY_GPU_CHECKPOINTS', 'KYTY_REC', 'KYTY_PIPELINE_PRECACHE')
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
           b'asyncpipelines: skipped draw')
X_ROW = re.compile(rb'^FrameTrace-x: n=(\d+)')
D_ROW = re.compile(rb'^FrameTrace-draw: n=(\d+)')
FIELD = re.compile(rb' (\w+)=(-?\d+)')
# Sealed predictions: (name, text, value function, low, high)
PREDICTIONS = (
    ('B1', 'BAD == 0', lambda r: r['bad'], 0, 0),
    ('B2', 'bda_scan level in [800, 1400] (the run is OLD)', lambda r: r['level']['bda_scan'], 800, 1400),
    ('B3', 'bda_ginv_reg level in [0.5, 3] a frame (global invalidations by registrations)',
     lambda r: r['per_row']['bda_ginv_reg'], 0.5, 3.0),
    ('B4', 'bda_nwould level in [800, 1400] a frame (what mode 1 would skip)',
     lambda r: r['per_row']['bda_nwould'], 800, 1400),
    ('B5', 'bgc_evict in [0.5, 3] a frame (the buffer GC runs)', lambda r: r['per_row']['bgc_evict'], 0.5, 3.0),
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
    pins = pin1 = markers = rows = missing = 0
    tot = {k: 0 for k in FIELDS_X}
    scans = []
    with open(log_p, 'rb') as f:
        for line in f:
            if line.startswith(b'GpuClockPin:'):
                pins += 1
                pin1 += int(line.startswith(b'GpuClockPin: mode 1'))
            if is_marker(line):
                markers += 1
            m = X_ROW.match(line)
            if m:
                rows += 1
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                missing += int(any(k not in d for k in FIELDS_X))
                for k in FIELDS_X:
                    tot[k] += d.get(k, 0)
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
    if markers:
        errors.append('NO_MARKER')
    if rows < MIN_ROWS or missing:
        errors.append('ROWS')
    scan_level = statistics.median(scans) if scans else 0
    if tot['bda_ginv_reg'] <= 0 or tot['bda_nwould'] < MIN_WOULD or tot['bda_nskip'] != 0:
        errors.append('ARMED')        # mode 2: global invalidations happen, the check looked, mode 1 never ran
    if tot['da_q_free'] <= 0 or tot['cspfree_hit'] <= 0 or tot['cspfree_bad'] != 0:
        errors.append('DEFAULTS')
    regime_old = scan_level >= REGIME_OLD
    bad = tot['bda_nmiss'] + tot['bda_nxthr']
    per_row = {k: tot[k] / rows if rows else 0.0 for k in FIELDS_X}
    out.update(errors=errors, rows=rows, total=tot, per_row=per_row, bad=bad, regime_old=regime_old,
               level={'bda_scan': scan_level}, scan_rows=len(scans))
    if errors:
        out['verdict'] = 'NOT_ADMITTED'
    elif not regime_old:
        out['verdict'] = 'NOT_EVALUABLE'
    elif bad == 0:
        out['verdict'] = 'GO'
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
        print('  bda_scan level %s  regime %s' % (res['level']['bda_scan'], 'OLD' if res['regime_old'] else 'NEW'))
    print('  BAD %s' % res.get('bad'))
    for p in res.get('predictions', []):
        print('  prediction %s %s  value %s  %s' % (p['name'], 'HIT ' if p['hit'] else 'MISS', p['value'], p['text']))
    print('  scorer %s' % res['scorer_sha256'])
    print('VERDICT: %s' % res['verdict'])
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] in ('GO', 'NO_GO', 'NOT_EVALUABLE') else 1


if __name__ == '__main__':
    sys.exit(main())
