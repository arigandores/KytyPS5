"""FS7c (HPP-567): fixtures of fs7c_read.py - every admission row, member and edge of the seal docs/track-f/fs7c.md section 4 (item 467
(g)(3), item 487 (g)(3), item 518 (v)(3)-(4)) for the tags fs7_h (form b24_h1) and fs7_n (form f8_n1).  Ends with ALL OK.
usage: python test_fs7c_read.py   (ASCII only)"""
import hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'fs7c_read.py')
sys.path.insert(0, HERE)
import fs7c_read as R

print('suite test_fs7c_read.py sha256 %s target fs7c_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(open(TARGET, 'rb').read()).hexdigest()))
N = [0]
FAIL = []


def check(name, cond):
    N[0] += 1
    if not cond:
        FAIL.append(name)
        print('FAIL', name)


GUEST = 'GuestOut: Level has started: underwater_aerial_garden'
MODL = 'GuestOut: MODL: '
PAD = 'Controller 0: "KYTY test pad" type=1 accel=0 gyro=0 path='
OPENED = 'AudioOut: opened SDL device "(system default)" (48000 Hz, 2 ch, format 0x8120)'
VIB = 'AudioOut: vibration port 3 (48000 Hz, 2 ch, 512 frames, float) -> pad haptics'
F8 = 'AudioOut: SDL_QueueAudio failed: Invalid audio device ID'
T_VIB = 9.464
FIX_DEFAULT = ['FixB4: mode=1', 'FixB24: mode=1']


def stamp(t):
    ms = int(round(t * 1000))
    return '[3][%02d:%02d:%02d.%03d]' % (ms // 3600000, (ms // 60000) % 60, (ms // 1000) % 60, ms % 1000)


def fr(n, dt, draws=3000):
    return 'FrameTrace: n=%d dt_us=%d draws=%d' % (n, dt, draws)


def frames(k, dt=16000, start=100):
    return [fr(start + i, dt) for i in range(k)]


def default_stat(**kw):
    s = dict(main_late_max_us=3000000, probes_posted=300, probes_run=300, pad_vib=180, pad_led=2, pad_trig=1, pad_wait_max_us=40,
             po_applied=150, po_wait_max_us=2999000, guest_sdl=0, removed=0, vp_rumble=0, vp_led=1, vp_effect=0)
    s.update(kw)
    return s


def stat_line(**kw):
    s = default_stat(**kw)
    pc = s.pop('pad_calls', s['pad_vib'] + s['pad_led'] + s['pad_trig'])
    mode = s.pop('mode', 'hold')
    vals = ['%s=%d' % (k, s[k]) for k in ('main_late_max_us', 'probes_posted', 'probes_run')] + ['pad_calls=%d' % pc]
    vals += ['%s=%d' % (k, s[k]) for k in R.STAT_KEYS[4:] if k in s]
    return 'TestHidLoss: stat mode=%s %s' % (mode, ' '.join(vals))


def head_lines(fixes, f8, rev):
    L = ['[3][00:00:01.000] start', '  version: Fork build arigandores/KytyPS5 %s' % rev]
    L += fixes if fixes is not None else FIX_DEFAULT
    L += f8 if f8 is not None else ['FixF8: mode=1']
    return L


def mk_h(fixes=None, f8=None, f8_after=None, rev='d6ee2dc', cfg=None, before=None, head=None, pre=None, win=None, post=None, extra=None,
         stat=None, armed=None, attach=None, pad=None, fire=None, done=None, quit=True, t=(70, 75, 135, 138), modl=True):
    L = head_lines(fixes, f8, rev)
    L += cfg if cfg is not None else ['TestHidLoss: config on delay_s=60 mode=hold hold_ms=3000']
    L += before or []
    L += [MODL] if modl else []
    L += f8_after or []
    L += [GUEST] + (head if head is not None else [fr(1, 16000, 50), fr(2, 16000, 100)])
    L += pre if pre is not None else frames(60, start=3)
    ta, tt, tf, td = t
    L += armed if armed is not None else ['TestHidLoss: armed t_us=%d' % (ta * 1000000)]
    L += frames(60, start=70)
    L += attach if attach is not None else ['TestHidLoss: attach index=0 t_us=%d' % (tt * 1000000)]
    L += pad if pad is not None else [PAD]
    L += frames(120, start=140)
    L += fire if fire is not None else ['TestHidLoss: fire mode=hold t_us=%d' % (tf * 1000000)]
    L += win if win is not None else frames(200, start=300)
    L += done if done is not None else ['TestHidLoss: done t_us=%d' % (td * 1000000)]
    L += frames(120, start=600)
    L += stat if stat is not None else [stat_line()]
    L += post if post is not None else frames(300, start=800)
    L += extra or []
    L += ['Window 1 closed'] + (['Event: quit'] if quit else [])
    return L


def mk_n(fixes=None, f8=None, f8_after=None, rev='d6ee2dc', A=3, vib=True, vib_stamp=True, before=None, head=None, frames_=None,
         extra=None, end=850, ports=(0, 2), status=1, init=None, acq=None, mod=None, f8_at=(), modl=True):
    L = head_lines(fixes, f8, rev)
    L += before or []
    L += ['[3][00:00:05.000] open'] + [OPENED] * A
    if vib:
        L += ([stamp(T_VIB) + ' vib'] if vib_stamp else []) + [VIB]
    L += [MODL] if modl else []
    L += f8_after or []
    L += [GUEST] + (head if head is not None else [fr(1, 16000, 50), fr(2, 16000, 100)])
    L += frames_ if frames_ is not None else [fr(i + 3, 33000) for i in range(40)]
    ev = []
    for tf in f8_at:
        ev.append((tf, 0, stamp(tf) + ' f8'))
        ev.append((tf, 2, F8))
    for t in range(11, end):
        ic = init(t) if init is not None else 1
        ac = acq(t) if acq is not None else 3 + int((t - T_VIB) / 3)
        ev.append((t, 0, stamp(t) + ' tick'))
        for p in ports:
            row = dict(t=t * 1000000, port=p, dev=p + 2, status=status, queued=7680, pushes=100 * t, q_fail=0, init_calls=ic, acq=ac)
            if mod:
                row = mod(t, p, row)
                if row is None:
                    continue
            ev.append((t, 1, 'AudioStat: t_us=%d port=%d dev=%d status=%d queued=%d pushes=%d q_fail=%d init_calls=%d acq=%d' % (
                row['t'], row['port'], row['dev'], row['status'], row['queued'], row['pushes'], row['q_fail'], row['init_calls'],
                row['acq'])))
    ev.sort(key=lambda x: (x[0], x[1]))
    L += [x[2] for x in ev]
    L += extra or []
    L += ['Window 1 closed', 'Event: quit']
    return L


SEAL_TEXT = 'seal fixture text\n'


def run_json(tag, env=None, binary=None, prereg=None, **att):
    sp = R.SPEC[tag]
    a = dict(outcome='ok', hold_exit=None, hold_s=float(sp['hold']) + 0.2, close_posted=1, close_rc=0, close_killed=False, close_s=2.1,
             close_wait_s=40)
    a.update(att)
    e = {'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_REC': 'x', 'KYTY_FRAME_TRACE': 'lite'}
    if tag == 'fs7_h':
        e['KYTY_TEST_HIDLOSS'] = '60:hold'
    else:
        e['KYTY_AV_TRACE'] = '1'
    for k, v in (env or {}).items():
        if v is None:
            e.pop(k, None)
        else:
            e[k] = v
    return dict(binary_sha256=R.BIN_EXPECT if binary is None else binary, env=e, attempts=[a],
                prereg=dict(sha256=hashlib.sha256(SEAL_TEXT.encode()).hexdigest() if prereg is None else prereg))


T = tempfile.mkdtemp(prefix='fs7c_fix_')
CNT = [0]


def case(tag, log=None, stdout=None, run=None, files=None, drop=(), idx=3100, seal=SEAL_TEXT, binbytes=None, **lk):
    CNT[0] += 1
    d = os.path.join(T, 'c%03d' % CNT[0])
    os.makedirs(d)
    f = dict(installed_sha=R.BIN_EXPECT, installed_before=R.WANT, installed_after=R.WANT,
             warm='warm form: C:/x/variant present at 2026-10-05T04:00:00Z; entries 5', manifest_cmp='manifest cmp EQUAL files 2 listsha abc',
             glitch='one-frame glitches: 0', sheet='sheet: x.png frames 3100')
    f.update(files or {})
    for k, v in f.items():
        if k not in drop:
            open(os.path.join(d, k + '.txt'), 'w').write(v + '\n')
    if 'log' not in drop:
        if log is None:
            log = mk_h(**lk) if tag == 'fs7_h' else mk_n(**lk)
        open(os.path.join(d, 'log.txt'), 'wb').write(('\n'.join(log) + '\n').encode())
    if 'stdout' not in drop:
        open(os.path.join(d, 'stdout.txt'), 'wb').write(('\n'.join(stdout or ['Shaders: VS 1']) + '\n').encode())
    if 'run' not in drop:
        open(os.path.join(d, 'es.json'), 'w').write(json.dumps(run if run is not None else run_json(tag)))
    if 'idx' not in drop:
        open(os.path.join(d, 'rec.idx'), 'w').write('r\n' * idx)
    if 'seal' not in drop:
        open(os.path.join(d, 'seal.md'), 'wb').write(seal.encode())
    if 'bin' not in drop:
        open(os.path.join(d, 'bin.exe'), 'wb').write(binbytes if binbytes is not None else b'MZ...' + R.VERSION + b'...')
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


def st(**kw):
    return [stat_line(**kw)]


try:
    # constants of the seal as literals (item 467 (g)(3): hold >= 840 s; item 487 (g)(3): 330 s; installed FS6 9325446c, item 510)
    check('hold fs7_h literal 330', R.SPEC['fs7_h']['hold'] == 330)
    check('hold fs7_n literal 840', R.SPEC['fs7_n']['hold'] == 840)
    check('installed literal FS6 9325446c', R.WANT == '9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2')
    check('binary literal FS7 8df61c00', R.BIN_EXPECT == '8df61c009fbe6d7fd7f4e7576e89ab1b0989129336a26f6d1cdf8fd778fbffe7')
    check('fs7_n hold_s 839.9 -> HARM_FAIL', word('fs7_n', run=run_json('fs7_n', hold_s=839.9)) == 'HARM_FAIL')
    check('fs7_n hold_s 840.0 -> PASS', word('fs7_n', run=run_json('fs7_n', hold_s=840.0)) == 'MEMBERS_PASS')
    check('fs7_h hold_s 329.9 -> HARM_FAIL', word('fs7_h', run=run_json('fs7_h', hold_s=329.9)) == 'HARM_FAIL')
    check('fs7_h hold_s 330.0 -> PASS', word('fs7_h', run=run_json('fs7_h', hold_s=330.0)) == 'MEMBERS_PASS')
    for tg in R.ORDER:
        check('%s installed before/after = FS6 literal -> PASS' % tg, word(tg, files=dict(
            installed_before='9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2',
            installed_after='9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2')) == 'MEMBERS_PASS')
        check('%s installed before/after = S12 adb0c82f -> FORM_FAIL' % tg, word(tg, files=dict(
            installed_before='adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421',
            installed_after='adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421')) == 'FORM_FAIL')
    # positive tags
    for tg in R.ORDER:
        w, res, out = rd(tg, case(tg))
        check('positive %s -> MEMBERS_PASS (got %s)' % (tg, w), w == 'MEMBERS_PASS')
        check('positive %s READING line' % tg, out[-1] == '  READING %s MEMBERS_PASS' % tg)
        check('positive %s N4 row printed with line numbers' % tg, any(x.startswith('  N4 row') and 'FixF8: mode=1 line 5, first GuestOut line'
                                                                         in x for x in out))
        check('positive %s EXIT row printed' % tg, any(x.startswith('  EXIT (report row, not a gate): close_posted 1 close_rc 0') for x in out))
        check('positive %s 8 members' % tg, len(res['mem']) == 8)
    w, res, out = rd('fs7_h', case('fs7_h'))
    check('h N3 line printed', any('sent= of PadTriggerEffect lines is not delivery - not read' in x for x in out))
    check('h identities are IDENT rows', any(x.startswith('  IDENT pad_calls') for x in out))
    w, res, out = rd('fs7_n', case('fs7_n'))
    check('n identities are IDENT-REF rows', any(x.startswith('  IDENT-REF q_fail') for x in out))
    # admission - binary, version, revision, seal, json
    for tg in R.ORDER:
        check('%s json binary other -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, binary=R.WANT)) == 'NOT_ADMITTED')
        check('%s installed_sha other -> NOT_ADMITTED' % tg, word(tg, files=dict(installed_sha=R.WANT)) == 'NOT_ADMITTED')
        check('%s installed_sha missing -> NOT_ADMITTED' % tg, word(tg, drop=('installed_sha',)) == 'NOT_ADMITTED')
        check('%s no json -> NOT_ADMITTED' % tg, word(tg, drop=('run',)) == 'NOT_ADMITTED')
        check('%s prereg sha mismatch -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, prereg='0' * 64)) == 'NOT_ADMITTED')
        check('%s seal file missing -> NOT_ADMITTED' % tg, word(tg, drop=('seal',)) == 'NOT_ADMITTED')
        check('%s seal edited after the run -> NOT_ADMITTED' % tg, word(tg, seal='seal fixture text edited\n') == 'NOT_ADMITTED')
        check('%s binary file missing -> NOT_ADMITTED (N3)' % tg, word(tg, drop=('bin',)) == 'NOT_ADMITTED')
        check('%s version string of FS6 in the binary -> NOT_ADMITTED (N3)' % tg,
              word(tg, binbytes=b'MZ KytyPS5-2026-09-15-6a2987a-1879-g3904522d ...') == 'NOT_ADMITTED')
        check('%s revision text 3904522 in the log -> NOT_ADMITTED (N3)' % tg, word(tg, rev='3904522') == 'NOT_ADMITTED')
        check('%s no revision text in the log -> NOT_ADMITTED (N3)' % tg,
              rd(tg, case(tg, log=[x for x in (mk_h() if tg == 'fs7_h' else mk_n()) if 'Fork build' not in x]))[0] == 'NOT_ADMITTED')
    # admission - env
    for tg in R.ORDER:
        for k, v in (('KYTY_FIX_F8', '1'), ('KYTY_FIX_B24', '1'), ('KYTY_FIX_B4', '1'), ('KYTY_FIX_F8', '0'), ('KYTY_FIX_F19', '1'),
                     ('KYTY_FIX_B24', ''), ('KYTY_HAPTICS', '1'), ('KYTY_GAME_PATCH', 'p'), ('KYTY_GPU_CHECKPOINTS', '0'),
                     ('KYTY_TEST_AUDIOLOSS', '60:retry'), ('KYTY_TEST_AUDIOLOSS', '')):
            check('%s env %s=%r -> NOT_ADMITTED' % (tg, k, v), word(tg, run=run_json(tg, env={k: v})) == 'NOT_ADMITTED')
    check('h stand absent -> NOT_ADMITTED', word('fs7_h', run=run_json('fs7_h', env={'KYTY_TEST_HIDLOSS': None})) == 'NOT_ADMITTED')
    check('h stand 30:hold -> NOT_ADMITTED', word('fs7_h', run=run_json('fs7_h', env={'KYTY_TEST_HIDLOSS': '30:hold'})) == 'NOT_ADMITTED')
    check('h stand 60:sleep -> NOT_ADMITTED', word('fs7_h', run=run_json('fs7_h', env={'KYTY_TEST_HIDLOSS': '60:sleep'})) == 'NOT_ADMITTED')
    check('h KYTY_AV_TRACE in env - admitted (form b24_h1, F19e)', word('fs7_h', run=run_json('fs7_h', env={'KYTY_AV_TRACE': '1'}))
          == 'MEMBERS_PASS')
    check('n KYTY_AV_TRACE absent -> NOT_ADMITTED', word('fs7_n', run=run_json('fs7_n', env={'KYTY_AV_TRACE': None})) == 'NOT_ADMITTED')
    check('n KYTY_AV_TRACE 0 -> NOT_ADMITTED', word('fs7_n', run=run_json('fs7_n', env={'KYTY_AV_TRACE': '0'})) == 'NOT_ADMITTED')
    check('n KYTY_TEST_HIDLOSS present -> NOT_ADMITTED', word('fs7_n', run=run_json('fs7_n', env={'KYTY_TEST_HIDLOSS': '60:hold'}))
          == 'NOT_ADMITTED')
    check('n KYTY_TEST_HIDLOSS empty -> NOT_ADMITTED', word('fs7_n', run=run_json('fs7_n', env={'KYTY_TEST_HIDLOSS': ''})) == 'NOT_ADMITTED')
    # admission - fs7_h stand lines (F19e)
    check('h config on missing -> NOT_ADMITTED', word('fs7_h', cfg=[]) == 'NOT_ADMITTED')
    check('h config on twice -> NOT_ADMITTED', word('fs7_h', cfg=['TestHidLoss: config on delay_s=60 mode=hold hold_ms=3000'] * 2)
          == 'NOT_ADMITTED')
    check('h config on delay 30 -> NOT_ADMITTED', word('fs7_h', cfg=['TestHidLoss: config on delay_s=30 mode=hold hold_ms=3000'])
          == 'NOT_ADMITTED')
    check('h config on sleep -> NOT_ADMITTED', word('fs7_h', cfg=['TestHidLoss: config on delay_s=60 mode=sleep hold_ms=3000'])
          == 'NOT_ADMITTED')
    check('h config on hold_ms 2000 -> NOT_ADMITTED', word('fs7_h', cfg=['TestHidLoss: config on delay_s=60 mode=hold hold_ms=2000'])
          == 'NOT_ADMITTED')
    check('h config invalid -> NOT_ADMITTED', word('fs7_h', cfg=['TestHidLoss: config on delay_s=60 mode=hold hold_ms=3000',
                                                                 'TestHidLoss: config invalid value="x", stand off']) == 'NOT_ADMITTED')
    check('h armed missing -> NOT_ADMITTED', word('fs7_h', armed=[]) == 'NOT_ADMITTED')
    check('h armed twice -> NOT_ADMITTED', word('fs7_h', armed=['TestHidLoss: armed t_us=70000000'] * 2) == 'NOT_ADMITTED')
    check('h attach missing -> NOT_ADMITTED', word('fs7_h', attach=[]) == 'NOT_ADMITTED')
    check('h attach failed instead -> NOT_ADMITTED', word('fs7_h', attach=['TestHidLoss: attach failed error="x" t_us=1']) == 'NOT_ADMITTED')
    check('h test pad missing -> NOT_ADMITTED', word('fs7_h', pad=[]) == 'NOT_ADMITTED')
    check('h test pad twice -> NOT_ADMITTED', word('fs7_h', pad=[PAD, PAD]) == 'NOT_ADMITTED')
    check('h another pad -> NOT_ADMITTED', word('fs7_h', before=['Controller 3: "DualSense Wireless Controller" type=7 accel=1 gyro=1 path=x'])
          == 'NOT_ADMITTED')
    check('h fire missing -> NOT_ADMITTED', word('fs7_h', fire=[]) == 'NOT_ADMITTED')
    check('h fire sleep -> NOT_ADMITTED', word('fs7_h', fire=['TestHidLoss: fire mode=sleep t_us=135000000']) == 'NOT_ADMITTED')
    check('h done missing -> NOT_ADMITTED', word('fs7_h', done=[]) == 'NOT_ADMITTED')
    check('h done twice -> NOT_ADMITTED', word('fs7_h', done=['TestHidLoss: done t_us=138000000'] * 2) == 'NOT_ADMITTED')
    check('h stat missing (N5) -> NOT_ADMITTED', word('fs7_h', stat=[]) == 'NOT_ADMITTED')
    check('h stat twice -> NOT_ADMITTED', word('fs7_h', stat=st() * 2) == 'NOT_ADMITTED')
    check('h stat sleep -> NOT_ADMITTED', word('fs7_h', stat=st(mode='sleep')) == 'NOT_ADMITTED')
    w, res, _ = rd('fs7_h', case('fs7_h', stat=[stat_line().replace(' vp_effect=0', '')]))
    check('h stat without a field -> NOT_ADMITTED', w == 'NOT_ADMITTED' and res['stat'] is None)
    check('h stat inside an interleaved line parsed', word('fs7_h', stat=['[7][00:01:02.003] xx' + stat_line()]) == 'MEMBERS_PASS')
    check('h valid plus malformed stat -> NOT_ADMITTED', word('fs7_h', extra=['TestHidLoss: stat mode=hold main_late_max_us=1'])
          == 'NOT_ADMITTED')
    check('h pad_calls 0 -> NOT_ADMITTED', word('fs7_h', stat=st(pad_vib=0, pad_led=0, pad_trig=0)) == 'NOT_ADMITTED')
    check('h pad_calls 1 -> admitted', word('fs7_h', stat=st(pad_vib=1, pad_led=0, pad_trig=0)) == 'MEMBERS_PASS')
    check('h probes_posted - probes_run = 1 -> NOT_ADMITTED', word('fs7_h', stat=st(probes_run=299)) == 'NOT_ADMITTED')
    lg = mk_h(quit=False)
    check('h N5 no quit line -> admitted', rd('fs7_h', case('fs7_h', log=lg))[0] == 'MEMBERS_PASS')
    lg = mk_h(quit=False)
    lg.insert(lg.index(stat_line()), 'Event: quit')
    check('h N5 quit before stat -> NOT_ADMITTED', rd('fs7_h', case('fs7_h', log=lg))[0] == 'NOT_ADMITTED')
    lg = mk_h()
    j = lg.index('TestHidLoss: attach index=0 t_us=75000000')
    s = lg.pop(lg.index(stat_line()))
    lg.insert(j, s)
    check('h N5 stat before attach -> NOT_ADMITTED', rd('fs7_h', case('fs7_h', log=lg))[0] == 'NOT_ADMITTED')
    # admission - fs7_n (F18e f8_n1)
    w, res, _ = rd('fs7_n', case('fs7_n', vib=False))
    check('n no vibration line -> NOT_ADMITTED, row NO', w == 'NOT_ADMITTED' and row(res, 'adm', 'vibration port present') is False)
    check('n Haptics opened -> NOT_ADMITTED', word('fs7_n', before=['Haptics: pad audio device "DualSense" opened (48000 Hz, 4 ch)'])
          == 'NOT_ADMITTED')
    check('n Haptics disabled (N5) -> NOT_ADMITTED', word('fs7_n', before=['Haptics: disabled by KYTY_HAPTICS=0']) == 'NOT_ADMITTED')
    check('n A = 0 -> NOT_ADMITTED', word('fs7_n', A=0) == 'NOT_ADMITTED')
    check('n A = 1 -> admitted', word('fs7_n', A=1) == 'MEMBERS_PASS')
    check('n no stamp before the vibration line -> NOT_ADMITTED', rd('fs7_n', case('fs7_n', log=[x for x in mk_n(vib_stamp=False)
                                                                                                if not x.startswith('[3]')]))[0] == 'NOT_ADMITTED')
    check('n TestAudioLoss line -> NOT_ADMITTED', word('fs7_n', before=['TestAudioLoss: armed t_us=1']) == 'NOT_ADMITTED')
    check('n a pad line is a reference', word('fs7_n', before=[PAD]) == 'MEMBERS_PASS')
    # interference
    for tg in R.ORDER:
        for line, want in (('Window 1 minimized', 'NOT_ADMITTED'), ('Recovering Vulkan swapchain', 'NOT_ADMITTED'),
                           ('GamePatch: x', 'NOT_ADMITTED'), ('Window 1 lost keyboard focus', 'MEMBERS_PASS'),
                           ('Window 1 restored', 'MEMBERS_PASS'), ('AsyncPipelines: skipped draw 1', 'MEMBERS_PASS'),
                           ('[Vulkan][E] x', 'MEMBERS_PASS')):
            check('%s line %s -> %s' % (tg, line, want), word(tg, before=[line]) == want)
    # form
    for tg in R.ORDER:
        check('%s installed before adb0c82f-like other -> FORM_FAIL' % tg, word(tg, files=dict(installed_before='a' * 64)) == 'FORM_FAIL')
        check('%s installed before = FS7 -> FORM_FAIL' % tg, word(tg, files=dict(installed_before=R.BIN_EXPECT)) == 'FORM_FAIL')
        check('%s installed after other -> FORM_FAIL' % tg, word(tg, files=dict(installed_after=R.BIN_EXPECT)) == 'FORM_FAIL')
        check('%s installed after missing -> FORM_FAIL' % tg, word(tg, drop=('installed_after',)) == 'FORM_FAIL')
        check('%s manifest DIFFER -> FORM_FAIL' % tg, word(tg, files=dict(manifest_cmp='manifest cmp DIFFER only-before 1')) == 'FORM_FAIL')
        check('%s manifest missing -> FORM_FAIL' % tg, word(tg, drop=('manifest_cmp',)) == 'FORM_FAIL')
        check('%s admission precedes form' % tg, word(tg, files=dict(installed_before='x'), rev='3904522') == 'NOT_ADMITTED')
    # Fix members (item 467 (g)(3), item 487 (g)(3), N4 of item 518 (v)(4)) - both tags
    for tg in R.ORDER:
        w, res, out = rd(tg, case(tg, f8=[], f8_after=['FixF8: mode=1']))
        check('%s FixF8 line after the first GuestOut -> member YES, PASS (N4)' % tg, w == 'MEMBERS_PASS' and row(res, 'mem', 'FixF8') is True)
        n4 = [x for x in out if x.startswith('  N4 row')]
        check('%s FixF8 after: N4 row prints both lines, FixF8 line > first GuestOut line' % tg, len(n4) == 1 and
              res['n4_row'][0] > res['n4_row'][1] and 'order: after the first GuestOut' in [n for n, _ in res['mem'] if 'FixF8' in n][0])
        w, res, _ = rd(tg, case(tg, f8=[]))
        check('%s FixF8 line missing -> MEMBERS_FAIL' % tg, w == 'MEMBERS_FAIL' and row(res, 'mem', 'FixF8') is False)
        check('%s FixF8 two lines -> MEMBERS_FAIL' % tg, word(tg, f8=['FixF8: mode=1'], f8_after=['FixF8: mode=1']) == 'MEMBERS_FAIL')
        check('%s FixF8 mode=0 -> MEMBERS_FAIL' % tg, word(tg, f8=['FixF8: mode=0']) == 'MEMBERS_FAIL')
        check('%s FixF8 mode=1 plus mode=0 -> MEMBERS_FAIL' % tg, word(tg, f8=['FixF8: mode=1', 'FixF8: mode=0']) == 'MEMBERS_FAIL')
        check('%s FixF8 line of another form -> MEMBERS_FAIL' % tg, word(tg, f8=['FixF8: mode=1', 'FixF8: enabled']) == 'MEMBERS_FAIL')
        check('%s FixF8 inside an interleaved line counted' % tg, word(tg, f8=['[5][00:00:02.000] xxFixF8: mode=1']) == 'MEMBERS_PASS')
        for k in ('B24', 'B4'):
            other = 'B4' if k == 'B24' else 'B24'
            keep = ['Fix%s: mode=1' % other]
            w, res, _ = rd(tg, case(tg, fixes=keep))
            check('%s Fix%s missing -> MEMBERS_FAIL' % (tg, k), w == 'MEMBERS_FAIL' and row(res, 'mem', 'Fix%s:' % k) is False)
            check('%s Fix%s after the first GuestOut -> MEMBERS_FAIL' % (tg, k),
                  word(tg, fixes=keep, f8_after=['Fix%s: mode=1' % k]) == 'MEMBERS_FAIL')
            check('%s Fix%s mode=0 -> MEMBERS_FAIL' % (tg, k), word(tg, fixes=keep + ['Fix%s: mode=0' % k]) == 'MEMBERS_FAIL')
            check('%s Fix%s two lines -> MEMBERS_FAIL' % (tg, k), word(tg, fixes=keep + ['Fix%s: mode=1' % k] * 2) == 'MEMBERS_FAIL')
            check('%s Fix%s mode=1 plus mode=0 -> MEMBERS_FAIL' % (tg, k),
                  word(tg, fixes=keep + ['Fix%s: mode=1' % k, 'Fix%s: mode=0' % k]) == 'MEMBERS_FAIL')
        check('%s FixB42 lines are not FixB4 lines' % tg,
              word(tg, extra=['FixB42: mode=1 hit=1 applied=1', 'FixB42Ext: mode=1 extent=480x270']) == 'MEMBERS_PASS')
        w, res, _ = rd(tg, case(tg, modl=False, log=None))
        check('%s first GuestOut = the level start line when MODL absent' % tg, w == 'MEMBERS_PASS' and res['first_guest'] is not None)
        lg = [x for x in (mk_h() if tg == 'fs7_h' else mk_n()) if not x.startswith('GuestOut')]
        w, res, _ = rd(tg, case(tg, log=lg))
        check('%s no GuestOut line -> B24/B4 not read, not entered -> HARM_FAIL' % tg, row(res, 'mem', 'FixB24') is None and
              row(res, 'mem', 'FixB4') is None and row(res, 'mem', 'FixF8') is True and w == 'HARM_FAIL')
    # fs7_h members (b24_h1)
    for k, v, want in (('main_late_max_us', 2700000, 'MEMBERS_PASS'), ('main_late_max_us', 2699999, 'MEMBERS_FAIL'),
                       ('po_wait_max_us', 2700000, 'MEMBERS_PASS'), ('po_wait_max_us', 2699999, 'MEMBERS_FAIL'),
                       ('pad_wait_max_us', 49999, 'MEMBERS_PASS'), ('pad_wait_max_us', 50000, 'MEMBERS_FAIL'),
                       ('guest_sdl', 1, 'MEMBERS_FAIL')):
        check('h %s %d -> %s' % (k, v, want), word('fs7_h', stat=st(**{k: v})) == want)
    check('h frame 1000000 in the window -> MEMBERS_FAIL', word('fs7_h', win=frames(5, start=300) + [fr(305, 1000000)]) == 'MEMBERS_FAIL')
    check('h frame 999999 in the window -> PASS', word('fs7_h', win=frames(5, start=300) + [fr(305, 999999)]) == 'MEMBERS_PASS')

    def pre_fire(long_dt, after_k, after_dt=100000):
        lg = mk_h()
        fl = [x for x in lg if x.startswith('TestHidLoss: fire')][0]
        i = lg.index(fl)
        return lg[:i] + [fr(290, long_dt)] + [fr(291 + k, after_dt) for k in range(after_k)] + lg[i:]
    w, res, _ = rd('fs7_h', case('fs7_h', log=pre_fire(2000000, 10)))
    check('h long frame 1.0 s before fire -> in the wide window -> MEMBERS_FAIL', w == 'MEMBERS_FAIL' and res['k2_wide'] == [290]
          and res['k2_strict'] == [])
    w, res, _ = rd('fs7_h', case('fs7_h', log=pre_fire(2000000, 11)))
    check('h long frame 1.1 s before fire -> outside the window -> HARM_FAIL', w == 'HARM_FAIL' and res['k2_wide'] == [])
    w, res, _ = rd('fs7_h', case('fs7_h', win=frames(5, start=300) + [fr(305, 1000000)]))
    check('h frame in the window is not a harm frame', row(res, 'harm', 'outside the stand window') is True)
    check('h frame >= 1 s after the stat line -> HARM_FAIL', word('fs7_h', post=frames(10, start=800) + [fr(900, 1000000)]) == 'HARM_FAIL')
    # fs7_h identities
    w, res, _ = rd('fs7_h', case('fs7_h', stat=st(pad_calls=999)))
    check('h pad_calls sum broken -> IDENT_FAIL', w == 'IDENT_FAIL' and row(res, 'ident', 'pad_calls =') is False)
    w, res, _ = rd('fs7_h', case('fs7_h', stat=st(probes_run=301)))
    check('h probes_run > posted -> identity NO (admission first)', row(res, 'ident', 'probes_run <=') is False and w == 'NOT_ADMITTED')
    check('h removed 1 in hold -> IDENT_FAIL', word('fs7_h', stat=st(removed=1)) == 'IDENT_FAIL')
    for tt, why in (((75, 75, 135, 138), 'armed = attach'), ((70, 136, 135, 138), 'attach > fire'), ((70, 75, 139, 138), 'fire > done')):
        w, res, _ = rd('fs7_h', case('fs7_h', t=tt))
        check('h t_us order %s -> IDENT_FAIL' % why, w == 'IDENT_FAIL' and row(res, 'ident', 't_us armed') is False)
    check('h t_us fire = done -> PASS', word('fs7_h', t=(70, 75, 135, 135)) == 'MEMBERS_PASS')
    check('h member fail precedes identity fail', word('fs7_h', stat=st(guest_sdl=1, pad_calls=999)) == 'MEMBERS_FAIL')
    check('h identity fail precedes harm fail', word('fs7_h', stat=st(pad_calls=999), idx=10) == 'IDENT_FAIL')
    w, res, _ = rd('fs7_h', case('fs7_h', stat=[]))
    check('h identities not read without stat', all(v is None for _, v in res['ident'][:3]))
    # fs7_n members (f8_n1 + item 487 (g)(3))
    w, res, _ = rd('fs7_n', case('fs7_n', f8_at=[300.5]))
    check('n F8 line -> MEMBERS_FAIL', w == 'MEMBERS_FAIL' and row(res, 'mem', 'F8 lines') is False)
    check('n other SDL_QueueAudio failed text is not F8', word('fs7_n', extra=['AudioOut: SDL_QueueAudio failed: Out of memory'])
          == 'MEMBERS_PASS')
    w, res, out = rd('fs7_n', case('fs7_n', init=lambda t: 2 if t == 400 else 1))
    check('n init_calls 2 in the middle, F = 0 -> MEMBERS_FAIL', w == 'MEMBERS_FAIL')
    w, res, out = rd('fs7_n', case('fs7_n', init=lambda t: 2 if t == 400 else 1, before=['AudioOut: SDL audio init failed: x']))
    check('n init_calls 2, F = 1 (AudioOut) -> HOST_NOISE', w == 'HOST_NOISE' and res['F'] == 1)
    check('n init_calls 2, F = 1 (AudioIn) -> HOST_NOISE',
          word('fs7_n', init=lambda t: 2 if t == 400 else 1, before=['AudioIn: SDL init failed: x']) == 'HOST_NOISE')
    check('n init_calls 2, F = 1 and another failure -> MEMBERS_FAIL',
          word('fs7_n', init=lambda t: 2 if t == 400 else 1, before=['AudioOut: SDL audio init failed: x'], f8_at=[300.5]) == 'MEMBERS_FAIL')
    check('n F = 1 with init_calls 1 -> PASS', word('fs7_n', before=['AudioOut: SDL audio init failed: x']) == 'MEMBERS_PASS')
    check('n init_calls 0 everywhere -> PASS', word('fs7_n', init=lambda t: 0) == 'MEMBERS_PASS')
    check('n acq 250 last -> PASS', word('fs7_n', acq=lambda t: 250) == 'MEMBERS_PASS')
    check('n acq 249 last -> MEMBERS_FAIL', word('fs7_n', acq=lambda t: 249) == 'MEMBERS_FAIL')
    check('n acq: the last row is read', word('fs7_n', acq=lambda t: 300 if t < 849 else 249) == 'MEMBERS_FAIL')
    check('n status 2 -> PASS', word('fs7_n', status=2) == 'MEMBERS_PASS')
    check('n status 0 -> MEMBERS_FAIL', word('fs7_n', status=0) == 'MEMBERS_FAIL')
    check('n status 3 -> MEMBERS_FAIL', word('fs7_n', status=3) == 'MEMBERS_FAIL')
    check('n status 0 at dev 0 not read', word('fs7_n', mod=lambda t, p, r: dict(r, dev=0, status=0) if p == 0 else r) == 'MEMBERS_PASS')
    check('n status 0 on one row -> MEMBERS_FAIL', word('fs7_n', mod=lambda t, p, r: dict(r, status=0) if t == 500 and p == 2 else r)
          == 'MEMBERS_FAIL')
    w, res, _ = rd('fs7_n', case('fs7_n', end=11))
    check('n no AudioStat rows -> NOT_EVALUABLE', w == 'NOT_EVALUABLE' and row(res, 'mem', 'acq >= 250') is None)
    w, res, _ = rd('fs7_n', case('fs7_n', before=['TestHidLoss: armed t_us=1']))
    check('n TestHidLoss line -> MEMBERS_FAIL', w == 'MEMBERS_FAIL' and row(res, 'mem', 'TestHidLoss') is False)
    w, res, _ = rd('fs7_n', case('fs7_n', extra=['AudioStat: t_us=1 port=0 garbage']))
    check('n malformed AudioStat counted, still PASS', w == 'MEMBERS_PASS' and res['astat_bad'] == 1)
    check('n AudioStat rows counted (2 ports x 839 s)', rd('fs7_n', case('fs7_n'))[1]['astat_rows'] == 2 * 839)
    check('n AudioStat inside an interleaved line parsed', rd('fs7_n', case('fs7_n', extra=['[7][00:20:00.000] xxAudioStat: t_us=900000000 port=2 dev=4 status=1 queued=0 pushes=99999 q_fail=0 init_calls=1 acq=290']))[1]['last_astat']['acq'] == 290)
    # fs7_n identities are references (N2)
    check('n q_fail > pushes -> reference only, PASS', word('fs7_n', mod=lambda t, p, r: dict(r, q_fail=r['pushes'] + 1) if t == 300 else r)
          == 'MEMBERS_PASS')
    w, res, _ = rd('fs7_n', case('fs7_n', mod=lambda t, p, r: dict(r, pushes=1) if t == 300 else r))
    check('n pushes decrease -> identity row NO, word PASS', w == 'MEMBERS_PASS' and row(res, 'ident', 'do not decrease') is False)
    # harm (both tags)
    for tg in R.ORDER:
        for mk in ('Unhandled exception:', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort:', 'ErrorDeviceLost'):
            check('%s death %s in log -> HARM_FAIL' % (tg, mk), word(tg, extra=[mk + ' x']) == 'HARM_FAIL')
        check('%s death in stdout -> HARM_FAIL' % tg, word(tg, stdout=['--- Fatal Error ---']) == 'HARM_FAIL')
        check('%s no stdout -> NOT_EVALUABLE' % tg, word(tg, drop=('stdout',)) == 'NOT_EVALUABLE')
        check('%s frame 1000000 after the scene -> HARM_FAIL' % tg, word(tg, extra=[fr(990, 1000000)]) == 'HARM_FAIL')
        check('%s frame 999999 after the scene -> PASS' % tg, word(tg, extra=[fr(990, 999999)]) == 'MEMBERS_PASS')
        check('%s frame >= 1 s before the first scene frame not counted' % tg,
              word(tg, head=[fr(1, 2000000, 99), fr(2, 16000, 100)]) == 'MEMBERS_PASS')
        check('%s frame >= 1 s on the first scene frame not counted' % tg,
              word(tg, head=[fr(1, 16000, 50), fr(2, 2000000, 100)]) == 'MEMBERS_PASS')
        check('%s frame >= 1 s after a scene change not counted' % tg,
              word(tg, extra=['GuestOut: Level has started: hub', fr(999, 2000000)]) == 'MEMBERS_PASS')
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
        lg = [x for x in (mk_h() if tg == 'fs7_h' else mk_n()) if x != GUEST]
        check('%s not entered -> HARM_FAIL' % tg, rd(tg, case(tg, log=lg))[0] == 'HARM_FAIL')
        check('%s member fail precedes harm' % tg, word(tg, f8=[], idx=10) == 'MEMBERS_FAIL')
        # exit is a report row
        check('%s close_killed True, close_rc None - still PASS (exit not a gate)' % tg,
              word(tg, run=run_json(tg, close_killed=True, close_rc=None)) == 'MEMBERS_PASS')
        w, res, out = rd(tg, case(tg, run=run_json(tg, close_rc=1, close_s=40.2)))
        check('%s exit row prints close_rc 1 close_s 40.2' % tg, w == 'MEMBERS_PASS' and any('close_rc 1 close_s 40.2' in x for x in out
                                                                                            if x.startswith('  EXIT')))
    # missing log
    for tg in R.ORDER:
        w, res, _ = rd(tg, case(tg, drop=('log',)))
        check('%s no log -> NOT_ADMITTED' % tg, w == 'NOT_ADMITTED' and res['log_sha256'] is None)
    # CLI: strict cp1250 without PYTHONIOENCODING, ASCII only, json, unknown tag
    for tg in R.ORDER:
        d = case(tg)
        env = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
        env['PYTHONIOENCODING'] = 'cp1250:strict'
        p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag', tg], capture_output=True, env=env)
        check('%s cli cp1250 strict rc 0' % tg, p.returncode == 0)
        check('%s cli ASCII only' % tg, all(b < 128 for b in p.stdout))
        check('%s cli READING line' % tg, ('  READING %s MEMBERS_PASS' % tg).encode() in p.stdout)
        env2 = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
        p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag', tg], capture_output=True, env=env2)
        check('%s cli without PYTHONIOENCODING rc 0' % tg, p.returncode == 0)
        jp = os.path.join(T, 'o_%s.json' % tg)
        p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag', tg, '--json', jp], capture_output=True)
        check('%s cli json written' % tg, p.returncode == 0 and json.load(open(jp))['word'] == 'MEMBERS_PASS')
    p = subprocess.run([sys.executable, TARGET, 'b24_h1'], capture_output=True)
    check('cli unknown tag refused', p.returncode != 0 and b'unknown tag' in p.stderr)
    p = subprocess.run([sys.executable, TARGET, '--dir', T], capture_output=True)
    check('cli --dir without --tag refused', p.returncode != 0)
finally:
    shutil.rmtree(T, ignore_errors=True)

print('checks %d failed %d' % (N[0], len(FAIL)))
if FAIL:
    sys.exit(1)
print('ALL OK')
