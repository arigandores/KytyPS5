"""Link 1b of s145 (HPP-379; ROADMAP s122 item 295): exact edits of C:/kyty/s145/sc145.py - each anchor must occur once.
ASCII only.  python p1b_sc.py"""
import hashlib
import sys

P = 'C:/kyty/s145/sc145.py'
src = open(P, 'rb').read().decode('utf-8')
assert '\r' not in src
N = [0]


def rep(old, new):
    c = src.count(old)
    if c != 1:
        print('ANCHOR COUNT %d: %r' % (c, old[:120]))
        sys.exit(1)
    N[0] += 1
    return src.replace(old, new)


src = rep('''The W form (item 254 (e), 273 (k)(2)): --vulkan-validation true, KYTY_PIPELINE_PRECACHE=0 and the filter of ONE message,
VK_LAYER_MESSAGE_ID_FILTER=Undefined-Value-ShaderOutputNotConsumed-DynamicRendering (the F6 warning "... it writes to
[Output variable, Location N, "out_mrt_N"] but there is no VkRenderingInfo::pColorAttachments[N] and this write is unused.",
the one message on which 13 W of s144 reached the duplicate limit - step0/f6scan145.out.txt; its VUID string by the layer
binary - step0/vuid145.out.txt).  Admission rows of profile 145: a W needs exactly that value in its json env, a V needs no
such variable.
''', '''The W form (item 254 (e), 273 (k)(2) as changed by item 295 (b); link 1b HPP-379, seal pred/03_sc145.md): --vulkan-validation
true, VK_LAYER_PATH, KYTY_PIPELINE_PRECACHE=0 and VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000; NO VK_LAYER_MESSAGE_ID_FILTER
(the filter of the one F6 message of step 0 is removed: it hid the only sign of the validation layer on the hold of every W -
review145.md RC1, option (A)).  Admission rows of a W of profile 145 instead of the row "W filter:" (item 295 (b)(1)-(4));
(1)-(3) are read on a HELD W (log present, no death marker, no hold_exit / ENDED / exited, attempt outcome ok), on another W
they print "n/a" and pass (a W stopped by validation keeps its outcome VALIDATION_STOP by the letter):
  W 295(b)(1)  0 layer limit lines ("this will be the last time reporting it", log and stdout);
  W 295(b)(2)  validation active: >= 1 line of the validation layer "[Vulkan][W][2]" or "[Vulkan][E][2]" (the third field
               2 = a validation message; the loader lines "[Vulkan][W][1]" are not counted), log and stdout;
  W 295(b)(3)  the last such line of the LOG lies at most 10 s (LAYER_END_US) of presented time before the last FrameTrace
               row of the hold: the sum of dt_us of the FrameTrace rows after its byte position up to that last row (the
               hold: the rows after the entry line, before a scene change) <= 10 000 000 us; no such line, no entry line or
               no hold row -> fail;
  W 295(b)(4)  the form line "W form: limit=<VK_LAYER_DUPLICATE_MESSAGE_LIMIT> filter=<VK_LAYER_MESSAGE_ID_FILTER or none>"
               built from the json env the harness writes (enter_scene.py) = "W form: limit=100000000 filter=none", and no
               VK_LAYER_MESSAGE_ID_FILTER key in that env (read on every W).
A V needs no VK_LAYER_MESSAGE_ID_FILTER (unchanged).
Data rows of item 295 (g), (d) (not gates): every "Window <id> <kind>" and "Mouse entered|left window <id>" line by kind (log
and stdout; the 15 kinds of window.cpp); for every K2 / K3 frame after the first scene frame the nearest window line of the
log within +-2 s of presented time (by byte position: a line's time is the end of the last FrameTrace row before it; the
distance is taken from the frame's interval [end - dt, end]) or "none"; next to the video continuity the share of FrameTrace
rows with a .idx record within 8 ms (all rows of the log; the 600 rows after the first scene frame, beside them the reading
600 rows from the first scene frame on) and the count of rows without a record (the continuity count) at the best shift of
the anchor in +-50 ms (1 ms steps; the most rows within 8 ms; a tie -> the smaller |shift|, then the negative one); the
counts at shift 0 and at the best shift differing by more than 10 % of the first (or 0 against > 0) -> the mark [I].
The gate (step2/gate145.py --before) stops on a failing W row of item 295 (b) of the made W right before (item 295 (v)).
''')

src = rep('''VKFILTER = 'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering'
''', '''W_FORM_LINE = 'W form: limit=100000000 filter=none'
LAYER_END_US = 10000000
WIN_NEAR_US = 2000000
VQ_NEAR = 0.008
VQ_SHIFT_MS = 50
VQ_ROWS = 600
VQ_MARK = 0.10
''')

src = rep("PRED_PATH = 'C:/kyty/s145/pred/02_sc145.md'", "PRED_PATH = 'C:/kyty/s145/pred/03_sc145.md'")

src = rep("""                'C:/kyty/s144/step2/times.txt', 'C:/kyty/s144/pred/01_sc144.md')
SEALED144 = (""", """                'C:/kyty/s144/step2/times.txt', 'C:/kyty/s144/pred/01_sc144.md',
                'C:/kyty/s144/runs144/cache_w144_20.after.json')
SEALED144 = (""")

src = rep("""REGRESS144_LIMIT = ('w144_02', 'w144_05', 'w144_06', 'w144_07', 'w144_08', 'w144_10', 'w144_11', 'w144_12', 'w144_13',
                    'w144_14', 'w144_15', 'w144_16', 'w144_17')
""", """REGRESS144_LIMIT = ('w144_02', 'w144_05', 'w144_06', 'w144_07', 'w144_08', 'w144_10', 'w144_11', 'w144_12', 'w144_13',
                    'w144_14', 'w144_15', 'w144_16', 'w144_17')
REGRESS144_NOTHELD = ('w144_09', 'w144_20')
REGRESS144_B3 = REGRESS144_LIMIT
""")

src = rep("""RX_VKT = re.compile(rb'\\[Vulkan\\]\\[\\w\\]\\[(\\d+)\\]')
""", """RX_VKT = re.compile(rb'\\[Vulkan\\]\\[\\w\\]\\[(\\d+)\\]')
RX_VKT2 = re.compile(rb'\\[Vulkan\\]\\[[WE]\\]\\[2\\]')
RX_WALL = re.compile(rb'Window \\d+ (shown|hidden|exposed|moved to|resized|size changed|minimized|maximized|restored|gained '
                     rb'keyboard focus|lost keyboard focus|closed|got unknown event)\\b|Mouse (entered|left) window \\d+')
WIN_ALL = ('shown', 'hidden', 'exposed', 'moved to', 'resized', 'size changed', 'minimized', 'maximized', 'restored',
           'gained keyboard focus', 'lost keyboard focus', 'closed', 'got unknown event', 'Mouse entered window',
           'Mouse left window')
""")

src = rep("""               guestout=None, precache=0, precache_any=0, win=dict((k, 0) for k in WIN_KEYS), rec=0, limit=0, f6=0,
               vkval=0)
""", """               guestout=None, precache=0, precache_any=0, win=dict((k, 0) for k in WIN_KEYS), rec=0, limit=0, f6=0,
               vkval=0, vk2=0, vk2_last=None, winall=dict((k, 0) for k in WIN_ALL), winpos=[])
""")

src = rep("""            for m in RX_VKT.finditer(whole):
                if int(m.group(1)) & 2:
                    res['vkval'] += 1
""", """            for m in RX_VKT.finditer(whole):
                if int(m.group(1)) & 2:
                    res['vkval'] += 1
            for m in RX_VKT2.finditer(whole):
                res['vk2'] += 1
                res['vk2_last'] = base + m.start()
            for m in RX_WALL.finditer(whole):
                k = m.group(1).decode() if m.group(1) else 'Mouse %s window' % m.group(2).decode()
                res['winall'][k] += 1
                res['winpos'].append((k, base + m.start()))
""")

src = rep("""    ends.reverse()
    after = []
    before = 0
""", """    ends.reverse()
    ends = [x + shift for x in ends]
    after = []
    before = 0
""")
src = rep("def vcont(rows, it, fn):\n", "def vcont(rows, it, fn, shift=0.0):\n")
src = rep("""    frame (its n is fn); else dict(after = such rows after the first scene frame, gaps = the gaps holding them, before = such
    rows at or before it, longest = (rows, first n, last n, gap s, record index) of the gap with the most rows among the
    gaps holding rows after it, or None).\"\"\"
""", """    frame (its n is fn); else dict(after = such rows after the first scene frame, gaps = the gaps holding them, before = such
    rows at or before it, longest = (rows, first n, last n, gap s, record index) of the gap with the most rows among the
    gaps holding rows after it, or None).  shift (s, item 295 (d)) moves every row end after the anchoring.\"\"\"
""")

src = rep("""def fmt_vcont(vc):
""", """def near_count(ends, it):
    \"\"\"Item 295 (d): the number of row ends with a .idx record within VQ_NEAR (records sorted by time).\"\"\"
    n = 0
    for e in ends:
        k = bisect.bisect_left(it, e)
        d = min(abs(it[k] - e) if k < len(it) else 9.0, abs(it[k - 1] - e) if k > 0 else 9.0)
        if d <= VQ_NEAR:
            n += 1
    return n


def vquality(rows, it, fn):
    \"\"\"Item 295 (d): the quality of the alignment the continuity count rests on.  None without rows, records or a first
    scene frame (or its row); else dict(rows, near = rows of the log whose end (anchored as in vcont) has a .idx record within
    VQ_NEAR; n600 / near600 = the same over the VQ_ROWS rows AFTER the first scene frame (the letter) and n600f / near600f =
    over VQ_ROWS rows FROM it on (the first scene frame included; the reading of review145.md); shift = the best shift of
    the anchor in ms in -VQ_SHIFT_MS..+VQ_SHIFT_MS (the most rows within VQ_NEAR; a tie -> the smaller |shift|, then the
    negative one), near_best; after0 = the continuity count at shift 0, after_best = at the best shift; mark = the two
    counts differ by more than VQ_MARK of after0 (after0 = 0: any count above 0)).\"\"\"
    if not rows or not it or fn is None:
        return None
    fi = None
    for i, r in enumerate(rows):
        if r[0] == fn:
            fi = i
            break
    if fi is None:
        return None
    base = []
    c = 0.0
    for r in reversed(rows):
        base.append(it[-1] - c)
        c += r[1] / 1e6
    base.reverse()
    best = None
    for s in range(-VQ_SHIFT_MS, VQ_SHIFT_MS + 1):
        n = near_count([x + s / 1000.0 for x in base], it)
        if best is None or n > best[1] or (n == best[1] and (abs(s) < abs(best[0]) or (abs(s) == abs(best[0]) and s < 0))):
            best = (s, n)
    a0 = vcont(rows, it, fn)['after']
    ab = vcont(rows, it, fn, best[0] / 1000.0)['after']
    w = base[fi + 1:fi + 1 + VQ_ROWS]
    wf = base[fi:fi + VQ_ROWS]
    return dict(rows=len(rows), near=near_count(base, it), n600=len(w), near600=near_count(w, it), n600f=len(wf),
                near600f=near_count(wf, it), shift=best[0], near_best=best[1], after0=a0, after_best=ab,
                mark=(abs(ab - a0) > VQ_MARK * a0) if a0 else ab > 0)


def fmt_vq(q):
    if q is None:
        return 'n/a (no video index, no FrameTrace row or no first scene frame)'
    return ('rows with a .idx record within 8 ms: %d of %d (%.1f %%); in the %d rows after the first scene frame %d (%.1f %%) '
            '[from the first scene frame on: %d of %d]; best shift of the anchor in +-50 ms %+d ms (%d rows within 8 ms); rows '
            'without a record after the first scene frame: %d at shift 0, %d at the best shift%s' % (
                q['near'], q['rows'], 100.0 * q['near'] / q['rows'], q['n600'], q['near600'],
                100.0 * q['near600'] / q['n600'] if q['n600'] else 0.0, q['near600f'], q['n600f'], q['shift'], q['near_best'],
                q['after0'], q['after_best'], ' - [I] the counts differ by more than 10 %' if q['mark'] else ''))


def win_near(sc, d):
    \"\"\"Item 295 (g): [(n, dt_us, class, place, nearest)] for every frame after the first scene frame (before a scene change)
    with dt_us >= K3_US: class K2 (>= K2_US) or K3, place entry (the ENTRY_WIN rows of the window) or hold; nearest = (kind,
    signed offset us) of the window line of the log nearest to the frame's interval [end - dt, end] of presented time, within
    WIN_NEAR_US, or None.  A line's time is the end of the last FrameTrace row before its byte position (0 before any row).\"\"\"
    if d['first'] is None or d['entry_pos'] is None:
        return []
    rows = sc['rows']
    ends = []
    c = 0
    for r in rows:
        c += r[1]
        ends.append(c)
    pos = [r[3] for r in rows]
    epos, cpos = d['entry_pos'], d['change_pos']
    after = [i for i, r in enumerate(rows) if r[3] > epos and (cpos is None or r[3] < cpos)]
    fi = None
    for j, i in enumerate(after):
        if rows[i][2] >= SCENE_DRAWS:
            fi = j
            break
    if fi is None:
        return []
    lines = []
    for k, q in sc['winpos']:
        x = bisect.bisect_left(pos, q)
        lines.append((k, ends[x - 1] if x > 0 else 0))
    out = []
    for j, i in enumerate(after[fi + 1:]):
        dt = rows[i][1]
        if dt < K3_US:
            continue
        hi, lo = ends[i], ends[i] - dt
        best = None
        for k, t in lines:
            off = t - lo if t < lo else (t - hi if t > hi else 0)
            if abs(off) <= WIN_NEAR_US and (best is None or abs(off) < abs(best[1])):
                best = (k, off)
        out.append((rows[i][0], dt, 'K2' if dt >= K2_US else 'K3', 'entry' if j < ENTRY_WIN else 'hold', best))
    return out


def fmt_near(wn):
    if not wn:
        return 'no K2 / K3 frame after the first scene frame'
    k2 = [x for x in wn if x[2] == 'K2']
    hit = ['n %d %s %s dt %d -> %s %+.3f s' % (x[0], x[2], x[3], x[1], x[4][0], x[4][1] / 1e6) for x in wn if x[4] is not None]
    k2n = ['n %d K2 %s dt %d -> none' % (x[0], x[3], x[1]) for x in k2 if x[4] is None]
    k3n = sum(1 for x in wn if x[2] == 'K3' and x[4] is None)
    return 'K2 %d frames, K3 %d frames; with a window line within 2 s: %s; K2 without one: %s; K3 without one (none): %d' % (
        len(k2), len(wn) - len(k2), '; '.join(hit) or 'none', '; '.join(k2n) or 'none', k3n)


def fmt_winall(w):
    return ', '.join('%s %d' % (k, w[k]) for k in WIN_ALL)


def w_form4(env):
    \"\"\"Item 295 (b)(4): (ok, the form line built from the json env).\"\"\"
    fl = env.get('VK_LAYER_MESSAGE_ID_FILTER')
    fm = 'W form: limit=%s filter=%s' % (env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT'), 'none' if fl is None else fl)
    return fm == W_FORM_LINE and 'VK_LAYER_MESSAGE_ID_FILTER' not in env, fm


def w_held(r):
    \"\"\"Item 295 (b): (held, reason) - a HELD W: log present, no death marker, no hold_exit / ENDED / exited, attempt ok.\"\"\"
    if not r['log_present']:
        return False, 'log missing'
    if r['marks']:
        return False, 'death marker %s' % r['marks'][0]['kind']
    if r['ended'] or r['exited']:
        return False, 'hold_exit / ENDED / exited'
    if r['attempt_outcome'] != 'ok':
        return False, 'attempt outcome %s' % r['attempt_outcome']
    return True, 'held'


def layer_end(sc, d):
    \"\"\"Item 295 (b)(3): the presented time (us) from the last validation-layer line of the log to the last FrameTrace row of
    the hold - the sum of dt_us of the hold rows after the line's byte position; None without such a line, without the entry
    line or without a hold row.\"\"\"
    lp = sc['vk2_last']
    epos, cpos = d['entry_pos'], d['change_pos']
    if lp is None or epos is None:
        return None
    hold = [r for r in sc['rows'] if r[3] > epos and (cpos is None or r[3] < cpos)]
    if not hold:
        return None
    return sum(r[1] for r in hold if r[3] > lp)


W295 = ('W 295(b)(1) 0 layer limit lines ("this will be the last time reporting it", log and stdout; item 295 (b)(1))',
        'W 295(b)(2) validation active: >= 1 validation-layer line [Vulkan][W][2] / [Vulkan][E][2], loader lines [1] not '
        'counted (log and stdout; item 295 (b)(2))',
        'W 295(b)(3) the last validation-layer line of the log at most 10 s of presented time before the last FrameTrace row '
        'of the hold (item 295 (b)(3))')


def w_form_rows(r):
    \"\"\"Item 295 (b)(1)-(3): the admission rows of a W (n/a and passing on a W that is not held).\"\"\"
    held, why = r['held']
    if not held:
        return [(name, True, 'n/a (W not held: %s)' % why) for name in W295]
    le = r['layer_end']
    return [(W295[0], r['limit'] == 0, r['limit']), (W295[1], r['vk2'] >= 1, r['vk2']),
            (W295[2], le is not None and le <= LAYER_END_US, 'none' if le is None else '%d us' % le)]


def fmt_vcont(vc):
""")

src = rep("""    if FORM145:
        fl = env.get('VK_LAYER_MESSAGE_ID_FILTER')
        if is_w:
            add('W filter: VK_LAYER_MESSAGE_ID_FILTER = %s, one id (item 273 (k)(2))' % VKFILTER, fl == VKFILTER, fl)
        else:
""", """    if FORM145:
        fl = env.get('VK_LAYER_MESSAGE_ID_FILTER')
        if is_w:
            f4, fm = w_form4(env)
            add('W 295(b)(4) form line "%s" from the json env the harness writes, no VK_LAYER_MESSAGE_ID_FILTER in it (item '
                '295 (b)(4))' % W_FORM_LINE, f4, fm)
        else:
""")

src = rep("""    r['vkval'] = sum(sc['vkval'] for sc in (log, std) if sc is not None)
""", """    r['vkval'] = sum(sc['vkval'] for sc in (log, std) if sc is not None)
    r['vk2'] = sum(sc['vk2'] for sc in (log, std) if sc is not None)
    r['winall'] = dict((k, sum(sc['winall'][k] for sc in (log, std) if sc is not None)) for k in WIN_ALL)
    r['winnear'] = win_near(log, d) if log is not None else []
    r['held'] = w_held(r)
    r['layer_end'] = layer_end(log, d) if log is not None else None
    r['form4'] = w_form4(js.get('env') or {})
""")

src = rep("""    if tag in W_TAGS:
        r['admit'].append(('validation active (0 no validation layer, >= 1 VK_EXT_validation_features, >= 1 [Vulkan][)',
                           r['val']['ok'], '%d/%d/%d' % (r['val']['noval'], r['val']['valfeat'], r['val']['vkany'])))
""", """    if tag in W_TAGS:
        r['admit'].append(('validation active (0 no validation layer, >= 1 VK_EXT_validation_features, >= 1 [Vulkan][)',
                           r['val']['ok'], '%d/%d/%d' % (r['val']['noval'], r['val']['valfeat'], r['val']['vkany'])))
        if FORM145:
            r['admit'].extend(w_form_rows(r))
""")

src = rep("""                       d['first'][0] if d['first'] is not None else None) if tag in V_TAGS else None
""", """                       d['first'][0] if d['first'] is not None else None) if tag in V_TAGS else None
    r['vq'] = vquality(log['rows'] if log is not None else [], idx_times(os.path.join(root, 'rec_%s.mp4.idx' % tag)),
                       d['first'][0] if d['first'] is not None else None) if tag in V_TAGS else None
""")

src = rep("""            o.append('  message filter (item 273 (k)(2)): lines of the filtered F6 text ("... and this write is unused.") %d; '
                     '[Vulkan][ lines of the validation type (bit 2) %d (info, not in the verdict)' % (r['f6'], r['vkval']))
        else:
            o.append('  video continuity (B38, item 273 (k)(3), the method of AUDIT144 s1.3; data next to SCENE_OK, not a '
                     'gate): %s' % fmt_vcont(r['vcont']))
""", """            le = r['layer_end']
            o.append('  W form of item 295 (b): %s; the form line "%s" (%s); validation-layer lines [W][2] / [E][2] %d (log and '
                     'stdout); the last one of the log %s before the last FrameTrace row of the hold; F6 text lines ("... and '
                     'this write is unused.") %d; [Vulkan][ lines of the validation type (bit 2) %d (info)' % (
                         'held' if r['held'][0] else 'NOT held (%s) - rows (1)-(3) n/a' % r['held'][1], r['form4'][1],
                         'PASS' if r['form4'][0] else 'FAIL', r['vk2'], 'none' if le is None else '%.3f s' % (le / 1e6),
                         r['f6'], r['vkval']))
        else:
            o.append('  video continuity (B38, item 273 (k)(3), the method of AUDIT144 s1.3; data next to SCENE_OK, not a '
                     'gate): %s' % fmt_vcont(r['vcont']))
            o.append('  video continuity alignment (item 295 (d); data, not a gate): %s' % fmt_vq(r['vq']))
        o.append('  window lines by kind (item 295 (g); log and stdout; data): %s' % fmt_winall(r['winall']))
        o.append('  window line nearest each K2 / K3 frame after the first scene frame (item 295 (g); +-2 s of presented time '
                 'by byte position in the log; data): %s' % fmt_near(r['winnear']))
""")

src = rep("""        fbad = [t for t in wm if not all(a[1] for a in ents[t]['admit'] if a[0].startswith('W filter'))]
        vfl = [t for t in vm if not all(a[1] for a in ents[t]['admit'] if 'VK_LAYER_MESSAGE_ID_FILTER' in a[0])]
        out.append('W FILTER (item 273 (k)(2)): VK_LAYER_MESSAGE_ID_FILTER=%s in %d of %d made W; V without it %d of %d made; '
                   'violated: %s; lines of the filtered F6 text in the W (info): %s' % (
                       VKFILTER, len(wm) - len(fbad), len(wm), len(vm) - len(vfl), len(vm), ','.join(fbad + vfl) or 'none',
                       ', '.join('%s %d' % (t, ents[t]['f6']) for t in wm) or 'none'))
""", """        fbad = [(t, [a[0][:11] for a in ents[t]['admit'] if a[0].startswith('W 295(b)(') and not a[1]]) for t in wm]
        fbad = [x for x in fbad if x[1]]
        vfl = [t for t in vm if not all(a[1] for a in ents[t]['admit'] if 'VK_LAYER_MESSAGE_ID_FILTER' in a[0])]
        nh = [t for t in wm if not ents[t]['held'][0]]
        out.append('W FORM 295 (item 295 (b)(1)-(4): 0 layer limit lines, validation active by [W][2] / [E][2] lines, the last '
                   'one within 10 s of the hold end, the form line %s): every row passed by %d of %d made W; failing: %s; not '
                   'held (rows (1)-(3) n/a): %s; V without VK_LAYER_MESSAGE_ID_FILTER %d of %d made, violated: %s; F6 text '
                   'lines in the W (info): %s' % (
                       W_FORM_LINE, len(wm) - len(fbad), len(wm),
                       '; '.join('%s %s' % (t, ','.join(x[5:] for x in b)) for t, b in fbad) or 'none',
                       ','.join(nh) or 'none', len(vm) - len(vfl), len(vm), ','.join(vfl) or 'none',
                       ', '.join('%s %d' % (t, ents[t]['f6']) for t in wm) or 'none'))
        wk = [t for t in made_e if any(ents[t]['winall'].values())]
        out.append('WINDOW LINES BY KIND (item 295 (g); log and stdout; data): %s' % (
            '; '.join('%s: %s' % (t, ', '.join('%s %d' % (k, ents[t]['winall'][k]) for k in WIN_ALL if ents[t]['winall'][k]))
                      for t in wk) or 'none'))
        nr = [(t, x) for t in made_e for x in ents[t]['winnear'] if x[4] is not None]
        out.append('WINDOW LINE NEAR A K2 / K3 FRAME (item 295 (g); within 2 s; data): %s' % (
            '; '.join('%s n %d %s %s -> %s %+.3f s' % (t, x[0], x[2], x[3], x[4][0], x[4][1] / 1e6) for t, x in nr) or 'none'))
        vqm = [t for t in vm if ents[t]['vq'] is not None and ents[t]['vq']['mark']]
        out.append('VIDEO CONTINUITY ALIGNMENT (item 295 (d); data, not a gate): V whose count at the best anchor shift differs '
                   'by more than 10 %% [I]: %s' % (', '.join('%s %d -> %d (%+d ms)' % (
                       t, ents[t]['vq']['after0'], ents[t]['vq']['after_best'], ents[t]['vq']['shift']) for t in vqm) or 'none'))
""")

# regress144: the new lines of item 295 apart (prefix NEW295), the old lines unchanged
src = rep("""        if t in wtags:
            lines.append('NEW %s W: window %s; layer limit lines %s; F6 text lines %d; [Vulkan][ lines of the validation type '
                         '%d' % (t, fmt_win(e['win']), e['limit'], e['f6'], e['vkval']))
        else:
""", """        if t in wtags:
            lines.append('NEW %s W: window %s; layer limit lines %s; F6 text lines %d; [Vulkan][ lines of the validation type '
                         '%d' % (t, fmt_win(e['win']), e['limit'], e['f6'], e['vkval']))
            rs = w_form_rows(e)
            res295[t] = [x[1] for x in rs] + [e['form4'][0]]
            lines.append('NEW295 %s W: %s; %s; (b)(4) %s -> %s; window lines %s; near K2 / K3: %s' % (
                t, 'held' if e['held'][0] else 'NOT held (%s)' % e['held'][1],
                '; '.join('(b)(%d) %s -> %s' % (i + 1, x[2], 'PASS' if x[1] else 'FAIL') for i, x in enumerate(rs)),
                e['form4'][1], 'PASS' if e['form4'][0] else 'FAIL', fmt_winall(e['winall']), fmt_near(e['winnear'])))
        else:
""")
src = rep("""            lines.append('NEW %s V: window %s; continuity %s; AUDIT144 vidcont144 %s -> %s' % (
                t, fmt_win(e['win']), fmt_vcont(vc), au, 'equal' if eq else 'DIFFERENT'))
""", """            lines.append('NEW %s V: window %s; continuity %s; AUDIT144 vidcont144 %s -> %s' % (
                t, fmt_win(e['win']), fmt_vcont(vc), au, 'equal' if eq else 'DIFFERENT'))
            lines.append('NEW295 %s V: window lines %s; near K2 / K3: %s; continuity alignment %s' % (
                t, fmt_winall(e['winall']), fmt_near(e['winnear']), fmt_vq(e['vq'])))
""")
src = rep("""    va = vcont_audit(vexpect)
    vc_n = vc_eq = 0
""", """    va = vcont_audit(vexpect)
    vc_n = vc_eq = 0
    res295 = {}
""")
src = rep("""    lines.append('NEW ROWS continuity: %d of %d V equal to %s (V of the profile %d) -> %s' % (
        vc_eq, vc_n, vexpect, nv, 'PASS' if vc_ok else 'FAIL'))
    ok = same and win_ok and lim_ok and vc_ok
""", """    lines.append('NEW ROWS continuity: %d of %d V equal to %s (V of the profile %d) -> %s' % (
        vc_eq, vc_n, vexpect, nv, 'PASS' if vc_ok else 'FAIL'))
    wt = [t for t in tags if t in res295]
    nh = tuple(t for t in wt if not ents[t]['held'][0])
    fl = [tuple(t for t in wt if not res295[t][i]) for i in range(4)]
    exp = (REGRESS144_LIMIT, (), REGRESS144_LIMIT, tuple(wt))
    m_ok = [fl[i] == exp[i] for i in range(4)]
    nh_ok = nh == REGRESS144_NOTHELD
    lines.append('NEW295 ROWS held: W not held (rows (1)-(3) n/a) %s (expected %s: stopped by validation) -> %s' % (
        ','.join(nh) or 'none', ','.join(REGRESS144_NOTHELD), 'PASS' if nh_ok else 'FAIL'))
    for i, what in enumerate(('(b)(1) layer limit lines 0: fails at the 13 W of s144 with the limit (expected by the data of '
                              's144, item 295 (z))', '(b)(2) validation active by [W][2] / [E][2] lines: fails nowhere',
                              '(b)(3) the last layer line within 10 s of the hold end: fails at the 13 W with the limit (F6 '
                              'ends at the limit line)', '(b)(4) the form line: fails at every W of s144 (its form: limit '
                              '1000000)')):
        lines.append('NEW295 ROWS %s: failing %d %s -> %s' % (what, len(fl[i]), ','.join(fl[i]) or 'none',
                                                              'PASS' if m_ok[i] else 'FAIL'))
    ok = same and win_ok and lim_ok and vc_ok and nh_ok and all(m_ok)
""")

open(P, 'wb').write(src.encode('ascii'))
print('edits %d; sc145.py sha256 %s' % (N[0], hashlib.sha256(src.encode('ascii')).hexdigest()))
