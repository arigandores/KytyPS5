"""Session 120: fixtures for spc120.py (spcen members A, B and package SP; design120.md s4-s6, spcen.md s11 as amended,
spcen_review.md RC1-RC6, ROADMAP s120 items 2, 4, 5).  A synthetic P|M ABBA log (LF), ADMITTED, every admission check
failing alone, both sides of every edge (500 us, 2SE, 10^-4 race, SKEW_COUNT, DRAW_ID tolerances, EMIT_TOL_US,
TR_ROUND_NS, draws > 3000, window positions 9/10/88/89, IDLE, MIN_PAIRS), every formula term, the unit traps, the zero
denominators, arm-by-text, the correctness rules over all rows, the controls and the report.
    python test_spc120.py <spc120.py> [--real]
--real also scores C:/kyty/s120/log_smk120.txt in --draft mode and checks the draft numbers of runs120/smk120_smoke.txt.
Sizes and constants come from this suite, never from the scorer.
"""
import importlib.util
import json
import math
import shutil
import statistics
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s120/fx_spc120')
NL = chr(10)
spec = importlib.util.spec_from_file_location('spc120', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)

TAG = 'cen120'
BUILD = '15cdbfc6e2c9d19a9aa803beaa1dff670d3403b54b74b56f4911c456de4ca661'
PERIOD = 90
START = 1800
BLOCKS = 8
PAIRS = BLOCKS // 2
ABBA = (0, 1, 1, 0)
PRED = 'C:\\kyty\\s120\\pred\\01_cen120.md'
FAKE_SHA = 'ab' * 32
FAKE_BYTES = 4321
FAKE = (FAKE_SHA, FAKE_BYTES)
GATES_TEXT = ' '.join(Path('C:/kyty/s120/gates_base.txt').read_text(encoding='utf-8').split())
TEXT = ('r1cen=2 r2cen=2 spcen=1 bindlap=1 pathlap=1 mutsite=1',
        'r1cen=0 r2cen=1 spcen=0 bindlap=1 pathlap=1 mutsite=1')
VALUES = tuple(dict(p.split('=') for p in t.split()) for t in TEXT)
ENV_OK = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GATE_FILE': 'C:\\kyty\\s120\\gates.req',
          'KYTY_SAMPLE_GATE': 'C:\\kyty\\s120\\sample.req', 'KYTY_QUEUE_TRACE': '1',
          'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden',
          'KYTY_GATE_SCHEDULE': '90+1800:' + TEXT[0] + '|' + TEXT[1], 'KYTY_GATE_SCHEDULE_ABBA': '1',
          'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'VK_SDK_PATH': 'C:\\VulkanSDK\\1.4.357.0'}
PIN = 'GpuClockPin: mode 1 - the guest GPU clock ignores the pacer speed (KYTY_GPU_CLOCK_PIN)'
CENSUS = 'SpCensus: mode 1 rt_targets=9 tr_slots=32'
SKIP = 'AsyncPipelines: skipped draw 0x1234'
RT_R = ('sp_rt_x_memo', 'sp_rt_x_cfg', 'sp_rt_x_dclr', 'sp_rt_x_meta', 'sp_rt_x_ids', 'sp_rt_x_live', 'sp_rt_x_ser',
        'sp_rt_x_bound', 'sp_rt_x_dsmp', 'sp_rt_x_pass')
TR_R = ('sp_tr_x_big', 'sp_tr_x_memo', 'sp_tr_x_meta', 'sp_tr_x_shape', 'sp_tr_x_ser', 'sp_tr_x_flags')
SP_ZERO = dict({k: 0 for k in RT_R + TR_R}, sp_rt_n=0, sp_rt_would=0, sp_rt_wg=0, sp_rt_tgt=0, pl_em_spchk_ns=0,
               sp_rt_chkh_ns=0, pl_em_rt_hit_ns=0, pl_em_rt_hitg_ns=0, pl_em_sppost_ns=0, sp_rt_rep_ns=0,
               sp_rt_rep_att=0, sp_rt_rep_kpx=0, sp_rt_rec=0, sp_rt_rec_ns=0, sp_rt_bad=0, sp_rt_race=0, sp_rt_rst=0,
               sp_rt_nt=0, sp_tr_n=0, sp_tr_slots=0, sp_tr_would=0, sp_tr_wg=0, sp_tr_wslots=0, sp_tr_loop_ns=0,
               bl_tr_hit_ns=0, bl_tr_hitg_ns=0, sp_tr_chk_ns=0, sp_tr_chkh_ns=0, sp_tr_post_ns=0, sp_tr_rep_ns=0,
               sp_tr_rec=0, sp_tr_rec_ns=0, sp_tr_bad=0, sp_tr_dcc=0)
X_P = dict(dict({k: 100 for k in RT_R}, **{k: 250 for k in TR_R}), sp_ser_n=400, sp_ser_val=1, sp_rt_n=5000,
           sp_rt_would=4000, sp_rt_wg=3900, sp_rt_tgt=14000, pl_em_spchk_ns=400000, sp_rt_chkh_ns=330000,
           pl_em_rt_hit_ns=1000000, pl_em_rt_hitg_ns=950000, pl_em_sppost_ns=400000, sp_rt_rep_ns=80000,
           sp_rt_rep_att=12000, sp_rt_rep_kpx=24000000, sp_rt_rec=4600, sp_rt_rec_ns=100000, sp_rt_bad=0, sp_rt_race=0,
           sp_rt_rst=3, sp_rt_nt=0, sp_tr_n=9000, sp_tr_slots=45000, sp_tr_would=7500, sp_tr_wg=7400,
           sp_tr_wslots=38000, sp_tr_loop_ns=900000, bl_tr_hit_ns=400000, bl_tr_hitg_ns=390000, sp_tr_chk_ns=200000,
           sp_tr_chkh_ns=150000, sp_tr_post_ns=250000, sp_tr_rep_ns=50000, sp_tr_rec=1500, sp_tr_rec_ns=100000,
           sp_tr_bad=0, sp_tr_dcc=0,
           pl_em_vtx_ns=1400000, pl_em_rt_ns=1400000, pl_em_pipe_ns=700000, pl_em_com_ns=2300000,
           pl_em_rec_ns=1200000, pl_em_rest_ns=50000, pl_em_n=5000, mh_emit_us=8000, bl_tr_us=1000, r2_nul_ns=7000,
           r2_nul_n=700, rt_att=16000, rt_kpx=30000000, rt_fast_ok=17000, rt_fast_no=500)
X_M = dict(X_P, **SP_ZERO)
X_M.update(pl_em_rt_ns=1600000, mh_emit_us=7400, bl_tr_us=1100, r2_nul_ns=3500)
X_ARM = (X_P, X_M)
MAIN_DEF = (dict(dt_us=33000, cpu_gpu_us=32000, draws=5000), dict(dt_us=31000, cpu_gpu_us=30000, draws=5000))
DRAW_DEF = dict(bda_scan=50)
SP_NAMES = tuple(k for k in X_P if k.startswith('sp_') or k in ('pl_em_spchk_ns', 'pl_em_sppost_ns', 'pl_em_rt_hit_ns',
                                                                 'pl_em_rt_hitg_ns', 'bl_tr_hit_ns', 'bl_tr_hitg_ns'))
P_BLOCKS = [b for b in range(BLOCKS) if ABBA[b % 4] == 0]
RESULTS = []


def make(name, blocks=BLOCKS, main=None, x=None, draw=None, env=None, gates=GATES_TEXT, pins=(PIN,), census=(CENSUS,),
         meta=None, gate_arm=None, gate_lines=None, drop=(), dup=(), extra_log=(), extra_at=None, stdout_lines=(),
         pre=5, order=ABBA, post=0, strip=()):
    """A fixture directory.  main/x/draw: callables (n, block, arm, pos) -> overrides (pos None before START); frames
    before START carry arm=0 blk=0 and the census-off values, as the real log does."""
    root = BASE / name
    root.mkdir(parents=True)
    lines = list(pins) + list(census)
    prev = None
    for n in range(START - pre + 1, START + PERIOD * blocks + post + 1):
        if n > START and (n - START - 1) % PERIOD == 0:
            b = (n - START - 1) // PERIOD
            arm = order[b % 4]
            if gate_arm is not None:
                lines.extend(gate_arm(b, arm))
            else:
                lines.append('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                             % (arm, b, START + PERIOD * b, TEXT[arm]))
            if gate_lines is not None:
                lines.extend(gate_lines(b, arm))
            elif prev != arm:
                for k, v in VALUES[arm].items():
                    if prev is None or VALUES[prev][k] != v:
                        lines.append('Gate: %s=%s frame=%d' % (k, v, START + PERIOD * b))
            prev = arm
        if n <= START:
            b, pos, arm = 0, None, 0
            mv, xv = dict(MAIN_DEF[1], arm=0, blk=0), dict(X_M)
        else:
            b, pos = (n - START - 1) // PERIOD, (n - START - 1) % PERIOD
            arm = order[b % 4]
            mv, xv = dict(MAIN_DEF[arm], arm=arm, blk=b), dict(X_ARM[arm])
        dv = dict(DRAW_DEF)
        if main:
            mv.update(main(n, b, arm, pos))
        if draw:
            dv.update(draw(n, b, arm, pos))
        if x:
            xv.update(x(n, b, arm, pos))
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
        if extra_at and n in extra_at:
            lines.extend(extra_at[n])
    lines.extend(extra_log)
    (root / ('log_%s.txt' % TAG)).write_bytes((NL.join(lines) + NL).encode('utf-8'))
    (root / ('stdout_%s.txt' % TAG)).write_bytes((NL.join(stdout_lines) + NL).encode('utf-8'))
    m = dict(tag=TAG, binary_sha256=BUILD, env=dict(ENV_OK if env is None else env), hold_s=300, gates=gates,
             attempts=[dict(label='a1', outcome='ok', hold_exit=None, stable_frame=500)],
             prereg=dict(path=PRED, sha256=FAKE_SHA, bytes=FAKE_BYTES), pre_run=dict(gpu_util_median=2))
    if meta:
        m.update(meta)
    (root / ('%s.json' % TAG)).write_text(json.dumps(m), encoding='utf-8')
    return root


def resolve(res, key):
    if key == 'failed':
        return sorted(k for k, v in res['checks'].items() if v is False)
    if key in ('common_failed', 'a_failed', 'b_failed'):
        group = {'common_failed': 'common', 'a_failed': 'a_controls', 'b_failed': 'b_controls'}[key]
        return sorted(k for k, v in res[group].items() if not v)
    if key in ('A', 'B', 'SP'):
        return res['members'][key]['verdict']
    if key[:2] in ('A_', 'B_') or key.startswith('SP_'):
        name, field = key.split('_', 1)
        return res['members'][name][{'point': 'point', 'upper': 'upper', 'se2': 'se2_upper',
                                     'se2pt': 'se2_point'}[field]]
    if key.startswith('t:'):
        return res['terms'].get(key[2:])
    if key.startswith('rep'):
        arm, field = key[3], key[5:]
        return res['report'][int(arm)][field]
    if key == 'is_draft':
        return res['draft']
    if key == 'consequence_head':
        return res['consequence'].split(' ')[0]
    if key in ('mconsfull_A', 'mconsfull_B'):
        return res['member_consequence'][key[-1]]
    if key in ('mcons_A', 'mcons_B'):
        return res['member_consequence'][key[-1]].split(' ')[0]
    return res.get(key)


def compare(res, expect):
    bad = []
    for key, want in expect.items():
        got = resolve(res, key)
        if isinstance(want, float):
            if not isinstance(got, (int, float)) or isinstance(got, bool) or math.isnan(got) \
                    or abs(got - want) > 1e-6 * max(1.0, abs(want)):
                bad.append('%s=%r want %r' % (key, got, want))
        elif got != want:
            bad.append('%s=%r want %r' % (key, got, want))
    return bad


def run(name, root, installed=BUILD, draft=False, pred_want=FAKE, pred_now=FAKE, min_pairs=PAIRS, gates_file=None,
        **expect):
    kw = {} if gates_file is None else {'gates_file': gates_file}
    if pred_want is not None:
        kw['pred_want'] = pred_want
    if pred_now is not None:
        kw['pred_now'] = pred_now
    res = mod.evaluate(str(root), TAG, installed_sha=installed, draft=draft, min_pairs=min_pairs, **kw)
    bad = compare(res, expect)
    RESULTS.append((name, not bad, bad))
    return res


def case(name, expect, **kw):
    runner = {k: kw.pop(k) for k in ('installed', 'draft', 'pred_want', 'pred_now', 'min_pairs', 'gates_file')
              if k in kw}
    return run(name, make(name, **kw), **runner, **expect)


def P(f):
    return lambda n, b, arm, pos: f(n, b, pos) if (arm == 0 and pos is not None) else {}


def M(f):
    return lambda n, b, arm, pos: f(n, b, pos) if (arm == 1 and pos is not None) else {}


def W(pos):
    return pos is not None and 10 <= pos <= 88


OK = dict(verdict='ADMITTED', failed=[], common_failed=[], a_failed=[], b_failed=[])
NE_ALL = dict(A='NOT_EVALUABLE', B='NOT_EVALUABLE', SP='NOT_EVALUABLE')
# base numbers (per frame, us): N_A = 1000 - 400 - 80 - 100; N_B = 400 - 200 - 50 - 100; zbar = 7000/700 = 10 ns;
# Z_A = 10*(2*5000 + 4600)/1000; Z_B = 10*2*9000/1000; D_A = 1.6e6 - 1.4e6; D_B = 1000*(1100 - 1000);
# D_B' = D_B + 10*9000; T_A = D_A*(1.0/1.4)/1000; T_B = D_B'*(0.4/0.9)/1000
T_A = 200000 * (1000000 / 1400000) / 1000
T_B = 190000 * (400000 / 900000) / 1000
BASE_T = {'t:G_A': 1000.0, 't:G_B': 400.0, 't:N_A': 420.0, 't:N_B': 50.0, 't:N': 470.0, 't:Z_A': 146.0,
          't:Z_B': 180.0, 't:Z': 326.0, 't:D_A_ns': 200000.0, 't:D_B_ns': 100000.0, 't:D_Bp_ns': 190000.0,
          't:T_A': T_A, 't:T_B': T_B, 't:N_A_up': 566.0 + T_A, 't:N_B_up': 230.0 + T_B,
          't:N_up': 796.0 + T_A + T_B, 't:G_A_up': 1000.0 + T_A, 't:G_B_up': 400.0 + T_B, 't:G_A_g': 950.0,
          't:G_B_g': 390.0, 't:N_A_g': 950.0 - 400.0 - 80.0 * 3900 / 4000 - 100.0,
          't:N_B_g': 390.0 - 200.0 - 50.0 * 7400 / 7500 - 100.0, 't:price_dt_us': 2000.0,
          't:price_cpu_gpu_us': 2000.0, 't:nfp': 4 * 79, 't:nfm': 4 * 79, 'zbar_ns': 10.0,
          'A_point': 420.0, 'A_upper': 566.0 + T_A, 'A_se2': 0.0, 'B_point': 50.0, 'B_upper': 230.0 + T_B,
          'B_se2': 0.0, 'SP_point': 470.0, 'SP_upper': 796.0 + T_A + T_B, 'SP_se2': 0.0, 'SP_se2pt': 0.0}
BASE_V = dict(A='NOT_OPENED', B='CLOSED', SP='NOT_OPENED')

# ------------------------------------------------------------------ the admitted base: every term
res_ok = case('ok', dict(OK, **BASE_T, **BASE_V, consequence_head='NOT_OPENED', carrying=[], fail_a=False,
                         fail_b=False, **{'rep0:bda_regime': 'NEW', 'rep1:bda_regime': 'NEW', 'rep0:frames': 316,
                                          'rep1:frames': 316, 'rep0:dt_us': 33000.0, 'rep1:dt_us': 31000.0}))
text = NL.join(mod.format_report(res_ok))
want_lines = ['VERDICT: ADMITTED', 'MEMBER A: NOT_OPENED point=420.0 upper=708.9 2se=0.0',
              'MEMBER B: CLOSED point=50.0 upper=314.4 2se=0.0', 'PACKAGE SP: NOT_OPENED point=470.0 upper=1023.3 2se=0.0',
              'CONSEQUENCE: ' + mod.CONSEQUENCES['NOT_OPENED']]
got_lines = [ln for ln in text.split(NL) if ln.split(' ')[0] in ('VERDICT:', 'MEMBER', 'PACKAGE', 'CONSEQUENCE:')]
RESULTS.append(('ok_lines', got_lines == want_lines and 'DRAFT' not in text, [] if got_lines == want_lines else
                ['%r' % got_lines]))
RESULTS.append(('ok_pairs', res_ok['pairs'] == [[0, 1], [3, 2], [4, 5], [7, 6]], ['%r' % res_ok['pairs']]))
want_member = ['CONSEQUENCE A: ' + mod.CONSEQUENCES['NOT_OPENED'], 'CONSEQUENCE B: ' + mod.CONSEQUENCES['CLOSED']]
got_member = [ln for ln in text.split(NL) if ln.startswith('CONSEQUENCE A:') or ln.startswith('CONSEQUENCE B:')]
RESULTS.append(('ok_member_lines', got_member == want_member, ['%r' % got_member]))
RESULTS.append(('ok_json', 'NaN' not in json.dumps(res_ok), ['NaN in json']))

# ------------------------------------------------------------------ formula terms, one at a time
case('term_rec_a', {'t:N_A': 370.0, 'A_point': 370.0}, x=P(lambda n, b, i: {'sp_rt_rec_ns': 150000}))
case('term_rep_a', {'t:N_A': 400.0, 'A_point': 400.0}, x=P(lambda n, b, i: {'sp_rt_rep_ns': 100000}))
case('term_chk_a', {'t:N_A': 390.0}, x=P(lambda n, b, i: {'pl_em_spchk_ns': 430000, 'mh_emit_us': 8030}))
case('term_rec_b', {'t:N_B': 30.0}, x=P(lambda n, b, i: {'sp_tr_rec_ns': 120000}))
case('term_rep_b', {'t:N_B': 40.0}, x=P(lambda n, b, i: {'sp_tr_rep_ns': 60000}))
case('term_chk_b', {'t:N_B': 20.0}, x=P(lambda n, b, i: {'sp_tr_chk_ns': 230000}))
case('term_hit_b', {'t:N_B': 150.0, 't:G_B': 500.0}, x=P(lambda n, b, i: {'bl_tr_hit_ns': 500000}))
case('term_z_rec', {'t:Z_A': 156.0}, x=P(lambda n, b, i: {'sp_rt_rec': 5600}))
case('term_z_rt_n', {'t:Z_A': 156.0}, x=P(lambda n, b, i: {'sp_rt_n': 5500, 'sp_rt_x_memo': 600, 'pl_em_n': 5500}))
case('term_z_tr_n', {'t:Z_B': 200.0, 't:D_Bp_ns': 200000.0},
     x=P(lambda n, b, i: {'sp_tr_n': 10000, 'sp_tr_x_big': 1250}))
case('term_zbar', {'zbar_ns': 20.0, 't:Z_A': 292.0, 't:Z_B': 360.0, 't:D_Bp_ns': 280000.0},
     x=P(lambda n, b, i: {'r2_nul_ns': 14000}))
case('term_zbar_not_from_m', {'zbar_ns': 10.0, 't:Z_A': 146.0}, x=M(lambda n, b, i: {'r2_nul_ns': 70000}))
case('term_zbar_window_only', {'zbar_ns': 10.0}, x=P(lambda n, b, i: {'r2_nul_ns': 900000} if not W(i) else {}))
case('term_da', {'t:D_A_ns': 300000.0, 't:T_A': 300000 / 1.4 / 1000}, x=M(lambda n, b, i: {'pl_em_rt_ns': 1700000,
                                                                                           'mh_emit_us': 7500}))
case('term_da_ratio', dict(OK, **{'t:T_A': 200000 * (1000000 / 2000000) / 1000, 't:D_A_ns': 200000.0}),
     x=lambda n, b, arm, i: ({'pl_em_rt_ns': 2000000, 'mh_emit_us': 8600} if arm == 0 else
                             {'pl_em_rt_ns': 2200000, 'mh_emit_us': 8000}) if i is not None else {})
case('term_da_clamp', {'t:D_A_ns': -100000.0, 't:T_A': 0.0, 't:N_A_up': 566.0},
     x=M(lambda n, b, i: {'pl_em_rt_ns': 1300000, 'mh_emit_us': 7100}))
case('term_db_units', {'t:D_B_ns': 300000.0, 't:D_Bp_ns': 390000.0, 't:T_B': 390000 * (4 / 9) / 1000},
     x=M(lambda n, b, i: {'bl_tr_us': 1300}))
case('term_dbp_clamp', {'t:D_B_ns': -200000.0, 't:D_Bp_ns': -110000.0, 't:T_B': 0.0, 't:N_B_up': 230.0},
     x=M(lambda n, b, i: {'bl_tr_us': 800}))
case('term_dbp_zero', {'t:D_Bp_ns': 0.0, 't:T_B': 0.0}, x=M(lambda n, b, i: {'bl_tr_us': 910}))
case('term_db_ratio', {'t:T_B': 190000 * (400000 / 1000000) / 1000},
     x=P(lambda n, b, i: {'sp_tr_loop_ns': 1000000, 'bl_tr_us': 1000}))
case('term_global', {'t:N_A_g': 950.0 - 400.0 - 80.0 * 2000 / 4000 - 100.0, 't:G_A_g': 950.0,
                     't:N_B_g': 380.0 - 200.0 - 50.0 * 3750 / 7500 - 100.0, 't:G_B_g': 380.0},
     x=P(lambda n, b, i: {'sp_rt_wg': 2000, 'sp_tr_wg': 3750, 'bl_tr_hitg_ns': 380000}))
case('term_global_zero_would', {'t:N_A_g': None, 'A': 'NOT_EVALUABLE', 'a_failed': ['rt_part']},
     x=P(lambda n, b, i: {'sp_rt_would': 0, 'sp_rt_wg': 0}))
case('term_price', {'t:price_dt_us': 2500.0, 't:price_cpu_gpu_us': 1000.0},
     main=lambda n, b, arm, i: ({'dt_us': 33500, 'cpu_gpu_us': 31000} if arm == 0 else {}) if i is not None else {})
case('term_price_window', {'t:price_dt_us': 2000.0},
     main=lambda n, b, arm, i: {'dt_us': 99999} if (i is not None and not W(i)) else {})
# which arm's estimator frame count divides each term: the two counts differ (10 window frames a block at draws 2000)
BASE_NF = {k: v for k, v in BASE_T.items() if k not in ('t:nfp', 't:nfm')}
LOW10 = lambda n, b, i: {'draws': 2000} if 10 <= i <= 19 else {}
case('term_div_m', dict(OK, **BASE_NF, **BASE_V, **{'t:nfm': 276, 't:nfp': 316}), main=M(LOW10))
case('term_div_p', dict(OK, **BASE_NF, **BASE_V, **{'t:nfp': 276, 't:nfm': 316}), main=P(LOW10))
# a P frame whose census counters all read 0 stays P (the arm is the GateArm text): nfp stays 316
case('arm_by_text_frame', {'t:nfp': 316, 't:N_A': 315 * 420.0 / 316, 't:D_A_ns': 200000.0, 'verdict': 'ADMITTED',
                           'a_failed': [], 'b_failed': [], 'common_failed': []},
     x=P(lambda n, b, i: dict(SP_ZERO, pl_em_n=0, mh_emit_us=7200) if (b == 3 and i == 40) else {}))
case('arm_by_text_block', {'t:nfp': 316, 't:N_A': 3 * 420.0 / 4, 't:nfm': 316, 't:D_A_ns': 200000.0,
                           'pairs': [[0, 1], [3, 2], [4, 5], [7, 6]]},
     x=P(lambda n, b, i: dict(SP_ZERO, pl_em_n=0, mh_emit_us=7200) if b == 0 else {}))

# ------------------------------------------------------------------ window and estimator frames
HUGE = dict(pl_em_rt_hit_ns=10 ** 9, pl_em_spchk_ns=0, sp_rt_rep_ns=0, sp_rt_rec_ns=0, bl_tr_hit_ns=10 ** 9,
            sp_rt_n=0, sp_tr_n=0, pl_em_rt_ns=1, bl_tr_us=1, r2_nul_ns=10 ** 9, dt_us=1)
case('window_pos9_89_P', dict(OK, **BASE_T, **BASE_V), x=P(lambda n, b, i: HUGE if i in (9, 89) else {}))
case('window_pos0_M', dict(OK, **BASE_T), x=M(lambda n, b, i: {'pl_em_rt_ns': 10 ** 9, 'bl_tr_us': 10 ** 6}
                                               if i in (0, 9, 89) else {}))
case('window_pos10', {'t:N_A': 424.0}, x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1316000} if i == 10 else {}))
case('window_pos88', {'t:N_A': 424.0}, x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1316000} if i == 88 else {}))
case('window_pos10_M', {'t:D_A_ns': 204000.0}, x=M(lambda n, b, i: {'pl_em_rt_ns': 1916000, 'mh_emit_us': 7716}
                                                 if i == 10 else {}))
case('draws_3000_out', {'t:N_A': 420.0, 't:nfp': 312},
     main=P(lambda n, b, i: {'draws': 3000} if i == 40 else {}),
     x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1316000} if i == 40 else {}))
case('draws_3001_in', {'t:N_A': 424.0, 't:nfp': 316},
     main=P(lambda n, b, i: {'draws': 3001} if i == 40 else {}),
     x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1316000} if i == 40 else {}))
case('draws_all_low_ne', dict(NE_ALL, verdict='NOT_ADMITTED', failed=['pairs'],
                              common_failed=['admitted', 'frames', 'pairs2', 'zbar']),
     main=P(lambda n, b, i: {'draws': 2000}))
# the controls read every WINDOW frame (design120 s4 "WINDOW sums", RC6 "window frames"), whatever its draws; only
# the formulas read the draws > 3000 subset
case('ctl_window_lowdraw_part', dict(A='NOT_EVALUABLE', SP='NOT_EVALUABLE', a_failed=['rt_part']),
     main=P(lambda n, b, i: {'draws': 2000} if (b == 4 and i == 40) else {}),
     x=P(lambda n, b, i: {'sp_rt_x_memo': 109} if (b == 4 and i == 40) else {}))
case('ctl_window_lowdraw_mzero', dict(NE_ALL, common_failed=['m_zeros']),
     main=M(lambda n, b, i: {'draws': 2000} if (b == 2 and i == 40) else {}),
     x=M(lambda n, b, i: {'sp_tr_n': 1} if (b == 2 and i == 40) else {}))
# the nesting edge tolerance reads the window's own edge lines (position 10 here has draws <= 3000)
case('ctl_window_edge_line', dict(OK),
     main=P(lambda n, b, i: {'draws': 2000} if (b == 3 and i == 10) else {}),
     x=P(lambda n, b, i: ({'bl_tr_hit_ns': 800000, 'sp_tr_loop_ns': 800000} if i == 10 else
                          {'sp_tr_loop_ns': 400000 - 1000000} if i == 40 else {'sp_tr_loop_ns': 400000})
         if b == 3 else {}))
# the multi-unit tolerance is the subset's value on BOTH edge lines: small on position 10 (100 000), large on 88
# (800 000); the block's excess of bl_tr_hit_ns over sp_tr_loop_ns is 700 000 <= 900 000 (2 * the first line = 200 000)
case('nest_edge_both_lines', dict(OK),
     x=P(lambda n, b, i: (dict({'sp_tr_loop_ns': 400000},
                               **({'bl_tr_hit_ns': 100000, 'bl_tr_hitg_ns': 90000} if i == 10 else
                                  {'bl_tr_hit_ns': 800000} if i == 88 else
                                  {'sp_tr_loop_ns': -200000} if i == 40 else {})) if b == 3 else {})))
# the draw identity total reads every P WINDOW frame, not only the estimator frames: -64 on a draws-2000 row of each
# of 6 P blocks = -384 over the window (per block 64 holds; the estimator rows carry 0)
case('draw_id_total_window_rows', dict(A='NOT_EVALUABLE', a_failed=['draw_id']), blocks=12,
     main=P(lambda n, b, i: {'draws': 2000} if i == 40 else {}),
     x=P(lambda n, b, i: {'pl_em_n': 5000 - 64} if i == 40 else {}))
# bl_tr_alive and a_den guard the formula denominators: they read the paired estimator frames, not the window
case('bl_tr_alive_estimator_m', dict(B='NOT_EVALUABLE', b_failed=['bl_tr_alive']),
     main=M(lambda n, b, i: {'draws': 2000} if i == 40 else {}),
     x=M(lambda n, b, i: {} if i == 40 else {'bl_tr_us': 0}))
case('bl_tr_alive_estimator_p', dict(B='NOT_EVALUABLE', b_failed=['bl_tr_alive', 'nest_tr_loop']),
     main=P(lambda n, b, i: {'draws': 2000} if i == 40 else {}),
     x=P(lambda n, b, i: {} if i == 40 else {'bl_tr_us': 0}))
case('a_den_estimator', dict(A='NOT_EVALUABLE', a_failed=['a_den']),
     main=P(lambda n, b, i: {'draws': 2000} if i == 40 else {}),
     x=P(lambda n, b, i: {} if i == 40 else {'pl_em_rt_ns': 0, 'pl_em_rt_hit_ns': 0, 'pl_em_rt_hitg_ns': 0,
                                             'mh_emit_us': 6450}))

# ------------------------------------------------------------------ verdict edges (500 us, 2SE)
case('open_500_0', {'SP': 'OPEN', 'SP_point': 500.0, 'A': 'NOT_OPENED', 'consequence_head': 'OPEN', 'carrying': []},
     x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1030000}))
case('open_499_9', {'SP': 'NOT_OPENED', 'SP_point': 499.9}, x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1029900}))
case('open_member_a', {'A': 'OPEN', 'SP': 'OPEN', 'B': 'CLOSED', 'carrying': ['A']},
     x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1080000}))
case('open_member_a_499_9', {'A': 'NOT_OPENED', 'SP': 'OPEN', 'carrying': []},
     x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1079900}))
case('open_member_b', {'B': 'OPEN', 'SP': 'OPEN', 'carrying': ['B'], 't:N_B': 500.0},
     x=P(lambda n, b, i: {'bl_tr_hit_ns': 850000}))
# every member carries its own consequence (pred "Member verdicts", ROADMAP s120 item 4): A OPEN (N_A 520) while
# N_B = -50 keeps the package NOT_OPENED (N 470) - the summary still opens A's track; B CLOSED records B exhausted
case('member_open_pkg_not', {'A': 'OPEN', 'B': 'CLOSED', 'SP': 'NOT_OPENED', 'A_point': 520.0, 'B_point': -50.0,
                             'SP_point': 470.0, 'carrying': ['A'], 'consequence_head': 'OPEN', 'mcons_A': 'OPEN',
                             'mcons_B': 'CLOSED', 'consequence': mod.CONSEQUENCES['OPEN'] % 'A',
                             'mconsfull_A': mod.CONSEQUENCES['OPEN'] % 'A', 'mconsfull_B': mod.CONSEQUENCES['CLOSED']},
     x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1100000, 'bl_tr_hit_ns': 300000, 'bl_tr_hitg_ns': 290000}))
# carrying is by the member VERDICT, never by its point: B's point 500 but B NOT_EVALUABLE (tr_part) -> no track
case('carry_by_verdict_not_point', {'B': 'NOT_EVALUABLE', 'B_point': 500.0, 'A': 'NOT_OPENED', 'SP': 'NOT_EVALUABLE',
                                    'carrying': [], 'consequence_head': 'NOT_EVALUABLE', 'mcons_A': 'NOT_OPENED',
                                    'mcons_B': 'NOT_EVALUABLE', 'b_failed': ['tr_part']},
     x=P(lambda n, b, i: {'bl_tr_hit_ns': 850000, 'sp_tr_x_meta': 251}))
# a member OPEN beside the other member NOT_EVALUABLE: the package is NOT_EVALUABLE, A's track still opens
case('member_open_other_ne', {'A': 'OPEN', 'B': 'NOT_EVALUABLE', 'SP': 'NOT_EVALUABLE', 'carrying': ['A'],
                              'consequence_head': 'OPEN', 'mcons_A': 'OPEN', 'mcons_B': 'NOT_EVALUABLE'},
     x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1100000, 'sp_tr_x_meta': 251}))
TB0 = M(lambda n, b, i: {'bl_tr_us': 910})
case('closed_b_499_9', {'B': 'CLOSED', 'B_upper': 499.9, 't:T_B': 0.0}, x=lambda n, b, arm, i: (
    {'bl_tr_hit_ns': 669900} if arm == 0 else {'bl_tr_us': 910}) if i is not None else {})
case('closed_b_500_0', {'B': 'NOT_OPENED', 'B_upper': 500.0}, x=lambda n, b, arm, i: (
    {'bl_tr_hit_ns': 670000} if arm == 0 else {'bl_tr_us': 910}) if i is not None else {})
# the add-back Z decides: N_B + T_B = 400 < 500 but N_B+ = 580 (design120 s4: a mutant dropping Z must not give CLOSED)
case('z_addback_decides', {'B': 'NOT_OPENED', 'B_upper': 580.0, 't:Z_B': 180.0}, x=lambda n, b, arm, i: (
    {'bl_tr_hit_ns': 750000} if arm == 0 else {'bl_tr_us': 910}) if i is not None else {})
# D_B' decides: D_B = 0, D_B' = 90 000 ns; N_B + Z_B = 470 < 500, N_B+ = 470 + 64 = 534
case('dbp_decides', {'B': 'NOT_OPENED', 't:D_B_ns': 0.0, 't:D_Bp_ns': 90000.0, 'B_upper': 470.0 + 64.0},
     x=lambda n, b, arm, i: ({'bl_tr_hit_ns': 640000} if arm == 0 else {'bl_tr_us': 1000}) if i is not None else {})
# G is not the upper: G_B = 490 < 500 but N_B+ = 140 + 180 + 340 000 * 490/900/1000 = 505.1
case('g_not_upper', {'B': 'NOT_OPENED', 't:G_B': 490.0, 'B_upper': 320.0 + 340000 * (490000 / 900000) / 1000},
     x=lambda n, b, arm, i: ({'bl_tr_hit_ns': 490000} if arm == 0 else {'bl_tr_us': 1250}) if i is not None else {})
# CLOSED reads N+, never N: A point 420 < 500 but N_A+ 708.9 (base) -> NOT_OPENED; SP closed when both are small
case('sp_closed', {'SP': 'CLOSED', 'A': 'CLOSED', 'B': 'CLOSED', 'SP_upper': 20.0 + 146.0 + 230.0 + T_B,
                   'consequence_head': 'CLOSED'},
     x=lambda n, b, arm, i: ({'pl_em_rt_hit_ns': 600000, 'pl_em_rt_hitg_ns': 550000} if arm == 0 else
                             {'pl_em_rt_ns': 1400000,
                                                                          'mh_emit_us': 7200}) if i is not None else {})
# the global-witness N^g is never the verdict: N_A^g = 500 while N_A = 420
case('global_not_verdict', {'A': 'NOT_OPENED', 't:N_A_g': 500.0, 'A_point': 420.0},
     x=P(lambda n, b, i: {'pl_em_rt_hitg_ns': 1000000, 'sp_rt_wg': 0}))
# the check is paid by EVERY armed draw: pl_em_spchk_ns (400) is subtracted, not sp_rt_chkh_ns (330)
case('chk_all_draws', {'SP': 'NOT_OPENED', 'SP_point': 490.0}, x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1020000}))
# 2SE: B upper per pair 502, 398, 502, 398 (T_B = 0): mean 450, 2SE = 2*stdev/sqrt(4) = 60.044
SE_B = 2 * statistics.stdev([502.0, 398.0, 502.0, 398.0]) / 2
case('se2_blocks_b', {'B': 'NOT_OPENED', 'B_upper': 450.0, 'B_se2': SE_B, 'B_se2pt': SE_B, 'SP_se2': SE_B},
     x=lambda n, b, arm, i: ({'bl_tr_hit_ns': 672000 if b in (0, 4) else 568000} if arm == 0
                             else {'bl_tr_us': 910}) if i is not None else {})
case('se2_blocks_b_closed', {'B': 'CLOSED', 'B_upper': 430.0, 'B_se2': SE_B},
     x=lambda n, b, arm, i: ({'bl_tr_hit_ns': 652000 if b in (0, 4) else 548000} if arm == 0
                             else {'bl_tr_us': 910}) if i is not None else {})
# the package 2SE is the 2SE of the per-pair SUMS: A and B move against each other, SP is constant
case('se2_package_sums', {'A_se2': SE_B, 'B_se2': SE_B, 'SP_se2': 0.0, 'SP_point': 420.0 + 270.0},
     x=lambda n, b, arm, i: ({'pl_em_rt_hit_ns': 1052000 if b in (0, 4) else 948000,
                              'bl_tr_hit_ns': 568000 if b in (0, 4) else 672000} if arm == 0
                             else {'bl_tr_us': 910, 'pl_em_rt_ns': 1400000, 'mh_emit_us': 7200})
     if i is not None else {})
# the M block of a pair feeds D per pair: M-only variation gives a nonzero 2SE of the upper, the point's stays 0
case('se2_from_m_block', {'A_se2pt': 0.0, 'A_se2': 2 * statistics.stdev([100000 / 1.4 / 1000 * 3, 100000 / 1.4 / 1000,
                                                                          100000 / 1.4 / 1000 * 3,
                                                                          100000 / 1.4 / 1000]) / 2},
     x=M(lambda n, b, i: {'pl_em_rt_ns': 1700000 if b in (1, 5) else 1500000,
                          'mh_emit_us': 7500 if b in (1, 5) else 7300}))
case('pairs_one_ne', dict(NE_ALL, common_failed=['pairs2']), blocks=3, min_pairs=1)

# ------------------------------------------------------------------ correctness over ALL rows (FAIL)
case('bad_rt_window', dict(A='FAIL', SP='FAIL', B='CLOSED', fail_a=True, consequence_head='FAIL'),
     x=P(lambda n, b, i: {'sp_rt_bad': 1} if (b == 3 and i == 40) else {}))
case('bad_rt_m_edge', dict(A='FAIL', SP='FAIL', B='CLOSED'),
     x=M(lambda n, b, i: {'sp_rt_bad': 1} if (b == 1 and i == 0) else {}))
case('bad_rt_prestart', dict(A='FAIL', SP='FAIL'), x=lambda n, b, arm, i: {'sp_rt_bad': 1} if n == START else {})
case('bad_rt_pos89', dict(A='FAIL'), x=P(lambda n, b, i: {'sp_rt_bad': 1} if (b == 0 and i == 89) else {}))
LATE = 'FrameTrace-x: n=%d ' % (START + 1 + PERIOD * 3 + 40) + ' '.join(
    '%s=%d' % kv for kv in dict(X_P, sp_tr_bad=1).items())
case('bad_tr_late_dup', dict(B='FAIL', SP='FAIL', A='NOT_EVALUABLE', verdict='NOT_ADMITTED',
                              failed=['streams_complete']), extra_log=(LATE,))
case('bad_tr_window', dict(B='FAIL', SP='FAIL', A='NOT_OPENED', fail_b=True, fail_a=False),
     x=P(lambda n, b, i: {'sp_tr_bad': 2} if (b == 4 and i == 70) else {}))
case('mismatch_rt_line', dict(A='FAIL', SP='FAIL', B='CLOSED', rt_mismatch_lines=1),
     extra_log=('SpRtMismatch: draw=5 why=0x04 id=3/1',))
case('mismatch_tr_line', dict(B='FAIL', SP='FAIL', A='NOT_OPENED', tr_mismatch_lines=1),
     extra_log=('SpTrMismatch: stage=1 why=0x01',))
case('mismatch_rt_midline', dict(A='FAIL'), extra_log=('[12][00:00:01.000] SpRtMismatch: draw=5',))
case('fail_beats_not_admitted', dict(A='FAIL', SP='FAIL', B='NOT_EVALUABLE', verdict='NOT_ADMITTED',
                                     failed=['binary'], consequence_head='FAIL', mcons_A='FAIL',
                                     mcons_B='NOT_ADMITTED'),
     meta=dict(binary_sha256='cd' * 32), x=P(lambda n, b, i: {'sp_rt_bad': 1} if (b == 0 and i == 40) else {}))
case('fail_beats_ne', dict(A='FAIL', B='NOT_EVALUABLE'),
     x=lambda n, b, arm, i: ({'sp_rt_bad': 1, 'bl_tr_us': 0} if arm == 1 and i == 40 else {'bl_tr_us': 0}
                             if arm == 1 else {}) if i is not None else {})
# race: 10^4 * sum race == sum would over all rows -> evaluable; one more -> A NOT_EVALUABLE; never a FAIL
WOULD_ALL = 4000 * 4 * 90
case('race_edge', dict(OK, A='NOT_OPENED', SP='NOT_OPENED'),
     x=P(lambda n, b, i: {'sp_rt_race': WOULD_ALL // 10000} if (b == 3 and i == 40) else {}))
case('race_over', dict(A='NOT_EVALUABLE', SP='NOT_EVALUABLE', B='CLOSED', a_failed=['race']),
     x=P(lambda n, b, i: {'sp_rt_race': WOULD_ALL // 10000 + 1} if (b == 3 and i == 40) else {}))
case('race_over_edge_frame', dict(A='NOT_EVALUABLE', a_failed=['race']),
     x=P(lambda n, b, i: {'sp_rt_race': WOULD_ALL // 10000 + 1} if (b == 0 and i == 0) else {}))
case('race_would_all_rows', dict(A='NOT_OPENED', a_failed=[]),
     x=P(lambda n, b, i: dict({'sp_rt_race': WOULD_ALL // 10000 + 1} if (b == 3 and i == 40) else {},
                              **({'sp_rt_would': 5000, 'sp_rt_x_memo': 0} if i in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
                                 else {}))))
# one ns-scale step past the edge: 10^4 * 145 = 1 450 000 > 1 449 999 = the would over all rows
case('race_over_by_one', dict(A='NOT_EVALUABLE', a_failed=['race']),
     x=P(lambda n, b, i: dict({'sp_rt_race': WOULD_ALL // 10000 + 1} if (b == 3 and i == 40) else {},
                              **({'sp_rt_would': 4000 + 9999} if (b == 0 and i == 0) else {}))))
case('race_one_not_bad', dict(A='NOT_OPENED', fail_a=False), x=P(lambda n, b, i: {'sp_rt_race': 1} if i == 40 else {}))
# pathlap missing (sp_rt_nt > 0) on any P row -> A NOT_EVALUABLE; before START or on an M edge row it is not P
case('nt_window', dict(A='NOT_EVALUABLE', SP='NOT_EVALUABLE', B='CLOSED', a_failed=['nt']),
     x=P(lambda n, b, i: {'sp_rt_nt': 1} if (b == 4 and i == 50) else {}))
case('nt_p_edge_row', dict(A='NOT_EVALUABLE', a_failed=['nt']),
     x=P(lambda n, b, i: {'sp_rt_nt': 1} if (b == 4 and i == 0) else {}))
case('nt_prestart_ok', dict(OK, A='NOT_OPENED'), x=lambda n, b, arm, i: {'sp_rt_nt': 5} if n == START else {})
case('nt_m_edge_ok', dict(OK, A='NOT_OPENED'), x=M(lambda n, b, i: {'sp_rt_nt': 5} if i == 89 else {}))
# the P rows of nt are the rows of P blocks by the GateArm text, never by the main line's arm label
case('nt_p_row_label_m', dict(A='NOT_EVALUABLE', a_failed=['nt']),
     main=P(lambda n, b, i: {'arm': 1} if (b == 4 and i == 89) else {}),
     x=P(lambda n, b, i: {'sp_rt_nt': 1} if (b == 4 and i == 89) else {}))
case('nt_m_row_label_p', dict(OK, A='NOT_OPENED'),
     main=M(lambda n, b, i: {'arm': 0} if (b == 5 and i == 89) else {}),
     x=M(lambda n, b, i: {'sp_rt_nt': 1} if (b == 5 and i == 89) else {}))

# ------------------------------------------------------------------ controls
case('zbar_no_pairs', dict(NE_ALL, common_failed=['zbar']), x=P(lambda n, b, i: {'r2_nul_ns': 0, 'r2_nul_n': 0}))
case('zbar_zero', dict(NE_ALL, common_failed=['zbar'], A_point=None, B_upper=None, **{'t:N': None}),
     x=P(lambda n, b, i: {'r2_nul_ns': 0}))
case('zbar_m_zero_ok', dict(OK, **BASE_V), x=M(lambda n, b, i: {'r2_nul_ns': 0, 'r2_nul_n': 0}))
for fld in ('sp_rt_would', 'pl_em_spchk_ns', 'pl_em_sppost_ns', 'pl_em_rt_hit_ns', 'pl_em_rt_hitg_ns', 'bl_tr_hit_ns',
            'bl_tr_hitg_ns', 'sp_tr_x_flags', 'sp_rt_x_memo', 'sp_rt_rst', 'sp_tr_dcc', 'sp_rt_rec_ns', 'sp_tr_slots'):
    case('mzero_' + fld, dict(NE_ALL, common_failed=['m_zeros']),
         x=(lambda f: M(lambda n, b, i: {f: 1} if (b == 2 and i == 40) else {}))(fld))
case('mzero_edge_frames_ok', dict(OK, **BASE_V), x=M(lambda n, b, i: dict(X_P) if i in (0, 9, 89) else {}))
case('ser_dead_m', dict(NE_ALL, common_failed=['ser_alive']), x=M(lambda n, b, i: {'sp_ser_n': 0, 'sp_ser_val': 0}))
case('ser_dead_p', dict(NE_ALL, common_failed=['ser_alive']), x=P(lambda n, b, i: {'sp_ser_n': 0, 'sp_ser_val': 0}))
case('ser_val_over', dict(NE_ALL, common_failed=['ser_nest']),
     x=M(lambda n, b, i: {'sp_ser_val': 401} if b == 1 else {}))
case('ser_val_over_edge_8', dict(OK), x=M(lambda n, b, i: {'sp_ser_val': 408 if i == 40 else 400}))
case('ser_val_over_edge_8_p', dict(OK), x=P(lambda n, b, i: {'sp_ser_val': 408 if i == 40 else 400}))
case('ser_val_over_9', dict(NE_ALL, common_failed=['ser_nest']),
     x=M(lambda n, b, i: {'sp_ser_val': 409 if (b == 1 and i == 40) else 400}))
case('ser_val_over_9_p', dict(NE_ALL, common_failed=['ser_nest']),
     x=P(lambda n, b, i: {'sp_ser_val': 409 if (b == 4 and i == 40) else 400}))
case('ser_val_skew_ok', dict(OK), x=M(lambda n, b, i: {'sp_ser_val': 401 if i == 40 else 399 if i == 41 else 400}))
case('alive_rt', dict(NE_ALL, common_failed=['alive']),
     x=P(lambda n, b, i: dict({k: 0 for k in RT_R}, sp_rt_n=0, sp_rt_would=0, sp_rt_wg=0, pl_em_n=0, sp_rt_rec=0)))
case('alive_pl_em_m', dict(NE_ALL, common_failed=['alive']), x=M(lambda n, b, i: {'pl_em_n': 0}))
# draw identity sp_rt_n = pl_em_n: per P block within 64, over the P window within 256
case('draw_id_block_64', dict(OK), x=P(lambda n, b, i: {'pl_em_n': 5000 - 64} if (b == 3 and i == 40) else {}))
case('draw_id_block_65', dict(A='NOT_EVALUABLE', SP='NOT_EVALUABLE', B='CLOSED', a_failed=['draw_id']),
     x=P(lambda n, b, i: {'pl_em_n': 5000 + 65} if (b == 3 and i == 40) else {}))
case('draw_id_off_by_one', dict(A='NOT_EVALUABLE', a_failed=['draw_id']), x=P(lambda n, b, i: {'pl_em_n': 4999}))
case('draw_id_skew_ok', dict(OK), x=P(lambda n, b, i: {'pl_em_n': 5020} if i % 2 == 0 else {'pl_em_n': 4980}))
case('draw_id_total_256', dict(OK), x=P(lambda n, b, i: {'pl_em_n': 5000 - 64} if i == 40 else {}))
case('draw_id_total_320', dict(A='NOT_EVALUABLE', a_failed=['draw_id']), blocks=12,
     x=P(lambda n, b, i: {'pl_em_n': 5000 - 64} if (i == 40 and b != 11) else {}))
# reason partitions: +-SKEW_COUNT = 8 per P block window (ROADMAP s120 item 6); a cancelling +1/-1 skew on adjacent
# lines is ADMITTED; a persistent off-by-one (79 a window) FAILs (NOT_EVALUABLE)
case('rt_part_skew_ok', dict(OK), x=P(lambda n, b, i: {'sp_rt_x_memo': 101} if i == 40 else
                                     {'sp_rt_x_memo': 99} if i == 41 else {}))
case('rt_part_edge_8', dict(OK), x=P(lambda n, b, i: {'sp_rt_x_pass': 108} if (b == 4 and i == 40) else {}))
case('rt_part_edge_9', dict(A='NOT_EVALUABLE', SP='NOT_EVALUABLE', B='CLOSED', a_failed=['rt_part']),
     x=P(lambda n, b, i: {'sp_rt_x_pass': 109} if (b == 4 and i == 40) else {}))
case('rt_part_edge_minus8', dict(OK), x=P(lambda n, b, i: {'sp_rt_x_dsmp': 92} if (b == 4 and i == 40) else {}))
case('rt_part_edge_minus9', dict(A='NOT_EVALUABLE', a_failed=['rt_part']),
     x=P(lambda n, b, i: {'sp_rt_x_dsmp': 91} if (b == 4 and i == 40) else {}))
case('rt_part_persistent', dict(A='NOT_EVALUABLE', a_failed=['rt_part']),
     x=P(lambda n, b, i: {'sp_rt_x_cfg': 101}))
case('tr_part_skew_ok', dict(OK), x=P(lambda n, b, i: {'sp_tr_x_flags': 251} if i == 40 else
                                     {'sp_tr_x_flags': 249} if i == 41 else {}))
case('tr_part_edge_minus8', dict(OK), x=P(lambda n, b, i: {'sp_tr_x_ser': 242} if (b == 7 and i == 40) else {}))
case('tr_part_edge_minus9', dict(B='NOT_EVALUABLE', SP='NOT_EVALUABLE', A='NOT_OPENED', b_failed=['tr_part']),
     x=P(lambda n, b, i: {'sp_tr_x_ser': 241} if (b == 7 and i == 40) else {}))
case('tr_part_edge_8', dict(OK), x=P(lambda n, b, i: {'sp_tr_x_big': 258} if (b == 7 and i == 40) else {}))
case('tr_part_edge_9', dict(B='NOT_EVALUABLE', b_failed=['tr_part']),
     x=P(lambda n, b, i: {'sp_tr_x_big': 259} if (b == 7 and i == 40) else {}))
case('tr_part_persistent', dict(B='NOT_EVALUABLE', b_failed=['tr_part']), x=P(lambda n, b, i: {'sp_tr_x_meta': 251}))
case('rt_part_m_ignored', dict(OK), x=M(lambda n, b, i: {'sp_rt_n': 0}))
# nestings on window sums (count pairs within SKEW_COUNT = 8; multi-unit pairs within the subset's two edge lines)
case('nest_rt_wg_8', dict(OK), x=P(lambda n, b, i: {'sp_rt_wg': 4008 if (b == 0 and i == 40) else 4000}))
case('nest_rt_wg_9', dict(A='NOT_EVALUABLE', a_failed=['nest_rt_wg']),
     x=P(lambda n, b, i: {'sp_rt_wg': 4009 if (b == 0 and i == 40) else 4000}))
case('nest_rt_wg_skew_ok', dict(OK), x=P(lambda n, b, i: dict(
    {'sp_rt_wg': 4000}, **({'sp_rt_would': 3999, 'sp_rt_x_memo': 101} if i == 30 else
                           {'sp_rt_would': 4001, 'sp_rt_x_memo': 99} if i == 31 else {}))))
case('nest_tr_wg_9', dict(B='NOT_EVALUABLE', b_failed=['nest_tr_wg']),
     x=P(lambda n, b, i: {'sp_tr_wg': 7509 if (b == 0 and i == 40) else 7500}))
case('nest_tr_wg_8', dict(OK), x=P(lambda n, b, i: {'sp_tr_wg': 7508 if (b == 0 and i == 40) else 7500}))
case('nest_tr_wslots_skew_ok', dict(OK), x=P(lambda n, b, i: {'sp_tr_wslots': 45000 + (6000 if i == 30 else -6000
                                                                                        if i == 31 else 0)}))
EVERY = (('rt_wg', {'sp_rt_wg': 4001}, 'a'), ('rt_hitg', {'pl_em_rt_hitg_ns': 2000001}, 'a'),
         ('rt_hit', {'pl_em_rt_hit_ns': 2800001}, 'a'), ('rt_chkh', {'sp_rt_chkh_ns': 800001}, 'a'),
         ('rt_rep', {'sp_rt_rep_ns': 800001}, 'a'), ('rt_att', {'sp_rt_rep_att': 32001, 'sp_rt_tgt': 40000, 'rt_fast_ok': 40000}, 'a'),
         ('rt_kpx', {'sp_rt_rep_kpx': 60000001}, 'a'), ('rt_att_tgt', {'sp_rt_rep_att': 28001, 'rt_att': 60000}, 'a'),
         ('rt_tgt', {'sp_rt_tgt': 35001}, 'a'), ('tr_wg', {'sp_tr_wg': 7501}, 'b'),
         ('tr_wslots', {'sp_tr_wslots': 90001}, 'b'), ('tr_hitg', {'bl_tr_hitg_ns': 800001}, 'b'),
         ('tr_hit', {'bl_tr_hit_ns': 1800001}, 'b'), ('tr_loop', {'sp_tr_loop_ns': 2002001}, 'b'),
         ('tr_chkh', {'sp_tr_chkh_ns': 400001}, 'b'), ('tr_rep', {'sp_tr_rep_ns': 500001}, 'b'),
         ('tr_rec', {'sp_tr_rec_ns': 500001}, 'b'))
for nm, extra, grp in EVERY:
    exp = {('a_failed' if grp == 'a' else 'b_failed'): ['nest_' + nm], ('A' if grp == 'a' else 'B'): 'NOT_EVALUABLE'}
    case('nest_' + nm + '_every_line', exp, x=(lambda e: P(lambda n, b, i: e))(dict(extra)))
# ns nesting edge: the deficit over a block window equals the subset's two edge lines -> ok; one more ns -> not
case('nest_tr_hit_edge_ok', dict(OK), x=P(lambda n, b, i: {'sp_tr_loop_ns': 400000, 'bl_tr_us': 1000} if b != 3 else
                                         {'sp_tr_loop_ns': -400000 if i == 40 else 400000}))
case('nest_tr_hit_edge_over', dict(B='NOT_EVALUABLE', b_failed=['nest_tr_hit']),
     x=P(lambda n, b, i: {'sp_tr_loop_ns': 400000} if b != 3 else {'sp_tr_loop_ns': -400001 if i == 40 else 400000}))
case('nest_tr_hit_skew_ok', dict(OK), x=P(lambda n, b, i: {'bl_tr_hit_ns': 950000, 'bl_tr_hitg_ns': 390000}
                                         if i == 30 else {'bl_tr_hit_ns': 400000 - 550000 + 400000} if i == 31 else {}))
case('nest_rt_hit_skew_ok', dict(OK), x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1500000} if i == 30 else
                                         {'pl_em_rt_hit_ns': 500000} if i == 31 else {}))
case('nest_rt_att_edge_ok', dict(OK), x=P(lambda n, b, i: {'rt_att': 12000 - 24000} if (b == 3 and i == 40) else
                                         {'rt_att': 12000} if b == 3 else {}))
case('nest_rt_att_edge_over', dict(A='NOT_EVALUABLE', a_failed=['nest_rt_att']),
     x=P(lambda n, b, i: {'rt_att': 12000 - 24001} if (b == 3 and i == 40) else {'rt_att': 12000} if b == 3 else {}))
# sp_tr_loop_ns <= 1000*bl_tr_us + TR_ROUND_NS a row + the edge lines (bl_tr_us is MICROseconds)
case('nest_tr_loop_rounding_ok', dict(OK), x=P(lambda n, b, i: {'bl_tr_us': 877}))
case('nest_tr_loop_rounding_over', dict(B='NOT_EVALUABLE', b_failed=['nest_tr_loop']),
     x=P(lambda n, b, i: {'bl_tr_us': 876}))
# the emit chain in each arm: |sum of the 8 parts / 1000 - mh_emit_us| <= 256 us a frame (P carries the two new parts)
case('emit_p_256', dict(OK), x=P(lambda n, b, i: {'mh_emit_us': 7850 + 256}))
case('emit_p_257', dict(A='NOT_EVALUABLE', SP='NOT_EVALUABLE', B='CLOSED', a_failed=['emit_chain']),
     x=P(lambda n, b, i: {'mh_emit_us': 7850 + 257}))
case('emit_p_minus257', dict(A='NOT_EVALUABLE', a_failed=['emit_chain']), x=P(lambda n, b, i: {'mh_emit_us': 7593}))
case('emit_m_256', dict(OK), x=M(lambda n, b, i: {'mh_emit_us': 7250 - 256}))
case('emit_m_257', dict(A='NOT_EVALUABLE', a_failed=['emit_chain']), x=M(lambda n, b, i: {'mh_emit_us': 7250 + 257}))
case('emit_p_needs_new_parts', dict(A='NOT_EVALUABLE', a_failed=['emit_chain']),
     x=P(lambda n, b, i: {'mh_emit_us': 7850 - 800 + 100}))
case('emit_parts_each', dict(OK), x=P(lambda n, b, i: {'pl_em_vtx_ns': 1300000, 'pl_em_pipe_ns': 800000}))
for part in ('pl_em_vtx_ns', 'pl_em_spchk_ns', 'pl_em_rt_ns', 'pl_em_sppost_ns', 'pl_em_pipe_ns', 'pl_em_com_ns',
             'pl_em_rec_ns', 'pl_em_rest_ns'):
    case('emit_part_' + part, dict(A='NOT_EVALUABLE', a_failed=['emit_chain']),
         x=(lambda p: P(lambda n, b, i: {p: X_P[p] + 300000, 'mh_emit_us': 7850 + 300 - 257,
                                         'pl_em_rt_hit_ns': 1000000, 'pl_em_rt_ns': X_P['pl_em_rt_ns']
                                         + (300000 if p == 'pl_em_rt_ns' else 0)}))(part))
case('den_a', dict(A='NOT_EVALUABLE', SP='NOT_EVALUABLE', B='CLOSED', a_failed=['a_den'], **{'t:T_A': None}),
     x=P(lambda n, b, i: {'pl_em_rt_ns': 0, 'pl_em_rt_hit_ns': 0, 'pl_em_rt_hitg_ns': 0, 'mh_emit_us': 6450}))
case('den_b', dict(B='NOT_EVALUABLE', SP='NOT_EVALUABLE', A='NOT_OPENED', b_failed=['b_den'], **{'t:T_B': None}),
     x=P(lambda n, b, i: {'sp_tr_loop_ns': 0, 'bl_tr_hit_ns': 0, 'bl_tr_hitg_ns': 0}))
case('bl_tr_m_zero', dict(B='NOT_EVALUABLE', SP='NOT_EVALUABLE', A='NOT_OPENED', b_failed=['bl_tr_alive']),
     x=M(lambda n, b, i: {'bl_tr_us': 0}))
case('bl_tr_p_zero', dict(B='NOT_EVALUABLE', b_failed=['bl_tr_alive', 'nest_tr_loop']),
     x=P(lambda n, b, i: {'bl_tr_us': 0}))

# ------------------------------------------------------------------ admission, one check at a time
NA = dict(verdict='NOT_ADMITTED', consequence_head='NOT_ADMITTED', **NE_ALL)
case('binary', dict(NA, failed=['binary'], mcons_A='NOT_ADMITTED', mcons_B='NOT_ADMITTED'),
     meta=dict(binary_sha256='cd' * 32))
case('installed', dict(NA, failed=['installed_now']), installed='cd' * 32)
case('installed_empty', dict(NA, failed=['installed_now']), installed='')
case('pin_env', dict(NA, failed=['env_exact', 'pinned']),
     env={k: v for k, v in ENV_OK.items() if k != 'KYTY_GPU_CLOCK_PIN'})
case('pin_two', dict(NA, failed=['pinned']), pins=(PIN, PIN))
case('pin_mode2', dict(NA, failed=['pinned']), pins=('GpuClockPin: mode 2',))
case('pin_malformed', dict(NA, failed=['pinned']), pins=('GpuClockPin: mode X',))
case('env_rec', dict(NA, failed=['env_exact']), env=dict(ENV_OK, KYTY_REC='C:/x.mp4'))
case('env_checkpoints', dict(NA, failed=['env_exact']), env=dict(ENV_OK, KYTY_GPU_CHECKPOINTS='0'))
case('env_schedule', dict(NA, failed=['env_exact']),
     env=dict(ENV_OK, KYTY_GATE_SCHEDULE='90+1800:' + TEXT[1] + '|' + TEXT[0]))
case('env_markers', dict(NA, failed=['env_exact']), env=dict(ENV_OK, KYTY_GPU_MARKERS='2'))
case('env_vk', dict(NA, failed=['env_vk']), env=dict(ENV_OK, VK_LAYER_PATH='C:/x'))
case('hold', dict(NA, failed=['hold']), meta=dict(hold_s=299))
case('hold_draft_skipped', dict(OK, is_draft=True, **BASE_V), meta=dict(hold_s=180), draft=True)
case('two_attempts', dict(NA, failed=['one_ok_attempt']),
     meta=dict(attempts=[dict(label='a1', outcome='timeout', hold_exit=None),
                         dict(label='a2', outcome='ok', hold_exit=None, stable_frame=500)]))
case('hold_exit', dict(NA, failed=['one_ok_attempt']),
     meta=dict(attempts=[dict(label='a1', outcome='ok', hold_exit=3, stable_frame=500)]))
case('prereg_path', dict(NA, failed=['prereg']), meta=dict(prereg=dict(path='C:\\kyty\\s120\\pred\\02_x.md',
                                                                       sha256=FAKE_SHA, bytes=FAKE_BYTES)))
case('prereg_slashes_ok', dict(OK), meta=dict(prereg=dict(path='C:/kyty/s120/pred/01_cen120.md', sha256=FAKE_SHA,
                                                          bytes=FAKE_BYTES)))
case('prereg_meta_sha', dict(NA, failed=['prereg']), meta=dict(prereg=dict(path=PRED, sha256='cd' * 32,
                                                                           bytes=FAKE_BYTES)))
case('prereg_meta_bytes', dict(NA, failed=['prereg']), meta=dict(prereg=dict(path=PRED, sha256=FAKE_SHA, bytes=1)))
case('prereg_now_sha', dict(NA, failed=['prereg']), pred_now=('cd' * 32, FAKE_BYTES))
case('prereg_now_bytes', dict(NA, failed=['prereg']), pred_now=(FAKE_SHA, FAKE_BYTES + 1))
case('prereg_missing', dict(NA, failed=['prereg']), meta=dict(prereg=None))
case('prereg_unsealed', dict(NA, failed=['prereg']), pred_want=(None, None),
     meta=dict(prereg=dict(path=PRED, sha256=None, bytes=None)), pred_now=(None, None))
case('prereg_unsealed_sha_only', dict(NA, failed=['prereg']), pred_want=(None, FAKE_BYTES),
     meta=dict(prereg=dict(path=PRED, sha256=None, bytes=FAKE_BYTES)), pred_now=(None, FAKE_BYTES))
case('prereg_unsealed_bytes_only', dict(NA, failed=['prereg']), pred_want=(FAKE_SHA, None),
     meta=dict(prereg=dict(path=PRED, sha256=FAKE_SHA, bytes=None)), pred_now=(FAKE_SHA, None))
case('prereg_unsealed_draft', dict(OK, is_draft=True), pred_want=(None, None), draft=True)
# the module's own constants: with a fake prereg in the json the sealed check never passes (unsealed: None refuses;
# sealed: the fake sha is not the seal)
case('prereg_module_constants', dict(NA, failed=['prereg']), pred_want=None, pred_now=None)
case('gates_changed', dict(NA, failed=['gates_exact']), gates=GATES_TEXT.replace('dawalk=1', 'dawalk=0'))
case('gates_whitespace_ok', dict(OK), gates='  ' + GATES_TEXT.replace(' ', '   ') + '  ')
for nm in ('bindwit', 'bindalt', 'blmove', 'bindfloor', 'cbmove', 'slicecen', 'spine', 'bindpack'):
    case('gates_named_' + nm, dict(NA, failed=['base_names', 'gates_exact']), gates=GATES_TEXT + ' %s=0' % nm)
for nm, v in (('texmemo2', '1'), ('texfastcheck', '1'), ('m4baton', '32'), ('fslean', '1')):
    case('gates_pin_' + nm, dict(NA, failed=['base_names', 'gates_exact']),
         gates=GATES_TEXT.replace(' %s=0' % nm, ' %s=%s' % (nm, v)))
GF = BASE / 'gates_other.txt'
GF.write_bytes((GATES_TEXT + NL).encode('utf-8'))
case('gates_file_other', dict(NA, failed=['gates_base']), gates_file=str(GF))
case('gates_file_missing', dict(NA, failed=['gates_base']), gates_file=str(BASE / 'nope.txt'))
case('gate_other_name', dict(NA, failed=['gate_lines']), extra_log=('Gate: dawalk=0 frame=1890',))
case('gate_wrong_value', dict(NA, failed=['gate_lines']), extra_log=('Gate: spcen=1 frame=1890',))
case('gate_off_block', dict(NA, failed=['gate_lines']), extra_log=('Gate: spcen=1 frame=1801',))
case('gate_before_start', dict(NA, failed=['gate_lines']), extra_log=('Gate: spcen=0 frame=1710',))
case('gate_unknown_block', dict(NA, failed=['gate_lines']), extra_log=('Gate: spcen=1 frame=%d' % (START + 90 * 40),))
case('gate_malformed', dict(NA, failed=['gate_lines']), extra_log=('Gate: spcen=1',))
case('gate_every_block_ok', dict(OK),
     gate_lines=lambda b, arm: ['Gate: %s=%s frame=%d' % (k, v, START + PERIOD * b) for k, v in VALUES[arm].items()])
ARM_FAIL = dict(NA, failed=['arms', 'gate_lines', 'pairs'])
GA = 'GateArm: arm=%d arms=%d block=%d frame=%d period=%d abba=%d text=%s'
case('arm_text', ARM_FAIL, gate_arm=lambda b, arm: [GA % (arm, 2, b, START + PERIOD * b, 90, 1, TEXT[0])])
case('arm_text_space', ARM_FAIL, gate_arm=lambda b, arm: [GA % (arm, 2, b, START + PERIOD * b, 90, 1,
                                                                TEXT[arm].replace(' ', '  '))])
case('arm_count', ARM_FAIL, gate_arm=lambda b, arm: [GA % (arm, 3, b, START + PERIOD * b, 90, 1, TEXT[arm])])
case('arm_period', ARM_FAIL, gate_arm=lambda b, arm: [GA % (arm, 2, b, START + PERIOD * b, 80, 1, TEXT[arm])])
case('arm_abba', ARM_FAIL, gate_arm=lambda b, arm: [GA % (arm, 2, b, START + PERIOD * b, 90, 0, TEXT[arm])])
case('arm_frame', ARM_FAIL, gate_arm=lambda b, arm: [GA % (arm, 2, b, START + PERIOD * b + 1, 90, 1, TEXT[arm])])
case('arm_order', ARM_FAIL, order=(0, 1, 0, 1))
case('arm_one_malformed', ARM_FAIL, extra_log=('GateArm: arm=0 block=9',))
case('arm_dup', ARM_FAIL, extra_log=(GA % (0, 2, 0, 1800, 90, 1, TEXT[0]),))
case('arm_gap', ARM_FAIL, gate_arm=lambda b, arm: [] if b == 3 else [GA % (arm, 2, b, START + PERIOD * b, 90, 1,
                                                                           TEXT[arm])])
case('census_absent', dict(NA, failed=['sp_logged']), census=())
case('census_twice', dict(NA, failed=['sp_logged']), census=(CENSUS, CENSUS))
case('census_mode0', dict(NA, failed=['sp_logged']), census=('SpCensus: mode 0 rt_targets=9 tr_slots=32',))
for mk, line in (('hang', 'GpuHangAbort: tick=5'), ('slow', 'GpuWaitSlow: tick=5'), ('mhung', 'GpuMarkerHung: cs=1'),
                 ('ckpt', 'GpuCheckpointHang: op=1'), ('lost', 'Vulkan: ErrorDeviceLost'),
                 ('term', '--- std::terminate ---'), ('abort', '--- abort() ---'), ('fatal', '--- Fatal Error ---'),
                 ('unh', 'Unhandled exception: 0xc0000005'), ('err', '--- Error ---')):
    case('marker_' + mk, dict(NA, failed=['no_marker']), extra_log=(line,))
case('marker_stdout', dict(NA, failed=['no_marker']), stdout_lines=('--- Fatal Error ---',))
# AsyncPipelines: skipped draw - a line printed after frame k's lines belongs to frame k+1
F0 = START + 1 + PERIOD * 2
case('skip_pos40', dict(NA, failed=['no_skip_window']), extra_at={F0 + 39: [SKIP]})
case('skip_pos10', dict(NA, failed=['no_skip_window']), extra_at={F0 + 9: [SKIP]})
case('skip_pos88', dict(NA, failed=['no_skip_window']), extra_at={F0 + 87: [SKIP]})
case('skip_pos9_ok', dict(OK, skip_total=1), extra_at={F0 + 8: [SKIP]})
case('skip_pos89_ok', dict(OK), extra_at={F0 + 88: [SKIP]})
case('skip_prestart_ok', dict(OK), extra_at={START - 3: [SKIP]})
case('skip_first_line_ok', dict(OK), pins=(SKIP, PIN))
case('skip_m_window', dict(NA, failed=['no_skip_window']), extra_at={START + 1 + PERIOD * 1 + 49: [SKIP]})
WF = START + 1 + PERIOD * 3 + 50
case('stream_missing_x', dict(NA, failed=['streams_complete']), drop=(('x', WF),))
case('stream_missing_draw', dict(NA, failed=['streams_complete']), drop=(('draw', WF),))
case('stream_missing_main', dict(NA, failed=['streams_complete']), drop=(('main', WF),))
case('stream_dup_x', dict(NA, failed=['streams_complete']), dup=(WF,))
case('stream_field_x', dict(NA, failed=['streams_complete']), strip=(('x', WF, 'sp_tr_x_flags'),))
case('stream_field_x_first', dict(NA, failed=['streams_complete']), strip=(('x', WF, 'sp_ser_n'),))
case('stream_field_x_rt_fast', dict(NA, failed=['streams_complete']), strip=(('x', WF, 'rt_fast_no'),))
case('stream_field_draw', dict(NA, failed=['streams_complete']), strip=(('draw', WF, 'bda_scan'),))
case('stream_field_main', dict(NA, failed=['streams_complete']), strip=(('main', WF, 'cpu_gpu_us'),))
case('stream_arm_label', dict(NA, failed=['streams_complete']),
     main=lambda n, b, arm, i: {'arm': 1 - arm} if n == WF else {})
case('stream_blk_label', dict(NA, failed=['streams_complete']),
     main=lambda n, b, arm, i: {'blk': b + 1} if n == WF else {})
case('stream_low_draws_row_ok', dict(OK), main=lambda n, b, arm, i: {'draws': 100} if n == WF else {})
case('stream_pos9_missing_ok', dict(OK), drop=(('x', START + 1 + PERIOD * 3 + 9),))
case('stream_pos89_dup_ok', dict(OK, **BASE_V), dup=(START + 1 + PERIOD * 3 + 89,))
case('stream_run_end_ok', dict(OK, **BASE_T), post=30)
case('unpaired_block_not_pooled', dict(OK, **BASE_T), post=40,
     x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1300000, 'bl_tr_hit_ns': 800000, 'r2_nul_ns': 70000,
                          'bl_tr_us': 1100, 'pl_em_rt_ns': 1500000, 'mh_emit_us': 8100} if b == 8 else {}))
case('unpaired_block_controls', dict(A='NOT_EVALUABLE', a_failed=['rt_part']), post=40,
     x=P(lambda n, b, i: {'sp_rt_x_memo': 109} if (b == 8 and i == 20) else {}))
case('stream_run_end_window', dict(OK, pairs=[[0, 1], [3, 2], [4, 5], [7, 6]]), blocks=9, post=0,
     x=lambda n, b, arm, i: {}, pre=5)
# the run ends after the last main line but before its -x (or -draw) line, or cuts it: that last line is exempt
# (g2_119 n < last_main, rpk120 n == last_main); frame 2650 = block 9 (M) position 39
LAST = START + PERIOD * 9 + 40
PAIRS4 = [[0, 1], [3, 2], [4, 5], [7, 6]]
case('stream_last_line_cut', dict(OK, pairs=PAIRS4), blocks=9, post=40, drop=(('x', LAST),))
case('stream_last_line_cut_draw', dict(OK, pairs=PAIRS4), blocks=9, post=40, drop=(('draw', LAST),))
case('stream_last_line_cut_both', dict(OK, pairs=PAIRS4), blocks=9, post=40, drop=(('draw', LAST), ('x', LAST)))
case('stream_last_line_short', dict(OK, pairs=PAIRS4), blocks=9, post=40, strip=(('x', LAST, 'rt_fast_no'),))
case('stream_penultimate_cut', dict(NA, failed=['streams_complete']), blocks=9, post=40, drop=(('x', LAST - 1),))
# a complete last main line is a row like any other (its counters reach the controls of the partial block)
case('stream_last_line_full_counts', dict(A='NOT_EVALUABLE', a_failed=['rt_part']), post=40,
     x=P(lambda n, b, i: {'sp_rt_x_memo': 109} if n == START + PERIOD * 8 + 40 else {}))
# a partial last block pairs only when its window reached position 88 (both blocks complete, as rpk120)
case('partial_last_pair', dict(OK, **BASE_T, pairs=PAIRS4), blocks=9, post=40,
     x=M(lambda n, b, i: {'pl_em_rt_ns': 1900000, 'mh_emit_us': 7700} if b == 9 else {}))
case('partial_last_pair_pos87', dict(OK, pairs=PAIRS4), blocks=9, post=88)
case('partial_last_pair_pos88', dict(OK, pairs=PAIRS4 + [[8, 9]]), blocks=9, post=89)
case('pairs_30', dict(OK), blocks=60, min_pairs=None)
case('pairs_29', dict(NA, failed=['pairs']), blocks=58, min_pairs=None)
case('pairs_draft_skipped', dict(OK, is_draft=True), blocks=8, min_pairs=None, draft=True)
case('idle_edge', dict(OK), meta=dict(pre_run=dict(gpu_util_median=10)))
case('idle_11', dict(NA, failed=['idle']), meta=dict(pre_run=dict(gpu_util_median=11)))
case('idle_missing', dict(NA, failed=['idle']), meta=dict(pre_run={}))
case('draft_not_other_checks', dict(NA, failed=['binary'], is_draft=True), draft=True, meta=dict(binary_sha256='cd' * 32))

# ------------------------------------------------------------------ report
for nm, v, regime in (('bda_new_300', 300, 'NEW'), ('bda_mixed_301', 301, 'MIXED'), ('bda_mixed_599', 599, 'MIXED'),
                      ('bda_old_600', 600, 'OLD')):
    case(nm, {'rep0:bda_regime': regime, 'rep1:bda_regime': 'NEW', 'rep0:bda_scan': float(v)},
         draw=(lambda val: P(lambda n, b, i: {'bda_scan': val}))(v))
root = make('report_draft_lines', meta=dict(hold_s=180))
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, draft=True, min_pairs=None, pred_want=(None, None),
                   pred_now=(None, None))
text = NL.join(mod.format_report(res))
ok = text.split(NL)[0].startswith('DRAFT') and 'VERDICT: ADMITTED' in text and res['draft'] is True
RESULTS.append(('report_draft_lines', ok, [] if ok else [text[:300]]))
root = make('report_na_lines', meta=dict(binary_sha256='cd' * 32))
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_pairs=PAIRS, pred_want=FAKE, pred_now=FAKE)
text = NL.join(mod.format_report(res))
ok = ('VERDICT: NOT_ADMITTED (failed: binary)' in text and 'REPORT OF A NOT_ADMITTED RUN' in text
      and 'MEMBER A: NOT_EVALUABLE point=420.0' in text and 'CONSEQUENCE: NOT_ADMITTED' in text)
RESULTS.append(('report_na_lines', ok, [] if ok else [text[-600:]]))
root = make('report_open_lines', x=P(lambda n, b, i: {'bl_tr_hit_ns': 850000}))
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_pairs=PAIRS, pred_want=FAKE, pred_now=FAKE)
text = NL.join(mod.format_report(res))
ok = ('MEMBER B: OPEN point=500.0' in text and 'PACKAGE SP: OPEN point=920.0' in text
      and 'CONSEQUENCE: OPEN' in text and 'member(s) B;' in text)
RESULTS.append(('report_open_lines', ok, [] if ok else [text[-600:]]))
root = make('report_open_both', x=P(lambda n, b, i: {'bl_tr_hit_ns': 850000, 'pl_em_rt_hit_ns': 1080000}))
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_pairs=PAIRS, pred_want=FAKE, pred_now=FAKE)
ok = res['carrying'] == ['A', 'B'] and 'member(s) A+B;' in res['consequence']
RESULTS.append(('report_open_both', ok, [] if ok else [res['consequence']]))
root = make('report_open_together', x=P(lambda n, b, i: {'pl_em_rt_hit_ns': 1030000}))
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_pairs=PAIRS, pred_want=FAKE, pred_now=FAKE)
ok = 'member(s) A+B (together);' in res['consequence']
RESULTS.append(('report_open_together', ok, [] if ok else [res['consequence']]))
root = make('report_ne_lines', x=P(lambda n, b, i: {'r2_nul_ns': 0}))
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_pairs=PAIRS, pred_want=FAKE, pred_now=FAKE)
text = NL.join(mod.format_report(res))
ok = ('PACKAGE SP: NOT_EVALUABLE point=NA upper=NA 2se=NA' in text and 'CONSEQUENCE: NOT_EVALUABLE' in text
      and 'common: FAIL zbar' in text)
RESULTS.append(('report_ne_lines', ok, [] if ok else [text[-700:]]))
root = make('report_price_se2', main=lambda n, b, arm, i: {'dt_us': 33000 + (100 if b in (0, 4) else -100)}
            if (arm == 0 and i is not None) else {})
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_pairs=PAIRS, pred_want=FAKE, pred_now=FAKE)
want_se = 2 * statistics.stdev([2100.0, 1900.0, 2100.0, 1900.0]) / 2
ok = (res['se2_price_dt_us'] is not None and abs(res['se2_price_dt_us'] - want_se) < 1e-9
      and res['se2_price_cpu_gpu_us'] == 0.0)
RESULTS.append(('report_price_se2', ok, [] if ok else ['%r' % res['se2_price_dt_us']]))
text = NL.join(mod.format_report(res_ok))
ok = ('zbar 10.00 ns' in text and "D_B' 190000.0 ns" in text and 'N_A+ 708.9' in text and 'G_A+ 1142.9' in text
      and 'N_A^g 372.0' in text and 'price P-M (report only): dt_us 2000.0' in text and 'bda_scan 50.0 (NEW)' in text
      and 'Z 326.0' in text and 'D_A 200000.0 ns' in text and 'T_B 84.4' in text)
RESULTS.append(('report_terms_text', ok, [] if ok else [text]))

se_a = 2 * statistics.stdev([100000 / 1.4 / 1000 * 3, 100000 / 1.4 / 1000, 100000 / 1.4 / 1000 * 3,
                              100000 / 1.4 / 1000]) / 2
root = make('report_se2_line', x=M(lambda n, b, i: {'pl_em_rt_ns': 1700000 if b in (1, 5) else 1500000,
                                                    'mh_emit_us': 7500 if b in (1, 5) else 7300}))
res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_pairs=PAIRS, pred_want=FAKE, pred_now=FAKE)
text = NL.join(mod.format_report(res))
want = 'MEMBER A: NOT_OPENED point=420.0 upper=%.1f 2se=%.1f' % (566.0 + 200000 / 1.4 / 1000, se_a)
RESULTS.append(('report_se2_line', want in text, [want, text[-500:]]))

real = Path(mod.PRED_PATH)
if mod.PRED_SHA is not None and real.is_file():
    data = real.read_bytes()
    import hashlib
    sha = hashlib.sha256(data).hexdigest()
    root = make('prereg_real', meta=dict(prereg=dict(path=PRED, sha256=sha, bytes=len(data))))
    res = mod.evaluate(str(root), TAG, installed_sha=BUILD, min_pairs=PAIRS)
    RESULTS.append(('prereg_real', res['checks']['prereg'] is True, ['%r' % res['checks']['prereg']]))

# ------------------------------------------------------------------ --real: the unsealed smoke smk120
if '--real' in sys.argv:
    R = 'C:/kyty/s120'
    res = mod.evaluate(R, 'smk120', installed_sha=BUILD, draft=True)
    t = res['terms']
    # the scorer's own numbers on the smoke (block 0 = frames 1801..1890 in the window)
    mine = dict(nfp=1658, nfm=1641, G_A=977.9, G_B=402.7, N_A=315.5, N_B=-9.8, N=305.7, Z=283.6, N_up=830.7,
                N_A_up=653.7, N_B_up=176.9, price_dt_us=2816.9)
    bad = ['%s=%r want %r' % (k, t.get(k), v) for k, v in mine.items()
           if t.get(k) is None or abs(t[k] - v) > 0.051]
    if res['verdict'] != 'ADMITTED' or res['members']['SP']['verdict'] != 'NOT_OPENED' \
            or res['members']['A']['verdict'] != 'NOT_OPENED' or res['members']['B']['verdict'] != 'CLOSED':
        bad.append('verdicts %s %r' % (res['verdict'], {k: v['verdict'] for k, v in res['members'].items()}))
    RESULTS.append(('real_scorer', not bad, bad))
    # the lead's draft (smoke120.py) groups by the main-line blk label and positions in that list: block 0 there
    # starts with the 1800 pre-schedule rows (they print arm=0 blk=0), so its positions 10..88 are frames 11..89 (all
    # draws <= 3000) and the real block 0 falls out.  Rebuild that population with the scorer's own terms().
    run_ = mod.read_run(R, 'smk120')
    fine, blocks = mod.arms_ok(run_['gate_arms'])
    seen = run_['seen']
    prow, mrow = [], []
    for b, arm in blocks.items():
        if b == 0:
            continue
        for pos in range(10, 89):
            n = START + 1 + PERIOD * b + pos
            if seen['main'].get(n) and seen['main'][n]['draws'] > 3000:
                (prow if arm == 0 else mrow).append(dict(seen['main'][n], **seen['draw'][n], **seen['x'][n]))
    zbar = sum(r['r2_nul_ns'] for r in prow) / sum(r['r2_nul_n'] for r in prow)
    td = mod.terms(prow, mrow, zbar)
    draft = dict(nfp=1579, nfm=1641, G_A=976.7, G_B=401.9, N_A=315.3, N_B=-10.1, N=305.2, Z=282.6, D_A_ns=289031.8,
                 D_Bp_ns=69729.7, N_up=830.0, price_dt_us=2783.8, price_cpu_gpu_us=2695.3)
    bad = ['%s=%r want %r' % (k, td.get(k), v) for k, v in draft.items() if abs(td[k] - v) > 0.051]
    if abs(zbar - 8.71) > 0.0051:
        bad.append('zbar %r' % zbar)
    for k, v in (('dt_us', 36856.4), ('cpu_gpu_us', 35596.8), ('draws', 5041.0), ('bda_scan', 67.8)):
        got = sum(r[k] for r in prow) / len(prow)
        if abs(got - v) > 0.051:
            bad.append('P %s %r want %r' % (k, got, v))
    for k, v in (('dt_us', 34072.6), ('cpu_gpu_us', 32901.5), ('draws', 5062.9), ('bda_scan', 60.3)):
        if abs(res['report'][1][k] - v) > 0.051:
            bad.append('M %s %r want %r' % (k, res['report'][1][k], v))
    RESULTS.append(('real_draft_population', not bad, bad))

fails = [r for r in RESULTS if not r[1]]
for name, ok, why in RESULTS:
    line = '%-32s %s %s' % (name, 'ok' if ok else 'FAIL', '; '.join(why) if not ok else '')
    print(line.encode('ascii', 'backslashreplace').decode('ascii'))
print('%d fixtures, %d failed' % (len(RESULTS), len(fails)))
print('ALL OK' if not fails else 'FIXTURE FAILURES')
sys.exit(0 if not fails else 1)
