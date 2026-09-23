"""Session 104, route A Stage 1 ("kill or go") scorer: runs mut104 (mutwide=0|15) and sh104
(shadowresolve=0|4), sealed to pred/02_a_stage1.md (draft: pred_drafts/02_a_stage1.draft.md).

    python C:/kyty/s104/a104.py --mut mut104 --sh sh104 --out C:/kyty/s104/runs104/a104_score.json
    python C:/kyty/s104/a104.py --mut <tag> --sh <tag> --root <dir> --draft [--period 30 --keep 20:29]

Offline only: never launches the game, never rebuilds, never retries, never overwrites an output
(--out is opened with mode 'x' and an existing file is refused before any work).

SEAL.  Production scoring refuses to run (exit 2) unless the sealed text pred/02_a_stage1.md is
byte-for-byte the text whose sha256 and size are the constants PRED_SHA / PRED_BYTES below.  Until
the executor seals the draft and fills them, PRED_SHA is None and only --draft works.  --draft skips
the seal, accepts any root, tag and population geometry, and can never print ADMITTED or a verdict:
its status is DRAFT and its G is labelled "draft arithmetic".

What is decided (pred/02 section numbers):
  s3  population: session 101 pred/01 4 carried by dab102.py - blocks of 90 from frame 1800, kept
      rows idx 60..88 (29) of each block, blocks with a kept frame below 2100 rejected, pairs
      (2k, 2k+1) inside complete ABBA quartets only; per block the arithmetic mean over its kept
      rows; per pair the difference (arm 1) - (arm 0); an arm's level = the median over its
      selected blocks of those block means.
  s4  admission, per run: the integrity controls of dab102.py (schema, field origin, contiguity,
      duration, GateArm texts, row arms, balanced orientations, no floor, markers off, no
      recording, streams complete, identity of the binary) + the controls of pred/03 s4 of
      session 102 (bands, work split per pred/05 1, area split and match, pin once, two record
      threads, no checkpoint line, no GpuHangAbort, no fatal marker, KYTY_GPU_CHECKPOINTS absent),
      pairs >= 30, and the arming controls of each run (s4.2 / s4.3).
  s5  the readouts and G:
        cpu_net   = sh104 arm-0 level of cpu_net_us = cpu_gpu_us - spin_gpu_us (uninstrumented)
        S_raw     = mut104 arm-1 level of a_mut_us (six amut sites + four mutwide surfaces)
        P_mw      = mean paired d cpu_net_us of mut104 (arm1 - arm0), its 2*SE
        T_in      = 5*pl_em_n + 3*(pl_prog_n + pl_pipe_n + pl_cs_n) + a_mut_n   (mut104 arm 1)
        dI        = C_TS_NS * T_in / 1000  (instrument timestamps inside a_mut_us)
        S_now     = S_raw - max(P_mw, 0) - dI                                   [central]
        S_now^    = S_raw - max(P_mw + 2SE, 0) - 2 dI                           [ceiling]
        E_move    = pl_em_rec_ns/1000 + W_E (session 101 cm101d write 675.455 + emit 440.120)
        E_move^   = (pl_em_rec_ns + pl_em_com_ns)/1000     (whole CommitBindings, this run)
        S_ctx     = S_now - E_move ;  S_ctx^ = S_now^ - E_move^
        spine     = sh104 arm-0 level of da_walk_us - da_queue_us (the GuestGpu walk, dawalk=0)
        T4        = mean paired d cpu_net_us of sh104 (arm 4 - arm 0)
        T4^       = max(0, T4 - 2SE - sh_push_us(arm 1 level))
        G         = cpu_net - [S_ctx + F*(cpu_net - S_ctx)] - spine - T4,  F = 0.30
        G^        = the same with S_ctx^ and T4^  (the CEILING, every uncertain term at its
                    A-favourable end)
  s6  THE RULE, applied to G (central), as ROADMAP s0.1 item 6 records it: G < 3000 us => route A
      CLOSED for max FPS; G >= 3000 us => route A proceeds by stages.  G^ (the ceiling) is printed
      beside it and decides nothing.  Not evaluable if either run is not ADMITTED or the two runs' arm-0
      render areas differ by more than 3 % (the levels would come from different DRS rungs).
  s7  predictions, scored with no decision weight.

Conventions fixed here (each stated so an audit can attack it):
  * every microsecond counter is read as printed (micros=true rows are already us), every *_ns
    counter is divided by 1000 here, never on the line;
  * "d X" = mean over pairs of the per-pair difference; t = mean / (sd/sqrt(n)), sample sd;
  * an arm-0 "dark" test is on the kept rows only (idx 60..88, far from the block edges where a
    straddling span or a flip-queue lag can book a count under the neighbouring arm);
  * the area cross-check between the two runs uses sum(rt_kpx)/sum(rt_att) over the kept rows of
    arm 0 of each run.
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
PRED = 'C:/kyty/s104/pred/02_a_stage1.md'
PRED_SHA = '29324c0c29603250255b5879d48ae2e9d8574672ef7291ceb27ebc44de2fbb8a'          # filled by the executor when pred/02 is sealed
PRED_BYTES = 16476        # filled by the executor when pred/02 is sealed
BINARY_SHA = '16ef56b69c4a99fa6ad613d0dbf57d7f59e0d5443bd6509c55442d83c4780352'
EXE = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
GATES_FILE = 'C:/kyty/s104/gates_base.txt'
GATES_SHA = '00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8'

PERIOD, START, FIRST_FRAME = 90, 1800, 2100
KEEP_LO, KEEP_HI = 60, 89                  # scheduled[60:89] -> 29 rows, idx 60..88
MIN_PAIRS = 30
HOLD_S = 300

MUT_ARMS = ('mutwide=0 mutsite=1 amut=1 plkstat=1 pathlap=1',
            'mutwide=15 mutsite=1 amut=1 plkstat=1 pathlap=1')
SH_ARMS = ('shadowresolve=0 shadowmask=3', 'shadowresolve=4 shadowmask=3')
RUNS = {
    'mut': dict(arms=MUT_ARMS, schedule='90+1800:%s|%s' % MUT_ARMS,
                tag_re=r'mut104b?(?:_entry1)?'),
    'sh': dict(arms=SH_ARMS, schedule='90+1800:%s|%s' % SH_ARMS,
               tag_re=r'sh104b?(?:_entry1)?'),
}

# pred/02 s5 constants
F_SERIAL = 0.30          # the ROADMAP rule's f at DCB granularity
F_SENS = 0.39            # the upper end of f_max (DESIGN_82 s1), sensitivity only
BAR_US = 3000.0          # the rule's bar
C_TS_NS = 3.96           # pl96a: 362.9 us / 91 663 GuestGpu timestamps a flip (pred/02 s5.2)
W_E_S101_US = 675.455 + 440.120   # cm101d write-list + emit per flip, session 101 (cross-run)
AREA_XRUN_PCT = 3.0

BANDS = {'dt_us': (28000.0, 40000.0), 'rec_n': (9000.0, 13000.0),
         'gpu_busy_us': (10000.0, 16000.0)}
WORK_TOL = 0.005
AREA_SPLIT_PCT, AREA_MATCH_PCT, AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 8
ID_TOL = 0.02            # the s83 identities, +-2 %
DARK_FRAC = 0.001        # arm-0 total of an arming counter <= 0.1 % of arm 1's
SH_JOB_BAND = (0.90, 1.02)
SH_DROP_MAX = 0.01
CHAIN_BAND = (0.95, 1.01)

# Where the build prints each field (verified on log_reg104.txt, binary 16ef56b6...).
EXPECTED_LINE = {
    'dt_us': 'main', 'draws': 'main', 'dispatches': 'main', 'cpu_gpu_us': 'main',
    'gpu_busy_us': 'main', 'arm': 'main', 'blk': 'main',
    'spin_gpu_us': 'draw', 'rec_n': 'draw', 'bda_n': 'draw', 'da_walks': 'draw',
    'da_walk_us': 'draw', 'da_queue_us': 'draw', 'da_take_us': 'draw', 'da_hit': 'draw',
    'da_miss': 'draw', 'da_late': 'draw',
    'rt_att': 'x', 'rt_kpx': 'x', 'bf_n': 'x', 'bf_disp': 'x', 'bf_skip': 'x',
    'bf_clr_skip': 'x', 'bf_skip_drop': 'x', 'gm_ops': 'x',
    'mw_n': 'x', 'a_mut_us': 'x', 'a_mut_n': 'x', 'a_hold_us': 'x', 'a_hold_n': 'x',
    'a_wait_us': 'x',
    'mh_n': 'x', 'mh_draws': 'x', 'mh_disp_n': 'x', 'mh_pro_us': 'x', 'mh_rt_us': 'x',
    'mh_prog_us': 'x', 'mh_bind_us': 'x', 'mh_emit_us': 'x', 'mh_tail_us': 'x',
    'mh_disp_us': 'x',
    'pl_prog_wait_us': 'x', 'pl_prog_hold_us': 'x', 'pl_prog_n': 'x',
    'pl_pipe_wait_us': 'x', 'pl_pipe_hold_us': 'x', 'pl_pipe_n': 'x',
    'pl_cs_wait_us': 'x', 'pl_cs_hold_us': 'x', 'pl_cs_n': 'x',
    'pl_em_vtx_ns': 'x', 'pl_em_rt_ns': 'x', 'pl_em_pipe_ns': 'x', 'pl_em_com_ns': 'x',
    'pl_em_rec_ns': 'x', 'pl_em_rest_ns': 'x', 'pl_em_n': 'x',
    'pl_proc_ns': 'x', 'pl_proc_n': 'x', 'pl_pref_ns': 'x', 'pl_pref_n': 'x',
    'sh_jobs': 'x', 'sh_drop': 'x', 'sh_over': 'x', 'sh_us': 'x', 'sh_push_us': 'x',
    'sh_lock_us': 'x', 'sh_trk_us': 'x', 'sh_wake': 'x', 'sh_img': 'x', 'sh_buf': 'x',
    'da_wjobs': 'x', 'da_wskip': 'x', 'da_wdrop': 'x',
}
FIELDS = tuple(EXPECTED_LINE)
CORE = ('arm', 'blk', 'dt_us', 'draws', 'cpu_gpu_us', 'spin_gpu_us', 'gpu_busy_us',
        'rt_att', 'rt_kpx')
FLOOR_KEYS = ('bf_n', 'bf_disp', 'bf_skip', 'bf_clr_skip', 'bf_skip_drop')
PL_EM = ('pl_em_vtx_ns', 'pl_em_rt_ns', 'pl_em_pipe_ns', 'pl_em_com_ns', 'pl_em_rec_ns',
         'pl_em_rest_ns')
LINE_KIND = ((b'FrameTrace: ', 'main'), (b'FrameTrace-draw: ', 'draw'), (b'FrameTrace-x: ', 'x'))
RE_TOKEN = re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')

FATAL = (b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---',
         b'ErrorDeviceLost', b'Unhandled exception:', b'GpuWaitSlow:',
         b'AsyncPipelines: skipped draw')
HANG = b'GpuHangAbort'
RE_PIN = re.compile(rb'GpuClockPin: mode (\d+)')
RE_SHW = re.compile(rb'ShadowResolve: worker (\d+) started')
ENV_EXPECTED = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_QUEUE_TRACE': '1',
                'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden',
                'KYTY_GATE_SCHEDULE_ABBA': '1', 'KYTY_GPU_CLOCK_PIN': '1',
                'KYTY_GPU_MARKERS': '0'}
ENV_PRESENT = ('KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE', 'KYTY_GATE_SCHEDULE')

PAIR_KEYS = ('cpu_net_us', 'dt_us', 'draws', 'gpu_busy_us', 'rec_n', 'spin_gpu_us',
             'da_take_us', 'da_hit', 'da_miss', 'da_late', 'spine_us', 'a_mut_us', 'a_hold_us',
             'sh_push_us', 'sh_us', 'mh_prog_us', 'mh_emit_us')


class SealError(RuntimeError):
    pass


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_seal(path=None, want_sha=None, want_bytes=None):
    """pred/02 by default, resolved at call time.  sha256 AND size.  An unfilled constant is a
    refusal, never a pass."""
    path = PRED if path is None else path
    want_sha = PRED_SHA if want_sha is None else want_sha
    want_bytes = PRED_BYTES if want_bytes is None else want_bytes
    if want_sha is None or want_bytes is None:
        raise SealError('PRED_SHA / PRED_BYTES are not filled: seal %s and put its sha256 and '
                        'size into a104.py (only --draft runs without a seal)' % path)
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise SealError('sealed pre-registration unreadable: %s (%s)' % (path, exc))
    got = hashlib.sha256(data).hexdigest()
    if got != want_sha or len(data) != want_bytes:
        raise SealError('SEALED PRE-REGISTRATION CHANGED: %s sha256 %s (%d B), sealed %s (%s B)'
                        % (path, got, len(data), want_sha, want_bytes))
    return got


# ------------------------------------------------------------------------------------ statistics
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
    """a / b - 1, None when either is missing or b is 0."""
    if a is None or b is None or b == 0:
        return None
    return a / b - 1.0


# ------------------------------------------------------------------------------------ reading
def new_counts():
    return {'hang': 0, 'fatal': {}, 'pin': {}, 'rec_started': 0, 'ckpt_lines': 0,
            'ckpt_off_lines': 0, 'ckpt_diag': 0, 'recording': 0, 'shadow_workers': []}


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
    if b'ShadowResolve: worker' in line:
        m = RE_SHW.search(line)
        if m:
            counts['shadow_workers'].append(int(m.group(1)))


def read_run(log_path, stdout_path):
    """One streaming pass.  Rows {n: {field: int}} built ONLY from each field's expected line;
    rows lacking a CORE field are dropped from the population (SCHEMA reports every missing
    field of every line)."""
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


# ------------------------------------------------------------------------------------ population
def select(rows, arms, period=PERIOD, start=START, first=FIRST_FRAME, keep=(KEEP_LO, KEEP_HI)):
    """session 101 pred/01 4 (cen100.select, as carried by dab102.py), geometry parameterised
    for --draft only."""
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
    """Per-row derived quantities; each only when its inputs are present."""
    out = dict(row)

    def have(*keys):
        return all(k in row for k in keys)

    if have('cpu_gpu_us', 'spin_gpu_us'):
        out['cpu_net_us'] = row['cpu_gpu_us'] - row['spin_gpu_us']
    if have('da_walk_us', 'da_queue_us'):
        out['spine_us'] = row['da_walk_us'] - row['da_queue_us']
    if have('pl_pref_ns', 'da_queue_us'):
        out['spine_pref_us'] = row['pl_pref_ns'] / 1000.0 - row['da_queue_us']
    if have('mh_n', 'mh_disp_n', 'bda_n'):
        out['mw_expect'] = 2 * row['mh_n'] + row['mh_disp_n'] + row['bda_n']
    if have('mh_n', 'mh_disp_n'):
        out['hold_expect'] = row['mh_n'] + row['mh_disp_n']
    if have(*PL_EM):
        out['em_sum_us'] = sum(row[k] for k in PL_EM) / 1000.0
    for k in PL_EM + ('pl_proc_ns', 'pl_pref_ns'):
        if k in row:
            out[k[:-3] + '_us'] = row[k] / 1000.0
    if have('pl_em_n', 'pl_prog_n', 'pl_pipe_n', 'pl_cs_n', 'a_mut_n'):
        out['t_in'] = (5 * row['pl_em_n'] + 3 * (row['pl_prog_n'] + row['pl_pipe_n']
                                                  + row['pl_cs_n']) + row['a_mut_n'])
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
    """Per arm: median over its selected blocks of the per-block means."""
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
    """pred/05 1 of session 102 = session 101's cen100 definition."""
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
    """area_verdict.py judge(), over every flip n >= first_frame that carries the fields
    (copied from dab102.py)."""
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
            'matched': matched, 'match_pct': 100.0 * matched / len(deltas) if deltas else 0.0,
            'area_arm0': a0, 'area_arm1': a1}


# ------------------------------------------------------------------------------------ one run
def protocol_errors(meta, kind, gates_file):
    errors = []
    err = errors.append
    env = meta.get('env') or {}
    kyty = {k: v for k, v in env.items() if k.startswith('KYTY_')}
    for key, value in ENV_EXPECTED.items():
        if kyty.get(key) != value:
            err('env %s=%r, expected %r' % (key, kyty.get(key), value))
    schedule = RUNS[kind]['schedule']
    if kyty.get('KYTY_GATE_SCHEDULE') != schedule:
        err('env KYTY_GATE_SCHEDULE=%r, expected %r' % (kyty.get('KYTY_GATE_SCHEDULE'), schedule))
    if (meta.get('schedule') or '') != schedule:
        err('meta schedule %r, expected %r' % (meta.get('schedule'), schedule))
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


def evaluate_run(root, tag, kind, draft=False, geometry=None, gates_file=GATES_FILE):
    """Scores one Stage-1 run.  kind = 'mut' or 'sh'.  geometry (draft only) overrides
    period/start/first/keep."""
    geo = dict(period=PERIOD, start=START, first=FIRST_FRAME, keep=(KEEP_LO, KEEP_HI))
    if geometry:
        if not draft:
            raise ValueError('population geometry can only be changed in --draft')
        geo.update(geometry)
    root = Path(root)
    log = root / ('log_%s.txt' % tag)
    stdout = root / ('stdout_%s.txt' % tag)
    meta_path = root / ('%s.json' % tag)
    out = {'tag': tag, 'kind': kind, 'draft': bool(draft), 'geometry': dict(geo, keep=list(geo['keep'])),
           'errors': [], 'notes': []}
    for p in (log, meta_path):
        if not p.is_file():
            out['errors'].append('missing input: %s' % p)
    if not stdout.is_file():
        out['notes'].append('no stdout file (markers read from the log only)')
    if out['errors']:
        return finish_run(out, {'INPUTS': False}, {})
    out['raw_sha256'] = {'log': sha256_file(log), 'meta': sha256_file(meta_path),
                         'stdout': sha256_file(stdout) if stdout.is_file() else None}
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    out['binary_sha256'] = meta.get('binary_sha256')
    out['errors'].extend(protocol_errors(meta, kind, gates_file))

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
    wrong_origin = {f: v for f, v in run['origin'].items() if v and v != [EXPECTED_LINE[f]]}
    integrity['FIELD_ORIGIN'] = not wrong_origin
    out['field_origin_defects'] = wrong_origin
    order = run['order']
    integrity['RAW_CONTIGUITY'] = (bool(order) and order == sorted(order)
                                   and len(order) == len(set(order))
                                   and order == list(range(min(order), max(order) + 1)))
    integrity['DURATION'] = (sum(r['dt_us'] for r in rows.values()) / 1e6
                             >= (meta.get('hold_s') or 0))

    want_text = RUNS[kind]['arms']
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
                or g['text'] != want_text[g['arm']]):
            ok_gate = False
    integrity['GATEARM'] = ok_gate
    out['gate_blocks'] = len(gate_blocks)
    out['gate_texts_seen'] = sorted({g.get('text', '?') for g in gate_blocks})[:4]

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
    out['streams_missing'] = missing[:20]
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
        return finish_run(out, integrity, controls)

    means = {b: block_means(rows, ns) for b, ns in sel['blocks'].items()}
    lev = arm_levels(means, arms)
    out['levels'] = {'arm0': lev[0], 'arm1': lev[1]}
    out['arm_texts'] = list(want_text)

    band_ok = True
    for key, (lo, hi) in BANDS.items():
        for a in (0, 1):
            v = lev[a].get(key)
            if v is None or not lo <= v <= hi:
                band_ok = False
    controls['BANDS'] = band_ok
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

    pairs = []
    for left, right in sel['pairs']:
        a0 = left if arms[left] == 0 else right
        a1 = right if a0 == left else left
        d = {}
        for k in PAIR_KEYS:
            if means[a0].get(k) is not None and means[a1].get(k) is not None:
                d[k] = means[a1][k] - means[a0][k]
        pairs.append({'blocks': [left, right], 'arm0_block': a0, 'arm1_block': a1, 'd': d})
    out['pairs'] = pairs
    out['pair_stats'] = {k: mean_t([p['d'].get(k) for p in pairs]) for k in PAIR_KEYS}

    arming = arming_mut(rows, sel, arms, lev) if kind == 'mut' else arming_sh(rows, sel, arms, lev,
                                                                              counts)
    out['arming'] = arming
    controls['ARMING'] = arming['passed']
    return finish_run(out, integrity, controls)


def arming_mut(rows, sel, arms, lev):
    """pred/02 s4.2."""
    a0, a1 = lev[0], lev[1]
    checks = {}
    tot0, tot1 = kept_total(rows, sel, arms, 0, 'mw_n'), kept_total(rows, sel, arms, 1, 'mw_n')
    checks['MW_DARK_ARM0'] = bool(a0.get('mw_n') == 0 and tot0 is not None and tot1
                                  and tot0 <= DARK_FRAC * tot1)
    r = rel(a1.get('mw_n'), a1.get('mw_expect'))
    checks['MW_IDENTITY_ARM1'] = r is not None and abs(r) <= ID_TOL
    checks['AMUT_ARMED'] = all((lev[a].get('a_mut_us') or 0) > 0 and (lev[a].get('a_mut_n') or 0) > 0
                               for a in (0, 1))
    hold_ok = True
    plk_ok = True
    pl_ok = True
    chain = {}
    for a in (0, 1):
        L = lev[a]
        rh = rel(L.get('a_hold_n'), L.get('hold_expect'))
        hold_ok = hold_ok and (L.get('mh_n') or 0) > 0 and rh is not None and abs(rh) <= ID_TOL
        rp = rel(L.get('pl_prog_n'), L.get('mh_n'))
        rc = rel(L.get('pl_cs_n'), L.get('dispatches'))
        plk_ok = plk_ok and rp is not None and abs(rp) <= ID_TOL and rc is not None \
            and abs(rc) <= ID_TOL and (L.get('pl_prog_hold_us') or 0) > 0
        re_ = rel(L.get('pl_em_n'), L.get('mh_draws'))
        c = (L.get('em_sum_us') / L['mh_emit_us']) if (L.get('em_sum_us') is not None
                                                        and L.get('mh_emit_us')) else None
        chain['arm%d' % a] = c
        pl_ok = pl_ok and re_ is not None and abs(re_) <= ID_TOL and (L.get('pl_pref_n') or 0) >= 1 \
            and c is not None and CHAIN_BAND[0] <= c <= CHAIN_BAND[1]
    checks['MUTSITE_HOLD_IDENTITY'] = hold_ok
    checks['PLKSTAT_IDENTITIES'] = plk_ok
    checks['PATHLAP_ARMED'] = pl_ok
    dark = True
    for a in (0, 1):
        for k in ('sh_jobs', 'da_wjobs'):
            t = kept_total(rows, sel, arms, a, k)
            dark = dark and t == 0
    checks['OTHER_INSTRUMENTS_DARK'] = dark
    return {'checks': checks, 'passed': all(bool(v) for v in checks.values()),
            'mw_n_arm0_kept_total': tot0, 'mw_n_arm1_kept_total': tot1,
            'mw_identity_rel': r, 'emit_chain_closure': chain}


def arming_sh(rows, sel, arms, lev, counts):
    """pred/02 s4.3."""
    a0, a1 = lev[0], lev[1]
    checks = {}
    tot0, tot1 = kept_total(rows, sel, arms, 0, 'sh_jobs'), kept_total(rows, sel, arms, 1, 'sh_jobs')
    checks['SH_DARK_ARM0'] = bool(a0.get('sh_jobs') == 0 and tot0 is not None and tot1
                                  and tot0 <= DARK_FRAC * tot1)
    ratio = (a1['sh_jobs'] / a1['draws']) if (a1.get('sh_jobs') is not None and a1.get('draws')) \
        else None
    checks['SH_JOBS_PER_DRAW'] = ratio is not None and SH_JOB_BAND[0] <= ratio <= SH_JOB_BAND[1]
    drop = (a1['sh_drop'] / a1['sh_jobs']) if (a1.get('sh_drop') is not None and a1.get('sh_jobs')) \
        else None
    checks['SH_NO_DROP'] = drop is not None and drop <= SH_DROP_MAX
    checks['SH_FOUR_WORKERS'] = sorted(counts['shadow_workers']) == [0, 1, 2, 3]
    dark = True
    for a in (0, 1):
        for k in ('a_hold_us', 'a_mut_us', 'mw_n', 'pl_em_n', 'pl_proc_n', 'pl_prog_n', 'da_wjobs'):
            t = kept_total(rows, sel, arms, a, k)
            dark = dark and t == 0
    checks['INSTRUMENTS_DARK'] = dark
    return {'checks': checks, 'passed': all(bool(v) for v in checks.values()),
            'sh_jobs_arm0_kept_total': tot0, 'sh_jobs_arm1_kept_total': tot1,
            'sh_jobs_per_draw': ratio, 'sh_drop_per_job': drop,
            'shadow_workers': counts['shadow_workers']}


def finish_run(out, integrity, controls):
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
    return out


# ------------------------------------------------------------------------------------ G
def lvl(run, arm, key):
    return ((run.get('levels') or {}).get('arm%d' % arm) or {}).get(key)


def pstat(run, key):
    return ((run.get('pair_stats') or {}).get(key)) or {}


def g_of(cpu_net, s_ctx, spine, t4, f=F_SERIAL):
    if None in (cpu_net, s_ctx, spine, t4):
        return None
    return cpu_net - (s_ctx + f * (cpu_net - s_ctx)) - spine - t4


def compute_g(mut, sh):
    """pred/02 s5 and s6.  Every term is printed; nothing is hidden inside G."""
    t = {}
    t['cpu_net'] = lvl(sh, 0, 'cpu_net_us')
    t['S_lo'] = lvl(mut, 0, 'a_mut_us')
    t['S_raw'] = lvl(mut, 1, 'a_mut_us')
    pm = pstat(mut, 'cpu_net_us')
    t['P_mw'], t['P_mw_2se'] = pm.get('mean'), (2 * pm['se'] if pm.get('se') is not None else None)
    t['T_in'] = lvl(mut, 1, 't_in')
    t['dI'] = C_TS_NS * t['T_in'] / 1000.0 if t['T_in'] is not None else None
    t['E_rec'] = lvl(mut, 1, 'pl_em_rec_us')
    t['E_com'] = lvl(mut, 1, 'pl_em_com_us')
    t['W_E_s101'] = W_E_S101_US
    t['spine'] = lvl(sh, 0, 'spine_us')
    t['spine_mut_arm0'] = lvl(mut, 0, 'spine_us')
    t['spine_pref_mut_arm0'] = lvl(mut, 0, 'spine_pref_us')
    ps = pstat(sh, 'cpu_net_us')
    t['T4'], t['T4_2se'] = ps.get('mean'), (2 * ps['se'] if ps.get('se') is not None else None)
    t['sh_push'] = lvl(sh, 1, 'sh_push_us')
    pd = pstat(sh, 'dt_us')
    t['T4_dt'] = pd.get('mean')
    t['T4_dt_2se'] = 2 * pd['se'] if pd.get('se') is not None else None

    def sub(*xs):
        return None if any(x is None for x in xs) else xs[0] - sum(xs[1:])

    c = {}
    if None not in (t['S_raw'], t['P_mw'], t['dI']):
        c['S_now'] = t['S_raw'] - max(t['P_mw'], 0.0) - t['dI']
    c['E_move'] = None if t['E_rec'] is None else t['E_rec'] + W_E_S101_US
    c['S_ctx'] = sub(c.get('S_now'), c['E_move']) if c.get('S_now') is not None else None
    c['T4'] = t['T4']
    c['G'] = g_of(t['cpu_net'], c['S_ctx'], t['spine'], c['T4'])
    c['G_f039'] = g_of(t['cpu_net'], c['S_ctx'], t['spine'], c['T4'], F_SENS)
    wall = (max(0.0, t['T4_dt'] - t['T4']) if None not in (t['T4_dt'], t['T4']) else None)
    c['G_wall'] = None if (c['G'] is None or wall is None) else c['G'] - wall
    c['G_spine_pref'] = g_of(t['cpu_net'], c['S_ctx'], t['spine_pref_mut_arm0'], c['T4'])

    h = {}
    if None not in (t['S_raw'], t['P_mw'], t['P_mw_2se'], t['dI']):
        h['S_now'] = t['S_raw'] - max(t['P_mw'] + t['P_mw_2se'], 0.0) - 2.0 * t['dI']
    h['E_move'] = None if (t['E_rec'] is None or t['E_com'] is None) else t['E_rec'] + t['E_com']
    h['S_ctx'] = sub(h.get('S_now'), h['E_move']) if h.get('S_now') is not None else None
    h['T4'] = (max(0.0, t['T4'] - t['T4_2se'] - t['sh_push'])
               if None not in (t['T4'], t['T4_2se'], t['sh_push']) else None)
    h['G'] = g_of(t['cpu_net'], h['S_ctx'], t['spine'], h['T4'])
    h['G_f039'] = g_of(t['cpu_net'], h['S_ctx'], t['spine'], h['T4'], F_SENS)

    # the T4 at which the ceiling would reach the bar (reported: how far the rule is from firing)
    kill_t4 = None
    if None not in (t['cpu_net'], c['S_ctx'], t['spine']):
        kill_t4 = (1.0 - F_SERIAL) * (t['cpu_net'] - c['S_ctx']) - t['spine'] - BAR_US
    area_mut = (mut.get('area_selected') or {}).get('area_arm0')
    area_sh = (sh.get('area_selected') or {}).get('area_arm0')
    xrun = rel(area_sh, area_mut)
    t['instrument_price_xrun'] = sub(lvl(mut, 0, 'cpu_net_us'), t['cpu_net']) \
        if lvl(mut, 0, 'cpu_net_us') is not None else None
    hm = (lvl(mut, 1, 'pl_prog_hold_us') / lvl(mut, 1, 'mh_prog_us')
          if lvl(mut, 1, 'pl_prog_hold_us') is not None and lvl(mut, 1, 'mh_prog_us') else None)
    return {'terms': t, 'central': c, 'ceiling': h, 'kill_T4_central_us': kill_t4,
            'area_mut_arm0': area_mut, 'area_sh_arm0': area_sh,
            'area_xrun_rel': xrun, 'H_over_M': hm, 'F': F_SERIAL, 'bar_us': BAR_US,
            'C_TS_NS': C_TS_NS}


def verdict(g, mut, sh):
    reasons = []
    if mut.get('status') != 'ADMITTED':
        reasons.append('mut run %s' % mut.get('status'))
    if sh.get('status') != 'ADMITTED':
        reasons.append('sh run %s' % sh.get('status'))
    x = g['area_xrun_rel']
    if x is None or abs(x) * 100.0 > AREA_XRUN_PCT:
        reasons.append('cross-run area %s outside +-%.1f %%'
                       % (None if x is None else round(100 * x, 3), AREA_XRUN_PCT))
    central = g['central']['G']
    if central is None:
        reasons.append('G (central) not computable')
    if_admitted = None
    if central is not None:
        if_admitted = ('A_CLOSED_FOR_MAX_FPS' if central < BAR_US else 'A_PROCEEDS_BY_STAGES')
    return {'verdict_if_admitted': if_admitted,
            'verdict': if_admitted if not reasons else 'NOT_EVALUABLE',
            'not_evaluable_reasons': reasons}


# ------------------------------------------------------------------------------------ predictions
def band_hit(v, lo, hi):
    return v is not None and (lo is None or v >= lo) and (hi is None or v <= hi)


def predictions(mut, sh, g):
    p = {}

    def add(key, text, value, lo, hi):
        p[key] = {'text': text, 'value': value, 'band': [lo, hi], 'hit': band_hit(value, lo, hi)}

    add('A1', 'mw_n arm 0 level exactly 0', lvl(mut, 0, 'mw_n'), 0, 0)
    add('A2', 'mw_n arm 1 / (2 mh_n + mh_disp_n + bda_n) - 1 within +-2 %',
        rel(lvl(mut, 1, 'mw_n'), lvl(mut, 1, 'mw_expect')), -0.02, 0.02)
    add('A3', 'S_lo (arm-0 a_mut_us) in [11 500, 14 500] us', lvl(mut, 0, 'a_mut_us'), 11500, 14500)
    add('A4', 'S_raw (arm-1 a_mut_us) in [18 500, 21 500] us', lvl(mut, 1, 'a_mut_us'), 18500, 21500)
    add('A5', 'P_mw in [0, +400] us', pstat(mut, 'cpu_net_us').get('mean'), 0, 400)
    add('A6', 'H/M = pl_prog_hold_us / mh_prog_us >= 0.60', g['H_over_M'], 0.60, None)
    add('A7a', 'pl_em_rec in [1 000, 1 500] us', lvl(mut, 1, 'pl_em_rec_us'), 1000, 1500)
    add('A7b', 'pl_em_com in [1 800, 2 700] us', lvl(mut, 1, 'pl_em_com_us'), 1800, 2700)
    add('A8', 'spine (sh104 arm 0) in [900, 1 300] us', g['terms']['spine'], 900, 1300)
    add('A9', 'cpu_net (sh104 arm 0) in [29 800, 31 600] us', g['terms']['cpu_net'], 29800, 31600)
    add('A10a', 'T4 in [+700, +2 600] us', g['terms']['T4'], 700, 2600)
    add('A10b', 'sh_push_us (arm 1) in [250, 700] us', g['terms']['sh_push'], 250, 700)
    add('A10c', 'sh_us (arm 1) in [2 500, 6 500] us', lvl(sh, 1, 'sh_us'), 2500, 6500)
    add('A11a', 'G central in [4 000, 8 000] us', g['central']['G'], 4000, 8000)
    add('A11b', 'G central >= 3 000 us (A proceeds) - the discriminating prediction',
        g['central']['G'], BAR_US, None)
    add('A12', 'cross-run instrument price cpu_net(mut arm0) - cpu_net(sh arm0) in [+500, +2 500]',
        g['terms']['instrument_price_xrun'], 500, 2500)
    return p


# ------------------------------------------------------------------------------------ report
def fmt(x, digits=1):
    if x is None:
        return 'None'
    if isinstance(x, float):
        return ('%.' + str(digits) + 'f') % x
    return str(x)


def run_summary(r):
    lines = ['  run %s (%s) status=%s' % (r['tag'], r['kind'], r['status'])]
    for e in r['errors'][:12]:
        lines.append('    PROTOCOL: %s' % e)
    if 'selection' in r:
        lines.append('    pairs %d (orientations %s), blocks %d, excluded %s'
                     % (r['selection']['pairs'], r.get('orientations'), r['selection']['blocks'],
                        r['selection']['excluded_edge_blocks']))
    for group in ('integrity', 'controls'):
        for k, v in sorted((r.get(group) or {}).items()):
            lines.append('    [%s] %-9s %s' % ('PASS' if v else 'FAIL', group[:9], k))
    for k, v in sorted(((r.get('arming') or {}).get('checks') or {}).items()):
        lines.append('    [%s] arming    %s' % ('PASS' if v else 'FAIL', k))
    lev = r.get('levels')
    if lev:
        keys = ('dt_us', 'cpu_net_us', 'draws', 'gpu_busy_us', 'rec_n', 'a_mut_us', 'a_hold_us',
                'mw_n', 'mw_expect', 'mh_prog_us', 'mh_emit_us', 'pl_prog_hold_us',
                'pl_em_rec_us', 'pl_em_com_us', 'spine_us', 'da_take_us', 'sh_jobs', 'sh_us',
                'sh_push_us')
        for k in keys:
            if lev['arm0'].get(k) is not None or lev['arm1'].get(k) is not None:
                lines.append('    %-16s arm0 %10s   arm1 %10s' % (k, fmt(lev['arm0'].get(k)),
                                                                  fmt(lev['arm1'].get(k))))
    for k in ('cpu_net_us', 'dt_us', 'draws'):
        s = (r.get('pair_stats') or {}).get(k)
        if s and s.get('n'):
            lines.append('    d %-12s mean %s  2SE %s  t %s  n %d'
                         % (k, fmt(s['mean']), fmt(2 * s['se'] if s['se'] else None),
                            fmt(s['t'], 2), s['n']))
    if isinstance(r.get('work_split'), dict):
        ws = r['work_split']
        lines.append('    work %s %%  area mirror valid %s  selected split %s %% match %s %%'
                     % (fmt(None if ws['work'] is None else 100 * ws['work'], 4),
                        (r.get('area_verdict_mirror') or {}).get('valid'),
                        fmt((r.get('area_selected') or {}).get('split_pct'), 3),
                        fmt((r.get('area_selected') or {}).get('match_pct'), 1)))
    for n in r.get('notes', []):
        lines.append('    note: %s' % n)
    lines.append('    failed: %s' % (r.get('failed_controls') or 'none'))
    return lines


def summary(out):
    lines = ['a104.py status=%s seal=%s' % (out['status'], out.get('pred_sha256'))]
    for key in ('mut', 'sh'):
        if out.get(key):
            lines.extend(run_summary(out[key]))
    g = out.get('G')
    if g:
        t, c, h = g['terms'], g['central'], g['ceiling']
        lines.append('  G TERMS (us): cpu_net %s | S_lo %s S_raw %s P_mw %s (2SE %s) T_in %s dI %s'
                     % (fmt(t['cpu_net']), fmt(t['S_lo']), fmt(t['S_raw']), fmt(t['P_mw']),
                        fmt(t['P_mw_2se']), fmt(t['T_in'], 0), fmt(t['dI'])))
        lines.append('    E_rec %s E_com %s W_E(s101) %s | spine %s (mut arm0 %s, pref-based %s)'
                     % (fmt(t['E_rec']), fmt(t['E_com']), fmt(t['W_E_s101']), fmt(t['spine']),
                        fmt(t['spine_mut_arm0']), fmt(t['spine_pref_mut_arm0'])))
        lines.append('    T4 %s (2SE %s) sh_push %s | T4 on dt %s (2SE %s)'
                     % (fmt(t['T4']), fmt(t['T4_2se']), fmt(t['sh_push']), fmt(t['T4_dt']),
                        fmt(t['T4_dt_2se'])))
        lines.append('  CENTRAL: S_now %s E_move %s S_ctx %s T4 %s  ->  G %s  (f=0.39: %s; wall: %s;'
                     ' pref spine: %s)'
                     % (fmt(c.get('S_now')), fmt(c.get('E_move')), fmt(c.get('S_ctx')),
                        fmt(c.get('T4')), fmt(c.get('G')), fmt(c.get('G_f039')),
                        fmt(c.get('G_wall')), fmt(c.get('G_spine_pref'))))
        lines.append('  CEILING: S_now %s E_move %s S_ctx %s T4 %s  ->  G^ %s  (f=0.39: %s)'
                     % (fmt(h.get('S_now')), fmt(h.get('E_move')), fmt(h.get('S_ctx')),
                        fmt(h.get('T4')), fmt(h.get('G')), fmt(h.get('G_f039'))))
        lines.append('  T4 that would bring the CENTRAL G to the bar: %s us; H/M %s; area xrun %s %%'
                     % (fmt(g['kill_T4_central_us']), fmt(g['H_over_M'], 3),
                        fmt(None if g['area_xrun_rel'] is None else 100 * g['area_xrun_rel'], 3)))
        v = out['verdict']
        lines.append('  RULE (G^ < %.0f => A CLOSED): if admitted %s ; VERDICT %s %s'
                     % (BAR_US, v['verdict_if_admitted'], v['verdict'],
                        v['not_evaluable_reasons'] or ''))
    for k, v in sorted((out.get('predictions') or {}).items()):
        lines.append('  prediction %-5s %s value %s band %s  %s'
                     % (k, 'HIT ' if v['hit'] else 'MISS', fmt(v['value'], 3), v['band'], v['text']))
    return '\n'.join(lines)


def evaluate(root, mut_tag, sh_tag, draft=False, geometry=None, gates_file=GATES_FILE):
    out = {'scorer': 'a104.py', 'pred': PRED, 'pred_sha256': None, 'draft': bool(draft)}
    if not draft:
        out['pred_sha256'] = check_seal()
    out['mut'] = evaluate_run(root, mut_tag, 'mut', draft, geometry, gates_file) if mut_tag else None
    out['sh'] = evaluate_run(root, sh_tag, 'sh', draft, geometry, gates_file) if sh_tag else None
    if out['mut'] and out['sh']:
        out['G'] = compute_g(out['mut'], out['sh'])
        out['verdict'] = verdict(out['G'], out['mut'], out['sh'])
        if draft:
            out['verdict']['verdict'] = 'DRAFT (no verdict: draft arithmetic only)'
        out['predictions'] = predictions(out['mut'], out['sh'], out['G'])
    statuses = [r['status'] for r in (out['mut'], out['sh']) if r]
    out['status'] = ('DRAFT' if draft else
                     'ADMITTED' if statuses and all(s == 'ADMITTED' for s in statuses) else 'INVALID')
    out['must_not_be_claimed'] = (
        'a speedup (Stage 1 changes nothing that ships); that route A will reach G; that f = 0.30 '
        'was measured; that the shadow probes reproduce the contention of writing contexts; a '
        'frame-rate figure; 60 FPS')
    return out


def parse_keep(text):
    lo, hi = text.split(':')
    return int(lo), int(hi)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--mut', default=None)
    ap.add_argument('--sh', default=None)
    ap.add_argument('--root', default=PRODUCTION_ROOT)
    ap.add_argument('--out')
    ap.add_argument('--draft', action='store_true')
    ap.add_argument('--period', type=int)
    ap.add_argument('--start', type=int)
    ap.add_argument('--first', type=int)
    ap.add_argument('--keep', type=parse_keep)
    ap.add_argument('--gates-file', default=GATES_FILE)
    ap.add_argument('--json', action='store_true')
    o = ap.parse_args(argv)
    if not (o.mut or o.sh):
        print('nothing to score: give --mut and/or --sh')
        return 2
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
        for tag, kind in ((o.mut, 'mut'), (o.sh, 'sh')):
            if tag and not re.fullmatch(RUNS[kind]['tag_re'], tag):
                print('tag %r is not a pred/02 %s tag' % (tag, kind))
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
        result = evaluate(o.root, o.mut, o.sh, o.draft, geometry or None, o.gates_file)
    except SealError as exc:
        print(str(exc) + ': refusing to score')
        return 2
    if not o.draft:
        exe_sha = sha256_file(EXE) if Path(EXE).is_file() else None
        result['installed_exe_sha256'] = exe_sha
        for key in ('mut', 'sh'):
            r = result.get(key)
            if r:
                r['integrity']['IDENTITY'] = (exe_sha == r.get('binary_sha256') == BINARY_SHA)
                finish_run(r, r['integrity'], r['controls'])
        statuses = [result[k]['status'] for k in ('mut', 'sh') if result.get(k)]
        result['status'] = 'ADMITTED' if all(s == 'ADMITTED' for s in statuses) else 'INVALID'
        if result.get('G'):
            result['verdict'] = verdict(result['G'], result['mut'], result['sh'])
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
