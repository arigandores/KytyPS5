"""Track F link F14g (HPP-507): fixtures of f14g_read.py - every row of the seal section 4 and every edge (port of F12f
test_f12f_read.py): the binary c01bde0c in every kind and the installed adb0c82f before / after, the directory row (_fixf19 in every line,
rd included; base dir, _fixf10 without _fixf19, mixed lines, no line, a suffix after _fixf19), hold 300 s / 300 s - 1 us, 3000 / 2999 video
records, glitches, sheet, frames >= 1 s (report row only), process end, death markers, W rows ([Vulkan][E] incl. VUID-06479, [Vulkan][W]
= 0 / 1, DualSrcBlend before / after the first GuestOut), manifest EQUAL / DIFFER / missing for both compares, interference (minimized,
Recovering Vulkan swapchain, GamePatch), rd captures (RenderDoc lines, rdc_sha lines, rd_cmp_f14c.py outputs: the item 409 (g)(4) letter
ACTS_IN_FRAME / CODE_FAIL by manual D16 / CODE_FAIL by native D16 with compareEnable 0 / OTHER by another op or filter / UNDETERMINED by
no record; D32 manual records do not count; a missing done line; SUMMARY != AGG sums; count mismatch; side files .qrd.txt), revision
text (never a gate; 082d161 and g082d1612 named, g9df15713 NO), output in strict cp1250 without PYTHONIOENCODING.
The first output line names the suite and the target with their sha256; the last line is ALL OK.  ASCII only."""
import hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'f14g_read.py')
sys.path.insert(0, HERE)
import f14g_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f14g_read.py sha256 %s target f14g_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(TARGET)))
OK = True
N = 0
NF = 0
TMP = tempfile.mkdtemp(prefix='f14g_fx_')
FIXSHA = R.BIN_EXPECT
INSHA = R.WANT
STC_FIX = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19'
STC_F10 = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10'
STC_BASE = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b'
ENTRY = {'rd': 'GuestOut: Level has started: underwater_aerial_garden', 'v1': 'GuestOut: Level has started: underwater_aerial_garden',
         'w1': 'GuestOut: Level has started: underwater_aerial_garden', 'ef': 'GuestOut: Level has started: enemy_final'}
DUAL = 'DualSrcBlend: supported=1 enabled=1'
COLD = 'cold form: C:/x/variant_fixb26_fixb1b_fixf10_fixf19 absent at 2026-10-04T00:00:00Z; entries of _ShaderCache/PPSA21564: 2'
EQ = 'manifest cmp EQUAL files 3 listsha ab'
DIFF = 'manifest cmp DIFFER only_before 1 only_after 1'
FORK_FIX = 'Fork build arigandores/KytyPS5 082d161'
FORK_INST = 'Fork build arigandores/KytyPS5 4d9e8ab'
ES_OK = {'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': None, 'hold_s': 330.1, 'stable_s': 40.0}]}
ES_EXIT = {'attempts': [{'outcome': 'exited', 'detail': 'exit code 5', 'hold_exit': None, 'hold_s': None, 'stable_s': None}]}
ES_HOLD_EXIT = {'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': 5, 'hold_s': 50.0, 'stable_s': 40.0}]}


def agg(kind, view, cen, cop, n, mag='VK_FILTER_LINEAR', mn='VK_FILTER_LINEAR', stage='FRAGMENT'):
    site = 'manual/ExplicitLod/FOrdLessThanEqual' if kind == 'manual' else 'native/SampleDrefExplicitLod/-'
    return ('AGG stage=%s mod=0123456789abcdef site=%s img=0:1[0] smp=0:2[0] depthflag=1 mag=%s min=%s mip=VK_SAMPLER_MIPMAP_MODE_NEAREST '
            'cmpEnable=%s cmpOp=%s aniso=0 smp_pnext=- view_format=%s aspect=VK_IMAGE_ASPECT_DEPTH_BIT image_format=%s src=set1/set1 n=%d'
            % (stage, site, mag, mn, cen, cop, view, view, n))


D16 = 'VK_FORMAT_D16_UNORM'
D32 = 'VK_FORMAT_D32_SFLOAT'
LEQ = 'VK_COMPARE_OP_LESS_OR_EQUAL'
NEV = 'VK_COMPARE_OP_NEVER'


def cmpout(aggs, done=True, unres=(), sum_records=None, sum_unres=None):
    recs = 0
    out = ['MODULE x']
    for a in aggs:
        out.append(a)
        recs += int(a.rsplit('n=', 1)[1])
    nu = 0
    for u in unres:
        out.append('UNRES stage=FRAGMENT mod=x site=y img=z smp=w n=%d' % u)
        nu += u
    out.append('SUMMARY draws_dispatches 900 with_compare_sites 40 modules 300 modules_with_sites 20 samplers 30 views 1000 pipelines 300 '
               'agg_rows %d records %d unresolved %d descriptor_copies 0' % (len(aggs), recs if sum_records is None else sum_records,
                                                                            nu if sum_unres is None else sum_unres))
    if done:
        out.append('done')
    return '\n'.join(out)


GOOD = cmpout([agg('native', D16, '1', LEQ, 500), agg('manual', D32, '0', NEV, 400), agg('native', D32, '1', LEQ, 7)])


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
         sha_t=None, before=INSHA, after=INSHA, cold=COLD, mcmp=EQ, mref=EQ, rdc=None, rdcmp=None, side=False):
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
    if sha_t is None:
        sha_t = FIXSHA
    if kind not in R.VIDEO_KINDS:
        glitch = sheet = None
    files = (('glitch.txt', glitch), ('sheet.txt', sheet), ('installed_sha.txt', sha_t), ('installed_before.txt', before),
             ('installed_after.txt', after), ('cold.txt', cold), ('manifest_cmp.txt', mcmp), ('manifest_cmp_ref.txt', mref),
             ('rdc_sha.txt', rdc))
    for fn, t in files:
        if t is not None:
            with open(os.path.join(d, fn), 'wb') as f:
                f.write((t + '\n').encode('utf-8'))
    for i, t in enumerate(rdcmp or [], 1):
        if t is None:
            continue
        with open(os.path.join(d, 'rdcmp_k%02d.txt' % i), 'wb') as f:
            f.write((t + '\n').encode('utf-8'))
        if side:
            with open(os.path.join(d, 'rdcmp_k%02d.txt.qrd.txt' % i), 'wb') as f:
                f.write(b'qrenderdoc output\n')
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
    global OK, N, NF
    N += 1
    if not cond:
        OK = False
        NF += 1
        print('FAIL %s' % name)


def row(rm, prefix):
    hits = [v for k, v in rm.items() if k.startswith(prefix)]
    return hits[0] if len(hits) == 1 else 'AMBIGUOUS %d' % len(hits)


# ---- kind_of, levels, constants
for k in R.KINDS:
    check('kind %s' % k, R.kind_of('f19_' + k) == k)
for bad in ('f19_v', 'f12_v', 'f19_w', 'f19_rdx', 'f19_v2', 'fs4_v'):
    try:
        R.kind_of(bad)
        check('kind %s raises' % bad, False)
    except SystemExit:
        check('kind %s raises' % bad, True)
check('levels', R.LEVEL['ef'] == 'enemy_final' and all(R.LEVEL[k] == 'underwater_aerial_garden' for k in ('rd', 'v1', 'w1')))
check('constants', R.BIN_EXPECT.startswith('c01bde0c') and R.WANT.startswith('adb0c82f') and R.REV == '082d161'
      and R.DIR_FIX == 'variant_fixb26_fixb1b_fixf10_fixf19' and len(R.BIN_EXPECT) == 64 and len(R.WANT) == 64)

# ---- V positive, per video kind
for k in ('v1', 'ef'):
    d = make('%s_pos' % k, k, [FORK_FIX, STC_FIX, 'GuestOut: boot'] + scene(k, 330000000))
    res, rm = rowmap(d, k)
    check('%s binary YES' % k, row(rm, 'binary sha256') == 'YES')
    check('%s before / after YES' % k, row(rm, 'installed adb0c82f before') == 'YES' and row(rm, 'installed adb0c82f after') == 'YES')
    check('%s revision YES' % k, row(rm, 'revision text') == 'YES')
    check('%s fixf19 YES' % k, row(rm, 'translation cache directory') == 'YES')
    check('%s cold YES' % k, row(rm, 'cold form') == 'YES')
    check('%s entered YES' % k, row(rm, 'entered') == 'YES')
    check('%s hold YES' % k, row(rm, 'hold >= 300 s') == 'YES')
    check('%s no end YES' % k, row(rm, 'no process end') == 'YES')
    check('%s frames >= 1 s = 0 YES (report)' % k, row(rm, 'frames >= 1 s after the first scene frame = 0') == 'YES')
    check('%s death YES' % k, row(rm, '0 death markers') == 'YES')
    check('%s video YES' % k, row(rm, 'video index records') == 'YES')
    check('%s glitches YES' % k, row(rm, '0 one-frame glitches') == 'YES')
    check('%s sheet YES' % k, row(rm, 'sheet for the lead') == 'YES')
    check('%s manifest YES' % k, row(rm, 'manifest of the caches') == 'YES' and row(rm, 'manifest after the return') == 'YES')
    check('%s interference none YES' % k, row(rm, 'no interference') == 'YES')
    check('%s has no W rows' % k, not any(x.startswith('0 [Vulkan][E]') for x in rm))
    check('%s has no rd rows' % k, not any(x.startswith(('item 409', 'every capture read')) for x in rm))

# ---- V edges
vh = [FORK_FIX, STC_FIX, 'GuestOut: boot']
d = make('v_short', 'v1', vh + scene('v1', 300000000 - 1))
check('v1 hold 300 s - 1 us: NO', row(rowmap(d, 'v1')[1], 'hold >= 300 s') == 'NO')
d = make('v_300', 'v1', vh + scene('v1', 300000000))
check('v1 hold 300 s: YES', row(rowmap(d, 'v1')[1], 'hold >= 300 s') == 'YES')
d = make('v_2999', 'v1', vh + scene('v1', 330000000), idx=2999)
check('v1 video 2999: NO', row(rowmap(d, 'v1')[1], 'video index records') == 'NO')
d = make('ef_2999', 'ef', vh + scene('ef', 330000000), idx=2999)
check('ef video 2999: NO', row(rowmap(d, 'ef')[1], 'video index records') == 'NO')
d = make('v_noidx', 'v1', vh + scene('v1', 330000000), idx=None)
check('v1 no video index: NO', row(rowmap(d, 'v1')[1], 'video index records') == 'NO')
d = make('v_gl', 'v1', vh + scene('v1', 330000000), glitch='one-frame glitches: 1')
check('v1 1 glitch: NO', row(rowmap(d, 'v1')[1], '0 one-frame glitches') == 'NO')
d = make('v_glmiss', 'v1', vh + scene('v1', 330000000), glitch='nothing')
check('v1 glitch line missing: NOT_READ', row(rowmap(d, 'v1')[1], '0 one-frame glitches') == 'NOT_READ')
d = make('v_nosheet', 'v1', vh + scene('v1', 330000000), sheet='error')
check('v1 no sheet line: NO', row(rowmap(d, 'v1')[1], 'sheet for the lead') == 'NO')
d = make('v_k2', 'v1', vh + scene('v1', 330000000, k2=2))
r_, m_ = rowmap(d, 'v1')
check('v1 2 frames >= 1 s: report row NO with the count, hold still YES', row(m_, 'frames >= 1 s after the first scene frame = 2') == 'NO'
      and r_['k2_after'] == 2 and row(m_, 'hold >= 300 s') == 'YES')
d = make('v_999', 'v1', vh + [ENTRY['v1'], ft(1, 1, 50), ft(2, 1, 400), ft(3, 999999, 400)] + scene('v1', 330000000)[3:])
check('v1 frame 999 999 us not counted', rowmap(d, 'v1')[0]['k2_after'] == 0)
d = make('v_death', 'v1', vh + scene('v1', 330000000) + ['GpuHangAbort: x'])
check('v1 death: NO', row(rowmap(d, 'v1')[1], '0 death markers') == 'NO')
d = make('ef_death', 'ef', vh + scene('ef', 330000000) + ['Unhandled exception: x'])
check('ef death: NO', row(rowmap(d, 'ef')[1], '0 death markers') == 'NO')
d = make('v_death_so', 'v1', vh + scene('v1', 330000000), stdout='--- Fatal Error ---\n')
check('v1 death in stdout: NO', row(rowmap(d, 'v1')[1], '0 death markers') == 'NO')
d = make('v_exit', 'v1', vh + scene('v1', 330000000), run=ES_HOLD_EXIT)
check('v1 hold_exit: no end NO', row(rowmap(d, 'v1')[1], 'no process end') == 'NO')
d = make('v_exit2', 'v1', vh + scene('v1', 330000000), run=ES_EXIT)
check('v1 exited: no end NO', row(rowmap(d, 'v1')[1], 'no process end') == 'NO')
d = make('v_norun', 'v1', vh + scene('v1', 330000000), run=None)
check('v1 no run json: NOT_READ', row(rowmap(d, 'v1')[1], 'no process end') == 'NOT_READ')
d = make('v_noentry', 'v1', vh + [ft(1, 400000000, 400)])
r_, m_ = rowmap(d, 'v1')
check('v1 no entry: entered NO, hold NO, frames row NO', row(m_, 'entered') == 'NO' and row(m_, 'hold >= 300 s') == 'NO'
      and row(m_, 'frames >= 1 s after the first scene frame = 0') == 'NO')
d = make('ef_wronglvl', 'ef', vh + scene('v1', 330000000))
check('ef log of Sky Garden: entered NO', row(rowmap(d, 'ef')[1], 'entered') == 'NO')
d = make('v_change', 'v1', vh + [ENTRY['v1'], ft(1, 1, 50), ft(2, 1, 400), ft(3, 100000000, 400),
                                  'GuestOut: Level has started: other', ft(4, 400000000, 400)])
r_, m_ = rowmap(d, 'v1')
check('v1 rows after a scene change not counted', r_['hold_us'] == 100000000 and row(m_, 'hold >= 300 s') == 'NO')
d = make('v_lowdraws', 'v1', vh + [ENTRY['v1']] + [ft(i, 100000, 99) for i in range(1, 4000)])
check('v1 draws 99 never a scene frame: hold 0', rowmap(d, 'v1')[0]['hold_us'] == 0)
d = make('v_draws100', 'v1', vh + [ENTRY['v1'], ft(1, 5, 100)] + [ft(i, 100000, 100) for i in range(2, 3002)])
check('v1 draws 100 is the first scene frame (not counted)', rowmap(d, 'v1')[0]['hold_us'] == 300000000)

# ---- directory row
for nm, stc in (('base', STC_BASE), ('f10', STC_F10)):
    d = make('v_dir_' + nm, 'v1', [FORK_FIX, stc, 'GuestOut: boot'] + scene('v1', 330000000))
    check('v1 dir %s: fixf19 NO' % nm, row(rowmap(d, 'v1')[1], 'translation cache directory') == 'NO')
d = make('v_mixed', 'v1', [FORK_FIX, STC_FIX, STC_F10, 'GuestOut: boot'] + scene('v1', 330000000))
check('v1 mixed dirs: fixf19 NO', row(rowmap(d, 'v1')[1], 'translation cache directory') == 'NO')
d = make('v_nostc', 'v1', [FORK_FIX, 'GuestOut: boot'] + scene('v1', 330000000))
check('v1 no dir line: fixf19 NO', row(rowmap(d, 'v1')[1], 'translation cache directory') == 'NO')
d = make('v_slash', 'v1', [FORK_FIX, 'Shader translation cache: _ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19', 'GuestOut: b']
         + scene('v1', 330000000))
check('v1 forward slashes: fixf19 YES', row(rowmap(d, 'v1')[1], 'translation cache directory') == 'YES')
d = make('v_fixx', 'v1', [FORK_FIX, STC_FIX + '_x', 'GuestOut: b'] + scene('v1', 330000000))
check('v1 dir with a suffix after _fixf19: NO', row(rowmap(d, 'v1')[1], 'translation cache directory') == 'NO')
d = make('v_warm', 'v1', vh + scene('v1', 330000000), cold='warm form: present')
check('v1 cold.txt without absent: cold NO', row(rowmap(d, 'v1')[1], 'cold form') == 'NO')
d = make('w_dir', 'w1', [FORK_FIX, DUAL, STC_F10, 'GuestOut: boot', '[Vulkan][W] x'] + scene('w1', 310000000))
check('w1 dir _fixf10 only: fixf19 NO', row(rowmap(d, 'w1')[1], 'translation cache directory') == 'NO')

# ---- binary rows
d = make('v_binbad', 'v1', vh + scene('v1', 330000000), sha_t=INSHA)
check('v1 tag binary adb0c82f: NO', row(rowmap(d, 'v1')[1], 'binary sha256') == 'NO')
d = make('v_bef', 'v1', vh + scene('v1', 330000000), before=FIXSHA)
check('v1 installed before not adb0c82f: NO', row(rowmap(d, 'v1')[1], 'installed adb0c82f before') == 'NO')
d = make('v_bef31', 'v1', vh + scene('v1', 330000000), before='31cbfee8' + '0' * 56)
check('v1 installed before 31cbfee8: NO (item 443 (d)(1))', row(rowmap(d, 'v1')[1], 'installed adb0c82f before') == 'NO')
d = make('v_aft', 'v1', vh + scene('v1', 330000000), after=None)
check('v1 installed after missing: NO', row(rowmap(d, 'v1')[1], 'installed adb0c82f after') == 'NO')
d = make('v_rev', 'v1', [FORK_INST, STC_FIX, 'GuestOut: b'] + scene('v1', 330000000))
r_, m_ = rowmap(d, 'v1')
check('v1 revision of another build: NO (reference, other rows unchanged)', row(m_, 'revision text') == 'NO' and row(m_, 'hold >= 300 s') == 'YES')
d = make('v_norev', 'v1', [STC_FIX, 'GuestOut: b'] + scene('v1', 330000000))
check('v1 no revision text: NOT_PRESENT', row(rowmap(d, 'v1')[1], 'revision text') == 'NOT_PRESENT')
d = make('v_gitrev', 'v1', ['Release, clang, ver = 0.1, git = KytyPS5-2026-09-15-6a2987a-2113-g082d1612, date = x', STC_FIX, 'GuestOut: b']
         + scene('v1', 330000000))
check('v1 git = ...-2113-g082d1612: YES', row(rowmap(d, 'v1')[1], 'revision text') == 'YES')
d = make('v_sdlrev', 'v1', ['Release, clang, ver = 0.1, git = SDL-KytyPS5-2026-09-15-6a2987a-2103-g9df15713, date = x', STC_FIX,
                            'GuestOut: b'] + scene('v1', 330000000))
check('v1 git = ...g9df15713 (SDL_REVISION text): NO', row(rowmap(d, 'v1')[1], 'revision text') == 'NO')

# ---- manifest rows
d = make('v_mdiff', 'v1', vh + scene('v1', 330000000), mcmp=DIFF)
check('v1 manifest DIFFER: NO', row(rowmap(d, 'v1')[1], 'manifest of the caches') == 'NO')
d = make('v_mrefdiff', 'v1', vh + scene('v1', 330000000), mref=DIFF)
r_, m_ = rowmap(d, 'v1')
check('v1 manifest vs ref DIFFER: ref NO, own YES', row(m_, 'manifest after the return') == 'NO' and row(m_, 'manifest of the caches') == 'YES')
d = make('v_mmiss', 'v1', vh + scene('v1', 330000000), mcmp=None, mref=None)
r_, m_ = rowmap(d, 'v1')
check('v1 manifests missing: both NO', row(m_, 'manifest after the return') == 'NO' and row(m_, 'manifest of the caches') == 'NO')

# ---- interference
for nm, extra in (('min', 'Window 1 minimized'), ('rec', 'Recovering Vulkan swapchain'), ('gp', 'GamePatch: loaded x')):
    d = make('v_int_' + nm, 'v1', vh + scene('v1', 330000000) + [extra])
    check('v1 interference %s: NO' % nm, row(rowmap(d, 'v1')[1], 'no interference') == 'NO')
d = make('v_focus', 'v1', vh + scene('v1', 330000000) + ['Window 1 lost keyboard focus', 'Window 1 restored'])
r_, m_ = rowmap(d, 'v1')
check('v1 focus / restored: data, interference YES', row(m_, 'no interference') == 'YES' and r_['win'] == {'lost keyboard focus': 1, 'restored': 1})

# ---- W
wl = [FORK_FIX, DUAL, STC_FIX, 'GuestOut: boot', '[Vulkan][W] x'] + scene('w1', 310000000)
d = make('w_pos', 'w1', wl)
res, rm = rowmap(d, 'w1')
for nm in ('binary sha256', 'translation cache directory', 'entered', 'hold >= 300 s', '0 [Vulkan][E]', 'positive control',
           'DualSrcBlend', 'manifest of the caches', 'manifest after the return', 'no interference', '0 death markers (reference)'):
    check('w1 %s YES' % nm, row(rm, nm) == 'YES')
check('w1 has no video rows', not any(x.startswith('video index') for x in rm))
d = make('w_e', 'w1', wl + ['[Vulkan][E] VUID-x'])
r_, m_ = rowmap(d, 'w1')
check('w1 1 [Vulkan][E]: NO, 06479 count 0', row(m_, '0 [Vulkan][E]') == 'NO' and r_['vke_06479'] == 0)
d = make('w_06479', 'w1', wl + ['[Vulkan][E] Validation Error: [ VUID-vkCmdDraw-None-06479 ] x'])
r_, m_ = rowmap(d, 'w1')
check('w1 VUID-06479: NO, counted', row(m_, '0 [Vulkan][E]') == 'NO' and r_['vke'] == 1 and r_['vke_06479'] == 1)
d = make('w_now', 'w1', [x for x in wl if not x.startswith('[Vulkan][W]')])
check('w1 0 [Vulkan][W]: positive control NO', row(rowmap(d, 'w1')[1], 'positive control') == 'NO')
d = make('w_dual_late', 'w1', [FORK_FIX, STC_FIX, 'GuestOut: boot', DUAL, '[Vulkan][W] x'] + scene('w1', 310000000))
check('w1 DualSrcBlend after the first GuestOut: NO', row(rowmap(d, 'w1')[1], 'DualSrcBlend') == 'NO')
d = make('w_dual0', 'w1', [FORK_FIX, 'DualSrcBlend: supported=1 enabled=0', STC_FIX, 'GuestOut: boot', '[Vulkan][W] x'] + scene('w1', 310000000))
check('w1 DualSrcBlend enabled=0: NO', row(rowmap(d, 'w1')[1], 'DualSrcBlend') == 'NO')
d = make('w_300', 'w1', [FORK_FIX, DUAL, STC_FIX, 'GuestOut: boot', '[Vulkan][W] x'] + scene('w1', 300000000))
check('w1 hold 300 s: YES', row(rowmap(d, 'w1')[1], 'hold >= 300 s') == 'YES')
d = make('w_short', 'w1', [FORK_FIX, DUAL, STC_FIX, 'GuestOut: boot', '[Vulkan][W] x'] + scene('w1', 299999999))
check('w1 hold 300 s - 1 us: NO', row(rowmap(d, 'w1')[1], 'hold >= 300 s') == 'NO')

# ---- RD
rl = [FORK_FIX, STC_FIX, 'GuestOut: boot', 'RenderDoc: level started at frame 193, capture at frame 202 (+1 more)'] + scene('rd', 120000000)
rl += ['RenderDoc: auto capture at frame 202 (level+9)', 'RenderDoc: captured guest flip 2/2', 'RenderDoc: capture finished',
       'RenderDoc: auto capture at frame 1093 (level+900)', 'RenderDoc: captured guest flip 2/2', 'RenderDoc: capture finished']
RDC2 = 'aa  f19_rd_k01.rdc\nbb  f19_rd_k02.rdc'
L1 = 'item 409 (g)(4) letter on k01'
LA = 'item 409 (g)(4) letter on all captures'
d = make('rd_pos', 'rd', rl, rdc=RDC2, rdcmp=[GOOD, GOOD])
res, rm = rowmap(d, 'rd')
check('rd binary c01bde0c YES', row(rm, 'binary sha256') == 'YES')
check('rd revision YES', row(rm, 'revision text') == 'YES')
check('rd fixf19 dir YES (member in rd)', row(rm, 'translation cache directory') == 'YES')
check('rd entered YES', row(rm, 'entered') == 'YES')
check('rd capture made YES', row(rm, '>= 1 capture made') == 'YES')
check('rd every capture read YES', row(rm, 'every capture read') == 'YES')
check('rd letter k01 ACTS_IN_FRAME YES', row(rm, L1) == 'YES' and any('ACTS_IN_FRAME' in k for k in rm if k.startswith(L1)))
check('rd letter all YES', row(rm, LA) == 'YES')
check('rd counts A B C D', res['rdcmp'][0]['A'] == 0 and res['rdcmp'][0]['B'] == 500 and res['rdcmp'][0]['C'] == 500
      and res['rdcmp'][0]['D'] == 0 and res['rdcmp'][0]['records'] == 907)
check('rd RenderDoc lines', res['rd_level'] == 193 and res['rd_auto'] == [(202, 9), (1093, 900)] and res['rd_flip2'] == 2
      and res['rd_finished'] == 2 and res['rdc_n'] == 2)
check('rd TAB rows printed', sum(1 for x in R.rows('fixture', res) if x.startswith('    TAB k01 ')) == 3)
check('rd has no hold / video rows', not any(x.startswith(('hold >=', 'video index')) for x in rm))
check('rd interference none YES', row(rm, 'no interference') == 'YES')
d = make('rd_side', 'rd', rl, rdc=RDC2, rdcmp=[GOOD, GOOD], side=True)
r_, m_ = rowmap(d, 'rd')
check('rd side files .qrd.txt are not reads: 2 reads, every read YES', len(r_['rdcmp']) == 2 and row(m_, 'every capture read') == 'YES')
BADM = cmpout([agg('native', D16, '1', LEQ, 500), agg('manual', D16, '0', NEV, 1)])
d = make('rd_man16', 'rd', rl, rdc=RDC2, rdcmp=[BADM, GOOD])
r_, m_ = rowmap(d, 'rd')
check('rd 1 manual D16 record: CODE_FAIL, k01 NO, all NO', r_['rdcmp'][0]['letter'] == 'CODE_FAIL' and row(m_, L1) == 'NO' and row(m_, LA) == 'NO')
BADD = cmpout([agg('native', D16, '1', LEQ, 500), agg('native', D16, '0', NEV, 2)])
d = make('rd_cen0', 'rd', rl, rdc=RDC2, rdcmp=[BADD, GOOD])
r_, m_ = rowmap(d, 'rd')
check('rd native D16 compareEnable 0: CODE_FAIL', r_['rdcmp'][0]['letter'] == 'CODE_FAIL' and r_['rdcmp'][0]['D'] == 2 and row(m_, L1) == 'NO')
OTH = cmpout([agg('native', D16, '1', 'VK_COMPARE_OP_GREATER', 5), agg('native', D16, '1', LEQ, 5)])
d = make('rd_other', 'rd', rl, rdc=RDC2, rdcmp=[OTH, GOOD])
r_, m_ = rowmap(d, 'rd')
check('rd native D16 GREATER: OTHER', r_['rdcmp'][0]['letter'] == 'OTHER' and row(m_, L1) == 'NO')
OTHF = cmpout([agg('native', D16, '1', LEQ, 5, mag='VK_FILTER_NEAREST', mn='VK_FILTER_NEAREST')])
d = make('rd_nearest', 'rd', rl, rdc=RDC2, rdcmp=[OTHF])
check('rd native D16 NEAREST: OTHER', rowmap(d, 'rd')[0]['rdcmp'][0]['letter'] == 'OTHER')
OTHM = cmpout([agg('native', D16, '1', LEQ, 5, mn='VK_FILTER_NEAREST')])
d = make('rd_minnear', 'rd', rl, rdc=RDC2, rdcmp=[OTHM])
check('rd native D16 min NEAREST only: OTHER', rowmap(d, 'rd')[0]['rdcmp'][0]['letter'] == 'OTHER')
NOB = cmpout([agg('manual', D32, '0', NEV, 50)])
d = make('rd_noB', 'rd', rl, rdc=RDC2, rdcmp=[NOB, GOOD])
r_, m_ = rowmap(d, 'rd')
check('rd only manual D32: OTHER (B = 0), k01 NO, all NO', r_['rdcmp'][0]['letter'] == 'OTHER' and row(m_, L1) == 'NO' and row(m_, LA) == 'NO')
EMP = cmpout([])
d = make('rd_empty', 'rd', rl, rdc=RDC2, rdcmp=[EMP, GOOD])
r_, m_ = rowmap(d, 'rd')
check('rd no record: UNDETERMINED on k01, k02 ACTS', r_['rdcmp'][0]['letter'] == 'UNDETERMINED' and r_['rdcmp'][1]['letter'] == 'ACTS_IN_FRAME'
      and row(m_, L1) == 'NO' and row(m_, LA) == 'NO')
CS16 = cmpout([agg('native', D16, '1', LEQ, 3, stage='CS')])
d = make('rd_cs', 'rd', rl, rdc=RDC2, rdcmp=[CS16])
check('rd native D16 in CS counts in B and C', rowmap(d, 'rd')[0]['rdcmp'][0]['B'] == 3 and rowmap(d, 'rd')[0]['rdcmp'][0]['letter'] == 'ACTS_IN_FRAME')
ND = cmpout([agg('native', D16, '1', LEQ, 3)], done=False)
d = make('rd_nodone', 'rd', rl, rdc=RDC2, rdcmp=[GOOD, ND])
r_, m_ = rowmap(d, 'rd')
check('rd read without done: every read NO, letter NOT_READ', row(m_, 'every capture read') == 'NO' and r_['rdcmp'][1]['letter'] == 'NOT_READ')
SM = cmpout([agg('native', D16, '1', LEQ, 3)], sum_records=4)
d = make('rd_summis', 'rd', rl, rdc=RDC2, rdcmp=[GOOD, SM])
check('rd SUMMARY records != AGG sum: every read NO', row(rowmap(d, 'rd')[1], 'every capture read') == 'NO')
SU = cmpout([agg('native', D16, '1', LEQ, 3)], unres=(2,))
d = make('rd_unres', 'rd', rl, rdc=RDC2, rdcmp=[GOOD, SU])
r_, m_ = rowmap(d, 'rd')
check('rd UNRES 2 counted, sums agree: every read YES', r_['rdcmp'][1]['unres'] == 2 and row(m_, 'every capture read') == 'YES')
SB = GOOD.replace('n=500', 'n=x')
d = make('rd_badagg', 'rd', rl, rdc=RDC2, rdcmp=[GOOD, SB])
check('rd malformed AGG: every read NO', row(rowmap(d, 'rd')[1], 'every capture read') == 'NO')
d = make('rd_count', 'rd', rl, rdc=RDC2, rdcmp=[GOOD])
check('rd 2 captures, 1 read: every capture read NO', row(rowmap(d, 'rd')[1], 'every capture read') == 'NO')
d = make('rd_nok01', 'rd', rl, rdc=RDC2, rdcmp=[None, GOOD])
r_, m_ = rowmap(d, 'rd')
check('rd no k01 file: k01 row NO (NO_K01)', row(m_, L1) == 'NO' and any('NO_K01' in k for k in m_))
d = make('rd_nocap', 'rd', rl, rdc='', rdcmp=[])
r_, m_ = rowmap(d, 'rd')
check('rd no capture: made NO, read NO, letters NO', row(m_, '>= 1 capture made') == 'NO' and row(m_, 'every capture read') == 'NO'
      and row(m_, L1) == 'NO' and row(m_, LA) == 'NO')
d = make('rd_f10', 'rd', [FORK_FIX, STC_F10, 'GuestOut: boot'] + scene('rd', 120000000), rdc=RDC2, rdcmp=[GOOD, GOOD])
check('rd with _fixf10 dir line (=1 off): fixf19 NO', row(rowmap(d, 'rd')[1], 'translation cache directory') == 'NO')
d = make('rd_bin', 'rd', rl, sha_t=INSHA, rdc=RDC2, rdcmp=[GOOD, GOOD])
check('rd tag binary adb0c82f: NO', row(rowmap(d, 'rd')[1], 'binary sha256') == 'NO')
d = make('rd_death', 'rd', rl + ['ErrorDeviceLost'], rdc=RDC2, rdcmp=[GOOD, GOOD])
check('rd death: data row NO', row(rowmap(d, 'rd')[1], '0 death markers (data)') == 'NO')

# ---- real negative control: the F14c reads of the =0 captures (installed 540c035a / dac02fb9; F14c table) read as CODE_FAIL
for nm, recs in (('cmp_k03.txt', 18210), ('cmp_ef.txt', 584)):
    c = R.one_cmp('01', 'C:/kyty/f287/f14c/' + nm)
    check('F14c %s (=0): done, records %d = SUMMARY, A > 0, B 0, CODE_FAIL' % (nm, recs), c['done'] and c['records'] == recs and c['sum_ok']
          and c['A'] > 0 and c['B'] == 0 and c['letter'] == 'CODE_FAIL' and c['bad_agg'] == 0)

# ---- output: ASCII and strict cp1250 without PYTHONIOENCODING (non-ASCII bytes in the log)
d = make('enc', 'v1', ['Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19\\\u043a\u044d\u0448',
                       'Release, x, ver = 1, git = \u0432\u0435\u0440\u0441\u0438\u044f, date = y', 'GuestOut: boot'] + scene('v1', 330000000))
env = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
env['PYTHONIOENCODING'] = 'cp1250:strict'
p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'v1'], capture_output=True, env=env)
check('cp1250 strict: rc 0', p.returncode == 0)
check('cp1250 strict: stdout ASCII only', all(b < 128 for b in p.stdout))
check('cp1250 strict: rows printed', b'ROW hold >= 300 s' in p.stdout)
env2 = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
p2 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'v1'], capture_output=True, env=env2)
check('no PYTHONIOENCODING: rc 0, ASCII', p2.returncode == 0 and all(b < 128 for b in p2.stdout))
jp = os.path.join(TMP, 'out.json')
p3 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'v1', '--json', jp], capture_output=True, env=env2)
check('json written', p3.returncode == 0 and json.load(open(jp))['kind'] == 'v1')
p4 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'x'], capture_output=True, env=env2)
check('unknown kind refused', p4.returncode != 0)
d = make('enc_rd', 'rd', rl, rdc=RDC2, rdcmp=[GOOD, GOOD])
p5 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'rd'], capture_output=True, env=env)
check('rd cp1250 strict: rc 0, ASCII, rdcmp rows', p5.returncode == 0 and all(b < 128 for b in p5.stdout) and b'rdcmp k02 rdcmp_k02.txt' in p5.stdout)

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d fails %d' % (N, NF))
print('ALL OK' if OK else 'SOME FAILED')
