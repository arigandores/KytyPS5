"""Track F link FS5c (HPP-511; ROADMAP s122 item 410 (g)(3), item 418): the reader of one tag of the FS5 binary 631ff987.
usage: python fs5c_read.py <tag> [--json <out.json>]            tags fs5_v, fs5_w, fs5_r1, fs5_hb
       python fs5c_read.py --dir <fixture dir> --tag-kind <v|w|r1|hb>   (fixtures: log.txt, stdout.txt, es.json, rec.idx, glitch.txt,
           sheet.txt, installed_sha.txt, installed_before.txt, installed_after.txt, cold.txt, manifest_cmp.txt, manifest_cmp_ref.txt)
Port of C:/kyty/f287/f12f/f12f_read.py (F12f HPP-480, edition 2 cd9deca6) with: the FS5 copy 631ff987 (every kind; the defaults of FS5,
no KYTY_FIX_F10 in the env), the installed FS4 31cbfee8 before the tag and after the return; the R1 rows of C:/kyty/f287/fs4c/fs4c_read.py
(FS4c HPP-472: FixSval mode=1 before the first GuestOut, 'SPIR-V validation failed' lines and hashes, FixSvalStat validated - reference);
the kind hb (V of hoover_beach) - REFERENCE, not a gate (item 410 (g)(3)); no RenderDoc kind.  Rows only, no verdict (the verdict is
FS5d's, HPP-512).
Definitions (seal docs/track-f/fs5c.md section 4):
  binary          installed_sha.txt (written after the install) = 631ff987...; installed_before.txt and installed_after.txt = 31cbfee8...
                  (the installed binary inside the lock before the tag and after the return).  Revision text (log / stdout 'Fork build
                  arigandores/KytyPS5 ' or ', git = '): reference, names 0e72bc1 (KYTY_GIT_REVISION of FS5a; YES / NO / NOT_PRESENT,
                  never a gate; the SDL_REVISION string of the binary is not read - item 418 (b)(1)).
  directory       every line 'Shader translation cache: <dir>'; FIXF10 row = >= 1 such line and every one ends with
                  variant_fixb26_fixb1b_fixf10 (member of every kind).
  cold form       cold.txt says 'absent' (variant_fixb26_fixb1b_fixf10 did not exist before the start) AND the first 'PipelinePrecache:'
                  line is 'PipelinePrecache: no ...variant_fixb26_fixb1b_fixf10...pipelines.bin yet' (reference; item 418 (v): no startup
                  precache on the first launch of FS5).
  FixSval line    'FixSval: mode=M ubo_std_layout=U'; the row wants >= 1 such line, all M=1 and U=1, the first before the first line carrying
                  'GuestOut' (member of r1; reference of v, w, hb).
  FixSvalStat     'FixSvalStat: validated=N rejected=R' (only with --shader-validation true): the last line printed (reference of r1, hb).
  validation failed  lines containing 'SPIR-V validation failed' in the log and in the stdout, distinct hashes 'hash=0x...' (member of r1:
                  0; reference of the others).
  entry           the first line 'GuestOut: Level has started: <level>'; first scene frame - the first FrameTrace row after it with
                  draws >= 100; hold - sum dt_us of the FrameTrace rows after the first scene frame (before a scene change); frames >= 1 s
                  - FrameTrace rows with dt_us >= 1 000 000 after the first scene frame (before a scene change): REPORT row, not a gate.
  death markers   'Unhandled exception:', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort:', 'ErrorDeviceLost' in the log and in the
                  emulator stdout.
  process end     the enter_scene attempt outcome 'exited' or hold_exit not null = the process ended before the timeout.
  W rows          '[Vulkan][E]' lines = 0; '[Vulkan][W]' lines > 0 (positive control of the layer); 'DualSrcBlend: supported=1
                  enabled=1' before the first line carrying 'GuestOut' (item 295 (b)(4)).
  video           (v, r1, hb) records of the video index >= 3000; one-frame glitches of s51_vidglitch.py (glitch.txt 'one-frame
                  glitches: N') = 0; the sheet for the lead made (sheet.txt line 'sheet: ').
  manifest        manifest_cmp.txt and manifest_cmp_ref.txt first lines start with 'manifest cmp EQUAL'.
  interference    a window line 'minimized' or 'Recovering Vulkan swapchain' (item 273 (z)) or a 'GamePatch:' line - the tag is not read
                  as an outcome (interference of the run; repeat only by an item of the lead).
ASCII output only."""
import hashlib, json, os, re, sys

G = 'C:/kyty/f287/fs5/fs5c'
SKY = 'underwater_aerial_garden'
HB = 'hoover_beach'
BIN_EXPECT = '631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17'
WANT = '31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5'
REV = '0e72bc1'
DIR_FIX = 'variant_fixb26_fixb1b_fixf10'
KINDS = ('v', 'w', 'r1', 'hb')
LEVEL = {'v': SKY, 'w': SKY, 'r1': SKY, 'hb': HB}
VIDEO_KINDS = ('v', 'r1', 'hb')
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d+) enabled=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
RX_FS = re.compile(rb'FixSval: mode=(\d+) ubo_std_layout=(\d+)')
RX_ST = re.compile(rb'FixSvalStat: validated=(\d+) rejected=(\d+)')
RX_HASH = re.compile(rb'hash=0x([0-9a-fA-F]+)')
M_START = b'GuestOut: Level has started: '
M_FAIL = b'SPIR-V validation failed'
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
K2_US = 1000000
VIDEO_MIN = 3000
HOLD_MIN_US = 300000000


def kind_of(tag):
    for k in KINDS:
        if tag == 'fs5_' + k:
            return k
    raise SystemExit('unknown tag: %s' % tag)


def paths(tag, kind, base=None):
    names = ('installed_sha', 'installed_before', 'installed_after', 'cold', 'manifest_cmp', 'manifest_cmp_ref', 'glitch', 'sheet')
    if base is not None:
        p = dict((n, os.path.join(base, n + '.txt')) for n in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((n, os.path.join(d, n + '.txt')) for n in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag) if kind in VIDEO_KINDS else None)
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
    r = dict(lines=0, rev=[], stc=[], precache_first=None, fs=[], st=[], fail=[], fail_hashes=[], guest_first=None, entry_line=None,
             scene_change_line=None, first_scene_n=None, hold_us=0, k2_after=0, dt_max_after=0, ft_rows=0, death=[], vke=0, vkw=0,
             vk_limit=0, dual=[], skipped_draw=0, win={}, recovering=0, gamepatch=0)
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
            if r['precache_first'] is None and b'PipelinePrecache: ' in raw:
                r['precache_first'] = raw[raw.index(b'PipelinePrecache: '):].strip()[:200].decode('ascii', 'replace')
            if b'FixSvalStat:' in raw:
                m = RX_ST.search(raw)
                if m:
                    r['st'].append((ln, int(m.group(1)), int(m.group(2))))
            elif b'FixSval:' in raw:
                m = RX_FS.search(raw)
                if m:
                    r['fs'].append((ln, int(m.group(1)), int(m.group(2))))
            if M_FAIL in raw:
                r['fail'].append(ln)
                mh = RX_HASH.search(raw)
                if mh:
                    hx = mh.group(1).decode().lower()
                    if hx not in r['fail_hashes']:
                        r['fail_hashes'].append(hx)
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
        return None, 0, [], [], None
    death, fail, rev, hashes = [], 0, [], []
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for i, raw in enumerate(f, 1):
            h.update(raw)
            if M_FAIL in raw:
                fail += 1
                mh = RX_HASH.search(raw)
                if mh:
                    hx = mh.group(1).decode().lower()
                    if hx not in hashes:
                        hashes.append(hx)
            rv = rev_text(raw)
            if rv is not None and len(rev) < 20:
                rev.append(('stdout', i, rv))
            for d in DEATH:
                if d in raw:
                    death.append(('stdout', d.decode(), i))
    return death, fail, rev, hashes, h.hexdigest()


def process_end(run):
    if run is None:
        return None, 'run record MISSING'
    att = (run.get('attempts') or [{}])[0]
    ended = att.get('outcome') == 'exited' or att.get('hold_exit') is not None
    return ended, 'outcome %s detail %s hold_exit %s hold_s %s stable_s %s' % (att.get('outcome'), att.get('detail'), att.get('hold_exit'),
                                                                           att.get('hold_s'), att.get('stable_s'))


def first_line(t):
    return (t or '').split('\n')[0].strip()


def read(p, kind):
    r = scan(p['log'], LEVEL[kind])
    sd, sfail, srev, shashes, ssha = stdout_scan(p['stdout'])
    rj = text(p['run'])
    run = json.loads(rj) if rj else None
    ended, end_info = process_end(run)
    sha = first_line(text(p['installed_sha'])) or None
    sha_b = first_line(text(p['installed_before'])) or None
    sha_a = first_line(text(p['installed_after'])) or None
    cold_t = text(p['cold'])
    mc = text(p['manifest_cmp'])
    mr = text(p['manifest_cmp_ref'])
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
    fixf10_ok = len(stc) >= 1 and all(s.replace('/', '\\').endswith('\\' + DIR_FIX) for s in stc)
    pf = r['precache_first']
    cold_ok = (bool(cold_t) and 'absent' in cold_t and pf is not None and pf.startswith('PipelinePrecache: no ')
               and pf.endswith(' yet') and DIR_FIX in pf)
    fs_ok = (len(r['fs']) >= 1 and all(m == 1 and u == 1 for _, m, u in r['fs'])
             and (r['guest_first'] is None or r['fs'][0][0] < r['guest_first']))
    last_st = r['st'][-1] if r['st'] else None
    rev = r['rev'] + srev
    if not rev:
        rev_row = 'NOT_PRESENT'
    else:
        rev_row = 'YES' if all(REV in t for _, _, t in rev) else 'NO'
    hashes = list(r['fail_hashes'])
    for hx in shashes:
        if hx not in hashes:
            hashes.append(hx)
    death = r['death'] + (sd or [])
    res = dict(kind=kind, level=LEVEL[kind], log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'], stdout_sha256=ssha, rev=rev[:6],
               rev_row=rev_row, stc=stc, fixf10_ok=fixf10_ok, precache_first=pf, cold_txt=(cold_t or '').strip()[:200], cold_ok=cold_ok,
               installed_sha=sha, installed_before=sha_b, installed_after=sha_a,
               sha_ok=sha == BIN_EXPECT, before_ok=sha_b == WANT, after_ok=sha_a == WANT,
               fs=r['fs'][:3], fs_ok=fs_ok, st_lines=len(r['st']), st_last=last_st,
               fail_log=len(r['fail']), fail_first=r['fail'][:3], fail_stdout=sfail, fail_hashes=hashes[:20],
               ended=ended, end_info=end_info, guest_first=r['guest_first'], entry_line=r['entry_line'],
               scene_change_line=r['scene_change_line'], first_scene_n=r['first_scene_n'], hold_us=r['hold_us'],
               hold_s=round(r['hold_us'] / 1e6, 1), k2_after=r['k2_after'], dt_max_after=r['dt_max_after'], ft_rows=r['ft_rows'],
               death=death, stdout_present=sd is not None, vke=r['vke'], vkw=r['vkw'], vk_limit=r['vk_limit'], dual=r['dual'][:2],
               dual_ok=any(s == 1 and e == 1 and (r['guest_first'] is None or ln < r['guest_first']) for ln, s, e in r['dual']),
               skipped_draw=r['skipped_draw'], win=r['win'], recovering=r['recovering'], gamepatch=r['gamepatch'],
               idx_records=idx_n, glitches=gl, sheet=sheet,
               manifest=first_line(mc)[:200], manifest_ok=bool(mc) and mc.startswith('manifest cmp EQUAL'),
               manifest_ref=first_line(mr)[:200], manifest_ref_ok=bool(mr) and mr.startswith('manifest cmp EQUAL'))
    return res


def yn(v):
    if v is None:
        return 'NOT_READ'
    if isinstance(v, str):
        return v
    return 'YES' if v else 'NO'


def rows(tag, res):
    k = res['kind']
    out = ['FS5C %s kind %s level %s log sha256 %s lines %d stdout sha256 %s' % (tag, k, res['level'], res['log_sha256'], res['log_lines'],
                                                                              res['stdout_sha256'])]
    add = out.append
    if k == 'hb':
        add('  kind hb: REFERENCE, not a gate (item 410 (g)(3))')
    add('  binary: tag %s (expected %s); installed before %s after %s (expected %s); revision texts %s'
        % (res['installed_sha'], BIN_EXPECT, res['installed_before'], res['installed_after'], WANT, res['rev']))
    add('  Shader translation cache lines %s; first PipelinePrecache line %r; form: %s' % (res['stc'][:3], res['precache_first'],
                                                                                          res['cold_txt']))
    add('  FixSval lines %s (first GuestOut line %s); FixSvalStat lines %d, last %s' % (res['fs'], res['guest_first'], res['st_lines'],
                                                                                       res['st_last']))
    add('  SPIR-V validation failed: log lines %d (first %s), stdout lines %d, hashes %s'
        % (res['fail_log'], res['fail_first'], res['fail_stdout'], res['fail_hashes']))
    add('  process end before the timeout: %s (%s)' % (yn(res['ended']), asc(res['end_info'])))
    add('  entry line %s; scene change line %s; first scene frame n %s; hold (sum dt after it) %.1f s; frames >= 1 s after it %d '
        '(max dt_us %d)' % (res['entry_line'], res['scene_change_line'], res['first_scene_n'], res['hold_s'], res['k2_after'],
                            res['dt_max_after']))
    add('  death markers: %d %s; emulator stdout %s' % (len(res['death']), res['death'][:3], 'present' if res['stdout_present'] else 'MISSING'))
    add('  window: %s, Recovering Vulkan swapchain %d; GamePatch lines %d; AsyncPipelines: skipped draw %d (reference)'
        % (res['win'] or 'none', res['recovering'], res['gamepatch'], res['skipped_draw']))
    if k in VIDEO_KINDS:
        add('  video: index records %s; one-frame glitches %s; %s' % (res['idx_records'], res['glitches'], res['sheet']))
    add('  W: [Vulkan][E] %d; [Vulkan][W] %d; last-time-reporting lines %d; DualSrcBlend %s' % (res['vke'], res['vkw'], res['vk_limit'],
                                                                                             res['dual']))
    add('  manifest: %s; vs the reference of the first tag: %s' % (res['manifest'], res['manifest_ref']))
    nfail = res['fail_log'] + res['fail_stdout']
    m = [('binary sha256 of the tag = 631ff987 (FS5 copy)', res['sha_ok']),
         ('installed 31cbfee8 before the tag', res['before_ok']),
         ('installed 31cbfee8 after the return', res['after_ok']),
         ('revision text names 0e72bc1 (reference)', res['rev_row']),
         ('translation cache directory %s in every line (member)' % DIR_FIX, res['fixf10_ok']),
         ('cold form: %s absent before the start, PipelinePrecache: no ... yet (reference)' % DIR_FIX, res['cold_ok']),
         ('entered (entry line of %s)' % res['level'], res['entry_line'] is not None),
         ('hold >= 300 s (sum dt after the first scene frame)', res['hold_us'] >= HOLD_MIN_US),
         ('no process end before the timeout', None if res['ended'] is None else res['ended'] is False),
         ('frames >= 1 s after the first scene frame = %d (REPORT, not a gate - cold entry)' % res['k2_after'],
          res['entry_line'] is not None and res['k2_after'] == 0)]
    if k == 'r1':
        m.append(('R1: FixSval mode=1 ubo_std_layout=1 before the first GuestOut (member)', res['fs_ok']))
        m.append(('R1: 0 lines SPIR-V validation failed (member)', nfail == 0))
        m.append(('R1: FixSvalStat line present (reference)', res['st_lines'] >= 1))
    else:
        m.append(('FixSval mode=1 ubo_std_layout=1 before the first GuestOut (reference)', res['fs_ok']))
        m.append(('0 lines SPIR-V validation failed (reference)', nfail == 0))
    if k in VIDEO_KINDS:
        m.append(('0 death markers', not res['death']))
        m.append(('video index records >= 3000', (res['idx_records'] or 0) >= VIDEO_MIN))
        m.append(('0 one-frame glitches', None if res['glitches'] is None else res['glitches'] == 0))
        m.append(('sheet for the lead made', res['sheet'] is not None))
    if k == 'w':
        m.append(('0 [Vulkan][E]', res['vke'] == 0))
        m.append(('positive control of the layer, [Vulkan][W] > 0', res['vkw'] > 0))
        m.append(('DualSrcBlend supported=1 enabled=1 before the first GuestOut', res['dual_ok']))
        m.append(('0 death markers (reference)', not res['death']))
    m.append(('manifest of the caches before = after the return', res['manifest_ok']))
    m.append(('manifest after the return = reference of the first tag (RC6)', res['manifest_ref_ok']))
    m.append(('no interference: window minimized / Recovering Vulkan swapchain / GamePatch line (else not read as an outcome, question '
              'to the lead)', not res['win'].get('minimized') and not res['recovering'] and not res['gamepatch']))
    for name, val in m:
        add('  ROW %s: %s' % (name, yn(val)))
    return out


def main(argv):
    if '--dir' in argv:
        base = argv[argv.index('--dir') + 1]
        kind = argv[argv.index('--tag-kind') + 1]
        if kind not in KINDS:
            raise SystemExit('unknown kind: %s' % kind)
        tag = 'fixture'
        p = paths(tag, kind, base)
    else:
        tag = argv[0]
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
