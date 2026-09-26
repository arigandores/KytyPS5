"""Session 121: fixtures for vfy121.py (seal 01, the texmemo8 verify run) - synthetic FrameTrace / -draw / -x / GateArm
logs, TAG.json, a dummy video and a glitch report (LF, built here), one fixture per admission check, per hard and soft
FAIL rule, per zero rule at several positions (before the schedule, a block edge, a window row, a partial last block),
per identity with its NEAR / FAR edge, per ratio band edge, per arming edge, the window edges, the marker attribution
edges, the video checks, the unit traps, and direct tests of the helpers.  Sizes and constants come from this suite.
    python test_vfy121.py <vfy121.py> [--real]
--real also scores the session-120 log C:/kyty/s120/log_cen120.txt (no tm8 counters, another build and schedule) in
--draft mode and requires a clean NOT_ADMITTED with the named admission failures, never a crash.
"""
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except (AttributeError, ValueError):
    pass
SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s121/fx_vfy121')
NL = chr(10)
spec = importlib.util.spec_from_file_location('vfy121', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)

TAG = 'vfy121'
BUILD = '0bd21ec24e546fbbb9b923c148fb76b57f45389ac166a71bad7410a3add738c7'
PERIOD = 90
START = 1800
BLOCKS = 8
SMALL = 2
TEXT = ('texmemo8=2 texfastcheck=1', 'texmemo8=1 texfastcheck=1', 'texmemo8=0 texfastcheck=1',
        'texmemo8=3 texfastcheck=1')
MODE = (2, 1, 0, 3)
SCHED = '90+1800:' + '|'.join(TEXT)
VALUES = tuple(dict(p.split('=') for p in t.split()) for t in TEXT)
GATES_REAL = 'C:/kyty/s121/gates_base.txt'
GATES_TEXT = ' '.join(Path(GATES_REAL).read_text(encoding='utf-8').split())
PRED_FX = BASE / 'pred_01_vfy121.md'
PRED_FX.write_bytes(('# fixture pre-registration' + NL + 'rule text' + NL).encode('utf-8'))
PRED_FX2 = BASE / 'pred_other.md'
PRED_FX2.write_bytes(('# another file' + NL).encode('utf-8'))
PRED_FX3 = BASE / 'pred_same_size.md'
PRED_FX3.write_bytes(PRED_FX.read_bytes().replace(b'rule', b'RULE'))
PSHA = hashlib.sha256(PRED_FX.read_bytes()).hexdigest()
PBYTES = len(PRED_FX.read_bytes())
FAKE_OK = BASE / 'fake_vidglitch_ok.py'
FAKE_BAD = BASE / 'fake_vidglitch_bad.py'


class _Done:
    def __init__(self, text, rc):
        self.stdout = text.encode('utf-8')
        self.stderr = b''
        self.returncode = rc


def _fake_run(argv, **kw):
    """The glitch scan in-process (no child process: mutlib runs the suite in parallel only when it spawns none).
    FAKE_OK answers only the exact call [python, script, video, '4', '12', <root>/vidframes_vfy121] with capture_output;
    FAKE_BAD answers like a crashed scan; anything else is a bad call."""
    if kw != {'capture_output': True} or not isinstance(argv, list) or len(argv) < 2 or argv[0] != sys.executable:
        return _Done('bad call', 2)
    if argv[1] == str(FAKE_OK):
        ok = (len(argv) == 6 and argv[3] == '4' and argv[4] == '12'
              and argv[5].replace(chr(92), '/').endswith('/vidframes_vfy121'))
        return _Done((argv[2] + ': 2531 frames 960x540, index entries 2531' if ok else 'bad arguments') + NL
                     + 'one-frame glitches: 0' + NL, 0)
    if argv[1] == str(FAKE_BAD):
        return _Done('Traceback: ffprobe failed' + NL, 1)
    return _Done('bad call', 2)


class _FakeSubprocess:
    run = staticmethod(_fake_run)


mod.subprocess = _FakeSubprocess
ENV_OK = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GATE_FILE': 'C:\\kyty\\s121\\gates.req',
          'KYTY_SAMPLE_GATE': 'C:\\kyty\\s121\\sample.req', 'KYTY_QUEUE_TRACE': '1',
          'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden', 'KYTY_REC': 'C:\\kyty\\s121\\rec_vfy121.mp4',
          'KYTY_GATE_SCHEDULE': SCHED, 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0',
          'VK_SDK_PATH': 'C:\\VulkanSDK\\1.4.357.0'}
PIN = 'GpuClockPin: mode 1 - the guest GPU clock ignores the pacer speed (KYTY_GPU_CLOCK_PIN)'
INJ = ('Tm8VerifyInjected: set=3 way=1 slot_id=5/7 claim_id=5/2147483655 fresh_id=5/7 rejected=1',
       'Tm8RebindInjected: mode=1 index=77 wrong=69 rejected=1')

TM8 = ['tm8_fill', 'tm8_evict', 'tm8_evict_view', 'tm8_alias', 'tm8_inval', 'tm8_mode', 'tm8_renorm', 'tm8_x2',
       'tm8_cenoff', 'tm8_look', 'tm8_hit', 'tm8_miss', 'tm8_stale', 'tm8_gain', 'tm8_vchk', 'tm8_bad', 'tm8_vctl',
       'tm8_vctl_bad', 'tm8_relive', 'tm8_inject', 'tm8_inject_miss', 'tm8_dlose', 'tm8_ddiff', 'tm8_dcc_chg',
       'tm8_rbchk', 'tm8_rbbad', 'tm8_rbinject', 'tm8_rbinject_miss', 'tm8_pb0_ns', 'tm8_pb_ns', 'tm8_pb_n']
PER_LOOKUP = TM8[9:]
TM8_ZERO = {k: 0 for k in TM8}
COMMON_X = dict(texmemo_empty=0, texmemo_stale=8, texfast_ok=44000, texfast_no=4000, texfast_rec=300,
                texfast_bad=0, tnull_hit=1400, tnull_miss=0)
VERIFY = dict(TM8_ZERO, tm8_fill=590, tm8_evict=580, tm8_evict_view=100, tm8_look=46608, tm8_hit=46000,
              tm8_miss=600, tm8_stale=8, tm8_gain=1200, tm8_vchk=1200, tm8_vctl=700, tm8_dlose=66, tm8_rbchk=45000,
              tm8_pb0_ns=5824, tm8_pb_ns=14560, tm8_pb_n=728)
X_MODE = {2: dict(COMMON_X, texmemo_collide=600, **VERIFY),
          1: dict(COMMON_X, texmemo_collide=600, **dict(TM8_ZERO, tm8_fill=590, tm8_evict=580, tm8_evict_view=100)),
          0: dict(COMMON_X, texmemo_collide=1800, **TM8_ZERO),
          3: dict(COMMON_X, texmemo_collide=600, **dict(VERIFY, tm8_inject=1, tm8_rbinject=44))}
DRAW_MODE = {2: dict(tex_hits=46000, b_texn=48008, bda_scan=60), 1: dict(tex_hits=46000, b_texn=48008, bda_scan=60),
             0: dict(tex_hits=44800, b_texn=48008, bda_scan=60), 3: dict(tex_hits=46000, b_texn=48008, bda_scan=60)}
DT = {2: 40000, 1: 33000, 0: 33400, 3: 40500}
RESULTS = []


def make(name, blocks=BLOCKS, main=None, draw=None, x=None, env=None, pins=(PIN,), meta=None, gate_arm=None,
         gate_lines=None, drop=(), dup=(), dupk=(), extra_log=INJ, stdout_lines=(), pre=5, post=0, strip=(), after=None,
         gates_copy=None, video=True, frames_delta=11, index_delta=0, report=None, glitches=()):
    """A fixture directory.  main/draw/x: callables (n, block, mode, pos) -> overrides of that frame's fields (block -1
    and pos -1 before the schedule); after: callable n -> lines written right after frame n's rows; report: callable
    (root, last_main) -> glitch report text, None = the default report (frames = last main n + frames_delta)."""
    root = BASE / name
    root.mkdir(parents=True)
    lines = list(pins)
    prev = None
    last_block = blocks + (1 if post else 0)
    last_n = None
    for n in range(START - pre + 1, START + PERIOD * blocks + post + 1):
        if n > START and (n - START - 1) % PERIOD == 0:
            b = (n - START - 1) // PERIOD
            if b < last_block:
                arm = b % 4
                if gate_arm is not None:
                    lines.extend(gate_arm(b, arm))
                else:
                    lines.append('GateArm: arm=%d arms=4 block=%d frame=%d period=90 abba=0 text=%s'
                                 % (arm, b, START + PERIOD * b, TEXT[arm]))
                if gate_lines is not None:
                    lines.extend(gate_lines(b, arm))
                else:
                    for k, v in VALUES[arm].items():
                        if (prev is None and v != '0') or (prev is not None and VALUES[prev][k] != v):
                            lines.append('Gate: %s=%s frame=%d' % (k, v, START + PERIOD * b))
                prev = arm
        if n <= START:
            b, pos, arm, mode = -1, -1, 2, 0
        else:
            b, pos = (n - START - 1) // PERIOD, (n - START - 1) % PERIOD
            arm = b % 4
            mode = MODE[arm]
        mv = dict(dt_us=DT[mode], cpu_gpu_us=DT[mode] - 1000, draws=5000, arm=arm if n > START else 0,
                  blk=b if n > START else 0)
        dv = dict(DRAW_MODE[mode])
        xv = dict(X_MODE[mode])
        if pos == 0:
            xv['tm8_mode'] = 1
            xv['tm8_inval'] = int(mode in (0, 3))
        if main:
            mv.update(main(n, b, mode, pos))
        if draw:
            dv.update(draw(n, b, mode, pos))
        if x:
            xv.update(x(n, b, mode, pos))
        for kind, sn, field in strip:
            if sn == n:
                {'main': mv, 'draw': dv, 'x': xv}[kind].pop(field, None)
        if ('main', n) not in drop:
            lines.append('FrameTrace: n=%d ' % n + ' '.join('%s=%d' % kv for kv in mv.items()))
            last_n = n
        if ('main', n) in dupk:
            lines.append('FrameTrace: n=%d ' % n + ' '.join('%s=%d' % kv for kv in mv.items()))
        if ('draw', n) not in drop:
            lines.append('FrameTrace-draw: n=%d ' % n + ' '.join('%s=%d' % kv for kv in dv.items()))
        if ('draw', n) in dupk:
            lines.append('FrameTrace-draw: n=%d ' % n + ' '.join('%s=%d' % kv for kv in dv.items()))
        if ('x', n) not in drop:
            lines.append('FrameTrace-x: n=%d ' % n + ' '.join('%s=%d' % kv for kv in xv.items()))
        if n in dup:
            lines.append('FrameTrace-x: n=%d ' % n + ' '.join('%s=%d' % kv for kv in xv.items()))
        if after:
            lines.extend(after(n))
    lines.extend(extra_log)
    (root / ('log_%s.txt' % TAG)).write_bytes((NL.join(lines) + NL).encode('utf-8'))
    (root / ('stdout_%s.txt' % TAG)).write_bytes((NL.join(stdout_lines) + NL).encode('utf-8'))
    m = dict(tag=TAG, binary_sha256=BUILD, env=dict(ENV_OK if env is None else env), schedule=SCHED, hold_s=240,
             gates=GATES_TEXT, attempts=[dict(label='attempt 1', outcome='ok', hold_exit=None, stable_frame=439)],
             prereg=dict(path=str(PRED_FX), sha256=PSHA, bytes=PBYTES), pre_run=dict(gpu_util_median=2))
    if meta:
        m.update(meta)
    (root / ('%s.json' % TAG)).write_text(json.dumps(m), encoding='utf-8')
    if gates_copy is not None:
        (root / 'gates_base.txt').write_bytes(gates_copy.encode('utf-8'))
    if video:
        (root / ('rec_%s.mp4' % TAG)).write_bytes(b'not a real video')
    if report is not None:
        text = report(root, last_n)
    else:
        vid = (root / ('rec_%s.mp4' % TAG)).as_posix()
        frames = (last_n or 0) + frames_delta
        text = NL.join(['%s: %d frames 960x540, index entries %d' % (vid, frames, frames + index_delta),
                        'one-frame glitches: %d' % len(glitches)]
                       + ['  video %5d present %6d t=%7.2fs diff_prev= 30.0 diff_next= 31.0 neighbours= 1.0 '
                          'changed_px=   1000 bbox=(1, 2, 3, 4)' % (g, g - 11, g / 30) for g in glitches]) + NL
    if text is not None:
        (root / 'glitch.txt').write_bytes(text.encode('utf-8'))
    return root


def get(res, path):
    for part in path.split('.'):
        if isinstance(res, list):
            res = res[int(part)]
        elif part in res:
            res = res[part]
        else:
            res = res[int(part)]
    return res


def run(name, root, installed=BUILD, min_blocks=SMALL, pred=(PSHA, PBYTES), pred_path=None, draft=False,
        gates_file=None, glitch='file', script=None, **expect):
    gf = str(root / 'gates_base.txt') if gates_file == 'copy' else (gates_file or GATES_REAL)
    kw = dict(draft=draft, installed_sha=installed, pred_path=pred_path or PRED_FX.as_posix(), gates_file=gf,
              min_blocks=min_blocks)
    if pred != 'default':
        kw['pred_want'] = pred
    if glitch == 'file':
        kw['glitch_report'] = str(root / 'glitch.txt')
    elif glitch == 'script':
        kw['glitch_script'] = str(script)
    bad = []
    try:
        res = mod.evaluate(str(root), TAG, **kw)
    except Exception as exc:  # a crash is a failure of the fixture, never of the suite
        RESULTS.append((name, False, ['crash: %r' % exc]))
        return
    try:
        json.dumps(res, allow_nan=False)
    except ValueError as exc:
        bad.append('json: %s' % exc)
    text = NL.join(mod.format_report(res))
    if re.search(r'(?i)\bnan\b|\binf\b', text):
        bad.append('nan/inf in the report')
    for key, want in expect.items():
        if key == 'failed':
            got = sorted(res['failed'])
            want = sorted(want)
        elif key in ('hard_bad', 'soft_bad'):
            got = sorted(res[key])
            want = sorted(want)
        elif key in ('soft_has', 'hard_has', 'failed_has'):
            lst = res[{'soft_has': 'soft_bad', 'hard_has': 'hard_bad', 'failed_has': 'failed'}[key]]
            miss = [w for w in want if w not in lst]
            if miss:
                bad.append('%s missing %r in %r' % (key, miss, lst))
            continue
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
        elif key == 'last_has':
            last = text.split(NL)[-1]
            for w in want:
                if w not in last:
                    bad.append('last line %r lacks %r' % (last[:70], w))
            continue
        else:
            got = get(res, key.replace('__', '.'))
        if isinstance(want, float) and isinstance(got, (int, float)) and not isinstance(got, bool):
            if abs(got - want) > 1e-6:
                bad.append('%s=%r want %r' % (key, got, want))
        elif got != want:
            bad.append('%s=%r want %r' % (key, got, want))
    RESULTS.append((name, not bad, bad))


def case(name, expect, **kw):
    runner = {k: kw.pop(k) for k in ('installed', 'min_blocks', 'pred', 'pred_path', 'draft', 'gates_file', 'glitch',
                                     'script') if k in kw}
    run(name, make(name, **kw), **runner, **expect)


def at(block, pos, values):
    """Overrides at one row (block, pos); block -1 = the row n = START - pos before the schedule."""
    if block == -1:
        return lambda n, b, mode, p: dict(values) if n == START - pos else {}
    return lambda n, b, mode, p: dict(values) if (b == block and p == pos) else {}


def in_mode(mode, values, window=True):
    return lambda n, b, m, p: dict(values) if (m == mode and b >= 0 and (not window or 10 <= p <= 88)) else {}


def after_row(n0, *text):
    return lambda n: list(text) if n == n0 else []


def row(block, pos):
    return START + 1 + PERIOD * block + pos


PASS = dict(verdict='PASS', failed=[], hard_bad=[], soft_bad=[])
NA = 'NOT_ADMITTED'
MARK = '--- Error --- descriptors.cpp:2463 EXIT'

# ------------------------------------------------------------------ the admitted base: every reported number
case('ok', dict(PASS))
case('ok_numbers', dict(PASS, per_mode_blocks__0=2, per_mode_blocks__1=2, per_mode_blocks__2=2, per_mode_blocks__3=2,
                        blocks=8, complete_blocks=8, last_main=2520, reports__2__dt_us=40000.0,
                        reports__1__dt_us=33000.0, reports__0__dt_us=33400.0, reports__3__dt_us=40500.0,
                        reports__3__cpu_gpu_us=39500.0, reports__0__tex_hits=44800.0, reports__1__tex_hits=46000.0,
                        reports__0__key_miss=1800.0, reports__1__key_miss=600.0, reports__2__frames=158,
                        reports__2__blocks=2, reports__2__tm8_look=46608.0, reports__3__tm8_inject=1.0,
                        reports__3__tm8_rbinject=44.0, reports__2__t_pb_ns=12.0,
                        reports__2__probe_us_frame=559.296, reports__0__t_pb_ns=None,
                        reports__0__probe_us_frame=None, reports__2__bda_regime='NEW',
                        reports__1__texfast_rec=300.0, d_tex_hits=1200.0, d_key_miss=-1200.0, key_ceiling=1800.0,
                        video__frames=2531, video__index=2531, video__glitches=0, video__tol=120.0,
                        video__presents=2520, gain_band__2=True, gain_band__3=True, x_lines=725, x_missing=0,
                        verify_markers=0, other_markers=0, lines__verify_injected=1, lines__rebind_injected=1,
                        checks__prereg=True, checks__video=True,
                        lines_has=['VERDICT: PASS' + NL,
                                   'mode 2 (arm 0, texmemo8=2 texfastcheck=1): blocks 2, estimator frames 158',
                                   'probe 12.00 ns a sampled lookup, 559.3 us a frame',
                                   'arming mode 1 - mode 0: tex_hits 1200.0 (>= +300.0), key misses -1200.0 (<= -300.0; '
                                   'both thresholds fixed in the scorer before the run)',
                                   'identity 19 (reported, not gated): 0 < rbchk <= texfast_ok + texfast_no on 4 of 4 '
                                   'mode-2/3 block windows' + NL,
                                   'NOTE (ROADMAP s121 item 3)', 'tautological'],
                        lines_not=['DRAFT', 'REPORT OF A NOT_ADMITTED', 'identity failures', 'ratio failures'],
                        last_has=['CONSEQUENCE: PASS - печать 01 пройдена']))
case('residuals_zero', dict(PASS, **{'identity_residuals__look=hit+miss+stale': [0, 0, 0, 0],
                                     'identity_residuals__fill<=collide+empty+stale+bad+vctl_bad+relive':
                                         [-1422, -1422, -1422, -1422]}))

# ------------------------------------------------------------------ admission: each check alone
case('binary', dict(verdict=NA, failed=['binary'], hard_bad=[], soft_bad=[],
                    lines_has=['REPORT OF A NOT_ADMITTED RUN', 'VERDICT: NOT_ADMITTED (admission: binary)'],
                    last_has=['CONSEQUENCE: NOT_ADMITTED']), meta=dict(binary_sha256='0' * 64))
case('installed_now', dict(verdict=NA, failed=['installed_now']), installed='f' * 64)
case('pinned_none', dict(verdict=NA, failed=['pinned']), pins=())
case('pinned_two', dict(verdict=NA, failed=['pinned']), pins=(PIN, PIN))
case('pinned_mode2', dict(verdict=NA, failed=['pinned']), pins=('GpuClockPin: mode 2 - control',))
case('pinned_garbled', dict(verdict=NA, failed=['pinned']), pins=('GpuClockPin: off',))
case('pinned_env0', dict(verdict=NA, failed=['pinned', 'env_exact']), env=dict(ENV_OK, KYTY_GPU_CLOCK_PIN='0'))
case('env_extra', dict(verdict=NA, failed=['env_exact']), env=dict(ENV_OK, KYTY_SYNC_SUBMIT='1'))
case('env_checkpoints', dict(verdict=NA, failed=['env_exact']), env=dict(ENV_OK, KYTY_GPU_CHECKPOINTS='0'))
case('env_no_rec', dict(verdict=NA, failed=['env_exact']), env={k: v for k, v in ENV_OK.items() if k != 'KYTY_REC'})
case('env_rec_other_tag', dict(verdict=NA, failed=['env_exact']),
     env=dict(ENV_OK, KYTY_REC='C:\\kyty\\s121\\rec_vfy121r.mp4'))
case('env_abba', dict(verdict=NA, failed=['env_exact']), env=dict(ENV_OK, KYTY_GATE_SCHEDULE_ABBA='1'))
case('env_markers', dict(verdict=NA, failed=['env_exact']), env=dict(ENV_OK, KYTY_GPU_MARKERS='2'))
case('env_gatefile_s120', dict(verdict=NA, failed=['env_exact']),
     env=dict(ENV_OK, KYTY_GATE_FILE='C:\\kyty\\s120\\gates.req'))
case('env_schedule', dict(verdict=NA, failed=['env_exact']),
     env=dict(ENV_OK, KYTY_GATE_SCHEDULE=SCHED.replace('texmemo8=3', 'texmemo8=2')))
case('meta_schedule', dict(verdict=NA, failed=['env_exact']), meta=dict(schedule=SCHED + ' '))
case('env_vk', dict(verdict=NA, failed=['env_vk']), env=dict(ENV_OK, VK_LAYER_PATH='C:\\VulkanSDK'))
case('hold_239', dict(verdict=NA, failed=['hold']), meta=dict(hold_s=239))
case('hold_300', dict(verdict=NA, failed=['hold']), meta=dict(hold_s=300))
case('attempts_two', dict(verdict=NA, failed=['one_ok_attempt']),
     meta=dict(attempts=[dict(outcome='ErrorDeviceLost', hold_exit=None), dict(outcome='ok', hold_exit=None)]))
case('attempt_not_ok', dict(verdict=NA, failed=['one_ok_attempt']), meta=dict(attempts=[dict(outcome='timeout',
                                                                                             hold_exit=None)]))
case('attempt_hold_exit', dict(verdict=NA, failed=['one_ok_attempt']),
     meta=dict(attempts=[dict(outcome='ok', hold_exit=3221225477)]))
case('attempts_none', dict(verdict=NA, failed=['one_ok_attempt']), meta=dict(attempts=[]))
case('prereg_sha', dict(verdict=NA, failed=['prereg']), pred=('0' * 64, PBYTES))
case('prereg_bytes', dict(verdict=NA, failed=['prereg']), pred=(PSHA, PBYTES + 1))
case('prereg_unsealed', dict(verdict=NA, failed=['prereg']), pred=(None, None))
case('prereg_unsealed_bytes', dict(verdict=NA, failed=['prereg']), pred=(PSHA, None))
case('prereg_default_constants', dict(verdict=NA, failed=['prereg']), pred='default')
case('prereg_meta_path', dict(verdict=NA, failed=['prereg']),
     meta=dict(prereg=dict(path=str(PRED_FX2), sha256=PSHA, bytes=PBYTES)))
case('prereg_meta_sha', dict(verdict=NA, failed=['prereg']),
     meta=dict(prereg=dict(path=str(PRED_FX), sha256='1' * 64, bytes=PBYTES)))
case('prereg_meta_bytes', dict(verdict=NA, failed=['prereg']),
     meta=dict(prereg=dict(path=str(PRED_FX), sha256=PSHA, bytes=PBYTES - 1)))
case('prereg_meta_none', dict(verdict=NA, failed=['prereg']), meta=dict(prereg=None))
case('prereg_file_now', dict(verdict=NA, failed=['prereg']), pred_path=PRED_FX2.as_posix(),
     meta=dict(prereg=dict(path=str(PRED_FX2), sha256=PSHA, bytes=PBYTES)))
case('prereg_all_none', dict(verdict=NA, failed=['prereg']), pred=(None, None), pred_path=(BASE / 'nope2.md').as_posix(),
     meta=dict(prereg=dict(path=str(BASE / 'nope2.md'), sha256=None, bytes=None)))
case('prereg_bytes_both', dict(verdict=NA, failed=['prereg']), pred=(PSHA, PBYTES + 1),
     meta=dict(prereg=dict(path=str(PRED_FX), sha256=PSHA, bytes=PBYTES + 1)))
case('prereg_file_same_size', dict(verdict=NA, failed=['prereg']), pred_path=PRED_FX3.as_posix(),
     meta=dict(prereg=dict(path=str(PRED_FX3), sha256=PSHA, bytes=PBYTES)))
case('prereg_file_missing', dict(verdict=NA, failed=['prereg']), pred_path=(BASE / 'nope.md').as_posix(),
     meta=dict(prereg=dict(path=str(BASE / 'nope.md'), sha256=PSHA, bytes=PBYTES)))
case('draft_skips_prereg', dict(verdict='PASS', failed=[], checks__prereg=None,
                                lines_has=['DRAFT: the pre-registration is not checked', 'skipped (draft)',
                                           'VERDICT: PASS DRAFT' + NL],
                                last_has=['CONSEQUENCE: PASS']), pred=(None, None), draft=True)
case('draft_checks_hold', dict(verdict=NA, failed=['hold']), draft=True, meta=dict(hold_s=300))
case('draft_checks_binary', dict(verdict=NA, failed=['binary']), draft=True, meta=dict(binary_sha256='0' * 64))
case('gates_text', dict(verdict=NA, failed=['gates_exact']), meta=dict(gates=GATES_TEXT + ' foo=1'))
case('gates_text_ws', dict(PASS), meta=dict(gates='  ' + GATES_TEXT.replace(' ', '   ') + ' '))
case('gates_copy_sha', dict(verdict=NA, failed=['gates_exact']), gates_file='copy', gates_copy=GATES_TEXT + NL + ' ')
case('gates_missing', dict(verdict=NA, failed=['gates_exact']), gates_file=(BASE / 'none.txt').as_posix())
case('gates_names_r1cen', dict(verdict=NA, failed=['gates_exact', 'base_names']),
     meta=dict(gates=GATES_TEXT + ' r1cen=0'))
case('gates_texmemo2_on', dict(verdict=NA, failed=['gates_exact', 'base_names']),
     meta=dict(gates=GATES_TEXT.replace('texmemo2=0', 'texmemo2=1')))
case('gates_texmemo8', dict(verdict=NA, failed=['gates_exact', 'base_names']),
     meta=dict(gates='texmemo8=1 ' + GATES_TEXT))
case('gate_line_garbled', dict(verdict=NA, failed=['gate_lines']),
     gate_lines=lambda b, arm: ['Gate: texmemo8=2=x frame=%d' % (START + PERIOD * b)] if b == 3 else [])
case('gate_line_wrong_value', dict(verdict=NA, failed=['gate_lines']),
     gate_lines=lambda b, arm: ['Gate: texmemo8=%d frame=%d' % ((MODE[arm] + 1) % 4 if b == 5 else MODE[arm],
                                                                 START + PERIOD * b)])
case('gate_line_frame', dict(verdict=NA, failed=['gate_lines']),
     gate_lines=lambda b, arm: ['Gate: texmemo8=%d frame=%d' % (MODE[arm], START + PERIOD * b + (1 if b == 2 else 0))])
case('gate_line_name', dict(verdict=NA, failed=['gate_lines']),
     gate_lines=lambda b, arm: ['Gate: texmemo8=%d frame=%d' % (MODE[arm], START + PERIOD * b)]
     + (['Gate: spcen=0 frame=%d' % (START + PERIOD * b)] if b == 4 else []))
case('gate_line_file', dict(verdict=NA, failed=['gate_lines']),
     extra_log=INJ + ('Gate: file C:\\kyty\\s121\\gates.req is too long, ignored',))
case('gate_line_before', dict(verdict=NA, failed=['gate_lines']),
     extra_log=INJ + ('Gate: texmemo8=2 frame=%d' % (START - PERIOD),))
case('gate_line_block_unknown', dict(verdict=NA, failed=['gate_lines']),
     extra_log=INJ + ('Gate: texmemo8=2 frame=%d' % (START + PERIOD * 40),))
case('gate_line_ok_all', dict(PASS), gate_lines=lambda b, arm: ['Gate: texmemo8=%d frame=%d' % (MODE[arm],
                                                                                               START + PERIOD * b),
                                                                 'Gate: texfastcheck=1 frame=%d' % (START + PERIOD * b)])
ARMS_FAIL = dict(verdict=NA, failed=['arms', 'gate_lines', 'modes'])
GA = 'GateArm: arm=%d arms=%d block=%d frame=%d period=%d abba=%d text=%s'
case('arms_text', ARMS_FAIL, gate_arm=lambda b, arm: [GA % (arm, 4, b, START + PERIOD * b, 90, 0,
                                                            TEXT[arm] + (' r1cen=0' if b == 3 else ''))])
case('arms_abba', ARMS_FAIL, gate_arm=lambda b, arm: [GA % (arm, 4, b, START + PERIOD * b, 90, 1, TEXT[arm])])
case('arms_count', ARMS_FAIL, gate_arm=lambda b, arm: [GA % (arm, 2, b, START + PERIOD * b, 90, 0, TEXT[arm])])
case('arms_period', ARMS_FAIL, gate_arm=lambda b, arm: [GA % (arm, 4, b, START + PERIOD * b, 91, 0, TEXT[arm])])
case('arms_frame', ARMS_FAIL, gate_arm=lambda b, arm: [GA % (arm, 4, b, START + PERIOD * b + (1 if b == 6 else 0),
                                                             90, 0, TEXT[arm])])
case('arms_order', ARMS_FAIL, gate_arm=lambda b, arm: [GA % ((arm + 1) % 4 if b == 1 else arm, 4, b,
                                                             START + PERIOD * b, 90, 0,
                                                             TEXT[(arm + 1) % 4 if b == 1 else arm])])
case('arms_arm_range', ARMS_FAIL, gate_arm=lambda b, arm: [GA % (4 if b == 1 else arm, 4, b, START + PERIOD * b, 90,
                                                                 0, TEXT[arm])])
case('arms_gap', ARMS_FAIL, gate_arm=lambda b, arm: [] if b == 4 else [GA % (arm, 4, b, START + PERIOD * b, 90, 0,
                                                                             TEXT[arm])])
case('arms_dup', ARMS_FAIL, gate_arm=lambda b, arm: [GA % (arm, 4, b, START + PERIOD * b, 90, 0, TEXT[arm])] * 2)
case('arms_garbled', ARMS_FAIL, gate_arm=lambda b, arm: ['GateArm: arm=%d text=%s' % (arm, TEXT[arm])] if b == 5
     else [GA % (arm, 4, b, START + PERIOD * b, 90, 0, TEXT[arm])])
case('arms_garbled_last', ARMS_FAIL, gate_arm=lambda b, arm: ['GateArm: arm=%d text=%s' % (arm, TEXT[arm])] if b == 7
     else [GA % (arm, 4, b, START + PERIOD * b, 90, 0, TEXT[arm])])
case('arms_none', ARMS_FAIL, gate_arm=lambda b, arm: [])
case('arms_first_missing', ARMS_FAIL, gate_arm=lambda b, arm: [] if b == 0 else [GA % (arm, 4, b, START + PERIOD * b,
                                                                                       90, 0, TEXT[arm])])
case('modes_min3', dict(verdict=NA, failed=['modes']), min_blocks=3)
case('modes_default_min', dict(verdict=NA, failed=['modes']), min_blocks=None)
case('modes_no_est_block', dict(verdict=NA, failed=['modes'], per_mode_blocks__0=1, reports__0__blocks=1,
                                complete_blocks=8),
     main=lambda n, b, m, p: {'draws': 3000} if b == 2 else {})
case('modes_incomplete_block', dict(verdict=NA, failed=['modes'], per_mode_blocks__1=1),
     strip=(('x', row(5, 3), 'tm8_fill'),))
case('modes_min1_blocks7', dict(PASS, per_mode_blocks__3=1), blocks=7, min_blocks=1)
case('modes_blocks7', dict(verdict=NA, failed=['modes']), blocks=7)
# markers outside mode-2/3 blocks -> NOT_ADMITTED; inside -> FAIL (hard)
case('marker_before_schedule', dict(verdict=NA, failed=['no_marker'], other_markers=1),
     after=after_row(START - 1, MARK))
case('marker_before_gatearm0', dict(verdict=NA, failed=['no_marker']), after=after_row(START, MARK))
case('marker_after_gatearm0', dict(verdict='FAIL', hard_bad=['verify_marker'], failed=[], verify_markers=1,
                                   other_markers=0), after=after_row(row(0, 0), MARK))
case('marker_mode1_window', dict(verdict=NA, failed=['no_marker']), after=after_row(row(1, 49), MARK))
case('marker_mode0_edge', dict(verdict=NA, failed=['no_marker']), after=after_row(row(2, 4), MARK))
case('marker_mode1_head', dict(verdict=NA, failed=['no_marker']), after=after_row(row(1, 0), MARK))
case('marker_mode1_tail', dict(verdict=NA, failed=['no_marker']), after=after_row(row(1, 89), MARK))
case('marker_mode0_tail', dict(verdict=NA, failed=['no_marker']), after=after_row(row(2, 89), MARK))
case('marker_mode2_tail', dict(verdict='FAIL', hard_bad=['verify_marker']), after=after_row(row(0, 89), MARK))
case('marker_mode2_window', dict(verdict='FAIL', hard_bad=['verify_marker'], failed=[], verify_markers=1),
     after=after_row(row(4, 49), MARK))
case('marker_mode3_head', dict(verdict='FAIL', hard_bad=['verify_marker']), after=after_row(row(3, 0), MARK))
case('marker_mode3_tail', dict(verdict='FAIL', hard_bad=['verify_marker']), after=after_row(row(3, 89), MARK))
case('marker_two_places', dict(verdict='FAIL', hard_bad=['verify_marker'], failed=['no_marker'], verify_markers=1,
                               other_markers=1),
     after=lambda n: [MARK] if n in (row(1, 30), row(3, 30)) else [])
case('marker_garbled_gatearm', dict(verdict=NA, failed=['arms', 'gate_lines', 'modes', 'no_marker']),
     gate_arm=lambda b, arm: ['GateArm: arm=%d garbled' % arm] if b == 4 else
     ['GateArm: arm=%d arms=4 block=%d frame=%d period=90 abba=0 text=%s' % (arm, b, START + PERIOD * b, TEXT[arm])],
     after=after_row(row(4, 30), MARK))
for _i, _m in enumerate(('GpuHangAbort: tick 5', 'GpuWaitSlow: 9000 ms', 'ErrorDeviceLost', '--- Fatal Error ---',
                         '--- std::terminate ---', '--- abort() ---', 'Unhandled exception: 0xc0000005',
                         'GpuMarkerHung: cs', 'GpuCheckpointHang: op')):
    if _i == 1:  # GpuWaitSlow is a slow (non-fatal) marker: NOT_ADMITTED anywhere, never a verify FAIL
        case('marker_kind_%d' % _i, dict(verdict=NA, failed=['no_marker'], hard_bad=[], verify_markers=0,
                                         other_markers=1), after=after_row(row(0, 30), _m))
    else:
        case('marker_kind_%d' % _i, dict(verdict='FAIL', hard_bad=['verify_marker']), after=after_row(row(0, 30), _m))
SLOW = ('GpuWaitSlow: role=4 requested=5 known=4 current=5 master=0x0 submit_backlog=0 record_backlog=0 '
        'acopy=1/1/1 acopy_pending=0')
case('marker_waitslow_mode3', dict(verdict=NA, failed=['no_marker'], hard_bad=[], verify_markers=0, other_markers=1,
                                   lines_has=['(log, mode 3, slow): GpuWaitSlow:']),
     after=after_row(row(3, 30), SLOW))
case('marker_waitslow_upper', dict(verdict=NA, failed=['no_marker'], hard_bad=[]),
     after=after_row(row(4, 30), SLOW.upper()))
case('marker_waitslow_stdout_mode3', dict(verdict=NA, failed=['no_marker'], hard_bad=[], other_markers=1),
     stdout_lines=('GpuWaitSlow: role=4 requested=5',))
case('marker_waitslow_plus_fatal', dict(verdict='FAIL', hard_bad=['verify_marker'], failed=['no_marker'],
                                        verify_markers=1, other_markers=1,
                                        lines_has=['(log, mode 2, fatal): --- Error ---']),
     after=lambda n: [SLOW] if n == row(0, 30) else ([MARK] if n == row(0, 40) else []))
case('marker_twin_mode1', dict(verdict=NA, failed=['no_marker'], hard_bad=[], other_markers=1, verify_markers=0),
     after=after_row(row(1, 49), SLOW), stdout_lines=('GpuWaitSlow: role=4 requested=5',))
case('marker_twin_fatal_mode2', dict(verdict='FAIL', hard_bad=['verify_marker'], verify_markers=1, other_markers=0),
     after=after_row(row(4, 30), MARK), stdout_lines=('--- Error ---',), blocks=5, min_blocks=1)
case('marker_twin_fatal_mode1_run_ends_mode3', dict(verdict=NA, failed=['no_marker'], hard_bad=[], verify_markers=0,
                                                    other_markers=1),
     after=after_row(row(1, 30), MARK), stdout_lines=('--- Error ---',))
case('marker_stdout_not_twin', dict(verdict='FAIL', hard_bad=['verify_marker'], failed=['no_marker'],
                                    verify_markers=1, other_markers=1),
     after=after_row(row(1, 30), MARK), stdout_lines=('--- Fatal Error --- other',))
case('marker_after_quit_mode3', dict(verdict=NA, failed=['no_marker'], hard_bad=[], verify_markers=0,
                                     other_markers=1, markers__0__0=None),
     extra_log=INJ + ('Event: quit', MARK))
case('marker_before_quit_mode3', dict(verdict='FAIL', hard_bad=['verify_marker'], verify_markers=1),
     extra_log=INJ + (MARK, 'Event: quit'))
case('marker_quit_midline_not_quit', dict(verdict='FAIL', hard_bad=['verify_marker'], verify_markers=1),
     extra_log=INJ + ('[1] Event: quit', MARK))
case('marker_stdout_last_mode3', dict(verdict='FAIL', hard_bad=['verify_marker'], failed=[]), stdout_lines=(MARK,))
case('marker_stdout_last_mode0', dict(verdict=NA, failed=['no_marker']), stdout_lines=(MARK,), blocks=7,
     min_blocks=1)
case('marker_stdout_partial_mode2', dict(verdict='FAIL', hard_bad=['verify_marker']), stdout_lines=(MARK,), post=20)
case('marker_mode2_not_admitted', dict(verdict='FAIL', hard_bad=['verify_marker'], failed=['binary']),
     after=after_row(row(0, 50), MARK), meta=dict(binary_sha256='0' * 64))
SKIP = 'AsyncPipelines: skipped draw (pipeline 0x1234 not ready)'
case('skip_window', dict(verdict=NA, failed=['no_skip_window']), after=after_row(row(1, 49), SKIP))
case('skip_window_first', dict(verdict=NA, failed=['no_skip_window']), after=after_row(row(1, 9), SKIP))
case('skip_window_last', dict(verdict=NA, failed=['no_skip_window']), after=after_row(row(6, 87), SKIP))
case('skip_pos9', dict(PASS), after=after_row(row(1, 8), SKIP))
case('skip_pos89', dict(PASS), after=after_row(row(1, 88), SKIP))
case('skip_before', dict(PASS), after=after_row(START - 3, SKIP))
case('skip_no_block', dict(PASS), after=after_row(row(7, 89), SKIP))
case('skip_unscheduled_block', dict(PASS, blocks=8), post=50, gate_lines=lambda b, arm: [],
     gate_arm=lambda b, arm: [] if b == 8 else ['GateArm: arm=%d arms=4 block=%d frame=%d period=90 abba=0 text=%s'
                                                 % (arm, b, START + PERIOD * b, TEXT[arm])],
     after=after_row(row(8, 29), SKIP))
case('streams_drop_x', dict(verdict=NA, failed=['streams']), drop=(('x', row(2, 30)),), min_blocks=1)
case('streams_drop_draw', dict(verdict=NA, failed=['streams']), drop=(('draw', row(5, 10)),), min_blocks=1)
case('streams_drop_main', dict(verdict=NA, failed=['streams']), drop=(('main', row(3, 88)),), min_blocks=1)
case('streams_dup', dict(verdict=NA, failed=['streams'], complete_blocks=7), dup=(row(1, 40),), min_blocks=1)
case('streams_dup_main', dict(verdict=NA, failed=['streams'], complete_blocks=7), dupk=(('main', row(1, 40)),),
     min_blocks=1)
case('streams_dup_draw', dict(verdict=NA, failed=['streams'], complete_blocks=7), dupk=(('draw', row(5, 20)),),
     min_blocks=1)
case('streams_dup_main_edge', dict(PASS, complete_blocks=7, per_mode_blocks__1=1,
                                   checks__streams=True, checks__modes=True), dupk=(('main', row(1, 5)),), min_blocks=1)
case('streams_strip', dict(verdict=NA, failed=['streams']), strip=(('draw', row(6, 20), 'tex_hits'),), min_blocks=1)
case('streams_strip_x', dict(verdict=NA, failed=['streams']), strip=(('x', row(6, 20), 'tm8_pb_n'),), min_blocks=1)
case('streams_arm_label', dict(verdict=NA, failed=['streams'], complete_blocks=7), main=at(4, 60, {'arm': 1}),
     min_blocks=1)
case('streams_blk_label', dict(verdict=NA, failed=['streams'], complete_blocks=7), main=at(4, 60, {'blk': 5}),
     min_blocks=1)
case('streams_edge_label', dict(PASS, complete_blocks=7), main=at(4, 3, {'arm': 1}), min_blocks=1)
case('streams_no_main', dict(verdict=NA, failed=['streams', 'modes', 'video'], last_main=None),
     drop=tuple(('main', n) for n in range(START - 10, START + 800)))
case('streams_no_x', dict(verdict=NA, failed=['streams', 'modes', 'fields_all_rows'], x_lines=0),
     drop=tuple(('x', n) for n in range(START - 10, START + 800)))
case('streams_last_main_label', dict(verdict=NA, failed=['streams'], last_main=row(5, 50)), blocks=6, min_blocks=1,
     drop=tuple((k, n) for k in ('main', 'draw', 'x') for n in range(row(5, 51), row(5, 90))),
     main=at(5, 50, {'arm': 0}))
case('streams_last_block_row', dict(verdict=NA, failed=['streams']), drop=(('x', row(7, 60)),), min_blocks=1)
case('streams_edge_row_ok', dict(PASS, per_mode_blocks__0=1), drop=(('x', row(2, 5)),), min_blocks=1)
case('streams_last_main_exempt_x', dict(PASS, per_mode_blocks__3=1), drop=(('x', row(7, 89)),), min_blocks=1)
case('streams_last_main_exempt_draw', dict(PASS, per_mode_blocks__3=1), drop=(('draw', row(7, 89)),), min_blocks=1)
case('streams_last_main_window', dict(PASS, last_main=row(5, 50)), blocks=6, post=0, min_blocks=1,
     drop=tuple((k, n) for k in ('main', 'draw', 'x') for n in range(row(5, 51), row(5, 90))) + (('x', row(5, 50)),),
     frames_delta=11)
case('streams_partial_post_ok', dict(PASS, blocks=9, complete_blocks=8), post=30)
case('fields_pre_row', dict(verdict=NA, failed=['fields_all_rows']), strip=(('x', START - 3, 'tm8_bad'),))
case('fields_post_row', dict(verdict=NA, failed=['fields_all_rows']), strip=(('x', row(8, 5), 'texfast_bad'),), post=10)
case('fields_x2', dict(verdict=NA, failed=['fields_all_rows']), strip=(('x', START - 1, 'tm8_x2'),))
case('fields_edge_row', dict(verdict=NA, failed=['fields_all_rows', 'modes'], per_mode_blocks__2=1),
     strip=(('x', row(4, 2), 'tm8_dcc_chg'),))
case('idle_11', dict(verdict=NA, failed=['idle']), meta=dict(pre_run=dict(gpu_util_median=11)))
case('idle_10', dict(PASS), meta=dict(pre_run=dict(gpu_util_median=10)))
case('idle_float', dict(verdict=NA, failed=['idle']), meta=dict(pre_run=dict(gpu_util_median=10.01)))
case('idle_none', dict(verdict=NA, failed=['idle']), meta=dict(pre_run=None))
case('idle_bool', dict(verdict=NA, failed=['idle']), meta=dict(pre_run=dict(gpu_util_median=True)))
# video
case('video_missing', dict(verdict=NA, failed=['video'], video__exists=False), video=False)
case('video_missing_no_script', dict(verdict=NA, failed=['video'], video__report=None), video=False, glitch=None,
     script=FAKE_BAD)
case('video_report_missing', dict(verdict=NA, failed=['video'], video__report=None), report=lambda r, n: None)
case('video_report_garbage', dict(verdict=NA, failed=['video']), report=lambda r, n: 'Traceback' + NL)
case('video_report_no_count', dict(verdict=NA, failed=['video']),
     report=lambda r, n: '%s: %d frames 960x540, index entries %d%s' % ((r / 'rec_vfy121.mp4').as_posix(), n + 11,
                                                                       n + 11, NL))
case('video_other_file', dict(verdict=NA, failed=['video'], video__names=False),
     report=lambda r, n: '%s: %d frames 960x540, index entries %d%sone-frame glitches: 0%s'
     % ((r / 'rec_vfy121r.mp4').as_posix(), n + 11, n + 11, NL, NL))
case('video_prefixed_name', dict(verdict=NA, failed=['video'], video__names=False),
     report=lambda r, n: '%s: %d frames 960x540, index entries %d%sone-frame glitches: 0%s'
     % ((r / 'xrec_vfy121.mp4').as_posix(), n + 11, n + 11, NL, NL))
case('video_backslash_name', dict(PASS, video__names=True),
     report=lambda r, n: '%s: %d frames 960x540, index entries %d%sone-frame glitches: 0%s'
     % (str(r / 'rec_vfy121.mp4'), n + 11, n + 11, NL, NL))
case('video_index_mismatch', dict(verdict=NA, failed=['video']), index_delta=1)
case('video_frames_tol_hi', dict(PASS), frames_delta=120)
case('video_frames_tol_hi_1', dict(verdict=NA, failed=['video']), frames_delta=121)
case('video_frames_tol_lo', dict(PASS), frames_delta=-120)
case('video_frames_tol_lo_1', dict(verdict=NA, failed=['video']), frames_delta=-121)
case('video_event_count', dict(verdict=NA, failed=['video']),
     report=lambda r, n: '%s: %d frames 960x540, index entries %d%sone-frame glitches: 2%s  video   100 present     89 '
     't=   3.33s x%s' % ((r / 'rec_vfy121.mp4').as_posix(), n + 11, n + 11, NL, NL, NL))
case('video_script_ok', dict(PASS, video__frames=2531,
                             video__report=(BASE / 'video_script_ok' / 'vfy121_glitch.txt').as_posix()),
     glitch='script', script=FAKE_OK)
case('video_script_bad', dict(verdict=NA, failed=['video']), glitch='script', script=FAKE_BAD)
case('glitch_one', dict(verdict='FAIL', hard_bad=['no_glitch'], failed=[], video__glitches=1,
                        video__events=[(2000, 1989)],
                        lines_has=['glitch video 2000 present 1989', 'VERDICT: FAIL (hard: no_glitch)'],
                        last_has=['CONSEQUENCE: FAIL - "ПРОВАЛ']), glitches=(2000,))
case('glitch_two', dict(verdict='FAIL', hard_bad=['no_glitch'], video__glitches=2), glitches=(700, 2400))
case('glitch_not_admitted', dict(verdict='FAIL', hard_bad=['no_glitch'], failed=['hold']), glitches=(700,),
     meta=dict(hold_s=100))
case('glitch_other_file', dict(verdict=NA, failed=['video'], hard_bad=[]),
     report=lambda r, n: '%s: %d frames 960x540, index entries %d%sone-frame glitches: 1%s  video   100 present     89 '
     't=   3.33s x%s' % ((r / 'other.mp4').as_posix(), n + 11, n + 11, NL, NL, NL))

# ------------------------------------------------------------------ hard FAIL: all-row zeros at every kind of position
POSITIONS = (('pre', -1, 0, 0), ('edge', 0, 3, 0), ('window', 1, 50, 0), ('post', 8, 5, 10), ('mode0', 6, 70, 0))
for _k in ('tm8_bad', 'tm8_vctl_bad', 'tm8_relive', 'tm8_rbbad', 'texfast_bad'):
    for _p, _b, _pos, _post in POSITIONS:
        case('hard_%s_%s' % (_k, _p), dict(verdict='FAIL', hard_bad=['hard_zero'], **{'all_rows__' + _k: 1}),
             x=at(_b, _pos, {_k: 1}), post=_post)
for _k in ('tm8_inject_miss', 'tm8_rbinject_miss', 'tm8_dcc_chg'):
    for _p, _b, _pos, _post in POSITIONS[:3]:
        case('struct_%s_%s' % (_k, _p), dict(verdict='FAIL', hard_bad=['struct_zero']), x=at(_b, _pos, {_k: 1}),
             post=_post)
case('hard_dup_row', dict(verdict='FAIL', hard_bad=['hard_zero'], failed=['streams'], all_rows__tm8_bad=2),
     x=at(1, 40, {'tm8_bad': 1}), dup=(row(1, 40),), min_blocks=1)
case('hard_two_kinds', dict(verdict='FAIL', hard_bad=['hard_zero', 'struct_zero']),
     x=at(3, 20, {'tm8_rbbad': 2, 'tm8_dcc_chg': 1}))
case('hard_not_admitted', dict(verdict='FAIL', hard_bad=['hard_zero'], failed=['binary']),
     x=at(2, 50, {'texfast_bad': 1}), meta=dict(binary_sha256='0' * 64))
case('hard_negative_sum', dict(verdict='FAIL', hard_bad=['hard_zero']), x=at(0, 50, {'tm8_bad': -1}))
for _name, _line in (('verify', 'Tm8VerifyMismatch: kind=gain inject=0 set=3 way=1 store=1 id_same=0'),
                     ('rebind', 'Tm8RebindMismatch: mode=1 index=77 version=3 hash=0x0'),
                     ('texfast', 'TexFastVerify: MISMATCH image=0x0 needs_work=0 memo_view=0 view=0')):
    case('line_%s' % _name, dict(verdict='FAIL', hard_bad=['no_mismatch'], **{'lines__%s_mismatch' % _name: 1}),
         after=after_row(START - 2, _line))
    case('line_%s_late' % _name, dict(verdict='FAIL', hard_bad=['no_mismatch']), extra_log=INJ + (_line,))
case('line_injected_not_mismatch', dict(PASS, lines__verify_injected=3), extra_log=INJ + INJ[:1] * 2)
case('line_verify_midline', dict(verdict='FAIL', hard_bad=['no_mismatch'], lines__verify_mismatch=1),
     extra_log=INJ + ('[12345] Tm8VerifyMismatch: kind=gain inject=0 set=3 way=1 store=1 id_same=0',))
case('line_rebind_midline', dict(verdict='FAIL', hard_bad=['no_mismatch'], lines__rebind_mismatch=1),
     after=after_row(row(4, 30), '[7] Tm8RebindMismatch: mode=1 index=77 version=3 hash=0x0'))

# ------------------------------------------------------------------ soft FAIL (evidence of an admitted run)
case('x2_pre', dict(verdict='FAIL', soft_bad=['config_zero'], hard_bad=[],
                    lines_has=['VERDICT: FAIL (evidence: config_zero)' + NL], last_has=['CONSEQUENCE: FAIL']),
     x=at(-1, 0, {'tm8_x2': 1}))
case('x2_window', dict(verdict='FAIL', soft_bad=['config_zero']), x=at(1, 50, {'tm8_x2': 1}))
case('cenoff_post', dict(verdict='FAIL', soft_bad=['config_zero']), x=at(8, 3, {'tm8_cenoff': 1}), post=10)
case('cenoff_window_mode1', dict(verdict='FAIL', soft_bad=['config_zero']), x=at(5, 40, {'tm8_cenoff': 1}))
case('x2_window_mode0', dict(verdict='FAIL', soft_bad=['config_zero']), x=at(2, 40, {'tm8_x2': 1}))
case('cenoff_edge', dict(verdict='FAIL', soft_bad=['config_zero']), x=at(5, 0, {'tm8_cenoff': 2}))
case('control_inject_dead', dict(verdict='FAIL', soft_bad=['control_alive']), x=in_mode(3, {'tm8_inject': 0}, False))
case('control_inject_edge_only', dict(verdict='FAIL', soft_bad=['control_alive']),
     x=lambda n, b, m, p: {'tm8_inject': 0 if 10 <= p <= 88 else 1} if m == 3 else {})
case('control_inject_one', dict(PASS), x=lambda n, b, m, p: {'tm8_inject': 1 if (b == 7 and p == 88) else 0}
     if m == 3 else {})
case('control_inject_wrong_mode', dict(verdict='FAIL', soft_bad=['control_alive', 'control_leak']),
     x=lambda n, b, m, p: {'tm8_inject': 0} if m == 3 else ({'tm8_inject': 1} if m == 2 else {}))
case('control_rbinject_dead', dict(verdict='FAIL', soft_bad=['control_alive']),
     x=in_mode(3, {'tm8_rbinject': 0}, False))
case('control_no_verify_line', dict(verdict='FAIL', soft_bad=['control_alive'], lines__verify_injected=0),
     extra_log=INJ[1:])
case('control_no_rebind_line', dict(verdict='FAIL', soft_bad=['control_alive']), extra_log=INJ[:1])
case('control_dead_not_admitted', dict(verdict=NA, failed=['binary'], soft_bad=['control_alive']),
     x=in_mode(3, {'tm8_inject': 0}, False), meta=dict(binary_sha256='0' * 64))
case('leak_inject_mode2', dict(verdict='FAIL', soft_bad=['control_leak']), x=at(4, 50, {'tm8_inject': 1}))
case('leak_rbinject_mode2', dict(verdict='FAIL', soft_bad=['control_leak']), x=at(0, 10, {'tm8_rbinject': 1}))
case('leak_inject_mode2_edge', dict(PASS), x=at(4, 0, {'tm8_inject': 1}))
case('leak_inject_mode2_pos89', dict(PASS), x=at(4, 89, {'tm8_rbinject': 3}))
case('leak_inject_mode1', dict(verdict='FAIL', soft_bad=['control_leak', 'dark_01']), x=at(1, 50, {'tm8_inject': 1}))
case('leak_rbinject_mode0', dict(verdict='FAIL', soft_bad=['control_leak', 'dark_01']),
     x=at(6, 88, {'tm8_rbinject': 1}))
case('alive_mode2_vchk', dict(verdict='FAIL', soft_bad=['verify_alive']),
     x=in_mode(2, {'tm8_vchk': 0, 'tm8_gain': 0}, False))
case('alive_mode3_vchk', dict(verdict='FAIL', soft_bad=['verify_alive']),
     x=in_mode(3, {'tm8_vchk': 0, 'tm8_gain': 0}, False))
case('alive_mode3_vchk_only', dict(verdict='FAIL', soft_bad=['verify_alive', 'identities']),
     x=in_mode(3, {'tm8_vchk': 0}, False))
case('only_block0', dict(verdict='FAIL', failed=[], hard_bad=[],
                         soft_bad=['control_alive', 'verify_alive', 'm1_fill', 'armed_hits', 'armed_keys']),
     blocks=1, min_blocks=0)
case('alive_mode2_gain_only', dict(verdict='FAIL', soft_bad=['verify_alive', 'identities']),
     x=in_mode(2, {'tm8_gain': 0}, False))
for _k in PER_LOOKUP:
    case('dark_mode1_%s' % _k, dict(**{'soft__dark_01': False}), x=at(1, 50, {_k: 1}))
    case('dark_mode0_%s' % _k, dict(**{'soft__dark_01': False}), x=at(6, 10, {_k: 1}))
case('dark_mode1_look_only', dict(verdict='FAIL', soft_bad=['dark_01'], hard_bad=[]), x=at(5, 88, {'tm8_look': 7}))
case('dark_mode1_edge', dict(PASS), x=at(5, 9, {'tm8_look': 7, 'tm8_pb_n': 3}))
case('dark_mode0_pos89', dict(PASS), x=at(2, 89, {'tm8_hit': 7, 'tm8_gain': 2}))
case('dark_rare_counters_ok', dict(PASS), x=lambda n, b, m, p: {'tm8_alias': 1, 'tm8_renorm': 1, 'tm8_evict': 3}
     if m == 1 else {})
case('m1_fill_zero_block', dict(verdict='FAIL', soft_bad=['m1_fill']), x=lambda n, b, m, p: {'tm8_fill': 0}
     if b == 5 else {})
case('m1_fill_edge_only', dict(verdict='FAIL', soft_bad=['m1_fill']),
     x=lambda n, b, m, p: {'tm8_fill': 0 if 10 <= p <= 88 else 5} if b == 1 else {})
case('m1_fill_one', dict(PASS), x=lambda n, b, m, p: {'tm8_fill': 1 if p == 10 else 0} if m == 1 else {})
case('m0_fill_window', dict(verdict='FAIL', soft_bad=['m0_fill']), x=at(6, 50, {'tm8_fill': 1}))
case('m0_fill_edge', dict(PASS), x=at(6, 3, {'tm8_fill': 1}))
case('m0_fill_window_first', dict(verdict='FAIL', soft_bad=['m0_fill']), x=at(2, 10, {'tm8_fill': 1}))
# arming (estimator rows: window, draws > 3000)
case('armed_hits_edge', dict(PASS, d_tex_hits=300.0), draw=in_mode(1, {'tex_hits': 45100}, False))
case('armed_hits_below', dict(verdict='FAIL', soft_bad=['armed_hits']),
     draw=lambda n, b, m, p: {'tex_hits': 45099 if (b == 5 and p == 40) else 45100} if m == 1 else {})
case('armed_hits_none', dict(verdict='FAIL', soft_bad=['armed_hits']), draw=in_mode(1, {'tex_hits': 44800}, False))
case('armed_hits_negative', dict(verdict='FAIL', soft_bad=['armed_hits', 'armed_keys']),
     draw=in_mode(0, {'tex_hits': 47000}, False), x=in_mode(0, {'texmemo_collide': 600}, False))
case('armed_keys_edge', dict(PASS, d_key_miss=-300.0), x=in_mode(1, {'texmemo_collide': 1500}, False))
case('armed_keys_above', dict(verdict='FAIL', soft_bad=['armed_keys']),
     x=lambda n, b, m, p: {'texmemo_collide': 1501 if (b == 1 and p == 40) else 1500} if m == 1 else {})
case('armed_keys_empty_counts', dict(verdict='FAIL', soft_bad=['armed_keys'], d_key_miss=0.0),
     x=in_mode(1, {'texmemo_collide': 0, 'texmemo_empty': 1800}, False))
case('armed_keys_empty_mode0', dict(PASS, d_key_miss=-1300.0), x=in_mode(0, {'texmemo_empty': 100}, False))
case('armed_est_draws', dict(PASS, d_tex_hits=1200.0),
     main=lambda n, b, m, p: {'draws': 3000} if (m == 1 and p == 40) else {},
     draw=lambda n, b, m, p: {'tex_hits': 10 ** 7} if (m == 1 and p == 40) else {})
case('armed_est_draws_3001', dict(PASS, d_tex_hits=1200.0 + (10 ** 7 - 46000) * 2 / 158),
     main=lambda n, b, m, p: {'draws': 3001} if (m == 1 and p == 40) else {},
     draw=lambda n, b, m, p: {'tex_hits': 10 ** 7} if (m == 1 and p == 40) else {})
case('armed_window_edges', dict(PASS, d_tex_hits=1200.0, d_key_miss=-1200.0),
     draw=lambda n, b, m, p: {'tex_hits': 0} if (m == 1 and p in (9, 89)) else {},
     x=lambda n, b, m, p: {'texmemo_collide': 10 ** 6} if (m == 1 and p in (0, 9, 89)) else {})
case('armed_window_pos10', dict(PASS, d_tex_hits=1200.0 - 46000 * 2 / 158),
     draw=lambda n, b, m, p: {'tex_hits': 0} if (m == 1 and p == 10) else {})
case('armed_window_pos88', dict(verdict='FAIL', soft_bad=['armed_keys'], d_key_miss=-1200.0 + 10 ** 6 * 2 / 158),
     x=lambda n, b, m, p: {'texmemo_collide': 600 + 10 ** 6} if (m == 1 and p == 88) else {})
# identities: NEAR (+-8 a block window)
case('near_look_8', dict(PASS), x=at(0, 50, {'tm8_look': 46608 + 8}))
case('near_look_9', dict(verdict='FAIL', soft_bad=['identities'], identity_failures=['look=hit+miss+stale@0']),
     x=at(0, 50, {'tm8_look': 46608 + 9}))
case('near_look_minus9', dict(verdict='FAIL', soft_bad=['identities']), x=at(4, 88, {'tm8_look': 46608 - 9}))
case('near_look_minus8', dict(PASS), x=at(4, 10, {'tm8_look': 46608 - 8}))
case('near_look_mode3_9', dict(verdict='FAIL', soft_bad=['identities'], identity_failures=['look=hit+miss+stale@3']),
     x=at(3, 60, {'tm8_look': 46608 + 9}))
case('near_look_constant_one', dict(verdict='FAIL', soft_bad=['identities']),
     x=lambda n, b, m, p: {'tm8_look': 46609} if b == 7 else {})
case('near_look_outside_window', dict(PASS), x=lambda n, b, m, p: {'tm8_look': 46708} if (b == 0 and p in (9, 89))
     else {})
case('near_look_stale_side', dict(PASS), x=at(0, 30, {'tm8_look': 46608 + 5, 'tm8_stale': 13}))
case('near_vchk_8', dict(PASS), x=at(3, 50, {'tm8_vchk': 1208}))
case('near_vchk_9', dict(verdict='FAIL', soft_bad=['identities'], identity_failures=['vchk=gain@3']),
     x=at(3, 50, {'tm8_vchk': 1209}))
case('near_vchk_gain_side', dict(verdict='FAIL', soft_bad=['identities']), x=at(0, 50, {'tm8_gain': 1191}))
# FAR: max(64, 1 per mille of the larger side)
_L11 = 46000 * 79
case('far11_rc1_525', dict(PASS), draw=at(0, 50, {'tex_hits': 46000 + 525}))
case('far11_plus_edge', dict(PASS), draw=at(0, 50, {'tex_hits': 46000 + _L11 // 999}))
case('far11_plus_over', dict(verdict='FAIL', soft_bad=['identities'],
                             identity_failures=['tex_hits=hit-bad-vctl_bad-relive@0']),
     draw=at(0, 50, {'tex_hits': 46000 + _L11 // 999 + 1}))
case('far11_minus_edge', dict(PASS), draw=at(4, 50, {'tex_hits': 46000 - _L11 // 1000}))
case('far11_minus_over', dict(verdict='FAIL', soft_bad=['identities']),
     draw=at(4, 50, {'tex_hits': 46000 - _L11 // 1000 - 1}))
case('far11_hit_side', dict(verdict='FAIL', soft_bad=['identities']),
     x=at(3, 50, {'tm8_hit': 46000 + 3700, 'tm8_look': 46608 + 3700}))
case('far11_bad_terms', dict(verdict='FAIL', hard_bad=['hard_zero'], soft_bad=[], **{'soft__identities': True}),
     draw=at(0, 50, {'tex_hits': 46000 - 5000}), x=at(0, 50, {'tm8_bad': 5000, 'tm8_fill': 590 + 5000}))
case('far11_vctl_bad_terms', dict(verdict='FAIL', hard_bad=['hard_zero'], soft_bad=[]),
     draw=at(4, 50, {'tex_hits': 46000 - 5000}), x=at(4, 50, {'tm8_vctl_bad': 5000, 'tm8_fill': 590 + 5000}))
case('far11_relive_terms', dict(verdict='FAIL', hard_bad=['hard_zero'], soft_bad=[]),
     draw=at(3, 50, {'tex_hits': 46000 - 5000}), x=at(3, 50, {'tm8_relive': 5000, 'tm8_fill': 590 + 5000}))
case('far13_floor_64', dict(PASS), x=at(0, 50, {'texmemo_collide': 600 + 64}))
case('far13_floor_65', dict(verdict='FAIL', soft_bad=['identities'], identity_failures=['miss=collide+empty@0']),
     x=at(0, 50, {'texmemo_collide': 600 + 65}))
case('far13_floor_minus65', dict(verdict='FAIL', soft_bad=['identities']), x=at(3, 50, {'texmemo_collide': 600 - 65}))
case('far13_empty_side', dict(verdict='FAIL', soft_bad=['identities']), x=at(3, 50, {'texmemo_empty': 65}))
case('far13_empty_balanced', dict(PASS), x=at(3, 50, {'texmemo_empty': 300, 'texmemo_collide': 300}))
case('far13_permille', dict(PASS), x=lambda n, b, m, p: {'tm8_miss': 100600, 'tm8_look': 146608, 'tm8_pb_n': 2291,
                                                         'texmemo_collide': 100600 + (7955 if p == 50 else 0)}
     if b == 4 else {})
case('far13_permille_over', dict(verdict='FAIL', soft_bad=['identities']),
     x=lambda n, b, m, p: {'tm8_miss': 100600, 'tm8_look': 146608, 'tm8_pb_n': 2291,
                           'texmemo_collide': 100600 + (7956 if p == 50 else 0)} if b == 4 else {})
_SLACK = 608 * 79 - 590 * 79
case('far1_bound_edge', dict(PASS), x=at(0, 50, {'tm8_fill': 590 + _SLACK + 64}))
case('far1_bound_over', dict(verdict='FAIL', soft_bad=['identities'],
                             identity_failures=['fill<=collide+empty+stale+bad+vctl_bad+relive@0']),
     x=at(0, 50, {'tm8_fill': 590 + _SLACK + 65}))
case('far1_bound_below_far', dict(PASS), x=in_mode(2, {'tm8_fill': 0}, False))
case('far1_bound_stale_side', dict(PASS), x=at(3, 50, {'tm8_fill': 590 + _SLACK + 500, 'texmemo_stale': 8 + 436,
                                                       'tm8_stale': 8 + 436, 'tm8_look': 46608 + 436}))
case('far1_bound_empty_side', dict(PASS), x=at(3, 50, {'tm8_fill': 590 + _SLACK + 500, 'texmemo_empty': 436,
                                                       'tm8_miss': 600 + 436, 'tm8_look': 46608 + 436}))
case('identity_mode1_not_checked', dict(PASS), draw=at(1, 50, {'tex_hits': 50000}))
case('identity_mode0_not_checked', dict(PASS), x=at(2, 50, {'texmemo_collide': 1800 + 5000}))
# ratio bands (RC8): vctl / (hit - gain), pb_n / look, per mode-2/3 block window
case('ratio_vctl_low_edge', dict(PASS), x=lambda n, b, m, p: {'tm8_vctl': 560} if b == 0 else {})
case('ratio_vctl_low_over', dict(verdict='FAIL', soft_bad=['ratios'], ratio_failures=['vctl/(hit-gain)@0']),
     x=lambda n, b, m, p: {'tm8_vctl': 559 if p == 50 else 560} if b == 0 else {})
case('ratio_vctl_high_edge', dict(PASS), x=lambda n, b, m, p: {'tm8_vctl': 896} if b == 3 else {})
case('ratio_vctl_high_over', dict(verdict='FAIL', soft_bad=['ratios']),
     x=lambda n, b, m, p: {'tm8_vctl': 897 if p == 50 else 896} if b == 3 else {})
case('ratio_vctl_zero', dict(verdict='FAIL', soft_bad=['ratios']), x=in_mode(2, {'tm8_vctl': 0}))
case('ratio_vctl_den_gain', dict(verdict='FAIL', soft_bad=['ratios']),
     x=lambda n, b, m, p: {'tm8_gain': 12000, 'tm8_vchk': 12000} if b == 4 else {})
case('ratio_pb_low_edge', dict(PASS), x=lambda n, b, m, p: {'tm8_pb_n': 583 if 10 <= p < 58 else 582} if b == 0
     else {})
case('ratio_pb_low_over', dict(verdict='FAIL', soft_bad=['ratios'], ratio_failures=['pb_n/look@0']),
     x=lambda n, b, m, p: {'tm8_pb_n': 583 if 10 <= p < 57 else 582} if b == 0 else {})
case('ratio_pb_high_edge', dict(PASS), x=lambda n, b, m, p: {'tm8_pb_n': 933 if 10 <= p < 22 else 932} if b == 7
     else {})
case('ratio_pb_high_over', dict(verdict='FAIL', soft_bad=['ratios']),
     x=lambda n, b, m, p: {'tm8_pb_n': 933 if 10 <= p < 23 else 932} if b == 7 else {})
case('ratio_outside_window', dict(PASS), x=lambda n, b, m, p: {'tm8_vctl': 0, 'tm8_pb_n': 0} if (m == 2 and
                                                                                              (p < 10 or p > 88))
     else {})
case('ratio_zero_den', dict(verdict='FAIL', soft_bad=['ratios', 'identities']),
     x=lambda n, b, m, p: {'tm8_look': 0} if b == 0 else {})
# report numbers: window means, estimator filter, units
case('means_window_edges', dict(PASS, reports__2__dt_us=40000.0, reports__0__cpu_gpu_us=32400.0),
     main=lambda n, b, m, p: {'dt_us': 10 ** 6, 'cpu_gpu_us': 10 ** 6} if p in (0, 9, 89) else {})
case('means_pos10', dict(PASS, reports__2__dt_us=40000.0 + (10 ** 6 - 40000) / 158),
     main=at(0, 10, {'dt_us': 10 ** 6}))
case('means_pos88', dict(PASS, reports__3__dt_us=40500.0 + (10 ** 6 - 40500) / 158),
     main=at(7, 88, {'dt_us': 10 ** 6}))
case('means_draws_3000', dict(PASS, reports__2__dt_us=40000.0, reports__2__frames=157),
     main=at(0, 50, {'dt_us': 10 ** 6, 'draws': 3000}))
case('means_draws_3001', dict(PASS, reports__2__dt_us=40000.0 + (10 ** 6 - 40000) / 158, reports__2__frames=158),
     main=at(0, 50, {'dt_us': 10 ** 6, 'draws': 3001}))
case('means_probe_units', dict(PASS, reports__3__t_pb_ns=20.0, reports__3__probe_us_frame=20.0 * 46608 / 1000),
     x=in_mode(3, {'tm8_pb_ns': 728 * 28, 'tm8_pb0_ns': 728 * 8}, False))
case('means_probe_clamp', dict(PASS, reports__2__t_pb_ns=0.0, reports__2__probe_us_frame=0.0),
     x=in_mode(2, {'tm8_pb_ns': 100, 'tm8_pb0_ns': 5824}, False))
case('means_bda_regimes', dict(PASS, reports__2__bda_regime='OLD', reports__1__bda_regime='MIXED',
                               reports__0__bda_regime='NEW', reports__3__bda_regime='NEW'),
     draw=lambda n, b, m, p: {'bda_scan': {2: 600, 1: 301, 0: 300, 3: 0}[m]})
case('means_bda_old_edge', dict(PASS, reports__2__bda_regime='MIXED'), draw=in_mode(2, {'bda_scan': 599}, False))
case('means_gain_band_out', dict(PASS, gain_band__2=False, gain_band__3=True),
     x=in_mode(2, {'tm8_gain': 2001, 'tm8_vchk': 2001}, False))
case('means_gain_band_edges', dict(PASS, gain_band__2=True, gain_band__3=True),
     x=lambda n, b, m, p: {'tm8_gain': 2000, 'tm8_vchk': 2000} if m == 2 else ({'tm8_gain': 600, 'tm8_vchk': 600}
                                                                              if m == 3 else {}))
case('means_gain_band_low', dict(PASS, gain_band__3=False), x=in_mode(3, {'tm8_gain': 599, 'tm8_vchk': 599}, False))
case('means_key_miss', dict(PASS, reports__0__key_miss=1850.0, key_ceiling=1850.0, d_key_miss=-1250.0),
     x=in_mode(0, {'texmemo_empty': 50}, False))
# the window rules act on ALL window rows, low-draw rows (draws <= 3000, not estimator rows) included
case('ident_lowdraw', dict(verdict='FAIL', soft_bad=['identities'], identity_failures=['look=hit+miss+stale@0']),
     main=at(0, 50, {'draws': 3000}), x=at(0, 50, {'tm8_look': 46608 + 9}))
case('ratio_lowdraw', dict(verdict='FAIL', soft_bad=['ratios'], ratio_failures=['vctl/(hit-gain)@0']),
     main=at(0, 50, {'draws': 3000}), x=lambda n, b, m, p: {'tm8_vctl': 559 if p == 50 else 560} if b == 0 else {})
case('dark_lowdraw', dict(verdict='FAIL', soft_bad=['dark_01']), main=at(1, 50, {'draws': 3000}),
     x=at(1, 50, {'tm8_look': 7}))
case('control_inject_lowdraw', dict(PASS), main=at(7, 50, {'draws': 3000}),
     x=lambda n, b, m, p: {'tm8_inject': 1 if (b == 7 and p == 50) else 0} if m == 3 else {})
case('m1_fill_lowdraw', dict(PASS), main=lambda n, b, m, p: {'draws': 3000} if (m == 1 and p == 50) else {},
     x=lambda n, b, m, p: {'tm8_fill': 1 if p == 50 else 0} if m == 1 else {})
case('leak_lowdraw', dict(verdict='FAIL', soft_bad=['control_leak']), main=at(4, 50, {'draws': 100}),
     x=at(4, 50, {'tm8_rbinject': 1}))
case('m0_fill_lowdraw', dict(verdict='FAIL', soft_bad=['m0_fill']), main=at(6, 50, {'draws': 100}),
     x=at(6, 50, {'tm8_fill': 1}))
# identity 19 (reported, not gated)
case('rbchk_bound_over', dict(PASS, rbchk_bound__0=False, rbchk_bound__4=True, rbchk_bound__3=True,
                              lines_has=['on 3 of 4 mode-2/3 block windows; fails at 0' + NL]),
     x=at(0, 50, {'tm8_rbchk': 45000 + 3000 * 79 + 1}))
case('rbchk_bound_edge', dict(PASS, rbchk_bound__0=True), x=at(0, 50, {'tm8_rbchk': 45000 + 3000 * 79}))
case('rbchk_bound_zero', dict(PASS, rbchk_bound__7=False), x=lambda n, b, m, p: {'tm8_rbchk': 0} if b == 7 else {})

# ------------------------------------------------------------------ direct tests of the helpers
_T = list(TEXT)
for _nm, _texts, _want in (('aa_ok', _T, True),
                           ('aa_swapped', [_T[1], _T[0], _T[2], _T[3]], False),
                           ('aa_fastcheck0', _T[:3] + ['texmemo8=3 texfastcheck=0'], False),
                           ('aa_fastcheck_missing', _T[:3] + ['texmemo8=3'], False),
                           ('aa_three', _T[:3], False),
                           ('aa_five', _T + [_T[0]], False),
                           ('aa_dup_mode', _T[:3] + ['texmemo8=2 texfastcheck=1'], False),
                           ('aa_first_wins', _T[:3] + ['texmemo8=3 texfastcheck=1 texmemo8=0'], True)):
    _got = mod.arm_asserts(_texts)
    RESULTS.append((_nm, _got is _want, [] if _got is _want else ['%r want %r' % (_got, _want)]))
for _nm, _gates, _texts, _want in (('bn_ok', GATES_TEXT, _T, True),
                                   ('bn_arm_spcen', GATES_TEXT, _T[:3] + [_T[3] + ' spcen=0'], False),
                                   ('bn_arm_r2cen', GATES_TEXT, [_T[0] + ' r2cen=0'] + _T[1:], False),
                                   ('bn_gate_bindlap', GATES_TEXT + ' bindlap=0', _T, False),
                                   ('bn_gate_pathlap', 'pathlap=1 ' + GATES_TEXT, _T, False),
                                   ('bn_pin_missing', GATES_TEXT.replace('mutsite=0 ', ''), _T, False),
                                   ('bn_pin_shadow', GATES_TEXT.replace('shadowresolve=0', 'shadowresolve=1'), _T,
                                    False),
                                   ('bn_pin_m4', GATES_TEXT.replace('m4baton=0', 'm4baton=32'), _T, False),
                                   ('bn_pin_fslean', GATES_TEXT.replace('fslean=0', 'fslean=1'), _T, False),
                                   ('bn_pin_first_wins', GATES_TEXT + ' texmemo2=1', _T, True),
                                   ('bn_absent_each', GATES_TEXT + ' slicecen=0', _T, False)):
    _got = mod.base_names_ok(_gates, _texts)
    RESULTS.append((_nm, _got is _want, [] if _got is _want else ['%r want %r' % (_got, _want)]))
for _k in ('texmemo8', 'r1cen', 'r2cen', 'spcen', 'bindwit', 'bindalt', 'blmove', 'bindfloor', 'cbmove', 'slicecen',
           'spine', 'bindlap', 'pathlap'):
    _got = mod.base_names_ok(GATES_TEXT + ' %s=0' % _k, _T)
    RESULTS.append(('bn_absent_' + _k, _got is False, [] if _got is False else ['accepted %s' % _k]))
for _nm, _arm, _want in (('ma_none', None, None), ('ma_0', 0, 2), ('ma_1', 1, 1), ('ma_2', 2, 0), ('ma_3', 3, 3),
                         ('ma_4', 4, None), ('ma_negative', -1, None)):
    _got = mod.mode_of_arm(_arm)
    RESULTS.append((_nm, _got == _want, [] if _got == _want else ['%r want %r' % (_got, _want)]))
_vd = BASE / 'unit_video'
_vd.mkdir()
(_vd / 'rec_vfy121.mp4').write_bytes(b'x')
for _nm, _frames, _last, _want in (('vc_permille_edge', 10200, 10000, True), ('vc_permille_over', 10201, 10000, False),
                                   ('vc_permille_low', 9800, 10000, True), ('vc_permille_low_over', 9799, 10000, False),
                                   ('vc_abs_floor', 5120, 5000, True), ('vc_abs_floor_over', 5121, 5000, False),
                                   ('vc_no_last', 10, None, False)):
    (_vd / 'r.txt').write_bytes(('%s: %d frames 960x540, index entries %d%sone-frame glitches: 0%s'
                                 % ((_vd / 'rec_vfy121.mp4').as_posix(), _frames, _frames, NL, NL)).encode('utf-8'))
    _got = mod.video_check(str(_vd), 'vfy121', str(_vd / 'r.txt'), 'unused', _last)['count_ok']
    RESULTS.append((_nm, _got is _want, [] if _got is _want else ['%r want %r' % (_got, _want)]))
_got = mod.video_check(str(_vd), 'vfy121', str(_vd / 'r.txt'), 'unused', 10000)['tol']
RESULTS.append(('vc_tol_value', _got == 200.0, [] if _got == 200.0 else ['%r' % _got]))
for _nm, _res, _l, _r, _want in (('wf_floor', 64, 100, 36, True), ('wf_floor_over', 65, 100, 35, False),
                                 ('wf_permille', 100, 100000, 99900, True), ('wf_permille_over', 101, 100000, 99899,
                                                                             False),
                                 ('wf_larger_side', 100, 0, 100000, True), ('wf_negative', -100, 99900, 100000, True)):
    _got = mod.within_far(_res, _l, _r)
    RESULTS.append((_nm, _got is _want, [] if _got is _want else ['%r want %r' % (_got, _want)]))
for _nm, _v, _want in (('rg_new', 300, 'NEW'), ('rg_mixed', 301, 'MIXED'), ('rg_old', 600, 'OLD'), ('rg_none', None,
                                                                                                   None)):
    _got = mod.regime(_v)
    RESULTS.append((_nm, _got == _want, [] if _got == _want else ['%r want %r' % (_got, _want)]))
_fv = mod.first_values('a=1 b=2 a=3 c')
RESULTS.append(('first_values', _fv == {'a': '1', 'b': '2'}, [] if _fv == {'a': '1', 'b': '2'} else ['%r' % _fv]))
_env = mod.env_expect('vfy121r')
_want_env = dict({k: v for k, v in ENV_OK.items() if k.startswith('KYTY_')}, KYTY_REC='C:\\kyty\\s121\\rec_vfy121r.mp4')
RESULTS.append(('env_expect_tag', _env == _want_env, [] if _env == _want_env else ['%r' % _env]))
consts = [(mod.ROOT, 'C:/kyty/s121'), (mod.TAG, 'vfy121'), (mod.TAGS, ('vfy121', 'vfy121r')), (mod.BUILD_SHA, BUILD),
          (mod.INSTALLED, os.path.expanduser('~') + '/OneDrive/Desktop/ps5 em/kyty_emulator.exe'),
          (mod.GATES_FILE, 'C:/kyty/s121/gates_base.txt'),
          (mod.GATES_SHA, '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'),
          (mod.PRED_PATH, 'C:/kyty/s121/pred/01_vfy121.md'), (mod.VIDGLITCH, 'C:/kyty/scripts/s51_vidglitch.py'),
          (mod.SCHEDULE, SCHED), (mod.HOLD_S, 240), (mod.MIN_BLOCKS, 8), (mod.ARM_TEXT, TEXT), (mod.MODE_OF_ARM, MODE),
          (mod.ARM_HITS_MIN, 300.0), (mod.ARM_KEYS_MIN, 300.0), (mod.NS_PER_US, 1000.0),
          (mod.PRED_SHA is None or bool(re.fullmatch('[0-9a-f]{64}', mod.PRED_SHA)), True),
          (mod.PRED_BYTES is None or (isinstance(mod.PRED_BYTES, int) and mod.PRED_BYTES > 0), True),
          ((mod.PRED_SHA is None) == (mod.PRED_BYTES is None), True)]
RESULTS.append(('constants', all(g == w for g, w in consts), ['%r != %r' % (g, w) for g, w in consts if g != w]))
_src = SRC.read_text(encoding='utf-8')
_lines_ok = (re.search(r"(?m)^PRED_SHA = (None|'[0-9a-f]{64}')", _src) is not None
             and re.search(r'(?m)^PRED_BYTES = (None|[0-9]+)', _src) is not None and chr(13) not in _src)
RESULTS.append(('pred_lines_lf', _lines_ok, [] if _lines_ok else ['PRED lines or CR']))
_argv = sys.argv
try:
    sys.argv = ['vfy121.py', '--tag', 'bogus121']
    _rc = mod.main()
except Exception as _exc:  # a crash (e.g. no bogus121.json) is a fixture failure, not a suite crash
    _rc = 'crash: %r' % _exc
finally:
    sys.argv = _argv
RESULTS.append(('main_unknown_tag', _rc == 2, [] if _rc == 2 else ['rc %r' % _rc]))

# ------------------------------------------------------------------ --real: a session-120 log (no tm8 counters)
if '--real' in sys.argv:
    bad = []
    try:
        res = mod.evaluate('C:/kyty/s120', 'cen120', draft=True, installed_sha=BUILD)
        text = NL.join(mod.format_report(res))
        want = [(res['verdict'], 'NOT_ADMITTED'), (res['hard_bad'], []),
                (sorted(res['failed']), sorted(['binary', 'env_exact', 'hold', 'gate_lines', 'arms', 'modes',
                                                'fields_all_rows', 'video'])),
                (res['checks']['prereg'], None), (res['checks']['pinned'], True),
                (res['checks']['gates_exact'], True), (res['checks']['one_ok_attempt'], True),
                (res['video']['exists'], False), (res['blocks'], 0), (res['x_missing'], res['x_lines']),
                (res['x_lines'] > 7000, True), ('VERDICT: NOT_ADMITTED (admission: ' in text, True),
                ('REPORT OF A NOT_ADMITTED RUN' in text, True), (text.split(NL)[-1].startswith(
                    'CONSEQUENCE: NOT_ADMITTED'), True)]
        bad = ['%r want %r' % (g, w) for g, w in want if g != w]
        json.dumps(res, allow_nan=False)
    except Exception as exc:
        bad.append('crash: %r' % exc)
    RESULTS.append(('real_cen120', not bad, bad))

fails = [r for r in RESULTS if not r[1]]
for name, ok, why in RESULTS:
    print('%-40s %s %s' % (name, 'ok' if ok else 'FAIL', '; '.join(why)))
print('%d fixtures, %d failed' % (len(RESULTS), len(fails)))
print('ALL OK' if not fails else 'FIXTURE FAILURES')
sys.exit(0 if not fails else 1)
