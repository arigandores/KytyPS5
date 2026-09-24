"""Session 111, the SHIP run of knob `daslot` (QueueDrawAhead - the walker thread's M1 queueing - takes only its own
ahead_queue_mutex, with per-slot guards, instead of PipelineCache::m_mutex; design109 A, ROADMAP s0.1 "session 111"
item 2), ABBA `daslot=0|1` with `dawalk=1 dawalklead=1` in both arms, shipping configuration (compute precache on,
knob cspfree=1 by default in BOTH arms), sealed to pred/03_shp111.md.  Derived from session 110's shp110.py (copied,
not imported; make_shp111.py) for the build c8235c90, whose FrameTrace-x rows add da_guard_busy, da_q_taking,
da_hint_defer, da_hint_torn, da_slot_bad, da_q_free, da_chk_ok and da_chk_bad after cs_sync_wait_us (all in the
schema); predictions K1-K6.

    python C:/kyty/s111/shp111.py shp111 [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s111/shp111.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)

Estimator (the executor's decision after session 110, ROADMAP s0.1 item 1; audit110 MAJOR-1): the MAIN estimator is
rows 10..89 of each 90-frame block (KEEP_LO, KEEP_HI = 10, 90).  The ship rule S1/S2, the pair statistics, BANDS,
WORK_SPLIT, AREA_SELECTED, the arm levels, the arming totals and the predictions read it.  The session-110 window,
rows 60..88 (SECONDARY_LO, SECONDARY_HI = 60, 89), is computed with its own selection exactly as shp110.py did and
printed as `secondary` (pair statistics and the S1/S2 values it would give); no admission or decision term reads it.
Pairing is unchanged: whole ABBA quartets, the others excluded as edge blocks.

Ship rule (ROADMAP, decision after session 104; session 108 items 1-2; decision after session 110 item 1): SHIP
daslot=1 as the new default only if the run is ADMITTED - including SYNC_COMPILE: over all rows from frame 2100, sum
cs_sync_new of arm 1 <= that of arm 0 + 2 - and S1 d mean dt_us (main estimator) <= -100 us and S2 its 2SE excludes
0, and the video pass vss111 (gate file gates_slot1.txt = gates_base.txt + daslot=1, pinned, >= 3000 frames, 0
one-frame glitches) reads PASS.  Arming (under control ARMING): the walk checks (unchanged); SLOT_DARK_ARM0 (arm-0
kept rows: sum da_q_free = 0); SLOT_ARMED_ARM1 (arm-1 level of da_q_free >= 1); SLOT_NO_BAD (sum da_slot_bad = 0 over
all rows); DEFAULTS_ON (cspfree_hit level >= 1 in both arms and sum cspfree_bad = 0 over all rows); INSTRUMENTS_DARK.
d cpu_net_us is reported, never deciding: no admission or decision term reads it (derived(), block_means(), pair
stats and the summary only).
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

PRODUCTION_ROOT = 'C:/kyty/s111'
PRED = 'C:/kyty/s111/pred/03_shp111.md'
PRED_SHA = '594e2402c8022dcd0a71ab111cb58f355400b51a261600a48c74eea044125f3f'   # pred/03_shp111.md sealed
PRED_BYTES = 3604       # pred/03_shp111.md sealed
BINARY_SHA = 'c8235c902e08d00782d0cff23528361d194a501ad1899344ca8302c742372a86'
EXE = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
GATES_FILE = 'C:/kyty/s111/gates_base.txt'
GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'

PERIOD, START, FIRST_FRAME = 90, 1800, 2100
KEEP_LO, KEEP_HI = 10, 90                  # MAIN estimator: in-block rows 10..89 (decision after session 110)
SECONDARY_LO, SECONDARY_HI = 60, 89        # the session-110 window, rows 60..88: printed, never deciding
MIN_PAIRS = 60
HOLD_S = 600
ARMS = ('dawalk=1 dawalklead=1 daslot=0', 'dawalk=1 dawalklead=1 daslot=1')
SCHEDULE = '90+1800:%s|%s' % ARMS
TAG_RE = r'shp111b?(?:_entry1)?'

SHIP_US = -100.0          # on d mean dt_us (ROADMAP, decision after session 104)
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
    'cspfam_look': 'x', 'cspfam_skip': 'x', 'cs_sync_new': 'x', 'cs_sync_wait': 'x',
    'cspf_have': 'x', 'cspf_new': 'x',
    'cspfam_clr': 'x', 'cspfree_look': 'x', 'cspfree_hit': 'x', 'cspfree_src_miss': 'x',
    'cspfree_spec_miss': 'x', 'cspfree_mat_fail': 'x', 'cspfree_clr': 'x', 'cspfree_store': 'x',
    'cspfree_bad': 'x', 'cspfree_moved': 'x',
    'cs_sync_new_us': 'x', 'cs_sync_wait_us': 'x',
    'da_guard_busy': 'x', 'da_q_taking': 'x', 'da_hint_defer': 'x', 'da_hint_torn': 'x', 'da_slot_bad': 'x',
    'da_q_free': 'x', 'da_chk_ok': 'x', 'da_chk_bad': 'x',
}
SYNC_SLACK = 2
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
                        'size into shp111.py (only --draft runs without a seal)' % path)
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
    """pred/03 (the lead105 walk arming plus SLOT_DARK_ARM0, SLOT_ARMED_ARM1, SLOT_NO_BAD and DEFAULTS_ON)."""
    checks = {}
    checks['WALK_ARMED_ARM0'] = bool((lev[0].get('da_wjobs') or 0) >= 1
                                     and (lev[0].get('da_wskip') or 0) >= 1)
    checks['WALK_ARMED_ARM1'] = bool((lev[1].get('da_wjobs') or 0) >= 1
                                     and (lev[1].get('da_wskip') or 0) >= 1)
    for a in (0, 1):
        sk = kept_total(rows, sel, arms, a, 'da_wskip')
        jb = kept_total(rows, sel, arms, a, 'da_wjobs')
        dr = kept_total(rows, sel, arms, a, 'da_wdrop')
        po = (jb + dr) if (jb is not None and dr is not None) else None
        idn = rel(sk, po)
        checks['WALK_IDENTITY_ARM%d' % a] = idn is not None and abs(idn) <= ID_TOL
        checks['WALK_DROPS_ARM%d' % a] = bool(po) and dr is not None and dr / po <= DROP_MAX
    skip = kept_total(rows, sel, arms, 1, 'da_wskip')
    jobs = kept_total(rows, sel, arms, 1, 'da_wjobs')
    drop = kept_total(rows, sel, arms, 1, 'da_wdrop')
    posts = (jobs + drop) if (jobs is not None and drop is not None) else None
    ident = rel(skip, posts)
    drop_frac = (drop / posts) if (posts and drop is not None) else None
    rw = rel(lev[1].get('da_walks'), lev[0].get('da_walks'))
    checks['WALKS_SAME'] = rw is not None and abs(rw) <= WALKS_TOL
    # Session 111: the daslot knob dark in arm 0 (no QueueDrawAhead call without m_mutex over the kept rows), armed
    # in arm 1 (level >= 1), and no knob-2 slot-key disagreement anywhere (over all rows; knob 1 never verifies,
    # so a non-zero sum means a wrong build or knob).
    free0 = kept_total(rows, sel, arms, 0, 'da_q_free')
    checks['SLOT_DARK_ARM0'] = free0 == 0
    checks['SLOT_ARMED_ARM1'] = bool((lev[1].get('da_q_free') or 0) >= 1)
    bad = sum(r.get('da_slot_bad', 0) for r in rows.values())
    checks['SLOT_NO_BAD'] = bad == 0
    # The shipping configuration: knob cspfree on by default (session 110) in BOTH arms - hitting (level >= 1 in
    # each arm) and never disagreeing (over all rows).
    hits = [lev[a].get('cspfree_hit') for a in (0, 1)]
    free_bad = sum(r.get('cspfree_bad', 0) for r in rows.values())
    checks['DEFAULTS_ON'] = bool((hits[0] or 0) >= 1 and (hits[1] or 0) >= 1 and free_bad == 0)
    dark = all(kept_total(rows, sel, arms, a, k) == 0 for a in (0, 1) for k in DARK_KEYS)
    checks['INSTRUMENTS_DARK'] = dark
    return {'checks': checks, 'passed': all(bool(v) for v in checks.values()),
            'arm1_kept_totals': {'da_wskip': skip, 'da_wjobs': jobs, 'da_wdrop': drop},
            'skip_over_posts_rel': ident, 'drop_fraction': drop_frac, 'walks_rel': rw,
            'slot_arm0_kept': {'da_q_free': free0}, 'da_slot_bad_all_rows': bad,
            'cspfree_hit_levels': hits, 'cspfree_bad_all_rows': free_bad}


def read_video(meta_path, report_path):
    """pred/03 video pass vss111 (pinned; gate file gates_slot1.txt = gates_base.txt + daslot=1).  Returns
    (state, detail): state in PASS / FAIL / ABSENT."""
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
        'daslot_1_in_gate_text': ' dawalk=1 ' in gates and ' daslot=1 ' in gates,
        'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1',
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


def paired(means, sel, arms):
    """The ABBA pair deltas (arm-1 block mean - arm-0 block mean) over PAIR_KEYS and their mean / SE."""
    pairs = []
    for left, right in sel['pairs']:
        a0 = left if arms[left] == 0 else right
        a1 = right if a0 == left else left
        d = {k: means[a1][k] - means[a0][k] for k in PAIR_KEYS
             if means[a0].get(k) is not None and means[a1].get(k) is not None}
        pairs.append({'blocks': [left, right], 'arm0_block': a0, 'arm1_block': a1, 'd': d})
    return pairs, {k: mean_t([p['d'].get(k) for p in pairs]) for k in PAIR_KEYS}


def ship_rules(dt):
    """S1 / S2 of the ship rule on one estimator's d dt_us statistics."""
    return {
        'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,
        'S2_dt_2se_excludes_0': (dt['mean'] is not None and dt['se'] is not None
                                 and dt['mean'] + 2 * dt['se'] < 0),
    }


def secondary(rows, arms, geo):
    """The session-110 estimator: rows SECONDARY_LO..SECONDARY_HI-1 of each block with its own selection and pairs,
    as the session-110 scorer computed it.  Printed as `secondary`; no admission or decision term reads it
    (decision after session 110, item 1)."""
    sel = select(rows, arms, geo['period'], geo['start'], geo['first'], geo['secondary'])
    out = {'window': list(geo['secondary']), 'deciding': False, 'pairs': len(sel['pairs']),
           'blocks': len(sel['blocks']), 'excluded_edge_blocks': sel['excluded_edge_blocks']}
    if not sel['pairs']:
        out.update(pair_stats={}, levels={}, rules_not_deciding={})
        return out
    means = {b: block_means(rows, ns) for b, ns in sel['blocks'].items()}
    lev = arm_levels(means, arms)
    _, stats = paired(means, sel, arms)
    out['pair_stats'] = stats
    out['levels'] = {k: [lev[0].get(k), lev[1].get(k)] for k in ('dt_us', 'cpu_net_us')}
    out['rules_not_deciding'] = ship_rules(stats['dt_us'])
    return out


def evaluate(root, tag, draft=False, geometry=None, gates_file=GATES_FILE, video_meta=None,
             video_report=None):
    geo = dict(period=PERIOD, start=START, first=FIRST_FRAME, keep=(KEEP_LO, KEEP_HI),
               secondary=(SECONDARY_LO, SECONDARY_HI))
    if geometry:
        if not draft:
            raise ValueError('population geometry can only be changed in --draft')
        geo.update(geometry)
    out = {'scorer': 'shp111.py', 'scorer_sha256': sha256_file(__file__), 'tag': tag, 'pred': PRED, 'draft': bool(draft),
           'pred_sha256': None if draft else check_seal(), 'errors': [], 'notes': [],
           'geometry': dict(geo, keep=list(geo['keep']), secondary=list(geo['secondary']))}
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
    # Session 108 guard, kept verbatim (pred/03): the dispatch-time compile guard over ALL rows from the first
    # frame, by row arm.
    sync = {a: sum(r.get('cs_sync_new', 0) for n, r in rows.items() if n >= geo['first'] and r.get('arm') == a)
            for a in (0, 1)}
    wait = {a: sum(r.get('cs_sync_wait', 0) for n, r in rows.items() if n >= geo['first'] and r.get('arm') == a)
            for a in (0, 1)}
    out['sync_compile'] = {'cs_sync_new': sync, 'cs_sync_wait': wait, 'slack': SYNC_SLACK}
    controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK

    # The MAIN estimator (rows KEEP_LO..KEEP_HI-1 of each block): the pair statistics every rule reads.
    pairs, stats = paired(means, sel, arms)
    out['pairs'] = pairs
    out['pair_stats'] = stats
    # The session-110 window (rows SECONDARY_LO..SECONDARY_HI-1): its own selection, printed, read by no term.
    out['secondary'] = secondary(rows, arms, geo)

    cpu, dt = stats['cpu_net_us'], stats['dt_us']
    rules = ship_rules(dt)
    vstate, vdetail = read_video(video_meta, video_report)
    out['video'] = {'state': vstate, **vdetail}
    decision = {'rules': rules, 'video': vstate}
    out['reported'] = {k: stats[k] for k in ('da_take_us', 'da_miss', 'da_late', 'da_hit',
                                             'da_stale', 'da_walk_us', 'da_queue_us', 'da_walks',
                                             'gpu_busy_us', 'draws')}
    out['reported']['da_wlag_us_arm1'] = lev[1].get('da_wlag_us')
    out['reported']['da_wdepth_arm1'] = lev[1].get('da_wdepth')
    for k in ('da_q_free', 'da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn'):
        out['reported'][k + '_levels'] = [lev[0].get(k), lev[1].get(k)]
    out['predictions'] = predictions(stats, lev, arm)
    out['decision'] = decision
    return finish(out, integrity, controls, decision)


def band_hit(v, lo, hi):
    return v is not None and (lo is None or v >= lo) and (hi is None or v <= hi)


def predictions(stats, lev, arm):
    p = {}

    def add(key, text, value, lo, hi):
        p[key] = {'text': text, 'value': value, 'band': [lo, hi], 'hit': band_hit(value, lo, hi)}

    add('K1', 'arm-1 da_q_free level in [800, 1400] a flip (every QueueDrawAhead call off m_mutex)',
        lev[1].get('da_q_free'), 800, 1400)
    add('K2', 'arm-0 da_q_free level = 0 (the knob dark)', lev[0].get('da_q_free'), 0, 0)
    add('K3', 'd mean dt_us (main estimator, rows 10..89) in [-400, 0] us', stats['dt_us']['mean'], -400, 0)
    add('K4', 'd mean dt_us (main estimator) <= -100 us (the ship bar) - the discriminating prediction, '
        'medium-low confidence', stats['dt_us']['mean'], None, SHIP_US)
    add('K5', 'd da_miss in [-40, +40] a flip', stats['da_miss']['mean'], -40, 40)
    add('K6', 'arm-1 da_guard_busy level <= 5 a flip', lev[1].get('da_guard_busy'), None, 5)
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
        v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP daslot=0 (run not admitted)'
    elif not measured:
        v = 'KEEP daslot=0 (ship rule S1-S2 on mean dt not met)'
    elif video == 'PASS':
        v = 'SHIP daslot=1 as the new default (a new build: its video pass is owed, ROADMAP 6)'
    elif video == 'ABSENT':
        v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vss111 is read)'
    else:
        v = 'KEEP daslot=0 (video pass failed)'
    out['ship_rules_S1_S2_met'] = measured
    out['verdict'] = v
    out['must_not_be_claimed'] = ('60 FPS; a game-speed figure on the unpinned default setup; any '
                                  'gain from d cpu_net_us alone; that route A is licensed by this run; a size '
                                  'read from the secondary 60-88 window')
    return out


def fmt(x, digits=1):
    if x is None:
        return 'None'
    if isinstance(x, float):
        return ('%.' + str(digits) + 'f') % x
    return str(x)


def summary(out):
    lines = ['shp111.py %s status=%s seal=%s' % (out['tag'], out['status'], out.get('pred_sha256'))]
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
        lines.append('  daslot arm-0 kept totals %s  da_slot_bad over all rows %s  cspfree_hit levels %s  '
                     'cspfree_bad over all rows %s'
                     % (a.get('slot_arm0_kept'), a.get('da_slot_bad_all_rows'), a.get('cspfree_hit_levels'),
                        a.get('cspfree_bad_all_rows')))
    lev = out.get('levels')
    if lev:
        for k in ('dt_us', 'cpu_net_us', 'draws', 'gpu_busy_us', 'rec_n', 'da_walk_us',
                  'da_queue_us', 'da_take_us', 'da_hit', 'da_miss', 'da_late', 'da_wjobs',
                  'da_wskip', 'da_wdrop', 'da_wlag_us', 'da_wdepth', 'da_qcall', 'da_q_free',
                  'da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'cspfree_hit', 'cspf_have',
                  'cspf_new'):
            lines.append('  %-12s arm0 %10s   arm1 %10s' % (k, fmt(lev['arm0'].get(k)),
                                                            fmt(lev['arm1'].get(k))))
    if out.get('pair_stats'):
        keep = (out.get('geometry') or {}).get('keep') or [KEEP_LO, KEEP_HI]
        lines.append('  main estimator (decides): rows %d..%d of each block' % (keep[0], keep[1] - 1))
    for k in ('cpu_net_us', 'dt_us', 'da_take_us', 'da_miss', 'da_late', 'da_hit', 'da_stale',
              'da_walk_us', 'gpu_busy_us'):
        s = (out.get('pair_stats') or {}).get(k)
        if s and s.get('n'):
            lines.append('  d %-12s mean %s  2SE %s  t %s  n %d'
                         % (k, fmt(s['mean']), fmt(2 * s['se'] if s['se'] else None),
                            fmt(s['t'], 2), s['n']))
    sec = out.get('secondary')
    if sec:
        lines.append('  secondary estimator (rows %d..%d, never deciding): pairs %d, blocks %d, excluded %s'
                     % (sec['window'][0], sec['window'][1] - 1, sec['pairs'], sec['blocks'],
                        sec['excluded_edge_blocks']))
        for k in ('cpu_net_us', 'dt_us'):
            s = (sec.get('pair_stats') or {}).get(k)
            if s and s.get('n'):
                lines.append('  secondary d %-12s mean %s  2SE %s  t %s  n %d'
                             % (k, fmt(s['mean']), fmt(2 * s['se'] if s['se'] else None),
                                fmt(s['t'], 2), s['n']))
        for k, v in sorted((sec.get('rules_not_deciding') or {}).items()):
            lines.append('  secondary would %s %s (not deciding)' % ('PASS' if v else 'FAIL', k))
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
    ap.add_argument('--secondary', type=parse_keep)
    ap.add_argument('--gates-file', default=GATES_FILE)
    ap.add_argument('--video-meta', default=None)
    ap.add_argument('--video-report', default=None)
    ap.add_argument('--json', action='store_true')
    o = ap.parse_args(argv)
    geometry = {k: v for k, v in (('period', o.period), ('start', o.start), ('first', o.first),
                                  ('keep', o.keep), ('secondary', o.secondary)) if v is not None}
    if not o.draft:
        try:
            check_seal()
        except SealError as exc:
            print(str(exc) + ': refusing to score')
            return 2
        if geometry:
            print('--period/--start/--first/--keep/--secondary are --draft only')
            return 2
        if Path(o.root).as_posix().rstrip('/') != PRODUCTION_ROOT:
            print('production root must be %s (use --draft elsewhere)' % PRODUCTION_ROOT)
            return 2
        if not re.fullmatch(TAG_RE, o.tag):
            print('tag %r is not a pred/03 tag (shp111, shp111b, optional _entry1)' % o.tag)
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
