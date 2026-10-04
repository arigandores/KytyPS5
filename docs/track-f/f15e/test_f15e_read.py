"""F15e (HPP-516): fixtures of f15e_read.py - every member and edge of the seal docs/track-f/f15e.md section 4.  Ends with ALL OK.
usage: python test_f15e_read.py   (ASCII only)"""
import copy, hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'f15e_read.py')
sys.path.insert(0, HERE)
import f15e_read as R

print('suite test_f15e_read.py sha256 %s target f15e_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(open(TARGET, 'rb').read()).hexdigest()))
N = [0]
FAIL = []


def check(name, cond):
    N[0] += 1
    if not cond:
        FAIL.append(name)
        print('FAIL', name)


GUEST = 'GuestOut: Level has started: underwater_aerial_garden'


def base_log(hold_frames=310, dt=1000000 - 1, extra_after=None, b4=('FixB4: mode=1',), quit=True, before=None):
    L = ['  version: Fork build arigandores/KytyPS5 5c2c5e5', 'Shader translation cache: _ShaderCache\\PPSA21564\\' + R.DIR_FIX]
    L += list(b4)
    L += before or []
    L += ['GuestOut: something', GUEST, 'FrameTrace: n=1 dt_us=16000 draws=50', 'FrameTrace: n=2 dt_us=16000 draws=100']
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
    return dict(env={'KYTY_FIX_B4': '1', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_REC': 'x'}, attempts=[a])


MF = ['_SaveData\tPPSA21564/sce_sdmemory/memory.bin\t10\taaa', '_ShaderCache\tx\t1\tbbb']


def make(d, log=None, stdout=None, run=None, files=None, drop=()):
    os.makedirs(d, exist_ok=True)
    f = dict(installed_sha=R.BIN_EXPECT, installed_before=R.WANT, installed_after=R.WANT,
             warm='warm form: C:/x/' + R.DIR_FIX + ' present at 2026-10-04T12:00:00Z; entries 5',
             manifest_cmp='manifest cmp EQUAL files 2 listsha abc', glitch='one-frame glitches: 0', sheet='sheet: x.png frames 3100')
    files = dict(files or {})
    mf_run = files.pop('_mf_run', MF)
    f.update(files)
    for k, v in f.items():
        if k not in drop:
            open(os.path.join(d, k + '.txt'), 'w').write(v + '\n')
    if 'log' not in drop:
        open(os.path.join(d, 'log.txt'), 'wb').write(('\n'.join(log if log is not None else base_log()) + '\n').encode())
    if 'stdout' not in drop:
        open(os.path.join(d, 'stdout.txt'), 'wb').write(('\n'.join(stdout or ['Shaders: VS 1']) + '\n').encode())
    if 'run' not in drop:
        open(os.path.join(d, 'es.json'), 'w').write(json.dumps(run if run is not None else run_json()))
    if 'idx' not in drop:
        open(os.path.join(d, 'rec.idx'), 'w').write('r\n' * 3100)
    if 'mf_before' not in drop:
        open(os.path.join(d, 'manifest_before.tsv'), 'w').write('\n'.join(MF) + '\n')
    if 'mf_run' not in drop:
        open(os.path.join(d, 'manifest_run.tsv'), 'w').write('\n'.join(mf_run) + '\n')
    if 'bin' not in drop:
        open(os.path.join(d, 'bin.exe'), 'wb').write(b'MZ\x00' + R.VERSION + b'\x00')
    return d


def rowmap(d):
    res = R.read(R.paths(d))
    out = R.rows('fixture', res)
    m = {}
    for x in out:
        x = x.strip()
        if x.startswith('ROW '):
            k, v = x[4:].rsplit(': ', 1)
            m[k] = v
    return m, res, out


K = dict(sha='binary sha256 of the tag = 907569f6 (F15c copy)', ver='version string ...-1878-g5c2c5e52 in the tag binary',
         before='installed adb0c82f before the tag', after='installed adb0c82f after the return',
         env='env: KYTY_FIX_B4=1, no other KYTY_FIX_*, no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS',
         rev='revision text names 5c2c5e5 (reference)',
         dir='translation cache directory %s in every line (reference)' % R.DIR_FIX,
         warm='warm form: %s present before the start (reference)' % R.DIR_FIX,
         b4='FixB4: mode=1 (every line) before the first GuestOut', entry='entered (entry line of underwater_aerial_garden)',
         hold='hold >= 300 s after the first scene frame', lived='the process lived through the hold (outcome ok, hold_exit null)',
         death='0 death markers (log and stdout)', video='video index records >= 3000', glitch='0 one-frame glitches',
         sheet='sheet for the lead made', quit='exit by the harness: Event: quit line in the log',
         after_quit='after Event: quit: 0 --- Fatal Error --- and 0 m_files[index] == nullptr (log)',
         end='the process ended before the harness timeout (40 s after WM_CLOSE, not killed)',
         manifest='manifest of the caches, saves and GLCache before = after the return',
         interf='no interference: window minimized / Recovering Vulkan swapchain / GamePatch line (else not read as an outcome, question '
                'to the lead)')


def k2key(n):
    return 'frames >= 1 s after the first scene frame = %d (REPORT, not a gate)' % n


T = tempfile.mkdtemp(prefix='f15e_fx_')
try:
    c = [0]

    def case(**kw):
        c[0] += 1
        return make(os.path.join(T, 'c%03d' % c[0]), **kw)

    # positive
    m, res, out = rowmap(case())
    for k in K.values():
        check('positive %s' % k, m.get(k) == 'YES')
    check('positive k2 row', m.get(k2key(0)) == 'YES')
    check('positive row count', len(m) == len(K) + 1)
    check('positive hold s', abs(res['hold_s'] - 310 * 0.999999) < 0.2)
    check('positive exit code line', any('exit code 0 (0x00000000)' in x for x in out))
    check('positive savedata equal', res['savedata']['equal'] is True and res['savedata']['before'] == 1)
    # binary rows
    m, _, _ = rowmap(case(files=dict(installed_sha='0' * 64)))
    check('tag sha other -> NO', m[K['sha']] == 'NO')
    m, _, _ = rowmap(case(files=dict(installed_sha='631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17')))
    check('tag sha FS5 -> NO', m[K['sha']] == 'NO')
    m, _, _ = rowmap(case(drop=('installed_sha',)))
    check('tag sha missing -> NO', m[K['sha']] == 'NO')
    d = case()
    open(os.path.join(d, 'bin.exe'), 'wb').write(b'MZ KytyPS5-2026-09-15-6a2987a-1877-g4d9e8ab7')
    m, _, _ = rowmap(d)
    check('version of S12 -> NO', m[K['ver']] == 'NO')
    m, _, _ = rowmap(case(drop=('bin',)))
    check('binary file missing -> NOT_READ', m[K['ver']] == 'NOT_READ')
    m, _, _ = rowmap(case(files=dict(installed_before='31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5')))
    check('installed before FS4 -> NO', m[K['before']] == 'NO')
    m, _, _ = rowmap(case(files=dict(installed_after=R.BIN_EXPECT)))
    check('installed after = tag binary -> NO', m[K['after']] == 'NO')
    m, _, _ = rowmap(case(drop=('installed_after',)))
    check('installed after missing -> NO', m[K['after']] == 'NO')
    # env
    r = run_json(); r['env'] = {'KYTY_FIX_B4': '0'}
    m, _, _ = rowmap(case(run=r))
    check('env B4=0 -> NO', m[K['env']] == 'NO')
    r = run_json(); r['env'] = {}
    m, _, _ = rowmap(case(run=r))
    check('env no B4 -> NO', m[K['env']] == 'NO')
    r = run_json(); r['env']['KYTY_FIX_F10'] = '1'
    m, _, _ = rowmap(case(run=r))
    check('env other KYTY_FIX -> NO', m[K['env']] == 'NO')
    r = run_json(); r['env']['KYTY_GAME_PATCH'] = 'p.txt'
    m, _, _ = rowmap(case(run=r))
    check('env GAME_PATCH -> NO', m[K['env']] == 'NO')
    r = run_json(); r['env']['KYTY_GPU_CHECKPOINTS'] = '0'
    m, _, _ = rowmap(case(run=r))
    check('env GPU_CHECKPOINTS present -> NO', m[K['env']] == 'NO')
    m, _, _ = rowmap(case(drop=('run',)))
    check('no run json -> env NOT_READ', m[K['env']] == 'NOT_READ')
    check('no run json -> lived NOT_READ', m[K['lived']] == 'NOT_READ')
    check('no run json -> end NOT_READ', m[K['end']] == 'NOT_READ')
    # revision (reference)
    L = base_log(); L[0] = '  version: Fork build arigandores/KytyPS5 4d9e8ab'
    m, _, _ = rowmap(case(log=L))
    check('revision other -> NO', m[K['rev']] == 'NO')
    m, _, _ = rowmap(case(log=base_log()[1:]))
    check('revision absent -> NOT_PRESENT', m[K['rev']] == 'NOT_PRESENT')
    # directory and warm (reference)
    L = base_log(); L[1] = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b'
    m, _, _ = rowmap(case(log=L))
    check('directory base -> NO', m[K['dir']] == 'NO')
    L = base_log(); L.insert(2, 'Shader translation cache: _ShaderCache/PPSA21564/' + R.DIR_FIX)
    m, _, _ = rowmap(case(log=L))
    check('directory forward slashes -> YES', m[K['dir']] == 'YES')
    L = base_log(); L[1] = 'Shader translation cache: _ShaderCache\\PPSA21564\\' + R.DIR_FIX + '_x'
    m, _, _ = rowmap(case(log=L))
    check('directory suffix -> NO', m[K['dir']] == 'NO')
    L = base_log(); del L[1]
    m, _, _ = rowmap(case(log=L))
    check('directory no line -> NO', m[K['dir']] == 'NO')
    m, _, _ = rowmap(case(files=dict(warm='warm form: C:/x/' + R.DIR_FIX + ' absent at 2026')))
    check('warm absent -> NO', m[K['warm']] == 'NO')
    m, _, _ = rowmap(case(drop=('warm',)))
    check('warm.txt missing -> NO', m[K['warm']] == 'NO')
    # FixB4
    m, _, _ = rowmap(case(log=base_log(b4=('FixB4: mode=0',))))
    check('FixB4 mode=0 -> NO', m[K['b4']] == 'NO')
    m, _, _ = rowmap(case(log=base_log(b4=())))
    check('FixB4 no line -> NO', m[K['b4']] == 'NO')
    m, _, _ = rowmap(case(log=base_log(b4=('FixB4: mode=1', 'FixB4: mode=0'))))
    check('FixB4 second line mode=0 -> NO', m[K['b4']] == 'NO')
    m, _, _ = rowmap(case(log=base_log(b4=('FixB4: mode=1', 'FixB4: mode=1'))))
    check('FixB4 two lines mode=1 -> YES', m[K['b4']] == 'YES')
    L = base_log(b4=()); i = L.index('GuestOut: something'); L.insert(i + 1, 'FixB4: mode=1')
    m, _, _ = rowmap(case(log=L))
    check('FixB4 after the first GuestOut -> NO', m[K['b4']] == 'NO')
    m, _, _ = rowmap(case(log=base_log(b4=('FixB4: mode=10',))))
    check('FixB4 mode=10 -> NO', m[K['b4']] == 'NO')
    # entry / hold
    L = base_log(); L[L.index(GUEST)] = 'GuestOut: Level has started: hoover_beach'
    m, _, _ = rowmap(case(log=L))
    check('entry other level -> NO', m[K['entry']] == 'NO')
    check('entry other level -> hold NO', m[K['hold']] == 'NO')
    m, res, _ = rowmap(case(log=base_log(hold_frames=300, dt=1000000 - 1)))
    check('hold 300 s - 300 us -> NO', m[K['hold']] == 'NO')
    L = base_log(hold_frames=299, dt=999999) ; i = L.index('Window 1 closed'); L.insert(i, 'FrameTrace: n=999 dt_us=1000299 draws=3000')
    m, res, _ = rowmap(case(log=L))
    check('hold exactly 300 s -> YES', m[K['hold']] == 'YES' and res['hold_us'] == 300000000)
    check('hold exactly 300 s with a 1 s frame -> k2 row NO', m.get(k2key(1)) == 'NO')
    check('k2 frame does not cost the hold', m[K['hold']] == 'YES')
    L = base_log(hold_frames=299, dt=999999); i = L.index('Window 1 closed'); L.insert(i, 'FrameTrace: n=999 dt_us=1000298 draws=3000')
    m, res, _ = rowmap(case(log=L))
    check('hold 300 s - 1 us -> NO', m[K['hold']] == 'NO' and res['hold_us'] == 300000000 - 1)
    m, res, _ = rowmap(case(log=base_log(hold_frames=310, dt=999999)))
    check('999 999 us is not a frame >= 1 s', res['k2_after'] == 0)
    L = base_log(); i = L.index('Window 1 closed'); L.insert(i, 'FrameTrace: n=998 dt_us=1000000 draws=3000')
    m, res, _ = rowmap(case(log=L))
    check('1 000 000 us is a frame >= 1 s', res['k2_after'] == 1 and m.get(k2key(1)) == 'NO')
    L = base_log(hold_frames=100); i = L.index('Window 1 closed')
    L[i:i] = ['GuestOut: Level has started: hub'] + ['FrameTrace: n=%d dt_us=999999 draws=3000' % (j + 500) for j in range(250)]
    m, res, _ = rowmap(case(log=L))
    check('scene change ends the hold -> NO', m[K['hold']] == 'NO' and res['scene_change_line'] is not None)
    L = base_log(); L[L.index('FrameTrace: n=2 dt_us=16000 draws=100')] = 'FrameTrace: n=2 dt_us=16000 draws=99'
    m, res, _ = rowmap(case(log=L))
    check('draws 99 is not the first scene frame', res['first_scene_n'] == 3)
    m, _, _ = rowmap(case(run=run_json(hold_exit=3221225477)))
    check('process ended inside the hold -> lived NO', m[K['lived']] == 'NO')
    m, _, _ = rowmap(case(run=run_json(outcome='timeout')))
    check('outcome timeout -> lived NO', m[K['lived']] == 'NO')
    # death markers
    for d_ in R.DEATH:
        L = base_log(before=[d_.decode() + ' x'])
        m, _, _ = rowmap(case(log=L))
        check('death in log %s -> NO' % d_.decode(), m[K['death']] == 'NO')
        m, _, _ = rowmap(case(stdout=[d_.decode() + ' x']))
        check('death in stdout %s -> NO' % d_.decode(), m[K['death']] == 'NO')
    # video
    d = case(); open(os.path.join(d, 'rec.idx'), 'w').write('r\n' * 3000)
    m, _, _ = rowmap(d)
    check('video 3000 -> YES', m[K['video']] == 'YES')
    d = case(); open(os.path.join(d, 'rec.idx'), 'w').write('r\n' * 2999)
    m, _, _ = rowmap(d)
    check('video 2999 -> NO', m[K['video']] == 'NO')
    m, _, _ = rowmap(case(drop=('idx',)))
    check('no video index -> NO', m[K['video']] == 'NO')
    m, _, _ = rowmap(case(files=dict(glitch='one-frame glitches: 1')))
    check('glitch 1 -> NO', m[K['glitch']] == 'NO')
    m, _, _ = rowmap(case(files=dict(glitch='error')))
    check('no glitch line -> NOT_READ', m[K['glitch']] == 'NOT_READ')
    m, _, _ = rowmap(case(drop=('sheet',)))
    check('no sheet -> NO', m[K['sheet']] == 'NO')
    # quit and after quit
    m, _, _ = rowmap(case(log=base_log(quit=False)))
    check('no Event: quit -> quit NO', m[K['quit']] == 'NO')
    check('no Event: quit -> after-quit NOT_READ', m[K['after_quit']] == 'NOT_READ')
    m, res, _ = rowmap(case(log=base_log(extra_after=['--- Fatal Error ---'])))
    check('fatal after quit -> NO', m[K['after_quit']] == 'NO' and res['fatal_after_quit'] == 1)
    check('fatal after quit -> death NO too', m[K['death']] == 'NO')
    m, res, _ = rowmap(case(log=base_log(extra_after=['[E] fileSystem.cpp:222: EXIT_IF(m_files[index] == nullptr)'])))
    check('m_files nullptr after quit -> NO', m[K['after_quit']] == 'NO' and res['null_after_quit'] == 1)
    check('m_files nullptr alone -> death YES (not a death marker)', m[K['death']] == 'YES')
    m, res, _ = rowmap(case(log=base_log(before=['m_files[index] == nullptr'])))
    check('m_files nullptr before quit -> after-quit YES, total 1', m[K['after_quit']] == 'YES' and res['null_log_total'] == 1)
    m, res, _ = rowmap(case(log=base_log(before=['--- Fatal Error ---'])))
    check('fatal before quit -> after-quit YES, death NO', m[K['after_quit']] == 'YES' and res['fatal_after_quit'] == 0
          and res['fatal_log_total'] == 1 and m[K['death']] == 'NO')
    m, res, _ = rowmap(case(stdout=['m_files[index] == nullptr', '--- Fatal Error ---']))
    check('stdout counts printed', res['null_stdout'] == 1 and res['fatal_stdout'] == 1)
    L = base_log(); L.append('Event: quit'); L.append('--- Fatal Error ---')
    m, res, _ = rowmap(case(log=L))
    check('second quit line: counted after the first', res['fatal_after_quit'] == 1 and m[K['after_quit']] == 'NO')
    # exit
    m, _, out = rowmap(case(run=run_json(close_killed=True, close_rc=1)))
    check('killed -> end NO', m[K['end']] == 'NO')
    m, _, out = rowmap(case(run=run_json(close_rc=None)))
    check('rc None (alive) -> end NO', m[K['end']] == 'NO')
    m, _, out = rowmap(case(run=run_json(close_rc=321)))
    check('rc 321 not killed -> end YES (exit code is a report row)', m[K['end']] == 'YES')
    check('rc 321 printed hex', any('exit code 321 (0x00000141)' in x for x in out))
    m, _, out = rowmap(case(run=run_json(close_rc=-1073740940)))
    check('negative rc printed hex', any('(0xc0000374)' in x for x in out))
    r = run_json(); del r['attempts'][0]['close_killed']
    m, _, _ = rowmap(case(run=r))
    check('no close record (old harness) -> end NOT_READ', m[K['end']] == 'NOT_READ')
    # _SaveData report
    mf2 = ['_SaveData\tPPSA21564/sce_sdmemory/memory.bin\t10\tccc', '_ShaderCache\tx\t1\tbbb']
    m, res, out = rowmap(case(files=dict(_mf_run=mf2)))
    check('savedata differ -> report, rows unchanged', res['savedata']['equal'] is False and len(m) == len(K) + 1
          and all(v == 'YES' for v in m.values()))
    check('savedata differ printed', any('equal NO' in x and 'memory.bin' in x for x in out))
    m, res, _ = rowmap(case(drop=('mf_run',)))
    check('savedata run manifest missing -> NOT_READ', res['savedata']['equal'] is None)
    # manifest
    m, _, _ = rowmap(case(files=dict(manifest_cmp='manifest cmp DIFFER only-before 1 only-after 1')))
    check('manifest DIFFER -> NO', m[K['manifest']] == 'NO')
    m, _, _ = rowmap(case(drop=('manifest_cmp',)))
    check('manifest missing -> NO', m[K['manifest']] == 'NO')
    # interference and data
    for line, want in (('Window 1 minimized', 'NO'), ('Recovering Vulkan swapchain', 'NO'), ('GamePatch: x', 'NO'),
                       ('Window 1 lost keyboard focus', 'YES'), ('Window 1 restored', 'YES'), ('AsyncPipelines: skipped draw 1', 'YES'),
                       ('[Vulkan][E] x', 'YES')):
        m, _, _ = rowmap(case(log=base_log(before=[line])))
        check('interference %s -> %s' % (line, want), m[K['interf']] == want)
    # missing log
    m, res, _ = rowmap(case(drop=('log',)))
    check('no log -> entry NO, quit NO', m[K['entry']] == 'NO' and m[K['quit']] == 'NO' and res['log_sha256'] is None)
    # CLI: strict cp1250 without PYTHONIOENCODING, ASCII only, json, unknown tag
    d = case()
    env = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    p = subprocess.run([sys.executable, TARGET, '--dir', d], capture_output=True, env=env)
    check('cli cp1250 strict rc 0', p.returncode == 0)
    check('cli ASCII only', all(b < 128 for b in p.stdout))
    check('cli has ROW lines', p.stdout.count(b'  ROW ') == len(K) + 1)
    env2 = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
    p = subprocess.run([sys.executable, TARGET, '--dir', d], capture_output=True, env=env2)
    check('cli without PYTHONIOENCODING rc 0', p.returncode == 0)
    jp = os.path.join(T, 'o.json')
    p = subprocess.run([sys.executable, TARGET, '--dir', d, '--json', jp], capture_output=True)
    check('cli json written', p.returncode == 0 and json.load(open(jp))['b4_ok'] is True)
    p = subprocess.run([sys.executable, TARGET, 'fs5_v'], capture_output=True)
    check('cli unknown tag refused', p.returncode != 0 and b'unknown tag' in p.stderr)
finally:
    shutil.rmtree(T, ignore_errors=True)

print('checks %d failed %d' % (N[0], len(FAIL)))
if FAIL:
    sys.exit(1)
print('ALL OK')
