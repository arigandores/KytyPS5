# Protocol lens (audit 111): files under C:/kyty and the emulator folder modified inside the sealed-run windows.
import os, sys, datetime as dt
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
WIN = [('go111', '2026-09-24 04:33:23', '2026-09-24 04:44:26'), ('go111b', '2026-09-24 04:46:51', '2026-09-24 05:05:41'),
       ('go111v', '2026-09-24 05:08:04', '2026-09-24 05:10:41')]
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
