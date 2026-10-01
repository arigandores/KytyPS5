"""test_fs_read.py - fixtures of fs_read.py (FSc, HPP-370): every member of p.282(g)(3) (a)-(d) and p.281(g), every edge -
the positive control DualSrcBlend supported=1 enabled=1 before / after the first GuestOut and its values, the patched line of
5514 (anywhere, other hashes), the hold sum dt at 300 / 310 s and the wall hold at 330 s, video frames 2999 / 3000, glitches,
death markers (K1 / K2 kinds), frames >= 1 s (999 999 / 1 000 000), BvhLoopCapTrip on (b) and as an executor member elsewhere,
[Vulkan][E], validation active, layer limit lines, the W layer env (filter, duplicate limit), admission (binary, knobs,
KYTY_FIX_* absent / KYTY_FIX_B1B=0 exactly, other knobs, clock pin, checkpoints, precache, video, validation flag, attempts,
level), the knob control by the translation cache line, the window events, the scene change, the stop check (fs_a not PASS,
validation stop data), the series summary, the seal check, win_fs.decide, sheetpair positions, a real log (f4c_a: positive
control, patched before GuestOut, validation), and the ASCII output under a strict cp1250 console.  Last line: ALL OK."""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fs_read as R  # noqa: E402
import win_fs as W  # noqa: E402
import sheetpair_f3d as SP  # noqa: E402

FX = os.path.join(HERE, 'fx', 'read')
REAL = os.path.join(HERE, 'fx', 'real')
N = [0]
FAIL = []
SKYROWS = 18000       # 18000 * 16667 us = 300.006 s
MGGROWS = 18600       # 18600 * 16667 us = 310.006 s


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check(name, cond, detail=''):
    N[0] += 1
    if not cond:
        FAIL.append(name)
        print('FAIL %s %s' % (name, detail))


def write_run(root, tag, rows=None, dt=16667, k2=(), trips=0, death=False, hang=False, vke=0, glitches=0, vframes=8000,
              sheet=True, env_over=None, env_drop=(), wall=None, noval=False, tcache='auto', win=(), entered=True,
              scene_change=False, binary=None, cmd_val=None, limit=0, attempts=1, guest=None, dual='pre', patched=(),
              hold_exit=None, pre=('PipelinePrecache: no _ShaderCache/PPSA21564/variant_fixb26_fixb1b/pipelines.bin yet',)):
    cfg = R.TAGS[tag]
    w = cfg['arm'] == 'W'
    if rows is None:
        rows = MGGROWS if tag == 'fs_v' else SKYROWS + 100
    os.makedirs(root, exist_ok=True)
    L = []
    if tcache == 'auto':
        L.append('Shader translation cache: _ShaderCache\\PPSA21564\\%s' % R.CACHE_DIR[cfg['knob']])
    elif tcache is not None:
        for t in tcache:
            L.append('Shader translation cache: %s' % t)
    if w and not noval:
        L.append('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features')
        L.append('[Vulkan][I] layer active')
    if noval:
        L.append('no validation layer: VK_LAYER_KHRONOS_validation')
    duals = dual if isinstance(dual, (list, tuple)) else [dual]
    for dv in duals:
        if dv == 'pre':
            L.append('DualSrcBlend: supported=1 enabled=1')
        elif isinstance(dv, str) and dv.startswith('pre:'):
            L.append('DualSrcBlend: supported=%s' % dv[4:])
    for p in pre:
        L.append(p)
    for h, where in patched:
        if where == 'pre':
            L.append('DualSrcBlend: patched ps=%s' % h)
    L.append('GuestOut: boot line')
    for dv in duals:
        if dv == 'post':
            L.append('DualSrcBlend: supported=1 enabled=1')
    for _ in range(limit):
        L.append('[Vulkan][W] x. Limit of 1000000 reached, this will be the last time reporting it.')
    for x in win:
        L.append(x)
    if entered:
        L.append('GuestOut: Level has started: %s' % cfg['level'])
    for h, where in patched:
        if where == 'post':
            L.append('DualSrcBlend: patched ps=%s' % h)
    L.append('FrameTrace: n=0 dt_us=500000 draws=10')
    L.append('FrameTrace: n=1 dt_us=900000 draws=500')
    for i in range(rows):
        n = i + 2
        if i == 100:
            for _ in range(trips):
                L.append('BvhLoopCapTrip: trips=+131072 total=131072 near=+0 near_total=0 max_spent=4096 cap=4096 slot0=0 slot1=0')
        if scene_change and i == rows - 10:
            L.append('GuestOut: Level has started: other_level')
        d = k2[n] if isinstance(k2, dict) and n in k2 else (1500000 if (not isinstance(k2, dict) and n in k2) else dt)
        L.append('FrameTrace: n=%d dt_us=%d draws=500' % (n, d))
    for _ in range(vke):
        L.append('[Vulkan][E] validation error x')
    if death:
        L.append('Unhandled exception: access violation')
    if hang:
        L.append('GpuHangAbort: queue stuck')
    L.append('Event: quit')
    with open(os.path.join(root, 'log_%s.txt' % tag), 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    with open(os.path.join(root, 'stdout_%s.txt' % tag), 'w', encoding='ascii', newline='\n') as f:
        f.write('stdout\n')
    env = dict(KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GUEST_ARGS='-lvl %s' % cfg['level'])
    if cfg['knob'] is not None:
        env['KYTY_FIX_B1B'] = cfg['knob']
    if w:
        env['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
        env['VK_LAYER_DUPLICATE_MESSAGE_LIMIT'] = R.VKDUP
        env['VK_LAYER_MESSAGE_ID_FILTER'] = R.VKFILTER
    if cfg['video']:
        env['KYTY_REC'] = 'C:\\kyty\\f287\\fsc\\rec_%s.mp4' % tag
    env.update(env_over or {})
    for k in env_drop:
        env.pop(k, None)
    vv = w if cmd_val is None else cmd_val
    wl = wall if wall is not None else (330.0 if cfg['arm'] != 'W' else 310.0)
    js = dict(attempts=[dict(label='attempt %d' % (i + 1), hold_s=wl, outcome='ok', hold_exit=hold_exit) for i in range(attempts)],
              env=env, guest_args=guest or '-lvl %s' % cfg['level'],
              cmdline=['kyty_emulator.exe', '--vulkan-validation', 'true' if vv else 'false'],
              binary_sha256=binary or R.BIN_SHA)
    with open(os.path.join(root, '%s.json' % tag), 'w', encoding='ascii') as f:
        json.dump(js, f)
    if cfg['video'] and vframes is not None:
        with open(os.path.join(root, 'glitch_%s.txt' % tag), 'w', encoding='ascii') as f:
            f.write('rec_%s.mp4: %d frames 960x540\none-frame glitches: %d\n' % (tag, vframes, glitches))
    if cfg['video'] and sheet:
        open(os.path.join(root, 'sheetpair_%s.png' % tag), 'wb').write(b'PNG')


def rd(name, tag, **kw):
    root = os.path.join(FX, name)
    shutil.rmtree(root, ignore_errors=True)
    write_run(root, tag, **kw)
    return R.read_tag(tag, root, SC)


def rt(r):
    return json.loads(json.dumps(r, default=str))


SC = R.load()
P = R.PS1592
print('suite test_fs_read.py sha256 %s target fs_read.py sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                    sha(os.path.join(HERE, 'fs_read.py'))))
# --- constants of p.282(g)(3), p.286(v), p.273(k)(2) ---
check('binary = FSa copy dac02fb9 (p.286(v) N1)', R.BIN_SHA == 'dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e')
check('levels', R.TAGS['fs_a']['level'] == R.SKY == 'underwater_aerial_garden' and R.TAGS['fs_v']['level'] == R.MGG == 'mini_giants_garden'
      and R.TAGS['fs_b']['level'] == R.SKY and R.TAGS['fs_g']['level'] == R.MGG and R.TAGS['fs_d']['level'] == R.SKY)
check('holds: a 300 sum, b 300 sum, v 310 sum, g 330 wall, d 300 sum',
      [(R.TAGS[t]['hold_sum'], R.TAGS[t]['hold_wall']) for t in R.SEQ] == [(300, None), (300, None), (310, None), (None, 330), (300, None)])
check('arms W V W V I', [R.TAGS[t]['arm'] for t in R.SEQ] == ['W', 'V', 'W', 'V', 'I'])
check('knob only fs_d KYTY_FIX_B1B=0', [R.TAGS[t]['knob'] for t in R.SEQ] == [None, None, None, None, '0'])
check('video b and g', [R.TAGS[t]['video'] for t in R.SEQ] == [False, True, False, True, False])
check('references v142 and f4c_g', R.TAGS['fs_b']['ref'] == 'C:/kyty/s142/rec_v142.mp4' and R.TAGS['fs_g']['ref'] == 'C:/kyty/f287/f4c/rec_f4c_g.mp4')
check('F6 filter and duplicate limit as sc145', R.VKFILTER == 'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering' and R.VKDUP == '1000000')
check('frames 3000, ps 5514e10f1a60df83', R.FRAMES_V == 3000 and R.PS1592 == '5514e10f1a60df83')
check('series order a b v g d, gated a b v g', R.SEQ == ('fs_a', 'fs_b', 'fs_v', 'fs_g', 'fs_d') and R.GATED == ('fs_a', 'fs_b', 'fs_v', 'fs_g'))
# --- knob control ---
check('knob defaults variant_fixb26_fixb1b ok', R.knob_control(['_ShaderCache\\PPSA21564\\variant_fixb26_fixb1b'], None)[0])
check('knob defaults with variant_fixb26 INVALID', not R.knob_control(['_ShaderCache\\PPSA21564\\variant_fixb26'], None)[0])
check('knob =0 variant_fixb26 ok', R.knob_control(['_ShaderCache\\PPSA21564\\variant_fixb26'], '0')[0])
check('knob =0 root INVALID', not R.knob_control(['_ShaderCache\\PPSA21564'], '0')[0])
check('knob no line INVALID', not R.knob_control([], None)[0])
check('knob mixed lines INVALID', not R.knob_control(['_ShaderCache\\PPSA21564\\variant_fixb26_fixb1b', '_ShaderCache\\PPSA21564'], None)[0])
check('knob forward slashes ok', R.knob_control(['_ShaderCache/PPSA21564/variant_fixb26_fixb1b/'], None)[0])
check('knob longer name INVALID', not R.knob_control(['_ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_bdalean'], None)[0])
# --- (a) control W ---
r = rd('a_ok', 'fs_a')
check('a ideal PASS', r['verdict'] == 'PASS' and r['admitted'] and r['knob_ok'], (r['verdict'], r['why']))
check('a stop check continue', R.stop_check(rt(r)).startswith('continue: PASS'), R.stop_check(rt(r)))
r = rd('a_nodual', 'fs_a', dual=None)
check('a no DualSrcBlend line -> FAIL (p.281(g))', r['verdict'] == 'FAIL' and any('positive control' in x for x in r['why']), (r['verdict'], r['why']))
check('a FAIL -> stop of the series', R.stop_check(rt(r)).startswith('stop: control W fs_a FAIL'), R.stop_check(rt(r)))
r = rd('a_dualpost', 'fs_a', dual='post')
check('a DualSrcBlend line after the first GuestOut -> FAIL', r['verdict'] == 'FAIL' and r['dual_pre'] == 0, (r['verdict'], r['dual_pre']))
r = rd('a_dual10', 'fs_a', dual='pre:1 enabled=0')
check('a supported=1 enabled=0 -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('a_dual01', 'fs_a', dual='pre:0 enabled=1')
check('a supported=0 enabled=1 -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('a_dual2', 'fs_a', dual=['pre', 'pre'])
check('a two lines before GuestOut -> PASS by the letter, executor member FAILED', r['verdict'] == 'PASS'
      and ('exactly one DualSrcBlend: supported= line', False) in r['exec'], (r['verdict'], r['exec']))
r = rd('a_vke', 'fs_a', vke=1)
check('a one [Vulkan][E] -> FAIL and stop', r['verdict'] == 'FAIL' and R.stop_check(rt(r)).startswith('stop: control W'), (r['verdict'], r['why']))
r = rd('a_limit', 'fs_a', limit=1)
check('a one layer limit line -> FAIL', r['verdict'] == 'FAIL' and r['limit_lines'] == 1, (r['verdict'], r['why']))
r = rd('a_short', 'fs_a', rows=SKYROWS - 1)
check('a sum dt 299.99 s -> NOT EVALUABLE and stop', r['verdict'] == 'NOT EVALUABLE' and R.stop_check(rt(r)).startswith('stop: control W fs_a NOT EVALUABLE'),
      (r['verdict'], r['hold_sum_s']))
r = rd('a_edge', 'fs_a', rows=SKYROWS)
check('a sum dt 300.006 s -> PASS', r['verdict'] == 'PASS' and r['hold_sum_s'] >= 300, (r['verdict'], r['hold_sum_s']))
r = rd('a_noentry', 'fs_a', entered=False)
check('a not entered -> NOT EVALUABLE', r['verdict'] == 'NOT EVALUABLE', (r['verdict'], r['why']))
r = rd('a_noval', 'fs_a', noval=True)
check('a validation not active -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', (r['verdict'], r['why']))
r = rd('a_flag', 'fs_a', cmd_val=False)
check('a --vulkan-validation false -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('a_filter', 'fs_a', env_drop=('VK_LAYER_MESSAGE_ID_FILTER',))
check('a without the F6 filter -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('a_filter2', 'fs_a', env_over=dict(VK_LAYER_MESSAGE_ID_FILTER='other'))
check('a other filter -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('a_dup', 'fs_a', env_drop=('VK_LAYER_DUPLICATE_MESSAGE_LIMIT',))
check('a without the duplicate limit -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('a_pc', 'fs_a', env_over=dict(KYTY_PIPELINE_PRECACHE='0'))
check('a KYTY_PIPELINE_PRECACHE=0 -> NOT ADMITTED (precache by default, p.281(g))', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('a_death', 'fs_a', death=True)
check('a death marker: executor member, verdict PASS, stop (no [Vulkan][E])', r['verdict'] == 'PASS' and ('0 death markers (W)', False) in r['exec']
      and R.stop_check(rt(r)).startswith('stop: death'), (r['verdict'], R.stop_check(rt(r))))
r = rd('a_trip', 'fs_a', trips=1)
check('a BvhLoopCapTrip: executor member (reopens B1b), verdict PASS', r['verdict'] == 'PASS' and r['trips'] == 1
      and any(n.startswith('0 BvhLoopCapTrip') and not ok for n, ok in r['exec']), (r['verdict'], r['exec']))
r = rd('a_change', 'fs_a', scene_change=True)
check('a scene change: executor member; sum dt before the change', ('no scene change', False) in r['exec'], r['exec'])
r = rd('a_k2', 'fs_a', k2=(500,))
check('a frame >= 1 s: executor member only', r['verdict'] == 'PASS' and r['k2'] == 1, (r['verdict'], r['k2']))
r = rd('a_pre', 'fs_a', pre=('PipelinePrecache: stale recipes (signature mismatch), ignored', 'PipelinePrecache: 5 recipes -> 4 graphics + 1 compute pipelines queued'))
check('a precache lines printed, information', r['pre_count'] == 2 and 'stale recipes' in r['pre'][0] and r['verdict'] == 'PASS', r['pre'])
r = rd('a_hexit', 'fs_a', hold_exit=1)
check('a hold_exit not None: executor member', ('game alive at the end of the hold (hold_exit None)', False) in r['exec'], r['exec'])
# --- (b) V Sky Garden ---
r = rd('b_ok', 'fs_b')
check('b ideal PASS', r['verdict'] == 'PASS' and r['hold_sum_s'] >= 300, (r['verdict'], r['why'], r['hold_sum_s']))
r = rd('b_short', 'fs_b', rows=SKYROWS - 1)
check('b sum dt 299.99 s -> NOT EVALUABLE, continue', r['verdict'] == 'NOT EVALUABLE' and R.stop_check(rt(r)).startswith('continue: NOT EVALUABLE'),
      (r['verdict'], r['hold_sum_s']))
r = rd('b_edge', 'fs_b', rows=SKYROWS)
check('b sum dt 300.006 s -> PASS', r['verdict'] == 'PASS', (r['verdict'], r['hold_sum_s']))
r = rd('b_f2999', 'fs_b', vframes=2999)
check('b video 2999 frames -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('b_f3000', 'fs_b', vframes=3000)
check('b video 3000 frames -> PASS', r['verdict'] == 'PASS', (r['verdict'], r['why']))
r = rd('b_gl', 'fs_b', glitches=1)
check('b one glitch -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('b_nogl', 'fs_b', vframes=None)
check('b no glitch file -> FAIL', r['verdict'] == 'FAIL' and r['glitch'] is None, (r['verdict'], r['why']))
r = rd('b_death', 'fs_b', death=True)
check('b death marker (K1) -> FAIL and stop', r['verdict'] == 'FAIL' and r['marks'][0][1] == 'K1' and R.stop_check(rt(r)).startswith('stop: death'),
      (r['verdict'], r['marks']))
r = rd('b_hang', 'fs_b', hang=True)
check('b GpuHangAbort (K2 marker) -> FAIL', r['verdict'] == 'FAIL' and r['marks'][0][1] == 'K2', (r['verdict'], r['marks']))
r = rd('b_k2', 'fs_b', k2=(3000,))
check('b frame >= 1 s -> FAIL', r['verdict'] == 'FAIL' and r['k2'] == 1, (r['verdict'], r['why']))
r = rd('b_k2e', 'fs_b', k2={3000: 1000000})
check('b frame 1 000 000 us -> FAIL (edge >=)', r['verdict'] == 'FAIL' and r['k2'] == 1, (r['verdict'], r['k2']))
r = rd('b_k2n', 'fs_b', k2={3000: 999999})
check('b frame 999 999 us -> PASS', r['verdict'] == 'PASS' and r['k2'] == 0, (r['verdict'], r['k2']))
r = rd('b_trip', 'fs_b', trips=1)
check('b one BvhLoopCapTrip -> FAIL', r['verdict'] == 'FAIL' and r['trips'] == 1, (r['verdict'], r['why']))
r = rd('b_sheet', 'fs_b', sheet=False)
check('b without the pair sheet -> FAIL', r['verdict'] == 'FAIL' and r['sheet_name'] == 'sheetpair_fs_b.png', (r['verdict'], r['why']))
r = rd('b_mean', 'fs_b', rows=SKYROWS + 100, dt=20000)
check('b mean dt is a number', abs(r['mean_dt_us'] - 20000) < 1e-6 and r['verdict'] == 'PASS', r['mean_dt_us'])
r = rd('b_mean2', 'fs_b', rows=100, k2={50: 150000}, dt=20000)
check('b mean dt over the rows after the first scene frame', abs(r['mean_dt_us'] - (99 * 20000 + 150000) / 100.0) < 1e-6, r['mean_dt_us'])
r = rd('b_novid', 'fs_b', env_drop=('KYTY_REC',))
check('b no KYTY_REC -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('b_val', 'fs_b', cmd_val=True)
check('b with validation -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('b_filt', 'fs_b', env_over=dict(VK_LAYER_MESSAGE_ID_FILTER=R.VKFILTER))
check('b with the layer filter -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('b_short_gl', 'fs_b', rows=SKYROWS - 1, glitches=2)
check('b short hold with a glitch -> FAIL (FAIL before NOT EVALUABLE)', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
# --- (v) W mini_giants_garden ---
r = rd('v_ok', 'fs_v', patched=((P, 'post'),))
check('v ideal PASS (patched after GuestOut counts)', r['verdict'] == 'PASS' and r['patched_1592'] == 1 and r['patched_1592_pre'] == 0,
      (r['verdict'], r['why']))
r = rd('v_pre', 'fs_v', patched=((P, 'pre'),))
check('v patched before GuestOut counts', r['verdict'] == 'PASS' and r['patched_1592_pre'] == 1, (r['verdict'], r['why']))
r = rd('v_nopatch', 'fs_v')
check('v no patched line -> FAIL', r['verdict'] == 'FAIL' and any('patched' in x for x in r['why']), (r['verdict'], r['why']))
r = rd('v_other', 'fs_v', patched=(('0123456789abcdef', 'post'),))
check('v patched of another ps -> FAIL', r['verdict'] == 'FAIL' and r['patched_all'] == 1, (r['verdict'], r['why']))
r = rd('v_short', 'fs_v', rows=MGGROWS - 1, patched=((P, 'post'),))
check('v sum dt 309.99 s -> NOT EVALUABLE, variant 300 ok printed', r['verdict'] == 'NOT EVALUABLE'
      and ('sum dt >= 300 s (variant reading of "> = 310 s")', True) in r['exec'], (r['verdict'], r['hold_sum_s']))
check('v NOT EVALUABLE continues the series', R.stop_check(rt(r)).startswith('continue: NOT EVALUABLE'), R.stop_check(rt(r)))
r = rd('v_edge', 'fs_v', rows=MGGROWS, patched=((P, 'post'),))
check('v sum dt 310.006 s -> PASS', r['verdict'] == 'PASS', (r['verdict'], r['hold_sum_s']))
r = rd('v_v300', 'fs_v', rows=SKYROWS - 1, patched=((P, 'post'),))
check('v sum dt 299.99 s: variant member FAILED too', ('sum dt >= 300 s (variant reading of "> = 310 s")', False) in r['exec'], r['exec'])
r = rd('v_vke', 'fs_v', vke=1, death=True, patched=((P, 'post'),))
check('v [Vulkan][E] -> FAIL; validation stop is data: continue', r['verdict'] == 'FAIL'
      and R.stop_check(rt(r)).startswith('continue: validation'), (r['verdict'], R.stop_check(rt(r))))
r = rd('v_nodual', 'fs_v', dual=None, patched=((P, 'post'),))
check('v positive control missing -> FAIL (form (a))', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('v_limit', 'fs_v', limit=3, patched=((P, 'post'),))
check('v layer limit lines -> FAIL (form (a))', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('v_noval', 'fs_v', noval=True, patched=((P, 'post'),))
check('v validation not active -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
# --- (g) V mini_giants_garden ---
r = rd('g_ok', 'fs_g', wall=330.0)
check('g ideal PASS (wall 330.0)', r['verdict'] == 'PASS', (r['verdict'], r['why']))
r = rd('g_wall', 'fs_g', wall=329.9)
check('g wall 329.9 s -> NOT EVALUABLE', r['verdict'] == 'NOT EVALUABLE', (r['verdict'], r['why']))
r = rd('g_wallnone', 'fs_g', wall=None)
check('g default fixture wall 330 -> PASS', r['verdict'] == 'PASS', r['verdict'])
r = rd('g_sum', 'fs_g', rows=1000, wall=330.0)
check('g sum dt short but wall 330: PASS by the letter, executor member sum >= 330 FAILED', r['verdict'] == 'PASS'
      and ('sum dt after the first scene frame >= 330 s', False) in r['exec'], (r['verdict'], r['exec']))
r = rd('g_f2999', 'fs_g', vframes=2999)
check('g video 2999 -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('g_gl', 'fs_g', glitches=3)
check('g glitches -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('g_death', 'fs_g', death=True)
check('g death -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('g_k2', 'fs_g', k2=(4000,))
check('g frame >= 1 s: executor member, PASS', r['verdict'] == 'PASS' and r['k2'] == 1
      and ('0 frames >= 1 s after the first scene frame (K2)', False) in r['exec'], (r['verdict'], r['exec']))
r = rd('g_sheet', 'fs_g', sheet=False)
check('g no pair sheet -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('g_trip', 'fs_g', trips=2)
check('g BvhLoopCapTrip: executor member', r['verdict'] == 'PASS' and r['trips'] == 2, (r['verdict'], r['trips']))
# --- (d) information ---
r = rd('d_ok', 'fs_d')
check('d INFO', r['verdict'] == 'INFO' and r['mean_dt_us'] is not None, (r['verdict'], r['why']))
r = rd('d_short', 'fs_d', rows=SKYROWS - 1)
check('d sum dt 299.99 -> NOT EVALUABLE', r['verdict'] == 'NOT EVALUABLE', r['verdict'])
r = rd('d_death', 'fs_d', death=True, k2=(700,), trips=4)
check('d death / K2 / trips are information: INFO, stop on death', r['verdict'] == 'INFO' and R.stop_check(rt(r)).startswith('stop: death'),
      (r['verdict'], r['why']))
r = rd('d_knob1', 'fs_d', env_over=dict(KYTY_FIX_B1B='1'))
check('d KYTY_FIX_B1B=1 -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('d_knobnone', 'fs_d', env_drop=('KYTY_FIX_B1B',))
check('d KYTY_FIX_B1B unset -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('d_knobsp', 'fs_d', env_over=dict(KYTY_FIX_B1B='0 '))
check('d KYTY_FIX_B1B="0 " -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('d_cache', 'fs_d', tcache=['_ShaderCache\\PPSA21564\\variant_fixb26_fixb1b'])
check('d with variant_fixb26_fixb1b -> INVALID and stop', r['verdict'] == 'INVALID' and R.stop_check(rt(r)).startswith('stop: INVALID'), r['verdict'])
# --- admission at the defaults ---
for k in R.FIX_NAMES:
    r = rd('ad_%s' % k, 'fs_b', env_over={k: '1'})
    check('b with %s=1 set -> NOT ADMITTED (defaults)' % k, r['verdict'] == 'NOT ADMITTED', r['verdict'])
for k in R.OTHER_ABSENT:
    r = rd('ad_%s' % k, 'fs_a', env_over={k: '0'})
    check('a with %s set -> NOT ADMITTED' % k, r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_bin', 'fs_a', binary='2fc78597' + '0' * 56)
check('FSb rebuild sha -> NOT ADMITTED (p.286(v) N1)', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_pin', 'fs_b', env_drop=('KYTY_GPU_CLOCK_PIN',))
check('no clock pin -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_att', 'fs_b', attempts=2)
check('two attempts -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_guest', 'fs_g', guest='-lvl underwater_aerial_garden')
check('other level -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_rec_a', 'fs_a', env_over=dict(KYTY_REC='C:/x/rec_fs_a.mp4'))
check('W with video -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_rec_d', 'fs_d', env_over=dict(KYTY_REC='C:/x/rec_fs_d.mp4'))
check('d with video -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_rec_name', 'fs_b', env_over=dict(KYTY_REC='C:/x/rec_fs_g.mp4'))
check('b video of another tag -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_kn', 'fs_b', tcache=['_ShaderCache\\PPSA21564'])
check('b root cache line -> INVALID', r['verdict'] == 'INVALID', r['verdict'])
r = rd('ad_kn0', 'fs_b', tcache=None)
check('b no cache line -> INVALID', r['verdict'] == 'INVALID', r['verdict'])
# --- window events ---
r = rd('win_min', 'fs_b', win=('Window 1 minimized',))
check('minimized -> WINDOW EVENT, stop', r['verdict'] == 'WINDOW EVENT' and R.stop_check(rt(r)).startswith('stop: WINDOW EVENT'), r['verdict'])
r = rd('win_rec', 'fs_g', win=('Recovering Vulkan swapchain',))
check('Recovering Vulkan swapchain -> WINDOW EVENT', r['verdict'] == 'WINDOW EVENT', r['verdict'])
r = rd('win_other', 'fs_b', win=('Window 1 restored', 'Window 1 lost keyboard focus', 'Window 1 resized', 'Window 1 size changed'))
check('other window lines counted, not an event', r['verdict'] == 'PASS' and r['win']['restored'] == 1 and r['win']['lost keyboard focus'] == 1
      and r['win']['resized'] == 1 and r['win']['size changed'] == 1, (r['verdict'], r['win']))
r = rd('win_fail', 'fs_b', win=('Window 1 minimized',), glitches=4)
check('WINDOW EVENT before FAIL', r['verdict'] == 'WINDOW EVENT', r['verdict'])
# --- stop check ---
check('stop check: no reading', R.stop_check(None).startswith('stop: no reading'))
r = rd('st_na', 'fs_b', binary='x')
check('stop check: NOT ADMITTED -> stop', R.stop_check(rt(r)).startswith('stop: NOT ADMITTED'), R.stop_check(rt(r)))
r = rd('st_fail', 'fs_g', glitches=1)
check('stop check: FAIL of (g) is data -> continue', R.stop_check(rt(r)).startswith('continue: FAIL'), R.stop_check(rt(r)))
r = rd('st_a_na', 'fs_a', binary='x')
check('stop check: fs_a NOT ADMITTED -> stop', R.stop_check(rt(r)).startswith('stop: NOT ADMITTED'), R.stop_check(rt(r)))


# --- summary ---
def series(over=None, drop=()):
    root = os.path.join(FX, 'series')
    shutil.rmtree(root, ignore_errors=True)
    kw = {t: {} for t in R.SEQ}
    kw['fs_v']['patched'] = ((P, 'post'),)
    for t, k in (over or {}).items():
        kw[t].update(k)
    for t in R.SEQ:
        if t not in drop:
            write_run(root, t, **kw[t])
    reads = {t: R.read_tag(t, root, SC) for t in R.SEQ}
    return R.summary(reads)


txt, word = series()
check('summary all ideal -> PASS', word == 'PASS' and 'fs_d INFO' in txt, txt)
txt, word = series(over={'fs_g': dict(glitches=1)})
check('summary one FAIL -> FAIL', word == 'FAIL' and 'FAIL tags fs_g' in txt, txt)
txt, word = series(drop=('fs_g',))
check('summary missing gated tag -> NOT EVALUABLE', word == 'NOT EVALUABLE' and 'fs_g=NO READING' in txt, txt)
txt, word = series(drop=('fs_d',))
check('summary missing (d) does not change the verdict', word == 'PASS' and 'fs_d NO READING' in txt, txt)
txt, word = series(over={'fs_d': dict(rows=100)})
check('summary (d) NOT EVALUABLE does not change the verdict', word == 'PASS', txt)
txt, word = series(over={'fs_b': dict(rows=SKYROWS - 1)})
check('summary short hold -> NOT EVALUABLE', word == 'NOT EVALUABLE', txt)
txt, word = series(over={'fs_b': dict(rows=SKYROWS - 1), 'fs_v': dict(patched=())})
check('summary FAIL beats NOT EVALUABLE', word == 'FAIL', txt)
txt, word = series(over={'fs_a': dict(win=('Window 1 minimized',))})
check('summary window event -> NOT EVALUABLE', word == 'NOT EVALUABLE' and 'fs_a=WINDOW EVENT' in txt, txt)
# --- text output ---
r = rd('tx', 'fs_v', patched=((P, 'post'), ('0123456789abcdef', 'pre')), trips=1, k2=(900,))
t = R.text(r)
check('text patched line', 'DualSrcBlend patched lines 2; ps=5514e10f1a60df83 1 (before the first GuestOut 0)' in t, t)
check('text letter lines', 'letter p.282(g)(3)(v) ok   >= 1 line DualSrcBlend: patched ps=5514e10f1a60df83' in t, t)
check('text verdict and executor lines last', t.split('\n')[-2].startswith('FS VERDICT fs_v: PASS') and
      t.split('\n')[-1].startswith('FS EXECUTOR MEMBERS fs_v [I] (not the verdict): FAILED'), t.split('\n')[-2:])
check('text is ASCII', all(ord(c) < 128 for c in t))
# --- seal check ---
sroot = os.path.join(FX, 'seal')
shutil.rmtree(sroot, ignore_errors=True)
os.makedirs(sroot)
open(os.path.join(sroot, 'a.txt'), 'w').write('a')
sa = sha(os.path.join(sroot, 'a.txt'))
open(os.path.join(sroot, 'p.md'), 'w').write('x\nseal: %s a.txt\n' % sa)
check('seal ok', R.check_seal(os.path.join(sroot, 'p.md'), sroot, ('a.txt',))[0])
open(os.path.join(sroot, 'p.md'), 'w').write('seal: %s a.txt\n' % ('0' * 64))
check('seal mismatch', not R.check_seal(os.path.join(sroot, 'p.md'), sroot, ('a.txt',))[0])
open(os.path.join(sroot, 'p.md'), 'w').write('seal: %s a.txt\nseal: %s a.txt\n' % (sa, sa))
check('seal duplicate line', not R.check_seal(os.path.join(sroot, 'p.md'), sroot, ('a.txt',))[0])
open(os.path.join(sroot, 'p.md'), 'w').write('nothing\n')
check('seal missing line', not R.check_seal(os.path.join(sroot, 'p.md'), sroot, ('a.txt',))[0])
check('seal names cover the harness', set(('go_fs.sh', 'fs_read.py', 'win_fs.py', 'sheetpair_f3d.py', 'test_fs_read.py',
                                           'test_go_fs.py', 'recipes143.py', R.SC142)) <= set(R.SEALED))
# --- win_fs.decide ---
ok = {i: ('done', None) for i in W.NEED_DONE}
ok.update({i: ('blocked', None) for i in W.YIELD_TO})
check('win open', W.decide(ok) == (0, 'open'))
for i in W.YIELD_TO:
    for st in ('todo', 'in_progress'):
        s = dict(ok)
        s[i] = (st, None)
        check('win %s %s closed' % (i, st), W.decide(s) == (5, 'closed'))
    s = dict(ok)
    s[i] = ('blocked', 'run-1')
    check('win %s with a run closed' % i, W.decide(s) == (5, 'closed'))
    s = dict(ok)
    s[i] = ('done', None)
    check('win %s done open' % i, W.decide(s) == (0, 'open'))
for i in W.NEED_DONE:
    s = dict(ok)
    s[i] = ('in_review', None)
    check('win %s not done closed' % i, W.decide(s) == (5, 'closed'))
    s = dict(ok)
    s[i] = ('done', 'run-2')
    check('win %s done with a run closed' % i, W.decide(s) == (5, 'closed'))
s = dict(ok)
s['HPP-357'] = (None, None)
check('win no answer rc 6', W.decide(s) == (6, 'error'))
check('win names FSb done; F5c, session run step, P17 first', set(W.YIELD_TO) == {'HPP-357', 'HPP-352', 'HPP-364'} and
      set(W.NEED_DONE) == {'HPP-369'})
pw = subprocess.run([sys.executable, os.path.join(HERE, 'win_fs.py')], capture_output=True,
                    env={k: v for k, v in os.environ.items() if not k.startswith('PAPERCLIP_') and k != 'PYTHONIOENCODING'})
check('win without API env refuses rc 6, ASCII line (cp1250)', pw.returncode == 6 and pw.stdout.decode('cp1250').startswith('win_fs HPP-369 None'), pw)
# --- sheetpair positions ---
check('sheetpair positions: same index, min length', SP.positions(10567, 10078, 24) == (419, [k * 419 for k in range(24)]))
check('sheetpair positions: empty video', SP.positions(0, 100, 24) == (0, []))
check('sheetpair positions: short video', SP.positions(10, 12, 24) == (1, list(range(10))))
# --- real log: f4c_a (W Sky Garden, c9a5e198, KYTY_FIX_DUALSRC=1): positive control at line 76, patched 5514 at line 656
#     before the first GuestOut (p.281(a)); the binary / env / cache line differ from FSc -> admission and knob fail, the scan
#     members are the point ---
os.makedirs(REAL, exist_ok=True)
for kind in ('log_%s.txt', 'stdout_%s.txt'):
    dst = os.path.join(REAL, kind % 'fs_a')
    if not os.path.exists(dst):
        os.link('C:/kyty/f287/f4c/' + kind % 'f4c_a', dst)
js = json.load(open('C:/kyty/f287/f4c/f4c_a.json', encoding='utf-8'))
json.dump(js, open(os.path.join(REAL, 'fs_a.json'), 'w', encoding='ascii'))
r = R.read_tag('fs_a', REAL, SC)
check('real f4c_a: positive control before GuestOut (one line)', r['dual'] == [(1, 1)] and r['dual_pre'] == 1 and r['dual_ctl'], (r['dual'], r['dual_pre']))
check('real f4c_a: patched 5514 before GuestOut', r['patched_1592_pre'] >= 1, (r['patched_1592'], r['patched_1592_pre']))
check('real f4c_a: validation active, 0 [Vulkan][E], 0 limit lines', r['val']['ok'] and r['vke'] == 0 and r['limit_lines'] == 0,
      (r['val'], r['vke'], r['limit_lines']))
check('real f4c_a: sum dt 324.5 s (p.281(a))', abs(r['hold_sum_s'] - 324.5) < 0.1, r['hold_sum_s'])
check('real f4c_a: other binary and KYTY_FIX_DUALSRC=1 -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED'
      and any('dac02fb9' in w for w in r['why']) and any('KYTY_FIX_DUALSRC' in w for w in r['why']), r['why'])
check('real f4c_a: root cache line -> knob control fails', not r['knob_ok'], r['tcache'])
check('real f4c_a: precache line N recipes', any('recipes ->' in x for x in r['pre']), r['pre'])
# --- strict cp1250 console ---
root = os.path.join(FX, 'cp')
shutil.rmtree(root, ignore_errors=True)
write_run(root, 'fs_v', patched=((P, 'post'),))
env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
env['PYTHONIOENCODING'] = 'cp1250:strict'
p = subprocess.run([sys.executable, os.path.join(HERE, 'fs_read.py'), '--tag', 'fs_v', '--root', root], capture_output=True, env=env)
check('cp1250 strict: rc 0 and ASCII', p.returncode == 0 and all(b < 128 for b in p.stdout), p.stderr[-300:])
p = subprocess.run([sys.executable, os.path.join(HERE, 'fs_read.py'), '--summary', '--root', root], capture_output=True, env=env)
check('cp1250 strict: summary rc 0', p.returncode == 0 and b'FS SERIES VERDICT' in p.stdout, p.stderr[-300:])
p = subprocess.run([sys.executable, os.path.join(HERE, 'fs_read.py'), '--tag', 'fs_zz'], capture_output=True, env=env)
check('usage rc 2', p.returncode == 2, p.stdout)
p = subprocess.run([sys.executable, os.path.join(HERE, 'fs_read.py'), '--tag', 'fs_a', '--root', root], capture_output=True, env=env)
check('no log rc 1', p.returncode == 1, p.stdout)
jp = os.path.join(root, 'v.read.json')
p = subprocess.run([sys.executable, os.path.join(HERE, 'fs_read.py'), '--tag', 'fs_v', '--root', root, '--json', jp], capture_output=True, env=env)
p2 = subprocess.run([sys.executable, os.path.join(HERE, 'fs_read.py'), '--stop-check', jp], capture_output=True, env=env)
check('json round trip -> stop check continue: PASS', p.returncode == 0 and p2.stdout.startswith(b'continue: PASS'), p2.stdout)
shutil.rmtree(FX, ignore_errors=True)
print('checks %d failed %d' % (N[0], len(FAIL)))
print('ALL OK' if not FAIL else 'SOME FAILED: %s' % FAIL)
sys.exit(0 if not FAIL else 1)
