"""f5c_read.py - F5c (HPP-357), track F: the reading of one F5c tag - ROADMAP "SESSION 122" p.273(e)(3)(a)-(g); window of
p.278(v); RC3 of F5b p.280(e)(1)-(3); stand reference p.280(v) and N2 / N1 of p.285(v); binary of p.285(v) (6f495a65).

The s142 reading is NOT copied and NOT changed: sc142.py is imported from C:/kyty/s142 after its sha256 is checked
(SC142_SHA; another sha -> rc 2, no reading); only scan / derive / markers / validation / read_glitch / last_value and the
constants K2_US / SCENE_DRAWS are called.  Everything F5c adds is in this file.

  python f5c_read.py --tag f5c_a|f5c_b|f5c_v|f5c_g [--root <dir>] [--json <out.json>]
  python f5c_read.py --stop-check <read.json>   (the series stop after one tag: 'continue ...' or 'stop ...')
  python f5c_read.py --check-seal <pred.md>     (rc 0 every 'seal:' line matches and every sealed name has one line)

Tags (p.273(e)(3); stand KYTY_TEST_MINIMIZE=60:10 in every tag; level -lvl underwater_aerial_garden):
  f5c_a  (a) W, KYTY_FIX_MINIMIZE=1, form W of p.273(k)(2): --vulkan-validation true + KYTY_PIPELINE_PRECACHE=0 +
         VK_LAYER_MESSAGE_ID_FILTER=<the F6 VUID>; letter: exactly one 'Window 1 minimized' line, 'SwapchainZeroExtent: begin'
         and 'SwapchainZeroExtent: end' lines, 0 [Vulkan][E], 0 death markers, hold >= 310 s, >= 1000 FrameTrace rows after
         'TestMinimize: restore', 'end' not later than 'restore' + 2 s (p.278(v)) -> PASS | FAIL
  f5c_b  (b) control KYTY_FIX_MINIMIZE=0, the same stand and form: a [Vulkan][E] line with VUID 01689 after
         'TestMinimize: minimize' and the emulator ended -> STOP VUID-01689 | NO STOP
  f5c_v  (v) V, =1, no validation, video: hold >= 330 s, video >= 3000 frames, 0 glitches outside the window, the present
         numbers of the .idx strictly increase after 'SwapchainZeroExtent: end' (p.280(e)(1), N1 p.285(v); a permutation or a
         repeat is a glitch), sheet for the lead, no K1/K2 outside the window, 'begin'/'end' lines and 'end' not later than
         'restore' + 2 s (p.278(v)) -> PASS | FAIL
  f5c_g  (g) V, =0, no validation, no video: the outcome is DATA (death markers, the last log line, the exit code) - p.273(e)(3)(g)
The window (p.278(v)): from the line 'TestMinimize: minimize' to the line 'SwapchainZeroExtent: end' + 2 s; no 'end' line -> the
  window runs to the end of the log and (a)/(v) are not met.  The clock of the log is the sum of FrameTrace dt_us (the clock
  of every hold and K2 of the programme); beside it the 'ms=' of the 'end' line is printed (variant of the executor); when the
  two readings of "end later than restore + 2 s" differ, the reader says so (question to the lead), the letter uses the log
  clock.
The window on the video: the log clock is put on the .idx clock by anchoring the ends (the method of
  docs/session-144/audit/vidcont144.py: the last FrameTrace row ends at the last record); beside it the variant 'idx gap'
  (the largest gap of the .idx, + 2 s after it) is printed; the letter uses the anchored log window.
Stand reference (p.280(v), N2 p.285(v)): the one 'TestMinimize: armed' line of the tag's own log; the start line before it must
  carry the non-blank level name; the shift armed - start (bytes, rows, s of dt) is printed as a control.
Not compared (p.280(e)(3)): frames_dropped of the 'end' line with the video.
Window events (p.280(e)(2)): 'Window 1 minimized' and 'Recovering Vulkan swapchain' are expected in F5c tags; they are counted
  and never stop the series by themselves.
Order of the verdict: NOT ADMITTED (run form) -> NOT EVALUABLE (controls of the stand and of the arm) -> the letter.
Output: ASCII only.  rc 0 - read (verdict in the text); rc 1 - no log / no json; rc 2 - usage or a sha mismatch.
"""
import bisect
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC142 = 'C:/kyty/s142/sc142.py'
SC142_SHA = '1ce612cdd036e2382ce5c5aae6bd25836062830dc0952da8512a9f2a74bb38c3'
ROOT = 'C:/kyty/f287/f5c'
SKY = 'underwater_aerial_garden'
CHUNK = 1 << 26
STAND = '60:10'
STAND_DELAY = 60.0
STAND_DUR = 10.0
VKFILTER = 'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering'
TAGS = {
    'f5c_a': dict(level=SKY, fix='1', arm='W', val=True, video=False, hold_s=310, letter='a'),
    'f5c_b': dict(level=SKY, fix='0', arm='W', val=True, video=False, hold_s=0, letter='b'),
    'f5c_v': dict(level=SKY, fix='1', arm='V', val=False, video=True, hold_s=330, letter='v'),
    'f5c_g': dict(level=SKY, fix='0', arm='V', val=False, video=False, hold_s=330, letter='g'),
}
FRAMES_V = 3000
ROWS_AFTER_RESTORE = 1000
LATE_S = 2.0
WIN_AFTER_END_S = 2.0
VUID = b'VUID-VkSwapchainCreateInfoKHR-imageExtent-01689'
M_GUEST = b'GuestOut'
M_CFG = b'TestMinimize: config '
RX_CFG = re.compile(rb'TestMinimize: config (\S+) delay_s=([0-9.]+) dur_s=([0-9.]+)')
M_ARMED = b'TestMinimize: armed'
M_MIN = b'TestMinimize: minimize'
M_RESTORE = b'TestMinimize: restore'
M_FIXON = b'FixMinimize: on'
M_BEGIN = b'SwapchainZeroExtent: begin'
M_END = b'SwapchainZeroExtent: end'
RX_END = re.compile(rb'SwapchainZeroExtent: end frames_dropped=(\d+) ms=(\d+)')
M_RECOVER = b'Recovering Vulkan swapchain'
M_EXHAUST = b'Vulkan presentation retry exhausted'
M_VKE = b'[Vulkan][E]'
M_LIMIT = b'last time reporting it'
RX_WIN = re.compile(rb'Window (\d+) (minimized|restored|resized to|size changed to|lost keyboard focus)')
M_WIN = b'Window '
VKE_MAX = 300
LAST_MAX = 200
# the F5c binary (p.285(v), F5a2 report, F5b2 PASS): its sha256 is a member of admission
BIN_SHA = '6f495a65388a90a0381c9170f224777e84cb07d657115ad2a8662fa0bae168dd'
NOT_SET = ('KYTY_FIX_DUALSRC', 'KYTY_FIX_B26', 'KYTY_S_PCW', 'KYTY_FIX_B1B', 'KYTY_PVAR', 'KYTY_GPU_CHECKPOINTS')
RX_GL = re.compile(r'^\s*video\s+(\d+)\s+present\s+(\d+)\s+t=\s*([0-9.]+)s')


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load(path, want, name):
    got = sha_file(path)
    if got != want:
        raise SystemExit('sha mismatch %s: %s != %s' % (path, got, want))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scan_f5c(path):
    """The F5c lines with byte positions: stand (config / armed / minimize / restore), FixMinimize: on, the zero-extent episode
    (begin / end with frames_dropped and ms), Recovering / retry exhausted, window events by kind, [Vulkan][E] lines (first
    text, positions of VUID 01689), layer limit lines, the last non-empty line."""
    res = dict(guest=None, cfg=[], armed=[], minimize=[], restore=[], fixon=[], begin=[], end=[], recover=[], exhaust=[],
               win={}, win1_min=[], vke1=None, vke1_text=None, vuid=[], limit=0, last=None)
    off = 0
    tail = b''
    last = b''
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            buf = tail + b
            if b:
                cut = buf.rfind(b'\n') + 1
                if cut == 0:
                    tail = buf
                    continue
                whole, tail = buf[:cut], buf[cut:]
            else:
                whole, tail = buf, b''
            if not whole:
                break
            base = off
            off += len(whole)
            ls = whole.rstrip(b'\r\n')
            if ls.strip():
                k = ls.rfind(b'\n')
                last = ls[k + 1:]
            if res['guest'] is None:
                i = whole.find(M_GUEST)
                if i >= 0:
                    res['guest'] = base + whole.rfind(b'\n', 0, i) + 1
            res['limit'] += whole.count(M_LIMIT)
            for marker in (M_CFG, M_ARMED, M_MIN, M_RESTORE, M_FIXON, M_BEGIN, M_END, M_RECOVER, M_EXHAUST, M_VKE, M_WIN):
                i = whole.find(marker)
                while i >= 0:
                    s = whole.rfind(b'\n', 0, i) + 1
                    e = whole.find(b'\n', i)
                    e = len(whole) if e < 0 else e
                    line = whole[s:e]
                    pos = base + s
                    if marker is M_CFG:
                        m = RX_CFG.search(line)
                        res['cfg'].append((pos, (m.group(1).decode('ascii', 'replace'), float(m.group(2)), float(m.group(3)))
                                           if m else None))
                    elif marker is M_ARMED:
                        res['armed'].append(pos)
                    elif marker is M_MIN:
                        res['minimize'].append(pos)
                    elif marker is M_RESTORE:
                        res['restore'].append(pos)
                    elif marker is M_FIXON:
                        res['fixon'].append(pos)
                    elif marker is M_BEGIN:
                        res['begin'].append(pos)
                    elif marker is M_END:
                        m = RX_END.search(line)
                        res['end'].append((pos, (int(m.group(1)), int(m.group(2))) if m else None))
                    elif marker is M_RECOVER:
                        res['recover'].append(pos)
                    elif marker is M_EXHAUST:
                        res['exhaust'].append(pos)
                    elif marker is M_VKE:
                        if res['vke1'] is None or pos < res['vke1']:
                            res['vke1'] = pos
                            res['vke1_text'] = line[:VKE_MAX].decode('ascii', 'replace')
                        if VUID in line:
                            res['vuid'].append(pos)
                    else:
                        m = RX_WIN.search(line)
                        if m:
                            kind = m.group(2).decode('ascii')
                            res['win'][kind] = res['win'].get(kind, 0) + 1
                            if kind == 'minimized' and m.group(1) == b'1':
                                res['win1_min'].append(pos)
                    i = whole.find(marker, e)
            if not b:
                break
    res['last'] = last[:LAST_MAX].decode('ascii', 'replace')
    return res


class Clock:
    """The log clock: the sum of FrameTrace dt_us of the rows that lie before a byte position (s)."""

    def __init__(self, rows):
        self.pos = [r[3] for r in rows]
        self.cum = []
        c = 0
        for r in rows:
            c += r[1]
            self.cum.append(c)
        self.rows = rows

    def at(self, pos):
        k = bisect.bisect_left(self.pos, pos)
        return (self.cum[k - 1] if k > 0 else 0) / 1e6

    def rows_between(self, a, b):
        return bisect.bisect_left(self.pos, b) - bisect.bisect_right(self.pos, a)

    def pos_after(self, pos, secs):
        """Byte position of the first row after pos whose end lies >= secs after pos (None - the log ends earlier)."""
        t0 = self.at(pos)
        k = bisect.bisect_right(self.pos, pos)
        while k < len(self.rows):
            if self.cum[k] / 1e6 - t0 >= secs:
                return self.pos[k]
            k += 1
        return None


def read_idx(path):
    """rec_<tag>.mp4.idx of the recorder: rows 'rec_frames present t' -> list of (int, int, float) or None."""
    if not os.path.isfile(path):
        return None
    out = []
    with open(path, 'rb') as f:
        for line in f.read().decode('ascii', 'replace').splitlines():
            x = line.split()
            if len(x) >= 3:
                try:
                    out.append((int(x[0]), int(x[1]), float(x[2])))
                except ValueError:
                    return None
    return out


def read_glitch_list(path):
    """The glitch lines of s51_vidglitch.py: [(video frame, present, t)]."""
    out = []
    if not os.path.isfile(path):
        return out
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            m = RX_GL.match(line)
            if m:
                out.append((int(m.group(1)), int(m.group(2)), float(m.group(3))))
    return out


def video_part(rows, idx, glist, mpos, epos, clock):
    """The video members of (v): the window on the .idx clock (anchored log window; variant idx gap), glitches outside it, the
    present order after 'end' (N1), the presented frames without a record after the first scene frame (data, vidcont144)."""
    v = dict(records=len(idx), rec_frames_consecutive=all(idx[i][0] == i for i in range(len(idx))))
    t_last = idx[-1][2] if idx else 0.0
    total = clock.cum[-1] / 1e6 if clock.cum else 0.0
    off = t_last - total          # idx time = log clock + off (ends anchored)
    w0 = clock.at(mpos) + off if mpos is not None else None
    w1 = (clock.at(epos) + off + WIN_AFTER_END_S) if epos is not None else None
    v['win_anchored'] = (w0, w1)
    gi = None
    for i in range(len(idx) - 1):
        g = idx[i + 1][2] - idx[i][2]
        if gi is None or g > idx[gi + 1][2] - idx[gi][2]:
            gi = i
    v['win_gap'] = (idx[gi][2], idx[gi + 1][2] + WIN_AFTER_END_S, idx[gi + 1][2] - idx[gi][2]) if gi is not None else None

    def outside(win, t):
        if win is None or win[0] is None:
            return True
        hi = win[1] if win[1] is not None else float('inf')
        return not (win[0] <= t <= hi)
    v['glitches_all'] = len(glist)
    v['glitches_out_anchored'] = [g for g in glist if outside(v['win_anchored'], g[2])]
    v['glitches_out_gap'] = [g for g in glist if outside(v['win_gap'], g[2])]
    # N1 / p.280(e)(1): present numbers strictly increase after 'end' (records at or after the anchored end time)
    t_end = (clock.at(epos) + off) if epos is not None else None
    after = [r for r in idx if t_end is not None and r[2] >= t_end]
    v['after_end_records'] = len(after)
    v['after_end_bad'] = [(a[0], a[1], b[1]) for a, b in zip(after, after[1:]) if b[1] <= a[1]]
    v['all_bad'] = [(a[0], a[1], b[1]) for a, b in zip(idx, idx[1:]) if b[1] <= a[1]]
    # vidcont144 method (data): rows ending inside an idx gap > 60 ms, outside the window
    ends = []
    c = 0.0
    for r in reversed(rows):
        ends.append(t_last - c)
        c += r[1] / 1e6
    ends.reverse()
    it = [r[2] for r in idx]
    miss = 0
    runmax = 0
    for i in range(len(it) - 1):
        if it[i + 1] - it[i] > 0.060:
            lo = bisect.bisect_right(ends, it[i] + 0.012)
            hi = bisect.bisect_left(ends, it[i + 1] - 0.012)
            n = sum(1 for k in range(lo, hi) if outside(v['win_anchored'], ends[k]))
            miss += n
            runmax = max(runmax, n)
    v['rows_without_record_outside'] = miss
    v['longest_run_outside'] = runmax
    return v


def read_tag(tag, root=ROOT, sc142=None):
    cfg = TAGS[tag]
    sc142 = sc142 or load(SC142, SC142_SHA, 'sc142')
    lp = os.path.join(root, 'log_%s.txt' % tag)
    sp = os.path.join(root, 'stdout_%s.txt' % tag)
    jp = os.path.join(root, '%s.json' % tag)
    if not os.path.isfile(lp) or not os.path.isfile(jp):
        return None
    with open(jp, encoding='utf-8') as f:
        js = json.load(f)
    at = (js.get('attempts') or [{}])[0]
    env = js.get('env') or {}
    log = sc142.scan(lp)
    std = sc142.scan(sp) if os.path.isfile(sp) else None
    d = sc142.derive(log, cfg['level'])
    marks = sc142.markers(log, std, d['entry_pos'], log['quit'])
    val = sc142.validation(log, std)
    x = scan_f5c(lp)
    xs = scan_f5c(sp) if os.path.isfile(sp) else None
    clock = Clock(log['rows'])
    r = dict(tag=tag, cfg=cfg, log_sha=log['sha256'], binary=js.get('binary_sha256'))
    adm = []

    def add(name, ok, detail=''):
        adm.append((name, bool(ok), str(detail)))
    add('one attempt', len(js.get('attempts') or []) == 1, len(js.get('attempts') or []))
    add('binary sha256 = F5c binary 6f495a65 (p.285(v))', js.get('binary_sha256') == BIN_SHA, (js.get('binary_sha256') or '')[:16])
    add('guest args -lvl %s' % cfg['level'], js.get('guest_args') == '-lvl %s' % cfg['level'], js.get('guest_args'))
    add('KYTY_FIX_MINIMIZE=%s exactly' % cfg['fix'], env.get('KYTY_FIX_MINIMIZE') == cfg['fix'], repr(env.get('KYTY_FIX_MINIMIZE')))
    add('KYTY_TEST_MINIMIZE=%s exactly' % STAND, env.get('KYTY_TEST_MINIMIZE') == STAND, repr(env.get('KYTY_TEST_MINIMIZE')))
    for k in NOT_SET:
        add('%s not set' % k, k not in env, repr(env.get(k)))
    add('KYTY_GPU_CLOCK_PIN=1', env.get('KYTY_GPU_CLOCK_PIN') == '1', env.get('KYTY_GPU_CLOCK_PIN'))
    if cfg['arm'] == 'W':
        add('KYTY_PIPELINE_PRECACHE=0 (form W p.273(k)(2))', env.get('KYTY_PIPELINE_PRECACHE') == '0',
            repr(env.get('KYTY_PIPELINE_PRECACHE')))
        add('VK_LAYER_MESSAGE_ID_FILTER = the F6 VUID exactly', env.get('VK_LAYER_MESSAGE_ID_FILTER') == VKFILTER,
            repr(env.get('VK_LAYER_MESSAGE_ID_FILTER')))
    else:
        add('KYTY_PIPELINE_PRECACHE not set (V: shipped defaults)', 'KYTY_PIPELINE_PRECACHE' not in env,
            repr(env.get('KYTY_PIPELINE_PRECACHE')))
        add('no VK_LAYER_MESSAGE_ID_FILTER (V)', 'VK_LAYER_MESSAGE_ID_FILTER' not in env, repr(env.get('VK_LAYER_MESSAGE_ID_FILTER')))
    rec = env.get('KYTY_REC')
    if cfg['video']:
        add('video KYTY_REC rec_%s.mp4' % tag, rec is not None and rec.replace('\\', '/').endswith('/rec_%s.mp4' % tag), rec)
    else:
        add('no video', rec is None, rec)
    vv = sc142.last_value(js.get('cmdline') or [], '--vulkan-validation')
    add('--vulkan-validation %s' % ('true' if cfg['val'] else 'false'), vv == ('true' if cfg['val'] else 'false'), vv)
    if cfg['val']:
        add('validation active (p.224: 0 no-layer, >= 1 validation_features, >= 1 [Vulkan][)', val['ok'],
            '%d/%d/%d' % (val['noval'], val['valfeat'], val['vkany']))
    r['admit'] = adm
    r['admitted'] = all(ok for _, ok, _ in adm)
    # controls of the stand and of the arm: a failure -> NOT EVALUABLE
    con = []

    def kadd(name, ok, detail=''):
        con.append((name, bool(ok), str(detail)))
    ctl = []

    def cadd(name, ok, detail=''):
        ctl.append((name, bool(ok), str(detail)))
    cfgs = [c for _, c in x['cfg']]
    kadd('exactly one line TestMinimize: config on delay_s=60.000 dur_s=10.000',
         len(cfgs) == 1 and cfgs[0] is not None and cfgs[0][0] == 'on' and abs(cfgs[0][1] - STAND_DELAY) < 1e-6
         and abs(cfgs[0][2] - STAND_DUR) < 1e-6, cfgs)
    kadd('exactly one line TestMinimize: armed', len(x['armed']) == 1, len(x['armed']))
    ap = x['armed'][0] if len(x['armed']) == 1 else None
    starts_before = [(n, p) for n, p in log['starts'] if ap is not None and p < ap]
    st = starts_before[-1] if starts_before else None
    empty_before = sum(1 for n, _ in starts_before if not n.strip())
    kadd('N2 p.285(v): the start line before armed carries the level name %s (not blank)' % cfg['level'],
         st is not None and st[0] == cfg['level'], (st, 'blank start lines before armed %d' % empty_before))
    r['shift'] = None
    if st is not None and ap is not None:
        r['shift'] = dict(start_pos=st[1], armed_pos=ap, bytes=ap - st[1], rows=clock.rows_between(st[1], ap),
                          dt_s=round(clock.at(ap) - clock.at(st[1]), 3), blank_before=empty_before)
    kadd('exactly one line TestMinimize: minimize, after armed', len(x['minimize']) == 1 and ap is not None and x['minimize'][0] > ap,
         (len(x['minimize']), x['minimize'][:1], ap))
    mpos = x['minimize'][0] if len(x['minimize']) == 1 else None
    if cfg['letter'] in ('a', 'v'):
        kadd('exactly one line TestMinimize: restore, after minimize', len(x['restore']) == 1 and mpos is not None
             and x['restore'][0] > mpos, (len(x['restore']), x['restore'][:1]))
    else:
        cadd('restore lines (b, g: data; the process may end inside the episode)', True, len(x['restore']))
    rpos = x['restore'][0] if len(x['restore']) == 1 else None
    want_fix = 1 if cfg['fix'] == '1' else 0
    kadd('FixMinimize: on lines = %d (arm %s)' % (want_fix, cfg['fix']), len(x['fixon']) == want_fix, len(x['fixon']))
    kadd('>= 1 line Window 1 minimized (the stand reached the window)', len(x['win1_min']) >= 1, len(x['win1_min']))
    r['entered'] = d['entered']
    r['first'] = d['first']
    # the first scene frame row position (derive gives n; find its row)
    first_pos = None
    if d['first'] is not None:
        for row in log['rows']:
            if row[0] == d['first'][0] and d['entry_pos'] is not None and row[3] > d['entry_pos']:
                first_pos = row[3]
                break
    r['first_pos'] = first_pos
    kadd('the first scene frame lies before TestMinimize: minimize', first_pos is not None and mpos is not None and first_pos < mpos,
         (first_pos, mpos))
    if cfg['fix'] == '0':
        kadd('no SwapchainZeroExtent line at =0', not x['begin'] and not x['end'], (len(x['begin']), len(x['end'])))
    r['controls'] = con
    r['controls_ok'] = all(ok for _, ok, _ in con)
    # the episode and its timings on the log clock
    ends = [(p, v) for p, v in x['end']]
    bpos = x['begin'][0] if x['begin'] else None
    epos = None
    eval_ = None
    for p, v in ends:
        if bpos is not None and p > bpos:
            epos, eval_ = p, v
            break
    r['episode'] = dict(begin=len(x['begin']), end=len(x['end']), begin_pos=bpos, end_pos=epos, end_val=eval_)
    r['t'] = dict(armed=clock.at(ap) if ap is not None else None, minimize=clock.at(mpos) if mpos is not None else None,
                  restore=clock.at(rpos) if rpos is not None else None, begin=clock.at(bpos) if bpos is not None else None,
                  end=clock.at(epos) if epos is not None else None, total=clock.cum[-1] / 1e6 if clock.cum else 0.0)
    tt = r['t']
    r['delay_s'] = (tt['minimize'] - tt['armed']) if tt['minimize'] is not None and tt['armed'] is not None else None
    r['dur_s'] = (tt['restore'] - tt['minimize']) if tt['restore'] is not None and tt['minimize'] is not None else None
    late_log = None
    late_ms = None
    if epos is not None and rpos is not None:
        late_log = (tt['end'] - tt['restore']) > LATE_S
    if eval_ is not None and tt['minimize'] is not None and tt['begin'] is not None:
        late_ms = (tt['begin'] - tt['minimize']) * 1000.0 + eval_[1] > (STAND_DUR + LATE_S) * 1000.0
    r['late_log'] = late_log
    r['late_ms'] = late_ms
    r['late_disagree'] = late_log is not None and late_ms is not None and late_log != late_ms
    r['rows_after_restore'] = clock.rows_between(rpos, 1 << 62) if rpos is not None else 0
    # the log window of p.278(v): minimize .. end + 2 s
    wend = clock.pos_after(epos, WIN_AFTER_END_S) if epos is not None else None
    wend = wend if wend is not None else (1 << 62)

    def inwin(pos):
        return mpos is not None and mpos <= pos <= wend
    r['scene_change'] = d['change_pos'] is not None
    r['marks'] = [(m['kind'], m['cls'], m['src'], m['at_exit'], m['pos']) for m in marks]
    r['deaths'] = len(marks)
    r['deaths_out'] = [m for m in r['marks'] if not (m[2] == 'log' and inwin(m[4]))]
    r['vke'] = len(log['vke']) + (len(std['vke']) if std else 0)
    r['vke_first'] = [t for t in (x['vke1_text'], xs['vke1_text'] if xs else None) if t][:1]
    r['vuid'] = len(x['vuid']) + (len(xs['vuid']) if xs else 0)
    r['vuid_after_min'] = bool(x['vuid']) and mpos is not None and x['vuid'][0] > mpos
    r['vuid_in_stdout'] = bool(xs and xs['vuid'])
    r['limit'] = x['limit'] + (xs['limit'] if xs else 0)
    r['win'] = x['win']
    r['win1_min'] = len(x['win1_min'])
    r['recover'] = len(x['recover'])
    r['exhaust'] = len(x['exhaust'])
    r['last_log'] = x['last']
    r['last_stdout'] = xs['last'] if xs else None
    r['dt_after_first_s'] = d['dt_after_first_us'] / 1e6
    r['hold_s_json'] = at.get('hold_s')
    r['hold_exit'] = at.get('hold_exit')
    r['outcome'] = at.get('outcome')
    r['detail'] = at.get('detail')
    r['val'] = val
    # K2 after the first scene frame, by position against the window
    k2 = []
    if first_pos is not None:
        for row in log['rows']:
            if row[3] > first_pos and (d['change_pos'] is None or row[3] < d['change_pos']) and row[1] >= sc142.K2_US:
                k2.append((row[0], row[1], row[3], inwin(row[3])))
    r['k2'] = [(n, dt, 'window' if w else 'outside') for n, dt, _, w in k2]
    r['k2_out'] = sum(1 for _, _, _, w in k2 if not w)
    r['skip_lines'] = log['skip_lines']
    r['video'] = None
    r['sheet'] = os.path.isfile(os.path.join(root, 'sheet_%s.png' % tag)) and os.path.getsize(os.path.join(root, 'sheet_%s.png' % tag)) > 0
    g = sc142.read_glitch(os.path.join(root, 'glitch_%s.txt' % tag))
    r['glitch'] = g
    if cfg['video']:
        idx = read_idx(os.path.join(root, 'rec_%s.mp4.idx' % tag))
        if idx:
            r['video'] = video_part(log['rows'], idx, read_glitch_list(os.path.join(root, 'glitch_%s.txt' % tag)), mpos, epos, clock)
            r['video']['win_disagree'] = len(r['video']['glitches_out_anchored']) != len(r['video']['glitches_out_gap'])
    r['not_evaluable_why'] = None
    hold_v = r['dt_after_first_s'] >= cfg['hold_s']
    r['hold_letter'] = hold_v
    L = cfg['letter']
    if L == 'a':
        parts = dict(entered=d['entered'], no_scene_change=not r['scene_change'], no_hold_exit=r['hold_exit'] is None,
                     one_window1_minimized=r['win1_min'] == 1, begin_end=bpos is not None and epos is not None,
                     vke0=r['vke'] == 0, deaths0=r['deaths'] == 0, hold=hold_v,
                     rows_after_restore=r['rows_after_restore'] >= ROWS_AFTER_RESTORE, end_not_late=late_log is False)
        r['parts'] = parts
        r['verdict_letter'] = 'PASS' if all(parts.values()) else 'FAIL'
        cadd('exactly one begin and one end line (executor)', len(x['begin']) == 1 and len(x['end']) == 1,
             (len(x['begin']), len(x['end'])))
    elif L == 'b':
        ended = r['hold_exit'] is not None or r['outcome'] == 'exited'
        parts = dict(vuid_01689_after_minimize=r['vuid_after_min'], emulator_ended=ended)
        r['parts'] = parts
        r['verdict_letter'] = 'STOP VUID-01689' if all(parts.values()) else 'NO STOP'
    elif L == 'v':
        vd = r['video']
        parts = dict(entered=d['entered'], no_scene_change=not r['scene_change'], no_hold_exit=r['hold_exit'] is None,
                     hold=hold_v, video_frames=g is not None and g['video_frames'] >= FRAMES_V, sheet=r['sheet'],
                     glitches_outside0=vd is not None and not vd['glitches_out_anchored'],
                     n1_present_order_after_end=vd is not None and epos is not None and vd['after_end_records'] > 0
                     and not vd['after_end_bad'],
                     no_k1k2_outside=not r['deaths_out'] and r['k2_out'] == 0,
                     begin_end=bpos is not None and epos is not None, end_not_late=late_log is False)
        r['parts'] = parts
        r['verdict_letter'] = 'PASS' if all(parts.values()) else 'FAIL'
    else:
        r['parts'] = {}
        r['verdict_letter'] = 'DATA'
    if not r['admitted']:
        r['verdict_letter'] = 'NOT ADMITTED'
    elif not r['controls_ok']:
        r['verdict_letter'] = 'NOT EVALUABLE'
        r['not_evaluable_why'] = 'controls failed: %s' % [n for n, ok, _ in con if not ok]
    r['exec_members'] = ctl
    r['exec_ok'] = all(ok for _, ok, _ in ctl)
    return r


def text(r):
    L = ['f5c_read tag %s level %s arm %s KYTY_FIX_MINIMIZE=%s stand %s log sha256 %s binary %s' % (
        r['tag'], r['cfg']['level'], r['cfg']['arm'], r['cfg']['fix'], STAND, r['log_sha'], (r['binary'] or '')[:16])]
    for name, ok, det in r['admit']:
        L.append('admit %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    for name, ok, det in r['controls']:
        L.append('control %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    for name, ok, det in r['exec_members']:
        L.append('executor member [I] %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    s = r['shift']
    L.append('stand shift (N2 p.285(v), control): %s' % (
        'start line byte %d -> armed byte %d: %d bytes, %d FrameTrace rows, %.3f s of dt; blank start lines before %d' % (
            s['start_pos'], s['armed_pos'], s['bytes'], s['rows'], s['dt_s'], s['blank_before']) if s else 'none'))
    t = r['t']

    def f(v):
        return 'none' if v is None else '%.3f' % v
    L.append('log clock (s of dt): armed %s minimize %s restore %s begin %s end %s total %s; armed->minimize %s (stand 60), '
             'minimize->restore %s (stand 10)' % (f(t['armed']), f(t['minimize']), f(t['restore']), f(t['begin']), f(t['end']),
                                                f(t['total']), f(r['delay_s']), f(r['dur_s'])))
    e = r['episode']
    L.append('episode: begin lines %d end lines %d; end frames_dropped/ms %s (frames_dropped is not compared with the video, '
             'p.280(e)(3))' % (e['begin'], e['end'], e['end_val']))
    L.append('end later than restore + 2 s (p.278(v)): log clock %s; variant of the executor by ms= %s%s' % (
        r['late_log'], r['late_ms'], ' - THE TWO READINGS DIFFER, question to the lead' if r['late_disagree'] else ''))
    L.append('FrameTrace rows after TestMinimize: restore %d (>= %d for (a))' % (r['rows_after_restore'], ROWS_AFTER_RESTORE))
    L.append('window events (p.280(e)(2), expected, not a stop): %s; Window 1 minimized %d; Recovering Vulkan swapchain %d; '
             'retry exhausted %d' % (sorted(r['win'].items()), r['win1_min'], r['recover'], r['exhaust']))
    L.append('entered %s first scene frame %s (byte %s) scene change %s enter_scene outcome %s detail %s' % (
        r['entered'], r['first'], r['first_pos'], r['scene_change'], r['outcome'], r['detail']))
    L.append('hold: sum dt after first %.1f s (>= %d); json hold_s %s (reference), hold_exit (exit code) %s' % (
        r['dt_after_first_s'], r['cfg']['hold_s'], r['hold_s_json'], r['hold_exit']))
    L.append('death markers %d %s; outside the window %d' % (r['deaths'], r['marks'][:4], len(r['deaths_out'])))
    L.append('K2 after the first scene frame %d %s; outside the window %d' % (len(r['k2']), r['k2'][:5], r['k2_out']))
    L.append('validation noval/valfeat/vkany %d/%d/%d active %s; [Vulkan][E] %d; VUID 01689 lines %d (first after minimize %s, '
             'stdout %s); layer limit lines %d' % (r['val']['noval'], r['val']['valfeat'], r['val']['vkany'], r['val']['ok'], r['vke'],
                                                 r['vuid'], r['vuid_after_min'], r['vuid_in_stdout'], r['limit']))
    L.append('first [Vulkan][E] line (<= %d chars): %s' % (VKE_MAX, [v.encode('ascii', 'replace').decode()
                                                                     for v in r['vke_first'][:1]]))
    L.append('last log line: %s' % r['last_log'])
    L.append('last stdout line: %s' % r['last_stdout'])
    L.append('AsyncPipelines skipped draw lines %d (data)' % r['skip_lines'])
    g = r['glitch']
    L.append('video: frames %s glitches (all) %s sheet %s' % (g['video_frames'] if g else None, g['glitches'] if g else None,
                                                             r['sheet']))
    v = r['video']
    if v:
        L.append('video window (p.278(v)) anchored log window on the idx clock %s; variant idx gap %s' % (
            v['win_anchored'], v['win_gap']))
        L.append('glitches outside the window: anchored %d %s; variant idx gap %d%s' % (
            len(v['glitches_out_anchored']), v['glitches_out_anchored'][:4], len(v['glitches_out_gap']),
            ' - THE TWO READINGS DIFFER, question to the lead' if v['win_disagree'] else ''))
        L.append('N1 (p.280(e)(1), p.285(v)): records after end %d, present order breaks after end %d %s; whole file breaks %d; '
                 'rec_frames consecutive %s; records %d' % (v['after_end_records'], len(v['after_end_bad']), v['after_end_bad'][:4],
                                                            len(v['all_bad']), v['rec_frames_consecutive'], v['records']))
        L.append('continuity (vidcont144 method, data, not a gate): presented frames without a record outside the window %d, '
                 'longest run %d' % (v['rows_without_record_outside'], v['longest_run_outside']))
    if r.get('parts'):
        L.append('letter members: %s' % ', '.join('%s=%s' % (k, v) for k, v in r['parts'].items()))
    if r.get('not_evaluable_why'):
        L.append('NOT EVALUABLE because: %s' % r['not_evaluable_why'])
    L.append('F5C VERDICT %s letter (%s): %s' % (r['tag'], r['cfg']['letter'], r['verdict_letter']))
    L.append('F5C EXECUTOR MEMBERS %s [I] (not the verdict): %s' % (
        r['tag'], 'all ok' if r['exec_ok'] else 'FAILED %s - question to the lead' % [n for n, ok, _ in r['exec_members'] if not ok]))
    return '\n'.join(L)


SEALED = ('go_f5c.sh', 'f5c_read.py', 'test_f5c_read.py', 'win_f5c.py', 'shalist_f2c.py', 'enter_scene.py', 'launch_run.py',
          'run_safety99.py', 'idle142.py', 'procload.py', 'sheet142.py', 'cachemf143.py', 'fgcpu143.py', 'gates_default.txt',
          SC142, 'C:/kyty/scripts/s51_vidglitch.py')
RX_SEAL = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)$')


def check_seal(pred, root=ROOT, names=SEALED):
    """Every 'seal: <sha256> <path>' line of the seal must match the file now (a path without 'C:/' is under root), and every
    name of SEALED must have exactly one line.  Returns (ok, lines)."""
    if not os.path.isfile(pred):
        return False, ['no seal %s' % pred]
    got = {}
    out = []
    ok = True
    with open(pred, encoding='utf-8') as f:
        for line in f:
            m = RX_SEAL.match(line.rstrip('\r\n'))
            if not m:
                continue
            name = m.group(2)
            path = name if name.startswith('C:/') else os.path.join(root, name)
            now = sha_file(path) if os.path.isfile(path) else None
            good = now == m.group(1)
            got[name] = got.get(name, 0) + 1
            ok &= good
            out.append('seal %s %s %s' % ('ok' if good else 'MISMATCH', name, (now or 'missing')[:16]))
    for n in names:
        if got.get(n, 0) != 1:
            ok = False
            out.append('seal line count %s = %d (want 1)' % (n, got.get(n, 0)))
    return ok, out


def stop_check(r):
    """The series stop of go_f5c.sh after one tag: returns 'continue ...' or 'stop ...'."""
    if r is None:
        return 'stop: no reading (no log or no json)'
    if r.get('verdict_letter') == 'NOT ADMITTED':
        return 'stop: tag not admitted'
    if r.get('verdict_letter') == 'NOT EVALUABLE':
        return 'stop: %s NOT EVALUABLE (%s) - question to the lead' % (r.get('tag'), r.get('not_evaluable_why'))
    if r.get('tag') in ('f5c_b', 'f5c_g'):
        return 'continue: (%s) %s is data' % (r['cfg']['letter'], r.get('verdict_letter'))
    if r.get('deaths', 0) > 0 and r.get('vke', 0) == 0:
        return 'stop: death marker without a [Vulkan][E] line (%s) - question to the lead' % (r.get('marks') or [])[:1]
    return 'continue: (%s) %s' % (r['cfg']['letter'], r.get('verdict_letter'))


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    root = a[a.index('--root') + 1] if '--root' in a and a.index('--root') + 1 < len(a) else ROOT
    if '--stop-check' in a and a.index('--stop-check') + 1 < len(a):
        p = a[a.index('--stop-check') + 1]
        r = None
        if os.path.isfile(p):
            with open(p, encoding='ascii') as f:
                r = json.load(f)
        print(stop_check(r))
        return 0
    if '--check-seal' in a and a.index('--check-seal') + 1 < len(a):
        ok, lines = check_seal(a[a.index('--check-seal') + 1], root)
        print('\n'.join(lines))
        print('check-seal %s' % ('OK' if ok else 'FAILED'))
        return 0 if ok else 1
    if '--tag' not in a or a.index('--tag') + 1 >= len(a) or a[a.index('--tag') + 1] not in TAGS:
        print('usage: f5c_read.py --tag %s [--root <dir>] [--json <out>]' % '|'.join(sorted(TAGS)))
        return 2
    tag = a[a.index('--tag') + 1]
    try:
        r = read_tag(tag, root)
    except SystemExit as e:
        print('refused: %s' % e)
        return 2
    if r is None:
        print('no log_%s.txt or %s.json in %s' % (tag, tag, root))
        return 1
    print(text(r))
    if '--json' in a:
        with open(a[a.index('--json') + 1], 'w', encoding='ascii') as f:
            json.dump(r, f, indent=1, default=str)
    return 0


if __name__ == '__main__':
    sys.exit(main())
