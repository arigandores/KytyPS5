"""Link 1b of s145 (HPP-379; ROADMAP s122 item 295 (z)): the mutants of the changed and new lines of sc145.py (in
mut_sc145.py) and of step2/gate145.py (a new file step2/mut_gate145.py); every anchor is checked to occur exactly once in
its target; prints the --only lists.  ASCII only.  python p1b_mut.py"""
import ast
import hashlib
import sys

SC = 'C:/kyty/s145/sc145.py'
MUT = 'C:/kyty/s145/mut_sc145.py'
GT = 'C:/kyty/s145/step2/gate145.py'
MUTG = 'C:/kyty/s145/step2/mut_gate145.py'

DROP = {'e_vkfilter': 'the constant VKFILTER is removed (item 295 (b))',
        'e_ad_any': 'the row "W filter:" is removed', 'e_ad_in': 'the row "W filter:" is removed',
        'e_ad_start': 'the row "W filter:" is removed', 'e_ad_isw': 'the row "W filter:" is removed',
        'e_su_fbad': 'the summary line W FILTER is replaced by W FORM 295'}
REANCHOR = {
    'e_pred': ("PRED_PATH = 'C:/kyty/s145/pred/03_sc145.md'", "PRED_PATH = 'C:/kyty/s145/pred/02_sc145.md'"),
    'e_sealed_x': ("                'C:/kyty/s144/step2/times.txt', 'C:/kyty/s144/pred/01_sc144.md',\n",
                   "                'C:/kyty/s144/pred/01_sc144.md',\n"),
    'e_bd_vc_w': ("d['first'][0] if d['first'] is not None else None) if tag in V_TAGS else None\n    r['vq']",
                  "d['first'][0] if d['first'] is not None else None) if tag in W_TAGS else None\n    r['vq']"),
    'e_rg_ok_vc': ('    ok = same and win_ok and lim_ok and vc_ok and nh_ok and all(m_ok)\n',
                   '    ok = same and win_ok and lim_ok and nh_ok and all(m_ok)\n'),
    'e_rg_ok_win': ('    ok = same and win_ok and lim_ok and vc_ok and nh_ok and all(m_ok)\n',
                    '    ok = same and lim_ok and vc_ok and nh_ok and all(m_ok)\n'),
    'e_rg_ok_lim': ('    ok = same and win_ok and lim_ok and vc_ok and nh_ok and all(m_ok)\n',
                    '    ok = same and win_ok and vc_ok and nh_ok and all(m_ok)\n'),
    'e_rg_ok_same': ('    ok = same and win_ok and lim_ok and vc_ok and nh_ok and all(m_ok)\n',
                     '    ok = win_ok and lim_ok and vc_ok and nh_ok and all(m_ok)\n'),
}
NEW = [
    ('l_wform', "W_FORM_LINE = 'W form: limit=100000000 filter=none'", "W_FORM_LINE = 'W form: limit=1000000 filter=none'"),
    ('l_lend', 'LAYER_END_US = 10000000\n', 'LAYER_END_US = 10000001\n'),
    ('l_near', 'WIN_NEAR_US = 2000000\n', 'WIN_NEAR_US = 1999999\n'),
    ('l_vqnear', 'VQ_NEAR = 0.008\n', 'VQ_NEAR = 0.011\n'),
    ('l_vqshift', 'VQ_SHIFT_MS = 50\n', 'VQ_SHIFT_MS = 2\n'),
    ('l_vqrows', 'VQ_ROWS = 600\n', 'VQ_ROWS = 10\n'),
    ('l_vqmark', 'VQ_MARK = 0.10\n', 'VQ_MARK = 0.20\n'),
    ('l_seal_ref', "                'C:/kyty/s144/runs144/cache_w144_20.after.json')\nSEALED144",
     "                'C:/kyty/s144/runs144/cache_w144_20.after.jsn')\nSEALED144"),
    ('l_nothld', "REGRESS144_NOTHELD = ('w144_09', 'w144_20')\n", "REGRESS144_NOTHELD = ('w144_09',)\n"),
    ('l_b3', 'REGRESS144_B3 = REGRESS144_LIMIT\n', 'REGRESS144_B3 = ()\n'),
    ('l_vkt2_we', "RX_VKT2 = re.compile(rb'\\[Vulkan\\]\\[[WE]\\]\\[2\\]')", "RX_VKT2 = re.compile(rb'\\[Vulkan\\]\\[\\w\\]\\[2\\]')"),
    ('l_vkt2_2', "RX_VKT2 = re.compile(rb'\\[Vulkan\\]\\[[WE]\\]\\[2\\]')", "RX_VKT2 = re.compile(rb'\\[Vulkan\\]\\[[WE]\\]\\[\\d+\\]')"),
    ('l_wall_moved', "(shown|hidden|exposed|moved to|resized", "(shown|hidden|exposed|resized"),
    ('l_wall_mouse', "got unknown event)\\b|Mouse (entered|left) window \\d+')", "got unknown event)\\b|Mouse (entered|left) window')"),
    ('l_wall_b', "got unknown event)\\b|Mouse", "got unknown event)|Mouse"),
    ('l_wall_list', "WIN_ALL = ('shown', 'hidden',", "WIN_ALL = ('hidden', 'shown',"),
    ('s_vk2_cnt', "                res['vk2'] += 1\n", "                res['vk2'] += 2\n"),
    ('s_vk2_last', "                res['vk2_last'] = base + m.start()\n", "                res['vk2_last'] = res['vk2_last'] or base + m.start()\n"),
    ('s_win_key', "k = m.group(1).decode() if m.group(1) else 'Mouse %s window' % m.group(2).decode()",
     "k = m.group(1).decode() if m.group(1) else 'Mouse entered window'"),
    ('s_winpos', "                res['winpos'].append((k, base + m.start()))\n", "                res['winpos'].append((k, base))\n"),
    ('v_shift', '    ends = [x + shift for x in ends]\n', '    ends = [x - shift for x in ends]\n'),
    ('n_le', '        if d <= VQ_NEAR:\n', '        if d < VQ_NEAR:\n'),
    ('n_k', 'd = min(abs(it[k] - e) if k < len(it) else 9.0, abs(it[k - 1] - e) if k > 0 else 9.0)',
     'd = min(abs(it[k] - e) if k < len(it) else 9.0, 9.0)'),
    ('n_k2', 'd = min(abs(it[k] - e) if k < len(it) else 9.0, abs(it[k - 1] - e) if k > 0 else 9.0)',
     'd = min(9.0, abs(it[k - 1] - e) if k > 0 else 9.0)'),
    ('q_none', "    if fi is None:\n        return None\n    base = []", "    if False:\n        return None\n    base = []"),
    ('q_anchor', "        base.append(it[-1] - c)\n", "        base.append(it[-1] - c + 0.004)\n"),
    ('q_range0', '    for s in range(-VQ_SHIFT_MS, VQ_SHIFT_MS + 1):\n', '    for s in range(0, VQ_SHIFT_MS + 1):\n'),
    ('q_tie_abs', "(n == best[1] and (abs(s) < abs(best[0]) or (abs(s) == abs(best[0]) and s < 0)))",
     "(n == best[1] and (abs(s) > abs(best[0]) or (abs(s) == abs(best[0]) and s < 0)))"),
    ('q_tie_neg', "(n == best[1] and (abs(s) < abs(best[0]) or (abs(s) == abs(best[0]) and s < 0)))",
     "(n == best[1] and (abs(s) < abs(best[0]) or (abs(s) == abs(best[0]) and s > 0)))"),
    ('q_gt', "        if best is None or n > best[1] or (n == best[1]", "        if best is None or n >= best[1] or (n == best[1]"),
    ('q_a0', "    a0 = vcont(rows, it, fn)['after']\n", "    a0 = vcont(rows, it, fn, best[0] / 1000.0)['after']\n"),
    ('q_ab', "    ab = vcont(rows, it, fn, best[0] / 1000.0)['after']\n", "    ab = vcont(rows, it, fn)['after']\n"),
    ('q_w', '    w = base[fi + 1:fi + 1 + VQ_ROWS]\n', '    w = base[fi:fi + VQ_ROWS]\n'),
    ('q_wf', '    wf = base[fi:fi + VQ_ROWS]\n', '    wf = base[fi + 1:fi + 1 + VQ_ROWS]\n'),
    ('q_near600', 'near600=near_count(w, it), n600f', 'near600=near_count(wf, it), n600f'),
    ('q_mark', '                mark=(abs(ab - a0) > VQ_MARK * a0) if a0 else ab > 0)',
     '                mark=(abs(ab - a0) >= VQ_MARK * a0) if a0 else ab > 0)'),
    ('q_mark0', '                mark=(abs(ab - a0) > VQ_MARK * a0) if a0 else ab > 0)',
     '                mark=(abs(ab - a0) > VQ_MARK * a0) if a0 else False)'),
    ('f_vq_mark', "' - [I] the counts differ by more than 10 %' if q['mark'] else ''", "''"),
    ('w_cum', '        c += r[1]\n        ends.append(c)\n', '        ends.append(c)\n        c += r[1]\n'),
    ('w_after_c', "    after = [i for i, r in enumerate(rows) if r[3] > epos and (cpos is None or r[3] < cpos)]\n",
     "    after = [i for i, r in enumerate(rows) if r[3] > epos]\n"),
    ('w_fi_draws', "        if rows[i][2] >= SCENE_DRAWS:\n            fi = j\n", "        if rows[i][2] >= SCENE_DRAWS - 1:\n            fi = j\n"),
    ('w_linetime', "        lines.append((k, ends[x - 1] if x > 0 else 0))\n", "        lines.append((k, ends[x] if x < len(ends) else 0))\n"),
    ('w_k3', '        if dt < K3_US:\n            continue\n', '        if dt <= K3_US:\n            continue\n'),
    ('w_off', '            off = t - lo if t < lo else (t - hi if t > hi else 0)\n',
     '            off = t - lo if t < lo else (t - hi if t > hi else 1)\n'),
    ('w_le', '            if abs(off) <= WIN_NEAR_US and', '            if abs(off) < WIN_NEAR_US and'),
    ('w_best', ' and (best is None or abs(off) < abs(best[1])):', ' and best is None:'),
    ('w_cls', "'K2' if dt >= K2_US else 'K3'", "'K2' if dt > K2_US else 'K3'"),
    ('w_place', "'entry' if j < ENTRY_WIN else 'hold', best))", "'entry' if j <= ENTRY_WIN else 'hold', best))"),
    ('fn_k3none', "    k3n = sum(1 for x in wn if x[2] == 'K3' and x[4] is None)\n", "    k3n = sum(1 for x in wn if x[4] is None)\n"),
    ('fn_empty', "        return 'no K2 / K3 frame after the first scene frame'\n", "        return ''\n"),
    ('f4_eq', "    return fm == W_FORM_LINE and 'VK_LAYER_MESSAGE_ID_FILTER' not in env, fm\n", "    return fm == W_FORM_LINE, fm\n"),
    ('f4_key', "    return fm == W_FORM_LINE and 'VK_LAYER_MESSAGE_ID_FILTER' not in env, fm\n",
     "    return 'VK_LAYER_MESSAGE_ID_FILTER' not in env, fm\n"),
    ('f4_none', "'none' if fl is None else fl)", "'none' if not fl else fl)"),
    ('h_log', "    if not r['log_present']:\n        return False, 'log missing'\n", "    if False:\n        return False, 'log missing'\n"),
    ('h_marks', "    if r['marks']:\n        return False, 'death marker %s'", "    if False:\n        return False, 'death marker %s'"),
    ('h_end', "    if r['ended'] or r['exited']:\n        return False, 'hold_exit / ENDED / exited'\n",
     "    if r['ended']:\n        return False, 'hold_exit / ENDED / exited'\n"),
    ('h_att', "    if r['attempt_outcome'] != 'ok':\n        return False, 'attempt outcome %s'",
     "    if False:\n        return False, 'attempt outcome %s'"),
    ('le_none', "    if lp is None or epos is None:\n        return None\n", "    if lp is None:\n        return None\n"),
    ('le_hold_c', "    hold = [r for r in sc['rows'] if r[3] > epos and (cpos is None or r[3] < cpos)]\n",
     "    hold = [r for r in sc['rows'] if r[3] > epos]\n"),
    ('le_empty', "    if not hold:\n        return None\n", "    if False:\n        return None\n"),
    ('le_gt', '    return sum(r[1] for r in hold if r[3] > lp)\n', '    return sum(r[1] for r in hold if r[3] < lp)\n'),
    ('wr_na', "        return [(name, True, 'n/a (W not held: %s)' % why) for name in W295]\n",
     "        return [(name, False, 'n/a (W not held: %s)' % why) for name in W295]\n"),
    ('wr_lim', "    return [(W295[0], r['limit'] == 0, r['limit'])", "    return [(W295[0], True, r['limit'])"),
    ('wr_vk2', "(W295[1], r['vk2'] >= 1, r['vk2'])", "(W295[1], r['vk2'] >= 0, r['vk2'])"),
    ('wr_le', "(W295[2], le is not None and le <= LAYER_END_US,", "(W295[2], le is not None and le < LAYER_END_US,"),
    ('wr_le_none', "(W295[2], le is not None and le <= LAYER_END_US,", "(W295[2], le is None or le <= LAYER_END_US,"),
    ('ad4', "                '295 (b)(4))' % W_FORM_LINE, f4, fm)", "                '295 (b)(4))' % W_FORM_LINE, True, fm)"),
    ('b_vk2', "    r['vk2'] = sum(sc['vk2'] for sc in (log, std) if sc is not None)\n",
     "    r['vk2'] = log['vk2'] if log is not None else 0\n"),
    ('b_winall', "    r['winall'] = dict((k, sum(sc['winall'][k] for sc in (log, std) if sc is not None)) for k in WIN_ALL)\n",
     "    r['winall'] = dict((k, log['winall'][k] if log is not None else 0) for k in WIN_ALL)\n"),
    ('b_winnear', "    r['winnear'] = win_near(log, d) if log is not None else []\n", "    r['winnear'] = []\n"),
    ('b_ext', "        if FORM145:\n            r['admit'].extend(w_form_rows(r))\n",
     "        if False:\n            r['admit'].extend(w_form_rows(r))\n"),
    ('b_form4', "    r['form4'] = w_form4(js.get('env') or {})\n", "    r['form4'] = (True, W_FORM_LINE)\n"),
    ('b_vq', "    r['vq'] = vquality(", "    r['vq'] = None and vquality("),
    ('b_le', "    r['layer_end'] = layer_end(log, d) if log is not None else None\n", "    r['layer_end'] = None\n"),
    ('fe_held', "'held' if r['held'][0] else 'NOT held (%s) - rows (1)-(3) n/a' % r['held'][1]", "'held'"),
    ('fe_vq', "            o.append('  video continuity alignment (item 295 (d); data, not a gate): %s' % fmt_vq(r['vq']))\n", ""),
    ('fe_win', "        o.append('  window lines by kind (item 295 (g); log and stdout; data): %s' % fmt_winall(r['winall']))\n", ""),
    ('su_fbad', "        fbad = [x for x in fbad if x[1]]\n", "        fbad = [x for x in fbad if not x[1]]\n"),
    ('su_fb5', "','.join(x[5:] for x in b)", "','.join(x for x in b)"),
    ('su_nh', "        nh = [t for t in wm if not ents[t]['held'][0]]\n", "        nh = []\n"),
    ('su_wk', "        wk = [t for t in made_e if any(ents[t]['winall'].values())]\n", "        wk = []\n"),
    ('su_nr', "        nr = [(t, x) for t in made_e for x in ents[t]['winnear'] if x[4] is not None]\n", "        nr = []\n"),
    ('su_vqm', "        vqm = [t for t in vm if ents[t]['vq'] is not None and ents[t]['vq']['mark']]\n", "        vqm = vm\n"),
    ('rg_res', "            res295[t] = [x[1] for x in rs] + [e['form4'][0]]\n", "            res295[t] = [x[1] for x in rs] + [True]\n"),
    ('rg_nh', "    nh = tuple(t for t in wt if not ents[t]['held'][0])\n", "    nh = ()\n"),
    ('rg_exp', "    exp = (REGRESS144_LIMIT, (), REGRESS144_B3, tuple(wt))\n", "    exp = (REGRESS144_LIMIT, (), REGRESS144_B3, ())\n"),
    ('rg_mok', '    ok = same and win_ok and lim_ok and vc_ok and nh_ok and all(m_ok)\n',
     '    ok = same and win_ok and lim_ok and vc_ok and nh_ok\n'),
    ('rg_nhok', '    ok = same and win_ok and lim_ok and vc_ok and nh_ok and all(m_ok)\n',
     '    ok = same and win_ok and lim_ok and vc_ok and all(m_ok)\n'),
    ('rg_wt', "    wt = [t for t in tags if t in res295]\n", "    wt = [t for t in tags if t in res295][:1]\n"),
]
NEWG = [
    ('g_pred', "PRED = ROOT + '/pred/03_sc145.md'", "PRED = ROOT + '/pred/02_sc145.md'"),
    ('g_refseal', "REF_SEAL = 'C:/kyty/s144/runs144/cache_w144_20.after.json'", "REF_SEAL = 'C:/kyty/s144/runs144/cache_w144_19.after.json'"),
    ('g_minfree', 'MIN_FREE = 60 * 2 ** 30', 'MIN_FREE = 60 * 10 ** 9'),
    ('g_disk', "DISK = 'C:/'", "DISK = 'D:/'"),
    ('g_rx', "re.findall(r'W 295(\\(b\\)\\(\\d\\))', s)", "re.findall(r'W 295(\\(b\\)\\(1\\))', s)"),
    ('g_wab_none', "    if not os.path.isfile(score):\n        return None\n    with open(score, 'r', encoding='utf-8', errors='replace') as f:\n        for line in f:\n            s = line.strip()\n            if s.startswith('admission:'):\n                return re.findall",
     "    if not os.path.isfile(score):\n        return []\n    with open(score, 'r', encoding='utf-8', errors='replace') as f:\n        for line in f:\n            s = line.strip()\n            if s.startswith('admission:'):\n                return re.findall"),
    ('g_wab_noline', "    return ['no admission line']\n\n\ndef made", "    return []\n\n\ndef made"),
    ('g_f4', '            if not f4[0]:\n', '            if False:\n'),
    ('g_f4_nojson', "                False, 'NO JSON')", "                True, 'NO JSON')"),
    ('g_wb_none', "            if wb is None:\n                bad.append('(v) W", "            if False:\n                bad.append('(v) W"),
    ('g_wb', '            elif wb:\n                bad.append(\'(v) W', '            elif False:\n                bad.append(\'(v) W'),
    ('g_ref_cmp', "    if got is None or got != want:\n        bad.append('(r)", "    if got is None:\n        bad.append('(r)"),
    ('g_ref_none', "    if got is None or got != want:\n        bad.append('(r)", "    if got != want:\n        bad.append('(r)"),
    ('g_free_cmp', '    if fr < MIN_FREE:\n', '    if fr <= MIN_FREE:\n'),
    ('g_early', "    if got is None:\n        det.append('(c)(1) not evaluable", "    if False:\n        det.append('(c)(1) not evaluable"),
]


def check(path, muts):
    src = open(path, 'rb').read().decode('utf-8')
    bad = [(n, src.count(o)) for n, o, _ in muts if src.count(o) != 1]
    same = [n for n, o, w in muts if o == w]
    return bad, same


def main():
    text = open(MUT, 'rb').read().decode('utf-8')
    assert '\r' not in text
    tree = ast.parse(text)
    lst = [n for n in tree.body if isinstance(n, ast.Assign) and n.targets[0].id == 'MUTANTS'][0].value
    old = [tuple(ast.literal_eval(e)) for e in lst.elts]
    names = [m[0] for m in old]
    for d in DROP:
        assert d in names, d
    for r in REANCHOR:
        assert r in names, r
    out = []
    for m in old:
        if m[0] in DROP:
            continue
        if m[0] in REANCHOR:
            m = (m[0],) + REANCHOR[m[0]]
        out.append(m)
    assert not set(n for n, _, _ in NEW) & set(names)
    out += NEW
    bad, same = check(SC, out)
    if bad or same:
        print('SC ANCHORS NOT UNIQUE: %s; OLD == NEW: %s' % (bad, same))
        sys.exit(1)
    badg, sameg = check(GT, NEWG)
    if badg or sameg:
        print('GATE ANCHORS NOT UNIQUE: %s; OLD == NEW: %s' % (badg, sameg))
        sys.exit(1)
    head = text[:text.index('MUTANTS = [')]
    assert text.rstrip().endswith(']')
    head = head.replace('"""Session 145 step 0 (HPP-350; ROADMAP s122 item 273 (k)(1)-(5)): mutants of sc145.py - each must be killed by\n',
                        '"""Session 145 step 0 (HPP-350; ROADMAP s122 item 273 (k)(1)-(5)) and link 1b (HPP-379, item 295): mutants of\n'
                        'sc145.py - each must be killed by test_sc145.py.  Link 1b: %d mutants dropped with their lines (%s), %d\n'
                        're-anchored on the changed lines (%s), %d new on the new lines of item 295 (the W form rows (b)(1)-(4), the\n'
                        'window kinds and the nearest window line, the alignment of the continuity, the summary and regress144 rows);\n'
                        'run --only over the re-anchored, the new and the carried mutants of the changed functions (item 295 (z)).\n'
                        'Step 0 text: mutants of sc145.py - each must be killed by\n' % (
                            len(DROP), ', '.join(sorted(DROP)), len(REANCHOR), ', '.join(sorted(REANCHOR)), len(NEW)), 1)
    assert 'Link 1b:' in head
    body = 'MUTANTS = [\n' + ''.join('    (%r, %r, %r),\n' % m for m in out) + ']\n'
    new = head + body
    open(MUT, 'wb').write(new.encode('ascii'))
    gh = ('"""Session 145 link 1b (HPP-379; ROADMAP s122 item 295 (v), (e), (z)): mutants of the changed and new lines of\n'
          'step2/gate145.py - each must be killed by step2/test_gate145.py (the suite loads the gate under test from argv[1]).\n'
          'Run through the frozen mutlib v4.1 with --control --no-memo --only over every mutant of this list (item 295 (z)):\n'
          '    python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s145/step2/gate145.py\n'
          '        --test C:/kyty/s145/step2/test_gate145.py --mutants C:/kyty/s145/step2/mut_gate145.py --control --no-memo\n'
          '        --workers 12 --work-dir C:/kyty/s145/mutwork_1bg --cache-dir C:/kyty/s145/mutcache_1bg\n'
          'Not mutated (the unchanged lines of step 0 / 0b; no mutant run of the gate existed before link 1b).  Every anchor\n'
          'occurs exactly once in gate145.py (LF).\n"""\n')
    gbody = 'MUTANTS = [\n' + ''.join('    (%r, %r, %r),\n' % m for m in NEWG) + ']\n'
    open(MUTG, 'wb').write((gh + gbody).encode('ascii'))
    carried = [n for n, _, _ in out if n.startswith(('e_vc_', 'e_bd_', 'e_su_', 'e_rg_', 'e_fe_', 'e_ad_', 'e_va_'))
               and n not in REANCHOR]
    only = sorted(set(list(REANCHOR) + [n for n, _, _ in NEW] + carried))
    print('mut_sc145.py: %d mutants (dropped %d, re-anchored %d, new %d); sha256 %s' % (
        len(out), len(DROP), len(REANCHOR), len(NEW), hashlib.sha256(new.encode('ascii')).hexdigest()))
    print('mut_gate145.py: %d mutants; sha256 %s' % (len(NEWG), hashlib.sha256((gh + gbody).encode('ascii')).hexdigest()))
    print('ONLY_SC %d %s' % (len(only), ','.join(only)))
    print('ONLY_GATE %d %s' % (len(NEWG), ','.join(n for n, _, _ in NEWG)))


main()
