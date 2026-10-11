"""FS15c (HPP-822): build test_tools_fs15c.py (beside this file) from C:/kyty/f287/fs14c/test_tools_fs14c.py by a fixed list of
replacements (each asserted).  LF, ASCII.  usage: python patch_tools_fs15c.py"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
s = open('C:/kyty/f287/fs14c/test_tools_fs14c.py', 'rb').read().replace(b'\r\n', b'\n').decode('ascii')


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:90])
    s = s.replace(old, new)


DOC_END = s.index('"""', 3) + 3
s = '''"""Fixtures of the FS15c chain (Track F link FS15c, HPP-822; ROADMAP s122 item 730 (g)(3), 732, 733, 634 / 660 / 661): the dry-run
plans of go_fs15c.sh for fs15_v / fs15_w / fs15_z (level, stable draws, timeout, hold, video / validation, knobs: no KYTY_FIX_* at fs15_v /
fs15_w, KYTY_FIX_F20=0 the only KYTY_FIX_ value at fs15_z, no KYTY_TEST_*), refusals of go_fs15c.sh and launch_fs15c.sh (usage; a repeat
without the lead's item - FS15C_REPEAT_OK), the form linter --series = ALL OK, the first executable line of go / launch = the linter, the
install / return of the binary (the FS15 copy bfac84be installed after the copies of the caches, the pinned FS14 013e1974 copy returned in
finish; the sha256 of both copies on disk = the literals), the own issue of queue / runchk / chk = HPP-822, the tempo tool = the FS14c one
with the names moved, the enter_scene.py ROOT and CLOSE_WAIT_S, ASCII of every script; post_fs15c.sh takes the plan by the line starting
'dryrun ' (checked by running post_fs15c.sh with FS15C_POST_PLANONLY=1 for every tag); the pair of fs15_v with the fs14_v sheet of FS14c
(letter of item 730 (g)(3): 'the sheet next to fs14_v'); strict cp1250 output; the last line is ALL OK.  Port of
C:/kyty/f287/fs14c/test_tools_fs14c.py by patch_tools_fs15c.py.  Early-exit form (ok = True, ok &= ..., sys.exit(0 if ok else 1)).
ASCII only.
usage: python test_tools_fs15c.py"""''' + s[DOC_END:]
rep("GO = os.path.join(HERE, 'go_fs14c.sh')\nLA = os.path.join(HERE, 'launch_fs14c.sh')\nPO = os.path.join(HERE, 'post_fs14c.sh')",
    "GO = os.path.join(HERE, 'go_fs15c.sh')\nLA = os.path.join(HERE, 'launch_fs15c.sh')\nPO = os.path.join(HERE, 'post_fs15c.sh')")
rep("TB = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'\nFS13 = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'\n"
    "LINT = 'python \"C:/kyty/KytyPS5/ps5 em/docs/form634_check.py\" --series C:/kyty/f287/fs14c'\n"
    "PAIR = 'C:/kyty/f287/fs13c/runs/fs13_v/sheet_fs13_v.png'",
    "TB = 'bfac84bea0eaec8bf3dae6ab5f67cd480f26921829f64f4a8b467bd50e922d8c'\nFS14 = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'\n"
    "LINT = 'python \"C:/kyty/KytyPS5/ps5 em/docs/form634_check.py\" --series C:/kyty/f287/fs15c'\n"
    "PAIR = 'C:/kyty/f287/fs14c/runs/fs14_v/sheet_fs14_v.png'")
rep("print('suite test_tools_fs14c.py sha256 %s target go_fs14c.sh sha256 %s'", "print('suite test_tools_fs15c.py sha256 %s target go_fs15c.sh sha256 %s'")
rep("        if k.startswith(('FS14C_', 'FS13C_')):", "        if k.startswith(('FS15C_', 'FS14C_')):")
rep("""    'fs14_v': 'level""", """    'fs15_v': 'level""")
rep("""    'fs14_w': 'level""", """    'fs15_w': 'level""")
rep("""    'fs14_z': 'level underwater_aerial_garden sd 300 timeout 480 hold 150 rec --rec knobs KYTY_FIX_F24=0 KYTY_FIX_F29=0 KYTY_GPU_CLOCK_PIN=1 '
              'KYTY_GPU_MARKERS=0',""", """    'fs15_z': 'level underwater_aerial_garden sd 300 timeout 480 hold 150 rec --rec knobs KYTY_FIX_F20=0 KYTY_GPU_CLOCK_PIN=1 '
              'KYTY_GPU_MARKERS=0',""")
rep("""        rc, out = sh(GO, [t], {'FS14C_DRYRUN': '1'})""", """        rc, out = sh(GO, [t], {'FS15C_DRYRUN': '1'})""")
rep("""    ok &= check('plan %s: KYTY_FIX_ only at fs14_z, only KYTY_FIX_F24=0 and KYTY_FIX_F29=0' % b,
                (w.count('KYTY_FIX_') == 2 and 'KYTY_FIX_F24=0' in w and 'KYTY_FIX_F29=0' in w) if b == 'fs14_z' else ('KYTY_FIX_' not in w))""",
    """    ok &= check('plan %s: KYTY_FIX_ only at fs15_z, only KYTY_FIX_F20=0' % b,
                (w.count('KYTY_FIX_') == 1 and 'KYTY_FIX_F20=0' in w) if b == 'fs15_z' else ('KYTY_FIX_' not in w))""")
rep("""rc, out = sh(GO, ['fs14_v'], {'FS14C_DRYRUN': '1'})""", """rc, out = sh(GO, ['fs15_v'], {'FS15C_DRYRUN': '1'})""")
rep("""            out.splitlines()[0].strip() == 'ALL OK' and out.splitlines()[1].startswith('dryrun fs14_v '))
for b in ('fs14_v', 'fs14_w', 'fs14_z', 'fs14_w_r2'):
    rc, out = sh(PO, [b], {'FS14C_POST_PLANONLY': '1'})
    lines = out.splitlines()
    pw = 'yes' if b.startswith('fs14_w') else 'no'""", """            out.splitlines()[0].strip() == 'ALL OK' and out.splitlines()[1].startswith('dryrun fs15_v '))
for b in ('fs15_v', 'fs15_w', 'fs15_z', 'fs15_w_r2'):
    rc, out = sh(PO, [b], {'FS15C_POST_PLANONLY': '1'})
    lines = out.splitlines()
    pw = 'yes' if b.startswith('fs15_w') else 'no'""")
rep("""            "bash $G/go_fs14c.sh $T 2>&1 | grep '^dryrun ' | head -1)" in po and 'go_fs14c.sh $T 2>&1 | head -1' not in po)""",
    """            "bash $G/go_fs15c.sh $T 2>&1 | grep '^dryrun ' | head -1)" in po and 'go_fs15c.sh $T 2>&1 | head -1' not in po)""")
rep("""            po.index('FS14C_POST_PLANONLY') < po.index('[ -e C:/kyty/SEALED_RUN.lock ]') < po.index('fs14c_read.py $T'))
ok &= check('post: pair of fs14_v with the fs13_v sheet of FS13c', PAIR in po and 'pair_${T}_fs13_v.png' in po
            and 'f25_v' not in po and 'f38c' not in po)
ok &= check('on disk: the fs13_v sheet exists', os.path.exists(PAIR))
for bad in ('fs14_x', 'fs14_v_r4', 'fs14_z_r0', 'fs13_v', 'f24_n1', ''):
    rc, out = sh(GO, [bad] if bad else [], {'FS14C_DRYRUN': '1'})
    ok &= check('go usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(LA, [bad] if bad else [], {'FS14C_DRYRUN': '2'})
    ok &= check('launch usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(PO, [bad] if bad else [], {'FS14C_POST_PLANONLY': '1'})""",
    """            po.index('FS15C_POST_PLANONLY') < po.index('[ -e C:/kyty/SEALED_RUN.lock ]') < po.index('fs15c_read.py $T'))
ok &= check('post: pair of fs15_v with the fs14_v sheet of FS14c', PAIR in po and 'pair_${T}_fs14_v.png' in po
            and 'fs13_v' not in po and 'fs13c' not in po)
ok &= check('on disk: the fs14_v sheet exists', os.path.exists(PAIR))
for bad in ('fs15_x', 'fs15_v_r4', 'fs15_z_r0', 'fs14_v', 'f20_v', ''):
    rc, out = sh(GO, [bad] if bad else [], {'FS15C_DRYRUN': '1'})
    ok &= check('go usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(LA, [bad] if bad else [], {'FS15C_DRYRUN': '2'})
    ok &= check('launch usage rc 2 for %r' % bad, rc == 2)
    rc, out = sh(PO, [bad] if bad else [], {'FS15C_POST_PLANONLY': '1'})""")
rep("""tmp = tempfile.mkdtemp(prefix='fs14ct_')""", """tmp = tempfile.mkdtemp(prefix='fs15ct_')""")
rep("""envq = {'FS14C_DRYRUN': '2', 'FS14C_QUEUE_SKIP': '1', 'FS14C_DISP_SKIP': '1', 'FS14C_TIMES': tm}
for t in ('fs14_v', 'fs14_w', 'fs14_z'):""", """envq = {'FS15C_DRYRUN': '2', 'FS15C_QUEUE_SKIP': '1', 'FS15C_DISP_SKIP': '1', 'FS15C_TIMES': tm}
for t in ('fs15_v', 'fs15_w', 'fs15_z'):""")
rep("""    ok &= check('launch repeat %s_r1 without FS14C_REPEAT_OK -> rc 11' % t, rc == 11)
    rc, out = sh(LA, [t + '_r1'], dict(envq, FS14C_REPEAT_OK='1'))
    ok &= check('launch repeat %s_r1 with FS14C_REPEAT_OK -> passes' % t, rc == 0 and 'dryrun2 rep 1' in out)""",
    """    ok &= check('launch repeat %s_r1 without FS15C_REPEAT_OK -> rc 11' % t, rc == 11)
    rc, out = sh(LA, [t + '_r1'], dict(envq, FS15C_REPEAT_OK='1'))
    ok &= check('launch repeat %s_r1 with FS15C_REPEAT_OK -> passes' % t, rc == 0 and 'dryrun2 rep 1' in out)""")
rep("""ok &= check('go: TB literal = 013e1974', 'TB=' + TB in src)
ok &= check('go: FS13 literal = abab2196', 'FS13=' + FS13 in src)
ok &= check('go: BIN and PINNED paths', 'BIN=$F/bin/kyty_emulator_013e1974.exe' in src and 'PINNED=$F/bin/kyty_emulator_abab2196.exe' in src)
ok &= check('on disk: sha256 of the FS14 copy = 013e1974', sha('C:/kyty/f287/bin/kyty_emulator_013e1974.exe') == TB)
ok &= check('on disk: sha256 of the pinned FS13 copy = abab2196', sha('C:/kyty/f287/bin/kyty_emulator_abab2196.exe') == FS13)""",
    """ok &= check('go: TB literal = bfac84be', 'TB=' + TB in src)
ok &= check('go: FS14 literal = 013e1974', 'FS14=' + FS14 in src)
ok &= check('go: BIN and PINNED paths', 'BIN=$F/bin/kyty_emulator_bfac84be.exe' in src and 'PINNED=$F/bin/kyty_emulator_013e1974.exe' in src)
ok &= check('on disk: sha256 of the FS15 copy = bfac84be', sha('C:/kyty/f287/bin/kyty_emulator_bfac84be.exe') == TB)
ok &= check('on disk: sha256 of the pinned FS14 copy = 013e1974', sha('C:/kyty/f287/bin/kyty_emulator_013e1974.exe') == FS14)""")
rep("""            src.index('lock taken $T') < src.index('guard_fs14c.py scan)') < src.index('hold_fs14c.py check)')""",
    """            src.index('lock taken $T') < src.index('guard_fs15c.py scan)') < src.index('hold_fs15c.py check)')""")
rep("""            src.index('guard_fs14c.py scan)') > src.index('set -o noclobber') and src.index('hold_fs14c.py check)') > src.index('set -o noclobber'))
ok &= check('go: install of the FS14 copy after the copies of the caches and after INSTALLED=1',""",
    """            src.index('guard_fs15c.py scan)') > src.index('set -o noclobber') and src.index('hold_fs15c.py check)') > src.index('set -o noclobber'))
ok &= check('go: install of the FS15 copy after the copies of the caches and after INSTALLED=1',""")
rep("""ok &= check('go: the return of the pinned FS13 copy in finish, before installed_after',""",
    """ok &= check('go: the return of the pinned FS14 copy in finish, before installed_after',""")
rep("""ok &= check('go: installed_after must be FS13', '[ "$(cat $OUT/installed_after.txt)" = "$FS13" ] || { OK=0;' in src)
ok &= check('go: installed before the tag must be FS13', '[ "$WANT" = "$FS13" ] ||' in src)
ok &= check('go: no FS12 / 46892c20 / FS11 / ea51ae80 left', all(w not in src for w in ('FS12', '46892c20', 'FS11', 'ea51ae80')))
ok &= check('go: KYTY_FIX_ in the knobs only KYTY_FIX_F24=0 and KYTY_FIX_F29=0 (fs14_z)',
            body.count('KYTY_FIX_') == body.count('KYTY_FIX_F24=0') + body.count('KYTY_FIX_F29=0') + body.count('KYTY_FIX_* except')
            and body.count('KYTY_FIX_F24=0') == 1 and body.count('KYTY_FIX_F29=0') == 1 and 'KYTY_FIX_F25' not in body)""",
    """ok &= check('go: installed_after must be FS14', '[ "$(cat $OUT/installed_after.txt)" = "$FS14" ] || { OK=0;' in src)
ok &= check('go: installed before the tag must be FS14', '[ "$WANT" = "$FS14" ] ||' in src)
ok &= check('go: no FS13 / abab2196 / FS12 / 46892c20 left', all(w not in src for w in ('FS13', 'abab2196', 'FS12', '46892c20')))
ok &= check('go: KYTY_FIX_ in the knobs only KYTY_FIX_F20=0 (fs15_z)',
            body.count('KYTY_FIX_') == body.count('KYTY_FIX_F20=0') + body.count('KYTY_FIX_* except')
            and body.count('KYTY_FIX_F20=0') == 1 and 'KYTY_FIX_F24' not in body and 'KYTY_FIX_F29' not in body)""")
rep("""ok &= check('go: lock line names HPP-814', 'echo "FS14c HPP-814 go_fs14c.sh $T pid $$ $(u)" > $LOCK' in src)
for nm in ('queue_fs14c.py', 'runchk_fs14c.py'):
    ok &= check('%s own issue HPP-814' % nm, "OWN = 'HPP-814'" in open(os.path.join(HERE, nm), encoding='ascii').read())
ok &= check('chk_fs14c.sh comments of HPP-814', '/api/issues/HPP-814/comments' in open(os.path.join(HERE, 'chk_fs14c.sh'), encoding='ascii').read())""",
    """ok &= check('go: lock line names HPP-822', 'echo "FS15c HPP-822 go_fs15c.sh $T pid $$ $(u)" > $LOCK' in src)
for nm in ('queue_fs15c.py', 'runchk_fs15c.py'):
    ok &= check('%s own issue HPP-822' % nm, "OWN = 'HPP-822'" in open(os.path.join(HERE, nm), encoding='ascii').read())
ok &= check('chk_fs15c.sh comments of HPP-822', '/api/issues/HPP-822/comments' in open(os.path.join(HERE, 'chk_fs15c.sh'), encoding='ascii').read())""")
rep("""ok &= check('enter_scene: ROOT = f287/fs14c', "ROOT = pathlib.Path('C:/kyty/f287/fs14c')" in es)""",
    """ok &= check('enter_scene: ROOT = f287/fs15c', "ROOT = pathlib.Path('C:/kyty/f287/fs15c')" in es)""")
rep("""a = open('C:/kyty/f287/fs13c/tempo_fs13c.py', 'rb').read().replace(b'\\r\\n', b'\\n')
for x, y in ((b'fs13c', b'fs14c'), (b'FS13C', b'FS14C'), (b'FS13c', b'FS14c'), (b'HPP-789', b'HPP-814')):
    a = a.replace(x, y)
b = open(os.path.join(HERE, 'tempo_fs14c.py'), 'rb').read()
ok &= check('tempo_fs14c.py = tempo_fs13c.py with the names moved (+ one header line)', b.split(b'\\n', 1)[1] == a)""",
    """a = open('C:/kyty/f287/fs14c/tempo_fs14c.py', 'rb').read().replace(b'\\r\\n', b'\\n')
for x, y in ((b'fs14c', b'fs15c'), (b'FS14C', b'FS15C'), (b'FS14c', b'FS15c'), (b'HPP-814', b'HPP-822')):
    a = a.replace(x, y)
b = open(os.path.join(HERE, 'tempo_fs15c.py'), 'rb').read()
ok &= check('tempo_fs15c.py = tempo_fs14c.py with the names moved (+ one header line)', b.split(b'\\n', 1)[1] == a)""")
import re as _re
for _l in s.split(chr(10)):
    if "fs14c" in _l: print("LEFT", _l[:150])
assert all(ord(c) < 128 for c in s)
open(os.path.join(HERE, 'test_tools_fs15c.py'), 'w', encoding='ascii', newline='\n').write(s)
print('test_tools_fs15c.py written')
print('ALL OK')
