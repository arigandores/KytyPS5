"""Track F link FS5c (HPP-511): fixtures of fs5c_read.py - every row of the seal section 4 and every edge (port of F12f
test_f12f_read.py with the R1 rows of FS4c test_fs4c_read.py): the binary (631ff987) and the installed 31cbfee8 before / after, the
directory row (_fixf10 in every line; mixed lines; no line; slashes; a suffix), the cold form (cold.txt and the first PipelinePrecache
line), hold 300 s / 300 s - 1 us, 3000 / 2999 video records, glitches, sheet, frames >= 1 s (report row only), process end, death
markers, FixSval (mode 0, ubo 0, after the first GuestOut, missing), SPIR-V validation failed in the log / stdout, FixSvalStat (reference),
W rows ([Vulkan][E], [Vulkan][W] = 0 / 1, DualSrcBlend before / after the first GuestOut), manifest EQUAL / DIFFER / missing for both
compares, interference (minimized, Recovering Vulkan swapchain, GamePatch), the hb reference header, revision text (never a gate),
output in strict cp1250 without PYTHONIOENCODING.  The first output line names the suite and the target with their sha256; the last line
is ALL OK.  ASCII only."""
import hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'fs5c_read.py')
sys.path.insert(0, HERE)
import fs5c_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_fs5c_read.py sha256 %s target fs5c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(TARGET)))
OK = True
N = 0
NF = 0
TMP = tempfile.mkdtemp(prefix='fs5c_fx_')
FIXSHA = R.BIN_EXPECT
INSHA = R.WANT
STC_FIX = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10'
STC_BASE = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b'
PC_COLD = 'PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10\\pipelines.bin yet'
PC_BASE = 'PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b\\pipelines.bin yet'
PC_WARM = 'PipelinePrecache: replayed 385 recipes'
FSV = 'FixSval: mode=1 ubo_std_layout=1'
ENTRY = {'v': 'GuestOut: Level has started: underwater_aerial_garden', 'w': 'GuestOut: Level has started: underwater_aerial_garden',
         'r1': 'GuestOut: Level has started: underwater_aerial_garden', 'hb': 'GuestOut: Level has started: hoover_beach'}
DUAL = 'DualSrcBlend: supported=1 enabled=1'
COLD = 'cold form: C:/x/variant_fixb26_fixb1b_fixf10 absent at 2026-10-04T00:00:00Z; entries of _ShaderCache/PPSA21564: 2'
EQ = 'manifest cmp EQUAL files 3 listsha ab'
DIFF = 'manifest cmp DIFFER only_before 1 only_after 1'
FORK_FIX = 'Fork build arigandores/KytyPS5 0e72bc1'
FORK_OLD = 'Fork build arigandores/KytyPS5 3d0e46d'
ES_OK = {'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': None, 'hold_s': 330.1, 'stable_s': 40.0}]}
ES_EXIT = {'attempts': [{'outcome': 'exited', 'detail': 'exit code 5', 'hold_exit': None, 'hold_s': None, 'stable_s': None}]}
ES_HOLD_EXIT = {'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': 5, 'hold_s': 50.0, 'stable_s': 40.0}]}
HEAD = [FORK_FIX, FSV, STC_FIX, PC_COLD, 'GuestOut: boot']


def ft(n, dt, draws):
    return 'FrameTrace: n=%d dt_us=%d draws=%d' % (n, dt, draws)


def scene(kind, hold_us=300000000, step=100000, k2=0):
    out = [ENTRY[kind], ft(1, 16667, 50), ft(2, 16667, 400)]
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


def make(name, kind, log, stdout='', run=ES_OK, idx=3000, glitch='one-frame glitches: 0', sheet='sheet: x.png frames 3000 step 1 tiles 8x6',
         sha_t=FIXSHA, before=INSHA, after=INSHA, cold=COLD, mcmp=EQ, mref=EQ):
    d = os.path.join(TMP, name)
    os.makedirs(d)
    with open(os.path.join(d, 'log.txt'), 'wb') as f:
        f.write(('\n'.join(log) + '\n').encode('utf-8'))
    with open(os.path.join(d, 'stdout.txt'), 'wb') as f:
        f.write(stdout.encode('utf-8'))
    if run is not None:
        with open(os.path.join(d, 'es.json'), 'w') as f:
            json.dump(run, f)
    if idx is not None and kind in R.VIDEO_KINDS:
        with open(os.path.join(d, 'rec.idx'), 'wb') as f:
            f.write(b'x\n' * idx)
    if kind not in R.VIDEO_KINDS:
        glitch = sheet = None
    files = (('glitch.txt', glitch), ('sheet.txt', sheet), ('installed_sha.txt', sha_t), ('installed_before.txt', before),
             ('installed_after.txt', after), ('cold.txt', cold), ('manifest_cmp.txt', mcmp), ('manifest_cmp_ref.txt', mref))
    for fn, t in files:
        if t is not None:
            with open(os.path.join(d, fn), 'wb') as f:
                f.write((t + '\n').encode('utf-8'))
    return d


def rowmap(d, kind):
    res = R.read(R.paths('fixture', kind, d), kind)
    out = {}
    lines = R.rows('fixture', res)
    for line in lines:
        if line.startswith('  ROW '):
            k, v = line[6:].rsplit(': ', 1)
            out[k] = v
    return res, out, lines


def check(name, cond):
    global OK, N, NF
    N += 1
    if not cond:
        OK = False
        NF += 1
        print('FAIL %s' % name)


def row(rm, prefix):
    hits = [v for k, v in rm.items() if k.startswith(prefix)]
    return hits[0] if len(hits) == 1 else 'AMBIGUOUS %d' % len(hits)


def rv(name, kind, log, prefix, **kw):
    return row(rowmap(make(name, kind, log, **kw), kind)[1], prefix)


# ---- kind_of, levels, constants
for k in R.KINDS:
    check('kind %s' % k, R.kind_of('fs5_' + k) == k)
for bad in ('fs5_r0', 'fs4_v', 'f12_v', 'fs5_v2', 'fs5_rd', 'fs5_vw'):
    try:
        R.kind_of(bad)
        check('kind %s raises' % bad, False)
    except SystemExit:
        check('kind %s raises' % bad, True)
check('levels', R.LEVEL['hb'] == 'hoover_beach' and all(R.LEVEL[k] == 'underwater_aerial_garden' for k in ('v', 'w', 'r1')))
check('constants', R.BIN_EXPECT.startswith('631ff987') and R.WANT.startswith('31cbfee8') and R.REV == '0e72bc1'
      and R.DIR_FIX == 'variant_fixb26_fixb1b_fixf10')

# ---- positive, per video kind
for k in ('v', 'r1', 'hb'):
    extra = ['FixSvalStat: validated=256 rejected=0'] if k == 'r1' else []
    d = make('%s_pos' % k, k, HEAD + extra + scene(k, 330000000))
    res, rm, lines = rowmap(d, k)
    for nm in ('binary sha256', 'installed 31cbfee8 before', 'installed 31cbfee8 after', 'revision text', 'translation cache directory',
               'cold form', 'entered', 'hold >= 300 s', 'no process end', 'frames >= 1 s after the first scene frame = 0', '0 death markers',
               'video index records', '0 one-frame glitches', 'sheet for the lead', 'manifest of the caches', 'manifest after the return',
               'no interference'):
        check('%s %s YES' % (k, nm), row(rm, nm) == 'YES')
    if k == 'r1':
        check('r1 FixSval member YES', row(rm, 'R1: FixSval mode=1') == 'YES')
        check('r1 0 validation failed member YES', row(rm, 'R1: 0 lines SPIR-V validation failed') == 'YES')
        check('r1 FixSvalStat present YES', row(rm, 'R1: FixSvalStat line present') == 'YES')
        check('r1 has no reference FixSval row', not any(x.startswith('FixSval mode=1') for x in rm))
    else:
        check('%s FixSval reference YES' % k, row(rm, 'FixSval mode=1') == 'YES')
        check('%s 0 validation failed reference YES' % k, row(rm, '0 lines SPIR-V validation failed') == 'YES')
        check('%s has no R1 rows' % k, not any(x.startswith('R1:') for x in rm))
    check('%s has no W rows' % k, not any(x.startswith('0 [Vulkan][E]') for x in rm))
    check('%s hb header only for hb' % k, any('REFERENCE, not a gate' in x for x in lines) == (k == 'hb'))
check('hb entered on its own level', rowmap(make('hb_sky', 'hb', HEAD + scene('v', 330000000)), 'hb')[1]['entered (entry line of hoover_beach)'] == 'NO')
check('v entered NO on a log of hoover_beach', rv('v_hb', 'v', HEAD + scene('hb', 330000000), 'entered') == 'NO')

# ---- V edges
check('v hold 300 s - 1 us: NO', rv('v_short', 'v', HEAD + scene('v', 300000000 - 1), 'hold >= 300 s') == 'NO')
check('v hold 300 s: YES', rv('v_300', 'v', HEAD + scene('v', 300000000), 'hold >= 300 s') == 'YES')
check('v video 2999: NO', rv('v_2999', 'v', HEAD + scene('v', 330000000), 'video index records', idx=2999) == 'NO')
check('v no video index: NO', rv('v_noidx', 'v', HEAD + scene('v', 330000000), 'video index records', idx=None) == 'NO')
check('v 1 glitch: NO', rv('v_gl', 'v', HEAD + scene('v', 330000000), '0 one-frame glitches', glitch='one-frame glitches: 1') == 'NO')
check('v glitch line missing: NOT_READ', rv('v_glmiss', 'v', HEAD + scene('v', 330000000), '0 one-frame glitches', glitch='x') == 'NOT_READ')
check('v no sheet line: NO', rv('v_nosheet', 'v', HEAD + scene('v', 330000000), 'sheet for the lead', sheet='error') == 'NO')
r_, m_, _ = rowmap(make('v_k2', 'v', HEAD + scene('v', 330000000, k2=2)), 'v')
check('v 2 frames >= 1 s: report row NO with the count, hold still YES', row(m_, 'frames >= 1 s after the first scene frame = 2') == 'NO'
      and r_['k2_after'] == 2 and row(m_, 'hold >= 300 s') == 'YES')
d = make('v_999', 'v', HEAD + [ENTRY['v'], ft(1, 1, 50), ft(2, 1, 400), ft(3, 999999, 400)] + scene('v', 330000000)[3:])
check('v frame 999 999 us not counted', rowmap(d, 'v')[0]['k2_after'] == 0)
check('v death: NO', rv('v_death', 'v', HEAD + scene('v', 330000000) + ['GpuHangAbort: x'], '0 death markers') == 'NO')
check('v death in stdout: NO', rv('v_death_so', 'v', HEAD + scene('v', 330000000), '0 death markers', stdout='--- Fatal Error ---\n') == 'NO')
check('v hold_exit: no end NO', rv('v_exit', 'v', HEAD + scene('v', 330000000), 'no process end', run=ES_HOLD_EXIT) == 'NO')
check('v exited: no end NO', rv('v_exit2', 'v', HEAD + scene('v', 330000000), 'no process end', run=ES_EXIT) == 'NO')
check('v no run json: NOT_READ', rv('v_norun', 'v', HEAD + scene('v', 330000000), 'no process end', run=None) == 'NOT_READ')
r_, m_, _ = rowmap(make('v_noentry', 'v', HEAD + [ft(1, 400000000, 400)]), 'v')
check('v no entry: entered NO, hold NO, frames row NO', row(m_, 'entered') == 'NO' and row(m_, 'hold >= 300 s') == 'NO'
      and row(m_, 'frames >= 1 s after the first scene frame = 0') == 'NO')
d = make('v_change', 'v', HEAD + [ENTRY['v'], ft(1, 1, 50), ft(2, 1, 400), ft(3, 100000000, 400),
                                   'GuestOut: Level has started: other', ft(4, 400000000, 400)])
r_, m_, _ = rowmap(d, 'v')
check('v rows after a scene change not counted', r_['hold_us'] == 100000000 and row(m_, 'hold >= 300 s') == 'NO')
check('v draws 99 never a scene frame: hold 0',
      rowmap(make('v_lowdraws', 'v', HEAD + [ENTRY['v']] + [ft(i, 100000, 99) for i in range(1, 4000)]), 'v')[0]['hold_us'] == 0)
check('v draws 100 is the first scene frame (not counted)',
      rowmap(make('v_d100', 'v', HEAD + [ENTRY['v'], ft(1, 5, 100)] + [ft(i, 100000, 100) for i in range(2, 3002)]), 'v')[0]['hold_us']
      == 300000000)

# ---- directory row and cold form
check('v base dir: fixf10 NO', rv('v_nofix', 'v', [FORK_FIX, FSV, STC_BASE, PC_COLD, 'GuestOut: b'] + scene('v', 330000000),
                                  'translation cache directory') == 'NO')
check('v mixed dirs: fixf10 NO', rv('v_mixed', 'v', [FORK_FIX, FSV, STC_FIX, STC_BASE, PC_COLD, 'GuestOut: b'] + scene('v', 330000000),
                                    'translation cache directory') == 'NO')
check('v no dir line: fixf10 NO', rv('v_nostc', 'v', [FORK_FIX, FSV, PC_COLD, 'GuestOut: b'] + scene('v', 330000000),
                                     'translation cache directory') == 'NO')
check('v forward slashes: fixf10 YES', rv('v_slash', 'v', [FORK_FIX, FSV, 'Shader translation cache: _ShaderCache/PPSA21564/'
                                                           'variant_fixb26_fixb1b_fixf10', PC_COLD, 'GuestOut: b'] + scene('v', 330000000),
                                          'translation cache directory') == 'YES')
check('v dir with a suffix after _fixf10: NO', rv('v_fixx', 'v', [FORK_FIX, FSV, STC_FIX + '_x', PC_COLD, 'GuestOut: b'] + scene('v', 330000000),
                                                  'translation cache directory') == 'NO')
check('v cold.txt without absent: cold NO', rv('v_warm', 'v', HEAD + scene('v', 330000000), 'cold form', cold='warm form: present') == 'NO')
check('v no cold.txt: cold NO', rv('v_nocold', 'v', HEAD + scene('v', 330000000), 'cold form', cold=None) == 'NO')
check('v first PipelinePrecache warm: cold NO', rv('v_pcw', 'v', [FORK_FIX, FSV, STC_FIX, PC_WARM, PC_COLD, 'GuestOut: b']
                                                   + scene('v', 330000000), 'cold form') == 'NO')
check('v PipelinePrecache of the base dir: cold NO', rv('v_pcb', 'v', [FORK_FIX, FSV, STC_FIX, PC_BASE, 'GuestOut: b'] + scene('v', 330000000),
                                                        'cold form') == 'NO')
check('v no PipelinePrecache line: cold NO', rv('v_pcn', 'v', [FORK_FIX, FSV, STC_FIX, 'GuestOut: b'] + scene('v', 330000000),
                                                'cold form') == 'NO')

# ---- FixSval and validation failed
check('r1 FixSval mode=0: NO', rv('r1_m0', 'r1', [FORK_FIX, 'FixSval: mode=0 ubo_std_layout=1', STC_FIX, PC_COLD, 'GuestOut: b']
                                  + scene('r1', 330000000), 'R1: FixSval mode=1') == 'NO')
check('r1 FixSval ubo=0: NO', rv('r1_u0', 'r1', [FORK_FIX, 'FixSval: mode=1 ubo_std_layout=0', STC_FIX, PC_COLD, 'GuestOut: b']
                                 + scene('r1', 330000000), 'R1: FixSval mode=1') == 'NO')
check('r1 FixSval after the first GuestOut: NO', rv('r1_late', 'r1', [FORK_FIX, STC_FIX, PC_COLD, 'GuestOut: b', FSV]
                                                    + scene('r1', 330000000), 'R1: FixSval mode=1') == 'NO')
check('r1 no FixSval line: NO', rv('r1_nofs', 'r1', [FORK_FIX, STC_FIX, PC_COLD, 'GuestOut: b'] + scene('r1', 330000000), 'R1: FixSval mode=1') == 'NO')
check('r1 two FixSval lines, second mode=0: NO', rv('r1_two', 'r1', [FORK_FIX, FSV, 'FixSval: mode=0 ubo_std_layout=1', STC_FIX, PC_COLD,
                                                                     'GuestOut: b'] + scene('r1', 330000000), 'R1: FixSval mode=1') == 'NO')
check('v FixSval mode=0: reference NO', rv('v_m0', 'v', [FORK_FIX, 'FixSval: mode=0 ubo_std_layout=1', STC_FIX, PC_COLD, 'GuestOut: b']
                                           + scene('v', 330000000), 'FixSval mode=1') == 'NO')
FAILL = '[Vulkan] SPIR-V validation failed: stage ps hash=0xC33DC20535A2CEBF'
r_, m_, _ = rowmap(make('r1_fail', 'r1', HEAD + scene('r1', 330000000) + [FAILL]), 'r1')
check('r1 1 failed line in the log: NO, hash parsed', row(m_, 'R1: 0 lines SPIR-V validation failed') == 'NO'
      and r_['fail_hashes'] == ['c33dc20535a2cebf'] and r_['fail_log'] == 1)
r_, m_, _ = rowmap(make('r1_fail_so', 'r1', HEAD + scene('r1', 330000000), stdout=FAILL + '\n' + FAILL + '\n'), 'r1')
check('r1 failed lines in the stdout: NO, counted 2, one hash', row(m_, 'R1: 0 lines SPIR-V validation failed') == 'NO'
      and r_['fail_stdout'] == 2 and r_['fail_hashes'] == ['c33dc20535a2cebf'])
check('w failed line: reference NO', rv('w_fail', 'w', [DUAL] + HEAD + ['[Vulkan][W] x'] + scene('w', 310000000) + [FAILL],
                                        '0 lines SPIR-V validation failed') == 'NO')
check('r1 no FixSvalStat: reference NO', rv('r1_nost', 'r1', HEAD + scene('r1', 330000000), 'R1: FixSvalStat line present') == 'NO')
r_, m_, _ = rowmap(make('r1_st', 'r1', HEAD + ['FixSvalStat: validated=256 rejected=0', 'FixSvalStat: validated=512 rejected=0']
                        + scene('r1', 330000000)), 'r1')
check('r1 FixSvalStat last line parsed, not taken for a FixSval line', r_['st_last'][1:] == (512, 0) and r_['st_lines'] == 2
      and len(r_['fs']) == 1)
check('r1 death: NO', rv('r1_death', 'r1', HEAD + scene('r1', 330000000) + ['Unhandled exception: x'], '0 death markers') == 'NO')
check('r1 exited: no end NO', rv('r1_exit', 'r1', HEAD + scene('r1', 330000000), 'no process end', run=ES_EXIT) == 'NO')
check('r1 1 glitch: NO', rv('r1_gl', 'r1', HEAD + scene('r1', 330000000), '0 one-frame glitches', glitch='one-frame glitches: 1') == 'NO')

# ---- binary rows
check('v tag binary 31cbfee8: NO', rv('v_binbad', 'v', HEAD + scene('v', 330000000), 'binary sha256', sha_t=INSHA) == 'NO')
check('v no installed_sha: NO', rv('v_binmiss', 'v', HEAD + scene('v', 330000000), 'binary sha256', sha_t=None) == 'NO')
check('v installed before not 31cbfee8: NO', rv('v_bef', 'v', HEAD + scene('v', 330000000), 'installed 31cbfee8 before', before=FIXSHA) == 'NO')
check('v installed after missing: NO', rv('v_aft', 'v', HEAD + scene('v', 330000000), 'installed 31cbfee8 after', after=None) == 'NO')
check('v installed after 540c035a: NO', rv('v_aft2', 'v', HEAD + scene('v', 330000000), 'installed 31cbfee8 after',
                                           after='540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1') == 'NO')
r_, m_, _ = rowmap(make('v_rev', 'v', [FORK_OLD] + HEAD[1:] + scene('v', 330000000)), 'v')
check('v revision of another build: NO (reference, other rows unchanged)', row(m_, 'revision text') == 'NO' and row(m_, 'hold >= 300 s') == 'YES')
check('v no revision text: NOT_PRESENT', rv('v_norev', 'v', HEAD[1:] + scene('v', 330000000), 'revision text') == 'NOT_PRESENT')
check('v git = revision text: YES', rv('v_gitrev', 'v', ['Release, clang, ver = 0.1, git = KytyPS5-x-g0e72bc19, date = x'] + HEAD[1:]
                                       + scene('v', 330000000), 'revision text') == 'YES')

# ---- manifest rows
check('v manifest DIFFER: NO', rv('v_mdiff', 'v', HEAD + scene('v', 330000000), 'manifest of the caches', mcmp=DIFF) == 'NO')
r_, m_, _ = rowmap(make('v_mrefdiff', 'v', HEAD + scene('v', 330000000), mref=DIFF), 'v')
check('v manifest vs ref DIFFER: ref NO, own YES', row(m_, 'manifest after the return') == 'NO' and row(m_, 'manifest of the caches') == 'YES')
r_, m_, _ = rowmap(make('v_mmiss', 'v', HEAD + scene('v', 330000000), mcmp=None, mref=None), 'v')
check('v manifests missing: both NO', row(m_, 'manifest after the return') == 'NO' and row(m_, 'manifest of the caches') == 'NO')

# ---- interference
for nm, extra in (('min', 'Window 1 minimized'), ('rec', 'Recovering Vulkan swapchain'), ('gp', 'GamePatch: loaded x')):
    check('v interference %s: NO' % nm, rv('v_int_' + nm, 'v', HEAD + scene('v', 330000000) + [extra], 'no interference') == 'NO')
r_, m_, _ = rowmap(make('v_focus', 'v', HEAD + scene('v', 330000000) + ['Window 1 lost keyboard focus', 'Window 1 restored']), 'v')
check('v focus / restored: data, interference YES', row(m_, 'no interference') == 'YES' and r_['win'] == {'lost keyboard focus': 1, 'restored': 1})
r_, m_, _ = rowmap(make('v_skip', 'v', HEAD + scene('v', 330000000) + ['AsyncPipelines: skipped draw x'] * 3), 'v')
check('v skipped draw: data only, counted 3, rows unchanged', r_['skipped_draw'] == 3 and row(m_, 'no interference') == 'YES'
      and row(m_, '0 death markers') == 'YES')

# ---- W
wl = [DUAL] + HEAD + ['[Vulkan][W] x'] + scene('w', 310000000)
res, rm, _ = rowmap(make('w_pos', 'w', wl), 'w')
for nm in ('binary sha256', 'installed 31cbfee8 before', 'installed 31cbfee8 after', 'translation cache directory', 'cold form', 'entered',
           'hold >= 300 s', 'no process end', '0 [Vulkan][E]', 'positive control', 'DualSrcBlend', 'FixSval mode=1',
           '0 lines SPIR-V validation failed', 'manifest of the caches', 'manifest after the return', 'no interference',
           '0 death markers (reference)'):
    check('w %s YES' % nm, row(rm, nm) == 'YES')
check('w has no video rows', not any(x.startswith('video index') for x in rm))
check('w 1 [Vulkan][E]: NO', rv('w_e', 'w', wl + ['[Vulkan][E] VUID-x'], '0 [Vulkan][E]') == 'NO')
check('w 0 [Vulkan][W]: positive control NO', rv('w_now', 'w', [x for x in wl if not x.startswith('[Vulkan][W]')], 'positive control') == 'NO')
check('w DualSrcBlend after the first GuestOut: NO', rv('w_dual_late', 'w', HEAD + [DUAL, '[Vulkan][W] x'] + scene('w', 310000000),
                                                        'DualSrcBlend') == 'NO')
check('w DualSrcBlend enabled=0: NO', rv('w_dual0', 'w', ['DualSrcBlend: supported=1 enabled=0'] + HEAD + ['[Vulkan][W] x']
                                         + scene('w', 310000000), 'DualSrcBlend') == 'NO')
check('w no DualSrcBlend line: NO', rv('w_dualn', 'w', HEAD + ['[Vulkan][W] x'] + scene('w', 310000000), 'DualSrcBlend') == 'NO')
check('w hold 300 s: YES', rv('w_300', 'w', [DUAL] + HEAD + ['[Vulkan][W] x'] + scene('w', 300000000), 'hold >= 300 s') == 'YES')
check('w hold 300 s - 1 us: NO', rv('w_short', 'w', [DUAL] + HEAD + ['[Vulkan][W] x'] + scene('w', 299999999), 'hold >= 300 s') == 'NO')
check('w death: reference NO', rv('w_death', 'w', wl + ['ErrorDeviceLost'], '0 death markers (reference)') == 'NO')

# ---- output: ASCII and strict cp1250 without PYTHONIOENCODING (non-ASCII bytes in the log)
d = make('enc', 'v', ['Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10\\\u043a\u044d\u0448',
                      'Release, x, ver = 1, git = \u0432\u0435\u0440\u0441\u0438\u044f, date = y', FSV, PC_COLD, 'GuestOut: boot']
         + scene('v', 330000000))
env = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
env['PYTHONIOENCODING'] = 'cp1250:strict'
p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'v'], capture_output=True, env=env)
check('cp1250 strict: rc 0', p.returncode == 0)
check('cp1250 strict: stdout ASCII only', all(b < 128 for b in p.stdout))
check('cp1250 strict: rows printed', b'ROW hold >= 300 s' in p.stdout)
env2 = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
p2 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'v'], capture_output=True, env=env2)
check('no PYTHONIOENCODING: rc 0, ASCII', p2.returncode == 0 and all(b < 128 for b in p2.stdout))
jp = os.path.join(TMP, 'out.json')
p3 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'v', '--json', jp], capture_output=True, env=env2)
check('json written', p3.returncode == 0 and json.load(open(jp))['kind'] == 'v')
p4 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'x'], capture_output=True, env=env2)
check('unknown kind refused', p4.returncode != 0)
d = make('enc_r1', 'r1', HEAD + scene('r1', 330000000), stdout=FAILL + ' \u043e\u0448\u0438\u0431\u043a\u0430\n')
p5 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'r1'], capture_output=True, env=env)
check('r1 cp1250 strict: rc 0, ASCII, R1 rows', p5.returncode == 0 and all(b < 128 for b in p5.stdout) and b'ROW R1: 0 lines' in p5.stdout)

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d fails %d' % (N, NF))
print('ALL OK' if OK else 'SOME FAILED')
