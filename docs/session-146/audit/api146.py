# api146.py - Session Auditor, s146 step 3 (HPP-389): read-only API pass (a port of the auditor's own api145.py).
# (1) status / assignee / review stage / monitor of the s146 chain, of the track chains and of every other
#     issue HPP-283..HPP-400 that is not done or carries a monitor (trap 12: a monitor write that wipes the review stage);
# (2) comments of every issue HPP-283..HPP-400 and of HPP-3 created inside the session lock windows of runs146/lock.log
#     (author role, time, length; no text);
# (3) activity of the chain and track issues: writes of executionPolicy with the number of stages before / after (trap 12).
# Needs PAPERCLIP_API_URL / PAPERCLIP_API_KEY / PAPERCLIP_COMPANY_ID in the environment. GET only.
import os, re, json, urllib.request, datetime

UTC = datetime.timezone.utc
base = os.environ['PAPERCLIP_API_URL'].rstrip('/')
if base.endswith('/api'):
    base = base[:-4]
KEY = os.environ['PAPERCLIP_API_KEY']
CO = os.environ.get('PAPERCLIP_COMPANY_ID', '')
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
for ln in open('C:/kyty/s146/runs146/lock.log', encoding='utf-8').read().splitlines():
    m = re.match(r'lock (taken|released) (\S+) (\S+)Z', ln)
    if m and m.group(1) == 'taken':
        cur[m.group(2)] = ts(m.group(3))
    elif m:
        W.append((m.group(2), cur.pop(m.group(2)), ts(m.group(3))))
SER = (W[1][1], W[-1][2])


def inwin(t):
    for tag, a, b in W:
        if a <= t <= b:
            return tag
    return None


def role(a):
    return ROLE.get((a or '')[:8], (a or 'user/none')[:8])


CHAIN = {354: 's145 4', 386: 's146 0', 387: 's146 1', 395: 's146 1b', 388: 's146 2', 389: 's146 3', 390: 's146 4', 391: 'P19', 392: 'P20', 393: 'P21', 394: 'P22',
         375: 'F6c', 376: 'F6d', 377: 'F6e', 378: 'F6f', 381: 'FS2a', 382: 'FS2b', 383: 'FS2c', 384: 'FS2d', 364: 'P17', 365: 'P18'}
issues = {}
ids = {}
for n in [3] + list(range(283, 401)):
    d = get('/api/issues/HPP-%d' % n)
    if 'error' in d or not d.get('identifier'):
        continue
    issues[n] = d
    ids[n] = d.get('id')
print('ISSUES read %d (HPP-3, HPP-283..HPP-400)' % len(issues))
nostage = []
for n, d in sorted(issues.items()):
    ep = d.get('executionPolicy') or {}
    st = [(s.get('type'), [role(p.get('agentId')) for p in s.get('participants', [])]) for s in ep.get('stages', [])]
    mon = ep.get('monitor')
    lead = role(d.get('assigneeAgentId')) == 'Roadmap Lead'
    show = n in CHAIN or n == 3 or d.get('status') != 'done' or mon
    if not lead and not st and n >= 386:
        nostage.append((d.get('identifier'), d.get('status'), role(d.get('assigneeAgentId'))))
    if show:
        print('ISSUE %s [%s] status %s assignee %s created %s started %s completed %s review stages %s monitor %s blockedBy %s' % (
            d.get('identifier'), CHAIN.get(n, ''), d.get('status'), role(d.get('assigneeAgentId')), str(d.get('createdAt'))[:19], str(d.get('startedAt'))[:19],
            str(d.get('completedAt'))[:19], st, (mon.get('serviceName'), str(mon.get('nextCheckAt'))[:19]) if mon else None,
            [(b.get('identifier'), b.get('status')) for b in (d.get('blockedBy') or [])]))
print('ISSUES HPP-386.. of an executor (assignee not the lead) WITHOUT a review stage now: %d %s' % (len(nostage), nostage))
tot = 0
inl = []
ser = {}
per = {}
for n in sorted(issues):
    c = get('/api/issues/HPP-%d/comments' % n)
    if isinstance(c, dict):
        c = c.get('comments') or c.get('items') or ([] if 'error' in c else [])
    for x in c:
        tot += 1
        t = ts(x['createdAt'])
        w = inwin(t)
        who = role(x.get('authorAgentId') or x.get('authorId'))
        if w:
            inl.append((x['createdAt'][:19], 'HPP-%d' % n, who, w, len(x.get('body') or '')))
            per[who] = per.get(who, 0) + 1
        elif SER[0] <= t <= SER[1]:
            ser[(who, 'HPP-%d' % n)] = ser.get((who, 'HPP-%d' % n), 0) + 1
print('COMMENTS of %d issues: %d in all; created inside a session lock window of s146 (warm-up and series): %d; by author %s' % (len(issues), tot, len(inl), per))
for x in sorted(inl):
    print('   COMMENT-IN-LOCK %s %s by %s under %s (%d chars)' % x)
print('COMMENTS inside the series window but outside the locks, by author and issue: %s' % sorted(ser.items()))
# (3) executionPolicy writes
for n in (386, 387, 395, 388, 389, 377, 391, 392, 393, 383, 364, 365, 315):
    if n not in ids:
        continue
    a = get('/api/companies/%s/activity?entityId=%s&limit=500' % (CO, ids[n]))
    if isinstance(a, dict):
        a = a.get('items') or a.get('activity') or a.get('data') or []
    ev = []
    for x in a:
        det = x.get('details') or x.get('metadata') or {}
        s = json.dumps(det)
        if 'executionPolicy' in s or 'reviewers' in str(x.get('action', '')) or 'stages' in s:
            new = det.get('executionPolicy') if isinstance(det.get('executionPolicy'), dict) else None
            prev = (det.get('_previous') or det.get('previous') or {}).get('executionPolicy') if isinstance(det.get('_previous') or det.get('previous'), dict) else None
            ev.append((str(x.get('createdAt'))[:19], x.get('action'), role(x.get('agentId') or x.get('actorId')),
                       len((new or {}).get('stages') or []) if new is not None else None, len((prev or {}).get('stages') or []) if prev is not None else None,
                       ((new or {}).get('monitor') or {}).get('serviceName') if new else None))
    print('ACTIVITY HPP-%d: events %d; policy / reviewer events %d' % (n, len(a), len(ev)))
    for e in sorted(ev):
        print('   %s %s by %s stages after %s (before %s) monitor %s' % e)
print('ALL DONE')
