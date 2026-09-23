"""Session 104, route A Stage 2 scorer: gate `dawalk` (the PM4 look-ahead walk off the GuestGpu
thread), ABBA `dawalk=0|1` with `dawalklead=1` in both arms, sealed to pred/03_dawalk.md
(draft: pred_drafts/03_dawalk.draft.md).

    python C:/kyty/s104/dwk104.py dwk104 --out C:/kyty/s104/runs104/dwk104_score.json
                                  [--video-meta C:/kyty/s104/vwk104.json
                                   --video-report C:/kyty/s104/vwk104_glitch.txt]
    python C:/kyty/s104/dwk104.py <tag> --root <dir> --draft [--period .. --keep lo:hi]

Offline only: never launches the game, never rebuilds, never retries, never overwrites an output.

SEAL.  Production scoring refuses to run (exit 2) unless pred/03_dawalk.md is byte-for-byte the
text whose sha256 and size are PRED_SHA / PRED_BYTES below.  Until the executor seals the draft
and fills them, PRED_SHA is None and only --draft works; --draft never prints SHIP.

What is decided (pred/03 section numbers):
  s2  one run dwk104, hold 600 s, schedule 90+1800:dawalk=0 dawalklead=1|dawalk=1 dawalklead=1,
      population of session 101 pred/01 4 (as dab102.py): blocks of 90 from frame 1800, kept rows
      idx 60..88, blocks with a kept frame below 2100 rejected, pairs inside complete ABBA
      quartets; per block the mean over its kept rows; per pair (arm 1) - (arm 0); >= 60 pairs.
  s3  admission: dab102.py integrity controls + session-102 pred/03 s4 controls (bands, work
      split per pred/05 1, area split and match, pin once, two record threads, no checkpoint
      line, no GpuHangAbort, no fatal marker, KYTY_GPU_CHECKPOINTS absent) + arming (s4).
  s4  arming: arm 0 dark (da_wjobs, da_wskip, da_wdrop sum to 0 over arm-0 kept rows);
      arm 1 armed (levels of da_wjobs and da_wskip >= 1); identity
      |sum da_wskip / sum(da_wjobs + da_wdrop) - 1| <= 1 % over arm-1 kept rows (verified on
      session 60's log_sky60.txt: 3 524 skips against 3 521 jobs+drops); drops <= 5 % of posts;
      da_walks level of arm 1 within +-5 % of arm 0's; the measurement instruments dark.
  s5  SHIP dawalk=1 as the new default only if ALL of
        S1  mean d cpu_net_us <= -150 us   (cpu_net_us = cpu_gpu_us - spin_gpu_us)
        S2  mean d cpu_net_us + 2 SE < 0
        S3  mean d dt_us < 0               (same sign)
        S4  the run is ADMITTED (s3, s4)
        S5  the video pass vwk104: installed binary, dawalk=1 in its gate text, KYTY_REC set,
            one ok attempt, >= 3 000 frames and 0 one-frame glitches in s51_vidglitch.py's report.
      S1-S4 true and no video report => SHIP_PENDING_VIDEO (nothing ships until S5 is read).
      Reported, deciding nothing: d da_take_us, d da_miss, d da_late, d da_hit, d da_stale,
      d da_walk_us (arm 1: the walker thread's own walk), d da_queue_us, da_wlag_us, da_wdepth.
  s6  predictions, no decision weight.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PRODUCTION_ROOT = 'C:/kyty/s104'
PRED = 'C:/kyty/s104/pred/03_dawalk.md'
PRED_SHA = '5f088c02c55b185e8f591ce403b0363b70c61a53bcd088b13354fec78e1d4a13'          # filled by the executor when pred/03 is sealed
PRED_BYTES = 8515        # filled by the executor when pred/03 is sealed
BINARY_SHA = '16ef56b69c4a99fa6ad613d0dbf57d7f59e0d5443bd6509c55442d83c4780352'
EXE = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
GATES_FILE = 'C:/kyty/s104/gates_base.txt'
GATES_SHA = '00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8'

PERIOD, START, FIRST_FRAME = 90, 1800, 2100
KEEP_LO, KEEP_HI = 60, 89
MIN_PAIRS = 60
HOLD_S = 600
ARMS = ('dawalk=0 dawalklead=1', 'dawalk=1 dawalklead=1')
SCHEDULE = '90+1800:%s|%s' % ARMS
TAG_RE = r'dwk104b?(?:_entry1)?'

SHIP_US = -150.0
VIDEO_MIN_FRAMES = 3000
ID_TOL = 0.01
DROP_MAX = 0.05
WALKS_TOL = 0.05

BANDS = {'dt_us': (28000.0, 40000.0), 'rec_n': (9000.0, 13000.0),
         'gpu_busy_us': (10000.0, 16000.0)}
WORK_TOL = 0.005
AREA_SPLIT_PCT, AREA_MATCH_PCT, AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 8

EXPECTED_LINE = {
    'dt_us': 'main', 'draws': 'main', 'dispatches': 'main', 'cpu_gpu_us': 'main',
    'gpu_busy_us': 'main', 'arm': 'main', 'blk': 'main',
    'spin_gpu_us': 'draw', 'rec_n': 'draw', 'da_walks': 'draw', 'da_walk_us': 'draw',
    'da_queue_us': 'draw', 'da_take_us': 'draw', 'da_hit': 'draw', 'da_miss': 'draw',
    'da_late': 'draw', 'da_stale': 'draw', 'da_stale_old': 'draw', 'da_busy': 'draw',
    'rt_att': 'x', 'rt_kpx': 'x', 'bf_n': 'x', 'bf_disp': 'x', 'bf_skip': 'x',
    'bf_clr_skip': 'x', 'bf_skip_drop': 'x', 'gm_ops': 'x',
    'da_wjobs': 'x', 'da_wskip': 'x', 'da_wdrop': 'x', 'da_wlag_us': 'x', 'da_wdepth': 'x',
    'da_qcall': 'x', 'mw_n': 'x', 'a_hold_us': 'x', 'a_mut_us': 'x', 'pl_em_n': 'x',
    'pl_proc_n': 'x', 'sh_jobs': 'x',
}
FIELDS = tuple(EXPECTED_LINE)
CORE = ('arm', 'blk', 'dt_us', 'draws', 'cpu_gpu_us', 'spin_gpu_us', 'gpu_busy_us',
        'rt_att', 'rt_kpx')
FLOOR_KEYS = ('bf_n', 'bf_disp', 'bf_skip', 'bf_clr_skip', 'bf_skip_drop')
LINE_KIND = ((b'FrameTrace: ', 'main'), (b'FrameTrace-draw: ', 'draw'), (b'FrameTrace-x: ', 'x'))
RE_TOKEN = re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')
FATAL = (b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---',
         b'ErrorDeviceLost', b'Unhandled exception:', b'GpuWaitSlow:',
         b'AsyncPipelines: skipped draw')
HANG = b'GpuHangAbort'
RE_PIN = re.compile(rb'GpuClockPin: mode (\d+)')
ENV_EXPECTED = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_QUEUE_TRACE': '1',
                'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden',
                'KYTY_GATE_SCHEDULE_ABBA': '1', 'KYTY_GPU_CLOCK_PIN': '1',
                'KYTY_GPU_MARKERS': '0'}
ENV_PRESENT = ('KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE', 'KYTY_GATE_SCHEDULE')
PAIR_KEYS = ('cpu_net_us', 'dt_us', 'draws', 'gpu_busy_us', 'rec_n', 'spin_gpu_us', 'da_take_us',
             'da_miss', 'da_late', 'da_hit', 'da_stale', 'da_busy', 'da_walk_us', 'da_queue_us',
             'da_walks', 'da_qcall')
DARK_KEYS = ('mw_n', 'a_hold_us', 'a_mut_us', 'pl_em_n', 'pl_proc_n', 'sh_jobs')


class SealError(RuntimeError):
    pass


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_seal(path=None, want_sha=None, want_bytes=None):
    path = PRED if path is None else path
    want_sha = PRED_SHA if want_sha is None else want_sha
    want_bytes = PRED_BYTES if want_bytes is None else want_bytes
    if want_sha is None or want_bytes is None:
        raise SealError('PRED_SHA / PRED_BYTES are not filled: seal %s and put its sha256 and '
                        'size into dwk104.py (only --draft runs without a seal)' % path)
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise SealError('sealed pre-registration unreadable: %s (%s)' % (path, exc))
    got = hashlib.sha256(data).hexdigest()
    if got != want_sha or len(data) != want_bytes:
        raise SealError('SEALED PRE-REGISTRATION CHANGED: %s sha256 %s (%d B), sealed %s (%s B)'
                        % (path, got, len(data), want_sha, want_bytes))
    return got


def mean_t(values):
    values = [v for v in values if v is not None]
    n = len(values)
    if n == 0:
        return {'n': 0, 'mean': None, 'sd': None, 'se': None, 't': None}
    mean = statistics.fmean(values)
    if n < 2:
        return {'n': n, 'mean': mean, 'sd': None, 'se': None, 't': None}
    sd = statistics.stdev(values)
    se = sd / math.sqrt(n)
    if se > 0:
        t = mean / se
    else:
        t = -math.inf if mean < 0 else (math.inf if mean > 0 else 0.0)
    return {'n': n, 'mean': mean, 'sd': sd, 'se': se, 't': t}


def median_or_none(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def rel(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b - 1.0


def new_counts():
    return {'hang': 0, 'fatal': {}, 'pin': {}, 'rec_started': 0, 'ckpt_lines': 0,
            'ckpt_off_lines': 0, 'ckpt_diag': 0, 'recording': 0}


def scan_markers(line, counts):
    if HANG in line:
        counts['hang'] += 1
    for marker in FATAL:
        if marker in line:
            counts['fatal'][marker.decode()] = counts['fatal'].get(marker.decode(), 0) + 1
    if b'GpuClockPin:' in line:
        m = RE_PIN.search(line)
        mode = m.group(1).decode() if m else '?'
        counts['pin'][mode] = counts['pin'].get(mode, 0) + 1
    if b'RecordThread: started' in line:
        counts['rec_started'] += 1
    if b'GPU checkpoints' in line:
        if b'GPU checkpoints off' in line:
            counts['ckpt_off_lines'] += 1
        else:
            counts['ckpt_lines'] += 1
    if b'diagnostic checkpoints enabled' in line:
        counts['ckpt_diag'] += 1
    if b'Recording:' in line:
        counts['recording'] += 1


def read_run(log_path, stdout_path):
    rows, order, bad = {}, [], []
    origin = {f: set() for f in FIELDS}
    seen = {'main': set(), 'draw': set(), 'x': set()}
    gate_blocks = []
    counts = new_counts()
    gate_re = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) '
                         rb'period=(\d+) abba=(\d+) text=(.*)$')
    wanted = {f.encode(): f for f in FIELDS}
    missing_fields = set()
    with open(log_path, 'rb') as handle:
        for raw in handle:
            scan_markers(raw, counts)
            if raw.startswith(b'GateArm:'):
                m = gate_re.match(raw.rstrip(b'\r\n'))
                if m:
                    arm, count, block, frame, period, abba, text = m.groups()
                    gate_blocks.append({'arm': int(arm), 'arms': int(count), 'block': int(block),
                                        'frame': int(frame), 'period': int(period),
                                        'abba': int(abba),
                                        'text': text.decode('utf-8', 'replace').strip()})
                else:
                    gate_blocks.append({'malformed': raw[:200].decode('utf-8', 'replace')})
                continue
            if not raw.startswith(b'FrameTrace'):
                continue
            kind = None
            for prefix, name in LINE_KIND:
                if raw.startswith(prefix):
                    kind = name
                    break
            if kind is None:
                continue
            tokens = dict(RE_TOKEN.findall(raw[len(b'FrameTrace'):]))
            if b'n' not in tokens:
                continue
            n = int(tokens[b'n'])
            seen[kind].add(n)
            if kind == 'main':
                order.append(n)
            row = rows.setdefault(n, {'n': n})
            for key, field in wanted.items():
                if key in tokens:
                    origin[field].add(kind)
                    if EXPECTED_LINE[field] == kind:
                        row[field] = int(tokens[key])
            for field, where in EXPECTED_LINE.items():
                if where == kind and field not in row:
                    if len(bad) < 200:
                        bad.append((kind, n, field))
                    missing_fields.add(field)
    if stdout_path is not None and Path(stdout_path).is_file():
        with open(stdout_path, 'rb') as handle:
            for raw in handle:
                scan_markers(raw, counts)
    usable = {n: r for n, r in rows.items() if all(f in r for f in CORE)}
    return {'rows': usable, 'all_rows': rows, 'order': order, 'bad': bad,
            'missing_fields': sorted(missing_fields),
            'origin': {f: sorted(v) for f, v in origin.items()}, 'seen': seen,
            'gate_blocks': gate_blocks, 'counts': counts}


def select(rows, arms, period=PERIOD, start=START, first=FIRST_FRAME, keep=(KEEP_LO, KEEP_HI)):
    lo, hi = keep
    eligible, rejected = {}, {}
    for block in sorted(arms):
        expected = list(range(start + 1 + period * block, start + 1 + period * (block + 1)))
        if not all(n in rows for n in expected):
            rejected[block] = 'incomplete block'
            continue
        kept = expected[lo:hi]
        if len(kept) != hi - lo or min(kept) < first:
            rejected[block] = 'outside first-frame window'
            continue
        eligible[block] = kept
    pairs, excluded = [], []
    top = max(arms) if arms else -1
    for b in range(0, top + 1, 4):
        quartet = list(range(b, b + 4))
        if all(k in eligible for k in quartet):
            pairs.extend([(b, b + 1), (b + 2, b + 3)])
        else:
            excluded.extend(k for k in quartet if k in eligible)
    used = sorted({b for pair in pairs for b in pair})
    return {'pairs': pairs, 'blocks': {b: eligible[b] for b in used},
            'rows': [n for b in used for n in eligible[b]], 'rejected': rejected,
            'excluded_edge_blocks': sorted(set(excluded))}


def derived(row):
    out = dict(row)
    if 'cpu_gpu_us' in row and 'spin_gpu_us' in row:
        out['cpu_net_us'] = row['cpu_gpu_us'] - row['spin_gpu_us']
    return out


def block_means(rows, ns):
    group = [derived(rows[n]) for n in ns]
    keys = set(group[0])
    for r in group[1:]:
        keys &= set(r)
    out = {k: statistics.fmean(r[k] for r in group) for k in keys if k != 'n'}
    out['rows'] = len(group)
    return out


def arm_levels(means, arms):
    keys = set()
    for m in means.values():
        keys |= set(m)
    return {a: {k: median_or_none(means[b].get(k) for b in means if arms[b] == a)
                for k in sorted(keys)} for a in (0, 1)}


def kept_total(rows, sel, arms, arm, key):
    vals = [rows[n].get(key) for b, ns in sel['blocks'].items() if arms[b] == arm for n in ns]
    if any(v is None for v in vals):
        return None
    return sum(vals)


def work_split(rows, sel, arms):
    retained = [rows[n] for n in sel['rows']]
    groups = {a: [r['draws'] for r in retained if r['arm'] == a] for a in (0, 1)}
    mean0 = statistics.fmean(groups[0]) if groups[0] else None
    mean1 = statistics.fmean(groups[1]) if groups[1] else None
    work = (mean1 / mean0 - 1) if (mean0 and mean1 is not None) else None
    return {'rows_arm0': len(groups[0]), 'rows_arm1': len(groups[1]), 'tolerance': WORK_TOL,
            'mean_draws_arm0': mean0, 'mean_draws_arm1': mean1, 'work': work,
            'passed': work is not None and abs(work) < WORK_TOL}


def area_of(rows_list):
    att = sum(r['rt_att'] for r in rows_list)
    return sum(r['rt_kpx'] for r in rows_list) / att if att > 0 else None


def area_verdict_mirror(all_rows, first_frame=FIRST_FRAME, tol=AREA_TOL_PCT,
                        min_flips=AREA_MIN_FLIPS):
    need = ('arm', 'blk', 'rt_att', 'rt_kpx', 'draws', 'cpu_gpu_us', 'gpu_busy_us')
    rows = [r for n, r in sorted(all_rows.items())
            if n >= first_frame and all(k in r for k in need)]
    out = {'flips': len(rows), 'valid': False}
    arms = sorted({r['arm'] for r in rows})
    out['arms'] = arms
    if len(arms) != 2:
        out['reason'] = 'not a two-arm run'
        return out

    def whole(arm):
        sel = [r for r in rows if r['arm'] == arm]
        att = sum(r['rt_att'] for r in sel)
        kpx = sum(r['rt_kpx'] for r in sel)
        draws = sum(r['draws'] for r in sel)
        return {'flips': len(sel), 'area': kpx / att if att else None,
                'draws_fr': draws / len(sel) if sel else None}

    w0, w1 = whole(0), whole(1)
    if not (w0['area'] and w1['area'] and w0['draws_fr']):
        out['reason'] = 'empty arm'
        return out
    split = (w1['area'] - w0['area']) / w0['area'] * 100.0
    dwork = (w1['draws_fr'] - w0['draws_fr']) / w0['draws_fr'] * 100.0
    acc = {}
    for r in rows:
        b = acc.setdefault((r['blk'], r['arm']), {'draws': 0.0, 'att': 0.0, 'kpx': 0.0, 'n': 0})
        b['draws'] += r['draws']
        b['att'] += r['rt_att']
        b['kpx'] += r['rt_kpx']
        b['n'] += 1
    ordered = sorted(acc.items(), key=lambda kv: kv[0][0])
    pairs = []
    for i in range(len(ordered) - 1):
        (blk_a, arm_a), ba = ordered[i]
        (blk_b, arm_b), bb = ordered[i + 1]
        if arm_a == arm_b or blk_b != blk_a + 1:
            continue
        a0, a1 = (ba, bb) if arm_a == 0 else (bb, ba)
        if a0['n'] < min_flips or a1['n'] < min_flips:
            continue
        if not (a0['draws'] and a1['draws'] and a0['att'] and a1['att']):
            continue
        area0, area1 = a0['kpx'] / a0['att'], a1['kpx'] / a1['att']
        pairs.append((area1 - area0) / area0 * 100.0)
    kept = [d for d in pairs if abs(d) <= tol]
    rate = 100.0 * len(kept) / len(pairs) if pairs else 0.0
    out.update(split_pct=split, work_pct=dwork, pairs=len(pairs), matched=len(kept),
               match_pct=rate, area0=w0['area'], area1=w1['area'])
    out['criteria'] = {'split': abs(split) < AREA_SPLIT_PCT, 'match': rate >= AREA_MATCH_PCT,
                       'work': abs(dwork) < AREA_WORK_PCT}
    out['valid'] = all(out['criteria'].values())
    return out


def selected_area(rows, sel, arms):
    groups = {0: [], 1: []}
    for b, ns in sel['blocks'].items():
        groups[arms[b]].extend(rows[n] for n in ns)
    a0, a1 = area_of(groups[0]), area_of(groups[1])
    if not a0 or not a1:
        return {'valid_data': False}
    deltas = []
    for left, right in sel['pairs']:
        g = {arms[left]: [rows[n] for n in sel['blocks'][left]],
             arms[right]: [rows[n] for n in sel['blocks'][right]]}
        if set(g) != {0, 1}:
            return {'valid_data': False}
        p0, p1 = area_of(g[0]), area_of(g[1])
        if not p0 or p1 is None:
            return {'valid_data': False}
        deltas.append(100.0 * (p1 / p0 - 1))
    matched = sum(abs(d) <= AREA_TOL_PCT for d in deltas)
    return {'valid_data': True, 'split_pct': 100.0 * (a1 / a0 - 1), 'pairs': len(deltas),
            'matched': matched, 'match_pct': 100.0 * matched / len(deltas) if deltas else 0.0}


def protocol_errors(meta, gates_file):
    errors = []
    err = errors.append
    env = meta.get('env') or {}
    kyty = {k: v for k, v in env.items() if k.startswith('KYTY_')}
    for key, value in ENV_EXPECTED.items():
        if kyty.get(key) != value:
            err('env %s=%r, expected %r' % (key, kyty.get(key), value))
    if kyty.get('KYTY_GATE_SCHEDULE') != SCHEDULE:
        err('env KYTY_GATE_SCHEDULE=%r, expected %r' % (kyty.get('KYTY_GATE_SCHEDULE'), SCHEDULE))
    if (meta.get('schedule') or '') != SCHEDULE:
        err('meta schedule %r, expected %r' % (meta.get('schedule'), SCHEDULE))
    for key in ENV_PRESENT:
        if key not in kyty:
            err('env %s absent' % key)
    extra = sorted(set(kyty) - set(ENV_EXPECTED) - set(ENV_PRESENT))
    if extra:
        err('env carries KYTY_* variables outside the sealed launch: %s' % extra)
    try:
        gates_text = ' '.join(Path(gates_file).read_text(encoding='utf-8').split())
        gates_sha = sha256_file(gates_file)
    except OSError:
        gates_text, gates_sha = None, None
    if gates_sha != GATES_SHA:
        err('gates_base.txt sha256 %s, expected %s' % (gates_sha, GATES_SHA))
    if meta.get('gates') != gates_text:
        err('meta gates text is not gates_base.txt')
    attempts = meta.get('attempts') or []
    if [a.get('label') for a in attempts] != ['attempt 1']:
        err('attempts are %r, expected exactly [attempt 1]' % ([a.get('label') for a in attempts],))
    for a in attempts:
        if a.get('outcome') != 'ok':
            err('attempt outcome %r' % a.get('outcome'))
        if a.get('hold_exit') is not None:
            err('the game ended inside the hold (hold_exit=%r)' % a.get('hold_exit'))
        if (a.get('hold_s') or 0) < HOLD_S - 5:
            err('hold_s %r below %d' % (a.get('hold_s'), HOLD_S - 5))
    if meta.get('hold_s') != HOLD_S:
        err('meta hold_s %r, expected %d' % (meta.get('hold_s'), HOLD_S))
    return errors


def arming(rows, sel, arms, lev):
    """pred/03 s4."""
    checks = {}
    dark0 = all(kept_total(rows, sel, arms, 0, k) == 0 for k in ('da_wjobs', 'da_wskip', 'da_wdrop'))
    checks['WALK_DARK_ARM0'] = dark0
    checks['WALK_ARMED_ARM1'] = bool((lev[1].get('da_wjobs') or 0) >= 1
                                     and (lev[1].get('da_wskip') or 0) >= 1)
    skip = kept_total(rows, sel, arms, 1, 'da_wskip')
    jobs = kept_total(rows, sel, arms, 1, 'da_wjobs')
    drop = kept_total(rows, sel, arms, 1, 'da_wdrop')
    posts = (jobs + drop) if (jobs is not None and drop is not None) else None
    ident = rel(skip, posts)
    checks['WALK_IDENTITY_ARM1'] = ident is not None and abs(ident) <= ID_TOL
    drop_frac = (drop / posts) if (posts and drop is not None) else None
    checks['WALK_DROPS'] = drop_frac is not None and drop_frac <= DROP_MAX
    rw = rel(lev[1].get('da_walks'), lev[0].get('da_walks'))
    checks['WALKS_SAME'] = rw is not None and abs(rw) <= WALKS_TOL
    dark = all(kept_total(rows, sel, arms, a, k) == 0 for a in (0, 1) for k in DARK_KEYS)
    checks['INSTRUMENTS_DARK'] = dark
    return {'checks': checks, 'passed': all(bool(v) for v in checks.values()),
            'arm1_kept_totals': {'da_wskip': skip, 'da_wjobs': jobs, 'da_wdrop': drop},
            'skip_over_posts_rel': ident, 'drop_fraction': drop_frac, 'walks_rel': rw}


def read_video(meta_path, report_path):
    """pred/03 s5 S5.  Returns (state, detail): state in PASS / FAIL / ABSENT."""
    if not meta_path or not report_path:
        return 'ABSENT', {'reason': 'no --video-meta / --video-report given'}
    mp, rp = Path(meta_path), Path(report_path)
    if not mp.is_file() or not rp.is_file():
        return 'ABSENT', {'reason': 'missing %s' % [str(p) for p in (mp, rp) if not p.is_file()]}
    meta = json.loads(mp.read_text(encoding='utf-8'))
    text = rp.read_text(encoding='utf-8', errors='replace')
    m_frames = re.search(r'(\d+) frames', text)
    m_glitch = re.search(r'one-frame glitches:\s*(\d+)', text)
    frames = int(m_frames.group(1)) if m_frames else None
    glitches = int(m_glitch.group(1)) if m_glitch else None
    env = meta.get('env') or {}
    gates = ' ' + (meta.get('gates') or '') + ' '
    attempts = meta.get('attempts') or []
    checks = {
        'binary': meta.get('binary_sha256') == BINARY_SHA,
        'dawalk_1_in_gate_text': ' dawalk=1 ' in gates and ' dawalklead=1 ' in gates,
        'recorded': bool(env.get('KYTY_REC')),
        'no_schedule': not env.get('KYTY_GATE_SCHEDULE'),
        'no_checkpoints': 'KYTY_GPU_CHECKPOINTS' not in env,
        'one_ok_attempt': [a.get('outcome') for a in attempts] == ['ok']
                          and all(a.get('hold_exit') is None for a in attempts),
        'frames': frames is not None and frames >= VIDEO_MIN_FRAMES,
        'no_glitch': glitches == 0,
    }
    detail = {'checks': checks, 'frames': frames, 'glitches': glitches,
              'meta_sha256': sha256_file(mp), 'report_sha256': sha256_file(rp)}
    return ('PASS' if all(checks.values()) else 'FAIL'), detail


def evaluate(root, tag, draft=False, geometry=None, gates_file=GATES_FILE, video_meta=None,
             video_report=None):
    geo = dict(period=PERIOD, start=START, first=FIRST_FRAME, keep=(KEEP_LO, KEEP_HI))
    if geometry:
        if not draft:
            raise ValueError('population geometry can only be changed in --draft')
        geo.update(geometry)
    out = {'scorer': 'dwk104.py', 'tag': tag, 'pred': PRED, 'draft': bool(draft),
           'pred_sha256': None if draft else check_seal(), 'errors': [], 'notes': [],
           'geometry': dict(geo, keep=list(geo['keep']))}
    root = Path(root)
    log, stdout, meta_path = (root / ('log_%s.txt' % tag), root / ('stdout_%s.txt' % tag),
                              root / ('%s.json' % tag))
    for p in (log, meta_path):
        if not p.is_file():
            out['errors'].append('missing input: %s' % p)
    if out['errors']:
        return finish(out, {'INPUTS': False}, {}, None)
    out['raw_sha256'] = {'log': sha256_file(log), 'meta': sha256_file(meta_path),
                         'stdout': sha256_file(stdout) if stdout.is_file() else None}
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    out['binary_sha256'] = meta.get('binary_sha256')
    out['errors'].extend(protocol_errors(meta, gates_file))
    integrity, controls = {}, {}
    prereg = meta.get('prereg') or {}
    integrity['PREREG_PINNED'] = (PRED_SHA is not None and prereg.get('sha256') == PRED_SHA
                                  and prereg.get('bytes') == PRED_BYTES)
    integrity['BINARY_SEALED'] = meta.get('binary_sha256') == BINARY_SHA

    run = read_run(log, stdout if stdout.is_file() else None)
    rows, counts = run['rows'], run['counts']
    out['markers'] = counts
    integrity['SCHEMA'] = not run['bad']
    out['schema_missing_fields'] = run['missing_fields']
    wrong = {f: v for f, v in run['origin'].items() if v and v != [EXPECTED_LINE[f]]}
    integrity['FIELD_ORIGIN'] = not wrong
    out['field_origin_defects'] = wrong
    order = run['order']
    integrity['RAW_CONTIGUITY'] = (bool(order) and order == sorted(order)
                                   and len(order) == len(set(order))
                                   and order == list(range(min(order), max(order) + 1)))
    integrity['DURATION'] = (sum(r['dt_us'] for r in rows.values()) / 1e6
                             >= (meta.get('hold_s') or 0))
    gate_blocks = run['gate_blocks']
    ok_gate = bool(gate_blocks)
    arms = {}
    for i, g in enumerate(gate_blocks):
        if 'malformed' in g:
            ok_gate = False
            continue
        arms[g['block']] = g['arm']
        if (g['block'] != i or (g['arms'], g['period'], g['abba']) != (2, geo['period'], 1)
                or g['arm'] != (0, 1, 1, 0)[i % 4] or g['frame'] != geo['start'] + geo['period'] * i
                or g['text'] != ARMS[g['arm']]):
            ok_gate = False
    integrity['GATEARM'] = ok_gate
    out['gate_blocks'] = len(gate_blocks)
    whole = list(rows.values())
    integrity['NO_FLOOR'] = all(sum(r.get(k, 0) for r in whole) == 0 for k in FLOOR_KEYS)
    integrity['MARKERS_OFF'] = sum(r.get('gm_ops', 0) for r in whole) == 0
    integrity['NO_RECORDING'] = counts['recording'] == 0
    sel = select(rows, arms, geo['period'], geo['start'], geo['first'], geo['keep'])
    out['selection'] = {'pairs': len(sel['pairs']), 'blocks': len(sel['blocks']),
                        'rejected': {str(k): v for k, v in sel['rejected'].items()},
                        'excluded_edge_blocks': sel['excluded_edge_blocks']}
    seen = run['seen']
    last_main = max(seen['main']) if seen['main'] else 0
    missing = sorted(n for n in seen['main'] if geo['start'] < n < last_main
                     and (n not in seen['draw'] or n not in seen['x']))
    integrity['STREAMS_COMPLETE'] = not missing
    integrity['ROW_ARMS'] = all(rows[n]['arm'] == arms[b] and rows[n]['blk'] == b
                                for b, ns in sel['blocks'].items() for n in ns)
    orient = [sum(arms[p[0]] == a for p in sel['pairs']) for a in (0, 1)]
    integrity['AB_BA_BALANCED'] = orient[0] == orient[1] and orient[0] > 0
    out['orientations'] = orient

    env = meta.get('env') or {}
    pins = counts['pin']
    controls['PIN_ONCE'] = pins.get('1', 0) == 1 and sum(pins.values()) == 1
    controls['RECORD_THREAD_TWO'] = counts['rec_started'] == 2
    controls['NO_CHECKPOINT_LINE'] = (counts['ckpt_lines'] == 0 and counts['ckpt_diag'] == 0
                                      and counts['ckpt_off_lines'] == 0)
    controls['NO_GPUHANGABORT'] = counts['hang'] == 0
    controls['NO_FATAL_MARKER'] = not counts['fatal']
    controls['ENV_NO_CHECKPOINTS'] = 'KYTY_GPU_CHECKPOINTS' not in env
    controls['PAIRS'] = len(sel['pairs']) >= MIN_PAIRS
    if not sel['pairs']:
        for k in ('BANDS', 'WORK_SPLIT', 'AREA_VERDICT', 'AREA_SELECTED', 'ARMING'):
            controls[k] = False
        return finish(out, integrity, controls, None)

    means = {b: block_means(rows, ns) for b, ns in sel['blocks'].items()}
    lev = arm_levels(means, arms)
    out['levels'] = {'arm0': lev[0], 'arm1': lev[1]}
    controls['BANDS'] = all(lev[a].get(k) is not None and lo <= lev[a][k] <= hi
                            for k, (lo, hi) in BANDS.items() for a in (0, 1))
    ws = work_split(rows, sel, arms)
    controls['WORK_SPLIT'] = ws['passed']
    out['work_split'] = ws
    av = area_verdict_mirror(run['all_rows'], geo['first'])
    out['area_verdict_mirror'] = av
    controls['AREA_VERDICT'] = bool(av.get('valid'))
    sa = selected_area(rows, sel, arms)
    out['area_selected'] = sa
    controls['AREA_SELECTED'] = bool(sa.get('valid_data') and abs(sa['split_pct']) < AREA_SPLIT_PCT
                                     and sa['match_pct'] >= AREA_MATCH_PCT)
    arm = arming(rows, sel, arms, lev)
    out['arming'] = arm
    controls['ARMING'] = arm['passed']

    pairs = []
    for left, right in sel['pairs']:
        a0 = left if arms[left] == 0 else right
        a1 = right if a0 == left else left
        d = {k: means[a1][k] - means[a0][k] for k in PAIR_KEYS
             if means[a0].get(k) is not None and means[a1].get(k) is not None}
        pairs.append({'blocks': [left, right], 'arm0_block': a0, 'arm1_block': a1, 'd': d})
    out['pairs'] = pairs
    stats = {k: mean_t([p['d'].get(k) for p in pairs]) for k in PAIR_KEYS}
    out['pair_stats'] = stats

    cpu, dt = stats['cpu_net_us'], stats['dt_us']
    rules = {
        'S1_cpu_net_le_-150': cpu['mean'] is not None and cpu['mean'] <= SHIP_US,
        'S2_cpu_net_2se_excludes_0': (cpu['mean'] is not None and cpu['se'] is not None
                                      and cpu['mean'] + 2 * cpu['se'] < 0),
        'S3_dt_same_sign': dt['mean'] is not None and dt['mean'] < 0,
    }
    vstate, vdetail = read_video(video_meta, video_report)
    out['video'] = {'state': vstate, **vdetail}
    decision = {'rules': rules, 'video': vstate}
    out['reported'] = {k: stats[k] for k in ('da_take_us', 'da_miss', 'da_late', 'da_hit',
                                             'da_stale', 'da_walk_us', 'da_queue_us', 'da_walks',
                                             'gpu_busy_us', 'draws')}
    out['reported']['da_wlag_us_arm1'] = lev[1].get('da_wlag_us')
    out['reported']['da_wdepth_arm1'] = lev[1].get('da_wdepth')
    out['predictions'] = predictions(stats, lev, arm)
    out['decision'] = decision
    return finish(out, integrity, controls, decision)


def band_hit(v, lo, hi):
    return v is not None and (lo is None or v >= lo) and (hi is None or v <= hi)


def predictions(stats, lev, arm):
    p = {}

    def add(key, text, value, lo, hi):
        p[key] = {'text': text, 'value': value, 'band': [lo, hi], 'hit': band_hit(value, lo, hi)}

    add('D1', 'arm-1 da_wskip level in [7, 9] a flip', lev[1].get('da_wskip'), 7, 9)
    add('D2', 'arm-1 skip/posts identity within +-1 %', arm.get('skip_over_posts_rel'), -0.01, 0.01)
    add('D3', 'd cpu_net_us in [-700, +100] us', stats['cpu_net_us']['mean'], -700, 100)
    add('D4', 'd da_take_us in [0, +800] us', stats['da_take_us']['mean'], 0, 800)
    add('D5', 'd da_miss in [+20, +250] a flip', stats['da_miss']['mean'], 20, 250)
    add('D6', 'd da_late in [0, +12] a flip', stats['da_late']['mean'], 0, 12)
    add('D7', 'd da_walk_us (walker thread in arm 1) in [+200, +1 000] us',
        stats['da_walk_us']['mean'], 200, 1000)
    add('D8', 'd cpu_net_us <= -150 us (the ship bar is met) - the discriminating prediction, '
              'low confidence', stats['cpu_net_us']['mean'], None, SHIP_US)
    return p


def finish(out, integrity, controls, decision):
    out['integrity'] = integrity
    out['controls'] = controls
    failed = sorted(['integrity:' + k for k, v in integrity.items() if not v]
                    + ['control:' + k for k, v in controls.items() if not v])
    if out['errors']:
        failed.append('protocol')
    out['failed_controls'] = failed
    if out['draft']:
        out['status'] = 'DRAFT'
    else:
        out['status'] = 'INVALID' if failed else 'ADMITTED'
    decision = decision or out.get('decision') or {}
    rules = decision.get('rules') or {}
    measured = bool(rules) and all(rules.values())
    admitted = out['status'] == 'ADMITTED'
    video = decision.get('video')
    if not admitted:
        v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP dawalk=0 (run not admitted)'
    elif not measured:
        v = 'KEEP dawalk=0 (ship rule S1-S3 not met)'
    elif video == 'PASS':
        v = 'SHIP dawalk=1 as the new default (a new build: its video pass is owed, ROADMAP 6)'
    elif video == 'ABSENT':
        v = 'SHIP_PENDING_VIDEO (S1-S4 met; nothing ships until vwk104 is read)'
    else:
        v = 'KEEP dawalk=0 (video pass failed)'
    out['ship_rules_S1_S3_met'] = measured
    out['verdict'] = v
    out['must_not_be_claimed'] = ('a frame-rate figure; 60 FPS; that the walk is gone from the '
                                  'machine (it moved to another thread); any saving from the '
                                  'arm-1 da_walk_us, which is the walker thread; that route A is '
                                  'licensed by this run')
    return out


def fmt(x, digits=1):
    if x is None:
        return 'None'
    if isinstance(x, float):
        return ('%.' + str(digits) + 'f') % x
    return str(x)


def summary(out):
    lines = ['dwk104.py %s status=%s seal=%s' % (out['tag'], out['status'], out.get('pred_sha256'))]
    for e in out['errors'][:12]:
        lines.append('  PROTOCOL: %s' % e)
    if 'selection' in out:
        lines.append('  pairs %d (orientations %s), blocks %d, excluded %s'
                     % (out['selection']['pairs'], out.get('orientations'),
                        out['selection']['blocks'], out['selection']['excluded_edge_blocks']))
    for group in ('integrity', 'controls'):
        for k, v in sorted((out.get(group) or {}).items()):
            lines.append('  [%s] %-9s %s' % ('PASS' if v else 'FAIL', group[:9], k))
    a = out.get('arming') or {}
    for k, v in sorted((a.get('checks') or {}).items()):
        lines.append('  [%s] arming    %s' % ('PASS' if v else 'FAIL', k))
    if a:
        lines.append('  arm-1 kept totals %s  skip/posts-1 %s  drop %s  walks rel %s'
                     % (a.get('arm1_kept_totals'), fmt(a.get('skip_over_posts_rel'), 4),
                        fmt(a.get('drop_fraction'), 4), fmt(a.get('walks_rel'), 4)))
    lev = out.get('levels')
    if lev:
        for k in ('dt_us', 'cpu_net_us', 'draws', 'gpu_busy_us', 'rec_n', 'da_walk_us',
                  'da_queue_us', 'da_take_us', 'da_hit', 'da_miss', 'da_late', 'da_wjobs',
                  'da_wskip', 'da_wdrop', 'da_wlag_us', 'da_wdepth'):
            lines.append('  %-12s arm0 %10s   arm1 %10s' % (k, fmt(lev['arm0'].get(k)),
                                                            fmt(lev['arm1'].get(k))))
    for k in ('cpu_net_us', 'dt_us', 'da_take_us', 'da_miss', 'da_late', 'da_hit', 'da_stale',
              'da_walk_us'):
        s = (out.get('pair_stats') or {}).get(k)
        if s and s.get('n'):
            lines.append('  d %-12s mean %s  2SE %s  t %s  n %d'
                         % (k, fmt(s['mean']), fmt(2 * s['se'] if s['se'] else None),
                            fmt(s['t'], 2), s['n']))
    if 'video' in out:
        lines.append('  video: %s %s' % (out['video']['state'], {k: v for k, v in out['video'].items()
                                                                  if k in ('frames', 'glitches',
                                                                           'checks', 'reason')}))
    for k, v in sorted(((out.get('decision') or {}).get('rules') or {}).items()):
        lines.append('  [%s] ship %s' % ('PASS' if v else 'FAIL', k))
    lines.append('  VERDICT: %s' % out.get('verdict'))
    for k, v in sorted((out.get('predictions') or {}).items()):
        lines.append('  prediction %-3s %s value %s band %s  %s'
                     % (k, 'HIT ' if v['hit'] else 'MISS', fmt(v['value'], 3), v['band'], v['text']))
    lines.append('  failed: %s' % (out.get('failed_controls') or 'none'))
    return '\n'.join(lines)


def parse_keep(text):
    lo, hi = text.split(':')
    return int(lo), int(hi)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('tag')
    ap.add_argument('--root', default=PRODUCTION_ROOT)
    ap.add_argument('--out')
    ap.add_argument('--draft', action='store_true')
    ap.add_argument('--period', type=int)
    ap.add_argument('--start', type=int)
    ap.add_argument('--first', type=int)
    ap.add_argument('--keep', type=parse_keep)
    ap.add_argument('--gates-file', default=GATES_FILE)
    ap.add_argument('--video-meta', default=None)
    ap.add_argument('--video-report', default=None)
    ap.add_argument('--json', action='store_true')
    o = ap.parse_args(argv)
    geometry = {k: v for k, v in (('period', o.period), ('start', o.start), ('first', o.first),
                                  ('keep', o.keep)) if v is not None}
    if not o.draft:
        try:
            check_seal()
        except SealError as exc:
            print(str(exc) + ': refusing to score')
            return 2
        if geometry:
            print('--period/--start/--first/--keep are --draft only')
            return 2
        if Path(o.root).as_posix().rstrip('/') != PRODUCTION_ROOT:
            print('production root must be %s (use --draft elsewhere)' % PRODUCTION_ROOT)
            return 2
        if not re.fullmatch(TAG_RE, o.tag):
            print('tag %r is not a pred/03 tag (dwk104, dwk104b, optional _entry1)' % o.tag)
            return 2
    if o.out:
        path = Path(o.out)
        if path.exists():
            print('output %s exists: never overwritten' % path)
            return 2
        if not o.draft and not path.as_posix().startswith(PRODUCTION_ROOT + '/'):
            print('output must live under %s' % PRODUCTION_ROOT)
            return 2
    try:
        result = evaluate(o.root, o.tag, o.draft, geometry or None, o.gates_file, o.video_meta,
                          o.video_report)
    except SealError as exc:
        print(str(exc) + ': refusing to score')
        return 2
    if not o.draft:
        exe_sha = sha256_file(EXE) if Path(EXE).is_file() else None
        result['installed_exe_sha256'] = exe_sha
        result['integrity']['IDENTITY'] = (exe_sha == result.get('binary_sha256') == BINARY_SHA)
        finish(result, result['integrity'], result['controls'], result.get('decision'))
    print(summary(result))
    text = json.dumps(result, indent=2, sort_keys=True, default=str)
    if o.json:
        print(text)
    if o.out:
        with open(o.out, 'x', encoding='utf-8') as handle:
            handle.write(text + '\n')
        print('wrote %s' % o.out)
    return 0 if result['status'] in ('ADMITTED', 'DRAFT') else 1


if __name__ == '__main__':
    raise SystemExit(main())
