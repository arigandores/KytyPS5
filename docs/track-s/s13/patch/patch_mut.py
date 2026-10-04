"""S13a4 (HPP-553, ROADMAP item 452 (b)-(d)): patch s13/mut_sc_s13.py - drop the mutants of the removed n_pre, rename the edition
mutants to seal 13, follow members_w (gating_fail), add the mutants of RC1 (nopb_data, fmt_nopb, the data lines) and RC2 (the
lists of names, row_class, post_fail, gating_fail, the print).  Then check every mutant target occurs exactly once in sc_s13.py.
LF, ASCII.
    python patch_mut.py <mut_sc_s13.py> <sc_s13.py>
"""
import importlib.util
import sys

NL = chr(10)
P, SC = sys.argv[1], sys.argv[2]
src = open(P, 'rb').read().decode('ascii')
assert chr(13) not in src
REPL = []


def R(a, b):
    REPL.append((a, b))


R('''"""Track S link S13a2 (HPP-498; ROADMAP "SESSION 122" item 408 (l), item 229 (e)(1), (3), item 414, item 428), reworked by S13a3
(HPP-537, item 436 (b)(1)-(7)): mutants of s13/sc_s13.py -''',
  '''"""Track S link S13a2 (HPP-498; ROADMAP "SESSION 122" item 408 (l), item 229 (e)(1), (3), item 414, item 428), reworked by S13a3
(HPP-537, item 436 (b)(1)-(7)) and S13a4 (HPP-553, item 452 (b), (c): RC1 the data of item 446 (b), RC2 the class "after the
arm"): mutants of s13/sc_s13.py -''')
R('''a log - then the RC2 gate is "missing" and every W member but E3-death is undetermined whatever the row says).''',
  '''a log - then the RC2 gate is "missing" and every W member but E3-death is undetermined whatever the row says).  S13a4: "x[4] >
later" -> ">=" in nopb_data (a FrameTrace row is never a preparation line); the anchor "$" and ".+?" -> ".*?" in _rx (no
admission name of one list is a prefix of a name of another, and no template part is empty); "nopb=None" dropped in the no-log
return of score_arm (r.get('nopb') is None either way).''')
R('''    ('g2_npre', "    r['n_pre'] = len(r['admit'])            #", "    r['n_pre'] = 0            #"),
    ('g2_pre_slice', "    pre = [a[0] for a in r['admit'][:r.get('n_pre', len(r['admit']))] if not a[1]]",
     "    pre = [a[0] for a in r['admit'] if not a[1]]"),
''', '')
R('''    ('mw_gate', "    out = [('catalogue installed (gates)', True if g else None, gw)]\\n    if not ok_arm(r) or not r.get('entered') or not g:",
     "    out = [('catalogue installed (gates)', True, gw)]\\n    if not ok_arm(r) or not r.get('entered') or not g:"),''',
  '''    ('mw_gate', "    out = [('catalogue installed (gates)', True if g else None, gw)]\\n    if gating_fail(r) or not r.get('entered') or not g:",
     "    out = [('catalogue installed (gates)', True, gw)]\\n    if gating_fail(r) or not r.get('entered') or not g:"),''')
R('''    ('ed6_rel', "SEAL_BASE_REL = 'pred/12_s.md' ", "SEAL_BASE_REL = 'pred/11_s.md' "),''',
  '''    ('ed6_rel', "SEAL_BASE_REL = 'pred/13_s.md' ", "SEAL_BASE_REL = 'pred/12_s.md' "),''')
R('''    ('mf_attempt',''', r'''    # item 452 (b), RC1 of S13r2: the data of the reading of item 446 (b)
    ('n1_created', "    if cr is not None:\n        why = 'not counted: the line", "    if False:\n        why = 'not counted: the line"),
    ('n1_ready', "    elif rd is None:\n        why = 'not counted: no line", "    elif False:\n        why = 'not counted: no line"),
    ('n1_nopb', "    elif nb is None:\n        why = 'not counted: no line", "    elif False:\n        why = 'not counted: no line"),
    ('n1_max_rd', "    later = None if why is not None else max(rd, nb)\n", "    later = None if why is not None else rd\n"),
    ('n1_max_nb', "    later = None if why is not None else max(rd, nb)\n", "    later = None if why is not None else nb\n"),
    ('n1_max_min', "    later = None if why is not None else max(rd, nb)\n", "    later = None if why is not None else min(rd, nb)\n"),
    ('n1_rows_ft', "    rows = None if later is None else sum(1 for x in s['rows'] if x[4] > later)",
     "    rows = None if later is None else len(s['rows'])"),
    ('n1_text', "                r['nopb_text'] = line.rstrip().decode('ascii', 'backslashreplace')\n", ""),
    ('n1_text_esc', "r['nopb_text'] = line.rstrip().decode('ascii', 'backslashreplace')",
     "r['nopb_text'] = line.rstrip().decode('ascii', 'replace')"),
    ('n1_var', "        var = len(parts) >= 2 and parts[-2] == inst[2]", "        var = len(parts) >= 2"),
    ('n1_var_slash', "        parts = path.replace('/', chr(92)).split(chr(92))", "        parts = path.split(chr(92))"),
    ('n1_var_inst', "    if tx is not None and inst is not None and inst[2]:", "    if tx is not None and inst is not None:"),
    ('n1_line', "    return dict(line=nb, text=tx,", "    return dict(line=rd, text=tx,"),
    ('n1_fmt_text', "    i = 'line %d \"%s\"' % (d['line'], d['text']) if d['line'] is not None else 'none'",
     "    i = 'line %d' % d['line'] if d['line'] is not None else 'none'"),
    ('n1_fmt_rows', "    ii = '%d' % d['rows_after'] if d['why'] is None else d['why']", "    ii = d['why'] or '-'"),
    ('n1_fmt_var', "{True: 'yes', False: 'NO', None: 'n/a'}[d['variant']]", "{True: 'yes', False: 'yes', None: 'n/a'}[d['variant']]"),
    ('n1_pr_arm', "    o.append('  data of item 446 (b) (item 452 (b), no outcome reads it): %s' % fmt_nopb(r))\n", ""),
    ('n1_pr_k', "        out.append('%s data of item 446 (b) (item 452 (b), no outcome reads it): %s' % (t, fmt_nopb(r)))\n        out.append('%s rows after the arm (item 452 (c)): %s' % (t, fmt_post(r)))\n    return out",
     "        out.append('%s rows after the arm (item 452 (c)): %s' % (t, fmt_post(r)))\n    return out"),
    ('n1_pr_u', "        out.append('%s data of item 446 (b) (item 452 (b), no outcome reads it): %s' % (t, fmt_nopb(r)))\n        out.append('%s rows after the arm (item 452 (c)): %s' % (t, fmt_post(r)))\n    rw = get('w13')",
     "        out.append('%s rows after the arm (item 452 (c)): %s' % (t, fmt_post(r)))\n    rw = get('w13')"),
    ('n1_pr_w', "    out.append('w13 data of item 446 (b) (item 452 (b), no outcome reads it): %s' % fmt_nopb(rw))\n", ""),
    # item 452 (c), RC2 of S13r2: the class "after the arm" by an explicit list of names
    ('n2_pre_cls', "if not a[1] and row_class(a[0]) in (C_PRE, None)]", "if not a[1] and row_class(a[0]) != C_LOG]"),
    ('n2_uncl', "if not a[1] and row_class(a[0]) in (C_PRE, None)]", "if not a[1] and row_class(a[0]) == C_PRE]"),
    ('n2_post_cls', "C_PRE, C_LOG, C_POST = 'before the run', 'by the log', 'after the arm'",
     "C_PRE, C_LOG, C_POST = 'before the run', 'by the log', 'before the run'"),
    ('n2_glc_drop', "ADMIT_POST = ('return_app after the arm = its copy', 'return_glc after the arm = its copy',",
     "ADMIT_POST = ('return_app after the arm = its copy',"),
    ('n2_glc_pre', "ADMIT_PRE = ('one attempt (--attempts 1, no warmup)',",
     "ADMIT_PRE = ('return_glc after the arm = its copy', 'one attempt (--attempts 1, no warmup)',"),
    ('n2_app_drop', "ADMIT_POST = ('return_app after the arm = its copy', 'return_glc", "ADMIT_POST = ('return_glc"),
    ('n2_bin_drop', "              'installed binary after the arm = before the arm (item 250 (b))',\n", ""),
    ('n2_mpa_drop', "              'manifest man_post_app recorded', 'manifest man_post_glc recorded',",
     "              'manifest man_post_glc recorded',"),
    ('n2_mpg_drop', "              'manifest man_post_app recorded', 'manifest man_post_glc recorded',",
     "              'manifest man_post_app recorded',"),
    ('n2_apc_drop', "              'app_post_copy recorded (cat/{}, the next arm restores it)')", "              )"),
    ('n2_pre_inst_drop', "             'installed binary before the arm = the seal line \"installed:\" (S9r2 observation 3)',\n", ""),
    ('n2_log_drop', "             '0 lines GamePatch: in the log (item 342 (e))',\n", ""),
    ('n2_amb', "    return hits[0] if len(hits) == 1 else None", "    return hits[0] if hits else None"),
    ('n2_postfail', "    return [a[0] for a in r['admit'] if not a[1] and row_class(a[0]) == C_POST]", "    return []"),
    ('n2_gating', "    return [x for x in r['fail'] if x not in post]", "    return list(r['fail'])"),
    ('n2_mw', "    if gating_fail(r) or not r.get('entered') or not g:", "    if r['fail'] or not r.get('entered') or not g:"),
    ('n2_pr_arm', "    o.append('  rows after the arm (item 452 (c)): %s' % fmt_post(r))\n", ""),
    ('n2_pr_cls', "row_class(name) or 'UNCLASSED', name, det))", "'before the run', name, det))"),
    ('n2_pr_uncl', "row_class(name) or 'UNCLASSED', name, det))", "row_class(name) or 'before the run', name, det))"),
    ('n2_fmt_ok', "    return 'ok' if not pf else 'FAIL %s - entry_state void, the members not gated' % '; '.join(pf)",
     "    return 'FAIL %s - entry_state void, the members not gated' % '; '.join(pf)"),
    ('n2_pr_k', "        out.append('%s data of item 446 (b) (item 452 (b), no outcome reads it): %s' % (t, fmt_nopb(r)))\n        out.append('%s rows after the arm (item 452 (c)): %s' % (t, fmt_post(r)))\n    return out",
     "        out.append('%s data of item 446 (b) (item 452 (b), no outcome reads it): %s' % (t, fmt_nopb(r)))\n    return out"),
    ('n2_pr_u', "        out.append('%s data of item 446 (b) (item 452 (b), no outcome reads it): %s' % (t, fmt_nopb(r)))\n        out.append('%s rows after the arm (item 452 (c)): %s' % (t, fmt_post(r)))\n    rw = get('w13')",
     "        out.append('%s data of item 446 (b) (item 452 (b), no outcome reads it): %s' % (t, fmt_nopb(r)))\n    rw = get('w13')"),
    ('n2_pr_w', "    out.append('w13 rows after the arm (item 452 (c)): %s' % fmt_post(rw))\n", ""),
    ('mf_attempt',''')

for a, b in REPL:
    n = src.count(a)
    if n != 1:
        raise SystemExit('patch_mut: the target occurs %d times: %r' % (n, a[:120]))
    src = src.replace(a, b)
# the edition mutants name seal 13
n12 = src.count('edition 12b: ') + src.count('the seal 12 exists') + src.count('of 12 but') + src.count('is in 12b,')
src = src.replace('edition 12b: ', 'edition 13b: ').replace('the seal 12 exists', 'the seal 13 exists').replace(
    'of 12 but', 'of 13 but').replace('is in 12b,', 'is in 13b,')
src.encode('ascii')
open(P, 'wb').write(src.encode('ascii'))
spec = importlib.util.spec_from_file_location('mutx', P)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
sc = open(SC, 'rb').read().decode('ascii')
bad = [(m[0], sc.count(m[1])) for m in M.MUTANTS if sc.count(m[1]) != 1]
ids = [m[0] for m in M.MUTANTS]
dup = sorted(set(x for x in ids if ids.count(x) > 1))
same = [m[0] for m in M.MUTANTS if m[1] == m[2]]
print('patch_mut: %d replacements, %d edition names renamed; mutants %d (n1 %d, n2 %d); targets not exactly once: %s; duplicate '
      'ids: %s; identical replacements: %s' % (len(REPL), n12, len(M.MUTANTS), sum(1 for x in ids if x.startswith('n1_')),
                                               sum(1 for x in ids if x.startswith('n2_')), bad or 'none', dup or 'none',
                                               same or 'none'))
sys.exit(0 if not bad and not dup and not same else 1)
