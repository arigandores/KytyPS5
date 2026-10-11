"""FS14c (HPP-814): build C:/kyty/f287/fs14c from the FS13c tools (names moved) and the drafts of this link (go / launch / post, the reader
and its fixtures, the regression, the references, beside this file).  LF output.  Refuses under the lock or the stop file.  ASCII only.
usage: python mk_fs14c.py <draft dir>"""
import os
import sys

SRC = 'C:/kyty/f287/fs13c'
DST = 'C:/kyty/f287/fs14c'
DRAFT = sys.argv[1]
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    print('lock or STOP - nothing written')
    sys.exit(3)
for d in ('runs', 'pred', 'base', 'old', 'draft'):
    os.makedirs(DST + '/' + d, exist_ok=True)


def moved(b):
    for a, z in ((b'fs13c', b'fs14c'), (b'FS13C', b'FS14C'), (b'FS13c', b'FS14c'), (b'HPP-789', b'HPP-814')):
        b = b.replace(a, z)
    return b


HDR = b'# Track F link FS14c (HPP-814; ROADMAP s122 item 710 (g)(3), 712 (g)(3)): copy of the FS13c (HPP-789) file %s with the names moved (fs13c -> fs14c, FS13C -> FS14C, FS13c -> FS14c, HPP-789 -> HPP-814); no change of meaning.\n'
ROWS = []
for name, new in (('dispstate.py', 'dispstate.py'), ('guard_fs13c.py', 'guard_fs14c.py'), ('hold_fs13c.py', 'hold_fs14c.py'),
                  ('hostload_fs13c.py', 'hostload_fs14c.py'), ('idle142.py', 'idle142.py'), ('launch_run.py', 'launch_run.py'),
                  ('manifest_fs4c.py', 'manifest_fs4c.py'), ('mfsub_fs13c.py', 'mfsub_fs14c.py'), ('procload.py', 'procload.py'),
                  ('queue_fs13c.py', 'queue_fs14c.py'), ('run_safety99.py', 'run_safety99.py'), ('runchk_fs13c.py', 'runchk_fs14c.py'),
                  ('sheet142.py', 'sheet142.py'), ('snap_fs13c.py', 'snap_fs14c.py'), ('wait_fs13c.sh', 'wait_fs14c.sh'),
                  ('chk_fs13c.sh', 'chk_fs14c.sh'), ('gates.req', 'gates.req'), ('sample.req', 'sample.req'),
                  ('gates_default.txt', 'gates_default.txt'), ('tempo_fs13c.py', 'tempo_fs14c.py')):
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
b = open(os.path.join(SRC, 'enter_scene.py'), 'rb').read().replace(b'\r\n', b'\n')
old = b"ROOT = pathlib.Path('C:/kyty/f287/fs13c')"
assert b.count(old) == 1
b = b.replace(old, b"ROOT = pathlib.Path('C:/kyty/f287/fs14c')")
b = (b'# Track F link FS14c (HPP-814; ROADMAP s122 item 710 (g)(3)): the FS13c file of this role with ROOT moved (f287/fs13c to f287/fs14c);\n'
     b'# nothing else changed.\n') + b
open(os.path.join(DST, 'enter_scene.py'), 'wb').write(b)
ROWS.append('enter_scene.py ROOT moved')
for name in ('go_fs14c.sh', 'launch_fs14c.sh', 'post_fs14c.sh', 'fs14c_read.py', 'test_fs14c_read.py', 'test_tools_fs14c.py', 'refs_fs14c.py',
             'regress_fs14c.py', 'mk_fs14c.py'):
    b = open(os.path.join(DRAFT, name), 'rb').read().replace(b'\r\n', b'\n')
    assert all(c < 128 for c in b), name
    open(os.path.join(DST, name), 'wb').write(b)
    ROWS.append('draft %s' % name)
for name in ('gen_fs14c.py', 'fix_fs14c.py'):
    b = open(os.path.join(DRAFT, name), 'rb').read().replace(b'\r\n', b'\n')
    open(os.path.join(DST, 'draft', name), 'wb').write(b)
    ROWS.append('draft/%s' % name)
for r in ROWS:
    print(r)
print('ALL OK')
