"""Session 113: fixtures for vbn113c.py (from test_vbn113b.py by make_vbn113c.py) - every verdict branch (GO, NO_GO, INVESTIGATE, NOT_EVALUABLE, NOT_ADMITTED),
every admission term alone (exact error set), both sides of every threshold, both edges of every prediction band, the
constants (not the seal values).
    python test_vbn113c.py <vbn113c.py>
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_vbn113c')
NL = chr(10)
spec = importlib.util.spec_from_file_location('vbn113c', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
seal = BASE / 'seal.md'
seal.write_bytes(b'fixture seal 113 vbn c')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
GATES = 'dawalk=1 smemocheck=0 dabatch=8 fslean=0'


def make(name, rows=9000, stable=300, installed=None, scan=1068, ginv=1, would=1100, nmiss=0, nxthr=0, nskip=0,
         evict=1, race=0, qfree=1100, hit=266, free_bad=0, lines=(), stdout=None, tag='vbn113c', gpu_util=0.0,
         row_edit=None, **bad):
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
    if gpu_util is not None:
        meta['pre_run'] = {'gpu_util_median': gpu_util, 'gpu_power_median': 18.0}
    if not bad.get('no_meta'):
        (d / (tag + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    out = list(bad.get('pin_lines', ['GpuClockPin: mode 1'])) + list(lines)
    skip_x = set(bad.get('skip_x', ()))
    extra_main = bad.get('extra_main', 0)
    for n in range(1, rows + 1):
        s = scan if n >= stable else bad.get('start_scan', 52)
        out.append('FrameTrace: n=%d dt_us=31000 cpu_gpu_us=30000 arm=0 blk=0' % n)
        out.append('FrameTrace-draw: n=%d draws=5000 bda_scan=%d bda_skip=20000 da_hit=8000' % (n, s))
        vals = dict(bda_ginv_reg=ginv, bda_ginv_map=0, bda_rinv=3, bda_nskip=nskip if n == 5000 else 0,
                    bda_nwould=would, bda_nmiss=nmiss if n == 4000 else 0, bda_nxthr=nxthr if n == 4100 else 0,
                    bgc_evict=evict, bda_nrace=race if n == 4200 else 0, da_q_free=qfree, cspfree_hit=hit,
                    cspfree_bad=free_bad if n == 3500 else 0)
        if row_edit is not None:
            row_edit(n, vals)
        f = ' '.join('%s=%d' % (k, v) for k, v in vals.items())
        if bad.get('drop_field') and n == 3000:
            f = f.replace('bda_nrace=', 'bda_nracX=')
        if n not in skip_x:
            out.append('FrameTrace-x: n=%d rt_att=100 %s' % (n, f))
    for i in range(extra_main):
        out.append('FrameTrace: n=%d dt_us=31000 cpu_gpu_us=30000 arm=0 blk=0' % (rows + 1 + i))
    (d / ('log_%s.txt' % tag)).write_bytes((NL.join(out) + NL).encode('utf-8'))
    if stdout is not None:
        (d / ('stdout_%s.txt' % tag)).write_bytes((stdout + NL).encode('utf-8'))
    return mod.evaluate(str(d), tag, installed_sha=installed or mod.BINARY_SHA)


def pattern(field, every):
    """Set `field` to 1 on rows n % every == 0 and 0 elsewhere (a median of 0 when every > 2)."""
    def edit(n, vals):
        vals[field] = 1 if n % every == 0 else 0
    return edit


cases = [
    ('GO', dict(), 'GO', []),
    ('GO_tag_d', dict(tag='vbn113d'), 'GO', []),
    ('GO_tag_e', dict(tag='vbn113e'), 'GO', []),
    ('GO_tag_f', dict(tag='vbn113f'), 'GO', []),
    ('GO_stdout_clean', dict(stdout='0xe06d7363 C++ exception (not a marker)'), 'GO', []),
    ('GO_start_old_excluded', dict(start_scan=5000), 'GO', []),
    ('INVESTIGATE_race', dict(race=1), 'INVESTIGATE', []),                     # a race may hide a real miss
    ('INVESTIGATE_race_xthr', dict(race=1, nxthr=1), 'INVESTIGATE', []),
    ('NO_GO_miss_and_race', dict(nmiss=1, race=1), 'NO_GO', []),
    ('NO_GO_miss', dict(nmiss=1), 'NO_GO', []),
    ('NO_GO_miss_and_xthr', dict(nmiss=1, nxthr=1), 'NO_GO', []),
    ('INVESTIGATE_xthr', dict(nxthr=1), 'INVESTIGATE', []),
    ('NOT_EVALUABLE_new', dict(scan=52), 'NOT_EVALUABLE', []),
    ('REGIME_edge_ok', dict(scan=500), 'GO', []),
    ('REGIME_edge_new', dict(scan=499), 'NOT_EVALUABLE', []),
    ('REGIME_start_only', dict(scan=52, start_scan=1068), 'NOT_EVALUABLE', []),
    ('REGIME_start_long', dict(rows=5000, stable=3000, scan=1068, start_scan=52), 'GO', []),
    ('TAG', dict(tag='vbn113g'), 'NOT_ADMITTED', ['TAG']),
    ('TAG_old', dict(tag='vbn113b'), 'NOT_ADMITTED', ['TAG']),
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
    ('ATT_extra_failed', dict(atts=[{'outcome': 'hang', 'hold_exit': None, 'hold_s': 300.1},
                                    {'outcome': 'ok', 'hold_exit': None, 'hold_s': 300.1, 'stable_frame': 300}]),
     'NOT_ADMITTED', ['ATTEMPT']),
    ('PRE_RUN_edge_ok', dict(gpu_util=10.0), 'GO', []),
    ('PRE_RUN_edge_fail', dict(gpu_util=10.1), 'NOT_ADMITTED', ['PRE_RUN']),
    ('PRE_RUN_missing', dict(gpu_util=None), 'NOT_ADMITTED', ['PRE_RUN']),
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
    ('STREAMS_gap', dict(skip_x=[6000]), 'NOT_ADMITTED', ['STREAMS']),               # one x row lost (glued or cut)
    ('STREAMS_main_extra_ok', dict(extra_main=1), 'GO', []),                          # the last flip's x row never prints
    ('STREAMS_main_extra_fail', dict(extra_main=2), 'NOT_ADMITTED', ['STREAMS']),
    ('ARMED_ginv', dict(ginv=0), 'NOT_ADMITTED', ['ARMED']),
    ('ARMED_would_zero', dict(rows=5000, would=0), 'NOT_ADMITTED', ['ARMED']),
    ('ARMED_nskip', dict(nskip=1), 'NOT_ADMITTED', ['ARMED']),
    ('DEFAULTS_slot', dict(qfree=0), 'NOT_ADMITTED', ['DEFAULTS']),
    ('DEFAULTS_free', dict(hit=0), 'NOT_ADMITTED', ['DEFAULTS']),
    ('DEFAULTS_bad', dict(free_bad=1), 'NOT_ADMITTED', ['DEFAULTS']),
]
ok = True
CONSTANTS = dict(TAGS=('vbn113c', 'vbn113d', 'vbn113e', 'vbn113f'), TAIL=' bdanarrow=2', HOLD_S=300, MIN_ROWS=5000, REGIME_OLD=500,
                 MIN_WOULD=1000, MAX_GPU_UTIL=10.0,
                 BINARY_SHA='7d9fa0288099204f16974292a0d474afee80e58df43770612e11b8d5db5d6e5f')
differ = [k for k, v in CONSTANTS.items() if getattr(mod, k) != v]
print('%-26s %s %s' % ('CONSTANTS', differ or 'match', 'OK' if not differ else 'FAIL'))
ok &= not differ
for name, kw, want, errs in cases:
    out = make(name, **kw)
    passed = out['verdict'] == want and out['errors'] == errs
    ok &= passed
    print('%-26s want %-13s got %-13s bad %s errors %s %s' % (name, want, out['verdict'], out.get('bad'),
                                                               out['errors'], 'OK' if passed else 'FAIL'))


def armed_edge(name, value):
    return make(name, row_edit=lambda n, vals: vals.__setitem__('bda_nwould', value if n == 4321 else 0))


o1 = armed_edge('ARMED_would_exact', mod.MIN_WOULD)
o2 = armed_edge('ARMED_would_under', mod.MIN_WOULD - 1)
passed = o1['errors'] == [] and o2['errors'] == ['ARMED']
print('%-26s exact %s under %s %s' % ('ARMED_would_edges', o1['errors'], o2['errors'], 'OK' if passed else 'FAIL'))
ok &= passed
base = make('PRED_base')
pv = {p['name']: (p['value'], p['hit']) for p in base['predictions']}
passed = (pv['B1'] == (0, True) and pv['B2'] == (1068, True) and pv['B3'] == (1, True) and pv['B4'] == (1100, True)
          and pv['B5'] == (1, True) and pv['B6'] == (0, True))
print('%-26s %s %s' % ('PRED_base', pv, 'OK' if passed else 'FAIL'))
ok &= passed
EDGES = [  # (fixture kwargs, prediction, expected hit)
    (dict(scan=800), 'B2', True), (dict(scan=799), 'B2', False), (dict(scan=1400), 'B2', True),
    (dict(scan=1401), 'B2', False), (dict(would=800), 'B4', True), (dict(would=799), 'B4', False),
    (dict(would=1400), 'B4', True), (dict(would=1401), 'B4', False), (dict(ginv=3), 'B3', True),
    (dict(ginv=4), 'B3', False), (dict(row_edit=pattern('bda_ginv_reg', 3)), 'B3', False),
    (dict(evict=3), 'B5', True), (dict(evict=4), 'B5', False), (dict(row_edit=pattern('bgc_evict', 3)), 'B5', False),
    (dict(race=40), 'B6', True), (dict(race=41), 'B6', False), (dict(race=0), 'B6', True), (dict(nmiss=1), 'B1', False),
    (dict(nxthr=1), 'B1', False),
]
for i, (kw, key, want) in enumerate(EDGES):
    o = make('PRED_edge_%d' % i, **kw)
    got = {p['name']: p['hit'] for p in o['predictions']}[key]
    passed = got == want
    ok &= passed
    print('%-26s %s want %s got %s %s' % ('PRED_edge_%d' % i, key, want, got, 'OK' if passed else 'FAIL'))
# B3/B5 are medians over the SCENE rows: a start phase of other values does not move them
o = make('PRED_median_scene', rows=5000, stable=3000,
         row_edit=lambda n, vals: vals.__setitem__('bgc_evict', 9 if n < 3000 else 1))
passed = {p['name']: p['value'] for p in o['predictions']}['B5'] == 1
print('%-26s B5 value %s %s' % ('PRED_median_scene', {p['name']: p['value'] for p in o['predictions']}['B5'],
                                'OK' if passed else 'FAIL'))
ok &= passed
o = make('PRED_median_scene_b3', rows=5000, stable=3000,
         row_edit=lambda n, vals: vals.__setitem__('bda_ginv_reg', 9 if n < 3000 else 1))
b3 = {p['name']: (p['value'], p['hit']) for p in o['predictions']}['B3']
passed = b3 == (1, True)   # the all-row mean would read 5.8 (a MISS)
print('%-26s B3 %s %s' % ('PRED_median_scene_b3', b3, 'OK' if passed else 'FAIL'))
ok &= passed
saved = (mod.PRED_SHA, mod.PRED_BYTES)
mod.PRED_SHA = None
out = make('DRAFT')
passed = out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['DRAFT']
print('%-26s errors %s %s' % ('DRAFT', out['errors'], 'OK' if passed else 'FAIL'))
ok &= passed
mod.PRED_SHA, mod.PRED_BYTES = saved[0], saved[1] + 1
out = make('SEAL')
passed = out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['SEAL']
print('%-26s errors %s %s' % ('SEAL', out['errors'], 'OK' if passed else 'FAIL'))
ok &= passed
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
