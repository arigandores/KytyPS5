"""FS15a (HPP-820, ROADMAP s122 item 730(g)(1)): strings of the FS15 exe against the FS14 copy 013e1974 (port of
binary_fs14a_f29.py). Member: one string of the format "FixF20: mode=" and one of "FixF20Stat:" in FS15 (0 in FS14).
Reference: the F20 knob present only in FS15; the base markers (F24, F29, F25, F21, B12, B13, B36, B4) and the translation
signature equal; diagnostics outside the base (KYTY_DIAG_B32, rts_bad_b, KYTY_F26_TINT, KYTY_FIX_F26) absent; the version
string embedded twice. Prints the table and ALL OK / FAIL.
    python binary_fs15a.py <FS15 exe> <FS14 exe> <FS15 version string>"""
import hashlib
import sys

fs15, fs14, ver = sys.argv[1], sys.argv[2], sys.argv[3]
a, b = open(fs15, 'rb').read(), open(fs14, 'rb').read()
print('FS15 %s sha256 %s' % (fs15, hashlib.sha256(a).hexdigest()))
print('FS14 %s sha256 %s' % (fs14, hashlib.sha256(b).hexdigest()))
# (string, want in FS15, want in FS14); None - reference only
MARKS = [('FixF20: mode=', 1, 0), ('FixF20Stat:', 1, 0), ('KYTY_FIX_F20', 1, 0),
         ('FixF24: init_owner', 1, 1), ('FixF24: mode=', 1, 1), ('KYTY_FIX_F24', 1, 1),
         ('FixF29: mode=', 1, 1), ('KYTY_FIX_F29', 1, 1), ('FixF29: overflow', 1, 1),
         ('KYTY_FIX_F25', 1, 1), ('FixF25: mode=', 1, 1), ('FixF25: read failed twice', 1, 1),
         ('KYTY_FIX_F21', 1, 1), ('FixF21: mode=', 1, 1), ('KYTY_FIX_B12', 1, 1), ('FixB12: mode=', 1, 1),
         ('KYTY_FIX_B13', 1, 1), ('KYTY_FIX_B36', 1, 1), ('FixB4: mode=', 1, 1), ('KYTY_FIX_B24', None, None),
         ('KYTY_DIAG_B32', 0, 0), ('rts_bad_b', 0, 0), ('KYTY_F26_TINT', 0, 0), ('KYTY_FIX_F26', 0, 0),
         ('F20Stand', 0, 0), ('KYTY_TEST_F20STAND', 0, 0),
         ('9177b4267de1fb8bac7d1113afd8733210addfac', 1, 1), (ver, 2, 0),
         ('KytyPS5-2026-09-15-6a2987a-1925-geb7e8b91', 0, 2)]
ok = True
for s, w15, w14 in MARKS:
    n15, n14 = a.count(s.encode()), b.count(s.encode())
    good = (w15 is None or n15 == w15) and (w14 is None or n14 == w14)
    ok &= good
    print('%s %-45s FS15 x%d FS14 x%d%s' % ('OK  ' if good else 'FAIL', s, n15, n14, '' if w15 is not None else ' (reference)'))
i = a.find(b'FixF20Stat:')
print('context of FixF20Stat: in FS15: %r' % a[i:i + 110] if i >= 0 else 'FixF20Stat: absent')
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
