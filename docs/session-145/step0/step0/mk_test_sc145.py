"""Session 145 step 0 (HPP-350): build test_sc145.py from C:/kyty/s144/test_sc144.py (PARTS A-D carried unchanged, run on
sc145.py in profiles 142 / 143 / 144) and append PART E (profile 145, step0/partE.py.txt).  ASCII only, LF."""
import sys

t = open('C:/kyty/s144/test_sc144.py', 'rb').read().decode('ascii')
assert '\r' not in t
R = []


def rep(old, new):
    R.append((old, new))


rep('"""Offline fixtures of sc144.py (session 144 step 0, HPP-330; ROADMAP s122 item 254 (e), (k)(1)-(5)).  PARTS A-C: the whole',
    '"""Offline fixtures of sc145.py (session 145 step 0, HPP-350; ROADMAP s122 item 273 (k)(1)-(5)).  PARTS A-D: the whole\n'
    'suite of sc144.py (C:/kyty/s144/test_sc144.py, every case unchanged) run on sc145.py: PART A in profile 142, PARTS B and C\n'
    'in profile 143, PART D in profile 144 (sc145.profile(sc145.P144)) - the reading of sc144 holds in the ported code.\n'
    'PART E (at the end): the profile of session 145 - the 34 tags and their order, the control W, the W repeat of\n'
    'rocket_hourglass with the V v144_09 of s144 (its root, chain, seal, log sha and sheet), the cold census, the W filter of\n'
    'one message and its violations, the window event (minimized, Recovering without minimized, the stdout, other window\n'
    'lines, chunks), the layer limit (control 0 required, other W "layer truncated"), the video continuity of B38 (the gap of\n'
    '60 ms, the margin of 12 ms, before / after the first scene frame, the longest run), the stop rule of the window event, the\n'
    'summary lines, the regression of profile 144 on a synthetic profile, the real constants, ASCII.\n'
    'Session 144 header (carried): PARTS A-C: the whole')
rep("    python C:/kyty/s144/test_sc144.py [<sc144 under test>]\n", "    python C:/kyty/s145/test_sc145.py [<sc145 under test>]\n")
rep("SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc144.py')\n",
    "SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc145.py')\n")
rep("print('suite test_sc144.py sha256 %s target sc144.py sha256 %s' % (",
    "print('suite test_sc145.py sha256 %s target sc145.py sha256 %s' % (")
rep("_spec = importlib.util.spec_from_file_location('sc144_under_test', SRC)",
    "_spec = importlib.util.spec_from_file_location('sc145_under_test', SRC)")
rep("P144 = S.profile(S.P143)     # PARTS B, C run in profile 143; PART D restores the profile of session 144\n",
    "P145 = S.profile(S.P144)     # PARTS A-D run in the profiles 142-144; PART E restores the profile of session 145\n"
    "P144 = S.profile(S.P143)     # PARTS B, C run in profile 143; PART D restores the profile of session 144\n")
rep("BASE = Path('C:/kyty/s144/fx_sc144')", "BASE = Path('C:/kyty/s145/fx_sc145')")
PARTE = open('C:/kyty/s145/step0/partE.py.txt', 'rb').read().decode('ascii')
assert '\r' not in PARTE
rep("print('checks: %d' % N_CASES[0])\nif ok:\n    print('ALL OK')\nsys.exit(0 if ok else 1)\n",
    PARTE + "print('checks: %d' % N_CASES[0])\nif ok:\n    print('ALL OK')\nsys.exit(0 if ok else 1)\n")
for old, new in R:
    n = t.count(old)
    if n != 1:
        print('ANCHOR COUNT %d: %r' % (n, old[:100]))
        sys.exit(1)
    t = t.replace(old, new)
t.encode('ascii')
open('C:/kyty/s145/test_sc145.py', 'wb').write(t.encode('ascii'))
print('mk_test_sc145: %d replacements, %d bytes' % (len(R), len(t)))
