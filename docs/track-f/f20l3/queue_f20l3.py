"""F20l3 (HPP-655; port of F20e queue_f20l3.py, own issue HPP-655; ROADMAP s122 item 462 (g)): the lock queue check - F20 is the last in the lock queue; a tag is taken only when no other
run link of any track (P, F, S) has a ready input.  A run link is an issue of the Harness Engineer agent (the only agent that starts the
game) other than HPP-655; it is READY when its status is todo or in_progress, or a run of it is going (executionRunId not empty) -
a blocked link without a run is not ready.  Prints one line per open link and QUEUE FREE (exit 0) or QUEUE BUSY (exit 1); exit 2 when the
API does not answer.  ASCII only.
usage: python queue_f20l3.py"""
import json
import os
import sys
import urllib.request

OWN = 'HPP-655'


def main():
    base = os.environ['PAPERCLIP_API_URL'].rstrip('/')
    if base.endswith('/api'):
        base = base[:-4]
    url = '%s/api/companies/%s/issues?assigneeAgentId=%s&limit=200' % (base, os.environ['PAPERCLIP_COMPANY_ID'], os.environ['PAPERCLIP_AGENT_ID'])
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + os.environ['PAPERCLIP_API_KEY']})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=30))
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
        print('%s %s run=%s ready=%s' % (i.get('identifier'), st, 'y' if run else 'n', 'y' if ready else 'n'))
        if ready:
            busy.append(i.get('identifier'))
    print('QUEUE %s%s' % ('BUSY: ' if busy else 'FREE', ' '.join(busy)))
    return 1 if busy else 0


if __name__ == '__main__':
    sys.exit(main())
