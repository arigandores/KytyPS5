# window137.py - Session Auditor, s.137 step 5: files modified between the start of step 4 (13:25 UTC) and the pooled reading
# (14:42:53 UTC) - is there a time parser on kp137 logs before the eighth attempt (p.194(e), 197(v))?  mtime = last write only.
import os, datetime as dt
lo = dt.datetime(2026, 9, 30, 13, 25, 0)
hi = dt.datetime(2026, 9, 30, 14, 42, 53)
for root in ('C:/kyty/s137', 'C:/kyty/KytyPS5/docs', 'C:/kyty/KytyPS5/ps5 em/docs', 'C:/kyty/KytyPS5/ps5 em', 'C:/kyty'):
    for dp, dn, fn in os.walk(root):
        dp = dp.replace(chr(92), '/')
        if any(s in dp for s in ('mutwork', 'mutcache', '.git', 'games', '_Shader')):
            continue
        if root in ('C:/kyty/KytyPS5/ps5 em', 'C:/kyty') and dp != root:
            continue
        for f in fn:
            p = dp + '/' + f
            try:
                t = dt.datetime.fromtimestamp(os.path.getmtime(p), dt.UTC).replace(tzinfo=None)
            except OSError:
                continue
            if lo <= t <= hi:
                print(t.time(), p)
