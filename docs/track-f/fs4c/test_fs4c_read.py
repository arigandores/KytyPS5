"""FS4c (HPP-472): fixtures of fs4c_read.py - every row of the seal section 4 and every edge (port of F10e test_f10e_read.py): 151 / 150 /
no FixSvalStat line, hold 300 s / 300 s - 1 us, 3000 / 2999 video records, FixSval before / after the first GuestOut and its mode per
kind, the cold form members (r0, r1, hb) and the warm form members (w, v), frames >= 1 s (gate of v), manifest EQUAL / DIFFER / missing,
process end per kind, the revision text (YES / NO / NOT_PRESENT, never a gate), output in strict cp1250 without PYTHONIOENCODING.
The first output line names the suite and the target with their sha256; the last line is ALL OK.  ASCII only."""
import hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'fs4c_read.py')
sys.path.insert(0, HERE)
import fs4c_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_fs4c_read.py sha256 %s target fs4c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(TARGET)))
OK = True
N = 0
TMP = tempfile.mkdtemp(prefix='fs4c_fx_')
GOOD_SHA = R.BIN_EXPECT
STC = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b'
PRE_COLD = 'PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b\\pipelines.bin yet'
PRE_WARM = 'PipelinePrecache: 1357 recipes -> 1234 graphics + 123 compute pipelines queued, 0 skipped, 2551 sources loaded'
FS1 = 'FixSval: mode=1 ubo_std_layout=1'
FS0 = 'FixSval: mode=0 ubo_std_layout=1'
ENTRY = 'GuestOut: Level has started: underwater_aerial_garden'
ENTRY_HB = 'GuestOut: Level has started: hoover_beach'
FAIL1 = '[ps] SPIR-V validation failed hash=0x00000000deadbeef:'
FAIL2 = 'ps failed hash=0x00000000deadbeef: SPIR-V validation failed'
DUAL = 'DualSrcBlend: supported=1 enabled=1'
COLD = 'cold form: C:/x/variant_fixb26_fixb1b absent at 2026-10-03T00:00:00Z'
WARM = 'warm form: C:/x/variant_fixb26_fixb1b present at 2026-10-03T00:00:00Z'
FORK = 'Fork build arigandores/KytyPS5 3d0e46d'
GITL = 'Release, clang, ver = 0.1, git = KytyPS5-2026-09-15-6a2987a-1874-g3d0e46da, date = x'


def ft(n, dt, draws):
    return 'FrameTrace: n=%d dt_us=%d draws=%d' % (n, dt, draws)


def scene(hold_us=300000000, entry=ENTRY, step=100000):
    """entry, the first scene frame (not counted), then rows of step us (last one shorter) that sum to hold_us."""
    out = [entry, ft(1, 16667, 50), ft(2, 16667, 400)]
    rest, n = hold_us, 3
    big = max(step, 1)
    while rest > 0:
        d = min(rest, big)
        out.append(ft(n, d, 400))
        rest -= d
        n += 1
    return out


def make(name, kind, log, stdout='', run=None, idx=None, glitch='one-frame glitches: 0', sheet='sheet: x.png frames 3000 step 1 tiles 8x6',
         sha_t=GOOD_SHA, cold=COLD, mcmp='manifest cmp EQUAL files 3 listsha ab'):
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


R0_OK_RUN = {'how': 'exit rc 321', 'rc': 321, 'exit_s': 13.3, 'wall_s': 15.0}
R0_TO_RUN = {'how': 'timeout, WM_CLOSE rc 0', 'rc': 0, 'exit_s': None, 'wall_s': 300.4}
ES_OK = {'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': None, 'hold_s': 330.1, 'stable_s': 40.0}]}
ES_EXIT = {'attempts': [{'outcome': 'exited', 'detail': 'exit code 321', 'hold_exit': None, 'hold_s': None, 'stable_s': None}]}
ES_HOLD_EXIT = {'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': 321, 'hold_s': 50.0, 'stable_s': 40.0}]}

# ---- kind_of
for k in ('r0', 'r1', 'hb', 'w', 'v'):
    check('kind %s' % k, R.kind_of('fs4_' + k) == k)
check('kind of the repeat fs4_r0r is r0', R.kind_of('fs4_r0r') == 'r0')
for bad in ('f10e_r1', 'fs4_r1x', 'fs3_v', 'fs4_r1r'):
    try:
        R.kind_of(bad)
        check('kind %s raises' % bad, False)
    except SystemExit:
        check('kind %s raises' % bad, True)
check('levels', R.LEVEL['hb'] == 'hoover_beach' and all(R.LEVEL[k] == 'underwater_aerial_garden' for k in ('r0', 'r1', 'w', 'v')))

# ---- R0 positive (the defect reproduced at =0 on the cold variant dir)
r0_log = [GITL, STC, FS0, PRE_COLD, 'GuestOut: x', FAIL1, 'body', FAIL2, '--- Error ---', FORK + ' EXIT text']
d = make('r0_pos', 'r0', r0_log, run=R0_OK_RUN)
res, rm = rowmap(d, 'r0')
check('r0 binary YES', row(rm, 'binary sha256') == 'YES')
check('r0 revision YES (both texts name 3d0e46d)', row(rm, 'revision text') == 'YES' and len(res['rev']) == 2)
check('r0 cold YES', row(rm, 'cold form') == 'YES')
check('r0 has no warm row', not any(k.startswith('warm form') for k in rm))
check('r0 FixSval mode=0 YES', row(rm, 'FixSval mode=0') == 'YES')
check('r0 fail YES', row(rm, 'R0: >= 1 line') == 'YES')
check('r0 fail count 2, 1 hash', res['fail_log'] == 2 and res['fail_hashes'] == ['00000000deadbeef'])
check('r0 ended YES', row(rm, 'R0: the process ended') == 'YES')
check('r0 nostat YES', row(rm, 'R0: 0 FixSvalStat') == 'YES')
check('r0 reproduced YES', row(rm, 'R0: defect reproduced') == 'YES')
check('r0 manifest YES', row(rm, 'manifest of the caches') == 'YES')
check('r0 has no R1 / HB / W / V rows', not any(k[:3] in ('R1:', 'HB ', 'W: ', 'V: ') for k in rm))
# revision text of another revision: row NO, binary row still YES (sha decides)
d = make('r0_rev_other', 'r0', [x.replace('3d0e46d', '92d1134') for x in r0_log], run=R0_OK_RUN)
res, rm = rowmap(d, 'r0')
check('r0 revision other: NO, binary YES', row(rm, 'revision text') == 'NO' and row(rm, 'binary sha256') == 'YES')
d = make('r0_rev_mixed', 'r0', r0_log + ['Fork build arigandores/KytyPS5 68602c4'], run=R0_OK_RUN)
check('r0 revision mixed: NO', row(rowmap(d, 'r0')[1], 'revision text') == 'NO')
d = make('r0_norev', 'r0', r0_log[1:-1], run=R0_OK_RUN)
res, rm = rowmap(d, 'r0')
check('r0 no revision text: NOT_PRESENT, binary YES', row(rm, 'revision text') == 'NOT_PRESENT' and row(rm, 'binary sha256') == 'YES')
d = make('r0_rev_stdout', 'r0', r0_log[1:-1], stdout=FORK + '\n', run=R0_OK_RUN)
res, rm = rowmap(d, 'r0')
check('r0 revision in stdout only: YES', row(rm, 'revision text') == 'YES' and res['rev'][0][0] == 'stdout')
# not reproduced: no failure, timeout
d = make('r0_norep', 'r0', [STC, FS0, PRE_COLD, 'GuestOut: x'] + scene(), run=R0_TO_RUN)
res, rm = rowmap(d, 'r0')
check('r0 norep fail NO', row(rm, 'R0: >= 1 line') == 'NO')
check('r0 norep ended NO', row(rm, 'R0: the process ended') == 'NO')
check('r0 norep reproduced NO', row(rm, 'R0: defect reproduced') == 'NO')
d = make('r0_stdout', 'r0', [STC, FS0, PRE_COLD], stdout=FAIL2 + '\n', run=R0_OK_RUN)
res, rm = rowmap(d, 'r0')
check('r0 stdout fail counts, hash from stdout', res['fail_stdout'] == 1 and row(rm, 'R0: defect reproduced') == 'YES'
      and res['fail_hashes'] == ['00000000deadbeef'])
d = make('r0_noexit', 'r0', [STC, FS0, PRE_COLD, FAIL1], run=R0_TO_RUN)
check('r0 fail without exit: reproduced NO', row(rowmap(d, 'r0')[1], 'R0: defect reproduced') == 'NO')
d = make('r0_nofail', 'r0', [STC, FS0, PRE_COLD], run=R0_OK_RUN)
check('r0 exit without fail: reproduced NO', row(rowmap(d, 'r0')[1], 'R0: defect reproduced') == 'NO')
d = make('r0_norun', 'r0', r0_log, run=None)
res, rm = rowmap(d, 'r0')
check('r0 no run.json: ended NOT_READ', row(rm, 'R0: the process ended') == 'NOT_READ' and row(rm, 'R0: defect reproduced') == 'NO')
d = make('r0_stat', 'r0', r0_log + ['FixSvalStat: validated=256 rejected=0'], run=R0_OK_RUN)
check('r0 stat line: reference NO', row(rowmap(d, 'r0')[1], 'R0: 0 FixSvalStat') == 'NO')
d = make('r0_mode1', 'r0', [STC, FS1, PRE_COLD, FAIL1], run=R0_OK_RUN)
check('r0 mode=1 (the default leaked): FixSval row NO', row(rowmap(d, 'r0')[1], 'FixSval mode=0') == 'NO')
# r0 on a warm variant dir (Z2: the rollback rejects only on a new translation) - the cold row is NO
d = make('r0_warm', 'r0', [STC, FS0, PRE_WARM, 'GuestOut: x'] + scene(), run=R0_TO_RUN, cold=WARM)
res, rm = rowmap(d, 'r0')
check('r0 warm (Z2): cold NO, reproduced NO', row(rm, 'cold form') == 'NO' and row(rm, 'R0: defect reproduced') == 'NO')

# ---- binary / cold / manifest members
d = make('bad_sha', 'r0', r0_log, run=R0_OK_RUN, sha_t='540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1')
check('installed 540c035a: binary NO', row(rowmap(d, 'r0')[1], 'binary sha256') == 'NO')
d = make('no_sha', 'r0', r0_log, run=R0_OK_RUN, sha_t=None)
check('no sha file: binary NO', row(rowmap(d, 'r0')[1], 'binary sha256') == 'NO')
d = make('warm_pre', 'r0', [STC, FS0, PRE_WARM, FAIL1], run=R0_OK_RUN)
check('cold.txt absent but warm precache: cold NO', row(rowmap(d, 'r0')[1], 'cold form') == 'NO')
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

# ---- R1 positive (default mode=1, no KYTY_FIX_SVAL)
r1_head = [STC, FS1, PRE_COLD, 'GuestOut: boot']
stat = ['FixSvalStat: validated=256 rejected=0', 'FixSvalStat: validated=512 rejected=0']
d = make('r1_pos', 'r1', r1_head + stat + scene(), run=ES_OK, idx=3000)
res, rm = rowmap(d, 'r1')
for k in ('binary sha256', 'cold form', 'FixSval mode=1', 'R1: 0 lines SPIR-V', 'R1: no process end', 'R1: 0 death', 'R1: validated',
          'R1: entered', 'R1: hold', 'R1: video index', 'R1: 0 one-frame', 'R1: sheet', 'manifest of the caches', 'no window'):
    check('r1 pos %s YES' % k, row(rm, k) == 'YES')
check('r1 pos revision NOT_PRESENT (reference)', row(rm, 'revision text') == 'NOT_PRESENT')
check('r1 pos last stat used', res['st_last'][1] == 512 and res['st_lines'] == 2)
check('r1 has no R0 / HB / W / V rows', not any(k[:3] in ('R0:', 'HB ', 'W: ', 'V: ') for k in rm))
for v, want in ((151, 'YES'), (150, 'NO'), (256, 'YES')):
    d = make('r1_val_%d' % v, 'r1', r1_head + ['FixSvalStat: validated=%d rejected=0' % v] + scene(), run=ES_OK, idx=3000)
    check('r1 validated %d -> %s' % (v, want), row(rowmap(d, 'r1')[1], 'R1: validated') == want)
d = make('r1_val_last', 'r1', r1_head + ['FixSvalStat: validated=512 rejected=0', 'FixSvalStat: validated=150 rejected=0'] + scene(),
         run=ES_OK, idx=3000)
check('r1 validated: the LAST line decides', row(rowmap(d, 'r1')[1], 'R1: validated') == 'NO')
d = make('r1_nostat', 'r1', r1_head + scene(), run=ES_OK, idx=3000)
check('r1 no FixSvalStat line -> NOT_DETERMINED', row(rowmap(d, 'r1')[1], 'R1: validated') == 'NOT_DETERMINED')
d = make('r1_mode0', 'r1', [STC, FS0, PRE_COLD, 'GuestOut: boot'] + stat + scene(), run=ES_OK, idx=3000)
check('r1 mode=0 (default not ON): FixSval NO', row(rowmap(d, 'r1')[1], 'FixSval mode=1') == 'NO')
d = make('r1_ubo0', 'r1', [STC, 'FixSval: mode=1 ubo_std_layout=0', PRE_COLD, 'GuestOut: boot'] + stat + scene(), run=ES_OK, idx=3000)
check('r1 ubo=0: FixSval NO', row(rowmap(d, 'r1')[1], 'FixSval mode=1') == 'NO')
d = make('r1_late', 'r1', [STC, PRE_COLD, 'GuestOut: boot', FS1] + stat + scene(), run=ES_OK, idx=3000)
check('r1 FixSval after the first GuestOut: NO', row(rowmap(d, 'r1')[1], 'FixSval mode=1') == 'NO')
d = make('r1_nofs', 'r1', [STC, PRE_COLD, 'GuestOut: boot'] + stat + scene(), run=ES_OK, idx=3000)
check('r1 no FixSval: NO', row(rowmap(d, 'r1')[1], 'FixSval mode=1') == 'NO')
d = make('r1_noguest', 'r1', [STC, FS1, PRE_COLD] + stat, run=ES_OK, idx=3000)
check('r1 FixSval with no GuestOut at all: YES', row(rowmap(d, 'r1')[1], 'FixSval mode=1') == 'YES')
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
d = make('r1_hold_edge', 'r1', r1_head + stat + scene(300000000 - 1), run=ES_OK, idx=3000)
check('r1 hold 300 s - 1 us: NO', row(rowmap(d, 'r1')[1], 'R1: hold') == 'NO')
d = make('r1_change', 'r1', r1_head + stat + scene(200000000) + ['GuestOut: Level has started: other', ft(99, 200000000, 400)],
         run=ES_OK, idx=3000)
check('r1 rows after a scene change not counted: NO', row(rowmap(d, 'r1')[1], 'R1: hold') == 'NO')
d = make('r1_noentry', 'r1', r1_head + stat + [ft(1, 400000000, 400)], run=ES_OK, idx=3000)
r_, m_ = rowmap(d, 'r1')
check('r1 no entry: entered NO, hold NO', row(m_, 'R1: entered') == 'NO' and row(m_, 'R1: hold') == 'NO')
d = make('r1_hb_entry', 'r1', r1_head + stat + scene(entry=ENTRY_HB), run=ES_OK, idx=3000)
check('r1 entry of hoover_beach is not the r1 entry: NO', row(rowmap(d, 'r1')[1], 'R1: entered') == 'NO')
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
d = make('r1_min', 'r1', r1_head + stat + scene() + ['Window 1 minimized'], run=ES_OK, idx=3000)
check('r1 minimized: window NO', row(rowmap(d, 'r1')[1], 'no window') == 'NO')
d = make('r1_rec', 'r1', r1_head + stat + scene() + ['Recovering Vulkan swapchain'], run=ES_OK, idx=3000)
check('r1 recovering: window NO', row(rowmap(d, 'r1')[1], 'no window') == 'NO')
d = make('r1_focus', 'r1', r1_head + stat + scene() + ['Window 1 lost keyboard focus'], run=ES_OK, idx=3000)
check('r1 focus only: window YES', row(rowmap(d, 'r1')[1], 'no window') == 'YES')
d = make('r1_warm', 'r1', [STC, FS1, PRE_WARM, 'GuestOut: boot'] + stat + scene(), run=ES_OK, idx=3000, cold=WARM)
check('r1 on a warm dir: cold NO', row(rowmap(d, 'r1')[1], 'cold form') == 'NO')

# ---- HB (reference): hoover_beach of the R1 form
hb_head = [STC, FS1, PRE_COLD, 'GuestOut: boot']
d = make('hb_pos', 'hb', hb_head + stat + scene(entry=ENTRY_HB), run=ES_OK, idx=3000)
res, rm = rowmap(d, 'hb')
for k in ('binary sha256', 'cold form', 'FixSval mode=1', 'HB (reference): 0 lines', 'HB (reference): no process', 'HB (reference): 0 death',
          'HB (reference): validated', 'HB (reference): entered', 'HB (reference): hold', 'HB (reference): video index',
          'HB (reference): 0 one-frame', 'HB (reference): sheet', 'manifest of the caches', 'no window'):
    check('hb pos %s YES' % k, row(rm, k) == 'YES')
check('hb has no R0 / R1 / W / V rows', not any(k[:3] in ('R0:', 'R1:', 'W: ', 'V: ') for k in rm))
d = make('hb_sky', 'hb', hb_head + stat + scene(), run=ES_OK, idx=3000)
check('hb entry of Sky Garden is not the hb entry: NO', row(rowmap(d, 'hb')[1], 'HB (reference): entered') == 'NO')
FAIL_OTHER = '[cs] SPIR-V validation failed hash=0x0000000012345678:'
d = make('hb_fail', 'hb', hb_head + stat + [FAIL1, FAIL_OTHER] + scene(entry=ENTRY_HB), run=ES_OK, idx=3000)
res, rm = rowmap(d, 'hb')
check('hb two failures: row NO, 2 hashes', row(rm, 'HB (reference): 0 lines') == 'NO' and res['fail_hashes'] == ['00000000deadbeef', '0000000012345678'])
d = make('hb_nostat', 'hb', hb_head + scene(entry=ENTRY_HB), run=ES_OK, idx=3000)
check('hb no stat line: NOT_DETERMINED', row(rowmap(d, 'hb')[1], 'HB (reference): validated') == 'NOT_DETERMINED')

# ---- W (harness --shader-validation false, warm, FixSval mode=1, no FixSvalStat)
w_head = [STC, FS1, PRE_WARM, DUAL, 'GuestOut: boot', '[Vulkan][W][2] x', '[Vulkan][W] y']
d = make('w_pos', 'w', w_head + scene(310000000), run=ES_OK, idx=None, glitch=None, sheet=None, cold=WARM)
res, rm = rowmap(d, 'w')
for k in ('binary sha256', 'warm form', 'FixSval mode=1', 'W: entered', 'W: hold', 'W: 0 [Vulkan][E]', 'W: positive control',
          'W: DualSrcBlend', 'W: 0 lines SPIR-V', 'W: no process end', 'W: 0 death', 'manifest of the caches', 'no window'):
    check('w pos %s YES' % k, row(rm, k) == 'YES')
check('w vkw count 2', res['vkw'] == 2)
check('w has no cold row', not any(k.startswith('cold form') for k in rm))
check('w has no R0 / R1 / HB / V rows', not any(k[:3] in ('R0:', 'R1:', 'HB ', 'V: ') for k in rm))
d = make('w_vke', 'w', w_head + ['[Vulkan][E] VUID'] + scene(), run=ES_OK, cold=WARM)
check('w one [Vulkan][E]: NO', row(rowmap(d, 'w')[1], 'W: 0 [Vulkan][E]') == 'NO')
d = make('w_novkw', 'w', [STC, FS1, PRE_WARM, DUAL, 'GuestOut: boot', '[Vulkan][I] z'] + scene(), run=ES_OK, cold=WARM)
check('w no [Vulkan][W]: positive control NO', row(rowmap(d, 'w')[1], 'W: positive control') == 'NO')
d = make('w_dual_late', 'w', [STC, FS1, PRE_WARM, 'GuestOut: boot', DUAL, '[Vulkan][W] y'] + scene(), run=ES_OK, cold=WARM)
check('w DualSrcBlend after GuestOut: NO', row(rowmap(d, 'w')[1], 'W: DualSrcBlend') == 'NO')
d = make('w_dual0', 'w', [STC, FS1, PRE_WARM, 'DualSrcBlend: supported=1 enabled=0', 'GuestOut: boot', '[Vulkan][W] y'] + scene(),
         run=ES_OK, cold=WARM)
check('w DualSrcBlend enabled=0: NO', row(rowmap(d, 'w')[1], 'W: DualSrcBlend') == 'NO')
d = make('w_short', 'w', w_head + scene(299000000), run=ES_OK, cold=WARM)
check('w hold 299 s: NO', row(rowmap(d, 'w')[1], 'W: hold') == 'NO')
d = make('w_mode0', 'w', [STC, FS0, PRE_WARM, DUAL, 'GuestOut: boot', '[Vulkan][W] y'] + scene(), run=ES_OK, cold=WARM)
check('w mode=0: FixSval NO', row(rowmap(d, 'w')[1], 'FixSval mode=1') == 'NO')
d = make('w_cold', 'w', [STC, FS1, PRE_COLD, DUAL, 'GuestOut: boot', '[Vulkan][W] y'] + scene(), run=ES_OK, cold=WARM)
check('w first precache line no ... yet: warm NO', row(rowmap(d, 'w')[1], 'warm form') == 'NO')
d = make('w_coldtxt', 'w', w_head + scene(), run=ES_OK, cold=COLD)
check('w cold.txt of the cold form: warm NO', row(rowmap(d, 'w')[1], 'warm form') == 'NO')
d = make('w_nocoldtxt', 'w', w_head + scene(), run=ES_OK, cold=None)
check('w no cold.txt: warm NO', row(rowmap(d, 'w')[1], 'warm form') == 'NO')
d = make('w_noprecache', 'w', [STC, FS1, DUAL, 'GuestOut: boot', '[Vulkan][W] y'] + scene(), run=ES_OK, cold=WARM)
check('w no precache line: warm NO', row(rowmap(d, 'w')[1], 'warm form') == 'NO')

# ---- V (SCENE_OK form, warm)
v_head = [STC, FS1, PRE_WARM, DUAL, 'GuestOut: boot']
d = make('v_pos', 'v', v_head + scene(330000000), run=ES_OK, idx=3000, cold=WARM)
res, rm = rowmap(d, 'v')
for k in ('binary sha256', 'warm form', 'FixSval mode=1', 'V: entered', 'V: hold', 'V: 0 death', 'V: 0 frames >= 1 s', 'V: no process end',
          'V: video index', 'V: 0 one-frame', 'V: sheet', 'manifest of the caches', 'no window'):
    check('v pos %s YES' % k, row(rm, k) == 'YES')
check('v has no R0 / R1 / HB / W rows', not any(k[:3] in ('R0:', 'R1:', 'HB ', 'W: ') for k in rm))
d = make('v_k2', 'v', v_head + scene(330000000) + [ft(9999, 1000000, 400)], run=ES_OK, idx=3000, cold=WARM)
check('v one frame of exactly 1 s after the first scene frame: NO', row(rowmap(d, 'v')[1], 'V: 0 frames >= 1 s') == 'NO')
d = make('v_k2_under', 'v', v_head + scene(330000000) + [ft(9999, 999999, 400)], run=ES_OK, idx=3000, cold=WARM)
check('v frame of 999 999 us: YES', row(rowmap(d, 'v')[1], 'V: 0 frames >= 1 s') == 'YES')
d = make('v_k2_before', 'v', v_head + [ENTRY, ft(1, 2000000, 50), ft(2, 16667, 400)] + scene(330000000)[3:], run=ES_OK, idx=3000, cold=WARM)
check('v long frame before the first scene frame not counted: YES', row(rowmap(d, 'v')[1], 'V: 0 frames >= 1 s') == 'YES')
d = make('v_k2_after_change', 'v', v_head + scene(330000000) + ['GuestOut: Level has started: other', ft(9999, 5000000, 400)], run=ES_OK,
         idx=3000, cold=WARM)
check('v long frame after a scene change not counted: YES', row(rowmap(d, 'v')[1], 'V: 0 frames >= 1 s') == 'YES')
d = make('v_noentry', 'v', v_head + [ft(1, 400000000, 400)], run=ES_OK, idx=3000, cold=WARM)
r_, m_ = rowmap(d, 'v')
check('v no entry: entered NO, frames row NO', row(m_, 'V: entered') == 'NO' and row(m_, 'V: 0 frames >= 1 s') == 'NO')
d = make('v_death', 'v', v_head + scene(330000000) + ['ErrorDeviceLost'], run=ES_OK, idx=3000, cold=WARM)
check('v death: NO', row(rowmap(d, 'v')[1], 'V: 0 death') == 'NO')
d = make('v_exit', 'v', v_head + scene(330000000), run=ES_HOLD_EXIT, idx=3000, cold=WARM)
check('v hold_exit: no-end NO', row(rowmap(d, 'v')[1], 'V: no process end') == 'NO')
d = make('v_2999', 'v', v_head + scene(330000000), run=ES_OK, idx=2999, cold=WARM)
check('v video 2999: NO', row(rowmap(d, 'v')[1], 'V: video index') == 'NO')
d = make('v_gl', 'v', v_head + scene(330000000), run=ES_OK, idx=3000, cold=WARM, glitch='one-frame glitches: 2')
check('v 2 glitches: NO', row(rowmap(d, 'v')[1], 'V: 0 one-frame') == 'NO')
d = make('v_short', 'v', v_head + scene(300000000 - 1), run=ES_OK, idx=3000, cold=WARM)
check('v hold 300 s - 1 us: NO', row(rowmap(d, 'v')[1], 'V: hold') == 'NO')

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
jp = os.path.join(TMP, 'out.json')
p3 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'r1', '--json', jp], capture_output=True, env=env2)
check('json written', p3.returncode == 0 and json.load(open(jp))['kind'] == 'r1')
p4 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'x'], capture_output=True, env=env2)
check('unknown kind refused', p4.returncode != 0)

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d' % N)
print('ALL OK' if OK else 'SOME FAILED')
sys.exit(0 if OK else 1)
