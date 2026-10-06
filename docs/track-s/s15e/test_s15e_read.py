"""Track S link S15e (HPP-636): fixtures of s15e_read.py - every member, admission, form and data row and every edge: member (1a) (1 line /
0 / 2 / 727 shaders / 'incompatible ...; ignored' only / a prefix before the line), (1b) (= the catalogue / other value / one of two lines
other / no line / no catalogue file), (2a)-(2d) from after.json (pipelines.bin absent, header other, size 20 430 720 / 20 430 719, 728 of
728 / 727 / manifest 729, no after.json), (3a)-(3d) (death markers in the log / stdout, no stdout, video 3000 / 2999 / missing, glitches 0 /
1 / unread, sheet), admission (binary FS7 in each of the four places, version string, revision text, prereg, KYTY_SHADER_SEED /
KYTY_SHADER_SEED_PATH / KYTY_CACHE_MODE / KYTY_FIX_F19 / validation true / no KYTY_REC / other level, pre-state BAD / missing, directory
base, minimized / Recovering / GamePatch), form (no entry, hold 300 s - 1 us, outcome timeout, a member NO wins), the data rows (skipped
draw and held lines before / after the first scene frame / after a scene change, frames >= 100 ms and >= 1 s, ShaderPreparation: ready and
PipelinePrecache: all pipelines created with ms), the functions pb_header, load_manifest, pre_state, after_state on temporary directories and
on the real catalogue, the variant of the executor (727 catalogue: letter MEMBERS_FAIL, variant
MEMBERS_PASS; its edges), the sealed import of fs8c_read.py, output in strict cp1250 without PYTHONIOENCODING, json, other tag refused.  The
first output line names the suite and the target with their sha256; the last line is ALL OK.  ASCII only."""
import copy, hashlib, json, os, shutil, struct, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 's15e_read.py')
sys.path.insert(0, HERE)
import s15e_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_s15e_read.py sha256 %s target s15e_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(TARGET)))
OK = True
N = 0
NF = 0
TMP = tempfile.mkdtemp(prefix='s15e_fx_')
FS8 = R.BIN_EXPECT
FS7 = '8df61c009fbe6d7fd7f4e7576e89ab1b0989129336a26f6d1cdf8fd778fbffe7'
SEAL = b'seal fixture text\n'
SEAL_SHA = hashlib.sha256(SEAL).hexdigest()
BIN8 = b'xx KytyPS5-2026-09-15-6a2987a-1889-g302347b4 yy KytyPS5-2026-09-15-6a2987a-1888-g0f78a522 zz'
BIN7 = b'xx KytyPS5-2026-09-15-6a2987a-1883-gd6ee2dc8 yy'
COMPAT = 'KytySeed1:PPSA21564:01.007.000:KytySC3:9177b426:robust:fixf19::10288:000010de:00002c59'
STC_FIX = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19'
STC_BASE = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10'
ENTRY = 'GuestOut: Level has started: underwater_aerial_garden'
FORK = 'Fork build arigandores/KytyPS5 302347b, x'
SEED_C = 'ShaderSeed: compatibility=' + COMPAT
SEED_I = 'ShaderSeed: installed (728 shaders)'
READY = 'ShaderPreparation: ready completed=900 total=900 skipped=0'
CREATED = 'PipelinePrecache: all pipelines created, 28123 ms'
HEAD = ['FixB4: mode=1 x', 'FixB24: mode=1 z', FORK, STC_FIX, SEED_C, SEED_I, 'FixF8: mode=1 y', READY, CREATED, 'GuestOut: boot']
ENV = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden',
       'KYTY_REC': 'C:\\kyty\\s288\\s15e\\rec_s15_i.mp4', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}
CMD = ['kyty_emulator.exe', '--vulkan-validation', 'false', '--shader-validation', 'false']
ES = {'binary_sha256': FS8, 'env': ENV, 'cmdline': CMD, 'prereg': {'sha256': SEAL_SHA},
      'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': None, 'hold_s': 330.1, 'stable_s': 30.0}]}
AFTER = {'pb_present': True, 'pb_size': 20500000, 'pb_sha256': 'ab', 'pb_header_sha256': 'h', 'cat_header_sha256': 'h',
         'header_equal': True, 'n_trans_manifest': 728, 'n_trans_match': 728, 'n_missing': 0, 'missing': [], 'n_differ': 0,
         'differ': [], 'variant_files': 729, 'manifest_sha256': 'm'}
PRE = 'manifest x\nseeds dir y = manifest: YES\nPRE-STATE OK'


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


def af(**kw):
    a = dict(AFTER)
    a.update(kw)
    return a


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
         sha_t=FS8, before=FS8, after_sha=FS8, pre=PRE, after=None, compat=COMPAT, binb=BIN8, seal=SEAL, norun=False, noafter=False, ncat=728):
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
                  ('installed_after.txt', after_sha), ('pre.txt', pre), ('compat.txt', compat)):
        if t is not None:
            with open(os.path.join(d, fn), 'wb') as f:
                f.write((t + '\r\n' if fn == 'compat.txt' else t + '\n').encode('utf-8'))
    if not noafter:
        with open(os.path.join(d, 'after.json'), 'w') as f:
            json.dump(after if after is not None else AFTER, f)
    if ncat is not None:
        with open(os.path.join(d, 'manifest.txt'), 'w', newline='\n') as f:
            f.write('compatibility.txt 170 %s\n' % ('c' * 64))
            f.write('manifest.json 99 %s\n' % ('d' * 64))
            for i in range(ncat):
                f.write('cs_%04d.bin 10 %s\n' % (i, 'a' * 64))
            f.write('pipelines.bin 20430720 %s\n' % ('b' * 64))
    if binb is not None:
        with open(os.path.join(d, 'bin.exe'), 'wb') as f:
            f.write(binb)
    if seal is not None:
        with open(os.path.join(d, 'seal.md'), 'wb') as f:
            f.write(seal)
    return d


def rm(d):
    res = R.read(R.paths(d))
    lines = R.rows(res)
    return res, res['reading'], lines


def check(name, cond):
    global OK, N, NF
    N += 1
    if not cond:
        OK = False
        NF += 1
        print('FAIL %s' % name)


def row(lines, prefix):
    for x in lines:
        s = x.strip()
        if s.startswith(prefix):
            return s.rsplit(': ', 1)[1]
    return 'ROW MISSING'


def case(log, prefix, **kw):
    res, w, lines = rm(make(log, **kw))
    return row(lines, prefix), w


# ---- sealed import
check('fs8c_read.py imported from C:/kyty/f287/fs8c, sha256 5c0b52c2', R.C.__file__.replace('\\', '/').startswith('C:/kyty/f287/fs8c/')
      and sha(R.C.__file__) == '5c0b52c2750d5fab0ab39a74d22f4c48346115b30fb36e4b93f20514dd34b008')
check('constants: 728 shaders, 20430720 bytes, variant _fixf19, seal 17_s.md', R.N_SHADERS == 728 and R.PB_MIN == 20430720
      and R.DIR_FIX == 'variant_fixb26_fixb1b_fixf10_fixf19' and R.SEAL_PATH == 'C:/kyty/s288/pred/17_s.md')

# ---- baseline
res, w, lines = rm(make(HEAD + scene()))
check('baseline: MEMBERS_PASS', w == 'MEMBERS_PASS' and lines[-1] == 'READING s15_i: MEMBERS_PASS')
check('baseline: 10 members, 9 admit, 3 form rows, 2 variant rows', len(res['rows']['MEMBER']) == 10
      and len(res['rows']['ADMIT']) == 9 and len(res['rows']['FORM']) == 3 and len(res['rows']['VARIANT']) == 2)
check('baseline: every row YES', all(row(lines, p) == 'YES' for p in ('MEMBER (1a)', 'MEMBER (1b)', 'MEMBER (2a)', 'MEMBER (2b)',
      'MEMBER (2c)', 'MEMBER (2d)', 'MEMBER (3a)', 'MEMBER (3b)', 'MEMBER (3c)', 'MEMBER (3d)')))

# ---- member (1a)
H0 = [x for x in HEAD if x != SEED_I]
r_, w_ = case(H0 + scene(), 'MEMBER (1a)')
check('(1a) no installed line: NO, MEMBERS_FAIL', r_ == 'NO' and w_ == 'MEMBERS_FAIL')
r_, w_ = case(HEAD + [SEED_I] + scene(), 'MEMBER (1a)')
check('(1a) two installed lines: NO', r_ == 'NO' and w_ == 'MEMBERS_FAIL')
r_, w_ = case(H0 + ['ShaderSeed: installed (727 shaders)'] + scene(), 'MEMBER (1a)')
check('(1a) 727 shaders: NO', r_ == 'NO')
r_, w_ = case(H0 + ['ShaderSeed: incompatible game, GPU or translator; ignored'] + scene(), 'MEMBER (1a)')
check('(1a) incompatible line only: NO', r_ == 'NO')
r_, w_ = case(H0 + ['ShaderSeed: installed (728 shaders) extra'] + scene(), 'MEMBER (1a)')
check('(1a) trailing text: NO', r_ == 'NO')
r_, w_ = case(H0 + ['[1][00:00:00.000] ShaderSeed: installed (728 shaders)'] + scene(), 'MEMBER (1a)')
check('(1a) a prefix before ShaderSeed: YES', r_ == 'YES')
r_, w_ = case(H0 + ['ShaderSeed: installed (728 shaders)\r'] + scene(), 'MEMBER (1a)')
check('(1a) CRLF line: YES', r_ == 'YES')

# ---- member (1b)
r_, w_ = case([x for x in HEAD if x != SEED_C] + scene(), 'MEMBER (1b)')
check('(1b) no compatibility line: NO', r_ == 'NO' and w_ == 'MEMBERS_FAIL')
r_, w_ = case([x if x != SEED_C else SEED_C + 'x' for x in HEAD] + scene(), 'MEMBER (1b)')
check('(1b) other value: NO', r_ == 'NO')
r_, w_ = case(HEAD + ['ShaderSeed: compatibility=other'] + scene(), 'MEMBER (1b)')
check('(1b) one of two lines other: NO', r_ == 'NO')
r_, w_ = case(HEAD + scene(), 'MEMBER (1b)', compat=None)
check('(1b) no catalogue compatibility file: NOT_DETERMINED, NOT_EVALUABLE', r_ == 'NOT_DETERMINED' and w_ == 'NOT_EVALUABLE')
r_, w_ = case(HEAD + scene(), 'MEMBER (1b)', compat=COMPAT[:-1])
check('(1b) catalogue first line differs by one char: NO', r_ == 'NO')
res, w, lines = rm(make(HEAD + scene()))
check('(1b) catalogue CRLF stripped: YES', row(lines, 'MEMBER (1b)') == 'YES' and res['compat_cat'] == COMPAT)

# ---- members (2a)-(2d)
for nm, a, p in (('pb absent', af(pb_present=False, pb_size=None), 'MEMBER (2a)'), ('header other', af(header_equal=False), 'MEMBER (2b)'),
                 ('size 20430719', af(pb_size=20430719), 'MEMBER (2c)'), ('size None', af(pb_size=None), 'MEMBER (2c)'),
                 ('727 of 728', af(n_trans_match=727), 'MEMBER (2d)'), ('manifest 729', af(n_trans_manifest=729, n_trans_match=729),
                                                                          'MEMBER (2d)')):
    r_, w_ = case(HEAD + scene(), p, after=a)
    check('(2) %s: NO, MEMBERS_FAIL' % nm, r_ == 'NO' and w_ == 'MEMBERS_FAIL')
r_, w_ = case(HEAD + scene(), 'MEMBER (2c)', after=af(pb_size=20430720))
check('(2c) size 20430720: YES, PASS', r_ == 'YES' and w_ == 'MEMBERS_PASS')
res, w, lines = rm(make(HEAD + scene(), noafter=True))
check('(2) no after.json: (2a)-(2d) NOT_DETERMINED, NOT_EVALUABLE', w == 'NOT_EVALUABLE' and all(row(lines, p) == 'NOT_DETERMINED'
      for p in ('MEMBER (2a)', 'MEMBER (2b)', 'MEMBER (2c)', 'MEMBER (2d)')))

# ---- members (3a)-(3d)
r_, w_ = case(HEAD + scene() + ['--- Fatal Error ---'], 'MEMBER (3a)')
check('(3a) death in the log: NO', r_ == 'NO' and w_ == 'MEMBERS_FAIL')
r_, w_ = case(HEAD + scene(), 'MEMBER (3a)', stdout='Unhandled exception: x\n')
check('(3a) death in stdout: NO', r_ == 'NO')
r_, w_ = case(HEAD + scene(), 'MEMBER (3a)', stdout=None)
check('(3a) no stdout: NOT_DETERMINED', r_ == 'NOT_DETERMINED' and w_ == 'NOT_EVALUABLE')
r_, w_ = case(HEAD + scene(), 'MEMBER (3b)', idx=2999)
check('(3b) 2999: NO', r_ == 'NO' and w_ == 'MEMBERS_FAIL')
r_, w_ = case(HEAD + scene(), 'MEMBER (3b)', idx=None)
check('(3b) no index: NO', r_ == 'NO')
r_, w_ = case(HEAD + scene(), 'MEMBER (3c)', glitch='one-frame glitches: 1')
check('(3c) 1 glitch: NO', r_ == 'NO')
r_, w_ = case(HEAD + scene(), 'MEMBER (3c)', glitch='garbage')
check('(3c) unread: NOT_DETERMINED', r_ == 'NOT_DETERMINED' and w_ == 'NOT_EVALUABLE')
r_, w_ = case(HEAD + scene(), 'MEMBER (3d)', sheet='error')
check('(3d) no sheet line: NO', r_ == 'NO')

# ---- admission
for nm, kw in (('before FS7', dict(before=FS7)), ('of the tag FS7', dict(sha_t=FS7)), ('after FS7', dict(after_sha=FS7)),
               ('json FS7', dict(run=es(binary_sha256=FS7))), ('version FS7', dict(binb=BIN7)), ('no binary file', dict(binb=None))):
    r_, w_ = case(HEAD + scene(), 'ADMIT binary' if 'version' not in nm and 'binary file' not in nm else 'ADMIT version', **kw)
    check('admit %s: NO, NOT_ADMITTED' % nm, r_ == 'NO' and w_ == 'NOT_ADMITTED')
r_, w_ = case([x if x != FORK else 'Fork build arigandores/KytyPS5 d6ee2dc, x' for x in HEAD] + scene(), 'ADMIT every revision')
check('admit revision d6ee2dc: NO', r_ == 'NO' and w_ == 'NOT_ADMITTED')
r_, w_ = case(HEAD + scene(), 'ADMIT json prereg', run=es(prereg={'sha256': '0' * 64}))
check('admit prereg other: NO', r_ == 'NO' and w_ == 'NOT_ADMITTED')
for k in ('KYTY_SHADER_SEED', 'KYTY_SHADER_SEED_PATH', 'KYTY_CACHE_MODE'):
    r_, w_ = case(HEAD + scene(), 'ADMIT none of KYTY_SHADER_SEED', run=es(env_set={k: '0'}))
    check('admit env %s: NO, NOT_ADMITTED' % k, r_ == 'NO' and w_ == 'NOT_ADMITTED')
for nm, run in (('KYTY_FIX_F19', es(env_set={'KYTY_FIX_F19': '1'})), ('validation true', es(cmdline=CMD + ['--vulkan-validation', 'true'])),
                ('no KYTY_REC', es(env_del=['KYTY_REC'])), ('other level', es(env_set={'KYTY_GUEST_ARGS': '-lvl hoover_beach'}))):
    r_, w_ = case(HEAD + scene(), 'ADMIT environment', run=run)
    check('admit env %s: NO' % nm, r_ == 'NO' and w_ == 'NOT_ADMITTED')
r_, w_ = case(HEAD + scene(), 'ADMIT pre-state', pre='x\nPRE-STATE BAD')
check('admit pre-state BAD: NO', r_ == 'NO' and w_ == 'NOT_ADMITTED')
r_, w_ = case(HEAD + scene(), 'ADMIT pre-state', pre=None)
check('admit pre-state missing: NO', r_ == 'NO' and w_ == 'NOT_ADMITTED')
r_, w_ = case([x if x != STC_FIX else STC_BASE for x in HEAD] + scene(), 'ADMIT translation cache')
check('admit directory _fixf10: NO', r_ == 'NO' and w_ == 'NOT_ADMITTED')
for nm, extra in (('minimized', 'Window 1 minimized'), ('recovering', 'Recovering Vulkan swapchain'), ('gamepatch', 'GamePatch: x')):
    r_, w_ = case(HEAD + scene() + [extra], 'ADMIT no window')
    check('admit %s: NO, NOT_ADMITTED' % nm, r_ == 'NO' and w_ == 'NOT_ADMITTED')
r_, w_ = case(HEAD + scene() + ['Window 1 minimized'], 'ADMIT no window', idx=10)
check('admission wins over a failed member', w_ == 'NOT_ADMITTED')
res, w, lines = rm(make(HEAD + scene() + ['Window 1 lost keyboard focus', 'Window 1 restored']))
check('focus / restored: not admission, PASS', w == 'MEMBERS_PASS')

# ---- form
res, w, lines = rm(make(HEAD + scene(entry='GuestOut: Level has started: hoover_beach')))
check('form: no entry -> NOT_EVALUABLE', row(lines, 'FORM entered') == 'NO' and w == 'NOT_EVALUABLE')
res, w, lines = rm(make(HEAD + scene(hold_us=300000000 - 1)))
check('form: hold 300 s - 1 us -> NO, NOT_EVALUABLE', row(lines, 'FORM hold') == 'NO' and w == 'NOT_EVALUABLE')
res, w, lines = rm(make(HEAD + scene(hold_us=300000000)))
check('form: hold 300 s -> YES, PASS', row(lines, 'FORM hold') == 'YES' and w == 'MEMBERS_PASS')
res, w, lines = rm(make(HEAD + scene(), run=es(outcome='timeout')))
check('form: outcome timeout -> NOT_EVALUABLE', row(lines, 'FORM the process') == 'NO' and w == 'NOT_EVALUABLE')
res, w, lines = rm(make(HEAD + scene(), run=es(hold_s=329.0)))
check('form: hold_s 329 -> NOT_EVALUABLE', w == 'NOT_EVALUABLE')
res, w, lines = rm(make(HEAD + scene(), norun=True))
check('no json: NOT_ADMITTED (binary, env, prereg)', w == 'NOT_ADMITTED')
res, w, lines = rm(make(H0 + scene(hold_us=1000000)))
check('a member NO wins over a form NO: MEMBERS_FAIL', w == 'MEMBERS_FAIL')

# ---- variant of the executor (n of the catalogue manifest)
I727 = 'ShaderSeed: installed (727 shaders)'
H727 = [x if x != SEED_I else I727 for x in HEAD]
A727 = af(n_trans_manifest=727, n_trans_match=727)
res, w, lines = rm(make(H727 + scene(), after=A727, ncat=727))
check('variant: 727 catalogue, 727 installed, 727 of 727 -> letter MEMBERS_FAIL ((1a), (2d) NO), variant MEMBERS_PASS',
      w == 'MEMBERS_FAIL' and res['reading_variant'] == 'MEMBERS_PASS' and row(lines, 'MEMBER (1a)') == 'NO'
      and row(lines, 'MEMBER (2d)') == 'NO' and row(lines, 'VARIANT (1a)') == 'YES' and row(lines, 'VARIANT (2d)') == 'YES'
      and res['n_cat'] == 727)
check('variant: the letter word is the last line, the variant line before it', lines[-1] == 'READING s15_i: MEMBERS_FAIL'
      and lines[-2].startswith('READING VARIANT s15_i: MEMBERS_PASS'))
res, w, lines = rm(make(HEAD + scene(), after=A727, ncat=727))
check('variant: 728 installed with 727 catalogue -> variant (1a) NO', row(lines, 'VARIANT (1a)') == 'NO'
      and res['reading_variant'] == 'MEMBERS_FAIL')
res, w, lines = rm(make(H727 + scene(), after=af(n_trans_manifest=727, n_trans_match=726), ncat=727))
check('variant: 726 of 727 -> variant (2d) NO', row(lines, 'VARIANT (2d)') == 'NO' and res['reading_variant'] == 'MEMBERS_FAIL')
res, w, lines = rm(make(H727 + scene(), after=A727, ncat=None))
check('variant: no manifest -> variant rows NOT_DETERMINED, NOT_EVALUABLE', row(lines, 'VARIANT (1a)') == 'NOT_DETERMINED'
      and res['reading_variant'] == 'NOT_EVALUABLE')
res, w, lines = rm(make(H727 + scene() + ['--- Fatal Error ---'], after=A727, ncat=727))
check('variant: a death marker fails both', w == 'MEMBERS_FAIL' and res['reading_variant'] == 'MEMBERS_FAIL')
res, w, lines = rm(make(H727 + scene() + ['Window 1 minimized'], after=A727, ncat=727))
check('variant: admission applies to both', w == 'NOT_ADMITTED' and res['reading_variant'] == 'NOT_ADMITTED')
res, w, lines = rm(make(HEAD + scene()))
check('baseline 728 catalogue: variant = letter MEMBERS_PASS', res['reading_variant'] == 'MEMBERS_PASS')

# ---- data rows (4)
lg = (HEAD + ['AsyncPipelines: skipped draw frame=1', 'AsyncPipelines: flip 1 held (incomplete frame)', ENTRY, ft(1, 16667, 50),
              'AsyncPipelines: skipped draw frame=2', ft(2, 16667, 400), 'AsyncPipelines: skipped draw frame=3',
              'AsyncPipelines: flip 3 held (incomplete frame)', 'SkipCeil: flip 4 held', ft(3, 100000, 400), ft(4, 99999, 400),
              ft(5, 1000000, 400)] + [ft(6 + i, 100000, 400) for i in range(3300)]
      + ['GuestOut: Level has started: other', 'AsyncPipelines: skipped draw frame=9', 'AsyncPipelines: flip 9 held (incomplete frame)',
         ft(9999, 2000000, 400)])
res, w, lines = rm(make(lg))
check('data: skipped draw after the first scene frame 1 (before 2, after a scene change 1 not counted)', res['skip_after'] == 1
      and res['skip_all'] == 4)
check('data: held after 2 (AsyncPipelines + SkipCeil), whole log 4', res['held_after'] == 2 and res['held_all'] == 4
      and [n for _, n in res['held_first']] == [3, 4])
check('data: frames >= 100 ms after 3302 (100000 counted, 99999 not, 1 s counted, after the scene change not)', res['f100_after'] == 3302)
check('data: frames >= 1 s after 1', res['f1s_after'] == 1)
check('data: data never decides (PASS with skips and held)', w == 'MEMBERS_PASS')
check('data: ready and created lines, ms 28123', res['created_ms'] == 28123 and len(res['ready']) == 1 and len(res['created']) == 1
      and res['ft_before_created'] == 0)
lg2 = [x for x in HEAD if x not in (READY, CREATED)] + [ft(1, 500000, 10), READY, ft(2, 600000, 10), CREATED] + scene()
res, w, lines = rm(make(lg2))
check('data: FrameTrace rows before the created line 2, 1.1 s', res['ft_before_created'] == 2 and res['dt_before_created_s'] == 1.1)
res, w, lines = rm(make([x for x in HEAD if x not in (READY, CREATED)] + scene()))
check('data: no ready / created lines -> printed empty, PASS', res['created_ms'] is None and res['ready'] == [] and w == 'MEMBERS_PASS')
check('data rows printed', sum(1 for x in lines if x.startswith('  DATA ')) == 4)

# ---- functions on temporary directories
SIG = b'KytySC3:9177b426:robust'
HDR = R.MAGIC + struct.pack('<I', len(SIG)) + SIG


def wr(p, b):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'wb') as f:
        f.write(b)


fd = os.path.join(TMP, 'fn')
cat = os.path.join(fd, 'cat')
seeds = os.path.join(fd, 'seeds')
var = os.path.join(fd, 'var')
files = {'cs_a.bin': b'A' * 40, 'ps_b.bin': b'B' * 50, 'vs_c.bin': b'C' * 60, 'compatibility.txt': (COMPAT + '\r\n').encode(),
         'pipelines.bin': HDR + b'R' * 100}
for n, b in files.items():
    wr(os.path.join(cat, n), b)
    wr(os.path.join(seeds, n), b)
man = os.path.join(fd, 'man.txt')
with open(man, 'w', newline='\n') as f:
    for n in sorted(files):
        f.write('%s %d %s\n' % (n, len(files[n]), hashlib.sha256(files[n]).hexdigest()))
os.makedirs(var)
check('pb_header: header of the form', R.pb_header(os.path.join(cat, 'pipelines.bin')) == HDR)
wr(os.path.join(fd, 'bad1.bin'), b'KytyPR2\n' + HDR[8:])
wr(os.path.join(fd, 'bad2.bin'), HDR[:-3])
check('pb_header: other magic -> None', R.pb_header(os.path.join(fd, 'bad1.bin')) is None)
check('pb_header: truncated -> None', R.pb_header(os.path.join(fd, 'bad2.bin')) is None)
check('pb_header: absent -> None', R.pb_header(os.path.join(fd, 'none.bin')) is None)
m_ = R.load_manifest(man)
check('load_manifest: 5 entries', m_ is not None and len(m_) == 5 and m_['cs_a.bin'][0] == 40)
pl = R.pre_state(seeds=seeds, variant=var, cat=cat, manifest=man)
check('pre_state: OK', pl[-1] == 'PRE-STATE OK')
wr(os.path.join(var, 'pipelines.bin'), HDR)
check('pre_state: variant pipelines.bin present -> BAD', R.pre_state(seeds=seeds, variant=var, cat=cat, manifest=man)[-1] == 'PRE-STATE BAD')
os.remove(os.path.join(var, 'pipelines.bin'))
wr(os.path.join(seeds, 'ps_b.bin'), b'X' * 50)
check('pre_state: seeds file differs -> BAD', R.pre_state(seeds=seeds, variant=var, cat=cat, manifest=man)[-1] == 'PRE-STATE BAD')
wr(os.path.join(seeds, 'ps_b.bin'), files['ps_b.bin'])
wr(os.path.join(seeds, 'extra.bin'), b'E')
check('pre_state: extra seeds file -> BAD', R.pre_state(seeds=seeds, variant=var, cat=cat, manifest=man)[-1] == 'PRE-STATE BAD')
os.remove(os.path.join(seeds, 'extra.bin'))
wr(os.path.join(cat, 'compatibility.txt'), b'other\n')
check('pre_state: compatibility differs from the catalogue -> BAD', R.pre_state(seeds=seeds, variant=var, cat=cat, manifest=man)[-1]
      == 'PRE-STATE BAD')
wr(os.path.join(cat, 'compatibility.txt'), files['compatibility.txt'])
check('pre_state: OK again', R.pre_state(seeds=seeds, variant=var, cat=cat, manifest=man)[-1] == 'PRE-STATE OK')
for n in ('cs_a.bin', 'ps_b.bin', 'vs_c.bin'):
    wr(os.path.join(var, n), files[n])
wr(os.path.join(var, 'old.bin'), b'O')
wr(os.path.join(var, 'pipelines.bin'), HDR + b'R' * 100 + b'grown')
st = R.after_state(variant=var, cat=cat, manifest=man)
check('after_state: present, header equal, 3 of 3 translations', st['pb_present'] and st['header_equal'] and st['n_trans_manifest'] == 3
      and st['n_trans_match'] == 3 and st['pb_size'] == len(HDR) + 105 and st['variant_files'] == 5)
wr(os.path.join(var, 'ps_b.bin'), b'Y' * 50)
os.remove(os.path.join(var, 'vs_c.bin'))
st = R.after_state(variant=var, cat=cat, manifest=man)
check('after_state: one differs, one missing', st['n_trans_match'] == 1 and st['n_differ'] == 1 and st['n_missing'] == 1
      and st['missing'] == ['vs_c.bin'] and st['differ'] == ['ps_b.bin'])
wr(os.path.join(var, 'pipelines.bin'), R.MAGIC + struct.pack('<I', len(SIG)) + b'KytySC3:0000000:robust' + b'R')
check('after_state: header other -> header_equal False', R.after_state(variant=var, cat=cat, manifest=man)['header_equal'] is False)
os.remove(os.path.join(var, 'pipelines.bin'))
st = R.after_state(variant=var, cat=cat, manifest=man)
check('after_state: pipelines.bin absent', st['pb_present'] is False and st['pb_size'] is None and st['header_equal'] is False)
# the real catalogue (read only)
rm_ = R.load_manifest(R.MANIFEST)
check('real seeds_manifest.txt: 730 entries = 727 translations + compatibility.txt + manifest.json + pipelines.bin 20430720 (fact '
      'behind the variant)', rm_ is not None and len(rm_) == 730 and sum(1 for n in rm_ if n.endswith('.bin') and n != 'pipelines.bin') == 727
      and 'manifest.json' in rm_ and 'compatibility.txt' in rm_
      and rm_['pipelines.bin'][0] == 20430720 and sha(R.MANIFEST).startswith('77a2389e'))
rh = R.pb_header(os.path.join(R.CAT, 'pipelines.bin'))
check('real catalogue pipelines.bin header: KytySC3:9177b426..., length 8 + 4 + size', rh is not None and rh[12:28] == b'KytySC3:9177b426'
      and len(rh) == 12 + struct.unpack('<I', rh[8:12])[0])
rc = R.first_text_line(os.path.join(R.CAT, 'compatibility.txt'))
check('real catalogue compatibility first line: KytySeed1 ... fixf19', rc is not None and rc.startswith(b'KytySeed1:PPSA21564:')
      and b':fixf19:' in rc)

# ---- output: ASCII, strict cp1250 without PYTHONIOENCODING, json, usage
d = make(['FixB4: mode=1 x', STC_FIX + '\\\u043a\u044d\u0448', 'Release, x, ver = 1, git = \u0432\u0435\u0440\u0441\u0438\u044f, date = y',
          SEED_C, SEED_I, 'ShaderSeed: \u043e\u0448\u0438\u0431\u043a\u0430', 'GuestOut: boot'] + scene(), stdout='\u043e\u0448\u0438\u0431\u043a\u0430\n')
env = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
env['PYTHONIOENCODING'] = 'cp1250:strict'
p = subprocess.run([sys.executable, TARGET, '--dir', d], capture_output=True, env=env)
check('cp1250 strict: rc 0, ASCII, word printed', p.returncode == 0 and all(b < 128 for b in p.stdout) and b'READING s15_i:' in p.stdout)
env2 = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
jp = os.path.join(TMP, 'out.json')
p2 = subprocess.run([sys.executable, TARGET, '--dir', make(HEAD + scene()), '--json', jp], capture_output=True, env=env2)
check('no PYTHONIOENCODING: rc 0, json reading and variant MEMBERS_PASS', p2.returncode == 0
      and json.load(open(jp))['reading'] == 'MEMBERS_PASS' and json.load(open(jp))['reading_variant'] == 'MEMBERS_PASS')
p3 = subprocess.run([sys.executable, TARGET, 'fs8_i'], capture_output=True, env=env2)
check('other tag refused', p3.returncode != 0)

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d fails %d' % (N, NF))
print('ALL OK' if OK else 'SOME FAILED')
