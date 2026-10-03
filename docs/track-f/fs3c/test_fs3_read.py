"""Fixtures of fs3_read.py (FS3c, HPP-449): every member row and its edges on synthetic logs, the FixB42Ext line and the EXT
reference of the lead line 417cc2d8 (SHOWN / NOT_DETERMINED with the edges of the phase and of the base), the cp1250 output of the
reader without PYTHONIOENCODING, and the regression on the real log of F9g f9g_v1 (numbers of docs/track-f/f9g/read_f9g_v1.txt:
sha 4a55c7f2..., 1 177 398 lines, 272 FixB42 lines, no FixB42Ext line, offset 30, last present 10 016, video index 10 014).
Last line: ALL OK.
usage: python test_fs3_read.py [--no-real]"""
import hashlib, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fs3_read as R

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'fs3_read.py')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_fs3_read.py sha256 %s target fs3_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(TARGET)))
ok = True
n = 0
TMP = tempfile.mkdtemp(prefix='fs3_fx_')


def check(name, cond, info=''):
    global ok, n
    n += 1
    if not cond:
        ok = False
        print('FAIL %s %s' % (name, info))


def fix(mode, hit, app, ext=(960, 540), drawn=0, rearm=0, ha=None, lf=100, clear='00000000/00000000'):
    return ('FixB42: mode=%d hit=%d applied=%d drawn=%d rearm=%d hit_all=%d last_frame=%d extent=%dx%d cmask=0x571728000 clear=%s'
            % (mode, hit, app, drawn, rearm, hit if ha is None else ha, lf, ext[0], ext[1], clear))


def xl(mode, hit, app, ext=(960, 540), drawn=0, rearm=0, frame=100):
    return ('FixB42Ext: mode=%d extent=%dx%d hit=%d applied=%d drawn=%d rearm=%d frame=%d'
            % (mode, ext[0], ext[1], hit, app, drawn, rearm, frame))


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


def rd(name, lines, kind, idx=3000, stdout=('ok',)):
    p = mk(name, lines, stdout=list(stdout) if stdout is not None else None, idx=idx)
    return R.read(p, p + '.stdout', p + '.idx', kind)


def txt(r):
    return '\n'.join(R.rows('t', r))


def phased(before, after, at_present=5951, fix_before=()):
    """A log with offset 20 (present 22 at n 2): lines 'before' at present 1020, lines 'after' at present at_present."""
    L = base({}, nmax=3)
    L.append(ft(1000))
    L.extend(list(fix_before) + list(before))
    L.append(ft(1000 + 1))   # before-lines get next n 1001 -> present 1021
    L.append(ft(at_present - 20 - 1))
    L.extend(after)
    L.append(ft(at_present - 20))   # after-lines get next n -> present at_present
    return L


# 1. healthy u: FixB42 + FixB42Ext on 960x540, offset present - n = 22 - 2 = 20
r = rd('u_ok', base({5: [fix(1, 1, 1), xl(1, 1, 1)], 9: [fix(1, 2, 2), fix(1, 1, 1, ext=(480, 270))]}), 'u')
t = txt(r)
check('u_ok offset', r['offset'] == 20, r['offset'])
check('u_ok ext line', r['ext_lines'] == 1 and r['ext_t6'][0]['present'] == 25 and r['ext_t6'][0]['frame'] == 100, r['ext_t6'])
check('u_ok ext extents', r['ext_extents'] == {'960x540': dict(hit=1, applied=1, drawn=0, rearm=0, lines=1)}, r['ext_extents'])
check('u_ok extents', r['extents'] == {'480x270': dict(hit=1, applied=1, drawn=0, rearm=0), '960x540': dict(hit=2, applied=2, drawn=0, rearm=0)}, r['extents'])
check('u_ok no violations', r['t6_violations'] == [])
check('u_ok entry', r['entry_line'] == 3, r['entry_line'])
check('u_ok first scene n', r['first_scene_n'] == 2, r['first_scene_n'])
check('u_ok modes', r['modes'] == [1] and r['ext_modes'] == [1])
check('u_ok row mode YES', 'ROW FixB42 lines mode=1 (>= 1 line, all of the expected mode): YES' in t)
check('u_ok row ext present YES', 'ROW reference: FixB42Ext extent=960x540 line present: YES' in t)
check('u_ok row video YES', 'ROW video index records >= 3000: YES' in t)
check('u_ok row hit0 NO', 'hit = 0 at the default) - question to the lead: NO' in t)
check('u_ok row gamepatch 0 YES', 'ROW GamePatch lines 0: YES' in t)
check('u_ok ext ref only approach -> NOT_DETERMINED', r['ext_ref'] == 'NOT_DETERMINED' and 'EXT reference' in t)

# 2. idx 2999 -> video row NO
check('idx 2999 row NO', 'ROW video index records >= 3000: NO' in txt(rd('u_2999', base({5: [fix(1, 1, 1)]}), 'u', idx=2999)))

# 3. EXT reference (lead line 417cc2d8)
r = rd('x_shown', phased([xl(1, 1, 1)], [xl(1, 2, 2, frame=900)]), 'u')
check('x shown', r['ext_ref'] == 'SHOWN' and r['ext_ref_info']['base'] == 1 and r['ext_ref_info']['line']['present'] == 5951,
      (r['ext_ref'], r['ext_ref_info']))
check('x shown phase static', r['ext_ref_info']['line']['phase'] == 'static')
check('x shown row text', 'growth of applied of 960x540 in the static phase: SHOWN' in txt(r))
r = rd('x_equal', phased([xl(1, 1, 1)], [xl(1, 2, 1)]), 'u')
check('x applied equal to base -> NOT_DETERMINED', r['ext_ref'] == 'NOT_DETERMINED', r['ext_ref'])
r = rd('x_nobase', phased([], [xl(1, 1, 1)]), 'u')
check('x no line before -> base 0 -> SHOWN', r['ext_ref'] == 'SHOWN' and r['ext_ref_info']['base'] == 0)
r = rd('x_edge5950', phased([xl(1, 1, 1)], [xl(1, 2, 2)], at_present=5950), 'u')
check('x present 5950 (steps) -> NOT_DETERMINED', r['ext_ref'] == 'NOT_DETERMINED' and r['ext_t6'][1]['phase'] == 'steps',
      (r['ext_ref'], r['ext_t6']))
r = rd('x_none', phased([], []), 'u')
check('x no ext line -> NOT_DETERMINED', r['ext_ref'] == 'NOT_DETERMINED' and r['ext_ref_var'] == 'NOT_DETERMINED')
check('x no ext line -> ext present row NO', 'ROW reference: FixB42Ext extent=960x540 line present: NO' in txt(r))
r = rd('x_var', phased([xl(1, 1, 1)], [xl(1, 2, 2)], fix_before=[fix(1, 3, 3, ha=3)]), 'u')
check('x variant base from FixB42 line', r['ext_ref'] == 'SHOWN' and r['ext_ref_var'] == 'NOT_DETERMINED'
      and r['ext_ref_var_info']['base'] == 3, (r['ext_ref'], r['ext_ref_var'], r['ext_ref_var_info']))
r = rd('x_other', phased([xl(1, 1, 1)], [xl(1, 5, 5, ext=(480, 270))]), 'u')
check('x other extent after -> NOT_DETERMINED', r['ext_ref'] == 'NOT_DETERMINED')
L = [x for x in phased([xl(1, 1, 1)], [xl(1, 2, 2)]) if 'InputScript' not in x]
r = rd('x_noin', L, 'u')
check('x no input -> NOT_DETERMINED', r['offset'] is None and r['ext_ref'] == 'NOT_DETERMINED')
r = rd('x_two_after', phased([xl(1, 1, 1)], [xl(1, 2, 1), xl(1, 3, 2)]), 'u')
check('x second after-line shown', r['ext_ref'] == 'SHOWN' and r['ext_ref_info']['line']['applied'] == 2)
r = rd('x_pu', phased([xl(1, 1, 1)], [xl(1, 2, 2)]) + ['GamePatch: applied sha=x pokes=2'], 'pu')
check('x pu has the EXT row', 'EXT reference' in txt(r))
check('x w has no EXT row', 'EXT reference' not in txt(rd('x_w', phased([xl(1, 1, 1)], [xl(1, 2, 2)]), 'w', idx=None)))

# 4. torn ext line, mode mismatch via ext
r = rd('x_torn', base({5: [fix(1, 1, 1), 'FixB42Ext: mode=1 extent=960x5']}), 'u')
check('ext torn 1', r['ext_torn'] == 1 and r['ext_lines'] == 0 and r['fix_lines'] == 1)
r = rd('x_mode', base({5: [fix(1, 1, 1), xl(0, 1, 0)]}), 'u')
check('ext mode 0 in u -> FORM ERROR', 'FORM ERROR' in txt(r) and 'mode=1 (>= 1 line, all of the expected mode): NO' in txt(r))
check('FixB42Ext not counted as FixB42', r['fix_lines'] == 1 and r['ext_lines'] == 1)

# 5. violation and drawn (reference rows)
r = rd('u_viol', base({5: [fix(1, 1, 1)], 9: [fix(1, 3, 2)]}), 'u')
check('viol count 1', len(r['t6_violations']) == 1, r['t6_violations'])
r = rd('u_eq', base({5: [fix(1, 1, 1)], 9: [fix(1, 3, 3)]}), 'u')
check('equal growth no violation', r['t6_violations'] == [])
r = rd('u_xviol', base({5: [xl(1, 1, 1)], 9: [xl(1, 3, 2)]}), 'u')
check('ext viol counted per kind', len(r['t6_violations']) == 1 and r['t6_violations'][0]['kind'] == 'ext')
check('drawn row YES', 'T6 got a draw; question to the lead: YES' in txt(rd('u_drawn', base({5: [fix(1, 1, 1, drawn=1)]}), 'u')))
check('drawn other extent NO', 'T6 got a draw; question to the lead: NO' in txt(rd('u_drawn2', base({5: [fix(1, 1, 1), fix(0, 0, 0, ext=(480, 270), drawn=3)]}), 'u')))

# 6. hit = 0 reference row
t = txt(rd('u_nohit', base({}), 'u'))
check('no line -> hit0 row YES', 'hit = 0 at the default) - question to the lead: YES' in t)
check('no line -> mode row NO', 'ROW FixB42 lines mode=1 (>= 1 line, all of the expected mode): NO' in t)

# 7. u0: C0 line by FixB42 or by FixB42Ext
r = rd('u0', base({5: [fix(0, 1, 0)], 9: [fix(0, 4, 0)]}), 'u0')
check('u0 c0 line fix', r['c0_line'] is not None and r['c0_line']['kind'] == 'fix')
check('u0 row YES', 'ROW C0 line: mode=0 extent=960x540 hit >= 1 applied=0: YES' in txt(r))
check('u0 mode row YES', 'ROW FixB42 lines mode=0 (>= 1 line, all of the expected mode): YES' in txt(r))
r = rd('u0_ext', base({5: [fix(0, 1, 1, ext=(480, 270)), xl(0, 1, 0)]}), 'u0')
check('u0 c0 line ext', r['c0_line'] is not None and r['c0_line']['kind'] == 'ext')
check('u0 applied 1 -> none', rd('u0_app', base({5: [fix(0, 1, 1)]}), 'u0')['c0_line'] is None)
check('u0 other extent -> none', rd('u0_480', base({5: [fix(0, 1, 0, ext=(480, 270))]}), 'u0')['c0_line'] is None)
check('u0 mode 1 -> FORM ERROR', 'FORM ERROR' in txt(rd('u0_form', base({5: [fix(1, 1, 1)]}), 'u0')))
check('u0 has no EXT row', 'EXT reference' not in txt(r))

# 8. frames >= 1 s: before the first scene frame not counted, after counted; edge 999 999 not counted; scene change
r = rd('k2', base({}, dt_at={10: 1000000, 11: 999999}), 'u')
check('k2 one row', len(r['k2_after']) == 1 and r['k2_after'][0][0] == 10, r['k2_after'])
L = base({})
L.insert(5, ft(0, dt=5000000, draws=10))
r = rd('k2_load', L, 'u')
check('k2 load row not counted', r['k2_after'] == [] and r['ft_all_k2'] == 1)
r = rd('k2_change', base({20: ['GuestOut: Level has started: other_level']}, dt_at={25: 2000000}), 'u')
check('k2 after scene change not counted', r['k2_after'] == [] and r['scene_change_line'] is not None)
check('hb k2 row marked reference', '(reference for hb)' in txt(rd('hb_k2', base({}, level='hoover_beach'), 'hb')))

# 9. death markers, stdout
r = rd('death', base({7: ['--- Fatal Error ---']}), 'u', stdout=['Unhandled exception: x'])
check('death log+stdout', len(r['death']) == 2 and 'ROW 0 death markers: NO' in txt(r), r['death'])
r = rd('nostdout', base({}), 'u', stdout=None)
check('stdout missing flagged', r['stdout_present'] is False)

# 10. W rows
r = rd('w_ok', base({5: [fix(1, 1, 1), '[Vulkan][W][2] something']}), 'w', idx=None)
t = txt(r)
check('w vke 0 YES', 'ROW W: 0 [Vulkan][E]: YES' in t)
check('w active YES', 'ROW W: validation active: YES' in t)
check('w dual YES', 'before the first GuestOut: YES' in t)
check('w mode YES', 'ROW FixB42 lines mode=1 (>= 1 line, all of the expected mode): YES' in t)
check('w no video row', 'video index records >= 3000' not in t)
L = base({5: ['[Vulkan][E][2] VUID-x']})
L[0] = 'nothing'
L.insert(4, 'DualSrcBlend: supported=1 enabled=1')
t = txt(rd('w_bad', L, 'w', idx=None))
check('w vke 1 NO', 'ROW W: 0 [Vulkan][E]: NO' in t)
check('w dual after GuestOut NO', 'before the first GuestOut: NO' in t)
check('w no FixB42 -> mode row NO', 'mode=1 (>= 1 line, all of the expected mode): NO' in t)
L = base({})
L[0] = 'DualSrcBlend: supported=1 enabled=0'
check('w dual enabled=0 NO', rd('w_dual0', L, 'w', idx=None)['dual_ok'] is False)
check('w no validation lines -> active NO', 'ROW W: validation active: NO' in txt(rd('w_noval', base({5: [fix(1, 1, 1)]}), 'w', idx=None)))

# 11. hold for w/v/hb: 300 s edge
L = base({}, nmax=3)
L += [ft(3, dt=150000000), ft(4, dt=149999999)]
check('hold 299.99 s NO', 'ROW hold >= 300 s (sum dt after the first scene frame): NO' in txt(rd('v_short', L, 'v')))
L[-1] = ft(4, dt=150000000)
check('hold 300.0 s YES', 'ROW hold >= 300 s (sum dt after the first scene frame): YES' in txt(rd('v_edge', L, 'v')))
check('w hold row exists', 'ROW hold >= 300 s' in txt(rd('w_hold', L, 'w', idx=None)))
check('u no hold row', 'ROW hold >= 300 s' not in txt(rd('u_hold', L, 'u')))
check('hb wrong level not entered', rd('hb_wrong', base({}), 'hb')['entry_line'] is None)
check('hb level entered', rd('hb_ok', base({}, level='hoover_beach'), 'hb')['entry_line'] is not None)

# 12. GamePatch: 0 expected outside pu; pu applied / refused
t = txt(rd('gp_u', base({5: ['GamePatch: applied sha=x']}), 'u'))
check('gamepatch in u -> row NO', 'ROW GamePatch lines 0: NO' in t)
r = rd('gp_pu', base({5: ['GamePatch: file x', 'GamePatch: applied sha=x pokes=2', fix(1, 1, 1)]}), 'pu')
check('pu applied 1', r['gp_applied'] == 1 and r['gamepatch'] == 2 and 'GamePatch applied >= 1 and refused 0: YES' in txt(r))
check('pu no GamePatch-0 row', 'ROW GamePatch lines 0' not in txt(r))
r = rd('gp_pu_ref', base({5: ['GamePatch: refused reason=sha']}), 'pu')
check('pu refused -> row NO', r['gp_refused'] == 1 and 'GamePatch applied >= 1 and refused 0: NO' in txt(r))

# 13. window lines, phases, kind_of, paths
r = rd('misc', base({5: ['Window 1 minimized', 'Recovering Vulkan swapchain']}), 'u')
check('window', r['win'] == {'minimized': 1} and r['recovering'] == 1 and 'Recovering Vulkan swapchain (else not read as an outcome, question to the lead): NO' in txt(r))
check('window focus only -> row YES', 'question to the lead): YES' in txt(rd('focus', base({5: ['Window 1 lost keyboard focus']}), 'u')))
check('phase edges', [R.phase(x) for x in (3840, 3841, 5850, 5851, 5950, 5951, None)] ==
      ['approach', 'rotation', 'rotation', 'steps', 'steps', 'static', 'unknown'])
check('kind_of', [R.kind_of(x) for x in ('fs3_w', 'fs3_v', 'fs3_u', 'fs3_u0', 'fs3_u0r', 'fs3_hb', 'fs3_pu')] ==
      ['w', 'v', 'u', 'u0', 'u0', 'hb', 'pu'])
check('paths w no idx', R.paths('fs3_w', 'w')['idx'] is None and R.paths('fs3_w', 'w')['log'].endswith('log_fs3_w.txt'))
check('paths u runs', R.paths('fs3_u', 'u')['log'].replace(os.sep, '/').endswith('runs/fs3_u/log.txt'))
check('modes table', R.MODE == {'u': 1, 'u0': 0, 'pu': 1, 'w': 1, 'v': 1, 'hb': 1})

# 14. cp1250 output without PYTHONIOENCODING
env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
env['PYTHONIOENCODING'] = 'cp1250:strict'
pr = subprocess.run([sys.executable, TARGET, '--log', os.path.join(TMP, 'x_shown'), '--tag-kind', 'u'], capture_output=True, env=env)
check('cp1250 strict rc 0', pr.returncode == 0, pr.stderr[-300:])
check('ascii output', all(b < 128 for b in pr.stdout))

# 15. regression on the real log of F9g f9g_v1 (F9e2c 24efead3 at KYTY_FIX_B42=1, no FixB42Ext line in that binary)
if '--no-real' not in sys.argv:
    d = 'C:/kyty/f287/f9/f9g/runs/f9g_v1/'
    r = R.read(d + 'log.txt', d + 'stdout.txt', d + 'rec.mp4.idx', 'u')
    check('real sha', r['log_sha256'] == '4a55c7f2f786fa76d7d2a62ba972e7863f039bfa069a0e76e1b3b6a7ccdc0554', r['log_sha256'])
    check('real lines', r['log_lines'] == 1177398, r['log_lines'])
    check('real fix 272 ext 0', r['fix_lines'] == 272 and r['ext_lines'] == 0, (r['fix_lines'], r['ext_lines']))
    check('real offset 30 last 10016', r['offset'] == 30 and r['last_present'] == 10016, (r['offset'], r['last_present']))
    check('real idx 10014', r['idx_records'] == 10014)
    check('real entry 224563', r['entry_line'] == 224563 and r['first_scene_n'] == 193)
    check('real hit_all 339 skipped 2', r['hit_all_max'] == 339 and r['skipped_draw'] == 2)
    check('real k2 0 max 183533', r['k2_after'] == [] and r['dt_max_all'] == 183533)
    check('real death 0 gamepatch 0', r['death'] == [] and r['gamepatch'] == 0)
    check('real ext ref NOT_DETERMINED', r['ext_ref'] == 'NOT_DETERMINED')
print('checks %d' % n)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
