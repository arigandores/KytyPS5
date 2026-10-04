"""Track F link F16m (HPP-585; ROADMAP s122 items 492 (d)-(zh), 495 (b)-(g), 496 (b)(3)-(5), 500 (b)(2)-(3), 501 (b)): the reader of one tag
of the F16k2 test binary d4328b0c (KYTY_FIX_F5CMU / KYTY_DIAG_F5ID / KYTY_DIAG_F5).  Rows only, no verdict (the reading is F16n's, HPP-586).
usage: python f16m_read.py <tag> [--json <out.json>]
       python f16m_read.py --dir <fixture dir> --tag <tag>   (fixture files: log.txt, stdout.txt, es.json, installed_sha.txt,
           installed_before.txt, installed_after.txt, warm.txt, manifest_cmp.txt, bin.exe, rec.idx, glitch.txt, sheet.txt)
tags: f5cmu_0 (KYTY_FIX_F5CMU=0), f5cmu_1 (=1) - enemy_final, form V of track F (KYTY_DIAG_F5=1, KYTY_DIAG_F5ID not set, video);
      f5id_sg (underwater_aerial_garden), f5id_ef (enemy_final), f5id_bh (big_hand_pirate_island), f5id_eb (ending_boss_after_credit) -
      form F16f (KYTY_DIAG_F5=1 KYTY_DIAG_F5ID=1, KYTY_FIX_F5CMU not set, no video).
Port of C:/kyty/f287/f16f/f16f_read.py (binary, env, entry, hold, death, window, manifest rows; the DiagF5 frame lines) with the readers of
the lines of KytyPS5 ed4f96d8 src/graphics/host_gpu/renderer/diagF5.cpp:
  'DiagF5: frame=<n> <name>=<value> ...'  59 counters in the order of F5Names (:159-:218): the 51 of F16d2, then f5cmu_kept,
      f5cmu_kept_applied, f5cmu_exact_stale, f5cmu_fallback, dcc_stale_bucket_only, dcc_stale_fallback, cmask_rt_bucket_only,
      f5cmu_exact_cpu (item 500 (b)(2): the line is longer by the last field f5cmu_exact_cpu).
  'FixF5Cmu: mode=1' (:586); 'DiagF5Id: mode=1' / 'DiagF5Id: mode=0 needs=KYTY_DIAG_F5' (:713).
  'DiagF5Ev: cmask_fce n= present= gpu= image= cmask= extent=WxH applied= fix= [why=]' (:644);
  'DiagF5Ev: cmask_fce_nohit n= b42= present= gpu= image= cmask= extent=WxH fix= [why=]' (:664); 64 lines per kind, then count only.
  'DiagF5Id: sum frame= exit= <36 counters of IdNames, the last stamp_late> marks= open= dcc_fce_no_image= meta_cs_untracked=
      meta_cs_tracked= id_fce=ok|bad id_cs=ok|bad' (:1047-:1053); 'DiagF5Id: key site=fce ...' (:1058), 'DiagF5Id: key site=cs ...' (:1067);
  'DiagF5Id: fce frame= present= ...' (:772), 'DiagF5Id: fce_next base= kind= ...' (:456), 'DiagF5Id: cs frame= ...' (:913),
  'DiagF5Id: stale_apply site= ...' (:941).
Definitions (the seal docs/track-f/f16m.md section 4):
  in scene        a line after the first 'GuestOut: Level has started: <level>' line (item 492 (d): the verdict is by the events in the scene,
                  the events before it are a reference).
  identity 496    item 496 (b)(5) on the f5cmu_1 arm: the count of DiagF5Ev lines of both kinds with fix in {kept, kept_applied} = f5cmu_kept,
                  with kept_applied = f5cmu_kept_applied, exact_stale = f5cmu_exact_stale, fallback = f5cmu_fallback; beyond the letter
                  exact_stale why=cpu = f5cmu_exact_cpu (F16k2 section 3).  LETTER: the event lines of the whole log against the last DiagF5
                  frame line.  VARIANT OF THE EXECUTOR: the event lines before the last DiagF5 frame line.  Both printed, the control reads the
                  LETTER.  Applies while no kind exhausted its limit (a line with n=64 of the kind; for cmask_fce also cmask_fce_b42 +
                  cmask_fce_unapplied > 64); exhausted -> the row is LIMIT (not a member; item 496 (b)(5)).
  b42=drawn       a 'cmask_fce_nohit b42=drawn' line = not this binary (item 501 (b)(1)): an interference row of the tag.
  pair controls   item 492 (e)(2): f5cmu_1 - 'FixF5Cmu: mode=1' before the first GuestOut; f5cmu_0 - 0 lines 'FixF5Cmu:'; DiagF5Ev lines >= 1 in
                  both; f5cmu_0 - 0 lines 'DiagF5Id:' (null control of item 492 (d)), every event fix=off, 0 nohit lines, f5cmu_* = 0 on
                  every frame line (item 492 (v)(5)); f5cmu_1 - f5cmu_kept_applied <= f5cmu_kept and f5cmu_exact_cpu <= f5cmu_exact_stale on
                  every frame line, identity 496.
  id controls     item 492 (d): 'DiagF5Id: mode=1' before the first GuestOut; identities (g)(4): id_fce=ok and id_cs=ok on every sum line,
                  >= 1 sum line; positive: the counter fce >= 1 on the last sum line of f5id_ef and f5id_eb (FCE site events), the counter cs >= 1
                  on each of the four (ClearMeta site events); 0 lines 'FixF5Cmu:'; meta_clear = 0 on the last sum line (item 495 (v): > 0 is an
                  interference of the run form).
  branch 2 keys   (base, dcc, reason) of the key lines site=fce (the last one per key: n texture target none exit cleared bufreads) and the
                  printed fce lines of the key (entry, clear_mask, dcc_en, wr_after, cpu_mod; the first 4 events of a key only); n at the entry
                  = max(key_n of the key's fce lines before the entry, n of its key lines before the entry) - a lower bound.
  branch 3 keys   (shader, addr, class) of the key lines site=cs (n, stale_apply) and the printed cs lines (sub, vclass, entry, clear_mask,
                  changed, mark).
  F26             dcc_stale_bucket_only, dcc_stale_fallback, cmask_rt_bucket_only of the last DiagF5 frame line (item 492 (g)(5)).
  stamp_late      the counter stamp_late of the last sum line (item 496 (b)(3), item 501 (b)(2)).
  admission rows  the tag binary d4328b0c by sha256 only (item 501 (b)(4); the version strings are printed as a reference); installed adb0c82f
                  before and after; env of the tag form; entry line of the level; hold (sum dt_us of FrameTrace rows after the first row with
                  draws >= 100 after the entry, before a scene change) >= 300 s; the process lived through the hold; manifest cmp EQUAL; no
                  interference (window minimized, Recovering Vulkan swapchain, GamePatch line - item 273 (z); b42=drawn line - item 501 (b)(1));
                  f5cmu_*: video index records >= 3000.  Frames >= 1 s, death markers, [Vulkan][E], one-frame glitches - REPORT rows.
ASCII output only."""
import hashlib, json, os, re, sys

G = 'C:/kyty/f287/f16m'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_d4328b0c.exe'
BIN_EXPECT = 'd4328b0c8053d7deae0ef34691462af3e244dd3a6be07722146505b642ca203c'
VERSIONS = (b'KytyPS5-2026-09-15-6a2987a-2240-ged4f96d8', b'KytyPS5-2026-09-15-6a2987a-2225-gc0789a34')
WANT = 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421'
DIR_FIX = 'variant_fixb26_fixb1b_fixf10'
TAGS = {'f5cmu_0': ('enemy_final', 'pair0'), 'f5cmu_1': ('enemy_final', 'pair1'),
        'f5id_sg': ('underwater_aerial_garden', 'id'), 'f5id_ef': ('enemy_final', 'id'),
        'f5id_bh': ('big_hand_pirate_island', 'id'), 'f5id_eb': ('ending_boss_after_credit', 'id')}
FCE_POS = ('f5id_ef', 'f5id_eb')
F5_NAMES = ['rt_resolves', 'dcc_rt', 'rtcheck_meta', 'dcc_rt_pending', 'dcc_rt_cleared', 'dcc_rt_skip_levels', 'dcc_rt_skip_partial',
            'dcc_rt_skip_decode', 'dcc_rt_skip_layers', 'dcc_mat_pending', 'dcc_mat_cleared', 'dcc_mat_undecoded', 'dcc_fce',
            'dcc_fce_image', 'dcc_fce_no_image', 'dcc_fill_all', 'dcc_fill_meta', 'dcc_fill_clear', 'dcc_fill_uncompressed',
            'dcc_fill_unknown', 'dcc_reset_stale', 'dcc_reset_type', 'meta_refused_known', 'meta_cs_tracked', 'meta_cs_untracked',
            'meta_dma_untracked', 'meta_dma_noclear', 'cmask_rt_pending', 'cmask_rt_cleared', 'cmask_rt_skip_value',
            'cmask_rt_skip_partial', 'cmask_rt_skip_decode', 'cmask_rt_skip_layers', 'cmask_fce', 'cmask_fce_noimage', 'cmask_fce_meta',
            'cmask_fce_msaa', 'cmask_fce_layout', 'cmask_fce_nofill', 'cmask_fce_drawn', 'cmask_fce_b42', 'cmask_fce_unapplied',
            'fmask_read', 'round_unorm', 'round_float', 'round_other', 'ds_unbound', 'ds_unbound_clear', 'stereo_writes',
            'stereo_nonzero', 'zero_disp', 'f5cmu_kept', 'f5cmu_kept_applied', 'f5cmu_exact_stale', 'f5cmu_fallback',
            'dcc_stale_bucket_only', 'dcc_stale_fallback', 'cmask_rt_bucket_only', 'f5cmu_exact_cpu']
CMU = ['f5cmu_kept', 'f5cmu_kept_applied', 'f5cmu_exact_stale', 'f5cmu_fallback', 'f5cmu_exact_cpu']
F26 = ['dcc_stale_bucket_only', 'dcc_stale_fallback', 'cmask_rt_bucket_only']
FAMILIES = [('dcc_rt_pending', ['dcc_rt_cleared', 'dcc_rt_skip_levels', 'dcc_rt_skip_partial', 'dcc_rt_skip_decode', 'dcc_rt_skip_layers']),
            ('dcc_mat_pending', ['dcc_mat_cleared', 'dcc_mat_undecoded']),
            ('dcc_fce', ['dcc_fce_image', 'dcc_fce_no_image']),
            ('dcc_fill_meta', ['dcc_fill_clear', 'dcc_fill_uncompressed', 'dcc_fill_unknown']),
            ('meta_refused_known', ['meta_cs_tracked', 'meta_cs_untracked', 'meta_dma_untracked', 'meta_dma_noclear']),
            ('cmask_rt_pending', ['cmask_rt_cleared', 'cmask_rt_skip_value', 'cmask_rt_skip_partial', 'cmask_rt_skip_decode',
                                  'cmask_rt_skip_layers']),
            ('cmask_fce', ['cmask_fce_noimage', 'cmask_fce_meta', 'cmask_fce_msaa', 'cmask_fce_layout', 'cmask_fce_nofill',
                           'cmask_fce_drawn', 'cmask_fce_b42', 'cmask_fce_unapplied'])]
F5_LE = [('dcc_rt', 'rt_resolves'), ('stereo_nonzero', 'stereo_writes'), ('ds_unbound_clear', 'ds_unbound'),
         ('f5cmu_kept_applied', 'f5cmu_kept'), ('f5cmu_exact_cpu', 'f5cmu_exact_stale')]
ID_NAMES = ['fce', 'r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'cs', 'img_clear', 'meta_clear', 'tracked', 'tracked_other',
            'exec_nofill', 'exec_fill_clear', 'exec_fill_other', 'changed', 'changed_na', 'marks_set', 'marks_dropped', 'marks_overflow',
            'stale_apply', 'next_texture', 'next_target', 'next_none', 'next_exit', 'next_cleared', 'next_bufreads', 'next_merged',
            'next_overflow', 'keys_fce', 'keys_cs', 'overflow_fce', 'overflow_cs', 'stamp_late']
SUM_TAIL = ['marks', 'open', 'dcc_fce_no_image', 'meta_cs_untracked', 'meta_cs_tracked']
FIXES = ('off', 'fresh', 'exact_stale', 'kept', 'kept_applied', 'fallback')
EV_LIMIT = 64
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_F5 = re.compile(rb'DiagF5: frame=(\d+)' + b''.join(rb' ' + n.encode() + rb'=(\d+)' for n in F5_NAMES) + rb'(?=\s|$)')
RX_EV = re.compile(rb'DiagF5Ev: cmask_fce n=(\d+) present=(\d+) gpu=(\d+) image=0x([0-9a-f]+) cmask=0x([0-9a-f]+) extent=(\d+)x(\d+) '
                   rb'applied=([01]) fix=([a-z_]+)(?: why=([a-z]+))?\s*$')
RX_NH = re.compile(rb'DiagF5Ev: cmask_fce_nohit n=(\d+) b42=(none|drawn) present=(\d+) gpu=(\d+) image=0x([0-9a-f]+) cmask=0x([0-9a-f]+) '
                   rb'extent=(\d+)x(\d+) fix=([a-z_]+)(?: why=([a-z]+))?\s*$')
RX_SUM = re.compile(rb'DiagF5Id: sum frame=(\d+) exit=([01])' + b''.join(rb' ' + n.encode() + rb'=(\d+)' for n in ID_NAMES + SUM_TAIL)
                    + rb' id_fce=(ok|bad) id_cs=(ok|bad)\s*$')
RX_KF = re.compile(rb'DiagF5Id: key site=fce base=0x([0-9a-f]+) dcc=0x([0-9a-f]+) reason=(r\d) n=(\d+) texture=(\d+) target=(\d+) none=(\d+) '
                   rb'exit=(\d+) cleared=(\d+) bufreads=(\d+)\s*$')
RX_KC = re.compile(rb'DiagF5Id: key site=cs shader=0x([0-9a-f]+) addr=0x([0-9a-f]+) class=([a-z_]+) n=(\d+) stale_apply=(\d+)\s*$')
RX_KV = re.compile(rb' ([a-z_]+)=([^ \r\n]+)')
M_START = b'GuestOut: Level has started: '
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
K2_US = 1000000
HOLD_MIN_US = 300000000
VIDEO_MIN = 3000
RX_GL = re.compile(r'one-frame glitches: (\d+)')
RX_GLP = re.compile(r'video\s+(\d+) present\s+(\d+)')


def kv(raw, key):
    """Fields name=value of a DiagF5Id fce / cs / fce_next / stale_apply line (the text after the key word)."""
    i = raw.find(key)
    return dict((k.decode(), v.decode('ascii', 'replace')) for k, v in RX_KV.findall(raw[i + len(key):]))


def ident_f5(d):
    bad = []
    for p, ch in FAMILIES:
        s = sum(d[c] for c in ch)
        if d[p] != s:
            bad.append('%s=%d != sum of children %d' % (p, d[p], s))
    for a, b in F5_LE:
        if d[a] > d[b]:
            bad.append('%s=%d > %s=%d' % (a, d[a], b, d[b]))
    return bad


class Series(object):
    """The DiagF5 frame lines: count, malformed, identities on every line, monotonicity, f5cmu_* nonzero lines, the last line."""

    def __init__(self):
        self.lines = self.malformed = 0
        self.mode = []
        self.ident_bad = []
        self.mono_bad = []
        self.cmu_nonzero = 0
        self.last = None
        self.last_lineno = None

    def add(self, d, ln):
        self.lines += 1
        if d is None:
            self.malformed += 1
            return
        bad = ident_f5(d)
        if bad:
            self.ident_bad.append((self.lines, ln, bad[:3]))
        if any(d[n] for n in CMU):
            self.cmu_nonzero += 1
        if self.last is not None:
            p = self.last
            dec = [n for n in F5_NAMES if d[n] < p[n]]
            if dec or d['frame'] < p['frame'] or sum(d[n] for n in F5_NAMES) <= sum(p[n] for n in F5_NAMES):
                self.mono_bad.append((self.lines, ln, dec[:3], d['frame'] < p['frame']))
        self.last = d
        self.last_lineno = ln


def parse_f5(raw):
    i = raw.find(b'DiagF5: frame=')
    m = RX_F5.match(raw, i) if i >= 0 else None
    if not m:
        return None
    v = [int(x) for x in m.groups()]
    d = dict(zip(F5_NAMES, v[1:]))
    d['frame'] = v[0]
    return d


def parse_event(raw):
    """One DiagF5Ev line -> dict, or None when malformed."""
    m = RX_EV.search(raw)
    if m:
        g = m.groups()
        return dict(kind='fce', n=int(g[0]), b42='hit', present=int(g[1]), gpu=int(g[2]), image=g[3].decode(), cmask=g[4].decode(),
                    extent='%sx%s' % (g[5].decode(), g[6].decode()), applied=int(g[7]), fix=g[8].decode(),
                    why=g[9].decode() if g[9] else None)
    m = RX_NH.search(raw)
    if m:
        g = m.groups()
        return dict(kind='nohit', n=int(g[0]), b42=g[1].decode(), present=int(g[2]), gpu=int(g[3]), image=g[4].decode(),
                    cmask=g[5].decode(), extent='%sx%s' % (g[6].decode(), g[7].decode()), applied=None, fix=g[8].decode(),
                    why=g[9].decode() if g[9] else None)
    return None


def parse_sum(raw):
    m = RX_SUM.search(raw)
    if not m:
        return None
    g = m.groups()
    d = dict(frame=int(g[0]), exit=int(g[1]))
    names = ID_NAMES + SUM_TAIL
    for n, v in zip(names, g[2:2 + len(names)]):
        d[n] = int(v)
    d['id_fce'], d['id_cs'] = g[-2].decode(), g[-1].decode()
    return d


def id_recount(s):
    """The identities (g)(4) recounted by the reader from the fields of a sum line (diagF5.cpp:1042-:1046, item 495 (b)(4))."""
    reasons = sum(s['r%d' % i] for i in range(1, 8))
    fce = reasons == s['dcc_fce_no_image'] and s['fce'] == reasons and s['r0'] == 0
    cs = (s['img_clear'] + s['meta_clear'] + s['tracked_other'] + s['exec_nofill'] + s['exec_fill_clear'] + s['exec_fill_other']
          == s['meta_cs_untracked'] and s['tracked'] == s['meta_cs_tracked'])
    return ('ok' if fce else 'bad', 'ok' if cs else 'bad')


def rev_text(raw):
    for m in (M_FORK, M_GIT):
        if m in raw:
            return raw.split(m, 1)[1].split(b',', 1)[0].strip()[:80].decode('ascii', 'replace')
    return None


def scan(log_path, level):
    r = dict(lines=0, rev=[], stc=[], guest_first=None, entry_line=None, scene_change_line=None, first_scene_n=None, hold_us=0,
             k2_after=0, dt_max_after=0, ft_rows=0, death=[], skipped_draw=0, win={}, recovering=0, gamepatch=0, vke=0,
             f5_any=0, f6_any=0, fix_mode=[], fix_any=0, id_mode=[], id_mode0=0, id_any=0, ev=[], ev_bad=0, ev_any=0,
             sums=[], sum_bad=0, kf={}, kc={}, kf_before={}, kc_before={}, fce_lines=[], cs_lines=[], next_lines=[], stale_lines=[])
    s5 = Series()
    h = hashlib.sha256()
    after_entry = in_scene = False
    if not log_path or not os.path.exists(log_path):
        r['sha256'] = None
        return r, s5
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
            scene = r['entry_line'] is not None
            if b'DiagF5:' in raw:
                r['f5_any'] += 1
                if b'DiagF5: frame=' in raw:
                    s5.add(parse_f5(raw), ln)
                elif b'DiagF5: mode=1' in raw:
                    s5.mode.append(ln)
            if b'DiagF6:' in raw:
                r['f6_any'] += 1
            if b'FixF5Cmu:' in raw:
                r['fix_any'] += 1
                if b'FixF5Cmu: mode=1' in raw:
                    r['fix_mode'].append(ln)
            if b'DiagF5Ev:' in raw:
                r['ev_any'] += 1
                e = parse_event(raw)
                if e is None:
                    r['ev_bad'] += 1
                else:
                    e['line'] = ln
                    e['scene'] = scene
                    r['ev'].append(e)
            if b'DiagF5Id:' in raw:
                r['id_any'] += 1
                if b'DiagF5Id: mode=1' in raw:
                    r['id_mode'].append(ln)
                elif b'DiagF5Id: mode=0' in raw:
                    r['id_mode0'] += 1
                elif b'DiagF5Id: sum ' in raw:
                    d = parse_sum(raw)
                    if d is None:
                        r['sum_bad'] += 1
                    else:
                        d['line'] = ln
                        r['sums'].append(d)
                elif b'DiagF5Id: key site=fce ' in raw:
                    m = RX_KF.search(raw)
                    if m:
                        g = [x.decode() for x in m.groups()]
                        k = (g[0], g[1], g[2])
                        rec = dict(n=int(g[3]), texture=int(g[4]), target=int(g[5]), none=int(g[6]), exit=int(g[7]), cleared=int(g[8]),
                                   bufreads=int(g[9]))
                        r['kf'][k] = rec
                        if not scene:
                            r['kf_before'][k] = rec['n']
                    else:
                        r['sum_bad'] += 1
                elif b'DiagF5Id: key site=cs ' in raw:
                    m = RX_KC.search(raw)
                    if m:
                        g = [x.decode() for x in m.groups()]
                        k = (g[0], g[1], g[2])
                        r['kc'][k] = dict(n=int(g[3]), stale_apply=int(g[4]))
                        if not scene:
                            r['kc_before'][k] = int(g[3])
                    else:
                        r['sum_bad'] += 1
                elif b'DiagF5Id: fce_next ' in raw:
                    d = kv(raw, b'DiagF5Id: fce_next')
                    d['line'], d['scene'] = ln, scene
                    r['next_lines'].append(d)
                elif b'DiagF5Id: fce ' in raw:
                    d = kv(raw, b'DiagF5Id: fce')
                    d['line'], d['scene'] = ln, scene
                    r['fce_lines'].append(d)
                elif b'DiagF5Id: cs ' in raw:
                    d = kv(raw, b'DiagF5Id: cs')
                    d['line'], d['scene'] = ln, scene
                    r['cs_lines'].append(d)
                elif b'DiagF5Id: stale_apply ' in raw:
                    d = kv(raw, b'DiagF5Id: stale_apply')
                    d['line'], d['scene'] = ln, scene
                    r['stale_lines'].append(d)
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
            if b'[Vulkan][E]' in raw:
                r['vke'] += 1
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
    return r, s5


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


def text(path):
    if not path or not os.path.exists(path):
        return None
    return open(path, 'rb').read().decode('utf-8', 'replace')


def first_line(t):
    return (t or '').split('\n')[0].strip()


def asc(s):
    return s.encode('ascii', 'replace').decode('ascii') if isinstance(s, str) else s


def bin_versions(path):
    if not path or not os.path.exists(path):
        return None
    b = open(path, 'rb').read()
    return [v.decode() for v in VERSIONS if v in b]


def paths(tag, base=None):
    names = ('installed_sha', 'installed_before', 'installed_after', 'warm', 'manifest_cmp', 'glitch', 'sheet')
    if base is not None:
        p = dict((n, os.path.join(base, n + '.txt')) for n in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 bin=os.path.join(base, 'bin.exe'), idx=os.path.join(base, 'rec.idx'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((n, os.path.join(d, n + '.txt')) for n in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             bin=BIN_PATH, idx=os.path.join(G, 'rec_%s.mp4.idx' % tag))
    return p


def read_idx(path):
    """present number -> video frame index (the first record of the present), and the record count; None when absent."""
    if not path or not os.path.exists(path):
        return None, None
    m = {}
    n = 0
    with open(path, 'rb') as f:
        for raw in f:
            parts = raw.split()
            if len(parts) >= 2:
                n += 1
                pr = int(parts[1])
                if pr not in m:
                    m[pr] = int(parts[0])
    return m, n


def env_ok_of(env, kind):
    other_fix = sorted(k for k in env if k.startswith('KYTY_FIX_') and k != 'KYTY_FIX_F5CMU')
    ok = (other_fix == [] and 'KYTY_GAME_PATCH' not in env and 'KYTY_GPU_CHECKPOINTS' not in env and 'KYTY_DIAG_F6' not in env
          and env.get('KYTY_DIAG_F5') == '1')
    if kind == 'pair0':
        return ok and env.get('KYTY_FIX_F5CMU') == '0' and 'KYTY_DIAG_F5ID' not in env
    if kind == 'pair1':
        return ok and env.get('KYTY_FIX_F5CMU') == '1' and 'KYTY_DIAG_F5ID' not in env
    return ok and env.get('KYTY_DIAG_F5ID') == '1' and 'KYTY_FIX_F5CMU' not in env


def ev_counts(evs):
    c = dict((f, 0) for f in FIXES)
    for e in evs:
        c[e['fix']] = c.get(e['fix'], 0) + 1
    return c


def identity496(evs, last):
    """item 496 (b)(5): event line counts by fix against the f5cmu_* counters of the frame line `last`."""
    c = ev_counts(evs)
    cpu = len([e for e in evs if e['fix'] == 'exact_stale' and e['why'] == 'cpu'])
    rows = [('kept+kept_applied = f5cmu_kept', c['kept'] + c['kept_applied'], last['f5cmu_kept']),
            ('kept_applied = f5cmu_kept_applied', c['kept_applied'], last['f5cmu_kept_applied']),
            ('exact_stale = f5cmu_exact_stale', c['exact_stale'], last['f5cmu_exact_stale']),
            ('fallback = f5cmu_fallback', c['fallback'], last['f5cmu_fallback']),
            ('exact_stale why=cpu = f5cmu_exact_cpu (beyond the letter)', cpu, last['f5cmu_exact_cpu'])]
    return [(n, a, b, a == b) for n, a, b in rows]


def limit_state(evs, last):
    fce_n = len([e for e in evs if e['kind'] == 'fce'])
    nh_n = len([e for e in evs if e['kind'] == 'nohit'])
    fce_ex = any(e['kind'] == 'fce' and e['n'] >= EV_LIMIT for e in evs) or (
        last is not None and last['cmask_fce_b42'] + last['cmask_fce_unapplied'] > EV_LIMIT)
    nh_ex = any(e['kind'] == 'nohit' and e['n'] >= EV_LIMIT for e in evs)
    return dict(fce_lines=fce_n, nohit_lines=nh_n, fce_exhausted=fce_ex, nohit_exhausted=nh_ex)


def branch2(r):
    """The keys (base, dcc, reason) with their fields; no rule outcome (F16n)."""
    out = []
    lines_by = {}
    for d in r['fce_lines']:
        k = (d.get('base', '')[2:], d.get('dcc', '')[2:], d.get('reason', ''))
        lines_by.setdefault(k, []).append(d)
    keys = list(r['kf'].keys()) + [k for k in lines_by if k not in r['kf']]
    for k in keys:
        rec = r['kf'].get(k)
        ls = lines_by.get(k, [])
        n_before = max([int(d.get('key_n', '0')) for d in ls if not d['scene']] + [r['kf_before'].get(k, 0)])
        n = rec['n'] if rec else max([int(d.get('key_n', '0')) for d in ls] + [0])
        out.append(dict(base=k[0], dcc=k[1], reason=k[2], n=n, n_at_entry=n_before, in_scene=n - n_before,
                        entry=sorted(set(d.get('entry', '?') for d in ls)),
                        clear_mask_nonzero=sorted(set(int(d.get('clear_mask', '0x0'), 16) != 0 for d in ls)),
                        dcc_en=sorted(set(d.get('dcc_en', '?') for d in ls)), wr_after=sorted(set(d.get('wr_after', '?') for d in ls)),
                        cpu_mod=sorted(set(d.get('cpu_mod', '?') for d in ls)), printed=len(ls),
                        printed_in_scene=len([d for d in ls if d['scene']]),
                        next=dict((x, rec[x]) for x in ('texture', 'target', 'none', 'exit', 'cleared', 'bufreads')) if rec else None))
    return out


def branch3(r):
    out = []
    lines_by = {}
    for d in r['cs_lines']:
        k = (d.get('shader', '')[2:], d.get('addr', '')[2:], d.get('class', ''))
        lines_by.setdefault(k, []).append(d)
    keys = list(r['kc'].keys()) + [k for k in lines_by if k not in r['kc']]
    for k in keys:
        rec = r['kc'].get(k)
        ls = lines_by.get(k, [])
        n_before = max([int(d.get('key_n', '0')) for d in ls if not d['scene']] + [r['kc_before'].get(k, 0)])
        n = rec['n'] if rec else max([int(d.get('key_n', '0')) for d in ls] + [0])
        out.append(dict(shader=k[0], addr=k[1], cls=k[2], n=n, n_at_entry=n_before, in_scene=n - n_before,
                        stale_apply=rec['stale_apply'] if rec else None, sub=sorted(set(d.get('sub', '?') for d in ls)),
                        vclass=sorted(set(d.get('vclass', '?') for d in ls)), entry=sorted(set(d.get('entry', '?') for d in ls)),
                        changed=sorted(set(d.get('changed', '?') for d in ls)), mark=sorted(set(d.get('mark', '?') for d in ls)),
                        printed=len(ls)))
    return out


def mode_ok(lines, guest_first):
    return len(lines) >= 1 and (guest_first is None or lines[0] < guest_first)


def read(p, tag):
    level, kind = TAGS[tag]
    r, s5 = scan(p['log'], level)
    sd, ssha = stdout_scan(p['stdout'])
    rj = text(p['run'])
    run = json.loads(rj) if rj else None
    att = ((run or {}).get('attempts') or [{}])[0] if run else None
    env = (run or {}).get('env') or {}
    sha, sha_b, sha_a = [first_line(text(p[k])) or None for k in ('installed_sha', 'installed_before', 'installed_after')]
    warm_t = text(p['warm'])
    mc = text(p['manifest_cmp'])
    env_ok = None if run is None else env_ok_of(env, kind)
    hold_ok = None if att is None else (att.get('outcome') == 'ok' and att.get('hold_exit') is None)
    close_info = None if att is None else ('outcome %s hold_exit %s hold_s %s close_rc %s close_killed %s' % (
        att.get('outcome'), att.get('hold_exit'), att.get('hold_s'), att.get('close_rc'), att.get('close_killed')))
    L5 = s5.last
    evs = r['ev']
    res = dict(tag=tag, kind=kind, level=level, log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'], stdout_sha256=ssha,
               rev=r['rev'][:6], installed_sha=sha, installed_before=sha_b, installed_after=sha_a, sha_ok=sha == BIN_EXPECT,
               versions=bin_versions(p['bin']), before_ok=sha_b == WANT, after_ok=sha_a == WANT,
               env=dict((k, env[k]) for k in sorted(env) if k.startswith('KYTY_FIX_') or k.startswith('KYTY_DIAG_')
                        or k in ('KYTY_GAME_PATCH', 'KYTY_GPU_CHECKPOINTS')), env_ok=env_ok,
               stc=r['stc'][:3], warm_txt=(warm_t or '').strip()[:240],
               guest_first=r['guest_first'], entry_line=r['entry_line'], scene_change_line=r['scene_change_line'],
               first_scene_n=r['first_scene_n'], hold_s=round(r['hold_us'] / 1e6, 1), hold_len_ok=r['hold_us'] >= HOLD_MIN_US,
               k2_after=r['k2_after'], dt_max_after=r['dt_max_after'], hold_ok=hold_ok, close_info=close_info,
               death=r['death'] + (sd or []), stdout_present=sd is not None, vke=r['vke'], skipped_draw=r['skipped_draw'],
               win=r['win'], recovering=r['recovering'], gamepatch=r['gamepatch'],
               manifest=first_line(mc)[:200], manifest_ok=bool(mc) and mc.startswith('manifest cmp EQUAL'),
               f5_any=r['f5_any'], f6_any=r['f6_any'], fix_any=r['fix_any'], fix_mode=r['fix_mode'][:3], id_any=r['id_any'],
               id_mode=r['id_mode'][:3], id_mode0=r['id_mode0'], ev_any=r['ev_any'], ev_bad=r['ev_bad'], events=evs,
               drawn=len([e for e in evs if e['b42'] == 'drawn']),
               f5=dict(mode=s5.mode[:3], lines=s5.lines, malformed=s5.malformed, ident_bad=s5.ident_bad[:5], ident_bad_n=len(s5.ident_bad),
                       mono_bad=s5.mono_bad[:5], mono_bad_n=len(s5.mono_bad), cmu_nonzero=s5.cmu_nonzero, last=L5,
                       last_lineno=s5.last_lineno, mode_ok=mode_ok(s5.mode, r['guest_first'])))
    res['f5']['health'] = L5 is not None and s5.malformed == 0 and not s5.ident_bad and not s5.mono_bad
    res['f26'] = dict((n, L5[n]) for n in F26) if L5 else None
    res['cmu_last'] = dict((n, L5[n]) for n in CMU) if L5 else None
    res['ev_counts'] = ev_counts(evs)
    res['ev_counts_scene'] = ev_counts([e for e in evs if e['scene']])
    res['limits'] = limit_state(evs, L5)
    # video rows (pair arms)
    idx, idx_n = read_idx(p.get('idx'))
    gt = text(p.get('glitch'))
    gm = RX_GL.search(gt or '')
    res['idx_records'] = idx_n
    res['glitches'] = int(gm.group(1)) if gm else None
    res['glitch_presents'] = [int(x[1]) for x in RX_GLP.findall(gt or '')]
    res['sheet'] = first_line(text(p.get('sheet')))[:200]
    # controls
    ctl = []
    if kind == 'pair1':
        ctl.append(('FixF5Cmu: mode=1 before the first GuestOut', mode_ok(r['fix_mode'], r['guest_first'])))
        ctl.append(('DiagF5Ev lines >= 1 (0 malformed)', len(evs) >= 1 and r['ev_bad'] == 0))
        ctl.append(('a parseable DiagF5 frame line, 0 malformed', L5 is not None and s5.malformed == 0))
        ctl.append(('f5cmu_kept_applied <= f5cmu_kept and f5cmu_exact_cpu <= f5cmu_exact_stale on every frame line',
                    L5 is not None and not [b for b in s5.ident_bad if any('f5cmu' in x for x in b[2])]))
        if L5 is not None:
            lim = res['limits']
            letter = identity496(evs, L5)
            variant = identity496([e for e in evs if e['line'] < s5.last_lineno], L5)
            res['id496_letter'] = letter
            res['id496_variant'] = variant
            res['id496_limit'] = lim['fce_exhausted'] or lim['nohit_exhausted']
            if res['id496_limit']:
                ctl.append(('identity of item 496 (b)(5) (LETTER) - LIMIT exhausted, not a member', True))
            else:
                ctl.append(('identity of item 496 (b)(5) (LETTER: event lines of the whole log vs the last DiagF5 line), 4 equalities',
                            all(x[3] for x in letter[:4])))
        ctl.append(('0 lines DiagF5Id: (KYTY_DIAG_F5ID not set)', r['id_any'] == 0))
    elif kind == 'pair0':
        ctl.append(('0 lines FixF5Cmu:', r['fix_any'] == 0))
        ctl.append(('DiagF5Ev lines >= 1 (0 malformed)', len(evs) >= 1 and r['ev_bad'] == 0))
        ctl.append(('a parseable DiagF5 frame line, 0 malformed', L5 is not None and s5.malformed == 0))
        ctl.append(('every event fix=off, 0 nohit lines', all(e['fix'] == 'off' for e in evs) and res['limits']['nohit_lines'] == 0))
        ctl.append(('f5cmu_* = 0 on every frame line (item 492 (v)(5))', L5 is not None and s5.cmu_nonzero == 0))
        ctl.append(('0 lines DiagF5Id: (null control, item 492 (d))', r['id_any'] == 0))
    else:
        sums = r['sums']
        last = sums[-1] if sums else None
        res['sum_last'] = last
        res['sum_lines'] = len(sums)
        res['sum_bad'] = r['sum_bad']
        res['sum_exit'] = len([s for s in sums if s['exit'] == 1])
        res['id_bad_lines'] = [(s['line'], s['id_fce'], s['id_cs'], id_recount(s)) for s in sums
                               if s['id_fce'] != 'ok' or s['id_cs'] != 'ok' or id_recount(s) != ('ok', 'ok')][:5]
        mono = []
        for a, b in zip(sums, sums[1:]):
            dec = [n for n in ID_NAMES if b[n] < a[n]]
            if dec:
                mono.append((b['line'], dec[:3]))
        res['sum_mono_bad'] = mono[:5]
        res['stamp_late'] = last['stamp_late'] if last else None
        res['branch2'] = branch2(r)
        res['branch3'] = branch3(r)
        res['next_lines'] = r['next_lines'][:64]
        res['stale_lines'] = r['stale_lines'][:64]
        res['fce_lines_n'] = len(r['fce_lines'])
        res['cs_lines_n'] = len(r['cs_lines'])
        ctl.append(('DiagF5Id: mode=1 before the first GuestOut', mode_ok(r['id_mode'], r['guest_first'])))
        ctl.append(('>= 1 sum line, 0 malformed DiagF5Id sum/key lines', last is not None and r['sum_bad'] == 0))
        ctl.append(('identities (g)(4): id_fce=ok and id_cs=ok on every sum line, printed and recounted by the reader',
                    last is not None and not res['id_bad_lines']))
        if tag in FCE_POS:
            ctl.append(('positive: FCE site events (fce) >= 1 on the last sum line', last is not None and last['fce'] >= 1))
        ctl.append(('positive: ClearMeta site events (cs) >= 1 on the last sum line', last is not None and last['cs'] >= 1))
        ctl.append(('0 lines FixF5Cmu: (KYTY_FIX_F5CMU not set)', r['fix_any'] == 0))
        ctl.append(('f5cmu_* = 0 on every frame line', L5 is not None and s5.cmu_nonzero == 0))
        ctl.append(('meta_clear = 0 on the last sum line (item 495 (v))', last is not None and last['meta_clear'] == 0))
    res['control'] = ctl
    res['control_alive'] = all(v for _, v in ctl)
    res['interference'] = bool(r['win'].get('minimized') or r['recovering'] or r['gamepatch'] or res['drawn'])
    return res


def yn(v):
    if v is None:
        return 'NOT_READ'
    if isinstance(v, str):
        return v
    return 'YES' if v else 'NO'


def fmt_ev(e):
    return ('%s n=%d b42=%s present=%d gpu=%d image=0x%s cmask=0x%s extent=%s applied=%s fix=%s why=%s line=%d %s' % (
        e['kind'], e['n'], e['b42'], e['present'], e['gpu'], e['image'], e['cmask'], e['extent'],
        '-' if e['applied'] is None else e['applied'], e['fix'], e['why'] or '-', e['line'], 'scene' if e['scene'] else 'before'))


def rows(res):
    tag, k = res['tag'], res['kind']
    out = ['F16M %s kind %s level %s log sha256 %s lines %d stdout sha256 %s' % (tag, k, res['level'], res['log_sha256'],
                                                                              res['log_lines'], res['stdout_sha256'])]
    add = out.append
    add('  binary: tag %s (expected %s); version strings in the binary (reference, item 501 (b)(4)): %s; installed before %s after %s '
        '(expected %s); revision texts %s' % (res['installed_sha'], BIN_EXPECT, res['versions'], res['installed_before'],
                                              res['installed_after'], WANT, res['rev']))
    add('  env of the tag (KYTY_DIAG_*, KYTY_FIX_*, KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS): %s' % res['env'])
    add('  Shader translation cache lines %s; %s' % (res['stc'], res['warm_txt']))
    add('  entry line %s; first GuestOut line %s; scene change line %s; first scene frame n %s; hold (sum dt after it) %.1f s; '
        'frames >= 1 s after it %d (max dt_us %d) - REPORT' % (res['entry_line'], res['guest_first'], res['scene_change_line'],
                                                           res['first_scene_n'], res['hold_s'], res['k2_after'], res['dt_max_after']))
    add('  run record: %s' % asc(res['close_info']))
    add('  death markers (REPORT): %d %s; emulator stdout %s' % (len(res['death']), res['death'][:3],
                                                                'present' if res['stdout_present'] else 'MISSING'))
    add('  window: %s, Recovering Vulkan swapchain %d; GamePatch lines %d; cmask_fce_nohit b42=drawn lines %d; [Vulkan][E] %d; '
        'AsyncPipelines: skipped draw %d (reference)' % (res['win'] or 'none', res['recovering'], res['gamepatch'], res['drawn'],
                                                         res['vke'], res['skipped_draw']))
    add('  manifest: %s' % res['manifest'])
    add('  lines carrying DiagF5: %d, DiagF6: %d, FixF5Cmu: %d %s, DiagF5Id: %d (mode=1 %s, mode=0 %d), DiagF5Ev: %d (malformed %d)' % (
        res['f5_any'], res['f6_any'], res['fix_any'], res['fix_mode'], res['id_any'], res['id_mode'], res['id_mode0'], res['ev_any'],
        res['ev_bad']))
    f5 = res['f5']
    add('  F5 frame lines %d (malformed %d); mode lines %s (before the first GuestOut %s); identity violations %d %s; monotonicity '
        'violations %d %s; lines with f5cmu_* != 0: %d; F5 health (REPORT) %s' % (
            f5['lines'], f5['malformed'], f5['mode'], yn(f5['mode_ok']), f5['ident_bad_n'], f5['ident_bad'][:2], f5['mono_bad_n'],
            f5['mono_bad'][:2], f5['cmu_nonzero'], 'OK' if f5['health'] else 'NOT OK'))
    if f5['last'] is not None:
        add('  F5 last line (log line %d): frame=%d %s' % (f5['last_lineno'], f5['last']['frame'],
                                                          ' '.join('%s=%d' % (n, f5['last'][n]) for n in F5_NAMES)))
        add('  F5 f5cmu_*: %s; F26 (item 492 (g)(5)): %s; cmask_fce_b42=%d cmask_fce_unapplied=%d cmask_fce_meta=%d' % (
            ' '.join('%s=%d' % (n, res['cmu_last'][n]) for n in CMU), ' '.join('%s=%d' % (n, res['f26'][n]) for n in F26),
            f5['last']['cmask_fce_b42'], f5['last']['cmask_fce_unapplied'], f5['last']['cmask_fce_meta']))
    lim = res['limits']
    add('  DiagF5Ev: cmask_fce lines %d (limit exhausted %s), cmask_fce_nohit lines %d (limit exhausted %s); fix counts all %s; in scene %s'
        % (lim['fce_lines'], yn(lim['fce_exhausted']), lim['nohit_lines'], yn(lim['nohit_exhausted']), res['ev_counts'],
           res['ev_counts_scene']))
    for e in res['events']:
        add('  EVENT %s' % fmt_ev(e))
    if k in ('pair0', 'pair1'):
        add('  video: index records %s; one-frame glitches %s at presents %s; %s' % (res['idx_records'], res['glitches'],
                                                                                   res['glitch_presents'][:20], res['sheet']))
    if k == 'pair1' and 'id496_letter' in res:
        for name, a, b, ok in res['id496_letter']:
            add('  ID496 LETTER %s: lines %d counter %d %s' % (name, a, b, 'EQUAL' if ok else 'DIFFERENT'))
        for name, a, b, ok in res['id496_variant']:
            add('  ID496 VARIANT OF THE EXECUTOR (event lines before the last DiagF5 line) %s: lines %d counter %d %s' % (
                name, a, b, 'EQUAL' if ok else 'DIFFERENT'))
        add('  ID496 limit exhausted: %s' % yn(res['id496_limit']))
    if k == 'id':
        last = res['sum_last']
        add('  DiagF5Id sum lines %d (malformed sum/key lines %d; exit=1 lines %d); id violations %s; monotonicity violations %s' % (
            res['sum_lines'], res['sum_bad'], res['sum_exit'], res['id_bad_lines'], res['sum_mono_bad']))
        if last is not None:
            add('  DiagF5Id last sum (log line %d): frame=%d exit=%d %s %s id_fce=%s id_cs=%s' % (
                last['line'], last['frame'], last['exit'], ' '.join('%s=%d' % (n, last[n]) for n in ID_NAMES),
                ' '.join('%s=%d' % (n, last[n]) for n in SUM_TAIL), last['id_fce'], last['id_cs']))
            add('  stamp_late (item 496 (b)(3), 501 (b)(2)) = %d; meta_clear = %d' % (last['stamp_late'], last['meta_clear']))
        add('  printed lines: fce %d, cs %d, fce_next %d, stale_apply %d' % (res['fce_lines_n'], res['cs_lines_n'], len(res['next_lines']),
                                                                             len(res['stale_lines'])))
        for b in res['branch2']:
            add('  B2KEY base=0x%s dcc=0x%s reason=%s n=%d n_at_entry>=%d in_scene<=%d printed=%d (in scene %d) entry=%s clear_mask!=0=%s '
                'dcc_en=%s wr_after=%s cpu_mod=%s next=%s' % (
                    b['base'], b['dcc'], b['reason'], b['n'], b['n_at_entry'], b['in_scene'], b['printed'], b['printed_in_scene'],
                    ','.join(b['entry']), ','.join(str(x) for x in b['clear_mask_nonzero']), ','.join(b['dcc_en']),
                    ','.join(b['wr_after']), ','.join(b['cpu_mod']),
                    ' '.join('%s=%d' % kv_ for kv_ in sorted(b['next'].items())) if b['next'] else 'NO_KEY_LINE'))
        for b in res['branch3']:
            add('  B3KEY shader=0x%s addr=0x%s class=%s n=%d n_at_entry>=%d in_scene<=%d stale_apply=%s sub=%s vclass=%s entry=%s '
                'changed=%s mark=%s printed=%d' % (b['shader'], b['addr'], b['cls'], b['n'], b['n_at_entry'], b['in_scene'],
                                                   b['stale_apply'], ','.join(b['sub']), ','.join(b['vclass']), ','.join(b['entry']),
                                                   ','.join(b['changed']), ','.join(b['mark']), b['printed']))
        for d in res['stale_lines']:
            add('  STALE_APPLY %s' % ' '.join('%s=%s' % (kk, d[kk]) for kk in ('site', 'addr', 'image', 'shader', 'class', 'dframes', 'line',
                                                                                'scene') if kk in d))
        for d in res['next_lines']:
            add('  FCE_NEXT %s' % ' '.join('%s=%s' % (kk, d[kk]) for kk in ('base', 'kind', 'dframes', 'meta', 'cleared', 'buf_reads',
                                                                             'merged', 'line', 'scene') if kk in d))
    m = [('binary sha256 of the tag = d4328b0c (F16k2 copy; item 501 (b)(4))', res['sha_ok']),
         ('installed adb0c82f before the tag', res['before_ok']),
         ('installed adb0c82f after the return', res['after_ok']),
         ('env of the form %s' % k, res['env_ok']),
         ('entered (entry line of %s)' % res['level'], res['entry_line'] is not None),
         ('hold >= 300 s after the first scene frame', res['hold_len_ok']),
         ('the process lived through the hold (outcome ok, hold_exit null)', res['hold_ok']),
         ('manifest of the caches, saves and GLCache before = after the return', res['manifest_ok']),
         ('no interference: window minimized / Recovering Vulkan swapchain / GamePatch / b42=drawn line (item 273 (z), 501 (b)(1))',
          not res['interference'])]
    if k in ('pair0', 'pair1'):
        m.append(('video index records >= 3000', (res['idx_records'] or 0) >= VIDEO_MIN))
    for name, val in m:
        add('  ROW %s: %s' % (name, yn(val)))
    for name, val in res['control']:
        add('  ROW control: %s: %s' % (name, yn(val)))
    add('  CONTROL %s %s' % (k.upper(), 'ALIVE' if res['control_alive'] else 'DEAD'))
    return out


def main(argv):
    if '--dir' in argv:
        base = argv[argv.index('--dir') + 1]
        tag = argv[argv.index('--tag') + 1]
        p = paths(tag, base)
    else:
        tag = argv[0] if argv else ''
        p = paths(tag)
    if tag not in TAGS:
        raise SystemExit('unknown tag: %s' % tag)
    res = read(p, tag)
    print('\n'.join(asc(x) for x in rows(res)))
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w') as f:
            json.dump(res, f, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
