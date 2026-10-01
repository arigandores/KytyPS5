"""Link 1b of s145 (HPP-379): the second set of exact edits of sc145.py after p1b_sc.py - (1) the expected failing set of
(b)(3) in regress144 is its own constant REGRESS144_B3 (= REGRESS144_LIMIT on the s144 data); (2) the anchor sum of vquality
is written "* 1e-6" so that every mutant anchor of vcont stays unique.  ASCII only."""
import hashlib
import sys

P = 'C:/kyty/s145/sc145.py'
src = open(P, 'rb').read().decode('utf-8')
for old, new in (("    exp = (REGRESS144_LIMIT, (), REGRESS144_LIMIT, tuple(wt))\n",
                  "    exp = (REGRESS144_LIMIT, (), REGRESS144_B3, tuple(wt))\n"),
                 ("        base.append(it[-1] - c)\n        c += r[1] / 1e6\n",
                  "        base.append(it[-1] - c)\n        c += r[1] * 1e-6\n")):
    if src.count(old) != 1:
        print('ANCHOR COUNT %d: %r' % (src.count(old), old))
        sys.exit(1)
    src = src.replace(old, new)
open(P, 'wb').write(src.encode('ascii'))
print('edits 2; sc145.py sha256 %s' % hashlib.sha256(src.encode('ascii')).hexdigest())
