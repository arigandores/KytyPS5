"""FS3c (HPP-449, ROADMAP s122 item 367 (g)(3); lead line of comment 417cc2d8 = remark Z2 of FS3b): the reader of one tag.
Port of C:/kyty/f287/f9/f9g/f9g_read.py (F9g, HPP-424) with the line 'FixB42Ext:' of FS3a and the tag set of item 367 (g)(3).
usage: python fs3_read.py <tag> [--json <out.json>]      python fs3_read.py --log <log.txt> --tag-kind <u|u0|pu|w|v|hb> (fixtures)
Reads (streaming, binary) the emulator log of the tag (runs/<tag>/log.txt for u/u0/pu, log_<tag>.txt of enter_scene for w/v/hb),
its stdout, the video index and prints the rows of the seal (docs/track-f/fs3c.md section 4).  Rows only, no verdict (the verdict
is the lead's, FS3d); the tile cells are counted by eye on the sheets (section 5 of the seal).
Definitions (seal section 4):
  FixB42 line    'FixB42: mode=M hit=H applied=A drawn=D rearm=R hit_all=HA last_frame=F extent=WxH cmask=0xC clear=W0/W1'
                 (item 353 (g)(3)); counters per extent; a torn line (the regex does not match) is counted apart.
  FixB42Ext line 'FixB42Ext: mode=M extent=WxH hit=H applied=A drawn=D rearm=R frame=F' (item 367 (g)(1)); written only on a call
                 with Hit, the first line of an extent at once, then not more often than once in 600 frames of the extent, <= 64
                 lines per extent; a torn line is counted apart.
  growth         of a counter of an extent: its value minus the value on the previous line of the same extent and kind (0 before
                 the first).
  present        of a log position: n of the next FrameTrace row + the offset median(present - n) over the InputScript press /
                 release lines (video frame v = present - 1); no InputScript line -> None.
  phases         by keys_a2_presents.txt (form of F9d / F9g): approach present < 3841; rotation [3841, 5851); steps [5851, 5951);
                 static >= 5951 (v >= 5950) up to the last present of the run.
  EXT reference  (fs3_u; lead line 417cc2d8): growth of applied of 960x540 in the static phase is SHOWN only if a FixB42Ext line
                 extent=960x540 with present in the phase or after it (present >= 5951) carries applied greater than the last
                 FixB42Ext extent=960x540 line before the phase (present < 5951; none -> 0); no such line -> NOT_DETERMINED (not
                 'does not grow'); a 960x540 FixB42Ext line without a present -> NOT_DETERMINED.  Executor's variant beside it: the
                 base is the largest applied of any 960x540 line (FixB42 or FixB42Ext) before the phase.
  C0 line        (fs3_u0; item 351 (g)(2) / 353 (d)(2)): >= 1 line (FixB42 or FixB42Ext) mode=0 extent=960x540 hit >= 1 applied=0.
  entry          the first line 'GuestOut: Level has started: <level>' with the level of the form; scene change - any later such line;
                 first scene frame - the first FrameTrace row after the entry with draws >= 100.
  frames >= 1 s  FrameTrace rows with dt_us >= 1 000 000 after the first scene frame (before a scene change); all rows - reference.
  death markers  'Unhandled exception:', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort:', 'ErrorDeviceLost' in the log and
                 in the emulator stdout.
  hold           sum dt_us of the FrameTrace rows after the first scene frame (before a scene change); w/v/hb: >= 300 s.
  W rows         [Vulkan][E] lines; validation active - >= 1 '[Vulkan][W][2]' or '[Vulkan][E][2]'; 'last time reporting it' lines;
                 'DualSrcBlend: supported=1 enabled=1' before the first line carrying 'GuestOut' (item 295 (b)(4)).
  GamePatch      0 lines expected except pu; pu: the lines 'GamePatch: applied', 'GamePatch: refused' counted (reference).
ASCII output only."""
import hashlib, json, os, re, statistics, sys

G = 'C:/kyty/f287/fs3/fs3c'
SKY = 'underwater_aerial_garden'
LEVEL = {'u': SKY, 'u0': SKY, 'pu': SKY, 'w': SKY, 'v': SKY, 'hb': 'hoover_beach'}
MODE = {'u': 1, 'u0': 0, 'pu': 1, 'w': 1, 'v': 1, 'hb': 1}
RX_FIX = re.compile(rb'FixB42: mode=(\d+) hit=(\d+) applied=(\d+) drawn=(\d+) rearm=(\d+) hit_all=(\d+) last_frame=(\d+) '
                    rb'extent=(\d+)x(\d+) cmask=0x([0-9a-fA-F]+) clear=([0-9a-fA-F]{8})/([0-9a-fA-F]{8})')
RX_EXT = re.compile(rb'FixB42Ext: mode=(\d+) extent=(\d+)x(\d+) hit=(\d+) applied=(\d+) drawn=(\d+) rearm=(\d+) frame=(\d+)')
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_IN = re.compile(rb'InputScript: (press|release) (\S+) at ([0-9.]+) s \(present (\d+)\)')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d+) enabled=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
M_START = b'GuestOut: Level has started: '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
K2_US = 1000000
STEPS_FROM, STATIC_FROM, APPROACH_END = 5851, 5951, 3841
T6 = (960, 540)


def kind_of(tag):
    t = tag[4:] if tag.startswith('fs3_') else tag
    for k, pre in (('u0', 'u0'), ('pu', 'pu'), ('hb', 'hb'), ('u', 'u'), ('w', 'w'), ('v', 'v')):
        if t.startswith(pre):
            return k
    raise SystemExit('unknown tag kind: %s' % tag)


def paths(tag, kind):
    if kind in ('w', 'v', 'hb'):
        return dict(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag),
                    idx=None if kind == 'w' else os.path.join(G, 'rec_%s.mp4.idx' % tag))
    d = os.path.join(G, 'runs', tag)
    return dict(log=os.path.join(d, 'log.txt'), stdout=os.path.join(d, 'stdout.txt'), idx=os.path.join(d, 'rec.mp4.idx'))


def phase(present):
    if present is None:
        return 'unknown'
    if present < APPROACH_END:
        return 'approach'
    if present < STEPS_FROM:
        return 'rotation'
    if present < STATIC_FROM:
        return 'steps'
    return 'static'


def scan(log_path, level):
    r = dict(lines=0, fix=[], fix_torn=0, ext=[], ext_torn=0, ft_rows=0, ft_all_k2=0, dt_max_all=0, inputs=[], dual=[],
             guest_first=None, entry_line=None, scene_change_line=None, first_scene_n=None, hold_us=0, k2_after=[], dt_max_after=0,
             death=[], vke=0, vk2=0, vk_limit=0, skipped_draw=0, gamepatch=0, gp_applied=0, gp_refused=0, win={}, recovering=0,
             last_ft_n=None)
    pending = []      # FixB42 / FixB42Ext / InputScript entries waiting for the next FrameTrace n
    h = hashlib.sha256()
    after_entry = False
    in_scene = False
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
                    r['last_ft_n'] = n
                    r['dt_max_all'] = max(r['dt_max_all'], dt)
                    if dt >= K2_US:
                        r['ft_all_k2'] += 1
                    for e in pending:
                        e['next_n'] = n
                    pending = []
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
                                r['k2_after'].append((n, dt, ln))
                continue
            if b'FixB42Ext:' in raw:
                m = RX_EXT.search(raw)
                if not m:
                    r['ext_torn'] += 1
                    continue
                e = dict(line=ln, kind='ext', mode=int(m.group(1)), extent=(int(m.group(2)), int(m.group(3))), hit=int(m.group(4)),
                         applied=int(m.group(5)), drawn=int(m.group(6)), rearm=int(m.group(7)), frame=int(m.group(8)), next_n=None)
                r['ext'].append(e)
                pending.append(e)
                continue
            if b'FixB42:' in raw:
                m = RX_FIX.search(raw)
                if not m:
                    r['fix_torn'] += 1
                    continue
                e = dict(line=ln, kind='fix', mode=int(m.group(1)), hit=int(m.group(2)), applied=int(m.group(3)), drawn=int(m.group(4)),
                         rearm=int(m.group(5)), hit_all=int(m.group(6)), last_frame=int(m.group(7)),
                         extent=(int(m.group(8)), int(m.group(9))), cmask=m.group(10).decode().lower(),
                         clear='%s/%s' % (m.group(11).decode().lower(), m.group(12).decode().lower()), next_n=None)
                r['fix'].append(e)
                pending.append(e)
                continue
            if b'InputScript: ' in raw:
                m = RX_IN.search(raw)
                if m:
                    e = dict(line=ln, ev=m.group(1).decode(), key=m.group(2).decode(), t=float(m.group(3)),
                             present=int(m.group(4)), next_n=None)
                    r['inputs'].append(e)
                    pending.append(e)
                continue
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
                if b'[Vulkan][W][2]' in raw or b'[Vulkan][E][2]' in raw:
                    r['vk2'] += 1
            if b'this will be the last time reporting it' in raw:
                r['vk_limit'] += 1
            if b'AsyncPipelines: skipped draw' in raw:
                r['skipped_draw'] += 1
            if b'GamePatch:' in raw:
                r['gamepatch'] += 1
                if b'GamePatch: applied' in raw:
                    r['gp_applied'] += 1
                if b'GamePatch: refused' in raw:
                    r['gp_refused'] += 1
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


def stdout_death(path):
    out = []
    if not path or not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        for i, raw in enumerate(f, 1):
            for d in DEATH:
                if d in raw:
                    out.append(('stdout', d.decode(), i))
    return out


def offset_of(inputs):
    vals = [e['present'] - e['next_n'] for e in inputs if e['next_n'] is not None]
    return int(statistics.median(vals)) if vals else None


def grow(lines, off):
    """Growth per extent (within one kind of line), present and phase of every line; returns the last counters per extent."""
    prev = {}
    for e in lines:
        p = prev.get(e['extent'], dict(hit=0, applied=0, drawn=0, rearm=0))
        for k in ('hit', 'applied', 'drawn', 'rearm'):
            e['d_' + k] = e[k] - p[k]
        prev[e['extent']] = dict(hit=e['hit'], applied=e['applied'], drawn=e['drawn'], rearm=e['rearm'])
        e['present'] = (e['next_n'] + off) if (off is not None and e['next_n'] is not None) else None
        e['phase'] = phase(e['present'])
    return prev


def ext_reference(ext_t6, fix_t6):
    """Lead line 417cc2d8: SHOWN / NOT_DETERMINED for the growth of applied of 960x540 in the static phase."""
    if any(e['present'] is None for e in ext_t6):
        return 'NOT_DETERMINED', None, 'NOT_DETERMINED', None
    before = [e for e in ext_t6 if e['present'] < STATIC_FROM]
    after = [e for e in ext_t6 if e['present'] >= STATIC_FROM]
    base = before[-1]['applied'] if before else 0
    hit = next((e for e in after if e['applied'] > base), None)
    vb = [e['applied'] for e in ext_t6 + fix_t6 if e['present'] is not None and e['present'] < STATIC_FROM]
    vbase = max(vb) if vb else 0
    vhit = next((e for e in after if e['applied'] > vbase), None)
    pick = lambda e: None if e is None else dict((k, e[k]) for k in ('line', 'present', 'phase', 'hit', 'applied', 'frame'))
    return ('SHOWN' if hit else 'NOT_DETERMINED'), dict(base=base, line=pick(hit)), \
           ('SHOWN' if vhit else 'NOT_DETERMINED'), dict(base=vbase, line=pick(vhit))


def read(log_path, stdout_path, idx_path, kind):
    level = LEVEL[kind]
    r = scan(log_path, level)
    off = offset_of(r['inputs'])
    last = grow(r['fix'], off)
    last_ext = grow(r['ext'], off)
    last_present = (r['last_ft_n'] + off) if (off is not None and r['last_ft_n'] is not None) else None
    t6 = [e for e in r['fix'] if e['extent'] == T6]
    ext_t6 = [e for e in r['ext'] if e['extent'] == T6]
    viol = [e for e in t6 + ext_t6 if e['d_hit'] > e['d_applied']]
    sd = stdout_death(stdout_path)
    death = r['death'] + (sd or [])
    idx_n = None
    if idx_path and os.path.exists(idx_path):
        with open(idx_path, 'rb') as f:
            idx_n = sum(1 for _ in f)
    modes = sorted(set(e['mode'] for e in r['fix']))
    ext_modes = sorted(set(e['mode'] for e in r['ext']))
    rel = [e for e in r['inputs'] if e['ev'] == 'release' and e['present'] == 5945]
    xr, xr_info, xv, xv_info = ext_reference(ext_t6, t6)
    res = dict(kind=kind, level=level, log=log_path, log_sha256=r['sha256'], log_lines=r['lines'], idx_records=idx_n,
               offset=off, last_present=last_present, fix_lines=len(r['fix']), fix_torn=r['fix_torn'], modes=modes,
               ext_lines=len(r['ext']), ext_torn=r['ext_torn'], ext_modes=ext_modes, mode_expect=MODE[kind],
               extents={'%dx%d' % k: v for k, v in sorted(last.items())},
               ext_extents={'%dx%d' % k: dict(v, lines=sum(1 for e in r['ext'] if e['extent'] == k)) for k, v in sorted(last_ext.items())},
               hit_all_max=max([e['hit_all'] for e in r['fix']] or [0]),
               t6_lines=len(t6), t6_hit_max=max([e['hit'] for e in t6 + ext_t6] or [0]),
               t6_drawn_max=max([e['drawn'] for e in t6 + ext_t6] or [0]),
               ext_t6=[dict((k, e[k]) for k in ('line', 'present', 'phase', 'hit', 'applied', 'drawn', 'rearm', 'frame')) for e in ext_t6],
               ext_ref=xr, ext_ref_info=xr_info, ext_ref_var=xv, ext_ref_var_info=xv_info,
               t6_violations=[dict((k, e[k]) for k in ('kind', 'line', 'present', 'phase', 'd_hit', 'd_applied')) for e in viol],
               c0_line=next((dict((k, e[k]) for k in ('kind', 'line', 'present', 'phase', 'hit', 'applied')) for e in t6 + ext_t6
                             if e['mode'] == 0 and e['hit'] >= 1 and e['applied'] == 0), None),
               clears=sorted(set('%dx%d %s' % (e['extent'][0], e['extent'][1], e['clear']) for e in r['fix']
                                 if e['extent'] in (T6, (480, 270)))),
               cmask_t6=sorted(set(e['cmask'] for e in t6)),
               entry_line=r['entry_line'], scene_change_line=r['scene_change_line'], first_scene_n=r['first_scene_n'],
               hold_s=round(r['hold_us'] / 1e6, 1), hold_us=r['hold_us'], k2_after=r['k2_after'], dt_max_after=r['dt_max_after'],
               ft_rows=r['ft_rows'], ft_all_k2=r['ft_all_k2'], dt_max_all=r['dt_max_all'], death=death,
               stdout_present=sd is not None, vke=r['vke'], vk2=r['vk2'], vk_limit=r['vk_limit'],
               dual=r['dual'], guest_first=r['guest_first'],
               dual_ok=any(s == 1 and e == 1 and (r['guest_first'] is None or ln < r['guest_first']) for ln, s, e in r['dual']),
               skipped_draw=r['skipped_draw'], gamepatch=r['gamepatch'], gp_applied=r['gp_applied'], gp_refused=r['gp_refused'],
               win=r['win'], recovering=r['recovering'], inputs=len(r['inputs']), release5945=bool(rel))
    return res


def form_ok(res):
    allm = sorted(set(res['modes']) | set(res['ext_modes']))
    return allm in ([res['mode_expect']], [])


def rows(tag, res):
    k = res['kind']
    out = ['FS3C %s kind %s level %s log sha256 %s lines %d' % (tag, k, res['level'], res['log_sha256'], res['log_lines'])]
    add = out.append
    gp_exp = 'expected >= 1 applied, 0 refused' if k == 'pu' else 'expected 0'
    add('  form: FixB42 mode values %s, FixB42Ext mode values %s (expected %d) -> %s; GamePatch lines %d (applied %d, refused %d; %s); '
        'torn FixB42 lines %d, torn FixB42Ext lines %d'
        % (res['modes'], res['ext_modes'], res['mode_expect'], 'OK' if form_ok(res) else 'FORM ERROR', res['gamepatch'],
           res['gp_applied'], res['gp_refused'], gp_exp, res['fix_torn'], res['ext_torn']))
    add('  entry line %s; scene change line %s; first scene frame n %s; hold (sum dt after it) %.1f s'
        % (res['entry_line'], res['scene_change_line'], res['first_scene_n'], res['hold_s']))
    add('  frames >= 1 s after the first scene frame: %d (max dt_us %d); all rows %d (max %d) - reference'
        % (len(res['k2_after']), res['dt_max_after'], res['ft_all_k2'], res['dt_max_all']))
    add('  death markers: %d %s; emulator stdout %s' % (len(res['death']), res['death'][:3], 'present' if res['stdout_present'] else 'MISSING'))
    add('  window: %s, Recovering Vulkan swapchain %d' % (res['win'] or 'none', res['recovering']))
    add('  video index records %s; FrameTrace rows %d; InputScript lines %d, release present 5945 %s; present offset %s; last present %s'
        % (res['idx_records'], res['ft_rows'], res['inputs'], res['release5945'], res['offset'], res['last_present']))
    add('  FixB42 lines %d; per extent (last counters): %s; hit_all max %d'
        % (res['fix_lines'], '; '.join('%s hit %d applied %d drawn %d rearm %d' % (x, v['hit'], v['applied'], v['drawn'], v['rearm'])
                                        for x, v in res['extents'].items()) or 'none', res['hit_all_max']))
    add('  FixB42Ext lines %d; per extent (lines, last counters): %s'
        % (res['ext_lines'], '; '.join('%s lines %d hit %d applied %d drawn %d rearm %d' % (x, v['lines'], v['hit'], v['applied'], v['drawn'], v['rearm'])
                                        for x, v in res['ext_extents'].items()) or 'none'))
    add('  FixB42Ext extent=960x540 lines: %s' % (res['ext_t6'] or 'none'))
    add('  extent 960x540: FixB42 lines %d, hit max %d, drawn max %d; violations (growth hit > growth applied, per kind of line) %d %s'
        % (res['t6_lines'], res['t6_hit_max'], res['t6_drawn_max'], len(res['t6_violations']), res['t6_violations'][:3]))
    add('  clear (reference, item 351 (g)(3)): %s; cmask of 960x540: %s' % (res['clears'] or 'none', res['cmask_t6'] or 'none'))
    add('  AsyncPipelines: skipped draw %d (reference)' % res['skipped_draw'])
    if k in ('u', 'pu'):
        add('  EXT reference (lead line 417cc2d8): growth of applied of 960x540 in the static phase: %s %s; executor variant (base = any '
            '960x540 line before the phase): %s %s' % (res['ext_ref'], res['ext_ref_info'], res['ext_ref_var'], res['ext_ref_var_info']))
    if k == 'w':
        add('  W: [Vulkan][E] %d; validation active ([W][2]/[E][2]) %d; last-time-reporting lines %d; DualSrcBlend lines %s, '
            'supported=1 enabled=1 before the first GuestOut (line %s): %s'
            % (res['vke'], res['vk2'], res['vk_limit'], res['dual'][:2], res['guest_first'], res['dual_ok']))
    m = []
    mode_row = ('FixB42 lines mode=%d (>= 1 line, all of the expected mode)' % res['mode_expect'],
                res['fix_lines'] >= 1 and form_ok(res))
    if k in ('u', 'pu', 'w', 'v', 'hb'):
        m.append(mode_row)
        m.append(('reference: no FixB42 line with hit_all >= 1 (hit = 0 at the default) - question to the lead', res['hit_all_max'] == 0))
    if k in ('u', 'pu'):
        m.append(('reference: FixB42Ext extent=960x540 line present', bool(res['ext_t6'])))
        m.append(('item 353 (d)(3): drawn > 0 on 960x540 -> read so: T6 got a draw; question to the lead', res['t6_drawn_max'] > 0))
    if k in ('u0',):
        m.append(mode_row)
        m.append(('C0 line: mode=0 extent=960x540 hit >= 1 applied=0', res['c0_line'] is not None))
    if k == 'pu':
        m.append(('reference: GamePatch applied >= 1 and refused 0', res['gp_applied'] >= 1 and res['gp_refused'] == 0))
    m.append(('0 death markers', not res['death']))
    m.append(('entered (entry line of %s)' % res['level'], res['entry_line'] is not None))
    m.append(('0 frames >= 1 s after the first scene frame' + (' (reference for hb)' if k == 'hb' else ''), not res['k2_after']))
    if k != 'w':
        m.append(('video index records >= 3000', (res['idx_records'] or 0) >= 3000))
    if k in ('w', 'v', 'hb'):
        m.append(('hold >= 300 s (sum dt after the first scene frame)', res['hold_us'] >= 300000000))
    if k == 'w':
        m.append(('W: 0 [Vulkan][E]', res['vke'] == 0))
        m.append(('W: validation active', res['vk2'] > 0))
        m.append(('W: DualSrcBlend supported=1 enabled=1 before the first GuestOut', res['dual_ok']))
    if k != 'pu':
        m.append(('GamePatch lines 0', res['gamepatch'] == 0))
    m.append(('no window minimized / Recovering Vulkan swapchain (else not read as an outcome, question to the lead)',
              not res['win'].get('minimized') and not res['recovering']))
    for name, val in m:
        add('  ROW %s: %s' % (name, 'YES' if val else 'NO'))
    return out


def main(argv):
    if '--log' in argv:
        lp = argv[argv.index('--log') + 1]
        kind = argv[argv.index('--tag-kind') + 1]
        res = read(lp, lp + '.stdout', lp + '.idx', kind)
        tag = 'fixture'
    else:
        tag = argv[0]
        kind = kind_of(tag)
        p = paths(tag, kind)
        res = read(p['log'], p['stdout'], p['idx'], kind)
    print('\n'.join(rows(tag, res)))
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w') as f:
            json.dump(res, f, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
