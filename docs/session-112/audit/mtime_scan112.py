# Protocol lens (audit 112, adapted): files under C:/kyty and the emulator folder modified inside the sealed-run windows.
import os, sys, datetime as dt
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
WIN = [('go112', '2026-09-24 07:50:11', '2026-09-24 08:08:55')]
W = [(n, dt.datetime.fromisoformat(a).timestamp(), dt.datetime.fromisoformat(b).timestamp()) for n, a, b in WIN]
roots = ['C:/kyty', 'C:/Users/<user>/OneDrive/Desktop/ps5 em']
hits = []; scanned = 0
for root in roots:
    for base, dirs, files in os.walk(root):
        if '.git' in dirs and base.endswith('KytyPS5'): dirs.remove('.git')
        for fn in files:
            p = os.path.join(base, fn)
            try: m = os.stat(p).st_mtime
            except OSError: continue
            scanned += 1
            for n, a, b in W:
                if a <= m <= b:
                    hits.append((n, dt.datetime.fromtimestamp(m).strftime('%H:%M:%S'), p.replace(os.sep, '/')))
print('scanned', scanned)
for h in sorted(hits, key=lambda x: x[1]): print(*h)
