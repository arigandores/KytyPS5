"""Item 404 (g): the seal path of go_s9.sh and of its suite -> pred/07_s.md (the seal 07 replaces 06b).  LF, write_bytes."""
import hashlib
import shutil
import sys

FILES = {'C:/kyty/s288/s9/go_s9.sh': ('a44064841674012aeb30033648f6728a4b1a9a527e37f1240f5db78eb8888c2c', [
    ('of pred/06b_s.md (item 377 (b)).', 'of pred/07_s.md (item 377 (b), item 404 (g)).'),
    ('\nPRED=pred/06b_s.md\n', '\nPRED=pred/07_s.md\n')]),
    'C:/kyty/s288/s9/test_go_s9.py': (None, [
        ("SC9, (BASE / 's10').as_posix(), (BASE / 'pred' / '06b_s.md').as_posix())",
         "SC9, (BASE / 's10').as_posix(), (BASE / 'pred' / '07_s.md').as_posix())"),
        ("    (BASE / 'pred' / '06b_s.md').write_text(", "    (BASE / 'pred' / '07_s.md').write_text("),
        ("the seal is pred/06b_s.md',", "the seal is pred/07_s.md',"),
        ("'PRED=pred/06b_s.md\\n' in src_t", "'PRED=pred/07_s.md\\n' in src_t"),
        ("(B2 / 'pred' / '06b_s.md').write_bytes(", "(B2 / 'pred' / '07_s.md').write_bytes(")])}
for p, (want, reps) in FILES.items():
    b = open(p, 'rb').read()
    print(p, 'before', hashlib.sha256(b).hexdigest())
    if want and hashlib.sha256(b).hexdigest() != want:
        sys.exit('refuse: %s changed' % p)
    shutil.copyfile(p, 'C:/kyty/s288/s10/r404/orig/' + p.rsplit('/', 1)[1])
    t = b.decode('ascii')
    assert '\r' not in t
    for a, c in reps:
        assert t.count(a) == 1, (p, a)
        t = t.replace(a, c, 1)
    assert '06b_s.md' not in t, p
    open(p, 'wb').write(t.encode('ascii'))
    print(p, 'after', hashlib.sha256(t.encode('ascii')).hexdigest())
