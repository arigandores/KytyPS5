"""Track F link FS8c (HPP-573): fixtures of fs8c_read.py - every row of the seal section 4 and every edge: the three tags positive (READING
MEMBERS_PASS); admission (binary json / installed_sha other or missing, version string of FS7 / no binary file, revision text 302347b /
d6ee2dc / the SDL_REVISION text g0f78a522 / no revision text / the full version string, prereg other / no seal / no json, environment per tag
- every KYTY_FIX_* incl. empty KYTY_FIX_F19, KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS, guest args of another level, V with VK_LAYER_* or
without KYTY_REC or with validation true, W without VK_LAYER_PATH, limit 1000000, filter, KYTY_PIPELINE_PRECACHE, KYTY_REC, validation
false, the last flag wins -, cold form present / missing, interference minimized / Recovering / GamePatch, focus and restored not an
interference); form (installed before / after other or missing, manifest DIFFER / missing; admission before form); members (entry, other
level, directory base / _fixf10 / mixed / no line / slashes / suffix, FixB4 and FixF8 none / two / mode=0 / mode=1 + mode=0 / after the first
GuestOut / no GuestOut = not determined, FixB42 lines not FixB4, a Fix line inside a glued line, hold 300 s / 300 s - 1 us, hold_exit,
outcome timeout, attempt hold_s H - 1 / H, death in log / stdout / no stdout, video 2999 / 3000 / no index, glitch 1 / no line, no sheet,
W [Vulkan][E] / VUID-06479 / [Vulkan][W] 0 / DualSrcBlend after the first GuestOut / enabled=0 / no GuestOut, death in W only REPORT);
REPORT rows never change the word (frames >= 1 s, skipped draw, limit lines, FixB24, FixF8 variant); word order; output ASCII in strict
cp1250 without PYTHONIOENCODING, json, refused tags.  The first output line names the suite and the target with their sha256; the last line
is ALL OK.  ASCII only."""
import hashlib, itertools, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'fs8c_read.py')
sys.path.insert(0, HERE)
import fs8c_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_fs8c_read.py sha256 %s target fs8c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(TARGET)))
OK = True
N = 0
NF = 0
TMP = tempfile.mkdtemp(prefix='fs8c_fx_')
CNT = itertools.count(1)
FIXSHA = R.BIN_EXPECT
INSHA = R.WANT
S12 = 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421'
FS7 = '8df61c009fbe6d7fd7f4e7576e89ab1b0989129336a26f6d1cdf8fd778fbffe7'
STC_FIX = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19'
STC_F10 = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10'
STC_BASE = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b'
LVL = {'fs8_v': 'underwater_aerial_garden', 'fs8_w': 'underwater_aerial_garden', 'fs8_ef': 'enemy_final'}
DUAL = 'DualSrcBlend: supported=1 enabled=1'
COLD = 'cold form: C:/x/variant_fixb26_fixb1b_fixf10_fixf19 absent at 2026-10-05T00:00:00Z; entries of _ShaderCache/PPSA21564: 2'
EQ = 'manifest cmp EQUAL files 3 listsha ab'
DIFF = 'manifest cmp DIFFER only_before 1 only_after 1'
FORK = '  version: Fork build arigandores/KytyPS5 302347b'
SEAL = b'seal text of fs8c\n'
SEALSHA = hashlib.sha256(SEAL).hexdigest()
CMD_V = ['C:\\x\\kyty_emulator.exe', '--vulkan-validation', 'false', '--game', 'x']
CMD_W = CMD_V + ['--vulkan-validation', 'true']


def env_of(tag):
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GATE_FILE': 'g', 'KYTY_SAMPLE_GATE': 's', 'KYTY_QUEUE_TRACE': '1',
         'KYTY_GUEST_ARGS': '-lvl ' + LVL[tag], 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}
    if tag == 'fs8_w':
        e.update(VK_LAYER_PATH='C:/VulkanSDK/1.4.357.0/Bin', VK_LAYER_DUPLICATE_MESSAGE_LIMIT='100000000')
    else:
        e['KYTY_REC'] = 'C:\\kyty\\f287\\fs8c\\rec_%s.mp4' % tag
    return e


def es(tag, outcome='ok', hold_exit=None, hold_s=None, env=None, cmd=None, binary=None, pre=None):
    hold = R.SPEC[tag]['hold']
    return {'binary_sha256': FIXSHA if binary is None else binary, 'env': env_of(tag) if env is None else env,
            'cmdline': (CMD_W if tag == 'fs8_w' else CMD_V) if cmd is None else cmd,
            'prereg': {'sha256': SEALSHA if pre is None else pre},
            'attempts': [{'outcome': outcome, 'detail': None, 'hold_exit': hold_exit, 'hold_s': hold + 0.2 if hold_s is None else hold_s,
                          'stable_s': 40.0, 'close_posted': True, 'close_rc': 0, 'close_killed': False, 'close_s': 3.1, 'close_wait_s': 40}]}


def ft(n, dt, draws):
    return 'FrameTrace: n=%d dt_us=%d draws=%d' % (n, dt, draws)


def scene(tag, hold_us=330000000, step=100000, k2=0):
    out = ['GuestOut: Level has started: ' + LVL[tag], ft(1, 16667, 50), ft(2, 16667, 400)]
    n = 3
    for _ in range(k2):
        out.append(ft(n, 1000000, 400))
        hold_us -= 1000000
        n += 1
    rest = hold_us
    while rest > 0:
        d = min(rest, step)
        out.append(ft(n, d, 400))
        rest -= d
        n += 1
    return out


def head(tag, fix=('FixB4: mode=1', 'FixB24: mode=1', 'FixF8: mode=1'), stc=STC_FIX, fork=FORK):
    h = []
    if fork:
        h.append(fork)
    h += list(fix)
    if tag == 'fs8_w':
        h.append(DUAL)
    if stc:
        h.append(stc)
    h.append('GuestOut: MODL: ')
    if tag == 'fs8_w':
        h.append('[Vulkan][W][2] Validation Warning x')
    return h


def good(tag, **kw):
    return head(tag, **kw) + scene(tag)


def make(name, tag, log, stdout='', run='default', idx=3000, glitch='one-frame glitches: 0', sheet='sheet: x.png frames 3000 step 1 tiles 8x6',
         sha_t=None, before=INSHA, after=INSHA, cold=COLD, mcmp=EQ, seal=SEAL, binf=b'xx' + R.VERSION + b'yy', stdout_file=True):
    d = os.path.join(TMP, '%04d_%s' % (next(CNT), name))
    os.makedirs(d)
    with open(os.path.join(d, 'log.txt'), 'wb') as f:
        f.write(('\n'.join(log) + '\n').encode('utf-8'))
    if stdout_file:
        with open(os.path.join(d, 'stdout.txt'), 'wb') as f:
            f.write(stdout.encode('utf-8'))
    if run == 'default':
        run = es(tag)
    if run is not None:
        with open(os.path.join(d, 'es.json'), 'w') as f:
            json.dump(run, f)
    if idx is not None and tag != 'fs8_w':
        with open(os.path.join(d, 'rec.idx'), 'wb') as f:
            f.write(b'x\n' * idx)
    if seal is not None:
        with open(os.path.join(d, 'seal.md'), 'wb') as f:
            f.write(seal)
    if binf is not None:
        with open(os.path.join(d, 'bin.exe'), 'wb') as f:
            f.write(binf)
    if sha_t is None:
        sha_t = FIXSHA
    if tag == 'fs8_w':
        glitch = sheet = None
    for fn, t in (('glitch.txt', glitch), ('sheet.txt', sheet), ('installed_sha.txt', sha_t), ('installed_before.txt', before),
                  ('installed_after.txt', after), ('cold.txt', cold), ('manifest_cmp.txt', mcmp)):
        if t is not None:
            with open(os.path.join(d, fn), 'wb') as f:
                f.write((t + '\n').encode('utf-8'))
    return d


def rd(d, tag):
    res = R.read(R.paths(tag, d), tag)
    rm = {}
    for line in R.rows(res):
        for cls in ('ADMIT', 'FORM', 'MEMBER', 'REPORT'):
            if line.startswith('  %s ' % cls):
                k, v = line[len(cls) + 3:].rsplit(': ', 1)
                rm[(cls, k)] = v
    return res, rm


def row(rm, cls, prefix):
    hits = [v for (c, k), v in rm.items() if c == cls and k.startswith(prefix)]
    return hits[0] if len(hits) == 1 else 'AMBIGUOUS %d' % len(hits)


def check(name, cond):
    global OK, N, NF
    N += 1
    if not cond:
        OK = False
        NF += 1
        print('FAIL %s' % name)


def word(d, tag):
    return rd(d, tag)[0]['reading']


TAGS = ('fs8_v', 'fs8_w', 'fs8_ef')

# ---- constants
check('constants', R.BIN_EXPECT.startswith('2c9b69b9') and R.WANT.startswith('9325446c') and R.REV == '302347b'
      and R.VERSION == b'KytyPS5-2026-09-15-6a2987a-1889-g302347b4' and R.DIR_FIX == 'variant_fixb26_fixb1b_fixf10_fixf19'
      and len(R.BIN_EXPECT) == 64 and len(R.WANT) == 64 and R.LIMIT == '100000000')
check('spec', R.SPEC['fs8_v'] == dict(kind='v', level='underwater_aerial_garden', hold=330)
      and R.SPEC['fs8_w'] == dict(kind='w', level='underwater_aerial_garden', hold=310)
      and R.SPEC['fs8_ef'] == dict(kind='ef', level='enemy_final', hold=330))
check('paths of a real tag', R.paths('fs8_v')['log'].replace('\\', '/') == 'C:/kyty/f287/fs8c/log_fs8_v.txt'
      and R.paths('fs8_w')['seal'] == R.SEAL_PATH and R.paths('fs8_ef')['bin'] == R.BIN_PATH)

# ---- positive per tag
for t in TAGS:
    d = make(t + '_pos', t, good(t))
    res, rm = rd(d, t)
    check('%s READING MEMBERS_PASS' % t, res['reading'] == 'MEMBERS_PASS')
    check('%s every ADMIT/FORM/MEMBER row YES' % t, all(v == 'YES' for (c, k), v in rm.items() if c != 'REPORT'))
    check('%s every REPORT row YES' % t, all(v == 'YES' for (c, k), v in rm.items() if c == 'REPORT'))
    n_mem = sum(1 for (c, k) in rm if c == 'MEMBER')
    check('%s member count %d' % (t, n_mem), n_mem == 10 if t != 'fs8_w' else n_mem == 9)
    check('%s admission count 7, form count 3' % t, sum(1 for (c, k) in rm if c == 'ADMIT') == 7 and sum(1 for (c, k) in rm if c == 'FORM') == 3)
    check('%s READING line printed last' % t, R.rows(res)[-1] == '  READING MEMBERS_PASS')
    check('%s hold and fix lines' % t, res['hold_us'] == 330000000 and res['fixl']['B4'] == [(2, '1')] and res['first_guest'] == (7 if t == 'fs8_w' else 6))
check('V has video rows, no W rows', any(k.startswith('video index') for (c, k) in rd(make('pv', 'fs8_v', good('fs8_v')), 'fs8_v')[1])
      and not any(k.startswith('0 [Vulkan][E]') for (c, k) in rd(make('pv2', 'fs8_v', good('fs8_v')), 'fs8_v')[1]))
check('W has W rows, no video rows', any(k.startswith('0 [Vulkan][E]') for (c, k) in rd(make('pw', 'fs8_w', good('fs8_w')), 'fs8_w')[1])
      and not any(k.startswith('video index') for (c, k) in rd(make('pw2', 'fs8_w', good('fs8_w')), 'fs8_w')[1]))

# ---- admission: binary
for t in TAGS:
    d = make(t + '_bj', t, good(t), run=es(t, binary=FS7))
    check('%s json binary FS7: NOT_ADMITTED' % t, word(d, t) == 'NOT_ADMITTED')
    d = make(t + '_bi', t, good(t), sha_t=INSHA)
    check('%s installed_sha FS6: NOT_ADMITTED' % t, word(d, t) == 'NOT_ADMITTED')
d = make('v_bj0', 'fs8_v', good('fs8_v'), run=dict(es('fs8_v'), binary_sha256=None))
check('v json binary missing: NOT_ADMITTED', word(d, 'fs8_v') == 'NOT_ADMITTED')
d = make('v_bin7', 'fs8_v', good('fs8_v'), binf=b'xxKytyPS5-2026-09-15-6a2987a-1883-gd6ee2dc8yy')
check('v binary file with the FS7 version string: NOT_ADMITTED', word(d, 'fs8_v') == 'NOT_ADMITTED')
d = make('v_bin0', 'fs8_v', good('fs8_v'), binf=None)
r_, m_ = rd(d, 'fs8_v')
check('v no binary file: version row NO, NOT_ADMITTED', row(m_, 'ADMIT', 'version string') == 'NO' and r_['reading'] == 'NOT_ADMITTED')
d = make('v_binsdl', 'fs8_v', good('fs8_v'), binf=b'xxKytyPS5-2026-09-15-6a2987a-1888-g0f78a522yy')
check('v binary with only the SDL_REVISION string: NOT_ADMITTED', word(d, 'fs8_v') == 'NOT_ADMITTED')
# ---- admission: revision texts (N1)
d = make('v_rev7', 'fs8_v', good('fs8_v', fork='  version: Fork build arigandores/KytyPS5 d6ee2dc'))
check('v revision d6ee2dc: NOT_ADMITTED', word(d, 'fs8_v') == 'NOT_ADMITTED')
d = make('v_revnone', 'fs8_v', good('fs8_v', fork=None))
check('v no revision text: NOT_ADMITTED', word(d, 'fs8_v') == 'NOT_ADMITTED')
d = make('v_revfull', 'fs8_v', good('fs8_v') + ['Release, clang, ver = 0.1, git = KytyPS5-2026-09-15-6a2987a-1889-g302347b4, date = x'])
check('v git = full version string beside: MEMBERS_PASS', word(d, 'fs8_v') == 'MEMBERS_PASS')
d = make('v_revsdl', 'fs8_v', good('fs8_v') + ['Release, clang, ver = 0.1, git = KytyPS5-2026-09-15-6a2987a-1888-g0f78a522, date = x'])
check('v git = SDL_REVISION text g0f78a522: NOT_ADMITTED', word(d, 'fs8_v') == 'NOT_ADMITTED')
d = make('v_revso', 'fs8_v', good('fs8_v'), stdout='  version: Fork build arigandores/KytyPS5 3904522\n')
check('v stdout revision of another build: NOT_ADMITTED', word(d, 'fs8_v') == 'NOT_ADMITTED')
d = make('v_revso2', 'fs8_v', good('fs8_v'), stdout='  version: Fork build arigandores/KytyPS5 302347b\n')
check('v stdout revision 302347b: MEMBERS_PASS', word(d, 'fs8_v') == 'MEMBERS_PASS')
# ---- admission: prereg
d = make('v_pre', 'fs8_v', good('fs8_v'), run=es('fs8_v', pre='0' * 64))
check('v prereg other: NOT_ADMITTED', word(d, 'fs8_v') == 'NOT_ADMITTED')
d = make('v_noseal', 'fs8_v', good('fs8_v'), seal=None)
check('v no seal file: NOT_ADMITTED', word(d, 'fs8_v') == 'NOT_ADMITTED')
d = make('v_sealedit', 'fs8_v', good('fs8_v'), seal=SEAL + b'edit after the run\n')
check('v seal edited after the run: NOT_ADMITTED', word(d, 'fs8_v') == 'NOT_ADMITTED')
d = make('v_nojson', 'fs8_v', good('fs8_v'), run=None)
r_, m_ = rd(d, 'fs8_v')
check('v no json: NOT_ADMITTED, lived row NOT_DETERMINED', r_['reading'] == 'NOT_ADMITTED'
      and row(m_, 'MEMBER', 'the process lived') == 'NOT_DETERMINED')
# ---- admission: environment
for t in TAGS:
    for k, v in (('KYTY_FIX_F19', '1'), ('KYTY_FIX_F19', '0'), ('KYTY_FIX_F19', ''), ('KYTY_FIX_F8', '1'), ('KYTY_FIX_B4', '1'),
                 ('KYTY_FIX_F10', '1'), ('KYTY_GAME_PATCH', 'x'), ('KYTY_GPU_CHECKPOINTS', '')):
        e = env_of(t)
        e[k] = v
        d = make('%s_env_%s_%s' % (t, k, len(v)), t, good(t), run=es(t, env=e))
        check('%s env %s=%r: NOT_ADMITTED' % (t, k, v), word(d, t) == 'NOT_ADMITTED')
    e = env_of(t)
    e['KYTY_GUEST_ARGS'] = '-lvl hoover_beach'
    d = make('%s_env_lvl' % t, t, good(t), run=es(t, env=e))
    check('%s guest args of another level: NOT_ADMITTED' % t, word(d, t) == 'NOT_ADMITTED')
for t in ('fs8_v', 'fs8_ef'):
    e = env_of(t)
    e['VK_LAYER_PATH'] = 'x'
    check('%s V with VK_LAYER_PATH: NOT_ADMITTED' % t, word(make(t + '_vkl', t, good(t), run=es(t, env=e)), t) == 'NOT_ADMITTED')
    e = env_of(t)
    del e['KYTY_REC']
    check('%s V without KYTY_REC: NOT_ADMITTED' % t, word(make(t + '_norec', t, good(t), run=es(t, env=e)), t) == 'NOT_ADMITTED')
    check('%s V with validation true (last flag): NOT_ADMITTED' % t, word(make(t + '_valt', t, good(t), run=es(t, cmd=CMD_W)), t) == 'NOT_ADMITTED')
    check('%s V without the validation flag: NOT_ADMITTED' % t,
          word(make(t + '_valn', t, good(t), run=es(t, cmd=['x', '--game', 'y'])), t) == 'NOT_ADMITTED')
e = env_of('fs8_w')
del e['VK_LAYER_PATH']
check('W without VK_LAYER_PATH: NOT_ADMITTED', word(make('w_nolp', 'fs8_w', good('fs8_w'), run=es('fs8_w', env=e)), 'fs8_w') == 'NOT_ADMITTED')
for k, v in (('VK_LAYER_DUPLICATE_MESSAGE_LIMIT', '1000000'), ('VK_LAYER_MESSAGE_ID_FILTER', 'x'), ('KYTY_PIPELINE_PRECACHE', '0'),
             ('KYTY_REC', 'x')):
    e = env_of('fs8_w')
    e[k] = v
    check('W %s=%s: NOT_ADMITTED' % (k, v), word(make('w_env_' + k, 'fs8_w', good('fs8_w'), run=es('fs8_w', env=e)), 'fs8_w') == 'NOT_ADMITTED')
e = env_of('fs8_w')
del e['VK_LAYER_DUPLICATE_MESSAGE_LIMIT']
check('W without the limit: NOT_ADMITTED', word(make('w_nolim', 'fs8_w', good('fs8_w'), run=es('fs8_w', env=e)), 'fs8_w') == 'NOT_ADMITTED')
check('W validation false only: NOT_ADMITTED', word(make('w_valf', 'fs8_w', good('fs8_w'), run=es('fs8_w', cmd=CMD_V)), 'fs8_w') == 'NOT_ADMITTED')
check('W validation true then false (last wins): NOT_ADMITTED',
      word(make('w_valtf', 'fs8_w', good('fs8_w'), run=es('fs8_w', cmd=CMD_W + ['--vulkan-validation', 'false'])), 'fs8_w') == 'NOT_ADMITTED')
check('W validation true only: MEMBERS_PASS',
      word(make('w_valt1', 'fs8_w', good('fs8_w'), run=es('fs8_w', cmd=['x', '--vulkan-validation', 'true'])), 'fs8_w') == 'MEMBERS_PASS')
# ---- admission: cold form and interference
for t in TAGS:
    check('%s cold present: NOT_ADMITTED' % t, word(make(t + '_warm', t, good(t), cold='cold form: x present at y'), t) == 'NOT_ADMITTED')
    check('%s cold.txt missing: NOT_ADMITTED' % t, word(make(t + '_nocold', t, good(t), cold=None), t) == 'NOT_ADMITTED')
    for nm, extra in (('min', 'Window 1 minimized'), ('rec', 'Recovering Vulkan swapchain'), ('gp', 'GamePatch: loaded x')):
        check('%s interference %s: NOT_ADMITTED' % (t, nm), word(make('%s_int_%s' % (t, nm), t, good(t) + [extra]), t) == 'NOT_ADMITTED')
    d = make(t + '_focus', t, good(t) + ['Window 1 lost keyboard focus', 'Window 1 restored', 'Window 1 resized'])
    r_ = rd(d, t)[0]
    check('%s focus / restored / resized: data, MEMBERS_PASS' % t, r_['reading'] == 'MEMBERS_PASS'
          and r_['win'] == {'lost keyboard focus': 1, 'restored': 1, 'resized': 1})

# ---- form
for t in TAGS:
    check('%s installed before S12: FORM_FAIL' % t, word(make(t + '_bef', t, good(t), before=S12), t) == 'FORM_FAIL')
    check('%s installed before FS8: FORM_FAIL' % t, word(make(t + '_bef8', t, good(t), before=FIXSHA), t) == 'FORM_FAIL')
    check('%s installed after missing: FORM_FAIL' % t, word(make(t + '_aft', t, good(t), after=None), t) == 'FORM_FAIL')
    check('%s installed after FS8: FORM_FAIL' % t, word(make(t + '_aft8', t, good(t), after=FIXSHA), t) == 'FORM_FAIL')
    check('%s manifest DIFFER: FORM_FAIL' % t, word(make(t + '_mdiff', t, good(t), mcmp=DIFF), t) == 'FORM_FAIL')
    check('%s manifest missing: FORM_FAIL' % t, word(make(t + '_mmiss', t, good(t), mcmp=None), t) == 'FORM_FAIL')
    check('%s admission before form' % t, word(make(t + '_order1', t, good(t), mcmp=DIFF, sha_t=INSHA), t) == 'NOT_ADMITTED')
    check('%s form before members' % t, word(make(t + '_order2', t, head(t) + scene(t, 299999999), mcmp=DIFF), t) == 'FORM_FAIL')

# ---- members: entry, directory
for t in TAGS:
    d = make(t + '_noentry', t, head(t) + [ft(1, 400000000, 400)])
    r_, m_ = rd(d, t)
    check('%s no entry: entered NO, hold NO, MEMBERS_FAIL' % t, row(m_, 'MEMBER', 'entered') == 'NO' and row(m_, 'MEMBER', 'hold >= 300 s') == 'NO'
          and r_['reading'] == 'MEMBERS_FAIL')
check('ef log of Sky Garden: MEMBERS_FAIL', word(make('ef_lvl', 'fs8_ef', head('fs8_ef') + scene('fs8_v')), 'fs8_ef') == 'MEMBERS_FAIL')
check('v log of enemy_final: MEMBERS_FAIL', word(make('v_lvl', 'fs8_v', head('fs8_v') + scene('fs8_ef')), 'fs8_v') == 'MEMBERS_FAIL')
for t in TAGS:
    for nm, stc in (('base', STC_BASE), ('f10', STC_F10), ('none', None), ('suffix', STC_FIX + '_x')):
        check('%s dir %s: MEMBERS_FAIL' % (t, nm), word(make('%s_dir_%s' % (t, nm), t, good(t, stc=stc)), t) == 'MEMBERS_FAIL')
    check('%s mixed dir lines: MEMBERS_FAIL' % t, word(make(t + '_dirmix', t, good(t) + [STC_F10]), t) == 'MEMBERS_FAIL')
    check('%s two fixf19 lines: MEMBERS_PASS' % t, word(make(t + '_dir2', t, good(t) + [STC_FIX]), t) == 'MEMBERS_PASS')
    d = make(t + '_dirsl', t, good(t, stc='Shader translation cache: _ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19'))
    check('%s forward slashes: MEMBERS_PASS' % t, word(d, t) == 'MEMBERS_PASS')

# ---- members: Fix lines
FIXSETS = {
    'B4 none': (('FixB24: mode=1', 'FixF8: mode=1'), 'MEMBERS_FAIL'),
    'B4 two': (('FixB4: mode=1', 'FixB4: mode=1', 'FixB24: mode=1', 'FixF8: mode=1'), 'MEMBERS_FAIL'),
    'B4 mode=0': (('FixB4: mode=0', 'FixB24: mode=1', 'FixF8: mode=1'), 'MEMBERS_FAIL'),
    'B4 1 + 0': (('FixB4: mode=1', 'FixB4: mode=0', 'FixB24: mode=1', 'FixF8: mode=1'), 'MEMBERS_FAIL'),
    'B4 other form': (('FixB4: mode=1', 'FixB4: on', 'FixB24: mode=1', 'FixF8: mode=1'), 'MEMBERS_FAIL'),
    'F8 none': (('FixB4: mode=1', 'FixB24: mode=1'), 'MEMBERS_FAIL'),
    'F8 two': (('FixB4: mode=1', 'FixB24: mode=1', 'FixF8: mode=1', 'FixF8: mode=1'), 'MEMBERS_FAIL'),
    'F8 mode=0': (('FixB4: mode=1', 'FixB24: mode=1', 'FixF8: mode=0'), 'MEMBERS_FAIL'),
    'B42 lines only': (('FixB42: mode=1', 'FixB42Ext: x', 'FixB24: mode=1', 'FixF8: mode=1'), 'MEMBERS_FAIL'),
    'B42 lines beside': (('FixB42: mode=1', 'FixB4: mode=1', 'FixB42Ext: x', 'FixB24: mode=1', 'FixF8: mode=1'), 'MEMBERS_PASS'),
    'B24 none (REPORT only)': (('FixB4: mode=1', 'FixF8: mode=1'), 'MEMBERS_PASS'),
    'B24 mode=0 (REPORT only)': (('FixB4: mode=1', 'FixB24: mode=0', 'FixF8: mode=1'), 'MEMBERS_PASS'),
    'glued line': (('[1][00:00:00.000] xFixB4: mode=1', 'FixB24: mode=1', 'FixF8: mode=1 tail'), 'MEMBERS_PASS'),
}
for nm, (fx, want) in FIXSETS.items():
    for t in TAGS:
        check('%s Fix %s: %s' % (t, nm, want), word(make('%s_fx_%s' % (t, nm.replace(' ', '_').replace('=', '').replace('+', 'p')), t,
                                                        good(t, fix=fx)), t) == want)
for t in TAGS:
    lg = head(t, fix=('FixB24: mode=1',)) + ['FixB4: mode=1', 'FixF8: mode=1'] + scene(t)
    r_, m_ = rd(make(t + '_fxlate', t, lg), t)
    check('%s FixB4 and FixF8 after the first GuestOut: both NO, F8 variant YES, MEMBERS_FAIL' % t,
          row(m_, 'MEMBER', 'FixB4') == 'NO' and row(m_, 'MEMBER', 'FixF8') == 'NO' and row(m_, 'REPORT', 'FixF8 by the reading') == 'YES'
          and r_['reading'] == 'MEMBERS_FAIL')
    lg = head(t, fix=('FixB4: mode=1', 'FixB24: mode=1')) + ['FixF8: mode=1'] + scene(t)
    r_, m_ = rd(make(t + '_f8late', t, lg), t)
    check('%s only FixF8 after the first GuestOut: letter NO, variant YES' % t, row(m_, 'MEMBER', 'FixF8') == 'NO'
          and row(m_, 'MEMBER', 'FixB4') == 'YES' and row(m_, 'REPORT', 'FixF8 by the reading') == 'YES' and r_['reading'] == 'MEMBERS_FAIL')
    lg = [x for x in good(t) if not x.startswith('GuestOut')]
    r_, m_ = rd(make(t + '_noguest', t, lg), t)
    check('%s no GuestOut line: Fix NOT_DETERMINED, entered NO -> MEMBERS_FAIL' % t, row(m_, 'MEMBER', 'FixB4') == 'NOT_DETERMINED'
          and row(m_, 'MEMBER', 'FixF8') == 'NOT_DETERMINED' and r_['reading'] == 'MEMBERS_FAIL')
d = make('v_guest_entry_first', 'fs8_v', head('fs8_v', fix=()) [:-1] + scene('fs8_v')[:1] + ['FixB4: mode=1', 'FixF8: mode=1']
         + scene('fs8_v')[1:])
check('v without MODL the entry line is the first GuestOut: Fix after it NO', row(rd(d, 'fs8_v')[1], 'MEMBER', 'FixB4') == 'NO')

# ---- members: hold and process
for t in TAGS:
    check('%s hold 300 s: MEMBERS_PASS' % t, word(make(t + '_h300', t, head(t) + scene(t, 300000000)), t) == 'MEMBERS_PASS')
    check('%s hold 300 s - 1 us: MEMBERS_FAIL' % t, word(make(t + '_h299', t, head(t) + scene(t, 299999999)), t) == 'MEMBERS_FAIL')
    H = R.SPEC[t]['hold']
    check('%s attempt hold_s H - 1: MEMBERS_FAIL' % t, word(make(t + '_hs1', t, good(t), run=es(t, hold_s=H - 1)), t) == 'MEMBERS_FAIL')
    check('%s attempt hold_s H: MEMBERS_PASS' % t, word(make(t + '_hs0', t, good(t), run=es(t, hold_s=H)), t) == 'MEMBERS_PASS')
    check('%s hold_exit: MEMBERS_FAIL' % t, word(make(t + '_hx', t, good(t), run=es(t, hold_exit=5)), t) == 'MEMBERS_FAIL')
    check('%s outcome timeout: MEMBERS_FAIL' % t, word(make(t + '_to', t, good(t), run=es(t, outcome='timeout')), t) == 'MEMBERS_FAIL')
    d = make(t + '_chg', t, head(t) + ['GuestOut: Level has started: ' + LVL[t], ft(1, 1, 50), ft(2, 1, 400), ft(3, 100000000, 400),
                                       'GuestOut: Level has started: other', ft(4, 400000000, 400)])
    r_ = rd(d, t)[0]
    check('%s rows after a scene change not counted' % t, r_['hold_us'] == 100000000 and r_['reading'] == 'MEMBERS_FAIL')
    d = make(t + '_d99', t, head(t) + ['GuestOut: Level has started: ' + LVL[t]] + [ft(i, 100000, 99) for i in range(1, 4000)])
    check('%s draws 99 never a scene frame: hold 0' % t, rd(d, t)[0]['hold_us'] == 0)
    d = make(t + '_d100', t, head(t) + ['GuestOut: Level has started: ' + LVL[t], ft(1, 5, 100)] + [ft(i, 100000, 100) for i in range(2, 3002)])
    check('%s draws 100 is the first scene frame (not counted)' % t, rd(d, t)[0]['hold_us'] == 300000000)

# ---- members: death, video (V and ef)
for t in ('fs8_v', 'fs8_ef'):
    for mk in ('Unhandled exception: x', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort: x', 'ErrorDeviceLost'):
        check('%s death %s in log: MEMBERS_FAIL' % (t, mk[:12]), word(make('%s_dl_%d' % (t, len(mk)), t, good(t) + [mk]), t) == 'MEMBERS_FAIL')
    check('%s death in stdout: MEMBERS_FAIL' % t, word(make(t + '_ds', t, good(t), stdout='--- Fatal Error ---\n'), t) == 'MEMBERS_FAIL')
    r_, m_ = rd(make(t + '_nos', t, good(t), stdout_file=False), t)
    check('%s no stdout: death NOT_DETERMINED, NOT_EVALUABLE' % t, row(m_, 'MEMBER', '0 death markers') == 'NOT_DETERMINED'
          and r_['reading'] == 'NOT_EVALUABLE')
    check('%s video 2999: MEMBERS_FAIL' % t, word(make(t + '_v2999', t, good(t), idx=2999), t) == 'MEMBERS_FAIL')
    check('%s video 3000: MEMBERS_PASS' % t, word(make(t + '_v3000', t, good(t), idx=3000), t) == 'MEMBERS_PASS')
    check('%s no video index: MEMBERS_FAIL' % t, word(make(t + '_vnone', t, good(t), idx=None), t) == 'MEMBERS_FAIL')
    check('%s 1 glitch: MEMBERS_FAIL' % t, word(make(t + '_g1', t, good(t), glitch='one-frame glitches: 1'), t) == 'MEMBERS_FAIL')
    check('%s glitch line missing: NOT_EVALUABLE' % t, word(make(t + '_gm', t, good(t), glitch='nothing'), t) == 'NOT_EVALUABLE')
    check('%s glitch file missing: NOT_EVALUABLE' % t, word(make(t + '_gf', t, good(t), glitch=None), t) == 'NOT_EVALUABLE')
    check('%s no sheet line: MEMBERS_FAIL' % t, word(make(t + '_sh', t, good(t), sheet='error'), t) == 'MEMBERS_FAIL')
    check('%s fail before not evaluable' % t, word(make(t + '_fne', t, good(t), glitch=None, idx=1), t) == 'MEMBERS_FAIL')
    check('%s [Vulkan][E] in V: data only, MEMBERS_PASS' % t, word(make(t + '_vke', t, good(t) + ['[Vulkan][E] x']), t) == 'MEMBERS_PASS')

# ---- members: W
check('W 1 [Vulkan][E]: MEMBERS_FAIL', word(make('w_e', 'fs8_w', good('fs8_w') + ['[Vulkan][E][2] VUID-x']), 'fs8_w') == 'MEMBERS_FAIL')
r_, m_ = rd(make('w_06479', 'fs8_w', good('fs8_w') + ['[Vulkan][E][2] Validation Error: [ VUID-vkCmdDraw-None-06479 ] x']), 'fs8_w')
check('W VUID-06479: counted, MEMBERS_FAIL', r_['vke'] == 1 and r_['vke_06479'] == 1 and r_['reading'] == 'MEMBERS_FAIL')
d = make('w_now', 'fs8_w', [x for x in good('fs8_w') if not x.startswith('[Vulkan][W]')])
check('W 0 [Vulkan][W]: MEMBERS_FAIL', word(d, 'fs8_w') == 'MEMBERS_FAIL')
lg = [x for x in good('fs8_w') if x != DUAL]
lg.insert(lg.index('GuestOut: MODL: ') + 1, DUAL)
check('W DualSrcBlend after the first GuestOut: MEMBERS_FAIL', word(make('w_dlate', 'fs8_w', lg), 'fs8_w') == 'MEMBERS_FAIL')
d = make('w_d0', 'fs8_w', [('DualSrcBlend: supported=1 enabled=0' if x == DUAL else x) for x in good('fs8_w')])
check('W DualSrcBlend enabled=0: MEMBERS_FAIL', word(d, 'fs8_w') == 'MEMBERS_FAIL')
d = make('w_dnone', 'fs8_w', [x for x in good('fs8_w') if x != DUAL])
check('W no DualSrcBlend: MEMBERS_FAIL', word(d, 'fs8_w') == 'MEMBERS_FAIL')
d = make('w_death', 'fs8_w', good('fs8_w') + ['GpuHangAbort: x'])
r_, m_ = rd(d, 'fs8_w')
check('W death: REPORT NO, MEMBERS_PASS', row(m_, 'REPORT', '0 death markers (REPORT for W)') == 'NO' and r_['reading'] == 'MEMBERS_PASS')
d = make('w_lim', 'fs8_w', good('fs8_w') + ['[Vulkan][W][2] x this will be the last time reporting it'])
r_, m_ = rd(d, 'fs8_w')
check('W limit line: REPORT NO, MEMBERS_PASS', row(m_, 'REPORT', 'last-time-reporting') == 'NO' and r_['reading'] == 'MEMBERS_PASS')

# ---- REPORT rows never change the word
for t in TAGS:
    d = make(t + '_k2', t, head(t) + scene(t, 330000000, k2=2))
    r_, m_ = rd(d, t)
    check('%s 2 frames >= 1 s: REPORT NO with the count, MEMBERS_PASS' % t, r_['k2_after'] == 2 and r_['reading'] == 'MEMBERS_PASS'
          and row(m_, 'REPORT', 'frames >= 1 s after the first scene frame = 2') == 'NO')
    d = make(t + '_999', t, head(t) + ['GuestOut: Level has started: ' + LVL[t], ft(1, 1, 50), ft(2, 1, 400), ft(3, 999999, 400)]
             + scene(t)[3:])
    check('%s frame 999 999 us not counted' % t, rd(d, t)[0]['k2_after'] == 0)
    d = make(t + '_k2pre', t, head(t) + ['GuestOut: Level has started: ' + LVL[t], ft(1, 5000000, 50)] + scene(t)[1:])
    check('%s frame >= 1 s before the first scene frame not counted' % t, rd(d, t)[0]['k2_after'] == 0)
    d = make(t + '_skip', t, good(t) + ['AsyncPipelines: skipped draw x'] * 3)
    r_, m_ = rd(d, t)
    check('%s skipped draw 3: REPORT NO, MEMBERS_PASS' % t, r_['skipped_draw'] == 3 and r_['reading'] == 'MEMBERS_PASS')

# ---- output: ASCII and strict cp1250 without PYTHONIOENCODING (non-ASCII bytes in the log)
d = make('enc', 'fs8_v', good('fs8_v') + ['Shader translation cache: \u043a\u044d\u0448', 'x \u0432\u0435\u0440\u0441\u0438\u044f'])
env = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
env['PYTHONIOENCODING'] = 'cp1250:strict'
p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag', 'fs8_v'], capture_output=True, env=env)
check('cp1250 strict: rc 0', p.returncode == 0)
check('cp1250 strict: stdout ASCII only', all(b < 128 for b in p.stdout))
check('cp1250 strict: rows printed', b'MEMBER hold >= 300 s' in p.stdout and b'READING MEMBERS_FAIL' in p.stdout)
env2 = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
p2 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag', 'fs8_v'], capture_output=True, env=env2)
check('no PYTHONIOENCODING: rc 0, ASCII', p2.returncode == 0 and all(b < 128 for b in p2.stdout))
jp = os.path.join(TMP, 'out.json')
d2 = make('json', 'fs8_w', good('fs8_w'))
p3 = subprocess.run([sys.executable, TARGET, '--dir', d2, '--tag', 'fs8_w', '--json', jp], capture_output=True, env=env2)
check('json written', p3.returncode == 0 and json.load(open(jp))['reading'] == 'MEMBERS_PASS')
for bad in (['--dir', d, '--tag', 'f19_v1'], ['--dir', d], ['fs7_h'], ['fs8_x'], []):
    p4 = subprocess.run([sys.executable, TARGET] + bad, capture_output=True, env=env2)
    check('refused %s' % bad, p4.returncode != 0)

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d fails %d' % (N, NF))
print('ALL OK' if OK else 'SOME FAILED')
