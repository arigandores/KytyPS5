# FS7a (HPP-565, ROADMAP s122 items 467(g)(1), 487(g)(1)): ports of the stand drivers to the FS7 defaults (KYTY_FIX_F8 and
# KYTY_FIX_B24 unset = ON). Text replacements on whole lines, each must hit exactly the expected count (else exit 1);
# a header line naming the port is put first; LF output (write_bytes). Sources: docs/track-f/f18c/run_stand_f18c.py,
# docs/track-f/f19c/run_stand_f19c.py, docs/track-f/f19c2/run_stand_f19c2.py (main), next_cycle.py and gate_free.py of
# F19c2 copied verbatim.
import sys

REPO = 'C:/kyty/KytyPS5/docs/track-f/'
DST = 'C:/kyty/f287/fs7a/'
NL = chr(10)


def port(src, dst, head, reps):
    t = open(REPO + src, 'rb').read().decode('utf-8').replace('\r\n', NL)
    for old, new, cnt in reps:
        n = t.count(old)
        if n != cnt:
            print('REPLACE FAIL %s: %r found %d, expected %d' % (src, old[:60], n, cnt))
            sys.exit(1)
        t = t.replace(old, new)
    open(DST + dst, 'wb').write((head + NL + t).encode('utf-8'))
    print('ported %s -> %s (%d replacements)' % (src, dst, len(reps)))


F8_PLAN_OLD = NL.join([
    'plan = [',
    "    lambda: direct('i_disk3_fix0', 'disk', 3, 'dev_', '0', 3, 3),",
    "    lambda: direct('i_dummy1_fix0', 'dummy', 1, None, '0', 1, 1),",
    "    lambda: direct('i_dummy3_fix0', 'dummy', 3, None, '0', 1, 3),",
    "    lambda: direct('i_disk3_unset', 'disk', 3, 'dev_', 'unset', 3, 3),",
    "    lambda: acquire('ii_disk3_fix1', 'disk', 3, 'dev_'),",
    "    lambda: acquire('ii_dummy1_fix1', 'dummy', 1, None),",
    "    lambda: threads('iii_dummy1_fix1', 'dummy', 1, None),",
    "    lambda: threads('iii_disk3_fix1', 'disk', 3, 'dev_'),",
    "    lambda: direct_fix1('i_disk3_fix1', 'disk', 3, 'dev_', 3),",
    "    lambda: direct_fix1('i_dummy1_fix1', 'dummy', 1, None, 1),",
    ']',
])
F8_PLAN_NEW = NL.join([
    '# FS7a members (item 467(g)(1), reading of item 448(b): disk x 3): KYTY_FIX_F8=0 - control (i); unset - the =1',
    '# expectations of (ii) and (iii); unset (i) in the =1 form - reference.',
    'plan = [',
    "    lambda: direct('i_disk3_fix0', 'disk', 3, 'dev_', '0', 3, 3),",
    "    lambda: acquire('ii_disk3_unset', 'disk', 3, 'dev_', 'unset'),",
    "    lambda: threads('iii_disk3_unset', 'disk', 3, 'dev_', 'unset'),",
    "    lambda: direct_fix1('i_disk3_unset', 'disk', 3, 'dev_', 3, 'unset'),",
    ']',
])

port('f18c/run_stand_f18c.py', 'run_stand_fs7a_f8.py',
     '# FS7a (HPP-565): port of run_stand_f18c.py - the =1 cases take the fix value (unset = the FS7 default ON); plan of the FS7a members; output stand_fs7a_f8.txt. Was:',
     [('def direct_fix1(name, driver, ndev, prefix, opened):', "def direct_fix1(name, driver, ndev, prefix, opened, fix='1'):", 1),
      ('def acquire(name, driver, ndev, prefix):', "def acquire(name, driver, ndev, prefix, fix='1'):", 1),
      ('def threads(name, driver, ndev, prefix):', "def threads(name, driver, ndev, prefix, fix='1'):", 1),
      ("    kv = run(name, args, driver, '1')", '    kv = run(name, args, driver, fix)', 3),
      (F8_PLAN_OLD, F8_PLAN_NEW, 1),
      ("'stand_f18c.txt'", "'stand_fs7a_f8.txt'", 1)])

B24_PLAN_OLD = NL.join([
    'plan = [',
    "    lambda: case_i('i_fix0', '0'),",
    "    lambda: case_i('i_unset', 'unset'),",
    "    lambda: case_ii('ii_fix1', '1'),",
    "    lambda: case_iii('iii_fix1'),",
    "    lambda: case_i('i_fix1', '1'),",
    "    lambda: case_ii('ii_fix0', '0'),",
    "    lambda: case_iii('iii_fix1_b'),",
    ']',
])
B24_PLAN_NEW = NL.join([
    '# FS7a members (item 487(g)(1)): KYTY_FIX_B24=0 - control (i); unset - the =1 expectations of (ii) and (iii);',
    '# unset (i) in the =1 form and (ii) at =0 - reference.',
    'plan = [',
    "    lambda: case_i('i_fix0', '0'),",
    "    lambda: case_ii('ii_unset', 'unset'),",
    "    lambda: case_iii('iii_unset', 'unset'),",
    "    lambda: case_i('i_unset', 'unset'),",
    "    lambda: case_ii('ii_fix0', '0'),",
    "    lambda: case_iii('iii_unset_b', 'unset'),",
    ']',
])

port('f19c/run_stand_f19c.py', 'run_stand_fs7a_b24.py',
     '# FS7a (HPP-565): port of run_stand_f19c.py - unset reads as the FS7 default ON (=1 expectations); case iii takes the fix value; plan of the FS7a members; output stand_fs7a_b24.txt. Was:',
     [("    fix1 = fix == '1'", "    fix1 = fix in ('1', 'unset')", 2),
      ('def case_iii(name):', "def case_iii(name, fix='1'):", 1),
      ("    kv = run(name, 'iii', '1')", "    kv = run(name, 'iii', fix)", 1),
      (B24_PLAN_OLD, B24_PLAN_NEW, 1),
      ("'stand_f19c.txt'", "'stand_fs7a_b24.txt'", 1)])

port('f19c2/run_stand_f19c2.py', 'run_stand_fs7a_b24dd.py',
     '# FS7a (HPP-565): port of run_stand_f19c2.py - dd runs without KYTY_FIX_B24 (FS7 default ON), trig runs unset and 0 (unset reads as =1); output trig_fs7a.txt. Was:',
     [("    env['KYTY_FIX_B24'] = fix", "    if fix != 'unset':" + NL + "        env['KYTY_FIX_B24'] = fix", 1),
      ("        kv, out = run(exe, 'dd', '1', cwd)", "        kv, out = run(exe, 'dd', 'unset', cwd)", 1),
      ("    for fix in ['1', '0']:", "    for fix in ['unset', '0']:", 1),
      ("            fix1 = fix == '1'", "            fix1 = fix != '0'", 1),
      ("                ('fix_b24 %s' % fix, num(kv, 'fix_b24') == int(fix)),",
       "                ('fix_b24 %s' % fix, num(kv, 'fix_b24') == (1 if fix1 else 0)),", 1),
      ("'trig_f19c2.txt'", "'trig_fs7a.txt'", 1)])

for f in ('next_cycle.py', 'gate_free.py'):
    open(DST + f, 'wb').write(open(REPO + 'f19c2/' + f, 'rb').read().replace(b'\r\n', b'\n'))
    print('copied', f)
print('PORT OK')
