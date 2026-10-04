"""F18e (HPP-541): fixtures of f18e_read.py - every member, edge and identity of the seal docs/track-f/f18e.md section 4 (item 441 (g),
(d)(4); item 448 (v); item 453 (v) N1, N2, N5).  Ends with ALL OK.
usage: python test_f18e_read.py   (ASCII only)"""
import hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'f18e_read.py')
sys.path.insert(0, HERE)
import f18e_read as R

print('suite test_f18e_read.py sha256 %s target f18e_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(open(TARGET, 'rb').read()).hexdigest()))
N = [0]
FAIL = []


def check(name, cond):
    N[0] += 1
    if not cond:
        FAIL.append(name)
        print('FAIL', name)


GUEST = 'GuestOut: Level has started: underwater_aerial_garden'
OPENED = 'AudioOut: opened SDL device "(system default)" (48000 Hz, 2 ch, format 0x8120)'
VIB = 'AudioOut: vibration port 3 (48000 Hz, 2 ch, 512 frames, float) -> pad haptics'
F8 = 'AudioOut: SDL_QueueAudio failed: Invalid audio device ID'
T_VIB = 9.464
ARMED, FIRE, DONE = 10, 70, 72


def stamp(t):
    ms = int(round(t * 1000))
    return '[3][%02d:%02d:%02d.%03d]' % (ms // 3600000, (ms // 60000) % 60, (ms // 1000) % 60, ms % 1000)


def mk_log(tag, A=3, end=None, r1=100, r2=None, f8=None, status=1, init=None, acq=None, mod=None, stand=None, fixlines=None,
           before=None, extra=None, frames=None, vib=True, vib_stamp=True, ports=(0, 1, 2), armed=ARMED, fire=FIRE, done=DONE,
           done_attempts=300, head=None):
    sp = R.SPEC[tag]
    s_tag = sp['stand']
    if end is None:
        end = 340 if s_tag else 850
    if r2 is None:
        r2 = (5 * r1 if tag == 'f8_s0' else r1) if s_tag else r1
    if f8 is None:
        f8 = {'f8_s0': [FIRE + 9.5], 'f8_n0': [T_VIB + 760.0]}.get(tag, [])
    L = ['[3][00:00:01.000] start', '  version: Fork build arigandores/KytyPS5 79b14ef']
    L += fixlines if fixlines is not None else (['FixF8: mode=1'] if sp['fix'] == '1' else [])
    L += stand if stand is not None else (['TestAudioLoss: config on delay_s=60 mode=retry'] if s_tag else [])
    L += before or []
    L += ['[3][00:00:05.000] open'] + [OPENED] * A
    if vib:
        L += ([stamp(T_VIB) + ' vib'] if vib_stamp else []) + [VIB]
    L += [GUEST] + (head if head is not None else ['FrameTrace: n=1 dt_us=16000 draws=50', 'FrameTrace: n=2 dt_us=16000 draws=100'])
    L += frames if frames is not None else ['FrameTrace: n=%d dt_us=33000 draws=3000' % (i + 3) for i in range(40)]
    ev = []
    if s_tag:
        if armed is not None:
            ev.append((armed, 1, 'TestAudioLoss: armed t_us=%d' % (armed * 1000000)))
        if fire is not None:
            ev.append((fire, 1, 'TestAudioLoss: fire t_us=%d' % (fire * 1000000)))
        if done is not None:
            ev.append((done, 1, 'TestAudioLoss: done attempts=%d t_us=%d' % (done_attempts, done * 1000000)))
    for tf in f8:
        ev.append((tf, 0, stamp(tf) + ' f8'))
        ev.append((tf, 2, F8))
    first_f8 = min(f8) if f8 else None
    for t in range(11, end):
        if s_tag:
            pushes = r1 * min(t, DONE) + r2 * max(0, t - DONE)
        else:
            pushes = r1 * t
        if init is not None:
            ic = init(t)
        elif sp['fix'] == '1':
            ic = 1
        elif s_tag:
            ic = 3 + (t - ARMED) // 3 if t < FIRE else (323 if t >= DONE else 3 + (FIRE - ARMED) // 3 + 150)
        else:
            ic = 3 + int((t - T_VIB) / 3)
        if acq is not None:
            ac = acq(t)
        elif sp['fix'] == '0':
            ac = 0
        elif s_tag:
            ac = 3 + (t - ARMED) // 3 if t < FIRE else (330 + (t - DONE) // 3 if t >= DONE else 200)
        else:
            ac = 3 + int((t - T_VIB) / 3)
        ev.append((t, 0, stamp(t) + ' tick'))
        for p in ports:
            st = status
            if tag == 'f8_s0' and first_f8 is not None and t > first_f8:
                st = 0
            row = dict(t=t * 1000000, port=p, dev=p + 2, status=st, queued=7680, pushes=pushes, q_fail=0, init_calls=ic, acq=ac)
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
    e = {'KYTY_FIX_F8': sp['fix'], 'KYTY_AV_TRACE': '1', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_REC': 'x',
         'KYTY_FRAME_TRACE': 'lite'}
    if sp['stand']:
        e['KYTY_TEST_AUDIOLOSS'] = '60:retry'
    if env:
        for k, v in env.items():
            if v is None:
                e.pop(k, None)
            else:
                e[k] = v
    return dict(binary_sha256=R.BIN_EXPECT if binary is None else binary, env=e, attempts=[a],
                prereg=dict(sha256=hashlib.sha256(SEAL_TEXT.encode()).hexdigest() if prereg is None else prereg))


T = tempfile.mkdtemp(prefix='f18e_fix_')
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


ALL = ('f8_s0', 'f8_s1', 'f8_n0', 'f8_n1')
try:
    # positive tags
    for tg in ALL:
        w, res, out = rd(tg, case(tg))
        check('positive %s -> MEMBERS_PASS (got %s)' % (tg, w), w == 'MEMBERS_PASS')
        check('positive %s has READING line' % tg, out[-1] == '  READING %s MEMBERS_PASS' % tg)
        check('positive %s A = 3, T_vib 9.464' % tg, res['a'] == 3 and abs(res['t_vib'] - T_VIB) < 1e-9)
    # admission - binary, seal, json
    for tg in ALL:
        check('%s json binary other -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, binary=R.WANT)) == 'NOT_ADMITTED')
    check('installed_sha other -> NOT_ADMITTED', word('f8_s1', files=dict(installed_sha=R.WANT)) == 'NOT_ADMITTED')
    check('installed_sha missing -> NOT_ADMITTED', word('f8_s1', drop=('installed_sha',)) == 'NOT_ADMITTED')
    check('no json -> NOT_ADMITTED', word('f8_n1', drop=('run',)) == 'NOT_ADMITTED')
    check('prereg sha mismatch -> NOT_ADMITTED', word('f8_s0', run=run_json('f8_s0', prereg='0' * 64)) == 'NOT_ADMITTED')
    check('seal file missing -> NOT_ADMITTED', word('f8_s0', drop=('seal',)) == 'NOT_ADMITTED')
    check('seal file edited after the run -> NOT_ADMITTED', word('f8_n0', seal='seal fixture text edited\n') == 'NOT_ADMITTED')
    w, res, _ = rd('f8_s1', case('f8_s1', drop=('bin',)))
    check('version file missing -> reference only, still PASS', w == 'MEMBERS_PASS' and row(res, 'adm', 'version string') is None)
    # admission - env
    for tg in ALL:
        other = '1' if R.SPEC[tg]['fix'] == '0' else '0'
        check('%s KYTY_FIX_F8 other -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_FIX_F8': other})) == 'NOT_ADMITTED')
        check('%s KYTY_FIX_F8 absent -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_FIX_F8': None})) == 'NOT_ADMITTED')
        check('%s KYTY_HAPTICS=1 in env (N5) -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_HAPTICS': '1'})) == 'NOT_ADMITTED')
        check('%s KYTY_AV_TRACE absent -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_AV_TRACE': None})) == 'NOT_ADMITTED')
        check('%s extra KYTY_FIX_F10 -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_FIX_F10': '1'})) == 'NOT_ADMITTED')
        check('%s KYTY_GAME_PATCH -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_GAME_PATCH': 'p'})) == 'NOT_ADMITTED')
        check('%s KYTY_GPU_CHECKPOINTS -> NOT_ADMITTED' % tg, word(tg, run=run_json(tg, env={'KYTY_GPU_CHECKPOINTS': '0'})) == 'NOT_ADMITTED')
    check('s0 stand 30:retry -> NOT_ADMITTED', word('f8_s0', run=run_json('f8_s0', env={'KYTY_TEST_AUDIOLOSS': '30:retry'})) == 'NOT_ADMITTED')
    check('s1 stand absent -> NOT_ADMITTED', word('f8_s1', run=run_json('f8_s1', env={'KYTY_TEST_AUDIOLOSS': None})) == 'NOT_ADMITTED')
    check('n0 stand present -> NOT_ADMITTED', word('f8_n0', run=run_json('f8_n0', env={'KYTY_TEST_AUDIOLOSS': '60:retry'})) == 'NOT_ADMITTED')
    check('n1 stand empty string present -> NOT_ADMITTED', word('f8_n1', run=run_json('f8_n1', env={'KYTY_TEST_AUDIOLOSS': ''})) == 'NOT_ADMITTED')
    # admission - log lines
    for tg in ALL:
        check('%s no vibration line -> NOT_ADMITTED' % tg, word(tg, vib=False) == 'NOT_ADMITTED')
        check('%s Haptics opened -> NOT_ADMITTED' % tg,
              word(tg, before=['Haptics: pad audio device "DualSense" opened (48000 Hz, 4 ch)']) == 'NOT_ADMITTED')
        check('%s Haptics disabled (N5) -> NOT_ADMITTED' % tg, word(tg, before=['Haptics: disabled by KYTY_HAPTICS=0']) == 'NOT_ADMITTED')
        check('%s A = 0 -> NOT_ADMITTED' % tg, word(tg, A=0) == 'NOT_ADMITTED')
    check('Haptics pad device failed line - admitted', word('f8_n1', before=['Haptics: pad audio device "x" failed: no']) == 'MEMBERS_PASS')
    check('no stamp before the vibration line -> NOT_ADMITTED',
          rd('f8_s1', case('f8_s1', log=[l for l in mk_log('f8_s1') if not l.startswith('[3][')]))[0] == 'NOT_ADMITTED')
    w, res, _ = rd('f8_s1', case('f8_s1', vib_stamp=False))
    check('T_vib = last stamp before the vibration line (no own stamp -> 5.0)', abs(res['t_vib'] - 5.0) < 1e-9 and w == 'MEMBERS_PASS')
    w, res, _ = rd('f8_n1', case('f8_n1', A=1))
    check('A = 1 admitted, A counted only before the vibration line', w == 'MEMBERS_PASS' and res['a'] == 1)
    w, res, _ = rd('f8_n1', case('f8_n1', extra=[OPENED, OPENED]))
    check('opened lines after the vibration line not in A', res['a'] == 3)
    check('=1 FixF8 line missing -> NOT_ADMITTED', word('f8_s1', fixlines=[]) == 'NOT_ADMITTED')
    check('=1 FixF8 two lines -> NOT_ADMITTED', word('f8_n1', fixlines=['FixF8: mode=1', 'FixF8: mode=1']) == 'NOT_ADMITTED')
    check('=1 FixF8 mode=0 -> NOT_ADMITTED', word('f8_n1', fixlines=['FixF8: mode=0']) == 'NOT_ADMITTED')
    check('=0 FixF8 line present -> NOT_ADMITTED', word('f8_n0', fixlines=['FixF8: mode=1']) == 'NOT_ADMITTED')
    check('s config on missing -> NOT_ADMITTED', word('f8_s0', stand=[]) == 'NOT_ADMITTED')
    check('s config on twice -> NOT_ADMITTED', word('f8_s1', stand=['TestAudioLoss: config on delay_s=60 mode=retry'] * 2) == 'NOT_ADMITTED')
    check('s config on delay 30 -> NOT_ADMITTED', word('f8_s1', stand=['TestAudioLoss: config on delay_s=30 mode=retry']) == 'NOT_ADMITTED')
    check('s config invalid line -> NOT_ADMITTED', word('f8_s0', stand=['TestAudioLoss: config on delay_s=60 mode=retry',
                                                                        'TestAudioLoss: config invalid value="x" (expected <s>[:retry]), stand off'])
          == 'NOT_ADMITTED')
    check('n any TestAudioLoss line -> NOT_ADMITTED', word('f8_n1', stand=['TestAudioLoss: armed t_us=1']) == 'NOT_ADMITTED')
    for line, want in (('Window 1 minimized', 'NOT_ADMITTED'), ('Recovering Vulkan swapchain', 'NOT_ADMITTED'), ('GamePatch: x', 'NOT_ADMITTED'),
                       ('Window 1 lost keyboard focus', 'MEMBERS_PASS'), ('Window 1 restored', 'MEMBERS_PASS'),
                       ('AsyncPipelines: skipped draw 1', 'MEMBERS_PASS'), ('[Vulkan][E] x', 'MEMBERS_PASS')):
        check('interference %s -> %s' % (line, want), word('f8_s1', before=[line]) == want)
    # form
    check('installed before other -> FORM_FAIL', word('f8_n1', files=dict(installed_before=R.BIN_EXPECT)) == 'FORM_FAIL')
    check('installed after other -> FORM_FAIL', word('f8_n1', files=dict(installed_after=R.BIN_EXPECT)) == 'FORM_FAIL')
    check('manifest DIFFER -> FORM_FAIL', word('f8_s0', files=dict(manifest_cmp='manifest cmp DIFFER only-before 1')) == 'FORM_FAIL')
    check('manifest missing -> FORM_FAIL', word('f8_s0', drop=('manifest_cmp',)) == 'FORM_FAIL')
    check('admission precedes form', word('f8_s0', files=dict(installed_before='x'), vib=False) == 'NOT_ADMITTED')
    # f8_s0 members
    check('s0 no fire -> MEMBERS_FAIL', word('f8_s0', fire=None) == 'MEMBERS_FAIL')
    check('s0 no done -> MEMBERS_FAIL', word('f8_s0', done=None) == 'MEMBERS_FAIL')
    check('s0 done attempts=299 -> MEMBERS_FAIL', word('f8_s0', done_attempts=299) == 'MEMBERS_FAIL')
    check('s0 no F8 line with fire and done -> MECHANISM_REFUTED', word('f8_s0', f8=[]) == 'MECHANISM_REFUTED')
    check('s0 no F8 line, refusal of admission first', word('f8_s0', f8=[], A=0) == 'NOT_ADMITTED')
    check('s0 F8 at fire + 9.5 s (up = fire + 10 s exactly) -> PASS', word('f8_s0', f8=[FIRE + 9.5]) == 'MEMBERS_PASS')
    check('s0 F8 at fire + 10.5 s (low = fire + 10, up = fire + 11) -> NOT_EVALUABLE', word('f8_s0', f8=[FIRE + 10.5]) == 'NOT_EVALUABLE')
    check('s0 F8 at fire + 11.5 s (low > fire + 10) -> MEMBERS_FAIL', word('f8_s0', f8=[FIRE + 11.5]) == 'MEMBERS_FAIL')
    w, res, _ = rd('f8_s0', case('f8_s0', f8=[FIRE + 3.5, FIRE + 30.5]))
    check('s0 first F8 line counts (bracket of the first)', w == 'MEMBERS_PASS' and res['f8_low'] == (FIRE + 3) * 1000000
          and res['f8_up'] == (FIRE + 4) * 1000000 and res['f8'] == 2)
    check('s0 init_calls first after done 256 -> PASS', word('f8_s0', init=lambda t: 256 if t >= DONE else 10) == 'MEMBERS_PASS')
    check('s0 init_calls first after done 255 -> MEMBERS_FAIL',
          word('f8_s0', init=lambda t: (255 if t == DONE else 400) if t >= DONE else 10) == 'MEMBERS_FAIL')
    check('s0 ratio exactly 5 -> PASS', word('f8_s0', r1=100, r2=500) == 'MEMBERS_PASS')
    check('s0 ratio 4.99 -> MEMBERS_FAIL', word('f8_s0', r1=100, r2=499) == 'MEMBERS_FAIL')
    check('s0 one port of three below 5 -> MEMBERS_FAIL', word('f8_s0', mod=lambda t, p, r: dict(r, pushes=r['pushes'] - (
        (400 * max(0, t - DONE)) if p == 1 else 0))) == 'MEMBERS_FAIL')
    check('s0 a port missing in W2 -> NOT_EVALUABLE', word('f8_s0', mod=lambda t, p, r: None if (p == 2 and t >= DONE) else r) == 'NOT_EVALUABLE')
    check('s0 W1 empty -> NOT_EVALUABLE', word('f8_s0', mod=lambda t, p, r: None if t < FIRE else r) == 'NOT_EVALUABLE')
    check('s0 dev = 0 port ignored in W1', word('f8_s0', mod=lambda t, p, r: dict(r, dev=0, pushes=0) if p == 2 else r) == 'MEMBERS_PASS')
    check('s0 W1 upper edge: row at t = fire excluded (jump there)',
          word('f8_s0', r1=100, r2=500, mod=lambda t, p, r: dict(r, pushes=r['pushes'] + (1000 if t >= FIRE else 0))) == 'MEMBERS_PASS')
    check('s0 W1 lower edge: row at armed + 5 s - 1 s excluded',
          word('f8_s0', r1=100, r2=500, mod=lambda t, p, r: dict(r, pushes=r['pushes'] - (50 if t < ARMED + 5 else 0))) == 'MEMBERS_PASS')
    check('s0 W1 lower edge: row at armed + 5 s included (only 2 rows in W1)',
          word('f8_s0', mod=lambda t, p, r: r if (t >= DONE or t in (ARMED + 5, ARMED + 6)) else None) == 'MEMBERS_PASS')
    check('s0 death marker -> still MEMBERS_PASS (harm is a reference)', word('f8_s0', extra=['--- Fatal Error ---']) == 'MEMBERS_PASS')
    # f8_s1 members
    check('s1 one F8 line -> MEMBERS_FAIL', word('f8_s1', f8=[100.5]) == 'MEMBERS_FAIL')
    check('s1 no fire -> MEMBERS_FAIL', word('f8_s1', fire=None) == 'MEMBERS_FAIL')
    check('s1 done attempts=301 -> MEMBERS_FAIL', word('f8_s1', done_attempts=301) == 'MEMBERS_FAIL')
    check('s1 last init_calls 2, F = 0 -> MEMBERS_FAIL', word('f8_s1', init=lambda t: 1 if t < 300 else 2) == 'MEMBERS_FAIL')
    check('s1 last init_calls 2, AudioOut init failed (F = 1) -> HOST_NOISE',
          word('f8_s1', init=lambda t: 1 if t < 300 else 2, before=['AudioOut: SDL audio init failed: x']) == 'HOST_NOISE')
    check('s1 last init_calls 2, AudioIn init failed (F = 1) -> HOST_NOISE',
          word('f8_s1', init=lambda t: 1 if t < 300 else 2, extra=['AudioIn: SDL init failed: x']) == 'HOST_NOISE')
    check('s1 F = 1 but another member fails too -> MEMBERS_FAIL',
          word('f8_s1', init=lambda t: 1 if t < 300 else 2, before=['AudioOut: SDL audio init failed: x'], f8=[100.5]) == 'MEMBERS_FAIL')
    check('s1 F = 1 with init_calls <= 1 -> PASS', word('f8_s1', before=['AudioOut: SDL audio init failed: x']) == 'MEMBERS_PASS')
    w, res, out = rd('f8_s1', case('f8_s1', init=lambda t: 1 if t < 300 else 2, before=['AudioOut: SDL audio init failed: x'] * 2))
    check('s1 F printed', res['F'] == 2 and any('F = 2' in x for x in out))
    check('s1 earlier init_calls 2, last 1 -> member by the letter (last row) passes',
          word('f8_s1', init=lambda t: 2 if t == 100 else 1) == 'MEMBERS_PASS')
    check('s1 acq last 300 -> PASS', word('f8_s1', acq=lambda t: 300 if t == 339 else 5) == 'MEMBERS_PASS')
    check('s1 acq last 299 -> MEMBERS_FAIL', word('f8_s1', acq=lambda t: 299 if t == 339 else 5) == 'MEMBERS_FAIL')
    check('s1 status 2 rows -> PASS (item 448 (v))', word('f8_s1', status=2) == 'MEMBERS_PASS')
    w, res, out = rd('f8_s1', case('f8_s1', mod=lambda t, p, r: dict(r, status=2) if t < 40 else r))
    check('s1 status 1/2 mix -> PASS, status 2 count printed', w == 'MEMBERS_PASS' and res['status2'] == 29 * 3
          and any('status 2: 87' in x for x in out))
    check('s1 one status 0 row -> MEMBERS_FAIL', word('f8_s1', mod=lambda t, p, r: dict(r, status=0) if (t == 200 and p == 1) else r)
          == 'MEMBERS_FAIL')
    check('s1 status 0 with dev = 0 ignored -> PASS',
          word('f8_s1', mod=lambda t, p, r: dict(r, status=0, dev=0) if (t == 200 and p == 1) else r) == 'MEMBERS_PASS')
    check('s1 status 3 -> MEMBERS_FAIL', word('f8_s1', mod=lambda t, p, r: dict(r, status=3) if t == 200 else r) == 'MEMBERS_FAIL')
    check('s1 no AudioStat rows -> NOT_EVALUABLE', word('f8_s1', ports=()) == 'NOT_EVALUABLE')
    check('s1 ratio 0.95 -> PASS', word('f8_s1', r1=100, r2=95) == 'MEMBERS_PASS')
    check('s1 ratio 1.05 -> PASS', word('f8_s1', r1=100, r2=105) == 'MEMBERS_PASS')
    check('s1 ratio 0.949 -> MEMBERS_FAIL', word('f8_s1', r1=1000, r2=949) == 'MEMBERS_FAIL')
    check('s1 ratio 1.051 -> MEMBERS_FAIL', word('f8_s1', r1=1000, r2=1051) == 'MEMBERS_FAIL')
    check('s1 W2 lower edge: row at done + 5 s - 1 s excluded',
          word('f8_s1', r1=100, r2=105, mod=lambda t, p, r: dict(r, pushes=r['pushes'] - (200 if t < DONE + 5 else 0))) == 'MEMBERS_PASS')
    check('s1 W2 lower edge: row at done + 5 s included (2 rows in W2)', word('f8_s1', end=DONE + 7) == 'MEMBERS_PASS')
    check('s1 W2 one row -> NOT_EVALUABLE', word('f8_s1', end=DONE + 6) == 'NOT_EVALUABLE')
    # harm (f8_s1, f8_n1)
    for tg in ('f8_s1', 'f8_n1'):
        for mk in ('Unhandled exception:', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort:', 'ErrorDeviceLost'):
            check('%s death %s in log -> HARM_FAIL' % (tg, mk), word(tg, extra=[mk + ' x']) == 'HARM_FAIL')
        check('%s death in stdout -> HARM_FAIL' % tg, word(tg, stdout=['--- Fatal Error ---']) == 'HARM_FAIL')
        check('%s no stdout -> NOT_EVALUABLE' % tg, word(tg, drop=('stdout',)) == 'NOT_EVALUABLE')
        fr = ['FrameTrace: n=%d dt_us=33000 draws=3000' % (i + 3) for i in range(40)]
        check('%s frame 1000000 us after the scene -> HARM_FAIL' % tg, word(tg, frames=fr + ['FrameTrace: n=99 dt_us=1000000 draws=3000'])
              == 'HARM_FAIL')
        check('%s frame 999999 us -> PASS' % tg, word(tg, frames=fr + ['FrameTrace: n=99 dt_us=999999 draws=3000']) == 'MEMBERS_PASS')
        check('%s frame >= 1 s before the first scene frame not counted' % tg,
              word(tg, head=['FrameTrace: n=1 dt_us=2000000 draws=99', 'FrameTrace: n=2 dt_us=16000 draws=100']) == 'MEMBERS_PASS')
        check('%s frame >= 1 s on the first scene frame itself not counted' % tg,
              word(tg, head=['FrameTrace: n=1 dt_us=16000 draws=50', 'FrameTrace: n=2 dt_us=2000000 draws=100']) == 'MEMBERS_PASS')
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
        check('%s member fail precedes harm' % tg, word(tg, f8=[200.5], idx=10) == 'MEMBERS_FAIL')
        check('%s frame >= 1 s after a scene change not counted' % tg,
              word(tg, extra=['GuestOut: Level has started: hub', 'FrameTrace: n=999 dt_us=2000000 draws=3000']) == 'MEMBERS_PASS')
    check('n0 harm is a reference', word('f8_n0', idx=10, extra=['--- Fatal Error ---']) == 'MEMBERS_PASS')
    # f8_n0 members
    check('n0 T_fail = T_vib + 759 (A = 3) -> PASS', word('f8_n0', f8=[T_VIB + 759.0], init=lambda t: 255) == 'MEMBERS_PASS')
    check('n0 T_fail = T_vib + 775 -> PASS', word('f8_n0', f8=[T_VIB + 775.0], init=lambda t: 255) == 'MEMBERS_PASS')
    check('n0 T_fail = T_vib + 758.9 -> MEMBERS_FAIL', word('f8_n0', f8=[T_VIB + 758.9], init=lambda t: 255) == 'MEMBERS_FAIL')
    check('n0 T_fail = T_vib + 775.1 -> MEMBERS_FAIL', word('f8_n0', f8=[T_VIB + 775.1], init=lambda t: 255) == 'MEMBERS_FAIL')
    check('n0 A = 2: window [762; 778], T_fail + 760 -> MEMBERS_FAIL', word('f8_n0', A=2, f8=[T_VIB + 760.0], init=lambda t: 255)
          == 'MEMBERS_FAIL')
    check('n0 A = 2: T_fail + 770 -> PASS', word('f8_n0', A=2, f8=[T_VIB + 770.0], init=lambda t: 255) == 'MEMBERS_PASS')
    w, res, _ = rd('f8_n0', case('f8_n0', f8=[T_VIB + 760.0, T_VIB + 800.0], init=lambda t: 255))
    check('n0 first F8 line counts', w == 'MEMBERS_PASS' and abs(res['t_fail'] - (T_VIB + 760.0)) < 1e-6)
    for v, want in ((253, 'MEMBERS_FAIL'), (254, 'MEMBERS_PASS'), (257, 'MEMBERS_PASS'), (258, 'MEMBERS_FAIL')):
        check('n0 init_calls before the first F8 = %d -> %s' % (v, want), word('f8_n0', init=lambda t, v=v: v) == want)
    check('n0 init_calls read from the last row BEFORE the F8 line',
          word('f8_n0', f8=[T_VIB + 760.0], init=lambda t: 255 if t <= 769 else 400) == 'MEMBERS_PASS')
    check('n0 no F8, log covers, init live -> MECHANISM_REFUTED', word('f8_n0', f8=[]) == 'MECHANISM_REFUTED')
    check('n0 no F8, log ends before T_vib + 775 -> NOT_EVALUABLE', word('f8_n0', f8=[], end=780) == 'NOT_EVALUABLE')
    check('n0 no F8, init_calls frozen -> NOT_EVALUABLE', word('f8_n0', f8=[], init=lambda t: 5) == 'NOT_EVALUABLE')
    check('n0 no F8, init 1 per 4 s (rate 0.25, live edge) -> MECHANISM_REFUTED',
          word('f8_n0', f8=[], init=lambda t: 3 + t // 4) == 'MECHANISM_REFUTED')
    check('n0 no F8, init 1 per 5 s (below live) -> NOT_EVALUABLE', word('f8_n0', f8=[], init=lambda t: 3 + t // 5) == 'NOT_EVALUABLE')
    check('n0 no F8, init 1 per 4.5 s (rate 0.222 < 0.25) -> NOT_EVALUABLE',
          word('f8_n0', f8=[], init=lambda t: 3 + int(t / 4.5)) == 'NOT_EVALUABLE')
    # f8_n1 members
    check('n1 one F8 line -> MEMBERS_FAIL', word('f8_n1', f8=[400.5]) == 'MEMBERS_FAIL')
    check('n1 init_calls 2 on a middle row, F = 0 -> MEMBERS_FAIL', word('f8_n1', init=lambda t: 2 if t == 400 else 1) == 'MEMBERS_FAIL')
    check('n1 init_calls 2 on a middle row, F = 1 -> HOST_NOISE',
          word('f8_n1', init=lambda t: 2 if t == 400 else 1, before=['AudioOut: SDL audio init failed: x']) == 'HOST_NOISE')
    check('n1 acq last 250 -> PASS', word('f8_n1', acq=lambda t: 250 if t == 849 else 3) == 'MEMBERS_PASS')
    check('n1 acq last 249 -> MEMBERS_FAIL', word('f8_n1', acq=lambda t: 249 if t == 849 else 3) == 'MEMBERS_FAIL')
    check('n1 status 0 row -> MEMBERS_FAIL', word('f8_n1', mod=lambda t, p, r: dict(r, status=0) if t == 500 else r) == 'MEMBERS_FAIL')
    check('n1 status 2 -> PASS', word('f8_n1', status=2) == 'MEMBERS_PASS')
    check('n1 no AudioStat rows -> NOT_EVALUABLE', word('f8_n1', ports=()) == 'NOT_EVALUABLE')
    # identities (item 441 (g), item 453 (v) N2)
    w, res, out = rd('f8_s1', case('f8_s1', mod=lambda t, p, r: dict(r, q_fail=r['pushes'] + 1) if (t == 50 and p == 0) else r))
    v = row(res, 'ident', 'q_fail <= pushes')
    check('ident q_fail > pushes -> NO with line number, reading unchanged', v is False and w == 'MEMBERS_PASS'
          and any('q_fail <= pushes' in x and 'violations at lines [' in x and '[]' not in x for x in out))
    w, res, _ = rd('f8_n0', case('f8_n0', mod=lambda t, p, r: dict(r, acq=1) if t == 300 else r))
    check('ident acq != 0 at =0 -> NO, reading unchanged', row(res, 'ident', 'acq = 0') is False and w == 'MEMBERS_PASS')
    w, res, _ = rd('f8_n1', case('f8_n1'))
    check('ident acq = 0 not applicable at =1', row(res, 'ident', 'acq = 0') is None)
    w, res, _ = rd('f8_n1', case('f8_n1', mod=lambda t, p, r: dict(r, pushes=r['pushes'] - 1000) if (t == 300 and p == 2) else r))
    check('ident pushes decrease per port -> NO', row(res, 'ident', 'do not decrease') is False)
    w, res, _ = rd('f8_s0', case('f8_s0', mod=lambda t, p, r: dict(r, q_fail=5 if t == 100 else 0) if p == 0 else r))
    check('ident q_fail decrease per port -> NO', row(res, 'ident', 'do not decrease') is False)
    w, res, _ = rd('f8_s0', case('f8_s0', init=lambda t: 300 if t == 200 else (323 if t >= DONE else 10)))
    check('ident init_calls decrease -> NO', row(res, 'ident', 'do not decrease') is False)
    w, res, _ = rd('f8_n1', case('f8_n1', acq=lambda t: 100 if t == 200 else 3 + t // 3))
    check('ident acq decrease -> NO', row(res, 'ident', 'do not decrease') is False)
    w, res, _ = rd('f8_n1', case('f8_n1', mod=lambda t, p, r: dict(r, pushes=10 ** 6 - t) if p == 1 else (dict(r, pushes=t) if p == 0 else r)))
    check('ident is per port (other ports independent)', row(res, 'ident', 'do not decrease') is False)
    w, res, _ = rd('f8_n1', case('f8_n1'))
    check('ident all clean on the positive tag', all(v is not False for _, v in res['ident']))
    w, res, _ = rd('f8_n1', case('f8_n1', extra=['AudioStat: t_us=1 port=0 dev=2 sta']))
    check('malformed AudioStat line counted, not a row', res['stat_bad'] == 1 and w == 'MEMBERS_PASS')
    w, res, _ = rd('f8_n1', case('f8_n1', extra=['xxAudioStat: t_us=900000000 port=0 dev=2 status=1 queued=0 pushes=99999 q_fail=0 '
                                                 'init_calls=1 acq=999']))
    check('AudioStat row inside an interleaved line parsed', res['stat_rows'] == 3 * (850 - 11) + 1)
    check('other SDL_QueueAudio failed text is not an F8 line',
          rd('f8_n1', case('f8_n1', extra=['AudioOut: SDL_QueueAudio failed: Out of memory']))[1]['f8'] == 0)
    # missing log
    w, res, _ = rd('f8_s1', case('f8_s1', drop=('log',)))
    check('no log -> NOT_ADMITTED', w == 'NOT_ADMITTED' and res['log_sha256'] is None)
    # CLI: strict cp1250 without PYTHONIOENCODING, ASCII only, json, unknown tag
    d = case('f8_s0')
    env = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag', 'f8_s0'], capture_output=True, env=env)
    check('cli cp1250 strict rc 0', p.returncode == 0)
    check('cli ASCII only', all(b < 128 for b in p.stdout))
    check('cli READING line', b'  READING f8_s0 MEMBERS_PASS' in p.stdout)
    env2 = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
    p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag', 'f8_s0'], capture_output=True, env=env2)
    check('cli without PYTHONIOENCODING rc 0', p.returncode == 0)
    jp = os.path.join(T, 'o.json')
    p = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag', 'f8_s0', '--json', jp], capture_output=True)
    check('cli json written', p.returncode == 0 and json.load(open(jp))['word'] == 'MEMBERS_PASS')
    p = subprocess.run([sys.executable, TARGET, 'b4_v'], capture_output=True)
    check('cli unknown tag refused', p.returncode != 0 and b'unknown tag' in p.stderr)
    p = subprocess.run([sys.executable, TARGET, '--dir', d], capture_output=True)
    check('cli --dir without --tag refused', p.returncode != 0)
finally:
    shutil.rmtree(T, ignore_errors=True)

print('checks %d failed %d' % (N[0], len(FAIL)))
if FAIL:
    sys.exit(1)
print('ALL OK')
