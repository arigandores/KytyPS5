"""Track F link FS8e (HPP-575): fixtures of fs8e_read.py - every member, reference and interference row and every edge: the binary
(installed before / of the tag / json = 2c9b69b9; FS7 8df61c00 in each place; missing), the version string in the binary file (FS8 / FS7 /
no file), the revision text (302347b / the full version string / d6ee2dc / the SDL_REVISION text g0f78a522 / none), the directory row (base
_fixf10 / mixed / no line / suffix / forward slashes), FixB4 and FixF8 (none / mode=0 / after the first GuestOut / no GuestOut / FixB42
not FixB4), entered, hold 300 s / 300 s - 1 us, scene change, process end (outcome timeout / hold_exit / hold_s 329 / no json), death
markers in the log / stdout / no stdout, video 3000 / 2999 / missing, glitches 0 / 1 / unread, sheet, the warm form (size > 0 / 0 / absent /
no file), references never decide (cold form, frames >= 1 s, FixB24, the FixF8 variant, skipped draw), interference (minimized /
Recovering / GamePatch / KYTY_FIX_F19 / KYTY_GAME_PATCH / validation true / VK_LAYER_PATH / no KYTY_REC / other level / prereg other ->
INTERFERENCE even when a member fails), the verdict line PASS / FAIL / INTERFERENCE, the sealed import of fs8c_read.py, output in strict
cp1250 without PYTHONIOENCODING, json, other tag refused.  The first output line names the suite and the target with their sha256; the last
line is ALL OK.  ASCII only."""
import copy, hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'fs8e_read.py')
sys.path.insert(0, HERE)
import fs8e_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_fs8e_read.py sha256 %s target fs8e_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(TARGET)))
OK = True
N = 0
NF = 0
TMP = tempfile.mkdtemp(prefix='fs8e_fx_')
FS8 = R.BIN_EXPECT
FS7 = '8df61c009fbe6d7fd7f4e7576e89ab1b0989129336a26f6d1cdf8fd778fbffe7'
SEAL = b'seal fixture text\n'
SEAL_SHA = hashlib.sha256(SEAL).hexdigest()
BIN8 = b'xx KytyPS5-2026-09-15-6a2987a-1889-g302347b4 yy KytyPS5-2026-09-15-6a2987a-1888-g0f78a522 zz'
BIN7 = b'xx KytyPS5-2026-09-15-6a2987a-1883-gd6ee2dc8 yy'
STC_FIX = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19'
STC_BASE = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10'
ENTRY = 'GuestOut: Level has started: underwater_aerial_garden'
COLD = 'cold form: C:/x/variant_fixb26_fixb1b_fixf10_fixf19 absent at 2026-10-05T00:00:00Z; entries of _ShaderCache/PPSA21564: 1347'
WARM = 'warm form after the tag: C:/x/variant_fixb26_fixb1b_fixf10_fixf19 files 400; pipelines.bin present size 3945014 sha256 ab'
FORK = 'Fork build arigandores/KytyPS5 302347b, x'
B4 = 'FixB4: mode=1 x'
F8 = 'FixF8: mode=1 y'
B24 = 'FixB24: mode=1 z'
HEAD = [B4, B24, FORK, STC_FIX, F8, 'GuestOut: boot']
ENV = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden',
       'KYTY_REC': 'C:\\kyty\\f287\\fs8e\\rec_fs8_i.mp4', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}
CMD = ['kyty_emulator.exe', '--vulkan-validation', 'false', '--shader-validation', 'false']
ES = {'binary_sha256': FS8, 'env': ENV, 'cmdline': CMD, 'prereg': {'sha256': SEAL_SHA},
      'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': None, 'hold_s': 330.1, 'stable_s': 30.0}]}


def es(**kw):
    e = copy.deepcopy(ES)
    for k, v in kw.items():
        if k in ('outcome', 'hold_exit', 'hold_s'):
            e['attempts'][0][k] = v
        elif k == 'env_set':
            e['env'].update(v)
        elif k == 'env_del':
            for x in v:
                e['env'].pop(x, None)
        else:
            e[k] = v
    return e


def ft(n, dt, draws):
    return 'FrameTrace: n=%d dt_us=%d draws=%d' % (n, dt, draws)


def scene(hold_us=330000000, step=100000, k2=0, entry=ENTRY):
    out = [entry, ft(1, 16667, 50), ft(2, 16667, 400)]
    n = 3
    for _ in range(k2):
        out.append(ft(n, 1000000, 400))
        hold_us -= 1000000
        n += 1
    while hold_us > 0:
        d = min(hold_us, step)
        out.append(ft(n, d, 400))
        hold_us -= d
        n += 1
    return out


CNT = [0]


def make(log, stdout='', run=None, idx=3000, glitch='one-frame glitches: 0', sheet='sheet: x.png frames 3000 step 1 tiles 8x6',
         sha_t=FS8, before=FS8, cold=COLD, warm=WARM, binb=BIN8, seal=SEAL, norun=False):
    CNT[0] += 1
    d = os.path.join(TMP, 'fx%03d' % CNT[0])
    os.makedirs(d)
    with open(os.path.join(d, 'log.txt'), 'wb') as f:
        f.write(('\n'.join(log) + '\n').encode('utf-8'))
    if stdout is not None:
        with open(os.path.join(d, 'stdout.txt'), 'wb') as f:
            f.write(stdout.encode('utf-8'))
    if not norun:
        with open(os.path.join(d, 'es.json'), 'w') as f:
            json.dump(run if run is not None else ES, f)
    if idx is not None:
        with open(os.path.join(d, 'rec.idx'), 'wb') as f:
            f.write(b'x\n' * idx)
    for fn, t in (('glitch.txt', glitch), ('sheet.txt', sheet), ('installed_sha.txt', sha_t), ('installed_before.txt', before),
                  ('cold.txt', cold), ('warm.txt', warm)):
        if t is not None:
            with open(os.path.join(d, fn), 'wb') as f:
                f.write((t + '\n').encode('utf-8'))
    if binb is not None:
        with open(os.path.join(d, 'bin.exe'), 'wb') as f:
            f.write(binb)
    if seal is not None:
        with open(os.path.join(d, 'seal.md'), 'wb') as f:
            f.write(seal)
    return d


def rm(d):
    res = R.read(R.paths(d))
    out = {}
    lines = R.rows(res)
    for line in lines:
        for pre in ('  MEMBER ', '  REFERENCE ', '  INTERFERENCE '):
            if line.startswith(pre):
                k, v = line[len(pre):].rsplit(': ', 1)
                out[pre.strip() + ' ' + k] = v
    return res, out, lines


def row(m, prefix):
    hits = [v for k, v in m.items() if k.startswith(prefix)]
    return hits[0] if len(hits) == 1 else 'AMBIGUOUS %d' % len(hits)


def check(name, cond):
    global OK, N, NF
    N += 1
    if not cond:
        OK = False
        NF += 1
        print('FAIL %s' % name)


def case(log, prefix, **kw):
    res, m, lines = rm(make(log, **kw))
    return row(m, prefix), lines[-1]


PASSV = 'WARMUP VERDICT fs8_i: PASS'
FAILV = 'WARMUP VERDICT fs8_i: FAIL'
INTV = 'WARMUP VERDICT fs8_i: INTERFERENCE'
ND = 'NOT_DETERMINED'

# ---- constants and the sealed import
check('constants', R.BIN_EXPECT.startswith('2c9b69b9') and R.REV == '302347b' and R.DIR_FIX == 'variant_fixb26_fixb1b_fixf10_fixf19'
      and R.LEVEL == 'underwater_aerial_garden' and R.TAG == 'fs8_i' and R.FORM == 'fs8_v' and R.HOLD == 330
      and R.VERSION == b'KytyPS5-2026-09-15-6a2987a-1889-g302347b4' and R.INSTALLED == 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe')
check('fs8c_read imported from FS8c', R.C.__file__.replace('\\', '/').endswith('f287/fs8c/fs8c_read.py'))
check('paths of the tag', R.paths()['bin'] == R.INSTALLED and R.paths()['seal'] == 'C:/kyty/f287/fs8e/pred/fs8e_seal.md'
      and R.paths()['log'].replace('\\', '/') == 'C:/kyty/f287/fs8e/log_fs8_i.txt')

# ---- positive
res, m, lines = rm(make(HEAD + scene()))
MEM = ('binary', 'version string', 'every revision text', 'translation cache directory', 'FixB4', 'FixF8', 'entered', 'hold >= 300 s',
       'the process lived', '0 death markers', 'video index records', '0 one-frame glitches', 'sheet for the lead', 'warm form after')
for nm in MEM:
    check('pos MEMBER %s YES' % nm, row(m, 'MEMBER ' + nm) == 'YES')
for nm in ('cold form', 'frames >= 1 s after the first scene frame = 0', 'FixB24', 'FixF8 exactly', 'AsyncPipelines'):
    check('pos REFERENCE %s YES' % nm, row(m, 'REFERENCE ' + nm) == 'YES')
for nm in ('window', 'environment', 'json prereg'):
    check('pos INTERFERENCE %s YES' % nm, row(m, 'INTERFERENCE none: ' + nm) == 'YES')
check('pos verdict PASS', lines[-1] == PASSV)
check('pos 14 members, 5 references, 3 interference rows', sum(1 for k in m if k.startswith('MEMBER')) == 14
      and sum(1 for k in m if k.startswith('REFERENCE')) == 5 and sum(1 for k in m if k.startswith('INTERFERENCE')) == 3)
check('no manifest rows (caches not returned)', not any('manifest' in k for k in m))

# ---- binary
for nm, kw in (('before FS7', dict(before=FS7)), ('tag FS7', dict(sha_t=FS7)), ('json FS7', dict(run=es(binary_sha256=FS7))),
               ('before missing', dict(before=None)), ('tag missing', dict(sha_t=None)), ('json missing', dict(run=es(binary_sha256=None)))):
    r_, v_ = case(HEAD + scene(), 'MEMBER binary', **kw)
    check('binary %s: NO, FAIL' % nm, r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER version string', binb=BIN7)
check('version string of FS7: NO, FAIL', r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER version string', binb=None)
check('no binary file: NOT_DETERMINED, FAIL', r_ == ND and v_ == FAILV)
# ---- revision
for nm, fork, want in (('d6ee2dc', 'Fork build arigandores/KytyPS5 d6ee2dc, x', 'NO'),
                       ('SDL text', 'Release, x, git = KytyPS5-2026-09-15-6a2987a-1888-g0f78a522, date', 'NO'),
                       ('full version', 'Release, x, git = KytyPS5-2026-09-15-6a2987a-1889-g302347b4, date', 'YES')):
    r_, v_ = case([B4, B24, fork, STC_FIX, F8, 'GuestOut: b'] + scene(), 'MEMBER every revision text')
    check('revision %s: %s' % (nm, want), r_ == want and v_ == (PASSV if want == 'YES' else FAILV))
r_, v_ = case([B4, B24, STC_FIX, F8, 'GuestOut: b'] + scene(), 'MEMBER every revision text')
check('no revision text: NO, FAIL', r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER every revision text', stdout='Fork build arigandores/KytyPS5 d6ee2dc, x\n')
check('other revision in stdout: NO, FAIL', r_ == 'NO' and v_ == FAILV)
# ---- directory
for nm, log in (('base _fixf10', [B4, B24, FORK, STC_BASE, F8, 'GuestOut: b'] + scene()),
                ('mixed dirs', [B4, B24, FORK, STC_FIX, STC_BASE, F8, 'GuestOut: b'] + scene()),
                ('no dir line', [B4, B24, FORK, F8, 'GuestOut: b'] + scene()),
                ('suffix', [B4, B24, FORK, STC_FIX + '_x', F8, 'GuestOut: b'] + scene())):
    r_, v_ = case(log, 'MEMBER translation cache directory')
    check('dir %s: NO, FAIL' % nm, r_ == 'NO' and v_ == FAILV)
r_, v_ = case([B4, B24, FORK, STC_FIX.replace('\\', '/'), F8, 'GuestOut: b'] + scene(), 'MEMBER translation cache directory')
check('dir forward slashes: YES, PASS', r_ == 'YES' and v_ == PASSV)
# ---- Fix members
for k, line in (('FixB4', B4), ('FixF8', F8)):
    base = [x for x in HEAD if x != line]
    r_, v_ = case(base + scene(), 'MEMBER ' + k)
    check('%s none: NO, FAIL' % k, r_ == 'NO' and v_ == FAILV)
    r_, v_ = case(base[:-1] + [line.replace('mode=1', 'mode=0'), 'GuestOut: b'] + scene(), 'MEMBER ' + k)
    check('%s mode=0: NO, FAIL' % k, r_ == 'NO' and v_ == FAILV)
    r_, v_ = case(base + [line] + scene(), 'MEMBER ' + k)
    check('%s after the first GuestOut: NO, FAIL' % k, r_ == 'NO' and v_ == FAILV)
    r_, v_ = case(base[:-1] + [line, line, 'GuestOut: b'] + scene(), 'MEMBER ' + k)
    check('%s two lines: NO, FAIL' % k, r_ == 'NO' and v_ == FAILV)
r_, v_ = case([B4, B24, FORK, STC_FIX, F8] + scene(entry='Level has started: underwater_aerial_garden'), 'MEMBER FixB4')
check('no GuestOut: FixB4 NOT_DETERMINED, FAIL', r_ == ND and v_ == FAILV)
r_, v_ = case(['FixB42Ext: mode=1', B4, B24, FORK, STC_FIX, F8, 'GuestOut: b'] + scene(), 'MEMBER FixB4')
check('FixB42 line is not FixB4: YES, PASS', r_ == 'YES' and v_ == PASSV)
# ---- entry, hold, process end
r_, v_ = case(HEAD + scene(entry='GuestOut: Level has started: hoover_beach'), 'MEMBER entered')
check('other level: entered NO, FAIL', r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(300000000 - 1), 'MEMBER hold >= 300 s')
check('hold 300 s - 1 us: NO, FAIL', r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(300000000), 'MEMBER hold >= 300 s')
check('hold 300 s: YES, PASS', r_ == 'YES' and v_ == PASSV)
res, m, lines = rm(make(HEAD + [ENTRY, ft(1, 1, 50), ft(2, 1, 400), ft(3, 100000000, 400), 'GuestOut: Level has started: other',
                                ft(4, 400000000, 400)]))
check('scene change: rows after it not counted, FAIL', res['hold_us'] == 100000000 and lines[-1] == FAILV)
for nm, kw, want in (('outcome timeout', dict(outcome='timeout'), 'NO'), ('hold_exit', dict(hold_exit='exit 5'), 'NO'),
                     ('hold_s 329.9', dict(hold_s=329.9), 'NO'), ('hold_s 330', dict(hold_s=330), 'YES')):
    r_, v_ = case(HEAD + scene(), 'MEMBER the process lived', run=es(**kw))
    check('process %s: %s' % (nm, want), r_ == want and v_ == (PASSV if want == 'YES' else FAILV))
r_, v_ = case(HEAD + scene(), 'MEMBER the process lived', norun=True)
check('no run json: NOT_DETERMINED, INTERFERENCE (env not of the form)', r_ == ND and v_ == INTV)
# ---- death
r_, v_ = case(HEAD + scene() + ['GpuHangAbort: x'], 'MEMBER 0 death markers')
check('death in the log: NO, FAIL', r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER 0 death markers', stdout='--- Fatal Error ---\n')
check('death in the stdout: NO, FAIL', r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER 0 death markers', stdout=None)
check('no stdout: NOT_DETERMINED, FAIL', r_ == ND and v_ == FAILV)
# ---- video
for nm, kw in (('2999', dict(idx=2999)), ('no index', dict(idx=None))):
    r_, v_ = case(HEAD + scene(), 'MEMBER video index records', **kw)
    check('video %s: NO, FAIL' % nm, r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER 0 one-frame glitches', glitch='one-frame glitches: 1')
check('1 glitch: NO, FAIL', r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER 0 one-frame glitches', glitch='error')
check('glitch unread: NOT_DETERMINED, FAIL', r_ == ND and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER sheet for the lead', sheet='error')
check('no sheet: NO, FAIL', r_ == 'NO' and v_ == FAILV)
# ---- warm form
for nm, w in (('size 0', 'warm form after the tag: x files 1; pipelines.bin present size 0'),
              ('absent', 'warm form after the tag: x files 0; pipelines.bin ABSENT'), ('no file', None)):
    r_, v_ = case(HEAD + scene(), 'MEMBER warm form after', warm=w)
    check('warm %s: NO, FAIL' % nm, r_ == 'NO' and v_ == FAILV)
# ---- references never decide
r_, v_ = case(HEAD + scene(k2=2), 'REFERENCE frames >= 1 s after the first scene frame = 2')
check('2 frames >= 1 s: reference NO, verdict PASS', r_ == 'NO' and v_ == PASSV)
r_, v_ = case(HEAD + scene(), 'REFERENCE cold form', cold='warm form before: present')
check('cold.txt present: reference NO, PASS', r_ == 'NO' and v_ == PASSV)
r_, v_ = case([x for x in HEAD if x != B24] + scene(), 'REFERENCE FixB24')
check('no FixB24: reference NO, PASS', r_ == 'NO' and v_ == PASSV)
res, m, lines = rm(make(HEAD + scene() + ['AsyncPipelines: skipped draw x'] * 3 + ['Window 1 lost keyboard focus', 'Window 1 restored']))
check('skipped draw, focus, restored: data only, PASS', res['skipped_draw'] == 3 and row(m, 'REFERENCE AsyncPipelines') == 'NO'
      and lines[-1] == PASSV)
# ---- interference
for nm, extra in (('minimized', 'Window 1 minimized'), ('recovering', 'Recovering Vulkan swapchain'), ('gamepatch', 'GamePatch: loaded x')):
    r_, v_ = case(HEAD + scene() + [extra], 'INTERFERENCE none: window')
    check('interference %s: NO, INTERFERENCE' % nm, r_ == 'NO' and v_ == INTV)
for nm, run in (('KYTY_FIX_F19 empty', es(env_set={'KYTY_FIX_F19': ''})), ('KYTY_FIX_F19=0', es(env_set={'KYTY_FIX_F19': '0'})),
                ('KYTY_GAME_PATCH', es(env_set={'KYTY_GAME_PATCH': 'x'})), ('KYTY_GPU_CHECKPOINTS', es(env_set={'KYTY_GPU_CHECKPOINTS': '1'})),
                ('VK_LAYER_PATH', es(env_set={'VK_LAYER_PATH': 'x'})), ('no KYTY_REC', es(env_del=['KYTY_REC'])),
                ('other level', es(env_set={'KYTY_GUEST_ARGS': '-lvl hoover_beach'})),
                ('validation true', es(cmdline=CMD + ['--vulkan-validation', 'true']))):
    r_, v_ = case(HEAD + scene(), 'INTERFERENCE none: environment', run=run)
    check('env %s: NO, INTERFERENCE' % nm, r_ == 'NO' and v_ == INTV)
r_, v_ = case(HEAD + scene(), 'INTERFERENCE none: json prereg', run=es(prereg={'sha256': '0' * 64}))
check('prereg other: NO, INTERFERENCE', r_ == 'NO' and v_ == INTV)
r_, v_ = case(HEAD + scene(), 'INTERFERENCE none: json prereg', seal=None)
check('no seal file: NO, INTERFERENCE', r_ == 'NO' and v_ == INTV)
r_, v_ = case(HEAD + scene() + ['Window 1 minimized'], 'INTERFERENCE none: window', idx=10)
check('interference wins over a failed member', v_ == INTV)

# ---- output: ASCII, strict cp1250 without PYTHONIOENCODING, json, usage
d = make([B4, B24, 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19\\\u043a\u044d\u0448',
          'Release, x, ver = 1, git = \u0432\u0435\u0440\u0441\u0438\u044f, date = y', F8, 'GuestOut: boot'] + scene(),
         stdout='\u043e\u0448\u0438\u0431\u043a\u0430\n')
env = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
env['PYTHONIOENCODING'] = 'cp1250:strict'
p = subprocess.run([sys.executable, TARGET, '--dir', d], capture_output=True, env=env)
check('cp1250 strict: rc 0, ASCII, verdict printed', p.returncode == 0 and all(b < 128 for b in p.stdout) and b'WARMUP VERDICT fs8_i:' in p.stdout)
env2 = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
jp = os.path.join(TMP, 'out.json')
p2 = subprocess.run([sys.executable, TARGET, '--dir', make(HEAD + scene()), '--json', jp], capture_output=True, env=env2)
check('no PYTHONIOENCODING: rc 0, json verdict PASS', p2.returncode == 0 and json.load(open(jp))['verdict'] == 'PASS')
p3 = subprocess.run([sys.executable, TARGET, 'fs8_v'], capture_output=True, env=env2)
check('other tag refused', p3.returncode != 0)

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d fails %d' % (N, NF))
print('ALL OK' if OK else 'SOME FAILED')
