"""F33e (HPP-746): build C:/kyty/f287/f33e from the F34c tools (names moved) and the FS11c tempo tool.  LF output.  ASCII only."""
import os
import sys

SRC = 'C:/kyty/f287/f34c'
DST = 'C:/kyty/f287/f33e'
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    print('lock or STOP - nothing written')
    sys.exit(3)
os.makedirs(DST + '/runs', exist_ok=True)
os.makedirs(DST + '/pred', exist_ok=True)
os.makedirs(DST + '/base', exist_ok=True)


def moved(b):
    for a, z in ((b'f34c', b'f33e'), (b'F34C', b'F33E'), (b'F34c', b'F33e'), (b'HPP-740', b'HPP-746')):
        b = b.replace(a, z)
    return b


HDR_PY = b'# Track F link F33e (HPP-746; ROADMAP s122 item 675 (d)(4), 682): copy of the F34c (HPP-740) file %s with the names moved (f34c -> f33e, F34C -> F33E, F34c -> F33e, HPP-740 -> HPP-746); no change of meaning.\n'
HDR_SH = HDR_PY
ROWS = []
for name, new in (('dispstate.py', 'dispstate.py'), ('guard_f34c.py', 'guard_f33e.py'), ('hold_f34c.py', 'hold_f33e.py'),
                  ('hostload_f34c.py', 'hostload_f33e.py'), ('idle142.py', 'idle142.py'), ('launch_run.py', 'launch_run.py'),
                  ('manifest_fs4c.py', 'manifest_fs4c.py'), ('mfsub_f34c.py', 'mfsub_f33e.py'), ('procload.py', 'procload.py'),
                  ('queue_f34c.py', 'queue_f33e.py'), ('run_safety99.py', 'run_safety99.py'), ('runchk_f34c.py', 'runchk_f33e.py'),
                  ('sheet142.py', 'sheet142.py'), ('snap_f34c.py', 'snap_f33e.py'), ('wait_f34c.sh', 'wait_f33e.sh'),
                  ('chk_f34c.sh', 'chk_f33e.sh'), ('gates.req', 'gates.req'), ('sample.req', 'sample.req'),
                  ('gates_default.txt', 'gates_default.txt')):
    b = open(os.path.join(SRC, name), 'rb').read().replace(b'\r\n', b'\n')
    nb = moved(b)
    if name.endswith('.py') and nb != b:
        h = HDR_PY % name.encode()
        if nb.startswith(b'#!'):
            i = nb.index(b'\n') + 1
            nb = nb[:i] + h + nb[i:]
        else:
            nb = h + nb
    elif name.endswith('.sh') and nb != b:
        i = nb.index(b'\n') + 1
        nb = nb[:i] + (HDR_SH % name.encode()) + nb[i:]
    open(os.path.join(DST, new), 'wb').write(nb)
    ROWS.append('%s -> %s changed %s' % (name, new, nb != b))
# enter_scene.py: only ROOT moved + a header line (the F34c options stay, all off by default)
b = open(os.path.join(SRC, 'enter_scene.py'), 'rb').read().replace(b'\r\n', b'\n')
old = b"ROOT = pathlib.Path('C:/kyty/f287/f34c')"
assert b.count(old) == 1
b = b.replace(old, b"ROOT = pathlib.Path('C:/kyty/f287/f33e')")
b = (b'# Track F link F33e (HPP-746; ROADMAP s122 item 675 (d)(4)): the F34c file of this role with ROOT moved (f287/f34c to f287/f33e);\n'
     b'# nothing else changed (the F34c options --natural, --until-sublevel, --proc-limit, --entry-at-level are not used by go_f33e.sh).\n'
     b'# Before: ') + b[2:] if b.startswith(b'# ') else b
open(os.path.join(DST, 'enter_scene.py'), 'wb').write(b)
ROWS.append('enter_scene.py ROOT moved')
# tempo from FS11c (names moved)
b = open('C:/kyty/f287/fs11c/tempo_fs11c.py', 'rb').read().replace(b'\r\n', b'\n')
for a, z in ((b'fs11c', b'f33e'), (b'FS11C', b'F33E'), (b'FS11c', b'F33e'), (b'HPP-716', b'HPP-746')):
    b = b.replace(a, z)
b = b'# Track F link F33e (HPP-746; ROADMAP s122 item 675 (d)(4)): copy of the FS11c (HPP-716) file tempo_fs11c.py with the names moved (fs11c -> f33e, FS11c -> F33e, HPP-716 -> HPP-746); no change of meaning.\n' + b
open(os.path.join(DST, 'tempo_f33e.py'), 'wb').write(b)
ROWS.append('tempo_fs11c.py -> tempo_f33e.py')
for r in ROWS:
    print(r)
print('ALL OK')
