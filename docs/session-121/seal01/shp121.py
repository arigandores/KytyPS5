"""Session 121, ROADMAP s0.1 "СЕССИЯ 121 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1-4 (item 4: two seals; this is seal 02), design
C:/kyty/s121/design/design121.md (wins over the files below), texmemo8.md (sections 6, 8.3, 8.4: identities, fixtures
S1-S15, mutants) and texmemo8_review.md (RC1 identity tolerances, RC8 bands), C:/kyty/s121/impl_report.txt (the
counters AS BUILT: 31 tm8_*, the name tm8_ddiff, identity 11 as built, positive controls tautological).
Pre-registration pred/02_shp121.md; fixtures test_shp121.py; mutants mut_shp121.py; chain go121a.sh shp121.

shp121 scores the SHIP ABBA of the R1 prototype, knob texmemo8, on build BUILD_SHA: Sky Garden, 300-s hold, one
attempt, pinned (KYTY_GPU_CLOCK_PIN=1), KYTY_GPU_MARKERS=0, gates_base.txt, KYTY_GATE_SCHEDULE=SCHEDULE with
KYTY_GATE_SCHEDULE_ABBA=1:  arm P (0) = "texmemo8=1" (8-way memo, the timed shipping arm), arm M (1) = "texmemo8=0"
(today's direct memo, the SAME build).  The shp121r repeat only on NOT_ADMITTED.

Frames.  Block b starts at frame START + PERIOD*b (its GateArm line; blocks come from the GateArm lines, never from the
blk label); its frames are n = START + 1 + PERIOD*b + pos, pos 0..89.  WINDOW = positions KEEP[0]..KEEP[1]-1 (10..88).
A block is complete when every window frame has exactly one FrameTrace, -draw and -x line with every field read and
its main line carries arm = the block's arm and blk = b.  ESTIMATOR rows = window rows with draws > DRAWS_MIN.
Pairs = blocks (2k, 2k+1) of the ABBA sequence (P M | M P | ...), both complete, both with estimator rows.

Admission (every check must hold, else NOT_ADMITTED; --draft skips ONLY prereg, prereg_sha, hold and pairs):
  binary / installed_now  TAG.json binary_sha256 and the installed exe (from the home dir) are BUILD_SHA
  pinned                  env KYTY_GPU_CLOCK_PIN == '1' and exactly one `GpuClockPin:` line, mode 1
  env_exact / env_vk      the KYTY_* env is exactly ENV_EXPECT and the TAG.json schedule SCHEDULE; of VK_* only VK_ALLOWED
  hold / one_ok_attempt   hold_s == HOLD_S; exactly one attempt, outcome ok, hold_exit None
  prereg / prereg_sha     prereg path PRED_PATH; PRED_SHA / PRED_BYTES filled (None => refused), the file matches them
                          now and TAG.json prereg sha256 / bytes are PRED_SHA / PRED_BYTES
  gates_exact             gates_base.txt hashes to GATES_SHA and TAG.json gates is its whitespace-normalised text
  arm_asserts             texmemo2, texfastcheck, r1cen, r2cen, spcen absent-or-0 in the run's gate text and named by
                          no observed arm text
  gate_lines / arms       every `Gate:` / `GateArm:` line matches the ABBA schedule; arm texts EXACTLY ARM_TEXT
  no_marker               no hang/crash marker in the log or stdout_TAG.txt
  no_skip_window          no `AsyncPipelines: skipped draw` attributed to a window frame
  streams                 every main row of every block window has its -draw and -x rows with every field read (the
                          last main row of the log is exempt)
  pairs                   >= MIN_PAIRS pairs
  idle                    pre_run.gpu_util_median <= IDLE_GPU_MAX
  armed_fill              every complete P block: window sums tm8_fill > 0 and tm8_evict > 0 (the arming proof)
  m_zero                  every window row of every complete M block: every tm8_* = 0 (no leak of the 8-way memo;
                          the switch rows lie at block positions 0-2, outside the window)
  no_switch_in_window     tm8_inval = tm8_mode = 0 on every window row of every complete block
  verify_leak             over ALL rows: every mode->=2 counter except the four correctness ones = 0 (tm8_look = 0:
                          no per-lookup counting in the timed arms), and no `Tm8VerifyInjected:` / `Tm8RebindInjected:`
  x2_cenoff               over ALL rows: tm8_x2 = tm8_cenoff = 0

Correctness (over ALL FrameTrace-x lines, any frame, duplicates included; they cannot count at modes 0/1): tm8_bad =
tm8_vctl_bad = tm8_relive = tm8_rbbad = 0 and no `Tm8VerifyMismatch:` / `Tm8RebindMismatch:` line, else NO_SHIP
(correctness failed; whatever the admission).

Not evaluable (=> NOT_EVALUABLE):
  arming   on the window rows of the paired blocks, per frame: P tex_hits - M tex_hits >= ARM_MIN and P key misses -
           M key misses <= -ARM_MIN (key misses = texmemo_collide + texmemo_empty); reported beside the census's
           +-CENSUS_ARM.  The floor ARM_MIN = 300 replaces the +800 of review RC8 / texmemo8.md S4 (ROADMAP s121 item
           4a, recorded before seal 02).  Ceiling (RC8, kept, "a hard impossibility"): P tex_hits - M tex_hits <= the
           M arm's own key misses a frame on the same rows (M_key_miss), else arming_ceiling.  The key-miss band's far
           edge needs no check: P key misses >= 0 bounds the difference by -M_key_miss by construction.
  identities (texmemo8_review RC1, as built) on the window sums of every complete block: NEAR (counters printed next to
           each other) |residual| <= SKEW_NEAR; FAR <= max(SKEW_FAR_ABS, SKEW_FAR_PERMILLE per mille of the larger
           side); an 'eq' FAR identity must also hold on the run's window totals to SKEW_MEAN_PER10K per 10 000
  bda      the BDA regime (bda_scan) of the two arms differs
  2SE undefined (fewer than two pairs)

Estimator: per block, the mean of main-line dt_us over its estimator rows; Delta = mean over pairs of (P block mean - M
block mean); 2SE = 2 * stdev(per-pair differences) / sqrt(pairs).  The same for cpu_gpu_us (reported).  Game speed
per arm = GAME_FRAME_US / (mean of that arm's paired block means).
Verdict: NO_SHIP (correctness) > NOT_ADMITTED (NOT_EVALUABLE on the repeat tag) > NOT_EVALUABLE > SHIP iff Delta +
2SE < 0 (strict) AND the sealed vfy121 result is PASS (runs121/<vfy tag>.score.json: verdict PASS, not a draft, tag the
vfy tag, build BUILD_SHA, scorer_sha256 == VFY_SCORER_SHA, which is None until seal 02 => never PASS) > NO_SHIP.
The procedural half of "shp121 runs only after vfy121 PASSes" (ROADMAP s121 item 4) is the chain's: go121a.sh
shp121|shp121r refuses to start unless chk_vfy121.py finds VFY_SCORER_SHA filled, equal to sha256(vfy121.py), and the
sealed PASS file (runs121/vfy121.score.json PASS, or vfy121 NOT_ADMITTED and runs121/vfy121r.score.json PASS; not a
draft, this build, that scorer); it writes the passing tag to runs121/<shp tag>.vfytag - score with --vfy <that tag>.
Every ns counter is divided by NS_PER_US exactly once.

    python C:/kyty/s121/shp121.py [--root C:/kyty/s121] [--tag shp121|shp121r] [--vfy vfy121|vfy121r] [--draft]
                                  [--out <json>]
"""
import hashlib
import json
import math
import os
import re
import statistics
import sys
from pathlib import Path

ROOT = 'C:/kyty/s121'
TAG = 'shp121'
TAGS = ('shp121', 'shp121r')
VFY_TAG = 'vfy121'
VFY_TAGS = ('vfy121', 'vfy121r')
BUILD_SHA = '0bd21ec24e546fbbb9b923c148fb76b57f45389ac166a71bad7410a3add738c7'  # git 5e8e1d2
INSTALLED = os.path.expanduser('~') + '/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
GATES_FILE = 'C:/kyty/s121/gates_base.txt'
GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'
PRED_PATH = 'C:/kyty/s121/pred/02_shp121.md'
PRED_SHA = '3b951163346efa7e1fd6196fe36cb4013f16f4f18628dc86ce32bee116e4fbdc'  # pred/02_shp121.md, sealed (session 121 seal 02)
PRED_BYTES = 3996        # pred/02_shp121.md, sealed
VFY_SCORER_SHA = '43359b1457ad7d1ff990c7406f0e6bec64588229b0604d68ad9084ee96a482f8'  # vfy121.py, sealed at seal 01
HOLD_S = 300
PERIOD = 90
START = 1800
KEEP = (10, 89)
DRAWS_MIN = 3000
ABBA = (0, 1, 1, 0)
ARM_P = 0
ARM_M = 1
ARM_TEXT = ('texmemo8=1', 'texmemo8=0')
MIN_PAIRS = 30
IDLE_GPU_MAX = 10
ARM_MIN = 300.0          # arming: tex_hits up, key misses down, a frame (ROADMAP s121 item 4a; RC8 had +800)
CENSUS_ARM = 1190.0      # the census's prediction of both arming differences (texmemo8.md section 6), reported
PRED_US = -350.0         # pre-registered Delta dt_us [I]
PRED_LO = -500.0
PRED_HI = -250.0
GAME_FRAME_US = 16667.0  # game speed = 16 667 / mean dt_us
NS_PER_US = 1000.0
SKEW_NEAR = 8            # counts a block window (ROADMAP s120 item 6; review RC1 NEAR)
SKEW_FAR_ABS = 64        # review RC1 FAR: max(64, 1 per mille of the larger window sum)
SKEW_FAR_PERMILLE = 1
SKEW_MEAN_PER10K = 1     # review RC1: FAR identities hold on run totals to 0.1 per mille
BDA_NEW_MAX = 300
BDA_OLD_MIN = 600
NL = chr(10)
SCHEDULE = '90+1800:' + ARM_TEXT[0] + '|' + ARM_TEXT[1]
ENV_EXPECT = {
    'KYTY_FRAME_TRACE': 'lite',
    'KYTY_GPU_HANG_ABORT_S': '8',
    'KYTY_GATE_FILE': 'C:\\kyty\\s121\\gates.req',
    'KYTY_SAMPLE_GATE': 'C:\\kyty\\s121\\sample.req',
    'KYTY_QUEUE_TRACE': '1',
    'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden',
    'KYTY_GATE_SCHEDULE': SCHEDULE,
    'KYTY_GATE_SCHEDULE_ABBA': '1',
    'KYTY_GPU_CLOCK_PIN': '1',
    'KYTY_GPU_MARKERS': '0',
}
VK_ALLOWED = ('VK_SDK_PATH',)
BASE_ABSENT_OR_0 = ('texmemo2', 'texfastcheck', 'r1cen', 'r2cen', 'spcen')
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---')
SKIPPED_DRAW = b'AsyncPipelines: skipped draw'
TM8_MISMATCH = re.compile(rb'Tm8(?:Verify|Rebind)Mismatch:')
TM8_INJECTED = re.compile(rb'Tm8(?:Verify|Rebind)Injected:')
# the 31 counters as built, in print order (impl_report.txt, videoOut.cpp); the first nine count at any mode on rare
# paths, the rest only at modes 2/3 (never in this run)
TM8_RARE = ('tm8_fill', 'tm8_evict', 'tm8_evict_view', 'tm8_alias', 'tm8_inval', 'tm8_mode', 'tm8_renorm', 'tm8_x2',
            'tm8_cenoff')
TM8_VERIFY = ('tm8_look', 'tm8_hit', 'tm8_miss', 'tm8_stale', 'tm8_gain', 'tm8_vchk', 'tm8_bad', 'tm8_vctl',
              'tm8_vctl_bad', 'tm8_relive', 'tm8_inject', 'tm8_inject_miss', 'tm8_dlose', 'tm8_ddiff', 'tm8_dcc_chg',
              'tm8_rbchk', 'tm8_rbbad', 'tm8_rbinject', 'tm8_rbinject_miss', 'tm8_pb0_ns', 'tm8_pb_ns', 'tm8_pb_n')
TM8_KEYS = TM8_RARE + TM8_VERIFY
CORRECT_KEYS = ('tm8_bad', 'tm8_vctl_bad', 'tm8_relive', 'tm8_rbbad')
LEAK_KEYS = tuple(k for k in TM8_VERIFY if k not in CORRECT_KEYS)
ZERO_ALL_KEYS = ('tm8_x2', 'tm8_cenoff')
SWITCH_KEYS = ('tm8_inval', 'tm8_mode')
ARMED_KEYS = ('tm8_fill', 'tm8_evict')
P_INFO_KEYS = ('tm8_fill', 'tm8_evict', 'tm8_evict_view', 'tm8_alias', 'tm8_renorm')
KEY_MISS = ('texmemo_collide', 'texmemo_empty')
MAIN_FIELDS = ('dt_us', 'cpu_gpu_us', 'draws', 'arm', 'blk')
DRAW_FIELDS = ('tex_hits', 'b_texn', 'bda_scan')
X_FIELDS = ('texmemo_collide', 'texmemo_empty', 'texmemo_stale', 'texfast_ok', 'texfast_no', 'texfast_rec',
            'tnull_hit', 'tnull_miss') + TM8_KEYS
REPORT_DIFFS = ('texmemo_stale', 'texfast_ok', 'texfast_no', 'texfast_rec', 'b_texn')
KINDS = ((re.compile(rb'^FrameTrace: n=(\d+)'), 'main', MAIN_FIELDS),
         (re.compile(rb'^FrameTrace-draw: n=(\d+)'), 'draw', DRAW_FIELDS),
         (re.compile(rb'^FrameTrace-x: n=(\d+)'), 'x', X_FIELDS))
FIELD = re.compile(rb' (\w+)=(-?\d+)')
PIN = re.compile(rb'^GpuClockPin: mode (\d+)')
GATE = re.compile(rb'^Gate: (\w+)=(\d+) frame=(\d+)$')
GATE_ARM = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
# identities on the window sums of every complete block (both arms): name, left, right, class, relation
IDENTITIES = (
    ('b_texn=hits+keymiss+stale+null', ('b_texn',),
     ('tex_hits', 'texmemo_collide', 'texmemo_empty', 'texmemo_stale', 'tnull_hit', 'tnull_miss'), 'far', 'eq'),
    ('fill<=keymiss+stale+bad', ('tm8_fill',),
     ('texmemo_collide', 'texmemo_empty', 'texmemo_stale', 'tm8_bad', 'tm8_vctl_bad', 'tm8_relive'), 'far', 'le'),
    ('evict<=fill', ('tm8_evict',), ('tm8_fill',), 'near', 'le'),
    ('evict<=collide', ('tm8_evict',), ('texmemo_collide',), 'far', 'le'),
    ('evict_view<=evict', ('tm8_evict_view',), ('tm8_evict',), 'near', 'le'),
)
# ROADMAP s121 item 1 / design121 section 2 / texmemo8.md section 8.3, quoted; English gloss after the quote
CONSEQUENCE = {
    'SHIP': ('SHIP - "SHIP (умолчание `texmemo8` → 1) только если интервал 2SE Δ`dt_us` целиком ниже 0, проверка — 0 '
             'рассогласований, видео чистое" (ROADMAP s121 item 1): the default of texmemo8 becomes 1 in '
             'KNOB_DEFINITIONS; later harnesses pin texmemo8=1 in gates_base.txt in place.'),
    'NO_SHIP': ('NO_SHIP - "иначе трек закрыт своим измеренным числом" (ROADMAP s121 item 1): the R1 track closes '
                'with its measured Delta +- 2SE (Sky Garden, this build, pinned, against texmemo8=0 of the same build).'),
    'NOT_ADMITTED': ('NOT_ADMITTED - one repeat shp121r (texmemo8.md section 8.3: "NOT_ADMITTED => one rerun '
                     'shp121r, then NOT_EVALUABLE"): admission, not a verdict.'),
    'NOT_EVALUABLE': ('NOT_EVALUABLE - no Delta is quoted as the track\'s number; the run did not show the arming, '
                      'identities or regime the rule needs (or the repeat was not admitted either).'),
}
CORRECTNESS_NOTE = ('correctness counters fired (tm8_bad / tm8_vctl_bad / tm8_relive / tm8_rbbad or a *Mismatch '
                    'line) in a run whose arms are modes 0/1 - the prototype is not shipped.')


def arm_values(text):
    return dict(pair.split('=') for pair in text.split())


ARM_VALUES = tuple(arm_values(t) for t in ARM_TEXT)


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def is_marker(line):
    low = line.lower()
    return any(k in low for k in MARKERS)


def idle_ok(meta):
    v = (meta.get('pre_run') or {}).get('gpu_util_median')
    return isinstance(v, (int, float)) and v <= IDLE_GPU_MAX


def two_se(values):
    """2 x the standard error of the per-pair values; None below two pairs."""
    if len(values) < 2:
        return None
    return 2.0 * statistics.stdev(values) / math.sqrt(len(values))


def mean(values):
    return sum(values) / len(values) if values else None


def diff(a, b):
    return None if a is None or b is None else a - b


def regime(v):
    if v is None:
        return None
    if v <= BDA_NEW_MAX:
        return 'NEW'
    if v >= BDA_OLD_MIN:
        return 'OLD'
    return 'MIXED'


def first_values(text):
    """name -> value of a gate text; the FIRST assignment of a name wins (gates.cpp FindAssignment, s111 trap)."""
    out = {}
    for pair in (text or '').split():
        if '=' in pair:
            k, v = pair.split('=', 1)
            out.setdefault(k, v)
    return out


def arm_asserts(texts, gates_text):
    """ROADMAP s121 item 4: r1cen / r2cen / spcen (and texmemo2, texfastcheck) named by no arm text and absent-or-0 in
    the run's gate text; both arms observed."""
    g = first_values(gates_text)
    if not texts.get(ARM_P) or not texts.get(ARM_M):
        return False
    for name in BASE_ABSENT_OR_0:
        if g.get(name) not in (None, '0'):
            return False
        for arm in (ARM_P, ARM_M):
            if any(name in first_values(t) for t in texts[arm]):
                return False
    return True


def arms_ok(gate_arms):
    """Blocks from the GateArm lines: arms=2, period, abba=1, text EXACTLY ARM_TEXT[arm], frame START + PERIOD*block,
    arm = ABBA[block % 4], blocks consecutive from 0."""
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


def parse_log(path, stdout_path=None):
    """One streaming pass.  Rows by kind and frame (only the fields read; a row missing one is None); every tm8_*
    summed over EVERY FrameTrace-x line; mismatch / injected / marker / skipped-draw lines."""
    seen = {'main': {}, 'draw': {}, 'x': {}}
    dups = set()
    raw = {k: 0 for k in TM8_KEYS}
    pins, gate_arms, gate_lines, markers = [], [], [], []
    lines = {'tm8_mismatch': 0, 'tm8_injected': 0}
    skipped = []
    last_main = None
    with open(path, 'rb') as f:
        for line in f:
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
            if SKIPPED_DRAW in line:
                skipped.append(None if last_main is None else last_main + 1)
            if TM8_MISMATCH.search(line):
                lines['tm8_mismatch'] += 1
            if TM8_INJECTED.search(line):
                lines['tm8_injected'] += 1
            if line.startswith(b'GpuClockPin:'):
                mp = PIN.match(line)
                pins.append(int(mp.group(1)) if mp else -1)
            if line.startswith(b'GateArm:'):
                mg = GATE_ARM.match(line.rstrip(b'\r\n'))
                gate_arms.append(None if mg is None else tuple(int(x) for x in mg.groups()[:6])
                                 + (mg.group(7).decode('utf-8', 'replace').strip(),))
            if line.startswith(b'Gate: '):
                gate_lines.append(line.rstrip())
            if not line.startswith(b'FrameTrace'):
                continue
            for regex, kind, names in KINDS:
                m = regex.match(line)
                if m is None:
                    continue
                n = int(m.group(1))
                got = dict(FIELD.findall(line, m.end()))
                rec = {k: int(got[k.encode()]) for k in names if k.encode() in got}
                if kind == 'x':
                    for k in raw:
                        raw[k] += int(got.get(k.encode(), 0))
                if kind == 'main':
                    last_main = n
                if n in seen[kind]:
                    dups.add(n)
                seen[kind][n] = rec if len(rec) == len(names) else None
                break
    if stdout_path is not None and Path(stdout_path).is_file():
        for line in open(stdout_path, 'rb'):
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
    return dict(seen=seen, dups=dups, raw=raw, pins=pins, gate_arms=gate_arms, gate_lines=gate_lines,
                markers=markers, lines=lines, skipped=skipped, last_main=last_main)


def block_frames(b):
    return list(range(START + 1 + PERIOD * b, START + 1 + PERIOD * (b + 1)))


def select(parsed, blocks):
    """Complete blocks (every window frame complete, labels = the schedule) with their window rows (ident) and
    estimator rows (est); pairs (2k, 2k+1), both complete, both with estimator rows."""
    seen, dups = parsed['seen'], parsed['dups']

    def complete(n):
        return n not in dups and all(seen[k].get(n) is not None for k in seen)

    def row(n):
        return dict(seen['main'][n], **seen['draw'][n], **seen['x'][n])

    done = {}
    for b, arm in sorted(blocks.items()):
        frames = block_frames(b)[KEEP[0]:KEEP[1]]
        if all(complete(n) and seen['main'][n]['arm'] == arm and seen['main'][n]['blk'] == b for n in frames):
            win = [row(n) for n in frames]
            done[b] = dict(arm=arm, ident=win, est=[r for r in win if r['draws'] > DRAWS_MIN])
    top = max(blocks) + 1 if blocks else 0
    pairs = [(b, b + 1) for b in range(0, top, 2)
             if b in done and b + 1 in done and done[b]['est'] and done[b + 1]['est']]
    return done, pairs


def streams_ok(parsed, blocks):
    """Every main row inside a block window has its -draw and -x rows with every field read (the last main row of the
    log is exempt)."""
    seen, dups = parsed['seen'], parsed['dups']
    for b in blocks:
        for n in block_frames(b)[KEEP[0]:KEEP[1]]:
            if n not in seen['main'] or n == parsed['last_main']:
                continue
            if n in dups or any(seen[k].get(n) is None for k in seen):
                return False
    return True


def skip_in_window(frame, blocks):
    if frame is None or frame <= START:
        return False
    b, pos = (frame - START - 1) // PERIOD, (frame - START - 1) % PERIOD
    return b in blocks and KEEP[0] <= pos < KEEP[1]


def armed_fill_ok(done):
    p = [blk for blk in done.values() if blk['arm'] == ARM_P]
    return bool(p) and all(sum(r[k] for r in blk['ident']) > 0 for blk in p for k in ARMED_KEYS)


def m_zero_ok(done):
    return all(r[k] == 0 for blk in done.values() if blk['arm'] == ARM_M for r in blk['ident'] for k in TM8_KEYS)


def no_switch_ok(done):
    return all(r[k] == 0 for blk in done.values() for r in blk['ident'] for k in SWITCH_KEYS)


def within(res, lhs, rhs, cls):
    if cls == 'near':
        return abs(res) <= SKEW_NEAR
    return 1000 * abs(res) <= max(1000 * SKEW_FAR_ABS, SKEW_FAR_PERMILLE * max(abs(lhs), abs(rhs)))


def identity_failures(done):
    """Names of the identities / bounds that break on some block window, plus the FAR equalities on the run totals."""
    bad = []
    for name, left, right, cls, rel in IDENTITIES:
        tl = tr = 0
        for b, blk in sorted(done.items()):
            lhs = sum(r[k] for r in blk['ident'] for k in left)
            rhs = sum(r[k] for r in blk['ident'] for k in right)
            tl += lhs
            tr += rhs
            res = lhs - rhs
            if rel == 'le' and res <= 0:
                continue
            if not within(res, lhs, rhs, cls):
                bad.append('%s@%d' % (name, b))
        if rel == 'eq' and cls == 'far' and 10000 * abs(tl - tr) > SKEW_MEAN_PER10K * max(abs(tl), abs(tr)):
            bad.append('%s@total' % name)
    return bad


def vfy_check(path, want_sha, vfy_tag):
    """(ok, reason, summary) of the sealed verify result: verdict PASS, not a draft, tag vfy_tag, build BUILD_SHA,
    scorer_sha256 == want_sha (None => not sealed => never ok)."""
    if not Path(path).is_file():
        return False, 'vfy_missing', None
    try:
        v = json.loads(Path(path).read_text(encoding='utf-8'))
    except (ValueError, OSError, UnicodeDecodeError):
        return False, 'vfy_unreadable', None
    if not isinstance(v, dict):
        return False, 'vfy_unreadable', None
    summary = dict(verdict=v.get('verdict'), tag=v.get('tag'), draft=v.get('draft'),
                   scorer_sha256=v.get('scorer_sha256'), build_sha256=v.get('build_sha256'))
    if want_sha is None:
        return False, 'vfy_sha_unsealed', summary
    if v.get('scorer_sha256') != want_sha:
        return False, 'vfy_scorer_sha', summary
    if v.get('build_sha256') != BUILD_SHA:
        return False, 'vfy_build', summary
    if v.get('tag') != vfy_tag:
        return False, 'vfy_tag', summary
    if v.get('draft') is not False:
        return False, 'vfy_draft', summary
    if v.get('verdict') != 'PASS':
        return False, 'vfy_verdict', summary
    return True, 'PASS', summary


def pred_checks(meta, draft, pred_sha, pred_bytes, pred_path):
    """(prereg, prereg_sha): True in --draft; else the sealed constants must be filled and match the file now."""
    if draft:
        return True, True
    prereg = meta.get('prereg') or {}
    path_ok = str(prereg.get('path') or '').replace('\\', '/') == pred_path
    if not pred_sha or not pred_bytes or not Path(pred_path).is_file():
        return path_ok, False
    data = Path(pred_path).read_bytes()
    sha_ok = (hashlib.sha256(data).hexdigest() == pred_sha and len(data) == pred_bytes
              and prereg.get('sha256') == pred_sha and prereg.get('bytes') == pred_bytes)
    return path_ok, sha_ok


def arm_pairs(done, pairs, arm):
    return [b for pr in pairs for b in pr if done[b]['arm'] == arm]


def estimate(done, pairs, key):
    """Per pair: P block mean - M block mean of key over the estimator rows; mean, 2SE, per-arm means of block means."""
    diffs, pm, mm = [], [], []
    for pr in pairs:
        pb = [b for b in pr if done[b]['arm'] == ARM_P][0]
        mb = [b for b in pr if done[b]['arm'] == ARM_M][0]
        a = mean([r[key] for r in done[pb]['est']])
        c = mean([r[key] for r in done[mb]['est']])
        diffs.append(a - c)
        pm.append(a)
        mm.append(c)
    return dict(delta=mean(diffs), two_se=two_se(diffs), P=mean(pm), M=mean(mm), pair_diffs=diffs)


def window_mean(rows, keys):
    return mean([sum(r[k] for k in keys) for r in rows])


def speed(dt):
    return None if not dt else GAME_FRAME_US / dt


def evaluate(root=ROOT, tag=TAG, draft=False, installed_sha=None, min_pairs=None, pred_sha=None, pred_bytes=None,
             pred_path=None, gates_file=GATES_FILE, vfy_tag=VFY_TAG, vfy_sha=None):
    """Admission, correctness, evaluability, the estimator and the verdict.  installed_sha None = hash INSTALLED;
    pred_sha / pred_bytes / pred_path None = PRED_SHA / PRED_BYTES / PRED_PATH; vfy_sha None = VFY_SCORER_SHA;
    min_pairs None = MIN_PAIRS (skipped in --draft)."""
    min_pairs = MIN_PAIRS if min_pairs is None else min_pairs
    pred_sha = PRED_SHA if pred_sha is None else pred_sha
    pred_bytes = PRED_BYTES if pred_bytes is None else pred_bytes
    pred_path = PRED_PATH if pred_path is None else pred_path
    vfy_sha = VFY_SCORER_SHA if vfy_sha is None else vfy_sha
    res = dict(scorer_sha256=sha_file(__file__), build_sha256=BUILD_SHA, tag=tag, draft=draft)
    meta = json.loads((Path(root) / (tag + '.json')).read_text(encoding='utf-8'))
    env = meta.get('env') or {}
    kyty_env = {k: v for k, v in env.items() if k.startswith('KYTY_')}
    vk_env = sorted(k for k in env if k.startswith('VK_'))
    atts = meta.get('attempts') or []
    ok_att = [a for a in atts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]
    gates_text = ' '.join((meta.get('gates') or '').split())
    base_text = ' '.join(Path(gates_file).read_text(encoding='utf-8').split()) if Path(gates_file).is_file() else None
    parsed = parse_log(Path(root) / ('log_%s.txt' % tag), Path(root) / ('stdout_%s.txt' % tag))
    arms_fine, blocks = arms_ok(parsed['gate_arms'])
    done, pairs = select(parsed, blocks)
    if installed_sha is None:
        installed_sha = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    prereg_ok, prereg_sha_ok = pred_checks(meta, draft, pred_sha, pred_bytes, pred_path)
    skipped_in = [f for f in parsed['skipped'] if skip_in_window(f, blocks)]
    texts = {}
    for g in parsed['gate_arms']:
        if g is not None and g[0] in (ARM_P, ARM_M):
            texts.setdefault(g[0], []).append(g[6])
    raw = parsed['raw']
    checks = dict(
        binary=meta.get('binary_sha256') == BUILD_SHA,
        installed_now=installed_sha == BUILD_SHA,
        pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and parsed['pins'] == [1],
        env_exact=kyty_env == ENV_EXPECT and meta.get('schedule') == SCHEDULE,
        env_vk=all(k in VK_ALLOWED for k in vk_env),
        hold=draft or meta.get('hold_s') == HOLD_S,
        one_ok_attempt=len(atts) == 1 and len(ok_att) == 1,
        prereg=prereg_ok,
        prereg_sha=prereg_sha_ok,
        gates_exact=(Path(gates_file).is_file() and sha_file(gates_file) == GATES_SHA and gates_text == base_text),
        arm_asserts=arm_asserts(texts, gates_text),
        gate_lines=gate_lines_ok(parsed['gate_lines'], blocks),
        arms=arms_fine,
        no_marker=not parsed['markers'],
        no_skip_window=not skipped_in,
        streams=streams_ok(parsed, blocks),
        pairs=draft or len(pairs) >= min_pairs,
        idle=idle_ok(meta),
        armed_fill=armed_fill_ok(done),
        m_zero=m_zero_ok(done),
        no_switch_in_window=no_switch_ok(done),
        verify_leak=all(raw[k] == 0 for k in LEAK_KEYS) and parsed['lines']['tm8_injected'] == 0,
        x2_cenoff=all(raw[k] == 0 for k in ZERO_ALL_KEYS))
    admitted = all(checks.values())
    correct = all(raw[k] == 0 for k in CORRECT_KEYS) and parsed['lines']['tm8_mismatch'] == 0

    # ---- estimator (pairs), arming (window rows of the paired blocks), regime
    p_blocks = arm_pairs(done, pairs, ARM_P)
    m_blocks = arm_pairs(done, pairs, ARM_M)
    wp = [r for b in p_blocks for r in done[b]['ident']]
    wm = [r for b in m_blocks for r in done[b]['ident']]
    est_p = [r for b in p_blocks for r in done[b]['est']]
    est_m = [r for b in m_blocks for r in done[b]['est']]
    dt = estimate(done, pairs, 'dt_us')
    cpu = estimate(done, pairs, 'cpu_gpu_us')
    arming = dict(tex_hits=diff(window_mean(wp, ('tex_hits',)), window_mean(wm, ('tex_hits',))),
                  key_miss=diff(window_mean(wp, KEY_MISS), window_mean(wm, KEY_MISS)),
                  P_tex_hits=window_mean(wp, ('tex_hits',)), M_tex_hits=window_mean(wm, ('tex_hits',)),
                  P_key_miss=window_mean(wp, KEY_MISS), M_key_miss=window_mean(wm, KEY_MISS))
    info = {k: diff(window_mean(wp, (k,)), window_mean(wm, (k,))) for k in REPORT_DIFFS}
    p_tm8 = {k: window_mean(wp, (k,)) for k in P_INFO_KEYS}
    bda = dict(P=mean([r['bda_scan'] for r in est_p]), M=mean([r['bda_scan'] for r in est_m]))
    bda.update(P_regime=regime(bda['P']), M_regime=regime(bda['M']))
    ne = []
    if arming['tex_hits'] is None or arming['tex_hits'] < ARM_MIN:
        ne.append('arming_tex_hits')
    if arming['key_miss'] is None or arming['key_miss'] > -ARM_MIN:
        ne.append('arming_key_miss')
    if arming['tex_hits'] is not None and arming['M_key_miss'] is not None and arming['tex_hits'] > arming['M_key_miss']:
        ne.append('arming_ceiling')
    ne += identity_failures(done)
    if bda['P_regime'] is None or bda['P_regime'] != bda['M_regime']:
        ne.append('bda_regime')
    if dt['two_se'] is None:
        ne.append('two_se_undefined')
    vfy_path = Path(root) / 'runs121' / (vfy_tag + '.score.json')
    vfy_ok, vfy_reason, vfy_summary = vfy_check(vfy_path, vfy_sha, vfy_tag)
    upper = None if dt['delta'] is None or dt['two_se'] is None else dt['delta'] + dt['two_se']
    if not correct:
        verdict = 'NO_SHIP'
    elif not admitted:
        verdict = 'NOT_EVALUABLE' if tag == TAGS[1] else 'NOT_ADMITTED'
    elif ne:
        verdict = 'NOT_EVALUABLE'
    elif upper < 0 and vfy_ok:
        verdict = 'SHIP'
    else:
        verdict = 'NO_SHIP'
    speeds = dict(P=speed(dt['P']), M=speed(dt['M']))
    speeds['change_pp'] = None if None in (speeds['P'], speeds['M']) else 100.0 * (speeds['P'] - speeds['M'])
    speeds['change_rel_pct'] = None if not dt['P'] or dt['M'] is None else 100.0 * (dt['M'] / dt['P'] - 1.0)
    probe = dict(pb_us=raw['tm8_pb_ns'] / NS_PER_US, pb0_us=raw['tm8_pb0_ns'] / NS_PER_US, n=raw['tm8_pb_n'],
                 t_pb_ns=None if raw['tm8_pb_n'] == 0
                 else max(0.0, (raw['tm8_pb_ns'] - raw['tm8_pb0_ns']) / raw['tm8_pb_n']))
    res.update(checks=checks, admission='ADMITTED' if admitted else 'NOT_ADMITTED', admitted=admitted,
               correct=correct, not_evaluable=ne, verdict=verdict, blocks=len(blocks), complete_blocks=len(done),
               pairs=len(pairs), est_frames=dict(P=len(est_p), M=len(est_m)),
               window_frames=dict(P=len(wp), M=len(wm)), dt_us=dt, cpu_gpu_us=cpu, upper=upper, speed=speeds,
               arming=arming, report_diffs=info, p_tm8=p_tm8, bda_scan=bda, raw=raw, lines=parsed['lines'],
               probe=probe, vfy=dict(ok=vfy_ok, reason=vfy_reason, tag=vfy_tag, path=str(vfy_path),
                                     summary=vfy_summary),
               skipped_draws=len(parsed['skipped']), skipped_in_window=len(skipped_in),
               markers=parsed['markers'][:10], pins=parsed['pins'], vk_env=vk_env)
    return res


def fmt(x, digits=1):
    if x is None:
        return '-'
    return ('%.' + str(digits) + 'f') % x


def format_report(res):
    out = []
    if res['draft']:
        out.append('DRAFT: unsealed scoring (pre-registration, hold and pair minimum not checked) - not a verdict')
    out.append('shp121 tag %s  scorer %s  build %s' % (res['tag'], res['scorer_sha256'][:16], res['build_sha256'][:16]))
    for k, v in res['checks'].items():
        out.append('  %-20s %s' % (k, 'ok' if v else 'FAIL'))
    out.append('  blocks %d complete %d pairs %d; estimator frames P %d M %d; window frames P %d M %d'
               % (res['blocks'], res['complete_blocks'], res['pairs'], res['est_frames']['P'], res['est_frames']['M'],
                  res['window_frames']['P'], res['window_frames']['M']))
    dt, cpu, sp = res['dt_us'], res['cpu_gpu_us'], res['speed']
    out.append('Delta dt_us (P - M) %s +- %s us (2SE, %d pairs), upper %s; P %s M %s us'
               % (fmt(dt['delta']), fmt(dt['two_se']), res['pairs'], fmt(res['upper']), fmt(dt['P']), fmt(dt['M'])))
    out.append('prediction %s us (range %s .. %s) [I]' % (fmt(PRED_US), fmt(PRED_LO), fmt(PRED_HI)))
    out.append('game speed (16 667 / mean dt_us) P %s M %s: change %s pp (%s %%)'
               % (fmt(sp['P'], 4), fmt(sp['M'], 4), fmt(sp['change_pp'], 2), fmt(sp['change_rel_pct'], 2)))
    out.append('Delta cpu_gpu_us (P - M) %s +- %s us; P %s M %s us (report)'
               % (fmt(cpu['delta']), fmt(cpu['two_se']), fmt(cpu['P']), fmt(cpu['M'])))
    a = res['arming']
    out.append('arming a frame: tex_hits P - M %s (need >= +%s and <= the M key misses %s; census +%s), key misses P - '
               'M %s (need <= -%s; census -%s); P tex_hits %s M %s, P key misses %s M %s'
               % (fmt(a['tex_hits']), fmt(ARM_MIN, 0), fmt(a['M_key_miss']), fmt(CENSUS_ARM, 0), fmt(a['key_miss']),
                  fmt(ARM_MIN, 0), fmt(CENSUS_ARM, 0), fmt(a['P_tex_hits']), fmt(a['M_tex_hits']),
                  fmt(a['P_key_miss']), fmt(a['M_key_miss'])))
    out.append('report P - M a frame: ' + ', '.join('%s %s' % (k, fmt(v)) for k, v in res['report_diffs'].items()))
    out.append('P window a frame: ' + ', '.join('%s %s' % (k, fmt(v)) for k, v in res['p_tm8'].items()))
    out.append('correctness (all rows): %s; lines %s' % (
        ', '.join('%s=%d' % (k, res['raw'][k]) for k in CORRECT_KEYS),
        ', '.join('%s=%d' % kv for kv in res['lines'].items())))
    out.append('verify leak (all rows): %s' % ', '.join('%s=%d' % (k, res['raw'][k]) for k in LEAK_KEYS + ZERO_ALL_KEYS))
    pb = res['probe']
    out.append('probe timer (all rows): pb %s us, pb0 %s us, n %d, t_pb %s ns'
               % (fmt(pb['pb_us'], 3), fmt(pb['pb0_us'], 3), pb['n'], fmt(pb['t_pb_ns'], 2)))
    out.append('bda_scan P %s (%s) M %s (%s)' % (fmt(res['bda_scan']['P']), res['bda_scan']['P_regime'],
                                                 fmt(res['bda_scan']['M']), res['bda_scan']['M_regime']))
    v = res['vfy']
    out.append('vfy %s: %s (%s)' % (v['tag'], 'PASS' if v['ok'] else 'not PASS', v['reason']))
    out.append('not evaluable: %s' % (', '.join(res['not_evaluable']) or '-'))
    failed = [k for k, ok in res['checks'].items() if not ok]
    out.append('ADMISSION: %s%s' % (res['admission'], ' failed=' + ','.join(failed) if failed else ''))
    if not res['admitted']:
        out.append('REPORT OF A NOT_ADMITTED RUN - NOT TO BE QUOTED')
    out.append('VERDICT: %s Delta=%s 2se=%s upper=%s%s' % (res['verdict'], fmt(dt['delta']), fmt(dt['two_se']),
                                                          fmt(res['upper']), ' DRAFT' if res['draft'] else ''))
    tail = ''
    if not res['correct']:
        tail = ' ' + CORRECTNESS_NOTE
    elif res['verdict'] == 'NO_SHIP' and not v['ok']:
        tail = ' The verify result is not a sealed PASS (%s).' % v['reason']
    out.append('CONSEQUENCE: %s%s' % (CONSEQUENCE[res['verdict']], tail))
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    tag = sys.argv[sys.argv.index('--tag') + 1] if '--tag' in sys.argv else TAG
    vfy = sys.argv[sys.argv.index('--vfy') + 1] if '--vfy' in sys.argv else VFY_TAG
    draft = '--draft' in sys.argv
    if (tag not in TAGS or vfy not in VFY_TAGS) and not draft:
        print('unknown tag %s / vfy %s (expected %s / %s; any tag only with --draft)'
              % (tag, vfy, ', '.join(TAGS), ', '.join(VFY_TAGS)))
        return 2
    res = evaluate(root, tag, draft=draft, vfy_tag=vfy)
    print(NL.join(format_report(res)))
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] in ('SHIP', 'NO_SHIP') else 1


if __name__ == '__main__':
    sys.exit(main())
