"""Session 121: fixtures for shp121.py - synthetic FrameTrace / -draw / -x / GateArm / Gate logs (LF, built in memory),
one fixture per admission check, per correctness key, per arming / identity / regime rule at its edge (at the threshold
and one past it), per window edge, per estimator term, per verify-result field, the fixtures S1-S15 of texmemo8.md
section 8.4 (S4 as the ROADMAP-s121-item-4a arming floor: >= 300 a frame, plus the RC8 ceiling = the M arm's key
misses; S13 as review RC1) and the
review's RC1 / RC8 edges.  Sizes and constants come from this suite, never from the scorer.
    python test_shp121.py <shp121.py> [--real]
--real also scores the session-120 log C:/kyty/s120/log_cen120.txt (no tm8_* counters, other arms): it must end in a
clean NOT_ADMITTED with named reasons, never a crash.
"""
import hashlib
import importlib.util
import io
import json
import math
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except (AttributeError, ValueError):
    pass
SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s121/fx_shp121')
NL = chr(10)
spec = importlib.util.spec_from_file_location('shp121', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)

TAG = 'shp121'
BUILD = '0bd21ec24e546fbbb9b923c148fb76b57f45389ac166a71bad7410a3add738c7'
VSHA = 'ab' * 32
PERIOD = 90
START = 1800
SMALL = 4
BLOCKS = 2 * SMALL
ABBA = (0, 1, 1, 0)
PRED_STANDIN = BASE / 'pred' / '02_shp121.md'
PRED_STANDIN.parent.mkdir(parents=True)
PRED_STANDIN.write_bytes(b'stand-in pre-registration for the fixtures' + NL.encode())
PSHA = hashlib.sha256(PRED_STANDIN.read_bytes()).hexdigest()
PBYTES = len(PRED_STANDIN.read_bytes())
PRED_FWD = str(PRED_STANDIN).replace('\\', '/')
PRED_BACK = PRED_FWD.replace('/', '\\')
PRED_REAL_BACK = 'C:\\kyty\\s121\\pred\\02_shp121.md'
GATES_REAL = 'C:/kyty/s121/gates_base.txt'
GATES_TEXT = ' '.join(Path(GATES_REAL).read_text(encoding='utf-8').split())
TEXT = ('texmemo8=1', 'texmemo8=0')
SCHED = '90+1800:' + TEXT[0] + '|' + TEXT[1]
VALUES = tuple(dict(p.split('=') for p in t.split()) for t in TEXT)
ENV_OK = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GATE_FILE': 'C:\\kyty\\s121\\gates.req',
          'KYTY_SAMPLE_GATE': 'C:\\kyty\\s121\\sample.req', 'KYTY_QUEUE_TRACE': '1',
          'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0',
          'KYTY_GATE_SCHEDULE': SCHED, 'KYTY_GATE_SCHEDULE_ABBA': '1', 'VK_SDK_PATH': 'C:\\VulkanSDK\\1.4.357.0'}
PIN = 'GpuClockPin: mode 1 - the guest GPU clock ignores the pacer speed (KYTY_GPU_CLOCK_PIN)'
TM8 = ['tm8_fill', 'tm8_evict', 'tm8_evict_view', 'tm8_alias', 'tm8_inval', 'tm8_mode', 'tm8_renorm', 'tm8_x2',
       'tm8_cenoff', 'tm8_look', 'tm8_hit', 'tm8_miss', 'tm8_stale', 'tm8_gain', 'tm8_vchk', 'tm8_bad', 'tm8_vctl',
       'tm8_vctl_bad', 'tm8_relive', 'tm8_inject', 'tm8_inject_miss', 'tm8_dlose', 'tm8_ddiff', 'tm8_dcc_chg',
       'tm8_rbchk', 'tm8_rbbad', 'tm8_rbinject', 'tm8_rbinject_miss', 'tm8_pb0_ns', 'tm8_pb_ns', 'tm8_pb_n']
TM8_ZERO = {k: 0 for k in TM8}
MAIN = ({'dt_us': 32650, 'cpu_gpu_us': 31000, 'draws': 5000},
        {'dt_us': 33000, 'cpu_gpu_us': 31400, 'draws': 5000})
DRAW = ({'tex_hits': 46190, 'bda_scan': 55},
        {'tex_hits': 45000, 'bda_scan': 55})
X_P = dict(dict(texmemo_collide=580, texmemo_empty=2, texmemo_stale=7, texfast_ok=45000, texfast_no=3700,
                texfast_rec=150, tnull_hit=1400, tnull_miss=0), **dict(TM8_ZERO, tm8_fill=500, tm8_evict=450,
                                                                         tm8_evict_view=30))
X_M = dict(dict(texmemo_collide=1772, texmemo_empty=0, texmemo_stale=7, texfast_ok=44000, texfast_no=4700,
                texfast_rec=300, tnull_hit=1400, tnull_miss=0), **TM8_ZERO)
X_ARM = (X_P, X_M)
B_TEXN_PARTS = ('texmemo_collide', 'texmemo_empty', 'texmemo_stale', 'tnull_hit', 'tnull_miss')
VFY_OK = dict(verdict='PASS', tag='vfy121', draft=False, build_sha256=BUILD, scorer_sha256=VSHA)
RESULTS = []


def arm_of(block, order=ABBA):
    return order[block % 4]


def frame(b, pos):
    return START + 1 + PERIOD * b + pos


def make(name, blocks=BLOCKS, main=None, x=None, draw=None, env=None, pins=(PIN,), meta=None, gate_arm=None,
         gate_lines=None, drop=(), dup=(), extra_log=(), stdout_lines=(), pre=5, order=ABBA, strip=(), after=None,
         gates_copy=None, tag=TAG, vfy=VFY_OK, vfy_tag='vfy121', last=None, switch=True, dup_x=None):
    """A fixture directory.  main/x/draw: callables (n, block, arm, pos) -> dict of overrides for that frame (pre-
    schedule rows get block -1, arm 1, pos -1); b_texn is derived from the -x parts unless draw() overrides it;
    after: callable n -> lines written right after frame n's lines; last: the last frame written; vfy: the verify
    result dict (None = no file, a str = raw file text); dup_x: n -> overrides of the SECOND -x line of a frame in dup."""
    root = BASE / name
    root.mkdir(parents=True)
    lines = list(pins)
    prev = None
    end = START + PERIOD * blocks if last is None else last
    for n in range(START - pre + 1, end + 1):
        if n > START and (n - START - 1) % PERIOD == 0:
            b = (n - START - 1) // PERIOD
            arm = arm_of(b, order)
            if gate_arm is not None:
                lines.extend(gate_arm(b, arm))
            else:
                lines.append('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                             % (arm, b, START + PERIOD * b, TEXT[arm]))
            if gate_lines is not None:
                lines.extend(gate_lines(b, arm))
            else:
                for k, v in VALUES[arm].items():
                    if (prev is None and v != '0') or (prev is not None and VALUES[prev][k] != v):
                        lines.append('Gate: %s=%s frame=%d' % (k, v, START + PERIOD * b))
            changed = prev is None or prev != arm
            prev = arm
        if n <= START:
            b, pos, arm = -1, -1, 1
        else:
            b, pos = (n - START - 1) // PERIOD, (n - START - 1) % PERIOD
            arm = arm_of(b, order)
        mv = dict(MAIN[arm], arm=arm if n > START else 0, blk=b if n > START else 0)
        dv = dict(DRAW[arm])
        xv = dict(X_ARM[arm])
        if switch and n > START:
            # the switch rows at block positions 0-2 (outside the window): the invalidation at the first resolve,
            # a refill burst in P, a skewed fill count on an M block's first rows
            if pos == 0 and changed:
                xv.update(tm8_inval=1, tm8_mode=1)
            if arm == 0 and pos < 10:
                xv.update(tm8_fill=2000, tm8_evict=10)
            if arm == 1 and pos in (1, 2):
                xv.update(tm8_fill=40)
        if main:
            mv.update(main(n, b, arm, pos))
        if x:
            xv.update(x(n, b, arm, pos))
        over = draw(n, b, arm, pos) if draw else {}
        dv.update(over)
        if 'b_texn' not in over:
            dv['b_texn'] = dv['tex_hits'] + sum(xv[k] for k in B_TEXN_PARTS)
        for kind, sn, field in strip:
            if sn == n:
                {'main': mv, 'draw': dv, 'x': xv}[kind].pop(field, None)
        if ('main', n) not in drop:
            lines.append('FrameTrace: n=%d ' % n + ' '.join('%s=%d' % kv for kv in mv.items()))
        if ('draw', n) not in drop:
            lines.append('FrameTrace-draw: n=%d ' % n + ' '.join('%s=%d' % kv for kv in dv.items()))
        if ('x', n) not in drop:
            lines.append('FrameTrace-x: n=%d ' % n + ' '.join('%s=%d' % kv for kv in xv.items()))
        if n in dup:
            xd = dict(xv, **((dup_x or {}).get(n) or {}))
            lines.append('FrameTrace-x: n=%d ' % n + ' '.join('%s=%d' % kv for kv in xd.items()))
        if after:
            lines.extend(after(n))
    lines.extend(extra_log)
    (root / ('log_%s.txt' % tag)).write_bytes((NL.join(lines) + NL).encode('utf-8'))
    (root / ('stdout_%s.txt' % tag)).write_bytes((NL.join(stdout_lines) + NL).encode('utf-8'))
    m = dict(tag=tag, binary_sha256=BUILD, env=dict(ENV_OK if env is None else env), schedule=SCHED, hold_s=300,
             gates=GATES_TEXT, attempts=[dict(label='attempt 1', outcome='ok', hold_exit=None, stable_frame=439)],
             prereg=dict(path=PRED_BACK, sha256=PSHA, bytes=PBYTES), pre_run=dict(gpu_util_median=2))
    if meta:
        m.update(meta)
    (root / ('%s.json' % tag)).write_text(json.dumps(m), encoding='utf-8')
    if gates_copy is not None:
        (root / 'gates_base.txt').write_bytes(gates_copy if isinstance(gates_copy, bytes) else gates_copy.encode('utf-8'))
    if vfy is not None:
        (root / 'runs121').mkdir()
        body = vfy if isinstance(vfy, str) else json.dumps(vfy)
        (root / 'runs121' / ('%s.score.json' % vfy_tag)).write_bytes(body.encode('utf-8'))
    return root


def get(res, path):
    for part in path.split('.'):
        res = res[int(part)] if isinstance(res, list) else res[part]
    return res


def run(name, root, installed=BUILD, min_pairs=SMALL, pred=(PSHA, PBYTES), pred_path=PRED_FWD, draft=False,
        gates_file=None, tag=TAG, vfy_tag='vfy121', vfy_sha=VSHA, **expect):
    gf = str(root / 'gates_base.txt') if gates_file == 'copy' else (gates_file or GATES_REAL)
    res = mod.evaluate(str(root), tag, draft=draft, installed_sha=installed, min_pairs=min_pairs, pred_sha=pred[0],
                       pred_bytes=pred[1], pred_path=pred_path, gates_file=gf, vfy_tag=vfy_tag, vfy_sha=vfy_sha)
    bad = []
    try:
        json.dumps(res, allow_nan=False)
    except ValueError as exc:
        bad.append('json: %s' % exc)
    text = NL.join(mod.format_report(res))
    if re.search(r'(?i)\bnan\b|\binf\b', text):
        bad.append('nan/inf in the report')
    for key, want in expect.items():
        if key == 'failed':
            got = sorted(k for k, v in res['checks'].items() if not v)
            want = sorted(want)
        elif key == 'failed_has':
            got = sorted(k for k, v in res['checks'].items() if not v)
            miss = [w for w in want if w not in got]
            if miss:
                bad.append('failed lacks %r in %r' % (miss, got))
            continue
        elif key == 'ne':
            got = res['not_evaluable']
        elif key == 'lines_has':
            for w in want:
                if w not in text:
                    bad.append('report lacks %r' % w)
            continue
        elif key == 'lines_not':
            for w in want:
                if w in text:
                    bad.append('report has %r' % w)
            continue
        elif key in ('last_has', 'last_not'):
            last = text.split(NL)[-1]
            for w in want:
                if (w in last) != (key == 'last_has'):
                    bad.append('last line %r: %s %r' % (last[:70], key, w))
            continue
        else:
            got = get(res, key[2:] if key.startswith('x_') else key.replace('__', '.'))
        if isinstance(want, float) and isinstance(got, (int, float)) and not isinstance(got, bool):
            if abs(got - want) > 1e-6:
                bad.append('%s=%r want %r' % (key, got, want))
        elif got != want:
            bad.append('%s=%r want %r' % (key, got, want))
    RESULTS.append((name, not bad, bad))
    return res


def case(name, expect, **kw):
    runner = {k: kw.pop(k) for k in ('installed', 'min_pairs', 'pred', 'pred_path', 'draft', 'gates_file',
                                     'vfy_sha') if k in kw}
    for k in ('tag', 'vfy_tag'):
        if k in kw:
            runner[k] = kw[k]
    return run(name, make(name, **kw), **runner, **expect)


def check(name, got, want):
    RESULTS.append((name, got == want, [] if got == want else ['%r want %r' % (got, want)]))


P = lambda f: (lambda n, b, arm, i: f(n, b, i) if arm == 0 and n > START else {})
M = lambda f: (lambda n, b, arm, i: f(n, b, i) if arm == 1 and n > START else {})
AT = lambda blk, pos, d: (lambda n, b, arm, i: d if (b, i) == (blk, pos) else {})
PRE = lambda d: (lambda n, b, arm, i: d if n == START - 1 else {})
OK = dict(verdict='SHIP', admission='ADMITTED', failed=[], ne=[], correct=True)
ADM = dict(admission='ADMITTED', failed=[])
CASCADE = ['arms', 'gate_lines', 'pairs', 'armed_fill']
SP = 16667.0 / 32650.0
SM = 16667.0 / 33000.0

# ------------------------------------------------------------------ the admitted base: every reported term
case('ok', dict(OK, pairs=4, blocks=8, complete_blocks=8, dt_us__delta=-350.0, dt_us__two_se=0.0, upper=-350.0,
                dt_us__P=32650.0, dt_us__M=33000.0, cpu_gpu_us__delta=-400.0, cpu_gpu_us__two_se=0.0,
                cpu_gpu_us__P=31000.0, cpu_gpu_us__M=31400.0, est_frames__P=316, est_frames__M=316,
                window_frames__P=316, window_frames__M=316, arming__tex_hits=1190.0, arming__key_miss=-1190.0,
                arming__P_tex_hits=46190.0, arming__M_tex_hits=45000.0, arming__P_key_miss=582.0,
                arming__M_key_miss=1772.0, report_diffs__texmemo_stale=0.0, report_diffs__texfast_ok=1000.0,
                report_diffs__texfast_no=-1000.0, report_diffs__texfast_rec=-150.0, report_diffs__b_texn=0.0,
                p_tm8__tm8_fill=500.0, p_tm8__tm8_evict=450.0, p_tm8__tm8_evict_view=30.0, p_tm8__tm8_alias=0.0,
                p_tm8__tm8_renorm=0.0, speed__P=SP, speed__M=SM, speed__change_pp=100.0 * (SP - SM),
                speed__change_rel_pct=100.0 * (33000.0 / 32650.0 - 1.0), bda_scan__P=55.0, bda_scan__M=55.0,
                bda_scan__P_regime='NEW', bda_scan__M_regime='NEW', vfy__ok=True, vfy__reason='PASS',
                vfy__tag='vfy121', vfy__summary__verdict='PASS', raw__tm8_inval=5, raw__tm8_mode=5,
                lines__tm8_mismatch=0, lines__tm8_injected=0, probe__pb_us=0.0, probe__t_pb_ns=None, x_tag=TAG,
                x_draft=False, build_sha256=BUILD,
                lines_has=['Delta dt_us (P - M) -350.0 +- 0.0 us (2SE, 4 pairs), upper -350.0; P 32650.0 M 33000.0 us',
                           'prediction -350.0 us (range -500.0 .. -250.0) [I]',
                           'game speed (16 667 / mean dt_us) P %.4f M %.4f: change %.2f pp (%.2f %%)'
                           % (SP, SM, 100 * (SP - SM), 100 * (33000.0 / 32650.0 - 1.0)),
                           'Delta cpu_gpu_us (P - M) -400.0 +- 0.0 us; P 31000.0 M 31400.0 us (report)',
                           'arming a frame: tex_hits P - M 1190.0 (need >= +300 and <= the M key misses 1772.0; '
                           'census +1190), key misses P - M -1190.0 (need <= -300; census -1190); P tex_hits 46190.0 '
                           'M 45000.0, P key misses 582.0 M 1772.0',
                           'report P - M a frame: texmemo_stale 0.0, texfast_ok 1000.0, texfast_no -1000.0, '
                           'texfast_rec -150.0, b_texn 0.0',
                           'P window a frame: tm8_fill 500.0, tm8_evict 450.0, tm8_evict_view 30.0, tm8_alias 0.0, '
                           'tm8_renorm 0.0',
                           'correctness (all rows): tm8_bad=0, tm8_vctl_bad=0, tm8_relive=0, tm8_rbbad=0; lines '
                           'tm8_mismatch=0, tm8_injected=0',
                           'probe timer (all rows): pb 0.000 us, pb0 0.000 us, n 0, t_pb - ns',
                           'bda_scan P 55.0 (NEW) M 55.0 (NEW)', 'vfy vfy121: PASS (PASS)', 'not evaluable: -',
                           'ADMISSION: ADMITTED', 'VERDICT: SHIP Delta=-350.0 2se=0.0 upper=-350.0',
                           '  blocks 8 complete 8 pairs 4; estimator frames P 316 M 316; window frames P 316 M 316',
                           'shp121 tag shp121  scorer '],
                lines_not=['REPORT OF A NOT_ADMITTED RUN', 'DRAFT'],
                last_has=['CONSEQUENCE: SHIP - "SHIP (умолчание `texmemo8` → 1)', 'KNOB_DEFINITIONS']))

# ------------------------------------------------------------------ estimator: S7 arithmetic, S5 window, draws edge
S7 = {0: 32700, 3: 32600, 4: 32650, 7: 32650}          # P blocks of pairs (0,1) (2,3) (4,5) (6,7): -300 -400 -350 -350
SD7 = statistics.stdev([-300.0, -400.0, -350.0, -350.0])
case('s7_arith', dict(OK, dt_us__delta=-350.0, dt_us__two_se=SD7, upper=-350.0 + SD7, dt_us__P=32650.0,
                      dt_us__pair_diffs=[-300.0, -400.0, -350.0, -350.0],
                      lines_has=['Delta dt_us (P - M) -350.0 +- 40.8 us (2SE, 4 pairs), upper -309.2']),
     main=P(lambda n, b, i: {'dt_us': S7[b]}))
check('s7_sd_value', round(SD7, 6), 40.824829)
# unequal estimator counts: the pooled mean of frames differs from the mean of block means (mutant: pooled frames)
case('s7_unequal_counts', dict(OK, dt_us__delta=-350.0, dt_us__P=32650.0, est_frames__P=306, window_frames__P=316),
     main=lambda n, b, arm, i: dict({'dt_us': S7[b]} if arm == 0 and n > START else {},
                                   **({'draws': 2000} if b == 0 and 20 <= i < 30 else {})))
# S5: positions 9 and 89 carry 10^6 (outside); positions 10 and 88 inside shift their block means
WIN = {(0, 9): 10 ** 6, (0, 89): 10 ** 6, (3, 9): 10 ** 6, (3, 89): 10 ** 6, (0, 10): 32650 + 790,
       (3, 88): 32650 + 1580, (1, 9): 10 ** 6, (1, 89): 10 ** 6}
case('s5_window', dict(OK, dt_us__delta=-342.5, dt_us__pair_diffs=[-340.0, -330.0, -350.0, -350.0]),
     main=lambda n, b, arm, i: {'dt_us': WIN[(b, i)]} if (b, i) in WIN else {})
# draws: 3000 is out of the estimator (a 10^6 row), 3001 is in
case('draws_edge', dict(OK, dt_us__delta=-325.0, est_frames__P=315, window_frames__P=316,
                        dt_us__pair_diffs=[-350.0, -250.0, -350.0, -350.0]),
     main=lambda n, b, arm, i: ({'draws': 3000, 'dt_us': 10 ** 6} if (b, i) == (0, 20) else
                                {'draws': 3001, 'dt_us': 32650 + 7900} if (b, i) == (3, 20) else {}))
# median would ignore one outlier row: a single row moves the block mean
case('mean_not_median', dict(OK, dt_us__delta=-340.0, dt_us__pair_diffs=[-310.0, -350.0, -350.0, -350.0]),
     main=AT(0, 40, {'dt_us': 32650 + 3160}))
# a pair whose M block has no estimator rows is dropped
case('pair_no_est', dict(OK, pairs=3, est_frames__M=237, est_frames__P=237, complete_blocks=8),
     main=lambda n, b, arm, i: {'draws': 2000} if b == 5 else {}, min_pairs=3)
# an estimator row's cpu_gpu_us
case('cpu_estimate', dict(OK, cpu_gpu_us__delta=-360.0, dt_us__delta=-350.0),
     main=lambda n, b, arm, i: {'cpu_gpu_us': 31000 + 40} if arm == 0 and n > START and 10 <= i < 89 else {})

# ------------------------------------------------------------------ S8: the strict ship edge, and the sign
EDGE = {0: 32991, 3: 32991, 4: 32991, 7: 33003}           # diffs -9 -9 -9 +3: mean -6, sd 6, 2SE 6 -> upper 0.0
case('s8_upper_zero', dict(ADM, verdict='NO_SHIP', dt_us__delta=-6.0, dt_us__two_se=6.0, upper=0.0, ne=[],
                           last_has=['CONSEQUENCE: NO_SHIP']),
     main=P(lambda n, b, i: {'dt_us': EDGE[b]}))
EDGE2 = {0: 32991, 3: 32991, 4: 32991, 7: 33002}          # -9 -9 -9 +2: mean -6.25, 2SE 5.5 -> upper -0.75
case('s8_upper_below', dict(OK, dt_us__delta=-6.25, dt_us__two_se=5.5, upper=-0.75),
     main=P(lambda n, b, i: {'dt_us': EDGE2[b]}))
case('s8_positive', dict(ADM, verdict='NO_SHIP', dt_us__delta=10.0, upper=10.0, ne=[],
                         lines_has=['VERDICT: NO_SHIP Delta=10.0 2se=0.0 upper=10.0']),
     main=P(lambda n, b, i: {'dt_us': 33010}))
case('s8_zero', dict(ADM, verdict='NO_SHIP', dt_us__delta=0.0, upper=0.0), main=P(lambda n, b, i: {'dt_us': 33000}))

# ------------------------------------------------------------------ S6: pairs, complete blocks, truncated tail
case('s6_stop_87', dict(OK, pairs=3, complete_blocks=7, blocks=8), last=frame(7, 87), min_pairs=3)
case('s6_stop_88', dict(OK, pairs=4, complete_blocks=8), last=frame(7, 88))
case('s6_stop_88_main_only', dict(OK, pairs=3, complete_blocks=7), last=frame(7, 88),
     drop=(('draw', frame(7, 88)), ('x', frame(7, 88))), min_pairs=3)
case('s6_stop_88_main_only_minpairs', dict(verdict='NOT_ADMITTED', admission='NOT_ADMITTED', failed=['pairs']),
     last=frame(7, 88), drop=(('draw', frame(7, 88)), ('x', frame(7, 88))))
case('s6_odd_blocks', dict(OK, pairs=4, blocks=9, complete_blocks=9), blocks=9)
case('s6_bmm_order', dict(verdict='NOT_ADMITTED', failed=CASCADE), order=(1, 0, 0, 1))
case('s6_label_arm', dict(OK, pairs=3, complete_blocks=7), main=AT(2, 30, {'arm': 0}), min_pairs=3)
case('s6_label_blk', dict(OK, pairs=3, complete_blocks=7), main=AT(5, 88, {'blk': 4}), min_pairs=3)
case('s6_label_outside', dict(OK, pairs=4, complete_blocks=8), main=AT(5, 89, {'blk': 4}))
case('min_pairs_5', dict(verdict='NOT_ADMITTED', failed=['pairs'], last_has=['CONSEQUENCE: NOT_ADMITTED']),
     min_pairs=5)
case('min_pairs_default', dict(verdict='NOT_ADMITTED', failed=['pairs']), min_pairs=None)
case('no_pairs', dict(verdict='NOT_ADMITTED', admission='NOT_ADMITTED', failed=['arm_asserts', 'pairs'], pairs=0, ne=['arming_tex_hits', 'arming_key_miss', 'bda_regime',
                                                            'two_se_undefined'], bda_scan__P_regime=None),
     blocks=1)
case('se_one_pair', dict(ADM, verdict='NOT_EVALUABLE', pairs=1, ne=['two_se_undefined'], dt_us__two_se=None,
                         upper=None, lines_has=['upper -;']),
     blocks=2, min_pairs=1)

# ------------------------------------------------------------------ admission: binary, pin, env, hold, attempts
NA = dict(verdict='NOT_ADMITTED', admission='NOT_ADMITTED')
case('binary', dict(NA, failed=['binary'], lines_has=['REPORT OF A NOT_ADMITTED RUN - NOT TO BE QUOTED']),
     meta=dict(binary_sha256='0' * 64))
case('installed', dict(NA, failed=['installed_now']), installed='1' * 64)
case('pin_env', dict(NA, failed=['pinned', 'env_exact']),
     env={k: v for k, v in ENV_OK.items() if k != 'KYTY_GPU_CLOCK_PIN'})
case('pin_none', dict(NA, failed=['pinned']), pins=())
case('pin_two', dict(NA, failed=['pinned']), pins=(PIN, PIN))
case('pin_mode2', dict(NA, failed=['pinned']), pins=('GpuClockPin: mode 2 - control',))
case('pin_garbled', dict(NA, failed=['pinned']), pins=('GpuClockPin: off',))
case('env_rec', dict(NA, failed=['env_exact']), env=dict(ENV_OK, KYTY_REC='C:\\kyty\\s121\\rec_shp121.mp4'))
case('env_ckpt', dict(NA, failed=['env_exact']), env=dict(ENV_OK, KYTY_GPU_CHECKPOINTS='0'))
case('env_no_abba', dict(NA, failed=['env_exact']),
     env={k: v for k, v in ENV_OK.items() if k != 'KYTY_GATE_SCHEDULE_ABBA'})
case('env_markers', dict(NA, failed=['env_exact']), env=dict(ENV_OK, KYTY_GPU_MARKERS='2'))
case('env_gatefile_s120', dict(NA, failed=['env_exact']), env=dict(ENV_OK, KYTY_GATE_FILE='C:\\kyty\\s120\\gates.req'))
case('env_sched_env', dict(NA, failed=['env_exact']), env=dict(ENV_OK, KYTY_GATE_SCHEDULE='90+1800:texmemo8=1|x=0'))
case('meta_sched', dict(NA, failed=['env_exact']), meta=dict(schedule='90+1800:texmemo8=0|texmemo8=1'))
case('env_vk', dict(NA, failed=['env_vk']), env=dict(ENV_OK, VK_LAYER_PATH='C:\\VulkanSDK\\1.4.357.0\\Bin'))
case('env_vk_sdk_only', dict(OK), env={k: v for k, v in ENV_OK.items() if k != 'VK_SDK_PATH'})
case('hold_299', dict(NA, failed=['hold']), meta=dict(hold_s=299))
case('hold_301', dict(NA, failed=['hold']), meta=dict(hold_s=301))
case('attempts_two', dict(NA, failed=['one_ok_attempt']),
     meta=dict(attempts=[dict(outcome='timeout', hold_exit=None), dict(outcome='ok', hold_exit=None)]))
case('attempt_exit', dict(NA, failed=['one_ok_attempt']), meta=dict(attempts=[dict(outcome='ok', hold_exit=0)]))
case('attempt_timeout', dict(NA, failed=['one_ok_attempt']), meta=dict(attempts=[dict(outcome='timeout',
                                                                                     hold_exit=None)]))
case('attempt_none', dict(NA, failed=['one_ok_attempt']), meta=dict(attempts=[]))
case('idle_11', dict(NA, failed=['idle']), meta=dict(pre_run=dict(gpu_util_median=11)))
case('idle_10', dict(OK), meta=dict(pre_run=dict(gpu_util_median=10)))
case('idle_missing', dict(NA, failed=['idle']), meta=dict(pre_run=None))
case('idle_text', dict(NA, failed=['idle']), meta=dict(pre_run=dict(gpu_util_median='2')))

# ------------------------------------------------------------------ admission: pre-registration (and --draft)
case('prereg_path', dict(NA, failed=['prereg']), meta=dict(prereg=dict(path='C:/kyty/s121/pred/01_vfy121.md',
                                                                      sha256=PSHA, bytes=PBYTES)))
case('prereg_meta_sha', dict(NA, failed=['prereg_sha']), meta=dict(prereg=dict(path=PRED_BACK, sha256='0' * 64,
                                                                              bytes=PBYTES)))
case('prereg_meta_bytes', dict(NA, failed=['prereg_sha']), meta=dict(prereg=dict(path=PRED_BACK, sha256=PSHA,
                                                                                bytes=PBYTES + 1)))
case('prereg_const_sha', dict(NA, failed=['prereg_sha']), pred=('0' * 64, PBYTES))
case('prereg_const_bytes', dict(NA, failed=['prereg_sha']), pred=(PSHA, PBYTES + 1))
MISSING = PRED_FWD.replace('02_shp121.md', 'missing.md')
case('prereg_file_missing', dict(NA, failed=['prereg_sha']), pred_path=MISSING,
     meta=dict(prereg=dict(path=MISSING, sha256=PSHA, bytes=PBYTES)))
case('prereg_unsealed', dict(NA, failed=['prereg_sha']), pred=(None, PBYTES))
EMPTY = BASE / 'pred' / 'empty.md'
EMPTY.write_bytes(b'')
ESHA = hashlib.sha256(b'').hexdigest()
EFWD = EMPTY.as_posix()
case('prereg_empty_file', dict(NA, failed=['prereg_sha']), pred=(ESHA, 0), pred_path=EFWD,
     meta=dict(prereg=dict(path=EFWD, sha256=ESHA, bytes=0)))
TAMPER = BASE / 'pred' / 'tampered.md'
TAMPER.write_bytes(bytes(b ^ 1 for b in PRED_STANDIN.read_bytes()))
TFWD = TAMPER.as_posix()
case('prereg_file_tampered', dict(NA, failed=['prereg_sha']), pred_path=TFWD,
     meta=dict(prereg=dict(path=TFWD, sha256=PSHA, bytes=PBYTES)))
case('prereg_bytes_both', dict(NA, failed=['prereg_sha']), pred=(PSHA, PBYTES + 1),
     meta=dict(prereg=dict(path=PRED_BACK, sha256=PSHA, bytes=PBYTES + 1)))
case('prereg_unsealed_bytes', dict(NA, failed=['prereg_sha']), pred=(PSHA, None))
# the scorer's own constants: PRED_PATH is the real path (prereg ok), the sha is None / the real file's (never the
# stand-in's) -> prereg_sha refused, before and after the seal
case('prereg_defaults', dict(NA, failed=['prereg_sha'], checks__prereg=True), pred=(None, None), pred_path=None,
     meta=dict(prereg=dict(path=PRED_REAL_BACK, sha256=PSHA, bytes=PBYTES)))
case('draft', dict(OK, x_draft=True, lines_has=['DRAFT: unsealed scoring', 'VERDICT: SHIP Delta=-350.0 2se=0.0 '
                                                                         'upper=-350.0 DRAFT']),
     draft=True, pred=(None, None), meta=dict(hold_s=1, prereg=None), min_pairs=99)
case('draft_keeps_idle', dict(NA, failed=['idle'], x_draft=True), draft=True, meta=dict(pre_run=dict(gpu_util_median=50)))

# ------------------------------------------------------------------ admission: gates and the arm asserts (S1)
case('gates_text', dict(NA, failed=['gates_exact']), meta=dict(gates=GATES_TEXT + ' x=1'))
case('gates_ws', dict(OK), meta=dict(gates='  ' + GATES_TEXT.replace(' ', '   ') + ' '))
case('gates_file_copy_same', dict(OK), gates_copy=Path(GATES_REAL).read_bytes(), gates_file='copy')
case('gates_file_copy_changed', dict(NA, failed=['gates_exact']), gates_copy=GATES_TEXT + ' x=1', gates_file='copy',
     meta=dict(gates=GATES_TEXT + ' x=1'))
case('gates_file_missing', dict(NA, failed=['gates_exact']), gates_file=str(BASE / 'nope.txt'))
for _name, _text in (('texmemo2', GATES_TEXT.replace('texmemo2=0', 'texmemo2=1')),
                     ('texfastcheck', GATES_TEXT.replace('texfastcheck=0', 'texfastcheck=1')),
                     ('r1cen', GATES_TEXT + ' r1cen=2'), ('r2cen', GATES_TEXT + ' r2cen=1'),
                     ('spcen', GATES_TEXT + ' spcen=1')):
    case('s1_base_' + _name, dict(NA, failed=['gates_exact', 'arm_asserts']), meta=dict(gates=_text))
case('s1_base_r1cen0', dict(NA, failed=['gates_exact']), meta=dict(gates=GATES_TEXT + ' r1cen=0'))
case('s1_base_first_wins', dict(NA, failed=['gates_exact']), meta=dict(gates=GATES_TEXT + ' texmemo2=1'))
check('s1_gates_base_pins', [mod.first_values(GATES_TEXT).get(k) for k in ('texmemo2', 'texfastcheck', 'r1cen',
                                                                           'r2cen', 'spcen', 'texmemo8')],
      ['0', '0', None, None, None, None])
for _arm, _text in ((0, 'texmemo8=1 spcen=0'), (1, 'texmemo8=0 r1cen=0'), (0, 'texmemo8=1 r2cen=0'),
                    (1, 'texmemo8=0 texmemo2=0'), (0, 'texmemo8=1 texfastcheck=0')):
    _texts = {0: ['texmemo8=1'], 1: ['texmemo8=0']}
    _texts[_arm] = ['texmemo8=%d' % (1 - _arm), _text]
    check('s1_arm_names_%s' % _text.split()[1].split('=')[0], mod.arm_asserts(_texts, GATES_TEXT), False)
check('s1_arm_plain', mod.arm_asserts({0: ['texmemo8=1'], 1: ['texmemo8=0']}, GATES_TEXT), True)
check('s1_arm_missing_m', mod.arm_asserts({0: ['texmemo8=1']}, GATES_TEXT), False)
check('s1_arm_missing_p', mod.arm_asserts({1: ['texmemo8=0']}, GATES_TEXT), False)


def text_arm(texts):
    return lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                           % (arm, b, START + PERIOD * b, texts[arm])]


case('s1_p_text_extra', dict(NA, failed=CASCADE + ['arm_asserts']), gate_arm=text_arm(('texmemo8=1 r1cen=0',
                                                                                       'texmemo8=0')))
case('s1_m_text_extra', dict(NA, failed=CASCADE + ['arm_asserts']), gate_arm=text_arm(('texmemo8=1',
                                                                                       'texmemo8=0 spcen=0')))
case('s1_p_text_texmemo2', dict(NA, failed=CASCADE + ['arm_asserts']), gate_arm=text_arm(('texmemo8=1 texmemo2=0',
                                                                                          'texmemo8=0')))
case('s1_p_text_2', dict(NA, failed=CASCADE), gate_arm=text_arm(('texmemo8=2', 'texmemo8=0')))
case('s1_m_text_1', dict(NA, failed=CASCADE), gate_arm=text_arm(('texmemo8=1', 'texmemo8=1')))
case('s1_texts_swapped', dict(NA, failed=CASCADE), gate_arm=text_arm(('texmemo8=0', 'texmemo8=1')))
case('s1_text_trailing_space', dict(OK), gate_arm=lambda b, arm: [
    'GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s ' % (arm, b, START + PERIOD * b, TEXT[arm])])


def arm_line(fmt_):
    return lambda b, arm: [fmt_ % dict(arm=arm, b=b, f=START + PERIOD * b, t=TEXT[arm])]


for _name, _fmt in (('period', 'GateArm: arm=%(arm)d arms=2 block=%(b)d frame=%(f)d period=91 abba=1 text=%(t)s'),
                    ('abba0', 'GateArm: arm=%(arm)d arms=2 block=%(b)d frame=%(f)d period=90 abba=0 text=%(t)s'),
                    ('arms3', 'GateArm: arm=%(arm)d arms=3 block=%(b)d frame=%(f)d period=90 abba=1 text=%(t)s'),
                    ('garbled', 'GateArm: arm=%(arm)d block=%(b)d frame=%(f)d text=%(t)s')):
    case('arms_' + _name, dict(NA, failed=CASCADE + (['arm_asserts'] if _name == 'garbled' else [])),
         gate_arm=arm_line(_fmt))
case('arms_frame', dict(NA, failed=CASCADE), gate_arm=lambda b, arm: [
    'GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s' % (arm, b, START + PERIOD * b + 1, TEXT[arm])])
case('arms_dup_block', dict(NA, failed=CASCADE), gate_arm=lambda b, arm: [
    'GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s' % (arm, b, START + PERIOD * b, TEXT[arm])] * 2)
case('arms_gap', dict(NA, failed=['arms', 'gate_lines', 'pairs'], pairs=3), gate_arm=lambda b, arm: [] if b == 3 else [
    'GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s' % (arm, b, START + PERIOD * b, TEXT[arm])])
case('arms_arm2', dict(NA, failed=CASCADE), gate_arm=lambda b, arm: [
    'GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
    % (2 if b == 5 else arm, b, START + PERIOD * b, TEXT[arm])])
case('arms_extra_garbled', dict(NA, failed=CASCADE), gate_arm=lambda b, arm: [
    'GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s' % (arm, b, START + PERIOD * b, TEXT[arm])]
    + (['GateArm: arm=0 garbled'] if b == 3 else []))
case('arms_none', dict(NA, failed=['arms', 'pairs', 'armed_fill', 'arm_asserts']), gate_arm=lambda b, arm: [],
     gate_lines=lambda b, arm: [])

# ------------------------------------------------------------------ admission: Gate: lines
case('gate_redundant_ok', dict(OK),
     gate_lines=lambda b, arm: (['Gate: texmemo8=0 frame=%d' % (START + PERIOD * b)] if b == 2 else []))
case('gate_wrong_value', dict(NA, failed=['gate_lines']),
     gate_lines=lambda b, arm: (['Gate: texmemo8=1 frame=%d' % (START + PERIOD * b)] if b == 1 else []))
case('gate_other_name', dict(NA, failed=['gate_lines']), extra_log=['Gate: r1cen=0 frame=1800'])
case('gate_off_block', dict(NA, failed=['gate_lines']), extra_log=['Gate: texmemo8=1 frame=1801'])
case('gate_before', dict(NA, failed=['gate_lines']), extra_log=['Gate: texmemo8=0 frame=1710'])
case('gate_after_blocks', dict(NA, failed=['gate_lines']), extra_log=['Gate: texmemo8=1 frame=%d' % frame(8, -1)])
case('gate_garbled', dict(NA, failed=['gate_lines']), extra_log=['Gate: texmemo8=1 frame=1800 extra'])
case('gate_none', dict(OK), gate_lines=lambda b, arm: [])

# ------------------------------------------------------------------ admission: markers, skipped draws, streams (S12)
case('s12_terminate_stdout', dict(NA, failed=['no_marker']), stdout_lines=['--- std::terminate ---'])
for _i, _m in enumerate(('--- Error ---', '--- Fatal Error ---', 'GpuWaitSlow: tick 5', 'GpuHangAbort: x',
                         'ErrorDeviceLost', 'Unhandled exception: 0xc0000005', '--- abort() ---',
                         'GpuMarkerHung: cs', 'GpuCheckpointHang')):
    case('marker_%d' % _i, dict(NA, failed=['no_marker']), extra_log=[_m])
case('skip_pos9', dict(OK, skipped_draws=1), after=lambda n: ['AsyncPipelines: skipped draw'] if n == frame(2, 8) else [])
case('skip_pos10', dict(NA, failed=['no_skip_window']),
     after=lambda n: ['AsyncPipelines: skipped draw'] if n == frame(2, 9) else [])
case('skip_pos88', dict(NA, failed=['no_skip_window']),
     after=lambda n: ['AsyncPipelines: skipped draw'] if n == frame(2, 87) else [])
case('skip_pos89', dict(OK), after=lambda n: ['AsyncPipelines: skipped draw'] if n == frame(2, 88) else [])
case('skip_pre', dict(OK), after=lambda n: ['AsyncPipelines: skipped draw'] if n == START - 1 else [])
case('skip_start', dict(OK), after=lambda n: ['AsyncPipelines: skipped draw'] if n == START else [], pre=1)
case('skip_first_line', dict(OK), pins=('AsyncPipelines: skipped draw', PIN))
# rows of a ninth block without a GateArm line are no block: a skipped draw at its position 50 is outside every window
case('skip_unscheduled', dict(OK, blocks=8, skipped_draws=1), blocks=9,
     gate_arm=lambda b, arm: [] if b == 8 else ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                                                % (arm, b, START + PERIOD * b, TEXT[arm])],
     after=lambda n: ['AsyncPipelines: skipped draw'] if n == frame(8, 49) else [])
case('streams_drop_x', dict(NA, failed=['streams', 'pairs'], complete_blocks=7), drop=(('x', frame(2, 50)),))
case('streams_drop_draw', dict(NA, failed=['streams', 'pairs']), drop=(('draw', frame(5, 10)),))
case('streams_dup_x', dict(NA, failed=['streams', 'pairs']), dup=(frame(6, 88),))
case('streams_strip_field', dict(NA, failed=['streams', 'pairs']), strip=(('x', frame(1, 30), 'tm8_pb_n'),))
case('streams_strip_draw', dict(NA, failed=['streams', 'pairs']), strip=(('draw', frame(1, 30), 'bda_scan'),))
case('streams_strip_main', dict(NA, failed=['streams', 'pairs']), strip=(('main', frame(1, 30), 'cpu_gpu_us'),))
case('streams_outside', dict(OK), drop=(('x', frame(2, 9)), ('draw', frame(2, 89))))
case('streams_last_exempt', dict(OK, pairs=4), last=frame(7, 89), drop=(('x', frame(7, 89)),))

# ------------------------------------------------------------------ admission: arming proof, leaks (S2), zeros (S3)
case('s2_p_fill_zero', dict(NA, failed=['armed_fill']),
     x=lambda n, b, arm, i: {'tm8_fill': 0, 'tm8_evict': 0, 'tm8_evict_view': 0} if b == 3 else {})
case('s2_p_fill_zero_evict_small', dict(NA, failed=['armed_fill']),
     x=lambda n, b, arm, i: ({'tm8_fill': 0, 'tm8_evict': 5 if i == 50 else 0, 'tm8_evict_view': 0}
                             if b == 3 and 10 <= i < 89 else {}))
case('s2_p_evict_zero', dict(NA, failed=['armed_fill']),
     x=lambda n, b, arm, i: {'tm8_evict': 0, 'tm8_evict_view': 0} if b == 4 and 10 <= i < 89 else {})
case('s2_p_fill_outside_only', dict(NA, failed=['armed_fill']),
     x=lambda n, b, arm, i: {'tm8_fill': 0, 'tm8_evict': 0, 'tm8_evict_view': 0} if b == 7 and 10 <= i < 89 else {})
# the arming proof sums the WINDOW rows: fills only on low-draw window rows 10..19 of a P block still arm it
case('armed_fill_low_draws', dict(OK, est_frames__P=306),
     x=lambda n, b, arm, i: ({'tm8_fill': 500, 'tm8_evict': 450, 'tm8_evict_view': 30} if b == 3 and 10 <= i < 20 else
                             {'tm8_fill': 0, 'tm8_evict': 0, 'tm8_evict_view': 0} if b == 3 and 20 <= i < 89 else {}),
     main=lambda n, b, arm, i: {'draws': 2000} if b == 3 and 10 <= i < 20 else {})
case('s2_p_fill_one_row', dict(OK),
     x=lambda n, b, arm, i: ({'tm8_fill': 0, 'tm8_evict': 0, 'tm8_evict_view': 0} if b == 0 and 11 <= i < 89 else
                             {'tm8_fill': 9, 'tm8_evict': 1, 'tm8_evict_view': 0} if (b, i) == (0, 10) else {}))
for _pos, _ok in ((9, True), (10, False), (88, False), (89, True)):
    case('s2_m_fill_pos%d' % _pos, dict(OK) if _ok else dict(NA, failed=['m_zero']),
         x=AT(1, _pos, {'tm8_fill': 1}))
for _k in ('tm8_evict', 'tm8_evict_view', 'tm8_alias', 'tm8_renorm'):
    case('s2_m_' + _k, dict(NA, failed=['m_zero']), x=AT(2, 50, {_k: 1}))
case('s2_m_inval', dict(NA, failed=['m_zero', 'no_switch_in_window']), x=AT(5, 40, {'tm8_inval': 1}))
case('s2_m_leak_low_draws', dict(NA, failed=['m_zero']), x=AT(1, 50, {'tm8_fill': 1}), main=AT(1, 50, {'draws': 2000}))
# an M block with no estimator row at all (its pair is dropped) is still checked for leaks
case('s2_m_leak_no_est_block', dict(NA, failed=['m_zero'], pairs=3), x=AT(5, 50, {'tm8_fill': 1}),
     main=lambda n, b, arm, i: {'draws': 2000} if b == 5 else {}, min_pairs=3)
case('s2_p_mode', dict(NA, failed=['no_switch_in_window']), x=AT(3, 30, {'tm8_mode': 1}))
# the switch rule reads every WINDOW row, not only the estimator rows (draws > 3000)
case('switch_low_draws', dict(NA, failed=['no_switch_in_window']), x=AT(3, 30, {'tm8_inval': 1}),
     main=AT(3, 30, {'draws': 2000}))
case('s2_p_inval_pos88', dict(NA, failed=['no_switch_in_window']), x=AT(4, 88, {'tm8_inval': 1}))
case('s2_p_mode_pos2', dict(OK), x=AT(3, 2, {'tm8_mode': 1}))
case('s2_no_switch_rows', dict(OK, raw__tm8_inval=0), switch=False)
for _k in ('tm8_look', 'tm8_hit', 'tm8_vchk', 'tm8_pb_n', 'tm8_miss', 'tm8_stale', 'tm8_gain', 'tm8_vctl',
           'tm8_inject', 'tm8_inject_miss', 'tm8_dlose', 'tm8_ddiff', 'tm8_dcc_chg', 'tm8_rbchk', 'tm8_rbinject',
           'tm8_rbinject_miss', 'tm8_pb0_ns', 'tm8_pb_ns'):
    case('s2_leak_' + _k, dict(NA, failed=['verify_leak'], correct=True), x=AT(3, 50, {_k: 1}))
case('s2_leak_pos3', dict(NA, failed=['verify_leak']), x=AT(0, 3, {'tm8_look': 1}))
case('s2_leak_pre', dict(NA, failed=['verify_leak']), x=PRE({'tm8_look': 1}))
case('s2_leak_m_window', dict(NA, failed=['verify_leak', 'm_zero']), x=AT(1, 50, {'tm8_hit': 1}))
case('s2_leak_dup_row', dict(NA, failed=['verify_leak', 'streams', 'pairs']), dup=(frame(8, -1) - 1,),
     x=AT(7, 88, {'tm8_vchk': 1}))
case('s2_injected_line', dict(NA, failed=['verify_leak'], lines__tm8_injected=1),
     extra_log=['Tm8VerifyInjected: set=3 way=1'])
case('s2_rebind_injected_line', dict(NA, failed=['verify_leak'], lines__tm8_injected=1),
     extra_log=['Tm8RebindInjected: index=9'])
case('s11_probe_units', dict(NA, failed=['verify_leak'], probe__pb_us=5.0, probe__pb0_us=1.0, probe__n=2,
                             probe__t_pb_ns=2000.0,
                             lines_has=['probe timer (all rows): pb 5.000 us, pb0 1.000 us, n 2, t_pb 2000.00 ns']),
     x=AT(3, 3, {'tm8_pb_ns': 5000, 'tm8_pb0_ns': 1000, 'tm8_pb_n': 2}))
case('s11_probe_floor', dict(NA, failed=['verify_leak'], probe__t_pb_ns=0.0),
     x=AT(3, 3, {'tm8_pb_ns': 500, 'tm8_pb0_ns': 1000, 'tm8_pb_n': 2}))
for _k in ('tm8_x2', 'tm8_cenoff'):
    for _where, _fx in (('pos3', AT(0, 3, {_k: 1})), ('pos50', AT(3, 50, {_k: 1})), ('pre', PRE({_k: 1}))):
        case('s3_%s_%s' % (_k, _where), dict(NA, failed=['x2_cenoff'], correct=True), x=_fx)
case('s3_x2_m_window', dict(NA, failed=['x2_cenoff', 'm_zero']), x=AT(2, 50, {'tm8_x2': 1}))

# ------------------------------------------------------------------ correctness over ALL rows (S3): NO_SHIP
NOSHIP_C = dict(verdict='NO_SHIP', correct=False, last_has=['CONSEQUENCE: NO_SHIP', 'correctness counters fired'])
for _k in ('tm8_bad', 'tm8_vctl_bad', 'tm8_relive', 'tm8_rbbad'):
    for _where, _fx in (('pos3', AT(0, 3, {_k: 1})), ('pos50', AT(3, 50, {_k: 1})), ('pre', PRE({_k: 1}))):
        case('s3_%s_%s' % (_k, _where), dict(NOSHIP_C, admission='ADMITTED', failed=[]), x=_fx)
case('s3_bad_in_dup', dict(NOSHIP_C, failed=['streams', 'pairs']), dup=(frame(4, 20),),
     x=lambda n, b, arm, i: {'tm8_bad': 1} if (b, i) == (4, 20) else {})
# duplicates included: only the SECOND copy of a duplicated -x line carries tm8_bad
case('s3_bad_second_dup_only', dict(NOSHIP_C, failed=['streams', 'pairs']), dup=(frame(4, 20),),
     dup_x={frame(4, 20): {'tm8_bad': 1}})
case('s3_bad_not_admitted', dict(NOSHIP_C, admission='NOT_ADMITTED', failed=['idle']), x=AT(3, 50, {'tm8_bad': 1}),
     meta=dict(pre_run=dict(gpu_util_median=40)))
case('s3_bad_not_evaluable', dict(NOSHIP_C, admission='ADMITTED', ne=['arming_tex_hits']), x=AT(3, 50, {'tm8_bad': 1}),
     draw=P(lambda n, b, i: {'tex_hits': 45000 + 299}))
case('s3_bad_repeat_tag', dict(NOSHIP_C, admission='NOT_ADMITTED', failed=['idle']), x=AT(3, 50, {'tm8_bad': 1}),
     meta=dict(pre_run=dict(gpu_util_median=40)), tag='shp121r')
case('s3_verify_mismatch_line', dict(NOSHIP_C, admission='ADMITTED', lines__tm8_mismatch=1),
     extra_log=['Tm8VerifyMismatch: kind=gain id=5'])
case('s3_rebind_mismatch_line', dict(NOSHIP_C, admission='ADMITTED', lines__tm8_mismatch=1),
     extra_log=['Tm8RebindMismatch: index=9'])
case('p_alias_info', dict(OK, p_tm8__tm8_alias=3.0 / 316, p_tm8__tm8_renorm=1.0 / 316),
     x=AT(3, 50, {'tm8_alias': 3, 'tm8_renorm': 1}))

# ------------------------------------------------------------------ S4 arming: >= 300 a frame each, reported
case('s4_hits_300', dict(OK, arming__tex_hits=300.0), draw=P(lambda n, b, i: {'tex_hits': 45300}))
case('s4_hits_299', dict(ADM, verdict='NOT_EVALUABLE', ne=['arming_tex_hits'], arming__tex_hits=299.0,
                         last_has=['CONSEQUENCE: NOT_EVALUABLE']),
     draw=P(lambda n, b, i: {'tex_hits': 45299}))
case('s4_hits_down', dict(ADM, verdict='NOT_EVALUABLE', ne=['arming_tex_hits'], arming__tex_hits=-1190.0),
     draw=P(lambda n, b, i: {'tex_hits': 43810}))
case('s4_miss_300', dict(OK, arming__key_miss=-300.0), x=P(lambda n, b, i: {'texmemo_collide': 1470}))
case('s4_miss_299', dict(ADM, verdict='NOT_EVALUABLE', ne=['arming_key_miss'], arming__key_miss=-299.0),
     x=P(lambda n, b, i: {'texmemo_collide': 1471}))
case('s4_miss_up', dict(ADM, verdict='NOT_EVALUABLE', ne=['arming_key_miss'], arming__key_miss=1192.0),
     x=P(lambda n, b, i: {'texmemo_collide': 2962, 'tm8_fill': 500}))
case('s4_miss_empty_counts', dict(ADM, verdict='NOT_EVALUABLE', ne=['arming_key_miss'], arming__key_miss=-298.0),
     x=P(lambda n, b, i: {'texmemo_collide': 1172, 'texmemo_empty': 302}))
# arming reads the WINDOW rows of the paired blocks (all draws), not only the estimator rows
case('s4_window_rows', dict(ADM, verdict='NOT_EVALUABLE', ne=['arming_tex_hits'], arming__tex_hits=400.0 * 59 / 79,
                            est_frames__P=236, window_frames__P=316),
     draw=lambda n, b, arm, i: ({'tex_hits': 45000 if 10 <= i < 30 else 45400} if arm == 0 and n > START else {}),
     main=lambda n, b, arm, i: {'draws': 1000} if arm == 0 and 10 <= i < 30 else {})
case('s4_window_rows_m', dict(OK, arming__tex_hits=299.0 + 400.0 * 20 / 79, est_frames__M=236),
     draw=lambda n, b, arm, i: ({'tex_hits': 45299} if arm == 0 and n > START else
                                {'tex_hits': 44600} if arm == 1 and 10 <= i < 30 and n > START else {}),
     main=lambda n, b, arm, i: {'draws': 1000} if arm == 1 and 10 <= i < 30 and n > START else {})
# RC8 ceiling (kept): P - M tex_hits <= the M arm's own key misses a frame (1 772 here; 1 500 when measured so)
case('s4_ceiling_edge', dict(OK, arming__tex_hits=1772.0, arming__M_key_miss=1772.0),
     draw=P(lambda n, b, i: {'tex_hits': 45000 + 1772}))
case('s4_ceiling_over', dict(ADM, verdict='NOT_EVALUABLE', ne=['arming_ceiling'], arming__tex_hits=1773.0),
     draw=P(lambda n, b, i: {'tex_hits': 45000 + 1773}))
case('s4_ceiling_measured_edge', dict(OK, arming__tex_hits=1500.0, arming__M_key_miss=1500.0),
     draw=P(lambda n, b, i: {'tex_hits': 45000 + 1500}), x=M(lambda n, b, i: {'texmemo_collide': 1500}))
case('s4_ceiling_measured_over', dict(ADM, verdict='NOT_EVALUABLE', ne=['arming_ceiling'], arming__tex_hits=1501.0,
                                      lines_has=['need >= +300 and <= the M key misses 1500.0;']),
     draw=P(lambda n, b, i: {'tex_hits': 45000 + 1501}), x=M(lambda n, b, i: {'texmemo_collide': 1500}))
# outside the window: a 10^6 tex_hits row at position 9 changes nothing
case('s4_outside', dict(OK, arming__tex_hits=1190.0), draw=AT(0, 9, {'tex_hits': 10 ** 6}))
# an unpaired P block (the ninth) does not enter the arming means
case('s4_unpaired_block', dict(OK, arming__tex_hits=1190.0, pairs=4, blocks=9), blocks=9,
     draw=lambda n, b, arm, i: {'tex_hits': 0} if b == 8 else {})

# ------------------------------------------------------------------ identities (RC1): NEAR +-8, FAR max(64, 1 per mille)
BT = 79 * (45000 + 1772 + 7 + 1400)                       # an M block's window b_texn: 3 806 141
check('bt_window', BT, 3806141)


def texn_res(res_by_block):
    return lambda n, b, arm, i: ({'b_texn': DRAW[arm]['tex_hits'] + sum(X_ARM[arm][k] for k in B_TEXN_PARTS)
                                  + res_by_block[b]} if b in res_by_block and i == 50 else {})


# block 1 (M) at the FAR edge: 1000 * 3809 <= 3806141 + 3809; blocks 2, 5 take the opposite sign so the total stays 0
case('s13_far_edge_pass', dict(OK), draw=texn_res({1: 3809, 2: -1905, 5: -1904}))
case('s13_far_edge_fail', dict(ADM, verdict='NOT_EVALUABLE', ne=['b_texn=hits+keymiss+stale+null@1']),
     draw=texn_res({1: 3810, 2: -1905, 5: -1905}))
case('s13_far_525', dict(OK), draw=texn_res({1: 525, 2: -525}))
# the identities sum every WINDOW row: the residual row (position 50) with draws 2000 still breaks block 1
case('identity_low_draws', dict(ADM, verdict='NOT_EVALUABLE', ne=['b_texn=hits+keymiss+stale+null@1']),
     draw=texn_res({1: 3810, 2: -1905, 5: -1905}), main=AT(1, 50, {'draws': 2000}))
case('s13_far_negative_edge', dict(ADM, verdict='NOT_EVALUABLE', ne=['b_texn=hits+keymiss+stale+null@2']),
     draw=texn_res({1: 1904, 2: -3807, 5: 1903}))
case('s13_far_negative_pass', dict(OK), draw=texn_res({1: 1903, 2: -3806, 5: 1903}))
# the run total: +380 every block passes (10000 * 3040 <= 30 449 128 + 3040), +381 fails
case('rc1_total_pass', dict(OK), draw=texn_res({b: 380 for b in range(8)}))
case('rc1_total_fail', dict(ADM, verdict='NOT_EVALUABLE', ne=['b_texn=hits+keymiss+stale+null@total']),
     draw=texn_res({b: 381 for b in range(8)}))
# total residual 3045: 10000 * 3045 = 30 450 000 lies between the smaller (30 449 128) and the larger (30 452 173)
# side - the per-mille bound is taken of the LARGER side (review RC1)
case('rc1_total_larger_side', dict(OK), draw=texn_res({b: 385 if b == 7 else 380 for b in range(8)}))
# NEAR: evict <= fill + 8 on a P block window; a constant +1 a row fails
case('near_evict_fill_8', dict(OK), x=lambda n, b, arm, i: ({'tm8_evict': 500 + (8 if i == 30 else 0),
                                                             'tm8_fill': 500} if b == 3 and 10 <= i < 89 else {}))
case('near_evict_fill_9_only', dict(ADM, verdict='NOT_EVALUABLE', ne=['evict<=fill@3']),
     x=lambda n, b, arm, i: ({'tm8_evict': 500 + (9 if i == 30 else 0), 'tm8_fill': 500}
                             if b == 3 and 10 <= i < 89 else {}))
case('near_const_one_a_row', dict(ADM, verdict='NOT_EVALUABLE', ne=['evict_view<=evict@4']),
     x=lambda n, b, arm, i: {'tm8_evict_view': 451} if b == 4 and 10 <= i < 89 else {})
case('near_view_8', dict(OK), x=lambda n, b, arm, i: ({'tm8_evict_view': 450 + (8 if i == 60 else 0)}
                                                      if b == 4 and 10 <= i < 89 else {}))
case('near_view_9', dict(ADM, verdict='NOT_EVALUABLE', ne=['evict_view<=evict@4']),
     x=lambda n, b, arm, i: ({'tm8_evict_view': 450 + (9 if i == 60 else 0)} if b == 4 and 10 <= i < 89 else {}))
# FAR floor 64 on small window sums: evict <= collide + 64 (block 3: collide 10 a row = 790, evict 854 / 855)
SMALLC = lambda extra: (lambda n, b, arm, i: ({'texmemo_collide': 10, 'tm8_evict': 10 + (extra if i == 40 else 0),
                                               'tm8_fill': 10 + (extra if i == 40 else 0), 'tm8_evict_view': 0}
                                              if b == 3 and 10 <= i < 89 else {}))
case('far_floor_64', dict(OK), x=SMALLC(64))
case('far_floor_65', dict(ADM, verdict='NOT_EVALUABLE', ne=['evict<=collide@3']), x=SMALLC(65))
# FAR: fill <= key misses + stale (+ bad, vctl_bad, relive); the per-mille half on large sums
FILLX = lambda extra: (lambda n, b, arm, i: ({'tm8_fill': 589 + (extra if i == 40 else 0)}
                                             if b == 4 and 10 <= i < 89 else {}))
case('far_fill_edge', dict(OK), x=FILLX(64))
case('far_fill_over', dict(ADM, verdict='NOT_EVALUABLE', ne=['fill<=keymiss+stale+bad@4']), x=FILLX(65))
# on the ninth (unpaired, P) block, so the arming means are untouched: rhs 79 046 531, edge 79 125 / 79 126
BIG = lambda extra: (lambda n, b, arm, i: ({'tm8_fill': 1000589 + (extra if i == 40 else 0),
                                            'texmemo_collide': 1000580} if b == 8 and 10 <= i < 89 else {}))
case('far_fill_permille', dict(OK, blocks=9, pairs=4), x=BIG(79125), blocks=9)
case('far_fill_permille_over', dict(ADM, verdict='NOT_EVALUABLE', ne=['fill<=keymiss+stale+bad@8']), x=BIG(79126),
     blocks=9)
# the fill bound's right side carries tm8_bad + tm8_vctl_bad + tm8_relive (identity 1 as built): 300 over, 300 back
# (each term alone is 100 > the FAR floor 64)
case('fill_bound_bad_terms', dict(verdict='NO_SHIP', correct=False, ne=[]),
     x=lambda n, b, arm, i: ({'tm8_fill': 589 + 300} if (b, i) == (4, 40) else
                             {'tm8_bad': 100, 'tm8_vctl_bad': 100, 'tm8_relive': 100, 'tm8_fill': 589} if (b, i) == (4, 41) else
                             {'tm8_fill': 589} if b == 4 and 10 <= i < 89 else {}))
# the bounds are one-sided and window-only; M blocks satisfy them with zeros
case('bounds_outside', dict(OK), x=AT(3, 5, {'tm8_evict': 10 ** 6, 'tm8_evict_view': 10 ** 6}))
case('b_texn_outside', dict(OK), draw=AT(1, 89, {'b_texn': 10 ** 7}))
case('b_texn_null_parts', dict(OK), x=lambda n, b, arm, i: {'tnull_hit': 0, 'tnull_miss': 1400} if arm == 1 else {})
case('b_texn_stale_part', dict(OK), x=lambda n, b, arm, i: {'texmemo_stale': 100} if arm == 1 else {})
check('within_near', [mod.within(8, 100, 92, 'near'), mod.within(-8, 92, 100, 'near'), mod.within(9, 100, 91, 'near')],
      [True, True, False])
check('within_far', [mod.within(64, 64, 0, 'far'), mod.within(65, 65, 0, 'far'), mod.within(-100, 0, 100000, 'far'),
                     mod.within(-101, 0, 100000, 'far'), mod.within(101, 101000, 100899, 'far')],
      [True, False, True, False, True])

# ------------------------------------------------------------------ S10: the BDA regime
for _p, _m, _ok in ((700, 55, False), (700, 700, True), (400, 400, True), (300, 301, False), (300, 300, True),
                    (600, 599, False), (55, 600, False)):
    case('s10_bda_%d_%d' % (_p, _m), dict(OK) if _ok else dict(ADM, verdict='NOT_EVALUABLE', ne=['bda_regime']),
         draw=lambda n, b, arm, i, _p=_p, _m=_m: {'bda_scan': _p if arm == 0 else _m})
check('regime_labels', [mod.regime(None), mod.regime(300), mod.regime(301), mod.regime(599), mod.regime(600)],
      [None, 'NEW', 'MIXED', 'MIXED', 'OLD'])
case('s10_bda_est_rows', dict(OK, bda_scan__P=55.0),
     draw=lambda n, b, arm, i: {'bda_scan': 900} if arm == 0 and i == 50 else {},
     main=lambda n, b, arm, i: {'draws': 2000} if arm == 0 and i == 50 else {})
case('s10_bda_report', dict(ADM, verdict='NOT_EVALUABLE', lines_has=['bda_scan P 700.0 (OLD) M 55.0 (NEW)']),
     draw=lambda n, b, arm, i: {'bda_scan': 700} if arm == 0 else {})

# ------------------------------------------------------------------ S9: the sealed verify result
NOSHIP_V = dict(ADM, verdict='NO_SHIP', ne=[], correct=True, vfy__ok=False)
case('s9_missing', dict(NOSHIP_V, vfy__reason='vfy_missing',
                        last_has=['CONSEQUENCE: NO_SHIP', 'The verify result is not a sealed PASS (vfy_missing).']),
     vfy=None)
case('s9_fail', dict(NOSHIP_V, vfy__reason='vfy_verdict', lines_has=['vfy vfy121: not PASS (vfy_verdict)']),
     vfy=dict(VFY_OK, verdict='FAIL'))
case('s9_not_evaluable', dict(NOSHIP_V, vfy__reason='vfy_verdict'), vfy=dict(VFY_OK, verdict='NOT_EVALUABLE'))
case('s9_scorer_sha', dict(NOSHIP_V, vfy__reason='vfy_scorer_sha'), vfy=dict(VFY_OK, scorer_sha256='cd' * 32))
case('s9_const_unsealed', dict(NOSHIP_V), vfy_sha=None)
case('s9_build', dict(NOSHIP_V, vfy__reason='vfy_build'), vfy=dict(VFY_OK, build_sha256='0' * 64))
case('s9_tag', dict(NOSHIP_V, vfy__reason='vfy_tag'), vfy=dict(VFY_OK, tag='vfy121r'))
case('s9_draft_true', dict(NOSHIP_V, vfy__reason='vfy_draft'), vfy=dict(VFY_OK, draft=True))
case('s9_draft_missing', dict(NOSHIP_V, vfy__reason='vfy_draft'),
     vfy={k: v for k, v in VFY_OK.items() if k != 'draft'})
case('s9_garbage', dict(NOSHIP_V, vfy__reason='vfy_unreadable', vfy__summary=None), vfy='{not json')
case('s9_list', dict(NOSHIP_V, vfy__reason='vfy_unreadable'), vfy='["PASS"]')
case('s9_repeat_tag', dict(OK, vfy__tag='vfy121r', lines_has=['vfy vfy121r: PASS (PASS)']),
     vfy=dict(VFY_OK, tag='vfy121r'), vfy_tag='vfy121r')
run('s9_wrong_file', make('s9_wrong_file', vfy=VFY_OK, vfy_tag='vfy121r'), **dict(NOSHIP_V, vfy__reason='vfy_missing'))
case('s9_summary', dict(OK, vfy__summary={'verdict': 'PASS', 'tag': 'vfy121', 'draft': False,
                                          'scorer_sha256': VSHA, 'build_sha256': BUILD}))
case('s9_pass_positive_delta', dict(ADM, verdict='NO_SHIP', vfy__ok=True, last_not=['The verify result is not']),
     main=P(lambda n, b, i: {'dt_us': 33010}))
case('s9_fail_not_admitted', dict(NA, failed=['idle'], vfy__ok=False), vfy=None,
     meta=dict(pre_run=dict(gpu_util_median=40)))

# ------------------------------------------------------------------ the repeat tag and the verdict order
case('repeat_ok', dict(OK, x_tag='shp121r'), tag='shp121r')
case('repeat_not_admitted', dict(verdict='NOT_EVALUABLE', admission='NOT_ADMITTED', failed=['idle'],
                                 last_has=['CONSEQUENCE: NOT_EVALUABLE']),
     tag='shp121r', meta=dict(pre_run=dict(gpu_util_median=40)))
case('first_not_admitted', dict(verdict='NOT_ADMITTED', admission='NOT_ADMITTED', failed=['idle']),
     meta=dict(pre_run=dict(gpu_util_median=40)))
case('na_before_ne', dict(verdict='NOT_ADMITTED', failed=['idle'], ne=['arming_tex_hits']),
     meta=dict(pre_run=dict(gpu_util_median=40)), draw=P(lambda n, b, i: {'tex_hits': 45000}))
case('ne_before_ship', dict(ADM, verdict='NOT_EVALUABLE', ne=['bda_regime']),
     draw=lambda n, b, arm, i: {'bda_scan': 700} if arm == 0 else {})

# ------------------------------------------------------------------ helpers and the command line
check('two_se_one', mod.two_se([5.0]), None)
check('two_se_two', mod.two_se([1.0, 3.0]), 2.0 * statistics.stdev([1.0, 3.0]) / math.sqrt(2))
check('mean_empty', mod.mean([]), None)
check('speed_none', [mod.speed(None), mod.speed(0), mod.speed(16667.0)], [None, None, 1.0])
check('first_values', mod.first_values('a=1 b=2 a=3 junk'), {'a': '1', 'b': '2'})
check('schedule', mod.SCHEDULE, SCHED)
check('env_expect', mod.ENV_EXPECT, {k: v for k, v in ENV_OK.items() if k.startswith('KYTY_')})
check('tm8_keys', list(mod.TM8_KEYS), TM8)
check('correct_keys', sorted(mod.CORRECT_KEYS), sorted(['tm8_bad', 'tm8_vctl_bad', 'tm8_relive', 'tm8_rbbad']))
check('leak_keys', sorted(mod.LEAK_KEYS), sorted(k for k in TM8[9:] if k not in ('tm8_bad', 'tm8_vctl_bad',
                                                                               'tm8_relive', 'tm8_rbbad')))
check('constants', [mod.BUILD_SHA, mod.GATES_SHA, mod.PRED_PATH, mod.HOLD_S, mod.PERIOD, mod.START, mod.KEEP,
                    mod.DRAWS_MIN, mod.ABBA, mod.ARM_TEXT, mod.MIN_PAIRS, mod.IDLE_GPU_MAX, mod.ARM_MIN,
                    mod.CENSUS_ARM, mod.PRED_US, mod.PRED_LO, mod.PRED_HI, mod.GAME_FRAME_US, mod.NS_PER_US,
                    mod.SKEW_NEAR, mod.SKEW_FAR_ABS, mod.SKEW_FAR_PERMILLE, mod.SKEW_MEAN_PER10K, mod.TAGS,
                    mod.VFY_TAGS, mod.VFY_TAG, mod.TAG, mod.ROOT, mod.GATES_FILE],
      [BUILD, '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf', 'C:/kyty/s121/pred/02_shp121.md',
       300, 90, 1800, (10, 89), 3000, (0, 1, 1, 0), ('texmemo8=1', 'texmemo8=0'), 30, 10, 300.0, 1190.0, -350.0,
       -500.0, -250.0, 16667.0, 1000.0, 8, 64, 1, 1, ('shp121', 'shp121r'), ('vfy121', 'vfy121r'), 'vfy121',
       'shp121', 'C:/kyty/s121', 'C:/kyty/s121/gates_base.txt'])
check('installed_path', mod.INSTALLED.replace('\\', '/').endswith('/OneDrive/Desktop/ps5 em/kyty_emulator.exe'), True)


def cli(argv):
    old_argv, old_out = sys.argv, sys.stdout
    sys.argv = ['shp121.py'] + argv
    sys.stdout = io.StringIO()
    try:
        rc = mod.main()
        text = sys.stdout.getvalue()
    finally:
        sys.argv, sys.stdout = old_argv, old_out
    return rc, text


_rc, _text = cli(['--root', str(BASE / 'ok'), '--tag', 'cen120'])
check('cli_unknown_tag', (_rc, _text.startswith('unknown tag cen120')), (2, True))
_rc, _text = cli(['--root', str(BASE / 'ok'), '--tag', 'shp121', '--vfy', 'vfy999'])
check('cli_unknown_vfy', _rc, 2)
_out = BASE / 'cli_out.json'
_rc, _text = cli(['--root', str(BASE / 's9_repeat_tag'), '--tag', 'shp121', '--vfy', 'vfy121r', '--draft', '--out',
                  str(_out)])
_j = json.loads(_out.read_text(encoding='utf-8'))
check('cli_out', (_j['tag'], _j['draft'], _j['vfy']['tag'], _rc == (0 if _j['verdict'] in ('SHIP', 'NO_SHIP') else 1),
                  _text.split(NL)[0].startswith('DRAFT'), 'VERDICT: ' + _j['verdict'] in _text),
      ('shp121', True, 'vfy121r', True, True, True))
_rc, _text = cli(['--root', str(BASE / 'ok'), '--draft'])
check('cli_defaults', ('shp121 tag shp121' in _text, 'vfy vfy121:' in _text), (True, True))
# Seal-02 repair (ROADMAP s121 item 7): two branches the sealed constants left without a killing fixture.
_rc, _text = cli(['--root', str(BASE / 'ok'), '--tag', 'shp121', '--vfy', 'vfy121'])
check('cli_rc_not_final', (_rc, 'VERDICT: SHIP' in _text or 'VERDICT: NO_SHIP' in _text), (1, False))
_vj = BASE / 'vfy_unsealed_probe.json'
_vj.write_text(json.dumps(dict(verdict='PASS', tag='vfy121', draft=False, scorer_sha256='0' * 64,
                               build_sha256=mod.BUILD_SHA)), encoding='utf-8')
check('vfy_check_unsealed', mod.vfy_check(str(_vj), None, 'vfy121')[:2], (False, 'vfy_sha_unsealed'))
check('vfy_check_sealed_ok', mod.vfy_check(str(_vj), '0' * 64, 'vfy121')[:2], (True, 'PASS'))

# ------------------------------------------------------------------ --real: the session-120 log (no tm8_* counters)
if '--real' in sys.argv:
    res = mod.evaluate('C:/kyty/s120', 'cen120', installed_sha=BUILD)
    text = mod.format_report(res)
    want = [(res['verdict'], 'NOT_ADMITTED'), (res['admission'], 'NOT_ADMITTED'), (res['correct'], True),
            (all(k in [c for c, v in res['checks'].items() if not v]
                 for k in ('binary', 'env_exact', 'arms', 'arm_asserts', 'gate_lines', 'prereg', 'prereg_sha')), True),
            (res['pairs'], 0), (res['blocks'], 0), ('arming_tex_hits' in res['not_evaluable'], True),
            (res['vfy']['ok'], False), (text[-1].startswith('CONSEQUENCE: NOT_ADMITTED'), True),
            (any(l.startswith('ADMISSION: NOT_ADMITTED failed=binary,') for l in text), True)]
    r2 = subprocess.run([sys.executable, str(SRC), '--root', 'C:/kyty/s120', '--tag', 'cen120', '--draft'],
                        capture_output=True, text=True, encoding='utf-8', errors='replace')
    want += [(r2.returncode, 1), ('Traceback' in r2.stderr, False), ('VERDICT: NOT_ADMITTED' in r2.stdout, True),
             ('ADMISSION: NOT_ADMITTED failed=binary,' in r2.stdout, True),
             ('env_exact,arm_asserts,gate_lines,arms,armed_fill' in r2.stdout, True)]
    bad = ['%r want %r' % (g, w) for g, w in want if g != w]
    RESULTS.append(('real_cen120', not bad, bad))

fails = [r for r in RESULTS if not r[1]]
for name, ok, why in RESULTS:
    print('%-34s %s %s' % (name, 'ok' if ok else 'FAIL', '; '.join(why)))
print('%d fixtures, %d failed' % (len(RESULTS), len(fails)))
print('ALL OK' if not fails else 'FIXTURE FAILURES')
sys.exit(0 if not fails else 1)
