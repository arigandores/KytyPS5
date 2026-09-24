"""Session 111: fixtures for vds111.py - every verdict branch and every admission term alone (exact error set).
    python test_vds111.py <vds111.py>
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_vds111')
NL = chr(10)
spec = importlib.util.spec_from_file_location('vds111', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
seal = BASE / 'seal.md'
seal.write_bytes(b'fixture seal 111 vds')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
GATES = 'dawalk=1 dabatch=8 fslean=0'


def make(name, rows=9000, installed=None, slot_bad=0, chk_bad=0, chk_ok=5, q_free=1, free_hit=250, free_bad=0,
         lines=(), stdout=None, **bad):
    d = BASE / name
    d.mkdir()
    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}
    env.update(bad.get('env', {}))
    for k in bad.get('env_drop', ()):
        env.pop(k, None)
    att = {'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None, 'hold_s': 300.1}
    att.update(bad.get('att', {}))
    meta = {'binary_sha256': bad.get('binary', mod.BINARY_SHA), 'env': env,
            'gates': bad.get('gates', GATES + mod.TAIL),
            'prereg': bad.get('prereg', {'sha256': mod.PRED_SHA, 'bytes': mod.PRED_BYTES}),
            'attempts': [att] * bad.get('n_att', 1)}
    if not bad.get('no_meta'):
        (d / (mod.TAG + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    out = list(bad.get('pin_lines', ['GpuClockPin: mode 1']))
    out += list(lines)
    for n in range(1, rows + 1):
        fields = ('da_slot_bad=%d da_chk_ok=%d da_chk_bad=%d da_q_free=%d da_guard_busy=0 da_q_taking=0 '
                  'da_hint_defer=0 da_hint_torn=0 cspfree_hit=%d cspfree_bad=%d') % (
                      slot_bad if n == 4000 else 0, chk_ok, chk_bad if n == 5000 else 0, q_free, free_hit,
                      free_bad if n == 6000 else 0)
        if bad.get('drop_field') and n == 3000:
            fields = fields.replace('da_q_taking=', 'da_q_takinX=')
        out.append('FrameTrace-x: n=%d rt_att=100 %s' % (n, fields))
    (d / ('log_%s.txt' % mod.TAG)).write_bytes((NL.join(out) + NL).encode('utf-8'))
    if stdout is not None:
        (d / ('stdout_%s.txt' % mod.TAG)).write_bytes((stdout + NL).encode('utf-8'))
    return mod.evaluate(str(d), installed_sha=installed or mod.BINARY_SHA)


cases = [
    ('GO', dict(), 'GO', []),
    ('GO_stdout_clean', dict(stdout='0xe06d7363 C++ exception (not a marker)'), 'GO', []),
    ('NO_GO_slot', dict(slot_bad=1), 'NO_GO', []),
    ('NO_GO_chk', dict(chk_bad=1), 'NO_GO', []),
    ('NO_GO_slot_line', dict(lines=['DaSlotVerify: MISMATCH slot=5 fingerprint=0x1']), 'NO_GO', []),
    ('NO_GO_chk_line', dict(lines=['DrawAheadVerify: MISMATCH hash=0x1 stage=1 materialized=1']), 'NO_GO', []),
    ('IDENTITY', dict(installed='0' * 64), 'NOT_ADMITTED', ['IDENTITY']),
    ('INPUTS', dict(no_meta=True), 'NOT_ADMITTED', ['INPUTS']),
    ('BINARY', dict(binary='1' * 64), 'NOT_ADMITTED', ['BINARY']),
    ('PREREG', dict(prereg={'sha256': '0' * 64, 'bytes': 1}), 'NOT_ADMITTED', ['PREREG']),
    ('ENV_PIN', dict(env_drop=['KYTY_GPU_CLOCK_PIN']), 'NOT_ADMITTED', ['ENV_PIN']),
    ('ENV_SCHED', dict(env={'KYTY_GATE_SCHEDULE': 'x'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN']),
    ('ENV_CKPT', dict(env={'KYTY_GPU_CHECKPOINTS': '0'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN']),
    ('ENV_REC', dict(env={'KYTY_REC': 'x.mp4'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN']),
    ('ENV_PRECACHE', dict(env={'KYTY_PIPELINE_PRECACHE': 'gfx'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN']),
    ('GATES_missing', dict(gates=GATES), 'NOT_ADMITTED', ['GATES']),
    ('GATES_no_check', dict(gates=GATES + ' daslot=2'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_mode1', dict(gates=GATES + ' daslot=1 smemocheck=1'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_twice', dict(gates=GATES + ' daslot=0' + mod.TAIL), 'NOT_ADMITTED', ['GATES']),
    ('GATES_order', dict(gates=GATES + ' smemocheck=1 daslot=2'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_chk_twice', dict(gates=GATES + ' smemocheck=0' + mod.TAIL), 'NOT_ADMITTED', ['GATES']),
    ('ATT_outcome', dict(att={'outcome': 'hang'}), 'NOT_ADMITTED', ['ATTEMPT']),
    ('ATT_exit', dict(att={'hold_exit': 3}), 'NOT_ADMITTED', ['ATTEMPT']),
    ('ATT_hold', dict(att={'hold_s': 280.0}), 'NOT_ADMITTED', ['ATTEMPT']),
    ('ATT_two', dict(n_att=2), 'NOT_ADMITTED', ['ATTEMPT']),
    ('PIN_none', dict(pin_lines=[]), 'NOT_ADMITTED', ['PIN_ONCE']),
    ('PIN_two', dict(pin_lines=['GpuClockPin: mode 1', 'GpuClockPin: mode 1']), 'NOT_ADMITTED', ['PIN_ONCE']),
    ('PIN_mode2', dict(pin_lines=['GpuClockPin: mode 1', 'GpuClockPin: mode 2']), 'NOT_ADMITTED', ['PIN_ONCE']),
    ('MARK_hang', dict(lines=['GpuHangAbort: role=4']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_error', dict(lines=['--- Error ---']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_fatal', dict(lines=['--- Fatal Error ---']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_skipped', dict(lines=['AsyncPipelines: skipped draw 5']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_slow', dict(lines=['GpuWaitSlow: 8 s']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_stdout', dict(stdout='Unhandled exception: 0xC0000005'), 'NOT_ADMITTED', ['NO_MARKER']),
    ('ROWS_few', dict(rows=4000), 'NOT_ADMITTED', ['ROWS']),
    ('ROWS_field', dict(drop_field=True), 'NOT_ADMITTED', ['ROWS']),
    ('ARMED_queue', dict(q_free=0), 'NOT_ADMITTED', ['ARMED']),
    ('ARMED_checks', dict(chk_ok=1, rows=9000), 'NOT_ADMITTED', ['ARMED']),          # 9 000 checks < 10 000
    ('ARMED_checks_edge', dict(chk_ok=0, chk_bad=0, rows=9000), 'NOT_ADMITTED', ['ARMED']),
    ('DEFAULTS_free', dict(free_hit=0), 'NOT_ADMITTED', ['DEFAULTS']),
    ('DEFAULTS_bad', dict(free_bad=1), 'NOT_ADMITTED', ['DEFAULTS']),
]
ok = True
for name, kw, want, errs in cases:
    out = make(name, **kw)
    passed = out['verdict'] == want and out['errors'] == errs
    ok &= passed
    print('%-18s want %-12s got %-12s bad %s errors %s %s' % (name, want, out['verdict'], out.get('bad'), out['errors'],
                                                               'OK' if passed else 'FAIL'))
# the check-count edge: exactly MIN_CHECKS passes
out = make('ARMED_edge_ok', rows=5000, chk_ok=2)
passed = out['verdict'] == 'GO' and out['errors'] == []
print('%-18s want GO (10 000 checks) got %s %s' % ('ARMED_edge_ok', out['verdict'], 'OK' if passed else 'FAIL'))
ok &= passed
saved = (mod.PRED_SHA, mod.PRED_BYTES)
mod.PRED_SHA = None
out = make('DRAFT')
passed = out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['DRAFT']
print('%-18s errors %s %s' % ('DRAFT', out['errors'], 'OK' if passed else 'FAIL'))
ok &= passed
mod.PRED_SHA, mod.PRED_BYTES = saved[0], saved[1] + 1
out = make('SEAL')
passed = out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['SEAL']
print('%-18s errors %s %s' % ('SEAL', out['errors'], 'OK' if passed else 'FAIL'))
ok &= passed
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
