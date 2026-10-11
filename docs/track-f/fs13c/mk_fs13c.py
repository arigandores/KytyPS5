"""FS13c (HPP-789): build C:/kyty/f287/fs13c from the FS12c tools (names moved) and the drafts of this link (go / launch / post, the reader
and its fixtures, beside this file).  LF output.  ASCII only.
usage: python mk_fs13c.py <draft dir>"""
import os
import shutil
import sys

SRC = 'C:/kyty/f287/fs12c'
DST = 'C:/kyty/f287/fs13c'
DRAFT = sys.argv[1]
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    print('lock or STOP - nothing written')
    sys.exit(3)
for d in ('runs', 'pred', 'base', 'old'):
    os.makedirs(DST + '/' + d, exist_ok=True)


def moved(b):
    for a, z in ((b'fs12c', b'fs13c'), (b'FS12C', b'FS13C'), (b'FS12c', b'FS13c'), (b'HPP-752', b'HPP-789')):
        b = b.replace(a, z)
    return b


HDR = b'# Track F link FS13c (HPP-789; ROADMAP s122 item 697 (g)(3)): copy of the FS12c (HPP-752) file %s with the names moved (fs12c -> fs13c, FS12C -> FS13C, FS12c -> FS13c, HPP-752 -> HPP-789); no change of meaning.\n'
ROWS = []
for name, new in (('dispstate.py', 'dispstate.py'), ('guard_fs12c.py', 'guard_fs13c.py'), ('hold_fs12c.py', 'hold_fs13c.py'),
                  ('hostload_fs12c.py', 'hostload_fs13c.py'), ('idle142.py', 'idle142.py'), ('launch_run.py', 'launch_run.py'),
                  ('manifest_fs4c.py', 'manifest_fs4c.py'), ('mfsub_fs12c.py', 'mfsub_fs13c.py'), ('procload.py', 'procload.py'),
                  ('queue_fs12c.py', 'queue_fs13c.py'), ('run_safety99.py', 'run_safety99.py'), ('runchk_fs12c.py', 'runchk_fs13c.py'),
                  ('sheet142.py', 'sheet142.py'), ('snap_fs12c.py', 'snap_fs13c.py'), ('wait_fs12c.sh', 'wait_fs13c.sh'),
                  ('chk_fs12c.sh', 'chk_fs13c.sh'), ('gates.req', 'gates.req'), ('sample.req', 'sample.req'),
                  ('gates_default.txt', 'gates_default.txt'), ('tempo_fs12c.py', 'tempo_fs13c.py')):
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
old = b"ROOT = pathlib.Path('C:/kyty/f287/fs12c')"
assert b.count(old) == 1
b = b.replace(old, b"ROOT = pathlib.Path('C:/kyty/f287/fs13c')")
b = (b'# Track F link FS13c (HPP-789; ROADMAP s122 item 697 (g)(3)): the FS12c file of this role with ROOT moved (f287/fs12c to f287/fs13c);\n'
     b'# nothing else changed.\n') + b
open(os.path.join(DST, 'enter_scene.py'), 'wb').write(b)
ROWS.append('enter_scene.py ROOT moved')
for name in ('go_fs13c.sh', 'launch_fs13c.sh', 'post_fs13c.sh', 'fs13c_read.py', 'test_fs13c_read.py', 'test_tools_fs13c.py', 'refs_fs13c.py',
             'regress_fs13c.py', 'mk_fs13c.py'):
    b = open(os.path.join(DRAFT, name), 'rb').read().replace(b'\r\n', b'\n')
    assert all(c < 128 for c in b), name
    open(os.path.join(DST, name), 'wb').write(b)
    ROWS.append('draft %s' % name)
for r in ROWS:
    print(r)
print('ALL OK')
