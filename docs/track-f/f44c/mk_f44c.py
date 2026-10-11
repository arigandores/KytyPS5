"""F44c (HPP-793): build C:/kyty/f287/f44c from the F38c tools (names moved) and the drafts of this link (go / launch / post, the reader,
its fixtures, the regression, the tool fixtures, the refs check, beside this file).  LF output.  ASCII only.  Refuses under the lock or the
stop file and when f44c/runs already has a tag.
usage: python mk_f44c.py <draft dir>"""
import os
import sys

SRC = 'C:/kyty/f287/f38c'
DST = 'C:/kyty/f287/f44c'
DRAFT = sys.argv[1]
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    print('lock or STOP - nothing written')
    sys.exit(3)
if os.path.isdir(DST + '/runs') and any(n.startswith('f29_v') for n in os.listdir(DST + '/runs')):
    print('a tag exists under f44c/runs - nothing written')
    sys.exit(3)
for d in ('runs', 'pred', 'base', 'old'):
    os.makedirs(DST + '/' + d, exist_ok=True)


def moved(b):
    for a, z in ((b'f38c', b'f44c'), (b'F38C', b'F44C'), (b'F38c', b'F44c'), (b'HPP-765', b'HPP-793')):
        b = b.replace(a, z)
    return b


HDR = b'# Track F link F44c (HPP-793; ROADMAP s122 item 698 (d)(4)): copy of the F38c (HPP-765) file %s with the names moved (f38c -> f44c, F38C -> F44C, F38c -> F44c, HPP-765 -> HPP-793); no change of meaning.\n'
ROWS = []
for name, new in (('dispstate.py', 'dispstate.py'), ('guard_f38c.py', 'guard_f44c.py'), ('hold_f38c.py', 'hold_f44c.py'),
                  ('hostload_f38c.py', 'hostload_f44c.py'), ('idle142.py', 'idle142.py'), ('launch_run.py', 'launch_run.py'),
                  ('manifest_fs4c.py', 'manifest_fs4c.py'), ('mfsub_f38c.py', 'mfsub_f44c.py'), ('procload.py', 'procload.py'),
                  ('queue_f38c.py', 'queue_f44c.py'), ('run_safety99.py', 'run_safety99.py'), ('runchk_f38c.py', 'runchk_f44c.py'),
                  ('sheet142.py', 'sheet142.py'), ('snap_f38c.py', 'snap_f44c.py'), ('wait_f38c.sh', 'wait_f44c.sh'),
                  ('chk_f38c.sh', 'chk_f44c.sh'), ('gates.req', 'gates.req'), ('sample.req', 'sample.req'),
                  ('gates_default.txt', 'gates_default.txt'), ('tempo_f38c.py', 'tempo_f44c.py')):
    b = open(os.path.join(SRC, name), 'rb').read().replace(b'\r\n', b'\n')
    nb = moved(b)
    if nb != b:
        h = HDR % name.encode()
        if nb.startswith(b'#!'):
            i = nb.index(b'\n') + 1
            nb = nb[:i] + h + nb[i:]
        else:
            nb = h + nb
    open(os.path.join(DST, new), 'wb').write(nb)
    ROWS.append('%s -> %s changed %s' % (name, new, nb != b))
# enter_scene.py: only ROOT moved + a header line
b = open(os.path.join(SRC, 'enter_scene.py'), 'rb').read().replace(b'\r\n', b'\n')
old = b"ROOT = pathlib.Path('C:/kyty/f287/f38c')"
assert b.count(old) == 1
b = b.replace(old, b"ROOT = pathlib.Path('C:/kyty/f287/f44c')")
b = (b'# Track F link F44c (HPP-793; ROADMAP s122 item 698 (d)(4)): the F38c file of this role with ROOT moved (f287/f38c to f287/f44c);\n'
     b'# nothing else changed.\n') + b
open(os.path.join(DST, 'enter_scene.py'), 'wb').write(b)
ROWS.append('enter_scene.py ROOT moved')
for name in ('go_f44c.sh', 'launch_f44c.sh', 'post_f44c.sh', 'f44c_read.py', 'test_f44c_read.py', 'regress_f44c.py', 'test_tools_f44c.py',
             'refs_f44c.py', 'mk_f44c.py'):
    b = open(os.path.join(DRAFT, name), 'rb').read().replace(b'\r\n', b'\n')
    assert all(c < 128 for c in b), name
    open(os.path.join(DST, name), 'wb').write(b)
    ROWS.append('draft %s' % name)
for r in ROWS:
    print(r)
print('ALL OK')
