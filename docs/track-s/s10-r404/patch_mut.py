"""Item 404 (g): the mutants of the domain identities and the prior seal in s9/mut_sc_s9.py, the fixture X9 in
s9/test_sc_s9.py (a skipped-draw line without frame=).  LF, write_bytes."""
import hashlib
import shutil
import sys

P = 'C:/kyty/s288/s9/mut_sc_s9.py'
b = open(P, 'rb').read()
if hashlib.sha256(b).hexdigest() != 'a3664f5a839f673389d87adf3bdd3153c0b6b56af333ce6d14f0eb8acfd1c849':
    sys.exit('mut_sc_s9.py changed - refuse')
shutil.copyfile(P, 'C:/kyty/s288/s10/r404/orig/mut_sc_s9.py')
t = b.decode('ascii')
A1 = """    ('pred', "PRED_PATH = 'C:/kyty/s288/pred/06b_s.md'", "PRED_PATH = 'C:/kyty/s288/pred/06_s.md'"),"""
assert t.count(A1) == 1
t = t.replace(A1, """    ('pred', "PRED_PATH = 'C:/kyty/s288/pred/07_s.md'", "PRED_PATH = 'C:/kyty/s288/pred/06b_s.md'"),""", 1)
NEW = r'''    # item 404 (g): T-1 / T-6 on the domain of an entered arm, the whole-log data row, the prior seal 06b of the five made arms
    ('id_none', "    if fi is None:\n        return ident\n    f0 = s['rows'][fi][0]", "    if True:\n        return ident\n    f0 = s['rows'][fi][0]"),
    ('id_f0', "    f0 = s['rows'][fi][0]\n", "    f0 = fi\n"),
    ('id_rows_gt', "for r in s['rows'] if r[0] >= f0]", "for r in s['rows'] if r[0] > f0]"),
    ('id_lines_gt', "if e[1] is not None and e[1] >= f0]", "if e[1] is not None and e[1] > f0]"),
    ('id_lines_none', "if e[1] is not None and e[1] >= f0]", "if e[1] >= f0]"),
    ('id_sk_k', "    sk = sum((t[0] or 0) for t in xs if t)\n    hi", "    sk = sum((t[1] or 0) for t in xs if t)\n    hi"),
    ('id_hi_k', "    hi = sum((t[1] or 0) for t in xs if t)\n    dom", "    hi = sum((t[0] or 0) for t in xs if t)\n    dom"),
    ('id_nof', "    nof = sum(1 for e in s['skips'] if e[1] is None)", "    nof = 0"),
    ('id_under_all', "    under = len(s['skips']) < A.SKIP_LINES_MAX", "    under = True"),
    ('id_under_dom', "    under = len(s['skips']) < A.SKIP_LINES_MAX", "    under = len(dom) < A.SKIP_LINES_MAX"),
    ('id_under_le', "    under = len(s['skips']) < A.SKIP_LINES_MAX", "    under = len(s['skips']) <= A.SKIP_LINES_MAX"),
    ('id_t1_eq', "(sk == len(dom)) if under else None", "(sk >= len(dom)) if under else None"),
    ('id_t6_eq', "(len(frames) == hi) if under else None", "(len(frames) <= hi) if under else None"),
    ('id_t1_name', "        if name.startswith('T-1 '):", "        if name.startswith('T-2 '):"),
    ('id_t6_name', "        elif name.startswith('T-6 '):", "        elif name.startswith('T-7 '):"),
    ('id_data_ok', "    out.append(('T-1 / T-6 whole log (data, item 404)', None,", "    out.append(('T-1 / T-6 whole log (data, item 404)', False,"),
    ('id_data_drop', "    out.append(('T-1 / T-6 whole log (data, item 404)', None, '; '.join(whole)))\n    return out",
     "    return out"),
    ('id_call', "    ident = ident_domain(ident, s, fi)                                     # item 404 (v)\n", ""),
    ('pr_tags', "    prior = spec['tag'] in PRIOR_TAGS and", "    prior = True and"),
    ('pr_tags_c5', "PRIOR_TAGS = ('pi_w1', 'pi_r1', 'pi_w0', 'pi_r0', 'c5_0')", "PRIOR_TAGS = ('pi_w1', 'pi_r1', 'pi_w0', 'pi_r0')"),
    ('pr_sha', "PRIOR_SHA = '605ebfa5", "PRIOR_SHA = '605ebfa6"),
    ('pr_path', "PRIOR_PATH = 'C:/kyty/s288/pred/06b_s.md'", "PRIOR_PATH = 'C:/kyty/s288/pred/06_s.md'"),
    ('pr_shachk', "pr.get('sha256') == PRIOR_SHA and", "True and"),
    ('pr_slash', "(pr.get('path') or '').replace('\\\\', '/') == PRIOR_PATH", "(pr.get('path') or '') == PRIOR_PATH"),
    ('pr_or', "        prior or pred_sha is not None", "        pred_sha is not None"),
'''
A2 = "    # seal and main\n"
assert t.count(A2) == 1
t = t.replace(A2, NEW + A2, 1)
A3 = "is `sys.exit(0 if ok else 1)`."
open(P, 'wb').write(t.encode('ascii'))
print('mut after', hashlib.sha256(t.encode('ascii')).hexdigest())

Q = 'C:/kyty/s288/s9/test_sc_s9.py'
u = open(Q, 'rb').read().decode('ascii')
X9 = r'''mkarm('c5_0', scene(S.L0, [(16000, dict(ev=C5_EV + [SKIP(8), SKIP(8), 'AsyncPipelines: skipped draw garbled'], skip=2,
                                        held=1))] + rows(10), header=HEADER_P0 + PRE_SKIP, pre_entry=PRE_ENTRY, first=FIRST_SK))
d9 = getter()('c5_0')
ok &= case('X9 item 404 (v): a skipped-draw line without frame= is not in the domain (frame= >= the first scene frame, by the '
           'letter) and is counted in the detail: T-1 on the domain 3 / 3 PASS (lines without frame= 1); the whole-log row 3 / 7',
           idrows(d9)[0] == (True, '3 / 3 (lines without frame= 1)') and idrows(d9)[1] == (True, '2 / 2') and
           idrows(d9)[2] == (None, 'T-1 3 / 7; T-6 4 / 2'))
'''
A4 = "SLM = S.A.SKIP_LINES_MAX\n"
assert u.count(A4) == 1
u = u.replace(A4, X9 + A4, 1)
open(Q, 'wb').write(u.encode('ascii'))
print('test after', hashlib.sha256(u.encode('ascii')).hexdigest())
