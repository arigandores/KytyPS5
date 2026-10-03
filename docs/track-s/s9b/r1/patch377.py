"""patch377.py - track S link S9b, rework 1 (HPP-458; ROADMAP "SESSION 122" item 377 (b), item 374 (g)): the admission row
installed_before = 540c035a (FS3, installed 2026-10-03T07:11:12Z) as a constant of its own in the harness (INST_WANT) and the
scorer (INST_WANT), apart from the u binary BIN_U (the pinned copy 4aa62e95, unchanged); the seal path pred/06b_s.md; fixtures of
both outcomes; mutants of the row; the generator of seal 06b (s9/mkseal_s06b.py, s9/seal06b_body.md, s9/seal06b_tail.md from
the files of seal 06, which do not change).  Every replacement matches once.  Originals copied to s9b/r1/orig first.  LF, ASCII.
Refuses under the lock or the stop file.
    python C:/kyty/s288/s9b/r1/patch377.py
"""
import os
import shutil
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/s288/STOP'
D = 'C:/kyty/s288/s9/'
O = 'C:/kyty/s288/s9b/r1/orig/'
NEW = '540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1'
OLD = '4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac'
ROW_OLD = "'installed binary before the arm = the installed 4aa62e95 of item 342 (item 371 (g), RC1)'"
ROW_NEW = "ROW_IB"

SC = [
    ("u_1 .. u_5 (item 355 (e), the installed 4aa62e95\n",
     "u_1 .. u_5 (item 355 (e), the pinned 4aa62e95\n"),
    ("PRED_PATH = 'C:/kyty/s288/pred/06_s.md'                        # item 371 (g)\n",
     "PRED_PATH = 'C:/kyty/s288/pred/06b_s.md'                       # item 371 (g), item 377 (b)(4)\n"),
    ("BIN_U = '%s'   # installed, item 342, item 355 (e)\n" % OLD,
     "BIN_U = '%s'   # binary u: the pinned copy, item 342, item 355 (e)\n"
     "INST_WANT = '%s'   # installed before every arm, item 374 (g), item 377 (b)(1)\n" % (OLD, NEW)),
    ("    add('installed binary before the arm = the installed %s of item 342 (item 371 (g), RC1)' % BIN_U[:8], ib == BIN_U,\n",
     "    add('installed binary before the arm = the installed %s of item 374 (g) (item 371 (g), RC1)' % INST_WANT[:8],\n"
     "        ib == INST_WANT,\n"),
]

GO = [
    ("KYTY_CACHE_MODE=prepare-cold, binary u (the installed 4aa62e95), the catalogue checked by sha before\n",
     "KYTY_CACHE_MODE=prepare-cold, binary u (the pinned copy 4aa62e95), the catalogue checked by sha before\n"),
    ("(4aa62e95) of pred/06_s.md (item 371 (g)).\n", "(4aa62e95) of pred/06b_s.md (item 377 (b)).\n"),
    ("ADMISSION: the installed binary before the arm = INST_WANT (4aa62e95, item\n"
     "#     342), else no arm (rc 1) - a new installation stops S10 until a lead item names the new sha.\n",
     "ADMISSION: the installed binary before the arm = INST_WANT (540c035a, FS3,\n"
     "#     item 374 (g), item 377 (b)), else no arm (rc 1); INST_WANT is not the binary u (the pinned 4aa62e95 of the seal line).\n"),
    ("PRED=pred/06_s.md\n", "PRED=pred/06b_s.md\n"),
    ('INST_WANT="%s"\n' % OLD, 'INST_WANT="%s"\n' % NEW),
    ('  log "the installed binary before the arm $INST_SHA != the installed of item 342 $INST_WANT - no arm (item 371 (g))"\n',
     '  log "the installed binary before the arm $INST_SHA != the installed of item 374 (g) $INST_WANT - no arm (item 371 (g))"\n'),
    ('  tline "installed binary before the arm $INST_SHA != $INST_WANT (item 342) - no arm; S10 stands until a lead item names the new sha"\n',
     '  tline "installed binary before the arm $INST_SHA != $INST_WANT (item 374 (g)) - no arm; a new installation needs a lead item"\n'),
]

TSC = [
    ("installed_before = 4aa62e95, the lower bound",
     "installed_before (S9b rework 1, item 377 (b): 540c035a passes, the pinned u binary 4aa62e95 fails), the lower bound"),
    ("BIN_U = '%s'\n" % OLD,
     "BIN_U = '%s'\nINST = '%s'\n"
     "ROW_IB = 'installed binary before the arm = the installed 540c035a of item 374 (g) (item 371 (g), RC1)'\n" % (OLD, NEW)),
    ("installed_before=dict(sha=BIN_U), installed_after=dict(sha=BIN_U), return_prev=dict(ok='1'))",
     "installed_before=dict(sha=INST), installed_after=dict(sha=INST), return_prev=dict(ok='1'))"),
    ("ok &= case('A3 binaries s = f3b3aa3b, u = 4aa62e95; snapshots d8ca8c8e / 1767ca0a; empty set e3b0c442; catalogue 72605a65',\n"
     "           S.BIN_S == BIN_S and S.BIN_U == BIN_U and",
     "ok &= case('A3 binaries s = f3b3aa3b, u = 4aa62e95, installed 540c035a (item 374 (g)) apart from u; snapshots d8ca8c8e / '\n"
     "           '1767ca0a; empty set e3b0c442; catalogue 72605a65',\n"
     "           S.BIN_S == BIN_S and S.BIN_U == BIN_U and S.INST_WANT == INST and S.INST_WANT != S.BIN_U and"),
    ("ok &= case('A6 paths: link C:/kyty/s288/s10, seal pred/06_s.md (item 371 (g)), Sky Garden, L0 shuriken_ninja_castle',\n"
     "           S.LINK_DIR == 'C:/kyty/s288/s10' and S.PRED_PATH == 'C:/kyty/s288/pred/06_s.md'",
     "ok &= case('A6 paths: link C:/kyty/s288/s10, seal pred/06b_s.md (item 377 (b)(4)), Sky Garden, L0 shuriken_ninja_castle',\n"
     "           S.LINK_DIR == 'C:/kyty/s288/s10' and S.PRED_PATH == 'C:/kyty/s288/pred/06b_s.md'"),
    ("ok &= case('F7 item 371 (g), RC1: installed_before must be the installed 4aa62e95 of item 342 - before = after = f3b3aa3b fails that '\n"
     "           'row only', [r[0] for r in crow('pi_w1', installed_before=dict(sha=BIN_S), installed_after=dict(sha=BIN_S))] ==\n"
     "           [%s] and\n"
     "           [r[0] for r in crow('u_2', installed_before=dict(sha=BIN_S), installed_after=dict(sha=BIN_S))] ==\n"
     "           [%s])\n" % (ROW_OLD, ROW_OLD),
     "ok &= case('F7 item 371 (g), RC1: installed_before must be the installed 540c035a of item 374 (g) - before = after = f3b3aa3b '\n"
     "           'fails that row only', [r[0] for r in crow('pi_w1', installed_before=dict(sha=BIN_S), installed_after=dict(sha=BIN_S))]\n"
     "           == [ROW_IB] and\n"
     "           [r[0] for r in crow('u_2', installed_before=dict(sha=BIN_S), installed_after=dict(sha=BIN_S))] == [ROW_IB])\n"
     "ok &= case('F7b item 377 (b)(2): installed 540c035a -> the row passes (pi_w1, u_2); installed 4aa62e95 (the pinned u binary, the '\n"
     "           'installed of item 342) -> that row only fails, for an s arm and a u arm',\n"
     "           ROW_IB not in [r[0] for r in crow('pi_w1')] and ROW_IB not in [r[0] for r in crow('u_2')] and\n"
     "           not crow('pi_w1') and not crow('u_2') and\n"
     "           [r[0] for r in crow('pi_w1', installed_before=dict(sha=BIN_U), installed_after=dict(sha=BIN_U))] == [ROW_IB] and\n"
     "           [r[0] for r in crow('u_2', installed_before=dict(sha=BIN_U), installed_after=dict(sha=BIN_U))] == [ROW_IB])\n"),
]

TGO = [
    ("no IN_ARM, no attempt.  The first output line",
     "no IN_ARM, no attempt.  S9b rework 1 (item 377 (b)(2)): INST_WANT = 540c035a (item 374 (g)) apart from the u binary - the\n"
     "fixture installed build differs from the pinned u stand-in; an arm with the installed = INST_WANT runs (the game sees the s / u\n"
     "binary, the installed build back after); the installed = the u stand-in (the 4aa62e95 of item 342) -> rc 1 inside the lock,\n"
     "nothing installed.  The first output line"),
    ("SC9, (BASE / 's10').as_posix(), (BASE / 'pred' / '06_s.md').as_posix())",
     "SC9, (BASE / 's10').as_posix(), (BASE / 'pred' / '06b_s.md').as_posix())"),
    ("    (BASE / 'pred' / '06_s.md').write_text('\\n'.join(lines) + '\\n', encoding='ascii')",
     "    (BASE / 'pred' / '06b_s.md').write_text('\\n'.join(lines) + '\\n', encoding='ascii')"),
    ("ok &= case('G23 item 371 (g): the shipped harness guards s10/IN_ARM with the RETURN_FAILED guards and pins INST_WANT = 4aa62e95 '\n"
     "           '(item 342); the seal is pred/06_s.md', '$ROOT/s10/RETURN_FAILED $ROOT/s10/IN_ARM; do' in src_t and\n"
     "           'INST_WANT=\"%s\"\\n' in src_t and\n"
     "           'PRED=pred/06_s.md\\n' in src_t and src_t.count('guardfiles\\n') == 2)" % OLD,
     "ok &= case('G23 item 371 (g), item 377 (b): the shipped harness guards s10/IN_ARM with the RETURN_FAILED guards and pins '\n"
     "           'INST_WANT = 540c035a (item 374 (g)), not 4aa62e95; the seal is pred/06b_s.md',\n"
     "           '$ROOT/s10/RETURN_FAILED $ROOT/s10/IN_ARM; do' in src_t and\n"
     "           'INST_WANT=\"%s\"\\n' in src_t and 'INST_WANT=\"4aa62e95' not in src_t and\n"
     "           'PRED=pred/06b_s.md\\n' in src_t and src_t.count('guardfiles\\n') == 2)" % NEW),
    ("ENV2 = dict(CACHEX_EMU=str(EMU2), CACHEX_GLC=str(GLC2), CACHEX_LOCK=LOCK2, CACHEX_KNOWN_LAD=str(LAD2), LOCALAPPDATA=str(LAD2))",
     "ENV2 = dict(CACHEX_EMU=str(EMU2), CACHEX_GLC=str(GLC2), CACHEX_LOCK=LOCK2, CACHEX_KNOWN_LAD=str(LAD2), LOCALAPPDATA=str(LAD2),\n"
     "            FX_GAME=str(GAME2))"),
    ("put2(PINU, b'installed build X')\n", "put2(PINU, b'4aa62e95 stand-in')\nINSTX = hashlib.sha256(b'installed build X').hexdigest()\n"),
    ('    "import json, os, sys\\ntag = sys.argv[1]\\n',
     '    "import hashlib, json, os, sys\\ntag = sys.argv[1]\\n'),
    ("\"'glc': sorted(os.listdir(os.path.join(glc, 'x')))}, open(",
     "\"'game': hashlib.sha256(open(os.environ['FX_GAME'], 'rb').read()).hexdigest(), \"\n"
     "    \"'glc': sorted(os.listdir(os.path.join(glc, 'x')))}, open("),
    ("'INST_WANT=\"%%s\"\\n' %% sha2(PINU))):" .replace('%%', '%'),
     "'INST_WANT=\"%s\"\\n' % INSTX)):"),
    ("('INST_WANT=\"" + OLD + "\"\\n', ", "('INST_WANT=\"" + NEW + "\"\\n', "),
    ("(B2 / 'pred' / '06_s.md').write_bytes(", "(B2 / 'pred' / '06b_s.md').write_bytes("),
    ("rc == 0 and GAME2.read_bytes() == b'installed build X' and c.get('installed_before', {}).get('sha') == sha2(PINU)\n"
     "           and c.get('installed_after', {}).get('sha') == sha2(PINU))",
     "rc == 0 and GAME2.read_bytes() == b'installed build X' and c.get('installed_before', {}).get('sha') == INSTX\n"
     "           and c.get('installed_after', {}).get('sha') == INSTX and j.get('game') == sha2(PINS))"),
    ("           CX.glc_manifest(str(GLC2))[1] == PRE_GLC)\nlr = lockrows()\n",
     "           CX.glc_manifest(str(GLC2))[1] == PRE_GLC)\n"
     "ok &= case('GL5b item 377 (b)(1): INST_WANT (the installed) is not the u binary - the game of u_1 ran the pinned u stand-in, '\n"
     "           'installed_before = the installed build, the installed build back after', j.get('game') == sha2(PINU) and\n"
     "           sha2(PINU) != INSTX and c.get('installed_before', {}).get('sha') == INSTX and\n"
     "           c.get('installed_after', {}).get('sha') == INSTX and GAME2.read_bytes() == b'installed build X')\n"
     "lr = lockrows()\n"),
    ("('installed: %s (copy' % sha2(PINU)) in ia1",
     "('installed: %s (copy' % INSTX) in ia1"),
    ("           ('!= %s (item 342) - no arm' % sha2(PINU)) in t5)\nput2(GAME2, b'installed build X')\n",
     "           ('!= %s (item 374 (g)) - no arm' % INSTX) in t5)\n"
     "put2(GAME2, b'4aa62e95 stand-in')\n"
     "n_lock = len(lockrows())\n"
     "rc, o = go2('pi_w0')\n"
     "t6 = (B2 / 's10' / 'times.txt').read_text()\n"
     "ok &= case('GL12b item 377 (b)(2): the installed = 4aa62e95 (the pinned u stand-in, the installed of item 342) -> rc 1 inside '\n"
     "           'the lock: nothing installed, no IN_ARM, no attempt, the lock taken and released', rc == 1 and\n"
     "           ('installed binary not %s' % INSTX) in o and GAME2.read_bytes() == b'4aa62e95 stand-in' and\n"
     "           not (B2 / 's10' / 'IN_ARM').exists() and not (B2 / 's10' / 'attempt_pi_w0.txt').exists() and\n"
     "           len(lockrows()) == n_lock + 2 and not Path(LOCK2).exists() and\n"
     "           ('installed binary before the arm %s != %s (item 374 (g)) - no arm' % (sha2(PINU), INSTX)) in t6)\n"
     "put2(GAME2, b'installed build X')\n"),
]

MUT = [
    ("the member rule and the three words of U, the RC4 data and the RC5 sheet frames.",
     "the member rule and the three words of U, the RC4 data and the RC5 sheet frames.  S9b rework 1 (item 377 (b)(3)): the constant\n"
     "INST_WANT (540c035a, item 374 (g)) apart from BIN_U and the row installed_before on it (--only, s9b/r1)."),
    ("    ('bin_u', \"BIN_U = '4aa62e95\", \"BIN_U = '4aa62e96\"),\n",
     "    ('bin_u', \"BIN_U = '4aa62e95\", \"BIN_U = '4aa62e96\"),\n"
     "    ('inst_want', \"INST_WANT = '540c035a\", \"INST_WANT = '540c035b\"),\n"
     "    ('inst_is_u', \"INST_WANT = '%s'\", \"INST_WANT = '%s'\"),\n" % (NEW, OLD)),
    ("    ('cr_ib', \"ib == BIN_U,\\n        (ib or '-')[:16])\", \"True,\\n        (ib or '-')[:16])\"),\n"
     "    ('cr_ib_s', \"ib == BIN_U,\\n        (ib or '-')[:16])\", \"ib in (BIN_U, BIN_S),\\n        (ib or '-')[:16])\"),\n",
     "    ('cr_ib', \"        ib == INST_WANT,\\n        (ib or '-')[:16])\", \"        True,\\n        (ib or '-')[:16])\"),\n"
     "    ('cr_ib_s', \"        ib == INST_WANT,\\n        (ib or '-')[:16])\", \"        ib in (INST_WANT, BIN_S),\\n        (ib or '-')[:16])\"),\n"
     "    ('cr_ib_u', \"        ib == INST_WANT,\\n        (ib or '-')[:16])\", \"        ib == BIN_U,\\n        (ib or '-')[:16])\"),\n"
     "    ('cr_ib_old', \"        ib == INST_WANT,\\n        (ib or '-')[:16])\", \"        ib in (INST_WANT, BIN_U),\\n        (ib or '-')[:16])\"),\n"),
    ("    ('pred', \"PRED_PATH = 'C:/kyty/s288/pred/06_s.md'\", \"PRED_PATH = 'C:/kyty/s288/pred/05b_s.md'\"),\n",
     "    ('pred', \"PRED_PATH = 'C:/kyty/s288/pred/06b_s.md'\", \"PRED_PATH = 'C:/kyty/s288/pred/06_s.md'\"),\n"),
]

MK = [
    ('"""mkseal_s06.py - track S, link S9b (HPP-458; item 371 (g)): writes the seal C:/kyty/s288/pred/06_s.md of link S10',
     '"""mkseal_s06b.py - track S, link S9b rework 1 (HPP-458; items 371 (g), 377 (b)): writes the seal C:/kyty/s288/pred/06b_s.md of link S10'),
    ('    python C:/kyty/s288/s9/mkseal_s06.py\n', '    python C:/kyty/s288/s9/mkseal_s06b.py\n'),
    ("OUT = R + '/pred/06_s.md'", "OUT = R + '/pred/06b_s.md'"),
    ("""    w('# Seal 06_s - track S link S9b (HPP-458) for link S10: the repeat of integrity, C5, the T2 base with t2_cs0, the S-cat '
      'probe (ROADMAP "SESSION 122" item 355 (g)-(zh), (k); items 362, 371)')""",
     """    w('# Seal 06b_s - track S link S9b (HPP-458), rework 1, for link S10: the repeat of integrity, C5, the T2 base with t2_cs0, '
      'the S-cat probe (ROADMAP "SESSION 122" item 355 (g)-(zh), (k); items 362, 371, 374 (g), 377)')"""),
    ("""    w('Written by C:/kyty/s288/s9/mkseal_s06.py (sha256 %s) at %s UTC, before any S10 arm.  It replaces the seal pred/05b_s.md '
      '(sha256 6641154ecb5cec89102c0c4b4af607d7d723f69e294ef7598d08a2d9804dcd81, not changed; it replaced pred/05_s.md '
      'd56e2e645ca7f0be60266c25bfa87869e94c4f3e0e9146796625fda000605784): S10 goes by this seal (item 371 (g)).'""",
     """    w('Written by C:/kyty/s288/s9/mkseal_s06b.py (sha256 %s) at %s UTC, before any S10 arm.  It replaces the seal pred/06_s.md '
      '(sha256 0fb11c0e703248bee62ce6f0f9fe40604c8c1526cc36ead8e738398152949c20, not changed; it replaced pred/05b_s.md '
      '6641154ecb5cec89102c0c4b4af607d7d723f69e294ef7598d08a2d9804dcd81 and pred/05_s.md '
      'd56e2e645ca7f0be60266c25bfa87869e94c4f3e0e9146796625fda000605784): S10 goes by this seal (item 377 (b)(4)).'"""),
    ("sha(R + '/s9/mkseal_s06.py')", "sha(R + '/s9/mkseal_s06b.py')"),
    ("open(R + '/s9/seal06_body.md'", "open(R + '/s9/seal06b_body.md'"),
    ("open(R + '/s9/seal06_tail.md'", "open(R + '/s9/seal06b_tail.md'"),
    ("    w('u binary: %s C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe' % S.BIN_U)\n",
     "    w('u binary: %s C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe' % S.BIN_U)\n"
     "    w('')\n"
     "    w('Admission row installed_before (item 374 (g), item 377 (b)(1); INST_WANT of go_s9.sh and of sc_s9.py; not the u binary): '\n"
     "      'the installed C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe before every arm = %s (FS3, installed 2026-10-03T07:11:12Z)'\n"
     "      % S.INST_WANT)\n"),
    ("""    w('- mutant runs (wall): ' + open(R + '/s9b/mutwalls.txt', encoding='ascii').read().strip())""",
     """    for name, p in (('mutants --only of rework 1 (item 377 (b)(3): the admission row installed_before, the constants, the seal '
                     'path)', R + '/s9b/r1/mut_screen7.txt'),):
        lines = open(p, encoding='ascii', errors='replace').read().splitlines()
        w('- %s: %s sha256 %s; %s' % (name, p, sha(p), lines[-1] if lines else '-'))
    w('- mutant runs (wall): ' + open(R + '/s9b/r1/mutwalls.txt', encoding='ascii').read().strip())"""),
]

BODY = [
    ("""  (a hard kill of an arm leaves it; the lead returns by hand and removes it).  Admission row installed_before = 4aa62e95 (the
  installed of item 342): in the harness inside the lock before the install (no arm otherwise, rc 1) and in the scorer
  (cache_rows); a change of the installed binary (for example FS3d HPP-450) stops S10 until a lead item names the new sha.
""",
     """  (a hard kill of an arm leaves it; the lead returns by hand and removes it).  Admission row installed_before = 540c035a (FS3,
  installed 2026-10-03T07:11:12Z; item 374 (g), item 377 (b)(1)): the constant INST_WANT of go_s9.sh and of sc_s9.py, apart from
  the u binary (BIN_U, the pinned copy 4aa62e95, unchanged); in the harness inside the lock before the install (no arm
  otherwise, rc 1, nothing installed) and in the scorer (cache_rows; 4aa62e95 installed -> the row fails).
"""),
    ("- (e) the S-cat probe, binary u (the installed 4aa62e95), form U:",
     "- (e) the S-cat probe, binary u (the pinned copy 4aa62e95), form U:"),
]

TAIL = [
    ("## 6. Executor variants and the decisions of items 362 and 371 (ROADMAP \"SESSION 122\" item 371, KytyPS5 dcc6cbf8; item 362, KytyPS5 a1f02bd5)\n",
     "## 6. Executor variants and the decisions of items 362, 371, 374 (g) and 377 (ROADMAP \"SESSION 122\" item 371, KytyPS5 dcc6cbf8; item 362, KytyPS5 a1f02bd5; item 374 (g), KytyPS5 704c13d2; item 377, KytyPS5 a387a2d4)\n"),
    ("- (g) RC1 - the guard s10/IN_ARM and the admission row installed_before = 4aa62e95 in the harness and the scorer (section 1);",
     "- (g) RC1 - the guard s10/IN_ARM and the admission row installed_before in the harness and the scorer (section 1; its sha by\n"
     "  item 374 (g), below);"),
    ("""- The installation changed during this link: since 2026-10-03T07:11:12Z the installed binary is FS3
  540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1 (FS3d HPP-450, ROADMAP "SESSION 122" items 374 - 375; the lead
  note in HPP-453 at 07:14:06Z).  By item 371 (g) the admission row installed_before = 4aa62e95 now fails (go_s9.sh rc 1 inside the
  lock, nothing installed): S10 stands until a lead item names the new sha.  This link does not change INST_WANT, BIN_U or the
  u binary line (the U arms run the pinned copy C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe by sha) - decisions of the lead.
""",
     """- Item 374 (g) (FS3d HPP-450; the lead comment 088c2da9 to this link): FS3 installed 2026-10-03T07:11:12Z, the admission row
  installed_before = 540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1 - INST_WANT of go_s9.sh and a constant of
  its own INST_WANT of sc_s9.py; the u binary line and BIN_U (the pinned copy C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe by sha)
  do not change - the binary of the u arms and the installed binary are different constants.
- Item 377 (the review of S9b, rework 1): (b) seal 06 is not changed, this edition 06b replaces it; fixtures of both outcomes
  (sc_s9: A3, F7, F7b - 540c035a passes, 4aa62e95 fails that row only; go_s9: G23, GL1, GL5b, GL10, GL12, GL12b - the installed
  = INST_WANT runs the arm with the s / u binary and returns the installed build, the installed = the u stand-in -> rc 1 inside
  the lock, nothing installed); mutants --only of the row, the constants and the seal path (section 5), the counted full run of
  S9b not repeated.  (v) "< 2 failing" of item 371 (v) = failing S-cat MEMBERS - the executor variant above is the letter; the
  other reading stays a reference line with "DIFFERS (a failing arm without a screen measure)" and gives no word; the scorer
  code does not change by (v).
"""),
]


def rep(t, reps, name):
    for a, b in reps:
        if b is None:
            continue
        n = t.count(a)
        if n != 1:
            raise SystemExit('NO MATCH (%d) in %s: %r' % (n, name, a[:120]))
        t = t.replace(a, b)
    t.encode('ascii')
    return t


def main():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCKED or STOP')
        return 5
    os.makedirs(O, exist_ok=True)
    jobs = (('sc_s9.py', SC, 'sc_s9.py'), ('go_s9.sh', GO, 'go_s9.sh'), ('test_sc_s9.py', TSC, 'test_sc_s9.py'),
            ('test_go_s9.py', TGO, 'test_go_s9.py'), ('mut_sc_s9.py', MUT, 'mut_sc_s9.py'),
            ('mkseal_s06.py', MK, 'mkseal_s06b.py'), ('seal06_body.md', BODY, 'seal06b_body.md'),
            ('seal06_tail.md', TAIL, 'seal06b_tail.md'))
    out = []
    for src, reps, dst in jobs:
        t = open(D + src, 'rb').read().decode('ascii')
        assert '\r' not in t, src
        out.append((dst, rep(t, reps, src)))
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCKED or STOP')
        return 5
    for src, _, dst in jobs:
        if src == dst and not os.path.exists(O + src):
            shutil.copy2(D + src, O + src)
    for src in ('test_sc_s9.out.txt', 'test_go_s9.out.txt', 'regress_s9.out.txt'):
        if not os.path.exists(O + src):
            shutil.copy2(D + src, O + src)
    for dst, t in out:
        open(D + dst, 'wb').write(t.encode('ascii'))
        print('written', dst)
    return 0


if __name__ == '__main__':
    sys.exit(main())
