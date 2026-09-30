#!/usr/bin/env python3
"""sc142.py - the scorer of the scene census sc142 and of the SCENE_OK attempt on Sky Garden (session 142, HPP-277; link 1b
HPP-282: the RC1-RC10 fixes of the review review142.md by ROADMAP "SESSION 122" item 224; items 221 (v), (g)(1)-(5), 223 (a),
215 (v)(2), 217 (b), 218 (g)-(d); brief docs/next-session-142.md).

Reading of one entry (item 221 (g)(2), item 223 (a), item 224 (a)):
  entry            - the line "GuestOut: Level has started: <level>" of the target level (exact name, first such line).
  scene change     - any later "GuestOut: Level has started:" line (another level, the same level again, an empty name)
                     (item 224 (a)(7)): the rows after it are printed apart and not classified for the scene of -lvl.
  first scene frame- the first FrameTrace row after the entry line with draws >= 100 (item 218 (g)).  Its dt is the tail
                     of the load: it is NOT in K2, NOT in K3 and NOT in the entry window (item 221 (v)).
  entry window     - the 599 presented frames (FrameTrace rows) after the first scene frame (item 221 (v));
  hold             - every later row (before a scene change).
  K2               - a row after the first scene frame with dt_us >= 1 000 000 (item 217 (b)); also a hang marker
                     (GpuHangAbort:, ErrorDeviceLost) and a hold whose last 5 s had no FrameTrace row (ft_tail = 0 of
                     <tag>.json, item 223 (a)(2)).
  K3               - a row with 100 000 <= dt_us < 1 000 000 after the first scene frame: in the entry window with the
                     note "no warm base" (a never-entered level has no warm log, item 218 (g)), and on the hold.
  death markers    - item 128 (g) / 89 (g): GpuHangAbort:, ErrorDeviceLost (class K2), Unhandled exception:, and item
                     218 (d)(2): "--- Fatal Error ---", "--- Error ---" (class K1) - in the emulator log and in its stdout;
                     the attempt markers hold_exit / the ENDED line / exited (class K1).
  ORDER (item 224 (a)(1)): the log markers by their position in the log, then the markers of the emulator stdout by their
                     position there, then the attempt markers.  The outcome class is the class of the FIRST marker in
                     that order (a hang before a crash is K2: the crash is its consequence); the stop key is its kind.
  outcome (census) - NOT_ENTERED (no entry line) / K1 or K2 (the first death marker; else hold_exit, ENDED, exited -> K1;
                     else a frame dt >= 1 s or the tail stall -> K2) / HOLDS_120 (entered, attempt ok, hold_s >= 120,
                     sum dt_us of the rows after the entry line >= 120 s, item 224 (a)(4)) / NOT_EVALUABLE with a reason
                     (no first scene frame; no stable (<attempt outcome>); hold_s < 120; presented < 120 s; scene change).
                     With a scene change only the log markers and K2 frames BEFORE it decide; otherwise NOT_EVALUABLE.
  per-entry prints - "AsyncPipelines: skipped draw" lines and frames (counted, NOT fatal here: form B5 under measurement);
                     "opcode is not implemented" by family/opcode minus the base profile 96/1/4 (B26, B7);
                     "=== Stubbed function" with the name (B9); PriorityStall: us > 50 000 (B3b); BvhLoopCapTrip: (B1b);
                     one-frame glitches of s51_vidglitch.py 4 6 (glitch_<tag>.txt), video frames, .idx records, FrameTrace
                     rows in all and after the first scene frame, the coverage "video frames >= FrameTrace rows - 100"
                     (item 224 (a)(3); census: a failed coverage prints "glitches not conclusive"), torn FrameTrace
                     lines, the validation-layer lines, the emulator stdout present or not (item 224 (a)(8)).
SCENE_OK of Sky Garden (item 221 (g)(3), item 224 (a)): V = v142 (video), W = w142 (--vulkan-validation true).  YES only if
  every machine row holds, the sheet file sheet_v142.png exists, is not empty and both its sha256 and the sha256 of
  rec_v142.mp4 equal the lines of step2/times.txt, AND the lead's sheet row says viewed; every machine row true and the
  sheet row unfilled -> PENDING_SHEET; anything else -> NO.
Where the rule leaves an edge open the scorer prints both readings: the letter (every row / every marker of the log) and
the variant "vx" of the executor (rows and markers before the first "Event: quit" line and without the last row of the
log); verdicts use the letter.
Output is ASCII only (item 175 (v)).  Logs are read in binary, streaming, in chunks - never whole.
    python sc142.py --tag <tag> [--sheet viewed|not-viewed]     score one run (json in runs142/<tag>.score.json)
    python sc142.py --summary [--sheet viewed|not-viewed]       every made tag, SCENE_OK, census table, k/10 rows
    python sc142.py --stop-check <tag>                          rc 5 when the stop rule of item 221 (g)(4) stands
    python sc142.py --check-seal                                every sha line of the seal against its file
    python sc142.py --calib                                     the calibration on the s122 logs (item 221 (g)(4))
    python sc142.py --check1b                                   s1s128, s2s128 -> K2; s6s137 validation active (item 224 (b)(2))
"""
import argparse
import hashlib
import json
import os
import re
import sys

ROOT = 'C:/kyty/s142'
PRED_PATH = 'C:/kyty/s142/pred/02_sc142.md'
BUILD_SHA = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
SKY = 'underwater_aerial_garden'
V_TAG = 'v142'
W_TAG = 'w142'
CENSUS = (('c142_01', 'bumper_enemy_snowy_canyon'), ('c142_02', 'big_hand_pirate_island'), ('c142_03', 'timestop_casino'),
          ('c142_04', 'mini_giants_garden'), ('c142_05', 'ice_iceberg'), ('c142_06', 'sponge_dirty_bath'),
          ('c142_07', 'hoover_beach'), ('c142_08', 'volcano_mountain'), ('c142_09', 'voxel_world'),
          ('c142_10', 'enemy_gorilla'))
SEQ = (V_TAG, W_TAG) + tuple(t for t, _ in CENSUS)
SCENE_DRAWS = 100
ENTRY_WIN = 599
K2_US = 1000000
K3_US = 100000
HOLD_CENSUS_US = 120000000
HOLD_CENSUS_S = 120
HOLD_SCENE_US = 300000000
HOLD_W_S = 300
HOLD_V_S = 330
FRAMES_V = 3000
COVER_SLACK = 100
PRIO_US = 50000
STOP_RUN = 3
HALF = 5
OPCODE_BASE = {('SOP1', '0x21'): 96, ('SOP1', '0x0c'): 1, ('VOPC', '0xe3'): 4}
CRASH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---')
HANG = (b'GpuHangAbort:', b'ErrorDeviceLost')
M_START = b'GuestOut: Level has started: '
M_FT = b'FrameTrace: n='
M_SKIP = b'AsyncPipelines: skipped draw'
M_OPC = b'opcode is not implemented'
M_STUB = b'=== Stubbed function'
M_PRIO = b'PriorityStall:'
M_BVH = b'BvhLoopCapTrip:'
M_VKE = b'[Vulkan][E]'
M_VKANY = b'[Vulkan]['
M_NOVAL = b'no validation layer:'
M_VALFEAT = b'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features'
M_QUIT = b'Event: quit'
M_ENDED = b'WARNING: the game ENDED inside the hold'
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_OP = re.compile(rb'family=(\w+) opcode=(0x[0-9a-fA-F]+)')
RX_PRIO = re.compile(rb' us=(\d+)')
RX_SKIPF = re.compile(rb' frame=(\d+)')
RX_GLITCH = re.compile(r'^one-frame glitches: (\d+)\s*$')
RX_VFRAMES = re.compile(r': (\d+) frames \d+x\d+')
RX_SEAL = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)$')
SEALED_NAMES = ('go142a.sh', 'sc142.py', 'test_sc142.py', 'mut_sc142.py', 'enter_scene.py',
                'idle142.py', 'procload.py', 'run_safety99.py', 'launch_run.py', 'gates_default.txt', 'sheet142.py',
                'test_go142a.py', 'C:/kyty/scripts/s51_vidglitch.py')
CHUNK = 1 << 26
CALIB = (('eatl122', 'C:/kyty/s122/log_eatl122.txt', 'penguin_atlantis'),
         ('edes122', 'C:/kyty/s122/log_edes122.txt', 'intro_next'),
         ('atl122', 'C:/kyty/s122/log_atl122.txt', 'penguin_atlantis'),
         ('ednn122', 'C:/kyty/s122/log_ednn122.txt', 'rotating_level_day_and_night'),
         ('eght122', 'C:/kyty/s122/log_eght122.txt', 'time_stopper_ghost_world'))
CHECK_K2 = (('s1s128', 'C:/kyty/s128'), ('s2s128', 'C:/kyty/s128'))
CHECK_VAL = ('s6s137', 'C:/kyty/s137/log_s6s137.txt', 'C:/kyty/s137/stdout_s6s137.txt')


def level_of(tag):
    if tag in (V_TAG, W_TAG):
        return SKY
    for t, lv in CENSUS:
        if t == tag:
            return lv
    return None


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _line(whole, i):
    s = whole.rfind(b'\n', 0, i) + 1
    e = whole.find(b'\n', i)
    if e < 0:
        e = len(whole)
    return s, e


def scan(path):
    """One streaming pass over a log (or an emulator stdout): rows, starts, markers - each with its byte position."""
    res = dict(path=path, rows=[], starts=[], crash=[], hang=[], skip_lines=0, skip_frames=set(), ops=[], stubs=[],
               prio=[], bvh=[], vke=[], quit=None, ended=[], bytes=0, torn=0, noval=0, valfeat=0, vkany=0)
    h = hashlib.sha256()
    off = 0
    tail = b''
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            h.update(b)
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
            nft = 0
            for m in RX_FT.finditer(whole):
                d = RX_DRAWS.search(m.group(3))
                res['rows'].append((int(m.group(1)), int(m.group(2)), int(d.group(1)) if d else -1, base + m.start()))
                nft += 1
            res['torn'] += whole.count(M_FT) - nft
            res['noval'] += whole.count(M_NOVAL)
            res['valfeat'] += whole.count(M_VALFEAT)
            res['vkany'] += whole.count(M_VKANY)
            for marker, key in ((M_START, 'starts'), (M_SKIP, 'skip'), (M_OPC, 'ops'), (M_STUB, 'stubs'),
                                (M_PRIO, 'prio'), (M_BVH, 'bvh'), (M_VKE, 'vke'), (M_QUIT, 'quit'), (M_ENDED, 'ended')) \
                    + tuple((m, 'crash') for m in CRASH) + tuple((m, 'hang') for m in HANG):
                i = whole.find(marker)
                while i >= 0:
                    s, e = _line(whole, i)
                    line = whole[s:e]
                    pos = base + s
                    if key == 'starts':
                        res['starts'].append((line[line.find(marker) + len(marker):].strip().decode('latin1'), pos))
                    elif key == 'skip':
                        res['skip_lines'] += 1
                        x = RX_SKIPF.search(line)
                        if x:
                            res['skip_frames'].add(int(x.group(1)))
                    elif key == 'ops':
                        y = RX_OP.search(line)
                        res['ops'].append(((y.group(1).decode(), y.group(2).decode().lower()) if y else ('?', '?'), pos))
                    elif key == 'stubs':
                        e2 = whole.find(b'\n', e + 1)
                        nxt = whole[e + 1:e2 if e2 >= 0 else len(whole)]
                        res['stubs'].append((nxt.split(b'\t')[-1].strip().decode('latin1')[:120], pos))
                    elif key == 'prio':
                        z = RX_PRIO.search(line)
                        res['prio'].append((int(z.group(1)) if z else -1, pos))
                    elif key == 'quit':
                        if res['quit'] is None or pos < res['quit']:
                            res['quit'] = pos
                    else:
                        res[key].append((marker.decode(), pos, line[:200].decode('latin1')))
                    i = whole.find(marker, e)
            if not b:
                break
    res['sha256'] = h.hexdigest()
    res['bytes'] = off
    res['rows'].sort(key=lambda r: r[3])
    for k in ('starts', 'ops', 'stubs', 'prio'):
        res[k].sort(key=lambda r: r[1])
    for k in ('crash', 'hang', 'bvh', 'vke', 'ended'):
        res[k].sort(key=lambda r: r[1])
    return res


def derive(sc, level, quit_pos=None):
    """The reading of item 221 (g)(2) with the first-frame rule of item 221 (v) and the scene change of item 224 (a)(7)
    on one scan (letter and variant vx)."""
    out = dict(level=level, entered=False, entry_pos=None, first=None, window=0, hold=0, k2=[], k3w=[], k3h=[],
               dt_after_entry_us=0, dt_after_first_us=0, frames_after_first=0, n_gaps=0, other_starts=[],
               change_pos=None, after_change=dict(rows=0, dt_us=0, k2=0), dt_median_us=None, dt_max_us=None,
               vx=dict(k2=[], k3w=[], k3h=[], dt_after_first_us=0, frames_after_first=0))
    ent = [p for name, p in sc['starts'] if name == level]
    if not ent:
        return out
    out['entered'] = True
    epos = ent[0]
    out['entry_pos'] = epos
    later = [(name, p) for name, p in sc['starts'] if p > epos]
    cpos = later[0][1] if later else None
    out['change_pos'] = cpos
    rows_after = [r for r in sc['rows'] if r[3] > epos]
    for name, p in later:
        prev = [r[0] for r in rows_after if r[3] < p]
        out['other_starts'].append((name, prev[-1] if prev else None))
    after = [r for r in rows_after if cpos is None or r[3] < cpos]
    beyond = [r for r in rows_after if cpos is not None and r[3] > cpos]
    out['after_change'] = dict(rows=len(beyond), dt_us=sum(r[1] for r in beyond),
                               k2=sum(1 for r in beyond if r[1] >= K2_US))
    out['dt_after_entry_us'] = sum(r[1] for r in after)
    fi = None
    for i, r in enumerate(after):
        if r[2] >= SCENE_DRAWS:
            fi = i
            break
    if fi is None:
        return out
    out['first'] = (after[fi][0], after[fi][1], after[fi][2])
    post = after[fi + 1:]

    def classes(rows):
        win, hold = rows[:ENTRY_WIN], rows[ENTRY_WIN:]
        k2 = [(r[0], r[1], 'entry' if j < ENTRY_WIN else 'hold') for j, r in enumerate(rows) if r[1] >= K2_US]
        k3w = [(r[0], r[1]) for r in win if K3_US <= r[1] < K2_US]
        k3h = [(r[0], r[1]) for r in hold if K3_US <= r[1] < K2_US]
        return k2, k3w, k3h, len(win), len(hold)
    out['k2'], out['k3w'], out['k3h'], out['window'], out['hold'] = classes(post)
    out['dt_after_first_us'] = sum(r[1] for r in post)
    out['frames_after_first'] = len(post)
    out['n_gaps'] = sum(1 for a, b in zip(post, post[1:]) if b[0] != a[0] + 1)
    ds = sorted(r[1] for r in post)
    if ds:
        out['dt_median_us'] = ds[len(ds) // 2]
        out['dt_max_us'] = ds[-1]
    q = quit_pos if quit_pos is not None else sc.get('quit')
    vpost = [r for r in post if q is None or r[3] < q]
    all_rows_end = sc['rows'][-1][3] if sc['rows'] else None
    vpost = [r for r in vpost if r[3] != all_rows_end]
    k2, k3w, k3h, _, _ = classes(vpost)
    out['vx'] = dict(k2=k2, k3w=k3w, k3h=k3h, dt_after_first_us=sum(r[1] for r in vpost), frames_after_first=len(vpost))
    return out


def markers(log, std, entry_pos, quit_pos):
    """Death markers of the log and the emulator stdout in the order of item 224 (a)(1): the log ones by position, then the
    stdout ones by position; kind, class, source, position, before/after the first Event: quit."""
    res = []
    for src, sc in (('log', log), ('stdout', std)):
        if sc is None:
            continue
        got = []
        for key in ('crash', 'hang'):
            for kind, pos, line in sc[key]:
                at_exit = src == 'log' and quit_pos is not None and pos > quit_pos
                got.append(dict(kind=kind, cls='K1' if key == 'crash' else 'K2', src=src, pos=pos, at_exit=at_exit,
                                line=line))
        got.sort(key=lambda m: m['pos'])
        res.extend(got)
    return res


def validation(log, std):
    """Item 224 (a)(2): the layer is active = 0 lines "no validation layer:" AND >= 1 line of the layer's extension
    VK_EXT_validation_features AND >= 1 "[Vulkan][" line (any level) - log and emulator stdout together."""
    n = dict(noval=0, valfeat=0, vkany=0)
    for sc in (log, std):
        if sc is not None:
            for k in ('noval', 'valfeat', 'vkany'):
                n[k] += sc[k]
    n['ok'] = log is not None and n['noval'] == 0 and n['valfeat'] >= 1 and n['vkany'] >= 1
    return n


def opcode_diff(ops, entry_pos):
    cnt = {}
    after = {}
    for k, pos in ops:
        cnt[k] = cnt.get(k, 0) + 1
        if entry_pos is not None and pos > entry_pos:
            after[k] = after.get(k, 0) + 1
    keys = sorted(set(cnt) | set(OPCODE_BASE))
    diff = [(k[0], k[1], cnt.get(k, 0), OPCODE_BASE.get(k, 0), cnt.get(k, 0) - OPCODE_BASE.get(k, 0), after.get(k, 0))
            for k in keys if cnt.get(k, 0) != OPCODE_BASE.get(k, 0)]
    return dict(total=sum(cnt.values()), diff=diff, profile_equal=not diff)


def read_glitch(path):
    """glitch_<tag>.txt of s51_vidglitch.py 4 6: (video frames, glitches) or None when the file or a line is missing."""
    if not os.path.isfile(path):
        return None
    frames = glitches = None
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            m = RX_GLITCH.match(line.rstrip('\n'))
            if m:
                glitches = int(m.group(1))
            v = RX_VFRAMES.search(line)
            if v and frames is None:
                frames = int(v.group(1))
    if frames is None or glitches is None:
        return None
    return dict(video_frames=frames, glitches=glitches)


def idx_count(path):
    """Records of rec_<tag>.mp4.idx (lines of >= 3 fields, as s51_vidglitch.py reads them); None without the file."""
    if not os.path.isfile(path):
        return None
    n = 0
    with open(path, 'rb') as f:
        for line in f:
            if len(line.split()) >= 3:
                n += 1
    return n


def sheet_state(root, tag):
    """Item 224 (a)(5): the sheet file, its sha256 and the sha256 of the video against the lines of step2/times.txt."""
    png = os.path.join(root, 'sheet_%s.png' % tag)
    mp4 = os.path.join(root, 'rec_%s.mp4' % tag)
    size = os.path.getsize(png) if os.path.isfile(png) else 0
    sha = sha_file(png) if size > 0 else None
    rec = sha_file(mp4) if os.path.isfile(mp4) else None
    t_sheet = t_rec = None
    tp = os.path.join(root, 'step2', 'times.txt')
    if os.path.isfile(tp):
        rs = re.compile(r'go142a %s sheet rc \S+ sheet_%s\.png sha256 ([0-9a-f]{64})' % (tag, tag))
        rr = re.compile(r'go142a %s s51_vidglitch rc \S+ glitch_%s\.txt sha256 \S* rec_%s\.mp4 sha256 ([0-9a-f]{64})'
                        % (tag, tag, tag))
        with open(tp, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                a = rs.search(line)
                if a:
                    t_sheet = a.group(1)
                b = rr.search(line)
                if b:
                    t_rec = b.group(1)
    ok = size > 0 and sha == t_sheet and rec is not None and rec == t_rec
    return dict(size=size, sha=sha, times_sha=t_sheet, rec_sha=rec, times_rec_sha=t_rec, ok=ok)


def last_value(seq, name):
    val = None
    for i, a in enumerate(seq):
        if a == name and i + 1 < len(seq):
            val = seq[i + 1]
    return val


def admit(tag, js, pred_sha):
    """Admission of one run by its json: (check, ok, detail) rows."""
    lv = level_of(tag)
    env = js.get('env') or {}
    at = js.get('attempts') or []
    rows = []

    def add(name, ok, detail=''):
        rows.append((name, bool(ok), str(detail)))
    add('one attempt (--attempts 1, no warmup)', len(at) == 1 and at[0].get('label') == 'attempt 1', len(at))
    add('build %s' % BUILD_SHA[:8], js.get('binary_sha256') == BUILD_SHA, (js.get('binary_sha256') or '')[:8])
    add('guest args -lvl %s' % lv, js.get('guest_args') == '-lvl %s' % lv, js.get('guest_args'))
    add('gates empty (shipped defaults)', js.get('gates') == '', repr(js.get('gates'))[:40])
    add('KYTY_GPU_CLOCK_PIN=1', env.get('KYTY_GPU_CLOCK_PIN') == '1', env.get('KYTY_GPU_CLOCK_PIN'))
    add('KYTY_GPU_MARKERS=0', env.get('KYTY_GPU_MARKERS') == '0', env.get('KYTY_GPU_MARKERS'))
    add('no KYTY_GPU_CHECKPOINTS', 'KYTY_GPU_CHECKPOINTS' not in env, '')
    add('no KYTY_GATE_SCHEDULE', 'KYTY_GATE_SCHEDULE' not in env and 'KYTY_GATE_SCHEDULE_ABBA' not in env, '')
    rec = env.get('KYTY_REC')
    if tag == W_TAG:
        add('no video in W', rec is None, rec)
    else:
        add('video KYTY_REC rec_%s.mp4' % tag, rec is not None and rec.replace('\\', '/').endswith('/rec_%s.mp4' % tag), rec)
    val = last_value(js.get('cmdline') or [], '--vulkan-validation')
    want = 'true' if tag == W_TAG else 'false'
    add('--vulkan-validation %s' % want, val == want, val)
    if tag == W_TAG:
        add('VK_LAYER_PATH in W', bool(env.get('VK_LAYER_PATH')), env.get('VK_LAYER_PATH'))
    pr = js.get('prereg') or {}
    add('prereg = the seal now', pred_sha is not None and pr.get('sha256') == pred_sha
        and (pr.get('path') or '').replace('\\', '/') == PRED_PATH, (pr.get('sha256') or '')[:8])
    add('no pipeline-cache retry', not any(a.get('pipeline_cache_off') for a in at), '')
    return rows


def build(tag, lv, js, log, std, es, root, pred_sha):
    """Everything the scorer reads about one run from its json and the scans of its log, stdout and enter_scene stdout."""
    at = (js.get('attempts') or [{}])[0]
    r = dict(tag=tag, level=lv, made=True, log_present=log is not None, stdout_present=std is not None,
             admit=admit(tag, js, pred_sha))
    if log is None:
        r.update(derive=derive(dict(rows=[], starts=[], quit=None), lv), marks=[], log_sha=None)
    else:
        r['log_sha'] = log['sha256']
        r['derive'] = derive(log, lv)
        r['marks'] = markers(log, std, r['derive']['entry_pos'], log['quit'])
    d = r['derive']
    ended = at.get('hold_exit') is not None or (es is not None and bool(es['ended']))
    exited = at.get('outcome') == 'exited'
    r['hold_exit'] = at.get('hold_exit')
    r['ended'] = ended
    r['exited'] = exited
    r['attempt_outcome'] = at.get('outcome')
    r['hold_s'] = at.get('hold_s')
    r['ft_tail'] = at.get('ft_tail')
    r['tail_stall'] = at.get('ft_tail') == 0 and at.get('hold_s') is not None
    r['val'] = validation(log, std)
    if tag == W_TAG:
        r['admit'].append(('validation active (0 no validation layer, >= 1 VK_EXT_validation_features, >= 1 [Vulkan][)',
                           r['val']['ok'], '%d/%d/%d' % (r['val']['noval'], r['val']['valfeat'], r['val']['vkany'])))
    r['rows_total'] = len(log['rows']) if log is not None else 0
    r['torn'] = log['torn'] if log is not None else 0
    if log is not None:
        r['skip'] = dict(lines=log['skip_lines'], frames=len(log['skip_frames']))
        r['ops'] = opcode_diff(log['ops'], d['entry_pos'])
        r['stubs'] = [n for n, _ in log['stubs']]
        pr = [u for u, _ in log['prio']]
        r['prio'] = dict(over=sum(1 for u in pr if u > PRIO_US), max=max(pr) if pr else 0, lines=len(pr))
        r['bvh'] = len(log['bvh'])
        r['vke'] = len(log['vke']) + (len(std['vke']) if std else 0)
        r['vke_first'] = [x[2] for x in (log['vke'] + (std['vke'] if std else []))[:3]]
    r['glitch'] = read_glitch(os.path.join(root, 'glitch_%s.txt' % tag))
    r['idx'] = idx_count(os.path.join(root, 'rec_%s.mp4.idx' % tag))
    g = r['glitch']
    r['cover'] = g is not None and g['video_frames'] >= r['rows_total'] - COVER_SLACK
    r['sheet_file'] = os.path.isfile(os.path.join(root, 'sheet_%s.png' % tag))
    r['sheet'] = sheet_state(root, tag) if tag == V_TAG else None
    r['outcome'], r['outcome_vx'], r['key'], r['reason'] = outcome(r)
    return r


def entry_of(tag, root=ROOT, pred_sha=None):
    """Everything the scorer reads about one run; None when the run was not made (no <tag>.json)."""
    lv = level_of(tag)
    jp = os.path.join(root, '%s.json' % tag)
    if not os.path.isfile(jp):
        return None
    js = json.load(open(jp, encoding='utf-8'))
    lp = os.path.join(root, 'log_%s.txt' % tag)
    sp = os.path.join(root, 'stdout_%s.txt' % tag)
    ep = os.path.join(root, '%s.stdout.txt' % tag)
    log = scan(lp) if os.path.isfile(lp) else None
    std = scan(sp) if os.path.isfile(sp) else None
    es = scan(ep) if os.path.isfile(ep) else None
    return build(tag, lv, js, log, std, es, root, pred_sha)


def attempt_marker(tag, root=ROOT):
    """Item 224 (a)(8): the chain's marker attempt_<tag>.txt of a made attempt."""
    return os.path.isfile(os.path.join(root, 'attempt_%s.txt' % tag))


def outcome(r):
    """(letter outcome, variant-vx outcome, stop key, reason) of one census entry (items 221 (g)(2), 223 (a), 224 (a))."""
    d = r['derive']
    ms = r.get('marks') or []

    def one(marks, k2):
        if not d['entered']:
            return 'NOT_ENTERED', 'no entry line'
        cpos = d['change_pos']
        if cpos is not None:
            pre = [m for m in marks if m['src'] == 'log' and m['pos'] < cpos]
            if pre:
                return pre[0]['cls'], 'first death marker %s before the scene change' % pre[0]['kind']
            if k2:
                return 'K2', 'frame dt >= 1 s before the scene change'
            return 'NOT_EVALUABLE', 'scene change'
        if marks:
            return marks[0]['cls'], 'first death marker %s (%s)' % (marks[0]['kind'], marks[0]['src'])
        if r['ended'] or r['exited']:
            return 'K1', 'hold_exit / ENDED / exited'
        if k2 or r['tail_stall']:
            return 'K2', 'frame dt >= 1 s or tail stall'
        if d['first'] is None:
            return 'NOT_EVALUABLE', 'no first scene frame'
        if r['attempt_outcome'] != 'ok':
            return 'NOT_EVALUABLE', 'no stable (%s)' % r['attempt_outcome']
        if (r['hold_s'] or 0) < HOLD_CENSUS_S:
            return 'NOT_EVALUABLE', 'hold_s %s < %d' % (r['hold_s'], HOLD_CENSUS_S)
        if d['dt_after_entry_us'] >= HOLD_CENSUS_US:
            return 'HOLDS_120', 'held'
        return 'NOT_EVALUABLE', 'presented time after the entry line < 120 s'
    letter, reason = one(ms, d['k2'])
    vx = one([m for m in ms if not m['at_exit']], d['vx']['k2'])[0]
    key = None
    if letter == 'NOT_ENTERED':
        key = ms[0]['kind'] if ms else ('attempt:%s' % r.get('attempt_outcome'))
    return letter, vx, key, reason


def scene_ok(v, w, sheet):
    """SCENE_OK of Sky Garden by item 221 (g)(3) and item 224 (a): (word, rows)."""
    rows = []

    def add(name, ok, detail=''):
        rows.append((name, bool(ok), str(detail)))
    add('V made', v is not None, '')
    add('W made', w is not None, '')
    if v is not None:
        dv = v['derive']
        g = v['glitch']
        add('V admitted', all(a[1] for a in v['admit']), ';'.join(a[0] for a in v['admit'] if not a[1]))
        add('V entered', dv['entered'], '')
        add('V first scene frame', dv['first'] is not None, dv['first'])
        add('V no scene change after the entry line', dv['change_pos'] is None, dv['other_starts'])
        add('V emulator stdout present', v['stdout_present'], '')
        add('V attempt ok, hold_s >= 330, no hold_exit / ENDED', v['attempt_outcome'] == 'ok'
            and (v['hold_s'] or 0) >= HOLD_V_S and v['hold_exit'] is None and not v['ended'], v['hold_s'])
        add('V 0 death markers (incl. hold_exit, exited)', not v['marks'] and not v['ended'] and not v['exited'],
            ';'.join(m['kind'] for m in v['marks']))
        add('V no frame dt >= 1 s after the first scene frame', not dv['k2'] and not v['tail_stall'],
            dv['k2'][:3])
        add('V n gaps after the first scene frame = 0', dv['n_gaps'] == 0, dv['n_gaps'])
        add('V sum dt_us after the first scene frame >= 300 s', dv['dt_after_first_us'] >= HOLD_SCENE_US,
            dv['dt_after_first_us'])
        add('V >= 3000 presented frames after the first scene frame', dv['frames_after_first'] >= FRAMES_V,
            dv['frames_after_first'])
        add('V video >= 3000 frames', g is not None and g['video_frames'] >= FRAMES_V,
            'missing' if g is None else g['video_frames'])
        add('V video frames >= FrameTrace rows in all - 100', v['cover'],
            '%s vs %d' % ('missing' if g is None else g['video_frames'], v['rows_total']))
        add('V 0 one-frame glitches (s51_vidglitch.py 4 6)', g is not None and g['glitches'] == 0,
            'missing' if g is None else g['glitches'])
    if w is not None:
        dw = w['derive']
        add('W admitted', all(a[1] for a in w['admit']), ';'.join(a[0] for a in w['admit'] if not a[1]))
        add('W entered', dw['entered'], '')
        add('W no scene change after the entry line', dw['change_pos'] is None, dw['other_starts'])
        add('W emulator stdout present', w['stdout_present'], '')
        add('W 0 death markers (incl. hold_exit, exited)', not w['marks'] and not w['ended'] and not w['exited'],
            ';'.join(m['kind'] for m in w['marks']))
        add('W 0 [Vulkan][E] lines', w.get('vke', 1) == 0 and w['log_present'], w.get('vke'))
        add('W ft_tail > 0', (w['ft_tail'] or 0) > 0, w['ft_tail'])
        add('W hold reached its end (ok, hold_s >= 300, no hold_exit)', w['attempt_outcome'] == 'ok'
            and (w['hold_s'] or 0) >= HOLD_W_S and w['hold_exit'] is None and not w['ended'], w['hold_s'])
    machine = all(x[1] for x in rows) and v is not None and w is not None
    sh = v['sheet'] if v is not None else None
    file_ok = sh is not None and sh['ok']
    rows.append(('V sheet file sheet_v142.png present, non-empty; its sha256 and the sha256 of rec_v142.mp4 = step2/times.txt',
                 file_ok, 'missing' if sh is None else 'size %d sha %s times %s rec %s times %s' % (
                     sh['size'], (sh['sha'] or '-')[:16], (sh['times_sha'] or '-')[:16], (sh['rec_sha'] or '-')[:16],
                     (sh['times_rec_sha'] or '-')[:16])))
    if not machine:
        word = 'NO'
    elif sheet == 'viewed':
        word = 'YES' if file_ok else 'NO'
    elif sheet == 'not-viewed':
        word = 'NO'
    else:
        word = 'PENDING_SHEET'
    rows.append(('sheet of V viewed by the lead (filled by the close)', sheet == 'viewed', sheet or 'UNSET'))
    return word, rows


def stop_check(outcomes):
    """Item 221 (g)(4): three census levels in a row NOT_ENTERED with one marker -> stop.  outcomes: [(tag, outcome, key)]
    in the census order, made ones only; returns (stop, tags)."""
    run = []
    for tag, oc, key in outcomes:
        if oc == 'NOT_ENTERED':
            if run and run[-1][2] != key:
                run = []
            run.append((tag, oc, key))
        else:
            run = []
        if len(run) >= STOP_RUN:
            return True, [t for t, _, _ in run[-STOP_RUN:]]
    return False, []


def fmt_entry(r):
    d = r['derive']
    o = []
    o.append('TAG %s level %s outcome %s (variant vx: %s) reason: %s; log %s' % (
        r['tag'], r['level'], r['outcome'], r['outcome_vx'], r['reason'], (r.get('log_sha') or 'MISSING')[:16]))
    bad = [a for a in r['admit'] if not a[1]]
    o.append('  admission: %s' % ('PASS' if not bad else 'FAIL ' + '; '.join('%s (%s)' % (a[0], a[2]) for a in bad)))
    o.append('  attempt: outcome %s hold_s %s hold_exit %s ft_tail %s' % (r['attempt_outcome'], r['hold_s'],
                                                                         r['hold_exit'], r['ft_tail']))
    o.append('  emulator stdout: %s' % ('present' if r['stdout_present'] else 'MISSING (its markers are not read)'))
    o.append('  entry line: %s; first scene frame (n, dt_us, draws): %s; window %d rows, hold %d rows; n gaps %d; '
             'torn FrameTrace lines %d' % ('yes' if d['entered'] else 'NO', d['first'], d['window'], d['hold'],
                                           d['n_gaps'], r['torn']))
    o.append('  scene change (Level has started after the entry line; name, last n before it): %s; rows after it %d '
             '(%.1f s, dt >= 1 s %d; not classified)' % (d['other_starts'] or 'none', d['after_change']['rows'],
                                                          d['after_change']['dt_us'] / 1e6, d['after_change']['k2']))
    o.append('  presented time: after the entry line %.1f s; after the first scene frame %.1f s over %d frames; dt_us '
             'median %s max %s' % (d['dt_after_entry_us'] / 1e6, d['dt_after_first_us'] / 1e6, d['frames_after_first'],
                                   d['dt_median_us'], d['dt_max_us']))
    o.append('  K2 frames (dt >= 1 s after the first scene frame): %s; tail stall (ft_tail 0): %s'
             % (d['k2'] or 'none', 'yes' if r['tail_stall'] else 'no'))
    o.append('  K3 entry window (no warm base): %s' % (d['k3w'] or 'none'))
    o.append('  K3 hold: %s' % (d['k3h'] or 'none'))
    vx = d['vx']
    o.append('  variant vx (before Event: quit, last row out): K2 %s; K3 window %s; K3 hold %s; %.1f s over %d frames'
             % (vx['k2'] or 'none', vx['k3w'] or 'none', vx['k3h'] or 'none', vx['dt_after_first_us'] / 1e6,
                vx['frames_after_first']))
    o.append('  death markers (in order): %s' % ('; '.join('%s %s %s@%d%s' % (m['cls'], m['kind'], m['src'], m['pos'],
                                                            ' at-exit' if m['at_exit'] else '') for m in r['marks'])
                                                 or 'none'))
    o.append('  hold_exit / game ended: %s; exited before stable: %s' % ('yes' if r['ended'] else 'no',
                                                                       'yes' if r['exited'] else 'no'))
    vl = r['val']
    o.append('  validation layer lines: no validation layer %d, VK_EXT_validation_features %d, [Vulkan][ %d -> active %s'
             % (vl['noval'], vl['valfeat'], vl['vkany'], 'yes' if vl['ok'] else 'no'))
    if r['log_present']:
        op = r['ops']
        o.append('  AsyncPipelines skipped draw: %d lines, %d frames (counted, not fatal)' % (r['skip']['lines'],
                                                                                         r['skip']['frames']))
        o.append('  opcode not implemented: %d lines; against 96/1/4: %s' % (op['total'], 'equal' if op['profile_equal']
                 else ', '.join('%s %s %d (base %d, %+d, after entry %d)' % x for x in op['diff'])))
        o.append('  Stubbed function: %d%s' % (len(r['stubs']), (' ' + ', '.join(r['stubs'][:10])) if r['stubs'] else ''))
        o.append('  PriorityStall > 50 ms: %d (lines %d, max %d us)' % (r['prio']['over'], r['prio']['lines'],
                                                                      r['prio']['max']))
        o.append('  BvhLoopCapTrip: %d' % r['bvh'])
        o.append('  [Vulkan][E]: %d%s' % (r['vke'], (' first: ' + ' | '.join(r['vke_first'])) if r['vke'] else ''))
    g = r['glitch']
    o.append('  video: frames %s, .idx records %s, FrameTrace rows in all %d, after the first scene frame %d; coverage '
             '(video >= rows - 100): %s' % ('n/a' if g is None else g['video_frames'], r['idx'], r['rows_total'],
                                             d['frames_after_first'],
                                             'yes' if r['cover'] else 'NO - glitches not conclusive'))
    o.append('  glitches s51_vidglitch.py 4 6: %s; sheet file: %s (viewed by the lead at the close)'
             % ('n/a' if g is None else '%d of %d video frames' % (g['glitches'], g['video_frames']),
                'yes' if r['sheet_file'] else 'no'))
    if r['sheet'] is not None:
        sh = r['sheet']
        o.append('  sheet and video sha256 (item 224 (a)(5)): sheet size %d sha %s (times.txt %s); rec sha %s (times.txt %s); '
                 'match %s' % (sh['size'], sh['sha'], sh['times_sha'], sh['rec_sha'], sh['times_rec_sha'],
                               'yes' if sh['ok'] else 'NO'))
    return o


def check_seal(pred=PRED_PATH, root=ROOT, me=None):
    """Every "seal: <sha> <name>" line of the seal against its file; the scorer itself and every SEALED_NAMES name must
    be there.  Returns (ok, rows)."""
    rows = []
    if not os.path.isfile(pred):
        return False, [('seal file', False, pred)]
    seen = {}
    for line in open(pred, encoding='utf-8'):
        m = RX_SEAL.match(line.rstrip('\n'))
        if m:
            seen[m.group(2)] = m.group(1)
    for name in SEALED_NAMES:
        if name not in seen:
            rows.append((name, False, 'no seal line'))
    for name, sh in sorted(seen.items()):
        p = name if (name.startswith('C:/') or name.startswith('/')) else os.path.join(root, name)
        now = sha_file(p) if os.path.isfile(p) else None
        rows.append((name, now == sh, (now or 'missing')[:16]))
    mine = sha_file(me or os.path.abspath(__file__))
    rows.append(('this scorer in the seal', seen.get('sc142.py') == mine, mine[:16]))
    return all(r[1] for r in rows), rows


def forms(ents):
    """(B5a, B5) counts over admitted entries (item 221 (v))."""
    b5a = sum(1 for e in ents if e['derive']['k2'])
    b5 = sum(1 for e in ents if any(x[2] == 'entry' for x in e['derive']['k2']) or e['derive']['k3w'])
    return b5a, b5


def summary(root, pred_sha, sheet):
    out = []
    ents = {t: entry_of(t, root, pred_sha) for t in SEQ}
    nojs = [t for t in SEQ if ents[t] is None and attempt_marker(t, root)]
    for t in SEQ:
        if ents[t] is not None:
            out.extend(fmt_entry(ents[t]))
        elif t in nojs:
            out.append('TAG %s: ATTEMPT MADE, NO JSON (instrument)' % t)
        else:
            out.append('TAG %s: not made' % t)
    word, rows = scene_ok(ents[V_TAG], ents[W_TAG], sheet)
    out.append('SCENE_OK %s: %s' % (SKY, word))
    for name, ok, det in rows:
        out.append('  %-4s %s (%s)' % ('PASS' if ok else 'FAIL', name, det))
    v, w = ents[V_TAG], ents[W_TAG]
    out.append('  info dt_us after the first scene frame: V median %s max %s; W median %s max %s; W presented %s s over %s '
               'frames' % (v['derive']['dt_median_us'] if v else None, v['derive']['dt_max_us'] if v else None,
                           w['derive']['dt_median_us'] if w else None, w['derive']['dt_max_us'] if w else None,
                           '%.1f' % (w['derive']['dt_after_first_us'] / 1e6) if w else None,
                           w['derive']['frames_after_first'] if w else None))
    made = [ents[t] for t, _ in CENSUS if ents[t] is not None]
    adm = [e for e in made if all(a[1] for a in e['admit'])]
    adm_tags = set(e['tag'] for e in adm)
    out.append('CENSUS made %d of %d (of them attempt made without json %d), admitted %d' % (
        len(made) + sum(1 for t, _ in CENSUS if t in nojs), len(CENSUS), sum(1 for t, _ in CENSUS if t in nojs), len(adm)))
    for t, lv in CENSUS:
        e = ents[t]
        if e is not None:
            out.append('  %s %-28s %-13s vx %-13s first %s K2 %d K3w %d K3h %d admitted %s reason %s' % (
                e['tag'], e['level'], e['outcome'], e['outcome_vx'], e['derive']['first'], len(e['derive']['k2']),
                len(e['derive']['k3w']), len(e['derive']['k3h']), 'yes' if e['tag'] in adm_tags else 'NO', e['reason']))
        elif t in nojs:
            out.append('  %s %-28s ATTEMPT MADE, NO JSON (instrument) - not admitted' % (t, lv))
    b5a, b5 = forms(adm)
    ent = sum(1 for e in adm if e['derive']['entered'])
    out.append('FORM B5a (a frame dt >= 1 s after the first scene frame): %d/%d [c] (admitted and entered %d)'
               % (b5a, len(CENSUS), ent))
    out.append('FORM B5 (a frame dt >= 100 ms in the entry window, no warm base): %d/%d [c] (admitted and entered %d)'
               % (b5, len(CENSUS), ent))
    first5 = [t for t, _ in CENSUS[:HALF]]
    fa, fb = forms([e for e in adm if e['tag'] in first5])
    la, lb = forms([e for e in adm if e['tag'] not in first5])
    out.append('FORMS second reading by the order (shared caches warm from earlier runs): first five B5a %d/5 B5 %d/5; '
               'last five B5a %d/5 B5 %d/5' % (fa, fb, la, lb))
    oc = []
    for t, _ in CENSUS:
        if ents[t] is not None:
            oc.append((t, ents[t]['outcome'], ents[t]['key']))
        elif t in nojs:
            oc.append((t, 'ATTEMPT_NO_JSON', None))
    stop, tags = stop_check(oc)
    out.append('STOP RULE (item 221 (g)(4)): %s' % (('STOP ' + ','.join(tags)) if stop else 'not met'))
    return out, ents, word


def calib():
    """Item 221 (g)(4): the five s122 logs; returns (passed, lines)."""
    lines = []
    passed = 0
    for tag, path, level in CALIB:
        sc = scan(path)
        d = derive(sc, level)
        k2 = [x[0] for x in d['k2']]
        k2loc = [x[2] for x in d['k2']]
        k3w = [x[0] for x in d['k3w']]
        k3h = [x[0] for x in d['k3h']]
        if tag == 'eatl122':
            ok = k2 == [191] and k2loc == ['entry']
        elif tag == 'edes122':
            ok = k2 == [4945] and k2loc == ['hold']
        elif tag == 'atl122':
            ok = not k2 and not k3w and not k3h
        elif tag == 'ednn122':
            ok = not k2 and not k3w and 1826 in k3h
        else:
            ok = not k2 and 389 in k3w
        passed += ok
        lines.append('CALIB %s %s sha %s level %s first %s K2 %s K3w %s K3h %s -> %s' % (
            tag, path, sc['sha256'][:16], level, d['first'], list(zip(k2, k2loc)) or 'none', k3w or 'none',
            k3h or 'none', 'PASS' if ok else 'FAIL'))
    lines.append('CALIB %d of %d' % (passed, len(CALIB)))
    return passed, lines


def checks1b():
    """Item 224 (b)(2): the device-lost logs s1s128, s2s128 -> outcome K2; s6s137 -> validation active by its three
    terms.  Returns (passed, total, lines)."""
    lines = []
    passed = 0
    for tag, root in CHECK_K2:
        js = json.load(open(os.path.join(root, '%s.json' % tag), encoding='utf-8'))
        lv = (js.get('guest_args') or '').split()[-1]
        paths = [os.path.join(root, x % tag) for x in ('log_%s.txt', 'stdout_%s.txt', '%s.stdout.txt')]
        scans = [scan(p) if os.path.isfile(p) else None for p in paths]
        r = build(tag, lv, js, scans[0], scans[1], scans[2], root, None)
        ok = r['outcome'] == 'K2'
        passed += ok
        lines.append('CHECK1B %s log sha %s level %s outcome %s key %s reason %s markers %s -> %s' % (
            tag, (r['log_sha'] or 'MISSING')[:16], lv, r['outcome'], r['key'], r['reason'],
            ';'.join('%s %s@%d' % (m['kind'], m['src'], m['pos']) for m in r['marks']), 'PASS' if ok else 'FAIL'))
    tag, lp, sp = CHECK_VAL
    log = scan(lp)
    std = scan(sp) if os.path.isfile(sp) else None
    vl = validation(log, std)
    passed += vl['ok']
    lines.append('CHECK1B %s log sha %s validation: no validation layer %d, VK_EXT_validation_features %d, [Vulkan][ %d '
                 '-> active %s -> %s' % (tag, log['sha256'][:16], vl['noval'], vl['valfeat'], vl['vkany'],
                                         'yes' if vl['ok'] else 'no', 'PASS' if vl['ok'] else 'FAIL'))
    total = len(CHECK_K2) + 1
    lines.append('CHECK1B %d of %d' % (passed, total))
    return passed, total, lines


def main(argv=None, root=ROOT, pred=PRED_PATH):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--tag')
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--stop-check')
    ap.add_argument('--check-seal', action='store_true')
    ap.add_argument('--calib', action='store_true')
    ap.add_argument('--check1b', action='store_true')
    ap.add_argument('--sheet', choices=('viewed', 'not-viewed'), default=None)
    a = ap.parse_args(argv)
    if a.check_seal:
        ok, rows = check_seal(pred, root)
        for name, good, det in rows:
            print('%-4s %s %s' % ('OK' if good else 'BAD', name, det))
        print('SEAL: %s' % ('PASS' if ok else 'FAIL'))
        return 0 if ok else 1
    if a.calib:
        n, lines = calib()
        print('\n'.join(lines))
        return 0 if n == len(CALIB) else 1
    if a.check1b:
        n, total, lines = checks1b()
        print('\n'.join(lines))
        return 0 if n == total else 1
    pred_sha = sha_file(pred) if os.path.isfile(pred) else None
    if a.stop_check:
        if a.stop_check not in SEQ:
            print('usage: unknown tag %s' % a.stop_check)
            return 2
        before = [t for t, _ in CENSUS]
        before = before[:before.index(a.stop_check)] if a.stop_check in before else []
        oc = []
        for t in before:
            e = entry_of(t, root, pred_sha)
            if e is not None:
                oc.append((t, e['outcome'], e['key']))
            elif attempt_marker(t, root):
                oc.append((t, 'ATTEMPT_NO_JSON', None))
        stop, tags = stop_check(oc)
        print('STOP RULE before %s: %s' % (a.stop_check, ('STOP ' + ','.join(tags)) if stop else 'not met'))
        return 5 if stop else 0
    if a.tag:
        if a.tag not in SEQ:
            print('usage: unknown tag %s' % a.tag)
            return 2
        e = entry_of(a.tag, root, pred_sha)
        if e is None:
            if attempt_marker(a.tag, root):
                print('TAG %s: ATTEMPT MADE, NO JSON (instrument)' % a.tag)
            else:
                print('TAG %s: NO_RUN (no %s.json)' % (a.tag, a.tag))
            return 1
        print('\n'.join(fmt_entry(e)))
        os.makedirs(os.path.join(root, 'runs142'), exist_ok=True)
        dump = dict((k, v) for k, v in e.items() if k != 'derive')
        dump['derive'] = e['derive']
        json.dump(dump, open(os.path.join(root, 'runs142', '%s.score.json' % a.tag), 'w', encoding='utf-8'),
                  indent=1, default=list)
        return 0 if all(x[1] for x in e['admit']) else 1
    if a.summary:
        out, _, word = summary(root, pred_sha, a.sheet)
        print('\n'.join(out))
        return 0
    print('usage: sc142.py --tag T | --summary | --stop-check T | --check-seal | --calib | --check1b')
    return 2


if __name__ == '__main__':
    sys.exit(main())
