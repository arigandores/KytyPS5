"""Track F link FS8c (HPP-573; ROADMAP s122 item 471 (g)(3), item 530 (g)(d)): the reader of the tags fs8_v, fs8_w, fs8_ef of the FS8 ship
binary 2c9b69b9 at its defaults (KYTY_FIX_F19 = 1 by default, no KYTY_FIX_* in the environment).  Rows and a READING word by the seal; the
verdict is the lead's (FS8d, HPP-574).
usage: python fs8c_read.py <tag> [--json <out.json>]                    tags fs8_v, fs8_w, fs8_ef
       python fs8c_read.py --dir <fixture dir> --tag <tag>   (fixtures: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt,
           installed_sha.txt, installed_before.txt, installed_after.txt, cold.txt, manifest_cmp.txt, seal.md, bin.exe)
Port of C:/kyty/f287/f14g/f14g_read.py (F14g HPP-507: forms f19_v1, f19_w1, f19_ef; the rd branch dropped - no capture in FS8c, item
471 (g)(3)) with the admission / form / READING scheme of C:/kyty/f287/fs7c/fs7c_read.py (FS7c HPP-567) and the members FixB4 / FixF8 of
item 471 (g)(3).
Definitions (seal docs/track-f/fs8c.md section 4):
  first GuestOut  the first log line that contains 'GuestOut:'.
  Fix members     'FixB4: mode=1' / 'FixF8: mode=1' searched anywhere in a line; another form = a line with 'FixB4:' / 'FixF8:' without
                  'mode=1' (or 'FixB42' lines never count as 'FixB4:'); member = exactly 1 line mode=1, 0 lines of another form, and its line
                  number < the line number of the first GuestOut (item 471 (g)(3) letter); no GuestOut line - not determined.  The reading
                  of item 518 (v)(4) for FixF8 (order not a gate) is printed beside as a REPORT row (executor variant, seal section 8).
  frame           a line 'FrameTrace: n=<n> dt_us=<dt>'; entry - the first line 'GuestOut: Level has started: <level>'; first scene frame -
                  the first FrameTrace row after it with draws >= 100; hold - sum dt_us of the FrameTrace rows after the first scene frame
                  (before a scene change); frames >= 1 s - FrameTrace rows with dt_us >= 1 000 000 after the first scene frame (before a
                  scene change): REPORT row (cold entry, item 471 (g)(3)).
  directory       every line 'Shader translation cache: <dir>'; member = >= 1 such line and every one ends with
                  variant_fixb26_fixb1b_fixf10_fixf19 (item 471 (g)(3): the =1 path of FixF19Enabled() [c code]).
  admission       json binary_sha256 = 2c9b69b9 and installed_sha.txt = 2c9b69b9; the version string ...-1889-g302347b4 in the binary file;
                  every revision text of the log / stdout ('Fork build arigandores/KytyPS5 ' or ', git = ') = 302347b or the version string (item 530 (g) N1:
                  the SDL_REVISION text ...-g0f78a522 is never read); json prereg sha256 = sha256 of the seal file; env: no KYTY_FIX_*
                  (empty included), no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS; fs8_v / fs8_ef: KYTY_REC set, no VK_LAYER_*, command line
                  '--vulkan-validation false' (the last occurrence of the flag); fs8_w: VK_LAYER_PATH set, VK_LAYER_DUPLICATE_MESSAGE_LIMIT = 100000000, no
                  VK_LAYER_MESSAGE_ID_FILTER, no KYTY_PIPELINE_PRECACHE, no KYTY_REC, command line '--vulkan-validation true'; cold.txt says
                  'absent' (the directory ..._fixf19 did not exist before the start); KYTY_GUEST_ARGS = '-lvl <level>'; no window
                  'minimized', no 'Recovering Vulkan swapchain', no 'GamePatch:' line.  A failure = NOT_ADMITTED (interference of the
                  run; a repeat only by a lead item, item 273 (z)).
  form            installed FS6 9325446c before the tag and after the return; manifest cmp EQUAL after the return.  A failure = FORM_FAIL.
  members         every tag: entered; directory; FixB4; FixF8 (letter); hold >= 300 s; the process lived to the end of the hold (outcome ok,
                  hold_exit null, attempt hold_s >= H); fs8_v / fs8_ef: 0 death markers (log, stdout); video index records >= 3000;
                  0 one-frame glitches (s51_vidglitch.py <rec> 4 6); sheet made; fs8_w: 0 '[Vulkan][E]' (VUID-06479 counted beside);
                  '[Vulkan][W]' > 0; 'DualSrcBlend: supported=1 enabled=1' before the first GuestOut.
  READING         NOT_ADMITTED -> FORM_FAIL -> MEMBERS_FAIL (a member NO) -> NOT_EVALUABLE (a member not determined) -> MEMBERS_PASS.
                  REPORT rows (frames >= 1 s, death markers of fs8_w, skipped draw, window lines, limit lines of the layer, FixB24, the
                  FixF8 variant, exit) never change the word.
ASCII output only."""
import hashlib, json, os, re, sys

G = 'C:/kyty/f287/fs8c'
SKY = 'underwater_aerial_garden'
EF = 'enemy_final'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe'
BIN_EXPECT = '2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1889-g302347b4'
WANT = '9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2'
REV = '302347b'
SEAL_PATH = 'C:/kyty/f287/fs8c/pred/fs8c_seal.md'
DIR_FIX = 'variant_fixb26_fixb1b_fixf10_fixf19'
SPEC = {'fs8_v': dict(kind='v', level=SKY, hold=330), 'fs8_w': dict(kind='w', level=SKY, hold=310),
        'fs8_ef': dict(kind='ef', level=EF, hold=330)}
VIDEO_KINDS = ('v', 'ef')
LIMIT = '100000000'
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d+) enabled=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
RX_FIXK = {'B4': re.compile(rb'FixB4: mode=(\d+)'), 'F8': re.compile(rb'FixF8: mode=(\d+)'), 'B24': re.compile(rb'FixB24: mode=(\d+)')}
M_FIXK = {'B4': b'FixB4:', 'F8': b'FixF8:', 'B24': b'FixB24:'}
M_GUEST = b'GuestOut:'
M_START = b'GuestOut: Level has started: '
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
M_QUIT = b'Event: quit'
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
K2_US = 1000000
VIDEO_MIN = 3000
HOLD_MIN_US = 300000000


def paths(tag, base=None):
    names = ('installed_sha', 'installed_before', 'installed_after', 'cold', 'manifest_cmp', 'glitch', 'sheet')
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
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def has_bytes(path, needle):
    if not path or not os.path.exists(path):
        return None
    return needle in open(path, 'rb').read()


def rev_text(raw):
    for m in (M_FORK, M_GIT):
        if m in raw:
            return raw.split(m, 1)[1].split(b',', 1)[0].strip()[:80].decode('ascii', 'replace')
    return None


def scan(log_path, level):
    r = dict(lines=0, rev=[], stc=[], first_guest=None, entry_line=None, scene_change_line=None, first_scene_n=None, hold_us=0,
             k2_after=0, dt_max_after=0, ft_rows=0, death=[], vke=0, vke_06479=0, vkw=0, vk_limit=0, dual=[], skipped_draw=0, win={},
             recovering=0, gamepatch=0, quit_line=None, fixl=dict((k, []) for k in M_FIXK))
    h = hashlib.sha256()
    after_entry = in_scene = False
    if not log_path or not os.path.exists(log_path):
        r['sha256'] = None
        return r
    with open(log_path, 'rb') as f:
        for raw in f:
            h.update(raw)
            r['lines'] += 1
            ln = r['lines']
            if b'FrameTrace: n=' in raw:
                m = RX_FT.search(raw)
                if m:
                    n, dt = int(m.group(1)), int(m.group(2))
                    r['ft_rows'] += 1
                    if after_entry and r['scene_change_line'] is None:
                        if not in_scene:
                            md = RX_DRAWS.search(m.group(3))
                            if md and int(md.group(1)) >= 100:
                                in_scene = True
                                r['first_scene_n'] = n
                        else:
                            r['hold_us'] += dt
                            r['dt_max_after'] = max(r['dt_max_after'], dt)
                            if dt >= K2_US:
                                r['k2_after'] += 1
                    continue
            rv = rev_text(raw)
            if rv is not None and len(r['rev']) < 20:
                r['rev'].append(('log', ln, rv))
            if b'Shader translation cache: ' in raw:
                r['stc'].append(raw.split(b'Shader translation cache: ', 1)[1].strip()[:200].decode('ascii', 'replace'))
            for k, mk in M_FIXK.items():
                if mk in raw:
                    m = RX_FIXK[k].search(raw)
                    r['fixl'][k].append((ln, m.group(1).decode() if m else None))
            if M_START in raw:
                name = raw.split(M_START, 1)[1].strip().decode('ascii', 'replace')
                if r['entry_line'] is None:
                    if name == level:
                        r['entry_line'] = ln
                        after_entry = True
                elif r['scene_change_line'] is None:
                    r['scene_change_line'] = ln
            if r['first_guest'] is None and M_GUEST in raw:
                r['first_guest'] = ln
            if b'DualSrcBlend:' in raw:
                m = RX_DUAL.search(raw)
                if m:
                    r['dual'].append((ln, int(m.group(1)), int(m.group(2))))
            if b'[Vulkan][' in raw:
                if b'[Vulkan][E]' in raw:
                    r['vke'] += 1
                    if b'06479' in raw:
                        r['vke_06479'] += 1
                if b'[Vulkan][W]' in raw:
                    r['vkw'] += 1
            if b'this will be the last time reporting it' in raw:
                r['vk_limit'] += 1
            if b'AsyncPipelines: skipped draw' in raw:
                r['skipped_draw'] += 1
            if b'Recovering Vulkan swapchain' in raw:
                r['recovering'] += 1
            if b'GamePatch:' in raw:
                r['gamepatch'] += 1
            if M_QUIT in raw and r['quit_line'] is None:
                r['quit_line'] = ln
            if b'Window ' in raw:
                m = RX_WIN.search(raw)
                if m:
                    k = m.group(1).decode()
                    r['win'][k] = r['win'].get(k, 0) + 1
            for d in DEATH:
                if d in raw:
                    r['death'].append(('log', d.decode(), ln))
    r['sha256'] = h.hexdigest()
    return r


def stdout_scan(path):
    if not path or not os.path.exists(path):
        return None, [], None
    death, rev = [], []
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for i, raw in enumerate(f, 1):
            h.update(raw)
            rv = rev_text(raw)
            if rv is not None and len(rev) < 20:
                rev.append(('stdout', i, rv))
            for d in DEATH:
                if d in raw:
                    death.append(('stdout', d.decode(), i))
    return death, rev, h.hexdigest()


def first_line(t):
    return (t or '').split('\n')[0].strip()


def fix_member(lines, first_guest, order=True):
    """(value, detail): exactly 1 line mode=1, 0 lines of another form, and (order) before the first GuestOut."""
    ones = [ln for ln, v in lines if v == '1']
    other = [ln for ln, v in lines if v != '1']
    detail = 'mode=1 lines %s, other form lines %s, first GuestOut line %s' % (ones[:3], other[:3], first_guest)
    if len(ones) != 1 or other:
        return False, detail
    if not order:
        return True, detail
    if first_guest is None:
        return None, detail
    return ones[0] < first_guest, detail


def env_admit(tag, run):
    """(ok, detail) of the environment and command line of the run record (seal section 1)."""
    if run is None:
        return False, 'run record MISSING'
    env = run.get('env') or {}
    cmd = run.get('cmdline') or []
    bad = []
    for k in env:
        if k.startswith('KYTY_FIX_') or k in ('KYTY_GAME_PATCH', 'KYTY_GPU_CHECKPOINTS'):
            bad.append(k)
    lvl = SPEC[tag]['level']
    if env.get('KYTY_GUEST_ARGS') != '-lvl ' + lvl:
        bad.append('KYTY_GUEST_ARGS=%s' % env.get('KYTY_GUEST_ARGS'))
    val = None
    for i, x in enumerate(cmd):
        if x == '--vulkan-validation':
            val = cmd[i + 1] if i + 1 < len(cmd) else None
    if SPEC[tag]['kind'] == 'w':
        if not env.get('VK_LAYER_PATH'):
            bad.append('no VK_LAYER_PATH')
        if env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT') != LIMIT:
            bad.append('VK_LAYER_DUPLICATE_MESSAGE_LIMIT=%s' % env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT'))
        for k in ('VK_LAYER_MESSAGE_ID_FILTER', 'KYTY_PIPELINE_PRECACHE', 'KYTY_REC'):
            if k in env:
                bad.append(k)
        if val != 'true':
            bad.append('--vulkan-validation %s' % val)
    else:
        if not env.get('KYTY_REC'):
            bad.append('no KYTY_REC')
        for k in env:
            if k.startswith('VK_LAYER_'):
                bad.append(k)
        if val != 'false':
            bad.append('--vulkan-validation %s' % val)
    return not bad, 'env keys %s; offending %s' % (sorted(env), bad)


def read(p, tag):
    spec = SPEC[tag]
    kind = spec['kind']
    r = scan(p['log'], spec['level'])
    sd, srev, ssha = stdout_scan(p['stdout'])
    rj = text(p['run'])
    run = json.loads(rj) if rj else None
    att = ((run or {}).get('attempts') or [{}])[0]
    sha = first_line(text(p['installed_sha'])) or None
    sha_b = first_line(text(p['installed_before'])) or None
    sha_a = first_line(text(p['installed_after'])) or None
    cold_t = text(p['cold'])
    mc = text(p['manifest_cmp'])
    idx_n = None
    if p.get('idx') and os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as f:
            idx_n = sum(1 for _ in f)
    gl = None
    gt = text(p['glitch'])
    if gt:
        m = RX_GL.search(gt)
        gl = int(m.group(1)) if m else None
    st = text(p['sheet'])
    sheet = next((x.strip() for x in st.split('\n') if x.startswith('sheet: ')), None) if st else None
    stc = r['stc']
    rev = r['rev'] + srev
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env_ok, env_info = env_admit(tag, run)
    death = r['death'] + (sd or [])
    fb4 = fix_member(r['fixl']['B4'], r['first_guest'])
    ff8 = fix_member(r['fixl']['F8'], r['first_guest'])
    ff8v = fix_member(r['fixl']['F8'], r['first_guest'], order=False)
    fb24 = fix_member(r['fixl']['B24'], r['first_guest'])
    ended_ok = None
    if run is not None:
        ended_ok = (att.get('outcome') == 'ok' and att.get('hold_exit') is None and att.get('hold_s') is not None
                    and att.get('hold_s') >= spec['hold'])
    res = dict(tag=tag, kind=kind, level=spec['level'], hold_req=spec['hold'], log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'],
               stdout_sha256=ssha, stdout_present=sd is not None, rev=rev[:6],
               json_binary=(run or {}).get('binary_sha256'), installed_sha=sha, installed_before=sha_b, installed_after=sha_a,
               version_in_bin=has_bytes(p['bin'], VERSION), prereg=pre, seal_sha=seal_sha, env_ok=env_ok, env_info=env_info,
               stc=stc, cold_txt=(cold_t or '').strip()[:200],
               attempt=dict((k, att.get(k)) for k in ('outcome', 'detail', 'hold_exit', 'hold_s', 'stable_s', 'close_posted', 'close_rc',
                                                      'close_killed', 'close_s', 'close_wait_s')),
               first_guest=r['first_guest'], entry_line=r['entry_line'], scene_change_line=r['scene_change_line'],
               first_scene_n=r['first_scene_n'], hold_us=r['hold_us'], hold_s=round(r['hold_us'] / 1e6, 1), k2_after=r['k2_after'],
               dt_max_after=r['dt_max_after'], ft_rows=r['ft_rows'], death=death, vke=r['vke'], vke_06479=r['vke_06479'], vkw=r['vkw'],
               vk_limit=r['vk_limit'], dual=r['dual'][:2], skipped_draw=r['skipped_draw'], win=r['win'], recovering=r['recovering'],
               gamepatch=r['gamepatch'], quit_line=r['quit_line'], fixl=r['fixl'], idx_records=idx_n, glitches=gl, sheet=sheet,
               manifest=first_line(mc)[:200])
    rev_ok = bool(rev) and all(t in (REV, VERSION.decode()) for _, _, t in rev)
    adm = [('binary sha256 of the tag = 2c9b69b9 (json binary_sha256 and installed_sha.txt; N1 item 530 (g))',
            res['json_binary'] == BIN_EXPECT and sha == BIN_EXPECT),
           ('version string ...-1889-g302347b4 in the binary file (N1)', bool(res['version_in_bin'])),
           ('every revision text of the log and stdout = %s (N1; SDL_REVISION never read) %s' % (REV, [t for _, _, t in rev][:3]), rev_ok),
           ('prereg sha256 of the json = sha256 of the seal file', bool(pre) and pre == seal_sha),
           ('environment and command line of the form (no KYTY_FIX_*, no KYTY_GAME_PATCH / KYTY_GPU_CHECKPOINTS; %s)'
            % ('W of item 295 (b)' if kind == 'w' else 'V with video, no validation'), env_ok),
           ('cold form: %s absent before the start' % DIR_FIX, bool(cold_t) and 'absent' in cold_t and 'present' not in cold_t),
           ('no interference: window minimized / Recovering Vulkan swapchain / GamePatch line',
            not r['win'].get('minimized') and not r['recovering'] and not r['gamepatch'])]
    form = [('installed FS6 9325446c before the tag', sha_b == WANT),
            ('installed FS6 9325446c after the return', sha_a == WANT),
            ('manifest of the caches before = after the return (manifest cmp EQUAL)', bool(mc) and mc.startswith('manifest cmp EQUAL'))]
    mem = [('entered (entry line of %s)' % spec['level'], r['entry_line'] is not None),
           ('translation cache directory %s in every line (>= 1 line) %s' % (DIR_FIX, stc[:2]),
            len(stc) >= 1 and all(s.replace('/', '\\').endswith('\\' + DIR_FIX) for s in stc)),
           ('FixB4: mode=1 before the first GuestOut (%s)' % fb4[1], fb4[0]),
           ('FixF8: mode=1 before the first GuestOut, letter of item 471 (g)(3) (%s)' % ff8[1], ff8[0]),
           ('hold >= 300 s (sum dt after the first scene frame)', r['hold_us'] >= HOLD_MIN_US),
           ('the process lived to the end of the hold (outcome ok, hold_exit null, hold_s >= %d)' % spec['hold'], ended_ok)]
    if kind in VIDEO_KINDS:
        mem += [('0 death markers (log and stdout)', None if sd is None else not death),
                ('video index records >= 3000', (idx_n or 0) >= VIDEO_MIN),
                ('0 one-frame glitches', None if gl is None else gl == 0),
                ('sheet for the lead made', sheet is not None)]
    else:
        mem += [('0 [Vulkan][E] (VUID-06479 lines %d)' % r['vke_06479'], r['vke'] == 0),
                ('positive control of the layer, [Vulkan][W] > 0', r['vkw'] > 0),
                ('DualSrcBlend supported=1 enabled=1 before the first GuestOut',
                 any(s == 1 and e == 1 and r['first_guest'] is not None and ln < r['first_guest'] for ln, s, e in r['dual']))]
    rep = [('frames >= 1 s after the first scene frame = %d, max dt_us %d (REPORT, not a gate - cold entry)' % (r['k2_after'], r['dt_max_after']),
            r['entry_line'] is not None and r['k2_after'] == 0),
           ('FixF8 by the reading of item 518 (v)(4): exactly 1 line mode=1, order not a gate (REPORT, executor variant)', ff8v[0]),
           ('FixB24: mode=1 before the first GuestOut (REPORT, base FS7 control beyond item 471 (g)(3); %s)' % fb24[1], fb24[0]),
           ('AsyncPipelines: skipped draw lines = %d (REPORT)' % r['skipped_draw'], r['skipped_draw'] == 0),
           ('last-time-reporting lines of the layer = %d (REPORT)' % r['vk_limit'], r['vk_limit'] == 0)]
    if kind == 'w':
        rep.append(('0 death markers (REPORT for W) %s' % death[:2], None if sd is None else not death))
    res['rows'] = dict(ADMIT=adm, FORM=form, MEMBER=mem, REPORT=rep)
    if not all(v for _, v in adm):
        word = 'NOT_ADMITTED'
    elif not all(v for _, v in form):
        word = 'FORM_FAIL'
    elif any(v is False for _, v in mem):
        word = 'MEMBERS_FAIL'
    elif any(v is None for _, v in mem):
        word = 'NOT_EVALUABLE'
    else:
        word = 'MEMBERS_PASS'
    res['reading'] = word
    return res


def yn(v):
    if v is None:
        return 'NOT_DETERMINED'
    return 'YES' if v else 'NO'


def rows(res):
    out = ['FS8C %s kind %s level %s log sha256 %s lines %d stdout sha256 %s' % (res['tag'], res['kind'], res['level'], res['log_sha256'],
                                                                              res['log_lines'], res['stdout_sha256'])]
    add = out.append
    add('  binary: json %s installed_sha %s (expected %s); installed before %s after %s (expected %s); revision texts %s'
        % (res['json_binary'], res['installed_sha'], BIN_EXPECT, res['installed_before'], res['installed_after'], WANT, res['rev']))
    add('  prereg %s seal %s; %s' % (res['prereg'], res['seal_sha'], res['env_info']))
    add('  Shader translation cache lines %d %s; form: %s' % (len(res['stc']), res['stc'][:2], res['cold_txt']))
    add('  Fix lines (line, mode): B4 %s F8 %s B24 %s; first GuestOut line %s'
        % (res['fixl']['B4'][:3], res['fixl']['F8'][:3], res['fixl']['B24'][:3], res['first_guest']))
    add('  entry line %s; scene change line %s; first scene frame n %s; hold (sum dt after it) %.1f s; frames >= 1 s after it %d '
        '(max dt_us %d); FrameTrace rows %d' % (res['entry_line'], res['scene_change_line'], res['first_scene_n'], res['hold_s'],
                                               res['k2_after'], res['dt_max_after'], res['ft_rows']))
    add('  death markers: %d %s; emulator stdout %s' % (len(res['death']), res['death'][:3], 'present' if res['stdout_present'] else 'MISSING'))
    add('  window: %s, Recovering Vulkan swapchain %d; GamePatch lines %d; AsyncPipelines: skipped draw %d'
        % (res['win'] or 'none', res['recovering'], res['gamepatch'], res['skipped_draw']))
    if res['kind'] in VIDEO_KINDS:
        add('  video: index records %s; one-frame glitches %s; %s' % (res['idx_records'], res['glitches'], res['sheet']))
    add('  W: [Vulkan][E] %d (VUID-06479 %d); [Vulkan][W] %d; last-time-reporting lines %d; DualSrcBlend %s'
        % (res['vke'], res['vke_06479'], res['vkw'], res['vk_limit'], res['dual']))
    add('  manifest: %s' % res['manifest'])
    add('  EXIT (report): %s; Event: quit line %s' % (res['attempt'], res['quit_line']))
    for cls in ('ADMIT', 'FORM', 'MEMBER', 'REPORT'):
        for name, val in res['rows'][cls]:
            add('  %s %s: %s' % (cls, name, yn(val)))
    add('  READING %s' % res['reading'])
    return out


def main(argv):
    if '--dir' in argv:
        base = argv[argv.index('--dir') + 1]
        if '--tag' not in argv:
            raise SystemExit('--dir needs --tag')
        tag = argv[argv.index('--tag') + 1]
        if tag not in SPEC:
            raise SystemExit('unknown tag: %s' % tag)
        p = paths(tag, base)
    else:
        tag = argv[0] if argv else ''
        if tag not in SPEC:
            raise SystemExit('unknown tag: %s' % tag)
        p = paths(tag)
    res = read(p, tag)
    print('\n'.join(asc(x) for x in rows(res)))
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w') as f:
            json.dump(res, f, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
