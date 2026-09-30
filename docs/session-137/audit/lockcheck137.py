# lockcheck137.py - Session Auditor, s.137 step 5 (HPP-255): were files written or commits made while the lock
# C:/kyty/SEALED_RUN.lock was held by a go137a.sh call (ROADMAP p.25(g), 197(b)(4))?  Lock intervals from go137a.log:
# "installed before" (the lock is taken right before the install) .. "restored" (the lock is removed after the restore);
# go137a.log time is local UTC+2.  Every file under C:/kyty/s137 and C:/kyty/KytyPS5/docs (mtime, UTC) and every commit of
# both repositories (committer time) inside an interval is listed; files the chain itself writes for the tag are excluded.
import os, re, subprocess, datetime as dt

LOG = 'C:/kyty/s137/go137a.log'
DAY = dt.date(2026, 9, 30)
iv, cur = [], {}
for ln in open(LOG, encoding='utf-8', errors='replace'):
    m = re.match(r'\[(\d\d):(\d\d):(\d\d)\] (.*)', ln)
    if not m:
        continue
    t = dt.datetime(DAY.year, DAY.month, DAY.day, int(m.group(1)), int(m.group(2)), int(m.group(3))) - dt.timedelta(hours=2)
    s = m.group(4)
    r = re.match(r'go137a\.sh (\S+) requested', s)
    if r:
        cur = dict(tag=r.group(1))
    if s.startswith('installed before') and cur:
        cur['start'] = t
    if s.startswith('restored') and cur.get('start'):
        cur['end'] = t
        iv.append(cur)
        cur = {}
print('lock intervals (UTC, from go137a.log "installed before" .. "restored"):')
for x in iv:
    print('  %-8s %s .. %s (%d s)' % (x['tag'], x['start'].time(), x['end'].time(), (x['end'] - x['start']).total_seconds()))


def inside(t):
    for x in iv:
        if x['start'] <= t <= x['end'] + dt.timedelta(seconds=1):
            return x['tag']
    return None


CHAIN = re.compile(r'(log_|stdout_|gpuclk_|hostdev_|envchk_|attempt_|score_|gates_)(\w+)\.(txt|csv)$|^(\w+)\.(json|stdout\.txt|score\.json)$')
hits = []
for root in ('C:/kyty/s137', 'C:/kyty/KytyPS5/docs', 'C:/kyty/KytyPS5/ps5 em/docs'):
    for dp, dn, fn in os.walk(root):
        if 'audit137' in dp or 'mutwork' in dp or 'mutcache' in dp:
            continue
        for f in fn:
            p = os.path.join(dp, f).replace('\\', '/')
            t = dt.datetime.utcfromtimestamp(os.path.getmtime(p))
            tag = inside(t)
            if not tag:
                continue
            m = CHAIN.search(f)
            own = False
            if m:
                g = m.group(2) or m.group(4)
                own = (g == tag)
            if f in ('go137a.log', 'calls.log', 'sample.req', 'gates.req', 'ct.txt') or '__pycache__' in dp:
                own = True
            if not own:
                hits.append((t, tag, p))
for repo in ('C:/kyty/KytyPS5', 'C:/kyty/KytyPS5/ps5 em'):
    out = subprocess.run(['git', '-C', repo, 'log', '--since=2026-09-30T09:00:00Z', '--format=%H %cI %s'], capture_output=True,
                         text=True, encoding='utf-8').stdout
    for ln in out.splitlines():
        h, ts, subj = ln.split(' ', 2)
        t = dt.datetime.fromisoformat(ts).astimezone(dt.timezone.utc).replace(tzinfo=None)
        tag = inside(t)
        if tag:
            hits.append((t, tag, 'COMMIT %s %s %s' % (repo, h[:8], subj[:80])))
print('files / commits inside a lock interval (not the chain\'s own files of that tag): %d' % len(hits))
for t, tag, p in sorted(hits):
    print('  %s under %s: %s' % (t.time(), tag, p))
