# locks144.py - Session Auditor s144 step 3 (HPP-333): every lock window of 2026-10-01 (session and tracks) from the lock.log
# files under C:/kyty/{s144,s143,p283,f287,s288}; files of the s144 steps 0-1 (and of the lead) and commits against the TRACK
# windows (a session link under a track lock), and the reverse table for the report. READ ONLY.
import os, re, datetime, subprocess

UTC = datetime.timezone.utc
GIT = 'C:/Program Files/Git/cmd/git.exe'


def ts(s):
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC).timestamp()


def iso(t):
    return datetime.datetime.fromtimestamp(t, UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


logs = []
for root in ('C:/kyty/s144', 'C:/kyty/s143', 'C:/kyty/p283', 'C:/kyty/f287', 'C:/kyty/s288'):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('mutwork', 'mutcache', 'mutwork_screen', 'mutcache_screen', '__pycache__') and not d.startswith('vidframes')]
        for f in fn:
            if f == 'lock.log':
                logs.append(os.path.join(dp, f).replace(chr(92), '/'))
W = []
for p in sorted(logs):
    cur = {}
    n = 0
    for ln in open(p, encoding='utf-8', errors='replace').read().splitlines():
        m = re.match(r'lock (taken|released) (\S+) (\S+Z)', ln)
        if not m:
            continue
        if m.group(1) == 'taken':
            cur[m.group(2)] = ts(m.group(3))
        elif m.group(2) in cur:
            a = cur.pop(m.group(2))
            b = ts(m.group(3))
            if a >= ts('2026-10-01T04:40:00Z'):
                W.append((a, b, m.group(2), p))
                n += 1
    print('LOCKLOG %s: windows since 04:40Z %d; taken without release %s' % (p, n, list(cur)))
W.sort()
for a, b, t, p in W:
    if '/s144/' not in p:
        print('WINDOW %s..%s %4.0f s %s (%s)' % (iso(a), iso(b), b - a, t, p.replace('C:/kyty/', '')))
TR = [(a, b, t, p) for a, b, t, p in W if '/s144/' not in p]
print('TRACK WINDOWS since 04:40Z: %d; session windows %d' % (len(TR), len(W) - len(TR)))


def intr(t):
    for a, b, tag, p in TR:
        if a <= t <= b:
            return tag
    return None


# files of the session links (s144 root, non-run files) written inside a TRACK window
hits = []
n = 0
for dp, dn, fn in os.walk('C:/kyty/s144'):
    dn[:] = [d for d in dn if d not in ('mutwork', 'mutcache', 'mutwork_screen', 'mutcache_screen', '__pycache__') and not d.startswith('vidframes')]
    for f in fn:
        p = os.path.join(dp, f).replace(chr(92), '/')
        st = os.stat(p)
        n += 1
        t = intr(st.st_mtime)
        if t:
            hits.append((st.st_mtime, t, p))
print('S144 FILES %d (without mutant work folders and video frame folders); mtime inside a track lock window: %d' % (n, len(hits)))
for m, t, p in sorted(hits)[:40]:
    print('   IN-TRACK-LOCK %s %s %s' % (iso(m), t, p))
for name, root in (('KytyPS5', 'C:/kyty/KytyPS5'), ('ps5-em', 'C:/kyty/KytyPS5/ps5 em')):
    r = subprocess.run([GIT, '-C', root, 'log', '--since=2026-10-01T04:40:00Z', '--format=%h %ct %s'], capture_output=True)
    k = 0
    for ln in r.stdout.decode('utf-8', 'replace').splitlines():
        h, ct, subj = ln.split(' ', 2)
        t = intr(int(ct))
        if t:
            k += 1
            print('   COMMIT-IN-TRACK-LOCK %s %s %s under %s: %s' % (name, h, iso(int(ct)), t, subj[:90].encode('ascii', 'replace').decode()))
    print('COMMITS %s inside a track lock window: %d' % (name, k))
print('ALL DONE')
