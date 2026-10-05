"""Track F link F20e (HPP-624; ROADMAP s122 item 543 (e); port of the F20c reader, item 462 (g)-(d), item 451 (e)): the reader of
the V Sky Garden series F20e for B2 and B32.  Edits against F20c: binary admission (FS8 only), the stop rule and the summary of
item 543 (e) (B2 base 28 warm, B32 - the F20e series alone); the reading rules of a tag are those of F20c.
Base: docs/track-f/f20a/sweep_f20a.py (interval of a frame, first scene frame), b2win_f20a.py (frame index after the first scene
frame), ana_f20a.py (B32 hold, attribution order).  ASCII only.

    python f20e_read.py <tag> [--json <out>]                 one tag of the series (files of C:/kyty/f287/f20e)
    python f20e_read.py --dir <fixture dir> --tag <tag> [--bin <sha256>] [--json <out>]
                                                              fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt,
                                                              installed_before.txt, installed_after.txt, manifest_cmp.txt, seal.md
    python f20e_read.py --regress [--out <file>]              the F20a logs of the main variant (item 462 (b)): N warm 6, N holds 8,
                                                              B2 frames 0, unattributed 0 - exit 1 otherwise
    python f20e_read.py --series [--runs <dir>]              the series: B2 base 28 + every read.json of runs/f20_vNN; B32 of
                                                              F20e alone; the stop rule of item 543 (e)
    python f20e_read.py --check-seal [--seal <md>]            every 'seal: <sha256> <path>' line of the seal against the file

DEFINITIONS (item 462 (b), (g)):
  scene            the first 'Level has started: underwater_aerial_garden' line (non-empty name); the scene ends at the next non-empty
                   'Level has started:' line or at 'Event: quit' (frames after it are not counted).
  first scene frame the first 'FrameTrace: n=' line with draws >= 100 after the level line; its own dt is not counted.
  frame idx        1-based index of a frame after the first scene frame; t_before = sum of dt_us of the frames idx 1..idx-1.
  interval         the log lines between the previous 'FrameTrace: n=' line (any) and the frame's own line.
  dump lines       IR lines (first non-blank character '%') + GCN listing lines ('<hex>: X_', not tab-led) of the interval.
  B2 window        frames idx 723..828 (B2_LO..B2_HI).  The window is read only when the scene holds frame idx 828.
  warm entry       window read and 0 dump lines in the intervals of the frames idx 723..828; cold entry - not in N of B2.
  B2 frame         a frame of the window of a warm entry with dt_us >= 100 000, and in its interval 0 lines
                   'Vulkan pipeline cache: saved' and 0 line starts 'BvhLoopCapTrip:'.
  B32 hold         a scene with scene time (sum of dt_us after the first scene frame) >= 300 s; every hold is in N (cold too).
  hold frame       dt_us >= 100 000 that STARTS at t_before >= 10 s.
  attribution      (item 451 (e) order) 'Vulkan pipeline cache: saved' -> B33 (only on the binaries before adb0c82f) ->
                   'BvhLoopCapTrip:' -> B1b -> dump lines -> B5 -> only 'PriorityStall:' -> 'prio only' -> 'nothing'.
                   Unattributed = 'nothing' + 'prio only' (item 462 (b)(4)).
                   LETTER (main): on adb0c82f, FS6 and FS8 a cache save is no attribution - the frame goes on to the next member.
                   VARIANT F20a (executor variant, printed beside): on adb0c82f / FS6 / FS8 a frame with a cache save is unattributed.
  reference        death markers (log and stdout), frames >= 1 s after the entry window, one-frame glitches of the video,
                   'AsyncPipelines: skipped draw' lines - not members.
ADMISSION of a tag (item 462 (g); a failed member = interference, the tag is repeated and is not counted): json binary_sha256 =
  FS8 2c9b69b9 (one binary of the series, item 543 (e)); installed before = after = json binary; json prereg sha256 = sha256 of the seal; env holds only the harness
  constants HARN; the last --vulkan-validation and --shader-validation are 'false', no --rd; guest args '-lvl underwater_aerial_garden';
  hold 330 s; no stand / patch / gate line in the log; the scene entered (first scene frame); 0 lines 'Window <id> minimized' and
  'Recovering Vulkan swapchain'; caches returned (manifest_cmp EQUAL).
STOP RULE (item 543 (e)): tags go until both hold: (i) B2 warm N = 28 + warm tags of F20e >= 30; (ii) B32 - a hold of F20e with
  >= 1 unattributed frame (letter) or 29 holds of F20e without one; at most 30 tags (f20_v25..f20_v54); interference is repeated.
"""
import hashlib
import json
import lzma
import math
import os
import re
import sys

G = 'C:/kyty/f287/f20e'
SEAL_PATH = G + '/pred/f20e_seal.md'
SG = b'underwater_aerial_garden'
B2_LO, B2_HI = 723, 828
SLOW_US = 100000
WIN_US = 10000000
HOLD_US = 300000000
K1S_US = 1000000
HOLD_S = 330
N_TARGET = 30
TAG_MAX = 30
B32_HOLDS = 29
BASE = dict(warm=28, b2=0)    # B2 base after F20d, item 543 (g): F20a 6 + F20c 22 warm entries, 0 B2 frames
BIN_OK = {'2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b': 'FS8 2c9b69b9'}
PRE_S12 = ('9235a7ac', 'dac02fb9', 'bbad499c', '4aa62e95', '540c035a', '31cbfee8', '631ff987')
HARN = {'KYTY_FRAME_TRACE', 'KYTY_GPU_HANG_ABORT_S', 'KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE', 'KYTY_QUEUE_TRACE', 'KYTY_GPU_CLOCK_PIN',
        'KYTY_GPU_MARKERS', 'KYTY_GUEST_ARGS', 'KYTY_REC'}
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
STAND = (b'GamePatch:', b'TestHidLoss:', b'TestAudioLoss:', b'TestMinimize:', b'PVar: armed', b'GateArm:', b'MainStallTest',
         b'PrepareHold')
FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
DRAWS = re.compile(rb' draws=(\d+)')
GCN = re.compile(rb'[0-9a-fA-F]+: [A-Z]_')
US_EQ = re.compile(rb' us=(\d+)')
MINI = re.compile(rb'Window \d+ minimized')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
LVL = b'Level has started:'
# F20a main-variant Sky Garden logs (ana_f20a_rc1.txt; item 462 (b)): path, binary prefix
REGRESS = (('C:/kyty/s128/log_shp128.txt.xz', '9235a7ac'), ('C:/kyty/s142/log_v142.txt', '9235a7ac'),
           ('C:/kyty/f287/fsc/log_fs_b.txt', 'dac02fb9'), ('C:/kyty/s146/log_i146_v.txt', 'dac02fb9'),
           ('C:/kyty/f287/fs3/fs3c/log_fs3_v.txt', '540c035a'), ('C:/kyty/f287/fs4c/log_fs4_v.txt', '31cbfee8'),
           ('C:/kyty/f287/fs5/fs5c/log_fs5_v.txt', '631ff987'), ('C:/kyty/f287/fs5/fs5e/log_fs5_i.txt', '631ff987'),
           ('C:/kyty/s288/s12/log_s12_v.txt', 'adb0c82f'))
REGRESS_WANT = dict(warm=6, holds=8, b2=0, unattr=0)


def sha_file(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def text(path):
    if not path or not os.path.exists(path):
        return None
    return open(path, 'rb').read().decode('utf-8', 'replace')


def new_iv():
    return [0, 0, 0, 0, 0, 0]          # ir, gcn, pcs, trip, prio, prio_us


def scan(path):
    """One pass over the log; returns the scene frames with their interval counters and the whole-log markers."""
    f = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    r = dict(lines=0, level_line=None, first_n=None, first_line=None, ended_by=None, frames=[], death=[], skipped=0, minimized=0,
             recovering=0, stand=[], sg_levels=0)
    state = 0                           # 0 before the scene, 1 in the scene, 2 after it
    cur = new_iv()
    fr = r['frames']
    sum_us = 0
    ln = 0
    for line in f:
        ln += 1
        if line.startswith(b'FrameTrace: n='):
            m = FT.match(line)
            if m:
                if state == 1:
                    n, dt = int(m.group(1)), int(m.group(2))
                    if r['first_n'] is None:
                        d = DRAWS.search(line)
                        if d and int(d.group(1)) >= 100:
                            r['first_n'] = n
                            r['first_line'] = ln
                    else:
                        fr.append((len(fr) + 1, n, dt, sum_us, cur[0], cur[1], cur[2], cur[3], cur[4], cur[5]))
                        sum_us += dt
                cur = new_iv()
                continue
        if b'---' in line or b'Unhandled' in line or b'GpuHang' in line or b'DeviceLost' in line:
            for d in DEATH:
                if d in line and len(r['death']) < 20:
                    r['death'].append([d.decode(), ln])
        if line.startswith(b'AsyncPipelines: skipped draw'):
            r['skipped'] += 1
        if b'Window ' in line and MINI.search(line):
            r['minimized'] += 1
        if b'Recovering Vulkan swapchain' in line:
            r['recovering'] += 1
        if line.startswith(STAND) and len(r['stand']) < 10:
            r['stand'].append(line[:80].decode('ascii', 'replace').strip())
        i = line.find(LVL)
        if i != -1:
            name = line[i + len(LVL):].strip()
            if name:
                if name == SG:
                    r['sg_levels'] += 1
                if state == 1:
                    state = 2
                    r['ended_by'] = 'level'
                elif state == 0 and name == SG:
                    state = 1
                    r['level_line'] = ln
            continue
        if line.startswith(b'Event: quit'):
            if state == 1:
                state = 2
                r['ended_by'] = 'quit'
            continue
        t = line.strip()
        if not t:
            continue
        if t[:1] == b'%':
            cur[0] += 1
        elif line[:1] != b'\t' and GCN.match(t):
            cur[1] += 1
        elif b'Vulkan pipeline cache: saved' in t:
            cur[2] += 1
        elif t.startswith(b'BvhLoopCapTrip:'):
            cur[3] += 1
        elif t.startswith(b'PriorityStall:'):
            cur[4] += 1
            u = US_EQ.search(t)
            if u:
                cur[5] = max(cur[5], int(u.group(1)))
    f.close()
    r['lines'] = ln
    r['scene_us'] = sum_us
    return r


def attr(fr, binary, variant):
    """Attribution of a hold frame by its interval (item 451 (e) order); variant 'letter' or 'f20a'."""
    _, _, _, _, ir, gcn, pcs, trip, prio, _ = fr
    pre = binary[:8] in PRE_S12
    if pcs:
        if pre:
            return 'B33'
        if variant == 'f20a':
            return 'pcs after S12'
    if trip:
        return 'B1b'
    if ir or gcn:
        return 'B5'
    if prio:
        return 'prio only'
    return 'nothing'


UNATTR = ('nothing', 'prio only', 'pcs after S12')


def evaluate(r, binary):
    fr = r['frames']
    e = dict(entered=r['level_line'] is not None and r['first_n'] is not None, first_n=r['first_n'], frames=len(fr),
             scene_s=round(r['scene_us'] / 1e6, 3), ended_by=r['ended_by'], sg_levels=r['sg_levels'])
    win = [x for x in fr if B2_LO <= x[0] <= B2_HI]
    e['window_read'] = len(fr) >= B2_HI
    e['window_dump'] = sum(x[4] + x[5] for x in win)
    e['window_dump_frames'] = [[x[0], x[4] + x[5]] for x in win if x[4] + x[5]][:20]
    e['warm'] = bool(e['window_read'] and e['window_dump'] == 0)
    slow_win = [x for x in win if x[2] >= SLOW_US]
    e['window_slow'] = [[x[0], x[1], x[2], x[6], x[7], x[8], x[9]] for x in slow_win]
    e['b2_frames'] = [[x[0], x[1], x[2], x[8], x[9]] for x in slow_win if x[6] == 0 and x[7] == 0] if e['warm'] else []
    e['window_max_us'] = max([x[2] for x in win] or [0])
    e['hold'] = r['scene_us'] >= HOLD_US
    hf = [x for x in fr if x[2] >= SLOW_US and x[3] >= WIN_US]
    rows = []
    for x in hf:
        rows.append(dict(idx=x[0], n=x[1], dt_us=x[2], t_before_s=round(x[3] / 1e6, 3), ir=x[4], gcn=x[5], pcs=x[6], trip=x[7],
                         prio=x[8], prio_us=x[9], letter=attr(x, binary, 'letter'), f20a=attr(x, binary, 'f20a')))
    e['hold_frames'] = rows
    e['unattr'] = sum(1 for x in rows if x['letter'] in UNATTR) if e['hold'] else 0
    e['unattr_f20a'] = sum(1 for x in rows if x['f20a'] in UNATTR) if e['hold'] else 0
    e['entry_window'] = [[x[0], x[1], x[2]] for x in fr if x[2] >= SLOW_US and x[3] < WIN_US]
    e['k1s_after'] = sum(1 for x in fr if x[2] >= K1S_US and x[3] >= WIN_US)
    e['dt_max_after'] = max([x[2] for x in fr if x[3] >= WIN_US] or [0])
    e['death'] = r['death']
    e['skipped'] = r['skipped']
    e['minimized'] = r['minimized']
    e['recovering'] = r['recovering']
    e['stand'] = r['stand']
    return e


def last_flag(cmd, flag):
    v = None
    for i, a in enumerate(cmd or []):
        if a == flag:
            v = cmd[i + 1] if i + 1 < len(cmd) else ''
    return v


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch')
    if base is not None:
        p = dict((n, os.path.join(base, n + '.txt')) for n in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((n, os.path.join(d, n + '.txt')) for n in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), seal=SEAL_PATH)
    return p


def stdout_death(path):
    out = []
    t = text(path)
    if t is None:
        return None
    for i, l in enumerate(t.splitlines(), 1):
        for d in DEATH:
            if d.decode() in l:
                out.append(['stdout', d.decode(), i])
    return out


def read_tag(tag, p):
    res = dict(tag=tag, reader_sha256=sha_file(os.path.abspath(__file__)))
    run = None
    if os.path.exists(p['run']):
        run = json.load(open(p['run'], encoding='utf-8'))
    jbin = (run or {}).get('binary_sha256')
    res['binary_sha256'] = jbin
    inst_b = (text(p['installed_before']) or '').strip() or None
    inst_a = (text(p['installed_after']) or '').strip() or None
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env = (run or {}).get('env') or {}
    cmd = (run or {}).get('cmdline') or []
    att = ((run or {}).get('attempts') or [{}])[-1]
    mcmp = (text(p['manifest_cmp']) or '').strip().splitlines()
    r = scan(p['log']) if os.path.exists(p['log']) else None
    e = evaluate(r, jbin or '') if r else None
    adm = [
        ('tag json present', run is not None),
        ('json binary_sha256 = FS8 2c9b69b9 (%s)' % (BIN_OK.get(jbin) or (jbin or '-')[:16]), jbin in BIN_OK),
        ('installed before = after = json binary (%s / %s)' % ((inst_b or '-')[:8], (inst_a or '-')[:8]),
         jbin is not None and inst_b == jbin and inst_a == jbin),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env only harness constants (extra: %s)' % sorted(k for k in env if k not in HARN), run is not None and all(k in HARN for k in env)),
        ('last --vulkan-validation false (%s)' % last_flag(cmd, '--vulkan-validation'), last_flag(cmd, '--vulkan-validation') == 'false'),
        ('last --shader-validation false (%s)' % last_flag(cmd, '--shader-validation'), last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args -lvl underwater_aerial_garden (%s)' % (run or {}).get('guest_args'),
         (run or {}).get('guest_args') == '-lvl underwater_aerial_garden'),
        ('hold %d s (%s)' % (HOLD_S, (run or {}).get('hold_s')), (run or {}).get('hold_s') == HOLD_S),
        ('log present', r is not None),
        ('no stand / patch / gate line (%s)' % ((e or {}).get('stand') or [])[:2], e is not None and not e['stand']),
        ('scene entered (first scene frame %s)' % (e or {}).get('first_n'), e is not None and e['entered']),
        ('window events: minimized %s, Recovering Vulkan swapchain %s' % ((e or {}).get('minimized'), (e or {}).get('recovering')),
         e is not None and e['minimized'] == 0 and e['recovering'] == 0),
        ('caches returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'), bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),
    ]
    res['admission'] = [[a, bool(b)] for a, b in adm]
    res['admitted'] = all(b for _, b in adm)
    res['eval'] = e
    sd = stdout_death(p['stdout'])
    idx_n = None
    if os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as fi:
            idx_n = sum(1 for _ in fi)
    gl = None
    gt = text(p['glitch'])
    if gt:
        mg = RX_GL.search(gt)
        gl = int(mg.group(1)) if mg else None
    res['ref'] = dict(death_log=(e or {}).get('death'), death_stdout=sd, k1s_after=(e or {}).get('k1s_after'),
                      dt_max_after=(e or {}).get('dt_max_after'), glitches=gl, video_index=idx_n, skipped_draw=(e or {}).get('skipped'),
                      outcome=att.get('outcome'), hold_exit=att.get('hold_exit'), hold_s=att.get('hold_s'))
    if not res['admitted']:
        res['reading'] = 'INTERFERENCE (repeat, not counted)'
    else:
        b2 = 'B2: window not read (scene < %d frames)' % B2_HI if not e['window_read'] else \
            ('B2: warm, frames %d' % len(e['b2_frames']) if e['warm'] else 'B2: cold window (dump %d lines) - not in N' % e['window_dump'])
        b32 = 'B32: hold, unattributed %d (variant F20a %d)' % (e['unattr'], e['unattr_f20a']) if e['hold'] else \
            'B32: no hold (scene %.1f s)' % e['scene_s']
        res['reading'] = b2 + '; ' + b32
    return res


def rows(res):
    out = ['tag %s  reader sha256 %s' % (res['tag'], res['reader_sha256'])]
    out.append('  ADMISSION %s' % ('PASS' if res['admitted'] else 'FAIL'))
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    e = res['eval']
    if e:
        out.append('  scene: first_n %s, frames %d, scene %.1f s, ended by %s, Sky Garden level lines %d' % (
            e['first_n'], e['frames'], e['scene_s'], e['ended_by'], e['sg_levels']))
        out.append('  B2 window idx %d..%d: read %s, dump lines %d %s, warm %s, max dt_us %d, frames >= 100 ms %s, B2 frames %s' % (
            B2_LO, B2_HI, e['window_read'], e['window_dump'], e['window_dump_frames'][:6], e['warm'], e['window_max_us'], e['window_slow'],
            e['b2_frames']))
        out.append('  B32: hold %s; hold frames %d; unattributed %d (variant F20a %d)' % (e['hold'], len(e['hold_frames']), e['unattr'],
                                                                                        e['unattr_f20a']))
        for x in e['hold_frames'][:40]:
            out.append('    FRAME idx %d n %d dt_us %d t %.1f s | ir %d gcn %d pcs %d trip %d prio %d/%d | %s / %s' % (
                x['idx'], x['n'], x['dt_us'], x['t_before_s'], x['ir'], x['gcn'], x['pcs'], x['trip'], x['prio'], x['prio_us'], x['letter'],
                x['f20a']))
        out.append('  entry window frames >= 100 ms [idx, n, dt_us]: %s' % e['entry_window'][:8])
    rf = res['ref']
    out.append('  REFERENCE: death log %s stdout %s; frames >= 1 s after the entry window %s (max dt_us %s); one-frame glitches %s; '
               'video index %s; skipped draw %s; outcome %s, hold_exit %s, hold_s %s' % (
                   rf['death_log'], rf['death_stdout'], rf['k1s_after'], rf['dt_max_after'], rf['glitches'], rf['video_index'],
                   rf['skipped_draw'], rf['outcome'], rf['hold_exit'], rf['hold_s']))
    out.append('  READING %s' % res['reading'])
    return out


def cp(k, n, lo):
    """Clopper-Pearson bound, two-sided 95 % (ana_f20a.py)."""
    if n == 0:
        return float('nan')
    if lo and k == 0:
        return 0.0
    if not lo and k == n:
        return 1.0
    a = 0.025

    def cdf(p, kk):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, kk + 1))
    x, y = 0.0, 1.0
    for _ in range(60):
        m = (x + y) / 2
        if lo:
            if 1 - cdf(m, k - 1) < a:
                x = m
            else:
                y = m
        else:
            if cdf(m, k) > a:
                x = m
            else:
                y = m
    return (x + y) / 2


def reading(n, k, what):
    """Item 462 (d): N >= 30 and 0 -> NOT A DEFECT; >= 1 -> defect with p and the interval; N < 30 and 0 -> shortage."""
    if k >= 1:
        return '%s: DEFECT candidate, %d of %d, p = %.3f, 95 %% CP [%.3f; %.3f]' % (what, k, n, k / n, cp(k, n, True), cp(k, n, False))
    if n >= N_TARGET:
        return '%s: NOT A DEFECT candidate, 0 of %d (upper 95 %% CP %.3f)' % (what, n, cp(0, n, False))
    return '%s: SHORTAGE, 0 of %d (%d to go)' % (what, n, N_TARGET - n)


def b32_line(n, k, what):
    """B32 of the F20e series alone (item 543 (e), (zh)): k holds with >= 1 unattributed frame of n holds."""
    if n == 0:
        return '%s: 0 holds' % what
    if k >= 1:
        return '%s: %d of %d holds, 95 %% CP [%.3f; %.3f]' % (what, k, n, cp(k, n, True), cp(k, n, False))
    return '%s: 0 of %d holds (one-sided upper 95 %% %.3f)' % (what, n, 1 - 0.05 ** (1.0 / n))


def series(results, base=BASE):
    s = dict(warm=base['warm'], b2=base['b2'], holds=0, unattr=0, unattr_f20a=0)    # B32: the F20e series alone
    tags = dict(made=0, interference=0, warm=0, cold=0, unread=0, holds=0, nohold=0)
    for res in results:
        tags['made'] += 1
        if not res['admitted']:
            tags['interference'] += 1
            continue
        e = res['eval']
        if e['window_read']:
            if e['warm']:
                tags['warm'] += 1
                s['warm'] += 1
                s['b2'] += 1 if e['b2_frames'] else 0
            else:
                tags['cold'] += 1
        else:
            tags['unread'] += 1
        if e['hold']:
            tags['holds'] += 1
            s['holds'] += 1
            s['unattr'] += 1 if e['unattr'] else 0
            s['unattr_f20a'] += 1 if e['unattr_f20a'] else 0
        else:
            tags['nohold'] += 1
    stop_b2 = s['warm'] >= N_TARGET
    stop_b32 = s['unattr'] >= 1 or s['holds'] - s['unattr'] >= B32_HOLDS
    out = dict(sum=s, tags=tags, b2=reading(s['warm'], s['b2'], 'B2 (entries with >= 1 B2 frame; base 28 warm of F20a + F20c)'),
               b32=b32_line(s['holds'], s['unattr'], 'B32 Sky Garden, F20e alone (holds with >= 1 unattributed frame, letter)'),
               b32_f20a=b32_line(s['holds'], s['unattr_f20a'], 'B32 Sky Garden, F20e alone (variant F20a)'),
               stop_i=stop_b2, stop_ii=stop_b32,
               need_more=not (stop_b2 and stop_b32) and tags['made'] < TAG_MAX)
    return out


def regress_one(a):
    # the result of one log is cached in G/regress_cache (key: path, size, mtime) so a run killed by the watchdog resumes
    path, b = a
    st = os.stat(path)
    key = hashlib.sha256(('%s|%d|%d|%s' % (path, st.st_size, int(st.st_mtime), b)).encode()).hexdigest()[:16]
    cdir = os.path.join(G, 'regress_cache')
    cf = os.path.join(cdir, key + '.json')
    if os.path.exists(cf):
        return path, b, json.load(open(cf, encoding='utf-8'))
    r = scan(path)
    e = evaluate(r, b)
    os.makedirs(cdir, exist_ok=True)
    with open(cf + '.tmp', 'w', encoding='ascii', newline=chr(10)) as f:
        json.dump(e, f, ensure_ascii=True)
    os.replace(cf + '.tmp', cf)
    return path, b, e


def main(argv):
    if '--check-seal' in argv:
        seal = argv[argv.index('--seal') + 1] if '--seal' in argv else 'C:/kyty/KytyPS5/docs/track-f/f20e.md'
        ok = True
        n = 0
        for l in open(seal, encoding='utf-8'):
            m = re.match(r'^seal: ([0-9a-f]{64}) (\S+)', l.strip().strip('`'))
            if m:
                n += 1
                got = sha_file(m.group(2))
                good = got == m.group(1)
                ok &= good
                print('%s %s %s' % ('ok' if good else 'MISMATCH', m.group(2), (got or 'missing')[:16]))
        print('SEAL %s (%d lines)' % ('PASS' if ok and n else 'FAIL', n))
        return 0 if ok and n else 1
    if '--regress' in argv:
        import multiprocessing
        with multiprocessing.Pool(len(REGRESS)) as pool:
            res = pool.map(regress_one, REGRESS)
        out = []
        tot = dict(warm=0, holds=0, b2=0, unattr=0, unattr_f20a=0, entries=0)
        for path, b, e in res:
            tot['entries'] += 1 if e['entered'] else 0
            tot['warm'] += 1 if e['warm'] else 0
            tot['b2'] += len(e['b2_frames'])
            tot['holds'] += 1 if e['hold'] else 0
            tot['unattr'] += e['unattr']
            tot['unattr_f20a'] += e['unattr_f20a']
            out.append('%s %s first_n %s frames %d scene %.1f s | window read %s dump %d warm %s max %d B2 %d | hold %s frames %d '
                       'unattr %d/%d %s' % (path.replace('C:/kyty/', ''), b, e['first_n'], e['frames'], e['scene_s'], e['window_read'],
                                            e['window_dump'], e['warm'], e['window_max_us'], len(e['b2_frames']), e['hold'],
                                            len(e['hold_frames']), e['unattr'], e['unattr_f20a'],
                                            [(x['n'], x['dt_us'], x['letter']) for x in e['hold_frames']]))
        ok = all(tot[k] == v for k, v in REGRESS_WANT.items())
        out.append('TOTAL entries %d; N warm %d; N holds %d; B2 frames %d; unattributed %d (variant F20a %d)' % (
            tot['entries'], tot['warm'], tot['holds'], tot['b2'], tot['unattr'], tot['unattr_f20a']))
        out.append('REGRESS %s (want N warm 6, N holds 8, B2 frames 0, unattributed 0)' % ('PASS' if ok else 'FAIL'))
        if '--out' in argv:
            with open(argv[argv.index('--out') + 1], 'w', encoding='ascii', errors='replace', newline='\n') as f:
                f.write('\n'.join(out) + '\n')
        for l in out:
            print(l)
        return 0 if ok else 1
    if '--series' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        results = []
        for t in sorted(os.listdir(rd)) if os.path.isdir(rd) else []:
            j = os.path.join(rd, t, 'read.json')
            if re.match(r'^f20_v\d\d$', t) and os.path.exists(j):
                results.append(json.load(open(j, encoding='utf-8')))
        s = series(results)
        for res in results:
            print('%s %s %s' % (res['tag'], 'ADMITTED' if res['admitted'] else 'INTERFERENCE', res['reading']))
        print('BASE B2 %s (F20a 6 + F20c 22, item 543 (g)); B32 - the F20e series alone (item 543 (e))' % BASE)
        print('SUM %s' % s['sum'])
        print('TAGS %s' % s['tags'])
        print('READING %s' % s['b2'])
        print('READING %s' % s['b32'])
        print('READING %s' % s['b32_f20a'])
        print('STOP (i) B2 warm N %d >= 30: %s; (ii) B32 F20e: holds %d, with unattributed %d (stop at >= 1 or %d clean): %s; tags made %d of %d'
              % (s['sum']['warm'], 'yes' if s['stop_i'] else 'no', s['sum']['holds'], s['sum']['unattr'], B32_HOLDS,
                 'yes' if s['stop_ii'] else 'no', s['tags']['made'], TAG_MAX))
        print('NEXT %s' % ('more tags (item 543 (e): (i) and (ii) not both met, tags made < 30)' if s['need_more'] else 'stop adding tags'))
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        p = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0]
        if not re.match(r'^f20_v\d\d$', tag):
            print('usage: f20e_read.py f20_vNN | --dir D --tag T | --regress | --series | --check-seal')
            return 2
        p = paths(tag)
    res = read_tag(tag, p)
    for l in rows(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
