"""Session 122, ROADMAP s0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1-3 and 8 (item 2 holds the reading rule
RC4-RC5, item 3 the implementation constants of the knob, item 8 the pair floor and the completeness of the map);
design C:/kyty/s122/design/design122.md and design/burn.md with design/burn_review.md; the format contract
C:/kyty/s122/map122_format_contract.md, confirmed line by line against the LIVE burn smoke log_bsky122.txt.
Pre-registration pred/01_map122.md; fixtures test_map122.py; mutants mut_map122.py; chain go122a.sh <tag>.

map122 scores ONE sealed ABBA of the measurement knob `burn` on ONE scene, on build BUILD_SHA: 300-s hold, one
attempt, pinned (KYTY_GPU_CLOCK_PIN=1), KYTY_GPU_MARKERS=0, gates_base.txt, KYTY_GATE_SCHEDULE=90+1800:burn=0|burn=V
with KYTY_GATE_SCHEDULE_ABBA=1.  Arm A (0) = "burn=0" (the baseline), arm B (1) = "burn=V" where V = code * 100000 +
dose_us of that scene's PLAN entry.  The '<tag>r' repeat only on NOT_ADMITTED.  The scene's verdict is the SLOPE of
the frame time in the dose, not a saving: nothing here ships anything.

Frames.  Block b starts at frame START + PERIOD*b (its GateArm line; blocks come from the GateArm lines, never from
the blk label, which shifts block 0); its frames are n = START + 1 + PERIOD*b + pos, pos 0..89.  WINDOW = positions
KEEP[0]..KEEP[1]-1 (10..88): the arm switch lands on position 89 of the OUTGOING block.  A block is complete when
every window frame has exactly one FrameTrace, -draw and -x line with every field read and its main line carries
arm = the block's arm and blk = b.  ESTIMATOR rows = window rows with draws > DRAWS_MIN.  Pairs = blocks (2k, 2k+1)
of the ABBA sequence (A B | B A | ...), both complete, both with estimator rows.

Admission (every check must hold, else NOT_ADMITTED; --draft skips ONLY prereg, prereg_sha and hold - and the pair
floor of the evaluability below):
  plan_sealed             the tag has a PLAN entry whose burn value is filled with a known code (None => the lead has
                          not recorded that arm => refused, never scored).  skym122, the main-guest-thread arm on
                          CODE 7, LEFT the map by ROADMAP s122 item 13 (b): the smoke csky122 armed code 7 but read
                          burn_s_main = 0 in every block (the burnt thread is not the main guest thread)
  binary / installed_now  TAG.json binary_sha256 and the installed exe are BUILD_SHA
  pinned                  env KYTY_GPU_CLOCK_PIN == '1' and exactly one `GpuClockPin:` line, mode 1
  env_exact / env_vk      the KYTY_* env is exactly the tag's ENV and TAG.json schedule its SCHEDULE; of VK_* only
                          VK_ALLOWED (KYTY_REC must be absent: a sealed run of this seal records no video)
  hold / one_ok_attempt   hold_s == HOLD_S; exactly one attempt, outcome ok, hold_exit None
  prereg / prereg_sha     prereg path PRED_PATH; PRED_SHA / PRED_BYTES filled (None => refused), the file matches
                          them now and TAG.json prereg sha256 / bytes are PRED_SHA / PRED_BYTES
  gates_exact             gates_base.txt hashes to GATES_SHA and TAG.json gates is its whitespace-normalised text
  arm_asserts             burn and the other census knobs of the recent sessions are absent-or-0 in the run's gate
                          text and named by no observed arm text except burn in the two arm texts; both arms observed
  gate_lines / arms       every `Gate:` / `GateArm:` line matches the ABBA schedule; arm texts EXACTLY ARM_TEXT
  no_marker               no hang/crash marker in the log or stdout_TAG.txt
  no_skip_window          ROADMAP s122 item 14: no `AsyncPipelines: skipped draw` attributed to a frame >= the FIRST
                          FRAME OF THE ESTIMATOR POPULATION (START + 1 + KEEP[0] of block 0; no threshold, one line
                          closes the run); earlier lines (the entry frames of a level carry ~20 at a cold pipeline
                          cache) are printed diagnostics - their count and the LARGEST frame; if the population's first
                          frame is unknown (no GateArm line, no block 0) every such line is fatal (item 14 (c))
  streams                 every main row of every block window has its -draw and -x rows with every field read (the
                          last main row of the log is exempt)
  outlier_pairs           ROADMAP s122 item 17 (c): a frame of a schedule block with dt_us >= OUTLIER_US declares its
                          block an outlier and the block leaves the population WHOLE together with its ABBA partner
                          (never a trim inside a block); every drop is printed with its frame and value; more than
                          MAX_OUTLIER_PAIRS dropped pairs => the run is INVALID (this check), and MIN_PAIRS is counted
                          AFTER the drops
  host_clean              ROADMAP s122 item 17 (a): hostdev_TAG.txt (hostdev122.py TAG --pad 0, a step of go122a.sh)
                          exists, names TAG, its window is exactly launched .. finished of TAG.json, and its verdict is
                          RUN_CLEAN or STALL_UNATTRIBUTED (a stall with no host event is judged by outlier_pairs);
                          RUN_INVALID (a HidBth / BTH* / nvlddmkm event in the window) fails, and a missing report,
                          an unknown window or NOT EVALUABLE (the journal was not read) is NOT CHECKED - also a fail
  host_tool               hostdev122.py hashes to HOSTDEV_SHA (the witness that wrote hostdev_TAG.txt is the pinned one)
  idle                    pre_run.gpu_util_median <= IDLE_GPU_MAX
  burn_ok                 over ALL rows burn_cpu_bad == 0 (item 3 (d): obligatory) and no `Burn: value=... rejected`
                          or `Burn: no calibrated TSC` line; the selftest line is present
  armed                   every complete B block: the window sum of the arm's own burn_*_ns > 0 and of every OTHER
                          group's _ns == 0; every complete A block: every burn_*_ns == 0 (the clean zero)
  arm_lines               every `Burn: arm code= thread= dose_us=` line carries the PLAN code / dose and the thread
                          name of that code; at least one such line
  dose                    the measured dose a frame of the B windows is within DOSE_TOL of DOSE_US (block codes: one
                          slice a frame, burn_*_ns/burn_*_n == the per-frame dose; spread codes 2/3: burn_*_ns/frames,
                          while burn_*_ns/burn_*_n is the per-unit dose - per worker for code 3, RC7)
  coverage                the coverage counter of the arm's code > 0 on the B windows (code 7: burn_s_seen, and its
                          role split burn_s_main > 0 as well - the arm measures the MAIN guest thread, item 13 (a);
                          every other code: burn_<prefix>_seen)

Not evaluable (=> NOT_EVALUABLE, the scene enters the map without a slope):
  pairs            fewer than MIN_PAIRS = 24 pairs AFTER the outlier drops (ROADMAP item 8 (c), 17 (c))
  two_se_undefined fewer than two pairs
  bda_regime       the BDA regime (bda_scan) of the two arms differs, or neither is NEW/OLD (regimes are not compared)

Estimator: per block, the mean of main-line dt_us over its estimator rows; Delta = mean over pairs of (B block mean -
A block mean); 2SE = 2 * stdev(per-pair differences) / sqrt(pairs); SLOPE s = Delta / DOSE_US and its 2SE likewise.
The same for cpu_gpu_us and gpu_busy_us (reported only).
Draw-adjusted estimator beside the raw one (reported only, never the verdict - RC4 is written on the raw slope): per
pair, adj = B mean dt - A mean dt * (B mean draws / A mean draws), i.e. the A block rescaled to the B block's draw
count; its mean, 2SE, slope and zone are printed, and a zone that differs from the raw zone is printed as
`DRAW-ADJUSTED ZONE DIFFERS`.
Reading (ROADMAP s122 items 17 (d), 18 (c)): the scene is HEADROOM by the MEASURED property of this run, never by its
level name - over the window rows (positions 10..88) of the base-arm (burn=0) blocks of the population pairs (after
the outlier drops), the share of frames with dt_us < HEADROOM_DT_US (25 000, midway between one and two vblanks) is
>= HEADROOM_SHARE (0.95).  There the slope measures HEADROOM - how much work the frame absorbs before it falls to the
next step - and is never quoted as speed: the verdict line says `reading=HEADROOM` and the game-speed line is
withheld.  No base-arm window row in the population => `reading=NOT_EVALUABLE` (never HEADROOM) and the game-speed
line is withheld as well; otherwise `reading=SPEED`.  Every verdict line carries the
BDA regime of the run; an OLD scene's numbers are never compared with those of NEW scenes (item 17 (e)).
Verdict (ROADMAP item 2, RC4-RC5, quoted in CONSEQUENCE, checked in this order):
  SUPERLINEAR  s - 2SE > 1                      the dose pushed frames across a vblank step
  CRITICAL     s - 2SE > 0.5 and s + 2SE >= 1   the thread is critical, a saving on it converts 1:1
  NOT_CRITICAL s + 2SE < 0.3                    not critical
  NOT_RESOLVED otherwise                        "НЕ РАЗРЕШЕНО" - no verdict for this scene and thread
Scene classification beside it (live lite counters): median gpu_busy/dt, cpu_gpu/dt, cpu_main/dt, rec_spin_us, the
vblank multiples of dt with their shares, PINCHED when >= PINCH of the frames sit on one multiple, and GPU_BOUND when
median gpu_busy/dt >= GPU_BOUND and this run's arm is the GuestGpu code with verdict NOT_CRITICAL (any other code
cannot answer the GPU question - reported as 'n/a (not the GuestGpu arm)').
Every ns counter is divided by NS_PER_US exactly once.

    python C:/kyty/s122/map122.py [--root C:/kyty/s122] [--tag sky122] [--draft] [--out <json>]
    python C:/kyty/s122/map122.py --plan-check <tag>      # exit 0 iff that tag's arm is sealed (used by go122a.sh)
"""
import hashlib
import json
import math
import re
import statistics
import sys
from pathlib import Path

ROOT = 'C:/kyty/s122'
BUILD_SHA = '2baf8742676255fefd37c72f727e6c27c024be9b67d3afa987bed7fe334af86b'  # git 25f3886, pinned copy in ROOT
INSTALLED = 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe'  # the emulator folder moved out of OneDrive (s122)
GATES_FILE = 'C:/kyty/s122/gates_base.txt'
GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'
PRED_PATH = 'C:/kyty/s122/pred/01_map122.md'
PRED_SHA = '3430b26fb77ae7284e23ec7351860b9d4f6b37f7085627de5b39028260d00677'   # pred/01_map122.md, sealed 2026-09-27 (step 3b)
PRED_BYTES = 11126        # pred/01_map122.md, sealed 2026-09-27
HOLD_S = 300
PERIOD = 90
START = 1800
KEEP = (10, 89)
DRAWS_MIN = 300          # the scenes of this map run 2 570..4 679 draws a frame; the floor only drops idle rows
ABBA = (0, 1, 1, 0)
ARM_A = 0                # "burn=0", the baseline
ARM_B = 1                # "burn=<code><dose>", the armed arm
MIN_PAIRS = 24           # ROADMAP item 8 (c); below it the scene is NOT_EVALUABLE, never judged by a slope
IDLE_GPU_MAX = 10
DOSE_US = 2000           # ROADMAP item 2: 2 000 us a frame on every arm of this map
DOSE_TOL = 0.05          # |measured per-frame dose / DOSE_US - 1| (arming, not a verdict)
S_CRIT_LO = 0.5          # RC4: critical needs s - 2SE > 0.5 ...
S_REACH = 1.0            # ... and the interval to reach 1
S_FLAT_HI = 0.3          # RC4: not critical needs s + 2SE < 0.3
S_SUPER = 1.0            # RC5: superlinear needs s - 2SE > 1
GPU_BOUND = 0.9          # RC4: GPU-bound needs median gpu_busy/dt >= 0.9 and the GuestGpu arm NOT_CRITICAL
PINCH = 0.80             # RC5: a "pinched" scene keeps >= 80 % of its frames on one vblank multiple
VBLANK_US = 16667.0
GAME_FRAME_US = 16667.0  # game speed = 16 667 / mean dt_us
NS_PER_US = 1000.0
BDA_NEW_MAX = 300
BDA_OLD_MIN = 600
CPU_WALL_BLOCK = 1.00    # item 3 (e): blocks ~1.00, spread codes ~1.33 against the base - printed diagnostics only
CPU_WALL_SPREAD = 1.33
OUTLIER_US = 500000      # item 17 (c): a frame of dt_us >= 0.5 s drops its block and the block's ABBA partner
MAX_OUTLIER_PAIRS = 2    # item 17 (c): more dropped pairs than this => the run is INVALID and repeated
HOSTDEV_PY = 'C:/kyty/s122/hostdev122.py'
HOSTDEV_SHA = '8404ff8c309a2cf723c44262c543343fe55a5a3b2e1c21c264831b8cac935a1c'   # 87 fixtures, ALL OK
HOST_OK = ('RUN_CLEAN', 'STALL_UNATTRIBUTED')   # item 17 (a): no host device event in the window
HEADROOM_DT_US = 25000   # item 18 (c): a frame is 'one vblank' when dt_us < 25 000 (midway between 1 and 2 vblanks)
HEADROOM_SHARE = 0.95    # item 18 (c): HEADROOM when >= 0.95 of the base-arm window frames are one vblank
NL = chr(10)
# the scenes of the map: tag -> level and the B arm's knob value (code * 100000 + dose_us).  None = the lead has not
# recorded that arm; such a tag is refused (ROADMAP item 3: an unrecorded decision is void).  The main-guest-thread
# arm is NOT in the map: the smoke bsky122 measured the code-4 site DEAD (burn_t_seen = 0, burn_s_main = 0), item 13
# moved the arm to code 7, and the smoke csky122 armed code 7 with burn_s_main = 0 in every block - item 13 (a) fails,
# so by item 13 (b) the skym122 arm left the map (no PLAN entry: the tag is refused).  Order of step 4 (item 17 (d)):
# sky122, skyp122, then des122 (intro_next) as the first additional scene.
PLAN_DEFAULT = {
    'sky122':  dict(level='underwater_aerial_garden', burn=102000),
    'skyp122': dict(level='underwater_aerial_garden', burn=802000),
    'atl122':  dict(level='penguin_atlantis', burn=102000),
    'ght122':  dict(level='time_stopper_ghost_world', burn=102000),
    'dnn122':  dict(level='rotating_level_day_and_night', burn=102000),
    'des122':  dict(level='intro_next', burn=102000),
    'mgg122':  dict(level='mini_giants_garden', burn=102000),
    'hub122':  dict(level='hub_crashsite', burn=102000),
    'hov122':  dict(level='hoover_beach', burn=102000),
    'ice122':  dict(level='ice_iceberg', burn=102000),
}
PLAN = dict(PLAN_DEFAULT)   # evaluate() resets this from its plan= argument on every call (the fixtures pass theirs)
# the five counter groups of the knob (map122_format_contract.md section 2; the thread names are the string literals
# of frameStats.cpp BurnArm, read off the build): code -> (prefix, kind, thread name)
CODE_GROUP = {1: ('g', 'block', 'GuestGpu'), 2: ('r', 'spread', 'Record'), 3: ('m', 'spread', 'M1'),
              4: ('t', 'block', 'Main'), 5: ('r', 'block', 'Record'), 6: ('m', 'block', 'M1worker0'),
              7: ('t', 'block', 'Submit'), 8: ('p', 'block', 'Placebo')}
PREFIXES = ('g', 'r', 'm', 't', 'p')
# the coverage counter of a code: code 7 is covered by burn_s_seen with the role split burn_s_main (item 3 (c))
COVER = {7: 'burn_s_seen'}
ROLE = {7: 'burn_s_main'}
BURN_NS = tuple('burn_%s_ns' % p for p in PREFIXES)
BURN_KEYS = tuple('burn_%s_%s' % (p, s) for p in PREFIXES for s in ('ns', 'n', 'cpu_ns', 'cpu_w', 'seen')) \
            + ('burn_r_q', 'burn_m_q', 'burn_m0_seen', 'burn_s_seen', 'burn_s_main', 'burn_late', 'burn_cpu_bad')
MAIN_FIELDS = ('dt_us', 'cpu_gpu_us', 'gpu_busy_us', 'cpu_main_us', 'draws', 'dispatches', 'submits', 'arm', 'blk')
DRAW_FIELDS = ('bda_scan',)
X_FIELDS = ('rec_spin_us',) + BURN_KEYS
BASE_ABSENT_OR_0 = ('burn', 'texmemo8', 'texmemo2', 'r1cen', 'r2cen', 'spcen', 'spine', 'slicecen', 'bindfloor',
                    'mergecost', 'framerep', 'bdacap', 'bdaall', 'plkstat', 'pathlap', 'blmove', 'cbmove')
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---')
SKIPPED_DRAW = b'AsyncPipelines: skipped draw'
KINDS = ((re.compile(rb'^FrameTrace: n=(\d+)'), 'main', MAIN_FIELDS),
         (re.compile(rb'^FrameTrace-draw: n=(\d+)'), 'draw', DRAW_FIELDS),
         (re.compile(rb'^FrameTrace-x: n=(\d+)'), 'x', X_FIELDS))
FIELD = re.compile(rb' (\w+)=(-?\d+)')
PIN = re.compile(rb'^GpuClockPin: mode (\d+)')
GATE = re.compile(rb'^Gate: (\w+)=(\d+) frame=(\d+)$')
GATE_ARM = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
BURN_ARM = re.compile(rb'^Burn: arm code=(\d+) thread=(\S+) dose_us=(\d+) q_ns=(\d+)$')
BURN_SELFTEST = re.compile(rb'^Burn: selftest target_us=(\d+) ')
BURN_REJECT = re.compile(rb'^Burn: value=\d+ rejected')
BURN_NOTSC = re.compile(rb'^Burn: no calibrated TSC')
BURN_LATE = re.compile(rb'^BurnLate: code=(\d+) us=([0-9.]+) target_us=(\d+)$')
VK_ALLOWED = ('VK_SDK_PATH',)
CONSEQUENCE = {
    'CRITICAL': ('CRITICAL - "критичен — s − 2SE > 0,5 и интервал достигает 1" (ROADMAP s122 item 2): the burnt '
                 'thread is on the critical path of this scene and a saving on it converts into frame time about '
                 '1:1; the track of THAT thread is the scene\'s candidate lever.'),
    'SUPERLINEAR': ('SUPERLINEAR - "сверхлинейный — s − 2SE > 1 (доза перекинула кадры через ступень вблэнка)" '
                    '(ROADMAP s122 item 2): the slope is not a cost of the thread alone - the dose moved frames '
                    'across a vblank step, so the number is an upper bound and the scene is read with its step '
                    'shares, never as a 1:1 conversion.'),
    'NOT_CRITICAL': ('NOT_CRITICAL - "не критичен — s + 2SE < 0,3" (ROADMAP s122 item 2): time burnt on this thread '
                     'does not reach the frame; no track of this thread is opened by this scene.'),
    'NOT_RESOLVED': ('NOT_RESOLVED ("НЕ РАЗРЕШЕНО", ROADMAP s122 item 2): the interval falls in neither band; the '
                     'scene enters the map WITHOUT a slope verdict and no lever is opened or closed by it.'),
    'NOT_ADMITTED': ('NOT_ADMITTED - one repeat <tag>r (the rule of every sealed run of this programme; a run INVALID '
                     'by host events or by more than two outlier pairs is repeated whole, ROADMAP s122 item 17): '
                     'admission, not a verdict; no number of this run is quoted.'),
    'NOT_EVALUABLE': ('NOT_EVALUABLE - "сцена с меньшим числом пар идёт в карту как NOT EVALUABLE и наклоном не '
                      'судится" (ROADMAP s122 item 8 (c)) or the two arms ran in different BDA regimes: the scene is '
                      'listed in the map as entered but unjudged; an empty population is never "no effect".'),
}


def base_tag(tag):
    return tag[:-1] if tag.endswith('r') else tag


def plan_of(tag):
    return PLAN.get(base_tag(tag))


def arm_value(tag):
    plan = plan_of(tag)
    return None if plan is None else plan['burn']


def code_dose(value):
    """The knob value -> (code, dose_us); 0 -> (0, 0)."""
    if value is None:
        return None, None
    return (0, 0) if value == 0 else (value // 100000, value % 100000)


def arm_texts(tag):
    v = arm_value(tag)
    return ('burn=0', None if v is None else 'burn=%d' % v)


def schedule_of(tag):
    texts = arm_texts(tag)
    return None if texts[1] is None else '%d+%d:%s|%s' % (PERIOD, START, texts[0], texts[1])


def env_of(tag):
    plan = plan_of(tag)
    sched = schedule_of(tag)
    if plan is None or sched is None:
        return None
    return {
        'KYTY_FRAME_TRACE': 'lite',
        'KYTY_GPU_HANG_ABORT_S': '8',
        'KYTY_GATE_FILE': 'C:\\kyty\\s122\\gates.req',
        'KYTY_SAMPLE_GATE': 'C:\\kyty\\s122\\sample.req',
        'KYTY_QUEUE_TRACE': '1',
        'KYTY_GUEST_ARGS': '-lvl ' + plan['level'],
        'KYTY_GATE_SCHEDULE': sched,
        'KYTY_GATE_SCHEDULE_ABBA': '1',
        'KYTY_GPU_CLOCK_PIN': '1',
        'KYTY_GPU_MARKERS': '0',
    }


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


def median(values):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def div(a, b):
    return None if a is None or not b else a / b


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


def arm_asserts(texts, gates_text, tag):
    """burn and the census knobs absent-or-0 in the run's gate file; both arms observed and every observed arm text
    EXACTLY the expected one ('burn=0' / 'burn=<V>' - so no arm text names anything but burn)."""
    want = arm_texts(tag)
    if want[1] is None or not texts.get(ARM_A) or not texts.get(ARM_B):
        return False
    g = first_values(gates_text)
    for name in BASE_ABSENT_OR_0:
        if g.get(name) not in (None, '0'):
            return False
    for arm in (ARM_A, ARM_B):
        for t in texts[arm]:
            if t != want[arm]:
                return False
    return True


def arms_ok(gate_arms, tag):
    """Blocks from the GateArm lines: arms=2, period, abba=1, text EXACTLY the tag's arm text, frame START +
    PERIOD*block, arm = ABBA[block % 4], blocks consecutive from 0."""
    want = arm_texts(tag)
    if want[1] is None:
        return False, {}
    blocks = {}
    for g in gate_arms:
        if g is None:
            return False, {}
        arm, arms, block, frame, period, abba, text = g
        if arms != 2 or period != PERIOD or abba != 1 or arm not in (0, 1) or text != want[arm]:
            return False, {}
        if frame != START + PERIOD * block or ABBA[block % 4] != arm or block in blocks:
            return False, {}
        blocks[block] = arm
    ok = bool(blocks) and sorted(blocks) == list(range(len(blocks)))
    return ok, blocks


def gate_lines_ok(lines, blocks, tag):
    """Every `Gate: burn=<v> frame=<n>` sits on a block boundary and carries that block's arm value."""
    values = tuple(first_values(t) for t in arm_texts(tag))
    if values[1] is None or 'burn' not in (values[1] or {}):
        return False
    for raw in lines:
        m = GATE.match(raw)
        if m is None:
            return False
        name = m.group(1).decode()
        frame = int(m.group(3))
        if name != 'burn' or frame < START or (frame - START) % PERIOD != 0:
            return False
        block = (frame - START) // PERIOD
        if block not in blocks or m.group(2).decode() != values[blocks[block]][name]:
            return False
    return True


def parse_log(path, stdout_path=None):
    """One streaming pass.  Rows by kind and frame (only the fields read; a row missing one is None); dt_us of every
    main line (the largest of duplicates, for the outlier rule, even on an incomplete row); every burn_* summed over
    EVERY FrameTrace-x line; the Burn lines; marker and skipped-draw lines."""
    seen = {'main': {}, 'draw': {}, 'x': {}}
    dts = {}
    dups = set()
    raw = {k: 0 for k in BURN_KEYS}
    pins, gate_arms, gate_lines, markers = [], [], [], []
    burn = dict(arm=[], late=[], reject=0, notsc=0, selftest=0)
    skipped = []
    last_main = None
    with open(path, 'rb') as f:
        for line in f:
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
            if SKIPPED_DRAW in line:
                skipped.append(None if last_main is None else last_main + 1)
            if line.startswith(b'Burn'):
                stripped = line.rstrip(b'\r\n')
                ma = BURN_ARM.match(stripped)
                if ma:
                    burn['arm'].append((int(ma.group(1)), ma.group(2).decode('utf-8', 'replace'), int(ma.group(3)),
                                        int(ma.group(4))))
                ml = BURN_LATE.match(stripped)
                if ml:
                    burn['late'].append((int(ml.group(1)), float(ml.group(2)), int(ml.group(3))))
                if BURN_REJECT.match(stripped):
                    burn['reject'] += 1
                if BURN_NOTSC.match(stripped):
                    burn['notsc'] += 1
                if BURN_SELFTEST.match(stripped):
                    burn['selftest'] += 1
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
                    if b'dt_us' in got:
                        dts[n] = max(dts.get(n, 0), int(got[b'dt_us']))
                if n in seen[kind]:
                    dups.add(n)
                seen[kind][n] = rec if len(rec) == len(names) else None
                break
    if stdout_path is not None and Path(stdout_path).is_file():
        for line in open(stdout_path, 'rb'):
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
    return dict(seen=seen, dups=dups, raw=raw, pins=pins, gate_arms=gate_arms, gate_lines=gate_lines,
                markers=markers, burn=burn, skipped=skipped, last_main=last_main, dts=dts)


def block_frames(b):
    return list(range(START + 1 + PERIOD * b, START + 1 + PERIOD * (b + 1)))


def outliers_of(parsed, blocks):
    """[(frame, dt_us, block)] of every frame of a schedule block (positions 0..89) with dt_us >= OUTLIER_US."""
    out = []
    for n, dt in sorted(parsed['dts'].items()):
        if dt >= OUTLIER_US:
            b = (n - START - 1) // PERIOD     # negative before the schedule: never a block
            if b in blocks:
                out.append((n, dt, b))
    return out


def dropped_pairs(outs):
    """The ABBA pairs (2k, 2k+1) an outlier frame takes out of the population, sorted."""
    return sorted({b - b % 2 for _n, _dt, b in outs})


def select(parsed, blocks, drop=()):
    """Complete blocks (every window frame complete, labels = the schedule) with their window rows (win) and
    estimator rows (est); pairs (2k, 2k+1), both complete, both with estimator rows, 2k not in drop."""
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
            done[b] = dict(arm=arm, win=win, est=[r for r in win if r['draws'] > DRAWS_MIN])
    top = max(blocks) + 1 if blocks else 0
    pairs = [(b, b + 1) for b in range(0, top, 2)
             if b in done and b + 1 in done and done[b]['est'] and done[b + 1]['est'] and b not in drop]
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


def first_population_frame(blocks):
    """The first frame of the estimator population (position KEEP[0] of block 0); None when block 0 is unknown."""
    return START + 1 + KEEP[0] if 0 in blocks else None


def skip_fatal(frame, first):
    """ROADMAP s122 item 14: a skipped-draw line is fatal from the population's first frame on; with that frame unknown
    every line is fatal (c).  A line before the first FrameTrace row carries frame None (before any population)."""
    if first is None:
        return True
    return frame is not None and frame >= first


def window_sums(done, arm, keys):
    out = {k: 0 for k in keys}
    for blk in done.values():
        if blk['arm'] == arm:
            for r in blk['win']:
                for k in keys:
                    out[k] += r[k]
    return out


def armed_ok(done, prefix):
    """Every complete B block: its own group burnt and no other; every complete A block: nothing burnt."""
    own = 'burn_%s_ns' % prefix
    b_blocks = [blk for blk in done.values() if blk['arm'] == ARM_B]
    if not b_blocks:
        return False
    for blk in b_blocks:
        if sum(r[own] for r in blk['win']) <= 0:
            return False
        if any(sum(r[k] for r in blk['win']) != 0 for k in BURN_NS if k != own):
            return False
    for blk in done.values():
        if blk['arm'] == ARM_A and any(sum(r[k] for r in blk['win']) != 0 for k in BURN_NS):
            return False
    return True


def arm_lines_ok(lines, code, dose):
    """Every `Burn: arm` line carries this run's code, its thread name and the dose; at least one line."""
    if not lines:
        return False
    thread = CODE_GROUP[code][2] if code in CODE_GROUP else None
    return all(c == code and d == dose and (thread is None or t == thread) for c, t, d, _q in lines)


def burn_measure(done, prefix, kind):
    """The measured dose of the B windows: per frame (always comparable to DOSE_US) and per armed unit (per worker for
    the spread code 3, RC7), with the cpu/wall ratio and the coverage."""
    rows = [r for blk in done.values() if blk['arm'] == ARM_B for r in blk['win']]
    keys = ('ns', 'n', 'cpu_ns', 'cpu_w', 'seen')
    s = {k: sum(r['burn_%s_%s' % (prefix, k)] for r in rows) for k in keys} if rows else {k: 0 for k in keys}
    return dict(frames=len(rows), ns=s['ns'], n=s['n'], seen=s['seen'],
                per_frame_us=div(s['ns'] / NS_PER_US, len(rows)), per_unit_us=div(s['ns'] / NS_PER_US, s['n']),
                cpu_wall=div(float(s['cpu_ns']), s['cpu_w']), kind=kind,
                cpu_wall_expect=CPU_WALL_SPREAD if kind == 'spread' else CPU_WALL_BLOCK)


def coverage_of(done, code, prefix):
    """(counter name, value on the B windows, role name, role value); code 7 is covered by burn_s_seen (item 3 (c))."""
    name = COVER.get(code, 'burn_%s_seen' % prefix)
    role = ROLE.get(code)
    keys = (name,) + ((role,) if role else ())
    s = window_sums(done, ARM_B, keys)
    return dict(counter=name, value=s[name], role=role, role_value=s[role] if role else None)


def coverage_ok(cover):
    """The coverage counter > 0 and, for a code with a role split (code 7), the role counter > 0 (item 13 (a))."""
    return bool(cover and cover['value'] > 0 and (cover['role'] is None or cover['role_value'] > 0))


def host_check(root, tag, meta):
    """(ok, verdict text) of hostdev_TAG.txt: it names TAG, its window is exactly launched .. finished of TAG.json and
    its verdict is in HOST_OK.  A missing report, a foreign window or NOT EVALUABLE is 'NOT CHECKED' (a fail)."""
    path = Path(root) / ('hostdev_%s.txt' % tag)
    if not path.is_file():
        return False, 'NOT CHECKED (no hostdev_%s.txt)' % tag
    lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
    want_window = 'window %s .. %s (padded)' % (meta.get('launched'), meta.get('finished'))
    verdicts = [ln[len('VERDICT: '):].split(' - ')[0].strip() for ln in lines if ln.startswith('VERDICT: ')]
    if not lines or lines[0].strip() != 'hostdev122 %s' % tag:
        return False, 'NOT CHECKED (the report names another run)'
    if want_window not in [ln.strip() for ln in lines]:
        return False, 'NOT CHECKED (the report window is not launched .. finished of %s.json)' % tag
    if len(verdicts) != 1:
        return False, 'NOT CHECKED (%d verdict lines)' % len(verdicts)
    if verdicts[0] == 'NOT EVALUABLE':
        return False, 'NOT CHECKED (the System journal was not read)'
    return verdicts[0] in HOST_OK, verdicts[0]


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


def estimate(done, pairs, key):
    """Per pair: B block mean - A block mean of key over the estimator rows; mean, 2SE, per-arm means of block means."""
    diffs, bm, am = [], [], []
    for pr in pairs:
        bb = [b for b in pr if done[b]['arm'] == ARM_B][0]
        ab = [b for b in pr if done[b]['arm'] == ARM_A][0]
        a = mean([r[key] for r in done[bb]['est']])
        c = mean([r[key] for r in done[ab]['est']])
        diffs.append(a - c)
        bm.append(a)
        am.append(c)
    return dict(delta=mean(diffs), two_se=two_se(diffs), B=mean(bm), A=mean(am), pair_diffs=diffs)


def estimate_draw_adjusted(done, pairs):
    """Per pair: B mean dt - A mean dt * (B mean draws / A mean draws) over the estimator rows (the A block rescaled to
    the B block's draw count); mean and 2SE.  Reported beside the raw estimator, never the verdict."""
    diffs = []
    for pr in pairs:
        bb = [b for b in pr if done[b]['arm'] == ARM_B][0]
        ab = [b for b in pr if done[b]['arm'] == ARM_A][0]
        b_dt = mean([r['dt_us'] for r in done[bb]['est']])
        a_dt = mean([r['dt_us'] for r in done[ab]['est']])
        ratio = div(mean([r['draws'] for r in done[bb]['est']]), mean([r['draws'] for r in done[ab]['est']]))
        diffs.append(b_dt - a_dt * ratio)
    draws = estimate(done, pairs, 'draws')
    return dict(delta=mean(diffs), two_se=two_se(diffs), pair_diffs=diffs, draws_delta=draws['delta'],
                draws_two_se=draws['two_se'])


def slope_of(est, dose):
    """The slope s = Delta / dose and its 2SE, with the interval edges."""
    s = div(est['delta'], dose)
    se = div(est['two_se'], dose)
    return dict(s=s, two_se=se, lo=None if s is None or se is None else s - se,
                hi=None if s is None or se is None else s + se)


def zone(sl):
    if sl['lo'] is None or sl['hi'] is None:
        return None
    if sl['lo'] > S_SUPER:
        return 'SUPERLINEAR'
    if sl['lo'] > S_CRIT_LO and sl['hi'] >= S_REACH:
        return 'CRITICAL'
    if sl['hi'] < S_FLAT_HI:
        return 'NOT_CRITICAL'
    return 'NOT_RESOLVED'


def vblank_shares(rows):
    """{multiple: share} of dt over the rows, and (multiple, share) of the largest."""
    dts = [r['dt_us'] for r in rows if 'dt_us' in r]
    if not dts:
        return {}, (None, None)
    counts = {}
    for dt in dts:
        k = max(1, int(round(dt / VBLANK_US)))
        counts[k] = counts.get(k, 0) + 1
    shares = {k: v / float(len(dts)) for k, v in sorted(counts.items())}
    top = max(shares.items(), key=lambda kv: kv[1])
    return shares, top


def scene_of(done, pairs, code, verdict):
    """The scene's classification from the live lite counters over the estimator rows of the paired blocks."""
    rows = [r for pr in pairs for b in pr for r in done[b]['est']]
    ratios = {}
    for name, key in (('gpu_busy/dt', 'gpu_busy_us'), ('cpu_gpu/dt', 'cpu_gpu_us'), ('cpu_main/dt', 'cpu_main_us')):
        ratios[name] = median([r[key] / float(r['dt_us']) for r in rows if r.get('dt_us')])
    shares, top = vblank_shares(rows)
    gpu_ratio = ratios['gpu_busy/dt']
    if code != 1:
        gpu_bound = None
    else:
        gpu_bound = bool(gpu_ratio is not None and gpu_ratio >= GPU_BOUND and verdict == 'NOT_CRITICAL')
    return dict(ratios=ratios, rec_spin_us=mean([r['rec_spin_us'] for r in rows]),
                dt_median=median([r['dt_us'] for r in rows]), draws=mean([r['draws'] for r in rows]),
                dispatches=mean([r['dispatches'] for r in rows]), submits=mean([r['submits'] for r in rows]),
                vblank_shares=shares, vblank_top=top[0], vblank_top_share=top[1],
                pinched=None if top[1] is None else bool(top[1] >= PINCH), gpu_bound=gpu_bound, frames=len(rows))


def reading_of(dts):
    """(reading, share, frames) of the base-arm window dt_us values (ROADMAP s122 item 18 (c)): HEADROOM when the
    share of dt_us < HEADROOM_DT_US is >= HEADROOM_SHARE, SPEED otherwise; no value => NOT_EVALUABLE (never
    HEADROOM)."""
    if not dts:
        return 'NOT_EVALUABLE', None, 0
    share = sum(1 for d in dts if d < HEADROOM_DT_US) / float(len(dts))
    return ('HEADROOM' if share >= HEADROOM_SHARE else 'SPEED'), share, len(dts)


def headroom_of(done, pairs):
    """The reading of this run from the window rows (positions KEEP) of the base-arm blocks of the population pairs."""
    return reading_of([r['dt_us'] for pr in pairs for b in pr if done[b]['arm'] == ARM_A for r in done[b]['win']])


def speed(dt):
    return None if not dt else GAME_FRAME_US / dt


def evaluate(root=ROOT, tag='sky122', draft=False, installed_sha=None, min_pairs=None, pred_sha=None, pred_bytes=None,
             pred_path=None, gates_file=GATES_FILE, plan=None, hostdev_py=None):
    """Admission, evaluability, the slope, the scene's classification and the verdict.  installed_sha None = hash
    INSTALLED; pred_* None = the module constants; plan None = PLAN (the fixtures pass their own); hostdev_py None =
    HOSTDEV_PY."""
    min_pairs = MIN_PAIRS if min_pairs is None else min_pairs
    hostdev_py = HOSTDEV_PY if hostdev_py is None else hostdev_py
    pred_sha = PRED_SHA if pred_sha is None else pred_sha
    pred_bytes = PRED_BYTES if pred_bytes is None else pred_bytes
    pred_path = PRED_PATH if pred_path is None else pred_path
    global PLAN
    PLAN = dict(PLAN_DEFAULT if plan is None else plan)
    entry = plan_of(tag)
    value = arm_value(tag)
    code, dose = code_dose(value)
    prefix, kind = (CODE_GROUP[code][0], CODE_GROUP[code][1]) if code in CODE_GROUP else (None, None)
    res = dict(scorer_sha256=sha_file(__file__), build_sha256=BUILD_SHA, tag=tag, draft=draft,
               level=None if entry is None else entry['level'], burn_value=value, code=code, dose_us=dose,
               prefix=prefix, dose_kind=kind)
    meta = json.loads((Path(root) / (tag + '.json')).read_text(encoding='utf-8'))
    env = meta.get('env') or {}
    kyty_env = {k: v for k, v in env.items() if k.startswith('KYTY_')}
    vk_env = sorted(k for k in env if k.startswith('VK_'))
    atts = meta.get('attempts') or []
    ok_att = [a for a in atts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]
    gates_text = ' '.join((meta.get('gates') or '').split())
    base_text = ' '.join(Path(gates_file).read_text(encoding='utf-8').split()) if Path(gates_file).is_file() else None
    parsed = parse_log(Path(root) / ('log_%s.txt' % tag), Path(root) / ('stdout_%s.txt' % tag))
    arms_fine, blocks = arms_ok(parsed['gate_arms'], tag)
    outs = outliers_of(parsed, blocks)
    drops = dropped_pairs(outs)
    done, pairs = select(parsed, blocks, drops)
    if installed_sha is None:
        installed_sha = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    prereg_ok, prereg_sha_ok = pred_checks(meta, draft, pred_sha, pred_bytes, pred_path)
    first_pop = first_population_frame(blocks)
    skipped_in = [f for f in parsed['skipped'] if skip_fatal(f, first_pop)]
    skipped_out = [f for f in parsed['skipped'] if not skip_fatal(f, first_pop)]
    host_ok, host_verdict = host_check(root, tag, meta)
    texts = {}
    for g in parsed['gate_arms']:
        if g is not None and g[0] in (ARM_A, ARM_B):
            texts.setdefault(g[0], []).append(g[6])
    raw = parsed['raw']
    burn = parsed['burn']
    sealed_plan = value is not None and code in CODE_GROUP
    measure = burn_measure(done, prefix, kind) if sealed_plan else None
    cover = coverage_of(done, code, prefix) if sealed_plan else None
    checks = dict(
        plan_sealed=sealed_plan,
        binary=meta.get('binary_sha256') == BUILD_SHA,
        installed_now=installed_sha == BUILD_SHA,
        pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and parsed['pins'] == [1],
        env_exact=sealed_plan and kyty_env == env_of(tag) and meta.get('schedule') == schedule_of(tag),
        env_vk=all(k in VK_ALLOWED for k in vk_env),
        hold=draft or meta.get('hold_s') == HOLD_S,
        one_ok_attempt=len(atts) == 1 and len(ok_att) == 1,
        prereg=prereg_ok,
        prereg_sha=prereg_sha_ok,
        gates_exact=(Path(gates_file).is_file() and sha_file(gates_file) == GATES_SHA and gates_text == base_text),
        arm_asserts=arm_asserts(texts, gates_text, tag),
        gate_lines=gate_lines_ok(parsed['gate_lines'], blocks, tag),
        arms=arms_fine,
        no_marker=not parsed['markers'],
        no_skip_window=not skipped_in,
        streams=streams_ok(parsed, blocks),
        outlier_pairs=len(drops) <= MAX_OUTLIER_PAIRS,
        host_clean=host_ok,
        host_tool=Path(hostdev_py).is_file() and sha_file(hostdev_py) == HOSTDEV_SHA,
        idle=idle_ok(meta),
        burn_ok=raw['burn_cpu_bad'] == 0 and burn['reject'] == 0 and burn['notsc'] == 0 and burn['selftest'] > 0,
        armed=sealed_plan and armed_ok(done, prefix),
        arm_lines=sealed_plan and arm_lines_ok(burn['arm'], code, dose),
        dose=bool(measure and measure['per_frame_us'] is not None
                  and abs(measure['per_frame_us'] - DOSE_US) <= DOSE_TOL * DOSE_US),
        coverage=coverage_ok(cover))
    admitted = all(checks.values())

    dt = estimate(done, pairs, 'dt_us')
    cpu = estimate(done, pairs, 'cpu_gpu_us')
    gpu = estimate(done, pairs, 'gpu_busy_us')
    adj = estimate_draw_adjusted(done, pairs)
    none = dict(s=None, two_se=None, lo=None, hi=None)
    sl = slope_of(dt, dose) if dose else none
    sl_adj = slope_of(adj, dose) if dose else none
    bda = dict(B=mean([r['bda_scan'] for pr in pairs for b in pr if done[b]['arm'] == ARM_B
                       for r in done[b]['est']]),
               A=mean([r['bda_scan'] for pr in pairs for b in pr if done[b]['arm'] == ARM_A
                       for r in done[b]['est']]))
    bda.update(B_regime=regime(bda['B']), A_regime=regime(bda['A']))
    ne = []
    if not draft and len(pairs) < min_pairs:
        ne.append('pairs')
    if dt['two_se'] is None:
        ne.append('two_se_undefined')
    if bda['A_regime'] is None or bda['A_regime'] != bda['B_regime'] or bda['A_regime'] == 'MIXED':
        ne.append('bda_regime')
    z = zone(sl)
    z_adj = zone(sl_adj)
    scene = scene_of(done, pairs, code, z)
    if not admitted:
        verdict = 'NOT_EVALUABLE' if tag.endswith('r') else 'NOT_ADMITTED'
    elif ne or z is None:
        verdict = 'NOT_EVALUABLE'
    else:
        verdict = z
    reading, fast_share, fast_frames = headroom_of(done, pairs)
    speeds = dict(A=speed(dt['A']), B=speed(dt['B']))
    speeds['change_rel_pct'] = None if not dt['B'] or dt['A'] is None else 100.0 * (dt['A'] / dt['B'] - 1.0)
    res.update(checks=checks, admission='ADMITTED' if admitted else 'NOT_ADMITTED', admitted=admitted,
               not_evaluable=ne, zone=z, verdict=verdict, blocks=len(blocks), complete_blocks=len(done),
               pairs=len(pairs), min_pairs=min_pairs, est_frames=dict(A=sum(len(done[b]['est']) for pr in pairs
                                                                           for b in pr if done[b]['arm'] == ARM_A),
                                                                     B=sum(len(done[b]['est']) for pr in pairs
                                                                           for b in pr if done[b]['arm'] == ARM_B)),
               dt_us=dt, cpu_gpu_us=cpu, gpu_busy_us=gpu, slope=sl, scene=scene, speed=speeds, bda_scan=bda,
               draw_adjusted=dict(est=adj, slope=sl_adj, zone=z_adj, differs=z_adj != z),
               reading=reading, headroom=dict(share=fast_share, frames=fast_frames, dt_us=HEADROOM_DT_US,
                                              threshold=HEADROOM_SHARE),
               outliers=[dict(frame=n, dt_us=d, block=b, pair=b - b % 2) for n, d, b in outs],
               dropped_pairs=len(drops), first_population_frame=first_pop, host=host_verdict,
               skipped_before=len(skipped_out), skipped_before_max=max([f for f in skipped_out if f is not None],
                                                                       default=None),
               burn=dict(measure=measure, coverage=cover, late=len(burn['late']), late_lines=burn['late'][:8],
                         arm_lines=burn['arm'][:8], reject=burn['reject'], notsc=burn['notsc'],
                         selftest=burn['selftest'], cpu_bad=raw['burn_cpu_bad'],
                         s_seen=raw['burn_s_seen'], s_main=raw['burn_s_main'], m0_seen=raw['burn_m0_seen']),
               raw={k: raw[k] for k in BURN_KEYS}, skipped_draws=len(parsed['skipped']),
               skipped_in_window=len(skipped_in), markers=parsed['markers'][:10], pins=parsed['pins'], vk_env=vk_env)
    return res


def fmt(x, digits=1):
    if x is None:
        return '-'
    return ('%.' + str(digits) + 'f') % x


def format_report(res):
    out = []
    if res['draft']:
        out.append('DRAFT: unsealed scoring (pre-registration, hold and the pair floor not checked) - not a verdict')
    out.append('map122 tag %s  scorer %s  build %s' % (res['tag'], res['scorer_sha256'][:16],
                                                       res['build_sha256'][:16]))
    out.append('  scene %s; arm B burn=%s (code %s %s, dose %s us), arm A burn=0'
               % (res['level'], res['burn_value'], res['code'], res['prefix'], res['dose_us']))
    for k, v in res['checks'].items():
        out.append('  %-16s %s' % (k, 'ok' if v else 'FAIL'))
    out.append('  blocks %d complete %d pairs %d (floor %d); estimator frames A %d B %d'
               % (res['blocks'], res['complete_blocks'], res['pairs'], res['min_pairs'],
                  res['est_frames']['A'], res['est_frames']['B']))
    dt, sl, sp = res['dt_us'], res['slope'], res['speed']
    out.append('Delta dt_us (B - A) %s +- %s us (2SE, %d pairs); A %s B %s us'
               % (fmt(dt['delta']), fmt(dt['two_se']), res['pairs'], fmt(dt['A']), fmt(dt['B'])))
    out.append('SLOPE s = Delta / dose %s +- %s (interval %s .. %s); zones: superlinear s-2SE>%s, critical '
               's-2SE>%s and s+2SE>=%s, not critical s+2SE<%s'
               % (fmt(sl['s'], 3), fmt(sl['two_se'], 3), fmt(sl['lo'], 3), fmt(sl['hi'], 3), fmt(S_SUPER, 1),
                  fmt(S_CRIT_LO, 1), fmt(S_REACH, 1), fmt(S_FLAT_HI, 1)))
    ad = res['draw_adjusted']
    out.append('DRAW-ADJUSTED (report only): Delta %s +- %s us, slope %s +- %s, zone %s; Delta draws (B - A) %s +- %s%s'
               % (fmt(ad['est']['delta']), fmt(ad['est']['two_se']), fmt(ad['slope']['s'], 3),
                  fmt(ad['slope']['two_se'], 3), ad['zone'] or '-', fmt(ad['est']['draws_delta']),
                  fmt(ad['est']['draws_two_se']), '  DRAW-ADJUSTED ZONE DIFFERS' if ad['differs'] else ''))
    hr = res['headroom']
    out.append('reading %s: base-arm window share of dt_us < %d = %s over %d frames (HEADROOM at >= %s; ROADMAP s122 '
               'item 18 (c))' % (res['reading'], hr['dt_us'], fmt(hr['share'], 4), hr['frames'],
                                 fmt(hr['threshold'], 2)))
    if res['reading'] == 'HEADROOM':
        out.append('game speed: NOT QUOTED - on this scene the slope measures HEADROOM before the next vblank step, '
                   'not speed (ROADMAP s122 items 17 (d), 18 (c))')
    elif res['reading'] != 'SPEED':
        out.append('game speed: NOT QUOTED - the reading is NOT EVALUABLE (no base-arm window row in the '
                   'population)')
    else:
        out.append('game speed (16 667 / mean dt_us) A %s B %s (%s %% speed change under the dose)'
                   % (fmt(sp['A'], 4), fmt(sp['B'], 4), fmt(sp['change_rel_pct'], 2)))
    for name, key in (('cpu_gpu_us', 'cpu_gpu_us'), ('gpu_busy_us', 'gpu_busy_us')):
        e = res[key]
        out.append('Delta %s (B - A) %s +- %s us; A %s B %s us (report)'
                   % (name, fmt(e['delta']), fmt(e['two_se']), fmt(e['A']), fmt(e['B'])))
    b = res['burn']
    m, c = b['measure'], b['coverage']
    if m:
        out.append('dose measured: %s us a frame (want %s +-%s %%), %s us an armed unit over %d armings on %d B '
                   'frames; cpu/wall %s (%s codes ~%s by construction - printed diagnostics, not a verdict)'
                   % (fmt(m['per_frame_us']), fmt(DOSE_US, 0), fmt(100 * DOSE_TOL, 0), fmt(m['per_unit_us']),
                      m['n'], m['frames'], fmt(m['cpu_wall'], 3), m['kind'], fmt(m['cpu_wall_expect'], 2)))
    if c:
        out.append('coverage %s = %d%s' % (c['counter'], c['value'],
                                           '' if not c['role'] else ' (role %s = %d)' % (c['role'], c['role_value'])))
    out.append('burn lines: selftest %d, arm %s, late %d%s, rejected %d, no-TSC %d, burn_cpu_bad %d (must be 0)'
               % (b['selftest'], b['arm_lines'] or '-', b['late'],
                  '' if not b['late_lines'] else ' e.g. code=%d us=%.1f' % (b['late_lines'][0][0],
                                                                           b['late_lines'][0][1]),
                  b['reject'], b['notsc'], b['cpu_bad']))
    s = res['scene']
    out.append('scene: dt median %s us, %s; vblank %s; top %sx = %s %% => %s'
               % (fmt(s['dt_median']), ', '.join('%s %s' % (k, fmt(v, 3)) for k, v in s['ratios'].items()),
                  ', '.join('%dvb=%.1f%%' % (k, 100 * v) for k, v in s['vblank_shares'].items()) or '-',
                  s['vblank_top'], fmt(None if s['vblank_top_share'] is None else 100 * s['vblank_top_share']),
                  'PINCHED (>= %.0f %%: a saving smaller than the distance to the next step does not move FPS)'
                  % (100 * PINCH) if s['pinched'] else 'not pinched'))
    out.append('scene: rec_spin_us %s, draws %s, dispatches %s, submits %s, frames %d'
               % (fmt(s['rec_spin_us']), fmt(s['draws']), fmt(s['dispatches']), fmt(s['submits']), s['frames']))
    out.append('GPU-bound: %s' % ('n/a (not the GuestGpu arm - only code 1 can answer it)' if s['gpu_bound'] is None
                                  else ('yes (median gpu_busy/dt >= %.1f and GuestGpu not critical)' % GPU_BOUND
                                        if s['gpu_bound'] else 'no')))
    out.append('bda_scan A %s (%s) B %s (%s)' % (fmt(res['bda_scan']['A']), res['bda_scan']['A_regime'],
                                                 fmt(res['bda_scan']['B']), res['bda_scan']['B_regime']))
    for o in res['outliers']:
        out.append('OUTLIER frame n=%d dt_us=%d (>= %d): block %d, pair (%d, %d) dropped whole'
                   % (o['frame'], o['dt_us'], OUTLIER_US, o['block'], o['pair'], o['pair'] + 1))
    out.append('outlier pairs dropped %d (limit %d; more => the run is INVALID)'
               % (res['dropped_pairs'], MAX_OUTLIER_PAIRS))
    out.append('host events (hostdev_%s.txt): %s' % (res['tag'], res['host']))
    out.append('skipped draws: %d fatal (frame >= %s), %d before the population (largest frame %s)'
               % (res['skipped_in_window'], res['first_population_frame'], res['skipped_before'],
                  res['skipped_before_max']))
    out.append('not evaluable: %s' % (', '.join(res['not_evaluable']) or '-'))
    failed = [k for k, ok in res['checks'].items() if not ok]
    out.append('ADMISSION: %s%s' % (res['admission'], ' failed=' + ','.join(failed) if failed else ''))
    if not res['admitted']:
        out.append('REPORT OF A NOT_ADMITTED RUN - NOT TO BE QUOTED')
    out.append('VERDICT: %s slope=%s 2se=%s interval=%s..%s pairs=%d bda=%s reading=%s%s'
               % (res['verdict'], fmt(sl['s'], 3), fmt(sl['two_se'], 3), fmt(sl['lo'], 3), fmt(sl['hi'], 3),
                  res['pairs'], res['bda_scan']['A_regime'], res['reading'], ' DRAFT' if res['draft'] else ''))
    note = ''
    if res['reading'] == 'HEADROOM':
        note += (' HEADROOM: the slope here is the work the frame absorbs before it falls to the next vblank step, '
                 'never a speed (ROADMAP s122 items 17 (d), 18 (c)).')
    if res['bda_scan']['A_regime'] == 'OLD':
        note += (' BDA OLD: this scene\'s numbers are quoted only with the regime and never compared with those of '
                 'NEW scenes (ROADMAP s122 item 17 (e)).')
    out.append('CONSEQUENCE: %s%s' % (CONSEQUENCE[res['verdict']], note))
    return out


def plan_check(tag, plan):
    """(exit code, line) of the chain gate: 0 the tag's arm is sealed, 1 its value is not filled, 2 no PLAN entry."""
    global PLAN
    PLAN = dict(plan)
    v = arm_value(tag)
    if plan_of(tag) is None:
        return 2, 'map122: no PLAN entry for tag %s' % tag
    if v is None or code_dose(v)[0] not in CODE_GROUP:
        return 1, ('map122: the arm of tag %s is NOT sealed (PLAN burn=%r) - the lead has to record that constant '
                   'first; refusing' % (tag, v))
    return 0, 'map122: tag %s arm burn=%d (code %d, dose %d us) sealed' % ((tag, v) + code_dose(v))


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass
    if '--plan-check' in sys.argv:
        rc, text = plan_check(sys.argv[sys.argv.index('--plan-check') + 1], PLAN_DEFAULT)
        print(text)
        return rc
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    tag = sys.argv[sys.argv.index('--tag') + 1] if '--tag' in sys.argv else 'sky122'
    draft = '--draft' in sys.argv
    if plan_of(tag) is None and not draft:
        print('unknown tag %s (expected one of %s, or any tag with --draft)'
              % (tag, ', '.join(sorted(PLAN))))
        return 2
    res = evaluate(root, tag, draft=draft)
    print(NL.join(format_report(res)))
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] in ('CRITICAL', 'SUPERLINEAR', 'NOT_CRITICAL', 'NOT_RESOLVED') else 1


if __name__ == '__main__':
    sys.exit(main())
