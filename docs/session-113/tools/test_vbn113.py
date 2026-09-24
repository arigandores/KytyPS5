"""Session 113: fixtures for vbn113.py - every verdict branch, every admission term alone (exact error set), both sides of
every threshold, both edges of every prediction band, the constants.
    python test_vbn113.py <vbn113.py>
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_vbn113')
NL = chr(10)
spec = importlib.util.spec_from_file_location('vbn113', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
seal = BASE / 'seal.md'
seal.write_bytes(b'fixture seal 113 vbn')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
GATES = 'dawalk=1 smemocheck=0 dabatch=8 fslean=0'


def make(name, rows=9000, stable=300, installed=None, scan=1068, ginv=1, would=1100, nmiss=0, nxthr=0, nskip=0,
         evict=1, qfree=1100, hit=266, free_bad=0, lines=(), stdout=None, tag='vbn113', **bad):
    d = BASE / name
    d.mkdir()
    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}
    env.update(bad.get('env', {}))
    for k in bad.get('env_drop', ()):
        env.pop(k, None)
    att = {'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None, 'hold_s': 300.1, 'stable_frame': stable}
    att.update(bad.get('att', {}))
    meta = {'binary_sha256': bad.get('binary', mod.BINARY_SHA), 'env': env,
            'gates': bad.get('gates', GATES + mod.TAIL),
            'prereg': bad.get('prereg', {'sha256': mod.PRED_SHA, 'bytes': mod.PRED_BYTES}),
            'attempts': bad.get('atts', [att] * bad.get('n_att', 1))}
    if not bad.get('no_meta'):
        (d / (tag + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    out = list(bad.get('pin_lines', ['GpuClockPin: mode 1'])) + list(lines)
    for n in range(1, rows + 1):
        # the start: 300 rows of a different scan level (excluded by the stable frame)
        s = scan if n >= stable else bad.get('start_scan', 52)
        out.append('FrameTrace-draw: n=%d draws=5000 bda_scan=%d bda_skip=20000 da_hit=8000' % (n, s))
        f = ('bda_ginv_reg=%d bda_ginv_map=0 bda_rinv=3 bda_nskip=%d bda_nwould=%d bda_nmiss=%d bda_nxthr=%d '
             'bgc_evict=%d da_q_free=%d cspfree_hit=%d cspfree_bad=%d') % (
                 ginv, nskip if n == 5000 else 0, would, nmiss if n == 4000 else 0, nxthr if n == 4100 else 0,
                 evict, qfree, hit, free_bad if n == 3500 else 0)
        if bad.get('drop_field') and n == 3000:
            f = f.replace('bda_nmiss=', 'bda_nmisX=')
        out.append('FrameTrace-x: n=%d rt_att=100 %s' % (n, f))
    (d / ('log_%s.txt' % tag)).write_bytes((NL.join(out) + NL).encode('utf-8'))
    if stdout is not None:
        (d / ('stdout_%s.txt' % tag)).write_bytes((stdout + NL).encode('utf-8'))
    return mod.evaluate(str(d), tag, installed_sha=installed or mod.BINARY_SHA)


cases = [
    ('GO', dict(), 'GO', []),
    ('GO_tag_b', dict(tag='vbn113b'), 'GO', []),
    ('GO_stdout_clean', dict(stdout='0xe06d7363 C++ exception (not a marker)'), 'GO', []),
    ('GO_start_old_excluded', dict(start_scan=5000), 'GO', []),
    ('NO_GO_miss', dict(nmiss=1), 'NO_GO', []),
    ('NO_GO_xthr', dict(nxthr=1), 'NO_GO', []),
    ('NOT_EVALUABLE_new', dict(scan=52), 'NOT_EVALUABLE', []),
    ('REGIME_edge_ok', dict(scan=500), 'GO', []),
    ('REGIME_edge_new', dict(scan=499), 'NOT_EVALUABLE', []),
    ('REGIME_start_only', dict(scan=52, start_scan=1068), 'NOT_EVALUABLE', []),
    ('REGIME_start_long', dict(rows=5000, stable=3000, scan=1068, start_scan=52), 'GO', []),   # the start is excluded
    ('ATT_extra_failed', dict(atts=[{'outcome': 'hang', 'hold_exit': None, 'hold_s': 300.1},
                                    {'outcome': 'ok', 'hold_exit': None, 'hold_s': 300.1, 'stable_frame': 300}]),
     'NOT_ADMITTED', ['ATTEMPT']),
    ('TAG', dict(tag='vbn113c'), 'NOT_ADMITTED', ['TAG']),
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
    ('GATES_mode1', dict(gates=GATES + ' bdanarrow=1'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_twice', dict(gates=GATES + ' bdanarrow=0' + ' bdanarrow=2'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_first', dict(gates='bdanarrow=0 ' + GATES + ' bdanarrow=2'), 'NOT_ADMITTED', ['GATES']),
    ('ATT_outcome', dict(att={'outcome': 'hang'}), 'NOT_ADMITTED', ['ATTEMPT']),
    ('ATT_exit', dict(att={'hold_exit': 3}), 'NOT_ADMITTED', ['ATTEMPT']),
    ('ATT_hold_edge_fail', dict(att={'hold_s': 284.9}), 'NOT_ADMITTED', ['ATTEMPT']),
    ('ATT_hold_edge_ok', dict(att={'hold_s': 285.0}), 'GO', []),
    ('ATT_two', dict(n_att=2), 'NOT_ADMITTED', ['ATTEMPT']),
    ('PIN_none', dict(pin_lines=[]), 'NOT_ADMITTED', ['PIN_ONCE']),
    ('PIN_two', dict(pin_lines=['GpuClockPin: mode 1', 'GpuClockPin: mode 1']), 'NOT_ADMITTED', ['PIN_ONCE']),
    ('PIN_mode2', dict(pin_lines=['GpuClockPin: mode 2']), 'NOT_ADMITTED', ['PIN_ONCE']),
    ('MARK_hang', dict(lines=['GpuHangAbort: role=4']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_slow', dict(lines=['GpuWaitSlow: 8 s']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_lost', dict(lines=['vk::Result ErrorDeviceLost']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_error', dict(lines=['--- Error ---']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_fatal', dict(lines=['--- Fatal Error ---']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_skipped', dict(lines=['AsyncPipelines: skipped draw 5']), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_stdout', dict(stdout='Unhandled exception: 0xC0000005'), 'NOT_ADMITTED', ['NO_MARKER']),
    ('ROWS_edge_fail', dict(rows=4999), 'NOT_ADMITTED', ['ROWS']),
    ('ROWS_edge_ok', dict(rows=5000), 'GO', []),
    ('ROWS_field', dict(drop_field=True), 'NOT_ADMITTED', ['ROWS']),
    ('ARMED_ginv', dict(ginv=0), 'NOT_ADMITTED', ['ARMED']),
    ('ARMED_would_edge_fail', dict(rows=5000, would=0, lines=[]), 'NOT_ADMITTED', ['ARMED']),
    ('ARMED_nskip', dict(nskip=1), 'NOT_ADMITTED', ['ARMED']),
    ('DEFAULTS_slot', dict(qfree=0), 'NOT_ADMITTED', ['DEFAULTS']),
    ('DEFAULTS_free', dict(hit=0), 'NOT_ADMITTED', ['DEFAULTS']),
    ('DEFAULTS_bad', dict(free_bad=1), 'NOT_ADMITTED', ['DEFAULTS']),
]
ok = True
CONSTANTS = dict(TAGS=('vbn113', 'vbn113b'), TAIL=' bdanarrow=2', HOLD_S=300, MIN_ROWS=5000, REGIME_OLD=500,
                 MIN_WOULD=1000, BINARY_SHA='94362eae5e28fa68c6a9d5ed921510a1fb1caa2868b0aa220099ba333df4da92')
differ = [k for k, v in CONSTANTS.items() if getattr(mod, k) != v]
print('%-24s %s %s' % ('CONSTANTS', differ or 'match', 'OK' if not differ else 'FAIL'))
ok &= not differ
for name, kw, want, errs in cases:
    out = make(name, **kw)
    passed = out['verdict'] == want and out['errors'] == errs
    ok &= passed
    print('%-24s want %-13s got %-13s bad %s errors %s %s' % (name, want, out['verdict'], out.get('bad'),
                                                               out['errors'], 'OK' if passed else 'FAIL'))
# the MIN_WOULD edge on a real total: 5 000 rows x 1 = 5 000 >= 1 000; 999 rows cannot be admitted, so use would per row
out = make('ARMED_would_edge_ok', rows=5000, would=0, lines=[])
passed = out['errors'] == ['ARMED']
d2 = BASE / 'ARMED_would_exact'
out2 = make('ARMED_would_exact', would=0)
# patch the log: exactly MIN_WOULD would-skips on one row -> admitted; MIN_WOULD - 1 -> ARMED
log = (d2 / 'log_vbn113.txt').read_text(encoding='utf-8')
exact = log.replace('bda_nwould=0 bda_nmiss=0 bda_nxthr=0 bgc_evict=1 da_q_free=1100 cspfree_hit=266 cspfree_bad=0' + NL,
                    'bda_nwould=%d bda_nmiss=0 bda_nxthr=0 bgc_evict=1 da_q_free=1100 cspfree_hit=266 cspfree_bad=0' % mod.MIN_WOULD + NL, 1)
(d2 / 'log_vbn113.txt').write_text(exact, encoding='utf-8')
o3 = mod.evaluate(str(d2), 'vbn113', installed_sha=mod.BINARY_SHA)
passed &= o3['errors'] == [] and o3['total']['bda_nwould'] == mod.MIN_WOULD
under = log.replace('bda_nwould=0 bda_nmiss=0 bda_nxthr=0 bgc_evict=1 da_q_free=1100 cspfree_hit=266 cspfree_bad=0' + NL,
                    'bda_nwould=%d bda_nmiss=0 bda_nxthr=0 bgc_evict=1 da_q_free=1100 cspfree_hit=266 cspfree_bad=0' % (mod.MIN_WOULD - 1) + NL, 1)
(d2 / 'log_vbn113.txt').write_text(under, encoding='utf-8')
o4 = mod.evaluate(str(d2), 'vbn113', installed_sha=mod.BINARY_SHA)
passed &= o4['errors'] == ['ARMED']
print('%-24s exact %s under %s %s' % ('ARMED_would_edges', o3['errors'], o4['errors'], 'OK' if passed else 'FAIL'))
ok &= passed
# predictions: base values, then each band's both edges
base = make('PRED_base')
pv = {p['name']: (p['value'], p['hit']) for p in base['predictions']}
passed = (pv['B1'] == (0, True) and pv['B2'] == (1068, True) and pv['B3'] == (1.0, True)
          and pv['B4'] == (1100.0, True) and pv['B5'] == (1.0, True))
print('%-24s %s %s' % ('PRED_base', pv, 'OK' if passed else 'FAIL'))
ok &= passed
EDGES = [  # (fixture kwargs, prediction, expected hit)
    (dict(scan=800), 'B2', True), (dict(scan=799), 'B2', False), (dict(scan=1400), 'B2', True),
    (dict(scan=1401), 'B2', False), (dict(would=800), 'B4', True), (dict(would=799), 'B4', False),
    (dict(would=1400), 'B4', True), (dict(would=1401), 'B4', False), (dict(ginv=3), 'B3', True),
    (dict(ginv=4), 'B3', False), (dict(evict=3), 'B5', True), (dict(evict=4), 'B5', False),
    (dict(nmiss=1), 'B1', False),
]
for i, (kw, key, want) in enumerate(EDGES):
    o = make('PRED_edge_%d' % i, **kw)
    got = {p['name']: p['hit'] for p in o['predictions']}[key]
    passed = got == want
    ok &= passed
    print('%-24s %s %s want %s got %s %s' % ('PRED_edge_%d' % i, key, kw, want, got, 'OK' if passed else 'FAIL'))
# B3 / B5 lower edges need fractional per-row values: one event every 2 rows = 0.5, less = below
for key, field in (('B3', 'bda_ginv_reg'), ('B5', 'bgc_evict')):
    for rate, want in ((2, True), (3, False), (45, False)):   # 45: 9 events in 20 rows = 0.45 a row
        name = 'PRED_%s_low_%d' % (key, rate)
        o = make(name, **({'ginv': 1} if key == 'B5' else {}))
        p = BASE / name / 'log_vbn113.txt'
        lines = p.read_text(encoding='utf-8').split(NL)
        fixed = []
        for line in lines:
            if line.startswith('FrameTrace-x: n='):
                n = int(line.split('n=')[1].split()[0])
                hit_row = (n % 20 < 9) if rate == 45 else (n % rate == 0)
                line = line.replace(' %s=1 ' % field, ' %s=%d ' % (field, 1 if hit_row else 0))
            fixed.append(line)
        p.write_text(NL.join(fixed), encoding='utf-8')
        o = mod.evaluate(str(BASE / name), 'vbn113', installed_sha=mod.BINARY_SHA)
        got = {q['name']: q['hit'] for q in o['predictions']}[key]
        value = {q['name']: q['value'] for q in o['predictions']}[key]
        passed = got == want and (o['errors'] == [] or key == 'B3' and not want)
        ok &= passed
        print('%-24s value %.4f want %s got %s errors %s %s' % (name, value, want, got, o['errors'],
                                                                 'OK' if passed else 'FAIL'))
saved = (mod.PRED_SHA, mod.PRED_BYTES)
mod.PRED_SHA = None
out = make('DRAFT')
passed = out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['DRAFT']
print('%-24s errors %s %s' % ('DRAFT', out['errors'], 'OK' if passed else 'FAIL'))
ok &= passed
mod.PRED_SHA, mod.PRED_BYTES = saved[0], saved[1] + 1
out = make('SEAL')
passed = out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['SEAL']
print('%-24s errors %s %s' % ('SEAL', out['errors'], 'OK' if passed else 'FAIL'))
ok &= passed
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
