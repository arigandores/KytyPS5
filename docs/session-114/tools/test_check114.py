"""Session 114: fixtures for check114.py (from test_check113.py by make_check114.py) - PASS, every check failing
alone (video and boot), and both sides of every threshold.
    python test_check114.py <check114.py>
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_check114')
NL = chr(10)
spec = importlib.util.spec_from_file_location('check114', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
GATES = 'dawalk=1 smemocheck=0 dabatch=8 fslean=0'
GC_OK = 'BufferGc: budget=14901313536 trigger=9747352781 critical=13183326618 shift_mb=0'


def write_boot(d, rows=3000, env=None, env_drop=(), atts=None, binary=None, pins=('GpuClockPin: mode 1',),
               holds=('PrepareHold: ms=10000',), waits=(10240,), lines=(), stdout=None, gates=GATES, overlap=0,
               drop_field=False, gpu_util=0.0, progress=tuple(range(0, 10001, 1000)), park=(10200000,),
               park_before=False):
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_PREPARE_HOLD_MS': '10000'}
    e.update(env or {})
    for k in env_drop:
        e.pop(k, None)
    meta = {'binary_sha256': binary or mod.BUILD_SHA, 'env': e, 'gates': gates, 'pre_run': {'gpu_util_median': gpu_util},
            'attempts': atts if atts is not None else [{'outcome': 'ok', 'hold_exit': None, 'stable_frame': 900}]}
    (d / (mod.BOOT_TAG + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    late = ['MainTaskLate: us=%d' % x for x in park]
    out = list(pins) + list(holds) + (late if park_before else [])
    out += ['ShaderPreparation: progress 682/682 skipped=41 elapsed_ms=%d' % ms for ms in progress]
    out += ['ShaderPreparation: startup wait finished in %d ms' % w for w in waits]
    out += ([] if park_before else late) + list(lines)
    for n in range(1, rows + 1):
        f = 'pres_title_n=1 present_overlap=%d' % (overlap if n == 40 else 0)
        if drop_field and n == 50:
            f = f.replace('present_overlap=', 'present_overlaX=')
        out.append('FrameTrace-x: n=%d rt_att=100 %s' % (n, f))
    (d / ('log_%s.txt' % mod.BOOT_TAG)).write_bytes((NL.join(out) + NL).encode('utf-8'))
    if stdout is not None:
        (d / ('stdout_%s.txt' % mod.BOOT_TAG)).write_bytes((stdout + NL).encode('utf-8'))


def make(name, rows=3700, stable=280, frames=4000, glitches=0, gates=GATES, env=None, env_drop=(), atts=None,
         binary=None, installed=None, pins=('GpuClockPin: mode 1',), lines=(), stdout=None, free=1100, noguard=0,
         slot_bad=0, hit=266, free_bad=0, sync_new=0, drop_field=False, glitch_text=None, nskip=0, would=0,
         gc=(GC_OK,), title_ns=22000, title_n=1, overlap=0, drop_title=False, boot=None, vid_gpu=0.0):
    d = BASE / name
    d.mkdir()
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_REC': 'x.mp4'}
    e.update(env or {})
    for k in env_drop:
        e.pop(k, None)
    meta = {'binary_sha256': binary or mod.BUILD_SHA, 'env': e, 'gates': gates, 'pre_run': {'gpu_util_median': vid_gpu},
            'attempts': atts if atts is not None else [{'outcome': 'ok', 'hold_exit': None, 'stable_frame': stable}]}
    (d / (mod.TAG + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    (d / (mod.TAG + '_glitch.txt')).write_text(
        glitch_text if glitch_text is not None else 'video %d frames' % frames + NL +
        'one-frame glitches: %d' % glitches + NL, encoding='utf-8')
    out = list(pins) + list(gc) + list(lines)
    for n in range(1, stable + rows):
        f = ('cspfree_hit=%d cspfree_bad=%d cs_sync_new=%d cs_sync_wait=0 da_q_free=%d da_q_noguard=%d '
             'da_slot_bad=%d da_guard_yield=0') % (hit, free_bad if n == stable + 5 else 0,
                                                   sync_new if n == stable + 7 else 0, free,
                                                   noguard if n == stable + 9 else 0,
                                                   slot_bad if n == stable + 11 else 0)
        f += ' bda_nskip=%d bda_nwould=%d prio_stall=0 prio_unsub=5' % (nskip if n == stable + 13 else 0,
                                                                       would if n == stable + 15 else 0)
        f += ' pres_title_ns=%d pres_title_n=%d present_overlap=%d' % (title_ns, title_n,
                                                                       overlap if n == stable + 17 else 0)
        if drop_field and n == stable + 20:
            f = f.replace('da_q_noguard=', 'da_q_noguarX=')
        if drop_title and n == stable + 21:
            f = f.replace('pres_title_n=', 'pres_title_X=')
        out.append('FrameTrace-x: n=%d rt_att=100 %s' % (n, f))
    (d / ('log_%s.txt' % mod.TAG)).write_bytes((NL.join(out) + NL).encode('utf-8'))
    if stdout is not None:
        (d / ('stdout_%s.txt' % mod.TAG)).write_bytes((stdout + NL).encode('utf-8'))
    write_boot(d, **(boot or {}))
    return mod.evaluate_all(str(d), installed_sha=installed or mod.BUILD_SHA)


def failing(res):
    return sorted(k for k, v in res['checks'].items() if not v)


cases = [
    ('PASS', dict(), []),
    ('PASS_stdout_clean', dict(stdout='0xe06d7363 C++ exception (not a marker)'), []),
    ('PASS_pre_stable_bad', dict(lines=['FrameTrace-x: n=10 da_slot_bad=5 da_q_noguard=9']), []),  # before the scene
    ('binary', dict(binary='1' * 64), ['binary']),
    ('installed', dict(installed='0' * 64), ['installed_now']),
    ('pin_env', dict(env_drop=['KYTY_GPU_CLOCK_PIN']), ['pinned']),
    ('pin_none', dict(pins=()), ['pinned']),
    ('pin_two', dict(pins=('GpuClockPin: mode 1', 'GpuClockPin: mode 1')), ['pinned']),
    ('pin_mode2', dict(pins=('GpuClockPin: mode 2',)), ['pinned']),
    ('recorded', dict(env_drop=['KYTY_REC']), ['recorded']),
    ('schedule', dict(env={'KYTY_GATE_SCHEDULE': 'x'}), ['no_schedule']),
    ('checkpoints', dict(env={'KYTY_GPU_CHECKPOINTS': '0'}), ['no_checkpoints']),
    ('att_two', dict(atts=[{'outcome': 'ok', 'hold_exit': None, 'stable_frame': 280}] * 2), ['one_ok_attempt']),
    ('att_extra_failed', dict(atts=[{'outcome': 'hang', 'hold_exit': None, 'stable_frame': 280},
                                    {'outcome': 'ok', 'hold_exit': None, 'stable_frame': 280}]), ['one_ok_attempt']),
    ('att_exit', dict(atts=[{'outcome': 'ok', 'hold_exit': 3, 'stable_frame': 280}]),
     ['free_default_armed', 'one_ok_attempt', 'rows', 'slot_default_armed', 'title_default_on']),   # no scene rows
    ('att_outcome', dict(atts=[{'outcome': 'hang', 'hold_exit': None, 'stable_frame': 280}]),
     ['free_default_armed', 'one_ok_attempt', 'rows', 'slot_default_armed', 'title_default_on']),
    ('gate_daslot', dict(gates=GATES + ' daslot=1'), ['default_runs']),
    ('gate_daguard', dict(gates=GATES + ' daguard=1'), ['default_runs']),
    ('gate_cspfree', dict(gates=GATES + ' cspfree=1'), ['default_runs']),
    ('gate_bdanarrow', dict(gates=GATES + ' bdanarrow=0'), ['default_runs']),
    ('shift', dict(env={'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '0'}), ['no_shift']),
    ('narrow_skip', dict(nskip=1), ['narrow_default_dark']),
    ('narrow_would', dict(would=1), ['narrow_default_dark']),
    ('gc_none', dict(gc=()), ['gc_default']),
    ('gc_two', dict(gc=(GC_OK, GC_OK)), ['gc_default']),
    ('gc_shift', dict(gc=(GC_OK.replace('shift_mb=0', 'shift_mb=1024'),)), ['gc_default']),
    ('gc_shift_10', dict(gc=(GC_OK.replace('shift_mb=0', 'shift_mb=10'),)), ['gc_default']),
    ('frames_edge_fail', dict(frames=2999), ['frames']),
    ('frames_edge_ok', dict(frames=3000), []),
    ('frames_missing', dict(glitch_text='one-frame glitches: 0' + NL), ['frames']),
    ('glitch', dict(glitches=1), ['no_glitch']),
    ('glitch_missing', dict(glitch_text='video 4000 frames' + NL), ['no_glitch']),
    ('rows_edge_fail', dict(rows=999), ['rows']),
    ('rows_edge_ok', dict(rows=1000), []),
    ('rows_field', dict(drop_field=True), ['rows']),
    ('slot_free', dict(free=0), ['slot_default_armed']),
    ('slot_noguard', dict(noguard=1), ['slot_default_armed']),
    ('slot_bad', dict(slot_bad=1), ['slot_no_bad']),
    ('free_hit', dict(hit=0), ['free_default_armed']),
    ('free_bad', dict(free_bad=1), ['free_default_armed']),
    ('guard', dict(sync_new=1), ['guard']),
    ('marker_log', dict(lines=['GpuHangAbort: role=4']), ['no_marker']),
    ('marker_fatal', dict(lines=['--- Fatal Error ---']), ['no_marker']),
    ('marker_skipped', dict(lines=['AsyncPipelines: skipped draw 3']), ['no_marker']),
    ('marker_stdout', dict(stdout='Unhandled exception: 0xC0000005'), ['no_marker']),
    ('gate_titleasync', dict(gates=GATES + ' titleasync=1'), ['no_title_knob']),
    ('gate_titleasync0', dict(gates=GATES + ' titleasync=0'), ['no_title_knob']),
    ('hold_env', dict(env={'KYTY_PREPARE_HOLD_MS': '10000'}), ['no_hold']),
    ('title_zero', dict(title_n=0, title_ns=0), ['title_default_on']),
    ('title_edge_ok', dict(title_ns=60000), []),
    ('title_edge_fail', dict(title_ns=60001), ['title_default_on']),
    ('title_wait', dict(title_ns=168468), ['title_default_on']),
    ('title_field', dict(drop_title=True), ['rows']),
    ('overlap_row', dict(overlap=1), ['no_overlap']),
    ('overlap_line', dict(lines=['PresentOverlap: thread=12345']), ['no_overlap']),
    ('boot_binary', dict(boot=dict(binary='1' * 64)), ['boot_binary']),
    ('boot_pin_env', dict(boot=dict(env_drop=['KYTY_GPU_CLOCK_PIN'])), ['boot_pinned']),
    ('boot_pin_none', dict(boot=dict(pins=())), ['boot_pinned']),
    ('boot_pin_two', dict(boot=dict(pins=('GpuClockPin: mode 1', 'GpuClockPin: mode 1'))), ['boot_pinned']),
    ('boot_pin_mode2', dict(boot=dict(pins=('GpuClockPin: mode 2',))), ['boot_pinned']),
    ('boot_hold_env_none', dict(boot=dict(env_drop=['KYTY_PREPARE_HOLD_MS'])), ['boot_hold_env']),
    ('boot_hold_env_5000', dict(boot=dict(env={'KYTY_PREPARE_HOLD_MS': '5000'})), ['boot_hold_env']),
    ('boot_schedule', dict(boot=dict(env={'KYTY_GATE_SCHEDULE': 'x'})), ['boot_no_schedule']),
    ('boot_checkpoints', dict(boot=dict(env={'KYTY_GPU_CHECKPOINTS': '0'})), ['boot_no_checkpoints']),
    ('boot_shift', dict(boot=dict(env={'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '0'})), ['boot_no_shift']),
    ('boot_att_two', dict(boot=dict(atts=[{'outcome': 'ok', 'hold_exit': None}] * 2)), ['boot_one_ok_attempt']),
    ('boot_att_outcome', dict(boot=dict(atts=[{'outcome': 'hang', 'hold_exit': None}])), ['boot_one_ok_attempt']),
    ('boot_att_exit', dict(boot=dict(atts=[{'outcome': 'ok', 'hold_exit': 3}])), ['boot_one_ok_attempt']),
    ('boot_att_none', dict(boot=dict(atts=[])), ['boot_one_ok_attempt']),
    ('boot_att_extra_failed', dict(boot=dict(atts=[{'outcome': 'hang', 'hold_exit': None},                                                  {'outcome': 'ok', 'hold_exit': None}])), ['boot_one_ok_attempt']),
    ('boot_gate_daslot', dict(boot=dict(gates=GATES + ' daslot=1')), ['boot_default_runs']),
    ('boot_gate_daguard', dict(boot=dict(gates=GATES + ' daguard=1')), ['boot_default_runs']),
    ('boot_gate_cspfree', dict(boot=dict(gates=GATES + ' cspfree=1')), ['boot_default_runs']),
    ('boot_gate_bdanarrow', dict(boot=dict(gates=GATES + ' bdanarrow=0')), ['boot_default_runs']),
    ('boot_gate_titleasync', dict(boot=dict(gates=GATES + ' titleasync=1')), ['boot_default_runs']),
    ('boot_hold_none', dict(boot=dict(holds=())), ['boot_hold_logged']),
    ('boot_hold_two', dict(boot=dict(holds=('PrepareHold: ms=10000',) * 2)), ['boot_hold_logged']),
    ('boot_hold_5000', dict(boot=dict(holds=('PrepareHold: ms=5000',))), ['boot_hold_logged']),
    ('boot_wait_edge_fail', dict(boot=dict(waits=(9999,))), ['boot_wait']),
    ('boot_wait_edge_ok', dict(boot=dict(waits=(10000,))), []),
    ('boot_wait_warm', dict(boot=dict(waits=(70,))), ['boot_wait']),
    ('boot_wait_none', dict(boot=dict(waits=())), ['adm_boot_parked', 'boot_wait']),
    ('boot_wait_two', dict(boot=dict(waits=(10240, 10240))), ['boot_wait']),
    ('boot_rows_edge_fail', dict(boot=dict(rows=999)), ['boot_rows']),
    ('boot_rows_edge_ok', dict(boot=dict(rows=1000)), []),
    ('boot_rows_field', dict(boot=dict(drop_field=True)), ['boot_rows']),
    ('boot_overlap_line', dict(boot=dict(lines=['PresentOverlap: thread=12345'])), ['boot_no_overlap']),
    ('boot_overlap_sum', dict(boot=dict(overlap=1)), ['boot_no_overlap']),
    ('boot_marker_log', dict(boot=dict(lines=['GpuHangAbort: role=4'])), ['boot_no_marker']),
    ('boot_marker_stdout', dict(boot=dict(stdout='Unhandled exception: 0xC0000005')), ['boot_no_marker']),
    ('boot_stdout_clean', dict(boot=dict(stdout='0xe06d7363 C++ exception (not a marker)')), []),
    ('both_fail', dict(glitches=1, boot=dict(waits=(70,))), ['boot_wait', 'no_glitch']),
    ('marker_waitslow', dict(lines=['GpuWaitSlow: tick=5 us=900000']), ['no_marker']),
    ('marker_devlost', dict(lines=['vkQueueSubmit: ErrorDeviceLost']), ['no_marker']),
    ('marker_terminate', dict(lines=['--- std::terminate ---']), ['no_marker']),
    ('marker_abort', dict(lines=['--- abort() ---']), ['no_marker']),
    ('marker_error', dict(lines=['--- Error ---']), ['no_marker']),
    ('marker_hung', dict(lines=['GpuMarkerHung: cs=1']), ['no_marker']),
    ('marker_ckpt', dict(lines=['GpuCheckpointHang: op=1']), ['no_marker']),
    ('overlap_midline', dict(lines=['[7][00:00:01.000] x PresentOverlap: thread=1']), ['no_overlap']),
    ('boot_overlap_midline', dict(boot=dict(lines=['[7] x PresentOverlap: thread=1'])), ['boot_no_overlap']),
    ('boot_marker_terminate', dict(boot=dict(lines=['--- std::terminate ---'])), ['boot_no_marker']),
    ('adm_idle_vid', dict(vid_gpu=10.5), ['adm_idle_vid']),
    ('adm_idle_vid_edge', dict(vid_gpu=10), []),
    ('adm_idle_vid_none', dict(vid_gpu=None), ['adm_idle_vid']),
    ('adm_idle_boot', dict(boot=dict(gpu_util=11)), ['adm_idle_boot']),
    ('adm_idle_boot_edge', dict(boot=dict(gpu_util=10.0)), []),
    ('adm_park_short', dict(boot=dict(park=(9999999,))), ['adm_boot_parked']),
    ('adm_park_edge', dict(boot=dict(park=(10000000,))), []),
    ('adm_park_none', dict(boot=dict(park=())), ['adm_boot_parked']),
    ('adm_park_before_wait', dict(boot=dict(park_before=True)), ['adm_boot_parked']),
    ('adm_park_first_only', dict(boot=dict(park=(300000, 10200000))), ['adm_boot_parked']),
    ('adm_park_later_long', dict(boot=dict(park=(10200000, 300000))), []),
    ('adm_prog_count', dict(boot=dict(progress=(0, 9000))), ['adm_boot_parked']),
    ('adm_prog_count_edge', dict(boot=dict(progress=tuple(range(1000, 9001, 1000)))), []),
    ('adm_prog_ms', dict(boot=dict(progress=tuple(range(0, 8001, 800)))), ['adm_boot_parked']),
    ('adm_prog_ms_edge', dict(boot=dict(progress=tuple(range(0, 9001, 900)))), []),
    ('adm_and_fail', dict(glitches=1, boot=dict(park=())), ['adm_boot_parked', 'no_glitch']),
]
ok = True
for name, kw, want in cases:
    res = make(name, **kw)
    got = failing(res)
    expect = 'PASS' if not want else ('NOT_ADMITTED' if any(w.startswith('adm_') for w in want) else 'FAIL')
    passed = got == sorted(want) and res['verdict'] == expect
    ok &= passed
    print('%-20s want %-40s got %-40s %s' % (name, want, got, 'OK' if passed else 'FAIL'))
CONSTANTS = dict(TAG='vid114', BOOT_TAG='boot114', MIN_FRAMES=3000, MIN_ROWS=1000, TITLE_WALL_MAX_NS=60000,
                 HOLD_MS=10000, BOOT_DEFAULTS=('daslot', 'daguard', 'cspfree', 'bdanarrow', 'titleasync'),
                 IDLE_GPU_MAX=10, PROG_MIN_LINES=9, PROG_MIN_MS=9000,
                 BUILD_SHA='8d7ba8f4ae995a3da10670a095670acf0c46450675f7b61137714eb7975956ec')
differ = [k for k, v in CONSTANTS.items() if getattr(mod, k) != v]
print('%-20s %s %s' % ('CONSTANTS', differ or 'match', 'OK' if not differ else 'FAIL'))
ok &= not differ
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
