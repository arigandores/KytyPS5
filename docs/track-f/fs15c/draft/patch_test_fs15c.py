"""FS15c (HPP-822): build test_fs15c_read.py (beside this file) from C:/kyty/f287/fs14c/test_fs14c_read.py (FS14c) by a fixed list of
replacements, each asserted to match exactly once (or the given count): FS15 / FS14 literals, the spec lines FixF20: mode= and the
FixF20Stat exit line after Event: quit, the env of fs15_z, the member counts and sets of item 730 (g)(3), new fixtures for every FixF20
member and row; the FS14c fixtures of members that are references at fs15_z are moved to reference checks.  LF, ASCII.
usage: python patch_test_fs15c.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
s = open('C:/kyty/f287/fs14c/test_fs14c_read.py', 'rb').read().replace(b'\r\n', b'\n').decode('ascii')


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:90])
    s = s.replace(old, new)


DOC_END = s.index('"""', 3) + 3
s = '''"""Fixtures of fs15c_read.py (Track F link FS15c, HPP-822; ROADMAP s122 item 730 (g)(3), item 732, 733): clean synthetic tags fs15_v /
fs15_w / fs15_z read ADMITTED / ALL YES; every admission member (env per tag: no KYTY_FIX_* at fs15_v / fs15_w, KYTY_FIX_F20 '0' exactly
and no other KYTY_FIX_* at fs15_z, no KYTY_TEST_* / KYTY_GAME_PATCH; KYTY_TEST_* key, 'ExitFatal:' and 'TestHidLoss:' lines) and every
member of each form flips the reading; the new members of item 730 (g)(3): FixF20: mode=<want> (opposite / absent / after GuestOut /
unparsable / second line / prefix / CR) at each tag; the FixF20Stat exit line after Event: quit (absent / before quit only / unparsable /
two lines - the last one / unmatched 1 / modules_bound != modules / rewritten 10 and 11) at fs15_v and fs15_w (rewritten only at fs15_v);
FixF20Stat: lines 0 at fs15_z (exit / periodic / unparsable each NO; other FixF20 lines - a row); the rows of the preparation screen,
'all pipelines created', the driver blob (cache_before.tsv / cache_after.tsv) and FixF20Stat (periodic, max unmatched) are not members;
the FS14c members kept (FixF24 / init / init_owner / FixF29 / FixF25 / FixF21 / FixB12 / FixB13 / LogAsync, edges 1 000 000 / 999 999,
hold 300 s / 120 s, hold_s 310 / 309.9, video 2 999 / 3 000, draws 99 / 100, Event: quit, '--- Fatal Error ---' before / after quit and
in stdout, wait_expired, pump_stop_expired, close_killed / close_rc; W: [Vulkan][E], limit line, [Vulkan][W] 0, DualSrcBlend,
VALIDATION_STOP); at fs15_z FixF24 / FixF29 / FixF25 / FixF21 / FixB12 are references; strict cp1250 output without PYTHONIOENCODING; the
last line is ALL OK.  Port of C:/kyty/f287/fs14c/test_fs14c_read.py (FS14c) by patch_test_fs15c.py.  Early-exit form (ok = True, ok &=
..., sys.exit(0 if ok else 1)).  ASCII only.  The reader is loaded in-process from argv[1] (default: fs15c_read.py beside this file); the
fixture directories live under BASE.
usage: python test_fs15c_read.py [<fs15c_read.py under test>]"""''' + s[DOC_END:]

rep("SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fs14c_read.py')",
    "SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fs15c_read.py')")
rep("BASE = Path(os.path.join(HERE, 'fx_fs14c'))", "BASE = Path(os.path.join(HERE, 'fx_fs15c'))")
rep("_spec = importlib.util.spec_from_file_location('fs14c_read_under_test', SRC)",
    "_spec = importlib.util.spec_from_file_location('fs15c_read_under_test', SRC)")
rep("print('suite test_fs14c_read.py sha256 %s target fs14c_read.py sha256 %s'", "print('suite test_fs15c_read.py sha256 %s target fs15c_read.py sha256 %s'")
rep("TB = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'   # literals, not the reader's constants\n"
    "FS13 = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'\n"
    "VERSION = b'KytyPS5-2026-09-15-6a2987a-1925-geb7e8b91'",
    "TB = 'bfac84bea0eaec8bf3dae6ab5f67cd480f26921829f64f4a8b467bd50e922d8c'   # literals, not the reader's constants\n"
    "INST = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'\n"
    "VERSION = b'KytyPS5-2026-09-15-6a2987a-1929-g6beb3b73'\n"
    "EXIT20 = 'FixF20Stat: when=exit calls=79 modules_bound=22 modules=22 sites=79 rewritten=79 unmatched=0'\n"
    "PREP = 'ShaderPreparation: startup wait finished in 2299 ms presents_other=0 presents_main=0'\n"
    "ALLP = 'PipelinePrecache: all pipelines created, 11190 ms'")
rep("        e.update(KYTY_FIX_F24='0', KYTY_FIX_F29='0')", "        e.update(KYTY_FIX_F20='0')")
rep("TAGS = {'v': 'fs14_v', 'w': 'fs14_w', 'z': 'fs14_z'}", "TAGS = {'v': 'fs15_v', 'w': 'fs15_w', 'z': 'fs15_z'}")
rep("""def F24(kind):
    return 'FixF24: mode=%d b24=1' % (0 if kind == 'z' else 1)


def F29(kind):
    return 'FixF29: mode=%d' % (0 if kind == 'z' else 1)""", """def F24(kind):
    return 'FixF24: mode=1 b24=1'


def F29(kind):
    return 'FixF29: mode=1'


def F20(kind):
    return 'FixF20: mode=%d' % (0 if kind == 'z' else 1)""")
rep("""    L = ['LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100', 'Fork build arigandores/KytyPS5 eb7e8b9',
         F21(kind), F25(kind), F24(kind)]
    if kind != 'z':
        L += [INIT, OWNER]
    L += [F29(kind), 'ShaderSeed""", """    L = ['LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100', 'Fork build arigandores/KytyPS5 6beb3b7',
         F21(kind), F25(kind), F24(kind), INIT, OWNER, F20(kind), 'PipelinePrecache: start recipes=3079', ALLP, PREP]
    L += [F29(kind), 'ShaderSeed""")
rep("""    L += ['Event: quit', 'shutdown line']""", """    L += ['Event: quit'] + ([EXIT20] if kind != 'z' else []) + ['shutdown line']""")
rep("""    side = dict(installed_before=FS13, installed_after=FS13, installed_sha=TB,""", """    side = dict(installed_before=INST, installed_after=INST, installed_sha=TB,""")
rep("""    return dict(lines=L, run=run, side=side, idx=(3200 if kind != 'w' else 0), stdout='stdout line\\n')""",
    """    tsv = dict(cache_before='_PipelineCache\\tblob.bin\\t1000\\tx\\nGLCache\\ta.bin\\t50\\ty\\n_ShaderCache\\tb.bin\\t7\\tz\\n',
               cache_after='_PipelineCache\\tblob.bin\\t8800\\tx\\nGLCache\\ta.bin\\t60\\ty\\n_ShaderCache\\tb.bin\\t7\\tz\\n')
    return dict(lines=L, run=run, side=side, idx=(3200 if kind != 'w' else 0), stdout='stdout line\\n', tsv=tsv)""")
rep("""    if s['stdout'] is not None:""", """    for k, v in (s.get('tsv') or {}).items():
        with open(os.path.join(d, k + '.tsv'), 'w', newline='\\n') as f:
            f.write(v)
    if s['stdout'] is not None:""")
s = s.replace("def read(s, tag='fs14_v'):", "def read(s, tag='fs15_v'):")
rep("""    ok &= check('clean %s reading says no verdict, FS14d' % k, 'no verdict' in r['reading'] and 'FS14d' in r['reading'])""",
    """    ok &= check('clean %s reading says no verdict, FS15d' % k, 'no verdict' in r['reading'] and 'FS15d' in r['reading'])""")
rep("""                and r['f29_rows']['accessed_stdout'] == 0 and r['f29_rows']['f29_mode_lines'] == [0 if k == 'z' else 1])""",
    """                and r['f29_rows']['accessed_stdout'] == 0 and r['f29_rows']['f29_mode_lines'] == [1])
    f2 = r['f20_rows']
    ok &= check('clean %s F20 rows: prep [2299], all pipelines created [11190], blob 1000 -> 8800, GLCache 50 -> 60, mode lines [want]' % k,
                f2['prep_ms'] == [2299] and f2['all_pipelines_created_ms'] == [11190] and f2['blob_pipelinecache_before'] == 1000
                and f2['blob_pipelinecache_after'] == 8800 and f2['glcache_before'] == 50 and f2['glcache_after'] == 60
                and f2['f20_mode_lines'] == [0 if k == 'z' else 1] and f2['precache_n'] == 2)
    ok &= check('clean %s FixF20Stat rows: lines %s, exit %s' % (k, f2['f20stat_lines'], f2['f20stat_exit']),
                (f2['f20stat_lines'] == 0 and f2['f20stat_exit'] is None) if k == 'z' else
                (f2['f20stat_lines'] == 1 and f2['f20stat_exit']['rewritten'] == 79 and f2['f20stat_max_unmatched'] == 0))""")
rep("""r = read(SP['v'], 'fs14_v')
ok &= check('members count v 20 / 5 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 20 and len(r['form_members']) == 5)""",
    """r = read(SP['v'], 'fs15_v')
ok &= check('members count v 25 / 5 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 25 and len(r['form_members']) == 5)
ok &= check('v letter carries FixF20 mode=1 and the four FixF20Stat exit members',
            all(in_letter(r, w) for w in ('FixF20: mode=1', 'FixF20Stat: when=exit line after Event: quit', 'FixF20Stat exit line: unmatched 0',
                                         'FixF20Stat exit line: modules_bound = modules', 'FixF20Stat exit line: rewritten >= 11')))""")
rep("""r = read(SP['w'], 'fs14_w')
ok &= check('members count w 8 / 6 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 8 and len(r['form_members']) == 6)
ok &= check('w letter carries FixF24 and FixF29, form carries FixF25 and FixF21',
            in_letter(r, 'FixF24: mode=1 b24=1') and in_letter(r, 'FixF29: mode=1') and in_form(r, 'FixF25: mode=1')
            and in_form(r, 'FixF21: mode=1') and not in_letter(r, 'FixF21') and not in_letter(r, 'FixF25'))
r = read(SP['z'], 'fs14_z')
ok &= check('members count z 7 / 0 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 7 and len(r['form_members']) == 0)
ok &= check('z letter carries FixF24 mode=0, other FixF24 0, FixF29 mode=0, other FixF29 0; not FixF25 / FixF21',
            in_letter(r, 'FixF24: mode=0 b24=1') and in_letter(r, 'other FixF24: lines 0') and in_letter(r, 'FixF29: mode=0')
            and in_letter(r, 'other FixF29: lines 0') and not in_letter(r, 'FixF25') and not in_letter(r, 'FixF21')
            and not any('wait_expired' in a for a, x in r['members']))
for tg in ('fs14_v_r1', 'fs14_w_r3', 'fs14_z_r2'):
    ok &= check('tag form %s' % tg, R.TAG_RX.match(tg) is not None)
ok &= check('v spec read as fs14_z -> NOT ADMITTED (env, hold option)', read(SP['v'], 'fs14_z')['status'] == 'NOT_ADMITTED')
ok &= check('z spec read as fs14_v -> NOT ADMITTED', read(SP['z'], 'fs14_v')['status'] == 'NOT_ADMITTED')""",
    """r = read(SP['w'], 'fs15_w')
ok &= check('members count w 11 / 7 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 11 and len(r['form_members']) == 7)
ok &= check('w letter carries FixF20, FixF24 and three FixF20Stat exit members (no rewritten); form carries FixF29, FixF25, FixF21',
            in_letter(r, 'FixF20: mode=1') and in_letter(r, 'FixF24: mode=1 b24=1') and in_letter(r, 'FixF20Stat: when=exit line after')
            and in_letter(r, 'FixF20Stat exit line: unmatched 0') and in_letter(r, 'FixF20Stat exit line: modules_bound = modules')
            and not in_letter(r, 'FixF20Stat exit line: rewritten') and in_form(r, 'FixF29: mode=1') and in_form(r, 'FixF25: mode=1')
            and in_form(r, 'FixF21: mode=1') and not in_letter(r, 'FixF21') and not in_letter(r, 'FixF25') and not in_letter(r, 'FixF29'))
r = read(SP['z'], 'fs15_z')
ok &= check('members count z 5 / 0 (%d / %d)' % (len(r['members']), len(r['form_members'])), len(r['members']) == 5 and len(r['form_members']) == 0)
ok &= check('z letter carries FixF20 mode=0 and FixF20Stat lines 0; not FixF24 / FixF29 / FixF25 / FixF21',
            in_letter(r, 'FixF20: mode=0') and in_letter(r, '0 FixF20Stat: lines') and not in_letter(r, 'FixF24')
            and not in_letter(r, 'FixF29') and not in_letter(r, 'FixF25') and not in_letter(r, 'FixF21')
            and not any('wait_expired' in a for a, x in r['members']))
for tg in ('fs15_v_r1', 'fs15_w_r3', 'fs15_z_r2'):
    ok &= check('tag form %s' % tg, R.TAG_RX.match(tg) is not None)
ok &= check('v spec read as fs15_z -> NOT ADMITTED (env, hold option)', read(SP['v'], 'fs15_z')['status'] == 'NOT_ADMITTED')
ok &= check('z spec read as fs15_v -> NOT ADMITTED', read(SP['z'], 'fs15_v')['status'] == 'NOT_ADMITTED')""")
rep("""    for key, val in (('installed_before', TB), ('installed_after', 'x'), ('installed_sha', FS13), ('level', 'pot'),""",
    """    for key, val in (('installed_before', TB), ('installed_after', 'x'), ('installed_sha', INST), ('level', 'pot'),""")
rep("""    for key, val in (('binary_sha256', FS13), ('guest_args', '-lvl pot'), ('hold_s', 100)):""",
    """    for key, val in (('binary_sha256', INST), ('guest_args', '-lvl pot'), ('hold_s', 100)):""")
rep("""    if k == 'z':
        bads += [('KYTY_FIX_F24', '1'), ('KYTY_FIX_F24', ''), ('KYTY_FIX_F29', '1'), ('KYTY_FIX_F29', ''), ('KYTY_FIX_F20', '1')]
    else:
        bads += [('KYTY_FIX_F24', '1'), ('KYTY_FIX_F24', '0'), ('KYTY_FIX_F24', ''), ('KYTY_FIX_F29', '1'), ('KYTY_FIX_F29', '0'),
                 ('KYTY_FIX_F29', '')]""", """    bads += [('KYTY_FIX_F24', '1'), ('KYTY_FIX_F24', '0'), ('KYTY_FIX_F24', ''), ('KYTY_FIX_F29', '1'), ('KYTY_FIX_F29', '0'),
             ('KYTY_FIX_F29', '')]
    if k == 'z':
        bads += [('KYTY_FIX_F20', '1'), ('KYTY_FIX_F20', '')]
    else:
        bads += [('KYTY_FIX_F20', '1'), ('KYTY_FIX_F20', '0'), ('KYTY_FIX_F20', '')]""")
rep("""    if k == 'z':
        must += ['KYTY_FIX_F24', 'KYTY_FIX_F29']""", """    if k == 'z':
        must += ['KYTY_FIX_F20']""")
rep("""r = R.read_tag('fs14_v', R.paths('fs14_v', d))
ok &= check('no log -> NOT_ADMITTED, no members', r['status'] == 'NOT_ADMITTED' and r['members'] is None)
os.remove(os.path.join(d, 'es.json'))
ok &= check('no json -> NOT_ADMITTED', R.read_tag('fs14_v', R.paths('fs14_v', d))['status'] == 'NOT_ADMITTED')""",
    """r = R.read_tag('fs15_v', R.paths('fs15_v', d))
ok &= check('no log -> NOT_ADMITTED, no members', r['status'] == 'NOT_ADMITTED' and r['members'] is None)
os.remove(os.path.join(d, 'es.json'))
ok &= check('no json -> NOT_ADMITTED', R.read_tag('fs15_v', R.paths('fs15_v', d))['status'] == 'NOT_ADMITTED')""")
rep("""mode_suite('FixF24', 'vwz', F24, lambda k: 'FixF24: mode=%d b24=1' % (0 if k == 'z' else 1),
           lambda k: 'FixF24: mode=%d b24=1' % (1 if k == 'z' else 0),
           lambda k: ['FixF24: mode=%d b24=0' % (0 if k == 'z' else 1), 'FixF24: mode=%d' % (0 if k == 'z' else 1),
                      'FixF24: mode=10 b24=1', 'FixF24: mode=x b24=1'],
           lambda k: True)
mode_suite('FixF29', 'vwz', F29, lambda k: 'FixF29: mode=%d' % (0 if k == 'z' else 1), lambda k: 'FixF29: mode=%d' % (1 if k == 'z' else 0),
           lambda k: ['FixF29: mode=10', 'FixF29: mode=x'], lambda k: True)""",
    """mode_suite('FixF20', 'vwz', F20, lambda k: 'FixF20: mode=%d' % (0 if k == 'z' else 1), lambda k: 'FixF20: mode=%d' % (1 if k == 'z' else 0),
           lambda k: ['FixF20: mode=10', 'FixF20: mode=x'], lambda k: True)
mode_suite('FixF24', 'vw', F24, lambda k: 'FixF24: mode=1 b24=1', lambda k: 'FixF24: mode=0 b24=1',
           lambda k: ['FixF24: mode=1 b24=0', 'FixF24: mode=1', 'FixF24: mode=10 b24=1', 'FixF24: mode=x b24=1'],
           lambda k: True)
mode_suite('FixF29', 'vw', F29, lambda k: 'FixF29: mode=1', lambda k: 'FixF29: mode=0',
           lambda k: ['FixF29: mode=10', 'FixF29: mode=x'], lambda k: k == 'v')""")
rep("""# FixF24 / FixF29 at z: '0' lines ok; FixF25 / FixF21 at z are reference only
for alt in ('FixF25: mode=0', None, 'FixF25: mode=x'):
    r = read(repl(SP['z'], F25('z'), alt), 'fs14_z')""", """# FixF24 / FixF29 / FixF25 / FixF21 at z are reference only
for line, alts in ((F24('z'), ('FixF24: mode=0 b24=1', None, 'FixF24: mode=x b24=1')), (F29('z'), ('FixF29: mode=0', None, 'FixF29: mode=x'))):
    for alt in alts:
        r = read(repl(SP['z'], line, alt), 'fs15_z')
        ok &= check('z %r -> reference only, ALL YES' % alt, r['ok'] is True and r['status'] == 'ADMITTED')
for alt in ('FixF25: mode=0', None, 'FixF25: mode=x'):
    r = read(repl(SP['z'], F25('z'), alt), 'fs15_z')""")
rep("""    r = read(repl(SP['z'], F21('z'), alt), 'fs14_z')""", """    r = read(repl(SP['z'], F21('z'), alt), 'fs15_z')""")
rep("""r = read(after_quit(SP['w'], PX), 'fs14_w')""", """r = read(after_quit(SP['w'], PX), 'fs15_w')""")
rep("""# --- other FixF24 / FixF29 lines at fs14_z (each kind) -> NO; at v / w rows only ---
Z = SP['z']
for line in (INIT, OWNER, 'FixF24: init_owner hid=x', PX, 'FixF24: pump_update_long us=250000', 'FixF24: open failed instance=3 error="x"',
             'FixF24: add event index=0', 'FixF24: wait error "x"', 'FixF24: anything', 'FixF24: mode=x b24=1'):
    r = read(before_quit(Z, line), 'fs14_z')
    ok &= check('z %r -> other FixF24 NO' % line[:30], mem(r, 'other FixF24: lines 0') is False and r['ok'] is False)
for line in ('FixF29: overflow pass=1 area=0 count=1100 read=1023 total=1', 'FixF29: anything', 'FixF29: mode=x'):
    r = read(before_quit(Z, line), 'fs14_z')
    ok &= check('z %r -> other FixF29 NO' % line[:30], mem(r, 'other FixF29: lines 0') is False and r['ok'] is False)
r = read(before_quit(Z, 'Accessed non-GPU cached memory at 0x0000000000001000'), 'fs14_z')""",
    """# --- FixF20Stat lines at fs15_z (each kind) -> NO; other FixF24 / FixF29 / FixF20 lines at fs15_z -> rows only ---
Z = SP['z']
for line, where in ((EXIT20, 'after'), (EXIT20, 'before'), ('FixF20Stat: when=periodic calls=4096 modules_bound=9 modules=9 sites=9 '
                                                            'rewritten=9 unmatched=0', 'before'),
                    ('FixF20Stat: when=exit calls=x', 'after'), ('FixF20Stat:', 'after')):
    r = read((after_quit if where == 'after' else before_quit)(Z, line), 'fs15_z')
    ok &= check('z %r %s quit -> FixF20Stat lines 0 NO' % (line[:34], where), mem(r, '0 FixF20Stat: lines') is False and r['ok'] is False)
for line in (PX, 'FixF24: pump_update_long us=250000', 'FixF24: open failed instance=3 error="x"', 'FixF24: anything',
             'FixF29: overflow pass=1 area=0 count=1100 read=1023 total=1', 'FixF29: anything', 'FixF20: anything else',
             'FixF20 something'):
    r = read(before_quit(Z, line), 'fs15_z')
    ok &= check('z %r -> row only, ALL YES' % line[:30], r['ok'] is True and r['status'] == 'ADMITTED')
r = read(before_quit(Z, 'FixF20: anything else'), 'fs15_z')
ok &= check('z other FixF20 line -> row f20_other 1', r['f20_rows']['f20_other'] == 1)
r = read(before_quit(Z, 'Accessed non-GPU cached memory at 0x0000000000001000'), 'fs15_z')""")
rep("""    r = read(before_quit(Z, line), 'fs14_z')
    ok &= check('z %r -> row only, ALL YES' % line[:20], r['ok'] is True and r['f24_rows']['controller_lines'] == 1)""",
    """    r = read(before_quit(Z, line), 'fs15_z')
    ok &= check('z %r -> row only, ALL YES' % line[:20], r['ok'] is True and r['f24_rows']['controller_lines'] == 1)""")
rep("""# --- exit members of fs14_v (form fs13_v / b4_v); rows at fs14_z / fs14_w ---""",
    """# --- FixF20Stat exit members at fs15_v (4) and fs15_w (3) ---
for k in 'vw':
    S0 = SP[k]
    T0 = TAGS[k]
    FE = 'FixF20Stat: when=exit line after'
    r = read(repl(S0, EXIT20, None), T0)
    ok &= check('%s no exit line -> exit NO, unmatched NO, bound NO' % k, mem(r, FE) is False and mem(r, 'FixF20Stat exit line: unmatched') is False
                and mem(r, 'FixF20Stat exit line: modules_bound') is False and r['ok'] is False)
    if k == 'v':
        ok &= check('v no exit line -> rewritten NO', mem(r, 'FixF20Stat exit line: rewritten') is False)
    t = repl(S0, EXIT20, None)
    t = before_quit(t, EXIT20)
    r = read(t, T0)
    ok &= check('%s exit line only before Event: quit -> NO' % k, mem(r, FE) is False and r['ok'] is False)
    r = read(repl(S0, 'Event: quit', None), T0)
    ok &= check('%s no Event: quit -> exit line NO' % k, mem(r, FE) is False)
    for bad in ('FixF20Stat: when=exit calls=79 modules_bound=22 modules=22 sites=79 rewritten=79', EXIT20 + ' x',
                'FixF20Stat: when=exit calls=79 modules_bound=22 modules=22 sites=79 rewritten=x unmatched=0'):
        r = read(repl(S0, EXIT20, bad), T0)
        ok &= check('%s unparsable exit line %r -> NO, row unparsable 1' % (k, bad[-24:]), mem(r, FE) is False
                    and r['f20_rows']['f20stat_unparsable'] == 1)
    for alt, member, want in ((EXIT20.replace('unmatched=0', 'unmatched=1'), 'FixF20Stat exit line: unmatched', False),
                              (EXIT20.replace('modules_bound=22', 'modules_bound=21'), 'FixF20Stat exit line: modules_bound', False),
                              (EXIT20.replace('modules=22 ', 'modules=23 '), 'FixF20Stat exit line: modules_bound', False),
                              (EXIT20.replace('[', ''), FE, True)):
        r = read(repl(S0, EXIT20, alt), T0)
        ok &= check('%s exit line %r -> %s %s' % (k, alt[-46:], member, want), mem(r, member) is want and (r['ok'] is want))
    for rw, want in ((10, False), (11, True), (0, False)):
        r = read(repl(S0, EXIT20, EXIT20.replace('rewritten=79', 'rewritten=%d' % rw)), T0)
        if k == 'v':
            ok &= check('v rewritten %d -> %s' % (rw, want), mem(r, 'FixF20Stat exit line: rewritten') is want and r['ok'] is want)
        else:
            ok &= check('w rewritten %d -> no member, ALL YES' % rw, mem(r, 'FixF20Stat exit line: rewritten') is None and r['ok'] is True)
    t = copy.deepcopy(S0)
    t['lines'].insert(t['lines'].index('shutdown line'), EXIT20.replace('unmatched=0', 'unmatched=5'))
    r = read(t, T0)
    ok &= check('%s two exit lines after quit, the last unmatched 5 -> NO (the last governs)' % k,
                mem(r, 'FixF20Stat exit line: unmatched') is False)
    t = after_quit(S0, EXIT20.replace('unmatched=0', 'unmatched=5'))
    t['lines'].insert(t['lines'].index('shutdown line'), EXIT20)
    r = read(t, T0)
    ok &= check('%s two exit lines after quit, the last clean -> YES' % k, mem(r, 'FixF20Stat exit line: unmatched') is True and r['ok'] is True)
    r = read(before_quit(S0, 'FixF20Stat: when=periodic calls=4096 modules_bound=9 modules=10 sites=9 rewritten=9 unmatched=7'), T0)
    ok &= check('%s periodic line with unmatched 7 -> row only (max unmatched 7, periodic 1), ALL YES' % k,
                r['ok'] is True and r['f20_rows']['f20stat_max_unmatched'] == 7 and r['f20_rows']['f20stat_periodic'] == 1)
    r = read(before_quit(S0, 'FixF20: anything else'), T0)
    ok &= check('%s other FixF20 line -> row only, ALL YES' % k, r['ok'] is True and r['f20_rows']['f20_other'] == 1)
    rows = '\\n'.join(R.rows_out(read(S0, T0)))
    ok &= check('%s rows printed: preparation screen, all pipelines created, blob, FixF20Stat' % k,
                'ROW preparation screen (not a gate): ShaderPreparation ms [2299]; PipelinePrecache: all pipelines created ms [11190]' in rows
                and 'ROW driver blob (not a gate): _PipelineCache bytes before 1000 after 8800' in rows
                and 'ROW FixF20Stat (not a gate beyond the members): lines 1' in rows and 'ROW PipelinePrecache (not a gate): 2 lines' in rows)
t = copy.deepcopy(SP['v'])
t['tsv'] = {}
r = read(t)
ok &= check('v no cache tsv -> blob rows None, ALL YES', r['ok'] is True and r['f20_rows']['blob_pipelinecache_before'] is None
            and r['f20_rows']['blob_pipelinecache_after'] is None)
r = read(repl(repl(SP['v'], PREP, None), ALLP, None))
ok &= check('v no preparation lines -> rows [] and [], ALL YES', r['ok'] is True and r['f20_rows']['prep_ms'] == []
            and r['f20_rows']['all_pipelines_created_ms'] == [])

# --- exit members of fs15_v (form fs14_v / b4_v); rows at fs15_z / fs15_w ---""")
rep("""r = read(SP['w'], 'fs14_w')
ok &= check('w has no wait_expired member (letter)', mem(r, '0 FixF21: wait_expired') is None)""",
    """r = read(SP['w'], 'fs15_w')
ok &= check('w has no wait_expired member (letter)', mem(r, '0 FixF21: wait_expired') is None)""")
rep("""# --- members of fs14_v ---""", """# --- members of fs15_v ---""")
rep("""# --- members of fs14_z ---""", """# --- members of fs15_z ---""")
rep("""# --- members of fs14_w ---
S = SP['w']
W = 'fs14_w'""", """# --- members of fs15_w ---
S = SP['w']
W = 'fs15_w'""")
rep("""ok &= check('z FixB12 mode=0 -> reference only', read(repl(S, 'FixB12: mode=1', 'FixB12: mode=0'), 'fs14_z')['ok'] is True)""",
    """ok &= check('z FixB12 mode=0 -> reference only', read(repl(S, 'FixB12: mode=1', 'FixB12: mode=0'), 'fs15_z')['ok'] is True)
r = read(S, 'fs15_z')
ok &= check('z info carries FixF24 / FixF29 mode lines (reference)', r['info']['f24'][0][:2] == (1, 1) or r['info']['f24'][0][:2] == [1, 1])""")
rep("""ok &= check('w FixF24: init absent -> no member (letter of fs14_w), ALL YES', r['ok'] is True and r['form_ok'] is True)""",
    """ok &= check('w FixF24: init absent -> no member (letter of fs15_w), ALL YES', r['ok'] is True and r['form_ok'] is True)""")
rep("""ok &= check('fork row', (r['ref']['fork_line'] or '').endswith('eb7e8b9'))""", """ok &= check('fork row', (r['ref']['fork_line'] or '').endswith('6beb3b7'))""")
rep("""os.makedirs(os.path.join(rd, 'fs14_v'))
json.dump(r, open(os.path.join(rd, 'fs14_v', 'read.json'), 'w'), default=list)
os.makedirs(os.path.join(rd, 'fs14_z'))
json.dump(read(SP['z'], 'fs14_z'), open(os.path.join(rd, 'fs14_z', 'read.json'), 'w'), default=list)
os.makedirs(os.path.join(rd, 'fs13_v'))
json.dump(r, open(os.path.join(rd, 'fs13_v', 'read.json'), 'w'), default=list)
tb = R.table(rd)
ok &= check('table rows (fs13_v dir ignored)', len(tb) == 4 and '| fs14_v | ADMITTED | 013e1974 | ALL YES | ALL YES | 0 / 0 / 0 | 0 / 0 | 0 / 0 | 0 | 4.1 |' in tb[2]
            and '| fs14_z | ADMITTED | 013e1974 | ALL YES | - | 0 / 0 / 0 | 0 / 0 | 0 / 0 | 0 | 4.1 |' in tb[3])""",
    """os.makedirs(os.path.join(rd, 'fs15_v'))
json.dump(r, open(os.path.join(rd, 'fs15_v', 'read.json'), 'w'), default=list)
os.makedirs(os.path.join(rd, 'fs15_z'))
json.dump(read(SP['z'], 'fs15_z'), open(os.path.join(rd, 'fs15_z', 'read.json'), 'w'), default=list)
os.makedirs(os.path.join(rd, 'fs14_v'))
json.dump(r, open(os.path.join(rd, 'fs14_v', 'read.json'), 'w'), default=list)
tb = R.table(rd)
ok &= check('table rows (fs14_v dir ignored)', len(tb) == 4
            and '| fs15_v | ADMITTED | bfac84be | ALL YES | ALL YES | 22/22/79/0 | [2299] | [11190] | 1000 / 8800 | 0 | 4.1 | 0 | 3200 |' in tb[2]
            and '| fs15_z | ADMITTED | bfac84be | ALL YES | - | - | [2299] | [11190] | 1000 / 8800 | 0 | 4.1 | 0 | 3200 |' in tb[3])""")
rep("""        rc_cp = R.main(['--dir', d, '--tag', 'fs14_v', '--json', js])""", """        rc_cp = R.main(['--dir', d, '--tag', 'fs15_v', '--json', js])""")
rep("""ok &= check('json carries the form, the exit row, f24 / f29 rows', json.load(open(js)).get('form') == 'fs14_v' and json.load(open(js))['exit']['close_rc'] == 0
            and 'f24_rows' in json.load(open(js)) and 'f29_rows' in json.load(open(js)))""",
    """ok &= check('json carries the form, the exit row, f24 / f29 / f20 rows', json.load(open(js)).get('form') == 'fs15_v' and json.load(open(js))['exit']['close_rc'] == 0
            and 'f24_rows' in json.load(open(js)) and 'f29_rows' in json.load(open(js)) and 'f20_rows' in json.load(open(js)))""")
rep("""for bad in ('fs13_v', 'f24_n1', 'fs14_x', 'fs14_v_r4', 'fs14_w_r0', ''):""", """for bad in ('fs14_v', 'f20_v', 'fs15_x', 'fs15_v_r4', 'fs15_w_r0', ''):""")
s = s.replace("read(SP[k], TAGS[k])", "read(SP[k], TAGS[k])")
s = s.replace("r = read(t, 'fs14_z')", "r = read(t, 'fs15_z')")
s = s.replace("read(t, 'fs14_z')", "read(t, 'fs15_z')")
s = s.replace("'fs14_z')", "'fs15_z')")
left = [w for w in ("'fs14_", 'FS13', 'FS14d', '013e1974ea8a', 'fs14c') if w in s.split('"""', 2)[2]]
# 013e1974 full sha is the INST literal - allowed once
assert s.split('"""', 2)[2].count('013e1974ea8a') == 1, 'INST literal'
left = [w for w in left if w != '013e1974ea8a']
for w in left:
    for i, l in enumerate(s.split(chr(10))):
        if w in l:
            print('LEFT', i + 1, l[:140])
assert not [w for w in left if w != "'fs14_"], left
assert all(ord(c) < 128 for c in s)
open(os.path.join(HERE, 'test_fs15c_read.py'), 'w', encoding='ascii', newline='\n').write(s)
print('test_fs15c_read.py written, %d lines' % s.count('\n'))
print('ALL OK')
