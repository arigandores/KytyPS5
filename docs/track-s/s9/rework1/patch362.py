"""patch362.py - track S, link S9 (HPP-431), rework 1 by ROADMAP "SESSION 122" item 362 (b), (v), (d): edits sc_s9.py, go_s9.sh,
test_go_s9.py, test_sc_s9.py, mut_sc_s9.py in C:/kyty/s288/s9.  Every replacement must match exactly once (count of the old text
in the file), else nothing is written.  LF, ASCII.  Refuses under the lock.
"""
import os
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
D = 'C:/kyty/s288/s9/'
NL = chr(10)

SC = [
    # docstring
    ("""             READ_1 (a series in pi_r1, none in pi_r0), READ_2 (no series in the four, or in both R; both R loaded N bytes = the
             last write of their own W, 0 disabled), READ_3 (a series only in pi_r0, or only in the W arms), READ_OTHER.
""",
     """             READ_1 (a series in pi_r1, none in pi_r0), READ_2 (no series in the four, or in both R; both R loaded N bytes = the
             last write of their own W, 0 disabled), READ_3 (a series only in pi_r0 among the R arms, or only in the W arms; AND
             the loaded member of READ_2 on both R - item 362 (v)), READ_OTHER; the executor's reading (READ_3 without the loaded
             member) printed beside.
"""),
    ("""  --read-t2  item 355 (d), (zh): the cold gate of item 241 (v)(7) (letter; the variant without the recipe member when the form
             runs KYTY_PIPELINE_PRECACHE=0 printed beside), the attribution, the S-early lead row, the BvhLoopCapTrip column,
             the data rows of t2_cs0 against t2_1.
""",
     """  --read-t2  item 355 (d), (zh), item 362 (b): the cold gate of item 241 (v)(7) - in the form C5 (KYTY_PIPELINE_PRECACHE=0) the
             recipe member is replaced by ">= 1 in-game creation after the entry line", in the form APP by the letter; the letter
             (with the recipe) and the executor's variant (the recipe member dropped) printed beside; the attribution, the S-early
             lead row, the BvhLoopCapTrip column, the data rows of t2_cs0 against t2_1.
"""),
    ("PRED_PATH = 'C:/kyty/s288/pred/05_s.md'", "PRED_PATH = 'C:/kyty/s288/pred/05b_s.md'                       # item 362 (d)"),
    ("T2_GATE_READING = 'letter'       # item 241 (v)(7) by the letter; 'variant' - see gate9() (a question to the lead, S9 report)",
     "T2_GATE_READING = 'p362'         # item 362 (b): C5 - the recipe member replaced by an in-game creation; APP - the letter"),
    # scan_x
    ("""    their us field, and the row count (= len(scan_s rows), an identity of this scan).\"\"\"
    r = dict(rows=0, bvh=[], csp={}, gamepatch=0, create=[], create_nous=0)
    with open(path, 'rb') as f:
        for line in f:
            c0 = line[:1]
""",
     """    their us field and their log line number (counted as sc_s.scan_s counts s['lines'], item 362 (b)), the row count (=
    len(scan_s rows)) and the line count (= scan_s lines) - identities of this scan.\"\"\"
    r = dict(rows=0, lines=0, bvh=[], csp={}, gamepatch=0, create=[], create_nous=0, create_ln=[])
    with open(path, 'rb') as f:
        for line in f:
            r['lines'] += 1
            c0 = line[:1]
"""),
    ("""                    else:
                        r['create'].append(us)
    return r
""",
     """                    else:
                        r['create'].append(us)
                        r['create_ln'].append(r['lines'])
    return r
"""),
    # gate9
    ("""def gate9(g, spec, reading=None):
    \"\"\"Item 241 (v)(7) cold gate on a C5 / T2 arm.  letter: the gate of sc_s (new permutation, new recipe and skipped draw after
    the entry line); variant: when the arm runs KYTY_PIPELINE_PRECACHE=0 the recipe member is dropped - that knob stops the
    recipe writer (4fc501f4 pipelineCache.cpp RecordGraphicsRecipe returns while PipelinePrecacheEnabled() is false), so the
    letter can never hold there.  Returns (cold, word).\"\"\"
    reading = reading or T2_GATE_READING
    if g is None:
        return False, 'undetermined (no scene frame)'
    if not g['attr_ok']:
        return False, 'undetermined (T-3/T-4)'
    if reading == 'variant' and spec['pre0']:
        cold = g['perm_after'] >= 1 and g['skip_after'] >= 1
    else:
""",
     """def gate9(g, spec, reading=None):
    \"\"\"Item 241 (v)(7) cold gate on a C5 / T2 arm, item 362 (b).  p362 (the seal): when the arm runs KYTY_PIPELINE_PRECACHE=0
    (form C5) the recipe member is replaced by >= 1 in-game creation after the entry line (create_after: lines "AvTrace: pipeline "
    without "precache" with a " us=" field whose log line number is above the line "Level has started: L"); new permutation and
    skipped draw by the letter; without PRECACHE=0 (form APP) the letter.  letter: the gate of sc_s (new permutation, new recipe
    and skipped draw after the entry line) - KYTY_PIPELINE_PRECACHE=0 stops the recipe writer (4fc501f4 pipelineCache.cpp:5858),
    so it never holds in the form C5; variant (the executor's, rejected by item 362 (b), printed): under PRECACHE=0 the recipe
    member dropped with no replacement.  Returns (cold, word).\"\"\"
    reading = reading or T2_GATE_READING
    if g is None:
        return False, 'undetermined (no scene frame)'
    if not g['attr_ok']:
        return False, 'undetermined (T-3/T-4)'
    if reading == 'p362' and spec['pre0']:
        cold = g['perm_after'] >= 1 and g.get('create_after', 0) >= 1 and g['skip_after'] >= 1
    elif reading == 'variant' and spec['pre0']:
        cold = g['perm_after'] >= 1 and g['skip_after'] >= 1
    else:
"""),
    # score_arm
    ("""    ident.append(('scan_x rows = scan_s rows (the group index of BvhLoopCapTrip / CsPretranslate)', sx['rows'] == len(s['rows']),
                  '%d / %d' % (sx['rows'], len(s['rows']))))
""",
     """    ident.append(('scan_x rows = scan_s rows (the group index of BvhLoopCapTrip / CsPretranslate)', sx['rows'] == len(s['rows']),
                  '%d / %d' % (sx['rows'], len(s['rows']))))
    ident.append(('scan_x lines = scan_s lines (the line numbers of the in-game creations, item 362 (b))', sx['lines'] == s['lines'],
                  '%d / %d' % (sx['lines'], s['lines'])))
"""),
    ("""        g['attr_ok'] = attr_ok
""",
     """        g['attr_ok'] = attr_ok
        el = A.entry_line(s, spec['level'])
        g['create_after'] = sum(1 for ln in sx['create_ln'] if el is not None and ln > el)      # item 362 (b)
"""),
    # read_pi
    ("""    word = pi_word(hz, loaded)
    wv = pi_word(var, loaded)
""",
     """    word = pi_word(hz, loaded)
    wv = pi_word(var, loaded)
    wx = pi_word(hz, loaded, False)
"""),
    ("""    if word == 'READ_3' and hz['pi_r0'] and (hz['pi_w1'] or hz['pi_w0']):
        out.append('note: a series in pi_r0 and in a W arm - "only in pi_r0" read among the R arms (executor\\'s reading); '
                   'the strict reading gives READ_OTHER')
""",
     """    out.append('reading of the executor (READ_3 without the loaded member of (2), rejected by item 362 (v)): %s%s' % (
        wx, '' if wx == word else ' - DIFFERS (the loaded member)'))
    if word == 'READ_3' and hz['pi_r0'] and (hz['pi_w1'] or hz['pi_w0']):
        out.append('note: a series in pi_r0 and in a W arm, none in pi_r1 - READ_3 ("only in pi_r0" among the R arms, item 362 (v))')
"""),
    ("""               'READ_3': '(3) an effect of the scene [I], as (2) (decision S11)',""",
     """               'READ_3': '(3) an effect of the scene [I], as (2): with the loaded member of (2) on both R (item 362 (v)) '
                         '(decision S11)',"""),
    ("""def pi_word(hz, loaded):
    r1, r0 = hz['pi_r1'], hz['pi_r0']
    w = hz['pi_w1'] or hz['pi_w0']
    both_loaded = all(loaded.values())
    if r1 and not r0:
        return 'READ_1'
    if r1 and r0:
        return 'READ_2' if both_loaded else 'READ_OTHER'
    if r0:
        return 'READ_3'
    if w:
        return 'READ_3'
""",
     """def pi_word(hz, loaded, need_load=True):
    \"\"\"Item 355 (g), item 362 (v): "as (2)" is the consequence and the condition - READ_3 needs the loaded member of (2) on both
    R, else READ_OTHER; need_load False gives the executor's reading (printed beside).\"\"\"
    r1, r0 = hz['pi_r1'], hz['pi_r0']
    w = hz['pi_w1'] or hz['pi_w0']
    both_loaded = all(loaded.values())
    if r1 and not r0:
        return 'READ_1'
    if r1 and r0:
        return 'READ_2' if both_loaded else 'READ_OTHER'
    if r0:
        return 'READ_3' if both_loaded or not need_load else 'READ_OTHER'
    if w:
        return 'READ_3' if both_loaded or not need_load else 'READ_OTHER'
"""),
    # read_t2
    ("""    counted = []
    counted_v = 0
    for j in range(len(T2_LIST)):
        tag = 't2_%d' % (j + 1)
        r = get(tag)
        if r is None:
            continue
        spec = resolved(SPEC[tag], r.get('form'))
        gl = gate9(r.get('gates'), spec, 'letter')
        gv = gate9(r.get('gates'), spec, 'variant')
        c = t2_counted(r)
        counted_v += t2_counted(r, 'variant')
""",
     """    counted = []
    counted_l = 0
    counted_v = 0
    for j in range(len(T2_LIST)):
        tag = 't2_%d' % (j + 1)
        r = get(tag)
        if r is None:
            continue
        spec = resolved(SPEC[tag], r.get('form'))
        gp = gate9(r.get('gates'), spec, 'p362')
        gl = gate9(r.get('gates'), spec, 'letter')
        gv = gate9(r.get('gates'), spec, 'variant')
        c = t2_counted(r)
        counted_l += t2_counted(r, 'letter')
        counted_v += t2_counted(r, 'variant')
"""),
    ("""        out.append('%s %s: %s; arm %s; gate letter %s, variant %s; skip rows %s held %s presented >= 100 ms %s; attributed >= 100 '
""",
     """        out.append('%s %s: %s; arm %s; gate (item 362 (b)) %s, by the letter (with the recipe) %s, executor variant %s; in-game '
                   'creations after the entry %s; skip rows %s held %s presented >= 100 ms %s; attributed >= 100 '
"""),
    ("""                       tag, r['level'], 'COUNTED' if c else 'OUT', 'PASS' if ok_arm(r) else 'FAIL %s' % r['fail'], gl[1], gv[1],
""",
     """                       tag, r['level'], 'COUNTED' if c else 'OUT', 'PASS' if ok_arm(r) else 'FAIL %s' % r['fail'], gp[1], gl[1],
                       gv[1], (r.get('gates') or {}).get('create_after'),
"""),
    ("""    out.append('T2 counted %d of %d needed (variant gate: %d)' % (len(counted), T2_NEED, counted_v))
""",
     """    out.append('T2 counted %d of %d needed (item 362 (b)); by the letter (with the recipe) %d; executor variant %d' % (
        len(counted), T2_NEED, counted_l, counted_v))
"""),
    # fmt_arm
    ("""    o.append('  cold gate letter %s, variant %s; gates %s' % (gate9(r['gates'], resolved(SPEC[r['tag']], r.get('form')), 'letter')[1],
                                                           gate9(r['gates'], resolved(SPEC[r['tag']], r.get('form')), 'variant')[1],
                                                           dict((k, v) for k, v in r['gates'].items())))
""",
     """    sp9 = resolved(SPEC[r['tag']], r.get('form'))
    o.append('  cold gate (item 362 (b)) %s, by the letter (with the recipe) %s, executor variant %s; gates %s' % (
        gate9(r['gates'], sp9, 'p362')[1], gate9(r['gates'], sp9, 'letter')[1], gate9(r['gates'], sp9, 'variant')[1],
        dict((k, v) for k, v in r['gates'].items())))
"""),
]

GO = [
    ('of pred/05_s.md.', 'of pred/05b_s.md (item 362 (d)).'),
    ('PRED=pred/05_s.md\n', 'PRED=pred/05b_s.md\n'),
    ('(go_s9.sh seal 05)" > $LOCK', '(go_s9.sh seal 05b)" > $LOCK'),
]

TGO = [
    ("(BASE / 'pred' / '05_s.md').as_posix())", "(BASE / 'pred' / '05b_s.md').as_posix())"),
    ("    (BASE / 'pred' / '05_s.md').write_text(", "    (BASE / 'pred' / '05b_s.md').write_text("),
]

TSC = [
    ("""threshold; the order of S10; the seal; main; ASCII output in strict cp1250.  Synthetic logs only, no process is started.
""",
     """threshold; the order of S10; the seal; main; ASCII output in strict cp1250.  Rework 1 (item 362): the line numbers of the
in-game creations, the gate p362 (form C5: a creation after the entry line instead of the recipe; form APP: the letter) with a
creation before / right after / after the entry line, a line without " us=", the APP form with and without a recipe, the T2 counts
of the three readings, the order with counted C5 arms; READ_3 with and without the loaded member of each R and the executor's
reading printed beside.  Synthetic logs only, no process is started.
"""),
    ("""           'stand 15000, gate reading letter', S.C5_MIN == 10""", """           'stand 15000, gate reading p362 (item 362 (b))', S.C5_MIN == 10"""),
    ("""and S.FRAMES_VIDEO == 3000 and S.PCW_FORCE_MS == '15000' and S.T2_GATE_READING == 'letter')""",
     """and S.FRAMES_VIDEO == 3000 and S.PCW_FORCE_MS == '15000' and S.T2_GATE_READING == 'p362')"""),
    ("""ok &= case('A6 paths: link C:/kyty/s288/s10, seal pred/05_s.md, Sky Garden, L0 shuriken_ninja_castle', S.LINK_DIR ==
           'C:/kyty/s288/s10' and S.PRED_PATH == 'C:/kyty/s288/pred/05_s.md'""",
     """ok &= case('A6 paths: link C:/kyty/s288/s10, seal pred/05b_s.md (item 362 (d)), Sky Garden, L0 shuriken_ninja_castle',
           S.LINK_DIR == 'C:/kyty/s288/s10' and S.PRED_PATH == 'C:/kyty/s288/pred/05b_s.md'"""),
    ("""           S.bvh_col(dict(bvh=[7]), [dict(n=1, i=8)]) == [(1, 1)])
""",
     """           S.bvh_col(dict(bvh=[7]), [dict(n=1, i=8)]) == [(1, 1)])
ok &= case('D9 item 362 (b): the log line numbers of the in-game creations (async 14, none 15, sync 16; the waited line 17 and the '
           'precache lines 18, 19 not) counted as sc_s.scan_s counts lines (22 = 22)', sx['create_ln'] == [14, 15, 16] and
           sx['lines'] == 22 and ss['lines'] == 22)
"""),
    ("""ok &= case('E5 gate: no gate dict -> undetermined (no scene frame); attribution broken -> undetermined (T-3/T-4); the default '
           'reading is the constant', S.gate9(None, dict(pre0=False)) == (False, 'undetermined (no scene frame)') and
           S.gate9(dict(g_full, attr_ok=False), dict(pre0=False)) == (False, 'undetermined (T-3/T-4)') and
           S.gate9(g_norec, dict(pre0=True)) == (False, 'level not cold'))
""",
     """ok &= case('E5 gate: no gate dict -> undetermined (no scene frame); attribution broken -> undetermined (T-3/T-4); the default '
           'reading is the constant p362', S.gate9(None, dict(pre0=False)) == (False, 'undetermined (no scene frame)') and
           S.gate9(dict(g_full, attr_ok=False), dict(pre0=False)) == (False, 'undetermined (T-3/T-4)') and
           S.gate9(g_norec, dict(pre0=True)) == (False, 'level not cold') and
           S.gate9(dict(g_norec, create_after=1), dict(pre0=True)) == (True, 'cold'))
g_c = dict(attr_ok=True, perm_after=1, rec_new_after=0, skip_after=1, create_after=1)
ok &= case('E9 gate p362 under PRECACHE=0 (form C5): new permutation AND an in-game creation after the entry AND a skipped draw; '
           'the recipe member is not asked; no create_after key -> not cold', S.gate9(g_c, dict(pre0=True), 'p362') ==
           (True, 'cold') and S.gate9(dict(g_c, create_after=0), dict(pre0=True), 'p362') == (False, 'level not cold') and
           S.gate9(dict(g_c, perm_after=0), dict(pre0=True), 'p362')[0] is False and
           S.gate9(dict(g_c, skip_after=0), dict(pre0=True), 'p362')[0] is False and
           S.gate9(dict(g_c, create_after=0, rec_new_after=5), dict(pre0=True), 'p362')[0] is False and
           S.gate9(g_norec, dict(pre0=True), 'p362')[0] is False)
ok &= case('E10 gate p362 without PRECACHE=0 (form APP) = the letter: a creation without a recipe is not cold, a recipe without a '
           'creation is cold', S.gate9(g_c, dict(pre0=False), 'p362') == (False, 'level not cold') and
           S.gate9(dict(g_c, rec_new_after=1, create_after=0), dict(pre0=False), 'p362') == (True, 'cold') and
           S.gate9(g_full, dict(pre0=False), 'p362') == (True, 'cold'))
ok &= case('E11 the letter and the variant do not read create_after: letter under PRECACHE=0 with a creation and no recipe is not '
           'cold; the variant without a creation is cold', S.gate9(g_c, dict(pre0=True), 'letter')[0] is False and
           S.gate9(dict(g_c, create_after=0), dict(pre0=True), 'variant') == (True, 'cold'))
"""),
    # pi readings
    ("""w4, _ = S.read_pi(getter())
ok &= case('I7 a series only in pi_r0 -> READ_3', w4 == 'READ_3')
""",
     """w4, _ = S.read_pi(getter())
ok &= case('I7 a series only in pi_r0, both R loaded the last write of their W -> READ_3', w4 == 'READ_3')
mkarm('pi_r0', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(7)]), sat=sat_for([(1500, 1510)]))
w4b, rd4b = S.read_pi(getter())
ok &= case('I7b a series only in pi_r0 but pi_r0 loaded another size than the last write of pi_w0 -> READ_OTHER (item 362 (v)); '
           'the executor reading READ_3 printed as DIFFERS', w4b == 'READ_OTHER' and any(
               x.startswith('reading of the executor') and x.endswith(': READ_3 - DIFFERS (the loaded member)') for x in rd4b))
"""),
    ("""w5, _ = S.read_pi(getter())
ok &= case('I8 a series only in a W arm -> READ_3', w5 == 'READ_3')
""",
     """w5, _ = S.read_pi(getter())
ok &= case('I8 a series only in a W arm, both R loaded -> READ_3', w5 == 'READ_3')
mkarm('pi_r0', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(5000)]), sat=sat_for([(1500, 1510)]))
w5c, rd5c = S.read_pi(getter())
ok &= case('I8c a series in pi_r0 and in a W arm, none in pi_r1, both loaded -> READ_3 with the note of item 362 (v)',
           w5c == 'READ_3' and any(x.startswith('note: a series in pi_r0 and in a W arm, none in pi_r1 - READ_3') for x in rd5c))
mkarm('pi_r0', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(5000)]))
mkarm('pi_r1', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(94435637), 'Vulkan pipeline cache: disabled (x)']))
w5d, rd5d = S.read_pi(getter())
ok &= case('I8b a series only in a W arm but pi_r1 has a disabled line (loaded member FAIL) -> READ_OTHER; the executor reading '
           'READ_3 printed as DIFFERS', w5d == 'READ_OTHER' and any(
               x.startswith('reading of the executor') and x.endswith(': READ_3 - DIFFERS (the loaded member)') for x in rd5d))
mkarm('pi_r1', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(94435637)]))
"""),
    ("""ok &= case('I17 pi_word table: (r1, r0, w, loaded)', S.pi_word(dict(pi_r1=True, pi_r0=False, pi_w1=True, pi_w0=True),
                                                               {'a': False}) == 'READ_1' and
           S.pi_word(dict(pi_r1=False, pi_r0=False, pi_w1=False, pi_w0=False), {'a': False}) == 'READ_OTHER' and
           S.pi_word(dict(pi_r1=False, pi_r0=False, pi_w1=False, pi_w0=False), {'a': True}) == 'READ_2' and
           S.pi_word(dict(pi_r1=False, pi_r0=True, pi_w1=False, pi_w0=False), {'a': False}) == 'READ_3' and
           S.pi_word(dict(pi_r1=False, pi_r0=False, pi_w1=False, pi_w0=True), {'a': False}) == 'READ_3' and
           S.pi_word(dict(pi_r1=True, pi_r0=True, pi_w1=False, pi_w0=False), {'a': True, 'b': False}) == 'READ_OTHER')
""",
     """ok &= case('I17 pi_word table: (r1, r0, w, loaded) - READ_3 needs both R loaded (item 362 (v)), the executor reading does not',
           S.pi_word(dict(pi_r1=True, pi_r0=False, pi_w1=True, pi_w0=True), {'a': False}) == 'READ_1' and
           S.pi_word(dict(pi_r1=False, pi_r0=False, pi_w1=False, pi_w0=False), {'a': False}) == 'READ_OTHER' and
           S.pi_word(dict(pi_r1=False, pi_r0=False, pi_w1=False, pi_w0=False), {'a': True}) == 'READ_2' and
           S.pi_word(dict(pi_r1=False, pi_r0=True, pi_w1=False, pi_w0=False), {'a': True}) == 'READ_3' and
           S.pi_word(dict(pi_r1=False, pi_r0=True, pi_w1=False, pi_w0=False), {'a': True, 'b': False}) == 'READ_OTHER' and
           S.pi_word(dict(pi_r1=False, pi_r0=True, pi_w1=False, pi_w0=False), {'a': False}, False) == 'READ_3' and
           S.pi_word(dict(pi_r1=False, pi_r0=False, pi_w1=False, pi_w0=True), {'a': True}) == 'READ_3' and
           S.pi_word(dict(pi_r1=False, pi_r0=False, pi_w1=True, pi_w0=False), {'a': False, 'b': True}) == 'READ_OTHER' and
           S.pi_word(dict(pi_r1=False, pi_r0=False, pi_w1=False, pi_w0=True), {'a': False}, False) == 'READ_3' and
           S.pi_word(dict(pi_r1=True, pi_r0=True, pi_w1=False, pi_w0=False), {'a': True, 'b': False}) == 'READ_OTHER' and
           S.pi_word(dict(pi_r1=True, pi_r0=False, pi_w1=False, pi_w0=False), {'a': False}, False) == 'READ_1')
"""),
    # T2
    ("""def t2_arm(tag, cold=True, form='c5', extra=(), lv=None):
    lvl = lv or S.SPEC[tag]['level']
    pre = [SH(0xaa, 50, 50)] if False else []
    post = [(16000, dict(ev=([SH(0x77, 50, 50)] if cold else []) + ([SKIP(8)] if cold else []) + list(extra),
""",
     """def t2_arm(tag, cold=True, form='c5', extra=(), lv=None, create=False):
    lvl = lv or S.SPEC[tag]['level']
    post = [(16000, dict(ev=([SH(0x77, 50, 50)] if cold else []) + ([SKIP(8)] if cold else []) +
                         ([GFX(30000, 'async')] if cold and create else []) + list(extra),
"""),
    ("""ok &= case('K1 a T2 arm in form C5: admitted, attribution, the gate letter "level not cold" (no recipe under PRECACHE=0), the '
           'variant "cold"', not t2a['fail'] and t2a['attr_ok'] and S.gate9(t2a['gates'], S.resolved(S.SPEC['t2_1'], 'c5'),
                                                                              'letter')[1] == 'level not cold'
           and S.gate9(t2a['gates'], S.resolved(S.SPEC['t2_1'], 'c5'), 'variant')[1] == 'cold')
ok &= case('K2 t2_counted: letter False, variant True on that arm; a failing arm never counts', not S.t2_counted(t2a) and
""",
     """ok &= case('K1 a T2 arm in form C5 without an in-game creation: admitted, attribution, p362 and the letter "level not cold" (no '
           'creation, no recipe under PRECACHE=0), the variant "cold"', not t2a['fail'] and t2a['attr_ok'] and
           S.gate9(t2a['gates'], S.resolved(S.SPEC['t2_1'], 'c5'), 'letter')[1] == 'level not cold' and
           S.gate9(t2a['gates'], S.resolved(S.SPEC['t2_1'], 'c5'), 'p362')[1] == 'level not cold' and
           t2a['gates']['create_after'] == 0 and S.gate9(t2a['gates'], S.resolved(S.SPEC['t2_1'], 'c5'), 'variant')[1] == 'cold')
ok &= case('K2 t2_counted: p362 (default) False, variant True on that arm; a failing arm never counts', not S.t2_counted(t2a) and
"""),
    ("""ok &= case('K3 read_t2 prints the form, OUT by the letter, the variant count, the S-early row', lt[0].startswith('T2 form: c5;')
           and any(x.startswith('t2_1 hero_kratos: OUT;') for x in lt) and any('T2 counted 0 of 5 needed (variant gate: 1)' == x
                                                                                for x in lt)
""",
     """ok &= case('K3 read_t2 prints the form, OUT by p362, the letter and variant counts, the S-early row',
           lt[0].startswith('T2 form: c5;') and any(x.startswith('t2_1 hero_kratos: OUT;') for x in lt) and
           any('T2 counted 0 of 5 needed (item 362 (b)); by the letter (with the recipe) 0; executor variant 1' == x for x in lt)
"""),
    ("""rm_arm('t2_7')
""",
     """rm_arm('t2_7')


def t2c(tag, hdr_extra=(), pre_entry=(), post_ev=(), form='c5'):
    \"\"\"A T2 arm cold by permutation and skipped draw; creations placed before the entry (header), right after the entry line
    (pre_entry) or after the first scene frame (post_ev).\"\"\"
    post = [(16000, dict(ev=[SH(0x77, 50, 50), SKIP(8)] + list(post_ev), skip=1, held=1))] + rows(10)
    hdr = (HEADER_P0 if form == 'c5' else HEADER_T) + list(hdr_extra)
    mkarm(tag, scene(S.SPEC[tag]['level'], post, header=hdr, pre_entry=pre_entry), form=form, stdout_shaders=1)
    return arm(tag, form)


sp8 = S.resolved(S.SPEC['t2_8'], 'c5')
k7 = t2c('t2_8', post_ev=[GFX(30000, 'async')])
ok &= case('K7 form C5, an in-game creation after the first scene frame: create_after 1, p362 cold, the letter not cold, the '
           'variant cold; t2_counted True, by the letter False', not k7['fail'] and k7['gates']['create_after'] == 1 and
           S.gate9(k7['gates'], sp8, 'p362') == (True, 'cold') and S.gate9(k7['gates'], sp8, 'letter')[0] is False and
           S.gate9(k7['gates'], sp8, 'variant')[0] is True and S.t2_counted(k7) and not S.t2_counted(k7, 'letter'))
lt8 = S.read_t2(getter())
ok &= case('K12 read_t2 with t2_8 counted: its line COUNTED with the three gate words and create_after; the counts 1 / 0 / 2',
           any(x.startswith('t2_8 voxel_challenge_5: COUNTED;') and 'gate (item 362 (b)) cold, by the letter (with the recipe) '
               'level not cold, executor variant cold; in-game creations after the entry 1;' in x for x in lt8) and
           any('T2 counted 1 of 5 needed (item 362 (b)); by the letter (with the recipe) 0; executor variant 2' == x for x in lt8))
k8 = t2c('t2_8', hdr_extra=[GFX(30000, 'async')])
ok &= case('K8 form C5, the only in-game creation before the entry line: create_after 0 -> p362 not cold (the variant cold); the '
           'creation is in the totals', not k8['fail'] and k8['gates']['create_after'] == 0 and k8['create']['n'] == 1 and
           S.gate9(k8['gates'], sp8, 'p362')[0] is False and S.gate9(k8['gates'], sp8, 'variant')[0] is True)
k9 = t2c('t2_8', pre_entry=[GFX(30000, 'none')])
ok &= case('K9 form C5, a creation on the line right after the entry line counts (create_after 1, p362 cold)', not k9['fail'] and
           k9['gates']['create_after'] == 1 and S.gate9(k9['gates'], sp8, 'p362') == (True, 'cold'))
k10 = t2c('t2_8', post_ev=[CSL(5, 'waited')])
ok &= case('K10 form C5, after the entry only a line without " us=" (waited_us): create_after 0 -> p362 not cold',
           not k10['fail'] and k10['gates']['create_after'] == 0 and k10['create']['nous'] == 1 and
           S.gate9(k10['gates'], sp8, 'p362')[0] is False)
spa = S.resolved(S.SPEC['t2_8'], 'app')
k11 = t2c('t2_8', post_ev=[GFX(30000, 'async')], form='app')
k11b = t2c('t2_8', post_ev=['PipelinePrecache: saved 101 recipes (100 bytes)'], form='app')
ok &= case('K11 form APP = the letter: a creation after the entry without a new recipe is not cold; a new recipe without a '
           'creation is cold', not k11['fail'] and k11['gates']['create_after'] == 1 and
           S.gate9(k11['gates'], spa, 'p362')[0] is False and not k11b['fail'] and k11b['gates']['create_after'] == 0 and
           S.gate9(k11b['gates'], spa, 'p362') == (True, 'cold'))
rm_arm('t2_8')
"""),
    ("""ok &= case('L7 by the letter none of five counted -> the reserve t2_6 allowed; u_1 waits for T2', S.allowed('t2_6', mk, g) ==
           (0, 'ok') and S.allowed('u_1', mk, g)[0] == 1)
""",
     """ok &= case('L7 by p362 none of five counted (no in-game creation after the entry) -> the reserve t2_6 allowed; u_1 waits for '
           'T2', S.allowed('t2_6', mk, g) == (0, 'ok') and S.allowed('u_1', mk, g)[0] == 1)
for j in range(1, 6):
    t2_arm('t2_%d' % j, form='c5', create=True)
mk = made()
g = getter()
ok &= case('L8 form C5 with an in-game creation after the entry in t2_1 .. t2_5: five counted by p362 -> T2 done, the reserve t2_6 '
           'refused rc 6, u_1 allowed', sum(1 for j in range(1, 6) if S.t2_counted(g('t2_%d' % j))) == 5 and
           S.t2_done(g, mk) and S.allowed('t2_6', mk, g)[0] == 6 and S.allowed('u_1', mk, g) == (0, 'ok'))
"""),
]

MUT = [
    ("""Not mutated (equivalent - no input can tell the mutant): the identity "scan_x rows = scan_s rows" (both scans count the same
lines;""",
     """Rework 1 (item 362): mutants of the gate p362, the creation line numbers, create_after, READ_3 with the loaded member and the
executor's reading.  Not mutated (equivalent): "ln > el" -> "ln >= el" (the entry line is never a creation line) and the
identity "scan_x lines = scan_s lines" (both count every line).
Not mutated (equivalent - no input can tell the mutant): the identity "scan_x rows = scan_s rows" (both scans count the same
lines;"""),
    ("""    ('gate_read', "T2_GATE_READING = 'letter'", "T2_GATE_READING = 'variant'"),
""",
     """    ('gate_read', "T2_GATE_READING = 'p362'", "T2_GATE_READING = 'letter'"),
    ('gate_read_v', "T2_GATE_READING = 'p362'", "T2_GATE_READING = 'variant'"),
"""),
    ("""    ('pred', "PRED_PATH = 'C:/kyty/s288/pred/05_s.md'", "PRED_PATH = 'C:/kyty/s288/pred/04_s.md'"),
""",
     """    ('pred', "PRED_PATH = 'C:/kyty/s288/pred/05b_s.md'", "PRED_PATH = 'C:/kyty/s288/pred/05_s.md'"),
"""),
    ("""    ('sx_nous', "                        r['create_nous'] += 1", "                        pass"),
""",
     """    ('sx_nous', "                        r['create_nous'] += 1", "                        pass"),
    ('sx_lines', "            r['lines'] += 1\\n", "            pass\\n"),
    ('sx_ln', "                        r['create_ln'].append(r['lines'])", "                        r['create_ln'].append(r['lines'] + 1)"),
    ('sx_ln_off', "                        r['create_ln'].append(r['lines'])", "                        pass"),
"""),
    ("""    ('g_default', "    reading = reading or T2_GATE_READING", "    reading = reading or 'variant'"),
""",
     """    ('g_default', "    reading = reading or T2_GATE_READING", "    reading = reading or 'variant'"),
    ('g_p362', "if reading == 'p362' and spec['pre0']:", "if reading == 'p362':"),
    ('g_p362_off', "if reading == 'p362' and spec['pre0']:", "if False:"),
    ('g_pcreate', "g['perm_after'] >= 1 and g.get('create_after', 0) >= 1 and g['skip_after'] >= 1", "g['perm_after'] >= 1 and g['skip_after'] >= 1"),
    ('g_pperm', "cold = g['perm_after'] >= 1 and g.get('create_after', 0) >= 1", "cold = g.get('create_after', 0) >= 1"),
    ('g_pskip', "g.get('create_after', 0) >= 1 and g['skip_after'] >= 1", "g.get('create_after', 0) >= 1"),
    ('g_pdef', "g.get('create_after', 0) >= 1", "g.get('create_after', 1) >= 1"),
    ('sa_cafter', "if el is not None and ln > el)", "if el is not None and ln < el)"),
    ('sa_cafter_src', "g['create_after'] = sum(1 for ln in sx['create_ln'] if", "g['create_after'] = sum(1 for ln in sx['create'] if"),
"""),
    ("""    ('pw_wor', "w = hz['pi_w1'] or hz['pi_w0']", "w = hz['pi_w1']"),
""",
     """    ('pw_wor', "w = hz['pi_w1'] or hz['pi_w0']", "w = hz['pi_w1']"),
    ('pw_3load', "    if r0:\\n        return 'READ_3' if both_loaded or not need_load", "    if r0:\\n        return 'READ_3' if True or not need_load"),
    ('pw_wload', "    if w:\\n        return 'READ_3' if both_loaded or not need_load", "    if w:\\n        return 'READ_3' if True or not need_load"),
    ('pw_or', "    if r0:\\n        return 'READ_3' if both_loaded or not need_load", "    if r0:\\n        return 'READ_3' if both_loaded and not need_load"),
    ('pw_need', "def pi_word(hz, loaded, need_load=True):", "def pi_word(hz, loaded, need_load=False):"),
    ('rp_wx', "    wx = pi_word(hz, loaded, False)", "    wx = pi_word(hz, loaded)"),
"""),
    ("""    ('rt_counted', "        c = t2_counted(r)\\n", "        c = t2_counted(r, 'variant')\\n"),
""",
     """    ('rt_counted', "        c = t2_counted(r)\\n", "        c = t2_counted(r, 'variant')\\n"),
    ('rt_counted_l', "        counted_l += t2_counted(r, 'letter')", "        counted_l += t2_counted(r, 'variant')"),
    ('rt_gp', "        gp = gate9(r.get('gates'), spec, 'p362')", "        gp = gate9(r.get('gates'), spec, 'letter')"),
"""),
]


def apply(name, reps, check_only):
    p = D + name
    t = open(p, 'rb').read().decode('ascii')
    assert chr(13) not in t, name + ' has CR'
    for a, b in reps:
        n = t.count(a)
        if n != 1:
            print('NO MATCH (%d) in %s: %r' % (n, name, a[:120]))
            return None
        t = t.replace(a, b)
    t.encode('ascii')
    return t


def main():
    if os.path.exists(LOCK):
        print('LOCKED')
        return 5
    out = {}
    for name, reps in (('sc_s9.py', SC), ('go_s9.sh', GO), ('test_go_s9.py', TGO), ('test_sc_s9.py', TSC), ('mut_sc_s9.py', MUT)):
        t = apply(name, reps, True)
        if t is None:
            return 1
        out[name] = t
    if os.path.exists(LOCK):
        print('LOCKED')
        return 5
    for name, t in out.items():
        open(D + name, 'wb').write(t.encode('ascii'))
        print('written %s' % name)
    return 0


if __name__ == '__main__':
    sys.exit(main())
