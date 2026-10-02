"""f6e_read.py - F6e (HPP-377), track F: the reading of one F6e tag and of the series - ROADMAP p.287(v)(3), (5)-(7) (criterion F6,
B9a), p.290(b)(1)-(2) (K3 base; the line 'FixB9a: on' - a member of the run form), p.294(b) (RC1 of F6d: 0 game asserts at =1),
p.294(v) (RC2 of F6d: the counter line by exact key=value tokens, no monotonicity of total, stubs from the log only), p.294(g) N4
(no KYTY_PRINT_NAMES), p.281(g) (precache by default), p.221(v) (first scene frame), p.273(z) (window event), p.258(d) (member
of the executor [I]: printed on its own line, it does not set the verdict); seal 02 (p.306(g)): I10 by B1 (a cold variant
directory: 'no <variant>/pipelines.bin yet' + 'saved <N> recipes' also admit), two warm-up entries f6e_w1 / f6e_w2 at =0 are not
read (B2).

The s142 reading is NOT copied and NOT changed: sc142.py is imported from C:/kyty/s142 after its sha256 is checked (SC142_SHA;
another sha -> rc 2, no reading); only scan / derive / markers / read_glitch / last_value and the constants K2_US / K3_US /
ENTRY_WIN / SCENE_DRAWS are called.  Everything F6e adds is in this file.

  python f6e_read.py --tag <tag> [--root <dir>] [--json <out.json>]
  python f6e_read.py --stop-check <tag.read.json>     (one line: "continue: ...", "repeat-form: ..." or "stop: ...")
  python f6e_read.py --repeats [--root <dir>]         (one line: "repeat: <tags>" or "repeat: none" - K3 repeats of p.287(v)(5))
  python f6e_read.py --summary [--root <dir>]         (the table of the series and the verdict of p.287(v)(5)-(7), p.294(b))
  python f6e_read.py --check-seal <pred.md>

Tags (p.287(v)(5)), all on the copy d8756dce of the F6c binary, no validation, precache by default, form V of sc144 (video,
FrameTrace, hold = sum dt_us of the shown frames after the first scene frame >= 120 s):
  f6e_a1, f6e_a2  timestop_casino          KYTY_FIX_B9A=1
  f6e_b1          mini_astro_clock_tower   KYTY_FIX_B9A=1
  f6e_c1          timestop_casino          KYTY_FIX_B9A=0  (control, p.287(v)(6))
  f6e_c2          mini_astro_clock_tower   KYTY_FIX_B9A=0  (control, p.287(v)(6))
  <tag>r          the one repeat of a =1 tag whose K3 hold exceeds the limit (p.287(v)(5): "the repeat decides")
  <tag>f          the one repeat of a tag whose 'FixB9a: on' count is wrong (p.290(b)(2): a form error, repeated by the harness,
                  not an outcome and not an attempt of the level)
Members of a =1 entry (p.287(v)(5), p.294(b)): 0 lines 'Unresolved import stub called [' in the LOG (any library; the stdout
printf lines are printed apart and never added, p.294(v)); 0 death markers; 0 frames >= 1 s after the first scene frame; video
>= 3000 frames and s51_vidglitch.py 4 6 = 0 glitches (and the sheet file); K3 hold <= max(base of the level, control =0 of the
same level in this series) - base timestop_casino 1, mini_astro_clock_tower 0; on timestop_casino: SourceCreate per frame on the
hold < 0.1 and the wake control SourceSetAttributes >= 1 or SourceRender >= 1; 0 lines with 'ASSERT:' in the log and in the
stdout; lines 'user_msg_param' in the log <= those of the control =0 of the same level in this series.
Frequency (p.287(v)(3)): delta SourceCreate / number of FrameTrace rows between the last counter line before the first scene
frame and the last counter line of the hold (by position in the log).  The counter line 'AudioPropagation: calls' is read by
whitespace tokens 'key=value' with the exact key (p.294(v)): SystemSetAttributes= never counts as SourceSetAttributes=.
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
ROOT = 'C:/kyty/f287/f6e'
# the F6c copy (p.290: C:/kyty/f287/bin/kyty_emulator_d8756dce.exe, confirmed by F6d p.286(b)); its sha256 is a member of admission
BIN_SHA = 'd8756dce0662fb318a24a3fb52a3260d31ea84628372fa9a438ca46ed6a6e43d'
TC = 'timestop_casino'
MA = 'mini_astro_clock_tower'
CHUNK = 1 << 26
HOLD_S = 120
FRAMES_V = 3000
FREQ_MAX = 0.1
GUEST_BASE = 0x900000000
K3_BASE = {TC: 1, MA: 0}              # p.287(v)(5): c142_03 1, v144_13 0 -> 1; v143_03 0 -> 0
BASE = {
    'f6e_a1': dict(level=TC, fix='1', mech=True, ref=None),
    'f6e_a2': dict(level=TC, fix='1', mech=True, ref='C:/kyty/s142/sheet_c142_03.png'),
    'f6e_b1': dict(level=MA, fix='1', mech=False, ref='C:/kyty/s143/sheet_v143_03.png'),
    'f6e_c1': dict(level=TC, fix='0', mech=False, ref=None),
    'f6e_c2': dict(level=MA, fix='0', mech=False, ref=None),
}
SEQ = ('f6e_a1', 'f6e_a2', 'f6e_b1', 'f6e_c1', 'f6e_c2')
ONE = ('f6e_a1', 'f6e_a2', 'f6e_b1')
CTL = {TC: 'f6e_c1', MA: 'f6e_c2'}
# p.287(v)(6) control profiles: the stub calls of AudioPropagation by NID (the letter "2 / ~295 / ~365 / ~362", "2 / ~1022")
PROFILE = {TC: {'b-dYXrjSNZU': 2, 'WXMhENV2NcA': 295, 'd84otraxt2s': 365, 'G+QLTfyLMYk': 362},
           MA: {'b-dYXrjSNZU': 2, 'WXMhENV2NcA': 1022}}
EXACT = 'b-dYXrjSNZU'                 # "2" without "~" in the letter
TOL = 15                              # [I] the reading of "~": +-15 calls (witnesses: 295/296, 364/365, 361/363)
CTL_MIN = 1000                        # p.287(v)(6): >= 1 000 lines with AudioPropagation at f6e_c1
FIX_NAMES = ('KYTY_FIX_B26', 'KYTY_FIX_B1B', 'KYTY_FIX_DUALSRC', 'KYTY_FIX_MINIMIZE')
OTHER_ABSENT = ('KYTY_PIPELINE_PRECACHE', 'KYTY_GPU_CHECKPOINTS', 'KYTY_PRINT_NAMES', 'KYTY_S_PCW', 'KYTY_PVAR',
                'KYTY_TEST_MINIMIZE', 'KYTY_GATE_SCHEDULE', 'KYTY_GATE_SCHEDULE_ABBA', 'KYTY_BVH_STUB', 'KYTY_BVH_LOOP_CAP',
                'KYTY_SHADER_CACHE')
M_STUB = b'Unresolved import stub called ['
M_STUB_STD = b'Unresolved import stub called: '
RX_STUB = re.compile(rb'Unresolved import stub called \[(\d+)\]:[^\n]*?symbol=([^\s\[]+)((?:\[[^\]\n]*\])*)')
M_CALLS = b'AudioPropagation: calls'
M_FIXON = b'FixB9a: on'
M_ASSERT = b'ASSERT:'
M_UMSG = b'user_msg_param'
M_TCACHE = b'Shader translation cache:'
M_REC = b'Recovering Vulkan swapchain'
RX_PRE = re.compile(rb'PipelinePrecache: \d+ recipes ->')
# p.306(g) B1 (I10 of seal 02): or >= 1 'PipelinePrecache: no <variant directory>\pipelines.bin yet' AND >= 1 'saved <N> recipes'
RX_PRE_NO = re.compile(rb'PipelinePrecache: no [^\n]*?[\\/]variant_[^\n\\/]*[\\/]pipelines\.bin yet')
RX_PRE_SAVED = re.compile(rb'PipelinePrecache: saved \d+ recipes')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
WIN_KEYS = ('minimized', 'restored', 'resized', 'size changed', 'lost keyboard focus')
RX_RIP = re.compile(r'rip=0x([0-9a-fA-F]+)')
RX_TAG = re.compile(r'^(f6e_(?:a1|a2|b1|c1|c2))([rf]?)$')


def cfg_of(tag):
    """The configuration of a tag name: a base tag, '<one>r' (K3 repeat of a =1 tag) or '<any>f' (form repeat)."""
    m = RX_TAG.match(tag or '')
    if not m:
        return None
    base, suf = m.group(1), m.group(2)
    if suf == 'r' and base not in ONE:
        return None
    return dict(BASE[base], base=base, suffix=suf)


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


def parse_calls(rest):
    """p.294(v)(a): whitespace tokens 'key=value' with an integer value, the exact key; any other token is ignored."""
    d = {}
    for tok in rest.split():
        if tok.count(b'=') != 1:
            continue
        k, v = tok.split(b'=')
        if k and v.isdigit():
            d[k.decode('latin1')] = int(v)
    return d


def scan_f6e(path):
    """One streaming pass: stub lines (index, symbol, library suffix, position), stdout-form stub lines, counter lines
    (position, fields), 'FixB9a: on', 'ASSERT:', 'user_msg_param', translation cache, precache, window lines."""
    res = dict(stub_lines=0, stubs=[], stub_std=0, calls=[], fixon=0, asserts=0, assert_first=[], umsg=0, tcache=[], pre=0,
               pre_no=0, pre_saved=0, win={k: 0 for k in WIN_KEYS}, recovering=0)
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
            res['stub_lines'] += whole.count(M_STUB)
            res['stub_std'] += whole.count(M_STUB_STD)
            for m in RX_STUB.finditer(whole):
                sfx = m.group(3).decode('latin1')
                lib = sfx[1:sfx.index(']')] if sfx.startswith('[') else ''
                res['stubs'].append((int(m.group(1)), m.group(2).decode('latin1'), lib, base + m.start()))
            i = whole.find(M_CALLS)
            while i >= 0:
                e = whole.find(b'\n', i)
                e = len(whole) if e < 0 else e
                res['calls'].append((base + i, parse_calls(whole[i + len(M_CALLS):e])))
                i = whole.find(M_CALLS, e)
            res['fixon'] += whole.count(M_FIXON)
            i = whole.find(M_ASSERT)
            while i >= 0:
                s = whole.rfind(b'\n', 0, i) + 1
                e = whole.find(b'\n', i)
                e = len(whole) if e < 0 else e
                res['asserts'] += 1
                if len(res['assert_first']) < 3:
                    res['assert_first'].append(whole[s:e][:160].decode('latin1'))
                i = whole.find(M_ASSERT, e)
            i = whole.find(M_UMSG)
            while i >= 0:
                e = whole.find(b'\n', i)
                e = len(whole) if e < 0 else e
                res['umsg'] += 1
                i = whole.find(M_UMSG, e)
            i = whole.find(M_TCACHE)
            while i >= 0:
                e = whole.find(b'\n', i)
                res['tcache'].append(whole[i + len(M_TCACHE):e if e >= 0 else len(whole)].strip().decode('latin1'))
                i = whole.find(M_TCACHE, i + 1)
            res['pre'] += len(RX_PRE.findall(whole))
            res['pre_no'] += len(RX_PRE_NO.findall(whole))
            res['pre_saved'] += len(RX_PRE_SAVED.findall(whole))
            for m in RX_WIN.finditer(whole):
                res['win'][m.group(1).decode()] += 1
            res['recovering'] += whole.count(M_REC)
            if not b:
                break
    res['stubs'].sort(key=lambda x: x[3])
    res['calls'].sort(key=lambda x: x[0])
    return res


def stub_profile(stubs):
    """Ф13: the stub lines by symbol, by library; the AudioPropagation lines (suffix [AudioPropagation_v1], p.294(v))."""
    by_sym = {}
    by_lib = {}
    ap = {}
    for _, sym, lib, _ in stubs:
        by_sym[sym] = by_sym.get(sym, 0) + 1
        by_lib[lib] = by_lib.get(lib, 0) + 1
        if lib == 'AudioPropagation_v1':
            ap[sym] = ap.get(sym, 0) + 1
    return by_sym, by_lib, ap


def first_scene_pos(sc142, log, d):
    if d['entry_pos'] is None or d['first'] is None:
        return None
    cpos = d['change_pos']
    after = [r for r in log['rows'] if r[3] > d['entry_pos'] and (cpos is None or r[3] < cpos)]
    fi = next((i for i, r in enumerate(after) if r[2] >= sc142.SCENE_DRAWS), None)
    return after[fi][3] if fi is not None else None


def frequency(rows, calls, fpos, cpos):
    """p.287(v)(3): (delta SourceCreate, rows, freq, how).  L0 = the last counter line before the first scene frame, L1 = the
    last counter line of the hold (after the first scene frame, before a scene change), by position; rows = FrameTrace rows
    strictly between them.  The letter leaves open: no L0 / no L1 / no rows -> freq None (NOT EVALUABLE); the executor
    variant [I] is printed beside: without L0 the base is 0 at the first scene frame, without L1 the bound 255 / rows."""
    out = dict(l0=None, l1=None, d_create=None, rows=None, freq=None, var=None)
    if fpos is None:
        return out
    before = [c for c in calls if c[0] < fpos]
    hold = [c for c in calls if c[0] > fpos and (cpos is None or c[0] < cpos)]
    l0 = before[-1] if before else None
    l1 = hold[-1] if hold else None
    out['l0'] = (l0[0], l0[1].get('SourceCreate'), l0[1].get('total')) if l0 else None
    out['l1'] = (l1[0], l1[1].get('SourceCreate'), l1[1].get('total')) if l1 else None
    if l0 and l1 and 'SourceCreate' in l0[1] and 'SourceCreate' in l1[1]:
        n = sum(1 for r in rows if l0[0] < r[3] < l1[0])
        dc = l1[1]['SourceCreate'] - l0[1]['SourceCreate']
        out['d_create'], out['rows'] = dc, n
        out['freq'] = (dc / n) if n > 0 else None
    # variant of the executor [I]
    hrows = [r for r in rows if r[3] > fpos and (cpos is None or r[3] < cpos)]
    if l1 and 'SourceCreate' in l1[1] and not l0:
        n = sum(1 for r in rows if fpos <= r[3] < l1[0])
        out['var'] = 'no counter line before the first scene frame: base 0 -> %d / %d = %s' % (
            l1[1]['SourceCreate'], n, ('%.4f' % (l1[1]['SourceCreate'] / n)) if n else None)
    elif not l1 and hrows:
        out['var'] = 'no counter line on the hold: < 256 library calls on %d hold rows -> SourceCreate per frame < %.4f' % (
            len(hrows), 256.0 / len(hrows))
    return out


def wake(calls):
    """p.287(v)(5): the wake control on the last counter line by position - SourceSetAttributes >= 1 or SourceRender >= 1."""
    if not calls:
        return False, None
    last = calls[-1][1]
    ssa, sr = last.get('SourceSetAttributes'), last.get('SourceRender')
    return (ssa or 0) >= 1 or (sr or 0) >= 1, dict(SourceSetAttributes=ssa, SourceRender=sr, SourceCreate=last.get('SourceCreate'),
                                                   SourceDestroy=last.get('SourceDestroy'), handles=last.get('handles'),
                                                   total=last.get('total'))


def k3_within(sc142, log, d, fpos, limit_s=HOLD_S):
    """[I] K3 hold rows within limit_s of shown time after the first scene frame (the hold of 120 s), entry window out."""
    if fpos is None:
        return None
    cpos = d['change_pos']
    post = [r for r in log['rows'] if r[3] > fpos and (cpos is None or r[3] < cpos)]
    acc = 0
    out = []
    for j, r in enumerate(post):
        acc += r[1]
        if acc > limit_s * 1e6:
            break
        if j >= sc142.ENTRY_WIN and sc142.K3_US <= r[1] < sc142.K2_US:
            out.append((r[0], r[1]))
    return out


def rips(marks):
    """p.294(b): the rip of each 'Unhandled exception:' line and its offset from 0x900000000 (information [I])."""
    out = []
    for m in marks:
        if not m['kind'].startswith('Unhandled exception'):
            continue
        x = RX_RIP.search(m.get('line') or '')
        if x:
            rip = int(x.group(1), 16)
            off = rip - GUEST_BASE
            out.append('rip 0x%x offset %s0x%x (%s)' % (rip, '+' if off >= 0 else '-', abs(off), m['src']))
        else:
            out.append('rip not in the line (%s)' % m['src'])
    return out


def read_tag(tag, root=ROOT, sc142=None):
    cfg = cfg_of(tag)
    sc142 = sc142 or load()
    lp = os.path.join(root, 'log_%s.txt' % tag)
    sp = os.path.join(root, 'stdout_%s.txt' % tag)
    jp = os.path.join(root, '%s.json' % tag)
    if cfg is None or not os.path.isfile(lp) or not os.path.isfile(jp):
        return None
    with open(jp, encoding='utf-8') as f:
        js = json.load(f)
    at = (js.get('attempts') or [{}])[0]
    env = js.get('env') or {}
    log = sc142.scan(lp)
    std = sc142.scan(sp) if os.path.isfile(sp) else None
    d = sc142.derive(log, cfg['level'])
    marks = sc142.markers(log, std, d['entry_pos'], log['quit'])
    ex = scan_f6e(lp)
    exs = scan_f6e(sp if os.path.isfile(sp) else None)
    r = dict(tag=tag, cfg=cfg, log_sha=log['sha256'], binary=js.get('binary_sha256'))
    adm = []

    def add(name, ok, detail=''):
        adm.append((name, bool(ok), str(detail)))
    add('one attempt', len(js.get('attempts') or []) == 1, len(js.get('attempts') or []))
    add('guest args -lvl %s' % cfg['level'], js.get('guest_args') == '-lvl %s' % cfg['level'], js.get('guest_args'))
    add('KYTY_FIX_B9A=%s exactly (p.287(v)(5))' % cfg['fix'], env.get('KYTY_FIX_B9A') == cfg['fix'], repr(env.get('KYTY_FIX_B9A')))
    for k in FIX_NAMES:
        add('%s not set (default of the binary)' % k, k not in env, repr(env.get(k)))
    for k in OTHER_ABSENT:
        add('%s not set%s' % (k, ' (p.294(g) N4)' if k == 'KYTY_PRINT_NAMES' else (' (p.281(g))' if k == 'KYTY_PIPELINE_PRECACHE' else '')),
            k not in env, repr(env.get(k)))
    add('binary sha256 = F6c copy d8756dce (p.287(v)(5))', js.get('binary_sha256') == BIN_SHA, (js.get('binary_sha256') or '')[:16])
    add('KYTY_GPU_CLOCK_PIN=1', env.get('KYTY_GPU_CLOCK_PIN') == '1', env.get('KYTY_GPU_CLOCK_PIN'))
    rec = env.get('KYTY_REC')
    add('video KYTY_REC rec_%s.mp4 (form V sc144)' % tag, rec is not None and rec.replace('\\', '/').endswith('/rec_%s.mp4' % tag), rec)
    vv = sc142.last_value(js.get('cmdline') or [], '--vulkan-validation')
    add('--vulkan-validation false', vv == 'false', vv)
    add('precache by default (I10, p.306(g) B1): >= 1 line "PipelinePrecache: <N> recipes ->" OR (>= 1 "PipelinePrecache: no '
        '<variant dir>\\pipelines.bin yet" AND >= 1 "PipelinePrecache: saved <N> recipes") in the log (form V sc144, p.281(g))',
        ex['pre'] >= 1 or (ex['pre_no'] >= 1 and ex['pre_saved'] >= 1),
        'recipes-> %d, no-variant %d, saved %d' % (ex['pre'], ex['pre_no'], ex['pre_saved']))
    r['admit'] = adm
    r['admitted'] = all(ok for _, ok, _ in adm)
    want_on = 1 if cfg['fix'] == '1' else 0
    r['fixon'] = ex['fixon']
    r['form_ok'] = ex['fixon'] == want_on
    r['tcache'] = ex['tcache'][:3]
    win = {k: ex['win'][k] + exs['win'][k] for k in WIN_KEYS}
    r['win'] = win
    r['recovering'] = ex['recovering'] + exs['recovering']
    r['winev'] = win['minimized'] > 0 or r['recovering'] > 0
    by_sym, by_lib, ap = stub_profile(ex['stubs'])
    r['stub_lines'] = ex['stub_lines']
    r['stub_parsed'] = len(ex['stubs'])
    r['stub_by_sym'] = by_sym
    r['stub_by_lib'] = by_lib
    r['stub_ap'] = ap
    r['stub_ap_lines'] = sum(ap.values())
    r['stub_std'] = exs['stub_std']
    r['calls_lines'] = len(ex['calls'])
    r['asserts_log'] = ex['asserts']
    r['asserts_std'] = exs['asserts']
    r['assert_first'] = (ex['assert_first'] + exs['assert_first'])[:2]
    r['umsg_log'] = ex['umsg']
    r['umsg_std'] = exs['umsg']
    r['entered'] = d['entered']
    r['first'] = d['first']
    r['hold_s'] = d['dt_after_first_us'] / 1e6
    r['hold_s_json'] = at.get('hold_s')
    r['hold_exit'] = at.get('hold_exit')
    r['scene_change'] = d['change_pos'] is not None
    r['marks'] = [(m['kind'], m['cls'], m['src'], m['at_exit']) for m in marks]
    r['deaths'] = len(marks)
    r['rips'] = rips(marks)
    r['k2'] = len(d['k2'])
    r['k3_window'] = len(d['k3w'])
    r['k3_hold'] = len(d['k3h'])
    r['k3_hold_rows'] = d['k3h'][:20]
    fpos = first_scene_pos(sc142, log, d)
    w120 = k3_within(sc142, log, d, fpos)
    r['k3_hold120'] = None if w120 is None else len(w120)
    post = [x for x in log['rows'] if fpos is not None and x[3] > fpos and (d['change_pos'] is None or x[3] < d['change_pos'])]
    r['mean_dt_us'] = (sum(x[1] for x in post) / len(post)) if post else None
    fr = frequency(log['rows'], ex['calls'], fpos, d['change_pos'])
    r['freq'] = fr
    wk, last = wake(ex['calls'])
    r['wake'], r['last_calls'] = wk, last
    g = sc142.read_glitch(os.path.join(root, 'glitch_%s.txt' % tag))
    r['glitch'] = g
    r['sheet'] = os.path.isfile(os.path.join(root, 'sheet_%s.png' % tag)) and os.path.getsize(os.path.join(root, 'sheet_%s.png' % tag)) > 0
    verdict(r)
    return r


def verdict(r):
    """The tag verdict (fields of r -> r['verdict'], r['why']).  The members that need the control =0 of this series (K3 limit,
    user_msg_param) are decided in the summary."""
    cfg = r['cfg']
    if not r['admitted']:
        r['verdict'], r['why'] = 'NOT ADMITTED', [n for n, ok, _ in r['admit'] if not ok]
        return
    if not r['form_ok']:
        r['verdict'], r['why'] = 'INVALID', ['FixB9a: on lines %d, want %d (p.290(b)(2) form)' % (r['fixon'], 1 if cfg['fix'] == '1' else 0)]
        return
    if r['winev']:
        r['verdict'], r['why'] = 'WINDOW EVENT', ['minimized %d, Recovering %d' % (r['win']['minimized'], r['recovering'])]
        return
    fail = []
    if cfg['fix'] == '1':
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
        if cfg['mech']:
            fq = r['freq']['freq']
            if fq is not None and fq >= FREQ_MAX:
                fail.append('SourceCreate per frame %.4f >= %.1f' % (fq, FREQ_MAX))
            if not r['wake']:
                fail.append('wake control: SourceSetAttributes and SourceRender 0 on the last counter line (%s)' % r['last_calls'])
        if fail:
            r['verdict'], r['why'] = 'FAIL', fail
            return
    if not r['entered'] or r['first'] is None:
        r['verdict'], r['why'] = 'NOT EVALUABLE', ['not entered or no first scene frame']
        return
    if r['hold_s'] < HOLD_S:
        r['verdict'], r['why'] = 'NOT EVALUABLE', ['hold %.1f s < %d s' % (r['hold_s'], HOLD_S)]
        return
    if cfg['fix'] == '1':
        if cfg['mech'] and r['freq']['freq'] is None:
            r['verdict'], r['why'] = 'NOT EVALUABLE', ['frequency not evaluable by the letter (%s)' % (r['freq']['var'] or 'no counter lines')]
            return
        r['verdict'], r['why'] = 'PASS', []
        return
    # control =0 (p.287(v)(6))
    prof = PROFILE[cfg['level']]
    bad = []
    if cfg['level'] == TC and r['stub_ap_lines'] < CTL_MIN:
        bad.append('AudioPropagation stub lines %d < %d' % (r['stub_ap_lines'], CTL_MIN))
    for sym, want in prof.items():
        got = r['stub_ap'].get(sym, 0)
        if (sym == EXACT and got != want) or (sym != EXACT and abs(got - want) > TOL):
            bad.append('%s %d (want %s%d)' % (sym, got, '' if sym == EXACT else '~', want))
    other = {s: n for s, n in r['stub_by_sym'].items() if s not in prof}
    if other:
        bad.append('other symbols %s' % other)
    if r['calls_lines']:
        bad.append('AudioPropagation: calls lines %d' % r['calls_lines'])
    r['verdict'], r['why'] = ('CONTROL FAIL', bad) if bad else ('CONTROL OK', [])


def stop_check(r):
    """The harness rule: stop the series on no reading / NOT ADMITTED / WINDOW EVENT / a death marker / an INVALID form repeat;
    an INVALID first reading -> one form repeat '<tag>f' (p.290(b)(2)); everything else is data: continue."""
    if r is None:
        return 'stop: no reading (no log or no json)'
    if r['verdict'] in ('NOT ADMITTED', 'WINDOW EVENT'):
        return 'stop: %s %s' % (r['verdict'], '; '.join(r['why'])[:200])
    if r['verdict'] == 'INVALID':
        if r['cfg']['suffix'] == '':
            return 'repeat-form: %sf %s' % (r['tag'], '; '.join(r['why'])[:200])
        return 'stop: INVALID again %s' % '; '.join(r['why'])[:200]
    if r['deaths']:
        return 'stop: death markers %d %s %s' % (r['deaths'], r['marks'][:2], r['rips'][:2])
    return 'continue: %s %s' % (r['verdict'], '; '.join(r['why'])[:200])


def eff(reads, base):
    """The reading of a base tag: its form repeat '<tag>f' when made, else the tag itself."""
    return reads.get(base + 'f') or reads.get(base)


def judge(reads):
    """The members of p.287(v)(5) that need the control =0 of this series, and the K3 repeat rule.  Returns
    {base: dict(status, k3, limit, umsg, umsg_ctl, rep, why)} for the =1 tags and the list of repeats due."""
    out = {}
    due = []
    for t in ONE:
        lv = BASE[t]['level']
        r = eff(reads, t)
        c = eff(reads, CTL[lv])
        rep = reads.get(t + 'r')
        o = dict(status=None, k3=None, limit=None, umsg=None, umsg_ctl=None, rep=rep['verdict'] if rep else None, why=[])
        out[t] = o
        if r is None:
            o['status'], o['why'] = 'NO READING', ['no reading']
            continue
        if r['verdict'] != 'PASS':
            o['status'], o['why'] = r['verdict'], r['why']
            continue
        if c is None or c['verdict'] not in ('CONTROL OK', 'CONTROL FAIL') or c['k3_hold'] is None:
            o['status'], o['why'] = 'NO CONTROL', ['control %s not readable' % CTL[lv]]
            continue
        lim = max(K3_BASE[lv], c['k3_hold'])
        o['k3'], o['limit'], o['umsg'], o['umsg_ctl'] = r['k3_hold'], lim, r['umsg_log'], c['umsg_log']
        fail = []
        if r['umsg_log'] > c['umsg_log']:
            fail.append('user_msg_param %d > control %d (p.294(b))' % (r['umsg_log'], c['umsg_log']))
        if rep is not None:
            if rep['verdict'] != 'PASS':
                fail.append('repeat %sr %s %s' % (t, rep['verdict'], '; '.join(rep['why'])[:120]))
            elif rep['umsg_log'] > c['umsg_log']:
                fail.append('repeat user_msg_param %d > control %d (p.294(b))' % (rep['umsg_log'], c['umsg_log']))
        if fail:
            o['status'], o['why'] = 'FAIL', fail
            continue
        if r['k3_hold'] <= lim:
            o['status'] = 'PASS'
        elif rep is None:
            o['status'], o['why'] = 'REPEAT DUE', ['K3 hold %d > limit %d' % (r['k3_hold'], lim)]
            due.append(t + 'r')
        elif rep['k3_hold'] <= lim:
            o['status'], o['why'] = 'PASS', ['K3 %d > %d, the repeat decides: %d' % (r['k3_hold'], lim, rep['k3_hold'])]
        else:
            o['status'], o['why'] = 'FAIL', ['K3 %d and repeat %d > limit %d' % (r['k3_hold'], rep['k3_hold'], lim)]
    return out, due


def summary(reads):
    """The series verdict of p.287(v)(5)-(7) and p.294(b) from the per-tag reads (dict tag -> read or None)."""
    L = ['F6E SERIES TABLE (p.287(v)(5)-(6); one attempt each; repeats r (K3) and f (form) where made)']
    L.append('tag      level                   fix verdict        stubs(log/AP/std) deaths K2 K3h K3h120 hold_s  freq    wake ASSERT(l/s) umsg video/glitch')
    order = [t + s for t in SEQ for s in ('', 'f', 'r') if (t + s) in reads or s == '']
    for t in order:
        r = reads.get(t)
        if r is None:
            L.append('%-8s %-23s %s   %-14s (not run or no reading)' % (t, cfg_of(t)['level'], cfg_of(t)['fix'], 'NO READING'))
            continue
        g = r.get('glitch')
        fq = r['freq']['freq']
        L.append('%-8s %-23s %s   %-14s %5d/%4d/%4d %6d %2d %3d %6s %7.1f %7s %4s %5d/%-5d %4d %s' % (
            t, r['cfg']['level'], r['cfg']['fix'], r['verdict'], r['stub_lines'], r['stub_ap_lines'], r['stub_std'], r['deaths'],
            r['k2'], r['k3_hold'], r['k3_hold120'], r['hold_s'], '%.4f' % fq if fq is not None else '-',
            'yes' if r['wake'] else 'no', r['asserts_log'], r['asserts_std'], r['umsg_log'],
            ('%s/%s' % (g['video_frames'], g['glitches'])) if g else '-'))
    j, due = judge(reads)
    for t in ONE:
        o = j[t]
        L.append('(5) %s: %s; K3 hold %s <= limit %s (max of base %d and control %s); user_msg_param %s <= control %s; repeat %s%s' % (
            t, o['status'], o['k3'], o['limit'], K3_BASE[BASE[t]['level']], CTL[BASE[t]['level']], o['umsg'], o['umsg_ctl'],
            o['rep'], (' - ' + '; '.join(o['why'])) if o['why'] else ''))
    for t in ('f6e_c1', 'f6e_c2'):
        c = eff(reads, t)
        L.append('(6) %s: %s%s' % (t, c['verdict'] if c else 'NO READING',
                                    (' - ' + '; '.join(c['why'])) if c and c['why'] else ''))
    bad = ('NO READING', 'NOT ADMITTED', 'INVALID', 'WINDOW EVENT', 'NOT EVALUABLE', 'NO CONTROL', 'REPEAT DUE')
    ones = [j[t]['status'] for t in ONE]
    ctls = [(eff(reads, t) or {}).get('verdict', 'NO READING') for t in ('f6e_c1', 'f6e_c2')]
    if any(s == 'FAIL' for s in ones) or any(v == 'CONTROL FAIL' for v in ctls):
        word = 'FAIL'
    elif any(s in bad for s in ones) or any(v != 'CONTROL OK' for v in ctls):
        word = 'NOT EVALUABLE'
    else:
        word = 'PASS'
    L.append('(7) N: timestop_casino =1 entries PASS %d of 2; mini_astro_clock_tower =1 entries PASS %d of 1' % (
        sum(1 for t in ('f6e_a1', 'f6e_a2') if j[t]['status'] == 'PASS'), 1 if j['f6e_b1']['status'] == 'PASS' else 0))
    L.append('repeats due (K3, p.287(v)(5)): %s' % (', '.join(due) or 'none'))
    L.append('F6E SERIES VERDICT p.287(v)(5)-(7) + p.294(b): %s; =1 %s; controls %s' % (
        word, ', '.join('%s=%s' % (t, j[t]['status']) for t in ONE), ', '.join(ctls)))
    return '\n'.join(L), word


def text(r):
    cfg = r['cfg']
    L = ['f6e_read tag %s level %s KYTY_FIX_B9A=%s log sha256 %s binary %s' % (
        r['tag'], cfg['level'], cfg['fix'], r['log_sha'], (r['binary'] or '')[:16])]
    for name, ok, det in r['admit']:
        L.append('admit %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    L.append('form (p.290(b)(2)): FixB9a: on lines %d (want %d) -> %s' % (r['fixon'], 1 if cfg['fix'] == '1' else 0,
                                                                         'ok' if r['form_ok'] else 'INVALID'))
    L.append('member of the executor [I]: translation cache lines %s (defaults of the binary)' % r['tcache'])
    L.append('window lines: %s, Recovering Vulkan swapchain %d -> %s' % (
        ', '.join('%s %d' % (k, r['win'][k]) for k in WIN_KEYS), r['recovering'], 'WINDOW EVENT' if r['winev'] else 'none'))
    L.append('entered %s first scene frame %s scene change %s' % (r['entered'], r['first'], r['scene_change']))
    L.append('hold: sum dt after the first scene frame %.1f s (named %d), json hold_s %s, hold_exit %s' % (
        r['hold_s'], HOLD_S, r['hold_s_json'], r['hold_exit']))
    L.append('stubs (log only, p.294(v)): lines "Unresolved import stub called [" %d (parsed %d); AudioPropagation_v1 %d %s' % (
        r['stub_lines'], r['stub_parsed'], r['stub_ap_lines'], sorted(r['stub_ap'].items())))
    L.append('stubs by library %s; by symbol (F13) %s' % (sorted(r['stub_by_lib'].items()), sorted(r['stub_by_sym'].items())[:12]))
    L.append('stdout printf stub lines (not added, p.294(v)): %d' % r['stub_std'])
    L.append('counter lines "AudioPropagation: calls" %d; last %s' % (r['calls_lines'], r['last_calls']))
    fr = r['freq']
    L.append('frequency (p.287(v)(3)): L0 %s L1 %s delta SourceCreate %s rows %s -> %s per frame (< %.1f)' % (
        fr['l0'], fr['l1'], fr['d_create'], fr['rows'], ('%.4f' % fr['freq']) if fr['freq'] is not None else None, FREQ_MAX))
    if fr['var']:
        L.append('frequency variant of the executor [I]: %s' % fr['var'])
    L.append('wake control (SourceSetAttributes >= 1 or SourceRender >= 1, last counter line): %s' % r['wake'])
    L.append('p.294(b): ASSERT: lines log %d stdout %d %s; user_msg_param lines log %d (stdout %d, information)' % (
        r['asserts_log'], r['asserts_std'], r['assert_first'][:1], r['umsg_log'], r['umsg_std']))
    L.append('death markers %d %s' % (r['deaths'], r['marks'][:4]))
    if r['rips']:
        L.append('p.294(b) information [I]: %s' % '; '.join(r['rips'][:4]))
    L.append('K2 frames after the first scene frame %d; K3 entry window %d; K3 hold %d %s' % (
        r['k2'], r['k3_window'], r['k3_hold'], r['k3_hold_rows'][:8]))
    L.append('K3 hold within 120 s of shown time after the first scene frame (variant of the executor [I]): %s' % r['k3_hold120'])
    L.append('mean dt_us after the first scene frame (a number, not a gate): %s' % (
        '%.1f' % r['mean_dt_us'] if r['mean_dt_us'] is not None else None))
    g = r['glitch']
    L.append('video: frames %s glitches %s sheet_%s.png %s; lead sheet reference %s' % (
        g['video_frames'] if g else None, g['glitches'] if g else None, r['tag'], r['sheet'], cfg['ref']))
    L.append('F6E VERDICT %s: %s%s' % (r['tag'], r['verdict'], (' (' + '; '.join(r['why']) + ')') if r['why'] else ''))
    return '\n'.join(L)


def all_reads(root, sc):
    names = [t + s for t in SEQ for s in ('', 'f', 'r') if cfg_of(t + s)]
    reads = {}
    for t in names:
        r = read_tag(t, root, sc)
        if r is not None or t in SEQ:
            reads[t] = r
    return reads


SEALED = ('go_f6e.sh', 'f6e_read.py', 'win_f6e.py', 'cachesig_f6e.py', 'shalist_f2c.py', 'test_f6e_read.py', 'test_go_f6e.py',
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
    if '--summary' in a or '--repeats' in a:
        try:
            sc = load()
        except SystemExit as e:
            print('refused: %s' % e)
            return 2
        reads = all_reads(root, sc)
        if '--repeats' in a:
            _, due = judge(reads)
            print('repeat: %s' % (' '.join(due) or 'none'))
            return 0
        txt, _ = summary(reads)
        print(txt)
        return 0
    if '--tag' not in a or a.index('--tag') + 1 >= len(a) or cfg_of(a[a.index('--tag') + 1]) is None:
        print('usage: f6e_read.py --tag %s[r|f] [--root <dir>] [--json <out>] | --stop-check <json> | --repeats | --summary | '
              '--check-seal <pred>' % '|'.join(SEQ))
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
