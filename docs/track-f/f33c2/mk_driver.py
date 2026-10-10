"""F33c2 (HPP-748): makes run_stand_f33c2.py from the F33c driver docs/track-f/f33c/run_stand_f33c.py (a4212bed) - BASE ->
C:/kyty/f287/f33c2, arm CN allowed, field nested_fatal (count of 'ExitFatal: nested_fatal' lines). No other change."""
import sys

src, dst = sys.argv[1], sys.argv[2]
t = open(src, 'rb').read().decode('utf-8').replace('\r\n', '\n')


def rep(old, new):
    global t
    assert t.count(old) == 1, ('anchor', old[:60], t.count(old))
    t = t.replace(old, new)


rep('"""F33c (HPP-744; ROADMAP s122 item 675(d)(1)): driver of the stand KYTY_TEST_EXITFATAL edition 2.\n',
    '# F33c2 (HPP-748; ROADMAP s122 item 681(v)(1)-(3)): copy of docs/track-f/f33c/run_stand_f33c.py (a4212bed) made by\n'
    '# mk_driver.py - BASE -> C:/kyty/f287/f33c2, arm CN (stand edition 3), field nested_fatal; no other change.\n'
    '"""F33c (HPP-744; ROADMAP s122 item 675(d)(1)): driver of the stand KYTY_TEST_EXITFATAL edition 2.\n')
rep("    python run_stand_f33c.py <arm P2|R2|G|C|N|H|HG> <seed_from>",
    "    python run_stand_f33c2.py <arm P2|R2|G|C|N|H|HG|CN> <seed_from>")
rep('  k1        - crash or hang or second or cut or expired>0\n',
    '  k1        - crash or hang or second or cut or expired>0\n'
    '  nested_fatal - (edition 3, arm CN) number of \'ExitFatal: nested_fatal\' lines (the second fatal of the injector\n'
    '              inside its own walk); dur_s - wall seconds of the trial (the driver\'s clock)\n')
rep("BASE = 'C:/kyty/f287/f33c'\n", "BASE = 'C:/kyty/f287/f33c2'\n")
rep("'wait_done', 'expired_seen', 'trig_waited_us', 'h_dt_s', 'fatal_text', 'abort', 'crash', 'k1', 'leftover',\n          'utc']",
    "'wait_done', 'expired_seen', 'trig_waited_us', 'h_dt_s', 'fatal_text', 'abort', 'crash', 'k1', 'leftover',\n          'nested_fatal', 'utc']")
rep("'trig_waited_us': '', 'guest_enter_e_us': None}",
    "'trig_waited_us': '', 'guest_enter_e_us': None, 'nested_fatal': 0}")
rep("        elif kind == 'trigger':\n",
    "        elif kind == 'nested_fatal':\n            r['nested_fatal'] += 1\n        elif kind == 'trigger':\n")
rep("    if arm not in ('P2', 'R2', 'G', 'C', 'N', 'H', 'HG'):\n",
    "    if arm not in ('P2', 'R2', 'G', 'C', 'N', 'H', 'HG', 'CN'):\n")
open(dst, 'wb').write(t.encode('utf-8'))
print('driver written', dst)
