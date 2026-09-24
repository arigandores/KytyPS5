"""Session 111: fixtures for obs111.py.  Rule (session-107 audit item 8, decision after 107): every verdict branch
and every admission term ALONE, each case asserting the verdict AND the exact error list; exact per-flip numbers on
a known synthetic log (window filter n >= 2100, per-flip division, tag mapping, ratio-of-sums shares); the
prediction bands at their edges.  Fixtures are written under <this dir>/fx/<scorer stem> and removed at the end
(--keep keeps them).
    python test_obs111.py [<obs111.py path>] [--keep]
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
HERE = Path(__file__).resolve().parent
SRC = Path(ARGS[0]) if ARGS else HERE / 'obs111.py'
BASE = HERE / 'fx' / SRC.stem
NL = chr(10)
spec = importlib.util.spec_from_file_location('obs111_under_test', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BINARY = '072861c89193c3726232e44e78be4f36172254af826394b56c8bf671ef609c21'
START = 2100
GATES = ('copy=1 srtpages=1 clamp=1 drawahead=1 dawalk=1 recordthread=1 fslean=0 recpin=1 dapin=3 dabatch=8 '
         'dawalklead=1 pfcap=1024 plkstat=1')
ok = True


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    print('%-22s %s %s' % (name, 'OK' if cond else 'FAIL', detail))


# ---- the sealed constants (a mutant of a constant dies here even when no fixture reaches it) ----
check('CONSTANTS', (mod.BINARY_SHA == BINARY and mod.PRODUCTION_ROOT == 'C:/kyty/s111'
                    and mod.PRED == 'C:/kyty/s111/pred/01_obs111.md'
                    and mod.GATES_FILE == 'C:/kyty/s111/gates_obs111.txt'
                    and mod.INSTALLED == 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
                    and mod.START == 2100 and mod.MIN_ROWS == 5000 and mod.MIN_HOLD_S == 285.0
                    and mod.RULE_US == 100.0 and mod.TAG == 'obs111'))

if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
seal = BASE / 'seal.md'
seal.write_bytes(b'fixture seal 111 obs')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
SEAL_PINS = (mod.PRED, mod.PRED_SHA, mod.PRED_BYTES)

# per-row values: h0..h3 the contended wall by holder tag (ns), hKn the acquisitions by tag, cpu the thread CPU of
# the contended waits, wq/wqn and wp/wpn the walker's holds, then the cspfree / prefetch counters
BASE_ROW = dict(h0=5000, h1=150000, h2=10000, h3=35000, h0n=11, h1n=200, h2n=23, h3n=66, cpu=160000,
                wq=1000000, wqn=1000, wp=5000, wpn=5, hit=250, look=266, have=16, new=2, bad=0)
SPIKE = dict(h1=5000000, h1n=500, cpu=-20000, wq=2000000, wqn=1000, hit=5000)     # added to row n = 2100 only
PRE_ROW = dict(h0=1000, h1=900000, h2=500000, h3=1000, h0n=1, h1n=1, h2n=1, h3n=1, cpu=10000, wq=7000000, wqn=10,
               wp=900000, wpn=100, hit=3, look=4, have=999, new=7, bad=0)       # rows 2000..2099, outside the window


def x_line(n, v, drop):
    f = [('rt_att', 100), ('cspm_look', 0), ('cspfam_look', 0), ('cs_sync_new', 0),
         ('pl_cont_n', v['h0n'] + v['h1n'] + v['h2n'] + v['h3n']),
         ('pl_cont_wall_ns', v['h0'] + v['h1'] + v['h2'] + v['h3']), ('pl_cont_cpu_ns', v['cpu']),
         ('pl_cont_h0_n', v['h0n']), ('pl_cont_h0_ns', v['h0']), ('pl_cont_h1_n', v['h1n']),
         ('pl_cont_h1_ns', v['h1']), ('pl_cont_h2_n', v['h2n']), ('pl_cont_h2_ns', v['h2']),
         ('pl_cont_h3_n', v['h3n']), ('pl_cont_h3_ns', v['h3']), ('pl_wq_hold_ns', v['wq']),
         ('pl_wq_hold_n', v['wqn']), ('pl_wp_hold_ns', v['wp']), ('pl_wp_hold_n', v['wpn']), ('cspm_would', 0),
         ('cspf_have', v['have']), ('cspf_new', v['new']), ('cspfam_skip', 0), ('cspfree_look', v['look']),
         ('cspfree_hit', v['hit']), ('cspfree_bad', v['bad']), ('cs_sync_new_us', 0)]
    return 'FrameTrace-x: n=%d ' % n + ' '.join('%s=%d' % kv for kv in f if kv[0] != drop)


_ROWS = {}


def row_text(rows, pre, base, spike, over, drop):
    key = repr((rows, pre, sorted(base.items()), sorted(spike.items()), sorted(over.items()), sorted(drop.items())))
    if key not in _ROWS:
        out = []
        for n in range(START - pre, START + rows):
            if n < START:
                v = dict(PRE_ROW)
            else:
                v = dict(base)
                if n == START:
                    for k, dv in spike.items():
                        v[k] += dv
            v.update(over.get(n, {}))
            out.append('FrameTrace: n=%d dt_us=31000 cpu_gpu_us=30000 draws=5000 dispatches=250' % n)
            out.append(x_line(n, v, drop.get(n)))
        _ROWS[key] = NL.join(out)
    return _ROWS[key]


def make(name, rows=5000, pre=100, base=None, spike=None, over=None, drop=None, pins=None, marker=None,
         stdout_marker=None, env=None, env_drop=(), gates=GATES, att=None, n_att=1, binary=BINARY, prereg='pin',
         no_log=False, no_meta=False, meta_text=None):
    d = BASE / name
    d.mkdir()
    b = dict(BASE_ROW)
    b.update(base or {})
    s = dict(SPIKE)
    s.update(spike or {})
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GATE_FILE': 'C:\\kyty\\s111\\gates.req',
         'KYTY_QUEUE_TRACE': '1', 'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden', 'KYTY_GPU_CLOCK_PIN': '1',
         'KYTY_GPU_MARKERS': '0'}
    e.update(env or {})
    for k in env_drop:
        e.pop(k)
    a = {'label': 'attempt 1', 'attempt': 1, 'outcome': 'ok', 'detail': None, 'hold_exit': None, 'hold_s': 300.1}
    a.update(att or {})
    if prereg == 'pin':
        prereg = {'path': SEAL_PINS[0], 'bytes': SEAL_PINS[2], 'sha256': SEAL_PINS[1]}
    meta = {'tag': 'obs111', 'binary_sha256': binary, 'env': e, 'gates': gates, 'attempts': [a] * n_att,
            'launched': '2026-09-24T12:00:00', 'hold_s': 300}
    if prereg is not None:
        meta['prereg'] = prereg
    if binary is None:
        meta.pop('binary_sha256')
    if not no_meta:
        (d / 'obs111.json').write_text(meta_text if meta_text is not None else json.dumps(meta), encoding='utf-8')
    head = ['RecordThread: started recorder=0x1 arena=65536KiB gpu=0',
            'RecordThread: started recorder=0x2 arena=65536KiB gpu=1']
    head += pins if pins is not None else [
        'GpuClockPin: mode 1 - the guest GPU clock ignores the pacer speed (KYTY_GPU_CLOCK_PIN)']
    head += ['Gate: plkstat=1 frame=1', 'PipelinePrecache: 641 recipes -> 520 graphics + 121 compute pipelines queued']
    text = NL.join(head) + NL + row_text(rows, pre, b, s, over or {}, drop or {}) + NL
    if marker is not None:
        text += marker + NL
    text += 'VideoOut: flip queue closed' + NL
    if not no_log:
        (d / 'log_obs111.txt').write_bytes(text.encode('utf-8'))
    (d / 'stdout_obs111.txt').write_bytes(('Vulkan: device selected' + NL + (stdout_marker + NL if stdout_marker
                                                                             else '')).encode('utf-8'))
    return d


def run(name, installed=BINARY, **kw):
    return mod.evaluate(str(make(name, **kw)), 'obs111', installed)


DEFAULT_NUMBERS = {
    'rows': 5000, 'rows_all': 5100, 'rows_missing': 0,
    'cont_wall_us': 201.0, 'tag1_us': 151.0, 'tag2_us': 10.0, 'tag03_us': 40.0, 'tag_residual_ns': 0,
    'cont_n': 300.1, 'cont_n_tag': {'0': 11.0, '1': 200.1, '2': 23.0, '3': 66.0},
    'spin_share': 0.796, 'tag1_share': 755000000 / 1005000000, 'tag2_share': 50000000 / 1005000000,
    'wq_hold_us': 1000.4, 'wq_n': 1000.2, 'wq_call_us': 5002000000 / 5001000 / 1000.0,
    'wp_hold_us': 5.0, 'wp_n': 5.0, 'cspfree_hit': 251.0, 'cspfree_look': 266.0, 'cspf_have': 16.0, 'cspf_new': 2.0,
    'cspfree_bad_all': 0,
}
DEFAULT_PRED = {'P1': True, 'P2': False, 'P3': True, 'P4': True, 'P5': True}
ZERO_CONT = dict(h0=0, h1=0, h2=0, h3=0, h0n=0, h1n=0, h2n=0, h3n=0, cpu=0)
ZERO_CONT_SPIKE = dict(h1=0, h1n=0, cpu=0)
P_EDGE = dict(h0=500, h1=126500, h2=20000, h3=2000, wp=20000, cpu=100000)   # wall 150.0, share 0.85, tag2 20, wp 20
P_TOP = dict(h0=500, h1=250000, h2=20000, h3=48500, wp=20000, cpu=100000)   # wall 320.0

# (name, make kwargs, verdict, errors, {readout: exact value}, {prediction: hit})
cases = [
    # verdict branches and the exact numbers of the known log
    ('BUILD', dict(), 'BUILD_DASLOT', [], DEFAULT_NUMBERS, DEFAULT_PRED),
    ('BUILD_edge', dict(base=dict(h1=99000)), 'BUILD_DASLOT', [], {'tag1_us': 100.0}, {'P5': True}),
    ('LOCK_edge', dict(base=dict(h1=99000), spike=dict(h1=4999999)), 'LOCK_DONE', [],
     {'tag1_us': 499999999 / 5000 / 1000.0}, {'P5': False}),
    ('LOCK', dict(base=dict(h1=50000)), 'LOCK_DONE', [],
     {'tag1_us': 51.0, 'cont_wall_us': 101.0, 'tag2_us': 10.0, 'tag03_us': 40.0,
      'spin_share': 799980000 / 505000000, 'tag1_share': 255000000 / 505000000}, {'P3': False, 'P5': False}),
    # the prediction bands at their edges (never deciding)
    ('P_edges', dict(base=P_EDGE), 'BUILD_DASLOT', [],
     {'tag2_us': 20.0, 'tag1_share': 0.85, 'cont_wall_us': 150.0, 'wp_hold_us': 20.0, 'tag1_us': 127.5},
     {'P1': True, 'P2': True, 'P3': True, 'P4': True, 'P5': True}),
    ('P1_over', dict(base=P_EDGE, spike=dict(h2=1)), 'BUILD_DASLOT', [], {'tag2_us': 100000001 / 5000 / 1000.0},
     {'P1': False}),
    ('P2_under', dict(base=P_EDGE, spike=dict(h0=1)), 'BUILD_DASLOT', [], {'tag1_share': 637500000 / 750000001},
     {'P2': False, 'P3': True}),
    ('P3_under', dict(base=P_EDGE, spike=dict(h0=-1)), 'BUILD_DASLOT', [],
     {'cont_wall_us': 749999999 / 5000 / 1000.0}, {'P2': True, 'P3': False}),
    ('P3_top', dict(base=P_TOP), 'BUILD_DASLOT', [], {'cont_wall_us': 320.0}, {'P3': True}),
    ('P3_over', dict(base=P_TOP, spike=dict(h3=1)), 'BUILD_DASLOT', [], {'cont_wall_us': 1600000001 / 5000 / 1000.0},
     {'P3': False}),
    ('P4_over', dict(base=P_EDGE, spike=dict(wp=1)), 'BUILD_DASLOT', [], {'wp_hold_us': 100000001 / 5000 / 1000.0},
     {'P4': False}),
    # IDENTITY / INPUTS / BINARY / PREREG
    ('IDENTITY', dict(installed='0' * 64), 'NOT_ADMITTED', ['IDENTITY'], {}, {}),
    ('IDENTITY_none', dict(installed=None), 'NOT_ADMITTED', ['IDENTITY'], {}, {}),
    ('INPUTS_log', dict(no_log=True), 'NOT_ADMITTED', ['INPUTS'], {}, {}),
    ('INPUTS_meta', dict(no_meta=True), 'NOT_ADMITTED', ['INPUTS'], {}, {}),
    ('INPUTS_json', dict(meta_text='{"tag": "obs111", '), 'NOT_ADMITTED', ['INPUTS'], {}, {}),
    ('INPUTS_list', dict(meta_text='[1, 2]'), 'NOT_ADMITTED', ['INPUTS'], {}, {}),
    ('BINARY', dict(binary='1' * 64), 'NOT_ADMITTED', ['BINARY'], {}, {}),
    ('BINARY_missing', dict(binary=None), 'NOT_ADMITTED', ['BINARY'], {}, {}),
    ('PREREG_sha', dict(prereg={'sha256': '0' * 64, 'bytes': SEAL_PINS[2]}), 'NOT_ADMITTED', ['PREREG'], {}, {}),
    ('PREREG_bytes', dict(prereg={'sha256': SEAL_PINS[1], 'bytes': SEAL_PINS[2] + 1}), 'NOT_ADMITTED', ['PREREG'],
     {}, {}),
    ('PREREG_missing', dict(prereg=None), 'NOT_ADMITTED', ['PREREG'], {}, {}),
    # environment
    ('ENV_PIN_drop', dict(env_drop=('KYTY_GPU_CLOCK_PIN',)), 'NOT_ADMITTED', ['ENV_PIN'], {}, {}),
    ('ENV_PIN_2', dict(env={'KYTY_GPU_CLOCK_PIN': '2'}), 'NOT_ADMITTED', ['ENV_PIN'], {}, {}),
    ('ENV_SCHED', dict(env={'KYTY_GATE_SCHEDULE': ''}), 'NOT_ADMITTED', ['ENV_FORBIDDEN'], {}, {}),
    ('ENV_CKPT', dict(env={'KYTY_GPU_CHECKPOINTS': '0'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN'], {}, {}),
    ('ENV_REC', dict(env={'KYTY_REC': 'C:/kyty/s111/rec.mp4'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN'], {}, {}),
    # gate text
    ('GATES_plk_first', dict(gates='plkstat=1 ' + GATES[:-len(' plkstat=1')]), 'BUILD_DASLOT', [], {}, {}),
    ('GATES_plk_none', dict(gates=GATES[:-len(' plkstat=1')]), 'NOT_ADMITTED', ['GATES_PLKSTAT'], {}, {}),
    ('GATES_plk_twice', dict(gates=GATES + ' plkstat=1'), 'NOT_ADMITTED', ['GATES_PLKSTAT'], {}, {}),
    ('GATES_plk_zero', dict(gates=GATES.replace('plkstat=1', 'plkstat=0 plkstat=1')), 'NOT_ADMITTED',
     ['GATES_PLKSTAT'], {}, {}),
    ('GATES_plk_ten', dict(gates=GATES + '0'), 'NOT_ADMITTED', ['GATES_PLKSTAT'], {}, {}),
    ('GATES_cspfree', dict(gates=GATES + ' cspfree=1'), 'NOT_ADMITTED', ['GATES_DEFAULTS'], {}, {}),
    ('GATES_cspmemo', dict(gates=GATES + ' cspmemo=0'), 'NOT_ADMITTED', ['GATES_DEFAULTS'], {}, {}),
    ('GATES_cspfam', dict(gates='cspfam=0 ' + GATES), 'NOT_ADMITTED', ['GATES_DEFAULTS'], {}, {}),
    # the attempt
    ('ATT_outcome', dict(att={'outcome': 'hang'}), 'NOT_ADMITTED', ['ATTEMPT'], {}, {}),
    ('ATT_exit', dict(att={'hold_exit': 3}), 'NOT_ADMITTED', ['ATTEMPT'], {}, {}),
    ('ATT_exit0', dict(att={'hold_exit': 0}), 'NOT_ADMITTED', ['ATTEMPT'], {}, {}),
    ('ATT_hold', dict(att={'hold_s': 284.9}), 'NOT_ADMITTED', ['ATTEMPT'], {}, {}),
    ('ATT_hold_edge', dict(att={'hold_s': 285.0}), 'BUILD_DASLOT', [], {}, {}),
    ('ATT_hold_none', dict(att={'hold_s': None}), 'NOT_ADMITTED', ['ATTEMPT'], {}, {}),
    ('ATT_two', dict(n_att=2), 'NOT_ADMITTED', ['ATTEMPT'], {}, {}),
    ('ATT_zero', dict(n_att=0), 'NOT_ADMITTED', ['ATTEMPT'], {}, {}),
    # the clock pin line
    ('PIN_none', dict(pins=[]), 'NOT_ADMITTED', ['PIN_ONCE'], {}, {}),
    ('PIN_two', dict(pins=['GpuClockPin: mode 1 - a', 'GpuClockPin: mode 1 - b']), 'NOT_ADMITTED', ['PIN_ONCE'],
     {}, {}),
    ('PIN_mode2', dict(pins=['GpuClockPin: mode 2 - control']), 'NOT_ADMITTED', ['PIN_ONCE'], {}, {}),
    ('PIN_mode10', dict(pins=['GpuClockPin: mode 10 - x']), 'NOT_ADMITTED', ['PIN_ONCE'], {}, {}),
    ('PIN_1_and_2', dict(pins=['GpuClockPin: mode 1 - a', 'GpuClockPin: mode 2 - b']), 'NOT_ADMITTED', ['PIN_ONCE'],
     {}, {}),
    ('PIN_garbled', dict(pins=['GpuClockPin: unavailable']), 'NOT_ADMITTED', ['PIN_ONCE'], {}, {}),
    # failure markers, one token each, log and stdout
    ('MARK_hang', dict(marker='GpuHangAbort: role=4 acopy=1/1/1'), 'NOT_ADMITTED', ['NO_MARKER'], {}, {}),
    ('MARK_slow', dict(marker='GpuWaitSlow: 8.0 s'), 'NOT_ADMITTED', ['NO_MARKER'], {}, {}),
    ('MARK_mhung', dict(marker='GpuMarkerHung: cs 0x1'), 'NOT_ADMITTED', ['NO_MARKER'], {}, {}),
    ('MARK_ckpt', dict(marker='GpuCheckpointHang: op=draw'), 'NOT_ADMITTED', ['NO_MARKER'], {}, {}),
    ('MARK_lost', dict(marker='Vulkan: ErrorDeviceLost'), 'NOT_ADMITTED', ['NO_MARKER'], {}, {}),
    ('MARK_term', dict(marker='--- std::terminate ---'), 'NOT_ADMITTED', ['NO_MARKER'], {}, {}),
    ('MARK_abort', dict(marker='--- abort() ---'), 'NOT_ADMITTED', ['NO_MARKER'], {}, {}),
    ('MARK_fatal', dict(marker='--- Fatal Error ---'), 'NOT_ADMITTED', ['NO_MARKER'], {}, {}),
    ('MARK_unhandled', dict(marker='Unhandled exception: 0xC0000005'), 'NOT_ADMITTED', ['NO_MARKER'], {}, {}),
    ('MARK_error', dict(marker='--- Error ---'), 'NOT_ADMITTED', ['NO_MARKER'], {}, {}),
    ('MARK_skipped', dict(marker='AsyncPipelines: skipped draw 5'), 'NOT_ADMITTED', ['NO_MARKER'], {}, {}),
    ('MARK_stdout', dict(stdout_marker='Unhandled exception: 0xC0000005'), 'NOT_ADMITTED', ['NO_MARKER'], {}, {}),
    # rows
    ('ROWS_few', dict(rows=4999), 'NOT_ADMITTED', ['ROWS'], {'rows': 4999, 'rows_all': 5099}, {}),
    ('ROWS_missing', dict(drop={3000: 'cspf_have'}), 'NOT_ADMITTED', ['ROWS'], {'rows_missing': 1}, {}),
    ('ROWS_missing_first', dict(drop={START: 'pl_cont_h1_ns'}), 'NOT_ADMITTED', ['ROWS'], {'rows_missing': 1}, {}),
    ('ROWS_missing_pre', dict(drop={START - 1: 'pl_cont_h1_ns'}), 'BUILD_DASLOT', [], {'rows_missing': 0,
                                                                                    'tag1_us': 151.0}, {}),
    # arming
    ('PLK_dark', dict(base=dict(ZERO_CONT, wq=0, wqn=0), spike=dict(ZERO_CONT_SPIKE, wq=0, wqn=0)), 'NOT_ADMITTED',
     ['PLKSTAT_ARMED'], {'tag1_us': 0.0, 'spin_share': None, 'tag1_share': None, 'wq_call_us': None}, {}),
    ('PLK_wq_only', dict(base=ZERO_CONT, spike=ZERO_CONT_SPIKE), 'LOCK_DONE', [], {'tag1_us': 0.0}, {}),
    ('PLK_cont_only', dict(base=dict(wq=0, wqn=0), spike=dict(wq=0, wqn=0)), 'BUILD_DASLOT', [], {'tag1_us': 151.0},
     {}),
    ('FREE_dark', dict(base=dict(hit=0), spike=dict(hit=0)), 'NOT_ADMITTED', ['CSPFREE_ARMED'], {'cspfree_hit': 0.0},
     {}),
    ('FREE_bad', dict(over={3000: {'bad': 1}}), 'NOT_ADMITTED', ['CSPFREE_BAD'], {'cspfree_bad_all': 1}, {}),
    ('FREE_bad_pre', dict(over={2050: {'bad': 2}}), 'NOT_ADMITTED', ['CSPFREE_BAD'], {'cspfree_bad_all': 2}, {}),
]


def numbers_ok(r, want):
    bad = []
    for k, v in want.items():
        got = None if r is None else r.get(k)
        if got != v:
            bad.append('%s=%r!=%r' % (k, got, v))
    return bad


for name, kw, want, errs, nums, preds in cases:
    try:
        out = run(name, **kw)
    except Exception as exc:        # a scorer that raises fails the fixture (no verdict at all)
        check(name, False, 'raised %s: %s' % (type(exc).__name__, str(exc)[:80]))
        continue
    bad = numbers_ok(out['readouts'], nums)
    for k, hit in preds.items():
        if out['predictions'] is None or out['predictions'][k]['hit'] != hit:
            bad.append('%s hit!=%s' % (k, hit))
    check(name, out['verdict'] == want and out['errors'] == errs and not bad,
          'want %s %s got %s %s %s' % (want, errs, out['verdict'], out['errors'], bad or ''))

# the seal terms (module-level pins)
mod.PRED_SHA, mod.PRED_BYTES = None, None
out = run('DRAFT', prereg={'sha256': None, 'bytes': None})
check('DRAFT', out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['DRAFT', 'PREREG'], out['errors'])
mod.PRED_SHA, mod.PRED_BYTES = SEAL_PINS[1], None
out = run('DRAFT_bytes', prereg={'sha256': SEAL_PINS[1], 'bytes': None})
check('DRAFT_bytes', out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['DRAFT'], out['errors'])
mod.PRED_SHA, mod.PRED_BYTES = SEAL_PINS[1], SEAL_PINS[2] + 1
out = run('SEAL_size', prereg={'sha256': SEAL_PINS[1], 'bytes': SEAL_PINS[2] + 1})
check('SEAL_size', out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['SEAL'], out['errors'])
mod.PRED_SHA, mod.PRED_BYTES = SEAL_PINS[1], SEAL_PINS[2]
mod.PRED = str(BASE / 'no_such_seal.md')
out = run('SEAL_missing')
check('SEAL_missing', out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['SEAL'], out['errors'])
mod.PRED = SEAL_PINS[0]
seal.write_bytes(b'fixture seal 111 obX')           # same size, other bytes
out = run('SEAL_changed')
check('SEAL_changed', out['verdict'] == 'NOT_ADMITTED' and out['errors'] == ['SEAL'], out['errors'])
seal.write_bytes(b'fixture seal 111 obs')
out = run('SEAL_restored')
check('SEAL_restored', out['verdict'] == 'BUILD_DASLOT' and out['errors'] == [], out['errors'])

if '--keep' not in sys.argv:
    shutil.rmtree(BASE)
    try:
        BASE.parent.rmdir()
    except OSError:
        pass
print('cases %d' % (len(cases) + 7))
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
