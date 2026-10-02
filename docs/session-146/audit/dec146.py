# dec146.py - Session Auditor s146 step 3 (HPP-389): "decision before action" for ROADMAP s122 items 309-320:
# the header time of the item, the commit that carries it, the first action by it (API comment of the lead / call row / lock).
# GET only for the API. No comment text is printed (author role, time, length).
import os, re, json, subprocess, urllib.request, datetime
UTC = datetime.timezone.utc
GIT = 'C:/Program Files/Git/cmd/git.exe'
KY = 'C:/kyty/KytyPS5'
base = os.environ['PAPERCLIP_API_URL'].rstrip('/')
if base.endswith('/api'):
    base = base[:-4]
KEY = os.environ['PAPERCLIP_API_KEY']
ROLE = {'06386e1c': 'Session Auditor', '2f5a0935': 'Harness Engineer', 'dc34de0a': 'Red Team', 'f1276629': 'Roadmap Lead', 'eb15eb75': 'Emu Engineer'}
def get(path):
    rq = urllib.request.Request(base + path, headers={'Authorization': 'Bearer ' + KEY})
    with urllib.request.urlopen(rq, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))
txt = open(KY + '/docs/ROADMAP.md', 'rb').read().decode('utf-8')
items = {}
for m in re.finditer(r'(?m)^(3(?:09|1[0-9]|20))[.] ', txt):
    n = int(m.group(1))
    seg = txt[m.start():m.start() + 1400]
    t = re.search(r'(2026-10-02) (\d\d:\d\d:\d\d) UTC', seg)
    items[n] = t.group(1) + 'T' + t.group(2) + 'Z' if t else None
log = subprocess.run([GIT, '-C', KY, 'log', '--since=2026-10-02T05:40:00Z', '--reverse', '--format=%h %cI %s'], capture_output=True).stdout.decode('utf-8', 'replace').splitlines()
com = {}
for ln in log:
    h, ct, subj = ln.split(' ', 2)
    t = datetime.datetime.fromisoformat(ct).astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    for n in re.findall(r'p[.](3\d\d)', subj):
        com.setdefault(int(n), []).append((t, h))
    print('COMMIT %s %s %s' % (h, t, subj[:90].encode('ascii', 'replace').decode()))
ev = {}
for n in (354, 386, 387, 395, 388, 389, 3, 365):
    c = get('/api/issues/HPP-%d/comments' % n)
    if isinstance(c, dict):
        c = c.get('comments') or c.get('items') or []
    for x in c:
        if x['createdAt'] >= '2026-10-02T05:40':
            ev.setdefault(n, []).append((x['createdAt'][:19] + 'Z', ROLE.get(str(x.get('authorAgentId'))[:8], 'other'), len(x.get('body') or ''), str(x.get('id'))[:8]))
for n in sorted(ev):
    for e in sorted(ev[n]):
        print('COMMENT HPP-%d %s by %s (%d chars) id %s' % ((n,) + e))
for n in sorted(items):
    print('ITEM %d: header time %s; commits naming it %s' % (n, items[n], com.get(n)))
print('ALL DONE')
