"""M6a3: run_stand_m6a3.py from run_stand_m6a2.py - exact substitutions, each must match once."""
SRC = 'C:/kyty/KytyPS5/docs/track-m/m6a2/run_stand_m6a2.py'
DST = 'C:/kyty/KytyPS5/docs/track-m/m6a3/run_stand_m6a3.py'
t = open(SRC, 'rb').read().decode('utf-8')
NL = chr(10)
subs = [
    ('"""Track M, M6a2 (HPP-854, ROADMAP s122 item 770(b)-(e)): copy of m6a/run_stand_m6a.py with the M6a2 expectations.' + NL,
     '"""Track M, M6a3 (HPP-856, ROADMAP s122 item 772(v), (g)): copy of m6a2/run_stand_m6a2.py with the M6a3 expectations:' + NL +
     'pure 128 of 128 (new cases ao_obj_vq_nz, ao_obj_vq_zero - private commit; ao_obj_noaccess, ao_obj_guard; clr_r8_hi_div8' + NL +
     '0x34121212; ao_obj_vq 0 on the storage and 0x1000 cases), M5W2Stat with ao_obj_vq last, audio 5 of 5 (push 5 - private commit).' + NL +
     'Was: Track M, M6a2 (HPP-854, ROADMAP s122 item 770(b)-(e)): copy of m6a/run_stand_m6a.py with the M6a2 expectations.' + NL),
    ("        if not (e['total'] == '103' and e['match'] == '103'):" + NL +
     "            fails.append('pure: match %s of %s (want 103 of 103)' % (e['match'], e['total']))",
     "        if not (e['total'] == '128' and e['match'] == '128'):" + NL +
     "            fails.append('pure: match %s of %s (want 128 of 128)' % (e['match'], e['total']))"),
    ("want_stat = dict(pushes='1', ao_obj_push='5', ao_obj_nz='2', ao_obj_nopcm='1', ao_bus_push='2', ao_bus_nz='1'," + NL +
     "                     clr_dw='12',",
     "want_stat = dict(pushes='1', ao_obj_push='9', ao_obj_nz='3', ao_obj_nopcm='1', ao_bus_push='2', ao_bus_nz='1'," + NL +
     "                     clr_dw='13',"),
    ("minlod_div_x='1', clr_dw_div8='2', ao_obj_unread='1', inv_part_src='2')",
     "minlod_div_x='1', clr_dw_div8='3', ao_obj_unread='3', inv_part_src='2', ao_obj_vq='2')"),
    ("'9': ('2', '0', '1')", "'9': ('3', '0', '2')"),
    ("e['total'] == '4' and e['match'] == '4'", "e['total'] == '5' and e['match'] == '5'"),
]
for old, new in subs:
    n = t.count(old)
    assert n == 1, (n, old[:80])
    t = t.replace(old, new, 1)
# the stat line must end with ao_obj_vq (field order: the new field is last)
old = "        s = kv(stat[0])" + NL
new = ("        s = kv(stat[0])" + NL +
       "        if not stat[0].rstrip().endswith(' inv_part_src=%s ao_obj_vq=%s' % (want_stat['inv_part_src'], want_stat['ao_obj_vq'])):" + NL +
       "            fails.append('pure: M5W2Stat does not end with inv_part_src= ao_obj_vq=')" + NL)
assert t.count(old) == 1
t = t.replace(old, new, 1)
open(DST, 'wb').write(t.encode('utf-8'))
print('ALL OK')
