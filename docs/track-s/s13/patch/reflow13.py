"""S13a4: reflow of the edition sentence in s13/seal13_body.md (text only, same words).  Exactly once.  LF, ASCII."""
P = 'C:/kyty/s288/s13/seal13_body.md'
NL = chr(10)
t = open(P, 'rb').read().decode('ascii')
a = NL.join([
    '  binary of S13b is not named yet (the edition is a lead item after the verdict of S13r3).  An edition pred/13b_s.md - every',
    '  line of this seal unchanged, in order, plus the line "installed:" naming the binary and EXACTLY ONE line "edition: base',
    '  pred/13_s.md sha256 <the 64 hex sha256 of',
    '  this seal file>" (RC6, item 436 (b)(6), item 452 (d)(2)) - is made by a lead item that names the sha, the signature, the',
    '  variant and',
    '  the sha256 of this seal (item 428 (g), V1); the scorer and the harness read the edition when it exists (sc_s13.py current_seal /',
])
b = NL.join([
    '  binary of S13b is not named yet (the edition is a lead item after the verdict of S13r3).  An edition pred/13b_s.md - every',
    '  line of this seal unchanged, in order, plus the line "installed:" naming the binary and EXACTLY ONE line "edition: base',
    '  pred/13_s.md sha256 <the 64 hex sha256 of this seal file>" (RC6, item 436 (b)(6), item 452 (d)(2)) - is made by a lead',
    '  item that names the sha, the signature, the variant and the sha256 of this seal (item 428 (g), V1); the scorer and the',
    '  harness read the edition when it exists (sc_s13.py current_seal /',
])
n = t.count(a)
if n != 1:
    raise SystemExit('reflow13: target occurs %d times' % n)
t = t.replace(a, b)
open(P, 'wb').write(t.encode('ascii'))
print('reflow13: done; longest line %d' % max(len(x) for x in t.split(NL)))
