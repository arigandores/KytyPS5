"""S13a4: Y5 reads the seal PENDING through nopb_data directly (score_arm is not run on a PENDING seal - go_s13.sh refuses every
tag then)."""
p = 'C:/kyty/s288/s13/test_sc_s13.py'
s = open(p, 'rb').read().decode('ascii')
BS = chr(92)
a = "rp = S.score_arm('k_01', ROOT, PRED_SHA, PRED, ('PENDING', None, None))\n"
b = ("lp1 = str(Path(ROOT) / 'log_k_01.txt')\n"
     "rp = dict(nopb=S.nopb_data(S.A.scan_s(lp1), S.scan_y(lp1), ('PENDING', None, None)), prep_end={})\n")
a2 = "any(x.endswith('(executor" + BS + "'s addition): n/a') for x in S.fmt_arm(rp)))"
b2 = "S.fmt_nopb(rp).endswith('(executor" + BS + "'s addition): n/a') and rp['nopb']['text'] == NOPB_SL)"
for x, y in ((a, b), (a2, b2)):
    assert s.count(x) == 1, (s.count(x), x)
    s = s.replace(x, y)
open(p, 'wb').write(s.encode('ascii'))
print('fix_y5 ok')
