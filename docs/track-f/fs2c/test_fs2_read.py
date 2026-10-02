"""test_fs2_read.py - FS2c (HPP-383): fixtures of fs2_read.py - one fixture per member and per edge (synthetic logs), the reference
fixtures of p.298(g)(2) / p.296(d) on log_w144_09.txt and log_f5c_b.txt (must give STOP, else the seal is not accepted), regression
reads of the real F5c / F6e logs (the numbers of the lead's recount), the series summary, the seal check and the strict cp1250 output.
The first line is 'suite test_fs2_read.py sha256 <sha> target fs2_read.py sha256 <sha>'; the set ends with 'ALL OK'.  ASCII only.
  python test_fs2_read.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fs2_read as R  # noqa: E402

ME = os.path.abspath(__file__)
TGT = os.path.join(HERE, 'fs2_read.py')
W144 = 'C:/kyty/s144/log_w144_09.txt'
F5B = 'C:/kyty/f287/f5c/log_f5c_b.txt'
F5 = 'C:/kyty/f287/f5c/'
F6 = 'C:/kyty/f287/f6e/'
DT = 50000
N_ROWS = 6700
MIN_ROW = 1200
RES_ROW = 1400


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_fs2_read.py sha256 %s target fs2_read.py sha256 %s' % (sha(ME), sha(TGT)))
MODS = R.Mods()
ok = True
NCHK = 0


def check(name, cond, detail=''):
    global ok, NCHK
    NCHK += 1
    ok &= bool(cond)
    print('%s %s%s' % ('ok  ' if cond else 'FAIL', name, (' [%s]' % detail) if not cond else ''))


TMP = tempfile.mkdtemp(prefix='fs2fx_')


def env_of(kind, tag):
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GUEST_ARGS': '-lvl x', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}
    if kind in ('W', 'W0', 'V'):
        e['KYTY_TEST_MINIMIZE'] = '60:10'
    if kind in ('W', 'W0'):
        e.update({'VK_LAYER_PATH': R.VKLAYER, 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT': '100000000'})
    if kind == 'W0':
        e['KYTY_FIX_MINIMIZE'] = '0'
    if kind in ('V', 'T'):
        e['KYTY_REC'] = 'C:\\kyty\\f287\\fs2c\\rec_%s.mp4' % tag
    return e


def build(tag, kind, o=None):
    """Write a synthetic tag (log, stdout, json, glitch, idx, sheet) under TMP/<case>; returns the paths dict.  o - overrides."""
    o = dict(o or {})
    case = o.pop('case', tag)
    d = os.path.join(TMP, case)
    os.makedirs(d, exist_ok=True)
    level = R.TC if kind == 'T' else R.SKY
    L = []
    S = list(o.get('stdout', []))
    if o.get('precache', 'line') == 'line':
        L.append('PipelinePrecache: 4000 recipes -> 4000 pipelines in 1.0 s')
    elif o.get('precache') == 'alt':
        L.append('PipelinePrecache: no C:\\x\\variant_fixb26_fixb1b\\pipelines.bin yet')
        L.append('PipelinePrecache: saved 12 recipes')
    dual = o.get('dual', [(1, 1)])
    if not o.get('dual_after'):
        L += ['DualSrcBlend: supported=%d enabled=%d' % x for x in dual]
    if kind in ('W', 'W0'):
        L.append('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features')
        L.append('[Vulkan][W][1]: loader line')
    L += ['FixMinimize: on'] * o.get('fixmin', 0 if kind in ('W0', 'T') else 1)
    L += ['FixB9a: on'] * o.get('fixb9a', 1)
    L.append('GuestOut: MODL: x')
    if o.get('dual_after'):
        L += ['DualSrcBlend: supported=%d enabled=%d' % x for x in dual]
    for n in range(1, 21):
        L.append('FrameTrace: n=%d dt_us=%d draws=0' % (n, DT))
    L.append('GuestOut: Level has started: %s' % level)
    stand = kind in ('W', 'W0', 'V')
    if stand and not o.get('no_config'):
        L.append('TestMinimize: config on delay_s=60.000 dur_s=10.000')
    if stand:
        L.append('TestMinimize: armed')
    rows = o.get('rows', N_ROWS)
    big = dict(o.get('big', {}))            # row index -> dt
    extra = dict(o.get('extra', {}))        # row index -> [lines] (before the row)
    idx = []
    t = 0.0
    n = 21
    calls_sc = 0
    died = False
    for i in range(rows):
        if stand and i == MIN_ROW:
            L.append('TestMinimize: minimize')
            L.append('Window 1 minimized')
            if kind == 'W0':
                L.append('Window 1 lost keyboard focus')
                L += o.get('w0_lines', ['[Vulkan][E][2]: vkCreateSwapchainKHR(): pCreateInfo->imageExtent (width = 0, height = 0) is invalid.',
                                        'The Vulkan spec states: imageExtent members width and height must both be non-zero '
                                        '(https://x#VUID-VkSwapchainCreateInfoKHR-imageExtent-01689)',
                                        '--- Error ---', ' in C:\\x\\vulkanWindow.cpp:913'])
                died = True
                break
            if not o.get('no_episode'):
                L.append('SwapchainZeroExtent: begin')
        if stand and i == RES_ROW:
            L.append('TestMinimize: restore')
            L.append('Window 1 restored')
            if not o.get('no_episode'):
                L.append('SwapchainZeroExtent: end frames_dropped=200 ms=%d' % o.get('end_ms', 10000))
            L.append('Recovering Vulkan swapchain')
        if stand and o.get('end_late') and i == RES_ROW:
            pass
        for ln in extra.get(i, []):
            L.append(ln)
        if kind in ('W',) and i % 100 == 50 and i < o.get('vk2_until', rows) and not o.get('no_vk2'):
            L.append('[Vulkan][W][2]: Validation Warning: x and this write is unused.')
        if kind == 'T' and i % o.get('calls_every', 200) == 0 and not (o.get('no_hold_calls') and i > 0):
            calls_sc = o.get('creates', lambda k: 0)(i)
            L.append('AudioPropagation: calls total=%d handles=3 SourceCreate=%d SourceSetAttributes=%d SourceRender=%d SourceDestroy=0' % (
                i + 10, calls_sc, o.get('ssa', 5), o.get('sr', 5)))
        dt = big.get(i, DT)
        L.append('FrameTrace: n=%d dt_us=%d draws=%d' % (n, dt, 200))
        t += dt / 1e6
        if not (stand and MIN_ROW <= i < RES_ROW):
            idx.append((len(idx), n, round(t, 3)))
        n += 1
    L += o.get('tail', [])
    js = dict(tag=tag, binary_sha256=o.get('binary', R.BIN_SHA), guest_args='-lvl %s' % level,
              cmdline=['kyty_emulator.exe', '--vulkan-validation', 'false'] + (['--vulkan-validation', 'true'] if kind in ('W', 'W0') or o.get('cmd_val') else []),
              env=env_of(kind, tag), attempts=[dict(outcome='ok', hold_s=330.0, hold_exit=(3221226505 if died else None))])
    js['env'].update(o.get('env', {}))
    for k in o.get('env_del', []):
        js['env'].pop(k, None)
    if o.get('attempts') is not None:
        js['attempts'] = o['attempts']
    P = dict(log=os.path.join(d, 'log.txt'), stdout=os.path.join(d, 'stdout.txt'), json=os.path.join(d, 'j.json'),
             glitch=os.path.join(d, 'glitch.txt'), sheet=os.path.join(d, 'sheet.png'), idx=os.path.join(d, 'rec.idx'))
    with open(P['log'], 'w', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    with open(P['stdout'], 'w', newline='\n') as f:
        f.write('\n'.join(S) + '\n')
    with open(P['json'], 'w') as f:
        json.dump(js, f)
    if kind in ('V', 'T'):
        idx = o.get('idx_fn', lambda x: x)(idx)
        frames = o.get('frames', len(idx))
        gl = o.get('glitches', [])
        with open(P['glitch'], 'w', newline='\n') as f:
            f.write('rec.mp4: %d frames 960x540, index entries %d\none-frame glitches: %d\n' % (frames, len(idx), len(gl)))
            for v, p, tt in gl:
                f.write('  video %5d present %6d t=%7.2fs diff_prev=  9.0 diff_next=  9.0\n' % (v, p, tt))
        with open(P['idx'], 'w', newline='\n') as f:
            f.write('\n'.join('%d %d %.3f' % x for x in idx) + '\n')
        if not o.get('no_sheet'):
            with open(P['sheet'], 'wb') as f:
                f.write(b'PNG')
    return P


def rd(tag, kind, o=None):
    return R.read_tag(tag, 'X', MODS, build(tag, kind, o))


def V(tag, kind, o=None):
    r = rd(tag, kind, o)
    return r['verdict'], r


# ---- the stop rule: the reference fixtures of p.298(g)(2) / p.296(d) (must give STOP) ----
s = R.stop_rule(W144)
check('reference log_w144_09.txt -> STOP (anchor Window 1 minimized, no stand line; VUID one line after)', s['stop'] and s['vuid'] == [(288182942, 1)],
      s)
s = R.stop_rule(F5B)
check('reference log_f5c_b.txt -> STOP (anchor TestMinimize: minimize; VUID one line after)', s['stop'] and s['anchor'] == 30639250
      and s['vuid'] == [(30643161, 1)], s)
check('real log_f5c_a.txt (=1) -> NO STOP', not R.stop_rule(F5 + 'log_f5c_a.txt')['stop'])
check('real log_f5c_g.txt (=0, no validation) -> NO STOP', not R.stop_rule(F5 + 'log_f5c_g.txt')['stop'])
E = '[Vulkan][E][2]: vkCreateSwapchainKHR(): pCreateInfo->imageExtent (width = 0, height = 0) is invalid.'
U = 'see #VUID-VkSwapchainCreateInfoKHR-imageExtent-01689'


def sr(lines, name):
    p = os.path.join(TMP, 'sr_%s.txt' % name)
    with open(p, 'w', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    return R.stop_rule(p)


check('stop rule: VUID in the same line -> STOP', sr(['TestMinimize: minimize', E + ' ' + U], 'same')['stop'])
check('stop rule: VUID 1 line after -> STOP', sr(['TestMinimize: minimize', E, U], 'n1')['stop'])
check('stop rule: VUID 3 lines after (edge) -> STOP', sr(['TestMinimize: minimize', E, 'a', 'b', U], 'n3')['stop'])
check('stop rule: VUID 4 lines after (edge+1) -> NO STOP', not sr(['TestMinimize: minimize', E, 'a', 'b', 'c', U], 'n4')['stop'])
check('stop rule: the [Vulkan][E] zero-extent line before the anchor -> NO STOP', not sr([E, U, 'TestMinimize: minimize'], 'before')['stop'])
check('stop rule: [Vulkan][E] without the zero extent -> NO STOP', not sr(['TestMinimize: minimize', '[Vulkan][E][2]: other', U], 'noext')['stop'])
check('stop rule: the zero-extent text in a [Vulkan][W] line -> NO STOP',
      not sr(['TestMinimize: minimize', E.replace('[E]', '[W]'), U], 'wline')['stop'])
check('stop rule: no stand line and no Window 1 minimized -> NO STOP (no anchor)', not sr([E, U], 'noanchor')['stop'])
x = sr(['Window 1 minimized', E, U], 'fallback')
check('stop rule: no stand line, Window 1 minimized -> STOP (reading of the executor [I])', x['stop'] and 'executor' in x['anchor_kind'])
x = sr(['Window 1 minimized', E, U, 'TestMinimize: minimize'], 'standwins')
check('stop rule: a stand line anywhere is the anchor (letter) - E before it -> NO STOP', not x['stop'] and 'letter' in x['anchor_kind'])
check('stop rule: VUID on the 4th line but a second E line within 3 -> STOP',
      sr(['TestMinimize: minimize', E, 'a', 'b', E, U], 'second')['stop'])

# ---- regression reads of the real logs (numbers of the lead's recount; admission fails by design: other binary / env) ----


def P(root, t):
    return dict(log=root + 'log_%s.txt' % t, stdout=root + 'stdout_%s.txt' % t, json=root + '%s.json' % t, glitch=root + 'glitch_%s.txt' % t,
                sheet=root + 'sheet_%s.png' % t, idx=root + 'rec_%s.mp4.idx' % t)


r = R.read_tag('fs2_w', 'X', MODS, P(F5, 'f5c_a'))
pa = r['parts']
check('real f5c_a as fs2_w: letter (a) members true except DualSrcBlend (binary 6f495a65, precache 0) and NOT ADMITTED',
      all(v for k, v in pa.items() if k != 'dualsrcblend_1_1') and not pa['dualsrcblend_1_1'] and r['verdict'] == 'NOT ADMITTED', pa)
check('real f5c_a: hold 324.5 s, rows after restore 2039, Recovering 1, window events outside the stand 0',
      abs(r['dt_after_first_s'] - 324.5) < 0.05 and r['rows_after_restore'] == 2039 and r['recovering'] == 1 and not r['window_out'],
      (r['dt_after_first_s'], r['rows_after_restore'], r['recovering'], r['window_out']))
r = R.read_tag('fs2_w0', 'X', MODS, P(F5, 'f5c_b'))
check('real f5c_b as fs2_w0: controls ok, stop rule STOP, W not held -> 295(b)(1)-(3) n/a', r['controls_ok'] and r['parts']['stop_rule']
      and r['held'] is False, (r['controls_ok'], r['parts'], r['held']))
r = R.read_tag('fs2_v', 'X', MODS, P(F5, 'f5c_v'))
check('real f5c_v as fs2_v: letter (v) members all true (334.4 s, 9152 frames, N1 7388 records after end)',
      all(r['parts'].values()) and r['video']['after_end_records'] == 7388 and r['glitch']['video_frames'] == 9152, r['parts'])
r = R.read_tag('fs2_t', 'X', MODS, P(F6, 'f6e_a2'))
check('real f6e_a2 as fs2_t: SourceCreate 48 / 7033 rows = 0.0068, wake yes, K3 hold 0, 0 stubs, 0 ASSERT',
      r['freq']['d_create'] == 48 and r['freq']['rows'] == 7033 and r['wake'] and r['k3_hold'] == 0 and r['stub_lines'] == 0
      and r['asserts_log'] == 0, (r['freq'], r['wake'], r['k3_hold']))
r = R.read_tag('fs2_t', 'X', MODS, P(F6, 'f6e_a1'))
check('real f6e_a1 as fs2_t: K3 hold 1 (= limit 1, not over)', r['k3_hold'] == 1 and not r['k3_over'], r['k3_hold'])
r = R.read_tag('fs2_t', 'X', MODS, P(F6, 'f6e_c1'))
check('real f6e_c1 (=0 control) as fs2_t: FixB9a: on 0 -> NOT ADMITTED first (env KYTY_FIX_B9A=0); user_msg_param 0 (UMSG_T basis)',
      r['verdict'] == 'NOT ADMITTED' and r['umsg_log'] == 0 and r['fixb9a'] == 0, (r['verdict'], r['umsg_log'], r['fixb9a']))

# ---- fs2_w synthetic: base and every member / edge ----
v, r = V('fs2_w', 'W')
check('fs2_w base -> PASS', v == 'PASS', (v, r['why']))
check('fs2_w base: stop-check continue', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('continue: fs2_w PASS'))
check('fs2_w: binary sha other -> NOT ADMITTED', V('fs2_w', 'W', dict(case='w_bin', binary='0' * 64))[0] == 'NOT ADMITTED')
check('fs2_w: KYTY_FIX_B9A=1 in the env -> NOT ADMITTED', V('fs2_w', 'W', dict(case='w_fixenv', env={'KYTY_FIX_B9A': '1'}))[0] == 'NOT ADMITTED')
check('fs2_w: KYTY_FIX_MINIMIZE=1 in the env -> NOT ADMITTED', V('fs2_w', 'W', dict(case='w_fixenv2', env={'KYTY_FIX_MINIMIZE': '1'}))[0] == 'NOT ADMITTED')
check('fs2_w: KYTY_PIPELINE_PRECACHE=0 -> NOT ADMITTED', V('fs2_w', 'W', dict(case='w_pc', env={'KYTY_PIPELINE_PRECACHE': '0'}))[0] == 'NOT ADMITTED')
check('fs2_w: VK_LAYER_MESSAGE_ID_FILTER set -> NOT ADMITTED (295(b)(4))',
      V('fs2_w', 'W', dict(case='w_filt', env={'VK_LAYER_MESSAGE_ID_FILTER': 'x'}))[0] == 'NOT ADMITTED')
check('fs2_w: VK_LAYER_DUPLICATE_MESSAGE_LIMIT=1000000 -> NOT ADMITTED (295(b)(4))',
      V('fs2_w', 'W', dict(case='w_lim', env={'VK_LAYER_DUPLICATE_MESSAGE_LIMIT': '1000000'}))[0] == 'NOT ADMITTED')
check('fs2_w: VK_LAYER_PATH missing -> NOT ADMITTED', V('fs2_w', 'W', dict(case='w_lp', env_del=['VK_LAYER_PATH']))[0] == 'NOT ADMITTED')
check('fs2_w: KYTY_TEST_MINIMIZE=60:9 -> NOT ADMITTED', V('fs2_w', 'W', dict(case='w_stand', env={'KYTY_TEST_MINIMIZE': '60:9'}))[0] == 'NOT ADMITTED')
check('fs2_w: KYTY_GPU_CLOCK_PIN missing -> NOT ADMITTED', V('fs2_w', 'W', dict(case='w_pin', env_del=['KYTY_GPU_CLOCK_PIN']))[0] == 'NOT ADMITTED')
check('fs2_w: KYTY_REC set -> NOT ADMITTED (no video on W)', V('fs2_w', 'W', dict(case='w_rec', env={'KYTY_REC': 'C:/x/rec_fs2_w.mp4'}))[0] == 'NOT ADMITTED')
check('fs2_w: two attempts -> NOT ADMITTED', V('fs2_w', 'W', dict(case='w_att', attempts=[dict(outcome='ok'), dict(outcome='ok')]))[0] == 'NOT ADMITTED')
check('fs2_w: no precache line -> NOT ADMITTED (I10)', V('fs2_w', 'W', dict(case='w_nopre', precache='none'))[0] == 'NOT ADMITTED')
check('fs2_w: precache alt (no-variant + saved) -> PASS (I10 B1)', V('fs2_w', 'W', dict(case='w_prealt', precache='alt'))[0] == 'PASS')
check('fs2_w: one layer limit line -> NOT ADMITTED (295(b)(1))',
      V('fs2_w', 'W', dict(case='w_limit', extra={3000: ['[Vulkan][W][2]: x, this will be the last time reporting it.']}))[0] == 'NOT ADMITTED')
check('fs2_w: limit line in the stdout -> NOT ADMITTED (295(b)(1))',
      V('fs2_w', 'W', dict(case='w_limit_std', stdout=['this will be the last time reporting it']))[0] == 'NOT ADMITTED')
check('fs2_w: no validation-layer line [W][2] -> NOT ADMITTED (295(b)(2), (3))', V('fs2_w', 'W', dict(case='w_novk2', no_vk2=True))[0] == 'NOT ADMITTED')
# 295(b)(3): the last vk2 line is placed before row k; the presented time after it = (N_ROWS - k) * DT
v, r = V('fs2_w', 'W', dict(case='w_le_edge', no_vk2=True, extra={N_ROWS - 200: ['[Vulkan][W][2]: last']}))
check('fs2_w: last [W][2] line exactly 10.0 s before the end (edge) -> PASS', v == 'PASS' and r['layer_end_us'] == 10000000, (v, r['layer_end_us']))
v, r = V('fs2_w', 'W', dict(case='w_le_over', no_vk2=True, extra={N_ROWS - 201: ['[Vulkan][W][2]: last']}))
check('fs2_w: last [W][2] line 10.05 s before the end -> NOT ADMITTED', v == 'NOT ADMITTED' and r['layer_end_us'] == 10050000, (v, r['layer_end_us']))
v, r = V('fs2_w', 'W', dict(case='w_e2', no_vk2=True, extra={N_ROWS - 5: ['[Vulkan][E][2]: err']}))
check('fs2_w: an [E][2] line counts as a validation-layer line but fails vke0 -> FAIL', v == 'FAIL' and 'vke0' in r['why'], (v, r['why']))
v, r = V('fs2_w', 'W', dict(case='w_dead', tail=['Unhandled exception: rip=0x900001000']))
check('fs2_w: a death marker -> W not held, 295(b)(1)-(3) n/a; letter FAIL (deaths0)', v == 'FAIL' and r['held'] is False
      and 'deaths0' in r['why'], (v, r['held'], r['why']))
check('fs2_w: death without [Vulkan][E] -> stop-check stop', R.stop_check(r).startswith('stop: death marker'))
v, r = V('fs2_w', 'W', dict(case='w_b9a0', fixb9a=0))
check('fs2_w: FixB9a: on 0 -> INVALID (form error, p.327(g)(1))', v == 'INVALID', v)
check('fs2_w: INVALID -> stop-check stop', R.stop_check(r).startswith('stop: fs2_w INVALID'))
check('fs2_w: FixB9a: on 2 -> INVALID', V('fs2_w', 'W', dict(case='w_b9a2', fixb9a=2))[0] == 'INVALID')
v, r = V('fs2_w', 'W', dict(case='w_fm0', fixmin=0))
check('fs2_w: FixMinimize: on 0 -> FAIL (fixminimize_on)', v == 'FAIL' and r['why'] == ['fixminimize_on'], (v, r['why']))
check('fs2_w: FixMinimize: on 2 -> FAIL', V('fs2_w', 'W', dict(case='w_fm2', fixmin=2))[0] == 'FAIL')
v, r = V('fs2_w', 'W', dict(case='w_dual0', dual=[]))
check('fs2_w: no DualSrcBlend line -> FAIL', v == 'FAIL' and r['why'] == ['dualsrcblend_1_1'], (v, r['why']))
check('fs2_w: DualSrcBlend supported=1 enabled=0 -> FAIL', V('fs2_w', 'W', dict(case='w_dual10', dual=[(1, 0)]))[0] == 'FAIL')
check('fs2_w: DualSrcBlend 1/1 and a second line 0/0 -> FAIL', V('fs2_w', 'W', dict(case='w_dual2', dual=[(1, 1), (0, 0)]))[0] == 'FAIL')
check('fs2_w: DualSrcBlend 1/1 after the first GuestOut -> FAIL (p.300(b)(4))', V('fs2_w', 'W', dict(case='w_dualafter', dual_after=True))[0] == 'FAIL')
v, r = V('fs2_w', 'W', dict(case='w_assert', extra={3000: ['ASSERT: x']}))
check('fs2_w: ASSERT: in the log -> FAIL (B9a)', v == 'FAIL' and r['why'] == ['b9a_assert0_log_stdout'], (v, r['why']))
check('fs2_w: ASSERT: in the stdout -> FAIL (B9a)', V('fs2_w', 'W', dict(case='w_assert_std', stdout=['ASSERT: y']))[0] == 'FAIL')
v, r = V('fs2_w', 'W', dict(case='w_umsg', extra={3000: ['user_msg_param 1']}))
check('fs2_w: user_msg_param in the log -> FAIL (B9a)', v == 'FAIL' and r['why'] == ['b9a_user_msg_param0'], (v, r['why']))
v, r = V('fs2_w', 'W', dict(case='w_umsg_std', stdout=['user_msg_param 2']))
check('fs2_w: user_msg_param only in the stdout -> PASS, member of the executor FAILED', v == 'PASS' and not r['exec_ok'], (v, r['exec_ok']))
ST = 'Unresolved import stub called [0]: patch_vaddr=0x1 jmprela_index=1 symbol=b-dYXrjSNZU[AudioPropagation_v1][AudioPropagation_v1.0][Func] type=Func'
v, r = V('fs2_w', 'W', dict(case='w_stub', extra={3000: [ST]}))
check('fs2_w: an AudioPropagation stub line in the log -> FAIL (B9a)', v == 'FAIL' and r['why'] == ['b9a_audiopropagation_stub_lines0'],
      (v, r['why']))
check('fs2_w: a stub line of another library -> PASS', V('fs2_w', 'W', dict(case='w_stub_other', extra={3000: [ST.replace('AudioPropagation', 'Other')]}))[0] == 'PASS')
v, r = V('fs2_w', 'W', dict(case='w_stub_std', stdout=['Unresolved import stub called: b-dYXrjSNZU[AudioPropagation_v1][AudioPropagation_v1.0][Func]']))
check('fs2_w: an AudioPropagation stub line only in the stdout -> PASS, member of the executor FAILED', v == 'PASS' and not r['exec_ok'], v)
check('fs2_w: a [Vulkan][E] line -> FAIL (vke0)', 'vke0' in V('fs2_w', 'W', dict(case='w_vke', extra={3000: ['[Vulkan][E][2]: x']}))[1]['why'])
v, r = V('fs2_w', 'W', dict(case='w_min2in', extra={1300: ['Window 1 minimized']}))
check('fs2_w: a second Window 1 minimized inside the stand window -> FAIL (one_window1_minimized)', v == 'FAIL'
      and r['why'] == ['one_window1_minimized'], (v, r['why']))
v, r = V('fs2_w', 'W', dict(case='w_minout', extra={3000: ['Window 1 minimized']}))
check('fs2_w: Window minimized outside the stand window -> NOT EVALUABLE (p.273(z))', v == 'NOT EVALUABLE', (v, r['why']))
check('fs2_w: window event outside -> stop-check stop', R.stop_check(r).startswith('stop: fs2_w NOT EVALUABLE'))
check('fs2_w: Window 2 minimized before the stand -> NOT EVALUABLE', V('fs2_w', 'W', dict(case='w_min2', extra={100: ['Window 2 minimized']}))[0] == 'NOT EVALUABLE')
v, r = V('fs2_w', 'W', dict(case='w_recout', extra={3000: ['Recovering Vulkan swapchain']}))
check('fs2_w: Recovering outside the stand window -> NOT EVALUABLE', v == 'NOT EVALUABLE', v)
check('fs2_w: Recovering 1.95 s after restore (edge inside +2 s) -> PASS',
      V('fs2_w', 'W', dict(case='w_recin', extra={RES_ROW + 39: ['Recovering Vulkan swapchain']}))[0] == 'PASS')
check('fs2_w: Recovering 2.1 s after restore -> NOT EVALUABLE',
      V('fs2_w', 'W', dict(case='w_recout2', extra={RES_ROW + 42: ['Recovering Vulkan swapchain']}))[0] == 'NOT EVALUABLE')
check('fs2_w: lost keyboard focus outside the stand -> PASS (data only)',
      V('fs2_w', 'W', dict(case='w_focus', extra={3000: ['Window 1 lost keyboard focus']}))[0] == 'PASS')
# hold >= 310: post rows = rows - 1; 310 s = 6200 rows of 0.05 s -> rows 6201 (edge) / 6200
check('fs2_w: hold exactly 310.0 s (edge) -> PASS', V('fs2_w', 'W', dict(case='w_h310', rows=6201, vk2_until=6201))[0] == 'PASS')
v, r = V('fs2_w', 'W', dict(case='w_h309', rows=6200, vk2_until=6200))
check('fs2_w: hold 309.95 s -> FAIL (hold)', v == 'FAIL' and r['why'] == ['hold'], (v, r['why']))
check('fs2_w: no SwapchainZeroExtent lines -> FAIL (begin_end, end_not_late)', set(V('fs2_w', 'W', dict(case='w_noep', no_episode=True))[1]['why'])
      >= {'begin_end'})
v, r = V('fs2_w', 'W', dict(case='w_late', no_episode=True, extra={MIN_ROW: ['SwapchainZeroExtent: begin'],
                                                                  RES_ROW + 41: ['SwapchainZeroExtent: end frames_dropped=1 ms=12050']}))
check('fs2_w: end 2.05 s after restore -> FAIL (end_not_late), both readings late', v == 'FAIL' and r['why'] == ['end_not_late']
      and r['late_log'] is True and r['late_ms'] is True, (v, r['why'], r['late_log'], r['late_ms']))
v, r = V('fs2_w', 'W', dict(case='w_late2', no_episode=True, extra={MIN_ROW: ['SwapchainZeroExtent: begin'],
                                                                   RES_ROW + 40: ['SwapchainZeroExtent: end frames_dropped=1 ms=12000']}))
check('fs2_w: end 2.00 s after restore (edge) -> PASS', v == 'PASS' and r['late_log'] is False, (v, r['why'], r['late_log']))
check('fs2_w: no config line -> NOT EVALUABLE', V('fs2_w', 'W', dict(case='w_nocfg', no_config=True))[0] == 'NOT EVALUABLE')
check('fs2_w: KYTY_FIX_* none, but the stand config line missing -> stop-check stop', R.stop_check(rd('fs2_w', 'W', dict(case='w_nocfg2', no_config=True))).startswith('stop'))

# ---- fs2_w0 ----
v, r = V('fs2_w0', 'W0')
check('fs2_w0 base -> STOP', v == 'STOP', (v, r['why']))
check('fs2_w0: stop-check continue: data', R.stop_check(r).startswith('continue: data (b) STOP'))
v, r = V('fs2_w0', 'W0', dict(case='w0_nostop', w0_lines=['[Vulkan][E][2]: other error', '--- Error ---']))
check('fs2_w0: no zero-extent line -> NO STOP, stop-check continue', v == 'NO STOP' and R.stop_check(r).startswith('continue: data'), v)
check('fs2_w0: VUID 4 lines after -> NO STOP', V('fs2_w0', 'W0', dict(case='w0_n4', w0_lines=[E, 'a', 'b', 'c', U]))[0] == 'NO STOP')
check('fs2_w0: KYTY_FIX_MINIMIZE missing from the env -> NOT ADMITTED', V('fs2_w0', 'W0', dict(case='w0_env', env_del=['KYTY_FIX_MINIMIZE']))[0] == 'NOT ADMITTED')
check('fs2_w0: KYTY_FIX_MINIMIZE=1 -> NOT ADMITTED', V('fs2_w0', 'W0', dict(case='w0_env1', env={'KYTY_FIX_MINIMIZE': '1'}))[0] == 'NOT ADMITTED')
check('fs2_w0: FixMinimize: on 1 -> NOT EVALUABLE (arm control)', V('fs2_w0', 'W0', dict(case='w0_fm', fixmin=1))[0] == 'NOT EVALUABLE')
check('fs2_w0: FixB9a: on 0 -> not a form error on w0 (STOP)', V('fs2_w0', 'W0', dict(case='w0_b9a', fixb9a=0))[0] == 'STOP')

# ---- fs2_v ----
v, r = V('fs2_v', 'V')
check('fs2_v base -> PASS', v == 'PASS', (v, r['why']))
check('fs2_v: a glitch outside the window -> FAIL', 'glitches_outside0' in V('fs2_v', 'V', dict(case='v_gout', glitches=[(3000, 3021, 160.0)]))[1]['why'])
check('fs2_v: a glitch inside the window (minimize .. end + 2 s) -> PASS', V('fs2_v', 'V', dict(case='v_gin', glitches=[(1250, 1300, 71.0)]))[0] == 'PASS')
check('fs2_v: video 3000 frames (edge) -> PASS', V('fs2_v', 'V', dict(case='v_f3000', frames=3000))[0] == 'PASS')
check('fs2_v: video 2999 frames -> FAIL', 'video_frames' in V('fs2_v', 'V', dict(case='v_f2999', frames=2999))[1]['why'])
check('fs2_v: no sheet -> FAIL', 'sheet' in V('fs2_v', 'V', dict(case='v_nosheet', no_sheet=True))[1]['why'])
check('fs2_v: K2 frame outside the window -> FAIL', 'no_k1k2_outside' in V('fs2_v', 'V', dict(case='v_k2out', big={3000: 1000000}))[1]['why'])
check('fs2_v: K2 frame inside the window -> PASS', V('fs2_v', 'V', dict(case='v_k2in', big={1300: 1500000}))[0] == 'PASS')
check('fs2_v: K2 999 999 us outside -> PASS (edge below 1 s)', V('fs2_v', 'V', dict(case='v_k2edge', big={3000: 999999}))[0] == 'PASS')


def swap_after(idx):
    k = len(idx) - 100
    a, b = idx[k], idx[k + 1]
    idx[k], idx[k + 1] = (a[0], b[1], a[2]), (b[0], a[1], b[2])
    return idx


check('fs2_v: present order break after end (N1) -> FAIL', 'n1_present_order_after_end' in V('fs2_v', 'V', dict(case='v_n1', idx_fn=swap_after))[1]['why'])
check('fs2_v: FixMinimize: on 0 -> NOT EVALUABLE', V('fs2_v', 'V', dict(case='v_fm0', fixmin=0))[0] == 'NOT EVALUABLE')
check('fs2_v: ASSERT: -> FAIL (B9a)', V('fs2_v', 'V', dict(case='v_assert', extra={3000: ['ASSERT: z']}))[1]['why'] == ['b9a_assert0_log_stdout'])
check('fs2_v: FixB9a: on 0 -> INVALID', V('fs2_v', 'V', dict(case='v_b9a', fixb9a=0))[0] == 'INVALID')
check('fs2_v: --vulkan-validation true -> NOT ADMITTED', V('fs2_v', 'V', dict(case='v_val', cmd_val=True))[0] == 'NOT ADMITTED')
check('fs2_v: hold 329.95 s -> FAIL', 'hold' in V('fs2_v', 'V', dict(case='v_h', rows=6600))[1]['why'])
check('fs2_v: a death marker in the stand window only -> PASS (no K1 outside)',
      V('fs2_v', 'V', dict(case='v_deathin', extra={1300: ['GpuHangAbort: x']}))[0] == 'PASS')

# ---- fs2_t / fs2_tr ----
CR = (lambda k: 2 if k > 0 else 0)          # 2 creates on the hold over ~6700 rows -> < 0.1


def T(case, **o):
    o.setdefault('creates', CR)
    o['case'] = case
    return o


v, r = V('fs2_t', 'T', T('t_base'))
check('fs2_t base -> PASS', v == 'PASS', (v, r['why']))
check('fs2_t: K3 hold 1 (= limit) -> PASS', V('fs2_t', 'T', T('t_k31', big={1000: 150000}))[0] == 'PASS')
v, r = V('fs2_t', 'T', T('t_k32', big={1000: 150000, 2000: 150000}))
check('fs2_t: K3 hold 2 -> K3 OVER, stop-check repeat-k3: fs2_tr', v == 'K3 OVER' and R.stop_check(r).startswith('repeat-k3: fs2_tr'), v)
check('fs2_t: K3 in the entry window (row < 599) not counted -> PASS', V('fs2_t', 'T', T('t_k3w', big={100: 150000, 200: 150000}))[0] == 'PASS')
check('fs2_t: K3 99 999 us not counted (edge) -> PASS', V('fs2_t', 'T', T('t_k3e', big={1000: 99999, 2000: 99999}))[0] == 'PASS')
reads = dict(fs2_t=r, fs2_tr=rd('fs2_tr', 'T', T('tr_pass')))
check('judge: fs2_t K3 OVER + fs2_tr PASS -> PASS (the repeat decides)', R.judge_t(reads)[0] == 'PASS', R.judge_t(reads))
reads['fs2_tr'] = rd('fs2_tr', 'T', T('tr_k3', big={1000: 150000, 2000: 150000}))
check('judge: fs2_tr K3 OVER too -> FAIL', R.judge_t(reads)[0] == 'FAIL', R.judge_t(reads))
reads['fs2_tr'] = rd('fs2_tr', 'T', T('tr_assert', extra={3000: ['ASSERT: q']}))
check('judge: fs2_tr FAIL on another member -> FAIL', R.judge_t(reads)[0] == 'FAIL', R.judge_t(reads))
reads['fs2_tr'] = None
check('judge: fs2_t K3 OVER, fs2_tr not run -> REPEAT DUE', R.judge_t(reads)[0] == 'REPEAT DUE')
ra = rd('fs2_t', 'T', T('t_assert', extra={3000: ['ASSERT: q']}))
check('judge: fs2_t FAIL (ASSERT) is not lifted by a repeat -> FAIL', R.judge_t(dict(fs2_t=ra, fs2_tr=rd('fs2_tr', 'T', T('tr_ok2'))))[0] == 'FAIL')
check('fs2_t: ASSERT: in the stdout -> FAIL', V('fs2_t', 'T', T('t_as', stdout=['ASSERT: s']))[0] == 'FAIL')
check('fs2_t: user_msg_param 1 > 0 -> FAIL (p.294(b), UMSG_T 0)', V('fs2_t', 'T', T('t_um', extra={3000: ['user_msg_param']}))[0] == 'FAIL')
check('fs2_t: a stub line of any library -> FAIL', V('fs2_t', 'T', T('t_st', extra={3000: [ST.replace('AudioPropagation', 'Other')]}))[0] == 'FAIL')
check('fs2_t: K2 frame -> FAIL', V('fs2_t', 'T', T('t_k2', big={3000: 1000000}))[0] == 'FAIL')
check('fs2_t: a glitch -> FAIL', V('fs2_t', 'T', T('t_gl', glitches=[(10, 10, 1.0)]))[0] == 'FAIL')
check('fs2_t: video 2999 frames -> FAIL', V('fs2_t', 'T', T('t_fr', frames=2999))[0] == 'FAIL')
check('fs2_t: no sheet -> FAIL', V('fs2_t', 'T', T('t_sh', no_sheet=True))[0] == 'FAIL')
check('fs2_t: a death marker -> FAIL and stop-check stop', R.stop_check(rd('fs2_t', 'T', T('t_d', tail=['--- Fatal Error ---']))).startswith('stop'))
# frequency: creates c on the last counter line of the hold, rows between L0 (row 0) and L1 (row 6600): 6599 rows
v, r = V('fs2_t', 'T', T('t_fq', creates=lambda k: 660 if k > 0 else 0))
check('fs2_t: SourceCreate per frame 660 / 6599 = 0.1000+ -> FAIL', v == 'FAIL' and r['freq']['freq'] >= 0.1, (v, r['freq']))
v, r = V('fs2_t', 'T', T('t_fq2', creates=lambda k: 659 if k > 0 else 0))
check('fs2_t: SourceCreate per frame 659 / 6599 < 0.1 -> PASS (edge)', v == 'PASS', (v, r['freq']))
check('fs2_t: wake control 0 / 0 -> FAIL', V('fs2_t', 'T', T('t_wk', ssa=0, sr=0))[0] == 'FAIL')
check('fs2_t: wake by SourceRender only -> PASS', V('fs2_t', 'T', T('t_wk2', ssa=0, sr=1))[0] == 'PASS')
check('fs2_t: no counter line on the hold -> NOT EVALUABLE', V('fs2_t', 'T', T('t_nc', no_hold_calls=True))[0] == 'NOT EVALUABLE')
check('fs2_t: hold 119.95 s -> NOT EVALUABLE', V('fs2_t', 'T', T('t_h', rows=2400, frames=3000))[0] == 'NOT EVALUABLE')
check('fs2_t: hold 120.0 s (edge) -> PASS', V('fs2_t', 'T', T('t_h2', rows=2401, calls_every=100, frames=3000))[0] == 'PASS')
v, r = V('fs2_t', 'T', T('t_win', extra={3000: ['Window 1 minimized']}))
check('fs2_t: Window minimized -> WINDOW EVENT, stop', v == 'WINDOW EVENT' and R.stop_check(r).startswith('stop'), v)
check('fs2_t: Recovering in the stdout -> WINDOW EVENT', V('fs2_t', 'T', T('t_win2', stdout=['Recovering Vulkan swapchain']))[0] == 'WINDOW EVENT')
check('fs2_t: FixB9a: on 0 -> INVALID', V('fs2_t', 'T', T('t_b9', fixb9a=0))[0] == 'INVALID')
check('fs2_t: KYTY_FIX_B9A=1 in the env -> NOT ADMITTED', V('fs2_t', 'T', T('t_env', env={'KYTY_FIX_B9A': '1'}))[0] == 'NOT ADMITTED')
check('fs2_t: KYTY_TEST_MINIMIZE set -> NOT ADMITTED', V('fs2_t', 'T', T('t_env2', env={'KYTY_TEST_MINIMIZE': '60:10'}))[0] == 'NOT ADMITTED')

# ---- summary ----
w, w0, vv, t = rd('fs2_w', 'W', dict(case='s_w')), rd('fs2_w0', 'W0', dict(case='s_w0')), rd('fs2_v', 'V', dict(case='s_v')), \
    rd('fs2_t', 'T', T('s_t'))
txt, word = R.summary(dict(fs2_w=w, fs2_w0=w0, fs2_v=vv, fs2_t=t, fs2_tr=None))
check('summary: all as named -> PASS, B9a PASS', word == 'PASS' and 'B9a members (1) PASS, (2) PASS -> PASS' in txt, txt[-300:])
nst = rd('fs2_w0', 'W0', dict(case='s_w0n', w0_lines=['--- Error ---']))
check('summary: fs2_w0 NO STOP -> FAIL', R.summary(dict(fs2_w=w, fs2_w0=nst, fs2_v=vv, fs2_t=t))[1] == 'FAIL')
bad = rd('fs2_v', 'V', dict(case='s_vb', extra={3000: ['ASSERT: z']}))
txt, word = R.summary(dict(fs2_w=w, fs2_w0=w0, fs2_v=bad, fs2_t=t))
check('summary: B9a member fails on fs2_v -> FAIL and "FS2d does not install FS2"', word == 'FAIL' and 'FS2d does not install FS2' in txt, txt[-300:])
txt, word = R.summary(dict(fs2_w=w, fs2_w0=w0, fs2_v=vv, fs2_t=rd('fs2_t', 'T', T('s_tf', extra={3000: ['ASSERT: z']}))))
check('summary: timestop FAIL -> FAIL and "FS2d does not install FS2"', word == 'FAIL' and 'FS2d does not install FS2' in txt)
check('summary: fs2_v missing -> NOT EVALUABLE', R.summary(dict(fs2_w=w, fs2_w0=w0, fs2_v=None, fs2_t=t))[1] == 'NOT EVALUABLE')
inv = rd('fs2_w', 'W', dict(case='s_winv', fixb9a=0))
txt, word = R.summary(dict(fs2_w=inv, fs2_w0=w0, fs2_v=vv, fs2_t=t))
check('summary: fs2_w INVALID -> NOT EVALUABLE, B9a (1) NOT EVALUABLE', word == 'NOT EVALUABLE' and 'members (1) NOT EVALUABLE' in txt, txt[-300:])
fw = rd('fs2_w', 'W', dict(case='s_wf', fixmin=0))
check('summary: fs2_w FAIL (FixMinimize) -> FAIL, B9a PASS', R.summary(dict(fs2_w=fw, fs2_w0=w0, fs2_v=vv, fs2_t=t))[1] == 'FAIL'
      and '-> PASS' in R.summary(dict(fs2_w=fw, fs2_w0=w0, fs2_v=vv, fs2_t=t))[0])
kt = rd('fs2_t', 'T', T('s_tk', big={1000: 150000, 2000: 150000}))
check('summary: fs2_t K3 OVER, fs2_tr PASS -> PASS', R.summary(dict(fs2_w=w, fs2_w0=w0, fs2_v=vv, fs2_t=kt, fs2_tr=t))[1] == 'PASS')

# ---- json round trip and stop-check by file ----
jp = os.path.join(TMP, 'w.read.json')
with open(jp, 'w', encoding='ascii') as f:
    json.dump(w, f, indent=1, default=str)
out = subprocess.run([sys.executable, TGT, '--stop-check', jp], capture_output=True, env=dict((k, v2) for k, v2 in os.environ.items()
                                                                                              if k != 'PYTHONIOENCODING'))
check('--stop-check by file (subprocess) -> continue: fs2_w PASS', out.stdout.decode('ascii').strip().startswith('continue: fs2_w PASS'), out)
check('--stop-check missing file -> stop: no reading', subprocess.run([sys.executable, TGT, '--stop-check', jp + '.none'],
                                                                      capture_output=True).stdout.decode('ascii').startswith('stop: no reading'))

# ---- seal check ----
pred = os.path.join(TMP, 'pred.md')
names = list(R.SEALED)
with open(pred, 'w', newline='\n') as f:
    for n in names:
        p = n if n.startswith('C:/') else os.path.join(HERE, n)
        f.write('seal: %s %s\n' % (sha(p) if os.path.isfile(p) else '0' * 64, n))
okc, lines = R.check_seal(pred, HERE)
miss = [n for n in names if not os.path.isfile(n if n.startswith('C:/') else os.path.join(HERE, n))]
check('check-seal: every name present with its sha -> OK (files present now: missing %s)' % miss, okc == (not miss), lines[-3:])
with open(pred, 'a', newline='\n') as f:
    f.write('seal: %s fs2_read.py\n' % ('0' * 64))
check('check-seal: a second line for one name / a wrong sha -> FAILED', not R.check_seal(pred, HERE)[0])

# ---- strict cp1250 output (no PYTHONIOENCODING) of every mode that prints ----
env = dict((k, v2) for k, v2 in os.environ.items() if k != 'PYTHONIOENCODING')
env['PYTHONIOENCODING'] = 'cp1250:strict'
out = subprocess.run([sys.executable, TGT, '--stop-rule', F5B], capture_output=True, env=env)
check('--stop-rule under cp1250:strict -> rc 0, ASCII', out.returncode == 0 and all(b < 128 for b in out.stdout), (out.returncode, out.stderr[-200:]))
out = subprocess.run([sys.executable, TGT, '--tag', 'fs2_w', '--root', os.path.join(TMP, 'none')], capture_output=True, env=env)
check('--tag without a log under cp1250:strict -> rc 1, ASCII', out.returncode == 1 and all(b < 128 for b in out.stdout), out)
out = subprocess.run([sys.executable, TGT], capture_output=True, env=env)
check('usage under cp1250:strict -> rc 2, ASCII', out.returncode == 2 and all(b < 128 for b in out.stdout), out)
txt = R.text(rd('fs2_v', 'V', dict(case='c_v')))
check('text() of a read is ASCII', all(ord(c) < 128 for c in txt))
txt = R.text(rd('fs2_t', 'T', T('c_t')))
check('text() of a timestop read is ASCII', all(ord(c) < 128 for c in txt))

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d' % NCHK)
print('ALL OK' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
