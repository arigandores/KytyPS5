"""Session 116 (DRAFT, not sealed; amended after the pre-seal check, ROADMAP 116 items 3-4): fixtures for obs116.py -
ADMITTED on a straddle-free synthetic log, every admission check failing alone (or together with the checks it implies
by construction: an env key that is also pinned by env_exact, a gate token that also changes GATES_SHA, a population
that also breaks its identity), both sides of every edge (MIN_ROWS 6000 with its real value, ID_HOLD_TOL 16,
ID_EMIT_TOL 256, PROC_N_TOL 16, PROC_WALL_PCT 101, HOLD_COVER 98..102 %, IDLE_GPU_MAX, the stable frame of the Gate
lines, the range bounds), a per-row emit skew of +-30 summing to +40 (ADMITTED) against a steady +1 a row over 300
rows (NOT_ADMITTED by the total), a gate toggled inside the scene (a straddle), the pre-registration hash (fake and the
real file),
the units (raw ns -> us, us kept), span keys without medians, and the report numbers of a small hand-computed log.
    python test_obs116.py <obs116.py>
Sizes come from this suite's own constants (EDGE, SMALL), never from the scorer: most fixtures are SMALL rows and are
evaluated with min_rows=SMALL; the two EDGE fixtures use the scorer's default MIN_ROWS.
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s116/fx_obs116')
NL = chr(10)
spec = importlib.util.spec_from_file_location('obs116', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)

SMALL = 12
EDGE = 6000
STABLE = 500
TAG = 'obs116'
BUILD = 'd3a981a23fc1c5df651eef2a93ff1f02a8bffd04416adea2fd5cd2218e290f64'
PRED = 'C:\\kyty\\s116\\pred\\01_obs116.md'
FAKE_SHA = 'ab' * 32
REAL_PRED_SHA = hashlib.sha256(Path('C:/kyty/s116/pred/01_obs116.md').read_bytes()).hexdigest()
GATES_OK = ('copy=1 srtpages=1 clamp=1 regionepoch=0 srtmemo=0 smemocheck=0 bdastamp=1 backpages=1 srtstat=0 '
            'metalock=1 drawahead=1 dause=1 asyncsubmit=1 imgrecycle=1 recordthread=1 trackfree=1 tfcheck=0 '
            'protfast=0 swlocal=0 swdefer=1 gdsepoch=0 atomimg=0 dsring=1 recpack=1 syncfree=1 sfcheck=0 '
            'protbatch=1 pbcheck=0 texfaulthint=1 daclass=1 daprefetch=1 daclone=0 texlru=1 texfast=1 '
            'texfastcheck=0 texmemo2=0 clampvma=1 smpmemo=1 bindspare=0 fslean=0 applyskip=0 recbatch=0 recrelax=0 '
            'recpin=1 stkstat=0 drawstat=0 dpslow=0 drawstate=1 snapkeep=1 buflru=1 snapdiff=1 snapswap=1 buffast=0 '
            'buffastcheck=0 protbatch2=0 acopyidle=1 dawalk=1 rtfast=1 progmemo=1 progmemocheck=0 armdefer=0 '
            'armcheck=0 dawitness=1 dawitptr=1 daqpre=0 cbstat=0 recimg=0 recup=0 shadowinline=0 savepersist=0 '
            'occzero=0 amut=0 pxstat=0 mutsite=1 imgskip=0 cleardec=0 daepceil=0 dawitfb=0 imgfuse=1 dawitcp=1 '
            'dawitcg=1 dawitcgcheck=0 pfhint=1 dathreads=4 recarena=64 dsbatch=32 dspool=1024 recspin=300 dapin=3 '
            'procpin=0 faultkb=64 dawalklead=1 recpubn=0 shadowresolve=0 shadowmask=3 m4baton=0 imgskipkb=4096 '
            'dawitloop=0 pfcap=1024 pathlap=1')
ENV_OK = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GATE_FILE': 'C:\\kyty\\s116\\gates.req',
          'KYTY_SAMPLE_GATE': 'C:\\kyty\\s116\\sample.req', 'KYTY_QUEUE_TRACE': '1',
          'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0',
          'KYTY_GPU_WALL': '1', 'VK_SDK_PATH': 'C:\\VulkanSDK\\1.4.357.0'}
PIN = 'GpuClockPin: mode 1 - the guest GPU clock ignores the pacer speed (KYTY_GPU_CLOCK_PIN)'
WALL = 'GpuWall: mode 1'
GATE_LINES = ('Gate: mutsite=1 frame=1', 'Gate: pathlap=1 frame=1')   # as obs111: `Gate: plkstat=1 frame=1`
MAIN_DEF = dict(dt_us=33000, cpu_gpu_us=31000, draws=5300, dispatches=270, gpu_busy_us=12000, semwait_gpu_us=0,
                prios=19, prio_us=0)
DRAW_DEF = dict(bda_scan=51)
X_DEF = dict(mh_pro_us=400, mh_rt_us=900, mh_prog_us=5000, mh_bind_us=10000, mh_emit_us=7000, mh_tail_us=100,
             mh_disp_us=2300, a_hold_us=25750, a_wait_us=150, mh_pres_us=300, mh_pres_wait_us=20,
             pl_proc_ns=30000000, pl_pref_ns=100000, pl_eop_ns=40000, pl_bar_ns=10000, pl_sub_ns=60000,
             pl_gc_ns=70000, pl_cmd_ns=500000, pl_look_ns=1000, pl_em_vtx_ns=1300000, pl_em_rt_ns=1500000,
             pl_em_pipe_ns=700000, pl_em_com_ns=2200000, pl_em_rec_ns=1200000, pl_em_rest_ns=40000,
             gw_idle_ns=800000, gw_blk_ns=100000, gw_flip_ns=500000, gw_proc_ns=30100000, gw_cmd_ns=50000,
             flip_rsv_wait_ns=0, mh_n=5310, mh_draws=5290, mh_disp_n=270, a_hold_n=5580, mh_pres_n=2,
             pl_proc_n=500, pl_pref_n=8, pl_eop_n=370, pl_bar_n=1100, pl_sub_n=540, pl_gc_n=8, pl_cmd_n=26000,
             pl_look_n=8, pl_em_n=5290, gw_idle_n=20, gw_blk_n=2, gw_flip_n=1, gw_proc_n=500, gw_cmd_n=3,
             flip_rsv_wait_n=0)
# The 4 rows of the hand-computed log (every other field at its default; mh_rt_us 2000 and mh_disp_us 1200 sit on
# the upper / lower bound of their report ranges; hold / a_hold = 106800 / 107000; gw_proc = pl_proc + 100 us).
HAND_COMMON = dict(mh_rt_us=2000, mh_disp_us=1200, flip_rsv_wait_ns=2000, flip_rsv_wait_n=2, semwait_gpu_us=10,
                   prio_us=19)
HAND = (dict(HAND_COMMON, dt_us=30000, cpu_gpu_us=28000, draws=5000, dispatches=250, mh_bind_us=9000,
             a_hold_us=24750, a_wait_us=100, pl_proc_ns=29000000, gw_proc_ns=29100000, gw_flip_ns=0, bda_scan=40),
        dict(HAND_COMMON, dt_us=32000, cpu_gpu_us=30000, draws=5200, dispatches=270, mh_bind_us=10000,
             a_hold_us=25750, a_wait_us=200, pl_proc_ns=30000000, gw_proc_ns=30100000, gw_flip_ns=500000,
             bda_scan=50),
        dict(HAND_COMMON, dt_us=34000, cpu_gpu_us=31000, draws=5400, dispatches=270, mh_bind_us=11000,
             a_hold_us=26750, a_wait_us=300, pl_proc_ns=31000000, gw_proc_ns=31100000, gw_flip_ns=1000000,
             bda_scan=60),
        dict(HAND_COMMON, dt_us=40000, cpu_gpu_us=35000, draws=5600, dispatches=290, mh_bind_us=14000,
             a_hold_us=29750, a_wait_us=400, pl_proc_ns=34000000, gw_proc_ns=34100000, gw_flip_ns=2500000,
             bda_scan=1000))
# Per-row skew of pl_em_n - mh_draws: +-30 a row, sum +40, median 0 (the shape of pl96a's read skew).
SKEW = (30, -30, 30, -30, 30, -30, 30, -30, 30, 10, 0, 0, 0, 0, 0)


def row_lines(n, over, drop):
    """The three FrameTrace lines of flip n: defaults, `over` (field -> value), `drop` (field names left out)."""
    m = dict(MAIN_DEF)
    dr = dict(DRAW_DEF)
    x = dict(X_DEF)
    for k, v in over.items():
        (m if k in m else dr if k in dr else x)[k] = v
    main = ('FrameTrace: n=%d dt_us=%d lat_us=3 gpu_proc=0 semwaits=2 semwait_us=40 draws=%d draw_us=0 '
            'dispatches=%d gpu_busy_us=%d cpu_main_us=9000 cpu_gpu_us=%d semwait_gpu_us=%d prios=%d prio_us=%d '
            'arm=0 blk=0' % (n, m['dt_us'], m['draws'], m['dispatches'], m['gpu_busy_us'], m['cpu_gpu_us'],
                             m['semwait_gpu_us'], m['prios'], m['prio_us']))
    draw = 'FrameTrace-draw: n=%d logs=1 bda_us=0 bda_scan=%d bda_skip=1000' % (n, dr['bda_scan'])
    xs = 'FrameTrace-x: n=%d ds_ring_new=0 pl_prog_wait_us=7 bda_scan_us=99 gw_idle_prio=0' % n
    xs += ''.join(' %s=%d' % (k, v) for k, v in x.items())
    for k in drop:
        main = main.replace(' %s=' % k, ' %sX=' % k)
        draw = draw.replace(' %s=' % k, ' %sX=' % k)
        xs = xs.replace(' %s=' % k, ' %sX=' % k)
    return main, draw, xs


def build(name, rows=SMALL, stable=STABLE, env=None, env_drop=(), atts=None, binary=None, gates=GATES_OK,
          gpu_util=0.0, pre_run=True, hold_s=300, prereg=PRED, prereg_sha=FAKE_SHA, pins=(PIN,), walls=(WALL,),
          gate_lines=GATE_LINES, lines=(), stdout=None, all_over=None, per_row=None, row_over=None, row_drop=None,
          skip=None, dup=None):
    """Writes one fixture directory and returns its path.  all_over: overrides of every scene row; per_row: a list
    of overrides, one per scene row; row_over / row_drop: {index: overrides / names to drop} of single scene rows;
    skip: {index: 'main'|'draw'|'x'} line left out; dup: index whose FrameTrace-x line is written twice."""
    d = BASE / name
    d.mkdir()
    e = dict(ENV_OK)
    e.update(env or {})
    for k in env_drop:
        e.pop(k, None)
    meta = {'binary_sha256': binary or BUILD, 'env': e, 'gates': gates, 'hold_s': hold_s,
            'attempts': atts if atts is not None else [{'outcome': 'ok', 'hold_exit': None, 'stable_frame': stable}]}
    if pre_run:
        meta['pre_run'] = {'gpu_util_median': gpu_util}
    if prereg is not None:
        meta['prereg'] = {'path': prereg, 'bytes': 1}
        if prereg_sha is not None:
            meta['prereg']['sha256'] = prereg_sha
    if hold_s is None:
        del meta['hold_s']
    (d / (TAG + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    out = ['--- Build ---', 'Fork build d3a981a2'] + list(pins) + list(walls) + list(gate_lines)
    for n in range(stable - 3, stable):   # before the scene: incomplete and off every identity, never read
        out += ['FrameTrace: n=%d dt_us=99999 draws=1' % n, 'FrameTrace-draw: n=%d bda_scan=5000' % n,
                'FrameTrace-x: n=%d a_hold_n=99999 mh_n=1 pl_em_n=77' % n]
    for i in range(rows):
        over = dict(all_over or {})
        over.update((per_row or [{}] * rows)[i])
        over.update((row_over or {}).get(i, {}))
        main, draw, xs = row_lines(stable + i, over, (row_drop or {}).get(i, ()))
        gone = (skip or {}).get(i)
        out += [s for s, kind in ((main, 'main'), (draw, 'draw'), (xs, 'x')) if kind != gone]
        if dup == i:
            out.append(xs)
    out += list(lines)
    (d / ('log_%s.txt' % TAG)).write_bytes((NL.join(out) + NL).encode('utf-8'))
    if stdout is not None:
        (d / ('stdout_%s.txt' % TAG)).write_bytes((stdout + NL).encode('utf-8'))
    return str(d)


def failing(res):
    return sorted(k for k, v in res['checks'].items() if not v)


NO_SCENE = ['armed', 'gate_lines', 'hold_cover', 'one_ok_attempt', 'rows']
EMIT = ['id_emit_n']
cases = [
    ('ADMITTED', dict(), {}, []),
    ('ADMITTED_stdout_clean', dict(stdout='0xe06d7363 C++ exception (not a marker)'), {}, []),
    ('ADMITTED_gate_order', dict(gate_lines=GATE_LINES[::-1]), {}, []),
    ('ADMITTED_prereg_slash', dict(prereg='C:/kyty/s116/pred/01_obs116.md'), {}, []),
    ('ADMITTED_no_vk', dict(env_drop=['VK_SDK_PATH']), {}, []),
    ('ADMITTED_gates_spacing', dict(gates=GATES_OK.replace(' ', '  ', 3) + NL), {}, []),
    ('ADMITTED_real_pred', dict(prereg_sha=REAL_PRED_SHA), dict(pred_sha=None), []),
    ('binary', dict(binary='1' * 64), {}, ['binary']),
    ('installed', dict(), dict(installed='0' * 64), ['installed_now']),
    ('pin_env', dict(env_drop=['KYTY_GPU_CLOCK_PIN']), {}, ['env_exact', 'pinned']),
    ('pin_env_2', dict(env={'KYTY_GPU_CLOCK_PIN': '2'}), {}, ['env_exact', 'pinned']),
    ('pin_none', dict(pins=()), {}, ['pinned']),
    ('pin_two', dict(pins=(PIN, PIN)), {}, ['pinned']),
    ('pin_mode2', dict(pins=(PIN.replace('mode 1', 'mode 2'),)), {}, ['pinned']),
    ('pin_garbled', dict(pins=(PIN, 'GpuClockPin: ?')), {}, ['pinned']),
    ('env_rec', dict(env={'KYTY_REC': 'C:\\kyty\\s116\\rec_obs116.mp4'}), {}, ['env_exact']),
    ('env_schedule', dict(env={'KYTY_GATE_SCHEDULE': '300:mutsite=1|mutsite=0'}), {}, ['env_exact']),
    ('env_checkpoints', dict(env={'KYTY_GPU_CHECKPOINTS': '0'}), {}, ['env_exact']),
    ('env_gputime', dict(env={'KYTY_GPU_TIME': '1'}), {}, ['env_exact']),
    ('env_shift', dict(env={'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '0'}), {}, ['env_exact']),
    ('env_wall_missing', dict(env_drop=['KYTY_GPU_WALL']), {}, ['env_exact']),
    ('env_markers_2', dict(env={'KYTY_GPU_MARKERS': '2'}), {}, ['env_exact']),
    ('env_markers_missing', dict(env_drop=['KYTY_GPU_MARKERS']), {}, ['env_exact']),
    ('env_trace_full', dict(env={'KYTY_FRAME_TRACE': '1'}), {}, ['env_exact']),
    ('env_gate_file', dict(env={'KYTY_GATE_FILE': 'C:\\kyty\\s115\\gates.req'}), {}, ['env_exact']),
    ('env_vk_layer', dict(env={'VK_LAYER_PATH': 'C:\\VulkanSDK\\Bin'}), {}, ['env_vk']),
    ('env_vk_instance', dict(env={'VK_INSTANCE_LAYERS': 'VK_LAYER_KHRONOS_validation'}), {}, ['env_vk']),
    ('hold_120', dict(hold_s=120), {}, ['hold']),
    ('hold_missing', dict(hold_s=None), {}, ['hold']),
    ('att_two', dict(atts=[{'outcome': 'ok', 'hold_exit': None, 'stable_frame': STABLE}] * 2), {},
     ['one_ok_attempt']),
    ('att_extra_failed', dict(atts=[{'outcome': 'hang', 'hold_exit': None, 'stable_frame': None},
                                    {'outcome': 'ok', 'hold_exit': None, 'stable_frame': STABLE}]), {},
     ['one_ok_attempt']),
    ('att_exit', dict(atts=[{'outcome': 'ok', 'hold_exit': 3, 'stable_frame': STABLE}]), {}, NO_SCENE),
    ('att_outcome', dict(atts=[{'outcome': 'timeout', 'hold_exit': None, 'stable_frame': None}]), {}, NO_SCENE),
    ('att_none', dict(atts=[]), {}, NO_SCENE),
    ('prereg_other', dict(prereg='C:\\kyty\\s116\\pred\\02_other.md'), {}, ['prereg']),
    ('prereg_missing', dict(prereg=None), {}, ['prereg', 'prereg_sha']),
    ('prereg_sha_other', dict(prereg_sha='cd' * 32), {}, ['prereg_sha']),
    ('prereg_sha_missing', dict(prereg_sha=None), {}, ['prereg_sha']),
    ('prereg_sha_real_mismatch', dict(), dict(pred_sha=None), ['prereg_sha']),
    ('gates_extra', dict(gates=GATES_OK + ' plkstat=1'), {}, ['gates_exact']),
    ('gates_mutsite0', dict(gates=GATES_OK.replace('mutsite=1', 'mutsite=0')), {}, ['gate_mutsite', 'gates_exact']),
    ('gates_mutsite_twice', dict(gates=GATES_OK + ' mutsite=1'), {}, ['gate_mutsite', 'gates_exact']),
    ('gates_pathlap_missing', dict(gates=GATES_OK.replace(' pathlap=1', '')), {}, ['gate_pathlap', 'gates_exact']),
    ('gates_pathlap0', dict(gates=GATES_OK.replace('pathlap=1', 'pathlap=0')), {}, ['gate_pathlap', 'gates_exact']),
    ('gates_pathlap_twice', dict(gates=GATES_OK + ' pathlap=1'), {}, ['gate_pathlap', 'gates_exact']),
    ('gate_lines_none', dict(gate_lines=()), {}, ['gate_lines']),
    ('gate_lines_mutsite_only', dict(gate_lines=GATE_LINES[:1]), {}, ['gate_lines']),
    ('gate_lines_pathlap0', dict(gate_lines=(GATE_LINES[0], 'Gate: pathlap=0 frame=1')), {}, ['gate_lines']),
    ('gate_lines_straddle', dict(lines=['Gate: mutsite=0 frame=%d' % (STABLE + 5)]), {}, ['gate_lines']),
    ('gate_lines_repeated', dict(gate_lines=GATE_LINES + GATE_LINES[:1]), {}, ['gate_lines']),
    ('gate_lines_extra_gate', dict(gate_lines=GATE_LINES + ('Gate: dawalk=0 frame=1',)), {}, ['gate_lines']),
    ('gate_lines_too_long', dict(gate_lines=GATE_LINES + ('Gate: file C:\\kyty\\s116\\gates.req is too long, ignored',)),
     {}, ['gate_lines']),
    ('gate_lines_frame_edge_ok', dict(gate_lines=('Gate: mutsite=1 frame=%d' % (STABLE - 1), GATE_LINES[1])), {}, []),
    ('gate_lines_frame_edge_fail', dict(gate_lines=('Gate: mutsite=1 frame=%d' % STABLE, GATE_LINES[1])), {},
     ['gate_lines']),
    ('wall_none', dict(walls=()), {}, ['wall_logged']),
    ('wall_two', dict(walls=(WALL, WALL)), {}, ['wall_logged']),
    ('wall_mode0', dict(walls=('GpuWall: mode 0',)), {}, ['wall_logged']),
    ('marker_hang', dict(lines=['GpuHangAbort: role=4 tick=9']), {}, ['no_marker']),
    ('marker_waitslow', dict(lines=['GpuWaitSlow: tick=5 us=900000']), {}, ['no_marker']),
    ('marker_hung', dict(lines=['GpuMarkerHung: cs=1']), {}, ['no_marker']),
    ('marker_ckpt', dict(lines=['GpuCheckpointHang: op=1']), {}, ['no_marker']),
    ('marker_devlost', dict(lines=['vkQueueSubmit: ErrorDeviceLost']), {}, ['no_marker']),
    ('marker_terminate', dict(lines=['--- std::terminate ---']), {}, ['no_marker']),
    ('marker_abort', dict(lines=['--- abort() ---']), {}, ['no_marker']),
    ('marker_fatal', dict(lines=['--- Fatal Error ---']), {}, ['no_marker']),
    ('marker_error', dict(lines=['--- Error ---']), {}, ['no_marker']),
    ('marker_skipped', dict(lines=['AsyncPipelines: skipped draw 3']), {}, ['no_marker']),
    ('marker_stdout', dict(stdout='Unhandled exception: 0xC0000005'), {}, ['no_marker']),
    ('rows_drop_us', dict(row_drop={4: ('a_wait_us',)}), {}, ['rows']),
    ('rows_drop_ns', dict(row_drop={5: ('pl_cmd_ns',)}), {}, ['rows']),
    ('rows_drop_count', dict(row_drop={6: ('gw_proc_n',)}), {}, ['rows']),
    ('rows_drop_main', dict(row_drop={7: ('gpu_busy_us',)}), {}, ['rows']),
    ('rows_drop_prio', dict(row_drop={7: ('prio_us',)}), {}, ['rows']),
    ('rows_drop_semwait', dict(row_drop={8: ('semwait_gpu_us',)}), {}, ['rows']),
    ('rows_drop_flip_rsv', dict(row_drop={9: ('flip_rsv_wait_ns',)}), {}, ['rows']),
    ('rows_drop_draw', dict(row_drop={8: ('bda_scan',)}), {}, ['rows']),
    ('rows_skip_main', dict(skip={2: 'main'}), {}, ['rows']),
    ('rows_skip_draw', dict(skip={3: 'draw'}), {}, ['rows']),
    ('rows_skip_x', dict(skip={9: 'x'}), {}, ['rows']),
    ('rows_dup_x', dict(dup=1), {}, ['rows']),
    ('rows_short', dict(rows=SMALL - 1), {}, ['rows']),
    ('rows_missing_extra', dict(rows=SMALL + 1, row_drop={4: ('a_wait_us',)}), {}, ['rows']),   # count ok, 1 missing
    ('rows_dup_extra', dict(rows=SMALL + 1, dup=1), {}, ['rows']),
    ('armed_both_draws', dict(all_over=dict(mh_draws=0, pl_em_n=0)), {}, ['armed']),
    ('armed_mh_draws', dict(all_over=dict(mh_draws=0)), {}, ['armed'] + EMIT),
    ('armed_pl_em', dict(all_over=dict(pl_em_n=0)), {}, ['armed'] + EMIT),
    ('armed_disp', dict(all_over=dict(mh_disp_n=0, a_hold_n=5310)), {}, ['armed']),
    ('armed_disp_id', dict(all_over=dict(mh_disp_n=0)), {}, ['armed', 'id_hold_n']),
    ('armed_proc', dict(all_over=dict(pl_proc_n=0)), {}, ['armed', 'proc_n']),
    ('armed_proc_both', dict(all_over=dict(pl_proc_n=0, gw_proc_n=0)), {}, ['armed']),
    ('armed_wall', dict(all_over=dict(gw_proc_n=0)), {}, ['armed', 'proc_n']),
    ('id_hold_edge_ok', dict(row_over={3: dict(a_hold_n=5596)}), {}, []),
    ('id_hold_edge_fail', dict(row_over={3: dict(a_hold_n=5597)}), {}, ['id_hold_n']),
    ('id_hold_edge_low_ok', dict(row_over={3: dict(a_hold_n=5564)}), {}, []),
    ('id_hold_edge_low_fail', dict(row_over={3: dict(a_hold_n=5563)}), {}, ['id_hold_n']),
    ('id_hold_mh_n', dict(row_over={3: dict(mh_n=5327)}), {}, ['id_hold_n']),
    ('id_hold_disp_n', dict(row_over={3: dict(mh_disp_n=287)}), {}, ['id_hold_n']),
    ('emit_skew_ok', dict(rows=len(SKEW), per_row=[dict(pl_em_n=5290 + s) for s in SKEW]), {}, []),
    ('emit_steady_long', dict(rows=300, all_over=dict(pl_em_n=5291)), {}, EMIT),   # +1 a row: total 300 > 256
    ('emit_edge_ok', dict(row_over={2: dict(pl_em_n=5546)}), {}, []),
    ('emit_edge_fail', dict(row_over={2: dict(pl_em_n=5547)}), {}, ['id_emit_n']),
    ('emit_edge_low_ok', dict(row_over={2: dict(mh_draws=5546)}), {}, []),
    ('emit_edge_low_fail', dict(row_over={2: dict(mh_draws=5547)}), {}, ['id_emit_n']),
    ('proc_n_edge_ok', dict(row_over={3: dict(gw_proc_n=516)}), {}, []),
    ('proc_n_edge_fail', dict(row_over={3: dict(gw_proc_n=517)}), {}, ['proc_n']),
    ('proc_n_hi_ok', dict(row_over={3: dict(pl_proc_n=516)}), {}, []),
    ('proc_n_hi_fail', dict(row_over={3: dict(pl_proc_n=517)}), {}, ['proc_n']),
    ('proc_wall_edge_ok', dict(all_over=dict(gw_proc_ns=30000000, pl_proc_ns=30300000)), {}, []),
    ('proc_wall_edge_fail', dict(all_over=dict(gw_proc_ns=30000000, pl_proc_ns=30300001)), {}, ['proc_wall']),
    ('proc_wall_one_row', dict(row_over={0: dict(pl_proc_ns=33000000)}), {}, []),   # one row above gw_proc, sum in
    ('hold_cover_hi_ok', dict(all_over=dict(a_hold_us=25000, mh_bind_us=9800)), {}, []),
    ('hold_cover_hi_fail', dict(all_over=dict(a_hold_us=25000, mh_bind_us=9801)), {}, ['hold_cover']),
    ('hold_cover_lo_ok', dict(all_over=dict(a_hold_us=25000, mh_bind_us=8800)), {}, []),
    ('hold_cover_lo_fail', dict(all_over=dict(a_hold_us=25000, mh_bind_us=8799)), {}, ['hold_cover']),
    ('hold_cover_zero', dict(all_over=dict(mh_pro_us=0, mh_rt_us=0, mh_prog_us=0, mh_bind_us=0, mh_emit_us=0,
                                           mh_tail_us=0, mh_disp_us=0, a_hold_us=0)), {}, ['hold_cover']),
    ('idle_edge_ok', dict(gpu_util=10), {}, []),
    ('idle_edge_fail', dict(gpu_util=10.5), {}, ['idle']),
    ('idle_none', dict(gpu_util=None), {}, ['idle']),
    ('idle_missing', dict(pre_run=False), {}, ['idle']),
    ('straddle_free', dict(rows=SMALL + 3), {}, []),
    ('edge_rows_ok', dict(rows=EDGE), dict(min_rows=None), []),
    ('edge_rows_fail', dict(rows=EDGE - 1), dict(min_rows=None), ['rows']),
]
ok = True
results = {}
for name, kw, ev, want in cases:
    path = build(name, **kw)
    res = mod.evaluate(path, installed_sha=ev.get('installed', BUILD), min_rows=ev.get('min_rows', SMALL),
                       pred_sha=ev.get('pred_sha', FAKE_SHA))
    results[name] = res
    got = failing(res)
    expect = 'ADMITTED' if not want else 'NOT_ADMITTED'
    passed = got == sorted(want) and res['verdict'] == expect
    ok &= passed
    print('%-28s want %-40s got %-40s %s' % (name, want, got, 'OK' if passed else 'FAIL'))

# ---- the report of the hand-computed log (4 rows, min_rows=4): every expected value below is worked out by hand
# from HAND and the defaults, independently of the scorer's code.  Span keys carry no median.
hand = mod.evaluate(build('HAND', rows=4, per_row=list(HAND)), installed_sha=BUILD, min_rows=4, pred_sha=FAKE_SHA)
passed = hand['verdict'] == 'ADMITTED' and failing(hand) == []
ok &= passed
print('%-28s %s' % ('HAND admitted', 'OK' if passed else 'FAIL %s' % failing(hand)))
R = hand['report'] or {'fields': {}, 'consistency': {}, 'bda': {}, 'predictions': {}}
F = R['fields']
CPU = 124000.0
OPS = 22280.0
NONE = 'None'


def med(key):
    e = F.get(key, {})
    return NONE if 'median' in e and e['median'] is None else e.get('median')


EXPECT = [
    ('n_rows', R.get('n_rows'), 4),
    ('stable_frame', R.get('stable_frame'), STABLE),
    ('span_s', R.get('span_s'), 0.136),
    ('dt_us mean', F.get('dt_us', {}).get('mean'), 34000.0),
    ('dt_us median', med('dt_us'), 33000.0),
    ('dt_us sum', F.get('dt_us', {}).get('sum'), 136000.0),
    ('cpu mean', F.get('cpu_gpu_us', {}).get('mean'), 31000.0),
    ('cpu median', med('cpu_gpu_us'), 30500.0),
    ('cpu share', F.get('cpu_gpu_us', {}).get('share_cpu'), 1.0),
    ('draws mean', F.get('draws', {}).get('mean'), 5300.0),
    ('dispatches median', med('dispatches'), 270.0),
    ('ops mean', F.get('ops', {}).get('mean'), 5570.0),
    ('ops median', med('ops'), 5570.0),
    ('cpu_per_op mean', F.get('cpu_per_op', {}).get('mean'),
     (28000 / 5250 + 30000 / 5470 + 31000 / 5670 + 35000 / 5890) / 4),
    ('cpu_per_op median', med('cpu_per_op'), (31000 / 5670 + 30000 / 5470) / 2),
    ('cpu_per_op sum_ratio', F.get('cpu_per_op', {}).get('sum_ratio'), CPU / OPS),
    ('mh_bind mean', F.get('mh_bind_us', {}).get('mean'), 11000.0),
    ('mh_bind median', med('mh_bind_us'), 10500.0),
    ('mh_bind share', F.get('mh_bind_us', {}).get('share_cpu'), 44000 / CPU),
    ('mh_bind per_op', F.get('mh_bind_us', {}).get('per_op'), 44000 / OPS),
    ('mh_bind per_unit', F.get('mh_bind_us', {}).get('per_unit'), 44000 / 21160),
    ('mh_disp per_unit', F.get('mh_disp_us', {}).get('per_unit'), 1200 / 270),
    ('mh_tail per_unit', F.get('mh_tail_us', {}).get('per_unit'), 100 / 5310),
    ('a_wait per_unit', F.get('a_wait_us', {}).get('per_unit'), 1000 / 22320),
    ('a_hold mean', F.get('a_hold_us', {}).get('mean'), 26750.0),
    ('a_hold median', med('a_hold_us'), 26250.0),
    ('hold mean', F.get('hold', {}).get('mean'), 26700.0),
    ('hold median (mh keys keep it)', med('hold'), 26200.0),
    ('hold per_op', F.get('hold', {}).get('per_op'), 106800 / OPS),
    ('named mean', F.get('named', {}).get('mean'), 780.0),
    ('named median dropped', med('named'), NONE),
    ('named sum', F.get('named', {}).get('sum'), 3120.0),
    ('named share', F.get('named', {}).get('share_cpu'), 3120 / CPU),
    ('units pl_proc mean (ns -> us)', F.get('pl_proc', {}).get('mean'), 31000.0),
    ('pl_proc median dropped', med('pl_proc'), NONE),
    ('pl_proc sum', F.get('pl_proc', {}).get('sum'), 124000.0),
    ('units pl_proc per_unit', F.get('pl_proc', {}).get('per_unit'), 124000 / 2000),
    ('units pl_em_com mean', F.get('pl_em_com', {}).get('mean'), 2200.0),
    ('pl_em_com median dropped', med('pl_em_com'), NONE),
    ('units pl_cmd per_unit', F.get('pl_cmd', {}).get('per_unit'), 500 / 26000),
    ('units pl_look mean', F.get('pl_look', {}).get('mean'), 1.0),
    ('units gw_flip mean', F.get('gw_flip', {}).get('mean'), 1000.0),
    ('gw_flip median dropped', med('gw_flip'), NONE),
    ('gw_flip sum', F.get('gw_flip', {}).get('sum'), 4000.0),
    ('gw_proc mean', F.get('gw_proc', {}).get('mean'), 31100.0),
    ('units gw_idle per_unit', F.get('gw_idle', {}).get('per_unit'), 800 / 20),
    ('units mh_emit kept us', F.get('mh_emit_us', {}).get('mean'), 7000.0),
    ('units a_wait kept us', F.get('a_wait_us', {}).get('mean'), 250.0),
    ('emit_split mean', F.get('emit_split', {}).get('mean'), 6940.0),
    ('emit_split median dropped', med('emit_split'), NONE),
    ('emit_split per_unit', F.get('emit_split', {}).get('per_unit'), 6940 / 5290),
    ('outside mean', F.get('outside', {}).get('mean'), 4000.0),
    ('outside median dropped', med('outside'), NONE),
    ('residue mean', F.get('residue', {}).get('mean'), 3220.0),
    ('residue median dropped', med('residue'), NONE),
    ('residue_noflip mean', F.get('residue_noflip', {}).get('mean'), 2220.0),
    ('residue_s96 mean', F.get('residue_s96', {}).get('mean'), 3770.0),
    ('attributed mean', F.get('attributed', {}).get('mean'), 27730.0),
    ('attributed median dropped', med('attributed'), NONE),
    ('remainder mean', F.get('remainder', {}).get('mean'), 3270.0),
    ('remainder median dropped', med('remainder'), NONE),
    ('remainder sum', F.get('remainder', {}).get('sum'), 13080.0),
    ('remainder share', F.get('remainder', {}).get('share_cpu'), 13080 / CPU),
    ('thread_unwalled mean', F.get('thread_unwalled', {}).get('mean'), 1950.0),
    ('thread_unwalled median dropped', med('thread_unwalled'), NONE),
    ('offcpu mean', F.get('offcpu', {}).get('mean'), 3000.0),
    ('offcpu median (kept)', med('offcpu'), 2500.0),
    ('offcpu_unexplained mean', F.get('offcpu_unexplained', {}).get('mean'), 1100.0),
    ('offcpu_unexplained median dropped', med('offcpu_unexplained'), NONE),
    ('units flip_rsv_wait mean (ns -> us)', F.get('flip_rsv_wait', {}).get('mean'), 2.0),
    ('flip_rsv_wait per_unit', F.get('flip_rsv_wait', {}).get('per_unit'), 1.0),
    ('flip_rsv_wait median dropped', med('flip_rsv_wait'), NONE),
    ('semwait_gpu_us mean', F.get('semwait_gpu_us', {}).get('mean'), 10.0),
    ('semwait_gpu_us sum', F.get('semwait_gpu_us', {}).get('sum'), 40.0),
    ('semwait_gpu_us median dropped', med('semwait_gpu_us'), NONE),
    ('prio_us mean', F.get('prio_us', {}).get('mean'), 19.0),
    ('prio_us per_unit', F.get('prio_us', {}).get('per_unit'), 1.0),
    ('prios median (count kept)', med('prios'), 19.0),
    ('bda median', R['bda'].get('median'), 55.0),
    ('bda label', R['bda'].get('label'), 'NEW'),
    ('hold_over_a_hold', R['consistency'].get('hold_over_a_hold'), 106800 / 107000),
    ('emit_split_over_mh_emit', R['consistency'].get('emit_split_over_mh_emit'), 6940 / 7000),
    ('pl_proc_over_gw_proc', R['consistency'].get('pl_proc_over_gw_proc'), 124000 / 124400),
    ('mh_n_over_draws', R['consistency'].get('mh_n_over_draws'), 21240 / 21200),
    ('mh_disp_n_over_dispatches', R['consistency'].get('mh_disp_n_over_dispatches'), 1.0),
    ('a_hold_n_minus_mh', R['consistency'].get('a_hold_n_minus_mh'), 0.0),
    ('pl_em_n_minus_mh_draws', R['consistency'].get('pl_em_n_minus_mh_draws'), 0.0),
    ('pl_proc_n_minus_gw_proc_n', R['consistency'].get('pl_proc_n_minus_gw_proc_n'), 0.0),
    ('raw pl_proc_ns', hand['raw_totals'].get('pl_proc_ns'), 124000000),
    ('raw gw_proc_ns', hand['raw_totals'].get('gw_proc_ns'), 124400000),
    ('raw a_hold_us', hand['raw_totals'].get('a_hold_us'), 107000),
    ('range mh_rt_us at hi', R['predictions'].get('mh_rt_us'), dict(lo=400, hi=2000, mean=2000.0, in_range=True)),
    ('range mh_disp_us at lo', R['predictions'].get('mh_disp_us'), dict(lo=1200, hi=4000, mean=1200.0, in_range=True)),
    ('range remainder in', (R['predictions'].get('remainder') or {}).get('in_range'), True),
]


def close(a, b):
    if isinstance(b, float) and isinstance(a, (int, float)):
        return abs(a - b) <= 1e-9 * max(1.0, abs(b))
    return a == b


for label, got, want in EXPECT:
    passed = close(got, want)
    ok &= passed
    print('%-36s want %-24s got %-24s %s' % (label, want, got, 'OK' if passed else 'FAIL'))

# ---- the report of the default log: a range outside, the residue inside; totals; the skew case.
D = (results['ADMITTED'].get('report') or {'predictions': {}, 'fields': {}})
MORE = [
    ('default remainder OUT of range', (D['predictions'].get('remainder') or {}).get('in_range'), False),
    ('default remainder mean', (D['predictions'].get('remainder') or {}).get('mean'), 4370.0),
    ('default residue in range', (D['predictions'].get('residue') or {}).get('in_range'), True),
    ('default residue mean', D['fields'].get('residue', {}).get('mean'), 3320.0),
    ('default n_rows', D.get('n_rows'), SMALL),
    ('pre-stable rows ignored (a_hold_n total)', results['ADMITTED']['totals'].get('a_hold_n'), 5580 * SMALL),
    ('skew total +40', (results['emit_skew_ok'].get('report') or {'consistency': {}})['consistency'].get(
        'pl_em_n_minus_mh_draws'), 40.0),
    ('steady +1 total 300', (results['emit_steady_long'].get('report') or {'consistency': {}})['consistency'].get(
        'pl_em_n_minus_mh_draws'), 300.0),
    ('real pred sha read', results['ADMITTED_real_pred'].get('pred_sha256_now'), REAL_PRED_SHA),
    ('vk keys reported', results['env_vk_layer'].get('vk_env'), ['VK_LAYER_PATH', 'VK_SDK_PATH']),
    ('straddle_free n_rows', (results['straddle_free'].get('report') or {}).get('n_rows'), SMALL + 3),
    ('edge_rows_ok n_rows', (results['edge_rows_ok'].get('report') or {}).get('n_rows'), EDGE),
    ('no scene -> no report', results['att_none'].get('report'), None),
    ('bda_label 300', mod.bda_label(300), 'NEW'),
    ('bda_label 301', mod.bda_label(301), 'UNCLEAR'),
    ('bda_label 599', mod.bda_label(599), 'UNCLEAR'),
    ('bda_label 600', mod.bda_label(600), 'OLD'),
    ('bda_label None', mod.bda_label(None), 'UNKNOWN'),
]
for label, got, want in MORE:
    passed = close(got, want)
    ok &= passed
    print('%-36s want %-24s got %-24s %s' % (label, want, got, 'OK' if passed else 'FAIL'))

# ---- the printed report: runs on every shape, never states a speed verdict, flags a NOT_ADMITTED report.
TEXT_A = mod.format_report(results['ADMITTED'])
TEXT_N = mod.format_report(results['armed_proc'])
TEXT_0 = mod.format_report(results['att_none'])
SHAPES = [
    ('text admitted ends', TEXT_A[-1], 'VERDICT: ADMITTED'),
    ('text not admitted ends', TEXT_N[-1], 'VERDICT: NOT_ADMITTED'),
    ('text not admitted flagged', any('NOT TO BE QUOTED' in s for s in TEXT_N), True),
    ('text admitted not flagged', any('NOT TO BE QUOTED' in s for s in TEXT_A), False),
    ('text no scene', any('no complete scene rows' in s for s in TEXT_0), True),
    ('text pl_proc median not printed', [s.split()[2] for s in TEXT_A if s.split()[:1] == ['pl_proc']], ['-']),
    ('text caveat (f) printed', any(s.startswith('  caveat (f)') for s in TEXT_A), True),
    ('text no speed words', any(w in s.lower() for s in TEXT_A for w in ('faster', 'slower', 'speed-up', 'ship')),
     False),
]
for label, got, want in SHAPES:
    passed = got == want
    ok &= passed
    print('%-36s want %-24s got %-24s %s' % (label, want, got, 'OK' if passed else 'FAIL'))

# ---- the chain's gate file is the text this suite (and GATES_SHA) was built from.
GFILE = ' '.join(Path('C:/kyty/s116/gates_obs116.txt').read_text(encoding='utf-8').split())
passed = GFILE == GATES_OK
ok &= passed
print('%-36s %s' % ('gates_obs116.txt == GATES_OK', 'OK' if passed else 'FAIL'))

CONSTANTS = dict(
    ROOT='C:/kyty/s116', TAG='obs116', TAGS=('obs116', 'obs116r'), BUILD_SHA=BUILD,
    INSTALLED='C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe', MIN_ROWS=6000, HOLD_S=300,
    ID_HOLD_TOL=16, ID_EMIT_TOL=256, PROC_N_TOL=16, PROC_WALL_PCT=101, HOLD_COVER_LO_PCT=98, HOLD_COVER_HI_PCT=102,
    IDLE_GPU_MAX=10, GATES_SHA='678fed0972d9a97f53159883ba80eec867c27be4429de325b12f22fa4441aa1b',
    PRED_PATH='C:/kyty/s116/pred/01_obs116.md', BDA_NEW_MAX=300, BDA_OLD_MIN=600,
    ENV_EXPECT={k: v for k, v in ENV_OK.items() if k.startswith('KYTY_')}, VK_ALLOWED=('VK_SDK_PATH',),
    MARKERS=(b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
             b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
             b'asyncpipelines: skipped draw'),
    MAIN_FIELDS=('dt_us', 'cpu_gpu_us', 'draws', 'dispatches', 'gpu_busy_us', 'semwait_gpu_us', 'prio_us', 'prios'),
    DRAW_FIELDS=('bda_scan',),
    US_FIELDS=('mh_pro_us', 'mh_rt_us', 'mh_prog_us', 'mh_bind_us', 'mh_emit_us', 'mh_tail_us', 'mh_disp_us',
               'a_hold_us', 'a_wait_us', 'mh_pres_us', 'mh_pres_wait_us'),
    NS_FIELDS=('pl_proc_ns', 'pl_pref_ns', 'pl_eop_ns', 'pl_bar_ns', 'pl_sub_ns', 'pl_gc_ns', 'pl_cmd_ns',
               'pl_look_ns', 'pl_em_vtx_ns', 'pl_em_rt_ns', 'pl_em_pipe_ns', 'pl_em_com_ns', 'pl_em_rec_ns',
               'pl_em_rest_ns', 'gw_idle_ns', 'gw_blk_ns', 'gw_flip_ns', 'gw_proc_ns', 'gw_cmd_ns',
               'flip_rsv_wait_ns'),
    COUNT_FIELDS=('mh_n', 'mh_draws', 'mh_disp_n', 'a_hold_n', 'mh_pres_n', 'pl_proc_n', 'pl_pref_n', 'pl_eop_n',
                  'pl_bar_n', 'pl_sub_n', 'pl_gc_n', 'pl_cmd_n', 'pl_look_n', 'pl_em_n', 'gw_idle_n', 'gw_blk_n',
                  'gw_flip_n', 'gw_proc_n', 'gw_cmd_n', 'flip_rsv_wait_n'),
    HOLD_PARTS=('mh_pro_us', 'mh_rt_us', 'mh_prog_us', 'mh_bind_us', 'mh_emit_us', 'mh_tail_us', 'mh_disp_us'),
    EMIT_PARTS=('pl_em_vtx', 'pl_em_rt', 'pl_em_pipe', 'pl_em_com', 'pl_em_rec', 'pl_em_rest'),
    NAMED_PARTS=('pl_pref', 'pl_eop', 'pl_bar', 'pl_sub', 'pl_gc', 'pl_cmd'),
    WALL_PARTS=('gw_idle', 'gw_blk', 'gw_proc', 'gw_cmd'),
    SPAN_KEYS=('pl_em_vtx', 'pl_em_rt', 'pl_em_pipe', 'pl_em_com', 'pl_em_rec', 'pl_em_rest', 'emit_split', 'pl_proc',
               'pl_pref', 'pl_eop', 'pl_bar', 'pl_sub', 'pl_gc', 'pl_cmd', 'pl_look', 'gw_idle', 'gw_blk', 'gw_proc',
               'gw_cmd', 'gw_flip', 'named', 'outside', 'residue', 'residue_noflip', 'residue_s96', 'attributed',
               'remainder', 'thread_unwalled', 'offcpu_unexplained', 'flip_rsv_wait', 'semwait_gpu_us', 'prio_us'),
    PREDICTIONS={'dt_us': (29000, 40000), 'cpu_gpu_us': (28000, 38000), 'draws': (4500, 6000),
                 'dispatches': (240, 300), 'cpu_per_op': (5.0, 7.5), 'a_hold_us': (22000, 34000),
                 'mh_bind_us': (6000, 14000), 'mh_emit_us': (5000, 10000), 'mh_prog_us': (2500, 7500),
                 'mh_disp_us': (1200, 4000), 'mh_rt_us': (400, 2000), 'emit_split': (5000, 10000),
                 'pl_pref': (0, 400), 'named': (300, 3000), 'residue': (0, 4000), 'remainder': (-2000, 4000),
                 'offcpu': (0, 4000)})
differ = [k for k, v in CONSTANTS.items() if getattr(mod, k, None) != v]
passed = not differ
ok &= passed
print('%-36s %s %s' % ('CONSTANTS', differ or 'match', 'OK' if passed else 'FAIL'))
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
