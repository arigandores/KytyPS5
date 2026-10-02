"""fix_ptg.py - corrects four anchors of port_testgo146.py: the old text still carries the tags of 145 (only the chain names are
renamed before the anchors) - and adds the rename of the msys path /c/kyty/s145."""
p = 'C:/kyty/s146/step0/port_testgo146.py'
t = open(p, 'rb').read().decode('ascii')
FIX = {
    'lv = re.findall(': (('(v146_', '(v145_'), ('|(w146_', '|(w145_'), ("(w146_\\\\d\\\\d)\\\\) LEVEL", "(w145_\\\\d\\\\d)\\\\) LEVEL")),
    "ok &= case('g47": (('w146_*', 'w145_*'), ('v146_*', 'v145_*')),
    "ok &= case('g49": (("('v146_01', 'w146_18', 'v146_18', 'v144_09', 'w144_09', 'w146_1x', 'v146_00')",
                        "('v145_01', 'w145_18', 'v145_18', 'v144_09', 'w144_09', 'w145_1x', 'v145_00')"),),
    "ok &= case('g50": (('name only session 146 (no 144', 'name only session 145 (no 144'), ("'the s146 times'", "'the s145 times'")),
}
parts = t.split('rep("""')
for i in range(1, len(parts)):
    for k, subs in FIX.items():
        if parts[i].startswith(k):
            end = parts[i].index('""",')
            old = parts[i][:end]
            for a, b in subs:
                assert a in old, (k, a)
                old = old.replace(a, b)
            parts[i] = old + parts[i][end:]
t = 'rep("""'.join(parts)
a = "             ('runs145', 'runs146'), ('sc145', 'sc146'), ('go145a', 'go146a'), ('C:/kyty/s145', 'C:/kyty/s146'),"
assert t.count(a) == 1
t = t.replace(a, a + " ('/c/kyty/s145', '/c/kyty/s146'),")
open(p, 'wb').write(t.encode('ascii'))
print('ok')
