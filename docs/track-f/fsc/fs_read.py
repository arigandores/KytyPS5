"""fs_read.py - FSc (HPP-370), track F: the reading of one FSc tag and of the series - ROADMAP p.282(g)(3) (the regression of
the track F shipment binary), p.281(v)-(g) (the W form on the shipment binary, the mini_giants_garden pair), p.286(v) N1
(only the copy dac02fb9, sha256 before every tag), p.224 (validation active), p.221(v) (first scene frame), p.273(z) (window
event), p.258(d) (member of the executor [I]: printed on its own line, it does not set the verdict).

The s142 reading is NOT copied and NOT changed: sc142.py is imported from C:/kyty/s142 after its sha256 is checked (SC142_SHA;
another sha -> rc 2, no reading); only scan / derive / markers / validation / read_glitch / last_value and the constants
K2_US / SCENE_DRAWS are called.  Everything FSc adds is in this file.

  python fs_read.py --tag <tag> [--root <dir>] [--json <out.json>]
  python fs_read.py --stop-check <tag.read.json>     (one line: "continue: ..." or "stop: ...")
  python fs_read.py --summary [--root <dir>]         (the table of the series and the series verdict)
  python fs_read.py --check-seal <pred.md>

Tags (p.282(g)(3); the letters of the item are the suffixes: a = (a), b = (b), v = (v), g = (g), d = (d)); at the defaults - no
KYTY_FIX_* is passed, except fs_d (KYTY_FIX_B1B=0 exactly):
  fs_a  (a) W Sky Garden -lvl underwater_aerial_garden - the control W: --vulkan-validation true, precache by default
        (KYTY_PIPELINE_PRECACHE not set, p.281(g)), VK_LAYER_MESSAGE_ID_FILTER (F6) and VK_LAYER_DUPLICATE_MESSAGE_LIMIT as sc145;
        letter: a line 'DualSrcBlend: supported=1 enabled=1' before the first GuestOut line (positive control; none -> FAIL,
        p.281(g)), entered, sum dt after the first scene frame >= 300 s (wall 310 s), 0 [Vulkan][E], validation active by p.224
        (a member of admission), 0 layer limit lines
  fs_b  (b) V Sky Garden: sum dt >= 300 s (wall 330 s), video >= 3000 frames, s51_vidglitch.py 4 6 0 glitches, 0 death markers,
        0 frames >= 1 s (K2 after the first scene frame), 0 'BvhLoopCapTrip:' lines, the pair sheet "v142 / FSc" at the same
        frame numbers, mean dt - a number
  fs_v  (v) W mini_giants_garden - form (a) (the positive control, validation active, 0 layer limit lines), sum dt >= 310 s
        (the letter "> = 310 s"; the reading sum dt >= 300 s is printed beside as the variant of the executor), 0 [Vulkan][E],
        >= 1 line 'DualSrcBlend: patched ps=5514e10f1a60df83' (anywhere in the log; before / after the first GuestOut printed)
  fs_g  (g) V mini_giants_garden: wall >= 330 s (hold_s of the attempt in <tag>.json; the sum dt is printed beside), video
        >= 3000 frames, 0 glitches, 0 death markers, the pair sheet against f4c_g (p.281(v)(2))
  fs_d  (d) V Sky Garden KYTY_FIX_B1B=0 - information: sum dt >= 300 s, mean dt - a number; no verdict (INFO)
Hold shorter than named -> NOT EVALUABLE (a repeat only by a lead line); a window event (a 'Window <id> minimized' or
'Recovering Vulkan swapchain' line) -> WINDOW EVENT, a run disturbance, not an outcome (p.273(z)).
Order of the verdict: NOT ADMITTED -> INVALID (knob control: the line 'Shader translation cache:' ends with
variant_fixb26_fixb1b at the defaults, variant_fixb26 at KYTY_FIX_B1B=0) -> WINDOW EVENT -> FAIL (a letter member failed) ->
NOT EVALUABLE (not entered / no first scene frame / hold short) -> PASS (fs_d: INFO).
Members of the executor [I] (p.258(d)): death markers on W; scene change; hold_exit; BvhLoopCapTrip lines on a =1 tag other
than fs_b (a line reopens B1b, p.282(d) - a question to the lead); the precache lines; K2 / mean dt where the letter does not
name them; exactly one 'DualSrcBlend: supported=' line.
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
ROOT = 'C:/kyty/f287/fsc'
# the FSa copy (p.282(g)(3), p.286(b)-(v) N1): its sha256 is a member of admission
BIN_SHA = 'dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e'
SKY = 'underwater_aerial_garden'
MGG = 'mini_giants_garden'
VKFILTER = 'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering'
VKDUP = '1000000'
CHUNK = 1 << 26
FRAMES_V = 3000
PS1592 = '5514e10f1a60df83'
TAGS = {
    'fs_a': dict(level=SKY, letter='a', arm='W', knob=None, video=False, hold_sum=300, hold_wall=None, patched=False,
                 ref=None),
    'fs_b': dict(level=SKY, letter='b', arm='V', knob=None, video=True, hold_sum=300, hold_wall=None, patched=False,
                 ref='C:/kyty/s142/rec_v142.mp4'),
    'fs_v': dict(level=MGG, letter='v', arm='W', knob=None, video=False, hold_sum=310, hold_wall=None, patched=True,
                 ref=None),
    'fs_g': dict(level=MGG, letter='g', arm='V', knob=None, video=True, hold_sum=None, hold_wall=330, patched=False,
                 ref='C:/kyty/f287/f4c/rec_f4c_g.mp4'),
    'fs_d': dict(level=SKY, letter='d', arm='I', knob='0', video=False, hold_sum=300, hold_wall=None, patched=False,
                 ref=None),
}
SEQ = ('fs_a', 'fs_b', 'fs_v', 'fs_g', 'fs_d')
GATED = ('fs_a', 'fs_b', 'fs_v', 'fs_g')
CACHE_DIR = {None: 'variant_fixb26_fixb1b', '0': 'variant_fixb26'}
FIX_NAMES = ('KYTY_FIX_B26', 'KYTY_FIX_B1B', 'KYTY_FIX_DUALSRC', 'KYTY_FIX_MINIMIZE')
OTHER_ABSENT = ('KYTY_PIPELINE_PRECACHE', 'KYTY_GPU_CHECKPOINTS', 'KYTY_S_PCW', 'KYTY_PVAR', 'KYTY_TEST_MINIMIZE',
                'KYTY_GATE_SCHEDULE', 'KYTY_GATE_SCHEDULE_ABBA', 'KYTY_BVH_STUB', 'KYTY_BVH_LOOP_CAP', 'KYTY_SHADER_CACHE')
M_GUEST = b'GuestOut'
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d+) enabled=(\d+)')
M_DUAL = b'DualSrcBlend: supported='
M_PATCHED = b'DualSrcBlend: patched ps='
RX_PATCHED = re.compile(rb'DualSrcBlend: patched ps=([0-9a-f]+)')
M_PRE = b'PipelinePrecache:'
M_TCACHE = b'Shader translation cache:'
M_LIMIT = b'this will be the last time reporting it'
M_REC = b'Recovering Vulkan swapchain'
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
WIN_KEYS = ('minimized', 'restored', 'resized', 'size changed', 'lost keyboard focus')
PRE_MAX = 6


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


def scan_fs(path):
    """One streaming pass: the first GuestOut line, the DualSrcBlend lines, the precache lines, the translation cache lines,
    the window lines, the layer limit lines - with byte positions."""
    res = dict(guest=None, dual=[], patched=[], pre=[], tcache=[], win={k: 0 for k in WIN_KEYS}, recovering=0, limit=0)
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
            if res['guest'] is None:
                i = whole.find(M_GUEST)
                if i >= 0:
                    res['guest'] = base + whole.rfind(b'\n', 0, i) + 1
            for marker in (M_DUAL, M_PATCHED, M_PRE, M_TCACHE):
                i = whole.find(marker)
                while i >= 0:
                    s = whole.rfind(b'\n', 0, i) + 1
                    e = whole.find(b'\n', i)
                    e = len(whole) if e < 0 else e
                    line = whole[s:e]
                    pos = base + s
                    if marker is M_DUAL:
                        m = RX_DUAL.search(line)
                        res['dual'].append((pos, (int(m.group(1)), int(m.group(2))) if m else None))
                    elif marker is M_PATCHED:
                        m = RX_PATCHED.search(line)
                        res['patched'].append((pos, m.group(1).decode('ascii') if m else None))
                    elif marker is M_PRE:
                        res['pre'].append((pos, line[line.find(M_PRE):][:160].decode('ascii', 'replace').strip()))
                    else:
                        res['tcache'].append(line[line.find(M_TCACHE) + len(M_TCACHE):].strip().decode('latin1'))
                    i = whole.find(marker, e)
            for m in RX_WIN.finditer(whole):
                res['win'][m.group(1).decode()] += 1
            res['recovering'] += whole.count(M_REC)
            res['limit'] += whole.count(M_LIMIT)
            if not b:
                break
    return res


def knob_control(tcache, knob):
    """At least one 'Shader translation cache:' line and every line ends with the variant directory of the knobs."""
    want = CACHE_DIR[knob]
    ok = len(tcache) >= 1 and all(t.replace('/', '\\').rstrip('\\').split('\\')[-1] == want for t in tcache)
    return ok, want


def post_rows(sc142, log, d):
    """FrameTrace rows after the first scene frame (before a scene change) - the rows of the sum dt."""
    if d['entry_pos'] is None or d['first'] is None:
        return []
    cpos = d['change_pos']
    after = [r for r in log['rows'] if r[3] > d['entry_pos'] and (cpos is None or r[3] < cpos)]
    fi = next((i for i, r in enumerate(after) if r[2] >= sc142.SCENE_DRAWS), None)
    return after[fi + 1:] if fi is not None else []


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
    x = scan_fs(lp)
    xs = scan_fs(sp if os.path.isfile(sp) else None)
    w = cfg['arm'] == 'W'
    r = dict(tag=tag, cfg=cfg, log_sha=log['sha256'], binary=js.get('binary_sha256'))
    adm = []

    def add(name, ok, detail=''):
        adm.append((name, bool(ok), str(detail)))
    add('one attempt', len(js.get('attempts') or []) == 1, len(js.get('attempts') or []))
    add('guest args -lvl %s' % cfg['level'], js.get('guest_args') == '-lvl %s' % cfg['level'], js.get('guest_args'))
    add('binary sha256 = FSa copy dac02fb9 (p.286(v) N1)', js.get('binary_sha256') == BIN_SHA, (js.get('binary_sha256') or '')[:16])
    for k in FIX_NAMES:
        if k == 'KYTY_FIX_B1B' and cfg['knob'] is not None:
            add('KYTY_FIX_B1B=%s exactly (p.282(g)(3)(d))' % cfg['knob'], env.get(k) == cfg['knob'], repr(env.get(k)))
        else:
            add('%s not set (defaults, p.282(g)(3))' % k, k not in env, repr(env.get(k)))
    for k in OTHER_ABSENT:
        add('%s not set' % k, k not in env, repr(env.get(k)))
    add('KYTY_GPU_CLOCK_PIN=1', env.get('KYTY_GPU_CLOCK_PIN') == '1', env.get('KYTY_GPU_CLOCK_PIN'))
    rec = env.get('KYTY_REC')
    if cfg['video']:
        add('video KYTY_REC rec_%s.mp4' % tag, rec is not None and rec.replace('\\', '/').endswith('/rec_%s.mp4' % tag), rec)
    else:
        add('no video', rec is None, rec)
    vv = sc142.last_value(js.get('cmdline') or [], '--vulkan-validation')
    add('--vulkan-validation %s' % ('true' if w else 'false'), vv == ('true' if w else 'false'), vv)
    if w:
        add('VK_LAYER_MESSAGE_ID_FILTER=%s (F6, as sc145)' % VKFILTER, env.get('VK_LAYER_MESSAGE_ID_FILTER') == VKFILTER,
            env.get('VK_LAYER_MESSAGE_ID_FILTER'))
        add('VK_LAYER_DUPLICATE_MESSAGE_LIMIT=%s (as sc145)' % VKDUP, env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT') == VKDUP,
            env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT'))
        add('validation active (p.224: 0 no-layer, >= 1 validation_features, >= 1 [Vulkan][)', val['ok'],
            '%d/%d/%d' % (val['noval'], val['valfeat'], val['vkany']))
    else:
        add('no VK_LAYER_MESSAGE_ID_FILTER', 'VK_LAYER_MESSAGE_ID_FILTER' not in env, env.get('VK_LAYER_MESSAGE_ID_FILTER'))
    r['admit'] = adm
    r['admitted'] = all(ok for _, ok, _ in adm)
    kok, kwant = knob_control(x['tcache'], cfg['knob'])
    r['knob_ok'], r['knob_want'], r['tcache'] = kok, kwant, x['tcache'][:4]
    win = {k: x['win'][k] + xs['win'][k] for k in WIN_KEYS}
    r['win'] = win
    r['recovering'] = x['recovering'] + xs['recovering']
    r['winev'] = win['minimized'] > 0 or r['recovering'] > 0
    r['limit_lines'] = x['limit'] + xs['limit']
    r['guest_pos'] = x['guest']
    r['dual'] = [v for _, v in x['dual']]
    r['dual_pre'] = sum(1 for p, v in x['dual'] if v == (1, 1) and (x['guest'] is None or p < x['guest']))
    r['dual_ctl'] = x['guest'] is not None and r['dual_pre'] >= 1
    p1592 = [p for p, h in x['patched'] if h == PS1592]
    r['patched_1592'] = len(p1592)
    r['patched_1592_pre'] = sum(1 for p in p1592 if x['guest'] is None or p < x['guest'])
    r['patched_all'] = len(x['patched'])
    r['pre'] = [t for _, t in x['pre']][:PRE_MAX]
    r['pre_count'] = len(x['pre'])
    r['entered'] = d['entered']
    r['first'] = d['first']
    r['hold_sum_s'] = d['dt_after_first_us'] / 1e6
    r['hold_wall_s'] = at.get('hold_s')
    r['hold_exit'] = at.get('hold_exit')
    r['outcome'] = at.get('outcome')
    r['scene_change'] = d['change_pos'] is not None
    r['marks'] = [(m['kind'], m['cls'], m['src'], m['at_exit']) for m in marks]
    r['deaths'] = len(marks)
    r['k2'] = len(d['k2'])
    r['k2_list'] = d['k2'][:5]
    r['dt_max_us'] = d['dt_max_us']
    post = post_rows(sc142, log, d)
    r['mean_dt_us'] = (sum(q[1] for q in post) / len(post)) if post else None
    r['frames_after_first'] = len(post)
    r['trips'] = len(log['bvh'])
    r['vke'] = len(log['vke']) + (len(std['vke']) if std else 0)
    r['vke_first'] = [q[2] for q in (log['vke'] + (std['vke'] if std else []))[:1]]
    r['val'] = val
    r['skip_lines'] = log['skip_lines']
    g = sc142.read_glitch(os.path.join(root, 'glitch_%s.txt' % tag)) if cfg['video'] else None
    r['glitch'] = g
    sheet = os.path.join(root, 'sheetpair_%s.png' % tag)
    r['sheet_name'] = 'sheetpair_%s.png' % tag
    r['sheet'] = cfg['video'] and os.path.isfile(sheet) and os.path.getsize(sheet) > 0
    verdict(r)
    return r


def letter_members(r):
    """The members of p.282(g)(3) for the tag: list of (name, ok) - a failed member makes the tag FAIL."""
    cfg = r['cfg']
    t = cfg['letter']
    m = []
    if cfg['arm'] == 'W':
        m.append(('positive control: a line DualSrcBlend: supported=1 enabled=1 before the first GuestOut line (p.281(g))',
                  r['dual_ctl']))
        m.append(('0 [Vulkan][E] (log and stdout)', r['vke'] == 0))
        m.append(('0 layer limit lines "last time reporting it"', r['limit_lines'] == 0))
        if t == 'v':
            m.append(('>= 1 line DualSrcBlend: patched ps=%s' % PS1592, r['patched_1592'] >= 1))
    if t == 'b':
        g = r['glitch']
        m.append(('video >= %d frames' % FRAMES_V, g is not None and g['video_frames'] >= FRAMES_V))
        m.append(('s51_vidglitch.py 4 6: 0 glitches', g is not None and g['glitches'] == 0))
        m.append(('0 death markers', r['deaths'] == 0))
        m.append(('0 frames >= 1 s after the first scene frame', r['k2'] == 0))
        m.append(('0 BvhLoopCapTrip lines', r['trips'] == 0))
        m.append(('pair sheet v142 / FSc %s' % r['sheet_name'], r['sheet']))
    if t == 'g':
        g = r['glitch']
        m.append(('video >= %d frames' % FRAMES_V, g is not None and g['video_frames'] >= FRAMES_V))
        m.append(('s51_vidglitch.py 4 6: 0 glitches', g is not None and g['glitches'] == 0))
        m.append(('0 death markers', r['deaths'] == 0))
        m.append(('pair sheet f4c_g / FSc %s' % r['sheet_name'], r['sheet']))
    return m


def exec_members(r):
    """Members of the executor [I] (p.258(d)): (name, ok) - printed, they do not set the verdict."""
    cfg = r['cfg']
    m = []
    if cfg['arm'] == 'W':
        m.append(('0 death markers (W)', r['deaths'] == 0))
        m.append(('exactly one DualSrcBlend: supported= line', len(r['dual']) == 1))
        if cfg['letter'] == 'v':
            m.append(('sum dt >= 300 s (variant reading of "> = 310 s")', r['hold_sum_s'] >= 300))
    if cfg['knob'] is None and cfg['letter'] != 'b':
        m.append(('0 BvhLoopCapTrip lines (a line reopens B1b, p.282(d))', r['trips'] == 0))
    if cfg['letter'] in ('g', 'd', 'a', 'v'):
        m.append(('0 frames >= 1 s after the first scene frame (K2)', r['k2'] == 0))
    if cfg['letter'] == 'g':
        m.append(('sum dt after the first scene frame >= 330 s', r['hold_sum_s'] >= 330))
    m.append(('no scene change', not r['scene_change']))
    m.append(('game alive at the end of the hold (hold_exit None)', r['hold_exit'] is None))
    return m


def verdict(r):
    cfg = r['cfg']
    r['letter'] = letter_members(r)
    r['exec'] = exec_members(r)
    if not r['admitted']:
        r['verdict'], r['why'] = 'NOT ADMITTED', [n for n, ok, _ in r['admit'] if not ok]
        return
    if not r['knob_ok']:
        r['verdict'], r['why'] = 'INVALID', ['knob control: want %s, lines %s' % (r['knob_want'], r['tcache'])]
        return
    if r['winev']:
        r['verdict'], r['why'] = 'WINDOW EVENT', ['minimized %d, Recovering %d' % (r['win']['minimized'], r['recovering'])]
        return
    fail = [n for n, ok in r['letter'] if not ok]
    if fail:
        r['verdict'], r['why'] = 'FAIL', fail
        return
    if not r['entered'] or r['first'] is None:
        r['verdict'], r['why'] = 'NOT EVALUABLE', ['not entered or no first scene frame']
        return
    if cfg['hold_sum'] is not None and r['hold_sum_s'] < cfg['hold_sum']:
        r['verdict'], r['why'] = 'NOT EVALUABLE', ['hold sum dt %.1f s < %d s' % (r['hold_sum_s'], cfg['hold_sum'])]
        return
    if cfg['hold_wall'] is not None and (r['hold_wall_s'] is None or r['hold_wall_s'] < cfg['hold_wall']):
        r['verdict'], r['why'] = 'NOT EVALUABLE', ['hold wall %s s < %d s' % (r['hold_wall_s'], cfg['hold_wall'])]
        return
    r['verdict'] = 'INFO' if cfg['arm'] == 'I' else 'PASS'
    r['why'] = []


def stop_check(r):
    """The series stop after one tag: (a) not PASS -> stop (p.282(g)(3) "a stop of (a) - stop of the series"; variant of the
    executor: any outcome of the control W other than PASS, p.254(i)); NOT ADMITTED / INVALID / WINDOW EVENT -> stop; a death
    marker without a [Vulkan][E] line -> stop (first reproduction).  A validation stop of fs_v is data: 'continue: validation'."""
    if r is None:
        return 'stop: no reading (no log or no json)'
    if r['verdict'] in ('NOT ADMITTED', 'INVALID', 'WINDOW EVENT'):
        return 'stop: %s %s' % (r['verdict'], '; '.join(r['why'])[:200])
    if r['tag'] == 'fs_a' and r['verdict'] != 'PASS':
        return 'stop: control W fs_a %s (%s) - series stop, question to the lead' % (r['verdict'], '; '.join(r['why'])[:200])
    if r['deaths'] and not r['vke']:
        return 'stop: death markers %d %s' % (r['deaths'], r['marks'][:2])
    if r['vke']:
        return 'continue: validation stop or error is data (%d [Vulkan][E]) %s' % (r['vke'], r['verdict'])
    return 'continue: %s %s' % (r['verdict'], '; '.join(r['why'])[:200])


def text(r):
    cfg = r['cfg']
    L = ['fs_read tag %s (%s) level %s arm %s knob %s log sha256 %s binary %s' % (
        r['tag'], cfg['letter'], cfg['level'], cfg['arm'], 'KYTY_FIX_B1B=' + cfg['knob'] if cfg['knob'] else 'defaults',
        r['log_sha'], (r['binary'] or '')[:16])]
    for name, ok, det in r['admit']:
        L.append('admit %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    L.append('knob control: want %s, lines %s -> %s' % (r['knob_want'], r['tcache'], 'ok' if r['knob_ok'] else 'INVALID'))
    L.append('window lines: %s, Recovering Vulkan swapchain %d -> %s' % (
        ', '.join('%s %d' % (k, r['win'][k]) for k in WIN_KEYS), r['recovering'], 'WINDOW EVENT' if r['winev'] else 'none'))
    L.append('DualSrcBlend supported lines %s; supported=1 enabled=1 before the first GuestOut (byte %s): %d' % (
        r['dual'], r['guest_pos'], r['dual_pre']))
    L.append('DualSrcBlend patched lines %d; ps=%s %d (before the first GuestOut %d)' % (
        r['patched_all'], PS1592, r['patched_1592'], r['patched_1592_pre']))
    L.append('PipelinePrecache lines %d: %s' % (r['pre_count'], r['pre']))
    L.append('entered %s first scene frame %s scene change %s enter_scene outcome %s' % (
        r['entered'], r['first'], r['scene_change'], r['outcome']))
    L.append('hold: sum dt after the first scene frame %.1f s (named %s); wall hold_s %s (named %s); hold_exit %s' % (
        r['hold_sum_s'], cfg['hold_sum'], r['hold_wall_s'], cfg['hold_wall'], r['hold_exit']))
    L.append('death markers %d %s' % (r['deaths'], r['marks'][:4]))
    L.append('frames >= 1 s after the first scene frame %d %s; max dt_us %s; AsyncPipelines skipped draw lines %d' % (
        r['k2'], r['k2_list'], r['dt_max_us'], r['skip_lines']))
    L.append('BvhLoopCapTrip lines %d' % r['trips'])
    L.append('mean dt_us after the first scene frame (a number, not a gate): %s over %d frames' % (
        '%.1f' % r['mean_dt_us'] if r['mean_dt_us'] is not None else None, r['frames_after_first']))
    if cfg['arm'] == 'W':
        L.append('validation noval/valfeat/vkany %d/%d/%d active %s; [Vulkan][E] %d %s' % (
            r['val']['noval'], r['val']['valfeat'], r['val']['vkany'], r['val']['ok'], r['vke'],
            [v.encode('ascii', 'replace').decode() for v in r['vke_first']]))
        L.append('layer limit lines "last time reporting it" %d' % r['limit_lines'])
    if cfg['video']:
        g = r['glitch']
        L.append('video: frames %s glitches %s; %s %s (reference %s)' % (
            g['video_frames'] if g else None, g['glitches'] if g else None, r['sheet_name'], r['sheet'], cfg['ref']))
    for name, ok in r['letter']:
        L.append('letter p.282(g)(3)(%s) %-4s %s' % (cfg['letter'], 'ok' if ok else 'FAIL', name))
    for name, ok in r['exec']:
        L.append('executor member [I] (p.258(d)) %-4s %s' % ('ok' if ok else 'FAIL', name))
    L.append('FS VERDICT %s: %s%s' % (r['tag'], r['verdict'], (' (' + '; '.join(r['why']) + ')') if r['why'] else ''))
    bad = [n for n, ok in r['exec'] if not ok]
    L.append('FS EXECUTOR MEMBERS %s [I] (not the verdict): %s' % (
        r['tag'], 'all ok' if not bad else 'FAILED %s - question to the lead' % bad))
    return '\n'.join(L)


def summary(reads):
    """The series verdict of p.282(g)(3) from the per-tag reads (dict tag -> read or None): PASS when (a)-(g) are PASS; FAIL
    when any of them is FAIL; NOT EVALUABLE otherwise; (d) is information."""
    L = ['FS SERIES TABLE (p.282(g)(3); one attempt each; binary dac02fb9)']
    L.append('tag   level                     arm knob verdict        entered hold_sum wall   meandt   K2 deaths trips vke limit dual patched video/glitch')
    for t in SEQ:
        r = reads.get(t)
        c = TAGS[t]
        if r is None:
            L.append('%-5s %-25s %s   %-4s %-14s (not run or no reading)' % (t, c['level'], c['arm'], c['knob'] or '-', 'NO READING'))
            continue
        g = r.get('glitch')
        L.append('%-5s %-25s %s   %-4s %-14s %-7s %8.1f %6s %8s %4d %6d %5d %3d %5d %4d %7d %s' % (
            t, c['level'], c['arm'], c['knob'] or '-', r['verdict'], r['entered'], r['hold_sum_s'], r['hold_wall_s'],
            '%.0f' % r['mean_dt_us'] if r['mean_dt_us'] is not None else '-', r['k2'], r['deaths'], r['trips'], r['vke'],
            r['limit_lines'], r['dual_pre'], r['patched_1592'], ('%s/%s' % (g['video_frames'], g['glitches'])) if g else '-'))
    vs = {t: (reads[t]['verdict'] if reads.get(t) else 'NO READING') for t in SEQ}
    fails = [t for t in GATED if vs[t] == 'FAIL']
    nev = [t for t in GATED if vs[t] != 'PASS' and vs[t] != 'FAIL']
    word = 'FAIL' if fails else ('NOT EVALUABLE' if nev else 'PASS')
    L.append('(d) information: fs_d %s, sum dt %s s, mean dt_us %s' % (
        vs['fs_d'], '%.1f' % reads['fs_d']['hold_sum_s'] if reads.get('fs_d') else '-',
        '%.1f' % reads['fs_d']['mean_dt_us'] if reads.get('fs_d') and reads['fs_d']['mean_dt_us'] is not None else '-'))
    L.append('FS SERIES VERDICT p.282(g)(3): %s; FAIL tags %s; not PASS / not FAIL tags %s' % (
        word, ','.join(fails) or 'none', ','.join('%s=%s' % (t, vs[t]) for t in nev) or 'none'))
    return '\n'.join(L), word


SEALED = ('go_fs.sh', 'fs_read.py', 'win_fs.py', 'sheetpair_f3d.py', 'shalist_f2c.py', 'recipes143.py', 'test_fs_read.py',
          'test_go_fs.py', 'enter_scene.py', 'launch_run.py', 'run_safety99.py', 'idle142.py', 'procload.py', 'sheet142.py',
          'cachemf143.py', 'fgcpu143.py', 'gates_default.txt', SC142, 'C:/kyty/scripts/s51_vidglitch.py')
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
        print('usage: fs_read.py --tag %s [--root <dir>] [--json <out>] | --stop-check <json> | --summary | --check-seal <pred>'
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
