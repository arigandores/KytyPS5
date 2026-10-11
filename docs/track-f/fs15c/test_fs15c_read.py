"""Fixtures of fs15c_read.py (Track F link FS15c, HPP-822; ROADMAP s122 item 730 (g)(3), item 732, 733): clean synthetic tags fs15_v /
fs15_w / fs15_z read ADMITTED / ALL YES; every admission member (env per tag: no KYTY_FIX_* at fs15_v / fs15_w, KYTY_FIX_F20 '0' exactly
and no other KYTY_FIX_* at fs15_z, no KYTY_TEST_* / KYTY_GAME_PATCH; KYTY_TEST_* key, 'ExitFatal:' and 'TestHidLoss:' lines) and every
member of each form flips the reading; the new members of item 730 (g)(3): FixF20: mode=<want> (opposite / absent / after GuestOut /
unparsable / second line / prefix / CR) at each tag; the FixF20Stat exit line after Event: quit (absent / before quit only / unparsable /
two lines - the last one / unmatched 1 / modules_bound != modules / rewritten 10 and 11) at fs15_v and fs15_w (rewritten only at fs15_v);
FixF20Stat: lines 0 at fs15_z (exit / periodic / unparsable each NO; other FixF20 lines - a row); the rows of the preparation screen,
'all pipelines created', the driver blob (cache_before.tsv / cache_after.tsv) and FixF20Stat (periodic, max unmatched) are not members;
the FS14c members kept (FixF24 / init / init_owner / FixF29 / FixF25 / FixF21 / FixB12 / FixB13 / LogAsync, edges 1 000 000 / 999 999,
hold 300 s / 120 s, hold_s 310 / 309.9, video 2 999 / 3 000, draws 99 / 100, Event: quit, '--- Fatal Error ---' before / after quit and
in stdout, wait_expired, pump_stop_expired, close_killed / close_rc; W: [Vulkan][E], limit line, [Vulkan][W] 0, DualSrcBlend,
VALIDATION_STOP); at fs15_z FixF24 / FixF29 / FixF25 / FixF21 / FixB12 are references; strict cp1250 output without PYTHONIOENCODING; the
last line is ALL OK.  Port of C:/kyty/f287/fs14c/test_fs14c_read.py (FS14c) by patch_test_fs15c.py.  Early-exit form (ok = True, ok &=
..., sys.exit(0 if ok else 1)).  ASCII only.  The reader is loaded in-process from argv[1] (default: fs15c_read.py beside this file); the
fixture directories live under BASE.
usage: python test_fs15c_read.py [<fs15c_read.py under test>]"""
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fs15c_read.py')
BASE = Path(os.path.join(HERE, 'fx_fs15c'))
_spec = importlib.util.spec_from_file_location('fs15c_read_under_test', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_fs15c_read.py sha256 %s target fs15c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0, 0]
SEAL = b'seal fixture\n'
TB = 'bfac84bea0eaec8bf3dae6ab5f67cd480f26921829f64f4a8b467bd50e922d8c'   # literals, not the reader's constants
INST = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1929-g6beb3b73'
EXIT20 = 'FixF20Stat: when=exit calls=79 modules_bound=22 modules=22 sites=79 rewritten=79 unmatched=0'
PREP = 'ShaderPreparation: startup wait finished in 2299 ms presents_other=0 presents_main=0'
ALLP = 'PipelinePrecache: all pipelines created, 11190 ms'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
INIT = 'FixF24: init tid=41124 pump tid=41124 main tid=52836'
OWNER = 'FixF24: init_owner hid=41124 helper=41124 msg=41124 pump=41124 main=52836'
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
        e.update(KYTY_FIX_F20='0')
    return e


STAT = 'FixB12Stat: passes=%d rewalk=%d rwd=%d lskip=%d'
TAGS = {'v': 'fs15_v', 'w': 'fs15_w', 'z': 'fs15_z'}


def F21(kind):
    return 'FixF21: mode=1 wait_ms=12000'


def F25(kind):
    return 'FixF25: mode=1'


def F24(kind):
    return 'FixF24: mode=1 b24=1'


def F29(kind):
    return 'FixF29: mode=1'


def F20(kind):
    return 'FixF20: mode=%d' % (0 if kind == 'z' else 1)


def spec(kind):
    """The clean tag of the kind: a list of log lines and the side files."""
    L = ['LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100', 'Fork build arigandores/KytyPS5 6beb3b7',
         F21(kind), F25(kind), F24(kind), INIT, OWNER, F20(kind), 'PipelinePrecache: start recipes=3079', ALLP, PREP]
    L += [F29(kind), 'ShaderSeed: compatibility=x:KytySC3:%s:y' % SIG, 'Shader translation cache: C:/e/_ShaderCache/PPSA21564/%s' % VARIANT_DIR,
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
    L += ['Event: quit'] + ([EXIT20] if kind != 'z' else []) + ['shutdown line']
    L.append('LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0')
    cmd = ['emu', '--vulkan-validation', 'false', '--shader-validation', 'false']
    if kind == 'w':
        cmd += ['--vulkan-validation', 'true']
    hold = {'v': 330, 'w': 310, 'z': 150}[kind]
    att = dict(outcome='ok', hold_exit=None, hold_s=float(hold) + 0.2, stable_s=12.0, close_posted=5, close_rc=0, close_killed=False,
               close_s=4.1, close_wait_s=40)
    run = dict(binary_sha256=TB, env=env_of(kind), cmdline=cmd, attempts=[att], guest_args='-lvl ' + SKY, hold_s=hold,
               prereg=dict(sha256=hashlib.sha256(SEAL).hexdigest()))
    side = dict(installed_before=INST, installed_after=INST, installed_sha=TB, level=SKY, manifest_cmp='manifest cmp EQUAL files 5 listsha x')
    if kind != 'w':
        side.update(glitch='one-frame glitches: 0', sheet='sheet ok')
    tsv = dict(cache_before='_PipelineCache\tblob.bin\t1000\tx\nGLCache\ta.bin\t50\ty\n_ShaderCache\tb.bin\t7\tz\n',
               cache_after='_PipelineCache\tblob.bin\t8800\tx\nGLCache\ta.bin\t60\ty\n_ShaderCache\tb.bin\t7\tz\n')
    return dict(lines=L, run=run, side=side, idx=(3200 if kind != 'w' else 0), stdout='stdout line\n', tsv=tsv)


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
    for k, v in (s.get('tsv') or {}).items():
        with open(os.path.join(d, k + '.tsv'), 'w', newline='\n') as f:
            f.write(v)
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


def read(s, tag='fs15_v'):
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


def in_form(r, start):
    return any(a.startswith(start) for a, b in (r['form_members'] or []))


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


def ins_after(s, anchor, line):
    s = copy.deepcopy(s)
    s['lines'].insert(s['lines'].index(anchor) + 1, line)
    return s


def move_after_guest(s, line):
    s = copy.deepcopy(s)
    s['lines'].remove(line)
    s['lines'].insert(s['lines'].index('GuestOut: Level has started: ') + 1, line)
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
    ok &= check('clean %s reading says no verdict, FS15d' % k, 'no verdict' in r['reading'] and 'FS15d' in r['reading'])
    ok &= check('clean %s F25 rows 0 / 0 / 0 / 0, mode lines 1' % k,
                r['f25_rows']['read_failed_twice_log'] == 0 and r['f25_rows']['read_failed_twice_stdout'] == 0
                and r['f25_rows']['direct_read_failed_log'] == 0 and r['f25_rows']['direct_read_failed_stdout'] == 0
                and r['f25_rows']['f25_mode_lines'] == 1)
    ok &= check('clean %s F24 rows 0 / 0 / 0, pump expired 0 / 0' % k,
                r['f24_rows']['pump_update_long'] == 0 and r['f24_rows']['open_failed'] == 0 and r['f24_rows']['controller_lines'] == 0
                and r['f24_rows']['pump_stop_expired_log'] == 0 and r['f24_rows']['pump_stop_expired_stdout'] == 0)
    ok &= check('clean %s F29 rows 0 / 0 / 0 / 0, mode lines [want]' % k,
                r['f29_rows']['overflow_log'] == 0 and r['f29_rows']['overflow_stdout'] == 0 and r['f29_rows']['accessed_log'] == 0
                and r['f29_rows']['accessed_stdout'] == 0 and r['f29_rows']['f29_mode_lines'] == [1])
    f2 = r['f20_rows']
    ok &= check('clean %s F20 rows: prep [2299], all pipelines created [11190], blob 1000 -> 8800, GLCache 50 -> 60, mode lines [want]' % k,
                f2['prep_ms'] == [2299] and f2['all_pipelines_created_ms'] == [11190] and f2['blob_pipelinecache_before'] == 1000
                and f2['blob_pipelinecache_after'] == 8800 and f2['glcache_before'] == 50 and f2['glcache_after'] == 60
                and f2['f20_mode_lines'] == [0 if k == 'z' else 1] and f2['precache_n'] == 2)
    ok &= check('clean %s FixF20Stat rows: lines %s, exit %s' % (k, f2['f20stat_lines'], f2['f20stat_exit']),
                (f2['f20stat_lines'] == 0 and f2['f20stat_exit'] is None) if k == 'z' else
                (f2['f20stat_lines'] == 1 and f2['f20stat_exit']['rewritten'] == 79 and f2['f20stat_max_unmatched'] == 0))
    ok &= check('clean %s admission count 25 (%d)' % (k, len(r['admission'])), len(r['admission']) == 25)
r = read(SP['v'], 'fs15_v')
ok &= check('members count v 25 / 5 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 25 and len(r['form_members']) == 5)
ok &= check('v letter carries FixF20 mode=1 and the four FixF20Stat exit members',
            all(in_letter(r, w) for w in ('FixF20: mode=1', 'FixF20Stat: when=exit line after Event: quit', 'FixF20Stat exit line: unmatched 0',
                                         'FixF20Stat exit line: modules_bound = modules', 'FixF20Stat exit line: rewritten >= 11')))
ok &= check('v letter carries FixF24 mode=1, init, init_owner x2, FixF25, FixF21, FixB12, FixF29, pump_stop_expired',
            all(in_letter(r, w) for w in ('FixF24: mode=1 b24=1', 'FixF24: init before', 'FixF24: init_owner exactly 1', 'FixF24: init_owner hid =',
                                         'FixF25: mode=1', 'FixF21: mode=1', 'FixB12: mode=1', 'FixF29: mode=1', '0 FixF24: pump_stop_expired')))
ok &= check('v init_owner row', r['f24_rows']['init_owner']['hid'] == 41124 and r['f24_rows']['init_owner']['main'] == 52836)
r = read(SP['w'], 'fs15_w')
ok &= check('members count w 11 / 7 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 11 and len(r['form_members']) == 7)
ok &= check('w letter carries FixF20, FixF24 and three FixF20Stat exit members (no rewritten); form carries FixF29, FixF25, FixF21',
            in_letter(r, 'FixF20: mode=1') and in_letter(r, 'FixF24: mode=1 b24=1') and in_letter(r, 'FixF20Stat: when=exit line after')
            and in_letter(r, 'FixF20Stat exit line: unmatched 0') and in_letter(r, 'FixF20Stat exit line: modules_bound = modules')
            and not in_letter(r, 'FixF20Stat exit line: rewritten') and in_form(r, 'FixF29: mode=1') and in_form(r, 'FixF25: mode=1')
            and in_form(r, 'FixF21: mode=1') and not in_letter(r, 'FixF21') and not in_letter(r, 'FixF25') and not in_letter(r, 'FixF29'))
r = read(SP['z'], 'fs15_z')
ok &= check('members count z 5 / 0 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 5 and len(r['form_members']) == 0)
ok &= check('z letter carries FixF20 mode=0 and FixF20Stat lines 0; not FixF24 / FixF29 / FixF25 / FixF21',
            in_letter(r, 'FixF20: mode=0') and in_letter(r, '0 FixF20Stat: lines') and not in_letter(r, 'FixF24')
            and not in_letter(r, 'FixF29') and not in_letter(r, 'FixF25') and not in_letter(r, 'FixF21')
            and not any('wait_expired' in a for a, x in r['members']))
for tg in ('fs15_v_r1', 'fs15_w_r3', 'fs15_z_r2'):
    ok &= check('tag form %s' % tg, R.TAG_RX.match(tg) is not None)
ok &= check('v spec read as fs15_z -> NOT ADMITTED (env, hold option)', read(SP['v'], 'fs15_z')['status'] == 'NOT_ADMITTED')
ok &= check('z spec read as fs15_v -> NOT ADMITTED', read(SP['z'], 'fs15_v')['status'] == 'NOT_ADMITTED')

# --- admission members (each flips to NOT_ADMITTED), all three tags ---
for k in 'vwz':
    S = SP[k]
    T = TAGS[k]
    for key, val in (('installed_before', TB), ('installed_after', 'x'), ('installed_sha', INST), ('level', 'pot'),
                     ('manifest_cmp', 'manifest cmp DIFFER only-before 1')):
        t = copy.deepcopy(S)
        t['side'][key] = val
        ok &= check('%s admission %s' % (k, key), read(t, T)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    del t['side']['manifest_cmp']
    ok &= check('%s admission no manifest_cmp file' % k, read(t, T)['status'] == 'NOT_ADMITTED')
    for key, val in (('binary_sha256', INST), ('guest_args', '-lvl pot'), ('hold_s', 100)):
        t = copy.deepcopy(S)
        t['run'][key] = val
        ok &= check('%s admission run %s' % (k, key), read(t, T)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    t['run']['prereg']['sha256'] = 'x'
    ok &= check('%s admission prereg' % k, read(t, T)['status'] == 'NOT_ADMITTED')
    bads = [('KYTY_FIX_B12', '1'), ('KYTY_FIX_B36', '1'), ('KYTY_DIAG_B32', '1'), ('KYTY_GAME_PATCH', 'p'), ('KYTY_GPU_CHECKPOINTS', '1'),
            ('KYTY_S_REPLAY', '3'), ('KYTY_FIX_F21', '0'), ('KYTY_FIX_F21', '1'), ('KYTY_FIX_F25', '0'), ('KYTY_FIX_F25', '1')]
    bads += [('KYTY_FIX_F24', '1'), ('KYTY_FIX_F24', '0'), ('KYTY_FIX_F24', ''), ('KYTY_FIX_F29', '1'), ('KYTY_FIX_F29', '0'),
             ('KYTY_FIX_F29', '')]
    if k == 'z':
        bads += [('KYTY_FIX_F20', '1'), ('KYTY_FIX_F20', '')]
    else:
        bads += [('KYTY_FIX_F20', '1'), ('KYTY_FIX_F20', '0'), ('KYTY_FIX_F20', '')]
    bads += [('VK_LAYER_PATH', 'x')] if k != 'w' else [('VK_LAYER_DUPLICATE_MESSAGE_LIMIT', '1000000'), ('VK_LAYER_MESSAGE_ID_FILTER', 'x'),
                                                        ('KYTY_REC', 'C:/x/r.mp4')]
    for kk, vv in bads:
        t = copy.deepcopy(S)
        t['run']['env'][kk] = vv
        r = read(t, T)
        ok &= check('%s admission env %s=%s' % (k, kk, vv), r['status'] == 'NOT_ADMITTED')
    for kk in ('KYTY_TEST_EXITFATAL', 'KYTY_TEST_HIDLOSS', 'KYTY_TEST_MINIMIZE'):
        t = copy.deepcopy(S)
        t['run']['env'][kk] = 'P:1'
        r = read(t, T)
        own = [b for a, b in r['admission'] if a.startswith('no KYTY_TEST_*')]
        ok &= check('%s env %s -> NOT_ADMITTED by its own member' % (k, kk), r['status'] == 'NOT_ADMITTED' and own == [False])
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
    t = copy.deepcopy(S)
    t['lines'].insert(4, '[3][00:00:01.000] TestHidLoss: config off')
    r = read(t, T)
    own = [b for a, b in r['admission'] if a.startswith('no TestHidLoss line')]
    ok &= check('%s TestHidLoss: line -> NOT_ADMITTED by its own member' % k, r['status'] == 'NOT_ADMITTED' and own == [False])
    must = ['KYTY_REC', 'KYTY_GPU_CLOCK_PIN', 'KYTY_GUEST_ARGS'] if k != 'w' else ['VK_LAYER_PATH', 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT', 'KYTY_GPU_CLOCK_PIN']
    if k == 'z':
        must += ['KYTY_FIX_F20']
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
r = R.read_tag('fs15_v', R.paths('fs15_v', d))
ok &= check('no log -> NOT_ADMITTED, no members', r['status'] == 'NOT_ADMITTED' and r['members'] is None)
os.remove(os.path.join(d, 'es.json'))
ok &= check('no json -> NOT_ADMITTED', R.read_tag('fs15_v', R.paths('fs15_v', d))['status'] == 'NOT_ADMITTED')


# --- a mode member, generic: (kinds, line of the clean spec, member text start, opposite line, broken lines, letter?) ---
def mode_suite(name, kinds, good_of, fm_of, other_of, broken_of, letter_of):
    global ok
    for k in kinds:
        S = SP[k]
        T = TAGS[k]
        good = good_of(k)
        FM = fm_of(k)
        lt = letter_of(k)
        r = read(repl(S, good, other_of(k)), T)
        ok &= check('%s %s opposite -> NO, %s NOT ALL YES' % (k, name, 'letter' if lt else 'form'),
                    mem(r, FM) is False and (r['ok'] if lt else r['form_ok']) is False and r['status'] == 'ADMITTED')
        if lt:
            ok &= check('%s %s opposite: form unchanged' % (k, name), r['form_ok'] is (None if k == 'z' else True))
        else:
            ok &= check('%s %s opposite: letter unchanged' % (k, name), r['ok'] is True)
        ok &= check('%s %s absent -> NO' % (k, name), mem(read(repl(S, good, None), T), FM) is False)
        for b in broken_of(k):
            ok &= check('%s %s broken %r -> NO' % (k, name, b), mem(read(repl(S, good, b), T), FM) is False)
        ok &= check('%s %s trailing garbage -> NO' % (k, name), mem(read(repl(S, good, good + ' x'), T), FM) is False)
        ok &= check('%s %s with a prefix -> YES' % (k, name), mem(read(repl(S, good, '[1][00:00:00.001] ' + good), T), FM) is True)
        ok &= check('%s %s with CR -> YES' % (k, name), mem(read(repl(S, good, good + '\r'), T), FM) is True)
        ok &= check('%s %s after the first GuestOut -> NO' % (k, name), mem(read(move_after_guest(S, good), T), FM) is False)
        ok &= check('%s %s second line opposite -> NO' % (k, name), mem(read(ins_after(S, good, other_of(k)), T), FM) is False)
        ok &= check('%s %s second line same -> YES' % (k, name), mem(read(ins_after(S, good, good), T), FM) is True)
        if broken_of(k):
            ok &= check('%s %s good + unparsable -> NO' % (k, name), mem(read(ins_after(S, good, broken_of(k)[0]), T), FM) is False)


mode_suite('FixF20', 'vwz', F20, lambda k: 'FixF20: mode=%d' % (0 if k == 'z' else 1), lambda k: 'FixF20: mode=%d' % (1 if k == 'z' else 0),
           lambda k: ['FixF20: mode=10', 'FixF20: mode=x'], lambda k: True)
mode_suite('FixF24', 'vw', F24, lambda k: 'FixF24: mode=1 b24=1', lambda k: 'FixF24: mode=0 b24=1',
           lambda k: ['FixF24: mode=1 b24=0', 'FixF24: mode=1', 'FixF24: mode=10 b24=1', 'FixF24: mode=x b24=1'],
           lambda k: True)
mode_suite('FixF29', 'vw', F29, lambda k: 'FixF29: mode=1', lambda k: 'FixF29: mode=0',
           lambda k: ['FixF29: mode=10', 'FixF29: mode=x'], lambda k: k == 'v')
mode_suite('FixF25', 'vw', F25, lambda k: 'FixF25: mode=1', lambda k: 'FixF25: mode=0', lambda k: ['FixF25: mode=10', 'FixF25: mode=x'],
           lambda k: k == 'v')
mode_suite('FixF21', 'vw', F21, lambda k: 'FixF21: mode=1', lambda k: 'FixF21: mode=0 wait_ms=12000',
           lambda k: ['FixF21: mode=1', 'FixF21: mode=10 wait_ms=12000', 'FixF21: mode=1 wait_ms=x'], lambda k: k == 'v')

# FixF24 / FixF29 / FixF25 / FixF21 at z are reference only
for line, alts in ((F24('z'), ('FixF24: mode=0 b24=1', None, 'FixF24: mode=x b24=1')), (F29('z'), ('FixF29: mode=0', None, 'FixF29: mode=x'))):
    for alt in alts:
        r = read(repl(SP['z'], line, alt), 'fs15_z')
        ok &= check('z %r -> reference only, ALL YES' % alt, r['ok'] is True and r['status'] == 'ADMITTED')
for alt in ('FixF25: mode=0', None, 'FixF25: mode=x'):
    r = read(repl(SP['z'], F25('z'), alt), 'fs15_z')
    ok &= check('z FixF25 %r -> reference only, ALL YES' % alt, r['ok'] is True and r['status'] == 'ADMITTED')
for alt in ('FixF21: mode=0 wait_ms=12000', None):
    r = read(repl(SP['z'], F21('z'), alt), 'fs15_z')
    ok &= check('z FixF21 %r -> row only, ALL YES' % alt, r['ok'] is True and r['status'] == 'ADMITTED')
# other FixF29 line at v / w -> row (f29_other), members ALL YES
for k in 'vw':
    r = read(ins_after(SP[k], F29(k), 'FixF29: something else'), TAGS[k])
    ok &= check('%s other FixF29 line -> row, ALL YES' % k, r['ok'] is True and r['f29_rows']['f29_other'] == 1)
    r = read(ins_after(SP[k], F25(k), 'FixF25: something else'), TAGS[k])
    ok &= check('%s other FixF25 line -> row, ALL YES' % k, r['ok'] is True and r['f25_rows']['f25_other'] == 1)

# --- FixF24: init and init_owner at fs14_v ---
S = SP['v']
FI = 'FixF24: init before'
FO = 'FixF24: init_owner exactly 1'
FS = 'FixF24: init_owner hid ='
ok &= check('v init absent -> NO', mem(read(repl(S, INIT, None)), FI) is False)
ok &= check('v init after the first GuestOut -> NO', mem(read(move_after_guest(S, INIT)), FI) is False)
ok &= check('v init with a prefix -> YES', mem(read(repl(S, INIT, '[1][00:00:00.001] ' + INIT)), FI) is True)
r = read(repl(S, OWNER, None))
ok &= check('v init_owner absent -> alive NO, same NO', mem(r, FO) is False and mem(r, FS) is False)
for line, alive, same in (('FixF24: init_owner hid=0 helper=41124 msg=41124 pump=41124 main=52836', False, False),
                          ('FixF24: init_owner hid=41124 helper=0 msg=41124 pump=41124 main=52836', False, False),
                          ('FixF24: init_owner hid=52836 helper=52836 msg=52836 pump=52836 main=52836', True, False),
                          ('FixF24: init_owner hid=41124 helper=52836 msg=41124 pump=41124 main=52836', True, False),
                          ('FixF24: init_owner hid=41124 helper=41124 msg=41124 pump=7 main=52836', True, False),
                          ('FixF24: init_owner hid=41124 helper=41124 msg=99 pump=41124 main=52836', True, True),
                          ('FixF24: init_owner hid=41124 helper=41124 msg=41124 pump=41124 main=52836 x', False, False),
                          ('FixF24: init_owner hid=41124 helper=41124 pump=41124 main=52836', False, False)):
    r = read(repl(S, OWNER, line))
    ok &= check('v init_owner %r -> alive %s same %s' % (line[25:], alive, same), mem(r, FO) is alive and mem(r, FS) is same)
r = read(ins_after(S, OWNER, OWNER))
ok &= check('v two init_owner lines -> NO (exactly 1)', mem(r, FO) is False and mem(r, FS) is False)
r = read(ins_after(S, OWNER, 'FixF24: init_owner hid=x'))
ok &= check('v init_owner + unparsable -> NO', mem(r, FO) is False and mem(r, FS) is False)
r = read(move_after_guest(S, OWNER))
ok &= check('v init_owner after the first GuestOut -> NO (letter: before the first GuestOut)', mem(r, FO) is False and mem(r, FS) is False)
# pump_stop_expired at v (letter), rows elsewhere
PX = 'FixF24: pump_stop_expired t_jp_ms=2000'
r = read(after_quit(S, PX))
ok &= check('v pump_stop_expired in log -> NO', mem(r, '0 FixF24: pump_stop_expired') is False and r['f24_rows']['pump_stop_expired_log'] == 1)
t = copy.deepcopy(S)
t['stdout'] = 'x\n' + PX + '\n'
r = read(t)
ok &= check('v pump_stop_expired in stdout -> NO', mem(r, '0 FixF24: pump_stop_expired') is False and r['f24_rows']['pump_stop_expired_stdout'] == 1)
r = read(after_quit(SP['w'], PX), 'fs15_w')
ok &= check('w pump_stop_expired -> row only, ALL YES', r['ok'] is True and r['form_ok'] is True and mem(r, '0 FixF24: pump') is None)

# --- FixF20Stat lines at fs15_z (each kind) -> NO; other FixF24 / FixF29 / FixF20 lines at fs15_z -> rows only ---
Z = SP['z']
for line, where in ((EXIT20, 'after'), (EXIT20, 'before'), ('FixF20Stat: when=periodic calls=4096 modules_bound=9 modules=9 sites=9 '
                                                            'rewritten=9 unmatched=0', 'before'),
                    ('FixF20Stat: when=exit calls=x', 'after'), ('FixF20Stat:', 'after')):
    r = read((after_quit if where == 'after' else before_quit)(Z, line), 'fs15_z')
    ok &= check('z %r %s quit -> FixF20Stat lines 0 NO' % (line[:34], where), mem(r, '0 FixF20Stat: lines') is False and r['ok'] is False)
for line in (PX, 'FixF24: pump_update_long us=250000', 'FixF24: open failed instance=3 error="x"', 'FixF24: anything',
             'FixF29: overflow pass=1 area=0 count=1100 read=1023 total=1', 'FixF29: anything', 'FixF20: anything else',
             'FixF20 something'):
    r = read(before_quit(Z, line), 'fs15_z')
    ok &= check('z %r -> row only, ALL YES' % line[:30], r['ok'] is True and r['status'] == 'ADMITTED')
r = read(before_quit(Z, 'FixF20: anything else'), 'fs15_z')
ok &= check('z other FixF20 line -> row f20_other 1', r['f20_rows']['f20_other'] == 1)
r = read(before_quit(Z, 'Accessed non-GPU cached memory at 0x0000000000001000'), 'fs15_z')
ok &= check('z accessed line -> row only, ALL YES', r['ok'] is True and r['f29_rows']['accessed_log'] == 1)
for line in ('Controller 0: "Xbox Controller" type=1 accel=0 gyro=0 path=x', 'Controller added: 0, time = 1.0000'):
    r = read(before_quit(Z, line), 'fs15_z')
    ok &= check('z %r -> row only, ALL YES' % line[:20], r['ok'] is True and r['f24_rows']['controller_lines'] == 1)

# --- rows at v / w: pump_update_long, open failed, Controller, overflow, accessed (not members) ---
for k in 'vw':
    t = copy.deepcopy(SP[k])
    for line in ('FixF24: pump_update_long us=150000', 'FixF24: pump_update_long us=250000', 'FixF24: open failed instance=3 error="x"',
                 'Controller 0: "Xbox Controller" type=1 accel=0 gyro=0 path=x', 'Controller added: 0, time = 1.0000',
                 'Controller 0: removed', 'Controller removed: 0, time = 9.0000', 'Game Controller mapping x',
                 'FixF29: overflow pass=7 area=3 count=1100 read=1023 total=1',
                 'Accessed non-GPU cached memory at 0x0000000000001000', 'Accessed non-GPU cached memory at 0x0000000000002000',
                 'FixF24: add event index=0'):
        t['lines'].insert(-6, line)
    t['stdout'] = 'x\nFixF29: overflow pass=8 area=1 count=2000 read=1023 total=2\nAccessed non-GPU cached memory at 0x3\n'
    r = read(t, TAGS[k])
    f24 = r['f24_rows']
    f29 = r['f29_rows']
    ok &= check('%s rows: pump_update_long 2, open failed 1, Controller 4, add event 1; members ALL YES' % k,
                f24['pump_update_long'] == 2 and f24['open_failed'] == 1 and f24['controller_lines'] == 4 and f24['add_event'] == 1
                and r['ok'] is True and r['form_ok'] is True and r['status'] == 'ADMITTED')
    ok &= check('%s rows: overflow 1 / 1, accessed 2 / 1' % k, f29['overflow_log'] == 1 and f29['overflow_stdout'] == 1
                and f29['accessed_log'] == 2 and f29['accessed_stdout'] == 1 and f29['f29_mode_lines'] == [1] and f29['f29_other'] == 0)
    rows = '\n'.join(R.rows_out(r))
    ok &= check('%s rows printed (F24, F29, first lines, a reference not an interference)' % k,
                'ROW F24 (not a gate): FixF24: pump_update_long 2, FixF24: open failed 1, host pad lines Controller 4' in rows
                and 'not an interference' in rows and 'ROW F24 first Controller line: Controller 0: "Xbox' in rows
                and 'ROW F29 (not a gate; overflow > 0' in rows and 'ROW F29 first lines: FixF29: overflow pass=7' in rows)

# --- F25 rows at every tag (not members) ---
for k in 'vwz':
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
    rows = '\n'.join(R.rows_out(r))
    ok &= check('%s rows carry the F25 row and the first lines' % k, 'ROW F25 (not a gate' in rows and 'ROW F25 first lines: FixF25: read failed twice d=5' in rows)

# --- FixF20Stat exit members at fs15_v (4) and fs15_w (3) ---
for k in 'vw':
    S0 = SP[k]
    T0 = TAGS[k]
    FE = 'FixF20Stat: when=exit line after'
    r = read(repl(S0, EXIT20, None), T0)
    ok &= check('%s no exit line -> exit NO, unmatched NO, bound NO' % k, mem(r, FE) is False and mem(r, 'FixF20Stat exit line: unmatched') is False
                and mem(r, 'FixF20Stat exit line: modules_bound') is False and r['ok'] is False)
    if k == 'v':
        ok &= check('v no exit line -> rewritten NO', mem(r, 'FixF20Stat exit line: rewritten') is False)
    t = repl(S0, EXIT20, None)
    t = before_quit(t, EXIT20)
    r = read(t, T0)
    ok &= check('%s exit line only before Event: quit -> NO' % k, mem(r, FE) is False and r['ok'] is False)
    r = read(repl(S0, 'Event: quit', None), T0)
    ok &= check('%s no Event: quit -> exit line NO' % k, mem(r, FE) is False)
    for bad in ('FixF20Stat: when=exit calls=79 modules_bound=22 modules=22 sites=79 rewritten=79', EXIT20 + ' x',
                'FixF20Stat: when=exit calls=79 modules_bound=22 modules=22 sites=79 rewritten=x unmatched=0'):
        r = read(repl(S0, EXIT20, bad), T0)
        ok &= check('%s unparsable exit line %r -> NO, row unparsable 1' % (k, bad[-24:]), mem(r, FE) is False
                    and r['f20_rows']['f20stat_unparsable'] == 1)
    for alt, member, want in ((EXIT20.replace('unmatched=0', 'unmatched=1'), 'FixF20Stat exit line: unmatched', False),
                              (EXIT20.replace('modules_bound=22', 'modules_bound=21'), 'FixF20Stat exit line: modules_bound', False),
                              (EXIT20.replace('modules=22 ', 'modules=23 '), 'FixF20Stat exit line: modules_bound', False),
                              (EXIT20.replace('[', ''), FE, True)):
        r = read(repl(S0, EXIT20, alt), T0)
        ok &= check('%s exit line %r -> %s %s' % (k, alt[-46:], member, want), mem(r, member) is want and (r['ok'] is want))
    for rw, want in ((10, False), (11, True), (0, False)):
        r = read(repl(S0, EXIT20, EXIT20.replace('rewritten=79', 'rewritten=%d' % rw)), T0)
        if k == 'v':
            ok &= check('v rewritten %d -> %s' % (rw, want), mem(r, 'FixF20Stat exit line: rewritten') is want and r['ok'] is want)
        else:
            ok &= check('w rewritten %d -> no member, ALL YES' % rw, mem(r, 'FixF20Stat exit line: rewritten') is None and r['ok'] is True)
    t = copy.deepcopy(S0)
    t['lines'].insert(t['lines'].index('shutdown line'), EXIT20.replace('unmatched=0', 'unmatched=5'))
    r = read(t, T0)
    ok &= check('%s two exit lines after quit, the last unmatched 5 -> NO (the last governs)' % k,
                mem(r, 'FixF20Stat exit line: unmatched') is False)
    t = after_quit(S0, EXIT20.replace('unmatched=0', 'unmatched=5'))
    t['lines'].insert(t['lines'].index('shutdown line'), EXIT20)
    r = read(t, T0)
    ok &= check('%s two exit lines after quit, the last clean -> YES' % k, mem(r, 'FixF20Stat exit line: unmatched') is True and r['ok'] is True)
    r = read(before_quit(S0, 'FixF20Stat: when=periodic calls=4096 modules_bound=9 modules=10 sites=9 rewritten=9 unmatched=7'), T0)
    ok &= check('%s periodic line with unmatched 7 -> row only (max unmatched 7, periodic 1), ALL YES' % k,
                r['ok'] is True and r['f20_rows']['f20stat_max_unmatched'] == 7 and r['f20_rows']['f20stat_periodic'] == 1)
    r = read(before_quit(S0, 'FixF20: anything else'), T0)
    ok &= check('%s other FixF20 line -> row only, ALL YES' % k, r['ok'] is True and r['f20_rows']['f20_other'] == 1)
    rows = '\n'.join(R.rows_out(read(S0, T0)))
    ok &= check('%s rows printed: preparation screen, all pipelines created, blob, FixF20Stat' % k,
                'ROW preparation screen (not a gate): ShaderPreparation ms [2299]; PipelinePrecache: all pipelines created ms [11190]' in rows
                and 'ROW driver blob (not a gate): _PipelineCache bytes before 1000 after 8800' in rows
                and 'ROW FixF20Stat (not a gate beyond the members): lines 1' in rows and 'ROW PipelinePrecache (not a gate): 2 lines' in rows)
t = copy.deepcopy(SP['v'])
t['tsv'] = {}
r = read(t)
ok &= check('v no cache tsv -> blob rows None, ALL YES', r['ok'] is True and r['f20_rows']['blob_pipelinecache_before'] is None
            and r['f20_rows']['blob_pipelinecache_after'] is None)
r = read(repl(repl(SP['v'], PREP, None), ALLP, None))
ok &= check('v no preparation lines -> rows [] and [], ALL YES', r['ok'] is True and r['f20_rows']['prep_ms'] == []
            and r['f20_rows']['all_pipelines_created_ms'] == [])

# --- exit members of fs15_v (form fs14_v / b4_v); rows at fs15_z / fs15_w ---
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
r = read(after_quit(S, 'FixF21: wait_expired tid=3 waited_ms=12012'))
ok &= check('v wait_expired in log after quit -> NO', mem(r, '0 FixF21: wait_expired') is False)
r = read(before_quit(S, 'FixF21: wait_expired tid=3 waited_ms=12012'))
ok &= check('v wait_expired in log before quit -> NO', mem(r, '0 FixF21: wait_expired') is False)
t = copy.deepcopy(S)
t['stdout'] = 'FixF21: wait_expired tid=7 waited_ms=12001\n'
r = read(t)
ok &= check('v wait_expired in stdout -> NO, mode member YES', mem(r, '0 FixF21: wait_expired') is False and mem(r, 'FixF21: mode=') is True)
r = read(SP['w'], 'fs15_w')
ok &= check('w has no wait_expired member (letter)', mem(r, '0 FixF21: wait_expired') is None)
t = copy.deepcopy(SP['z'])
t['stdout'] = 'FixF21: wait_expired tid=7 waited_ms=12001\n'
r = read(t, 'fs15_z')
ok &= check('z wait_expired -> no member, row in info, ALL YES', mem(r, '0 FixF21: wait_expired') is None and r['ok'] is True
            and r['info']['expired_stdout'] == 1)
for key, val in (('close_killed', True), ('close_rc', None)):
    t = copy.deepcopy(S)
    t['run']['attempts'][0][key] = val
    ok &= check('v %s=%s -> end NO' % (key, val), mem(read(t), 'the process ended before') is False)
    t = copy.deepcopy(SP['z'])
    t['run']['attempts'][0][key] = val
    r = read(t, 'fs15_z')
    ok &= check('z %s=%s -> row only, members ALL YES' % (key, val), r['ok'] is True)
t = copy.deepcopy(S)
del t['run']['attempts'][0]['close_killed']
ok &= check('v close_killed missing -> end NO', mem(read(t), 'the process ended before') is False)
r = read(repl(SP['z'], 'Event: quit', None), 'fs15_z')
ok &= check('z no Event: quit -> row only (quit_ln None), ALL YES', r['ok'] is True and r['exit']['quit_ln'] is None)
r = read(after_quit(SP['z'], '--- Fatal Error ---'), 'fs15_z')
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

# --- members of fs15_v ---
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
for gv in ('one-frame glitches: 1', None, 'no line here'):
    t = copy.deepcopy(S)
    if gv is None:
        del t['side']['glitch']
    else:
        t['side']['glitch'] = gv
    ok &= check('v glitch %r -> NO' % gv, mem(read(t), '0 one-frame') is False)
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
ok &= check('v FixB12 after the first GuestOut -> NO', mem(read(move_after_guest(S, 'FixB12: mode=1')), 'FixB12: mode=1') is False)
t = copy.deepcopy(S)
t['lines'].insert(-4, '[Vulkan][E] VUID-x')
r = read(t)
ok &= check('v [Vulkan][E] is a reference only', r['ok'] is True and r['form_ok'] is True and r['ref']['vke'] == 1)
fw = 'LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0'
r = read(repl(S, 'LogAsync: full_waits=', fw.replace('drain_timeouts=0', 'drain_timeouts=3')))
ok &= check('v drain_timeouts 3 -> form NO, letter YES', mem(r, 'drain_timeouts 0') is False and r['ok'] is True and r['form_ok'] is False)
ok &= check('v FixB13 mode=0 -> NO', mem(read(repl(S, 'FixB13: mode=1', 'FixB13: mode=0')), 'FixB13') is False)
ok &= check('v no FixB12Stat -> NO', mem(read(repl(S, 'FixB12Stat:', None, True)), 'FixB12Stat: line present') is False)
ok &= check('v LogAsync mode=0 -> NO', mem(read(repl(S, 'LogAsync: mode=1', 'LogAsync: mode=0 requested=1 reason=direction')), 'LogAsync: mode=1') is False)

# --- members of fs15_z ---
S = SP['z']
t = copy.deepcopy(S)
t['lines'] = [l for l in t['lines'] if not (l.startswith('FrameTrace: n=') and int(l.split('=')[1].split()[0]) >= 7198)]
r = read(t, 'fs15_z')   # 7186 frames x 16 700 = 120 006 200 us; 7185 = 119 989 500
ok &= check('z hold 120.006 s -> YES (%s)' % r['info']['hold_s'], mem(r, 'hold >= 120') is True)
t['lines'] = [l for l in t['lines'] if l != 'FrameTrace: n=7197 dt_us=16700 draws=300']
r = read(t, 'fs15_z')
ok &= check('z hold 119.99 s -> NO (%s)' % r['info']['hold_s'], mem(r, 'hold >= 120') is False)
t = copy.deepcopy(S)
t['run']['attempts'][0]['hold_exit'] = 'died'
ok &= check('z hold_exit -> NO', mem(read(t, 'fs15_z'), 'the process lived') is False)
ok &= check('z death in log -> NO', mem(read(before_quit(S, 'ErrorDeviceLost'), 'fs15_z'), '0 death') is False)
t = copy.deepcopy(S)
t['stdout'] = 'Unhandled exception: x\n'
ok &= check('z death in stdout -> NO', mem(read(t, 'fs15_z'), '0 death') is False)
t = copy.deepcopy(S)
t['lines'].insert(-4, 'FrameTrace: n=99999 dt_us=2000000 draws=300')
ok &= check('z frame >= 1 s -> reference only', read(t, 'fs15_z')['ok'] is True)
t = copy.deepcopy(S)
t['idx'] = 10
ok &= check('z short video -> reference only', read(t, 'fs15_z')['ok'] is True)
ok &= check('z FixB12 mode=0 -> reference only', read(repl(S, 'FixB12: mode=1', 'FixB12: mode=0'), 'fs15_z')['ok'] is True)
r = read(S, 'fs15_z')
ok &= check('z info carries FixF24 / FixF29 mode lines (reference)', r['info']['f24'][0][:2] == (1, 1) or r['info']['f24'][0][:2] == [1, 1])

# --- members of fs15_w ---
S = SP['w']
W = 'fs15_w'
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
ok &= check('w DualSrcBlend after the first GuestOut -> NO', mem(read(move_after_guest(S, 'DualSrcBlend: supported=1 enabled=1'), W), 'DualSrcBlend') is False)
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
r = read(repl(S, INIT, None), W)
ok &= check('w FixF24: init absent -> no member (letter of fs15_w), ALL YES', r['ok'] is True and r['form_ok'] is True)
r = read(repl(S, OWNER, 'FixF24: init_owner hid=0 helper=0 msg=0 pump=0 main=1'), W)
ok &= check('w dead init_owner -> no member, ALL YES', r['ok'] is True and r['form_ok'] is True)

# --- reference rows and the table ---
r = read(SP['v'])
ok &= check('bin version string row', r['ref']['bin_version_string'] is True)
ok &= check('fork row', (r['ref']['fork_line'] or '').endswith('6beb3b7'))
ok &= check('FixB12Stat last row', r['ref']['b12stat_last']['passes'] == 5000 and r['ref']['b12stat_lines'] == 3)
rd = os.path.join(TMP, 'runs')
os.makedirs(os.path.join(rd, 'fs15_v'))
json.dump(r, open(os.path.join(rd, 'fs15_v', 'read.json'), 'w'), default=list)
os.makedirs(os.path.join(rd, 'fs15_z'))
json.dump(read(SP['z'], 'fs15_z'), open(os.path.join(rd, 'fs15_z', 'read.json'), 'w'), default=list)
os.makedirs(os.path.join(rd, 'fs14_v'))
json.dump(r, open(os.path.join(rd, 'fs14_v', 'read.json'), 'w'), default=list)
tb = R.table(rd)
ok &= check('table rows (fs14_v dir ignored)', len(tb) == 4
            and '| fs15_v | ADMITTED | bfac84be | ALL YES | ALL YES | 22/22/79/0 | [2299] | [11190] | 1000 / 8800 | 0 | 4.1 | 0 | 3200 |' in tb[2]
            and '| fs15_z | ADMITTED | bfac84be | ALL YES | - | - | [2299] | [11190] | 1000 / 8800 | 0 | 4.1 | 0 | 3200 |' in tb[3])

# --- strict cp1250 output (in-process), ASCII, json, usage ---
d = os.path.join(TMP, 'cp')
write(d, spec('v'))
js = os.path.join(TMP, 'o.json')
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        rc_cp = R.main(['--dir', d, '--tag', 'fs15_v', '--json', js])
        R.main(['--table', '--runs', rd])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
    rc_cp = None
ok &= check('output in strict cp1250 without PYTHONIOENCODING, rc 0', cp_ok and rc_cp == 0 and len(raw.getvalue()) > 1000)
ok &= check('output ASCII only', all(c < 128 for c in raw.getvalue()))
ok &= check('json written and ASCII', os.path.exists(js) and all(c < 128 for c in open(js, 'rb').read()))
ok &= check('json carries the form, the exit row, f24 / f29 / f20 rows', json.load(open(js)).get('form') == 'fs15_v' and json.load(open(js))['exit']['close_rc'] == 0
            and 'f24_rows' in json.load(open(js)) and 'f29_rows' in json.load(open(js)) and 'f20_rows' in json.load(open(js)))
ok &= check('reader file ASCII', all(c < 128 for c in open(SRC, 'rb').read()))
for bad in ('fs14_v', 'f20_v', 'fs15_x', 'fs15_v_r4', 'fs15_w_r0', ''):
    with contextlib.redirect_stdout(io.StringIO()):
        rc_u = R.main([bad])
    ok &= check('usage rc 2 for %r' % bad, rc_u == 2)
shutil.rmtree(TMP, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
