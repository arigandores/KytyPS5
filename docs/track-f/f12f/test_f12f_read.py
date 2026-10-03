"""Track F link F12f (HPP-480): fixtures of f12f_read.py - every row of the seal section 4 and every edge (port of FS4c
test_fs4c_read.py): the binary per kind (rd 540c035a, the others b714f5c4) and the installed before / after, the directory row
(_fixf10 in every line for v/w/vw/bh; rd control - no _fixf10, base dir; mixed lines; no line), hold 300 s / 300 s - 1 us,
3000 / 2999 video records, glitches, sheet, frames >= 1 s (report row only), process end, death markers, W rows ([Vulkan][E],
[Vulkan][W] = 0 / 1, DualSrcBlend before / after the first GuestOut), manifest EQUAL / DIFFER / missing for both compares,
interference (minimized, Recovering Vulkan swapchain, GamePatch), rd captures (RenderDoc lines, rdc_sha lines, rdcs summaries with /
without marks, a missing done line, count mismatch), revision text (never a gate), output in strict cp1250 without PYTHONIOENCODING.
The first output line names the suite and the target with their sha256; the last line is ALL OK.  ASCII only."""
import hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'f12f_read.py')
sys.path.insert(0, HERE)
import f12f_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f12f_read.py sha256 %s target f12f_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(TARGET)))
OK = True
N = 0
NF = 0
TMP = tempfile.mkdtemp(prefix='f12f_fx_')
FIXSHA = R.BIN_EXPECT
INSHA = R.WANT
STC_FIX = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10'
STC_BASE = 'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b'
ENTRY = {'rd': 'GuestOut: Level has started: underwater_aerial_garden', 'v': 'GuestOut: Level has started: underwater_aerial_garden',
         'w': 'GuestOut: Level has started: underwater_aerial_garden', 'vw': 'GuestOut: Level has started: voxel_world',
         'bh': 'GuestOut: Level has started: big_hand_pirate_island'}
DUAL = 'DualSrcBlend: supported=1 enabled=1'
COLD = 'cold form: C:/x/variant_fixb26_fixb1b_fixf10 absent at 2026-10-03T00:00:00Z; entries of _ShaderCache/PPSA21564: 2'
INST = 'installed form: variant_fixb26_fixb1b'
EQ = 'manifest cmp EQUAL files 3 listsha ab'
DIFF = 'manifest cmp DIFFER only_before 1 only_after 1'
FORK_FIX = 'Fork build arigandores/KytyPS5 1833ee2'
FORK_INST = 'Fork build arigandores/KytyPS5 4e72289'
ES_OK = {'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': None, 'hold_s': 330.1, 'stable_s': 40.0}]}
ES_EXIT = {'attempts': [{'outcome': 'exited', 'detail': 'exit code 5', 'hold_exit': None, 'hold_s': None, 'stable_s': None}]}
ES_HOLD_EXIT = {'attempts': [{'outcome': 'ok', 'detail': None, 'hold_exit': 5, 'hold_s': 50.0, 'stable_s': 40.0}]}
SUM_M = 'capture x\nDISPATCH eid=5 dims=1x1x1 cs_sha=aa bytes=4 mark=380b name=d\nSUMMARY dispatches 354 distinct_cs 53 marked_380b 2 marked_eids 5,9\ndone'
SUM_0 = 'capture x\nSUMMARY dispatches 354 distinct_cs 53 marked_380b 0 marked_eids -\ndone'
SUM_ND = 'capture x\nSUMMARY dispatches 354 distinct_cs 53 marked_380b 1 marked_eids 5'


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
         sha_t=None, before=INSHA, after=INSHA, cold=None, mcmp=EQ, mref=EQ, rdc=None, rdcs=None):
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
        sha_t = INSHA if kind == 'rd' else FIXSHA
    if cold is None:
        cold = INST if kind == 'rd' else COLD
    if kind not in R.VIDEO_KINDS:
        glitch = sheet = None
    files = (('glitch.txt', glitch), ('sheet.txt', sheet), ('installed_sha.txt', sha_t), ('installed_before.txt', before),
             ('installed_after.txt', after), ('cold.txt', cold), ('manifest_cmp.txt', mcmp), ('manifest_cmp_ref.txt', mref),
             ('rdc_sha.txt', rdc))
    for fn, t in files:
        if t is not None:
            with open(os.path.join(d, fn), 'wb') as f:
                f.write((t + '\n').encode('utf-8'))
    for i, t in enumerate(rdcs or [], 1):
        with open(os.path.join(d, 'rdcs_k%02d.txt' % i), 'wb') as f:
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
    global OK, N, NF
    N += 1
    if not cond:
        OK = False
        NF += 1
        print('FAIL %s' % name)


def row(rm, prefix):
    hits = [v for k, v in rm.items() if k.startswith(prefix)]
    return hits[0] if len(hits) == 1 else 'AMBIGUOUS %d' % len(hits)


# ---- kind_of, levels
for k in R.KINDS:
    check('kind %s' % k, R.kind_of('f12_' + k) == k)
for bad in ('f12_r1', 'fs4_v', 'f12_v2', 'f12_rdx', 'f13_rd'):
    try:
        R.kind_of(bad)
        check('kind %s raises' % bad, False)
    except SystemExit:
        check('kind %s raises' % bad, True)
check('levels', R.LEVEL['vw'] == 'voxel_world' and R.LEVEL['bh'] == 'big_hand_pirate_island'
      and all(R.LEVEL[k] == 'underwater_aerial_garden' for k in ('rd', 'v', 'w')))

# ---- V positive, per video kind
for k in ('v', 'vw', 'bh'):
    d = make('%s_pos' % k, k, [FORK_FIX, STC_FIX, 'GuestOut: boot'] + scene(k, 330000000))
    res, rm = rowmap(d, k)
    check('%s binary YES' % k, row(rm, 'binary sha256') == 'YES')
    check('%s before / after YES' % k, row(rm, 'installed 540c035a before') == 'YES' and row(rm, 'installed 540c035a after') == 'YES')
    check('%s revision YES' % k, row(rm, 'revision text') == 'YES')
    check('%s fixf10 YES' % k, row(rm, 'translation cache directory') == 'YES')
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
    check('%s has no rd rows' % k, not any(x.startswith('captures with') for x in rm))

# ---- V edges
vh = [FORK_FIX, STC_FIX, 'GuestOut: boot']
d = make('v_short', 'v', vh + scene('v', 300000000 - 1))
check('v hold 300 s - 1 us: NO', row(rowmap(d, 'v')[1], 'hold >= 300 s') == 'NO')
d = make('v_300', 'v', vh + scene('v', 300000000))
check('v hold 300 s: YES', row(rowmap(d, 'v')[1], 'hold >= 300 s') == 'YES')
d = make('v_2999', 'v', vh + scene('v', 330000000), idx=2999)
check('v video 2999: NO', row(rowmap(d, 'v')[1], 'video index records') == 'NO')
d = make('v_noidx', 'v', vh + scene('v', 330000000), idx=None)
check('v no video index: NO', row(rowmap(d, 'v')[1], 'video index records') == 'NO')
d = make('v_gl', 'v', vh + scene('v', 330000000), glitch='one-frame glitches: 1')
check('v 1 glitch: NO', row(rowmap(d, 'v')[1], '0 one-frame glitches') == 'NO')
d = make('v_glmiss', 'v', vh + scene('v', 330000000), glitch='nothing')
check('v glitch line missing: NOT_READ', row(rowmap(d, 'v')[1], '0 one-frame glitches') == 'NOT_READ')
d = make('v_nosheet', 'v', vh + scene('v', 330000000), sheet='error')
check('v no sheet line: NO', row(rowmap(d, 'v')[1], 'sheet for the lead') == 'NO')
d = make('v_k2', 'v', vh + scene('v', 330000000, k2=2))
r_, m_ = rowmap(d, 'v')
check('v 2 frames >= 1 s: report row NO with the count, hold still YES', row(m_, 'frames >= 1 s after the first scene frame = 2') == 'NO'
      and r_['k2_after'] == 2 and row(m_, 'hold >= 300 s') == 'YES')
d = make('v_999', 'v', vh + [ENTRY['v'], ft(1, 1, 50), ft(2, 1, 400), ft(3, 999999, 400)] + scene('v', 330000000)[3:])
check('v frame 999 999 us not counted', rowmap(d, 'v')[0]['k2_after'] == 0)
d = make('v_death', 'v', vh + scene('v', 330000000) + ['GpuHangAbort: x'])
check('v death: NO', row(rowmap(d, 'v')[1], '0 death markers') == 'NO')
d = make('v_death_so', 'v', vh + scene('v', 330000000), stdout='--- Fatal Error ---\n')
check('v death in stdout: NO', row(rowmap(d, 'v')[1], '0 death markers') == 'NO')
d = make('v_exit', 'v', vh + scene('v', 330000000), run=ES_HOLD_EXIT)
check('v hold_exit: no end NO', row(rowmap(d, 'v')[1], 'no process end') == 'NO')
d = make('v_exit2', 'v', vh + scene('v', 330000000), run=ES_EXIT)
check('v exited: no end NO', row(rowmap(d, 'v')[1], 'no process end') == 'NO')
d = make('v_norun', 'v', vh + scene('v', 330000000), run=None)
check('v no run json: NOT_READ', row(rowmap(d, 'v')[1], 'no process end') == 'NOT_READ')
d = make('v_noentry', 'v', vh + [ft(1, 400000000, 400)])
r_, m_ = rowmap(d, 'v')
check('v no entry: entered NO, hold NO, frames row NO', row(m_, 'entered') == 'NO' and row(m_, 'hold >= 300 s') == 'NO'
      and row(m_, 'frames >= 1 s after the first scene frame = 0') == 'NO')
d = make('v_wronglvl', 'vw', vh + scene('v', 330000000))
check('vw log of Sky Garden: entered NO', row(rowmap(d, 'vw')[1], 'entered') == 'NO')
d = make('v_change', 'v', vh + [ENTRY['v'], ft(1, 1, 50), ft(2, 1, 400), ft(3, 100000000, 400),
                                 'GuestOut: Level has started: other', ft(4, 400000000, 400)])
r_, m_ = rowmap(d, 'v')
check('v rows after a scene change not counted', r_['hold_us'] == 100000000 and row(m_, 'hold >= 300 s') == 'NO')
d = make('v_lowdraws', 'v', vh + [ENTRY['v']] + [ft(i, 100000, 99) for i in range(1, 4000)])
check('v draws 99 never a scene frame: hold 0', rowmap(d, 'v')[0]['hold_us'] == 0)
d = make('v_draws100', 'v', vh + [ENTRY['v'], ft(1, 5, 100)] + [ft(i, 100000, 100) for i in range(2, 3002)])
check('v draws 100 is the first scene frame (not counted)', rowmap(d, 'v')[0]['hold_us'] == 300000000)

# ---- directory row
d = make('v_nofix', 'v', [FORK_FIX, STC_BASE, 'GuestOut: boot'] + scene('v', 330000000))
check('v base dir: fixf10 NO', row(rowmap(d, 'v')[1], 'translation cache directory') == 'NO')
d = make('v_mixed', 'v', [FORK_FIX, STC_FIX, STC_BASE, 'GuestOut: boot'] + scene('v', 330000000))
check('v mixed dirs: fixf10 NO', row(rowmap(d, 'v')[1], 'translation cache directory') == 'NO')
d = make('v_nostc', 'v', [FORK_FIX, 'GuestOut: boot'] + scene('v', 330000000))
check('v no dir line: fixf10 NO', row(rowmap(d, 'v')[1], 'translation cache directory') == 'NO')
d = make('v_slash', 'v', [FORK_FIX, 'Shader translation cache: _ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10', 'GuestOut: b']
         + scene('v', 330000000))
check('v forward slashes: fixf10 YES', row(rowmap(d, 'v')[1], 'translation cache directory') == 'YES')
d = make('v_fixx', 'v', [FORK_FIX, STC_FIX + '_x', 'GuestOut: b'] + scene('v', 330000000))
check('v dir with a suffix after _fixf10: NO', row(rowmap(d, 'v')[1], 'translation cache directory') == 'NO')
d = make('v_warm', 'v', vh + scene('v', 330000000), cold='warm form: present')
check('v cold.txt without absent: cold NO', row(rowmap(d, 'v')[1], 'cold form') == 'NO')

# ---- binary rows
d = make('v_binbad', 'v', vh + scene('v', 330000000), sha_t=INSHA)
check('v tag binary 540c035a: NO', row(rowmap(d, 'v')[1], 'binary sha256') == 'NO')
d = make('v_bef', 'v', vh + scene('v', 330000000), before=FIXSHA)
check('v installed before not 540c035a: NO', row(rowmap(d, 'v')[1], 'installed 540c035a before') == 'NO')
d = make('v_aft', 'v', vh + scene('v', 330000000), after=None)
check('v installed after missing: NO', row(rowmap(d, 'v')[1], 'installed 540c035a after') == 'NO')
d = make('v_rev', 'v', [FORK_INST, STC_FIX, 'GuestOut: b'] + scene('v', 330000000))
r_, m_ = rowmap(d, 'v')
check('v revision of another build: NO (reference, other rows unchanged)', row(m_, 'revision text') == 'NO' and row(m_, 'hold >= 300 s') == 'YES')
d = make('v_norev', 'v', [STC_FIX, 'GuestOut: b'] + scene('v', 330000000))
check('v no revision text: NOT_PRESENT', row(rowmap(d, 'v')[1], 'revision text') == 'NOT_PRESENT')
d = make('v_gitrev', 'v', ['Release, clang, ver = 0.1, git = KytyPS5-x-g1833ee28, date = x', STC_FIX, 'GuestOut: b'] + scene('v', 330000000))
check('v git = revision text: YES', row(rowmap(d, 'v')[1], 'revision text') == 'YES')

# ---- manifest rows
d = make('v_mdiff', 'v', vh + scene('v', 330000000), mcmp=DIFF)
check('v manifest DIFFER: NO', row(rowmap(d, 'v')[1], 'manifest of the caches') == 'NO')
d = make('v_mrefdiff', 'v', vh + scene('v', 330000000), mref=DIFF)
r_, m_ = rowmap(d, 'v')
check('v manifest vs ref DIFFER: ref NO, own YES', row(m_, 'manifest after the return') == 'NO' and row(m_, 'manifest of the caches') == 'YES')
d = make('v_mmiss', 'v', vh + scene('v', 330000000), mcmp=None, mref=None)
r_, m_ = rowmap(d, 'v')
check('v manifests missing: both NO', row(m_, 'manifest after the return') == 'NO' and row(m_, 'manifest of the caches') == 'NO')

# ---- interference
for nm, extra in (('min', 'Window 1 minimized'), ('rec', 'Recovering Vulkan swapchain'), ('gp', 'GamePatch: loaded x')):
    d = make('v_int_' + nm, 'v', vh + scene('v', 330000000) + [extra])
    check('v interference %s: NO' % nm, row(rowmap(d, 'v')[1], 'no interference') == 'NO')
d = make('v_focus', 'v', vh + scene('v', 330000000) + ['Window 1 lost keyboard focus', 'Window 1 restored'])
r_, m_ = rowmap(d, 'v')
check('v focus / restored: data, interference YES', row(m_, 'no interference') == 'YES' and r_['win'] == {'lost keyboard focus': 1, 'restored': 1})

# ---- W
wl = [FORK_FIX, DUAL, STC_FIX, 'GuestOut: boot', '[Vulkan][W] x'] + scene('w', 310000000)
d = make('w_pos', 'w', wl)
res, rm = rowmap(d, 'w')
for nm in ('binary sha256', 'translation cache directory', 'entered', 'hold >= 300 s', '0 [Vulkan][E]', 'positive control',
           'DualSrcBlend', 'manifest of the caches', 'manifest after the return', 'no interference', '0 death markers (reference)'):
    check('w %s YES' % nm, row(rm, nm) == 'YES')
check('w has no video rows', not any(x.startswith('video index') for x in rm))
d = make('w_e', 'w', wl + ['[Vulkan][E] VUID-x'])
check('w 1 [Vulkan][E]: NO', row(rowmap(d, 'w')[1], '0 [Vulkan][E]') == 'NO')
d = make('w_now', 'w', [x for x in wl if not x.startswith('[Vulkan][W]')])
check('w 0 [Vulkan][W]: positive control NO', row(rowmap(d, 'w')[1], 'positive control') == 'NO')
d = make('w_dual_late', 'w', [FORK_FIX, STC_FIX, 'GuestOut: boot', DUAL, '[Vulkan][W] x'] + scene('w', 310000000))
check('w DualSrcBlend after the first GuestOut: NO', row(rowmap(d, 'w')[1], 'DualSrcBlend') == 'NO')
d = make('w_dual0', 'w', [FORK_FIX, 'DualSrcBlend: supported=1 enabled=0', STC_FIX, 'GuestOut: boot', '[Vulkan][W] x'] + scene('w', 310000000))
check('w DualSrcBlend enabled=0: NO', row(rowmap(d, 'w')[1], 'DualSrcBlend') == 'NO')
d = make('w_300', 'w', [FORK_FIX, DUAL, STC_FIX, 'GuestOut: boot', '[Vulkan][W] x'] + scene('w', 300000000))
check('w hold 300 s: YES', row(rowmap(d, 'w')[1], 'hold >= 300 s') == 'YES')
d = make('w_short', 'w', [FORK_FIX, DUAL, STC_FIX, 'GuestOut: boot', '[Vulkan][W] x'] + scene('w', 299999999))
check('w hold 300 s - 1 us: NO', row(rowmap(d, 'w')[1], 'hold >= 300 s') == 'NO')

# ---- RD
rl = [FORK_INST, STC_BASE, 'GuestOut: boot', 'RenderDoc: level started at frame 193, capture at frame 196 (+11 more)'] + scene('rd', 120000000)
rl += ['RenderDoc: auto capture at frame 196 (level+3)', 'RenderDoc: captured guest flip 2/2', 'RenderDoc: capture finished',
       'RenderDoc: auto capture at frame 199 (level+6)', 'RenderDoc: captured guest flip 2/2', 'RenderDoc: capture finished']
RDC2 = 'aa  f12_rd_k01.rdc\nbb  f12_rd_k02.rdc'
d = make('rd_pos', 'rd', rl, rdc=RDC2, rdcs=[SUM_0, SUM_M])
res, rm = rowmap(d, 'rd')
check('rd binary 540c035a YES', row(rm, 'binary sha256') == 'YES')
check('rd revision without 1833ee2 YES', row(rm, 'revision text') == 'YES')
check('rd control YES', row(rm, 'control: translation cache') == 'YES')
check('rd entered YES', row(rm, 'entered') == 'YES')
check('rd capture made YES', row(rm, '>= 1 capture made') == 'YES')
check('rd every capture read YES', row(rm, 'every capture read') == 'YES')
check('rd marked 1 of 2 YES', row(rm, 'captures with >= 1 dispatch of 380bb9d6 by SPIR-V sha (DATA for F12g, no gate): 1 of 2') == 'YES')
check('rd RenderDoc lines', res['rd_level'] == 193 and res['rd_auto'] == [(196, 3), (199, 6)] and res['rd_flip2'] == 2
      and res['rd_finished'] == 2 and res['rdc_n'] == 2)
check('rd rdcs parsed', res['rdcs'][1]['marked'] == 2 and res['rdcs'][1]['eids'] == '5,9' and res['rdcs'][0]['marked'] == 0)
check('rd has no hold / video / fixf10 rows', not any(x.startswith(('hold >=', 'video index', 'translation cache directory')) for x in rm))
check('rd interference none YES', row(rm, 'no interference') == 'YES')
d = make('rd_none', 'rd', rl, rdc=RDC2, rdcs=[SUM_0, SUM_0])
check('rd 0 marked: data row NO', row(rowmap(d, 'rd')[1], 'captures with >= 1 dispatch of 380bb9d6 by SPIR-V sha (DATA for F12g, no gate): 0 of 2') == 'NO')
d = make('rd_nodone', 'rd', rl, rdc=RDC2, rdcs=[SUM_0, SUM_ND])
check('rd rdcs without done: every capture read NO', row(rowmap(d, 'rd')[1], 'every capture read') == 'NO')
d = make('rd_count', 'rd', rl, rdc=RDC2, rdcs=[SUM_0])
check('rd 2 captures, 1 rdcs: every capture read NO', row(rowmap(d, 'rd')[1], 'every capture read') == 'NO')
d = make('rd_nocap', 'rd', rl, rdc='', rdcs=[])
r_, m_ = rowmap(d, 'rd')
check('rd no capture: made NO, read NO, data 0 of 0 NO', row(m_, '>= 1 capture made') == 'NO' and row(m_, 'every capture read') == 'NO'
      and row(m_, 'captures with >= 1 dispatch of 380bb9d6 by SPIR-V sha (DATA for F12g, no gate): 0 of 0') == 'NO')
d = make('rd_fix', 'rd', [FORK_INST, STC_FIX, 'GuestOut: boot'] + scene('rd', 120000000), rdc=RDC2, rdcs=[SUM_M, SUM_M])
check('rd with _fixf10 line: control NO', row(rowmap(d, 'rd')[1], 'control: translation cache') == 'NO')
d = make('rd_fixpath', 'rd', [FORK_INST, STC_BASE.replace('PPSA21564', 'PPSA21564_fixf10'), 'GuestOut: boot'] + scene('rd', 120000000),
         rdc=RDC2, rdcs=[SUM_M, SUM_M])
check('rd _fixf10 anywhere in the line, base dir at the end: control NO', row(rowmap(d, 'rd')[1], 'control: translation cache') == 'NO')
d = make('rd_bin', 'rd', rl, sha_t=FIXSHA, rdc=RDC2, rdcs=[SUM_M, SUM_M])
check('rd tag binary b714f5c4: NO', row(rowmap(d, 'rd')[1], 'binary sha256') == 'NO')
d = make('rd_rev', 'rd', [FORK_FIX] + rl[1:], rdc=RDC2, rdcs=[SUM_M, SUM_M])
check('rd revision 1833ee2: NO (reference)', row(rowmap(d, 'rd')[1], 'revision text') == 'NO')
d = make('rd_death', 'rd', rl + ['ErrorDeviceLost'], rdc=RDC2, rdcs=[SUM_M, SUM_M])
check('rd death: data row NO', row(rowmap(d, 'rd')[1], '0 death markers (data)') == 'NO')

# ---- output: ASCII and strict cp1250 without PYTHONIOENCODING (non-ASCII bytes in the log)
d = make('enc', 'v', ['Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10\\\u043a\u044d\u0448',
                      'Release, x, ver = 1, git = \u0432\u0435\u0440\u0441\u0438\u044f, date = y', 'GuestOut: boot'] + scene('v', 330000000))
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
d = make('enc_rd', 'rd', rl, rdc=RDC2, rdcs=[SUM_0, SUM_M])
p5 = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag-kind', 'rd'], capture_output=True, env=env)
check('rd cp1250 strict: rc 0, ASCII, rdcs rows', p5.returncode == 0 and all(b < 128 for b in p5.stdout) and b'rdcs rdcs_k02.txt' in p5.stdout)

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d fails %d' % (N, NF))
print('ALL OK' if OK else 'SOME FAILED')
