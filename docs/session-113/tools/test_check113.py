"""Session 113: fixtures for check113.py (from test_check112.py by make_check113.py) - PASS, every check failing
alone, and both sides of every threshold.
    python test_check113.py <check113.py>
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_check113')
NL = chr(10)
spec = importlib.util.spec_from_file_location('check113', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
GATES = 'dawalk=1 smemocheck=0 dabatch=8 fslean=0'
GC_OK = 'BufferGc: budget=14901313536 trigger=9747352781 critical=13183326618 shift_mb=0'


def make(name, rows=3700, stable=280, frames=4000, glitches=0, gates=GATES, env=None, env_drop=(), atts=None,
         binary=None, installed=None, pins=('GpuClockPin: mode 1',), lines=(), stdout=None, free=1100, noguard=0,
         slot_bad=0, hit=266, free_bad=0, sync_new=0, drop_field=False, glitch_text=None, nskip=0, would=0,
         gc=(GC_OK,)):
    d = BASE / name
    d.mkdir()
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_REC': 'x.mp4'}
    e.update(env or {})
    for k in env_drop:
        e.pop(k, None)
    meta = {'binary_sha256': binary or mod.BUILD_SHA, 'env': e, 'gates': gates,
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
        if drop_field and n == stable + 20:
            f = f.replace('da_q_noguard=', 'da_q_noguarX=')
        out.append('FrameTrace-x: n=%d rt_att=100 %s' % (n, f))
    (d / ('log_%s.txt' % mod.TAG)).write_bytes((NL.join(out) + NL).encode('utf-8'))
    if stdout is not None:
        (d / ('stdout_%s.txt' % mod.TAG)).write_bytes((stdout + NL).encode('utf-8'))
    return mod.evaluate(str(d), installed_sha=installed or mod.BUILD_SHA)


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
     ['free_default_armed', 'one_ok_attempt', 'rows', 'slot_default_armed']),   # no scene rows at all
    ('att_outcome', dict(atts=[{'outcome': 'hang', 'hold_exit': None, 'stable_frame': 280}]),
     ['free_default_armed', 'one_ok_attempt', 'rows', 'slot_default_armed']),
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
]
ok = True
for name, kw, want in cases:
    res = make(name, **kw)
    got = failing(res)
    passed = got == sorted(want) and res['verdict'] == ('PASS' if not want else 'FAIL')
    ok &= passed
    print('%-20s want %-40s got %-40s %s' % (name, want, got, 'OK' if passed else 'FAIL'))
CONSTANTS = dict(TAG='vid113', MIN_FRAMES=3000, MIN_ROWS=1000,
                 BUILD_SHA='1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373')
differ = [k for k, v in CONSTANTS.items() if getattr(mod, k) != v]
print('%-20s %s %s' % ('CONSTANTS', differ or 'match', 'OK' if not differ else 'FAIL'))
ok &= not differ
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
