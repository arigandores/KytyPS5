"""Link 1b (HPP-321): rebuilds C:/kyty/s143/mut_sc143.py - the 309 mutants of step 0 with 13 anchors moved by the edits of
item 242 (the same mutation on the new text, unique again), then the mutants of the new terms of link 1b.  Every anchor must
occur exactly once in sc143.py (LF) and differ from its replacement.  ASCII output."""
import ast
import hashlib

SC = 'C:/kyty/s143/sc143.py'
OUT = 'C:/kyty/s143/mut_sc143.py'
OLD = 'C:/kyty/s143/step1b/v0/mut_sc143.py'
t = open(SC, 'rb').read().decode('utf-8')
src = open(OLD, 'rb').read().decode('utf-8')
muts = None
for node in ast.parse(src).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'MUTANTS':
        muts = ast.literal_eval(node.value)
MOVED = {
    'pred_path': ("PRED_PATH = 'C:/kyty/s143/pred/02_sc143.md'", "PRED_PATH = 'C:/kyty/s142/pred/02_sc143.md'"),
    'der_k2_loc': ("        k2 = [(r[0], r[1], 'entry' if j < ENTRY_WIN else 'hold')",
                   "        k2 = [(r[0], r[1], 'entry' if j <= ENTRY_WIN else 'hold')"),
    'oc_hold_ge': ("        if d['dt_after_entry_us'] >= HOLD_CENSUS_US:", "        if d['dt_after_entry_us'] > HOLD_CENSUS_US:"),
    'oc_vx_exit': ("vx = one([m for m in ms if not m['at_exit']], [] if nodt else d['vx']['k2'])",
                   "vx = one(ms, [] if nodt else d['vx']['k2'])"),
    'sh_times': ("t_sheet = t_rec = None\n    tp = os.path.join(root, 'step2', 'times.txt')",
                 "t_sheet = t_rec = None\n    tp = os.path.join(root, 'times.txt')"),
    'oc_change_first': ("                return pre[0]['cls'], 'first death", "                return pre[-1]['cls'], 'first death"),
    'oc_hold_s_le': ("        if (r['hold_s'] or 0) < HOLD_CENSUS_S:", "        if (r['hold_s'] or 0) <= HOLD_CENSUS_S:"),
    'oc_reason_stable': ("            return 'NOT_EVALUABLE', 'no stable (%s)' % r['attempt_outcome']",
                         "            return 'NOT_EVALUABLE', 'no stable'"),
    'sealed_vid143': ("'test_fgcpu143.py', 'C:/kyty/scripts/s51_vidglitch.py',\n", "'test_fgcpu143.py',\n"),
    'sk_pair_tags': ("v['tag'] == vt and w['tag'] == wt and same(v) and same(w)", "True and same(v) and same(w)"),
    'sk_pair_vguest': ("and w['tag'] == wt and same(v) and same(w)", "and w['tag'] == wt and same(w)"),
    'sk_pair_wguest': ("same(v) and same(w),", "same(v),"),
    'su_b33_off': ("or 'none'))\n        b33, b33v, b33t = form_b33(adm)\n", "or 'none'))\n        b33, b33v, b33t = 0, 0, []\n"),
}
NEW = [
    # (d) the report of "--- Error ---" and the class VALIDATION_STOP
    ('rpt_build', "                if M_BUILD in line:\n                    break\n", ""),
    ('rpt_loc', "                if RX_LOC.search(line):\n                    break", "                if False:\n                    break"),
    ('rpt_lines_49', 'REPORT_LINES = 50', 'REPORT_LINES = 49'),
    ('rpt_lines_51', 'REPORT_LINES = 50', 'REPORT_LINES = 51'),
    ('rpt_title', "f.read(REPORT_BYTES).split(b'\\n')[1:REPORT_LINES + 1]", "f.read(REPORT_BYTES).split(b'\\n')[2:REPORT_LINES + 1]"),
    ('rpt_kind', "for kind, pos, _ in res['crash'] if kind == '--- Error ---'])", "for kind, pos, _ in res['crash'] if kind == '--- Fatal Error ---'])"),
    ('rpt_vke', "                if M_VKE in line:\n                    out.add(pos)", "                if M_VKANY in line:\n                    out.add(pos)"),
    ('vs_off', "        if EXTRA:\n            for m in r['marks']:", "        if False:\n            for m in r['marks']:"),
    ('vs_on', "        if EXTRA:\n            for m in r['marks']:", "        if True:\n            for m in r['marks']:"),
    ('vs_src', "src = log if m['src'] == 'log' else std", "src = log"),
    ('vs_cls', "                    m['cls'] = VSTOP", "                    m['cls'] = 'K1'"),
    ('vs_kind', "if m['kind'] == '--- Error ---' and m['pos'] in src.get('err_vk', ())", "if m['pos'] in src.get('err_vk', ())"),
    ('vs_const', "VSTOP = 'VALIDATION_STOP'", "VSTOP = 'VALIDATION'"),
    # (d) W without the dt rule
    ('nodt_off', "nodt = EXTRA and r['tag'] in W_TAGS", 'nodt = False'),
    ('nodt_all', "nodt = EXTRA and r['tag'] in W_TAGS", 'nodt = EXTRA'),
    ('nodt_v', "nodt = EXTRA and r['tag'] in W_TAGS", "nodt = EXTRA and r['tag'] in V_TAGS"),
    ('nodt_letter', "letter, reason = one(ms, [] if nodt else d['k2'])", "letter, reason = one(ms, d['k2'])"),
    ('nodt_vx', "[] if nodt else d['vx']['k2'])[0]", "d['vx']['k2'])[0]"),
    ('fe_winfo', "    if EXTRA and r['tag'] in W_TAGS:\n        o.append('  frames dt >= 1 s", "    if False:\n        o.append('  frames dt >= 1 s"),
    # (c) B5a variant 120 s, the outcome on 120 s
    ('o120_w', "r['outcome120'] = outcome120(r) if EXTRA and tag not in W_TAGS else None", "r['outcome120'] = outcome120(r) if EXTRA else None"),
    ('o120_142', "r['outcome120'] = outcome120(r) if EXTRA and tag not in W_TAGS else None", "r['outcome120'] = outcome120(r) if tag not in W_TAGS else None"),
    ('cut_set', "            out['cut120_pos'] = r[3]\n", ""),
    ('k2_120_within', "if r[1] >= K2_US and r[3] in within]", "if r[1] >= K2_US]"),
    ('k2_120_ge', "                     if r[1] >= K2_US and r[3] in within]", "                     if r[1] > K2_US and r[3] in within]"),
    ('k2_120_loc', "    out['k2_120'] = [(r[0], r[1], 'entry' if j < ENTRY_WIN else 'hold')", "    out['k2_120'] = [(r[0], r[1], 'entry' if j <= ENTRY_WIN else 'hold')"),
    ('o120_ent', "    if not d['entered']:\n        return 'NOT_ENTERED', 'no entry line'\n    cut", "    if False:\n        return 'NOT_ENTERED', 'no entry line'\n    cut"),
    ('o120_ms_all', "if cut is None or (m['src'] == 'log' and m['pos'] < cut)]", "if True]"),
    ('o120_ms_src', "if cut is None or (m['src'] == 'log' and m['pos'] < cut)]", "if cut is None or (m['pos'] < cut)]"),
    ('o120_cpos', "and (cut is None or d['change_pos'] < cut) else None", "and True else None"),
    ('o120_pre', "        pre = [m for m in ms if m['src'] == 'log' and m['pos'] < cpos]", "        pre = []"),
    ('o120_k2chg', "        if d['k2_120']:\n            return 'K2', 'frame dt >= 1 s before the scene change'", "        if False:\n            return 'K2', 'frame dt >= 1 s before the scene change'"),
    ('o120_marks', "    if ms:\n        return ms[0]['cls']", "    if False:\n        return ms[0]['cls']"),
    ('o120_ended', "    if r['exited'] or (cut is None and r['ended']):", "    if r['exited'] or r['ended']:"),
    ('o120_exited', "    if r['exited'] or (cut is None and r['ended']):", "    if (cut is None and r['ended']):"),
    ('o120_stall', "    if d['k2_120'] or (cut is None and r['tail_stall']):", "    if d['k2_120'] or r['tail_stall']:"),
    ('o120_k2', "    if d['k2_120'] or (cut is None and r['tail_stall']):", "    if (cut is None and r['tail_stall']):"),
    ('o120_first', "    if d['first'] is None:\n        return 'NOT_EVALUABLE', 'no first scene frame'", "    if False:\n        return 'NOT_EVALUABLE', 'no first scene frame'"),
    ('o120_stable', "    if r['attempt_outcome'] != 'ok':\n        return 'NOT_EVALUABLE', 'no stable (%s)'", "    if False:\n        return 'NOT_EVALUABLE', 'no stable (%s)'"),
    ('o120_hold_s', "    if (r['hold_s'] or 0) < HOLD_CENSUS_S:\n        return 'NOT_EVALUABLE', 'hold_s", "    if (r['hold_s'] or 0) <= HOLD_CENSUS_S:\n        return 'NOT_EVALUABLE', 'hold_s"),
    ('o120_hold_s_off', "    if (r['hold_s'] or 0) < HOLD_CENSUS_S:\n        return 'NOT_EVALUABLE', 'hold_s", "    if False:\n        return 'NOT_EVALUABLE', 'hold_s"),
    ('o120_held', "    if d['dt_after_entry_us'] >= HOLD_CENSUS_US:\n        return 'HOLDS_120'", "    if d['dt_after_entry_us'] > HOLD_CENSUS_US:\n        return 'HOLDS_120'"),
    ('f120_v120', "v120 = [e['tag'] for e in ents if e['derive']['k2_120']]", "v120 = [e['tag'] for e in ents if e['derive']['k2']]"),
    ('f120_entry', "k2e = [e['tag'] for e in ents if any(x[2] == 'entry'", "k2e = [e['tag'] for e in ents if any(x[2] == 'hold'"),
    ('f120_hold', "k2h = [e['tag'] for e in ents if any(x[2] == 'hold'", "k2h = [e['tag'] for e in ents if any(x[2] == 'entry'"),
    ('f120_late', "if e['derive']['k2'] and not e['derive']['k2_120']]", "if e['derive']['k2']]"),
    ('su_f120', "        v120, k2e, k2h, late = forms120(adm)", "        v120, k2e, k2h, late = forms120([])"),
    ('su_maprow', "            if EXTRA:\n                out.append('    map (A) row", "            if False:\n                out.append('    map (A) row"),
    ('fe_o120', "    if r.get('outcome120') is not None:\n        o.append('  K2 frames within 120 s", "    if False:\n        o.append('  K2 frames within 120 s"),
    # (e) the pair row
    ('pr_level', " and e['att_level'] == lv and e['log_sha'] is not None", " and e['log_sha'] is not None"),
    ('pr_sha', "\n                    and e['log_sha'] == e['times_log_sha'])", "\n                    and True)"),
    ('pr_sha_none', "e['att_level'] == lv and e['log_sha'] is not None\n", "e['att_level'] == lv\n"),
    ('pr_guest', "return (e is not None and e['guest_args'] == want and e['att_level']", "return (e is not None and e['att_level']"),
    ('ts_chain', "rx = re.compile(r'%s %s enter_scene end rc \\S+ log_%s\\.txt sha256 ([0-9a-f]{64})' % (CHAIN, tag, tag))", "rx = re.compile(r'%s enter_scene end rc \\S+ log_%s\\.txt sha256 ([0-9a-f]{64})' % (tag, tag))"),
    ('ts_last', "                got = m.group(1)\n", "                got = got or m.group(1)\n"),
    ('ts_off', "r['times_log_sha'] = times_log_sha(root, tag) if EXTRA else None", "r['times_log_sha'] = None"),
    ('ts_level', "r['att_level'] = at.get('level')", "r['att_level'] = None"),
    # (b) the cache continuity
    ('cc_off', "    if EXTRA:\n        made_tags = ", "    if False:\n        made_tags = "),
    ('cc_nobreak', "            brk = brk or m\n            continue", "            continue"),
    ('cc_changed_nobrk', "fmt_diff(dd)))\n            brk = brk or m", "fmt_diff(dd)))"),
    ('cc_first', "fmt_diff(dd)))\n            brk = brk or m", "fmt_diff(dd)))\n            brk = m"),
    ('cc_made', "        if n not in made or m not in made:\n            continue", "        if False:\n            continue"),
    ('cc_same', "        if all(x == (0, 0, 0, False) for x in dd.values()):", "        if True:"),
    ('cc_within', "        if a is not None and b is not None:\n            lines.append('  within", "        if False:\n            lines.append('  within"),
    ('cd_presence', "a['roots'].get(name) != b['roots'].get(name))", "False)"),
    ('cd_changed', "sum(1 for k in set(fa) & set(fb) if fa[k] != fb[k])", "0"),
    ('cd_swap', "out[name] = (len(set(fb) - set(fa)), len(set(fa) - set(fb)),", "out[name] = (len(set(fa) - set(fb)), len(set(fb) - set(fa)),"),
    ('cm_except', "    except (ValueError, KeyError, TypeError, IndexError):\n        return None\n    return dict(roots=roots", "    except (KeyError,):\n        return None\n    return dict(roots=roots"),
    ('cm_mtime', "(x[2], x[3], x[4])) for x in js['files'])", "(x[2], x[4], x[4])) for x in js['files'])"),
    ('cm_sha', "(x[2], x[3], x[4])) for x in js['files'])", "(x[2], x[3], x[3])) for x in js['files'])"),
    ('cm_present', "roots = dict((x[0], bool(x[2])) for x in js['roots'])", "roots = dict((x[0], bool(x[1])) for x in js['roots'])"),
    ('su_keep_le', "keep = [e for e in adm if SEQ.index(e['tag']) < SEQ.index(brk)]", "keep = [e for e in adm if SEQ.index(e['tag']) <= SEQ.index(brk)]"),
    ('su_keep_all', "keep = [e for e in adm if SEQ.index(e['tag']) < SEQ.index(brk)]", "keep = adm"),
    ('su_nobrk', "        if brk is None:\n            out.append('FORMS without", "        if True:\n            out.append('FORMS without"),
    # constants of the seal and the roots
    ('sealed_tools', "'cachemf143.py', 'lockcheck143.py', 'test_tools143.py', 'step2/next_one.sh', 'step2/call_one.sh',\n", "'step2/next_one.sh', 'step2/call_one.sh',\n"),
    ('cache_roots', "CACHE_ROOTS = ('shader', 'pipeline', 'glcache')", "CACHE_ROOTS = ('shader', 'glcache')"),
]
out = []
for name, old, new in muts:
    if name in MOVED:
        old, new = MOVED[name]
    out.append((name, old, new))
allm = out + NEW
bad = 0
names = set()
for name, old, new in allm:
    c = t.count(old)
    if c != 1 or old == new or name in names:
        bad += 1
        print('BAD %s count %d same %s dup %s' % (name, c, old == new, name in names))
    names.add(name)
print('mutants: %d (carried %d, of them moved %d; new %d); bad anchors %d' % (len(allm), len(out), len(MOVED), len(NEW), bad))
if bad:
    raise SystemExit(1)
i = src.index('MUTANTS = [')
j = src.index('\n]\n', i) + 3
head = src[:i]
HDR = ('"""Session 143 link 1b (HPP-321; ROADMAP s122 item 242 (b)-(e)): mutants of sc143.py - each must be killed by\n'
       'test_sc143.py.  The 309 mutants of step 0 are carried (13 anchors moved by the edits of item 242 - pred_path, der_k2_loc,\n'
       'oc_hold_ge, oc_vx_exit, sh_times, oc_change_first, oc_hold_s_le, oc_reason_stable, sealed_vid143, sk_pair_tags,\n'
       'sk_pair_vguest, sk_pair_wguest, su_b33_off: the same mutation on the new text), then the mutants of the new terms:\n'
       'the report of "--- Error ---" and VALIDATION_STOP, W without the dt rule, the outcome on 120 s and the B5a variant,\n'
       'the pair row by the json level and the log sha of times.txt, the cache continuity, the seal names and the roots.\n'
       'Not mutated, EQUIVALENT: outcome120 "m[\'pos\'] < cut" -> "<=" (a marker line and a FrameTrace row never share a\n'
       'position); the err_reports early return on no positions.\n'
       'Step 0 header (carried): ')
head = head.replace('"""Session 143 step 0 (HPP-297', HDR + 'Session 143 step 0 (HPP-297', 1)
body = 'MUTANTS = [\n' + ''.join('    (%r, %r, %r),\n' % m for m in allm) + ']\n'
text = head + body + src[j:]
open(OUT, 'wb').write(text.encode('ascii'))
print('written %s sha256 %s' % (OUT, hashlib.sha256(text.encode('ascii')).hexdigest()))
