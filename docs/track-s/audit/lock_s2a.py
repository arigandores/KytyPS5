# S2a (HPP-312): mtimes (UTC) of the track S files against the lock windows of s142 (lock.log) and s143.
import os, datetime, re
UTC = datetime.timezone.utc
wins = []
t = open('C:/kyty/s142/runs142/lock.log', encoding='utf-8').read().split()
rows = re.findall(r'lock (taken|released) (\S+) (\S+)', open('C:/kyty/s142/runs142/lock.log', encoding='utf-8').read())
cur = {}
for kind, tag, ts in rows:
    d = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC)
    if kind == 'taken':
        cur[tag] = d
    else:
        wins.append((tag, cur.pop(tag), d))
print('s142 lock windows', len(wins), 'first', wins[0][1].isoformat(), 'last release', wins[-1][2].isoformat(), 'unreleased', list(cur))
for p in ('C:/kyty/s143/runs143/lock.log', 'C:/kyty/s143/runs143', 'C:/kyty/p283/runs', 'C:/kyty/p283/p6', 'C:/kyty/f287/runs', 'C:/kyty/SEALED_RUN.lock'):
    print('exists', p, os.path.exists(p))
files = []
for root in ('C:/kyty/s288/s0', 'C:/kyty/s288/s1', 'C:/kyty/s288/lead', 'C:/kyty/s288/snap0_drv', 'C:/kyty/s288/s3', 'C:/kyty/KytyPS5/docs/track-s'):
    for r, ds, fs in os.walk(root):
        for f in fs:
            p = os.path.join(r, f).replace(os.sep, '/')
            files.append((datetime.datetime.fromtimestamp(os.stat(p).st_mtime, UTC), p))
files.append((datetime.datetime.fromtimestamp(os.stat('C:/kyty/s288/FACTS.md').st_mtime, UTC), 'C:/kyty/s288/FACTS.md'))
files.append((datetime.datetime.fromtimestamp(os.stat('C:/kyty/s288/snap0').st_mtime, UTC), 'C:/kyty/s288/snap0 (dir)'))
files.sort()
inside = [(d, p) for d, p in files for tag, a, b in wins if a <= d <= b]
print('files', len(files), 'earliest', files[0][0].isoformat(), files[0][1])
print('files with mtime inside an s142 lock window:', len(inside))
for d, p in inside:
    print('  ', d.isoformat(), p)
# snap0_drv copies keep the source mtime (copy2): list them apart
pre = [(d, p) for d, p in files if d < wins[-1][2]]
print('files with mtime before the last s142 lock release:', len(pre))
for d, p in pre:
    print('  ', d.isoformat(), p)
for root in ('C:/kyty/s288/s0', 'C:/kyty/s288/s1', 'C:/kyty/s288/lead', 'C:/kyty/s288/s3'):
    ds = [d for d, p in files if p.startswith(root + '/')]
    print(root, 'n', len(ds), 'min', min(ds).strftime('%H:%M:%SZ'), 'max', max(ds).strftime('%H:%M:%SZ'))
