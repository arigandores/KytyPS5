"""Track F link F18e (HPP-541; ROADMAP s122 item 441 (g), (d)(4), item 448 (v), item 449 (g), item 453 (v)): the reader of the tags
f8_s0, f8_s1, f8_n0, f8_n1 of the F18c binary 35c4a754 (KYTY_FIX_F8, stand KYTY_TEST_AUDIOLOSS, counters AudioStat).  Rows and a READING
word by the seal; the verdict on F8 is the lead's (F18f, HPP-542).
usage: python f18e_read.py <tag> [--json <out.json>]
       python f18e_read.py --dir <fixture dir> --tag <tag>   (fixtures: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt,
           installed_sha.txt, installed_before.txt, installed_after.txt, warm.txt, manifest_cmp.txt, seal.md, bin.exe)
Port of C:/kyty/f287/f15e/f15e_read.py (F15e HPP-516) with the rows of item 441 (d)(4).
Definitions (seal docs/track-f/f18e.md section 4):
  stamp           the last '[<tid>][HH:MM:SS.mmm]' before a line, in seconds (F18a section 2.1; the AudioOut lines carry none).
  t_us            the field t_us= of the lines 'AudioStat:' and 'TestAudioLoss: armed|fire|done' (process time, KernelGetProcessTime).
  vibration       the first line 'AudioOut: vibration port'; A = number of lines 'AudioOut: opened SDL device' before it; T_vib = its stamp.
  F8 line         'AudioOut: SDL_QueueAudio failed: Invalid audio device ID'.  Its time in t_us is bracketed: low = the last t_us line before
                  the first F8 line, up = the first t_us line after it.
  AudioStat row   'AudioStat: t_us=T port=P dev=D status=S queued=Q pushes=N q_fail=F init_calls=I acq=C'; a line with 'AudioStat:'
                  that does not parse is counted (malformed, reference).
  rate of a port  over the AudioStat rows of the port with dev != 0 whose t_us lies in a window: (pushes_last - pushes_first) /
                  (t_last - t_first) per second; >= 2 rows needed, else not evaluable.  Windows (item 441 (d)(4)): W1 = [t_armed + 5 s;
                  t_fire), W2 = [t_done + 5 s; end of the log].  Member: every port with >= 2 rows in W1 (executor's reading of 'the port',
                  section 8 of the seal); the sum over those ports - printed beside (executor's variant).
  admission       (item 441 (d)(4) + item 453 (v) N5): json binary_sha256 = 35c4a754 (and installed_sha.txt), json prereg sha256 = sha256 of
                  the seal file; env KYTY_FIX_F8 of the tag, KYTY_TEST_AUDIOLOSS = 60:retry for f8_s*, absent for f8_n*, KYTY_AV_TRACE = 1,
                  KYTY_HAPTICS absent, no other KYTY_FIX_*, no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS; line 'AudioOut: vibration port'
                  present; 'Haptics: pad audio device ... opened' 0; 'Haptics: disabled by KYTY_HAPTICS=0' 0; A >= 1 and T_vib read
                  (executor: A = 0 - every output port without a device, F23, interference of the host); FixF8: mode=1 exactly 1 line at =1,
                  0 lines at =0; f8_s*: exactly 1 'TestAudioLoss: config on delay_s=60 mode=retry', 0 'config invalid'; f8_n*: 0 lines
                  'TestAudioLoss:'; no window 'minimized', no 'Recovering Vulkan swapchain', no 'GamePatch:'.  A failure = NOT_ADMITTED
                  (interference of the run, item 273 (z); a repeat by the lead's item, not 'mechanism refuted').
  form            installed adb0c82f before the tag and after the return; manifest cmp EQUAL after the return.  A failure = FORM_FAIL.
  members         item 441 (d)(4) with item 448 (v) (status in {1, 2}) and item 453 (v) N1 (init_calls <= 1 failed: F = lines
                  'AudioOut: SDL audio init failed' + 'AudioIn: SDL init failed'; F >= 1 - HOST_NOISE, F = 0 - the member fails by the letter).
  no harm         (f8_s1, f8_n1): entered; lived through the hold (outcome ok, hold_exit null, hold_s >= H); 0 death markers (log, stdout);
                  0 frames >= 1 s after the first scene frame; video index records >= 3000; 0 one-frame glitches; sheet made.
  identities      item 441 (g): q_fail <= pushes on every row; acq = 0 on every row at =0; pushes, q_fail, init_calls, acq do not decrease
                  per port.  A violation is printed with line numbers; by item 453 (v) N2 it proves no defect without a check that the port
                  was fed by >= 2 threads (reference rows, not members).
ASCII output only."""
import hashlib, json, os, re, sys

G = 'C:/kyty/f287/f18e'
SKY = 'underwater_aerial_garden'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_35c4a754.exe'
BIN_EXPECT = '35c4a75425bd54c5a59185c015ca47014b385ba926d10e7d849af8da3d181d29'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1878-g79b14ef2'
WANT = 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421'
REV = '79b14ef'
SEAL_PATH = 'C:/kyty/f287/f18e/pred/f18e_seal.md'
SPEC = {'f8_s0': dict(fix='0', stand=True, hold=330), 'f8_s1': dict(fix='1', stand=True, hold=330),
        'f8_n0': dict(fix='0', stand=False, hold=840), 'f8_n1': dict(fix='1', stand=False, hold=840)}
STAND_VALUE = '60:retry'
RX_TS = re.compile(rb'\[\d+\]\[(\d\d):(\d\d):(\d\d)\.(\d{3})\]')
RX_STAT = re.compile(rb'AudioStat: t_us=(\d+) port=(-?\d+) dev=(\d+) status=(-?\d+) queued=(\d+) pushes=(\d+) q_fail=(\d+) '
                     rb'init_calls=(\d+) acq=(\d+)')
RX_ARMED = re.compile(rb'TestAudioLoss: armed t_us=(\d+)')
RX_FIRE = re.compile(rb'TestAudioLoss: fire t_us=(\d+)')
RX_DONE = re.compile(rb'TestAudioLoss: done attempts=(\d+) t_us=(\d+)')
RX_FIX = re.compile(rb'FixF8: mode=(\d+)')
RX_HAP_OPEN = re.compile(rb'Haptics: pad audio device ".*" opened')
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
M_VIB = b'AudioOut: vibration port'
M_OPENED = b'AudioOut: opened SDL device'
M_F8 = b'AudioOut: SDL_QueueAudio failed: Invalid audio device ID'
M_QFAIL = b'AudioOut: SDL_QueueAudio failed: '
M_INIT_OUT = b'AudioOut: SDL audio init failed'
M_INIT_IN = b'AudioIn: SDL init failed'
M_HAP_OFF = b'Haptics: disabled by KYTY_HAPTICS=0'
M_TAL = b'TestAudioLoss:'
M_CONFIG_ON = b'TestAudioLoss: config on delay_s=60 mode=retry'
M_CONFIG_BAD = b'TestAudioLoss: config invalid'
M_START = b'GuestOut: Level has started: '
M_QUIT = b'Event: quit'
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
K2_US = 1000000
VIDEO_MIN = 3000
WIN_SKIP_US = 5000000
S0_F8_AFTER_FIRE_US = 10000000
S0_INIT_MIN = 256
S0_RATIO_MIN = 5.0
S1_ACQ_MIN = 300
S1_RATIO_LO, S1_RATIO_HI = 0.95, 1.05
N0_INIT_LO, N0_INIT_HI = 254, 257
N0_STEP_S, N0_WRAP, N0_WIDTH_S = 3, 256, 16
N1_ACQ_MIN = 250
LIVE_RATE_MIN = 0.25
DONE_ATTEMPTS = 300
STATUS_OK = (1, 2)


def paths(tag, base=None):
    names = ('installed_sha', 'installed_before', 'installed_after', 'warm', 'manifest_cmp', 'glitch', 'sheet')
    if base is not None:
        p = dict((n, os.path.join(base, n + '.txt')) for n in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'), bin=os.path.join(base, 'bin.exe'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((n, os.path.join(d, n + '.txt')) for n in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), seal=SEAL_PATH, bin=BIN_PATH)
    return p


def text(path):
    if not path or not os.path.exists(path):
        return None
    return open(path, 'rb').read().decode('utf-8', 'replace')


def asc(s):
    return s.encode('ascii', 'replace').decode('ascii') if isinstance(s, str) else s


def sha_file(path):
    if not path or not os.path.exists(path):
        return None
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def rev_text(raw):
    for m in (M_FORK, M_GIT):
        if m in raw:
            return raw.split(m, 1)[1].split(b',', 1)[0].strip()[:80].decode('ascii', 'replace')
    return None


def scan(log_path, level):
    r = dict(lines=0, rev=[], stat=[], stat_bad=0, vib_line=None, t_vib=None, a=None, opened=0, hap_open=0, hap_off=0, fix=[], tal=0,
             config_on=0, config_bad=0, armed=None, fire=None, done=None, f8=0, f8_first=None, t_fail=None, f8_low=None, f8_up=None,
             qfail_other=0, init_out=0, init_in=0, last_stamp=None, entry_line=None, scene_change_line=None, first_scene_n=None,
             hold_us=0, k2_after=0, dt_max_after=0, ft_rows=0, death=[], vke=0, skipped_draw=0, win={}, recovering=0, gamepatch=0,
             quit_line=None)
    if not log_path or not os.path.exists(log_path):
        r['sha256'] = None
        return r
    h = hashlib.sha256()
    stamp = None
    last_t = None
    want_up = False
    after_entry = in_scene = False
    with open(log_path, 'rb') as f:
        for raw in f:
            h.update(raw)
            r['lines'] += 1
            ln = r['lines']
            m = RX_TS.search(raw)
            if m:
                stamp = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1000.0
                r['last_stamp'] = stamp
            if b'FrameTrace: n=' in raw:
                mf = RX_FT.search(raw)
                if mf:
                    n, dt = int(mf.group(1)), int(mf.group(2))
                    r['ft_rows'] += 1
                    if after_entry and r['scene_change_line'] is None:
                        if not in_scene:
                            md = RX_DRAWS.search(mf.group(3))
                            if md and int(md.group(1)) >= 100:
                                in_scene = True
                                r['first_scene_n'] = n
                        else:
                            r['hold_us'] += dt
                            r['dt_max_after'] = max(r['dt_max_after'], dt)
                            if dt >= K2_US:
                                r['k2_after'] += 1
                continue
            t_line = None
            if b'AudioStat:' in raw:
                ms = RX_STAT.search(raw)
                if ms:
                    v = [int(x) for x in ms.groups()]
                    r['stat'].append(dict(ln=ln, t=v[0], port=v[1], dev=v[2], status=v[3], queued=v[4], pushes=v[5], q_fail=v[6],
                                          init_calls=v[7], acq=v[8]))
                    t_line = v[0]
                else:
                    r['stat_bad'] += 1
            if M_TAL in raw:
                r['tal'] += 1
                if M_CONFIG_ON in raw:
                    r['config_on'] += 1
                if M_CONFIG_BAD in raw:
                    r['config_bad'] += 1
                ma = RX_ARMED.search(raw)
                if ma and r['armed'] is None:
                    r['armed'] = (ln, int(ma.group(1)))
                    t_line = int(ma.group(1))
                mfi = RX_FIRE.search(raw)
                if mfi and r['fire'] is None:
                    r['fire'] = (ln, int(mfi.group(1)))
                    t_line = int(mfi.group(1))
                mdn = RX_DONE.search(raw)
                if mdn and r['done'] is None:
                    r['done'] = (ln, int(mdn.group(1)), int(mdn.group(2)))
                    t_line = int(mdn.group(2))
            if t_line is not None:
                if want_up:
                    r['f8_up'] = t_line
                    want_up = False
                last_t = t_line
            if M_QFAIL in raw:
                if M_F8 in raw:
                    r['f8'] += 1
                    if r['f8_first'] is None:
                        r['f8_first'] = ln
                        r['t_fail'] = stamp
                        r['f8_low'] = last_t
                        want_up = True
                else:
                    r['qfail_other'] += 1
            if M_INIT_OUT in raw:
                r['init_out'] += 1
            if M_INIT_IN in raw:
                r['init_in'] += 1
            if M_OPENED in raw:
                r['opened'] += 1
            if r['vib_line'] is None and M_VIB in raw:
                r['vib_line'] = ln
                r['t_vib'] = stamp
                r['a'] = r['opened']
            if b'Haptics: ' in raw:
                if RX_HAP_OPEN.search(raw):
                    r['hap_open'] += 1
                if M_HAP_OFF in raw:
                    r['hap_off'] += 1
            if b'FixF8:' in raw:
                mx = RX_FIX.search(raw)
                if mx:
                    r['fix'].append((ln, int(mx.group(1))))
            rv = rev_text(raw)
            if rv is not None and len(r['rev']) < 20:
                r['rev'].append(rv)
            if M_START in raw:
                name = raw.split(M_START, 1)[1].strip().decode('ascii', 'replace')
                if r['entry_line'] is None:
                    if name == level:
                        r['entry_line'] = ln
                        after_entry = True
                elif r['scene_change_line'] is None:
                    r['scene_change_line'] = ln
            if r['quit_line'] is None and M_QUIT in raw:
                r['quit_line'] = ln
            if b'[Vulkan][E]' in raw:
                r['vke'] += 1
            if b'AsyncPipelines: skipped draw' in raw:
                r['skipped_draw'] += 1
            if b'Recovering Vulkan swapchain' in raw:
                r['recovering'] += 1
            if b'GamePatch:' in raw:
                r['gamepatch'] += 1
            if b'Window ' in raw:
                mw = RX_WIN.search(raw)
                if mw:
                    k = mw.group(1).decode()
                    r['win'][k] = r['win'].get(k, 0) + 1
            for d in DEATH:
                if d in raw:
                    r['death'].append(('log', d.decode(), ln))
    r['sha256'] = h.hexdigest()
    return r


def stdout_scan(path):
    if not path or not os.path.exists(path):
        return None, None
    death = []
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for i, raw in enumerate(f, 1):
            h.update(raw)
            for d in DEATH:
                if d in raw:
                    death.append(('stdout', d.decode(), i))
    return death, h.hexdigest()


def port_rates(stat, lo, hi):
    """{port: (rows, rate per s or None)} over the rows with dev != 0 and lo <= t < hi (hi None = to the end)."""
    by = {}
    for s in stat:
        if s['dev'] == 0 or s['t'] < lo or (hi is not None and s['t'] >= hi):
            continue
        by.setdefault(s['port'], []).append(s)
    out = {}
    for p, rows in by.items():
        if len(rows) < 2 or rows[-1]['t'] <= rows[0]['t']:
            out[p] = (len(rows), None)
        else:
            out[p] = (len(rows), (rows[-1]['pushes'] - rows[0]['pushes']) * 1e6 / (rows[-1]['t'] - rows[0]['t']))
    return out


def ratio_member(r, lo_ok, hi_ok):
    """(member YES/NO/None, detail, sum ratio).  lo_ok/hi_ok - bounds on rate(W2)/rate(W1) per port (None = unbounded)."""
    if r['armed'] is None or r['fire'] is None or r['done'] is None:
        return None, 'armed/fire/done missing', None
    w1 = port_rates(r['stat'], r['armed'][1] + WIN_SKIP_US, r['fire'][1])
    w2 = port_rates(r['stat'], r['done'][2] + WIN_SKIP_US, None)
    ports = sorted(p for p, (n, rate) in w1.items() if rate is not None)
    if not ports:
        return None, 'no port with >= 2 rows in W1 %s' % sorted(w1.items()), None
    res, det, s1, s2 = [], [], 0.0, 0.0
    for p in ports:
        r1 = w1[p][1]
        n2, r2 = w2.get(p, (0, None))
        if r1 <= 0 or r2 is None:
            res.append(None)
            det.append('port %d W1 %d rows %.3f/s W2 %d rows %s' % (p, w1[p][0], r1, n2, r2))
            continue
        q = r2 / r1
        s1 += r1
        s2 += r2
        ok = (lo_ok is None or q >= lo_ok) and (hi_ok is None or q <= hi_ok)
        res.append(ok)
        det.append('port %d W1 %d rows %.3f/s W2 %d rows %.3f/s ratio %.4f' % (p, w1[p][0], r1, n2, r2, q))
    if any(x is False for x in res):
        mem = False
    elif any(x is None for x in res):
        mem = None
    else:
        mem = True
    return mem, '; '.join(det), (s2 / s1 if s1 > 0 else None)


def identities(stat, fix):
    q, acq0, dec = [], [], []
    last = {}
    for s in stat:
        if s['q_fail'] > s['pushes']:
            q.append(s['ln'])
        if fix == '0' and s['acq'] != 0:
            acq0.append(s['ln'])
        prev = last.get(s['port'])
        if prev is not None and any(s[k] < prev[k] for k in ('pushes', 'q_fail', 'init_calls', 'acq')):
            dec.append(s['ln'])
        last[s['port']] = s
    return q, acq0, dec


def read(tag, p):
    sp = SPEC[tag]
    r = scan(p['log'], SKY)
    sd, ssha = stdout_scan(p['stdout'])
    rj = text(p['run'])
    run = json.loads(rj) if rj else None
    att = ((run or {}).get('attempts') or [{}])[0] if run else None
    env = (run or {}).get('env') or {}
    first = lambda t: (t or '').split('\n')[0].strip() or None
    res = dict(tag=tag, level=SKY, log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'], stdout_sha256=ssha, rev=r['rev'][:4])
    # admission
    jbin = (run or {}).get('binary_sha256') if run else None
    inst = first(text(p['installed_sha']))
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256') if run else None
    fix_keys = sorted(k for k in env if k.startswith('KYTY_FIX_'))
    env_ok = None if run is None else (env.get('KYTY_FIX_F8') == sp['fix'] and fix_keys == ['KYTY_FIX_F8']
                                       and env.get('KYTY_TEST_AUDIOLOSS') == (STAND_VALUE if sp['stand'] else None)
                                       and env.get('KYTY_AV_TRACE') == '1' and 'KYTY_HAPTICS' not in env
                                       and 'KYTY_GAME_PATCH' not in env and 'KYTY_GPU_CHECKPOINTS' not in env)
    fix_ok = (len(r['fix']) == 1 and r['fix'][0][1] == 1) if sp['fix'] == '1' else len(r['fix']) == 0
    stand_ok = (r['config_on'] == 1 and r['config_bad'] == 0) if sp['stand'] else r['tal'] == 0
    interf = bool(r['win'].get('minimized')) or r['recovering'] > 0 or r['gamepatch'] > 0
    adm = [('binary: json binary_sha256 = 35c4a754 (F18c) and installed_sha.txt = 35c4a754', None if run is None else
            (jbin == BIN_EXPECT and inst == BIN_EXPECT)),
           ('version string ...-1878-g79b14ef2 in the binary file (reference)', None if not os.path.exists(p['bin'] or '') else
            VERSION in open(p['bin'], 'rb').read()),
           ('pre-registration: json prereg sha256 = sha256 of the seal file', None if run is None or seal_sha is None else pre == seal_sha),
           ('env: KYTY_FIX_F8=%s, KYTY_TEST_AUDIOLOSS %s, KYTY_AV_TRACE=1, no KYTY_HAPTICS (N5), no other KYTY_FIX_*, no KYTY_GAME_PATCH, '
            'no KYTY_GPU_CHECKPOINTS' % (sp['fix'], STAND_VALUE if sp['stand'] else 'absent'), env_ok),
           ('line AudioOut: vibration port present', r['vib_line'] is not None),
           ('lines Haptics: pad audio device ... opened = 0', r['hap_open'] == 0),
           ('lines Haptics: disabled by KYTY_HAPTICS=0 = 0 (N5)', r['hap_off'] == 0),
           ('A >= 1 and T_vib read (executor: A = 0 is F23, interference of the host)', r['a'] is not None and r['a'] >= 1
            and r['t_vib'] is not None),
           ('FixF8: mode=1 lines = %d' % (1 if sp['fix'] == '1' else 0), fix_ok),
           ('stand lines: %s' % ('config on delay_s=60 mode=retry = 1, config invalid = 0' if sp['stand'] else 'TestAudioLoss: = 0'),
            stand_ok),
           ('no interference: window minimized / Recovering Vulkan swapchain / GamePatch line', not interf)]
    adm_eval = [x for x in adm if not x[0].endswith('(reference)')]
    sha_b, sha_a = first(text(p['installed_before'])), first(text(p['installed_after']))
    mc = text(p['manifest_cmp'])
    form = [('installed adb0c82f before the tag (inside the lock)', sha_b == WANT),
            ('installed adb0c82f after the return', sha_a == WANT),
            ('manifest of the caches, saves and GLCache before = after the return', bool(mc) and mc.startswith('manifest cmp EQUAL'))]
    # members
    stat = r['stat']
    stat_dev = [s for s in stat if s['dev'] != 0]
    F = r['init_out'] + r['init_in']
    mem, note = [], []
    host_noise_member = None
    refuted = False
    if tag == 'f8_s0':
        mem.append(('fire and done attempts=300 present', r['fire'] is not None and r['done'] is not None
                    and r['done'][1] == DONE_ATTEMPTS))
        if r['fire'] is None:
            v = None
        elif r['f8_first'] is None:
            v = False
        elif r['f8_up'] is not None and r['f8_up'] <= r['fire'][1] + S0_F8_AFTER_FIRE_US:
            v = True
        elif r['f8_low'] is not None and r['f8_low'] > r['fire'][1] + S0_F8_AFTER_FIRE_US:
            v = False
        else:
            v = None
        mem.append(('first F8 line not later than fire + 10 s (t_us bracket low %s up %s, fire %s)' % (
            r['f8_low'], r['f8_up'], None if r['fire'] is None else r['fire'][1]), v))
        after = [s for s in stat if r['done'] is not None and s['ln'] > r['done'][0]]
        mem.append(('init_calls in the first AudioStat row after done >= 256 (%s)' % (after[0]['init_calls'] if after else None),
                    None if not after else after[0]['init_calls'] >= S0_INIT_MIN))
        rm, rdet, rsum = ratio_member(r, S0_RATIO_MIN, None)
        mem.append(('pushes per second W2 / W1 >= 5 for every port [%s]; sum over ports %s (executor variant)' % (
            rdet, None if rsum is None else '%.4f' % rsum), rm))
        refuted = r['f8'] == 0 and r['fire'] is not None and r['done'] is not None
    elif tag == 'f8_s1':
        mem.append(('fire and done attempts=300 present', r['fire'] is not None and r['done'] is not None
                    and r['done'][1] == DONE_ATTEMPTS))
        mem.append(('F8 lines in the whole log = 0 (%d)' % r['f8'], r['f8'] == 0))
        last = stat[-1] if stat else None
        v = None if last is None else last['init_calls'] <= 1
        mem.append(('init_calls <= 1 in the last AudioStat row (%s); on failure F = %d' % (None if last is None else last['init_calls'], F),
                    v))
        host_noise_member = (v is False and F >= 1)
        mem.append(('acq >= 300 in the last AudioStat row (%s)' % (None if last is None else last['acq']),
                    None if last is None else last['acq'] >= S1_ACQ_MIN))
        mem.append(('status in {1, 2} on every AudioStat row with dev != 0 (rows %d, status 2: %d, status 0 lines %s)' % (
            len(stat_dev), sum(1 for s in stat_dev if s['status'] == 2), [s['ln'] for s in stat_dev if s['status'] not in STATUS_OK][:5]),
            None if not stat_dev else all(s['status'] in STATUS_OK for s in stat_dev)))
        rm, rdet, rsum = ratio_member(r, S1_RATIO_LO, S1_RATIO_HI)
        mem.append(('pushes per second W2 / W1 in [0.95; 1.05] for every port [%s]; sum over ports %s (executor variant)' % (
            rdet, None if rsum is None else '%.4f' % rsum), rm))
    elif tag == 'f8_n0':
        lo = None if r['a'] is None else N0_STEP_S * (N0_WRAP - r['a'])
        if r['t_vib'] is None or lo is None or r['f8_first'] is None or r['t_fail'] is None:
            v = None
        else:
            d = r['t_fail'] - r['t_vib']
            v = lo <= d <= lo + N0_WIDTH_S
        mem.append(('first F8 line in T_vib + [3(256-A); 3(256-A)+16] s (T_vib %s, T_fail %s, A %s, window %s)' % (
            r['t_vib'], r['t_fail'], r['a'], None if lo is None else '[%d; %d]' % (lo, lo + N0_WIDTH_S)), v))
        before = [s for s in stat if r['f8_first'] is not None and s['ln'] < r['f8_first']]
        mem.append(('init_calls in the last AudioStat row before the first F8 line in [254; 257] (%s)' % (
            before[-1]['init_calls'] if before else None), None if not before else N0_INIT_LO <= before[-1]['init_calls'] <= N0_INIT_HI))
        live = None
        if len(stat) >= 2 and stat[-1]['t'] > stat[0]['t']:
            live = (stat[-1]['init_calls'] - stat[0]['init_calls']) * 1e6 / (stat[-1]['t'] - stat[0]['t'])
        cover = None if lo is None or r['t_vib'] is None or r['last_stamp'] is None else \
            r['last_stamp'] >= r['t_vib'] + lo + N0_WIDTH_S
        note.append('init_calls growth over the log %s per s (live: >= %.2f, executor variant); log covers T_vib + %s s: %s (last stamp %s)'
                    % (None if live is None else '%.4f' % live, LIVE_RATE_MIN, None if lo is None else lo + N0_WIDTH_S, cover,
                       r['last_stamp']))
        refuted = r['f8'] == 0 and cover is True and live is not None and live >= LIVE_RATE_MIN
    elif tag == 'f8_n1':
        mem.append(('F8 lines in the whole log = 0 (%d)' % r['f8'], r['f8'] == 0))
        bad = [s['ln'] for s in stat if s['init_calls'] > 1]
        v = None if not stat else not bad
        mem.append(('init_calls <= 1 on every AudioStat row (rows > 1: %s); on failure F = %d' % (bad[:5], F), v))
        host_noise_member = (v is False and F >= 1)
        last = stat[-1] if stat else None
        mem.append(('acq >= 250 in the last AudioStat row (%s)' % (None if last is None else last['acq']),
                    None if last is None else last['acq'] >= N1_ACQ_MIN))
        mem.append(('status in {1, 2} on every AudioStat row with dev != 0 (rows %d, status 2: %d, status 0 lines %s)' % (
            len(stat_dev), sum(1 for s in stat_dev if s['status'] == 2), [s['ln'] for s in stat_dev if s['status'] not in STATUS_OK][:5]),
            None if not stat_dev else all(s['status'] in STATUS_OK for s in stat_dev)))
    # no harm
    death = r['death'] + (sd or [])
    idx_n = None
    if p.get('idx') and os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as f:
            idx_n = sum(1 for _ in f)
    gl = None
    gt = text(p['glitch'])
    if gt:
        mg = RX_GL.search(gt)
        gl = int(mg.group(1)) if mg else None
    st = text(p['sheet'])
    sheet = next((x.strip() for x in st.split('\n') if x.startswith('sheet: ')), None) if st else None
    if att is None:
        hold_ok, att_info = None, 'run record MISSING'
    else:
        hold_ok = att.get('outcome') == 'ok' and att.get('hold_exit') is None and (att.get('hold_s') or 0) >= sp['hold']
        att_info = 'outcome %s hold_exit %s hold_s %s close_rc %s close_killed %s' % (
            att.get('outcome'), att.get('hold_exit'), att.get('hold_s'), att.get('close_rc'), att.get('close_killed'))
    harm = [('entered (entry line of %s)' % SKY, r['entry_line'] is not None),
            ('lived through the hold (outcome ok, hold_exit null, hold_s >= %d)' % sp['hold'], hold_ok),
            ('0 death markers (log and stdout) %s' % death[:3], None if sd is None else not death),
            ('0 frames >= 1 s after the first scene frame (%d, max dt_us %d)' % (r['k2_after'], r['dt_max_after']),
             None if r['first_scene_n'] is None else r['k2_after'] == 0),
            ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN),
            ('0 one-frame glitches (%s)' % gl, None if gl is None else gl == 0),
            ('sheet for the lead made', sheet is not None)]
    q, acq0, dec = identities(stat, sp['fix'])
    ident = [('q_fail <= pushes on every row (violations at lines %s)' % q[:5], not q),
             ('acq = 0 on every row at =0 (violations at lines %s)' % acq0[:5], None if sp['fix'] != '0' else not acq0),
             ('pushes, q_fail, init_calls, acq do not decrease per port (violations at lines %s)' % dec[:5], not dec)]
    if sp['fix'] == '1':
        ident[1] = ('acq = 0 on every row at =0 - not applicable at =1', None)
    # reading
    harm_on = tag in ('f8_s1', 'f8_n1')
    if any(v is not True for _, v in adm_eval):
        word = 'NOT_ADMITTED'
    elif any(v is not True for _, v in form):
        word = 'FORM_FAIL'
    elif refuted:
        word = 'MECHANISM_REFUTED'
    else:
        vals = [v for _, v in mem]
        hv = [v for _, v in harm] if harm_on else []
        if any(v is False for v in vals):
            only_init = host_noise_member and sum(1 for v in vals if v is False) == 1
            word = 'HOST_NOISE' if only_init else 'MEMBERS_FAIL'
        elif any(v is False for v in hv):
            word = 'HARM_FAIL'
        elif any(v is None for v in vals + hv):
            word = 'NOT_EVALUABLE'
        else:
            word = 'MEMBERS_PASS'
    res.update(adm=adm, form=form, mem=mem, harm=harm, harm_on=harm_on, ident=ident, note=note, word=word, F=F, a=r['a'],
               t_vib=r['t_vib'], vib_line=r['vib_line'], f8=r['f8'], f8_first=r['f8_first'], t_fail=r['t_fail'], f8_low=r['f8_low'],
               f8_up=r['f8_up'], qfail_other=r['qfail_other'], armed=r['armed'], fire=r['fire'], done=r['done'], stat_rows=len(stat),
               stat_bad=r['stat_bad'], status2=sum(1 for s in stat_dev if s['status'] == 2), last_stat=stat[-1] if stat else None,
               fix_lines=r['fix'][:3], hap_open=r['hap_open'], hap_off=r['hap_off'], env=dict((k, env[k]) for k in sorted(env)
               if k.startswith(('KYTY_FIX_', 'KYTY_TEST_', 'KYTY_HAPTICS', 'KYTY_AV_TRACE', 'KYTY_GAME_PATCH', 'KYTY_GPU_CHECKPOINTS'))),
               json_binary=jbin, installed_sha=inst, installed_before=sha_b, installed_after=sha_a, seal_sha256=seal_sha, prereg_sha256=pre,
               entry_line=r['entry_line'], first_scene_n=r['first_scene_n'], hold_s=round(r['hold_us'] / 1e6, 1), att=att_info,
               win=r['win'], recovering=r['recovering'], gamepatch=r['gamepatch'], vke=r['vke'], skipped_draw=r['skipped_draw'],
               quit_line=r['quit_line'], warm=(text(p['warm']) or '').strip()[:200], manifest=(first(mc) or '')[:200])
    return res


def yn(v):
    if v is None:
        return 'NOT_READ'
    return 'YES' if v else 'NO'


def rows(res):
    out = ['F18E %s level %s log sha256 %s lines %d stdout sha256 %s' % (res['tag'], res['level'], res['log_sha256'], res['log_lines'],
                                                                     res['stdout_sha256'])]
    add = out.append
    add('  binary: json %s installed %s (expected %s); installed before %s after %s (expected %s); revision texts %s (expected %s)'
        % (res['json_binary'], res['installed_sha'], BIN_EXPECT, res['installed_before'], res['installed_after'], WANT, res['rev'], REV))
    add('  seal sha256 %s; json prereg sha256 %s' % (res['seal_sha256'], res['prereg_sha256']))
    add('  env: %s' % res['env'])
    add('  vibration line %s, A %s, T_vib %s s; Haptics opened %d, disabled %d; FixF8 lines %s' % (
        res['vib_line'], res['a'], res['t_vib'], res['hap_open'], res['hap_off'], res['fix_lines']))
    add('  stand: armed %s fire %s done %s' % (res['armed'], res['fire'], res['done']))
    add('  F8 lines %d, first at line %s, its stamp %s s, t_us bracket [%s; %s]; other SDL_QueueAudio failed lines %d; '
        'F (SDL audio init failed lines) %d' % (res['f8'], res['f8_first'], res['t_fail'], res['f8_low'], res['f8_up'], res['qfail_other'],
                                                res['F']))
    add('  AudioStat rows %d (malformed %d), status 2 rows (dev != 0) %d (reference, item 448 (v)); last row %s' % (
        res['stat_rows'], res['stat_bad'], res['status2'], res['last_stat']))
    for n in res['note']:
        add('  note: %s' % n)
    add('  entry line %s; first scene frame n %s; hold (sum dt after it) %.1f s; attempt %s' % (
        res['entry_line'], res['first_scene_n'], res['hold_s'], asc(res['att'])))
    add('  window %s, Recovering %d, GamePatch %d, skipped draw %d, [Vulkan][E] %d, Event: quit line %s (reference)' % (
        res['win'] or 'none', res['recovering'], res['gamepatch'], res['skipped_draw'], res['vke'], res['quit_line']))
    add('  %s; manifest: %s' % (res['warm'], res['manifest']))
    for name, val in res['adm']:
        add('  ADMIT %s: %s' % (name, yn(val)))
    for name, val in res['form']:
        add('  FORM %s: %s' % (name, yn(val)))
    for name, val in res['mem']:
        add('  MEMBER %s: %s' % (name, yn(val)))
    for name, val in res['harm']:
        add('  %s %s: %s' % ('HARM' if res['harm_on'] else 'HARM-REF', name, yn(val)))
    for name, val in res['ident']:
        add('  IDENT %s: %s' % (name, yn(val)))
    add('  READING %s %s' % (res['tag'], res['word']))
    return out


def main(argv):
    if '--dir' in argv:
        if '--tag' not in argv:
            raise SystemExit('--dir needs --tag')
        tag = argv[argv.index('--tag') + 1]
        if tag not in SPEC:
            raise SystemExit('unknown tag: %s' % tag)
        p = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        if tag not in SPEC:
            raise SystemExit('unknown tag: %s' % tag)
        p = paths(tag)
    res = read(tag, p)
    print('\n'.join(asc(x) for x in rows(res)))
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w') as f:
            json.dump(res, f, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
