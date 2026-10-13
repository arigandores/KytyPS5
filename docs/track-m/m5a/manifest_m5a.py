"""M5a (HPP-845): sha256 of every file of docs/track-m/m5a (except sha256.txt itself) -> sha256.txt; also checks that no
committed text carries a user-profile path. Prints the table and ALL OK / FAIL. Refuses to run under C:/kyty/SEALED_RUN.lock.
Usage: python manifest_m5a.py   (run inside the folder)"""
import hashlib, os, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
root = os.path.dirname(os.path.abspath(__file__))
bad = [b'C:/' + b'Users/', b'C:' + bytes([92]) + b'Users', b'App' + b'Data']
rows, ok = [], True
for d, _, fs in os.walk(root):
    if '__pycache__' in d:
        continue
    for f in sorted(fs):
        p = os.path.join(d, f)
        rel = os.path.relpath(p, root).replace(os.sep, '/')
        if rel == 'sha256.txt':
            continue
        b = open(p, 'rb').read()
        for k in bad:
            if k in b:
                print('PRIVATE PATH in', rel, k)
                ok = False
        rows.append('%s  %s' % (hashlib.sha256(b).hexdigest(), rel))
rows.sort(key=lambda r: r.split('  ', 1)[1])
open(os.path.join(root, 'sha256.txt'), 'w', newline='\n').write('\n'.join(rows) + '\n')
print('\n'.join(rows))
print('files', len(rows))
print('ALL OK' if ok else 'FAIL')
