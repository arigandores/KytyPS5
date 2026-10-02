"""s146 link 1b (HPP-395; ROADMAP s122 item 316 (d)): the seal path pred/01_sc146.md -> pred/02_sc146.md in the chain, the
gate of step 2, the call wrapper and their suites (every occurrence; counts checked against the reading before the edit).
LF in, LF out (write_bytes)."""
import hashlib

R = 'C:/kyty/s146/'
WANT = {'go146a.sh': 1, 'step2/gate146.py': 3, 'step2/call_one.sh': 1, 'test_go146a.py': 5, 'step2/test_gate146.py': 6}
out = []
for name, c in WANT.items():
    p = R + name
    t = open(p, 'rb').read().decode('ascii')
    assert '\r' not in t, name
    got = t.count('01_sc146')
    if got == 0 and t.count('02_sc146') == c:
        out.append('%s already done (02 x %d) sha256 %s' % (name, c, hashlib.sha256(t.encode('ascii')).hexdigest()))
        continue
    assert got == c, (name, got, c)
    t = t.replace('01_sc146', '02_sc146')
    open(p, 'wb').write(t.encode('ascii'))
    out.append('%s %d -> sha256 %s' % (name, got, hashlib.sha256(t.encode('ascii')).hexdigest()))
print('\n'.join(out))
