"""Session 121, ROADMAP s0.1 "СЕССИЯ 121 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1-4 (item 4: seal 01 = this scorer, the verify
run's PASS rule sealed before the run; item 3: the code review's consequences), design docs/session-121/design121.md
(C:/kyty/s121/design/design121.md, which wins), texmemo8.md (sections 5, 6, 8.2) with the review texmemo8_review.md
RC1-RC8, and C:/kyty/s121/impl_report.txt (the 31 tm8_* counters AS BUILT).  Pre-registration pred/01_vfy121.md;
fixtures test_vfy121.py; mutants mut_vfy121.py; chain go121a.sh vfy121|vfy121r.

vfy121 scores the VERIFY run of knob texmemo8 (0 direct memo, 1 8-way memo, 2 verify, 3 verify + positive control):
Sky Garden, build BUILD_SHA, 240-s hold, one attempt, pinned (KYTY_GPU_CLOCK_PIN=1), KYTY_GPU_MARKERS=0, gates
gates_base.txt, video KYTY_REC = ROOT/rec_<tag>.mp4 (enter_scene --rec), schedule SCHEDULE WITHOUT ABBA: FOUR arms in
turn, arm = block % 4, arm i text ARM_TEXT[i], mode MODE_OF_ARM[i] (2, 1, 0, 3), every arm with texfastcheck=1.

Blocks come from the `GateArm:` lines only (never from the blk label; the label must agree).  Block b starts at frame
START + PERIOD*b; its rows are n = START + 1 + PERIOD*b + pos, pos 0..89.  A block is COMPLETE when all 90 rows carry
the three streams with every field read, no duplicate, and main-line arm/blk equal to the GateArm arm and b.  WINDOW =
positions KEEP[0]..KEEP[1]-1 (10..88) of a complete block; ESTIMATOR rows = window rows with draws > DRAWS_MIN.

Verdict: PASS / FAIL / NOT_ADMITTED (ROADMAP s121 item 4), in this order:
  1. HARD FAIL - a fact of the run, whatever its admission (a divergence was found):
       hard_zero      sum over ALL FrameTrace-x lines (any frame, duplicates included) of tm8_bad, tm8_vctl_bad,
                      tm8_relive, tm8_rbbad, texfast_bad is 0 each
       struct_zero    the same for tm8_inject_miss, tm8_rbinject_miss, tm8_dcc_chg (zeros BY CONSTRUCTION, item 3(в):
                      never evidence of a pass - but a nonzero one means the control or the build is not as reviewed)
       no_mismatch    no `Tm8VerifyMismatch:`, `Tm8RebindMismatch:` or `TexFastVerify: MISMATCH` line in the log
       verify_marker  no FATAL marker (MARKERS but not SLOW_MARKERS) printed while a mode-2/3 arm was in force
                      (item 3(б): the full resolution of the verify can EXIT where a mode-1 hit does not; such a marker
                      is a divergence found, i.e. FAIL).  A SLOW marker (`GpuWaitSlow:`, a single 2-s diagnostic
                      timeout after which the wait continues, masterSemaphore.cpp) is never fatal: anywhere it is
                      NOT_ADMITTED (no_marker); a real hang still becomes `GpuHangAbort:` + EXIT, which stay fatal.
                      The arm in force at a log marker is the arm of the last `GateArm:` line printed before it
                      (gates.cpp applies the arm's text right after printing that line); a log marker printed after the
                      `Event: quit` line (shutdown, after the hold) has no arm; a marker of stdout_TAG.txt whose text
                      begins a log marker's text is that log marker's twin (LOGF + printf print it twice) and is
                      skipped; any other stdout marker gets the arm of the LAST `GateArm:` line of the log (the run
                      ended under it); no `GateArm:` line before it (the schedule had not started) = no mode
       no_glitch      the video report (s51_vidglitch.py; parsed and naming rec_<tag>.mp4) shows 0 one-frame glitches
  2. NOT_ADMITTED - any admission check fails (--draft skips ONLY prereg):
       binary / installed_now   TAG.json binary_sha256 and the installed exe (from the home dir) are BUILD_SHA
       pinned                   env KYTY_GPU_CLOCK_PIN == '1' and exactly one `GpuClockPin:` line, mode 1
       env_exact / env_vk       KYTY_* env exactly env_expect(tag), meta schedule == SCHEDULE; of VK_* only VK_ALLOWED
       hold / one_ok_attempt    hold_s == HOLD_S; exactly one attempt, outcome ok, hold_exit None
       prereg                   prereg path PRED_PATH; PRED_SHA / PRED_BYTES filled (None = refused), the file matches
                                them now and TAG.json prereg sha256 / bytes are them
       gates_exact              gates_base.txt sha256 is GATES_SHA and TAG.json gates is its whitespace-normalised text
       base_names               the gate text pins BASE_PINS and names none of BASE_ABSENT; the arm texts name none
                                of them but texmemo8 (the scheduled knob)
       arm_asserts              the arm texts: texmemo8 = MODE_OF_ARM, texfastcheck=1, the four modes once each
       gate_lines / arms        every `Gate:` / `GateArm:` line matches the 4-arm schedule (arms=4, abba=0, period,
                                frame = START + PERIOD*b, arm = b % 4, text exact, blocks consecutive from 0)
       modes                    every mode has >= MIN_BLOCKS complete blocks with estimator rows
       no_marker                no marker printed while no arm or a mode-0/1 arm was in force (before the schedule,
                                mode-0/1 blocks, after `Event: quit`) and no SLOW marker anywhere
       no_skip_window           no `AsyncPipelines: skipped draw` attributed to a window row
       streams                  every window row up to the last main line has its three rows, every field, the right
                                labels, no duplicate (the last main line is exempt when its -draw/-x row is cut)
       fields_all_rows          every FrameTrace-x line of the run carries every all-row field (ALL_ROW)
       idle                     pre_run.gpu_util_median <= IDLE_GPU_MAX
       video                    rec_<tag>.mp4 exists; the report parses and names it; frames == index entries;
                                |frames - last main FrameTrace n| <= max(VID_TOL_ABS, VID_TOL_PERMILLE per mille)
  3. SOFT FAIL - the PASS evidence of an admitted run is missing (ROADMAP s121 item 4 conditions):
       config_zero    tm8_x2 = tm8_cenoff = 0 over ALL rows
       control_alive  mode-3 window rows: sum tm8_inject > 0 and sum tm8_rbinject > 0, and at least one
                      `Tm8VerifyInjected:` and one `Tm8RebindInjected:` line (item 3(а): this proves only that the
                      counter and log path fire - the power of tm8_bad / tm8_rbbad is the offline unit test)
       control_leak   tm8_inject + tm8_rbinject = 0 over the window rows of modes 0, 1, 2
       verify_alive   modes 2 and 3 each: sum tm8_vchk > 0 and sum tm8_gain > 0 over their window rows
       dark_01        modes 0 and 1: every per-lookup counter (PER_LOOKUP, tm8_look first) sums to 0 over their window
                      rows (the timed arms carry no per-lookup instrument, design section 6)
       m1_fill        every complete mode-1 block: sum tm8_fill over its window > 0 (the 8-way stores)
       m0_fill        sum tm8_fill over the mode-0 window rows = 0 (the direct memo has no ways)
       armed_hits     mean tex_hits (mode-1 estimator rows) - mean (mode 0) >= ARM_HITS_MIN
       armed_keys     mean key misses (texmemo_collide + texmemo_empty) mode 1 - mode 0 <= -ARM_KEYS_MIN
       identities     on the window sums of every complete mode-2/3 block (RC1; NEAR = counters Added by one
                      operation and printed next to each other in the tm8_* block: |res| <= SKEW_NEAR; FAR = printed far
                      apart or on another line: |res| <= max(SKEW_FAR_ABS, SKEW_FAR_PERMILLE per mille of the larger
                      side); a FAR bound fails only on an excess beyond that):
                        NEAR tm8_look = tm8_hit + tm8_miss + tm8_stale        NEAR tm8_vchk = tm8_gain
                        FAR  tex_hits = tm8_hit - tm8_bad - tm8_vctl_bad - tm8_relive     (identity 11 as built)
                        FAR  tm8_miss = texmemo_collide + texmemo_empty                  (identity 13)
                        FAR  tm8_fill <= collide + empty + stale + tm8_bad + tm8_vctl_bad + tm8_relive (identity 1)
       ratios         RC8 bands per mode-2/3 block window: tm8_vctl / (tm8_hit - tm8_gain) and tm8_pb_n / tm8_look in
                      RATIO_BAND (xorshift 1/64 samples)
  4. PASS.

Arming thresholds (mine, written before the run): the census cen120 predicts the 8-way memo gains W = 1 258.7 key
misses a frame less the 8-way's losses of ~66.6, i.e. tex_hits + ~1 190 and key misses - ~1 190 a frame (design121
s1.4; the M arm's own key misses, ~1 772 a frame, are the physical ceiling).  ARM_HITS_MIN = ARM_KEYS_MIN = 300 a frame
is ~25 % of the prediction: a knob that is not honoured (delta ~0, the scene's block-to-block drift of the interleaved
mode-0/1 means is far below 300 with ~16 blocks each) fails; any working 8-way passes with a wide margin.  The
verify gained-hit band [600, 2 000] of texmemo8.md 8.2, the ceiling and identity 19 of texmemo8.md s6
(0 < tm8_rbchk <= texfast_ok + texfast_no on every mode-2/3 block window) are REPORTED, not gated.
Every ns counter (tm8_pb*_ns) is divided by NS_PER_US exactly once (the probe cost in us a frame); ns per probe stays ns.

    python C:/kyty/s121/vfy121.py [--root C:/kyty/s121] [--tag vfy121|vfy121r] [--draft] [--out <json>]
                                  [--glitch-report <file>] [--installed-sha <sha>]
Without --glitch-report the scorer runs VIDGLITCH on ROOT/rec_<tag>.mp4 (slow: minutes) and keeps its output as
ROOT/<tag>_glitch.txt.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = 'C:/kyty/s121'
TAG = 'vfy121'
TAGS = ('vfy121', 'vfy121r')
BUILD_SHA = '0bd21ec24e546fbbb9b923c148fb76b57f45389ac166a71bad7410a3add738c7'  # git 5e8e1d2
INSTALLED = os.path.expanduser('~') + '/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
GATES_FILE = 'C:/kyty/s121/gates_base.txt'
GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'
PRED_PATH = 'C:/kyty/s121/pred/01_vfy121.md'
PRED_SHA = 'f681d4db7d55f522f74b943df49a4a5ef3d2f79eb53a1e321606e1f57e2466ea'  # pred/01_vfy121.md, sealed (session 121 seal 01)
PRED_BYTES = 5490        # pred/01_vfy121.md, sealed
VIDGLITCH = 'C:/kyty/scripts/s51_vidglitch.py'
HOLD_S = 240
PERIOD = 90
START = 1800
KEEP = (10, 89)
DRAWS_MIN = 3000
ARMS = 4
ARM_TEXT = ('texmemo8=2 texfastcheck=1',
            'texmemo8=1 texfastcheck=1',
            'texmemo8=0 texfastcheck=1',
            'texmemo8=3 texfastcheck=1')
MODE_OF_ARM = (2, 1, 0, 3)
MIN_BLOCKS = 8
IDLE_GPU_MAX = 10
SKEW_NEAR = 8
SKEW_FAR_ABS = 64
SKEW_FAR_PERMILLE = 1
RATIO_BAND = (1 / 80, 1 / 50)
ARM_HITS_MIN = 300.0
ARM_KEYS_MIN = 300.0
GAIN_BAND = (600.0, 2000.0)
VID_TOL_ABS = 120
VID_TOL_PERMILLE = 20
NS_PER_US = 1000.0
BDA_NEW_MAX = 300
BDA_OLD_MIN = 600
NL = chr(10)
SCHEDULE = '90+1800:' + '|'.join(ARM_TEXT)
VK_ALLOWED = ('VK_SDK_PATH',)
BASE_PINS = {'texmemo2': '0', 'texfastcheck': '0', 'fslean': '0', 'm4baton': '0', 'mutsite': '0',
             'shadowresolve': '0'}
BASE_ABSENT = ('texmemo8', 'r1cen', 'r2cen', 'spcen', 'bindwit', 'bindalt', 'blmove', 'bindfloor', 'cbmove',
               'slicecen', 'spine', 'bindlap', 'pathlap')
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---')
SLOW_MARKERS = (b'gpuwaitslow',)
QUIT = b'Event: quit'
SKIPPED_DRAW = b'AsyncPipelines: skipped draw'
LINE_KEYS = (('verify_mismatch', b'Tm8VerifyMismatch:'), ('rebind_mismatch', b'Tm8RebindMismatch:'),
             ('texfast_mismatch', b'TexFastVerify: MISMATCH'), ('verify_injected', b'Tm8VerifyInjected:'),
             ('rebind_injected', b'Tm8RebindInjected:'))
TM8 = ('tm8_fill', 'tm8_evict', 'tm8_evict_view', 'tm8_alias', 'tm8_inval', 'tm8_mode', 'tm8_renorm', 'tm8_x2',
       'tm8_cenoff', 'tm8_look', 'tm8_hit', 'tm8_miss', 'tm8_stale', 'tm8_gain', 'tm8_vchk', 'tm8_bad', 'tm8_vctl',
       'tm8_vctl_bad', 'tm8_relive', 'tm8_inject', 'tm8_inject_miss', 'tm8_dlose', 'tm8_ddiff', 'tm8_dcc_chg',
       'tm8_rbchk', 'tm8_rbbad', 'tm8_rbinject', 'tm8_rbinject_miss', 'tm8_pb0_ns', 'tm8_pb_ns', 'tm8_pb_n')
PER_LOOKUP = TM8[9:]
HARD_ZERO = ('tm8_bad', 'tm8_vctl_bad', 'tm8_relive', 'tm8_rbbad', 'texfast_bad')
STRUCT_ZERO = ('tm8_inject_miss', 'tm8_rbinject_miss', 'tm8_dcc_chg')
CONFIG_ZERO = ('tm8_x2', 'tm8_cenoff')
ALL_ROW = HARD_ZERO + STRUCT_ZERO + CONFIG_ZERO
MAIN_FIELDS = ('dt_us', 'cpu_gpu_us', 'draws', 'arm', 'blk')
DRAW_FIELDS = ('tex_hits', 'b_texn', 'bda_scan')
X_FIELDS = ('texmemo_collide', 'texmemo_empty', 'texmemo_stale', 'texfast_ok', 'texfast_no', 'texfast_rec',
            'texfast_bad', 'tnull_hit', 'tnull_miss') + TM8
REPORT_FIELDS = MAIN_FIELDS[:3] + DRAW_FIELDS + X_FIELDS
KINDS = ((re.compile(rb'^FrameTrace: n=(\d+)'), 'main', MAIN_FIELDS),
         (re.compile(rb'^FrameTrace-draw: n=(\d+)'), 'draw', DRAW_FIELDS),
         (re.compile(rb'^FrameTrace-x: n=(\d+)'), 'x', X_FIELDS))
FIELD = re.compile(rb' (\w+)=(-?\d+)')
PIN = re.compile(rb'^GpuClockPin: mode (\d+)')
GATE = re.compile(rb'^Gate: (\w+)=(\d+) frame=(\d+)$')
GATE_ARM = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
VID_HEAD = re.compile(r'(?m)^(.*): (\d+) frames (\d+)x(\d+), index entries (\d+)\s*$')
VID_COUNT = re.compile(r'(?m)^one-frame glitches: (\d+)\s*$')
VID_EVENT = re.compile(r'(?m)^  video +(\d+) present +(-?\d+) ')
# identities on the window sums of every complete mode-2/3 block: name, left keys, right (key, sign), class
IDENTITIES = (
    ('look=hit+miss+stale', ('tm8_look',), (('tm8_hit', 1), ('tm8_miss', 1), ('tm8_stale', 1)), 'near'),
    ('vchk=gain', ('tm8_vchk',), (('tm8_gain', 1),), 'near'),
    ('tex_hits=hit-bad-vctl_bad-relive', ('tex_hits',),
     (('tm8_hit', 1), ('tm8_bad', -1), ('tm8_vctl_bad', -1), ('tm8_relive', -1)), 'far'),
    ('miss=collide+empty', ('tm8_miss',), (('texmemo_collide', 1), ('texmemo_empty', 1)), 'far'),
    ('fill<=collide+empty+stale+bad+vctl_bad+relive', ('tm8_fill',),
     (('texmemo_collide', 1), ('texmemo_empty', 1), ('texmemo_stale', 1), ('tm8_bad', 1), ('tm8_vctl_bad', 1),
      ('tm8_relive', 1)), 'far_le'),
)
RATIOS = (('vctl/(hit-gain)', 'tm8_vctl', (('tm8_hit', 1), ('tm8_gain', -1))),
          ('pb_n/look', 'tm8_pb_n', (('tm8_look', 1),)))
CONSEQUENCE = {
    'PASS': ('PASS - печать 01 пройдена: 0 расхождений проверки, положительный контроль режима 3 жив, вооружение '
             'режима 1 против режима 0, видео без одно-кадровых глитчей (ROADMAP s121 item 4); seal 02 (shp121) may '
             'run.'),
    'FAIL': ('FAIL - "ПРОВАЛ ⇒ трек R1 закрыт до исправления, `shp121` не запускается" (ROADMAP s121 item 4).'),
    'NOT_ADMITTED': ('NOT_ADMITTED - admission, not a verdict: the repeat vfy121r runs only on NOT_ADMITTED '
                     '(go121a.sh); shp121 does not run before a PASS.'),
}
NOTE = ('NOTE (ROADMAP s121 item 3): tm8_inject / tm8_rbinject > 0 prove only that the counter and the log path fire '
        '(the control is tautological); the evidence that tm8_bad / tm8_rbbad can fire is the offline unit test (374 '
        'of 200 000 direct-layout entries look placed).  tm8_inject_miss, tm8_rbinject_miss, tm8_dcc_chg are zeros by '
        'construction, never evidence.  Mode 2/3 state diverges from mode 1 (FindImage before the hit tail): the '
        'evidence for mode 1 itself is its blocks under texfastcheck=1 with texfast_bad = 0 and the zero-leak checks.')
_UNSET = object()


def arm_values(text):
    return dict(pair.split('=', 1) for pair in text.split())


ARM_VALUES = tuple(arm_values(t) for t in ARM_TEXT)


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def env_expect(tag):
    return {'KYTY_FRAME_TRACE': 'lite',
            'KYTY_GPU_HANG_ABORT_S': '8',
            'KYTY_GATE_FILE': 'C:\\kyty\\s121\\gates.req',
            'KYTY_SAMPLE_GATE': 'C:\\kyty\\s121\\sample.req',
            'KYTY_QUEUE_TRACE': '1',
            'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden',
            'KYTY_REC': 'C:\\kyty\\s121\\rec_%s.mp4' % tag,
            'KYTY_GATE_SCHEDULE': SCHEDULE,
            'KYTY_GPU_CLOCK_PIN': '1',
            'KYTY_GPU_MARKERS': '0'}


def is_marker(line):
    low = line.lower()
    return any(k in low for k in MARKERS)


def is_slow(line):
    return any(k in line.lower() for k in SLOW_MARKERS)


def idle_ok(meta):
    v = (meta.get('pre_run') or {}).get('gpu_util_median')
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v <= IDLE_GPU_MAX


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


def arm_asserts(texts):
    """The arm texts themselves: texmemo8 of arm i is MODE_OF_ARM[i], texfastcheck=1 everywhere, the four modes once
    each, exactly ARMS texts."""
    if len(texts) != ARMS or len(MODE_OF_ARM) != ARMS or sorted(MODE_OF_ARM) != [0, 1, 2, 3]:
        return False
    for i, text in enumerate(texts):
        v = first_values(text)
        if v.get('texmemo8') != str(MODE_OF_ARM[i]) or v.get('texfastcheck') != '1':
            return False
    return True


def base_names_ok(gates_text, texts):
    g = first_values(gates_text)
    if any(g.get(k) != v for k, v in BASE_PINS.items()) or any(k in g for k in BASE_ABSENT):
        return False
    # the arm texts own texmemo8 (the scheduled knob); every other absent name stays absent there too
    return not any(k in first_values(t) for t in texts for k in BASE_ABSENT if k != 'texmemo8')


def arms_ok(gate_arms):
    blocks = {}
    for g in gate_arms:
        if g is None:
            return False, {}
        arm, arms, block, frame, period, abba, text = g
        if arms != ARMS or period != PERIOD or abba != 0 or arm >= ARMS or text != ARM_TEXT[arm]:
            return False, {}
        if frame != START + PERIOD * block or block % ARMS != arm or block in blocks:
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
        if name not in ARM_VALUES[0] or frame < START or (frame - START) % PERIOD != 0:
            return False
        block = (frame - START) // PERIOD
        if block not in blocks or m.group(2).decode() != ARM_VALUES[blocks[block]][name]:
            return False
    return True


def read_run(path, stdout_path=None):
    """One streaming pass over the log: rows by kind and frame (only the fields read; a row missing one is None), the
    all-row sums over EVERY FrameTrace-x line, the diagnostic lines, markers with the arm in force when printed."""
    seen = {'main': {}, 'draw': {}, 'x': {}}
    dups = set()
    all_rows = {k: 0 for k in ALL_ROW}
    x_lines = 0
    x_missing = 0
    lines = {k: 0 for k, _ in LINE_KEYS}
    pins, gate_arms, gate_lines, markers, skipped = [], [], [], [], []
    last_main = None
    arm_now = None
    quit_seen = False
    with open(path, 'rb') as f:
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
                        x_lines += 1
                        x_missing += int(any(k.encode() not in got for k in ALL_ROW))
                        for k in ALL_ROW:
                            all_rows[k] += int(got.get(k.encode(), 0))
                    if kind == 'main':
                        last_main = n
                    if n in seen[kind]:
                        dups.add(n)
                    seen[kind][n] = rec if len(rec) == len(names) else None
                    break
                continue
            if line.startswith(QUIT):
                quit_seen = True
            if is_marker(line):
                markers.append((None if quit_seen else arm_now, 'log', line[:200].decode('utf-8', 'replace').strip(),
                                is_slow(line)))
            if SKIPPED_DRAW in line:
                skipped.append(None if last_main is None else last_main + 1)
            for key, text in LINE_KEYS:
                if text in line:
                    lines[key] += 1
            if line.startswith(b'GpuClockPin:'):
                mp = PIN.match(line)
                pins.append(int(mp.group(1)) if mp else -1)
            if line.startswith(b'GateArm:'):
                mg = GATE_ARM.match(line.rstrip(b'\r\n'))
                gate_arms.append(None if mg is None else tuple(int(x) for x in mg.groups()[:6])
                                 + (mg.group(7).decode('utf-8', 'replace').strip(),))
                arm_now = None if mg is None else int(mg.group(1))
            if line.startswith(b'Gate: '):
                gate_lines.append(line.rstrip())
    log_texts = [m[2] for m in markers]
    if stdout_path is not None and Path(stdout_path).is_file():
        for line in open(stdout_path, 'rb'):
            if is_marker(line):
                text = line[:200].decode('utf-8', 'replace').strip()
                if any(t.startswith(text) for t in log_texts):
                    continue  # the printf twin of a LOGF marker: the log copy carries the arm
                markers.append((arm_now, 'stdout', text, is_slow(line)))
    return dict(seen=seen, dups=dups, all_rows=all_rows, x_lines=x_lines, x_missing=x_missing, lines=lines,
                pins=pins, gate_arms=gate_arms, gate_lines=gate_lines, markers=markers, skipped=skipped,
                last_main=last_main)


def block_frames(b):
    return list(range(START + 1 + PERIOD * b, START + 1 + PERIOD * (b + 1)))


def block_of(frame):
    if frame is None or frame <= START:
        return None
    return (frame - START - 1) // PERIOD


def mode_of_arm(arm):
    return MODE_OF_ARM[arm] if arm is not None and 0 <= arm < ARMS else None


def select(parsed, blocks):
    """Complete blocks (all PERIOD rows, three streams, every field, labels = the GateArm arm and block, no duplicate):
    their window rows and estimator rows."""
    seen, dups = parsed['seen'], parsed['dups']

    def complete(n, arm, b):
        return (n not in dups and all(seen[k].get(n) is not None for k in seen)
                and seen['main'][n]['arm'] == arm and seen['main'][n]['blk'] == b)

    done = {}
    for b, arm in sorted(blocks.items()):
        frames = block_frames(b)
        if all(complete(n, arm, b) for n in frames):
            win = [dict(seen['main'][n], **seen['draw'][n], **seen['x'][n]) for n in frames[KEEP[0]:KEEP[1]]]
            done[b] = dict(arm=arm, mode=MODE_OF_ARM[arm], win=win, est=[r for r in win if r['draws'] > DRAWS_MIN])
    return done


def streams_ok(parsed, blocks):
    """Every window row up to the last main line: three rows, every field, the right labels, no duplicate; the last main
    line itself is exempt when its -draw/-x row is missing or cut (the run ended there)."""
    seen, dups, last = parsed['seen'], parsed['dups'], parsed['last_main']
    if last is None:
        return not blocks
    for b, arm in blocks.items():
        for n in block_frames(b)[KEEP[0]:KEEP[1]]:
            if n > last:
                break
            if n == last and (seen['draw'].get(n) is None or seen['x'].get(n) is None):
                continue
            main = seen['main'].get(n)
            if n in dups or main is None or seen['draw'].get(n) is None or seen['x'].get(n) is None:
                return False
            if main['arm'] != arm or main['blk'] != b:
                return False
    return True


def ksum(rows, keys):
    return {k: sum(r[k] for r in rows) for k in keys}


def side(s, left, right):
    lhs = sum(s[k] for k in left)
    rhs = sum(sign * s[k] for k, sign in right)
    return lhs, rhs


def within_far(res, lhs, rhs):
    return 1000 * abs(res) <= max(1000 * SKEW_FAR_ABS, SKEW_FAR_PERMILLE * max(abs(lhs), abs(rhs)))


def identity_failures(done):
    """Names of the identities that break on the window sums of a complete mode-2/3 block, and every residual."""
    bad, residuals = [], {}
    keys = sorted({k for _, left, right, _ in IDENTITIES for k in left + tuple(k for k, _ in right)})
    for b, blk in sorted(done.items()):
        if blk['mode'] not in (2, 3):
            continue
        s = ksum(blk['win'], keys)
        for name, left, right, cls in IDENTITIES:
            lhs, rhs = side(s, left, right)
            res = lhs - rhs
            residuals.setdefault(name, []).append(res)
            if cls == 'near':
                fine = abs(res) <= SKEW_NEAR
            elif cls == 'far':
                fine = within_far(res, lhs, rhs)
            else:
                fine = res <= 0 or within_far(res, lhs, rhs)
            if not fine:
                bad.append('%s@%d' % (name, b))
    return bad, residuals


def ratio_failures(done):
    bad, values = [], {}
    for b, blk in sorted(done.items()):
        if blk['mode'] not in (2, 3):
            continue
        s = ksum(blk['win'], TM8)
        for name, num, den in RATIOS:
            d = sum(sign * s[k] for k, sign in den)
            v = None if d <= 0 else s[num] / d
            values.setdefault(name, []).append(v)
            if v is None or v < RATIO_BAND[0] or v > RATIO_BAND[1]:
                bad.append('%s@%d' % (name, b))
    return bad, values


def rbchk_bound(done):
    """Identity 19 of texmemo8.md s6, REPORTED only: block -> 0 < tm8_rbchk <= texfast_ok + texfast_no on the window
    sums of every complete mode-2/3 block."""
    out = {}
    for b, blk in sorted(done.items()):
        if blk['mode'] in (2, 3):
            s = ksum(blk['win'], ('tm8_rbchk', 'texfast_ok', 'texfast_no'))
            out[b] = 0 < s['tm8_rbchk'] <= s['texfast_ok'] + s['texfast_no']
    return out


def mode_rows(done, mode, kind):
    return [r for b, blk in sorted(done.items()) if blk['mode'] == mode for r in blk[kind]]


def mode_report(done, mode):
    est = mode_rows(done, mode, 'est')
    out = {k: (sum(r[k] for r in est) / len(est) if est else None) for k in REPORT_FIELDS}
    out['frames'] = len(est)
    out['blocks'] = sum(1 for blk in done.values() if blk['mode'] == mode and blk['est'])
    out['key_miss'] = (None if not est else sum(r['texmemo_collide'] + r['texmemo_empty'] for r in est) / len(est))
    pn = sum(r['tm8_pb_n'] for r in est)
    t_pb = None if pn == 0 else max(0.0, (sum(r['tm8_pb_ns'] for r in est) - sum(r['tm8_pb0_ns'] for r in est)) / pn)
    out['t_pb_ns'] = t_pb
    out['probe_us_frame'] = (None if t_pb is None or out['tm8_look'] is None
                             else t_pb * out['tm8_look'] / NS_PER_US)
    out['bda_regime'] = regime(out['bda_scan'])
    return out


def run_glitch(root, tag, video, script):
    """Run the glitch scan on the video; keep its output as ROOT/<tag>_glitch.txt; return that path."""
    out_dir = Path(root) / ('vidframes_%s' % tag)
    done = subprocess.run([sys.executable, script, str(video), '4', '12', str(out_dir)], capture_output=True)
    text = done.stdout.decode('utf-8', 'replace') + done.stderr.decode('utf-8', 'replace')
    path = Path(root) / ('%s_glitch.txt' % tag)
    path.write_bytes(text.encode('utf-8'))
    return path


def video_check(root, tag, report_path, script, last_main):
    video = Path(root) / ('rec_%s.mp4' % tag)
    out = dict(video=str(video).replace('\\', '/'), exists=video.is_file(), report=None, parsed=False, names=False,
               frames=None, index=None, glitches=None, events=[], presents=last_main, tol=None, count_ok=False,
               index_ok=False)
    if report_path is None and out['exists']:
        report_path = run_glitch(root, tag, video, script)
    if report_path is None or not Path(report_path).is_file():
        return out
    out['report'] = str(report_path).replace('\\', '/')
    text = Path(report_path).read_text(encoding='utf-8', errors='replace')
    mh = VID_HEAD.search(text)
    mc = VID_COUNT.search(text)
    if mh is None or mc is None:
        return out
    events = [(int(a), int(b)) for a, b in VID_EVENT.findall(text)]
    out.update(parsed=len(events) == int(mc.group(1)), frames=int(mh.group(2)), index=int(mh.group(5)),
               glitches=int(mc.group(1)), events=events[:40],
               names=mh.group(1).replace('\\', '/').split('/')[-1] == 'rec_%s.mp4' % tag)
    out['index_ok'] = out['frames'] == out['index']
    if last_main is not None:
        out['tol'] = max(VID_TOL_ABS, VID_TOL_PERMILLE * last_main / 1000)
        out['count_ok'] = abs(out['frames'] - last_main) <= out['tol']
    return out


def evaluate(root=ROOT, tag=TAG, draft=False, installed_sha=None, pred_want=_UNSET, pred_path=PRED_PATH,
             gates_file=GATES_FILE, min_blocks=None, glitch_report=None, glitch_script=VIDGLITCH):
    """The verdict and every number.  installed_sha None = hash INSTALLED; pred_want (sha, bytes) default (PRED_SHA,
    PRED_BYTES); min_blocks default MIN_BLOCKS; glitch_report None = run glitch_script on ROOT/rec_<tag>.mp4."""
    min_blocks = MIN_BLOCKS if min_blocks is None else min_blocks
    want_sha, want_bytes = (PRED_SHA, PRED_BYTES) if pred_want is _UNSET else pred_want
    res = dict(scorer_sha256=sha_file(__file__), build_sha256=BUILD_SHA, tag=tag, draft=bool(draft))
    meta = json.loads((Path(root) / (tag + '.json')).read_text(encoding='utf-8'))
    env = meta.get('env') or {}
    kyty_env = {k: v for k, v in env.items() if k.startswith('KYTY_')}
    vk_env = sorted(k for k in env if k.startswith('VK_'))
    atts = meta.get('attempts') or []
    ok_att = [a for a in atts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]
    gates_text = ' '.join((meta.get('gates') or '').split())
    gf = Path(gates_file)
    base_text = ' '.join(gf.read_text(encoding='utf-8').split()) if gf.is_file() else None
    parsed = read_run(Path(root) / ('log_%s.txt' % tag), Path(root) / ('stdout_%s.txt' % tag))
    arms_fine, blocks = arms_ok(parsed['gate_arms'])
    done = select(parsed, blocks)
    last_main = parsed['last_main']
    if installed_sha is None:
        installed_sha = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    prereg = meta.get('prereg') or {}
    if draft:
        prereg_ok = None
    else:
        pp = Path(pred_path)
        now = (sha_file(pp), pp.stat().st_size) if pp.is_file() else (None, None)
        prereg_ok = (want_sha is not None and want_bytes is not None
                     and str(prereg.get('path') or '').replace('\\', '/') == pred_path
                     and prereg.get('sha256') == want_sha and prereg.get('bytes') == want_bytes
                     and now[0] == want_sha and now[1] == want_bytes)
    # markers: the arm in force when printed (log: the last GateArm line before it, none after `Event: quit`; stdout:
    # the last of the log, twins skipped); only a FATAL (not slow) marker under a mode-2/3 arm is a verify FAIL
    markers = [(arm, src, text, mode_of_arm(arm), slow) for arm, src, text, slow in parsed['markers']]
    verify_markers = [m for m in markers if m[3] in (2, 3) and not m[4]]
    other_markers = [m for m in markers if not (m[3] in (2, 3) and not m[4])]
    skipped_in = [f for f in parsed['skipped'] if f is not None and block_of(f) in blocks
                  and KEEP[0] <= (f - START - 1) % PERIOD < KEEP[1]]
    per_mode_blocks = {m: sum(1 for blk in done.values() if blk['mode'] == m and blk['est']) for m in range(4)}
    video = video_check(root, tag, glitch_report, glitch_script, last_main)
    checks = dict(
        binary=meta.get('binary_sha256') == BUILD_SHA,
        installed_now=installed_sha == BUILD_SHA,
        pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and parsed['pins'] == [1],
        env_exact=kyty_env == env_expect(tag) and meta.get('schedule') == SCHEDULE,
        env_vk=all(k in VK_ALLOWED for k in vk_env),
        hold=meta.get('hold_s') == HOLD_S,
        one_ok_attempt=len(atts) == 1 and len(ok_att) == 1,
        prereg=prereg_ok,
        gates_exact=gf.is_file() and sha_file(gf) == GATES_SHA and gates_text == base_text,
        base_names=base_names_ok(gates_text, ARM_TEXT),
        arm_asserts=arm_asserts(ARM_TEXT),
        gate_lines=gate_lines_ok(parsed['gate_lines'], blocks),
        arms=arms_fine,
        modes=all(per_mode_blocks[m] >= min_blocks for m in range(4)),
        no_marker=not other_markers,
        no_skip_window=not skipped_in,
        streams=streams_ok(parsed, blocks),
        fields_all_rows=parsed['x_lines'] > 0 and parsed['x_missing'] == 0,
        idle=idle_ok(meta),
        video=(video['exists'] and video['parsed'] and video['names'] and video['index_ok'] and video['count_ok']))
    admitted = all(v is not False for v in checks.values())

    ar = parsed['all_rows']
    hard = dict(
        hard_zero=all(ar[k] == 0 for k in HARD_ZERO),
        struct_zero=all(ar[k] == 0 for k in STRUCT_ZERO),
        no_mismatch=(parsed['lines']['verify_mismatch'] == 0 and parsed['lines']['rebind_mismatch'] == 0
                     and parsed['lines']['texfast_mismatch'] == 0),
        verify_marker=not verify_markers,
        no_glitch=not (video['parsed'] and video['names'] and video['glitches'] > 0))

    def wsum(modes, keys):
        return sum(r[k] for m in modes for r in mode_rows(done, m, 'win') for k in keys)

    reports = {m: mode_report(done, m) for m in range(4)}
    d_hits = (None if reports[1]['tex_hits'] is None or reports[0]['tex_hits'] is None
              else reports[1]['tex_hits'] - reports[0]['tex_hits'])
    d_keys = (None if reports[1]['key_miss'] is None or reports[0]['key_miss'] is None
              else reports[1]['key_miss'] - reports[0]['key_miss'])
    id_bad, residuals = identity_failures(done)
    ratio_bad, ratios = ratio_failures(done)
    m1_blocks = [blk for b, blk in sorted(done.items()) if blk['mode'] == 1]
    soft = dict(
        config_zero=all(ar[k] == 0 for k in CONFIG_ZERO),
        control_alive=(wsum((3,), ('tm8_inject',)) > 0 and wsum((3,), ('tm8_rbinject',)) > 0
                       and parsed['lines']['verify_injected'] > 0 and parsed['lines']['rebind_injected'] > 0),
        control_leak=wsum((0, 1, 2), ('tm8_inject', 'tm8_rbinject')) == 0,
        verify_alive=all(wsum((m,), ('tm8_vchk',)) > 0 and wsum((m,), ('tm8_gain',)) > 0 for m in (2, 3)),
        dark_01=all(wsum((0, 1), (k,)) == 0 for k in PER_LOOKUP),
        m1_fill=bool(m1_blocks) and all(sum(r['tm8_fill'] for r in blk['win']) > 0 for blk in m1_blocks),
        m0_fill=wsum((0,), ('tm8_fill',)) == 0,
        armed_hits=d_hits is not None and d_hits >= ARM_HITS_MIN,
        armed_keys=d_keys is not None and d_keys <= -ARM_KEYS_MIN,
        identities=not id_bad,
        ratios=not ratio_bad)
    hard_bad = [k for k, v in hard.items() if not v]
    soft_bad = [k for k, v in soft.items() if not v]
    na_bad = [k for k, v in checks.items() if v is False]
    if hard_bad:
        verdict = 'FAIL'
    elif not admitted:
        verdict = 'NOT_ADMITTED'
    elif soft_bad:
        verdict = 'FAIL'
    else:
        verdict = 'PASS'
    gains = {m: reports[m]['tm8_gain'] for m in (2, 3)}
    res.update(verdict=verdict, admitted=admitted, checks=checks, hard=hard, soft=soft, hard_bad=hard_bad,
               soft_bad=soft_bad, failed=na_bad, blocks=len(blocks), complete_blocks=len(done),
               per_mode_blocks=per_mode_blocks, all_rows=ar, x_lines=parsed['x_lines'],
               x_missing=parsed['x_missing'], lines=parsed['lines'], pins=parsed['pins'],
               markers=[list(m) for m in markers[:20]], verify_markers=len(verify_markers),
               other_markers=len(other_markers), skipped_draws=len(parsed['skipped']),
               skipped_in_window=len(skipped_in), last_main=last_main, video=video, reports=reports,
               d_tex_hits=d_hits, d_key_miss=d_keys, key_ceiling=reports[0]['key_miss'],
               identity_failures=id_bad[:40], identity_residuals={k: v for k, v in residuals.items()},
               ratio_failures=ratio_bad[:40], ratio_values=ratios,
               gain_band={m: (None if g is None else GAIN_BAND[0] <= g <= GAIN_BAND[1]) for m, g in gains.items()},
               rbchk_bound=rbchk_bound(done),
               vk_env=vk_env, installed_sha256=installed_sha, prereg_sha256=prereg.get('sha256'))
    return res


def fmt(x, digits=1):
    if x is None:
        return '-'
    if isinstance(x, bool):
        return str(x)
    return ('%.' + str(digits) + 'f') % x


def format_report(res):
    out = []
    if res['draft']:
        out.append('DRAFT: the pre-registration is not checked - not a sealed verdict')
    out.append('vfy121 tag %s  scorer %s  build %s' % (res['tag'], res['scorer_sha256'][:16], res['build_sha256'][:16]))
    for k, v in res['checks'].items():
        out.append('  admission %-16s %s' % (k, 'skipped (draft)' if v is None else 'ok' if v else 'FAIL'))
    for k, v in res['hard'].items():
        out.append('  hard      %-16s %s' % (k, 'ok' if v else 'FAIL'))
    for k, v in res['soft'].items():
        out.append('  evidence  %-16s %s' % (k, 'ok' if v else 'FAIL'))
    out.append('  blocks %d complete %d; per mode (complete, with estimator rows) %s; last main n %s'
               % (res['blocks'], res['complete_blocks'],
                  ' '.join('m%d=%d' % kv for kv in sorted(res['per_mode_blocks'].items())), res['last_main']))
    out.append('  correctness (all %d -x rows, %d lacking a field): %s' % (
        res['x_lines'], res['x_missing'], ', '.join('%s=%d' % kv for kv in res['all_rows'].items())))
    out.append('  lines: %s' % ', '.join('%s=%d' % kv for kv in res['lines'].items()))
    out.append('  markers: %d in mode-2/3 blocks, %d elsewhere; skipped draws %d (%d in a window)'
               % (res['verify_markers'], res['other_markers'], res['skipped_draws'], res['skipped_in_window']))
    for arm, src, text, mode, slow in res['markers'][:5]:
        out.append('    marker under arm %s (%s, mode %s, %s): %s' % (arm, src, mode, 'slow' if slow else 'fatal',
                                                                     text[:120]))
    v = res['video']
    out.append('  video %s: exists %s, report %s, frames %s, index entries %s, presents (last main n) %s, tol %s, '
               'one-frame glitches %s' % (v['video'], v['exists'], v['report'] or '-', v['frames'], v['index'],
                                          v['presents'], fmt(v['tol']), v['glitches']))
    for vid, present in v['events'][:12]:
        out.append('    glitch video %d present %d' % (vid, present))
    for arm, mode in enumerate(MODE_OF_ARM):
        r = res['reports'][mode]
        out.append('  mode %d (arm %d, %s): blocks %d, estimator frames %d; means a frame: dt_us %s cpu_gpu_us %s '
                   'draws %s tex_hits %s b_texn %s key_miss %s (collide %s empty %s) stale %s bda_scan %s (%s)'
                   % (mode, arm, ARM_TEXT[arm], r['blocks'], r['frames'], fmt(r['dt_us']), fmt(r['cpu_gpu_us']),
                      fmt(r['draws']), fmt(r['tex_hits']), fmt(r['b_texn']), fmt(r['key_miss']),
                      fmt(r['texmemo_collide']), fmt(r['texmemo_empty']), fmt(r['texmemo_stale']),
                      fmt(r['bda_scan']), r['bda_regime']))
        out.append('    texfast ok %s no %s rec %s bad %s' % (fmt(r['texfast_ok']), fmt(r['texfast_no']),
                                                            fmt(r['texfast_rec']), fmt(r['texfast_bad'], 3)))
        out.append('    ' + ' '.join('%s %s' % (k[4:], fmt(r[k], 2)) for k in TM8))
        out.append('    probe %s ns a sampled lookup, %s us a frame' % (fmt(r['t_pb_ns'], 2),
                                                                     fmt(r['probe_us_frame'], 1)))
    out.append('  arming mode 1 - mode 0: tex_hits %s (>= +%s), key misses %s (<= -%s; both thresholds fixed in the '
               'scorer before the run); ceiling = mode-0 key misses %s a frame (reported)'
               % (fmt(res['d_tex_hits']), fmt(ARM_HITS_MIN), fmt(res['d_key_miss']), fmt(ARM_KEYS_MIN),
                  fmt(res['key_ceiling'])))
    out.append('  verify gained hits in [600, 2000] a frame (reported, not gated): mode 2 %s, mode 3 %s'
               % (res['gain_band'][2], res['gain_band'][3]))
    rb = res['rbchk_bound']
    out.append('  identity 19 (reported, not gated): 0 < rbchk <= texfast_ok + texfast_no on %d of %d mode-2/3 block '
               'windows%s' % (sum(1 for v in rb.values() if v), len(rb),
                              '; fails at ' + ' '.join(str(b) for b, v in rb.items() if not v)
                              if not all(rb.values()) else ''))
    for name, vals in res['identity_residuals'].items():
        out.append('  identity %s: max |residual| %s over %d mode-2/3 block windows'
                   % (name, max(abs(x) for x in vals) if vals else '-', len(vals)))
    if res['identity_failures']:
        out.append('  identity failures: %s' % ' '.join(res['identity_failures'][:12]))
    for name, vals in res['ratio_values'].items():
        good = [x for x in vals if x is not None]
        out.append('  ratio %s: min %s max %s (band [%s, %s])' % (name, fmt(min(good) if good else None, 5),
                                                                  fmt(max(good) if good else None, 5),
                                                                  fmt(RATIO_BAND[0], 5), fmt(RATIO_BAND[1], 5)))
    if res['ratio_failures']:
        out.append('  ratio failures: %s' % ' '.join(res['ratio_failures'][:12]))
    out.append('  ' + NOTE)
    if not res['admitted']:
        out.append('REPORT OF A NOT_ADMITTED RUN - NOT TO BE QUOTED')
    why = []
    if res['hard_bad']:
        why.append('hard: ' + ','.join(res['hard_bad']))
    if res['failed']:
        why.append('admission: ' + ','.join(res['failed']))
    if res['soft_bad']:
        why.append('evidence: ' + ','.join(res['soft_bad']))
    out.append('VERDICT: %s%s%s' % (res['verdict'], ' (%s)' % '; '.join(why) if why else '',
                                    ' DRAFT' if res['draft'] else ''))
    out.append('CONSEQUENCE: %s' % CONSEQUENCE[res['verdict']])
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    tag = sys.argv[sys.argv.index('--tag') + 1] if '--tag' in sys.argv else TAG
    draft = '--draft' in sys.argv
    inst = sys.argv[sys.argv.index('--installed-sha') + 1] if '--installed-sha' in sys.argv else None
    report = sys.argv[sys.argv.index('--glitch-report') + 1] if '--glitch-report' in sys.argv else None
    if tag not in TAGS and not draft:
        print('unknown tag %s (expected one of %s; any tag only with --draft)' % (tag, ', '.join(TAGS)))
        return 2
    res = evaluate(root, tag, draft=draft, installed_sha=inst, glitch_report=report)
    print(NL.join(format_report(res)))
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1, ensure_ascii=False)
                                                                .encode('utf-8'))
    return 0 if res['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
