"""patch_sc_s15.py - S15a (HPP-601): the semantic changes of item 511 (z)(3)-(5) and (z)(i) on the mechanical port sc_s15.py.
Every anchor must occur exactly once.  LF, ASCII.
    python patch_sc_s15.py <sc_s15.py>
"""
import sys

NL = chr(10)
P = sys.argv[1]
t = open(P, 'rb').read().decode('ascii').replace(chr(13) + NL, NL)

R = []


def rep(old, new):
    R.append((old, new))


# ---------------------------------------------------------------------------------------------------- the header
rep('''"""sc_s15.py - the scorer of track S, fourth wave, the catalogue of the 19 known levels (link S13a, HPP-498; ROADMAP "SESSION''',
    '''"""sc_s15.py - the scorer of track S, fifth wave S15 (link S15a, HPP-601; ROADMAP "SESSION 122" item 511 (z)): the port of
s13/sc_s13.py (seal 13, sha256 a0c66cc9ae2efe53272724d05dbb9a3f72e22cc000af2945d10029d559b06237) into C:/kyty/s288/s15 for the
arms of link S15b on the installed FS8 after FS8e (the seal pred/14_s.md says "installed: PENDING"; the edition pred/14b_s.md is a
lead item).  The changes against sc_s13.py (every other rule unchanged - item 511 (z)(6): the attribution, the members (e)(1),
(e)(3), RC1-RC7 of item 436, the answers of items 446, 452):
  (z)(3)  the collection arms k_01 .. k_19 hold HOLD_K = 300 s (was 180 s).
  (z)(4)  a U arm is held by enter_scene_s15.py --hold-u U_RULE ("120:3000:300"): while the presented time after the first scene
          frame is < 120 s or the video holds < 3 000 frames, but not longer than 300 s of presented time after the first scene
          frame (HOLD_U = 300 is the --hold of the arm; the wall cap is 300 + 60 s).  Admission row "before the run": the json
          carries the hold rule of the arm (hold_rule = HOLD_RULE_U on a U arm, absent on k / w13).  A video below 3 000 frames
          at the end of the hold is E3-video FAIL by the letter (unchanged member).  The hold end of the attempt (cause, anchor,
          presented time, video frames) is a data line per U arm.
  (z)(5)  an arm with the entry line of its level and WITHOUT a first scene frame (ps_logo): the E1 domain is every FrameTrace row
          after the entry line (the rows i >= eg, eg = the rows before the entry line) to the end of the hold - a scene change does
          not cut it (item 436 (b)(1)); the reading 2 of sc_s (no held first frame to add - there is no first scene frame); its
          presented time < 120 s without a death marker -> the E1 members UNDETERMINED (DOMAIN_MIN_US unchanged).  The domain line
          names the anchor ("first scene frame" / "entry line (item 511 (z)(5))").
  (z)(i)  the identities T-1, T-2, T-6 on the domain by the ROW that counts a line, not by frame=: T-1 - the "AsyncPipelines:
          skipped draw" lines of the groups g >= lo (a line of group g is logged after the row g-1 and counted by the row g) = the
          sum of skc_ap_skip of the rows i >= lo; T-6 - the distinct frame= of the same lines = the sum of skc_held_inc of the
          same rows; T-2 - the "AsyncPipelines: flip N held" lines with N >= the n of the row lo, capped as the emulator caps
          them (min(64 - the held lines before, the sum of skc_held_inc of the rows i >= lo)); lo = the first scene frame, else
          the entry row eg (z)(5), else the whole log - and never below row 1 (lines before the first FrameTrace row are counted by
          no row).  The cause [c, S13b logs]: k_01 - the line "flip 1 held" comes before the first FrameTrace row (n = 2), no row
          counts it (T-2 2 / 3); k_02 - a line "skipped draw frame=240" is logged after the row n = 235 and counted by the row
          n = 236 < the first scene frame 238 (frame= runs 2-4 ahead of n), so the cut by frame= >= 238 takes it and the cut by
          n >= 238 does not (T-1 325 / 326).  By the row: 39 of 39 S13b logs equal on T-1, T-2, T-6 (s15/ident_s15.out.txt).  The
          rows of item 404 (sc_s9.ident_domain, by frame=) are printed beside as one data row, no outcome reads them.
The S13 text below is kept (its "S13b" reads "S15b" for the arms of this seal).
Port header of sc_s13.py:  the scorer of track S, fourth wave, the catalogue of the 19 known levels (link S13a, HPP-498; ROADMAP "SESSION''')

# ---------------------------------------------------------------------------------------------------- constants
rep("SEAL_BASE = 'C:/kyty/s288/pred/14_s.md'       # the seal of S13a4: \"installed: PENDING\" (item 452 (d)(2): 12 not in force)",
    "SEAL_BASE = 'C:/kyty/s288/pred/14_s.md'       # the seal of S15a: \"installed: PENDING\" (item 511 (z)(1))")
rep("HOLD_K = 180                     # executor's variant: the collection holds 60 s longer than the U arm it serves",
    "HOLD_K = 300                     # item 511 (z)(3): the collection holds 300 s (was 180 s)")
rep("HOLD_U = 120                     # item 355 (e): the form U arm, 120 s",
    "HOLD_U = 300                     # item 511 (z)(4): the --hold of a U arm = the cap of its hold rule, 300 s\n"
    "U_MIN_S = 120                    # item 511 (z)(4): presented after the first scene frame (or the entry line, (z)(5))\n"
    "U_CAP_S = 300                    # item 511 (z)(4): not longer than 300 s presented after the first scene frame\n"
    "U_WALL_EXTRA_S = 60              # enter_scene_s15.py: the wall cap of a U hold is U_CAP_S + 60 s (executor's variant)\n"
    "U_SCENE_DRAWS = 100              # enter_scene_s15.py SCENE_DRAWS_U = sc_s.SCENE_DRAWS (the first scene frame)")
rep("FRAMES_VIDEO = 3000              # item 229 (e)(3)",
    "FRAMES_VIDEO = 3000              # item 229 (e)(3); item 511 (z)(4): the video frames of the U hold rule\n"
    "U_RULE = '%d:%d:%d' % (U_MIN_S, FRAMES_VIDEO, U_CAP_S)        # enter_scene_s15.py --hold-u\n"
    "HOLD_RULE_U = dict(min_shown_s=U_MIN_S, video_frames=FRAMES_VIDEO, cap_s=U_CAP_S, wall_extra_s=U_WALL_EXTRA_S,\n"
    "                   scene_draws=U_SCENE_DRAWS)                   # the json field hold_rule of a U arm\n"
    "HELD_LINES_MAX = 64              # sc_s.HELD_LINES_MAX: the emulator prints at most 64 lines \"flip N held\" per process")
rep("M_NOPB_END = b' yet'                                         # item 452 (b): the path is between M_NOPB and this",
    "M_NOPB_END = b' yet'                                         # item 452 (b): the path is between M_NOPB and this\n"
    "RX_HELDF = re.compile(rb'^AsyncPipelines: flip (\\d+) held')    # item 511 (z)(i): T-2 by the flip number")

# ---------------------------------------------------------------------------------------------------- arms and plan
rep('''def plan(spec):
    """One line for go_s15.sh: link level cls mode hold src sdraws timeout rec val."""
    sd, to = stable_timeout(spec)
    return 's15 %s %s %s %d %s %d %d %d %d' % (spec['level'], spec['cls'], spec['mode'], spec['hold'], spec['src'] or '-', sd, to,
                                               1 if spec['rec'] else 0, 1 if spec['val'] else 0)''',
    '''def hold_rule(spec):
    """Item 511 (z)(4): the hold rule of an arm - U_RULE on a U arm, None on k_NN and w13 (a fixed hold)."""
    return U_RULE if spec['group'] == 'u' else None


def plan(spec):
    """One line for go_s15.sh: link level cls mode hold src sdraws timeout rec val holdrule ('-' without a rule)."""
    sd, to = stable_timeout(spec)
    return 's15 %s %s %s %d %s %d %d %d %d %s' % (spec['level'], spec['cls'], spec['mode'], spec['hold'], spec['src'] or '-', sd,
                                                  to, 1 if spec['rec'] else 0, 1 if spec['val'] else 0, hold_rule(spec) or '-')''')

# ---------------------------------------------------------------------------------------------------- scan_y: held flips
rep("""             created_line=None, nopb_line=None, nopb_text=None)
    n = 0""", """             created_line=None, nopb_line=None, nopb_text=None, held_flips=[])
    n = 0""")
rep("""            if M_RECOVER in line:
                r['recover'] += 1
    return r""", """            if M_RECOVER in line:
                r['recover'] += 1
            if line.startswith(b'AsyncPipelines: flip'):
                m = RX_HELDF.match(line)
                if m and b' held' in line:
                    r['held_flips'].append(int(m.group(1)))      # item 511 (z)(i): T-2 by the flip number
    return r""")

# ---------------------------------------------------------------------------------------------------- admission: hold rule
rep("""             'hold --hold {}', 'prereg = the seal', 'no pipeline-cache retry',""",
    """             'hold --hold {}', 'hold rule {} in the json (item 511 (z)(4))', 'prereg = the seal', 'no pipeline-cache retry',""")
rep("""    add('hold --hold %d' % spec['hold'], js.get('hold_s') == spec['hold'], js.get('hold_s'))""",
    """    add('hold --hold %d' % spec['hold'], js.get('hold_s') == spec['hold'], js.get('hold_s'))
    want_rule = HOLD_RULE_U if hold_rule(spec) else None
    add('hold rule %s in the json (item 511 (z)(4))' % (hold_rule(spec) or 'none (a fixed hold)'), js.get('hold_rule') == want_rule,
        js.get('hold_rule'))""")

# ---------------------------------------------------------------------------------------------------- identities (z)(i)
rep('''def frame_rows(s, fi, end):''', '''def ident_lo(s, fi, eg):
    """Item 511 (z)(i): the first row of the identity domain - the first scene frame fi, else the entry row eg (z)(5), else the
    whole log; never below row 1 (a line logged before the first FrameTrace row is counted by no row)."""
    lo = fi if fi is not None else (eg if eg is not None else 0)
    return max(lo, 1)


def ident_rows(ident, s, sy, lo):
    """Item 511 (z)(i): T-1, T-2 and T-6 of sc_s.identities() on the rows i >= lo by the row that counts a line (see the header);
    the rows of item 404 (sc_s9.ident_domain, by frame=) arrive in ident and are kept as ONE data row (ok None).  A domain past
    the last row (lo >= rows) compares 0 with 0.  SKIP_LINES_MAX of sc_s unchanged (T-1, T-6 undetermined at the cap)."""
    rows = s['rows']
    xs = [s['x'].get(r[0]) for r in rows[lo:]]
    sk = sum((t[0] or 0) for t in xs if t)
    hi = sum((t[1] or 0) for t in xs if t)
    dom = [e for e in s['skips'] if e[0] >= lo]
    frames = set(e[1] for e in dom if e[1] is not None)
    under = len(s['skips']) < A.SKIP_LINES_MAX
    n_lo = rows[lo][0] if lo < len(rows) else None
    hf = sy['held_flips']
    before = sum(1 for f in hf if n_lo is None or f < n_lo)
    inside = sum(1 for f in hf if n_lo is not None and f >= n_lo)
    cap = max(0, HELD_LINES_MAX - before)
    old = [('%s %s' % (name.split(' ')[0], det)) for name, ok, det in ident
           if name.startswith(('T-1 ', 'T-2 ', 'T-6 ', 'T-1 / T-6 whole log'))]
    out = [x for x in ident if not x[0].startswith(('T-1 ', 'T-2 ', 'T-6 ', 'T-1 / T-6 whole log'))]
    where = 'the rows i >= %d (n >= %s; item 511 (z)(i))' % (lo, n_lo)
    out.append(('T-1 sum skc_ap_skip = skipped-draw lines of the groups g >= lo, on %s' % where, (sk == len(dom)) if under else None,
                '%d / %d (lines without frame= %d)' % (sk, len(dom), sum(1 for e in dom if e[1] is None))))
    out.append(('T-2 min(64 - held lines before, sum skc_held_inc) = "flip N held" lines with N >= n, on %s' % where,
                min(cap, hi) == inside, '%d / %d (lines before %d)' % (min(cap, hi), inside, before)))
    out.append(('T-6 distinct frame= of the skipped-draw lines of the groups g >= lo = sum skc_held_inc, on %s' % where,
                (len(frames) == hi) if under else None, '%d / %d' % (len(frames), hi)))
    out.append(('T-1 / T-2 / T-6 by frame= of item 404 and whole log (data, item 511 (z)(i))', None, '; '.join(old) or '-'))
    return out


def frame_rows(s, fi, end):''')

# ---------------------------------------------------------------------------------------------------- domain_of: anchor
rep('''def domain_of(s, level, fi, sc_end, attempt, ended, exited):''',
    '''def domain_of(s, level, fi, sc_end, attempt, ended, exited, anchor='first scene frame'):''')
rep('''    return dict(end=nrows, cause=cause, changes=ch, rows=max(0, nrows - fi - 1), shown_us=shown_us(s, fi + 1, nrows),
                ref_end=sc_end, ref_rows=max(0, sc_end - fi - 1), ref_shown_us=shown_us(s, fi + 1, sc_end))''',
    '''    return dict(end=nrows, cause=cause, changes=ch, rows=max(0, nrows - fi - 1), shown_us=shown_us(s, fi + 1, nrows),
                ref_end=sc_end, ref_rows=max(0, sc_end - fi - 1), ref_shown_us=shown_us(s, fi + 1, sc_end), anchor=anchor)''')

# ---------------------------------------------------------------------------------------------------- score_arm
rep('''    r['video'] = os.path.isfile(os.path.join(root, 'rec_%s.mp4' % tag))''',
    '''    r['video'] = os.path.isfile(os.path.join(root, 'rec_%s.mp4' % tag))
    r['hold_end'] = at.get('hold_end')          # item 511 (z)(4): data - the end of the U hold (enter_scene_s15.py)''')
rep('''    ident = S9.ident_domain(ident, s, fi)                                # item 404 (v)''',
    '''    ident = S9.ident_domain(ident, s, fi)                                # item 404 (v) - kept as one data row below
    r['ident_lo'] = ident_lo(s, fi, eg)
    ident = ident_rows(ident, s, sy, r['ident_lo'])                         # item 511 (z)(i): by the row that counts a line''')
rep('''    sy = scan_y(lp)
    eg, end, fi = A.locate(s, spec['level'])''', '''    sy = scan_y(lp)
    eg, end, fi = A.locate(s, spec['level'])
    r['entry_row'] = eg''')
rep('''    if fi is not None:
        prep = A.assign_prep(s)
        # item 436 (b)(1), RC1 - the letter: the domain is every row after fi to the end of the hold (the last row of the log)
        dom = domain_of(s, spec['level'], fi, end, r['attempt'], r['ended'], r['exited'])
        r['dom'] = dom
        dend = dom['end']
        r['f1'] = A.freeze(s, fi, dend, prep, attr_ok, 1)
        r['f2'] = A.freeze(s, fi, dend, prep, attr_ok, 2)
        r['split'] = split_at(s, fi, dend, end, r['f1'], attr_ok)
        # the reference of Red Team (no decision): the domain to the first scene change, as sealed in pred/11_s.md
        fr = A.freeze(s, fi, end, prep, attr_ok, 1)
        r['ref'] = dict(after=frame_rows(s, fi, end), att100=A.attributed(fr, attr_ok, A.K3_US))''',
    '''    if fi is not None or eg is not None:
        prep = A.assign_prep(s)
        # item 511 (z)(5): an entered arm without a first scene frame - the anchor is the row before the entry row (the domain is
        # every row i >= eg), the reading 2 of sc_s for both readings (no first scene frame to add)
        if fi is not None:
            anc, rd1, akind = fi, 1, 'first scene frame'
        else:
            anc, rd1, akind = eg - 1, 2, 'entry line (item 511 (z)(5))'
        # item 436 (b)(1), RC1 - the letter: the domain is every row after the anchor to the end of the hold (the last row of the log)
        dom = domain_of(s, spec['level'], anc, end, r['attempt'], r['ended'], r['exited'], akind)
        r['dom'] = dom
        dend = dom['end']
        r['f1'] = A.freeze(s, anc, dend, prep, attr_ok, rd1)
        r['f2'] = A.freeze(s, anc, dend, prep, attr_ok, 2)
        r['split'] = split_at(s, anc, dend, end, r['f1'], attr_ok)
        # the reference of Red Team (no decision): the domain to the first scene change, as sealed in pred/11_s.md
        fr = A.freeze(s, anc, end, prep, attr_ok, rd1)
        r['ref'] = dict(after=frame_rows(s, anc, end), att100=A.attributed(fr, attr_ok, A.K3_US))''')
rep('''        r['after'] = frame_rows(s, fi, dend)
        r['held_r1'] = r['f1']['window']['held'] + r['f1']['hold']['held']
        r['pre_dom'], r['nof'] = pre_domain_lines(s, spec['level'], s['rows'][fi][0])''',
    '''        r['after'] = frame_rows(s, anc, dend)
        r['held_r1'] = r['f1']['window']['held'] + r['f1']['hold']['held']
        if fi is not None:
            r['pre_dom'], r['nof'] = pre_domain_lines(s, spec['level'], s['rows'][fi][0])
        else:
            r['pre_dom'], r['nof'] = None, sum(1 for e in s['skips'] if e[1] is None)    # (z)(5): no first scene frame''')

# ---------------------------------------------------------------------------------------------------- printing
rep('''    return ('end row %d (cause: %s), rows %d, presented %.3f s (minimum %d s); scene changes inside: %s; before the first '
            'scene change: %s; after it: %s; reference to the first scene change: rows %d, presented %.3f s' % (
                d['end'], d['cause'], d['rows'], d['shown_us'] / 1e6, DOMAIN_MIN_US // 1000000,''',
    '''    return ('anchor %s; end row %d (cause: %s), rows %d, presented %.3f s (minimum %d s); scene changes inside: %s; before the '
            'first scene change: %s; after it: %s; reference to the first scene change: rows %d, presented %.3f s' % (
                d.get('anchor', 'first scene frame'), d['end'], d['cause'], d['rows'], d['shown_us'] / 1e6, DOMAIN_MIN_US // 1000000,''')
rep('''    if 'f1' not in r:
        o.append('  entered %s, first scene frame %s - no freeze reading' % (r.get('entered'), r.get('first')))
    else:
        o.append('  entered yes; first scene frame (n, dt, draws) %s; attribution %s' % (
            r['first'], 'DETERMINED' if r['attr_ok'] else 'UNDETERMINED'))''',
    '''    o.append('  hold end (item 511 (z)(4), data): %s' % fmt_hold(r))
    if 'f1' not in r:
        o.append('  entered %s, first scene frame %s - no freeze reading' % (r.get('entered'), r.get('first')))
    else:
        o.append('  entered yes; first scene frame (n, dt, draws) %s; anchor of the domain %s; attribution %s' % (
            r['first'], r['dom'].get('anchor'), 'DETERMINED' if r['attr_ok'] else 'UNDETERMINED'))''')
rep('''def fmt_arm(r):''', '''def fmt_hold(r):
    """Item 511 (z)(4): the end of the hold of the attempt (enter_scene_s15.py hold_end) - data."""
    h = (r or {}).get('hold_end')
    if not h:
        return 'none (a fixed hold or no U hold record)'
    return 'cause %s, anchor %s, presented after the anchor %.3f s, video frames %s, rows %s' % (
        h.get('cause'), h.get('anchor'), (h.get('shown_us') or 0) / 1e6, h.get('video_frames'), h.get('rows'))


def fmt_arm(r):''')
rep('''        out.append('%s data of item 446 (b) (item 452 (b), no outcome reads it): %s' % (t, fmt_nopb(r)))
        out.append('%s rows after the arm (item 452 (c)): %s' % (t, fmt_post(r)))
    rw = get('w13')''', '''        out.append('%s data of item 446 (b) (item 452 (b), no outcome reads it): %s' % (t, fmt_nopb(r)))
        out.append('%s rows after the arm (item 452 (c)): %s' % (t, fmt_post(r)))
        out.append('%s hold end (item 511 (z)(4), data): %s' % (t, fmt_hold(r)))
    rw = get('w13')''')

# ---------------------------------------------------------------------------------------------------- the seal names
rep('''SEALED_NAMES = ('s15/go_s15.sh', 's15/sc_s15.py', 's15/test_sc_s15.py', 's15/mut_sc_s15.py', 's15/test_go_s15.py',
                's15/seedexp_s15.py', 's15/test_seedexp_s15.py', 's13/lvl_s13.py', 's13/lvl_s13.out.txt', 's9/sc_s9.py',
                's9/enter_scene_s9.py', 'sc_s.py',''', '''SEALED_NAMES = ('s15/go_s15.sh', 's15/sc_s15.py', 's15/test_sc_s15.py', 's15/mut_sc_s15.py', 's15/test_go_s15.py',
                's15/seedexp_s15.py', 's15/test_seedexp_s15.py', 's15/enter_scene_s15.py', 's15/mk_enter_s15.py',
                's15/test_enter_scene_s15.py', 's13/lvl_s13.py', 's13/lvl_s13.out.txt', 's9/sc_s9.py',
                's9/enter_scene_s9.py', 'sc_s.py',''')

rep("with frame= below the first scene frame %d; '", "with frame= below the first scene frame %s; '")

for old, new in R:
    c = t.count(old)
    if c != 1:
        print('STOP: anchor found %d times: %r' % (c, old[:120]))
        sys.exit(1)
    t = t.replace(old, new)
t.encode('ascii')
open(P, 'wb').write(t.encode('ascii'))
print('PATCHED %s: %d replacements' % (P, len(R)))
