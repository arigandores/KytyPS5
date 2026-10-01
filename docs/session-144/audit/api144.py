# api144.py - Session Auditor s144 step 3 (HPP-333): read-only API pass over the chain and track issues.
# (1) createdAt / startedAt / completedAt / status / review stage of the s144 chain and of the s143 close link;
# (2) comments of every issue HPP-283..HPP-352 created inside the lock windows of runs144/lock.log (author role, time; no text).
# Needs PAPERCLIP_API_URL / PAPERCLIP_API_KEY in the environment. GET only.
import os, re, json, urllib.request, datetime

UTC = datetime.timezone.utc
base = os.environ['PAPERCLIP_API_URL'].rstrip('/')
if base.endswith('/api'):
    base = base[:-4]
KEY = os.environ['PAPERCLIP_API_KEY']
ROLE = {'06386e1c': 'Session Auditor', '2f5a0935': 'Harness Engineer', '8e98843f': 'Probe Designer', 'aabc0a15': 'Lever Researcher',
        'dc34de0a': 'Red Team', 'eb15eb75': 'Emu Engineer', 'f1276629': 'Roadmap Lead', '641ba04e': 'First agent'}


def get(path):
    rq = urllib.request.Request(base + path, headers={'Authorization': 'Bearer ' + KEY})
    try:
        with urllib.request.urlopen(rq, timeout=30) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {'error': repr(e)[:120]}


def ts(s):
    return datetime.datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=UTC).timestamp()


W = []
cur = {}
for ln in open('C:/kyty/s144/runs144/lock.log', encoding='utf-8').read().splitlines():
    m = re.match(r'lock (taken|released) (\S+) (\S+)Z', ln)
    if m and m.group(1) == 'taken':
        cur[m.group(2)] = ts(m.group(3))
    elif m:
        W.append((m.group(2), cur.pop(m.group(2)), ts(m.group(3))))


def inwin(t):
    for tag, a, b in W:
        if a <= t <= b:
            return tag
    return None


def role(a):
    return ROLE.get((a or '')[:8], (a or 'user/none')[:8])


for n in (301, 330, 331, 332, 333, 334, 3):
    d = get('/api/issues/HPP-%d' % n)
    if 'error' in d:
        print('ISSUE HPP-%d error %s' % (n, d['error']))
        continue
    ep = d.get('executionPolicy') or {}
    st = [(s.get('type'), [role(p.get('agentId')) for p in s.get('participants', [])]) for s in ep.get('stages', [])]
    print('ISSUE %s status %s assignee %s created %s started %s completed %s updated %s review stages %s blockedBy %s' % (
        d.get('identifier'), d.get('status'), role(d.get('assigneeAgentId')), d.get('createdAt'), d.get('startedAt'), d.get('completedAt'), d.get('updatedAt'),
        st, [(b.get('identifier'), b.get('status')) for b in (d.get('blockedBy') or [])]))
tot = 0
inl = []
per = {}
for n in range(283, 353):
    c = get('/api/issues/HPP-%d/comments' % n)
    if isinstance(c, dict):
        c = c.get('comments') or c.get('items') or ([] if 'error' in c else [])
    for x in c:
        tot += 1
        t = ts(x['createdAt'])
        w = inwin(t)
        if w:
            who = role(x.get('authorAgentId') or x.get('authorId'))
            inl.append((x['createdAt'], 'HPP-%d' % n, who, w, len(x.get('body') or '')))
            per[who] = per.get(who, 0) + 1
print('COMMENTS of HPP-283..HPP-352: %d in all; created inside a lock window of sc144: %d; by author %s' % (tot, len(inl), per))
for x in sorted(inl):
    print('   COMMENT-IN-LOCK %s %s by %s under %s (%d chars)' % x)
print('ALL DONE')
