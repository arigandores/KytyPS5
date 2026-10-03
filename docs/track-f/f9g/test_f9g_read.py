"""Fixtures of f9g_read.py (F9g, HPP-424): every member row and its edges on synthetic logs, the cp1250 output of the reader
without PYTHONIOENCODING, and the regression on the real log of F9d f9d_2 (numbers of docs/track-f/f9d.md: no FixB42 line,
AsyncPipelines: skipped draw 2, frames >= 1 s 0 with max dt_us 214 996, video index 10 232).  Last line: ALL OK.
usage: python test_f9g_read.py [--no-real]"""
import hashlib, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f9g_read as R

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'f9g_read.py')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f9g_read.py sha256 %s target f9g_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(TARGET)))
ok = True
n = 0
TMP = tempfile.mkdtemp(prefix='f9g_fx_')


def check(name, cond, info=''):
    global ok, n
    n += 1
    if not cond:
        ok = False
        print('FAIL %s %s' % (name, info))


def fix(mode, hit, app, ext=(960, 540), drawn=0, rearm=0, ha=None, lf=100, clear='00000000/00000000'):
    return ('FixB42: mode=%d hit=%d applied=%d drawn=%d rearm=%d hit_all=%d last_frame=%d extent=%dx%d cmask=0x571728000 clear=%s'
            % (mode, hit, app, drawn, rearm, hit if ha is None else ha, lf, ext[0], ext[1], clear))


def ft(nn, dt=16667, draws=3000):
    return 'FrameTrace: n=%d dt_us=%d lat_us=1 draws=%d draw_us=0' % (nn, dt, draws)


def mk(name, lines, stdout=None, idx=None):
    p = os.path.join(TMP, name)
    with open(p, 'wb') as f:
        f.write(('\n'.join(lines) + '\n').encode())
    if stdout is not None:
        with open(p + '.stdout', 'wb') as f:
            f.write(('\n'.join(stdout) + '\n').encode())
    if idx is not None:
        with open(p + '.idx', 'wb') as f:
            f.write(''.join('%d %d 0.0\n' % (i, i + 1) for i in range(idx)).encode())
    return p


def base(extra_mid, level='underwater_aerial_garden', n0=1, nmax=40, extra_start=(), dt_at=None):
    L = ['DualSrcBlend: supported=1 enabled=1'] + list(extra_start) + ['GuestOut: Level has started: ',
                                                                       'GuestOut: Level has started: ' + level]
    L.append(ft(n0, draws=50))
    L.append('InputScript: press w at 1.00 s (present 22)')
    for i in range(n0 + 1, nmax):
        if i in extra_mid:
            L.extend(extra_mid[i])
        L.append(ft(i, dt=(dt_at or {}).get(i, 16667)))
    return L


# 1. healthy V: growth of applied on 960x540, offset present - n = 22 - 2 = 20
p = mk('v_ok', base({5: [fix(1, 1, 1)], 9: [fix(1, 2, 2), fix(1, 1, 1, ext=(480, 270))]}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('v_ok offset', r['offset'] == 20, r['offset'])
check('v_ok first applied', r['t6_first_applied'] is not None and r['t6_first_applied']['line'] > 0, r['t6_first_applied'])
check('v_ok present of first applied', r['t6_first_applied']['present'] == 25, r['t6_first_applied'])
check('v_ok no violations', r['t6_violations'] == [])
check('v_ok extents', r['extents'] == {'480x270': dict(hit=1, applied=1, drawn=0, rearm=0), '960x540': dict(hit=2, applied=2, drawn=0, rearm=0)}, r['extents'])
check('v_ok idx 3000', r['idx_records'] == 3000)
check('v_ok entry', r['entry_line'] == 3, r['entry_line'])
check('v_ok first scene n', r['first_scene_n'] == 2, r['first_scene_n'])
check('v_ok death 0', r['death'] == [])
check('v_ok modes', r['modes'] == [1])
txt = '\n'.join(R.rows('t', r))
check('v_ok row int YES', 'ROW (g)(1)-int: line 960x540 with growth of applied (<= last present): YES' in txt)
check('v_ok row viol YES', 'ROW (g)(1)-int: growth hit <= growth applied between 960x540 lines: YES' in txt)
check('v_ok row hit0 NO', 'NOT READABLE, one repeat: NO' in txt)
check('v_ok row video YES', 'ROW video index records >= 3000: YES' in txt)

# 2. edge: idx 2999 -> video row NO
p = mk('v_2999', base({5: [fix(1, 1, 1)]}), stdout=['ok'], idx=2999)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('idx 2999 row NO', 'ROW video index records >= 3000: NO' in '\n'.join(R.rows('t', r)))

# 3. violation: hit grows by 2, applied by 1 between lines; first line from zero hit 1 applied 0 -> violation too
p = mk('v_viol', base({5: [fix(1, 1, 0)], 9: [fix(1, 3, 2)]}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('viol count 1', len(r['t6_violations']) == 1, r['t6_violations'])
check('viol first applied is line 2', r['t6_first_applied'] and r['t6_first_applied']['applied'] == 2)
p = mk('v_viol2', base({5: [fix(1, 1, 1)], 9: [fix(1, 3, 2)]}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('viol edge d_hit 2 d_app 1', len(r['t6_violations']) == 1)
p = mk('v_eq', base({5: [fix(1, 1, 1)], 9: [fix(1, 3, 3)]}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('equal growth no violation', r['t6_violations'] == [])
# another extent does not count against 960x540
p = mk('v_other', base({5: [fix(1, 1, 1)], 7: [fix(1, 5, 0, ext=(480, 270), ha=6)], 9: [fix(1, 2, 2, ha=7)]}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('other extent ignored', r['t6_violations'] == [] and r['hit_all_max'] == 7, (r['t6_violations'], r['hit_all_max']))

# 4. hit = 0: no line at all -> NOT READABLE YES
p = mk('v_nohit', base({}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
t = '\n'.join(R.rows('t', r))
check('no hit -> NOT READABLE YES', 'NOT READABLE, one repeat: YES' in t)
check('no hit -> int row NO', 'growth of applied (<= last present): NO' in t)

# 5. drawn > 0 on 960x540
p = mk('v_drawn', base({5: [fix(1, 1, 1)], 9: [fix(1, 1, 1, drawn=1)]}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('drawn row YES', 'T6 got a draw; question to the lead: YES' in '\n'.join(R.rows('t', r)))
p = mk('v_drawn_other', base({5: [fix(1, 1, 1)], 9: [fix(0, 0, 0, ext=(480, 270), drawn=3)]}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('drawn other extent row NO', 'T6 got a draw; question to the lead: NO' in '\n'.join(R.rows('t', r)))

# 6. C0
p = mk('c0', base({5: [fix(0, 1, 0)], 9: [fix(0, 4, 0)]}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'c0')
check('c0 line', r['c0_line'] is not None and r['c0_line']['hit'] == 1)
check('c0 row YES', 'ROW (g)(2)-C0: line mode=0 extent=960x540 hit >= 1 applied=0: YES' in '\n'.join(R.rows('t', r)))
p = mk('c0_app', base({5: [fix(0, 1, 1)]}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'c0')
check('c0 applied 1 -> no c0 line', r['c0_line'] is None)
p = mk('c0_480', base({5: [fix(0, 1, 0, ext=(480, 270))]}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'c0')
check('c0 other extent -> no c0 line', r['c0_line'] is None)
# form error: a mode=1 line in C0
t = '\n'.join(R.rows('t', R.read(mk('c0_form', base({5: [fix(1, 1, 1)]}), stdout=['ok'], idx=3000),
                                    os.path.join(TMP, 'c0_form.stdout'), os.path.join(TMP, 'c0_form.idx'), 'c0')))
check('c0 mode 1 -> FORM ERROR', 'FORM ERROR' in t)

# 7. frames >= 1 s: before the first scene frame not counted, after counted; edge 999 999 not counted
p = mk('k2', base({}, dt_at={10: 1000000, 11: 999999}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('k2 one row', len(r['k2_after']) == 1 and r['k2_after'][0][0] == 10, r['k2_after'])
L = base({})
L.insert(5, ft(0, dt=5000000, draws=10))   # a load row before the first scene frame (draws < 100)
p = mk('k2_load', L, stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('k2 load row not counted', r['k2_after'] == [] and r['ft_all_k2'] == 1, (r['k2_after'], r['ft_all_k2']))
# after a scene change not counted
L = base({20: ['GuestOut: Level has started: other_level']}, dt_at={25: 2000000})
p = mk('k2_change', L, stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('k2 after scene change not counted', r['k2_after'] == [] and r['scene_change_line'] is not None)

# 8. death markers in log and stdout
p = mk('death', base({7: ['--- Fatal Error ---']}), stdout=['Unhandled exception: x'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('death log+stdout', len(r['death']) == 2, r['death'])
p = mk('nostdout', base({}), idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('stdout missing flagged', r['stdout_present'] is False)

# 9. W rows
p = mk('w_ok', base({5: [fix(1, 1, 1), '[Vulkan][W][2] something']}), stdout=['ok'])
r = R.read(p, p + '.stdout', p + '.idx', 'w')
t = '\n'.join(R.rows('t', r))
check('w vke 0 YES', 'ROW W: 0 [Vulkan][E]: YES' in t)
check('w active YES', 'ROW W: validation active: YES' in t)
check('w dual YES', 'before the first GuestOut: YES' in t)
check('w hit YES', 'ROW W: hit >= 1 (hit_all): YES' in t)
L = base({5: ['[Vulkan][E][2] VUID-x']})
L[0] = 'nothing'
L.insert(4, 'DualSrcBlend: supported=1 enabled=1')    # after the first GuestOut
p = mk('w_bad', L, stdout=['ok'])
r = R.read(p, p + '.stdout', p + '.idx', 'w')
t = '\n'.join(R.rows('t', r))
check('w vke 1 NO', 'ROW W: 0 [Vulkan][E]: NO' in t and r['vke'] == 1)
check('w dual after GuestOut NO', 'before the first GuestOut: NO' in t)
check('w hit 0 NOT READABLE', 'NOT READABLE, one repeat: YES' in t)
L = base({})
L[0] = 'DualSrcBlend: supported=1 enabled=0'
r = R.read(mk('w_dual0', L, stdout=['ok']), os.path.join(TMP, 'w_dual0.stdout'), None, 'w')
check('w dual enabled=0 NO', r['dual_ok'] is False)

# 10. hold for sg/hb: 300 s edge
L = base({}, nmax=3)
L += [ft(3, dt=150000000), ft(4, dt=149999999)]
r = R.read(mk('sg_short', L, stdout=['ok'], idx=3000), os.path.join(TMP, 'sg_short.stdout'), os.path.join(TMP, 'sg_short.idx'), 'sg')
check('hold 299.99 s NO', 'ROW hold >= 300 s (sum dt after the first scene frame): NO' in '\n'.join(R.rows('t', r)), r['hold_s'])
L[-1] = ft(4, dt=150000000)
r = R.read(mk('sg_edge', L, stdout=['ok'], idx=3000), os.path.join(TMP, 'sg_edge.stdout'), os.path.join(TMP, 'sg_edge.idx'), 'sg')
check('hold 300.0 s YES', ('ROW hold >= 300 s (sum dt after the first scene frame): YES' in '\n'.join(R.rows('t', r))), r['hold_s'])
r = R.read(mk('hb_wrong', base({}, level='underwater_aerial_garden'), stdout=['ok'], idx=3000), os.path.join(TMP, 'hb_wrong.stdout'), os.path.join(TMP, 'hb_wrong.idx'), 'hb')
check('hb wrong level not entered', r['entry_line'] is None)

# 11. torn FixB42 line, phases, GamePatch, window lines
p = mk('misc', base({5: ['FixB42: mode=1 hit=1 appl', 'GamePatch: x', 'Window 1 minimized', 'Recovering Vulkan swapchain']}), stdout=['ok'], idx=3000)
r = R.read(p, p + '.stdout', p + '.idx', 'v')
check('torn 1', r['fix_torn'] == 1 and r['fix_lines'] == 0)
check('gamepatch 1', r['gamepatch'] == 1)
check('window', r['win'] == {'minimized': 1} and r['recovering'] == 1)
check('phase edges', [R.phase(x) for x in (3840, 3841, 5850, 5851, 5950, 5951, None)] ==
      ['approach', 'rotation', 'rotation', 'steps', 'steps', 'static', 'unknown'])
check('kind_of', [R.kind_of(x) for x in ('f9g_v1', 'f9g_v2r', 'f9g_c0r', 'f9g_w', 'f9g_wr', 'f9g_sg', 'f9g_hb')] ==
      ['v', 'v', 'c0', 'w', 'w', 'sg', 'hb'])
# no InputScript line -> present None, phase unknown
L = [x for x in base({5: [fix(1, 1, 1)]}) if 'InputScript' not in x]
r = R.read(mk('noin', L, stdout=['ok'], idx=3000), os.path.join(TMP, 'noin.stdout'), os.path.join(TMP, 'noin.idx'), 'sg')
check('no input -> offset None', r['offset'] is None and r['t6_first_applied']['phase'] == 'unknown')

# 12. cp1250 output without PYTHONIOENCODING
env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
env['PYTHONIOENCODING'] = 'cp1250:strict'
pr = subprocess.run([sys.executable, TARGET, '--log', os.path.join(TMP, 'v_ok'), '--tag-kind', 'v'], capture_output=True, env=env)
check('cp1250 strict rc 0', pr.returncode == 0, pr.stderr[-300:])
check('ascii output', all(b < 128 for b in pr.stdout))

# 13. regression on the real log of F9d f9d_2 (4aa62e95, no fix code)
if '--no-real' not in sys.argv:
    d = 'C:/kyty/f287/f9/runs/f9d_2/'
    r = R.read(d + 'log.txt', d + 'stdout.txt', d + 'rec.mp4.idx', 'c0')
    check('real sha', r['log_sha256'] == 'b98ed851a30dd73bf5bcb57b05b67de22ba5cfddb75ab280d38aedb8ed334215', r['log_sha256'])
    check('real lines', r['log_lines'] == 1507088, r['log_lines'])
    check('real no FixB42', r['fix_lines'] == 0)
    check('real skipped 2', r['skipped_draw'] == 2, r['skipped_draw'])
    check('real k2 0, max 214996', r['k2_after'] == [] and r['dt_max_all'] == 214996, (r['k2_after'], r['dt_max_all']))
    check('real idx 10232', r['idx_records'] == 10232)
    check('real entered', r['entry_line'] is not None and r['scene_change_line'] is None)
    check('real release 5945', r['release5945'] and r['offset'] == 23, r['offset'])
    check('real death 0 vke 0 gamepatch 0', r['death'] == [] and r['vke'] == 0 and r['gamepatch'] == 0)
print('checks %d' % n)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
