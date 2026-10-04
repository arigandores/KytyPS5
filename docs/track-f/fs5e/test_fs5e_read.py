"""Track F link FS5e (HPP-513): fixtures of fs5e_read.py - every member and reference row and every edge: the binary (installed before
= of the tag = 631ff987; 31cbfee8 before; missing), the directory row, entered, hold 300 s / 300 s - 1 us, process end, death markers in
the log / stdout, video 3000 / 2999 / missing, glitches 0 / 1 / unread, sheet, the warm form (size > 0 / 0 / absent / no file), the
cold form (reference), frames >= 1 s (reference only), interference (minimized / Recovering / GamePatch -> INTERFERENCE even when a member
fails), the verdict line PASS / FAIL / INTERFERENCE, the sealed import of fs5c_read.py, output in strict cp1250 without PYTHONIOENCODING.
The first output line names the suite and the target with their sha256; the last line is ALL OK.  ASCII only."""
import hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'fs5e_read.py')
sys.path.insert(0, HERE)
import fs5e_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_fs5e_read.py sha256 %s target fs5e_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(TARGET)))
OK = True
N = 0
NF = 0
TMP = tempfile.mkdtemp(prefix='fs5e_fx_')
FS5 = R.BIN_EXPECT
FS4 = '31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5'
STC_FIX = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10'
STC_BASE = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b'
PC_COLD = 'PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10\\pipelines.bin yet'
FSV = 'FixSval: mode=1 ubo_std_layout=1'
ENTRY = 'GuestOut: Level has started: underwater_aerial_garden'
COLD = 'cold form: C:/x/variant_fixb26_fixb1b_fixf10 absent at 2026-10-04T00:00:00Z; entries of _ShaderCache/PPSA21564: 2'
WARM = 'warm form after the tag: C:/x/variant_fixb26_fixb1b_fixf10 files 120; pipelines.bin present size 3945014'
FORK = 'Fork build arigandores/KytyPS5 0e72bc1'
ES_OK = {'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': None, 'hold_s': 330.1, 'stable_s': 40.0}]}
ES_EXIT = {'attempts': [{'outcome': 'exited', 'detail': 'exit code 5', 'hold_exit': None, 'hold_s': None, 'stable_s': None}]}
HEAD = [FORK, FSV, STC_FIX, PC_COLD, 'GuestOut: boot']


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


def make(log, stdout='', run=ES_OK, idx=3000, glitch='one-frame glitches: 0', sheet='sheet: x.png frames 3000 step 1 tiles 8x6',
         sha_t=FS5, before=FS5, cold=COLD, warm=WARM):
    CNT[0] += 1
    d = os.path.join(TMP, 'fx%03d' % CNT[0])
    os.makedirs(d)
    with open(os.path.join(d, 'log.txt'), 'wb') as f:
        f.write(('\n'.join(log) + '\n').encode('utf-8'))
    with open(os.path.join(d, 'stdout.txt'), 'wb') as f:
        f.write(stdout.encode('utf-8'))
    if run is not None:
        with open(os.path.join(d, 'es.json'), 'w') as f:
            json.dump(run, f)
    if idx is not None:
        with open(os.path.join(d, 'rec.idx'), 'wb') as f:
            f.write(b'x\n' * idx)
    for fn, t in (('glitch.txt', glitch), ('sheet.txt', sheet), ('installed_sha.txt', sha_t), ('installed_before.txt', before),
                  ('cold.txt', cold), ('warm.txt', warm)):
        if t is not None:
            with open(os.path.join(d, fn), 'wb') as f:
                f.write((t + '\n').encode('utf-8'))
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


# ---- constants and the sealed import
check('constants', R.BIN_EXPECT.startswith('631ff987') and R.REV == '0e72bc1' and R.DIR_FIX == 'variant_fixb26_fixb1b_fixf10'
      and R.LEVEL == 'underwater_aerial_garden' and R.TAG == 'fs5_i')
check('fs5c_read imported from FS5c', os.path.normcase(os.path.abspath(R.C.__file__)).endswith(os.path.normcase('fs5c\\fs5c_read.py'))
      or R.C.__file__.replace('\\', '/').endswith('fs5/fs5c/fs5c_read.py'))

# ---- positive
res, m, lines = rm(make(HEAD + scene()))
for nm in ('binary', 'translation cache directory', 'entered', 'hold >= 300 s', 'no process end', '0 death markers', 'video index records',
           '0 one-frame glitches', 'sheet for the lead', 'warm form after'):
    check('pos MEMBER %s YES' % nm, row(m, 'MEMBER ' + nm) == 'YES')
for nm in ('revision text', 'cold form', 'frames >= 1 s after the first scene frame = 0', 'FixSval', '0 lines SPIR-V'):
    check('pos REFERENCE %s YES' % nm, row(m, 'REFERENCE ' + nm) == 'YES')
check('pos interference none YES', row(m, 'INTERFERENCE') == 'YES')
check('pos verdict PASS', lines[-1] == 'WARMUP VERDICT fs5_i: PASS')
check('pos 10 members, 5 references', sum(1 for k in m if k.startswith('MEMBER')) == 10 and sum(1 for k in m if k.startswith('REFERENCE')) == 5)
check('no manifest equality rows (caches not returned)', not any('manifest' in k for k in m))

FAILV = 'WARMUP VERDICT fs5_i: FAIL'
# ---- binary
for nm, kw in (('before 31cbfee8', dict(before=FS4)), ('tag 31cbfee8', dict(sha_t=FS4)), ('before missing', dict(before=None)),
               ('tag missing', dict(sha_t=None))):
    r_, v_ = case(HEAD + scene(), 'MEMBER binary', **kw)
    check('binary %s: NO, FAIL' % nm, r_ == 'NO' and v_ == FAILV)
# ---- directory
for nm, log in (('base dir', [FORK, FSV, STC_BASE, PC_COLD, 'GuestOut: b'] + scene()),
                ('mixed dirs', [FORK, FSV, STC_FIX, STC_BASE, PC_COLD, 'GuestOut: b'] + scene()),
                ('no dir line', [FORK, FSV, PC_COLD, 'GuestOut: b'] + scene()),
                ('suffix', [FORK, FSV, STC_FIX + '_x', PC_COLD, 'GuestOut: b'] + scene())):
    r_, v_ = case(log, 'MEMBER translation cache directory')
    check('dir %s: NO, FAIL' % nm, r_ == 'NO' and v_ == FAILV)
r_, v_ = case([FORK, FSV, STC_FIX.replace('\\', '/'), PC_COLD, 'GuestOut: b'] + scene(), 'MEMBER translation cache directory')
check('dir forward slashes: YES, PASS', r_ == 'YES' and v_.endswith('PASS'))
# ---- entry and hold
r_, v_ = case(HEAD + scene(entry='GuestOut: Level has started: hoover_beach'), 'MEMBER entered')
check('other level: entered NO, FAIL', r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(300000000 - 1), 'MEMBER hold >= 300 s')
check('hold 300 s - 1 us: NO, FAIL', r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(300000000), 'MEMBER hold >= 300 s')
check('hold 300 s: YES, PASS', r_ == 'YES' and v_.endswith('PASS'))
d = make(HEAD + [ENTRY, ft(1, 1, 50), ft(2, 1, 400), ft(3, 100000000, 400), 'GuestOut: Level has started: other', ft(4, 400000000, 400)])
res, m, lines = rm(d)
check('scene change: rows after it not counted, FAIL', res['hold_us'] == 100000000 and lines[-1] == FAILV)
# ---- process end, death
r_, v_ = case(HEAD + scene(), 'MEMBER no process end', run=ES_EXIT)
check('exited: NO, FAIL', r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER no process end', run=None)
check('no run json: NOT_READ, FAIL', r_ == 'NOT_READ' and v_ == FAILV)
r_, v_ = case(HEAD + scene() + ['GpuHangAbort: x'], 'MEMBER 0 death markers')
check('death in the log: NO, FAIL', r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER 0 death markers', stdout='--- Fatal Error ---\n')
check('death in the stdout: NO, FAIL', r_ == 'NO' and v_ == FAILV)
# ---- video
for nm, kw, want in (('2999', dict(idx=2999), 'NO'), ('no index', dict(idx=None), 'NO')):
    r_, v_ = case(HEAD + scene(), 'MEMBER video index records', **kw)
    check('video %s: %s, FAIL' % (nm, want), r_ == want and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER 0 one-frame glitches', glitch='one-frame glitches: 1')
check('1 glitch: NO, FAIL', r_ == 'NO' and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER 0 one-frame glitches', glitch='error')
check('glitch unread: NOT_READ, FAIL', r_ == 'NOT_READ' and v_ == FAILV)
r_, v_ = case(HEAD + scene(), 'MEMBER sheet for the lead', sheet='error')
check('no sheet: NO, FAIL', r_ == 'NO' and v_ == FAILV)
# ---- warm form
for nm, w in (('size 0', 'warm form after the tag: x files 1; pipelines.bin present size 0'),
              ('absent', 'warm form after the tag: x files 0; pipelines.bin ABSENT'), ('no file', None)):
    r_, v_ = case(HEAD + scene(), 'MEMBER warm form after', warm=w)
    check('warm %s: NO, FAIL' % nm, r_ == 'NO' and v_ == FAILV)
# ---- references never decide
r_, v_ = case(HEAD + scene(k2=2), 'REFERENCE frames >= 1 s after the first scene frame = 2')
check('2 frames >= 1 s: reference NO, verdict PASS', r_ == 'NO' and v_.endswith('PASS'))
r_, v_ = case(HEAD + scene(), 'REFERENCE cold form', cold='warm form: present')
check('cold.txt without absent: reference NO, PASS', r_ == 'NO' and v_.endswith('PASS'))
r_, v_ = case([FORK, STC_FIX, PC_COLD, 'GuestOut: b', FSV] + scene(), 'REFERENCE FixSval')
check('FixSval after GuestOut: reference NO, PASS', r_ == 'NO' and v_.endswith('PASS'))
r_, v_ = case(HEAD + scene() + ['[Vulkan] SPIR-V validation failed: hash=0xAB'], 'REFERENCE 0 lines SPIR-V')
check('validation failed line: reference NO, PASS', r_ == 'NO' and v_.endswith('PASS'))
r_, v_ = case(['Fork build arigandores/KytyPS5 3d0e46d'] + HEAD[1:] + scene(), 'REFERENCE revision text')
check('other revision: reference NO, PASS', r_ == 'NO' and v_.endswith('PASS'))
res, m, lines = rm(make(HEAD + scene() + ['AsyncPipelines: skipped draw x'] * 3 + ['Window 1 lost keyboard focus']))
check('skipped draw and focus: data only, PASS', res['skipped_draw'] == 3 and lines[-1].endswith('PASS'))
# ---- interference
for nm, extra in (('minimized', 'Window 1 minimized'), ('recovering', 'Recovering Vulkan swapchain'), ('gamepatch', 'GamePatch: loaded x')):
    r_, v_ = case(HEAD + scene() + [extra], 'INTERFERENCE')
    check('interference %s: NO, INTERFERENCE' % nm, r_ == 'NO' and v_ == 'WARMUP VERDICT fs5_i: INTERFERENCE')
r_, v_ = case(HEAD + scene() + ['Window 1 minimized'], 'INTERFERENCE', idx=10)
check('interference wins over a failed member', v_ == 'WARMUP VERDICT fs5_i: INTERFERENCE')

# ---- output: ASCII, strict cp1250 without PYTHONIOENCODING, json, usage
d = make(['Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10\\\u043a\u044d\u0448',
          'Release, x, ver = 1, git = \u0432\u0435\u0440\u0441\u0438\u044f, date = y', FSV, PC_COLD, 'GuestOut: boot'] + scene(),
         stdout='\u043e\u0448\u0438\u0431\u043a\u0430\n')
env = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
env['PYTHONIOENCODING'] = 'cp1250:strict'
p = subprocess.run([sys.executable, TARGET, '--dir', d], capture_output=True, env=env)
check('cp1250 strict: rc 0, ASCII, verdict printed', p.returncode == 0 and all(b < 128 for b in p.stdout) and b'WARMUP VERDICT fs5_i:' in p.stdout)
env2 = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
jp = os.path.join(TMP, 'out.json')
p2 = subprocess.run([sys.executable, TARGET, '--dir', make(HEAD + scene()), '--json', jp], capture_output=True, env=env2)
check('no PYTHONIOENCODING: rc 0, json verdict PASS', p2.returncode == 0 and json.load(open(jp))['verdict'] == 'PASS')
p3 = subprocess.run([sys.executable, TARGET, 'fs5_v'], capture_output=True, env=env2)
check('other tag refused', p3.returncode != 0)

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d fails %d' % (N, NF))
print('ALL OK' if OK else 'SOME FAILED')
