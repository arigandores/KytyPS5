"""F44c (HPP-793): manual negative controls of the reader (outside the seal, form of F38c neg/): 7 edits of f44c_read.py, each must make
test_f44c_read.py fail (prints the failed check count per edit).  Writes mutants under <dir>/neg/.  ASCII only.
usage: python neg_f44c.py <f44c dir>"""
import os
import subprocess
import sys

D = sys.argv[1]
SRC = open(os.path.join(D, 'f44c_read.py'), encoding='ascii').read()
EDITS = [
    ('FixF29 member always YES', "    ok = bool(x['f29']) and x['f29_bad'] == 0 and all(v == 1 for v, l in x['f29']) and g is not None and x['f29'][0][1] < g\n",
     "    ok = True\n"),
    ('env without KYTY_FIX_F29', ", KYTY_REC=None, KYTY_FIX_F29='1')", ", KYTY_REC=None)"),
    ('installed before / after any', "         inst_b == BIN_INST and inst_a == BIN_INST),", "         True),"),
    ('overflow in stdout dead', "            if M_OVF in line:\n                ovf += 1\n", "            if M_OVF in line:\n                pass\n"),
    ('accessed in log dead', "        if M_ACC in line:\n            r['acc'] += 1\n", "        if M_ACC in line and False:\n            r['acc'] += 1\n"),
    ('FixF29 moved to the form group', "         f29_member(x)]\n    f = [f21_member(x),", "         ]\n    f = [f29_member(x), f21_member(x),"),
    ('glitches always YES', "         ('0 one-frame glitches (%s)' % gl, gl == 0),", "         ('0 one-frame glitches (%s)' % gl, True),"),
]
os.makedirs(os.path.join(D, 'neg'), exist_ok=True)
allok = True
for i, (name, a, b) in enumerate(EDITS, 1):
    assert SRC.count(a) == 1, name
    p = os.path.join(D, 'neg', 'm%d_f44c_read.py' % i)
    open(p, 'w', encoding='ascii', newline='\n').write(SRC.replace(a, b))
    r = subprocess.run([sys.executable, os.path.join(D, 'test_f44c_read.py'), p], capture_output=True, text=True)
    last = [l for l in r.stdout.splitlines() if l.startswith('checks ')]
    caught = r.returncode != 0
    allok &= caught
    print('m%d %-34s rc %d %s -> %s' % (i, name, r.returncode, last[-1] if last else '-', 'CAUGHT' if caught else 'NOT CAUGHT'))
print('ALL OK' if allok else 'FAILED')
sys.exit(0 if allok else 1)
