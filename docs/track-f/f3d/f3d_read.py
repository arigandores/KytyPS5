"""f3d_read.py - F3d (HPP-342), track F: the reading of one F3d tag and of the series - ROADMAP p.259(e)(4)-(6), p.277(b)
(RC1 of F3c), p.254(e) (form of W), p.224 (validation active), p.221(v) (first scene frame), p.258(d) (member of the executor).

The s142 reading is NOT copied and NOT changed: sc142.py is imported from C:/kyty/s142 after its sha256 is checked (SC142_SHA;
another sha -> rc 2, no reading); only scan / derive / markers / validation / read_glitch / last_value and the constants
K2_US / K3_US / ENTRY_WIN / SCENE_DRAWS are called.  Everything F3d adds is in this file: the fault pairs and low faults of
p.259(e)(4), the knob control by the line "Shader translation cache:" (p.277(b)(1)), the window events (item 273 (z)), the
layer limit lines, the arm verdicts and the series verdict of p.259(e)(4)-(6).

  python f3d_read.py --tag <tag> [--root <dir>] [--json <out.json>]
  python f3d_read.py --stop-check <tag.read.json>     (one line: "continue: ..." or "stop: ...")
  python f3d_read.py --summary [--root <dir>]         (the table of the series and the verdict of p.259(e)(4)-(6))
  python f3d_read.py --check-seal <pred.md>

Members of one tag (p.259(e)(4)-(5)):
  pairs     distinct fault pages of the lines "Accessed non-GPU cached memory at 0x<X>" (log); a pair = a page X >= 4 GiB
            (0x100000000) whose page (X >> 8) & ~0x3fff is also a fault page of the same log; =1: 0, =0: >= 1
  low       fault pages below 4 GiB; =1: 0 - every exception is a line with its address (the decision is the lead's at the
            acceptance: the tag verdict carries "LOW <n>, lead decision", it is not FAIL by itself)
  trips     lines "BvhLoopCapTrip:" (log); =1: 0
  deaths    death markers of sc142.markers (log, then stdout); 0 on every =1 entry
  K2        FrameTrace rows with dt_us >= 1 000 000 after the first scene frame (sc142.derive); 0 on every =1 entry
  hold      sum of dt_us of the shown frames after the first scene frame (p.221(v)); below the named hold -> NOT EVALUABLE
  K3 hold   rows >= 100 ms after the entry window (599 rows after the first scene frame), with their byte intervals -
            information (p.259(e)(5)(a))
  mean dt   mean dt_us of the rows after the first scene frame - a number, not a gate (p.259(e)(5)(b))
  video     s51_vidglitch.py 4 6 glitches (0) and the sheet; Sky Garden V: >= 3000 video frames, the pair sheet v142 / F3d
  W         p.254(e): --vulkan-validation true and KYTY_PIPELINE_PRECACHE=0; p.224: validation active by three signs;
            0 [Vulkan][E] (log and stdout)
Admission (p.277(b)(3)-(4)): one attempt, -lvl <level>, KYTY_FIX_B1B exactly '1' or '0' as the tag, KYTY_FIX_B26 not set,
KYTY_GPU_CLOCK_PIN=1, no KYTY_GPU_CHECKPOINTS, binary sha256 = the F3b copy 2e6df8f0.
Knob control (p.277(b)(1)): every "Shader translation cache:" line of the log ends with variant_fixb26_fixb1b (=1) or
variant_fixb26 (=0), at least one line; else the tag is INVALID (a run disturbance, a repeat only by a lead line).
Window event (item 273 (z)): a "Window <id> minimized" or "Recovering Vulkan swapchain" line -> WINDOW EVENT, not an outcome.
Output: ASCII only.  rc 0 - read; rc 1 - no log / no json; rc 2 - usage or a sha mismatch.
"""
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC142 = 'C:/kyty/s142/sc142.py'
SC142_SHA = '1ce612cdd036e2382ce5c5aae6bd25836062830dc0952da8512a9f2a74bb38c3'
ROOT = 'C:/kyty/f287/f3d'
BIN_SHA = '2e6df8f09f006ef8d49173bd4abccea074da94769c5c31b9caeeaadc3eaf74ae'
CHUNK = 1 << 26
BH = 'big_hand_pirate_island'
VW = 'voxel_world'
SKY = 'underwater_aerial_garden'
GIB4 = 0x100000000
PAGE = 0x4000
FRAMES_V = 3000
# kind: cold (only (4) and deaths/K2 count), warm (+ hold 120, video), skyv, skyw, ctl
TAGS = {
    'f3d_a1': dict(level=BH, fix='1', kind='cold', val=False, video=False, hold_s=None),
    'f3d_a2': dict(level=BH, fix='1', kind='warm', val=False, video=True, hold_s=120),
    'f3d_a3': dict(level=VW, fix='1', kind='cold', val=False, video=False, hold_s=None),
    'f3d_a4': dict(level=VW, fix='1', kind='warm', val=False, video=True, hold_s=120),
    'f3d_bv': dict(level=SKY, fix='1', kind='skyv', val=False, video=True, hold_s=300),
    'f3d_bw': dict(level=SKY, fix='1', kind='skyw', val=True, video=False, hold_s=300),
    'f3d_c1': dict(level=BH, fix='0', kind='ctl', val=False, video=False, hold_s=120),
    'f3d_c2': dict(level=VW, fix='0', kind='ctl', val=False, video=False, hold_s=120),
}
SEQ = ('f3d_a1', 'f3d_a2', 'f3d_a3', 'f3d_a4', 'f3d_bv', 'f3d_bw', 'f3d_c1', 'f3d_c2')
CACHE_DIR = {'1': 'variant_fixb26_fixb1b', '0': 'variant_fixb26'}
M_FAULT = b'Accessed non-GPU cached memory at '
RX_FAULT = re.compile(rb'Accessed non-GPU cached memory at (?:0x)?([0-9a-fA-F]+)')
M_TCACHE = b'Shader translation cache:'
M_LIMIT = b'this will be the last time reporting it'
M_REC = b'Recovering Vulkan swapchain'
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
WIN_KEYS = ('minimized', 'restored', 'resized', 'size changed', 'lost keyboard focus')


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load(path=SC142, want=SC142_SHA, name='sc142'):
    got = sha_file(path)
    if got != want:
        raise SystemExit('sha mismatch %s: %s != %s' % (path, got, want))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scan_extra(path):
    """One streaming pass: fault lines (address, byte position), translation cache lines, window lines, layer limit lines."""
    res = dict(faults=[], tcache=[], win={k: 0 for k in WIN_KEYS}, recovering=0, limit=0)
    if path is None or not os.path.isfile(path):
        return res
    off = 0
    tail = b''
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
            for m in RX_FAULT.finditer(whole):
                res['faults'].append((int(m.group(1), 16), base + m.start()))
            i = whole.find(M_TCACHE)
            while i >= 0:
                e = whole.find(b'\n', i)
                res['tcache'].append(whole[i + len(M_TCACHE):e if e >= 0 else len(whole)].strip().decode('latin1'))
                i = whole.find(M_TCACHE, i + 1)
            for m in RX_WIN.finditer(whole):
                k = m.group(1).decode()
                res['win'][k] += 1
            res['recovering'] += whole.count(M_REC)
            res['limit'] += whole.count(M_LIMIT)
            if not b:
                break
    return res


def fault_members(faults):
    """p.259(e)(4): distinct pages; pairs (X >= 4 GiB, (X >> 8) & ~0x3fff also faulted); low pages (< 4 GiB)."""
    pages = sorted(set(a for a, _ in faults))
    ps = set(pages)
    pairs = [(a, (a >> 8) & ~(PAGE - 1)) for a in pages if a >= GIB4 and ((a >> 8) & ~(PAGE - 1)) in ps]
    lows = [a for a in pages if a < GIB4]
    return pages, pairs, lows


def knob_control(tcache, fix):
    """p.277(b)(1): at least one line and every line ends with the variant directory of the knob value."""
    want = CACHE_DIR[fix]
    ok = len(tcache) >= 1 and all(t.replace('/', '\\').rstrip('\\').split('\\')[-1] == want for t in tcache)
    return ok, want


def hold_frames(sc142, log, d):
    """Rows >= K3_US after the entry window (before a scene change), each with its byte interval - information."""
    if d['entry_pos'] is None or d['first'] is None:
        return None
    cpos = d['change_pos']
    after = [r for r in log['rows'] if r[3] > d['entry_pos'] and (cpos is None or r[3] < cpos)]
    fi = next((i for i, r in enumerate(after) if r[2] >= sc142.SCENE_DRAWS), None)
    if fi is None:
        return None
    post = after[fi + 1:]
    return [dict(n=post[j][0], dt_us=post[j][1], lo=post[j - 1][3], hi=post[j][3], k2=post[j][1] >= sc142.K2_US)
            for j in range(sc142.ENTRY_WIN, len(post)) if post[j][1] >= sc142.K3_US]


def mean_dt(sc142, log, d):
    if d['entry_pos'] is None or d['first'] is None:
        return None
    cpos = d['change_pos']
    after = [r for r in log['rows'] if r[3] > d['entry_pos'] and (cpos is None or r[3] < cpos)]
    fi = next((i for i, r in enumerate(after) if r[2] >= sc142.SCENE_DRAWS), None)
    post = after[fi + 1:]
    return (sum(r[1] for r in post) / len(post)) if post else None


def read_tag(tag, root=ROOT, sc142=None):
    cfg = TAGS[tag]
    sc142 = sc142 or load()
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
    ex = scan_extra(lp)
    exs = scan_extra(sp if os.path.isfile(sp) else None)
    pages, pairs, lows = fault_members(ex['faults'])
    r = dict(tag=tag, cfg=cfg, log_sha=log['sha256'], binary=js.get('binary_sha256'))
    adm = []

    def add(name, ok, detail=''):
        adm.append((name, bool(ok), str(detail)))
    add('one attempt', len(js.get('attempts') or []) == 1, len(js.get('attempts') or []))
    add('guest args -lvl %s' % cfg['level'], js.get('guest_args') == '-lvl %s' % cfg['level'], js.get('guest_args'))
    add('KYTY_FIX_B1B=%s exactly (p.277(b)(3))' % cfg['fix'], env.get('KYTY_FIX_B1B') == cfg['fix'], repr(env.get('KYTY_FIX_B1B')))
    add('KYTY_FIX_B26 not set (default, p.277(b)(1))', 'KYTY_FIX_B26' not in env, repr(env.get('KYTY_FIX_B26')))
    add('binary sha256 = F3b copy 2e6df8f0 (p.277(b)(4))', js.get('binary_sha256') == BIN_SHA, (js.get('binary_sha256') or '')[:16])
    add('KYTY_GPU_CLOCK_PIN=1', env.get('KYTY_GPU_CLOCK_PIN') == '1', env.get('KYTY_GPU_CLOCK_PIN'))
    add('no KYTY_GPU_CHECKPOINTS', 'KYTY_GPU_CHECKPOINTS' not in env, '')
    pc = env.get('KYTY_PIPELINE_PRECACHE')
    add('KYTY_PIPELINE_PRECACHE %s' % ('=0 (p.254(e))' if cfg['val'] else 'not set'),
        pc == '0' if cfg['val'] else pc is None, repr(pc))
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
    kok, kwant = knob_control(ex['tcache'], cfg['fix'])
    r['knob_ok'], r['knob_want'], r['tcache'] = kok, kwant, ex['tcache'][:4]
    win = {k: ex['win'][k] + exs['win'][k] for k in WIN_KEYS}
    r['win'] = win
    r['recovering'] = ex['recovering'] + exs['recovering']
    r['winev'] = win['minimized'] > 0 or r['recovering'] > 0
    r['limit_lines'] = ex['limit'] + exs['limit']
    r['pages'] = ['0x%x' % a for a in pages]
    r['pairs'] = [('0x%x' % a, '0x%x' % b) for a, b in pairs]
    r['lows'] = ['0x%x' % a for a in lows]
    r['fault_lines'] = len(ex['faults'])
    r['trips'] = len(log['bvh'])
    r['entered'] = d['entered']
    r['first'] = d['first']
    r['hold_s'] = d['dt_after_first_us'] / 1e6
    r['hold_s_json'] = at.get('hold_s')
    r['hold_exit'] = at.get('hold_exit')
    r['scene_change'] = d['change_pos'] is not None
    r['marks'] = [(m['kind'], m['cls'], m['src'], m['at_exit']) for m in marks]
    r['deaths'] = len(marks)
    r['k2'] = len(d['k2'])
    r['k3_window'] = len(d['k3w'])
    r['hold_frames'] = hold_frames(sc142, log, d)
    r['mean_dt_us'] = mean_dt(sc142, log, d)
    r['vke'] = len(log['vke']) + (len(std['vke']) if std else 0)
    r['vke_first'] = [x[2] for x in (log['vke'] + (std['vke'] if std else []))[:2]]
    r['val'] = val
    r['skip_lines'] = log['skip_lines']
    g = sc142.read_glitch(os.path.join(root, 'glitch_%s.txt' % tag)) if cfg['video'] else None
    r['glitch'] = g
    sheet = 'sheetpair_%s.png' % tag if cfg['kind'] == 'skyv' else 'sheet_%s.png' % tag
    r['sheet_name'] = sheet
    r['sheet'] = cfg['video'] and os.path.isfile(os.path.join(root, sheet)) and os.path.getsize(os.path.join(root, sheet)) > 0
    verdict(r)
    return r


def verdict(r):
    """The arm verdict of p.259(e)(4)-(5) and p.277(b) (fields of r -> r['verdict'], r['why'])."""
    cfg = r['cfg']
    why = []
    if not r['admitted']:
        r['verdict'], r['why'] = 'NOT ADMITTED', [n for n, ok, _ in r['admit'] if not ok]
        return
    if not r['knob_ok']:
        r['verdict'], r['why'] = 'INVALID', ['knob control: want %s, lines %s' % (r['knob_want'], r['tcache'])]
        return
    if r['winev']:
        r['verdict'], r['why'] = 'WINDOW EVENT', ['minimized %d, Recovering %d' % (r['win']['minimized'], r['recovering'])]
        return
    fail = []
    if r['deaths']:
        fail.append('death markers %d' % r['deaths'])
    if cfg['fix'] == '1':
        if r['k2']:
            fail.append('K2 %d' % r['k2'])
        if r['pairs']:
            fail.append('pairs %d' % len(r['pairs']))
        if r['trips']:
            fail.append('BvhLoopCapTrip %d' % r['trips'])
        if r['scene_change']:
            fail.append('scene change')
        if cfg['video']:
            g = r['glitch']
            if g is None:
                fail.append('no glitch reading')
            elif g['glitches'] != 0:
                fail.append('glitches %d' % g['glitches'])
            if not r['sheet']:
                fail.append('no sheet %s' % r['sheet_name'])
            if cfg['kind'] == 'skyv' and (g is None or g['video_frames'] < FRAMES_V):
                fail.append('video frames %s < %d' % (g['video_frames'] if g else None, FRAMES_V))
        if cfg['val']:
            if r['vke']:
                fail.append('[Vulkan][E] %d' % r['vke'])
    else:
        if not r['pairs']:
            fail.append('pairs 0 (control does not return)')
    if fail:
        r['verdict'], r['why'] = 'FAIL', fail
        return
    if not r['entered'] or r['first'] is None:
        r['verdict'], r['why'] = 'NOT EVALUABLE', ['not entered or no first scene frame']
        return
    if cfg['hold_s'] is not None and r['hold_s'] < cfg['hold_s']:
        r['verdict'], r['why'] = 'NOT EVALUABLE', ['hold %.1f s < %d s' % (r['hold_s'], cfg['hold_s'])]
        return
    if r['hold_exit'] is not None:
        why.append('hold_exit %s (information)' % r['hold_exit'])
    if cfg['fix'] == '1' and r['lows']:
        r['verdict'] = 'PASS EXCEPT LOW'
        why.append('low fault pages %d, lead decision: %s' % (len(r['lows']), ', '.join(r['lows'])))
    else:
        r['verdict'] = 'CONTROL RETURNS' if cfg['fix'] == '0' else 'PASS'
    r['why'] = why


def stop_check(r):
    """The harness rule: stop the series on a not admitted / invalid / window-event tag or on a death marker (stop on the first
    reproduction; the question goes to the lead).  Everything else is data: continue."""
    if r is None:
        return 'stop: no reading (no log or no json)'
    if r['verdict'] in ('NOT ADMITTED', 'INVALID', 'WINDOW EVENT'):
        return 'stop: %s %s' % (r['verdict'], '; '.join(r['why'])[:200])
    if r['deaths']:
        return 'stop: death markers %d %s' % (r['deaths'], r['marks'][:2])
    return 'continue: %s %s' % (r['verdict'], '; '.join(r['why'])[:200])


def text(r):
    cfg = r['cfg']
    L = ['f3d_read tag %s level %s KYTY_FIX_B1B=%s kind %s log sha256 %s binary %s' % (
        r['tag'], cfg['level'], cfg['fix'], cfg['kind'], r['log_sha'], (r['binary'] or '')[:16])]
    for name, ok, det in r['admit']:
        L.append('admit %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    L.append('knob control (p.277(b)(1)): want %s, lines %s -> %s' % (r['knob_want'], r['tcache'], 'ok' if r['knob_ok'] else 'INVALID'))
    L.append('window lines: %s, Recovering Vulkan swapchain %d -> %s' % (
        ', '.join('%s %d' % (k, r['win'][k]) for k in WIN_KEYS), r['recovering'], 'WINDOW EVENT' if r['winev'] else 'none'))
    L.append('entered %s first scene frame %s scene change %s' % (r['entered'], r['first'], r['scene_change']))
    L.append('hold: sum dt after first scene frame %.1f s (named %s), json hold_s %s, hold_exit %s' % (
        r['hold_s'], cfg['hold_s'], r['hold_s_json'], r['hold_exit']))
    L.append('(4) fault lines %d, distinct pages %d: %s' % (r['fault_lines'], len(r['pages']), ', '.join(r['pages'][:12])))
    L.append('(4) pairs X >= 4 GiB with (X >> 8) & ~0x3fff faulted: %d %s' % (len(r['pairs']), r['pairs'][:6]))
    L.append('(4) low fault pages (< 4 GiB): %d' % len(r['lows']))
    for a in r['lows']:
        L.append('  low fault page %s' % a)
    L.append('(4) BvhLoopCapTrip lines: %d' % r['trips'])
    L.append('death markers %d %s' % (r['deaths'], r['marks'][:4]))
    L.append('K2 frames after the first scene frame %d; K3 in the entry window %d; AsyncPipelines skipped draw lines %d' % (
        r['k2'], r['k3_window'], r['skip_lines']))
    hf = r['hold_frames']
    if hf is None:
        L.append('hold frames >= 100 ms: not evaluable (no entry or no first scene frame)')
    else:
        L.append('hold frames >= 100 ms after the entry window (information): %d' % len(hf))
        for x in hf[:40]:
            L.append('  frame n=%d dt_us=%d %s interval [%d,%d]' % (x['n'], x['dt_us'], 'K2' if x['k2'] else 'K3', x['lo'], x['hi']))
    L.append('mean dt_us after the first scene frame (a number, not a gate): %s' % (
        '%.1f' % r['mean_dt_us'] if r['mean_dt_us'] is not None else None))
    if cfg['val']:
        L.append('validation noval/valfeat/vkany %d/%d/%d active %s; [Vulkan][E] %d %s' % (
            r['val']['noval'], r['val']['valfeat'], r['val']['vkany'], r['val']['ok'], r['vke'], r['vke_first'][:1]))
        L.append('member of the executor [I] (p.258(d)): layer limit lines "last time reporting it" %d' % r['limit_lines'])
    if cfg['video']:
        g = r['glitch']
        L.append('video: frames %s glitches %s sheet %s %s' % (g['video_frames'] if g else None, g['glitches'] if g else None,
                                                            r['sheet_name'], r['sheet']))
    L.append('F3D VERDICT %s: %s%s' % (r['tag'], r['verdict'], (' (' + '; '.join(r['why']) + ')') if r['why'] else ''))
    return '\n'.join(L)


def summary(reads):
    """The series verdict of p.259(e)(4)-(6) from the per-tag reads (dict tag -> read or None)."""
    L = ['F3D SERIES TABLE (p.259(e)(5); one attempt each)']
    L.append('tag     level                     fix kind verdict          pairs low trips deaths K2 hold_s  meandt  K3hold video/glitch')
    for t in SEQ:
        r = reads.get(t)
        if r is None:
            L.append('%-7s %-25s %s   %-4s %-16s (not run or no reading)' % (t, TAGS[t]['level'], TAGS[t]['fix'], TAGS[t]['kind'], 'NO READING'))
            continue
        g = r.get('glitch')
        L.append('%-7s %-25s %s   %-4s %-16s %5d %3d %5d %6d %2d %7.1f %7s %6s %s' % (
            t, r['cfg']['level'], r['cfg']['fix'], r['cfg']['kind'], r['verdict'], len(r['pairs']), len(r['lows']), r['trips'],
            r['deaths'], r['k2'], r['hold_s'], '%.0f' % r['mean_dt_us'] if r['mean_dt_us'] else '-',
            len(r['hold_frames']) if r['hold_frames'] is not None else '-',
            ('%s/%s' % (g['video_frames'], g['glitches'])) if g else '-'))
    one = [t for t in SEQ if TAGS[t]['fix'] == '1']
    a = [t for t in SEQ if TAGS[t]['kind'] in ('cold', 'warm')]
    ctl = [t for t in SEQ if TAGS[t]['fix'] == '0']
    bad = ('NO READING', 'NOT ADMITTED', 'INVALID', 'WINDOW EVENT', 'NOT EVALUABLE')
    vs = {t: (reads[t]['verdict'] if reads.get(t) else 'NO READING') for t in SEQ}
    fails = [t for t in SEQ if vs[t] == 'FAIL']
    nev = [t for t in SEQ if vs[t] in bad]
    lowx = [t for t in one if vs[t] == 'PASS EXCEPT LOW']
    no_trip = sum(1 for t in a if reads.get(t) and vs[t] not in bad and reads[t]['trips'] == 0)
    L.append('(4) pairs on the six =1 entries: %s' % ', '.join('%s %s' % (t, len(reads[t]['pairs']) if reads.get(t) else '-') for t in one))
    L.append('(4) pairs on the =0 controls: %s' % ', '.join('%s %s' % (t, len(reads[t]['pairs']) if reads.get(t) else '-') for t in ctl))
    L.append('(6) =1 entries of (a) without a BvhLoopCapTrip line: %d of 4 (N >= 4)' % no_trip)
    L.append('(6) =1 entries of (a) with 0 pairs: %d of 4 (N >= 2 per level)' % sum(
        1 for t in a if reads.get(t) and vs[t] not in bad and not reads[t]['pairs']))
    if fails:
        word = 'FAIL'
    elif nev:
        word = 'NOT EVALUABLE'
    elif lowx:
        word = 'PASS EXCEPT LOW (lead decision on the low pages)'
    else:
        word = 'PASS'
    L.append('F3D SERIES VERDICT p.259(e)(4)-(6): %s; FAIL tags %s; not evaluable/invalid tags %s; low-page tags %s' % (
        word, ','.join(fails) or 'none', ','.join('%s=%s' % (t, vs[t]) for t in nev) or 'none', ','.join(lowx) or 'none'))
    return '\n'.join(L), word


SEALED = ('go_f3d.sh', 'f3d_read.py', 'win_f3d.py', 'sheetpair_f3d.py', 'shalist_f2c.py', 'test_f3d_read.py', 'test_go_f3d.py',
          'enter_scene.py', 'launch_run.py', 'run_safety99.py', 'idle142.py', 'procload.py', 'sheet142.py', 'cachemf143.py',
          'fgcpu143.py', 'gates_default.txt', SC142, 'C:/kyty/scripts/s51_vidglitch.py')
RX_SEAL = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)$')


def check_seal(pred, root=ROOT, names=SEALED):
    """Every 'seal: <sha256> <path>' line must match the file now (a path without 'C:/' is under root), and every name of
    SEALED must have exactly one line.  Returns (ok, lines)."""
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


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    root = a[a.index('--root') + 1] if '--root' in a and a.index('--root') + 1 < len(a) else ROOT
    if '--check-seal' in a and a.index('--check-seal') + 1 < len(a):
        ok, lines = check_seal(a[a.index('--check-seal') + 1], root)
        print('\n'.join(lines))
        print('check-seal %s' % ('OK' if ok else 'FAILED'))
        return 0 if ok else 1
    if '--stop-check' in a and a.index('--stop-check') + 1 < len(a):
        p = a[a.index('--stop-check') + 1]
        r = None
        if os.path.isfile(p):
            with open(p, encoding='ascii') as f:
                r = json.load(f)
        print(stop_check(r))
        return 0
    if '--summary' in a:
        try:
            sc = load()
        except SystemExit as e:
            print('refused: %s' % e)
            return 2
        reads = {t: read_tag(t, root, sc) for t in SEQ}
        txt, _ = summary(reads)
        print(txt)
        return 0
    if '--tag' not in a or a.index('--tag') + 1 >= len(a) or a[a.index('--tag') + 1] not in TAGS:
        print('usage: f3d_read.py --tag %s [--root <dir>] [--json <out>] | --stop-check <json> | --summary | --check-seal <pred>'
              % '|'.join(SEQ))
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
