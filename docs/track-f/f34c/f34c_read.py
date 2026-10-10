"""Track F link F34c (HPP-740; ROADMAP s122 item 673 (z)(2), 674 (v)-(g), 676 (b)-(l)): the reader of the B6 series on the INSTALLED FS11
ea51ae80.  Rows only, NO VERDICT (the reading is F34d, HPP-741).  Port of C:/kyty/f287/fs11c/fs11c_read.py (FS11c, HPP-716): the scan, the
admission and the W members of fs11_w are kept (b6_w0 is fs11_w unchanged, item 676 (d)); the members of the cutscene tags are those of
F34a section 5.3 with the amendments of item 674 (v)-(g) and item 676 (b)-(k).  ASCII only.

    python f34c_read.py <tag> [--json <out>]                        one tag (files of C:/kyty/f287/f34c)
    python f34c_read.py --dir <fixture dir> --tag <tag> [--json <out>]
        fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt, installed_before.txt, installed_after.txt,
        manifest_cmp.txt, level.txt, seal.md
    python f34c_read.py --timeline <tag> | --dir D --tag T --timeline      the json timeline for the sheets (post_f34c.sh)
    python f34c_read.py --table [--runs <dir>]                      the table over every runs/<tag>/read.json

FORMS: w0 = b6_w0 (control W, Sky Garden, fs11_w unchanged); vn = b6_v, b6_v2 (V, natural start, KYTY_KEYS); vl = b6_vl (V, -lvl intro_next);
       wn = b6_w (W, natural start, KYTY_KEYS); wl = b6_wl (W, -lvl intro_next).  <tag>_r1.._r4 - a repeat of the same form.
DEFINITIONS:
  n_cur        n of the last 'FrameTrace: n=' line before a line (the position in the log, item 676 (e)(1)); the field frame= of the
               AsyncPipelines lines is NOT read.
  n_intro      n of the first FrameTrace after the line 'GuestOut: Level has started: intro_next'.
  n_sw         n of the first FrameTrace after the first line 'SubLevelLocator sublevel_locator_space [...] state changed 7->6'.
  off (vn, wn) the median over the InputScript press / release lines of (present of the line - n_cur); off_L of vl / wl is [U] in [0; 25]
               (item 676 (v)) - not computed.
  room window  n in [n_intro + 2880; n_intro + 3330] (V5, item 676 (b), (e)); sheet window (V4): vn - present in [P_intro + 2880;
               P_intro + 3330] step 10, P = n + off; vl - present in [n_intro + 2880; n_intro + 3355] step 10 (item 676 (v)); four big frames at
               +2950, +3050, +3150, +3250.
  cutscene     (V2) vn - .idx records with present in [n_intro + off; n_sw + off]; vl - in [n_intro; n_sw + 25].
ADMISSION (a failed member - INTERFERENCE, the tag is not read; a repeat by a times.txt line, item 676 (l)): json; binary_sha256 = FS11
  ea51ae80; installed before = after = FS11 (the binary is not installed); prereg = seal sha256; env = the form exactly; last
  --vulkan-validation true only at W; --shader-validation false; no --rd; guest args of the form and the harness level file; hold option;
  log; window lines minimized / Recovering Vulkan swapchain 0; signature 9177b426 and the catalog variant_fixb26_fixb1b_fixf10_fixf19;
  GamePatch: 0; DiagB32 0; TestLogStall 0; caches returned (manifest cmp EQUAL); the summary 'LogAsync: full_waits=' once (not applied to
  a W with a [Vulkan][E] line - the layer ends the process, item 676 (b)); w0 also: entry outcome ok and the Sky Garden entry line.
"""
import hashlib
import json
import os
import re
import statistics
import sys

G = 'C:/kyty/f287/f34c'
SEAL_PATH = G + '/pred/f34c_seal.md'
BIN_TAG = 'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
INTRO = 'intro_next'
TITLE = 'title_controller_ship'
KEYS = '@2170:j,@2460:j'
TAG_RX = re.compile(r'^(b6_w0|b6_v|b6_v2|b6_vl|b6_w|b6_wl)(_r[1-4])?$')
FORM = {'b6_w0': 'w0', 'b6_v': 'vn', 'b6_v2': 'vn', 'b6_vl': 'vl', 'b6_w': 'wn', 'b6_wl': 'wl'}
HOLD_OPT = {'w0': 310, 'vn': 600, 'vl': 600, 'wn': 1800, 'wl': 1800}
HOLD_W0_S = 310
K2_US = 1000000
VIDEO_MIN = 3000
ROOM_LO, ROOM_HI = 2880, 3330
SHEET_HI_L = 3355
BIG = (2950, 3050, 3150, 3250)
DELTA_LO, DELTA_HI = 4480, 4620
W_TAIL = 300
OFF_L_MAX = 25
HELD_CAP = 64
LIMIT = '100000000'
VKLAYER = 'C:/VulkanSDK/1.4.357.0/Bin'
RX_SUM = re.compile(rb'^LogAsync: full_waits=\d+ ')
RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_B13 = re.compile(rb'FixB13: mode=(\d+)')
RX_B12 = re.compile(rb'FixB12: mode=(\d+)\s*$')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d) enabled=(\d)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GA = re.compile(rb'GuestArgs: source=(\S+) argc=(\d+)')
RX_ARGV = re.compile(rb'GuestArgs:   argv\[(\d+)\] = (.*)$')
RX_SCHED = re.compile(rb'InputScript: scheduled (\S+) at present (\d+) \(hold ([0-9.]+) ms\)')
RX_IN = re.compile(rb'InputScript: (press|release) (\S+) at ([0-9.]+) s \(present (\d+)\)')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
RX_GLROW = re.compile(r'^\s*video\s+(\d+) present\s+(\d+) ')
SEED = re.compile(rb':KytySC3:([0-9a-f]{40}):')
M_SUB = b'SubLevelLocator sublevel_locator_space ['
M_SUB_STATE = b'state changed 7->6'
M_SKIP = b'AsyncPipelines: skipped draw'
M_HELD = b'held (incomplete frame)'
M_LIMIT = b'this will be the last time reporting it'
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
SUM_KEYS = ('full_waits', 'full_wait_us', 'stalls', 'stall_cut', 'lines', 'bytes', 'max_queued_bytes', 'sync_lines', 'drain_timeouts')
REF_PREFIX = (b'ShaderReplay:', b'PipelinePrecache:', b'ShaderPreparation: startup wait', b'FixSval:', b'LogAsync: mode=')


def sha_file(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def text(path):
    if not path or not os.path.exists(path):
        return None
    return open(path, 'rb').read().decode('utf-8', 'replace')


def last_flag(cmd, flag):
    v = None
    for i, a in enumerate(cmd or []):
        if a == flag:
            v = cmd[i + 1] if i + 1 < len(cmd) else ''
    return v


def num(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def form_of(tag):
    return FORM[TAG_RX.match(tag).group(1)]


def is_w(form):
    return form in ('w0', 'wn', 'wl')


def level_of(form):
    return SKY if form == 'w0' else INTRO


def expected_env(form):
    """Every KYTY_* / VK_* key of the tag json env -> the value (None: any value; the path keys)."""
    e = dict(KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None, KYTY_QUEUE_TRACE='1',
             KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8')
    if form == 'w0':
        e.update(KYTY_GUEST_ARGS='-lvl ' + SKY)
    elif form in ('vl', 'wl'):
        e.update(KYTY_GUEST_ARGS='-lvl ' + INTRO)
    if form in ('vn', 'wn'):
        e.update(KYTY_KEYS=KEYS)
    if is_w(form):
        e.update(VK_LAYER_PATH=VKLAYER, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=LIMIT)
    else:
        e.update(KYTY_REC=None)
    return e


def env_diff(env, want):
    bad = []
    for key in sorted(set(env) | set(want)):
        if key not in env:
            bad.append('missing %s' % key)
        elif key not in want:
            bad.append('extra %s=%s' % (key, env[key]))
        elif want[key] is not None and env[key] != want[key]:
            bad.append('%s=%s (want %s)' % (key, env[key], want[key]))
    return bad


def scan(path, level):
    """One pass over the log; every event line gets n_cur (the n of the last FrameTrace before it)."""
    import lzma
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    r = dict(mode=[], summary=[], summary_bad=0, other_async=0, ft=[], entry_ln=None, title_ln=None, intro_ln=None, first_guest_ln=None,
             death=[], minimized=0, recovering=0, win={}, b13=[], b12=[], b12_bad=0, dual=[], vke=0, vke_ev=[], vkw=0, vkw2=0, vkw_after=0,
             vkw_after2=0, vk_last_n=None, vk_limit=0, lines=0, sig=[], variant_dir=[], gamepatch=0, diagb32=0, stall_lines=0, ga=[], argv=[],
             sched=[], inp=[], sub_ln=None, sub_n=None, skip_n=[], held_n=[], translat_pre=0, refs=[])
    lvl = ('GuestOut: Level has started: %s' % level).encode()
    lvl_title = ('GuestOut: Level has started: %s' % TITLE).encode()
    lvl_intro = ('GuestOut: Level has started: %s' % INTRO).encode()
    ln = 0
    n_cur = None
    after_intro = False   # a FrameTrace after the intro line was seen: n_cur >= n_intro from here on
    for line in fh:
        ln += 1
        if line.startswith(b'FrameTrace: n='):
            m = RX_FT.match(line)
            if m:
                d = RX_DRAWS.search(line)
                n_cur = int(m.group(1))
                r['ft'].append((n_cur, int(m.group(2)), int(d.group(1)) if d else None, ln))
                if r['intro_ln'] is not None:
                    after_intro = True
            continue
        if line.startswith(b'FrameTrace'):
            continue
        if line.startswith(b'DiagB32'):
            r['diagb32'] += 1
            continue
        if line.startswith(b'TestLogStall:'):
            r['stall_lines'] += 1
            continue
        if line.startswith(b'LogAsync:'):
            if line.startswith(b'LogAsync: mode='):
                r['mode'].append((line.decode('ascii', 'replace').strip()[:160], ln))
            elif RX_SUM.match(line):
                f = dict(tok.split('=', 1) for tok in line.decode('ascii', 'replace').strip().split(' ')[1:] if '=' in tok)
                if all(k in f for k in SUM_KEYS):
                    r['summary'].append(dict((k, num(f[k])) for k in SUM_KEYS))
                else:
                    r['summary_bad'] += 1
            else:
                r['other_async'] += 1
            continue
        s = line.rstrip(b'\r\n')
        if r['entry_ln'] is None and s.endswith(lvl):
            r['entry_ln'] = ln
        if r['title_ln'] is None and s.endswith(lvl_title):
            r['title_ln'] = ln
        if r['intro_ln'] is None and s.endswith(lvl_intro):
            r['intro_ln'] = ln
        if r['first_guest_ln'] is None and b'GuestOut' in line:
            r['first_guest_ln'] = ln
        if b'[Vulkan]' in line:
            if b'[Vulkan][E]' in line:
                r['vke'] += 1
                if len(r['vke_ev']) < 50:
                    r['vke_ev'].append((ln, n_cur, after_intro))
            if b'[Vulkan][W]' in line:
                r['vkw'] += 1
                w2 = b'[Vulkan][W][2]' in line
                r['vkw2'] += w2
                if after_intro:
                    r['vkw_after'] += 1
                    r['vkw_after2'] += w2
            r['vk_last_n'] = n_cur
        if M_LIMIT in line:
            r['vk_limit'] += 1
        if M_SKIP in line:
            if len(r['skip_n']) < 200000:
                r['skip_n'].append(n_cur)
            continue
        if M_HELD in line:
            if len(r['held_n']) < 200000:
                r['held_n'].append(n_cur)
            continue
        if r['sub_ln'] is None and M_SUB in line and M_SUB_STATE in line:
            r['sub_ln'] = ln
        if line.startswith(b'GuestArgs:'):
            m = RX_GA.search(line)
            if m:
                r['ga'].append((m.group(1).decode('ascii', 'replace'), int(m.group(2))))
            m = RX_ARGV.search(s)
            if m:
                r['argv'].append(m.group(2).decode('ascii', 'replace').strip())
        if line.startswith(b'InputScript:'):
            m = RX_SCHED.search(line)
            if m:
                r['sched'].append((m.group(1).decode('ascii', 'replace'), int(m.group(2)), float(m.group(3))))
            m = RX_IN.search(line)
            if m:
                r['inp'].append((m.group(1).decode(), m.group(2).decode('ascii', 'replace'), int(m.group(4)), n_cur, ln))
        m = RX_B13.search(line)
        if m:
            r['b13'].append((int(m.group(1)), ln))
        if b'FixB12: mode=' in line:
            m = RX_B12.search(line)
            if m:
                r['b12'].append((int(m.group(1)), ln))
            else:
                r['b12_bad'] += 1
        m = RX_DUAL.search(line)
        if m:
            r['dual'].append((m.group(1) == b'1' and m.group(2) == b'1', ln))
        if line.startswith(b'GamePatch:'):
            r['gamepatch'] += 1
        if line.startswith(b'ShaderSeed: compatibility=') and len(r['sig']) < 4:
            mm = SEED.search(line)
            r['sig'].append(mm.group(1).decode('ascii') if mm else '?')
        if line.startswith(b'Shader translation cache: ') and len(r['variant_dir']) < 4:
            r['variant_dir'].append(line.decode('ascii', 'replace').strip().replace('\\', '/').rsplit('/', 1)[-1])
        elif r['intro_ln'] is None and b'ranslat' in line:
            r['translat_pre'] += 1
        if line.startswith(REF_PREFIX) and len(r['refs']) < 12:
            r['refs'].append(line.decode('ascii', 'replace').strip()[:160])
        for dm in DEATH:
            if dm in line and len(r['death']) < 20:
                r['death'].append((dm.decode(), n_cur))
        if b'Recovering Vulkan swapchain' in line:
            r['recovering'] += 1
        mw = RX_WIN.search(line)
        if mw:
            k = mw.group(1).decode()
            r['win'][k] = r['win'].get(k, 0) + 1
            if k == 'minimized':
                r['minimized'] += 1
    r['lines'] = ln
    fh.close()
    return r


def ft_after(x, ln0):
    """n of the first FrameTrace after line ln0 (None if none)."""
    if ln0 is None:
        return None
    for n, dt, d, ln in x['ft']:
        if ln > ln0:
            return n
    return None


def timeline(form, x):
    """n_intro, n_sw, delta, off, the windows of the sheet and of the cutscene, last n."""
    t = dict(n_intro=ft_after(x, x['intro_ln']), n_sw=ft_after(x, x['sub_ln']), n_last=x['ft'][-1][0] if x['ft'] else None)
    t['delta'] = None if t['n_intro'] is None or t['n_sw'] is None else t['n_sw'] - t['n_intro']
    off = None
    if form in ('vn', 'wn'):
        ds = [p - n for (k, key, p, n, ln) in x['inp'] if n is not None]
        off = statistics.median(ds) if ds else None
        if off is not None and off != int(off):
            off = float(off)
        elif off is not None:
            off = int(off)
    t['off'] = off
    t['off_note'] = 'off_L [U] in [0; 25] (item 676 (v))' if form in ('vl', 'wl') else ('median of %d InputScript lines' % len(
        [1 for z in x['inp'] if z[3] is not None]))
    ni = t['n_intro']
    if ni is not None:
        t['room_n'] = [ni + ROOM_LO, ni + ROOM_HI]
        if form == 'vl':
            t['sheet_p'] = [ni + ROOM_LO, ni + SHEET_HI_L]
            t['big_p'] = [ni + b for b in BIG]
        elif off is not None:
            t['sheet_p'] = [ni + off + ROOM_LO, ni + off + ROOM_HI]
            t['big_p'] = [ni + off + b for b in BIG]
        else:
            t['sheet_p'] = t['big_p'] = None
        if t['n_sw'] is not None:
            if form == 'vl':
                t['cut_p'] = [ni, t['n_sw'] + OFF_L_MAX]
            elif off is not None:
                t['cut_p'] = [ni + off, t['n_sw'] + off]
            else:
                t['cut_p'] = None
        else:
            t['cut_p'] = None
    else:
        t['room_n'] = t['sheet_p'] = t['big_p'] = t['cut_p'] = None
    return t


def in_rng(v, rng):
    return v is not None and rng is not None and rng[0] <= v <= rng[1]


def idx_records(path):
    out = []
    if path and os.path.exists(path):
        for l in open(path, 'rb'):
            p = l.split()
            if len(p) >= 2:
                out.append((int(p[0]), int(p[1])))
    return out


def glitch_rows(gt):
    """(count, [(video frame, present)]) of the s51_vidglitch.py output."""
    if not gt:
        return None, []
    mg = RX_GL.search(gt)
    rows = []
    for l in gt.splitlines():
        m = RX_GLROW.match(l)
        if m:
            rows.append((int(m.group(1)), int(m.group(2))))
    return (int(mg.group(1)) if mg else None), rows


def mode_member(x):
    g = x['first_guest_ln']
    ok = len(x['mode']) == 1 and x['mode'][0][0].startswith('LogAsync: mode=1 ') and g is not None and x['mode'][0][1] < g
    return ('LogAsync: mode=1 exactly once, before the first GuestOut (lines %s, first GuestOut %s)' % (
        [(t[:40], l) for t, l in x['mode'][:2]], g), ok)


def b13_member(x):
    g = x['first_guest_ln']
    ok = bool(x['b13']) and all(v == 1 for v, l in x['b13']) and g is not None and x['b13'][0][1] < g
    return ('FixB13: mode=1 (every line) before the first GuestOut (%s; first GuestOut %s) - form fs10_w' % (x['b13'][:3], g), ok)


def b12_member(x):
    g = x['first_guest_ln']
    ok = bool(x['b12']) and x['b12_bad'] == 0 and all(v == 1 for v, l in x['b12']) and g is not None and x['b12'][0][1] < g
    return ('FixB12: mode=1 (every line) before the first GuestOut (%s; bad %d; first GuestOut %s) - form fs11_w' % (
        x['b12'][:3], x['b12_bad'], g), ok)


def dual_member(x):
    g = x['first_guest_ln']
    dual = [d for d in x['dual'] if d[0] and g is not None and d[1] < g]
    return ('DualSrcBlend: supported=1 enabled=1 before the first GuestOut (%d)' % len(dual), bool(dual))


def first_scene(x):
    ent = x['entry_ln']
    if ent is None:
        return None, []
    for i, (n, dt, draws, ln) in enumerate(x['ft']):
        if ln > ent and draws is not None and draws >= 100:
            return i, x['ft'][i + 1:]
    return None, []


def members_w0(x, att, death):
    """b6_w0 = fs11_w of FS11c unchanged (item 676 (d), last sentence)."""
    lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None and (att.get('hold_s') or 0) >= HOLD_W0_S
    i, after = first_scene(x)
    info = dict(frames_ge1s_report=sum(1 for (n, dt, d, ln) in after if dt >= K2_US), scene_frames=len(after),
                mean_dt_us=(round(sum(dt for (n, dt, d, ln) in after) / len(after), 1) if after else None), vkw=x['vkw'])
    m = [('lived to the end of the hold (outcome %s, hold_exit %s, hold_s %s >= 310)' % (att.get('outcome'), att.get('hold_exit'),
                                                                                      att.get('hold_s')), lived),
         ('0 death markers (log and stdout) %s' % death[:3], not death),
         ('0 [Vulkan][E] (%d)' % x['vke'], x['vke'] == 0),
         ('0 limit lines of the layer (%d)' % x['vk_limit'], x['vk_limit'] == 0),
         ('positive control: [Vulkan][W] %d > 0' % x['vkw'], x['vkw'] > 0),
         dual_member(x),
         mode_member(x),
         ('no VALIDATION_STOP (a [Vulkan][E] line and the process did not live to the end of the hold)', not (x['vke'] > 0 and not lived)),
         b13_member(x),
         b12_member(x)]
    return m, info, ('W0_MEMBERS_ALL_YES' if all(b for _, b in m) else 'W0_MEMBERS_NOT_ALL_YES')


def path_members(form, x, t):
    """(P1)-(P5) of F34a section 5.3 with item 676 (g) for W.  Returns (members, facts)."""
    m = []
    natural = form in ('vn', 'wn')
    if natural:
        ga = x['ga']
        m.append(('(P1) GuestArgs: source=none argc=1, no -lvl in argv (%s; argv %s)' % (ga[:2], x['argv'][:4]),
                  ga == [('none', 1)] and not any(a == '-lvl' for a in x['argv'])))
        sched = sorted((k, p) for (k, p, h) in x['sched'])
        press = sorted(p for (k, key, p, n, ln) in x['inp'] if k == 'press' and key == 'j')
        m.append(('(P2) InputScript: scheduled j at present 2170 and 2460 once each, press j at present 2170 and 2460 once each '
                  '(scheduled %s; press %s)' % (sched, press), sched == [('j', 2170), ('j', 2460)] and press == [2170, 2460]))
        pl = [ln for (k, key, p, n, ln) in x['inp'] if k == 'press']
        ok3 = (x['title_ln'] is not None and len(pl) >= 2 and x['title_ln'] < pl[0] and x['intro_ln'] is not None and x['intro_ln'] > pl[1]
               and t['n_intro'] is not None)
        m.append(('(P3) title line (%s) before the first press (%s), intro_next line (%s) after the second press (%s), n_intro %s' % (
            x['title_ln'], pl[:1], x['intro_ln'], pl[1:2], t['n_intro']), ok3))
    else:
        m.append(('(P1) GuestArgs: source=KYTY_GUEST_ARGS argc=3, argv -lvl intro_next (%s; argv %s)' % (x['ga'][:2], x['argv'][:4]),
                  x['ga'] == [('KYTY_GUEST_ARGS', 3)] and x['argv'][1:3] == ['-lvl', INTRO]))
        m.append(('(P2) no InputScript press / release line - form L has no input (%d)' % len(x['inp']), not x['inp'] and not x['sched']))
        ok3 = x['intro_ln'] is not None and t['n_intro'] is not None
        m.append(('(P3) intro_next line (%s), n_intro %s' % (x['intro_ln'], t['n_intro']), ok3))
    sub = x['sub_ln'] is not None and t['n_sw'] is not None
    band = t['delta'] is not None and DELTA_LO <= t['delta'] <= DELTA_HI
    if is_w(form):
        m.append(('(P4) row: sub-level line %s, n_sw %s, delta %s - reference at W (item 676 (g))' % (x['sub_ln'], t['n_sw'], t['delta']), True))
        tail = sub and t['n_last'] is not None and t['n_last'] >= t['n_sw'] + W_TAIL
        m.append(('(P5)_W sub-level line present and the last FrameTrace n %s >= n_sw + 300 (%s) - item 676 (g)' % (
            t['n_last'], None if t['n_sw'] is None else t['n_sw'] + W_TAIL), bool(tail)))
    else:
        m.append(('(P4) sub-level line %s, n_sw %s, delta %s in [4480; 4620]' % (x['sub_ln'], t['n_sw'], t['delta']), sub and band))
        cov = t['n_intro'] is not None and t['n_last'] is not None and t['n_last'] >= t['n_intro'] + ROOM_HI
        m.append(('(P5) the last FrameTrace n %s >= n_intro + 3330 (%s)' % (
            t['n_last'], None if t['n_intro'] is None else t['n_intro'] + ROOM_HI), bool(cov)))
    return m, dict(entered=bool(ok3), sub=sub, band=band)


def cold_room(x, t):
    """(V5, item 676 (e)): skipped / held lines with n_cur in the room window; the n of the 64th held line."""
    rn = t['room_n']
    sk = sum(1 for n in x['skip_n'] if in_rng(n, rn))
    hd = sum(1 for n in x['held_n'] if in_rng(n, rn))
    h64 = x['held_n'][HELD_CAP - 1] if len(x['held_n']) >= HELD_CAP else None
    held_u = h64 is not None and rn is not None and (h64 is None or h64 < rn[1])
    return dict(skipped_in_room=sk, held_in_room=hd, skipped_all=len(x['skip_n']), held_all=len(x['held_n']), held_64th_n=h64,
                held_in_room_unknown=bool(held_u))


def members_v(form, x, t, att, death, idx, glc, glrows, sheet):
    pm, pf = path_members(form, x, t)
    lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None
    cut = t['cut_p']
    rec_cut = sum(1 for (f, p) in idx if in_rng(p, cut))
    gl_cut = [(f, p) for (f, p) in glrows if in_rng(p, cut)]
    cr = cold_room(x, t)
    m = list(pm)
    m += [('(V1) the process lived to the end (outcome %s, hold_exit %s, hold_end %s)' % (att.get('outcome'), att.get('hold_exit'),
                                                                                        att.get('hold_end')), lived),
          ('(V1) 0 death markers (log and stdout) %s' % death[:3], not death),
          ('(V2) cutscene records of the video %d >= 3000 (present %s; all records %d)' % (rec_cut, cut, len(idx)), rec_cut >= VIDEO_MIN),
          ('(V3) 0 one-frame glitches on the cutscene records (%d: %s; whole video %s)' % (len(gl_cut), gl_cut[:6], glc),
           glc is not None and not gl_cut),
          ('(V4) room sheet made - the last line of sheet.txt is sheets done (%s)' % sheet, sheet == 'sheets done'),
          ('(V5) 0 skipped draw / held lines with n in the room window %s (skipped %d, held %d; 64th held at n %s%s)' % (
              t['room_n'], cr['skipped_in_room'], cr['held_in_room'], cr['held_64th_n'],
              ', held in the window [U]' if cr['held_in_room_unknown'] else ''), cr['skipped_in_room'] == 0 and cr['held_in_room'] == 0)]
    if not pf['entered']:
        st = 'NOT_ENTERED'
    elif not (t['n_last'] is not None and t['n_intro'] is not None and t['n_last'] >= t['n_intro'] + ROOM_HI):
        st = 'ROOM_NOT_COVERED'
    elif not (pf['sub'] and pf['band']):
        st = 'TIMELINE_OTHER'
    else:
        st = 'ROOM_COVERED'
    flags = []
    if death:
        flags.append('DEATH_MARKER')
    if not lived:
        flags.append('NOT_LIVED')
    if st == 'ROOM_COVERED' and (cr['skipped_in_room'] or cr['held_in_room']):
        flags.append('COLD_ROOM')
    info = dict(cold=cr, records_cut=rec_cut, glitches_cut=gl_cut[:20], glitches_all=glc,
                frames_ge1s_before_intro=sum(1 for (n, dt, d, ln) in x['ft'] if dt >= K2_US and (t['n_intro'] is None or n < t['n_intro'])),
                frames_ge1s_after_intro=sum(1 for (n, dt, d, ln) in x['ft'] if dt >= K2_US and t['n_intro'] is not None and n >= t['n_intro']),
                translation_lines_before_intro=x['translat_pre'])
    return m, info, st, flags


def members_wc(form, x, t, att, death, env):
    """b6_w / b6_wl: item 676 (b) (layer error first), (i) W_NOT_ENTERED, (g) (P5)_W / W_SHORT, (d) positive control."""
    pm, pf = path_members(form, x, t)
    lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None
    rn = t['room_n']
    ev = x['vke_ev']
    stop_n = ev[0][1] if ev else None
    e_in = sum(1 for (ln, n, a) in ev if a and in_rng(n, rn))
    e_out = x['vke'] - e_in
    form_w = env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT') == LIMIT and 'VK_LAYER_MESSAGE_ID_FILTER' not in env
    m = list(pm)
    m += [('lived to the end (outcome %s, hold_exit %s, hold_end %s)' % (att.get('outcome'), att.get('hold_exit'), att.get('hold_end')), lived),
          ('0 death markers (log and stdout) %s' % death[:3], not death),
          ('0 [Vulkan][E] (%d; in the room window %d, outside %d - by construction <= 1, item 676 (b))' % (x['vke'], e_in, e_out), x['vke'] == 0),
          ('0 limit lines of the layer (%d)' % x['vk_limit'], x['vk_limit'] == 0),
          ('positive control (item 676 (d)): [Vulkan][W] lines with n >= n_intro %d >= 1 (of them [W][2] %d; all [W] %d)' % (
              x['vkw_after'], x['vkw_after2'], x['vkw']), x['vkw_after'] >= 1),
          ('W form line from the env (item 295 (b)(4)): limit=%s filter=%s' % (env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT'),
                                                                               env.get('VK_LAYER_MESSAGE_ID_FILTER', 'none')), form_w),
          dual_member(x),
          mode_member(x),
          ('no VALIDATION_STOP (a [Vulkan][E] line and the process did not live to the end)', not (x['vke'] > 0 and not lived))]
    notes = []
    if x['vke'] > 0:
        st = 'W_LAYER_ERROR'
        passed = t['n_intro'] is not None and stop_n is not None and stop_n >= t['n_intro'] + ROOM_LO
        notes.append('read only by item 674 (g)(2) (item 676 (b)): stop at n %s against the room window %s%s' % (
            stop_n, rn, '' if passed else ' - room not passed by the layer'))
    elif not pf['entered']:
        st = 'W_NOT_ENTERED'
    elif not pf['sub']:
        st = 'W_SHORT'
    elif not (t['n_last'] is not None and t['n_last'] >= t['n_sw'] + W_TAIL):
        st = 'W_TAIL_SHORT'
        notes.append('sub-level line present, the tail < n_sw + 300 - not named by the items (question to the lead)')
    elif not (x['vkw_after'] >= 1 and x['vk_limit'] == 0 and form_w):
        st = 'W_NO_POSITIVE_CONTROL'
    else:
        st = 'W_MEMBERS_ALL_YES' if all(b for _, b in m) else 'W_MEMBERS_NOT_ALL_YES'
    flags = []
    if death and st != 'W_LAYER_ERROR':
        flags.append('DEATH_MARKER')
    info = dict(stop_n=stop_n, e_in_room=e_in, e_out_room=e_out, vkw_after=x['vkw_after'], vk_last_n=x['vk_last_n'], n_last=t['n_last'],
                ref_295b3='last layer line at n %s, last FrameTrace n %s (reference, item 676 (d))' % (x['vk_last_n'], t['n_last']),
                frames_ge1s=sum(1 for (n, dt, d, ln) in x['ft'] if dt >= K2_US), notes=notes)
    return m, info, st, flags


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'level', 'sheet')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), seal=SEAL_PATH)
    return p


def stdout_death(path):
    out = []
    if path and os.path.exists(path):
        data = open(path, 'rb').read()
        for dm in DEATH:
            if dm in data:
                out.append(dm.decode())
    return out


def read_tag(tag, p):
    form = form_of(tag)
    lv = level_of(form)
    res = dict(tag=tag, form=form, level=lv, reader_sha256=sha_file(os.path.abspath(__file__)))
    run = json.load(open(p['run'], encoding='utf-8')) if os.path.exists(p['run']) else None
    jbin = (run or {}).get('binary_sha256')
    res['binary_sha256'] = jbin
    inst_b = (text(p['installed_before']) or '').strip() or None
    inst_a = (text(p['installed_after']) or '').strip() or None
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env = dict((k, v) for k, v in ((run or {}).get('env') or {}).items() if k.startswith(('KYTY_', 'VK_')))
    cmd = (run or {}).get('cmdline') or []
    att = ((run or {}).get('attempts') or [{}])[-1]
    mcmp = (text(p['manifest_cmp']) or '').strip().splitlines()
    hlev = (text(p['level']) or '').strip() or None
    ga = (run or {}).get('guest_args')
    have_log = os.path.exists(p['log'])
    x = scan(p['log'], lv) if have_log else None
    ebad = env_diff(env, expected_env(form))
    vv = 'true' if is_w(form) else 'false'
    want_ga = None if form in ('vn', 'wn') else '-lvl ' + lv
    sd = stdout_death(p['stdout'])
    adm = [
        ('tag json present', run is not None),
        ('json binary_sha256 = FS11 ea51ae80 (%s)' % (jbin or '-')[:16], jbin == BIN_TAG),
        ('installed before = after = FS11 ea51ae80 - not installed (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_TAG and inst_a == BIN_TAG),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env = the form of the tag (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad),
        ('last --vulkan-validation %s (%s)' % (vv, last_flag(cmd, '--vulkan-validation')), last_flag(cmd, '--vulkan-validation') == vv),
        ('last --shader-validation false (%s)' % last_flag(cmd, '--shader-validation'), last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args %s (%s; harness %s)' % (want_ga or 'none (natural start)', ga, hlev), run is not None and ga == want_ga and hlev == lv),
        ('hold option %d s (%s)' % (HOLD_OPT[form], (run or {}).get('hold_s')), (run or {}).get('hold_s') == HOLD_OPT[form]),
        ('log present', have_log),
        ('window events: minimized %s, Recovering Vulkan swapchain %s (all %s)' % ((x or {}).get('minimized'), (x or {}).get('recovering'),
                                                                                  (x or {}).get('win')),
         x is not None and x['minimized'] == 0 and x['recovering'] == 0),
        ('translation signature 9177b426 and cache dir %s (%s / %s)' % (VARIANT_DIR, [z[:8] for z in (x or {}).get('sig') or []],
                                                                       (x or {}).get('variant_dir')),
         x is not None and x['sig'] == [SIG] and x['variant_dir'] == [VARIANT_DIR]),
        ('no GamePatch: line (%s)' % (x or {}).get('gamepatch'), x is not None and x['gamepatch'] == 0),
        ('no DiagB32 line (%s)' % (x or {}).get('diagb32'), x is not None and x['diagb32'] == 0),
        ('no TestLogStall line (%s)' % (x or {}).get('stall_lines'), x is not None and x['stall_lines'] == 0),
        ('caches returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'), bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),
    ]
    if form == 'w0':
        adm += [('entry outcome ok (%s)' % att.get('outcome'), att.get('outcome') == 'ok'),
                ('Sky Garden entry line present (%s)' % (x or {}).get('entry_ln'), x is not None and x['entry_ln'] is not None)]
    why = None
    if x is not None:
        if is_w(form) and form != 'w0' and x['vke'] > 0:
            adm.append(('summary line LogAsync: full_waits= - not applied: [Vulkan][E] ends the process (item 676 (b)) (%d)' % len(x['summary']),
                        True))
        else:
            ok = len(x['summary']) == 1 and x['summary_bad'] == 0
            adm.append(('summary line LogAsync: full_waits= present once, all fields (%d, bad %d) - absent: killed (item 615 (b)(6))' % (
                len(x['summary']), x['summary_bad']), ok))
            if not ok and not x['summary']:
                why = 'run (item 615 (b)(6): no summary line - killed; repeat by a times.txt line, item 676 (l))'
    res['admission'] = [[a, bool(b)] for a, b in adm]
    admitted = all(b for _, b in adm)
    res['admitted'] = admitted
    res['interference'] = None if admitted else (why or 'admission member: %s' % [a for a, b in adm if not b][:3])
    idx = idx_records(p['idx'])
    glc, glrows = glitch_rows(text(p['glitch']))
    st_txt = (text(p['sheet']) or '').strip()
    sheet = st_txt.splitlines()[-1][:160] if st_txt else None
    res['ref'] = dict(outcome=att.get('outcome'), hold_exit=att.get('hold_exit'), hold_s=att.get('hold_s'), hold_end=att.get('hold_end'),
                      n_sw_harness=att.get('n_sw'), n_end_harness=att.get('n_end'), stable_s=att.get('stable_s'), lines=(x or {}).get('lines'),
                      video_index=len(idx), glitches=glc, sheet=sheet, refs=(x or {}).get('refs'), log_sha256=sha_file(p['log']))
    res['members'] = res['info'] = res['timeline'] = None
    res['path_status'] = None
    res['flags'] = []
    if x is not None:
        t = timeline(form, x)
        res['timeline'] = t
    if x is not None and admitted:
        death = [d for d, n in x['death']] + sd
        if form == 'w0':
            m, info, st = members_w0(x, att, death)
            flags = []
        elif form in ('vn', 'vl'):
            m, info, st, flags = members_v(form, x, t, att, death, idx, glc, glrows, sheet)
        else:
            m, info, st, flags = members_wc(form, x, t, att, death, env)
        res['members'] = [[a, bool(b)] for a, b in m]
        res['info'] = info
        res['path_status'] = st
        res['flags'] = flags
    if not admitted:
        res['status'] = 'INTERFERENCE'
    elif res['flags']:
        res['status'] = 'INTERFERENCE_FLAG ' + ','.join(res['flags'])
    else:
        res['status'] = 'ADMITTED'
    res['reading'] = ('%s, %s (no verdict; reading - F34d)' % (res['status'], res['path_status'])) if admitted else (
        'INTERFERENCE: %s' % res['interference'])
    return res


def rows_out(res):
    out = ['tag %s (form %s, level %s)  reader sha256 %s' % (res['tag'], res['form'], res['level'], res['reader_sha256'])]
    out.append('  ADMISSION %s; STATUS %s; PATH %s' % ('PASS' if res['admitted'] else 'FAIL', res['status'], res['path_status']))
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    out.append('  binary_sha256 %s' % res['binary_sha256'])
    out.append('  TIMELINE %s' % json.dumps(res['timeline'], sort_keys=True))
    if res['members'] is not None:
        out.append('  MEMBERS %s (path %s, flags %s)' % (res['form'], res['path_status'], res['flags'] or '-'))
        for a, b in res['members']:
            out.append('    [%s] %s' % ('YES' if b else 'NO', a))
        out.append('  INFO %s' % json.dumps(res['info'], sort_keys=True, default=list)[:1500])
    out.append('  REFERENCE: %s' % json.dumps(res['ref'], sort_keys=True)[:1500])
    out.append('  READING %s' % res['reading'])
    return out


def table(rd):
    out = ['| tag | status | path | binary_sha256 | n_intro | n_sw | delta | off | last n | video | glitches |', '|' + '---|' * 11]
    if os.path.isdir(rd):
        for t in sorted(os.listdir(rd)):
            js = os.path.join(rd, t, 'read.json')
            if TAG_RX.match(t) and os.path.exists(js):
                r = json.load(open(js, encoding='utf-8'))
                tl = r.get('timeline') or {}
                out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                    t, r['status'], r.get('path_status'), (r['binary_sha256'] or '-')[:8], tl.get('n_intro'), tl.get('n_sw'), tl.get('delta'),
                    tl.get('off'), tl.get('n_last'), r['ref']['video_index'], r['ref']['glitches']))
    return out


def main(argv):
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader f34c_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for l in table(rd):
            print(l)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        p = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        if tag == '--timeline':
            tag = argv[1] if len(argv) > 1 else ''
        p = paths(tag) if TAG_RX.match(tag) else None
    if not TAG_RX.match(tag):
        print('usage: f34c_read.py <tag> | --dir D --tag T | --timeline <tag> | --table')
        return 2
    if '--timeline' in argv:
        form = form_of(tag)
        x = scan(p['log'], level_of(form)) if os.path.exists(p['log']) else None
        print(json.dumps(timeline(form, x) if x is not None else None, sort_keys=True))
        return 0 if x is not None else 1
    res = read_tag(tag, p)
    for l in rows_out(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
