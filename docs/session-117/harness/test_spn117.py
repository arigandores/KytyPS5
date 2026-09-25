"""Session 117 (DRAFT, not sealed): fixtures for spn117.py - ADMITTED on a synthetic ABBA log, every admission check
failing alone, both sides of every edge (K1_MAX_US 1200 us, CMP_MIN_PCT 90 %, walker fit strict, IDLE_GPU_MAX 10,
MIN_BLOCKS), every consequence branch (PART2, PART2_WALKER, CLOSE_A, STOP_STAGE4 by spine_bad and by spine_misal,
NOT_EVALUABLE), the frames that count for K5 (every frame after the schedule start, block edges included; frames
before it do not) and for K1 (kept frames 10..89 of arm-0 blocks only), and the report numbers of a hand pattern.
    python test_spn117.py <spn117.py>
Sizes and constants come from this suite (SMALL blocks, the build and gate hashes), never from the scorer.
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s117/fx_spn117')
NL = chr(10)
spec = importlib.util.spec_from_file_location('spn117', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)

TAG = 'spn117'
BUILD = '3cde1af8ed1af960a2216957288c6d9f54e606fd7c3e48bd97659b052a9c64b9'
PERIOD = 90
START = 1800
SMALL = 4                 # blocks per arm in most fixtures; evaluated with min_blocks=SMALL
BLOCKS = 2 * SMALL        # ABBA x2: arms 0 1 1 0 0 1 1 0
ABBA = (0, 1, 1, 0)
PRED = 'C:\\kyty\\s117\\pred\\01_spn117.md'
FAKE_SHA = 'ab' * 32
GATES_TEXT = ' '.join(Path('C:/kyty/s117/gates_base.txt').read_text(encoding='utf-8').split())
ENV_OK = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GATE_FILE': 'C:\\kyty\\s117\\gates.req',
          'KYTY_SAMPLE_GATE': 'C:\\kyty\\s117\\sample.req', 'KYTY_QUEUE_TRACE': '1',
          'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0',
          'KYTY_GATE_SCHEDULE': '90+1800:spine=1|spine=2', 'KYTY_GATE_SCHEDULE_ABBA': '1',
          'VK_SDK_PATH': 'C:\\VulkanSDK\\1.4.357.0'}
PIN = 'GpuClockPin: mode 1 - the guest GPU clock ignores the pacer speed (KYTY_GPU_CLOCK_PIN)'
SPINE = 'Spine: mode=1 snap=8000 ctx=4000 ucfg=300 sh=3000'
TEXT = ('spine=1', 'spine=2')
MAIN_DEF = dict(dt_us=33000, cpu_gpu_us=31000, draws=5300, dispatches=270)
DRAW_DEF = dict(da_walk_us=1000)
X_ARM = ({'spine_n': 12, 'spine_ns': 500000, 'spine_pk': 40000, 'spine_el': 5500, 'spine_ib': 30, 'spine_cf_br': 0,
          'spine_cf_cond': 2, 'spine_cf_pred': 1, 'spine_cf_predw': 0, 'spine_cf_ind': 20, 'spine_abort': 0,
          'spine_cmp': 0, 'spine_bad': 0, 'spine_misal': 0, 'spine_pad': 0, 'spine_lost': 0, 'spine_chk_ns': 0,
          'cram_write': 0},
         {'spine_n': 12, 'spine_ns': 520000, 'spine_pk': 40000, 'spine_el': 5500, 'spine_ib': 30, 'spine_cf_br': 0,
          'spine_cf_cond': 2, 'spine_cf_pred': 1, 'spine_cf_predw': 0, 'spine_cf_ind': 20, 'spine_abort': 0,
          'spine_cmp': 5500, 'spine_bad': 0, 'spine_misal': 0, 'spine_pad': 3, 'spine_lost': 0,
          'spine_chk_ns': 6000000, 'cram_write': 0})
RESULTS = []


def arm_of(block, order=ABBA):
    return order[block % 4]


def frame_block(n):
    """(block, index in block) of a frame > START, as the emulator labels it (frames START+1+90b .. START+90(b+1))."""
    b = (n - START - 1) // PERIOD
    return b, (n - START - 1) % PERIOD


def make(name, blocks=BLOCKS, main=None, x=None, draw=None, env=None, gates=GATES_TEXT, pins=(PIN,),
         spine_lines=(SPINE,), meta=None, gate_arm=None, gate_lines=None, drop=(), dup=(), extra_log=(),
         stdout_lines=(), pre=5, order=ABBA, post=0, strip=()):
    """A fixture directory.  main/x/draw: callables (n, block, arm, index) -> dict of overrides for that frame."""
    root = BASE / name
    root.mkdir(parents=True)
    lines = list(pins) + list(spine_lines)
    arms_seen = []
    prev = None
    first = START - pre + 1
    last = START + PERIOD * blocks + post
    for n in range(first, last + 1):
        if n > START and (n - START - 1) % PERIOD == 0:
            b = (n - START - 1) // PERIOD
            if b < blocks:
                arm = arm_of(b, order)
                if gate_arm is not None:
                    lines.extend(gate_arm(b, arm))
                else:
                    lines.append('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                                 % (arm, b, START + PERIOD * b, TEXT[arm]))
                if gate_lines is not None:
                    lines.extend(gate_lines(b, arm))
                elif prev != arm:
                    lines.append('Gate: spine=%d frame=%d' % (1 + arm, START + PERIOD * b))
                prev = arm
        if n <= START:
            b, idx, arm = 0, 0, 0
        else:
            b, idx = frame_block(n)
            arm = arm_of(min(b, blocks - 1), order)
        mv = dict(MAIN_DEF, arm=arm, blk=b if n > START else 0)
        dv = dict(DRAW_DEF)
        xv = dict(X_ARM[arm] if n > START else X_ARM[0])
        if main:
            mv.update(main(n, b, arm, idx))
        if draw:
            dv.update(draw(n, b, arm, idx))
        if x:
            xv.update(x(n, b, arm, idx))
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
            lines.append('FrameTrace-x: n=%d ' % n + ' '.join('%s=%d' % kv for kv in xv.items()))
    lines.extend(extra_log)
    (root / ('log_%s.txt' % TAG)).write_bytes((NL.join(lines) + NL).encode('utf-8'))
    (root / ('stdout_%s.txt' % TAG)).write_bytes((NL.join(stdout_lines) + NL).encode('utf-8'))
    m = dict(tag=TAG, binary_sha256=BUILD, env=dict(ENV_OK if env is None else env), hold_s=300, gates=gates,
             attempts=[dict(label='a1', outcome='ok', hold_exit=None, stable_frame=500)],
             prereg=dict(path=PRED, sha256=FAKE_SHA), pre_run=dict(gpu_util_median=2))
    if meta:
        m.update(meta)
    (root / ('%s.json' % TAG)).write_text(json.dumps(m), encoding='utf-8')
    return root


def run(name, root, installed=BUILD, min_blocks=SMALL, pred_sha=FAKE_SHA, **expect):
    res = mod.evaluate(str(root), TAG, installed_sha=installed, min_blocks=min_blocks, pred_sha=pred_sha)
    bad = []
    for key, want in expect.items():
        if key.startswith('check_'):
            got = res['checks'].get(key[6:])
        elif key == 'failed':
            got = sorted(k for k, v in res['checks'].items() if not v)
            want = sorted(want)
        else:
            got = res.get(key)
        if isinstance(want, float) and isinstance(got, float):
            if abs(got - want) > 1e-6:
                bad.append('%s=%r want %r' % (key, got, want))
        elif got != want:
            bad.append('%s=%r want %r' % (key, got, want))
    RESULTS.append((name, not bad, bad))


def case(name, expect, **kw):
    runner = {k: kw.pop(k) for k in ('installed', 'min_blocks', 'pred_sha') if k in kw}
    run(name, make(name, **kw), **runner, **expect)


OK = dict(verdict='ADMITTED', failed=[])

# ------------------------------------------------------------------ the admitted base and the consequences
case('ok', dict(OK, k5='PASS', k1='PASS', consequence='PART2', k1_us=500.0, cmp_ratio=1.0))
case('k1_edge_1200', dict(OK, k1='PASS', consequence='PART2', k1_us=1200.0),
     x=lambda n, b, arm, i: {'spine_ns': 1200000})
case('k1_over_walker_fit', dict(OK, k1='FAIL', consequence='PART2_WALKER', walker_fit=True),
     x=lambda n, b, arm, i: {'spine_ns': 1200001})
case('k1_over_walker_edge', dict(OK, k1='FAIL', consequence='CLOSE_A', walker_fit=False),
     x=lambda n, b, arm, i: {'spine_ns': 2000000}, draw=lambda n, b, arm, i: {'da_walk_us': 29000})
case('k1_over_walker_just_fits', dict(OK, k1='FAIL', consequence='PART2_WALKER', walker_fit=True),
     x=lambda n, b, arm, i: {'spine_ns': 2000000}, draw=lambda n, b, arm, i: {'da_walk_us': 28999})
case('k1_over_walker_old_rule', dict(OK, k1='FAIL', consequence='CLOSE_A', walker_fit=False),
     x=lambda n, b, arm, i: {'spine_ns': 2000000}, draw=lambda n, b, arm, i: {'da_walk_us': 30000})
# K1 reads kept frames of arm 0 only: a huge spine_ns on arm 1, or on edge frames 0..9 of arm-0 blocks, changes nothing
case('k1_arm1_ignored', dict(OK, k1='PASS', k1_us=500.0),
     x=lambda n, b, arm, i: {'spine_ns': 9000000} if arm == 1 else {})
case('k1_edges_ignored', dict(OK, k1='PASS', k1_us=500.0),
     x=lambda n, b, arm, i: {'spine_ns': 9000000} if i < 10 else {})
case('k1_mean', dict(OK, k1='PASS', k1_us=700.0),
     x=lambda n, b, arm, i: {'spine_ns': 900000} if (arm == 0 and i % 2 == 0) else {})
# K5
case('bad_one', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     x=lambda n, b, arm, i: {'spine_bad': 1} if (b == 1 and i == 40) else {})
case('bad_on_edge_frame', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     x=lambda n, b, arm, i: {'spine_bad': 1} if (b == 2 and i == 0) else {})
case('bad_before_start_ignored', dict(OK, k5='PASS', consequence='PART2'),
     x=lambda n, b, arm, i: {'spine_bad': 1} if n == START - 2 else {})
case('bad_in_first_block', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     x=lambda n, b, arm, i: {'spine_bad': 1} if n == START + 5 else {})
case('bad_at_start_frame_ignored', dict(OK, k5='PASS'), x=lambda n, b, arm, i: {'spine_bad': 1} if n == START else {})
case('bad_in_trailing_frames', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     post=3, x=lambda n, b, arm, i: {'spine_bad': 1} if n == START + PERIOD * BLOCKS + 2 else {})
case('misal_one', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     x=lambda n, b, arm, i: {'spine_misal': 1} if (b == 5 and i == 70) else {})
case('pad_lost_abort_ok', dict(OK, k5='PASS', consequence='PART2'),
     x=lambda n, b, arm, i: {'spine_pad': 7, 'spine_lost': 1, 'spine_abort': 1} if arm == 1 else {})
case('cmp_ratio_edge_90', dict(OK, k5='PASS', cmp_ratio=0.9),
     x=lambda n, b, arm, i: {'spine_cmp': 4950} if arm == 1 else {})
case('cmp_ratio_below', dict(verdict='ADMITTED', k5='NOT_EVALUABLE', consequence='NOT_EVALUABLE'),
     x=lambda n, b, arm, i: {'spine_cmp': 4949} if arm == 1 else {})
case('bad_beats_low_ratio', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     x=lambda n, b, arm, i: dict({'spine_cmp': 100} if arm == 1 else {}, **({'spine_bad': 2} if n == 1900 else {})))
# ------------------------------------------------------------------ admission, one check at a time
case('binary', dict(verdict='NOT_ADMITTED', failed=['binary'], consequence='NOT_ADMITTED'),
     meta=dict(binary_sha256='cd' * 32))
case('installed', dict(verdict='NOT_ADMITTED', failed=['installed_now']), installed='cd' * 32)
case('pin_env', dict(verdict='NOT_ADMITTED', failed=['pinned', 'env_exact']),
     env={k: v for k, v in ENV_OK.items() if k != 'KYTY_GPU_CLOCK_PIN'})
case('pin_two_lines', dict(verdict='NOT_ADMITTED', failed=['pinned']), pins=(PIN, PIN))
case('pin_mode2', dict(verdict='NOT_ADMITTED', failed=['pinned']), pins=('GpuClockPin: mode 2',))
case('pin_absent', dict(verdict='NOT_ADMITTED', failed=['pinned']), pins=())
case('env_rec', dict(verdict='NOT_ADMITTED', failed=['env_exact']), env=dict(ENV_OK, KYTY_REC='C:/x.mp4'))
case('env_no_abba', dict(verdict='NOT_ADMITTED', failed=['env_exact']),
     env={k: v for k, v in ENV_OK.items() if k != 'KYTY_GATE_SCHEDULE_ABBA'})
case('env_schedule_text', dict(verdict='NOT_ADMITTED', failed=['env_exact']),
     env=dict(ENV_OK, KYTY_GATE_SCHEDULE='90+1800:spine=1|spine=1'))
case('env_vk', dict(verdict='NOT_ADMITTED', failed=['env_vk']), env=dict(ENV_OK, VK_LAYER_PATH='C:/x'))
case('hold', dict(verdict='NOT_ADMITTED', failed=['hold']), meta=dict(hold_s=299))
case('two_attempts', dict(verdict='NOT_ADMITTED', failed=['one_ok_attempt']),
     meta=dict(attempts=[dict(label='a1', outcome='timeout', hold_exit=None),
                         dict(label='a2', outcome='ok', hold_exit=None, stable_frame=500)]))
case('hold_exit', dict(verdict='NOT_ADMITTED', failed=['one_ok_attempt']),
     meta=dict(attempts=[dict(label='a1', outcome='ok', hold_exit=3, stable_frame=500)]))
case('prereg_path', dict(verdict='NOT_ADMITTED', failed=['prereg']),
     meta=dict(prereg=dict(path='C:\\kyty\\s117\\pred\\02_x.md', sha256=FAKE_SHA)))
case('prereg_sha', dict(verdict='NOT_ADMITTED', failed=['prereg_sha']), pred_sha='cd' * 32)
case('gates_changed', dict(verdict='NOT_ADMITTED', failed=['gates_exact']), gates=GATES_TEXT.replace('dawalk=1', 'dawalk=0'))
case('gates_spine_token', dict(verdict='NOT_ADMITTED', failed=['gates_exact']), gates=GATES_TEXT + ' spine=1')
case('gates_whitespace_ok', dict(OK), gates='  ' + GATES_TEXT.replace(' ', '   ') + '  ')
case('gate_line_other', dict(verdict='NOT_ADMITTED', failed=['gate_lines']),
     extra_log=('Gate: dawalk=0 frame=2000',))
case('gate_line_other_at_block', dict(verdict='NOT_ADMITTED', failed=['gate_lines']),
     extra_log=('Gate: titleasync=2 frame=1890',))
case('gate_line_value', dict(verdict='NOT_ADMITTED', failed=['gate_lines']),
     gate_lines=lambda b, arm: ['Gate: spine=%d frame=%d' % (2 - arm, START + PERIOD * b)])
case('gate_line_frame', dict(verdict='NOT_ADMITTED', failed=['gate_lines']),
     gate_lines=lambda b, arm: ['Gate: spine=%d frame=%d' % (1 + arm, START + PERIOD * b + 1)])
case('gate_line_every_block_ok', dict(OK),
     gate_lines=lambda b, arm: ['Gate: spine=%d frame=%d' % (1 + arm, START + PERIOD * b)])
case('arm_text', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks', 'armed', 'el_ops']),
     gate_arm=lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                              % (arm, b, START + PERIOD * b, 'spine=2' if arm == 0 else 'spine=2')])
case('arm_abba_flag', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks', 'armed', 'el_ops']),
     gate_arm=lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=0 text=%s'
                              % (arm, b, START + PERIOD * b, TEXT[arm])])
case('arm_period', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks', 'armed', 'el_ops']),
     gate_arm=lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=80 abba=1 text=%s'
                              % (arm, b, START + PERIOD * b, TEXT[arm])])
case('arm_frame', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks', 'armed', 'el_ops']),
     gate_arm=lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                              % (arm, b, START + PERIOD * b + 1, TEXT[arm])])
case('arm_count3', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks', 'armed', 'el_ops']),
     gate_arm=lambda b, arm: ['GateArm: arm=%d arms=3 block=%d frame=%d period=90 abba=1 text=%s'
                              % (arm, b, START + PERIOD * b, TEXT[arm])])
case('arm_one_malformed', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks', 'armed', 'el_ops']),
     extra_log=('GateArm: arm=0 block=9',))
case('arm_malformed', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks', 'armed', 'el_ops']),
     gate_arm=lambda b, arm: ['GateArm: arm=%d block=%d' % (arm, b)])
case('arm_order_abab', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks', 'armed', 'el_ops']),
     order=(0, 1, 0, 1))
case('arm_duplicate_block', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks', 'armed', 'el_ops']),
     extra_log=('GateArm: arm=0 arms=2 block=0 frame=1800 period=90 abba=1 text=spine=1',))
case('bad_in_incomplete_frame', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'), blocks=12,
     x=lambda n, b, arm, i: {'spine_bad': 3} if n == START + 1 + PERIOD * 4 + 40 else {},
     drop=(('draw', START + 1 + PERIOD * 4 + 40),))
case('bad_in_dup_frame', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'), blocks=12,
     x=lambda n, b, arm, i: {'spine_bad': 2} if n == START + 1 + PERIOD * 5 + 40 else {},
     dup=(START + 1 + PERIOD * 5 + 40,))
case('mismatch_line_only', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     extra_log=('SpineMismatch: sub=15 el=0 op=0x15 parts=sh, reg=8',))
case('misalign_line_only', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     extra_log=('SpineMisalign: sub=15 planned=7 executed=6',))
case('abort_line_ok', dict(OK, k5='PASS'), extra_log=('SpineAbort: sub=15 packets=10 elements=2',))
case('cram_write_one', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     x=lambda n, b, arm, i: {'cram_write': 1} if (b == 2 and i == 3) else {})
case('el_ops_lo_edge', dict(OK), x=lambda n, b, arm, i: {'spine_el': 5292} if arm == 1 else {})
case('el_ops_lo', dict(verdict='NOT_ADMITTED', failed=['el_ops']),
     x=lambda n, b, arm, i: {'spine_el': 5291} if arm == 1 else {})
case('el_ops_hi_edge', dict(OK), x=lambda n, b, arm, i: {'spine_el': 5848} if arm == 1 else {})
case('el_ops_hi', dict(verdict='NOT_ADMITTED', failed=['el_ops']),
     x=lambda n, b, arm, i: {'spine_el': 5849} if arm == 1 else {})
for mk, text in (('hang', 'GpuHangAbort: tick=5'), ('slow', 'GpuWaitSlow: tick=5'), ('mhung', 'GpuMarkerHung: cs=1'),
                 ('ckpt', 'GpuCheckpointHang: op=1'), ('lost', 'Vulkan: ErrorDeviceLost'),
                 ('term', '--- std::terminate ---'), ('abort', '--- abort() ---'), ('fatal', '--- Fatal Error ---'),
                 ('unh', 'Unhandled exception: 0xc0000005'), ('err', '--- Error ---'),
                 ('skip', 'AsyncPipelines: skipped draw 0x1')):
    case('marker_' + mk, dict(verdict='NOT_ADMITTED', failed=['no_marker']), extra_log=(text,))
case('arm_block_gap', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks']),
     gate_arm=lambda b, arm: [] if b == 3 else ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                                                % (arm, b, START + PERIOD * b, TEXT[arm])])
case('field_missing', dict(verdict='NOT_ADMITTED', failed=['blocks']),
     strip=(('x', START + 1 + PERIOD * 2 + 50, 'spine_pad'),))
case('pin_malformed', dict(verdict='NOT_ADMITTED', failed=['pinned']), pins=('GpuClockPin: mode X',))
case('spine_line_absent', dict(verdict='NOT_ADMITTED', failed=['spine_logged']), spine_lines=())
case('spine_line_twice', dict(verdict='NOT_ADMITTED', failed=['spine_logged']), spine_lines=(SPINE, SPINE))
case('marker_log', dict(verdict='NOT_ADMITTED', failed=['no_marker']),
     extra_log=('GpuWaitSlow: tick=5 waited 3000 ms',))
case('marker_skipped_draw', dict(verdict='NOT_ADMITTED', failed=['no_marker']),
     extra_log=('AsyncPipelines: skipped draw 0x1234',))
case('marker_stdout', dict(verdict='NOT_ADMITTED', failed=['no_marker']),
     stdout_lines=('--- Fatal Error ---',))
case('blocks_default_20', dict(OK), blocks=40, min_blocks=None)
case('blocks_default_19', dict(verdict='NOT_ADMITTED', failed=['blocks']), blocks=38, min_blocks=None)
case('blocks_min_edge', dict(OK), min_blocks=SMALL)
case('blocks_too_few', dict(verdict='NOT_ADMITTED', failed=['blocks']), min_blocks=SMALL + 1)
case('block_missing_x', dict(verdict='NOT_ADMITTED', failed=['blocks']), drop=(('x', START + 1 + PERIOD * 3 + 50),))
case('block_missing_draw', dict(verdict='NOT_ADMITTED', failed=['blocks']),
     drop=(('draw', START + 1 + PERIOD * 4 + 5),))
case('block_dup_x', dict(verdict='NOT_ADMITTED', failed=['blocks']), dup=(START + 1 + PERIOD * 6 + 20,))
case('block_arm_label', dict(verdict='NOT_ADMITTED', failed=['blocks']),
     main=lambda n, b, arm, i: {'arm': 1 - arm} if (b == 2 and i == 30) else {})
case('block_blk_label', dict(verdict='NOT_ADMITTED', failed=['blocks']),
     main=lambda n, b, arm, i: {'blk': b + 1} if (b == 5 and i == 89) else {})
case('armed_arm0_cmp', dict(verdict='NOT_ADMITTED', failed=['armed']),
     x=lambda n, b, arm, i: {'spine_cmp': 56} if arm == 0 else {})
case('armed_arm0_cmp_1pct_ok', dict(OK), x=lambda n, b, arm, i: {'spine_cmp': 55} if arm == 0 else {})
case('armed_arm0_cmp_edge_ok', dict(OK), x=lambda n, b, arm, i: {'spine_cmp': 1} if (arm == 0 and i == 5) else {})
case('armed_arm1_no_cmp', dict(verdict='NOT_ADMITTED', failed=['armed'], k5='NOT_EVALUABLE'),
     x=lambda n, b, arm, i: {'spine_cmp': 0} if arm == 1 else {})
case('armed_arm0_no_plan', dict(verdict='NOT_ADMITTED', failed=['armed']),
     x=lambda n, b, arm, i: {'spine_n': 0} if arm == 0 else {})
case('armed_arm0_no_el', dict(verdict='NOT_ADMITTED', failed=['armed']),
     x=lambda n, b, arm, i: {'spine_el': 0} if arm == 0 else {})
case('idle_edge_10', dict(OK), meta=dict(pre_run=dict(gpu_util_median=10)))
case('idle_11', dict(verdict='NOT_ADMITTED', failed=['idle']), meta=dict(pre_run=dict(gpu_util_median=11)))
case('idle_missing', dict(verdict='NOT_ADMITTED', failed=['idle']), meta=dict(pre_run={}))
# ------------------------------------------------------------------ report numbers
root = make('report', x=lambda n, b, arm, i: {'spine_cmp': 5000} if arm == 1 else {},
            main=lambda n, b, arm, i: {'dt_us': 40000} if arm == 1 else {})
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_blocks=SMALL, pred_sha=FAKE_SHA)
rep = res['report']
want = [(rep[0]['kept_frames'], 80 * SMALL), (rep[1]['kept_frames'], 80 * SMALL), (rep[0]['complete_blocks'], SMALL),
        (rep[0]['dt_us'], 33000.0), (rep[1]['dt_us'], 40000.0), (rep[1]['spine_chk_us'], 6000.0),
        (rep[0]['spine_us'], 500.0), (rep[1]['spine_us'], 520.0), (round(res['cmp_ratio'], 9), round(5000 / 5500, 9)),
        (rep[0]['el_over_ops'], 5500 / 5570), (rep[0]['pk_per_plan'], 40000 / 12),
        (res['walker_need_us'], 1500.0), (res['dt0_us'], 33000.0), (res['frame_nospine_us'], 32500.0),
        (res['raw_k5']['spine_bad'], 0), (res['k5_lines'], 0), (res['sums_all']['spine_pad'], 3 * 90 * SMALL),
        (res['k5'], 'PASS'), (res['all_frames'], PERIOD * BLOCKS)]
bad = ['%r want %r' % (g, w) for g, w in want if (abs(g - w) > 1e-9 if isinstance(w, float) else g != w)]
RESULTS.append(('report', not bad, bad))
# the real pre-registration file, if present, is what prereg_sha compares against
real = Path(mod.PRED_PATH)
if real.is_file():
    sha = hashlib.sha256(real.read_bytes()).hexdigest()
    root = make('prereg_real', meta=dict(prereg=dict(path=PRED, sha256=sha)))
    res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_blocks=SMALL)
    RESULTS.append(('prereg_real', res['checks']['prereg_sha'], [] if res['checks']['prereg_sha'] else ['sha']))

fails = [r for r in RESULTS if not r[1]]
for name, ok, why in RESULTS:
    print('%-28s %s %s' % (name, 'ok' if ok else 'FAIL', '; '.join(why)))
print('%d fixtures, %d failed' % (len(RESULTS), len(fails)))
print('ALL OK' if not fails else 'FIXTURE FAILURES')
sys.exit(0 if not fails else 1)
