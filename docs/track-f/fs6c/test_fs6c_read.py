"""FS6c (HPP-557): fixtures of fs6c_read.py - every member and edge of the seal docs/track-f/fs6c.md section 4, kinds v and w.
Ends with ALL OK.  Port of C:/kyty/f287/f15e/test_f15e_read.py (kind v) with the W fixtures of FS5c test_fs5c_read.py (kind w).
usage: python test_fs6c_read.py   (ASCII only)"""
import hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'fs6c_read.py')
sys.path.insert(0, HERE)
import fs6c_read as R

print('suite test_fs6c_read.py sha256 %s target fs6c_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(open(TARGET, 'rb').read()).hexdigest()))
N = [0]
FAIL = []


def check(name, cond):
    N[0] += 1
    if not cond:
        FAIL.append(name)
        print('FAIL', name)


GUEST = 'GuestOut: Level has started: underwater_aerial_garden'
DUAL = 'DualSrcBlend: supported=1 enabled=1'


def base_log(kind='v', hold_frames=310, dt=1000000 - 1, extra_after=None, b4=('FixB4: mode=1',), quit=True, before=None, dual=True,
             vkw=True):
    L = ['  version: Fork build arigandores/KytyPS5 3904522', 'Shader translation cache: _ShaderCache\\PPSA21564\\' + R.DIR_FIX]
    L += list(b4)
    if dual:
        L.append(DUAL)
    L += before or []
    L += ['GuestOut: something', GUEST, 'FrameTrace: n=1 dt_us=16000 draws=50', 'FrameTrace: n=2 dt_us=16000 draws=100']
    if kind == 'w' and vkw:
        L.append('[Vulkan][W] Validation Warning: x')
    for i in range(hold_frames):
        L.append('FrameTrace: n=%d dt_us=%d draws=3000' % (i + 3, dt))
    if quit:
        L += ['Window 1 closed', 'Event: quit']
    L += extra_after or []
    L += ['PipelinePrecache: saved 1 recipes (1 bytes)']
    return L


def run_json(**att):
    a = dict(outcome='ok', hold_exit=None, hold_s=330.0, close_posted=1, close_rc=0, close_killed=False, close_s=2.1, close_wait_s=40)
    a.update(att)
    return dict(env={'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_REC': 'x'}, attempts=[a])


MF = ['_SaveData\tPPSA21564/sce_sdmemory/memory.bin\t10\taaa', '_ShaderCache\tx\t1\tbbb']


def make(d, kind='v', log=None, stdout=None, run=None, files=None, drop=()):
    os.makedirs(d, exist_ok=True)
    f = dict(installed_sha=R.BIN_EXPECT, installed_before=R.WANT, installed_after=R.WANT,
             warm='warm form: C:/x/' + R.DIR_FIX + ' present at 2026-10-04T12:00:00Z; entries 5',
             manifest_cmp='manifest cmp EQUAL files 2 listsha abc')
    if kind == 'v':
        f.update(glitch='one-frame glitches: 0', sheet='sheet: x.png frames 3100')
    files = dict(files or {})
    mf_run = files.pop('_mf_run', MF)
    f.update(files)
    for k, v in f.items():
        if k not in drop:
            open(os.path.join(d, k + '.txt'), 'w').write(v + '\n')
    if 'log' not in drop:
        open(os.path.join(d, 'log.txt'), 'wb').write(('\n'.join(log if log is not None else base_log(kind)) + '\n').encode())
    if 'stdout' not in drop:
        open(os.path.join(d, 'stdout.txt'), 'wb').write(('\n'.join(stdout or ['Shaders: VS 1']) + '\n').encode())
    if 'run' not in drop:
        open(os.path.join(d, 'es.json'), 'w').write(json.dumps(run if run is not None else run_json()))
    if kind == 'v' and 'idx' not in drop:
        open(os.path.join(d, 'rec.idx'), 'w').write('r\n' * 3100)
    if 'mf_before' not in drop:
        open(os.path.join(d, 'manifest_before.tsv'), 'w').write('\n'.join(MF) + '\n')
    if 'mf_run' not in drop:
        open(os.path.join(d, 'manifest_run.tsv'), 'w').write('\n'.join(mf_run) + '\n')
    if 'bin' not in drop:
        open(os.path.join(d, 'bin.exe'), 'wb').write(b'MZ\x00' + R.VERSION + b'\x00')
    return d


def rowmap(d, kind='v'):
    res = R.read(R.paths('fixture', kind, d), kind)
    out = R.rows('fixture', res)
    m = {}
    for x in out:
        x = x.strip()
        if x.startswith('ROW '):
            k, v = x[4:].rsplit(': ', 1)
            m[k] = v
    return m, res, out


K = dict(sha='binary sha256 of the tag = 9325446c (FS6 copy)', ver='version string ...-1879-g3904522d in the tag binary',
         before='installed adb0c82f before the tag', after='installed adb0c82f after the return',
         env='env: no KYTY_FIX_*, no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS (defaults of the binary)',
         rev='revision text names 3904522 (reference)',
         dir='translation cache directory %s in every line (reference)' % R.DIR_FIX,
         warm='warm form: %s present before the start (reference)' % R.DIR_FIX,
         b4='FixB4: mode=1 (every line) before the first GuestOut', entry='entered (entry line of underwater_aerial_garden)',
         hold='hold >= 300 s after the first scene frame', lived='the process lived through the hold (outcome ok, hold_exit null)',
         manifest='manifest of the caches, saves and GLCache before = after the return',
         interf='no interference: window minimized / Recovering Vulkan swapchain / GamePatch line (else not read as an outcome, question '
                'to the lead)')
KV = dict(death='0 death markers (log and stdout)', video='video index records >= 3000', glitch='0 one-frame glitches',
          sheet='sheet for the lead made', quit='exit by the harness: Event: quit line in the log',
          after_quit='after Event: quit: 0 --- Fatal Error --- and 0 m_files[index] == nullptr (log)',
          end='the process ended before the harness timeout (40 s after WM_CLOSE, not killed)')
KW = dict(vke='0 [Vulkan][E]', vkw='positive control of the layer, [Vulkan][W] > 0',
          dual='DualSrcBlend supported=1 enabled=1 before the first GuestOut', death='0 death markers (reference)',
          quit='exit by the harness: Event: quit line in the log (reference)',
          after_quit='after Event: quit: 0 --- Fatal Error --- and 0 m_files[index] == nullptr (reference)',
          end='the process ended before the harness timeout (reference)')


def k2key(n):
    return 'frames >= 1 s after the first scene frame = %d (REPORT, not a gate)' % n


T = tempfile.mkdtemp(prefix='fs6c_fx_')
try:
    c = [0]

    def case(kind='v', **kw):
        c[0] += 1
        return make(os.path.join(T, 'c%03d' % c[0]), kind=kind, **kw)

    # constants of the seal
    check('const BIN_EXPECT FS6', R.BIN_EXPECT == '9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2')
    check('const WANT S12', R.WANT == 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421')
    check('const VERSION', R.VERSION == b'KytyPS5-2026-09-15-6a2987a-1879-g3904522d')
    check('const kinds', R.KINDS == ('v', 'w') and R.kind_of('fs6_v') == 'v' and R.kind_of('fs6_w') == 'w')
    check('const hold 300 s, video 3000, K2 1 s', R.HOLD_MIN_US == 300000000 and R.VIDEO_MIN == 3000 and R.K2_US == 1000000)
    # positive, both kinds
    for kind, extra in (('v', KV), ('w', KW)):
        m, res, out = rowmap(case(kind), kind)
        for k in list(K.values()) + list(extra.values()):
            check('positive %s %s' % (kind, k), m.get(k) == 'YES')
        check('positive %s k2 row' % kind, m.get(k2key(0)) == 'YES')
        check('positive %s row count' % kind, len(m) == len(K) + len(extra) + 1)
        check('positive %s hold s' % kind, abs(res['hold_s'] - 310 * 0.999999) < 0.2)
        check('positive %s exit code line' % kind, any('exit code 0 (0x00000000)' in x for x in out))
        check('positive %s savedata equal' % kind, res['savedata']['equal'] is True and res['savedata']['before'] == 1)
    m, _, out = rowmap(case('w'), 'w')
    check('w has no video rows', not any(x.strip().startswith('video:') for x in out) and KV['video'] not in m)
    m, _, out = rowmap(case('v'), 'v')
    check('v has no W member rows', KW['vke'] not in m and KW['vkw'] not in m and KW['dual'] not in m)
    # binary rows
    for kind in ('v', 'w'):
        m, _, _ = rowmap(case(kind, files=dict(installed_sha='0' * 64)), kind)
        check('%s tag sha other -> NO' % kind, m[K['sha']] == 'NO')
    m, _, _ = rowmap(case(files=dict(installed_sha='907569f641bfea9fb9881213b77588a2c8365a084512e5ef734baf5aae82aff1')))
    check('tag sha F15c -> NO', m[K['sha']] == 'NO')
    m, _, _ = rowmap(case(files=dict(installed_sha=R.WANT)))
    check('tag sha = installed S12 -> NO', m[K['sha']] == 'NO')
    m, _, _ = rowmap(case(drop=('installed_sha',)))
    check('tag sha missing -> NO', m[K['sha']] == 'NO')
    d = case()
    open(os.path.join(d, 'bin.exe'), 'wb').write(b'MZ KytyPS5-2026-09-15-6a2987a-1878-g5c2c5e52')
    m, _, _ = rowmap(d)
    check('version of F15c -> NO', m[K['ver']] == 'NO')
    d = case()
    open(os.path.join(d, 'bin.exe'), 'wb').write(b'MZ KytyPS5-2026-09-15-6a2987a-1877-g4d9e8ab7')
    m, _, _ = rowmap(d)
    check('version of S12 -> NO', m[K['ver']] == 'NO')
    m, _, _ = rowmap(case(drop=('bin',)))
    check('binary file missing -> NOT_READ', m[K['ver']] == 'NOT_READ')
    m, _, _ = rowmap(case(files=dict(installed_before='631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17')))
    check('installed before FS5 -> NO', m[K['before']] == 'NO')
    m, _, _ = rowmap(case(files=dict(installed_after=R.BIN_EXPECT)))
    check('installed after = tag binary (FS6 left installed) -> NO', m[K['after']] == 'NO')
    m, _, _ = rowmap(case(drop=('installed_after',)))
    check('installed after missing -> NO', m[K['after']] == 'NO')
    # env: defaults of the binary
    for kind in ('v', 'w'):
        r = run_json(); r['env']['KYTY_FIX_B4'] = '1'
        m, _, _ = rowmap(case(kind, run=r), kind)
        check('%s env KYTY_FIX_B4=1 passed -> NO' % kind, m[K['env']] == 'NO')
    r = run_json(); r['env']['KYTY_FIX_B4'] = '0'
    m, _, _ = rowmap(case(run=r))
    check('env KYTY_FIX_B4=0 -> NO', m[K['env']] == 'NO')
    r = run_json(); r['env']['KYTY_FIX_B4'] = ''
    m, _, _ = rowmap(case(run=r))
    check('env KYTY_FIX_B4 empty -> NO', m[K['env']] == 'NO')
    r = run_json(); r['env']['KYTY_FIX_F10'] = '1'
    m, _, _ = rowmap(case(run=r))
    check('env other KYTY_FIX -> NO', m[K['env']] == 'NO')
    r = run_json(); r['env']['KYTY_GAME_PATCH'] = 'p.txt'
    m, _, _ = rowmap(case(run=r))
    check('env GAME_PATCH -> NO', m[K['env']] == 'NO')
    r = run_json(); r['env']['KYTY_GPU_CHECKPOINTS'] = '0'
    m, _, _ = rowmap(case(run=r))
    check('env GPU_CHECKPOINTS present -> NO', m[K['env']] == 'NO')
    r = run_json(); r['env']['KYTY_FIXB4'] = '1'
    m, _, _ = rowmap(case(run=r))
    check('env KYTY_FIXB4 (not a KYTY_FIX_ name) -> YES', m[K['env']] == 'YES')
    r = run_json(); r['env']['VK_LAYER_PATH'] = 'C:/x'; r['env']['VK_LAYER_DUPLICATE_MESSAGE_LIMIT'] = '100000000'
    m, _, _ = rowmap(case('w', run=r), 'w')
    check('w env VK_LAYER_* -> env YES', m[K['env']] == 'YES')
    m, _, _ = rowmap(case(drop=('run',)))
    check('no run json -> env NOT_READ', m[K['env']] == 'NOT_READ')
    check('no run json -> lived NOT_READ', m[K['lived']] == 'NOT_READ')
    check('no run json -> end NOT_READ', m[KV['end']] == 'NOT_READ')
    # revision (reference)
    L = base_log(); L[0] = '  version: Fork build arigandores/KytyPS5 5c2c5e5'
    m, _, _ = rowmap(case(log=L))
    check('revision of F15c -> NO', m[K['rev']] == 'NO')
    L = base_log(); L[0] = '  version: KytyPS5, git = 3904522d, x'
    m, _, _ = rowmap(case(log=L))
    check('revision git form -> YES', m[K['rev']] == 'YES')
    m, _, _ = rowmap(case(log=base_log()[1:]))
    check('revision absent -> NOT_PRESENT', m[K['rev']] == 'NOT_PRESENT')
    # directory and warm (reference)
    L = base_log(); L[1] = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b'
    m, _, _ = rowmap(case(log=L))
    check('directory base -> NO', m[K['dir']] == 'NO')
    L = base_log(); L.insert(2, 'Shader translation cache: _ShaderCache/PPSA21564/' + R.DIR_FIX)
    m, _, _ = rowmap(case(log=L))
    check('directory forward slashes -> YES', m[K['dir']] == 'YES')
    L = base_log(); L[1] = 'Shader translation cache: _ShaderCache\\PPSA21564\\' + R.DIR_FIX + '_fixf19'
    m, _, _ = rowmap(case(log=L))
    check('directory suffix -> NO', m[K['dir']] == 'NO')
    L = base_log(); del L[1]
    m, _, _ = rowmap(case(log=L))
    check('directory no line -> NO', m[K['dir']] == 'NO')
    m, _, _ = rowmap(case(files=dict(warm='warm form: C:/x/' + R.DIR_FIX + ' absent at 2026')))
    check('warm absent -> NO', m[K['warm']] == 'NO')
    m, _, _ = rowmap(case(drop=('warm',)))
    check('warm.txt missing -> NO', m[K['warm']] == 'NO')
    # FixB4, both kinds
    for kind in ('v', 'w'):
        m, _, _ = rowmap(case(kind, log=base_log(kind, b4=('FixB4: mode=0',))), kind)
        check('%s FixB4 mode=0 -> NO' % kind, m[K['b4']] == 'NO')
        m, _, _ = rowmap(case(kind, log=base_log(kind, b4=())), kind)
        check('%s FixB4 no line -> NO' % kind, m[K['b4']] == 'NO')
        L = base_log(kind, b4=()); i = L.index('GuestOut: something'); L.insert(i + 1, 'FixB4: mode=1')
        m, _, _ = rowmap(case(kind, log=L), kind)
        check('%s FixB4 after the first GuestOut -> NO' % kind, m[K['b4']] == 'NO')
    m, _, _ = rowmap(case(log=base_log(b4=('FixB4: mode=1', 'FixB4: mode=0'))))
    check('FixB4 second line mode=0 -> NO', m[K['b4']] == 'NO')
    m, _, _ = rowmap(case(log=base_log(b4=('FixB4: mode=1', 'FixB4: mode=1'))))
    check('FixB4 two lines mode=1 -> YES', m[K['b4']] == 'YES')
    m, _, _ = rowmap(case(log=base_log(b4=('FixB4: mode=10',))))
    check('FixB4 mode=10 -> NO', m[K['b4']] == 'NO')
    # entry / hold
    for kind in ('v', 'w'):
        L = base_log(kind); L[L.index(GUEST)] = 'GuestOut: Level has started: hoover_beach'
        m, _, _ = rowmap(case(kind, log=L), kind)
        check('%s entry other level -> NO' % kind, m[K['entry']] == 'NO' and m[K['hold']] == 'NO')
        m, res, _ = rowmap(case(kind, log=base_log(kind, hold_frames=300, dt=1000000 - 1)), kind)
        check('%s hold 300 s - 300 us -> NO' % kind, m[K['hold']] == 'NO')
    L = base_log(hold_frames=299, dt=999999); i = L.index('Window 1 closed'); L.insert(i, 'FrameTrace: n=999 dt_us=1000299 draws=3000')
    m, res, _ = rowmap(case(log=L))
    check('hold exactly 300 s -> YES', m[K['hold']] == 'YES' and res['hold_us'] == 300000000)
    check('hold exactly 300 s with a 1 s frame -> k2 row NO', m.get(k2key(1)) == 'NO')
    L = base_log(hold_frames=299, dt=999999); i = L.index('Window 1 closed'); L.insert(i, 'FrameTrace: n=999 dt_us=1000298 draws=3000')
    m, res, _ = rowmap(case(log=L))
    check('hold 300 s - 1 us -> NO', m[K['hold']] == 'NO' and res['hold_us'] == 300000000 - 1)
    m, res, _ = rowmap(case(log=base_log(hold_frames=310, dt=999999)))
    check('999 999 us is not a frame >= 1 s', res['k2_after'] == 0)
    L = base_log(); i = L.index('Window 1 closed'); L.insert(i, 'FrameTrace: n=998 dt_us=1000000 draws=3000')
    m, res, _ = rowmap(case(log=L))
    check('1 000 000 us is a frame >= 1 s, hold kept', res['k2_after'] == 1 and m.get(k2key(1)) == 'NO' and m[K['hold']] == 'YES')
    L = base_log(hold_frames=100); i = L.index('Window 1 closed')
    L[i:i] = ['GuestOut: Level has started: hub'] + ['FrameTrace: n=%d dt_us=999999 draws=3000' % (j + 500) for j in range(250)]
    m, res, _ = rowmap(case(log=L))
    check('scene change ends the hold -> NO', m[K['hold']] == 'NO' and res['scene_change_line'] is not None)
    L = base_log(); L[L.index('FrameTrace: n=2 dt_us=16000 draws=100')] = 'FrameTrace: n=2 dt_us=16000 draws=99'
    m, res, _ = rowmap(case(log=L))
    check('draws 99 is not the first scene frame', res['first_scene_n'] == 3)
    for kind in ('v', 'w'):
        m, _, _ = rowmap(case(kind, run=run_json(hold_exit=3221225477)), kind)
        check('%s process ended inside the hold -> lived NO' % kind, m[K['lived']] == 'NO')
        m, _, _ = rowmap(case(kind, run=run_json(outcome='timeout')), kind)
        check('%s outcome timeout -> lived NO' % kind, m[K['lived']] == 'NO')
    # death markers: member of v, reference of w
    for d_ in R.DEATH:
        m, _, _ = rowmap(case(log=base_log(before=[d_.decode() + ' x'])))
        check('v death in log %s -> NO' % d_.decode(), m[KV['death']] == 'NO')
        m, _, _ = rowmap(case(stdout=[d_.decode() + ' x']))
        check('v death in stdout %s -> NO' % d_.decode(), m[KV['death']] == 'NO')
    m, _, _ = rowmap(case('w', log=base_log('w', before=['ErrorDeviceLost'])), 'w')
    check('w death -> reference NO', m[KW['death']] == 'NO')
    m, _, _ = rowmap(case('w', stdout=['--- Fatal Error --- x']), 'w')
    check('w death in stdout -> reference NO', m[KW['death']] == 'NO')
    # video (v)
    d = case(); open(os.path.join(d, 'rec.idx'), 'w').write('r\n' * 3000)
    m, _, _ = rowmap(d)
    check('video 3000 -> YES', m[KV['video']] == 'YES')
    d = case(); open(os.path.join(d, 'rec.idx'), 'w').write('r\n' * 2999)
    m, _, _ = rowmap(d)
    check('video 2999 -> NO', m[KV['video']] == 'NO')
    m, _, _ = rowmap(case(drop=('idx',)))
    check('no video index -> NO', m[KV['video']] == 'NO')
    m, _, _ = rowmap(case(files=dict(glitch='one-frame glitches: 1')))
    check('glitch 1 -> NO', m[KV['glitch']] == 'NO')
    m, _, _ = rowmap(case(files=dict(glitch='error')))
    check('no glitch line -> NOT_READ', m[KV['glitch']] == 'NOT_READ')
    m, _, _ = rowmap(case(drop=('sheet',)))
    check('no sheet -> NO', m[KV['sheet']] == 'NO')
    # quit and after quit (v members; w reference)
    m, _, _ = rowmap(case(log=base_log(quit=False)))
    check('no Event: quit -> quit NO', m[KV['quit']] == 'NO')
    check('no Event: quit -> after-quit NOT_READ', m[KV['after_quit']] == 'NOT_READ')
    m, res, _ = rowmap(case(log=base_log(extra_after=['--- Fatal Error ---'])))
    check('fatal after quit -> NO', m[KV['after_quit']] == 'NO' and res['fatal_after_quit'] == 1)
    check('fatal after quit -> death NO too', m[KV['death']] == 'NO')
    m, res, _ = rowmap(case(log=base_log(extra_after=['[E] fileSystem.cpp:228: EXIT_IF(m_files[index] == nullptr)'])))
    check('m_files nullptr after quit -> NO', m[KV['after_quit']] == 'NO' and res['null_after_quit'] == 1)
    check('m_files nullptr alone -> death YES (not a death marker)', m[KV['death']] == 'YES')
    m, res, _ = rowmap(case(log=base_log(before=['m_files[index] == nullptr'])))
    check('m_files nullptr before quit -> after-quit YES, total 1', m[KV['after_quit']] == 'YES' and res['null_log_total'] == 1)
    m, res, _ = rowmap(case(log=base_log(before=['--- Fatal Error ---'])))
    check('fatal before quit -> after-quit YES, death NO', m[KV['after_quit']] == 'YES' and res['fatal_after_quit'] == 0
          and res['fatal_log_total'] == 1 and m[KV['death']] == 'NO')
    m, res, _ = rowmap(case(stdout=['m_files[index] == nullptr', '--- Fatal Error ---']))
    check('stdout counts printed', res['null_stdout'] == 1 and res['fatal_stdout'] == 1)
    L = base_log(); L.append('Event: quit'); L.append('--- Fatal Error ---')
    m, res, _ = rowmap(case(log=L))
    check('second quit line: counted after the first', res['fatal_after_quit'] == 1 and m[KV['after_quit']] == 'NO')
    m, _, _ = rowmap(case('w', log=base_log('w', quit=False)), 'w')
    check('w no Event: quit -> reference NO, after NOT_READ', m[KW['quit']] == 'NO' and m[KW['after_quit']] == 'NOT_READ')
    m, _, _ = rowmap(case('w', log=base_log('w', extra_after=['m_files[index] == nullptr'])), 'w')
    check('w m_files after quit -> reference NO', m[KW['after_quit']] == 'NO')
    # exit
    m, _, out = rowmap(case(run=run_json(close_killed=True, close_rc=1)))
    check('killed -> end NO', m[KV['end']] == 'NO')
    m, _, out = rowmap(case(run=run_json(close_rc=None)))
    check('rc None (alive) -> end NO', m[KV['end']] == 'NO')
    m, _, out = rowmap(case(run=run_json(close_rc=321)))
    check('rc 321 not killed -> end YES (exit code is a report row)', m[KV['end']] == 'YES')
    check('rc 321 printed hex', any('exit code 321 (0x00000141)' in x for x in out))
    m, _, out = rowmap(case(run=run_json(close_rc=-1073740940)))
    check('negative rc printed hex', any('(0xc0000374)' in x for x in out))
    r = run_json(); del r['attempts'][0]['close_killed']
    m, _, _ = rowmap(case(run=r))
    check('no close record -> end NOT_READ', m[KV['end']] == 'NOT_READ')
    m, _, _ = rowmap(case('w', run=run_json(close_killed=True, close_rc=1)), 'w')
    check('w killed -> end reference NO', m[KW['end']] == 'NO')
    # W rows
    m, _, _ = rowmap(case('w', log=base_log('w', before=['[Vulkan][E] VUID-x'])), 'w')
    check('w 1 [Vulkan][E] -> NO', m[KW['vke']] == 'NO')
    m, _, _ = rowmap(case('w', log=base_log('w', vkw=False)), 'w')
    check('w 0 [Vulkan][W] -> positive control NO', m[KW['vkw']] == 'NO')
    L = base_log('w', dual=False); i = L.index('GuestOut: something'); L.insert(i + 1, DUAL)
    m, _, _ = rowmap(case('w', log=L), 'w')
    check('w DualSrcBlend after the first GuestOut -> NO', m[KW['dual']] == 'NO')
    m, _, _ = rowmap(case('w', log=base_log('w', dual=False, before=['DualSrcBlend: supported=1 enabled=0'])), 'w')
    check('w DualSrcBlend enabled=0 -> NO', m[KW['dual']] == 'NO')
    m, _, _ = rowmap(case('w', log=base_log('w', dual=False, before=['DualSrcBlend: supported=0 enabled=0'])), 'w')
    check('w DualSrcBlend supported=0 -> NO', m[KW['dual']] == 'NO')
    m, _, _ = rowmap(case('w', log=base_log('w', dual=False)), 'w')
    check('w no DualSrcBlend line -> NO', m[KW['dual']] == 'NO')
    m, res, out = rowmap(case('w', log=base_log('w', before=['x: this will be the last time reporting it'])), 'w')
    check('w last-time-reporting counted (reference, rows YES)', res['vk_limit'] == 1 and m[KW['vke']] == 'YES')
    m, res, _ = rowmap(case(log=base_log(before=['[Vulkan][E] x'])))
    check('v [Vulkan][E] -> no member row in v', res['vke'] == 1 and all(v == 'YES' for v in m.values()))
    # _SaveData report
    mf2 = ['_SaveData\tPPSA21564/sce_sdmemory/memory.bin\t10\tccc', '_ShaderCache\tx\t1\tbbb']
    m, res, out = rowmap(case(files=dict(_mf_run=mf2)))
    check('savedata differ -> report, rows unchanged', res['savedata']['equal'] is False and all(v == 'YES' for v in m.values()))
    check('savedata differ printed', any('equal NO' in x and 'memory.bin' in x for x in out))
    m, res, _ = rowmap(case(drop=('mf_run',)))
    check('savedata run manifest missing -> NOT_READ', res['savedata']['equal'] is None)
    # manifest
    for kind in ('v', 'w'):
        m, _, _ = rowmap(case(kind, files=dict(manifest_cmp='manifest cmp DIFFER only-before 1 only-after 1')), kind)
        check('%s manifest DIFFER -> NO' % kind, m[K['manifest']] == 'NO')
        m, _, _ = rowmap(case(kind, drop=('manifest_cmp',)), kind)
        check('%s manifest missing -> NO' % kind, m[K['manifest']] == 'NO')
    # interference and data
    for kind in ('v', 'w'):
        for line, want in (('Window 1 minimized', 'NO'), ('Recovering Vulkan swapchain', 'NO'), ('GamePatch: x', 'NO'),
                           ('Window 1 lost keyboard focus', 'YES'), ('Window 1 restored', 'YES'),
                           ('AsyncPipelines: skipped draw 1', 'YES')):
            m, _, _ = rowmap(case(kind, log=base_log(kind, before=[line])), kind)
            check('%s interference %s -> %s' % (kind, line, want), m[K['interf']] == want)
    # missing log
    m, res, _ = rowmap(case(drop=('log',)))
    check('no log -> entry NO, quit NO', m[K['entry']] == 'NO' and m[KV['quit']] == 'NO' and res['log_sha256'] is None)
    # CLI: strict cp1250 without PYTHONIOENCODING, ASCII only, json, unknown tag / kind
    for kind in ('v', 'w'):
        d = case(kind)
        env = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
        env['PYTHONIOENCODING'] = 'cp1250:strict'
        p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', kind], capture_output=True, env=env)
        check('%s cli cp1250 strict rc 0' % kind, p.returncode == 0)
        check('%s cli ASCII only' % kind, all(b < 128 for b in p.stdout))
        check('%s cli has ROW lines' % kind, p.stdout.count(b'  ROW ') == len(K) + 7 + 1)
        env2 = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
        p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', kind], capture_output=True, env=env2)
        check('%s cli without PYTHONIOENCODING rc 0' % kind, p.returncode == 0)
    jp = os.path.join(T, 'o.json')
    p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'w', '--json', jp], capture_output=True)
    check('cli json written', p.returncode == 0 and json.load(open(jp))['b4_ok'] is True and json.load(open(jp))['dual_ok'] is True)
    p = subprocess.run([sys.executable, TARGET, 'b4_v'], capture_output=True)
    check('cli unknown tag refused', p.returncode != 0 and b'unknown tag' in p.stderr)
    p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'r1'], capture_output=True)
    check('cli unknown kind refused', p.returncode != 0 and b'unknown kind' in p.stderr)
finally:
    shutil.rmtree(T, ignore_errors=True)

print('checks %d failed %d' % (N[0], len(FAIL)))
if FAIL:
    sys.exit(1)
print('ALL OK')
