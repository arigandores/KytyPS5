"""M3a2 (HPP-861; ROADMAP s122 item 778 (d)(3)-(8), 783 (b), (d), 786 (g), 787 (g)): copy the helper set of M3a (C:/kyty/m657/m3a,
HPP-842 - itself the FS15c set) into C:/kyty/m657/m3a2 with the names moved; nothing else changed.  The chain (go/launch/chk/wait/post),
the reader and the gate tools of M3a2 are new files (ports), not made here.  Prints one line per file: src sha256 -> dst sha256 and the
count of each replacement.  Refuses under the lock (exit 3) and with the stop file C:/kyty/m657/STOP (exit 4).  ASCII only."""
import hashlib
import os
import re
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('lock held - exit 3')
    sys.exit(3)
if os.path.exists('C:/kyty/m657/STOP'):
    print('STOP - exit 4')
    sys.exit(4)
SRC = 'C:/kyty/m657/m3a'
DST = 'C:/kyty/m657/m3a2'
FILES = (
    ('enter_scene.py', 'enter_scene.py'), ('procload.py', 'procload.py'), ('dispstate.py', 'dispstate.py'),
    ('idle142.py', 'idle142.py'), ('launch_run.py', 'launch_run.py'), ('run_safety99.py', 'run_safety99.py'),
    ('sheet142.py', 'sheet142.py'), ('gates_default.txt', 'gates_default.txt'), ('gates.req', 'gates.req'),
    ('sample.req', 'sample.req'), ('manifest_fs4c.py', 'manifest_fs4c.py'),
    ('guard_m3a.py', 'guard_m3a2.py'), ('hold_m3a.py', 'hold_m3a2.py'), ('hostload_m3a.py', 'hostload_m3a2.py'),
    ('snap_m3a.py', 'snap_m3a2.py'), ('mfsub_m3a.py', 'mfsub_m3a2.py'), ('runchk_m3a.py', 'runchk_m3a2.py'),
    ('queue_m3a.py', 'queue_m3a2.py'), ('tempo_m3a.py', 'tempo_m3a2.py'), ('watch_m3a.py', 'watch_m3a2.py'),
    ('kset_m3a.py', 'kset_m3a2.py'),
)
REPL = (
    (rb'HPP-842', b'HPP-861'),
    (rb'm3a(?!2)', b'm3a2'), (rb'M3A(?!2)', b'M3A2'), (rb'M3a(?!2)', b'M3a2'),
)


def sha(b):
    return hashlib.sha256(b).hexdigest()


os.makedirs(DST, exist_ok=True)
for s, d in FILES:
    raw = open(os.path.join(SRC, s), 'rb').read()
    out = raw
    counts = []
    for a, b in REPL:
        out, n = re.subn(a, b, out)
        counts.append('%s:%d' % (b.decode(), n))
    with open(os.path.join(DST, d), 'wb') as f:
        f.write(out)
    print('%s %s -> %s %s  %s' % (s, sha(raw)[:16], d, sha(out)[:16], ' '.join(c for c in counts if not c.endswith(':0'))))
print('ALL OK')
