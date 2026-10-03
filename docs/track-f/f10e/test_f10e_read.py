"""F10e (HPP-453): fixtures of f10e_read.py - every row of the seal section 4 and every edge (151 / 150 / no FixSvalStat line, hold
300 s / 300 s - 1 us, 3000 / 2999 video records, FixSval before / after the first GuestOut, the cold form members, manifest EQUAL /
DIFFER / missing, process end per kind), the reference text after ', git = ' (RC2: never a gate), output in strict cp1250 without
PYTHONIOENCODING.  The first output line names the suite and the target with their sha256; the last line is ALL OK.  ASCII only."""
import hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'f10e_read.py')
sys.path.insert(0, HERE)
import f10e_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f10e_read.py sha256 %s target f10e_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(TARGET)))
OK = True
N = 0
TMP = tempfile.mkdtemp(prefix='f10e_fx_')
GOOD_SHA = R.BIN_EXPECT
STC = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b'
PRE_COLD = 'PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b\\pipelines.bin yet'
PRE_WARM = 'PipelinePrecache: 1357 recipes -> 1234 graphics + 123 compute pipelines queued, 0 skipped, 2551 sources loaded'
FS1 = 'FixSval: mode=1 ubo_std_layout=1'
FS0 = 'FixSval: mode=0 ubo_std_layout=1'
ENTRY = 'GuestOut: Level has started: underwater_aerial_garden'
FAIL1 = '[ps] SPIR-V validation failed hash=0x00000000deadbeef:'
FAIL2 = 'ps failed hash=0x00000000deadbeef: SPIR-V validation failed'
DUAL = 'DualSrcBlend: supported=1 enabled=1'


def ft(n, dt, draws):
    return 'FrameTrace: n=%d dt_us=%d draws=%d' % (n, dt, draws)


def scene(hold_us=300000000):
    """entry, the first scene frame (not counted), then rows that sum to hold_us."""
    out = [ENTRY, ft(1, 16667, 50), ft(2, 16667, 400)]
    rest, n = hold_us, 3
    while rest > 0:
        d = min(rest, 100000000)
        out.append(ft(n, d, 400))
        rest -= d
        n += 1
    return out


def make(name, kind, log, stdout='', run=None, idx=None, glitch='one-frame glitches: 0', sheet='sheet: x.png frames 3000 step 1 tiles 8x6',
         sha_t=GOOD_SHA, cold='cold form: C:/x/variant_fixb26_fixb1b absent at 2026-10-03T00:00:00Z', mcmp='manifest cmp EQUAL files 3 listsha ab'):
    d = os.path.join(TMP, name)
    os.makedirs(d)
    with open(os.path.join(d, 'log.txt'), 'wb') as f:
        f.write(('\n'.join(log) + '\n').encode('utf-8'))
    with open(os.path.join(d, 'stdout.txt'), 'wb') as f:
        f.write(stdout.encode('utf-8'))
    if run is not None:
        with open(os.path.join(d, 'run.json' if kind == 'r0' else 'es.json'), 'w') as f:
            json.dump(run, f)
    if idx is not None:
        with open(os.path.join(d, 'rec.idx'), 'wb') as f:
            f.write(b'x\n' * idx)
    for fn, t in (('glitch.txt', glitch), ('sheet.txt', sheet), ('installed_sha.txt', sha_t), ('cold.txt', cold), ('manifest_cmp.txt', mcmp)):
        if t is not None:
            with open(os.path.join(d, fn), 'wb') as f:
                f.write((t + '\n').encode('utf-8'))
    return d


def rowmap(d, kind):
    res = R.read(R.paths('fixture', kind, d), kind)
    out = {}
    for line in R.rows('fixture', res):
        if line.startswith('  ROW '):
            k, v = line[6:].rsplit(': ', 1)
            out[k] = v
    return res, out


def check(name, cond):
    global OK, N
    N += 1
    if not cond:
        OK = False
        print('FAIL %s' % name)


def row(rm, prefix):
    hits = [v for k, v in rm.items() if k.startswith(prefix)]
    return hits[0] if len(hits) == 1 else 'AMBIGUOUS %d' % len(hits)


R0_OK_RUN = {'how': 'exit rc 321', 'rc': 321, 'exit_s': 41.2, 'wall_s': 43.0}
R0_TO_RUN = {'how': 'timeout, WM_CLOSE rc 0', 'rc': 0, 'exit_s': None, 'wall_s': 300.4}
ES_OK = {'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': None, 'hold_s': 330.1, 'stable_s': 40.0}]}
ES_EXIT = {'attempts': [{'outcome': 'exited', 'detail': 'exit code 321', 'hold_exit': None, 'hold_s': None, 'stable_s': None}]}
ES_HOLD_EXIT = {'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': 321, 'hold_s': 50.0, 'stable_s': 40.0}]}

# ---- kind_of
check('kind r0', R.kind_of('f10e_r0') == 'r0')
check('kind r1', R.kind_of('f10e_r1') == 'r1')
check('kind w', R.kind_of('f10e_w') == 'w')
try:
    R.kind_of('fs3_w')
    check('kind unknown raises', False)
except SystemExit:
    check('kind unknown raises', True)

# ---- R0 positive (the defect reproduced)
r0_log = ['Release, clang, ver = 0.1, git = KytyPS5-2026-09-15-6a2987a-1959-g465f0d8e, date = x', STC, FS0, PRE_COLD, 'GuestOut: x', FAIL1, 'body', FAIL2,
          '--- Error ---']
d = make('r0_pos', 'r0', r0_log, run=R0_OK_RUN)
res, rm = rowmap(d, 'r0')
check('r0 binary YES', row(rm, 'binary sha256') == 'YES')
check('r0 git reference read', res['git'] == 'KytyPS5-2026-09-15-6a2987a-1959-g465f0d8e')
check('r0 cold YES', row(rm, 'cold form') == 'YES')
check('r0 FixSval mode=0 YES', row(rm, 'FixSval mode=0') == 'YES')
check('r0 fail YES', row(rm, 'R0: >= 1 line') == 'YES')
check('r0 fail count 2, 1 hash', res['fail_log'] == 2 and res['fail_hashes'] == ['00000000deadbeef'])
check('r0 ended YES', row(rm, 'R0: the process ended') == 'YES')
check('r0 nostat YES', row(rm, 'R0: 0 FixSvalStat') == 'YES')
check('r0 reproduced YES', row(rm, 'R0: defect reproduced') == 'YES')
check('r0 manifest YES', row(rm, 'manifest of the caches') == 'YES')
check('r0 has no R1 rows', not any(k.startswith('R1:') for k in rm))
# git label of another revision does not change the binary row (RC2)
d = make('r0_git_other', 'r0', [x.replace('g465f0d8e', 'g68602c4f') for x in r0_log], run=R0_OK_RUN)
res, rm = rowmap(d, 'r0')
check('r0 git other: binary still YES', row(rm, 'binary sha256') == 'YES' and res['git'].endswith('g68602c4f'))
# no git line at all
d = make('r0_nogit', 'r0', r0_log[1:], run=R0_OK_RUN)
res, rm = rowmap(d, 'r0')
check('r0 no git line: None, binary YES', res['git'] is None and row(rm, 'binary sha256') == 'YES')
# not reproduced: no failure, timeout
d = make('r0_norep', 'r0', [STC, FS0, PRE_COLD, 'GuestOut: x'] + scene(), run=R0_TO_RUN)
res, rm = rowmap(d, 'r0')
check('r0 norep fail NO', row(rm, 'R0: >= 1 line') == 'NO')
check('r0 norep ended NO', row(rm, 'R0: the process ended') == 'NO')
check('r0 norep reproduced NO', row(rm, 'R0: defect reproduced') == 'NO')
# failure only in stdout, process ended
d = make('r0_stdout', 'r0', [STC, FS0, PRE_COLD], stdout=FAIL2 + '\n', run=R0_OK_RUN)
res, rm = rowmap(d, 'r0')
check('r0 stdout fail counts', res['fail_stdout'] == 1 and row(rm, 'R0: defect reproduced') == 'YES')
# failure but no exit (one member only)
d = make('r0_noexit', 'r0', [STC, FS0, PRE_COLD, FAIL1], run=R0_TO_RUN)
res, rm = rowmap(d, 'r0')
check('r0 fail without exit: reproduced NO', row(rm, 'R0: defect reproduced') == 'NO')
# exit without failure line
d = make('r0_nofail', 'r0', [STC, FS0, PRE_COLD], run=R0_OK_RUN)
res, rm = rowmap(d, 'r0')
check('r0 exit without fail: reproduced NO', row(rm, 'R0: defect reproduced') == 'NO')
# run record missing
d = make('r0_norun', 'r0', r0_log, run=None)
res, rm = rowmap(d, 'r0')
check('r0 no run.json: ended NOT_READ', row(rm, 'R0: the process ended') == 'NOT_READ' and row(rm, 'R0: defect reproduced') == 'NO')
# stat line at =0 (reference)
d = make('r0_stat', 'r0', r0_log + ['FixSvalStat: validated=256 rejected=0'], run=R0_OK_RUN)
res, rm = rowmap(d, 'r0')
check('r0 stat line: reference NO', row(rm, 'R0: 0 FixSvalStat') == 'NO')
# FixSval mode=1 at r0
d = make('r0_mode1', 'r0', [STC, FS1, PRE_COLD, FAIL1], run=R0_OK_RUN)
res, rm = rowmap(d, 'r0')
check('r0 mode=1: FixSval row NO', row(rm, 'FixSval mode=0') == 'NO')

# ---- binary / cold / manifest members
d = make('bad_sha', 'r0', r0_log, run=R0_OK_RUN, sha_t='4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac')
check('bad sha: binary NO', row(rowmap(d, 'r0')[1], 'binary sha256') == 'NO')
d = make('no_sha', 'r0', r0_log, run=R0_OK_RUN, sha_t=None)
check('no sha file: binary NO', row(rowmap(d, 'r0')[1], 'binary sha256') == 'NO')
d = make('warm', 'r0', [STC, FS0, PRE_WARM, FAIL1], run=R0_OK_RUN)
check('warm precache: cold NO', row(rowmap(d, 'r0')[1], 'cold form') == 'NO')
d = make('stc_other', 'r0', ['Shader translation cache: _ShaderCache\\PPSA21564', FS0, PRE_COLD, FAIL1], run=R0_OK_RUN)
check('other cache dir: cold NO', row(rowmap(d, 'r0')[1], 'cold form') == 'NO')
d = make('no_cold_txt', 'r0', r0_log, run=R0_OK_RUN, cold=None)
check('no cold.txt: cold NO', row(rowmap(d, 'r0')[1], 'cold form') == 'NO')
d = make('cold_txt_present', 'r0', r0_log, run=R0_OK_RUN, cold='cold form FAILED: still exists')
check('cold.txt without absent: cold NO', row(rowmap(d, 'r0')[1], 'cold form') == 'NO')
d = make('no_precache', 'r0', [STC, FS0, FAIL1], run=R0_OK_RUN)
check('no precache line: cold NO', row(rowmap(d, 'r0')[1], 'cold form') == 'NO')
d = make('m_differ', 'r0', r0_log, run=R0_OK_RUN, mcmp='manifest cmp DIFFER only-before 1 only-after 1')
check('manifest DIFFER: NO', row(rowmap(d, 'r0')[1], 'manifest of the caches') == 'NO')
d = make('m_missing', 'r0', r0_log, run=R0_OK_RUN, mcmp=None)
check('manifest missing: NO', row(rowmap(d, 'r0')[1], 'manifest of the caches') == 'NO')

# ---- R1 positive
r1_head = [STC, FS1, PRE_COLD, 'GuestOut: boot']
stat = ['FixSvalStat: validated=256 rejected=0', 'FixSvalStat: validated=512 rejected=0']
d = make('r1_pos', 'r1', r1_head + stat + scene(), run=ES_OK, idx=3000)
res, rm = rowmap(d, 'r1')
for k in ('binary sha256', 'cold form', 'FixSval mode=1', 'R1: 0 lines SPIR-V', 'R1: no process end', 'R1: 0 death', 'R1: validated',
          'R1: entered', 'R1: hold', 'R1: video index', 'R1: 0 one-frame', 'R1: sheet', 'manifest of the caches', 'no window'):
    check('r1 pos %s YES' % k, row(rm, k) == 'YES')
check('r1 pos last stat used', res['st_last'][1] == 512 and res['st_lines'] == 2)
check('r1 has no R0 / W rows', not any(k.startswith('R0:') or k.startswith('W:') for k in rm))
# validated edges (RC3)
for v, want in ((151, 'YES'), (150, 'NO'), (256, 'YES')):
    d = make('r1_val_%d' % v, 'r1', r1_head + ['FixSvalStat: validated=%d rejected=0' % v] + scene(), run=ES_OK, idx=3000)
    check('r1 validated %d -> %s' % (v, want), row(rowmap(d, 'r1')[1], 'R1: validated') == want)
d = make('r1_val_last', 'r1', r1_head + ['FixSvalStat: validated=512 rejected=0', 'FixSvalStat: validated=150 rejected=0'] + scene(),
         run=ES_OK, idx=3000)
check('r1 validated: the LAST line decides', row(rowmap(d, 'r1')[1], 'R1: validated') == 'NO')
d = make('r1_nostat', 'r1', r1_head + scene(), run=ES_OK, idx=3000)
check('r1 no FixSvalStat line -> NOT_DETERMINED (RC3 (b))', row(rowmap(d, 'r1')[1], 'R1: validated') == 'NOT_DETERMINED')
# FixSval members
d = make('r1_mode0', 'r1', [STC, FS0, PRE_COLD, 'GuestOut: boot'] + stat + scene(), run=ES_OK, idx=3000)
check('r1 mode=0: FixSval NO', row(rowmap(d, 'r1')[1], 'FixSval mode=1') == 'NO')
d = make('r1_ubo0', 'r1', [STC, 'FixSval: mode=1 ubo_std_layout=0', PRE_COLD, 'GuestOut: boot'] + stat + scene(), run=ES_OK, idx=3000)
check('r1 ubo=0: FixSval NO', row(rowmap(d, 'r1')[1], 'FixSval mode=1') == 'NO')
d = make('r1_late', 'r1', [STC, PRE_COLD, 'GuestOut: boot', FS1] + stat + scene(), run=ES_OK, idx=3000)
check('r1 FixSval after the first GuestOut: NO', row(rowmap(d, 'r1')[1], 'FixSval mode=1') == 'NO')
d = make('r1_nofs', 'r1', [STC, PRE_COLD, 'GuestOut: boot'] + stat + scene(), run=ES_OK, idx=3000)
check('r1 no FixSval: NO', row(rowmap(d, 'r1')[1], 'FixSval mode=1') == 'NO')
d = make('r1_noguest', 'r1', [STC, FS1, PRE_COLD] + stat, run=ES_OK, idx=3000)
check('r1 FixSval with no GuestOut at all: YES', row(rowmap(d, 'r1')[1], 'FixSval mode=1') == 'YES')
# failure / end / death
d = make('r1_fail', 'r1', r1_head + stat + scene() + [FAIL1], run=ES_OK, idx=3000)
check('r1 one failure line: NO', row(rowmap(d, 'r1')[1], 'R1: 0 lines SPIR-V') == 'NO')
d = make('r1_fail_stdout', 'r1', r1_head + stat + scene(), stdout=FAIL2 + '\n', run=ES_OK, idx=3000)
check('r1 failure in stdout: NO', row(rowmap(d, 'r1')[1], 'R1: 0 lines SPIR-V') == 'NO')
d = make('r1_exit', 'r1', r1_head + stat, run=ES_EXIT, idx=10)
check('r1 exited: no-end NO', row(rowmap(d, 'r1')[1], 'R1: no process end') == 'NO')
d = make('r1_hold_exit', 'r1', r1_head + stat + scene(), run=ES_HOLD_EXIT, idx=3000)
check('r1 hold_exit: no-end NO', row(rowmap(d, 'r1')[1], 'R1: no process end') == 'NO')
d = make('r1_norun', 'r1', r1_head + stat + scene(), run=None, idx=3000)
check('r1 no es.json: no-end NO (not proven)', row(rowmap(d, 'r1')[1], 'R1: no process end') == 'NO')
d = make('r1_death', 'r1', r1_head + stat + scene() + ['GpuHangAbort: x'], run=ES_OK, idx=3000)
check('r1 death in log: NO', row(rowmap(d, 'r1')[1], 'R1: 0 death') == 'NO')
d = make('r1_death_so', 'r1', r1_head + stat + scene(), stdout='Unhandled exception: x\n', run=ES_OK, idx=3000)
check('r1 death in stdout: NO', row(rowmap(d, 'r1')[1], 'R1: 0 death') == 'NO')
# hold edges
d = make('r1_hold_edge', 'r1', r1_head + stat + scene(300000000 - 1), run=ES_OK, idx=3000)
check('r1 hold 300 s - 1 us: NO', row(rowmap(d, 'r1')[1], 'R1: hold') == 'NO')
d = make('r1_change', 'r1', r1_head + stat + scene(200000000) + ['GuestOut: Level has started: other', ft(99, 200000000, 400)],
         run=ES_OK, idx=3000)
check('r1 rows after a scene change not counted: NO', row(rowmap(d, 'r1')[1], 'R1: hold') == 'NO')
d = make('r1_noentry', 'r1', r1_head + stat + [ft(1, 400000000, 400)], run=ES_OK, idx=3000)
r_, m_ = rowmap(d, 'r1')
check('r1 no entry: entered NO, hold NO', row(m_, 'R1: entered') == 'NO' and row(m_, 'R1: hold') == 'NO')
# video edges
d = make('r1_v2999', 'r1', r1_head + stat + scene(), run=ES_OK, idx=2999)
check('r1 video 2999: NO', row(rowmap(d, 'r1')[1], 'R1: video index') == 'NO')
d = make('r1_noidx', 'r1', r1_head + stat + scene(), run=ES_OK, idx=None)
check('r1 no index: NO', row(rowmap(d, 'r1')[1], 'R1: video index') == 'NO')
d = make('r1_gl1', 'r1', r1_head + stat + scene(), run=ES_OK, idx=3000, glitch='x: 3000 frames\none-frame glitches: 1')
check('r1 1 glitch: NO', row(rowmap(d, 'r1')[1], 'R1: 0 one-frame') == 'NO')
d = make('r1_nogl', 'r1', r1_head + stat + scene(), run=ES_OK, idx=3000, glitch=None)
check('r1 no glitch file: NOT_READ', row(rowmap(d, 'r1')[1], 'R1: 0 one-frame') == 'NOT_READ')
d = make('r1_nosheet', 'r1', r1_head + stat + scene(), run=ES_OK, idx=3000, sheet='ffmpeg failed')
check('r1 no sheet line: NO', row(rowmap(d, 'r1')[1], 'R1: sheet') == 'NO')
# window events
d = make('r1_min', 'r1', r1_head + stat + scene() + ['Window 1 minimized'], run=ES_OK, idx=3000)
check('r1 minimized: window NO', row(rowmap(d, 'r1')[1], 'no window') == 'NO')
d = make('r1_rec', 'r1', r1_head + stat + scene() + ['Recovering Vulkan swapchain'], run=ES_OK, idx=3000)
check('r1 recovering: window NO', row(rowmap(d, 'r1')[1], 'no window') == 'NO')
d = make('r1_focus', 'r1', r1_head + stat + scene() + ['Window 1 lost keyboard focus'], run=ES_OK, idx=3000)
check('r1 focus only: window YES', row(rowmap(d, 'r1')[1], 'no window') == 'YES')

# ---- W
w_head = [STC, FS1, PRE_COLD, DUAL, 'GuestOut: boot', '[Vulkan][W][2] x', '[Vulkan][W] y']
d = make('w_pos', 'w', w_head + stat + scene(310000000), run=ES_OK, idx=None, glitch=None, sheet=None)
res, rm = rowmap(d, 'w')
for k in ('binary sha256', 'cold form', 'FixSval mode=1', 'W: entered', 'W: hold', 'W: 0 [Vulkan][E]', 'W: positive control',
          'W: DualSrcBlend', 'W: 0 lines SPIR-V', 'W: no process end', 'W: 0 death', 'manifest of the caches', 'no window'):
    check('w pos %s YES' % k, row(rm, k) == 'YES')
check('w vkw count 2', res['vkw'] == 2)
check('w has no R0 / R1 rows', not any(k.startswith('R0:') or k.startswith('R1:') for k in rm))
d = make('w_vke', 'w', w_head + ['[Vulkan][E] VUID'] + scene(), run=ES_OK)
check('w one [Vulkan][E]: NO', row(rowmap(d, 'w')[1], 'W: 0 [Vulkan][E]') == 'NO')
d = make('w_novkw', 'w', [STC, FS1, PRE_COLD, DUAL, 'GuestOut: boot', '[Vulkan][I] z'] + scene(), run=ES_OK)
check('w no [Vulkan][W]: positive control NO', row(rowmap(d, 'w')[1], 'W: positive control') == 'NO')
d = make('w_dual_late', 'w', [STC, FS1, PRE_COLD, 'GuestOut: boot', DUAL, '[Vulkan][W] y'] + scene(), run=ES_OK)
check('w DualSrcBlend after GuestOut: NO', row(rowmap(d, 'w')[1], 'W: DualSrcBlend') == 'NO')
d = make('w_dual0', 'w', [STC, FS1, PRE_COLD, 'DualSrcBlend: supported=1 enabled=0', 'GuestOut: boot', '[Vulkan][W] y'] + scene(), run=ES_OK)
check('w DualSrcBlend enabled=0: NO', row(rowmap(d, 'w')[1], 'W: DualSrcBlend') == 'NO')
d = make('w_short', 'w', w_head + scene(299000000), run=ES_OK)
check('w hold 299 s: NO', row(rowmap(d, 'w')[1], 'W: hold') == 'NO')

# ---- output: ASCII and strict cp1250 without PYTHONIOENCODING (non-ASCII bytes in the log)
d = make('enc', 'r1', ['Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b\\\u043a\u044d\u0448', FS1, PRE_COLD,
                       'Release, x, ver = 1, git = \u0432\u0435\u0440\u0441\u0438\u044f, date = y', 'GuestOut: boot'] + stat + scene(),
         run=ES_OK, idx=3000)
env = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
env['PYTHONIOENCODING'] = 'cp1250:strict'
p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'r1'], capture_output=True, env=env)
check('cp1250 strict: rc 0', p.returncode == 0)
check('cp1250 strict: stdout ASCII only', all(b < 128 for b in p.stdout))
check('cp1250 strict: rows printed', b'ROW R1: validated' in p.stdout)
env2 = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
p2 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'r1'], capture_output=True, env=env2)
check('no PYTHONIOENCODING: rc 0, ASCII', p2.returncode == 0 and all(b < 128 for b in p2.stdout))
# json output
jp = os.path.join(TMP, 'out.json')
p3 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'r1', '--json', jp], capture_output=True, env=env2)
check('json written', p3.returncode == 0 and json.load(open(jp))['kind'] == 'r1')

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d' % N)
print('ALL OK' if OK else 'SOME FAILED')
sys.exit(0 if OK else 1)
