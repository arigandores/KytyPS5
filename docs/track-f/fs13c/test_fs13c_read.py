"""Fixtures of fs13c_read.py (Track F link FS13c, HPP-789; ROADMAP s122 item 697 (g)(3), item 699): clean synthetic tags fs13_v /
fs13_w / fs13_z read ADMITTED / ALL YES; every admission member (env per tag: no KYTY_FIX_* at fs13_v / fs13_w, KYTY_FIX_F25 '0' exactly at
fs13_z, no KYTY_TEST_* / KYTY_GAME_PATCH; KYTY_TEST_* key and 'ExitFatal:' lines in the log and in stdout) and every member of each form
flips the reading; edges (1 000 000 / 999 999, hold 300 s / 120 s, hold_s 310 / 309.9, video 2 999 / 3 000, draws 99 / 100, FixF25 mode=0
/ 1 / absent / after GuestOut / unparsable / second line, FixF21 at fs13_v / fs13_w and a row at fs13_z, Event: quit absent, '--- Fatal
Error ---' before / after quit and in stdout, wait_expired in log / stdout, close_killed / close_rc null; W: [Vulkan][E], limit line,
[Vulkan][W] 0, DualSrcBlend absent / 0 / after GuestOut, VALIDATION_STOP; Z: 'FixF25: read failed twice' in log / stdout); the F25 rows at
every tag; the exit rows; strict cp1250 output without PYTHONIOENCODING; the last line is ALL OK.  Port of
C:/kyty/f287/fs12c/test_fs12c_read.py (FS12c) with the F25 fixtures of C:/kyty/f287/f38c/test_f38c_read.py (F38c).  Early-exit form
(ok = True, ok &= ..., sys.exit(0 if ok else 1)).  ASCII only.
The reader is loaded in-process from argv[1] (default: fs13c_read.py beside this file); the fixture directories live under BASE.
usage: python test_fs13c_read.py [<fs13c_read.py under test>]"""
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fs13c_read.py')
BASE = Path(os.path.join(HERE, 'fx_fs13c'))
_spec = importlib.util.spec_from_file_location('fs13c_read_under_test', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_fs13c_read.py sha256 %s target fs13c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0, 0]
SEAL = b'seal fixture\n'
TB = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'   # literals, not the reader's constants
FS12 = '46892c20080819ae090598511748265dfbac31f303a02f1804e5b10db8acae26'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1919-gea6c6e9e'
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


def env_of(kind):
    e = dict(KYTY_GUEST_ARGS='-lvl ' + SKY, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE='C:/x/g', KYTY_SAMPLE_GATE='C:/x/s', KYTY_QUEUE_TRACE='1',
             KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8')
    if kind == 'w':
        e.update(VK_LAYER_PATH='C:/VulkanSDK/1.4.357.0/Bin', VK_LAYER_DUPLICATE_MESSAGE_LIMIT='100000000')
    else:
        e.update(KYTY_REC='C:/x/rec.mp4')
    if kind == 'z':
        e.update(KYTY_FIX_F25='0')
    return e


STAT = 'FixB12Stat: passes=%d rewalk=%d rwd=%d lskip=%d'
TAGS = {'v': 'fs13_v', 'w': 'fs13_w', 'z': 'fs13_z'}


def F21(kind):
    return 'FixF21: mode=1 wait_ms=12000'


def F25(kind):
    return 'FixF25: mode=%d' % (0 if kind == 'z' else 1)


def spec(kind):
    """The clean tag of the kind: a list of log lines and the side files."""
    L = ['LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100', 'Fork build arigandores/KytyPS5 ea6c6e9',
         F21(kind), F25(kind), 'ShaderSeed: compatibility=x:KytySC3:%s:y' % SIG, 'Shader translation cache: C:/e/_ShaderCache/PPSA21564/%s' % VARIANT_DIR,
         'FixB12: mode=1', 'FixB13: mode=1', 'DualSrcBlend: supported=1 enabled=1', 'GuestOut: Level has started: ',
         'GuestOut: Level has started: %s' % SKY, 'FrameTrace: n=10 dt_us=500000 draws=20', 'FrameTrace: n=11 dt_us=16000 draws=300']
    nfr = 20000 if kind == 'v' else (9000 if kind == 'z' else 2400)
    for i in range(nfr):
        L.append('FrameTrace: n=%d dt_us=%d draws=300' % (12 + i, 16700 if kind != 'w' else 130000))
        if kind != 'z' and i in (100, 900):
            L.append(STAT % (i, i // 2, 0, 1))
        if kind == 'w' and i % 100 == 0:
            L.append('[Vulkan][W] some warning %d' % i)
    if kind != 'z':
        L.append(STAT % (5000, 3000, 7, 2))
    L += ['Event: quit', 'shutdown line']
    L.append('LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0')
    cmd = ['emu', '--vulkan-validation', 'false', '--shader-validation', 'false']
    if kind == 'w':
        cmd += ['--vulkan-validation', 'true']
    hold = {'v': 330, 'w': 310, 'z': 150}[kind]
    att = dict(outcome='ok', hold_exit=None, hold_s=float(hold) + 0.2, stable_s=12.0, close_posted=5, close_rc=0, close_killed=False,
               close_s=4.1, close_wait_s=40)
    run = dict(binary_sha256=TB, env=env_of(kind), cmdline=cmd, attempts=[att], guest_args='-lvl ' + SKY, hold_s=hold,
               prereg=dict(sha256=hashlib.sha256(SEAL).hexdigest()))
    side = dict(installed_before=FS12, installed_after=FS12, installed_sha=TB, level=SKY, manifest_cmp='manifest cmp EQUAL files 5 listsha x')
    if kind != 'w':
        side.update(glitch='one-frame glitches: 0', sheet='sheet ok')
    return dict(lines=L, run=run, side=side, idx=(3200 if kind != 'w' else 0), stdout='stdout line\n')


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


def read(s, tag='fs13_v'):
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


SP = dict((k, spec(k)) for k in 'vwz')

# --- clean tags ---
for k in 'vwz':
    r = read(SP[k], TAGS[k])
    ok &= check('clean %s ADMITTED %s' % (k, [a for a, x in r['admission'] if not x]), r['status'] == 'ADMITTED')
    ok &= check('clean %s members ALL YES %s' % (k, [a for a, x in (r['members'] or []) if not x]), r['ok'] is True)
    want_form = None if k == 'z' else True
    ok &= check('clean %s form members %s' % (k, [a for a, x in (r['form_members'] or []) if not x]), r['form_ok'] is want_form)
    ok &= check('clean %s exit rows' % k, r['exit']['close_rc'] == 0 and r['exit']['close_s'] == 4.1 and r['exit']['close_rc_hex'] == '0x00000000')
    ok &= check('clean %s reading says no verdict, FS13d' % k, 'no verdict' in r['reading'] and 'FS13d' in r['reading'])
    ok &= check('clean %s F25 rows 0 / 0 / 0 / 0, mode lines 1' % k,
                r['f25_rows']['read_failed_twice_log'] == 0 and r['f25_rows']['read_failed_twice_stdout'] == 0
                and r['f25_rows']['direct_read_failed_log'] == 0 and r['f25_rows']['direct_read_failed_stdout'] == 0
                and r['f25_rows']['f25_mode_lines'] == 1)
    ok &= check('clean %s admission count 24 (%d)' % (k, len(r['admission'])), len(r['admission']) == 24)
r = read(SP['v'], 'fs13_v')
ok &= check('members count v 14 / 5 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 14 and len(r['form_members']) == 5)
ok &= check('v letter carries FixF25, FixF21, FixB12', all(any(a.startswith(w) for a, x in r['members']) for w in
                                                          ('FixF25: mode=1', 'FixF21: mode=1', 'FixB12: mode=1')))
r = read(SP['w'], 'fs13_w')
ok &= check('members count w 7 / 5 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 7 and len(r['form_members']) == 5)
ok &= check('w letter carries FixF25, form carries FixF21', any(a.startswith('FixF25: mode=1') for a, x in r['members'])
            and any(a.startswith('FixF21: mode=1') for a, x in r['form_members']) and not any(a.startswith('FixF21') for a, x in r['members']))
r = read(SP['z'], 'fs13_z')
ok &= check('members count z 5 / 0 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 5 and len(r['form_members']) == 0)
ok &= check('z letter carries FixF25 mode=0 and read failed twice, not FixF21', any(a.startswith('FixF25: mode=0') for a, x in r['members'])
            and any(a.startswith('0 FixF25: read failed twice') for a, x in r['members']) and not any(a.startswith('FixF21') for a, x in r['members'])
            and not any('wait_expired' in a for a, x in r['members']))
for tg in ('fs13_v_r1', 'fs13_w_r3', 'fs13_z_r2'):
    ok &= check('tag form %s' % tg, R.TAG_RX.match(tg) is not None)
# the tag form decides: a v spec read as z or w is not ALL YES / not admitted
ok &= check('v spec read as fs13_z -> NOT ADMITTED (env, hold option)', read(SP['v'], 'fs13_z')['status'] == 'NOT_ADMITTED')
ok &= check('z spec read as fs13_v -> NOT ADMITTED', read(SP['z'], 'fs13_v')['status'] == 'NOT_ADMITTED')

# --- admission members (each flips to NOT_ADMITTED), all three tags ---
for k in 'vwz':
    S = SP[k]
    T = TAGS[k]
    for key, val in (('installed_before', TB), ('installed_after', 'x'), ('installed_sha', FS12), ('level', 'pot'),
                     ('manifest_cmp', 'manifest cmp DIFFER only-before 1')):
        t = copy.deepcopy(S)
        t['side'][key] = val
        ok &= check('%s admission %s' % (k, key), read(t, T)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    del t['side']['manifest_cmp']
    ok &= check('%s admission no manifest_cmp file' % k, read(t, T)['status'] == 'NOT_ADMITTED')
    for key, val in (('binary_sha256', FS12), ('guest_args', '-lvl pot'), ('hold_s', 100)):
        t = copy.deepcopy(S)
        t['run'][key] = val
        ok &= check('%s admission run %s' % (k, key), read(t, T)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    t['run']['prereg']['sha256'] = 'x'
    ok &= check('%s admission prereg' % k, read(t, T)['status'] == 'NOT_ADMITTED')
    bads = [('KYTY_FIX_B12', '1'), ('KYTY_FIX_B36', '1'), ('KYTY_DIAG_B32', '1'), ('KYTY_GAME_PATCH', 'p'), ('KYTY_GPU_CHECKPOINTS', '1'),
            ('KYTY_S_REPLAY', '3')]
    bads += [('KYTY_FIX_F21', '0'), ('KYTY_FIX_F21', '1')]
    bads += [('KYTY_FIX_F25', '1')] if k == 'z' else [('KYTY_FIX_F25', '1'), ('KYTY_FIX_F25', '0'), ('KYTY_FIX_F25', '')]
    bads += [('VK_LAYER_PATH', 'x')] if k != 'w' else [('VK_LAYER_DUPLICATE_MESSAGE_LIMIT', '1000000'), ('VK_LAYER_MESSAGE_ID_FILTER', 'x'),
                                                        ('KYTY_REC', 'C:/x/r.mp4')]
    for kk, vv in bads:
        t = copy.deepcopy(S)
        t['run']['env'][kk] = vv
        r = read(t, T)
        ok &= check('%s admission env %s=%s' % (k, kk, vv), r['status'] == 'NOT_ADMITTED')
    # KYTY_TEST_* key - its own admission member fails (named)
    for kk in ('KYTY_TEST_EXITFATAL', 'KYTY_TEST_LOGSTALL', 'KYTY_TEST_MINIMIZE'):
        t = copy.deepcopy(S)
        t['run']['env'][kk] = 'P:1'
        r = read(t, T)
        own = [b for a, b in r['admission'] if a.startswith('no KYTY_TEST_*')]
        ok &= check('%s env %s -> NOT_ADMITTED by its own member' % (k, kk), r['status'] == 'NOT_ADMITTED' and own == [False])
    # ExitFatal: lines in the log or in stdout
    for where in ('log', 'stdout'):
        t = copy.deepcopy(S)
        if where == 'log':
            t['lines'].insert(4, 'ExitFatal: config arm=P seed=1')
        else:
            t['stdout'] = 'ExitFatal: config arm=P seed=1\n'
        r = read(t, T)
        own = [b for a, b in r['admission'] if a.startswith('0 ExitFatal:')]
        ok &= check('%s ExitFatal: in %s -> NOT_ADMITTED' % (k, where), r['status'] == 'NOT_ADMITTED' and own == [False])
    t = copy.deepcopy(S)
    t['lines'].insert(4, 'ExitFatal without colon')
    ok &= check('%s ExitFatal without colon -> ADMITTED' % k, read(t, T)['status'] == 'ADMITTED')
    must = ['KYTY_REC', 'KYTY_GPU_CLOCK_PIN', 'KYTY_GUEST_ARGS'] if k != 'w' else ['VK_LAYER_PATH', 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT', 'KYTY_GPU_CLOCK_PIN']
    if k == 'z':
        must.append('KYTY_FIX_F25')
    for k0 in must:
        t = copy.deepcopy(S)
        del t['run']['env'][k0]
        ok &= check('%s admission env missing %s' % (k, k0), read(t, T)['status'] == 'NOT_ADMITTED')
    flip = ['--vulkan-validation', 'false'] if k == 'w' else ['--vulkan-validation', 'true']
    for extra in (flip, ['--shader-validation', 'true'], ['--rd']):
        t = copy.deepcopy(S)
        t['run']['cmdline'] = t['run']['cmdline'] + extra
        ok &= check('%s admission cmdline %s' % (k, extra), read(t, T)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    t['run']['attempts'][0]['outcome'] = 'not_entered'
    ok &= check('%s admission outcome' % k, read(t, T)['status'] == 'NOT_ADMITTED')
    for extra in ('Window 1 minimized', 'Recovering Vulkan swapchain', 'GamePatch: loaded', 'DiagB32: mode=1',
                  'TestLogStall: config at_ms=1 sleep_ms=3000 k=3 gap_ms=5000 on=writer'):
        t = copy.deepcopy(S)
        t['lines'].insert(4, extra)
        ok &= check('%s admission line %s' % (k, extra), read(t, T)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    t['lines'].insert(4, 'Window 1 restored')
    ok &= check('%s restored is not interference' % k, read(t, T)['status'] == 'ADMITTED')
    ok &= check('%s admission signature' % k, read(repl(S, 'ShaderSeed:', 'ShaderSeed: compatibility=x:KytySC3:%s:y' % ('0' * 40)), T)['status'] == 'NOT_ADMITTED')
    ok &= check('%s admission catalog' % k, read(repl(S, 'Shader translation cache:', 'Shader translation cache: C:/e/variant_fixb26'), T)['status'] == 'NOT_ADMITTED')
    ok &= check('%s admission entry line' % k, read(repl(S, 'GuestOut: Level has started: %s' % SKY, None), T)['status'] == 'NOT_ADMITTED')
    r = read(repl(S, 'LogAsync: full_waits=', None), T)
    ok &= check('%s no summary -> NOT_ADMITTED run' % k, r['status'] == 'NOT_ADMITTED' and r['interference'].startswith('run'))
    t = copy.deepcopy(S)
    t['lines'].append([l for l in t['lines'] if l.startswith('LogAsync: full_waits=')][0])
    ok &= check('%s two summary lines -> NOT_ADMITTED' % k, read(t, T)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    t['stdout'] = None
    ok &= check('%s no stdout file -> NOT_ADMITTED' % k, read(t, T)['status'] == 'NOT_ADMITTED')
d = os.path.join(TMP, 'nolog')
write(d, copy.deepcopy(SP['v']))
os.remove(os.path.join(d, 'log.txt'))
r = R.read_tag('fs13_v', R.paths('fs13_v', d))
ok &= check('no log -> NOT_ADMITTED, no members', r['status'] == 'NOT_ADMITTED' and r['members'] is None)
os.remove(os.path.join(d, 'es.json'))
ok &= check('no json -> NOT_ADMITTED', R.read_tag('fs13_v', R.paths('fs13_v', d))['status'] == 'NOT_ADMITTED')

# --- FixF25 member, each tag (want 1 at v / w, 0 at z; letter of item 697 (g)(3)) ---
for k in 'vwz':
    S = SP[k]
    T = TAGS[k]
    want = 0 if k == 'z' else 1
    good = F25(k)
    FM = 'FixF25: mode=%d' % want
    other = 'FixF25: mode=%d' % (1 - want)
    r = read(repl(S, good, other), T)
    ok &= check('%s FixF25 opposite mode -> NO, letter NOT ALL YES' % k, mem(r, FM) is False and r['ok'] is False)
    ok &= check('%s FixF25 absent -> NO' % k, mem(read(repl(S, good, None), T), FM) is False)
    ok &= check('%s FixF25 mode=10 -> NO' % k, mem(read(repl(S, good, 'FixF25: mode=10'), T), FM) is False)
    ok &= check('%s FixF25 trailing garbage -> NO' % k, mem(read(repl(S, good, good + ' x'), T), FM) is False)
    ok &= check('%s FixF25 with a prefix -> YES' % k, mem(read(repl(S, good, '[1][00:00:00.001] ' + good), T), FM) is True)
    ok &= check('%s FixF25 with CR -> YES' % k, mem(read(repl(S, good, good + '\r'), T), FM) is True)
    t = copy.deepcopy(S)
    t['lines'].remove(good)
    t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, good)
    ok &= check('%s FixF25 after the first GuestOut -> NO' % k, mem(read(t, T), FM) is False)
    t = copy.deepcopy(S)
    t['lines'].insert(t['lines'].index(good) + 1, other)
    ok &= check('%s FixF25 second line opposite -> NO' % k, mem(read(t, T), FM) is False)
    t = copy.deepcopy(S)
    t['lines'].insert(t['lines'].index(good) + 1, 'FixF25: mode=x')
    ok &= check('%s FixF25 good + unparsable -> NO' % k, mem(read(t, T), FM) is False)
    t = copy.deepcopy(S)
    t['lines'].insert(4, 'FixF25: something else')
    r = read(t, T)
    ok &= check('%s other FixF25 line -> row, still ALL YES' % k, r['ok'] is True and r['f25_rows']['f25_other'] == 1)

# --- F25 rows at v / w (not members); the member 0 'read failed twice' at z ---
for k in 'vw':
    t = copy.deepcopy(SP[k])
    for i in range(3):
        t['lines'].insert(-6, 'FixF25: read failed twice d=%d size=4096 pos=8192' % (5 + i))
    t['lines'].insert(-6, 'KernelRead: direct read failed, dst=0x10 size=0x20')
    t['stdout'] = 'x\nFixF25: read failed twice d=9 size=1 pos=2\nKernelRead: direct read failed, dst=0x1 size=0x1\nKernelRead: direct read failed, dst=0x2\n'
    r = read(t, TAGS[k])
    fr = r['f25_rows']
    ok &= check('%s F25 rows counted: log 3 / 1, stdout 1 / 2, members ALL YES' % k,
                fr['read_failed_twice_log'] == 3 and fr['direct_read_failed_log'] == 1 and fr['read_failed_twice_stdout'] == 1
                and fr['direct_read_failed_stdout'] == 2 and r['ok'] is True and r['status'] == 'ADMITTED')
    ok &= check('%s F25 rows: read failed twice is not a mode line' % k, fr['f25_mode_lines'] == 1 and fr['f25_unparsable'] == 0 and fr['f25_other'] == 0)
    rows = '\n'.join(R.rows_out(r))
    ok &= check('%s rows carry the F25 row and the first lines' % k, 'ROW F25 (not a gate' in rows and 'ROW F25 first lines: FixF25: read failed twice d=5' in rows)
S = SP['z']
t = copy.deepcopy(S)
t['lines'].insert(-6, 'FixF25: read failed twice d=5 size=4096 pos=8192')
r = read(t, 'fs13_z')
ok &= check('z read failed twice in log -> NO, still a row', mem(r, '0 FixF25: read failed twice') is False and r['f25_rows']['read_failed_twice_log'] == 1)
t = copy.deepcopy(S)
t['stdout'] = 'FixF25: read failed twice d=9 size=1 pos=2\n'
r = read(t, 'fs13_z')
ok &= check('z read failed twice in stdout -> NO', mem(r, '0 FixF25: read failed twice') is False and r['f25_rows']['read_failed_twice_stdout'] == 1)
t = copy.deepcopy(S)
t['lines'].insert(-6, 'KernelRead: direct read failed, dst=0x10 size=0x20')
r = read(t, 'fs13_z')
ok &= check('z direct read failed -> row only, ALL YES', r['ok'] is True and r['f25_rows']['direct_read_failed_log'] == 1)
t = copy.deepcopy(S)
t['stdout'] = None
ok &= check('z no stdout -> NOT_ADMITTED (not a silent zero)', read(t, 'fs13_z')['status'] == 'NOT_ADMITTED')

# --- FixF21 member at v (letter) and w (form fs12_w); a row at z ---
for k in 'vw':
    S = SP[k]
    T = TAGS[k]
    want = 1
    good = F21(k)
    FM = 'FixF21: mode=%d' % want
    other = 'FixF21: mode=%d wait_ms=12000' % (1 - want)
    ok &= check('%s FixF21 opposite mode -> NO' % k, mem(read(repl(S, good, other), T), FM) is False)
    ok &= check('%s FixF21 absent -> NO' % k, mem(read(repl(S, good, None), T), FM) is False)
    ok &= check('%s FixF21 mode=10 -> NO' % k, mem(read(repl(S, good, 'FixF21: mode=10 wait_ms=12000'), T), FM) is False)
    ok &= check('%s FixF21 no wait_ms -> NO' % k, mem(read(repl(S, good, 'FixF21: mode=%d' % want), T), FM) is False)
    ok &= check('%s FixF21 trailing garbage -> NO' % k, mem(read(repl(S, good, good + ' x'), T), FM) is False)
    ok &= check('%s FixF21 with a prefix -> YES' % k, mem(read(repl(S, good, '[1][00:00:00.001] ' + good), T), FM) is True)
    t = copy.deepcopy(S)
    t['lines'].remove(good)
    t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, good)
    ok &= check('%s FixF21 after the first GuestOut -> NO' % k, mem(read(t, T), FM) is False)
    t = copy.deepcopy(S)
    t['lines'].insert(t['lines'].index(good) + 1, other)
    ok &= check('%s FixF21 second line opposite -> NO' % k, mem(read(t, T), FM) is False)
    t = copy.deepcopy(S)
    t['lines'].insert(t['lines'].index(good) + 1, 'FixF21: mode=%d wait_ms=x' % want)
    ok &= check('%s FixF21 good + unparsable -> NO' % k, mem(read(t, T), FM) is False)
    t = copy.deepcopy(S)
    t['lines'].insert(4, 'FixF21: something else')
    r = read(t, T)
    ok &= check('%s other FixF21 line -> reference row, still ALL YES' % k, r['ok'] is True and r['ref']['f21_other'] == 1)
r = read(repl(SP['w'], F21('w'), 'FixF21: mode=0 wait_ms=12000'), 'fs13_w')
ok &= check('w FixF21 mode=0 -> form NO, letter ALL YES', r['ok'] is True and r['form_ok'] is False)
for alt in ('FixF21: mode=0 wait_ms=12000', None):
    r = read(repl(SP['z'], F21('z'), alt), 'fs13_z')
    ok &= check('z FixF21 %r -> row only, ALL YES' % alt, r['ok'] is True and r['status'] == 'ADMITTED')

# --- exit members of fs13_v (form fs12_v / b4_v); rows at fs13_z / fs13_w ---
S = SP['v']
r = read(repl(S, 'Event: quit', None))
ok &= check('v no Event: quit -> quit NO and after-quit NO', mem(r, 'exit by the harness') is False and mem(r, 'after Event: quit') is False)
r = read(repl(S, 'Event: quit', 'x Event: quit y'))
ok &= check('v Event: quit inside a line -> YES', mem(r, 'exit by the harness') is True)
r = read(after_quit(S, '--- Fatal Error ---'))
ok &= check('v Fatal after quit -> after-quit NO, death NO', mem(r, 'after Event: quit') is False and mem(r, '0 death') is False
            and r['info']['fatal_after_quit'] == 1)
r = read(before_quit(S, '--- Fatal Error ---'))
ok &= check('v Fatal before quit -> after-quit YES, death NO', mem(r, 'after Event: quit') is True and mem(r, '0 death') is False)
t = copy.deepcopy(S)
t['stdout'] = 'x\n--- Fatal Error ---\n'
r = read(t)
ok &= check('v Fatal in stdout -> after-quit NO, death NO', mem(r, 'after Event: quit') is False and mem(r, '0 death') is False)
for k in 'v':
    T = TAGS[k]
    r = read(after_quit(SP[k], 'FixF21: wait_expired tid=3 waited_ms=12012'), T)
    ok &= check('%s wait_expired in log after quit -> NO' % k, mem(r, '0 FixF21: wait_expired') is False)
    r = read(before_quit(SP[k], 'FixF21: wait_expired tid=3 waited_ms=12012'), T)
    ok &= check('%s wait_expired in log before quit -> NO' % k, mem(r, '0 FixF21: wait_expired') is False)
    t = copy.deepcopy(SP[k])
    t['stdout'] = 'FixF21: wait_expired tid=7 waited_ms=12001\n'
    r = read(t, T)
    ok &= check('%s wait_expired in stdout -> NO, mode member YES' % k, mem(r, '0 FixF21: wait_expired') is False
                and mem(r, 'FixF21: mode=') is True)
r = read(SP['w'], 'fs13_w')
ok &= check('w has no wait_expired member (letter)', mem(r, '0 FixF21: wait_expired') is None)
t = copy.deepcopy(SP['z'])
t['stdout'] = 'FixF21: wait_expired tid=7 waited_ms=12001\n'
r = read(t, 'fs13_z')
ok &= check('z wait_expired -> no member, row in info, ALL YES', mem(r, '0 FixF21: wait_expired') is None and r['ok'] is True
            and r['info']['expired_stdout'] == 1)
for key, val in (('close_killed', True), ('close_rc', None)):
    t = copy.deepcopy(S)
    t['run']['attempts'][0][key] = val
    ok &= check('v %s=%s -> end NO' % (key, val), mem(read(t), 'the process ended before') is False)
    t = copy.deepcopy(SP['z'])
    t['run']['attempts'][0][key] = val
    r = read(t, 'fs13_z')
    ok &= check('z %s=%s -> row only, members ALL YES' % (key, val), r['ok'] is True)
t = copy.deepcopy(S)
del t['run']['attempts'][0]['close_killed']
ok &= check('v close_killed missing -> end NO', mem(read(t), 'the process ended before') is False)
r = read(repl(SP['z'], 'Event: quit', None), 'fs13_z')
ok &= check('z no Event: quit -> row only (quit_ln None), ALL YES', r['ok'] is True and r['exit']['quit_ln'] is None)
r = read(after_quit(SP['z'], '--- Fatal Error ---'), 'fs13_z')
ok &= check('z Fatal after quit -> death NO, row fatal_after_quit 1', mem(r, '0 death') is False and r['exit']['fatal_after_quit'] == 1)
t = copy.deepcopy(S)
t['run']['attempts'][0]['close_rc'] = 321
r = read(t)
ok &= check('v exit code 321 -> row only, members ALL YES', r['ok'] is True and r['exit']['close_rc_hex'] == '0x00000141')
t = copy.deepcopy(S)
t['run']['attempts'][0]['close_rc'] = -1073741819
r = read(t)
rows = '\n'.join(R.rows_out(r))
ok &= check('v rows carry the exit row', 'ROW exit (not a gate): exit code -1073741819 (0xc0000005' in rows and '4.1 s' in rows)

# --- members of fs13_v ---
t = copy.deepcopy(S)
t['lines'].insert(-4, 'FrameTrace: n=99999 dt_us=1000000 draws=300')
ok &= check('v frame 1 000 000 -> NO', mem(read(t), '0 frames >= 1 s') is False)
t = copy.deepcopy(S)
t['lines'].insert(-4, 'FrameTrace: n=99999 dt_us=999999 draws=300')
ok &= check('v frame 999 999 -> YES', mem(read(t), '0 frames >= 1 s') is True)
r = read(repl(S, 'FrameTrace: n=11 ', 'FrameTrace: n=11 dt_us=5000000 draws=300'))
ok &= check('v the first scene frame itself >= 1 s -> YES, with it 1', mem(r, '0 frames >= 1 s') is True and r['info']['frames_ge1s_with_first'] == 1)
t = copy.deepcopy(S)
t['lines'] = [l.replace('draws=300', 'draws=99') for l in t['lines']]
r = read(t)
ok &= check('v no first scene frame (draws 99) -> NO', mem(r, '0 frames >= 1 s') is False and mem(r, 'hold >= 300') is False)
t = copy.deepcopy(S)
t['lines'] = [l for l in t['lines'] if not (l.startswith('FrameTrace: n=') and int(l.split('=')[1].split()[0]) >= 17976)]
r = read(t)   # 17964 frames after n=11 x 16 700 = 299 998 800 us
ok &= check('v hold 299.9988 s -> NO (%s)' % r['info']['hold_s'], mem(r, 'hold >= 300') is False)
t['lines'].insert(t['lines'].index('Event: quit'), 'FrameTrace: n=17976 dt_us=1200 draws=300')
r = read(t)
ok &= check('v hold exactly 300 s -> YES (%s)' % r['info']['hold_s'], mem(r, 'hold >= 300') is True)
for n_idx, want in ((2999, False), (3000, True), (0, False)):
    t = copy.deepcopy(S)
    t['idx'] = n_idx
    ok &= check('v video %d -> %s' % (n_idx, want), mem(read(t), 'video index') is want)
for gv, want in (('one-frame glitches: 1', False), (None, False), ('no line here', False)):
    t = copy.deepcopy(S)
    if gv is None:
        del t['side']['glitch']
    else:
        t['side']['glitch'] = gv
    ok &= check('v glitch %r -> NO' % gv, mem(read(t), '0 one-frame') is want)
t = copy.deepcopy(S)
del t['side']['sheet']
ok &= check('v no sheet -> NO', mem(read(t), 'sheet') is False)
t = copy.deepcopy(S)
t['run']['attempts'][0]['hold_exit'] = 'died'
ok &= check('v hold_exit -> NO', mem(read(t), 'the process lived') is False)
for dm in ('Unhandled exception: x', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort: x', 'ErrorDeviceLost'):
    ok &= check('v death in log %s -> NO' % dm, mem(read(before_quit(S, dm)), '0 death') is False)
t = copy.deepcopy(S)
t['stdout'] = 'GpuHangAbort: x'
ok &= check('v death stdout -> NO', mem(read(t), '0 death') is False)
ok &= check('v FixB12 mode=0 -> NO (letter member)', mem(read(repl(S, 'FixB12: mode=1', 'FixB12: mode=0')), 'FixB12: mode=1') is False)
r = read(repl(S, 'FixB12: mode=1', None))
ok &= check('v FixB12 absent -> letter group NO', r['ok'] is False and mem(r, 'FixB12: mode=1') is False)
t = copy.deepcopy(S)
t['lines'].remove('FixB12: mode=1')
t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, 'FixB12: mode=1')
ok &= check('v FixB12 after the first GuestOut -> NO', mem(read(t), 'FixB12: mode=1') is False)
t = copy.deepcopy(S)
t['lines'].insert(-4, '[Vulkan][E] VUID-x')
r = read(t)
ok &= check('v [Vulkan][E] is a reference only', r['ok'] is True and r['form_ok'] is True and r['ref']['vke'] == 1)
# form fs12_v
fw = 'LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0'
r = read(repl(S, 'LogAsync: full_waits=', fw.replace('drain_timeouts=0', 'drain_timeouts=3')))
ok &= check('v drain_timeouts 3 -> form NO, letter YES', mem(r, 'drain_timeouts 0') is False and r['ok'] is True and r['form_ok'] is False)
ok &= check('v FixB13 mode=0 -> NO', mem(read(repl(S, 'FixB13: mode=1', 'FixB13: mode=0')), 'FixB13') is False)
ok &= check('v no FixB12Stat -> NO', mem(read(repl(S, 'FixB12Stat:', None, True)), 'FixB12Stat: line present') is False)
ok &= check('v LogAsync mode=0 -> NO', mem(read(repl(S, 'LogAsync: mode=1', 'LogAsync: mode=0 requested=1 reason=direction')), 'LogAsync: mode=1') is False)

# --- members of fs13_z ---
S = SP['z']
t = copy.deepcopy(S)
t['lines'] = [l for l in t['lines'] if not (l.startswith('FrameTrace: n=') and int(l.split('=')[1].split()[0]) >= 7198)]
r = read(t, 'fs13_z')   # 7186 frames x 16 700 = 120 006 200 us; 7185 = 119 989 500
ok &= check('z hold 120.006 s -> YES (%s)' % r['info']['hold_s'], mem(r, 'hold >= 120') is True)
t['lines'] = [l for l in t['lines'] if l != 'FrameTrace: n=7197 dt_us=16700 draws=300']
r = read(t, 'fs13_z')
ok &= check('z hold 119.99 s -> NO (%s)' % r['info']['hold_s'], mem(r, 'hold >= 120') is False)
t = copy.deepcopy(S)
t['run']['attempts'][0]['hold_exit'] = 'died'
ok &= check('z hold_exit -> NO', mem(read(t, 'fs13_z'), 'the process lived') is False)
ok &= check('z death in log -> NO', mem(read(before_quit(S, 'ErrorDeviceLost'), 'fs13_z'), '0 death') is False)
t = copy.deepcopy(S)
t['lines'].insert(-4, 'FrameTrace: n=99999 dt_us=2000000 draws=300')
ok &= check('z frame >= 1 s -> reference only', read(t, 'fs13_z')['ok'] is True)
t = copy.deepcopy(S)
t['idx'] = 10
ok &= check('z short video -> reference only', read(t, 'fs13_z')['ok'] is True)
ok &= check('z FixB12 mode=0 -> reference only', read(repl(S, 'FixB12: mode=1', 'FixB12: mode=0'), 'fs13_z')['ok'] is True)

# --- members of fs13_w ---
S = SP['w']
W = 'fs13_w'
t = copy.deepcopy(S)
t['lines'].insert(-4, '[Vulkan][E] VUID-x')
r = read(t, W)
ok &= check('w [Vulkan][E] -> NO, no VALIDATION_STOP while lived', mem(r, '0 [Vulkan][E]') is False and mem(r, 'no VALIDATION_STOP') is True)
t['run']['attempts'][0]['hold_exit'] = 'died'
r = read(t, W)
ok &= check('w [Vulkan][E] and died -> VALIDATION_STOP NO', mem(r, 'no VALIDATION_STOP') is False and mem(r, 'lived to the end') is False)
t = copy.deepcopy(S)
t['lines'].insert(-4, 'x this will be the last time reporting it')
ok &= check('w limit line -> NO', mem(read(t, W), '0 limit lines') is False)
r = read(repl(S, '[Vulkan][W]', None, True), W)
ok &= check('w [Vulkan][W] 0 -> NO', mem(r, 'positive control') is False)
ok &= check('w DualSrcBlend absent -> NO', mem(read(repl(S, 'DualSrcBlend:', None), W), 'DualSrcBlend') is False)
ok &= check('w DualSrcBlend enabled=0 -> NO', mem(read(repl(S, 'DualSrcBlend:', 'DualSrcBlend: supported=1 enabled=0'), W), 'DualSrcBlend') is False)
t = copy.deepcopy(S)
t['lines'].remove('DualSrcBlend: supported=1 enabled=1')
t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, 'DualSrcBlend: supported=1 enabled=1')
ok &= check('w DualSrcBlend after the first GuestOut -> NO', mem(read(t, W), 'DualSrcBlend') is False)
for hs, want in ((309.9, False), (310.0, True)):
    t = copy.deepcopy(S)
    t['run']['attempts'][0]['hold_s'] = hs
    ok &= check('w hold_s %s -> %s' % (hs, want), mem(read(t, W), 'lived to the end') is want)
ok &= check('w death in log -> NO', mem(read(before_quit(S, 'GpuHangAbort: x'), W), '0 death') is False)
ok &= check('w FixB13 absent -> form NO', mem(read(repl(S, 'FixB13: mode=1', None), W), 'FixB13') is False)
ok &= check('w FixB12 mode=0 -> form NO', mem(read(repl(S, 'FixB12: mode=1', 'FixB12: mode=0'), W), 'FixB12') is False)
ok &= check('w LogAsync mode absent -> form NO', mem(read(repl(S, 'LogAsync: mode=1', None), W), 'LogAsync: mode=1') is False)
t = copy.deepcopy(S)
t['run']['attempts'][0]['close_killed'] = True
ok &= check('w close_killed -> row only', read(t, W)['ok'] is True)

# --- reference rows and the table ---
r = read(SP['v'])
ok &= check('bin version string row', r['ref']['bin_version_string'] is True)
ok &= check('fork row', (r['ref']['fork_line'] or '').endswith('ea6c6e9'))
ok &= check('FixB12Stat last row', r['ref']['b12stat_last']['passes'] == 5000 and r['ref']['b12stat_lines'] == 3)
rd = os.path.join(TMP, 'runs')
os.makedirs(os.path.join(rd, 'fs13_v'))
json.dump(r, open(os.path.join(rd, 'fs13_v', 'read.json'), 'w'), default=list)
os.makedirs(os.path.join(rd, 'fs13_z'))
json.dump(read(SP['z'], 'fs13_z'), open(os.path.join(rd, 'fs13_z', 'read.json'), 'w'), default=list)
os.makedirs(os.path.join(rd, 'fs12_v'))
json.dump(r, open(os.path.join(rd, 'fs12_v', 'read.json'), 'w'), default=list)
tb = R.table(rd)
ok &= check('table rows (fs12_v dir ignored)', len(tb) == 4 and '| fs13_v | ADMITTED | abab2196 | ALL YES | ALL YES | 0 / 0 | 0 / 0 | 0 | 4.1 |' in tb[2]
            and '| fs13_z | ADMITTED | abab2196 | ALL YES | - | 0 / 0 | 0 / 0 | 0 | 4.1 |' in tb[3])

# --- strict cp1250 output (in-process), ASCII, json, usage ---
d = os.path.join(TMP, 'cp')
write(d, spec('v'))
js = os.path.join(TMP, 'o.json')
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        rc_cp = R.main(['--dir', d, '--tag', 'fs13_v', '--json', js])
        R.main(['--table', '--runs', rd])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
    rc_cp = None
ok &= check('output in strict cp1250 without PYTHONIOENCODING, rc 0', cp_ok and rc_cp == 0 and len(raw.getvalue()) > 1000)
ok &= check('output ASCII only', all(c < 128 for c in raw.getvalue()))
ok &= check('json written and ASCII', os.path.exists(js) and all(c < 128 for c in open(js, 'rb').read()))
ok &= check('json carries the form and the exit row', json.load(open(js)).get('form') == 'fs13_v' and json.load(open(js))['exit']['close_rc'] == 0)
ok &= check('reader file ASCII', all(c < 128 for c in open(SRC, 'rb').read()))
for bad in ('fs12_v', 'f25_v', 'fs13_x', 'fs13_v_r4', 'fs13_w_r0', ''):
    with contextlib.redirect_stdout(io.StringIO()):
        rc_u = R.main([bad])
    ok &= check('usage rc 2 for %r' % bad, rc_u == 2)
shutil.rmtree(TMP, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
