"""F27c (HPP-694; copy of FS10c queue_fs10c.py with OWN moved).  Before: F25m (HPP-686; copy of F24e queue_f24e.py with OWN moved - the same rule for every F run link).  Before: F24e (HPP-664; ROADMAP s122 item 595 (zh), item 322 (g): the lock queue P > F > S): the lock queue check before a tag.  Port of F20l3
queue_f20l3.py (there F20 was the last in the queue, item 462 (g)); here F24e is a link of the track F: a tag is taken only when no run link
of the track P has a ready input.  A run link is an issue of the Harness Engineer agent (the only agent that starts the game) other than
HPP-694; it is READY when its status is todo or in_progress, or a run of it is going (executionRunId not empty).  The track of a link is read
from its title ('\u0442\u0440\u0435\u043a P' / 'track P' -> P, the same for F and S).  Links of F and S are printed (reference) and do not
hold the queue: F links take the lock by the gate in turn (executor variant, seal section 5); the lock file itself is the exclusion.
Prints one line per open link and QUEUE FREE (exit 0) or QUEUE BUSY (exit 1); exit 2 when the API does not answer.  --fake F (fixtures
only) reads the issue list from a json file.  ASCII only.
usage: python queue_f27c.py [--fake F]"""
import json
import os
import sys
import urllib.request

OWN = 'HPP-694'
TRACK_WORD = ('\u0442\u0440\u0435\u043a ', 'track ')


def track_of(title):
    t = title or ''
    for w in TRACK_WORD:
        i = t.find(w)
        if i >= 0 and i + len(w) < len(t):
            c = t[i + len(w)]
            if c in 'PFS':
                return c
    return '?'


def load(fake):
    if fake:
        return json.load(open(fake, encoding='utf-8'))
    base = os.environ['PAPERCLIP_API_URL'].rstrip('/')
    if base.endswith('/api'):
        base = base[:-4]
    url = '%s/api/companies/%s/issues?assigneeAgentId=%s&limit=200' % (base, os.environ['PAPERCLIP_COMPANY_ID'], os.environ['PAPERCLIP_AGENT_ID'])
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + os.environ['PAPERCLIP_API_KEY']})
    return json.load(urllib.request.urlopen(req, timeout=30))


def main(argv):
    fake = argv[argv.index('--fake') + 1] if '--fake' in argv else None
    try:
        d = load(fake)
    except Exception as e:  # noqa: BLE001
        print('API error %s' % type(e).__name__)
        return 2
    d = d if isinstance(d, list) else d.get('issues', [])
    busy = []
    for i in d:
        st = i.get('status')
        if st in ('done', 'cancelled') or i.get('identifier') == OWN:
            continue
        run = bool(i.get('executionRunId'))
        ready = st in ('todo', 'in_progress') or run
        tr = track_of(i.get('title'))
        print('%s %s track %s run=%s ready=%s' % (i.get('identifier'), st, tr, 'y' if run else 'n', 'y' if ready else 'n'))
        if ready and tr == 'P':
            busy.append(i.get('identifier'))
    print('QUEUE %s%s' % ('BUSY: ' if busy else 'FREE', ' '.join(busy)))
    return 1 if busy else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
