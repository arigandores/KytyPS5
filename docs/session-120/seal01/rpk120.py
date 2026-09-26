"""Session 120, ROADMAP s0.1 "СЕССИЯ 120 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 2, 4, 5; design design120.md sections 2, 3, 5, 6
(with r1.md + r1_review.md RC1-RC11, r2.md + r2_review.md C1-C10, and the accepted deviations of
docs/session-120/impl_report.md: r2_s_* are SUBSETS of the class counters, w1 carries a full counter set).
Pre-registration pred/01_cen120.md; fixtures test_rpk120.py; mutants mut_rpk120.py; chain go120a.sh.

rpk120 scores the image-resolve package R of the sealed run cen120 (Sky Garden, build BUILD_SHA, 300-s hold, pinned,
KYTY_GPU_MARKERS=0, gates_base.txt, schedule SCHEDULE with KYTY_GATE_SCHEDULE_ABBA=1):
  arm P (0) = r1cen=2 r2cen=2 spcen=1 bindlap=1 pathlap=1 mutsite=1
  arm M (1) = r1cen=0 r2cen=1 spcen=0 bindlap=1 pathlap=1 mutsite=1
Members: R1 (texture-memo shape census, P arm) and R2 (stage image-block repeat census, M arm; the replay of P is
information only); package R = R1 + R2.

Admission (every check must hold, else NOT_ADMITTED; --draft skips ONLY the pre-registration checks, the hold and the
pair minimum):
  binary / installed_now   TAG.json binary_sha256 and the installed exe (from the home dir) are BUILD_SHA
  pinned                   env KYTY_GPU_CLOCK_PIN == '1' and exactly one `GpuClockPin:` line, mode 1
  env_exact / env_vk       KYTY_* env exactly ENV_EXPECT and meta schedule SCHEDULE; of VK_* only VK_ALLOWED
  hold / one_ok_attempt    hold_s == HOLD_S; exactly one attempt, outcome ok, hold_exit None
  prereg / prereg_sha      prereg.path is PRED_PATH; PRED_SHA / PRED_BYTES filled, the file matches them now, and
                           TAG.json prereg sha256 / bytes are PRED_SHA / PRED_BYTES (refused while they are None)
  gates_exact              gates_base.txt sha256 is GATES_SHA and TAG.json gates is its whitespace-normalised text
  gate_lines / arms        every `Gate:` / `GateArm:` line matches the ABBA schedule (arm by TEXT, never by counter)
  no_marker                no hang/failure marker in the log or stdout_TAG.txt
  no_skip_window           no `AsyncPipelines: skipped draw` inside a window (positions 10..88 of a block)
  streams                  every main row of every block window has its -draw and -x rows with every field read
  pairs                    >= MIN_PAIRS usable ABBA pairs (consecutive blocks 2k, 2k+1, both complete)
  idle                     pre_run.gpu_util_median <= IDLE_GPU_MAX
A NOT_ADMITTED run makes every member NOT_EVALUABLE (design120 s6) unless a member FAILs (correctness is a fact of
the run whatever its admission).

Estimator window: positions KEEP[0]..KEEP[1]-1 (10..88) of every block, draws > DRAWS_MIN.  Pairs: blocks (2k, 2k+1);
2SE from per-pair values (R1: the pair's P block, R2: its M block, package: the per-pair sum).  Identities, partitions
and bounds: on the window sums of positions 10..88 of every block (contiguous, so the flip's per-counter row skew
telescopes to the two window edges), NEAR (+-8 counts a block window: the design120 s4 row-skew rule, widened from
+-2 by ROADMAP s120 item 6; a persistent off-by-one per row gives >= 79 a window and still fails) for counters Added
by one operation and printed next to each other, FAR (max(256, 0.1 %), r1.md F2) for counters printed far apart or
on another line (measured edge skew in smk120: up to 740 counts a block window for r1_hn vs tex_hits).

Correctness over ALL rows of the run (every FrameTrace-x line, any frame, duplicates included) and every mismatch
line: R1 FAIL if sum r1_{w4,w8,d16}_bad > 0 or any `R1CenMismatch:`; R1 NOT_EVALUABLE if sum r1_incl, r1_xthr or any
r1_w1_* is nonzero.  R2 FAIL if sum (r2_bad + r2_bad_key) > 0 or any `R2Mismatch:` / `R2MismatchKey:`.

Verdict per member and package: FAIL > NOT_EVALUABLE > OPEN (point >= BAR_US) > CLOSED (upper + 2SE < BAR_US) >
NOT_OPENED.  R1: point = upper = C_R1 = max_T C_T.  R2: point C_pt (play), upper C_up (traced).  Package R:
R_pt = C_R1 + C_R2,pt, R_up = C_R1 + C_R2,up.  Every ns counter is divided by NS_PER_US exactly once.
Consequences (ROADMAP s120 item 4 addendum, recorded before the seal): one `CONSEQUENCE: <name>` line per member and
the package, then the summary `CONSEQUENCE:` line (last): FAIL if any member fails, else NOT_ADMITTED if not admitted,
else OPEN naming the OPEN member(s) (or R1+R2 together when only the package is OPEN) when any member or the package
is OPEN, else the package's own consequence (function summary_of).

    python C:/kyty/s120/rpk120.py [--root C:/kyty/s120] [--tag cen120|cen120r] [--draft] [--out <json>]
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
GATES_FILE = 'C:/kyty/s120/gates_base.txt'
GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'
PRED_PATH = 'C:/kyty/s120/pred/01_cen120.md'
PRED_SHA = 'd20cd3de41cb8e58634e7ac024c76338a51b4bfa33a6415b3cbabd148ab73849'  # pred/01_cen120.md, sealed (session 120 seal 01)
PRED_BYTES = 8483        # pred/01_cen120.md, sealed
HOLD_S = 300
PERIOD = 90
START = 1800
KEEP = (10, 89)
DRAWS_MIN = 3000
ABBA = (0, 1, 1, 0)
ARM_P = 0
ARM_M = 1
ARM_TEXT = ('r1cen=2 r2cen=2 spcen=1 bindlap=1 pathlap=1 mutsite=1',
            'r1cen=0 r2cen=1 spcen=0 bindlap=1 pathlap=1 mutsite=1')
MIN_PAIRS = 30
IDLE_GPU_MAX = 10
BAR_US = 500.0
NS_PER_US = 1000.0
# R2 pre-registered constants (design120 s3), ns
B_NS = 8.49
B_LO_NS = 5.0
T_PRIME_NS = 15.00 - 3.0
P_NS = 15.08
N0_NS = 2.0
LS_NS = 5.0
R_RESET_NS = 2.0
A_TR_NS = 1.2
PC_LO_NS = 25.0
PC_HI_NS = 90.0
# samplers: R1 (r1.md F3 with the self split of the review), R2 (the 1/8 pre-loop sample), pre/post (F4), resets (F7)
HIT_BAND = (0.10, 0.15)
POST_BAND = (0.45, 0.55)
FAST_BAND = (0.05, 0.075)
SELF_BAND = (0.012, 0.019)
R2_SMP_BAND = (0.10, 0.15)
PREPOST_MAX = 0.02
RESET_MAX_PCT = 25
# row skew (design120 s4 rule, NEAR widened from +-2 to +-8 counts a block window by ROADMAP s120 item 6;
# FAR = r1.md F2 tolerance)
SKEW_NEAR = 8
SKEW_FAR_ABS = 256
SKEW_FAR_PERMILLE = 1
# BDA regime labels (s112/s113: NEW ~52, OLD ~1066 scans a frame), reported only
BDA_NEW_MAX = 300
BDA_OLD_MIN = 600
NL = chr(10)
SCHEDULE = '90+1800:' + ARM_TEXT[0] + '|' + ARM_TEXT[1]
ENV_EXPECT = {
    'KYTY_FRAME_TRACE': 'lite',
    'KYTY_GPU_HANG_ABORT_S': '8',
    'KYTY_GATE_FILE': 'C:\\kyty\\s120\\gates.req',
    'KYTY_SAMPLE_GATE': 'C:\\kyty\\s120\\sample.req',
    'KYTY_QUEUE_TRACE': '1',
    'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden',
    'KYTY_GPU_CLOCK_PIN': '1',
    'KYTY_GPU_MARKERS': '0',
    'KYTY_GATE_SCHEDULE': SCHEDULE,
    'KYTY_GATE_SCHEDULE_ABBA': '1',
}
VK_ALLOWED = ('VK_SDK_PATH',)
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---')
SKIPPED_DRAW = b'AsyncPipelines: skipped draw'
R1_MISMATCH = re.compile(rb'R1CenMismatch:')
R2_MISMATCH = re.compile(rb'R2Mismatch(?:Key)?:')
R2_DIVERGE = re.compile(rb'R2Diverge:')

TABLES = ('w4', 'w8', 'd16')
R1_KEYS = ('r1_hn', 'r1_mn', 'r1_sn', 'r1_hit_ns', 'r1_hit_t', 'r1_miss_ns', 'r1_nost', 'r1_nost_ns', 'r1_rb_ns',
           'r1_rb_n', 'r1_rbf_ns', 'r1_rbf_n', 'r1_mp', 'r1_mp_ns',
           'r1_w4_q', 'r1_w4_qns', 'r1_w4_p', 'r1_w4_pns', 'r1_w4_lose', 'r1_w4_bad', 'r1_w4_rb', 'r1_w4_rbns',
           'r1_w4_pb_ns',
           'r1_w8_q', 'r1_w8_qns', 'r1_w8_p', 'r1_w8_pns', 'r1_w8_lose', 'r1_w8_bad', 'r1_w8_rb', 'r1_w8_rbns',
           'r1_w8_pb_ns',
           'r1_d16_q', 'r1_d16_qns', 'r1_d16_p', 'r1_d16_pns', 'r1_d16_bad', 'r1_d16_rb', 'r1_d16_rbns',
           'r1_w1_q', 'r1_w1_qns', 'r1_w1_p', 'r1_w1_pns', 'r1_w1_lose', 'r1_w1_bad', 'r1_w1_rb', 'r1_w1_rbns',
           'r1_pb0_ns', 'r1_pb_n', 'r1_am_n', 'r1_ham_ns', 'r1_ham_t', 'r1_sstale', 'r1_cold', 'r1_reset', 'r1_tagx',
           'r1_incl', 'r1_xthr', 'r1_self_h_ns', 'r1_self_h_n', 'r1_self_m_ns', 'r1_self_m_n', 'r1_self_s_ns',
           'r1_self_s_n')
R2_KEYS = ('r2_stg', 'r2_noimg', 'r2_big', 'r2_odd', 'r2_prog', 'r2_rep', 'r2_cl', 'r2_mx', 'r2_cl_ns', 'r2_mx_ns',
           'r2_ot_ns', 'r2_cl_sl', 'r2_cl_nul', 'r2_mx_sl', 'r2_mx_eq', 'r2_ot_sl', 'r2_s_cl_ns', 'r2_s_cl_sl',
           'r2_s_cl_nul', 'r2_s_mx_ns', 'r2_s_mx_sl', 'r2_s_ot_ns', 'r2_s_ot_sl', 'r2_sl_eq', 'r2_sl_hit',
           'r2_cl_lod', 'r2_cl_dcc', 'r2_cl_bc', 'r2_cl_tick', 'r2_cl_meta', 'r2_bad', 'r2_bad_key', 'r2_div',
           'r2_nul_ns', 'r2_nul_n', 'r2_wr_ns', 'r2_wr_n', 'r2_wo_ns', 'r2_wo_n', 'r2_st_ns', 'r2_st_n', 'r2_rm_ns',
           'r2_rm_sl', 'r2_rm_n')
MAIN_FIELDS = ('dt_us', 'cpu_gpu_us', 'draws', 'arm', 'blk')
DRAW_FIELDS = ('tex_hits', 'b_texn', 'bda_scan')
X_FIELDS = ('texmemo_collide', 'texmemo_empty', 'texmemo_stale', 'texfast_ok', 'texfast_no', 'tnull_hit',
            'tnull_miss', 'bl_prep_n', 'bl_res_us', 'bl_res_n') + R1_KEYS + R2_KEYS
KINDS = ((re.compile(rb'^FrameTrace: n=(\d+)'), 'main', MAIN_FIELDS),
         (re.compile(rb'^FrameTrace-draw: n=(\d+)'), 'draw', DRAW_FIELDS),
         (re.compile(rb'^FrameTrace-x: n=(\d+)'), 'x', X_FIELDS))
FIELD = re.compile(rb' (\w+)=(-?\d+)')
PIN = re.compile(rb'^GpuClockPin: mode (\d+)')
GATE = re.compile(rb'^Gate: (\w+)=(\d+) frame=(\d+)$')
GATE_ARM = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
R1_BAD_KEYS = ('r1_w4_bad', 'r1_w8_bad', 'r1_d16_bad')
R1_NE_KEYS = ('r1_incl', 'r1_xthr') + tuple(k for k in R1_KEYS if k.startswith('r1_w1_'))
R2_BAD_KEYS = ('r2_bad', 'r2_bad_key')
RAW_KEYS = R1_BAD_KEYS + R1_NE_KEYS + R2_BAD_KEYS + ('r1_reset',)
R2_RM_KEYS = ('r2_rm_ns', 'r2_rm_sl', 'r2_rm_n')
# identities on the per-block window sums (positions 10..88): name, arms, left keys, right keys, tolerance class
IDENTITIES = (
    ('r1_hn=tex_hits', (ARM_P,), ('r1_hn',), ('tex_hits',), 'far'),
    ('r1_mn=collide+empty', (ARM_P,), ('r1_mn',), ('texmemo_collide', 'texmemo_empty'), 'far'),
    ('r1_sn=stale', (ARM_P,), ('r1_sn',), ('texmemo_stale',), 'far'),
    ('b_texn=lookups+null', (ARM_P,), ('b_texn',), ('r1_hn', 'r1_mn', 'r1_sn', 'tnull_hit', 'tnull_miss'), 'far'),
    ('r1_pb_n=self_h_n', (ARM_P,), ('r1_pb_n',), ('r1_self_h_n',), 'near'),
    ('r2_stg=bl_prep_n', (ARM_P, ARM_M), ('r2_stg',), ('bl_prep_n',), 'far'),
    ('r2_slots=bl_res_n', (ARM_P, ARM_M), ('r2_cl_sl', 'r2_cl_nul', 'r2_mx_sl', 'r2_ot_sl'), ('bl_res_n',), 'far'),
    ('r2_rep=cl+mx', (ARM_P, ARM_M), ('r2_rep',), ('r2_cl', 'r2_mx'), 'near'),
    ('r2_wr+wo=nul', (ARM_P, ARM_M), ('r2_wr_n', 'r2_wo_n'), ('r2_nul_n',), 'near'),
    ('r2_rm_sl=s_cl', (ARM_P,), ('r2_rm_sl',), ('r2_s_cl_sl', 'r2_s_cl_nul'), 'far'),
)
R1_IDS = ('r1_hn=tex_hits', 'r1_mn=collide+empty', 'r1_sn=stale', 'b_texn=lookups+null', 'r1_pb_n=self_h_n')
# R2 class bounds (r2.md s10 fixture 4 with the impl deviations: r2_odd, no r2_cl_lru, r2_s_* subsets): left <= right
R2_BOUNDS = (
    ('rep<=prog', ('r2_rep',), ('r2_prog',)),
    ('prog<=img_stages', ('r2_prog', 'r2_noimg', 'r2_big', 'r2_odd'), ('r2_stg',)),
    ('mx_eq<=mx_sl', ('r2_mx_eq',), ('r2_mx_sl',)),
    ('sl_hit<=sl_eq', ('r2_sl_hit',), ('r2_sl_eq',)),
    ('R_slots<=sl_hit', ('r2_cl_sl', 'r2_cl_nul', 'r2_mx_eq'), ('r2_sl_hit',)),
    ('lod<=cl_sl', ('r2_cl_lod',), ('r2_cl_sl',)),
    ('dcc<=cl_sl', ('r2_cl_dcc',), ('r2_cl_sl',)),
    ('bc<=cl_sl', ('r2_cl_bc',), ('r2_cl_sl',)),
    ('tick<=cl', ('r2_cl_tick',), ('r2_cl',)),
    ('meta<=cl', ('r2_cl_meta',), ('r2_cl',)),
    ('s_cl_ns<=cl_ns', ('r2_s_cl_ns',), ('r2_cl_ns',)),
    ('s_cl_sl<=cl_sl', ('r2_s_cl_sl',), ('r2_cl_sl',)),
    ('s_cl_nul<=cl_nul', ('r2_s_cl_nul',), ('r2_cl_nul',)),
    ('s_mx_ns<=mx_ns', ('r2_s_mx_ns',), ('r2_mx_ns',)),
    ('s_mx_sl<=mx_sl', ('r2_s_mx_sl',), ('r2_mx_sl',)),
    ('s_ot_ns<=ot_ns', ('r2_s_ot_ns',), ('r2_ot_ns',)),
    ('s_ot_sl<=ot_sl', ('r2_s_ot_sl',), ('r2_ot_sl',)),
)
# ROADMAP s120 item 4 (the verdict rules and their consequences), quoted; English gloss after the quote
CONSEQUENCE = {
    'OPEN': ('OPEN - "точечный чистый потолок ≥ 500 мкс на кадр (пакет R: C_R1 + C_R2,pt) — открывается трек '
             'несущего члена, отгрузка — только по п. 2(в)"; "«Попало бы» — потолок, а не ускорение" (ROADMAP s120 '
             'item 4): a speed track opens for the carrying member(s); the prototype has its own verify gate and ships '
             'only by item 2(в) (sealed ABBA gain with the 2SE interval below 0, verify 0 mismatches, video without '
             'glitches).'),
    'CLOSED': ('CLOSED - "верхний X_up + 2SE < 500 (R: C_R1 + C_R2,up) — путь записывается исчерпанным на Sky Garden '
               'по правилу 0,5 мс" (ROADMAP s120 item 4).'),
    'NOT_OPENED': ('NOT_OPENED - "граница, записывается; допустим только повтор, решается при закрытии" (ROADMAP s120 '
                   'item 4).'),
    'FAIL': ('FAIL - "любой счётчик ошибок члена > 0 на ЛЮБОЙ строке или строка *Mismatch: (механизм неверен; ошибка '
             'R1/R2 значит ещё и возможный устаревший ответ СУЩЕСТВУЮЩЕЙ памяти — следующая сессия начинает с '
             'корректности)" (ROADMAP s120 item 4).'),
    'NOT_EVALUABLE': ('NOT_EVALUABLE - "провал допуска, тождеств, выборок, контролей, здравого смысла" (ROADMAP s120 '
                      'item 4): no ceiling is quoted.'),
    'NOT_ADMITTED': ('NOT_ADMITTED - "повтор cen120r — только при NOT_ADMITTED" (ROADMAP s120 item 4): admission, not '
                     'a verdict.'),
}


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


def ratio(num, den):
    return None if den == 0 else num / den


def two_se(values):
    """2 x the standard error of the per-pair values; None below two pairs or with an undefined pair."""
    if len(values) < 2 or any(v is None for v in values):
        return None
    return 2.0 * statistics.stdev(values) / math.sqrt(len(values))


def mean(values):
    return sum(values) / len(values) if values else None


def ksum(rows, keys):
    return {k: sum(r[k] for r in rows) for k in keys}


def within_far(res, ref):
    return 1000 * abs(res) <= max(1000 * SKEW_FAR_ABS, SKEW_FAR_PERMILLE * abs(ref))


def regime(v):
    if v is None:
        return None
    if v <= BDA_NEW_MAX:
        return 'NEW'
    if v >= BDA_OLD_MIN:
        return 'OLD'
    return 'MIXED'


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


def first_values(text):
    """name -> value of a gate text; the FIRST assignment of a name wins (gates.cpp FindAssignment, s111 trap)."""
    out = {}
    for pair in (text or '').split():
        if '=' in pair:
            k, v = pair.split('=', 1)
            out.setdefault(k, v)
    return out


def text_asserts(arm, text, g):
    """One observed arm text against gates_base values g: the text first, then gates_base, else absent."""
    a = first_values(text)

    def eff(name):
        return a.get(name, g.get(name))

    ok = eff('bindlap') == '1'
    ok = ok and eff('texmemo2') == '0'
    ok = ok and eff('texfastcheck') == '0'
    ok = ok and eff('m4baton') == '0'
    ok = ok and eff('fslean') == '0'
    ok = ok and eff('bindpack') in (None, '1')
    for name in ('bindwit', 'bindalt', 'blmove', 'bindfloor', 'cbmove'):
        ok = ok and eff(name) in (None, '0')
    ok = ok and eff('r1cen') == ('2' if arm == ARM_P else '0')
    ok = ok and eff('r2cen') == ('2' if arm == ARM_P else '1')
    return ok


def arm_asserts(texts, gates_text):
    """design120 s5 / r1_review RC10 / r2_review C7: every arm text seen in a `GateArm:` line (both arms present),
    with gates_base, gives bindlap=1, texmemo2=texfastcheck=m4baton=fslean=0, bindpack absent-or-1,
    bindwit/bindalt/blmove/bindfloor/cbmove absent-or-0, and r1cen 2|0, r2cen 2|1 (P|M)."""
    g = first_values(gates_text)
    if not texts.get(ARM_P) or not texts.get(ARM_M):
        return False
    return all(text_asserts(arm, t, g) for arm in (ARM_P, ARM_M) for t in texts[arm])


def parse_log(path, stdout_path=None):
    """One streaming pass over the log.  Rows by kind and frame (only the fields read; a row missing one is None);
    correctness counters over EVERY FrameTrace-x line; mismatch / marker / skipped-draw lines."""
    seen = {'main': {}, 'draw': {}, 'x': {}}
    dups = set()
    raw = {k: 0 for k in RAW_KEYS}
    pins, gate_arms, gate_lines, markers = [], [], [], []
    lines = {'r1_mismatch': 0, 'r2_mismatch': 0, 'r2_diverge': 0}
    skipped = []
    last_main = None
    with open(path, 'rb') as f:
        for line in f:
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
            if SKIPPED_DRAW in line:
                skipped.append(None if last_main is None else last_main + 1)
            if R1_MISMATCH.search(line):
                lines['r1_mismatch'] += 1
            if R2_MISMATCH.search(line):
                lines['r2_mismatch'] += 1
            if R2_DIVERGE.search(line):
                lines['r2_diverge'] += 1
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
    """Complete blocks (all PERIOD frames present, no duplicate, labels = the schedule), usable pairs, the estimator
    rows (positions KEEP, draws > DRAWS_MIN) and the identity rows (positions KEEP, all) of every complete block."""
    seen, dups = parsed['seen'], parsed['dups']

    def complete(n):
        return n not in dups and all(seen[k].get(n) is not None for k in seen)

    def row(n):
        return dict(seen['main'][n], **seen['draw'][n], **seen['x'][n])

    done = {}
    for b, arm in sorted(blocks.items()):
        frames = block_frames(b)
        if all(complete(n) and seen['main'][n]['arm'] == arm and seen['main'][n]['blk'] == b for n in frames):
            win = [row(n) for n in frames[KEEP[0]:KEEP[1]]]
            done[b] = dict(arm=arm, ident=win, est=[r for r in win if r['draws'] > DRAWS_MIN])
    pairs = [(b, b + 1) for b in range(0, max(blocks) + 1 if blocks else 0, 2) if b in done and b + 1 in done]
    return done, pairs


def streams_ok(parsed, blocks):
    """STREAMS_COMPLETE: every main row inside a block window has its -draw and -x rows with every field read (the
    last main row of the log is exempt)."""
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


def identity_failures(done, names):
    """Names of the identities that break on some block window (positions 10..88)."""
    bad = []
    for name, arms, left, right, cls in IDENTITIES:
        for b, blk in sorted(done.items()):
            if blk['arm'] not in arms or name not in names:
                continue
            lhs = sum(r[k] for r in blk['ident'] for k in left)
            rhs = sum(r[k] for r in blk['ident'] for k in right)
            res = lhs - rhs
            if cls == 'near':
                fine = abs(res) <= SKEW_NEAR
            else:
                fine = within_far(res, rhs)
            if not fine:
                bad.append('%s@%d' % (name, b))
    return bad


def ns_partition_failures(done):
    """r2_cl_ns + r2_mx_ns + r2_ot_ns against 1000 x bl_res_us (bl_res_us is truncated per row, so the ns sum lies
    in [0, 1000 per row] above it), FAR tolerance, every block window of both arms."""
    bad = []
    for b, blk in sorted(done.items()):
        ns = sum(r['r2_cl_ns'] + r['r2_mx_ns'] + r['r2_ot_ns'] for r in blk['ident'])
        ref = 1000 * sum(r['bl_res_us'] for r in blk['ident'])
        res = ns - ref
        top = res - 1000 * len(blk['ident'])
        if (res < 0 and not within_far(res, ref)) or (top > 0 and not within_far(top, ref)):
            bad.append('r2_ns=bl_res@%d' % b)
    return bad


# ------------------------------------------------------------------------------------------------ R1 (design120 s2)
def r1_terms(s, nf):
    """Net ceiling per table on P-arm window sums s over nf frames.  Returns the terms (ns per frame -> us once);
    ok False where a denominator is zero."""
    out = dict(nf=nf, ok=False)
    t_hit = ratio(s['r1_hit_ns'], s['r1_hit_t'])
    t_miss = ratio(s['r1_mp_ns'], s['r1_mp'])
    t_fast = ratio(s['r1_rbf_ns'], s['r1_rbf_n'])
    t_ham = ratio(s['r1_ham_ns'], s['r1_ham_t'])
    pre = s['r1_mn'] - s['r1_mp']
    look = s['r1_hn'] + s['r1_mn'] + s['r1_sn']
    out.update(t_hit=t_hit, t_miss=t_miss, t_fast=t_fast, t_ham=t_ham, lookups=None if nf == 0 else look / nf,
               nost=None if nf == 0 else s['r1_nost'] / nf, t_nost=ratio(s['r1_nost_ns'], s['r1_nost']))
    if None in (t_hit, t_miss, t_fast, t_ham) or pre == 0 or s['r1_mn'] == 0 or s['r1_pb_n'] == 0 or nf == 0:
        return out
    tables = {}
    for t in TABLES:
        t_t = ratio(s['r1_%s_pns' % t], s['r1_%s_p' % t])
        if t_t is None:
            return out
        w = s['r1_%s_q' % t] * s['r1_mn'] / pre
        a = w * (t_t - t_hit)
        l_ = 0.0 if t == 'd16' else s['r1_%s_lose' % t] * max(0.0, min(t_t, t_miss) - t_hit)
        r = s['r1_%s_rbns' % t] - s['r1_%s_rb' % t] * t_fast
        e = max(0.0, t_ham - t_hit) * s['r1_am_n'] * w / s['r1_mn']
        p = 0.0 if t == 'd16' else look * max(0.0, (s['r1_%s_pb_ns' % t] - s['r1_pb0_ns']) / s['r1_pb_n'])
        t_pre = ratio(s['r1_%s_qns' % t], s['r1_%s_q' % t])
        tables[t] = dict(W=w / nf, t_T=t_t, A=a / nf / NS_PER_US, L=l_ / nf / NS_PER_US, R=r / nf / NS_PER_US,
                         E=e / nf / NS_PER_US, P=p / nf / NS_PER_US,
                         C=(a - l_ + r + e - p) / nf / NS_PER_US, C_noE=(a - l_ + r - p) / nf / NS_PER_US,
                         warm_ns=None if t_pre is None else t_pre - t_t)
    best = max(TABLES, key=lambda t: tables[t]['C'])
    out.update(ok=True, tables=tables, argmax=best, C_R1=tables[best]['C'])
    return out


def r1_controls(done, pairs_p, est_p, est_m):
    """Samplers (F3 + the pb/self identity), bounds (F5), pre/post agreement (F4), arming (F1) and M-arm zeros."""
    fails = []
    s = ksum(est_p, R1_KEYS + ('texfast_ok', 'texfast_no'))
    look = s['r1_hn'] + s['r1_mn'] + s['r1_sn']
    selfn = s['r1_self_h_n'] + s['r1_self_m_n'] + s['r1_self_s_n']
    for name, num, den, band in (('hit', s['r1_hit_t'], s['r1_hn'], HIT_BAND),
                                 ('post', s['r1_mp'], s['r1_mn'], POST_BAND),
                                 ('fast', s['r1_rbf_n'], s['texfast_ok'], FAST_BAND),
                                 ('self', selfn, look, SELF_BAND)):
        v = ratio(num, den)
        if v is None or v < band[0] or v > band[1]:
            fails.append('sampler_' + name)
    for t in TABLES:
        if s['r1_%s_q' % t] + s['r1_%s_p' % t] > s['r1_mn']:
            fails.append('bound_%s_qp' % t)
        if s['r1_%s_pns' % t] > s['r1_mp_ns']:
            fails.append('bound_%s_pns' % t)
        if t != 'd16' and s['r1_%s_lose' % t] > s['r1_hn']:
            fails.append('bound_%s_lose' % t)
        if s['r1_%s_rb' % t] > s['r1_%s_q' % t] + s['r1_%s_p' % t]:
            fails.append('bound_%s_rb' % t)
    if s['r1_rb_n'] > s['texfast_no']:
        fails.append('bound_rb_n')
    for t in TABLES:
        diffs = []
        for b in pairs_p:
            bs = ksum(done[b]['est'], ('r1_mn', 'r1_mp', 'r1_%s_q' % t, 'r1_%s_p' % t))
            rq = ratio(bs['r1_%s_q' % t], bs['r1_mn'] - bs['r1_mp'])
            rp = ratio(bs['r1_%s_p' % t], bs['r1_mp'])
            diffs.append(None if rq is None or rp is None else rq - rp)
        se2 = two_se(diffs)
        if se2 is None or abs(mean(diffs)) > max(se2, PREPOST_MAX):
            fails.append('prepost_' + t)
    for k in ('r1_hn', 'r1_mn', 'r1_hit_t', 'r1_mp'):
        if not est_p or any(r[k] <= 0 for r in est_p):
            fails.append('armed_' + k)
    sm = ksum(est_m, R1_KEYS)
    if any(sm[k] != 0 for k in R1_KEYS):
        fails.append('m_leak')
    return fails


# ------------------------------------------------------------------------------------------------ R2 (design120 s3)
def r2_terms(s, nf, sp=None):
    """Ceilings on M-arm window sums s over nf frames (r2_s_* are SUBSETS of the class counters); sp: P-arm window
    sums for the replay proxy C_rp (information).  ns per frame -> us once; ok False where a denominator is 0."""
    out = dict(nf=nf, ok=False)
    z = ratio(s['r2_nul_ns'], s['r2_nul_n'])
    w_rep = ratio(s['r2_wr_ns'], s['r2_wr_n'])
    w_oth = ratio(s['r2_wo_ns'], s['r2_wo_n'])
    st_bar = ratio(s['r2_st_ns'], s['r2_st_n'])
    su = s['r2_cl_sl'] - s['r2_s_cl_sl']
    zu = s['r2_cl_nul'] - s['r2_s_cl_nul']
    out.update(z_bar=z, w_rep=w_rep, w_oth=w_oth, st_bar=st_bar, dcc_share=ratio(s['r2_cl_dcc'], s['r2_cl_sl']))
    if None in (z, w_rep, w_oth, st_bar) or su + zu == 0 or nf == 0:
        return out
    S = s['r2_cl_sl'] / nf
    Z = s['r2_cl_nul'] / nf
    L = s['r2_cl_lod'] / nf
    if S + Z == 0:
        return out
    rep = s['r2_rep'] / nf
    nonrep = (s['r2_stg'] - s['r2_noimg'] - s['r2_big'] - s['r2_odd'] - s['r2_rep']) / nf
    t_star = (s['r2_cl_ns'] - s['r2_s_cl_ns']) * (s['r2_cl_sl'] + s['r2_cl_nul']) / (su + zu) / nf
    W = (w_rep - z) * rep + (w_oth - z) * nonrep
    ST = (st_bar - z) * nonrep
    c_up = t_star - B_LO_NS * (S + Z) + R_RESET_NS * (S + Z) - W - ST
    c_up_b = t_star - B_NS * (S + Z) + R_RESET_NS * (S + Z) - W - ST
    c_pt_tr = t_star - ((B_NS + T_PRIME_NS) * S + (B_NS + N0_NS) * Z + LS_NS * L) - W - ST
    c_pt = t_star - ((B_NS + T_PRIME_NS) * S + (B_NS + N0_NS) * Z + LS_NS * L) - W - ST - A_TR_NS * (2 * S + Z)
    c_lo = t_star - ((B_NS + T_PRIME_NS + P_NS) * S + (B_NS + N0_NS) * Z + LS_NS * L) - W - ST - A_TR_NS * (2 * S + Z)
    p_c = t_star / (S + Z)
    c_ext = c_pt + s['r2_mx_eq'] / nf * (p_c - B_NS - T_PRIME_NS)
    s_slots = s['r2_s_cl_sl'] + s['r2_s_cl_nul']
    first_touch = None if s_slots == 0 else (s['r2_cl_ns'] - s['r2_s_cl_ns']) / (su + zu) - s['r2_s_cl_ns'] / s_slots
    c_rp = None
    k_rp = None
    if sp is not None:
        zp = ratio(sp['r2_nul_ns'], sp['r2_nul_n'])
        if zp is not None and sp['r2_rm_sl'] != 0:
            per_slot = (sp['r2_rm_ns'] - zp * sp['r2_rm_n']) / sp['r2_rm_sl']
            c_rp = (per_slot * (S + Z) - W - ST) / NS_PER_US
            k_rp = p_c - sp['r2_rm_ns'] / sp['r2_rm_sl']
    out.update(ok=True, S=S, Z=Z, L=L, rep=rep, nonrep=nonrep, T_star=t_star / NS_PER_US, W=W / NS_PER_US,
               ST=ST / NS_PER_US, p_c=p_c, C_up=c_up / NS_PER_US, C_pt=c_pt / NS_PER_US, C_lo=c_lo / NS_PER_US,
               C_ext=c_ext / NS_PER_US, C_rp=c_rp, K_rp=k_rp, first_touch_ns=first_touch,
               C_up_B849=c_up_b / NS_PER_US, C_pt_traced=c_pt_tr / NS_PER_US,
               K_rp_ok=None if k_rp is None else k_rp >= B_NS)
    return out


def r2_bound_failures(est, arm_name):
    s = ksum(est, R2_KEYS)
    bad = []
    for name, left, right in R2_BOUNDS:
        lhs = sum(s[k] for k in left)
        rhs = sum(s[k] for k in right)
        if lhs > rhs and not within_far(lhs - rhs, rhs):
            bad.append('bound_%s@%s' % (name, arm_name))
    return bad


def r2_controls(done, est_p, est_m, terms):
    fails = []
    sm = ksum(est_m, R2_KEYS)
    sp = ksum(est_p, R2_KEYS)
    if sm['r2_stg'] <= 0 or sp['r2_stg'] <= 0:
        fails.append('armed_stg')
    if any(sm[k] != 0 for k in R2_RM_KEYS):
        fails.append('m_replay')
    if sp['r2_rm_sl'] <= 0:
        fails.append('armed_replay')
    for name, s in (('P', sp), ('M', sm)):
        v = ratio(s['r2_nul_n'], s['r2_stg'] - s['r2_noimg'] - s['r2_big'])
        if v is None or v < R2_SMP_BAND[0] or v > R2_SMP_BAND[1]:
            fails.append('sampler_r2@' + name)
    fails += r2_bound_failures(est_p, 'P')
    fails += r2_bound_failures(est_m, 'M')
    if terms['ok']:
        if not PC_LO_NS <= terms['p_c'] <= PC_HI_NS:
            fails.append('sanity_pc')
        if not terms['C_lo'] <= terms['C_pt'] <= terms['C_up']:
            fails.append('sanity_order')
    return fails


# ------------------------------------------------------------------------------------------------ verdicts (s6)
def verdict(fail, not_evaluable, point, upper, se2):
    if fail:
        return 'FAIL'
    if not_evaluable or point is None or upper is None or se2 is None:
        return 'NOT_EVALUABLE'
    if point >= BAR_US:
        return 'OPEN'
    if upper + se2 < BAR_US:
        return 'CLOSED'
    return 'NOT_OPENED'


def summary_of(admitted, r1_fail, r2_fail, r1_v, r2_v, pk_v):
    """The summary consequence (ROADMAP s120 item 4 addendum): FAIL > NOT_ADMITTED > OPEN (any member or the package
    OPEN; names the OPEN members, 'R1+R2 (together)' when only the package is) > the package's own verdict."""
    open_m = [n for n, v in (('R1', r1_v), ('R2', r2_v)) if v == 'OPEN']
    if r1_fail or r2_fail:
        summary = 'FAIL'
    elif not admitted:
        summary = 'NOT_ADMITTED'
    elif open_m or pk_v == 'OPEN':
        summary = 'OPEN'
    else:
        summary = pk_v
    carrying = '+'.join(open_m) if open_m else ('R1+R2 (together)' if pk_v == 'OPEN' else '')
    return dict(verdict=summary, carrying=carrying, open_members=open_m)


def pred_checks(meta, draft, pred_sha, pred_bytes):
    """(prereg, prereg_sha): True in --draft; else the sealed constants must be filled and match the file now."""
    if draft:
        return True, True
    prereg = meta.get('prereg') or {}
    path_ok = str(prereg.get('path') or '').replace('\\', '/') == PRED_PATH
    if not pred_sha or not pred_bytes or not Path(PRED_PATH).is_file():
        return path_ok, False
    data = Path(PRED_PATH).read_bytes()
    sha_ok = (hashlib.sha256(data).hexdigest() == pred_sha and len(data) == pred_bytes
              and prereg.get('sha256') == pred_sha and prereg.get('bytes') == pred_bytes)
    return path_ok, sha_ok


def evaluate(root=ROOT, tag=TAG, draft=False, installed_sha=None, min_pairs=None, pred_sha=None, pred_bytes=None,
             gates_file=GATES_FILE):
    """Admission, both members, the package, their consequences; every term.  installed_sha None = hash INSTALLED;
    pred_sha / pred_bytes None = PRED_SHA / PRED_BYTES; min_pairs None = MIN_PAIRS (skipped in --draft)."""
    min_pairs = MIN_PAIRS if min_pairs is None else min_pairs
    pred_sha = PRED_SHA if pred_sha is None else pred_sha
    pred_bytes = PRED_BYTES if pred_bytes is None else pred_bytes
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
    prereg_ok, prereg_sha_ok = pred_checks(meta, draft, pred_sha, pred_bytes)
    skipped_in = [f for f in parsed['skipped'] if skip_in_window(f, blocks)]
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
        gate_lines=gate_lines_ok(parsed['gate_lines'], blocks),
        arms=arms_fine,
        no_marker=not parsed['markers'],
        no_skip_window=not skipped_in,
        streams=streams_ok(parsed, blocks),
        pairs=draft or len(pairs) >= min_pairs,
        idle=idle_ok(meta))
    admitted = all(checks.values())
    texts = {}
    for g in parsed['gate_arms']:
        if g is not None and g[0] in (ARM_P, ARM_M):
            texts.setdefault(g[0], []).append(g[6])
    asserts_ok = arm_asserts(texts, base_text)

    # ---- R1: P blocks of the pairs; a P block with a census reset inside positions 10..88 is dropped (r1.md F7)
    p_blocks = [b for pr in pairs for b in pr if done[b]['arm'] == ARM_P]
    m_blocks = [b for pr in pairs for b in pr if done[b]['arm'] == ARM_M]
    reset_blocks = [b for b in p_blocks if sum(r['r1_reset'] for r in done[b]['ident']) > 0]
    r1_pairs = [pr for pr in pairs if not any(b in reset_blocks for b in pr)]
    r1_p = [b for pr in r1_pairs for b in pr if done[b]['arm'] == ARM_P]
    est_p1 = [r for b in r1_p for r in done[b]['est']]
    est_p = [r for b in p_blocks for r in done[b]['est']]
    est_m = [r for b in m_blocks for r in done[b]['est']]
    r1 = r1_terms(ksum(est_p1, X_FIELDS + DRAW_FIELDS), len(est_p1))
    r1_ne = []
    if not admitted:
        r1_ne.append('not_admitted')
    if not asserts_ok:
        r1_ne.append('arm_asserts')
    if any(parsed['raw'][k] != 0 for k in R1_NE_KEYS):
        r1_ne.append('incl_xthr_w1')
    if 100 * len(reset_blocks) > RESET_MAX_PCT * len(p_blocks):
        r1_ne.append('resets')
    r1_ne += identity_failures(done, R1_IDS)
    r1_ne += r1_controls(done, r1_p, est_p1, est_m)
    if not r1['ok']:
        r1_ne.append('zero_den')
    r1_pair_vals = []
    for pr in r1_pairs:
        pb = [b for b in pr if done[b]['arm'] == ARM_P][0]
        t = r1_terms(ksum(done[pb]['est'], X_FIELDS + DRAW_FIELDS), len(done[pb]['est']))
        r1_pair_vals.append(t['tables'][r1['argmax']]['C'] if t['ok'] and r1['ok'] else None)
    r1_se2 = two_se(r1_pair_vals)
    r1_fail = sum(parsed['raw'][k] for k in R1_BAD_KEYS) > 0 or parsed['lines']['r1_mismatch'] > 0
    r1_point = r1.get('C_R1')
    r1_v = verdict(r1_fail, bool(r1_ne), r1_point, r1_point, r1_se2)

    # ---- R2: M blocks (T*, S, Z, L, W, ST from the M arm only); the P replay is information
    r2 = r2_terms(ksum(est_m, R2_KEYS), len(est_m), ksum(est_p, R2_KEYS))
    r2_ne = []
    if not admitted:
        r2_ne.append('not_admitted')
    if not asserts_ok:
        r2_ne.append('arm_asserts')
    r2_ne += identity_failures(done, tuple(name for name, *_ in IDENTITIES if name.startswith('r2_')))
    r2_ne += ns_partition_failures(done)
    r2_ne += r2_controls(done, est_p, est_m, r2)
    if not r2['ok']:
        r2_ne.append('zero_den')
    r2_pair_up, r2_pair_pt = [], []
    for pr in pairs:
        mb = [b for b in pr if done[b]['arm'] == ARM_M][0]
        t = r2_terms(ksum(done[mb]['est'], R2_KEYS), len(done[mb]['est']))
        r2_pair_up.append(t['C_up'] if t['ok'] else None)
        r2_pair_pt.append(t['C_pt'] if t['ok'] else None)
    r2_se2 = two_se(r2_pair_up)
    r2_fail = sum(parsed['raw'][k] for k in R2_BAD_KEYS) > 0 or parsed['lines']['r2_mismatch'] > 0
    r2_v = verdict(r2_fail, bool(r2_ne), r2.get('C_pt'), r2.get('C_up'), r2_se2)

    # ---- package R: per-pair sums over the pairs both members use
    pk_vals = []
    for i, pr in enumerate(pairs):
        if pr in r1_pairs:
            a = r1_pair_vals[r1_pairs.index(pr)]
            pk_vals.append(None if a is None or r2_pair_up[i] is None else a + r2_pair_up[i])
    pk_se2 = two_se(pk_vals)
    pk_point = None if r1_point is None or r2.get('C_pt') is None else r1_point + r2['C_pt']
    pk_upper = None if r1_point is None or r2.get('C_up') is None else r1_point + r2['C_up']
    pk_v = verdict(r1_fail or r2_fail, bool(r1_ne or r2_ne), pk_point, pk_upper, pk_se2)
    summary = summary_of(admitted, r1_fail, r2_fail, r1_v, r2_v, pk_v)

    # ---- report: BDA regime, the P-M price (never a verdict input)
    price = {}
    for key in ('dt_us', 'cpu_gpu_us'):
        diffs = []
        for pr in pairs:
            pb = [b for b in pr if done[b]['arm'] == ARM_P][0]
            mb = [b for b in pr if done[b]['arm'] == ARM_M][0]
            mp_, mm_ = mean([r[key] for r in done[pb]['est']]), mean([r[key] for r in done[mb]['est']])
            diffs.append(None if mp_ is None or mm_ is None else mp_ - mm_)
        price[key] = dict(pair_mean=mean([d for d in diffs if d is not None]), two_se=two_se(diffs),
                          P=mean([r[key] for r in est_p]), M=mean([r[key] for r in est_m]))
    bda = dict(P=mean([r['bda_scan'] for r in est_p]), M=mean([r['bda_scan'] for r in est_m]))
    bda.update(P_regime=regime(bda['P']), M_regime=regime(bda['M']))
    res.update(checks=checks, verdict='ADMITTED' if admitted else 'NOT_ADMITTED', admitted=admitted,
               blocks=len(blocks), complete_blocks=len(done), pairs=len(pairs), r1_pairs=len(r1_pairs),
               reset_blocks=reset_blocks, est_frames=dict(P=len(est_p), M=len(est_m), R1=len(est_p1)),
               raw=parsed['raw'], lines=parsed['lines'], skipped_draws=len(parsed['skipped']),
               skipped_in_window=len(skipped_in), markers=parsed['markers'][:10], pins=parsed['pins'],
               vk_env=vk_env, arm_asserts=asserts_ok,
               R1=dict(terms=r1, verdict=r1_v, point=r1_point, upper=r1_point, two_se=r1_se2, fail=r1_fail,
                       not_evaluable=r1_ne, pair_values=r1_pair_vals),
               R2=dict(terms=r2, verdict=r2_v, point=r2.get('C_pt'), upper=r2.get('C_up'), two_se=r2_se2,
                       fail=r2_fail, not_evaluable=r2_ne, pair_up=r2_pair_up, pair_pt=r2_pair_pt),
               R=dict(verdict=pk_v, point=pk_point, upper=pk_upper, two_se=pk_se2, pair_values=pk_vals),
               summary=summary, price=price, bda_scan=bda)
    return res


def fmt(x, digits=1):
    if x is None:
        return '-'
    return ('%.' + str(digits) + 'f') % x


def consequence(name, v, res, extra=''):
    if v == 'FAIL':
        return 'CONSEQUENCE: %s %s' % (name, CONSEQUENCE['FAIL'])
    if not res['admitted']:
        return 'CONSEQUENCE: %s %s' % (name, CONSEQUENCE['NOT_ADMITTED'])
    return 'CONSEQUENCE: %s %s%s' % (name, CONSEQUENCE[v], extra)


def format_report(res):
    out = []
    if res['draft']:
        out.append('DRAFT: unsealed scoring (pre-registration, hold and pair minimum not checked) - not a verdict')
    out.append('rpk120 tag %s  scorer %s  build %s' % (res['tag'], res['scorer_sha256'][:16], res['build_sha256'][:16]))
    for k, v in res['checks'].items():
        out.append('  %-15s %s' % (k, 'ok' if v else 'FAIL'))
    out.append('  blocks %d complete %d pairs %d (R1 %d, reset blocks %s); estimator frames P %d M %d'
               % (res['blocks'], res['complete_blocks'], res['pairs'], res['r1_pairs'], res['reset_blocks'],
                  res['est_frames']['P'], res['est_frames']['M']))
    t1 = res['R1']['terms']
    out.append('R1 t_hit %s t_miss %s t_fast %s t_ham %s ns; lookups %s a frame; no-store key misses %s a frame at %s ns'
               % (fmt(t1.get('t_hit'), 2), fmt(t1.get('t_miss'), 2), fmt(t1.get('t_fast'), 2),
                  fmt(t1.get('t_ham'), 2), fmt(t1.get('lookups'), 1), fmt(t1.get('nost'), 1),
                  fmt(t1.get('t_nost'), 1)))
    for t in TABLES:
        if t1.get('ok'):
            e = t1['tables'][t]
            out.append('R1 %-3s W %s t_T %s ns | A %s L %s R %s E %s P %s -> C %s us (without E %s) | warming %s ns'
                       % (t, fmt(e['W']), fmt(e['t_T']), fmt(e['A']), fmt(e['L']), fmt(e['R']), fmt(e['E']),
                          fmt(e['P']), fmt(e['C']), fmt(e['C_noE']), fmt(e['warm_ns'])))
    t2 = res['R2']['terms']
    out.append('R2 (M) S %s Z %s L %s | z %s w_rep %s w_oth %s st %s ns | T* %s W %s ST %s us | p_c %s ns'
               % (fmt(t2.get('S')), fmt(t2.get('Z')), fmt(t2.get('L')), fmt(t2.get('z_bar'), 2),
                  fmt(t2.get('w_rep'), 2), fmt(t2.get('w_oth'), 2), fmt(t2.get('st_bar'), 2),
                  fmt(t2.get('T_star')), fmt(t2.get('W')), fmt(t2.get('ST')), fmt(t2.get('p_c'))))
    out.append('R2 C_up %s C_pt %s C_lo %s us | C_rp %s C_ext %s us (information) | K_rp %s ns | first touch %s ns'
               % (fmt(t2.get('C_up')), fmt(t2.get('C_pt')), fmt(t2.get('C_lo')), fmt(t2.get('C_rp')),
                  fmt(t2.get('C_ext')), fmt(t2.get('K_rp')), fmt(t2.get('first_touch_ns'), 2)))
    out.append('R2 information: C_up at B=8.49 %s us, C_pt traced %s us, DCC-lock share of clean slots %s, replay proxy %s'
               % (fmt(t2.get('C_up_B849')), fmt(t2.get('C_pt_traced')), fmt(t2.get('dcc_share'), 4),
                  '-' if t2.get('K_rp_ok') is None else ('kept' if t2['K_rp_ok'] else 'rejected (K_rp < B)')))
    out.append('correctness (all rows): %s; lines %s' % (', '.join('%s=%d' % kv for kv in res['raw'].items()),
                                                         ', '.join('%s=%d' % kv for kv in res['lines'].items())))
    out.append('not evaluable R1 %s; R2 %s' % (res['R1']['not_evaluable'] or '-', res['R2']['not_evaluable'] or '-'))
    for key, p in res['price'].items():
        out.append('price P-M %s %s +- %s (pairs); P %s M %s (report only)'
                   % (key, fmt(p['pair_mean']), fmt(p['two_se']), fmt(p['P']), fmt(p['M'])))
    out.append('bda_scan P %s (%s) M %s (%s)' % (fmt(res['bda_scan']['P']), res['bda_scan']['P_regime'],
                                                 fmt(res['bda_scan']['M']), res['bda_scan']['M_regime']))
    if not res['admitted']:
        out.append('REPORT OF A NOT_ADMITTED RUN - NOT TO BE QUOTED')
    failed = [k for k, v in res['checks'].items() if not v]
    out.append('VERDICT: %s%s%s' % (res['verdict'], ' failed=' + ','.join(failed) if failed else '',
                                    ' DRAFT' if res['draft'] else ''))
    for name, key in (('R1', 'R1'), ('R2', 'R2')):
        m = res[key]
        out.append('MEMBER %s: %s point=%s upper=%s 2se=%s' % (name, m['verdict'], fmt(m['point']), fmt(m['upper']),
                                                             fmt(m['two_se'])))
    p = res['R']
    out.append('PACKAGE R: %s point=%s upper=%s 2se=%s' % (p['verdict'], fmt(p['point']), fmt(p['upper']),
                                                          fmt(p['two_se'])))
    ext = t2.get('C_ext')
    per_slot = (' Per-slot variant unmeasured (C_ext %s us >= %s): the CLOSE covers the whole-block per-stage-type '
                'R2 only.' % (fmt(ext), fmt(BAR_US))) if ext is not None and ext >= BAR_US else ''
    out.append(consequence('R1', res['R1']['verdict'], res,
                           ' Table %s.' % t1['argmax'] if res['R1']['verdict'] == 'OPEN' else ''))
    out.append(consequence('R2', res['R2']['verdict'], res, per_slot if res['R2']['verdict'] == 'CLOSED' else ''))
    sm = res['summary']
    carry = ''
    if p['verdict'] == 'OPEN':
        carry = ' Open members: %s.' % sm['carrying']
    elif p['verdict'] == 'CLOSED':
        carry = per_slot
    if p['verdict'] != 'OPEN' and sm['verdict'] == 'OPEN':
        carry += ' Superseded for the OPEN member(s) %s by the summary line.' % sm['carrying']
    out.append(consequence('R', p['verdict'], res, carry))
    tail = ''
    if sm['verdict'] == 'OPEN':
        tail = ' Open: %s.' % sm['carrying']
    elif sm['verdict'] == 'CLOSED':
        tail = per_slot
    out.append('CONSEQUENCE: %s%s' % (CONSEQUENCE[sm['verdict']], tail))
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    tag = sys.argv[sys.argv.index('--tag') + 1] if '--tag' in sys.argv else TAG
    draft = '--draft' in sys.argv
    if tag not in TAGS and not draft:
        print('unknown tag %s (expected one of %s; any tag only with --draft)' % (tag, ', '.join(TAGS)))
        return 2
    res = evaluate(root, tag, draft=draft)
    print(NL.join(format_report(res)))
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] == 'ADMITTED' else 1


if __name__ == '__main__':
    sys.exit(main())
