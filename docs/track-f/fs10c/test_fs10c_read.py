"""Fixtures of fs10c_read.py (Track F link FS10c, HPP-686): a clean synthetic tag of each form reads ADMITTED / ALL YES; every admission
member and every member of every form, and each edge (window edges, 2 900 000 / 2 500 000 / 1 000 000, exit gap 250, first scene frame,
sleep placement, mode line after GuestOut, mode=0 requested=1 reason=direction), flips the reading; strict cp1250 output without
PYTHONIOENCODING; the last line is ALL OK.  ASCII only.
usage: python test_fs10c_read.py"""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fs10c_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_fs10c_read.py sha256 %s target fs10c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(R.__file__)))
N = [0, 0]
SEAL = b'seal fixture\n'
AT = 1000000   # at_ms of the stand config (process start + 60 000 ms)


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
        print('FAIL %s' % name)


def env_of(base):
    e = dict((k, ('C:/x/' + k) if v is None else v) for k, v in R.expected_env(base).items())
    return e


def spec(base):
    """The clean tag of the form: a list of log lines and the side files."""
    kind = R.kind_of(base)
    L = ['Fork build arigandores/KytyPS5 dc5d471', 'ShaderSeed: compatibility=x:KytySC3:%s:y' % R.SIG,
         'Shader translation cache: C:/e/_ShaderCache/PPSA21564/%s' % R.VARIANT_DIR]
    if base != 'fs10_s0':
        L.append('LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100')
    if kind == 'w':
        L.append('DualSrcBlend: supported=1 enabled=1')
    if kind in ('v', 'w'):
        L.append('FixB13: mode=1')
    if kind in ('stand_user', 'stand_harness'):
        L.append('TestLogStall: config at_ms=%d sleep_ms=3000 k=3 gap_ms=5000 on=%s' % (AT, 'caller' if base == 'fs10_s0' else 'writer'))
    L += ['GuestOut: Level has started: ', 'GuestOut: Level has started: %s' % R.SKY]
    if kind != 'stand_user':
        L.append('FrameTrace: n=10 dt_us=500000 draws=20')
        L.append('FrameTrace: n=11 dt_us=16000 draws=300')     # the first scene frame
        nfr = {'stand_harness': 9000, 'v': 20000, 'w': 2500}[kind]
        dt = {'stand_harness': 16700, 'v': 16700, 'w': 130000}[kind]
        for i in range(nfr):
            L.append('FrameTrace: n=%d dt_us=%d draws=300' % (12 + i, dt))
    on = 'caller' if base == 'fs10_s0' else 'writer'
    if kind in ('stand_user', 'stand_harness'):
        for i in range(3):
            t0 = AT + 8000 * i
            L.append('TestLogStall: i=%d sleep_ms=3000 slept_us=3000400 t0_ms=%d t1_ms=%d on=%s tid=7 role=other line="abc"' % (
                i + 1, t0, t0 + 3000, on))
            if base == 'fs10_s0':
                L.append('LongFrame: n=%d dt_us=3016000 log_async=0 t_ms=%d' % (100 + i, t0 + 3020))
            else:
                L.append('LogAsync: stall us=3000500 queued_bytes=1000 t_ms=%d' % (t0 + 3000))
    if base != 'fs10_s0':
        L.append('LogAsync: full_waits=0 full_wait_us=0 stalls=3 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0')
    if kind == 'w':
        L += ['[Vulkan][W] something'] * 5
    hold = {'stand_user': 150, 'stand_harness': 150, 'v': 330, 'w': 310}[kind]
    cmd = ['emu', '--vulkan-validation', 'true' if kind == 'w' else 'false', '--shader-validation', 'false']
    att = dict(outcome='ok', hold_exit=None, hold_s=float(hold), stable_s=12.0)
    run = dict(binary_sha256=R.BIN_FS10, env=env_of(base), cmdline=cmd, attempts=[att], guest_args='-lvl ' + R.SKY, hold_s=hold,
               prereg=dict(sha256=hashlib.sha256(SEAL).hexdigest()))
    side = dict(installed_before=R.BIN_FS9, installed_after=R.BIN_FS9, installed_sha=R.BIN_FS10, level=R.SKY,
                manifest_cmp='manifest cmp EQUAL files 5 listsha x')
    if kind == 'v':
        side.update(glitch='one-frame glitches: 0', sheet='sheet ok')
    return dict(lines=L, run=run, side=side, idx=(3200 if kind == 'v' else 0), stdout='')


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
        f.write(b'xx' + R.VERSION + b'yy')


TMP = tempfile.mkdtemp(prefix='fs10c_fx_')
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


def adm(r, start):
    for a, b in r['admission']:
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


BASES = ('fs10_s1', 'fs10_s0', 'fs10_f1', 'fs10_v', 'fs10_w')
for b in BASES:
    r = read(b, spec(b))
    check('%s clean ADMITTED' % b, r['status'] == 'ADMITTED')
    check('%s clean ALL YES %s' % (b, [a for a, x in (r['members'] or []) if not x]), r['ok'] is True)
    for tg in (b + '_r1', b + '_r3'):
        check('%s tag form %s' % (b, tg), R.base_of(tg) == b)

# --- admission members (each flips to INTERFERENCE) ---
for b in BASES:
    s = spec(b)
    for key, val in (('installed_before', R.BIN_FS10), ('installed_after', 'x'), ('installed_sha', R.BIN_FS9), ('level', 'pot'),
                     ('manifest_cmp', 'manifest cmp DIFFER only-before 1')):
        t = copy.deepcopy(s)
        t['side'][key] = val
        check('%s admission %s' % (b, key), read(b, t)['status'] == 'INTERFERENCE')
    for key, val in (('binary_sha256', R.BIN_FS9), ('guest_args', '-lvl pot'), ('hold_s', 100)):
        t = copy.deepcopy(s)
        t['run'][key] = val
        check('%s admission run %s' % (b, key), read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['prereg']['sha256'] = 'x'
    check('%s admission prereg' % b, read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['env']['KYTY_FIX_B36'] = '1'
    check('%s admission env extra KYTY_FIX_B36=1 (or wrong value)' % b, read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['env']['KYTY_DIAG_B32'] = '1'
    check('%s admission env KYTY_DIAG_B32' % b, read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['env']['KYTY_GAME_PATCH'] = 'p'
    check('%s admission env KYTY_GAME_PATCH' % b, read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    k0 = sorted(t['run']['env'])[0]
    del t['run']['env'][k0]
    check('%s admission env missing %s' % (b, k0), read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['cmdline'] = t['run']['cmdline'] + ['--vulkan-validation', 'false' if b == 'fs10_w' else 'true']
    check('%s admission last vulkan-validation' % b, read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['cmdline'] = t['run']['cmdline'] + ['--rd']
    check('%s admission --rd' % b, read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['attempts'][0]['outcome'] = 'not_entered'
    check('%s admission outcome' % b, read(b, t)['status'] == 'INTERFERENCE')
    for extra in ('Window 1 minimized', 'Recovering Vulkan swapchain', 'GamePatch: loaded', 'DiagB32: mode=1'):
        t = copy.deepcopy(s)
        t['lines'].insert(4, extra)
        check('%s admission line %s' % (b, extra), read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['lines'].insert(4, 'Window 1 restored')
    check('%s restored is not interference' % b, read(b, t)['status'] == 'ADMITTED')
    check('%s admission signature' % b, read(b, repl(s, 'ShaderSeed:', 'ShaderSeed: compatibility=x:KytySC3:%s:y' % ('0' * 40)))['status'] == 'INTERFERENCE')
    check('%s admission catalog' % b, read(b, repl(s, 'Shader translation cache:', 'Shader translation cache: C:/e/variant_fixb26'))['status'] == 'INTERFERENCE')
    check('%s admission entry line' % b, read(b, repl(s, 'GuestOut: Level has started: %s' % R.SKY, None))['status'] == 'INTERFERENCE')
    if b == 'fs10_s0':
        t = copy.deepcopy(s)
        t['lines'].insert(-1, 'LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=1 bytes=1 max_queued_bytes=1 sync_lines=0 drain_timeouts=0')
        r = read(b, t)
        check('s0 LogAsync summary line -> member NO', r['status'] == 'ADMITTED' and mem(r, '0 LogAsync') is False)
    else:
        r = read(b, repl(s, 'LogAsync: full_waits=', None))
        check('%s no summary -> INTERFERENCE run' % b, r['status'] == 'INTERFERENCE' and r['interference'].startswith('run'))
        r = read(b, repl(s, 'LogAsync: full_waits=', 'LogAsync: full_waits=0 full_wait_us=0'))
        check('%s summary missing fields -> INTERFERENCE' % b, r['status'] == 'INTERFERENCE')
    if R.kind_of(b) in ('stand_user', 'stand_harness'):
        check('%s stand config absent' % b, read(b, repl(s, 'TestLogStall: config', None))['status'] == 'INTERFERENCE')
        check('%s stand config k=2' % b, read(b, repl(s, 'TestLogStall: config', lambda l: l.replace('k=3', 'k=2')))['status'] == 'INTERFERENCE')
        check('%s stand sleep 3 absent' % b, read(b, repl(s, 'TestLogStall: i=3', None))['status'] == 'INTERFERENCE')
        check('%s stand slept 2 899 999' % b, read(b, repl(s, 'TestLogStall: i=2', lambda l: l.replace('slept_us=3000400', 'slept_us=2899999')))['status'] == 'INTERFERENCE')
        check('%s stand slept 2 900 000 edge ok' % b, read(b, repl(s, 'TestLogStall: i=2', lambda l: l.replace('slept_us=3000400', 'slept_us=2900000')))['status'] == 'ADMITTED')
        check('%s stand bad sleep line' % b, read(b, repl(s, 'TestLogStall: i=2', 'TestLogStall: i=2 garbage'))['status'] == 'INTERFERENCE')
        # placement: the first sleep before the anchor
        t = copy.deepcopy(s)
        sl = [l for l in t['lines'] if l.startswith('TestLogStall: i=1')][0]
        t['lines'].remove(sl)
        t['lines'].insert(1, sl)
        check('%s stand sleep before the anchor' % b, read(b, t)['status'] == 'INTERFERENCE')
        t = copy.deepcopy(s)
        t['stdout'] = '--- Fatal Error ---'
        check('%s stand death in stdout' % b, read(b, t)['status'] == 'INTERFERENCE')
        t = copy.deepcopy(s)
        t['lines'].insert(-1, 'Unhandled exception: x')
        check('%s stand death in log' % b, read(b, t)['status'] == 'INTERFERENCE')
    else:
        t = copy.deepcopy(s)
        t['lines'].insert(5, 'TestLogStall: config at_ms=1 sleep_ms=3000 k=3 gap_ms=5000 on=writer')
        check('%s non-stand TestLogStall line' % b, read(b, t)['status'] == 'INTERFERENCE')

# --- user form ---
for b in ('fs10_s1', 'fs10_s0'):
    s = spec(b)
    t = copy.deepcopy(s)
    t['lines'].append('FrameTrace: n=1 dt_us=1 draws=1')
    check('%s FrameTrace in user form' % b, read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['attempts'][0]['hold_s'] = 119.9
    check('%s hold 119.9' % b, read(b, t)['status'] == 'INTERFERENCE')
    t = copy.deepcopy(s)
    t['run']['attempts'][0]['hold_exit'] = 'died'
    check('%s hold_exit' % b, read(b, t)['status'] == 'INTERFERENCE')
    # exit window: estimated exit = AT - 60000 + 1000*(12+150) = AT + 102000; last t1 = AT + 19000; gap = 102000 - 21000
    t = copy.deepcopy(s)
    t['run']['attempts'][0]['hold_s'] = 120.0
    t['run']['attempts'][0]['stable_s'] = 0.0
    r = read(b, t)   # exit = AT + 60000, gap 60000 - 21000 = 39000 -> ok
    check('%s exit window ok' % b, mem(r, 'exit window') is True)
    last_t1 = AT + 16000 + 3000
    for st, want in ((((last_t1 + 2000 + 250) - AT + 60000) / 1000.0 - 120.0, True), (((last_t1 + 2000 + 249) - AT + 60000) / 1000.0 - 120.0, False)):
        t = copy.deepcopy(s)
        t['run']['attempts'][0]['hold_s'] = 120.0
        t['run']['attempts'][0]['stable_s'] = st
        r = read(b, t)
        check('%s exit window edge stable %.3f -> %s' % (b, st, want), mem(r, 'exit window') is want)

s = spec('fs10_s1')
r = read('fs10_s1', repl(s, 'LogAsync: mode=1', 'LogAsync: mode=0 requested=1 reason=direction'))
check('s1 mode=0 requested=1 reason=direction -> NO (item 626 (g))', mem(r, 'LogAsync: mode=1') is False)
t = copy.deepcopy(s)
ml = [l for l in t['lines'] if l.startswith('LogAsync: mode=1')][0]
t['lines'].remove(ml)
t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, ml)
check('s1 mode line after the first GuestOut -> NO', mem(read('fs10_s1', t), 'LogAsync: mode=1') is False)
t = copy.deepcopy(s)
t['lines'].insert(3, 'LogAsync: mode=1 limit_bytes=1 drain_ms=1 stall_ms=1 flush_ms=1')
check('s1 two mode lines -> NO', mem(read('fs10_s1', t), 'LogAsync: mode=1') is False)
check('s1 on=caller sleeps -> NO', mem(read('fs10_s1', repl(s, 'TestLogStall: i=2', lambda l: l.replace('on=writer', 'on=caller'))), '3 sleeps') is False)
check('s1 config on=caller -> NO', mem(read('fs10_s1', repl(s, 'TestLogStall: config', lambda l: l.replace('on=writer', 'on=caller'))), '3 sleeps') is False)
t = copy.deepcopy(s)
t['lines'].insert(-1, 'LongFrame: n=500 dt_us=1000000 log_async=1 t_ms=%d' % (AT + 50000))
check('s1 LongFrame 1 000 000 after the entry -> NO', mem(read('fs10_s1', t), '0 LongFrame') is False)
t = copy.deepcopy(s)
t['lines'].insert(-1, 'LongFrame: n=500 dt_us=999999 log_async=1 t_ms=%d' % (AT + 50000))
check('s1 LongFrame 999 999 -> YES', mem(read('fs10_s1', t), '0 LongFrame') is True)
t = copy.deepcopy(s)
t['lines'].insert(2, 'LongFrame: n=5 dt_us=2000000 log_async=1 t_ms=1')
r = read('fs10_s1', t)
check('s1 LongFrame >= 1 s before the entry -> YES by the letter, whole log 1 printed', mem(r, '0 LongFrame') is True and r['info']['lf_ge1s'] == 1)
check('s1 stall 2 899 999 -> NO', mem(read('fs10_s1', repl(s, 'LogAsync: stall', 'LogAsync: stall us=2899999 queued_bytes=1 t_ms=1')), '>= 3 LogAsync') is False)
check('s1 stall 2 900 000 edge -> YES', mem(read('fs10_s1', repl(s, 'LogAsync: stall', 'LogAsync: stall us=2900000 queued_bytes=1 t_ms=1')), '>= 3 LogAsync') is True)
check('s1 stall flush=1 counts', mem(read('fs10_s1', repl(s, 'LogAsync: stall', 'LogAsync: stall us=3000000 queued_bytes=1 t_ms=1 flush=1')), '>= 3 LogAsync') is True)
fw = 'LogAsync: full_waits=0 full_wait_us=0 stalls=3 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0'
r = read('fs10_s1', repl(s, 'LogAsync: full_waits=', fw.replace('full_waits=0', 'full_waits=1')))
check('s1 full_waits 1 -> NO', mem(r, 'full_waits 0') is False)
r = read('fs10_s1', repl(s, 'LogAsync: full_waits=', fw.replace('drain_timeouts=0', 'drain_timeouts=1')))
check('s1 drain_timeouts 1 -> NO', mem(r, 'drain_timeouts 0') is False)

s = spec('fs10_s0')
check('s0 clean -> 0 LogAsync YES', mem(read('fs10_s0', s), '0 LogAsync') is True)
t = copy.deepcopy(s)
t['lines'].insert(3, 'LogAsync: mode=0 requested=0 reason=x')
check('s0 LogAsync: mode line -> NO', mem(read('fs10_s0', t), '0 LogAsync') is False)
t = copy.deepcopy(s)
t['lines'].insert(-1, 'LogAsync: stall us=5 queued_bytes=1 t_ms=1')
check('s0 LogAsync: stall line -> NO', mem(read('fs10_s0', t), '0 LogAsync') is False)
check('s0 on=writer -> NO', mem(read('fs10_s0', repl(s, 'TestLogStall: i=1', lambda l: l.replace('on=caller', 'on=writer'))), '3 sleeps') is False)
check('s0 sleep 2 without LongFrame -> NO', mem(read('fs10_s0', repl(s, 'LongFrame: n=101', None)), 'every sleep') is False)
check('s0 LongFrame 2 499 999 -> NO', mem(read('fs10_s0', repl(s, 'LongFrame: n=101', lambda l: l.replace('dt_us=3016000', 'dt_us=2499999'))), 'every sleep') is False)
check('s0 LongFrame 2 500 000 edge -> YES', mem(read('fs10_s0', repl(s, 'LongFrame: n=101', lambda l: l.replace('dt_us=3016000', 'dt_us=2500000'))), 'every sleep') is True)
t0 = AT + 8000
for tm, want in ((t0 - 2000, True), (t0 - 2001, False), (t0 + 3000 + 2000, True), (t0 + 3000 + 2001, False)):
    r = read('fs10_s0', repl(s, 'LongFrame: n=101', 'LongFrame: n=101 dt_us=3016000 log_async=0 t_ms=%d' % tm))
    check('s0 window edge t_ms %d -> %s' % (tm - t0, want), mem(r, 'every sleep') is want)

# --- harness stand f1 ---
s = spec('fs10_f1')
t = copy.deepcopy(s)
t['lines'].insert(t['lines'].index('FrameTrace: n=11 dt_us=16000 draws=300') + 3, 'FrameTrace: n=9999 dt_us=1000000 draws=300')
check('f1 frame 1 000 000 after the first scene frame -> NO', mem(read('fs10_f1', t), '0 FrameTrace') is False)
t = copy.deepcopy(s)
t['lines'].insert(t['lines'].index('FrameTrace: n=11 dt_us=16000 draws=300') + 3, 'FrameTrace: n=9999 dt_us=999999 draws=300')
check('f1 frame 999 999 -> YES', mem(read('fs10_f1', t), '0 FrameTrace') is True)
r = read('fs10_f1', repl(s, 'FrameTrace: n=11 ', 'FrameTrace: n=11 dt_us=5000000 draws=300'))
check('f1 the first scene frame itself >= 1 s -> YES by the letter, printed with it 1', mem(r, '0 FrameTrace') is True and r['info']['ge1s_with_first'] == 1)
r = read('fs10_f1', repl(s, 'FrameTrace: n=10 ', 'FrameTrace: n=10 dt_us=5000000 draws=20'))
check('f1 frame >= 1 s before the first scene frame (draws < 100) -> YES', mem(r, '0 FrameTrace') is True)
t = copy.deepcopy(s)
t['lines'] = [l.replace('draws=300', 'draws=99') for l in t['lines']]
check('f1 no first scene frame (draws 99) -> INTERFERENCE', read('fs10_f1', t)['status'] == 'INTERFERENCE')
t = copy.deepcopy(s)
t['lines'] = [l for l in t['lines'] if not (l.startswith('FrameTrace: n=') and int(l.split('=')[1].split()[0]) >= 7000)]
check('f1 scene < 120 s -> INTERFERENCE', read('fs10_f1', t)['status'] == 'INTERFERENCE')
check('f1 on=caller -> NO', mem(read('fs10_f1', repl(s, 'TestLogStall: i=3', lambda l: l.replace('on=writer', 'on=caller'))), '3 sleeps') is False)
check('f1 stall 2 899 999 -> NO', mem(read('fs10_f1', repl(s, 'LogAsync: stall', 'LogAsync: stall us=2899999 queued_bytes=1 t_ms=1')), '>= 3 LogAsync') is False)
check('f1 mode=0 -> NO', mem(read('fs10_f1', repl(s, 'LogAsync: mode=1', 'LogAsync: mode=0 requested=1 reason=direction')), 'LogAsync: mode=1') is False)
r = read('fs10_f1', repl(s, 'LogAsync: full_waits=', fw.replace('full_waits=0', 'full_waits=2')))
check('f1 full_waits 2 -> NO', mem(r, 'full_waits 0') is False)
r = read('fs10_f1', repl(s, 'LogAsync: full_waits=', fw.replace('drain_timeouts=0', 'drain_timeouts=1')))
check('f1 drain_timeouts 1 -> NO', mem(r, 'drain_timeouts 0') is False)
t = copy.deepcopy(s)
sl = [l for l in t['lines'] if l.startswith('TestLogStall: i=1')][0]
t['lines'].remove(sl)
t['lines'].insert(t['lines'].index('FrameTrace: n=11 dt_us=16000 draws=300'), sl)
check('f1 sleep before the first scene frame -> INTERFERENCE', read('fs10_f1', t)['status'] == 'INTERFERENCE')

# --- v ---
s = spec('fs10_v')
t = copy.deepcopy(s)
t['lines'].insert(-2, 'FrameTrace: n=99999 dt_us=1000000 draws=300')
check('v frame 1 s -> NO', mem(read('fs10_v', t), '0 frames >= 1 s') is False)
t = copy.deepcopy(s)
t['lines'] = [l for l in t['lines'] if not (l.startswith('FrameTrace: n=') and int(l.split('=')[1].split()[0]) >= 17900)]
check('v hold < 300 s -> NO', mem(read('fs10_v', t), 'hold >= 300') is False)
t = copy.deepcopy(s)
t['idx'] = 2999
check('v video 2999 -> NO', mem(read('fs10_v', t), 'video index') is False)
t = copy.deepcopy(s)
t['idx'] = 3000
check('v video 3000 edge -> YES', mem(read('fs10_v', t), 'video index') is True)
t = copy.deepcopy(s)
t['side']['glitch'] = 'one-frame glitches: 1'
check('v glitch 1 -> NO', mem(read('fs10_v', t), '0 one-frame') is False)
t = copy.deepcopy(s)
del t['side']['glitch']
check('v no glitch file -> NO', mem(read('fs10_v', t), '0 one-frame') is False)
t = copy.deepcopy(s)
del t['side']['sheet']
check('v no sheet -> NO', mem(read('fs10_v', t), 'sheet') is False)
t = copy.deepcopy(s)
t['stdout'] = 'GpuHangAbort: x'
check('v death stdout -> NO', mem(read('fs10_v', t), '0 death') is False)
t = copy.deepcopy(s)
t['run']['attempts'][0]['hold_exit'] = 'died'
check('v hold_exit -> NO', mem(read('fs10_v', t), 'the process lived') is False)
check('v FixB13 mode=0 -> NO', mem(read('fs10_v', repl(s, 'FixB13: mode=1', 'FixB13: mode=0')), 'FixB13') is False)
check('v FixB13 absent -> NO', mem(read('fs10_v', repl(s, 'FixB13: mode=1', None)), 'FixB13') is False)
check('v mode=0 -> NO', mem(read('fs10_v', repl(s, 'LogAsync: mode=1', 'LogAsync: mode=0 requested=1 reason=direction')), 'LogAsync: mode=1') is False)
r = read('fs10_v', repl(s, 'LogAsync: full_waits=', fw.replace('drain_timeouts=0', 'drain_timeouts=3')))
check('v drain_timeouts 3 -> NO', mem(r, 'drain_timeouts 0') is False)

# --- w ---
s = spec('fs10_w')
t = copy.deepcopy(s)
t['lines'].insert(-2, '[Vulkan][E] VUID-x')
check('w [Vulkan][E] -> NO', mem(read('fs10_w', t), '0 [Vulkan][E]') is False)
t = copy.deepcopy(s)
t['lines'].insert(-2, 'x this will be the last time reporting it')
check('w limit line -> NO', mem(read('fs10_w', t), '0 limit') is False)
check('w no [Vulkan][W] -> NO', mem(read('fs10_w', repl(s, '[Vulkan][W]', None, True)), 'positive control') is False)
check('w DualSrcBlend 0 -> NO', mem(read('fs10_w', repl(s, 'DualSrcBlend', 'DualSrcBlend: supported=1 enabled=0')), 'DualSrcBlend') is False)
t = copy.deepcopy(s)
dl = [l for l in t['lines'] if l.startswith('DualSrcBlend')][0]
t['lines'].remove(dl)
t['lines'].append(dl)
check('w DualSrcBlend after GuestOut -> NO', mem(read('fs10_w', t), 'DualSrcBlend') is False)
t = copy.deepcopy(s)
t['run']['attempts'][0]['hold_s'] = 309.9
check('w hold 309.9 -> NO', mem(read('fs10_w', t), 'lived to the end') is False)
t = copy.deepcopy(s)
t['run']['attempts'][0]['hold_s'] = 309.9
t['lines'].insert(-2, '[Vulkan][E] VUID-x')
check('w VALIDATION_STOP -> NO', mem(read('fs10_w', t), 'no VALIDATION_STOP') is False)
check('w mode=0 -> NO', mem(read('fs10_w', repl(s, 'LogAsync: mode=1', 'LogAsync: mode=0 requested=1 reason=direction')), 'LogAsync: mode=1') is False)
check('w FixB13 absent -> NO', mem(read('fs10_w', repl(s, 'FixB13: mode=1', None)), 'FixB13') is False)

# --- reference rows ---
r = read('fs10_v', spec('fs10_v'))
check('bin version string row', r['ref']['bin_version_string'] is True)
check('fork row', (r['ref']['fork_line'] or '').endswith('dc5d471'))
check('interference reading row', read('fs10_v', repl(spec('fs10_v'), 'GuestOut: Level has started: %s' % R.SKY, None))['reading'].startswith('INTERFERENCE'))

# --- strict cp1250 output without PYTHONIOENCODING, json written ---
d = os.path.join(TMP, 'cp')
write(d, spec('fs10_f1'))
env = dict(os.environ)
env.pop('PYTHONIOENCODING', None)
env['PYTHONUTF8'] = '0'
js = os.path.join(TMP, 'o.json')
p = subprocess.run([sys.executable, '-X', 'utf8=0', R.__file__, '--dir', d, '--tag', 'fs10_f1', '--json', js], capture_output=True, env=env)
check('cp1250 run rc 0 (%s)' % p.stderr[-200:], p.returncode == 0)
try:
    p.stdout.decode('cp1250', 'strict')
    ok = all(c < 128 for c in p.stdout)
except UnicodeDecodeError:
    ok = False
check('output is ASCII / strict cp1250', ok)
check('json written and ASCII', os.path.exists(js) and all(c < 128 for c in open(js, 'rb').read()))
check('usage rc 2', subprocess.run([sys.executable, R.__file__, 'b36_v'], capture_output=True, env=env).returncode == 2)
shutil.rmtree(TMP, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if N[1] == 0:
    print('ALL OK')
sys.exit(0 if N[1] == 0 else 1)
