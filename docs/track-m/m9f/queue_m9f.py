"""Track M link M9f (HPP-871; ROADMAP s122 item 785 (v)(5), 322 (g)): the lock queue check before a tag.  Port of queue_m6c.py
(M6c, HPP-850) with one rule added: item 785 (v)(5) - "at simultaneous readiness M3a2 / M3b2 (HPP-861, HPP-862) go ahead of T188".
A run link is an issue of the Harness Engineer agent (the only agent that starts the game) other than HPP-871; it is READY when its status
is todo or in_progress, or a run of it is going (executionRunId not empty).  QUEUE BUSY when (a) a ready link of track P exists (item
322 (g)) or (b) HPP-861 (M3a2, the locked series of the gates M3 wave 2) is ready - its series goes first.  HPP-862 (M3b2, the lead's
reading; it takes no lock) is fetched and printed as a reference row: M3b2 is ahead only through the tags it orders, which M3a2 runs.
The track of a link is read from its title ('\u0442\u0440\u0435\u043a P' / 'track P' -> P, the same for F, S, M).  Prints one line per
open link and QUEUE FREE (exit 0) or QUEUE BUSY (exit 1); exit 2 when the API does not answer.  --fake F (fixtures only) reads the issue
list from a json file (a list, or {"issues": [...], "extra": [...]} - extra stands for the issues fetched by id).  ASCII only.
usage: python queue_m9f.py [--fake F]"""
import json
import os
import sys
import urllib.request

OWN = 'HPP-871'
AHEAD = 'HPP-861'
REF = 'HPP-862'
TRACK_WORD = ('\u0442\u0440\u0435\u043a ', 'track ')


def track_of(title):
    t = title or ''
    for w in TRACK_WORD:
        i = t.find(w)
        if i >= 0 and i + len(w) < len(t):
            c = t[i + len(w)]
            if c in 'PFSM':
                return c
    return '?'


def api(path):
    base = os.environ['PAPERCLIP_API_URL'].rstrip('/')
    if base.endswith('/api'):
        base = base[:-4]
    req = urllib.request.Request(base + path, headers={'Authorization': 'Bearer ' + os.environ['PAPERCLIP_API_KEY']})
    return json.load(urllib.request.urlopen(req, timeout=30))


def load(fake):
    if fake:
        d = json.load(open(fake, encoding='utf-8'))
        if isinstance(d, list):
            return d, []
        return d.get('issues', []), d.get('extra', [])
    d = api('/api/companies/%s/issues?assigneeAgentId=%s&limit=200' % (os.environ['PAPERCLIP_COMPANY_ID'], os.environ['PAPERCLIP_AGENT_ID']))
    d = d if isinstance(d, list) else d.get('issues', [])
    have = set(i.get('identifier') for i in d)
    extra = [api('/api/issues/%s' % k) for k in (AHEAD, REF) if k not in have]
    return d, extra


def ready_of(i):
    return i.get('status') in ('todo', 'in_progress') or bool(i.get('executionRunId'))


def main(argv):
    fake = argv[argv.index('--fake') + 1] if '--fake' in argv else None
    try:
        d, extra = load(fake)
    except Exception as e:  # noqa: BLE001
        print('API error %s' % type(e).__name__)
        return 2
    busy = []
    seen = set()
    for i in list(d) + list(extra):
        ident = i.get('identifier')
        if ident in seen:
            continue
        seen.add(ident)
        st = i.get('status')
        if ident == OWN or (st in ('done', 'cancelled') and ident not in (AHEAD, REF)):
            continue
        run = bool(i.get('executionRunId'))
        ready = ready_of(i) and st not in ('done', 'cancelled')
        tr = track_of(i.get('title'))
        note = ''
        if ident == AHEAD:
            note = ' (M3a2: ahead at simultaneous readiness, item 785 (v)(5))'
        elif ident == REF:
            note = ' (M3b2: reference row, takes no lock)'
        print('%s %s track %s run=%s ready=%s%s' % (ident, st, tr, 'y' if run else 'n', 'y' if ready else 'n', note))
        if ready and (tr == 'P' or ident == AHEAD):
            busy.append(ident)
    if AHEAD not in seen:
        print('%s not fetched - QUEUE BUSY by rule (the series ahead is not known)' % AHEAD)
        busy.append(AHEAD + '?')
    print('QUEUE %s%s' % ('BUSY: ' if busy else 'FREE', ' '.join(busy)))
    return 1 if busy else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
