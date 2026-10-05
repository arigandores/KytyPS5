"""port_s15.py - S15a (HPP-601): the mechanical port of the S13 harness files into C:/kyty/s288/s15 (names and paths only).
The semantic changes of item 511 (z)(3)-(5) and (z)(i) are made by patch_s15.py after this.  Refuses when the lock exists or
when a target exists.  LF, ASCII.
"""
import os
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
S13 = 'C:/kyty/s288/s13'
S15 = 'C:/kyty/s288/s15'
FILES = [('go_s13.sh', 'go_s15.sh'), ('sc_s13.py', 'sc_s15.py'), ('test_sc_s13.py', 'test_sc_s15.py'),
         ('mut_sc_s13.py', 'mut_sc_s15.py'), ('test_go_s13.py', 'test_go_s15.py'), ('seedexp_s13.py', 'seedexp_s15.py'),
         ('test_seedexp_s13.py', 'test_seedexp_s15.py'), ('mkseal_s13.py', 'mkseal_s15.py'),
         ('seal13_body.md', 'seal14_body.md'), ('seal13_tail.md', 'seal14_tail.md')]
# protected tokens: the sealed list of the 19 levels stays the S13 file (item 511 (z)(2): the same 19 levels)
PROTECT = [('s13/lvl_s13.py', '@@LVLPY@@'), ('s13/lvl_s13.out.txt', '@@LVLOUT@@'), ('lvl_s13.out.txt', '@@LVLOUT2@@'),
           ('lvl_s13.py', '@@LVLPY2@@'), ('s13/seeds_manifest.txt (65a95adf', '@@OLDMANI@@')]
REPL = [('C:/kyty/s288/s13', 'C:/kyty/s288/s15'),
        ('pred/13b_s.md', 'pred/14b_s.md'), ('pred/13_s.md', 'pred/14_s.md'), ('pred/12_s.md', 'pred/13_s.md'),
        ("'13b_s.md'", "'14b_s.md'"), ("'13_s.md'", "'14_s.md'"),
        ('13b_s.md', '14b_s.md'), ('13_s.md', '14_s.md'),
        ('test_seedexp_s13', 'test_seedexp_s15'), ('seedexp_s13', 'seedexp_s15'), ('test_sc_s13', 'test_sc_s15'),
        ('mut_sc_s13', 'mut_sc_s15'), ('test_go_s13', 'test_go_s15'), ('mkseal_s13', 'mkseal_s15'), ('sc_s13', 'sc_s15'),
        ('go_s13', 'go_s15'), ('seal13_body', 'seal14_body'), ('seal13_tail', 'seal14_tail'),
        ('fx_go_lock13', 'fx_go_lock15'), ('fx_seedexp_s13', 'fx_seedexp_s15'),
        ("'s13/", "'s15/"), ('"s13/', '"s15/'), (' s13/', ' s15/'), ('(s13/', '(s15/'),
        ("ROOT + '/s13'", "ROOT + '/s15'"), ("/ 's13'", "/ 's15'"), ("'s13'", "'s15'"), ('/s13/', '/s15/'), ('/s13 ', '/s15 '),
        ('$ROOT/s13', '$ROOT/s15'), ('link s13', 'link s15'), ("'s13 %s", "'s15 %s"), ('s13\\ *', 's15\\ *'),
        ('LD=$ROOT/s13', 'LD=$ROOT/s15'), ('S13=$ROOT/s13', 'S15=$ROOT/s15')]


def port(text):
    for a, b in PROTECT:
        text = text.replace(a, b)
    for a, b in REPL:
        text = text.replace(a, b)
    for a, b in PROTECT:
        text = text.replace(b, a)
    return text


def main():
    if os.path.exists(LOCK):
        print('LOCKED - nothing written')
        return 5
    os.makedirs(S15, exist_ok=True)
    for a, b in FILES:
        if os.path.exists(os.path.join(S15, b)):
            print('STOP: %s exists' % b)
            return 1
    for a, b in FILES:
        t = open(os.path.join(S13, a), 'rb').read().decode('ascii').replace('\r\n', '\n')
        u = port(t)
        with open(os.path.join(S15, b), 'wb') as f:
            f.write(u.encode('ascii'))
        left = [ln for ln in u.split('\n') if 's13' in ln.lower() and 'lvl_s13' not in ln]
        print('%s -> %s: %d lines; lines still naming s13: %d' % (a, b, u.count('\n'), len(left)))
        for ln in left[:12]:
            print('    ' + ln[:150])
    return 0


if __name__ == '__main__':
    sys.exit(main())
