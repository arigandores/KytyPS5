"""S3b (HPP-325): test_sc_s.py - fixtures on the edges the --only pre-run left alive (cr_bin_len, cr_bin_none, ua_ser).
Writes LF."""
from pathlib import Path

P = Path('C:/kyty/s288/test_sc_s.py')
t = P.read_bytes().decode('ascii').replace('\r\n', '\n')

A1 = "f, s, fi = fz([(999999, {}), (16000, {})], attr=True)\nok &= case('D14h RC8 edge"
B1 = ("post = [(1100000, dict(held=1)), (16000, {})]\n"
      "f, s, fi = fz(post, attr=True)\n"
      "ok &= case('D14g2 RC8 edge: a series of gap 1 116 000 with no PRIO row (gap_pipe 1 116 000 >= 1 s) is attributed, '\n"
      "           'NOT a not attributed series', S.unattributed(f, True, 1000000)['series'] == 0 and\n"
      "           S.attributed(f, True, 1000000) == 1)\n" + A1)
A2 = ("mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), cj={})\n"
      "ok &= case('H21 an empty cache json -> FAIL'")
B2 = ("for over, label in ((dict(installed_before={}, installed_after={}), 'neither installed_before nor installed_after '\n"
      "                      '(None = None is not a return)'),\n"
      "                     (dict(installed_before=dict(sha='ab'), installed_after=dict(sha='ab')),\n"
      "                      'installed_before = installed_after but not a sha256')):\n"
      "    mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), cj=cj_for('sw_m2', **over))\n"
      "    ok &= case('H20b RC1 edge: %s -> the binary row FAIL' % label,\n"
      "               any(x.startswith('admission') and 'installed binary' in x for x in arm('sw_m2')['fail']))\n" + A2)
for a, b in ((A1, B1), (A2, B2)):
    assert t.count(a) == 1, a[:40]
    t = t.replace(a, b)
P.write_bytes(t.encode('ascii'))
print('patched')
