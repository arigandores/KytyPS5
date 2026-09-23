"""Session 110: fixtures for stl110b.py (from test_stl110.py by make_stl110b.py).  Rule (decision after 107 item 2): every admission term alone and every
verdict branch; each case asserts the verdict AND the exact error set.
    python test_ent109.py <ent109.py>
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_stl110b')
NL = chr(10)
spec = importlib.util.spec_from_file_location('stl110b', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)
seal = BASE / 'seal.md'
seal.write_bytes(b'fixture seal 110 stlb')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
GATES = 'dawalk=1 dabatch=8 fslean=0'


def entry(d, i, arm, s=1, sync_split=True, **bad):
    tag = mod.TAGS[i]
    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_PIPELINE_PRECACHE': 'gfx', 'KYTY_GPU_CLOCK_PIN': '1',
           'KYTY_GPU_MARKERS': '0'}
    env.update(bad.get('env', {}))
    for k in bad.get('env_drop', ()):
        env.pop(k, None)
    att = {'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None, 'hold_s': 150.2}
    att.update(bad.get('att', {}))
    atts = [att] * bad.get('n_att', 1)
    meta = {'binary_sha256': bad.get('binary', mod.BINARY_SHA), 'env': env,
            'gates': bad.get('gates', GATES + ' ' + mod.TOKEN[arm]),
            'prereg': bad.get('prereg', {'sha256': mod.PRED_SHA, 'bytes': mod.PRED_BYTES}),
            'attempts': atts, 'launched': bad.get('launched', '2026-09-24T10:%02d:00' % (10 + 3 * i))}
    (d / (tag + '.json')).write_text(json.dumps(meta), encoding='utf-8')
    lines = ['GpuClockPin: mode 1'] * bad.get('pins', 1)
    lines.append('PipelinePrecache: 641 recipes -> 520 graphics + %d compute pipelines queued, 121 skipped'
                 % bad.get('queued', 0))
    if 'marker' in bad:
        lines.append(bad['marker'])
    # Session 110b: the counted stalls' lines go right after the first FrameTrace-x row; 'startup_stalls' lines
    # precede every row (as the real startup stalls do) and count in D and M only
    stall_block = []
    for k in range(bad.get('stall_lines', s)):
        us = bad.get('stall_first_us', 5000) if k == 0 else 5000
        stall_block.append('CsStall: kind=%s us=%d id=%d hash=0x%016x' % ('new' if k % 2 == 0 else 'wait', us, 100 + k, k))
    for k, us in enumerate(bad.get('startup_stalls', ())):
        lines.append('CsStall: kind=wait us=%d id=%d hash=0x%016x' % (us, 900 + k, k))
    rows = bad.get('rows', 1100)
    first_row = len(lines)
    new_left, wait_left = (s, 0) if sync_split else (0, s)
    for n in range(1, rows + 1):
        sn = 1 if (new_left > 0 and n % 97 == 0) else 0
        sw = 1 if (wait_left > 0 and n % 89 == 0) else 0
        new_left -= sn
        wait_left -= sw
        look = 0 if arm == 'A' else 266
        skip = 0 if arm == 'A' else 250
        if arm == 'A':
            look += bad.get('a_look', 0)
            skip += bad.get('a_skip', 0)
        elif 'b_skip' in bad:
            skip = bad['b_skip']
        fields = ('cs_sync_new=%d cs_sync_wait=%d cspfam_look=0 cspfam_skip=0 cspfam_clr=%d cspf_new=0 '
                  'cspfree_look=%d cspfree_hit=%d cspfree_bad=%d cs_sync_new_us=0 cs_sync_wait_us=0') % (
                      sn, sw, 1 if arm == 'B' else 0, look, skip,
                                                                     bad.get('free_bad', 0) if n == 700 else 0)
        if bad.get('drop_field') and n == 500:
            fields = fields.replace('cspfam_clr=', 'cspfam_clx=')
        lines.append('FrameTrace-x: n=%d rt_att=100 %s' % (n, fields))
    assert new_left <= 0 and wait_left <= 0, 'fixture too short for s'
    lines[first_row + 1:first_row + 1] = stall_block
    if 'stdout_marker' in bad:
        (d / ('stdout_%s.txt' % tag)).write_bytes((bad['stdout_marker'] + NL).encode('utf-8'))
    if 'pin_extra' in bad:
        lines.insert(1, bad['pin_extra'])
    if 'precache_first' in bad:
        lines.insert(1, bad['precache_first'])
    if not bad.get('no_log'):
        (d / ('log_%s.txt' % tag)).write_bytes((NL.join(lines) + NL).encode('utf-8'))


def run(name, sa=(1, 1, 1, 1), sb=(1, 1, 1, 1), per=None, installed=None, **kw):
    """per: {index: bad-dict}; sa/sb: S per A/B entry in order"""
    d = BASE / name
    d.mkdir()
    ia = ib = 0
    for i, arm in enumerate(mod.ORDER):
        if arm == 'A':
            s, ia = sa[ia], ia + 1
        else:
            s, ib = sb[ib], ib + 1
        entry(d, i, arm, s=s, sync_split=(i % 2 == 0), **((per or {}).get(i, {})))
    return mod.evaluate(str(d), installed_sha=installed or mod.BINARY_SHA)


B0 = 1  # index of the first B entry (order A B B A ...)
cases = [
    # verdict branches
    ('PASS', dict(), 'PASS', []),                                               # D_A 20 000, D_B 20 000
    ('PASS_D_edge', dict(sb=(3, 2, 2, 2)), 'PASS', []),                         # D_B 45 000 = 1.25 * 20 000 + 20 000
    ('FAIL_D', dict(sb=(3, 3, 2, 2)), 'FAIL', []),                              # D_B 50 000
    ('FAIL_D_just', dict(sb=(3, 2, 2, 2), per={1: {'stall_first_us': 5001}}), 'FAIL', []),  # D_B 45 001
    ('FAIL_M_first', dict(sb=(2, 1, 1, 1), per={1: {'stall_first_us': 15001}}), 'FAIL', []),  # max is not the last line
    ('PASS_M_edge', dict(per={1: {'stall_first_us': 15000}}), 'PASS', []),      # M_B = M_A + 10 000
    ('FAIL_M', dict(per={1: {'stall_first_us': 15001}}), 'FAIL', []),           # only M exceeds (D_B 30 001)
    ('PASS_more_events', dict(sa=(3, 3, 3, 3), sb=(4, 4, 4, 4)), 'PASS', []),   # 16 vs 12 events, D 80 000 <= 95 000
    ('NO_POWER', dict(sa=(0, 0, 0, 0), sb=(0, 0, 0, 0)), 'NO_POWER', []),
    ('NO_POWER_b', dict(sa=(0, 0, 0, 0), sb=(3, 0, 0, 0)), 'NO_POWER', []),     # B alone cannot give power
    ('SYNC_inflight', dict(per={1: {'stall_lines': 0}}), 'PASS', []),          # one stall in flight at exit is allowed
    ('SYNC_missing', dict(sb=(2, 1, 1, 1), per={1: {'stall_lines': 0}}), 'NOT_ADMITTED', ['stl110b_2:STALL_SYNC']),
    ('SYNC_extra', dict(per={0: {'stall_lines': 2}}), 'NOT_ADMITTED', ['stl110b_1:STALL_SYNC']),
    ('STARTUP_ok', dict(per={0: {'startup_stalls': (12000,)}, 1: {'startup_stalls': (12000,)}}), 'PASS', []),
    ('STARTUP_only', dict(sa=(0, 0, 0, 0), sb=(0, 0, 0, 0), per={0: {'startup_stalls': (3000,)}}), 'PASS', []),
    ('STARTUP_in_M', dict(per={1: {'startup_stalls': (15001,)}}), 'FAIL', []),
    ('STARTUP_in_D', dict(per={1: {'startup_stalls': (5000, 5000, 5000, 5000, 5000, 5001)}}), 'FAIL', []),
    # run-level admission terms, each alone
    ('IDENTITY', dict(installed='0' * 64), 'NOT_ADMITTED', ['IDENTITY']),
    ('ORDER', dict(per={5: {'launched': '2026-09-24T10:00:00'}}), 'NOT_ADMITTED', ['ORDER']),
    ('INPUTS', dict(per={3: {'no_log': True}}), 'NOT_ADMITTED', ['stl110b_4:INPUTS', 'ORDER']),
    # per-entry admission terms, each alone (on one A and one B entry where the term is arm-free)
    ('BINARY', dict(per={0: {'binary': '1' * 64}}), 'NOT_ADMITTED', ['stl110b_1:BINARY']),
    ('PREREG', dict(per={B0: {'prereg': {'sha256': '0' * 64, 'bytes': 1}}}), 'NOT_ADMITTED', ['stl110b_2:PREREG']),
    ('ENV_PRECACHE', dict(per={0: {'env_drop': ['KYTY_PIPELINE_PRECACHE']}}), 'NOT_ADMITTED',
     ['stl110b_1:ENV_PRECACHE']),
    ('ENV_PRECACHE_cs', dict(per={B0: {'env': {'KYTY_PIPELINE_PRECACHE': '1'}}}), 'NOT_ADMITTED',
     ['stl110b_2:ENV_PRECACHE']),
    ('ENV_PIN', dict(per={B0: {'env_drop': ['KYTY_GPU_CLOCK_PIN']}}), 'NOT_ADMITTED', ['stl110b_2:ENV_PIN']),
    ('ENV_SCHED', dict(per={0: {'env': {'KYTY_GATE_SCHEDULE': 'x'}}}), 'NOT_ADMITTED', ['stl110b_1:ENV_FORBIDDEN']),
    ('ENV_CKPT', dict(per={3: {'env': {'KYTY_GPU_CHECKPOINTS': '0'}}}), 'NOT_ADMITTED', ['stl110b_4:ENV_FORBIDDEN']),
    ('ENV_REC', dict(per={B0: {'env': {'KYTY_REC': 'x.mp4'}}}), 'NOT_ADMITTED', ['stl110b_2:ENV_FORBIDDEN']),
    ('GATES_A', dict(per={0: {'gates': GATES + ' cspfree=1'}}), 'NOT_ADMITTED',
     ['stl110b_1:GATES_ARM', 'stl110b_1:ARM_A_DARK'] if False else ['stl110b_1:GATES_ARM']),
    ('GATES_B', dict(per={B0: {'gates': GATES}}), 'NOT_ADMITTED', ['stl110b_2:GATES_ARM']),
    ('GATES_both', dict(per={B0: {'gates': GATES + ' cspfree=0 cspfree=1'}}), 'NOT_ADMITTED', ['stl110b_2:GATES_ARM']),
    ('ATT_outcome', dict(per={0: {'att': {'outcome': 'hang'}}}), 'NOT_ADMITTED', ['stl110b_1:ATTEMPT']),
    ('ATT_exit', dict(per={B0: {'att': {'hold_exit': 3}}}), 'NOT_ADMITTED', ['stl110b_2:ATTEMPT']),
    ('ATT_hold', dict(per={3: {'att': {'hold_s': 100.0}}}), 'NOT_ADMITTED', ['stl110b_4:ATTEMPT']),
    ('ATT_two', dict(per={B0: {'n_att': 2}}), 'NOT_ADMITTED', ['stl110b_2:ATTEMPT']),
    ('PIN_none', dict(per={0: {'pins': 0}}), 'NOT_ADMITTED', ['stl110b_1:PIN_ONCE']),
    ('PIN_two', dict(per={B0: {'pins': 2}}), 'NOT_ADMITTED', ['stl110b_2:PIN_ONCE']),
    ('PRECACHE_on', dict(per={0: {'queued': 121}}), 'NOT_ADMITTED', ['stl110b_1:PRECACHE_OFF']),
    ('MARK_hang', dict(per={B0: {'marker': 'GpuHangAbort: role=4'}}), 'NOT_ADMITTED', ['stl110b_2:NO_MARKER']),
    ('MARK_error', dict(per={0: {'marker': '--- Error ---'}}), 'NOT_ADMITTED', ['stl110b_1:NO_MARKER']),
    ('MARK_skipped', dict(per={B0: {'marker': 'AsyncPipelines: skipped draw 5'}}), 'NOT_ADMITTED',
     ['stl110b_2:NO_MARKER']),
    ('MARK_slow', dict(per={3: {'marker': 'GpuWaitSlow: 8 s'}}), 'NOT_ADMITTED', ['stl110b_4:NO_MARKER']),
    ('ROWS_few', dict(per={0: {'rows': 900}}), 'NOT_ADMITTED', ['stl110b_1:ROWS']),
    ('ROWS_field', dict(per={B0: {'drop_field': True}}), 'NOT_ADMITTED', ['stl110b_2:ROWS']),
    ('ARM_A_skip', dict(per={0: {'a_skip': 1}}), 'NOT_ADMITTED', ['stl110b_1:ARM_A_DARK']),
    ('ARM_A_look', dict(per={3: {'a_look': 1}}), 'NOT_ADMITTED', ['stl110b_4:ARM_A_DARK']),
    ('ARM_B_dark', dict(per={B0: {'b_skip': 0}}), 'NOT_ADMITTED', ['stl110b_2:ARM_B_ARMED']),
    ('ARM_B_bad', dict(per={B0: {'free_bad': 1}}), 'NOT_ADMITTED', ['stl110b_2:ARM_B_ARMED']),
    ('PIN_mode2', dict(per={0: {'pin_extra': 'GpuClockPin: mode 2'}}), 'NOT_ADMITTED', ['stl110b_1:PIN_ONCE']),
    ('MARK_fatal', dict(per={B0: {'marker': '--- Fatal Error ---'}}), 'NOT_ADMITTED', ['stl110b_2:NO_MARKER']),
    ('MARK_stdout', dict(per={3: {'stdout_marker': 'Unhandled exception: 0xC0000005'}}), 'NOT_ADMITTED',
     ['stl110b_4:NO_MARKER']),
    ('GATES_notail', dict(per={B0: {'gates': 'cspfree=1 ' + GATES}}), 'NOT_ADMITTED', ['stl110b_2:GATES_ARM']),
    ('ATT_hold_edge', dict(per={0: {'att': {'hold_s': 140.0}}}), 'NOT_ADMITTED', ['stl110b_1:ATTEMPT']),
    ('ORDER_dupe', dict(per={1: {'launched': '2026-09-24T10:10:00'}}), 'NOT_ADMITTED', ['ORDER']),
    ('PRECACHE_first', dict(per={0: {'precache_first': 'PipelinePrecache: 641 recipes -> 520 graphics + 121 compute '
                                                       'pipelines queued, 0 skipped'}}), 'NOT_ADMITTED',
     ['stl110b_1:PRECACHE_OFF']),
]
ok = True
for name, kw, want, errs in cases:
    out = run(name, **kw)
    got = out['verdict']
    passed = got == want and out['errors'] == errs
    ok &= passed
    print('%-16s want %-12s got %-12s S_A %2d S_B %2d errors %s %s' % (name, want, got, out['S_A'], out['S_B'],
                                                                     out['errors'], 'OK' if passed else 'FAIL'))
# the DRAFT and SEAL terms (module-level seal pins)
saved = (mod.PRED_SHA, mod.PRED_BYTES)
mod.PRED_SHA = None
out = run('DRAFT')
passed = out['verdict'] == 'NOT_ADMITTED' and out['errors'][0] == 'DRAFT'
print('%-16s errors %s %s' % ('DRAFT', out['errors'][:2], 'OK' if passed else 'FAIL'))
ok &= passed
mod.PRED_SHA, mod.PRED_BYTES = saved
mod.PRED_BYTES = saved[1] + 1
out = run('SEAL')
passed = out['verdict'] == 'NOT_ADMITTED' and out['errors'][0] == 'SEAL'
print('%-16s errors %s %s' % ('SEAL', out['errors'][:2], 'OK' if passed else 'FAIL'))
ok &= passed
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
