"""F20l2 (HPP-648; ROADMAP s122 item 587 (g) - the debt "a detached tag call checks by API before taking the lock that the run which
launched it is alive"): go_f20l2.sh calls this script right before procload.py and the lock.  The issue HPP-648 must have a going run
(executionRunId not empty) equal to the run id the launcher passed (F20L2_RUN_ID, set by launch_f20l2.sh from PAPERCLIP_RUN_ID).  Prints
RUN ALIVE (exit 0), RUN GONE (exit 1: the run was cancelled or ended - the detached call must not start the game), API ERROR (exit 2 -
also a refusal).  --fake <json> (fixtures only) reads the issue json from a file.  ASCII only.
usage: python runchk_f20l2.py [--fake F]"""
import json
import os
import sys
import urllib.request

OWN = 'HPP-648'


def get_issue(fake):
    if fake:
        return json.load(open(fake, encoding='ascii'))
    base = os.environ['PAPERCLIP_API_URL'].rstrip('/')
    if base.endswith('/api'):
        base = base[:-4]
    req = urllib.request.Request('%s/api/issues/%s' % (base, OWN), headers={'Authorization': 'Bearer ' + os.environ['PAPERCLIP_API_KEY']})
    return json.load(urllib.request.urlopen(req, timeout=30))


def main(argv):
    fake = argv[argv.index('--fake') + 1] if '--fake' in argv else None
    want = os.environ.get('F20L2_RUN_ID', '')
    try:
        d = get_issue(fake)
    except Exception as e:  # noqa: BLE001
        print('API ERROR %s' % type(e).__name__)
        return 2
    run = d.get('executionRunId') or ''
    st = d.get('status')
    if want and run == want and st == 'in_progress':
        print('RUN ALIVE %s status %s' % (run[:8], st))
        return 0
    print('RUN GONE want %s issue run %s status %s' % (want[:8] or '-', run[:8] or '-', st))
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
