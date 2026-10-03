"""glsha.py - F7b: listing sha of %LOCALAPPDATA%/NVIDIA/GLCache (relative path, size, mtime_ns) - a record, not a guard."""
import hashlib
import os

lad = os.environ.get('LOCALAPPDATA') or os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
root = os.path.join(lad, 'NVIDIA', 'GLCache')
rows = []
for d, _, fs in os.walk(root):
    for f in fs:
        p = os.path.join(d, f)
        st = os.stat(p)
        rows.append('%s|%d|%d' % (os.path.relpath(p, root).replace('\\', '/'), st.st_size, st.st_mtime_ns))
rows.sort()
print('files %d bytes %d listsha %s' % (len(rows), sum(int(r.split('|')[1]) for r in rows),
                                        hashlib.sha256('\n'.join(rows).encode()).hexdigest()))
