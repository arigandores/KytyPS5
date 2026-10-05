"""Track F link F16q (HPP-597; ROADMAP s122 items 504 (zh)-(z), 507 (b)(4), (v)-(g), 515 (v)): the reader of one tag of the F16o2 test
binary 7e4ded19 (KYTY_FIX_F5CMU / KYTY_FIX_F26 / KYTY_DIAG_F5ID / KYTY_DIAG_F5).  Rows only, no verdict (the reading is F16r's, HPP-598).
usage: python f16q_read.py <tag> [--json <out.json>]
       python f16q_read.py --dir <fixture dir> --tag <tag>   (fixture files: log.txt, stdout.txt, es.json, installed_sha.txt,
           installed_before.txt, installed_after.txt, warm.txt, manifest_cmp.txt, bin.exe, rec.idx, glitch.txt, sheet.txt, luma.txt)
tags (all enemy_final, form V of track F: -lvl entry, hold, video; the warm-up without video):
  f16q_w   warm-up, KYTY_DIAG_F5=1 KYTY_FIX_F5CMU=0 KYTY_FIX_F26=0, KYTY_DIAG_F5ID not set, no video - NOT READ (rows printed as a report)
  f5cmu_0b KYTY_DIAG_F5=1 KYTY_FIX_F5CMU=0 (KYTY_DIAG_F5ID, KYTY_FIX_F26 not set)            - pair A arm 0
  f5cmu_1b KYTY_DIAG_F5=1 KYTY_FIX_F5CMU=1 (KYTY_DIAG_F5ID, KYTY_FIX_F26 not set)            - pair A arm 1
  f26_0    KYTY_DIAG_F5=1 KYTY_DIAG_F5ID=1 KYTY_FIX_F26=0 (KYTY_FIX_F5CMU not set)           - pair B arm 0
  f26_1    KYTY_DIAG_F5=1 KYTY_DIAG_F5ID=1 KYTY_FIX_F26=1 (KYTY_FIX_F5CMU not set)           - pair B arm 1
Port of C:/kyty/f287/f16m/f16m_read.py (F16m HPP-585, seal 641ed1ed) with the lines of KytyPS5 365cc3c2
src/graphics/host_gpu/renderer/diagF5.cpp:
  'DiagF5: frame=<n> <name>=<value> ...'  64 counters in the order of F5Names (:159-:223): the 59 of F16k2, then f26_kept,
      f26_kept_applied, f26_exact_stale, f26_fallback (F16o) and f26_deferred_declined (F16o2, item 507 (b)(3)) - a line without the
      last field is malformed.
  'FixF5Cmu: mode=1' (:591); 'FixF26: mode=1' (:606); 'DiagF5Id: mode=1' (:790).
  'DiagF5Ev: cmask_fce n= present= gpu= image= cmask= extent=WxH applied= fix= [why=]' (:667), limit 1024 lines (:679, item 504 (e)(5));
  'DiagF5Ev: cmask_fce_nohit n= b42= present= gpu= image= cmask= extent=WxH fix= [why=]' (:687), limit 64 lines (:699);
  'DiagF5Ev: dcc_stale site=<prepare|adopt> n= present= gpu= image= dcc= extent=WxH exact=<stale|fresh|fallback|na>
      fix=<off|exact_stale|kept|kept_applied|fallback> [why=]' (:722), limit 256 lines (:737, item 504 (e)(3));
  'DiagF5Ev: dcc_stale_apply n= present= gpu= image= dcc= result=<cleared|declined> layers=0x<8 hex>' (:746), printed only when the n
      of its adopt line was printed (n <= 256, :753; item 507 (b)(3)).
Definitions (the seal docs/track-f/f16q.md section 4):
  in scene        a line after the first 'GuestOut: Level has started: enemy_final' line (flag scene/before of every event).
  LIMIT           a kind exhausted its line limit: cmask_fce - a line with n=1024, or cmask_fce_b42 + cmask_fce_unapplied > 1024 on the last
                  DiagF5 line; cmask_fce_nohit - a line with n=64; dcc_stale - a line with n=256, or on the arm with KYTY_FIX_F26=1
                  f26_kept + f26_exact_stale + f26_fallback > 256 on the last DiagF5 line.  An exhausted kind makes its identity rows LIMIT
                  (not a member, item 496 (b)(5)).
  identity 496    item 496 (b)(5) on f5cmu_1b, the cmask kinds only: lines with fix in {kept, kept_applied} = f5cmu_kept, kept_applied =
                  f5cmu_kept_applied, exact_stale = f5cmu_exact_stale, fallback = f5cmu_fallback; beyond the letter exact_stale why=cpu =
                  f5cmu_exact_cpu.  MEMBER: the VARIANT (event lines before the last DiagF5 frame line, item 502 (b)); the LETTER (the whole
                  log) is printed as a reference.
  identity 507    item 507 (b)(4) (replaces 504 (e)(4) in the part kept_applied) on f26_1, the dcc kinds: lines fix in {kept, kept_applied}
                  = f26_kept; lines fix=kept_applied (prepare) + lines result=cleared = f26_kept_applied; lines fix=exact_stale =
                  f26_exact_stale; lines fix=fallback = f26_fallback; lines result=declined = f26_deferred_declined; lines site=adopt
                  fix=kept_applied = 0.  MEMBER: the VARIANT (lines before the last DiagF5 line, the form of item 502 (b)); LETTER printed.
                  On EVERY DiagF5 line (member): f26_kept_applied + f26_deferred_declined <= f26_kept; on f26_1 (KYTY_DIAG_F5ID=1)
                  f26_kept = dcc_stale_bucket_only; on f26_0 and the pair A arms all f26_* = 0.
  apply_late      item 515 (v)(1): a dcc_stale_apply line result=cleared whose present or gpu differs from the dcc_stale site=adopt line
                  of the same n; printed with its pairs (n, present/gpu of the event and of the outcome); a subset of result=cleared - the
                  identity 507 counts them as before (515 (v)(3)).
  pair controls   item 504 (zh): f5cmu_1b 'FixF5Cmu: mode=1' before the first GuestOut, f5cmu_0b 0 lines 'FixF5Cmu:'; cmask_fce lines >= 1 in
                  both; identity 496 (f5cmu_1b); f5cmu_kept_applied <= f5cmu_kept, f5cmu_exact_cpu <= f5cmu_exact_stale on every line;
                  f5cmu_0b every cmask event fix=off, 0 nohit lines, f5cmu_* = 0 on every line; both: 0 lines 'DiagF5Id:', 0 lines
                  'FixF26:', f26_* = 0 on every line, every dcc_stale line fix=off, 0 lines dcc_stale_apply (KYTY_FIX_F26 not set).
  f26 controls    item 504 (zh), 507 (b)(4): f26_1 'FixF26: mode=1' before the first GuestOut, f26_0 0 lines 'FixF26:'; dcc_stale lines >= 1
                  in both; identity 507 (f26_1) and the frame-line identities; f26_0 every dcc_stale line fix=off, 0 lines dcc_stale_apply;
                  both: 'DiagF5Id: mode=1' before the first GuestOut (KYTY_DIAG_F5ID=1), 0 lines 'FixF5Cmu:', f5cmu_* = 0 on every line.
  admission rows  the tag binary 7e4ded19 by sha256 (item 507 (g)); installed FS6 9325446c before and after; env of the tag form (no other
                  KYTY_FIX_*, no KYTY_SKIP_CEILING and no 'skipceil' in the gate text - item 515 N1); entry line of enemy_final; hold (sum
                  dt_us of FrameTrace rows after the first row with draws >= 100 after the entry, before a scene change) >= 300 s; the
                  process lived through the hold; manifest cmp EQUAL; no interference (window minimized, Recovering Vulkan swapchain,
                  GamePatch line, cmask_fce_nohit b42=drawn line); video tags: index records >= 3000.  Frames >= 1 s, death markers,
                  [Vulkan][E], skipped draw lines, one-frame glitches, the present of the first scene frame (luma.txt) - REPORT rows.
ASCII output only."""
import hashlib, json, os, re, sys

G = 'C:/kyty/f287/f16q'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_7e4ded19.exe'
BIN_EXPECT = '7e4ded19f577cc9b03b2443111f40ac701a29d6234ffa3d3c9c64f4475a58fcb'
VERSIONS = (b'KytyPS5-2026-09-15-6a2987a-2264-g365cc3c2', b'KytyPS5-2026-09-15-6a2987a-2225-gc0789a34')
WANT = '9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2'
DIR_FIX = 'variant_fixb26_fixb1b_fixf10'
LEVEL = 'enemy_final'
TAGS = {'f16q_w': (LEVEL, 'warm'), 'f5cmu_0b': (LEVEL, 'pair0'), 'f5cmu_1b': (LEVEL, 'pair1'),
        'f26_0': (LEVEL, 'f26_0'), 'f26_1': (LEVEL, 'f26_1')}
F5_NAMES = ['rt_resolves', 'dcc_rt', 'rtcheck_meta', 'dcc_rt_pending', 'dcc_rt_cleared', 'dcc_rt_skip_levels', 'dcc_rt_skip_partial',
            'dcc_rt_skip_decode', 'dcc_rt_skip_layers', 'dcc_mat_pending', 'dcc_mat_cleared', 'dcc_mat_undecoded', 'dcc_fce',
            'dcc_fce_image', 'dcc_fce_no_image', 'dcc_fill_all', 'dcc_fill_meta', 'dcc_fill_clear', 'dcc_fill_uncompressed',
            'dcc_fill_unknown', 'dcc_reset_stale', 'dcc_reset_type', 'meta_refused_known', 'meta_cs_tracked', 'meta_cs_untracked',
            'meta_dma_untracked', 'meta_dma_noclear', 'cmask_rt_pending', 'cmask_rt_cleared', 'cmask_rt_skip_value',
            'cmask_rt_skip_partial', 'cmask_rt_skip_decode', 'cmask_rt_skip_layers', 'cmask_fce', 'cmask_fce_noimage', 'cmask_fce_meta',
            'cmask_fce_msaa', 'cmask_fce_layout', 'cmask_fce_nofill', 'cmask_fce_drawn', 'cmask_fce_b42', 'cmask_fce_unapplied',
            'fmask_read', 'round_unorm', 'round_float', 'round_other', 'ds_unbound', 'ds_unbound_clear', 'stereo_writes',
            'stereo_nonzero', 'zero_disp', 'f5cmu_kept', 'f5cmu_kept_applied', 'f5cmu_exact_stale', 'f5cmu_fallback',
            'dcc_stale_bucket_only', 'dcc_stale_fallback', 'cmask_rt_bucket_only', 'f5cmu_exact_cpu',
            'f26_kept', 'f26_kept_applied', 'f26_exact_stale', 'f26_fallback', 'f26_deferred_declined']
CMU = ['f5cmu_kept', 'f5cmu_kept_applied', 'f5cmu_exact_stale', 'f5cmu_fallback', 'f5cmu_exact_cpu']
F26C = ['f26_kept', 'f26_kept_applied', 'f26_exact_stale', 'f26_fallback', 'f26_deferred_declined']
F26R = ['dcc_stale_bucket_only', 'dcc_stale_fallback', 'cmask_rt_bucket_only']
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
LIM_FCE = 1024
LIM_NOHIT = 64
LIM_DCC = 256
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_F5 = re.compile(rb'DiagF5: frame=(\d+)' + b''.join(rb' ' + n.encode() + rb'=(\d+)' for n in F5_NAMES) + rb'(?=\s|$)')
RX_EV = re.compile(rb'DiagF5Ev: cmask_fce n=(\d+) present=(\d+) gpu=(\d+) image=0x([0-9a-f]+) cmask=0x([0-9a-f]+) extent=(\d+)x(\d+) '
                   rb'applied=([01]) fix=([a-z_]+)(?: why=([a-z]+))?\s*$')
RX_NH = re.compile(rb'DiagF5Ev: cmask_fce_nohit n=(\d+) b42=(none|drawn) present=(\d+) gpu=(\d+) image=0x([0-9a-f]+) cmask=0x([0-9a-f]+) '
                   rb'extent=(\d+)x(\d+) fix=([a-z_]+)(?: why=([a-z]+))?\s*$')
RX_DS = re.compile(rb'DiagF5Ev: dcc_stale site=(prepare|adopt) n=(\d+) present=(\d+) gpu=(\d+) image=0x([0-9a-f]+) dcc=0x([0-9a-f]+) '
                   rb'extent=(\d+)x(\d+) exact=(stale|fresh|fallback|na) fix=([a-z_]+)(?: why=([a-z]+))?\s*$')
RX_DA = re.compile(rb'DiagF5Ev: dcc_stale_apply n=(\d+) present=(\d+) gpu=(\d+) image=0x([0-9a-f]+) dcc=0x([0-9a-f]+) '
                   rb'result=(cleared|declined) layers=0x([0-9a-f]{8})\s*$')
RX_SUM = re.compile(rb'DiagF5Id: sum frame=(\d+) exit=([01])' + b''.join(rb' ' + n.encode() + rb'=(\d+)' for n in ID_NAMES + SUM_TAIL)
                    + rb' id_fce=(ok|bad) id_cs=(ok|bad)\s*$')
RX_SKIP = re.compile(rb'(AsyncPipelines|BindFloor): skipped draw \S* ?frame=(\d+)')
M_START = b'GuestOut: Level has started: '
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
K2_US = 1000000
HOLD_MIN_US = 300000000
VIDEO_MIN = 3000
RX_GL = re.compile(r'one-frame glitches: (\d+)')
RX_GLP = re.compile(r'video\s+(\d+) present\s+(\d+)')


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


def ident_f26(d, kind):
    """item 504 (e)(4) / 507 (b)(4) on one DiagF5 line."""
    bad = []
    if d['f26_kept_applied'] + d['f26_deferred_declined'] > d['f26_kept']:
        bad.append('f26_kept_applied+f26_deferred_declined=%d > f26_kept=%d' % (d['f26_kept_applied'] + d['f26_deferred_declined'],
                                                                                 d['f26_kept']))
    if kind == 'f26_1':
        if d['f26_kept'] != d['dcc_stale_bucket_only']:
            bad.append('f26_kept=%d != dcc_stale_bucket_only=%d' % (d['f26_kept'], d['dcc_stale_bucket_only']))
    elif any(d[n] for n in F26C):
        bad.append('f26_* != 0 (%s)' % ' '.join('%s=%d' % (n, d[n]) for n in F26C if d[n]))
    return bad


class Series(object):
    """The DiagF5 frame lines: count, malformed, identities on every line, monotonicity, f5cmu_* / f26_* nonzero lines, the last line."""

    def __init__(self, kind):
        self.kind = kind
        self.lines = self.malformed = 0
        self.mode = []
        self.ident_bad = []
        self.f26_bad = []
        self.mono_bad = []
        self.cmu_nonzero = 0
        self.f26_nonzero = 0
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
        bad = ident_f26(d, self.kind)
        if bad:
            self.f26_bad.append((self.lines, ln, bad[:3]))
        if any(d[n] for n in CMU):
            self.cmu_nonzero += 1
        if any(d[n] for n in F26C):
            self.f26_nonzero += 1
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
    """One DiagF5Ev line -> dict (kind fce / nohit / dcc / apply), or None when malformed."""
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
    m = RX_DS.search(raw)
    if m:
        g = m.groups()
        return dict(kind='dcc', site=g[0].decode(), n=int(g[1]), present=int(g[2]), gpu=int(g[3]), image=g[4].decode(),
                    dcc=g[5].decode(), extent='%sx%s' % (g[6].decode(), g[7].decode()), exact=g[8].decode(), fix=g[9].decode(),
                    why=g[10].decode() if g[10] else None)
    m = RX_DA.search(raw)
    if m:
        g = m.groups()
        return dict(kind='apply', n=int(g[0]), present=int(g[1]), gpu=int(g[2]), image=g[3].decode(), dcc=g[4].decode(),
                    result=g[5].decode(), layers=g[6].decode(), fix=None, why=None)
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
    """The identities (g)(4) of item 492 recounted from the fields of a sum line (REPORT here)."""
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


def scan(log_path, level, kind):
    r = dict(lines=0, rev=[], stc=[], guest_first=None, entry_line=None, scene_change_line=None, first_scene_n=None, hold_us=0,
             k2_after=0, dt_max_after=0, ft_rows=0, death=[], skipped_draw=0, skips=[], win={}, recovering=0, gamepatch=0, vke=0,
             f5_any=0, fix_mode=[], fix_any=0, f26_mode=[], f26_any=0, id_mode=[], id_any=0, ev=[], ds=[], da=[], ev_bad=0, ev_any=0,
             sums=[], sum_bad=0)
    s5 = Series(kind)
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
            if b'FixF5Cmu:' in raw:
                r['fix_any'] += 1
                if b'FixF5Cmu: mode=1' in raw:
                    r['fix_mode'].append(ln)
            if b'FixF26:' in raw:
                r['f26_any'] += 1
                if b'FixF26: mode=1' in raw:
                    r['f26_mode'].append(ln)
            if b'DiagF5Ev:' in raw:
                r['ev_any'] += 1
                e = parse_event(raw)
                if e is None:
                    r['ev_bad'] += 1
                else:
                    e['line'] = ln
                    e['scene'] = scene
                    if e['kind'] in ('fce', 'nohit'):
                        r['ev'].append(e)
                    elif e['kind'] == 'dcc':
                        r['ds'].append(e)
                    else:
                        r['da'].append(e)
            if b'DiagF5Id:' in raw:
                r['id_any'] += 1
                if b'DiagF5Id: mode=1' in raw:
                    r['id_mode'].append(ln)
                elif b'DiagF5Id: sum ' in raw:
                    d = parse_sum(raw)
                    if d is None:
                        r['sum_bad'] += 1
                    else:
                        d['line'] = ln
                        r['sums'].append(d)
            if b'skipped draw' in raw:
                m = RX_SKIP.search(raw)
                if m:
                    r['skips'].append((ln, m.group(1).decode(), int(m.group(2))))
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
    names = ('installed_sha', 'installed_before', 'installed_after', 'warm', 'manifest_cmp', 'glitch', 'sheet', 'luma')
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


def env_ok_of(env, kind, gates):
    mine = ('KYTY_FIX_F5CMU', 'KYTY_FIX_F26')
    other_fix = sorted(k for k in env if k.startswith('KYTY_FIX_') and k not in mine)
    ok = (other_fix == [] and 'KYTY_GAME_PATCH' not in env and 'KYTY_GPU_CHECKPOINTS' not in env and 'KYTY_DIAG_F6' not in env
          and 'KYTY_SKIP_CEILING' not in env and 'skipceil' not in (gates or '') and env.get('KYTY_DIAG_F5') == '1')
    if kind == 'warm':
        return (ok and env.get('KYTY_FIX_F5CMU') == '0' and env.get('KYTY_FIX_F26') == '0' and 'KYTY_DIAG_F5ID' not in env)
    if kind == 'pair0':
        return ok and env.get('KYTY_FIX_F5CMU') == '0' and 'KYTY_DIAG_F5ID' not in env and 'KYTY_FIX_F26' not in env
    if kind == 'pair1':
        return ok and env.get('KYTY_FIX_F5CMU') == '1' and 'KYTY_DIAG_F5ID' not in env and 'KYTY_FIX_F26' not in env
    want = '0' if kind == 'f26_0' else '1'
    return ok and env.get('KYTY_DIAG_F5ID') == '1' and env.get('KYTY_FIX_F26') == want and 'KYTY_FIX_F5CMU' not in env


def ev_counts(evs):
    c = dict((f, 0) for f in FIXES)
    for e in evs:
        c[e['fix']] = c.get(e['fix'], 0) + 1
    return c


def identity496(evs, last):
    """item 496 (b)(5): cmask event line counts by fix against the f5cmu_* counters of the frame line `last`."""
    c = ev_counts(evs)
    cpu = len([e for e in evs if e['fix'] == 'exact_stale' and e['why'] == 'cpu'])
    rows = [('kept+kept_applied = f5cmu_kept', c['kept'] + c['kept_applied'], last['f5cmu_kept']),
            ('kept_applied = f5cmu_kept_applied', c['kept_applied'], last['f5cmu_kept_applied']),
            ('exact_stale = f5cmu_exact_stale', c['exact_stale'], last['f5cmu_exact_stale']),
            ('fallback = f5cmu_fallback', c['fallback'], last['f5cmu_fallback']),
            ('exact_stale why=cpu = f5cmu_exact_cpu (beyond the letter)', cpu, last['f5cmu_exact_cpu'])]
    return [(n, a, b, a == b) for n, a, b in rows]


def identity507(ds, da, last):
    """item 507 (b)(4): dcc_stale / dcc_stale_apply line counts against the f26_* counters of the frame line `last`."""
    c = ev_counts(ds)
    ka_prep = len([e for e in ds if e['fix'] == 'kept_applied' and e['site'] == 'prepare'])
    ka_adopt = len([e for e in ds if e['fix'] == 'kept_applied' and e['site'] == 'adopt'])
    cleared = len([a for a in da if a['result'] == 'cleared'])
    declined = len([a for a in da if a['result'] == 'declined'])
    rows = [('kept+kept_applied = f26_kept', c['kept'] + c['kept_applied'], last['f26_kept']),
            ('kept_applied(prepare)+cleared = f26_kept_applied', ka_prep + cleared, last['f26_kept_applied']),
            ('exact_stale = f26_exact_stale', c['exact_stale'], last['f26_exact_stale']),
            ('fallback = f26_fallback', c['fallback'], last['f26_fallback']),
            ('declined = f26_deferred_declined', declined, last['f26_deferred_declined']),
            ('site=adopt fix=kept_applied = 0', ka_adopt, 0)]
    return [(n, a, b, a == b) for n, a, b in rows]


def apply_join(ds, da):
    """item 507 (v) with 515 (v): every dcc_stale_apply line with its adopt line of the same n; apply_late = result=cleared with present or
    gpu differing from the adopt line; an apply line without an adopt line of its n is listed (orphan)."""
    adopt = {}
    for e in ds:
        if e['site'] == 'adopt':
            adopt.setdefault(e['n'], e)
    out = []
    for a in da:
        e = adopt.get(a['n'])
        late = None if e is None else (a['result'] == 'cleared' and (a['present'] != e['present'] or a['gpu'] != e['gpu']))
        out.append(dict(n=a['n'], result=a['result'], present=a['present'], gpu=a['gpu'], layers=a['layers'], line=a['line'],
                        ev_present=e['present'] if e else None, ev_gpu=e['gpu'] if e else None, ev_why=e['why'] if e else None,
                        ev_fix=e['fix'] if e else None, orphan=e is None, late=bool(late)))
    return out


def limit_state(evs, ds, last, kind):
    fce_n = len([e for e in evs if e['kind'] == 'fce'])
    nh_n = len([e for e in evs if e['kind'] == 'nohit'])
    fce_ex = any(e['kind'] == 'fce' and e['n'] >= LIM_FCE for e in evs) or (
        last is not None and last['cmask_fce_b42'] + last['cmask_fce_unapplied'] > LIM_FCE)
    nh_ex = any(e['kind'] == 'nohit' and e['n'] >= LIM_NOHIT for e in evs)
    dcc_ex = any(e['n'] >= LIM_DCC for e in ds) or (
        kind == 'f26_1' and last is not None and last['f26_kept'] + last['f26_exact_stale'] + last['f26_fallback'] > LIM_DCC)
    return dict(fce_lines=fce_n, nohit_lines=nh_n, dcc_lines=len(ds), fce_exhausted=fce_ex, nohit_exhausted=nh_ex, dcc_exhausted=dcc_ex)


def mode_ok(lines, guest_first):
    return len(lines) >= 1 and (guest_first is None or lines[0] < guest_first)


def read(p, tag):
    level, kind = TAGS[tag]
    r, s5 = scan(p['log'], level, kind)
    sd, ssha = stdout_scan(p['stdout'])
    rj = text(p['run'])
    run = json.loads(rj) if rj else None
    att = ((run or {}).get('attempts') or [{}])[0] if run else None
    env = (run or {}).get('env') or {}
    gates = (run or {}).get('gates')
    sha, sha_b, sha_a = [first_line(text(p[k])) or None for k in ('installed_sha', 'installed_before', 'installed_after')]
    warm_t = text(p['warm'])
    mc = text(p['manifest_cmp'])
    env_ok = None if run is None else env_ok_of(env, kind, gates)
    hold_ok = None if att is None else (att.get('outcome') == 'ok' and att.get('hold_exit') is None)
    close_info = None if att is None else ('outcome %s hold_exit %s hold_s %s close_rc %s close_killed %s' % (
        att.get('outcome'), att.get('hold_exit'), att.get('hold_s'), att.get('close_rc'), att.get('close_killed')))
    L5 = s5.last
    evs, ds, da = r['ev'], r['ds'], r['da']
    res = dict(tag=tag, kind=kind, level=level, log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'], stdout_sha256=ssha,
               rev=r['rev'][:6], installed_sha=sha, installed_before=sha_b, installed_after=sha_a, sha_ok=sha == BIN_EXPECT,
               versions=bin_versions(p['bin']), before_ok=sha_b == WANT, after_ok=sha_a == WANT,
               env=dict((k, env[k]) for k in sorted(env) if k.startswith('KYTY_FIX_') or k.startswith('KYTY_DIAG_')
                        or k in ('KYTY_GAME_PATCH', 'KYTY_GPU_CHECKPOINTS', 'KYTY_SKIP_CEILING')), env_ok=env_ok,
               gates=(gates or '')[:200], stc=r['stc'][:3], warm_txt=(warm_t or '').strip()[:240],
               guest_first=r['guest_first'], entry_line=r['entry_line'], scene_change_line=r['scene_change_line'],
               first_scene_n=r['first_scene_n'], hold_s=round(r['hold_us'] / 1e6, 1), hold_len_ok=r['hold_us'] >= HOLD_MIN_US,
               k2_after=r['k2_after'], dt_max_after=r['dt_max_after'], hold_ok=hold_ok, close_info=close_info,
               death=r['death'] + (sd or []), stdout_present=sd is not None, vke=r['vke'], skipped_draw=r['skipped_draw'],
               skips=r['skips'], win=r['win'], recovering=r['recovering'], gamepatch=r['gamepatch'],
               manifest=first_line(mc)[:200], manifest_ok=bool(mc) and mc.startswith('manifest cmp EQUAL'),
               f5_any=r['f5_any'], fix_any=r['fix_any'], fix_mode=r['fix_mode'][:3], f26_any=r['f26_any'], f26_mode=r['f26_mode'][:3],
               id_any=r['id_any'], id_mode=r['id_mode'][:3], ev_any=r['ev_any'], ev_bad=r['ev_bad'], events=evs, dcc=ds, apply=da,
               drawn=len([e for e in evs if e['b42'] == 'drawn']),
               f5=dict(mode=s5.mode[:3], lines=s5.lines, malformed=s5.malformed, ident_bad=s5.ident_bad[:5], ident_bad_n=len(s5.ident_bad),
                       f26_bad=s5.f26_bad[:5], f26_bad_n=len(s5.f26_bad), mono_bad=s5.mono_bad[:5], mono_bad_n=len(s5.mono_bad),
                       cmu_nonzero=s5.cmu_nonzero, f26_nonzero=s5.f26_nonzero, last=L5, last_lineno=s5.last_lineno,
                       mode_ok=mode_ok(s5.mode, r['guest_first'])))
    res['f5']['health'] = L5 is not None and s5.malformed == 0 and not s5.ident_bad and not s5.mono_bad
    res['f26r'] = dict((n, L5[n]) for n in F26R) if L5 else None
    res['f26_last'] = dict((n, L5[n]) for n in F26C) if L5 else None
    res['cmu_last'] = dict((n, L5[n]) for n in CMU) if L5 else None
    res['ev_counts'] = ev_counts(evs)
    res['ev_counts_scene'] = ev_counts([e for e in evs if e['scene']])
    res['dcc_counts'] = ev_counts(ds)
    res['dcc_counts_scene'] = ev_counts([e for e in ds if e['scene']])
    res['dcc_sites'] = dict((s, len([e for e in ds if e['site'] == s])) for s in ('prepare', 'adopt'))
    res['apply_counts'] = dict((x, len([a for a in da if a['result'] == x])) for x in ('cleared', 'declined'))
    res['joined'] = apply_join(ds, da)
    res['apply_late'] = [j for j in res['joined'] if j['late']]
    res['apply_orphan'] = [j for j in res['joined'] if j['orphan']]
    res['limits'] = limit_state(evs, ds, L5, kind)
    sums = r['sums']
    res['sum_lines'] = len(sums)
    res['sum_bad'] = r['sum_bad']
    res['sum_id_bad'] = len([s for s in sums if s['id_fce'] != 'ok' or s['id_cs'] != 'ok' or id_recount(s) != ('ok', 'ok')])
    res['stamp_late'] = sums[-1]['stamp_late'] if sums else None
    # video rows
    idx, idx_n = read_idx(p.get('idx'))
    gt = text(p.get('glitch'))
    gm = RX_GL.search(gt or '')
    res['idx_records'] = idx_n
    res['glitches'] = int(gm.group(1)) if gm else None
    res['glitch_presents'] = [int(x[1]) for x in RX_GLP.findall(gt or '')]
    res['sheet'] = first_line(text(p.get('sheet')))[:200]
    res['luma'] = [x.strip() for x in (text(p.get('luma')) or '').split('\n') if x.startswith('SCENE')][:3]
    # controls
    lim = res['limits']
    ctl = []
    if kind in ('pair0', 'pair1'):
        if kind == 'pair1':
            ctl.append(('FixF5Cmu: mode=1 before the first GuestOut', mode_ok(r['fix_mode'], r['guest_first'])))
        else:
            ctl.append(('0 lines FixF5Cmu:', r['fix_any'] == 0))
        ctl.append(('cmask_fce event lines >= 1, 0 malformed DiagF5Ev lines', lim['fce_lines'] >= 1 and r['ev_bad'] == 0))
        ctl.append(('a parseable DiagF5 frame line (64 fields), 0 malformed', L5 is not None and s5.malformed == 0))
        if kind == 'pair1':
            ctl.append(('f5cmu_kept_applied <= f5cmu_kept and f5cmu_exact_cpu <= f5cmu_exact_stale on every frame line',
                        L5 is not None and not [b for b in s5.ident_bad if any('f5cmu' in x for x in b[2])]))
            if L5 is not None:
                res['id496_letter'] = identity496(evs, L5)
                res['id496_variant'] = identity496([e for e in evs if e['line'] < s5.last_lineno], L5)
                res['id496_limit'] = lim['fce_exhausted'] or lim['nohit_exhausted']
                if res['id496_limit']:
                    ctl.append(('identity of item 496 (b)(5) - LIMIT exhausted, not a member', True))
                else:
                    ctl.append(('identity of item 496 (b)(5) (VARIANT: cmask event lines before the last DiagF5 line, item 502 (b)), '
                                '4 equalities', all(x[3] for x in res['id496_variant'][:4])))
        else:
            ctl.append(('every cmask event fix=off, 0 nohit lines', all(e['fix'] == 'off' for e in evs) and lim['nohit_lines'] == 0))
            ctl.append(('f5cmu_* = 0 on every frame line', L5 is not None and s5.cmu_nonzero == 0))
        ctl.append(('0 lines DiagF5Id: (KYTY_DIAG_F5ID not set)', r['id_any'] == 0))
        ctl.append(('0 lines FixF26: and f26_* = 0 on every frame line (KYTY_FIX_F26 not set)',
                    r['f26_any'] == 0 and L5 is not None and s5.f26_nonzero == 0))
        ctl.append(('every dcc_stale line fix=off, 0 lines dcc_stale_apply', all(e['fix'] == 'off' for e in ds) and len(da) == 0))
    elif kind in ('f26_0', 'f26_1'):
        if kind == 'f26_1':
            ctl.append(('FixF26: mode=1 before the first GuestOut', mode_ok(r['f26_mode'], r['guest_first'])))
        else:
            ctl.append(('0 lines FixF26:', r['f26_any'] == 0))
        ctl.append(('dcc_stale event lines >= 1, 0 malformed DiagF5Ev lines', lim['dcc_lines'] >= 1 and r['ev_bad'] == 0))
        ctl.append(('a parseable DiagF5 frame line (64 fields), 0 malformed', L5 is not None and s5.malformed == 0))
        ctl.append(('frame-line identities of item 507 (b)(4) on every DiagF5 line (%s)' % (
            'f26_kept_applied+f26_deferred_declined <= f26_kept, f26_kept = dcc_stale_bucket_only' if kind == 'f26_1'
            else 'all f26_* = 0'), L5 is not None and s5.f26_bad == []))
        if kind == 'f26_1':
            if L5 is not None:
                res['id507_letter'] = identity507(ds, da, L5)
                res['id507_variant'] = identity507([e for e in ds if e['line'] < s5.last_lineno],
                                                   [a for a in da if a['line'] < s5.last_lineno], L5)
                res['id507_limit'] = lim['dcc_exhausted']
                if res['id507_limit']:
                    ctl.append(('identity of item 507 (b)(4) - LIMIT exhausted, not a member', True))
                else:
                    ctl.append(('identity of item 507 (b)(4) (VARIANT: dcc lines before the last DiagF5 line), 6 equalities',
                                all(x[3] for x in res['id507_variant'])))
        else:
            ctl.append(('every dcc_stale line fix=off, 0 lines dcc_stale_apply', all(e['fix'] == 'off' for e in ds) and len(da) == 0))
        ctl.append(('DiagF5Id: mode=1 before the first GuestOut (KYTY_DIAG_F5ID=1)', mode_ok(r['id_mode'], r['guest_first'])))
        ctl.append(('0 lines FixF5Cmu: and f5cmu_* = 0 on every frame line (KYTY_FIX_F5CMU not set)',
                    r['fix_any'] == 0 and L5 is not None and s5.cmu_nonzero == 0))
    res['control'] = ctl
    res['control_alive'] = None if kind == 'warm' else all(v for _, v in ctl)
    res['interference'] = bool(r['win'].get('minimized') or r['recovering'] or r['gamepatch'] or res['drawn'])
    return res


def yn(v):
    if v is None:
        return 'NOT_READ'
    if isinstance(v, str):
        return v
    return 'YES' if v else 'NO'


def fmt_ev(e):
    if e['kind'] == 'dcc':
        return ('dcc_stale site=%s n=%d present=%d gpu=%d image=0x%s dcc=0x%s extent=%s exact=%s fix=%s why=%s line=%d %s' % (
            e['site'], e['n'], e['present'], e['gpu'], e['image'], e['dcc'], e['extent'], e['exact'], e['fix'], e['why'] or '-',
            e['line'], 'scene' if e['scene'] else 'before'))
    if e['kind'] == 'apply':
        return ('dcc_stale_apply n=%d present=%d gpu=%d image=0x%s dcc=0x%s result=%s layers=0x%s line=%d %s' % (
            e['n'], e['present'], e['gpu'], e['image'], e['dcc'], e['result'], e['layers'], e['line'], 'scene' if e['scene'] else 'before'))
    return ('%s n=%d b42=%s present=%d gpu=%d image=0x%s cmask=0x%s extent=%s applied=%s fix=%s why=%s line=%d %s' % (
        e['kind'], e['n'], e['b42'], e['present'], e['gpu'], e['image'], e['cmask'], e['extent'],
        '-' if e['applied'] is None else e['applied'], e['fix'], e['why'] or '-', e['line'], 'scene' if e['scene'] else 'before'))


def rows(res):
    tag, k = res['tag'], res['kind']
    out = ['F16Q %s kind %s level %s log sha256 %s lines %d stdout sha256 %s' % (tag, k, res['level'], res['log_sha256'],
                                                                              res['log_lines'], res['stdout_sha256'])]
    add = out.append
    if k == 'warm':
        add('  WARM-UP TAG (item 504 (zh)(1)): not read; the rows below are a report of the run')
    add('  binary: tag %s (expected %s); version strings in the binary (reference): %s; installed before %s after %s (expected %s); '
        'revision texts %s' % (res['installed_sha'], BIN_EXPECT, res['versions'], res['installed_before'], res['installed_after'], WANT,
                               res['rev']))
    add('  env of the tag (KYTY_DIAG_*, KYTY_FIX_*, KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS, KYTY_SKIP_CEILING): %s; gate text %r' % (
        res['env'], res['gates']))
    add('  Shader translation cache lines %s; %s' % (res['stc'], res['warm_txt']))
    add('  entry line %s; first GuestOut line %s; scene change line %s; first scene frame n %s; hold (sum dt after it) %.1f s; '
        'frames >= 1 s after it %d (max dt_us %d) - REPORT' % (res['entry_line'], res['guest_first'], res['scene_change_line'],
                                                           res['first_scene_n'], res['hold_s'], res['k2_after'], res['dt_max_after']))
    add('  run record: %s' % asc(res['close_info']))
    add('  death markers (REPORT): %d %s; emulator stdout %s' % (len(res['death']), res['death'][:3],
                                                                'present' if res['stdout_present'] else 'MISSING'))
    add('  window: %s, Recovering Vulkan swapchain %d; GamePatch lines %d; cmask_fce_nohit b42=drawn lines %d; [Vulkan][E] %d; '
        'skipped draw lines %d (AsyncPipelines %d) (reference)' % (res['win'] or 'none', res['recovering'], res['gamepatch'], res['drawn'],
                                                                   res['vke'], len(res['skips']), res['skipped_draw']))
    add('  manifest: %s' % res['manifest'])
    add('  lines carrying DiagF5: %d, FixF5Cmu: %d %s, FixF26: %d %s, DiagF5Id: %d (mode=1 %s), DiagF5Ev: %d (malformed %d)' % (
        res['f5_any'], res['fix_any'], res['fix_mode'], res['f26_any'], res['f26_mode'], res['id_any'], res['id_mode'], res['ev_any'],
        res['ev_bad']))
    f5 = res['f5']
    add('  F5 frame lines %d (malformed %d); mode lines %s (before the first GuestOut %s); identity violations %d %s; f26 identity '
        'violations %d %s; monotonicity violations %d %s; lines with f5cmu_* != 0: %d, with f26_* != 0: %d; F5 health (REPORT) %s' % (
            f5['lines'], f5['malformed'], f5['mode'], yn(f5['mode_ok']), f5['ident_bad_n'], f5['ident_bad'][:2], f5['f26_bad_n'],
            f5['f26_bad'][:2], f5['mono_bad_n'], f5['mono_bad'][:2], f5['cmu_nonzero'], f5['f26_nonzero'],
            'OK' if f5['health'] else 'NOT OK'))
    if f5['last'] is not None:
        add('  F5 last line (log line %d): frame=%d %s' % (f5['last_lineno'], f5['last']['frame'],
                                                          ' '.join('%s=%d' % (n, f5['last'][n]) for n in F5_NAMES)))
        add('  F5 f5cmu_*: %s; f26_*: %s; F26 reference: %s; cmask_fce_b42=%d cmask_fce_unapplied=%d' % (
            ' '.join('%s=%d' % (n, res['cmu_last'][n]) for n in CMU), ' '.join('%s=%d' % (n, res['f26_last'][n]) for n in F26C),
            ' '.join('%s=%d' % (n, res['f26r'][n]) for n in F26R), f5['last']['cmask_fce_b42'], f5['last']['cmask_fce_unapplied']))
    lim = res['limits']
    add('  LIMIT cmask_fce (n=%d): lines %d exhausted %s; LIMIT cmask_fce_nohit (n=%d): lines %d exhausted %s; LIMIT dcc_stale (n=%d): '
        'lines %d exhausted %s' % (LIM_FCE, lim['fce_lines'], yn(lim['fce_exhausted']), LIM_NOHIT, lim['nohit_lines'],
                                   yn(lim['nohit_exhausted']), LIM_DCC, lim['dcc_lines'], yn(lim['dcc_exhausted'])))
    add('  cmask fix counts all %s; in scene %s' % (res['ev_counts'], res['ev_counts_scene']))
    add('  dcc_stale sites %s; fix counts all %s; in scene %s; dcc_stale_apply %s' % (res['dcc_sites'], res['dcc_counts'],
                                                                                     res['dcc_counts_scene'], res['apply_counts']))
    add('  APPLY_LATE (item 515 (v)): %d lines%s; apply lines without an adopt line of their n: %d' % (
        len(res['apply_late']), ''.join(' [n=%d event present=%s gpu=%s outcome present=%d gpu=%d]' % (
            j['n'], j['ev_present'], j['ev_gpu'], j['present'], j['gpu']) for j in res['apply_late'][:32]), len(res['apply_orphan'])))
    for e in res['events'] + res['dcc'] + res['apply']:
        add('  EVENT %s' % fmt_ev(e))
    if k != 'warm':
        add('  video: index records %s; one-frame glitches %s at presents %s; %s' % (res['idx_records'], res['glitches'],
                                                                                   res['glitch_presents'][:20], res['sheet']))
        add('  first scene frame (REPORT, luma.txt): %s' % (res['luma'] or 'NOT_READ'))
    add('  DiagF5Id sum lines %d (malformed %d, identity (g)(4) violations %d - REPORT); stamp_late %s' % (
        res['sum_lines'], res['sum_bad'], res['sum_id_bad'], res['stamp_late']))
    if k == 'pair1' and 'id496_letter' in res:
        for name, a, b, ok in res['id496_variant']:
            add('  ID496 VARIANT (member; cmask event lines before the last DiagF5 line) %s: lines %d counter %d %s' % (
                name, a, b, 'EQUAL' if ok else 'DIFFERENT'))
        for name, a, b, ok in res['id496_letter']:
            add('  ID496 LETTER (reference; the whole log) %s: lines %d counter %d %s' % (name, a, b, 'EQUAL' if ok else 'DIFFERENT'))
        add('  ID496 limit exhausted: %s' % yn(res['id496_limit']))
    if k == 'f26_1' and 'id507_letter' in res:
        for name, a, b, ok in res['id507_variant']:
            add('  ID507 VARIANT (member; dcc lines before the last DiagF5 line) %s: lines %d counter %d %s' % (
                name, a, b, 'EQUAL' if ok else 'DIFFERENT'))
        for name, a, b, ok in res['id507_letter']:
            add('  ID507 LETTER (reference; the whole log) %s: lines %d counter %d %s' % (name, a, b, 'EQUAL' if ok else 'DIFFERENT'))
        add('  ID507 limit exhausted: %s' % yn(res['id507_limit']))
    m = [('binary sha256 of the tag = 7e4ded19 (F16o2 copy; item 507 (g), 515)', res['sha_ok']),
         ('installed FS6 9325446c before the tag', res['before_ok']),
         ('installed FS6 9325446c after the return', res['after_ok']),
         ('env of the form %s (no KYTY_SKIP_CEILING / skipceil, item 515 N1)' % k, res['env_ok']),
         ('entered (entry line of %s)' % res['level'], res['entry_line'] is not None),
         ('hold >= 300 s after the first scene frame', res['hold_len_ok']),
         ('the process lived through the hold (outcome ok, hold_exit null)', res['hold_ok']),
         ('manifest of the caches, saves and GLCache before = after the return', res['manifest_ok']),
         ('no interference: window minimized / Recovering Vulkan swapchain / GamePatch / b42=drawn line', not res['interference'])]
    if k != 'warm':
        m.append(('video index records >= 3000', (res['idx_records'] or 0) >= VIDEO_MIN))
    for name, val in m:
        add('  ROW %s: %s' % (name, yn(val)))
    for name, val in res['control']:
        add('  ROW control: %s: %s' % (name, yn(val)))
    if k != 'warm':
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
