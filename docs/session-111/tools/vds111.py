"""Session 111, pred/02_vds111.md: the verify run of knob `daslot` (mode 2: the M1 queue without PipelineCache::m_mutex
plus a key check under every take's slot guard), with gate `smemocheck` on (every M1 take re-materialized and
compared), Sky Garden 300 s, pinned, compute precache ON (shipping).
    GO            admitted, BAD == 0
    NO_GO         admitted, BAD > 0 (the candidate is closed as built)
    NOT_ADMITTED  any admission term fails
BAD = sum(da_slot_bad) + sum(da_chk_bad) over ALL FrameTrace-x rows + the count of `DaSlotVerify: MISMATCH` and
`DrawAheadVerify: MISMATCH` lines (the lines are capped at 40 each; the counters are not).

    python C:/kyty/s111/vds111.py [--root C:/kyty/s111] [--out <json>]
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = 'C:/kyty/s111'
TAG = 'vds111'
PRED = 'C:/kyty/s111/pred/02_vds111.md'
PRED_SHA = '0dadb4f7f5c57adc9db0e484a66285c1ed0ce162120eb7fb9651b8f50a7f7994'   # pred/02_vds111.md sealed
PRED_BYTES = 2809       # pred/02_vds111.md sealed
BINARY_SHA = 'c8235c902e08d00782d0cff23528361d194a501ad1899344ca8302c742372a86'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
TAIL = ' daslot=2 smemocheck=1'
HOLD_S = 300
MIN_ROWS = 5000
MIN_CHECKS = 10000
FIELDS = ('da_slot_bad', 'da_chk_ok', 'da_chk_bad', 'da_q_free', 'da_guard_busy', 'da_q_taking', 'da_hint_defer',
          'da_hint_torn', 'cspfree_hit', 'cspfree_bad')
FORBIDDEN_ENV = ('KYTY_GATE_SCHEDULE', 'KYTY_GPU_CHECKPOINTS', 'KYTY_REC', 'KYTY_PIPELINE_PRECACHE')
# run_safety99.FAILURE_TOKENS (copied, lower case) plus the two markers the session-108 audit found missing
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
           b'asyncpipelines: skipped draw')
MISMATCH = (b'DaSlotVerify: MISMATCH', b'DrawAheadVerify: MISMATCH')
ROW = re.compile(rb'^FrameTrace-x: n=(\d+)')
FIELD = re.compile(rb' (\w+)=(-?\d+)')


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scan_markers(path):
    if not Path(path).is_file():
        return 0
    with open(path, 'rb') as f:
        return sum(1 for line in f if any(k in line.lower() for k in MARKERS))


def evaluate(root=ROOT, installed_sha=None):
    out = dict(scorer_sha256=sha_file(__file__), pred=PRED, pred_sha256=PRED_SHA)
    errors = []
    if PRED_SHA is None or PRED_BYTES is None:
        errors.append('DRAFT')
    elif not Path(PRED).is_file() or sha_file(PRED) != PRED_SHA or Path(PRED).stat().st_size != PRED_BYTES:
        errors.append('SEAL')
    if installed_sha is None:
        installed_sha = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    if installed_sha != BINARY_SHA:
        errors.append('IDENTITY')
    meta_p, log_p = Path(root) / (TAG + '.json'), Path(root) / ('log_%s.txt' % TAG)
    if not meta_p.is_file() or not log_p.is_file():
        out.update(errors=errors + ['INPUTS'], verdict='NOT_ADMITTED')
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
    if not gates.endswith(TAIL) or gates.count(' daslot=') != 1 or gates.count(' smemocheck=') != 1:
        errors.append('GATES')
    att = meta.get('attempts') or []
    if (len(att) != 1 or att[0].get('outcome') != 'ok' or att[0].get('hold_exit') is not None
            or (att[0].get('hold_s') or 0) < 0.95 * HOLD_S):
        errors.append('ATTEMPT')
    pins = pin1 = markers = rows = missing = 0
    mismatch = {k.decode(): 0 for k in MISMATCH}
    tot = {k: 0 for k in FIELDS}
    with open(log_p, 'rb') as f:
        for line in f:
            if line.startswith(b'GpuClockPin:'):
                pins += 1
                pin1 += int(line.startswith(b'GpuClockPin: mode 1'))
            for k in MISMATCH:
                if line.startswith(k):
                    mismatch[k.decode()] += 1
            if any(k in line.lower() for k in MARKERS):
                markers += 1
            m = ROW.match(line)
            if m:
                rows += 1
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                missing += int(any(k not in d for k in FIELDS))
                for k in FIELDS:
                    tot[k] += d.get(k, 0)
    markers += scan_markers(Path(root) / ('stdout_%s.txt' % TAG))
    if pins != 1 or pin1 != 1:
        errors.append('PIN_ONCE')
    if markers:
        errors.append('NO_MARKER')
    if rows < MIN_ROWS or missing:
        errors.append('ROWS')
    if tot['da_q_free'] <= 0 or tot['da_chk_ok'] + tot['da_chk_bad'] < MIN_CHECKS:
        errors.append('ARMED')
    if tot['cspfree_hit'] <= 0 or tot['cspfree_bad'] != 0:
        errors.append('DEFAULTS')
    bad = tot['da_slot_bad'] + tot['da_chk_bad'] + sum(mismatch.values())
    out.update(errors=errors, rows=rows, total=tot, mismatch_lines=mismatch, bad=bad)
    if errors:
        out['verdict'] = 'NOT_ADMITTED'
    elif bad == 0:
        out['verdict'] = 'GO'
    else:
        out['verdict'] = 'NO_GO'
    return out


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    res = evaluate(root)
    print('  rows %s  errors %s' % (res.get('rows'), res['errors'] or 'none'))
    for k in FIELDS:
        if 'total' in res:
            print('  %-14s total %12d' % (k, res['total'][k]))
    print('  mismatch lines %s  BAD %s' % (res.get('mismatch_lines'), res.get('bad')))
    print('  scorer %s' % res['scorer_sha256'])
    print('VERDICT: %s' % res['verdict'])
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] in ('GO', 'NO_GO') else 1


if __name__ == '__main__':
    sys.exit(main())
