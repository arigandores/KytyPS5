"""setup146.py - session 146 step 0 (HPP-386): copy the helper files of the harness into C:/kyty/s146 (port of s145 and of the
FSc files of track F).  Only the root path / the session number in names and headers change - no change of meaning.  Every
copy is printed with the sha256 of source and target.  ASCII only.  Writes LF bytes."""
import hashlib
import os

S145 = 'C:/kyty/s145'
FSC = 'C:/kyty/f287/fsc'
DST = 'C:/kyty/s146'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def put(src, dst, subs=()):
    b = open(src, 'rb').read()
    t = b
    for a, c in subs:
        t = t.replace(a, c)
    t = t.replace(b'\r\n', b'\n') if b'\r\n' not in b else t
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'wb') as f:
        f.write(t)
    print('copy %s %s -> %s %s' % (src, sha(b)[:16], dst, sha(t)[:16]))


same = ('procload.py', 'idle142.py', 'sheet142.py', 'launch_run.py', 'run_safety99.py', 'gates_default.txt')
for n in same:
    put('%s/%s' % (S145, n), '%s/%s' % (DST, n))
put('%s/enter_scene.py' % S145, '%s/enter_scene.py' % DST, (
    (b"# Session 145 step 0 (HPP-350): the session-144 file of this role with the root moved (s144 to s145) - no change of meaning.",
     b"# Session 146 step 0 (HPP-386): the session-145 file of this role with the root moved (s145 to s146) - no change of meaning."),
    (b"ROOT = pathlib.Path('C:/kyty/s145')", b"ROOT = pathlib.Path('C:/kyty/s146')")))
put('%s/cachemf145.py' % S145, '%s/cachemf146.py' % DST, (
    (b'to s145 by HPP-350, names 143 -> 144 -> 145)', b'to s145 by HPP-350, to s146 by HPP-386, names 143 -> 144 -> 145 -> 146)'),
    (b'cachemf145', b'cachemf146'), (b'go145a.sh', b'go146a.sh'), (b'sc145.py', b'sc146.py')))
put('%s/fgcpu145.py' % S145, '%s/fgcpu146.py' % DST, (
    (b'to s145 by HPP-350, names 143 -> 144 -> 145)', b'to s145 by HPP-350, to s146 by HPP-386, names 143 -> 144 -> 145 -> 146)'),
    (b'fgcpu145', b'fgcpu146'), (b'go145a.sh', b'go146a.sh')))
for n in ('shalist_f2c.py', 'sheetpair_f3d.py'):
    put('%s/%s' % (FSC, n), '%s/%s' % (DST, n))
print('ALL OK')
