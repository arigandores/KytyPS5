"""Session 114: fixtures for ctl114.py - PASS, FAIL on each verdict term alone, every admission term alone in each run
(exact error sets), both sides of every threshold, the stall window's position (first rows AFTER the queued line) and
the constants.
    python test_ctl114.py <ctl114.py>
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_ctl114')
NL = chr(10)
spec = importlib.util.spec_from_file_location('ctl114', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
seal = BASE / 'seal.md'
seal.write_bytes(b'fixture seal 114 ctl')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
GATES = 'dawalk=1 smemocheck=0 dabatch=8 fslean=0'
FROZEN, CALM = 3040000, 33000


def run_files(d, tag, rows=3000, stall_row=1500, window=None, gates=None, env=None, env_drop=(), atts=None,
              pins=('GpuClockPin: mode 1',), triggers=1, queued=1, waits=None, lates=None, slow=None, lines=(),
              stdout=None, gpu_util=0.0, binary=None, prereg=None, before=None, after=None, no_meta=False):
    asy = mod.ASYNC[tag]
    if window is None:
        window = [FROZEN, 17000, 33000] if asy == 0 else [CALM, 33000, 33000]
    if waits is None:
        waits = [(3001000, 3000), (40000, 1)] if asy == 0 else []
    if lates is None:
        lates = [3000500]
    if slow is None:
        slow = 1 if asy == 0 else 0
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0',
         'KYTY_MAIN_STALL_TEST': '3000:3000'}
    e.update(env or {})
    for k in env_drop:
        e.pop(k, None)
    att = [{'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None, 'hold_s': 180.1, 'stable_frame': 300}]
    meta = {'binary_sha256': binary or mod.BINARY_SHA, 'env': e,
            'gates': gates if gates is not None else GATES + ' titleasync=%d' % asy,
            'prereg': prereg or {'sha256': mod.PRED_SHA, 'bytes': mod.PRED_BYTES},
            'attempts': atts if atts is not None else att}
    if gpu_util is not None:
        meta['pre_run'] = {'gpu_util_median': gpu_util}
    if not no_meta:
        (d / (tag + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    out = list(pins) + ['MainStallTest: frame=3000 ms=3000'] * triggers + list(lines)
    for n in range(1, rows + 1):
        if n == stall_row:
            out.extend(['MainStallTest: queued frame=3000 ms=3000'] * queued)
            out.extend(['GpuWaitSlow: role=4 requested=5 known=4 current=5'] * slow)
            out.extend('MainThreadWait: us=%d frame=%d titleasync=%d' % (us, fr, asy) for us, fr in waits)
            out.extend('MainTaskLate: us=%d' % us for us in lates)
        k = n - stall_row
        if 0 <= k < len(window):
            dt = window[k]
        elif before is not None and k == -1:
            dt = before
        elif after is not None and k == len(window):
            dt = after
        else:
            dt = 33000
        out.append('FrameTrace: n=%d dt_us=%d cpu_gpu_us=30000 arm=0 blk=0' % (n, dt))
    (d / ('log_%s.txt' % tag)).write_bytes((NL.join(out) + NL).encode('utf-8'))
    if stdout is not None:
        (d / ('stdout_%s.txt' % tag)).write_bytes((stdout + NL).encode('utf-8'))


def make(name, a=None, b=None, installed=None):
    d = BASE / name
    d.mkdir()
    run_files(d, 'ctl114a', **(a or {}))
    run_files(d, 'ctl114b', **(b or {}))
    return mod.evaluate(str(d), installed_sha=installed or mod.BINARY_SHA)


def errs(res):
    return {'top': res['errors'], 'a': res['runs']['ctl114a'].get('errors'), 'b': res['runs']['ctl114b'].get('errors')}


def failed_checks(res):
    return sorted(k for k, v in (res.get('checks') or {}).items() if not v)


# (name, a kwargs, b kwargs, verdict, errors in a, errors in b, failing checks)
cases = [
    ('PASS', {}, {}, 'PASS', [], [], []),
    ('PASS_stdout_clean', {'stdout': '0xe06d7363 C++ exception'}, {}, 'PASS', [], [], []),
    ('PASS_edges', {'window': [2500000, 17000, 33000], 'waits': [(2500000, 3000)]},
     {'window': [500000, 33000, 33000], 'lates': [2500000]}, 'PASS', [], [], []),
    ('PASS_freeze_third_row', {'window': [33000, 17000, 3040000]}, {}, 'PASS', [], [], []),
    ('FAIL_a_no_freeze', {'window': [2499999, 17000, 33000]}, {}, 'FAIL', [], [], ['a_froze']),
    ('FAIL_a_freeze_before_window', {'window': [33000, 33000, 33000], 'before': 3040000}, {}, 'FAIL', [], [],
     ['a_froze']),
    ('FAIL_a_freeze_after_window', {'window': [33000, 33000, 33000], 'after': 3040000}, {}, 'FAIL', [], [],
     ['a_froze']),
    ('FAIL_a_no_wait', {'waits': [(2499999, 3000)]}, {}, 'FAIL', [], [], ['a_waited_main']),
    ('FAIL_a_wait_other_frame', {'waits': [(3001000, 1)]}, {}, 'FAIL', [], [], ['a_waited_main']),
    ('FAIL_b_froze', {}, {'window': [500001, 33000, 33000]}, 'FAIL', [], [], ['b_calm']),
    ('FAIL_b_froze_second_row', {}, {'window': [33000, 3040000, 33000]}, 'FAIL', [], [], ['b_calm']),
    ('FAIL_b_slow', {}, {'slow': 1}, 'FAIL', [], [], ['b_no_slow']),
    ('FAIL_b_main_did_not_sleep', {}, {'lates': [2499999]}, 'FAIL', [], [], ['b_main_slept']),
    ('FAIL_b_no_late_line', {}, {'lates': []}, 'FAIL', [], [], ['b_main_slept']),
    ('A_slow_allowed', {'slow': 2}, {}, 'PASS', [], [], []),
]
for tag in ('a', 'b'):
    cases += [
        ('INPUTS_%s' % tag, None, None, 'NOT_ADMITTED', None, None, None),
    ]
ADMIT = [
    ('BINARY', {'binary': '1' * 64}, ['BINARY']),
    ('PREREG', {'prereg': {'sha256': '0' * 64, 'bytes': 1}}, ['PREREG']),
    ('ENV_PIN', {'env_drop': ['KYTY_GPU_CLOCK_PIN']}, ['ENV_PIN']),
    ('ENV_STALL', {'env': {'KYTY_MAIN_STALL_TEST': '3000:2000'}}, ['ENV_STALL']),
    ('ENV_STALL_missing', {'env_drop': ['KYTY_MAIN_STALL_TEST']}, ['ENV_STALL']),
    ('ENV_SCHED', {'env': {'KYTY_GATE_SCHEDULE': 'x'}}, ['ENV_FORBIDDEN']),
    ('ENV_CKPT', {'env': {'KYTY_GPU_CHECKPOINTS': '0'}}, ['ENV_FORBIDDEN']),
    ('ENV_REC', {'env': {'KYTY_REC': 'x.mp4'}}, ['ENV_FORBIDDEN']),
    ('ENV_PRECACHE', {'env': {'KYTY_PIPELINE_PRECACHE': 'gfx'}}, ['ENV_FORBIDDEN']),
    ('ENV_SHIFT', {'env': {'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '1024'}}, ['ENV_FORBIDDEN']),
    ('ENV_TITLE', {'env': {'KYTY_TITLE_ASYNC': '1'}}, ['ENV_FORBIDDEN']),
    ('GATES_missing', {'gates': GATES}, ['GATES']),
    ('GATES_twice', {'gates': GATES + ' titleasync=0 titleasync=1'}, ['GATES']),
    ('ATT_outcome', {'atts': [{'outcome': 'hang', 'hold_exit': None, 'hold_s': 180.1}]}, ['ATTEMPT']),
    ('ATT_exit', {'atts': [{'outcome': 'ok', 'hold_exit': 3, 'hold_s': 180.1}]}, ['ATTEMPT']),
    ('ATT_hold_fail', {'atts': [{'outcome': 'ok', 'hold_exit': None, 'hold_s': 170.9}]}, ['ATTEMPT']),
    ('ATT_two', {'atts': [{'outcome': 'ok', 'hold_exit': None, 'hold_s': 180.1}] * 2}, ['ATTEMPT']),
    ('ATT_extra_failed', {'atts': [{'outcome': 'hang', 'hold_exit': None, 'hold_s': 180.1},
                                   {'outcome': 'ok', 'hold_exit': None, 'hold_s': 180.1}]}, ['ATTEMPT']),
    ('PRE_RUN_fail', {'gpu_util': 10.1}, ['PRE_RUN']),
    ('PRE_RUN_missing', {'gpu_util': None}, ['PRE_RUN']),
    ('PIN_none', {'pins': ()}, ['PIN_ONCE']),
    ('PIN_two', {'pins': ('GpuClockPin: mode 1', 'GpuClockPin: mode 1')}, ['PIN_ONCE']),
    ('PIN_mode2', {'pins': ('GpuClockPin: mode 2',)}, ['PIN_ONCE']),
    ('MARK_hang', {'lines': ['GpuHangAbort: role=4']}, ['NO_MARKER']),
    ('MARK_lost', {'lines': ['vk::Result ErrorDeviceLost']}, ['NO_MARKER']),
    ('MARK_fatal', {'lines': ['--- Fatal Error ---']}, ['NO_MARKER']),
    ('MARK_skipped', {'lines': ['AsyncPipelines: skipped draw 3']}, ['NO_MARKER']),
    ('MARK_stdout', {'stdout': 'Unhandled exception: 0xC0000005'}, ['NO_MARKER']),
    ('ROWS_fail', {'rows': 999, 'stall_row': 500}, ['ROWS']),
    ('TRIGGER_none', {'triggers': 0}, ['TRIGGER']),
    ('TRIGGER_two', {'triggers': 2}, ['TRIGGER']),
    ('QUEUED_none', {'queued': 0}, ['TRIGGER', 'STALL_ROWS']),
    ('QUEUED_two', {'queued': 2}, ['TRIGGER']),
    ('STALL_ROWS_short', {'rows': 1501, 'stall_row': 1500, 'window': [3040000, 17000]}, ['STALL_ROWS']),
]
ok = True
for name, akw, bkw, want, ea, eb, fc in cases:
    if akw is None:
        continue
    res = make(name, akw, bkw)
    e = errs(res)
    passed = (res['verdict'] == want and e['top'] == [] and e['a'] == ea and e['b'] == eb
              and failed_checks(res) == fc)
    ok &= passed
    print('%-30s want %-12s got %-12s a %s b %s checks %s %s' % (name, want, res['verdict'], e['a'], e['b'],
                                                                 failed_checks(res), 'OK' if passed else 'FAIL'))
for name, kw, want_errs in ADMIT:
    for side in ('a', 'b'):
        res = make('%s_%s' % (name, side), kw if side == 'a' else None, kw if side == 'b' else None)
        e = errs(res)
        passed = res['verdict'] == 'NOT_ADMITTED' and e[side] == want_errs and e['b' if side == 'a' else 'a'] == []
        ok &= passed
        print('%-30s want %s got %s %s' % ('%s_%s' % (name, side), want_errs, e[side], 'OK' if passed else 'FAIL'))
# ATTEMPT edge: 171.0 = 0.95 x 180 passes
res = make('ATT_hold_edge_ok', {'atts': [{'outcome': 'ok', 'hold_exit': None, 'hold_s': 171.0}]}, None)
passed = res['verdict'] == 'PASS'
ok &= passed
print('%-30s got %s %s' % ('ATT_hold_edge_ok', res['verdict'], 'OK' if passed else 'FAIL'))
# PRE_RUN edge 10.0 passes
res = make('PRE_RUN_edge_ok', {'gpu_util': 10.0}, {'gpu_util': 10.0})
passed = res['verdict'] == 'PASS'
ok &= passed
print('%-30s got %s %s' % ('PRE_RUN_edge_ok', res['verdict'], 'OK' if passed else 'FAIL'))
# ROWS edge 1000 passes
res = make('ROWS_edge_ok', {'rows': 1000, 'stall_row': 500}, {'rows': 1000, 'stall_row': 500})
passed = res['verdict'] == 'PASS'
ok &= passed
print('%-30s got %s %s' % ('ROWS_edge_ok', res['verdict'], 'OK' if passed else 'FAIL'))
# INPUTS (a missing run), IDENTITY, DRAFT, SEAL
d = BASE / 'INPUTS_a'
d.mkdir()
run_files(d, 'ctl114a', no_meta=True)
run_files(d, 'ctl114b')
res = mod.evaluate(str(d), installed_sha=mod.BINARY_SHA)
passed = res['verdict'] == 'NOT_ADMITTED' and res['runs']['ctl114a']['errors'] == ['INPUTS']
ok &= passed
print('%-30s got %s %s' % ('INPUTS_a', res['runs']['ctl114a']['errors'], 'OK' if passed else 'FAIL'))
res = make('IDENTITY', None, None, installed='0' * 64)
passed = res['verdict'] == 'NOT_ADMITTED' and res['errors'] == ['IDENTITY']
ok &= passed
print('%-30s got %s %s' % ('IDENTITY', res['errors'], 'OK' if passed else 'FAIL'))
saved = (mod.PRED_SHA, mod.PRED_BYTES)
mod.PRED_SHA = None
res = make('DRAFT', None, None)
passed = res['verdict'] == 'NOT_ADMITTED' and res['errors'] == ['DRAFT']
ok &= passed
print('%-30s got %s %s' % ('DRAFT', res['errors'], 'OK' if passed else 'FAIL'))
mod.PRED_SHA, mod.PRED_BYTES = saved[0], saved[1] + 1
res = make('SEAL', None, None)
passed = res['verdict'] == 'NOT_ADMITTED' and 'SEAL' in res['errors']
ok &= passed
print('%-30s got %s %s' % ('SEAL', res['errors'], 'OK' if passed else 'FAIL'))
mod.PRED_SHA, mod.PRED_BYTES = saved
CONSTANTS = dict(TAGS=('ctl114a', 'ctl114b'), ASYNC={'ctl114a': 0, 'ctl114b': 1}, STALL_ENV='3000:3000',
                 STALL_FRAME=3000, HOLD_S=180, MIN_ROWS=1000, WINDOW=3, FREEZE_US=2500000, CALM_US=500000,
                 MAX_GPU_UTIL=10.0,
                 BINARY_SHA='916f64898a5a31c697ad0d823f0795850acc160cf56271b566e8ae330c7c3b2c')
differ = [k for k, v in CONSTANTS.items() if getattr(mod, k) != v]
print('%-30s %s %s' % ('CONSTANTS', differ or 'match', 'OK' if not differ else 'FAIL'))
ok &= not differ
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
