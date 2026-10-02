"""port_tests146.py - session 146 step 0 (HPP-386): test_fgcpu146.py and test_tools146.py from the s145 suites (names 145 -> 146;
fgcpu146 prints <app> for every process name - "Process" 5 of s145, item 309 (i): the expected 'appX:<pid>:<rate>' strings
become '<app>:<pid>:<rate>' and a case checks that no input name reaches the output; lockcheck146 pins dac02fb9).  LF, ASCII."""
import hashlib
import re
import sys

S5 = 'C:/kyty/s145'
S6 = 'C:/kyty/s146'
OK = [True]


def port(src, dst, subs, regex=(), extra_before_end=None):
    b = open(src, 'rb').read()
    t = b.decode('ascii')
    for a, c, n in subs:
        k = t.count(a)
        if (n is not None and k != n) or k == 0:
            print('ANCHOR %s %r count %d (want %s)' % (src, a[:60], k, n))
            OK[0] = False
        t = t.replace(a, c)
    for rx, c in regex:
        t, k = re.subn(rx, c, t)
        print('regex %s %r: %d' % (dst, rx, k))
    if extra_before_end is not None:
        end = "print('checks"
        i = t.rfind(end)
        if i < 0:
            end = 'if ok:'
            i = t.rfind(end)
        t = t[:i] + extra_before_end + t[i:]
    if any(ord(c) > 127 for c in t):
        print('NON-ASCII', dst)
        OK[0] = False
    open(dst, 'wb').write(t.encode('ascii'))
    print('port %s %s -> %s %s' % (src, hashlib.sha256(b).hexdigest()[:16], dst, hashlib.sha256(t.encode('ascii')).hexdigest()[:16]))


port(S5 + '/test_fgcpu145.py', S6 + '/test_fgcpu146.py',
     [('to s145 by HPP-350, names 143 -> 144 -> 145)', 'to s145 by HPP-350, to s146 by HPP-386, names 143 -> 144 -> 145 -> 146; '
       'session 146: every process of a TOP list prints as <app>:<pid>:<rate>)', None),
      ('fgcpu145', 'fgcpu146', None), ('go145a', 'go146a', None), ('C:/kyty/s145', 'C:/kyty/s146', None),
      ("'bash:70:0.100'", "'<app>:70:0.100'", 1), ("'bash:71:0.050'", "'<app>:71:0.050'", 1),
      ("'proc?x:1:0.500' in out", "'<app>:1:0.500' in out", 1)],
     regex=((r"app[A-Z]:(\d+):(\d+\.\d{3})", r"<app>:\1:\2"),),
     extra_before_end="""ok &= case('f146 session 146 ("Process" 5 of s145): no input process name reaches the output - every TOP entry is '
           '<app>:<pid>:<rate>', all(('app%s:' % c) not in out for c in 'ABCDEFGH') and '<app>:' in out)
""")
port(S5 + '/test_tools145.py', S6 + '/test_tools146.py',
     [('to s145 by HPP-350, names 143 -> 144 -> 145)', 'to s145 by HPP-350, to s146 by HPP-386, names 143 -> 144 -> 145 -> 146)',
       None),
      ('cachemf145', 'cachemf146', None), ('lockcheck145', 'lockcheck146', None), ('go145a', 'go146a', None),
      ('test_tools145', 'test_tools146', None), ('sc145', 'sc146', None), ('runs145', 'runs146', None),
      ('C:/kyty/s145', 'C:/kyty/s146', None), ('w145_00', 'w146_00', None), ('w145_01', 'r146_01', None),
      ('w145_09', 'w146_09', None), ('(!= the pinned 9235a7ac)', '(!= the pinned dac02fb9)', 1), ('the s145 root', 'the s146 root', 1),
      ("L.BUILD == '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'", "L.BUILD == 'dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e'", 1)])
print('ALL OK' if OK[0] else 'SOME FAILED')
sys.exit(0 if OK[0] else 1)
