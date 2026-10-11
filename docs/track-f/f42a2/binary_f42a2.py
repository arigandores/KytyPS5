"""F42a2 (HPP-805, ROADMAP s122 item 705(b)(4), (5)): strings of the F42a2 tag exe against the FS12 copy 46892c20 and the
F42a tag copy 6abebc7b (copy of the F42a binary_f42a.py with the version marks of the F42a2 build - worktree 5ccb1d31,
configured at adcd0eba): F20 present in the tag exe (as in F42a), absent in FS12; the FS12 markers and the translation
signature 9177b426 equal; markers of rows not in the base (F25, F24, F29, diagnostics) absent.
Prints the table and ALL OK / FAIL.   python binary_f42a2.py <tag exe> <FS12 exe> <F42a exe>"""
import hashlib
import sys

tag, fs12, f42a = sys.argv[1], sys.argv[2], sys.argv[3]
a, b, c = open(tag, 'rb').read(), open(fs12, 'rb').read(), open(f42a, 'rb').read()
print('TAG  %s sha256 %s' % (tag, hashlib.sha256(a).hexdigest()))
print('FS12 %s sha256 %s' % (fs12, hashlib.sha256(b).hexdigest()))
print('F42a %s sha256 %s' % (f42a, hashlib.sha256(c).hexdigest()))
# (string, want in tag, want in FS12, want in F42a); None - reference only
MARKS = [('KYTY_FIX_F20', 1, 0, 1), ('FixF20: mode=', 1, 0, 1), ('FixF20Stat:', 1, 0, 1),
         ('KYTY_FIX_F21', 1, 1, 1), ('FixF21: mode=', 1, 1, 1), ('KYTY_FIX_B12', 1, 1, 1), ('FixB12: mode=', 1, 1, 1),
         ('KYTY_FIX_B13', 1, 1, 1), ('KYTY_FIX_B36', 1, 1, 1), ('KYTY_FIX_B4', None, None, None), ('FixB4: mode=', 1, 1, 1),
         ('KYTY_FIX_F25', 0, 0, 0), ('FixF25: mode=', 0, 0, 0), ('KYTY_FIX_F24', 0, 0, 0), ('FixF24:', 0, 0, 0),
         ('KYTY_FIX_F29', 0, 0, 0), ('KYTY_DIAG_B32', 0, 0, 0), ('rts_bad_b', 0, 0, 0),
         ('KYTY_PIPELINE_SALT', 1, 1, 1),
         ('9177b4267de1fb8bac7d1113afd8733210addfac', 1, 1, 1),
         # version of main.cpp (kytyGitVersion.h, regenerated at every build) - NUL-delimited
         ('\x00KytyPS5-2026-09-15-6a2987a-1917-g5ccb1d31\x00', 1, 0, 0),
         ('\x00KytyPS5-2026-09-15-6a2987a-1916-g26283087\x00', 0, 0, 1),
         ('\x00KytyPS5-2026-09-15-6a2987a-1914-g730ed40a\x00', 0, 1, 0),
         # SDL_REVISION of 3rdparty/SDL2 - fixed at the configure of the build folder: the F42a2 worktree was configured
         # at adcd0eba (730ed40a + the two F42a picks) before the F42a2 pick; SDL sources are not changed by F42a2
         ('SDL-KytyPS5-2026-09-15-6a2987a-1916-gadcd0eba\x00', 1, 0, 0),
         ('SDL-KytyPS5-2026-09-15-6a2987a-1914-g730ed40a\x00', 0, 1, 1)]
ok = True
for s, wt, w12, w42 in MARKS:
    nt, n12, n42 = a.count(s.encode()), b.count(s.encode()), c.count(s.encode())
    good = (wt is None or nt == wt) and (w12 is None or n12 == w12) and (w42 is None or n42 == w42)
    ok &= good
    print('%s %-48s TAG x%d FS12 x%d F42a x%d%s' % ('OK  ' if good else 'FAIL', s.replace('\x00', ' '), nt, n12, n42,
                                                   '' if wt is not None else ' (reference)'))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
