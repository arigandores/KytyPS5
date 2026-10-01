"""Session 144 step 0 (HPP-330): write C:/kyty/s144/mut_sc144.py - the 384 mutants of mut_sc143.py carried (25 anchors moved
by the port: the same mutation on the new text; the five regress142 mutants made unique by their function context and
copied for regress143), then the mutants of the new terms of profile 144.  Every anchor must occur exactly once in
sc144.py and every mutant must parse.  ASCII, LF."""
import ast
import sys

SC = 'C:/kyty/s144/sc144.py'
t = open(SC, 'rb').read().decode('ascii')
ns = {}
exec(compile(open('C:/kyty/s143/mut_sc143.py', 'rb').read().decode('ascii'), 'mut_sc143', 'exec'), ns)
OLD = ns['MUTANTS']

f142 = t[t.index('def regress142('):t.index('def regress143(')]
f143 = t[t.index('def regress143('):t.index('def calib():')]


def ctx(fun, head, o, n):
    i = fun.index(head)
    j = fun.index(o, i) + len(o)
    return fun[i:j], fun[i:j - len(o)] + n


REMAP = {
    'pred_path': ("PRED143 = 'C:/kyty/s143/pred/02_sc143.md'", "PRED143 = 'C:/kyty/s142/pred/02_sc143.md'"),
    'ad_pred_path': ("(pr.get('path') or '').replace('\\\\', '/') == (pred_path or PRED_PATH)", 'True'),
    'st_main_rc': ("('STOP ' + ','.join(tags)) if stop else 'not met'))\n        return 5 if stop else 0",
                   "('STOP ' + ','.join(tags)) if stop else 'not met'))\n        return 0"),
    'half': ('XSRC={}, XSHEET=(), HALF=5)\nREGRESS143_FILE', 'XSRC={}, XSHEET=(), HALF=4)\nREGRESS143_FILE'),
    'sh_only_v': ("r['sheet'] = sheet_state(root, tag, chain) if tag in V_TAGS else None",
                  "r['sheet'] = sheet_state(root, tag, chain) if tag in W_TAGS else None"),
    'lv_order': ("LEVELS143 = ('spring_punch_sky_aztec', 'booster_construction',",
                 "LEVELS143 = ('booster_construction', 'spring_punch_sky_aztec',"),
    'lv_last': ("'booster_magic_lamp',\n             'rocket_space_station')",
                "'booster_magic_lamp',\n             'rocket_space_station_x')"),
    'pairs_v_num': ("PAIRS143 = tuple(('v143_%02d' % (i + 1),", "PAIRS143 = tuple(('v143_%02d' % i,"),
    'census_w': ('CENSUS=tuple((v, lv) for v, _, lv in PAIRS143)', 'CENSUS=tuple((w, lv) for _, w, lv in PAIRS143)'),
    'seq_wv': ('SEQ=tuple(t for v, w, _ in PAIRS143 for t in (v, w))', 'SEQ=tuple(t for v, w, _ in PAIRS143 for t in (w, v))'),
    'wtags': ('W_TAGS=tuple(w for _, w, _ in PAIRS143)', 'W_TAGS=tuple(v for v, _, _ in PAIRS143)'),
    'root143': ("ROOT143 = 'C:/kyty/s143'", "ROOT143 = 'C:/kyty/s142'"),
    'chain143': ("PRED_PATH=PRED143, CHAIN='go143a',", "PRED_PATH=PRED143, CHAIN='go142a',"),
    'runs143': ("RUNS='runs143'", "RUNS='runs142'"),
    'scorer143': ("SCORER='sc143.py'", "SCORER='sc142.py'"),
    'sealed_sheet143': ("'gates_default.txt', 'sheet142.py',\n             'test_go143a.py'",
                        "'gates_default.txt',\n             'test_go143a.py'"),
    'bd_guest': ("admit=admit(tag, js, pred_sha, pred_path), guest_args=js.get('guest_args'))",
                 'admit=admit(tag, js, pred_sha, pred_path), guest_args=None)'),
    'su_sheet_tags': ("sh = 'viewed' if vt in XSHEET else (sheet if (sheet_tags is None or vt in sheet_tags) else None)",
                      "sh = 'viewed' if vt in XSHEET else sheet"),
    'ts_chain': ("rx = re.compile(r'%s %s enter_scene end rc \\S+ log_%s\\.txt sha256 ([0-9a-f]{64})' % (chain or CHAIN, tag, tag))",
                 "rx = re.compile(r'%s enter_scene end rc \\S+ log_%s\\.txt sha256 ([0-9a-f]{64})' % (tag, tag))"),
    'ts_off': ("r['times_log_sha'] = times_log_sha(root, tag, chain) if EXTRA else None", "r['times_log_sha'] = None"),
}
RG = ('rg_same', 'rg_crlf', 'rg_restore', 'rg_sheet', 'rg_adm')
out = []
moved = []
for name, o, n in OLD:
    if name in REMAP:
        o, n = REMAP[name]
        moved.append(name)
    elif name in RG:
        o2, n2 = ctx(f142, '    old = profile(P142)', o, n)
        out.append((name, o2, n2))
        o3, n3 = ctx(f143, '    old = profile(P143)', o, n)
        out.append(('rg3' + name[2:], o3, n3))
        moved.append(name)
        continue
    out.append((name, o, n))

NEW = [
    # constants of profile 144 (the cheap failures first)
    ('n_pred144', "PRED_PATH = 'C:/kyty/s144/pred/01_sc144.md'", "PRED_PATH = 'C:/kyty/s143/pred/01_sc144.md'"),
    ('n_root144', "ROOT = 'C:/kyty/s144'", "ROOT = 'C:/kyty/s143'"),
    ('n_chain144', "CHAIN = 'go144a'", "CHAIN = 'go143a'"),
    ('n_runs144', "RUNS = 'runs144'", "RUNS = 'runs143'"),
    ('n_scorer144', "SCORER = 'sc144.py'", "SCORER = 'sc143.py'"),
    ('n_form_off', 'FORM144 = True', 'FORM144 = False'),
    ('n_half6', 'HALF = 6\n', 'HALF = 5\n'),
    ('n_old_order', "('v143_09', 'booster_magic_lamp')", "('v143_07', 'booster_magic_lamp')"),
    ('n_old_last', "('v143_10', 'rocket_space_station'))", "('v143_10', 'rocket_space_station_x'))"),
    ('n_new_first', "NEW144 = ('rocket_hourglass', 'pot_treasure_cave',", "NEW144 = ('pot_treasure_cave', 'rocket_hourglass',"),
    ('n_new_last', "'enemy_gorilla',\n          'mini_giants_garden')", "'mini_giants_garden',\n          'enemy_gorilla')"),
    ('n_control_lv', "CONTROL = ('w144_00', SKY)", "CONTROL = ('w144_00', 'intro_next')"),
    ('n_control_tag', "CONTROL = ('w144_00', SKY)", "CONTROL = ('w144_99', SKY)"),
    ('n_pairs_w', "(v, 'w144_%02d' % (i + 1), lv)", "(v, 'w144_%02d' % i, lv)"),
    ('n_pairs_v', "('v144_%02d' % (i + 9), 'w144_%02d' % (i + 9), lv)", "('v144_%02d' % (i + 8), 'w144_%02d' % (i + 9), lv)"),
    ('n_census', 'CENSUS = tuple((v, lv) for v, _, lv in PAIRS[len(OLD143):])', 'CENSUS = tuple((v, lv) for v, _, lv in PAIRS)'),
    ('n_seq_ctrl', 'SEQ = (CONTROL[0],) + tuple', 'SEQ = () + tuple'),
    ('n_seq_order', 'for t in (v, w))\nV_TAGS', 'for t in (w, v))\nV_TAGS'),
    ('n_wtags_ctrl', 'W_TAGS = (CONTROL[0],) + tuple', 'W_TAGS = () + tuple'),
    ('n_vtags', 'V_TAGS = tuple(v for v, _, _ in PAIRS)\n', 'V_TAGS = tuple(v for v, _, _ in PAIRS[len(OLD143):])\n'),
    ('n_xsrc_chain', "XSRC = dict((v, dict(root=ROOT143, chain='go143a', pred=PRED143))",
     "XSRC = dict((v, dict(root=ROOT143, chain='go144a', pred=PRED143))"),
    ('n_xsrc_pred', "XSRC = dict((v, dict(root=ROOT143, chain='go143a', pred=PRED143))",
     "XSRC = dict((v, dict(root=ROOT143, chain='go143a', pred=PRED_PATH))"),
    ('n_xsheet', 'XSHEET = tuple(v for v, _ in OLD143)', 'XSHEET = ()'),
    ('n_sealed_api', "'step2/wait_one.sh', 'step2/apichk144.py', 'C:/kyty/s143/step2/times.txt'",
     "'step2/wait_one.sh', 'C:/kyty/s143/step2/times.txt'"),
    ('n_sealed_x', "'step2/apichk144.py', 'C:/kyty/s143/step2/times.txt', 'C:/kyty/s143/pred/02_sc143.md')",
     "'step2/apichk144.py')"),
    ('n_wstop_3', 'W_STOP_RUN = 2', 'W_STOP_RUN = 3'),
    ('n_wstop_1', 'W_STOP_RUN = 2', 'W_STOP_RUN = 1'),
    ('n_numw', "NUMW = {5: 'five', 6: 'six'}", "NUMW = {5: 'five'}"),
    ('n_p143_form', "SCORER='sc143.py', EXTRA=True, FORM144=False,", "SCORER='sc143.py', EXTRA=True, FORM144=True,"),
    ('n_p142_form', 'FORM144=False, LEVELS=tuple(lv for _, lv in CENSUS142)', 'FORM144=True, LEVELS=tuple(lv for _, lv in CENSUS142)'),
    ('n_p143_xsrc', 'SEALED_NAMES=SEALED143, CONTROL=None, XSRC={}, XSHEET=(), HALF=5)',
     'SEALED_NAMES=SEALED143, CONTROL=None, XSHEET=(), HALF=5)'),
    ('n_p142_ctrl', 'FORM144=False, LEVELS=tuple(lv for _, lv in CENSUS142), CONTROL=None,',
     'FORM144=False, LEVELS=tuple(lv for _, lv in CENSUS142),'),
    ('n_rg3_b33', "REGRESS143_B33 = ('v143_02', 'v143_07', 'v143_08', 'v143_09')", "REGRESS143_B33 = ('v143_02', 'v143_07', 'v143_08')"),
    ('n_rg3_file', "REGRESS143_FILE = 'C:/kyty/s143/step4/summary143_viewed.txt'",
     "REGRESS143_FILE = 'C:/kyty/s142/step4/summary143_viewed.txt'"),
    # markers and the scan
    ('n_m_guest', "M_GUEST = b'GuestOut'", "M_GUEST = b'GuestOut:x'"),
    ('n_m_pre', "M_PRECACHE = b'PipelinePrecache:'", "M_PRECACHE = b'PipelinePrecache::'"),
    ('n_rx_pre', "RX_PRECACHE = re.compile(rb'PipelinePrecache: \\d+ recipes ->')",
     "RX_PRECACHE = re.compile(rb'PipelinePrecache: \\d+ recipe ->')"),
    ('n_sc_pre', "res['precache'] += len(RX_PRECACHE.findall(whole))", "res['precache'] += 0"),
    ('n_sc_pre_any', "res['precache_any'] += whole.count(M_PRECACHE)", "res['precache_any'] += 0"),
    ('n_sc_guest_first', "            if res['guestout'] is None:\n                gi", "            if True:\n                gi"),
    ('n_sc_guest_off', "                    res['guestout'] = base + _line(whole, gi)[0]", '                    pass'),
    # admission
    ('n_ad_off', "    if FORM144:\n        pc = env.get('KYTY_PIPELINE_PRECACHE')", "    if False:\n        pc = env.get('KYTY_PIPELINE_PRECACHE')"),
    ('n_ad_w', "add('W form: KYTY_PIPELINE_PRECACHE=0 in the env (item 254 (e))', pc == '0', pc)",
     "add('W form: KYTY_PIPELINE_PRECACHE=0 in the env (item 254 (e))', True, pc)"),
    ('n_ad_w_val', "add('W form: KYTY_PIPELINE_PRECACHE=0 in the env (item 254 (e))', pc == '0', pc)",
     "add('W form: KYTY_PIPELINE_PRECACHE=0 in the env (item 254 (e))', pc is not None, pc)"),
    ('n_ad_v', "add('V shipped defaults: no KYTY_PIPELINE_PRECACHE in the env (item 254 (k)(2))', pc is None, pc)",
     "add('V shipped defaults: no KYTY_PIPELINE_PRECACHE in the env (item 254 (k)(2))', True, pc)"),
    ('n_ad_isw', "        if is_w:\n            add('W form:", "        if not is_w:\n            add('W form:"),
    ('n_ad_pp', "== (pred_path or PRED_PATH), (pr.get('sha256')", "== PRED_PATH, (pr.get('sha256')"),
    # build
    ('n_bd_off', "    if FORM144:\n        pl = log['precache']", "    if False:\n        pl = log['precache']"),
    ('n_bd_wl', "line in the log (item 254 (e))', pl == 0,", "line in the log (item 254 (e))', True,"),
    ('n_su_wstd', "wstd = [t for t in wm if (ents[t].get('precache') or {}).get('stdout')]", 'wstd = []'),
    ('n_bd_v', "pl is not None and pl >= 1, 'log %s' % pl", "True, 'log %s' % pl"),
    ('n_bd_v2', "pl is not None and pl >= 1, 'log %s' % pl", "pl is not None and pl >= 2, 'log %s' % pl"),
    ('n_bd_ps', "ps = std['precache'] if std is not None else 0", 'ps = 0'),
    ('n_bd_pl', "pl = log['precache'] if log is not None else None", "pl = log['precache'] if log is not None else 0"),
    ('n_bd_wtag', "        if tag in W_TAGS:\n            r['admit'].append(('W form:", "        if tag in V_TAGS:\n            r['admit'].append(('W form:"),
    ('n_bd_guest', "r['guestout'] = log['guestout'] if log is not None else None", "r['guestout'] = None"),
    ('n_bd_wkey', "        r['wkey'] = w_stop_key(r)", "        r['wkey'] = None"),
    ('n_bd_wkey_v', "    if FORM144 and tag in W_TAGS:\n        r['wkey']", "    if FORM144 and tag in V_TAGS:\n        r['wkey']"),
    ('n_bd_tls', "r['times_log_sha'] = times_log_sha(root, tag, chain) if EXTRA", "r['times_log_sha'] = times_log_sha(root, tag) if EXTRA"),
    ('n_bd_shc', "r['sheet'] = sheet_state(root, tag, chain) if tag in V_TAGS", "r['sheet'] = sheet_state(root, tag) if tag in V_TAGS"),
    ('n_sh_chain1', "sheet_%s\\.png sha256 ([0-9a-f]{64})' % (chain or CHAIN, tag, tag))", "sheet_%s\\.png sha256 ([0-9a-f]{64})' % (CHAIN, tag, tag))"),
    ('n_sh_chain2', '                        % (chain or CHAIN, tag, tag, tag))', '                        % (CHAIN, tag, tag, tag))'),
    # level_of, entry_of
    ('n_lv_ctrl', '    if CONTROL is not None and tag == CONTROL[0]:\n        return CONTROL[1]', '    if False:\n        return CONTROL[1]'),
    ('n_eo_x', '    x = XSRC.get(tag)\n', '    x = None\n'),
    ('n_eo_sha', '        pred_sha = sha_file(pred_path) if os.path.isfile(pred_path) else None\n', '        pass\n'),
    ('n_eo_root', "root, pred_path, chain = x['root'], x['pred'], x['chain']", "pred_path, chain = x['pred'], x['chain']"),
    ('n_eo_chain', "root, pred_path, chain = x['root'], x['pred'], x['chain']", "root, pred_path, chain = x['root'], x['pred'], None"),
    ('n_eo_build', 'return build(tag, lv, js, log, std, es, root, pred_sha, pred_path, chain)', 'return build(tag, lv, js, log, std, es, root, pred_sha)'),
    # w_stop_key
    ('n_wk_nolog', "    if not r['log_present']:\n        return None\n    g = r.get('guestout')", "    if False:\n        return None\n    g = r.get('guestout')"),
    ('n_wk_filter', "ms = [m for m in r['marks'] if g is None or (m['src'] == 'log' and m['pos'] < g)]", "ms = list(r['marks'])"),
    ('n_wk_lt', "(m['src'] == 'log' and m['pos'] < g)]", "(m['src'] == 'log' and m['pos'] > g)]"),
    ('n_wk_src', "(m['src'] == 'log' and m['pos'] < g)]", "(m['pos'] < g)]"),
    ('n_wk_first', "return '%s %s' % (ms[0]['cls'], ms[0]['kind'])", "return '%s %s' % (ms[-1]['cls'], ms[-1]['kind'])"),
    ('n_wk_cls', "return '%s %s' % (ms[0]['cls'], ms[0]['kind'])", "return '%s %s' % (ms[0]['kind'], ms[0]['kind'])"),
    ('n_wk_exit_g', "    if g is None and (r['ended'] or r['exited']):", "    if (r['ended'] or r['exited']):"),
    ('n_wk_exit', "    if g is None and (r['ended'] or r['exited']):", "    if g is None and r['ended']:"),
    # stop_check_w
    ('n_sw_none', '        if key is None:\n            run = []\n            continue', '        if key is None:\n            continue'),
    ('n_sw_diff', '        if run and run[-1][1] != key:\n            run = []\n        run.append((tag, key))\n        if len(run) >= W_STOP_RUN:',
     '        run.append((tag, key))\n        if len(run) >= W_STOP_RUN:'),
    ('n_sw_ge', 'if len(run) >= W_STOP_RUN:', 'if len(run) > W_STOP_RUN:'),
    ('n_sw_tags', 'return True, [t for t, _ in run[-W_STOP_RUN:]]', 'return True, [t for t, _ in run[-1:]]'),
    # control_state
    ('n_cs_nojson', "            return True, False, [], ['attempt made without json (instrument)']",
     "            return False, False, [], ['attempt made without json (instrument)']"),
    ('n_cs_marks', "    if e['marks']:\n        letter.append", "    if False:\n        letter.append"),
    ('n_cs_ended', "    if e['ended'] or e['exited']:\n        letter.append", "    if False:\n        letter.append"),
    ('n_cs_vke', "    if e.get('vke'):\n        letter.append", "    if False:\n        letter.append"),
    ('n_cs_rows', "if x[0].startswith('W ')]", 'if False]'),
    ('n_cs_gate', 'return bool(letter) or bool(execu), bool(letter), letter, execu', 'return bool(letter), bool(letter), letter, execu'),
    ('n_cs_log', "    if not e['log_present']:\n        execu.append('log missing')", "    if False:\n        execu.append('log missing')"),
    # made, stop_check144
    ('n_made', "return os.path.isfile(os.path.join(root, '%s.json' % t)) or attempt_marker(t, root)",
     "return os.path.isfile(os.path.join(root, '%s.json' % t))"),
    ('n_s4_before', '    before = list(SEQ[:SEQ.index(tag)])', '    before = list(SEQ[:SEQ.index(tag) + 1])'),
    ('n_s4_ctrl_in', '    if c in before:\n        e = entry_of(c, root, pred_sha)', '    if False:\n        e = entry_of(c, root, pred_sha)'),
    ('n_s4_nojson', 'gate, let, lr, xr = control_state(e, e is None and attempt_marker(c, root))',
     'gate, let, lr, xr = control_state(e, False)'),
    ('n_s4_gate', '        stop = stop or gate\n', '        stop = stop\n'),
    ('n_s4_w', '    stop = stop or sw\n', '    stop = stop\n'),
    ('n_s4_v', '    stop = stop or sv\n', '    stop = stop\n'),
    ('n_s4_wwin', 'for t in ws[-W_STOP_RUN:]:', 'for t in ws[-1:]:'),
    ('n_s4_vwin', 'for t in vs[-STOP_RUN:]:', 'for t in vs[-2:]:'),
    ('n_s4_wtags', 'ws = [t for t in before if t in W_TAGS and made(t, root)]', 'ws = [t for t in before if made(t, root)]'),
    ('n_s4_census', 'vs = [t for t, _ in CENSUS if t in before and made(t, root)]', 'vs = [t for t in before if made(t, root)]'),
    # summary, fmt_entry, scene_ok, main
    ('n_su_xsrc', '    for t in XSRC:\n        ents[t] = entry_of(t, root, pred_sha)', '    for t in ():\n        ents[t] = entry_of(t, root, pred_sha)'),
    ('n_su_xsheet', "sh = 'viewed' if vt in XSHEET else (", "sh = 'viewed' if False else ("),
    ('n_su_ctrl', '    if FORM144:\n        c = CONTROL[0]', '    if False:\n        c = CONTROL[0]'),
    ('n_su_ctrl_nojs', 'gate, let, lr, xr = control_state(ents[c], c in nojs)', 'gate, let, lr, xr = control_state(ents[c], False)'),
    ('n_su_vbad', "vbad = [t for t in vm if not all(a[1] for a in ents[t]['admit'] if a[0].startswith(('V positive', 'V shipped')))]",
     'vbad = []'),
    ('n_su_wbad', "wbad = [t for t in wm if not all(a[1] for a in ents[t]['admit'] if a[0].startswith('W form'))]", 'wbad = []'),
    ('n_su_census_hdr', "    if FORM144:\n        out.append('CENSUS = the V tags", "    if False:\n        out.append('CENSUS = the V tags"),
    ('n_su_maprep', "e['level'], ' (repeated entry)' if FORM144 else '',", "e['level'], '',"),
    ('n_su_stopw', "    if FORM144:\n        keys = [(t, ents[t]['wkey']", "    if False:\n        keys = [(t, ents[t]['wkey']"),
    ('n_su_stopw_f', 'for k in keys if k[1] is not None) or', 'for k in keys) or'),
    ('n_fm_skip', "'distinct frame= ids, debt D-7; ' if FORM144 else ''", "''"),
    ('n_fm_pre', "    if FORM144:\n        pc = r.get('precache') or {}", "    if False:\n        pc = r.get('precache') or {}"),
    ('n_fm_wstop', "        if r['tag'] in W_TAGS:\n            o.append('  W stop", "        if False:\n            o.append('  W stop"),
    ('n_so_pair', "' of its own session; item 254 (e)' if FORM144", "'' if FORM144"),
    ('n_so_xsheet', "' (item 254 (a): viewed at the close of s143)' if vt in XSHEET else ''", "''"),
    ('n_mn_144', '        if FORM144:\n            stop, lines = stop_check144', '        if False:\n            stop, lines = stop_check144'),
    ('n_mn_rg3', '    if a.regress143:\n        ok, lines = regress143()', '    if False:\n        ok, lines = regress143()'),
    ('n_rg3_b33ok', 'b33ok = tuple(b33t) == REGRESS143_B33', 'b33ok = True'),
    ('n_rg3_ok', '    ok = same and b33ok\n', '    ok = same\n'),
]
out += NEW
names = [m[0] for m in out]
assert len(names) == len(set(names)), [n for n in names if names.count(n) > 1]
bad = 0
for name, o, n in out:
    c = t.count(o)
    if c != 1:
        print('ANCHOR %s count %d: %r' % (name, c, o[:120]))
        bad += 1
        continue
    try:
        ast.parse(t.replace(o, n, 1))
    except SyntaxError as e:
        print('SYNTAX %s: %s' % (name, e))
        bad += 1
    if o == n:
        print('SAME %s' % name)
        bad += 1
if bad:
    sys.exit(1)
HEAD = '''"""Session 144 step 0 (HPP-330; ROADMAP s122 item 254 (e), (k)(1)-(5)): mutants of sc144.py - each must be killed by
test_sc144.py.  The %d mutants of mut_sc143.py (link 1b of s143) are carried; %d anchors moved with the port (%s - the same
mutation on the new text; the five regress142 mutants are made unique by the text of their function from "old =
profile(P142)" and copied for regress143 as rg3_*), then %d mutants of the new terms of profile 144: the constants of the
33 tags, the pairs, the control, the other-session V (root, chain, seal, sheet), the seal names, the profiles 143 / 142,
the regression of profile 143; the W form markers and the scan (first GuestOut line, precache lines); the admission rows
of the W form and the V positive control; the stop key of a W stopped before the first GuestOut line; the two-W rule; the
control W (letter and gate); the made test and the windows of --stop-check; the summary lines (control, W FORM, census
header, repeated entry, stop W); the print lines (skipped draws by distinct frame=, the precache form, the W stop).
Not mutated, EQUIVALENT (proofs): (1) "res['guestout'] = base + _line(whole, gi)[0]" -> "base + gi": the two differ only
when a death marker sits on the same line as the first "GuestOut" text before it, and a marker's position is its line
start, so "m['pos'] < g" gives the same answer; (2) summary "nf, nl = HALF, len(CENSUS) - HALF" -> "nl = HALF": len(CENSUS)
= 2 * HALF in every profile (10 / 5, 12 / 6).  Run through the frozen mutlib v4.1 FULL (never --changed-from), ONE counted
run (items 84, 85, 87 (b)(3), 165 (v)):
    python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s144/sc144.py
        --test C:/kyty/s144/test_sc144.py --mutants C:/kyty/s144/mut_sc144.py --control --no-memo --workers 12
        --work-dir C:/kyty/s144/mutwork --cache-dir C:/kyty/s144/mutcache --out C:/kyty/s144/mut_sc144.txt
Every anchor occurs exactly once in sc144.py (LF).  The carried header of mut_sc143.py:
''' % (len(OLD), len(moved), ', '.join(moved), len(NEW))
old_doc = ast.get_docstring(ast.parse(open('C:/kyty/s143/mut_sc143.py', 'rb').read().decode('ascii')))
body = HEAD + old_doc.replace('"""', "'''") + '\n"""\nMUTANTS = [\n'
for m in out:
    body += '    %r,\n' % (m,)
body += ']\n'
body.encode('ascii')
open('C:/kyty/s144/mut_sc144.py', 'wb').write(body.encode('ascii'))
print('mut_sc144: %d mutants (%d carried, %d moved, %d rg3 copies, %d new)' % (
    len(out), len(OLD), len(moved), len(RG), len(NEW)))
