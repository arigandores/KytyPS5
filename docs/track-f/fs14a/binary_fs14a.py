"""FS14a (HPP-812, ROADMAP s122 item 710(g)(1)): strings of the FS14 exe against the FS13 copy abab2196 (port of
binary_fs13a.py). Member: one string of the format "FixF24: init_owner" and one of "TestHidLoss: f24" in FS14 (0 in FS13).
Reference: F24 knob and lines present only in FS14; the base markers (F25, F21, B12, B13, B36, B4) and the translation
signature equal; diagnostics outside the base (F20, KYTY_DIAG_B32, rts_bad_b) absent; the version string embedded twice.
Prints the table and ALL OK / FAIL.
    python binary_fs14a.py <FS14 exe> <FS13 exe> <FS14 version string>"""
import hashlib
import sys

fs14, fs13, ver = sys.argv[1], sys.argv[2], sys.argv[3]
a, b = open(fs14, 'rb').read(), open(fs13, 'rb').read()
print('FS14 %s sha256 %s' % (fs14, hashlib.sha256(a).hexdigest()))
print('FS13 %s sha256 %s' % (fs13, hashlib.sha256(b).hexdigest()))
# (string, want in FS14, want in FS13); None - reference only
MARKS = [('FixF24: init_owner', 1, 0), ('TestHidLoss: f24', 1, 0),
         ('KYTY_FIX_F24', 1, 0), ('FixF24: mode=', 1, 0), ('FixF24: pump_stop_expired', 1, 0),
         ('FixF24: open failed', None, 0), ('FixF24: pump_update_long', None, 0), ('KYTY_TEST_HIDLOSS', None, None),
         ('KYTY_FIX_F25', 1, 1), ('FixF25: mode=', 1, 1), ('FixF25: read failed twice', 1, 1),
         ('KYTY_FIX_F21', 1, 1), ('FixF21: mode=', 1, 1), ('KYTY_FIX_B12', 1, 1), ('FixB12: mode=', 1, 1),
         ('KYTY_FIX_B13', 1, 1), ('KYTY_FIX_B36', 1, 1), ('FixB4: mode=', 1, 1), ('KYTY_FIX_B24', None, None),
         ('KYTY_FIX_F20', 0, 0), ('KYTY_DIAG_B32', 0, 0), ('rts_bad_b', 0, 0),
         ('9177b4267de1fb8bac7d1113afd8733210addfac', 1, 1), (ver, 2, 0),
         ('KytyPS5-2026-09-15-6a2987a-1919-gea6c6e9e', 0, 2)]
ok = True
for s, w14, w13 in MARKS:
    n14, n13 = a.count(s.encode()), b.count(s.encode())
    good = (w14 is None or n14 == w14) and (w13 is None or n13 == w13)
    ok &= good
    print('%s %-45s FS14 x%d FS13 x%d%s' % ('OK  ' if good else 'FAIL', s, n14, n13, '' if w14 is not None else ' (reference)'))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
