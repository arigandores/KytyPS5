"""S18c2 (HPP-654): fixtures of the S18c2 reader s18c2_read.py (seal docs/track-s/s18c2.md; ROADMAP s122 item 586 (g)-(d)).  Two synthetic
roots: the S18c root (state/s18_c19/replay, replay_known) and the S18c2 root with the tag s18_w2 made; the baseline reads MEMBERS_PASS; then one
change per admission row, form row and member of item 586 (g)(1)-(4) and every edge (share 0.90 / 0.89, records 0, the identity, the last
rebuild line, hold 310.0 / 309.9 s, VALIDATION_STOP with and without the end of the hold, the positive control of the layer), the paths of
the two roots, the dispatch of the S18c W group, the outputs (json, table, strict cp1250).
The mutlib early-exit form: the only bindings of the flag are `ok = True` and `ok &= ...`, the last statement is `sys.exit(0 if ok else 1)`.
The first output line names the suite and the targets with sha256; the output ends with ALL OK.  Synthetic files only, no game.  ASCII only.
usage: python test_s18c2_read.py [<s18c2_read.py under test>]"""
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 's18c2_read.py')


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


_spec = importlib.util.spec_from_file_location('s18c2_read_under_test', SRC)
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)
R = M.R
print('suite test_s18c2_read.py sha256 %s target s18c2_read.py sha256 %s s18c_read.py sha256 %s' % (
    sha(os.path.abspath(__file__)), sha(SRC), sha(M.BASE)))
N = [0]


def check(cond, name):
    N[0] += 1
    print(('ok   ' if cond else 'FAIL ') + name)
    return bool(cond)


ok = True
# ------------------------------------------------------------------------------------------------ constants of the print (before the synthetic ones)
REAL_KNOWN = (('replay.45.bin', 6250527, '12cb378741308d1a82133be521311882881d1bbf04aff649cccc6d8e6607fee1'),
              ('replay.46.bin', 6253395, '332a2f2d6aef0e8b64ccfe366d87df3476117abaf3b6aaf736ffbec2befc7c9a'),
              ('replay.cur', 3, 'a5331f18877e9e1543361e44b4cb0a1f5f0ed5f8297d850bf1fcc68bd7a3ab5f'))
ok &= check(M.KNOWN == REAL_KNOWN and M.KNOWN_DIR == 'replay_known', 'KNOWN = the manifest c644e3ad of replay_known (3 files)')
ok &= check(M.BASE_SHA == '16570bed3667e5a1c9a9e62a92fe2dc03f27453cb4c8d8322edca73d9c026693', 'BASE_SHA = s18c_read.py of the S18c seal')
ok &= check(M.TAG == 's18_w2' and M.HOLD == 310, 'tag s18_w2, hold 310 s')
ok &= check(R.SPEC['s18_w2'] == dict(level='underwater_aerial_garden', form='w', hold=310, state='cat_full', prev=None,
                                     env={'KYTY_SHADER_SEED': '0'}, group='W2'), 'SPEC s18_w2: Sky Garden, form w, 310 s, cat_full, KYTY_SHADER_SEED=0 only')
ok &= check('s18_w2' not in R.SEED0_TAGS and 's18_w2' not in R.ORDER and len(R.ORDER) == 25, 'S18c tables unchanged (seed lines are member (1))')
ok &= check(R.SHARE_MIN == 0.90 and R.LIMIT == '100000000' and R.BIN_EXPECT.startswith('b3cee576138a'), 'S18c constants: share, limit, binary')
ok &= check(R.ROOT == M.SRC_ROOT and R.SEAL_PATH == M.SEAL2 and M.SRC_ROOT == 'C:/kyty/s288/s18c' and M.ROOT2 == 'C:/kyty/s288/s18c2',
            'import: the S18c reader reads the S18c root and the S18c2 seal; the S18c2 root')
_real = M.files_of('C:/kyty/s288/s18c/replay_known')
ok &= check(_real == dict((n, (s, h)) for n, s, h in REAL_KNOWN), 'the real C:/kyty/s288/s18c/replay_known = KNOWN')

# ------------------------------------------------------------------------------------------------ builders
SKY = R.SKY
DUAL = 'DualSrcBlend: supported=1 enabled=1'
RB = ('ShaderReplay: rebuild records=%d prepared=%d rejected=%d pending=%d rej_src=0 rej_fused=%d rej_key=0 rej_version=0 rej_shape=0 '
      'rej_translate=0 rej_emit=0 rej_val=0 rej_write=0 rej_ref=0 translate_ms=10 wall_ms=20 perms_new=8 perms_cached=0 pipelines_bin=%s')


def rb(records=10, prepared=9, rejected=1, pending=0, pb='written'):
    return RB % (records, prepared, rejected, pending, rejected, pb)


RB0 = rb()
LOG = ['Fork build arigandores/KytyPS5 %s, test' % R.REV,
       'Shader translation cache: _ShaderCache' + chr(92) + 'PPSA21564' + chr(92) + R.DIR1,
       'ShaderSeed: compatibility=KytySeed1:PPSA21564:01.007.000:%s::10288:376:216:44:516:125:000010de:00002c59' % R.SIG1,
       'ShaderReplay: mode=3 dir=_ShaderCache' + chr(92) + 'PPSA21564' + chr(92) + 'replay compat=ok generation=46 corrupt=0 sources=1 specs=2 '
       'pipes=3 test=none',
       RB0, DUAL, '[Vulkan][W] some warning',
       'ShaderPreparation: startup wait finished in 90000 ms presents_other=0 presents_main=0',
       'GuestOut: hello', 'GuestOut: Level has started: ' + SKY,
       'FrameTrace: n=9 dt_us=16000 draws=50', 'FrameTrace: n=10 dt_us=16000 draws=500', 'FrameTrace: n=11 dt_us=100000 draws=500',
       'tail line']
FILES = {'replay.45.bin': b'catalogue 45', 'replay.46.bin': b'catalogue 46 longer', 'replay.cur': b'46\n'}


def put(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(t if isinstance(t, bytes) else t.encode('ascii'))


def state_text(f19=False, files=None):
    out = ['dir f10 present files 3 cache_files 2 pipelines_bin 10 abc',
           'dir f19 present files 4 cache_files 3 pipelines_bin 10 def' if f19 else 'dir f19 absent',
           'dir replay present files 3 cache_files 0 pipelines_bin absent', 'replay.cur 46']
    for n, b in sorted((files or FILES).items()):
        out.append('file %s %d %s' % (n, len(b), hashlib.sha256(b).hexdigest()))
    return '\n'.join(out) + '\n'


def env_w2():
    e = dict(R.BASE_ENV)
    e.update(KYTY_GUEST_ARGS='-lvl ' + SKY, KYTY_SHADER_SEED='0', KYTY_GATE_FILE='C:/x/gates.req', KYTY_SAMPLE_GATE='C:/x/sample.req',
             VK_LAYER_PATH='C:/VulkanSDK/1.4.357.0/Bin', VK_LAYER_DUPLICATE_MESSAGE_LIMIT='100000000', VK_SDK_PATH='C:/VulkanSDK')
    return e


def make(root):
    shutil.rmtree(root, ignore_errors=True)
    src, own = os.path.join(root, 'src'), os.path.join(root, 'own')
    for n, b in FILES.items():
        put(os.path.join(src, 'state', 's18_c19', 'replay', n), b)
        put(os.path.join(src, 'replay_known', n), b)
    put(os.path.join(own, 'seal.md'), 'seal S18c2 of the fixtures\n')
    put(os.path.join(own, 'bin.exe'), b'MZ...' + R.VERSION + b'...')
    put(os.path.join(own, 'log_s18_w2.txt'), '\n'.join(LOG) + '\n')
    put(os.path.join(own, 'stdout_s18_w2.txt'), 'Shaders: VS 1 | PS 1\nKytyPS5 git = %s, x\n' % R.REV)
    run = dict(tag='s18_w2', binary_sha256=R.BIN_EXPECT, env=env_w2(), cmdline=['kyty_emulator.exe', '--vulkan-validation', 'true'],
               prereg=dict(sha256=sha(os.path.join(own, 'seal.md'))),
               attempts=[dict(label='attempt 1', outcome='ok', hold_exit=None, hold_s=310.2, close_rc=0, close_killed=False, close_s=2.0,
                              detail=None)])
    put(os.path.join(own, 's18_w2.json'), json.dumps(run))
    d = os.path.join(own, 'runs', 's18_w2')
    for n, t in (('installed_sha.txt', R.BIN_EXPECT), ('installed_before.txt', R.FS8), ('installed_after.txt', R.FS8),
                 ('manifest_cmp.txt', 'manifest cmp EQUAL files 9 listsha 00'), ('state_in_name.txt', 'cat_full'),
                 ('state_in.txt', state_text().rstrip('\n')),
                 ('state_out.txt', 'dir f10 present files 3 cache_files 2 pipelines_bin 10 abc\ndir f19 present files 728 cache_files 727 '
                                   'pipelines_bin 20430720 5392\ndir replay present files 3 cache_files 0 pipelines_bin absent')):
        put(os.path.join(d, n), t + '\n')
    return src, own


SYN_KNOWN = tuple((n, len(b), hashlib.sha256(b).hexdigest()) for n, b in sorted(FILES.items()))


def use(src, own):
    M.SRC_ROOT = src
    M.ROOT2 = own
    M.SEAL2 = os.path.join(own, 'seal.md')
    M.KNOWN = SYN_KNOWN
    R.ROOT = src
    R.SEAL_PATH = M.SEAL2
    R.BIN_PATH = os.path.join(own, 'bin.exe')


BASE = Path('C:/kyty/s288/s18c2/fx_s18c2')   # mutlib gives every job its own copy of this directory
shutil.rmtree(BASE, ignore_errors=True)
BASE.mkdir(parents=True)
TMP = str(BASE)
K = [0]


def variant(change=None, mod=None):
    """A fresh pair of roots with the change applied; s18_w2 read; mod(M) -> a function that undoes a module change."""
    K[0] += 1
    src, own = make(os.path.join(TMP, 'v%03d' % K[0]))
    use(src, own)
    if change is not None:
        change(src, own)
    undo = mod() if mod is not None else None
    try:
        rows, meta = R.read_tag('s18_w2')
    finally:
        if undo is not None:
            undo()
    shutil.rmtree(os.path.join(TMP, 'v%03d' % K[0]), ignore_errors=True)
    return rows


def rowval(rows, prefix, kind='m'):
    for name, ok_, det in {'m': rows.mem, 'a': rows.adm, 'f': rows.form}[kind]:
        if name.startswith(prefix):
            return ok_
    return 'MISSING'


def one(change, prefix, want, kind='m', name=None, word=None, mod=None):
    rows = variant(change, mod)
    got = rowval(rows, prefix, kind)
    good = got == want and (word is None or rows.word() == word)
    return check(good, 's18_w2: %s -> %s%s (got %s, reading %s)' % (name or prefix[:60], R.yn(want) if want in (True, False, None) else want,
                                                                  '' if word is None else ' ' + word,
                                                                  R.yn(got) if got in (True, False, None) else got, rows.word()))


def logedit(old, new):
    def ch(src, own):
        p = os.path.join(own, 'log_s18_w2.txt')
        t = open(p, encoding='ascii').read()
        assert t.count(old) >= 1, old
        open(p, 'w', newline='\n').write(t.replace(old, new, 1))
    return ch


def outedit(text):
    return lambda src, own: put(os.path.join(own, 'stdout_s18_w2.txt'), text)


def jsonedit(fn):
    def ch(src, own):
        p = os.path.join(own, 's18_w2.json')
        d = json.load(open(p))
        fn(d)
        put(p, json.dumps(d))
    return ch


def setenv(key, value):
    def f(d):
        if value is None:
            d['env'].pop(key, None)
        else:
            d['env'][key] = value
    return jsonedit(f)


def setatt(**kw):
    return jsonedit(lambda d: d['attempts'][0].update(kw))


def runfile(name, text):
    return lambda src, own: put(os.path.join(own, 'runs', 's18_w2', name), text)


def setmod(name, value):
    def mod():
        old = getattr(M, name)
        setattr(M, name, value)
        return lambda: setattr(M, name, old)
    return mod


# ------------------------------------------------------------------------------------------------ baseline
src0, own0 = make(os.path.join(TMP, 'base'))
use(src0, own0)
W0, meta0 = R.read_tag('s18_w2')
ok &= check(W0.word() == 'MEMBERS_PASS', 'baseline s18_w2 reads MEMBERS_PASS (got %s %s)' % (
    W0.word(), [x for x in W0.adm + W0.form + W0.mem if x[1] is not True][:3]))
ok &= check(meta0['group'] == 'W2' and meta0['level'] == SKY, 'baseline: group W2, level Sky Garden')
ok &= check(len([x for x in W0.mem if x[0].startswith('W2 (')]) == 13 and all(x[0].startswith('W2 (') for x in W0.mem),
            'baseline: 13 members W2 (1)-(4), no other member')
ok &= check(len(W0.adm) == 15, 'baseline: 15 admission rows (12 of S18c + 3 of S18c2) (got %d)' % len(W0.adm))
ok &= check(M.paths('s18_w2')['log'].replace(chr(92), '/').startswith(own0.replace(chr(92), '/')) and
            M.paths('s18_c19')['state'].replace(chr(92), '/').startswith(src0.replace(chr(92), '/')) and R.ROOT == src0,
            'paths: s18_w2 under the S18c2 root, s18_c19 under the S18c root, the S18c root restored')
_rep = dict(W0.rep)
ok &= check(_rep.get('rebuild under the layer: records prepared rejected pending perms_new perms_cached translate_ms wall_ms') ==
            '10 9 1 0 8 0 10 20', 'report: the rebuild numbers under the layer')
ok &= check("'pipelines_bin': True" in _rep.get('%s after the run (state_out.txt)' % R.DIR1, ''), 'report: pipelines.bin after the run')
ok &= check(_rep.get('translation cache directory = %s (reference)' % R.DIR1) == 'True' and "'mode': '3'" in _rep.get('mode line (reference)', ''),
            'report: directory and mode line')
ok &= check(_rep.get('frames >= 1 s after the first scene frame / from the entry line (under the layer, reference)') == '0 / 0',
            'report: frames >= 1 s')

# ------------------------------------------------------------------------------------------------ admission
NA = 'NOT_ADMITTED'
ok &= one(None, 'S18c reader s18c_read.py', False, 'a', 'S18c reader other than the seal', NA, setmod('BASE_SHA', '0' * 64))
ok &= one(None, 'catalogue replay_known = manifest', False, 'a', 'replay_known other than the manifest', NA,
          setmod('KNOWN', SYN_KNOWN[:2] + (('replay.cur', 3, '0' * 64),)))
ok &= one(None, 'catalogue replay_known = state/', True, 'a', 'manifest other: replay_known = state/s18_c19 still YES', NA,
          setmod('KNOWN', SYN_KNOWN[:2]))
ok &= one(lambda s, o: put(os.path.join(s, 'state', 's18_c19', 'replay', 'replay.cur'), b'45\n'), 'catalogue replay_known = state/', False,
          'a', 'state/s18_c19 other than replay_known', NA)
ok &= one(lambda s, o: put(os.path.join(s, 'replay_known', 'extra.bin'), b'x'), 'catalogue replay_known = manifest', False, 'a',
          'an extra file in replay_known', NA)
ok &= one(lambda s, o: shutil.rmtree(os.path.join(s, 'replay_known')), 'catalogue replay_known = state/', False, 'a', 'no replay_known', NA)
ok &= one(lambda s, o: os.makedirs(os.path.join(s, 'replay_known', 'sub')), 'catalogue replay_known = manifest', True, 'a',
          'a subfolder of replay_known is not a file (go_s18c2.sh refuses it by ls)', 'MEMBERS_PASS')
ok &= one(lambda s, o: (shutil.rmtree(os.path.join(s, 'replay_known')), shutil.rmtree(os.path.join(s, 'state'))),
          'catalogue replay_known = state/', False, 'a', 'neither replay_known nor state/s18_c19 (empty = empty is NO)', NA)
for k, v, nm in (('KYTY_SHADER_SEED', None, 'no KYTY_SHADER_SEED'), ('KYTY_SHADER_SEED', '1', 'KYTY_SHADER_SEED=1'),
                 ('KYTY_S_REPLAY', '3', 'KYTY_S_REPLAY=3'), ('KYTY_S_REPLAY_TEST', '', 'empty KYTY_S_REPLAY_TEST'),
                 ('KYTY_S_REPLAY_TEST', 'stop', 'KYTY_S_REPLAY_TEST=stop'), ('KYTY_FIX_F19', '1', 'KYTY_FIX_F19=1'),
                 ('KYTY_PIPELINE_PRECACHE', '0', 'KYTY_PIPELINE_PRECACHE=0'), ('KYTY_REC', 'C:/x.mp4', 'KYTY_REC at W'),
                 ('VK_LAYER_PATH', None, 'no VK_LAYER_PATH'), ('VK_LAYER_DUPLICATE_MESSAGE_LIMIT', '1000000', 'layer limit 1000000'),
                 ('VK_LAYER_MESSAGE_ID_FILTER', 'x', 'a message filter'), ('KYTY_GUEST_ARGS', '-lvl ' + R.MGG, 'other level')):
    ok &= one(setenv(k, v), 'environment', False, 'a', nm, NA)
ok &= one(jsonedit(lambda d: d.update(cmdline=['k', '--vulkan-validation', 'false'])), 'command line', False, 'a', 'validation false', NA)
ok &= one(jsonedit(lambda d: d.update(binary_sha256='0' * 64)), 'binary of the run', False, 'a', 'json binary other', NA)
ok &= one(runfile('installed_sha.txt', '0' * 64 + '\n'), 'binary of the run', False, 'a', 'installed_sha other', NA)
ok &= one(jsonedit(lambda d: d.update(prereg=dict(sha256='0' * 64))), 'prereg sha256', False, 'a', 'prereg other than the seal', NA)
ok &= one(jsonedit(lambda d: d.update(attempts=d['attempts'] * 2)), 'run record', False, 'a', 'two attempts', NA)
ok &= one(runfile('state_in_name.txt', 'inst_cat\n'), 'input state name', False, 'a', 'input state inst_cat', NA)
ok &= one(runfile('state_in.txt', state_text(f19=True)), 'input state cat_full: variant', False, 'a', 'input with _fixf19 present', NA)
ok &= one(runfile('state_in.txt', state_text(files=dict(FILES, **{'replay.cur': b'45\n'}))), 'input state cat_full: replay', False, 'a',
          'input replay other than state/s18_c19', NA)
ok &= one(logedit('tail line', 'Window 1 minimized'), 'no window minimized', False, 'a', 'window minimized', NA)
ok &= one(logedit('tail line', 'Recovering Vulkan swapchain'), 'no window minimized', False, 'a', 'Recovering Vulkan swapchain', NA)
ok &= one(logedit('arigandores/KytyPS5 %s' % R.REV, 'arigandores/KytyPS5 62ff7b5'), 'revision texts', False, 'a', 'other revision', NA)


def nobin():
    old = R.BIN_PATH
    R.BIN_PATH = os.path.join(TMP, 'nobin.exe')

    def undo():
        R.BIN_PATH = old
    return undo


ok &= one(None, 'version string', False, 'a', 'version string missing', NA, nobin)
ok &= one(lambda s, o: os.remove(os.path.join(o, 'log_s18_w2.txt')), 'emulator log present', False, 'a', 'no log', NA)
ok &= one(logedit('tail line', 'ShaderSeed: installed 727 shaders'), 'W2 (1) no line ShaderSeed', False, 'm',
          'ShaderSeed installed is member (1), not admission', 'MEMBERS_FAIL')
# ------------------------------------------------------------------------------------------------ form
ok &= one(runfile('installed_after.txt', '0' * 64 + '\n'), 'installed binary before = after', False, 'f', 'installed after other', 'FORM_FAIL')
ok &= one(runfile('installed_before.txt', '1' * 64 + '\n'), 'installed binary before = after', False, 'f', 'installed before not FS8',
          'FORM_FAIL')
ok &= one(runfile('manifest_cmp.txt', 'manifest cmp DIFFER only-before 1\n'), 'manifest of the caches', False, 'f', 'manifest DIFFER',
          'FORM_FAIL')
# ------------------------------------------------------------------------------------------------ member (1)
MF = 'MEMBERS_FAIL'
ok &= one(logedit(RB0, 'other'), 'W2 (1) a line ShaderReplay: rebuild records=', False, name='no rebuild line', word=MF)
ok &= one(logedit(RB0, 'ShaderReplay: rebuild queued groups=3'), 'W2 (1) a line ShaderReplay: rebuild records=', False,
          name='a rebuild line without records=', word=MF)
ok &= one(logedit(RB0, 'ShaderReplay: rebuild skipped reason=recipes_current'), 'W2 (1) no line rebuild skipped', False,
          name='rebuild skipped instead', word=MF)
ok &= one(logedit('tail line', 'ShaderReplay: rebuild skipped reason=recipes_current'), 'W2 (1) no line rebuild skipped', False,
          name='rebuild and rebuild skipped', word=MF)
ok &= one(outedit('Shaders: VS 1\nShaderSeed: installed 3\nKytyPS5 git = %s, x\n' % R.REV), 'W2 (1) no line ShaderSeed', False,
          name='ShaderSeed installed in stdout', word=MF)
# ------------------------------------------------------------------------------------------------ member (2)
ok &= one(None, 'W2 (2) share', True, name='share 9 / 10 = 0.90 (edge) YES')
ok &= one(logedit(RB0, rb(100, 89, 11)), 'W2 (2) share', False, name='share 89 / 100 = 0.89', word=MF)
ok &= one(logedit(RB0, rb(100, 90, 10)), 'W2 (2) share', True, name='share 90 / 100 = 0.90 YES')
ok &= one(logedit(RB0, rb(0, 0, 0)), 'W2 (2) share', None, name='records 0 - not determined', word='NOT_EVALUABLE')
ok &= one(logedit(RB0, rb(10, 9, 1, 1)), 'W2 (2) identity', False, name='9 + 1 + 1 != 10', word=MF)
ok &= one(logedit(RB0, rb(10, 8, 1, 1)), 'W2 (2) identity', True, name='8 + 1 + 1 = 10 with pending YES')
ok &= one(logedit(RB0, rb(pb='stopped')), 'W2 (2) pipelines_bin=written', False, name='pipelines_bin=stopped', word=MF)
ok &= one(logedit('tail line', rb(pb='failed')), 'W2 (2) pipelines_bin=written', False, name='the last rebuild line counts', word=MF)
ok &= one(logedit(RB0, rb(10, 5, 0, 5, pb='stopped') + '\n' + RB0), 'W2 (2) pipelines_bin=written', True,
          name='a stopped line then the written one YES')
ok &= one(logedit(RB0, 'other'), 'W2 (2) share', None, name='no rebuild line: share not determined')
ok &= one(logedit(RB0, 'other'), 'W2 (2) identity', None, name='no rebuild line: identity not determined')
# ------------------------------------------------------------------------------------------------ member (3)
ok &= one(logedit('tail line', '[Vulkan][E] VUID x'), 'W2 (3) 0 [Vulkan][E]', False, name='one error', word=MF)
ok &= one(logedit('tail line', 'Validation: this will be the last time reporting it'), 'W2 (3) 0 limit lines', False,
          name='one limit line', word=MF)
ok &= one(logedit('[Vulkan][W] some warning', 'other'), 'W2 (3) positive control', False, name='no warning line', word=MF)
ok &= one(logedit(DUAL, 'other'), 'W2 (3) positive control', False, name='no DualSrcBlend line', word=MF)
ok &= one(logedit(DUAL, 'DualSrcBlend: supported=1 enabled=0'), 'W2 (3) positive control', False, name='dual enabled 0', word=MF)
ok &= one(logedit(DUAL, 'DualSrcBlend: supported=0 enabled=1'), 'W2 (3) positive control', False, name='dual supported 0', word=MF)
ok &= one(lambda s, o: (logedit(DUAL, 'other')(s, o), logedit('tail line', DUAL)(s, o)), 'W2 (3) positive control', False,
          name='DualSrcBlend after the first GuestOut', word=MF)
ok &= one(lambda s, o: (logedit('tail line', '[Vulkan][E] VUID x')(s, o), setatt(outcome='exited', detail='exit code 1', hold_s=20.0)(s, o)),
          'W2 (3) no VALIDATION_STOP', False, name='E and the process ended (VALIDATION_STOP)', word=MF)
ok &= one(lambda s, o: (logedit('tail line', '[Vulkan][E] VUID x')(s, o), setatt(hold_s=309.9)(s, o)),
          'W2 (3) no VALIDATION_STOP', False, name='E and hold 309.9 s (VALIDATION_STOP)', word=MF)
ok &= one(logedit('tail line', '[Vulkan][E] VUID x'), 'W2 (3) no VALIDATION_STOP', True, name='E but lived 310 s: no VALIDATION_STOP')
ok &= one(setatt(outcome='exited', detail='exit code 1', hold_s=20.0), 'W2 (3) no VALIDATION_STOP', True,
          name='ended without E: no VALIDATION_STOP', word=MF)
# ------------------------------------------------------------------------------------------------ member (4)
ok &= one(logedit('GuestOut: Level has started: ', 'GuestOut: y: '), 'W2 (4) entered', False, name='not entered', word=MF)
ok &= one(logedit('Level has started: ' + SKY, 'Level has started: ' + R.MGG), 'W2 (4) entered', False, name='other level started', word=MF)
ok &= one(setatt(outcome='timeout'), 'W2 (4) entered', False, name='outcome timeout', word=MF)
ok &= one(setatt(hold_s=309.9), 'W2 (4) the process lived', False, name='hold 309.9 s', word=MF)
ok &= one(setatt(hold_s=310.0), 'W2 (4) the process lived', True, name='hold 310.0 s (edge)')
ok &= one(setatt(hold_exit='died'), 'W2 (4) the process lived', False, name='hold_exit set', word=MF)
ok &= one(logedit('tail line', 'Unhandled exception: x'), 'W2 (4) 0 death markers', False, name='death marker in the log', word=MF)
ok &= one(outedit('KytyPS5 git = %s, x\n--- Fatal Error ---\n' % R.REV), 'W2 (4) 0 death markers', False, name='death marker in stdout',
          word=MF)
ok &= one(logedit('tail line', 'GpuHangAbort: 8 s'), 'W2 (4) 0 death markers', False, name='GpuHangAbort', word=MF)

# ------------------------------------------------------------------------------------------------ dispatch, outputs
use(src0, own0)
_r = R.scan(os.path.join(own0, 'log_s18_w2.txt'), SKY)
_so = R.stdout_scan(os.path.join(own0, 'stdout_s18_w2.txt'))
_rows = R.Rows()
M.w_rows(_rows, 's18_w', _r, _so, dict(outcome='ok', hold_s=310.0, hold_exit=None), {})
ok &= check(_rows.mem and all(x[0].startswith('W ') for x in _rows.mem), 'dispatch: the S18c tag s18_w is read by the S18c W group')
ok &= check(R.w_rows is M.w_rows and R.paths is M.paths, 'the S18c reader reads through the S18c2 paths and dispatch')
jp = os.path.join(TMP, 'w2.json')
with contextlib.redirect_stdout(io.StringIO()) as _o:
    _rc = M.main(['s18_w2', '--json', jp])
jd = json.load(open(jp))
ok &= check(_rc == 0 and jd['reading'] == 'MEMBERS_PASS' and jd['group'] == 'W2' and jd['extra']['rebuild']['records'] == '10' and
            'S18c2 reader over s18c_read.py sha256 ' + M.BASE_SHA in _o.getvalue(), 'json output of s18_w2 and the reader line')
shutil.copy(jp, os.path.join(own0, 'runs', 's18_w2', 'read.json'))
with contextlib.redirect_stdout(io.StringIO()) as _o:
    M.table()
tb = _o.getvalue()
ok &= check('S18c2 tag s18_w2' in tb and 'READING MEMBERS_PASS' in tb and tb.count('NOT READ') == 25 and 'W2 (3) 0 [Vulkan][E]' in tb,
            'table: the 25 S18c tags (not in the synthetic root) and the row of s18_w2')
with contextlib.redirect_stdout(io.StringIO()):
    _rc1, _rc2, _rc3 = M.main([]), M.main(['s18_w']), M.main(['x'])
ok &= check(_rc1 == 2 and _rc2 == 2 and _rc3 == 2, 'no argument, the S18c tag s18_w, an unknown tag -> rc 2')
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        M.main(['s18_w2'])
        M.main(['--table'])
        M.main([])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
ok &= check(cp_ok and len(raw.getvalue()) > 1000, 'output in strict cp1250 without PYTHONIOENCODING')

print('checks %d' % N[0])
print('ALL OK' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
