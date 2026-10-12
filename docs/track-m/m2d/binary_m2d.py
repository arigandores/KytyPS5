"""M2d (HPP-841, ROADMAP s122 items 756(g), 762(v)): strings of the MS1 exe against the FS15 copy bfac84be (port of
f287/fs15a/binary_fs15a.py). Members: the knob names and log formats of the seven MS1 themes and of T256/T306 (code in
MS1, default 0) present once in MS1 and absent in FS15; the base markers of FS15 (F20, F24, F29, F25, F21, B12) present in
both; translation source hash: MS1 has its own (from kytyGitVersion.h), not FS15's 9177b426; the MS1 version string twice
in MS1, the FS15 one twice in FS15. Prints the table and ALL OK / FAIL.
    python binary_m2d.py <MS1 exe> <FS15 exe> <MS1 version string> <MS1 shader source hash>"""
import hashlib
import sys

ms1, fs15, ver, shash = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
a, b = open(ms1, 'rb').read(), open(fs15, 'rb').read()
print('MS1  %s sha256 %s' % (ms1, hashlib.sha256(a).hexdigest()))
print('FS15 %s sha256 %s' % (fs15, hashlib.sha256(b).hexdigest()))
# (string, want in MS1, want in FS15)
MARKS = [('MWave1: mask=', 1, 0), ('MTexOffset:', None, 0), ('MT265: mode=', 1, 0), ('MT272: mode=', 1, 0),
         ('MT231: mode=', 1, 0)] + \
        [('KYTY_M_' + t, 1, 0) for t in ('T234', 'T233', 'T256', 'T306', 'T032', 'T203', 'T265', 'T272', 'T231')] + \
        [('FixF20: mode=', 'eq', 'eq'), ('KYTY_FIX_F20', 'eq', 'eq'), ('FixF24: mode=', 'eq', 'eq'), ('FixF29: mode=', 'eq', 'eq'),
         ('FixF25: mode=', 'eq', 'eq'), ('FixF21: mode=', 'eq', 'eq'), ('FixB12: mode=', 'eq', 'eq'), ('KYTY_S_REPLAY', 'eq', 'eq'),
         ('KYTY_DIAG_F47DT', 0, 0), ('KYTY_DIAG_B32', 0, 0), ('KYTY_F26_TINT', 0, 0),
         (shash, 1, 0), ('9177b4267de1fb8bac7d1113afd8733210addfac', 0, 1), (ver, 2, 0),
         ('KytyPS5-2026-09-15-6a2987a-1929-g6beb3b73', 0, 2)]
ok = True
for s, wa, wb in MARKS:
    na, nb = a.count(s.encode()), b.count(s.encode())
    if wa == 'eq':  # base marker of FS15: the same count in both, >= 1 (edition 2; edition 1 wanted x1 - KYTY_S_REPLAY is x2)
        good = na == nb >= 1
    else:
        good = (wa is None or na == wa) and (wb is None or nb == wb)
    ok &= good
    print('%s %-45s MS1 x%d FS15 x%d%s' % ('OK  ' if good else 'FAIL', s, na, nb, '' if wa is not None else ' (reference)'))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
