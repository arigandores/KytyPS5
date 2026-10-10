"""FS12c (HPP-752): build C:/kyty/f287/fs12c from the F33e tools (names moved).  LF output.  ASCII only.
The chain scripts (go / launch / post), the reader and the fixtures are written separately (drafts moved by one command)."""
import os
import sys

SRC = 'C:/kyty/f287/f33e'
DST = 'C:/kyty/f287/fs12c'
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    print('lock or STOP - nothing written')
    sys.exit(3)
for d in ('runs', 'pred', 'base', 'old'):
    os.makedirs(DST + '/' + d, exist_ok=True)


def moved(b):
    for a, z in ((b'f33e', b'fs12c'), (b'F33E', b'FS12C'), (b'F33e', b'FS12c'), (b'HPP-746', b'HPP-752')):
        b = b.replace(a, z)
    return b


HDR = b'# Track F link FS12c (HPP-752; ROADMAP s122 item 683 (g)(3), 686 (v)): copy of the F33e (HPP-746) file %s with the names moved (f33e -> fs12c, F33E -> FS12C, F33e -> FS12c, HPP-746 -> HPP-752); no change of meaning.\n'
ROWS = []
for name, new in (('dispstate.py', 'dispstate.py'), ('guard_f33e.py', 'guard_fs12c.py'), ('hold_f33e.py', 'hold_fs12c.py'),
                  ('hostload_f33e.py', 'hostload_fs12c.py'), ('idle142.py', 'idle142.py'), ('launch_run.py', 'launch_run.py'),
                  ('manifest_fs4c.py', 'manifest_fs4c.py'), ('mfsub_f33e.py', 'mfsub_fs12c.py'), ('procload.py', 'procload.py'),
                  ('queue_f33e.py', 'queue_fs12c.py'), ('run_safety99.py', 'run_safety99.py'), ('runchk_f33e.py', 'runchk_fs12c.py'),
                  ('sheet142.py', 'sheet142.py'), ('snap_f33e.py', 'snap_fs12c.py'), ('wait_f33e.sh', 'wait_fs12c.sh'),
                  ('chk_f33e.sh', 'chk_fs12c.sh'), ('gates.req', 'gates.req'), ('sample.req', 'sample.req'),
                  ('gates_default.txt', 'gates_default.txt'), ('tempo_f33e.py', 'tempo_fs12c.py')):
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
old = b"ROOT = pathlib.Path('C:/kyty/f287/f33e')"
assert b.count(old) == 1
b = b.replace(old, b"ROOT = pathlib.Path('C:/kyty/f287/fs12c')")
b = (b'# Track F link FS12c (HPP-752; ROADMAP s122 item 683 (g)(3)): the F33e file of this role with ROOT moved (f287/f33e to f287/fs12c);\n'
     b'# nothing else changed.\n') + b
open(os.path.join(DST, 'enter_scene.py'), 'wb').write(b)
ROWS.append('enter_scene.py ROOT moved')
for r in ROWS:
    print(r)
print('ALL OK')
