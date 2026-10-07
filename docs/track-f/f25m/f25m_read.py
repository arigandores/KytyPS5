"""Track F link F25m (HPP-680; ROADMAP s122 item 613 (g)(3)-(5), (e), (z)(2) with item 615 (b)(1), (2), (6), item 616 (b)(1), (2), (4),
item 618 (b)(5), (v), item 619 (b)(1)): the reader of the KYTY_FIX_B36 series on the test binary T2 9745eb78 - the stands b36_s0 / b36_s1
(user form) and b36_f0 / b36_f1 (harness form), the cold series b36_k01..b36_k13 (form f25_k) and "no harm" b36_v / b36_w.
NO VERDICT - the reading is F25n (lead).  theta_load is read from the seal (line 'theta_load: <x>').  ASCII only.

    python f25m_read.py <tag> [--json <out>]                        one tag (files of C:/kyty/f287/f25m)
    python f25m_read.py --dir <fixture dir> --tag <tag> [--json <out>]
                                                                    fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt,
                                                                    m6.txt, cal.txt, installed_before.txt, installed_after.txt,
                                                                    installed_sha.txt, manifest_cmp.txt, snap_cmp.txt, level.txt, seal.md
    python f25m_read.py --table [--runs <dir>]                      the table over every runs/<tag>/read.json
    python f25m_read.py --series [--runs <dir>]                     stands, the cold series by level, K, S, no harm, interference

THE COLD READING (item 613 (g)(4)): K - frames in count by the rule of item 596 (d), 599 with the F25f reader f25_read.py (copy, sha256
F25_SHA, checked; its module constants BIN_B / BIN_INST set to T2 / FS9) and one class more (item 613 (z)(2)): INSTR_POLL - a K2 frame
(not B5 / B33 / B1b, not INSTR_MADE_K2) whose interval (the lines between FrameTrace n - 1 and n, the F25f mapping of FlipHold) holds a
'FlipHold:' line with poll_us >= 100 000: not in count, in K_I.  FlipHold is printed at most 32 times per run (videoOut.cpp
'hold_logged < 32'): a K2 frame after the flip of the 32nd FlipHold line - POLL_UNKNOWN (stays in count by the letter, flagged).
S - lines 'LogAsync: stall us=<us>' with us >= 1 000 000 (flush=1 lines included, split printed).
THE STANDS (item 613 (g)(3), 615 (b)(1)): a sleep = a line 'TestLogStall: i=<i> ... t0_ms=<a> t1_ms=<b> on=<caller|writer> tid=<t>
role=<r> line="<first <= 40 bytes>"'; a LongFrame line 'LongFrame: n=<n> dt_us=<us> log_async=<0|1> t_ms=<ms>' or a frame matches a sleep
when its end t_ms lies in [t0_ms - 2 000; t1_ms + 2 000] (the clock FrameStats::NowNs of all three lines; a FrameTrace frame n gets its end
t_ms from the LongFrame line n, else from flip_ns of the DiagB32 window n).
  b36_s0  member: every sleep has >= 1 LongFrame line with dt_us >= 2 500 000 in its window (letter 'from each sleep').
  b36_s1  members: 0 LongFrame lines with dt_us >= 1 000 000 (letter: the whole log; executor variant: the lines after the level line);
          >= 3 'LogAsync: stall' lines with us >= 2 900 000; full_waits 0 (the field of the summary line, item 615 (b)(2)).
  b36_f0  member: >= 1 FrameTrace frame of the scene with dt_us >= 2 500 000 in the window of a sleep (letter 'from the sleep'; the
          number of sleeps with such a frame printed - executor variant 'every sleep').
  b36_f1  member: 0 FrameTrace frames of the scene with dt_us >= 1 000 000 (executor variant: 0 LongFrame lines >= 1 s in the whole log).
  The exit window (item 616 (b)(2), 618 (b)(5)): LongFrame records of the last <= 250 ms before the exit may not reach the file - a stand
  tag is read only when the estimated exit (at_ms - 60 000 + 1 000 x (stable_s + hold_s)) is >= 250 ms after t1_ms + 2 000 of the last
  sleep (a member of the stand reading).
LOGASYNC (item 615 (b)(2), (6), 616 (b)(4)): KYTY_FIX_B36=1 - exactly one 'LogAsync: mode=1' line (absent: INTERFERENCE 'tag'); the
  summary line 'LogAsync: full_waits=' present (absent: INTERFERENCE 'run' - the tag was killed; repeat by the lead's item; its LongFrame
  / stall counts are not read).  KYTY_FIX_B36=0 - no 'LogAsync:' line at all.  drain_timeouts >= 1 in the summary (RC3): the order of
  the lines at the end of the log is not guaranteed, segments at a death are not read; the tag is read by the other members (a row).
LONGFRAMEPRINTER (item 619 (b)(1)): in tags with KYTY_LONGFRAME=1 the write time (and the stand sleep) of the thread LongFramePrinter enters
  its log_us / LogNs with the role 'other'; it does not belong to the frame holder and is not in the sum of log_us over threads (F25i
  RC4) - the reader prints the FrameTrace-draw log_us of the frame as a row only.
NO HARM (item 613 (g)(5)): b36_v - hold >= 300 s after the first scene frame, lived, 0 death markers, 0 frames >= 1 s after the first
  scene frame, video index >= 3 000, 0 one-frame glitches, the sheet made; b36_w - lived to the end of the hold (hold_s >= 310), 0 death
  markers, 0 '[Vulkan][E]', 0 limit lines of the layer, positive control ([Vulkan][W] > 0 and 'DualSrcBlend: supported=1 enabled=1'
  before the first GuestOut), no VALIDATION_STOP.  Both: 'FixB13: mode=1' before the first GuestOut.
INTERFERENCE: a failed admission member (the tag is repeated by the lead, item 273 (z); not counted).
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f25_read as R  # noqa: E402  (the F25f reader, unchanged)

F = R.F
F25_SHA = '933f36c1f63bbb3159144e1a7ca7395dc000234d6dc3be27349e40b2ff902ddf'
G = 'C:/kyty/f287/f25m'
SEAL_PATH = G + '/pred/f25m_seal.md'
BIN_T2 = '9745eb7851d541740ce9730b86258f7bb26cab270f0d35434d43037c5cefd885'
BIN_FS9 = '3861eeeae6f2487682b0519195c10d2b4d927029462e695f3634b5bdddea4eb5'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
R.BIN_B = BIN_T2
R.BIN_INST = BIN_FS9
POT, BONUS, SKY = 'pot_treasure_cave', 'bonus_path_maker_mix', 'underwater_aerial_garden'
TAG_RX = re.compile(r'^(b36_s[01]|b36_f[01]|b36_k(?:0[1-9]|1[0-3])|b36_v|b36_w)(_r[1-3])?$')
COLD_POT = ('b36_k01', 'b36_k03', 'b36_k05', 'b36_k07', 'b36_k09', 'b36_k11', 'b36_k12', 'b36_k13')
COLD_BON = ('b36_k02', 'b36_k04', 'b36_k06', 'b36_k08', 'b36_k10')
POLL_US = 100000
K2_US = 1000000
LF_S0_US = 2500000
STALL_S1_US = 2900000
STALL_S_US = 1000000
WIN_MS = 2000
EXIT_MS = 250
STAND_AT_MS = 60000
STAND = '60:3000:3'
FH_CAP = 32
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
RX_FH = re.compile(rb'^FlipHold: us=(\d+) present_us=(\d+) poll_us=(\d+) other_us=(\d+) flip=(\d+)')
RX_FTD = re.compile(rb'^FrameTrace-draw: n=(\d+) logs=(\d+) log_us=(\d+) log_gpu_us=(\d+)')
RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_B13 = re.compile(rb'FixB13: mode=(\d+)')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d) enabled=(\d)')
M_LIMIT = b'this will be the last time reporting it'
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
SUM_KEYS = ('full_waits', 'full_wait_us', 'stalls', 'stall_cut', 'lines', 'bytes', 'max_queued_bytes', 'sync_lines', 'drain_timeouts')


def sha_file(path):
    return F.sha_file(path)


def base_of(tag):
    return TAG_RX.match(tag).group(1)


def kind_of(base):
    if base in ('b36_s0', 'b36_s1'):
        return 'stand_user'
    if base in ('b36_f0', 'b36_f1'):
        return 'stand_harness'
    if base.startswith('b36_k'):
        return 'cold'
    return base[4]


def level_of(base):
    if base in ('b36_v', 'b36_w'):
        return SKY
    if base in COLD_BON:
        return BONUS
    return POT


def fix_of(base):
    return '0' if base in ('b36_s0', 'b36_f0') else '1'


def expected_env(base):
    """Every KYTY_* / VK_* key of the tag json env -> the value (None: any value; the path keys)."""
    k = kind_of(base)
    lv = level_of(base)
    e = dict(KYTY_GUEST_ARGS='-lvl ' + lv, KYTY_FIX_B36=fix_of(base))
    if k == 'stand_user':
        e.update(KYTY_LONGFRAME='1', KYTY_TEST_LOGSTALL=STAND)
        return e
    e.update(KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None, KYTY_QUEUE_TRACE='1', KYTY_GPU_CLOCK_PIN='1',
             KYTY_GPU_MARKERS='0')
    if k in ('stand_harness', 'cold'):
        e.update(KYTY_GPU_WALL='1', KYTY_GPU_HANG_ABORT_S='22', KYTY_DIAG_B32='1', KYTY_REC=None)
        if k == 'stand_harness':
            e.update(KYTY_LONGFRAME='1', KYTY_TEST_LOGSTALL=STAND)
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


def scan_extra(path, level):
    """One pass: LongFrame, LogAsync, TestLogStall, FlipHold (poll_us by the interval of the next FrameTrace), FrameTrace-draw log_us,
    FrameTrace (n, dt, draws), the level line, death markers, window events, FixB13, DualSrcBlend, [Vulkan] lines."""
    import lzma
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    r = dict(lf=[], lf_bad=0, stall=[], stall_bad=0, sleep=[], sleep_bad=0, cfg=[], mode=[], summary=[], summary_bad=0, fh=[],
             poll_ivl={}, ftd={}, ft=[], level_ln=None, first_guest_ln=None, death=[], minimized=0, recovering=0, win={}, b13=[],
             b13_before_guest=False, dual=[], vke=0, vkw=0, vk_limit=0, lines=0, sig=[], variant_dir=[], gamepatch=0)
    lvl = ('GuestOut: Level has started: %s' % level).encode()
    pend_poll = None
    ln = 0
    for line in fh:
        ln += 1
        if line.startswith(b'FrameTrace: n='):
            m = RX_FT.match(line)
            if m:
                n = int(m.group(1))
                d = RX_DRAWS.search(line)
                r['ft'].append((n, int(m.group(2)), int(d.group(1)) if d else None, ln))
                if pend_poll is not None:
                    r['poll_ivl'][n] = pend_poll
                pend_poll = None
            continue
        if line.startswith(b'FrameTrace-draw: '):
            m = RX_FTD.match(line)
            if m:
                r['ftd'][int(m.group(1))] = (int(m.group(3)), int(m.group(4)))
            continue
        if line.startswith(b'DiagB32'):
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
                r['mode'].append(line.decode('ascii', 'replace').strip()[:160])
            elif RX_SUM.match(line):
                f = dict(tok.split('=', 1) for tok in line.decode('ascii', 'replace').strip().split(' ')[1:] if '=' in tok)
                if all(k in f for k in SUM_KEYS):
                    r['summary'].append(dict((k, R.num(f[k])) for k in SUM_KEYS))
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
        if line.startswith(b'FlipHold: '):
            m = RX_FH.match(line)
            if m:
                rec = dict(us=int(m.group(1)), present=int(m.group(2)), poll=int(m.group(3)), other=int(m.group(4)), flip=int(m.group(5)))
                r['fh'].append(rec)
                pend_poll = max(pend_poll or 0, rec['poll'])
            continue
        if r['level_ln'] is None and lvl in line and line.rstrip(b'\r\n').endswith(lvl):
            r['level_ln'] = ln
        if b'GuestOut' in line and r['first_guest_ln'] is None:
            r['first_guest_ln'] = ln
        m = RX_B13.search(line)
        if m:
            r['b13'].append(int(m.group(1)))
            if r['first_guest_ln'] is None and not r['b13_before_guest']:
                r['b13_before_guest'] = True
        m = RX_DUAL.search(line)
        if m:
            r['dual'].append((m.group(1) == b'1' and m.group(2) == b'1', r['first_guest_ln'] is None))
        if b'[Vulkan][E]' in line:
            r['vke'] += 1
        if b'[Vulkan][W]' in line:
            r['vkw'] += 1
        if M_LIMIT in line:
            r['vk_limit'] += 1
        if line.startswith(b'GamePatch:'):
            r['gamepatch'] += 1
        if line.startswith(b'ShaderSeed: compatibility=') and len(r['sig']) < 4:
            mm = R.SEED.search(line)
            r['sig'].append(mm.group(1).decode('ascii') if mm else '?')
        if line.startswith(b'Shader translation cache: ') and len(r['variant_dir']) < 4:
            r['variant_dir'].append(line.decode('ascii', 'replace').strip().replace('\\', '/').rsplit('/', 1)[-1])
        for dm in F.DEATH:
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


def sleep_windows(sleeps):
    return [(s['t0_ms'] - WIN_MS, s['t1_ms'] + WIN_MS) for s in sleeps]


def in_win(t, w):
    return w[0] <= t <= w[1]


def frame_end_ms(n, lf_by_n, diag):
    if n in lf_by_n:
        return lf_by_n[n]['t_ms'], 'LongFrame'
    d = diag.get(n) if diag else None
    if d and d.get('hdr') and R.num(d['hdr'].get('flip_ns')) is not None:
        return R.num(d['hdr']['flip_ns']) // 1000000, 'flip_ns'
    return None, None


def logasync(x, fix):
    """Members of item 615 (b)(2), (6) and the RC3 row; returns (members, interference reason or None, rc3 row)."""
    summ = x['summary'][-1] if x['summary'] else None
    rc3 = None
    if fix == '1':
        m1 = len([l for l in x['mode'] if l.startswith('LogAsync: mode=1 ')]) == 1 and len(x['mode']) == 1
        m2 = summ is not None and len(x['summary']) == 1
        mem = [('LogAsync: mode=1 line exactly once (%s)' % x['mode'][:2], m1),
               ('summary line LogAsync: full_waits= present once, all fields (%d, bad %d)' % (len(x['summary']), x['summary_bad']),
                m2 and x['summary_bad'] == 0)]
        why = None if m1 else 'tag (item 615 (b)(2): no LogAsync: mode=1 at KYTY_FIX_B36=1)'
        if why is None and not m2:
            why = 'run (item 615 (b)(6): no summary line - killed; repeat by the lead; LongFrame / stall not read)'
        if summ is not None and (summ['drain_timeouts'] or 0) >= 1:
            rc3 = ('RC3 (item 616 (b)(4)): drain_timeouts %d - the order of the lines at the end of the log is not guaranteed, segments at '
                   'a death are not read; the tag is read by the other members' % summ['drain_timeouts'])
        return mem, why, rc3, summ
    none = not x['mode'] and not x['summary'] and not x['stall'] and x['summary_bad'] == 0 and x['stall_bad'] == 0
    return [('KYTY_FIX_B36=0: no LogAsync: line (mode %d, summary %d, stall %d)' % (len(x['mode']), len(x['summary']), len(x['stall'])),
             none)], (None if none else 'tag (LogAsync lines at KYTY_FIX_B36=0)'), None, summ


def stand_admission(x, fix):
    on = 'writer' if fix == '1' else 'caller'
    cfg = x['cfg']
    sl = x['sleep']
    c_ok = len(cfg) == 1 and cfg[0]['sleep_ms'] == 3000 and cfg[0]['k'] == 3 and cfg[0]['on'] == on
    s_ok = [s['i'] for s in sl] == [1, 2, 3] and all(s['on'] == on and s['slept_us'] >= 2900000 for s in sl) and x['sleep_bad'] == 0
    return [('TestLogStall config once: sleep_ms 3000, k 3, on=%s (%s)' % (on, cfg[:1]), c_ok),
            ('TestLogStall sleeps i=1,2,3, on=%s, slept_us >= 2 900 000 (%s; bad %d)' % (
                on, [(s['i'], s['slept_us'], s['on']) for s in sl][:4], x['sleep_bad']), s_ok)]


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


def read_stand(base, x, r, att):
    """Members of the stand reading (item 613 (g)(3)); x - scan_extra, r - f25_read.read_log or None (user form)."""
    sl = x['sleep']
    wins = sleep_windows(sl)
    lf = x['lf']
    lf_by_n = dict((l['n'], l) for l in lf)
    out = dict(sleeps=[dict(i=s['i'], t0_ms=s['t0_ms'], t1_ms=s['t1_ms'], slept_us=s['slept_us'], on=s['on'], tid=s['tid'], role=s['role'],
                            line=s['line']) for s in sl])
    em = exit_member(x, att)
    out['exit'] = em[2]
    mem = [(em[0], em[1])]
    lf1 = [l for l in lf if l['dt_us'] >= K2_US]
    lf1_after = [l for l in lf1 if x['level_ln'] is not None and l['ln'] > x['level_ln']]
    st29 = [s for s in x['stall'] if s['us'] >= STALL_S1_US]
    summ = x['summary'][-1] if x['summary'] else None
    out.update(lf_n=len(lf), lf_ge1s=len(lf1), lf_ge1s_after_level=len(lf1_after), lf_max=max([l['dt_us'] for l in lf] or [0]),
               stall_ge29=len(st29), full_waits=None if summ is None else summ['full_waits'])
    per = []
    if base in ('b36_s0', 'b36_s1'):
        for s, w in zip(sl, wins):
            hits = [l for l in lf if l['dt_us'] >= LF_S0_US and in_win(l['t_ms'], w)]
            per.append(dict(i=s['i'], win=w, hits=[(l['n'], l['dt_us'], l['t_ms']) for l in hits]))
        if base == 'b36_s0':
            mem.append(('every sleep has >= 1 LongFrame dt_us >= 2 500 000 in [t0_ms - 2 000; t1_ms + 2 000] (%d of %d sleeps)' % (
                sum(1 for p in per if p['hits']), len(per)), len(per) == 3 and all(p['hits'] for p in per)))
        else:
            mem += [('0 LongFrame lines dt_us >= 1 000 000 in the whole log (%d; executor variant after the level line: %d)' % (
                        len(lf1), len(lf1_after)), not lf1),
                    ('>= 3 LogAsync: stall lines us >= 2 900 000 (%d)' % len(st29), len(st29) >= 3),
                    ('full_waits 0 (summary field: %s)' % (None if summ is None else summ['full_waits']),
                     summ is not None and summ['full_waits'] == 0)]
    else:
        frames = (r or {}).get('frames_all') or []
        diag = (r or {}).get('_diag') or {}
        big = []
        for (n, dt, t_before) in frames:
            if dt >= LF_S0_US:
                t, src = frame_end_ms(n, lf_by_n, diag)
                big.append((n, dt, t, src))
        for s, w in zip(sl, wins):
            hits = [b for b in big if b[2] is not None and in_win(b[2], w)]
            per.append(dict(i=s['i'], win=w, hits=hits))
        ge1 = [(n, dt) for (n, dt, t_before) in frames if dt >= K2_US]
        out['scene_ge1s'] = len(ge1)
        out['scene_ge1s_list'] = ge1[:10]
        cross = []
        for (n, dt, t_before) in frames:
            if n in lf_by_n:
                cross.append(abs(lf_by_n[n]['dt_us'] - dt))
        out['lf_ft_cross'] = dict(pairs=len(cross), max_abs_diff_us=max(cross) if cross else None)
        if base == 'b36_f0':
            mem.append(('>= 1 scene frame dt_us >= 2 500 000 in the window of a sleep (sleeps with such a frame: %d of %d; executor '
                        'variant every sleep: %s)' % (sum(1 for p in per if p['hits']), len(per), all(p['hits'] for p in per) and
                                                      len(per) == 3), any(p['hits'] for p in per)))
        else:
            mem.append(('0 scene frames dt_us >= 1 000 000 (%d %s; executor variant LongFrame >= 1 s whole log: %d)' % (
                len(ge1), ge1[:4], len(lf1)), not ge1))
    out['per_sleep'] = per
    out['members'] = mem
    out['ok'] = all(b for _, b in mem)
    return out


def instr_poll(res, x):
    """Item 613 (z)(2): INSTR_POLL / POLL_UNKNOWN on the rows of f25_read.read_log, then K, K_I, in count, class recomputed."""
    fh = x['fh']
    cap_flip = fh[FH_CAP - 1]['flip'] if len(fh) >= FH_CAP else None
    for row in res['frames']:
        n = row['n']
        row['poll_us'] = x['poll_ivl'].get(n)
        row['instr_poll'] = False
        row['poll_unknown'] = False
        lg = x['ftd'].get(n)
        row['ftd_log_us'] = lg[0] if lg else None
        row['ftd_log_gpu_us'] = lg[1] if lg else None
        if row['k2'] and row['p_i'] and not row['instr_made_k2']:
            if (row['poll_us'] or 0) >= POLL_US:
                row['instr_poll'] = True
                row['in_count'] = False
                row['cls_reader'] = row['cls']
                row['cls'] = 'INSTR_POLL'
                row['family'] = 'INSTR_POLL'
            elif cap_flip is not None and n > cap_flip + 1:
                row['poll_unknown'] = True
    rows = res['frames']
    k2 = [z for z in rows if z['k2'] and z['p_i']]
    cnt = [z for z in rows if z['in_count']]
    ab = res['abort_hold']
    res['K_I'] = 1 if res['hold_any'] and (k2 or ab) else 0
    res['K'] = 1 if res['hold_any'] and (cnt or ab) else 0
    res['P_I_K2'] = len(k2)
    res['in_count'] = len(cnt) + (1 if ab else 0)
    res['instr_poll_n'] = sum(1 for z in rows if z.get('instr_poll'))
    res['poll_unknown_n'] = sum(1 for z in rows if z.get('poll_unknown') and z['in_count'])
    res['fliphold_lines'] = len(fh)
    res['fliphold_cap_flip'] = cap_flip
    if ab:
        res['hold_class'], res['hold_family'] = 'NO_SAMPLES:abort', 'NO_SAMPLES'
    elif cnt and res['hold_any']:
        big = max(cnt, key=lambda z: z['dt_us'])
        res['hold_class'], res['hold_family'] = big['cls'], big['family']
    else:
        res['hold_class'] = res['hold_family'] = None
    res['hold_form'] = max(cnt, key=lambda z: z['dt_us'])['form'] if cnt else None
    res['hold_burst'] = (all(z['m6_burst'] is True for z in cnt) if cnt else None)
    return res


def stall_overlap(row, x):
    """LogAsync stall lines whose [t_ms - us/1000; t_ms] meets the frame [end - dt; end] (end = flip_ns of the window n) - a row."""
    end = None
    if row.get('flip_ns') is not None and row.get('key') == row['n']:
        end = row['flip_ns'] // 1000000
    if end is None:
        return None
    a = end - row['dt_us'] // 1000
    return [(s['us'], s['t_ms']) for s in x['stall'] if s['t_ms'] - s['us'] // 1000 <= end and s['t_ms'] >= a]


def vw_members(base, x, att, idx_n, gl, sheet, death_stdout):
    ent = x['level_ln']
    first = None
    hold = 0
    ge1 = 0
    for (n, dt, draws, ln) in x['ft']:
        if ent is None or ln < ent:
            continue
        if first is None:
            if draws is not None and draws >= 100:
                first = n
            continue
        hold += dt
        if dt >= K2_US:
            ge1 += 1
    death = x['death'] + death_stdout
    m = [('FixB13: mode=1 (every line) before the first GuestOut (%s, before %s)' % (x['b13'][:3], x['b13_before_guest']),
          bool(x['b13']) and all(v == 1 for v in x['b13']) and x['b13_before_guest'])]
    if base == 'b36_v':
        lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None
        m += [('hold >= 300 s after the first scene frame (%.1f s)' % (hold / 1e6), hold >= HOLD_V_US),
              ('the process lived through the hold (outcome %s, hold_exit %s)' % (att.get('outcome'), att.get('hold_exit')), lived),
              ('0 frames >= 1 s after the first scene frame (%d; first %s)' % (ge1, first), first is not None and ge1 == 0),
              ('0 death markers (log and stdout) %s' % death[:3], not death),
              ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN),
              ('0 one-frame glitches (%s)' % gl, gl == 0),
              ('sheet for the lead made (%s)' % sheet, bool(sheet))]
    else:
        lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None and (att.get('hold_s') or 0) >= HOLD_W_S
        dual = [d for d in x['dual'] if d[0] and d[1]]
        m += [('lived to the end of the hold (outcome %s, hold_exit %s, hold_s %s >= 310)' % (att.get('outcome'), att.get('hold_exit'),
                                                                                          att.get('hold_s')), lived),
              ('0 death markers (log and stdout) %s' % death[:3], not death),
              ('0 [Vulkan][E] (%d)' % x['vke'], x['vke'] == 0),
              ('0 limit lines of the layer (%d)' % x['vk_limit'], x['vk_limit'] == 0),
              ('positive control: [Vulkan][W] %d > 0 and DualSrcBlend: supported=1 enabled=1 before the first GuestOut (%d)' % (
                  x['vkw'], len(dual)), x['vkw'] > 0 and bool(dual)),
              ('no VALIDATION_STOP (a [Vulkan][E] line and the process did not live to the end of the hold)', not (x['vke'] > 0 and not lived))]
    return m, dict(first_scene_n=first, hold_s=round(hold / 1e6, 1), frames_ge1s=ge1)


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'snap_cmp', 'glitch', 'installed_sha', 'level', 'sheet')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'), tmp=base, m6=os.path.join(base, 'm6.txt'),
                 cal=os.path.join(base, 'cal.txt'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), seal=SEAL_PATH, tmp=os.path.join(G, 'runs'), m6=os.path.join(d, 'm6.txt'),
             cal=os.path.join(d, 'cal.txt'))
    return p


_ORIG = dict(scan=F.scan, scan_b32=R.scan_b32)


def with_cache(log_path):
    """One pass per parser over the tag log: F.scan (F20c frames) and R.scan_b32 results of THIS path are kept for the call (the RC13
    stripped copy is scanned anew); the parsers themselves are not changed."""
    memo = {}

    def scan(path):
        if path != log_path:
            return _ORIG['scan'](path)
        if 'scan' not in memo:
            memo['scan'] = _ORIG['scan'](path)
        return memo['scan']

    def scan_b32(path, level):
        if path != log_path:
            return _ORIG['scan_b32'](path, level)
        if level not in memo:
            memo[level] = _ORIG['scan_b32'](path, level)
        return memo[level]
    F.scan = scan
    R.scan_b32 = scan_b32


def without_cache():
    F.scan = _ORIG['scan']
    R.scan_b32 = _ORIG['scan_b32']


def stdout_death(path):
    out = []
    if path and os.path.exists(path):
        data = open(path, 'rb').read()
        for dm in F.DEATH:
            if dm in data:
                out.append(dm.decode())
    return out


def read_tag(tag, p):
    base = base_of(tag)
    kind = kind_of(base)
    fix = fix_of(base)
    level = level_of(base)
    theta = R.read_theta(p['seal'])
    res = dict(tag=tag, form=base, kind=kind, level=level, fix=fix, reader_sha256=sha_file(os.path.abspath(__file__)),
               f25_read_sha256=sha_file(R.__file__), theta=theta)
    run = json.load(open(p['run'], encoding='utf-8')) if os.path.exists(p['run']) else None
    jbin = (run or {}).get('binary_sha256')
    res['binary_sha256'] = jbin
    inst_b = (F.text(p['installed_before']) or '').strip() or None
    inst_a = (F.text(p['installed_after']) or '').strip() or None
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env = (run or {}).get('env') or {}
    cmd = (run or {}).get('cmdline') or []
    att = ((run or {}).get('attempts') or [{}])[-1]
    mcmp = (F.text(p['manifest_cmp']) or '').strip().splitlines()
    scmp = (F.text(p['snap_cmp']) or '').strip().splitlines()
    hlev = (F.text(p['level']) or '').strip() or None
    ga = (run or {}).get('guest_args') or ''
    have_log = os.path.exists(p['log'])
    x = scan_extra(p['log'], level) if have_log else None
    r = None
    if have_log and kind in ('stand_harness', 'cold') and theta is not None:
        m6 = R.read_m6(p['m6'])
        cal = R.read_cal(p['cal'])
        with_cache(p['log'])
        try:
            r = R.read_log(p['log'], theta, level, p['tmp'], m6, cal)
            s = R.scan_b32(p['log'], level)
            fr = F.scan(p['log'])['frames']
        finally:
            without_cache()
        r['frames_all'] = [(z[1], z[2], z[3]) for z in fr]
        r['_diag'] = s['diag']
        instr_poll(r, x)
        for row in r['frames']:
            row['stall_overlap'] = stall_overlap(row, x)
    want_env = expected_env(base)
    ebad = env_diff(dict((k, v) for k, v in env.items() if k.startswith(('KYTY_', 'VK_'))), want_env)
    vv = 'true' if base == 'b36_w' else 'false'
    hold_opt = {'stand_user': 150, 'stand_harness': 150, 'cold': 330, 'v': 330, 'w': 310}[kind]
    sd = stdout_death(p['stdout'])
    adm = [
        ('tag json present', run is not None),
        ('theta_load from the seal (%s)' % theta, theta is not None),
        ('json binary_sha256 = T2 9745eb78 (%s)' % (jbin or '-')[:16], jbin == BIN_T2),
        ('installed during the tag = T2 (%s)' % ((F.text(p['installed_sha']) or '-').strip()[:16]),
         (F.text(p['installed_sha']) or '').strip() == BIN_T2),
        ('installed before = after = FS9 3861eeea (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_FS9 and inst_a == BIN_FS9),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env = the form of the tag (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad),
        ('last --vulkan-validation %s (%s)' % (vv, F.last_flag(cmd, '--vulkan-validation')), F.last_flag(cmd, '--vulkan-validation') == vv),
        ('last --shader-validation false (%s)' % F.last_flag(cmd, '--shader-validation'), F.last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args -lvl %s (%s; harness %s)' % (level, ga, hlev), ga == '-lvl ' + level and hlev == level),
        ('hold option %d s (%s)' % (hold_opt, (run or {}).get('hold_s')), (run or {}).get('hold_s') == hold_opt),
        ('log present', have_log),
        ('entry outcome ok (%s)' % att.get('outcome'), att.get('outcome') == 'ok'),
        ('window events: minimized %s, Recovering Vulkan swapchain %s (all %s)' % ((x or {}).get('minimized'), (x or {}).get('recovering'),
                                                                                  (x or {}).get('win')),
         x is not None and x['minimized'] == 0 and x['recovering'] == 0),
        ('translation signature 9177b426 and cache dir %s (%s / %s)' % (VARIANT_DIR, [z[:8] for z in (x or {}).get('sig') or []],
                                                                       (x or {}).get('variant_dir')),
         x is not None and x['sig'] == [SIG] and x['variant_dir'] == [VARIANT_DIR]),
        ('no GamePatch: line (%s)' % (x or {}).get('gamepatch'), x is not None and x['gamepatch'] == 0),
        ('caches before = snapshot of the form (%s)' % (scmp[0][:50] if scmp else '-'), bool(scmp) and scmp[0].startswith('manifest cmp EQUAL')),
        ('caches returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'), bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),
    ]
    why = None
    la = None
    if x is not None:
        la = logasync(x, fix)
        adm += la[0]
        why = la[1]
        res['rc3'] = la[2]
        res['summary'] = la[3]
        if kind in ('stand_user', 'stand_harness'):
            adm += stand_admission(x, fix)
        else:
            adm.append(('no TestLogStall line (%d / %d)' % (len(x['cfg']), len(x['sleep'])), not x['cfg'] and not x['sleep']))
    if kind == 'stand_user':
        adm += [('hold >= %d s, lived (hold_s %s, hold_exit %s)' % (HOLD_STAND_S, att.get('hold_s'), att.get('hold_exit')),
                 (att.get('hold_s') or 0) >= HOLD_STAND_S and att.get('hold_exit') is None),
                ('user form: 0 FrameTrace and 0 DiagB32 lines (%s)' % (len(x['ft']) if x else None), x is not None and not x['ft']),
                ('no death marker (log %s, stdout %s)' % ((x or {}).get('death'), sd), x is not None and not x['death'] and not sd)]
    elif kind == 'stand_harness':
        adm += [('scene entered and scene >= %d s (first %s, %s s)' % (HOLD_STAND_S, (r or {}).get('first_n'), (r or {}).get('scene_s')),
                 r is not None and r['first_n'] is not None and (r['scene_s'] or 0) >= HOLD_STAND_S),
                ('no death marker (log %s, stdout %s)' % ((x or {}).get('death'), sd), x is not None and not x['death'] and not sd),
                ('DiagB32 mode line once (%s)' % len((r or {}).get('mode') or []), r is not None and len(r['mode']) == 1 and not r['invalid'])]
    elif kind == 'cold':
        death = (r or {}).get('death') or []
        ia = death.index('GpuHangAbort:') if 'GpuHangAbort:' in death else None
        other = [z for i, z in enumerate(death) if z != 'GpuHangAbort:' and not (ia is not None and i > ia and z == '--- Error ---')]
        adm += [('scene entered (first %s)' % (r or {}).get('first_n'), r is not None and r['first_n'] is not None),
                ('hold: scene >= 300 s (%s s) or GpuHangAbort after >= 10 s (%s)' % ((r or {}).get('scene_s'), (r or {}).get('abort')),
                 r is not None and r['hold_any']),
                ('no death marker other than GpuHangAbort (%s)' % other[:3], r is not None and not other),
                ('DiagB32 mode line once, no config invalid (%s)' % len((r or {}).get('mode') or []),
                 r is not None and len(r['mode']) == 1 and not r['invalid']),
                ('rep_drop 0 (%s)' % (r or {}).get('rep_drop'), r is not None and r['rep_drop'] == 0)]
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
    gt = F.text(p['glitch'])
    if gt:
        mg = F.RX_GL.search(gt)
        gl = int(mg.group(1)) if mg else None
    sheet = (F.text(p['sheet']) or '').strip()[:120] or None
    res['ref'] = dict(glitches=gl, video_index=idx_n, outcome=att.get('outcome'), hold_exit=att.get('hold_exit'), hold_s=att.get('hold_s'),
                      stable_s=att.get('stable_s'), sheet=sheet)
    stalls = (x or {}).get('stall') or []
    res['S'] = sum(1 for s in stalls if s['us'] >= STALL_S_US)
    res['S_flush'] = sum(1 for s in stalls if s['us'] >= STALL_S_US and s['flush'])
    res['stall_lines'] = len(stalls)
    res['stall_max_us'] = max([s['us'] for s in stalls] or [0])
    res['lf_ge1s'] = sum(1 for l in (x or {}).get('lf') or [] if l['dt_us'] >= K2_US)
    res['sleeps'] = [dict(i=s['i'], t0_ms=s['t0_ms'], t1_ms=s['t1_ms'], on=s['on'], tid=s['tid'], role=s['role'], line=s['line'])
                     for s in (x or {}).get('sleep') or []]
    res['log'] = None
    if r is not None:
        rr = dict((k, v) for k, v in r.items() if k not in ('_diag', 'frames_all'))
        res['log'] = rr
        res['scene_ge1s'] = sum(1 for (n, dt, t) in r['frames_all'] if dt >= K2_US)
    res['stand'] = read_stand(base, x, r, att) if x is not None and kind in ('stand_user', 'stand_harness') else None
    res['vw'] = None
    if x is not None and kind in ('v', 'w'):
        m, info = vw_members(base, x, att, idx_n, gl, sheet, sd)
        res['vw'] = dict(members=m, ok=all(b for _, b in m), info=info)
    res['reading'] = 'ADMITTED (no verdict; reading - F25n)' if admitted else 'INTERFERENCE: %s' % res['interference']
    return res


def rows_out(res):
    out = ['tag %s (form %s, kind %s, level %s, KYTY_FIX_B36=%s)  reader sha256 %s  f25_read sha256 %s  theta %s' % (
        res['tag'], res['form'], res['kind'], res['level'], res['fix'], res['reader_sha256'], res['f25_read_sha256'], res['theta'])]
    out.append('  ADMISSION %s; STATUS %s' % ('PASS' if res['admitted'] else 'FAIL', res['status']))
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    out.append('  binary_sha256 %s' % res['binary_sha256'])
    if res.get('rc3'):
        out.append('  %s' % res['rc3'])
    out.append('  LogAsync summary %s; S (stall us >= 1 000 000) %d (flush=1 %d); stall lines %d, max us %d; LongFrame >= 1 s %d' % (
        res.get('summary'), res['S'], res['S_flush'], res['stall_lines'], res['stall_max_us'], res['lf_ge1s']))
    for s in res['sleeps']:
        out.append('  SLEEP i %d t0_ms %d t1_ms %d on %s tid %d role %s line="%s"' % (s['i'], s['t0_ms'], s['t1_ms'], s['on'], s['tid'],
                                                                                   s['role'], s['line'] if s['line'] is not None else '<absent>'))
    st = res.get('stand')
    if st:
        out.append('  STAND %s %s; exit gap %s ms; LongFrame %d (>= 1 s %d, after the level line %d, max %d); stall >= 2.9 s %d; full_waits %s'
                   % (res['form'], 'PASS' if st['ok'] else 'FAIL', st['exit'], st['lf_n'], st['lf_ge1s'], st['lf_ge1s_after_level'],
                      st['lf_max'], st['stall_ge29'], st['full_waits']))
        for a, b in st['members']:
            out.append('    [%s] %s' % ('ok' if b else 'NO', a))
        for p in st['per_sleep']:
            out.append('    sleep %d window %s hits %s' % (p['i'], list(p['win']), p['hits'][:6]))
        if 'scene_ge1s' in st:
            out.append('    scene frames >= 1 s %d %s; LongFrame / FrameTrace dt cross-check %s' % (st['scene_ge1s'], st['scene_ge1s_list'][:6],
                                                                                              st['lf_ft_cross']))
    r = res.get('log')
    if r:
        out.append('  scene: first_n %s, frames %d, scene %.1f s, hold %s (abort hold %s); DiagB32 lines %d; death %s' % (
            r['first_n'], r['frames_n'], r['scene_s'], r['hold'], r['abort_hold'], r['diag_lines'], r['death'][:4]))
        out.append('  K_I %d; K %d; K2 frames not attributed %d; in count %d; INSTR_MADE_K2 %d; INSTR_POLL %d; POLL_UNKNOWN in count %d; '
                   'FlipHold lines %d (cap flip %s); scene frames >= 1 s %s' % (
                       r['K_I'], r['K'], r['P_I_K2'], r['in_count'], r['instr_made_k2'], r['instr_poll_n'], r['poll_unknown_n'],
                       r['fliphold_lines'], r['fliphold_cap_flip'], res.get('scene_ge1s')))
        out.append('  hold class (longest frame in count): %s; family %s; form %s; M6_BURST all %s' % (
            r['hold_class'], r['hold_family'], r['hold_form'], r['hold_burst']))
        for z in r['frames'][:80]:
            tg = ' IN COUNT' if z['in_count'] else (' INSTR_POLL' if z.get('instr_poll') else (' INSTR_MADE_K2' if z['instr_made_k2'] else (
                ' K2-ref(%s)' % z['attr'] if z['k2'] else ' ref')))
            out.append('    FRAME n %d dt_us %d t %.1f s attr %s | key %s(%s) win %s instr %s | %s%s%s | %s | poll_us %s | ftd log_us %s '
                       'log_gpu_us %s | stall overlap %s | %s | M6_BURST %s' % (
                           z['n'], z['dt_us'], z['t_s'], z['attr'], z['key'], z['key_branch'], z['key_dt_us'], z['instr_us'], z['cls'], tg,
                           ' POLL_UNKNOWN' if z.get('poll_unknown') else '', ' > '.join(z['path'] or []), z.get('poll_us'),
                           z.get('ftd_log_us'), z.get('ftd_log_gpu_us'), z.get('stall_overlap'), z['form'], z['m6_burst']))
        out.append('  U5 windows bad %d %s' % (r['u5_bad_n'], r['u5_bad'][:4]))
    vw = res.get('vw')
    if vw:
        out.append('  NO HARM %s %s %s' % (res['form'], 'PASS' if vw['ok'] else 'FAIL', vw['info']))
        for a, b in vw['members']:
            out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    rf = res['ref']
    out.append('  REFERENCE: glitches %s, video index %s, outcome %s, hold_exit %s, hold_s %s, stable_s %s, sheet %s' % (
        rf['glitches'], rf['video_index'], rf['outcome'], rf['hold_exit'], rf['hold_s'], rf['stable_s'], rf['sheet']))
    out.append('  LONGFRAMEPRINTER (item 619 (b)(1)): its log_us / LogNs (role other) are not the frame holder\'s and not in the sum of '
               'log_us over threads (F25i RC4)')
    out.append('  READING %s' % res['reading'])
    return out


def load_runs(rd):
    out = {}
    if not os.path.isdir(rd):
        return out
    for t in os.listdir(rd):
        if TAG_RX.match(t) and os.path.exists(os.path.join(rd, t, 'read.json')):
            out[t] = json.load(open(os.path.join(rd, t, 'read.json'), encoding='utf-8'))
    return out


def first_good(runs, base):
    tags = sorted(t for t in runs if base_of(t) == base and runs[t]['status'] == 'ADMITTED')
    return tags[0] if tags else None


def table(rd):
    runs = load_runs(rd)
    out = ['| tag | level | status | binary_sha256 | K | K_I | in count | INSTR_POLL | S | frames >= 1 s (scene / LongFrame) | full_waits | '
           'drain_timeouts | members | glitches |', '|' + '---|' * 14]
    for t in sorted(runs):
        res = runs[t]
        r = res.get('log') or {}
        sm = res.get('summary') or {}
        mem = res.get('stand') or res.get('vw')
        out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %d | %s / %d | %s | %s | %s | %s |' % (
            t, res['level'][:5], res['status'], (res['binary_sha256'] or '-')[:8], r.get('K', '-'), r.get('K_I', '-'), r.get('in_count', '-'),
            r.get('instr_poll_n', '-'), res['S'], res.get('scene_ge1s', '-'), res['lf_ge1s'], sm.get('full_waits'), sm.get('drain_timeouts'),
            '-' if mem is None else ('PASS' if mem['ok'] else 'FAIL'), res['ref'].get('glitches')))
    return out


def series(rd):
    runs = load_runs(rd)
    out = ['SERIES over %s (tags read %d)' % (rd, len(runs))]
    interf = sorted(t for t in runs if runs[t]['status'] != 'ADMITTED')
    out.append('INTERFERENCE %d %s' % (len(interf), ['%s: %s' % (t, (runs[t].get('interference') or '')[:60]) for t in interf][:8]))
    for b in ('b36_s0', 'b36_s1', 'b36_f0', 'b36_f1'):
        t = first_good(runs, b)
        st = runs[t]['stand'] if t else None
        out.append('STAND %s %s' % (b, 'PENDING' if t is None else '%s (%s) %s' % ('PASS' if st['ok'] else 'FAIL', t,
                                                                                      [a[:70] for a, ok in st['members'] if not ok][:3])))
    stot = 0
    for lv, bases in ((POT, COLD_POT), (BONUS, COLD_BON)):
        tags = [first_good(runs, b) for b in bases]
        got = [t for t in tags if t]
        k = sum(runs[t]['log']['K'] for t in got)
        ki = sum(runs[t]['log']['K_I'] for t in got)
        s = sum(runs[t]['S'] for t in got)
        stot += s
        ip = sum(runs[t]['log']['instr_poll_n'] for t in got)
        out.append('COLD %s admitted %d of %d: K %d, K_I %d, INSTR_POLL frames %d, S %d; classes %s' % (
            lv, len(got), len(bases), k, ki, ip, s, sorted(set(str(runs[t]['log']['hold_class']) for t in got if runs[t]['log']['K']))))
    out.append('COLD S (stall us >= 1 000 000) over the series %d - no verdict, the reading of item 613 (g)(4) is F25n' % stot)
    for b in ('b36_v', 'b36_w'):
        t = first_good(runs, b)
        out.append('NO HARM %s %s' % (b, 'PENDING' if t is None else '%s (%s)' % ('PASS' if runs[t]['vw']['ok'] else 'FAIL', t)))
    made = len(runs)
    out.append('BUDGET tags read %d (plan 19 + repeats)' % made)
    return out


def main(argv):
    if '--table' in argv or '--series' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        lines = table(rd) if '--table' in argv else series(rd)
        print('reader f25m_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for l in lines:
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
        print('usage: f25m_read.py b36_s0|b36_s1|b36_f0|b36_f1|b36_k01..13|b36_v|b36_w[_r1..3] | --dir D --tag T | --table | --series')
        return 2
    if sha_file(R.__file__) != F25_SHA:
        print('f25_read.py sha256 %s != %s - refused' % (sha_file(R.__file__), F25_SHA))
        return 1
    res = read_tag(tag, p)
    for l in rows_out(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
