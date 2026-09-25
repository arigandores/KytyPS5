"""Session 114: fixtures for bootctl114.py - KEEP_1, every setup member failing alone on each tag, every outcome member
failing alone on each tag.
    python test_bootctl114.py <bootctl114.py>
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_bootctl114')
NL = chr(10)
spec = importlib.util.spec_from_file_location('bootctl114', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
GATES = 'dawalk=1 smemocheck=0 dabatch=8 fslean=0'
FATAL = 'Error: condition (m_producer != self || m_open_slot != nullptr) is true in C:\\kyty\\x\\commandRecorder.cpp:326'


def write(d, tag, env=None, env_drop=(), gates=None, binary=None, lines=None):
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_PREPARE_HOLD_MS': '10000'}
    if tag.endswith('c'):
        e['KYTY_TITLE_ASYNC'] = '0'
    e.update(env or {})
    for k in env_drop:
        e.pop(k, None)
    if gates is None:
        gates = GATES + (' titleasync=0' if tag.endswith('c') else '')
    meta = {'binary_sha256': binary or mod.BUILD_SHA, 'env': e, 'gates': gates, 'attempts': [{'outcome': 'fail'}]}
    (d / (tag + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    if lines is None:
        lines = ['entry = 0x0000000900000070', 'PrepareHold: ms=10000', 'Window 1 shown', '--- Fatal Error ---', FATAL]
    (d / ('log_%s.txt' % tag)).write_bytes((NL.join(lines) + NL).encode('utf-8'))


def make(name, b=None, c=None):
    d = BASE / name
    d.mkdir()
    write(d, 'boot114b', **(b or {}))
    write(d, 'boot114c', **(c or {}))
    return mod.evaluate(str(d))


HOLD = 'PrepareHold: ms=10000'
WAIT = 'ShaderPreparation: startup wait finished in 10016 ms'
cases = [('KEEP', dict(), 'KEEP_1')]
for t in ('b', 'c'):
    cases += [
        ('%s_binary' % t, {t: dict(binary='1' * 64)}, 'NOT_EVALUABLE'),
        ('%s_hold_env' % t, {t: dict(env_drop=['KYTY_PREPARE_HOLD_MS'])}, 'NOT_EVALUABLE'),
        ('%s_hold_env_5000' % t, {t: dict(env={'KYTY_PREPARE_HOLD_MS': '5000'})}, 'NOT_EVALUABLE'),
        ('%s_pin' % t, {t: dict(env_drop=['KYTY_GPU_CLOCK_PIN'])}, 'NOT_EVALUABLE'),
        ('%s_schedule' % t, {t: dict(env={'KYTY_GATE_SCHEDULE': 'x'})}, 'NOT_EVALUABLE'),
        ('%s_checkpoints' % t, {t: dict(env={'KYTY_GPU_CHECKPOINTS': '0'})}, 'NOT_EVALUABLE'),
        ('%s_no_fatal' % t, {t: dict(lines=[HOLD, 'Window 1 shown', WAIT])}, 'DEFAULT_0'),
        ('%s_no_fatal_no_wait' % t, {t: dict(lines=[HOLD, 'Window 1 shown'])}, 'DEFAULT_0'),
        ('%s_other_fatal' % t, {t: dict(lines=[HOLD, '--- Fatal Error ---', 'Error: x.cpp:12'])}, 'DEFAULT_0'),
        ('%s_fatal_before_hold' % t, {t: dict(lines=[FATAL, HOLD])}, 'DEFAULT_0'),
        ('%s_fatal_and_wait' % t, {t: dict(lines=[HOLD, WAIT, FATAL])}, 'DEFAULT_0'),
        ('%s_no_hold' % t, {t: dict(lines=['Window 1 shown', FATAL])}, 'DEFAULT_0'),
        ('%s_two_holds' % t, {t: dict(lines=[HOLD, HOLD, FATAL])}, 'DEFAULT_0'),
        ('%s_hold_5000_line' % t, {t: dict(lines=['PrepareHold: ms=5000', FATAL])}, 'DEFAULT_0'),
    ]
cases += [
    ('b_env_knob', dict(b=dict(env={'KYTY_TITLE_ASYNC': '1'})), 'NOT_EVALUABLE'),
    ('b_gate_knob', dict(b=dict(gates=GATES + ' titleasync=1')), 'NOT_EVALUABLE'),
    ('c_env_knob_missing', dict(c=dict(env_drop=['KYTY_TITLE_ASYNC'])), 'NOT_EVALUABLE'),
    ('c_env_knob_1', dict(c=dict(env={'KYTY_TITLE_ASYNC': '1'})), 'NOT_EVALUABLE'),
    ('c_gate_knob_missing', dict(c=dict(gates=GATES)), 'NOT_EVALUABLE'),
    ('c_gate_knob_1', dict(c=dict(gates=GATES + ' titleasync=1')), 'NOT_EVALUABLE'),
    ('c_gate_knob_10', dict(c=dict(gates=GATES + ' titleasync=10')), 'NOT_EVALUABLE'),
    ('c_gate_knob_01', dict(c=dict(gates=GATES + ' titleasync=01')), 'NOT_EVALUABLE'),
    ('both_other', dict(b=dict(lines=[HOLD, WAIT]), c=dict(lines=[HOLD, WAIT])), 'DEFAULT_0'),
    ('setup_beats_outcome', dict(b=dict(binary='1' * 64), c=dict(lines=[HOLD, WAIT])), 'NOT_EVALUABLE'),
    ('fatal_midline', dict(b=dict(lines=[HOLD, '[3] x ' + FATAL])), 'KEEP_1'),
]
ok = True
for name, kw, want in cases:
    res = make(name, **kw)
    passed = res['verdict'] == want
    ok &= passed
    print('%-24s want %-14s got %-14s %s' % (name, want, res['verdict'], 'OK' if passed else 'FAIL'))
CONSTANTS = dict(TAGS=('boot114b', 'boot114c'), HOLD_LINE=b'PrepareHold: ms=10000', FATAL_SITE=b'commandRecorder.cpp:326',
                 WAIT_LINE=b'ShaderPreparation: startup wait finished',
                 BUILD_SHA='8d7ba8f4ae995a3da10670a095670acf0c46450675f7b61137714eb7975956ec')
differ = [k for k, v in CONSTANTS.items() if getattr(mod, k) != v]
print('%-24s %s %s' % ('CONSTANTS', differ or 'match', 'OK' if not differ else 'FAIL'))
ok &= not differ
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
