"""F42c (HPP-781): build C:/kyty/f287/f42c from the F44c tools (names moved) and the drafts of this link (go / launch / post / chk, the
reader, series_f42c.py, the fixtures, the regression, the tool fixtures, the refs check, beside this file).  LF output.  ASCII only.
Refuses under the lock or the stop file and when f42c/runs already has a call or f42c/series exists.
usage: python mk_f42c.py <draft dir>"""
import os
import sys

SRC = 'C:/kyty/f287/f44c'
DST = 'C:/kyty/f287/f42c'
DRAFT = sys.argv[1]
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    print('lock or STOP - nothing written')
    sys.exit(3)
if os.path.isdir(DST + '/runs') and any(n.startswith(('f20_', 'f42c_ret')) for n in os.listdir(DST + '/runs')):
    print('a call exists under f42c/runs - nothing written')
    sys.exit(3)
if os.path.exists(DST + '/series'):
    print('f42c/series exists - nothing written')
    sys.exit(3)
for d in ('runs', 'pred', 'base', 'old'):
    os.makedirs(DST + '/' + d, exist_ok=True)


def moved(b):
    for a, z in ((b'f44c', b'f42c'), (b'F44C', b'F42C'), (b'F44c', b'F42c'), (b'HPP-793', b'HPP-781')):
        b = b.replace(a, z)
    return b


HDR = b'# Track F link F42c (HPP-781; ROADMAP s122 item 694 (g)(6)): copy of the F44c (HPP-793) file %s with the names moved (f44c -> f42c, F44C -> F42C, F44c -> F42c, HPP-793 -> HPP-781); no change of meaning.\n'
ROWS = []
for name, new in (('dispstate.py', 'dispstate.py'), ('guard_f44c.py', 'guard_f42c.py'), ('hold_f44c.py', 'hold_f42c.py'),
                  ('hostload_f44c.py', 'hostload_f42c.py'), ('idle142.py', 'idle142.py'), ('launch_run.py', 'launch_run.py'),
                  ('manifest_fs4c.py', 'manifest_fs4c.py'), ('procload.py', 'procload.py'), ('queue_f44c.py', 'queue_f42c.py'),
                  ('run_safety99.py', 'run_safety99.py'), ('runchk_f44c.py', 'runchk_f42c.py'), ('sheet142.py', 'sheet142.py'),
                  ('wait_f44c.sh', 'wait_f42c.sh'), ('gates.req', 'gates.req'), ('sample.req', 'sample.req'),
                  ('gates_default.txt', 'gates_default.txt'), ('tempo_f44c.py', 'tempo_f42c.py')):
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
old = b"ROOT = pathlib.Path('C:/kyty/f287/f44c')"
assert b.count(old) == 1
b = b.replace(old, b"ROOT = pathlib.Path('C:/kyty/f287/f42c')")
b = (b'# Track F link F42c (HPP-781; ROADMAP s122 item 694 (g)(6)): the F44c file of this role with ROOT moved (f287/f44c to f287/f42c);\n'
     b'# nothing else changed.\n') + b
open(os.path.join(DST, 'enter_scene.py'), 'wb').write(b)
ROWS.append('enter_scene.py ROOT moved')
for name in ('go_f42c.sh', 'launch_f42c.sh', 'post_f42c.sh', 'chk_f42c.sh', 'f42c_read.py', 'series_f42c.py', 'test_f42c_read.py',
             'regress_f42c.py', 'test_tools_f42c.py', 'refs_f42c.py', 'mk_f42c.py'):
    b = open(os.path.join(DRAFT, name), 'rb').read().replace(b'\r\n', b'\n')
    assert all(c < 128 for c in b), name
    open(os.path.join(DST, name), 'wb').write(b)
    ROWS.append('draft %s' % name)
for r in ROWS:
    print(r)
print('ALL OK')
