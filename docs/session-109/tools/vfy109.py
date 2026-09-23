"""Session 109, pred/01b_vfy109.md: the verify run of knob `cspfree` (mode 2), Sky Garden 300 s, compute precache off
(KYTY_PIPELINE_PRECACHE=gfx: new permutations are met), pinned.
    GO            admitted, BAD == 0 and HIT_RATE >= 0.9
    NO_GO         admitted, otherwise (the candidate is closed)
    NOT_ADMITTED  any admission term fails
BAD = sum(cspfree_bad) over ALL FrameTrace-x rows; HIT_RATE = sum(cspfree_hit) / sum(cspfree_look) over rows n >= 2100.

    python C:/kyty/s109/vfy109.py [--root C:/kyty/s109] [--out <json>]
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = 'C:/kyty/s109'
TAG = 'vfy109'
PRED = 'C:/kyty/s109/pred/01b_vfy109.md'
PRED_SHA = 'f626da410e534afb858e7c95b8a41ee152690870ad572123575dcdc04d133768'   # pred/01b_vfy109.md sealed
PRED_BYTES = 2743       # pred/01b_vfy109.md sealed
BINARY_SHA = '2f5932296d564b1098831b75a7fc6c8796d3a9ac7e871ea0c3a1c6b0610a4b77'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
TOKEN = 'cspfree=2'
HOLD_S = 300
MIN_ROWS = 5000
STEADY_FROM = 2100
HIT_BAR = 0.9
FIELDS = ('cs_sync_new', 'cs_sync_wait', 'cspf_new', 'cspf_have', 'cspfree_look', 'cspfree_hit', 'cspfree_src_miss',
          'cspfree_spec_miss', 'cspfree_mat_fail', 'cspfree_clr', 'cspfree_store', 'cspfree_bad', 'cspfree_moved')
FORBIDDEN_ENV = ('KYTY_GATE_SCHEDULE', 'KYTY_GPU_CHECKPOINTS', 'KYTY_REC')
# run_safety99.FAILURE_TOKENS (copied, lower case) plus the two markers the session-108 audit found missing
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
           b'asyncpipelines: skipped draw')
ROW = re.compile(rb'^FrameTrace-x: n=(\d+)')
FIELD = re.compile(rb' (\w+)=(-?\d+)')
PRECACHE = re.compile(rb'^PipelinePrecache: \d+ recipes -> \d+ graphics \+ (\d+) compute pipelines queued')


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


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
    if env.get('KYTY_PIPELINE_PRECACHE') != 'gfx':
        errors.append('ENV_PRECACHE')
    if env.get('KYTY_GPU_CLOCK_PIN') != '1':
        errors.append('ENV_PIN')
    if any(k in env for k in FORBIDDEN_ENV):
        errors.append('ENV_FORBIDDEN')
    gates = ' '.join((meta.get('gates') or '').split())
    if not gates.endswith(' ' + TOKEN) or gates.count('cspfree=') != 1:
        errors.append('GATES')
    att = meta.get('attempts') or []
    if (len(att) != 1 or att[0].get('outcome') != 'ok' or att[0].get('hold_exit') is not None
            or (att[0].get('hold_s') or 0) < 0.95 * HOLD_S):
        errors.append('ATTEMPT')
    pins = markers = rows = missing = 0
    queued = None
    tot = {k: 0 for k in FIELDS}
    steady = {k: 0 for k in FIELDS}
    with open(log_p, 'rb') as f:
        for line in f:
            if line.startswith(b'GpuClockPin: mode 1'):
                pins += 1
            m = PRECACHE.match(line)
            if m and queued is None:
                queued = int(m.group(1))
            if any(k in line.lower() for k in MARKERS):
                markers += 1
            m = ROW.match(line)
            if m:
                rows += 1
                n = int(m.group(1))
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                missing += int(any(k not in d for k in FIELDS))
                for k in FIELDS:
                    tot[k] += d.get(k, 0)
                    if n >= STEADY_FROM:
                        steady[k] += d.get(k, 0)
    if pins != 1:
        errors.append('PIN_ONCE')
    if queued != 0:
        errors.append('PRECACHE_OFF')
    if markers:
        errors.append('NO_MARKER')
    if rows < MIN_ROWS or missing:
        errors.append('ROWS')
    if tot['cspfree_look'] <= 0:
        errors.append('ARMED')
    out.update(errors=errors, rows=rows, total=tot, steady=steady)
    bad = tot['cspfree_bad']
    rate = steady['cspfree_hit'] / steady['cspfree_look'] if steady['cspfree_look'] else 0.0
    out.update(bad=bad, hit_rate=rate)
    if errors:
        out['verdict'] = 'NOT_ADMITTED'
    elif bad == 0 and rate >= HIT_BAR:
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
            print('  %-18s total %10d  steady(n>=%d) %10d' % (k, res['total'][k], STEADY_FROM, res['steady'][k]))
    print('  BAD %s  HIT_RATE %.4f (bar %.2f)' % (res.get('bad'), res.get('hit_rate', 0.0), HIT_BAR))
    print('  scorer %s' % res['scorer_sha256'])
    print('VERDICT: %s' % res['verdict'])
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] in ('GO', 'NO_GO') else 1


if __name__ == '__main__':
    sys.exit(main())
