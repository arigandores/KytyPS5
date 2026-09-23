"""Session 110, pred/02_stl110b.md: the powered guard of knob `cspfree` by stall DURATION, an ABBA of ENTRIES (from
stl110.py by make_stl110b.py: STALL_SYNC counts only CsStall lines after the first FrameTrace-x row).

Eight entries into Sky Garden with the compute precache off (KYTY_PIPELINE_PRECACHE=gfx), order A B B A A B B A
(A = gates_free0.txt, cspfree=0; B = gates_free1.txt, cspfree=1), 150 s each, pinned.  Each dispatch-time stall
(a synchronous compute compile or a wait for a pending one) logs `CsStall: kind=new|wait us=<N> ...`; per entry D = sum
of us, M = the longest; D_A, D_B sum over each arm's entries, M_A, M_B the longest over them.
    PASS      admitted, A has >= 1 CsStall line (the positive control), D_B <= 1.25 * D_A + 20 000 us and
              M_B <= M_A + 10 000 us
    FAIL      admitted, the control holds, and either bound is exceeded
    NO_POWER  admitted and A has no CsStall line
    NOT_ADMITTED  any admission term fails (the ent109b terms plus STALL_SYNC: the CsStall lines of an entry equal
              its FrameTrace-x sum(cs_sync_new + cs_sync_wait) after the first row, one stall in flight allowed)

    python C:/kyty/s110/stl110b.py [--root C:/kyty/s109] [--out <json>]
"""
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = 'C:/kyty/s110'
PRED = 'C:/kyty/s110/pred/02_stl110b.md'
PRED_SHA = '0299b403a1744560199b046f4ed6d53df1108089f52b3d687c64d90d043cc198'   # pred/02_stl110b.md sealed
PRED_BYTES = 2978       # pred/02_stl110b.md sealed
BINARY_SHA = 'b3f7a2c957dd344bfd140fe6d04eb2b95ac9387d01dabf5b7dde42b6765b6a82'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
ORDER = 'ABBAABBA'
TAGS = ['stl110b_%d' % (i + 1) for i in range(len(ORDER))]
TOKEN = {'A': 'cspfree=0', 'B': 'cspfree=1'}
HOLD_S = 150
D_FACTOR = 1.25
D_SLACK_US = 20000
M_SLACK_US = 10000
MIN_ROWS = 1000
FIELDS = ('cs_sync_new', 'cs_sync_wait', 'cspfam_look', 'cspfam_skip', 'cspfam_clr', 'cspf_new', 'cspfree_look',
          'cspfree_hit', 'cspfree_bad', 'cs_sync_new_us', 'cs_sync_wait_us')
STALL = re.compile(rb'^CsStall: kind=(new|wait) us=(\d+) ')
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
    pins = pin1 = markers = rows = missing = 0
    stall_n = stall_d = stall_m = stall_after = 0
    queued = None
    tot = {k: 0 for k in FIELDS}
    with open(log_p, 'rb') as f:
        for line in f:
            if line.startswith(b'GpuClockPin:'):
                pins += 1
                pin1 += int(line.startswith(b'GpuClockPin: mode 1'))
            m = PRECACHE.match(line)
            if m and queued is None:
                queued = int(m.group(1))
            if any(k in line.lower() for k in MARKERS):
                markers += 1
            m = STALL.match(line)
            if m:
                us = int(m.group(2))
                stall_n += 1
                stall_after += int(rows > 0)  # startup stalls precede every counted row
                stall_d += us
                stall_m = max(stall_m, us)
            m = ROW.match(line)
            if m:
                rows += 1
                d = {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}
                missing += int(any(k not in d for k in FIELDS))
                for k in FIELDS:
                    tot[k] += d.get(k, 0)
    stdout_p = Path(root) / ('stdout_%s.txt' % tag)
    if stdout_p.is_file():
        with open(stdout_p, 'rb') as f:
            markers += sum(1 for line in f if any(k in line.lower() for k in MARKERS))
    if pins != 1 or pin1 != 1:
        fails.append('PIN_ONCE')
    if queued != 0:
        fails.append('PRECACHE_OFF')
    if markers:
        fails.append('NO_MARKER')
    if rows < MIN_ROWS or missing:
        fails.append('ROWS')
    if arm == 'A' and (tot['cspfree_hit'] or tot['cspfree_look']):
        fails.append('ARM_A_DARK')
    if arm == 'B' and (tot['cspfree_hit'] <= 0 or tot['cspfree_bad']):
        fails.append('ARM_B_ARMED')
    s = tot['cs_sync_new'] + tot['cs_sync_wait']
    if not 0 <= s - stall_after <= 1:
        fails.append('STALL_SYNC')
    res = dict(tag=tag, arm=arm, rows=rows, launched=meta.get('launched'), fails=fails, s=s, stall_n=stall_n, stall_after=stall_after,
               d=stall_d, m=stall_m, **tot)
    return res, meta


def evaluate(root=ROOT, installed_sha=None):
    out = dict(scorer_sha256=sha_file(__file__), pred=PRED, pred_sha256=PRED_SHA, order=ORDER, d_factor=D_FACTOR,
               d_slack_us=D_SLACK_US, m_slack_us=M_SLACK_US)
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
    na = sum(e.get('stall_n', 0) for e in entries if e['arm'] == 'A')
    da = sum(e.get('d', 0) for e in entries if e['arm'] == 'A')
    db = sum(e.get('d', 0) for e in entries if e['arm'] == 'B')
    ma = max([e.get('m', 0) for e in entries if e['arm'] == 'A'] or [0])
    mb = max([e.get('m', 0) for e in entries if e['arm'] == 'B'] or [0])
    out.update(S_A=sa, S_B=sb, N_A=na, D_A=da, D_B=db, M_A=ma, M_B=mb, D_BOUND=D_FACTOR * da + D_SLACK_US,
               M_BOUND=ma + M_SLACK_US)
    if errors:
        out['verdict'] = 'NOT_ADMITTED'
    elif na == 0:
        out['verdict'] = 'NO_POWER'
    elif db <= D_FACTOR * da + D_SLACK_US and mb <= ma + M_SLACK_US:
        out['verdict'] = 'PASS'
    else:
        out['verdict'] = 'FAIL'
    return out


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    res = evaluate(root)
    for e in res['entries']:
        print('  %-10s %s rows %6s  new %3s wait %3s  lines %3s  D_us %8s  M_us %7s  cspf_new %4s  hit %8s  %s'
              % (e['tag'], e['arm'], e.get('rows'), e.get('cs_sync_new'), e.get('cs_sync_wait'), e.get('stall_n'),
                 e.get('d'), e.get('m'), e.get('cspf_new'), e.get('cspfree_hit'), ','.join(e['fails']) or 'ok'))
    print('  S_A %d S_B %d  N_A %d  D_A %d D_B %d (bound %.0f)  M_A %d M_B %d (bound %d)  errors %s'
          % (res['S_A'], res['S_B'], res['N_A'], res['D_A'], res['D_B'], res['D_BOUND'], res['M_A'], res['M_B'],
             res['M_BOUND'], res['errors'] or 'none'))
    print('  scorer %s' % res['scorer_sha256'])
    print('VERDICT: %s' % res['verdict'])
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] in ('PASS', 'FAIL', 'NO_POWER') else 1


if __name__ == '__main__':
    sys.exit(main())
