"""Track F link F16f (HPP-523; ROADMAP s122 items 421 (g), 427 (b)-(zh), 433 (v)-(g), 458 (b)-(v), 470 (g), 482): the reader of one tag of
the F16d2 diagnostic binary 4ad735ad (KYTY_DIAG_F5 / KYTY_DIAG_F6).  Rows only, no verdict (the reading is F16g's, HPP-524).
usage: python f16f_read.py <f5_sg|f5_ef|f5_bh|f5_eb|f5_sg0> [--json <out.json>]
       python f16f_read.py --dir <fixture dir> --tag <tag>        (fixture files: log.txt, stdout.txt, es.json, installed_sha.txt,
           installed_before.txt, installed_after.txt, warm.txt, manifest_cmp.txt, bin.exe)
       python f16f_read.py --set <read.json> [<read.json> ...]  (facts over the tags for F16g; no verdict)
Port of C:/kyty/f287/fs6c/fs6c_read.py (FS6c HPP-557: binary, env, entry, hold, death, window, manifest rows) with the DiagF5 / DiagF6
reader of the seal docs/track-f/f16f.md section 4.
Line forms (KytyPS5 56b04817 src/graphics/host_gpu/renderer/diagF5.cpp:65-67, :140): 'DiagF5: mode=1', 'DiagF6: mode=1' once per process
at device creation; 'DiagF5: frame=<n> <name>=<value> ...' (51 counters in the order of F5_NAMES) and 'DiagF6: frame=<n> ...' (20, F6_NAMES)
printed by Service() on the GuestGpu thread from ONE copy of the counters (form (a) of item 470 (v)(1), k = 0 by construction, item 480).
Definitions:
  parseable line  the text from 'DiagF5: frame=' (or 'DiagF6: frame=') carries every name of its list in order with a decimal value;
                  otherwise the line is MALFORMED (counted; a malformed line counts as an identity not shown to hold).
  last line       the last parseable frame line of the log (the log is one process: enter_scene --attempts 1).
  identities      item 470 (g): violated if the relation is false on ANY line of the tag (no 'transient of the snapshot' row).
                  F5: the 7 families parent = sum of the children (item 427 (g)(1), F16d section 2) and dcc_rt <= rt_resolves,
                  stereo_nonzero <= stereo_writes, ds_unbound_clear <= ds_unbound (F16d section 2, RC12 '<=').
                  F6 (item 433 (v)(4)): s_bound+s_addr0_fmt+s_addr0_nofmt+s_mask0_addr+s_empty = 8*draws; h_bound = s_bound-bound_missing+
                  bound_extra; w_total = w_bound+w_mask0+w_addr0_fmt+w_addr0_nofmt+w_ge8; draws_idx+draws_auto+draws_ind+draws_mesh = draws;
                  ps_draws <= draws.
  monotone        every counter of a line >= the same counter of the previous parseable line, frame non-decreasing, and the sum
                  strictly grows (a line is printed only on growth, item 427 (e)).
  line_mismatch   F16a section 2.4 item 4 with the F16c amendments, as F16d section 2 lists them, on the last line L against the count C of
                  the journal line in the log:  meta [L.rtcheck_meta>=1] != [C('ignoring PS5 color metadata')>=1];  round [sum round_*>=1] !=
                  [C('ignoring PS5 color round mode')>=1];  ds [L.ds_unbound>=1] != [C('without a bound attachment')>=1];  stereo
                  min(L.stereo_writes,16) != C('ignoring indirect uc reg GE_STEREO_CNTL');  zero min(L.zero_disp,32) !=
                  C('skipping zero-sized dispatch');  fill min(L.dcc_fill_all,32) != C('GraphicsRenderDispatchDirect: metadata fill').
                  LETTER: C over the whole log.  VARIANT OF THE EXECUTOR: C over the log lines before the last DiagF5 frame line (the
                  journal line of an event after the last snapshot is not in L).  Both are printed; the control row reads the LETTER.
  F5 control      item 421 (g) with items 427 (d), (g) and 458 (v): 'DiagF5: mode=1' before the first line carrying 'GuestOut';
                  rt_resolves > 0; line_mismatch_* = 0 (all six); the identities hold on every line; monotone; cmask_fce_noimage = 0
                  (> 0 = violation of the family invariant, item 458 (v), 470 (b)); on f5_sg dcc_rt >= 1 and dcc_rt_pending >= 1.
  F6 control      item 433 (v): 'DiagF6: mode=1' before the first GuestOut; draws > 0, s_bound > 0, ps_draws > 0;
                  w_mask0 + w_addr0_fmt + w_addr0_nofmt > 0; the identities hold on every line; monotone; on f5_sg draws_mesh > 0.
  null control    f5_sg0: 0 lines carrying 'DiagF5:' and 0 lines carrying 'DiagF6:' (item 421 (g), 433 (v)).
  B set           item 427 (b) U {cmask_fce_layout} (item 458 (b)): 17 counters; their values of the last line are printed.
  reference       meta_dma_noclear; fmask_read (a lower bound, item 458 (g)); cmask_fce_drawn; parents = 0 (item 427 (g)); stereo_nonzero
                  (> 0 reopens member 5, item 421 (v)(5)); F6: w_addr0_fmt, bound_missing, bound_extra, w_ge8, s_addr0_fmt (inputs of
                  item 433 (v)(i)-(iv); the reading is F16g's).
  admission rows  the tag binary 4ad735ad by sha256 and version string; installed adb0c82f before and after; env: KYTY_DIAG_F5=1 and
                  KYTY_DIAG_F6=1 on the four diag tags, neither on f5_sg0, no KYTY_FIX_*, KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS; entry line
                  of the level; hold (sum dt_us of FrameTrace rows after the first row with draws >= 100 after the entry, before a scene
                  change) >= 300 s (f5_sg0: >= 60 s); the process lived through the hold; manifest cmp EQUAL; no interference (window
                  minimized, Recovering Vulkan swapchain, GamePatch line - item 273 (z)).  Frames >= 1 s and K2 on the entry and death
                  markers - REPORT rows, not members (item 427 (zh): interference of the run on a cold entry).
ASCII output only."""
import hashlib, json, os, re, sys

G = 'C:/kyty/f287/f16f'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_4ad735ad.exe'
BIN_EXPECT = '4ad735ad70b7504df85560dc6b6c2e3520f0256aa655a4ff4db03f71122b09f6'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1881-g4950557a'
WANT = 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421'
REV = '4950557'
DIR_FIX = 'variant_fixb26_fixb1b_fixf10'
TAGS = {'f5_sg': ('underwater_aerial_garden', 'diag'), 'f5_ef': ('enemy_final', 'diag'),
        'f5_bh': ('big_hand_pirate_island', 'diag'), 'f5_eb': ('ending_boss_after_credit', 'diag'),
        'f5_sg0': ('underwater_aerial_garden', 'null')}
SG = 'f5_sg'
F5_NAMES = ['rt_resolves', 'dcc_rt', 'rtcheck_meta', 'dcc_rt_pending', 'dcc_rt_cleared', 'dcc_rt_skip_levels', 'dcc_rt_skip_partial',
            'dcc_rt_skip_decode', 'dcc_rt_skip_layers', 'dcc_mat_pending', 'dcc_mat_cleared', 'dcc_mat_undecoded', 'dcc_fce',
            'dcc_fce_image', 'dcc_fce_no_image', 'dcc_fill_all', 'dcc_fill_meta', 'dcc_fill_clear', 'dcc_fill_uncompressed',
            'dcc_fill_unknown', 'dcc_reset_stale', 'dcc_reset_type', 'meta_refused_known', 'meta_cs_tracked', 'meta_cs_untracked',
            'meta_dma_untracked', 'meta_dma_noclear', 'cmask_rt_pending', 'cmask_rt_cleared', 'cmask_rt_skip_value',
            'cmask_rt_skip_partial', 'cmask_rt_skip_decode', 'cmask_rt_skip_layers', 'cmask_fce', 'cmask_fce_noimage', 'cmask_fce_meta',
            'cmask_fce_msaa', 'cmask_fce_layout', 'cmask_fce_nofill', 'cmask_fce_drawn', 'cmask_fce_b42', 'cmask_fce_unapplied',
            'fmask_read', 'round_unorm', 'round_float', 'round_other', 'ds_unbound', 'ds_unbound_clear', 'stereo_writes',
            'stereo_nonzero', 'zero_disp']
F6_NAMES = ['draws', 'draws_idx', 'draws_auto', 'draws_ind', 'draws_mesh', 'ps_draws', 's_bound', 's_addr0_fmt', 's_addr0_nofmt',
            's_mask0_addr', 's_empty', 'h_bound', 'bound_missing', 'bound_extra', 'w_total', 'w_bound', 'w_mask0', 'w_addr0_fmt',
            'w_addr0_nofmt', 'w_ge8']
FAMILIES = [('dcc_rt_pending', ['dcc_rt_cleared', 'dcc_rt_skip_levels', 'dcc_rt_skip_partial', 'dcc_rt_skip_decode', 'dcc_rt_skip_layers']),
            ('dcc_mat_pending', ['dcc_mat_cleared', 'dcc_mat_undecoded']),
            ('dcc_fce', ['dcc_fce_image', 'dcc_fce_no_image']),
            ('dcc_fill_meta', ['dcc_fill_clear', 'dcc_fill_uncompressed', 'dcc_fill_unknown']),
            ('meta_refused_known', ['meta_cs_tracked', 'meta_cs_untracked', 'meta_dma_untracked', 'meta_dma_noclear']),
            ('cmask_rt_pending', ['cmask_rt_cleared', 'cmask_rt_skip_value', 'cmask_rt_skip_partial', 'cmask_rt_skip_decode',
                                  'cmask_rt_skip_layers']),
            ('cmask_fce', ['cmask_fce_noimage', 'cmask_fce_meta', 'cmask_fce_msaa', 'cmask_fce_layout', 'cmask_fce_nofill',
                           'cmask_fce_drawn', 'cmask_fce_b42', 'cmask_fce_unapplied'])]
F5_LE = [('dcc_rt', 'rt_resolves'), ('stereo_nonzero', 'stereo_writes'), ('ds_unbound_clear', 'ds_unbound')]
B_SET = ['dcc_fill_unknown', 'dcc_rt_skip_levels', 'dcc_rt_skip_partial', 'dcc_rt_skip_decode', 'dcc_rt_skip_layers', 'dcc_mat_undecoded',
         'dcc_fce_no_image', 'meta_cs_untracked', 'meta_dma_untracked', 'cmask_rt_skip_value', 'cmask_rt_skip_partial',
         'cmask_rt_skip_decode', 'cmask_rt_skip_layers', 'cmask_fce_msaa', 'cmask_fce_nofill', 'cmask_fce_unapplied', 'cmask_fce_layout']
JOURNAL = [('meta', b'ignoring PS5 color metadata'), ('round', b'ignoring PS5 color round mode'), ('ds', b'without a bound attachment'),
           ('stereo', b'ignoring indirect uc reg GE_STEREO_CNTL'), ('zero', b'skipping zero-sized dispatch'),
           ('fill', b'GraphicsRenderDispatchDirect: metadata fill')]
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
M_START = b'GuestOut: Level has started: '
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
K2_US = 1000000
HOLD_MIN_US = {'diag': 300000000, 'null': 60000000}


def frame_rx(tag, names):
    return re.compile(tag + rb': frame=(\d+)' + b''.join(rb' ' + n.encode() + rb'=(\d+)' for n in names) + rb'(?=\s|$)')


RX5 = frame_rx(b'DiagF5', F5_NAMES)
RX6 = frame_rx(b'DiagF6', F6_NAMES)


def parse_frame(raw, key, rx, names):
    """dict of one frame line (frame + counters) or None when malformed."""
    i = raw.find(key)
    m = rx.match(raw, i) if i >= 0 else None
    if not m:
        return None
    v = [int(x) for x in m.groups()]
    d = dict(zip(names, v[1:]))
    d['frame'] = v[0]
    return d


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


def ident_f6(d):
    bad = []
    s = d['s_bound'] + d['s_addr0_fmt'] + d['s_addr0_nofmt'] + d['s_mask0_addr'] + d['s_empty']
    if s != 8 * d['draws']:
        bad.append('slot classes %d != 8*draws %d' % (s, 8 * d['draws']))
    h = d['s_bound'] - d['bound_missing'] + d['bound_extra']
    if d['h_bound'] != h:
        bad.append('h_bound %d != s_bound-bound_missing+bound_extra %d' % (d['h_bound'], h))
    w = d['w_bound'] + d['w_mask0'] + d['w_addr0_fmt'] + d['w_addr0_nofmt'] + d['w_ge8']
    if d['w_total'] != w:
        bad.append('w_total %d != export classes %d' % (d['w_total'], w))
    k = d['draws_idx'] + d['draws_auto'] + d['draws_ind'] + d['draws_mesh']
    if k != d['draws']:
        bad.append('draw kinds %d != draws %d' % (k, d['draws']))
    if d['ps_draws'] > d['draws']:
        bad.append('ps_draws %d > draws %d' % (d['ps_draws'], d['draws']))
    return bad


class Series(object):
    """The frame lines of one knob: count, malformed, identities on every line, monotonicity, the last line."""

    def __init__(self, names, ident):
        self.names, self.ident = names, ident
        self.lines = self.malformed = 0
        self.mode = []
        self.any_key = 0
        self.ident_bad = []
        self.mono_bad = []
        self.last = None
        self.last_lineno = None

    def add(self, d, ln):
        self.lines += 1
        if d is None:
            self.malformed += 1
            return
        bad = self.ident(d)
        if bad:
            self.ident_bad.append((self.lines, ln, bad[:3]))
        if self.last is not None:
            p = self.last
            dec = [n for n in self.names if d[n] < p[n]]
            if dec or d['frame'] < p['frame'] or sum(d[n] for n in self.names) <= sum(p[n] for n in self.names):
                self.mono_bad.append((self.lines, ln, dec[:3], d['frame'] < p['frame']))
        self.last = d
        self.last_lineno = ln


def rev_text(raw):
    for m in (M_FORK, M_GIT):
        if m in raw:
            return raw.split(m, 1)[1].split(b',', 1)[0].strip()[:80].decode('ascii', 'replace')
    return None


def scan(log_path, level):
    r = dict(lines=0, rev=[], stc=[], guest_first=None, entry_line=None, scene_change_line=None, first_scene_n=None, hold_us=0,
             k2_after=0, dt_max_after=0, ft_rows=0, death=[], skipped_draw=0, win={}, recovering=0, gamepatch=0, vke=0,
             journal=dict((k, []) for k, _ in JOURNAL), f5_any=0, f6_any=0)
    s5, s6 = Series(F5_NAMES, ident_f5), Series(F6_NAMES, ident_f6)
    h = hashlib.sha256()
    after_entry = in_scene = False
    if not log_path or not os.path.exists(log_path):
        r['sha256'] = None
        return r, s5, s6
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
            if b'DiagF5:' in raw:
                r['f5_any'] += 1
                if b'DiagF5: frame=' in raw:
                    s5.add(parse_frame(raw, b'DiagF5: frame=', RX5, F5_NAMES), ln)
                elif b'DiagF5: mode=1' in raw:
                    s5.mode.append(ln)
            if b'DiagF6:' in raw:
                r['f6_any'] += 1
                if b'DiagF6: frame=' in raw:
                    s6.add(parse_frame(raw, b'DiagF6: frame=', RX6, F6_NAMES), ln)
                elif b'DiagF6: mode=1' in raw:
                    s6.mode.append(ln)
            for k, pat in JOURNAL:
                c = raw.count(pat)
                if c:
                    r['journal'][k].extend([ln] * c)
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
    return r, s5, s6


def mismatch(L, journal, upto):
    """line_mismatch_* of item 421 (g) on the last F5 line L; upto = None (LETTER, whole log) or a line number (VARIANT)."""
    def c(k):
        return len([x for x in journal[k] if upto is None or x < upto])
    rnd = L['round_unorm'] + L['round_float'] + L['round_other']
    return dict(meta=int((L['rtcheck_meta'] >= 1) != (c('meta') >= 1)), round=int((rnd >= 1) != (c('round') >= 1)),
                ds=int((L['ds_unbound'] >= 1) != (c('ds') >= 1)), stereo=int(min(L['stereo_writes'], 16) != c('stereo')),
                zero=int(min(L['zero_disp'], 32) != c('zero')), fill=int(min(L['dcc_fill_all'], 32) != c('fill')),
                counts=dict((k, c(k)) for k, _ in JOURNAL))


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


def bin_version(path):
    if not path or not os.path.exists(path):
        return None
    return VERSION in open(path, 'rb').read()


def paths(tag, base=None):
    names = ('installed_sha', 'installed_before', 'installed_after', 'warm', 'manifest_cmp')
    if base is not None:
        p = dict((n, os.path.join(base, n + '.txt')) for n in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 bin=os.path.join(base, 'bin.exe'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((n, os.path.join(d, n + '.txt')) for n in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             bin=BIN_PATH)
    return p


def mode_ok(series, guest_first):
    return len(series.mode) >= 1 and (guest_first is None or series.mode[0] < guest_first)


def read(p, tag):
    level, kind = TAGS[tag]
    r, s5, s6 = scan(p['log'], level)
    sd, ssha = stdout_scan(p['stdout'])
    rj = text(p['run'])
    run = json.loads(rj) if rj else None
    att = ((run or {}).get('attempts') or [{}])[0] if run else None
    env = (run or {}).get('env') or {}
    sha, sha_b, sha_a = [first_line(text(p[k])) or None for k in ('installed_sha', 'installed_before', 'installed_after')]
    warm_t = text(p['warm'])
    mc = text(p['manifest_cmp'])
    fix_keys = sorted(k for k in env if k.startswith('KYTY_FIX_'))
    if run is None:
        env_ok = None
    else:
        env_ok = fix_keys == [] and 'KYTY_GAME_PATCH' not in env and 'KYTY_GPU_CHECKPOINTS' not in env
        if kind == 'diag':
            env_ok = env_ok and env.get('KYTY_DIAG_F5') == '1' and env.get('KYTY_DIAG_F6') == '1'
        else:
            env_ok = env_ok and 'KYTY_DIAG_F5' not in env and 'KYTY_DIAG_F6' not in env
    hold_ok = None if att is None else (att.get('outcome') == 'ok' and att.get('hold_exit') is None)
    close_info = None if att is None else ('outcome %s hold_exit %s hold_s %s close_rc %s close_killed %s' % (
        att.get('outcome'), att.get('hold_exit'), att.get('hold_s'), att.get('close_rc'), att.get('close_killed')))
    stc = r['stc']
    res = dict(tag=tag, kind=kind, level=level, log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'], stdout_sha256=ssha,
               rev=r['rev'][:6], rev_row='NOT_PRESENT' if not r['rev'] else ('YES' if all(REV in t for _, _, t in r['rev']) else 'NO'),
               installed_sha=sha, installed_before=sha_b, installed_after=sha_a, sha_ok=sha == BIN_EXPECT,
               version_ok=bin_version(p['bin']), before_ok=sha_b == WANT, after_ok=sha_a == WANT,
               env=dict((k, env[k]) for k in sorted(env) if k.startswith('KYTY_FIX_') or k.startswith('KYTY_DIAG_')
                        or k in ('KYTY_GAME_PATCH', 'KYTY_GPU_CHECKPOINTS')), env_ok=env_ok,
               stc=stc[:3], dir_ok=len(stc) >= 1 and all(s.replace('/', '\\').endswith('\\' + DIR_FIX) for s in stc),
               warm_txt=(warm_t or '').strip()[:240], warm_ok=bool(warm_t) and ' present at ' in warm_t,
               guest_first=r['guest_first'], entry_line=r['entry_line'], scene_change_line=r['scene_change_line'],
               first_scene_n=r['first_scene_n'], hold_s=round(r['hold_us'] / 1e6, 1), hold_min_s=HOLD_MIN_US[kind] // 1000000,
               hold_len_ok=r['hold_us'] >= HOLD_MIN_US[kind], k2_after=r['k2_after'], dt_max_after=r['dt_max_after'],
               hold_ok=hold_ok, close_info=close_info, death=r['death'] + (sd or []), stdout_present=sd is not None,
               vke=r['vke'], skipped_draw=r['skipped_draw'], win=r['win'], recovering=r['recovering'], gamepatch=r['gamepatch'],
               manifest=first_line(mc)[:200], manifest_ok=bool(mc) and mc.startswith('manifest cmp EQUAL'),
               f5_any=r['f5_any'], f6_any=r['f6_any'],
               f5=dict(mode=s5.mode[:3], mode_n=len(s5.mode), lines=s5.lines, malformed=s5.malformed, ident_bad=s5.ident_bad[:5],
                       ident_bad_n=len(s5.ident_bad), mono_bad=s5.mono_bad[:5], mono_bad_n=len(s5.mono_bad), last=s5.last,
                       last_lineno=s5.last_lineno),
               f6=dict(mode=s6.mode[:3], mode_n=len(s6.mode), lines=s6.lines, malformed=s6.malformed, ident_bad=s6.ident_bad[:5],
                       ident_bad_n=len(s6.ident_bad), mono_bad=s6.mono_bad[:5], mono_bad_n=len(s6.mono_bad), last=s6.last,
                       last_lineno=s6.last_lineno))
    L5, L6 = s5.last, s6.last
    res['f5']['mode_ok'] = mode_ok(s5, r['guest_first'])
    res['f6']['mode_ok'] = mode_ok(s6, r['guest_first'])
    if L5 is not None:
        mm = mismatch(L5, r['journal'], None)
        mv = mismatch(L5, r['journal'], s5.last_lineno)
        res['f5']['mismatch_letter'] = mm
        res['f5']['mismatch_variant'] = mv
        res['f5']['b'] = dict((n, L5[n]) for n in B_SET)
        res['f5']['b_sum'] = sum(L5[n] for n in B_SET)
        res['f5']['parents_zero'] = [p_ for p_, _ in FAMILIES if L5[p_] == 0]
        mism_ok = all(mm[k] == 0 for k, _ in JOURNAL)
        sg_ok = (L5['dcc_rt'] >= 1 and L5['dcc_rt_pending'] >= 1) if tag == SG else True
        res['f5']['control'] = [
            ('DiagF5: mode=1 before the first GuestOut', res['f5']['mode_ok']),
            ('rt_resolves > 0 (last line)', L5['rt_resolves'] > 0),
            ('line_mismatch_* = 0, all six (LETTER: whole log)', mism_ok),
            ('identities (7 families =, 3 pairs <=) hold on every line, 0 malformed lines', s5.malformed == 0 and not s5.ident_bad),
            ('monotone over the lines', not s5.mono_bad),
            ('cmask_fce_noimage = 0 (family invariant, items 458 (v), 470 (b))', L5['cmask_fce_noimage'] == 0)]
        if tag == SG:
            res['f5']['control'].append(('f5_sg: dcc_rt >= 1 and dcc_rt_pending >= 1 (items 421 (g), 427 (g)(2))', sg_ok))
    else:
        res['f5']['control'] = [('a parseable DiagF5 frame line exists', False), ('DiagF5: mode=1 before the first GuestOut',
                                                                                   res['f5']['mode_ok'])]
    if L6 is not None:
        c6 = [('DiagF6: mode=1 before the first GuestOut', res['f6']['mode_ok']),
              ('draws > 0, s_bound > 0, ps_draws > 0', L6['draws'] > 0 and L6['s_bound'] > 0 and L6['ps_draws'] > 0),
              ('w_mask0 + w_addr0_fmt + w_addr0_nofmt > 0', L6['w_mask0'] + L6['w_addr0_fmt'] + L6['w_addr0_nofmt'] > 0),
              ('identities (4 =, 1 <=) hold on every line, 0 malformed lines', s6.malformed == 0 and not s6.ident_bad),
              ('monotone over the lines', not s6.mono_bad)]
        if tag == SG:
            c6.append(('f5_sg: draws_mesh > 0 (item 433 (v))', L6['draws_mesh'] > 0))
        res['f6']['control'] = c6
        res['f6']['inputs'] = dict((n, L6[n]) for n in ('w_addr0_fmt', 'bound_missing', 'bound_extra', 'w_ge8', 's_addr0_fmt'))
    else:
        res['f6']['control'] = [('a parseable DiagF6 frame line exists', False), ('DiagF6: mode=1 before the first GuestOut',
                                                                                   res['f6']['mode_ok'])]
    res['f5']['control_alive'] = all(v for _, v in res['f5']['control'])
    res['f6']['control_alive'] = all(v for _, v in res['f6']['control'])
    res['null_ok'] = r['f5_any'] == 0 and r['f6_any'] == 0
    res['interference'] = bool(r['win'].get('minimized') or r['recovering'] or r['gamepatch'])
    return res


def yn(v):
    if v is None:
        return 'NOT_READ'
    if isinstance(v, str):
        return v
    return 'YES' if v else 'NO'


def fmt_line(d, names):
    return 'frame=%d ' % d['frame'] + ' '.join('%s=%d' % (n, d[n]) for n in names)


def rows(res):
    tag, k = res['tag'], res['kind']
    out = ['F16F %s kind %s level %s log sha256 %s lines %d stdout sha256 %s' % (tag, k, res['level'], res['log_sha256'],
                                                                              res['log_lines'], res['stdout_sha256'])]
    add = out.append
    add('  binary: tag %s (expected %s); version string %s in the binary: %s; installed before %s after %s (expected %s); revision '
        'texts %s' % (res['installed_sha'], BIN_EXPECT, VERSION.decode(), yn(res['version_ok']), res['installed_before'],
                      res['installed_after'], WANT, res['rev']))
    add('  env of the tag (KYTY_DIAG_*, KYTY_FIX_*, KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS): %s' % res['env'])
    add('  Shader translation cache lines %s; %s' % (res['stc'], res['warm_txt']))
    add('  entry line %s; first GuestOut line %s; scene change line %s; first scene frame n %s; hold (sum dt after it) %.1f s; '
        'frames >= 1 s after it %d (max dt_us %d) - REPORT' % (res['entry_line'], res['guest_first'], res['scene_change_line'],
                                                           res['first_scene_n'], res['hold_s'], res['k2_after'], res['dt_max_after']))
    add('  run record: %s' % asc(res['close_info']))
    add('  death markers (REPORT): %d %s; emulator stdout %s' % (len(res['death']), res['death'][:3],
                                                                'present' if res['stdout_present'] else 'MISSING'))
    add('  window: %s, Recovering Vulkan swapchain %d; GamePatch lines %d; [Vulkan][E] %d; AsyncPipelines: skipped draw %d (reference)'
        % (res['win'] or 'none', res['recovering'], res['gamepatch'], res['vke'], res['skipped_draw']))
    add('  manifest: %s' % res['manifest'])
    add('  lines carrying DiagF5: %d, DiagF6: %d' % (res['f5_any'], res['f6_any']))
    for knob, names in (('f5', F5_NAMES), ('f6', F6_NAMES)):
        s = res[knob]
        add('  %s: mode lines %d %s; frame lines %d (malformed %d); identity violations %d %s; monotonicity violations %d %s'
            % (knob.upper(), s['mode_n'], s['mode'], s['lines'], s['malformed'], s['ident_bad_n'], s['ident_bad'][:2], s['mono_bad_n'],
               s['mono_bad'][:2]))
        if s['last'] is not None:
            add('  %s last line (log line %d): %s' % (knob.upper(), s['last_lineno'], fmt_line(s['last'], names)))
    f5 = res['f5']
    if f5['last'] is not None:
        mm, mv = f5['mismatch_letter'], f5['mismatch_variant']
        add('  F5 line_mismatch LETTER (whole log): %s; journal counts %s' % (
            ' '.join('%s=%d' % (kk, mm[kk]) for kk, _ in JOURNAL), mm['counts']))
        add('  F5 line_mismatch VARIANT OF THE EXECUTOR (journal before the last DiagF5 line): %s; journal counts %s' % (
            ' '.join('%s=%d' % (kk, mv[kk]) for kk, _ in JOURNAL), mv['counts']))
        add('  F5 B set (17, items 427 (b), 458 (b)) last line: sum %d; %s' % (f5['b_sum'], ' '.join('%s=%d' % (n, f5['b'][n])
                                                                                                    for n in B_SET)))
        add('  F5 B > 0: %s' % (','.join(n for n in B_SET if f5['b'][n] > 0) or 'none'))
        L = f5['last']
        add('  F5 reference: meta_dma_noclear=%d fmask_read=%d (lower bound) cmask_fce_drawn=%d cmask_fce_noimage=%d stereo_nonzero=%d '
            'stereo_writes=%d; parents = 0: %s' % (L['meta_dma_noclear'], L['fmask_read'], L['cmask_fce_drawn'], L['cmask_fce_noimage'],
                                                 L['stereo_nonzero'], L['stereo_writes'], ','.join(f5['parents_zero']) or 'none'))
    if res['f6']['last'] is not None:
        add('  F6 inputs of item 433 (v)(i)-(iv): %s' % ' '.join('%s=%d' % kv for kv in sorted(res['f6']['inputs'].items())))
    m = [('binary sha256 of the tag = 4ad735ad (F16d2 copy)', res['sha_ok']),
         ('version string ...-1881-g4950557a in the tag binary', res['version_ok']),
         ('installed adb0c82f before the tag', res['before_ok']),
         ('installed adb0c82f after the return', res['after_ok']),
         ('env: %s, no KYTY_FIX_*, KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS' % ('KYTY_DIAG_F5=1 KYTY_DIAG_F6=1' if k == 'diag'
                                                                            else 'no KYTY_DIAG_F5 / KYTY_DIAG_F6'), res['env_ok']),
         ('revision text names %s (reference)' % REV, res['rev_row']),
         ('translation cache directory %s in every line (reference)' % DIR_FIX, res['dir_ok']),
         ('warm form: %s present before the start (reference)' % DIR_FIX, res['warm_ok']),
         ('entered (entry line of %s)' % res['level'], res['entry_line'] is not None),
         ('hold >= %d s after the first scene frame' % res['hold_min_s'], res['hold_len_ok']),
         ('the process lived through the hold (outcome ok, hold_exit null)', res['hold_ok']),
         ('manifest of the caches, saves and GLCache before = after the return', res['manifest_ok']),
         ('no interference: window minimized / Recovering Vulkan swapchain / GamePatch line (else not read, item 273 (z))',
          not res['interference'])]
    for name, val in m:
        add('  ROW %s: %s' % (name, yn(val)))
    if k == 'diag':
        for knob in ('f5', 'f6'):
            for name, val in res[knob]['control']:
                add('  ROW %s control: %s: %s' % (knob.upper(), name, yn(val)))
            add('  CONTROL %s %s' % (knob.upper(), 'ALIVE' if res[knob]['control_alive'] else 'DEAD'))
    else:
        add('  ROW null control: 0 lines DiagF5 and 0 lines DiagF6: %s' % yn(res['null_ok']))
        add('  CONTROL NULL %s' % ('HOLDS' if res['null_ok'] else 'BROKEN'))
    return out


def set_rows(reads):
    """Facts over the tags for F16g (no verdict): control states, B > 0, F6 inputs, null control."""
    out = []
    diag = [o for o in reads if o['kind'] == 'diag']
    for o in reads:
        adm = (o['sha_ok'] and o['before_ok'] and o['after_ok'] and o['env_ok'] and o['entry_line'] is not None and o['hold_len_ok']
               and o['hold_ok'] and o['manifest_ok'] and not o['interference'])
        if o['kind'] == 'diag':
            out.append('SET %s %s admission %s F5 %s F6 %s B_sum %s B>0 %s F6_inputs %s' % (
                o['tag'], o['level'], 'OK' if adm else 'FAIL', 'ALIVE' if o['f5']['control_alive'] else 'DEAD',
                'ALIVE' if o['f6']['control_alive'] else 'DEAD', o['f5'].get('b_sum'),
                ','.join(n for n in B_SET if (o['f5'].get('b') or {}).get(n, 0) > 0) or 'none',
                ' '.join('%s=%d' % kv for kv in sorted((o['f6'].get('inputs') or {}).items()))))
        else:
            out.append('SET %s %s admission %s NULL %s' % (o['tag'], o['level'], 'OK' if adm else 'FAIL',
                                                           'HOLDS' if o['null_ok'] else 'BROKEN'))
    out.append('SET diag tags %d; F5 control alive on %d; F6 control alive on %d; tags with B > 0: %s' % (
        len(diag), sum(1 for o in diag if o['f5']['control_alive']), sum(1 for o in diag if o['f6']['control_alive']),
        ','.join(o['tag'] for o in diag if (o['f5'].get('b_sum') or 0) > 0) or 'none'))
    return out


def main(argv):
    if argv[:1] == ['--set']:
        for row in set_rows([json.load(open(x)) for x in argv[1:]]):
            print(asc(row))
        return 0
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
