"""Track F link FS15c (HPP-822; ROADMAP s122 item 730 (g)(3), acceptance FS15a / FS15b item 732, 733): the reader of the tags
fs15_v / fs15_w / fs15_z of the shipping binary FS15 bfac84be (FS14 eb7e8b91 + a6342c98 + a9d6fd1c + 82570fd2 + 38fc76c1, default
KYTY_FIX_F20=1, version KytyPS5-2026-09-15-6a2987a-1929-g6beb3b73); installed FS14 013e1974 before and after (item 727-728).  Rows only,
NO VERDICT (the reading and the install are FS15d, HPP-823).  Port of C:/kyty/f287/fs14c/fs14c_read.py (FS14c, HPP-814: the forms fs14_v /
fs14_w, the members of F24 / F29 / F25 / F21 / B12, the exit of the form fs12_v) with the FixF20 parts of C:/kyty/f287/f42c/f42c_read.py
(F42c, HPP-781: 'FixF20: mode=', 'FixF20Stat:', the preparation screen, PipelinePrecache, the driver blob).  ASCII only.

    python fs15c_read.py <tag> [--json <out>]                       one tag (files of C:/kyty/f287/fs15c)
    python fs15c_read.py --dir <fixture dir> --tag <tag> [--json <out>]
        fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt, installed_before.txt, installed_after.txt,
        installed_sha.txt, manifest_cmp.txt, level.txt, cache_before.tsv, cache_after.tsv, seal.md, bin.exe
    python fs15c_read.py --table [--runs <dir>]                     the table over every runs/<tag>/read.json

DEFINITIONS (seal pred/fs15c_seal.md section 4):
  entry line      the first line ending 'GuestOut: Level has started: underwater_aerial_garden'; first GuestOut - the first line carrying
                  'GuestOut'.
  first scene     the first 'FrameTrace: n=' line after the entry line with draws >= 100; the frames 'after the first scene frame' are the
  frame           FrameTrace lines after it (the first itself not counted; a row prints the count with it).
  FixF20          'FixF20: mode=<0|1>' (6beb3b73 fixF20.cpp Mode(), once per process): >= 1 parsed line, no unparsable line, every line
                  mode=<want>, the first before the first GuestOut; want 1 at fs15_v / fs15_w (the default, no variable), 0 at fs15_z.
  FixF20Stat      'FixF20Stat: when=<w> calls=<n> modules_bound=<n> modules=<n> sites=<n> rewritten=<n> unmatched=<n>' (fixF20.cpp
                  PrintStat; when=periodic every 4 096 modules, when=exit at the end of Execute after WindowRun, only at mode 1); the exit
                  line - the LAST parsed line with when=exit AFTER the first 'Event: quit' line (none - every exit member NO).
  quit            the first log line containing 'Event: quit' (the harness exit, WM_CLOSE posted at the end of the hold).
  FixF24 / FixF29 / FixF25 / FixF21 / FixB12 / FixB13 / LogAsync / init / init_owner / wait_expired / pump_stop_expired / ExitFatal /
                  F25 / F29 rows - as in fs14c_read.py.
ADMISSION (a failed member - NOT_ADMITTED, not read; a repeat by the lead's item): json; binary_sha256 = FS15 bfac84be; installed during the
  tag = bfac84be; installed before = after = FS14 013e1974; prereg = seal sha256; env = the form exactly (KYTY_* / VK_*; path values of
  KYTY_GATE_FILE, KYTY_SAMPLE_GATE, KYTY_REC any; no KYTY_FIX_* at fs15_v / fs15_w; KYTY_FIX_F20 = '0' and no other KYTY_FIX_* at fs15_z;
  no KYTY_GAME_PATCH); no KYTY_TEST_* key and 0 'ExitFatal:' lines (log and stdout); last --vulkan-validation true only at fs15_w, else
  false; --shader-validation false; no --rd; -lvl underwater_aerial_garden and the harness level file; hold option 330 / 310 / 150; log;
  stdout; entry outcome ok; entry line; window lines minimized / Recovering Vulkan swapchain 0; signature 9177b426 and the catalog
  variant_fixb26_fixb1b_fixf10_fixf19; GamePatch: 0; DiagB32 0; TestLogStall 0; TestHidLoss 0; caches returned (manifest cmp EQUAL); the
  summary line 'LogAsync: full_waits=' once with all fields (absent: killed - item 615 (b)(6)) - 25.
MEMBERS (letter of item 730 (g)(3)):
  fs15_v  the 20 members of fs14_v (hold >= 300 s; lived; 0 death markers; 0 frames >= 1 s; video >= 3 000; 0 glitches; sheet; FixF24:
          mode=1 b24=1, FixF24: init, init_owner alive, init_owner hid = helper = pump != main, FixF25: mode=1, FixF21: mode=1, FixB12:
          mode=1, FixF29: mode=1 before the first GuestOut; Event: quit; 0 Fatal after it; 0 wait_expired; 0 pump_stop_expired; ended
          before the harness timeout) + FixF20: mode=1 before the first GuestOut + FixF20Stat: when=exit line after Event: quit; its
          unmatched 0; its modules_bound = modules; its rewritten >= 11 - 25.
          + group 'form fs14_v' (= fs13_v): LogAsync: mode=1 once; summary; drain_timeouts 0; FixB13: mode=1; FixB12Stat: present - 5.
  fs15_w  lived (hold_s >= 310); 0 death markers; 0 [Vulkan][E]; 0 limit lines of the layer; [Vulkan][W] > 0; DualSrcBlend: supported=1
          enabled=1, FixF20: mode=1 and FixF24: mode=1 b24=1 before the first GuestOut; FixF20Stat: when=exit line after Event: quit; its
          unmatched 0; its modules_bound = modules - 11.
          + group 'form fs14_w': FixF29: mode=1; FixF25: mode=1; FixF21: mode=1; LogAsync: mode=1; no VALIDATION_STOP; FixB13: mode=1;
          FixB12: mode=1 - 7.
  fs15_z  hold >= 120 s after the first scene frame; lived; 0 death markers (log and stdout); FixF20: mode=0 before the first GuestOut;
          FixF20Stat: lines 0 (parsed and unparsable, whole log) - 5.
ROWS (no gate): the preparation screen 'ShaderPreparation: startup wait finished in <ms> ms'; 'PipelinePrecache: all pipelines created,
  <ms> ms' and every 'PipelinePrecache:' line; 'Vulkan pipeline cache:' lines; the driver blob: bytes of _PipelineCache (and GLCache,
  _ShaderCache) before the tag (manifest_before.tsv) and after the run before the return (manifest_run.tsv); every FixF20Stat line (count,
  periodic, unparsable, max unmatched, the exit line, the last line); F24 / F29 / F25 rows; exit code close_rc and close_s (every tag; at
  fs15_z 'the harness exit - a row'); fs15_z: FixF24 / FixF29 / FixF25 / FixF21 / FixB12 mode lines (reference).
"""
import hashlib
import json
import os
import re
import sys

G = 'C:/kyty/f287/fs15c'
SEAL_PATH = G + '/pred/fs15c_seal.md'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_bfac84be.exe'
BIN_TAG = 'bfac84bea0eaec8bf3dae6ab5f67cd480f26921829f64f4a8b467bd50e922d8c'
BIN_INST = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1929-g6beb3b73'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
VKLAYER = 'C:/VulkanSDK/1.4.357.0/Bin'
LIMIT = '100000000'
TAG_RX = re.compile(r'^(fs15_v|fs15_w|fs15_z)(_r[1-3])?$')
K2_US = 1000000
HOLD_V_US = 300000000
HOLD_Z_US = 120000000
HOLD_W_S = 310
HOLD_OPT = {'v': 330, 'w': 310, 'z': 150}
VIDEO_MIN = 3000
REWRITTEN_MIN = 11
OWNER_KEYS = ('hid', 'helper', 'msg', 'pump', 'main')
RX_SUM = re.compile(rb'^LogAsync: full_waits=\d+ ')
RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_B13 = re.compile(rb'FixB13: mode=(\d+)')
RX_B12 = re.compile(rb'FixB12: mode=(\d+)\s*$')
RX_B12S = re.compile(rb'FixB12Stat: passes=(\d+) rewalk=(\d+) rwd=(\d+) lskip=(\d+)\s*$')
RX_F21 = re.compile(rb'FixF21: mode=(\d+) wait_ms=(\d+)\s*$')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d) enabled=(\d)')
RX_F25 = re.compile(rb'FixF25: mode=(\d+)\s*$')
RX_F24 = re.compile(rb'FixF24: mode=(\d+) b24=(\d+)\s*$')
RX_OWNER = re.compile(rb'FixF24: init_owner hid=(\d+) helper=(\d+) msg=(\d+) pump=(\d+) main=(\d+)\s*$')
RX_F29 = re.compile(rb'FixF29: mode=(\d+)\s*$')
RX_F20 = re.compile(rb'FixF20: mode=(\d+)\s*$')
RX_F20S = re.compile(rb'FixF20Stat: when=([a-z]+) calls=(\d+) modules_bound=(\d+) modules=(\d+) sites=(\d+) rewritten=(\d+) '
                     rb'unmatched=(\d+)\s*$')
RX_PREP = re.compile(rb'ShaderPreparation: startup wait finished in (\d+) ms')
RX_ALLP = re.compile(rb'PipelinePrecache: all pipelines created, (\d+) ms')
STAT_KEYS = ('when', 'calls', 'modules_bound', 'modules', 'sites', 'rewritten', 'unmatched')
RX_CTL = re.compile(rb'Controller (?:-?\d+|added|removed)\b')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
SEED = re.compile(rb':KytySC3:([0-9a-f]{40}):')
M_FORK = b'Fork build arigandores/KytyPS5 '
M_QUIT = b'Event: quit'
M_FATAL = b'--- Fatal Error ---'
M_EXPIRED = b'FixF21: wait_expired'
M_STAND = b'ExitFatal:'
M_LIMIT = b'this will be the last time reporting it'
M_F25FAIL = b'FixF25: read failed twice'
M_DIRECT = b'KernelRead: direct read failed'
M_PUMPX = b'FixF24: pump_stop_expired'
M_OVF = b'FixF29: overflow'
M_ACC = b'Accessed non-GPU cached memory'
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
    return {'fs15_v': 'v', 'fs15_w': 'w', 'fs15_z': 'z'}[base]


def expected_env(kind):
    """Every KYTY_* / VK_* key of the tag json env -> the value (None: any value; the path keys)."""
    e = dict(KYTY_GUEST_ARGS='-lvl ' + SKY, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None, KYTY_QUEUE_TRACE='1',
             KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8')
    if kind == 'w':
        e.update(VK_LAYER_PATH=VKLAYER, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=LIMIT)
    else:
        e.update(KYTY_REC=None)
    if kind == 'z':
        e.update(KYTY_FIX_F20='0')
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


def first_of(r, key, line):
    if r[key] is None:
        r[key] = line.decode('ascii', 'replace').strip()[:160]


def scan(path):
    """One pass over the log."""
    import lzma
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    r = dict(mode=[], summary=[], summary_bad=0, other_async=0, ft=[], entry_ln=None, first_guest_ln=None, death=[], minimized=0,
             recovering=0, win={}, b13=[], b12=[], b12_bad=0, stat=[], stat_bad=0, f21=[], f21_bad=0, f21_other=0, expired=0,
             f25=[], f25_bad=0, f25_other=0, f25_fail=0, direct=0, f25_fail_first=None, direct_first=None,
             f24=[], f24_bad=0, init=[], owner=[], owner_bad=0, pumpx=0, upd_long=0, open_failed=0, add_event=0, wait_error=0, f24_other=0,
             f29=[], f29_bad=0, f29_other=0, ovf=0, acc=0, ovf_first=None, acc_first=None, ctl=0, ctl_first=None, hidloss=0,
             quit_ln=None, fatal_after_quit=0, fatal_total=0, stand=0, dual=[], vke=0, vkw=0, vk_limit=0, lines=0, sig=[],
             variant_dir=[], gamepatch=0, diagb32=0, stall_lines=0, fork=None,
             f20=[], f20_bad=0, f20s=[], f20s_bad=0, f20_other=0, prep=[], allp=[], precache=[], precache_n=0, vkpc=[], vkpc_n=0)
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
        if line.startswith(b'TestLogStall:'):
            r['stall_lines'] += 1
            continue
        if b'TestHidLoss:' in line:
            r['hidloss'] += 1
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
        if b'FixF25:' in line:
            if M_F25FAIL in line:
                r['f25_fail'] += 1
                first_of(r, 'f25_fail_first', line)
            elif b'FixF25: mode=' in line:
                m = RX_F25.search(line)
                if m:
                    r['f25'].append((int(m.group(1)), ln))
                else:
                    r['f25_bad'] += 1
            else:
                r['f25_other'] += 1
        if M_DIRECT in line:
            r['direct'] += 1
            first_of(r, 'direct_first', line)
        if b'FixF24:' in line:
            if b'FixF24: mode=' in line:
                m = RX_F24.search(line)
                if m:
                    r['f24'].append((int(m.group(1)), int(m.group(2)), ln))
                else:
                    r['f24_bad'] += 1
            elif b'FixF24: init_owner' in line:
                m = RX_OWNER.search(line)
                if m:
                    d = dict(zip(OWNER_KEYS, (int(g) for g in m.groups())))
                    d['ln'] = ln
                    r['owner'].append(d)
                else:
                    r['owner_bad'] += 1
            elif b'FixF24: init tid=' in line:
                r['init'].append(ln)
            elif M_PUMPX in line:
                r['pumpx'] += 1
            elif b'FixF24: pump_update_long' in line:
                r['upd_long'] += 1
            elif b'FixF24: open failed' in line:
                r['open_failed'] += 1
            elif b'FixF24: add event' in line:
                r['add_event'] += 1
            elif b'FixF24: wait error' in line:
                r['wait_error'] += 1
            else:
                r['f24_other'] += 1
        if b'FixF20' in line:
            if b'FixF20Stat:' in line:
                m = RX_F20S.search(line)
                if m:
                    st = dict(zip(STAT_KEYS, [m.group(1).decode()] + [int(m.group(k)) for k in range(2, 8)]))
                    st['ln'] = ln
                    r['f20s'].append(st)
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
            m = RX_ALLP.search(line)
            if m:
                r['allp'].append(int(m.group(1)))
        if M_VKPC in line:
            r['vkpc_n'] += 1
            if len(r['vkpc']) < 8:
                r['vkpc'].append(line.decode('ascii', 'replace').strip()[:200])
        if b'FixF29:' in line:
            if M_OVF in line:
                r['ovf'] += 1
                first_of(r, 'ovf_first', line)
            elif b'FixF29: mode=' in line:
                m = RX_F29.search(line)
                if m:
                    r['f29'].append((int(m.group(1)), ln))
                else:
                    r['f29_bad'] += 1
            else:
                r['f29_other'] += 1
        if M_ACC in line:
            r['acc'] += 1
            first_of(r, 'acc_first', line)
        if b'Controller ' in line and RX_CTL.search(line):
            r['ctl'] += 1
            first_of(r, 'ctl_first', line)
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


def f21_member(x, want):
    g = x['first_guest_ln']
    ok = bool(x['f21']) and x['f21_bad'] == 0 and all(v == want for v, w, l in x['f21']) and g is not None and x['f21'][0][2] < g
    return ('FixF21: mode=%d (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s)' % (
        want, x['f21'][:3], x['f21_bad'], g), ok)


def f25_member(x, want):
    g = x['first_guest_ln']
    ok = bool(x['f25']) and x['f25_bad'] == 0 and all(v == want for v, l in x['f25']) and g is not None and x['f25'][0][1] < g
    return ('FixF25: mode=%d (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s)' % (
        want, x['f25'][:3], x['f25_bad'], g), ok)


def f24_member(x, want):
    g = x['first_guest_ln']
    ok = (bool(x['f24']) and x['f24_bad'] == 0 and all(v == want and b == 1 for v, b, l in x['f24']) and g is not None
          and x['f24'][0][2] < g)
    return ('FixF24: mode=%d b24=1 (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s)' % (
        want, x['f24'][:3], x['f24_bad'], g), ok)


def f29_member(x, want):
    g = x['first_guest_ln']
    ok = bool(x['f29']) and x['f29_bad'] == 0 and all(v == want for v, l in x['f29']) and g is not None and x['f29'][0][1] < g
    return ('FixF29: mode=%d (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s)' % (
        want, x['f29'][:3], x['f29_bad'], g), ok)


def f20_member(x, want):
    g = x['first_guest_ln']
    ok = bool(x['f20']) and x['f20_bad'] == 0 and all(v == want for v, l in x['f20']) and g is not None and x['f20'][0][1] < g
    return ('FixF20: mode=%d (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s) - item 730 (g)(3)' % (
        want, x['f20'][:3], x['f20_bad'], g), ok)


def exit_after_quit(x):
    """The last parsed FixF20Stat line with when=exit after the first Event: quit line; None if none."""
    q = x['quit_ln']
    ex = [st for st in x['f20s'] if st['when'] == 'exit' and q is not None and st['ln'] > q]
    return ex[-1] if ex else None


def stat_members(x, with_rewritten):
    e = exit_after_quit(x)
    q = x['quit_ln']
    n_after = len([st for st in x['f20s'] if st['when'] == 'exit' and q is not None and st['ln'] > q])
    out = [('FixF20Stat: when=exit line after Event: quit (quit %s; exit lines after it %d; all exit lines %d; unparsable FixF20Stat %d)' % (
               q, n_after, len([st for st in x['f20s'] if st['when'] == 'exit']), x['f20s_bad']), e is not None),
           ('FixF20Stat exit line: unmatched 0 (%s)' % (None if e is None else e['unmatched']), e is not None and e['unmatched'] == 0),
           ('FixF20Stat exit line: modules_bound = modules (%s / %s)' % (None if e is None else e['modules_bound'],
                                                                         None if e is None else e['modules']),
            e is not None and e['modules_bound'] == e['modules'])]
    if with_rewritten:
        out.append(('FixF20Stat exit line: rewritten >= %d (%s)' % (REWRITTEN_MIN, None if e is None else e['rewritten']),
                    e is not None and e['rewritten'] >= REWRITTEN_MIN))
    return out


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


def f24_other_count(x):
    """Every FixF24 line other than the mode lines (the letter of fs14_z: 'other FixF24: lines 0')."""
    return (x['f24_bad'] + len(x['init']) + len(x['owner']) + x['owner_bad'] + x['pumpx'] + x['upd_long'] + x['open_failed']
            + x['add_event'] + x['wait_error'] + x['f24_other'])


def owner_parts(x):
    g = x['first_guest_ln']
    o = x['owner'][0] if len(x['owner']) == 1 and x['owner_bad'] == 0 and g is not None and x['owner'][0]['ln'] < g else None
    alive = o is not None and o['hid'] != 0 and o['helper'] != 0
    same = o is not None and o['hid'] == o['helper'] == o['pump'] and o['pump'] != o['main']
    return o, alive, same


def summary_of(x):
    return x['summary'][-1] if x['summary'] else None


def stdout_scan(path):
    """death markers, '--- Fatal Error ---', 'FixF21: wait_expired', 'ExitFatal:', 'FixF25: read failed twice', 'KernelRead: direct read
    failed', 'FixF24: pump_stop_expired', 'FixF29: overflow', 'Accessed non-GPU cached memory' over the whole stdout file; None if
    absent."""
    if not path or not os.path.exists(path):
        return None
    death = []
    c = dict(fatal=0, expired=0, stand=0, f25_fail=0, direct=0, pumpx=0, ovf=0, acc=0)
    marks = (('fatal', M_FATAL), ('expired', M_EXPIRED), ('stand', M_STAND), ('f25_fail', M_F25FAIL), ('direct', M_DIRECT),
             ('pumpx', M_PUMPX), ('ovf', M_OVF), ('acc', M_ACC))
    with open(path, 'rb') as f:
        for line in f:
            for dm in DEATH:
                if dm in line and len(death) < 20:
                    death.append(dm.decode())
            for k, mk in marks:
                if mk in line:
                    c[k] += 1
    c['death'] = death
    return c


def scene(x):
    i, after = first_scene(x)
    hold = sum(dt for (n, dt, d, ln) in after)
    ge1 = sum(1 for (n, dt, d, ln) in after if dt >= K2_US)
    ge1_with_first = ge1 + (1 if i is not None and x['ft'][i][1] >= K2_US else 0)
    info = dict(first_scene_n=None if i is None else x['ft'][i][0], hold_s=round(hold / 1e6, 1), frames_ge1s=ge1,
                frames_ge1s_with_first=ge1_with_first, scene_frames=len(after),
                mean_dt_us=(round(hold / len(after), 1) if after else None), max_dt=max([dt for (n, dt, d, ln) in after] or [0]))
    return i, hold, ge1, ge1_with_first, info


def members(kind, x, att, idx_n, gl, sheet, so):
    summ = summary_of(x)
    death = x['death'] + ((so or {}).get('death') or [])
    s_fatal = None if so is None else so['fatal']
    s_exp = None if so is None else so['expired']
    s_pumpx = None if so is None else so['pumpx']
    lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None
    i, hold, ge1, ge1_with_first, info = scene(x)
    info.update(summary=summ, quit_ln=x['quit_ln'], fatal_after_quit=x['fatal_after_quit'], fatal_log_total=x['fatal_total'],
                fatal_stdout=s_fatal, expired_log=x['expired'], expired_stdout=s_exp, vke=x['vke'], vkw=x['vkw'])
    death_m = ('0 death markers (log and stdout) %s' % death[:3], not death and so is not None)
    exp_m = ('0 FixF21: wait_expired (whole log %d; whole stdout %s)' % (x['expired'], s_exp), x['expired'] == 0 and s_exp == 0)
    g = x['first_guest_ln']
    if kind == 'v':
        end_ok = att.get('close_killed') is False and att.get('close_rc') is not None
        o, alive, same = owner_parts(x)
        init_ok = bool(x['init']) and g is not None and x['init'][0] < g
        m = [('hold >= 300 s after the first scene frame (%.1f s)' % (hold / 1e6), hold >= HOLD_V_US),
             ('the process lived through the hold (outcome %s, hold_exit %s)' % (att.get('outcome'), att.get('hold_exit')), lived),
             death_m,
             ('0 frames >= 1 s after the first scene frame (%d; first %s; with the first frame %d)' % (ge1, info['first_scene_n'],
                                                                                                   ge1_with_first),
              i is not None and ge1 == 0),
             ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN),
             ('0 one-frame glitches (%s)' % gl, gl == 0),
             ('sheet for the lead made (%s)' % sheet, bool(sheet)),
             f20_member(x, 1),
             f24_member(x, 1),
             ('FixF24: init before the first GuestOut (lines %s; first GuestOut %s)' % (x['init'][:2], g), init_ok),
             ('FixF24: init_owner exactly 1 before the first GuestOut (%d, unparsable %d) %s: hid != 0 and helper != 0 (witness '
              'alive)' % (len(x['owner']), x['owner_bad'], o), alive),
             ('FixF24: init_owner hid = helper = pump != main', same),
             f25_member(x, 1),
             f21_member(x, 1),
             b12_member(x),
             f29_member(x, 1),
             ('exit by the harness: Event: quit line in the log (%s)' % x['quit_ln'], x['quit_ln'] is not None),
             ('after Event: quit: 0 --- Fatal Error --- (log %d; whole stdout %s)' % (x['fatal_after_quit'], s_fatal),
              x['quit_ln'] is not None and x['fatal_after_quit'] == 0 and s_fatal == 0),
             exp_m,
             ('0 FixF24: pump_stop_expired (whole log %d; whole stdout %s)' % (x['pumpx'], s_pumpx), x['pumpx'] == 0 and s_pumpx == 0),
             ('the process ended before the harness timeout (close_killed %s, close_rc %s, close_wait_s %s)' % (
                 att.get('close_killed'), att.get('close_rc'), att.get('close_wait_s')), end_ok)] + stat_members(x, True)
        f = [mode_member(x),
             ('summary LogAsync: full_waits= present (%d)' % len(x['summary']), summ is not None),
             ('drain_timeouts 0 (%s)' % (None if summ is None else summ['drain_timeouts']), summ is not None and summ['drain_timeouts'] == 0),
             b13_member(x),
             ('FixB12Stat: line present (parsed %d, unparsable %d)' % (len(x['stat']), x['stat_bad']), len(x['stat']) >= 1)]
    elif kind == 'z':
        n20s = len(x['f20s']) + x['f20s_bad']
        m = [('hold >= 120 s after the first scene frame (%.1f s)' % (hold / 1e6), i is not None and hold >= HOLD_Z_US),
             ('the process lived through the hold (outcome %s, hold_exit %s)' % (att.get('outcome'), att.get('hold_exit')), lived),
             death_m,
             f20_member(x, 0),
             ('0 FixF20Stat: lines (%d: parsed %d - exit %d, periodic %d; unparsable %d)' % (
                 n20s, len(x['f20s']), len([st for st in x['f20s'] if st['when'] == 'exit']),
                 len([st for st in x['f20s'] if st['when'] == 'periodic']), x['f20s_bad']), n20s == 0)]
        f = []
        info.update(video_index=idx_n, glitches=gl, sheet=sheet, b12=x['b12'][:3], b13=x['b13'][:3], f21=x['f21'][:3], f25=x['f25'][:3],
                    f24=x['f24'][:3], f29=x['f29'][:3], f21_unparsable=x['f21_bad'], expired_log=x['expired'], expired_stdout=s_exp,
                    pump_stop_expired_log=x['pumpx'], pump_stop_expired_stdout=s_pumpx,
                    logasync_mode=[t[:40] for t, l in x['mode'][:2]], stat_lines=len(x['stat']))
    else:
        lived_w = lived and (att.get('hold_s') or 0) >= HOLD_W_S
        dual = [d for d in x['dual'] if d[0] and g is not None and d[1] < g]
        m = [('lived to the end of the hold (outcome %s, hold_exit %s, hold_s %s >= 310)' % (att.get('outcome'), att.get('hold_exit'),
                                                                                         att.get('hold_s')), lived_w),
             death_m,
             ('0 [Vulkan][E] (%d)' % x['vke'], x['vke'] == 0),
             ('0 limit lines of the layer (%d)' % x['vk_limit'], x['vk_limit'] == 0),
             ('positive control: [Vulkan][W] %d > 0' % x['vkw'], x['vkw'] > 0),
             ('DualSrcBlend: supported=1 enabled=1 before the first GuestOut (%d)' % len(dual), bool(dual)),
             f20_member(x, 1),
             f24_member(x, 1)] + stat_members(x, False)
        f = [f29_member(x, 1),
             f25_member(x, 1),
             f21_member(x, 1),
             mode_member(x),
             ('no VALIDATION_STOP (a [Vulkan][E] line and the process did not live to the end of the hold)',
              not (x['vke'] > 0 and not lived_w)),
             b13_member(x),
             b12_member(x)]
    return m, f, info


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha', 'level', 'sheet')
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
             cache_before=os.path.join(d, 'manifest_before.tsv'), cache_after=os.path.join(d, 'manifest_run.tsv'))
    return p


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
    kenv = dict((k, v) for k, v in env.items() if k.startswith(('KYTY_', 'VK_')))
    ebad = env_diff(kenv, expected_env(kind))
    test_keys = sorted(k for k in env if k.startswith('KYTY_TEST_'))
    so = stdout_scan(p['stdout'])
    vv = 'true' if kind == 'w' else 'false'
    hold_opt = HOLD_OPT[kind]
    s_stand = None if so is None else so['stand']
    adm = [
        ('tag json present', run is not None),
        ('json binary_sha256 = FS15 bfac84be (%s)' % (jbin or '-')[:16], jbin == BIN_TAG),
        ('installed during the tag = FS15 bfac84be (%s)' % (inst_t or '-')[:16], inst_t == BIN_TAG),
        ('installed before = after = FS14 013e1974 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_INST and inst_a == BIN_INST),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env = the form of the tag (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad),
        ('no KYTY_TEST_* in the env (%s)' % (test_keys or 'none'), run is not None and not test_keys),
        ('0 ExitFatal: lines (log %s; whole stdout %s)' % ((x or {}).get('stand'), s_stand),
         x is not None and x['stand'] == 0 and s_stand == 0),
        ('last --vulkan-validation %s (%s)' % (vv, last_flag(cmd, '--vulkan-validation')), last_flag(cmd, '--vulkan-validation') == vv),
        ('last --shader-validation false (%s)' % last_flag(cmd, '--shader-validation'), last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args -lvl %s (%s; harness %s)' % (SKY, ga, hlev), ga == '-lvl ' + SKY and hlev == SKY),
        ('hold option %d s (%s)' % (hold_opt, (run or {}).get('hold_s')), (run or {}).get('hold_s') == hold_opt),
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
        ('no TestHidLoss line - the stand is off (%s)' % (x or {}).get('hidloss'), x is not None and x['hidloss'] == 0),
        ('caches returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'), bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),
    ]
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
    xx = x or {}
    o = None
    if x is not None:
        o = owner_parts(x)[0] or (x['owner'][0] if x['owner'] else None)
    res['f24_rows'] = dict(pump_update_long=xx.get('upd_long'), open_failed=xx.get('open_failed'), controller_lines=xx.get('ctl'),
                           controller_first=xx.get('ctl_first'), pump_stop_expired_log=xx.get('pumpx'),
                           pump_stop_expired_stdout=None if so is None else so['pumpx'],
                           mode_lines=None if x is None else [[v, b] for v, b, l in x['f24']], mode_unparsable=xx.get('f24_bad'),
                           init_lines=None if x is None else len(x['init']),
                           owner_lines=None if x is None else len(x['owner']), owner_unparsable=xx.get('owner_bad'), init_owner=o,
                           add_event=xx.get('add_event'), wait_error=xx.get('wait_error'), other=xx.get('f24_other'))
    res['f29_rows'] = dict(overflow_log=xx.get('ovf'), overflow_stdout=None if so is None else so['ovf'],
                           accessed_log=xx.get('acc'), accessed_stdout=None if so is None else so['acc'],
                           overflow_first=xx.get('ovf_first'), accessed_first=xx.get('acc_first'),
                           f29_mode_lines=None if x is None else [v for v, l in x['f29']], f29_unparsable=xx.get('f29_bad'),
                           f29_other=xx.get('f29_other'))
    res['f25_rows'] = dict(read_failed_twice_log=xx.get('f25_fail'), read_failed_twice_stdout=None if so is None else so['f25_fail'],
                           direct_read_failed_log=xx.get('direct'), direct_read_failed_stdout=None if so is None else so['direct'],
                           read_failed_twice_first=xx.get('f25_fail_first'), direct_read_failed_first=xx.get('direct_first'),
                           f25_mode_lines=None if x is None else len(x['f25']), f25_unparsable=xx.get('f25_bad'),
                           f25_other=xx.get('f25_other'))
    cb, ca = tsv_bytes(p['cache_before']), tsv_bytes(p['cache_after'])
    f20s = xx.get('f20s') or []
    ex = exit_after_quit(x) if x is not None else None
    res['f20_rows'] = dict(
        prep_ms=[a for a, b in xx.get('prep') or []], prep_lines=[b for a, b in xx.get('prep') or []],
        all_pipelines_created_ms=xx.get('allp'), precache_lines=xx.get('precache'), precache_n=xx.get('precache_n'),
        vk_pipeline_cache_lines=xx.get('vkpc'), vk_pipeline_cache_n=xx.get('vkpc_n'),
        blob_pipelinecache_before=None if cb is None else cb.get('_PipelineCache'),
        blob_pipelinecache_after=None if ca is None else ca.get('_PipelineCache'),
        glcache_before=None if cb is None else cb.get('GLCache'), glcache_after=None if ca is None else ca.get('GLCache'),
        shadercache_before=None if cb is None else cb.get('_ShaderCache'), shadercache_after=None if ca is None else ca.get('_ShaderCache'),
        f20stat_lines=len(f20s), f20stat_periodic=len([st for st in f20s if st['when'] == 'periodic']),
        f20stat_unparsable=xx.get('f20s_bad'), f20stat_max_unmatched=max(st['unmatched'] for st in f20s) if f20s else None,
        f20stat_exit=None if ex is None else dict((k, ex[k]) for k in STAT_KEYS),
        f20stat_last=None if not f20s else dict((k, f20s[-1][k]) for k in STAT_KEYS),
        f20_mode_lines=None if x is None else [v for v, l in x['f20']], f20_unparsable=xx.get('f20_bad'), f20_other=xx.get('f20_other'))
    last_stat = x['stat'][-1] if x is not None and x['stat'] else None
    res['ref'] = dict(glitches=gl, video_index=idx_n, outcome=att.get('outcome'), hold_exit=att.get('hold_exit'), hold_s=att.get('hold_s'),
                      stable_s=att.get('stable_s'), sheet=sheet, bin_version_string=binv, fork_line=xx.get('fork'),
                      lines=xx.get('lines'), vke=xx.get('vke'), vkw=xx.get('vkw'),
                      other_logasync=xx.get('other_async'), f21_lines=None if x is None else len(x['f21']),
                      f21_other=xx.get('f21_other'), stand_log=xx.get('stand'), stand_stdout=s_stand,
                      b12stat_last=last_stat, b12stat_lines=None if x is None else len(x['stat']),
                      env_keys=sorted(kenv))
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
        res['form_ok'] = all(b for _, b in f) if f else None
    fn = {'v': 'fs14_v', 'w': 'fs14_w', 'z': '-'}[kind]
    res['reading'] = ('ADMITTED, members 730(g)(3) %s, members of the form %s %s (no verdict; reading - FS15d)' % (
        'ALL YES' if res['ok'] else 'NOT ALL YES', fn,
        'ALL YES' if res['form_ok'] else ('none' if res['form_ok'] is None else 'NOT ALL YES'))) if admitted else (
        'NOT_ADMITTED: %s' % res['interference'])
    return res


def rows_out(res):
    out = ['tag %s (form %s, level %s)  reader sha256 %s' % (res['tag'], res['form'], res['level'], res['reader_sha256'])]
    out.append('  ADMISSION %s; STATUS %s' % ('PASS' if res['admitted'] else 'FAIL', res['status']))
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    out.append('  binary_sha256 %s' % res['binary_sha256'])
    if res['members'] is not None:
        out.append('  MEMBERS 730(g)(3) %s' % ('ALL YES' if res['ok'] else 'NOT ALL YES'))
        for a, b in res['members']:
            out.append('    [%s] %s' % ('YES' if b else 'NO', a))
        if res['form_members']:
            out.append('  MEMBERS form %s %s' % ({'v': 'fs14_v', 'w': 'fs14_w'}[res['kind']], 'ALL YES' if res['form_ok'] else 'NOT ALL YES'))
            for a, b in res['form_members']:
                out.append('    [%s] %s' % ('YES' if b else 'NO', a))
        out.append('  INFO %s' % json.dumps(res['info'], sort_keys=True, default=list)[:1400])
    r = res['f24_rows']
    out.append('  ROW F24 (not a gate): FixF24: pump_update_long %s, FixF24: open failed %s, host pad lines Controller %s (a reference, not an '
               'interference); pump_stop_expired log %s, whole stdout %s; FixF24: mode= lines %s, unparsable %s; init %s; init_owner %s '
               '(unparsable %s) %s; add event %s, wait error %s, other %s' % (
                   r['pump_update_long'], r['open_failed'], r['controller_lines'], r['pump_stop_expired_log'], r['pump_stop_expired_stdout'],
                   r['mode_lines'], r['mode_unparsable'], r['init_lines'], r['owner_lines'], r['owner_unparsable'],
                   json.dumps(r['init_owner'], sort_keys=True), r['add_event'], r['wait_error'], r['other']))
    if r['controller_first']:
        out.append('  ROW F24 first Controller line: %s' % r['controller_first'])
    r = res['f29_rows']
    out.append('  ROW F29 (not a gate; overflow > 0 - evidence of F29 in the game, item of the lead): FixF29: overflow log %s, whole stdout %s; '
               'Accessed non-GPU cached memory log %s, whole stdout %s; FixF29: mode= lines %s, unparsable %s, other FixF29 lines %s' % (
                   r['overflow_log'], r['overflow_stdout'], r['accessed_log'], r['accessed_stdout'],
                   r['f29_mode_lines'], r['f29_unparsable'], r['f29_other']))
    if r['overflow_first'] or r['accessed_first']:
        out.append('  ROW F29 first lines: %s | %s' % (r['overflow_first'], r['accessed_first']))
    r = res['f25_rows']
    out.append('  ROW F25 (not a gate): FixF25: read failed twice log %s, whole stdout %s; KernelRead: direct read failed log %s, whole '
               'stdout %s; FixF25: mode= lines %s, unparsable %s, other FixF25 lines %s' % (
                   r['read_failed_twice_log'], r['read_failed_twice_stdout'], r['direct_read_failed_log'], r['direct_read_failed_stdout'],
                   r['f25_mode_lines'], r['f25_unparsable'], r['f25_other']))
    if r['read_failed_twice_first'] or r['direct_read_failed_first']:
        out.append('  ROW F25 first lines: %s | %s' % (r['read_failed_twice_first'], r['direct_read_failed_first']))
    r = res['f20_rows']
    out.append('  ROW preparation screen (not a gate): ShaderPreparation ms %s; PipelinePrecache: all pipelines created ms %s' % (
        r['prep_ms'], r['all_pipelines_created_ms']))
    out.append('  ROW PipelinePrecache (not a gate): %s lines; %s' % (r['precache_n'], ' | '.join(r['precache_lines'] or [])))
    out.append('  ROW Vulkan pipeline cache (not a gate): %s lines; %s' % (r['vk_pipeline_cache_n'],
                                                                         ' | '.join(r['vk_pipeline_cache_lines'] or [])))
    out.append('  ROW driver blob (not a gate): _PipelineCache bytes before %s after %s; GLCache bytes before %s after %s; '
               '_ShaderCache bytes before %s after %s' % (r['blob_pipelinecache_before'], r['blob_pipelinecache_after'], r['glcache_before'],
                                                         r['glcache_after'], r['shadercache_before'], r['shadercache_after']))
    out.append('  ROW FixF20Stat (not a gate beyond the members): lines %s (periodic %s, unparsable %s), max unmatched %s; exit after quit %s; '
               'last %s; FixF20: mode= lines %s, unparsable %s, other FixF20 lines %s' % (
                   r['f20stat_lines'], r['f20stat_periodic'], r['f20stat_unparsable'], r['f20stat_max_unmatched'],
                   json.dumps(r['f20stat_exit'], sort_keys=True), json.dumps(r['f20stat_last'], sort_keys=True), r['f20_mode_lines'],
                   r['f20_unparsable'], r['f20_other']))
    e = res['exit']
    out.append('  ROW exit (not a gate): exit code %s (%s); WM_CLOSE post -> process end %s s; killed %s; posted %s; harness timeout %s s; '
               'Event: quit line %s; --- Fatal Error --- after it %s, whole stdout %s' % (
                   e['close_rc'], e['close_rc_hex'], e['close_s'], e['close_killed'], e['close_posted'], e['close_wait_s'], e['quit_ln'],
                   e['fatal_after_quit'], e['fatal_stdout']))
    out.append('  REFERENCE: %s' % json.dumps(res['ref'], sort_keys=True))
    out.append('  READING %s' % res['reading'])
    return out


def table(rd):
    out = ['| tag | status | binary_sha256 | members 730(g)(3) | form | FixF20Stat exit (bound/modules/rewritten/unmatched) | prep ms '
           '| all pipelines created ms | _PipelineCache before / after | exit code | close_s | glitches | video index | hold_s |',
           '|' + '---|' * 14]
    if os.path.isdir(rd):
        for t in sorted(os.listdir(rd)):
            js = os.path.join(rd, t, 'read.json')
            if TAG_RX.match(t) and os.path.exists(js):
                r = json.load(open(js, encoding='utf-8'))
                yn = (lambda v: '-' if v is None else ('ALL YES' if v else 'NOT ALL YES'))
                f = r['f20_rows']
                e = f['f20stat_exit']
                es = '-' if not e else '%s/%s/%s/%s' % (e['modules_bound'], e['modules'], e['rewritten'], e['unmatched'])
                out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s / %s | %s | %s | %s | %s | %s |' % (
                    t, r['status'], (r['binary_sha256'] or '-')[:8], yn(r['ok']), yn(r['form_ok']), es, f['prep_ms'],
                    f['all_pipelines_created_ms'], f['blob_pipelinecache_before'], f['blob_pipelinecache_after'], r['exit']['close_rc'],
                    r['exit']['close_s'], r['ref']['glitches'], r['ref']['video_index'], r['ref']['hold_s']))
    return out


def main(argv):
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader fs15c_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
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
        print('usage: fs15c_read.py fs15_v|fs15_w|fs15_z[_r1..3] | --dir D --tag T | --table')
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
