"""Session 109, pred/01_ent109.md: the powered guard of `cspfam` v2 as an ABBA of ENTRIES.

Eight entries into Sky Garden with the compute precache off (KYTY_PIPELINE_PRECACHE=gfx), order A B B A A B B A
(A = gates_fam0.txt, cspfam=0; B = gates_fam4.txt, cspfam=4 = v2 at K=4), 150 s each, pinned.  Over ALL
FrameTrace-x rows of each entry (the load included) S = sum(cs_sync_new + cs_sync_wait).
    PASS      admitted, S_A > 0 (the positive control: the guard has exposure) and S_B <= S_A + SLACK
    FAIL      admitted, S_A > 0 and S_B > S_A + SLACK
    NO_POWER  admitted and S_A == 0 (nothing to catch: v2 is not shipped on this run)
    NOT_ADMITTED  any admission term fails

    python C:/kyty/s109/ent109.py [--root C:/kyty/s109] [--out <json>]
"""
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = 'C:/kyty/s109'
PRED = 'C:/kyty/s109/pred/01_ent109.md'
PRED_SHA = 'e2627de0052fedd22db9e3910d77b1fd7b4f4c51815ba80f11b8f3bec76e52b0'   # pred/01 sealed
PRED_BYTES = 4222       # pred/01 sealed
BINARY_SHA = 'e90f55438d95b3b673cde11275965f9ec8a342db40dd4063c4ea8d6836443d40'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
ORDER = 'ABBAABBA'
TAGS = ['ent109_%d' % (i + 1) for i in range(len(ORDER))]
TOKEN = {'A': 'cspfam=0', 'B': 'cspfam=4'}
HOLD_S = 150
SLACK = 2
MIN_ROWS = 1000
FIELDS = ('cs_sync_new', 'cs_sync_wait', 'cspfam_look', 'cspfam_skip', 'cspfam_clr', 'cspf_new')
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


def read_entry(root, tag, arm):
    """per-entry numbers and the list of failed admission terms (term names are stable: fixtures assert them)"""
    fails = []
    meta_p, log_p = Path(root) / (tag + '.json'), Path(root) / ('log_%s.txt' % tag)
    if not meta_p.is_file() or not log_p.is_file():
        return dict(tag=tag, arm=arm, fails=['INPUTS']), None
    meta = json.loads(meta_p.read_text(encoding='utf-8'))
    env = meta.get('env') or {}
    if meta.get('binary_sha256') != BINARY_SHA:
        fails.append('BINARY')
    pre = meta.get('prereg') or {}
    if pre.get('sha256') != PRED_SHA or pre.get('bytes') != PRED_BYTES:
        fails.append('PREREG')
    if env.get('KYTY_PIPELINE_PRECACHE') != 'gfx':
        fails.append('ENV_PRECACHE')
    if env.get('KYTY_GPU_CLOCK_PIN') != '1':
        fails.append('ENV_PIN')
    if any(k in env for k in FORBIDDEN_ENV):
        fails.append('ENV_FORBIDDEN')
    gates = ' '.join((meta.get('gates') or '').split())
    other = TOKEN['B' if arm == 'A' else 'A']
    if not gates.endswith(' ' + TOKEN[arm]) or (' ' + other) in (' ' + gates + ' '):
        fails.append('GATES_ARM')
    att = meta.get('attempts') or []
    if (len(att) != 1 or att[0].get('outcome') != 'ok' or att[0].get('hold_exit') is not None
            or (att[0].get('hold_s') or 0) < 0.95 * HOLD_S):
        fails.append('ATTEMPT')
    pins = markers = rows = missing = 0
    queued = None
    tot = {k: 0 for k in FIELDS}
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
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                missing += int(any(k not in d for k in FIELDS))
                for k in FIELDS:
                    tot[k] += d.get(k, 0)
    if pins != 1:
        fails.append('PIN_ONCE')
    if queued != 0:
        fails.append('PRECACHE_OFF')
    if markers:
        fails.append('NO_MARKER')
    if rows < MIN_ROWS or missing:
        fails.append('ROWS')
    if arm == 'A' and (tot['cspfam_skip'] or tot['cspfam_look']):
        fails.append('ARM_A_DARK')
    if arm == 'B' and tot['cspfam_skip'] <= 0:
        fails.append('ARM_B_ARMED')
    res = dict(tag=tag, arm=arm, rows=rows, launched=meta.get('launched'), fails=fails,
               s=tot['cs_sync_new'] + tot['cs_sync_wait'], **tot)
    return res, meta


def evaluate(root=ROOT, installed_sha=None):
    out = dict(scorer_sha256=sha_file(__file__), pred=PRED, pred_sha256=PRED_SHA, order=ORDER, slack=SLACK)
    errors = []
    if PRED_SHA is None or PRED_BYTES is None:
        errors.append('DRAFT')
    elif not Path(PRED).is_file() or sha_file(PRED) != PRED_SHA or Path(PRED).stat().st_size != PRED_BYTES:
        errors.append('SEAL')
    if installed_sha is None:
        installed_sha = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    if installed_sha != BINARY_SHA:
        errors.append('IDENTITY')
    entries = []
    for tag, arm in zip(TAGS, ORDER):
        e, _ = read_entry(root, tag, arm)
        entries.append(e)
        errors += ['%s:%s' % (tag, t) for t in e['fails']]
    stamps = [e.get('launched') for e in entries]
    if any(s is None for s in stamps) or stamps != sorted(stamps) or len(set(stamps)) != len(stamps):
        errors.append('ORDER')
    out['entries'] = entries
    out['errors'] = errors
    sa = sum(e.get('s', 0) for e in entries if e['arm'] == 'A')
    sb = sum(e.get('s', 0) for e in entries if e['arm'] == 'B')
    out['S_A'], out['S_B'] = sa, sb
    if errors:
        out['verdict'] = 'NOT_ADMITTED'
    elif sa == 0:
        out['verdict'] = 'NO_POWER'
    elif sb <= sa + SLACK:
        out['verdict'] = 'PASS'
    else:
        out['verdict'] = 'FAIL'
    return out


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    res = evaluate(root)
    for e in res['entries']:
        print('  %-10s %s rows %6s  sync_new %4s  sync_wait %4s  S %4s  cspf_new %4s  skip %9s  clr %6s  %s'
              % (e['tag'], e['arm'], e.get('rows'), e.get('cs_sync_new'), e.get('cs_sync_wait'), e.get('s'),
                 e.get('cspf_new'), e.get('cspfam_skip'), e.get('cspfam_clr'), ','.join(e['fails']) or 'ok'))
    print('  S_A %d  S_B %d  slack %d  errors %s' % (res['S_A'], res['S_B'], SLACK, res['errors'] or 'none'))
    print('  scorer %s' % res['scorer_sha256'])
    print('VERDICT: %s' % res['verdict'])
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] in ('PASS', 'FAIL', 'NO_POWER') else 1


if __name__ == '__main__':
    sys.exit(main())
