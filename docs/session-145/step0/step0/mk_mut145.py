"""Session 145 step 0 (HPP-350): build C:/kyty/s145/mut_sc145.py - the 506 mutants of C:/kyty/s144/mut_sc144.py carried (17
anchors moved with the port onto the text of profile 144 and the census header / map row / sheet note of sc145: the same
mutation on the new text), then the mutants of the new terms of profile 145.  Every anchor must occur exactly once in
sc145.py (checked here).  ASCII only, LF."""
import sys

src = open('C:/kyty/s144/mut_sc144.py', encoding='ascii').read()
ns = {}
exec(compile(src, 'mut_sc144', 'exec'), ns)
OLD = ns['MUTANTS']
SC = open('C:/kyty/s145/sc145.py', encoding='ascii').read()

REMAP = {
    'half': ("XSRC={}, XSHEET=(), HALF=5,\n            FORM145=False, REPEAT=True, XSHEET_NOTE='')\nREGRESS143_FILE",
             "XSRC={}, XSHEET=(), HALF=4,\n            FORM145=False, REPEAT=True, XSHEET_NOTE='')\nREGRESS143_FILE"),
    'n_pred144': ("P144 = dict(ROOT=ROOT144, PRED_PATH=PRED144,", "P144 = dict(ROOT=ROOT144, PRED_PATH=PRED143,"),
    'n_root144': ("P144 = dict(ROOT=ROOT144,", "P144 = dict(ROOT=ROOT143,"),
    'n_chain144': ("CHAIN='go144a', RUNS='runs144'", "CHAIN='go143a', RUNS='runs144'"),
    'n_runs144': ("RUNS='runs144', SCORER='sc144.py'", "RUNS='runs143', SCORER='sc144.py'"),
    'n_scorer144': ("SCORER='sc144.py', EXTRA=True, FORM144=True,", "SCORER='sc143.py', EXTRA=True, FORM144=True,"),
    'n_half6': ("XSHEET_NOTE=' (item 254 (a): viewed at the close of s143)', HALF=6)",
                "XSHEET_NOTE=' (item 254 (a): viewed at the close of s143)', HALF=5)"),
    'n_control_lv': ("CONTROL144 = ('w144_00', SKY)", "CONTROL144 = ('w144_00', 'intro_next')"),
    'n_control_tag': ("CONTROL144 = ('w144_00', SKY)", "CONTROL144 = ('w144_99', SKY)"),
    'n_census': ("CENSUS=tuple((v, lv) for v, _, lv in PAIRS144[len(OLD143):])",
                 "CENSUS=tuple((v, lv) for v, _, lv in PAIRS144)"),
    'n_xsrc_chain': ("XSRC=dict((v, dict(root=ROOT143, chain='go143a', pred=PRED143)) for v, _ in OLD143)",
                     "XSRC=dict((v, dict(root=ROOT143, chain='go144a', pred=PRED143)) for v, _ in OLD143)"),
    'n_xsrc_pred': ("XSRC=dict((v, dict(root=ROOT143, chain='go143a', pred=PRED143)) for v, _ in OLD143)",
                    "XSRC=dict((v, dict(root=ROOT143, chain='go143a', pred=PRED144)) for v, _ in OLD143)"),
    'n_xsheet': ("XSHEET=tuple(v for v, _ in OLD143), XSHEET_NOTE", "XSHEET=(), XSHEET_NOTE"),
    'n_p143_xsrc': ("SEALED_NAMES=SEALED143, CONTROL=None, XSRC={}, XSHEET=(), HALF=5,",
                    "SEALED_NAMES=SEALED143, CONTROL=None, XSHEET=(), HALF=5,"),
    'n_su_census_hdr': ("    if FORM144 and REPEAT:\n        out.append('CENSUS = the V tags",
                        "    if False:\n        out.append('CENSUS = the V tags"),
    'n_su_maprep': ("e['level'], ' (repeated entry)' if FORM144 and REPEAT else",
                    "e['level'], '' if FORM144 and REPEAT else"),
    'n_so_xsheet': ("        XSHEET_NOTE if vt in XSHEET else '')))", "        '' if vt in XSHEET else '')))"),
}

NEW = [
    # the constants of profile 145 (E1-E6)
    ('e_root', "ROOT = 'C:/kyty/s145'", "ROOT = 'C:/kyty/s144'"),
    ('e_pred', "PRED_PATH = 'C:/kyty/s145/pred/01_sc145.md'", "PRED_PATH = 'C:/kyty/s145/pred/01_sc144.md'"),
    ('e_chain', "CHAIN = 'go145a'", "CHAIN = 'go144a'"),
    ('e_runs', "RUNS = 'runs145'", "RUNS = 'runs144'"),
    ('e_scorer', "SCORER = 'sc145.py'", "SCORER = 'sc144.py'"),
    ('e_form145', 'FORM145 = True', 'FORM145 = False'),
    ('e_repeat', 'REPEAT = False', 'REPEAT = True'),
    ('e_lv_first', "NEW145 = ('small_pot_lava', 'spin_drill_natural_cave',", "NEW145 = ('spin_drill_natural_cave', 'small_pot_lava',"),
    ('e_lv_last', "'cymbal_party_land', 'enemy_final')", "'cymbal_party_land', 'enemy_finale')"),
    ('e_old144', "OLD144 = (('v144_09', 'rocket_hourglass'),)", "OLD144 = (('v144_10', 'rocket_hourglass'),)"),
    ('e_old144_lv', "OLD144 = (('v144_09', 'rocket_hourglass'),)", "OLD144 = (('v144_09', 'pot_treasure_cave'),)"),
    ('e_vkfilter', "VKFILTER = 'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering'",
     "VKFILTER = 'Undefined-Value-ShaderOutputNotConsumed'"),
    ('e_control', "CONTROL = ('w145_00', SKY)", "CONTROL = ('w145_01', SKY)"),
    ('e_control_lv', "CONTROL = ('w145_00', SKY)", "CONTROL = ('w145_00', 'intro_next')"),
    ('e_pairs_w', "PAIRS = tuple((v, 'w145_%02d' % (i + 1), lv) for i, (v, lv) in enumerate(OLD144))",
     "PAIRS = tuple((v, 'w145_%02d' % (i + 2), lv) for i, (v, lv) in enumerate(OLD144))"),
    ('e_pairs_v', "    ('v145_%02d' % (i + 2), 'w145_%02d' % (i + 2), lv) for i, lv in enumerate(NEW145))",
     "    ('v145_%02d' % (i + 3), 'w145_%02d' % (i + 2), lv) for i, lv in enumerate(NEW145))"),
    ('e_census', 'CENSUS = tuple((v, lv) for v, _, lv in PAIRS[len(OLD144):])', 'CENSUS = tuple((v, lv) for v, _, lv in PAIRS)'),
    ('e_seq_w', 'SEQ = (CONTROL[0],) + tuple(w for _, w, _ in PAIRS[:len(OLD144)]) + tuple(',
     'SEQ = (CONTROL[0],) + tuple(w for _, w, _ in PAIRS[:0]) + tuple('),
    ('e_root144', "ROOT144 = 'C:/kyty/s144'", "ROOT144 = 'C:/kyty/s143'"),
    ('e_pred144', "PRED144 = 'C:/kyty/s144/pred/01_sc144.md'", "PRED144 = 'C:/kyty/s144/pred/02_sc144.md'"),
    ('e_xsrc_chain', "XSRC = dict((v, dict(root=ROOT144, chain='go144a', pred=PRED144)) for v, _ in OLD144)",
     "XSRC = dict((v, dict(root=ROOT144, chain='go145a', pred=PRED144)) for v, _ in OLD144)"),
    ('e_xsrc_pred', "XSRC = dict((v, dict(root=ROOT144, chain='go144a', pred=PRED144)) for v, _ in OLD144)",
     "XSRC = dict((v, dict(root=ROOT144, chain='go144a', pred=PRED_PATH)) for v, _ in OLD144)"),
    ('e_xsheet', 'XSHEET = tuple(v for v, _ in OLD144)', 'XSHEET = ()'),
    ('e_xnote', "XSHEET_NOTE = ' (item 273 (a): viewed at the close of s144)'", "XSHEET_NOTE = ''"),
    ('e_sealed_gate', "'step2/pre_one.sh', 'step2/apichk145.py', 'step2/gate145.py', 'step2/test_gate145.py',",
     "'step2/pre_one.sh', 'step2/apichk145.py', 'step2/test_gate145.py',"),
    ('e_sealed_x', "                'C:/kyty/s144/step2/times.txt', 'C:/kyty/s144/pred/01_sc144.md')",
     "                'C:/kyty/s144/pred/01_sc144.md')"),
    ('e_half', 'HALF = 8\n', 'HALF = 7\n'),
    ('e_p144_form145', 'FORM145=False, REPEAT=True, LEVELS=tuple(lv for _, _, lv in PAIRS144)',
     'FORM145=True, REPEAT=True, LEVELS=tuple(lv for _, _, lv in PAIRS144)'),
    ('e_p144_repeat', 'FORM145=False, REPEAT=True, LEVELS=tuple(lv for _, _, lv in PAIRS144)',
     'FORM145=False, REPEAT=False, LEVELS=tuple(lv for _, _, lv in PAIRS144)'),
    ('e_p143_form145', "SEALED_NAMES=SEALED143, CONTROL=None, XSRC={}, XSHEET=(), HALF=5,\n            FORM145=False",
     "SEALED_NAMES=SEALED143, CONTROL=None, XSRC={}, XSHEET=(), HALF=5,\n            FORM145=True"),
    ('e_p142_form145', "CENSUS142), CONTROL=None, XSRC={}, XSHEET=(), HALF=5,\n            FORM145=False",
     "CENSUS142), CONTROL=None, XSRC={}, XSHEET=(), HALF=5,\n            FORM145=True"),
    ('e_rg_winev', "REGRESS144_WINEV = ('w144_09',)", "REGRESS144_WINEV = ('w144_10',)"),
    ('e_rg_limit', "REGRESS144_LIMIT = ('w144_02', 'w144_05',", "REGRESS144_LIMIT = ('w144_05',"),
    ('e_rg_file', "REGRESS144_FILE = 'C:/kyty/s144/step4/summary144_viewed.txt'",
     "REGRESS144_FILE = 'C:/kyty/s144/step2/summary144.txt'"),
    ('e_rg_vfile', "VCONT144_FILE = 'C:/kyty/KytyPS5/docs/session-144/audit/vidcont144.out.txt'",
     "VCONT144_FILE = 'C:/kyty/KytyPS5/docs/session-144/audit/vid144.out.txt'"),
    ('e_m_limit', "M_LIMIT = b'this will be the last time reporting it'", "M_LIMIT = b'the last time reporting'"),
    ('e_m_f6', "M_F6 = b'and this write is unused.'", "M_F6 = b'this write is unused'"),
    ('e_m_rec', "M_REC = b'Recovering Vulkan swapchain'", "M_REC = b'Recovering Vulkan'"),
    ('e_rx_win_b', "(minimized|restored|resized|size changed|lost keyboard focus)\\b')",
     "(minimized|restored|resized|size changed|lost keyboard focus)')"),
    ('e_rx_win_id', "RX_WIN = re.compile(rb'Window \\d+ (", "RX_WIN = re.compile(rb'Window .*?("),
    ('e_win_keys', "WIN_KEYS = ('minimized', 'restored', 'resized', 'size changed', 'lost keyboard focus')",
     "WIN_KEYS = ('minimized', 'resized', 'restored', 'size changed', 'lost keyboard focus')"),
    ('e_gap_up', 'VC_GAP = 0.060', 'VC_GAP = 0.061'),
    ('e_gap_down', 'VC_GAP = 0.060', 'VC_GAP = 0.059'),
    ('e_marg_up', 'VC_MARG = 0.012', 'VC_MARG = 0.013'),
    ('e_marg_down', 'VC_MARG = 0.012', 'VC_MARG = 0.011'),
    # the scan
    ('e_sc_rec', "            res['rec'] += whole.count(M_REC)\n", "            res['rec'] += 0\n"),
    ('e_sc_limit', "            res['limit'] += whole.count(M_LIMIT)\n", "            res['limit'] += 0\n"),
    ('e_sc_f6', "            res['f6'] += whole.count(M_F6)\n", "            res['f6'] += 0\n"),
    ('e_sc_win', "                res['win'][m.group(1).decode()] += 1\n", "                res['win'][m.group(1).decode()] += 2\n"),
    ('e_sc_vkt', "                if int(m.group(1)) & 2:\n", "                if int(m.group(1)) & 1:\n"),
    ('e_sc_vkt2', "                    res['vkval'] += 1\n", "                    res['vkval'] += 2\n"),
    # the admission of profile 145
    ('e_ad_off', "    if FORM145:\n        fl = env.get('VK_LAYER_MESSAGE_ID_FILTER')", "    if False:\n        fl = env.get('VK_LAYER_MESSAGE_ID_FILTER')"),
    ('e_ad_any', 'fl == VKFILTER, fl)', 'fl is not None, fl)'),
    ('e_ad_in', 'fl == VKFILTER, fl)', "VKFILTER in (fl or ''), fl)"),
    ('e_ad_start', 'fl == VKFILTER, fl)', "(fl or '').startswith(VKFILTER), fl)"),
    ('e_ad_v', "add('V shipped defaults: no VK_LAYER_MESSAGE_ID_FILTER in the env (item 273 (k)(2))', fl is None, fl)",
     "add('V shipped defaults: no VK_LAYER_MESSAGE_ID_FILTER in the env (item 273 (k)(2))', True, fl)"),
    ('e_ad_isw', "        if is_w:\n            add('W filter:", "        if not is_w:\n            add('W filter:"),
    # build
    ('e_bd_win_std', "r['win'] = dict((k, sum(sc['win'][k] for sc in (log, std) if sc is not None)) for k in WIN_KEYS)",
     "r['win'] = dict((k, sum(sc['win'][k] for sc in (log,) if sc is not None)) for k in WIN_KEYS)"),
    ('e_bd_rec_std', "r['win']['recovering'] = sum(sc['rec'] for sc in (log, std) if sc is not None)",
     "r['win']['recovering'] = sum(sc['rec'] for sc in (log,) if sc is not None)"),
    ('e_bd_ev_min', "r['winev'] = r['win']['minimized'] > 0 or r['win']['recovering'] > 0",
     "r['winev'] = r['win']['minimized'] > 0"),
    ('e_bd_ev_rec', "r['winev'] = r['win']['minimized'] > 0 or r['win']['recovering'] > 0",
     "r['winev'] = r['win']['recovering'] > 0"),
    ('e_bd_ev_and', "r['winev'] = r['win']['minimized'] > 0 or r['win']['recovering'] > 0",
     "r['winev'] = r['win']['minimized'] > 0 and r['win']['recovering'] > 0"),
    ('e_bd_lim_std', "r['limit'] = None if log is None else log['limit'] + (std['limit'] if std is not None else 0)",
     "r['limit'] = None if log is None else log['limit']"),
    ('e_bd_f6', "r['f6'] = sum(sc['f6'] for sc in (log, std) if sc is not None)", "r['f6'] = 0"),
    ('e_bd_vkval', "r['vkval'] = sum(sc['vkval'] for sc in (log, std) if sc is not None)", "r['vkval'] = 0"),
    ('e_bd_adm_off', "    if FORM145:\n        r['admit'].append(('window event:", "    if False:\n        r['admit'].append(('window event:"),
    ('e_bd_adm_true', "'(k)(3))', not r['winev'], 'minimized %d", "'(k)(3))', True, 'minimized %d"),
    ('e_bd_vc_w', "d['first'][0] if d['first'] is not None else None) if tag in V_TAGS else None",
     "d['first'][0] if d['first'] is not None else None) if tag in W_TAGS else None"),
    ('e_bd_vc_rows', "    r['vcont'] = vcont(log['rows'] if log is not None else [],", "    r['vcont'] = vcont([],"),
    # idx_times, vcont
    ('e_it_ge', "            if len(x) >= 3:\n                try:\n                    out.append(float(x[2]))",
     "            if len(x) >= 2:\n                try:\n                    out.append(float(x[2]))"),
    ('e_it_none', "    if not os.path.isfile(path):\n        return None\n    out = []\n", "    if not os.path.isfile(path):\n        return []\n    out = []\n"),
    ('e_vc_it', "    if not rows or not it or fn is None:\n        return None\n    ends = []",
     "    if not rows or fn is None:\n        return None\n    ends = []"),
    ('e_vc_fn', "    if not rows or not it or fn is None:\n        return None\n    ends = []",
     "    if not rows or not it:\n        return None\n    ends = []"),
    ('e_vc_anchor', '        ends.append(it[-1] - c)\n', '        ends.append(it[-1] + c)\n'),
    ('e_vc_anchor0', '        ends.append(it[-1] - c)\n', '        ends.append(it[0] - c)\n'),
    ('e_vc_unit', '        c += r[1] / 1e6\n', '        c += r[1] / 1e5\n'),
    ('e_vc_ge', '        if g > VC_GAP:\n', '        if g >= VC_GAP:\n'),
    ('e_vc_lo', 'lo = bisect.bisect_right(ends, it[i] + VC_MARG)', 'lo = bisect.bisect_right(ends, it[i] - VC_MARG)'),
    ('e_vc_hi', 'hi = bisect.bisect_left(ends, it[i + 1] - VC_MARG)', 'hi = bisect.bisect_left(ends, it[i + 1] + VC_MARG)'),
    ('e_vc_hilo', '            if hi > lo:\n                ns = ', '            if hi >= lo:\n                ns = '),
    ('e_vc_before', 'before += sum(1 for n in ns if n <= fn)', 'before += sum(1 for n in ns if n < fn)'),
    ('e_vc_after_if', '                if ns[-1] > fn:\n', '                if ns[-1] >= fn:\n'),
    ('e_vc_max', 'worst = max(after, key=lambda x: len(x[2])) if after else None', 'worst = min(after, key=lambda x: len(x[2])) if after else None'),
    ('e_vc_after_n', 'after=sum(sum(1 for n in ns if n > fn) for _, _, ns in after)', 'after=sum(sum(1 for n in ns if n >= fn) for _, _, ns in after)'),
    ('e_vc_gaps', 'gaps=len(after), before=before,', 'gaps=len(after) + before, before=before,'),
    ('e_vc_n0', 'longest=(len(worst[2]), worst[2][0], worst[2][-1], round(worst[1], 3), worst[0])',
     'longest=(len(worst[2]), worst[2][1], worst[2][-1], round(worst[1], 3), worst[0])'),
    ('e_vc_rec', 'longest=(len(worst[2]), worst[2][0], worst[2][-1], round(worst[1], 3), worst[0])',
     'longest=(len(worst[2]), worst[2][0], worst[2][-1], round(worst[1], 3), worst[0] + 1)'),
    # prints
    ('e_fv_run', "'%d rows n %d..%d (gap %.3f s after record %d)' % lg, vc['before']))",
     "'%d rows (gap %.3f s after record %d) n %d..%d' % lg, vc['before']))"),
    ('e_fw_keys', "            % tuple(w[k] for k in WIN_KEYS + ('recovering',)))", "            % tuple(w[k] for k in WIN_KEYS + ('minimized',)))"),
    ('e_cs_limit', "    if FORM145 and e.get('limit'):\n        letter.append", "    if False:\n        letter.append"),
    ('e_s4_off', "    if FORM145:\n        mt = [t for t in before if made(t, root)]", "    if False:\n        mt = [t for t in before if made(t, root)]"),
    ('e_s4_last', '        p = mt[-1] if mt else None\n', '        p = mt[0] if mt else None\n'),
    ('e_s4_ev', "        ev = e is not None and e['winev']\n", '        ev = False\n'),
    ('e_s4_stop', '        stop = stop or ev\n    return stop, lines\n', '        stop = stop\n    return stop, lines\n'),
    ('e_fe_off', "    if FORM145:\n        o.append('  window events", "    if False:\n        o.append('  window events"),
    ('e_fe_ctrl', "            ctrl = CONTROL is not None and r['tag'] == CONTROL[0]\n", '            ctrl = False\n'),
    ('e_fe_trunc', "' - LAYER TRUNCATED (the outcome stands by the letter)' if r['limit'] else ''",
     "' - LAYER TRUNCATED (the outcome stands by the letter)' if True else ''"),
    ('e_fe_wtag', "        if r['tag'] in W_TAGS:\n            ctrl = CONTROL", "        if r['tag'] in V_TAGS:\n            ctrl = CONTROL"),
    # the summary
    ('e_su_info_off', "        if FORM145:\n            out.append('  info video continuity of V", "        if False:\n            out.append('  info video continuity of V"),
    ('e_su_info_ev', "'yes' if v and v['winev'] else 'no', 'yes' if w and w['winev'] else 'no'))",
     "'no', 'yes' if w and w['winev'] else 'no'))"),
    ('e_su_new_off', "    if FORM145:\n        made_e = [t for t in tuple(SEQ) + tuple(XSRC)", "    if False:\n        made_e = [t for t in tuple(SEQ) + tuple(XSRC)"),
    ('e_su_ev', "        ev = [t for t in made_e if ents[t]['winev']]\n", '        ev = []\n'),
    ('e_su_oth', "any(ents[t]['win'][k] for k in WIN_KEYS[1:])]", "any(ents[t]['win'][k] for k in WIN_KEYS[2:])]"),
    ('e_su_lim', "lim = [t for t in wm if t != c and ents[t]['limit']]", "lim = [t for t in wm if ents[t]['limit']]"),
    ('e_su_lim_pass', "('PASS' if ce['limit'] == 0 else 'FAIL (a letter term of the '", "('PASS' if True else 'FAIL (a letter term of the '"),
    ('e_su_fbad', "fbad = [t for t in wm if not all(a[1] for a in ents[t]['admit'] if a[0].startswith('W filter'))]", 'fbad = []'),
    ('e_su_vfl', "vfl = [t for t in vm if not all(a[1] for a in ents[t]['admit'] if 'VK_LAYER_MESSAGE_ID_FILTER' in a[0])]", 'vfl = []'),
    ('e_su_vr', "              and ents[t]['vcont']['longest'][0] >= 2]", "              and ents[t]['vcont']['longest'][0] >= 4]"),
    ('e_su_cold_off', "    if FORM145:\n        out.append('CENSUS = the V tags %s..%s, COLD", "    if False:\n        out.append('CENSUS = the V tags %s..%s, COLD"),
    ('e_su_rep_and', "    if FORM144 and REPEAT:\n        out.append('CENSUS = the V tags %s..%s, REPEATED",
     "    if FORM144:\n        out.append('CENSUS = the V tags %s..%s, REPEATED"),
    ('e_su_maprep_and', "' (repeated entry)' if FORM144 and REPEAT else", "' (repeated entry)' if FORM144 else"),
    ('e_su_mapcold', "(' (cold first entry)' if FORM145 else '')", "''"),
    # the regression of profile 144 and the audit file
    ('e_rg_ok_vc', '    ok = same and win_ok and lim_ok and vc_ok\n', '    ok = same and win_ok and lim_ok\n'),
    ('e_rg_ok_win', '    ok = same and win_ok and lim_ok and vc_ok\n', '    ok = same and lim_ok and vc_ok\n'),
    ('e_rg_ok_lim', '    ok = same and win_ok and lim_ok and vc_ok\n', '    ok = same and win_ok and vc_ok\n'),
    ('e_rg_ok_same', '    ok = same and win_ok and lim_ok and vc_ok\n', '    ok = win_ok and lim_ok and vc_ok\n'),
    ('e_rg_win', '    win_ok = ev == REGRESS144_WINEV\n', '    win_ok = True\n'),
    ('e_rg_lim_ctrl', "    lim_ok = lim == REGRESS144_LIMIT and c0 is not None and c0['limit'] == 0\n", '    lim_ok = lim == REGRESS144_LIMIT\n'),
    ('e_rg_eq', '            eq = au is not None and mine == au\n', '            eq = True\n'),
    ('e_rg_va', '    va = vcont_audit(vexpect)\n', '    va = {}\n'),
    ('e_rg_mine', "vc['before'], vc['after'], vc['gaps'],", "vc['after'], vc['after'], vc['gaps'],"),
    ('e_rg_prof', "    old = profile(P144)\n    try:\n        pred_sha = sha_file(PRED_PATH) if os.path.isfile(PRED_PATH) else None\n"
     "        out, ents, _ = summary(ROOT, pred_sha, 'viewed')\n        tags = list(SEQ) + list(XSRC)",
     "    old = profile(P143)\n    try:\n        pred_sha = sha_file(PRED_PATH) if os.path.isfile(PRED_PATH) else None\n"
     "        out, ents, _ = summary(ROOT, pred_sha, 'viewed')\n        tags = list(SEQ) + list(XSRC)"),
    ('e_va_lg', 'int(m.group(9)), int(m.group(10)), int(m.group(11)))', 'int(m.group(9)), int(m.group(10)), 0)'),
    ('e_va_swap', 'out[(m.group(1), m.group(2))] = (m.group(3), int(m.group(4)), int(m.group(5)), int(m.group(6)), lg)',
     'out[(m.group(1), m.group(2))] = (m.group(3), int(m.group(5)), int(m.group(4)), int(m.group(6)), lg)'),
    ('e_mn_rg4', '    if a.regress144:\n        ok, lines = regress144()', '    if False:\n        ok, lines = regress144()'),
]

out = []
moved = []
for name, a, b in OLD:
    if name in REMAP:
        a, b = REMAP[name]
        moved.append(name)
    out.append((name, a, b))
assert sorted(moved) == sorted(REMAP), (sorted(moved), sorted(REMAP))
names = [m[0] for m in out] + [m[0] for m in NEW]
assert len(names) == len(set(names)), 'duplicate names'
out += NEW
bad = [(n, SC.count(a)) for n, a, b in out if SC.count(a) != 1]
same = [n for n, a, b in out if a == b]
if bad or same:
    print('BAD ANCHORS', bad, 'NO-OP', same)
    sys.exit(1)
HEAD = ('"""Session 145 step 0 (HPP-350; ROADMAP s122 item 273 (k)(1)-(5)): mutants of sc145.py - each must be killed by\n'
        'test_sc145.py.  The 506 mutants of mut_sc144.py (step 0 of s144) are carried; 17 anchors moved with the port (half,\n'
        'n_pred144, n_root144, n_chain144, n_runs144, n_scorer144, n_half6, n_control_lv, n_control_tag, n_census, n_xsrc_chain,\n'
        'n_xsrc_pred, n_xsheet, n_p143_xsrc - onto the text of the profile 144 dict P144 / P143; n_su_census_hdr, n_su_maprep,\n'
        'n_so_xsheet - onto the census header, the map row and the sheet note of sc145: the same mutation on the new text), then\n'
        '%d mutants of the new terms of profile 145: the constants of the 34 tags, the pairs, the control, the V of s144 (root,\n'
        'chain, seal, sheet note), the filter id, the seal names, the profiles 144 / 143 / 142 (FORM145, REPEAT), the regression\n'
        'constants; the scan of the window lines, the Recovering, limit and F6 lines and the validation type; the admission rows\n'
        'of the filter and of the window event; the video continuity (idx_times, vcont: anchor, unit, gap, margin, before /\n'
        'after, longest); the control letter of the layer limit; the stop rule of the window event; the prints; the summary\n'
        'lines (window events, layer limit, filter, continuity, cold census, map row); regress144 and vcont_audit; main.\n'
        'Not mutated, EQUIVALENT or not reachable by a fixture (proofs): (1) vcont "bisect.bisect_right" -> "bisect_left" and\n'
        '"bisect_left" -> "bisect_right": they differ only for a row end EXACTLY at it[i] + VC_MARG (or it[i + 1] - VC_MARG) in\n'
        'floating point, which the real streams (us dt, ms records) never give and no fixture can set exactly; (2) regress144\n'
        '"vc_n == nv and nv > 0": the profile 144 has 20 V (the fixtures use 1), a V-less profile 144 does not exist; (3) the\n'
        'text of the print lines no fixture reads; (4) the docstring.  Run through the frozen mutlib v4.1 FULL (never\n'
        '--changed-from), ONE counted run (items 84, 85, 87 (b)(3), 165 (v)):\n'
        '    python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s145/sc145.py\n'
        '        --test C:/kyty/s145/test_sc145.py --mutants C:/kyty/s145/mut_sc145.py --control --no-memo --workers 12\n'
        '        --work-dir C:/kyty/s145/mutwork --cache-dir C:/kyty/s145/mutcache --out C:/kyty/s145/mut_sc145.txt\n'
        'Every anchor occurs exactly once in sc145.py (LF).  The carried header of mut_sc144.py:\n' % len(NEW))
old_doc = src[src.index('"""') + 3:src.index('"""', 3)]
body = HEAD + old_doc.replace('"""', "'''") + '"""\nMUTANTS = [\n' + ''.join('    (%r, %r, %r),\n' % m for m in out) + ']\n'
body.encode('ascii')
open('C:/kyty/s145/mut_sc145.py', 'wb').write(body.encode('ascii'))
print('mut_sc145.py: %d mutants (%d carried, %d moved, %d new)' % (len(out), len(OLD), len(moved), len(NEW)))
