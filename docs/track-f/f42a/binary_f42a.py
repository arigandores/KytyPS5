"""F42a (HPP-779, ROADMAP s122 item 694(g)(2), (z)): strings of the F42a tag exe against the FS12 copy 46892c20 (copy of
the FS13a binary_fs13a.py with the marks changed): F20 present only in the tag exe; the FS12 markers and the translation
signature 9177b426 equal; markers of rows not in the base (F25, F24, diagnostics) absent. Prints the table and
ALL OK / FAIL.   python binary_f42a.py <tag exe> <FS12 exe>"""
import hashlib
import sys

tag, fs12 = sys.argv[1], sys.argv[2]
a, b = open(tag, 'rb').read(), open(fs12, 'rb').read()
print('TAG  %s sha256 %s' % (tag, hashlib.sha256(a).hexdigest()))
print('FS12 %s sha256 %s' % (fs12, hashlib.sha256(b).hexdigest()))
# (string, want in tag, want in FS12); None - reference only
MARKS = [('KYTY_FIX_F20', 1, 0), ('FixF20: mode=', 1, 0), ('FixF20Stat:', 1, 0),
         ('KYTY_FIX_F21', 1, 1), ('FixF21: mode=', 1, 1), ('KYTY_FIX_B12', 1, 1), ('FixB12: mode=', 1, 1),
         ('KYTY_FIX_B13', 1, 1), ('KYTY_FIX_B36', 1, 1), ('KYTY_FIX_B4', None, None), ('FixB4: mode=', 1, 1),
         ('KYTY_FIX_F25', 0, 0), ('FixF25: mode=', 0, 0), ('KYTY_FIX_F24', 0, 0), ('FixF24:', 0, 0),
         ('KYTY_FIX_F29', 0, 0), ('KYTY_DIAG_B32', 0, 0), ('rts_bad_b', 0, 0),
         ('9177b4267de1fb8bac7d1113afd8733210addfac', 1, 1),
         # version of main.cpp (kytyGitVersion.h, regenerated at every build) - NUL-delimited
         ('\x00KytyPS5-2026-09-15-6a2987a-1916-g26283087\x00', 1, 0),
         ('\x00KytyPS5-2026-09-15-6a2987a-1914-g730ed40a\x00', 0, 1),
         # SDL_REVISION of 3rdparty/SDL2 - fixed at the configure of the build folder (the worktree was configured at
         # 730ed40a before the cherry-picks; SDL sources are not changed by F42a); first run expected the version x2 in
         # the tag exe - corrected after the first run (FAIL x1/x1), the string is read here as the configure revision
         ('SDL-KytyPS5-2026-09-15-6a2987a-1914-g730ed40a\x00', 1, 1)]
ok = True
for s, wt, w12 in MARKS:
    nt, n12 = a.count(s.encode()), b.count(s.encode())
    good = (wt is None or nt == wt) and (w12 is None or n12 == w12)
    ok &= good
    print('%s %-45s TAG x%d FS12 x%d%s' % ('OK  ' if good else 'FAIL', s, nt, n12, '' if wt is not None else ' (reference)'))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
