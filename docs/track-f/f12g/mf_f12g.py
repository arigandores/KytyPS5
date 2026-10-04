# Track F link F12g (HPP-481): manifest of a directory tree - one line per file "sha256 size relpath", sorted.  usage: mf_f12g.py <dir> <out>
import hashlib, os, sys
root, outp = sys.argv[1], sys.argv[2]
rows = []
for d, _, fs in os.walk(root):
    for f in fs:
        p = os.path.join(d, f)
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        rows.append('%s %d %s' % (h, os.path.getsize(p), os.path.relpath(p, root).replace(os.sep, '/')))
rows.sort(key=lambda r: r.split(' ', 2)[2])
open(outp, 'wb').write(('\n'.join(rows) + '\n').encode())
print('files', len(rows))
