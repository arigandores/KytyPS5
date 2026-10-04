"""F19e (HPP-549): fixtures of f19e_read.py - every member of item 451 (d)(4), every identity and invariant of F19a section 6.1, every
admission row (with item 460 (d) N5) and edge of the seal docs/track-f/f19e.md section 4.  Ends with ALL OK.
usage: python test_f19e_read.py   (ASCII only)"""
import hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'f19e_read.py')
sys.path.insert(0, HERE)
import f19e_read as R

print('suite test_f19e_read.py sha256 %s target f19e_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(open(TARGET, 'rb').read()).hexdigest()))
N = [0]
FAIL = []


def check(name, cond):
    N[0] += 1
    if not cond:
        FAIL.append(name)
        print('FAIL', name)


GUEST = 'GuestOut: Level has started: underwater_aerial_garden'
PAD = 'Controller 0: "KYTY test pad" type=1 accel=0 gyro=0 path='
ALL = R.ORDER
STAND = ('b24_h0', 'b24_s0', 'b24_h1', 'b24_d0', 'b24_d1')


def fr(n, dt, draws=3000):
    return 'FrameTrace: n=%d dt_us=%d draws=%d' % (n, dt, draws)


def frames(k, dt=16000, start=100):
    return [fr(start + i, dt) for i in range(k)]


def default_stat(tag):
    sp = R.SPEC[tag]
    s = dict(main_late_max_us=3000000, probes_posted=300, probes_run=300, pad_vib=180, pad_led=2, pad_trig=1, pad_wait_max_us=120,
             po_applied=0, po_wait_max_us=0, guest_sdl=180, removed=0, vp_rumble=0, vp_led=1, vp_effect=0)
    if sp['mode'] == 'hold' and sp['fix'] == '0':
        s.update(pad_wait_max_us=2999000)
    if sp['fix'] == '1':
        s.update(po_applied=150, po_wait_max_us=500, guest_sdl=0)
        if sp['mode'] == 'hold':
            s.update(po_wait_max_us=2999000, pad_wait_max_us=40)
    if sp['mode'] == 'detach':
        s.update(main_late_max_us=20000, removed=1)
    return s


def stat_line(tag, **kw):
    s = default_stat(tag)
    s.update(kw)
    pc = s.pop('pad_calls', s['pad_vib'] + s['pad_led'] + s['pad_trig'])
    keys = ['main_late_max_us', 'probes_posted', 'probes_run']
    vals = ['%s=%d' % (k, s[k]) for k in keys] + ['pad_calls=%d' % pc]
    vals += ['%s=%d' % (k, s[k]) for k in R.STAT_KEYS[4:] if k in s]
    return 'TestHidLoss: stat mode=%s %s' % (s.pop('mode', R.SPEC[tag]['mode']), ' '.join(vals))


def mk_log(tag, fixlines=None, cfg=None, before=None, head=None, pre=None, win=None, post=None, extra=None, stat=None, armed=None,
           attach=None, pad=None, fire=None, done=None, removed=None, quit=True, t=(70, 75, 135, 138), order=None):
    sp = R.SPEC[tag]
    m = sp['mode']
    L = ['[3][00:00:01.000] start', '  version: Fork build arigandores/KytyPS5 52d2f54']
    L += fixlines if fixlines is not None else (['FixB24: mode=1'] if sp['fix'] == '1' else [])
    if m is not None:
        L += cfg if cfg is not None else ['TestHidLoss: config on delay_s=60 mode=%s hold_ms=3000' % m]
    L += before or []
    L += [GUEST] + (head if head is not None else [fr(1, 16000, 50), fr(2, 16000, 100)])
    L += pre if pre is not None else frames(60, start=3)
    if m is None:
        L += win if win is not None else frames(400, start=200)
    else:
        ta, tt, tf, td = t
        L += armed if armed is not None else ['TestHidLoss: armed t_us=%d' % (ta * 1000000)]
        L += frames(60, start=70)
        L += attach if attach is not None else ['TestHidLoss: attach index=0 t_us=%d' % (tt * 1000000)]
        L += pad if pad is not None else [PAD]
        L += frames(120, start=140)
        L += fire if fire is not None else ['TestHidLoss: fire mode=%s t_us=%d' % (m, tf * 1000000)]
        if win is not None:
            L += win
        elif m == 'hold' and sp['fix'] == '0':
            L += frames(3, start=300) + [fr(303, 3000000)] + frames(60, start=304)
        else:
            L += frames(200, start=300)
        L += done if done is not None else ['TestHidLoss: done t_us=%d' % (td * 1000000)]
        L += removed if removed is not None else (['Controller 0: removed'] if m == 'detach' else [])
        L += frames(120, start=600)
        L += stat if stat is not None else [stat_line(tag)]
    L += post if post is not None else frames(300, start=800)
    L += extra or []
    L += ['Window 1 closed'] + (['Event: quit'] if quit else [])
    return L


SEAL_TEXT = 'seal fixture text\n'


def run_json(tag, env=None, binary=None, prereg=None, **att):
    sp = R.SPEC[tag]
    a = dict(outcome='ok', hold_exit=None, hold_s=float(sp['hold']) + 0.2, close_posted=1, close_rc=0, close_killed=False, close_s=2.1,
             close_wait_s=40)
    a.update(att)
    e = {'KYTY_FIX_B24': sp['fix'], 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_REC': 'x', 'KYTY_FRAME_TRACE': 'lite'}
    if sp['mode'] is not None:
        e['KYTY_TEST_HIDLOSS'] = '60:%s' % sp['mode']
    if env:
        for k, v in env.items():
            if v is None:
                e.pop(k, None)
            else:
                e[k] = v
    return dict(binary_sha256=R.BIN_EXPECT if binary is None else binary, env=e, attempts=[a],
                prereg=dict(sha256=hashlib.sha256(SEAL_TEXT.encode()).hexdigest() if prereg is None else prereg))


T = tempfile.mkdtemp(prefix='f19e_fix_')
CNT = [0]


def case(tag, log=None, stdout=None, run=None, files=None, drop=(), idx=3100, seal=SEAL_TEXT, **lk):
    CNT[0] += 1
    d = os.path.join(T, 'c%03d' % CNT[0])
    os.makedirs(d)
    f = dict(installed_sha=R.BIN_EXPECT, installed_before=R.WANT, installed_after=R.WANT,
             warm='warm form: C:/x/variant present at 2026-10-04T12:00:00Z; entries 5', manifest_cmp='manifest cmp EQUAL files 2 listsha abc',
             glitch='one-frame glitches: 0', sheet='sheet: x.png frames 3100')
    f.update(files or {})
    for k, v in f.items():
        if k not in drop:
            open(os.path.join(d, k + '.txt'), 'w').write(v + '\n')
    if 'log' not in drop:
        open(os.path.join(d, 'log.txt'), 'wb').write(('\n'.join(log if log is not None else mk_log(tag, **lk)) + '\n').encode())
    if 'stdout' not in drop:
        open(os.path.join(d, 'stdout.txt'), 'wb').write(('\n'.join(stdout or ['Shaders: VS 1']) + '\n').encode())
    if 'run' not in drop:
        open(os.path.join(d, 'es.json'), 'w').write(json.dumps(run if run is not None else run_json(tag)))
    if 'idx' not in drop:
        open(os.path.join(d, 'rec.idx'), 'w').write('r\n' * idx)
    if 'seal' not in drop:
        open(os.path.join(d, 'seal.md'), 'wb').write(seal.encode())
    if 'bin' not in drop:
        open(os.path.join(d, 'bin.exe'), 'wb').write(b'MZ...' + R.VERSION + b'...')
    return d


def rd(tag, d):
    res = R.read(tag, R.paths(tag, d))
    return res['word'], res, R.rows(res)


def word(tag, **kw):
    return rd(tag, case(tag, **kw))[0]


def row(res, prefix, sub):
    for name, val in res[prefix]:
        if sub in name:
            return val
    raise KeyError(sub)


def st(tag, **kw):
    return [stat_line(tag, **kw)]


try:
    # positive tags
    for tg in ALL:
        w, res, out = rd(tg, case(tg))
        check('positive %s -> MEMBERS_PASS (got %s)' % (tg, w), w == 'MEMBERS_PASS')
        check('positive %s has READING line' % tg, out[-1] == '  READING %s MEMBERS_PASS' % tg)
        check('positive %s N3 line printed' % tg, any('sent= of PadTriggerEffect lines is not delivery - not read' in x for x in out))
    w, res, out = rd('b24_h0', case('b24_h0'))
    check('h0 the long frame n 303 in both windows', res['k2_wide'] == [303] and res['k2_strict'] == [303])
    w, res, out = rd('b24_h1', case('b24_h1'))
    check('h1 N1 notes printed', any('N1: tautology at =1' in x for x in out) and any('N1: informative' in x for x in out))
    # admission - binary, seal, json
    for tg in ALL:
        check('%s json binary other -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, binary=R.WANT)) == 'NOT_ADMITTED')
    check('installed_sha other -> NOT_ADMITTED', word('b24_h1', files=dict(installed_sha=R.WANT)) == 'NOT_ADMITTED')
    check('installed_sha missing -> NOT_ADMITTED', word('b24_h1', drop=('installed_sha',)) == 'NOT_ADMITTED')
    check('no json -> NOT_ADMITTED', word('b24_n1', drop=('run',)) == 'NOT_ADMITTED')
    check('prereg sha mismatch -> NOT_ADMITTED', word('b24_h0', run=run_json('b24_h0', prereg='0' * 64)) == 'NOT_ADMITTED')
    check('seal file missing -> NOT_ADMITTED', word('b24_h0', drop=('seal',)) == 'NOT_ADMITTED')
    check('seal file edited after the run -> NOT_ADMITTED', word('b24_d0', seal='seal fixture text edited\n') == 'NOT_ADMITTED')
    w, res, _ = rd('b24_h1', case('b24_h1', drop=('bin',)))
    check('version file missing -> reference only, still PASS', w == 'MEMBERS_PASS' and row(res, 'adm', 'version string') is None)
    # admission - env
    for tg in ALL:
        other = '1' if R.SPEC[tg]['fix'] == '0' else '0'
        check('%s KYTY_FIX_B24 other -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_FIX_B24': other})) == 'NOT_ADMITTED')
        check('%s KYTY_FIX_B24 absent -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_FIX_B24': None})) == 'NOT_ADMITTED')
        check('%s extra KYTY_FIX_F8 -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_FIX_F8': '0'})) == 'NOT_ADMITTED')
        check('%s KYTY_GAME_PATCH -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_GAME_PATCH': 'p'})) == 'NOT_ADMITTED')
        check('%s KYTY_GPU_CHECKPOINTS -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_GPU_CHECKPOINTS': '0'})) == 'NOT_ADMITTED')
    for tg in STAND:
        m = R.SPEC[tg]['mode']
        check('%s stand absent -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_TEST_HIDLOSS': None})) == 'NOT_ADMITTED')
        check('%s stand 30:%s -> NOT_ADMITTED' % (tg, m), word(tg, run=run_json(tg, env={'KYTY_TEST_HIDLOSS': '30:' + m})) == 'NOT_ADMITTED')
        om = 'sleep' if m != 'sleep' else 'hold'
        check('%s stand mode %s -> NOT_ADMITTED' % (tg, om), word(tg, run=run_json(tg, env={'KYTY_TEST_HIDLOSS': '60:' + om})) == 'NOT_ADMITTED')
    check('n1 stand present -> NOT_ADMITTED', word('b24_n1', run=run_json('b24_n1', env={'KYTY_TEST_HIDLOSS': '60:hold'})) == 'NOT_ADMITTED')
    check('n1 stand empty string present -> NOT_ADMITTED', word('b24_n1', run=run_json('b24_n1', env={'KYTY_TEST_HIDLOSS': ''})) == 'NOT_ADMITTED')
    check('KYTY_AV_TRACE in env - admitted', word('b24_s0', run=run_json('b24_s0', env={'KYTY_AV_TRACE': '1'})) == 'MEMBERS_PASS')
    # admission - FixB24 lines
    check('=1 FixB24 line missing -> NOT_ADMITTED', word('b24_d1', fixlines=[]) == 'NOT_ADMITTED')
    check('=1 FixB24 two lines -> NOT_ADMITTED', word('b24_n1', fixlines=['FixB24: mode=1', 'FixB24: mode=1']) == 'NOT_ADMITTED')
    check('=1 FixB24 mode=0 -> NOT_ADMITTED', word('b24_h1', fixlines=['FixB24: mode=0']) == 'NOT_ADMITTED')
    check('=0 FixB24 line present -> NOT_ADMITTED', word('b24_h0', fixlines=['FixB24: mode=1']) == 'NOT_ADMITTED')
    # admission - stand lines
    for tg in STAND:
        m = R.SPEC[tg]['mode']
        check('%s config on missing -> NOT_ADMITTED' % tg, word(tg, cfg=[]) == 'NOT_ADMITTED')
        check('%s config on twice -> NOT_ADMITTED' % tg, word(tg, cfg=['TestHidLoss: config on delay_s=60 mode=%s hold_ms=3000' % m] * 2)
              == 'NOT_ADMITTED')
        check('%s armed missing -> NOT_ADMITTED' % tg, word(tg, armed=[]) == 'NOT_ADMITTED')
        check('%s attach missing -> NOT_ADMITTED' % tg, word(tg, attach=[]) == 'NOT_ADMITTED')
        check('%s test pad line missing -> NOT_ADMITTED' % tg, word(tg, pad=[]) == 'NOT_ADMITTED')
        check('%s fire missing -> NOT_ADMITTED' % tg, word(tg, fire=[]) == 'NOT_ADMITTED')
        check('%s done missing -> NOT_ADMITTED' % tg, word(tg, done=[]) == 'NOT_ADMITTED')
        check('%s stat missing (the tag ended inside the window, N5) -> NOT_ADMITTED' % tg, word(tg, stat=[]) == 'NOT_ADMITTED')
        check('%s pad_calls 0 -> NOT_ADMITTED' % tg, word(tg, stat=st(tg, pad_vib=0, pad_led=0, pad_trig=0)) == 'NOT_ADMITTED')
        check('%s pad_calls 1 -> admitted' % tg, word(tg, stat=st(tg, pad_vib=1, pad_led=0, pad_trig=0)) != 'NOT_ADMITTED')
        check('%s probes_posted - probes_run = 1 -> NOT_ADMITTED' % tg, word(tg, stat=st(tg, probes_run=299)) == 'NOT_ADMITTED')
    check('config on delay 30 -> NOT_ADMITTED', word('b24_h1', cfg=['TestHidLoss: config on delay_s=30 mode=hold hold_ms=3000']) == 'NOT_ADMITTED')
    check('config on other mode -> NOT_ADMITTED', word('b24_h1', cfg=['TestHidLoss: config on delay_s=60 mode=sleep hold_ms=3000']) == 'NOT_ADMITTED')
    check('config on hold_ms 2000 -> NOT_ADMITTED', word('b24_h0', cfg=['TestHidLoss: config on delay_s=60 mode=hold hold_ms=2000']) == 'NOT_ADMITTED')
    check('config invalid line -> NOT_ADMITTED', word('b24_s0', cfg=['TestHidLoss: config on delay_s=60 mode=sleep hold_ms=3000',
                                                                    'TestHidLoss: config invalid value="x" (expected <s>[:detach|hold|sleep]), stand off'])
          == 'NOT_ADMITTED')
    check('armed twice -> NOT_ADMITTED', word('b24_h0', armed=['TestHidLoss: armed t_us=70000000'] * 2) == 'NOT_ADMITTED')
    check('attach twice -> NOT_ADMITTED', word('b24_d0', attach=['TestHidLoss: attach index=0 t_us=75000000'] * 2) == 'NOT_ADMITTED')
    check('attach failed line instead of attach -> NOT_ADMITTED',
          word('b24_d0', attach=['TestHidLoss: attach failed error="x" t_us=75000000']) == 'NOT_ADMITTED')
    check('test pad line twice -> NOT_ADMITTED', word('b24_d1', pad=[PAD, PAD]) == 'NOT_ADMITTED')
    check('fire of another mode -> NOT_ADMITTED', word('b24_h0', fire=['TestHidLoss: fire mode=sleep t_us=135000000']) == 'NOT_ADMITTED')
    check('fire twice -> NOT_ADMITTED', word('b24_s0', fire=['TestHidLoss: fire mode=sleep t_us=135000000'] * 2) == 'NOT_ADMITTED')
    check('done twice -> NOT_ADMITTED', word('b24_s0', done=['TestHidLoss: done t_us=138000000'] * 2) == 'NOT_ADMITTED')
    check('stat twice -> NOT_ADMITTED', word('b24_h1', stat=st('b24_h1') * 2) == 'NOT_ADMITTED')
    check('stat of another mode -> NOT_ADMITTED', word('b24_h1', stat=st('b24_h1', mode='sleep')) == 'NOT_ADMITTED')
    bad_stat = stat_line('b24_h1').replace(' vp_effect=0', '')
    w, res, _ = rd('b24_h1', case('b24_h1', stat=[bad_stat]))
    check('stat with a missing field -> malformed, NOT_ADMITTED', w == 'NOT_ADMITTED' and res['stat'] is None)
    w, res, _ = rd('b24_h1', case('b24_h1', stat=['[7][00:01:02.003] xx' + stat_line('b24_h1')]))
    check('stat inside an interleaved line parsed', w == 'MEMBERS_PASS' and res['stat'] is not None)
    for tg in ALL:
        check('%s another pad line -> NOT_ADMITTED' % tg,
              word(tg, before=['Controller 3: "DualSense Wireless Controller" type=7 accel=1 gyro=1 path=x']) == 'NOT_ADMITTED')
    check('n1 TestHidLoss line -> NOT_ADMITTED', word('b24_n1', before=['TestHidLoss: armed t_us=1']) == 'NOT_ADMITTED')
    check('n1 test pad line -> NOT_ADMITTED', word('b24_n1', before=[PAD]) == 'NOT_ADMITTED')
    # N5 (item 460 (d))
    lg = mk_log('b24_h1', quit=False)
    check('N5 no quit line, stat present -> admitted', rd('b24_h1', case('b24_h1', log=lg))[0] == 'MEMBERS_PASS')
    lg = mk_log('b24_h1', quit=False)
    i = lg.index(stat_line('b24_h1'))
    lg.insert(i, 'Event: quit')
    check('N5 quit line before the stat line -> NOT_ADMITTED', rd('b24_h1', case('b24_h1', log=lg))[0] == 'NOT_ADMITTED')
    lg = mk_log('b24_d0')
    j = lg.index('TestHidLoss: attach index=0 t_us=75000000')
    s = lg.pop(lg.index(stat_line('b24_d0')))
    lg.insert(j, s)
    check('N5 stat line before the attach line -> NOT_ADMITTED', rd('b24_d0', case('b24_d0', log=lg))[0] == 'NOT_ADMITTED')
    w, res, _ = rd('b24_d1', case('b24_d1', stat=[]))
    check('N5 row NO when the tag ends inside the window', row(res, 'adm', 'N5') is False)
    # interference
    for line, want in (('Window 1 minimized', 'NOT_ADMITTED'), ('Recovering Vulkan swapchain', 'NOT_ADMITTED'), ('GamePatch: x', 'NOT_ADMITTED'),
                       ('Window 1 lost keyboard focus', 'MEMBERS_PASS'), ('Window 1 restored', 'MEMBERS_PASS'),
                       ('AsyncPipelines: skipped draw 1', 'MEMBERS_PASS'), ('[Vulkan][E] x', 'MEMBERS_PASS'),
                       ('PadTriggerEffect: #1 mask=0x0c L=0[00 00 00 00] R=0[00 00 00 00] sent=0', 'MEMBERS_PASS'),
                       ('Controller removed: 0, time = 1.0000', 'MEMBERS_PASS')):
        check('line %s -> %s' % (line, want), word('b24_h1', before=[line]) == want)
    # form
    check('installed before other -> FORM_FAIL', word('b24_n1', files=dict(installed_before=R.BIN_EXPECT)) == 'FORM_FAIL')
    check('installed after other -> FORM_FAIL', word('b24_n1', files=dict(installed_after=R.BIN_EXPECT)) == 'FORM_FAIL')
    check('manifest DIFFER -> FORM_FAIL', word('b24_h0', files=dict(manifest_cmp='manifest cmp DIFFER only-before 1')) == 'FORM_FAIL')
    check('manifest missing -> FORM_FAIL', word('b24_h0', drop=('manifest_cmp',)) == 'FORM_FAIL')
    check('admission precedes form', word('b24_h0', files=dict(installed_before='x'), pad=[]) == 'NOT_ADMITTED')
    # b24_h0 members
    check('h0 main_late 2700000 -> PASS', word('b24_h0', stat=st('b24_h0', main_late_max_us=2700000)) == 'MEMBERS_PASS')
    check('h0 main_late 2699999 -> MEMBERS_FAIL', word('b24_h0', stat=st('b24_h0', main_late_max_us=2699999)) == 'MEMBERS_FAIL')
    check('h0 pad_wait 2700000 -> PASS', word('b24_h0', stat=st('b24_h0', pad_wait_max_us=2700000)) == 'MEMBERS_PASS')
    check('h0 pad_wait 2699999 -> MEMBERS_FAIL', word('b24_h0', stat=st('b24_h0', pad_wait_max_us=2699999)) == 'MEMBERS_FAIL')
    check('h0 no frame >= 1 s in the window -> STOP_ITERATION', word('b24_h0', win=frames(200, start=300)) == 'STOP_ITERATION')
    check('h0 window frame 999999 -> STOP_ITERATION', word('b24_h0', win=frames(3, start=300) + [fr(303, 999999)]) == 'STOP_ITERATION')
    check('h0 window frame 1000000 -> PASS', word('b24_h0', win=frames(3, start=300) + [fr(303, 1000000)]) == 'MEMBERS_PASS')
    check('h0 stop precedes other member failures',
          word('b24_h0', win=frames(20, start=300), stat=st('b24_h0', main_late_max_us=10)) == 'STOP_ITERATION')
    check('h0 stop only after admission', word('b24_h0', win=frames(20, start=300), pad=[]) == 'NOT_ADMITTED')
    check('h0 long frame after the stat line is outside the window -> STOP_ITERATION',
          word('b24_h0', win=frames(20, start=300), post=[fr(800, 3000000)] + frames(100, start=801)) == 'STOP_ITERATION')
    # window edges (wide = fire - 1 s by the dt_us of the frames before the fire line; strict = between fire and stat)
    def pre_fire(tag, long_dt, after_k, after_dt=100000):
        lg = mk_log(tag, win=frames(200, start=300))
        fl = [x for x in lg if x.startswith('TestHidLoss: fire')][0]
        i = lg.index(fl)
        return lg[:i] + [fr(290, long_dt)] + [fr(291 + k, after_dt) for k in range(after_k)] + lg[i:]
    w, res, _ = rd('b24_s0', case('b24_s0', log=pre_fire('b24_s0', 2000000, 10)))
    check('s0 long frame 1.0 s before the fire line (10 x 100 ms after it) -> in wide, not strict -> STOP_ITERATION',
          w == 'STOP_ITERATION' and res['k2_wide'] == [290] and res['k2_strict'] == [])
    w, res, _ = rd('b24_s0', case('b24_s0', log=pre_fire('b24_s0', 2000000, 11)))
    check('s0 long frame 1.1 s before the fire line -> outside the window -> PASS', w == 'MEMBERS_PASS' and res['k2_wide'] == [])
    w, res, _ = rd('b24_h0', case('b24_h0', log=pre_fire('b24_h0', 2000000, 10)))
    check('h0 only a long frame 1.0 s before fire -> wide reading counts it (PASS), strict 0',
          w == 'MEMBERS_PASS' and res['k2_strict'] == [])
    w, res, _ = rd('b24_h1', case('b24_h1', log=pre_fire('b24_h1', 2000000, 11)))
    check('h1 long frame 1.1 s before fire -> outside the window -> HARM_FAIL', w == 'HARM_FAIL')
    w, res, _ = rd('b24_h1', case('b24_h1', log=pre_fire('b24_h1', 2000000, 10)))
    check('h1 long frame 1.0 s before fire -> in the window -> MEMBERS_FAIL', w == 'MEMBERS_FAIL')
    # b24_s0 members
    check('s0 main_late 2699999 -> MEMBERS_FAIL', word('b24_s0', stat=st('b24_s0', main_late_max_us=2699999)) == 'MEMBERS_FAIL')
    check('s0 pad_wait 49999 -> PASS', word('b24_s0', stat=st('b24_s0', pad_wait_max_us=49999)) == 'MEMBERS_PASS')
    check('s0 pad_wait 50000 -> MEMBERS_FAIL', word('b24_s0', stat=st('b24_s0', pad_wait_max_us=50000)) == 'MEMBERS_FAIL')
    check('s0 frame >= 1 s in the window -> STOP_ITERATION', word('b24_s0', win=frames(5, start=300) + [fr(305, 1000000)]) == 'STOP_ITERATION')
    check('s0 frame 999999 in the window -> PASS', word('b24_s0', win=frames(5, start=300) + [fr(305, 999999)]) == 'MEMBERS_PASS')
    check('s0 harm is a reference', word('b24_s0', idx=10, extra=['--- Fatal Error ---']) == 'MEMBERS_PASS')
    # b24_h1 members
    for k, v, want in (('main_late_max_us', 2700000, 'MEMBERS_PASS'), ('main_late_max_us', 2699999, 'MEMBERS_FAIL'),
                       ('po_wait_max_us', 2700000, 'MEMBERS_PASS'), ('po_wait_max_us', 2699999, 'MEMBERS_FAIL'),
                       ('pad_wait_max_us', 49999, 'MEMBERS_PASS'), ('pad_wait_max_us', 50000, 'MEMBERS_FAIL'),
                       ('guest_sdl', 1, 'MEMBERS_FAIL')):
        check('h1 %s %d -> %s' % (k, v, want), word('b24_h1', stat=st('b24_h1', **{k: v})) == want)
    check('h1 frame >= 1 s in the window -> MEMBERS_FAIL', word('b24_h1', win=frames(5, start=300) + [fr(305, 1000000)]) == 'MEMBERS_FAIL')
    check('h1 frame 999999 in the window -> PASS', word('b24_h1', win=frames(5, start=300) + [fr(305, 999999)]) == 'MEMBERS_PASS')
    w, res, _ = rd('b24_h1', case('b24_h1', fixlines=[]))
    check('h1 FixB24 member NO when the line is missing', row(res, 'mem', 'FixB24') is False and w == 'NOT_ADMITTED')
    # b24_d0, b24_d1 members
    for tg in ('b24_d0', 'b24_d1'):
        check('%s removed 0 -> MEMBERS_FAIL' % tg, word(tg, stat=st(tg, removed=0)) == 'MEMBERS_FAIL')
        check('%s removed 2 -> MEMBERS_FAIL' % tg, word(tg, stat=st(tg, removed=2)) == 'MEMBERS_FAIL')
        check('%s removed lines 0 -> MEMBERS_FAIL' % tg, word(tg, removed=[]) == 'MEMBERS_FAIL')
        check('%s removed lines 2 -> MEMBERS_FAIL' % tg, word(tg, removed=['Controller 0: removed'], extra=['Controller 0: removed']) == 'MEMBERS_FAIL')
        check('%s debug removed text not a removed line' % tg, word(tg, removed=['Controller removed: 0, time = 1.0']) == 'MEMBERS_FAIL')
        check('%s frame >= 1 s in the window -> MEMBERS_FAIL' % tg, word(tg, win=frames(5, start=300) + [fr(305, 1000000)]) == 'MEMBERS_FAIL')
        check('%s frame >= 1 s after the stat line -> reference (PASS)' % tg, word(tg, post=[fr(800, 2000000)] + frames(10, start=801))
              == 'MEMBERS_PASS')
        check('%s detach failed line is a reference' % tg, rd(tg, case(tg, extra=['TestHidLoss: detach failed index=-1 error="x"']))[1]['detach_bad'] == 1)
    # b24_n1 members and harm
    check('n1 FixB24 member', row(rd('b24_n1', case('b24_n1'))[1], 'mem', 'FixB24') is True)
    check('n1 TestHidLoss member', row(rd('b24_n1', case('b24_n1'))[1], 'mem', 'TestHidLoss') is True)
    # harm (b24_h1, b24_n1)
    for tg in ('b24_h1', 'b24_n1'):
        for mk in ('Unhandled exception:', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort:', 'ErrorDeviceLost'):
            check('%s death %s in log -> HARM_FAIL' % (tg, mk), word(tg, extra=[mk + ' x']) == 'HARM_FAIL')
        check('%s death in stdout -> HARM_FAIL' % tg, word(tg, stdout=['--- Fatal Error ---']) == 'HARM_FAIL')
        check('%s no stdout -> NOT_EVALUABLE' % tg, word(tg, drop=('stdout',)) == 'NOT_EVALUABLE')
        check('%s frame 1000000 us after the scene outside the window -> HARM_FAIL' % tg,
              word(tg, post=frames(10, start=800) + [fr(900, 1000000)]) == 'HARM_FAIL')
        check('%s frame 999999 us outside the window -> PASS' % tg, word(tg, post=frames(10, start=800) + [fr(900, 999999)]) == 'MEMBERS_PASS')
        check('%s frame >= 1 s before the first scene frame not counted' % tg,
              word(tg, head=[fr(1, 2000000, 99), fr(2, 16000, 100)]) == 'MEMBERS_PASS')
        check('%s frame >= 1 s on the first scene frame itself not counted' % tg,
              word(tg, head=[fr(1, 16000, 50), fr(2, 2000000, 100)]) == 'MEMBERS_PASS')
        check('%s video 2999 -> HARM_FAIL' % tg, word(tg, idx=2999) == 'HARM_FAIL')
        check('%s video 3000 -> PASS' % tg, word(tg, idx=3000) == 'MEMBERS_PASS')
        check('%s no video index -> HARM_FAIL' % tg, word(tg, drop=('idx',)) == 'HARM_FAIL')
        check('%s glitch 1 -> HARM_FAIL' % tg, word(tg, files=dict(glitch='one-frame glitches: 1')) == 'HARM_FAIL')
        check('%s no glitch file -> NOT_EVALUABLE' % tg, word(tg, drop=('glitch',)) == 'NOT_EVALUABLE')
        check('%s no sheet -> HARM_FAIL' % tg, word(tg, drop=('sheet',)) == 'HARM_FAIL')
        h = R.SPEC[tg]['hold']
        check('%s hold_s %d - 1 -> HARM_FAIL' % (tg, h), word(tg, run=run_json(tg, hold_s=h - 1.0)) == 'HARM_FAIL')
        check('%s hold_s exactly %d -> PASS' % (tg, h), word(tg, run=run_json(tg, hold_s=float(h))) == 'MEMBERS_PASS')
        check('%s hold_exit set -> HARM_FAIL' % tg, word(tg, run=run_json(tg, hold_exit=3221225477)) == 'HARM_FAIL')
        check('%s outcome timeout -> HARM_FAIL' % tg, word(tg, run=run_json(tg, outcome='timeout')) == 'HARM_FAIL')
        check('%s not entered -> HARM_FAIL' % tg, rd(tg, case(tg, log=[l for l in mk_log(tg) if l != GUEST]))[0] == 'HARM_FAIL')
        check('%s frame >= 1 s after a scene change not counted' % tg,
              word(tg, extra=['GuestOut: Level has started: hub', fr(999, 2000000)]) == 'MEMBERS_PASS')
    check('h1 member fail precedes harm', word('b24_h1', stat=st('b24_h1', guest_sdl=1), idx=10) == 'MEMBERS_FAIL')
    check('h0 harm is a reference', word('b24_h0', idx=10, extra=['--- Fatal Error ---']) == 'MEMBERS_PASS')
    check('d1 harm is a reference', word('b24_d1', drop=('glitch',)) == 'MEMBERS_PASS')
    # identities and invariants (F19a section 6.1)
    for tg in STAND:
        w, res, _ = rd(tg, case(tg, stat=st(tg, pad_calls=999)))
        check('%s pad_calls != vib + led + trig -> IDENT_FAIL' % tg, w == 'IDENT_FAIL' and row(res, 'ident', 'pad_calls =') is False)
        w, res, _ = rd(tg, case(tg, stat=st(tg, probes_run=301)))
        check('%s probes_run > probes_posted -> identity NO (admission first)' % tg,
              row(res, 'ident', 'probes_run <=') is False and w == 'NOT_ADMITTED')
        w, res, _ = rd(tg, case(tg))
        check('%s identities all YES on the positive tag' % tg, all(v is True for _, v in res['ident']) and len(res['ident']) == 5)
    for tg in ('b24_h0', 'b24_s0', 'b24_h1'):
        w, res, _ = rd(tg, case(tg, stat=st(tg, removed=1)))
        check('%s removed 1 in hold/sleep -> IDENT_FAIL' % tg, w == 'IDENT_FAIL' and row(res, 'ident', 'removed = 0') is False)
    w, res, _ = rd('b24_d0', case('b24_d0', stat=st('b24_d0', removed=0)))
    check('d0 removed 0 in detach -> identity NO', row(res, 'ident', 'removed = 1') is False)
    for t, why in (((75, 75, 135, 138), 'armed = attach'), ((70, 136, 135, 138), 'attach > fire'), ((70, 75, 139, 138), 'fire > done'),
                   ((80, 75, 135, 138), 'armed > attach')):
        w, res, _ = rd('b24_s0', case('b24_s0', t=t))
        check('t_us order %s -> IDENT_FAIL' % why, w == 'IDENT_FAIL' and row(res, 'ident', 't_us armed') is False)
    check('t_us fire = done -> PASS', word('b24_s0', t=(70, 75, 135, 135)) == 'MEMBERS_PASS')
    for tg in ('b24_h0', 'b24_s0', 'b24_d0'):
        check('%s po_applied 1 at =0 -> IDENT_FAIL' % tg, word(tg, stat=st(tg, po_applied=1)) == 'IDENT_FAIL')
        check('%s po_wait_max_us 1 at =0 -> IDENT_FAIL' % tg, word(tg, stat=st(tg, po_wait_max_us=1)) == 'IDENT_FAIL')
    check('d1 guest_sdl 1 at =1 -> IDENT_FAIL', word('b24_d1', stat=st('b24_d1', guest_sdl=1)) == 'IDENT_FAIL')
    w, res, _ = rd('b24_d1', case('b24_d1'))
    check('=1 invariant row is guest_sdl', row(res, 'ident', 'guest_sdl = 0 at =1') is True)
    w, res, _ = rd('b24_n1', case('b24_n1'))
    check('n1 no identities', res['ident'] == [])
    w, res, _ = rd('b24_h0', case('b24_h0', stat=[]))
    check('identities not read without stat', all(v is None for _, v in res['ident'][:3]))
    # rows read on their own (sensitivity of sens_f19e.py)
    w, res, _ = rd('b24_h1', case('b24_h1', win=frames(5, start=300) + [fr(305, 1000000)]))
    check('h1 frame >= 1 s inside the window is not a harm frame (harm row YES)',
          row(res, 'harm', 'outside the stand window') is True and w == 'MEMBERS_FAIL')
    check('identity failure precedes harm failure', word('b24_h1', stat=st('b24_h1', pad_calls=999), idx=10) == 'IDENT_FAIL')
    w, res, _ = rd('b24_d0', case('b24_d0', attach=[]))
    check('attach row NO when the attach line is missing', row(res, 'adm', 'attach exactly') is False)
    w, res, _ = rd('b24_h1', case('b24_h1', extra=['TestHidLoss: stat mode=hold main_late_max_us=1']))
    check('a valid stat plus a malformed stat line -> NOT_ADMITTED', w == 'NOT_ADMITTED' and res['stat'] is not None)
    w, res, _ = rd('b24_n1', case('b24_n1', fixlines=[]))
    check('n1 FixB24 member NO when the line is missing', row(res, 'mem', 'FixB24') is False and w == 'NOT_ADMITTED')
    # missing log
    w, res, _ = rd('b24_h1', case('b24_h1', drop=('log',)))
    check('no log -> NOT_ADMITTED', w == 'NOT_ADMITTED' and res['log_sha256'] is None)
    # CLI: strict cp1250 without PYTHONIOENCODING, ASCII only, json, unknown tag
    d = case('b24_h0')
    env = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag', 'b24_h0'], capture_output=True, env=env)
    check('cli cp1250 strict rc 0', p.returncode == 0)
    check('cli ASCII only', all(b < 128 for b in p.stdout))
    check('cli READING line', b'  READING b24_h0 MEMBERS_PASS' in p.stdout)
    env2 = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
    p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag', 'b24_h0'], capture_output=True, env=env2)
    check('cli without PYTHONIOENCODING rc 0', p.returncode == 0)
    jp = os.path.join(T, 'o.json')
    p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag', 'b24_h0', '--json', jp], capture_output=True)
    check('cli json written', p.returncode == 0 and json.load(open(jp))['word'] == 'MEMBERS_PASS')
    p = subprocess.run([sys.executable, TARGET, 'f8_s0'], capture_output=True)
    check('cli unknown tag refused', p.returncode != 0 and b'unknown tag' in p.stderr)
    p = subprocess.run([sys.executable, TARGET, '--dir', d], capture_output=True)
    check('cli --dir without --tag refused', p.returncode != 0)
finally:
    shutil.rmtree(T, ignore_errors=True)

print('checks %d failed %d' % (N[0], len(FAIL)))
if FAIL:
    sys.exit(1)
print('ALL OK')
