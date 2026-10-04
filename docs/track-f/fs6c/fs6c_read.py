"""Track F link FS6c (HPP-557; ROADMAP s122 item 454 (g)(3), item 461 (g), item 476): the reader of one tag of the FS6 ship binary
9325446c at the defaults of the binary.  Rows only, no verdict (the verdict is FS6d's, HPP-558).
usage: python fs6c_read.py <fs6_v|fs6_w> [--json <out.json>]
       python fs6c_read.py --dir <fixture dir> --tag-kind <v|w>   (fixtures: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt,
           installed_sha.txt, installed_before.txt, installed_after.txt, warm.txt, manifest_cmp.txt, manifest_before.tsv, manifest_run.tsv,
           bin.exe)
Port of C:/kyty/f287/f15e/f15e_read.py (F15e HPP-516, kind v = form b4_v) with the W rows of C:/kyty/f287/fs5/fs5c/fs5c_read.py (FS5c
HPP-511, kind w).
Definitions (seal docs/track-f/fs6c.md section 4):
  binary          installed_sha.txt (written after the install) = 9325446c...; the binary file carries the version string
                  'KytyPS5-2026-09-15-6a2987a-1879-g3904522d' (item 461 (g): the tag binary is known by sha256 and this string);
                  installed_before.txt and installed_after.txt = adb0c82f... (S12, items 437-438).  Revision text of the log
                  ('Fork build arigandores/KytyPS5 ' or ', git = '): reference, YES when it names 3904522.
  env             the env of the tag in es.json: no KYTY_FIX_* at all (KYTY_FIX_B4 included), no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS
                  (member of both kinds: the tags run at the defaults of the binary, item 454 (g)(3)).
  FixB4 line      'FixB4: mode=M'; the row wants >= 1 such line, every M = 1, the first before the first line carrying 'GuestOut' (member of
                  both kinds).
  directory       every 'Shader translation cache: <dir>' line ends with variant_fixb26_fixb1b_fixf10 (reference; signature 26ce5fc7 = the
                  installed one, item 461 (b)); warm form - warm.txt says 'present' (reference).
  entry           the first line 'GuestOut: Level has started: underwater_aerial_garden'; first scene frame - the first FrameTrace row after
                  it with draws >= 100; hold - sum dt_us of the FrameTrace rows after the first scene frame (before a scene change), member
                  >= 300 s; frames >= 1 s after the first scene frame - REPORT row, not a gate.
  hold end        the enter_scene attempt outcome 'ok' and hold_exit null = the process lived through the hold (member of both kinds).
  death markers   'Unhandled exception:', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort:', 'ErrorDeviceLost' in the log and in the
                  emulator stdout (member of v: 0; reference of w - form FS5c).
  video (v)       records of the video index >= 3000; one-frame glitches of s51_vidglitch.py ('one-frame glitches: N') = 0; the sheet
                  for the lead made (sheet.txt line 'sheet: ') - members.
  quit            the first log line 'Event: quit' (the harness exit, WM_CLOSE) must exist; after it in the log: 0 lines
                  '--- Fatal Error ---' and 0 lines 'm_files[index] == nullptr' (members of v; reference of w).  The stdout has no quit
                  line: both counts over the whole stdout are printed beside.
  exit            the attempt record of enter_scene: close_killed false and close_rc not null = the process ended before the harness
                  timeout (CLOSE_WAIT_S = 40 s after WM_CLOSE) - member of v, reference of w; close_rc (exit code) - REPORT row.
  _SaveData       the lines with label _SaveData of manifest_before.tsv (before the tag) and manifest_run.tsv (after the tag, before the
                  return): files, equal or not, the differing paths - REPORT row, not a gate.
  W rows (w)      '[Vulkan][E]' lines = 0; '[Vulkan][W]' lines > 0 (positive control of the layer); 'DualSrcBlend: supported=1 enabled=1'
                  before the first line carrying 'GuestOut' (item 295 (b)(4)) - members.
  manifest        manifest_cmp.txt first line starts with 'manifest cmp EQUAL' (caches, saves, GLCache before = after the return) - member.
  interference    a window line 'minimized' or 'Recovering Vulkan swapchain' (item 273 (z)) or a 'GamePatch:' line - the tag is not read
                  as an outcome (interference of the run; repeat only by an item of the lead).
ASCII output only."""
import hashlib, json, os, re, sys

G = 'C:/kyty/f287/fs6c'
SKY = 'underwater_aerial_garden'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_9325446c.exe'
BIN_EXPECT = '9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1879-g3904522d'
WANT = 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421'
REV = '3904522'
DIR_FIX = 'variant_fixb26_fixb1b_fixf10'
KINDS = ('v', 'w')
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
RX_B4 = re.compile(rb'FixB4: mode=(\d+)')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d+) enabled=(\d+)')
M_START = b'GuestOut: Level has started: '
M_QUIT = b'Event: quit'
M_FATAL = b'--- Fatal Error ---'
M_NULL = b'm_files[index] == nullptr'
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
K2_US = 1000000
VIDEO_MIN = 3000
HOLD_MIN_US = 300000000


def kind_of(tag):
    for k in KINDS:
        if tag == 'fs6_' + k:
            return k
    raise SystemExit('unknown tag: %s' % tag)


def paths(tag, kind, base=None):
    names = ('installed_sha', 'installed_before', 'installed_after', 'warm', 'manifest_cmp', 'glitch', 'sheet')
    if base is not None:
        p = dict((n, os.path.join(base, n + '.txt')) for n in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), mf_before=os.path.join(base, 'manifest_before.tsv'),
                 mf_run=os.path.join(base, 'manifest_run.tsv'), bin=os.path.join(base, 'bin.exe'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((n, os.path.join(d, n + '.txt')) for n in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag) if kind == 'v' else None, mf_before=os.path.join(d, 'manifest_before.tsv'),
             mf_run=os.path.join(d, 'manifest_run.tsv'), bin=BIN_PATH)
    return p


def text(path):
    if not path or not os.path.exists(path):
        return None
    return open(path, 'rb').read().decode('utf-8', 'replace')


def asc(s):
    return s.encode('ascii', 'replace').decode('ascii') if isinstance(s, str) else s


def rev_text(raw):
    for m in (M_FORK, M_GIT):
        if m in raw:
            return raw.split(m, 1)[1].split(b',', 1)[0].strip()[:80].decode('ascii', 'replace')
    return None


def scan(log_path, level):
    r = dict(lines=0, rev=[], stc=[], b4=[], guest_first=None, entry_line=None, scene_change_line=None, first_scene_n=None, hold_us=0,
             k2_after=0, dt_max_after=0, ft_rows=0, death=[], vke=0, vkw=0, vk_limit=0, dual=[], skipped_draw=0, win={}, recovering=0,
             gamepatch=0, quit_line=None, fatal_after_quit=0, null_after_quit=0, fatal_total=0, null_total=0)
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
            if b'FixB4:' in raw:
                m = RX_B4.search(raw)
                if m:
                    r['b4'].append((ln, int(m.group(1))))
            if M_START in raw:
                name = raw.split(M_START, 1)[1].strip().decode('ascii', 'replace')
                if r['entry_line'] is None:
                    if name == level:
                        r['entry_line'] = ln
                        after_entry = True
                elif r['scene_change_line'] is None:
                    r['scene_change_line'] = ln
            if r['guest_first'] is None and b'GuestOut' in raw:
                r['guest_first'] = ln
            if r['quit_line'] is None and M_QUIT in raw:
                r['quit_line'] = ln
            if M_FATAL in raw:
                r['fatal_total'] += 1
                if r['quit_line'] is not None:
                    r['fatal_after_quit'] += 1
            if M_NULL in raw:
                r['null_total'] += 1
                if r['quit_line'] is not None:
                    r['null_after_quit'] += 1
            if b'DualSrcBlend:' in raw:
                m = RX_DUAL.search(raw)
                if m:
                    r['dual'].append((ln, int(m.group(1)), int(m.group(2))))
            if b'[Vulkan][' in raw:
                if b'[Vulkan][E]' in raw:
                    r['vke'] += 1
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
        return None, 0, 0, None
    death, fatal, null = [], 0, 0
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for i, raw in enumerate(f, 1):
            h.update(raw)
            if M_FATAL in raw:
                fatal += 1
            if M_NULL in raw:
                null += 1
            for d in DEATH:
                if d in raw:
                    death.append(('stdout', d.decode(), i))
    return death, fatal, null, h.hexdigest()


def bin_version(path):
    if not path or not os.path.exists(path):
        return None
    return VERSION in open(path, 'rb').read()


def savedata(before_path, run_path):
    def lines(p):
        t = text(p)
        if t is None:
            return None
        return sorted(x for x in t.split('\n') if x.startswith('_SaveData\t'))
    a, b = lines(before_path), lines(run_path)
    if a is None or b is None:
        return dict(read=False, before=None if a is None else len(a), run=None if b is None else len(b), equal=None, diff=[])
    sa, sb = set(a), set(b)
    diff = ['before-only ' + x.split('\t')[1] for x in sorted(sa - sb)] + ['run-only ' + x.split('\t')[1] for x in sorted(sb - sa)]
    return dict(read=True, before=len(a), run=len(b), equal=a == b, diff=diff[:6])


def first_line(t):
    return (t or '').split('\n')[0].strip()


def read(p, kind):
    r = scan(p['log'], SKY)
    sd, sfatal, snull, ssha = stdout_scan(p['stdout'])
    rj = text(p['run'])
    run = json.loads(rj) if rj else None
    att = ((run or {}).get('attempts') or [{}])[0] if run else None
    env = (run or {}).get('env') or {}
    sha = first_line(text(p['installed_sha'])) or None
    sha_b = first_line(text(p['installed_before'])) or None
    sha_a = first_line(text(p['installed_after'])) or None
    warm_t = text(p['warm'])
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
    dir_ok = len(stc) >= 1 and all(s.replace('/', '\\').endswith('\\' + DIR_FIX) for s in stc)
    b4_ok = (len(r['b4']) >= 1 and all(mm == 1 for _, mm in r['b4'])
             and (r['guest_first'] is None or r['b4'][0][0] < r['guest_first']))
    rev = r['rev']
    rev_row = 'NOT_PRESENT' if not rev else ('YES' if all(REV in t for _, _, t in rev) else 'NO')
    fix_keys = sorted(k for k in env if k.startswith('KYTY_FIX_'))
    env_ok = None if run is None else (fix_keys == [] and 'KYTY_GAME_PATCH' not in env and 'KYTY_GPU_CHECKPOINTS' not in env)
    if att is None:
        hold_ok, end_ok, close_rc, close_info = None, None, None, 'run record MISSING'
    else:
        hold_ok = att.get('outcome') == 'ok' and att.get('hold_exit') is None
        if 'close_killed' not in att:
            end_ok = None
        else:
            end_ok = att.get('close_killed') is False and att.get('close_rc') is not None
        close_rc = att.get('close_rc')
        close_info = ('outcome %s hold_exit %s hold_s %s close_posted %s close_rc %s close_killed %s close_s %s close_wait_s %s'
                      % (att.get('outcome'), att.get('hold_exit'), att.get('hold_s'), att.get('close_posted'), att.get('close_rc'),
                         att.get('close_killed'), att.get('close_s'), att.get('close_wait_s')))
    death = r['death'] + (sd or [])
    return dict(kind=kind, level=SKY, log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'], stdout_sha256=ssha, rev=rev[:6],
                rev_row=rev_row, installed_sha=sha, installed_before=sha_b, installed_after=sha_a, sha_ok=sha == BIN_EXPECT,
                version_ok=bin_version(p['bin']), before_ok=sha_b == WANT, after_ok=sha_a == WANT,
                env=dict((k, env[k]) for k in sorted(env) if k.startswith('KYTY_FIX_') or k in ('KYTY_GAME_PATCH', 'KYTY_GPU_CHECKPOINTS')),
                env_ok=env_ok, b4=r['b4'][:3], b4_lines=len(r['b4']), b4_ok=b4_ok, guest_first=r['guest_first'], stc=stc[:3],
                dir_ok=dir_ok, warm_txt=(warm_t or '').strip()[:240], warm_ok=bool(warm_t) and ' present at ' in warm_t,
                entry_line=r['entry_line'], scene_change_line=r['scene_change_line'], first_scene_n=r['first_scene_n'],
                hold_us=r['hold_us'], hold_s=round(r['hold_us'] / 1e6, 1), k2_after=r['k2_after'], dt_max_after=r['dt_max_after'],
                ft_rows=r['ft_rows'], hold_ok=hold_ok, death=death, stdout_present=sd is not None,
                quit_line=r['quit_line'], fatal_after_quit=r['fatal_after_quit'], null_after_quit=r['null_after_quit'],
                fatal_log_total=r['fatal_total'], null_log_total=r['null_total'], fatal_stdout=sfatal, null_stdout=snull,
                end_ok=end_ok, close_rc=close_rc, close_info=close_info, vke=r['vke'], vkw=r['vkw'], vk_limit=r['vk_limit'],
                dual=r['dual'][:2], dual_ok=any(s == 1 and e == 1 and (r['guest_first'] is None or ln < r['guest_first'])
                                                for ln, s, e in r['dual']),
                skipped_draw=r['skipped_draw'], win=r['win'], recovering=r['recovering'], gamepatch=r['gamepatch'],
                idx_records=idx_n, glitches=gl, sheet=sheet,
                savedata=savedata(p['mf_before'], p['mf_run']), manifest=first_line(mc)[:200],
                manifest_ok=bool(mc) and mc.startswith('manifest cmp EQUAL'))


def yn(v):
    if v is None:
        return 'NOT_READ'
    if isinstance(v, str):
        return v
    return 'YES' if v else 'NO'


def rows(tag, res):
    k = res['kind']
    out = ['FS6C %s kind %s level %s log sha256 %s lines %d stdout sha256 %s' % (tag, k, res['level'], res['log_sha256'], res['log_lines'],
                                                                              res['stdout_sha256'])]
    add = out.append
    add('  binary: tag %s (expected %s); version string %s in the binary: %s; installed before %s after %s (expected %s); revision '
        'texts %s' % (res['installed_sha'], BIN_EXPECT, VERSION.decode(), yn(res['version_ok']), res['installed_before'],
                      res['installed_after'], WANT, res['rev']))
    add('  env of the tag (KYTY_FIX_*, KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS): %s' % res['env'])
    add('  FixB4 lines %d, first %s (first GuestOut line %s)' % (res['b4_lines'], res['b4'], res['guest_first']))
    add('  Shader translation cache lines %s; %s' % (res['stc'], res['warm_txt']))
    add('  entry line %s; scene change line %s; first scene frame n %s; hold (sum dt after it) %.1f s; frames >= 1 s after it %d '
        '(max dt_us %d)' % (res['entry_line'], res['scene_change_line'], res['first_scene_n'], res['hold_s'], res['k2_after'],
                            res['dt_max_after']))
    add('  death markers: %d %s; emulator stdout %s' % (len(res['death']), res['death'][:3], 'present' if res['stdout_present'] else 'MISSING'))
    add('  quit: first Event: quit line %s; after it in the log: --- Fatal Error --- %d, m_files[index] == nullptr %d; whole log %d / %d; '
        'whole stdout (no quit line there) %d / %d' % (res['quit_line'], res['fatal_after_quit'], res['null_after_quit'],
                                                       res['fatal_log_total'], res['null_log_total'], res['fatal_stdout'], res['null_stdout']))
    rc = res['close_rc']
    add('  exit: %s; exit code %s%s (REPORT row, 0 expected [I])' % (asc(res['close_info']), rc,
                                                                    '' if rc is None else ' (0x%08x)' % (rc & 0xffffffff)))
    sv = res['savedata']
    add('  _SaveData manifest (REPORT row, not a gate): before %s files, after the tag (before the return) %s files, equal %s, differing %s'
        % (sv['before'], sv['run'], yn(sv['equal']), sv['diff']))
    add('  window: %s, Recovering Vulkan swapchain %d; GamePatch lines %d; AsyncPipelines: skipped draw %d (reference)'
        % (res['win'] or 'none', res['recovering'], res['gamepatch'], res['skipped_draw']))
    add('  W: [Vulkan][E] %d; [Vulkan][W] %d; last-time-reporting lines %d; DualSrcBlend %s%s'
        % (res['vke'], res['vkw'], res['vk_limit'], res['dual'], '' if k == 'w' else ' (reference: no validation in kind v)'))
    if k == 'v':
        add('  video: index records %s; one-frame glitches %s; %s' % (res['idx_records'], res['glitches'], res['sheet']))
    add('  manifest: %s' % res['manifest'])
    m = [('binary sha256 of the tag = 9325446c (FS6 copy)', res['sha_ok']),
         ('version string ...-1879-g3904522d in the tag binary', res['version_ok']),
         ('installed adb0c82f before the tag', res['before_ok']),
         ('installed adb0c82f after the return', res['after_ok']),
         ('env: no KYTY_FIX_*, no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS (defaults of the binary)', res['env_ok']),
         ('revision text names 3904522 (reference)', res['rev_row']),
         ('translation cache directory %s in every line (reference)' % DIR_FIX, res['dir_ok']),
         ('warm form: %s present before the start (reference)' % DIR_FIX, res['warm_ok']),
         ('FixB4: mode=1 (every line) before the first GuestOut', res['b4_ok']),
         ('entered (entry line of %s)' % res['level'], res['entry_line'] is not None),
         ('hold >= 300 s after the first scene frame', res['hold_us'] >= HOLD_MIN_US),
         ('the process lived through the hold (outcome ok, hold_exit null)', res['hold_ok']),
         ('frames >= 1 s after the first scene frame = %d (REPORT, not a gate)' % res['k2_after'],
          res['entry_line'] is not None and res['k2_after'] == 0)]
    after_quit = None if res['quit_line'] is None else res['fatal_after_quit'] == 0 and res['null_after_quit'] == 0
    if k == 'v':
        m += [('0 death markers (log and stdout)', not res['death']),
              ('video index records >= 3000', (res['idx_records'] or 0) >= VIDEO_MIN),
              ('0 one-frame glitches', None if res['glitches'] is None else res['glitches'] == 0),
              ('sheet for the lead made', res['sheet'] is not None),
              ('exit by the harness: Event: quit line in the log', res['quit_line'] is not None),
              ('after Event: quit: 0 --- Fatal Error --- and 0 m_files[index] == nullptr (log)', after_quit),
              ('the process ended before the harness timeout (40 s after WM_CLOSE, not killed)', res['end_ok'])]
    else:
        m += [('0 [Vulkan][E]', res['vke'] == 0),
              ('positive control of the layer, [Vulkan][W] > 0', res['vkw'] > 0),
              ('DualSrcBlend supported=1 enabled=1 before the first GuestOut', res['dual_ok']),
              ('0 death markers (reference)', not res['death']),
              ('exit by the harness: Event: quit line in the log (reference)', res['quit_line'] is not None),
              ('after Event: quit: 0 --- Fatal Error --- and 0 m_files[index] == nullptr (reference)', after_quit),
              ('the process ended before the harness timeout (reference)', res['end_ok'])]
    m += [('manifest of the caches, saves and GLCache before = after the return', res['manifest_ok']),
          ('no interference: window minimized / Recovering Vulkan swapchain / GamePatch line (else not read as an outcome, question '
           'to the lead)', not res['win'].get('minimized') and not res['recovering'] and not res['gamepatch'])]
    for name, val in m:
        add('  ROW %s: %s' % (name, yn(val)))
    return out


def main(argv):
    if '--dir' in argv:
        base = argv[argv.index('--dir') + 1]
        kind = argv[argv.index('--tag-kind') + 1] if '--tag-kind' in argv else ''
        if kind not in KINDS:
            raise SystemExit('unknown kind: %s' % kind)
        tag = 'fixture'
        p = paths(tag, kind, base)
    else:
        tag = argv[0] if argv else ''
        kind = kind_of(tag)
        p = paths(tag, kind)
    res = read(p, kind)
    print('\n'.join(asc(x) for x in rows(tag, res)))
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w') as f:
            json.dump(res, f, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
