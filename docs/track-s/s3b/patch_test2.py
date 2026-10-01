"""S3b (HPP-325): test_sc_s.py - H20c: the restore-of-GLCache row alone (man_launch_glc follows the bad got, so the RC10 row
does not mask it; the survivor cr_glc_got of the first full mutant run).  Writes LF."""
from pathlib import Path

P = Path('C:/kyty/s288/test_sc_s.py')
t = P.read_bytes().decode('ascii').replace('\r\n', '\n')
A = ("mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), cj={})\n"
     "ok &= case('H21 an empty cache json -> FAIL'")
B = ("mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), cj=cj_for('sw_m2', restore_glc=dict(expected=SNAP_DRV, got='00' * 32),\n"
     "                                                           man_launch_glc=dict(sha='00' * 32)))\n"
     "r = arm('sw_m2')\n"
     "ok &= case('H20c GLCache not at snap0_drv while man_launch_glc = restore_glc.got (RC10 row clean) -> the restore of '\n"
     "           'GLCache row FAIL alone', [x for x in r['fail'] if x.startswith('admission')] != [] and\n"
     "           all('restore of GLCache' in x for x in r['fail'] if x.startswith('admission')))\n" + A)
assert t.count(A) == 1
P.write_bytes(t.replace(A, B).encode('ascii'))
print('patched')
