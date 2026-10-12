# Track F link F47i (HPP-826; ROADMAP s122 item 740 (v)(3), 742 (e), 744 (g)-(d)): copy of the F47d (HPP-809) file queue_f47d.py with the names moved (f47d -> f47i, F47D -> F47I, F47d -> F47i, HPP-809 -> HPP-826); no change of meaning.
"""Track F link F47i (HPP-826; ROADMAP s122 item 322 (g), item 714 (b)(2), general rule 27): the lock queue check before a tag.  Port of
C:/kyty/f287/f46c/queue_f46c.py (a run link of the track P with a ready input holds the queue: P > F > S) with one more rule of item 714
(b)(2) - 'between the tags of another series nobody is inserted': a run link of the Harness Engineer (the only agent that starts the
game) other than HPP-826, of ANY track, with status in_progress and a going run (executionRunId not empty) may be inside its series - it
holds the queue too (conservative reading of the executor; the end of such a series is read from its comment 'end of the series' and
then F47I_QUEUE_OK=<issue> set after a times.txt line lets that one issue pass).  Prints one line per open link and QUEUE FREE (exit 0)
or QUEUE BUSY (exit 1); exit 2 when the API does not answer.  --fake F (fixtures only) reads the issue list from a json file.  ASCII only.
usage: python queue_f47i.py [--fake F]"""
import json
import os
import sys
import urllib.request

OWN = 'HPP-826'
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
    ok_ids = set(x for x in (os.environ.get('F47I_QUEUE_OK') or '').split(',') if x)
    try:
        d = load(fake)
    except Exception as e:  # noqa: BLE001
        print('API error %s' % type(e).__name__)
        return 2
    d = d if isinstance(d, list) else d.get('issues', [])
    busy = []
    for i in d:
        st = i.get('status')
        ident = i.get('identifier')
        if st in ('done', 'cancelled') or ident == OWN:
            continue
        run = bool(i.get('executionRunId'))
        ready = st in ('todo', 'in_progress') or run
        tr = track_of(i.get('title'))
        series = st == 'in_progress' and run
        print('%s %s track %s run=%s ready=%s series=%s' % (ident, st, tr, 'y' if run else 'n', 'y' if ready else 'n', 'y' if series else 'n'))
        if ready and tr == 'P':
            busy.append(ident)
        elif series and ident not in ok_ids:
            busy.append(ident)
    print('QUEUE %s%s' % ('BUSY: ' if busy else 'FREE', ' '.join(busy)))
    return 1 if busy else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
