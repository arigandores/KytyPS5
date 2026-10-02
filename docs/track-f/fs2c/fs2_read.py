"""fs2_read.py - FS2c (HPP-383), track F: the reading of one FS2c tag and of the series - ROADMAP "SESSION 122" p.298(g)(1)-(4)
(regression of the second track F shipment binary FS2 at the defaults), p.273(e)(3)(a), (b), (v) (the letters of B37), p.295(b)(1)-(4)
(form W), p.296(b), (d) (the stop by the letter; a member naming a reference log carries a fixture on it), p.300(b)(4) and p.281(g)
(precache by default, DualSrcBlend line), p.327(g)(1)-(3) (members of B9a), p.287(v)(5) and p.294(b) (members of an =1 entry of
timestop_casino), p.306(g) B1 (I10), p.273(z) (window event outside the stand - a disturbance of the run), p.258(d) (member of the
executor [I]: printed on its own line, it does not set the verdict).

Nothing earlier is copied or changed: sc142.py (C:/kyty/s142), f5c_read.py (C:/kyty/f287/f5c) and f6e_read.py (C:/kyty/f287/f6e) are
imported after their sha256 is checked (another sha -> rc 2, no reading); from sc142 - scan / derive / markers / validation /
read_glitch / last_value and K2_US / K3_US / ENTRY_WIN / SCENE_DRAWS; from f5c_read - scan_f5c / Clock / read_idx / read_glitch_list /
video_part (the stand, the episode, the window of p.278(v), the video members of (v)); from f6e_read - scan_f6e / stub_profile /
first_scene_pos / frequency / wake / k3_within / rips (the members of p.287(v)(5)).  Everything FS2c adds is in this file.

  python fs2_read.py --tag fs2_w|fs2_w0|fs2_v|fs2_t|fs2_tr [--root <dir>] [--json <out.json>]
  python fs2_read.py --stop-check <tag.read.json>   (one line: 'continue: ...', 'repeat-k3: fs2_tr ...' or 'stop: ...')
  python fs2_read.py --summary [--root <dir>]       (the table of the series and the verdict of p.298(g) + p.327(g)(3))
  python fs2_read.py --check-seal <pred.md>
  python fs2_read.py --stop-rule <log> [<log> ...]  (the stop rule of p.298(g)(2) on any log - the reference fixture of p.296(d))

Tags (one attempt each; the copy bbad499c of the FS2 binary; no KYTY_FIX_* in the env except fs2_w0):
  fs2_w   (g)(1) W Sky Garden at the defaults, precache by default, form W of p.295(b), stand KYTY_TEST_MINIMIZE=60:10:
          letter (a) of p.273(e)(3) + 'DualSrcBlend: supported=1 enabled=1' + 'FixMinimize: on' + members of B9a (1)
  fs2_w0  (g)(2) the same with KYTY_FIX_MINIMIZE=0: STOP | NO STOP by the stop rule
  fs2_v   (g)(3) V Sky Garden at the defaults with the stand, no validation, video: letter (v) of p.273(e)(3) + members of B9a (1)
  fs2_t   p.327(g)(2) timestop_casino at the defaults, no validation, precache by default, form V of F6e (video, FrameTrace, sum dt
          after the first scene frame >= 120 s): members of p.287(v)(5) for =1 verbatim and p.294(b), 'FixB9a: on' exactly 1,
          K3 hold limit 1; over the limit -> one repeat fs2_tr ("the repeat decides"; it never lifts the other members)
  fs2_tw  the warm-up of timestop_casino (60 s, no video) is NOT read here - the harness stops on rc != 0, death or window lines.
THE STOP RULE (p.298(g)(2), letter): a line '[Vulkan][E]' carrying 'imageExtent (width = 0, height = 0)' after the line
  'TestMinimize: minimize', and 'VUID-VkSwapchainCreateInfoKHR-imageExtent-01689' in the same line or in one of the 3 lines after it.
  Anchor: the first 'TestMinimize: minimize' line; a log WITHOUT any stand line (the reference log_w144_09.txt: the window was
  minimized from outside, there is no stand) is anchored at its first 'Window 1 minimized' line - reading of the executor [I], named
  in the seal: the letter names log_w144_09.txt as a reference that must give STOP (p.298(g)(2), p.296(d)); on fs2_w0 itself the
  stand control demands exactly one 'TestMinimize: minimize' line, so the anchor there is the letter's.
B9a MEMBERS (p.327(g)(1), fs2_w and fs2_v): 'FixB9a: on' exactly 1 (a mismatch is a form error of the tag: INVALID); 'ASSERT:' 0 in
  the log and in the stdout; 'user_msg_param' 0 (the log, p.294(b) - the stdout count is a member of the executor [I]); lines
  'Unresolved import stub called' carrying '[AudioPropagation_v1]' 0 (the log, p.294(v) - the stdout count: member of the executor
  [I]); the last 'AudioPropagation: calls' line - information.
fs2_t user_msg_param: p.294(b) compares with "the control =0 of the same level of this series"; FS2c has no control (p.327(g)(2): "the
  control =0 is not assigned in FS2c") - the limit is UMSG_T = 0: the control f6e_c1 of the F6e series 2 has 0 lines [c] and the base
  of the witnesses is 0 (p.294(a)); both readings give 0.
WINDOW EVENT (p.273(z)): stand tags - a line 'Window <id> minimized' or 'Recovering Vulkan swapchain' outside the stand window (from
  'TestMinimize: minimize' to max(restore, SwapchainZeroExtent: end) + 2 s of the log clock; no restore -> the end of the log) is a
  disturbance of the run: NOT EVALUABLE, series stop; timestop tags - any such line: WINDOW EVENT, series stop.
Order of the verdict: NOT ADMITTED (run form, form W p.295(b)) -> INVALID (FixB9a: on count) -> NOT EVALUABLE (controls of the stand
  and of the arm, window event outside the stand) / WINDOW EVENT (fs2_t) -> the letter.
Output: ASCII only.  rc 0 - read; rc 1 - no log / no json; rc 2 - usage or a sha mismatch.
"""
import hashlib
import importlib.util
import json
import os
import re
import sys

ROOT = 'C:/kyty/f287/fs2c'
SC142 = 'C:/kyty/s142/sc142.py'
SC142_SHA = '1ce612cdd036e2382ce5c5aae6bd25836062830dc0952da8512a9f2a74bb38c3'
F5C = 'C:/kyty/f287/f5c/f5c_read.py'
F5C_SHA = '0cc8b3cdef53acd66a270a83d50bde9c409f339c5e7d3115ecb9cd51c6fc18fe'
F6E = 'C:/kyty/f287/f6e/f6e_read.py'
F6E_SHA = '27a5cc0337419d02b29f67cab444415a1951fe2847b6307eae904d67d19d809b'
# the FS2 binary (FS2a 9c9d86ae, accepted p.329(a)): its sha256 is a member of admission
BIN_SHA = 'bbad499c56b744dfcef85b7556735c025ebb3db185b6bb9b02e7a0b3a228eb55'
SKY = 'underwater_aerial_garden'
TC = 'timestop_casino'
CHUNK = 1 << 26
STAND = '60:10'
STAND_DELAY = 60.0
STAND_DUR = 10.0
VKLAYER = 'C:/VulkanSDK/1.4.357.0/Bin'
W_FORM_LINE = 'W form: limit=100000000 filter=none'
LAYER_END_US = 10000000              # p.295(b)(3): 10 s
FRAMES_V = 3000
ROWS_AFTER_RESTORE = 1000
LATE_S = 2.0
WIN_AFTER_S = 2.0
HOLD_T = 120
K3_T = 1                             # p.327(g)(2): the K3 hold limit of fs2_t
UMSG_T = 0                           # p.294(b) with no control in FS2c - see the header
FREQ_MAX = 0.1                       # p.287(v)(5)
VUID_NEXT = 3                        # p.298(g)(2): the same line or one of the 3 next
TAGS = {
    'fs2_w': dict(level=SKY, kind='W', val=True, video=False, stand=True, fixenv={}, hold_s=310, letter='a'),
    'fs2_w0': dict(level=SKY, kind='W', val=True, video=False, stand=True, fixenv={'KYTY_FIX_MINIMIZE': '0'}, hold_s=0, letter='b'),
    'fs2_v': dict(level=SKY, kind='V', val=False, video=True, stand=True, fixenv={}, hold_s=330, letter='v'),
    'fs2_t': dict(level=TC, kind='T', val=False, video=True, stand=False, fixenv={}, hold_s=HOLD_T, letter='t'),
    'fs2_tr': dict(level=TC, kind='T', val=False, video=True, stand=False, fixenv={}, hold_s=HOLD_T, letter='t'),
}
SEQ = ('fs2_w', 'fs2_w0', 'fs2_v', 'fs2_t', 'fs2_tr')
OTHER_ABSENT = ('KYTY_PIPELINE_PRECACHE', 'KYTY_GPU_CHECKPOINTS', 'KYTY_PRINT_NAMES', 'KYTY_S_PCW', 'KYTY_PVAR', 'KYTY_GATE_SCHEDULE',
                'KYTY_GATE_SCHEDULE_ABBA', 'KYTY_BVH_STUB', 'KYTY_BVH_LOOP_CAP', 'KYTY_BVH_NATIVE', 'KYTY_SHADER_CACHE')
M_VKE = b'[Vulkan][E]'
M_EXTENT = b'imageExtent (width = 0, height = 0)'
VUID = b'VUID-VkSwapchainCreateInfoKHR-imageExtent-01689'
M_MIN = b'TestMinimize: minimize'
M_WIN1MIN = b'Window 1 minimized'
M_LIMIT = b'last time reporting it'
M_GUEST = b'GuestOut'
M_FIXMIN = b'FixMinimize: on'
M_FIXB9A = b'FixB9a: on'
M_ASSERT = b'ASSERT:'
M_UMSG = b'user_msg_param'
M_STUBCALL = b'Unresolved import stub called'
M_AP = b'[AudioPropagation_v1]'
M_CALLS = b'AudioPropagation: calls'
M_REC = b'Recovering Vulkan swapchain'
RX_VK2 = re.compile(rb'\[Vulkan\]\[[WE]\]\[2\]')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d+) enabled=(\d+)')
RX_MINW = re.compile(rb'Window \d+ minimized')
RX_WALL = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
REPORT = 1 << 16


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


class Mods:
    def __init__(self):
        self.sc = load(SC142, SC142_SHA, 'sc142')
        self.f5 = load(F5C, F5C_SHA, 'f5c_read')
        self.f6 = load(F6E, F6E_SHA, 'f6e_read')


def _lines(whole, marker):
    i = whole.find(marker)
    while i >= 0:
        s = whole.rfind(b'\n', 0, i) + 1
        e = whole.find(b'\n', i)
        e = len(whole) if e < 0 else e
        yield s, e
        i = whole.find(marker, e)


def scan_fs2(path):
    """One streaming pass: the FS2c lines with byte positions (validation-layer lines, layer limit lines, [Vulkan][E] lines with
    the zero extent, DualSrcBlend, the first GuestOut, FixMinimize / FixB9a, ASSERT:, user_msg_param, AudioPropagation stub lines,
    the counter lines, minimized / Recovering / other window lines)."""
    res = dict(vk2=0, vk2_last=None, limit=0, vke=0, extent=[], dual=[], guest=None, minimize=None, win1min=None, fixmin=0,
               fixb9a=0, asserts=0, umsg=0, apstub=0, calls=0, calls_last=None, minw=[], rec=[], win={}, bytes=0)
    if path is None or not os.path.isfile(path):
        return None
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
            for m in RX_VK2.finditer(whole):
                res['vk2'] += 1
                res['vk2_last'] = base + m.start()
            res['limit'] += whole.count(M_LIMIT)
            res['vke'] += whole.count(M_VKE)
            for s, e in _lines(whole, M_VKE):
                if M_EXTENT in whole[s:e]:
                    res['extent'].append(base + s)
            for m in RX_DUAL.finditer(whole):
                res['dual'].append((base + m.start(), int(m.group(1)), int(m.group(2))))
            if res['guest'] is None:
                i = whole.find(M_GUEST)
                if i >= 0:
                    res['guest'] = base + whole.rfind(b'\n', 0, i) + 1
            if res['minimize'] is None:
                i = whole.find(M_MIN)
                if i >= 0:
                    res['minimize'] = base + whole.rfind(b'\n', 0, i) + 1
            if res['win1min'] is None:
                i = whole.find(M_WIN1MIN)
                if i >= 0:
                    res['win1min'] = base + whole.rfind(b'\n', 0, i) + 1
            res['fixmin'] += whole.count(M_FIXMIN)
            res['fixb9a'] += whole.count(M_FIXB9A)
            res['asserts'] += whole.count(M_ASSERT)
            res['umsg'] += whole.count(M_UMSG)
            for s, e in _lines(whole, M_STUBCALL):
                if M_AP in whole[s:e]:
                    res['apstub'] += 1
            for s, e in _lines(whole, M_CALLS):
                res['calls'] += 1
                res['calls_last'] = whole[s:e][:300].decode('ascii', 'replace')
            for m in RX_MINW.finditer(whole):
                res['minw'].append(base + m.start())
            for s, e in _lines(whole, M_REC):
                res['rec'].append(base + s)
            for m in RX_WALL.finditer(whole):
                k = m.group(1).decode()
                res['win'][k] = res['win'].get(k, 0) + 1
            if not b:
                break
    res['bytes'] = off
    return res


def vuid_near(path, positions):
    """For each '[Vulkan][E]' zero-extent line position: the index (0 = the same line, 1..3 = the next lines) of the first line
    carrying VUID 01689 within VUID_NEXT lines, or None."""
    out = []
    with open(path, 'rb') as f:
        for pos in positions:
            f.seek(pos)
            lines = f.read(REPORT).split(b'\n')[:1 + VUID_NEXT]
            k = next((j for j, ln in enumerate(lines) if VUID in ln), None)
            out.append((pos, k))
    return out


def stop_rule(path, x=None):
    """p.298(g)(2): dict(stop, anchor, anchor_kind, extent_after, vuid) on one log (x - its scan_fs2, made when None)."""
    x = x or scan_fs2(path)
    if x is None:
        return dict(stop=False, anchor=None, anchor_kind='no log', extent_after=[], vuid=[])
    if x['minimize'] is not None:
        anchor, kind = x['minimize'], 'TestMinimize: minimize (letter)'
    elif x['win1min'] is not None:
        anchor, kind = x['win1min'], 'Window 1 minimized (no stand line in the log - reading of the executor [I])'
    else:
        anchor, kind = None, 'none'
    after = [p for p in x['extent'] if anchor is not None and p > anchor]
    vu = vuid_near(path, after) if after else []
    return dict(stop=any(k is not None for _, k in vu), anchor=anchor, anchor_kind=kind, extent_after=after, vuid=vu)


def layer_end(rows, vk2_last, entry_pos, change_pos):
    """p.295(b)(3) (the method of sc146 layer_end): the presented time (us) from the last validation-layer line of the log to the
    last FrameTrace row of the hold - the sum of dt_us of the hold rows after its byte position; None without such a line, without
    the entry line or without a hold row."""
    if vk2_last is None or entry_pos is None:
        return None
    hold = [r for r in rows if r[3] > entry_pos and (change_pos is None or r[3] < change_pos)]
    if not hold:
        return None
    return sum(r[1] for r in hold if r[3] > vk2_last)


def w_form4(env):
    """p.295(b)(4): (ok, the form line built from the json env)."""
    fl = env.get('VK_LAYER_MESSAGE_ID_FILTER')
    fm = 'W form: limit=%s filter=%s' % (env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT'), 'none' if fl is None else fl)
    return fm == W_FORM_LINE and 'VK_LAYER_MESSAGE_ID_FILTER' not in env, fm


def paths_of(tag, root, paths=None):
    p = dict(log=os.path.join(root, 'log_%s.txt' % tag), stdout=os.path.join(root, 'stdout_%s.txt' % tag),
             json=os.path.join(root, '%s.json' % tag), glitch=os.path.join(root, 'glitch_%s.txt' % tag),
             sheet=os.path.join(root, 'sheet_%s.png' % tag), idx=os.path.join(root, 'rec_%s.mp4.idx' % tag))
    p.update(paths or {})
    return p


def read_tag(tag, root=ROOT, mods=None, paths=None):
    cfg = TAGS.get(tag)
    if cfg is None:
        return None
    P = paths_of(tag, root, paths)
    if not os.path.isfile(P['log']) or not os.path.isfile(P['json']):
        return None
    m = mods or Mods()
    sc, f5, f6 = m.sc, m.f5, m.f6
    with open(P['json'], encoding='utf-8') as f:
        js = json.load(f)
    at = (js.get('attempts') or [{}])[0]
    env = js.get('env') or {}
    sp = P['stdout'] if os.path.isfile(P['stdout']) else None
    log = sc.scan(P['log'])
    std = sc.scan(sp) if sp else None
    d = sc.derive(log, cfg['level'])
    marks = sc.markers(log, std, d['entry_pos'], log['quit'])
    val = sc.validation(log, std)
    x = scan_fs2(P['log'])
    xs = scan_fs2(sp)
    e6 = f6.scan_f6e(P['log'])
    clock = f5.Clock(log['rows'])
    r = dict(tag=tag, cfg=cfg, log_sha=log['sha256'], binary=js.get('binary_sha256'))
    adm = []

    def add(name, ok, detail=''):
        adm.append((name, bool(ok), str(detail)))
    add('one attempt', len(js.get('attempts') or []) == 1, len(js.get('attempts') or []))
    add('binary sha256 = FS2 copy bbad499c (p.298(g), p.329(a))', js.get('binary_sha256') == BIN_SHA, (js.get('binary_sha256') or '')[:16])
    add('guest args -lvl %s' % cfg['level'], js.get('guest_args') == '-lvl %s' % cfg['level'], js.get('guest_args'))
    fixes = dict((k, v) for k, v in env.items() if k.startswith('KYTY_FIX_'))
    add('KYTY_FIX_* in the env = %s exactly (p.298(g)(1): none at the defaults)' % (cfg['fixenv'] or '{}'), fixes == cfg['fixenv'], fixes)
    if cfg['stand']:
        add('KYTY_TEST_MINIMIZE=%s exactly' % STAND, env.get('KYTY_TEST_MINIMIZE') == STAND, repr(env.get('KYTY_TEST_MINIMIZE')))
    else:
        add('KYTY_TEST_MINIMIZE not set', 'KYTY_TEST_MINIMIZE' not in env, repr(env.get('KYTY_TEST_MINIMIZE')))
    for k in OTHER_ABSENT:
        add('%s not set%s' % (k, ' (precache by default, p.281(g), p.300(b)(4))' if k == 'KYTY_PIPELINE_PRECACHE' else ''),
            k not in env, repr(env.get(k)))
    add('KYTY_GPU_CLOCK_PIN=1', env.get('KYTY_GPU_CLOCK_PIN') == '1', env.get('KYTY_GPU_CLOCK_PIN'))
    rec = env.get('KYTY_REC')
    if cfg['video']:
        add('video KYTY_REC rec_%s.mp4' % tag, rec is not None and rec.replace('\\', '/').endswith('/rec_%s.mp4' % tag), rec)
    else:
        add('no video', rec is None, rec)
    vv = sc.last_value(js.get('cmdline') or [], '--vulkan-validation')
    add('--vulkan-validation %s' % ('true' if cfg['val'] else 'false'), vv == ('true' if cfg['val'] else 'false'), vv)
    add('precache by default (I10, p.306(g) B1): >= 1 "PipelinePrecache: <N> recipes ->" OR (>= 1 "PipelinePrecache: no <variant '
        'dir>\\pipelines.bin yet" AND >= 1 "PipelinePrecache: saved <N> recipes") in the log',
        e6['pre'] >= 1 or (e6['pre_no'] >= 1 and e6['pre_saved'] >= 1),
        'recipes-> %d, no-variant %d, saved %d' % (e6['pre'], e6['pre_no'], e6['pre_saved']))
    held = None
    if cfg['kind'] == 'W':
        add('VK_LAYER_PATH = %s' % VKLAYER, env.get('VK_LAYER_PATH') == VKLAYER, env.get('VK_LAYER_PATH'))
        ok4, fm = w_form4(env)
        add('W 295(b)(4) the form line "%s" from the json env, no VK_LAYER_MESSAGE_ID_FILTER key' % W_FORM_LINE, ok4, fm)
        add('validation active (p.224: 0 no-layer, >= 1 validation_features, >= 1 [Vulkan][)', val['ok'],
            '%d/%d/%d' % (val['noval'], val['valfeat'], val['vkany']))
        held = bool(marks) is False and at.get('hold_exit') is None and at.get('outcome') == 'ok' and not log['ended']
        le = layer_end(log['rows'], x['vk2_last'], d['entry_pos'], d['change_pos'])
        limit = x['limit'] + (xs['limit'] if xs else 0)
        vk2 = x['vk2'] + (xs['vk2'] if xs else 0)
        r['layer_end_us'] = le
        r['limit'] = limit
        r['vk2'] = vk2
        if held:
            add('W 295(b)(1) 0 layer limit lines (log and stdout)', limit == 0, limit)
            add('W 295(b)(2) validation active: >= 1 validation-layer line [Vulkan][W][2] / [Vulkan][E][2] (log and stdout)', vk2 >= 1, vk2)
            add('W 295(b)(3) the last validation-layer line of the log at most 10 s of presented time before the last FrameTrace '
                'row of the hold', le is not None and le <= LAYER_END_US, 'none' if le is None else '%d us' % le)
        else:
            for name in ('W 295(b)(1)', 'W 295(b)(2)', 'W 295(b)(3)'):
                add('%s - n/a (W not held: marks %d, hold_exit %s, outcome %s; read on a held W, p.295(b))' % (
                    name, len(marks), at.get('hold_exit'), at.get('outcome')), True, 'n/a')
    r['held'] = held
    r['admit'] = adm
    r['admitted'] = all(ok for _, ok, _ in adm)
    # B9a and default lines (p.327(g)(1), p.298(g)(1))
    r['fixb9a'] = x['fixb9a']
    r['fixmin'] = x['fixmin']
    r['asserts_log'], r['asserts_std'] = x['asserts'], (xs['asserts'] if xs else 0)
    r['umsg_log'], r['umsg_std'] = x['umsg'], (xs['umsg'] if xs else 0)
    r['apstub_log'], r['apstub_std'] = x['apstub'], (xs['apstub'] if xs else 0)
    r['calls'], r['calls_last'] = x['calls'], x['calls_last']
    r['dual'] = [(p, s, e) for p, s, e in x['dual']]
    r['guest'] = x['guest']
    r['dual_ok'] = bool(x['dual']) and all(s == 1 and e == 1 for _, s, e in x['dual']) and x['guest'] is not None \
        and x['dual'][0][0] < x['guest']
    r['form_ok'] = x['fixb9a'] == 1 if cfg['letter'] in ('a', 'v', 't') else True
    r['vke'] = len(log['vke']) + (len(std['vke']) if std else 0)
    r['entered'] = d['entered']
    r['first'] = d['first']
    r['scene_change'] = d['change_pos'] is not None
    r['marks'] = [(mk['kind'], mk['cls'], mk['src'], mk['at_exit'], mk['pos']) for mk in marks]
    r['deaths'] = len(marks)
    r['hold_s_json'] = at.get('hold_s')
    r['hold_exit'] = at.get('hold_exit')
    r['outcome'] = at.get('outcome')
    r['dt_after_first_s'] = d['dt_after_first_us'] / 1e6
    r['win'] = x['win']
    r['minw'] = len(x['minw'])
    r['recovering'] = len(x['rec'])
    r['minw_std'] = len(xs['minw']) if xs else 0
    r['recovering_std'] = len(xs['rec']) if xs else 0
    r['skip_lines'] = log['skip_lines']
    g = sc.read_glitch(P['glitch'])
    r['glitch'] = g
    r['sheet'] = os.path.isfile(P['sheet']) and os.path.getsize(P['sheet']) > 0
    r['exec_members'] = []
    if cfg['kind'] == 'T':
        read_t(r, cfg, log, std, d, marks, e6, sc, f6)
    else:
        read_stand(r, cfg, log, d, x, xs, clock, P, sc, f5)
    r['exec_ok'] = all(ok for _, ok, _ in r['exec_members'])
    return r


def read_stand(r, cfg, log, d, x, xs, clock, P, sc, f5):
    """fs2_w, fs2_w0, fs2_v: the stand and arm controls of F5c (f5c_read.read_tag, same names), the window event outside the stand,
    the letter."""
    y = f5.scan_f5c(P['log'])
    con = []

    def kadd(name, ok, detail=''):
        con.append((name, bool(ok), str(detail)))

    def cadd(name, ok, detail=''):
        r['exec_members'].append((name, bool(ok), str(detail)))
    cfgs = [c for _, c in y['cfg']]
    kadd('exactly one line TestMinimize: config on delay_s=60.000 dur_s=10.000',
         len(cfgs) == 1 and cfgs[0] is not None and cfgs[0][0] == 'on' and abs(cfgs[0][1] - STAND_DELAY) < 1e-6
         and abs(cfgs[0][2] - STAND_DUR) < 1e-6, cfgs)
    kadd('exactly one line TestMinimize: armed', len(y['armed']) == 1, len(y['armed']))
    ap = y['armed'][0] if len(y['armed']) == 1 else None
    starts_before = [(n, p) for n, p in log['starts'] if ap is not None and p < ap]
    st = starts_before[-1] if starts_before else None
    kadd('N2 p.285(v): the start line before armed carries the level name %s (not blank)' % cfg['level'],
         st is not None and st[0] == cfg['level'], st)
    kadd('exactly one line TestMinimize: minimize, after armed', len(y['minimize']) == 1 and ap is not None and y['minimize'][0] > ap,
         (len(y['minimize']), y['minimize'][:1], ap))
    mpos = y['minimize'][0] if len(y['minimize']) == 1 else None
    if cfg['letter'] in ('a', 'v'):
        kadd('exactly one line TestMinimize: restore, after minimize', len(y['restore']) == 1 and mpos is not None
             and y['restore'][0] > mpos, (len(y['restore']), y['restore'][:1]))
    rpos = y['restore'][0] if len(y['restore']) == 1 else None
    if cfg['letter'] == 'v':
        kadd('FixMinimize: on lines = 1 (positive control of the default, arm V)', x['fixmin'] == 1, x['fixmin'])
    elif cfg['letter'] == 'b':
        kadd('FixMinimize: on lines = 0 (arm KYTY_FIX_MINIMIZE=0)', x['fixmin'] == 0, x['fixmin'])
        kadd('no SwapchainZeroExtent line at =0', not y['begin'] and not y['end'], (len(y['begin']), len(y['end'])))
    kadd('>= 1 line Window 1 minimized (the stand reached the window)', len(y['win1_min']) >= 1, len(y['win1_min']))
    first_pos = None
    if d['first'] is not None:
        for row in log['rows']:
            if row[0] == d['first'][0] and d['entry_pos'] is not None and row[3] > d['entry_pos']:
                first_pos = row[3]
                break
    r['first_pos'] = first_pos
    kadd('the first scene frame lies before TestMinimize: minimize', first_pos is not None and mpos is not None and first_pos < mpos,
         (first_pos, mpos))
    # the episode (f5c_read) and the stand window
    bpos = y['begin'][0] if y['begin'] else None
    epos = eval_ = None
    for p, v in y['end']:
        if bpos is not None and p > bpos:
            epos, eval_ = p, v
            break
    r['episode'] = dict(begin=len(y['begin']), end=len(y['end']), begin_pos=bpos, end_pos=epos, end_val=eval_)
    tt = dict(armed=clock.at(ap) if ap is not None else None, minimize=clock.at(mpos) if mpos is not None else None,
              restore=clock.at(rpos) if rpos is not None else None, begin=clock.at(bpos) if bpos is not None else None,
              end=clock.at(epos) if epos is not None else None, total=clock.cum[-1] / 1e6 if clock.cum else 0.0)
    r['t'] = tt
    late_log = late_ms = None
    if epos is not None and rpos is not None:
        late_log = (tt['end'] - tt['restore']) > LATE_S
    if eval_ is not None and tt['minimize'] is not None and tt['begin'] is not None:
        late_ms = (tt['begin'] - tt['minimize']) * 1000.0 + eval_[1] > (STAND_DUR + LATE_S) * 1000.0
    r['late_log'], r['late_ms'] = late_log, late_ms
    r['rows_after_restore'] = clock.rows_between(rpos, 1 << 62) if rpos is not None else 0
    # the stand window of p.273(z): minimize .. max(restore, end) + 2 s; no restore -> to the end of the log
    last = max([p for p in (rpos, epos) if p is not None], default=None)
    sw_end = clock.pos_after(last, WIN_AFTER_S) if last is not None else None
    sw_end = sw_end if sw_end is not None else (1 << 62)
    out_ev = [('minimized', p) for p in x['minw'] if mpos is None or not (mpos <= p <= sw_end)] + \
             [('Recovering', p) for p in x['rec'] if mpos is None or not (mpos <= p <= sw_end)]
    r['window_out'] = out_ev
    kadd('no window event outside the stand window (p.273(z): Window <id> minimized / Recovering Vulkan swapchain outside '
         'minimize .. max(restore, end) + 2 s)', not out_ev, out_ev[:4])
    r['controls'] = con
    r['controls_ok'] = all(ok for _, ok, _ in con)
    # the window of p.278(v) for deaths and K2: minimize .. end + 2 s (f5c_read)
    wend = clock.pos_after(epos, WIN_AFTER_S) if epos is not None else None
    wend = wend if wend is not None else (1 << 62)

    def inwin(pos):
        return mpos is not None and mpos <= pos <= wend
    r['deaths_out'] = [mk for mk in r['marks'] if not (mk[2] == 'log' and inwin(mk[4]))]
    k2 = []
    if first_pos is not None:
        for row in log['rows']:
            if row[3] > first_pos and (d['change_pos'] is None or row[3] < d['change_pos']) and row[1] >= sc.K2_US:
                k2.append((row[0], row[1], 'window' if inwin(row[3]) else 'outside'))
    r['k2'] = k2
    r['k2_out'] = sum(1 for _, _, w in k2 if w == 'outside')
    r['video'] = None
    hold_v = r['dt_after_first_s'] >= cfg['hold_s']
    L = cfg['letter']
    b9 = b9a_members(r)
    r['b9a'] = b9
    if L == 'a':
        parts = dict(entered=d['entered'], no_scene_change=not r['scene_change'], no_hold_exit=r['hold_exit'] is None,
                     one_window1_minimized=len(y['win1_min']) == 1, begin_end=bpos is not None and epos is not None,
                     vke0=r['vke'] == 0, deaths0=r['deaths'] == 0, hold=hold_v,
                     rows_after_restore=r['rows_after_restore'] >= ROWS_AFTER_RESTORE, end_not_late=late_log is False,
                     dualsrcblend_1_1=r['dual_ok'], fixminimize_on=x['fixmin'] == 1)
        parts.update(b9)
        cadd('exactly one begin and one end line', len(y['begin']) == 1 and len(y['end']) == 1, (len(y['begin']), len(y['end'])))
    elif L == 'b':
        sr = stop_rule(P['log'], x)
        r['stop_rule'] = sr
        ended = r['hold_exit'] is not None or r['outcome'] == 'exited' or bool(r['marks'])
        cadd('the emulator ended after the stop line (hold_exit / exited / a death marker)', ended,
             (r['hold_exit'], r['outcome'], len(r['marks'])))
        parts = dict(stop_rule=sr['stop'])
    else:
        idx = f5.read_idx(P['idx'])
        if idx:
            r['video'] = f5.video_part(log['rows'], idx, f5.read_glitch_list(P['glitch']), mpos, epos, clock)
        vd = r['video']
        g = r['glitch']
        parts = dict(entered=d['entered'], no_scene_change=not r['scene_change'], no_hold_exit=r['hold_exit'] is None,
                     hold=hold_v, video_frames=g is not None and g['video_frames'] >= FRAMES_V, sheet=r['sheet'],
                     glitches_outside0=vd is not None and not vd['glitches_out_anchored'],
                     n1_present_order_after_end=vd is not None and epos is not None and vd['after_end_records'] > 0
                     and not vd['after_end_bad'],
                     no_k1k2_outside=not r['deaths_out'] and r['k2_out'] == 0,
                     begin_end=bpos is not None and epos is not None, end_not_late=late_log is False)
        parts.update(b9)
        if vd is not None:
            cadd('the two video windows agree (anchored vs idx gap)', len(vd['glitches_out_anchored']) == len(vd['glitches_out_gap']),
                 (len(vd['glitches_out_anchored']), len(vd['glitches_out_gap'])))
    if L in ('a', 'v'):
        cadd('stdout: user_msg_param 0 and AudioPropagation stub lines 0', r['umsg_std'] == 0 and r['apstub_std'] == 0,
             (r['umsg_std'], r['apstub_std']))
        cadd('end later than restore + 2 s: the log clock and the ms= reading agree', late_log is None or late_ms is None
             or late_log == late_ms, (late_log, late_ms))
    r['parts'] = parts
    if L == 'b':
        r['verdict'] = 'STOP' if parts['stop_rule'] else 'NO STOP'
    else:
        r['verdict'] = 'PASS' if all(parts.values()) else 'FAIL'
    r['why'] = [k for k, v in parts.items() if not v]
    if not r['admitted']:
        r['verdict'], r['why'] = 'NOT ADMITTED', [n for n, ok, _ in r['admit'] if not ok]
    elif not r['form_ok']:
        r['verdict'], r['why'] = 'INVALID', ['FixB9a: on lines %d, want 1 (p.327(g)(1): a form error of the tag)' % r['fixb9a']]
    elif not r['controls_ok']:
        r['verdict'], r['why'] = 'NOT EVALUABLE', [n for n, ok, _ in con if not ok]


def b9a_members(r):
    """p.327(g)(1): the members of B9a on fs2_w and fs2_v (FixB9a: on is the form - INVALID before the letter)."""
    return dict(b9a_assert0_log_stdout=r['asserts_log'] == 0 and r['asserts_std'] == 0, b9a_user_msg_param0=r['umsg_log'] == 0,
                b9a_audiopropagation_stub_lines0=r['apstub_log'] == 0)


def read_t(r, cfg, log, std, d, marks, e6, sc, f6):
    """fs2_t, fs2_tr: the members of p.287(v)(5) for =1 (mechanism on timestop_casino), p.294(b), FixB9a: on 1, K3 limit 1."""
    def cadd(name, ok, detail=''):
        r['exec_members'].append((name, bool(ok), str(detail)))
    r['controls'] = []
    r['controls_ok'] = True
    r['winev'] = r['minw'] + r['minw_std'] > 0 or r['recovering'] + r['recovering_std'] > 0
    by_sym, by_lib, ap = f6.stub_profile(e6['stubs'])
    r['stub_lines'] = e6['stub_lines']
    r['stub_ap'] = ap
    r['stub_std'] = 0
    fpos = f6.first_scene_pos(sc, log, d)
    w120 = f6.k3_within(sc, log, d, fpos)
    r['k2'] = len(d['k2'])
    r['k3_window'] = len(d['k3w'])
    r['k3_hold'] = len(d['k3h'])
    r['k3_hold_rows'] = d['k3h'][:20]
    r['k3_hold120'] = None if w120 is None else len(w120)
    fr = f6.frequency(log['rows'], e6['calls'], fpos, d['change_pos'])
    r['freq'] = fr
    wk, last = f6.wake(e6['calls'])
    r['wake'], r['last_calls'] = wk, last
    r['rips'] = f6.rips(marks)
    post = [q for q in log['rows'] if fpos is not None and q[3] > fpos and (d['change_pos'] is None or q[3] < d['change_pos'])]
    r['mean_dt_us'] = (sum(q[1] for q in post) / len(post)) if post else None
    cadd('stdout: user_msg_param 0 and AudioPropagation stub lines 0', r['umsg_std'] == 0 and r['apstub_std'] == 0,
         (r['umsg_std'], r['apstub_std']))
    fail = []
    if r['stub_lines']:
        fail.append('stub lines %d' % r['stub_lines'])
    if r['deaths']:
        fail.append('death markers %d' % r['deaths'])
    if r['k2']:
        fail.append('K2 %d' % r['k2'])
    if r['scene_change']:
        fail.append('scene change')
    g = r['glitch']
    if g is None:
        fail.append('no glitch reading')
    else:
        if g['glitches'] != 0:
            fail.append('glitches %d' % g['glitches'])
        if g['video_frames'] < FRAMES_V:
            fail.append('video frames %d < %d' % (g['video_frames'], FRAMES_V))
    if not r['sheet']:
        fail.append('no sheet sheet_%s.png' % r['tag'])
    if r['asserts_log'] or r['asserts_std']:
        fail.append('ASSERT: lines log %d stdout %d (p.294(b))' % (r['asserts_log'], r['asserts_std']))
    if r['umsg_log'] > UMSG_T:
        fail.append('user_msg_param %d > %d (p.294(b))' % (r['umsg_log'], UMSG_T))
    fq = fr['freq']
    if fq is not None and fq >= FREQ_MAX:
        fail.append('SourceCreate per frame %.4f >= %.1f' % (fq, FREQ_MAX))
    if not wk:
        fail.append('wake control: SourceSetAttributes and SourceRender 0 on the last counter line (%s)' % last)
    r['k3_over'] = r['k3_hold'] > K3_T
    if not r['admitted']:
        r['verdict'], r['why'] = 'NOT ADMITTED', [n for n, ok, _ in r['admit'] if not ok]
    elif not r['form_ok']:
        r['verdict'], r['why'] = 'INVALID', ['FixB9a: on lines %d, want 1 (p.327(g)(2))' % r['fixb9a']]
    elif r['winev']:
        r['verdict'], r['why'] = 'WINDOW EVENT', ['minimized %d, Recovering %d' % (r['minw'], r['recovering'])]
    elif fail:
        r['verdict'], r['why'] = 'FAIL', fail
    elif not r['entered'] or r['first'] is None:
        r['verdict'], r['why'] = 'NOT EVALUABLE', ['not entered or no first scene frame']
    elif r['dt_after_first_s'] < HOLD_T:
        r['verdict'], r['why'] = 'NOT EVALUABLE', ['hold %.1f s < %d s' % (r['dt_after_first_s'], HOLD_T)]
    elif fq is None:
        r['verdict'], r['why'] = 'NOT EVALUABLE', ['frequency not evaluable by the letter (%s)' % (fr['var'] or 'no counter lines')]
    elif r['k3_over']:
        r['verdict'], r['why'] = 'K3 OVER', ['K3 hold %d > limit %d - one repeat fs2_tr decides (p.287(v)(5), p.327(g)(2))' % (
            r['k3_hold'], K3_T)]
    else:
        r['verdict'], r['why'] = 'PASS', []


def stop_check(r):
    """The series stop of go_fs2.sh after one tag: 'continue ...', 'repeat-k3: fs2_tr ...' or 'stop ...'."""
    if r is None:
        return 'stop: no reading (no log or no json)'
    v = r.get('verdict')
    if v in ('NOT ADMITTED', 'NOT EVALUABLE', 'INVALID', 'WINDOW EVENT'):
        return 'stop: %s %s %s - question to the lead' % (r.get('tag'), v, '; '.join(str(w) for w in r.get('why') or [])[:200])
    if r.get('tag') == 'fs2_w0':
        return 'continue: data (b) %s' % v
    if r.get('deaths', 0) > 0 and r.get('vke', 0) == 0:
        return 'stop: death marker without a [Vulkan][E] line (%s) - question to the lead' % (r.get('marks') or [])[:1]
    if r.get('tag') == 'fs2_t' and v == 'K3 OVER':
        return 'repeat-k3: fs2_tr (%s)' % '; '.join(r.get('why') or [])[:200]
    if r.get('vke', 0) > 0:
        return 'continue: validation [Vulkan][E] %d - %s %s' % (r['vke'], r.get('tag'), v)
    return 'continue: %s %s' % (r.get('tag'), v)


def judge_t(reads):
    """p.327(g)(2): the timestop member - fs2_t, or its K3 repeat fs2_tr ("the repeat decides"; it never lifts other members)."""
    t, tr = reads.get('fs2_t'), reads.get('fs2_tr')
    if t is None:
        return 'NO READING', ['fs2_t not run or no reading']
    if t['verdict'] == 'PASS':
        return 'PASS', []
    if t['verdict'] != 'K3 OVER':
        return t['verdict'], t['why']
    if tr is None:
        return 'REPEAT DUE', ['fs2_t K3 %d > %d, fs2_tr not run' % (t['k3_hold'], K3_T)]
    if tr['verdict'] == 'PASS':
        return 'PASS', ['fs2_t K3 %d > %d, the repeat decides: fs2_tr K3 %d' % (t['k3_hold'], K3_T, tr['k3_hold'])]
    if tr['verdict'] == 'K3 OVER':
        return 'FAIL', ['K3 fs2_t %d and fs2_tr %d > limit %d' % (t['k3_hold'], tr['k3_hold'], K3_T)]
    return tr['verdict'], ['repeat fs2_tr: %s' % '; '.join(tr['why'])]


def b9a_one(w, v):
    """p.327(g)(1) over fs2_w and fs2_v: FAIL when a read, admitted tag of a right form fails a B9a member; PASS when both are read,
    admitted, of a right form and all members hold; else NOT EVALUABLE (no reading, not admitted, INVALID form - question)."""
    rs = [r for r in (w, v) if r is not None and r['admitted'] and r['form_ok']]
    if any(not all(r['b9a'].values()) for r in rs):
        return 'FAIL'
    if len(rs) == 2:
        return 'PASS'
    return 'NOT EVALUABLE'


def summary(reads):
    L = ['FS2 SERIES TABLE (p.298(g)(1)-(4), p.327(g)(1)-(3); one attempt each; fs2_tr only when fs2_t is K3 OVER)']
    L.append('tag     level                     verdict        hold_s  vke deaths K2  FixMin FixB9a ASSERT(l/s) umsg(l/s) APstub(l/s) Dual video/glitch')
    for t in SEQ:
        r = reads.get(t)
        if r is None:
            L.append('%-7s %-25s %s' % (t, TAGS[t]['level'], 'NO READING (not run or no log)'))
            continue
        g = r.get('glitch')
        k2 = len(r['k2']) if isinstance(r.get('k2'), list) else r.get('k2')
        L.append('%-7s %-25s %-14s %6.1f %4d %6d %3s %6d %6d %5d/%-5d %4d/%-4d %5d/%-5d %4s %s' % (
            t, r['cfg']['level'], r['verdict'], r['dt_after_first_s'], r['vke'], r['deaths'], k2, r['fixmin'], r['fixb9a'],
            r['asserts_log'], r['asserts_std'], r['umsg_log'], r['umsg_std'], r['apstub_log'], r['apstub_std'],
            'ok' if r['dual_ok'] else 'no', ('%s/%s' % (g['video_frames'], g['glitches'])) if g else '-'))
    w, w0, v = reads.get('fs2_w'), reads.get('fs2_w0'), reads.get('fs2_v')
    tst, twhy = judge_t(reads)
    L.append('(1) fs2_w: %s%s' % (w['verdict'] if w else 'NO READING', (' - ' + '; '.join(map(str, w['why']))) if w and w['why'] else ''))
    L.append('(2) fs2_w0: %s%s' % (w0['verdict'] if w0 else 'NO READING',
                                    (' (anchor %s; extent lines after it %d; vuid %s)' % (w0['stop_rule']['anchor_kind'],
                                                                                         len(w0['stop_rule']['extent_after']),
                                                                                         w0['stop_rule']['vuid'][:2]))
                                    if w0 and w0.get('stop_rule') else ''))
    L.append('(3) fs2_v: %s%s' % (v['verdict'] if v else 'NO READING', (' - ' + '; '.join(map(str, v['why']))) if v and v['why'] else ''))
    L.append('(4) p.327(g)(2) timestop_casino (fs2_t / fs2_tr): %s%s' % (tst, (' - ' + '; '.join(twhy)) if twhy else ''))
    b9_1 = b9a_one(w, v)
    b9_2 = tst if tst in ('PASS', 'FAIL') else 'NOT EVALUABLE'
    b9 = 'PASS' if b9_1 == 'PASS' and b9_2 == 'PASS' else ('FAIL' if 'FAIL' in (b9_1, b9_2) else 'NOT EVALUABLE')
    L.append('p.327(g)(3): B9a members (1) %s, (2) %s -> %s%s' % (b9_1, b9_2, b9,
                                                              ' - FS2d does not install FS2' if b9 == 'FAIL' else ''))
    want = [('fs2_w', w, 'PASS'), ('fs2_w0', w0, 'STOP'), ('fs2_v', v, 'PASS')]
    fails = [n for n, r, x in want if r is not None and r['verdict'] in ('FAIL', 'NO STOP')] + (['timestop'] if tst == 'FAIL' else [])
    good = all(r is not None and r['verdict'] == x for _, r, x in want) and tst == 'PASS'
    word = 'PASS' if good else ('FAIL' if fails or b9 == 'FAIL' else 'NOT EVALUABLE')
    L.append('FS2 SERIES VERDICT p.298(g) + p.327(g)(3): %s; fs2_w=%s fs2_w0=%s fs2_v=%s timestop=%s; B9a %s' % (
        word, w['verdict'] if w else '-', w0['verdict'] if w0 else '-', v['verdict'] if v else '-', tst, b9))
    return '\n'.join(L), word


def f(v):
    return 'none' if v is None else '%.3f' % v


def text(r):
    cfg = r['cfg']
    L = ['fs2_read tag %s level %s kind %s letter %s log sha256 %s binary %s' % (
        r['tag'], cfg['level'], cfg['kind'], cfg['letter'], r['log_sha'], (r['binary'] or '')[:16])]
    for name, ok, det in r['admit']:
        L.append('admit %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    for name, ok, det in r.get('controls') or []:
        L.append('control %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    for name, ok, det in r['exec_members']:
        L.append('executor member [I] %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    L.append('defaults: FixMinimize: on %d; FixB9a: on %d (want 1 on fs2_w, fs2_v, fs2_t); DualSrcBlend lines %s (first GuestOut byte %s) '
             '-> supported=1 enabled=1 before the first GuestOut %s' % (r['fixmin'], r['fixb9a'], r['dual'][:3], r['guest'], r['dual_ok']))
    L.append('B9a (p.327(g)(1)): ASSERT: log %d stdout %d; user_msg_param log %d stdout %d; stub lines with [AudioPropagation_v1] '
             'log %d stdout %d; AudioPropagation: calls lines %d, last (information): %s' % (
                 r['asserts_log'], r['asserts_std'], r['umsg_log'], r['umsg_std'], r['apstub_log'], r['apstub_std'], r['calls'],
                 r['calls_last']))
    L.append('window lines %s; Window <id> minimized %d; Recovering Vulkan swapchain %d' % (sorted(r['win'].items()), r['minw'],
                                                                                              r['recovering']))
    L.append('entered %s first scene frame %s scene change %s outcome %s hold_exit %s' % (
        r['entered'], r['first'], r['scene_change'], r['outcome'], r['hold_exit']))
    L.append('hold: sum dt after the first scene frame %.1f s (>= %d); json hold_s %s' % (r['dt_after_first_s'], cfg['hold_s'],
                                                                                         r['hold_s_json']))
    L.append('death markers %d %s; [Vulkan][E] lines %d; AsyncPipelines skipped draw lines %d (data)' % (
        r['deaths'], r['marks'][:3], r['vke'], r['skip_lines']))
    if cfg['kind'] == 'W':
        L.append('form W p.295(b): held %s; layer limit lines %s; validation-layer lines [W][2]/[E][2] %s; last one before the end of '
                 'the hold %s us (<= %d)' % (r['held'], r.get('limit'), r.get('vk2'), r.get('layer_end_us'), LAYER_END_US))
    if cfg['kind'] != 'T':
        t = r['t']
        L.append('log clock (s of dt): armed %s minimize %s restore %s begin %s end %s total %s' % (
            f(t['armed']), f(t['minimize']), f(t['restore']), f(t['begin']), f(t['end']), f(t['total'])))
        e = r['episode']
        L.append('episode: begin lines %d end lines %d; end frames_dropped/ms %s; end later than restore + 2 s: log clock %s, ms= %s' % (
            e['begin'], e['end'], e['end_val'], r['late_log'], r['late_ms']))
        L.append('FrameTrace rows after TestMinimize: restore %d (>= %d for (a)); window events outside the stand %s' % (
            r['rows_after_restore'], ROWS_AFTER_RESTORE, r['window_out'][:4]))
        L.append('K2 after the first scene frame %d %s; outside the window %d; deaths outside the window %d' % (
            len(r['k2']), r['k2'][:5], r['k2_out'], len(r['deaths_out'])))
        if r.get('stop_rule'):
            s = r['stop_rule']
            L.append('stop rule (p.298(g)(2)): anchor %s at byte %s; [Vulkan][E] zero-extent lines after it %d; VUID 01689 line index '
                     '(0 same, 1..3 next) %s -> %s' % (s['anchor_kind'], s['anchor'], len(s['extent_after']), s['vuid'][:3],
                                                     'STOP' if s['stop'] else 'NO STOP'))
        v = r.get('video')
        if v:
            L.append('video window anchored %s; idx gap %s; glitches outside: anchored %d %s, idx gap %d' % (
                v['win_anchored'], v['win_gap'], len(v['glitches_out_anchored']), v['glitches_out_anchored'][:4],
                len(v['glitches_out_gap'])))
            L.append('N1: records after end %d, present order breaks after end %d %s; whole file breaks %d; records %d; continuity '
                     '(data) rows without a record outside %d, longest run %d' % (
                         v['after_end_records'], len(v['after_end_bad']), v['after_end_bad'][:4], len(v['all_bad']), v['records'],
                         v['rows_without_record_outside'], v['longest_run_outside']))
    else:
        fr = r['freq']
        L.append('stubs (log) %d, AudioPropagation_v1 %s; counter: L0 %s L1 %s delta SourceCreate %s rows %s -> %s per frame (< %.1f)%s' % (
            r['stub_lines'], sorted(r['stub_ap'].items()), fr['l0'], fr['l1'], fr['d_create'], fr['rows'],
            ('%.4f' % fr['freq']) if fr['freq'] is not None else None, FREQ_MAX, ('; variant [I] ' + fr['var']) if fr['var'] else ''))
        L.append('wake control %s (last counter line %s); K2 %d; K3 entry window %d; K3 hold %d (limit %d) %s; K3 hold within 120 s [I] %s; '
                 'mean dt_us %s; rips %s' % (r['wake'], r['last_calls'], r['k2'], r['k3_window'], r['k3_hold'], K3_T,
                                             r['k3_hold_rows'][:6], r['k3_hold120'],
                                             ('%.1f' % r['mean_dt_us']) if r['mean_dt_us'] is not None else None, r['rips'][:2]))
    g = r['glitch']
    L.append('video: frames %s glitches (all) %s sheet %s' % (g['video_frames'] if g else None, g['glitches'] if g else None, r['sheet']))
    if r.get('parts'):
        L.append('letter members: %s' % ', '.join('%s=%s' % (k, v) for k, v in r['parts'].items()))
    L.append('FS2 VERDICT %s: %s%s' % (r['tag'], r['verdict'], (' (' + '; '.join(map(str, r['why'])) + ')') if r['why'] else ''))
    L.append('FS2 EXECUTOR MEMBERS %s [I] (not the verdict): %s' % (
        r['tag'], 'all ok' if r['exec_ok'] else 'FAILED %s - question to the lead' % [n for n, ok, _ in r['exec_members'] if not ok]))
    return '\n'.join(L).encode('ascii', 'replace').decode('ascii')


SEALED = ('go_fs2.sh', 'fs2_read.py', 'test_fs2_read.py', 'test_go_fs2.py', 'win_fs2.py', 'cachesig_f6e.py', 'shalist_f2c.py',
          'enter_scene.py', 'launch_run.py', 'run_safety99.py', 'idle142.py', 'procload.py', 'sheet142.py', 'cachemf146.py',
          'fgcpu146.py', 'gates_default.txt', SC142, F5C, F6E, 'C:/kyty/scripts/s51_vidglitch.py')
RX_SEAL = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)$')


def check_seal(pred, root=ROOT, names=SEALED):
    """Every 'seal: <sha256> <path>' line must match the file now (a path without 'C:/' is under root), and every name of SEALED
    must have exactly one line.  Returns (ok, lines)."""
    if not os.path.isfile(pred):
        return False, ['no seal %s' % pred]
    got = {}
    out = []
    ok = True
    with open(pred, encoding='utf-8') as fh:
        for line in fh:
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
            with open(p, encoding='ascii') as fh:
                r = json.load(fh)
        print(stop_check(r))
        return 0
    if '--stop-rule' in a:
        rc = 0
        for p in a[a.index('--stop-rule') + 1:]:
            s = stop_rule(p)
            print('stop rule %s: anchor %s at %s; zero-extent lines after %d; vuid %s -> %s' % (
                p, s['anchor_kind'], s['anchor'], len(s['extent_after']), s['vuid'][:3], 'STOP' if s['stop'] else 'NO STOP'))
            rc |= 0 if s['stop'] else 1
        return rc
    if '--summary' in a:
        try:
            m = Mods()
        except SystemExit as e:
            print('refused: %s' % e)
            return 2
        reads = dict((t, read_tag(t, root, m)) for t in SEQ)
        txt, _ = summary(reads)
        print(txt.encode('ascii', 'replace').decode('ascii'))
        return 0
    if '--tag' not in a or a.index('--tag') + 1 >= len(a) or a[a.index('--tag') + 1] not in TAGS:
        print('usage: fs2_read.py --tag %s [--root <dir>] [--json <out>] | --stop-check <json> | --summary | --check-seal <pred> | '
              '--stop-rule <log>...' % '|'.join(SEQ))
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
        with open(a[a.index('--json') + 1], 'w', encoding='ascii') as fh:
            json.dump(r, fh, indent=1, default=str)
    return 0


if __name__ == '__main__':
    sys.exit(main())
