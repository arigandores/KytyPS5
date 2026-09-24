"""Session 112, pred/01_vdg112.md: the verify run of knob `daguard` WITH arm transitions - an ABBA schedule
(90 flips a block from flip 1800) of arm 0 `daslot=0 daguard=0` (the M1 queue under m_mutex without slot guards) and
arm 1 `daslot=1 daguard=1` (the shipped mode), gate `smemocheck=1` in the gate file (every M1 take re-materialized and
compared), Sky Garden 300 s, pinned, compute precache ON.  Written fresh for session 112 (the admission terms follow
vds111b.py; the per-arm split follows shp111.py: rows after the first `GateArm:` line, positions 10..89 of a block).
    GO            admitted, BAD == 0
    NO_GO         admitted, BAD > 0 (the candidate is closed as built)
    NOT_ADMITTED  any admission term fails
BAD = sum(da_slot_bad) + sum(da_chk_bad) over ALL FrameTrace-x rows + the count of `DaSlotVerify: MISMATCH` and
`DrawAheadVerify: MISMATCH` lines.

    python C:/kyty/s112/vdg112.py [--root C:/kyty/s112] [--out <json>]
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = 'C:/kyty/s112'
TAG = 'vdg112'
PRED = 'C:/kyty/s112/pred/01_vdg112.md'
PRED_SHA = 'e4029a493abc48998b789f06ca44f812ed6e2e32468db53f9bd43ef3471a8e8b'   # pred/01_vdg112.md sealed
PRED_BYTES = 3513       # pred/01_vdg112.md sealed
BINARY_SHA = 'b47b58a997b441478ab1d278c992949d79795014370d034b747d5fd4e7b9f7f7'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
ARM_TEXT = ('dawalk=1 dawalklead=1 daslot=0 daguard=0', 'dawalk=1 dawalklead=1 daslot=1 daguard=1')
SCHEDULE = '90+1800:' + ARM_TEXT[0] + '|' + ARM_TEXT[1]
PERIOD = 90
MAIN = (10, 89)          # positions within a block (inclusive) for the per-arm terms
HOLD_S = 300
MIN_ROWS = 5000
MIN_BLOCKS = 40          # GateArm lines
MIN_MAIN_ROWS = 1000     # per arm
CHECK_RATIO = 0.99       # (da_chk_ok + da_chk_bad) / da_hit per arm
FIELDS = ('da_slot_bad', 'da_chk_ok', 'da_chk_bad', 'da_q_free', 'da_q_noguard', 'da_guard_busy', 'da_guard_yield',
          'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'da_qcall', 'cspfree_hit', 'cspfree_bad')
FORBIDDEN_ENV = ('KYTY_GPU_CHECKPOINTS', 'KYTY_REC', 'KYTY_PIPELINE_PRECACHE')
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
           b'asyncpipelines: skipped draw')
MISMATCH = (b'DaSlotVerify: MISMATCH', b'DrawAheadVerify: MISMATCH')
MAIN_ROW = re.compile(rb'^FrameTrace: n=(\d+)')
X_ROW = re.compile(rb'^FrameTrace-x: n=(\d+)')
D_ROW = re.compile(rb'^FrameTrace-draw: n=(\d+)')
GATEARM = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
FIELD = re.compile(rb' (\w+)=(-?\d+)')
# Sealed predictions: (name, text, function of the result -> value, low, high)
PREDICTIONS = (
    ('D1', 'BAD == 0', lambda r: r['bad'], 0, 0),
    ('D2', 'arm-1 da_q_free level in [800, 1400] a flip', lambda r: r['level'][1]['da_q_free'], 800, 1400),
    ('D3', 'arm-0 da_q_noguard level in [800, 1400] a flip', lambda r: r['level'][0]['da_q_noguard'], 800, 1400),
    ('D4', 'da_guard_yield total <= 100', lambda r: r['total']['da_guard_yield'], None, 100),
    ('D5', 'checks/hits >= 0.99 in both arms', lambda r: min(r['ratio']), CHECK_RATIO, None),
)


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scan_markers(path):
    if not Path(path).is_file():
        return 0
    with open(path, 'rb') as f:
        return sum(1 for line in f if any(k in line.lower() for k in MARKERS))


def median(values):
    v = sorted(values)
    if not v:
        return 0.0
    m = len(v) // 2
    return float(v[m]) if len(v) % 2 else (v[m - 1] + v[m]) / 2.0


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
    if env.get('KYTY_GATE_SCHEDULE') != SCHEDULE or env.get('KYTY_GATE_SCHEDULE_ABBA') != '1':
        errors.append('SCHEDULE')
    gates = ' ' + ' '.join((meta.get('gates') or '').split()) + ' '
    if (gates.count(' smemocheck=') != 1 or ' smemocheck=1 ' not in gates or ' daslot=' in gates
            or ' daguard=' in gates):
        errors.append('GATES')
    att = meta.get('attempts') or []
    if (len(att) != 1 or att[0].get('outcome') != 'ok' or att[0].get('hold_exit') is not None
            or (att[0].get('hold_s') or 0) < 0.95 * HOLD_S):
        errors.append('ATTEMPT')
    pins = pin1 = markers = rows = missing = 0
    arm_errors = 0
    mismatch = {k.decode(): 0 for k in MISMATCH}
    tot = {k: 0 for k in FIELDS}
    scheduled = False
    block_of = {}            # n -> (arm, blk) for main lines after the first GateArm
    position = {}            # n -> position within its block
    counts = {}              # blk -> rows seen
    xrow, hits = {}, {}
    armlines = 0
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
            g = GATEARM.match(line.rstrip(b'\r\n'))
            if g:
                scheduled = True
                armlines += 1
                arm = int(g.group(1))
                if (arm > 1 or g.group(2) != b'2' or int(g.group(5)) != PERIOD or g.group(6) != b'1'
                        or g.group(7).decode('utf-8', 'replace').strip() != ARM_TEXT[arm]):
                    arm_errors += 1
                continue
            m = MAIN_ROW.match(line)
            if m:
                if scheduled:
                    d = dict(FIELD.findall(line[m.end():]))
                    if b'arm' in d and b'blk' in d:
                        n, blk = int(m.group(1)), int(d[b'blk'])
                        block_of[n] = (int(d[b'arm']), blk)
                        position[n] = counts.get(blk, 0)
                        counts[blk] = counts.get(blk, 0) + 1
                continue
            m = X_ROW.match(line)
            if m:
                rows += 1
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                missing += int(any(k not in d for k in FIELDS))
                for k in FIELDS:
                    tot[k] += d.get(k, 0)
                xrow[int(m.group(1))] = d
                continue
            m = D_ROW.match(line)
            if m:
                d = dict(FIELD.findall(line[m.end():]))
                hits[int(m.group(1))] = int(d.get(b'da_hit', 0))
    markers += scan_markers(Path(root) / ('stdout_%s.txt' % TAG))
    if pins != 1 or pin1 != 1:
        errors.append('PIN_ONCE')
    if markers:
        errors.append('NO_MARKER')
    if rows < MIN_ROWS or missing:
        errors.append('ROWS')
    if armlines < MIN_BLOCKS or arm_errors:
        errors.append('GATEARM')
    # per arm, main positions
    per = [dict(n=0, hit=0, chk=0, **{k: [] for k in FIELDS}) for _ in range(2)]
    for n, (arm, blk) in block_of.items():
        if arm > 1 or not (MAIN[0] <= position[n] <= MAIN[1]) or n not in xrow:
            continue
        p = per[arm]
        p['n'] += 1
        for k in FIELDS:
            p[k].append(xrow[n].get(k, 0))
        p['hit'] += hits.get(n, 0)
        p['chk'] += xrow[n].get('da_chk_ok', 0) + xrow[n].get('da_chk_bad', 0)
    level = [{k: median(p[k]) for k in FIELDS} for p in per]
    ratio = [p['chk'] / p['hit'] if p['hit'] > 0 else 0.0 for p in per]
    if per[0]['n'] < MIN_MAIN_ROWS or per[1]['n'] < MIN_MAIN_ROWS:
        errors.append('ARM_ROWS')
    if level[0]['da_q_noguard'] < 1 or sum(per[0]['da_q_free']) != 0:
        errors.append('ARMED_ARM0')
    if level[1]['da_q_free'] < 1 or sum(per[1]['da_q_noguard']) != 0:
        errors.append('ARMED_ARM1')
    if min(ratio) < CHECK_RATIO:
        errors.append('CHECKED')
    if tot['cspfree_hit'] <= 0 or tot['cspfree_bad'] != 0:
        errors.append('DEFAULTS')
    bad = tot['da_slot_bad'] + tot['da_chk_bad'] + sum(mismatch.values())
    out.update(errors=errors, rows=rows, total=tot, mismatch_lines=mismatch, bad=bad, gatearm_lines=armlines,
               arm_rows=[p['n'] for p in per], level=level, ratio=ratio)
    if errors:
        out['verdict'] = 'NOT_ADMITTED'
    elif bad == 0:
        out['verdict'] = 'GO'
    else:
        out['verdict'] = 'NO_GO'
    preds = []
    for name, text, fn, low, high in PREDICTIONS:
        try:
            value = fn(out)
        except (KeyError, IndexError, TypeError, ValueError):
            value = None
        hit = value is not None and (low is None or value >= low) and (high is None or value <= high)
        preds.append(dict(name=name, text=text, value=value, low=low, high=high, hit=hit))
    out['predictions'] = preds
    return out


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    res = evaluate(root)
    print('  rows %s  gatearm %s  arm rows %s  errors %s' % (res.get('rows'), res.get('gatearm_lines'),
                                                           res.get('arm_rows'), res['errors'] or 'none'))
    for k in FIELDS:
        if 'total' in res:
            print('  %-14s total %12d   level arm0 %10.1f  arm1 %10.1f' % (
                k, res['total'][k], res['level'][0][k], res['level'][1][k]))
    if 'ratio' in res:
        print('  checks/hits arm0 %.6f  arm1 %.6f' % tuple(res['ratio']))
    print('  mismatch lines %s  BAD %s' % (res.get('mismatch_lines'), res.get('bad')))
    for p in res.get('predictions', []):
        print('  prediction %s %s  value %s  %s' % (p['name'], 'HIT ' if p['hit'] else 'MISS', p['value'], p['text']))
    print('  scorer %s' % res['scorer_sha256'])
    print('VERDICT: %s' % res['verdict'])
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] in ('GO', 'NO_GO') else 1


if __name__ == '__main__':
    sys.exit(main())
