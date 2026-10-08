"""Track F link FS10c (HPP-686; ROADMAP s122 item 624 (e)(3), item 626 (b), (g)): the reader of the five tags of the ship binary FS10
abfded5e (FS9 11164d72 + a8ee1b05, b4ee756a, 0e4b2f5a, 5064c5bb + FS10a 7f34b1e2, worktree dc5d4712; default KYTY_FIX_B36=1):
fs10_s1 / fs10_s0 (stand, user form, default / KYTY_FIX_B36=0), fs10_f1 (stand, harness form without KYTY_DIAG_B32, default),
fs10_v (form fs9_v) and fs10_w (form fs9_w).  Rows only, NO VERDICT (the reading is FS10d, HPP-687).  Port of the members of
C:/kyty/f287/f25m/f25m_read.py (stands, LogAsync, exit window) and C:/kyty/f287/fs9c/fs9c_read.py (V / W); standalone (no f25_read.py:
no DiagB32, no cold series).  ASCII only.

    python fs10c_read.py <tag> [--json <out>]                       one tag (files of C:/kyty/f287/fs10c)
    python fs10c_read.py --dir <fixture dir> --tag <tag> [--json <out>]
        fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt, installed_before.txt, installed_after.txt,
        installed_sha.txt, manifest_cmp.txt, level.txt, seal.md, bin.exe
    python fs10c_read.py --table [--runs <dir>]                     the table over every runs/<tag>/read.json

DEFINITIONS (seal docs/track-f/fs10c.md section 3):
  entry line      the first line ending 'GuestOut: Level has started: underwater_aerial_garden'; first GuestOut - the first line
                  carrying 'GuestOut'.
  first scene     harness form (fs10_f1, fs10_v, fs10_w): the first 'FrameTrace: n=' line after the entry line with draws >= 100; the
  frame           frames 'after the first scene frame' are the FrameTrace lines after it (the first itself not counted; a row prints the
                  count with it).  User form (fs10_s1, fs10_s0; no FrameTrace): the letter 'after the first scene frame' is read as
                  'LongFrame lines after the entry line in log order' (executor variant, named); the whole-log count is printed beside.
  sleep           'TestLogStall: i=<i> sleep_ms=<ms> slept_us=<us> t0_ms=<a> t1_ms=<b> on=<caller|writer> tid=<t> role=<r> line="<..>"';
                  window of a sleep [t0_ms - 2 000; t1_ms + 2 000] (edges included) on the clock of LongFrame t_ms (FrameStats::NowNs).
  exit window     (items 616 (b)(2), 618 (b)(5)) the estimated exit at_ms - 60 000 + 1 000 x (stable_s + hold_s) is >= 250 ms after
                  t1_ms + 2 000 of the last sleep - a member of each stand.
  LogAsync        'LogAsync: mode=1 ' line before the first GuestOut (member of every tag at the default; item 626 (g): 'LogAsync:
                  mode=0 requested=1 reason=direction' = the writer is OFF - the member fails); the summary 'LogAsync: full_waits=' with
                  all fields; at the default its absence = INTERFERENCE 'run' (item 615 (b)(6): killed; repeat by the lead's item);
                  fs10_s0 (KYTY_FIX_B36=0) - no 'LogAsync:' line at all (member).
ADMISSION (a failed member - INTERFERENCE, not read): json; binary_sha256 = FS10; installed during the tag = FS10; installed before = after
  = FS9; prereg = seal sha256; env = the form exactly (KYTY_* / VK_*; path values of KYTY_GATE_FILE, KYTY_SAMPLE_GATE, KYTY_REC any); last
  --vulkan-validation true only at fs10_w; --shader-validation false; no --rd; -lvl underwater_aerial_garden and the harness level file;
  hold option; log; entry outcome ok; window lines minimized / Recovering Vulkan swapchain 0; signature 9177b426 and the catalog
  variant_fixb26_fixb1b_fixf10_fixf19; GamePatch: 0; caches returned (manifest cmp EQUAL); no KYTY_DIAG_B32 effect (DiagB32 lines 0);
  stands: one 'TestLogStall: config' sleep_ms 3000 k 3, three sleeps i=1,2,3 slept_us >= 2 900 000, all after the entry line (user form)
  / after the first scene frame (harness form) by log order; user form: 0 FrameTrace lines, hold >= 120 s lived, 0 death markers; harness
  stand: scene entered, scene >= 120 s, 0 death markers; non-stands: no TestLogStall line.
MEMBERS:
  fs10_s1  LogAsync: mode=1 before the first GuestOut; 3 sleeps on=writer; 0 LongFrame dt_us >= 1 000 000 after the first scene frame
           (user-form reading above); >= 3 'LogAsync: stall' us >= 2 900 000; full_waits 0; drain_timeouts 0; exit window.
  fs10_s0  0 'LogAsync:' lines; 3 sleeps on=caller; every sleep >= 1 LongFrame dt_us >= 2 500 000 in its window; exit window.
  fs10_f1  LogAsync: mode=1 before the first GuestOut; 3 sleeps on=writer; 0 FrameTrace frames dt_us >= 1 000 000 after the first scene
           frame; >= 3 'LogAsync: stall' us >= 2 900 000; summary present, full_waits 0, drain_timeouts 0.
  fs10_v   hold >= 300 s after the first scene frame; lived; 0 death markers; 0 frames >= 1 s after the first scene frame; video index
           >= 3 000; 0 one-frame glitches; sheet made; LogAsync: mode=1 before the first GuestOut; summary present; drain_timeouts 0;
           FixB13: mode=1 before the first GuestOut (form fs9_v).
  fs10_w   lived (hold_s >= 310); 0 death markers; 0 [Vulkan][E]; 0 limit lines of the layer; [Vulkan][W] > 0; DualSrcBlend:
           supported=1 enabled=1 and LogAsync: mode=1 before the first GuestOut; no VALIDATION_STOP; FixB13: mode=1 (form fs9_w).
"""
import hashlib
import json
import os
import re
import sys

G = 'C:/kyty/f287/fs10c'
SEAL_PATH = G + '/pred/fs10c_seal.md'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_abfded5e.exe'
BIN_FS10 = 'abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe'
BIN_FS9 = '3861eeeae6f2487682b0519195c10d2b4d927029462e695f3634b5bdddea4eb5'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1905-gdc5d4712'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
TAG_RX = re.compile(r'^(fs10_s[01]|fs10_f1|fs10_v|fs10_w)(_r[1-3])?$')
STAND = '60:3000:3'
STAND_AT_MS = 60000
K2_US = 1000000
LF_S0_US = 2500000
STALL_US = 2900000
WIN_MS = 2000
EXIT_MS = 250
HOLD_STAND_S = 120
HOLD_V_US = 300000000
HOLD_W_S = 310
VIDEO_MIN = 3000
LIMIT = '100000000'
VKLAYER = 'C:/VulkanSDK/1.4.357.0/Bin'
RX_LF = re.compile(rb'^LongFrame: n=(\d+) dt_us=(\d+) log_async=(\d+) t_ms=(\d+)\s*$')
RX_ST = re.compile(rb'^LogAsync: stall us=(\d+) queued_bytes=(\d+) t_ms=(\d+)( flush=1)?\s*$')
RX_SL = re.compile(rb'^TestLogStall: i=(\d+) sleep_ms=(\d+) slept_us=(\d+) t0_ms=(\d+) t1_ms=(\d+) on=(\w+) tid=(\d+) role=(\w+)'
                   rb'(?: line="([^"]*)")?\s*$')
RX_CFG = re.compile(rb'^TestLogStall: config at_ms=(\d+) sleep_ms=(\d+) k=(\d+) gap_ms=(\d+) on=(\w+)\s*$')
RX_SUM = re.compile(rb'^LogAsync: full_waits=\d+ ')
RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_B13 = re.compile(rb'FixB13: mode=(\d+)')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d) enabled=(\d)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
SEED = re.compile(rb':KytySC3:([0-9a-f]{40}):')
M_LIMIT = b'this will be the last time reporting it'
M_FORK = b'Fork build arigandores/KytyPS5 '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
SUM_KEYS = ('full_waits', 'full_wait_us', 'stalls', 'stall_cut', 'lines', 'bytes', 'max_queued_bytes', 'sync_lines', 'drain_timeouts')


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


def base_of(tag):
    return TAG_RX.match(tag).group(1)


def kind_of(base):
    return {'fs10_s1': 'stand_user', 'fs10_s0': 'stand_user', 'fs10_f1': 'stand_harness', 'fs10_v': 'v', 'fs10_w': 'w'}[base]


def expected_env(base):
    """Every KYTY_* / VK_* key of the tag json env -> the value (None: any value; the path keys)."""
    k = kind_of(base)
    e = dict(KYTY_GUEST_ARGS='-lvl ' + SKY)
    if k == 'stand_user':
        e.update(KYTY_LONGFRAME='1', KYTY_TEST_LOGSTALL=STAND)
        if base == 'fs10_s0':
            e['KYTY_FIX_B36'] = '0'
        return e
    e.update(KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None, KYTY_QUEUE_TRACE='1', KYTY_GPU_CLOCK_PIN='1',
             KYTY_GPU_MARKERS='0')
    if k == 'stand_harness':
        e.update(KYTY_GPU_WALL='1', KYTY_GPU_HANG_ABORT_S='22', KYTY_LONGFRAME='1', KYTY_TEST_LOGSTALL=STAND, KYTY_REC=None)
    elif k == 'v':
        e.update(KYTY_GPU_HANG_ABORT_S='8', KYTY_REC=None)
    else:
        e.update(KYTY_GPU_HANG_ABORT_S='8', VK_LAYER_PATH=VKLAYER, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=LIMIT)
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


def scan(path):
    """One pass over the log."""
    import lzma
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    r = dict(lf=[], lf_bad=0, stall=[], stall_bad=0, sleep=[], sleep_bad=0, cfg=[], mode=[], summary=[], summary_bad=0, ft=[],
             entry_ln=None, first_guest_ln=None, death=[], minimized=0, recovering=0, win={}, b13=[], dual=[], vke=0, vkw=0, vk_limit=0,
             lines=0, sig=[], variant_dir=[], gamepatch=0, diagb32=0, fork=None)
    lvl = ('GuestOut: Level has started: %s' % SKY).encode()
    ln = 0
    for line in fh:
        ln += 1
        if line.startswith(b'FrameTrace: n='):
            m = RX_FT.match(line)
            if m:
                d = RX_DRAWS.search(line)
                r['ft'].append((int(m.group(1)), int(m.group(2)), int(d.group(1)) if d else None, ln))
            continue
        if line.startswith(b'FrameTrace'):
            continue
        if line.startswith(b'DiagB32'):
            r['diagb32'] += 1
            continue
        if line.startswith(b'LongFrame:'):
            m = RX_LF.match(line)
            if m:
                r['lf'].append(dict(n=int(m.group(1)), dt_us=int(m.group(2)), log_async=int(m.group(3)), t_ms=int(m.group(4)), ln=ln))
            else:
                r['lf_bad'] += 1
            continue
        if line.startswith(b'LogAsync:'):
            if line.startswith(b'LogAsync: stall '):
                m = RX_ST.match(line)
                if m:
                    r['stall'].append(dict(us=int(m.group(1)), queued=int(m.group(2)), t_ms=int(m.group(3)), flush=bool(m.group(4)), ln=ln))
                else:
                    r['stall_bad'] += 1
            elif line.startswith(b'LogAsync: mode='):
                r['mode'].append((line.decode('ascii', 'replace').strip()[:160], ln))
            elif RX_SUM.match(line):
                f = dict(tok.split('=', 1) for tok in line.decode('ascii', 'replace').strip().split(' ')[1:] if '=' in tok)
                if all(k in f for k in SUM_KEYS):
                    r['summary'].append(dict((k, num(f[k])) for k in SUM_KEYS))
                else:
                    r['summary_bad'] += 1
            else:
                r['summary_bad'] += 1
            continue
        if line.startswith(b'TestLogStall:'):
            if line.startswith(b'TestLogStall: config '):
                m = RX_CFG.match(line)
                if m:
                    r['cfg'].append(dict(at_ms=int(m.group(1)), sleep_ms=int(m.group(2)), k=int(m.group(3)), gap_ms=int(m.group(4)),
                                         on=m.group(5).decode()))
                else:
                    r['sleep_bad'] += 1
                continue
            m = RX_SL.match(line)
            if m:
                r['sleep'].append(dict(i=int(m.group(1)), sleep_ms=int(m.group(2)), slept_us=int(m.group(3)), t0_ms=int(m.group(4)),
                                       t1_ms=int(m.group(5)), on=m.group(6).decode(), tid=int(m.group(7)), role=m.group(8).decode(),
                                       line=None if m.group(9) is None else m.group(9).decode('ascii', 'replace'), ln=ln))
            else:
                r['sleep_bad'] += 1
            continue
        if r['entry_ln'] is None and line.rstrip(b'\r\n').endswith(lvl):
            r['entry_ln'] = ln
        if r['first_guest_ln'] is None and b'GuestOut' in line:
            r['first_guest_ln'] = ln
        m = RX_B13.search(line)
        if m:
            r['b13'].append((int(m.group(1)), ln))
        m = RX_DUAL.search(line)
        if m:
            r['dual'].append((m.group(1) == b'1' and m.group(2) == b'1', ln))
        if b'[Vulkan][E]' in line:
            r['vke'] += 1
        if b'[Vulkan][W]' in line:
            r['vkw'] += 1
        if M_LIMIT in line:
            r['vk_limit'] += 1
        if line.startswith(b'GamePatch:'):
            r['gamepatch'] += 1
        if r['fork'] is None and M_FORK in line:
            r['fork'] = line.decode('ascii', 'replace').strip()[:160]
        if line.startswith(b'ShaderSeed: compatibility=') and len(r['sig']) < 4:
            mm = SEED.search(line)
            r['sig'].append(mm.group(1).decode('ascii') if mm else '?')
        if line.startswith(b'Shader translation cache: ') and len(r['variant_dir']) < 4:
            r['variant_dir'].append(line.decode('ascii', 'replace').strip().replace('\\', '/').rsplit('/', 1)[-1])
        for dm in DEATH:
            if dm in line and len(r['death']) < 20:
                r['death'].append(dm.decode())
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


def first_scene(x):
    """(index in x['ft'] of the first scene frame or None, rows after it)."""
    ent = x['entry_ln']
    if ent is None:
        return None, []
    for i, (n, dt, draws, ln) in enumerate(x['ft']):
        if ln > ent and draws is not None and draws >= 100:
            return i, x['ft'][i + 1:]
    return None, []


def mode_member(x):
    g = x['first_guest_ln']
    ok = len(x['mode']) == 1 and x['mode'][0][0].startswith('LogAsync: mode=1 ') and (g is None or x['mode'][0][1] < g)
    ok = ok and g is not None
    return ('LogAsync: mode=1 exactly once, before the first GuestOut (lines %s, first GuestOut %s)' % (
        [(t[:40], l) for t, l in x['mode'][:2]], g), ok)


def b13_member(x):
    g = x['first_guest_ln']
    ok = bool(x['b13']) and all(v == 1 for v, l in x['b13']) and g is not None and x['b13'][0][1] < g
    return ('FixB13: mode=1 (every line) before the first GuestOut (%s; first GuestOut %s) - form fs9_v / fs9_w' % (x['b13'][:3], g), ok)


def summary_of(x):
    return x['summary'][-1] if x['summary'] else None


def exit_member(x, att):
    cfg = x['cfg'][0] if x['cfg'] else None
    sl = x['sleep']
    st, hs = att.get('stable_s'), att.get('hold_s')
    if cfg is None or not sl or st is None or hs is None:
        return ('exit window (item 616 (b)(2), 618 (b)(5)): not computable (config %s, sleeps %d, stable_s %s, hold_s %s)' % (
            bool(cfg), len(sl), st, hs), False, None)
    exit_ms = cfg['at_ms'] - STAND_AT_MS + int(round(1000 * (st + hs)))
    gap = exit_ms - (sl[-1]['t1_ms'] + WIN_MS)
    return ('exit window: estimated exit %d ms - (last t1_ms %d + 2 000) = %d >= %d' % (exit_ms, sl[-1]['t1_ms'], gap, EXIT_MS),
            gap >= EXIT_MS, gap)


def stand_admission(x, kind):
    cfg = x['cfg']
    sl = x['sleep']
    c_ok = len(cfg) == 1 and cfg[0]['sleep_ms'] == 3000 and cfg[0]['k'] == 3
    s_ok = [s['i'] for s in sl] == [1, 2, 3] and all(s['slept_us'] >= 2900000 for s in sl) and x['sleep_bad'] == 0
    if kind == 'stand_user':
        anchor, what = x['entry_ln'], 'the entry line'
    else:
        i, _ = first_scene(x)
        anchor, what = (x['ft'][i][3] if i is not None else None), 'the first scene frame'
    p_ok = anchor is not None and bool(sl) and all(s['ln'] > anchor for s in sl)
    return [('TestLogStall config once: sleep_ms 3000, k 3 (%s)' % cfg[:1], c_ok),
            ('TestLogStall sleeps i=1,2,3, slept_us >= 2 900 000 (%s; bad %d)' % (
                [(s['i'], s['slept_us'], s['on']) for s in sl][:4], x['sleep_bad']), s_ok),
            ('all sleeps after %s by log order (anchor line %s, sleep lines %s)' % (what, anchor, [s['ln'] for s in sl][:4]), p_ok)]


def on_member(x, on):
    sl = x['sleep']
    cfg_on = [c['on'] for c in x['cfg']]
    return ('3 sleeps TestLogStall ... on=%s (sleeps %s, config %s)' % (on, [s['on'] for s in sl], cfg_on),
            len(sl) == 3 and all(s['on'] == on for s in sl) and cfg_on == [on])


def in_win(t, s):
    return s['t0_ms'] - WIN_MS <= t <= s['t1_ms'] + WIN_MS


def members(base, x, att, idx_n, gl, sheet, sd):
    kind = kind_of(base)
    info = {}
    m = []
    summ = summary_of(x)
    st29 = [s for s in x['stall'] if s['us'] >= STALL_US]
    death = x['death'] + sd
    if kind == 'stand_user':
        lf1 = [l for l in x['lf'] if l['dt_us'] >= K2_US]
        lf1_after = [l for l in lf1 if x['entry_ln'] is not None and l['ln'] > x['entry_ln']]
        em = exit_member(x, att)
        info.update(lf=len(x['lf']), lf_ge1s=len(lf1), lf_ge1s_after_entry=len(lf1_after), lf_max=max([l['dt_us'] for l in x['lf']] or [0]),
                    stall_ge29=len(st29), exit_gap_ms=em[2], summary=summ)
        if base == 'fs10_s1':
            m += [mode_member(x), on_member(x, 'writer'),
                  ('0 LongFrame dt_us >= 1 000 000 after the first scene frame (user form: after the entry line by log order) - %d; '
                   'whole log %d' % (len(lf1_after), len(lf1)), not lf1_after),
                  ('>= 3 LogAsync: stall lines us >= 2 900 000 (%d: %s)' % (len(st29), [s['us'] for s in st29][:5]), len(st29) >= 3),
                  ('full_waits 0 (%s)' % (None if summ is None else summ['full_waits']), summ is not None and summ['full_waits'] == 0),
                  ('drain_timeouts 0 (%s)' % (None if summ is None else summ['drain_timeouts']),
                   summ is not None and summ['drain_timeouts'] == 0),
                  (em[0], em[1])]
        else:
            per = []
            for s in x['sleep']:
                hits = [(l['n'], l['dt_us'], l['t_ms']) for l in x['lf'] if l['dt_us'] >= LF_S0_US and in_win(l['t_ms'], s)]
                per.append(dict(i=s['i'], win=[s['t0_ms'] - WIN_MS, s['t1_ms'] + WIN_MS], hits=hits))
            info['per_sleep'] = per
            none = not x['mode'] and not x['summary'] and not x['stall'] and x['summary_bad'] == 0 and x['stall_bad'] == 0
            m += [('0 LogAsync: lines (mode %d, summary %d, stall %d, other %d)' % (len(x['mode']), len(x['summary']), len(x['stall']),
                                                                                   x['summary_bad'] + x['stall_bad']), none),
                  on_member(x, 'caller'),
                  ('every sleep has >= 1 LongFrame dt_us >= 2 500 000 in [t0_ms - 2 000; t1_ms + 2 000] (%d of %d sleeps)' % (
                      sum(1 for p in per if p['hits']), len(per)), len(per) == 3 and all(p['hits'] for p in per)),
                  (em[0], em[1])]
    elif kind == 'stand_harness':
        i, after = first_scene(x)
        ge1 = [(n, dt) for (n, dt, d, ln) in after if dt >= K2_US]
        ge1_with_first = ge1 + ([(x['ft'][i][0], x['ft'][i][1])] if i is not None and x['ft'][i][1] >= K2_US else [])
        lf1 = [l for l in x['lf'] if l['dt_us'] >= K2_US]
        info.update(first_scene_n=None if i is None else x['ft'][i][0], scene_frames=len(after), ge1s=len(ge1),
                    ge1s_with_first=len(ge1_with_first), lf_ge1s_whole=len(lf1), max_dt=max([dt for (n, dt, d, ln) in after] or [0]),
                    stall_ge29=len(st29), summary=summ)
        m += [mode_member(x), on_member(x, 'writer'),
              ('0 FrameTrace frames dt_us >= 1 000 000 after the first scene frame (%d %s; with the first frame %d; LongFrame >= 1 s '
               'whole log %d)' % (len(ge1), ge1[:4], len(ge1_with_first), len(lf1)), i is not None and not ge1),
              ('>= 3 LogAsync: stall lines us >= 2 900 000 (%d: %s)' % (len(st29), [s['us'] for s in st29][:5]), len(st29) >= 3),
              ('summary LogAsync: full_waits= present (%d)' % len(x['summary']), summ is not None),
              ('full_waits 0 (%s)' % (None if summ is None else summ['full_waits']), summ is not None and summ['full_waits'] == 0),
              ('drain_timeouts 0 (%s)' % (None if summ is None else summ['drain_timeouts']), summ is not None and summ['drain_timeouts'] == 0)]
    elif kind == 'v':
        i, after = first_scene(x)
        hold = sum(dt for (n, dt, d, ln) in after)
        ge1 = sum(1 for (n, dt, d, ln) in after if dt >= K2_US)
        lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None
        info.update(first_scene_n=None if i is None else x['ft'][i][0], hold_s=round(hold / 1e6, 1), frames_ge1s=ge1,
                    max_dt=max([dt for (n, dt, d, ln) in after] or [0]), summary=summ)
        m += [('hold >= 300 s after the first scene frame (%.1f s)' % (hold / 1e6), hold >= HOLD_V_US),
              ('the process lived through the hold (outcome %s, hold_exit %s)' % (att.get('outcome'), att.get('hold_exit')), lived),
              ('0 death markers (log and stdout) %s' % death[:3], not death),
              ('0 frames >= 1 s after the first scene frame (%d; first %s)' % (ge1, info['first_scene_n']), i is not None and ge1 == 0),
              ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN),
              ('0 one-frame glitches (%s)' % gl, gl == 0),
              ('sheet for the lead made (%s)' % sheet, bool(sheet)),
              mode_member(x),
              ('summary LogAsync: full_waits= present (%d)' % len(x['summary']), summ is not None),
              ('drain_timeouts 0 (%s)' % (None if summ is None else summ['drain_timeouts']), summ is not None and summ['drain_timeouts'] == 0),
              b13_member(x)]
    else:
        lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None and (att.get('hold_s') or 0) >= HOLD_W_S
        g = x['first_guest_ln']
        dual = [d for d in x['dual'] if d[0] and g is not None and d[1] < g]
        i, after = first_scene(x)
        info.update(frames_ge1s_report=sum(1 for (n, dt, d, ln) in after if dt >= K2_US), vkw=x['vkw'], summary=summ)
        m += [('lived to the end of the hold (outcome %s, hold_exit %s, hold_s %s >= 310)' % (att.get('outcome'), att.get('hold_exit'),
                                                                                          att.get('hold_s')), lived),
              ('0 death markers (log and stdout) %s' % death[:3], not death),
              ('0 [Vulkan][E] (%d)' % x['vke'], x['vke'] == 0),
              ('0 limit lines of the layer (%d)' % x['vk_limit'], x['vk_limit'] == 0),
              ('positive control: [Vulkan][W] %d > 0' % x['vkw'], x['vkw'] > 0),
              ('DualSrcBlend: supported=1 enabled=1 before the first GuestOut (%d)' % len(dual), bool(dual)),
              mode_member(x),
              ('no VALIDATION_STOP (a [Vulkan][E] line and the process did not live to the end of the hold)', not (x['vke'] > 0 and not lived)),
              b13_member(x)]
    return m, info


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha', 'level', 'sheet')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'), bin=os.path.join(base, 'bin.exe'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), seal=SEAL_PATH, bin=BIN_PATH)
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
    base = base_of(tag)
    kind = kind_of(base)
    res = dict(tag=tag, form=base, kind=kind, level=SKY, reader_sha256=sha_file(os.path.abspath(__file__)))
    run = json.load(open(p['run'], encoding='utf-8')) if os.path.exists(p['run']) else None
    jbin = (run or {}).get('binary_sha256')
    res['binary_sha256'] = jbin
    inst_b = (text(p['installed_before']) or '').strip() or None
    inst_a = (text(p['installed_after']) or '').strip() or None
    inst_t = (text(p['installed_sha']) or '').strip() or None
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env = (run or {}).get('env') or {}
    cmd = (run or {}).get('cmdline') or []
    att = ((run or {}).get('attempts') or [{}])[-1]
    mcmp = (text(p['manifest_cmp']) or '').strip().splitlines()
    hlev = (text(p['level']) or '').strip() or None
    ga = (run or {}).get('guest_args') or ''
    have_log = os.path.exists(p['log'])
    x = scan(p['log']) if have_log else None
    ebad = env_diff(dict((k, v) for k, v in env.items() if k.startswith(('KYTY_', 'VK_'))), expected_env(base))
    vv = 'true' if base == 'fs10_w' else 'false'
    hold_opt = {'stand_user': 150, 'stand_harness': 150, 'v': 330, 'w': 310}[kind]
    sd = stdout_death(p['stdout'])
    adm = [
        ('tag json present', run is not None),
        ('json binary_sha256 = FS10 abfded5e (%s)' % (jbin or '-')[:16], jbin == BIN_FS10),
        ('installed during the tag = FS10 (%s)' % (inst_t or '-')[:16], inst_t == BIN_FS10),
        ('installed before = after = FS9 3861eeea (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_FS9 and inst_a == BIN_FS9),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env = the form of the tag (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad),
        ('last --vulkan-validation %s (%s)' % (vv, last_flag(cmd, '--vulkan-validation')), last_flag(cmd, '--vulkan-validation') == vv),
        ('last --shader-validation false (%s)' % last_flag(cmd, '--shader-validation'), last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args -lvl %s (%s; harness %s)' % (SKY, ga, hlev), ga == '-lvl ' + SKY and hlev == SKY),
        ('hold option %d s (%s)' % (hold_opt, (run or {}).get('hold_s')), (run or {}).get('hold_s') == hold_opt),
        ('log present', have_log),
        ('entry outcome ok (%s)' % att.get('outcome'), att.get('outcome') == 'ok'),
        ('entry line present (%s)' % (x or {}).get('entry_ln'), x is not None and x['entry_ln'] is not None),
        ('window events: minimized %s, Recovering Vulkan swapchain %s (all %s)' % ((x or {}).get('minimized'), (x or {}).get('recovering'),
                                                                                  (x or {}).get('win')),
         x is not None and x['minimized'] == 0 and x['recovering'] == 0),
        ('translation signature 9177b426 and cache dir %s (%s / %s)' % (VARIANT_DIR, [z[:8] for z in (x or {}).get('sig') or []],
                                                                       (x or {}).get('variant_dir')),
         x is not None and x['sig'] == [SIG] and x['variant_dir'] == [VARIANT_DIR]),
        ('no GamePatch: line (%s)' % (x or {}).get('gamepatch'), x is not None and x['gamepatch'] == 0),
        ('no DiagB32 line - no KYTY_DIAG_B32 (%s)' % (x or {}).get('diagb32'), x is not None and x['diagb32'] == 0),
        ('caches returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'), bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),
    ]
    why = None
    if x is not None:
        if base != 'fs10_s0':
            ok = len(x['summary']) == 1 and x['summary_bad'] == 0
            adm.append(('summary line LogAsync: full_waits= present once, all fields (%d, bad %d) - absent: killed (item 615 (b)(6))' % (
                len(x['summary']), x['summary_bad']), ok))
            if not ok and not x['summary']:
                why = 'run (item 615 (b)(6): no summary line at the default - killed; repeat by the lead; LongFrame / stall not read)'
        if kind in ('stand_user', 'stand_harness'):
            adm += stand_admission(x, kind)
        else:
            adm.append(('no TestLogStall line (%d / %d)' % (len(x['cfg']), len(x['sleep'])), not x['cfg'] and not x['sleep']))
        if kind == 'stand_user':
            adm += [('hold >= %d s, lived (hold_s %s, hold_exit %s)' % (HOLD_STAND_S, att.get('hold_s'), att.get('hold_exit')),
                     (att.get('hold_s') or 0) >= HOLD_STAND_S and att.get('hold_exit') is None),
                    ('user form: 0 FrameTrace lines (%d)' % len(x['ft']), not x['ft']),
                    ('no death marker (log %s, stdout %s)' % (x['death'][:3], sd), not x['death'] and not sd)]
        elif kind == 'stand_harness':
            i, after = first_scene(x)
            scene_s = sum(dt for (n, dt, d, ln) in after) / 1e6
            adm += [('scene entered and scene >= %d s (first %s, %.1f s)' % (HOLD_STAND_S, None if i is None else x['ft'][i][0], scene_s),
                     i is not None and scene_s >= HOLD_STAND_S),
                    ('no death marker (log %s, stdout %s)' % (x['death'][:3], sd), not x['death'] and not sd)]
    res['admission'] = [[a, bool(b)] for a, b in adm]
    admitted = all(b for _, b in adm)
    res['status'] = 'ADMITTED' if admitted else 'INTERFERENCE'
    res['interference'] = None if admitted else (why or 'admission member: %s' % [a for a, b in adm if not b][:3])
    res['admitted'] = admitted
    idx_n = None
    if os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as fi:
            idx_n = sum(1 for _ in fi)
    gl = None
    gt = text(p['glitch'])
    if gt:
        mg = RX_GL.search(gt)
        gl = int(mg.group(1)) if mg else None
    sheet = (text(p['sheet']) or '').strip()[:120] or None
    binv = None
    if os.path.exists(p['bin']):
        binv = VERSION in open(p['bin'], 'rb').read()
    res['ref'] = dict(glitches=gl, video_index=idx_n, outcome=att.get('outcome'), hold_exit=att.get('hold_exit'), hold_s=att.get('hold_s'),
                      stable_s=att.get('stable_s'), sheet=sheet, bin_version_string=binv, fork_line=(x or {}).get('fork'),
                      lines=(x or {}).get('lines'))
    res['sleeps'] = [dict(i=s['i'], slept_us=s['slept_us'], t0_ms=s['t0_ms'], t1_ms=s['t1_ms'], on=s['on'], tid=s['tid'], role=s['role'],
                          line=s['line']) for s in (x or {}).get('sleep') or []]
    stalls = (x or {}).get('stall') or []
    res['stalls'] = [(s['us'], s['t_ms'], s['flush']) for s in stalls][:20]
    res['S'] = sum(1 for s in stalls if s['us'] >= K2_US)
    res['members'] = None
    res['info'] = None
    res['ok'] = None
    if x is not None and admitted:
        m, info = members(base, x, att, idx_n, gl, sheet, sd)
        res['members'] = [[a, bool(b)] for a, b in m]
        res['info'] = info
        res['ok'] = all(b for _, b in m)
    res['reading'] = ('ADMITTED, members %s (no verdict; reading - FS10d)' % ('ALL YES' if res['ok'] else 'NOT ALL YES')) if admitted else (
        'INTERFERENCE: %s' % res['interference'])
    return res


def rows_out(res):
    out = ['tag %s (form %s, kind %s, level %s)  reader sha256 %s' % (res['tag'], res['form'], res['kind'], res['level'],
                                                                      res['reader_sha256'])]
    out.append('  ADMISSION %s; STATUS %s' % ('PASS' if res['admitted'] else 'FAIL', res['status']))
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    out.append('  binary_sha256 %s' % res['binary_sha256'])
    for s in res['sleeps']:
        out.append('  SLEEP i %d slept_us %d t0_ms %d t1_ms %d on %s tid %d role %s line="%s"' % (
            s['i'], s['slept_us'], s['t0_ms'], s['t1_ms'], s['on'], s['tid'], s['role'], s['line'] if s['line'] is not None else '<absent>'))
    out.append('  LogAsync stall lines %s; S (us >= 1 000 000) %d' % (res['stalls'][:6], res['S']))
    if res['members'] is not None:
        out.append('  MEMBERS %s %s' % (res['form'], 'ALL YES' if res['ok'] else 'NOT ALL YES'))
        for a, b in res['members']:
            out.append('    [%s] %s' % ('YES' if b else 'NO', a))
        out.append('  INFO %s' % json.dumps(res['info'], sort_keys=True, default=list)[:900])
    rf = res['ref']
    out.append('  REFERENCE: %s' % json.dumps(rf, sort_keys=True))
    out.append('  READING %s' % res['reading'])
    return out


def table(rd):
    out = ['| tag | status | binary_sha256 | members | S | glitches | video index | hold_s |', '|' + '---|' * 8]
    if os.path.isdir(rd):
        for t in sorted(os.listdir(rd)):
            js = os.path.join(rd, t, 'read.json')
            if TAG_RX.match(t) and os.path.exists(js):
                r = json.load(open(js, encoding='utf-8'))
                out.append('| %s | %s | %s | %s | %d | %s | %s | %s |' % (
                    t, r['status'], (r['binary_sha256'] or '-')[:8], '-' if r['ok'] is None else ('ALL YES' if r['ok'] else 'NOT ALL YES'),
                    r['S'], r['ref']['glitches'], r['ref']['video_index'], r['ref']['hold_s']))
    return out


def main(argv):
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader fs10c_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for l in table(rd):
            print(l)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        p = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        p = paths(tag)
    if not TAG_RX.match(tag):
        print('usage: fs10c_read.py fs10_s1|fs10_s0|fs10_f1|fs10_v|fs10_w[_r1..3] | --dir D --tag T | --table')
        return 2
    res = read_tag(tag, p)
    for l in rows_out(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
