"""Assembles C:/kyty/s143/test_sc143.py: PART A = C:/kyty/s142/test_sc142.py of link 1b with 5 replacements (header, target,
module name + profile 142, fixture dir), PART B = step0/partB.py.txt inserted before the final checks line.  LF, ASCII."""
s = open('C:/kyty/s142/test_sc142.py', encoding='utf-8').read()
reps = [
    ('"""Offline fixtures of sc142.py (the scorer of the scene census sc142 and of SCENE_OK on Sky Garden; session 142 step 0,\n',
     '"""Offline fixtures of sc143.py (session 143 step 0, HPP-297; ROADMAP s122 item 231 (i)(1)-(4)).  PART A: the whole suite of\n'
     'sc142.py (test_sc142.py of link 1b, every case unchanged) run on sc143.py in PROFILE 142 (sc143.profile(sc143.P142): the tags,\n'
     'seal, chain name and roots of session 142) - the reading of sc142 after item 224 holds in the ported code.  PART B (at the\n'
     'end): the profile of session 143 - the new terms and edges of item 231 (i).\n'
     'Session 142 header of PART A: offline fixtures of sc142.py (the scorer of the scene census sc142 and of SCENE_OK on Sky Garden; session 142 step 0,\n'),
    ('    python C:/kyty/s142/test_sc142.py [<sc142 under test>]\n', '    python C:/kyty/s143/test_sc143.py [<sc143 under test>]\n'),
    ("SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc142.py')\nprint('suite test_sc142.py sha256 %s target sc142.py sha256 %s' % (",
     "SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc143.py')\nprint('suite test_sc143.py sha256 %s target sc143.py sha256 %s' % ("),
    ("_spec = importlib.util.spec_from_file_location('sc142_under_test', SRC)\nS = importlib.util.module_from_spec(_spec)\n_spec.loader.exec_module(S)\n",
     "_spec = importlib.util.spec_from_file_location('sc143_under_test', SRC)\nS = importlib.util.module_from_spec(_spec)\n_spec.loader.exec_module(S)\n"
     "P143 = S.profile(S.P142)     # PART A runs in profile 142; PART B restores the profile of session 143\n"),
    ("BASE = Path('C:/kyty/s142/fx_sc142')   # mutlib gives every job its own copy of this directory",
     "BASE = Path('C:/kyty/s143/fx_sc143')   # mutlib gives every job its own copy of this directory"),
]
for a, b in reps:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
tail = "print('checks: %d' % N_CASES[0])\n"
assert s.count(tail) == 1
pb = open('C:/kyty/s143/step0/partB.py.txt', encoding='utf-8').read()
s = s.replace(tail, pb + tail)
assert '\r' not in s and all(ord(c) < 128 for c in s)
open('C:/kyty/s143/test_sc143.py', 'w', encoding='utf-8', newline='\n').write(s)
print('assembled test_sc143.py lines %d' % len(s.split('\n')))
