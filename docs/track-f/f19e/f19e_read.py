"""Track F link F19e (HPP-549; ROADMAP s122 item 451 (d)(4), item 460 (d)): the reader of the tags b24_h0, b24_s0, b24_h1, b24_d0,
b24_d1, b24_n1 of the F19c test binary 9b00ad40 (KYTY_FIX_B24, stand KYTY_TEST_HIDLOSS, line 'TestHidLoss: stat').  Rows and a READING
word by the seal; the verdict on B24 is the lead's (F19f, HPP-550).
usage: python f19e_read.py <tag> [--json <out.json>]
       python f19e_read.py --dir <fixture dir> --tag <tag>   (fixtures: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt,
           installed_sha.txt, installed_before.txt, installed_after.txt, warm.txt, manifest_cmp.txt, seal.md, bin.exe)
Port of C:/kyty/f287/f18e/f18e_read.py (F18e HPP-541) with the rows of item 451 (d)(4) and the identities of F19a section 6.1.
Definitions (seal docs/track-f/f19e.md section 4):
  frame           a line 'FrameTrace: n=<n> dt_us=<dt>' (item 451 (d)(4): the frame is dt_us of the FrameTrace line).
  stand lines     'TestHidLoss: config on delay_s=60 mode=<m> hold_ms=3000', 'armed t_us=', 'attach index= t_us=', 'fire mode= t_us=',
                  'done t_us=', 'stat mode=<m> main_late_max_us=... vp_effect=...' (16 fields of F19a section 6.1, all required).
  stand window    item 451 (d)(4): from fire - 1 s to the stat line.  FrameTrace lines carry no time: the frames whose line lies between the
                  fire line and the stat line, plus the frames before the fire line taken backwards while the sum of dt_us of the frames
                  after them (up to the fire line) is <= 1 000 000 (executor's reading 'wide', seal section 8.1); the frames between the fire
                  and the stat lines only - printed beside (reading 'strict').  Members read the wide window.
  pad line        'Controller <id>: "<name>" type=' (the emulator opened a pad); the test pad - name 'KYTY test pad'.
  removed line    'Controller <id>: removed' (always printed by F19c).
  admission       item 451 (d)(4): json binary_sha256 = 9b00ad40 (and installed_sha.txt), json prereg sha256 = sha256 of the seal file; env
                  KYTY_FIX_B24 of the tag, KYTY_TEST_HIDLOSS = 60:<mode> (absent for b24_n1), no other KYTY_FIX_*, no KYTY_GAME_PATCH, no
                  KYTY_GPU_CHECKPOINTS; FixB24: mode=1 exactly 1 line at =1, 0 at =0; stand tags: config on (exactly 1, delay 60, the mode,
                  hold_ms 3000), 0 config invalid, armed, attach, the test pad line, fire (the mode), done, stat (the mode) - each exactly 1;
                  pad_calls >= 1; probes_posted - probes_run = 0; pad lines of another pad 0; item 460 (d) N5: the tag does not end inside
                  the stand window (stat line after the attach line, the quit line - if any - after the stat line); b24_n1: 0 lines
                  'TestHidLoss:', 0 pad lines; no window 'minimized', no 'Recovering Vulkan swapchain', no 'GamePatch:'.  A failure =
                  NOT_ADMITTED (interference of the run, item 273 (z); a repeat by the lead's item).
  form            installed adb0c82f before the tag and after the return; manifest cmp EQUAL after the return.  A failure = FORM_FAIL.
  members         item 451 (d)(4) per tag (thresholds 2 700 000 us, 50 000 us, 1 000 000 us).
  no harm         (b24_h1, b24_n1): entered; lived through the hold; 0 death markers (log, stdout); 0 frames >= 1 s after the first scene
                  frame outside the stand window (wide); video index records >= 3000; 0 one-frame glitches; sheet made.
  identities      F19a section 6.1: pad_calls = pad_vib + pad_led + pad_trig; probes_run <= probes_posted; removed = 1 in detach, 0 in
                  hold and sleep; t_us armed < attach < fire <= done; invariants guest_sdl = 0 at =1, po_applied = 0 and po_wait_max_us = 0
                  at =0.  A violation - IDENT_FAIL (executor's variant, seal section 8.4).
  N1 / N3         (item 460 (d)) guest_sdl = 0 at =1 and pad_calls >= 1 are tautologies, the members stay; informative are
                  pad_wait_max_us < 50 000 at po_wait_max_us >= 2 700 000.  The field sent= of 'PadTriggerEffect:' lines is not read.
ASCII output only."""
import hashlib, json, os, re, sys

G = 'C:/kyty/f287/f19e'
SKY = 'underwater_aerial_garden'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_9b00ad40.exe'
BIN_EXPECT = '9b00ad40acc836a0302ce5123f77661eccf46042f25fd3739809e5c4e8511244'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1878-g52d2f546'
WANT = 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421'
REV = '52d2f54'
SEAL_PATH = 'C:/kyty/f287/f19e/pred/f19e_seal.md'
SPEC = {'b24_h0': dict(fix='0', mode='hold', hold=150), 'b24_s0': dict(fix='0', mode='sleep', hold=150),
        'b24_h1': dict(fix='1', mode='hold', hold=330), 'b24_d0': dict(fix='0', mode='detach', hold=150),
        'b24_d1': dict(fix='1', mode='detach', hold=150), 'b24_n1': dict(fix='1', mode=None, hold=330)}
ORDER = ('b24_h0', 'b24_s0', 'b24_h1', 'b24_d0', 'b24_d1', 'b24_n1')
DELAY = '60'
HOLD_MS = '3000'
TEST_PAD = 'KYTY test pad'
STAT_KEYS = ('main_late_max_us', 'probes_posted', 'probes_run', 'pad_calls', 'pad_vib', 'pad_led', 'pad_trig', 'pad_wait_max_us',
             'po_applied', 'po_wait_max_us', 'guest_sdl', 'removed', 'vp_rumble', 'vp_led', 'vp_effect')
RX_CONFIG_ON = re.compile(rb'TestHidLoss: config on delay_s=(\S+) mode=(\w+) hold_ms=(\d+)')
RX_ARMED = re.compile(rb'TestHidLoss: armed t_us=(\d+)')
RX_ATTACH = re.compile(rb'TestHidLoss: attach index=(-?\d+) t_us=(\d+)')
RX_FIRE = re.compile(rb'TestHidLoss: fire mode=(\w+) t_us=(\d+)')
RX_DONE = re.compile(rb'TestHidLoss: done t_us=(\d+)')
RX_STAT = re.compile(rb'TestHidLoss: stat mode=(\w+)((?: \w+=\d+)+)')
RX_KV = re.compile(rb' (\w+)=(\d+)')
RX_PAD = re.compile(rb'Controller (-?\d+): "([^"]*)" type=')
RX_REMOVED = re.compile(rb'Controller (-?\d+): removed\b')
RX_FIX = re.compile(rb'FixB24: mode=(\d+)')
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
M_THL = b'TestHidLoss:'
M_CONFIG_BAD = b'TestHidLoss: config invalid'
M_ATTACH_BAD = b'TestHidLoss: attach failed'
M_DETACH_BAD = b'TestHidLoss: detach failed'
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
    r = dict(lines=0, rev=[], fix=[], thl=0, config_on=[], config_bad=0, attach_bad=0, detach_bad=0, armed=[], attach=[], fire=[], done=[],
             stat=[], stat_bad=0, pads=[], removed=[], frames=[], entry_line=None, scene_change_line=None, first_scene_i=None,
             hold_us=0, death=[], vke=0, skipped_draw=0, win={}, recovering=0, gamepatch=0, quit_line=None)
    if not log_path or not os.path.exists(log_path):
        r['sha256'] = None
        return r
    h = hashlib.sha256()
    after_entry = in_scene = False
    with open(log_path, 'rb') as f:
        for raw in f:
            h.update(raw)
            r['lines'] += 1
            ln = r['lines']
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
                    m = RX_STAT.search(raw)
                    kv = dict((k.decode(), int(v)) for k, v in RX_KV.findall(m.group(2))) if m else {}
                    if m and all(k in kv for k in STAT_KEYS):
                        kv['mode'] = m.group(1).decode('ascii', 'replace')
                        kv['ln'] = ln
                        r['stat'].append(kv)
                    else:
                        r['stat_bad'] += 1
            if b'Controller ' in raw:
                m = RX_PAD.search(raw)
                if m:
                    r['pads'].append((ln, int(m.group(1)), m.group(2).decode('ascii', 'replace')))
                m = RX_REMOVED.search(raw)
                if m:
                    r['removed'].append((ln, int(m.group(1))))
            if b'FixB24:' in raw:
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
    st = one(r['stat'])
    armed, attach, fire, done = one(r['armed']), one(r['attach']), one(r['fire']), one(r['done'])
    test_pads = [x for x in r['pads'] if x[2] == TEST_PAD]
    other_pads = [x for x in r['pads'] if x[2] != TEST_PAD]
    # admission
    jbin = (run or {}).get('binary_sha256') if run else None
    inst = first(text(p['installed_sha']))
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256') if run else None
    fix_keys = sorted(k for k in env if k.startswith('KYTY_FIX_'))
    want_stand = ('%s:%s' % (DELAY, sp['mode'])) if stand else None
    env_ok = None if run is None else (env.get('KYTY_FIX_B24') == sp['fix'] and fix_keys == ['KYTY_FIX_B24']
                                       and env.get('KYTY_TEST_HIDLOSS') == want_stand
                                       and 'KYTY_GAME_PATCH' not in env and 'KYTY_GPU_CHECKPOINTS' not in env)
    fix_ok = (len(r['fix']) == 1 and r['fix'][0][1] == 1) if sp['fix'] == '1' else len(r['fix']) == 0
    interf = bool(r['win'].get('minimized')) or r['recovering'] > 0 or r['gamepatch'] > 0
    adm = [('binary: json binary_sha256 = 9b00ad40 (F19c) and installed_sha.txt = 9b00ad40', None if run is None else
            (jbin == BIN_EXPECT and inst == BIN_EXPECT)),
           ('version string ...-1878-g52d2f546 in the binary file (reference)', None if not os.path.exists(p['bin'] or '') else
            VERSION in open(p['bin'], 'rb').read()),
           ('pre-registration: json prereg sha256 = sha256 of the seal file', None if run is None or seal_sha is None else pre == seal_sha),
           ('env: KYTY_FIX_B24=%s, KYTY_TEST_HIDLOSS %s, no other KYTY_FIX_*, no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS' % (
               sp['fix'], want_stand or 'absent'), env_ok),
           ('FixB24: mode=1 lines = %d (%s)' % (1 if sp['fix'] == '1' else 0, r['fix'][:3]), fix_ok),
           ('pad lines of another pad = 0 (%s)' % [x[2] for x in other_pads][:3], not other_pads)]
    if stand:
        cfg = one(r['config_on'])
        adm += [('config on delay_s=60 mode=%s hold_ms=3000 exactly 1 line, config invalid 0 (%s)' % (sp['mode'], r['config_on'][:2]),
                 cfg is not None and cfg[1] == DELAY and cfg[2] == sp['mode'] and cfg[3] == HOLD_MS and r['config_bad'] == 0),
                ('armed exactly 1 line (%d)' % len(r['armed']), armed is not None),
                ('attach exactly 1 line (%d; attach failed %d)' % (len(r['attach']), r['attach_bad']), attach is not None),
                ('emulator pad line "KYTY test pad" exactly 1 (%d)' % len(test_pads), len(test_pads) == 1),
                ('fire mode=%s exactly 1 line (%s)' % (sp['mode'], r['fire'][:2]), fire is not None and fire[2] == sp['mode']),
                ('done exactly 1 line (%d)' % len(r['done']), done is not None),
                ('stat mode=%s exactly 1 line, all 15 fields (%d, malformed %d)' % (sp['mode'], len(r['stat']), r['stat_bad']),
                 st is not None and st['mode'] == sp['mode'] and r['stat_bad'] == 0),
                ('pad_calls >= 1 (%s; N1: tautology, the member stays)' % (None if st is None else st['pad_calls']),
                 None if st is None else st['pad_calls'] >= 1),
                ('probes_posted - probes_run = 0 (%s)' % (None if st is None else st['probes_posted'] - st['probes_run']),
                 None if st is None else st['probes_posted'] - st['probes_run'] == 0),
                ('N5 (item 460 (d)): the tag does not end inside the stand window (attach line %s < stat line %s, quit line %s after it)' % (
                    None if attach is None else attach[0], None if st is None else st['ln'], r['quit_line']),
                 attach is not None and st is not None and attach[0] < st['ln']
                 and (r['quit_line'] is None or r['quit_line'] > st['ln']))]
    else:
        adm += [('lines TestHidLoss: = 0 (%d)' % r['thl'], r['thl'] == 0),
                ('pad lines = 0 (%d)' % len(r['pads']), not r['pads'])]
    adm.append(('no interference: window minimized / Recovering Vulkan swapchain / GamePatch line', not interf))
    adm_eval = [x for x in adm if not x[0].endswith('(reference)')]
    sha_b, sha_a = first(text(p['installed_before'])), first(text(p['installed_after']))
    mc = text(p['manifest_cmp'])
    form = [('installed adb0c82f before the tag (inside the lock)', sha_b == WANT),
            ('installed adb0c82f after the return', sha_a == WANT),
            ('manifest of the caches, saves and GLCache before = after the return', bool(mc) and mc.startswith('manifest cmp EQUAL'))]
    # stand window
    frames = r['frames']
    wide, strict = windows(frames, None if fire is None else fire[0], None if st is None else st['ln'])
    k2w = None if wide is None else sorted(i for i in wide if frames[i][2] >= K2_US)
    k2s = None if strict is None else sorted(i for i in strict if frames[i][2] >= K2_US)
    dtw = None if not wide else max(frames[i][2] for i in wide)
    g = (lambda k: None if st is None else st[k])
    # members
    mem = []
    stop_member = None
    win_txt = 'frames >= 1 s in the stand window (wide %s of %s frames, strict %s of %s; max dt_us %s)' % (
        None if k2w is None else len(k2w), None if wide is None else len(wide), None if k2s is None else len(k2s),
        None if strict is None else len(strict), dtw)
    if tag == 'b24_h0':
        mem.append(('main_late_max_us >= 2700000 (%s)' % g('main_late_max_us'), None if st is None else st['main_late_max_us'] >= BLOCK_US))
        mem.append(('pad_wait_max_us >= 2700000 (%s)' % g('pad_wait_max_us'), None if st is None else st['pad_wait_max_us'] >= BLOCK_US))
        stop_member = len(mem)
        mem.append((win_txt + ' >= 1', None if k2w is None else len(k2w) >= 1))
    elif tag == 'b24_s0':
        mem.append(('main_late_max_us >= 2700000 (%s)' % g('main_late_max_us'), None if st is None else st['main_late_max_us'] >= BLOCK_US))
        mem.append(('pad_wait_max_us < 50000 (%s)' % g('pad_wait_max_us'), None if st is None else st['pad_wait_max_us'] < FREE_US))
        stop_member = len(mem)
        mem.append((win_txt + ' = 0', None if k2w is None else len(k2w) == 0))
    elif tag == 'b24_h1':
        mem.append(('main_late_max_us >= 2700000 (%s)' % g('main_late_max_us'), None if st is None else st['main_late_max_us'] >= BLOCK_US))
        mem.append(('po_wait_max_us >= 2700000 (%s; the block moved to PadOutput)' % g('po_wait_max_us'),
                    None if st is None else st['po_wait_max_us'] >= BLOCK_US))
        mem.append(('pad_wait_max_us < 50000 (%s; N1: informative with po_wait_max_us >= 2700000)' % g('pad_wait_max_us'),
                    None if st is None else st['pad_wait_max_us'] < FREE_US))
        mem.append(('guest_sdl = 0 (%s; N1: tautology at =1, the member stays)' % g('guest_sdl'),
                    None if st is None else st['guest_sdl'] == 0))
        mem.append((win_txt + ' = 0', None if k2w is None else len(k2w) == 0))
        mem.append(('line FixB24: mode=1 (%d)' % len(r['fix']), len(r['fix']) == 1 and r['fix'][0][1] == 1))
    elif tag in ('b24_d0', 'b24_d1'):
        mem.append(('removed = 1 (%s)' % g('removed'), None if st is None else st['removed'] == 1))
        mem.append(('lines Controller <id>: removed = 1 (%d)' % len(r['removed']), len(r['removed']) == 1))
        mem.append((win_txt + ' = 0', None if k2w is None else len(k2w) == 0))
    elif tag == 'b24_n1':
        mem.append(('line FixB24: mode=1 (%d)' % len(r['fix']), len(r['fix']) == 1 and r['fix'][0][1] == 1))
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
        hold_ok, att_info = None, 'run record MISSING'
    else:
        hold_ok = att.get('outcome') == 'ok' and att.get('hold_exit') is None and (att.get('hold_s') or 0) >= sp['hold']
        att_info = 'outcome %s hold_exit %s hold_s %s close_rc %s close_killed %s' % (
            att.get('outcome'), att.get('hold_exit'), att.get('hold_s'), att.get('close_rc'), att.get('close_killed'))
    out_win = wide or set()
    k2_scene = [i for i, fr in enumerate(frames) if fr[3] and fr[2] >= K2_US]
    k2_out = [i for i in k2_scene if i not in out_win]
    k2_out_strict = [i for i in k2_scene if i not in (strict or set())]
    harm = [('entered (entry line of %s)' % SKY, r['entry_line'] is not None),
            ('lived through the hold (outcome ok, hold_exit null, hold_s >= %d)' % sp['hold'], hold_ok),
            ('0 death markers (log and stdout) %s' % death[:3], None if sd is None else not death),
            ('0 frames >= 1 s after the first scene frame outside the stand window (wide: %d, strict: %d; in scene %d)' % (
                len(k2_out), len(k2_out_strict), len(k2_scene)),
             None if r['first_scene_i'] is None or (stand and wide is None) else not k2_out),
            ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN),
            ('0 one-frame glitches (%s)' % gl, None if gl is None else gl == 0),
            ('sheet for the lead made', sheet is not None)]
    # identities
    ident = []
    if stand:
        ident.append(('pad_calls = pad_vib + pad_led + pad_trig', None if st is None else
                      st['pad_calls'] == st['pad_vib'] + st['pad_led'] + st['pad_trig']))
        ident.append(('probes_run <= probes_posted', None if st is None else st['probes_run'] <= st['probes_posted']))
        ident.append(('removed = %d in %s' % (1 if sp['mode'] == 'detach' else 0, sp['mode']), None if st is None else
                      st['removed'] == (1 if sp['mode'] == 'detach' else 0)))
        ts = [None if x is None else x[1] for x in (armed, attach, fire, done)]
        ident.append(('t_us armed < attach < fire <= done (%s)' % ts, None if None in ts else ts[0] < ts[1] < ts[2] <= ts[3]))
        if sp['fix'] == '1':
            ident.append(('invariant guest_sdl = 0 at =1', None if st is None else st['guest_sdl'] == 0))
        else:
            ident.append(('invariant po_applied = 0 and po_wait_max_us = 0 at =0', None if st is None else
                          st['po_applied'] == 0 and st['po_wait_max_us'] == 0))
    # reading
    harm_on = tag in ('b24_h1', 'b24_n1')
    vals = [v for _, v in mem]
    hv = [v for _, v in harm] if harm_on else []
    if any(v is not True for _, v in adm_eval):
        word = 'NOT_ADMITTED'
    elif any(v is not True for _, v in form):
        word = 'FORM_FAIL'
    elif stop_member is not None and mem[stop_member][1] is False:
        word = 'STOP_ITERATION'
    elif any(v is False for v in vals):
        word = 'MEMBERS_FAIL'
    elif any(v is False for _, v in ident):
        word = 'IDENT_FAIL'
    elif any(v is False for v in hv):
        word = 'HARM_FAIL'
    elif any(v is None for v in vals + hv) or any(v is None for _, v in ident):
        word = 'NOT_EVALUABLE'
    else:
        word = 'MEMBERS_PASS'
    res.update(adm=adm, form=form, mem=mem, harm=harm, harm_on=harm_on, ident=ident, word=word, stat=st, armed=armed, attach=attach,
               fire=fire, done=done, config_on=r['config_on'][:2], thl=r['thl'], attach_bad=r['attach_bad'], detach_bad=r['detach_bad'],
               pads=r['pads'][:4], removed_lines=r['removed'][:4], fix_lines=r['fix'][:3],
               k2_wide=None if k2w is None else [frames[i][1] for i in k2w][:10],
               k2_strict=None if k2s is None else [frames[i][1] for i in k2s][:10],
               win_frames=[None if wide is None else len(wide), None if strict is None else len(strict)],
               env=dict((k, env[k]) for k in sorted(env) if k.startswith(('KYTY_FIX_', 'KYTY_TEST_', 'KYTY_GAME_PATCH', 'KYTY_GPU_CHECKPOINTS'))),
               json_binary=jbin, installed_sha=inst, installed_before=sha_b, installed_after=sha_a, seal_sha256=seal_sha, prereg_sha256=pre,
               entry_line=r['entry_line'], first_scene_n=None if r['first_scene_i'] is None else frames[r['first_scene_i']][1],
               hold_s=round(r['hold_us'] / 1e6, 1), att=att_info, win=r['win'], recovering=r['recovering'], gamepatch=r['gamepatch'],
               vke=r['vke'], skipped_draw=r['skipped_draw'], quit_line=r['quit_line'], warm=(text(p['warm']) or '').strip()[:200],
               manifest=(first(mc) or '')[:200])
    return res


def yn(v):
    if v is None:
        return 'NOT_READ'
    return 'YES' if v else 'NO'


def rows(res):
    out = ['F19E %s level %s log sha256 %s lines %d stdout sha256 %s' % (res['tag'], res['level'], res['log_sha256'], res['log_lines'],
                                                                     res['stdout_sha256'])]
    add = out.append
    add('  binary: json %s installed %s (expected %s); installed before %s after %s (expected %s); revision texts %s (expected %s)'
        % (res['json_binary'], res['installed_sha'], BIN_EXPECT, res['installed_before'], res['installed_after'], WANT, res['rev'], REV))
    add('  seal sha256 %s; json prereg sha256 %s' % (res['seal_sha256'], res['prereg_sha256']))
    add('  env: %s' % res['env'])
    add('  FixB24 lines %s; TestHidLoss lines %d; config on %s; attach failed %d, detach failed %d (reference)' % (
        res['fix_lines'], res['thl'], res['config_on'], res['attach_bad'], res['detach_bad']))
    add('  stand: armed %s attach %s fire %s done %s' % (res['armed'], res['attach'], res['fire'], res['done']))
    add('  stat: %s' % (None if res['stat'] is None else ' '.join('%s=%s' % (k, res['stat'][k]) for k in ('mode', 'ln') + STAT_KEYS)))
    add('  pad lines %s; removed lines %s' % (res['pads'], res['removed_lines']))
    add('  stand window frames (wide, strict) %s; frames >= 1 s there: wide n %s, strict n %s' % (
        res['win_frames'], res['k2_wide'], res['k2_strict']))
    add('  N3 (item 460 (d)): the field sent= of PadTriggerEffect lines is not delivery - not read')
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
