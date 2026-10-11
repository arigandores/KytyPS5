"""Track F link F42c (HPP-781; ROADMAP s122 item 694 (g)(6), item 705 (b)(5) and (v) N1, item 713, item 719): the reader of the tags
f20_v / f20_hb / f20_w of the F42a2 binary 1994a0ce (worktree 730ed40a + F42a + F42a2, HEAD 5ccb1d31, version
KytyPS5-2026-09-15-6a2987a-1917-g5ccb1d31) at KYTY_FIX_F20=1, other FS12 defaults; installed FS13 abab2196 before and after (item 703-704).
Rows only, NO VERDICT (the reading is F42d, HPP-782).  Port of C:/kyty/f287/f44c/f44c_read.py (F44c, HPP-793; the form fs12_v) and of the
W part of C:/kyty/f287/fs13c/fs13c_read.py (FS13c, HPP-789; the form fs12_w) with: the tag binary 1994a0ce, KYTY_FIX_F20=1 in the env of
every tag, the level hoover_beach at f20_hb, the series form of the caches (seal section 2: _ShaderCache, _ShaderSeeds, _PipelineCache and
GLCache are copied once before f20_v and returned once after the last tag by the call f42c_ret; _SaveData is copied and returned at every
tag), the members 'FixF20: mode=1' and 'FixF20Stat: when=exit' (unmatched 0, modules_bound = modules, rewritten >= 11) and the rows of the
preparation screen, PipelinePrecache, the driver blob size and FixF20Stat.  ASCII only.

    python f42c_read.py <tag> [--json <out>]                       one tag (files of C:/kyty/f287/f42c)
    python f42c_read.py --dir <fixture dir> --tag <tag> [--json <out>]
        fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt, installed_before.txt, installed_after.txt,
        installed_sha.txt, manifest_cmp.txt, level.txt, series_taken.txt, same_cmp.txt, cache_before.tsv, cache_after.tsv, seal.md, bin.exe
    python f42c_read.py --table [--runs <dir>]                     the table over every runs/<tag>/read.json

DEFINITIONS (seal pred/f42c_seal.md section 4):
  entry line      the first line ending 'GuestOut: Level has started: <level>' (underwater_aerial_garden at f20_v / f20_w, hoover_beach at
                  f20_hb); first GuestOut - the first line carrying 'GuestOut'.
  first scene     the first 'FrameTrace: n=' line after the entry line with draws >= 100; the frames 'after the first scene frame' are the
  frame           FrameTrace lines after it (the first itself not counted; a row prints the count with it).
  FixF20          'FixF20: mode=<0|1>' (fixF20.cpp Mode(), once per process, the PipelineCache constructor): >= 1 parsed line, no
                  unparsable line, every line mode=1, the first before the first GuestOut.
  FixF20Stat      'FixF20Stat: when=<w> calls=<n> modules_bound=<n> modules=<n> sites=<n> rewritten=<n> unmatched=<n>' (fixF20.cpp
                  PrintStat; when=periodic every 4 096 modules, when=exit at the end of Execute - emulator.cpp, after WindowRun); the
                  exit line - the last parsed line with when=exit.
  N1              (item 705 (v)): the tag is closed by the window ('Event: quit'); with 'Event: quit' the line 'FixF20Stat: when=exit'
                  after it is obligatory - member 'Event: quit present and a FixF20Stat: when=exit line after it'; Event: quit with no
                  exit line - a defect of the witness: post_f42c.sh writes SERIES_STOP (question to the lead).
  quit            the first log line containing 'Event: quit' (the harness exit, WM_CLOSE posted at the end of the hold).
ADMISSION (a failed member - NOT_ADMITTED, not read; a repeat by the lead's item): json; binary_sha256 = F42a2 1994a0ce; installed during
  the tag = 1994a0ce; installed before = after = FS13 abab2196; prereg = seal sha256; env = the form exactly (KYTY_* / VK_*; path values
  of KYTY_GATE_FILE, KYTY_SAMPLE_GATE, KYTY_REC any; KYTY_FIX_F20 = '1'; no other KYTY_FIX_*, no KYTY_GAME_PATCH); no KYTY_TEST_* key in
  the env and 0 'ExitFatal:' lines (log and stdout); last --vulkan-validation true only at f20_w, else false; --shader-validation false;
  no --rd; -lvl <level> and the harness level file; hold option (330 / 330 / 310); log; stdout; entry outcome ok; entry line; window
  lines minimized / Recovering Vulkan swapchain 0; signature 9177b426 and the catalog variant_fixb26_fixb1b_fixf10_fixf19; GamePatch: 0;
  DiagB32 lines 0; TestLogStall lines 0; _SaveData returned (manifest cmp EQUAL); the summary line 'LogAsync: full_waits=' once with all
  fields (absent: killed - item 615 (b)(6)); series: f20_v - the series snapshot taken in this call (series_taken.txt 'series snapshot
  taken'); f20_hb / f20_w - the caches before the tag = after the previous tag of the series (same_cmp.txt 'same caches EQUAL':
  _ShaderCache, _ShaderSeeds, _PipelineCache; GLCache is a row).
MEMBERS (letter of item 694 (g)(6) with item 705 (v) N1):
  f20_v   hold >= 300 s after the first scene frame; lived; 0 death markers (log and stdout); 0 frames >= 1 s after the first scene frame;
          video index >= 3 000; 0 one-frame glitches; sheet made; FixF20: mode=1 before the first GuestOut; FixF20Stat exit line:
          unmatched 0, modules_bound = modules, rewritten >= 11; N1.
  f20_hb  hold >= 300 s; lived; 0 death markers; 0 frames >= 1 s; video >= 3 000; 0 glitches; sheet made; N1.
  f20_w   lived to the end of the hold (hold_s >= 310); 0 death markers; 0 [Vulkan][E]; 0 limit lines of the layer; [Vulkan][W] > 0
          (positive control of the layer); N1.
  + group 'form' (not the letter; printed separately): f20_v / f20_hb - the form fs12_v (FixF21: mode=1, FixB12: mode=1, Event: quit,
  0 Fatal after it, 0 wait_expired, ended before the harness timeout, LogAsync: mode=1, summary, drain_timeouts 0, FixB13: mode=1,
  FixB12Stat: present); f20_hb also FixF20: mode=1, exit line unmatched 0 and modules_bound = modules; f20_w - the form fs12_w
  (DualSrcBlend: supported=1 enabled=1, FixF21, LogAsync, no VALIDATION_STOP, FixB13, FixB12) and FixF20: mode=1, unmatched 0,
  modules_bound = modules.
ROWS (no gate, item 694 (v)(2)(v)): the preparation screen 'ShaderPreparation: startup wait finished in <ms> ms'; the 'PipelinePrecache:'
  lines; the 'Vulkan pipeline cache:' lines (loaded / saved); the driver blob: bytes of _PipelineCache and of GLCache before and after the
  tag (cache_before.tsv / cache_after.tsv); every FixF20Stat line (count, periodic count, the exit line, the maximum unmatched); exit code
  close_rc and close_s.
"""
import hashlib
import json
import os
import re
import sys

G = 'C:/kyty/f287/f42c'
SEAL_PATH = G + '/pred/f42c_seal.md'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_1994a0ce.exe'
BIN_TAG = '1994a0ced45c8135f17c8d2aa568278c66375250f1667430c83ba4d0b1a93f29'
BIN_INST = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'
BIN_INST14 = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1917-g5ccb1d31'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
HB = 'hoover_beach'
VKLAYER = 'C:/VulkanSDK/1.4.357.0/Bin'
LIMIT = '100000000'
TAG_RX = re.compile(r'^(f20_v|f20_hb|f20_w)(_r[1-3])?$')
LEVEL_OF = {'v': SKY, 'hb': HB, 'w': SKY}
HOLD_OPT = {'v': 330, 'hb': 330, 'w': 310}
K2_US = 1000000
HOLD_V_US = 300000000
HOLD_W_S = 310
VIDEO_MIN = 3000
REWRITTEN_MIN = 11
RX_SUM = re.compile(rb'^LogAsync: full_waits=\d+ ')
RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_B13 = re.compile(rb'FixB13: mode=(\d+)')
RX_B12 = re.compile(rb'FixB12: mode=(\d+)\s*$')
RX_B12S = re.compile(rb'FixB12Stat: passes=(\d+) rewalk=(\d+) rwd=(\d+) lskip=(\d+)\s*$')
RX_F21 = re.compile(rb'FixF21: mode=(\d+) wait_ms=(\d+)\s*$')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d) enabled=(\d)')
RX_F20 = re.compile(rb'FixF20: mode=(\d+)\s*$')
RX_F20S = re.compile(rb'FixF20Stat: when=([a-z]+) calls=(\d+) modules_bound=(\d+) modules=(\d+) sites=(\d+) rewritten=(\d+) '
                     rb'unmatched=(\d+)\s*$')
RX_PREP = re.compile(rb'ShaderPreparation: startup wait finished in (\d+) ms')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
SEED = re.compile(rb':KytySC3:([0-9a-f]{40}):')
STAT_KEYS = ('when', 'calls', 'modules_bound', 'modules', 'sites', 'rewritten', 'unmatched')
M_FORK = b'Fork build arigandores/KytyPS5 '
M_QUIT = b'Event: quit'
M_FATAL = b'--- Fatal Error ---'
M_EXPIRED = b'FixF21: wait_expired'
M_STAND = b'ExitFatal:'
M_LIMIT = b'this will be the last time reporting it'
M_PRECACHE = b'PipelinePrecache:'
M_VKPC = b'Vulkan pipeline cache:'
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
    return {'f20_v': 'v', 'f20_hb': 'hb', 'f20_w': 'w'}[base]


def expected_env(kind):
    """Every KYTY_* / VK_* key of the tag json env -> the value (None: any value; the path keys)."""
    e = dict(KYTY_GUEST_ARGS='-lvl ' + LEVEL_OF[kind], KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None,
             KYTY_QUEUE_TRACE='1', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8', KYTY_FIX_F20='1')
    if kind == 'w':
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
    """One pass over the log."""
    import lzma
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    r = dict(mode=[], summary=[], summary_bad=0, other_async=0, ft=[], entry_ln=None, first_guest_ln=None, death=[], minimized=0,
             recovering=0, win={}, b13=[], b12=[], b12_bad=0, stat=[], stat_bad=0, f21=[], f21_bad=0, f21_other=0, expired=0,
             f20=[], f20_bad=0, f20s=[], f20s_bad=0, f20_other=0, prep=[], precache=[], precache_n=0, vkpc=[], vkpc_n=0,
             quit_ln=None, fatal_after_quit=0, fatal_total=0, stand=0, dual=[], vke=0, vkw=0, vk_limit=0, lines=0, sig=[],
             variant_dir=[], gamepatch=0, diagb32=0, stall_lines=0, fork=None)
    lvl = ('GuestOut: Level has started: %s' % level).encode()
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
        if line.startswith(b'TestLogStall:'):
            r['stall_lines'] += 1
            continue
        if b'FixB12Stat:' in line:
            m = RX_B12S.search(line)
            if m:
                r['stat'].append(dict(passes=int(m.group(1)), rewalk=int(m.group(2)), rwd=int(m.group(3)), lskip=int(m.group(4)), ln=ln))
            else:
                r['stat_bad'] += 1
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
        if b'FixF21:' in line:
            if M_EXPIRED in line:
                r['expired'] += 1
            elif b'FixF21: mode=' in line:
                m = RX_F21.search(line)
                if m:
                    r['f21'].append((int(m.group(1)), int(m.group(2)), ln))
                else:
                    r['f21_bad'] += 1
            else:
                r['f21_other'] += 1
        if b'FixF20' in line:
            if b'FixF20Stat:' in line:
                m = RX_F20S.search(line)
                if m:
                    s = dict(zip(STAT_KEYS, [m.group(1).decode()] + [int(m.group(k)) for k in range(2, 8)]))
                    s['ln'] = ln
                    r['f20s'].append(s)
                else:
                    r['f20s_bad'] += 1
            elif b'FixF20: mode=' in line:
                m = RX_F20.search(line)
                if m:
                    r['f20'].append((int(m.group(1)), ln))
                else:
                    r['f20_bad'] += 1
            else:
                r['f20_other'] += 1
        if b'ShaderPreparation: startup wait finished' in line:
            m = RX_PREP.search(line)
            r['prep'].append((int(m.group(1)) if m else None, line.decode('ascii', 'replace').strip()[:200]))
        if M_PRECACHE in line:
            r['precache_n'] += 1
            if len(r['precache']) < 8:
                r['precache'].append(line.decode('ascii', 'replace').strip()[:200])
        if M_VKPC in line:
            r['vkpc_n'] += 1
            if len(r['vkpc']) < 8:
                r['vkpc'].append(line.decode('ascii', 'replace').strip()[:200])
        if M_STAND in line:
            r['stand'] += 1
        if r['quit_ln'] is None and M_QUIT in line:
            r['quit_ln'] = ln
        if M_FATAL in line:
            r['fatal_total'] += 1
            if r['quit_ln'] is not None:
                r['fatal_after_quit'] += 1
        if r['entry_ln'] is None and line.rstrip(b'\r\n').endswith(lvl):
            r['entry_ln'] = ln
        if r['first_guest_ln'] is None and b'GuestOut' in line:
            r['first_guest_ln'] = ln
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
    return ('FixB13: mode=1 (every line) before the first GuestOut (%s; first GuestOut %s)' % (x['b13'][:3], g), ok)


def b12_member(x):
    g = x['first_guest_ln']
    ok = bool(x['b12']) and x['b12_bad'] == 0 and all(v == 1 for v, l in x['b12']) and g is not None and x['b12'][0][1] < g
    return ('FixB12: mode=1 (every line) before the first GuestOut (%s; bad %d; first GuestOut %s)' % (x['b12'][:3], x['b12_bad'], g), ok)


def f21_member(x):
    g = x['first_guest_ln']
    ok = bool(x['f21']) and x['f21_bad'] == 0 and all(v == 1 for v, w, l in x['f21']) and g is not None and x['f21'][0][2] < g
    return ('FixF21: mode=1 (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s)' % (
        x['f21'][:3], x['f21_bad'], g), ok)


def f20_member(x):
    g = x['first_guest_ln']
    ok = bool(x['f20']) and x['f20_bad'] == 0 and all(v == 1 for v, l in x['f20']) and g is not None and x['f20'][0][1] < g
    return ('FixF20: mode=1 (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s) - item 694 (g)(6)' % (
        x['f20'][:3], x['f20_bad'], g), ok)


def exit_stat(x):
    ex = [s for s in x['f20s'] if s['when'] == 'exit']
    return ex[-1] if ex else None


def n1_member(x):
    q = x['quit_ln']
    ex = [s for s in x['f20s'] if s['when'] == 'exit' and q is not None and s['ln'] > q]
    return ('N1 (item 705 (v)): Event: quit present and a FixF20Stat: when=exit line after it (quit %s; exit lines after it %d; '
            'all exit lines %d; unparsable FixF20Stat %d)' % (q, len(ex), len([s for s in x['f20s'] if s['when'] == 'exit']),
                                                              x['f20s_bad']), q is not None and bool(ex))


def stat_members(x, with_rewritten):
    e = exit_stat(x)
    out = [('FixF20Stat exit line: unmatched 0 (%s)' % (None if e is None else e['unmatched']), e is not None and e['unmatched'] == 0),
           ('FixF20Stat exit line: modules_bound = modules (%s / %s)' % (None if e is None else e['modules_bound'],
                                                                         None if e is None else e['modules']),
            e is not None and e['modules_bound'] == e['modules'])]
    if with_rewritten:
        out.append(('FixF20Stat exit line: rewritten >= %d (%s)' % (REWRITTEN_MIN, None if e is None else e['rewritten']),
                    e is not None and e['rewritten'] >= REWRITTEN_MIN))
    return out


def summary_of(x):
    return x['summary'][-1] if x['summary'] else None


def stdout_scan(path):
    """death markers, '--- Fatal Error ---', 'FixF21: wait_expired', 'ExitFatal:' over the whole stdout file; None if absent."""
    if not path or not os.path.exists(path):
        return None
    death, fatal, expired, stand = [], 0, 0, 0
    with open(path, 'rb') as f:
        for line in f:
            for dm in DEATH:
                if dm in line and len(death) < 20:
                    death.append(dm.decode())
            if M_FATAL in line:
                fatal += 1
            if M_EXPIRED in line:
                expired += 1
            if M_STAND in line:
                stand += 1
    return dict(death=death, fatal=fatal, expired=expired, stand=stand)


def scene(x):
    i, after = first_scene(x)
    hold = sum(dt for (n, dt, d, ln) in after)
    ge1 = sum(1 for (n, dt, d, ln) in after if dt >= K2_US)
    ge1_with_first = ge1 + (1 if i is not None and x['ft'][i][1] >= K2_US else 0)
    info = dict(first_scene_n=None if i is None else x['ft'][i][0], hold_s=round(hold / 1e6, 1), frames_ge1s=ge1,
                frames_ge1s_with_first=ge1_with_first, scene_frames=len(after),
                mean_dt_us=(round(hold / len(after), 1) if after else None), max_dt=max([dt for (n, dt, d, ln) in after] or [0]))
    return i, hold, ge1, ge1_with_first, info


def v_form_group(x, att, so):
    summ = summary_of(x)
    s_fatal = None if so is None else so['fatal']
    s_exp = None if so is None else so['expired']
    end_ok = att.get('close_killed') is False and att.get('close_rc') is not None
    return [f21_member(x),
            b12_member(x),
            ('exit by the harness: Event: quit line in the log (%s)' % x['quit_ln'], x['quit_ln'] is not None),
            ('after Event: quit: 0 --- Fatal Error --- (log %d; whole stdout %s)' % (x['fatal_after_quit'], s_fatal),
             x['quit_ln'] is not None and x['fatal_after_quit'] == 0 and s_fatal == 0),
            ('0 FixF21: wait_expired (whole log %d; whole stdout %s)' % (x['expired'], s_exp), x['expired'] == 0 and s_exp == 0),
            ('the process ended before the harness timeout (close_killed %s, close_rc %s, close_wait_s %s)' % (
                att.get('close_killed'), att.get('close_rc'), att.get('close_wait_s')), end_ok),
            mode_member(x),
            ('summary LogAsync: full_waits= present (%d)' % len(x['summary']), summ is not None),
            ('drain_timeouts 0 (%s)' % (None if summ is None else summ['drain_timeouts']), summ is not None and summ['drain_timeouts'] == 0),
            b13_member(x),
            ('FixB12Stat: line present (parsed %d, unparsable %d)' % (len(x['stat']), x['stat_bad']), len(x['stat']) >= 1)]


def members(kind, x, att, idx_n, gl, sheet, so):
    summ = summary_of(x)
    death = x['death'] + ((so or {}).get('death') or [])
    lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None
    i, hold, ge1, ge1_with_first, info = scene(x)
    info.update(summary=summ, quit_ln=x['quit_ln'], fatal_after_quit=x['fatal_after_quit'], fatal_log_total=x['fatal_total'],
                fatal_stdout=None if so is None else so['fatal'], expired_log=x['expired'],
                expired_stdout=None if so is None else so['expired'], vke=x['vke'], vkw=x['vkw'])
    death_m = ('0 death markers (log and stdout) %s' % death[:3], not death and so is not None)
    if kind in ('v', 'hb'):
        m = [('hold >= 300 s after the first scene frame (%.1f s)' % (hold / 1e6), hold >= HOLD_V_US),
             ('the process lived through the hold (outcome %s, hold_exit %s)' % (att.get('outcome'), att.get('hold_exit')), lived),
             death_m,
             ('0 frames >= 1 s after the first scene frame (%d; first %s; with the first frame %d)' % (ge1, info['first_scene_n'],
                                                                                                   ge1_with_first),
              i is not None and ge1 == 0),
             ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN),
             ('0 one-frame glitches (%s)' % gl, gl == 0),
             ('sheet for the lead made (%s)' % sheet, bool(sheet))]
        f = v_form_group(x, att, so)
        if kind == 'v':
            m += [f20_member(x)] + stat_members(x, True) + [n1_member(x)]
        else:
            m += [n1_member(x)]
            f += [f20_member(x)] + stat_members(x, False)
    else:
        lived_w = lived and (att.get('hold_s') or 0) >= HOLD_W_S
        g = x['first_guest_ln']
        dual = [d for d in x['dual'] if d[0] and g is not None and d[1] < g]
        m = [('lived to the end of the hold (outcome %s, hold_exit %s, hold_s %s >= 310)' % (att.get('outcome'), att.get('hold_exit'),
                                                                                         att.get('hold_s')), lived_w),
             death_m,
             ('0 [Vulkan][E] (%d)' % x['vke'], x['vke'] == 0),
             ('0 limit lines of the layer (%d)' % x['vk_limit'], x['vk_limit'] == 0),
             ('positive control: [Vulkan][W] %d > 0' % x['vkw'], x['vkw'] > 0),
             n1_member(x)]
        f = [('DualSrcBlend: supported=1 enabled=1 before the first GuestOut (%d)' % len(dual), bool(dual)),
             f21_member(x),
             mode_member(x),
             ('no VALIDATION_STOP (a [Vulkan][E] line and the process did not live to the end of the hold)',
              not (x['vke'] > 0 and not lived_w)),
             b13_member(x),
             b12_member(x),
             f20_member(x)] + stat_members(x, False)
    return m, f, info


def tsv_bytes(path):
    """{label: bytes} of a manifest_fs4c.py tsv; None if absent."""
    if not path or not os.path.exists(path):
        return None
    out = {}
    for line in open(path, 'rb').read().decode('ascii', 'replace').splitlines():
        p = line.split('\t')
        if len(p) >= 3:
            out[p[0]] = out.get(p[0], 0) + (num(p[2]) or 0)
    return out


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha', 'level', 'sheet', 'series_taken',
             'same_cmp')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'), bin=os.path.join(base, 'bin.exe'),
                 cache_before=os.path.join(base, 'cache_before.tsv'), cache_after=os.path.join(base, 'cache_after.tsv'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), seal=SEAL_PATH, bin=BIN_PATH,
             cache_before=os.path.join(d, 'cache_before.tsv'), cache_after=os.path.join(d, 'cache_after.tsv'))
    return p


def read_tag(tag, p):
    base = base_of(tag)
    kind = kind_of(base)
    level = LEVEL_OF[kind]
    res = dict(tag=tag, form=base, kind=kind, level=level, reader_sha256=sha_file(os.path.abspath(__file__)))
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
    x = scan(p['log'], level) if have_log else None
    kenv = dict((k, v) for k, v in env.items() if k.startswith(('KYTY_', 'VK_')))
    ebad = env_diff(kenv, expected_env(kind))
    test_keys = sorted(k for k in env if k.startswith('KYTY_TEST_'))
    so = stdout_scan(p['stdout'])
    s_stand = None if so is None else so['stand']
    vv = last_flag(cmd, '--vulkan-validation')
    want_vv = 'true' if kind == 'w' else 'false'
    adm = [
        ('tag json present', run is not None),
        ('json binary_sha256 = F42a2 1994a0ce (%s)' % (jbin or '-')[:16], jbin == BIN_TAG),
        ('installed during the tag = F42a2 1994a0ce (%s)' % (inst_t or '-')[:16], inst_t == BIN_TAG),
        ('installed before = after, FS13 abab2196 or FS14 013e1974 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b in (BIN_INST, BIN_INST14) and inst_a == inst_b),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env = the form of the tag (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad),
        ('no KYTY_TEST_* in the env (%s)' % (test_keys or 'none'), run is not None and not test_keys),
        ('0 ExitFatal: lines (log %s; whole stdout %s)' % ((x or {}).get('stand'), s_stand),
         x is not None and x['stand'] == 0 and s_stand == 0),
        ('last --vulkan-validation %s (%s)' % (want_vv, vv), vv == want_vv),
        ('last --shader-validation false (%s)' % last_flag(cmd, '--shader-validation'), last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args -lvl %s (%s; harness %s)' % (level, ga, hlev), ga == '-lvl ' + level and hlev == level),
        ('hold option %d s (%s)' % (HOLD_OPT[kind], (run or {}).get('hold_s')), (run or {}).get('hold_s') == HOLD_OPT[kind]),
        ('log present', have_log),
        ('stdout present', so is not None),
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
        ('no TestLogStall line (%s)' % (x or {}).get('stall_lines'), x is not None and x['stall_lines'] == 0),
        ('_SaveData returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'), bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),
    ]
    if kind == 'v':
        st = (text(p['series_taken']) or '').strip().splitlines()
        adm.append(('series snapshot taken in this call before the install (%s)' % (st[0][:60] if st else '-'),
                    bool(st) and st[0].startswith('series snapshot taken')))
    else:
        sc = (text(p['same_cmp']) or '').strip().splitlines()
        adm.append(('caches before the tag = after the previous tag of the series (_ShaderCache, _ShaderSeeds, _PipelineCache) (%s)' % (
            sc[0][:60] if sc else '-'), bool(sc) and sc[0].startswith('same caches EQUAL')))
    why = None
    if x is not None:
        ok = len(x['summary']) == 1 and x['summary_bad'] == 0
        adm.append(('summary line LogAsync: full_waits= present once, all fields (%d, bad %d) - absent: killed (item 615 (b)(6))' % (
            len(x['summary']), x['summary_bad']), ok))
        if not ok and not x['summary']:
            why = 'run (item 615 (b)(6): no summary line at the default - killed; repeat by the lead)'
    res['admission'] = [[a, bool(b)] for a, b in adm]
    admitted = all(b for _, b in adm)
    res['status'] = 'ADMITTED' if admitted else 'NOT_ADMITTED'
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
    rc = att.get('close_rc')
    res['exit'] = dict(close_rc=rc, close_rc_hex=None if rc is None else '0x%08x' % (rc & 0xffffffff), close_s=att.get('close_s'),
                       close_killed=att.get('close_killed'), close_posted=att.get('close_posted'), close_wait_s=att.get('close_wait_s'),
                       quit_ln=(x or {}).get('quit_ln'), fatal_after_quit=(x or {}).get('fatal_after_quit'),
                       fatal_stdout=None if so is None else so['fatal'])
    cb, ca = tsv_bytes(p['cache_before']), tsv_bytes(p['cache_after'])
    f20s = (x or {}).get('f20s') or []
    ex = exit_stat(x) if x is not None else None
    res['f20_rows'] = dict(
        prep_ms=[a for a, b in (x or {}).get('prep') or []], prep_lines=[b for a, b in (x or {}).get('prep') or []],
        precache_lines=(x or {}).get('precache'), precache_n=(x or {}).get('precache_n'),
        vk_pipeline_cache_lines=(x or {}).get('vkpc'), vk_pipeline_cache_n=(x or {}).get('vkpc_n'),
        blob_pipelinecache_before=None if cb is None else cb.get('_PipelineCache'),
        blob_pipelinecache_after=None if ca is None else ca.get('_PipelineCache'),
        glcache_before=None if cb is None else cb.get('GLCache'), glcache_after=None if ca is None else ca.get('GLCache'),
        shadercache_before=None if cb is None else cb.get('_ShaderCache'), shadercache_after=None if ca is None else ca.get('_ShaderCache'),
        f20stat_lines=len(f20s), f20stat_periodic=len([s for s in f20s if s['when'] == 'periodic']),
        f20stat_unparsable=(x or {}).get('f20s_bad'), f20stat_max_unmatched=max(s['unmatched'] for s in f20s) if f20s else None,
        f20stat_exit=None if ex is None else dict((k, ex[k]) for k in STAT_KEYS),
        f20stat_last=None if not f20s else dict((k, f20s[-1][k]) for k in STAT_KEYS),
        f20_mode_lines=None if x is None else len(x['f20']), f20_unparsable=(x or {}).get('f20_bad'), f20_other=(x or {}).get('f20_other'))
    last_stat = (x or {}).get('stat')[-1] if x is not None and x['stat'] else None
    res['ref'] = dict(glitches=gl, video_index=idx_n, outcome=att.get('outcome'), hold_exit=att.get('hold_exit'), hold_s=att.get('hold_s'),
                      stable_s=att.get('stable_s'), sheet=sheet, bin_version_string=binv, fork_line=(x or {}).get('fork'),
                      lines=(x or {}).get('lines'), vke=(x or {}).get('vke'), vkw=(x or {}).get('vkw'),
                      other_logasync=(x or {}).get('other_async'), f21_lines=None if x is None else len(x['f21']),
                      f21_other=(x or {}).get('f21_other'), stand_log=(x or {}).get('stand'), stand_stdout=s_stand,
                      b12stat_last=last_stat, b12stat_lines=None if x is None else len(x['stat']), env_keys=sorted(kenv))
    res['members'] = None
    res['form_members'] = None
    res['info'] = None
    res['ok'] = None
    res['form_ok'] = None
    if x is not None and admitted:
        m, f, info = members(kind, x, att, idx_n, gl, sheet, so)
        res['members'] = [[a, bool(b)] for a, b in m]
        res['form_members'] = [[a, bool(b)] for a, b in f]
        res['info'] = info
        res['ok'] = all(b for _, b in m)
        res['form_ok'] = all(b for _, b in f)
    res['n1_stop'] = bool(x is not None and x['quit_ln'] is not None and not n1_member(x)[1])
    res['reading'] = ('ADMITTED, members 694(g)(6) %s, members of the form %s (no verdict; reading - F42d)' % (
        'ALL YES' if res['ok'] else 'NOT ALL YES', 'ALL YES' if res['form_ok'] else 'NOT ALL YES')) if admitted else (
        'NOT_ADMITTED: %s' % res['interference'])
    return res


def rows_out(res):
    out = ['tag %s (form %s, level %s)  reader sha256 %s' % (res['tag'], res['form'], res['level'], res['reader_sha256'])]
    out.append('  ADMISSION %s; STATUS %s' % ('PASS' if res['admitted'] else 'FAIL', res['status']))
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    out.append('  binary_sha256 %s' % res['binary_sha256'])
    if res['members'] is not None:
        out.append('  MEMBERS 694(g)(6) %s' % ('ALL YES' if res['ok'] else 'NOT ALL YES'))
        for a, b in res['members']:
            out.append('    [%s] %s' % ('YES' if b else 'NO', a))
        out.append('  MEMBERS form %s' % ('ALL YES' if res['form_ok'] else 'NOT ALL YES'))
        for a, b in res['form_members']:
            out.append('    [%s] %s' % ('YES' if b else 'NO', a))
        out.append('  INFO %s' % json.dumps(res['info'], sort_keys=True, default=list)[:1400])
    r = res['f20_rows']
    out.append('  ROW preparation screen (not a gate): ShaderPreparation ms %s' % r['prep_ms'])
    out.append('  ROW PipelinePrecache (not a gate): %s lines; %s' % (r['precache_n'], ' | '.join(r['precache_lines'] or [])))
    out.append('  ROW Vulkan pipeline cache (not a gate): %s lines; %s' % (r['vk_pipeline_cache_n'],
                                                                         ' | '.join(r['vk_pipeline_cache_lines'] or [])))
    out.append('  ROW driver blob (not a gate): _PipelineCache bytes before %s after %s; GLCache bytes before %s after %s; '
               '_ShaderCache bytes before %s after %s' % (r['blob_pipelinecache_before'], r['blob_pipelinecache_after'], r['glcache_before'],
                                                         r['glcache_after'], r['shadercache_before'], r['shadercache_after']))
    out.append('  ROW FixF20Stat (not a gate beyond the members): lines %s (periodic %s, unparsable %s), max unmatched %s; exit %s; last %s; '
               'FixF20: mode= lines %s, unparsable %s, other FixF20 lines %s' % (
                   r['f20stat_lines'], r['f20stat_periodic'], r['f20stat_unparsable'], r['f20stat_max_unmatched'],
                   json.dumps(r['f20stat_exit'], sort_keys=True), json.dumps(r['f20stat_last'], sort_keys=True), r['f20_mode_lines'],
                   r['f20_unparsable'], r['f20_other']))
    e = res['exit']
    out.append('  ROW exit (not a gate): exit code %s (%s); WM_CLOSE post -> process end %s s; killed %s; posted %s; harness timeout %s s; '
               'Event: quit line %s; --- Fatal Error --- after it %s, whole stdout %s' % (
                   e['close_rc'], e['close_rc_hex'], e['close_s'], e['close_killed'], e['close_posted'], e['close_wait_s'], e['quit_ln'],
                   e['fatal_after_quit'], e['fatal_stdout']))
    if res['n1_stop']:
        out.append('  N1 STOP: Event: quit present and no FixF20Stat: when=exit line after it - a defect of the witness, SERIES_STOP, '
                   'item of the lead (item 705 (v))')
    out.append('  REFERENCE: %s' % json.dumps(res['ref'], sort_keys=True))
    out.append('  READING %s' % res['reading'])
    return out


def table(rd):
    out = ['| tag | status | binary_sha256 | members 694(g)(6) | form | FixF20Stat exit (bound/modules/rewritten/unmatched) | prep ms '
           '| _PipelineCache before / after | exit code | close_s | glitches | video index | hold_s |',
           '|' + '---|' * 13]
    if os.path.isdir(rd):
        for t in sorted(os.listdir(rd)):
            js = os.path.join(rd, t, 'read.json')
            if TAG_RX.match(t) and os.path.exists(js):
                r = json.load(open(js, encoding='utf-8'))
                yn = (lambda v: '-' if v is None else ('ALL YES' if v else 'NOT ALL YES'))
                f = r['f20_rows']
                e = f['f20stat_exit']
                es = '-' if not e else '%s/%s/%s/%s' % (e['modules_bound'], e['modules'], e['rewritten'], e['unmatched'])
                out.append('| %s | %s | %s | %s | %s | %s | %s | %s / %s | %s | %s | %s | %s | %s |' % (
                    t, r['status'], (r['binary_sha256'] or '-')[:8], yn(r['ok']), yn(r['form_ok']), es, f['prep_ms'],
                    f['blob_pipelinecache_before'], f['blob_pipelinecache_after'], r['exit']['close_rc'], r['exit']['close_s'],
                    r['ref']['glitches'], r['ref']['video_index'], r['ref']['hold_s']))
    return out


def main(argv):
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader f42c_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for l in table(rd):
            print(l)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        p = None
    else:
        tag = argv[0] if argv else ''
    if not TAG_RX.match(tag):
        print('usage: f42c_read.py f20_v|f20_hb|f20_w[_r1..3] | --dir D --tag T | --table')
        return 2
    p = paths(tag, argv[argv.index('--dir') + 1]) if '--dir' in argv else paths(tag)
    res = read_tag(tag, p)
    for l in rows_out(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
