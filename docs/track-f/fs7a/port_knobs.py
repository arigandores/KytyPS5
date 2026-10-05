# FS7a (HPP-565): knobs_fs7a.py = knobs_fs6a.py with the expected set + KYTY_FIX_F8 (item 467(g)(1)) + KYTY_FIX_B24
# (item 487(g)(1)); one header line added. LF output.
import sys
NL = chr(10)
t = open('C:/kyty/f287/fs6a/knobs_fs6a.py', 'rb').read().decode('utf-8').replace('\r\n', NL)
old = '"KYTY_S_PCW", "KYTY_FIX_B4"}'
new = '"KYTY_S_PCW", "KYTY_FIX_B4", "KYTY_FIX_F8", "KYTY_FIX_B24"}'
old2 = '+ p.408(l) + p.454(g)(1)):'
new2 = '+ p.408(l) + p.454(g)(1) + p.467(g)(1) + p.487(g)(1)):'
for o in (old, old2):
    if t.count(o) != 1:
        print('REPLACE FAIL', o)
        sys.exit(1)
t = t.replace(old, new).replace(old2, new2)
head = '# FS7a (HPP-565, ROADMAP s122 p.467(g)(1), 487(g)(1)): copy of knobs_fs6a.py, the expected set + KYTY_FIX_F8 and KYTY_FIX_B24 (base FS6a 3904522d: eleven names). Was:'
open('C:/kyty/f287/fs7a/knobs_fs7a.py', 'wb').write((head + NL + t).encode('utf-8'))
print('PORT OK')
