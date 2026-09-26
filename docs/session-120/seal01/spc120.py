"""Session 120, ROADMAP s0.1 "СЕССИЯ 120" items 2, 4, 5; design C:/kyty/s120/design/design120.md sections 2-6 (section 4
with the code-review blocks: the timer-read add-back in N+ and the row-skew rule), spcen.md + spcen_review.md RC1-RC6,
docs/session-120/impl_report.md.  Pre-registration pred/01_cen120.md; fixtures test_spc120.py; mutants mut_spc120.py.

spc120 scores the same-pass census (gate spcen) of the sealed run cen120 (repeat cen120r only on NOT_ADMITTED): Sky
Garden, build BUILD_SHA, 300-s hold, pinned (KYTY_GPU_CLOCK_PIN=1), KYTY_GPU_MARKERS=0, gates gates_base.txt, schedule
SCHEDULE with KYTY_GATE_SCHEDULE_ABBA=1: arm P (0) = ARM_TEXT[0] (census on), arm M (1) = ARM_TEXT[1] (census off).
Members A (the render-target memo inside the open pass), B (the transit skip of CommitBindings), package SP = A + B.

Frames.  Block b starts at frame START + PERIOD * b (its GateArm line); its frames are n = START + 1 + PERIOD*b + pos,
pos 0..89.  WINDOW = positions KEEP[0]..KEEP[1]-1 (10..88) of every block; ESTIMATOR frames = window frames with
draws > DRAWS_MIN.  The arm of a frame is the arm of its block by the GateArm TEXT (never a counter > 0); its main line
must carry arm = that arm and blk = b.  Pairs = blocks (2i, 2i+1) of the ABBA sequence (A B | B A | A B ...), each
with one P and one M block, both with estimator frames, both complete (the later block's window position 88 is at or
before the last main line; as rpk120).  Point values pool the estimator frames of the PAIRED blocks of
an arm (sum / frames; an unpaired block, e.g. a partial last block, feeds the controls only); 2SE = 2 * stdev(per-pair
values) / sqrt(pairs) (a P quantity from the pair's P block, an M one from its M block, a package from the per-pair
sums).  Controls (identities, partitions, nestings, M zeros, emit chain, alive) read every WINDOW frame of every block
(positions 10..88 whatever its draws: design120 s4 "WINDOW sums", RC6 "window frames"); the formulas read the
estimator frames.  Every ns counter is divided by 1000 exactly once (at the member value); bl_tr_us is
microseconds and enters the ns algebra as 1000 * bl_tr_us.

Admission (every check must hold, else NOT_ADMITTED; --draft skips ONLY prereg, hold and pairs):
  binary / installed_now  TAG.json binary_sha256 and the installed exe (derived from the home dir) are BUILD_SHA
  pinned                  env KYTY_GPU_CLOCK_PIN == '1' and exactly one `GpuClockPin:` line, mode 1
  env_exact / env_vk      the KYTY_* env is exactly ENV_EXPECT; of VK_* only VK_ALLOWED
  hold                    TAG.json hold_s == HOLD_S
  one_ok_attempt          exactly one attempt, outcome ok, hold_exit None
  prereg                  TAG.json prereg path PRED_PATH, its sha256/bytes == PRED_SHA/PRED_BYTES == the file now
                          (PRED_SHA / PRED_BYTES None => refused: no sealed verdict without the seal)
  gates_exact             the whitespace-normalised TAG.json gate text hashes to GATES_TEXT_SHA
  gates_base              GATES_FILE hashes to GATES_FILE_SHA and its normalised text to GATES_TEXT_SHA
  base_names              the gate text pins BASE_PINS and names none of BASE_ABSENT (neither do the arm texts)
  gate_lines              every `Gate:` line is `Gate: NAME=V frame=F`, NAME a schedule name, F a block start, V the
                          value of that block's arm
  arms                    every `GateArm:` line parses; arms=2 period=PERIOD abba=1; text exactly ARM_TEXT[arm]; block b
                          at frame START + PERIOD*b; arm = ABBA[b % 4]; blocks consecutive from 0
  sp_logged               exactly one `SpCensus: mode 1` line
  no_marker               no hang/crash marker (MARKERS) in the log or stdout_TAG.txt
  no_skip_window          no `AsyncPipelines: skipped draw` attributed to a window frame (the frame after the last main
                          FrameTrace line printed before it)
  streams_complete        every window frame up to the last main line has exactly one FrameTrace, FrameTrace-draw and
                          FrameTrace-x line with every field read (MAIN_FIELDS, DRAW_FIELDS, X_FIELDS), arm and blk right;
                          the last main line itself is exempt when its -draw/-x line is missing or cut (the run ended
                          there; g2_119, rpk120) and is then not a row
  pairs                   >= MIN_PAIRS complete pairs
  idle                    pre_run.gpu_util_median <= IDLE_GPU_MAX

Correctness (over ALL FrameTrace-x lines of the run, every n, duplicates included) => FAIL of the member:
  A: sum sp_rt_bad > 0 or any `SpRtMismatch:` line;  B: sum sp_tr_bad > 0 or any `SpTrMismatch:` line.
Controls (=> NOT_EVALUABLE; common ones hit A, B and SP):
  common  admitted; estimator frames in both arms; >= 2 pairs; zbar (P sum r2_nul_n > 0 and zbar > 0); M zeros (every
          M_ZERO field sums to 0 over the M window frames: RC6, window only); ser_alive (sum sp_ser_n > 0 in both arms);
          ser_nest (sp_ser_val <= sp_ser_n + SKEW_COUNT per block, both arms); alive (P sum sp_rt_n, sp_tr_n > 0, both
          arms sum pl_em_n > 0); arm_assert (both texts pathlap=1 mutsite=1 bindlap=1, cbmove/slicecen/spine absent or
          0; P spcen=1 r2cen=2, M spcen=0)
  A       race: 10^4 * sum_all sp_rt_race <= sum_all sp_rt_would; nt: sum sp_rt_nt over every row of every P block
          (arm by the GateArm text, all positions) = 0;
          draw_id: |sum sp_rt_n - sum pl_em_n| <= DRAW_ID_BLOCK_TOL per P block and <= DRAW_ID_TOL over the P window;
          rt_part: |sp_rt_n - sp_rt_would - sum RT_REASONS| <= SKEW_COUNT per P block; a_nest (A_NESTS); emit_chain:
          |mean(sum EMIT_PARTS)/1000 - mean mh_emit_us| <= EMIT_TOL_US in each arm; a_den: P sum pl_em_rt_ns > 0
  B       tr_part (6 reasons, as rt_part); b_nest (B_NESTS); bl_tr_alive: sum bl_tr_us > 0 in both arms (RC5(e));
          b_den: P sum sp_tr_loop_ns > 0
  Nestings are tested on the window sums of every P block: a count pair within SKEW_COUNT; a multi-unit pair (ns,
  slots, targets, Kpx) within the subset counter's own values on the block's first and last window lines (a
  straddling event lands in at most those lines); sp_tr_loop_ns <= 1000*bl_tr_us also gets TR_ROUND_NS a row.

Formulas (per frame, P estimator frames unless (M)):
  G_A = pl_em_rt_hit_ns                      N_A = pl_em_rt_hit_ns - pl_em_spchk_ns - sp_rt_rep_ns - sp_rt_rec_ns
  G_B = bl_tr_hit_ns                         N_B = bl_tr_hit_ns - sp_tr_chk_ns - sp_tr_rep_ns - sp_tr_rec_ns
  zbar = sum r2_nul_ns / sum r2_nul_n        Z_A = zbar*(2*sp_rt_n + sp_rt_rec)     Z_B = zbar*2*sp_tr_n
  D_A = pl_em_rt_ns(M) - pl_em_rt_ns(P)      D_B = 1000*(bl_tr_us(M) - bl_tr_us(P))     D_B' = D_B + zbar*sp_tr_n(P)
  T_A = max(0, D_A) * pl_em_rt_hit_ns / pl_em_rt_ns        T_B = max(0, D_B') * bl_tr_hit_ns / sp_tr_loop_ns
  point: N_A, N_B, N = N_A + N_B            upper: N_A+ = N_A + Z_A + T_A, N_B+ = N_B + Z_B + T_B, N+ = N_A+ + N_B+
  reported only: G, G+ = G + T, the global-witness N^g (hitg, replay scaled by wg/would), the unclamped D_A, D_B, D_B',
  the P-M price of dt_us and cpu_gpu_us, bda_scan (regime NEW <= BDA_NEW_MAX, OLD >= BDA_OLD_MIN).
  zbar in the per-pair values is the pooled P-window zbar (a timer constant, not a pair quantity).
Verdict (member and package): FAIL > NOT_EVALUABLE > OPEN (point >= THRESHOLD_US) > CLOSED (upper + 2SE < THRESHOLD_US)
  > NOT_OPENED.  2SE in the output line is the 2SE of the upper (the value CLOSED reads).
Consequences (pred "Member verdicts", ROADMAP s120 item 4): every member carries its own (`CONSEQUENCE A:`/`B:`); the
  summary `CONSEQUENCE:` is FAIL if the package fails, else NOT_ADMITTED, else OPEN naming the OPEN member(s) when any
  member or the package is OPEN, else the package's own.

    python C:/kyty/s120/spc120.py [--root C:/kyty/s120] [--tag cen120|cen120r] [--draft] [--out <json>]
                                  [--installed-sha <sha>]
"""
import hashlib
import json
import math
import os
import re
import statistics
import sys
from pathlib import Path

ROOT = 'C:/kyty/s120'
TAG = 'cen120'
TAGS = ('cen120', 'cen120r')
BUILD_SHA = '15cdbfc6e2c9d19a9aa803beaa1dff670d3403b54b74b56f4911c456de4ca661'
INSTALLED = os.path.expanduser('~') + '/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
HOLD_S = 300
PERIOD = 90
START = 1800
KEEP = (10, 89)
DRAWS_MIN = 3000
ABBA = (0, 1, 1, 0)
ARM_TEXT = ('r1cen=2 r2cen=2 spcen=1 bindlap=1 pathlap=1 mutsite=1',
            'r1cen=0 r2cen=1 spcen=0 bindlap=1 pathlap=1 mutsite=1')
MIN_PAIRS = 30
THRESHOLD_US = 500.0
RACE_PER = 10000
SKEW_COUNT = 8          # row skew of a count pair, counts a block window (ROADMAP s120 item 6; was 2)
DRAW_ID_BLOCK_TOL = 64
DRAW_ID_TOL = 256
EMIT_TOL_US = 256
TR_ROUND_NS = 1000
IDLE_GPU_MAX = 10
BDA_NEW_MAX = 300
BDA_OLD_MIN = 600
GATES_FILE = 'C:/kyty/s120/gates_base.txt'
GATES_FILE_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'
GATES_TEXT_SHA = '91da50f6d85b99d09fe4198da1438f5766a0773112268302efa62c0d1ba09c5e'
BASE_PINS = {'texmemo2': '0', 'texfastcheck': '0', 'm4baton': '0', 'fslean': '0'}
BASE_ABSENT = ('bindwit', 'bindalt', 'blmove', 'bindfloor', 'cbmove', 'slicecen', 'spine', 'bindpack')
PRED_PATH = 'C:/kyty/s120/pred/01_cen120.md'
PRED_SHA = 'd20cd3de41cb8e58634e7ac024c76338a51b4bfa33a6415b3cbabd148ab73849'  # pred/01_cen120.md, sealed (session 120 seal 01)
PRED_BYTES = 8483        # pred/01_cen120.md, sealed
NL = chr(10)
SCHEDULE = '90+1800:' + ARM_TEXT[0] + '|' + ARM_TEXT[1]
ENV_EXPECT = {
    'KYTY_FRAME_TRACE': 'lite',
    'KYTY_GPU_HANG_ABORT_S': '8',
    'KYTY_GATE_FILE': 'C:\\kyty\\s120\\gates.req',
    'KYTY_SAMPLE_GATE': 'C:\\kyty\\s120\\sample.req',
    'KYTY_QUEUE_TRACE': '1',
    'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden',
    'KYTY_GATE_SCHEDULE': SCHEDULE,
    'KYTY_GATE_SCHEDULE_ABBA': '1',
    'KYTY_GPU_CLOCK_PIN': '1',
    'KYTY_GPU_MARKERS': '0',
}
VK_ALLOWED = ('VK_SDK_PATH',)
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---')
SKIP_MARK = b'AsyncPipelines: skipped draw'
RT_MISMATCH = b'SpRtMismatch:'
TR_MISMATCH = b'SpTrMismatch:'
SP_CENSUS = b'SpCensus: mode 1'

RT_REASONS = ('sp_rt_x_memo', 'sp_rt_x_cfg', 'sp_rt_x_dclr', 'sp_rt_x_meta', 'sp_rt_x_ids', 'sp_rt_x_live',
              'sp_rt_x_ser', 'sp_rt_x_bound', 'sp_rt_x_dsmp', 'sp_rt_x_pass')
TR_REASONS = ('sp_tr_x_big', 'sp_tr_x_memo', 'sp_tr_x_meta', 'sp_tr_x_shape', 'sp_tr_x_ser', 'sp_tr_x_flags')
SP_FIELDS = ('sp_ser_n', 'sp_ser_val', 'sp_rt_n', 'sp_rt_would', 'sp_rt_wg', 'sp_rt_tgt', 'pl_em_spchk_ns',
             'sp_rt_chkh_ns', 'pl_em_rt_hit_ns', 'pl_em_rt_hitg_ns', 'pl_em_sppost_ns', 'sp_rt_rep_ns', 'sp_rt_rep_att',
             'sp_rt_rep_kpx', 'sp_rt_rec', 'sp_rt_rec_ns', 'sp_rt_bad', 'sp_rt_race', 'sp_rt_rst', 'sp_rt_nt') \
    + RT_REASONS + ('sp_tr_n', 'sp_tr_slots', 'sp_tr_would', 'sp_tr_wg', 'sp_tr_wslots', 'sp_tr_loop_ns',
                    'bl_tr_hit_ns', 'bl_tr_hitg_ns', 'sp_tr_chk_ns', 'sp_tr_chkh_ns', 'sp_tr_post_ns', 'sp_tr_rep_ns',
                    'sp_tr_rec', 'sp_tr_rec_ns', 'sp_tr_bad', 'sp_tr_dcc') + TR_REASONS
EMIT_PARTS = ('pl_em_vtx_ns', 'pl_em_spchk_ns', 'pl_em_rt_ns', 'pl_em_sppost_ns', 'pl_em_pipe_ns', 'pl_em_com_ns',
              'pl_em_rec_ns', 'pl_em_rest_ns')
MAIN_FIELDS = ('dt_us', 'cpu_gpu_us', 'draws', 'arm', 'blk')
DRAW_FIELDS = ('bda_scan',)
X_FIELDS = SP_FIELDS + ('pl_em_vtx_ns', 'pl_em_rt_ns', 'pl_em_pipe_ns', 'pl_em_com_ns', 'pl_em_rec_ns',
                        'pl_em_rest_ns', 'pl_em_n', 'mh_emit_us', 'bl_tr_us', 'r2_nul_ns', 'r2_nul_n', 'rt_att',
                        'rt_kpx', 'rt_fast_ok', 'rt_fast_no')
ALL_ROW_FIELDS = ('sp_rt_bad', 'sp_tr_bad', 'sp_rt_race', 'sp_rt_would', 'sp_rt_nt')
M_ZERO = tuple(k for k in SP_FIELDS if k not in ('sp_ser_n', 'sp_ser_val'))
# nestings: (name, subset, superset, kind); kind 'count' = unit Adds (SKEW_COUNT), 'edge' = the subset's edge lines
A_NESTS = (('rt_wg', 'sp_rt_wg', 'sp_rt_would', 'count'),
           ('rt_hitg', 'pl_em_rt_hitg_ns', 'pl_em_rt_hit_ns', 'edge'),
           ('rt_hit', 'pl_em_rt_hit_ns', 'pl_em_rt_ns', 'edge'),
           ('rt_chkh', 'sp_rt_chkh_ns', 'pl_em_spchk_ns', 'edge'),
           ('rt_rep', 'sp_rt_rep_ns', 'pl_em_sppost_ns', 'edge'),
           ('rt_att', 'sp_rt_rep_att', 'rt_att', 'edge'),
           ('rt_kpx', 'sp_rt_rep_kpx', 'rt_kpx', 'edge'),
           ('rt_att_tgt', 'sp_rt_rep_att', 'sp_rt_tgt', 'edge'),
           ('rt_tgt', 'sp_rt_tgt', ('rt_fast_ok', 'rt_fast_no'), 'edge'))
B_NESTS = (('tr_wg', 'sp_tr_wg', 'sp_tr_would', 'count'),
           ('tr_wslots', 'sp_tr_wslots', 'sp_tr_slots', 'edge'),
           ('tr_hitg', 'bl_tr_hitg_ns', 'bl_tr_hit_ns', 'edge'),
           ('tr_hit', 'bl_tr_hit_ns', 'sp_tr_loop_ns', 'edge'),
           ('tr_loop', 'sp_tr_loop_ns', 'bl_tr_us', 'us'),
           ('tr_chkh', 'sp_tr_chkh_ns', 'sp_tr_chk_ns', 'edge'),
           ('tr_rep', 'sp_tr_rep_ns', 'sp_tr_post_ns', 'edge'),
           ('tr_rec', 'sp_tr_rec_ns', 'sp_tr_post_ns', 'edge'))
KINDS = ((re.compile(rb'^FrameTrace: n=(\d+)'), 'main', MAIN_FIELDS),
         (re.compile(rb'^FrameTrace-draw: n=(\d+)'), 'draw', DRAW_FIELDS),
         (re.compile(rb'^FrameTrace-x: n=(\d+)'), 'x', X_FIELDS))
FIELD = re.compile(rb' (\w+)=(-?\d+)')
PIN = re.compile(rb'^GpuClockPin: mode (\d+)')
GATE = re.compile(rb'^Gate: (\w+)=(\d+) frame=(\d+)$')
GATE_ARM = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
CONSEQUENCES = {
    'FAIL': 'FAIL - "механизм неверен" (ROADMAP s120 item 4: любой счётчик ошибок члена > 0 на ЛЮБОЙ строке или '
            'строка *Mismatch:); the spcen mechanism is unsound as designed, the next session starts with correctness',
    'NOT_EVALUABLE': 'NOT_EVALUABLE - "провал допуска, тождеств, выборок, контролей, здравого смысла" (ROADMAP s120 '
                     'item 4): no verdict on the spcen path',
    'OPEN': 'OPEN - "открывается трек несущего члена, отгрузка — только по п. 2(в)" (ROADMAP s120 item 4): a speed '
            'track opens for the carrying member(s) %s; a would-hit is a ceiling, not a speed-up',
    'CLOSED': 'CLOSED - "путь записывается исчерпанным на Sky Garden по правилу 0,5 мс" (ROADMAP s120 item 4)',
    'NOT_OPENED': 'NOT_OPENED - "граница, записывается; допустим только повтор, решается при закрытии" (ROADMAP s120 '
                  'item 4)',
    'NOT_ADMITTED': 'NOT_ADMITTED - "повтор cen120r — только при NOT_ADMITTED" (ROADMAP s120 item 4): admission, '
                    'not a verdict',
}
_UNSET = object()


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def is_marker(line):
    low = line.lower()
    return any(k in low for k in MARKERS)


def idle_ok(meta):
    v = (meta.get('pre_run') or {}).get('gpu_util_median')
    return isinstance(v, (int, float)) and v <= IDLE_GPU_MAX


def arm_values(text):
    return dict(pair.split('=') for pair in text.split())


ARM_VALUES = tuple(arm_values(t) for t in ARM_TEXT)


def arm_assert():
    """The arm texts themselves (design120 s5, RC5(e)): pathlap, mutsite, bindlap on in both; the stage-span gates
    off; P arms the census and the R2 null pair, M does not arm the census."""
    for v in ARM_VALUES:
        if v.get('pathlap') != '1' or v.get('mutsite') != '1' or v.get('bindlap') != '1':
            return False
        if any(v.get(k, '0') != '0' for k in ('cbmove', 'slicecen', 'spine')):
            return False
    return (ARM_VALUES[0].get('spcen') == '1' and ARM_VALUES[0].get('r2cen') == '2'
            and ARM_VALUES[1].get('spcen') == '0')


def window_pos(n):
    """(block, position) of frame n > START, else None."""
    if n <= START:
        return None
    return (n - START - 1) // PERIOD, (n - START - 1) % PERIOD


def in_window(pos):
    return KEEP[0] <= pos < KEEP[1]


def arms_ok(gate_arms):
    blocks = {}
    for g in gate_arms:
        if g is None:
            return False, {}
        arm, arms, block, frame, period, abba, text = g
        if arms != 2 or period != PERIOD or abba != 1 or arm not in (0, 1) or text != ARM_TEXT[arm]:
            return False, {}
        if frame != START + PERIOD * block or ABBA[block % 4] != arm or block in blocks:
            return False, {}
        blocks[block] = arm
    ok = bool(blocks) and sorted(blocks) == list(range(len(blocks)))
    return ok, blocks


def gate_lines_ok(lines, blocks):
    for raw in lines:
        m = GATE.match(raw)
        if m is None:
            return False
        name = m.group(1).decode()
        frame = int(m.group(3))
        if name not in ARM_VALUES[0] or (frame - START) % PERIOD != 0 or frame < START:
            return False
        block = (frame - START) // PERIOD
        if block not in blocks or m.group(2).decode() != ARM_VALUES[blocks[block]][name]:
            return False
    return True


def read_run(root, tag):
    """One pass over log_TAG.txt (and stdout_TAG.txt): the rows, the diagnostic lines, the all-row sums."""
    pins, gate_arms, gate_lines, markers, census = [], [], [], [], []
    seen = {'main': {}, 'draw': {}, 'x': {}}
    dups = set()
    all_rows = {k: 0 for k in ALL_ROW_FIELDS}
    by_n = {}
    rt_lines = 0
    tr_lines = 0
    skip_frames = []
    last_main = None
    with open(Path(root) / ('log_%s.txt' % tag), 'rb') as f:
        for line in f:
            if line.startswith(b'FrameTrace'):
                for regex, kind, names in KINDS:
                    m = regex.match(line)
                    if m is None:
                        continue
                    n = int(m.group(1))
                    got = dict(FIELD.findall(line, m.end()))
                    rec = {k: int(got[k.encode()]) for k in names if k.encode() in got}
                    if kind == 'x':
                        row = by_n.setdefault(n, {k: 0 for k in ALL_ROW_FIELDS})
                        for k in ALL_ROW_FIELDS:
                            v = int(got.get(k.encode(), 0))
                            all_rows[k] += v
                            row[k] += v
                    if kind == 'main':
                        last_main = n
                    if n in seen[kind]:
                        dups.add(n)
                    seen[kind][n] = rec if len(rec) == len(names) else None
                    break
                continue
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
            if SKIP_MARK in line:
                skip_frames.append(None if last_main is None else last_main + 1)
            if RT_MISMATCH in line:
                rt_lines += 1
            if TR_MISMATCH in line:
                tr_lines += 1
            if line.startswith(b'SpCensus:'):
                census.append(line.rstrip())
            if line.startswith(b'GpuClockPin:'):
                mp = PIN.match(line)
                pins.append(int(mp.group(1)) if mp else -1)
            if line.startswith(b'GateArm:'):
                mg = GATE_ARM.match(line.rstrip(b'\r\n'))
                gate_arms.append(None if mg is None else tuple(int(x) for x in mg.groups()[:6])
                                 + (mg.group(7).decode('utf-8', 'replace').strip(),))
            if line.startswith(b'Gate: '):
                gate_lines.append(line.rstrip())
    so = Path(root) / ('stdout_%s.txt' % tag)
    if so.is_file():
        for line in open(so, 'rb'):
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
    return dict(pins=pins, gate_arms=gate_arms, gate_lines=gate_lines, markers=markers, census=census, seen=seen,
                dups=dups, all_rows=all_rows, by_n=by_n, rt_lines=rt_lines, tr_lines=tr_lines,
                skip_frames=skip_frames)


def se2(values):
    """2 * standard error of the mean of the per-pair values; None when fewer than two or any is None."""
    if len(values) < 2 or any(v is None for v in values):
        return None
    return 2.0 * statistics.stdev(values) / math.sqrt(len(values))


def div(a, b):
    return None if not b else a / b


def ssum(rows, key):
    return sum(r[key] for r in rows)


def terms(prow, mrow, zbar):
    """Every formula term from P estimator rows prow and M estimator rows mrow (per frame, microseconds unless _ns);
    zbar in ns.  Missing denominators give None, never NaN."""
    nfp, nfm = len(prow), len(mrow)
    t = dict(nfp=nfp, nfm=nfm)
    if not nfp or not nfm or zbar is None:
        return t

    def sp(k):
        return ssum(prow, k)

    def sm(k):
        return ssum(mrow, k)

    t['G_A'] = sp('pl_em_rt_hit_ns') / nfp / 1000
    t['G_B'] = sp('bl_tr_hit_ns') / nfp / 1000
    t['N_A'] = (sp('pl_em_rt_hit_ns') - sp('pl_em_spchk_ns') - sp('sp_rt_rep_ns') - sp('sp_rt_rec_ns')) / nfp / 1000
    t['N_B'] = (sp('bl_tr_hit_ns') - sp('sp_tr_chk_ns') - sp('sp_tr_rep_ns') - sp('sp_tr_rec_ns')) / nfp / 1000
    t['N'] = t['N_A'] + t['N_B']
    t['Z_A'] = zbar * (2 * sp('sp_rt_n') + sp('sp_rt_rec')) / nfp / 1000
    t['Z_B'] = zbar * (2 * sp('sp_tr_n')) / nfp / 1000
    t['Z'] = t['Z_A'] + t['Z_B']
    t['D_A_ns'] = sm('pl_em_rt_ns') / nfm - sp('pl_em_rt_ns') / nfp
    t['D_B_ns'] = 1000 * (sm('bl_tr_us') / nfm - sp('bl_tr_us') / nfp)
    t['D_Bp_ns'] = t['D_B_ns'] + zbar * sp('sp_tr_n') / nfp
    r_a = div(sp('pl_em_rt_hit_ns'), sp('pl_em_rt_ns'))
    r_b = div(sp('bl_tr_hit_ns'), sp('sp_tr_loop_ns'))
    t['r_A'], t['r_B'] = r_a, r_b
    t['T_A'] = None if r_a is None else max(0.0, t['D_A_ns']) * r_a / 1000
    t['T_B'] = None if r_b is None else max(0.0, t['D_Bp_ns']) * r_b / 1000
    t['N_A_up'] = None if t['T_A'] is None else t['N_A'] + t['Z_A'] + t['T_A']
    t['N_B_up'] = None if t['T_B'] is None else t['N_B'] + t['Z_B'] + t['T_B']
    t['N_up'] = None if t['N_A_up'] is None or t['N_B_up'] is None else t['N_A_up'] + t['N_B_up']
    t['G_A_up'] = None if t['T_A'] is None else t['G_A'] + t['T_A']
    t['G_B_up'] = None if t['T_B'] is None else t['G_B'] + t['T_B']
    t['G_A_g'] = sp('pl_em_rt_hitg_ns') / nfp / 1000
    t['G_B_g'] = sp('bl_tr_hitg_ns') / nfp / 1000
    wa = div(sp('sp_rt_wg'), sp('sp_rt_would'))
    wb = div(sp('sp_tr_wg'), sp('sp_tr_would'))
    t['N_A_g'] = None if wa is None else (sp('pl_em_rt_hitg_ns') - sp('pl_em_spchk_ns') - sp('sp_rt_rep_ns') * wa
                                          - sp('sp_rt_rec_ns')) / nfp / 1000
    t['N_B_g'] = None if wb is None else (sp('bl_tr_hitg_ns') - sp('sp_tr_chk_ns') - sp('sp_tr_rep_ns') * wb
                                          - sp('sp_tr_rec_ns')) / nfp / 1000
    t['price_dt_us'] = sp('dt_us') / nfp - sm('dt_us') / nfm
    t['price_cpu_gpu_us'] = sp('cpu_gpu_us') / nfp - sm('cpu_gpu_us') / nfm
    return t


def nest_ok(blocks_rows, sub, sup, kind):
    """subset <= superset on the window sums of every P block, within the row-skew tolerance of design120 s4."""
    for rows in blocks_rows:
        s = ssum(rows, sub)
        if isinstance(sup, tuple):
            big = sum(ssum(rows, k) for k in sup)
        elif kind == 'us':
            big = 1000 * ssum(rows, sup) + TR_ROUND_NS * len(rows)
        else:
            big = ssum(rows, sup)
        if kind == 'count':
            tol = SKEW_COUNT
        else:
            tol = rows[0][sub] + rows[-1][sub]
        if s > big + tol:
            return False
    return True


def part_ok(blocks_rows, total, would, reasons):
    for rows in blocks_rows:
        res = ssum(rows, total) - ssum(rows, would) - sum(ssum(rows, k) for k in reasons)
        if abs(res) > SKEW_COUNT:
            return False
    return True


def verdict(fail, notev, point, upper, two_se):
    if fail:
        return 'FAIL'
    if notev or point is None or upper is None or two_se is None:
        return 'NOT_EVALUABLE'
    if point >= THRESHOLD_US:
        return 'OPEN'
    if upper + two_se < THRESHOLD_US:
        return 'CLOSED'
    return 'NOT_OPENED'


def evaluate(root=ROOT, tag=TAG, installed_sha=None, draft=False, pred_want=_UNSET, pred_now=_UNSET, min_pairs=None,
             gates_file=GATES_FILE):
    """Admission, correctness, controls, the member and package verdicts, and every term.  installed_sha None = hash
    the installed exe; pred_want (sha, bytes) default (PRED_SHA, PRED_BYTES); pred_now (sha, bytes) default = the file
    PRED_PATH now; min_pairs default MIN_PAIRS."""
    min_pairs = MIN_PAIRS if min_pairs is None else min_pairs
    want_sha, want_bytes = (PRED_SHA, PRED_BYTES) if pred_want is _UNSET else pred_want
    res = dict(scorer_sha256=sha_file(__file__), build_sha256=BUILD_SHA, tag=tag, draft=bool(draft))
    meta = json.loads((Path(root) / (tag + '.json')).read_text(encoding='utf-8'))
    env = meta.get('env') or {}
    kyty_env = {k: v for k, v in env.items() if k.startswith('KYTY_')}
    vk_env = sorted(k for k in env if k.startswith('VK_'))
    atts = meta.get('attempts') or []
    ok_att = [a for a in atts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]
    gates = ' '.join((meta.get('gates') or '').split())
    gate_names = dict(p.split('=', 1) for p in gates.split() if '=' in p)
    prereg = meta.get('prereg') or {}
    run = read_run(root, tag)
    seen, dups = run['seen'], run['dups']
    arms_fine, blocks = arms_ok(run['gate_arms'])

    last_main = max(seen['main']) if seen['main'] else 0
    streams_bad = []
    est = {}
    win = {}
    for b, arm in sorted(blocks.items()):
        rows = []
        for pos in range(KEEP[0], KEEP[1]):
            n = START + 1 + PERIOD * b + pos
            if n > last_main:
                break
            main, draw, x = seen['main'].get(n), seen['draw'].get(n), seen['x'].get(n)
            if n == last_main and (draw is None or x is None):
                break
            if n in dups or main is None or draw is None or x is None or main['arm'] != arm or main['blk'] != b:
                streams_bad.append(n)
                continue
            rows.append(dict(main, **draw, **x))
        win[b] = rows
        est[b] = [r for r in rows if r['draws'] > DRAWS_MIN]
    arm_of = {b: blocks[b] for b in est}
    p_blocks = [win[b] for b in sorted(win) if arm_of[b] == 0 and win[b]]
    m_blocks = [win[b] for b in sorted(win) if arm_of[b] == 1 and win[b]]
    prow_all = [r for rows in p_blocks for r in rows]
    mrow_all = [r for rows in m_blocks for r in rows]
    pairs = []
    for b in sorted(est):
        if (b % 2 == 0 and b + 1 in est and est[b] and est[b + 1]
                and START + PERIOD * (b + 1) + KEEP[1] <= last_main):
            p, m = (b, b + 1) if arm_of[b] == 0 else (b + 1, b)
            pairs.append((p, m))
    prow = [r for p, m in pairs for r in est[p]]
    mrow = [r for p, m in pairs for r in est[m]]
    skip_window = [f for f in run['skip_frames']
                   if f is not None and window_pos(f) is not None and window_pos(f)[0] in blocks
                   and in_window(window_pos(f)[1])]

    if installed_sha is None:
        installed_sha = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    if pred_now is _UNSET:
        pp = Path(PRED_PATH)
        pred_now = (sha_file(pp), pp.stat().st_size) if pp.is_file() else (None, None)
    prereg_ok = (want_sha is not None and want_bytes is not None
                 and str(prereg.get('path') or '').replace('\\', '/') == PRED_PATH
                 and prereg.get('sha256') == want_sha and prereg.get('bytes') == want_bytes
                 and pred_now[0] == want_sha and pred_now[1] == want_bytes)
    gf = Path(gates_file)
    gates_base = (gf.is_file() and sha_file(gf) == GATES_FILE_SHA and hashlib.sha256(
        ' '.join(gf.read_text(encoding='utf-8').split()).encode('utf-8')).hexdigest() == GATES_TEXT_SHA)
    arm_names = set(ARM_VALUES[0]) | set(ARM_VALUES[1])
    checks = dict(
        binary=meta.get('binary_sha256') == BUILD_SHA,
        installed_now=installed_sha == BUILD_SHA,
        pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and run['pins'] == [1],
        env_exact=kyty_env == ENV_EXPECT,
        env_vk=all(k in VK_ALLOWED for k in vk_env),
        hold=None if draft else meta.get('hold_s') == HOLD_S,
        one_ok_attempt=len(atts) == 1 and len(ok_att) == 1,
        prereg=None if draft else prereg_ok,
        gates_exact=hashlib.sha256(gates.encode('utf-8')).hexdigest() == GATES_TEXT_SHA,
        gates_base=gates_base,
        base_names=(all(gate_names.get(k) == v for k, v in BASE_PINS.items())
                    and not any(k in gate_names or k in arm_names for k in BASE_ABSENT)),
        gate_lines=gate_lines_ok(run['gate_lines'], blocks),
        arms=arms_fine,
        sp_logged=len(run['census']) == 1 and run['census'][0].startswith(SP_CENSUS),
        no_marker=not run['markers'],
        no_skip_window=not skip_window,
        streams_complete=not streams_bad,
        pairs=None if draft else len(pairs) >= min_pairs,
        idle=idle_ok(meta))
    admitted = all(v is not False for v in checks.values())

    def sp(k):
        return ssum(prow, k)

    def sm(k):
        return ssum(mrow, k)

    def cp(k):
        return ssum(prow_all, k)

    def cm(k):
        return ssum(mrow_all, k)

    zbar = div(sp('r2_nul_ns'), sp('r2_nul_n'))
    all_rows = run['all_rows']
    nt_p = sum(v['sp_rt_nt'] for n, v in run['by_n'].items()
               if window_pos(n) is not None and blocks.get(window_pos(n)[0]) == 0)
    em_p = None if not prow_all else abs(sum(cp(k) for k in EMIT_PARTS) / len(prow_all) / 1000
                                         - cp('mh_emit_us') / len(prow_all))
    em_m = None if not mrow_all else abs(sum(cm(k) for k in EMIT_PARTS) / len(mrow_all) / 1000
                                         - cm('mh_emit_us') / len(mrow_all))
    common = dict(
        admitted=admitted,
        frames=bool(prow) and bool(mrow),
        pairs2=len(pairs) >= 2,
        zbar=sp('r2_nul_n') > 0 and zbar is not None and zbar > 0,
        m_zeros=all(cm(k) == 0 for k in M_ZERO),
        ser_alive=cp('sp_ser_n') > 0 and cm('sp_ser_n') > 0,
        ser_nest=nest_ok(p_blocks + m_blocks, 'sp_ser_val', 'sp_ser_n', 'count'),
        alive=cp('sp_rt_n') > 0 and cp('sp_tr_n') > 0 and cp('pl_em_n') > 0 and cm('pl_em_n') > 0,
        arm_assert=arm_assert())
    a_ctl = dict(
        race=RACE_PER * all_rows['sp_rt_race'] <= all_rows['sp_rt_would'],
        nt=nt_p == 0,
        draw_id=(all(abs(ssum(rows, 'sp_rt_n') - ssum(rows, 'pl_em_n')) <= DRAW_ID_BLOCK_TOL for rows in p_blocks)
                 and abs(cp('sp_rt_n') - cp('pl_em_n')) <= DRAW_ID_TOL),
        rt_part=part_ok(p_blocks, 'sp_rt_n', 'sp_rt_would', RT_REASONS),
        emit_chain=em_p is not None and em_m is not None and em_p <= EMIT_TOL_US and em_m <= EMIT_TOL_US,
        a_den=sp('pl_em_rt_ns') > 0)
    for name, sub, sup, kind in A_NESTS:
        a_ctl['nest_' + name] = nest_ok(p_blocks, sub, sup, kind)
    b_ctl = dict(
        tr_part=part_ok(p_blocks, 'sp_tr_n', 'sp_tr_would', TR_REASONS),
        bl_tr_alive=sp('bl_tr_us') > 0 and sm('bl_tr_us') > 0,
        b_den=sp('sp_tr_loop_ns') > 0)
    for name, sub, sup, kind in B_NESTS:
        b_ctl['nest_' + name] = nest_ok(p_blocks, sub, sup, kind)

    t = terms(prow, mrow, zbar if common['zbar'] else None)
    per_pair = [terms(est[p], est[m], zbar if common['zbar'] else None) for p, m in pairs]

    def pair_col(key):
        return [pt.get(key) for pt in per_pair]

    fail_a = all_rows['sp_rt_bad'] > 0 or run['rt_lines'] > 0
    fail_b = all_rows['sp_tr_bad'] > 0 or run['tr_lines'] > 0
    ne_common = not all(common.values())
    ne_a = ne_common or not all(a_ctl.values())
    ne_b = ne_common or not all(b_ctl.values())
    members = {}
    for name, fail, notev, pk, uk in (('A', fail_a, ne_a, 'N_A', 'N_A_up'), ('B', fail_b, ne_b, 'N_B', 'N_B_up'),
                                      ('SP', fail_a or fail_b, ne_a or ne_b, 'N', 'N_up')):
        two_se = se2(pair_col(uk))
        members[name] = dict(verdict=verdict(fail, notev, t.get(pk), t.get(uk), two_se), point=t.get(pk),
                             upper=t.get(uk), se2_upper=two_se, se2_point=se2(pair_col(pk)))
    sp_v = members['SP']['verdict']
    carrying = [n for n in ('A', 'B') if members[n]['verdict'] == 'OPEN']
    if sp_v == 'FAIL':
        consequence = CONSEQUENCES['FAIL']
    elif not admitted:
        consequence = CONSEQUENCES['NOT_ADMITTED']
    elif sp_v == 'OPEN' or carrying:
        consequence = CONSEQUENCES['OPEN'] % ('+'.join(carrying) if carrying else 'A+B (together)')
    else:
        consequence = CONSEQUENCES[sp_v]
    member_consequence = {}
    for n in ('A', 'B'):
        v = members[n]['verdict']
        if v == 'FAIL':
            member_consequence[n] = CONSEQUENCES['FAIL']
        elif not admitted:
            member_consequence[n] = CONSEQUENCES['NOT_ADMITTED']
        elif v == 'OPEN':
            member_consequence[n] = CONSEQUENCES['OPEN'] % n
        else:
            member_consequence[n] = CONSEQUENCES[v]
    report = {}
    for arm, rows in ((0, prow), (1, mrow)):
        report[arm] = {k: (ssum(rows, k) / len(rows) if rows else None) for k in MAIN_FIELDS + DRAW_FIELDS + X_FIELDS}
        report[arm]['frames'] = len(rows)
        bda = report[arm]['bda_scan']
        report[arm]['bda_regime'] = (None if bda is None else 'NEW' if bda <= BDA_NEW_MAX
                                     else 'OLD' if bda >= BDA_OLD_MIN else 'MIXED')
    pair_price = [pt.get('price_dt_us') for pt in per_pair]
    res.update(checks=checks, verdict='ADMITTED' if admitted else 'NOT_ADMITTED', common=common, a_controls=a_ctl,
               b_controls=b_ctl, members=members, consequence=consequence, carrying=carrying,
               member_consequence=member_consequence, terms=t, zbar_ns=zbar,
               pairs=[list(p) for p in pairs], per_pair=per_pair, se2_price_dt_us=se2(pair_price),
               se2_price_cpu_gpu_us=se2([pt.get('price_cpu_gpu_us') for pt in per_pair]),
               fail_a=fail_a, fail_b=fail_b, all_rows=all_rows, rt_mismatch_lines=run['rt_lines'],
               tr_mismatch_lines=run['tr_lines'], nt_p=nt_p, emit_dev_us=[em_p, em_m], streams_bad=streams_bad[:20],
               skip_window=skip_window[:20], skip_total=len(run['skip_frames']), markers=run['markers'][:10],
               pins=run['pins'], census=[c.decode('utf-8', 'replace') for c in run['census']], vk_env=vk_env,
               report=report, blocks=len(blocks), prereg_sha256=prereg.get('sha256'), pred_now=list(pred_now),
               installed_sha256=installed_sha)
    return res


def fmt(x, digits=1):
    if x is None:
        return 'NA'
    if isinstance(x, bool):
        return str(x)
    return ('%.' + str(digits) + 'f') % x


def format_report(res):
    out = []
    if res['draft']:
        out.append('DRAFT (prereg, hold and the pair minimum are not checked; not a sealed verdict)')
    out.append('spc120 tag %s  scorer %s  build %s' % (res['tag'], res['scorer_sha256'][:16], res['build_sha256'][:16]))
    for k, v in res['checks'].items():
        out.append('  admission %-18s %s' % (k, 'skipped (draft)' if v is None else 'ok' if v else 'FAIL'))
    for group in ('common', 'a_controls', 'b_controls'):
        bad = [k for k, v in res[group].items() if not v]
        out.append('  %s: %s' % (group, 'ok' if not bad else 'FAIL ' + ' '.join(bad)))
    t = res['terms']
    out.append('  frames P %s M %s, pairs %d, blocks %d; zbar %s ns' % (t.get('nfp'), t.get('nfm'), len(res['pairs']),
                                                                       res['blocks'], fmt(res['zbar_ns'], 2)))
    out.append('  A: G_A %s  N_A %s  Z_A %s  D_A %s ns (unclamped)  r_A %s  T_A %s  N_A+ %s  G_A+ %s  N_A^g %s G_A^g %s'
               % tuple(fmt(t.get(k), d) for k, d in (('G_A', 1), ('N_A', 1), ('Z_A', 1), ('D_A_ns', 1), ('r_A', 4),
                                                     ('T_A', 1), ('N_A_up', 1), ('G_A_up', 1), ('N_A_g', 1),
                                                     ('G_A_g', 1))))
    out.append('  B: G_B %s  N_B %s  Z_B %s  D_B %s ns  D_B\' %s ns (unclamped)  r_B %s  T_B %s  N_B+ %s  G_B+ %s  '
               'N_B^g %s G_B^g %s'
               % tuple(fmt(t.get(k), d) for k, d in (('G_B', 1), ('N_B', 1), ('Z_B', 1), ('D_B_ns', 1),
                                                     ('D_Bp_ns', 1), ('r_B', 4), ('T_B', 1), ('N_B_up', 1),
                                                     ('G_B_up', 1), ('N_B_g', 1), ('G_B_g', 1))))
    out.append('  SP: N %s  Z %s  N+ %s (us a frame)' % (fmt(t.get('N')), fmt(t.get('Z')), fmt(t.get('N_up'))))
    for arm in (0, 1):
        r = res['report'][arm]
        out.append('  arm %s: frames %d dt_us %s cpu_gpu_us %s draws %s bda_scan %s (%s)'
                   % ('PM'[arm], r['frames'], fmt(r['dt_us']), fmt(r['cpu_gpu_us']), fmt(r['draws']),
                      fmt(r['bda_scan']), r['bda_regime']))
    out.append('  price P-M (report only): dt_us %s 2se %s  cpu_gpu_us %s 2se %s'
               % (fmt(t.get('price_dt_us')), fmt(res['se2_price_dt_us']), fmt(t.get('price_cpu_gpu_us')),
                  fmt(res['se2_price_cpu_gpu_us'])))
    out.append('  correctness (all rows): %s; SpRtMismatch lines %d, SpTrMismatch lines %d; sp_rt_nt over P rows %d'
               % (', '.join('%s=%d' % kv for kv in res['all_rows'].items()), res['rt_mismatch_lines'],
                  res['tr_mismatch_lines'], res['nt_p']))
    if res['verdict'] != 'ADMITTED':
        out.append('REPORT OF A NOT_ADMITTED RUN - NOT TO BE QUOTED')
    failed = [k for k, v in res['checks'].items() if v is False]
    out.append('VERDICT: %s%s' % (res['verdict'], ' (failed: %s)' % ' '.join(failed) if failed else ''))
    for name in ('A', 'B', 'SP'):
        m = res['members'][name]
        out.append('%s %s: %s point=%s upper=%s 2se=%s' % ('PACKAGE' if name == 'SP' else 'MEMBER', name,
                                                        m['verdict'], fmt(m['point']), fmt(m['upper']),
                                                        fmt(m['se2_upper'])))
    out.append('CONSEQUENCE: %s' % res['consequence'])
    for name in ('A', 'B'):
        out.append('CONSEQUENCE %s: %s' % (name, res['member_consequence'][name]))
    return out


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    tag = sys.argv[sys.argv.index('--tag') + 1] if '--tag' in sys.argv else TAG
    draft = '--draft' in sys.argv
    inst = sys.argv[sys.argv.index('--installed-sha') + 1] if '--installed-sha' in sys.argv else None
    if tag not in TAGS and not draft:
        print('unknown tag %s (expected one of %s; any tag only with --draft)' % (tag, ', '.join(TAGS)))
        return 2
    res = evaluate(root, tag, installed_sha=inst, draft=draft)
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass
    print(NL.join(format_report(res)))
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1, ensure_ascii=False)
                                                                .encode('utf-8'))
    return 0 if res['verdict'] == 'ADMITTED' else 1


if __name__ == '__main__':
    sys.exit(main())
