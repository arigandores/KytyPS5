"""Track F link FS7c (HPP-567; ROADMAP s122 item 467 (g)(3), item 487 (g)(3), item 518 (v)): the reader of the tags fs7_h and fs7_n of the FS7
ship binary 8df61c00 at its defaults (KYTY_FIX_F8 = 1 and KYTY_FIX_B24 = 1 by default, no KYTY_FIX_* in the environment).  Rows and a
READING word by the seal; the verdict is the lead's (FS7d, HPP-568).
usage: python fs7c_read.py <tag> [--json <out.json>]
       python fs7c_read.py --dir <fixture dir> --tag <tag>   (fixtures: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt,
           installed_sha.txt, installed_before.txt, installed_after.txt, warm.txt, manifest_cmp.txt, seal.md, bin.exe)
Port of C:/kyty/f287/f19e/f19e_read.py (F19e HPP-549, form b24_h1 -> fs7_h) and C:/kyty/f287/f18e/f18e_read.py (F18e HPP-541, form f8_n1
-> fs7_n) with the members of item 487 (g)(3) and the reading N4 of item 518 (v)(4).
Definitions (seal docs/track-f/fs7c.md section 4):
  first GuestOut  the first log line that contains 'GuestOut:'.
  FixF8 member    (item 518 (v)(4), N4) exactly 1 line 'FixF8: mode=1' and 0 lines with 'FixF8:' of another form - YES; the line number
                  of that line and of the first GuestOut are printed, the order is not a gate; no line - NO (a member failure).
  FixB24 / FixB4  exactly 1 line 'FixB24: mode=1' / 'FixB4: mode=1', 0 lines 'FixB24:' / 'FixB4:' of another form, and the line before
  member          the first GuestOut (item 467 (g)(3), item 487 (g)(3)); no GuestOut line - not read.
  frame           a line 'FrameTrace: n=<n> dt_us=<dt>'.
  fs7_h           stand lines of KYTY_TEST_HIDLOSS (F19e section 4: config on, armed, attach, the test pad line, fire, done, stat with 16
                  fields); stand window: frames between the fire and the stat lines plus the frames before the fire line taken backwards
                  while the sum of dt_us after them up to the fire line is <= 1 000 000 (wide, F19e section 8.1); strict - printed beside.
  fs7_n           the F18e definitions: vibration line, A, T_vib, F8 line, AudioStat rows, N1 (F = SDL audio init failed lines).
  admission       json binary_sha256 = 8df61c00 and installed_sha.txt; version string ...-1883-gd6ee2dc8 in the binary file and the
                  revision text d6ee2dc in the log (item 518 (v)(3), N3); json prereg sha256 = sha256 of the seal file; env: no KYTY_FIX_*,
                  no KYTY_HAPTICS, no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS, no KYTY_TEST_AUDIOLOSS; fs7_h: KYTY_TEST_HIDLOSS = 60:hold
                  and the stand lines of F19e (with item 460 (d) N5), pad lines of another pad 0; fs7_n: KYTY_AV_TRACE = 1, no
                  KYTY_TEST_HIDLOSS, the vibration line, Haptics opened 0, Haptics disabled 0, A >= 1 and T_vib read, lines
                  'TestAudioLoss:' 0; no window 'minimized', no 'Recovering Vulkan swapchain', no 'GamePatch:'.  A failure = NOT_ADMITTED.
  form            installed FS6 9325446c before the tag and after the return; manifest cmp EQUAL after the return.  A failure = FORM_FAIL.
  members         fs7_h: item 487 (g)(3); fs7_n: item 467 (g)(3) + item 487 (g)(3) (FixB24, TestHidLoss lines 0) with N1 of item 453 (v).
  no harm         entered; lived through the hold (outcome ok, hold_exit null, hold_s >= H); 0 death markers (log, stdout); 0 frames >= 1 s
                  after the first scene frame (fs7_h: outside the wide stand window); video index records >= 3000; 0 one-frame glitches;
                  sheet made.
  identities      fs7_h: F19a section 6.1 at =1 (a violation - IDENT_FAIL); fs7_n: item 441 (g) at =1 (reference rows, item 453 (v) N2).
  exit            the harness exit (close_rc, close_s, close_killed of the run record, the Event: quit line) - a report row, not a gate.
ASCII output only."""
import hashlib, json, os, re, sys

G = 'C:/kyty/f287/fs7c'
SKY = 'underwater_aerial_garden'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_8df61c00.exe'
BIN_EXPECT = '8df61c009fbe6d7fd7f4e7576e89ab1b0989129336a26f6d1cdf8fd778fbffe7'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1883-gd6ee2dc8'
WANT = '9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2'
REV = 'd6ee2dc'
SEAL_PATH = 'C:/kyty/f287/fs7c/pred/fs7c_seal.md'
SPEC = {'fs7_h': dict(mode='hold', hold=330), 'fs7_n': dict(mode=None, hold=840)}
ORDER = ('fs7_h', 'fs7_n')
DELAY = '60'
HOLD_MS = '3000'
TEST_PAD = 'KYTY test pad'
STAT_KEYS = ('main_late_max_us', 'probes_posted', 'probes_run', 'pad_calls', 'pad_vib', 'pad_led', 'pad_trig', 'pad_wait_max_us',
             'po_applied', 'po_wait_max_us', 'guest_sdl', 'removed', 'vp_rumble', 'vp_led', 'vp_effect')
RX_TS = re.compile(rb'\[\d+\]\[(\d\d):(\d\d):(\d\d)\.(\d{3})\]')
RX_ASTAT = re.compile(rb'AudioStat: t_us=(\d+) port=(-?\d+) dev=(\d+) status=(-?\d+) queued=(\d+) pushes=(\d+) q_fail=(\d+) '
                      rb'init_calls=(\d+) acq=(\d+)')
RX_CONFIG_ON = re.compile(rb'TestHidLoss: config on delay_s=(\S+) mode=(\w+) hold_ms=(\d+)')
RX_ARMED = re.compile(rb'TestHidLoss: armed t_us=(\d+)')
RX_ATTACH = re.compile(rb'TestHidLoss: attach index=(-?\d+) t_us=(\d+)')
RX_FIRE = re.compile(rb'TestHidLoss: fire mode=(\w+) t_us=(\d+)')
RX_DONE = re.compile(rb'TestHidLoss: done t_us=(\d+)')
RX_HSTAT = re.compile(rb'TestHidLoss: stat mode=(\w+)((?: \w+=\d+)+)')
RX_KV = re.compile(rb' (\w+)=(\d+)')
RX_PAD = re.compile(rb'Controller (-?\d+): "([^"]*)" type=')
RX_REMOVED = re.compile(rb'Controller (-?\d+): removed\b')
RX_FIX = {'F8': re.compile(rb'FixF8: mode=(\d+)'), 'B24': re.compile(rb'FixB24: mode=(\d+)'), 'B4': re.compile(rb'FixB4: mode=(\d+)')}
M_FIX = {'F8': b'FixF8:', 'B24': b'FixB24:', 'B4': b'FixB4:'}
RX_HAP_OPEN = re.compile(rb'Haptics: pad audio device ".*" opened')
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
M_THL = b'TestHidLoss:'
M_CONFIG_BAD = b'TestHidLoss: config invalid'
M_ATTACH_BAD = b'TestHidLoss: attach failed'
M_DETACH_BAD = b'TestHidLoss: detach failed'
M_TAL = b'TestAudioLoss:'
M_VIB = b'AudioOut: vibration port'
M_OPENED = b'AudioOut: opened SDL device'
M_F8 = b'AudioOut: SDL_QueueAudio failed: Invalid audio device ID'
M_QFAIL = b'AudioOut: SDL_QueueAudio failed: '
M_INIT_OUT = b'AudioOut: SDL audio init failed'
M_INIT_IN = b'AudioIn: SDL init failed'
M_HAP_OFF = b'Haptics: disabled by KYTY_HAPTICS=0'
M_GUEST = b'GuestOut:'
M_START = b'GuestOut: Level has started: '
M_QUIT = b'Event: quit'
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
K2_US = 1000000
WIN_PRE_US = 1000000
BLOCK_US = 2700000
FREE_US = 50000
VIDEO_MIN = 3000
N1_ACQ_MIN = 250
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
    r = dict(lines=0, rev=[], fixl=dict((k, []) for k in M_FIX), first_guest=None,
             thl=0, config_on=[], config_bad=0, attach_bad=0, detach_bad=0, armed=[], attach=[], fire=[], done=[], hstat=[], hstat_bad=0,
             pads=[], removed=[], frames=[], first_scene_i=None, hold_us=0,
             astat=[], astat_bad=0, vib_line=None, t_vib=None, a=None, opened=0, hap_open=0, hap_off=0, tal=0, f8=0, f8_first=None,
             qfail_other=0, init_out=0, init_in=0, last_stamp=None,
             entry_line=None, scene_change_line=None, death=[], vke=0, skipped_draw=0, win={}, recovering=0, gamepatch=0, quit_line=None)
    if not log_path or not os.path.exists(log_path):
        r['sha256'] = None
        return r
    h = hashlib.sha256()
    stamp = None
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
                    scene = False
                    if after_entry and r['scene_change_line'] is None:
                        if not in_scene:
                            md = RX_DRAWS.search(mf.group(3))
                            if md and int(md.group(1)) >= 100:
                                in_scene = True
                                r['first_scene_i'] = len(r['frames'])
                        else:
                            scene = True
                            r['hold_us'] += dt
                    r['frames'].append((ln, n, dt, scene))
                continue
            if r['first_guest'] is None and M_GUEST in raw:
                r['first_guest'] = ln
            for k, mk in M_FIX.items():
                if mk in raw:
                    mx = RX_FIX[k].search(raw)
                    r['fixl'][k].append((ln, int(mx.group(1)) if mx else None))
            if M_THL in raw:
                r['thl'] += 1
                if M_CONFIG_BAD in raw:
                    r['config_bad'] += 1
                if M_ATTACH_BAD in raw:
                    r['attach_bad'] += 1
                if M_DETACH_BAD in raw:
                    r['detach_bad'] += 1
                m = RX_CONFIG_ON.search(raw)
                if m:
                    r['config_on'].append((ln, m.group(1).decode('ascii', 'replace'), m.group(2).decode('ascii', 'replace'),
                                           m.group(3).decode('ascii', 'replace')))
                m = RX_ARMED.search(raw)
                if m:
                    r['armed'].append((ln, int(m.group(1))))
                m = RX_ATTACH.search(raw)
                if m:
                    r['attach'].append((ln, int(m.group(2))))
                m = RX_FIRE.search(raw)
                if m:
                    r['fire'].append((ln, int(m.group(2)), m.group(1).decode('ascii', 'replace')))
                m = RX_DONE.search(raw)
                if m:
                    r['done'].append((ln, int(m.group(1))))
                if b'TestHidLoss: stat' in raw:
                    m = RX_HSTAT.search(raw)
                    kv = dict((k.decode(), int(v)) for k, v in RX_KV.findall(m.group(2))) if m else {}
                    if m and all(k in kv for k in STAT_KEYS):
                        kv['mode'] = m.group(1).decode('ascii', 'replace')
                        kv['ln'] = ln
                        r['hstat'].append(kv)
                    else:
                        r['hstat_bad'] += 1
            if b'Controller ' in raw:
                m = RX_PAD.search(raw)
                if m:
                    r['pads'].append((ln, int(m.group(1)), m.group(2).decode('ascii', 'replace')))
                m = RX_REMOVED.search(raw)
                if m:
                    r['removed'].append((ln, int(m.group(1))))
            if b'AudioStat:' in raw:
                ms = RX_ASTAT.search(raw)
                if ms:
                    v = [int(x) for x in ms.groups()]
                    r['astat'].append(dict(ln=ln, t=v[0], port=v[1], dev=v[2], status=v[3], queued=v[4], pushes=v[5], q_fail=v[6],
                                           init_calls=v[7], acq=v[8]))
                else:
                    r['astat_bad'] += 1
            if M_TAL in raw:
                r['tal'] += 1
            if M_QFAIL in raw:
                if M_F8 in raw:
                    r['f8'] += 1
                    if r['f8_first'] is None:
                        r['f8_first'] = ln
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


def windows(frames, fire_ln, stat_ln):
    """(wide set, strict set) of frame indexes.  strict: fire_ln < line < stat_ln; wide: strict plus the frames before the fire line
    taken backwards while the sum of dt_us of the frames after them up to the fire line is <= WIN_PRE_US."""
    if fire_ln is None or stat_ln is None:
        return None, None
    strict = set(i for i, fr in enumerate(frames) if fire_ln < fr[0] < stat_ln)
    wide = set(strict)
    acc = 0
    for i in range(len(frames) - 1, -1, -1):
        if frames[i][0] >= fire_ln:
            continue
        if acc > WIN_PRE_US:
            break
        wide.add(i)
        acc += frames[i][2]
    return wide, strict


def one(lst):
    return lst[0] if len(lst) == 1 else None


def fix_member(lines, first_guest, need_before):
    """(value, detail) of a Fix<X> member: exactly one line mode=1 and no other line of the prefix; need_before - the line lies before
    the first GuestOut (None when there is no GuestOut line)."""
    ones = [ln for ln, mode in lines if mode == 1]
    other = [ln for ln, mode in lines if mode != 1]
    ok = len(ones) == 1 and not other
    det = 'mode=1 lines %s, other lines %s, first GuestOut line %s' % (ones[:3], other[:3], first_guest)
    if ok and len(ones) == 1 and first_guest is not None:
        det += ', order: %s the first GuestOut' % ('before' if ones[0] < first_guest else 'after')
    if not ok:
        return False, det
    if not need_before:
        return True, det
    if first_guest is None:
        return None, det
    return ones[0] < first_guest, det


def read(tag, p):
    sp = SPEC[tag]
    stand = sp['mode'] is not None
    r = scan(p['log'], SKY)
    sd, ssha = stdout_scan(p['stdout'])
    rj = text(p['run'])
    run = json.loads(rj) if rj else None
    att = ((run or {}).get('attempts') or [{}])[0] if run else None
    env = (run or {}).get('env') or {}
    first = lambda t: (t or '').split('\n')[0].strip() or None
    res = dict(tag=tag, level=SKY, log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'], stdout_sha256=ssha, rev=r['rev'][:4])
    st = one(r['hstat'])
    armed, attach, fire, done = one(r['armed']), one(r['attach']), one(r['fire']), one(r['done'])
    test_pads = [x for x in r['pads'] if x[2] == TEST_PAD]
    other_pads = [x for x in r['pads'] if x[2] != TEST_PAD]
    astat = r['astat']
    astat_dev = [s for s in astat if s['dev'] != 0]
    # admission
    jbin = (run or {}).get('binary_sha256') if run else None
    inst = first(text(p['installed_sha']))
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256') if run else None
    fix_keys = sorted(k for k in env if k.startswith('KYTY_FIX_'))
    common_env = (not fix_keys and 'KYTY_HAPTICS' not in env and 'KYTY_GAME_PATCH' not in env and 'KYTY_GPU_CHECKPOINTS' not in env
                  and 'KYTY_TEST_AUDIOLOSS' not in env)
    if stand:
        env_ok = None if run is None else (common_env and env.get('KYTY_TEST_HIDLOSS') == '%s:%s' % (DELAY, sp['mode']))
        env_txt = 'KYTY_TEST_HIDLOSS=60:hold'
    else:
        env_ok = None if run is None else (common_env and env.get('KYTY_AV_TRACE') == '1' and 'KYTY_TEST_HIDLOSS' not in env)
        env_txt = 'KYTY_AV_TRACE=1, no KYTY_TEST_HIDLOSS'
    interf = bool(r['win'].get('minimized')) or r['recovering'] > 0 or r['gamepatch'] > 0
    adm = [('binary: json binary_sha256 = 8df61c00 (FS7) and installed_sha.txt = 8df61c00', None if run is None else
            (jbin == BIN_EXPECT and inst == BIN_EXPECT)),
           ('version string ...-1883-gd6ee2dc8 in the binary file (N3)', os.path.exists(p['bin'] or '') and
            VERSION in open(p['bin'], 'rb').read()),
           ('revision text d6ee2dc in the log (N3) %s' % r['rev'][:2], bool(r['rev']) and all(x == REV for x in r['rev'])),
           ('pre-registration: json prereg sha256 = sha256 of the seal file', None if run is None or seal_sha is None else pre == seal_sha),
           ('env: no KYTY_FIX_* (%s), %s, no KYTY_TEST_AUDIOLOSS, no KYTY_HAPTICS, no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS' % (
               fix_keys, env_txt), env_ok)]
    if stand:
        cfg = one(r['config_on'])
        adm += [('pad lines of another pad = 0 (%s)' % [x[2] for x in other_pads][:3], not other_pads),
                ('config on delay_s=60 mode=hold hold_ms=3000 exactly 1 line, config invalid 0 (%s)' % r['config_on'][:2],
                 cfg is not None and cfg[1] == DELAY and cfg[2] == sp['mode'] and cfg[3] == HOLD_MS and r['config_bad'] == 0),
                ('armed exactly 1 line (%d)' % len(r['armed']), armed is not None),
                ('attach exactly 1 line (%d; attach failed %d)' % (len(r['attach']), r['attach_bad']), attach is not None),
                ('emulator pad line "KYTY test pad" exactly 1 (%d)' % len(test_pads), len(test_pads) == 1),
                ('fire mode=hold exactly 1 line (%s)' % r['fire'][:2], fire is not None and fire[2] == sp['mode']),
                ('done exactly 1 line (%d)' % len(r['done']), done is not None),
                ('stat mode=hold exactly 1 line, all 15 fields (%d, malformed %d)' % (len(r['hstat']), r['hstat_bad']),
                 st is not None and st['mode'] == sp['mode'] and r['hstat_bad'] == 0),
                ('pad_calls >= 1 (%s; N1 of item 460 (d): tautology, the row stays)' % (None if st is None else st['pad_calls']),
                 None if st is None else st['pad_calls'] >= 1),
                ('probes_posted - probes_run = 0 (%s)' % (None if st is None else st['probes_posted'] - st['probes_run']),
                 None if st is None else st['probes_posted'] - st['probes_run'] == 0),
                ('N5 (item 460 (d)): the tag does not end inside the stand window (attach line %s < stat line %s, quit line %s after it)' % (
                    None if attach is None else attach[0], None if st is None else st['ln'], r['quit_line']),
                 attach is not None and st is not None and attach[0] < st['ln']
                 and (r['quit_line'] is None or r['quit_line'] > st['ln']))]
    else:
        adm += [('line AudioOut: vibration port present', r['vib_line'] is not None),
                ('lines Haptics: pad audio device ... opened = 0', r['hap_open'] == 0),
                ('lines Haptics: disabled by KYTY_HAPTICS=0 = 0 (N5 of item 453 (v))', r['hap_off'] == 0),
                ('A >= 1 and T_vib read (F18e section 8.3: A = 0 is F23, interference of the host)', r['a'] is not None and r['a'] >= 1
                 and r['t_vib'] is not None),
                ('lines TestAudioLoss: = 0 (%d)' % r['tal'], r['tal'] == 0)]
    adm.append(('no interference: window minimized / Recovering Vulkan swapchain / GamePatch line', not interf))
    sha_b, sha_a = first(text(p['installed_before'])), first(text(p['installed_after']))
    mc = text(p['manifest_cmp'])
    form = [('installed FS6 9325446c before the tag (inside the lock)', sha_b == WANT),
            ('installed FS6 9325446c after the return', sha_a == WANT),
            ('manifest of the caches, saves and GLCache before = after the return', bool(mc) and mc.startswith('manifest cmp EQUAL'))]
    # members
    fg = r['first_guest']
    f8v, f8d = fix_member(r['fixl']['F8'], fg, False)
    b24v, b24d = fix_member(r['fixl']['B24'], fg, True)
    b4v, b4d = fix_member(r['fixl']['B4'], fg, True)
    fix_rows = [('FixB24: mode=1 before the first GuestOut (%s)' % b24d, b24v),
                ('FixF8: mode=1 exactly 1 line and 0 FixF8 lines of another form, order not a gate (N4 of item 518 (v)(4); %s)' % f8d, f8v),
                ('FixB4: mode=1 before the first GuestOut (%s)' % b4d, b4v)]
    frames = r['frames']
    wide, strict = windows(frames, None if fire is None else fire[0], None if st is None else st['ln'])
    k2w = None if wide is None else sorted(i for i in wide if frames[i][2] >= K2_US)
    k2s = None if strict is None else sorted(i for i in strict if frames[i][2] >= K2_US)
    dtw = None if not wide else max(frames[i][2] for i in wide)
    g = (lambda k: None if st is None else st[k])
    F = r['init_out'] + r['init_in']
    mem = []
    host_noise_member = None
    if stand:
        mem.append(('main_late_max_us >= 2700000 (%s)' % g('main_late_max_us'), None if st is None else st['main_late_max_us'] >= BLOCK_US))
        mem.append(('po_wait_max_us >= 2700000 (%s; the block moved to PadOutput)' % g('po_wait_max_us'),
                    None if st is None else st['po_wait_max_us'] >= BLOCK_US))
        mem.append(('pad_wait_max_us < 50000 (%s; N1: informative with po_wait_max_us >= 2700000)' % g('pad_wait_max_us'),
                    None if st is None else st['pad_wait_max_us'] < FREE_US))
        mem.append(('guest_sdl = 0 (%s; N1: tautology at =1, the member stays)' % g('guest_sdl'),
                    None if st is None else st['guest_sdl'] == 0))
        mem.append(('frames >= 1 s in the stand window = 0 (wide %s of %s frames, strict %s of %s; max dt_us %s)' % (
            None if k2w is None else len(k2w), None if wide is None else len(wide), None if k2s is None else len(k2s),
            None if strict is None else len(strict), dtw), None if k2w is None else len(k2w) == 0))
        mem += fix_rows
    else:
        mem.append(('F8 lines in the whole log = 0 (%d)' % r['f8'], r['f8'] == 0))
        bad = [s['ln'] for s in astat if s['init_calls'] > 1]
        v = None if not astat else not bad
        mem.append(('init_calls <= 1 on every AudioStat row (rows > 1: %s); on failure F = %d' % (bad[:5], F), v))
        host_noise_member = (v is False and F >= 1)
        last = astat[-1] if astat else None
        mem.append(('acq >= 250 in the last AudioStat row (%s)' % (None if last is None else last['acq']),
                    None if last is None else last['acq'] >= N1_ACQ_MIN))
        mem.append(('status in {1, 2} on every AudioStat row with dev != 0 (rows %d, status 2: %d, status out lines %s)' % (
            len(astat_dev), sum(1 for s in astat_dev if s['status'] == 2), [s['ln'] for s in astat_dev if s['status'] not in STATUS_OK][:5]),
            None if not astat_dev else all(s['status'] in STATUS_OK for s in astat_dev)))
        mem.append((fix_rows[1][0], fix_rows[1][1]))
        mem.append((fix_rows[2][0], fix_rows[2][1]))
        mem.append((fix_rows[0][0], fix_rows[0][1]))
        mem.append(('lines TestHidLoss: = 0 (%d)' % r['thl'], r['thl'] == 0))
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
    sht = text(p['sheet'])
    sheet = next((x.strip() for x in sht.split('\n') if x.startswith('sheet: ')), None) if sht else None
    if att is None:
        hold_ok, att_info, exit_info = None, 'run record MISSING', 'run record MISSING'
    else:
        hold_ok = att.get('outcome') == 'ok' and att.get('hold_exit') is None and (att.get('hold_s') or 0) >= sp['hold']
        att_info = 'outcome %s hold_exit %s hold_s %s close_rc %s close_killed %s' % (
            att.get('outcome'), att.get('hold_exit'), att.get('hold_s'), att.get('close_rc'), att.get('close_killed'))
        exit_info = 'close_posted %s close_rc %s close_s %s close_killed %s close_wait_s %s' % (
            att.get('close_posted'), att.get('close_rc'), att.get('close_s'), att.get('close_killed'), att.get('close_wait_s'))
    out_win = wide or set()
    k2_scene = [i for i, fr in enumerate(frames) if fr[3] and fr[2] >= K2_US]
    k2_out = [i for i in k2_scene if i not in out_win]
    k2_out_strict = [i for i in k2_scene if i not in (strict or set())]
    dt_scene = max([fr[2] for fr in frames if fr[3]] or [0])
    if stand:
        k2_row = ('0 frames >= 1 s after the first scene frame outside the stand window (wide: %d, strict: %d; in scene %d)' % (
            len(k2_out), len(k2_out_strict), len(k2_scene)), None if r['first_scene_i'] is None or wide is None else not k2_out)
    else:
        k2_row = ('0 frames >= 1 s after the first scene frame (%d, max dt_us %d)' % (len(k2_scene), dt_scene),
                  None if r['first_scene_i'] is None else not k2_scene)
    harm = [('entered (entry line of %s)' % SKY, r['entry_line'] is not None),
            ('lived through the hold (outcome ok, hold_exit null, hold_s >= %d)' % sp['hold'], hold_ok),
            ('0 death markers (log and stdout) %s' % death[:3], None if sd is None else not death),
            k2_row,
            ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN),
            ('0 one-frame glitches (%s)' % gl, None if gl is None else gl == 0),
            ('sheet for the lead made', sheet is not None)]
    # identities
    ident = []
    if stand:
        ident.append(('pad_calls = pad_vib + pad_led + pad_trig', None if st is None else
                      st['pad_calls'] == st['pad_vib'] + st['pad_led'] + st['pad_trig']))
        ident.append(('probes_run <= probes_posted', None if st is None else st['probes_run'] <= st['probes_posted']))
        ident.append(('removed = 0 in hold', None if st is None else st['removed'] == 0))
        ts = [None if x is None else x[1] for x in (armed, attach, fire, done)]
        ident.append(('t_us armed < attach < fire <= done (%s)' % ts, None if None in ts else ts[0] < ts[1] < ts[2] <= ts[3]))
        ident.append(('invariant guest_sdl = 0 at =1', None if st is None else st['guest_sdl'] == 0))
    else:
        q, dec = [], []
        lastp = {}
        for s in astat:
            if s['q_fail'] > s['pushes']:
                q.append(s['ln'])
            prev = lastp.get(s['port'])
            if prev is not None and any(s[k] < prev[k] for k in ('pushes', 'q_fail', 'init_calls', 'acq')):
                dec.append(s['ln'])
            lastp[s['port']] = s
        ident.append(('q_fail <= pushes on every row (violations at lines %s; reference, N2)' % q[:5], not q))
        ident.append(('pushes, q_fail, init_calls, acq do not decrease per port (violations at lines %s; reference, N2)' % dec[:5], not dec))
    # reading
    vals = [v for _, v in mem]
    hv = [v for _, v in harm]
    iv = [v for _, v in ident] if stand else []
    if any(v is not True for _, v in adm):
        word = 'NOT_ADMITTED'
    elif any(v is not True for _, v in form):
        word = 'FORM_FAIL'
    elif any(v is False for v in vals):
        only_init = host_noise_member and sum(1 for v in vals if v is False) == 1
        word = 'HOST_NOISE' if only_init else 'MEMBERS_FAIL'
    elif any(v is False for v in iv):
        word = 'IDENT_FAIL'
    elif any(v is False for v in hv):
        word = 'HARM_FAIL'
    elif any(v is None for v in vals + hv + iv):
        word = 'NOT_EVALUABLE'
    else:
        word = 'MEMBERS_PASS'
    f8_ones = [ln for ln, mode in r['fixl']['F8'] if mode == 1]
    res.update(adm=adm, form=form, mem=mem, harm=harm, ident=ident, ident_ref=not stand, word=word, stat=st, armed=armed, attach=attach,
               fire=fire, done=done, config_on=r['config_on'][:2], thl=r['thl'], attach_bad=r['attach_bad'], detach_bad=r['detach_bad'],
               pads=r['pads'][:4], removed_lines=r['removed'][:4], fix_lines=dict((k, r['fixl'][k][:3]) for k in M_FIX),
               first_guest=fg, n4_row=(f8_ones[0] if len(f8_ones) == 1 else f8_ones[:3], fg),
               k2_wide=None if k2w is None else [frames[i][1] for i in k2w][:10],
               k2_strict=None if k2s is None else [frames[i][1] for i in k2s][:10],
               win_frames=[None if wide is None else len(wide), None if strict is None else len(strict)],
               F=F, a=r['a'], t_vib=r['t_vib'], vib_line=r['vib_line'], f8=r['f8'], f8_first=r['f8_first'], qfail_other=r['qfail_other'],
               astat_rows=len(astat), astat_bad=r['astat_bad'], status2=sum(1 for s in astat_dev if s['status'] == 2),
               last_astat=astat[-1] if astat else None, max_init=max([s['init_calls'] for s in astat] or [None]) if astat else None,
               hap_open=r['hap_open'], hap_off=r['hap_off'], tal=r['tal'],
               env=dict((k, env[k]) for k in sorted(env) if k.startswith(('KYTY_FIX_', 'KYTY_TEST_', 'KYTY_HAPTICS', 'KYTY_AV_TRACE',
                                                                           'KYTY_GAME_PATCH', 'KYTY_GPU_CHECKPOINTS'))),
               json_binary=jbin, installed_sha=inst, installed_before=sha_b, installed_after=sha_a, seal_sha256=seal_sha, prereg_sha256=pre,
               entry_line=r['entry_line'], first_scene_n=None if r['first_scene_i'] is None else frames[r['first_scene_i']][1],
               hold_s=round(r['hold_us'] / 1e6, 1), att=att_info, exit=exit_info, win=r['win'], recovering=r['recovering'],
               gamepatch=r['gamepatch'], vke=r['vke'], skipped_draw=r['skipped_draw'], quit_line=r['quit_line'], lines=r['lines'],
               warm=(text(p['warm']) or '').strip()[:200], manifest=(first(mc) or '')[:200])
    return res


def yn(v):
    if v is None:
        return 'NOT_READ'
    return 'YES' if v else 'NO'


def rows(res):
    out = ['FS7C %s level %s log sha256 %s lines %d stdout sha256 %s' % (res['tag'], res['level'], res['log_sha256'], res['log_lines'],
                                                                     res['stdout_sha256'])]
    add = out.append
    add('  binary: json %s installed %s (expected %s); installed before %s after %s (expected %s); revision texts %s (expected %s)'
        % (res['json_binary'], res['installed_sha'], BIN_EXPECT, res['installed_before'], res['installed_after'], WANT, res['rev'], REV))
    add('  seal sha256 %s; json prereg sha256 %s' % (res['seal_sha256'], res['prereg_sha256']))
    add('  env: %s' % res['env'])
    add('  Fix lines (line, mode) %s; first GuestOut line %s' % (res['fix_lines'], res['first_guest']))
    add('  N4 row (item 518 (v)(4)): FixF8: mode=1 line %s, first GuestOut line %s (order - not a gate)' % res['n4_row'])
    if res['tag'] == 'fs7_h':
        add('  TestHidLoss lines %d; config on %s; attach failed %d, detach failed %d (reference)' % (
            res['thl'], res['config_on'], res['attach_bad'], res['detach_bad']))
        add('  stand: armed %s attach %s fire %s done %s' % (res['armed'], res['attach'], res['fire'], res['done']))
        add('  stat: %s' % (None if res['stat'] is None else ' '.join('%s=%s' % (k, res['stat'][k]) for k in ('mode', 'ln') + STAT_KEYS)))
        add('  pad lines %s; removed lines %s' % (res['pads'], res['removed_lines']))
        add('  stand window frames (wide, strict) %s; frames >= 1 s there: wide n %s, strict n %s' % (
            res['win_frames'], res['k2_wide'], res['k2_strict']))
        add('  N3 (item 460 (d)): the field sent= of PadTriggerEffect lines is not delivery - not read')
    else:
        add('  vibration line %s, A %s, T_vib %s s; Haptics opened %d, disabled %d; TestAudioLoss lines %d; TestHidLoss lines %d' % (
            res['vib_line'], res['a'], res['t_vib'], res['hap_open'], res['hap_off'], res['tal'], res['thl']))
        add('  F8 lines %d, first at line %s; other SDL_QueueAudio failed lines %d; F (SDL audio init failed lines) %d' % (
            res['f8'], res['f8_first'], res['qfail_other'], res['F']))
        add('  AudioStat rows %d (malformed %d), max init_calls %s, status 2 rows (dev != 0) %d (reference); last row %s' % (
            res['astat_rows'], res['astat_bad'], res['max_init'], res['status2'], res['last_astat']))
        add('  pad lines %s (reference)' % (res['pads'],))
    add('  entry line %s; first scene frame n %s; hold (sum dt after it) %.1f s; attempt %s' % (
        res['entry_line'], res['first_scene_n'], res['hold_s'], asc(res['att'])))
    add('  EXIT (report row, not a gate): %s; Event: quit line %s of %s' % (asc(res['exit']), res['quit_line'], res['lines']))
    add('  window %s, Recovering %d, GamePatch %d, skipped draw %d, [Vulkan][E] %d (reference)' % (
        res['win'] or 'none', res['recovering'], res['gamepatch'], res['skipped_draw'], res['vke']))
    add('  %s; manifest: %s' % (res['warm'], res['manifest']))
    for name, val in res['adm']:
        add('  ADMIT %s: %s' % (name, yn(val)))
    for name, val in res['form']:
        add('  FORM %s: %s' % (name, yn(val)))
    for name, val in res['mem']:
        add('  MEMBER %s: %s' % (name, yn(val)))
    for name, val in res['harm']:
        add('  HARM %s: %s' % (name, yn(val)))
    for name, val in res['ident']:
        add('  %s %s: %s' % ('IDENT-REF' if res['ident_ref'] else 'IDENT', name, yn(val)))
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
