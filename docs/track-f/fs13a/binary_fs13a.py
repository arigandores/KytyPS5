"""FS13a (HPP-787): strings of the FS13 exe against the FS12 copy 46892c20 (reference: F25 present only in FS13; the base
markers and the translation signature equal; diagnostics outside the base absent). The version string is
embedded twice in each exe (first run expected 1 - corrected to 2 after the first run, the FS12 copy has 2 as well). Prints the table and ALL OK / FAIL.
    python binary_fs13a.py <FS13 exe> <FS12 exe>"""
import hashlib
import sys

fs13, fs12 = sys.argv[1], sys.argv[2]
a, b = open(fs13, 'rb').read(), open(fs12, 'rb').read()
print('FS13 %s sha256 %s' % (fs13, hashlib.sha256(a).hexdigest()))
print('FS12 %s sha256 %s' % (fs12, hashlib.sha256(b).hexdigest()))
# (string, want in FS13, want in FS12); None - reference only
MARKS = [('KYTY_FIX_F25', 1, 0), ('FixF25: mode=', 1, 0), ('FixF25: read failed twice', 1, 0),
         ('KYTY_FIX_F21', 1, 1), ('FixF21: mode=', 1, 1), ('KYTY_FIX_B12', 1, 1), ('FixB12: mode=', 1, 1),
         ('KYTY_FIX_B13', 1, 1), ('KYTY_FIX_B36', 1, 1), ('KYTY_FIX_B4', None, None), ('FixB4: mode=', 1, 1),
         ('KYTY_FIX_F24', 0, 0), ('FixF24:', 0, 0), ('KYTY_FIX_F20', 0, 0), ('KYTY_DIAG_B32', 0, 0), ('rts_bad_b', 0, 0),
         ('9177b4267de1fb8bac7d1113afd8733210addfac', 1, 1), ('KytyPS5-2026-09-15-6a2987a-1919-gea6c6e9e', 2, 0),
         ('KytyPS5-2026-09-15-6a2987a-1914-g730ed40a', 0, 2)]
ok = True
for s, w13, w12 in MARKS:
    n13, n12 = a.count(s.encode()), b.count(s.encode())
    good = (w13 is None or n13 == w13) and (w12 is None or n12 == w12)
    ok &= good
    print('%s %-45s FS13 x%d FS12 x%d%s' % ('OK  ' if good else 'FAIL', s, n13, n12, '' if w13 is not None else ' (reference)'))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
