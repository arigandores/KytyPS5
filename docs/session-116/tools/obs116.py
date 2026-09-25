"""Session 116, ROADMAP §0.1 "СЕССИЯ 116 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 2-4 (step (2) of item 1) - DRAFT, NOT SEALED
(pre-registration pred/01_obs116.md; fixtures test_obs116.py; mutants mut_obs116.py; chain go116a.sh).  Amended after
the independent pre-seal check (item 3: BLOCKER emit identity, MAJOR span medians, cross-checks, prereg hash, VK_*)
and by item 4 (the per-row emit median check removed: chance refusals 2-4 %, redundant with the total).

obs116 is an OBSERVATION: one Sky Garden entry on the installed build d3a981a2 (git 7c73f26), 300-s hold, pinned
(KYTY_GPU_CLOCK_PIN=1), KYTY_GPU_MARKERS=0, KYTY_GPU_WALL=1, no recording, gates gates_obs116.txt (gates_base.txt with
mutsite=0 -> mutsite=1 replaced IN PLACE, pathlap=1 appended).  It splits the CPU time of the GuestGpu thread per frame
into phases for the choice of the next speed track (ROADMAP 116 item 1 step 3).  The verdict is ADMITTED or
NOT_ADMITTED only; the REPORT never carries a verdict on speed and its ranges are report-only.

Admission (every check must hold, else NOT_ADMITTED):
  binary / installed_now  TAG.json binary_sha256 and the installed exe are BUILD_SHA
  pinned                  env KYTY_GPU_CLOCK_PIN == '1' and exactly one `GpuClockPin:` line, and it is mode 1
  env_exact               the KYTY_* part of env is exactly ENV_EXPECT (lite, pin, markers 0, wall 1, the s116 gate
                          file; hence no KYTY_REC, no schedule, no checkpoints, no GC shift, no KYTY_GPU_TIME ...)
  env_vk                  of the VK_* part of env only VK_ALLOWED (VK_SDK_PATH) may appear
  hold                    TAG.json hold_s == HOLD_S
  one_ok_attempt          exactly one attempt, outcome ok, hold_exit None
  prereg                  TAG.json prereg.path is PRED_PATH (the run claims this pre-registration)
  prereg_sha              TAG.json prereg.sha256 (enter_scene.py reads it before the emulator starts) equals the
                          sha256 of PRED_PATH on disk now: the pre-registration was not edited after the run began
  gates_exact             the whitespace-normalised gate text hashes to GATES_SHA (gates_obs116.txt)
  gate_mutsite            exactly one `mutsite=` token in the gate text, and it is `mutsite=1`
  gate_pathlap            exactly one `pathlap=` token in the gate text, and it is `pathlap=1`
                          (both hold whenever gates_exact does; they name the two gates the measurement needs)
  gate_lines              the `Gate:` lines of the log are exactly `Gate: mutsite=1 frame=F` and `Gate: pathlap=1
                          frame=F'` (either order), F and F' < the stable frame: no toggle inside the scene
  wall_logged             exactly one `GpuWall:` line, and it is `GpuWall: mode 1`
  no_marker               no failure marker (MARKERS, as check115) in the log or in stdout_TAG.txt
  rows                    >= MIN_ROWS complete scene rows (n >= the stable frame): every n has one FrameTrace, one
                          FrameTrace-draw and one FrameTrace-x line, each carrying every field used; no n incomplete
                          or repeated
  armed                   over the scene rows sum mh_draws, mh_disp_n, pl_proc_n, pl_em_n, gw_proc_n all > 0
  id_hold_n               |sum a_hold_n - sum (mh_n + mh_disp_n)| <= ID_HOLD_TOL (session 69: MutexMark and HoldLap
                          count the same draw/dispatch holds; the flip reads the counters one by one, so neighbouring
                          counters are skewed by the draws that run between two reads)
  id_emit_n               |sum pl_em_n - sum mh_draws| <= ID_EMIT_TOL (counters 578 HoldDraws and 1043 PathEmN are
                          read far apart: the per-row skew reaches +-33 and a window sum 60 on pl96a; over >= MIN_ROWS
                          rows the tolerance still catches a steady drift of 256 / 6000 = 0.043 a row)
  proc_n                  |sum pl_proc_n - sum gw_proc_n| <= PROC_N_TOL (two spans around the same GuestGpu::Process)
  proc_wall               100 * sum pl_proc_ns <= PROC_WALL_PCT * sum gw_proc_ns (pl_proc lies inside gw_proc)
  hold_cover              sum a_hold_us > 0 and sum hold / sum a_hold_us in [HOLD_COVER_LO_PCT, HOLD_COVER_HI_PCT] %
  idle                    pre_run.gpu_util_median <= IDLE_GPU_MAX
  (the three cross-checks compare integer totals, so their edges are exact)

UNITS (videoOut.cpp `named` table, third field): a_hold_us, a_wait_us, mh_*_us print in MICROseconds (micros=true);
every pl_*_ns, gw_*_ns and flip_rsv_wait_ns prints RAW NANOseconds (micros=false) and is divided by 1000 here, once,
into a key without the `_ns` suffix (pl_proc_ns -> pl_proc, us).  Main line: dt_us (host wall between flips),
cpu_gpu_us (GuestGpu thread CPU cycle time, QueryThreadCycleTime), draws, dispatches, gpu_busy_us, semwait_gpu_us,
prio_us (a Scope: reads 0 in lite), prios.  FrameTrace-draw: bda_scan.

Report (per scene row = per flip; mean, run sum, and the per-row median EXCEPT for SPAN_KEYS; share =
sum(x)/sum(cpu_gpu_us); per_op = sum(x)/sum(draws + dispatches); per_unit = sum(x)/sum(own population)):
  hold       = mh_pro + mh_rt + mh_prog + mh_bind + mh_emit + mh_tail + mh_disp   (render mutex, GuestGpu, wall)
  emit_split = sum pl_em_* (the pathlap chain inside mh_emit)
  named      = pl_pref + pl_eop + pl_bar + pl_sub + pl_gc + pl_cmd              (outside the mutex, inside Process)
  outside    = pl_proc - a_hold_us - a_wait_us  (a_hold_us holds draws and dispatches only: MutexMark sits in
               renderDraw.cpp/renderCompute.cpp, never at the present sites, swapchain.cpp:765)
  residue    = outside - named;   residue_noflip = residue - gw_flip (R_WAIT_FLIP_DONE is a PM4 handler in Process)
  residue_s96 = pl_proc - (a_hold_us - mh_pres_us) - named  (session 96's sealed form, shown for comparison only)
  attributed = hold + a_wait_us + named;   remainder = cpu_gpu_us - attributed  (CPU minus WALL: signed)
  thread_unwalled = dt_us - (gw_idle + gw_blk + gw_proc + gw_cmd)
  offcpu = dt_us - cpu_gpu_us;   offcpu_unexplained = offcpu - (gw_idle + gw_blk + gw_flip)
  ops = draws + dispatches;   cpu_per_op = cpu_gpu_us / ops (per row)
SPAN_KEYS (charged whole when the span ends, so a flip can carry a neighbour's span): every pl_*, gw_*, flip_rsv_wait,
semwait_gpu_us, prio_us and every key derived from them - only their mean and run sum are reported, their per-row
median is None (choice: dropped, not computed over blocks).
BDA regime: median bda_scan of the scene rows -> NEW (<= BDA_NEW_MAX), OLD (>= BDA_OLD_MIN), else UNCLEAR.

    python C:/kyty/s116/obs116.py [--root C:/kyty/s116] [--tag obs116|obs116r] [--out <json>]
"""
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = 'C:/kyty/s116'
TAG = 'obs116'
TAGS = ('obs116', 'obs116r')
BUILD_SHA = 'd3a981a23fc1c5df651eef2a93ff1f02a8bffd04416adea2fd5cd2218e290f64'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
MIN_ROWS = 6000
HOLD_S = 300
ID_HOLD_TOL = 16
ID_EMIT_TOL = 256
PROC_N_TOL = 16
PROC_WALL_PCT = 101
HOLD_COVER_LO_PCT = 98
HOLD_COVER_HI_PCT = 102
IDLE_GPU_MAX = 10
GATES_SHA = '678fed0972d9a97f53159883ba80eec867c27be4429de325b12f22fa4441aa1b'
PRED_PATH = 'C:/kyty/s116/pred/01_obs116.md'
NL = chr(10)
BDA_NEW_MAX = 300
BDA_OLD_MIN = 600
ENV_EXPECT = {
    'KYTY_FRAME_TRACE': 'lite',
    'KYTY_GPU_HANG_ABORT_S': '8',
    'KYTY_GATE_FILE': 'C:\\kyty\\s116\\gates.req',
    'KYTY_SAMPLE_GATE': 'C:\\kyty\\s116\\sample.req',
    'KYTY_QUEUE_TRACE': '1',
    'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden',
    'KYTY_GPU_CLOCK_PIN': '1',
    'KYTY_GPU_MARKERS': '0',
    'KYTY_GPU_WALL': '1',
}
VK_ALLOWED = ('VK_SDK_PATH',)
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
           b'asyncpipelines: skipped draw')

MAIN_FIELDS = ('dt_us', 'cpu_gpu_us', 'draws', 'dispatches', 'gpu_busy_us', 'semwait_gpu_us', 'prio_us', 'prios')
DRAW_FIELDS = ('bda_scan',)
US_FIELDS = ('mh_pro_us', 'mh_rt_us', 'mh_prog_us', 'mh_bind_us', 'mh_emit_us', 'mh_tail_us', 'mh_disp_us',
             'a_hold_us', 'a_wait_us', 'mh_pres_us', 'mh_pres_wait_us')
NS_FIELDS = ('pl_proc_ns', 'pl_pref_ns', 'pl_eop_ns', 'pl_bar_ns', 'pl_sub_ns', 'pl_gc_ns', 'pl_cmd_ns', 'pl_look_ns',
             'pl_em_vtx_ns', 'pl_em_rt_ns', 'pl_em_pipe_ns', 'pl_em_com_ns', 'pl_em_rec_ns', 'pl_em_rest_ns',
             'gw_idle_ns', 'gw_blk_ns', 'gw_flip_ns', 'gw_proc_ns', 'gw_cmd_ns', 'flip_rsv_wait_ns')
COUNT_FIELDS = ('mh_n', 'mh_draws', 'mh_disp_n', 'a_hold_n', 'mh_pres_n', 'pl_proc_n', 'pl_pref_n', 'pl_eop_n',
                'pl_bar_n', 'pl_sub_n', 'pl_gc_n', 'pl_cmd_n', 'pl_look_n', 'pl_em_n', 'gw_idle_n', 'gw_blk_n',
                'gw_flip_n', 'gw_proc_n', 'gw_cmd_n', 'flip_rsv_wait_n')
X_FIELDS = US_FIELDS + NS_FIELDS + COUNT_FIELDS
HOLD_PARTS = ('mh_pro_us', 'mh_rt_us', 'mh_prog_us', 'mh_bind_us', 'mh_emit_us', 'mh_tail_us', 'mh_disp_us')
EMIT_PARTS = ('pl_em_vtx', 'pl_em_rt', 'pl_em_pipe', 'pl_em_com', 'pl_em_rec', 'pl_em_rest')
NAMED_PARTS = ('pl_pref', 'pl_eop', 'pl_bar', 'pl_sub', 'pl_gc', 'pl_cmd')
WALL_PARTS = ('gw_idle', 'gw_blk', 'gw_proc', 'gw_cmd')
# Time keys of the report, in us a flip, in print order; the count keys follow them.
TIME_KEYS = (('dt_us', 'cpu_gpu_us', 'gpu_busy_us') + HOLD_PARTS + ('hold', 'a_hold_us', 'a_wait_us', 'mh_pres_us',
             'mh_pres_wait_us') + EMIT_PARTS + ('emit_split',) + ('pl_proc',) + NAMED_PARTS
             + ('named', 'outside', 'residue', 'residue_noflip', 'residue_s96', 'attributed', 'remainder', 'pl_look')
             + WALL_PARTS + ('gw_flip', 'thread_unwalled', 'offcpu', 'offcpu_unexplained', 'flip_rsv_wait',
                             'semwait_gpu_us', 'prio_us'))
CNT_KEYS = ('draws', 'dispatches', 'ops', 'cpu_per_op', 'bda_scan', 'prios') + COUNT_FIELDS
# Charged whole when the span (or the wait) ENDS: a Process slice of up to ~58 ms lands in the flip in which it ended,
# so a per-row median of these keys, or of any key built from them, is not a frame statistic.  Mean and sum only.
SPAN_KEYS = (EMIT_PARTS + ('emit_split', 'pl_proc') + NAMED_PARTS + ('pl_look',) + WALL_PARTS
             + ('gw_flip', 'named', 'outside', 'residue', 'residue_noflip', 'residue_s96', 'attributed', 'remainder',
                'thread_unwalled', 'offcpu_unexplained', 'flip_rsv_wait', 'semwait_gpu_us', 'prio_us'))
# per_unit: a time key divided by the population it was counted on.
POP = {'mh_pro_us': 'mh_draws', 'mh_rt_us': 'mh_draws', 'mh_prog_us': 'mh_draws', 'mh_bind_us': 'mh_draws',
       'mh_emit_us': 'mh_draws', 'mh_tail_us': 'mh_n', 'mh_disp_us': 'mh_disp_n', 'a_hold_us': 'a_hold_n',
       'a_wait_us': 'a_hold_n', 'mh_pres_us': 'mh_pres_n', 'mh_pres_wait_us': 'mh_pres_n', 'pl_proc': 'pl_proc_n',
       'pl_pref': 'pl_pref_n', 'pl_eop': 'pl_eop_n', 'pl_bar': 'pl_bar_n', 'pl_sub': 'pl_sub_n', 'pl_gc': 'pl_gc_n',
       'pl_cmd': 'pl_cmd_n', 'pl_look': 'pl_look_n', 'pl_em_vtx': 'pl_em_n', 'pl_em_rt': 'pl_em_n',
       'pl_em_pipe': 'pl_em_n', 'pl_em_com': 'pl_em_n', 'pl_em_rec': 'pl_em_n', 'pl_em_rest': 'pl_em_n',
       'emit_split': 'pl_em_n', 'gw_idle': 'gw_idle_n', 'gw_blk': 'gw_blk_n', 'gw_flip': 'gw_flip_n',
       'gw_proc': 'gw_proc_n', 'gw_cmd': 'gw_cmd_n', 'flip_rsv_wait': 'flip_rsv_wait_n', 'prio_us': 'prios'}
# Report-only ranges of the MEAN, us a flip (counts: a flip; cpu_per_op: us).  Never a verdict.
PREDICTIONS = {
    'dt_us': (29000, 40000),
    'cpu_gpu_us': (28000, 38000),
    'draws': (4500, 6000),
    'dispatches': (240, 300),
    'cpu_per_op': (5.0, 7.5),
    'a_hold_us': (22000, 34000),
    'mh_bind_us': (6000, 14000),
    'mh_emit_us': (5000, 10000),
    'mh_prog_us': (2500, 7500),
    'mh_disp_us': (1200, 4000),
    'mh_rt_us': (400, 2000),
    'emit_split': (5000, 10000),
    'pl_pref': (0, 400),
    'named': (300, 3000),
    'residue': (0, 4000),
    'remainder': (-2000, 4000),
    'offcpu': (0, 4000),
}
CAVEATS = (
    '(a) instruments on: mutsite ~0.10 ms a frame (session 69, +0.312 % +- 0.294 % cpu/draw), pathlap +362.9 +- 80.8 '
    'us a flip on top of mutsite=1 (session 96, pl96a), KYTY_GPU_WALL not priced (a few timestamps a submission) - '
    'levels are instrumented levels and compare with no uninstrumented run',
    '(b) every phase is a WALL interval (rdtsc) of the GuestGpu thread; cpu_gpu_us is its CPU cycle time - shares of '
    'cpu_gpu_us are wall over CPU, and remainder / residue are signed',
    '(c) mh_pres_us and mh_pres_wait_us are BOTH threads (PrepareFrame/PrepareBlankFrame at the flip packet on '
    'GuestGpu, inside residue; Present on the present thread) - not separable by these counters; pl_look runs on the '
    'guest submit thread and is in no sum',
    '(d) the named outside spans are taken as disjoint from each other and from the render-mutex holds (session 96 '
    'design; PathSpan refuses to arm inside a hold, the reverse is not checked here)',
    '(e) one entry, one launch state (BDA regime reported); no A/B, nothing here is a speed effect',
    '(f) PathSpan, WallSpan and PathLap marks (every pl_*, gw_*) and the waits flip_rsv_wait, semwait_gpu_us, prio_us '
    'add their whole interval to the flip in which they END - a Process slice can last ~58 ms (pl96a) - so a flip can '
    'carry a neighbour\'s span; for these keys and every key built from them (emit_split, named, outside, residue*, '
    'attributed, remainder, thread_unwalled, offcpu_unexplained) only means and run sums are reported, no per-row '
    'medians',
    '(g) per_unit of mh_pro/mh_rt/mh_prog/mh_bind/mh_emit divides by mh_draws, which excludes the ~20 draws a frame that '
    'return early (session 71) although their holds up to the return sit in those phases - a slight overstatement per '
    'draw; mh_tail is divided by mh_n',
    '(h) prio_us is timed by a Scope (commandScheduler.cpp:682) and reads 0 in a lite run (its count prios is live); '
    'semwait_gpu_us (masterSemaphore.cpp:92/152) and flip_rsv_wait (videoOut.cpp:526-530) are live',
)


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def is_marker(line):
    low = line.lower()
    return any(k in low for k in MARKERS)


def idle_ok(meta):
    v = (meta.get('pre_run') or {}).get('gpu_util_median')
    return isinstance(v, (int, float)) and v <= IDLE_GPU_MAX


LINE_MAIN = re.compile(rb'^FrameTrace: n=(\d+)')
LINE_DRAW = re.compile(rb'^FrameTrace-draw: n=(\d+)')
LINE_X = re.compile(rb'^FrameTrace-x: n=(\d+)')
FIELD = re.compile(rb' (\w+)=(-?\d+)')
PIN = re.compile(rb'^GpuClockPin: mode (\d+)')
GATE = re.compile(rb'^Gate: (\w+)=(\d+) frame=(\d+)$')
KINDS = ((LINE_MAIN, 'main', MAIN_FIELDS), (LINE_DRAW, 'draw', DRAW_FIELDS), (LINE_X, 'x', X_FIELDS))


def row_values(m, dr, x):
    """One scene row in us (times) and plain counts; the derived keys of the docstring."""
    v = {k: float(m[k]) for k in MAIN_FIELDS}
    v['bda_scan'] = float(dr['bda_scan'])
    v.update((k, float(x[k])) for k in US_FIELDS)
    v.update((k[:-3], x[k] / 1000.0) for k in NS_FIELDS)
    v.update((k, float(x[k])) for k in COUNT_FIELDS)
    v['ops'] = v['draws'] + v['dispatches']
    v['cpu_per_op'] = v['cpu_gpu_us'] / v['ops'] if v['ops'] > 0 else None
    v['hold'] = sum(v[k] for k in HOLD_PARTS)
    v['emit_split'] = sum(v[k] for k in EMIT_PARTS)
    v['named'] = sum(v[k] for k in NAMED_PARTS)
    v['outside'] = v['pl_proc'] - v['a_hold_us'] - v['a_wait_us']
    v['residue'] = v['outside'] - v['named']
    v['residue_noflip'] = v['residue'] - v['gw_flip']
    v['residue_s96'] = v['pl_proc'] - (v['a_hold_us'] - v['mh_pres_us']) - v['named']
    v['attributed'] = v['hold'] + v['a_wait_us'] + v['named']
    v['remainder'] = v['cpu_gpu_us'] - v['attributed']
    v['thread_unwalled'] = v['dt_us'] - sum(v[k] for k in WALL_PARTS)
    v['offcpu'] = v['dt_us'] - v['cpu_gpu_us']
    v['offcpu_unexplained'] = v['offcpu'] - (v['gw_idle'] + v['gw_blk'] + v['gw_flip'])
    return v


def bda_label(median):
    if median is None:
        return 'UNKNOWN'
    if median <= BDA_NEW_MAX:
        return 'NEW'
    if median >= BDA_OLD_MIN:
        return 'OLD'
    return 'UNCLEAR'


def report(values, stable):
    """The report of the complete scene rows `values` (list of row_values dicts).  Numbers only, no verdict."""
    if not values:
        return None
    sums = {}
    for k in TIME_KEYS + CNT_KEYS:
        col = [v[k] for v in values if v[k] is not None]
        sums[k] = sum(col)
    cpu = sums['cpu_gpu_us']
    ops = sums['ops']
    fields = {}
    for k in TIME_KEYS + CNT_KEYS:
        col = [v[k] for v in values if v[k] is not None]
        entry = dict(unit='us' if k in TIME_KEYS else ('us/op' if k == 'cpu_per_op' else 'count'),
                     mean=sum(col) / len(col) if col else None,
                     sum=sums[k],
                     median=statistics.median(col) if col else None)
        if k in SPAN_KEYS:
            entry['median'] = None
        if k in TIME_KEYS:
            entry['share_cpu'] = sums[k] / cpu if cpu else None
            entry['per_op'] = sums[k] / ops if ops else None
            pop = POP.get(k)
            if pop is not None:
                entry['per_unit'] = sums[k] / sums[pop] if sums[pop] else None
                entry['unit_pop'] = pop
        fields[k] = entry
    fields['cpu_per_op']['sum_ratio'] = cpu / ops if ops else None
    consistency = dict(
        hold_over_a_hold=sums['hold'] / sums['a_hold_us'] if sums['a_hold_us'] else None,
        emit_split_over_mh_emit=sums['emit_split'] / sums['mh_emit_us'] if sums['mh_emit_us'] else None,
        pl_proc_over_gw_proc=sums['pl_proc'] / sums['gw_proc'] if sums['gw_proc'] else None,
        mh_n_over_draws=sums['mh_n'] / sums['draws'] if sums['draws'] else None,
        mh_disp_n_over_dispatches=sums['mh_disp_n'] / sums['dispatches'] if sums['dispatches'] else None,
        a_hold_n_minus_mh=sums['a_hold_n'] - sums['mh_n'] - sums['mh_disp_n'],
        pl_em_n_minus_mh_draws=sums['pl_em_n'] - sums['mh_draws'],
        pl_proc_n_minus_gw_proc_n=sums['pl_proc_n'] - sums['gw_proc_n'])
    bda_med = fields['bda_scan']['median']
    predictions = {}
    for k, (lo, hi) in PREDICTIONS.items():
        mean = fields[k]['mean']
        predictions[k] = dict(lo=lo, hi=hi, mean=mean, in_range=mean is not None and lo <= mean <= hi)
    return dict(n_rows=len(values), stable_frame=stable, span_s=sums['dt_us'] / 1e6, fields=fields,
                consistency=consistency, bda=dict(median=bda_med, label=bda_label(bda_med)),
                predictions=predictions, caveats=list(CAVEATS))


def evaluate(root=ROOT, tag=TAG, installed_sha=None, min_rows=None, pred_sha=None):
    """ADMITTED iff every check of the docstring holds, else NOT_ADMITTED; the report is computed either way (a
    NOT_ADMITTED report is not to be quoted).  installed_sha / pred_sha: None = hash the installed exe / PRED_PATH."""
    min_rows = MIN_ROWS if min_rows is None else min_rows
    res = dict(scorer_sha256=sha_file(__file__), build_sha256=BUILD_SHA, tag=tag)
    meta = json.loads((Path(root) / (tag + '.json')).read_text(encoding='utf-8'))
    env = meta.get('env') or {}
    kyty_env = {k: v for k, v in env.items() if k.startswith('KYTY_')}
    vk_env = sorted(k for k in env if k.startswith('VK_'))
    atts = meta.get('attempts') or []
    ok_att = [a for a in atts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]
    stable = ok_att[-1].get('stable_frame') if ok_att else None
    gates = ' '.join((meta.get('gates') or '').split())
    tokens = gates.split()
    mut_tokens = [t for t in tokens if t.startswith('mutsite=')]
    path_tokens = [t for t in tokens if t.startswith('pathlap=')]
    prereg = meta.get('prereg') or {}
    prereg_path = str(prereg.get('path') or '')
    pins = []
    walls = []
    gate_lines = []
    markers = []
    seen = {'main': {}, 'draw': {}, 'x': {}}
    dups = set()
    with open(Path(root) / ('log_%s.txt' % tag), 'rb') as f:
        for line in f:
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
            if line.startswith(b'GpuClockPin:'):
                mp = PIN.match(line)
                pins.append(int(mp.group(1)) if mp else -1)
            if line.startswith(b'GpuWall:'):
                walls.append(line.rstrip())
            if line.startswith(b'Gate: '):
                gate_lines.append(line.rstrip())
            if stable is None or not line.startswith(b'FrameTrace'):
                continue
            for regex, kind, names in KINDS:
                m = regex.match(line)
                if m is None:
                    continue
                n = int(m.group(1))
                if n >= stable:
                    got = dict(FIELD.findall(line, m.end()))
                    rec = {k: int(got[k.encode()]) for k in names if k.encode() in got}
                    if n in seen[kind]:
                        dups.add(n)
                    seen[kind][n] = rec if len(rec) == len(names) else None
                break
    so = Path(root) / ('stdout_%s.txt' % tag)
    if so.is_file():
        for line in open(so, 'rb'):
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
    ns = set(seen['main']) | set(seen['draw']) | set(seen['x'])
    good = sorted(n for n in ns if n not in dups and all(seen[k].get(n) is not None for k in seen))
    missing = len(ns) - len(good)
    values = [row_values(seen['main'][n], seen['draw'][n], seen['x'][n]) for n in good]
    tot = {k: sum(seen['x'][n][k] for n in good) for k in COUNT_FIELDS}
    raw = {k: sum(seen['x'][n][k] for n in good) for k in ('pl_proc_ns', 'gw_proc_ns', 'a_hold_us') + HOLD_PARTS}
    hold_raw = sum(raw[k] for k in HOLD_PARTS)
    parsed_gates = [GATE.match(g) for g in gate_lines]
    gate_pairs = sorted((g.group(1).decode(), g.group(2).decode()) for g in parsed_gates if g)
    gate_frames_ok = stable is not None and all(g is not None and int(g.group(3)) < stable for g in parsed_gates)
    if installed_sha is None:
        installed_sha = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    if pred_sha is None:
        pred_sha = sha_file(PRED_PATH) if Path(PRED_PATH).is_file() else None
    checks = dict(
        binary=meta.get('binary_sha256') == BUILD_SHA,
        installed_now=installed_sha == BUILD_SHA,
        pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and pins == [1],
        env_exact=kyty_env == ENV_EXPECT,
        env_vk=all(k in VK_ALLOWED for k in vk_env),
        hold=meta.get('hold_s') == HOLD_S,
        one_ok_attempt=len(atts) == 1 and len(ok_att) == 1,
        prereg=prereg_path.replace('\\', '/') == PRED_PATH,
        prereg_sha=pred_sha is not None and prereg.get('sha256') == pred_sha,
        gates_exact=hashlib.sha256(gates.encode('utf-8')).hexdigest() == GATES_SHA,
        gate_mutsite=mut_tokens == ['mutsite=1'],
        gate_pathlap=path_tokens == ['pathlap=1'],
        gate_lines=gate_pairs == [('mutsite', '1'), ('pathlap', '1')] and gate_frames_ok,
        wall_logged=walls == [b'GpuWall: mode 1'],
        no_marker=not markers,
        rows=len(good) >= min_rows and missing == 0,
        armed=(tot['mh_draws'] > 0 and tot['mh_disp_n'] > 0 and tot['pl_proc_n'] > 0 and tot['pl_em_n'] > 0
               and tot['gw_proc_n'] > 0),
        id_hold_n=abs(tot['a_hold_n'] - tot['mh_n'] - tot['mh_disp_n']) <= ID_HOLD_TOL,
        id_emit_n=abs(tot['pl_em_n'] - tot['mh_draws']) <= ID_EMIT_TOL,
        proc_n=abs(tot['pl_proc_n'] - tot['gw_proc_n']) <= PROC_N_TOL,
        proc_wall=100 * raw['pl_proc_ns'] <= PROC_WALL_PCT * raw['gw_proc_ns'],
        hold_cover=(raw['a_hold_us'] > 0 and 100 * hold_raw >= HOLD_COVER_LO_PCT * raw['a_hold_us']
                    and 100 * hold_raw <= HOLD_COVER_HI_PCT * raw['a_hold_us']),
        idle=idle_ok(meta))
    res.update(checks=checks, stable_frame=stable, scene_rows=len(good), missing_rows=missing, dup_rows=len(dups),
               markers=markers[:10], pins=pins, gate_lines=[g.decode('utf-8', 'replace') for g in gate_lines],
               walls=[w.decode('utf-8', 'replace') for w in walls], vk_env=vk_env, totals=tot, raw_totals=raw,
               prereg_sha256=prereg.get('sha256'), pred_sha256_now=pred_sha, report=report(values, stable))
    res['verdict'] = 'ADMITTED' if all(checks.values()) else 'NOT_ADMITTED'
    return res


def fmt(x, digits=1):
    if x is None:
        return '-'
    return ('%.' + str(digits) + 'f') % x


def format_report(res):
    """Human-readable lines of res (checks, then the report).  Report-only; no speed verdict anywhere."""
    out = ['obs116 tag %s  scorer %s  build %s' % (res['tag'], res['scorer_sha256'][:16], res['build_sha256'][:16])]
    for k, v in res['checks'].items():
        out.append('  %-16s %s' % (k, 'ok' if v else 'FAIL'))
    rep = res['report']
    if rep is None:
        out.append('REPORT: no complete scene rows')
    else:
        if res['verdict'] != 'ADMITTED':
            out.append('REPORT OF A NOT_ADMITTED RUN - NOT TO BE QUOTED')
        out.append('REPORT (report only, no verdict on speed): %d scene rows from frame %s, %.1f s, BDA %s (median '
                   'bda_scan %s); median "-" on a span key: not reported, caveat (f)'
                   % (rep['n_rows'], rep['stable_frame'], rep['span_s'], rep['bda']['label'],
                      fmt(rep['bda']['median'], 0)))
        out.append('  %-20s %10s %10s %12s %8s %9s %10s  %s' % ('key', 'mean', 'median', 'sum', '%cpu', 'us/op',
                                                               'us/unit', 'unit'))
        for k in TIME_KEYS:
            e = rep['fields'][k]
            share = None if e['share_cpu'] is None else 100.0 * e['share_cpu']
            out.append('  %-20s %10s %10s %12s %8s %9s %10s  %s' % (k, fmt(e['mean']), fmt(e['median']),
                                                                    fmt(e['sum'], 0), fmt(share, 2),
                                                                    fmt(e['per_op'], 3), fmt(e.get('per_unit'), 3),
                                                                    e.get('unit_pop', '')))
        for k in CNT_KEYS:
            e = rep['fields'][k]
            out.append('  %-20s %10s %10s %12s  (%s)' % (k, fmt(e['mean'], 3), fmt(e['median'], 3), fmt(e['sum'], 0),
                                                        e['unit']))
        out.append('  cpu_per_op as a ratio of sums: %s us' % fmt(rep['fields']['cpu_per_op']['sum_ratio'], 4))
        out.append('  consistency: ' + ', '.join('%s=%s' % (k, fmt(v, 4) if isinstance(v, float) else v)
                                                 for k, v in rep['consistency'].items()))
        out.append('  ranges (report only): ' + ', '.join('%s %s [%s, %s] %s' % (k, fmt(p['mean']), p['lo'], p['hi'],
                                                                                 'in' if p['in_range'] else 'OUT')
                                                          for k, p in rep['predictions'].items()))
        for c in rep['caveats']:
            out.append('  caveat ' + c)
    out.append('VERDICT: %s' % res['verdict'])
    return out


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    tag = sys.argv[sys.argv.index('--tag') + 1] if '--tag' in sys.argv else TAG
    if tag not in TAGS:
        print('unknown tag %s (expected one of %s)' % (tag, ', '.join(TAGS)))
        return 2
    res = evaluate(root, tag)
    print(NL.join(format_report(res)))
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] == 'ADMITTED' else 1


if __name__ == '__main__':
    sys.exit(main())
