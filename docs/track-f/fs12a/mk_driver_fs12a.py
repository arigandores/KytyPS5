# FS12a (HPP-750, ROADMAP s122 item 683(g)(1)): makes run_stand_fs12a.py from docs/track-f/f33c2/run_stand_f33c2.py
# (66ec6149 / a4212bed form): BASE -> C:/kyty/f287/fs12a; --fix takes 'd' besides 0/1 - 'd' = the default: KYTY_FIX_F21
# is removed from the environment (not set), the TSV goes to <out>/fixd/; nothing else changes (arms, fields, classes).
import sys

SRC = 'C:/kyty/KytyPS5/docs/track-f/f33c2/run_stand_f33c2.py'
DST = sys.argv[1]
t = open(SRC, 'rb').read().decode('utf-8').replace('\r\n', '\n')
edits = [
    ("BASE = 'C:/kyty/f287/f33c2'\n", "BASE = 'C:/kyty/f287/fs12a'\n"),
    ("    if fix not in ('0', '1'):\n        sys.exit('--fix 0|1 is required')\n",
     "    if fix not in ('0', '1', 'd'):\n        sys.exit('--fix 0|1|d is required')\n"),
    ("    env['KYTY_FIX_F21'] = fix\n",
     "    if fix != 'd':  # FS12a: 'd' - the default, KYTY_FIX_F21 not set (removed above with every KYTY_*)\n"
     "        env['KYTY_FIX_F21'] = fix\n"),
]
for old, new in edits:
    assert t.count(old) == 1, old
    t = t.replace(old, new)
head = ('# FS12a (HPP-750; ROADMAP s122 item 683(g)(1)): copy of docs/track-f/f33c2/run_stand_f33c2.py made by\n'
        '# mk_driver_fs12a.py - BASE -> C:/kyty/f287/fs12a, --fix d = KYTY_FIX_F21 not set (the FS12 default); no other change.\n'
        '# Was:\n')
open(DST, 'w', encoding='utf-8', newline='\n').write(head + t)
print('written', DST)
