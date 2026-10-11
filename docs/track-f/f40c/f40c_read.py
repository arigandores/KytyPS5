"""Track F link F40c (HPP-772; ROADMAP s122 item 692 (g)(1), (g)(3), (g)(4), item 696 (b)(1)-(3), item 700 (b)): the reader of the tags of
the stand KYTY_TEST_HIDLOSS edition 2 (F24), of the mutant tags and of f24_n1 "no harm".  Rows and a READING word by the seal; NO VERDICT
(the reading of F24 is F40d, HPP-773).  Port of C:/kyty/f287/f38c/f38c_read.py (the form fs12_v, F38c HPP-765) and of the stand parts of
C:/kyty/f287/f19e/f19e_read.py (F19e HPP-549: the stand window from the fire line to the stat line, 'wide' and 'strict').  ASCII only.

    python f40c_read.py <tag> [--json <out>]                           one tag (files of C:/kyty/f287/f40c)
    python f40c_read.py --dir <fixture dir> --tag <tag> [--partner <dir>] [--json <out>]
        fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt, installed_before.txt, installed_after.txt,
        installed_sha.txt, manifest_cmp.txt, level.txt, seal.md; --partner: a fixture dir of the partner tag (u0 for u1, p0 for p1)
    python f40c_read.py --table [--runs <dir>]                         the table over every runs/<tag>/read.json

DEFINITIONS (seal pred/f40c_seal.md section 4):
  entry line      the first line ending 'GuestOut: Level has started: underwater_aerial_garden'; first GuestOut - the first line with
                  'GuestOut'.
  first scene     the first 'FrameTrace: n=' line after the entry line with draws >= 100; the frames after it are the scene frames.
  frame           a 'FrameTrace: n=<n> dt_us=<dt>' line; a frame >= 1 s - dt_us >= 1 000 000.
  stand window    from the 'TestHidLoss: fire' line to the 'TestHidLoss: stat' line (item 692 (g)(1): the keyboard / window probes run from
                  fire - 1 s to done + 2 s; the stat and f24 lines close the window).  FrameTrace lines carry no time: 'strict' - the frames
                  whose line lies between the fire and the stat lines; 'wide' - strict plus the frames before the fire line taken
                  backwards while the sum of dt_us of the frames after them (up to the fire line) is <= 1 000 000 (F19e reading).  Members
                  read 'wide'; 'strict' is printed beside (executor's variant, seal section 8).
  f24 line        'TestHidLoss: f24 mode=<m> fix=<0|1>' and the 24 named fields of F40a section 2 / F40a2 section 2.
  init_owner      'FixF24: init_owner hid= helper= msg= pump= main=' (F40a2 section 1).
  pump expired    a line containing 'FixF24: pump_stop_expired'; jp_task ran - a line containing 'TestHidLoss: jp_task ran'.
  exit time       x1 / m2 (enter_scene --mark-quit): quit_mark.exit_upper_s - from the last poll of the log WITHOUT the line
                  'TestHidLoss: quit posted' to the first poll that saw the process ended (an upper bound of 'quit posted -> process end').
ADMISSION (a failed member - NOT_ADMITTED, an interference of the run, item 273 (z): not read, the attempt is not spent; a repeat by a new
  name): every tag - json; binary_sha256 = the tag binary; installed during the tag = it; installed before = after = FS13 abab2196 (item 703 (d)); prereg =
  seal sha256; env = the form exactly; 0 'ExitFatal:'; --vulkan-validation false; --shader-validation false; no --rd; -lvl
  underwater_aerial_garden; hold option; log; stdout; entry outcome ok; entry line; window minimized / Recovering 0; signature 9177b426 and
  the catalog variant_fixb26_fixb1b_fixf10_fixf19; GamePatch 0; DiagB32 0; TestLogStall 0; caches returned (manifest cmp EQUAL); 'FixF24:
  mode=<fix> b24=1' exactly 1 before the first GuestOut; pad lines of a pad other than 'KYTY test pad' / 'KYTY flap pad' 0; the summary
  'LogAsync: full_waits=' once (not for the exit tags).  Stand tags - config on (delay 60, the mode, edition 2, fix_f24, hold_upd_ms 8000,
  in_ms 100, probe_ms 20) exactly 1, config invalid 0, armed 1, attach 1 with hwnd=1, attach failed 0, the 'KYTY test pad' line 1, fire
  (the mode) 1, the fire line after the first scene frame (and 'pad probe start' after it for upd / pad); not exit: done 1, stat 1, f24 1
  (all fields, the mode, fix), the harness 'Event: quit' after the f24 line; pad: title off 1, pad probe start / end 1; exit: jp_task posted
  1, quit posted 1.  Flap tags (item 696 (b)(2)): f24_f1 / f24_m1 - flap_life_min_us > 0, flap_life_max_us < 50 000 and
  jp_scan_gap_max_us < flap_life_min_us; f24_f0 - flap_life_min_us > 0 and flap_life_max_us < 50 000 (word NOT_ADMITTED:flap).
  f24_n1 - 0 'TestHidLoss:' lines, no KYTY_TEST_* key.
MEMBERS (letter of item 692 (g)(1), (g)(4) with item 696 (b)(1)-(3)): see MEMBER_TEXT in the code and the seal section 4.
WORDS: NOT_ADMITTED[:flap] | DEAD_CONTROL (u0: in_lat_max_us < 7 200 000 or upd_on_main != 1 - stand defect, stop) | WITNESS_DEAD (u1 / n1:
  init_owner hid = 0 or helper = 0, or no init_owner line - stop) | PAD_ONLY_FAIL (u1 / p1: only pad probe members failed - the repeat
  pair) | MEMBERS_FAIL | MEMBERS_PASS | REFERENCE (p0, f0) | CAUGHT / NOT_CAUGHT (mutants) | NO_PARTNER (u1 / p1 without an admitted
  partner) | NOT_EVALUABLE.
"""
import hashlib
import json
import os
import re
import sys

G = 'C:/kyty/f287/f40c'
SEAL_PATH = G + '/pred/f40c_seal.md'
BIN_INST = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'   # the installed FS13 (item 703 (v), (d))
BINS = {'ddf0ca91': 'ddf0ca913f9feb8a66569fa30668de4b97e275ab6c4cc3e5c69889b4cb82e5d5',
        'c164a6d3': 'c164a6d34f0ab8b089d23752bf052da1db24f5ead9798ad0d8b8caa264d4ef0b',
        'fcf462d8': 'fcf462d823eee56a0069866de224aeef9df2b1c6d9bc83288fee364705de0bef',
        'ea84198d': 'ea84198deaebc903b38e07df98fc1f6af84172434c024874b6a5c787a0069446',
        'bec75cc2': 'bec75cc20b86609bd1440a1a7aea1afea95a23af763f19b0f3a6e4c7e2f2fe94',
        'bd6dcc81': 'bd6dcc81a32519eae50de4eb44ce88187d9ba9d4a8221c656b402c6065068c8f'}
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
SPEC = {'f24_u0': dict(bin='ddf0ca91', fix='0', mode='upd', hold=150, kind='u0'),
        'f24_u1': dict(bin='ddf0ca91', fix='1', mode='upd', hold=150, kind='u1', partner='f24_u0'),
        'f24_p0': dict(bin='ddf0ca91', fix='0', mode='pad', hold=150, kind='p0'),
        'f24_p1': dict(bin='ddf0ca91', fix='1', mode='pad', hold=150, kind='p1', partner='f24_p0'),
        'f24_f0': dict(bin='ddf0ca91', fix='0', mode='flap', hold=150, kind='f0'),
        'f24_f1': dict(bin='ddf0ca91', fix='1', mode='flap', hold=150, kind='f1'),
        'f24_x1': dict(bin='ddf0ca91', fix='1', mode='exit', hold=150, kind='x1'),
        'f24_d1': dict(bin='ddf0ca91', fix='1', mode='detach', hold=150, kind='d1'),
        'f24_m1': dict(bin='c164a6d3', fix='1', mode='flap', hold=150, kind='m1'),
        'f24_m2': dict(bin='fcf462d8', fix='1', mode='exit', hold=150, kind='m2'),
        'f24_m4': dict(bin='ea84198d', fix='1', mode='detach', hold=150, kind='m4'),
        'f24_m5': dict(bin='bec75cc2', fix='1', mode='upd', hold=150, kind='m5'),
        'f24_m6': dict(bin='bd6dcc81', fix='1', mode='upd', hold=150, kind='m6'),
        'f24_n1': dict(bin='ddf0ca91', fix='1', mode=None, hold=330, kind='n1'),
        'f24_u0b': dict(bin='ddf0ca91', fix='0', mode='upd', hold=150, kind='u0'),
        'f24_u1b': dict(bin='ddf0ca91', fix='1', mode='upd', hold=150, kind='u1', partner='f24_u0b'),
        'f24_p0b': dict(bin='ddf0ca91', fix='0', mode='pad', hold=150, kind='p0'),
        'f24_p1b': dict(bin='ddf0ca91', fix='1', mode='pad', hold=150, kind='p1', partner='f24_p0b')}
ORDER = ('f24_u0', 'f24_u1', 'f24_p0', 'f24_p1', 'f24_f0', 'f24_f1', 'f24_x1', 'f24_d1', 'f24_m1', 'f24_m2', 'f24_m4', 'f24_m5', 'f24_m6',
         'f24_n1', 'f24_u0b', 'f24_u1b', 'f24_p0b', 'f24_p1b')
TAG_RX = re.compile(r'^(f24_(?:u0b?|u1b?|p0b?|p1b?|f0|f1|x1|d1|m1|m2|m4|m5|m6|n1))(_r[1-2])?$')
BLOCK_US = 7200000          # 0.9 * HOLD_UPD_MS
FREE_US = 100000            # item 692 (g)(1) f24_u1: < 100 000
PRE_US = 50000              # f24_u0: in_pre_lat_max_us < 50 000
P99_TOL = 2000
MAX_TOL = 16667
FLAP_DELAY_US = 50000       # TEST_HIDLOSS_FLAP_TASK_DELAY_MS * 1 000
EXIT_MAX_S = 13.0           # HOLD_UPD_MS + 5 s
K2_US = 1000000
WIN_PRE_US = 1000000
HOLD_V_US = 300000000
VIDEO_MIN = 3000
F24_KEYS = ('upd_on_main', 'upd_slept_us', 'main_late_max_us', 'in_posted', 'in_seen', 'in_post_fail', 'in_lat_max_us',
            'in_pre_lat_max_us', 'hung_ms', 'jp_update_max_us', 'jp_tasks', 'pad_posted', 'pad_seen', 'pad_lat_p99_us', 'pad_lat_max_us',
            'attached', 'opened', 'open_failed', 'open_lat_max_us', 'flap_life_min_us', 'flap_life_max_us', 'jp_scan_gap_max_us')
OWNER_KEYS = ('hid', 'helper', 'msg', 'pump', 'main')
SUM_KEYS = ('full_waits', 'full_wait_us', 'stalls', 'stall_cut', 'lines', 'bytes', 'max_queued_bytes', 'sync_lines', 'drain_timeouts')
RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_CONFIG_ON = re.compile(rb'TestHidLoss: config on delay_s=(\S+) mode=(\w+) hold_ms=(\d+) edition=(\d+) hold_upd_ms=(\d+) in_ms=(\d+) '
                          rb'probe_ms=(\d+) fix_f24=(\d+)')
RX_ARMED = re.compile(rb'TestHidLoss: armed t_us=(\d+)')
RX_ATTACH = re.compile(rb'TestHidLoss: attach index=(-?\d+) t_us=(\d+) hwnd=(\d+)')
RX_FIRE = re.compile(rb'TestHidLoss: fire mode=(\w+) t_us=(\d+)')
RX_DONE = re.compile(rb'TestHidLoss: done t_us=(\d+)')
RX_STAT = re.compile(rb'TestHidLoss: stat mode=(\w+) ')
RX_F24 = re.compile(rb'TestHidLoss: f24 mode=(\w+) fix=(\d+)((?: \w+=\d+)+)\s*$')
RX_KV = re.compile(rb' (\w+)=(\d+)')
RX_MODE = re.compile(rb'FixF24: mode=(\d+) b24=(\d+)\s*$')
RX_OWNER = re.compile(rb'FixF24: init_owner hid=(\d+) helper=(\d+) msg=(\d+) pump=(\d+) main=(\d+)\s*$')
RX_PAD = re.compile(rb'Controller (-?\d+): "([^"]*)" type=')
RX_REMOVED = re.compile(rb'Controller (-?\d+): removed\b')
RX_B13 = re.compile(rb'FixB13: mode=(\d+)')
RX_B12 = re.compile(rb'FixB12: mode=(\d+)\s*$')
RX_B12S = re.compile(rb'FixB12Stat: passes=(\d+) rewalk=(\d+) rwd=(\d+) lskip=(\d+)\s*$')
RX_F21 = re.compile(rb'FixF21: mode=(\d+) wait_ms=(\d+)\s*$')
RX_SUM = re.compile(rb'^LogAsync: full_waits=\d+ ')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
SEED = re.compile(rb':KytySC3:([0-9a-f]{40}):')
TEST_PAD = 'KYTY test pad'
FLAP_PAD = 'KYTY flap pad'
M_QUIT = b'Event: quit'
M_FATAL = b'--- Fatal Error ---'
M_EXPIRED = b'FixF21: wait_expired'
M_STAND = b'ExitFatal:'
M_FORK = b'Fork build arigandores/KytyPS5 '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')


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
    m = TAG_RX.match(tag)
    return m.group(1) if m else None


def expected_env(sp):
    e = dict(KYTY_GUEST_ARGS='-lvl ' + SKY, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None, KYTY_QUEUE_TRACE='1',
             KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8', KYTY_FIX_F24=sp['fix'])
    if sp['mode'] is None:
        e['KYTY_REC'] = None
    else:
        e['KYTY_TEST_HIDLOSS'] = '60:' + sp['mode']
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
    r = dict(lines=0, frames=[], entry_ln=None, first_guest_ln=None, first_scene_i=None, scene_change_ln=None, thl=0, config_on=[],
             config_bad=0, armed=[], attach=[], attach_bad=0, detach_bad=0, flap_attach_bad=0, fire=[], done=[], stat=[], f24=[], f24_bad=0,
             title_off=[], pps=[], ppe=[], jp_posted=[], jp_ran=[], quit_posted=[], mode=[], mode_bad=0, init=[], owner=[], owner_bad=0,
             expired=[], upd_long=0, open_failed=0, add_event=0, wait_error=0, f24_other=0, pads=[], removed=[], death=[], quit_ln=None,
             fatal_total=0, fatal_after_quit=0, f21x=0, stand=0, vke=0, skipped=0, win={}, minimized=0, recovering=0, gamepatch=0,
             diagb32=0, stall_lines=0, sig=[], variant_dir=[], fork=None, async_mode=[], summary=[], summary_bad=0, other_async=0, b13=[],
             b12=[], b12_bad=0, stat12=[], stat12_bad=0, f21=[], f21_bad=0)
    if not path or not os.path.exists(path):
        r['sha256'] = None
        return r
    lvl = ('GuestOut: Level has started: %s' % SKY).encode()
    start = b'GuestOut: Level has started: '
    h = hashlib.sha256()
    after_entry = False
    with open(path, 'rb') as fh:
        for raw in fh:
            h.update(raw)
            r['lines'] += 1
            ln = r['lines']
            line = raw.rstrip(b'\r\n')
            if line.startswith(b'FrameTrace: n='):
                m = RX_FT.match(line)
                if m:
                    d = RX_DRAWS.search(line)
                    if after_entry and r['first_scene_i'] is None and d and int(d.group(1)) >= 100:
                        r['first_scene_i'] = len(r['frames'])
                    r['frames'].append((ln, int(m.group(1)), int(m.group(2))))
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
                r['thl'] += 1
                if b'TestHidLoss: config invalid' in line:
                    r['config_bad'] += 1
                m = RX_CONFIG_ON.search(line)
                if m:
                    r['config_on'].append(tuple(g.decode('ascii', 'replace') for g in m.groups()) + (ln,))
                m = RX_ARMED.search(line)
                if m:
                    r['armed'].append((ln, int(m.group(1))))
                m = RX_ATTACH.search(line)
                if m:
                    r['attach'].append((ln, int(m.group(2)), int(m.group(3))))
                if b'TestHidLoss: attach failed' in line:
                    r['attach_bad'] += 1
                if b'TestHidLoss: detach failed' in line:
                    r['detach_bad'] += 1
                if b'TestHidLoss: flap attach failed' in line:
                    r['flap_attach_bad'] += 1
                m = RX_FIRE.search(line)
                if m:
                    r['fire'].append((ln, int(m.group(2)), m.group(1).decode('ascii', 'replace')))
                m = RX_DONE.search(line)
                if m:
                    r['done'].append((ln, int(m.group(1))))
                m = RX_STAT.search(line)
                if m:
                    r['stat'].append((ln, m.group(1).decode('ascii', 'replace')))
                if b'TestHidLoss: f24 ' in line:
                    m = RX_F24.search(line)
                    kv = dict((k.decode(), int(v)) for k, v in RX_KV.findall(m.group(3))) if m else {}
                    if m and all(k in kv for k in F24_KEYS):
                        kv.update(mode=m.group(1).decode('ascii', 'replace'), fix=int(m.group(2)), ln=ln)
                        r['f24'].append(kv)
                    else:
                        r['f24_bad'] += 1
                if b'TestHidLoss: title off' in line:
                    r['title_off'].append(ln)
                if b'TestHidLoss: pad probe start' in line:
                    r['pps'].append(ln)
                if b'TestHidLoss: pad probe end' in line:
                    r['ppe'].append(ln)
                if b'TestHidLoss: jp_task posted' in line:
                    r['jp_posted'].append(ln)
                if b'TestHidLoss: jp_task ran' in line:
                    r['jp_ran'].append(ln)
                if b'TestHidLoss: quit posted' in line:
                    r['quit_posted'].append(ln)
            if b'FixF24:' in line:
                if b'FixF24: mode=' in line:
                    m = RX_MODE.search(line)
                    if m:
                        r['mode'].append((int(m.group(1)), int(m.group(2)), ln))
                    else:
                        r['mode_bad'] += 1
                elif b'FixF24: init_owner' in line:
                    m = RX_OWNER.search(line)
                    if m:
                        d = dict(zip(OWNER_KEYS, (int(g) for g in m.groups())))
                        d['ln'] = ln
                        r['owner'].append(d)
                    else:
                        r['owner_bad'] += 1
                elif b'FixF24: init tid=' in line:
                    r['init'].append((ln, line.decode('ascii', 'replace')[line.find(b'FixF24:'):][:120]))
                elif b'FixF24: pump_stop_expired' in line:
                    r['expired'].append(ln)
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
            if b'Controller ' in line:
                m = RX_PAD.search(line)
                if m:
                    r['pads'].append((ln, int(m.group(1)), m.group(2).decode('ascii', 'replace')))
                m = RX_REMOVED.search(line)
                if m:
                    r['removed'].append((ln, int(m.group(1))))
            if line.startswith(b'LogAsync:'):
                if line.startswith(b'LogAsync: mode='):
                    r['async_mode'].append((line.decode('ascii', 'replace').strip()[:160], ln))
                elif RX_SUM.match(line):
                    f = dict(tok.split('=', 1) for tok in line.decode('ascii', 'replace').strip().split(' ')[1:] if '=' in tok)
                    if all(k in f for k in SUM_KEYS):
                        r['summary'].append(dict((k, num(f[k])) for k in SUM_KEYS))
                    else:
                        r['summary_bad'] += 1
                else:
                    r['other_async'] += 1
                continue
            if b'FixB12Stat:' in line:
                m = RX_B12S.search(line)
                if m:
                    r['stat12'].append(ln)
                else:
                    r['stat12_bad'] += 1
                continue
            if b'FixF21:' in line:
                if M_EXPIRED in line:
                    r['f21x'] += 1
                elif b'FixF21: mode=' in line:
                    m = RX_F21.search(line)
                    if m:
                        r['f21'].append((int(m.group(1)), ln))
                    else:
                        r['f21_bad'] += 1
            m = RX_B13.search(line)
            if m:
                r['b13'].append((int(m.group(1)), ln))
            if b'FixB12: mode=' in line:
                m = RX_B12.search(line)
                if m:
                    r['b12'].append((int(m.group(1)), ln))
                else:
                    r['b12_bad'] += 1
            if M_STAND in line:
                r['stand'] += 1
            if r['quit_ln'] is None and M_QUIT in line:
                r['quit_ln'] = ln
            if M_FATAL in line:
                r['fatal_total'] += 1
                if r['quit_ln'] is not None:
                    r['fatal_after_quit'] += 1
            if start in line:
                if r['entry_ln'] is None:
                    if line.endswith(lvl):
                        r['entry_ln'] = ln
                        after_entry = True
                elif r['scene_change_ln'] is None:
                    r['scene_change_ln'] = ln
            if r['first_guest_ln'] is None and b'GuestOut' in line:
                r['first_guest_ln'] = ln
            if b'[Vulkan][E]' in line:
                r['vke'] += 1
            if b'AsyncPipelines: skipped draw' in line:
                r['skipped'] += 1
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
                    r['death'].append((dm.decode(), ln))
            if b'Recovering Vulkan swapchain' in line:
                r['recovering'] += 1
            mw = RX_WIN.search(line)
            if mw:
                k = mw.group(1).decode()
                r['win'][k] = r['win'].get(k, 0) + 1
                if k == 'minimized':
                    r['minimized'] += 1
    r['sha256'] = h.hexdigest()
    return r


def stdout_scan(path):
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


def windows(frames, fire_ln, stat_ln):
    """(wide set, strict set) of frame indexes (F19e)."""
    if fire_ln is None or stat_ln is None:
        return None, None
    strict = set(i for i, fr in enumerate(frames) if fire_ln < fr[0] < stat_ln)
    wide = set(strict)
    acc = 0
    for i in range(len(frames) - 1, -1, -1):
        if frames[i][0] >= fire_ln:
            continue
        if acc > WIN_PRE_US:
            break
        wide.add(i)
        acc += frames[i][2]
    return wide, strict


def one(lst):
    return lst[0] if len(lst) == 1 else None


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha', 'level', 'sheet')
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


def partner_read(partner_base, runs_dir):
    """The admitted read.json of the partner family (<p>, <p>_r1, <p>_r2) - at most one is admitted; None if none."""
    if runs_dir is None:
        return None
    found = None
    for name in (partner_base, partner_base + '_r1', partner_base + '_r2'):
        js = os.path.join(runs_dir, name, 'read.json')
        if os.path.exists(js):
            r = json.load(open(js, encoding='utf-8'))
            if r.get('admitted'):
                found = r
    return found


def owner_parts(x):
    o = one(x['owner'])
    alive = o is not None and o['hid'] != 0 and o['helper'] != 0
    same = o is not None and o['hid'] == o['helper'] == o['pump'] and o['pump'] != o['main']
    return o, alive, same


def read_tag(tag, p, partner=None):
    base = base_of(tag)
    sp = SPEC[base]
    kind = sp['kind']
    stand = sp['mode'] is not None
    res = dict(tag=tag, base=base, kind=kind, mode=sp['mode'], fix=sp['fix'], binary=sp['bin'], level=SKY,
               reader_sha256=sha_file(os.path.abspath(__file__)))
    run = json.load(open(p['run'], encoding='utf-8')) if os.path.exists(p['run']) else None
    jbin = (run or {}).get('binary_sha256')
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
    x = scan(p['log'])
    have_log = x['sha256'] is not None
    so = stdout_scan(p['stdout'])
    kenv = dict((k, v) for k, v in env.items() if k.startswith(('KYTY_', 'VK_')))
    ebad = env_diff(kenv, expected_env(sp))
    want_bin = BINS[sp['bin']]
    g = x['first_guest_ln']
    fs_i = x['first_scene_i']
    fs_ln = None if fs_i is None else x['frames'][fs_i][0]
    mode_ok = (len(x['mode']) == 1 and x['mode_bad'] == 0 and str(x['mode'][0][0]) == sp['fix'] and x['mode'][0][1] == 1
               and g is not None and x['mode'][0][2] < g)
    other_pads = [q for q in x['pads'] if q[2] not in (TEST_PAD, FLAP_PAD)]
    exit_kind = sp['mode'] == 'exit'
    adm = [
        ('tag json present', run is not None),
        ('json binary_sha256 = %s (%s)' % (sp['bin'], (jbin or '-')[:16]), jbin == want_bin),
        ('installed during the tag = %s (%s)' % (sp['bin'], (inst_t or '-')[:16]), inst_t == want_bin),
        ('installed before = after = FS13 abab2196 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_INST and inst_a == BIN_INST),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env = the form of the tag (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad),
        ('0 ExitFatal: lines (log %s; whole stdout %s)' % (x['stand'], None if so is None else so['stand']),
         have_log and x['stand'] == 0 and so is not None and so['stand'] == 0),
        ('last --vulkan-validation false (%s)' % last_flag(cmd, '--vulkan-validation'), last_flag(cmd, '--vulkan-validation') == 'false'),
        ('last --shader-validation false (%s)' % last_flag(cmd, '--shader-validation'), last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args -lvl %s (%s; harness %s)' % (SKY, ga, hlev), ga == '-lvl ' + SKY and hlev == SKY),
        ('hold option %d s (%s)' % (sp['hold'], (run or {}).get('hold_s')), (run or {}).get('hold_s') == sp['hold']),
        ('log present', have_log),
        ('stdout present', so is not None),
        ('entry outcome ok (%s)' % att.get('outcome'), att.get('outcome') == 'ok'),
        ('entry line present (%s)' % x['entry_ln'], x['entry_ln'] is not None),
        ('window events: minimized %d, Recovering Vulkan swapchain %d (all %s)' % (x['minimized'], x['recovering'], x['win']),
         have_log and x['minimized'] == 0 and x['recovering'] == 0),
        ('translation signature 9177b426 and cache dir %s (%s / %s)' % (VARIANT_DIR, [z[:8] for z in x['sig']], x['variant_dir']),
         x['sig'] == [SIG] and x['variant_dir'] == [VARIANT_DIR]),
        ('no GamePatch: line (%d)' % x['gamepatch'], have_log and x['gamepatch'] == 0),
        ('no DiagB32 line (%d)' % x['diagb32'], have_log and x['diagb32'] == 0),
        ('no TestLogStall line (%d)' % x['stall_lines'], have_log and x['stall_lines'] == 0),
        ('caches returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'), bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),
        ('FixF24: mode=%s b24=1 exactly 1, before the first GuestOut (%s; unparsable %d; first GuestOut %s)' % (
            sp['fix'], x['mode'][:2], x['mode_bad'], g), mode_ok),
        ('pad lines of another pad 0 (%s)' % [q[2] for q in other_pads][:3], have_log and not other_pads),
    ]
    if not exit_kind:
        adm.append(('summary LogAsync: full_waits= once, all fields (%d, bad %d) - absent: killed (item 615 (b)(6))' % (
            len(x['summary']), x['summary_bad']), len(x['summary']) == 1 and x['summary_bad'] == 0))
    armed, attach, fire, done = one(x['armed']), one(x['attach']), one(x['fire']), one(x['done'])
    st = one(x['stat'])
    f = one(x['f24'])
    test_pads = [q for q in x['pads'] if q[2] == TEST_PAD]
    if stand:
        cfg = one(x['config_on'])
        cfg_ok = (cfg is not None and cfg[0] == '60' and cfg[1] == sp['mode'] and cfg[3] == '2' and cfg[4] == '8000' and cfg[5] == '100'
                  and cfg[6] == '20' and cfg[7] == sp['fix'] and x['config_bad'] == 0)
        adm += [('config on delay_s=60 mode=%s edition=2 hold_upd_ms=8000 in_ms=100 probe_ms=20 fix_f24=%s exactly 1, invalid 0 (%s)' % (
                    sp['mode'], sp['fix'], [c[:8] for c in x['config_on'][:2]]), cfg_ok),
                ('armed exactly 1 (%d)' % len(x['armed']), armed is not None),
                ('attach exactly 1 with hwnd=1, attach failed 0 (%s; failed %d)' % (x['attach'][:2], x['attach_bad']),
                 attach is not None and attach[2] == 1 and x['attach_bad'] == 0),
                ('emulator pad line "KYTY test pad" exactly 1 (%d)' % len(test_pads), len(test_pads) == 1),
                ('fire mode=%s exactly 1 (%s)' % (sp['mode'], x['fire'][:2]), fire is not None and fire[2] == sp['mode']),
                ('stimulus after the first scene frame: fire line %s > first scene frame line %s' % (None if fire is None else fire[0], fs_ln),
                 fire is not None and fs_ln is not None and fire[0] > fs_ln)]
        if sp['mode'] in ('upd', 'pad'):
            pps = one(x['pps'])
            adm.append(('pad probe start exactly 1 after the first scene frame (%s; first scene %s)' % (x['pps'][:2], fs_ln),
                        pps is not None and fs_ln is not None and pps > fs_ln))
        if sp['mode'] == 'pad':
            adm += [('title off exactly 1 (%d)' % len(x['title_off']), len(x['title_off']) == 1),
                    ('pad probe end exactly 1 (%d)' % len(x['ppe']), len(x['ppe']) == 1)]
        if exit_kind:
            adm += [('jp_task posted exactly 1 (%d)' % len(x['jp_posted']), len(x['jp_posted']) == 1),
                    ('quit posted exactly 1 (%d)' % len(x['quit_posted']), len(x['quit_posted']) == 1)]
        else:
            fok = f is not None and f['mode'] == sp['mode'] and str(f['fix']) == sp['fix'] and x['f24_bad'] == 0
            adm += [('done exactly 1 (%d)' % len(x['done']), done is not None),
                    ('stat mode=%s exactly 1 (%s)' % (sp['mode'], x['stat'][:2]), st is not None and st[1] == sp['mode']),
                    ('f24 line exactly 1, all fields, mode=%s fix=%s (%d, malformed %d)' % (sp['mode'], sp['fix'], len(x['f24']), x['f24_bad']),
                     fok),
                    ('the tag does not end inside the stand window: Event: quit line %s after the f24 line %s' % (
                        x['quit_ln'], None if f is None else f['ln']), f is not None and x['quit_ln'] is not None and x['quit_ln'] > f['ln'])]
    else:
        test_keys = sorted(k for k in env if k.startswith('KYTY_TEST_'))
        adm += [('lines TestHidLoss: = 0 (%d)' % x['thl'], have_log and x['thl'] == 0),
                ('no KYTY_TEST_* key in the env (%s)' % (test_keys or 'none'), run is not None and not test_keys)]
    flap_adm = None
    if sp['mode'] == 'flap' and f is not None:
        lmin, lmax, gap = f['flap_life_min_us'], f['flap_life_max_us'], f['jp_scan_gap_max_us']
        if kind == 'f0':
            ok = lmin > 0 and lmax < FLAP_DELAY_US
            txt = 'flap admission (item 696 (b)(2), f24_f0): flap_life_min_us %d > 0 and flap_life_max_us %d < 50000' % (lmin, lmax)
        else:
            ok = lmin > 0 and lmax < FLAP_DELAY_US and gap < lmin
            txt = ('flap admission (item 696 (b)(2)): flap_life_min_us %d > 0, flap_life_max_us %d < 50000 and jp_scan_gap_max_us %d < '
                   'flap_life_min_us %d' % (lmin, lmax, gap, lmin))
        flap_adm = (txt, ok)
        adm.append(flap_adm)
    res['admission'] = [[a, bool(b)] for a, b in adm]
    admitted = all(b for _, b in adm)
    only_flap = (not admitted and flap_adm is not None and not flap_adm[1]
                 and all(b for a, b in adm if a != flap_adm[0]))
    res['admitted'] = admitted
    res['status'] = 'ADMITTED' if admitted else ('NOT_ADMITTED:flap' if only_flap else 'NOT_ADMITTED')
    # stand window and frames
    frames = x['frames']
    wide, strict = windows(frames, None if fire is None else fire[0], None if st is None else st[0])
    k2w = None if wide is None else sorted(i for i in wide if frames[i][2] >= K2_US)
    k2s = None if strict is None else sorted(i for i in strict if frames[i][2] >= K2_US)
    win = dict(wide_frames=None if wide is None else len(wide), strict_frames=None if strict is None else len(strict),
               ge1s_wide=None if k2w is None else len(k2w), ge1s_strict=None if k2s is None else len(k2s),
               ge1s_wide_n=None if k2w is None else [frames[i][1] for i in k2w][:10],
               max_dt_wide=None if not wide else max(frames[i][2] for i in wide))
    res['window'] = win
    res['f24'] = f
    o, alive, same = owner_parts(x)
    res['init_owner'] = o
    res['lines'] = dict(init=x['init'][:2], init_n=len(x['init']), owner_n=len(x['owner']), owner_bad=x['owner_bad'], expired=x['expired'][:3],
                        upd_long=x['upd_long'], open_failed=x['open_failed'], add_event=x['add_event'], wait_error=x['wait_error'],
                        f24_other=x['f24_other'], jp_posted=x['jp_posted'][:2], jp_ran=x['jp_ran'][:4], quit_posted=x['quit_posted'][:2],
                        removed=x['removed'][:4], pads_n=len(x['pads']), test_pads=[q[:2] for q in test_pads][:2], skipped_draw=x['skipped'],
                        vke=x['vke'], death_log=x['death'][:5], death_stdout=None if so is None else so['death'][:5],
                        quit_ln=x['quit_ln'], fatal_total=x['fatal_total'], summary=x['summary'][-1] if x['summary'] else None)
    res['exit'] = dict(hold_exit=att.get('hold_exit'), hold_s=att.get('hold_s'), close_rc=att.get('close_rc'), close_s=att.get('close_s'),
                       close_killed=att.get('close_killed'), quit_mark=att.get('quit_mark'))
    res['members'] = None
    res['catch'] = None
    res['word'] = res['status'] if not admitted else None
    res['partner'] = None
    if admitted:
        word, mem, catch = judge(kind, sp, x, f, o, alive, same, win, att, so, partner, res, p)
        res['members'] = None if mem is None else [[a, b] for a, b in mem]
        res['catch'] = catch
        res['word'] = word
    return res


def judge(kind, sp, x, f, o, alive, same, win, att, so, partner, res, p):
    """(word, members [(text, True/False/None)], catch text or None)."""
    g = (lambda k: None if f is None else f[k])
    mem = []
    owner_txt = 'init_owner exactly 1 (%d, bad %d) %s' % (len(x['owner']), x['owner_bad'], o)
    if kind == 'u0':
        dead = f is None or f['in_lat_max_us'] < BLOCK_US or f['upd_on_main'] != 1
        mem = [('upd_on_main = 1 (%s)' % g('upd_on_main'), None if f is None else f['upd_on_main'] == 1),
               ('main_late_max_us >= 7200000 (%s)' % g('main_late_max_us'), None if f is None else f['main_late_max_us'] >= BLOCK_US),
               ('in_lat_max_us >= 7200000 (%s)' % g('in_lat_max_us'), None if f is None else f['in_lat_max_us'] >= BLOCK_US),
               ('in_pre_lat_max_us < 50000 (%s)' % g('in_pre_lat_max_us'), None if f is None else f['in_pre_lat_max_us'] < PRE_US),
               ('window member alive: hung_ms > 0 (%s; 0 - the window member of f24_u1 drops, item 692 (v)(8)(b); not a failure)' % g('hung_ms'),
                None if f is None else True)]
        res['window_member_alive'] = None if f is None else f['hung_ms'] > 0
        res['row_rc6a'] = 'frames >= 1 s in the stand window (wide %s, strict %s) - a reading line of item 692 (v)(8)(a), not a member' % (
            win['ge1s_wide'], win['ge1s_strict'])
        res['row_fixf24_other'] = 'FixF24 lines other than mode=0 at =0: init %d, init_owner %d, other %d (item 692 (g)(2): none)' % (
            len(x['init']), len(x['owner']), x['f24_other'] + x['upd_long'] + x['open_failed'] + x['add_event'] + x['wait_error'] + len(x['expired']))
        if dead:
            return 'DEAD_CONTROL', mem, None
        return word_of(mem), mem, None
    if kind == 'u1':
        if partner is None:
            return 'NO_PARTNER', None, None
        pf = partner.get('f24') or {}
        walive = partner.get('window_member_alive')
        res['partner'] = dict(tag=partner.get('tag'), pad_lat_p99_us=pf.get('pad_lat_p99_us'), pad_lat_max_us=pf.get('pad_lat_max_us'),
                              window_member_alive=walive, word=partner.get('word'))
        mem = [('upd_on_main = 0 (%s)' % g('upd_on_main'), None if f is None else f['upd_on_main'] == 0),
               ('jp_update_max_us >= 7200000 (%s)' % g('jp_update_max_us'), None if f is None else f['jp_update_max_us'] >= BLOCK_US),
               ('main_late_max_us < 100000 (%s)' % g('main_late_max_us'), None if f is None else f['main_late_max_us'] < FREE_US),
               ('in_lat_max_us < 100000 (%s)' % g('in_lat_max_us'), None if f is None else f['in_lat_max_us'] < FREE_US)]
        if walive:
            mem.append(('hung_ms = 0 (%s; the window member is alive in %s)' % (g('hung_ms'), partner.get('tag')),
                        None if f is None else f['hung_ms'] == 0))
        else:
            mem.append(('hung_ms member dropped: hung_ms of %s = 0 (item 692 (v)(8)(b)); hung_ms here %s - a row' % (partner.get('tag'),
                                                                                                                 g('hung_ms')), True))
        mem += [('in_posted = in_seen (%s / %s)' % (g('in_posted'), g('in_seen')), None if f is None else f['in_posted'] == f['in_seen']),
                ('frames >= 1 s in the stand window 0 (wide %s, strict %s)' % (win['ge1s_wide'], win['ge1s_strict']),
                 None if win['ge1s_wide'] is None else win['ge1s_wide'] == 0),
                ('PAD pad_posted = pad_seen (%s / %s)' % (g('pad_posted'), g('pad_seen')), None if f is None else f['pad_posted'] == f['pad_seen']),
                ('PAD pad_lat_p99_us %s <= %s of %s + 2000' % (g('pad_lat_p99_us'), pf.get('pad_lat_p99_us'), partner.get('tag')),
                 None if f is None or pf.get('pad_lat_p99_us') is None else f['pad_lat_p99_us'] <= pf['pad_lat_p99_us'] + P99_TOL),
                ('PAD pad_lat_max_us %s <= %s of %s + 16667' % (g('pad_lat_max_us'), pf.get('pad_lat_max_us'), partner.get('tag')),
                 None if f is None or pf.get('pad_lat_max_us') is None else f['pad_lat_max_us'] <= pf['pad_lat_max_us'] + MAX_TOL),
                (owner_txt + ': hid != 0 and helper != 0 (witness alive)', alive),
                ('init_owner hid = helper = pump != main', same)]
        if not alive:
            return 'WITNESS_DEAD', mem, None
        return pad_word(mem), mem, None
    if kind == 'p0':
        mem = [('reference: pad_posted %s, pad_seen %s, pad_lat_p99_us %s, pad_lat_max_us %s' % (
            g('pad_posted'), g('pad_seen'), g('pad_lat_p99_us'), g('pad_lat_max_us')), None if f is None else True)]
        return ('REFERENCE' if f is not None else 'NOT_EVALUABLE'), mem, None
    if kind == 'p1':
        if partner is None:
            return 'NO_PARTNER', None, None
        pf = partner.get('f24') or {}
        res['partner'] = dict(tag=partner.get('tag'), pad_lat_p99_us=pf.get('pad_lat_p99_us'), pad_lat_max_us=pf.get('pad_lat_max_us'),
                              pad_posted=pf.get('pad_posted'), pad_seen=pf.get('pad_seen'), word=partner.get('word'))
        mem = [('PAD pad_lat_p99_us %s <= %s of %s + 2000' % (g('pad_lat_p99_us'), pf.get('pad_lat_p99_us'), partner.get('tag')),
                None if f is None or pf.get('pad_lat_p99_us') is None else f['pad_lat_p99_us'] <= pf['pad_lat_p99_us'] + P99_TOL),
               ('PAD pad_lat_max_us %s <= %s of %s + 16667' % (g('pad_lat_max_us'), pf.get('pad_lat_max_us'), partner.get('tag')),
                None if f is None or pf.get('pad_lat_max_us') is None else f['pad_lat_max_us'] <= pf['pad_lat_max_us'] + MAX_TOL)]
        res['row_pad'] = 'pad_posted %s, pad_seen %s (a row)' % (g('pad_posted'), g('pad_seen'))
        return pad_word(mem), mem, None
    if kind == 'f0':
        mem = [('reference: attached %s, opened %s, open_failed %s, open_lat_max_us %s; death markers (log %d, stdout %s)' % (
            g('attached'), g('opened'), g('open_failed'), g('open_lat_max_us'), len(x['death']), None if so is None else len(so['death'])),
            None if f is None else True)]
        return ('REFERENCE' if f is not None else 'NOT_EVALUABLE'), mem, None
    if kind == 'f1':
        death = [d for d, _ in x['death']] + ((so or {}).get('death') or [])
        mem = [('0 fatals: death markers 0 (log and stdout) %s' % death[:3], None if so is None else not death),
               ('opened = attached (%s / %s)' % (g('opened'), g('attached')), None if f is None else f['opened'] == f['attached'])]
        res['row_flap'] = 'open_failed %s (number, not a member), open_lat_max_us %s, FixF24 open failed lines %d' % (
            g('open_failed'), g('open_lat_max_us'), x['open_failed'])
        return word_of(mem), mem, None
    if kind == 'x1':
        qm = att.get('quit_mark') or {}
        ex = x['expired'][0] if x['expired'] else None
        after = [ln for ln in x['jp_ran'] if ex is not None and ln > ex]
        up = qm.get('exit_upper_s')
        mem = [('line FixF24: pump_stop_expired (%s)' % x['expired'][:3], bool(x['expired'])),
               ('exit code 0 (hold_exit %s)' % att.get('hold_exit'), att.get('hold_exit') == 0),
               ('0 lines TestHidLoss: jp_task ran after FixF24: pump_stop_expired (after: %s; all jp_task ran %s)' % (after[:3], x['jp_ran'][:3]),
                None if ex is None else not after),
               ('exit <= HOLD_UPD_MS + 5 s from quit posted: upper bound %s s <= 13.0 (lower %s s)' % (up, qm.get('exit_lower_s')),
                None if up is None else up <= EXIT_MAX_S)]
        return word_of(mem), mem, None
    if kind == 'd1':
        vp = [q[1] for q in x['pads'] if q[2] == TEST_PAD]
        rem = [r for r in x['removed'] if vp and r[1] == vp[0]]
        mem = [('line Controller <id>: removed of the test pad (%s; test pad id %s)' % (x['removed'][:3], vp[:1]), bool(rem)),
               ('jp_tasks >= 1 (%s)' % g('jp_tasks'), None if f is None else f['jp_tasks'] >= 1),
               ('frames >= 1 s in the stand window 0 (wide %s, strict %s)' % (win['ge1s_wide'], win['ge1s_strict']),
                None if win['ge1s_wide'] is None else win['ge1s_wide'] == 0)]
        return word_of(mem), mem, None
    if kind == 'm1':
        c = None if f is None else f['opened'] < f['attached']
        return catch_word(c), [('caught: opened < attached (%s / %s)' % (g('opened'), g('attached')), c)], 'm1 opened < attached'
    if kind == 'm2':
        ex = x['expired'][0] if x['expired'] else None
        after = [ln for ln in x['jp_ran'] if ex is not None and ln > ex]
        c = None if ex is None else bool(after)
        return catch_word(c), [('caught: TestHidLoss: jp_task ran after FixF24: pump_stop_expired (expired %s, jp_task ran %s)' % (
            x['expired'][:2], x['jp_ran'][:3]), c)], 'm2 jp_task ran after pump_stop_expired'
    if kind == 'm4':
        c = None if f is None else f['jp_tasks'] == 0
        return catch_word(c), [('caught: jp_tasks = 0 (%s)' % g('jp_tasks'), c)], 'm4 jp_tasks = 0'
    if kind == 'm5':
        if f is None:
            return 'NOT_EVALUABLE', [('caught: any f24_u1 member of item 696 (b)(3) fails', None)], 'm5'
        fails = [n for n, ok in (('upd_on_main = 0', f['upd_on_main'] == 0), ('main_late_max_us < 100000', f['main_late_max_us'] < FREE_US),
                                 ('in_lat_max_us < 100000', f['in_lat_max_us'] < FREE_US)) if not ok]
        c = bool(fails)
        return catch_word(c), [('caught: a member of f24_u1 fails (item 696 (b)(3)): failed %s (upd_on_main %s, main_late_max_us %s, '
                                'in_lat_max_us %s)' % (fails, f['upd_on_main'], f['main_late_max_us'], f['in_lat_max_us']), c)], 'm5'
    if kind == 'm6':
        c = None if o is None else (o['hid'] == o['main'] or o['helper'] == o['main'])
        return catch_word(c), [('caught: init_owner hid = main or helper = main (%s)' % o, c)], 'm6'
    if kind == 'n1':
        return judge_n1(x, att, so, o, alive, same, p, res)
    return 'NOT_EVALUABLE', None, None


def judge_n1(x, att, so, o, alive, same, p, res):
    fs_i = x['first_scene_i']
    after = [] if fs_i is None else x['frames'][fs_i + 1:]
    hold = sum(fr[2] for fr in after)
    ge1 = sum(1 for fr in after if fr[2] >= K2_US)
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
    death = [d for d, _ in x['death']] + ((so or {}).get('death') or [])
    gfl = x['first_guest_ln']
    lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None
    init_ok = bool(x['init']) and gfl is not None and x['init'][0][0] < gfl
    summ = x['summary'][-1] if x['summary'] else None
    s_fatal = None if so is None else so['fatal']
    s_exp = None if so is None else so['expired']
    mem = [('hold >= 300 s after the first scene frame (%.1f s)' % (hold / 1e6), hold >= HOLD_V_US),
           ('the process lived through the hold (outcome %s, hold_exit %s)' % (att.get('outcome'), att.get('hold_exit')), lived),
           ('0 death markers (log and stdout) %s' % death[:3], so is not None and not death),
           ('0 frames >= 1 s after the first scene frame (%d)' % ge1, fs_i is not None and ge1 == 0),
           ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN),
           ('0 one-frame glitches (%s)' % gl, gl == 0),
           ('sheet for the lead made (%s)' % sheet, bool(sheet)),
           ('FixF24: mode=1 b24=1 before the first GuestOut (admission member, %s)' % x['mode'][:1], True),
           ('FixF24: init before the first GuestOut (%s; first GuestOut %s)' % (x['init'][:1], gfl), init_ok),
           ('init_owner exactly 1 (%d, bad %d) %s: hid != 0 and helper != 0 (witness alive)' % (len(x['owner']), x['owner_bad'], o), alive),
           ('init_owner hid = helper = pump != main', same)]
    form = [('FixF21: mode=1 before the first GuestOut (%s)' % x['f21'][:2],
             bool(x['f21']) and x['f21_bad'] == 0 and all(v == 1 for v, l in x['f21']) and gfl is not None and x['f21'][0][1] < gfl),
            ('FixB12: mode=1 before the first GuestOut (%s)' % x['b12'][:2],
             bool(x['b12']) and x['b12_bad'] == 0 and all(v == 1 for v, l in x['b12']) and gfl is not None and x['b12'][0][1] < gfl),
            ('exit by the harness: Event: quit line (%s)' % x['quit_ln'], x['quit_ln'] is not None),
            ('after Event: quit: 0 --- Fatal Error --- (log %d; whole stdout %s)' % (x['fatal_after_quit'], s_fatal),
             x['quit_ln'] is not None and x['fatal_after_quit'] == 0 and s_fatal == 0),
            ('0 FixF21: wait_expired (log %d; stdout %s)' % (x['f21x'], s_exp), x['f21x'] == 0 and s_exp == 0),
            ('the process ended before the harness timeout (close_killed %s, close_rc %s)' % (att.get('close_killed'), att.get('close_rc')),
             att.get('close_killed') is False and att.get('close_rc') is not None),
            ('LogAsync: mode=1 exactly once before the first GuestOut (%s)' % [t[:30] for t, l in x['async_mode'][:2]],
             len(x['async_mode']) == 1 and x['async_mode'][0][0].startswith('LogAsync: mode=1 ') and gfl is not None
             and x['async_mode'][0][1] < gfl),
            ('summary present', summ is not None),
            ('drain_timeouts 0 (%s)' % (None if summ is None else summ['drain_timeouts']), summ is not None and summ['drain_timeouts'] == 0),
            ('FixB13: mode=1 before the first GuestOut (%s)' % x['b13'][:2],
             bool(x['b13']) and all(v == 1 for v, l in x['b13']) and gfl is not None and x['b13'][0][1] < gfl),
            ('FixB12Stat: line present (%d)' % len(x['stat12']), len(x['stat12']) >= 1)]
    res['form_members'] = [[a, b] for a, b in form]
    res['form_ok'] = all(b for _, b in form)
    res['row_n1'] = ('FixF24: pump_update_long %d, FixF24: open failed %d (rows, not members); mean dt_us %s; scene frames %d' % (
        x['upd_long'], x['open_failed'], round(hold / len(after), 1) if after else None, len(after)))
    res['video'] = dict(glitches=gl, video_index=idx_n, sheet=sheet)
    if not alive:
        return 'WITNESS_DEAD', mem, None
    return word_of(mem), mem, None


def word_of(mem):
    vals = [v for _, v in mem]
    if any(v is False for v in vals):
        return 'MEMBERS_FAIL'
    if any(v is None for v in vals):
        return 'NOT_EVALUABLE'
    return 'MEMBERS_PASS'


def pad_word(mem):
    """item 692 (g)(1): a failure by the pad probe members only (texts starting 'PAD ') - PAD_ONLY_FAIL (the repeat pair)."""
    fail = [a for a, v in mem if v is False]
    if fail and all(a.startswith('PAD ') for a in fail):
        return 'PAD_ONLY_FAIL'
    return word_of(mem)


def catch_word(c):
    return 'NOT_EVALUABLE' if c is None else ('CAUGHT' if c else 'NOT_CAUGHT')


def rows_out(res):
    out = ['F40C %s (base %s, kind %s, mode %s, KYTY_FIX_F24=%s, binary %s, level %s) reader sha256 %s' % (
        res['tag'], res['base'], res['kind'], res['mode'], res['fix'], res['binary'], res['level'], res['reader_sha256'])]
    out.append('  ADMISSION %s; STATUS %s' % ('PASS' if res['admitted'] else 'FAIL', res['status']))
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    if res['members'] is not None:
        out.append('  MEMBERS (item 692 (g), 696 (b))')
        for a, b in res['members']:
            out.append('    [%s] %s' % ('YES' if b else ('NOT_READ' if b is None else 'NO'), a))
    if res.get('form_members') is not None:
        out.append('  MEMBERS form fs12_v %s' % ('ALL YES' if res['form_ok'] else 'NOT ALL YES'))
        for a, b in res['form_members']:
            out.append('    [%s] %s' % ('YES' if b else 'NO', a))
    for k in ('row_rc6a', 'row_fixf24_other', 'row_pad', 'row_flap', 'row_n1'):
        if res.get(k):
            out.append('  ROW %s' % res[k])
    out.append('  F24 LINE %s' % json.dumps(res['f24'], sort_keys=True))
    out.append('  INIT_OWNER %s' % json.dumps(res['init_owner'], sort_keys=True))
    out.append('  WINDOW %s' % json.dumps(res['window'], sort_keys=True))
    out.append('  LINES %s' % json.dumps(res['lines'], sort_keys=True))
    out.append('  EXIT %s' % json.dumps(res['exit'], sort_keys=True))
    if res.get('partner'):
        out.append('  PARTNER %s' % json.dumps(res['partner'], sort_keys=True))
    if res.get('video'):
        out.append('  VIDEO %s' % json.dumps(res['video'], sort_keys=True))
    out.append('  WORD %s (no verdict; reading - F40d)' % res['word'])
    return out


def table(rd):
    out = ['| tag | binary | status | word | upd_on_main | main_late_max_us | in_lat_max_us | hung_ms | jp_update_max_us | jp_tasks | '
           'pad p99 / max | attached / opened | init_owner hid/helper/pump/main | expired / exit |',
           '|' + '---|' * 14]
    if os.path.isdir(rd):
        names = [t for t in os.listdir(rd) if TAG_RX.match(t) and os.path.exists(os.path.join(rd, t, 'read.json'))]
        names.sort(key=lambda t: (ORDER.index(base_of(t)) if base_of(t) in ORDER else 99, t))
        for t in names:
            r = json.load(open(os.path.join(rd, t, 'read.json'), encoding='utf-8'))
            f = r.get('f24') or {}
            o = r.get('init_owner') or {}
            e = r.get('exit') or {}
            ln = r.get('lines') or {}
            out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s | %s / %s | %s/%s/%s/%s | %s / %s |' % (
                t, r['binary'], r['status'], r['word'], f.get('upd_on_main'), f.get('main_late_max_us'), f.get('in_lat_max_us'),
                f.get('hung_ms'), f.get('jp_update_max_us'), f.get('jp_tasks'), f.get('pad_lat_p99_us'), f.get('pad_lat_max_us'),
                f.get('attached'), f.get('opened'), o.get('hid'), o.get('helper'), o.get('pump'), o.get('main'),
                len(ln.get('expired') or []), e.get('hold_exit')))
    return out


def main(argv):
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader f40c_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for l in table(rd):
            print(l)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        p = paths(tag, argv[argv.index('--dir') + 1])
        partner = None
        if '--partner' in argv:
            pd = argv[argv.index('--partner') + 1]
            pt = SPEC[base_of(tag)].get('partner') if base_of(tag) else None
            partner = read_tag(pt, paths(pt, pd)) if pt else None
            partner = partner if partner and partner.get('admitted') else None
    else:
        tag = argv[0] if argv else ''
        p = paths(tag)
        partner = None
        if base_of(tag) and SPEC[base_of(tag)].get('partner'):
            partner = partner_read(SPEC[base_of(tag)]['partner'], os.path.join(G, 'runs'))
    if not base_of(tag):
        print('usage: f40c_read.py <tag> | --dir D --tag T [--partner P] | --table')
        return 2
    res = read_tag(tag, p, partner)
    for l in rows_out(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
