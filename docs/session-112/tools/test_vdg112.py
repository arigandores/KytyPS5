"""Session 112: fixtures for vdg112.py - every verdict branch, every admission term alone (exact error set), and
the edge of every threshold (both sides).
    python test_vdg112.py <vdg112.py>
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_vdg112')
NL = chr(10)
spec = importlib.util.spec_from_file_location('vdg112', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
seal = BASE / 'seal.md'
seal.write_bytes(b'fixture seal 112 vdg')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
GATES = 'dawalk=1 smemocheck=1 dabatch=8 fslean=0'
ABBA = (0, 1, 1, 0)


def make(name, pre=1600, blocks=60, installed=None, slot_bad=0, chk_bad=0, chk=99, hit=100, q=1080, leak=5,
         leak_pos=0, leak1_pos=0, free_hit=250, free_bad=0, yields=0, lines=(), stdout=None, arm_line=None,
         block_len=90, **bad):
    d = BASE / name
    d.mkdir()
    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0',
           'KYTY_GATE_SCHEDULE': mod.SCHEDULE, 'KYTY_GATE_SCHEDULE_ABBA': '1'}
    env.update(bad.get('env', {}))
    for k in bad.get('env_drop', ()):
        env.pop(k, None)
    att = {'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None, 'hold_s': 300.1}
    att.update(bad.get('att', {}))
    meta = {'binary_sha256': bad.get('binary', mod.BINARY_SHA), 'env': env, 'gates': bad.get('gates', GATES),
            'prereg': bad.get('prereg', {'sha256': mod.PRED_SHA, 'bytes': mod.PRED_BYTES}),
            'attempts': [att] * bad.get('n_att', 1)}
    if not bad.get('no_meta'):
        (d / (mod.TAG + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    out = list(bad.get('pin_lines', ['GpuClockPin: mode 1']))
    out += list(lines)
    n = 0

    def row(arm, blk, pos, scheduled):
        nonlocal n
        n += 1
        out.append('FrameTrace: n=%d dt_us=31000 cpu_gpu_us=30000 arm=%d blk=%d rt_w=3840' % (n, arm, blk))
        out.append('FrameTrace-draw: n=%d draws=5000 da_hit=%d da_miss=3' % (n, hit))
        # unscheduled rows run the defaults (daslot 1); a block's boundary rows carry the other arm's calls
        free, noguard = (q, 0) if (not scheduled or arm == 1) else (0, q)
        if scheduled and arm == 0 and pos == leak_pos:
            free = leak
        if scheduled and arm == 1 and pos == leak1_pos:
            noguard = leak
        fields = ('da_slot_bad=%d da_chk_ok=%d da_chk_bad=%d da_q_free=%d da_q_noguard=%d da_guard_busy=0 '
                  'da_guard_yield=%d da_q_taking=0 da_hint_defer=0 da_hint_torn=0 da_qcall=%d cspfree_hit=%d '
                  'cspfree_bad=%d') % (
                      slot_bad if n == 4000 else 0, chk, chk_bad if n == 4500 else 0, free, noguard,
                      yields if n == 3000 else 0, q, free_hit, free_bad if n == 3500 else 0)
        if bad.get('drop_field') and n == 3000:
            fields = fields.replace('da_q_noguard=', 'da_q_noguarX=')
        out.append('FrameTrace-x: n=%d rt_att=100 %s' % (n, fields))

    for _ in range(pre):
        row(0, 0, 0, False)
    for blk in range(blocks):
        arm = ABBA[blk % 4]
        text = mod.ARM_TEXT[arm]
        if arm_line is not None and blk == 7:
            out.append(arm_line)
        else:
            out.append('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s' % (arm, blk, 1800 + 90 * blk,
                                                                                          text))
        for pos in range(block_len):
            row(arm, blk, pos, True)
    (d / ('log_%s.txt' % mod.TAG)).write_bytes((NL.join(out) + NL).encode('utf-8'))
    if stdout is not None:
        (d / ('stdout_%s.txt' % mod.TAG)).write_bytes((stdout + NL).encode('utf-8'))
    return mod.evaluate(str(d), installed_sha=installed or mod.BINARY_SHA)


GOOD_TEXT = 'GateArm: arm=1 arms=2 block=7 frame=2430 period=90 abba=1 text=' + mod.ARM_TEXT[1]
cases = [
    ('GO', dict(), 'GO', []),
    ('GO_no_leak', dict(leak=0), 'GO', []),
    ('GO_leak_pos9', dict(leak_pos=9), 'GO', []),
    ('GO_stdout_clean', dict(stdout='0xe06d7363 C++ exception (not a marker)'), 'GO', []),
    ('GO_armline_ok', dict(arm_line=GOOD_TEXT), 'GO', []),
    ('NO_GO_slot', dict(slot_bad=1), 'NO_GO', []),
    ('NO_GO_chk', dict(chk_bad=1), 'NO_GO', []),
    ('NO_GO_slot_line', dict(lines=['DaSlotVerify: MISMATCH slot=5 fingerprint=0x1']), 'NO_GO', []),
    ('NO_GO_chk_line', dict(lines=['DrawAheadVerify: MISMATCH hash=0x1 stage=1 materialized=1']), 'NO_GO', []),
    ('IDENTITY', dict(installed='0' * 64), 'NOT_ADMITTED', ['IDENTITY']),
    ('INPUTS', dict(no_meta=True), 'NOT_ADMITTED', ['INPUTS']),
    ('BINARY', dict(binary='1' * 64), 'NOT_ADMITTED', ['BINARY']),
    ('PREREG', dict(prereg={'sha256': '0' * 64, 'bytes': 1}), 'NOT_ADMITTED', ['PREREG']),
    ('ENV_PIN', dict(env_drop=['KYTY_GPU_CLOCK_PIN']), 'NOT_ADMITTED', ['ENV_PIN']),
    ('ENV_CKPT', dict(env={'KYTY_GPU_CHECKPOINTS': '0'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN']),
    ('ENV_REC', dict(env={'KYTY_REC': 'x.mp4'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN']),
    ('ENV_PRECACHE', dict(env={'KYTY_PIPELINE_PRECACHE': 'gfx'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN']),
    ('SCHED_missing', dict(env_drop=['KYTY_GATE_SCHEDULE']), 'NOT_ADMITTED', ['SCHEDULE']),
    ('SCHED_text', dict(env={'KYTY_GATE_SCHEDULE': mod.SCHEDULE.replace('daguard=0', 'daguard=1')}),
     'NOT_ADMITTED', ['SCHEDULE']),
    ('SCHED_abba', dict(env_drop=['KYTY_GATE_SCHEDULE_ABBA']), 'NOT_ADMITTED', ['SCHEDULE']),
    ('GATES_check_off', dict(gates='dawalk=1 smemocheck=0 dabatch=8 fslean=0'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_appended', dict(gates='dawalk=1 smemocheck=0 dabatch=8 fslean=0 smemocheck=1'), 'NOT_ADMITTED',
     ['GATES']),                                                                          # the session-111 defect
    ('GATES_none', dict(gates='dawalk=1 dabatch=8 fslean=0'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_daslot', dict(gates=GATES + ' daslot=1'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_daguard', dict(gates=GATES + ' daguard=0'), 'NOT_ADMITTED', ['GATES']),
    ('ATT_outcome', dict(att={'outcome': 'hang'}), 'NOT_ADMITTED', ['ATTEMPT']),
    ('ATT_exit', dict(att={'hold_exit': 3}), 'NOT_ADMITTED', ['ATTEMPT']),
    ('ATT_hold_edge_fail', dict(att={'hold_s': 284.9}), 'NOT_ADMITTED', ['ATTEMPT']),
    ('ATT_hold_edge_ok', dict(att={'hold_s': 285.0}), 'GO', []),
    ('ATT_two', dict(n_att=2), 'NOT_ADMITTED', ['ATTEMPT']),
    ('PIN_none', dict(pin_lines=[]), 'NOT_ADMITTED', ['PIN_ONCE']),
    ('PIN_two', dict(pin_lines=['GpuClockPin: mode 1', 'GpuClockPin: mode 1']), 'NOT_ADMITTED', ['PIN_ONCE']),
    ('PIN_mode2', dict(pin_lines=['GpuClockPin: mode 2']), 'NOT_ADMITTED', ['PIN_ONCE']),
    ('MARK_hang', dict(lines=['GpuHangAbort: role=4']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_error', dict(lines=['--- Error ---']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_fatal', dict(lines=['--- Fatal Error ---']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_skipped', dict(lines=['AsyncPipelines: skipped draw 5']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_slow', dict(lines=['GpuWaitSlow: 8 s']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_stdout', dict(stdout='Unhandled exception: 0xC0000005'), 'NOT_ADMITTED', ['NO_MARKER']),
    ('ROWS_edge_fail', dict(pre=1399, blocks=40), 'NOT_ADMITTED', ['ROWS']),            # 1 399 + 3 600 = 4 999
    ('ROWS_edge_ok', dict(pre=1400, blocks=40), 'GO', []),                              # 1 400 + 3 600 = 5 000
    ('ROWS_field', dict(drop_field=True), 'NOT_ADMITTED', ['ROWS']),
    ('GATEARM_edge_fail', dict(pre=1600, blocks=39), 'NOT_ADMITTED', ['GATEARM']),
    ('GATEARM_text', dict(arm_line=GOOD_TEXT.replace('daguard=1', 'daguard=0')), 'NOT_ADMITTED', ['GATEARM']),
    ('GATEARM_abba', dict(arm_line=GOOD_TEXT.replace('abba=1', 'abba=0')), 'NOT_ADMITTED', ['GATEARM']),
    ('GATEARM_period', dict(arm_line=GOOD_TEXT.replace('period=90', 'period=60')), 'NOT_ADMITTED', ['GATEARM']),
    ('GATEARM_arms', dict(arm_line=GOOD_TEXT.replace('arms=2', 'arms=3')), 'NOT_ADMITTED', ['GATEARM']),
    ('ARMED_arm0_leak10', dict(leak_pos=10), 'NOT_ADMITTED', ['ARMED_ARM0']),
    ('ARMED_arm1_leak10', dict(leak1_pos=10), 'NOT_ADMITTED', ['ARMED_ARM1']),
    ('GO_leak1_pos9', dict(leak1_pos=9), 'GO', []),
    ('ARMED_arm0_leak89', dict(leak_pos=89), 'NOT_ADMITTED', ['ARMED_ARM0']),
    ('GO_leak_pos90', dict(leak_pos=90, block_len=92), 'GO', []),                     # a long block's tail
    ('ARMED_arm0_dark', dict(q=0), 'NOT_ADMITTED', ['ARMED_ARM0', 'ARMED_ARM1']),
    ('CHECKED_edge_fail', dict(chk=9899, hit=10000), 'NOT_ADMITTED', ['CHECKED']),
    ('CHECKED_edge_ok', dict(chk=9900, hit=10000), 'GO', []),
    ('CHECKED_none', dict(chk=0), 'NOT_ADMITTED', ['CHECKED']),
    ('DEFAULTS_free', dict(free_hit=0), 'NOT_ADMITTED', ['DEFAULTS']),
    ('DEFAULTS_bad', dict(free_bad=1), 'NOT_ADMITTED', ['DEFAULTS']),
]
ok = True
# the constants of the rule (the sealed seal values PRED_SHA/PRED_BYTES are not pinned here)
CONSTANTS = dict(MIN_ROWS=5000, MIN_BLOCKS=40, MIN_MAIN_ROWS=1000, CHECK_RATIO=0.99, MAIN=(10, 89), HOLD_S=300,
                 PERIOD=90, ARM_TEXT=('dawalk=1 dawalklead=1 daslot=0 daguard=0', 'dawalk=1 dawalklead=1 daslot=1 daguard=1'),
                 BINARY_SHA='b47b58a997b441478ab1d278c992949d79795014370d034b747d5fd4e7b9f7f7', TAG='vdg112')
differ = [k for k, v in CONSTANTS.items() if getattr(mod, k) != v]
print('%-20s %s %s' % ('CONSTANTS', differ or 'match', 'OK' if not differ else 'FAIL'))
ok &= not differ
for name, kw, want, errs in cases:
    out = make(name, **kw)
    passed = out['verdict'] == want and out['errors'] == errs
    ok &= passed
    print('%-20s want %-12s got %-12s bad %s errors %s %s' % (name, want, out['verdict'], out.get('bad'), out['errors'],
                                                               'OK' if passed else 'FAIL'))
# arm-row edges: exactly MIN_MAIN_ROWS passes, one more fails
base = make('ARM_ROWS_probe')
saved = mod.MIN_MAIN_ROWS
mod.MIN_MAIN_ROWS = min(base['arm_rows'])
out = mod.evaluate(str(BASE / 'ARM_ROWS_probe'), installed_sha=mod.BINARY_SHA)
passed = out['verdict'] == 'GO'
mod.MIN_MAIN_ROWS = min(base['arm_rows']) + 1
out2 = mod.evaluate(str(BASE / 'ARM_ROWS_probe'), installed_sha=mod.BINARY_SHA)
passed &= out2['errors'] == ['ARM_ROWS']
mod.MIN_MAIN_ROWS = saved
print('%-20s rows %s edge ok %s edge+1 %s %s' % ('ARM_ROWS_edges', base['arm_rows'], out['verdict'], out2['errors'],
                                                 'OK' if passed else 'FAIL'))
ok &= passed
# predictions: values and HIT/MISS on the base run
base = make('PRED_values', yields=101)
pv = {p['name']: (p['value'], p['hit']) for p in base['predictions']}
passed = (pv['D1'] == (0, True) and pv['D2'] == (1080.0, True) and pv['D3'] == (1080.0, True)
          and pv['D4'] == (101, False) and pv['D5'][1] is True)
print('%-20s %s %s' % ('PRED_values', pv, 'OK' if passed else 'FAIL'))
ok &= passed
saved = (mod.PRED_SHA, mod.PRED_BYTES)
mod.PRED_SHA = None
out = make('DRAFT')
passed = out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['DRAFT']
print('%-20s errors %s %s' % ('DRAFT', out['errors'], 'OK' if passed else 'FAIL'))
ok &= passed
mod.PRED_SHA, mod.PRED_BYTES = saved[0], saved[1] + 1
out = make('SEAL')
passed = out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['SEAL']
print('%-20s errors %s %s' % ('SEAL', out['errors'], 'OK' if passed else 'FAIL'))
ok &= passed
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
