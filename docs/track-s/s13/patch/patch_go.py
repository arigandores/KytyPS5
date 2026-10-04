"""S13a4 (HPP-553, item 452 (d)(2)): go_s13.sh and test_go_s13.py read the seal 13 (pred/13_s.md, its edition pred/13b_s.md);
nothing else changes in the harness.  LF, ASCII.
    python patch_go.py
"""
S13 = 'C:/kyty/s288/s13'


def patch(p, repl, glob=()):
    s = open(p, 'rb').read().decode('ascii')
    assert chr(13) not in s
    for a, b in repl:
        n = s.count(a)
        if n != 1:
            raise SystemExit('%s: the target occurs %d times: %r' % (p, n, a[:100]))
        s = s.replace(a, b)
    ng = 0
    for a, b in glob:
        ng += s.count(a)
        s = s.replace(a, b)
    s.encode('ascii')
    open(p, 'wb').write(s.encode('ascii'))
    print('%s: %d replacements, %d global' % (p, len(repl), ng))


patch(S13 + '/go_s13.sh', [
    ('# the seal in force is pred/12_s.md or its edition pred/12b_s.md (pred/11_s.md is not in force).\n',
     '# S13a4 (HPP-553, item 452 (d)(2)): the seal in force is pred/13_s.md or its edition pred/13b_s.md (pred/12_s.md and\n'
     '# pred/11_s.md are not in force).\n'),
    ('"installed: PENDING" (seal 12, before the installation of S12d / FS5d)', '"installed: PENDING" (seal 13, until its edition)'),
    ('# the seal in force: the edition pred/12b_s.md (12 with the line "installed:" named and the line "edition: base pred/12_s.md\n'
     '# sha256 <sha>", a lead item) when it exists, else 12\n',
     '# the seal in force: the edition pred/13b_s.md (13 with the line "installed:" named and the line "edition: base pred/13_s.md\n'
     '# sha256 <sha>", a lead item) when it exists, else 13\n'),
    ('  pred/12_s.md|pred/12b_s.md) ;;\n', '  pred/13_s.md|pred/13b_s.md) ;;\n'),
    ('the seal path is not pred/12_s.md or pred/12b_s.md ($PRED)', 'the seal path is not pred/13_s.md or pred/13b_s.md ($PRED)'),
])
patch(S13 + '/test_go_s13.py', [
    ('a file one level deeper is not a guard (G5b); the seal is 12.\n',
     'a file one level deeper is not a guard (G5b); S13a4 (item 452 (d)(2)): the seal is 13.\n'),
], glob=(('12b_s.md', '13b_s.md'), ('12_s.md', '13_s.md')))
