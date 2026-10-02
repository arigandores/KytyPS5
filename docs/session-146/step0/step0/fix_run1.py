"""fix_run1.py - session 146 step 0 (HPP-386; ROADMAP p.314(g)): the analysis of the 6 survivors of the counted full mutant run 1
(mut_sc146.txt 90ec012d...): extra143, n_form_off, e_form145, e_repeat, e_half mutate the module defaults EXTRA / FORM144 /
FORM145 / REPEAT / HALF, which the port shadowed by literal values in the dict P145 -> P145 now takes the defaults by name
(HALF after its definition); ma_regress_rc's anchor moved onto the new --regress145 branch of main (real logs only, no fixture)
-> re-anchored on the --regress144 branch (its place in sc145).  Edits port_sc146.py and mk_mut146.py (LF)."""
p = 'C:/kyty/s146/step0/port_sc146.py'
t = open(p, 'rb').read().decode('ascii')


def rep(old, new):
    global t
    assert t.count(old) == 1, old[:80]
    t = t.replace(old, new)


rep("""P145 = dict(ROOT=ROOT, PRED_PATH=PRED_PATH, CHAIN=CHAIN, RUNS=RUNS, SCORER=SCORER, EXTRA=True, FORM144=True, FORM145=True,
            FORM146=False, REPEAT=False, BUILD_SHA=BUILD145, RECHECK=(), LEVELS=LEVELS, PAIRS=PAIRS, CENSUS=CENSUS, SEQ=SEQ,
            V_TAGS=V_TAGS, W_TAGS=W_TAGS, SEALED_NAMES=SEALED_NAMES, CONTROL=CONTROL, XSRC=XSRC, XSHEET=XSHEET,
            XSHEET_NOTE=XSHEET_NOTE, HALF=8)""", """P145 = dict(ROOT=ROOT, PRED_PATH=PRED_PATH, CHAIN=CHAIN, RUNS=RUNS, SCORER=SCORER, EXTRA=EXTRA, FORM144=FORM144,
            FORM145=FORM145, FORM146=FORM146, REPEAT=REPEAT, BUILD_SHA=BUILD_SHA, RECHECK=RECHECK, LEVELS=LEVELS, PAIRS=PAIRS,
            CENSUS=CENSUS, SEQ=SEQ, V_TAGS=V_TAGS, W_TAGS=W_TAGS, SEALED_NAMES=SEALED_NAMES, CONTROL=CONTROL, XSRC=XSRC,
            XSHEET=XSHEET, XSHEET_NOTE=XSHEET_NOTE)""")
rep("""# ---- 3. markers of the new data rows""", """# HALF of profile 145 is the module default, set where it is defined
t = rep('''HALF = 8
''', '''HALF = 8
P145['HALF'] = HALF
''')

# ---- 3. markers of the new data rows""")
open(p, 'wb').write(t.encode('ascii'))
m = 'C:/kyty/s146/step0/mk_mut146.py'
t = open(m, 'rb').read().decode('ascii')
rep("""    ('g_p145_f146', "            FORM146=False, REPEAT=False, BUILD_SHA=BUILD145, RECHECK=(), LEVELS=LEVELS,",
     "            FORM146=True, REPEAT=False, BUILD_SHA=BUILD145, RECHECK=(), LEVELS=LEVELS,"),
    ('g_p145_build', "            FORM146=False, REPEAT=False, BUILD_SHA=BUILD145, RECHECK=(), LEVELS=LEVELS,",
     "            FORM146=False, REPEAT=False, BUILD_SHA=BUILD146, RECHECK=(), LEVELS=LEVELS,"),""",
    """    ('g_p145_f146', "            FORM145=FORM145, FORM146=FORM146, REPEAT=REPEAT,", "            FORM145=FORM145, FORM146=True, REPEAT=REPEAT,"),
    ('g_p145_build', "REPEAT=REPEAT, BUILD_SHA=BUILD_SHA, RECHECK=RECHECK,", "REPEAT=REPEAT, BUILD_SHA=BUILD146, RECHECK=RECHECK,"),
    ('g_p145_rck', "REPEAT=REPEAT, BUILD_SHA=BUILD_SHA, RECHECK=RECHECK,", "REPEAT=REPEAT, BUILD_SHA=BUILD_SHA, RECHECK=RECHECK146,"),
    ('g_f146_def', "FORM146 = False\\n", "FORM146 = True\\n"),
    ('g_half145', "P145['HALF'] = HALF\\n", "P145['HALF'] = 6\\n"),""")
rep("""    'l_seal_ref': (""", """    'ma_regress_rc': ("        ok, lines = regress144()\\n        print('\\\\n'.join(lines))\\n        return 0 if ok else 1\\n",
                      "        ok, lines = regress144()\\n        print('\\\\n'.join(lines))\\n        return 0\\n"),
    'l_seal_ref': (""")
rep("""'step0/regress145.out.txt, not a fixture); (3)""", """'step0/regress145.out.txt, not a fixture; the same for its branch of main); (3)""")
rep("""        'test_sc146.py.  The %d mutants of mut_sc145.py (link 1b of s145) are carried; 9 anchors moved with the port (build_sha onto\\n'
        'BUILD145, sk_pending, pr_level, pr_sha_none, n_ad_isw, n_bd_wtag, e_s4_stop, e_su_cold_off, l_seal_ref - the same mutation on\\n'
        'the new text), then""", """        'test_sc146.py.  The %d mutants of mut_sc145.py (link 1b of s145) are carried; 10 anchors moved with the port (build_sha onto\\n'
        'BUILD145, sk_pending, pr_level, pr_sha_none, n_ad_isw, n_bd_wtag, e_s4_stop, e_su_cold_off, l_seal_ref, ma_regress_rc onto\\n'
        'the --regress144 branch - the same mutation on the new text), then""")
open(m, 'wb').write(t.encode('ascii'))
print('ok')
