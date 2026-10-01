"""test_f3d_read.py - fixtures of f3d_read.py (F3d, HPP-342): every member of p.259(e)(4)-(6) and of p.277(b) and every edge -
pairs, low pages, the 4 GiB edge, the page mask, BvhLoopCapTrip, death markers, K2, the hold (sum dt_us after the first scene
frame) at the named edge, K3 hold frames and the entry window edge, mean dt, video / glitch / sheet, the W form and the
validation, the knob control, the admission, the window events, the stop check, the series summary and (6), the seal check,
win_f3d.decide, sheetpair positions, two real s142 logs (hard links in fx/real; the independent F3a scan12 numbers), and the
ASCII output under a strict cp1250 console.  Last line: ALL OK."""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f3d_read as R  # noqa: E402
import win_f3d as W  # noqa: E402
import sheetpair_f3d as SP  # noqa: E402

FX = os.path.join(HERE, 'fx', 'read')
REAL = os.path.join(HERE, 'fx', 'real')
N = [0]
FAIL = []


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check(name, cond, detail=''):
    N[0] += 1
    if not cond:
        FAIL.append(name)
        print('FAIL %s %s' % (name, detail))


def write_run(root, tag, fix=None, rows=7300, dt=16667, k3=(), k2=(), faults=(), trips=0, death=False, hang=False, vke=0,
              glitches=0, vframes=8000, sheet=True, env_over=None, env_drop=(), hold_s=None, noval=False, tcache='auto',
              win=(), entered=True, scene_change=False, binary=None, cmd_val=None, limit=0, attempts=1, guest=None):
    cfg = R.TAGS[tag]
    fix = cfg['fix'] if fix is None else fix
    os.makedirs(root, exist_ok=True)
    L = []
    if tcache == 'auto':
        L.append('Shader translation cache: _ShaderCache\\PPSA21564\\%s' % R.CACHE_DIR[fix])
    elif tcache is not None:
        for t in tcache:
            L.append('Shader translation cache: %s' % t)
    if cfg['val'] and not noval:
        L.append('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features')
        L.append('[Vulkan][I] layer active')
    if noval:
        L.append('no validation layer: VK_LAYER_KHRONOS_validation')
    for _ in range(limit):
        L.append('[Vulkan][W] x. Limit of 1000000 reached, this will be the last time reporting it.')
    for w in win:
        L.append(w)
    if entered:
        L.append('GuestOut: Level has started: %s' % cfg['level'])
    L.append('FrameTrace: n=0 dt_us=500000 draws=10')
    L.append('FrameTrace: n=1 dt_us=900000 draws=500')
    fl = list(faults)
    for i in range(rows):
        n = i + 2
        if i == 100:
            for a in fl:
                L.append('Accessed non-GPU cached memory at 0x%016x' % a)
            for _ in range(trips):
                L.append('BvhLoopCapTrip: trips=+131072 total=131072 near=+0 near_total=0 max_spent=4096 cap=4096 slot0=0 slot1=0')
        if scene_change and i == rows - 10:
            L.append('GuestOut: Level has started: other_level')
        d = 1500000 if n in k2 else (150000 if n in k3 else dt)
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
    env = dict(KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_FIX_B1B=fix)
    if cfg['val']:
        env['KYTY_PIPELINE_PRECACHE'] = '0'
        env['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
    if cfg['video']:
        env['KYTY_REC'] = 'C:\\kyty\\f287\\f3d\\rec_%s.mp4' % tag
    env.update(env_over or {})
    for k in env_drop:
        env.pop(k, None)
    vv = cfg['val'] if cmd_val is None else cmd_val
    js = dict(attempts=[dict(label='attempt %d' % (i + 1), hold_s=hold_s or cfg['hold_s'] or 120, outcome='ok', hold_exit=None)
                        for i in range(attempts)],
              env=env, guest_args=guest or '-lvl %s' % cfg['level'],
              cmdline=['kyty_emulator.exe', '--vulkan-validation', 'true' if vv else 'false'],
              binary_sha256=binary or R.BIN_SHA)
    with open(os.path.join(root, '%s.json' % tag), 'w', encoding='ascii') as f:
        json.dump(js, f)
    if cfg['video'] and vframes is not None:
        with open(os.path.join(root, 'glitch_%s.txt' % tag), 'w', encoding='ascii') as f:
            f.write('rec_%s.mp4: %d frames 960x540\none-frame glitches: %d\n' % (tag, vframes, glitches))
    sn = 'sheetpair_%s.png' % tag if cfg['kind'] == 'skyv' else 'sheet_%s.png' % tag
    if cfg['video'] and sheet:
        open(os.path.join(root, sn), 'wb').write(b'PNG')


def rd(name, tag, **kw):
    root = os.path.join(FX, name)
    shutil.rmtree(root, ignore_errors=True)
    write_run(root, tag, **kw)
    return R.read_tag(tag, root, SC)


SC = R.load()
X1 = 0x401bc0000            # voxel_world X1 of F3a (page (X1 >> 8) & ~0x3fff = 0x4018000)
P1 = (X1 >> 8) & ~0x3fff
X2 = 0x40253c000
P2 = (X2 >> 8) & ~0x3fff
print('suite test_f3d_read.py sha256 %s target f3d_read.py sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                      sha(os.path.join(HERE, 'f3d_read.py'))))
# --- fault members (p.259(e)(4)) ---
check('page mask of X1 = 0x4018000 (F3a)', P1 == 0x4018000, hex(P1))
check('page mask of X2 = 0x4024000 (F3a)', P2 == 0x4024000, hex(P2))
pages, pairs, lows = R.fault_members([(X1, 0), (P1, 1)])
check('pair X1 / page counted', pairs == [(X1, P1)] and lows == [P1], (pairs, lows))
pages, pairs, lows = R.fault_members([(X1, 0)])
check('X alone: no pair', pairs == [] and lows == [], (pairs, lows))
pages, pairs, lows = R.fault_members([(P1, 0)])
check('page alone: no pair, one low', pairs == [] and lows == [P1], (pairs, lows))
pages, pairs, lows = R.fault_members([(X1, 0), (P1, 1), (X1, 2), (P1, 3)])
check('repeated lines: distinct pages', pairs == [(X1, P1)] and len(pages) == 2, (pairs, pages))
pages, pairs, lows = R.fault_members([(X1, 0), (P1 + 0x4000, 1)])
check('neighbour page is not the pair page', pairs == [], pairs)
pages, pairs, lows = R.fault_members([(0x100000000, 0), (0x1000000, 1)])
check('X = 4 GiB exactly is >= 4 GiB (pair with 0x1000000)', pairs == [(0x100000000, 0x1000000)], pairs)
pages, pairs, lows = R.fault_members([(0xffffc000, 0), (0xffffc0 & ~0x3fff, 1)])
check('X just below 4 GiB is low, not a pair', pairs == [] and lows == [0xffc000, 0xffffc000], (pairs, [hex(a) for a in lows]))
pages, pairs, lows = R.fault_members([(X1, 0), (P1, 1), (X2, 2), (P2, 3), (0xc019a4000, 4), (0xda98000, 5)])
check('two pairs, three lows', pairs == [(X1, P1), (X2, P2)] and lows == [P1, P2, 0xda98000], (pairs, lows))
# --- knob control (p.277(b)(1)) ---
check('knob =1 variant_fixb26_fixb1b ok', R.knob_control(['_ShaderCache\\PPSA21564\\variant_fixb26_fixb1b'], '1')[0])
check('knob =1 with variant_fixb26 INVALID', not R.knob_control(['_ShaderCache\\PPSA21564\\variant_fixb26'], '1')[0])
check('knob =0 variant_fixb26 ok', R.knob_control(['_ShaderCache\\PPSA21564\\variant_fixb26'], '0')[0])
check('knob =0 root INVALID', not R.knob_control(['_ShaderCache\\PPSA21564'], '0')[0])
check('knob no line INVALID', not R.knob_control([], '1')[0])
check('knob mixed lines INVALID', not R.knob_control(['_ShaderCache\\PPSA21564\\variant_fixb26_fixb1b', '_ShaderCache\\PPSA21564'], '1')[0])
check('knob forward slashes ok', R.knob_control(['_ShaderCache/PPSA21564/variant_fixb26_fixb1b/'], '1')[0])
check('knob longer name INVALID', not R.knob_control(['_ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_x'], '1')[0])
# --- cold =1 ---
r = rd('a1_ok', 'f3d_a1')
check('a1 ideal PASS', r['verdict'] == 'PASS' and r['admitted'] and r['knob_ok'], (r['verdict'], r['why']))
check('a1 ideal zero members', r['pairs'] == [] and r['lows'] == [] and r['trips'] == 0 and r['deaths'] == 0 and r['k2'] == 0)
r = rd('a1_pair', 'f3d_a1', faults=(X1, P1))
check('a1 pair -> FAIL', r['verdict'] == 'FAIL' and any('pairs 1' in w for w in r['why']), (r['verdict'], r['why']))
r = rd('a1_trip', 'f3d_a1', trips=1)
check('a1 one BvhLoopCapTrip -> FAIL', r['verdict'] == 'FAIL' and r['trips'] == 1, (r['verdict'], r['why']))
r = rd('a1_low', 'f3d_a1', faults=(0xda98000,))
check('a1 low page -> PASS EXCEPT LOW with the address', r['verdict'] == 'PASS EXCEPT LOW' and '0xda98000' in ' '.join(r['why']),
      (r['verdict'], r['why']))
r = rd('a1_high', 'f3d_a1', faults=(0xc019a4000,))
check('a1 high page alone -> PASS', r['verdict'] == 'PASS', (r['verdict'], r['why']))
r = rd('a1_death', 'f3d_a1', death=True)
check('a1 death -> FAIL', r['verdict'] == 'FAIL' and r['deaths'] == 1, (r['verdict'], r['why']))
check('a1 death -> stop', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('stop: death'), R.stop_check(r))
r = rd('a1_hang', 'f3d_a1', hang=True)
check('a1 GpuHangAbort (K2 marker) -> FAIL', r['verdict'] == 'FAIL' and r['marks'][0][1] == 'K2', (r['verdict'], r['marks']))
r = rd('a1_k2', 'f3d_a1', k2=(50,))
check('a1 K2 frame in the entry window -> FAIL', r['verdict'] == 'FAIL' and r['k2'] == 1, (r['verdict'], r['why']))
r = rd('a1_k2b', 'f3d_a1', k2=(3000,))
check('a1 K2 frame in the hold -> FAIL', r['verdict'] == 'FAIL' and r['k2'] == 1, (r['verdict'], r['why']))
r = rd('a1_k2edge', 'f3d_a1', dt=999999, rows=200, k3=())
check('a1 dt 999 999 is not K2', r['k2'] == 0, r['k2'])
r = rd('a1_short', 'f3d_a1', rows=600)
check('a1 cold: hold not named -> PASS with 10 s', r['verdict'] == 'PASS' and r['hold_s'] < 20, (r['verdict'], r['hold_s']))
r = rd('a1_noentry', 'f3d_a1', entered=False)
check('a1 not entered -> NOT EVALUABLE', r['verdict'] == 'NOT EVALUABLE', (r['verdict'], r['why']))
r = rd('a1_noentry_pair', 'f3d_a1', entered=False, faults=(X1, P1))
check('a1 not entered with a pair -> FAIL (pair counts on every log)', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('a1_change', 'f3d_a1', scene_change=True)
check('a1 scene change -> FAIL', r['verdict'] == 'FAIL' and r['scene_change'], (r['verdict'], r['why']))
# --- warm =1 ---
r = rd('a2_ok', 'f3d_a2')
check('a2 ideal PASS', r['verdict'] == 'PASS', (r['verdict'], r['why']))
r = rd('a2_edge_ok', 'f3d_a2', rows=7200)
check('a2 hold 120.0024 s -> PASS', r['verdict'] == 'PASS' and r['hold_s'] >= 120, (r['verdict'], r['hold_s']))
r = rd('a2_edge_short', 'f3d_a2', rows=7199)
check('a2 hold 119.985 s -> NOT EVALUABLE', r['verdict'] == 'NOT EVALUABLE', (r['verdict'], r['hold_s']))
r = rd('a2_short_pair', 'f3d_a2', rows=7199, faults=(X1, P1))
check('a2 short hold with a pair -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('a2_glitch', 'f3d_a2', glitches=1)
check('a2 one glitch -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('a2_noglitch', 'f3d_a2', vframes=None)
check('a2 no glitch file -> FAIL', r['verdict'] == 'FAIL' and 'no glitch reading' in r['why'], (r['verdict'], r['why']))
r = rd('a2_nosheet', 'f3d_a2', sheet=False)
check('a2 no sheet -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('a2_novideo', 'f3d_a2', env_drop=('KYTY_REC',))
check('a2 no KYTY_REC -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', (r['verdict'], r['why']))
r = rd('a2_k3', 'f3d_a2', k3=(300, 600, 601, 5000))
hf = r['hold_frames']
check('a2 K3: rows 601 and 5000 are hold frames, 300 and 600 in the window', [x['n'] for x in hf] == [601, 5000] and r['k3_window'] == 2,
      (hf, r['k3_window']))
check('a2 K3 is information: PASS', r['verdict'] == 'PASS', r['verdict'])
check('a2 K3 interval from the row before', hf[0]['lo'] < hf[0]['hi'], hf[0])
r = rd('a2_mean', 'f3d_a2', rows=100, dt=20000, k3=(50,))
check('a2 mean dt over the rows after the first scene frame', abs(r['mean_dt_us'] - (99 * 20000 + 150000) / 100.0) < 1e-6, r['mean_dt_us'])
# --- admission (p.277(b)(3)-(4)) ---
r = rd('ad_b1b_true', 'f3d_a2', env_over=dict(KYTY_FIX_B1B='true'))
check('B1B=true -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_b1b_sp', 'f3d_a2', env_over=dict(KYTY_FIX_B1B='1 '))
check('B1B="1 " -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_b1b_none', 'f3d_a1', env_drop=('KYTY_FIX_B1B',))
check('B1B unset -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_b1b_wrong', 'f3d_c1', env_over=dict(KYTY_FIX_B1B='1'))
check('control with B1B=1 -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_b26', 'f3d_a1', env_over=dict(KYTY_FIX_B26='1'))
check('KYTY_FIX_B26 set -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_bin', 'f3d_a1', binary='5821482a13a38bb9e42719b75fbd7b6e308a08c8e98caab02afb5398aac368dd')
check('other binary -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_pin', 'f3d_a1', env_drop=('KYTY_GPU_CLOCK_PIN',))
check('no clock pin -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_ckpt', 'f3d_a1', env_over=dict(KYTY_GPU_CHECKPOINTS='0'))
check('KYTY_GPU_CHECKPOINTS present (any value) -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_pc_v', 'f3d_bv', env_over=dict(KYTY_PIPELINE_PRECACHE='0'))
check('V with PRECACHE=0 -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_att', 'f3d_a1', attempts=2)
check('two attempts -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_guest', 'f3d_a1', guest='-lvl voxel_world')
check('other level -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_val_v', 'f3d_a1', cmd_val=True)
check('V with validation -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('ad_rec_c', 'f3d_c1', env_over=dict(KYTY_REC='C:/x/rec_f3d_c1.mp4'))
check('control with video -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
# --- knob control in a run ---
r = rd('kn_wrong', 'f3d_a1', tcache=['_ShaderCache\\PPSA21564\\variant_fixb26'])
check('=1 run with variant_fixb26 -> INVALID', r['verdict'] == 'INVALID', (r['verdict'], r['why']))
check('INVALID -> stop', R.stop_check(r).startswith('stop: INVALID'), R.stop_check(r))
r = rd('kn_none', 'f3d_c1', tcache=None)
check('no cache line -> INVALID', r['verdict'] == 'INVALID', r['verdict'])
r = rd('kn_c_ok', 'f3d_c1', faults=(X1, P1))
check('control knob ok and pair -> CONTROL RETURNS', r['verdict'] == 'CONTROL RETURNS', (r['verdict'], r['why']))
# --- window events (item 273 (z)) ---
r = rd('win_min', 'f3d_a1', win=('Window 1 minimized',))
check('minimized -> WINDOW EVENT', r['verdict'] == 'WINDOW EVENT' and r['win']['minimized'] == 1, (r['verdict'], r['win']))
check('WINDOW EVENT -> stop', R.stop_check(r).startswith('stop: WINDOW EVENT'), R.stop_check(r))
r = rd('win_rec', 'f3d_a1', win=('Recovering Vulkan swapchain',))
check('Recovering Vulkan swapchain -> WINDOW EVENT', r['verdict'] == 'WINDOW EVENT', r['verdict'])
r = rd('win_other', 'f3d_a1', win=('Window 1 restored', 'Window 1 lost keyboard focus', 'Window 1 resized', 'Window 1 size changed'))
check('other window lines counted, not an event', r['verdict'] == 'PASS' and r['win']['restored'] == 1 and
      r['win']['lost keyboard focus'] == 1 and r['win']['resized'] == 1 and r['win']['size changed'] == 1, (r['verdict'], r['win']))
# --- Sky Garden V ---
r = rd('bv_ok', 'f3d_bv', rows=18100)
check('bv ideal PASS', r['verdict'] == 'PASS' and r['hold_s'] >= 300, (r['verdict'], r['why'], r['hold_s']))
r = rd('bv_short', 'f3d_bv', rows=17999)
check('bv hold 299.98 s -> NOT EVALUABLE', r['verdict'] == 'NOT EVALUABLE', (r['verdict'], r['hold_s']))
r = rd('bv_edge', 'f3d_bv', rows=18000)
check('bv hold 300.006 s -> PASS', r['verdict'] == 'PASS', (r['verdict'], r['hold_s']))
r = rd('bv_frames', 'f3d_bv', rows=18100, vframes=2999)
check('bv video 2999 frames -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('bv_frames3000', 'f3d_bv', rows=18100, vframes=3000)
check('bv video 3000 frames -> PASS', r['verdict'] == 'PASS', (r['verdict'], r['why']))
r = rd('bv_sheet', 'f3d_bv', rows=18100, sheet=False)
check('bv without the pair sheet -> FAIL', r['verdict'] == 'FAIL' and r['sheet_name'] == 'sheetpair_f3d_bv.png', (r['verdict'], r['why']))
r = rd('bv_mean', 'f3d_bv', rows=18100, dt=16667)
check('bv mean dt is a number, not a gate', abs(r['mean_dt_us'] - 16667) < 1e-6 and r['verdict'] == 'PASS', r['mean_dt_us'])
# --- Sky Garden W ---
r = rd('bw_ok', 'f3d_bw', rows=18100)
check('bw ideal PASS', r['verdict'] == 'PASS', (r['verdict'], r['why']))
r = rd('bw_vke', 'f3d_bw', rows=18100, vke=1)
check('bw one [Vulkan][E] -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('bw_noval', 'f3d_bw', rows=18100, noval=True)
check('bw validation not active -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', (r['verdict'], r['why']))
r = rd('bw_pc', 'f3d_bw', rows=18100, env_drop=('KYTY_PIPELINE_PRECACHE',))
check('bw without PRECACHE=0 -> NOT ADMITTED (p.254(e))', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('bw_flag', 'f3d_bw', rows=18100, cmd_val=False)
check('bw --vulkan-validation false -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
r = rd('bw_short', 'f3d_bw', rows=17999)
check('bw hold 299.98 s -> NOT EVALUABLE', r['verdict'] == 'NOT EVALUABLE', r['verdict'])
r = rd('bw_limit', 'f3d_bw', rows=18100, limit=2)
check('bw layer limit lines counted, member [I], PASS', r['limit_lines'] == 2 and r['verdict'] == 'PASS', (r['limit_lines'], r['verdict']))
# --- controls =0 ---
r = rd('c1_nopair', 'f3d_c1')
check('control without a pair -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('c1_ok', 'f3d_c1', faults=(X2, P2), trips=6, k3=(700,))
check('control pair -> CONTROL RETURNS, trips and K3 information', r['verdict'] == 'CONTROL RETURNS' and r['trips'] == 6 and
      len(r['hold_frames']) == 1, (r['verdict'], r['why']))
r = rd('c1_short', 'f3d_c1', rows=7199, faults=(X2, P2))
check('control hold 119.985 s -> NOT EVALUABLE', r['verdict'] == 'NOT EVALUABLE', r['verdict'])
r = rd('c1_k2', 'f3d_c1', faults=(X2, P2), k2=(800,))
check('control K2 frame is information', r['verdict'] == 'CONTROL RETURNS' and r['k2'] == 1, r['verdict'])
r = rd('c1_death', 'f3d_c1', faults=(X2, P2), death=True)
check('control death -> FAIL and stop', r['verdict'] == 'FAIL' and R.stop_check(r).startswith('stop: death'), (r['verdict'], R.stop_check(r)))
# --- stop check ---
check('stop check: no reading', R.stop_check(None).startswith('stop: no reading'))
r = rd('st_fail', 'f3d_a1', faults=(X1, P1))
check('stop check: a FAIL member is data -> continue', R.stop_check(r).startswith('continue: FAIL'), R.stop_check(r))
r = rd('st_na', 'f3d_a1', binary='x')
check('stop check: NOT ADMITTED -> stop', R.stop_check(r).startswith('stop: NOT ADMITTED'), R.stop_check(r))
r = rd('st_ne', 'f3d_a2', rows=7199)
check('stop check: NOT EVALUABLE -> continue', R.stop_check(r).startswith('continue: NOT EVALUABLE'), R.stop_check(r))
# --- summary and (6) ---


def series(over=None, drop=()):
    root = os.path.join(FX, 'series')
    shutil.rmtree(root, ignore_errors=True)
    kw = {t: dict(rows=18100 if R.TAGS[t]['kind'] in ('skyv', 'skyw') else 7300) for t in R.SEQ}
    for t in ('f3d_c1', 'f3d_c2'):
        kw[t]['faults'] = (X2, P2)
    for t, k in (over or {}).items():
        kw[t].update(k)
    for t in R.SEQ:
        if t not in drop:
            write_run(root, t, **kw[t])
    reads = {t: R.read_tag(t, root, SC) for t in R.SEQ}
    return R.summary(reads)


txt, word = series()
check('summary all ideal -> PASS', word == 'PASS', txt)
check('summary (6) 4 of 4 without a trip', '(6) =1 entries of (a) without a BvhLoopCapTrip line: 4 of 4' in txt, txt)
txt, word = series(over={'f3d_a3': dict(trips=1)})
check('summary one trip -> FAIL, (6) 3 of 4', word == 'FAIL' and 'without a BvhLoopCapTrip line: 3 of 4' in txt, txt)
txt, word = series(over={'f3d_bw': dict(faults=(X1, P1))})
check('summary pair on Sky W -> FAIL', word == 'FAIL', txt)
txt, word = series(over={'f3d_c2': dict(faults=())})
check('summary control without a pair -> FAIL', word == 'FAIL', txt)
txt, word = series(drop=('f3d_c2',))
check('summary missing tag -> NOT EVALUABLE', word == 'NOT EVALUABLE' and 'f3d_c2=NO READING' in txt, txt)
txt, word = series(over={'f3d_a2': dict(rows=7199)})
check('summary short hold -> NOT EVALUABLE', word == 'NOT EVALUABLE', txt)
txt, word = series(over={'f3d_a4': dict(faults=(0xda98000,))})
check('summary low page -> PASS EXCEPT LOW', word.startswith('PASS EXCEPT LOW') and 'f3d_a4' in txt, txt)
txt, word = series(over={'f3d_a1': dict(faults=(0xda98000,)), 'f3d_a3': dict(faults=(X1, P1))})
check('summary FAIL beats low', word == 'FAIL', txt)
txt, word = series(over={'f3d_a1': dict(win=('Window 1 minimized',))})
check('summary window event -> NOT EVALUABLE', word == 'NOT EVALUABLE' and 'f3d_a1=WINDOW EVENT' in txt, txt)
# --- text output ---
r = rd('tx_low', 'f3d_a1', faults=(X1, P1, 0xda98000), trips=2, k3=(900,))
t = R.text(r)
check('text names every low page with its address', '  low fault page 0x4018000' in t and '  low fault page 0xda98000' in t, t)
check('text pairs line', "(4) pairs X >= 4 GiB with (X >> 8) & ~0x3fff faulted: 1 [('0x401bc0000', '0x4018000')]" in t, t)
check('text verdict line', t.split('\n')[-1].startswith('F3D VERDICT f3d_a1: FAIL'), t.split('\n')[-1])
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
check('seal names cover the harness', set(('go_f3d.sh', 'f3d_read.py', 'win_f3d.py', 'sheetpair_f3d.py', 'test_f3d_read.py',
                                           'test_go_f3d.py', R.SC142)) <= set(R.SEALED))
# --- win_f3d.decide ---
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
s['HPP-337'] = (None, None)
check('win no answer rc 6', W.decide(s) == (6, 'error'))
check('win names F4c, session run step, P17', set(W.YIELD_TO) == {'HPP-337', 'HPP-352', 'HPP-364'} and
      set(W.NEED_DONE) == {'HPP-333', 'HPP-341'})
pw = subprocess.run([sys.executable, os.path.join(HERE, 'win_f3d.py')], capture_output=True,
                    env={k: v for k, v in os.environ.items() if not k.startswith('PAPERCLIP_') and k != 'PYTHONIOENCODING'})
check('win without API env refuses rc 6, ASCII line (cp1250)', pw.returncode == 6 and pw.stdout.decode('cp1250').startswith('win_f3d HPP-333 None'), pw)
# --- sheetpair positions ---
check('sheetpair positions: same index, min length', SP.positions(10567, 10078, 24) == (419, [k * 419 for k in range(24)]))
check('sheetpair positions: empty video', SP.positions(0, 100, 24) == (0, []))
check('sheetpair positions: short video', SP.positions(10, 12, 24) == (1, list(range(10))))
# --- real s142 logs (F3a scan12: c142_02 pairs [0x40253c000/0x4024000], lows 0x4018000 0x4024000 0xda98000, trips 6;
#     c142_09 voxel_world pairs and trips 6) ---
os.makedirs(REAL, exist_ok=True)
for src, tag in (('c142_02', 'f3d_c1'), ('c142_09', 'f3d_c2')):
    for kind in ('log_%s.txt', 'stdout_%s.txt'):
        dst = os.path.join(REAL, kind % tag)
        if not os.path.exists(dst):
            os.link('C:/kyty/s142/' + kind % src, dst)
    js = json.load(open('C:/kyty/s142/%s.json' % src, encoding='utf-8'))
    js['env'] = dict(js.get('env') or {}, KYTY_FIX_B1B='0')
    js['env'].pop('KYTY_REC', None)  # the census of s142 recorded a video; the F3d control does not
    js['binary_sha256'] = R.BIN_SHA
    json.dump(js, open(os.path.join(REAL, '%s.json' % tag), 'w', encoding='ascii'))
r = R.read_tag('f3d_c1', REAL, SC)
check('real c142_02: pairs = F3a scan12', r['pairs'] == [('0x40253c000', '0x4024000')], r['pairs'])
check('real c142_02: lows = F3a scan12', r['lows'] == ['0x4018000', '0x4024000', '0xda98000'], r['lows'])
check('real c142_02: trips 6', r['trips'] == 6, r['trips'])
check('real c142_02: entered, hold >= 120 s', r['entered'] and r['hold_s'] >= 120, r['hold_s'])
check('real c142_02: root cache line -> INVALID for a =0 tag (knob control)', r['verdict'] == 'INVALID', (r['verdict'], r['why']))
r2 = R.read_tag('f3d_c2', REAL, SC)
check('real c142_09: pair X1 0x401bc0000 / 0x4018000 (F3a)', ('0x401bc0000', '0x4018000') in r2['pairs'], r2['pairs'])
check('real c142_09: trips 6', r2['trips'] == 6, r2['trips'])
# --- strict cp1250 console ---
root = os.path.join(FX, 'cp')
shutil.rmtree(root, ignore_errors=True)
write_run(root, 'f3d_a1', faults=(X1, P1, 0xda98000))
env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
env['PYTHONIOENCODING'] = 'cp1250:strict'
p = subprocess.run([sys.executable, os.path.join(HERE, 'f3d_read.py'), '--tag', 'f3d_a1', '--root', root], capture_output=True, env=env)
check('cp1250 strict: rc 0 and ASCII', p.returncode == 0 and all(b < 128 for b in p.stdout), p.stderr[-300:])
p = subprocess.run([sys.executable, os.path.join(HERE, 'f3d_read.py'), '--summary', '--root', root], capture_output=True, env=env)
check('cp1250 strict: summary rc 0', p.returncode == 0 and b'F3D SERIES VERDICT' in p.stdout, p.stderr[-300:])
p = subprocess.run([sys.executable, os.path.join(HERE, 'f3d_read.py'), '--tag', 'f3d_zz'], capture_output=True, env=env)
check('usage rc 2', p.returncode == 2, p.stdout)
p = subprocess.run([sys.executable, os.path.join(HERE, 'f3d_read.py'), '--tag', 'f3d_a2', '--root', root], capture_output=True, env=env)
check('no log rc 1', p.returncode == 1, p.stdout)
shutil.rmtree(FX, ignore_errors=True)
print('checks %d failed %d' % (N[0], len(FAIL)))
print('ALL OK' if not FAIL else 'SOME FAILED: %s' % FAIL)
sys.exit(0 if not FAIL else 1)
