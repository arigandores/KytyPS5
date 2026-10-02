"""mk_mut146.py - session 146 step 0 (HPP-386): writes C:/kyty/s146/mut_sc146.py - the 714 mutants of mut_sc145.py carried
(9 re-anchored on the text the port moved) + the mutants of the new terms of profile 146.  Every anchor must occur exactly
once in sc146.py (checked here; a failure stops the script).  LF, ASCII."""
import hashlib
import importlib.util
import sys

SC = 'C:/kyty/s146/sc146.py'
OLD = 'C:/kyty/s145/mut_sc145.py'
DST = 'C:/kyty/s146/mut_sc146.py'
t = open(SC, encoding='ascii').read()
spec = importlib.util.spec_from_file_location('m145', OLD)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
B145 = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
B146 = 'dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e'
OTHER = '05431dad252676b05128828a42169de0c1f84aff799838a513a0d80b32afcd84'
REANCHOR = {
    'build_sha': ("BUILD145 = '%s'" % B145, "BUILD145 = '%s'" % OTHER),
    'sk_pending': ("    else:\n        word = 'PENDING_SHEET'\n    rows.append((", "    else:\n        word = 'YES'\n    rows.append(("),
    'pr_level': ("e['guest_args'] == want and e['att_level'] == lv and e['log_sha'] is not None",
                 "e['guest_args'] == want and e['log_sha'] is not None"),
    'pr_sha_none': ("e['guest_args'] == want and e['att_level'] == lv and e['log_sha'] is not None\n",
                    "e['guest_args'] == want and e['att_level'] == lv\n"),
    'n_ad_isw': ("        elif is_w:\n            add('W form: KYTY_PIPELINE_PRECACHE=0", "        elif not is_w:\n            add('W form: KYTY_PIPELINE_PRECACHE=0"),
    'n_bd_wtag': ("        elif tag in W_TAGS:\n            r['admit'].append(('W form:", "        elif tag in V_TAGS:\n            r['admit'].append(('W form:"),
    'e_s4_stop': ('        stop = stop or ev\n', '        stop = stop\n'),
    'e_su_cold_off': ("    elif FORM145:\n        out.append('CENSUS = the V tags %s..%s, COLD", "    elif False:\n        out.append('CENSUS = the V tags %s..%s, COLD"),
    'ma_regress_rc': ("        ok, lines = regress144()\n        print('\\n'.join(lines))\n        return 0 if ok else 1\n",
                      "        ok, lines = regress144()\n        print('\\n'.join(lines))\n        return 0\n"),
    'l_seal_ref': ("                'C:/kyty/s144/runs144/cache_w144_20.after.json')\nP145 = dict(",
                   "                'C:/kyty/s144/runs144/cache_w144_20.after.jsn')\nP145 = dict("),
}
NEW = [
    # constants of profile 146 (cheap failures first)
    ('g_b146', "BUILD146 = '%s'" % B146, "BUILD146 = '%s'" % OTHER),
    ('g_root', "P146 = dict(ROOT='C:/kyty/s146',", "P146 = dict(ROOT='C:/kyty/s147',"),
    ('g_chain', "CHAIN='go146a', RUNS='runs146',", "CHAIN='go145a', RUNS='runs146',"),
    ('g_runs', "CHAIN='go146a', RUNS='runs146',", "CHAIN='go146a', RUNS='runs145',"),
    ('g_pred', "PRED_PATH='C:/kyty/s146/pred/01_sc146.md'", "PRED_PATH='C:/kyty/s146/pred/02_sc146.md'"),
    ('g_scorer', "SCORER='sc146.py', EXTRA=True, FORM144=True, FORM145=True, FORM146=True,",
     "SCORER='sc145.py', EXTRA=True, FORM144=True, FORM145=True, FORM146=True,"),
    ('g_f146', "SCORER='sc146.py', EXTRA=True, FORM144=True, FORM145=True, FORM146=True,",
     "SCORER='sc146.py', EXTRA=True, FORM144=True, FORM145=True, FORM146=False,"),
    ('g_p145_f146', "            FORM145=FORM145, FORM146=FORM146, REPEAT=REPEAT,", "            FORM145=FORM145, FORM146=True, REPEAT=REPEAT,"),
    ('g_p145_build', "REPEAT=REPEAT, BUILD_SHA=BUILD_SHA, RECHECK=RECHECK,", "REPEAT=REPEAT, BUILD_SHA=BUILD146, RECHECK=RECHECK,"),
    ('g_p145_rck', "REPEAT=REPEAT, BUILD_SHA=BUILD_SHA, RECHECK=RECHECK,", "REPEAT=REPEAT, BUILD_SHA=BUILD_SHA, RECHECK=RECHECK146,"),
    ('g_f146_def', "FORM146 = False\n", "FORM146 = True\n"),
    ('g_half145', "P145['HALF'] = HALF\n", "P145['HALF'] = 6\n"),
    ('g_pold', "    _p.update(FORM146=False, BUILD_SHA=BUILD145, RECHECK=())", "    _p.update(FORM146=True, BUILD_SHA=BUILD145, RECHECK=())"),
    ('g_new_first', "NEW146 = ('robot_builder_next', 'interactive_credit_00',", "NEW146 = ('robot_builder', 'interactive_credit_00',"),
    ('g_new_last', "'voxel_challenge_2',\n          'fragile_battle_3')", "'voxel_challenge_2',\n          'fragile_battle_4')"),
    ('g_rck_order', "RECHECK146 = (('r146_01', 'hoover_beach'), ('r146_02', 'sponge_dirty_bath'),",
     "RECHECK146 = (('r146_01', 'sponge_dirty_bath'), ('r146_02', 'hoover_beach'),"),
    ('g_rck_b40', "              ('r146_04', 'bonus_path_maker_mix'))", "              ('r146_04', 'bonus_path_maker'))"),
    ('g_b40tag', "B40_TAG = 'r146_04'", "B40_TAG = 'r146_03'"),
    ('g_b40first', "B40_FIRST = 'v145_14'", "B40_FIRST = 'v145_13'"),
    ('g_warm', "WARMUP = ('i146_v', 'score_i146_v.txt')", "WARMUP = ('i146_v', 'score_i146.txt')"),
    ('g_ctrl', "CONTROL146 = ('w146_00', SKY)", "CONTROL146 = ('w146_01', SKY)"),
    ('g_pairs_num', "PAIRS146 = tuple(('v146_%02d' % (i + 5), 'w146_%02d' % (i + 5), lv)",
     "PAIRS146 = tuple(('v146_%02d' % (i + 5), 'w146_%02d' % (i + 6), lv)"),
    ('g_seq_order', "            SEQ=(CONTROL146[0],) + tuple(r for r, _ in RECHECK146) + tuple(x for v, w, _ in PAIRS146 for x in (v, w)),",
     "            SEQ=(CONTROL146[0],) + tuple(x for v, w, _ in PAIRS146 for x in (v, w)) + tuple(r for r, _ in RECHECK146),"),
    ('g_seq_wv', "tuple(x for v, w, _ in PAIRS146 for x in (v, w)),\n            V_TAGS",
     "tuple(x for v, w, _ in PAIRS146 for x in (w, v)),\n            V_TAGS"),
    ('g_vtags_r', "            V_TAGS=tuple(r for r, _ in RECHECK146) + tuple(v for v, _, _ in PAIRS146),",
     "            V_TAGS=tuple(v for v, _, _ in PAIRS146),"),
    ('g_wtags_c', "            W_TAGS=(CONTROL146[0],) + tuple(w for _, w, _ in PAIRS146), SEALED_NAMES=SEALED146,",
     "            W_TAGS=tuple(w for _, w, _ in PAIRS146), SEALED_NAMES=SEALED146,"),
    ('g_census', "            CENSUS=tuple((v, lv) for v, _, lv in PAIRS146),", "            CENSUS=tuple((v, lv) for v, _, lv in PAIRS146[1:]),"),
    ('g_rck_set', "            RECHECK=RECHECK146, LEVELS=", "            RECHECK=(), LEVELS="),
    ('g_sealed', "'lockcheck146.py', 'tiles146.py', 'test_tools146.py',", "'lockcheck146.py', 'test_tools146.py',"),
    ('g_sealed_lvl', "             'step0/lvl146.py', 'step0/lvl146.out.txt',", "             'step0/lvl146.py',"),
    ('g_m_stub', "M_STUBCALL = b'Unresolved import stub called'", "M_STUBCALL = b'Unresolved import stub'"),
    ('g_m_assert', "M_ASSERT = b'ASSERT:'", "M_ASSERT = b'ASSERT'"),
    ('g_m_ump', "M_UMP = b'user_msg_param'", "M_UMP = b'user_msg'"),
    ('g_rx_dual', "RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\\d+) enabled=(\\d+)')",
     "RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\\d+) enabled=(\\d)')"),
    ('g_rx_tiles', "tile events T4 (\\d+), T12 (\\d+); events (.*)$')", "tile events T4 (\\d+), T12 (\\d+); events (.+)$')"),
    # scan
    ('s_stub', "            res['stubcall'] += whole.count(M_STUBCALL)\n", ''),
    ('s_assert', "            res['asserts'] += whole.count(M_ASSERT)\n", ''),
    ('s_ump', "            res['ump'] += whole.count(M_UMP)\n", ''),
    ('s_dual_v', "                res['dual'].append((base + m.start(), (int(m.group(1)), int(m.group(2)))))\n",
     "                res['dual'].append((base + m.start(), (int(m.group(1)), int(m.group(1)))))\n"),
    # level_of, admission, build
    ('l_rck', "    for t, lv in RECHECK:\n        if t == tag:\n            return lv\n", ''),
    ('a_pc', "                '281 (g))', pc is None, pc)", "                '281 (g))', pc is None or pc == '0', pc)"),
    ('a_branch', "        if is_w and FORM146:\n            add('W form on the shipment binary",
     "        if is_w and not FORM146:\n            add('W form on the shipment binary"),
    ('b_wskip', "        if tag in W_TAGS and FORM146:\n            pass\n", "        if False:\n            pass\n"),
    ('b_stub_std', "stdout=std['stubcall'] if std is not None else None)", "stdout=None)"),
    ('b_ump_std', "ump_stdout=std['ump'] if std is not None else None)", "ump_stdout=0)"),
    ('b_dual11', "if v == (1, 1) and (gp is None or p < gp)) if log is not None else 0",
     "if v[0] == 1 and (gp is None or p < gp)) if log is not None else 0"),
    ('b_dual_pos', "if v == (1, 1) and (gp is None or p < gp)) if log is not None else 0",
     "if v == (1, 1)) if log is not None else 0"),
    ('b_dual_nog', "if v == (1, 1) and (gp is None or p < gp)) if log is not None else 0",
     "if v == (1, 1) and (gp is not None and p < gp)) if log is not None else 0"),
    ('b_dual_ge', "        r['dual_ok'] = r['dual_pre'] >= 1\n", "        r['dual_ok'] = r['dual_pre'] >= 2\n"),
    ('b_tiles_v', "        r['tiles'] = read_tiles(root, tag) if tag in V_TAGS else None\n",
     "        r['tiles'] = read_tiles(root, tag) if tag in W_TAGS else None\n"),
    ('c_dual', "    if FORM146 and not e.get('dual_ok'):\n", "    if False:\n"),
    # the stop-check source
    ('j_src', "    if src == 'json':\n        p = os.path.join(root, RUNS,", "    if False:\n        p = os.path.join(root, RUNS,"),
    ('j_sha', "                if e.get('log_sha') is not None and e.get('log_sha') == ts:\n",
     "                if e.get('log_sha') is not None:\n"),
    ('j_broken', "                why = 'score.json broken'\n", ''),
    ('j_vs', "    if FORM146:\n        vs = [t for t in before if t in V_TAGS and made(t, root)]\n",
     "    if False:\n        vs = [t for t in before if t in V_TAGS and made(t, root)]\n"),
    ('j_srcline', "    if FORM146:\n        lines.append('STOP CHECK SOURCES", "    if False:\n        lines.append('STOP CHECK SOURCES"),
    ('j_main', "stop_check144(a.stop_check, root, pred_sha, 'json' if FORM146 else 'log')",
     "stop_check144(a.stop_check, root, pred_sha, 'log')"),
    # skip
    ('k_file', "    return os.path.isfile(os.path.join(root, 'skipped_%s.txt' % t))", "    return os.path.isfile(os.path.join(root, 'skip_%s.txt' % t))"),
    ('k_pairv', "        if w2 == w:\n            return v\n", "        if w2 == w:\n            return w2\n"),
    ('k_ne', "    if e['outcome'] == 'NOT_ENTERED':\n        return True, 'SKIPPED_V_NOT_ENTERED",
     "    if e['outcome'] != 'NOT_ENTERED':\n        return True, 'SKIPPED_V_NOT_ENTERED"),
    ('k_none', "        return False, 'RUN %s: its V %s has no reading (%s)' % (w, v, s)",
     "        return True, 'RUN %s: its V %s has no reading (%s)' % (w, v, s)"),
    ('k_main_rc', "        print(line)\n        return 0 if sk else 1\n", "        print(line)\n        return 0\n"),
    # summary of 146
    ('u_mach', "        if not machine:\n            word = 'REMOVES SCENE_OK'\n", "        if False:\n            word = 'REMOVES SCENE_OK'\n"),
    ('u_file', "            word = 'PASSES' if file_ok else 'REMOVES SCENE_OK'\n", "            word = 'PASSES'\n"),
    ('u_notv', "        elif sh == 'not-viewed':\n            word = 'REMOVES SCENE_OK'\n", "        elif sh == 'not-viewed':\n            word = 'PENDING_SHEET'\n"),
    ('u_tags', "        sh = sheet if (sheet_tags is None or rt in sheet_tags) else None\n        if e is None:\n            out.append('RECHECK",
     "        sh = sheet\n        if e is None:\n            out.append('RECHECK"),
    ('u_pairrow', "        vr = [x for x in rows if x[0].startswith('V ') and 'are the pair of one level' not in x[0]\n",
     "        vr = [x for x in rows if x[0].startswith('V ')\n"),
    ('u_guest_sha', "        vr.append(('V guest args -lvl %s, json level %s, sha256 of the log read = the enter_scene end line of step2/times.txt'\n"
                    "                   % (lv, lv), e['guest_args'] == '-lvl %s' % lv and e['att_level'] == lv and e['log_sha'] is not None\n"
                    "                   and e['log_sha'] == e['times_log_sha'],",
     "        vr.append(('V guest args -lvl %s, json level %s, sha256 of the log read = the enter_scene end line of step2/times.txt'\n"
     "                   % (lv, lv), e['guest_args'] == '-lvl %s' % lv and e['att_level'] == lv and e['log_sha'] is not None,"),
    ('u_b40', "        if rt == B40_TAG:\n", "        if False:\n"),
    ('u_sky_ctrl', "'not made' if ce is None else ('STOP' if control_state(ce)[0] else 'PASS')))",
     "'not made' if ce is None else 'PASS'))"),
    ('u_sky_line', "            if line.startswith('WARMUP VERDICT'):\n", "            if 'VERDICT' in line:\n"),
    ('u_asserts', "    aa = [t for t in made_e if any(ents[t]['asserts'][k] for k in ents[t]['asserts'])]\n", "    aa = made_e\n"),
    ('u_skipped', "    sk = [w for _, w, _ in PAIRS if ents.get(w) is None and skipped(w, root)]\n", "    sk = []\n"),
    ('u_tagline', "        elif FORM146 and skipped(t, root):\n", "        elif False:\n"),
    ('u_call', "    if FORM146:\n        out.extend(summary146(root, ents, sheet, sheet_tags))\n", ''),
    ('u_census', "    if FORM146:\n        out.append('CENSUS = the V tags %s..%s, COLD first entries of never-entered levels on dac02fb9",
     "    if False:\n        out.append('CENSUS = the V tags %s..%s, COLD first entries of never-entered levels on dac02fb9"),
    # prints and the tile reader
    ('f_call', "    if FORM146:\n        o.extend(fmt146(r))\n", ''),
    ('f_dual_word', "'present' if r['dual_ok'] else 'ABSENT',", "'present',"),
    ('f_var', "                     'pass' if r['dual_ok'] else 'FAIL'))", "                     'pass'))"),
    ('f_tiles_t', "            return dict(video=m.group(1), sha=m.group(2), frames=int(m.group(3)), t4=int(m.group(4)), t12=int(m.group(5)),",
     "            return dict(video=m.group(1), sha=m.group(2), frames=int(m.group(3)), t4=int(m.group(5)), t12=int(m.group(4)),"),
    ('f_tiles_none', "    if not os.path.isfile(p):\n        return None\n    for line in open(p, 'r', encoding='ascii', errors='replace'):",
     "    if not os.path.isfile(p):\n        return dict(video='', sha='', frames=0, t4=0, t12=0, events='')\n    for line in open(p, 'r', encoding='ascii', errors='replace'):"),
    ('f_reg_note', "        ' - != 0: a row of the close in register F' if any(a[k] for k in a) else ''))",
     "        ''))"),
]
OK = True
for name, a, b in NEW + [(k,) + v for k, v in REANCHOR.items()]:
    n = t.count(a)
    if n != 1:
        print('ANCHOR %s occurs %d times' % (name, n))
        OK = False
    if a == b:
        print('IDENTICAL %s' % name)
        OK = False
names = [m[0] for m in M.MUTANTS] + [m[0] for m in NEW]
if len(set(names)) != len(names):
    print('DUPLICATE NAMES', [x for x in set(names) if names.count(x) > 1])
    OK = False
if not OK:
    sys.exit(1)
carried = []
for name, a, b in M.MUTANTS:
    if name in REANCHOR:
        a, b = REANCHOR[name]
    if t.count(a) != 1:
        print('CARRIED ANCHOR %s occurs %d times' % (name, t.count(a)))
        sys.exit(1)
    carried.append((name, a, b))
src = open(OLD, encoding='ascii').read()
doc = src[src.index('"""') + 3:src.index('"""', 3)]
head = ('"""Session 146 step 0 (HPP-386; ROADMAP s122 item 309 (k), (l)(1)-(7)): mutants of sc146.py - each must be killed by\n'
        'test_sc146.py.  The %d mutants of mut_sc145.py (link 1b of s145) are carried; 10 anchors moved with the port (build_sha onto\n'
        'BUILD145, sk_pending, pr_level, pr_sha_none, n_ad_isw, n_bd_wtag, e_s4_stop, e_su_cold_off, l_seal_ref, ma_regress_rc onto\n'
        'the --regress144 branch - the same mutation on the new text), then %d mutants of the new terms of profile 146: the constants (build, root, chain, runs, seal, scorer,\n'
        'FORM146, the 15 levels, the re-check and B40 tags, the control, the order, V / W tags, census, seal names, markers), the scan\n'
        'of the stub / assert / DualSrcBlend lines, level_of, the admission of the W form on the shipment binary, the DualSrcBlend\n'
        'reading and the control letter, the tile rows, the stop-check source (json / log), the three-V rule over every V, the skip\n'
        'of item 309 (k)(1), the summary lines of 146 (RECHECK, B40, Sky Garden, DATA, SKIPPED, census header) and the prints.\n'
        'Not mutated (proofs): (1) the dual position "base + m.start()" -> "m.start()": equal while the log is one chunk (every\n'
        'fixture with a DualSrcBlend line is < 64 MB); (2) regress145 (its lines read the real logs of s145 - the evidence is\n'
        'step0/regress145.out.txt, not a fixture; the same for its branch of main); (3) the --skip-w usage test "a.skip_w not in W_TAGS or" (pair_v is None for every\n'
        'tag outside the pairs); (4) the print texts no fixture reads (the W FORM line of 146, the B40 wording); (5) the docstring.\n'
        'Run through the frozen mutlib v4.1 FULL (never --changed-from), ONE counted run (items 84, 85, 87 (b)(3), 165 (v)):\n'
        '    python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s146/sc146.py\n'
        '        --test C:/kyty/s146/test_sc146.py --mutants C:/kyty/s146/mut_sc146.py --control --no-memo --workers 12\n'
        '        --work-dir C:/kyty/s146/mutwork --cache-dir C:/kyty/s146/mutcache --out C:/kyty/s146/mut_sc146.txt\n'
        'Every anchor occurs exactly once in sc146.py (LF).  The carried header of mut_sc145.py:\n') % (len(carried), len(NEW))
out = [head + doc + '"""', 'MUTANTS = [']
for name, a, b in NEW[:31] + carried + NEW[31:]:
    out.append('    (%r, %r, %r),' % (name, a, b))
out.append(']')
txt = '\n'.join(out) + '\n'
if any(ord(c) > 127 for c in txt):
    print('NON-ASCII')
    sys.exit(1)
open(DST, 'wb').write(txt.encode('ascii'))
print('mk_mut146: carried %d (re-anchored %d) + new %d = %d mutants; %s sha256 %s' % (
    len(carried), len(REANCHOR), len(NEW), len(carried) + len(NEW), DST, hashlib.sha256(txt.encode('ascii')).hexdigest()))
print('ALL OK')
