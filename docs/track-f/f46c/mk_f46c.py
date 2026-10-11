"""F46c (HPP-800): build C:/kyty/f287/f46c from the F44c tools (names moved) and the drafts of this link (go / launch / post, the reader,
the machine rules, the video measures, their fixtures, the tool fixtures, the regression, the refs check, beside this file).  LF output.
ASCII only.  Refuses under the lock or the stop file and when f46c/runs already has a tag.
usage: python mk_f46c.py <draft dir>"""
import os
import sys

SRC = 'C:/kyty/f287/f44c'
DST = 'C:/kyty/f287/f46c'
DRAFT = sys.argv[1]
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    print('lock or STOP - nothing written')
    sys.exit(3)
if os.path.isdir(DST + '/runs') and any(n.startswith('f26s_') for n in os.listdir(DST + '/runs')):
    print('a tag exists under f46c/runs - nothing written')
    sys.exit(3)
for d in ('runs', 'pred', 'base', 'old'):
    os.makedirs(DST + '/' + d, exist_ok=True)


def moved(b):
    for a, z in ((b'f44c', b'f46c'), (b'F44C', b'F46C'), (b'F44c', b'F46c'), (b'HPP-793', b'HPP-800')):
        b = b.replace(a, z)
    return b


HDR = b'# Track F link F46c (HPP-800; ROADMAP s122 item 702 (g)): copy of the F44c (HPP-793) file %s with the names moved (f44c -> f46c, F44C -> F46C, F44c -> F46c, HPP-793 -> HPP-800); no change of meaning.\n'
ROWS = []
for name, new in (('dispstate.py', 'dispstate.py'), ('guard_f44c.py', 'guard_f46c.py'), ('hold_f44c.py', 'hold_f46c.py'),
                  ('hostload_f44c.py', 'hostload_f46c.py'), ('idle142.py', 'idle142.py'), ('launch_run.py', 'launch_run.py'),
                  ('manifest_fs4c.py', 'manifest_fs4c.py'), ('mfsub_f44c.py', 'mfsub_f46c.py'), ('procload.py', 'procload.py'),
                  ('queue_f44c.py', 'queue_f46c.py'), ('run_safety99.py', 'run_safety99.py'), ('runchk_f44c.py', 'runchk_f46c.py'),
                  ('sheet142.py', 'sheet142.py'), ('snap_f44c.py', 'snap_f46c.py'), ('wait_f44c.sh', 'wait_f46c.sh'),
                  ('chk_f44c.sh', 'chk_f46c.sh'), ('gates.req', 'gates.req'), ('sample.req', 'sample.req'),
                  ('gates_default.txt', 'gates_default.txt'), ('tempo_f44c.py', 'tempo_f46c.py')):
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
old = b"ROOT = pathlib.Path('C:/kyty/f287/f44c')"
assert b.count(old) == 1
b = b.replace(old, b"ROOT = pathlib.Path('C:/kyty/f287/f46c')")
b = (b'# Track F link F46c (HPP-800; ROADMAP s122 item 702 (g)): the F44c file of this role with ROOT moved (f287/f44c to f287/f46c);\n'
     b'# nothing else changed.\n') + b
open(os.path.join(DST, 'enter_scene.py'), 'wb').write(b)
ROWS.append('enter_scene.py ROOT moved')
for name in ('go_f46c.sh', 'launch_f46c.sh', 'post_f46c.sh', 'f46c_read.py', 'next_f46c.py', 'f46c_vid.py', 'test_f46c_read.py',
             'test_next_f46c.py', 'test_f46c_vid.py', 'test_tools_f46c.py', 'regress_f46c.py', 'refs_f46c.py', 'neg_f46c.py',
             'gen_refs_f46c.py', 'mk_f46c.py'):
    p = os.path.join(DRAFT, name)
    if not os.path.exists(p):
        ROWS.append('draft %s ABSENT' % name)
        continue
    b = open(p, 'rb').read().replace(b'\r\n', b'\n')
    assert all(c < 128 for c in b), name
    open(os.path.join(DST, name), 'wb').write(b)
    ROWS.append('draft %s' % name)
for r in ROWS:
    print(r)
print('ALL OK')
