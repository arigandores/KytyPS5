"""Track F link F24e (HPP-664; ROADMAP s122 item 595 (e)(4), (zh); item 603 (v)): the reader of the tags b13_v (V Sky Garden) and b13_w (W
Sky Garden under the validation layer) of the F24c TEST binary 91f155b7 at KYTY_FIX_B13=1.  Rows only, no verdict (the verdict is F24f's,
HPP-665).
usage: python f24e_read.py b13_v|b13_w[_r1..3] [--json <out.json>]
       python f24e_read.py --dir <fixture dir> --form v|w   (fixtures: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt,
           installed_sha.txt, installed_before.txt, installed_after.txt, warm.txt, manifest_cmp.txt, manifest_before.tsv, manifest_run.tsv,
           bin.exe)
Port of C:/kyty/f287/f15e/f15e_read.py (F15e HPP-516, V form) with the W members of C:/kyty/s288/s18c2/s18c2_read.py (s18_w2, item 587).
Definitions (seal docs/track-f/f24e.md section 4):
  binary          installed_sha.txt (written after the install) = 91f155b7...; the binary file carries the version string
                  'KytyPS5-2026-09-15-6a2987a-1899-gfbae3a68' (F24d: KYTY_GIT_VERSION ...-1899-gfbae3a68 = F24c); installed_before.txt and
                  installed_after.txt = b3cee576... (S18, item 590).  Revision text of the log ('Fork build arigandores/KytyPS5 ' or
                  ', git = '): reference, YES when it names fbae3a6.
  env             es.json env: KYTY_FIX_B13 = '1'; no other KYTY_FIX_*, no KYTY_GAME_PATCH, no KYTY_GPU_CHECKPOINTS, no KYTY_SHADER_SEED,
                  no KYTY_S_REPLAY, no KYTY_S_REPLAY_TEST (the other defaults of the binary).  Form v: no VK_LAYER_*, no --vulkan-validation
                  in the command line.  Form w: VK_LAYER_PATH not empty, VK_LAYER_DUPLICATE_MESSAGE_LIMIT = 100000000, no
                  VK_LAYER_MESSAGE_ID_FILTER, no other VK_LAYER_*; '--vulkan-validation true' in the command line.
  FixB13 line     'FixB13: mode=M'; >= 1 line, every M = 1, the first before the first line carrying 'GuestOut' (member, both forms).
  directory       every 'Shader translation cache: <dir>' line ends with variant_fixb26_fixb1b_fixf10_fixf19 (reference; signature 9177b426 =
                  S18, F24d); warm.txt - the state before the start (reference).
  entry           the first line 'GuestOut: Level has started: underwater_aerial_garden' and the attempt outcome 'ok'; first scene frame -
                  the first FrameTrace row after the entry line with draws >= 100; hold - sum dt_us of the FrameTrace rows after the first
                  scene frame (before a scene change).
  v               hold >= 300 s (member); the process lived through the hold (outcome ok, hold_exit null) (member); frames with
                  dt_us >= 1 000 000 after the first scene frame = 0 (member); video index records >= 3000, one-frame glitches of
                  s51_vidglitch.py = 0, the sheet for the lead made (members).
  w               the process lived to the end of the hold: outcome ok, hold_exit null, hold_s >= 310 (member); 0 lines '[Vulkan][E]'
                  (member); 0 lines 'this will be the last time reporting it' (limit lines of the layer, member); positive control of the
                  layer - [Vulkan][W] > 0 and a line 'DualSrcBlend: supported=1 enabled=1' before the first GuestOut (member);
                  VALIDATION_STOP (a [Vulkan][E] line and the process did not live to the end of the hold) - NO (member); frames >= 1 s
                  (REPORT under the layer).
  death markers   'Unhandled exception:', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort:', 'ErrorDeviceLost' in the log and in the
                  emulator stdout (member: 0, both forms).
  manifest        manifest_cmp.txt first line starts with 'manifest cmp EQUAL' (caches, seeds, saves, GLCache before = after the return).
  interference    a window line 'minimized' or 'Recovering Vulkan swapchain' (item 273 (z)) or a 'GamePatch:' line - the tag is not read
                  as an outcome (interference of the run; the attempt is not spent).
ASCII output only."""
import hashlib, json, os, re, sys

G = 'C:/kyty/f287/f24e'
SKY = 'underwater_aerial_garden'
TAGS = ('b13_v', 'b13_w')
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_91f155b7.exe'
BIN_EXPECT = '91f155b70f867124781a687b0d86442f45abed90e33d4b9e749d296ccfa63e2f'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1899-gfbae3a68'
WANT = 'b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a'
REV = 'fbae3a6'
DIR_FIX = 'variant_fixb26_fixb1b_fixf10_fixf19'
LIMIT = '100000000'
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
RX_B13 = re.compile(rb'FixB13: mode=(\d+)')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d) enabled=(\d)')
M_START = b'GuestOut: Level has started: '
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
M_LIMIT = b'this will be the last time reporting it'
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
NO_ENV = ('KYTY_GAME_PATCH', 'KYTY_GPU_CHECKPOINTS', 'KYTY_SHADER_SEED', 'KYTY_S_REPLAY', 'KYTY_S_REPLAY_TEST')
K2_US = 1000000
VIDEO_MIN = 3000
HOLD_V_US = 300000000
HOLD_W_S = 310


def base_of(tag):
    return re.sub(r'_r[1-3]$', '', tag)


def paths(tag=None, base=None):
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
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), mf_before=os.path.join(d, 'manifest_before.tsv'),
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
    r = dict(lines=0, rev=[], stc=[], b13=[], dual=[], guest_first=None, entry_line=None, scene_change_line=None, first_scene_n=None,
             hold_us=0, scene_frames=0, k2_after=0, dt_max_after=0, ft_rows=0, death=[], vke=0, vkw=0, vk_limit=0, skipped_draw=0, win={}, recovering=0,
             gamepatch=0, rebuild_skipped=0)
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
                            r['scene_frames'] += 1
                            r['dt_max_after'] = max(r['dt_max_after'], dt)
                            if dt >= K2_US:
                                r['k2_after'] += 1
                continue
            rv = rev_text(raw)
            if rv is not None and len(r['rev']) < 20:
                r['rev'].append(('log', ln, rv))
            if b'Shader translation cache: ' in raw:
                r['stc'].append(raw.split(b'Shader translation cache: ', 1)[1].strip()[:200].decode('ascii', 'replace'))
            if b'FixB13:' in raw:
                m = RX_B13.search(raw)
                if m:
                    r['b13'].append((ln, int(m.group(1))))
            if b'DualSrcBlend:' in raw:
                m = RX_DUAL.search(raw)
                if m:
                    r['dual'].append((ln, int(m.group(1)), int(m.group(2))))
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
            if b'[Vulkan][' in raw:
                if b'[Vulkan][E]' in raw:
                    r['vke'] += 1
                if b'[Vulkan][W]' in raw:
                    r['vkw'] += 1
            if M_LIMIT in raw:
                r['vk_limit'] += 1
            if b'AsyncPipelines: skipped draw' in raw:
                r['skipped_draw'] += 1
            if b'rebuild skipped' in raw:
                r['rebuild_skipped'] += 1
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


def env_check(run, form):
    """None when there is no run record; else the list of offending items (empty = the form of the tag)."""
    if run is None:
        return None
    env = run.get('env') or {}
    bad = []
    if env.get('KYTY_FIX_B13') != '1':
        bad.append('KYTY_FIX_B13=%s' % env.get('KYTY_FIX_B13'))
    bad += ['extra %s' % k for k in sorted(env) if k.startswith('KYTY_FIX_') and k != 'KYTY_FIX_B13']
    bad += ['extra %s' % k for k in NO_ENV if k in env]
    vk = dict((k, v) for k, v in env.items() if k.startswith('VK_LAYER_'))
    cmd = [str(x) for x in (run.get('cmdline') or [])]
    val = None
    for i, x in enumerate(cmd):
        if x == '--vulkan-validation':
            val = cmd[i + 1] if i + 1 < len(cmd) else ''
    if form == 'w':
        if not vk.get('VK_LAYER_PATH'):
            bad.append('no VK_LAYER_PATH')
        if vk.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT') != LIMIT:
            bad.append('VK_LAYER_DUPLICATE_MESSAGE_LIMIT=%s' % vk.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT'))
        bad += ['VK_LAYER_* extra %s' % k for k in sorted(vk) if k not in ('VK_LAYER_PATH', 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT')]
        if val != 'true':
            bad.append('--vulkan-validation %s' % val)
    else:
        bad += ['VK_LAYER_* %s' % k for k in sorted(vk)]
        if val is not None and val != 'false':
            bad.append('--vulkan-validation %s' % val)
    return bad


def read(p, form):
    r = scan(p['log'], SKY)
    sd, ssha = stdout_scan(p['stdout'])
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
    b13_ok = (len(r['b13']) >= 1 and all(mm == 1 for _, mm in r['b13'])
              and r['guest_first'] is not None and r['b13'][0][0] < r['guest_first'])
    rev = r['rev']
    rev_row = 'NOT_PRESENT' if not rev else ('YES' if all(REV in t for _, _, t in rev) else 'NO')
    bad = env_check(run, form)
    if att is None:
        lived_v = lived_w = entered = None
        close_rc, close_info = None, 'run record MISSING'
    else:
        lived_v = att.get('outcome') == 'ok' and att.get('hold_exit') is None
        lived_w = lived_v and (att.get('hold_s') or 0) >= HOLD_W_S
        entered = r['entry_line'] is not None and att.get('outcome') == 'ok'
        close_rc = att.get('close_rc')
        close_info = ('outcome %s hold_exit %s hold_s %s close_posted %s close_rc %s close_killed %s close_s %s'
                      % (att.get('outcome'), att.get('hold_exit'), att.get('hold_s'), att.get('close_posted'), att.get('close_rc'),
                         att.get('close_killed'), att.get('close_s')))
    dual_before = [x for x in r['dual'] if r['guest_first'] is not None and x[0] < r['guest_first'] and x[1] == 1 and x[2] == 1]
    death = r['death'] + (sd or [])
    return dict(form=form, level=SKY, log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'], stdout_sha256=ssha, rev=rev[:6],
                rev_row=rev_row, installed_sha=sha, installed_before=sha_b, installed_after=sha_a, sha_ok=sha == BIN_EXPECT,
                version_ok=bin_version(p['bin']), before_ok=sha_b == WANT, after_ok=sha_a == WANT,
                env=dict((k, env[k]) for k in sorted(env) if k.startswith('KYTY_FIX_') or k.startswith('VK_LAYER_') or k in NO_ENV),
                env_bad=bad, env_ok=None if bad is None else not bad,
                b13=r['b13'][:3], b13_lines=len(r['b13']), b13_ok=b13_ok, guest_first=r['guest_first'], stc=stc[:3], dir_ok=dir_ok,
                warm_txt=(warm_t or '').strip()[:240], entry_line=r['entry_line'], entered=entered,
                scene_change_line=r['scene_change_line'], first_scene_n=r['first_scene_n'], hold_us=r['hold_us'],
                hold_s=round(r['hold_us'] / 1e6, 1), scene_frames=r['scene_frames'],
                mean_dt_us=round(r['hold_us'] / r['scene_frames'], 1) if r['scene_frames'] else None, k2_after=r['k2_after'], dt_max_after=r['dt_max_after'], ft_rows=r['ft_rows'],
                lived_v=lived_v, lived_w=lived_w, death=death, stdout_present=sd is not None, close_rc=close_rc, close_info=close_info,
                vke=r['vke'], vkw=r['vkw'], vk_limit=r['vk_limit'], dual=r['dual'][:3], dual_ok=r['vkw'] > 0 and len(dual_before) >= 1,
                validation_stop=None if lived_w is None else (r['vke'] > 0 and not lived_w),
                skipped_draw=r['skipped_draw'], rebuild_skipped=r['rebuild_skipped'], win=r['win'], recovering=r['recovering'],
                gamepatch=r['gamepatch'], idx_records=idx_n, glitches=gl, sheet=sheet,
                savedata=savedata(p['mf_before'], p['mf_run']), manifest=first_line(mc)[:200],
                manifest_ok=bool(mc) and mc.startswith('manifest cmp EQUAL'))


def yn(v):
    if v is None:
        return 'NOT_READ'
    if isinstance(v, str):
        return v
    return 'YES' if v else 'NO'


def members(res):
    m = [('binary sha256 of the tag = 91f155b7 (F24c copy)', res['sha_ok']),
         ('version string ...-1899-gfbae3a68 in the tag binary', res['version_ok']),
         ('installed b3cee576 before the tag', res['before_ok']),
         ('installed b3cee576 after the return', res['after_ok']),
         ('env = form %s: KYTY_FIX_B13=1, other defaults of the binary%s' % (
             res['form'], ', W layer form of s18_w2' if res['form'] == 'w' else ', no layer'), res['env_ok']),
         ('FixB13: mode=1 (every line) before the first GuestOut', res['b13_ok']),
         ('entered (Level has started: %s, outcome ok)' % res['level'], res['entered'])]
    if res['form'] == 'v':
        m += [('hold >= 300 s after the first scene frame', res['hold_us'] >= HOLD_V_US),
              ('the process lived through the hold (outcome ok, hold_exit null)', res['lived_v']),
              ('0 frames >= 1 s after the first scene frame', res['entry_line'] is not None and res['first_scene_n'] is not None
               and res['k2_after'] == 0),
              ('0 death markers (log and stdout)', None if not res['stdout_present'] else not res['death']),
              ('video index records >= 3000', (res['idx_records'] or 0) >= VIDEO_MIN),
              ('0 one-frame glitches', None if res['glitches'] is None else res['glitches'] == 0),
              ('sheet for the lead made', res['sheet'] is not None)]
    else:
        m += [('the process lived to the end of the hold (outcome ok, hold_exit null, hold_s >= 310)', res['lived_w']),
              ('0 death markers (log and stdout)', None if not res['stdout_present'] else not res['death']),
              ('0 [Vulkan][E]', res['log_sha256'] is not None and res['vke'] == 0),
              ('0 limit lines of the layer', res['log_sha256'] is not None and res['vk_limit'] == 0),
              ('positive control of the layer: [Vulkan][W] > 0 and DualSrcBlend: supported=1 enabled=1 before the first GuestOut',
               res['dual_ok']),
              ('no VALIDATION_STOP ([Vulkan][E] and the process did not live to the end of the hold)',
               None if res['validation_stop'] is None else not res['validation_stop'])]
    m += [('manifest of the caches, seeds, saves and GLCache before = after the return', res['manifest_ok']),
          ('no interference: window minimized / Recovering Vulkan swapchain / GamePatch line (else not read as an outcome, question '
           'to the lead)', not res['win'].get('minimized') and not res['recovering'] and not res['gamepatch'])]
    return m


def rows(tag, res):
    out = ['F24E %s form %s level %s log sha256 %s lines %d stdout sha256 %s' % (tag, res['form'], res['level'], res['log_sha256'],
                                                                              res['log_lines'], res['stdout_sha256'])]
    add = out.append
    add('  binary: tag %s (expected %s); version string %s in the binary: %s; installed before %s after %s (expected %s); revision '
        'texts %s' % (res['installed_sha'], BIN_EXPECT, VERSION.decode(), yn(res['version_ok']), res['installed_before'],
                      res['installed_after'], WANT, res['rev']))
    add('  env of the tag (KYTY_FIX_*, VK_LAYER_*, forbidden keys): %s; offending %s' % (res['env'], res['env_bad']))
    add('  FixB13 lines %d, first %s (first GuestOut line %s)' % (res['b13_lines'], res['b13'], res['guest_first']))
    add('  Shader translation cache lines %s; %s' % (res['stc'], res['warm_txt']))
    add('  entry line %s; scene change line %s; first scene frame n %s; hold (sum dt after it) %.1f s; frames >= 1 s after it %d '
        '(max dt_us %d)' % (res['entry_line'], res['scene_change_line'], res['first_scene_n'], res['hold_s'], res['k2_after'],
                            res['dt_max_after']))
    add('  REF frame time after the first scene frame (item 603 (b)(3) N3: reference, not a member): frames %d, mean dt_us %s'
        % (res['scene_frames'], res['mean_dt_us']))
    add('  death markers: %d %s; emulator stdout %s' % (len(res['death']), res['death'][:3], 'present' if res['stdout_present'] else 'MISSING'))
    rc = res['close_rc']
    add('  exit: %s; exit code %s%s (REPORT row)' % (asc(res['close_info']), rc, '' if rc is None else ' (0x%08x)' % (rc & 0xffffffff)))
    add('  layer: [Vulkan][E] %d, [Vulkan][W] %d, limit lines %d, DualSrcBlend lines %s' % (res['vke'], res['vkw'], res['vk_limit'],
                                                                                         res['dual']))
    sv = res['savedata']
    add('  _SaveData manifest (REPORT row, not a gate): before %s files, after the tag (before the return) %s files, equal %s, differing %s'
        % (sv['before'], sv['run'], yn(sv['equal']), sv['diff']))
    add('  window: %s, Recovering Vulkan swapchain %d; GamePatch lines %d; AsyncPipelines: skipped draw %d; rebuild skipped lines %d '
        '(reference)' % (res['win'] or 'none', res['recovering'], res['gamepatch'], res['skipped_draw'], res['rebuild_skipped']))
    if res['form'] == 'v':
        add('  video: index records %s; one-frame glitches %s; %s' % (res['idx_records'], res['glitches'], res['sheet']))
    else:
        add('  frames >= 1 s after the first scene frame under the layer: %d (REPORT, not a gate)' % res['k2_after'])
    add('  manifest: %s' % res['manifest'])
    add('  REF revision text names %s: %s' % (REV, res['rev_row']))
    add('  REF translation cache directory %s in every line: %s' % (DIR_FIX, yn(res['dir_ok'])))
    for name, val in members(res):
        add('  ROW %s: %s' % (name, yn(val)))
    return out


def main(argv):
    if '--dir' in argv:
        tag = 'fixture'
        form = argv[argv.index('--form') + 1] if '--form' in argv else 'v'
        p = paths(base=argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        if base_of(tag) not in TAGS:
            raise SystemExit('unknown tag: %s' % tag)
        form = 'v' if base_of(tag) == 'b13_v' else 'w'
        p = paths(tag)
    res = read(p, form)
    print('\n'.join(asc(x) for x in rows(tag, res)))
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w') as f:
            json.dump(res, f, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
