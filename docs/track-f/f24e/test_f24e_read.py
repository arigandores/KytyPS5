"""Fixtures of f24e_read.py (F24e HPP-664; seal docs/track-f/f24e.md section 7): every member and edge of both forms (v, w), the references,
the interference rows, the outputs (strict cp1250, ASCII, json, unknown tag, repeat tags).  Synthetic files only, no game.
The mutlib early-exit form: the only bindings of the flag are `ok = True` and `ok &= ...`, the last statement is `sys.exit(0 if ok else 1)`;
the reader is loaded in-process from argv[1] (default: f24e_read.py beside this file); the fixture directories live under BASE.
The first line names the suite and the target with sha256; the output ends with ALL OK.  ASCII only.
usage: python test_f24e_read.py [<f24e_read.py under test>]"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f24e_read.py')
BASE = Path(os.path.join(HERE, 'fx_f24e'))   # mutlib gives every job its own copy of this directory
TB = '91f155b70f867124781a687b0d86442f45abed90e33d4b9e749d296ccfa63e2f'
S18 = 'b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a'
FS8 = '2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b'
VER = 'KytyPS5-2026-09-15-6a2987a-1899-gfbae3a68'
DIRL = '_ShaderCache' + chr(92) + 'PPSA21564' + chr(92) + 'variant_fixb26_fixb1b_fixf10_fixf19'
LAYER = 'C:/VulkanSDK/1.4.357.0/Bin'
CMD = ['kyty_emulator.exe', '--vulkan-validation', 'false', '--game', 'x']
NL = chr(10)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


_spec = importlib.util.spec_from_file_location('f24e_read_under_test', SRC)
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)
print('suite test_f24e_read.py sha256 %s target f24e_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0]
LAST = ['']
SEQ = [0]


def check(name, cond):
    N[0] += 1
    print(('ok   ' if cond else 'FAIL ') + name)
    return bool(cond)


def scene_rows(n_frames=310, dt=999999, big=None, draws=200):
    rows = []
    for i in range(n_frames):
        d = big if (big is not None and i == 5) else dt
        rows.append('FrameTrace: n=%d dt_us=%d draws=%d' % (100 + i, d, draws))
    return rows


def base_log(form, **kw):
    lines = ['  version: Fork build arigandores/KytyPS5 fbae3a6, x', 'Shader translation cache: ' + DIRL]
    if kw.get('b13', True):
        lines += kw.get('b13_lines', ['FixB13: mode=1'])
    if form == 'w' and kw.get('dual', True):
        lines.append('DualSrcBlend: supported=1 enabled=1')
    lines += kw.get('pre', [])
    lines.append('GuestOut: hello')
    lines += kw.get('post_guest', [])
    lines.append('FrameTrace: n=1 dt_us=16000 draws=10')
    lines.append('GuestOut: Level has started: %s' % kw.get('level', 'underwater_aerial_garden'))
    lines.append('FrameTrace: n=99 dt_us=16000 draws=%d' % kw.get('first_draws', 100))
    lines += kw.get('scene', scene_rows())
    if form == 'w':
        lines += ['[Vulkan][W] some warning'] * kw.get('vkw', 1)
    lines += kw.get('tail', [])
    return lines


def wr(d, name, data):
    with open(os.path.join(d, name), 'wb') as f:
        f.write(data.encode('utf-8') if isinstance(data, str) else data)


def make(form='v', **kw):
    SEQ[0] += 1
    d = str(BASE / ('c%03d' % SEQ[0]))
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    log = kw.get('log', base_log(form, **kw))
    if log is not None:
        wr(d, 'log.txt', NL.join(log) + NL)
    if kw.get('stdout', 'ok' + NL) is not None:
        wr(d, 'stdout.txt', kw.get('stdout', 'ok' + NL))
    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_FIX_B13': '1', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}
    cmd = list(CMD)
    if form == 'w':
        env.update(VK_LAYER_PATH=LAYER, VK_LAYER_DUPLICATE_MESSAGE_LIMIT='100000000')
        cmd += ['--vulkan-validation', 'true']
    else:
        env['KYTY_REC'] = 'x.mp4'
    for k, v in kw.get('env_set', {}).items():
        if v is None:
            env.pop(k, None)
        else:
            env[k] = v
    if 'cmd' in kw:
        cmd = kw['cmd']
    att = {'outcome': 'ok', 'hold_exit': None, 'hold_s': 330.1 if form == 'v' else 310.0, 'close_posted': 5, 'close_rc': 0,
           'close_killed': False, 'close_s': 4.0}
    att.update(kw.get('att', {}))
    if kw.get('es', True):
        wr(d, 'es.json', json.dumps({'env': env, 'cmdline': cmd, 'attempts': [att]}))
    if form == 'v' and kw.get('idx', 3100) is not None:
        wr(d, 'rec.idx', ('r' + NL) * kw.get('idx', 3100))
    if kw.get('glitch', 'one-frame glitches: 0') is not None:
        wr(d, 'glitch.txt', kw.get('glitch', 'one-frame glitches: 0') + NL)
    if kw.get('sheet', True):
        wr(d, 'sheet.txt', 'sheet: x.png' + NL)
    for n, v in (('installed_sha', kw.get('isha', TB)), ('installed_before', kw.get('ibefore', S18)),
                 ('installed_after', kw.get('iafter', S18))):
        if v is not None:
            wr(d, n + '.txt', v + NL)
    wr(d, 'warm.txt', 'state before the start: pipelines.bin present' + NL)
    if kw.get('mc', 'manifest cmp EQUAL files 10') is not None:
        wr(d, 'manifest_cmp.txt', kw.get('mc', 'manifest cmp EQUAL files 10') + NL)
    wr(d, 'manifest_before.tsv', '_SaveData' + chr(9) + 'a' + chr(9) + 'x' + NL)
    wr(d, 'manifest_run.tsv', kw.get('mfrun', '_SaveData' + chr(9) + 'a' + chr(9) + 'x' + NL))
    if kw.get('bin', True):
        wr(d, 'bin.exe', b'MZ' + kw.get('ver', VER).encode() + b'.')
    return d


def out_of(d, form):
    return NL.join(M.rows('fixture', M.read(M.paths(base=d), form)))


def rowmap(out):
    m = {}
    for ln in out.split(NL):
        if ln.startswith('  ROW '):
            k, v = ln[6:].rsplit(': ', 1)
            m[k] = v
    return m


def key(rm, sub):
    ks = [k for k in rm if sub in k]
    return rm[ks[0]] if len(ks) == 1 else 'KEY?%d' % len(ks)


def case(name, form, expect, **kw):
    """expect: {substring of a row name: value}; every other row must be YES."""
    d = make(form, **kw)
    out = out_of(d, form)
    LAST[0] = out
    rm = rowmap(out)
    good = check('%s: rows read (%d)' % (name, len(rm)), len(rm) >= 15)
    for sub, v in expect.items():
        got = key(rm, sub)
        good = check('%s row [%s] = %s (got %s)' % (name, sub, v, got), got == v) and good
    others = [k for k in rm if not any(s in k for s in expect)]
    bad = [k for k in others if rm[k] != 'YES']
    good = check('%s other rows YES (bad %s)' % (name, bad), not bad) and good
    return good


ok = True
ok &= check('constants: tag binary, version, installed S18, directory, limit, holds, video', M.BIN_EXPECT == TB
            and M.VERSION == VER.encode() and M.WANT == S18 and M.DIR_FIX == 'variant_fixb26_fixb1b_fixf10_fixf19'
            and M.LIMIT == '100000000' and M.HOLD_V_US == 300000000 and M.HOLD_W_S == 310 and M.VIDEO_MIN == 3000
            and M.K2_US == 1000000 and M.TAGS == ('b13_v', 'b13_w') and M.REV == 'fbae3a6')

# positive
ok &= case('v positive', 'v', {})
ok &= check('v positive has 16 rows', LAST[0].count('  ROW ') == 16)
ok &= check('v positive REF revision YES', 'REF revision text names fbae3a6: YES' in LAST[0])
ok &= check('v positive REF directory YES', 'in every line: YES' in LAST[0])
ok &= case('w positive', 'w', {})
ok &= check('w positive has 15 rows', LAST[0].count('  ROW ') == 15)
# binary and installed
ok &= case('v tag binary FS8', 'v', {'binary sha256 of the tag': 'NO'}, isha=FS8)
ok &= case('v tag binary missing', 'v', {'binary sha256 of the tag': 'NO'}, isha=None)
ok &= case('v version S18', 'v', {'version string': 'NO'}, ver='KytyPS5-2026-09-15-6a2987a-1897-g0005e11f')
ok &= case('v version no bin', 'v', {'version string': 'NOT_READ'}, bin=False)
ok &= case('v installed before FS8', 'v', {'installed b3cee576 before': 'NO'}, ibefore=FS8)
ok &= case('v installed after = tag binary', 'v', {'installed b3cee576 after': 'NO'}, iafter=TB)
ok &= case('w installed after missing', 'w', {'installed b3cee576 after': 'NO'}, iafter=None)
# env
ok &= case('v env B13=0', 'v', {'env = form': 'NO'}, env_set={'KYTY_FIX_B13': '0'})
ok &= case('v env no B13', 'v', {'env = form': 'NO'}, env_set={'KYTY_FIX_B13': None})
ok &= case('v env extra FIX', 'v', {'env = form': 'NO'}, env_set={'KYTY_FIX_F10': '1'})
ok &= case('v env GAME_PATCH', 'v', {'env = form': 'NO'}, env_set={'KYTY_GAME_PATCH': 'x'})
ok &= case('v env CHECKPOINTS', 'v', {'env = form': 'NO'}, env_set={'KYTY_GPU_CHECKPOINTS': '0'})
ok &= case('w env SHADER_SEED', 'w', {'env = form': 'NO'}, env_set={'KYTY_SHADER_SEED': '0'})
ok &= case('w env S_REPLAY', 'w', {'env = form': 'NO'}, env_set={'KYTY_S_REPLAY': '3'})
ok &= case('w env S_REPLAY_TEST', 'w', {'env = form': 'NO'}, env_set={'KYTY_S_REPLAY_TEST': 'stop'})
ok &= case('v env layer present', 'v', {'env = form': 'NO'}, env_set={'VK_LAYER_PATH': LAYER})
ok &= case('v env validation true', 'v', {'env = form': 'NO'}, cmd=CMD + ['--vulkan-validation', 'true'])
ok &= case('w env no layer path', 'w', {'env = form': 'NO'}, env_set={'VK_LAYER_PATH': None})
ok &= case('w env limit 1000000', 'w', {'env = form': 'NO'}, env_set={'VK_LAYER_DUPLICATE_MESSAGE_LIMIT': '1000000'})
ok &= case('w env filter', 'w', {'env = form': 'NO'}, env_set={'VK_LAYER_MESSAGE_ID_FILTER': 'x'})
ok &= case('w env extra layer key', 'w', {'env = form': 'NO'}, env_set={'VK_LAYER_SETTINGS_PATH': 'x'})
ok &= case('w env validation false', 'w', {'env = form': 'NO'}, cmd=list(CMD))
ok &= case('v no es.json', 'v', {'env = form': 'NOT_READ', 'entered': 'NOT_READ', 'lived through the hold': 'NOT_READ'}, es=False)
# FixB13
ok &= case('v FixB13 mode=0', 'v', {'FixB13': 'NO'}, b13_lines=['FixB13: mode=0'])
ok &= case('w FixB13 missing', 'w', {'FixB13': 'NO'}, b13=False)
ok &= case('v FixB13 second mode=0', 'v', {'FixB13': 'NO'}, b13_lines=['FixB13: mode=1', 'FixB13: mode=0'])
ok &= case('v FixB13 two mode=1', 'v', {}, b13_lines=['FixB13: mode=1', 'FixB13: mode=1'])
ok &= case('v FixB13 mode=10', 'v', {'FixB13': 'NO'}, b13_lines=['FixB13: mode=10'])
ok &= case('v FixB13 after GuestOut', 'v', {'FixB13': 'NO'}, b13=False, post_guest=['FixB13: mode=1'])
ok &= case('v FixB4 not FixB13', 'v', {'FixB13': 'NO'}, b13_lines=['FixB4: mode=1'])
# entry, hold, frames
ok &= case('v other level', 'v', {'entered': 'NO', 'hold >= 300': 'NO', '0 frames >= 1 s': 'NO'}, level='intro_next')
ok &= case('w outcome timeout', 'w', {'entered': 'NO', 'lived to the end': 'NO'}, att={'outcome': 'timeout'})
ok &= case('v hold 300 s - 1 us', 'v', {'hold >= 300': 'NO'}, scene=scene_rows(300) + ['FrameTrace: n=999 dt_us=299 draws=200'])
ok &= case('v hold exactly 300 s', 'v', {}, scene=scene_rows(300) + ['FrameTrace: n=999 dt_us=300 draws=200'])
ok &= case('v first scene draws 99', 'v', {'hold >= 300': 'NO', '0 frames >= 1 s': 'NO'}, first_draws=99,
     scene=['FrameTrace: n=%d dt_us=999999 draws=99' % i for i in range(400)])
ok &= case('v frame 1 000 000 us counted', 'v', {'0 frames >= 1 s': 'NO'}, scene=scene_rows(310, 999999, big=1000000))
ok &= case('v frame 999 999 us not counted', 'v', {}, scene=scene_rows(310, 999999, big=999999) + ['FrameTrace: n=9999 dt_us=999999 draws=200'])
ok &= case('v scene change stops the hold', 'v', {'hold >= 300': 'NO'},
     scene=scene_rows(100, 999999) + ['GuestOut: Level has started: intro_next'] + scene_rows(300, 999999))
ok &= case('v frame after scene change not counted', 'v', {},
     scene=scene_rows(310, 999999) + ['GuestOut: Level has started: intro_next', 'FrameTrace: n=5000 dt_us=5000000 draws=200'])
ok &= case('v hold_exit set', 'v', {'lived through the hold': 'NO'}, att={'hold_exit': 'process ended'})
ok &= case('w hold_s 309.9', 'w', {'lived to the end': 'NO'}, att={'hold_s': 309.9})
ok &= case('w hold_s 310.0', 'w', {}, att={'hold_s': 310.0})
ok &= case('w frames >= 1 s not a gate', 'w', {}, scene=scene_rows(310, 999999, big=2000000))
# death markers
for dm in ('Unhandled exception:', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort:', 'ErrorDeviceLost'):
    ok &= case('v log death %s' % dm, 'v', {'death markers': 'NO'}, tail=[dm + ' x'])
    ok &= case('w stdout death %s' % dm, 'w', {'death markers': 'NO'}, stdout='x\n' + dm + ' y\n')
ok &= case('v no stdout', 'v', {'death markers': 'NOT_READ'}, stdout=None)
# video
ok &= case('v video 3000', 'v', {}, idx=3000)
ok &= case('v video 2999', 'v', {'video index records': 'NO'}, idx=2999)
ok &= case('v video no index', 'v', {'video index records': 'NO'}, idx=None)
ok &= case('v glitch 1', 'v', {'one-frame glitches': 'NO'}, glitch='one-frame glitches: 1')
ok &= case('v no glitch line', 'v', {'one-frame glitches': 'NOT_READ'}, glitch='nothing')
ok &= case('v no sheet', 'v', {'sheet for the lead': 'NO'}, sheet=False)
# layer
ok &= case('w one [Vulkan][E]', 'w', {'0 [Vulkan][E]': 'NO'}, tail=['[Vulkan][E] VUID-x'])
ok &= case('v [Vulkan][E] is a reference in v', 'v', {}, tail=['[Vulkan][E] VUID-x'])
ok &= case('w limit line', 'w', {'0 limit lines': 'NO'}, tail=['... this will be the last time reporting it'])
ok &= case('w no [Vulkan][W]', 'w', {'positive control': 'NO'}, vkw=0)
ok &= case('w no DualSrcBlend', 'w', {'positive control': 'NO'}, dual=False)
ok &= case('w DualSrcBlend enabled=0', 'w', {'positive control': 'NO'}, dual=False, pre=['DualSrcBlend: supported=1 enabled=0'])
ok &= case('w DualSrcBlend after GuestOut', 'w', {'positive control': 'NO'}, dual=False, post_guest=['DualSrcBlend: supported=1 enabled=1'])
ok &= case('w VALIDATION_STOP', 'w', {'0 [Vulkan][E]': 'NO', 'VALIDATION_STOP': 'NO', 'lived to the end': 'NO'},
     tail=['[Vulkan][E] VUID-x'], att={'hold_exit': 'process ended', 'hold_s': 12.0})
ok &= case('w ended early without E', 'w', {'lived to the end': 'NO'}, att={'hold_exit': 'process ended', 'hold_s': 12.0})
# manifest, interference, references
ok &= case('v manifest DIFFER', 'v', {'manifest of the caches': 'NO'}, mc='manifest cmp DIFFER 1')
ok &= case('w manifest missing', 'w', {'manifest of the caches': 'NO'}, mc=None)
ok &= case('v minimized', 'v', {'no interference': 'NO'}, tail=['Window 1 minimized'])
ok &= case('w Recovering', 'w', {'no interference': 'NO'}, tail=['Recovering Vulkan swapchain'])
ok &= case('v GamePatch', 'v', {'no interference': 'NO'}, tail=['GamePatch: x'])
ok &= case('v focus is data', 'v', {}, tail=['Window 1 lost keyboard focus', 'Window 1 restored', 'AsyncPipelines: skipped draw x'])
ok &= case('v savedata differs (report)', 'v', {}, mfrun='_SaveData\tb\ty\n')
ok &= check('v savedata report row', 'equal NO' in LAST[0])
ok &= case('v revision other (reference)', 'v', {}, log=['  version: Fork build arigandores/KytyPS5 0005e11, x'] + base_log('v')[1:])
ok &= check('v revision other REF NO', 'REF revision text names fbae3a6: NO' in LAST[0])
ok &= case('v directory fixf10 (reference)', 'v', {}, log=['Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10'] + base_log('v')[2:])
ok &= check('v directory other REF NO', 'in every line: NO' in LAST[0])
d = make('v', log=None)
rm = rowmap(out_of(d, 'v'))
ok &= check('v no log: FixB13 NO, entered NO, hold NO', key(rm, 'FixB13') == 'NO' and key(rm, 'entered') == 'NO'
            and key(rm, 'hold >= 300') == 'NO')
d = make('w', log=None)
rm = rowmap(out_of(d, 'w'))
ok &= check('w no log: 0 [Vulkan][E] NO, limit NO', key(rm, '0 [Vulkan][E]') == 'NO' and key(rm, '0 limit lines') == 'NO')
# outputs: strict cp1250 without PYTHONIOENCODING, ASCII only, json, unknown tag, repeat tags
d = make('w', tail=['[Vulkan][E] ' + chr(0x442) + chr(0x440)])
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        M.main(['--dir', d, '--form', 'w'])
        M.main(['--dir', d, '--form', 'v'])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
ok &= check('output in strict cp1250 without PYTHONIOENCODING', cp_ok and len(raw.getvalue()) > 1000)
ok &= check('output ASCII only', all(b < 128 for b in raw.getvalue()))
jf = os.path.join(d, 'r.json')
with contextlib.redirect_stdout(io.StringIO()):
    M.main(['--dir', d, '--form', 'w', '--json', jf])
_j = json.load(open(jf))
ok &= check('json written with the form and the members data', _j.get('form') == 'w' and _j.get('vke') == 1 and _j.get('env_ok') is True)
try:
    with contextlib.redirect_stdout(io.StringIO()):
        M.main(['b4_v'])
    refused = False
except SystemExit:
    refused = True
ok &= check('unknown tag refused', refused)
ok &= check('repeat tags map to the base form and their own files', M.base_of('b13_v_r2') == 'b13_v' and M.base_of('b13_w') == 'b13_w'
            and M.paths('b13_w_r1')['log'].replace(chr(92), '/').endswith('f24e/log_b13_w_r1.txt')
            and M.paths('b13_v')['idx'].replace(chr(92), '/').endswith('f24e/rec_b13_v.mp4.idx')
            and M.paths('b13_v')['bin'] == M.BIN_PATH)
_d = make('v')
_orig_paths = M.paths
M.paths = lambda tag=None, base=None: _orig_paths(base=_d)
_forms = []
for _t in ('b13_v', 'b13_w', 'b13_v_r1', 'b13_w_r3'):
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf):
        M.main([_t])
    _forms.append(_buf.getvalue().split(NL)[0].split(' form ')[1].split(' ')[0])
M.paths = _orig_paths
ok &= check('the tag selects the form: b13_v v, b13_w w, repeats by their base (got %s)' % _forms, _forms == ['v', 'w', 'v', 'w'])
shutil.rmtree(str(BASE), ignore_errors=True)

print('checks %d' % N[0])
print('ALL OK' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
