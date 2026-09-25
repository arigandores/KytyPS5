"""Session 118: fixtures for spk118.py - ADMITTED on a synthetic P|M ABBA log, every admission check failing alone,
both sides of every edge (CMP_MIN_PCT 90 %, SAFE_MAX_PCT 10 %, EL_OPS 95..105 %, K3 250 permille, K4 300 permille,
K4_MIN_PCT 50 %, IDLE_GPU_MAX 10, MIN_BLOCKS), every consequence (STAGE3, W2_CEILING, CLOSE_A, STOP_STAGE4 by K5 and by C,
NOT_EVALUABLE), the frames each verdict reads, and the report numbers.
    python test_spk118.py <spk118.py>
Sizes and constants come from this suite, never from the scorer.
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s118/fx_spk118')
NL = chr(10)
spec = importlib.util.spec_from_file_location('spk118', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)

TAG = 'spk118'
BUILD = '321175ab43ebba1664b03d307cb09e61782505a4f9628196c2f089414babcf76'
PERIOD = 90
START = 1800
SMALL = 4
BLOCKS = 2 * SMALL
ABBA = (0, 1, 1, 0)
PRED = 'C:\\kyty\\s118\\pred\\01_spk118.md'
FAKE_SHA = 'ab' * 32
GATES_TEXT = ' '.join(Path('C:/kyty/s118/gates_base.txt').read_text(encoding='utf-8').split())
TEXT = ('spine=2 slicecen=1 takelap=0 bindlap=0 pathlap=0 mutsite=0',
        'spine=0 slicecen=0 takelap=1 bindlap=1 pathlap=1 mutsite=1')
VALUES = tuple(dict(p.split('=') for p in t.split()) for t in TEXT)
ENV_OK = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GATE_FILE': 'C:\\kyty\\s118\\gates.req',
          'KYTY_SAMPLE_GATE': 'C:\\kyty\\s118\\sample.req', 'KYTY_QUEUE_TRACE': '1',
          'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0',
          'KYTY_GATE_SCHEDULE': '90+1800:' + TEXT[0] + '|' + TEXT[1], 'KYTY_GATE_SCHEDULE_ABBA': '1',
          'VK_SDK_PATH': 'C:\\VulkanSDK\\1.4.357.0'}
PIN = 'GpuClockPin: mode 1 - the guest GPU clock ignores the pacer speed (KYTY_GPU_CLOCK_PIN)'
SPINE = 'Spine: mode=2 snap=4096 ctx=2672 ucfg=148 sh=1208'
MAIN_DEF = dict(dt_us=33000, cpu_gpu_us=31000, draws=5300, dispatches=270)
DRAW_DEF = dict(da_take_us=3000, bda_scan=50)
ZERO_M = {k: 0 for k in ('da_t_n', 'da_t_key_us', 'da_t_prb_us', 'da_t_pfa_us', 'da_t_pfb_us', 'da_t_ver_us',
                         'da_t_cpy_us', 'bl_stage_n', 'bl_prep_us', 'bl_img_us', 'bl_buf_us', 'bl_res_us', 'bl_smp_us',
                         'bl_sd_us', 'bl_tr_us', 'bl_wr_us', 'bl_em_us', 'mh_pro_us', 'mh_rt_us', 'mh_prog_us',
                         'mh_bind_us', 'mh_emit_us', 'mh_tail_us', 'mh_disp_us', 'mh_draws', 'pl_em_vtx_ns',
                         'pl_em_rt_ns', 'pl_em_pipe_ns', 'pl_em_com_ns', 'pl_em_rec_ns', 'pl_em_rest_ns', 'pl_em_n')}
ZERO_P = {k: 0 for k in ('spine_n', 'spine_ns', 'spine_el', 'spine_abort', 'spine_cmp', 'spine_bad', 'spine_misal',
                         'spine_unc', 'carry_cmp', 'carry_bad', 'carry_skip', 'cram_write', 'sc_frames', 'sc_el',
                         'sc_runs', 'k3_max', 'k4_w2_n', 'k4_w2_any', 'k4_w2_dep', 'k4_w2_fmax', 'k4_w4_n',
                         'k4_w4_any', 'k4_w4_dep', 'k4_w4_fmax', 'k4_nocut', 'sc_ns')}
X_P = dict(ZERO_M, **dict(ZERO_P, spine_n=8, spine_ns=900000, spine_el=5500, spine_cmp=5500, carry_cmp=8,
                          sc_frames=1, sc_el=5500, sc_runs=190, k3_max=900, k4_w2_n=1, k4_w2_any=260, k4_w2_dep=50,
                          k4_w2_fmax=550, k4_w4_n=1, k4_w4_any=740, k4_w4_dep=200, k4_w4_fmax=300, sc_ns=2500000))
X_M = dict(ZERO_P, **dict(ZERO_M, da_t_n=8800, da_t_key_us=130, da_t_prb_us=190, da_t_pfa_us=600, da_t_pfb_us=300,
                          da_t_ver_us=1250, da_t_cpy_us=470, bl_stage_n=9200, bl_prep_us=4300, bl_img_us=1100,
                          bl_buf_us=3900, bl_res_us=3300, bl_smp_us=350, bl_sd_us=420, bl_tr_us=990, bl_wr_us=700,
                          bl_em_us=480, mh_pro_us=340, mh_rt_us=810, mh_prog_us=6800, mh_bind_us=11400, mh_emit_us=7700,
                          mh_tail_us=220, mh_disp_us=2500, mh_draws=5100, pl_em_vtx_ns=1400000, pl_em_rt_ns=1600000,
                          pl_em_pipe_ns=760000, pl_em_com_ns=2400000, pl_em_rec_ns=1300000, pl_em_rest_ns=50000,
                          pl_em_n=5100))
X_ARM = (X_P, X_M)
RESULTS = []


def arm_of(block, order=ABBA):
    return order[block % 4]


def make(name, blocks=BLOCKS, main=None, x=None, draw=None, env=None, gates=GATES_TEXT, pins=(PIN,),
         spine_lines=(SPINE,), meta=None, gate_arm=None, gate_lines=None, drop=(), dup=(), extra_log=(),
         stdout_lines=(), pre=5, order=ABBA, post=0, strip=()):
    """A fixture directory.  main/x/draw: callables (n, block, arm, index) -> dict of overrides for that frame."""
    root = BASE / name
    root.mkdir(parents=True)
    lines = list(pins) + list(spine_lines)
    prev = None
    for n in range(START - pre + 1, START + PERIOD * blocks + post + 1):
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
                    for k, v in VALUES[arm].items():
                        if prev is None and v == '0':
                            continue
                        lines.append('Gate: %s=%s frame=%d' % (k, v, START + PERIOD * b))
                prev = arm
        if n <= START:
            b, idx, arm = 0, 0, 1
        else:
            b, idx = (n - START - 1) // PERIOD, (n - START - 1) % PERIOD
            arm = arm_of(min(b, blocks - 1), order)
        mv = dict(MAIN_DEF, arm=arm if n > START else 0, blk=b if n > START else 0)
        dv = dict(DRAW_DEF)
        xv = dict(X_ARM[arm])
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
        if key == 'failed':
            got = sorted(k for k, v in res['checks'].items() if not v)
            want = sorted(want)
        elif key.startswith('k4w'):
            got = res['k4'][int(key[3])][key[5:]]
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
P = lambda f: (lambda n, b, arm, i: f(n, b, i) if arm == 0 else {})

# ------------------------------------------------------------------ the admitted base and the consequences
case('ok', dict(OK, k5='PASS', carry='PASS', safe=True, consequence='STAGE3', w_max=8, k4w2_verdict='PASS',
                k4w4_verdict='PASS'))
case('k4w2_edge_300', dict(OK, consequence='STAGE3', k4w2_verdict='PASS', k4w2_median=300),
     x=P(lambda n, b, i: {'k4_w2_dep': 300}))
case('k4w2_fail_301', dict(OK, consequence='CLOSE_A', k4w2_verdict='FAIL'), x=P(lambda n, b, i: {'k4_w2_dep': 301}))
case('k4w4_edge_300', dict(OK, consequence='STAGE3', k4w4_verdict='PASS'), x=P(lambda n, b, i: {'k4_w4_dep': 300}))
case('k4w4_fail_301', dict(OK, consequence='W2_CEILING', k4w4_verdict='FAIL'), x=P(lambda n, b, i: {'k4_w4_dep': 301}))
case('k4_median_not_mean', dict(OK, consequence='STAGE3', k4w2_verdict='PASS', k4w2_median=50),
     x=P(lambda n, b, i: {'k4_w2_dep': 900} if i % 5 == 0 else {}))
case('k4w4_nocut_ne', dict(OK, consequence='W2_CEILING', k4w4_verdict='NOT_EVALUABLE'),
     x=P(lambda n, b, i: {'k4_w4_n': 0} if i % 2 == 0 else {}))
case('k4w4_half_ok', dict(OK, consequence='STAGE3', k4w4_verdict='PASS'),
     x=P(lambda n, b, i: {'k4_w4_n': 0} if i < 39 else {}))
case('k4w2_nocut_ne', dict(OK, consequence='NOT_EVALUABLE', k4w2_verdict='NOT_EVALUABLE'),
     x=P(lambda n, b, i: {'k4_w2_n': 0} if i % 2 == 0 else {}))
case('k4_two_frames_row_skipped', dict(OK, consequence='STAGE3', k4w2_median=50),
     x=P(lambda n, b, i: {'sc_frames': 2, 'k4_w2_dep': 999} if i == 40 else {}))
case('k3_edge_250', dict(OK, w_max=4), x=P(lambda n, b, i: {'k3_max': 1375}))
case('k3_below_249', dict(OK, w_max=8), x=P(lambda n, b, i: {'k3_max': 1369}))
case('k5_bad', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     x=P(lambda n, b, i: {'spine_bad': 1} if (b == 0 and i == 40) else {}))
case('k5_bad_edge_frame', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     x=lambda n, b, arm, i: {'spine_bad': 1} if (b == 2 and i == 0) else {})
case('k5_bad_before_start_ignored', dict(OK, k5='PASS'), x=lambda n, b, arm, i: {'spine_bad': 1} if n == START else {})
case('k5_bad_first_block', dict(verdict='ADMITTED', k5='FAIL'),
     x=lambda n, b, arm, i: {'spine_bad': 1} if n == START + 1 else {})
case('k5_misal', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     x=P(lambda n, b, i: {'spine_misal': 1} if (b == 3 and i == 50) else {}))
case('k5_cram', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     x=lambda n, b, arm, i: {'cram_write': 1} if (b == 1 and i == 5) else {})
case('k5_mismatch_line', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     extra_log=('SpineMismatch: sub=1 el=0 op=0x15 parts=sh, reg=8',))
case('k5_misalign_line', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     extra_log=('SpineMisalign: sub=1 planned=7 executed=6',))
case('k5_bad_in_dup', dict(verdict='ADMITTED', k5='FAIL'), blocks=12,
     x=lambda n, b, arm, i: {'spine_bad': 2} if n == START + 1 + PERIOD * 5 + 40 else {},
     dup=(START + 1 + PERIOD * 5 + 40,))
case('k5_cmp_edge_90', dict(OK, k5='PASS'), x=P(lambda n, b, i: {'spine_cmp': 4950}))
case('k5_cmp_below', dict(verdict='ADMITTED', k5='NOT_EVALUABLE', consequence='NOT_EVALUABLE'),
     x=P(lambda n, b, i: {'spine_cmp': 4949}))
case('c_bad', dict(verdict='ADMITTED', carry='FAIL', consequence='STOP_STAGE4'),
     x=P(lambda n, b, i: {'carry_bad': 1} if (b == 3 and i == 20) else {}))
case('c_bad_edge_frame', dict(verdict='ADMITTED', carry='FAIL'),
     x=lambda n, b, arm, i: {'carry_bad': 1} if (b == 1 and i == 1) else {})
case('c_line', dict(verdict='ADMITTED', carry='FAIL', consequence='STOP_STAGE4'),
     extra_log=('SpineCarry: sub=5 parts=ctx, reg=8',))
case('c_cmp_edge', dict(OK, carry='PASS'), x=P(lambda n, b, i: {'carry_cmp': 9, 'spine_n': 11, 'carry_skip': 1}))
case('c_cmp_below', dict(verdict='ADMITTED', carry='NOT_EVALUABLE', consequence='NOT_EVALUABLE'),
     x=P(lambda n, b, i: {'carry_cmp': 8, 'spine_n': 10, 'carry_skip': 1}))
case('c_skip_counts', dict(OK, carry='PASS'), x=P(lambda n, b, i: {'carry_cmp': 4, 'carry_skip': 4}))
case('safe_edge_10', dict(OK, safe=True, k5='PASS'), x=P(lambda n, b, i: {'spine_n': 10, 'spine_abort': 1,
                                                                           'carry_cmp': 10}))
case('safe_over', dict(verdict='ADMITTED', safe=False, k5='NOT_EVALUABLE', carry='NOT_EVALUABLE',
                       consequence='NOT_EVALUABLE'),
     x=P(lambda n, b, i: {'spine_n': 10, 'spine_abort': 1, 'spine_unc': 1, 'carry_cmp': 10}))
case('safe_over_bad_still_fails', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     x=P(lambda n, b, i: dict({'spine_unc': 5}, **({'spine_bad': 1} if i == 30 else {}))))
case('safe_over_11', dict(verdict='ADMITTED', safe=False, k5='NOT_EVALUABLE', consequence='NOT_EVALUABLE'),
     x=P(lambda n, b, i: {'spine_n': 100, 'spine_abort': 11, 'carry_cmp': 100}))
# arm-P blocks are 0, 3, 4, 7: 40 + 40 + 39 + 39 = 158 qualifying frames of 316 = exactly 50 %
case('k4w4_q_exact_50', dict(OK, consequence='STAGE3', k4w4_verdict='PASS'),
     x=P(lambda n, b, i: {'k4_w4_n': 0} if i < (49 if b in (0, 3) else 50) else {}))
LATE = 'FrameTrace-x: n=%d ' % (START + 1 + PERIOD * 3 + 40) + ' '.join('%s=%d' % kv for kv in dict(X_P, spine_bad=1).items())
case('k5_bad_in_late_dup', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'), blocks=12,
     extra_log=(LATE,))
case('k3_two_frame_rows', dict(OK, w_max=8, consequence='NOT_EVALUABLE', k4w2_verdict='NOT_EVALUABLE'),
     x=P(lambda n, b, i: {'sc_frames': 2, 'k3_max': 2000, 'k4_w2_dep': 999, 'k4_w4_dep': 999} if i % 20 < 11 else {}))
# item 4 (m2): rows whose W-window count is 2 are not K4 rows; with_pred = 0; the order of the consequences
case('k4w2_n2_rows_skipped', dict(OK, consequence='STAGE3', k4w2_verdict='PASS', k4w2_median=50),
     x=P(lambda n, b, i: {'k4_w2_n': 2, 'k4_w2_dep': 999} if i % 5 == 0 else {}))
case('k4w4_n2_majority_ne', dict(OK, consequence='W2_CEILING', k4w4_verdict='NOT_EVALUABLE'),
     x=P(lambda n, b, i: {'k4_w4_n': 2} if i % 2 == 0 else {}))
case('k4w2_n2_majority_ne', dict(OK, consequence='NOT_EVALUABLE', k4w2_verdict='NOT_EVALUABLE'),
     x=P(lambda n, b, i: {'k4_w2_n': 2} if i % 2 == 0 else {}))
case('with_pred_zero', dict(OK, with_pred=0, carry='NOT_EVALUABLE', consequence='NOT_EVALUABLE'),
     x=P(lambda n, b, i: {'carry_skip': 8}))
case('order_k5_fail_over_close', dict(verdict='ADMITTED', k5='FAIL', k4w2_verdict='FAIL', consequence='STOP_STAGE4'),
     x=P(lambda n, b, i: dict({'k4_w2_dep': 301}, **({'spine_bad': 1} if i == 30 else {}))))
case('order_c_fail_over_close', dict(verdict='ADMITTED', carry='FAIL', k4w2_verdict='FAIL', consequence='STOP_STAGE4'),
     x=P(lambda n, b, i: dict({'k4_w2_dep': 301}, **({'carry_bad': 1} if i == 30 else {}))))
case('order_k5_ne_over_close', dict(OK, k5='NOT_EVALUABLE', k4w2_verdict='FAIL', consequence='NOT_EVALUABLE'),
     x=P(lambda n, b, i: {'k4_w2_dep': 301, 'spine_cmp': 4949}))
case('order_c_ne_over_close', dict(OK, carry='NOT_EVALUABLE', k4w2_verdict='FAIL', consequence='NOT_EVALUABLE'),
     x=P(lambda n, b, i: {'k4_w2_dep': 301, 'carry_skip': 8}))
case('order_k5_fail_over_ne', dict(verdict='ADMITTED', k5='FAIL', carry='NOT_EVALUABLE', consequence='STOP_STAGE4'),
     x=P(lambda n, b, i: dict({'carry_skip': 8}, **({'spine_bad': 1} if i == 30 else {}))))
# ------------------------------------------------------------------ admission, one check at a time
case('binary', dict(verdict='NOT_ADMITTED', failed=['binary'], consequence='NOT_ADMITTED'),
     meta=dict(binary_sha256='cd' * 32))
case('installed', dict(verdict='NOT_ADMITTED', failed=['installed_now']), installed='cd' * 32)
case('pin_env', dict(verdict='NOT_ADMITTED', failed=['pinned', 'env_exact']),
     env={k: v for k, v in ENV_OK.items() if k != 'KYTY_GPU_CLOCK_PIN'})
case('pin_two', dict(verdict='NOT_ADMITTED', failed=['pinned']), pins=(PIN, PIN))
case('pin_mode2', dict(verdict='NOT_ADMITTED', failed=['pinned']), pins=('GpuClockPin: mode 2',))
case('pin_malformed', dict(verdict='NOT_ADMITTED', failed=['pinned']), pins=('GpuClockPin: mode X',))
case('env_rec', dict(verdict='NOT_ADMITTED', failed=['env_exact']), env=dict(ENV_OK, KYTY_REC='C:/x.mp4'))
case('env_schedule', dict(verdict='NOT_ADMITTED', failed=['env_exact']),
     env=dict(ENV_OK, KYTY_GATE_SCHEDULE='90+1800:' + TEXT[1] + '|' + TEXT[0]))
case('env_vk', dict(verdict='NOT_ADMITTED', failed=['env_vk']), env=dict(ENV_OK, VK_LAYER_PATH='C:/x'))
case('hold', dict(verdict='NOT_ADMITTED', failed=['hold']), meta=dict(hold_s=299))
case('two_attempts', dict(verdict='NOT_ADMITTED', failed=['one_ok_attempt']),
     meta=dict(attempts=[dict(label='a1', outcome='timeout', hold_exit=None),
                         dict(label='a2', outcome='ok', hold_exit=None, stable_frame=500)]))
case('hold_exit', dict(verdict='NOT_ADMITTED', failed=['one_ok_attempt']),
     meta=dict(attempts=[dict(label='a1', outcome='ok', hold_exit=3, stable_frame=500)]))
case('prereg_path', dict(verdict='NOT_ADMITTED', failed=['prereg']),
     meta=dict(prereg=dict(path='C:\\kyty\\s118\\pred\\02_x.md', sha256=FAKE_SHA)))
case('prereg_sha', dict(verdict='NOT_ADMITTED', failed=['prereg_sha']), pred_sha='cd' * 32)
case('gates_changed', dict(verdict='NOT_ADMITTED', failed=['gates_exact']), gates=GATES_TEXT.replace('dawalk=1', 'dawalk=0'))
case('gates_whitespace_ok', dict(OK), gates='  ' + GATES_TEXT.replace(' ', '   ') + '  ')
case('gate_other_name', dict(verdict='NOT_ADMITTED', failed=['gate_lines']),
     extra_log=('Gate: dawalk=0 frame=1890',))
case('gate_wrong_value', dict(verdict='NOT_ADMITTED', failed=['gate_lines']),
     extra_log=('Gate: takelap=0 frame=1890',))
case('gate_off_block', dict(verdict='NOT_ADMITTED', failed=['gate_lines']),
     extra_log=('Gate: spine=2 frame=1801',))
case('gate_malformed', dict(verdict='NOT_ADMITTED', failed=['gate_lines']), extra_log=('Gate: spine=2',))
case('gate_every_block_ok', dict(OK),
     gate_lines=lambda b, arm: ['Gate: %s=%s frame=%d' % (k, v, START + PERIOD * b) for k, v in VALUES[arm].items()])
ARM_FAIL = dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks', 'armed', 'el_ops'])
case('arm_text', ARM_FAIL, gate_arm=lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                                                    % (arm, b, START + PERIOD * b, TEXT[0])])
case('arm_count', ARM_FAIL, gate_arm=lambda b, arm: ['GateArm: arm=%d arms=3 block=%d frame=%d period=90 abba=1 text=%s'
                                                     % (arm, b, START + PERIOD * b, TEXT[arm])])
case('arm_period', ARM_FAIL, gate_arm=lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=80 abba=1 text=%s'
                                                      % (arm, b, START + PERIOD * b, TEXT[arm])])
case('arm_abba', ARM_FAIL, gate_arm=lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=0 text=%s'
                                                    % (arm, b, START + PERIOD * b, TEXT[arm])])
case('arm_frame', ARM_FAIL, gate_arm=lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                                                     % (arm, b, START + PERIOD * b + 1, TEXT[arm])])
case('arm_order', ARM_FAIL, order=(0, 1, 0, 1))
case('arm_one_malformed', ARM_FAIL, extra_log=('GateArm: arm=0 block=9',))
case('arm_dup', ARM_FAIL, extra_log=('GateArm: arm=0 arms=2 block=0 frame=1800 period=90 abba=1 text=' + TEXT[0],))
case('arm_gap', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks']),
     gate_arm=lambda b, arm: [] if b == 3 else ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                                                % (arm, b, START + PERIOD * b, TEXT[arm])])
case('spine_absent', dict(verdict='NOT_ADMITTED', failed=['spine_logged']), spine_lines=())
case('spine_twice', dict(verdict='NOT_ADMITTED', failed=['spine_logged']), spine_lines=(SPINE, SPINE))
for mk, text in (('hang', 'GpuHangAbort: tick=5'), ('slow', 'GpuWaitSlow: tick=5'), ('mhung', 'GpuMarkerHung: cs=1'),
                 ('ckpt', 'GpuCheckpointHang: op=1'), ('lost', 'Vulkan: ErrorDeviceLost'),
                 ('term', '--- std::terminate ---'), ('abort', '--- abort() ---'), ('fatal', '--- Fatal Error ---'),
                 ('unh', 'Unhandled exception: 0xc0000005'), ('err', '--- Error ---'),
                 ('skip', 'AsyncPipelines: skipped draw 0x1')):
    case('marker_' + mk, dict(verdict='NOT_ADMITTED', failed=['no_marker']), extra_log=(text,))
case('marker_stdout', dict(verdict='NOT_ADMITTED', failed=['no_marker']), stdout_lines=('--- Fatal Error ---',))
case('blocks_edge', dict(OK), min_blocks=SMALL)
case('blocks_few', dict(verdict='NOT_ADMITTED', failed=['blocks']), min_blocks=SMALL + 1)
case('blocks_default_20', dict(OK), blocks=40, min_blocks=None)
case('blocks_default_19', dict(verdict='NOT_ADMITTED', failed=['blocks']), blocks=38, min_blocks=None)
case('block_missing_x', dict(verdict='NOT_ADMITTED', failed=['blocks']), drop=(('x', START + 1 + PERIOD * 3 + 50),))
case('block_missing_draw', dict(verdict='NOT_ADMITTED', failed=['blocks']), drop=(('draw', START + 1 + PERIOD * 4 + 5),))
case('block_dup', dict(verdict='NOT_ADMITTED', failed=['blocks']), dup=(START + 1 + PERIOD * 6 + 20,))
case('block_field_missing', dict(verdict='NOT_ADMITTED', failed=['blocks']),
     strip=(('x', START + 1 + PERIOD * 2 + 50, 'carry_skip'),))
case('block_draw_field_missing', dict(verdict='NOT_ADMITTED', failed=['blocks']),
     strip=(('draw', START + 1 + PERIOD * 2 + 50, 'bda_scan'),))
case('block_arm_label', dict(verdict='NOT_ADMITTED', failed=['blocks']),
     main=lambda n, b, arm, i: {'arm': 1 - arm} if (b == 2 and i == 30) else {})
case('block_blk_label', dict(verdict='NOT_ADMITTED', failed=['blocks']),
     main=lambda n, b, arm, i: {'blk': b + 1} if (b == 5 and i == 70) else {})
for field, arm, value in (('spine_n', 0, 0), ('sc_frames', 0, 0), ('carry_cmp', 0, 0), ('da_t_n', 1, 0),
                          ('bl_stage_n', 1, 0), ('pl_em_n', 1, 0), ('mh_draws', 1, 0)):
    extra = {'carry_skip': 8} if field == 'carry_cmp' else {}
    case('armed_%s' % field, dict(verdict='NOT_ADMITTED', failed=['armed'] + (['el_ops'] if False else [])),
         x=(lambda f, a, v, e: (lambda n, b, arm, i: dict({f: v}, **e) if arm == a else {}))(field, arm, value, extra))
case('armed_p_takelap', dict(verdict='NOT_ADMITTED', failed=['armed']), x=P(lambda n, b, i: {'da_t_n': 1} if i == 40 else {}))
case('armed_m_census', dict(verdict='NOT_ADMITTED', failed=['armed']),
     x=lambda n, b, arm, i: {'sc_frames': 1} if (arm == 1 and i == 40) else {})
case('armed_m_spine_1pct_ok', dict(OK), x=lambda n, b, arm, i: {'spine_n': 8} if (arm == 1 and b == 1 and i in (20, 40, 60)) else {})
case('armed_m_spine_over', dict(verdict='NOT_ADMITTED', failed=['armed']),
     x=lambda n, b, arm, i: {'spine_n': 8} if (arm == 1 and b in (1, 2) and i in (20, 40, 60)) else {})
case('armed_edge_frames_ignored', dict(OK), x=lambda n, b, arm, i: {'da_t_n': 5} if (arm == 0 and i in (5, 89)) else {})
case('el_ops_lo_edge', dict(OK), x=P(lambda n, b, i: {'spine_el': 5292, 'spine_cmp': 5292}))
case('el_ops_lo', dict(verdict='NOT_ADMITTED', failed=['el_ops']), x=P(lambda n, b, i: {'spine_el': 5291, 'spine_cmp': 5291}))
case('el_ops_hi_edge', dict(OK), x=P(lambda n, b, i: {'spine_el': 5848, 'spine_cmp': 5848}))
case('el_ops_hi', dict(verdict='NOT_ADMITTED', failed=['el_ops']), x=P(lambda n, b, i: {'spine_el': 5849, 'spine_cmp': 5849}))
case('idle_edge', dict(OK), meta=dict(pre_run=dict(gpu_util_median=10)))
case('idle_11', dict(verdict='NOT_ADMITTED', failed=['idle']), meta=dict(pre_run=dict(gpu_util_median=11)))
case('idle_missing', dict(verdict='NOT_ADMITTED', failed=['idle']), meta=dict(pre_run={}))
# ------------------------------------------------------------------ report numbers
root = make('report', x=P(lambda n, b, i: {'k3_max': 1100} if i % 2 == 0 else {}))
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_blocks=SMALL, pred_sha=FAKE_SHA)
rep = res['report']
want = [(rep[0]['kept_frames'], 79 * SMALL), (rep[1]['kept_frames'], 79 * SMALL), (rep[0]['complete_blocks'], SMALL),
        (rep[1]['da_t_ver_us'], 1250.0), (rep[1]['mh_bind_us'], 11400.0), (rep[0]['spine_ns'], 900000.0),
        (res['k3_frames'], 79 * SMALL), (round(res['k3_median'], 9), round(1100 / 5500, 9)),
        (res['k4'][2]['median'], 50), (res['k4'][4]['frames'], 79 * SMALL), (res['k4'][2]['any_median'], 260),
        (res['k4'][4]['fmax_median'], 300), (res['plans'], 8 * 79 * SMALL), (res['with_pred'], 8 * 79 * SMALL),
        (res['raw']['spine_bad'], 0), (res['k5_lines'], 0), (res['c_lines'], 0)]
bad = ['%r want %r' % (g, w) for g, w in want if (abs(g - w) > 1e-9 if isinstance(w, float) else g != w)]
RESULTS.append(('report', not bad, bad))
# item 4 report lines: arm-P blocks 0, 3, 4, 7; block 3 all at 100, the others at 317 except i % 4 == 0 (20 of 79 kept)
root = make('report_k4', x=P(lambda n, b, i: {'k4_w4_dep': 100 if (b == 3 or i % 4 == 0) else 317,
                                                'k4_w2_dep': 301 if (b == 0 and i < 50) else 50, 'carry_skip': 2}))
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_blocks=SMALL, pred_sha=FAKE_SHA)
e2, e4 = res['k4'][2], res['k4'][4]
text = NL.join(mod.format_report(res))
want = [(e4['above_pct'], 100.0 * 177 / 316), (e4['block_medians'], [[0, 317], [3, 100], [4, 317], [7, 317]]),
        (e4['median'], 317), (e4['verdict'], 'FAIL'), (res['consequence'], 'W2_CEILING'),
        (e2['above_pct'], 100.0 * 40 / 316), (e2['block_medians'], [[0, 301], [3, 50], [4, 50], [7, 50]]),
        (e2['median'], 50), (res['carry_skip_pct'], 25.0),
        ('W=4 above the bar 56.0 % of 316 frames; block medians 0:317 3:100 4:317 7:317' in text, True),
        ('W=2 above the bar 12.7 % of 316 frames; block medians 0:301 3:50 4:50 7:50' in text, True),
        ('carry_skip 25.0 % of plans' in text, True)]
bad = ['%r want %r' % (g, w) for g, w in want if (abs(g - w) > 1e-9 if isinstance(w, float) else g != w)]
RESULTS.append(('report_k4', not bad, bad))
root = make('report_k4_equal_bar', x=P(lambda n, b, i: {'k4_w4_dep': 300}))
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_blocks=SMALL, pred_sha=FAKE_SHA)
ok = res['k4'][4]['above_pct'] == 0.0 and res['carry_skip_pct'] == 0.0
RESULTS.append(('report_k4_equal_bar', ok, [] if ok else ['above %r skip %r' % (res['k4'][4]['above_pct'],
                                                                              res['carry_skip_pct'])]))
root = make('report_k4_partial', x=P(lambda n, b, i: {'k4_w4_n': 0} if i % 2 == 0 else {'k4_w4_dep': 317}))
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_blocks=SMALL, pred_sha=FAKE_SHA)
ok = (res['k4'][4]['above_pct'] == 100.0 and res['k4'][4]['frames'] == 156
      and res['k4'][4]['verdict'] == 'NOT_EVALUABLE' and res['consequence'] == 'W2_CEILING')
RESULTS.append(('report_k4_partial', ok, [] if ok else ['%r' % (res['k4'][4],)]))
root = make('report_k4_none', x=P(lambda n, b, i: {'k4_w4_n': 0}))
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_blocks=SMALL, pred_sha=FAKE_SHA)
ok = res['k4'][4]['above_pct'] is None and res['k4'][4]['block_medians'] == [] and 'above the bar - % of 0' in NL.join(
    mod.format_report(res))
RESULTS.append(('report_k4_none', ok, [] if ok else ['%r' % (res['k4'][4],)]))
real = Path(mod.PRED_PATH)
if real.is_file():
    import hashlib
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
