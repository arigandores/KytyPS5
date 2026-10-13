"""M3a (HPP-842; ROADMAP item 756 (g)(3)-(7), 761 (d)-(e), 763 (v)): copy the helper set of FS15c (C:/kyty/f287/fs15c, HPP-822)
into C:/kyty/m657/m3a with the names moved; nothing else changed.  The chain (go/launch/chk/wait/post), the reader and the gate
tools of M3a are new files, not made here.  Prints one line per file: src sha256 -> dst sha256 and the count of each replacement.
Refuses under the lock (exit 3) and with the stop file C:/kyty/m657/STOP (exit 4).  ASCII only."""
import hashlib
import os
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('lock held - exit 3')
    sys.exit(3)
if os.path.exists('C:/kyty/m657/STOP'):
    print('STOP - exit 4')
    sys.exit(4)
SRC = 'C:/kyty/f287/fs15c'
DST = 'C:/kyty/m657/m3a'
FILES = (
    ('enter_scene.py', 'enter_scene.py'), ('procload.py', 'procload.py'), ('dispstate.py', 'dispstate.py'),
    ('idle142.py', 'idle142.py'), ('launch_run.py', 'launch_run.py'), ('run_safety99.py', 'run_safety99.py'),
    ('sheet142.py', 'sheet142.py'), ('gates_default.txt', 'gates_default.txt'), ('gates.req', 'gates.req'),
    ('sample.req', 'sample.req'), ('manifest_fs4c.py', 'manifest_fs4c.py'),
    ('guard_fs15c.py', 'guard_m3a.py'), ('hold_fs15c.py', 'hold_m3a.py'), ('hostload_fs15c.py', 'hostload_m3a.py'),
    ('snap_fs15c.py', 'snap_m3a.py'), ('mfsub_fs15c.py', 'mfsub_m3a.py'), ('runchk_fs15c.py', 'runchk_m3a.py'),
    ('queue_fs15c.py', 'queue_m3a.py'), ('tempo_fs15c.py', 'tempo_m3a.py'), ('watch_fs15c.py', 'watch_m3a.py'),
)
REPL = (
    ('C:/kyty/f287/fs15c', 'C:/kyty/m657/m3a'),
    ('C:/kyty/f287/STOP', 'C:/kyty/m657/STOP'),
    ('C:/kyty/f287/times.txt', 'C:/kyty/m657/m3a/times.txt'),
    ('HPP-822', 'HPP-842'),
    ('fs15c', 'm3a'), ('FS15C', 'M3A'), ('FS15c', 'M3a'),
)


def sha(b):
    return hashlib.sha256(b).hexdigest()


for s, d in FILES:
    raw = open(os.path.join(SRC, s), 'rb').read()
    out = raw
    counts = []
    for a, b in REPL:
        n = out.count(a.encode())
        out = out.replace(a.encode(), b.encode())
        counts.append('%s:%d' % (b, n))
    with open(os.path.join(DST, d), 'wb') as f:
        f.write(out)
    print('%s %s -> %s %s  %s' % (s, sha(raw)[:16], d, sha(out)[:16], ' '.join(c for c in counts if not c.endswith(':0'))))
print('ALL OK')
