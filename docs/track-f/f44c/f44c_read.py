"""Track F link F44c (HPP-793; ROADMAP s122 item 698 (d)(4), item 701, item 707): the reader of the tag f29_v "no harm" of the F44a
binary d760708d (worktree 730ed40a + e148f54c, version KytyPS5-2026-09-15-6a2987a-1915-ge148f54c) at KYTY_FIX_F29=1, other FS12 defaults;
installed FS13 abab2196 before and after (item 703-704).  Rows only, NO VERDICT (the reading is F44d, HPP-794).
Port of C:/kyty/f287/f38c/f38c_read.py (F38c, HPP-765; the form fs12_v) with: the tag binary d760708d instead of 5a14a111, installed
before = after = FS13 abab2196 instead of FS12, KYTY_FIX_F29=1 in the env, the member 'FixF29: mode=1 before the first GuestOut', the
members of the form fs12_v as a group (the tag binary is FS12a based), and the rows 'FixF29: overflow' / 'Accessed non-GPU cached
memory' instead of the F25 rows.  ASCII only.

    python f44c_read.py <tag> [--json <out>]                       one tag (files of C:/kyty/f287/f44c)
    python f44c_read.py --dir <fixture dir> --tag <tag> [--json <out>]
        fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt, installed_before.txt, installed_after.txt,
        installed_sha.txt, manifest_cmp.txt, level.txt, seal.md, bin.exe
    python f44c_read.py --table [--runs <dir>]                     the table over every runs/<tag>/read.json

DEFINITIONS (seal docs/track-f/f44c.md section 4):
  entry line      the first line ending 'GuestOut: Level has started: underwater_aerial_garden'; first GuestOut - the first line carrying
                  'GuestOut'.
  first scene     the first 'FrameTrace: n=' line after the entry line with draws >= 100; the frames 'after the first scene frame' are the
  frame           FrameTrace lines after it (the first itself not counted; a row prints the count with it).
  FixF29          'FixF29: mode=<0|1>' (15c9d2f2 faultManager.cpp, once in the FaultManager constructor): >= 1 parsed line, no
                  unparsable line, every line mode=1, the first before the first GuestOut.
  overflow        a line containing 'FixF29: overflow' (KYTY_FIX_F29=1 only, raw > 1023, limit 32 per process) - a row (log and whole
                  stdout), not a member; > 0 - evidence of F29 in the game, an item of the lead.
  accessed        a line containing 'Accessed non-GPU cached memory' (the visitor of ProcessFaultBuffer, the former LOGF) - a row (log and
                  whole stdout), not a member.
  FixF21          'FixF21: mode=<0|1> wait_ms=<n>' (730ed40a subsystems.cpp:80): the FS12 default, mode=1 - group 'form fs12_v'.
  quit            the first log line containing 'Event: quit' (the harness exit, WM_CLOSE posted at the end of the hold).
  wait_expired    a line containing 'FixF21: wait_expired' (stderr) - counted in the whole log AND the whole stdout file.
  ExitFatal       a line containing 'ExitFatal:' (the stand KYTY_TEST_EXITFATAL writes to stderr) - whole log and whole stdout.
ADMISSION (a failed member - NOT_ADMITTED, not read; a repeat by the lead's item): json; binary_sha256 = F44a d760708d; installed during
  the tag = d760708d; installed before = after = FS13 abab2196; prereg = seal sha256; env = the form exactly (KYTY_* / VK_*; path values
  of KYTY_GATE_FILE, KYTY_SAMPLE_GATE, KYTY_REC any; KYTY_FIX_F29 = '1'; no other KYTY_FIX_*, no KYTY_GAME_PATCH); no KYTY_TEST_* key in
  the env and 0 'ExitFatal:' lines (log and stdout); last --vulkan-validation false; --shader-validation false; no --rd;
  -lvl underwater_aerial_garden and the harness level file; hold option 330; log; stdout; entry outcome ok; entry line; window lines
  minimized / Recovering Vulkan swapchain 0; signature 9177b426 and the catalog variant_fixb26_fixb1b_fixf10_fixf19; GamePatch: 0;
  DiagB32 lines 0; TestLogStall lines 0; caches returned (manifest cmp EQUAL); the summary line 'LogAsync: full_waits=' once with all
  fields (absent: killed - item 615 (b)(6)).
MEMBERS (letter of item 698 (d)(4)):
  f29_v   hold >= 300 s after the first scene frame; lived; 0 death markers (log and stdout); 0 frames >= 1 s after the first scene frame;
          video index >= 3 000; 0 one-frame glitches; sheet made; FixF29: mode=1 before the first GuestOut.
          + group 'form fs12_v' (FS12c, item 683 (g)(3)): FixF21: mode=1 before the first GuestOut; FixB12: mode=1 before the first
          GuestOut; Event: quit line in the log; after it 0 '--- Fatal Error ---' (log; stdout whole); 0 'FixF21: wait_expired' (log and
          stdout, whole); the process ended before the harness timeout; LogAsync: mode=1 once before the first GuestOut; summary present;
          drain_timeouts 0; FixB13: mode=1; FixB12Stat: line present.
ROWS (no gate): 'FixF29: overflow' and 'Accessed non-GPU cached memory' (log and whole stdout, with the first line of each kind);
  FixF29 lines of other kinds; exit code close_rc and close_s; last FixB12Stat: line.
"""
import hashlib
import json
import os
import re
import sys

G = 'C:/kyty/f287/f44c'
SEAL_PATH = G + '/pred/f44c_seal.md'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_d760708d.exe'
BIN_TAG = 'd760708d416d4fb5d494a9ca98c0417f2bf1911403f5334752783ed7a3b27c5f'
BIN_INST = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1915-ge148f54c'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
TAG_RX = re.compile(r'^(f29_v)(_r[1-3])?$')
K2_US = 1000000
HOLD_V_US = 300000000
HOLD_OPT = 330
VIDEO_MIN = 3000
RX_SUM = re.compile(rb'^LogAsync: full_waits=\d+ ')
RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_B13 = re.compile(rb'FixB13: mode=(\d+)')
RX_B12 = re.compile(rb'FixB12: mode=(\d+)\s*$')
RX_B12S = re.compile(rb'FixB12Stat: passes=(\d+) rewalk=(\d+) rwd=(\d+) lskip=(\d+)\s*$')
RX_F21 = re.compile(rb'FixF21: mode=(\d+) wait_ms=(\d+)\s*$')
RX_F29 = re.compile(rb'FixF29: mode=(\d+)\s*$')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
SEED = re.compile(rb':KytySC3:([0-9a-f]{40}):')
M_FORK = b'Fork build arigandores/KytyPS5 '
M_QUIT = b'Event: quit'
M_FATAL = b'--- Fatal Error ---'
M_EXPIRED = b'FixF21: wait_expired'
M_STAND = b'ExitFatal:'
M_OVF = b'FixF29: overflow'
M_ACC = b'Accessed non-GPU cached memory'
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


def expected_env():
    """Every KYTY_* / VK_* key of the tag json env -> the value (None: any value; the path keys)."""
    return dict(KYTY_GUEST_ARGS='-lvl ' + SKY, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None, KYTY_QUEUE_TRACE='1',
                KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8', KYTY_REC=None, KYTY_FIX_F29='1')


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
    r = dict(mode=[], summary=[], summary_bad=0, other_async=0, ft=[], entry_ln=None, first_guest_ln=None, death=[], minimized=0,
             recovering=0, win={}, b13=[], b12=[], b12_bad=0, stat=[], stat_bad=0, f21=[], f21_bad=0, f21_other=0, expired=0,
             f29=[], f29_bad=0, f29_other=0, ovf=0, acc=0, ovf_first=None, acc_first=None,
             quit_ln=None, fatal_after_quit=0, fatal_total=0, stand=0, vke=0, lines=0, sig=[], variant_dir=[], gamepatch=0, diagb32=0,
             stall_lines=0, fork=None)
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
        if b'FixF29:' in line:
            if M_OVF in line:
                r['ovf'] += 1
                if r['ovf_first'] is None:
                    r['ovf_first'] = line.decode('ascii', 'replace').strip()[:160]
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
            if r['acc_first'] is None:
                r['acc_first'] = line.decode('ascii', 'replace').strip()[:160]
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
        if b'[Vulkan][E]' in line:
            r['vke'] += 1
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


def f29_member(x):
    g = x['first_guest_ln']
    ok = bool(x['f29']) and x['f29_bad'] == 0 and all(v == 1 for v, l in x['f29']) and g is not None and x['f29'][0][1] < g
    return ('FixF29: mode=1 (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s) - item 698 (d)(4)' % (
        x['f29'][:3], x['f29_bad'], g), ok)


def summary_of(x):
    return x['summary'][-1] if x['summary'] else None


def stdout_scan(path):
    """death markers, '--- Fatal Error ---', 'FixF21: wait_expired', 'ExitFatal:', 'FixF29: overflow', 'Accessed non-GPU cached memory'
    over the whole stdout file; None if absent."""
    if not path or not os.path.exists(path):
        return None
    death, fatal, expired, stand, ovf, acc = [], 0, 0, 0, 0, 0
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
            if M_OVF in line:
                ovf += 1
            if M_ACC in line:
                acc += 1
    return dict(death=death, fatal=fatal, expired=expired, stand=stand, ovf=ovf, acc=acc)


def scene(x):
    i, after = first_scene(x)
    hold = sum(dt for (n, dt, d, ln) in after)
    ge1 = sum(1 for (n, dt, d, ln) in after if dt >= K2_US)
    ge1_with_first = ge1 + (1 if i is not None and x['ft'][i][1] >= K2_US else 0)
    info = dict(first_scene_n=None if i is None else x['ft'][i][0], hold_s=round(hold / 1e6, 1), frames_ge1s=ge1,
                frames_ge1s_with_first=ge1_with_first, scene_frames=len(after),
                mean_dt_us=(round(hold / len(after), 1) if after else None), max_dt=max([dt for (n, dt, d, ln) in after] or [0]))
    return i, hold, ge1, ge1_with_first, info


def members(x, att, idx_n, gl, sheet, so):
    summ = summary_of(x)
    death = x['death'] + ((so or {}).get('death') or [])
    s_fatal = None if so is None else so['fatal']
    s_exp = None if so is None else so['expired']
    lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None
    i, hold, ge1, ge1_with_first, info = scene(x)
    info.update(summary=summ, quit_ln=x['quit_ln'], fatal_after_quit=x['fatal_after_quit'], fatal_log_total=x['fatal_total'],
                fatal_stdout=s_fatal, expired_log=x['expired'], expired_stdout=s_exp, vke=x['vke'])
    end_ok = att.get('close_killed') is False and att.get('close_rc') is not None
    m = [('hold >= 300 s after the first scene frame (%.1f s)' % (hold / 1e6), hold >= HOLD_V_US),
         ('the process lived through the hold (outcome %s, hold_exit %s)' % (att.get('outcome'), att.get('hold_exit')), lived),
         ('0 death markers (log and stdout) %s' % death[:3], not death and so is not None),
         ('0 frames >= 1 s after the first scene frame (%d; first %s; with the first frame %d)' % (ge1, info['first_scene_n'],
                                                                                               ge1_with_first),
          i is not None and ge1 == 0),
         ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN),
         ('0 one-frame glitches (%s)' % gl, gl == 0),
         ('sheet for the lead made (%s)' % sheet, bool(sheet)),
         f29_member(x)]
    f = [f21_member(x),
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
    return m, f, info


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


def read_tag(tag, p):
    res = dict(tag=tag, form='f29_v', level=SKY, reader_sha256=sha_file(os.path.abspath(__file__)))
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
    ebad = env_diff(kenv, expected_env())
    test_keys = sorted(k for k in env if k.startswith('KYTY_TEST_'))
    so = stdout_scan(p['stdout'])
    s_stand = None if so is None else so['stand']
    adm = [
        ('tag json present', run is not None),
        ('json binary_sha256 = F44a d760708d (%s)' % (jbin or '-')[:16], jbin == BIN_TAG),
        ('installed during the tag = F44a d760708d (%s)' % (inst_t or '-')[:16], inst_t == BIN_TAG),
        ('installed before = after = FS13 abab2196 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_INST and inst_a == BIN_INST),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env = the form of the tag (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad),
        ('no KYTY_TEST_* in the env (%s)' % (test_keys or 'none'), run is not None and not test_keys),
        ('0 ExitFatal: lines (log %s; whole stdout %s)' % ((x or {}).get('stand'), s_stand),
         x is not None and x['stand'] == 0 and s_stand == 0),
        ('last --vulkan-validation false (%s)' % last_flag(cmd, '--vulkan-validation'), last_flag(cmd, '--vulkan-validation') == 'false'),
        ('last --shader-validation false (%s)' % last_flag(cmd, '--shader-validation'), last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args -lvl %s (%s; harness %s)' % (SKY, ga, hlev), ga == '-lvl ' + SKY and hlev == SKY),
        ('hold option %d s (%s)' % (HOLD_OPT, (run or {}).get('hold_s')), (run or {}).get('hold_s') == HOLD_OPT),
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
    res['f29_rows'] = dict(overflow_log=(x or {}).get('ovf'), overflow_stdout=None if so is None else so['ovf'],
                           accessed_log=(x or {}).get('acc'), accessed_stdout=None if so is None else so['acc'],
                           overflow_first=(x or {}).get('ovf_first'), accessed_first=(x or {}).get('acc_first'),
                           f29_mode_lines=None if x is None else len(x['f29']), f29_unparsable=(x or {}).get('f29_bad'),
                           f29_other=(x or {}).get('f29_other'))
    last_stat = (x or {}).get('stat')[-1] if x is not None and x['stat'] else None
    res['ref'] = dict(glitches=gl, video_index=idx_n, outcome=att.get('outcome'), hold_exit=att.get('hold_exit'), hold_s=att.get('hold_s'),
                      stable_s=att.get('stable_s'), sheet=sheet, bin_version_string=binv, fork_line=(x or {}).get('fork'),
                      lines=(x or {}).get('lines'), vke=(x or {}).get('vke'), other_logasync=(x or {}).get('other_async'),
                      f21_lines=None if x is None else len(x['f21']), f21_other=(x or {}).get('f21_other'),
                      stand_log=(x or {}).get('stand'), stand_stdout=s_stand,
                      b12stat_last=last_stat, b12stat_lines=None if x is None else len(x['stat']), env_keys=sorted(kenv))
    res['members'] = None
    res['form_members'] = None
    res['info'] = None
    res['ok'] = None
    res['form_ok'] = None
    if x is not None and admitted:
        m, f, info = members(x, att, idx_n, gl, sheet, so)
        res['members'] = [[a, bool(b)] for a, b in m]
        res['form_members'] = [[a, bool(b)] for a, b in f]
        res['info'] = info
        res['ok'] = all(b for _, b in m)
        res['form_ok'] = all(b for _, b in f)
    res['reading'] = ('ADMITTED, members 698(d)(4) %s, members of the form fs12_v %s (no verdict; reading - F44d)' % (
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
        out.append('  MEMBERS 698(d)(4) %s' % ('ALL YES' if res['ok'] else 'NOT ALL YES'))
        for a, b in res['members']:
            out.append('    [%s] %s' % ('YES' if b else 'NO', a))
        out.append('  MEMBERS form fs12_v %s' % ('ALL YES' if res['form_ok'] else 'NOT ALL YES'))
        for a, b in res['form_members']:
            out.append('    [%s] %s' % ('YES' if b else 'NO', a))
        out.append('  INFO %s' % json.dumps(res['info'], sort_keys=True, default=list)[:1400])
    r = res['f29_rows']
    out.append('  ROW F29 (not a gate; overflow > 0 - evidence of F29 in the game, item of the lead): FixF29: overflow log %s, whole stdout %s; '
               'Accessed non-GPU cached memory log %s, whole stdout %s; FixF29: mode= lines %s, unparsable %s, other FixF29 lines %s' % (
                   r['overflow_log'], r['overflow_stdout'], r['accessed_log'], r['accessed_stdout'],
                   r['f29_mode_lines'], r['f29_unparsable'], r['f29_other']))
    if r['overflow_first'] or r['accessed_first']:
        out.append('  ROW F29 first lines: %s | %s' % (r['overflow_first'], r['accessed_first']))
    e = res['exit']
    out.append('  ROW exit (not a gate): exit code %s (%s); WM_CLOSE post -> process end %s s; killed %s; posted %s; harness timeout %s s; '
               'Event: quit line %s; --- Fatal Error --- after it %s, whole stdout %s' % (
                   e['close_rc'], e['close_rc_hex'], e['close_s'], e['close_killed'], e['close_posted'], e['close_wait_s'], e['quit_ln'],
                   e['fatal_after_quit'], e['fatal_stdout']))
    out.append('  REFERENCE: %s' % json.dumps(res['ref'], sort_keys=True))
    out.append('  READING %s' % res['reading'])
    return out


def table(rd):
    out = ['| tag | status | binary_sha256 | members 698(d)(4) | form fs12_v | FixF29: overflow (log/stdout) | Accessed non-GPU cached memory (log/stdout) '
           '| exit code | close_s | glitches | video index | hold_s |',
           '|' + '---|' * 12]
    if os.path.isdir(rd):
        for t in sorted(os.listdir(rd)):
            js = os.path.join(rd, t, 'read.json')
            if TAG_RX.match(t) and os.path.exists(js):
                r = json.load(open(js, encoding='utf-8'))
                yn = (lambda v: '-' if v is None else ('ALL YES' if v else 'NOT ALL YES'))
                f = r['f29_rows']
                out.append('| %s | %s | %s | %s | %s | %s / %s | %s / %s | %s | %s | %s | %s | %s |' % (
                    t, r['status'], (r['binary_sha256'] or '-')[:8], yn(r['ok']), yn(r['form_ok']), f['overflow_log'],
                    f['overflow_stdout'], f['accessed_log'], f['accessed_stdout'], r['exit']['close_rc'],
                    r['exit']['close_s'], r['ref']['glitches'], r['ref']['video_index'], r['ref']['hold_s']))
    return out


def main(argv):
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader f44c_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
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
        print('usage: f44c_read.py f29_v[_r1..3] | --dir D --tag T | --table')
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
