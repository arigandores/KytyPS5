"""Fixtures of f38c_read.py (Track F link F38c, HPP-765; ROADMAP s122 item 691 (d)(4)): the clean synthetic tag f25_v reads ADMITTED /
ALL YES; every admission member (env: KYTY_FIX_F25 '1' exactly, no other KYTY_FIX_*, no KYTY_TEST_* / KYTY_GAME_PATCH; 'ExitFatal:'
lines in the log and in stdout; installed before / after = FS12, during = F38a) and every member of the letter and of the form fs12_v
flips the reading; edges (1 000 000 / 999 999, hold 300 s, video 2 999 / 3 000, draws 99 / 100, FixF25 mode=0 / absent / after GuestOut
/ unparsable / second line, FixF21 mode=0 / absent, Event: quit absent, '--- Fatal Error ---' before / after quit and in stdout,
wait_expired in log / stdout, close_killed / close_rc null); the F25 rows ('FixF25: read failed twice', 'KernelRead: direct read
failed' in the log and in stdout - rows only, members stay ALL YES); the exit rows; strict cp1250 output without PYTHONIOENCODING; the
last line is ALL OK.  Port of C:/kyty/f287/fs12c/test_fs12c_read.py (FS12c, the kind v).  Early-exit form (ok = True, ok &= ...,
sys.exit(0 if ok else 1)).  ASCII only.
The reader is loaded in-process from argv[1] (default: f38c_read.py beside this file); the fixture directories live under BASE.
usage: python test_f38c_read.py [<f38c_read.py under test>]"""
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f38c_read.py')
BASE = Path(os.path.join(HERE, 'fx_f38c'))
_spec = importlib.util.spec_from_file_location('f38c_read_under_test', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f38c_read.py sha256 %s target f38c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0, 0]
SEAL = b'seal fixture\n'
TB = '5a14a1118e041c85257d7fd6faa8c8c98cea5c1c5a17ae7a4eff6707ec204754'   # literals, not the reader's constants
FS12 = '46892c20080819ae090598511748265dfbac31f303a02f1804e5b10db8acae26'
FS11 = 'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1917-g531d6488'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
TAG = 'f25_v'
ok = True


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
        print('FAIL %s' % name)
    return bool(cond)


def env_of():
    return dict(KYTY_GUEST_ARGS='-lvl ' + SKY, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE='C:/x/g', KYTY_SAMPLE_GATE='C:/x/s', KYTY_QUEUE_TRACE='1',
                KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8', KYTY_REC='C:/x/rec.mp4', KYTY_FIX_F25='1')


STAT = 'FixB12Stat: passes=%d rewalk=%d rwd=%d lskip=%d'
F21 = 'FixF21: mode=1 wait_ms=12000'
F25 = 'FixF25: mode=1'


def spec():
    """The clean tag: a list of log lines and the side files."""
    L = ['LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100', 'Fork build arigandores/KytyPS5 531d648',
         F21, 'ShaderSeed: compatibility=x:KytySC3:%s:y' % SIG, 'Shader translation cache: C:/e/_ShaderCache/PPSA21564/%s' % VARIANT_DIR,
         'FixB12: mode=1', 'FixB13: mode=1', F25, 'DualSrcBlend: supported=1 enabled=1', 'GuestOut: Level has started: ',
         'GuestOut: Level has started: %s' % SKY, 'FrameTrace: n=10 dt_us=500000 draws=20', 'FrameTrace: n=11 dt_us=16000 draws=300']
    for i in range(20000):
        L.append('FrameTrace: n=%d dt_us=16700 draws=300' % (12 + i))
        if i in (100, 900):
            L.append(STAT % (i, i // 2, 0, 1))
    L.append(STAT % (5000, 3000, 7, 2))
    L += ['Event: quit', 'shutdown line']
    L.append('LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0')
    cmd = ['emu', '--vulkan-validation', 'false', '--shader-validation', 'false']
    att = dict(outcome='ok', hold_exit=None, hold_s=330.2, stable_s=12.0, close_posted=5, close_rc=0, close_killed=False,
               close_s=4.1, close_wait_s=40)
    run = dict(binary_sha256=TB, env=env_of(), cmdline=cmd, attempts=[att], guest_args='-lvl ' + SKY, hold_s=330,
               prereg=dict(sha256=hashlib.sha256(SEAL).hexdigest()))
    side = dict(installed_before=FS12, installed_after=FS12, installed_sha=TB, level=SKY, manifest_cmp='manifest cmp EQUAL files 5 listsha x',
                glitch='one-frame glitches: 0', sheet='sheet ok')
    return dict(lines=L, run=run, side=side, idx=3200, stdout='stdout line\n')


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
    if s['stdout'] is not None:
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


def read(s, tag=TAG):
    CNT[0] += 1
    d = os.path.join(TMP, 'c%d' % CNT[0])
    write(d, s)
    r = R.read_tag(tag, R.paths(tag, d))
    shutil.rmtree(d, ignore_errors=True)
    return r


def mem(r, start):
    for a, b in (r['members'] or []) + (r['form_members'] or []):
        if a.startswith(start):
            return b
    return None


def in_letter(r, start):
    return any(a.startswith(start) for a, b in (r['members'] or []))


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


def before_quit(s, line):
    s = copy.deepcopy(s)
    s['lines'].insert(s['lines'].index('Event: quit'), line)
    return s


def after_quit(s, line):
    s = copy.deepcopy(s)
    s['lines'].insert(s['lines'].index('Event: quit') + 1, line)
    return s


S = spec()

# --- the clean tag ---
r = read(S)
ok &= check('clean ADMITTED %s' % [a for a, x in r['admission'] if not x], r['status'] == 'ADMITTED')
ok &= check('clean members ALL YES %s' % [a for a, x in (r['members'] or []) if not x], r['ok'] is True)
ok &= check('clean form members ALL YES %s' % [a for a, x in (r['form_members'] or []) if not x], r['form_ok'] is True)
ok &= check('clean exit rows', r['exit']['close_rc'] == 0 and r['exit']['close_s'] == 4.1 and r['exit']['close_rc_hex'] == '0x00000000')
ok &= check('clean reading says no verdict, F38d', 'no verdict' in r['reading'] and 'F38d' in r['reading'])
ok &= check('clean admission count 24 (%d)' % len(r['admission']), len(r['admission']) == 24)
ok &= check('members count 8 / 11 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 8 and len(r['form_members']) == 11)
ok &= check('letter carries FixF25, form carries FixF21', in_letter(r, 'FixF25: mode=1') and not in_letter(r, 'FixF21: mode=1')
            and mem(r, 'FixF21: mode=1') is True)
ok &= check('clean F25 rows 0 / 0 / 0 / 0, mode lines 1',
            r['f25_rows']['read_failed_twice_log'] == 0 and r['f25_rows']['read_failed_twice_stdout'] == 0
            and r['f25_rows']['direct_read_failed_log'] == 0 and r['f25_rows']['direct_read_failed_stdout'] == 0
            and r['f25_rows']['f25_mode_lines'] == 1)
for tg in ('f25_v_r1', 'f25_v_r3'):
    ok &= check('tag form %s' % tg, R.TAG_RX.match(tg) is not None)

# --- admission members (each flips to NOT_ADMITTED) ---
for key, val in (('installed_before', TB), ('installed_before', FS11), ('installed_after', FS11), ('installed_after', 'x'),
                 ('installed_sha', FS12), ('level', 'pot'), ('manifest_cmp', 'manifest cmp DIFFER only-before 1')):
    t = copy.deepcopy(S)
    t['side'][key] = val
    ok &= check('admission %s=%s' % (key, val[:8]), read(t)['status'] == 'NOT_ADMITTED')
t = copy.deepcopy(S)
del t['side']['manifest_cmp']
ok &= check('admission no manifest_cmp file', read(t)['status'] == 'NOT_ADMITTED')
for key, val in (('binary_sha256', FS12), ('guest_args', '-lvl pot'), ('hold_s', 150)):
    t = copy.deepcopy(S)
    t['run'][key] = val
    ok &= check('admission run %s' % key, read(t)['status'] == 'NOT_ADMITTED')
t = copy.deepcopy(S)
t['run']['prereg']['sha256'] = 'x'
ok &= check('admission prereg', read(t)['status'] == 'NOT_ADMITTED')
for kk, vv in (('KYTY_FIX_B12', '1'), ('KYTY_FIX_B36', '1'), ('KYTY_FIX_F21', '1'), ('KYTY_FIX_F21', '0'), ('KYTY_FIX_F24', '1'),
               ('KYTY_DIAG_B32', '1'), ('KYTY_GAME_PATCH', 'p'), ('KYTY_GPU_CHECKPOINTS', '1'), ('KYTY_S_REPLAY', '3'),
               ('KYTY_FIX_F25', '0'), ('KYTY_FIX_F25', 'true'), ('KYTY_FIX_F25', ''), ('VK_LAYER_PATH', 'x')):
    t = copy.deepcopy(S)
    t['run']['env'][kk] = vv
    ok &= check('admission env %s=%s' % (kk, vv), read(t)['status'] == 'NOT_ADMITTED')
for kk in ('KYTY_TEST_EXITFATAL', 'KYTY_TEST_HIDLOSS', 'KYTY_TEST_LOGSTALL'):
    t = copy.deepcopy(S)
    t['run']['env'][kk] = 'P:1'
    r = read(t)
    own = [b for a, b in r['admission'] if a.startswith('no KYTY_TEST_*')]
    ok &= check('env %s -> NOT_ADMITTED by its own member' % kk, r['status'] == 'NOT_ADMITTED' and own == [False])
for where in ('log', 'stdout'):
    t = copy.deepcopy(S)
    if where == 'log':
        t['lines'].insert(4, 'ExitFatal: config arm=P seed=1')
    else:
        t['stdout'] = 'ExitFatal: config arm=P seed=1\n'
    r = read(t)
    own = [b for a, b in r['admission'] if a.startswith('0 ExitFatal:')]
    ok &= check('ExitFatal: in %s -> NOT_ADMITTED' % where, r['status'] == 'NOT_ADMITTED' and own == [False])
t = copy.deepcopy(S)
t['lines'].insert(4, 'ExitFatal without colon')
ok &= check('ExitFatal without colon -> ADMITTED', read(t)['status'] == 'ADMITTED')
for k0 in ('KYTY_REC', 'KYTY_GPU_CLOCK_PIN', 'KYTY_GUEST_ARGS', 'KYTY_FIX_F25', 'KYTY_GPU_HANG_ABORT_S'):
    t = copy.deepcopy(S)
    del t['run']['env'][k0]
    ok &= check('admission env missing %s' % k0, read(t)['status'] == 'NOT_ADMITTED')
for extra in (['--vulkan-validation', 'true'], ['--shader-validation', 'true'], ['--rd']):
    t = copy.deepcopy(S)
    t['run']['cmdline'] = t['run']['cmdline'] + extra
    ok &= check('admission cmdline %s' % extra, read(t)['status'] == 'NOT_ADMITTED')
t = copy.deepcopy(S)
t['run']['attempts'][0]['outcome'] = 'not_entered'
ok &= check('admission outcome', read(t)['status'] == 'NOT_ADMITTED')
for extra in ('Window 1 minimized', 'Recovering Vulkan swapchain', 'GamePatch: loaded', 'DiagB32: mode=1',
              'TestLogStall: config at_ms=1 sleep_ms=3000 k=3 gap_ms=5000 on=writer'):
    t = copy.deepcopy(S)
    t['lines'].insert(4, extra)
    ok &= check('admission line %s' % extra, read(t)['status'] == 'NOT_ADMITTED')
t = copy.deepcopy(S)
t['lines'].insert(4, 'Window 1 restored')
ok &= check('restored is not interference', read(t)['status'] == 'ADMITTED')
ok &= check('admission signature', read(repl(S, 'ShaderSeed:', 'ShaderSeed: compatibility=x:KytySC3:%s:y' % ('0' * 40)))['status'] == 'NOT_ADMITTED')
ok &= check('admission catalog', read(repl(S, 'Shader translation cache:', 'Shader translation cache: C:/e/variant_fixb26'))['status'] == 'NOT_ADMITTED')
ok &= check('admission entry line', read(repl(S, 'GuestOut: Level has started: %s' % SKY, None))['status'] == 'NOT_ADMITTED')
r = read(repl(S, 'LogAsync: full_waits=', None))
ok &= check('no summary -> NOT_ADMITTED run', r['status'] == 'NOT_ADMITTED' and r['interference'].startswith('run'))
t = copy.deepcopy(S)
t['lines'].append([l for l in t['lines'] if l.startswith('LogAsync: full_waits=')][0])
ok &= check('two summary lines -> NOT_ADMITTED', read(t)['status'] == 'NOT_ADMITTED')
t = copy.deepcopy(S)
t['stdout'] = None
ok &= check('no stdout file -> NOT_ADMITTED', read(t)['status'] == 'NOT_ADMITTED')
d = os.path.join(TMP, 'nolog')
write(d, copy.deepcopy(S))
os.remove(os.path.join(d, 'log.txt'))
r = R.read_tag(TAG, R.paths(TAG, d))
ok &= check('no log -> NOT_ADMITTED, no members', r['status'] == 'NOT_ADMITTED' and r['members'] is None)
os.remove(os.path.join(d, 'es.json'))
ok &= check('no json -> NOT_ADMITTED', R.read_tag(TAG, R.paths(TAG, d))['status'] == 'NOT_ADMITTED')

# --- FixF25 member (letter of item 691 (d)(4)) ---
FM = 'FixF25: mode=1'
ok &= check('FixF25 mode=0 -> NO, letter NOT ALL YES', mem(read(repl(S, F25, 'FixF25: mode=0')), FM) is False
            and read(repl(S, F25, 'FixF25: mode=0'))['ok'] is False)
ok &= check('FixF25 absent -> NO', mem(read(repl(S, F25, None)), FM) is False)
ok &= check('FixF25 mode=10 -> NO', mem(read(repl(S, F25, 'FixF25: mode=10')), FM) is False)
ok &= check('FixF25 trailing garbage -> NO', mem(read(repl(S, F25, F25 + ' x')), FM) is False)
ok &= check('FixF25 with a prefix -> YES', mem(read(repl(S, F25, '[1][00:00:00.001] ' + F25)), FM) is True)
ok &= check('FixF25 with CRLF -> YES', mem(read(repl(S, F25, F25 + '\r')), FM) is True)
t = copy.deepcopy(S)
t['lines'].remove(F25)
t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, F25)
ok &= check('FixF25 after the first GuestOut -> NO', mem(read(t), FM) is False)
t = copy.deepcopy(S)
t['lines'].insert(t['lines'].index(F25) + 1, 'FixF25: mode=0')
ok &= check('FixF25 second line mode=0 -> NO', mem(read(t), FM) is False)
t = copy.deepcopy(S)
t['lines'].insert(t['lines'].index(F25) + 1, 'FixF25: mode=x')
ok &= check('FixF25 good + unparsable -> NO', mem(read(t), FM) is False)
t = copy.deepcopy(S)
t['lines'].insert(4, 'FixF25: something else')
r = read(t)
ok &= check('other FixF25 line -> row, still ALL YES', r['ok'] is True and r['f25_rows']['f25_other'] == 1)

# --- F25 rows (not members) ---
t = copy.deepcopy(S)
for i in range(3):
    t['lines'].insert(-6, 'FixF25: read failed twice d=%d size=4096 pos=8192' % (5 + i))
t['lines'].insert(-6, 'KernelRead: direct read failed, dst=0x0000000200000000 size=0x1000')
t['stdout'] = 'x\nFixF25: read failed twice d=9 size=1 pos=2\nKernelRead: direct read failed, dst=0x1 size=0x1\nKernelRead: direct read failed, dst=0x2\n'
r = read(t)
fr = r['f25_rows']
ok &= check('F25 rows counted: log 3 / 1, stdout 1 / 2, members ALL YES',
            fr['read_failed_twice_log'] == 3 and fr['direct_read_failed_log'] == 1 and fr['read_failed_twice_stdout'] == 1
            and fr['direct_read_failed_stdout'] == 2 and r['ok'] is True and r['form_ok'] is True and r['status'] == 'ADMITTED')
ok &= check('F25 rows: read failed twice is not a mode line', fr['f25_mode_lines'] == 1 and fr['f25_unparsable'] == 0 and fr['f25_other'] == 0)
ok &= check('F25 first lines kept', (fr['read_failed_twice_first'] or '').startswith('FixF25: read failed twice d=5')
            and (fr['direct_read_failed_first'] or '').startswith('KernelRead: direct read failed'))
rows = '\n'.join(R.rows_out(r))
ok &= check('rows print the F25 row', 'ROW F25 (not a gate' in rows and 'read failed twice log 3, whole stdout 1' in rows
            and 'direct read failed log 1, whole stdout 2' in rows)
r = read(S)
rows = '\n'.join(R.rows_out(r))
ok &= check('clean rows print the F25 row with zeros', 'read failed twice log 0, whole stdout 0' in rows and 'ROW F25 first lines' not in rows)

# --- form fs12_v: FixF21, FixB12, exit members ---
ok &= check('FixF21 mode=0 -> form NO, letter YES', mem(read(repl(S, F21, 'FixF21: mode=0 wait_ms=12000')), 'FixF21: mode=1') is False
            and read(repl(S, F21, 'FixF21: mode=0 wait_ms=12000'))['ok'] is True)
ok &= check('FixF21 absent -> form NO', mem(read(repl(S, F21, None)), 'FixF21: mode=1') is False)
ok &= check('FixF21 no wait_ms -> form NO', mem(read(repl(S, F21, 'FixF21: mode=1')), 'FixF21: mode=1') is False)
t = copy.deepcopy(S)
t['lines'].remove(F21)
t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, F21)
ok &= check('FixF21 after the first GuestOut -> form NO', mem(read(t), 'FixF21: mode=1') is False)
r = read(repl(S, 'Event: quit', None))
ok &= check('no Event: quit -> quit NO and after-quit NO', mem(r, 'exit by the harness') is False and mem(r, 'after Event: quit') is False)
r = read(repl(S, 'Event: quit', 'x Event: quit y'))
ok &= check('Event: quit inside a line -> YES', mem(r, 'exit by the harness') is True)
r = read(after_quit(S, '--- Fatal Error ---'))
ok &= check('Fatal after quit -> after-quit NO, death NO', mem(r, 'after Event: quit') is False and mem(r, '0 death') is False
            and r['info']['fatal_after_quit'] == 1)
r = read(before_quit(S, '--- Fatal Error ---'))
ok &= check('Fatal before quit -> after-quit YES, death NO', mem(r, 'after Event: quit') is True and mem(r, '0 death') is False)
t = copy.deepcopy(S)
t['stdout'] = 'x\n--- Fatal Error ---\n'
r = read(t)
ok &= check('Fatal in stdout -> after-quit NO, death NO', mem(r, 'after Event: quit') is False and mem(r, '0 death') is False)
r = read(after_quit(S, 'FixF21: wait_expired tid=3 waited_ms=12012'))
ok &= check('wait_expired in log -> form NO', mem(r, '0 FixF21: wait_expired') is False)
t = copy.deepcopy(S)
t['stdout'] = 'FixF21: wait_expired tid=7 waited_ms=12001\n'
r = read(t)
ok &= check('wait_expired in stdout -> form NO, FixF21 mode YES', mem(r, '0 FixF21: wait_expired') is False and mem(r, 'FixF21: mode=') is True)
for key, val in (('close_killed', True), ('close_rc', None)):
    t = copy.deepcopy(S)
    t['run']['attempts'][0][key] = val
    r = read(t)
    ok &= check('%s=%s -> form end NO, letter YES' % (key, val), mem(r, 'the process ended before') is False and r['ok'] is True)
t = copy.deepcopy(S)
del t['run']['attempts'][0]['close_killed']
ok &= check('close_killed missing -> end NO', mem(read(t), 'the process ended before') is False)
t = copy.deepcopy(S)
t['run']['attempts'][0]['close_rc'] = 321
r = read(t)
ok &= check('exit code 321 -> row only, ALL YES', r['ok'] is True and r['form_ok'] is True and r['exit']['close_rc_hex'] == '0x00000141')
t = copy.deepcopy(S)
t['run']['attempts'][0]['close_rc'] = -1073741819
rows = '\n'.join(R.rows_out(read(t)))
ok &= check('rows carry the exit row', 'ROW exit (not a gate): exit code -1073741819 (0xc0000005' in rows and '4.1 s' in rows)
ok &= check('FixB12 mode=0 -> form NO', mem(read(repl(S, 'FixB12: mode=1', 'FixB12: mode=0')), 'FixB12: mode=1') is False)
t = copy.deepcopy(S)
t['lines'].remove('FixB12: mode=1')
t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, 'FixB12: mode=1')
ok &= check('FixB12 after the first GuestOut -> NO', mem(read(t), 'FixB12: mode=1') is False)
fw = 'LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0'
r = read(repl(S, 'LogAsync: full_waits=', fw.replace('drain_timeouts=0', 'drain_timeouts=3')))
ok &= check('drain_timeouts 3 -> form NO, letter YES', mem(r, 'drain_timeouts 0') is False and r['ok'] is True and r['form_ok'] is False)
ok &= check('FixB13 mode=0 -> NO', mem(read(repl(S, 'FixB13: mode=1', 'FixB13: mode=0')), 'FixB13') is False)
ok &= check('no FixB12Stat -> NO', mem(read(repl(S, 'FixB12Stat:', None, True)), 'FixB12Stat: line present') is False)
ok &= check('LogAsync mode=0 -> NO', mem(read(repl(S, 'LogAsync: mode=1', 'LogAsync: mode=0 requested=1 reason=direction')), 'LogAsync: mode=1') is False)

# --- letter members ---
t = copy.deepcopy(S)
t['lines'].insert(-4, 'FrameTrace: n=99999 dt_us=1000000 draws=300')
ok &= check('frame 1 000 000 -> NO', mem(read(t), '0 frames >= 1 s') is False)
t = copy.deepcopy(S)
t['lines'].insert(-4, 'FrameTrace: n=99999 dt_us=999999 draws=300')
ok &= check('frame 999 999 -> YES', mem(read(t), '0 frames >= 1 s') is True)
r = read(repl(S, 'FrameTrace: n=11 ', 'FrameTrace: n=11 dt_us=5000000 draws=300'))
ok &= check('the first scene frame itself >= 1 s -> YES, with it 1', mem(r, '0 frames >= 1 s') is True and r['info']['frames_ge1s_with_first'] == 1)
t = copy.deepcopy(S)
t['lines'] = [l.replace('draws=300', 'draws=99') for l in t['lines']]
r = read(t)
ok &= check('no first scene frame (draws 99) -> NO', mem(r, '0 frames >= 1 s') is False and mem(r, 'hold >= 300') is False)
t = copy.deepcopy(S)
t['lines'] = [l.replace('n=11 dt_us=16000 draws=300', 'n=11 dt_us=16000 draws=100') for l in t['lines']]
r = read(t)
ok &= check('draws 100 is the first scene frame (n 11)', r['info']['first_scene_n'] == 11)
t = copy.deepcopy(S)
t['lines'] = [l for l in t['lines'] if not (l.startswith('FrameTrace: n=') and int(l.split('=')[1].split()[0]) >= 17976)]
r = read(t)   # 17964 frames after n=11 x 16 700 = 299 998 800 us
ok &= check('hold 299.9988 s -> NO (%s)' % r['info']['hold_s'], mem(r, 'hold >= 300') is False)
t['lines'].insert(t['lines'].index('Event: quit'), 'FrameTrace: n=17976 dt_us=1200 draws=300')
r = read(t)
ok &= check('hold exactly 300 s -> YES (%s)' % r['info']['hold_s'], mem(r, 'hold >= 300') is True)
for n_idx, want in ((2999, False), (3000, True), (0, False)):
    t = copy.deepcopy(S)
    t['idx'] = n_idx
    ok &= check('video %d -> %s' % (n_idx, want), mem(read(t), 'video index') is want)
for gv in ('one-frame glitches: 1', None, 'no line here'):
    t = copy.deepcopy(S)
    if gv is None:
        del t['side']['glitch']
    else:
        t['side']['glitch'] = gv
    ok &= check('glitch %r -> NO' % gv, mem(read(t), '0 one-frame') is False)
t = copy.deepcopy(S)
del t['side']['sheet']
ok &= check('no sheet -> NO', mem(read(t), 'sheet') is False)
t = copy.deepcopy(S)
t['run']['attempts'][0]['hold_exit'] = 'died'
ok &= check('hold_exit -> NO', mem(read(t), 'the process lived') is False)
for dm in ('Unhandled exception: x', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort: x', 'ErrorDeviceLost'):
    ok &= check('death in log %s -> NO' % dm, mem(read(before_quit(S, dm)), '0 death') is False)
t = copy.deepcopy(S)
t['stdout'] = 'GpuHangAbort: x'
ok &= check('death stdout -> NO', mem(read(t), '0 death') is False)
t = copy.deepcopy(S)
t['lines'].insert(-4, '[Vulkan][E] VUID-x')
r = read(t)
ok &= check('[Vulkan][E] is a reference only', r['ok'] is True and r['form_ok'] is True and r['ref']['vke'] == 1)

# --- reference rows and the table ---
r = read(S)
ok &= check('bin version string row', r['ref']['bin_version_string'] is True)
ok &= check('fork row', (r['ref']['fork_line'] or '').endswith('531d648'))
ok &= check('FixB12Stat last row', r['ref']['b12stat_last']['passes'] == 5000 and r['ref']['b12stat_lines'] == 3)
rd = os.path.join(TMP, 'runs')
os.makedirs(os.path.join(rd, 'f25_v'))
json.dump(r, open(os.path.join(rd, 'f25_v', 'read.json'), 'w'), default=list)
os.makedirs(os.path.join(rd, 'fs12_v'))
json.dump(r, open(os.path.join(rd, 'fs12_v', 'read.json'), 'w'), default=list)
tb = R.table(rd)
ok &= check('table rows (only f25_v)', len(tb) == 3 and '| f25_v | ADMITTED | 5a14a111 | ALL YES | ALL YES | 0 / 0 | 0 / 0 | 0 | 4.1 |' in tb[2])

# --- strict cp1250 output (in-process), ASCII, json, usage ---
d = os.path.join(TMP, 'cp')
write(d, spec())
js = os.path.join(TMP, 'o.json')
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        rc_cp = R.main(['--dir', d, '--tag', TAG, '--json', js])
        R.main(['--table', '--runs', rd])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
    rc_cp = None
ok &= check('output in strict cp1250 without PYTHONIOENCODING, rc 0', cp_ok and rc_cp == 0 and len(raw.getvalue()) > 1000)
ok &= check('output ASCII only', all(c < 128 for c in raw.getvalue()))
ok &= check('json written and ASCII', os.path.exists(js) and all(c < 128 for c in open(js, 'rb').read()))
ok &= check('json carries the form, the exit row and the F25 rows', json.load(open(js)).get('form') == 'f25_v'
            and json.load(open(js))['exit']['close_rc'] == 0 and json.load(open(js))['f25_rows']['read_failed_twice_log'] == 0)
ok &= check('reader file ASCII', all(c < 128 for c in open(SRC, 'rb').read()))
for bad in ('fs12_v', 'f21_v', 'f25_w', 'f25_v_r4', 'f25_v_r0', ''):
    with contextlib.redirect_stdout(io.StringIO()):
        rc_u = R.main([bad])
    ok &= check('usage rc 2 for %r' % bad, rc_u == 2)
shutil.rmtree(TMP, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
