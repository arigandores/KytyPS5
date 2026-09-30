"""Add-only proof for test_sc142.py after the counted full mutlib run (session 142 link 1b): the new suite equals the suite of
the full run (step1b/v1/test_sc142.py) with lines inserted right before the final checks line and nothing else changed, so
every kill of the full run (its kill line) stands on the new suite.  ASCII output."""
import hashlib

OLD = 'C:/kyty/s142/step1b/v1/test_sc142.py'
NEW = 'C:/kyty/s142/test_sc142.py'
a = open(OLD, 'rb').read()
b = open(NEW, 'rb').read()
la = a.decode().split('\n')
lb = b.decode().split('\n')
k = la.index("print('checks: %d' % N_CASES[0])")
ok = lb[:k] == la[:k] and lb[len(lb) - (len(la) - k):] == la[k:]
print('old %s %s lines %d' % (OLD, hashlib.sha256(a).hexdigest(), len(la)))
print('new %s %s lines %d' % (NEW, hashlib.sha256(b).hexdigest(), len(lb)))
print('ADDONLY: %s (added %d lines before line %d of the old suite)' % ('PASS' if ok else 'FAIL', len(lb) - len(la), k + 1))
