# FS4a (HPP-470, ROADMAP s122 item 378(g)(1)): knobs_fs4a.py = knobs_fs3a.py with the expected set + KYTY_FIX_SVAL.
NL = chr(10)
s = open('C:/kyty/f287/fs3/fs3a/knobs_fs3a.py', encoding='utf-8').read().replace('\r\n', '\n')
old_e = 'expected = {"KYTY_FIX_B26", "KYTY_FIX_B1B", "KYTY_FIX_DUALSRC", "KYTY_FIX_MINIMIZE", "KYTY_FIX_B9A", "KYTY_FIX_B42"}'
assert s.count(old_e) == 1
s = s.replace(old_e, old_e[:-1] + ', "KYTY_FIX_SVAL"}')
old_p = 'print("expected (p.298(v) + p.327(g) + p.367(g)(1)):"'
assert s.count(old_p) == 1
s = s.replace(old_p, 'print("expected (p.298(v) + p.327(g) + p.367(g)(1) + p.378(g)(1)):"')
old_h = '# FS3a (HPP-447, ROADMAP s122 p.367(g)(1)): copy of knobs_fs2a.py, the expected set + KYTY_FIX_B42. Was:'
assert s.count(old_h) == 1
s = s.replace(old_h, '# FS4a (HPP-470, ROADMAP s122 p.378(g)(1)): copy of knobs_fs3a.py, the expected set + KYTY_FIX_SVAL. Was:' + NL + old_h)
open('C:/kyty/f287/fs4/fs4a/knobs_fs4a.py', 'wb').write(s.encode('utf-8'))
print('ok')
