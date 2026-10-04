"""S13a4 (HPP-553, ROADMAP item 452 (b)-(d)): patch s13/sc_s13.py - RC1 (the data of item 446 (b)) and RC2 (the class "after the
arm"); the seal 13.  Every replacement must occur exactly once.  LF, ASCII.
    python patch_sc.py <path of sc_s13.py>
"""
import sys

NL = chr(10)
P = sys.argv[1]
src = open(P, 'rb').read().decode('ascii')
assert chr(13) not in src
REPL = []


def R(a, b):
    REPL.append((a, b))


# --- docstring
R('''  RC7  the sha of the manifest man_launch_glc is printed per U arm and w13 (a data line).
Output is ASCII only.''', '''  RC7  the sha of the manifest man_launch_glc is printed per U arm and w13 (a data line).
S13a4 (link HPP-553, item 452 (b)-(d); the review S13r2 ffae6160:docs/track-s/s13r2-review.md section 2; the seal pred/13_s.md
replaces 12, which is not in force):
  RC1  item 452 (b): the data of the reading of item 446 (b), per arm (U, w13, k_NN), a data line - entry_state, the members and
       the words do not read it: (i) the log line number and the text (ASCII, the path whole) of the first line
       "PipelinePrecache: no <path> yet", or "none"; (ii) the FrameTrace rows (the form the scorer counts frames by, the rows of
       RC4) after max(ready_line, nopb_line) when the line "PipelinePrecache: all pipelines created" is absent and both
       "ShaderPreparation: ready" and "no ... yet" are present; else "not counted" with the reason.  Beside them (executor's
       addition, data): whether the parent directory of the path is the variant of the seal line "installed:".
  RC2  item 452 (c): the admission rows fall into three classes by an EXPLICIT LIST OF NAMES (ADMIT_PRE, ADMIT_LOG, ADMIT_POST;
       not by position): "before the run" (json, environment, binary, prereg, the cache protocol before the arm), "by the log"
       (item 436 (b)(2) unchanged), "after the arm" (return_app, return_glc, the installed binary after the arm, the manifests
       man_post_app and man_post_glc, app_post_copy of k_NN).  A failing row after the arm is printed beside the arm and makes
       entry_state 'void' (item 436 (b)(3) unchanged) but does not gate the members of the arm - they count as without it.  A
       row of no list (or of two) is UNCLASSED: printed so and read as "before the run"; the suite fails on any such row of
       any arm kind (a new admission row without a class does not pass ALL OK).
Output is ASCII only.''')
# --- the seal 13
R("""SEAL_BASE = 'C:/kyty/s288/pred/12_s.md'       # the seal of S13a3: "installed: PENDING" (item 436 (v)(2): 11 not in force)
SEAL_B = 'C:/kyty/s288/pred/12b_s.md'         # its edition: the same lines, the line "installed:" named, the line "edition:"
SEAL_BASE_REL = 'pred/12_s.md'                # the name of the seal in the line "edition: base <name> sha256 <sha>" (RC6)""",
  """SEAL_BASE = 'C:/kyty/s288/pred/13_s.md'       # the seal of S13a4: "installed: PENDING" (item 452 (d)(2): 12 not in force)
SEAL_B = 'C:/kyty/s288/pred/13b_s.md'         # its edition: the same lines, the line "installed:" named, the line "edition:"
SEAL_BASE_REL = 'pred/13_s.md'                # the name of the seal in the line "edition: base <name> sha256 <sha>" (RC6)""")
R('''    """The seal in force: the edition 11b when it exists, else 11."""''',
  '''    """The seal in force: the edition 13b when it exists, else 13."""''')
R("NL = chr(10)\nFAMILIES = A.FAMILIES", "M_NOPB_END = b' yet'                                         # item 452 (b): the path is between M_NOPB "
  "and this\nNL = chr(10)\nFAMILIES = A.FAMILIES")
# --- scan_y: the text of the line "no ... yet"
R('''    pipelines.bin yet" (data)."""
    r = dict(compat=None, tcache=None, dual_before=False, guest_seen=False, vke=0, win={}, recover=0, ready_line=None,
             created_line=None, nopb_line=None)''', '''    pipelines.bin yet" (data); item 452 (b): the text of that line, ASCII (bytes above 127 as backslash escapes)."""
    r = dict(compat=None, tcache=None, dual_before=False, guest_seen=False, vke=0, win={}, recover=0, ready_line=None,
             created_line=None, nopb_line=None, nopb_text=None)''')
R('''                r['nopb_line'] = n
''', '''                r['nopb_line'] = n
                r['nopb_text'] = line.rstrip().decode('ascii', 'backslashreplace')
''')
# --- RC2: the classes by an explicit list of names
R('''def admit(spec, js, pred_sha, pred_path, cj, cjs_of, inst):''', '''def _rx(name):
    """An explicit row name; '{}' stands for the part that names the arm (tag, level, hold, source)."""
    return re.compile('^' + '.+?'.join(re.escape(p) for p in name.split('{}')) + '$')


# item 452 (c), RC2: the admission rows by an explicit list of names (not by position)
ADMIT_PRE = ('one attempt (--attempts 1, no warmup)',
             'arm binary = binary_sha256 of the json = the seal line "installed:" (item 414 (b))',
             'guest args -lvl {}', 'gates empty (shipped defaults)', 'no KYTY_GPU_CHECKPOINTS', 'no KYTY_GATE_SCHEDULE',
             'no KYTY_GAME_PATCH (item 342 (e))', 'KYTY_S_PCW=%s named in the env (item 419 (v) Z3, item 428 (v)(2))' % SPCW_ENV,
             'no KYTY_S_PCW_FORCE_MS / KYTY_FIX_* in the env (item 428 (v)(1))', 'video KYTY_REC rec_{}.mp4',
             'no video (KYTY_REC absent)', '--vulkan-validation {}',
             'W form line "%s" (item 295 (b)(4)), no VK_LAYER_MESSAGE_ID_FILTER' % W_FORM_LINE, 'VK_LAYER_PATH in the W env',
             'KYTY_* families = the seal (item 241 (v)(6), letter)', 'every KYTY_* key = the seal (executor variant, stricter)',
             'hold --hold {}', 'prereg = the seal', 'no pipeline-cache retry',
             'cache protocol json present', 'restore of the app caches = {}', 'GLCache not restored before the arm (as found)',
             'man_launch_glc right before the game = man_pre_glc (GLCache as found)',
             'the catalogue before the arm = seeds_manifest.txt of the export',
             'installed binary before the arm = the seal line "installed:" (S9r2 observation 3)',
             'return_prev_ok (no RETURN_FAILED / IN_ARM guard before the arm)',
             'manifest man_pre_app recorded', 'manifest man_pre_glc recorded', 'manifest glc_pre_copy recorded')
ADMIT_LOG = ('every S-pcw: line (>= 1) = "%s" with the KYTY_S_PCW of the env of the arm (item 419 (v) Z3)' % SPCW_FMT,
             '0 lines GamePatch: in the log (item 342 (e))',
             'the compatibility line carries the signature of the seal line "installed:"',
             'the translation cache line ends with the variant of the seal line "installed:"',
             'no window event minimized / Recovering Vulkan swapchain (item 273 (z))')
ADMIT_POST = ('return_app after the arm = its copy', 'return_glc after the arm = its copy',
              'installed binary after the arm = before the arm (item 250 (b))',
              'manifest man_post_app recorded', 'manifest man_post_glc recorded',
              'app_post_copy recorded (cat/{}, the next arm restores it)')
C_PRE, C_LOG, C_POST = 'before the run', 'by the log', 'after the arm'


def row_class(name):
    """Item 452 (c): the class of one admission row by its name - C_PRE, C_LOG, C_POST; None (UNCLASSED) when the name is in no
    list or in more than one."""
    hits = [c for c, names in ((C_PRE, ADMIT_PRE), (C_LOG, ADMIT_LOG), (C_POST, ADMIT_POST))
            if any(_rx(x).match(name) for x in names)]
    return hits[0] if len(hits) == 1 else None


def post_fail(r):
    """Item 452 (c): the failing admission rows of the class "after the arm"."""
    return [a[0] for a in r['admit'] if not a[1] and row_class(a[0]) == C_POST]


def gating_fail(r):
    """Item 452 (c): the failures that gate the members - every failing row but those after the arm."""
    post = set('admission: %s' % n for n in post_fail(r))
    return [x for x in r['fail'] if x not in post]


def admit(spec, js, pred_sha, pred_path, cj, cjs_of, inst):''')
R('''    r['admit'] = admit(spec, js, pred_sha, pred_path, cj, cjs_of, inst)
    r['n_pre'] = len(r['admit'])            # item 436 (b)(2): the rows before the run; the rows by the log follow them
''', '''    r['admit'] = admit(spec, js, pred_sha, pred_path, cj, cjs_of, inst)     # item 452 (c): classed by row_class
''')
R('''    if log142 is None:
        r.update(entered=False, ident=[], fail=['no log'], log_rows={'the log': 'missing'})
        return r''', '''    if log142 is None:
        r.update(entered=False, ident=[], fail=['no log'], log_rows={'the log': 'missing'}, nopb=None)
        return r''')
# --- RC1: the data of item 446 (b)
R('''    r['compat'] = sy['compat']
    r['tcache'] = sy['tcache']''', '''    r['nopb'] = nopb_data(s, sy, inst)       # item 452 (b), RC1: data only, no outcome reads it
    r['compat'] = sy['compat']
    r['tcache'] = sy['tcache']''')
R('''def frame_rows(s, fi, end):''', '''def nopb_data(s, sy, inst):
    """Item 452 (b), RC1 (data only): (i) the log line number and the text of the first "PipelinePrecache: no <path> yet" (None
    when absent); (ii) the FrameTrace rows after max(ready_line, nopb_line) when "PipelinePrecache: all pipelines created" is
    absent and both "ShaderPreparation: ready" and "no ... yet" are present, else None with the reason why it is not counted;
    the parent directory of the path against the variant of the seal line "installed:" (True / False; None when there is no
    line or the seal is PENDING)."""
    rd, nb, cr = sy['ready_line'], sy['nopb_line'], sy['created_line']
    if cr is not None:
        why = 'not counted: the line "PipelinePrecache: all pipelines created" is present (line %d)' % cr
    elif rd is None:
        why = 'not counted: no line "ShaderPreparation: ready"'
    elif nb is None:
        why = 'not counted: no line "PipelinePrecache: no ... yet"'
    else:
        why = None
    later = None if why is not None else max(rd, nb)
    rows = None if later is None else sum(1 for x in s['rows'] if x[4] > later)
    tx = sy['nopb_text']
    var = None
    if tx is not None and inst is not None and inst[2]:
        path = tx[len(M_NOPB):]
        path = path[:-len(M_NOPB_END)] if path.endswith(M_NOPB_END.decode('ascii')) else path
        parts = path.replace('/', chr(92)).split(chr(92))
        var = len(parts) >= 2 and parts[-2] == inst[2]
    return dict(line=nb, text=tx, later=later, rows_after=rows, why=why, variant=var)


def fmt_nopb(r):
    """Item 452 (b): the data line of the reading of item 446 (b) for one arm."""
    d = (r or {}).get('nopb')
    if d is None:
        return 'not made or no log'
    i = 'line %d "%s"' % (d['line'], d['text']) if d['line'] is not None else 'none'
    ii = '%d' % d['rows_after'] if d['why'] is None else d['why']
    return ('(i) "PipelinePrecache: no <path> yet": %s; (ii) FrameTrace rows after max(ShaderPreparation: ready line %s, '
            '"no ... yet" line %s): %s; the parent directory of the path = the variant of the seal line "installed:" '
            '(executor\\'s addition): %s' % (i, (r.get('prep_end') or {}).get('ready_line'), d['line'], ii,
                                             {True: 'yes', False: 'NO', None: 'n/a'}[d['variant']]))


def fmt_post(r):
    """Item 452 (c): the rows after the arm of one arm - ok or FAIL with the names."""
    if r is None:
        return 'not made'
    pf = post_fail(r)
    return 'ok' if not pf else 'FAIL %s - entry_state void, the members not gated' % '; '.join(pf)


def frame_rows(s, fi, end):''')
# --- the gate
R('''    """Item 436 (b)(2), RC2: ('pre', rows) - a failing admission row before the run (json, env, binary, prereg, the cache
    protocol); ('differs', rows) - a row by the log present and not the form, or a window event; ('missing', rows) - a row by the
    log whose line is not in the log; ('ok', [])."""
    pre = [a[0] for a in r['admit'][:r.get('n_pre', len(r['admit']))] if not a[1]]''',
  '''    """Item 436 (b)(2), RC2: ('pre', rows) - a failing admission row before the run (json, env, binary, prereg, the cache
    protocol before the arm) or an UNCLASSED one; ('differs', rows) - a row by the log present and not the form, or a window
    event; ('missing', rows) - a row by the log whose line is not in the log; ('ok', []).  Item 452 (c): a row after the arm
    does not gate."""
    pre = [a[0] for a in r['admit'] if not a[1] and row_class(a[0]) in (C_PRE, None)]''')
# --- members_w: the rows after the arm do not gate
R('''    if not ok_arm(r) or not r.get('entered') or not g:
        out.append(('W admitted and entered', None, 'admission / identity %s; entered %s' % (r['fail'][:3] or 'ok',
                                                                                             r.get('entered'))))''',
  '''    if gating_fail(r) or not r.get('entered') or not g:
        out.append(('W admitted and entered', None, 'admission / identity %s; entered %s' % (gating_fail(r)[:3] or 'ok',
                                                                                             r.get('entered'))))''')
# --- printing: read_known
R('''        out.append('%s GLCache at the launch man_launch_glc sha256 %s (item 436 (b)(7); not the driver cache of a first run of '
                   'the user)' % (t, (r or {}).get('glc_launch') or '-'))''',
  '''        out.append('%s GLCache at the launch man_launch_glc sha256 %s (item 436 (b)(7); not the driver cache of a first run of '
                   'the user)' % (t, (r or {}).get('glc_launch') or '-'))
        out.append('%s data of item 446 (b) (item 452 (b), no outcome reads it): %s' % (t, fmt_nopb(r)))
        out.append('%s rows after the arm (item 452 (c)): %s' % (t, fmt_post(r)))''')
R('''    out.append('w13 GLCache at the launch man_launch_glc sha256 %s (item 436 (b)(7))' % ((rw or {}).get('glc_launch') or '-'))''',
  '''    out.append('w13 GLCache at the launch man_launch_glc sha256 %s (item 436 (b)(7))' % ((rw or {}).get('glc_launch') or '-'))
    out.append('w13 data of item 446 (b) (item 452 (b), no outcome reads it): %s' % fmt_nopb(rw))
    out.append('w13 rows after the arm (item 452 (c)): %s' % fmt_post(rw))''')
# --- printing: read_k
R('''                                  ';'.join(m['kind'] for m in r['marks']) or 'none', r.get('window'), entry_state(r)))
    return out''', '''                                  ';'.join(m['kind'] for m in r['marks']) or 'none', r.get('window'), entry_state(r)))
        out.append('%s data of item 446 (b) (item 452 (b), no outcome reads it): %s' % (t, fmt_nopb(r)))
        out.append('%s rows after the arm (item 452 (c)): %s' % (t, fmt_post(r)))
    return out''')
# --- printing: fmt_arm
R('''    for j, (name, ok, det) in enumerate(r['admit']):
        o.append('  %-4s admit %s %s (%s)' % ('PASS' if ok else 'FAIL', 'before the run' if j < r.get('n_pre', 0) else 'by the log',
                                              name, det))
    kind, rows = admission_gate(r)
    o.append('  admission gate (item 436 (b)(2)): %s%s' % (kind, (' - ' + '; '.join(rows)) if rows else ''))''',
  '''    for name, ok, det in r['admit']:
        o.append('  %-4s admit %s %s (%s)' % ('PASS' if ok else 'FAIL', row_class(name) or 'UNCLASSED', name, det))
    kind, rows = admission_gate(r)
    o.append('  admission gate (item 436 (b)(2)): %s%s' % (kind, (' - ' + '; '.join(rows)) if rows else ''))
    o.append('  rows after the arm (item 452 (c)): %s' % fmt_post(r))''')
R('''                 pe.get('ready_line'), pe.get('created_line'), pe.get('rows_after'), pe.get('nopb_line')))
    o.append('  GLCache at the launch''', '''                 pe.get('ready_line'), pe.get('created_line'), pe.get('rows_after'), pe.get('nopb_line')))
    o.append('  data of item 446 (b) (item 452 (b), no outcome reads it): %s' % fmt_nopb(r))
    o.append('  GLCache at the launch''')
# --- the edition 13b
for a, b in (("""    \"\"\"The edition 12b (when it exists): every line of 12 except the lines "installed:" / "edition:" is in 12b in the same order
    and nothing else; 12 says "installed: PENDING" and carries no line "edition:"; 12b names the installed binary; item 436
    (b)(6), RC6: 12b carries exactly one line "edition: base pred/12_s.md sha256 <64 hex>" and its sha256 = the sha256 of the
    file of the seal 12.  Returns [(name, ok, detail)].\"\"\"""",
              """    \"\"\"The edition 13b (when it exists): every line of 13 except the lines "installed:" / "edition:" is in 13b in the same order
    and nothing else; 13 says "installed: PENDING" and carries no line "edition:"; 13b names the installed binary; item 436
    (b)(6), RC6: 13b carries exactly one line "edition: base pred/13_s.md sha256 <64 hex>" and its sha256 = the sha256 of the
    file of the seal 13.  Returns [(name, ok, detail)].\"\"\""""),
             ("        return [('edition 12b: the seal 12 exists', False, base)]", "        return [('edition 13b: the seal 13 exists', False, base)]"),
             ("""    rows.append(('edition 12b: every line of 12 but "installed:" / "edition:" is in 12b, in order, nothing else', ka == kb,""",
              """    rows.append(('edition 13b: every line of 13 but "installed:" / "edition:" is in 13b, in order, nothing else', ka == kb,"""),
             ("""    rows.append(('edition 12b: 12 says "installed: PENDING", 12b names the installed binary', ia is not None and""",
              """    rows.append(('edition 13b: 13 says "installed: PENDING", 13b names the installed binary', ia is not None and"""),
             ("""    rows.append(('edition 12b: the seal 12 carries no line "edition:"',""",
              """    rows.append(('edition 13b: the seal 13 carries no line "edition:"',"""),
             ("""    rows.append(('edition 12b: one line "edition: base %s sha256 <64 hex>" = the sha256 of the seal 12 (item 436 (b)(6))' % base_rel,""",
              """    rows.append(('edition 13b: one line "edition: base %s sha256 <64 hex>" = the sha256 of the seal 13 (item 436 (b)(6))' % base_rel,""")):
    R(a, b)

for a, b in REPL:
    n = src.count(a)
    if n != 1:
        raise SystemExit('patch_sc: the target occurs %d times: %r' % (n, a[:120]))
    src = src.replace(a, b)
src.encode('ascii')
open(P, 'wb').write(src.encode('ascii'))
print('patch_sc: %d replacements applied to %s' % (len(REPL), P))
