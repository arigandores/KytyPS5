"""Fixtures of fs11c_read.py (Track F link FS11c, HPP-716): a clean synthetic tag of each form (fs11_v, fs11_w, fs11_z) reads ADMITTED /
ALL YES; every admission member (env: KYTY_FIX_B12 absent at fs11_v / fs11_w, '0' at fs11_z) and every member of the three forms, and each
edge (1 000 000 / 999 999, hold 300 s, hold 120 s at fs11_z, video 2 999 / 3 000, draws 99 / 100, hold_s 309.9 / 310.0, FixB12 mode=0 /
absent / after GuestOut / second line / unparsable, FixB12Stat present at fs11_v, 0 lines at fs11_z, the last line a report row),
flips the reading; strict cp1250 output without PYTHONIOENCODING; the last line is ALL OK.  Port of C:/kyty/f287/f29e/test_f29e_read.py
(F29e).  Early-exit form of mutlib (ok = True, ok &= ..., sys.exit(0 if ok else 1)).  ASCII only.
The reader is loaded in-process from argv[1] (default: fs11c_read.py beside this file); the fixture directories live under BASE.
usage: python test_fs11c_read.py [<fs11c_read.py under test>]"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fs11c_read.py')
BASE = Path(os.path.join(HERE, 'fx_fs11c'))   # mutlib gives every job its own copy of this directory
_spec = importlib.util.spec_from_file_location('fs11c_read_under_test', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_fs11c_read.py sha256 %s target fs11c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0, 0]
SEAL = b'seal fixture\n'
TB = 'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce'   # literals, not the reader's constants (mutants)
FS10 = 'abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1910-gee9632be'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
ok = True


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
        print('FAIL %s' % name)
    return bool(cond)


def env_of(base):
    e = dict(KYTY_GUEST_ARGS='-lvl ' + SKY, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE='C:/x/g', KYTY_SAMPLE_GATE='C:/x/s', KYTY_QUEUE_TRACE='1',
             KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8')
    if base == 'fs11_w':
        e.update(VK_LAYER_PATH='C:/VulkanSDK/1.4.357.0/Bin', VK_LAYER_DUPLICATE_MESSAGE_LIMIT='100000000')
    else:
        e['KYTY_REC'] = 'C:/x/rec.mp4'
    if base == 'fs11_z':
        e['KYTY_FIX_B12'] = '0'
    return e


STAT = 'FixB12Stat: passes=%d rewalk=%d rwd=%d lskip=%d'


def spec(base):
    """The clean tag of the form: a list of log lines and the side files."""
    kind = R.kind_of(base)
    L = ['LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100', 'Fork build arigandores/KytyPS5 ee9632b',
         'ShaderSeed: compatibility=x:KytySC3:%s:y' % SIG, 'Shader translation cache: C:/e/_ShaderCache/PPSA21564/%s' % VARIANT_DIR]
    if kind == 'w':
        L.append('DualSrcBlend: supported=1 enabled=1')
    L += ['FixB12: mode=%d' % (0 if kind == 'z' else 1), 'FixB13: mode=1', 'GuestOut: Level has started: ',
          'GuestOut: Level has started: %s' % SKY,
          'FrameTrace: n=10 dt_us=500000 draws=20', 'FrameTrace: n=11 dt_us=16000 draws=300']    # n=11 - the first scene frame
    nfr = {'v': 20000, 'w': 2500, 'z': 9000}[kind]
    dt = {'v': 16700, 'w': 130000, 'z': 16700}[kind]
    for i in range(nfr):
        L.append('FrameTrace: n=%d dt_us=%d draws=300' % (12 + i, dt))
        if i in (100, 900) and kind != 'z':
            L.append(STAT % (i, i // 2, 0, 1))
    if kind != 'z':
        L.append(STAT % (5000, 3000, 7, 2))
    L.append('LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0')
    if kind == 'w':
        L += ['[Vulkan][W] something'] * 5
    hold = {'v': 330, 'w': 310, 'z': 150}[kind]
    cmd = ['emu', '--vulkan-validation', 'true' if kind == 'w' else 'false', '--shader-validation', 'false']
    att = dict(outcome='ok', hold_exit=None, hold_s=float(hold), stable_s=12.0)
    run = dict(binary_sha256=TB, env=env_of(base), cmdline=cmd, attempts=[att], guest_args='-lvl ' + SKY, hold_s=hold,
               prereg=dict(sha256=hashlib.sha256(SEAL).hexdigest()))
    side = dict(installed_before=FS10, installed_after=FS10, installed_sha=TB, level=SKY,
                manifest_cmp='manifest cmp EQUAL files 5 listsha x')
    if kind != 'w':
        side.update(glitch='one-frame glitches: 0', sheet='sheet ok')
    return dict(lines=L, run=run, side=side, idx=(0 if kind == 'w' else 3200), stdout='')


def write(d, s):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'log.txt'), 'wb') as f:
        f.write(('\n'.join(s['lines']) + '\n').encode('ascii'))
    with open(os.path.join(d, 'es.json'), 'w') as f:
        json.dump(s['run'], f)
    for k, v in s['side'].items():
        with open(os.path.join(d, k + '.txt'), 'w') as f:
            f.write(v + '\n')
    with open(os.path.join(d, 'seal.md'), 'wb') as f:
        f.write(SEAL)
    with open(os.path.join(d, 'stdout.txt'), 'w') as f:
        f.write(s['stdout'])
    if s['idx']:
        with open(os.path.join(d, 'rec.idx'), 'w') as f:
            f.write('r\n' * s['idx'])
    with open(os.path.join(d, 'bin.exe'), 'wb') as f:
        f.write(b'xx' + VERSION + b'yy')


shutil.rmtree(str(BASE), ignore_errors=True)
os.makedirs(str(BASE), exist_ok=True)
TMP = str(BASE)
CNT = [0]


def read(base, s):
    CNT[0] += 1
    d = os.path.join(TMP, 'c%d' % CNT[0])
    write(d, s)
    r = R.read_tag(base, R.paths(base, d))
    shutil.rmtree(d, ignore_errors=True)
    return r


def mem(r, start):
    for a, b in (r['members'] or []):
        if a.startswith(start):
            return b
    return None


def repl(s, old, new, all_=False):
    s = copy.deepcopy(s)
    out = []
    done = False
    for l in s['lines']:
        if l.startswith(old) and (all_ or not done):
            done = True
            if new is not None:
                out.append(new if not callable(new) else new(l))
        else:
            out.append(l)
    s['lines'] = out
    return s


BASES = ('fs11_v', 'fs11_w')
ALLB = ('fs11_v', 'fs11_w', 'fs11_z')
for b in ALLB:
    r = read(b, spec(b))
    ok &= check('%s clean ADMITTED %s' % (b, [a for a, x in r['admission'] if not x]), r['status'] == 'ADMITTED')
    ok &= check('%s clean ALL YES %s' % (b, [a for a, x in (r['members'] or []) if not x]), r['ok'] is True)
    ok &= check('%s members count %d' % (b, len(r['members'] or [])), len(r['members'] or []) == {'fs11_v': 13, 'fs11_w': 10, 'fs11_z': 5}[b])
    for tg in (b + '_r1', b + '_r3'):
        ok &= check('%s tag form %s' % (b, tg), R.base_of(tg) == b)
    if b == 'fs11_z':
        ok &= check('%s FixB12Stat row empty' % b, r['fixb12stat']['lines'] == 0 and r['fixb12stat']['last'] is None)
    else:
        ok &= check('%s FixB12Stat last row' % b, r['fixb12stat']['lines'] == 3 and r['fixb12stat']['bad'] == 0
                    and r['fixb12stat']['last'] == dict(passes=5000, rewalk=3000, rwd=7, lskip=2))

# --- admission members (each flips to INTERFERENCE) ---
for b in ALLB:
    s = spec(b)
    for key, val in (('installed_before', TB), ('installed_after', 'x'), ('installed_sha', FS10), ('level', 'pot'),
                     ('manifest_cmp', 'manifest cmp DIFFER only-before 1')):
        t = copy.deepcopy(s)
        t['side'][key] = val
        ok &= check('%s admission %s' % (b, key), read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    del t['side']['manifest_cmp']
    ok &= check('%s admission no manifest_cmp file' % b, read(b, t)['status'] == 'INTERFERENCE')
    for key, val in (('binary_sha256', FS10), ('guest_args', '-lvl pot'), ('hold_s', 100)):
        t = copy.deepcopy(s)
        t['run'][key] = val
        ok &= check('%s admission run %s' % (b, key), read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['prereg']['sha256'] = 'x'
    ok &= check('%s admission prereg' % b, read(b, t)['status'] == 'INTERFERENCE')
    kv = [('KYTY_FIX_B12', '1')] + ([] if b == 'fs11_z' else [('KYTY_FIX_B12', '0')])
    for k, v in kv + [('KYTY_FIX_B36', '1'), ('KYTY_FIX_B13', '1'), ('KYTY_DIAG_B32', '1'), ('KYTY_GAME_PATCH', 'p'),
                      ('KYTY_GPU_CHECKPOINTS', '1'), ('KYTY_S_REPLAY', '3'), ('VK_LAYER_MESSAGE_ID_FILTER', 'x')]:
        t = copy.deepcopy(s)
        t['run']['env'][k] = v
        ok &= check('%s admission env %s=%s' % (b, k, v), read(b, t)['status'] == 'INTERFERENCE')
    for k0 in {'fs11_v': ('KYTY_REC', 'KYTY_GPU_CLOCK_PIN'), 'fs11_w': ('VK_LAYER_PATH', 'KYTY_GPU_CLOCK_PIN'),
               'fs11_z': ('KYTY_FIX_B12', 'KYTY_REC', 'KYTY_GPU_CLOCK_PIN')}[b]:
        t = copy.deepcopy(s)
        del t['run']['env'][k0]
        ok &= check('%s admission env missing %s' % (b, k0), read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['cmdline'] = t['run']['cmdline'] + ['--vulkan-validation', 'false' if b == 'fs11_w' else 'true']
    ok &= check('%s admission last vulkan-validation' % b, read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['cmdline'] = t['run']['cmdline'] + ['--shader-validation', 'true']
    ok &= check('%s admission shader-validation' % b, read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['cmdline'] = t['run']['cmdline'] + ['--rd']
    ok &= check('%s admission --rd' % b, read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['attempts'][0]['outcome'] = 'not_entered'
    ok &= check('%s admission outcome' % b, read(b, t)['status'] == 'INTERFERENCE')
    for extra in ('Window 1 minimized', 'Recovering Vulkan swapchain', 'GamePatch: loaded', 'DiagB32: mode=1',
                  'TestLogStall: config at_ms=1 sleep_ms=3000 k=3 gap_ms=5000 on=writer'):
        t = copy.deepcopy(s)
        t['lines'].insert(4, extra)
        ok &= check('%s admission line %s' % (b, extra), read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['lines'].insert(4, 'Window 1 restored')
    ok &= check('%s restored is not interference' % b, read(b, t)['status'] == 'ADMITTED')
    ok &= check('%s admission signature' % b, read(b, repl(s, 'ShaderSeed:', 'ShaderSeed: compatibility=x:KytySC3:%s:y' % ('0' * 40)))['status'] == 'INTERFERENCE')
    ok &= check('%s admission catalog' % b, read(b, repl(s, 'Shader translation cache:', 'Shader translation cache: C:/e/variant_fixb26'))['status'] == 'INTERFERENCE')
    ok &= check('%s admission entry line' % b, read(b, repl(s, 'GuestOut: Level has started: %s' % SKY, None))['status'] == 'INTERFERENCE')
    r = read(b, repl(s, 'LogAsync: full_waits=', None))
    ok &= check('%s no summary -> INTERFERENCE run' % b, r['status'] == 'INTERFERENCE' and r['interference'].startswith('run'))
    r = read(b, repl(s, 'LogAsync: full_waits=', 'LogAsync: full_waits=0 full_wait_us=0'))
    ok &= check('%s summary missing fields -> INTERFERENCE' % b, r['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['lines'].append(t['lines'][[i for i, l in enumerate(t['lines']) if l.startswith('LogAsync: full_waits=')][0]])
    ok &= check('%s two summary lines -> INTERFERENCE' % b, read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    os.makedirs(os.path.join(TMP, 'nolog'), exist_ok=True)
    d = os.path.join(TMP, 'nolog%s' % b)
    write(d, t)
    os.remove(os.path.join(d, 'log.txt'))
    r = R.read_tag(b, R.paths(b, d))
    ok &= check('%s no log -> INTERFERENCE, no members' % b, r['status'] == 'INTERFERENCE' and r['members'] is None)
    os.remove(os.path.join(d, 'es.json'))
    r = R.read_tag(b, R.paths(b, d))
    ok &= check('%s no json -> INTERFERENCE' % b, r['status'] == 'INTERFERENCE')

# --- FixB12 member (both tags) and the FixB12Stat row ---
for b in BASES:
    s = spec(b)
    ok &= check('%s FixB12 mode=0 -> NO' % b, mem(read(b, repl(s, 'FixB12: mode=1', 'FixB12: mode=0')), 'FixB12: mode=1') is False)
    ok &= check('%s FixB12 absent -> NO' % b, mem(read(b, repl(s, 'FixB12: mode=1', None)), 'FixB12: mode=1') is False)
    ok &= check('%s FixB12 mode=10 -> NO' % b, mem(read(b, repl(s, 'FixB12: mode=1', 'FixB12: mode=10')), 'FixB12: mode=1') is False)
    ok &= check('%s FixB12 unparsable -> NO' % b, mem(read(b, repl(s, 'FixB12: mode=1', 'FixB12: mode=1 x')), 'FixB12: mode=1') is False)
    t = copy.deepcopy(s)
    fl = [l for l in t['lines'] if l.startswith('FixB12: mode=1')][0]
    t['lines'].remove(fl)
    t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, fl)
    ok &= check('%s FixB12 after the first GuestOut -> NO' % b, mem(read(b, t), 'FixB12: mode=1') is False)
    t = copy.deepcopy(s)
    t['lines'].insert(t['lines'].index('FixB12: mode=1') + 1, 'FixB12: mode=0')
    ok &= check('%s FixB12 second line mode=0 -> NO' % b, mem(read(b, t), 'FixB12: mode=1') is False)
    t = copy.deepcopy(s)
    t['lines'].insert(t['lines'].index('FixB12: mode=1') + 1, 'FixB12: mode=1 garbage')
    ok &= check('%s FixB12 good line and an unparsable line -> NO' % b, mem(read(b, t), 'FixB12: mode=1') is False)
    t = copy.deepcopy(s)
    t['lines'].insert(t['lines'].index('FixB12: mode=1') + 1, 'FixB12: mode=1')
    ok &= check('%s FixB12 two lines mode=1 -> YES' % b, mem(read(b, t), 'FixB12: mode=1') is True)
    r = read(b, repl(s, 'FixB12Stat:', None, True))
    if b == 'fs11_v':
        ok &= check('%s no FixB12Stat -> the member FixB12Stat present NO, row empty' % b,
                    mem(r, 'FixB12Stat: line present') is False and r['fixb12stat']['lines'] == 0 and r['fixb12stat']['last'] is None)
        r1 = read(b, repl(repl(s, 'FixB12Stat:', None, True), 'LogAsync: full_waits=', lambda l: STAT % (1, 0, 0, 0) + chr(10) + l))
        ok &= check('%s one FixB12Stat line -> present YES' % b, mem(r1, 'FixB12Stat: line present') is True)
        r2 = read(b, repl(repl(s, 'FixB12Stat:', None, True), 'LogAsync: full_waits=', lambda l: 'FixB12Stat: passes=1 rewalk=x' + chr(10) + l))
        ok &= check('%s only an unparsable FixB12Stat line -> present NO' % b, mem(r2, 'FixB12Stat: line present') is False)
    else:
        ok &= check('%s no FixB12Stat -> still ALL YES (report row)' % b, r['ok'] is True and r['fixb12stat']['lines'] == 0
                    and r['fixb12stat']['last'] is None)
    t = copy.deepcopy(s)
    t['lines'].insert(-2, 'FixB12Stat: passes=1 rewalk=x')
    r = read(b, t)
    ok &= check('%s unparsable FixB12Stat -> counted, not a member' % b, r['ok'] is True and r['fixb12stat']['bad'] == 1
                and r['fixb12stat']['last']['passes'] == 5000)
    t = copy.deepcopy(s)
    t['lines'].append(STAT % (9, 8, 6, 5))
    r = read(b, t)
    ok &= check('%s FixB12Stat last line wins' % b, r['fixb12stat']['last'] == dict(passes=9, rewalk=8, rwd=6, lskip=5))
    t = copy.deepcopy(s)
    t['lines'].append('[3][01:02:03.004] FixB12Stat: passes=11 rewalk=12 rwd=13 lskip=14')
    r = read(b, t)
    ok &= check('%s FixB12Stat with a prefix parsed' % b, r['fixb12stat']['last'] == dict(passes=11, rewalk=12, rwd=13, lskip=14))
    r = read(b, repl(s, 'FixB12: mode=1', 'FixB12: mode=0'))
    rows = '\n'.join(R.rows_out(r))
    ok &= check('%s rows carry the FixB12Stat row' % b, 'ROW FixB12Stat (last line - report row, not a gate' in rows and 'rwd=7' in rows)
    ok &= check('%s FixB13 mode=0 -> NO' % b, mem(read(b, repl(s, 'FixB13: mode=1', 'FixB13: mode=0')), 'FixB13') is False)
    ok &= check('%s FixB13 absent -> NO' % b, mem(read(b, repl(s, 'FixB13: mode=1', None)), 'FixB13') is False)
    ok &= check('%s mode=0 requested=1 reason=direction -> NO' % b,
                mem(read(b, repl(s, 'LogAsync: mode=1', 'LogAsync: mode=0 requested=1 reason=direction')), 'LogAsync: mode=1') is False)
    t = copy.deepcopy(s)
    t['lines'].insert(3, 'LogAsync: mode=1 limit_bytes=1 drain_ms=1 stall_ms=1 flush_ms=1')
    ok &= check('%s two mode lines -> NO' % b, mem(read(b, t), 'LogAsync: mode=1') is False)
    t = copy.deepcopy(s)
    ml = [l for l in t['lines'] if l.startswith('LogAsync: mode=1')][0]
    t['lines'].remove(ml)
    t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, ml)
    ok &= check('%s mode line after the first GuestOut -> NO' % b, mem(read(b, t), 'LogAsync: mode=1') is False)
    t = copy.deepcopy(s)
    t['stdout'] = 'GpuHangAbort: x'
    ok &= check('%s death stdout -> NO' % b, mem(read(b, t), '0 death') is False)
    for dm in ('Unhandled exception: x', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort: x', 'ErrorDeviceLost'):
        t = copy.deepcopy(s)
        t['lines'].insert(-2, dm)
        ok &= check('%s death in log %s -> NO' % (b, dm), mem(read(b, t), '0 death') is False)

# --- v ---
s = spec('fs11_v')
fw = 'LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0'
t = copy.deepcopy(s)
t['lines'].insert(-2, 'FrameTrace: n=99999 dt_us=1000000 draws=300')
ok &= check('v frame 1 000 000 -> NO', mem(read('fs11_v', t), '0 frames >= 1 s') is False)
t = copy.deepcopy(s)
t['lines'].insert(-2, 'FrameTrace: n=99999 dt_us=999999 draws=300')
ok &= check('v frame 999 999 -> YES', mem(read('fs11_v', t), '0 frames >= 1 s') is True)
r = read('fs11_v', repl(s, 'FrameTrace: n=11 ', 'FrameTrace: n=11 dt_us=5000000 draws=300'))
ok &= check('v the first scene frame itself >= 1 s -> YES by the letter, printed with it 1', mem(r, '0 frames >= 1 s') is True
            and r['info']['frames_ge1s_with_first'] == 1)
r = read('fs11_v', repl(s, 'FrameTrace: n=10 ', 'FrameTrace: n=10 dt_us=5000000 draws=20'))
ok &= check('v frame >= 1 s before the first scene frame (draws < 100) -> YES', mem(r, '0 frames >= 1 s') is True)
t = copy.deepcopy(s)
t['lines'] = [l.replace('draws=300', 'draws=99') for l in t['lines']]
r = read('fs11_v', t)
ok &= check('v no first scene frame (draws 99) -> NO', mem(r, '0 frames >= 1 s') is False and mem(r, 'hold >= 300') is False)
t = copy.deepcopy(s)
t['lines'] = [l for l in t['lines'] if not (l.startswith('FrameTrace: n=') and int(l.split('=')[1].split()[0]) >= 17976)]
r = read('fs11_v', t)   # 17964 frames after n=11 x 16 700 = 299 998 800 us
ok &= check('v hold 299.9988 s -> NO (%s)' % r['info']['hold_s'], mem(r, 'hold >= 300') is False)
t = copy.deepcopy(s)
t['lines'] = [l for l in t['lines'] if not (l.startswith('FrameTrace: n=') and int(l.split('=')[1].split()[0]) >= 17976)]
t['lines'].insert(-3, 'FrameTrace: n=17976 dt_us=1200 draws=300')
r = read('fs11_v', t)   # + 1 200 us = 300 000 000 us
ok &= check('v hold exactly 300 s -> YES (%s)' % r['info']['hold_s'], mem(r, 'hold >= 300') is True)
t = copy.deepcopy(s)
t['idx'] = 2999
ok &= check('v video 2999 -> NO', mem(read('fs11_v', t), 'video index') is False)
t = copy.deepcopy(s)
t['idx'] = 3000
ok &= check('v video 3000 edge -> YES', mem(read('fs11_v', t), 'video index') is True)
t = copy.deepcopy(s)
t['idx'] = 0
ok &= check('v no video index -> NO', mem(read('fs11_v', t), 'video index') is False)
t = copy.deepcopy(s)
t['side']['glitch'] = 'one-frame glitches: 1'
ok &= check('v glitch 1 -> NO', mem(read('fs11_v', t), '0 one-frame') is False)
t = copy.deepcopy(s)
del t['side']['glitch']
ok &= check('v no glitch file -> NO', mem(read('fs11_v', t), '0 one-frame') is False)
t = copy.deepcopy(s)
t['side']['glitch'] = 'no line here'
ok &= check('v no glitch line -> NO', mem(read('fs11_v', t), '0 one-frame') is False)
t = copy.deepcopy(s)
del t['side']['sheet']
ok &= check('v no sheet -> NO', mem(read('fs11_v', t), 'sheet') is False)
t = copy.deepcopy(s)
t['run']['attempts'][0]['hold_exit'] = 'died'
ok &= check('v hold_exit -> NO', mem(read('fs11_v', t), 'the process lived') is False)
r = read('fs11_v', repl(s, 'LogAsync: full_waits=', fw.replace('drain_timeouts=0', 'drain_timeouts=3')))
ok &= check('v drain_timeouts 3 -> NO', mem(r, 'drain_timeouts 0') is False)
t = copy.deepcopy(s)
t['lines'].insert(-2, '[Vulkan][E] VUID-x')
r = read('fs11_v', t)
ok &= check('v [Vulkan][E] is a reference only', r['ok'] is True and r['ref']['vke'] == 1)
t = copy.deepcopy(s)
t['lines'].insert(4, 'AsyncPipelines: skipped draw x')
ok &= check('v skipped draw is not a member', read('fs11_v', t)['ok'] is True)

# --- w ---
s = spec('fs11_w')
t = copy.deepcopy(s)
t['lines'].insert(-2, '[Vulkan][E] VUID-x')
ok &= check('w [Vulkan][E] -> NO', mem(read('fs11_w', t), '0 [Vulkan][E]') is False)
t = copy.deepcopy(s)
t['lines'].insert(-2, 'x this will be the last time reporting it')
ok &= check('w limit line -> NO', mem(read('fs11_w', t), '0 limit') is False)
ok &= check('w no [Vulkan][W] -> NO', mem(read('fs11_w', repl(s, '[Vulkan][W]', None, True)), 'positive control') is False)
ok &= check('w DualSrcBlend enabled=0 -> NO', mem(read('fs11_w', repl(s, 'DualSrcBlend', 'DualSrcBlend: supported=1 enabled=0')), 'DualSrcBlend') is False)
ok &= check('w DualSrcBlend absent -> NO', mem(read('fs11_w', repl(s, 'DualSrcBlend', None)), 'DualSrcBlend') is False)
t = copy.deepcopy(s)
dl = [l for l in t['lines'] if l.startswith('DualSrcBlend')][0]
t['lines'].remove(dl)
t['lines'].append(dl)
ok &= check('w DualSrcBlend after GuestOut -> NO', mem(read('fs11_w', t), 'DualSrcBlend') is False)
t = copy.deepcopy(s)
t['run']['attempts'][0]['hold_s'] = 309.9
ok &= check('w hold 309.9 -> NO', mem(read('fs11_w', t), 'lived to the end') is False)
t = copy.deepcopy(s)
t['run']['attempts'][0]['hold_s'] = 310.0
ok &= check('w hold 310.0 -> YES', mem(read('fs11_w', t), 'lived to the end') is True)
t = copy.deepcopy(s)
t['run']['attempts'][0]['hold_exit'] = 'died'
ok &= check('w hold_exit -> NO', mem(read('fs11_w', t), 'lived to the end') is False)
t = copy.deepcopy(s)
t['run']['attempts'][0]['hold_s'] = 309.9
t['lines'].insert(-2, '[Vulkan][E] VUID-x')
ok &= check('w VALIDATION_STOP -> NO', mem(read('fs11_w', t), 'no VALIDATION_STOP') is False)
t = copy.deepcopy(s)
t['run']['attempts'][0]['hold_s'] = 309.9
ok &= check('w early end without [Vulkan][E] -> VALIDATION_STOP member YES, lived NO', mem(read('fs11_w', t), 'no VALIDATION_STOP') is True)
t = copy.deepcopy(s)
t['lines'].insert(-2, 'FrameTrace: n=99999 dt_us=2000000 draws=300')
r = read('fs11_w', t)
ok &= check('w frame >= 1 s under the layer is a reference only', r['ok'] is True and r['info']['frames_ge1s_report'] == 1)

# --- z (the rollback control KYTY_FIX_B12=0) ---
s = spec('fs11_z')
Z = 'fs11_z'
ok &= check('z FixB12 mode=1 -> NO', mem(read(Z, repl(s, 'FixB12: mode=0', 'FixB12: mode=1')), 'FixB12: mode=0') is False)
ok &= check('z FixB12 absent -> NO', mem(read(Z, repl(s, 'FixB12: mode=0', None)), 'FixB12: mode=0') is False)
ok &= check('z FixB12 mode=01 -> NO', mem(read(Z, repl(s, 'FixB12: mode=0', 'FixB12: mode=01')), 'FixB12: mode=0') is False)
ok &= check('z FixB12 unparsable -> NO', mem(read(Z, repl(s, 'FixB12: mode=0', 'FixB12: mode=0 x')), 'FixB12: mode=0') is False)
t = copy.deepcopy(s)
fl = [l for l in t['lines'] if l.startswith('FixB12: mode=0')][0]
t['lines'].remove(fl)
t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, fl)
ok &= check('z FixB12 after the first GuestOut -> NO', mem(read(Z, t), 'FixB12: mode=0') is False)
t = copy.deepcopy(s)
t['lines'].insert(t['lines'].index('FixB12: mode=0') + 1, 'FixB12: mode=1')
ok &= check('z FixB12 second line mode=1 -> NO', mem(read(Z, t), 'FixB12: mode=0') is False)
t = copy.deepcopy(s)
t['lines'].insert(-2, STAT % (1, 0, 0, 0))
r = read(Z, t)
ok &= check('z one FixB12Stat line -> NO', mem(r, 'FixB12Stat: lines 0') is False and r['fixb12stat']['lines'] == 1)
t = copy.deepcopy(s)
t['lines'].insert(-2, 'FixB12Stat: passes=1 rewalk=x')
ok &= check('z an unparsable FixB12Stat line -> NO', mem(read(Z, t), 'FixB12Stat: lines 0') is False)
t = copy.deepcopy(s)
t['lines'].insert(-2, '[3][01:02:03.004] FixB12Stat: passes=11 rewalk=12 rwd=13 lskip=14')
ok &= check('z a FixB12Stat line with a prefix -> NO', mem(read(Z, t), 'FixB12Stat: lines 0') is False)
t = copy.deepcopy(s)
t['lines'] = [l for l in t['lines'] if not (l.startswith('FrameTrace: n=') and int(l.split('=')[1].split()[0]) >= 12 + 7185)]
r = read(Z, t)   # 7185 frames after n=11 x 16 700 = 119 989 500 us
ok &= check('z hold 119.9895 s -> NO (%s)' % r['info']['hold_s'], mem(r, 'hold >= 120') is False)
t['lines'].insert(-2, 'FrameTrace: n=%d dt_us=10500 draws=300' % (12 + 7185))
r = read(Z, t)   # + 10 500 us = 120 000 000 us
ok &= check('z hold exactly 120 s -> YES (%s)' % r['info']['hold_s'], mem(r, 'hold >= 120') is True)
t = copy.deepcopy(s)
t['lines'] = [l.replace('draws=300', 'draws=99') for l in t['lines']]
ok &= check('z no first scene frame -> hold NO', mem(read(Z, t), 'hold >= 120') is False)
t = copy.deepcopy(s)
t['run']['attempts'][0]['hold_exit'] = 'died'
ok &= check('z hold_exit -> lived NO', mem(read(Z, t), 'the process lived') is False)
t = copy.deepcopy(s)
t['run']['attempts'][0]['outcome'] = 'stalled'
ok &= check('z outcome not ok -> INTERFERENCE', read(Z, t)['status'] == 'INTERFERENCE')
t = copy.deepcopy(s)
t['stdout'] = 'Unhandled exception: x'
ok &= check('z death stdout -> NO', mem(read(Z, t), '0 death') is False)
for dm in ('Unhandled exception: x', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort: x', 'ErrorDeviceLost'):
    t = copy.deepcopy(s)
    t['lines'].insert(-2, dm)
    ok &= check('z death in log %s -> NO' % dm, mem(read(Z, t), '0 death') is False)
t = copy.deepcopy(s)
t['lines'].insert(-2, 'FrameTrace: n=99999 dt_us=2000000 draws=300')
t['side']['glitch'] = 'one-frame glitches: 3'
t['idx'] = 10
t['lines'].insert(-2, '[Vulkan][E] VUID-x')
r = read(Z, t)
ok &= check('z frame >= 1 s, glitches, short video, [Vulkan][E] are reference rows only', r['ok'] is True
            and r['info']['frames_ge1s_report'] == 1 and r['info']['glitches'] == 3 and r['info']['video_index'] == 10)
r = read(Z, repl(s, 'LogAsync: mode=1', 'LogAsync: mode=0 requested=1 reason=direction'))
ok &= check('z LogAsync mode=0 is a reference row only', r['ok'] is True)
r = read(Z, repl(s, 'FixB13: mode=1', None))
ok &= check('z FixB13 absent is a reference row only', r['ok'] is True)
rows = '\n'.join(R.rows_out(read(Z, s)))
ok &= check('z rows: FixB12Stat row <absent>', 'ROW FixB12Stat' in rows and '<absent>' in rows)

# --- reference rows ---
r = read('fs11_v', spec('fs11_v'))
ok &= check('bin version string row', r['ref']['bin_version_string'] is True)
ok &= check('fork row', (r['ref']['fork_line'] or '').endswith('ee9632b'))
ok &= check('interference reading row', read('fs11_v', repl(spec('fs11_v'), 'GuestOut: Level has started: %s' % SKY, None))['reading'].startswith('INTERFERENCE'))
ok &= check('reading row says no verdict', 'no verdict' in r['reading'])

# --- the table over runs ---
rd = os.path.join(TMP, 'runs')
os.makedirs(os.path.join(rd, 'fs11_v'))
json.dump(r, open(os.path.join(rd, 'fs11_v', 'read.json'), 'w'), default=list)
tb = R.table(rd)
ok &= check('table row of fs11_v with the last FixB12Stat', len(tb) == 3 and 'passes=5000 rewalk=3000 rwd=7 lskip=2' in tb[2])

# --- strict cp1250 output (in-process, no child process - mutlib workers), ASCII, json, usage ---
d = os.path.join(TMP, 'cp')
write(d, spec('fs11_w'))
js = os.path.join(TMP, 'o.json')
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        rc_cp = R.main(['--dir', d, '--tag', 'fs11_w', '--json', js])
        R.main(['--dir', d, '--tag', 'fs11_v'])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
    rc_cp = None
ok &= check('output in strict cp1250 without PYTHONIOENCODING, rc 0', cp_ok and rc_cp == 0 and len(raw.getvalue()) > 1000)
ok &= check('output ASCII only', all(c < 128 for c in raw.getvalue()))
ok &= check('json written and ASCII', os.path.exists(js) and all(c < 128 for c in open(js, 'rb').read()))
ok &= check('json carries the form and the FixB12Stat row', json.load(open(js)).get('form') == 'fs11_w'
            and json.load(open(js))['fixb12stat']['last']['rwd'] == 7)
for bad in ('fs10_v', 'b12_v', 'b13_v', 'fs11_v_r4', 'fs11_x', 'fs11_z_r0'):
    with contextlib.redirect_stdout(io.StringIO()):
        rc_u = R.main([bad])
    ok &= check('usage rc 2 for %s' % bad, rc_u == 2)
shutil.rmtree(TMP, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
