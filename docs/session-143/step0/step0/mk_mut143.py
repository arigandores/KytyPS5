"""Builds C:/kyty/s143/mut_sc143.py from C:/kyty/s142/mut_sc142.py (link 1b, 245 mutants): the 7 anchors whose text moved in
the port are replaced by the same mutation on the new text; the mutants of the new terms of session 143 are appended.
Every anchor must occur exactly once in sc143.py (LF).  ASCII output."""
import ast
import hashlib

SC = 'C:/kyty/s143/sc143.py'
OLD = 'C:/kyty/s142/mut_sc142.py'
OUT = 'C:/kyty/s143/mut_sc143.py'
t = open(SC, 'rb').read().decode('utf-8')
tree = ast.parse(open(OLD, encoding='utf-8').read())
muts = None
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'MUTANTS':
        muts = ast.literal_eval(node.value)
MOVED = {
    'pred_path': ("PRED_PATH = 'C:/kyty/s143/pred/01_sc143.md'", "PRED_PATH = 'C:/kyty/s142/pred/01_sc143.md'"),
    'seq_vw': ("SEQ=('v142', 'w142') + tuple", "SEQ=('w142', 'v142') + tuple"),
    'ad_val_want': ("want = 'true' if is_w else 'false'", "want = 'true' if not is_w else 'false'"),
    'st_main_before': ('before = [t for t, _ in CENSUS if SEQ.index(t) < SEQ.index(a.stop_check)]',
                       'before = [t for t, _ in CENSUS if SEQ.index(t) <= SEQ.index(a.stop_check)]'),
    'se_me': ("rows.append(('this scorer in the seal', seen.get(SCORER) == mine, mine[:16]))",
              "rows.append(('this scorer in the seal', True, mine[:16]))"),
    'sh_only_v': ("r['sheet'] = sheet_state(root, tag) if tag in V_TAGS else None",
                  "r['sheet'] = sheet_state(root, tag) if tag in W_TAGS else None"),
    'bd_val_w': ("    if tag in W_TAGS:\n        r['admit'].append((", "    if False:\n        r['admit'].append(("),
}
out = []
for name, old, new in muts:
    if name in MOVED:
        old, new = MOVED[name]
    out.append((name, old, new))
NEW = [
    # constants of session 143 (item 231 (i)(1)-(2), (4))
    ('lv_order', "LEVELS = ('spring_punch_sky_aztec', 'booster_construction',", "LEVELS = ('booster_construction', 'spring_punch_sky_aztec',"),
    ('lv_last', "'booster_magic_lamp',\n          'rocket_space_station')", "'booster_magic_lamp',\n          'rocket_space_station_x')"),
    ('pairs_v_num', "PAIRS = tuple(('v143_%02d' % (i + 1),", "PAIRS = tuple(('v143_%02d' % i,"),
    ('pairs_w_num', "'w143_%02d' % (i + 1), lv) for i, lv", "'w143_%02d' % (i + 2), lv) for i, lv"),
    ('census_w', 'CENSUS = tuple((v, lv) for v, _, lv in PAIRS)', 'CENSUS = tuple((w, lv) for _, w, lv in PAIRS)'),
    ('seq_wv', 'SEQ = tuple(t for v, w, _ in PAIRS for t in (v, w))', 'SEQ = tuple(t for v, w, _ in PAIRS for t in (w, v))'),
    ('vtags', 'V_TAGS = tuple(v for v, _, _ in PAIRS)', 'V_TAGS = tuple(w for _, w, _ in PAIRS)'),
    ('wtags', 'W_TAGS = tuple(w for _, w, _ in PAIRS)', 'W_TAGS = tuple(v for v, _, _ in PAIRS)'),
    ('root143', "ROOT = 'C:/kyty/s143'", "ROOT = 'C:/kyty/s142'"),
    ('chain143', "CHAIN = 'go143a'", "CHAIN = 'go142a'"),
    ('runs143', "RUNS = 'runs143'", "RUNS = 'runs142'"),
    ('scorer143', "SCORER = 'sc143.py'", "SCORER = 'sc142.py'"),
    ('extra143', 'EXTRA = True', 'EXTRA = False'),
    ('sealed_fg', "'test_go143a.py', 'fgcpu143.py', 'test_fgcpu143.py',", "'test_go143a.py', 'test_fgcpu143.py',"),
    ('sealed_sheet143', "'gates_default.txt', 'sheet142.py',\n                'test_go143a.py'", "'gates_default.txt',\n                'test_go143a.py'"),
    ('sealed_mut143', "'mut_sc143.py', 'enter_scene.py',", "'enter_scene.py',"),
    ('sealed_vid143', "'test_fgcpu143.py', 'C:/kyty/scripts/s51_vidglitch.py')", "'test_fgcpu143.py')"),
    ('hold_w_harness_up', 'HOLD_W_HARNESS_S = 310', 'HOLD_W_HARNESS_S = 311'),
    ('hold_w_harness_down', 'HOLD_W_HARNESS_S = 310', 'HOLD_W_HARNESS_S = 309'),
    # profile 142 (the regression of item 231 (i)(4))
    ('p142_root', "P142 = dict(ROOT='C:/kyty/s142',", "P142 = dict(ROOT='C:/kyty/s141',"),
    ('p142_pred', "PRED_PATH='C:/kyty/s142/pred/02_sc142.md', CHAIN=", "PRED_PATH='C:/kyty/s142/pred/01_sc142.md', CHAIN="),
    ('p142_chain', "CHAIN='go142a', RUNS='runs142',", "CHAIN='go143a', RUNS='runs142',"),
    ('p142_runs', "RUNS='runs142',\n", "RUNS='runs143',\n"),
    ('p142_scorer', "SCORER='sc142.py', EXTRA=False,", "SCORER='sc143.py', EXTRA=False,"),
    ('p142_extra', 'EXTRA=False, PAIRS=', 'EXTRA=True, PAIRS='),
    ('p142_pairs', "PAIRS=(('v142', 'w142', SKY),)", "PAIRS=(('w142', 'v142', SKY),)"),
    ('p142_vtags', "V_TAGS=('v142',),", "V_TAGS=(),"),
    ('p142_wtags', "W_TAGS=('w142',),", "W_TAGS=(),"),
    ('p142_census', 'CENSUS=CENSUS142,', 'CENSUS=CENSUS142[1:],'),
    ('regress_file', "REGRESS_FILE = 'C:/kyty/s142/step4/summary142_viewed.txt'", "REGRESS_FILE = 'C:/kyty/s142/step2/summary142.txt'"),
    ('regress_b33', "REGRESS_B33 = ('c142_02', 'c142_03', 'c142_05')", "REGRESS_B33 = ('c142_02', 'c142_03')"),
    # profile(), level_of, admission, build
    ('pf_update', '    g.update(values)\n', '    pass\n'),
    ('pf_old', 'old = dict((k, g[k]) for k in values)', 'old = dict(values)'),
    ('lo_w', '        if tag in (v, w):\n', '        if tag == v:\n'),
    ('ad_is_w', 'is_w = tag in W_TAGS', 'is_w = tag in V_TAGS'),
    ('bd_guest', "admit=admit(tag, js, pred_sha), guest_args=js.get('guest_args'))", "admit=admit(tag, js, pred_sha), guest_args=None)"),
    # derive: the K3 hold within 120 s (B33 executor variant)
    ('k120_gt', '        if cum > HOLD_CENSUS_US:\n', '        if cum >= HOLD_CENSUS_US:\n'),
    ('k120_cum', '        cum += r[1]\n', '        cum += 0\n'),
    ('k120_win', "out['k3h120'] = [(r[0], r[1]) for r in post[ENTRY_WIN:] if r[3] in within", "out['k3h120'] = [(r[0], r[1]) for r in post if r[3] in within"),
    ('k120_lo', "if r[3] in within and K3_US <= r[1] < K2_US]", "if r[3] in within and K3_US < r[1] < K2_US]"),
    # scene_ok per pair
    ('sk_pair_tags', "v['tag'] == vt and w['tag'] == wt and v['guest_args'] == want", "True and v['guest_args'] == want"),
    ('sk_pair_vguest', "and w['tag'] == wt and v['guest_args'] == want\n", "and w['tag'] == wt\n"),
    ('sk_pair_wguest', "            and w['guest_args'] == want, '%s / %s'", "            and True, '%s / %s'"),
    ('sk_pair_off', '    if EXTRA:\n        want = ', '    if False:\n        want = '),
    ('sk_default_pair', 'vt, wt, lv = pair if pair is not None else PAIRS[0]', 'vt, wt, lv = pair if pair is not None else PAIRS[-1]'),
    ('sk_sheet_label', "                 % (vt, vt), file_ok,", "                 % (wt, wt), file_ok,"),
    # summary
    ('su_sheet_tags', 'sh = sheet if (sheet_tags is None or vt in sheet_tags) else None', 'sh = sheet'),
    ('su_pair_arg', 'word, rows = scene_ok(ents[vt], ents[wt], sh, (vt, wt, lv))', 'word, rows = scene_ok(ents[vt], ents[wt], sh)'),
    ('su_w310', "('yes' if (w['hold_s'] or 0) >= HOLD_W_HARNESS_S else", "('yes' if (w['hold_s'] or 0) > HOLD_W_HARNESS_S else"),
    ('su_levels_yes', "words.count('YES'), words.count('PENDING_SHEET')", "words.count('PENDING_SHEET'), words.count('PENDING_SHEET')"),
    ('su_levels_no', "words.count('NO'), len(PAIRS)))", "len(PAIRS) - 1, len(PAIRS)))"),
    ('su_b33_off', '    if EXTRA:\n        b33, b33v, b33t = form_b33(adm)', '    if False:\n        b33, b33v, b33t = form_b33(adm)'),
    ('b33_letter', "tags = [e['tag'] for e in ents if e['derive']['k3h']]", "tags = [e['tag'] for e in ents if e['derive']['k3w']]"),
    ('b33_var', "var = sum(1 for e in ents if e['derive']['k3h120'])", "var = sum(1 for e in ents if e['derive']['k3h'])"),
    ('fe_k120_off', "    if EXTRA:\n        o.append('  K3 hold within 120 s", "    if True:\n        o.append('  K3 hold within 120 s"),
    # the regression
    ('rg_same', 'same = raw == new and bool(raw)', 'same = bool(raw)'),
    ('rg_crlf', "new = ('\\r\\n'.join(out) + '\\r\\n').encode('ascii', 'replace')", "new = ('\\n'.join(out) + '\\n').encode('ascii', 'replace')"),
    ('rg_b33', 'b33ok = tuple(b33t) == REGRESS_B33', 'b33ok = True'),
    ('rg_restore', '    finally:\n        profile(old)\n', '    finally:\n        pass\n'),
    ('rg_sheet', "out, ents, _ = summary(ROOT, pred_sha, 'viewed')", "out, ents, _ = summary(ROOT, pred_sha, None)"),
    ('rg_adm', "adm = [ents[t] for t, _ in CENSUS if ents[t] is not None and all(a[1] for a in ents[t]['admit'])]",
     "adm = [ents[t] for t, _ in CENSUS if ents[t] is not None]"),
    # main
    ('ma_regress_rc', '        return 0 if ok else 1\n    pred_sha = ', '        return 0\n    pred_sha = '),
    ('ma_sheet_tags_bad', 'bad = [t for t in tags if t not in V_TAGS]', 'bad = []'),
    ('ma_sheet_tags_pass', 'out, _, _ = summary(root, pred_sha, a.sheet, tags)', 'out, _, _ = summary(root, pred_sha, a.sheet)'),
]
names = set()
bad = 0
for name, old, new in out + NEW:
    c = t.count(old)
    if c != 1 or name in names or old == new:
        print('BAD %s count %d' % (name, c))
        bad += 1
    names.add(name)
allm = out + NEW
print('mutants: %d (carried %d, of them moved %d; new %d); bad anchors %d' % (len(allm), len(out), len(MOVED), len(NEW), bad))
src = open(OLD, encoding='utf-8').read()
head = src[:src.index('MUTANTS = [')]
head = head.replace('"""Session 142 step 0 (HPP-277), link 1b (HPP-282; ROADMAP s122 item 224 (a), (b)(3)): mutants of sc142.py (the scorer of\nthe scene census sc142 and of SCENE_OK on Sky Garden) - each must be killed by test_sc142.py.',
                    '"""Session 143 step 0 (HPP-297; ROADMAP s122 item 231 (i)(4)): mutants of sc143.py (the scorer of the SCENE_OK series sc143,\nthe port of sc142.py with profile 142 for the regression) - each must be killed by test_sc143.py.  The 245 mutants of\nmut_sc142.py of link 1b are carried (7 anchors moved with the port: pred_path, seq_vw, ad_val_want, st_main_before, se_me,\nsh_only_v, bd_val_w - the same mutation on the new text), then the mutants of the new terms of session 143 (levels, pairs,\norder, seal, chain, profile 142, the pair row, the sheet per V, B33 and its 120 s variant, the W 310 s info, the levels\nline, the regression, main).  Equivalent, not mutated: regress142 "and not diff" (raw == new already makes diff empty).\nSession 142 header (carried): mutants of sc142.py - each must be killed by test_sc142.py.')
head = head.replace('python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s142/sc142.py\n        --test C:/kyty/s142/test_sc142.py --mutants C:/kyty/s142/mut_sc142.py --control --no-memo --workers 8\n        --work-dir C:/kyty/s142/mutwork1b --cache-dir C:/kyty/s142/mutcache1b --out C:/kyty/s142/mut_sc142_1b.txt',
                    'python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s143/sc143.py\n        --test C:/kyty/s143/test_sc143.py --mutants C:/kyty/s143/mut_sc143.py --control --no-memo --workers 12\n        --work-dir C:/kyty/s143/mutwork --cache-dir C:/kyty/s143/mutcache --out C:/kyty/s143/mut_sc143.txt')
assert 'sc143' in head.split('\n')[0] and '--workers 12' in head
body = 'MUTANTS = [\n' + ''.join('    (%r, %r, %r),\n' % m for m in allm) + ']\n'
open(OUT, 'w', encoding='utf-8', newline='\n').write(head + body)
print('wrote %s sha256 %s' % (OUT, hashlib.sha256(open(OUT, 'rb').read()).hexdigest()))
