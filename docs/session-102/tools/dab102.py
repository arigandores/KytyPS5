"""Session 102, candidate 3 scorer (knob `dabatch`), sealed to pred/03_dabatch.md as amended by
the sealed addendum pred/05_dabatch_addendum.md.

    python C:/kyty/s102/dab102.py <tag> --phase pilot|decision --out <json>
                                 [--root C:/kyty/s102] [--pilot-score <json>]
    python C:/kyty/s102/dab102.py <tag> --phase ... --root <any> --mechanics-only   # never admits

Offline only: it never launches the game, never rebuilds, never retries and never overwrites an
output (the --out file is opened with mode 'x' and an existing one is refused before any work).
It refuses to score (exit 2) unless BOTH seals are byte-for-byte the sealed texts:
pred/03_dabatch.md (sha256 f828e257..., 6 909 B) and pred/05_dabatch_addendum.md (sha256
b889c57a..., 2 347 B); the output JSON records both hashes.  Everything deciding is the sealed
text; nothing is widened.  pred/05 replaces two rules of pred/03 4 (marked [pred/05] below) and
changes nothing else (pred/05 4):

  pred/03 2   population of session 101 pred/01 4: blocks of 90 from frame 1800, rows idx 60..88
              (29) of each block, blocks with a kept frame below 2100 rejected, pairs (2k, 2k+1)
              inside complete ABBA quartets only; per block the arithmetic mean over its kept
              rows; per pair the difference (non-default arm) - (arm dabatch=64).
              b_hat = mean_pairs d(da_queue_us) / mean_pairs d(da_qcall), 90 % percentile
              bootstrap over pairs (20 000 resamples, seed 102);
              Q64 = median da_qcall (64 arm), W = median da_walks, R = median(da_req + da_nohint),
              Q1024 = W + R/1024, S_hat = b_hat * (Q64 - Q1024) with its bootstrap interval;
              pilot: upper bound of S_hat < 60 us => CLOSED (no second run), else RUN_2.
              Mechanism (reported): d(da_walk_us) against d(da_queue_us); > 2x => b_hat is a
              LOWER bound (stated, not repaired).
  pred/03 3   decision run: SHIP dabatch=1024 only if (1) d cpu_net_us mean < 0 and t <= -2.0,
              (2) d da_walk_us mean < 0 and t <= -2.0, (3) |d da_late| <= 0.10, d da_hit >= -1 % of
              the 64 arm's da_hit, d da_miss <= +1 % of that da_hit, d da_busy <= +5, (4) every
              control of 4.  Otherwise the default stays 64.
  pred/03 4   controls (both runs): arm medians dt_us [28000, 40000], rec_n [9000, 13000],
              gpu_busy_us [10000, 16000]; area split valid as in session 101; exactly one
              'GpuClockPin: mode 1', two 'RecordThread: started', no 'GPU checkpoints' line, no
              GpuHangAbort, no fatal marker; KYTY_GPU_CHECKPOINTS absent from env;
              pairs >= 10 (pilot) / >= 30 (decision).
  pred/05 1   [replaces pred/03 4 "work split"] session 101's own definition (cen100.py
              population, carried by cm101.py:296): work = mean of `draws` over ALL retained rows
              (the selected blocks' kept rows) of the non-default arm / the same mean of the 64
              arm - 1; WORK_SPLIT passes iff |work| < 0.5 % (strict).  The rows are grouped by
              their own `arm` field, exactly as cen100.population does (ROW_ARMS guarantees it
              equals the GateArm arm).  pred/03's block-median and row-median readings are
              printed as REPORTED and never decide.
  pred/05 2   [replaces pred/03 4 "arming"] each arm's median da_qcall must lie in
              [0.75 * R/B, 1.25 * (W + R/B)] (closed), W and R the 64 arm's medians, B the arm's
              own batch (64 for arm 0; 8 or 1024 for arm 1).  Both intervals and both observed
              medians are reported; pred/03's +-25 % ratio deviation is a note, never deciding.
  pred/05 3   da_qcall is read from FrameTrace-x only; seen on any other line => FIELD_ORIGIN
              fails the run (EXPECTED_LINE below).
  pred/03 5   Q1-Q3 are scored and printed with no decision weight.

Conventions this file fixes because the seal does not spell them out (each one stated here so an
audit can attack it):
  * An arm's "median" (Q64, W, R, the dt/rec_n/gpu_busy bands, the arming da_qcall, da_hit) is
    the median over that arm's SELECTED blocks of the per-block mean over kept rows (pred/03 2:
    "Per block: arithmetic means over its kept rows").  The row-level median is printed beside it
    and never decides.  `draws` is NOT judged by a median any more (pred/05 1).
  * "d X" in the ship rule and the safety bands is the mean over pairs of the per-pair difference;
    t = mean / (sd / sqrt(n)) with the sample sd.
  * Bootstrap: one random.Random(102) generator; each resample draws n pair indices with
    randrange(n); the statistic is the ratio of the resampled sums (equal to the ratio of means);
    interval ends are the 5th / 95th percentiles, linearly interpolated (numpy 'linear').  S_hat's
    interval is the b_hat resamples times the fixed (Q64 - Q1024); Q64 and Q1024 are not resampled.
  * "Area split valid as in session 101" = BOTH (a) this file's mirror of area_verdict.py over
    every flip n >= 2100 (whole-arm split < 1.0 %, adjacent-block pair match >= 90 % at 0.5 %
    tolerance with >= 8 flips a block, whole-arm work < 0.5 %) and (b) session 101 cm101.py's
    selected-population AREA_SPLIT (< 1 %) and AREA_MATCH (>= 90 %).
  * "Fatal marker" = the session-101 scorer's set (cen100.FATAL), which contains the four texts
    named in the brief: '--- Error ---', '--- Fatal Error ---', '--- std::terminate ---',
    '--- abort() ---', plus ErrorDeviceLost, 'Unhandled exception:', 'GpuWaitSlow:' and
    'AsyncPipelines: skipped draw'.  GpuHangAbort is its own control.  Log AND stdout, every line.
  * 'GPU checkpoints' line: any line of log or stdout containing 'GPU checkpoints' or
    'diagnostic checkpoints enabled'.
  * 'two RecordThread: started' = exactly two; 'GpuClockPin: mode 1' exactly once and no
    GpuClockPin line of another mode.
  * da_qcall: pred/03 1 writes "(FrameTrace-draw)"; the build prints it on FrameTrace-x
    (videoOut.cpp:2426, the `named` table; pred/05 3).  Every field is read from the line the build prints it
    on (EXPECTED_LINE below, each verified against log_cm101d.txt or the source) and a field seen
    on any other line fails the FIELD_ORIGIN control; a missing field is a SCHEMA failure, never a
    zero.
  * The integrity controls of session 101's cm101.py are carried and decide (PREREG_PINNED,
    IDENTITY, SCHEMA, FIELD_ORIGIN, RAW_CONTIGUITY, DURATION, GATEARM (+ arm texts), ROW_ARMS,
    STREAMS_COMPLETE, AB_BA_BALANCED, NO_FLOOR, MARKERS_OFF, NO_RECORDING) together with the launch
    protocol of pred/03 2 (env, schedule, gates file, one attempt, hold).
  * The decision run is licensed only by an ADMITTED pilot score that says RUN_2 (pred/03 3 "only
    if 2 says so") AND was scored under both seals (its pred_sha256 and addendum_sha256 are the
    sealed ones: a pilot scored before pred/05 does not license); --pilot-score names it (default
    runs102/dab102a_score.json).
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import re
import statistics
import sys

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PRODUCTION_ROOT = 'C:/kyty/s102'
PRED = 'C:/kyty/s102/pred/03_dabatch.md'
PRED_SHA = 'f828e2578a1e68e2dbf99e976be7ce49f4041e6631d96c4773f0d23642b6135e'
PRED_BYTES = 6909
PRED05 = 'C:/kyty/s102/pred/05_dabatch_addendum.md'
PRED05_SHA = 'b889c57a6f8c0f56eaa3ac43f68e9ea168dfef32b4a7122cb0b918fee5e7686d'
PRED05_BYTES = 2347
BINARY_SHA = '346ba4f6448c35cba8677101a1599c6ddd0b907d3ea76015ada692cd3b3dc776'
EXE = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
GATES_FILE = 'C:/kyty/s102/gates_base.txt'
GATES_SHA = '00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8'
DEFAULT_PILOT_SCORE = 'C:/kyty/s102/runs102/dab102a_score.json'

PERIOD, START, FIRST_FRAME = 90, 1800, 2100
KEEP_LO, KEEP_HI = 60, 89                  # scheduled[60:89] -> 29 rows, idx 60..88
PHASES = {
    'pilot': dict(B=8, hold=300, min_pairs=10, tag='dab102a',
                  schedule='90+1800:dabatch=64|dabatch=8'),
    'decision': dict(B=1024, hold=900, min_pairs=30, tag='dab102b',
                     schedule='90+1800:dabatch=64|dabatch=1024'),
}
BOOT_N, BOOT_SEED, CI_LEVEL = 20000, 102, 0.90
USEFUL_US = 60.0                            # session 92 usefulness threshold, pred/03 2
BANDS = {'dt_us': (28000.0, 40000.0), 'rec_n': (9000.0, 13000.0),
         'gpu_busy_us': (10000.0, 16000.0)}
WORK_TOL = 0.005                            # pred/05 1: strict |work| < 0.5 %
ARM_LO, ARM_HI = 0.75, 1.25                 # pred/05 2: [0.75 R/B, 1.25 (W + R/B)]
OLD_ARMING_TOL = 0.25                       # pred/03 4 ratio rule, replaced: a note only
SHIP_T = -2.0
LATE_BAND = 0.10
HIT_FRAC = 0.01
MISS_FRAC = 0.01
BUSY_MAX = 5.0
MECH_FACTOR = 2.0
Q1_BAND = (0.05, 1.5)
Q3_BAND = 0.05
AREA_SPLIT_PCT, AREA_MATCH_PCT, AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 8

# Where the build prints each field (verified on log_cm101d.txt; da_qcall from the source).
EXPECTED_LINE = {
    'dt_us': 'main', 'draws': 'main', 'cpu_gpu_us': 'main', 'gpu_busy_us': 'main',
    'arm': 'main', 'blk': 'main',
    'spin_gpu_us': 'draw', 'rec_n': 'draw', 'da_walks': 'draw', 'da_walk_us': 'draw',
    'da_nohint': 'draw', 'da_busy': 'draw', 'da_hit': 'draw', 'da_late': 'draw',
    'da_miss': 'draw', 'da_queue_us': 'draw',
    'da_req': 'x', 'da_qcall': 'x', 'rt_att': 'x', 'rt_kpx': 'x',
    'bf_n': 'x', 'bf_disp': 'x', 'bf_skip': 'x', 'bf_clr_skip': 'x', 'bf_skip_drop': 'x',
    'gm_ops': 'x',
}
FIELDS = tuple(EXPECTED_LINE)
FLOOR_KEYS = ('bf_n', 'bf_disp', 'bf_skip', 'bf_clr_skip', 'bf_skip_drop')
LINE_KIND = ((b'FrameTrace: ', 'main'), (b'FrameTrace-draw: ', 'draw'), (b'FrameTrace-x: ', 'x'))
RE_TOKEN = re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')
# pred/05 3: da_qcall on ANY line other than FrameTrace-x fails the run (FIELD_ORIGIN), including
# lines this scorer does not otherwise parse (FrameTrace-rp, -direct, GateArm, ...).
RE_QCALL = re.compile(rb'(?<![A-Za-z_0-9])da_qcall=')
RE_LINE_LABEL = re.compile(rb'^([A-Za-z_][A-Za-z_0-9-]*):')

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

PAIR_KEYS = ('cpu_net_us', 'da_queue_us', 'da_qcall', 'da_walk_us', 'da_late', 'da_hit',
             'da_miss', 'da_busy', 'draws', 'dt_us', 'gpu_busy_us', 'rec_n')
ARM_KEYS = ('dt_us', 'rec_n', 'gpu_busy_us', 'draws', 'da_qcall', 'da_walks', 'R', 'da_hit',
            'da_miss', 'da_late', 'da_busy', 'da_queue_us', 'da_walk_us', 'cpu_net_us',
            'da_req', 'da_nohint')


class SealError(RuntimeError):
    pass


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_seal(path=None, want_sha=None, want_bytes=None):
    """pred/03 by default.  Defaults are resolved at CALL time (module globals), never frozen at
    definition time.  Checks sha256 AND size."""
    path = PRED if path is None else path
    want_sha = PRED_SHA if want_sha is None else want_sha
    want_bytes = PRED_BYTES if want_bytes is None else want_bytes
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise SealError('sealed pre-registration unreadable: %s (%s)' % (path, exc))
    got = hashlib.sha256(data).hexdigest()
    if got != want_sha or len(data) != want_bytes:
        raise SealError('SEALED PRE-REGISTRATION CHANGED: %s sha256 %s (%d B), sealed %s (%d B)'
                        % (path, got, len(data), want_sha, want_bytes))
    return got


def check_addendum(path=None):
    """pred/05 (the sealed addendum), sha256 AND size, resolved at call time."""
    return check_seal(PRED05 if path is None else path, PRED05_SHA, PRED05_BYTES)


def check_seals(seal_path=None, addendum_path=None):
    """Both seals or nothing: raises SealError when either differs from its sealed bytes."""
    return {'pred03': check_seal(seal_path), 'pred05': check_addendum(addendum_path)}


# ------------------------------------------------------------------------------------ statistics
def quantile(sorted_values, q):
    """numpy.percentile(..., method='linear') on an already sorted list."""
    n = len(sorted_values)
    if n == 0:
        return None
    pos = q * (n - 1)
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    if lo == hi:
        return sorted_values[lo]
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo)


def ratio_bootstrap(num, den, n_boot=BOOT_N, seed=BOOT_SEED):
    """All n_boot resampled ratios sum(num*)/sum(den*), sorted; None if any denominator is 0."""
    n = len(num)
    if n == 0:
        return None
    rng = random.Random(seed)
    out = []
    for _ in range(n_boot):
        sn = sd = 0.0
        for _ in range(n):
            i = rng.randrange(n)
            sn += num[i]
            sd += den[i]
        if sd == 0:
            return None
        out.append(sn / sd)
    out.sort()
    return out


def mean_t(values):
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
    values = list(values)
    return statistics.median(values) if values else None


# ------------------------------------------------------------------------------------ reading
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
        counts['ckpt_lines'] += 1
    if b'diagnostic checkpoints enabled' in line:
        counts['ckpt_diag'] += 1
    if b'Recording:' in line:
        counts['recording'] += 1


def new_counts():
    return {'hang': 0, 'fatal': {}, 'pin': {}, 'rec_started': 0, 'ckpt_lines': 0,
            'ckpt_diag': 0, 'recording': 0}


def read_run(log_path, stdout_path):
    """One streaming pass over the log (and the stdout for the markers).

    Returns rows {n: {field: int}} built ONLY from each field's expected line, the main-line
    order, schema defects, the line kinds each wanted field was seen on, the frames each stream
    carried, the GateArm blocks and the marker counts."""
    rows, order, bad = {}, [], []
    origin = {f: set() for f in FIELDS}
    seen = {'main': set(), 'draw': set(), 'x': set()}
    gate_blocks = []
    counts = new_counts()
    gate_re = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) '
                         rb'period=(\d+) abba=(\d+) text=(.*)$')
    wanted = {f.encode(): f for f in FIELDS}
    with open(log_path, 'rb') as handle:
        for raw in handle:
            scan_markers(raw, counts)
            if (b'da_qcall=' in raw and not raw.startswith(b'FrameTrace-x: ')
                    and RE_QCALL.search(raw)):
                if raw.startswith(b'FrameTrace: '):
                    origin['da_qcall'].add('main')
                elif raw.startswith(b'FrameTrace-draw: '):
                    origin['da_qcall'].add('draw')
                else:
                    label = RE_LINE_LABEL.match(raw)
                    origin['da_qcall'].add('other:' + (label.group(1).decode('ascii', 'replace')
                                                       if label else '?'))
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
                    bad.append((kind, n, field))
    if stdout_path is not None and Path(stdout_path).is_file():
        with open(stdout_path, 'rb') as handle:
            for raw in handle:
                scan_markers(raw, counts)
    complete = {n: r for n, r in rows.items() if all(f in r for f in FIELDS)}
    return {'rows': complete, 'all_rows': rows, 'order': order, 'bad': bad,
            'origin': {f: sorted(v) for f, v in origin.items()}, 'seen': seen,
            'gate_blocks': gate_blocks, 'counts': counts}


# ------------------------------------------------------------------------------------ population
def select(rows, arms):
    """session 101 pred/01 4 (cen100.select), carried verbatim."""
    eligible, rejected = {}, {}
    for block in sorted(arms):
        expected = list(range(START + 1 + PERIOD * block, START + 1 + PERIOD * (block + 1)))
        if not all(n in rows for n in expected):
            rejected[block] = 'incomplete block'
            continue
        kept = expected[KEEP_LO:KEEP_HI]
        if len(kept) != 29 or min(kept) < FIRST_FRAME:
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
    return dict(row, cpu_net_us=row['cpu_gpu_us'] - row['spin_gpu_us'],
                R=row['da_req'] + row['da_nohint'])


def block_means(rows, ns, keys=None):
    group = [derived(rows[n]) for n in ns]
    if keys is None:
        keys = set(PAIR_KEYS) | set(ARM_KEYS) | {'rt_att', 'rt_kpx'}
    out = {k: statistics.fmean(r[k] for r in group) for k in keys}
    out['rows'] = len(group)
    return out


def arm_block_medians(rows, sel, arms, keys):
    """Per arm: median over its selected blocks of the per-block mean over kept rows."""
    means = {b: block_means(rows, ns, keys) for b, ns in sel['blocks'].items()}
    return {a: {k: median_or_none(means[b][k] for b in means if arms[b] == a) for k in keys}
            for a in (0, 1)}


def work_split(rows, sel, arms):
    """pred/05 1 = session 101 cen100.population work_pct: mean of `draws` over ALL retained rows
    (sel['rows'], the selected blocks' kept rows) of arm 1 / the same mean of arm 0 - 1, rows
    grouped by their own `arm` field as cen100 does; pass iff |work| < WORK_TOL (strict).
    pred/03's block-median and row-median readings ride along as REPORTED (never deciding)."""
    retained = [rows[n] for n in sel['rows']]
    groups = {a: [r['draws'] for r in retained if r['arm'] == a] for a in (0, 1)}
    out = {'definition': 'pred/05 1: mean of draws over all retained rows, arm 1 / arm 0 - 1, '
                         'strict |work| < %.3f' % WORK_TOL,
           'rows_arm0': len(groups[0]), 'rows_arm1': len(groups[1]), 'tolerance': WORK_TOL}
    mean0 = statistics.fmean(groups[0]) if groups[0] else None
    mean1 = statistics.fmean(groups[1]) if groups[1] else None
    work = (mean1 / mean0 - 1) if (mean0 and mean1 is not None) else None
    out.update(mean_draws_arm0=mean0, mean_draws_arm1=mean1, work=work,
               passed=work is not None and abs(work) < WORK_TOL)
    blk = arm_block_medians(rows, sel, arms, ('draws',))
    row_med = {a: median_or_none(groups[a]) for a in (0, 1)}
    out['reported_block_median'] = (blk[1]['draws'] / blk[0]['draws'] - 1
                                    if blk[0]['draws'] and blk[1]['draws'] is not None else None)
    out['reported_row_median'] = (row_med[1] / row_med[0] - 1
                                  if row_med[0] and row_med[1] is not None else None)
    out['reported_note'] = ('pred/03 4 readings (median draws ratio - 1 <= 0.5 %), replaced by '
                            'pred/05 1: REPORTED, never deciding')
    return out


def arming_bounds(w, r, batch):
    """pred/05 2: [0.75 * R/B, 1.25 * (W + R/B)] for batch B."""
    if w is None or r is None or not batch:
        return None
    return [ARM_LO * r / batch, ARM_HI * (w + r / batch)]


def arming_check(arm_med, batch1):
    """pred/05 2: BOTH arms' block-median da_qcall inside their closed intervals, W and R the 64
    arm's medians, B = 64 for arm 0 and `batch1` (8 or 1024) for arm 1.  pred/03's +-25 % ratio
    deviation is computed and kept as a note only."""
    w, r = arm_med[0]['da_walks'], arm_med[0]['R']
    out = {'rule': 'pred/05 2: each arm median da_qcall in [%.2f R/B, %.2f (W + R/B)], W and R of '
                   'the 64 arm' % (ARM_LO, ARM_HI), 'W': w, 'R': r, 'arms': {}}
    ok = True
    for arm, batch in ((0, 64), (1, batch1)):
        q = arm_med[arm]['da_qcall']
        bounds = arming_bounds(w, r, batch)
        inside = q is not None and bounds is not None and bounds[0] <= q <= bounds[1]
        out['arms']['arm%d_dabatch%d' % (arm, batch)] = {
            'B': batch, 'observed_median_da_qcall': q, 'interval': bounds, 'inside': inside}
        ok = ok and inside
    out['passed'] = ok
    q64, qb = arm_med[0]['da_qcall'], arm_med[1]['da_qcall']
    q_pred = (w + r / batch1) if (w is not None and r is not None) else None
    dev = (qb / q_pred - 1) if (qb is not None and q_pred) else None
    out['old_rule_note'] = {
        'text': 'pred/03 4 ratio rule (|obs ratio / ((W + R/B)/Q64) - 1| <= 25 %), replaced by '
                'pred/05 2: a NOTE, never deciding',
        'Q64': q64, 'Q_B_observed': qb, 'Q_B_predicted': q_pred,
        'ratio_observed': (qb / q64) if (qb is not None and q64) else None,
        'ratio_predicted': (q_pred / q64) if (q_pred is not None and q64) else None,
        'relative_deviation': dev, 'old_tolerance': OLD_ARMING_TOL,
        'old_rule_would_pass': dev is not None and abs(dev) <= OLD_ARMING_TOL,
        'calls_per_walk_64': (q64 / w) if (q64 is not None and w) else None}
    return out


def area_of(rows_list):
    att = sum(r['rt_att'] for r in rows_list)
    return sum(r['rt_kpx'] for r in rows_list) / att if att > 0 else None


def area_verdict_mirror(all_rows, first_frame=FIRST_FRAME, tol=AREA_TOL_PCT,
                        min_flips=AREA_MIN_FLIPS):
    """area_verdict.py judge(), over every flip n >= first_frame that carries the fields."""
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
    """cm101.py population(): selected-row whole-arm split and per-pair match."""
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


# ------------------------------------------------------------------------------------ evaluate
def evaluate(root, tag, phase, mechanics=False, pilot_score=None, seal_path=None,
             gates_file=GATES_FILE, addendum_path=None):
    """Scores one run.  Raises SealError when either sealed text (pred/03, pred/05) is not the
    sealed text."""
    seals = check_seals(seal_path, addendum_path)
    cfg = PHASES[phase]
    root = Path(root)
    log = root / ('log_%s.txt' % tag)
    stdout = root / ('stdout_%s.txt' % tag)
    meta_path = root / ('%s.json' % tag)
    out = {'tag': tag, 'phase': phase, 'scorer': 'dab102.py', 'pred': PRED,
           'pred_sha256': seals['pred03'], 'pred_bytes': PRED_BYTES,
           'addendum': PRED05, 'addendum_sha256': seals['pred05'], 'addendum_bytes': PRED05_BYTES,
           'mechanics_only': bool(mechanics), 'B': cfg['B'], 'errors': [], 'notes': []}
    err = out['errors'].append
    for p in (log, stdout, meta_path):
        if not p.is_file():
            err('missing input: %s' % p)
    if out['errors']:
        return finish(out, {'INPUTS': False}, {}, None, mechanics)
    out['raw_sha256'] = {'log': sha256_file(log), 'stdout': sha256_file(stdout),
                         'meta': sha256_file(meta_path)}
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    out['binary_sha256'] = meta.get('binary_sha256')

    # ---------------------------------------------------------------- launch protocol (pred/03 2)
    env = meta.get('env') or {}
    kyty = {k: v for k, v in env.items() if k.startswith('KYTY_')}
    for key, value in ENV_EXPECTED.items():
        if kyty.get(key) != value:
            err('env %s=%r, expected %r' % (key, kyty.get(key), value))
    if kyty.get('KYTY_GATE_SCHEDULE') != cfg['schedule']:
        err('env KYTY_GATE_SCHEDULE=%r, expected %r' % (kyty.get('KYTY_GATE_SCHEDULE'),
                                                        cfg['schedule']))
    if (meta.get('schedule') or '') != cfg['schedule']:
        err('meta schedule %r, expected %r' % (meta.get('schedule'), cfg['schedule']))
    for key in ENV_PRESENT:
        if key not in kyty:
            err('env %s absent' % key)
    allowed = set(ENV_EXPECTED) | set(ENV_PRESENT) | {'KYTY_GPU_CHECKPOINTS'}
    extra = sorted(set(kyty) - allowed)
    if extra:
        err('env carries KYTY_* variables outside the sealed launch: %s' % extra)
    if 'KYTY_REC' in kyty:
        err('KYTY_REC present: pred/03 2 requires it absent entirely')
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
        if (a.get('hold_s') or 0) < cfg['hold'] - 5:
            err('hold_s %r below %d' % (a.get('hold_s'), cfg['hold'] - 5))
    if meta.get('hold_s') != cfg['hold']:
        err('meta hold_s %r, expected %d' % (meta.get('hold_s'), cfg['hold']))

    integrity, controls = {}, {}
    prereg = meta.get('prereg') or {}
    integrity['PREREG_PINNED'] = (prereg.get('sha256') == PRED_SHA
                                  and prereg.get('bytes') == PRED_BYTES)
    integrity['BINARY_SEALED'] = meta.get('binary_sha256') == BINARY_SHA

    if phase == 'decision':
        lic = None
        path = Path(pilot_score or DEFAULT_PILOT_SCORE)
        try:
            pil = json.loads(path.read_text(encoding='utf-8'))
            lic = (pil.get('status') == 'ADMITTED_PILOT' and pil.get('pilot_decision') == 'RUN_2'
                   and pil.get('pred_sha256') == PRED_SHA
                   and pil.get('addendum_sha256') == PRED05_SHA)
            out['pilot_licence'] = {'path': str(path), 'status': pil.get('status'),
                                    'pilot_decision': pil.get('pilot_decision'),
                                    'pred_sha256': pil.get('pred_sha256'),
                                    'addendum_sha256': pil.get('addendum_sha256'),
                                    'S_hat_ci_us': pil.get('estimates', {}).get('S_hat_ci_us')}
        except (OSError, ValueError):
            out['pilot_licence'] = {'path': str(path), 'status': None}
        if not lic:
            err('decision run not licensed: no ADMITTED pilot score saying RUN_2 under both seals '
                '(pred/03 + pred/05) at %s' % path)

    # ---------------------------------------------------------------- the log
    run = read_run(log, stdout)
    rows, counts = run['rows'], run['counts']
    out['markers'] = counts
    out['field_origin'] = run['origin']
    integrity['SCHEMA'] = not run['bad']
    out['schema_bad'] = [list(x) for x in run['bad'][:20]]
    wrong_origin = {f: v for f, v in run['origin'].items() if v != [EXPECTED_LINE[f]]}
    integrity['FIELD_ORIGIN'] = not wrong_origin
    out['field_origin_defects'] = wrong_origin
    order = run['order']
    integrity['RAW_CONTIGUITY'] = (bool(order) and order == sorted(order)
                                   and len(order) == len(set(order))
                                   and order == list(range(min(order), max(order) + 1)))
    integrity['DURATION'] = (sum(r['dt_us'] for r in rows.values()) / 1e6
                             >= (meta.get('hold_s') or 0))

    gate_blocks = run['gate_blocks']
    want_text = ('dabatch=64', 'dabatch=%d' % cfg['B'])
    ok_gate = bool(gate_blocks)
    arms = {}
    for i, g in enumerate(gate_blocks):
        if 'malformed' in g:
            ok_gate = False
            continue
        arms[g['block']] = g['arm']
        if (g['block'] != i or (g['arms'], g['period'], g['abba']) != (2, PERIOD, 1)
                or g['arm'] != (0, 1, 1, 0)[i % 4] or g['frame'] != START + PERIOD * i
                or g['text'] != want_text[g['arm']]):
            ok_gate = False
    integrity['GATEARM'] = ok_gate
    out['gate_blocks'] = len(gate_blocks)

    whole = list(rows.values())
    integrity['NO_FLOOR'] = all(sum(r[k] for r in whole) == 0 for k in FLOOR_KEYS)
    integrity['MARKERS_OFF'] = sum(r['gm_ops'] for r in whole) == 0
    integrity['NO_RECORDING'] = counts['recording'] == 0

    sel = select(rows, arms)
    out['selection'] = {'pairs': len(sel['pairs']), 'blocks': len(sel['blocks']),
                        'rejected': {str(k): v for k, v in sel['rejected'].items()},
                        'excluded_edge_blocks': sel['excluded_edge_blocks']}
    seen = run['seen']
    last_main = max(seen['main']) if seen['main'] else 0
    missing = sorted(n for n in seen['main'] if START < n < last_main
                     and (n not in seen['draw'] or n not in seen['x']))
    integrity['STREAMS_COMPLETE'] = not missing
    out['streams_missing'] = missing[:20]
    integrity['ROW_ARMS'] = all(rows[n]['arm'] == arms[b] and rows[n]['blk'] == b
                                for b, ns in sel['blocks'].items() for n in ns)
    orient = [sum(arms[p[0]] == a for p in sel['pairs']) for a in (0, 1)]
    integrity['AB_BA_BALANCED'] = orient[0] == orient[1] and orient[0] > 0
    out['orientations'] = orient

    # ---------------------------------------------------------------- sealed controls, markers
    pins = counts['pin']
    controls['PIN_ONCE'] = pins.get('1', 0) == 1 and sum(pins.values()) == 1
    controls['RECORD_THREAD_TWO'] = counts['rec_started'] == 2
    controls['NO_CHECKPOINT_LINE'] = counts['ckpt_lines'] == 0 and counts['ckpt_diag'] == 0
    controls['NO_GPUHANGABORT'] = counts['hang'] == 0
    controls['NO_FATAL_MARKER'] = not counts['fatal']
    controls['ENV_NO_CHECKPOINTS'] = 'KYTY_GPU_CHECKPOINTS' not in env
    controls['PAIRS'] = len(sel['pairs']) >= cfg['min_pairs']

    if not sel['pairs']:
        for k in ('BAND_dt_us', 'BAND_rec_n', 'BAND_gpu_busy_us', 'WORK_SPLIT', 'AREA_VERDICT',
                  'AREA_SELECTED', 'ARMING'):
            controls[k] = False
        return finish(out, integrity, controls, None, mechanics)

    means = {b: block_means(rows, ns) for b, ns in sel['blocks'].items()}
    by_arm = {a: [means[b] for b in means if arms[b] == a] for a in (0, 1)}
    arm_med = {a: {k: median_or_none(m[k] for m in by_arm[a]) for k in ARM_KEYS} for a in (0, 1)}
    rows_arm = {a: [derived(rows[n]) for b, ns in sel['blocks'].items() if arms[b] == a
                    for n in ns] for a in (0, 1)}
    arm_row_med = {a: {k: median_or_none(r[k] for r in rows_arm[a]) for k in ARM_KEYS}
                   for a in (0, 1)}
    out['arm_medians'] = {'arm0_dabatch64': arm_med[0], 'arm1_dabatch%d' % cfg['B']: arm_med[1]}
    out['arm_row_medians_reported'] = {'arm0_dabatch64': arm_row_med[0],
                                       'arm1_dabatch%d' % cfg['B']: arm_row_med[1]}

    for key, (lo, hi) in BANDS.items():
        controls['BAND_%s' % key] = all(arm_med[a][key] is not None and lo <= arm_med[a][key] <= hi
                                        for a in (0, 1))
        row_ok = all(arm_row_med[a][key] is not None and lo <= arm_row_med[a][key] <= hi
                     for a in (0, 1))
        if row_ok != controls['BAND_%s' % key]:
            out['notes'].append('BAND_%s: block-median and row-median readings DISAGREE '
                                '(block decides)' % key)
    ws = work_split(rows, sel, arms)                          # pred/05 1
    controls['WORK_SPLIT'] = ws['passed']
    out['work_split'] = ws

    av = area_verdict_mirror(run['all_rows'])
    out['area_verdict_mirror'] = av
    controls['AREA_VERDICT'] = bool(av.get('valid'))
    sa = selected_area(rows, sel, arms)
    out['area_selected'] = sa
    controls['AREA_SELECTED'] = bool(sa.get('valid_data') and abs(sa['split_pct']) < AREA_SPLIT_PCT
                                     and sa['match_pct'] >= AREA_MATCH_PCT)

    q64, w, r = arm_med[0]['da_qcall'], arm_med[0]['da_walks'], arm_med[0]['R']
    arming = arming_check(arm_med, cfg['B'])                  # pred/05 2
    controls['ARMING'] = arming['passed']
    out['arming'] = arming
    old = arming['old_rule_note']
    if old['old_rule_would_pass'] != arming['passed']:
        out['notes'].append('ARMING: the replaced pred/03 +-25 %% ratio rule would say %s '
                            '(deviation %s); pred/05 2 decides'
                            % ('PASS' if old['old_rule_would_pass'] else 'FAIL',
                               fmt(old['relative_deviation'], 4)))

    # ---------------------------------------------------------------- per-pair differences
    pairs = []
    for left, right in sel['pairs']:
        a0 = left if arms[left] == 0 else right
        a1 = right if a0 == left else left
        pairs.append({'blocks': [left, right], 'arm0_block': a0, 'arm1_block': a1,
                      'd': {k: means[a1][k] - means[a0][k] for k in PAIR_KEYS}})
    out['pairs'] = pairs
    delta = {k: [p['d'][k] for p in pairs] for k in PAIR_KEYS}
    stats = {k: mean_t(delta[k]) for k in PAIR_KEYS}
    out['pair_stats'] = stats

    dq_mean, dqc_mean = stats['da_queue_us']['mean'], stats['da_qcall']['mean']
    b_hat = dq_mean / dqc_mean if dqc_mean else None
    boot = ratio_bootstrap(delta['da_queue_us'], delta['da_qcall'])
    tail = (1.0 - CI_LEVEL) / 2.0
    b_ci = [quantile(boot, tail), quantile(boot, 1.0 - tail)] if boot else None
    q1024 = w + r / 1024.0
    factor = q64 - q1024
    s_hat = b_hat * factor if b_hat is not None else None
    s_ci = None
    if boot:
        s_boot = sorted(x * factor for x in boot)
        s_ci = [quantile(s_boot, tail), quantile(s_boot, 1.0 - tail)]
    out['estimates'] = {'b_hat_us_per_call': b_hat, 'b_ci_us': b_ci,
                        'mean_d_da_queue_us': dq_mean, 'mean_d_da_qcall': dqc_mean,
                        'Q64': q64, 'W': w, 'R': r, 'Q1024': q1024, 'Q64_minus_Q1024': factor,
                        'S_hat_us': s_hat, 'S_hat_ci_us': s_ci, 'bootstrap': {
                            'n': BOOT_N, 'seed': BOOT_SEED, 'level': CI_LEVEL,
                            'method': 'pairs resampled with random.Random(102).randrange; '
                                      'ratio of sums; linear percentiles'}}
    dw = stats['da_walk_us']['mean']
    # pred/03 2 states it for the pilot, where both differences are positive; the ratio form
    # reads the same on the decision run, where both are negative (fewer calls).
    ratio_wq = (dw / dq_mean) if (dw is not None and dq_mean) else None
    lower = ratio_wq is not None and ratio_wq > MECH_FACTOR
    if ratio_wq is None:
        statement = 'not computable (d da_queue_us is 0 or missing)'
    elif ratio_wq < 0:
        statement = 'd da_walk_us and d da_queue_us have OPPOSITE signs: mechanism not as read'
    elif lower:
        statement = ('d da_walk_us > 2 x d da_queue_us: part of the call cost is outside the '
                     'timed region, b_hat is a LOWER bound (stated, not repaired)')
    else:
        statement = 'd da_walk_us <= 2 x d da_queue_us'
    out['mechanism'] = {'mean_d_da_walk_us': dw, 'mean_d_da_queue_us': dq_mean,
                        'walk_over_queue': ratio_wq, 'b_hat_is_lower_bound': lower,
                        'statement': statement}

    decision = {}
    if phase == 'pilot':
        closed = s_ci is not None and s_ci[1] < USEFUL_US
        decision['pilot_decision_if_admitted'] = 'CLOSED' if closed else 'RUN_2'
        decision['rule'] = ('upper 90 %% bound of S_hat (%s us) < %.0f us => CLOSED, no second run; '
                            'else RUN_2' % (None if s_ci is None else round(s_ci[1], 3), USEFUL_US))
    else:
        cpu, walk = stats['cpu_net_us'], stats['da_walk_us']
        hit64 = arm_med[0]['da_hit']
        rules = {
            'R1_cpu_net': cpu['mean'] is not None and cpu['t'] is not None
                          and cpu['mean'] < 0 and cpu['t'] <= SHIP_T,
            'R2_da_walk': walk['mean'] is not None and walk['t'] is not None
                          and walk['mean'] < 0 and walk['t'] <= SHIP_T,
            'R3_late': stats['da_late']['mean'] is not None
                       and abs(stats['da_late']['mean']) <= LATE_BAND,
            'R3_hit': hit64 is not None and stats['da_hit']['mean'] >= -HIT_FRAC * hit64,
            'R3_miss': hit64 is not None and stats['da_miss']['mean'] <= MISS_FRAC * hit64,
            'R3_busy': stats['da_busy']['mean'] <= BUSY_MAX,
        }
        decision['ship_rules'] = rules
        decision['da_hit_64'] = hit64
        decision['ship_if_admitted'] = all(rules.values())
    out['decision'] = decision

    # ---------------------------------------------------------------- predictions (no weight)
    preds = {}
    if phase == 'pilot':
        preds['Q1_b_hat_in_0.05_1.5_us'] = {'value': b_hat, 'band': list(Q1_BAND),
                                            'hit': b_hat is not None
                                                   and Q1_BAND[0] <= b_hat <= Q1_BAND[1]}
        preds['Q2_closes_after_pilot'] = {'value': None if s_ci is None else s_ci[1],
                                          'band': [None, USEFUL_US],
                                          'hit': s_ci is not None and s_ci[1] < USEFUL_US}
        late = stats['da_late']['mean']
        preds['Q3_d_da_late_within_0.05'] = {'value': late, 'band': [-Q3_BAND, Q3_BAND],
                                             'hit': late is not None and abs(late) <= Q3_BAND}
    else:
        preds['note'] = 'Q1-Q3 are registered on the pilot (8 - 64); not scored on the decision run'
    out['predictions'] = preds
    return finish(out, integrity, controls, decision, mechanics)


def finish(out, integrity, controls, decision, mechanics):
    out['integrity'] = integrity
    out['controls'] = controls
    failed = sorted(['integrity:' + k for k, v in integrity.items() if not v]
                    + ['control:' + k for k, v in controls.items() if not v])
    if out['errors']:
        failed.append('protocol')
    out['failed_controls'] = failed
    phase = out['phase']
    if failed:
        out['status'] = 'INVALID'
    elif mechanics:
        out['status'] = 'MECHANICS_ONLY'
    else:
        out['status'] = 'ADMITTED_PILOT' if phase == 'pilot' else 'ADMITTED_DECISION'
    admitted = out['status'].startswith('ADMITTED')
    decision = decision or {}
    if phase == 'pilot':
        out['pilot_decision'] = decision.get('pilot_decision_if_admitted') if admitted else None
    else:
        ship = bool(admitted and decision.get('ship_if_admitted'))
        out['ship_dabatch_1024'] = ship
        out['verdict'] = ('SHIP dabatch=1024 as the new default (a new build: the video pass of '
                          'the shipped build is owed, ROADMAP 6)' if ship else
                          'KEEP 64 (default unchanged; the knob stays a measurement knob)')
    out['must_not_be_claimed'] = ('a speedup from the pilot; that m_mutex contention was measured; '
                                  'a frame-rate gain; 60 FPS (pred/03 6)')
    return out


# ------------------------------------------------------------------------------------ report
def fmt(x, digits=3):
    if x is None:
        return 'None'
    if isinstance(x, float):
        return ('%.' + str(digits) + 'f') % x
    return str(x)


def summary(out):
    lines = ['dab102.py %s phase=%s B=%s status=%s' % (out['tag'], out['phase'], out.get('B'),
                                                       out['status']),
             '  seals: pred/03 %s  pred/05 %s' % (out.get('pred_sha256'),
                                                  out.get('addendum_sha256'))]
    for e in out['errors']:
        lines.append('  PROTOCOL ERROR: %s' % e)
    if 'selection' in out:
        lines.append('  pairs %d (orientations %s), blocks %d, excluded edge blocks %s'
                     % (out['selection']['pairs'], out.get('orientations'),
                        out['selection']['blocks'], out['selection']['excluded_edge_blocks']))
    for group in ('integrity', 'controls'):
        for k, v in sorted((out.get(group) or {}).items()):
            lines.append('  [%s] %-9s %s' % ('PASS' if v else 'FAIL', group[:9], k))
    am = out.get('arm_medians')
    if am:
        for name, med in am.items():
            lines.append('  %-16s dt %s rec_n %s gpu_busy %s draws %s qcall %s walks %s R %s'
                         % (name, fmt(med['dt_us'], 1), fmt(med['rec_n'], 1),
                            fmt(med['gpu_busy_us'], 1), fmt(med['draws'], 1),
                            fmt(med['da_qcall'], 2), fmt(med['da_walks'], 2), fmt(med['R'], 1)))
    if isinstance(out.get('work_split'), dict):
        ws = out['work_split']
        lines.append('  work split (pred/05 1, mean of rows %d/%d): %s %%  (strict < %.2f %%) -> %s'
                     % (ws['rows_arm1'], ws['rows_arm0'],
                        fmt(None if ws['work'] is None else 100 * ws['work'], 4),
                        100 * ws['tolerance'], 'PASS' if ws['passed'] else 'FAIL'))
        lines.append('    REPORTED, never deciding: block-median %s %%, row-median %s %%'
                     % (fmt(None if ws['reported_block_median'] is None
                            else 100 * ws['reported_block_median'], 4),
                        fmt(None if ws['reported_row_median'] is None
                            else 100 * ws['reported_row_median'], 4)))
    if 'arming' in out:
        a = out['arming']
        lines.append('  arming (pred/05 2): W %s  R %s -> %s'
                     % (fmt(a['W'], 3), fmt(a['R'], 2), 'PASS' if a['passed'] else 'FAIL'))
        for name, v in a['arms'].items():
            lines.append('    %-16s median da_qcall %s in [%s, %s]: %s'
                         % (name, fmt(v['observed_median_da_qcall'], 3),
                            fmt(v['interval'][0] if v['interval'] else None, 3),
                            fmt(v['interval'][1] if v['interval'] else None, 3),
                            'inside' if v['inside'] else 'OUTSIDE'))
        o = a['old_rule_note']
        lines.append('    note (pred/03 ratio rule, replaced): Q_B obs %s pred %s  dev %s'
                     % (fmt(o['Q_B_observed'], 2), fmt(o['Q_B_predicted'], 2),
                        fmt(o['relative_deviation'], 4)))
    if 'area_verdict_mirror' in out:
        av = out['area_verdict_mirror']
        lines.append('  area_verdict mirror: split %s %%  match %s %% (%s/%s)  work %s %%  valid %s'
                     % (fmt(av.get('split_pct')), fmt(av.get('match_pct'), 1), av.get('matched'),
                        av.get('pairs'), fmt(av.get('work_pct')), av.get('valid')))
    if 'estimates' in out:
        e = out['estimates']
        lines.append('  b_hat %s us/call  90%% CI %s' % (fmt(e['b_hat_us_per_call'], 4),
                                                        [fmt(x, 4) for x in e['b_ci_us'] or []]))
        lines.append('  Q64 %s  W %s  R %s  Q1024 %s  S_hat %s us  90%% CI %s'
                     % (fmt(e['Q64'], 2), fmt(e['W'], 2), fmt(e['R'], 1), fmt(e['Q1024'], 3),
                        fmt(e['S_hat_us'], 2), [fmt(x, 2) for x in e['S_hat_ci_us'] or []]))
        m = out['mechanism']
        lines.append('  mechanism: d walk %s us, d queue %s us, ratio %s -> %s'
                     % (fmt(m['mean_d_da_walk_us'], 2), fmt(m['mean_d_da_queue_us'], 2),
                        fmt(m['walk_over_queue'], 3), m['statement']))
        for k in ('cpu_net_us', 'da_walk_us', 'da_late', 'da_hit', 'da_miss', 'da_busy'):
            s = out['pair_stats'][k]
            lines.append('  d %-12s mean %s  t %s  n %d' % (k, fmt(s['mean'], 4), fmt(s['t'], 2),
                                                           s['n']))
    d = out.get('decision') or {}
    if out['phase'] == 'pilot':
        lines.append('  pilot decision if admitted: %s   pilot decision: %s'
                     % (d.get('pilot_decision_if_admitted'), out.get('pilot_decision')))
    else:
        for k, v in sorted((d.get('ship_rules') or {}).items()):
            lines.append('  [%s] ship %s' % ('PASS' if v else 'FAIL', k))
        lines.append('  ship if admitted: %s' % d.get('ship_if_admitted'))
        lines.append('  VERDICT: %s' % out.get('verdict'))
    for k, v in sorted((out.get('predictions') or {}).items()):
        if isinstance(v, dict):
            lines.append('  prediction %-28s %s value %s band %s'
                         % (k, 'HIT ' if v['hit'] else 'MISS', fmt(v['value'], 4), v['band']))
    for n in out.get('notes', []):
        lines.append('  note: %s' % n)
    lines.append('  failed: %s' % (out.get('failed_controls') or 'none'))
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('tag')
    ap.add_argument('--phase', choices=('pilot', 'decision'), required=True)
    ap.add_argument('--root', default=PRODUCTION_ROOT)
    ap.add_argument('--out')
    ap.add_argument('--pilot-score', default=None)
    ap.add_argument('--mechanics-only', action='store_true')
    ap.add_argument('--json', action='store_true', help='also print the whole JSON')
    options = ap.parse_args(argv)
    mechanics = options.mechanics_only
    try:
        check_seals()
    except SealError as exc:
        print(str(exc) + ': refusing to score')
        return 2
    if Path(options.root).as_posix().rstrip('/') != PRODUCTION_ROOT and not mechanics:
        print('production root must be %s (use --mechanics-only elsewhere)' % PRODUCTION_ROOT)
        return 2
    named = re.fullmatch(r'dab102([ab])(?:_entry1)?', options.tag)
    if not mechanics:
        if named is None:
            print('tag %r is not a pred/03 tag (dab102a, dab102b, optional _entry1)' % options.tag)
            return 2
        if PHASES[options.phase]['tag'] != 'dab102' + named.group(1):
            print('tag %r does not belong to phase %s' % (options.tag, options.phase))
            return 2
    if options.out:
        path = Path(options.out)
        if path.exists():
            print('output %s exists: never overwritten' % path)
            return 2
        if not mechanics and not path.as_posix().startswith(PRODUCTION_ROOT + '/'):
            print('output must live under %s' % PRODUCTION_ROOT)
            return 2
    try:
        result = evaluate(options.root, options.tag, options.phase, mechanics,
                          options.pilot_score)
    except SealError as exc:
        print(str(exc) + ': refusing to score')
        return 2
    if not mechanics:
        exe_sha = sha256_file(EXE) if Path(EXE).is_file() else None
        result['integrity']['IDENTITY'] = (exe_sha == result.get('binary_sha256') == BINARY_SHA)
        result['installed_exe_sha256'] = exe_sha
        if not result['integrity']['IDENTITY']:
            finish(result, result['integrity'], result['controls'], result.get('decision'),
                   mechanics)
    else:
        result['notes'].append('MECHANICS ONLY: not a scoring; IDENTITY of the installed exe '
                               'not checked')
    print(summary(result))
    text = json.dumps(result, indent=2, sort_keys=True, default=str)
    if options.json:
        print(text)
    if options.out:
        with open(options.out, 'x', encoding='utf-8') as handle:
            handle.write(text + '\n')
        print('wrote %s' % options.out)
    return 0 if result['status'] in ('ADMITTED_PILOT', 'ADMITTED_DECISION', 'MECHANICS_ONLY') else 1


if __name__ == '__main__':
    raise SystemExit(main())
