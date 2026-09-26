"""Session 120: fixtures for rpk120.py - synthetic FrameTrace / -draw / -x / GateArm logs (LF, built in memory), one
fixture per formula term, per edge (at a threshold and one past it), per admission and correctness rule, per identity
with its skew tolerance, the window edges, unit traps, zero denominators, arm by text, and the fixtures / mutants the
designs, reviews and ROADMAP s120 items 4-5 list.  Sizes and constants come from this suite, never from the scorer.
    python test_rpk120.py <rpk120.py> [--real]
--real also scores the unsealed smoke C:/kyty/s120/log_smk120.txt in --draft mode and checks the lead's draft numbers
(runs120/smk120_smoke.txt) where the formulas coincide.
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
BASE = Path('C:/kyty/s120/fx_rpk120')
NL = chr(10)
spec = importlib.util.spec_from_file_location('rpk120', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)

TAG = 'cen120'
BUILD = '15cdbfc6e2c9d19a9aa803beaa1dff670d3403b54b74b56f4911c456de4ca661'
PERIOD = 90
START = 1800
SMALL = 4
BLOCKS = 2 * SMALL
ABBA = (0, 1, 1, 0)
PRED_REAL = Path('C:/kyty/s120/pred/01_cen120.md')
PRED = 'C:\\kyty\\s120\\pred\\01_cen120.md'
PSHA = hashlib.sha256(PRED_REAL.read_bytes()).hexdigest()
PBYTES = len(PRED_REAL.read_bytes())
GATES_REAL = 'C:/kyty/s120/gates_base.txt'
GATES_TEXT = ' '.join(Path(GATES_REAL).read_text(encoding='utf-8').split())
TEXT = ('r1cen=2 r2cen=2 spcen=1 bindlap=1 pathlap=1 mutsite=1',
        'r1cen=0 r2cen=1 spcen=0 bindlap=1 pathlap=1 mutsite=1')
SCHED = '90+1800:' + TEXT[0] + '|' + TEXT[1]
VALUES = tuple(dict(p.split('=') for p in t.split()) for t in TEXT)
ENV_OK = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GATE_FILE': 'C:\\kyty\\s120\\gates.req',
          'KYTY_SAMPLE_GATE': 'C:\\kyty\\s120\\sample.req', 'KYTY_QUEUE_TRACE': '1',
          'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0',
          'KYTY_GATE_SCHEDULE': SCHED, 'KYTY_GATE_SCHEDULE_ABBA': '1', 'VK_SDK_PATH': 'C:\\VulkanSDK\\1.4.357.0'}
PIN = 'GpuClockPin: mode 1 - the guest GPU clock ignores the pacer speed (KYTY_GPU_CLOCK_PIN)'

MAIN = ({'dt_us': 36000, 'cpu_gpu_us': 34700, 'draws': 5000},
        {'dt_us': 33000, 'cpu_gpu_us': 32000, 'draws': 5000})
DRAW = ({'tex_hits': 47000, 'b_texn': 50208, 'bda_scan': 68},
        {'tex_hits': 46000, 'b_texn': 50000, 'bda_scan': 60})
R1_NAMES = ['r1_hn', 'r1_mn', 'r1_sn', 'r1_hit_ns', 'r1_hit_t', 'r1_miss_ns', 'r1_nost', 'r1_nost_ns', 'r1_rb_ns',
            'r1_rb_n', 'r1_rbf_ns', 'r1_rbf_n', 'r1_mp', 'r1_mp_ns']
for _t in ('w4', 'w8', 'd16', 'w1'):
    R1_NAMES += ['r1_%s_%s' % (_t, k) for k in ('q', 'qns', 'p', 'pns')]
    R1_NAMES += ['r1_%s_lose' % _t] if _t != 'd16' else []
    R1_NAMES += ['r1_%s_%s' % (_t, k) for k in ('bad', 'rb', 'rbns')]
    R1_NAMES += ['r1_%s_pb_ns' % _t] if _t in ('w4', 'w8') else []
R1_NAMES += ['r1_pb0_ns', 'r1_pb_n', 'r1_am_n', 'r1_ham_ns', 'r1_ham_t', 'r1_sstale', 'r1_cold', 'r1_reset', 'r1_tagx',
             'r1_incl', 'r1_xthr', 'r1_self_h_ns', 'r1_self_h_n', 'r1_self_m_ns', 'r1_self_m_n', 'r1_self_s_ns',
             'r1_self_s_n']
R1_ZERO = {k: 0 for k in R1_NAMES}
R1_P = dict(R1_ZERO, r1_hn=47000, r1_mn=1800, r1_sn=8, r1_hit_ns=146875, r1_hit_t=5875, r1_miss_ns=900000, r1_nost=10,
            r1_nost_ns=5000, r1_rb_ns=105000, r1_rb_n=1500, r1_rbf_ns=56000, r1_rbf_n=2800, r1_mp=900, r1_mp_ns=432000,
            r1_w4_q=800, r1_w4_qns=350000, r1_w4_p=800, r1_w4_pns=380000, r1_w4_lose=300, r1_w4_rb=1400,
            r1_w4_rbns=84000, r1_w4_pb_ns=7350,
            r1_w8_q=600, r1_w8_qns=280000, r1_w8_p=600, r1_w8_pns=300000, r1_w8_lose=100, r1_w8_rb=1000,
            r1_w8_rbns=60000, r1_w8_pb_ns=8085,
            r1_d16_q=800, r1_d16_qns=350000, r1_d16_p=800, r1_d16_pns=380000, r1_d16_rb=1400, r1_d16_rbns=84000,
            r1_pb0_ns=5880, r1_pb_n=735, r1_am_n=900, r1_ham_ns=4500, r1_ham_t=100, r1_sstale=5,
            r1_self_h_ns=29400, r1_self_h_n=735, r1_self_m_ns=8400, r1_self_m_n=28)
R2_P = dict(r2_stg=9100, r2_noimg=400, r2_big=0, r2_odd=0, r2_prog=7900, r2_rep=4500, r2_cl=4300, r2_mx=200,
            r2_cl_ns=1700000, r2_mx_ns=120000, r2_ot_ns=2580500, r2_cl_sl=25600, r2_cl_nul=1600, r2_mx_sl=2000,
            r2_mx_eq=1500, r2_ot_sl=18800, r2_s_cl_ns=212500, r2_s_cl_sl=3200, r2_s_cl_nul=200, r2_s_mx_ns=15000,
            r2_s_mx_sl=250, r2_s_ot_ns=322500, r2_s_ot_sl=2350, r2_sl_eq=30000, r2_sl_hit=28700, r2_cl_lod=2000,
            r2_cl_dcc=10, r2_cl_bc=20, r2_cl_tick=4000, r2_cl_meta=4300, r2_bad=0, r2_bad_key=0, r2_div=0,
            r2_nul_ns=7700, r2_nul_n=1100, r2_wr_ns=34500, r2_wr_n=575, r2_wo_ns=10500, r2_wo_n=525, r2_st_ns=7875,
            r2_st_n=525, r2_rm_ns=71780, r2_rm_sl=3400, r2_rm_n=540)
R2_M = dict(r2_stg=9200, r2_noimg=400, r2_big=0, r2_odd=0, r2_prog=8000, r2_rep=4600, r2_cl=4400, r2_mx=200,
            r2_cl_ns=1307500, r2_mx_ns=100000, r2_ot_ns=1793000, r2_cl_sl=25600, r2_cl_nul=1600, r2_mx_sl=2000,
            r2_mx_eq=1500, r2_ot_sl=18800, r2_s_cl_ns=170000, r2_s_cl_sl=3200, r2_s_cl_nul=200, r2_s_mx_ns=12500,
            r2_s_mx_sl=250, r2_s_ot_ns=224000, r2_s_ot_sl=2350, r2_sl_eq=30000, r2_sl_hit=28700, r2_cl_lod=2000,
            r2_cl_dcc=10, r2_cl_bc=20, r2_cl_tick=4100, r2_cl_meta=4400, r2_bad=0, r2_bad_key=0, r2_div=3,
            r2_nul_ns=9900, r2_nul_n=1100, r2_wr_ns=28750, r2_wr_n=575, r2_wo_ns=7875, r2_wo_n=525, r2_st_ns=6300,
            r2_st_n=525, r2_rm_ns=0, r2_rm_sl=0, r2_rm_n=0)
X_P = dict(dict(texmemo_collide=1800, texmemo_empty=0, texmemo_stale=8, texfast_ok=44800, texfast_no=4800,
                tnull_hit=1400, tnull_miss=0, bl_prep_n=9100, bl_res_us=4400, bl_res_n=48000), **R1_P, **R2_P)
X_M = dict(dict(texmemo_collide=1790, texmemo_empty=0, texmemo_stale=7, texfast_ok=44000, texfast_no=4700,
                tnull_hit=1400, tnull_miss=0, bl_prep_n=9200, bl_res_us=3200, bl_res_n=48000), **R1_ZERO, **R2_M)
X_ARM = (X_P, X_M)
RESULTS = []


def arm_of(block, order=ABBA):
    return order[block % 4]


def make(name, blocks=BLOCKS, main=None, x=None, draw=None, env=None, pins=(PIN,), meta=None, gate_arm=None,
         gate_lines=None, drop=(), dup=(), extra_log=(), stdout_lines=(), pre=5, order=ABBA, post=0, strip=(),
         after=None, gates_copy=None):
    """A fixture directory.  main/x/draw: callables (n, block, arm, index) -> dict of overrides for that frame;
    after: callable n -> lines written right after frame n's three lines; gates_copy: text of a gates file copy."""
    root = BASE / name
    root.mkdir(parents=True)
    lines = list(pins)
    prev = None
    last_block = blocks + (1 if post else 0)
    for n in range(START - pre + 1, START + PERIOD * blocks + post + 1):
        if n > START and (n - START - 1) % PERIOD == 0:
            b = (n - START - 1) // PERIOD
            if b < last_block:
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
                prev = arm
        if n <= START:
            b, idx, arm = 0, 0, 1
        else:
            b, idx = (n - START - 1) // PERIOD, (n - START - 1) % PERIOD
            arm = arm_of(b, order)
        mv = dict(MAIN[arm], arm=arm if n > START else 0, blk=b if n > START else 0)
        dv = dict(DRAW[arm])
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
        if after:
            lines.extend(after(n))
    lines.extend(extra_log)
    (root / ('log_%s.txt' % TAG)).write_bytes((NL.join(lines) + NL).encode('utf-8'))
    (root / ('stdout_%s.txt' % TAG)).write_bytes((NL.join(stdout_lines) + NL).encode('utf-8'))
    m = dict(tag=TAG, binary_sha256=BUILD, env=dict(ENV_OK if env is None else env), schedule=SCHED, hold_s=300,
             gates=GATES_TEXT, attempts=[dict(label='attempt 1', outcome='ok', hold_exit=None, stable_frame=439)],
             prereg=dict(path=PRED, sha256=PSHA, bytes=PBYTES), pre_run=dict(gpu_util_median=2))
    if meta:
        m.update(meta)
    (root / ('%s.json' % TAG)).write_text(json.dumps(m), encoding='utf-8')
    if gates_copy is not None:
        (root / 'gates_base.txt').write_bytes(gates_copy.encode('utf-8'))
    return root


def get(res, path):
    for part in path.split('.'):
        res = res[int(part)] if isinstance(res, list) else res[part]
    return res


def run(name, root, installed=BUILD, min_pairs=SMALL, pred=(PSHA, PBYTES), draft=False, gates_file=None,
        **expect):
    gf = str(root / 'gates_base.txt') if gates_file == 'copy' else (gates_file or GATES_REAL)
    res = mod.evaluate(str(root), TAG, draft=draft, installed_sha=installed, min_pairs=min_pairs, pred_sha=pred[0],
                       pred_bytes=pred[1], gates_file=gf)
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
        elif key in ('ne1_has', 'ne2_has'):
            lst = res['R1' if key == 'ne1_has' else 'R2']['not_evaluable']
            miss = [w for w in want if w not in lst]
            if miss:
                bad.append('%s missing %r in %r' % (key, miss, lst))
            continue
        elif key in ('ne1_not', 'ne2_not'):
            lst = res['R1' if key == 'ne1_not' else 'R2']['not_evaluable']
            extra = [w for w in want if w in lst]
            if extra:
                bad.append('%s has %r' % (key, extra))
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
        elif key in ('last_has', 'last_not'):
            last = text.split(NL)[-1]
            for w in want:
                if (w in last) != (key == 'last_has'):
                    bad.append('last line %r: %s %r' % (last[:60], key, w))
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
    runner = {k: kw.pop(k) for k in ('installed', 'min_pairs', 'pred', 'draft', 'gates_file') if k in kw}
    run(name, make(name, **kw), **runner, **expect)


OK = dict(verdict='ADMITTED', failed=[])
P = lambda f: (lambda n, b, arm, i: f(n, b, i) if arm == 0 else {})
M = lambda f: (lambda n, b, arm, i: f(n, b, i) if arm == 1 else {})
V1 = 'R1__verdict'
V2 = 'R2__verdict'
VR = 'R__verdict'
C1 = 'R1__point'
CPT = 'R2__terms__C_pt'
CUP = 'R2__terms__C_up'
T1 = 'R1__terms__tables__'
T2 = 'R2__terms__'

# ------------------------------------------------------------------ the admitted base: every term of every formula
case('ok', dict(OK, **{V1: 'OPEN', V2: 'NOT_OPENED', VR: 'OPEN', 'R1__terms__argmax': 'd16', C1: 792.0,
                       'R1__upper': 792.0, 'R1__two_se': 0.0, 'R1__terms__t_hit': 25.0, 'R1__terms__t_miss': 480.0,
                       'R1__terms__t_fast': 20.0, 'R1__terms__t_ham': 45.0, 'R1__terms__lookups': 48808.0,
                       T1 + 'd16__W': 1600.0, T1 + 'd16__t_T': 475.0, T1 + 'd16__A': 720.0, T1 + 'd16__L': 0.0,
                       T1 + 'd16__R': 56.0, T1 + 'd16__E': 16.0, T1 + 'd16__P': 0.0, T1 + 'd16__C': 792.0,
                       T1 + 'd16__C_noE': 776.0,
                       T1 + 'w4__W': 1600.0, T1 + 'w4__t_T': 475.0, T1 + 'w4__A': 720.0, T1 + 'w4__L': 135.0,
                       T1 + 'w4__R': 56.0, T1 + 'w4__E': 16.0, T1 + 'w4__P': 97.616, T1 + 'w4__C': 559.384,
                       T1 + 'w4__C_noE': 543.384,
                       T1 + 'w8__W': 1200.0, T1 + 'w8__t_T': 500.0, T1 + 'w8__A': 570.0, T1 + 'w8__L': 45.5,
                       T1 + 'w8__R': 40.0, T1 + 'w8__E': 12.0, T1 + 'w8__P': 146.424, T1 + 'w8__C': 430.076,
                       T1 + 'w8__C_noE': 418.076,
                       T2 + 'S': 25600.0, T2 + 'Z': 1600.0, T2 + 'L': 2000.0, T2 + 'z_bar': 9.0, T2 + 'w_rep': 50.0,
                       T2 + 'w_oth': 15.0, T2 + 'st_bar': 12.0, T2 + 'rep': 4600.0, T2 + 'nonrep': 4200.0,
                       T2 + 'T_star': 1300.0, T2 + 'W': 213.8, T2 + 'ST': 12.6, T2 + 'p_c': 1300000 / 27200,
                       CUP: 992.0, CPT: 458.912, T2 + 'C_lo': 72.864, T2 + 'C_ext': 458.912 + 1.5 * (1300000 / 27200 - 20.49),
                       T2 + 'C_rp': 317.6, T2 + 'K_rp': 1300000 / 27200 - 71780 / 3400,
                       T2 + 'first_touch_ns': 1137500 / 23800 - 50.0, 'R2__point': 458.912, 'R2__upper': 992.0,
                       'R2__two_se': 0.0, 'R__point': 1250.912, 'R__upper': 1784.0, 'R__two_se': 0.0,
                       'price__dt_us__pair_mean': 3000.0, 'price__dt_us__two_se': 0.0, 'price__dt_us__P': 36000.0,
                       'price__dt_us__M': 33000.0, 'price__cpu_gpu_us__pair_mean': 2700.0, 'bda_scan__P': 68.0,
                       'bda_scan__M': 60.0, 'pairs': 4, 'r1_pairs': 4, 'complete_blocks': 8, 'est_frames__P': 316,
                       'est_frames__M': 316, 'est_frames__R1': 316, 'R1__not_evaluable': [], 'R2__not_evaluable': [],
                       'arm_asserts': True,
                       'lines_has': ['MEMBER R1: OPEN point=792.0 upper=792.0 2se=0.0',
                                     'MEMBER R2: NOT_OPENED point=458.9 upper=992.0 2se=0.0',
                                     'PACKAGE R: OPEN point=1250.9 upper=1784.0 2se=0.0',
                                     'VERDICT: ADMITTED' + NL, 'CONSEQUENCE: R1 OPEN - "точечный чистый потолок',
                                     'CONSEQUENCE: R2 NOT_OPENED - "граница, записывается',
                                     'CONSEQUENCE: R OPEN - "точечный', ' Open members: R1.' + NL,
                                     ' Table d16.', 'bda_scan P 68.0 (NEW) M 60.0 (NEW)',
                                     'R2 information: C_up at B=8.49 897.1 us, C_pt traced 522.3 us, DCC-lock share of clean slots 0.0004, replay proxy kept',
                                     'no-store key misses 10.0 a frame at 500.0 ns', '| warming -37.5 ns'],
                       'lines_not': ['DRAFT', 'Per-slot variant', 'REPORT OF A NOT_ADMITTED', 'Carried by', 'Superseded'],
                       'summary__verdict': 'OPEN', 'summary__carrying': 'R1', 'summary__open_members': ['R1'],
                       'last_has': ['CONSEQUENCE: OPEN - "точечный', ' Open: R1.']}))

# ------------------------------------------------------------------ R1 thresholds (C_R1 point = upper) and the 2SE
case('r1_open_500', dict(OK, **{V1: 'OPEN', C1: 500.0, VR: 'OPEN'}),
     x=P(lambda n, b, i: {'r1_d16_pns': 234000, 'r1_w4_pns': 234000}))
case('r1_closed_4999', dict(OK, **{V1: 'CLOSED', C1: 499.9, 'lines_has': ['CONSEQUENCE: R1 CLOSED - "верхний X_up + 2SE < 500']}),
     x=P(lambda n, b, i: {'r1_d16_pns': 233950, 'r1_w4_pns': 233950}))
case('r1_border_se', dict(OK, **{V1: 'NOT_OPENED', C1: 490.0, 'R1__two_se': 2 * (400 * 4 / 3) ** 0.5 / 2,
                                 'R1__pair_values': [470.0, 510.0, 470.0, 510.0]}),
     x=P(lambda n, b, i: {'r1_d16_pns': 219000 if (b // 2) % 2 == 0 else 239000,
                          'r1_w4_pns': 219000 if (b // 2) % 2 == 0 else 239000}))
# ------------------------------------------------------------------ R1 terms, one by one
case('r1_E_clamp', dict(OK, **{T1 + 'd16__E': 0.0, T1 + 'd16__C': 776.0, 'R1__terms__t_ham': 20.0}),
     x=P(lambda n, b, i: {'r1_ham_ns': 2000}))
case('r1_P_clamp', dict(OK, **{T1 + 'w4__P': 0.0, T1 + 'w4__C': 657.0, T1 + 'w8__P': 146.424}),
     x=P(lambda n, b, i: {'r1_w4_pb_ns': 5000}))
case('r1_R_negative', dict(OK, **{T1 + 'd16__R': -8.0, T1 + 'd16__C': 728.0}), x=P(lambda n, b, i: {'r1_d16_rbns': 20000}))
case('r1_argmax_w8', dict(OK, **{'R1__terms__argmax': 'w8', C1: 870.076, T1 + 'w8__R': 480.0,
                                 'lines_has': [' Table w8.']}), x=P(lambda n, b, i: {'r1_w8_rbns': 500000}))
case('r1_argmax_w4', dict(OK, **{'R1__terms__argmax': 'w4', C1: 975.384}), x=P(lambda n, b, i: {'r1_w4_rbns': 500000}))
case('r1_W_uses_pre_half', dict(OK, **{T1 + 'd16__W': 1600.0, T1 + 'd16__t_T': 475.0, T1 + 'd16__C': 792.0}),
     x=P(lambda n, b, i: {'r1_d16_p': 783, 'r1_d16_pns': 783 * 475}))
case('r1_L_uses_tT_below_tmiss', dict(OK, **{T1 + 'w4__L': 300 * 425 / 1000, T1 + 'w4__t_T': 450.0}),
     x=P(lambda n, b, i: {'r1_w4_pns': 800 * 450}))
case('r1_L_uses_tmiss_above', dict(OK, **{T1 + 'w8__L': 100 * 455 / 1000, T1 + 'w8__t_T': 520.0}),
     x=P(lambda n, b, i: {'r1_w8_pns': 600 * 520}))
case('r1_L_clamp', dict(OK, **{T1 + 'w4__L': 0.0}), x=P(lambda n, b, i: {'r1_w4_pns': 800 * 20}))
case('r1_P_lookups', dict(OK, **{T1 + 'w4__P': 2 * 48900 / 1000, 'R1__terms__lookups': 48900.0}),
     x=P(lambda n, b, i: {'r1_sn': 100, 'texmemo_stale': 100}), draw=P(lambda n, b, i: {'b_texn': 50300}))
case('r1_P_probe_net', dict(OK, **{T1 + 'w4__P': 48808 * 4 / 1000, T1 + 'w8__P': 48808 * 5 / 1000}),
     x=P(lambda n, b, i: {'r1_pb0_ns': 735 * 6}))
case('r1_E_share', dict(OK, **{T1 + 'd16__E': 20 * 450 * 1600 / 1800 / 1000, T1 + 'w8__E': 20 * 450 * 1200 / 1800 / 1000}),
     x=P(lambda n, b, i: {'r1_am_n': 450}))
# ------------------------------------------------------------------ R2 thresholds (point C_pt, upper C_up) and terms
S0 = {'r2_s_cl_ns': 0, 'r2_s_cl_sl': 0, 'r2_s_cl_nul': 0}
EXT = {'r2_mx_sl': 60000, 'bl_res_n': 106000, 'r2_sl_hit': 87200, 'r2_sl_eq': 90000}


def tstar(t, extra=None):
    """M rows with T* = t ns (no sampled clean stage), the ns partition kept."""
    d = dict(S0, r2_cl_ns=t, r2_ot_ns=3200500 - t - 100000)
    if extra:
        d.update(extra)
    return M(lambda n, b, i: d)


case('r2_open_500', dict(OK, **{V2: 'OPEN', CPT: 500.0, CUP: 1033.088, 'R2__two_se': 0.0, 'lines_not': ['Per-slot variant']}),
     x=tstar(1341088))
case('r2_below_4999', dict(OK, **{V2: 'NOT_OPENED', CPT: 499.9}), x=tstar(1340988))
case('r2_closed_edge_500', dict(OK, **{V2: 'NOT_OPENED', CUP: 500.0}), x=tstar(808000))
case('r2_closed_4999', dict(OK, **{V2: 'CLOSED', CUP: 499.9, 'lines_has': ['CONSEQUENCE: R2 CLOSED - "верхний'],
                                   'lines_not': ['Per-slot variant']}), x=tstar(807900))
case('r2_closed_ext', dict(OK, **{V2: 'CLOSED', T2 + 'C_ext': -33.188 + 60 * (807900 / 27200 - 20.49),
                                  'lines_has': ['Per-slot variant unmeasured (C_ext 519.5 us >= 500.0)'],
                                  'R2__not_evaluable': []}),
     x=tstar(807900, dict(EXT, r2_mx_eq=60000)))
case('r2_closed_ext_edge', dict(OK, **{V2: 'CLOSED', 'lines_not': ['Per-slot variant']}),
     x=tstar(807900, dict(EXT, r2_mx_eq=57000)))
case('r2_border_se', dict(OK, **{V2: 'NOT_OPENED', CUP: 497.0, 'R2__two_se': (100 / 3) ** 0.5,
                                 'R2__pair_up': [492.0, 502.0, 492.0, 502.0]}),
     x=lambda n, b, arm, i: (dict(S0, r2_cl_ns=800000 if (b // 2) % 2 == 0 else 810000,
                                  r2_ot_ns=3100500 - (800000 if (b // 2) % 2 == 0 else 810000)) if arm == 1 else {}))
case('r2_pc_25', dict(OK, **{T2 + 'p_c': 25.0, 'ne2_not': ['sanity_pc']}), x=tstar(680000))
case('r2_pc_249', dict(OK, **{V2: 'NOT_EVALUABLE', 'ne2_has': ['sanity_pc'], VR: 'NOT_EVALUABLE'}), x=tstar(677280))
case('r2_pc_90', dict(OK, **{T2 + 'p_c': 90.0, V2: 'OPEN', 'ne2_not': ['sanity_pc']}), x=tstar(2448000))
case('r2_pc_901', dict(OK, **{V2: 'NOT_EVALUABLE', 'ne2_has': ['sanity_pc']}), x=tstar(2450720))
case('r2_order_lo', dict(OK, **{V2: 'NOT_EVALUABLE', 'ne2_has': ['sanity_order'], 'ne2_not': ['sanity_pc']}),
     x=tstar(1300000, {'r2_cl_sl': -800, 'r2_cl_nul': 28000}))
case('r2_order_up', dict(OK, **{V2: 'NOT_EVALUABLE', 'ne2_has': ['sanity_order'], 'ne2_not': ['sanity_pc']}),
     x=tstar(1300000, {'r2_cl_lod': -200000}))
case('r2_nonrep_terms', dict(OK, **{T2 + 'nonrep': 4050.0, T2 + 'W': 212.9, T2 + 'ST': 12.15, CUP: 993.35}),
     x=M(lambda n, b, i: {'r2_big': 100, 'r2_odd': 50}))
case('r2_nonrep_noimg', dict(OK, **{T2 + 'nonrep': 4100.0}), x=M(lambda n, b, i: {'r2_noimg': 500}))
case('r2_W_rep_weight', dict(OK, **{T2 + 'rep': 4500.0, T2 + 'nonrep': 4300.0, T2 + 'W': (41 * 4500 + 6 * 4300) / 1000}),
     x=M(lambda n, b, i: {'r2_rep': 4500, 'r2_cl': 4300}))
case('r2_L_term', dict(OK, **{CPT: 458.912 - 5.0, T2 + 'C_lo': 72.864 - 5.0, CUP: 992.0}),
     x=M(lambda n, b, i: {'r2_cl_lod': 3000}))
case('r2_Z_terms', dict(OK, **{T2 + 'Z': 3200.0, T2 + 'T_star': 1300.0, CUP: (1300000 - 3 * 28800 - 226400) / 1000,
                               CPT: (1300000 - (524544 + 33568 + 10000) - 226400 - 65280) / 1000}),
     x=M(lambda n, b, i: {'r2_cl_nul': 3200, 'r2_s_cl_nul': 400, 'r2_ot_sl': 17200}))
case('r2_crp_none', dict(OK, **{T2 + 'C_rp': None, T2 + 'K_rp': None, 'ne2_has': ['armed_replay']}),
     x=P(lambda n, b, i: {'r2_rm_sl': 0, 'r2_rm_ns': 0, 'r2_rm_n': 0, 'r2_s_cl_sl': 0, 'r2_s_cl_nul': 0}))
case('r2_crp_z_of_P', dict(OK, **{T2 + 'C_rp': (20 * 27200 - 226400) / 1000}),
     x=P(lambda n, b, i: {'r2_nul_ns': 11000, 'r2_rm_ns': 3400 * 20 + 540 * 10}))
# ------------------------------------------------------------------ package R
R1_100 = {'r1_d16_pns': 34000, 'r1_w4_pns': 34000, 'r1_w8_pns': 24000}
case('r2_se_of_up', dict(OK, **{'R2__two_se': 0.0, CPT: 458.912 - 25.0, 'R2__pair_pt': [458.912, 408.912, 458.912, 408.912],
                                 'R__two_se': 0.0, 'R__pair_values': [1784.0, 1784.0, 1784.0, 1784.0]}),
     x=M(lambda n, b, i: {'r2_cl_lod': 2000 if (b // 2) % 2 == 0 else 12000}))
case('r1_se_uses_pooled_argmax', dict(OK, **{'R1__terms__argmax': 'd16', 'R1__two_se': 0.0, T1 + 'w8__C': 750.076,
                                             'R1__pair_values': [792.0, 792.0, 792.0, 792.0]}),
     x=P(lambda n, b, i: {'r1_w8_rbns': 700000 if (b // 2) % 2 == 0 else 60000}))
case('pk_open_500', dict(OK, **{VR: 'OPEN', 'R__point': 500.0, C1: 100.0, V1: 'CLOSED', CPT: 400.0, V2: 'NOT_OPENED',
                                'lines_has': ['CONSEQUENCE: R OPEN - "точечный', ' Open members: R1+R2 (together).'],
                                'summary__verdict': 'OPEN', 'summary__carrying': 'R1+R2 (together)',
                                'last_has': ['CONSEQUENCE: OPEN - ', ' Open: R1+R2 (together).'],
                                'lines_not': ['Superseded']}),
     x=lambda n, b, arm, i: R1_100 if arm == 0 else dict(S0, r2_cl_ns=1241088, r2_ot_ns=3200500 - 1341088))
# ------------------------------------------------------------------ the summary consequence (ROADMAP s120 item 4 addendum)
case('sum_r1_open_r2_ne', dict(OK, **{V1: 'OPEN', V2: 'NOT_EVALUABLE', VR: 'NOT_EVALUABLE', 'ne2_has': ['sanity_pc'],
                                      'summary__verdict': 'OPEN', 'summary__carrying': 'R1',
                                      'lines_has': ['CONSEQUENCE: R NOT_EVALUABLE - "провал допуска',
                                                    ' Superseded for the OPEN member(s) R1 by the summary line.'],
                                      'last_has': ['CONSEQUENCE: OPEN - "точечный', ' Open: R1.'],
                                      'last_not': ['NOT_EVALUABLE', 'R1+']}), x=tstar(677280))
case('sum_r1_open_pk_closed', dict(OK, **{V1: 'OPEN', C1: 792.0, V2: 'CLOSED', CUP: 992.0 - 1610.0, VR: 'CLOSED',
                                          'R__upper': 792.0 - 618.0, 'R2__not_evaluable': [],
                                          'summary__verdict': 'OPEN', 'summary__carrying': 'R1',
                                          'lines_has': ['CONSEQUENCE: R CLOSED - "верхний',
                                                        ' Superseded for the OPEN member(s) R1 by the summary line.'],
                                          'last_has': ['CONSEQUENCE: OPEN - "точечный', ' Open: R1.'],
                                          'last_not': ['исчерпанным']}),
     x=M(lambda n, b, i: {'r2_wr_ns': 400 * 575}))
case('sum_r2_open_alone', dict(OK, **{V1: 'CLOSED', C1: 100.0, V2: 'OPEN', CPT: 500.0, VR: 'OPEN',
                                      'summary__verdict': 'OPEN', 'summary__carrying': 'R2',
                                      'lines_has': [' Open members: R2.'],
                                      'last_has': ['CONSEQUENCE: OPEN - ', ' Open: R2.'], 'last_not': ['R1+']}),
     x=lambda n, b, arm, i: R1_100 if arm == 0 else dict(S0, r2_cl_ns=1341088, r2_ot_ns=3200500 - 1441088))
case('sum_both_open', dict(OK, **{V1: 'OPEN', V2: 'OPEN', VR: 'OPEN', 'summary__carrying': 'R1+R2',
                                  'lines_has': [' Open members: R1+R2.'], 'last_has': [' Open: R1+R2.']}),
     x=tstar(1341088))
case('sum_fail_with_open', dict(OK, **{V1: 'OPEN', V2: 'FAIL', VR: 'FAIL', 'summary__verdict': 'FAIL',
                                       'summary__carrying': 'R1',
                                       'last_has': ['CONSEQUENCE: FAIL - "любой'], 'last_not': ['Open']}),
     x=M(lambda n, b, i: {'r2_bad': 1} if (b == 2 and i == 40) else {}))
case('sum_fail_r1_open_r2', dict(OK, **{V1: 'FAIL', V2: 'OPEN', 'summary__verdict': 'FAIL',
                                        'last_has': ['CONSEQUENCE: FAIL - ']}),
     x=lambda n, b, arm, i: ({'r1_d16_bad': 1} if (arm == 0 and b == 0 and i == 40) else {}) if arm == 0
     else dict(S0, r2_cl_ns=1341088, r2_ot_ns=3200500 - 1441088))
case('sum_closed', dict(OK, **{V1: 'CLOSED', V2: 'CLOSED', VR: 'CLOSED', 'summary__verdict': 'CLOSED',
                               'summary__carrying': '', 'last_has': ['CONSEQUENCE: CLOSED - "верхний'],
                               'lines_not': ['Superseded', 'Open']}),
     x=lambda n, b, arm, i: R1_100 if arm == 0 else dict(S0, r2_cl_ns=707900, r2_ot_ns=3200500 - 807900))
R1_0 = {'r1_d16_pns': 24000, 'r1_w4_pns': 24000, 'r1_w8_pns': 14000, 'r1_d16_rbns': 0, 'r1_w4_rbns': 0}
case('sum_closed_ext', dict(OK, **{V1: 'CLOSED', C1: -4.0, 'R__upper': 495.9, V2: 'CLOSED', VR: 'CLOSED', 'summary__verdict': 'CLOSED',
                                   'last_has': ['CONSEQUENCE: CLOSED - ', 'Per-slot variant unmeasured']}),
     x=lambda n, b, arm, i: R1_0 if arm == 0 else dict(EXT, r2_mx_eq=60000, **dict(S0, r2_cl_ns=807900,
                                                                                  r2_ot_ns=3200500 - 907900)))
case('sum_not_opened', dict(OK, **{V1: 'CLOSED', V2: 'NOT_OPENED', VR: 'NOT_OPENED', 'summary__verdict': 'NOT_OPENED',
                                   'last_has': ['CONSEQUENCE: NOT_OPENED - "граница']}),
     x=lambda n, b, arm, i: R1_100 if arm == 0 else dict(S0, r2_cl_ns=1240988, r2_ot_ns=3200500 - 1340988))
case('sum_ne', dict(OK, **{V1: 'NOT_EVALUABLE', V2: 'NOT_OPENED', VR: 'NOT_EVALUABLE', 'summary__verdict': 'NOT_EVALUABLE',
                           'last_has': ['CONSEQUENCE: NOT_EVALUABLE - "провал']}),
     x=P(lambda n, b, i: {'r1_incl': 1} if (b == 3 and i == 40) else {}))
case('pk_below_4999', dict(OK, **{VR: 'NOT_OPENED', 'R__point': 499.9}),
     x=lambda n, b, arm, i: R1_100 if arm == 0 else dict(S0, r2_cl_ns=1240988, r2_ot_ns=3200500 - 1340988))
case('pk_closed_edge_500', dict(OK, **{VR: 'NOT_OPENED', 'R__upper': 500.0, V1: 'CLOSED', V2: 'CLOSED'}),
     x=lambda n, b, arm, i: R1_100 if arm == 0 else dict(S0, r2_cl_ns=708000, r2_ot_ns=3200500 - 808000))
case('pk_closed_4999', dict(OK, **{VR: 'CLOSED', 'R__upper': 499.9, 'lines_has': ['CONSEQUENCE: R CLOSED - "верхний']}),
     x=lambda n, b, arm, i: R1_100 if arm == 0 else dict(S0, r2_cl_ns=707900, r2_ot_ns=3200500 - 807900))


def pk_se(n, b, arm, i):
    k = (b // 2) % 2
    if arm == 0:
        return {'r1_d16_pns': 29000 if k == 0 else 39000, 'r1_w4_pns': 29000 if k == 0 else 39000, 'r1_w8_pns': 24000}
    t = 717000 if k == 0 else 697000
    return dict(S0, r2_cl_ns=t, r2_ot_ns=3100500 - t)


case('pk_se_per_pair_sum', dict(OK, **{VR: 'CLOSED', 'R__upper': 499.0, 'R__two_se': 0.0, C1: 100.0, CUP: 399.0,
                                       'R1__two_se': 2 * (400 / 3) ** 0.5 / 2, 'R2__two_se': 2 * (400 / 3) ** 0.5 / 2,
                                       'R__pair_values': [499.0, 499.0, 499.0, 499.0]}), x=pk_se)
case('pk_fail_by_r2', dict(OK, **{VR: 'FAIL', V2: 'FAIL', V1: 'OPEN'}),
     x=M(lambda n, b, i: {'r2_bad': 1} if (b == 2 and i == 40) else {}))
case('pk_ne_by_r1', dict(OK, **{VR: 'NOT_EVALUABLE', V1: 'NOT_EVALUABLE', V2: 'NOT_OPENED'}),
     x=P(lambda n, b, i: {'r1_incl': 1} if (b == 3 and i == 40) else {}))
case('pk_fail_over_ne', dict(OK, **{VR: 'FAIL', V1: 'NOT_EVALUABLE', V2: 'FAIL'}),
     x=lambda n, b, arm, i: {'r1_incl': 1, 'r2_bad_key': 1} if (b == 3 and i == 40) else {})
# ------------------------------------------------------------------ correctness: every row of the run, every line
for nm, field, where in (('r1_bad_w4_window', 'r1_w4_bad', lambda b, i: b == 0 and i == 40),
                         ('r1_bad_w8_pos3', 'r1_w8_bad', lambda b, i: b == 3 and i == 3),
                         ('r1_bad_d16_pos89', 'r1_d16_bad', lambda b, i: b == 4 and i == 89),
                         ('r1_bad_in_m_row', 'r1_w4_bad', lambda b, i: b == 5 and i == 50)):
    case(nm, dict(OK, **{V1: 'FAIL', VR: 'FAIL', V2: 'NOT_OPENED', 'lines_has': ['CONSEQUENCE: R1 FAIL - "любой счётчик ошибок']}),
         x=(lambda f, w: (lambda n, b, arm, i: {f: 1} if (n > START and w(b, i)) else {}))(field, where))
case('r1_bad_pre_start', dict(OK, **{V1: 'FAIL'}), x=lambda n, b, arm, i: {'r1_d16_bad': 1} if n == START - 2 else {})
case('r1_bad_in_dup', dict(verdict='NOT_ADMITTED', **{V1: 'FAIL'}), x=lambda n, b, arm, i: {'r1_w8_bad': 1} if n == START + 1 + PERIOD * 5 + 40 else {},
     dup=(START + 1 + PERIOD * 5 + 40,))
case('r1_bad_after_blocks', dict(OK, **{V1: 'FAIL'}), post=20,
     x=lambda n, b, arm, i: {'r1_w4_bad': 1} if n == START + PERIOD * BLOCKS + 15 else {})
case('r1_mismatch_line', dict(OK, **{V1: 'FAIL', VR: 'FAIL', 'lines__r1_mismatch': 1}),
     extra_log=('R1CenMismatch: table=w4 post=0 store=1 id_same=0 desc_same=1 addr=0x0000100000',))
case('r1_mismatch_midline', dict(OK, **{V1: 'FAIL'}), extra_log=('[12] x R1CenMismatch: table=d16',))
case('r2_bad_m', dict(OK, **{V2: 'FAIL', VR: 'FAIL', V1: 'OPEN'}), x=M(lambda n, b, i: {'r2_bad': 2} if (b == 6 and i == 70) else {}))
case('r2_bad_key_p_pos3', dict(OK, **{V2: 'FAIL'}), x=P(lambda n, b, i: {'r2_bad_key': 1} if (b == 7 and i == 3) else {}))
case('r2_bad_pre_start', dict(OK, **{V2: 'FAIL'}), x=lambda n, b, arm, i: {'r2_bad': 1} if n == START else {})
case('r2_mismatch_line', dict(OK, **{V2: 'FAIL', VR: 'FAIL'}), extra_log=('R2Mismatch: stage=4 slot=1 n=3',))
case('r2_mismatch_key_line', dict(OK, **{V2: 'FAIL'}), extra_log=('R2MismatchKey: stage=4 slot=1 n=3 fields=0',))
case('r2_diverge_line_info', dict(OK, **{V2: 'NOT_OPENED', 'lines__r2_diverge': 1}), extra_log=('R2Diverge: stage=1',))
for nm, field in (('r1_incl', 'r1_incl'), ('r1_xthr', 'r1_xthr'), ('r1_w1_q', 'r1_w1_q'), ('r1_w1_lose', 'r1_w1_lose'),
                  ('r1_w1_rbns', 'r1_w1_rbns'), ('r1_w1_bad', 'r1_w1_bad'), ('r1_w1_pns', 'r1_w1_pns')):
    case('ne_' + nm, dict(OK, **{V1: 'NOT_EVALUABLE', VR: 'NOT_EVALUABLE', 'ne1_has': ['incl_xthr_w1'],
                                 'lines_has': ['CONSEQUENCE: R1 NOT_EVALUABLE - "провал допуска']}),
         x=(lambda f: (lambda n, b, arm, i: {f: 1} if (b == 1 and i == 3 and n > START) else {}))(field))
case('ne_w1_negative', dict(OK, **{V1: 'NOT_EVALUABLE', 'ne1_has': ['incl_xthr_w1']}),
     x=P(lambda n, b, i: {'r1_w1_rbns': -5} if (b == 3 and i == 20) else {}))
case('ne_incl_pre_start', dict(OK, **{V1: 'NOT_EVALUABLE'}), x=lambda n, b, arm, i: {'r1_incl': 1} if n == START - 1 else {})
case('fail_over_ne_r1', dict(OK, **{V1: 'FAIL'}), x=P(lambda n, b, i: {'r1_incl': 1, 'r1_d16_bad': 1} if i == 20 else {}))
# ------------------------------------------------------------------ identities on window sums (NEAR +-8, FAR 0.1 %)
# NEAR = +-8 counts a block window (ROADMAP s120 item 6): 8 admitted, 9 rejected on each side; a persistent
# off-by-one per row (79 rows a window) still fails.
ID_ROW = lambda f: P(lambda n, b, i: f if (b == 3 and i == 50) else {})
case('id_hn_far_edge', dict(OK, **{'ne1_not': ['r1_hn=tex_hits@3']}), x=ID_ROW({'r1_hn': 47000 + 3713}))
case('id_hn_far_over', dict(OK, **{V1: 'NOT_EVALUABLE', V2: 'NOT_OPENED', 'ne1_has': ['r1_hn=tex_hits@3']}),
     x=ID_ROW({'r1_hn': 47000 + 3714}))
case('id_hn_far_under', dict(OK, **{'ne1_has': ['r1_hn=tex_hits@3']}), x=ID_ROW({'r1_hn': 47000 - 3714}))
case('id_mn_abs_edge', dict(OK, **{'ne1_not': ['r1_mn=collide+empty@3']}), x=ID_ROW({'texmemo_collide': 1800 + 256}))
case('id_mn_abs_over', dict(OK, **{'ne1_has': ['r1_mn=collide+empty@3']}), x=ID_ROW({'texmemo_collide': 1800 + 257}))
case('id_mn_empty', dict(OK, **{'ne1_has': ['r1_mn=collide+empty@3']}), x=ID_ROW({'texmemo_empty': 257}))
case('id_sn_abs_edge', dict(OK, **{'ne1_not': ['r1_sn=stale@3']}), x=ID_ROW({'texmemo_stale': 8 + 256}))
case('id_sn_abs_over', dict(OK, **{'ne1_has': ['r1_sn=stale@3']}), x=ID_ROW({'texmemo_stale': 8 + 257}))
case('id_btexn_edge', dict(OK, **{'ne1_not': ['b_texn=lookups+null@3']}), draw=ID_ROW({'b_texn': 50208 + 3966}))
case('id_btexn_over', dict(OK, **{'ne1_has': ['b_texn=lookups+null@3']}), draw=ID_ROW({'b_texn': 50208 + 3967}))
case('id_btexn_tnull', dict(OK, **{'ne1_has': ['b_texn=lookups+null@3']}), x=ID_ROW({'tnull_miss': 4000}))
case('id_tex_hits_draw_line', dict(OK, **{'ne1_has': ['r1_hn=tex_hits@3']}), draw=ID_ROW({'tex_hits': 47000 - 3714}))
case('id_pb_near_edge', dict(OK, **{'ne1_not': ['r1_pb_n=self_h_n@3']}), x=ID_ROW({'r1_pb_n': 735 + 8}))
case('id_pb_near_over', dict(OK, **{'ne1_has': ['r1_pb_n=self_h_n@3']}), x=ID_ROW({'r1_pb_n': 735 + 9}))
case('id_pb_near_under_edge', dict(OK, **{'ne1_not': ['r1_pb_n=self_h_n@3']}), x=ID_ROW({'r1_self_h_n': 735 + 8}))
case('id_pb_near_under', dict(OK, **{'ne1_has': ['r1_pb_n=self_h_n@3']}), x=ID_ROW({'r1_self_h_n': 735 + 9}))
case('id_pb_near_spread', dict(OK, **{'ne1_not': ['r1_pb_n=self_h_n@3']}),
     x=P(lambda n, b, i: {'r1_pb_n': 736} if (b == 3 and i in (20, 30, 40, 50, 60, 70, 80, 88)) else {}))
case('id_pb_near_spread_over', dict(OK, **{'ne1_has': ['r1_pb_n=self_h_n@3']}),
     x=P(lambda n, b, i: {'r1_pb_n': 736} if (b == 3 and i in (10, 20, 30, 40, 50, 60, 70, 80, 88)) else {}))
case('id_pb_skew_cancels', dict(OK, **{'ne1_not': ['r1_pb_n=self_h_n@3', 'r1_pb_n=self_h_n@4']}),
     x=P(lambda n, b, i: {'r1_pb_n': 736} if i == 30 else ({'r1_pb_n': 734} if i == 31 else {})))
case('id_pb_persistent', dict(OK, **{V1: 'NOT_EVALUABLE', 'ne1_has': ['r1_pb_n=self_h_n@0']}),
     x=P(lambda n, b, i: {'r1_pb_n': 736}))
case('id_pb_persistent_under', dict(OK, **{V1: 'NOT_EVALUABLE', 'ne1_has': ['r1_pb_n=self_h_n@3']}),
     x=P(lambda n, b, i: {'r1_pb_n': 734}))
case('id_rep_persistent', dict(OK, **{V2: 'NOT_EVALUABLE', 'ne2_has': ['r2_rep=cl+mx@1', 'r2_rep=cl+mx@0']}),
     x=lambda n, b, arm, i: {'r2_rep': (4501 if arm == 0 else 4601)})
case('id_nul_persistent', dict(OK, **{V2: 'NOT_EVALUABLE', 'ne2_has': ['r2_wr+wo=nul@2']}),
     x=M(lambda n, b, i: {'r2_nul_n': 1099}))
case('id_pb_pos9_89_ignored', dict(OK, **{'R1__not_evaluable': []}),
     x=P(lambda n, b, i: {'r1_pb_n': 800} if i in (9, 89) else {}))
case('id_pb_pos10', dict(OK, **{'ne1_has': ['r1_pb_n=self_h_n@0']}), x=P(lambda n, b, i: {'r1_pb_n': 800} if i == 10 else {}))
case('id_pb_pos88', dict(OK, **{'ne1_has': ['r1_pb_n=self_h_n@0']}), x=P(lambda n, b, i: {'r1_pb_n': 800} if i == 88 else {}))
case('id_r1_only_p', dict(OK, **{'R1__not_evaluable': []}), draw=M(lambda n, b, i: {'tex_hits': 1}))
case('id_ident_rows_ignore_draws', dict(OK, **{'ne1_has': ['r1_pb_n=self_h_n@0']}),
     main=P(lambda n, b, i: {'draws': 100} if i == 50 else {}), x=P(lambda n, b, i: {'r1_pb_n': 800} if i == 50 else {}))
IDM = lambda f: M(lambda n, b, i: f if (b == 2 and i == 50) else {})
case('id_stg_far_edge', dict(OK, **{'ne2_not': ['r2_stg=bl_prep_n@2']}), x=IDM({'r2_stg': 9200 + 726}))
case('id_stg_far_over', dict(OK, **{V2: 'NOT_EVALUABLE', V1: 'OPEN', 'ne2_has': ['r2_stg=bl_prep_n@2']}),
     x=IDM({'r2_stg': 9200 + 727}))
case('id_stg_p_over', dict(OK, **{'ne2_has': ['r2_stg=bl_prep_n@3']}), x=ID_ROW({'r2_stg': 9100 + 727}))
case('id_slots_p_over', dict(OK, **{'ne2_has': ['r2_slots=bl_res_n@3']}), x=ID_ROW({'r2_ot_sl': 18800 + 3793}))
case('id_nul_p_over', dict(OK, **{'ne2_has': ['r2_wr+wo=nul@3']}), x=ID_ROW({'r2_nul_n': 1109}))
case('id_slots_edge', dict(OK, **{'ne2_not': ['r2_slots=bl_res_n@2']}), x=IDM({'r2_ot_sl': 18800 + 3792}))
case('id_slots_over', dict(OK, **{'ne2_has': ['r2_slots=bl_res_n@2']}), x=IDM({'r2_ot_sl': 18800 + 3793}))
for fld in ('r2_cl_sl', 'r2_cl_nul', 'r2_mx_sl'):
    case('id_slots_' + fld, dict(OK, **{'ne2_has': ['r2_slots=bl_res_n@2']}), x=IDM({fld: X_M[fld] + 3793}))
case('id_rep_edge', dict(OK, **{'ne2_not': ['r2_rep=cl+mx@2']}), x=IDM({'r2_rep': 4608}))
case('id_rep_over', dict(OK, **{'ne2_has': ['r2_rep=cl+mx@2']}), x=IDM({'r2_rep': 4609}))
case('id_rep_under_edge', dict(OK, **{'ne2_not': ['r2_rep=cl+mx@2']}), x=IDM({'r2_rep': 4592}))
case('id_rep_under', dict(OK, **{'ne2_has': ['r2_rep=cl+mx@2']}), x=IDM({'r2_rep': 4591}))
case('id_rep_mx', dict(OK, **{'ne2_has': ['r2_rep=cl+mx@2']}), x=IDM({'r2_mx': 191}))
case('id_rep_p_arm', dict(OK, **{'ne2_has': ['r2_rep=cl+mx@3']}), x=ID_ROW({'r2_rep': 4509}))
case('id_nul_edge', dict(OK, **{'ne2_not': ['r2_wr+wo=nul@3']}), x=ID_ROW({'r2_nul_n': 1108}))
case('id_nul_high_edge', dict(OK, **{'ne2_not': ['r2_wr+wo=nul@2']}), x=IDM({'r2_nul_n': 1092}))
case('id_nul_high', dict(OK, **{'ne2_has': ['r2_wr+wo=nul@2']}), x=IDM({'r2_nul_n': 1091}))
case('id_nul_over', dict(OK, **{'ne2_has': ['r2_wr+wo=nul@2']}), x=IDM({'r2_nul_n': 1109}))
case('id_nul_wo', dict(OK, **{'ne2_has': ['r2_wr+wo=nul@2']}), x=IDM({'r2_wo_n': 534}))
case('id_rm_edge', dict(OK, **{'ne2_not': ['r2_rm_sl=s_cl@3']}), x=ID_ROW({'r2_rm_sl': 3400 + 268}))
case('id_rm_over', dict(OK, **{'ne2_has': ['r2_rm_sl=s_cl@3']}), x=ID_ROW({'r2_rm_sl': 3400 + 269}))
case('id_rm_nul', dict(OK, **{'ne2_has': ['r2_rm_sl=s_cl@3']}), x=ID_ROW({'r2_s_cl_nul': 200 + 269}))
case('id_ns_top_edge', dict(OK, **{'ne2_not': ['r2_ns=bl_res@2']}), x=IDM({'r2_ot_ns': 1793000 + 292300}))
case('id_ns_top_over', dict(OK, **{V2: 'NOT_EVALUABLE', 'ne2_has': ['r2_ns=bl_res@2']}), x=IDM({'r2_ot_ns': 1793000 + 292301}))
case('id_ns_low_edge', dict(OK, **{'ne2_not': ['r2_ns=bl_res@2']}), x=IDM({'r2_ot_ns': 1793000 - 292300}))
case('id_ns_low_over', dict(OK, **{'ne2_has': ['r2_ns=bl_res@2']}), x=IDM({'r2_ot_ns': 1793000 - 292301}))
case('id_ns_units_us', dict(OK, **{'ne2_has': ['r2_ns=bl_res@2']}), x=IDM({'r2_mx_ns': 100000 + 400000}))
case('id_ns_p_arm', dict(OK, **{'ne2_has': ['r2_ns=bl_res@3']}), x=ID_ROW({'r2_cl_ns': 1700000 + 400000}))
case('id_ns_bl_res_us', dict(OK, **{'ne2_has': ['r2_ns=bl_res@2']}), x=IDM({'bl_res_us': 3200 + 400}))
# ------------------------------------------------------------------ R1 samplers, bounds, pre/post agreement, arming
for nm, fields, want in (('smp_hit_010', {'r1_hit_t': 4700, 'r1_hit_ns': 4700 * 25}, False),
                         ('smp_hit_0099', {'r1_hit_t': 4699, 'r1_hit_ns': 4699 * 25}, True),
                         ('smp_hit_015', {'r1_hit_t': 7050, 'r1_hit_ns': 7050 * 25}, False),
                         ('smp_hit_0151', {'r1_hit_t': 7051, 'r1_hit_ns': 7051 * 25}, True),
                         ('smp_fast_005', {'r1_rbf_n': 2240, 'r1_rbf_ns': 2240 * 20}, False),
                         ('smp_fast_0049', {'r1_rbf_n': 2239, 'r1_rbf_ns': 2239 * 20}, True),
                         ('smp_fast_0075', {'r1_rbf_n': 3360, 'r1_rbf_ns': 3360 * 20}, False),
                         ('smp_fast_0076', {'r1_rbf_n': 3361, 'r1_rbf_ns': 3361 * 20}, True),
                         ('smp_self_0012', {'r1_sn': 1200, 'texmemo_stale': 1200, 'r1_pb_n': 500, 'r1_self_h_n': 500,
                                            'r1_self_m_n': 100}, False),
                         ('smp_self_0119', {'r1_sn': 1200, 'texmemo_stale': 1200, 'r1_pb_n': 500, 'r1_self_h_n': 500,
                                            'r1_self_m_n': 99}, True),
                         ('smp_self_0019', {'r1_sn': 1200, 'texmemo_stale': 1200, 'r1_self_m_n': 215}, False),
                         ('smp_self_0191', {'r1_sn': 1200, 'texmemo_stale': 1200, 'r1_self_m_n': 216}, True),
                         ('smp_self_s_counts', {'r1_sn': 1200, 'texmemo_stale': 1200, 'r1_self_m_n': 200,
                                                'r1_self_s_n': 16}, True)):
    name = nm.split('_')[1]
    case(nm, dict(OK, **{('ne1_has' if want else 'ne1_not'): ['sampler_' + name]}),
         x=(lambda f: P(lambda n, b, i: f))(fields),
         draw=P(lambda n, b, i: {'b_texn': 51400}) if 'r1_sn' in fields else None)


def post_fields(mp, rates=(8 / 9, 8 / 9, 2 / 3)):
    """mp post-mode key misses of 1800, pre half 1800 - mp; q and p at equal rates per table (F4 stays quiet)."""
    pre = 1800 - mp
    d = {'r1_mp': mp, 'r1_mp_ns': mp * 480}
    for t, r, price in (('w4', rates[0], 475), ('d16', rates[1], 475), ('w8', rates[2], 500)):
        p = round(r * mp)
        d.update({'r1_%s_q' % t: round(r * pre), 'r1_%s_p' % t: p, 'r1_%s_pns' % t: p * price})
    return d


for nm, mp, want in (('smp_post_045', 810, False), ('smp_post_0449', 809, True), ('smp_post_055', 990, False),
                     ('smp_post_0551', 991, True)):
    case(nm, dict(OK, **({'ne1_has': ['sampler_post'], 'ne1_not': ['prepost_w4', 'prepost_d16', 'prepost_w8']} if want
                         else {'ne1_not': ['sampler_post', 'prepost_w4', 'prepost_d16', 'prepost_w8']})),
         x=(lambda f: P(lambda n, b, i: f))(post_fields(mp)))
case('smp_post_W_scaled', dict(OK, **{T1 + 'd16__W': 880 * 1800 / 990, T1 + 'd16__t_T': 475.0, 'R1__terms__t_miss': 480.0}),
     x=P(lambda n, b, i: post_fields(810)))
for nm, fields, flag, bad in (('bound_qp_edge', {'r1_w4_q': 900, 'r1_w4_p': 900}, 'bound_w4_qp', False),
                              ('bound_qp_over', {'r1_w4_q': 901, 'r1_w4_p': 900}, 'bound_w4_qp', True),
                              ('bound_pns_edge', {'r1_d16_pns': 432000}, 'bound_d16_pns', False),
                              ('bound_pns_over', {'r1_d16_pns': 432001}, 'bound_d16_pns', True),
                              ('bound_lose_edge', {'r1_w8_lose': 47000}, 'bound_w8_lose', False),
                              ('bound_lose_over', {'r1_w8_lose': 47001}, 'bound_w8_lose', True),
                              ('bound_rb_edge', {'r1_d16_rb': 1600}, 'bound_d16_rb', False),
                              ('bound_rb_over', {'r1_d16_rb': 1601}, 'bound_d16_rb', True),
                              ('bound_rbn_edge', {'r1_rb_n': 4800}, 'bound_rb_n', False),
                              ('bound_rbn_over', {'r1_rb_n': 4801}, 'bound_rb_n', True)):
    case(nm, dict(OK, **{('ne1_has' if bad else 'ne1_not'): [flag]}), x=(lambda f: P(lambda n, b, i: f))(fields))
case('prepost_089_067', dict(OK, **{V1: 'NOT_EVALUABLE', 'ne1_has': ['prepost_d16'], 'ne1_not': ['prepost_w4']}),
     x=P(lambda n, b, i: {'r1_d16_p': 600, 'r1_d16_pns': 600 * 475}))
PP = {'r1_mn': 2000, 'texmemo_collide': 2000, 'r1_mp': 1000, 'r1_mp_ns': 480000, 'r1_w4_p': 800, 'r1_w8_p': 600,
      'r1_d16_q': 800}
case('prepost_edge_0019', dict(OK, **{'ne1_not': ['prepost_d16']}),
     x=P(lambda n, b, i: dict(PP, r1_d16_p=781, r1_d16_pns=781 * 475)), draw=P(lambda n, b, i: {'b_texn': 50408}))
case('prepost_edge_0021', dict(OK, **{'ne1_has': ['prepost_d16']}),
     x=P(lambda n, b, i: dict(PP, r1_d16_p=779, r1_d16_pns=779 * 475)), draw=P(lambda n, b, i: {'b_texn': 50408}))
case('prepost_negative', dict(OK, **{'ne1_has': ['prepost_d16']}),
     x=P(lambda n, b, i: dict(PP, r1_d16_p=821, r1_d16_pns=821 * 475)), draw=P(lambda n, b, i: {'b_texn': 50408}))
case('prepost_se_widens', dict(OK, **{'ne1_not': ['prepost_d16']}),
     x=P(lambda n, b, i: {'r1_d16_p': 728 if (b // 2) % 2 == 0 else 818,
                          'r1_d16_pns': (728 if (b // 2) % 2 == 0 else 818) * 475}))
case('prepost_w8', dict(OK, **{'ne1_has': ['prepost_w8'], 'ne1_not': ['prepost_d16']}),
     x=P(lambda n, b, i: {'r1_w8_p': 500, 'r1_w8_pns': 500 * 500}))
for fld in ('r1_hn', 'r1_mn', 'r1_hit_t', 'r1_mp'):
    case('armed_' + fld, dict(OK, **{V1: 'NOT_EVALUABLE', 'ne1_has': ['armed_' + fld]}), x=P(lambda n, b, i, f=fld: {f: 0}))
case('r1_m_leak', dict(OK, **{V1: 'NOT_EVALUABLE', 'ne1_has': ['m_leak'], C1: 792.0}),
     x=M(lambda n, b, i: {'r1_hn': 5} if (b == 5 and i == 40) else {}))
case('r1_m_leak_ns_field', dict(OK, **{'ne1_has': ['m_leak']}),
     x=M(lambda n, b, i: {'r1_self_s_ns': 5} if (b == 1 and i == 60) else {}))
case('r1_m_leak_outside_window', dict(OK, **{'R1__not_evaluable': []}),
     x=M(lambda n, b, i: {'r1_hn': 5} if i in (5, 89) else {}))
DEAD = dict(R1_ZERO, tex_hits=0, texmemo_collide=0, texmemo_stale=0, texfast_ok=0, texfast_no=0)
case('arm_by_text_dead_p_block', dict(OK, **{V1: 'NOT_EVALUABLE', C1: 792.0 * 0.75,
                                             'ne1_has': ['prepost_d16', 'armed_r1_hn']}),
     x=P(lambda n, b, i: DEAD if b == 4 else {}), draw=P(lambda n, b, i: {'tex_hits': 0, 'b_texn': 1400} if b == 4 else {}))
case('r1_reset_one_block', dict(OK, **{V1: 'OPEN', C1: 792.0, 'r1_pairs': 3, 'reset_blocks': [3],
                                       'ne1_not': ['resets'], 'R__pair_values': [1784.0, 1784.0, 1784.0]}),
     x=P(lambda n, b, i: ({'r1_reset': 1} if i == 40 else {'r1_d16_pns': 10 ** 9}) if b == 3 else {}))
case('r1_reset_two_blocks', dict(OK, **{V1: 'NOT_EVALUABLE', 'ne1_has': ['resets'], 'r1_pairs': 2}),
     x=P(lambda n, b, i: {'r1_reset': 1} if (b in (3, 4) and i == 40) else {}))
case('r1_reset_edges_ignored', dict(OK, **{'r1_pairs': 4, 'reset_blocks': []}),
     x=P(lambda n, b, i: {'r1_reset': 1} if i in (0, 9, 89) else {}))
# ------------------------------------------------------------------ R2 arming (C2(b): r2cen=1 in M, the replay in P only)
case('r2_m_replay_leak', dict(OK, **{V2: 'NOT_EVALUABLE', 'ne2_has': ['m_replay']}),
     x=M(lambda n, b, i: {'r2_rm_n': 1} if (b == 6 and i == 30) else {}))
case('r2_m_replay_outside', dict(OK, **{'R2__not_evaluable': []}), x=M(lambda n, b, i: {'r2_rm_ns': 7} if i == 5 else {}))
case('r2_armed_stg_m', dict(OK, **{V2: 'NOT_EVALUABLE', 'ne2_has': ['armed_stg']}),
     x=M(lambda n, b, i: {'r2_stg': 0, 'bl_prep_n': 0}))
case('r2_armed_stg_p', dict(OK, **{'ne2_has': ['armed_stg']}), x=P(lambda n, b, i: {'r2_stg': 0, 'bl_prep_n': 0}))
# ------------------------------------------------------------------ zero denominators: NOT_EVALUABLE, never NaN
for nm, fn, member in (('zd_hit_t', P(lambda n, b, i: {'r1_hit_t': 0, 'r1_hit_ns': 0}), 'R1'),
                       ('zd_d16_p', P(lambda n, b, i: {'r1_d16_p': 0, 'r1_d16_pns': 0}), 'R1'),
                       ('zd_rbf_n', P(lambda n, b, i: {'r1_rbf_n': 0, 'r1_rbf_ns': 0}), 'R1'),
                       ('zd_ham_t', P(lambda n, b, i: {'r1_ham_t': 0, 'r1_ham_ns': 0}), 'R1'),
                       ('zd_pb_n', P(lambda n, b, i: {'r1_pb_n': 0, 'r1_self_h_n': 0}), 'R1'),
                       ('zd_mp', P(lambda n, b, i: {'r1_mp': 0, 'r1_mp_ns': 0}), 'R1'),
                       ('zd_pre_half', P(lambda n, b, i: {'r1_mp': 1800, 'r1_mp_ns': 1800 * 480}), 'R1'),
                       ('zd_nul_n', M(lambda n, b, i: {'r2_nul_n': 0, 'r2_nul_ns': 0}), 'R2'),
                       ('zd_wr_n', M(lambda n, b, i: {'r2_wr_n': 0, 'r2_wr_ns': 0}), 'R2'),
                       ('zd_wo_n', M(lambda n, b, i: {'r2_wo_n': 0, 'r2_wo_ns': 0}), 'R2'),
                       ('zd_st_n', M(lambda n, b, i: {'r2_st_n': 0, 'r2_st_ns': 0}), 'R2'),
                       ('zd_unsampled', M(lambda n, b, i: {'r2_s_cl_sl': 25600, 'r2_s_cl_nul': 1600}), 'R2'),
                       ('zd_SZ', M(lambda n, b, i: {'r2_cl_sl': 1600, 'r2_cl_nul': -1600, 'r2_s_cl_sl': 200,
                                                    'r2_s_cl_nul': 0, 'r2_ot_sl': 46000}), 'R2')):
    case(nm, dict(OK, **{member + '__verdict': 'NOT_EVALUABLE', VR: 'NOT_EVALUABLE',
                         ('ne1_has' if member == 'R1' else 'ne2_has'): ['zero_den']}), x=fn)
case('zd_pair_only', dict(OK, **{V1: 'NOT_EVALUABLE', 'R1__two_se': None, 'ne1_not': ['zero_den'], C1: 792.0}),
     x=P(lambda n, b, i: {'r1_ham_t': 0, 'r1_ham_ns': 0} if b == 3 else {}))
case('zd_pair_only_r2', dict(OK, **{V2: 'NOT_EVALUABLE', 'R2__two_se': None, 'ne2_not': ['zero_den']}),
     x=M(lambda n, b, i: {'r2_st_n': 0, 'r2_st_ns': 0} if b == 5 else {}))
case('zd_one_pair_draft', dict(OK, **{V1: 'NOT_EVALUABLE', 'pairs': 1, 'R1__two_se': None}), blocks=2, draft=True)
# ------------------------------------------------------------------ window edges, draws > 3000, unit traps
WIN = lambda pos, d: P(lambda n, b, i: {'r1_d16_pns': 380000 + d} if i == pos else {})
case('win_pos9_89_absurd', dict(OK, **{C1: 792.0, CUP: 992.0, 'price__dt_us__pair_mean': 3000.0, 'bda_scan__P': 68.0,
                                       'R1__not_evaluable': [], 'R2__not_evaluable': []}),
     x=lambda n, b, arm, i: {'r1_d16_pns': 10 ** 9, 'r2_cl_ns': 10 ** 9, 'r1_hn': 1} if i in (9, 89) else {},
     main=lambda n, b, arm, i: {'dt_us': 10 ** 7} if i in (9, 89) else {},
     draw=lambda n, b, arm, i: {'bda_scan': 10 ** 6} if i in (9, 89) else {})
case('win_pos10_counts', dict(OK, **{C1: 798.4}), x=WIN(10, 252800))
case('win_pos88_counts', dict(OK, **{C1: 798.4}), x=WIN(88, 252800))
case('win_pos10_m', dict(OK, **{T2 + 'T_star': 1300.0 + 4 * 79 * 800 * 8 / 7 / 316 / 1000}),
     x=M(lambda n, b, i: {'r2_cl_ns': 1307500 + 79 * 800, 'r2_ot_ns': 1793000 - 79 * 800} if i == 10 else {}))
case('draws_3000_excluded', dict(OK, **{C1: 792.0, 'est_frames__P': 312, 'R1__not_evaluable': []}),
     main=P(lambda n, b, i: {'draws': 3000} if i == 50 else {}), x=WIN(50, 10 ** 8))
case('draws_3001_included', dict(OK, **{C1: 798.4, 'est_frames__P': 316}),
     main=P(lambda n, b, i: {'draws': 3001} if i == 50 else {}), x=WIN(50, 252800))
case('draws_m_excluded', dict(OK, **{CUP: 992.0, 'est_frames__M': 312}),
     main=M(lambda n, b, i: {'draws': 3000} if i == 50 else {}), x=M(lambda n, b, i: {'r2_wr_ns': 10 ** 8} if i == 50 else {}))
case('unit_ns_vs_us', dict(OK, **{C1: 792.0 + 1.0, T1 + 'd16__R': 57.0}), x=P(lambda n, b, i: {'r1_d16_rbns': 85000}))
case('price_pairs', dict(OK, **{'price__dt_us__pair_mean': 3000.0, 'price__dt_us__two_se': 2 * (10000 ** 2 * 4 / 3) ** 0.5 / 2,
                                'price__cpu_gpu_us__pair_mean': 2700.0}),
     main=P(lambda n, b, i: {'dt_us': 46000 if (b // 2) % 2 == 0 else 26000}))
# ------------------------------------------------------------------ arm assertions (texts and gates_base)
for nm, extra in (('texmemo2', 'texmemo2=1'), ('texfastcheck', 'texfastcheck=1'), ('m4baton', 'm4baton=1'),
                  ('fslean', 'fslean=1'), ('bindpack0', 'bindpack=0'), ('bindwit', 'bindwit=1'), ('bindalt', 'bindalt=1'),
                  ('blmove', 'blmove=1'), ('bindfloor', 'bindfloor=1'), ('cbmove', 'cbmove=1')):
    key = extra.split('=')[0]
    text = (' '.join(p if p.split('=')[0] != key else extra for p in GATES_TEXT.split())
            if (' ' + key + '=') in (' ' + GATES_TEXT) else extra + ' ' + GATES_TEXT)
    case('assert_' + nm, dict(verdict='NOT_ADMITTED', failed=['gates_exact'], **{V1: 'NOT_EVALUABLE', V2: 'NOT_EVALUABLE',
                                                                              'ne1_has': ['arm_asserts'],
                                                                              'ne2_has': ['arm_asserts']}),
         gates_copy=text, gates_file='copy')
for nm, extra in (('bindpack1', 'bindpack=1'), ('bindwit0', 'bindwit=0'), ('cbmove0', 'cbmove=0')):
    case('assert_ok_' + nm, dict(verdict='NOT_ADMITTED', failed=['gates_exact'], **{'ne1_not': ['arm_asserts'],
                                                                                    'arm_asserts': True}),
         gates_copy=extra + ' ' + GATES_TEXT, gates_file='copy')
case('assert_first_assignment_wins', dict(verdict='NOT_ADMITTED', failed=['gates_exact'], arm_asserts=True),
     gates_copy=GATES_TEXT + ' texmemo2=1', gates_file='copy')
for nm, arm, old, new in (('bindlap_m', 1, 'bindlap=1', 'bindlap=0'), ('bindlap_p', 0, 'bindlap=1', 'bindlap=0'),
                          ('r1cen_p', 0, 'r1cen=2', 'r1cen=1'), ('r1cen_m', 1, 'r1cen=0', 'r1cen=2'),
                          ('r2cen_p', 0, 'r2cen=2', 'r2cen=1'), ('r2cen_m', 1, 'r2cen=1', 'r2cen=2'),
                          ('texmemo2_text', 1, 'mutsite=1', 'mutsite=1 texmemo2=1')):
    case('assert_text_' + nm, dict(verdict='NOT_ADMITTED', arm_asserts=False,
                                   **{'ne1_has': ['arm_asserts'], 'ne2_has': ['arm_asserts']}),
         gate_arm=(lambda a, o, w: (lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                                                    % (arm, b, START + PERIOD * b,
                                                       TEXT[arm].replace(o, w) if arm == a else TEXT[arm])]))(arm, old, new))
case('assert_one_arm_only', dict(arm_asserts=False, **{'ne1_has': ['arm_asserts']}), blocks=1, draft=True)
# ------------------------------------------------------------------ admission, one check at a time
case('binary', dict(verdict='NOT_ADMITTED', failed=['binary'], lines_has=['CONSEQUENCE: R1 NOT_ADMITTED',
                                                                          'VERDICT: NOT_ADMITTED failed=binary',
                                                                          'REPORT OF A NOT_ADMITTED RUN']),
     meta=dict(binary_sha256='cd' * 32))
case('installed', dict(verdict='NOT_ADMITTED', failed=['installed_now']), installed='cd' * 32)
case('installed_draft', dict(verdict='NOT_ADMITTED', failed=['installed_now']), installed='cd' * 32, draft=True)
case('pin_env', dict(verdict='NOT_ADMITTED', failed=['pinned', 'env_exact']),
     env={k: v for k, v in ENV_OK.items() if k != 'KYTY_GPU_CLOCK_PIN'})
case('pin_two', dict(verdict='NOT_ADMITTED', failed=['pinned']), pins=(PIN, PIN))
case('pin_mode2', dict(verdict='NOT_ADMITTED', failed=['pinned']), pins=('GpuClockPin: mode 2',))
case('pin_malformed', dict(verdict='NOT_ADMITTED', failed=['pinned']), pins=('GpuClockPin: mode X',))
case('pin_absent', dict(verdict='NOT_ADMITTED', failed=['pinned']), pins=())
case('env_rec', dict(verdict='NOT_ADMITTED', failed=['env_exact']), env=dict(ENV_OK, KYTY_REC='C:/x.mp4'))
case('env_markers', dict(verdict='NOT_ADMITTED', failed=['env_exact']), env=dict(ENV_OK, KYTY_GPU_MARKERS='2'))
case('env_schedule', dict(verdict='NOT_ADMITTED', failed=['env_exact']),
     env=dict(ENV_OK, KYTY_GATE_SCHEDULE='90+1800:' + TEXT[1] + '|' + TEXT[0]))
case('meta_schedule', dict(verdict='NOT_ADMITTED', failed=['env_exact']), meta=dict(schedule='90+1800:x|y'))
case('env_vk', dict(verdict='NOT_ADMITTED', failed=['env_vk']), env=dict(ENV_OK, VK_LAYER_PATH='C:/x'))
case('hold', dict(verdict='NOT_ADMITTED', failed=['hold']), meta=dict(hold_s=180))
case('hold_draft_skipped', dict(OK), meta=dict(hold_s=180), draft=True)
case('two_attempts', dict(verdict='NOT_ADMITTED', failed=['one_ok_attempt']),
     meta=dict(attempts=[dict(label='a1', outcome='timeout', hold_exit=None),
                         dict(label='a2', outcome='ok', hold_exit=None, stable_frame=500)]))
case('hold_exit', dict(verdict='NOT_ADMITTED', failed=['one_ok_attempt']),
     meta=dict(attempts=[dict(label='a1', outcome='ok', hold_exit=3, stable_frame=500)]))
case('attempt_not_ok', dict(verdict='NOT_ADMITTED', failed=['one_ok_attempt']),
     meta=dict(attempts=[dict(label='a1', outcome='timeout', hold_exit=None)]))
case('prereg_path', dict(verdict='NOT_ADMITTED', failed=['prereg']),
     meta=dict(prereg=dict(path='C:\\kyty\\s120\\pred\\02_x.md', sha256=PSHA, bytes=PBYTES)))
case('prereg_json_sha', dict(verdict='NOT_ADMITTED', failed=['prereg_sha']),
     meta=dict(prereg=dict(path=PRED, sha256='cd' * 32, bytes=PBYTES)))
case('prereg_file_sha', dict(verdict='NOT_ADMITTED', failed=['prereg_sha']), pred=('cd' * 32, PBYTES),
     meta=dict(prereg=dict(path=PRED, sha256='cd' * 32, bytes=PBYTES)))
case('prereg_file_bytes', dict(verdict='NOT_ADMITTED', failed=['prereg_sha']), pred=(PSHA, PBYTES + 1),
     meta=dict(prereg=dict(path=PRED, sha256=PSHA, bytes=PBYTES + 1)))
case('prereg_json_bytes', dict(verdict='NOT_ADMITTED', failed=['prereg_sha']),
     meta=dict(prereg=dict(path=PRED, sha256=PSHA, bytes=PBYTES + 1)))
case('prereg_json_no_bytes', dict(verdict='NOT_ADMITTED', failed=['prereg_sha']),
     meta=dict(prereg=dict(path=PRED, sha256=PSHA)))
case('prereg_forward_slash_ok', dict(OK), meta=dict(prereg=dict(path='C:/kyty/s120/pred/01_cen120.md', sha256=PSHA,
                                                                  bytes=PBYTES)))
case('prereg_sealed_sha', dict(verdict='NOT_ADMITTED', failed=['prereg_sha']), pred=('cd' * 32, PBYTES))
case('prereg_sealed_bytes', dict(verdict='NOT_ADMITTED', failed=['prereg_sha']), pred=(PSHA, PBYTES + 1))
case('prereg_unfilled', dict(verdict='NOT_ADMITTED', failed=['prereg_sha']), pred=('', 0))
case('prereg_unfilled_bytes', dict(verdict='NOT_ADMITTED', failed=['prereg_sha']), pred=(PSHA, 0))
case('prereg_absent_meta', dict(verdict='NOT_ADMITTED', failed=['prereg', 'prereg_sha']), meta=dict(prereg=None))
case('prereg_draft_skipped', dict(OK, lines_has=['DRAFT: unsealed', 'VERDICT: ADMITTED DRAFT']),
     meta=dict(prereg=None, hold_s=180), pred=('', 0), draft=True)
case('gates_meta_changed', dict(verdict='NOT_ADMITTED', failed=['gates_exact']),
     meta=dict(gates=GATES_TEXT.replace('dawalk=1', 'dawalk=0')))
case('gates_whitespace_ok', dict(OK), meta=dict(gates='  ' + GATES_TEXT.replace(' ', '   ') + '  '))
case('gates_file_sha', dict(verdict='NOT_ADMITTED', failed=['gates_exact'], arm_asserts=True),
     gates_copy=GATES_TEXT, gates_file='copy', meta=dict(gates=GATES_TEXT))
case('gates_file_missing', dict(verdict='NOT_ADMITTED', failed=['gates_exact']), gates_file='C:/kyty/s120/fx_none.txt')
case('gate_other_name', dict(verdict='NOT_ADMITTED', failed=['gate_lines']), extra_log=('Gate: dawalk=0 frame=1890',))
case('gate_wrong_value', dict(verdict='NOT_ADMITTED', failed=['gate_lines']), extra_log=('Gate: r2cen=2 frame=1890',))
case('gate_off_block', dict(verdict='NOT_ADMITTED', failed=['gate_lines']), extra_log=('Gate: r1cen=2 frame=1801',))
case('gate_before_start', dict(verdict='NOT_ADMITTED', failed=['gate_lines']), extra_log=('Gate: r1cen=2 frame=1710',))
case('gate_unknown_block', dict(verdict='NOT_ADMITTED', failed=['gate_lines']), extra_log=('Gate: r1cen=2 frame=3240',))
case('gate_malformed', dict(verdict='NOT_ADMITTED', failed=['gate_lines']), extra_log=('Gate: r1cen=2',))
case('gate_every_block_ok', dict(OK),
     gate_lines=lambda b, arm: ['Gate: %s=%s frame=%d' % (k, v, START + PERIOD * b) for k, v in VALUES[arm].items()])
ARM_FAIL = dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'pairs', 'streams'][:3])
GA = 'GateArm: arm=%d arms=%d block=%d frame=%d period=%d abba=%d text=%s'
case('arm_text', ARM_FAIL, gate_arm=lambda b, arm: [GA % (arm, 2, b, START + PERIOD * b, 90, 1, TEXT[0])])
case('arm_count', ARM_FAIL, gate_arm=lambda b, arm: [GA % (arm, 3, b, START + PERIOD * b, 90, 1, TEXT[arm])])
case('arm_period', ARM_FAIL, gate_arm=lambda b, arm: [GA % (arm, 2, b, START + PERIOD * b, 80, 1, TEXT[arm])])
case('arm_abba', ARM_FAIL, gate_arm=lambda b, arm: [GA % (arm, 2, b, START + PERIOD * b, 90, 0, TEXT[arm])])
case('arm_frame', ARM_FAIL, gate_arm=lambda b, arm: [GA % (arm, 2, b, START + PERIOD * b + 1, 90, 1, TEXT[arm])])
case('arm_order', ARM_FAIL, order=(0, 1, 0, 1))
case('arm_one_malformed', ARM_FAIL, extra_log=('GateArm: arm=0 block=9',))
case('arm_dup', ARM_FAIL, extra_log=('GateArm: arm=0 arms=2 block=0 frame=1800 period=90 abba=1 text=' + TEXT[0],))
case('arm_gap', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'pairs']),
     gate_arm=lambda b, arm: [] if b == 3 else [GA % (arm, 2, b, START + PERIOD * b, 90, 1, TEXT[arm])])
for mk, text in (('hang', 'GpuHangAbort: tick=5'), ('slow', 'GpuWaitSlow: tick=5'), ('mhung', 'GpuMarkerHung: cs=1'),
                 ('ckpt', 'GpuCheckpointHang: op=1'), ('lost', 'Vulkan: ErrorDeviceLost'),
                 ('term', '--- std::terminate ---'), ('abort', '--- abort() ---'), ('fatal', '--- Fatal Error ---'),
                 ('unh', 'Unhandled exception: 0xc0000005'), ('err', '--- Error ---')):
    case('marker_' + mk, dict(verdict='NOT_ADMITTED', failed=['no_marker']), extra_log=(text,))
case('marker_stdout', dict(verdict='NOT_ADMITTED', failed=['no_marker']), stdout_lines=('--- Fatal Error ---',))
SKIP = 'AsyncPipelines: skipped draw 0x1234 (pipeline not ready)'
case('skip_in_window', dict(verdict='NOT_ADMITTED', failed=['no_skip_window'], skipped_in_window=1),
     after=lambda n: [SKIP] if n == START + PERIOD * 2 + 30 else [])
case('skip_window_first', dict(verdict='NOT_ADMITTED', failed=['no_skip_window']),
     after=lambda n: [SKIP] if n == START + PERIOD * 2 + 10 else [])
case('skip_window_last', dict(verdict='NOT_ADMITTED', failed=['no_skip_window']),
     after=lambda n: [SKIP] if n == START + PERIOD * 2 + 88 else [])
case('skip_pos_89_ok', dict(OK, skipped_draws=1, skipped_in_window=0), after=lambda n: [SKIP] if n == START + PERIOD * 2 + 89 else [])
case('skip_pos_9_ok', dict(OK, skipped_draws=1), after=lambda n: [SKIP] if n == START + PERIOD * 2 + 9 else [])
case('skip_pre_start_ok', dict(OK, skipped_draws=1), after=lambda n: [SKIP] if n == START - 3 else [])
case('skip_before_frames_ok', dict(OK, skipped_draws=1), pins=(PIN, SKIP))
case('skip_after_blocks_ok', dict(OK), extra_log=(SKIP,))
case('skip_beyond_blocks_ok', dict(OK, skipped_draws=1), post=40, after=lambda n: [SKIP] if n == START + PERIOD * BLOCKS + 30 else [],
     gate_arm=lambda b, arm: [] if b >= BLOCKS else [GA % (arm, 2, b, START + PERIOD * b, 90, 1, TEXT[arm])])
W_N = START + 1 + PERIOD * 3 + 50
case('streams_missing_x', dict(verdict='NOT_ADMITTED', failed=['streams', 'pairs']), drop=(('x', W_N),))
case('streams_missing_draw', dict(verdict='NOT_ADMITTED', failed=['streams', 'pairs']), drop=(('draw', W_N),))
case('streams_field_missing', dict(verdict='NOT_ADMITTED', failed=['streams', 'pairs']), strip=(('x', W_N, 'r2_rm_n'),))
case('streams_draw_field', dict(verdict='NOT_ADMITTED', failed=['streams', 'pairs']), strip=(('draw', W_N, 'bda_scan'),))
case('streams_main_field', dict(verdict='NOT_ADMITTED', failed=['streams', 'pairs']), strip=(('main', W_N, 'cpu_gpu_us'),))
case('streams_dup', dict(verdict='NOT_ADMITTED', failed=['streams', 'pairs']), dup=(W_N,))
case('streams_outside_window', dict(verdict='NOT_ADMITTED', failed=['pairs']), drop=(('x', START + 1 + PERIOD * 3 + 5),))
case('streams_last_row_exempt', dict(OK), post=20, drop=(('x', START + PERIOD * BLOCKS + 20),))
case('streams_partial_block', dict(verdict='NOT_ADMITTED', failed=['streams']), post=20,
     drop=(('x', START + PERIOD * BLOCKS + 19),))
case('label_arm', dict(verdict='NOT_ADMITTED', failed=['pairs']), main=lambda n, b, arm, i: {'arm': 1 - arm} if (b == 2 and i == 30) else {})
case('label_blk', dict(verdict='NOT_ADMITTED', failed=['pairs']), main=lambda n, b, arm, i: {'blk': b + 1} if (b == 5 and i == 70) else {})
case('pairs_edge', dict(OK, pairs=4), min_pairs=SMALL)
case('pairs_few', dict(verdict='NOT_ADMITTED', failed=['pairs']), min_pairs=SMALL + 1)
case('pairs_default_30', dict(OK, pairs=30), blocks=60, min_pairs=None)
case('pairs_default_29', dict(verdict='NOT_ADMITTED', failed=['pairs'], pairs=29), blocks=58, min_pairs=None)
case('pairs_draft_skipped', dict(OK, pairs=2), blocks=4, min_pairs=None, draft=True)
case('pairs_odd_block_unpaired', dict(OK, pairs=4, complete_blocks=9), blocks=9)
case('idle_edge', dict(OK), meta=dict(pre_run=dict(gpu_util_median=10)))
case('idle_11', dict(verdict='NOT_ADMITTED', failed=['idle']), meta=dict(pre_run=dict(gpu_util_median=11)))
case('idle_missing', dict(verdict='NOT_ADMITTED', failed=['idle']), meta=dict(pre_run={}))

# ------------------------------------------------------------------ a NOT_ADMITTED run: members NOT_EVALUABLE, FAIL wins
NA = dict(pre_run=dict(gpu_util_median=11))
case('na_members_ne', dict(verdict='NOT_ADMITTED', failed=['idle'],
                           **{V1: 'NOT_EVALUABLE', V2: 'NOT_EVALUABLE', VR: 'NOT_EVALUABLE', 'ne1_has': ['not_admitted'],
                              'ne2_has': ['not_admitted'], C1: 792.0,
                              'lines_has': ['CONSEQUENCE: R1 NOT_ADMITTED - "повтор cen120r',
                                            'CONSEQUENCE: R2 NOT_ADMITTED - ', 'CONSEQUENCE: R NOT_ADMITTED - ',
                                            'REPORT OF A NOT_ADMITTED RUN'], 'summary__verdict': 'NOT_ADMITTED',
                              'last_has': ['CONSEQUENCE: NOT_ADMITTED - "повтор cen120r']}), meta=NA)
case('na_fail_r1_dominates', dict(verdict='NOT_ADMITTED', failed=['idle'],
                                  **{V1: 'FAIL', V2: 'NOT_EVALUABLE', VR: 'FAIL',
                                     'lines_has': ['CONSEQUENCE: R1 FAIL - ', 'CONSEQUENCE: R2 NOT_ADMITTED - ',
                                                   'CONSEQUENCE: R FAIL - '], 'summary__verdict': 'FAIL',
                                     'last_has': ['CONSEQUENCE: FAIL - "любой']}),
     meta=NA, x=P(lambda n, b, i: {'r1_w4_bad': 1} if (b == 0 and i == 40) else {}))
case('na_fail_r2_dominates', dict(verdict='NOT_ADMITTED', failed=['idle'],
                                  **{V1: 'NOT_EVALUABLE', V2: 'FAIL', VR: 'FAIL',
                                     'lines_has': ['CONSEQUENCE: R1 NOT_ADMITTED - ', 'CONSEQUENCE: R2 FAIL - ']}),
     meta=NA, x=M(lambda n, b, i: {'r2_bad': 1} if (b == 1 and i == 40) else {}))
case('admitted_fail_consequence', dict(OK, **{V2: 'FAIL', 'lines_has': ['CONSEQUENCE: R2 FAIL - "любой',
                                                                       'CONSEQUENCE: R FAIL - "любой']}),
     x=M(lambda n, b, i: {'r2_bad': 1} if (b == 1 and i == 40) else {}))
# ------------------------------------------------------------------ BDA regime labels (reported only)
for nm, v, want in (('300', 300, 'NEW'), ('301', 301, 'MIXED'), ('599', 599, 'MIXED'), ('600', 600, 'OLD')):
    case('regime_' + nm, dict(OK, **{'bda_scan__P_regime': want, 'bda_scan__M_regime': 'NEW', 'bda_scan__P': float(v),
                                     V1: 'OPEN'}),
         draw=(lambda v: P(lambda n, b, i: {'bda_scan': v}))(v))
case('regime_m_old', dict(OK, **{'bda_scan__M_regime': 'OLD', 'bda_scan__P_regime': 'NEW',
                                 'lines_has': ['bda_scan P 68.0 (NEW) M 1066.0 (OLD)']}),
     draw=M(lambda n, b, i: {'bda_scan': 1066}))
# ------------------------------------------------------------------ information terms (R1 warming, no-store; R2 rows)
case('r1_info_terms', dict(OK, **{T1 + 'w4__warm_ns': -37.5, T1 + 'w8__warm_ns': 280000 / 600 - 500,
                                  T1 + 'd16__warm_ns': -37.5, 'R1__terms__nost': 10.0, 'R1__terms__t_nost': 500.0}))
case('r1_warm_pre_price', dict(OK, **{T1 + 'w4__warm_ns': 25.0, T1 + 'w4__C': 559.384, T1 + 'd16__warm_ns': -37.5}),
     x=P(lambda n, b, i: {'r1_w4_qns': 400000}))
case('r1_warm_q0', dict(OK, **{T1 + 'w8__warm_ns': None, T1 + 'w8__W': 0.0}), x=P(lambda n, b, i: {'r1_w8_q': 0}))
case('r1_nost_zero', dict(OK, **{'R1__terms__nost': 0.0, 'R1__terms__t_nost': None, C1: 792.0}),
     x=P(lambda n, b, i: {'r1_nost': 0, 'r1_nost_ns': 0}))
case('r1_nost_price', dict(OK, **{'R1__terms__nost': 20.0, 'R1__terms__t_nost': 300.0}),
     x=P(lambda n, b, i: {'r1_nost': 20, 'r1_nost_ns': 6000}))
case('r2_info_terms', dict(OK, **{T2 + 'C_up_B849': 897.072, T2 + 'C_pt_traced': 522.272, T2 + 'dcc_share': 10 / 25600,
                                  T2 + 'K_rp_ok': True}))
case('r2_dcc_share', dict(OK, **{T2 + 'dcc_share': 0.25, 'lines_has': ['DCC-lock share of clean slots 0.2500']}),
     x=M(lambda n, b, i: {'r2_cl_dcc': 6400}))
case('r2_dcc_share_p_ignored', dict(OK, **{T2 + 'dcc_share': 10 / 25600}), x=P(lambda n, b, i: {'r2_cl_dcc': 6400}))
case('r2_krp_edge', dict(OK, **{T2 + 'K_rp_ok': True, T2 + 'p_c': 8.49, 'lines_has': ['replay proxy kept']}),
     x=lambda n, b, arm, i: (dict(S0, r2_cl_ns=230928, r2_ot_ns=3200500 - 230928 - 100000) if arm == 1
                             else {'r2_rm_ns': 0}))
case('r2_krp_below', dict(OK, **{T2 + 'K_rp_ok': False, 'lines_has': ['replay proxy rejected (K_rp < B)']}),
     x=lambda n, b, arm, i: (dict(S0, r2_cl_ns=230927, r2_ot_ns=3200500 - 230927 - 100000) if arm == 1
                             else {'r2_rm_ns': 0}))
case('r2_krp_none', dict(OK, **{T2 + 'K_rp_ok': None, 'lines_has': ['replay proxy -']}),
     x=P(lambda n, b, i: {'r2_rm_sl': 0, 'r2_rm_ns': 0, 'r2_rm_n': 0}))
# ------------------------------------------------------------------ R2 sampler (the 1/8 pre-loop sample, both arms)
for nm, fn, flag, bad in (('m_010', M(lambda n, b, i: {'r2_nul_n': 880}), 'sampler_r2@M', False),
                          ('m_0099', M(lambda n, b, i: {'r2_nul_n': 879}), 'sampler_r2@M', True),
                          ('m_015', M(lambda n, b, i: {'r2_nul_n': 1320}), 'sampler_r2@M', False),
                          ('m_0151', M(lambda n, b, i: {'r2_nul_n': 1321}), 'sampler_r2@M', True),
                          ('p_low', P(lambda n, b, i: {'r2_nul_n': 869}), 'sampler_r2@P', True),
                          ('p_edge', P(lambda n, b, i: {'r2_nul_n': 870}), 'sampler_r2@P', False),
                          ('big', M(lambda n, b, i: {'r2_big': 1600}), 'sampler_r2@M', True),
                          ('noimg', M(lambda n, b, i: {'r2_noimg': 2000}), 'sampler_r2@M', True),
                          ('odd_kept', M(lambda n, b, i: {'r2_odd': 1600}), 'sampler_r2@M', False),
                          ('zero_den', M(lambda n, b, i: {'r2_stg': 400, 'bl_prep_n': 400}), 'sampler_r2@M', True)):
    case('smp_r2_' + nm, dict(OK, **{('ne2_has' if bad else 'ne2_not'): [flag]}), x=fn)
# ------------------------------------------------------------------ R2 class bounds (window sums per arm, FAR)
for nm, fn, flag in (('rep', M(lambda n, b, i: {'r2_rep': 9000, 'r2_cl': 8800}), 'bound_rep<=prog@M'),
                     ('rep_p', P(lambda n, b, i: {'r2_rep': 8000, 'r2_cl': 7800}), 'bound_rep<=prog@P'),
                     ('prog', M(lambda n, b, i: {'r2_prog': 9000}), 'bound_prog<=img_stages@M'),
                     ('prog_noimg', M(lambda n, b, i: {'r2_noimg': 1300}), 'bound_prog<=img_stages@M'),
                     ('prog_big', M(lambda n, b, i: {'r2_big': 900}), 'bound_prog<=img_stages@M'),
                     ('prog_odd', M(lambda n, b, i: {'r2_odd': 900}), 'bound_prog<=img_stages@M'),
                     ('mx_eq', M(lambda n, b, i: {'r2_mx_eq': 2100}), 'bound_mx_eq<=mx_sl@M'),
                     ('sl_hit', M(lambda n, b, i: {'r2_sl_hit': 31000}), 'bound_sl_hit<=sl_eq@M'),
                     ('R_sl_hit', M(lambda n, b, i: {'r2_sl_hit': 28000}), 'bound_R_slots<=sl_hit@M'),
                     ('R_cl_sl', M(lambda n, b, i: {'r2_cl_sl': 25700}), 'bound_R_slots<=sl_hit@M'),
                     ('R_cl_nul', M(lambda n, b, i: {'r2_cl_nul': 1700}), 'bound_R_slots<=sl_hit@M'),
                     ('R_mx_eq', M(lambda n, b, i: {'r2_mx_eq': 1600}), 'bound_R_slots<=sl_hit@M'),
                     ('lod', M(lambda n, b, i: {'r2_cl_lod': 26000}), 'bound_lod<=cl_sl@M'),
                     ('dcc', M(lambda n, b, i: {'r2_cl_dcc': 26000}), 'bound_dcc<=cl_sl@M'),
                     ('bc', M(lambda n, b, i: {'r2_cl_bc': 26000}), 'bound_bc<=cl_sl@M'),
                     ('tick', M(lambda n, b, i: {'r2_cl_tick': 4500}), 'bound_tick<=cl@M'),
                     ('meta', M(lambda n, b, i: {'r2_cl_meta': 4500}), 'bound_meta<=cl@M'),
                     ('s_cl_ns', M(lambda n, b, i: {'r2_s_cl_ns': 1400000}), 'bound_s_cl_ns<=cl_ns@M'),
                     ('s_cl_sl', M(lambda n, b, i: {'r2_s_cl_sl': 25700}), 'bound_s_cl_sl<=cl_sl@M'),
                     ('s_cl_nul', M(lambda n, b, i: {'r2_s_cl_nul': 1700}), 'bound_s_cl_nul<=cl_nul@M'),
                     ('s_mx_ns', M(lambda n, b, i: {'r2_s_mx_ns': 110000}), 'bound_s_mx_ns<=mx_ns@M'),
                     ('s_mx_sl', M(lambda n, b, i: {'r2_s_mx_sl': 2100}), 'bound_s_mx_sl<=mx_sl@M'),
                     ('s_ot_ns', M(lambda n, b, i: {'r2_s_ot_ns': 1800000}), 'bound_s_ot_ns<=ot_ns@M'),
                     ('s_ot_sl', M(lambda n, b, i: {'r2_s_ot_sl': 18900}), 'bound_s_ot_sl<=ot_sl@M')):
    case('bound_r2_' + nm, dict(OK, **{V2: 'NOT_EVALUABLE', 'ne2_has': [flag]}), x=fn)
case('bound_r2_tick_edge', dict(OK, **{'ne2_not': ['bound_tick<=cl@M']}),
     x=M(lambda n, b, i: {'r2_cl_tick': 4400 + (1390 if (b == 1 and i == 40) else 0)}))
case('bound_r2_tick_over', dict(OK, **{'ne2_has': ['bound_tick<=cl@M']}),
     x=M(lambda n, b, i: {'r2_cl_tick': 4400 + (1391 if (b == 1 and i == 40) else 0)}))
case('bound_r2_equal_ok', dict(OK, **{'R2__not_evaluable': []}),
     x=M(lambda n, b, i: {'r2_cl_tick': 4400, 'r2_cl_meta': 4400, 'r2_mx_eq': 2000, 'r2_sl_hit': 29200,
                          'r2_sl_eq': 29200}))
case('bound_r2_window_only', dict(OK, **{'R2__not_evaluable': []}),
     x=M(lambda n, b, i: {'r2_cl_tick': 10 ** 7, 'r2_cl_lod': 10 ** 7} if i in (9, 89) else {}))
case('bound_r2_draws_excluded', dict(OK, **{'R2__not_evaluable': []}),
     main=M(lambda n, b, i: {'draws': 3000} if (b == 2 and i == 50) else {}),
     x=M(lambda n, b, i: {'r2_cl_tick': 10 ** 7} if (b == 2 and i == 50) else {}))
# ------------------------------------------------------------------ R1 arming per estimator row (r1.md F1)
for fld in ('r1_hn', 'r1_mn', 'r1_hit_t', 'r1_mp'):
    case('armed_row_' + fld, dict(OK, **{V1: 'NOT_EVALUABLE', 'ne1_has': ['armed_' + fld]}),
         x=P(lambda n, b, i, f=fld: {f: 0} if (b == 3 and i == 50) else {}))
case('armed_row_pos9_89', dict(OK, **{'ne1_not': ['armed_r1_mp', 'armed_r1_hit_t']}),
     x=P(lambda n, b, i: {'r1_mp': 0, 'r1_hit_t': 0} if i in (9, 89) else {}))
case('armed_row_low_draws', dict(OK, **{'ne1_not': ['armed_r1_mp']}),
     main=P(lambda n, b, i: {'draws': 3000} if (b == 3 and i == 50) else {}),
     x=P(lambda n, b, i: {'r1_mp': 0} if (b == 3 and i == 50) else {}))
case('armed_row_negative', dict(OK, **{'ne1_has': ['armed_r1_mp']}),
     x=P(lambda n, b, i: {'r1_mp': -1} if (b == 3 and i == 50) else {}))
case('armed_row_one', dict(OK, **{'ne1_not': ['armed_r1_mp', 'armed_r1_hn']}),
     x=P(lambda n, b, i: {'r1_mp': 1, 'r1_hn': 1} if (b == 3 and i == 50) else {}))
case('armed_row_reset_block', dict(OK, **{'ne1_not': ['armed_r1_mp'], 'reset_blocks': [3]}),
     x=P(lambda n, b, i: {'r1_mp': 0, 'r1_reset': 1} if (b == 3 and i == 50) else {}))

# ------------------------------------------------------------------ fixtures added for mutants that survived round 1
case('r1_argmax_E_decides', dict(OK, **{'R1__terms__argmax': 'd16', C1: 792.0, T1 + 'w8__C': 790.0,
                                        T1 + 'w8__C_noE': 778.0}), x=P(lambda n, b, i: {'r1_w8_rbns': 419924}))
case('r2_tstar_scaling', dict(OK, **{T2 + 'T_star': 1137500 * 27200 / 24000 / 1000}),
     x=M(lambda n, b, i: {'r2_s_cl_nul': 0}))
EXT2 = {'r2_mx_eq': 120000, 'r2_mx_sl': 120000, 'bl_res_n': 166000, 'r2_sl_hit': 147200, 'r2_sl_eq': 150000}
case('pk_closed_perslot', dict(OK, **{VR: 'CLOSED', V2: 'CLOSED', 'R__upper': 499.9, 'R2__not_evaluable': [],
                                      'lines_has': ['CONSEQUENCE: R ' + mod.CONSEQUENCE['CLOSED']
                                                    + ' Per-slot variant unmeasured (C_ext 531.1 us >= 500.0)',
                                                    'CONSEQUENCE: R2 ' + mod.CONSEQUENCE['CLOSED']
                                                    + ' Per-slot variant unmeasured (C_ext 531.1 us >= 500.0)']}),
     x=lambda n, b, arm, i: R1_100 if arm == 0 else dict(S0, **EXT2, r2_cl_ns=707900, r2_ot_ns=3200500 - 807900))
consts = [(mod.GATES_FILE, 'C:/kyty/s120/gates_base.txt'), (mod.ROOT, 'C:/kyty/s120'), (mod.TAG, 'cen120'),
          (mod.TAGS, ('cen120', 'cen120r')), (mod.PRED_PATH, 'C:/kyty/s120/pred/01_cen120.md'),
          (mod.INSTALLED, os.path.expanduser('~') + '/OneDrive/Desktop/ps5 em/kyty_emulator.exe'),
          (mod.GATES_SHA, '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'), (mod.BUILD_SHA, BUILD)]
RESULTS.append(('constants', all(g == w for g, w in consts), ['%r != %r' % (g, w) for g, w in consts if g != w]))
# ------------------------------------------------------------------ summary_of directly (orderings e2e cannot reach)
for nm, args, want in (
        ('sumf_na_over_open', (False, False, False, 'OPEN', 'OPEN', 'OPEN'),
         {'verdict': 'NOT_ADMITTED', 'carrying': 'R1+R2', 'open_members': ['R1', 'R2']}),
        ('sumf_na_over_pkg_open', (False, False, False, 'CLOSED', 'NOT_OPENED', 'OPEN'),
         {'verdict': 'NOT_ADMITTED', 'carrying': 'R1+R2 (together)', 'open_members': []}),
        ('sumf_fail_over_na', (False, False, True, 'OPEN', 'FAIL', 'FAIL'),
         {'verdict': 'FAIL', 'carrying': 'R1', 'open_members': ['R1']}),
        ('sumf_fail_r1_over_na', (False, True, False, 'FAIL', 'OPEN', 'FAIL'),
         {'verdict': 'FAIL', 'carrying': 'R2', 'open_members': ['R2']}),
        ('sumf_open_member_over_pkg', (True, False, False, 'CLOSED', 'OPEN', 'NOT_EVALUABLE'),
         {'verdict': 'OPEN', 'carrying': 'R2', 'open_members': ['R2']}),
        ('sumf_pkg_open_only', (True, False, False, 'NOT_OPENED', 'CLOSED', 'OPEN'),
         {'verdict': 'OPEN', 'carrying': 'R1+R2 (together)', 'open_members': []}),
        ('sumf_pkg_verdict', (True, False, False, 'CLOSED', 'NOT_OPENED', 'NOT_OPENED'),
         {'verdict': 'NOT_OPENED', 'carrying': '', 'open_members': []}),
        ('sumf_pkg_ne', (True, False, False, 'NOT_EVALUABLE', 'CLOSED', 'NOT_EVALUABLE'),
         {'verdict': 'NOT_EVALUABLE', 'carrying': '', 'open_members': []})):
    got = mod.summary_of(*args)
    RESULTS.append((nm, got == want, [] if got == want else ['%r want %r' % (got, want)]))

# ------------------------------------------------------------------ --real: the unsealed smoke, --draft
if '--real' in sys.argv:
    res = mod.evaluate('C:/kyty/s120', 'smk120', draft=True, installed_sha=BUILD)
    t1, t2 = res['R1']['terms'], res['R2']['terms']
    want = [(res['verdict'], 'ADMITTED'), (res['pairs'], 21), (res['est_frames']['P'], 1658),
            (res['est_frames']['M'], 1641), (res['R1']['not_evaluable'], []), (res['R2']['not_evaluable'], []),
            (res['R1']['verdict'], 'OPEN'), (res['R2']['verdict'], 'NOT_OPENED'), (res['R']['verdict'], 'OPEN'),
            (t1['argmax'], 'w8'), (round(t1['tables']['w4']['C'], 1), 473.8), (round(t1['tables']['w8']['C'], 1), 615.9),
            (round(t1['tables']['d16']['C'], 1), 538.4), (round(res['R1']['two_se'], 1), 12.6),
            (round(t2['C_up'], 1), 1088.0), (round(t2['C_pt'], 1), 444.1), (round(t2['C_lo'], 1), -36.5),
            (round(res['R2']['two_se'], 1), 14.9), (round(res['R']['point'], 1), 1060.0),
            (round(res['R']['upper'], 1), 1703.9), (round(res['R']['two_se'], 1), 21.3),
            (sum(res['raw'][k] for k in ('r1_w4_bad', 'r1_w8_bad', 'r1_d16_bad', 'r2_bad', 'r2_bad_key')), 0),
            (res['lines'], {'r1_mismatch': 0, 'r2_mismatch': 0, 'r2_diverge': 0})]
    # the lead's draft (smoke120.py) grouped rows by the blk label; the rows before the schedule carry blk=0, so its
    # "positions 10..88" of block 0 were frames 12..90 (all draws <= 3000): its P window lacks block 0 (1579 frames).
    # Recomputed here with block 0 dropped from P, the formulas coincide with runs120/smk120_smoke.txt to 0.1 us.
    parsed = mod.parse_log('C:/kyty/s120/log_smk120.txt')
    _, blocks = mod.arms_ok(parsed['gate_arms'])
    done, _ = mod.select(parsed, blocks)
    est_p = [r for b, d in sorted(done.items()) if d['arm'] == 0 and b != 0 for r in d['est']]
    est_m = [r for b, d in sorted(done.items()) if d['arm'] == 1 for r in d['est']]
    d1 = mod.r1_terms(mod.ksum(est_p, mod.X_FIELDS + mod.DRAW_FIELDS), len(est_p))
    d2 = mod.r2_terms(mod.ksum(est_m, mod.R2_KEYS), len(est_m))
    draft = {'w4': (991.9, 506.9, 483.3, 61.7, 49.5, 22.7, 19.8, 473.9, 451.2),
             'w8': (1196.6, 509.9, 586.6, 28.0, 60.0, 27.4, 25.8, 620.2, 592.8),
             'd16': (929.7, 525.4, 470.2, 0.0, 47.3, 21.3, 0.0, 538.7, 517.4)}
    want += [(len(est_p), 1579), (len(est_m), 1641), (round(d1['t_hit'], 1), 19.7), (round(d1['t_miss'], 1), 509.9),
             (round(d1['t_fast'], 1), 9.9), (round(d1['t_ham'], 1), 50.4)]
    for t, vals in draft.items():
        e = d1['tables'][t]
        want += [(tuple(round(e[k], 1) for k in ('W', 't_T', 'A', 'L', 'R', 'E', 'P', 'C', 'C_noE')), vals)]
    want += [(round(d2['S'], 1), 31869.8), (round(d2['Z'], 1), 880.4), (round(d2['L'], 1), 463.6),
             (round(d2['z_bar'], 2), 8.85), (round(d2['w_rep'], 2), 49.91), (round(d2['w_oth'], 2), 14.69),
             (round(d2['T_star'], 1), 1395.9), (round(d2['p_c'], 1), 42.6), (round(d2['W'], 1), 196.3),
             (round(d2['ST'], 1), 13.4), (round(d2['C_up'], 1), 1088.0), (round(d2['C_pt'], 1), 444.1),
             (round(d2['C_lo'], 1), -36.5), (round(d1['C_R1'] + d2['C_pt'], 1), 1064.3),
             (round(d1['C_R1'] + d2['C_up'], 1), 1708.2),
             (round(mod.mean([r['dt_us'] for r in est_p]) - mod.mean([r['dt_us'] for r in est_m]), 1), 2783.8),
             (round(mod.mean([r['cpu_gpu_us'] for r in est_p]) - mod.mean([r['cpu_gpu_us'] for r in est_m]), 1), 2695.3),
             (round(mod.mean([r['bda_scan'] for r in est_p]), 1), 67.8), (round(mod.mean([r['bda_scan'] for r in est_m]), 1), 60.3),
             (round(mod.mean([r['r1_hn'] for r in est_p]), 1), 45027.8), (round(mod.mean([r['tex_hits'] for r in est_p]), 1), 45027.6)]
    want += [(round(t2['C_up_B849'], 1), 973.7), (round(t2['C_pt_traced'], 1), 521.7), (round(t2['K_rp'], 1), 26.6),
             (t2['K_rp_ok'], True), (round(t2['C_rp'], 1), 275.4), (round(t2['C_ext'], 1), 446.3),
             (round(t2['first_touch_ns'], 2), 4.02), (res['bda_scan']['P_regime'], 'NEW'), (res['bda_scan']['M_regime'], 'NEW'),
             (round(res['price']['dt_us']['pair_mean'], 1), 2819.5), (round(res['price']['cpu_gpu_us']['pair_mean'], 1), 2734.0),
             (res['checks']['installed_now'], True), (res['R1']['verdict'] + res['R2']['verdict'], 'OPENNOT_OPENED'),
             (res['summary'], {'verdict': 'OPEN', 'carrying': 'R1', 'open_members': ['R1']}),
             (mod.format_report(res)[-1].endswith(' Open: R1.'), True)]
    bad = ['%r want %r' % (g, w) for g, w in want if g != w]
    RESULTS.append(('real_smk120', not bad, bad))

fails = [r for r in RESULTS if not r[1]]
for name, ok, why in RESULTS:
    print('%-34s %s %s' % (name, 'ok' if ok else 'FAIL', '; '.join(why)))
print('%d fixtures, %d failed' % (len(RESULTS), len(fails)))
print('ALL OK' if not fails else 'FIXTURE FAILURES')
sys.exit(0 if not fails else 1)
