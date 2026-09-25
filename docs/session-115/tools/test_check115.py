"""Session 115: fixtures for check115.py (from the sealed test_check114.py by make_check115.py) - PASS, every check
failing alone (video, the fix boots a/c, the control b), and both sides of every threshold.
    python test_check115.py <check115.py>
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_check115')
NL = chr(10)
spec = importlib.util.spec_from_file_location('check115', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
GATES = 'dawalk=1 smemocheck=0 dabatch=8 fslean=0'
GC_OK = 'BufferGc: budget=14901313536 trigger=9747352781 critical=13183326618 shift_mb=0'
FATAL = 'Error: condition (m_producer != self || m_open_slot != nullptr) is true in C:\\kyty\\x\\commandRecorder.cpp:326'
W = 'ShaderPreparation: startup wait finished in %d ms presents_other=%d presents_main=%d'


def write_boot(d, tag, env=None, env_drop=(), atts=None, binary=None, pins=None,
               holds=('PrepareHold: ms=10000',), waits=None, mains=None, lines=None, stdout=None, gates=GATES,
               gpu_util=0.0):
    control = tag == mod.BOOT_CONTROL
    if pins is None:
        pins = () if control else ('GpuClockPin: mode 1',)
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_PREPARE_HOLD_MS': '10000'}
    if control:
        e['KYTY_PREPARE_MAIN_PRESENT'] = '1'
    if tag == mod.BOOT_SHIP:
        e['KYTY_TITLE_ASYNC'] = '1'
    e.update(env or {})
    for k in env_drop:
        e.pop(k, None)
    if atts is None:
        atts = [{'outcome': 'fail' if control else 'ok', 'hold_exit': None, 'stable_frame': 900}]
    meta = {'binary_sha256': binary or mod.BUILD_SHA, 'env': e, 'gates': gates, 'pre_run': {'gpu_util_median': gpu_util},
            'attempts': atts}
    (d / (tag + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    if waits is None:
        waits = () if control else ('ShaderPreparation: startup wait finished in 10016 ms presents_other=601 '
                                    'presents_main=0',)
    if mains is None:
        mains = ('PrepareMainPresent: mode 1',) if control else ()
    if lines is None:
        lines = ('--- Fatal Error ---', FATAL) if control else ('FrameTrace-x: n=1 present_overlap=0',)
    out = list(pins) + list(holds) + list(mains) + list(waits) + list(lines)
    (d / ('log_%s.txt' % tag)).write_bytes((NL.join(out) + NL).encode('utf-8'))
    if stdout is not None:
        (d / ('stdout_%s.txt' % tag)).write_bytes((stdout + NL).encode('utf-8'))


def make(name, rows=3700, stable=280, frames=4000, glitches=0, gates=GATES, env=None, env_drop=(), atts=None,
         binary=None, installed=None, pins=('GpuClockPin: mode 1',), lines=(), stdout=None, free=1100, noguard=0,
         slot_bad=0, hit=266, free_bad=0, sync_new=0, drop_field=False, glitch_text=None, nskip=0, would=0,
         gc=(GC_OK,), title_ns=22000, title_n=1, overlap=0, drop_title=False, boots=None, vid_gpu=0.0):
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
    for tag in mod.BOOT_TAGS:
        write_boot(d, tag, **((boots or {}).get(tag) or {}))
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
    ('marker_waitslow', dict(lines=['GpuWaitSlow: tick=5 us=900000']), ['no_marker']),
    ('marker_devlost', dict(lines=['vkQueueSubmit: ErrorDeviceLost']), ['no_marker']),
    ('marker_terminate', dict(lines=['--- std::terminate ---']), ['no_marker']),
    ('marker_abort', dict(lines=['--- abort() ---']), ['no_marker']),
    ('marker_error', dict(lines=['--- Error ---']), ['no_marker']),
    ('marker_hung', dict(lines=['GpuMarkerHung: cs=1']), ['no_marker']),
    ('marker_ckpt', dict(lines=['GpuCheckpointHang: op=1']), ['no_marker']),
    ('overlap_midline', dict(lines=['[7][00:00:01.000] x PresentOverlap: thread=1']), ['no_overlap']),
    ('adm_idle_vid', dict(vid_gpu=10.5), ['adm_idle_vid']),
    ('adm_idle_vid_edge', dict(vid_gpu=10), []),
    ('adm_idle_vid_none', dict(vid_gpu=None), ['adm_idle_vid']),
    ('a_binary', dict(boots={'boot115a': dict(binary='1' * 64)}), ['a_binary']),
    ('a_pin_env', dict(boots={'boot115a': dict(env_drop=['KYTY_GPU_CLOCK_PIN'])}), ['a_pinned']),
    ('a_pin_none', dict(boots={'boot115a': dict(pins=())}), ['a_pinned']),
    ('a_pin_two', dict(boots={'boot115a': dict(pins=('GpuClockPin: mode 1',) * 2)}), ['a_pinned']),
    ('a_pin_mode2', dict(boots={'boot115a': dict(pins=('GpuClockPin: mode 2',))}), ['a_pinned']),
    ('a_hold_env_none', dict(boots={'boot115a': dict(env_drop=['KYTY_PREPARE_HOLD_MS'])}), ['a_hold_env']),
    ('a_hold_env_5000', dict(boots={'boot115a': dict(env={'KYTY_PREPARE_HOLD_MS': '5000'})}), ['a_hold_env']),
    ('a_schedule', dict(boots={'boot115a': dict(env={'KYTY_GATE_SCHEDULE': 'x'})}), ['a_no_schedule']),
    ('a_checkpoints', dict(boots={'boot115a': dict(env={'KYTY_GPU_CHECKPOINTS': '0'})}), ['a_no_checkpoints']),
    ('a_shift', dict(boots={'boot115a': dict(env={'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '0'})}), ['a_no_shift']),
    ('a_main_env', dict(boots={'boot115a': dict(env={'KYTY_PREPARE_MAIN_PRESENT': '1'})}), ['a_main_env']),
    ('a_att_two', dict(boots={'boot115a': dict(atts=[{'outcome': 'ok', 'hold_exit': None}] * 2)}), ['a_one_ok_attempt']),
    ('a_att_outcome', dict(boots={'boot115a': dict(atts=[{'outcome': 'hang', 'hold_exit': None}])}), ['a_one_ok_attempt']),
    ('a_att_exit', dict(boots={'boot115a': dict(atts=[{'outcome': 'ok', 'hold_exit': 3}])}), ['a_one_ok_attempt']),
    ('a_att_none', dict(boots={'boot115a': dict(atts=[])}), ['a_one_ok_attempt']),
    ('a_att_extra', dict(boots={'boot115a': dict(atts=[{'outcome': 'hang', 'hold_exit': None}, {'outcome': 'ok', 'hold_exit': None}])}), ['a_one_ok_attempt']),
    ('a_hold_none', dict(boots={'boot115a': dict(holds=())}), ['a_hold_logged']),
    ('a_hold_two', dict(boots={'boot115a': dict(holds=('PrepareHold: ms=10000',) * 2)}), ['a_hold_logged']),
    ('a_hold_5000', dict(boots={'boot115a': dict(holds=('PrepareHold: ms=5000',))}), ['a_hold_logged']),
    ('a_wait_edge_fail', dict(boots={'boot115a': dict(waits=(W % (9999, 601, 0),))}), ['a_wait']),
    ('a_wait_edge_ok', dict(boots={'boot115a': dict(waits=(W % (10000, 601, 0),))}), []),
    ('a_wait_none', dict(boots={'boot115a': dict(waits=())}), ['a_presents_main', 'a_presents_other', 'a_wait']),
    ('a_wait_two', dict(boots={'boot115a': dict(waits=(W % (10016, 601, 0),) * 2)}), ['a_presents_main', 'a_presents_other', 'a_wait']),
    ('a_wait_old_format', dict(boots={'boot115a': dict(waits=('ShaderPreparation: startup wait finished in 10016 ms',))}), ['a_presents_main', 'a_presents_other']),
    ('a_pmain_1', dict(boots={'boot115a': dict(waits=(W % (10016, 601, 1),))}), ['a_presents_main']),
    ('a_pother_edge_fail', dict(boots={'boot115a': dict(waits=(W % (10016, 299, 0),))}), ['a_presents_other']),
    ('a_pother_edge_ok', dict(boots={'boot115a': dict(waits=(W % (10016, 300, 0),))}), []),
    ('a_main_line', dict(boots={'boot115a': dict(mains=('PrepareMainPresent: mode 1',))}), ['a_no_main_line']),
    ('a_fatal', dict(boots={'boot115a': dict(lines=(FATAL,))}), ['a_no_fatal']),
    ('a_overlap', dict(boots={'boot115a': dict(lines=('PresentOverlap: thread=1',))}), ['a_no_overlap']),
    ('a_overlap_midline', dict(boots={'boot115a': dict(lines=('[7] x PresentOverlap: thread=1',))}), ['a_no_overlap']),
    ('a_marker_log', dict(boots={'boot115a': dict(lines=('GpuHangAbort: role=4',))}), ['a_no_marker']),
    ('a_marker_stdout', dict(boots={'boot115a': dict(stdout='Unhandled exception: 0xC0000005')}), ['a_no_marker']),
    ('a_stdout_clean', dict(boots={'boot115a': dict(stdout='0xe06d7363 C++ exception (not a marker)')}), []),
    ('a_idle', dict(boots={'boot115a': dict(gpu_util=10.5)}), ['adm_idle_a']),
    ('a_idle_edge', dict(boots={'boot115a': dict(gpu_util=10)}), []),
    ('a_gate_daslot', dict(boots={'boot115a': dict(gates=GATES + ' daslot=1')}), ['a_default_runs']),
    ('a_gate_daguard', dict(boots={'boot115a': dict(gates=GATES + ' daguard=1')}), ['a_default_runs']),
    ('a_gate_cspfree', dict(boots={'boot115a': dict(gates=GATES + ' cspfree=1')}), ['a_default_runs']),
    ('a_gate_bdanarrow', dict(boots={'boot115a': dict(gates=GATES + ' bdanarrow=1')}), ['a_default_runs']),
    ('a_gate_titleasync', dict(boots={'boot115a': dict(gates=GATES + ' titleasync=1')}), ['a_default_runs']),
    ('c_binary', dict(boots={'boot115c': dict(binary='1' * 64)}), ['c_binary']),
    ('c_pin_env', dict(boots={'boot115c': dict(env_drop=['KYTY_GPU_CLOCK_PIN'])}), ['c_pinned']),
    ('c_pin_none', dict(boots={'boot115c': dict(pins=())}), ['c_pinned']),
    ('c_pin_two', dict(boots={'boot115c': dict(pins=('GpuClockPin: mode 1',) * 2)}), ['c_pinned']),
    ('c_pin_mode2', dict(boots={'boot115c': dict(pins=('GpuClockPin: mode 2',))}), ['c_pinned']),
    ('c_hold_env_none', dict(boots={'boot115c': dict(env_drop=['KYTY_PREPARE_HOLD_MS'])}), ['c_hold_env']),
    ('c_hold_env_5000', dict(boots={'boot115c': dict(env={'KYTY_PREPARE_HOLD_MS': '5000'})}), ['c_hold_env']),
    ('c_schedule', dict(boots={'boot115c': dict(env={'KYTY_GATE_SCHEDULE': 'x'})}), ['c_no_schedule']),
    ('c_checkpoints', dict(boots={'boot115c': dict(env={'KYTY_GPU_CHECKPOINTS': '0'})}), ['c_no_checkpoints']),
    ('c_shift', dict(boots={'boot115c': dict(env={'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '0'})}), ['c_no_shift']),
    ('c_main_env', dict(boots={'boot115c': dict(env={'KYTY_PREPARE_MAIN_PRESENT': '1'})}), ['c_main_env']),
    ('c_att_two', dict(boots={'boot115c': dict(atts=[{'outcome': 'ok', 'hold_exit': None}] * 2)}), ['c_one_ok_attempt']),
    ('c_att_outcome', dict(boots={'boot115c': dict(atts=[{'outcome': 'hang', 'hold_exit': None}])}), ['c_one_ok_attempt']),
    ('c_att_exit', dict(boots={'boot115c': dict(atts=[{'outcome': 'ok', 'hold_exit': 3}])}), ['c_one_ok_attempt']),
    ('c_att_none', dict(boots={'boot115c': dict(atts=[])}), ['c_one_ok_attempt']),
    ('c_att_extra', dict(boots={'boot115c': dict(atts=[{'outcome': 'hang', 'hold_exit': None}, {'outcome': 'ok', 'hold_exit': None}])}), ['c_one_ok_attempt']),
    ('c_hold_none', dict(boots={'boot115c': dict(holds=())}), ['c_hold_logged']),
    ('c_hold_two', dict(boots={'boot115c': dict(holds=('PrepareHold: ms=10000',) * 2)}), ['c_hold_logged']),
    ('c_hold_5000', dict(boots={'boot115c': dict(holds=('PrepareHold: ms=5000',))}), ['c_hold_logged']),
    ('c_wait_edge_fail', dict(boots={'boot115c': dict(waits=(W % (9999, 601, 0),))}), ['c_wait']),
    ('c_wait_edge_ok', dict(boots={'boot115c': dict(waits=(W % (10000, 601, 0),))}), []),
    ('c_wait_none', dict(boots={'boot115c': dict(waits=())}), ['c_presents_main', 'c_presents_other', 'c_wait']),
    ('c_wait_two', dict(boots={'boot115c': dict(waits=(W % (10016, 601, 0),) * 2)}), ['c_presents_main', 'c_presents_other', 'c_wait']),
    ('c_wait_old_format', dict(boots={'boot115c': dict(waits=('ShaderPreparation: startup wait finished in 10016 ms',))}), ['c_presents_main', 'c_presents_other']),
    ('c_pmain_1', dict(boots={'boot115c': dict(waits=(W % (10016, 601, 1),))}), ['c_presents_main']),
    ('c_pother_edge_fail', dict(boots={'boot115c': dict(waits=(W % (10016, 299, 0),))}), ['c_presents_other']),
    ('c_pother_edge_ok', dict(boots={'boot115c': dict(waits=(W % (10016, 300, 0),))}), []),
    ('c_main_line', dict(boots={'boot115c': dict(mains=('PrepareMainPresent: mode 1',))}), ['c_no_main_line']),
    ('c_fatal', dict(boots={'boot115c': dict(lines=(FATAL,))}), ['c_no_fatal']),
    ('c_overlap', dict(boots={'boot115c': dict(lines=('PresentOverlap: thread=1',))}), ['c_no_overlap']),
    ('c_overlap_midline', dict(boots={'boot115c': dict(lines=('[7] x PresentOverlap: thread=1',))}), ['c_no_overlap']),
    ('c_marker_log', dict(boots={'boot115c': dict(lines=('GpuHangAbort: role=4',))}), ['c_no_marker']),
    ('c_marker_stdout', dict(boots={'boot115c': dict(stdout='Unhandled exception: 0xC0000005')}), ['c_no_marker']),
    ('c_stdout_clean', dict(boots={'boot115c': dict(stdout='0xe06d7363 C++ exception (not a marker)')}), []),
    ('c_idle', dict(boots={'boot115c': dict(gpu_util=10.5)}), ['adm_idle_c']),
    ('c_idle_edge', dict(boots={'boot115c': dict(gpu_util=10)}), []),
    ('c_gate_daslot', dict(boots={'boot115c': dict(gates=GATES + ' daslot=1')}), ['c_default_runs']),
    ('c_gate_daguard', dict(boots={'boot115c': dict(gates=GATES + ' daguard=1')}), ['c_default_runs']),
    ('c_gate_cspfree', dict(boots={'boot115c': dict(gates=GATES + ' cspfree=1')}), ['c_default_runs']),
    ('c_gate_bdanarrow', dict(boots={'boot115c': dict(gates=GATES + ' bdanarrow=1')}), ['c_default_runs']),
    ('c_gate_titleasync', dict(boots={'boot115c': dict(gates=GATES + ' titleasync=1')}), ['c_default_runs']),
    ('a_knob_env', dict(boots={'boot115a': dict(env={'KYTY_TITLE_ASYNC': '1'})}), ['a_knob']),
    ('c_knob_missing', dict(boots={'boot115c': dict(env_drop=['KYTY_TITLE_ASYNC'])}), ['c_knob']),
    ('c_knob_0', dict(boots={'boot115c': dict(env={'KYTY_TITLE_ASYNC': '0'})}), ['c_knob']),
    ('b_binary', dict(boots={'boot115b': dict(binary='1' * 64)}), ['adm_b_binary']),
    ('b_pin_none', dict(boots={'boot115b': dict(pins=())}), []),
    ('b_pin_line', dict(boots={'boot115b': dict(pins=('GpuClockPin: mode 1',))}), []),
    ('b_pin_mode2', dict(boots={'boot115b': dict(pins=('GpuClockPin: mode 2',))}), ['adm_b_pinned']),
    ('b_pin_two', dict(boots={'boot115b': dict(pins=('GpuClockPin: mode 1',) * 2)}), ['adm_b_pinned']),
    ('b_hold_5000', dict(boots={'boot115b': dict(holds=('PrepareHold: ms=5000',))}), ['adm_b_hold_logged']),
    ('b_real_shape', dict(boots={'boot115b': dict(pins=(), lines=('--- Build ---', 'Fork build x', '--- Fatal Error ---', FATAL))}), []),
    ('b_pin_env', dict(boots={'boot115b': dict(env_drop=['KYTY_GPU_CLOCK_PIN'])}), ['adm_b_pinned']),
    ('b_hold_env', dict(boots={'boot115b': dict(env_drop=['KYTY_PREPARE_HOLD_MS'])}), ['adm_b_hold_env']),
    ('b_schedule', dict(boots={'boot115b': dict(env={'KYTY_GATE_SCHEDULE': 'x'})}), ['adm_b_no_schedule']),
    ('b_checkpoints', dict(boots={'boot115b': dict(env={'KYTY_GPU_CHECKPOINTS': '0'})}), ['adm_b_no_checkpoints']),
    ('b_shift', dict(boots={'boot115b': dict(env={'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '0'})}), ['adm_b_no_shift']),
    ('b_gate', dict(boots={'boot115b': dict(gates=GATES + ' titleasync=1')}), ['adm_b_default_runs']),
    ('b_hold_none', dict(boots={'boot115b': dict(holds=())}), ['adm_b_fatal', 'adm_b_hold_logged']),
    ('b_knob_env', dict(boots={'boot115b': dict(env={'KYTY_TITLE_ASYNC': '1'})}), ['adm_b_knob']),
    ('b_main_env_missing', dict(boots={'boot115b': dict(env_drop=['KYTY_PREPARE_MAIN_PRESENT'])}), ['adm_b_main_env']),
    ('b_main_env_2', dict(boots={'boot115b': dict(env={'KYTY_PREPARE_MAIN_PRESENT': '2'})}), ['adm_b_main_env']),
    ('b_main_missing', dict(boots={'boot115b': dict(mains=())}), ['adm_b_main_logged']),
    ('b_main_two', dict(boots={'boot115b': dict(mains=('PrepareMainPresent: mode 1',) * 2)}), ['adm_b_main_logged']),
    ('b_no_fatal', dict(boots={'boot115b': dict(lines=('--- Fatal Error ---', 'Error: other.cpp:1'))}), ['adm_b_fatal']),
    ('b_fatal_midline', dict(boots={'boot115b': dict(lines=('[3] x ' + FATAL,))}), []),
    ('b_waited', dict(boots={'boot115b': dict(waits=(W % (10016, 601, 3),))}), ['adm_b_no_wait']),
    ('b_idle', dict(boots={'boot115b': dict(gpu_util=11)}), ['adm_idle_b']),
    ('b_markers_allowed', dict(boots={'boot115b': dict(stdout='--- Fatal Error ---')}), []),
    ('b_att_ignored', dict(boots={'boot115b': dict(atts=[])}), []),
    ('a_and_vid_fail', dict(glitches=1, boots={'boot115a': dict(waits=(W % (70, 5, 0),))}), ['a_presents_other', 'a_wait', 'no_glitch']),
    ('adm_and_fail', dict(glitches=1, boots={'boot115b': dict(mains=())}), ['adm_b_main_logged', 'no_glitch']),
    ('b_fatal_before_hold', dict(boots={'boot115b': dict(holds=(), lines=(FATAL, 'PrepareHold: ms=10000'))}), ['adm_b_fatal']),
]
ok = True
for name, kw, want in cases:
    res = make(name, **kw)
    got = failing(res)
    expect = 'PASS' if not want else ('NOT_ADMITTED' if any(w.startswith('adm_') for w in want) else 'FAIL')
    passed = got == sorted(want) and res['verdict'] == expect
    ok &= passed
    print('%-24s want %-40s got %-40s %s' % (name, want, got, 'OK' if passed else 'FAIL'))
CONSTANTS = dict(TAG='vid115', BOOT_TAGS=('boot115a', 'boot115b', 'boot115c'), BOOT_CONTROL='boot115b',
                 BOOT_SHIP='boot115c', MIN_FRAMES=3000, MIN_ROWS=1000, TITLE_WALL_MAX_NS=60000,
                 HOLD_MS=10000, BOOT_DEFAULTS=('daslot', 'daguard', 'cspfree', 'bdanarrow', 'titleasync'),
                 IDLE_GPU_MAX=10, PRESENTS_MIN=300, FATAL_SITE=b'commandRecorder.cpp:326',
                 BUILD_SHA='d3a981a23fc1c5df651eef2a93ff1f02a8bffd04416adea2fd5cd2218e290f64')
differ = [k for k, v in CONSTANTS.items() if getattr(mod, k) != v]
print('%-20s %s %s' % ('CONSTANTS', differ or 'match', 'OK' if not differ else 'FAIL'))
ok &= not differ
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
