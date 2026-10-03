"""Track F link F12f (HPP-480; ROADMAP s122 item 391 (g)(4)-(5), item 393 (v)): the reader of one tag of F12f.
usage: python f12f_read.py <tag> [--json <out.json>]            tags f12_rd, f12_v, f12_w, f12_vw, f12_bh
       python f12f_read.py --dir <fixture dir> --tag-kind <rd|v|w|vw|bh>   (fixtures: log.txt, stdout.txt, es.json, rec.idx, glitch.txt,
           sheet.txt, installed_sha.txt, installed_before.txt, installed_after.txt, cold.txt, manifest_cmp.txt, manifest_cmp_ref.txt,
           rdc_sha.txt and rdcs_k*.txt for rd)
Port of C:/kyty/f287/fs4c/fs4c_read.py (FS4c HPP-472) with: the F12d copy b714f5c4 (kinds v, w, vw, bh; KYTY_FIX_F10=1) and the
installed 540c035a (kind rd, the RenderDoc capture); the row of the translation cache directory with '_fixf10' (item 393 (v): a member of
every tag v, w, vw, bh; in rd its ABSENCE is the control); no FixSval rows (not a member of F12f); the frames >= 1 s after the first scene
frame - a report row, not a gate (item 391 (g)(5): cold entry into a new directory); 'GamePatch:' lines - interference of the run
(item 342 (e)); the rd rows of the captures (RenderDoc lines of the log, captures moved, rdcs_f12f.sh summaries - DATA for F12g).
Rows only, no verdict (the verdict is F12h's).
Definitions (seal section 4):
  binary          rd: installed_sha.txt = 540c035a...; v/w/vw/bh: installed_sha.txt (written after the install) = b714f5c4...;
                  every kind: installed_before.txt and installed_after.txt = 540c035a... (the installed binary before the tag and after
                  the return).  The revision text (log / stdout 'Fork build arigandores/KytyPS5 ' or ', git = '): reference, rd 1833ee2
                  absent, the others 1833ee2 (YES / NO / NOT_PRESENT, never a gate).
  directory       every line 'Shader translation cache: <dir>'; FIXF10 row (v, w, vw, bh) = >= 1 such line and every one ends with
                  variant_fixb26_fixb1b_fixf10; rd control = >= 1 such line, none contains '_fixf10', and every one ends with
                  variant_fixb26_fixb1b.
  cold form       (v, w, vw, bh; reference) cold.txt says 'absent' (the directory variant_fixb26_fixb1b_fixf10 did not exist before the
                  start).
  entry           the first line 'GuestOut: Level has started: <level>'; first scene frame - the first FrameTrace row after it with
                  draws >= 100; hold - sum dt_us of the FrameTrace rows after the first scene frame (before a scene change); frames >= 1 s
                  - FrameTrace rows with dt_us >= 1 000 000 after the first scene frame (before a scene change): REPORT row.
  death markers   'Unhandled exception:', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort:', 'ErrorDeviceLost' in the log and in the
                  emulator stdout.
  process end     the enter_scene attempt outcome 'exited' or hold_exit not null = the process ended before the timeout.
  W rows          '[Vulkan][E]' lines = 0; '[Vulkan][W]' lines > 0 (positive control of the layer); 'DualSrcBlend: supported=1
                  enabled=1' before the first line carrying 'GuestOut' (item 295 (b)(4)).
  video           (v, vw, bh) records of the video index >= 3000; one-frame glitches of s51_vidglitch.py (glitch.txt 'one-frame
                  glitches: N') = 0; the sheet for the lead made (sheet.txt line 'sheet: ').
  manifest        manifest_cmp.txt and manifest_cmp_ref.txt first lines start with 'manifest cmp EQUAL'.
  interference    a window line 'minimized' or 'Recovering Vulkan swapchain' (item 273 (z)) or a 'GamePatch:' line - the tag is not read
                  as an outcome (interference of the run, the attempt is not spent; question to the lead).
  rd captures     'RenderDoc: level started at frame N', 'RenderDoc: auto capture at frame F (level+X)', 'RenderDoc: captured guest flip
                  2/2', 'RenderDoc: capture finished' lines; rdc_sha.txt lines (captures moved); per capture the rdcs_f12_rd_kNN.txt line
                  'SUMMARY dispatches D distinct_cs C marked_380b M marked_eids E' and its 'done' line.  Row 'captures with >= 1 dispatch
                  whose CS SPIR-V sha256 = the =0 SPIR-V of 380bb9d636390bae (F12d section 5)' - DATA for F12g (item 391 (g)(4)), no gate.
ASCII output only."""
import glob, hashlib, json, os, re, sys

G = 'C:/kyty/f287/f12f'
SKY = 'underwater_aerial_garden'
VW = 'voxel_world'
BH = 'big_hand_pirate_island'
BIN_EXPECT = 'b714f5c4af578928243c1f1028e7b2acd65b733fce90f2e3cda5b6ae46d5eb5e'
WANT = '540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1'
REV = '1833ee2'
DIR_BASE = 'variant_fixb26_fixb1b'
DIR_FIX = 'variant_fixb26_fixb1b_fixf10'
KINDS = ('rd', 'v', 'w', 'vw', 'bh')
LEVEL = {'rd': SKY, 'v': SKY, 'w': SKY, 'vw': VW, 'bh': BH}
VIDEO_KINDS = ('v', 'vw', 'bh')
FIX_KINDS = ('v', 'w', 'vw', 'bh')
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d+) enabled=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
RX_RDL = re.compile(rb'RenderDoc: level started at frame (\d+)')
RX_RDA = re.compile(rb'RenderDoc: auto capture at frame (\d+) \(level\+(\d+)\)')
RX_SUM = re.compile(r'SUMMARY dispatches (\d+) distinct_cs (\d+) marked_380b (\d+) marked_eids (\S+)')
M_START = b'GuestOut: Level has started: '
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
K2_US = 1000000
VIDEO_MIN = 3000
HOLD_MIN_US = 300000000


def kind_of(tag):
    for k in KINDS:
        if tag == 'f12_' + k:
            return k
    raise SystemExit('unknown tag: %s' % tag)


def paths(tag, kind, base=None):
    names = ('installed_sha', 'installed_before', 'installed_after', 'cold', 'manifest_cmp', 'manifest_cmp_ref', 'glitch', 'sheet', 'rdc_sha')
    if base is not None:
        p = dict((n, os.path.join(base, n + '.txt')) for n in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), rdcs=sorted(glob.glob(os.path.join(base, 'rdcs_k*.txt'))))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((n, os.path.join(d, n + '.txt')) for n in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag) if kind in VIDEO_KINDS else None,
             rdcs=sorted(glob.glob(os.path.join(G, 'rdcs_f12_rd_k*.txt'))) if kind == 'rd' else [])
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
    r = dict(lines=0, rev=[], stc=[], guest_first=None, entry_line=None, scene_change_line=None, first_scene_n=None, hold_us=0,
             k2_after=0, dt_max_after=0, ft_rows=0, death=[], vke=0, vkw=0, vk_limit=0, dual=[], skipped_draw=0, win={}, recovering=0,
             gamepatch=0, rd_level=None, rd_auto=[], rd_flip2=0, rd_finished=0)
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
            if b'RenderDoc: ' in raw:
                m = RX_RDL.search(raw)
                if m and r['rd_level'] is None:
                    r['rd_level'] = int(m.group(1))
                m = RX_RDA.search(raw)
                if m:
                    r['rd_auto'].append((int(m.group(1)), int(m.group(2))))
                if b'RenderDoc: captured guest flip 2/2' in raw:
                    r['rd_flip2'] += 1
                if b'RenderDoc: capture finished' in raw:
                    r['rd_finished'] += 1
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


def process_end(run):
    if run is None:
        return None, 'run record MISSING'
    att = (run.get('attempts') or [{}])[0]
    ended = att.get('outcome') == 'exited' or att.get('hold_exit') is not None
    return ended, 'outcome %s detail %s hold_exit %s hold_s %s stable_s %s' % (att.get('outcome'), att.get('detail'), att.get('hold_exit'),
                                                                           att.get('hold_s'), att.get('stable_s'))


def first_line(t):
    return (t or '').split('\n')[0].strip()


def rdcs_read(files):
    out = []
    for p in files:
        t = text(p) or ''
        m = RX_SUM.search(t)
        done = any(x.strip() == 'done' for x in t.split('\n'))
        out.append(dict(file=os.path.basename(p), done=done, dispatches=int(m.group(1)) if m else None,
                        distinct=int(m.group(2)) if m else None, marked=int(m.group(3)) if m else None,
                        eids=m.group(4) if m else None))
    return out


def read(p, kind):
    r = scan(p['log'], LEVEL[kind])
    sd, srev, ssha = stdout_scan(p['stdout'])
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
    rd_ctrl_ok = (len(stc) >= 1 and not any('_fixf10' in s for s in stc)
                  and all(s.replace('/', '\\').endswith('\\' + DIR_BASE) for s in stc))
    cold_ok = bool(cold_t) and 'absent' in cold_t
    rev = r['rev'] + srev
    want_rev = REV if kind in FIX_KINDS else None
    if not rev:
        rev_row = 'NOT_PRESENT'
    elif want_rev:
        rev_row = 'YES' if all(want_rev in t for _, _, t in rev) else 'NO'
    else:
        rev_row = 'YES' if not any(REV in t for _, _, t in rev) else 'NO'
    rdc_t = text(p['rdc_sha'])
    rdc_n = len([x for x in (rdc_t or '').split('\n') if x.strip()]) if rdc_t is not None else None
    rdcs = rdcs_read(p.get('rdcs') or [])
    death = r['death'] + (sd or [])
    res = dict(kind=kind, level=LEVEL[kind], log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'], stdout_sha256=ssha, rev=rev[:6],
               rev_row=rev_row, stc=stc, fixf10_ok=fixf10_ok, rd_ctrl_ok=rd_ctrl_ok, cold_txt=(cold_t or '').strip()[:200],
               cold_ok=cold_ok, installed_sha=sha, installed_before=sha_b, installed_after=sha_a,
               sha_ok=sha == (WANT if kind == 'rd' else BIN_EXPECT), before_ok=sha_b == WANT, after_ok=sha_a == WANT,
               ended=ended, end_info=end_info, guest_first=r['guest_first'], entry_line=r['entry_line'],
               scene_change_line=r['scene_change_line'], first_scene_n=r['first_scene_n'], hold_us=r['hold_us'],
               hold_s=round(r['hold_us'] / 1e6, 1), k2_after=r['k2_after'], dt_max_after=r['dt_max_after'], ft_rows=r['ft_rows'],
               death=death, stdout_present=sd is not None, vke=r['vke'], vkw=r['vkw'], vk_limit=r['vk_limit'], dual=r['dual'][:2],
               dual_ok=any(s == 1 and e == 1 and (r['guest_first'] is None or ln < r['guest_first']) for ln, s, e in r['dual']),
               skipped_draw=r['skipped_draw'], win=r['win'], recovering=r['recovering'], gamepatch=r['gamepatch'],
               idx_records=idx_n, glitches=gl, sheet=sheet,
               manifest=first_line(mc)[:200], manifest_ok=bool(mc) and mc.startswith('manifest cmp EQUAL'),
               manifest_ref=first_line(mr)[:200], manifest_ref_ok=bool(mr) and mr.startswith('manifest cmp EQUAL'),
               rd_level=r['rd_level'], rd_auto=r['rd_auto'], rd_flip2=r['rd_flip2'], rd_finished=r['rd_finished'], rdc_n=rdc_n, rdcs=rdcs)
    return res


def yn(v):
    if v is None:
        return 'NOT_READ'
    if isinstance(v, str):
        return v
    return 'YES' if v else 'NO'


def rows(tag, res):
    k = res['kind']
    out = ['F12F %s kind %s level %s log sha256 %s lines %d stdout sha256 %s' % (tag, k, res['level'], res['log_sha256'], res['log_lines'],
                                                                              res['stdout_sha256'])]
    add = out.append
    add('  binary: tag %s (expected %s); installed before %s after %s; revision texts %s'
        % (res['installed_sha'], WANT if k == 'rd' else BIN_EXPECT, res['installed_before'], res['installed_after'], res['rev']))
    add('  Shader translation cache lines %s; form: %s' % (res['stc'][:3], res['cold_txt']))
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
    if k == 'rd':
        add('  RenderDoc: level started at frame %s; auto captures (frame, level+X) %s; captured flip 2/2 %d; capture finished %d; '
            'captures moved %s' % (res['rd_level'], res['rd_auto'], res['rd_flip2'], res['rd_finished'], res['rdc_n']))
        for c in res['rdcs']:
            add('  rdcs %s: done %s dispatches %s distinct CS %s marked_380b %s eids %s'
                % (c['file'], yn(c['done']), c['dispatches'], c['distinct'], c['marked'], c['eids']))
    m = [('binary sha256 of the tag = %s' % ('540c035a (installed, no fix)' if k == 'rd' else 'b714f5c4 (F12d copy)'), res['sha_ok']),
         ('installed 540c035a before the tag', res['before_ok']),
         ('installed 540c035a after the return', res['after_ok']),
         ('revision text %s (reference)' % ('without 1833ee2' if k == 'rd' else 'names 1833ee2'), res['rev_row'])]
    if k == 'rd':
        m.append(('control: translation cache line(s) %s, no _fixf10 (else interference)' % DIR_BASE, res['rd_ctrl_ok']))
        m.append(('entered (entry line of %s)' % SKY, res['entry_line'] is not None))
        m.append(('>= 1 capture made and moved (data)', bool(res['rdc_n'])))
        m.append(('every capture read by rdcs (done line)', bool(res['rdcs']) and all(c['done'] for c in res['rdcs'])
                  and len(res['rdcs']) == (res['rdc_n'] or 0)))
        nm = sum(1 for c in res['rdcs'] if (c['marked'] or 0) > 0)
        m.append(('captures with >= 1 dispatch of 380bb9d6 by SPIR-V sha (DATA for F12g, no gate): %d of %d' % (nm, len(res['rdcs'])),
                  nm >= 1))
        m.append(('0 death markers (data)', not res['death']))
    else:
        m.append(('translation cache directory %s in every line (member, item 393 (v))' % DIR_FIX, res['fixf10_ok']))
        m.append(('cold form: %s absent before the start (reference)' % DIR_FIX, res['cold_ok']))
        m.append(('entered (entry line of %s)' % res['level'], res['entry_line'] is not None))
        m.append(('hold >= 300 s (sum dt after the first scene frame)', res['hold_us'] >= HOLD_MIN_US))
        m.append(('no process end before the timeout', None if res['ended'] is None else res['ended'] is False))
        m.append(('frames >= 1 s after the first scene frame = %d (REPORT, not a gate - cold entry)' % res['k2_after'],
                  res['entry_line'] is not None and res['k2_after'] == 0))
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
