"""f4c_read.py - F4c (HPP-337), track F: the reading of one F4c tag - ROADMAP p.254(zh)(2)(a)-(g); F4b RC1-RC4; lead answers
to B1-B4 p.262 (b)-(e); binary of p.268(v).

The s142 reading is NOT copied and NOT changed: sc142.py is imported from C:/kyty/s142 after its sha256 is checked
(SC142_SHA; another sha -> rc 2, no reading); only scan / derive / markers / validation / read_glitch / last_value and the
constants K2_US / SCENE_DRAWS are called.  Everything F4c adds is in this file: the admission of the run, the positive
controls of p.262(d) (members of admission: a failure -> NOT EVALUABLE, not FAIL), the stop text of the control (b), the
comparison of (g) with c142_04.

  python f4c_read.py --tag f4c_a|f4c_b|f4c_v|f4c_g [--root <dir>] [--json <out.json>]
  python f4c_read.py --pre-check <tag> [--root <dir>]  (p.262(g): 'continue' when runs/recipes_<tag>.json holds a
                                                        dual-source record, else 'stop ...')
  python f4c_read.py --check-seal <pred.md>     (rc 0 every 'seal:' line matches and every sealed name has one line)
  python f4c_read.py --c14204                   (prints the c142_04 base of (g))

Tags (p.254(zh)(2)); the letters of the item are the tag suffixes (v = (v), g = (g)):
  f4c_a  (a) W Sky Garden -lvl underwater_aerial_garden, --vulkan-validation true, precache by default, KYTY_FIX_DUALSRC=1:
         a GuestOut line, hold >= 310 s, 0 [Vulkan][E], 0 death markers, the line DualSrcBlend: supported=1 enabled=1
  f4c_b  (b) control KYTY_FIX_DUALSRC=0, the same entry: a stop with the same text before the first GuestOut line
  f4c_v  (v) W mini_giants_garden =1, precache by default: hold >= 310 s, 0 [Vulkan][E]
  f4c_g  (g) V mini_giants_garden =1, no validation: hold >= 330 s, video >= 3000 frames, 0 glitches, sheet for the lead,
         no new K1/K2 against c142_04
Hold (p.262(e), p.221(v)): the sum of dt_us after the first scene frame, W >= 310 s, V >= 330 s; hold_s of <tag>.json is
printed beside as a reference.
Order of the verdict: NOT ADMITTED (run form) -> NOT EVALUABLE (controls of p.262(d); (b) without the stop, p.262(e)) ->
the letter of p.254(zh)(2): (a) entered with a GuestOut line, sum dt >= 310, 0 [Vulkan][E], 0 death markers, exactly one
line DualSrcBlend: supported=1 enabled=1 -> PASS | FAIL; (b) a [Vulkan][E] line with STOP_TEXT before the first GuestOut
line, not entered -> STOP SAME TEXT; (v) entered, sum dt >= 310, 0 [Vulkan][E] -> PASS | FAIL; (g) sum dt >= 330 s, video
>= 3000 frames, 0 glitches, sheet, no new K1/K2 against c142_04 -> PASS | FAIL.
Controls of p.262(d) (members of admission, B3 of the executor accepted with the lead's addition):
  every tag   exactly one line 'DualSrcBlend: supported=1 enabled=<arm>' and it lies before the first GuestOut line
  a, v        >= 1 line 'DualSrcBlend: patched ps=5514e10f1a60df83' before the first GuestOut line; one line
              'PipelinePrecache: N recipes ->' with N = the count of the recipe file parsed before the tag
              (runs/recipes_<tag>.json, recipes143.py) - not applicable (variant of the executor) when the first [Vulkan][E]
              line comes before any such line (a validation stop inside the precache is the letter's FAIL, p.262(e)); no
              'stale recipes' and no 'no ... yet' line; the file before the tag holds a dual-source record (factors 15..18)
  b           0 lines 'DualSrcBlend: patched'; no 'stale recipes' line; the file before the tag holds a dual-source record
              (the 'N recipes ->' line is printed when the precache completes - the W stops of s143 have none)
Executor members [I] (p.258(d): printed on separate lines, they do not set the verdict; a failure is a question to the lead):
  v           0 death markers
  g           one 'N recipes ->' line with N = count; no 'stale recipes' / 'no ... yet' line; >= 1 'patched' line of 5514
Output: ASCII only.  rc 0 - read (verdict in the text); rc 1 - no log / no json; rc 2 - usage or a sha mismatch.
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
ROOT = 'C:/kyty/f287/f4c'
SKY = 'underwater_aerial_garden'
MGG = 'mini_giants_garden'
C14204_LOG = 'C:/kyty/s142/log_c142_04.txt'
C14204_STD = 'C:/kyty/s142/stdout_c142_04.txt'
CHUNK = 1 << 26
TAGS = {
    'f4c_a': dict(level=SKY, fix='1', arm='W', val=True, video=False, hold_s=310, precache=True, need_dual=True, patched='>=1'),
    'f4c_b': dict(level=SKY, fix='0', arm='W', val=True, video=False, hold_s=0, precache=False, need_dual=True, patched='0'),
    'f4c_v': dict(level=MGG, fix='1', arm='W', val=True, video=False, hold_s=310, precache=True, need_dual=True, patched='>=1'),
    'f4c_g': dict(level=MGG, fix='1', arm='V', val=False, video=True, hold_s=330, precache=True, need_dual=False, patched=None),
}
FRAMES_V = 3000
DUAL_FACTORS = (15, 16, 17, 18)
STOP_TEXT = (b'srcColorBlendFactor (VK_BLEND_FACTOR_SRC1_ALPHA) is a dual-source blend factor, '
             b'but dualSrcBlend feature was not enabled')
M_GUEST = b'GuestOut'
M_DUAL = b'DualSrcBlend: supported='
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d+) enabled=(\d+)')
M_PATCHED = b'DualSrcBlend: patched ps='
RX_PATCHED = re.compile(rb'DualSrcBlend: patched ps=([0-9a-f]+)')
M_SKIP = b'DualSrcBlend: skip ps='
RX_SKIP = re.compile(rb'DualSrcBlend: skip ps=([0-9a-f]+) reason=(\S*)')
PS1592 = '5514e10f1a60df83'
M_PRE = b'PipelinePrecache:'
RX_PRE_N = re.compile(rb'PipelinePrecache: (\d+) recipes ->')
M_STALE = b'stale recipes'
RX_NOYET = re.compile(rb'PipelinePrecache: no \S*pipelines\.bin yet')
M_VKE = b'[Vulkan][E]'
VKE_MAX = 300
# the F4c binary (p.268(v), F4a2 report): its sha256 is a member of admission
BIN_SHA = 'c9a5e1986e254132f776f0c7f1c9446d0bdc862e199bbbc1d57aedf17d4c9f9b'
# KYTY_FIX_B26 value required in every tag, None = must be absent (the F4c binary does not read it, p.268(a))
FIXB26 = None


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


def scan_f4c(path):
    """First GuestOut line, the DualSrcBlend lines (supported / patched / skip), the precache lines, the [Vulkan][E] lines
    (first position, positions with the stop text) - with byte positions."""
    res = dict(guest=None, dual=[], patched=[], skip=[], pre_n=[], stale=[], noyet=[], pre_lines=0, stop=[], vke1=None, vke1_text=None)
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
            for marker in (M_DUAL, M_PATCHED, M_SKIP, M_PRE, M_VKE):
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
                    elif marker is M_SKIP:
                        m = RX_SKIP.search(line)
                        res['skip'].append((pos, (m.group(1).decode('ascii'), m.group(2).decode('ascii', 'replace'))
                                            if m else None))
                    elif marker is M_PRE:
                        res['pre_lines'] += 1
                        m = RX_PRE_N.search(line)
                        if m:
                            res['pre_n'].append((pos, int(m.group(1))))
                        if M_STALE in line:
                            res['stale'].append(pos)
                        if RX_NOYET.search(line):
                            res['noyet'].append(pos)
                    else:
                        if res['vke1'] is None or pos < res['vke1']:
                            res['vke1'] = pos
                            res['vke1_text'] = line[:VKE_MAX].decode('ascii', 'replace')
                        if STOP_TEXT in line:
                            res['stop'].append(pos)
                    i = whole.find(marker, e)
            if not b:
                break
    return res


def recipes_before(root, tag):
    """runs/recipes_<tag>.json (recipes143.py <json> cur=<pipelines.bin>, written by go_f4c.sh before the tag):
    (count, sha256, dual-source records) or None."""
    p = os.path.join(root, 'runs', 'recipes_%s.json' % tag)
    if not os.path.isfile(p):
        return None
    with open(p, encoding='ascii') as f:
        j = json.load(f)
    c = j.get('cur') or {}
    if 'count' not in c or not c.get('at_end'):
        return dict(count=None, sha=c.get('sha256'), dual=0, error=c.get('error', 'not parsed to the end'))
    dual = [x for x in (c.get('flagged') or [])
            if any(v in DUAL_FACTORS for v in (x.get('srcblend') or []) + (x.get('destblend') or []))]
    return dict(count=c['count'], sha=c.get('sha256'), dual=len(dual), sig=c.get('signature'), error=None)


def pre_check(root, tag):
    """p.262(g) / go_f4c.sh before (b) and (a): the recipe file before the tag must hold a dual-source record."""
    rb = recipes_before(root, tag)
    if rb is None or rb['error'] is not None:
        return 'stop: recipe file before %s not parsed (%s) - NOT EVALUABLE, question to the lead' % (
            tag, 'none' if rb is None else rb['error'])
    if rb['dual'] < 1:
        return 'stop: no dual-source record in the recipe file before %s (count %s) - NOT EVALUABLE (p.262(g)), question to the lead' % (
            tag, rb['count'])
    return 'continue: %d dual-source record(s) in the recipe file before %s (count %s)' % (rb['dual'], tag, rb['count'])


def c14204(sc142):
    """The base of (g): c142_04 (9235a7ac, census 120 s) - death markers by kind and K2 frames after the first scene frame."""
    log = sc142.scan(C14204_LOG)
    std = sc142.scan(C14204_STD) if os.path.isfile(C14204_STD) else None
    d = sc142.derive(log, MGG)
    marks = sc142.markers(log, std, d['entry_pos'], log['quit'])
    return dict(log_sha=log['sha256'], kinds=sorted(set((m['cls'], m['kind']) for m in marks if not m['at_exit'])),
                k2=len(d['k2']), dt_after_first_s=d['dt_after_first_us'] / 1e6, first=d['first'])


def read_tag(tag, root=ROOT, sc142=None, base=None):
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
    x = scan_f4c(lp)
    xs = scan_f4c(sp) if os.path.isfile(sp) else None
    rb = recipes_before(root, tag)
    r = dict(tag=tag, cfg=cfg, log_sha=log['sha256'], binary=js.get('binary_sha256'))
    adm = []

    def add(name, ok, detail=''):
        adm.append((name, bool(ok), str(detail)))
    add('one attempt', len(js.get('attempts') or []) == 1, len(js.get('attempts') or []))
    add('binary sha256 = F4c binary (p.268(v))', js.get('binary_sha256') == BIN_SHA, (js.get('binary_sha256') or '')[:16])
    add('guest args -lvl %s' % cfg['level'], js.get('guest_args') == '-lvl %s' % cfg['level'], js.get('guest_args'))
    add('KYTY_FIX_DUALSRC=%s exactly' % cfg['fix'], env.get('KYTY_FIX_DUALSRC') == cfg['fix'], repr(env.get('KYTY_FIX_DUALSRC')))
    add('KYTY_FIX_B26 %s' % ('not set' if FIXB26 is None else '=' + FIXB26), env.get('KYTY_FIX_B26') == FIXB26,
        repr(env.get('KYTY_FIX_B26')))
    add('KYTY_S_PCW not set', 'KYTY_S_PCW' not in env, repr(env.get('KYTY_S_PCW')))
    add('KYTY_GPU_CLOCK_PIN=1', env.get('KYTY_GPU_CLOCK_PIN') == '1', env.get('KYTY_GPU_CLOCK_PIN'))
    add('no KYTY_GPU_CHECKPOINTS', 'KYTY_GPU_CHECKPOINTS' not in env, '')
    add('KYTY_PIPELINE_PRECACHE not set (precache by default, p.254(zh)(2))', 'KYTY_PIPELINE_PRECACHE' not in env,
        repr(env.get('KYTY_PIPELINE_PRECACHE')))
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
    add('recipe file parsed before the tag (runs/recipes_%s.json)' % tag, rb is not None and rb['error'] is None,
        rb if rb is None else (rb['count'], (rb['sha'] or '')[:16], rb['error']))
    r['admit'] = adm
    r['admitted'] = all(ok for _, ok, _ in adm)
    # controls of p.262(d) - members of admission: a failure -> NOT EVALUABLE
    con = []

    def kadd(name, ok, detail=''):
        con.append((name, bool(ok), str(detail)))
    # executor members [I] (p.258(d))
    ctl = []

    def cadd(name, ok, detail=''):
        ctl.append((name, bool(ok), str(detail)))
    duals = x['dual']
    kadd('exactly one DualSrcBlend line = supported=1 enabled=%s' % cfg['fix'],
         len(duals) == 1 and duals[0][1] == (1, int(cfg['fix'])), [v for _, v in duals])
    kadd('the DualSrcBlend line before the first GuestOut line',
         len(duals) == 1 and (x['guest'] is None or duals[0][0] < x['guest']), (duals[:1], x['guest']))
    p1592 = [p for p, h in x['patched'] if h == PS1592]
    p1592_pre = [p for p in p1592 if x['guest'] is None or p < x['guest']]
    ns = [n for _, n in x['pre_n']]
    pre_na = not ns and x['vke1'] is not None
    pre_ok = (len(ns) == 1 and rb is not None and ns[0] == rb['count']) or pre_na
    pre_name = 'one "PipelinePrecache: N recipes ->" line with N = count of the file before the tag'
    pre_det = (ns, rb['count'] if rb else None, 'not applicable: [Vulkan][E] before any N line' if pre_na else '')
    if cfg['patched'] == '>=1':
        kadd('>= 1 line DualSrcBlend: patched ps=%s before the first GuestOut line' % PS1592, len(p1592_pre) >= 1,
             (len(p1592_pre), len(x['patched'])))
        kadd(pre_name + ' (not applicable after a validation stop inside the precache - variant of the executor)', pre_ok,
             pre_det)
        kadd('no stale recipes line', not x['stale'], len(x['stale']))
        kadd('no "no ... pipelines.bin yet" line', not x['noyet'], len(x['noyet']))
    elif cfg['patched'] == '0':
        kadd('0 lines DualSrcBlend: patched', not x['patched'], len(x['patched']))
        kadd('no stale recipes line', not x['stale'], len(x['stale']))
    else:
        cadd(pre_name, len(ns) == 1 and rb is not None and ns[0] == rb['count'], pre_det)
        cadd('no stale recipes line', not x['stale'], len(x['stale']))
        cadd('no "no ... pipelines.bin yet" line', not x['noyet'], len(x['noyet']))
        cadd('>= 1 line DualSrcBlend: patched ps=%s' % PS1592, len(p1592) >= 1, (len(p1592), len(x['patched'])))
    if cfg['need_dual']:
        kadd('the recipe file before the tag holds a dual-source record', rb is not None and rb['dual'] >= 1,
             rb['dual'] if rb else None)
    r['entered'] = d['entered']
    r['first'] = d['first']
    r['guest_pos'] = x['guest']
    r['dt_after_first_s'] = d['dt_after_first_us'] / 1e6
    r['hold_s_json'] = at.get('hold_s')
    r['hold_exit'] = at.get('hold_exit')
    r['outcome'] = at.get('outcome')
    r['scene_change'] = d['change_pos'] is not None
    r['marks'] = [(m['kind'], m['cls'], m['src'], m['at_exit']) for m in marks]
    r['deaths'] = len(marks)
    r['vke'] = len(log['vke']) + (len(std['vke']) if std else 0)
    # first [Vulkan][E] line <= VKE_MAX chars from this file's own scan (sc142 keeps 200), the log first, then stdout
    r['vke_first'] = [t for t in (x['vke1_text'], xs['vke1_text'] if xs else None) if t][:1]
    r['stop_lines'] = len(x['stop']) + (len(xs['stop']) if xs else 0)
    r['stop_before_guest'] = bool(x['stop']) and (x['guest'] is None or x['stop'][0] < x['guest'])
    r['patched'] = [h for _, h in x['patched']]
    r['patched_1592_before_guest'] = len(p1592_pre)
    r['skip'] = [v for _, v in x['skip']]
    r['val'] = val
    r['k2_after_first'] = len(d['k2'])
    r['k2_list'] = d['k2'][:5]
    r['skip_lines'] = log['skip_lines']
    r['recipes'] = rb
    g = sc142.read_glitch(os.path.join(root, 'glitch_%s.txt' % tag))
    r['glitch'] = g
    sp_ = os.path.join(root, 'sheet_%s.png' % tag)
    r['sheet'] = os.path.isfile(sp_) and os.path.getsize(sp_) > 0
    dual_letter = len(duals) == 1 and duals[0][1] == (1, 1)
    r['not_evaluable_why'] = None
    if tag == 'f4c_b':
        # (b): a stop with the same text before the first GuestOut line; no stop -> NOT EVALUABLE (p.262(e))
        crit = r['stop_before_guest'] and not d['entered']
        r['verdict_letter'] = 'STOP SAME TEXT' if crit else 'NOT EVALUABLE'
        if not crit:
            r['not_evaluable_why'] = 'control (b) did not stop with the same text before GuestOut (p.262(e))'
    elif cfg['arm'] == 'W':
        hold_v = r['dt_after_first_s'] >= cfg['hold_s']
        clean = d['entered'] and not r['scene_change'] and r['vke'] == 0 and r['hold_exit'] is None
        if tag == 'f4c_a':
            clean = clean and x['guest'] is not None and r['deaths'] == 0 and dual_letter
        else:
            cadd('0 death markers (v)', r['deaths'] == 0, r['deaths'])
        r['hold_letter'] = hold_v
        r['verdict_letter'] = 'PASS' if clean and hold_v else 'FAIL'
    else:
        base = base or c14204(sc142)
        r['base'] = base
        new_kinds = sorted(set((m['cls'], m['kind']) for m in marks if not m['at_exit']) - set(tuple(k) for k in base['kinds']))
        new_k2 = r['k2_after_first'] > base['k2']
        r['new_k1k2'] = dict(kinds=new_kinds, k2=r['k2_after_first'], k2_base=base['k2'], new_k2=new_k2)
        hold_v = r['dt_after_first_s'] >= cfg['hold_s']
        vid = g is not None and g['video_frames'] >= FRAMES_V and g['glitches'] == 0 and r['sheet']
        r['video_ok'] = vid
        clean = d['entered'] and not r['scene_change'] and not new_kinds and not new_k2 and r['hold_exit'] is None
        r['hold_letter'] = hold_v
        r['verdict_letter'] = 'PASS' if clean and hold_v and vid else 'FAIL'
    r['controls'] = con
    r['controls_ok'] = all(ok for _, ok, _ in con)
    if not r['admitted']:
        r['verdict_letter'] = 'NOT ADMITTED'
        r['not_evaluable_why'] = None
    elif not r['controls_ok']:
        r['verdict_letter'] = 'NOT EVALUABLE'
        r['not_evaluable_why'] = 'controls of p.262(d) failed: %s' % [n for n, ok, _ in con if not ok]
    r['exec_members'] = ctl
    r['exec_ok'] = all(ok for _, ok, _ in ctl)
    return r


def text(r):
    L = ['f4c_read tag %s level %s arm %s KYTY_FIX_DUALSRC=%s log sha256 %s binary %s' % (
        r['tag'], r['cfg']['level'], r['cfg']['arm'], r['cfg']['fix'], r['log_sha'], (r['binary'] or '')[:16])]
    for name, ok, det in r['admit']:
        L.append('admit %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    for name, ok, det in r['controls']:
        L.append('control p.262(d) %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    for name, ok, det in r['exec_members']:
        L.append('executor member [I] %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    rb = r['recipes']
    L.append('recipe file before the tag: %s' % ('none' if rb is None else 'count %s sha256 %s dual-source records %s %s' % (
        rb['count'], rb['sha'], rb['dual'], rb.get('sig') or rb.get('error'))))
    L.append('DualSrcBlend patched lines %d (5514 before the first GuestOut %d) %s; skip lines %d %s' % (
        len(r['patched']), r['patched_1592_before_guest'], r['patched'][:4], len(r['skip']), r['skip'][:4]))
    L.append('entered %s first scene frame %s scene change %s first GuestOut at byte %s enter_scene outcome %s' % (
        r['entered'], r['first'], r['scene_change'], r['guest_pos'], r['outcome']))
    L.append('hold: sum dt after first %.1f s (the letter, p.262(e)); json hold_s %s (reference), hold_exit %s' % (
        r['dt_after_first_s'], r['hold_s_json'], r['hold_exit']))
    L.append('death markers %d %s' % (r['deaths'], r['marks'][:4]))
    L.append('validation noval/valfeat/vkany %d/%d/%d active %s; [Vulkan][E] %d' % (
        r['val']['noval'], r['val']['valfeat'], r['val']['vkany'], r['val']['ok'], r['vke']))
    L.append('first [Vulkan][E] line (<= %d chars): %s' % (VKE_MAX, [v.encode('ascii', 'replace').decode()
                                                                     for v in r['vke_first'][:1]]))
    L.append('stop text lines %d, first before the first GuestOut %s' % (r['stop_lines'], r['stop_before_guest']))
    L.append('K2 frames after first scene frame %d %s; AsyncPipelines skipped draw lines %d' % (
        r['k2_after_first'], r['k2_list'], r['skip_lines']))
    g = r['glitch']
    L.append('video: %s glitches %s sheet %s%s' % (g['video_frames'] if g else None, g['glitches'] if g else None, r['sheet'],
                                                  (' -> ok %s' % r['video_ok']) if 'video_ok' in r else ''))
    if 'new_k1k2' in r:
        b = r['base']
        L.append('c142_04 base: log sha256 %s kinds %s K2 %d sum dt after first %.1f s' % (b['log_sha'][:16], b['kinds'], b['k2'],
                                                                                         b['dt_after_first_s']))
        L.append('new K1/K2 against c142_04: kinds %s, K2 %d vs %d -> new K2 %s' % (
            r['new_k1k2']['kinds'], r['new_k1k2']['k2'], r['new_k1k2']['k2_base'], r['new_k1k2']['new_k2']))
    if 'hold_letter' in r:
        L.append('hold >= %d s by the sum of dt after the first scene frame: %s' % (r['cfg']['hold_s'], r['hold_letter']))
    if r.get('not_evaluable_why'):
        L.append('NOT EVALUABLE because: %s' % r['not_evaluable_why'])
    L.append('F4C VERDICT %s letter: %s' % (r['tag'], r['verdict_letter']))
    L.append('F4C EXECUTOR MEMBERS %s [I] (p.258(d), not the verdict): %s' % (
        r['tag'], 'all ok' if r['exec_ok'] else 'FAILED %s - question to the lead' % [n for n, ok, _ in r['exec_members'] if not ok]))
    return '\n'.join(L)


SEALED = ('go_f4c.sh', 'f4c_read.py', 'test_f4c_read.py', 'test_go_f4c.py', 'recipes143.py', 'shalist_f2c.py',
          'win_f4c.py', 'enter_scene.py', 'launch_run.py', 'run_safety99.py', 'idle142.py', 'procload.py', 'sheet142.py',
          'cachemf143.py', 'fgcpu143.py', 'gates_default.txt', SC142, 'C:/kyty/scripts/s51_vidglitch.py')
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
    """The series stop of go_f4c.sh after one tag (B4, p.262(e)): returns 'continue ...' or 'stop ...'."""
    if r is None:
        return 'stop: no reading (no log or no json)'
    if r.get('verdict_letter') == 'NOT ADMITTED':
        return 'stop: tag not admitted'
    if r.get('verdict_letter') == 'NOT EVALUABLE':
        return 'stop: %s NOT EVALUABLE (%s) - question to the lead' % (r.get('tag'), r.get('not_evaluable_why'))
    if r['tag'] == 'f4c_b':
        return 'continue: control (b) stopped with the same text'
    if r.get('deaths', 0) > 0 and r.get('vke', 0) == 0:
        return 'stop: death marker without a [Vulkan][E] line (%s)' % (r.get('marks') or [])[:1]
    if r.get('vke', 0) > 0:
        return 'continue: validation stop or error is data (%d [Vulkan][E])' % r['vke']
    return 'continue'


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
    if '--pre-check' in a and a.index('--pre-check') + 1 < len(a):
        t = a[a.index('--pre-check') + 1]
        if t not in TAGS:
            print('usage: --pre-check %s' % '|'.join(sorted(TAGS)))
            return 2
        print(pre_check(root, t))
        return 0
    if '--check-seal' in a and a.index('--check-seal') + 1 < len(a):
        ok, lines = check_seal(a[a.index('--check-seal') + 1])
        print('\n'.join(lines))
        print('check-seal %s' % ('OK' if ok else 'FAILED'))
        return 0 if ok else 1
    if '--c14204' in a:
        try:
            b = c14204(load(SC142, SC142_SHA, 'sc142'))
        except SystemExit as e:
            print('refused: %s' % e)
            return 2
        print('c142_04 base: log sha256 %s kinds %s K2 %d sum dt after first %.1f s first %s' % (
            b['log_sha'], b['kinds'], b['k2'], b['dt_after_first_s'], b['first']))
        return 0
    if '--tag' not in a or a.index('--tag') + 1 >= len(a) or a[a.index('--tag') + 1] not in TAGS:
        print('usage: f4c_read.py --tag %s [--root <dir>] [--json <out>]' % '|'.join(sorted(TAGS)))
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
