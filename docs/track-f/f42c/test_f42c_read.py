"""Fixtures of f42c_read.py (Track F link F42c, HPP-781; ROADMAP s122 item 694 (g)(6), 705 (v) N1): the clean synthetic tags f20_v,
f20_hb, f20_w read ADMITTED / ALL YES; every admission member (env: KYTY_FIX_F20 '1' exactly at every tag, no other KYTY_FIX_*, no
KYTY_TEST_* / KYTY_GAME_PATCH; level and guest args per tag; --vulkan-validation true only at f20_w; 'ExitFatal:' lines in the log and in
stdout; installed before / after = FS13, during = F42a2; _SaveData manifest cmp; the series members - f20_v 'series snapshot taken',
f20_hb / f20_w 'same caches EQUAL') flips the status; every member of the letter and of the form flips the reading; FixF20 (mode=0 /
absent / after GuestOut / unparsable / second line / with a prefix / CRLF), FixF20Stat (exit line absent, only periodic, unmatched 1,
modules_bound != modules, rewritten 10 / 11, unparsable, two exit lines - the last counts), N1 (quit with no exit line -> member NO and
n1_stop; exit line before quit -> NO; no quit -> NO without n1_stop); edges (1 000 000 / 999 999, hold 300 s, video 2 999 / 3 000,
draws 99 / 100, hold_s 309.9 / 310); W ([Vulkan][E], limit line, [Vulkan][W] 0, DualSrcBlend absent / 0 / after GuestOut,
VALIDATION_STOP); the rows (preparation screen, PipelinePrecache, Vulkan pipeline cache, blob bytes before / after from the tsv,
FixF20Stat counts); the table; strict cp1250 output without PYTHONIOENCODING; the last line is ALL OK.  Port of C:/kyty/f287/f44c/
test_f44c_read.py (F44c, HPP-793).  Early-exit form (ok = True, ok &= ..., sys.exit(0 if ok else 1)).  ASCII only.
The reader is loaded in-process from argv[1] (default: f42c_read.py beside this file); the fixture directories live under BASE.
usage: python test_f42c_read.py [<f42c_read.py under test>]"""
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f42c_read.py')
BASE = Path(os.path.join(HERE, 'fx_f42c'))
_spec = importlib.util.spec_from_file_location('f42c_read_under_test', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f42c_read.py sha256 %s target f42c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0, 0]
SEAL = b'seal fixture\n'
TB = '1994a0ced45c8135f17c8d2aa568278c66375250f1667430c83ba4d0b1a93f29'   # literals, not the reader's constants
FS13 = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'
FS14 = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'
FS12 = '46892c20080819ae090598511748265dfbac31f303a02f1804e5b10db8acae26'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1917-g5ccb1d31'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
HB = 'hoover_beach'
LV = {'f20_v': SKY, 'f20_hb': HB, 'f20_w': SKY}
ok = True


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
        print('FAIL %s' % name)
    return bool(cond)


def env_of(tag):
    e = dict(KYTY_GUEST_ARGS='-lvl ' + LV[tag], KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE='C:/x/g', KYTY_SAMPLE_GATE='C:/x/s',
             KYTY_QUEUE_TRACE='1', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8', KYTY_FIX_F20='1')
    if tag == 'f20_w':
        e.update(VK_LAYER_PATH='C:/VulkanSDK/1.4.357.0/Bin', VK_LAYER_DUPLICATE_MESSAGE_LIMIT='100000000')
    else:
        e.update(KYTY_REC='C:/x/rec.mp4')
    return e


STAT = 'FixB12Stat: passes=%d rewalk=%d rwd=%d lskip=%d'
F21 = 'FixF21: mode=1 wait_ms=12000'
F20 = 'FixF20: mode=1'
F20S = 'FixF20Stat: when=%s calls=%d modules_bound=%d modules=%d sites=%d rewritten=%d unmatched=%d'
EXITS = F20S % ('exit', 5000, 22, 22, 11, 11, 0)
PER = F20S % ('periodic', 4096, 20, 20, 10, 10, 0)
TSV_B = '_PipelineCache\tPPSA21564/pc.bin\t1000\taa\nGLCache\tx/a.bin\t500\tbb\nGLCache\tx/b.bin\t20\tcc\n_ShaderCache\tPPSA21564/p.bin\t7\tdd\n'
TSV_A = '_PipelineCache\tPPSA21564/pc.bin\t1600\tee\nGLCache\tx/a.bin\t900\tff\nGLCache\tx/b.bin\t20\tcc\n_ShaderCache\tPPSA21564/p.bin\t7\tdd\n'


def spec(tag):
    """The clean tag: a list of log lines and the side files."""
    lv = LV[tag]
    L = ['LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100', 'Fork build arigandores/KytyPS5 5ccb1d3',
         F21, 'ShaderSeed: compatibility=x:KytySC3:%s:y' % SIG, 'Shader translation cache: C:/e/_ShaderCache/PPSA21564/%s' % VARIANT_DIR,
         'Vulkan pipeline cache: loaded 1000 bytes from C:/e/_PipelineCache/x.bin', F20,
         'PipelinePrecache: 1986 recipes -> 1842 graphics + 144 compute pipelines queued, 0 skipped, complete, 4690 ms',
         'PipelinePrecache: all pipelines created, 4690 ms',
         'FixB12: mode=1', 'FixB13: mode=1', 'DualSrcBlend: supported=1 enabled=1',
         'ShaderPreparation: startup wait finished in 1234 ms presents_other=0 presents_main=0',
         'GuestOut: Level has started: ', 'GuestOut: Level has started: %s' % lv,
         'FrameTrace: n=10 dt_us=500000 draws=20', 'FrameTrace: n=11 dt_us=16000 draws=300']
    if tag == 'f20_w':
        L += ['[Vulkan][W] some warning', '[Vulkan][W] another']
    for i in range(20000):
        L.append('FrameTrace: n=%d dt_us=16700 draws=300' % (12 + i))
        if i in (100, 900):
            L.append(STAT % (i, i // 2, 0, 1))
        if i == 5000:
            L.append(PER)
    L.append(STAT % (5000, 3000, 7, 2))
    L += ['Event: quit', 'shutdown line', 'Vulkan pipeline cache: saved 1600 bytes to C:/e/_PipelineCache/x.bin (10 us)', EXITS]
    L.append('LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0')
    cmd = ['emu', '--vulkan-validation', 'true' if tag == 'f20_w' else 'false', '--shader-validation', 'false']
    hold = 310 if tag == 'f20_w' else 330
    att = dict(outcome='ok', hold_exit=None, hold_s=hold + 0.2, stable_s=12.0, close_posted=5, close_rc=0, close_killed=False,
               close_s=4.1, close_wait_s=40)
    run = dict(binary_sha256=TB, env=env_of(tag), cmdline=cmd, attempts=[att], guest_args='-lvl ' + lv, hold_s=hold,
               prereg=dict(sha256=hashlib.sha256(SEAL).hexdigest()))
    side = dict(installed_before=FS13, installed_after=FS13, installed_sha=TB, level=lv, manifest_cmp='manifest cmp EQUAL files 5 listsha x',
                glitch='one-frame glitches: 0', sheet='sheet ok')
    if tag == 'f20_v':
        side['series_taken'] = 'series snapshot taken manifest x files 9 at 2026-10-11T13:00:00Z'
    else:
        side['same_cmp'] = 'same caches EQUAL files 4816\nGLCache row DIFFER only-before 1 only-after 2 (row, not a gate)'
    return dict(lines=L, run=run, side=side, idx=0 if tag == 'f20_w' else 3200, stdout='stdout line\n', tag=tag,
                tsv=dict(cache_before=TSV_B, cache_after=TSV_A))


def write(d, s):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'log.txt'), 'wb') as f:
        f.write(('\n'.join(s['lines']) + '\n').encode('ascii'))
    with open(os.path.join(d, 'es.json'), 'w') as f:
        json.dump(s['run'], f)
    for k, v in s['side'].items():
        with open(os.path.join(d, k + '.txt'), 'w') as f:
            f.write(v + '\n')
    for k, v in s['tsv'].items():
        with open(os.path.join(d, k + '.tsv'), 'w', newline='\n') as f:
            f.write(v)
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


def read(s, tag=None):
    tag = tag or s['tag']
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


SV, SH, SW = spec('f20_v'), spec('f20_hb'), spec('f20_w')
ALL = (SV, SH, SW)

# --- the clean tags ---
for S in ALL:
    tg = S['tag']
    r = read(S)
    ok &= check('%s clean ADMITTED %s' % (tg, [a for a, x in r['admission'] if not x]), r['status'] == 'ADMITTED')
    ok &= check('%s clean members ALL YES %s' % (tg, [a for a, x in (r['members'] or []) if not x]), r['ok'] is True)
    ok &= check('%s clean form ALL YES %s' % (tg, [a for a, x in (r['form_members'] or []) if not x]), r['form_ok'] is True)
    ok &= check('%s admission count 25 (%d)' % (tg, len(r['admission'])), len(r['admission']) == 25)
    ok &= check('%s reading: no verdict, F42d' % tg, 'no verdict' in r['reading'] and 'F42d' in r['reading'])
    ok &= check('%s level %s' % (tg, LV[tg]), r['level'] == LV[tg])
    ok &= check('%s n1_stop false' % tg, r['n1_stop'] is False)
    ok &= check('%s N1 in the letter' % tg, in_letter(r, 'N1 (item 705 (v))'))
r = read(SV)
ok &= check('f20_v counts 12 / 11 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 12 and len(r['form_members']) == 11)
ok &= check('f20_v letter carries FixF20 mode and the three stat members',
            in_letter(r, 'FixF20: mode=1') and in_letter(r, 'FixF20Stat exit line: unmatched 0')
            and in_letter(r, 'FixF20Stat exit line: modules_bound = modules') and in_letter(r, 'FixF20Stat exit line: rewritten >= 11'))
r = read(SH)
ok &= check('f20_hb counts 8 / 14 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 8 and len(r['form_members']) == 14)
ok &= check('f20_hb FixF20 in the form, not the letter; no rewritten member', not in_letter(r, 'FixF20: mode=1')
            and mem(r, 'FixF20: mode=1') is True and mem(r, 'FixF20Stat exit line: rewritten') is None)
r = read(SW)
ok &= check('f20_w counts 6 / 9 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 6 and len(r['form_members']) == 9)
ok &= check('f20_w letter carries [Vulkan][E] and the positive control', in_letter(r, '0 [Vulkan][E]') and in_letter(r, 'positive control'))
for tg in ('f20_v_r1', 'f20_hb_r3', 'f20_w_r2'):
    ok &= check('tag form %s' % tg, R.TAG_RX.match(tg) is not None)

# --- admission members (each flips to NOT_ADMITTED), every tag ---
for S in ALL:
    tg = S['tag']
    for key, val in (('installed_before', TB), ('installed_before', FS12), ('installed_after', FS12), ('installed_after', 'x'),
                     ('installed_sha', FS13), ('level', 'pot'), ('manifest_cmp', 'manifest cmp DIFFER only-before 1')):
        t = copy.deepcopy(S)
        t['side'][key] = val
        ok &= check('%s admission %s=%s' % (tg, key, val[:8]), read(t)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    t['side']['installed_before'] = FS14
    t['side']['installed_after'] = FS14
    ok &= check('%s admission installed FS14 before = after - admitted' % tg, read(t)['status'] == 'ADMITTED')
    for b_, a_ in ((FS13, FS14), (FS14, FS13)):
        t = copy.deepcopy(S)
        t['side']['installed_before'] = b_
        t['side']['installed_after'] = a_
        ok &= check('%s admission installed %s -> %s' % (tg, b_[:8], a_[:8]), read(t)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    del t['side']['manifest_cmp']
    ok &= check('%s admission no manifest_cmp file' % tg, read(t)['status'] == 'NOT_ADMITTED')
    for key, val in (('binary_sha256', FS13), ('guest_args', '-lvl pot'), ('hold_s', 150)):
        t = copy.deepcopy(S)
        t['run'][key] = val
        ok &= check('%s admission run %s' % (tg, key), read(t)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    t['run']['prereg']['sha256'] = 'x'
    ok &= check('%s admission prereg' % tg, read(t)['status'] == 'NOT_ADMITTED')
    for kk, vv in (('KYTY_FIX_B12', '1'), ('KYTY_FIX_F21', '1'), ('KYTY_FIX_F25', '1'), ('KYTY_FIX_F29', '1'), ('KYTY_FIX_F24', '1'),
                   ('KYTY_FIX_F26', '1'), ('KYTY_DIAG_B32', '1'), ('KYTY_GAME_PATCH', 'p'), ('KYTY_GPU_CHECKPOINTS', '1'),
                   ('KYTY_S_REPLAY', '3'), ('KYTY_PIPELINE_SALT', '1'), ('KYTY_FIX_F20', '0'), ('KYTY_FIX_F20', 'true'),
                   ('KYTY_FIX_F20', ''), ('KYTY_FIX_F20', '2')):
        t = copy.deepcopy(S)
        t['run']['env'][kk] = vv
        ok &= check('%s admission env %s=%s' % (tg, kk, vv), read(t)['status'] == 'NOT_ADMITTED')
    for k0 in ('KYTY_GPU_CLOCK_PIN', 'KYTY_GUEST_ARGS', 'KYTY_FIX_F20', 'KYTY_GPU_HANG_ABORT_S'):
        t = copy.deepcopy(S)
        del t['run']['env'][k0]
        ok &= check('%s admission env missing %s' % (tg, k0), read(t)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    t['run']['env']['KYTY_TEST_EXITFATAL'] = 'P:1'
    r = read(t)
    ok &= check('%s env KYTY_TEST_ -> own member' % tg, r['status'] == 'NOT_ADMITTED'
                and [b for a, b in r['admission'] if a.startswith('no KYTY_TEST_*')] == [False])
    for where in ('log', 'stdout'):
        t = copy.deepcopy(S)
        if where == 'log':
            t['lines'].insert(4, 'ExitFatal: config arm=P seed=1')
        else:
            t['stdout'] = 'ExitFatal: config arm=P seed=1\n'
        ok &= check('%s ExitFatal: in %s -> NOT_ADMITTED' % (tg, where), read(t)['status'] == 'NOT_ADMITTED')
    for extra in (['--shader-validation', 'true'], ['--rd'], ['--vulkan-validation', 'true' if tg != 'f20_w' else 'false']):
        t = copy.deepcopy(S)
        t['run']['cmdline'] = t['run']['cmdline'] + extra
        ok &= check('%s admission cmdline %s' % (tg, extra), read(t)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    t['run']['attempts'][0]['outcome'] = 'not_entered'
    ok &= check('%s admission outcome' % tg, read(t)['status'] == 'NOT_ADMITTED')
    for extra in ('Window 1 minimized', 'Recovering Vulkan swapchain', 'GamePatch: loaded', 'DiagB32: mode=1',
                  'TestLogStall: config at_ms=1 sleep_ms=3000 k=3 gap_ms=5000 on=writer'):
        t = copy.deepcopy(S)
        t['lines'].insert(4, extra)
        ok &= check('%s admission line %s' % (tg, extra), read(t)['status'] == 'NOT_ADMITTED')
    ok &= check('%s admission signature' % tg, read(repl(S, 'ShaderSeed:', 'ShaderSeed: compatibility=x:KytySC3:%s:y' % ('0' * 40)))['status'] == 'NOT_ADMITTED')
    ok &= check('%s admission catalog' % tg, read(repl(S, 'Shader translation cache:', 'Shader translation cache: C:/e/variant_fixb26'))['status'] == 'NOT_ADMITTED')
    ok &= check('%s admission entry line' % tg, read(repl(S, 'GuestOut: Level has started: %s' % LV[tg], None))['status'] == 'NOT_ADMITTED')
    r = read(repl(S, 'LogAsync: full_waits=', None))
    ok &= check('%s no summary -> NOT_ADMITTED run' % tg, r['status'] == 'NOT_ADMITTED' and r['interference'].startswith('run'))
    t = copy.deepcopy(S)
    t['stdout'] = None
    ok &= check('%s no stdout -> NOT_ADMITTED' % tg, read(t)['status'] == 'NOT_ADMITTED')
# the level of the entry line: Sky Garden entry at f20_hb (and hoover_beach at f20_v) is not the entry
ok &= check('f20_hb with the Sky Garden entry line -> NOT_ADMITTED',
            read(repl(SH, 'GuestOut: Level has started: %s' % HB, 'GuestOut: Level has started: %s' % SKY))['status'] == 'NOT_ADMITTED')
ok &= check('f20_v with the hoover_beach entry line -> NOT_ADMITTED',
            read(repl(SV, 'GuestOut: Level has started: %s' % SKY, 'GuestOut: Level has started: %s' % HB))['status'] == 'NOT_ADMITTED')
t = copy.deepcopy(SH)
t['run']['env']['KYTY_GUEST_ARGS'] = '-lvl ' + SKY
ok &= check('f20_hb env guest args Sky Garden -> NOT_ADMITTED', read(t)['status'] == 'NOT_ADMITTED')
t = copy.deepcopy(SW)
t['run']['env']['KYTY_REC'] = 'C:/x/r.mp4'
ok &= check('f20_w with KYTY_REC -> NOT_ADMITTED', read(t)['status'] == 'NOT_ADMITTED')
t = copy.deepcopy(SV)
t['run']['env']['VK_LAYER_PATH'] = 'x'
ok &= check('f20_v with VK_LAYER_PATH -> NOT_ADMITTED', read(t)['status'] == 'NOT_ADMITTED')
t = copy.deepcopy(SW)
t['run']['env']['VK_LAYER_DUPLICATE_MESSAGE_LIMIT'] = '1000000'
ok &= check('f20_w limit 1000000 -> NOT_ADMITTED', read(t)['status'] == 'NOT_ADMITTED')
# --- series members ---
for val in (None, 'series snapshot missing', ''):
    t = copy.deepcopy(SV)
    if val is None:
        del t['side']['series_taken']
    else:
        t['side']['series_taken'] = val
    ok &= check('f20_v series_taken %r -> NOT_ADMITTED' % val, read(t)['status'] == 'NOT_ADMITTED')
for S in (SH, SW):
    for val in (None, 'same caches DIFFER only-before 1 only-after 0', 'same caches MISSING x'):
        t = copy.deepcopy(S)
        if val is None:
            del t['side']['same_cmp']
        else:
            t['side']['same_cmp'] = val
        ok &= check('%s same_cmp %r -> NOT_ADMITTED' % (S['tag'], val), read(t)['status'] == 'NOT_ADMITTED')
    t = copy.deepcopy(S)
    t['side']['same_cmp'] = 'same caches EQUAL files 3\nGLCache row EQUAL only-before 0 only-after 0 (row, not a gate)'
    ok &= check('%s same caches EQUAL with GLCache EQUAL -> ADMITTED' % S['tag'], read(t)['status'] == 'ADMITTED')
t = copy.deepcopy(SV)
t['side']['same_cmp'] = 'same caches DIFFER'
ok &= check('f20_v ignores same_cmp', read(t)['status'] == 'ADMITTED')
t = copy.deepcopy(SH)
t['side']['series_taken'] = 'nothing'
ok &= check('f20_hb ignores series_taken', read(t)['status'] == 'ADMITTED')
d = os.path.join(TMP, 'nolog')
write(d, copy.deepcopy(SV))
os.remove(os.path.join(d, 'log.txt'))
r = R.read_tag('f20_v', R.paths('f20_v', d))
ok &= check('no log -> NOT_ADMITTED, no members', r['status'] == 'NOT_ADMITTED' and r['members'] is None)
os.remove(os.path.join(d, 'es.json'))
ok &= check('no json -> NOT_ADMITTED', R.read_tag('f20_v', R.paths('f20_v', d))['status'] == 'NOT_ADMITTED')

# --- FixF20 mode (letter at f20_v, form at f20_hb / f20_w) ---
FM = 'FixF20: mode=1'
for S, where in ((SV, 'ok'), (SH, 'form_ok'), (SW, 'form_ok')):
    tg = S['tag']
    r = read(repl(S, F20, 'FixF20: mode=0'))
    ok &= check('%s FixF20 mode=0 -> NO, %s False' % (tg, where), mem(r, FM) is False and r[where] is False)
    ok &= check('%s FixF20 absent -> NO' % tg, mem(read(repl(S, F20, None)), FM) is False)
    ok &= check('%s FixF20 mode=10 -> NO' % tg, mem(read(repl(S, F20, 'FixF20: mode=10')), FM) is False)
    ok &= check('%s FixF20 trailing garbage -> NO' % tg, mem(read(repl(S, F20, F20 + ' x')), FM) is False)
    ok &= check('%s FixF20 prefix -> YES' % tg, mem(read(repl(S, F20, '[1][00:00:00.001] ' + F20)), FM) is True)
    ok &= check('%s FixF20 CRLF -> YES' % tg, mem(read(repl(S, F20, F20 + '\r')), FM) is True)
    t = copy.deepcopy(S)
    t['lines'].remove(F20)
    t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, F20)
    ok &= check('%s FixF20 after the first GuestOut -> NO' % tg, mem(read(t), FM) is False)
    t = copy.deepcopy(S)
    t['lines'].insert(t['lines'].index(F20) + 1, 'FixF20: mode=x')
    ok &= check('%s FixF20 good + unparsable -> NO' % tg, mem(read(t), FM) is False)
    t = copy.deepcopy(S)
    t['lines'].insert(t['lines'].index(F20) + 1, 'FixF20: mode=0')
    ok &= check('%s FixF20 second line mode=0 -> NO' % tg, mem(read(t), FM) is False)
    t = copy.deepcopy(S)
    t['lines'].insert(4, 'FixF20: something')
    r = read(t)
    ok &= check('%s other FixF20 line -> row, ALL YES' % tg, r['ok'] is True and r['form_ok'] is True and r['f20_rows']['f20_other'] == 1)

# --- FixF20Stat members and N1 ---
UM, BM, RW = 'FixF20Stat exit line: unmatched 0', 'FixF20Stat exit line: modules_bound = modules', 'FixF20Stat exit line: rewritten'
N1 = 'N1 (item 705 (v))'
for S in ALL:
    tg = S['tag']
    r = read(repl(S, EXITS, None))
    ok &= check('%s no exit line -> stat NO, N1 NO, n1_stop' % tg, mem(r, UM) is False and mem(r, BM) is False and mem(r, N1) is False
                and r['n1_stop'] is True and 'N1 STOP' in '\n'.join(R.rows_out(r)))
    r = read(repl(S, EXITS, F20S % ('exit', 5000, 22, 22, 11, 11, 1)))
    ok &= check('%s unmatched 1 -> NO' % tg, mem(r, UM) is False and mem(r, BM) is True)
    r = read(repl(S, EXITS, F20S % ('exit', 5000, 22, 21, 11, 11, 0)))
    ok &= check('%s bound 22 != modules 21 -> NO' % tg, mem(r, BM) is False and mem(r, UM) is True)
    r = read(repl(S, EXITS, EXITS + ' x'))
    ok &= check('%s unparsable exit line -> NO, counted' % tg, mem(r, UM) is False and r['f20_rows']['f20stat_unparsable'] == 1)
    r = read(repl(S, EXITS, None))
    t = copy.deepcopy(S)
    t['lines'].remove(EXITS)
    t['lines'].insert(t['lines'].index('Event: quit'), EXITS)
    r = read(t)
    ok &= check('%s exit line before Event: quit -> N1 NO, stat YES' % tg, mem(r, N1) is False and mem(r, UM) is True and r['n1_stop'] is True)
    r = read(repl(S, 'Event: quit', None))
    ok &= check('%s no Event: quit -> N1 NO, no n1_stop' % tg, mem(r, N1) is False and r['n1_stop'] is False)
    t = copy.deepcopy(S)
    t['lines'].insert(t['lines'].index(EXITS), F20S % ('exit', 4000, 20, 20, 10, 10, 3))
    r = read(t)
    ok &= check('%s two exit lines - the last counts' % tg, mem(r, UM) is True and r['f20_rows']['f20stat_max_unmatched'] == 3)
    t = copy.deepcopy(S)
    t['lines'] = [l.replace(PER, F20S % ('periodic', 4096, 20, 20, 10, 10, 2)) for l in t['lines']]
    r = read(t)
    ok &= check('%s periodic unmatched 2 -> row only' % tg, mem(r, UM) is True and r['f20_rows']['f20stat_max_unmatched'] == 2
                and r['f20_rows']['f20stat_periodic'] == 1)
    r = read(repl(S, EXITS, '[3][00:00:01.000] ' + EXITS))
    ok &= check('%s exit line with a prefix -> YES' % tg, mem(r, UM) is True and mem(r, N1) is True)
for rw, want in ((10, False), (11, True), (0, False)):
    r = read(repl(SV, EXITS, F20S % ('exit', 5000, 22, 22, 11, rw, 0)))
    ok &= check('f20_v rewritten %d -> %s' % (rw, want), mem(r, RW) is want)
r = read(repl(SH, EXITS, F20S % ('exit', 5000, 22, 22, 0, 0, 0)))
ok &= check('f20_hb rewritten 0 -> no member, ALL YES', r['ok'] is True and r['form_ok'] is True)

# --- form fs12_v (f20_v / f20_hb) ---
for S in (SV, SH):
    tg = S['tag']
    r = read(repl(S, F21, 'FixF21: mode=0 wait_ms=12000'))
    ok &= check('%s FixF21 mode=0 -> form NO, letter YES' % tg, mem(r, 'FixF21: mode=1') is False and r['ok'] is True)
    r = read(after_quit(S, '--- Fatal Error ---'))
    ok &= check('%s Fatal after quit -> after-quit NO, death NO' % tg, mem(r, 'after Event: quit') is False and mem(r, '0 death') is False)
    r = read(after_quit(S, 'FixF21: wait_expired tid=3 waited_ms=12012'))
    ok &= check('%s wait_expired -> form NO' % tg, mem(r, '0 FixF21: wait_expired') is False)
    for key, val in (('close_killed', True), ('close_rc', None)):
        t = copy.deepcopy(S)
        t['run']['attempts'][0][key] = val
        r = read(t)
        ok &= check('%s %s=%s -> form end NO, letter YES' % (tg, key, val), mem(r, 'the process ended before') is False and r['ok'] is True)
    fw = 'LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0'
    r = read(repl(S, 'LogAsync: full_waits=', fw.replace('drain_timeouts=0', 'drain_timeouts=3')))
    ok &= check('%s drain_timeouts 3 -> form NO' % tg, mem(r, 'drain_timeouts 0') is False and r['ok'] is True)
    ok &= check('%s FixB13 mode=0 -> NO' % tg, mem(read(repl(S, 'FixB13: mode=1', 'FixB13: mode=0')), 'FixB13') is False)
    ok &= check('%s FixB12 mode=0 -> NO' % tg, mem(read(repl(S, 'FixB12: mode=1', 'FixB12: mode=0')), 'FixB12: mode=1') is False)
    ok &= check('%s no FixB12Stat -> NO' % tg, mem(read(repl(S, 'FixB12Stat:', None, True)), 'FixB12Stat: line present') is False)
    ok &= check('%s LogAsync mode=0 -> NO' % tg, mem(read(repl(S, 'LogAsync: mode=1', 'LogAsync: mode=0 requested=1')), 'LogAsync: mode=1') is False)
    # letter
    t = copy.deepcopy(S)
    t['lines'].insert(t['lines'].index('Event: quit'), 'FrameTrace: n=99999 dt_us=1000000 draws=300')
    ok &= check('%s frame 1 000 000 -> NO' % tg, mem(read(t), '0 frames >= 1 s') is False)
    t = copy.deepcopy(S)
    t['lines'].insert(t['lines'].index('Event: quit'), 'FrameTrace: n=99999 dt_us=999999 draws=300')
    ok &= check('%s frame 999 999 -> YES' % tg, mem(read(t), '0 frames >= 1 s') is True)
    t = copy.deepcopy(S)
    t['lines'] = [l.replace('draws=300', 'draws=99') for l in t['lines']]
    r = read(t)
    ok &= check('%s no first scene frame -> NO' % tg, mem(r, '0 frames >= 1 s') is False and mem(r, 'hold >= 300') is False)
    t = copy.deepcopy(S)
    t['lines'] = [l.replace('n=11 dt_us=16000 draws=300', 'n=11 dt_us=16000 draws=100') for l in t['lines']]
    ok &= check('%s draws 100 is the first scene frame' % tg, read(t)['info']['first_scene_n'] == 11)
    t = copy.deepcopy(S)
    t['lines'] = [l for l in t['lines'] if not (l.startswith('FrameTrace: n=') and int(l.split('=')[1].split()[0]) >= 17976)]
    r = read(t)
    ok &= check('%s hold 299.9988 s -> NO' % tg, mem(r, 'hold >= 300') is False)
    t['lines'].insert(t['lines'].index('Event: quit'), 'FrameTrace: n=17976 dt_us=1200 draws=300')
    ok &= check('%s hold exactly 300 s -> YES' % tg, mem(read(t), 'hold >= 300') is True)
    for n_idx, want in ((2999, False), (3000, True), (0, False)):
        t = copy.deepcopy(S)
        t['idx'] = n_idx
        ok &= check('%s video %d -> %s' % (tg, n_idx, want), mem(read(t), 'video index') is want)
    for gv in ('one-frame glitches: 1', None):
        t = copy.deepcopy(S)
        if gv is None:
            del t['side']['glitch']
        else:
            t['side']['glitch'] = gv
        ok &= check('%s glitch %r -> NO' % (tg, gv), mem(read(t), '0 one-frame') is False)
    t = copy.deepcopy(S)
    del t['side']['sheet']
    ok &= check('%s no sheet -> NO' % tg, mem(read(t), 'sheet') is False)
    t = copy.deepcopy(S)
    t['run']['attempts'][0]['hold_exit'] = 'died'
    ok &= check('%s hold_exit -> NO' % tg, mem(read(t), 'the process lived') is False)
    for dm in ('Unhandled exception: x', 'GpuHangAbort: x', 'ErrorDeviceLost'):
        ok &= check('%s death %s -> NO' % (tg, dm), mem(read(before_quit(S, dm)), '0 death') is False)
    t = copy.deepcopy(S)
    t['lines'].insert(-4, '[Vulkan][E] VUID-x')
    r = read(t)
    ok &= check('%s [Vulkan][E] is a reference only' % tg, r['ok'] is True and r['ref']['vke'] == 1)

# --- W ---
r = read(SW)
ok &= check('f20_w clean: no video member', mem(r, 'video index') is None)
t = copy.deepcopy(SW)
t['lines'].insert(-4, '[Vulkan][E] VUID-x')
r = read(t)
ok &= check('f20_w [Vulkan][E] -> NO; lived -> no VALIDATION_STOP', mem(r, '0 [Vulkan][E]') is False and mem(r, 'no VALIDATION_STOP') is True)
t['run']['attempts'][0]['hold_s'] = 120
r = read(t)
ok &= check('f20_w [Vulkan][E] and not lived -> VALIDATION_STOP NO', mem(r, 'no VALIDATION_STOP') is False and mem(r, 'lived to the end') is False)
for hs, want in ((309.9, False), (310, True)):
    t = copy.deepcopy(SW)
    t['run']['attempts'][0]['hold_s'] = hs
    ok &= check('f20_w hold_s %s -> %s' % (hs, want), mem(read(t), 'lived to the end') is want)
t = copy.deepcopy(SW)
t['lines'].insert(-4, 'x this will be the last time reporting it')
ok &= check('f20_w limit line -> NO', mem(read(t), '0 limit lines') is False)
ok &= check('f20_w [Vulkan][W] 0 -> NO', mem(read(repl(SW, '[Vulkan][W]', None, True)), 'positive control') is False)
ok &= check('f20_w DualSrcBlend absent -> NO', mem(read(repl(SW, 'DualSrcBlend:', None)), 'DualSrcBlend') is False)
ok &= check('f20_w DualSrcBlend enabled=0 -> NO', mem(read(repl(SW, 'DualSrcBlend:', 'DualSrcBlend: supported=1 enabled=0')), 'DualSrcBlend') is False)
t = copy.deepcopy(SW)
t['lines'].remove('DualSrcBlend: supported=1 enabled=1')
t['lines'].insert(t['lines'].index('GuestOut: Level has started: ') + 1, 'DualSrcBlend: supported=1 enabled=1')
ok &= check('f20_w DualSrcBlend after GuestOut -> NO', mem(read(t), 'DualSrcBlend') is False)
ok &= check('f20_w FixF21 mode=0 -> form NO', mem(read(repl(SW, F21, 'FixF21: mode=0 wait_ms=1')), 'FixF21: mode=1') is False)
t = copy.deepcopy(SW)
t['stdout'] = 'GpuHangAbort: x\n'
ok &= check('f20_w death in stdout -> NO', mem(read(t), '0 death') is False)

# --- rows ---
r = read(SV)
fr = r['f20_rows']
ok &= check('row prep ms 1234', fr['prep_ms'] == [1234])
ok &= check('row PipelinePrecache 2 lines', fr['precache_n'] == 2 and fr['precache_lines'][1].endswith('4690 ms'))
ok &= check('row Vulkan pipeline cache 2 lines', fr['vk_pipeline_cache_n'] == 2)
ok &= check('row blob before / after 1000 / 1600, GLCache 520 / 920', fr['blob_pipelinecache_before'] == 1000 and fr['blob_pipelinecache_after'] == 1600
            and fr['glcache_before'] == 520 and fr['glcache_after'] == 920)
ok &= check('row FixF20Stat 2 lines, periodic 1, exit rewritten 11', fr['f20stat_lines'] == 2 and fr['f20stat_periodic'] == 1
            and fr['f20stat_exit']['rewritten'] == 11 and fr['f20stat_last']['when'] == 'exit')
rows = '\n'.join(R.rows_out(r))
ok &= check('rows print prep, precache, blob and FixF20Stat rows', 'ROW preparation screen (not a gate): ShaderPreparation ms [1234]' in rows
            and 'ROW driver blob (not a gate): _PipelineCache bytes before 1000 after 1600' in rows and 'ROW FixF20Stat' in rows
            and 'ROW PipelinePrecache (not a gate): 2 lines' in rows)
t = copy.deepcopy(SV)
t['tsv'] = {}
r = read(t)
ok &= check('no tsv -> blob rows None, still ALL YES', r['f20_rows']['blob_pipelinecache_before'] is None and r['ok'] is True)
r = read(repl(SV, 'ShaderPreparation:', 'ShaderPreparation: startup wait finished in x ms'))
ok &= check('prep line unparsable -> row None', r['f20_rows']['prep_ms'] == [None])
ok &= check('bin version string row', read(SV)['ref']['bin_version_string'] is True)

# --- table ---
rd = os.path.join(TMP, 'runs')
for tg, S in (('f20_v', SV), ('f20_hb', SH), ('f20_w', SW), ('fs13_v', SV)):
    os.makedirs(os.path.join(rd, tg))
    json.dump(read(S), open(os.path.join(rd, tg, 'read.json'), 'w'), default=list)
tb = R.table(rd)
ok &= check('table rows (three tags, fs13_v skipped)', len(tb) == 5)
ok &= check('table f20_v row', '| f20_v | ADMITTED | 1994a0ce | ALL YES | ALL YES | 22/22/11/0 | [1234] | 1000 / 1600 | 0 | 4.1 |' in tb[3])

# --- strict cp1250 output (in-process), ASCII, json, usage ---
d = os.path.join(TMP, 'cp')
write(d, spec('f20_hb'))
js = os.path.join(TMP, 'o.json')
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        rc_cp = R.main(['--dir', d, '--tag', 'f20_hb', '--json', js])
        R.main(['--table', '--runs', rd])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
    rc_cp = None
ok &= check('output in strict cp1250 without PYTHONIOENCODING, rc 0', cp_ok and rc_cp == 0 and len(raw.getvalue()) > 1000)
ok &= check('output ASCII only', all(c < 128 for c in raw.getvalue()))
ok &= check('json written and ASCII', os.path.exists(js) and all(c < 128 for c in open(js, 'rb').read()))
ok &= check('json carries the form and the rows', json.load(open(js)).get('form') == 'f20_hb' and json.load(open(js))['f20_rows']['prep_ms'] == [1234])
ok &= check('reader file ASCII', all(c < 128 for c in open(SRC, 'rb').read()))
for bad in ('fs13_v', 'f29_v', 'f20_x', 'f20_v_r4', 'f20_hb_r0', 'f42c_ret', ''):
    with contextlib.redirect_stdout(io.StringIO()):
        rc_u = R.main([bad])
    ok &= check('usage rc 2 for %r' % bad, rc_u == 2)
shutil.rmtree(TMP, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
