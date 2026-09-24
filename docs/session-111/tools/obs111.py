"""Session 111, pred/01_obs111.md scorer: one pinned OBSERVATION run `obs111` under the session-111 defaults (build
072861c8..., knob cspfree=1 by default) with the measurement gate plkstat=1 and nothing else - who still holds
PipelineCache::m_mutex behind GuestGpu's contended wall once the walker's compute prefetch returns before the lock.
Written directly, not by substitution: the readouts come from C:/kyty/s107/obs107.py (contended wall by holder tag,
the walker's holds, the spin share), the admission terms from the session-109/110 scorers (stl110b.py, shp110.py).
One arm, no ABBA, no schedule.

    python C:/kyty/s111/obs111.py obs111 [--root <dir>] [--out <json>]

Window: every FrameTrace-x row with n >= 2100 (the steady scene); one row is one flip.  Per flip = sum over the
window / window rows; shares are ratios of sums.
  cont_wall_us  sum pl_cont_wall_ns / rows / 1000     GuestGpu's contended wall at m_mutex (three plkstat sites)
  tag1_us       sum pl_cont_h1_ns / rows / 1000       ... the holder was the walker in QueueDrawAhead
  tag2_us       sum pl_cont_h2_ns / rows / 1000       ... the holder was the walker in PrefetchComputePipeline
  tag03_us      sum (pl_cont_h0_ns + pl_cont_h3_ns) / rows / 1000   ... untagged + compute compile completion
  cont_n        sum pl_cont_n / rows                  contended acquisitions (by tag: pl_cont_hK_n)
  spin_share    sum pl_cont_cpu_ns / sum pl_cont_wall_ns   a LOWER bound (session-107 audit, item 1)
  tag1_share    sum pl_cont_h1_ns / sum pl_cont_wall_ns
  wq_hold_us    sum pl_wq_hold_ns / rows / 1000; wq_call_us = sum pl_wq_hold_ns / sum pl_wq_hold_n / 1000
  wp_hold_us    sum pl_wp_hold_ns / rows / 1000       expected ~0: cspfree=1 returns before the locked prefetch
  cspfree_hit, cspfree_look, cspf_have, cspf_new per flip
Rule (sealed): tag1_us >= 100 => BUILD_DASLOT, otherwise LOCK_DONE; NOT_ADMITTED if any admission term fails.
Admission terms (stable names; the fixtures assert the exact failing set):
  DRAFT (PRED_SHA/PRED_BYTES unpinned) | SEAL (pred file missing, other sha or size), IDENTITY (installed exe sha,
  computed in main, injectable), INPUTS (meta json or log missing/unreadable), BINARY (meta binary_sha256), PREREG
  (meta prereg sha256/bytes = the pins), ENV_PIN (KYTY_GPU_CLOCK_PIN=1), ENV_FORBIDDEN (no KYTY_GATE_SCHEDULE,
  KYTY_GPU_CHECKPOINTS, KYTY_REC at any value), GATES_PLKSTAT (the only plkstat= token is plkstat=1, once),
  GATES_DEFAULTS (no cspfree= / cspmemo= / cspfam= token: the defaults run), ATTEMPT (one attempt, ok, no hold exit,
  hold_s >= 285), PIN_ONCE (one GpuClockPin: line, mode 1), NO_MARKER (run_safety99 tokens + '--- error ---' +
  'asyncpipelines: skipped draw', case-insensitive, log and stdout_<tag>.txt), ROWS (>= 5000 window rows, each with
  every counter used), PLKSTAT_ARMED (window sum pl_cont_n > 0 or sum pl_wq_hold_n > 0), CSPFREE_ARMED (window sum
  cspfree_hit > 0), CSPFREE_BAD (sum cspfree_bad over ALL rows == 0).
Predictions P1-P5 are printed, never deciding.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PRODUCTION_ROOT = 'C:/kyty/s111'
PRED = 'C:/kyty/s111/pred/01_obs111.md'
PRED_SHA = '985318280ea6c461abb25acfbf171ce98b28873677ee0c39c808c6bf54e1272d'   # pred/01_obs111.md sealed
PRED_BYTES = 2952       # pred/01_obs111.md sealed
BINARY_SHA = '072861c89193c3726232e44e78be4f36172254af826394b56c8bf671ef609c21'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
GATES_FILE = 'C:/kyty/s111/gates_obs111.txt'
TAG = 'obs111'
START = 2100
MIN_ROWS = 5000
MIN_HOLD_S = 285.0
RULE_US = 100.0
FIELDS = ('pl_cont_n', 'pl_cont_wall_ns', 'pl_cont_cpu_ns', 'pl_cont_h0_n', 'pl_cont_h0_ns', 'pl_cont_h1_n',
          'pl_cont_h1_ns', 'pl_cont_h2_n', 'pl_cont_h2_ns', 'pl_cont_h3_n', 'pl_cont_h3_ns', 'pl_wq_hold_ns',
          'pl_wq_hold_n', 'pl_wp_hold_ns', 'pl_wp_hold_n', 'cspfree_look', 'cspfree_hit', 'cspfree_bad',
          'cspf_have', 'cspf_new')
FORBIDDEN_ENV = ('KYTY_GATE_SCHEDULE', 'KYTY_GPU_CHECKPOINTS', 'KYTY_REC')
DEFAULT_KNOBS = ('cspfree=', 'cspmemo=', 'cspfam=')
# run_safety99.FAILURE_TOKENS (copied, lower case) plus the two markers the session-108 audit found missing
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
           b'asyncpipelines: skipped draw')
ROW = re.compile(rb'^FrameTrace-x: n=(\d+)')
FIELD = re.compile(rb' (\w+)=(-?\d+)')
PIN = re.compile(rb'^GpuClockPin: mode (\d+)')


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_log(root, tag):
    """every FrameTrace-x row as (n, {name: value}), the GpuClockPin lines and the failure-marker lines"""
    rows, pins, pin1, markers = [], 0, 0, 0
    with open(Path(root) / ('log_%s.txt' % tag), 'rb') as f:
        for line in f:
            if line.startswith(b'GpuClockPin:'):
                pins += 1
                m = PIN.match(line)
                pin1 += int(m is not None and m.group(1) == b'1')
            low = line.lower()
            if any(k in low for k in MARKERS):
                markers += 1
            m = ROW.match(line)
            if m:
                rows.append((int(m.group(1)), {k.decode(): int(v) for k, v in FIELD.findall(line[m.end():])}))
    stdout_p = Path(root) / ('stdout_%s.txt' % tag)
    if stdout_p.is_file():
        with open(stdout_p, 'rb') as f:
            markers += sum(1 for line in f if any(k in line.lower() for k in MARKERS))
    return rows, pins, pin1, markers


def evaluate(root, tag, installed_sha):
    out = dict(scorer='obs111.py', scorer_sha256=sha_file(__file__), tag=tag, root=str(root), pred=PRED,
               pred_sha256=PRED_SHA, pred_bytes=PRED_BYTES, binary_sha256_sealed=BINARY_SHA,
               installed_sha256=installed_sha, gates_file=GATES_FILE, start=START, min_rows=MIN_ROWS,
               rule_us=RULE_US)
    errors = []
    if PRED_SHA is None or PRED_BYTES is None:
        errors.append('DRAFT')
    elif not Path(PRED).is_file() or sha_file(PRED) != PRED_SHA or Path(PRED).stat().st_size != PRED_BYTES:
        errors.append('SEAL')
    if installed_sha != BINARY_SHA:
        errors.append('IDENTITY')
    meta_p, log_p = Path(root) / (tag + '.json'), Path(root) / ('log_%s.txt' % tag)
    meta = None
    if meta_p.is_file() and log_p.is_file():
        try:
            meta = json.loads(meta_p.read_text(encoding='utf-8'))
        except ValueError:
            meta = None
    if not isinstance(meta, dict):
        errors.append('INPUTS')
        out.update(errors=errors, readouts=None, predictions=None, verdict='NOT_ADMITTED')
        return out
    env = meta.get('env') or {}
    if meta.get('binary_sha256') != BINARY_SHA:
        errors.append('BINARY')
    pre = meta.get('prereg') or {}
    if PRED_SHA is None or pre.get('sha256') != PRED_SHA or pre.get('bytes') != PRED_BYTES:
        errors.append('PREREG')
    if env.get('KYTY_GPU_CLOCK_PIN') != '1':
        errors.append('ENV_PIN')
    if any(k in env for k in FORBIDDEN_ENV):
        errors.append('ENV_FORBIDDEN')
    tokens = (meta.get('gates') or '').split()
    if [t for t in tokens if t.startswith('plkstat=')] != ['plkstat=1']:
        errors.append('GATES_PLKSTAT')
    if any(t.startswith(DEFAULT_KNOBS) for t in tokens):
        errors.append('GATES_DEFAULTS')
    att = meta.get('attempts') or []
    if (len(att) != 1 or att[0].get('outcome') != 'ok' or att[0].get('hold_exit') is not None
            or (att[0].get('hold_s') or 0) < MIN_HOLD_S):
        errors.append('ATTEMPT')
    rows, pins, pin1, markers = read_log(root, tag)
    if pins != 1 or pin1 != 1:
        errors.append('PIN_ONCE')
    if markers:
        errors.append('NO_MARKER')
    steady = [d for n, d in rows if n >= START]
    nrow = len(steady)
    missing = sum(1 for d in steady if any(k not in d for k in FIELDS))
    tot = {k: sum(d.get(k, 0) for d in steady) for k in FIELDS}
    bad_all = sum(d.get('cspfree_bad', 0) for n, d in rows)
    if nrow < MIN_ROWS or missing:
        errors.append('ROWS')
    if not (tot['pl_cont_n'] > 0 or tot['pl_wq_hold_n'] > 0):
        errors.append('PLKSTAT_ARMED')
    if tot['cspfree_hit'] <= 0:
        errors.append('CSPFREE_ARMED')
    if bad_all != 0:
        errors.append('CSPFREE_BAD')

    def per(x):
        return x / nrow if nrow else None

    def us(x):
        return x / nrow / 1000.0 if nrow else None

    wall = tot['pl_cont_wall_ns']
    r = dict(
        rows=nrow, rows_all=len(rows), rows_missing=missing,
        cont_wall_us=us(wall),
        tag1_us=us(tot['pl_cont_h1_ns']),
        tag2_us=us(tot['pl_cont_h2_ns']),
        tag03_us=us(tot['pl_cont_h0_ns'] + tot['pl_cont_h3_ns']),
        tag_residual_ns=wall - (tot['pl_cont_h0_ns'] + tot['pl_cont_h1_ns'] + tot['pl_cont_h2_ns']
                                + tot['pl_cont_h3_ns']),
        cont_n=per(tot['pl_cont_n']),
        cont_n_tag={'0': per(tot['pl_cont_h0_n']), '1': per(tot['pl_cont_h1_n']), '2': per(tot['pl_cont_h2_n']),
                    '3': per(tot['pl_cont_h3_n'])},
        spin_share=tot['pl_cont_cpu_ns'] / wall if wall else None,
        tag1_share=tot['pl_cont_h1_ns'] / wall if wall else None,
        tag2_share=tot['pl_cont_h2_ns'] / wall if wall else None,
        wq_hold_us=us(tot['pl_wq_hold_ns']),
        wq_n=per(tot['pl_wq_hold_n']),
        wq_call_us=tot['pl_wq_hold_ns'] / tot['pl_wq_hold_n'] / 1000.0 if tot['pl_wq_hold_n'] else None,
        wp_hold_us=us(tot['pl_wp_hold_ns']),
        wp_n=per(tot['pl_wp_hold_n']),
        cspfree_hit=per(tot['cspfree_hit']),
        cspfree_look=per(tot['cspfree_look']),
        cspf_have=per(tot['cspf_have']),
        cspf_new=per(tot['cspf_new']),
        cspfree_bad_all=bad_all,
        sums=tot,
    )
    if errors:
        verdict = 'NOT_ADMITTED'
    elif r['tag1_us'] >= RULE_US:
        verdict = 'BUILD_DASLOT'
    else:
        verdict = 'LOCK_DONE'
    p = {}

    def add(key, text, value, lo, hi):
        p[key] = {'text': text, 'value': value, 'band': [lo, hi],
                  'hit': value is not None and (lo is None or value >= lo) and (hi is None or value <= hi)}

    add('P1', 'tag-2 contended wall <= 20 us a flip', r['tag2_us'], None, 20.0)
    add('P2', 'tag-1 share of the contended wall >= 0.85', r['tag1_share'], 0.85, None)
    add('P3', 'total contended wall in [150, 320] us a flip', r['cont_wall_us'], 150.0, 320.0)
    add('P4', 'pl_wp_hold_ns per flip <= 20 us', r['wp_hold_us'], None, 20.0)
    add('P5', 'verdict BUILD_DASLOT', 1.0 if verdict == 'BUILD_DASLOT' else 0.0, 1.0, 1.0)
    gates_match = None
    if Path(GATES_FILE).is_file():   # information only, never deciding
        gates_match = Path(GATES_FILE).read_text(encoding='utf-8').strip() == (meta.get('gates') or '').strip()
    out.update(errors=errors, readouts=r, predictions=p, verdict=verdict, binary_sha256=meta.get('binary_sha256'),
               prereg=pre, pins=pins, markers=markers, gates_file_match=gates_match)
    return out


def main():
    argv = sys.argv[1:]
    tag = argv[0] if argv and not argv[0].startswith('--') else TAG
    root = argv[argv.index('--root') + 1] if '--root' in argv else PRODUCTION_ROOT
    out_p = Path(argv[argv.index('--out') + 1]) if '--out' in argv else None
    if out_p is not None and out_p.exists():
        print('output %s exists: never overwritten' % out_p)
        return 2
    installed = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    res = evaluate(root, tag, installed)
    r = res['readouts'] or {}
    print('obs111.py %s root %s rows %s (all %s)' % (tag, root, r.get('rows'), r.get('rows_all')))
    print('  errors %s' % (res['errors'] or 'none'))
    if r:
        print('  contended wall %s us/flip  tag1 %s  tag2 %s  tags0+3 %s  (residual %s ns)'
              % (r['cont_wall_us'], r['tag1_us'], r['tag2_us'], r['tag03_us'], r['tag_residual_ns']))
        print('  contended acquisitions %s/flip  by tag %s' % (r['cont_n'], r['cont_n_tag']))
        print('  spin share (lower bound) %s  tag1 share %s  tag2 share %s'
              % (r['spin_share'], r['tag1_share'], r['tag2_share']))
        print('  walker QueueDrawAhead holds %s us/flip  %s calls/flip  %s us/call'
              % (r['wq_hold_us'], r['wq_n'], r['wq_call_us']))
        print('  walker prefetch holds %s us/flip  %s calls/flip' % (r['wp_hold_us'], r['wp_n']))
        print('  cspfree_hit %s  cspfree_look %s  cspf_have %s  cspf_new %s per flip  cspfree_bad (all rows) %s'
              % (r['cspfree_hit'], r['cspfree_look'], r['cspf_have'], r['cspf_new'], r['cspfree_bad_all']))
        for k, v in res['predictions'].items():
            print('  prediction %s %s value %s  %s' % (k, 'HIT ' if v['hit'] else 'MISS', v['value'], v['text']))
        print('  gates file %s match %s (information only)' % (GATES_FILE, res['gates_file_match']))
    print('  scorer %s' % res['scorer_sha256'])
    print('VERDICT: %s' % res['verdict'])
    if out_p is not None:
        with open(out_p, 'x', encoding='utf-8') as handle:
            handle.write(json.dumps(res, indent=1, default=str) + '\n')
        print('wrote %s' % out_p)
    return 0 if res['verdict'] in ('BUILD_DASLOT', 'LOCK_DONE') else 1


if __name__ == '__main__':
    sys.exit(main())
