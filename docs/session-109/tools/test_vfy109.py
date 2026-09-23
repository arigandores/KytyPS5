"""Session 109: fixtures for vfy109.py - every verdict branch and every admission term alone (exact error set).
    python test_vfy109.py <vfy109.py>
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_vfy109')
NL = chr(10)
spec = importlib.util.spec_from_file_location('vfy109', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
seal = BASE / 'seal.md'
seal.write_bytes(b'fixture seal 109 vfy')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
GATES = 'dawalk=1 dabatch=8 fslean=0'


def make(name, hit=250, look=266, bad_rows=0, moved=0, rows=9000, installed=None, early_hit=None, **bad):
    d = BASE / name
    d.mkdir()
    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_PIPELINE_PRECACHE': 'gfx', 'KYTY_GPU_CLOCK_PIN': '1',
           'KYTY_GPU_MARKERS': '0'}
    env.update(bad.get('env', {}))
    for k in bad.get('env_drop', ()):
        env.pop(k, None)
    att = {'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None, 'hold_s': 300.1}
    att.update(bad.get('att', {}))
    meta = {'binary_sha256': bad.get('binary', mod.BINARY_SHA), 'env': env,
            'gates': bad.get('gates', GATES + ' ' + mod.TOKEN),
            'prereg': bad.get('prereg', {'sha256': mod.PRED_SHA, 'bytes': mod.PRED_BYTES}),
            'attempts': [att] * bad.get('n_att', 1)}
    if not bad.get('no_meta'):
        (d / (mod.TAG + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    lines = ['GpuClockPin: mode 1'] * bad.get('pins', 1)
    lines.append('PipelinePrecache: 641 recipes -> 520 graphics + %d compute pipelines queued, 121 skipped'
                 % bad.get('queued', 0))
    if 'marker' in bad:
        lines.append(bad['marker'])
    for n in range(1, rows + 1):
        b = 1 if n <= bad_rows else 0
        h = early_hit if (early_hit is not None and n < mod.STEADY_FROM) else hit
        fields = ('cs_sync_new=0 cs_sync_wait=0 cspf_new=0 cspf_have=266 cspfree_look=%d cspfree_hit=%d '
                  'cspfree_src_miss=0 cspfree_spec_miss=%d cspfree_mat_fail=0 cspfree_clr=0 cspfree_store=0 '
                  'cspfree_bad=%d cspfree_moved=%d') % (look, h, look - h, b, moved)
        if bad.get('drop_field') and n == 3000:
            fields = fields.replace('cspfree_moved=', 'cspfree_movex=')
        lines.append('FrameTrace-x: n=%d rt_att=100 %s' % (n, fields))
    (d / ('log_%s.txt' % mod.TAG)).write_bytes((NL.join(lines) + NL).encode('utf-8'))
    return mod.evaluate(str(d), installed_sha=installed or mod.BINARY_SHA)


cases = [
    ('GO', dict(), 'GO', []),
    ('GO_edge', dict(hit=900, look=1000), 'GO', []),            # rate exactly 0.9
    ('GO_moved', dict(moved=1), 'GO', []),                      # moved is benign
    ('NO_GO_bad', dict(bad_rows=1), 'NO_GO', []),
    ('GO_load_miss', dict(early_hit=0), 'GO', []),                # misses only before the steady part
    ('NO_GO_rate', dict(hit=899, look=1000), 'NO_GO', []),
    ('IDENTITY', dict(installed='0' * 64), 'NOT_ADMITTED', ['IDENTITY']),
    ('INPUTS', dict(no_meta=True), 'NOT_ADMITTED', ['INPUTS']),
    ('BINARY', dict(binary='1' * 64), 'NOT_ADMITTED', ['BINARY']),
    ('PREREG', dict(prereg={'sha256': '0' * 64, 'bytes': 1}), 'NOT_ADMITTED', ['PREREG']),
    ('ENV_PRECACHE', dict(env_drop=['KYTY_PIPELINE_PRECACHE']), 'NOT_ADMITTED', ['ENV_PRECACHE']),
    ('ENV_PIN', dict(env_drop=['KYTY_GPU_CLOCK_PIN']), 'NOT_ADMITTED', ['ENV_PIN']),
    ('ENV_SCHED', dict(env={'KYTY_GATE_SCHEDULE': 'x'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN']),
    ('ENV_CKPT', dict(env={'KYTY_GPU_CHECKPOINTS': '0'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN']),
    ('ENV_REC', dict(env={'KYTY_REC': 'x.mp4'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN']),
    ('GATES_missing', dict(gates=GATES), 'NOT_ADMITTED', ['GATES']),
    ('GATES_value', dict(gates=GATES + ' cspfree=1'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_twice', dict(gates=GATES + ' cspfree=0 cspfree=2'), 'NOT_ADMITTED', ['GATES']),
    ('ATT_outcome', dict(att={'outcome': 'hang'}), 'NOT_ADMITTED', ['ATTEMPT']),
    ('ATT_exit', dict(att={'hold_exit': 3}), 'NOT_ADMITTED', ['ATTEMPT']),
    ('ATT_hold', dict(att={'hold_s': 200.0}), 'NOT_ADMITTED', ['ATTEMPT']),
    ('ATT_two', dict(n_att=2), 'NOT_ADMITTED', ['ATTEMPT']),
    ('PIN_none', dict(pins=0), 'NOT_ADMITTED', ['PIN_ONCE']),
    ('PIN_two', dict(pins=2), 'NOT_ADMITTED', ['PIN_ONCE']),
    ('PRECACHE_on', dict(queued=121), 'NOT_ADMITTED', ['PRECACHE_OFF']),
    ('MARK_hang', dict(marker='GpuHangAbort: role=4'), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_error', dict(marker='--- Error ---'), 'NOT_ADMITTED', ['NO_MARKER']),
    ('MARK_skipped', dict(marker='AsyncPipelines: skipped draw 5'), 'NOT_ADMITTED', ['NO_MARKER']),
    ('ROWS_few', dict(rows=4000), 'NOT_ADMITTED', ['ROWS']),
    ('ROWS_field', dict(drop_field=True), 'NOT_ADMITTED', ['ROWS']),
    ('ARMED', dict(hit=0, look=0), 'NOT_ADMITTED', ['ARMED']),
]
ok = True
for name, kw, want, errs in cases:
    out = make(name, **kw)
    passed = out['verdict'] == want and out['errors'] == errs
    ok &= passed
    print('%-14s want %-12s got %-12s bad %s rate %.4f errors %s %s' % (name, want, out['verdict'], out.get('bad'),
                                                                     out.get('hit_rate', 0.0), out['errors'],
                                                                     'OK' if passed else 'FAIL'))
saved = (mod.PRED_SHA, mod.PRED_BYTES)
mod.PRED_SHA = None
out = make('DRAFT')
passed = out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['DRAFT']
print('%-14s errors %s %s' % ('DRAFT', out['errors'], 'OK' if passed else 'FAIL'))
ok &= passed
mod.PRED_SHA, mod.PRED_BYTES = saved[0], saved[1] + 1
out = make('SEAL')
passed = out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['SEAL']
print('%-14s errors %s %s' % ('SEAL', out['errors'], 'OK' if passed else 'FAIL'))
ok &= passed
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
