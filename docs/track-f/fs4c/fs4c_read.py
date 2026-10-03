"""FS4c (HPP-472, ROADMAP s122 item 378 (g)(3); item 383 (c) = Z2 of FS4b): the reader of one tag of the FS4 binary 31cbfee8.
usage: python fs4c_read.py <tag> [--json <out.json>]            tags fs4_r0, fs4_r1, fs4_hb, fs4_w, fs4_v
       python fs4c_read.py --dir <fixture dir> --tag-kind <r0|r1|hb|w|v>   (fixtures: log.txt, stdout.txt, run.json | es.json, rec.idx,
                                                                         glitch.txt, sheet.txt, installed_sha.txt, cold.txt, manifest_cmp.txt)
Port of C:/kyty/f287/f10e/f10e_read.py (F10e HPP-453, seal docs/track-f/f10e.md section 4) with: the FS4 binary (sha256 31cbfee8...);
the kinds hb (hoover_beach of the R1 form, reference - not a gate of the install), w (W of item 295 (b): the harness
--shader-validation false, WARM cache, FixSval mode=1) and v (V of the SCENE_OK form, WARM cache); no KYTY_FIX_SVAL in r1 / hb / w / v
(the default of FS4 is the mode=1 row); the revision text of KYTY_GIT_REVISION in the log / stdout, where present, as a row (lead
comment 64e6a50c, Z1: the SDL_REVISION string of the binary names 92d11340 and is not read).  Reads (streaming, binary) the emulator
log of the tag (runs/<tag>/log.txt for r0; log_<tag>.txt of enter_scene for the others), its stdout, the run record (run.json of
run_fs4c.py for r0; <tag>.json of enter_scene for the others), the video index and the glitch / sheet outputs of post_fs4c.sh (r1, hb, v),
the files installed_sha.txt, cold.txt, manifest_cmp.txt of go_fs4c.sh, and prints the rows of the seal (docs/track-f/fs4c.md section 4).
Rows only, no verdict (the verdict is the lead's, FS4d).
Definitions (seal section 4):
  binary          the sha256 written by go_fs4c.sh after the install (installed_sha.txt) = 31cbfee8... (the binary is known ONLY by this
                  sha); the revision text: every log / stdout line carrying 'Fork build arigandores/KytyPS5 ' or ', git = ' - the row is YES
                  if >= 1 such text and all name 3d0e46d, NO if one names another revision, NOT_PRESENT if none (reference, not a gate).
  cold form       (r0, r1, hb) cold.txt says the variant dir was absent before the start AND the log line 'Shader translation cache: ' names
                  variant_fixb26_fixb1b AND the first 'PipelinePrecache:' line is 'PipelinePrecache: no ... yet'.
  warm form       (w, v) cold.txt says 'warm form' and 'present' AND the translation cache line names variant_fixb26_fixb1b AND the first
                  'PipelinePrecache:' line is NOT 'PipelinePrecache: no ...' (recipes replayed from the warm variant dir).
  FixSval line    'FixSval: mode=M ubo_std_layout=U'; the row wants >= 1 such line, all with the expected M (r0: 0, the others: 1 - the
                  default of FS4) and U=1, the first one before the first line carrying 'GuestOut'.
  FixSvalStat     'FixSvalStat: validated=N rejected=R' (only at mode=1 with --shader-validation true, every 256th check); validated =
                  number of ALL checks of ValidateShaderSpirv (all stages).  r1 gate 'validated >= 151': YES if the last line has N >= 151;
                  NO if N < 151; NOT_DETERMINED if there is no such line.  hb: the same value, reference.
  validation failed  lines containing 'SPIR-V validation failed' in the log and in the stdout, and the distinct hashes 'hash=0x...'.
  process end     r0: run.json how starts with 'exit rc' (the process ended before 300 s), rc and exit_s printed; the others: the
                  enter_scene attempt outcome 'exited' or hold_exit not null = the process ended before the timeout.
  entry           the first line 'GuestOut: Level has started: <level of the kind>'; first scene frame - the first FrameTrace row after it
                  with draws >= 100; hold - sum dt_us of the FrameTrace rows after the first scene frame (before a scene change); frames
                  >= 1 s - FrameTrace rows with dt_us >= 1 000 000 after the first scene frame (before a scene change): gate of v, reference
                  of the others.
  death markers   'Unhandled exception:', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort:', 'ErrorDeviceLost' in the log and in the
                  emulator stdout.
  W rows          '[Vulkan][E]' lines; positive control of the layer - '[Vulkan][W]' lines > 0; 'last time reporting it' lines;
                  'DualSrcBlend: supported=1 enabled=1' before the first line carrying 'GuestOut' (item 295 (b)(4)).
  video           r1, hb, v: records of the video index >= 3000; one-frame glitches of s51_vidglitch.py (glitch.txt line 'one-frame
                  glitches: N') = 0; the sheet for the lead made (sheet.txt line 'sheet: ').
  manifest        manifest_cmp.txt first line starts with 'manifest cmp EQUAL'.
ASCII output only."""
import hashlib, json, os, re, sys

G = 'C:/kyty/f287/fs4c'
SKY = 'underwater_aerial_garden'
HB = 'hoover_beach'
BIN_EXPECT = '31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5'
REV = '3d0e46d'
VARIANT = b'variant_fixb26_fixb1b'
KINDS = ('r0', 'r1', 'hb', 'w', 'v')
MODE = {'r0': 0, 'r1': 1, 'hb': 1, 'w': 1, 'v': 1}
LEVEL = {'r0': SKY, 'r1': SKY, 'hb': HB, 'w': SKY, 'v': SKY}
COLD_KINDS = ('r0', 'r1', 'hb')
VIDEO_KINDS = ('r1', 'hb', 'v')
RX_FS = re.compile(rb'FixSval: mode=(\d+) ubo_std_layout=(\d+)')
RX_ST = re.compile(rb'FixSvalStat: validated=(\d+) rejected=(\d+)')
RX_HASH = re.compile(rb'hash=0x([0-9a-fA-F]+)')
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d+) enabled=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
M_START = b'GuestOut: Level has started: '
M_FAIL = b'SPIR-V validation failed'
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
K2_US = 1000000
VIDEO_MIN = 3000
VALIDATED_MIN = 151
HOLD_MIN_US = 300000000


def kind_of(tag):
    if tag == 'fs4_r0r':   # the one repeat of fs4_r0 (item 378 (g)(3): no rejection - one repeat)
        return 'r0'
    for k in KINDS:
        if tag == 'fs4_' + k:
            return k
    raise SystemExit('unknown tag: %s' % tag)


def paths(tag, kind, base=None):
    if base is not None:
        j = os.path.join(base, 'run.json' if kind == 'r0' else 'es.json')
        return dict(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=j,
                    idx=os.path.join(base, 'rec.idx'), glitch=os.path.join(base, 'glitch.txt'), sheet=os.path.join(base, 'sheet.txt'),
                    sha=os.path.join(base, 'installed_sha.txt'), cold=os.path.join(base, 'cold.txt'),
                    mcmp=os.path.join(base, 'manifest_cmp.txt'))
    d = os.path.join(G, 'runs', tag)
    p = dict(sha=os.path.join(d, 'installed_sha.txt'), cold=os.path.join(d, 'cold.txt'), mcmp=os.path.join(d, 'manifest_cmp.txt'),
             glitch=os.path.join(d, 'glitch.txt'), sheet=os.path.join(d, 'sheet.txt'))
    if kind == 'r0':
        p.update(log=os.path.join(d, 'log.txt'), stdout=os.path.join(d, 'stdout.txt'), run=os.path.join(d, 'run.json'), idx=None)
    else:
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
    """the revision text of one line (the text after 'Fork build arigandores/KytyPS5 ' or ', git = '), or None."""
    for m in (M_FORK, M_GIT):
        if m in raw:
            return raw.split(m, 1)[1].split(b',', 1)[0].strip()[:80].decode('ascii', 'replace')
    return None


def scan(log_path, level):
    r = dict(lines=0, rev=[], stc=[], precache_first=None, fs=[], st=[], fail=[], fail_hashes=[], guest_first=None, entry_line=None,
             scene_change_line=None, first_scene_n=None, hold_us=0, k2_after=0, dt_max_after=0, ft_rows=0, death=[], vke=0, vkw=0,
             vk_limit=0, dual=[], skipped_draw=0, win={}, recovering=0)
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


def process_end(kind, run):
    """(ended, info): r0 - run.json of run_fs4c.py; the others - the first attempt of enter_scene."""
    if run is None:
        return None, 'run record MISSING'
    if kind == 'r0':
        how = run.get('how', '')
        return how.startswith('exit rc'), 'how %r rc %s exit_s %s wall_s %s' % (how, run.get('rc'), run.get('exit_s'), run.get('wall_s'))
    att = (run.get('attempts') or [{}])[0]
    ended = att.get('outcome') == 'exited' or att.get('hold_exit') is not None
    return ended, 'outcome %s detail %s hold_exit %s hold_s %s stable_s %s' % (att.get('outcome'), att.get('detail'), att.get('hold_exit'),
                                                                           att.get('hold_s'), att.get('stable_s'))


def read(p, kind):
    r = scan(p['log'], LEVEL[kind])
    sd, sfail, srev, shashes, ssha = stdout_scan(p['stdout'])
    rj = text(p['run'])
    run = json.loads(rj) if rj else None
    ended, end_info = process_end(kind, run)
    sha_t = text(p['sha'])
    sha = sha_t.strip() if sha_t else None
    cold_t = text(p['cold'])
    mc = text(p['mcmp'])
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
    fs_ok = (len(r['fs']) >= 1 and all(m == MODE[kind] and u == 1 for _, m, u in r['fs'])
             and (r['guest_first'] is None or r['fs'][0][0] < r['guest_first']))
    last_st = r['st'][-1] if r['st'] else None
    if last_st is None:
        validated = 'NOT_DETERMINED'
    else:
        validated = 'YES' if last_st[1] >= VALIDATED_MIN else 'NO'
    stc_ok = any(VARIANT.decode() in s for s in r['stc'])
    pf = r['precache_first']
    cold_ok = (bool(cold_t) and 'absent' in cold_t and stc_ok and pf is not None and pf.startswith('PipelinePrecache: no ')
               and pf.endswith(' yet'))
    warm_ok = (bool(cold_t) and 'warm form' in cold_t and 'present' in cold_t and stc_ok and pf is not None
               and not pf.startswith('PipelinePrecache: no '))
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
               rev_row=rev_row, stc=r['stc'], precache_first=pf, cold_txt=(cold_t or '').strip()[:200], cold_ok=cold_ok, warm_ok=warm_ok,
               installed_sha=sha, sha_ok=sha == BIN_EXPECT, fs=r['fs'], fs_ok=fs_ok, st_lines=len(r['st']), st_last=last_st,
               validated=validated, fail_log=len(r['fail']), fail_first=r['fail'][:3], fail_hashes=hashes[:20],
               fail_stdout=sfail, ended=ended, end_info=end_info, guest_first=r['guest_first'], entry_line=r['entry_line'],
               scene_change_line=r['scene_change_line'], first_scene_n=r['first_scene_n'], hold_us=r['hold_us'],
               hold_s=round(r['hold_us'] / 1e6, 1), k2_after=r['k2_after'], dt_max_after=r['dt_max_after'], ft_rows=r['ft_rows'],
               death=death, stdout_present=sd is not None, vke=r['vke'], vkw=r['vkw'], vk_limit=r['vk_limit'], dual=r['dual'][:2],
               dual_ok=any(s == 1 and e == 1 and (r['guest_first'] is None or ln < r['guest_first']) for ln, s, e in r['dual']),
               skipped_draw=r['skipped_draw'], win=r['win'], recovering=r['recovering'], idx_records=idx_n, glitches=gl,
               sheet=sheet, manifest=(mc or '').split('\n')[0].strip()[:200],
               manifest_ok=bool(mc) and mc.startswith('manifest cmp EQUAL'))
    return res


def yn(v):
    if v is None:
        return 'NOT_READ'
    if isinstance(v, str):
        return v
    return 'YES' if v else 'NO'


def video_rows(res, pfx):
    return [('%s: video index records >= 3000' % pfx, (res['idx_records'] or 0) >= VIDEO_MIN),
            ('%s: 0 one-frame glitches' % pfx, None if res['glitches'] is None else res['glitches'] == 0),
            ('%s: sheet for the lead made' % pfx, res['sheet'] is not None)]


def rows(tag, res):
    k = res['kind']
    out = ['FS4C %s kind %s level %s log sha256 %s lines %d stdout sha256 %s' % (tag, k, res['level'], res['log_sha256'], res['log_lines'],
                                                                              res['stdout_sha256'])]
    add = out.append
    add('  binary: installed sha256 %s (expected %s); revision texts %s' % (res['installed_sha'], BIN_EXPECT, res['rev']))
    add('  %s: %s; Shader translation cache %s; first PipelinePrecache line %r'
        % ('cold' if k in COLD_KINDS else 'warm', res['cold_txt'], res['stc'][:2], res['precache_first']))
    add('  FixSval lines %s (expected mode=%d ubo_std_layout=1, first before the first GuestOut line %s)'
        % (res['fs'][:3], MODE[k], res['guest_first']))
    add('  FixSvalStat lines %d, last %s (validated = ALL checks of ValidateShaderSpirv, all stages)' % (res['st_lines'], res['st_last']))
    add('  SPIR-V validation failed: log lines %d (first %s), stdout lines %d, hashes %s'
        % (res['fail_log'], res['fail_first'], res['fail_stdout'], res['fail_hashes']))
    add('  process end before the timeout: %s (%s)' % (yn(res['ended']), asc(res['end_info'])))
    add('  entry line %s; scene change line %s; first scene frame n %s; hold (sum dt after it) %.1f s; frames >= 1 s after it %d '
        '(max dt_us %d)' % (res['entry_line'], res['scene_change_line'], res['first_scene_n'], res['hold_s'], res['k2_after'],
                            res['dt_max_after']))
    add('  death markers: %d %s; emulator stdout %s' % (len(res['death']), res['death'][:3], 'present' if res['stdout_present'] else 'MISSING'))
    add('  window: %s, Recovering Vulkan swapchain %d; AsyncPipelines: skipped draw %d (reference)'
        % (res['win'] or 'none', res['recovering'], res['skipped_draw']))
    add('  video: index records %s; one-frame glitches %s; %s' % (res['idx_records'], res['glitches'], res['sheet']))
    add('  W: [Vulkan][E] %d; [Vulkan][W] %d; last-time-reporting lines %d; DualSrcBlend %s, supported=1 enabled=1 before the first '
        'GuestOut: %s' % (res['vke'], res['vkw'], res['vk_limit'], res['dual'], res['dual_ok']))
    add('  manifest: %s' % res['manifest'])
    m = [('binary sha256 = 31cbfee8', res['sha_ok']),
         ('revision text names 3d0e46d (KYTY_GIT_REVISION; NOT_PRESENT - no such text; reference)', res['rev_row'])]
    if k in COLD_KINDS:
        m.append(('cold form (variant dir absent, translation cache path, PipelinePrecache: no ... yet)', res['cold_ok']))
    else:
        m.append(('warm form (variant dir present, translation cache path, PipelinePrecache replayed)', res['warm_ok']))
    m.append(('FixSval mode=%d ubo_std_layout=1 before the first GuestOut' % MODE[k], res['fs_ok']))
    nfail = res['fail_log'] + res['fail_stdout']
    if k == 'r0':
        m.append(('R0: >= 1 line SPIR-V validation failed', nfail >= 1))
        m.append(('R0: the process ended before 300 s', res['ended']))
        m.append(('R0: 0 FixSvalStat lines at =0 (reference)', res['st_lines'] == 0))
        m.append(('R0: defect reproduced in the game (both rows above; else - not reproduced in the game)', nfail >= 1 and bool(res['ended'])))
    if k == 'r1':
        m.append(('R1: 0 lines SPIR-V validation failed', nfail == 0))
        m.append(('R1: no process end before the timeout', res['ended'] is False))
        m.append(('R1: 0 death markers', not res['death']))
        m.append(('R1: validated of the last FixSvalStat >= 151 (no line - NOT_DETERMINED)', res['validated']))
        m.append(('R1: entered (entry line of %s)' % SKY, res['entry_line'] is not None))
        m.append(('R1: hold >= 300 s (sum dt after the first scene frame)', res['hold_us'] >= HOLD_MIN_US))
        m += video_rows(res, 'R1')
    if k == 'hb':
        m.append(('HB (reference): 0 lines SPIR-V validation failed', nfail == 0))
        m.append(('HB (reference): no process end before the timeout', res['ended'] is False))
        m.append(('HB (reference): 0 death markers', not res['death']))
        m.append(('HB (reference): validated of the last FixSvalStat >= 151 (no line - NOT_DETERMINED)', res['validated']))
        m.append(('HB (reference): entered (entry line of %s)' % HB, res['entry_line'] is not None))
        m.append(('HB (reference): hold >= 300 s (sum dt after the first scene frame)', res['hold_us'] >= HOLD_MIN_US))
        m += video_rows(res, 'HB (reference)')
    if k == 'w':
        m.append(('W: entered (entry line of %s)' % SKY, res['entry_line'] is not None))
        m.append(('W: hold >= 300 s (sum dt after the first scene frame)', res['hold_us'] >= HOLD_MIN_US))
        m.append(('W: 0 [Vulkan][E]', res['vke'] == 0))
        m.append(('W: positive control of the layer, [Vulkan][W] > 0', res['vkw'] > 0))
        m.append(('W: DualSrcBlend supported=1 enabled=1 before the first GuestOut', res['dual_ok']))
        m.append(('W: 0 lines SPIR-V validation failed (reference)', nfail == 0))
        m.append(('W: no process end before the timeout (reference)', res['ended'] is False))
        m.append(('W: 0 death markers (reference)', not res['death']))
    if k == 'v':
        m.append(('V: entered (entry line of %s)' % SKY, res['entry_line'] is not None))
        m.append(('V: hold >= 300 s (sum dt after the first scene frame)', res['hold_us'] >= HOLD_MIN_US))
        m.append(('V: 0 death markers', not res['death']))
        m.append(('V: 0 frames >= 1 s after the first scene frame', res['entry_line'] is not None and res['k2_after'] == 0))
        m.append(('V: no process end before the timeout', res['ended'] is False))
        m += video_rows(res, 'V')
    m.append(('manifest of the caches before = after the return', res['manifest_ok']))
    m.append(('no window minimized / Recovering Vulkan swapchain (else not read as an outcome, question to the lead)',
              not res['win'].get('minimized') and not res['recovering']))
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
