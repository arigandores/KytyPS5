"""Session 144 step 0 (HPP-330): build test_sc144.py from C:/kyty/s143/test_sc143.py (PARTS A-C carried unchanged, run on
sc144.py in profiles 142 / 143) and append PART D (profile 144).  ASCII only, LF."""
import sys

t = open('C:/kyty/s143/test_sc143.py', 'rb').read().decode('ascii')
assert '\r' not in t
R = []


def rep(old, new):
    R.append((old, new))


rep('"""Offline fixtures of sc143.py (session 143 step 0, HPP-297; ROADMAP s122 item 231 (i)(1)-(4)).  PART A: the whole suite of',
    '"""Offline fixtures of sc144.py (session 144 step 0, HPP-330; ROADMAP s122 item 254 (e), (k)(1)-(5)).  PARTS A-C: the whole\n'
    'suite of sc143.py (C:/kyty/s143/test_sc143.py of link 1b, every case unchanged) run on sc144.py: PART A in profile 142, PARTS\n'
    'B and C in profile 143 (sc144.profile(sc144.P143)) - the reading of sc143 after items 242, 246 holds in the ported code.\n'
    'PART D (at the end): the profile of session 144 - the 33 tags and their order, the control W, the cross-session pair (a W\n'
    'of s144 with the V of s143: its root, chain, seal, log sha and sheet), the W form of item 254 (e) and its violations, the W\n'
    'stopped before / after the first GuestOut line, the stop rules of item 254 (k)(4) (control, two W, three V), the repeated\n'
    'entry V, the skipped-draw frames by distinct frame= (debt D-7), the regression of profile 143, ASCII.\n'
    'Session 143 header (carried): PART A: the whole suite of')
rep("    python C:/kyty/s143/test_sc143.py [<sc143 under test>]\n", "    python C:/kyty/s144/test_sc144.py [<sc144 under test>]\n")
rep("SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc143.py')\n",
    "SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc144.py')\n")
rep("print('suite test_sc143.py sha256 %s target sc143.py sha256 %s' % (",
    "print('suite test_sc144.py sha256 %s target sc144.py sha256 %s' % (")
rep("_spec = importlib.util.spec_from_file_location('sc143_under_test', SRC)",
    "_spec = importlib.util.spec_from_file_location('sc144_under_test', SRC)")
rep("P143 = S.profile(S.P142)     # PART A runs in profile 142; PART B restores the profile of session 143\n",
    "P144 = S.profile(S.P143)     # PARTS B, C run in profile 143; PART D restores the profile of session 144\n"
    "P143 = S.profile(S.P142)     # PART A runs in profile 142; PART B restores the profile of session 143\n")
rep("BASE = Path('C:/kyty/s143/fx_sc143')", "BASE = Path('C:/kyty/s144/fx_sc144')")

PARTD = open('C:/kyty/s144/step0/partD.py.txt', 'rb').read().decode('ascii')
assert '\r' not in PARTD
PARTD2 = open('C:/kyty/s144/step0/partD2.py.txt', 'rb').read().decode('ascii')
assert '\r' not in PARTD2 and PARTD.count('S.XSRC = dict(XSRC_REAL)\nREQ144') == 1
PARTD = PARTD.replace('S.XSRC = dict(XSRC_REAL)\nREQ144', PARTD2 + 'S.XSRC = dict(XSRC_REAL)\nREQ144')
rep("print('checks: %d' % N_CASES[0])\nif ok:\n    print('ALL OK')\nsys.exit(0 if ok else 1)\n",
    PARTD + "print('checks: %d' % N_CASES[0])\nif ok:\n    print('ALL OK')\nsys.exit(0 if ok else 1)\n")
for old, new in R:
    n = t.count(old)
    if n != 1:
        print('ANCHOR COUNT %d: %r' % (n, old[:100]))
        sys.exit(1)
    t = t.replace(old, new)
t.encode('ascii')
open('C:/kyty/s144/test_sc144.py', 'wb').write(t.encode('ascii'))
print('mk_test_sc144: %d replacements, %d bytes' % (len(R), len(t)))
