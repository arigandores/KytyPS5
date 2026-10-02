"""gen_test146.py - session 146 step 0 (HPP-386): writes C:/kyty/s146/test_sc146.py = the whole suite of sc145.py
(C:/kyty/s145/test_sc145.py, every case unchanged; PARTS A-E run in the profiles 142-145 of sc146.py) + PART F (the profile of
session 146, step0/partf146.py.txt).  Anchored edits only: the header, the target, the first profile switch, the fixture
directory, PART F before the final count.  LF, ASCII; prints the sha256 of the inputs and of the output."""
import hashlib
import sys

SRC = 'C:/kyty/s145/test_sc145.py'
PARTF = 'C:/kyty/s146/step0/partf146.py.txt'
DST = 'C:/kyty/s146/test_sc146.py'
t = open(SRC, 'rb').read().decode('ascii')
f = open(PARTF, 'rb').read().decode('ascii').replace('\r\n', '\n')
OK = [True]


def rep(old, new):
    global t
    if t.count(old) != 1:
        print('ANCHOR %d: %r' % (t.count(old), old[:100]))
        OK[0] = False
        return
    t = t.replace(old, new)


rep('''"""Offline fixtures of sc145.py (session 145 step 0, HPP-350; ROADMAP s122 item 273 (k)(1)-(5)).''',
    '''"""Offline fixtures of sc146.py (session 146 step 0, HPP-386; ROADMAP s122 item 309 (k), (l)(1)-(7), item 300 (b)(4)).
PARTS A-E: the whole suite of sc145.py (C:/kyty/s145/test_sc145.py, every case unchanged) run on sc146.py in the profiles
142-145 (sc146.profile(sc146.P145) first) - the reading of sc145 holds in the ported code.  PART F (at the end): the profile
of session 146 - the 35 tags and their order, the re-check and second-hold V, the W form on the shipment binary (precache by
default), the DualSrcBlend control (control stop term, data row of every W, the variant of item 281 (g)), the stubs (F13) and
asserts (F14) rows, the tile events (D-4), SKIPPED_V_NOT_ENTERED (--skip-w, the summary), the stop-check from score.json (its
source line and the fall back to the log), the three-V rule over every made V, the RECHECK / B40 / Sky Garden / DATA lines,
the real log of the warm-up i146_v, ASCII.  Cases F1-F22.
    python C:/kyty/s146/test_sc146.py [<sc146 under test>]
Session 145 header (carried):
Offline fixtures of sc145.py (session 145 step 0, HPP-350; ROADMAP s122 item 273 (k)(1)-(5)).''')
rep('''SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc145.py')
print('suite test_sc145.py sha256 %s target sc145.py sha256 %s' % (''', '''SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc146.py')
print('suite test_sc146.py sha256 %s target sc146.py sha256 %s' % (''')
rep('''_spec = importlib.util.spec_from_file_location('sc145_under_test', SRC)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
''', '''_spec = importlib.util.spec_from_file_location('sc146_under_test', SRC)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
P146 = S.profile(S.P145)     # PARTS A-E run in the profiles 142-145; PART F restores the profile of session 146
''')
rep('''BASE = Path('C:/kyty/s145/fx_sc145')''', '''BASE = Path('C:/kyty/s146/fx_sc146')''')
rep('''print('checks: %d' % N_CASES[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)''', f.rstrip('\n') + '''
print('checks: %d' % N_CASES[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)''')
if any(ord(c) > 127 for c in t):
    print('NON-ASCII')
    OK[0] = False
open(DST, 'wb').write(t.encode('ascii'))
print('gen_test146: %s %s + %s %s -> %s %s' % (SRC, hashlib.sha256(open(SRC, 'rb').read()).hexdigest()[:16], PARTF,
                                                hashlib.sha256(f.encode('ascii')).hexdigest()[:16], DST,
                                                hashlib.sha256(t.encode('ascii')).hexdigest()[:16]))
print('ALL OK' if OK[0] else 'SOME FAILED')
sys.exit(0 if OK[0] else 1)
