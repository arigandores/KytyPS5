# Track F link F30m (HPP-723; ROADMAP s122 item 655 (e)): copy of the F30f (HPP-711) file with the names moved (f287/f30f -> f287/f30m, *_f30f -> *_f30m, F30F_ -> F30M_, HPP-711 -> HPP-723); no change of meaning.
# Track F link F30f (HPP-723): copy of the F29e tool with the names moved (f29e -> f30f, HPP-704 -> HPP-723); no change of meaning.
"""F25m (HPP-723; port of F20l3 runchk_f20l3.py: own issue HPP-723, variable F30M_RUN_ID).  Before: F20l3 (HPP-655; ROADMAP s122 item 587 (g) - the debt "a detached tag call checks by API before taking the lock that the run which
launched it is alive"): go_f20l3.sh calls this script right before procload.py and the lock.  The issue HPP-655 must have a going run
(executionRunId not empty) equal to the run id the launcher passed (F20L3_RUN_ID, set by launch_f20l3.sh from PAPERCLIP_RUN_ID).  Prints
RUN ALIVE (exit 0), RUN GONE (exit 1: the run was cancelled or ended - the detached call must not start the game), API ERROR (exit 2 -
also a refusal).  --fake <json> (fixtures only) reads the issue json from a file.  ASCII only.
usage: python runchk_f20l3.py [--fake F]"""
import json
import os
import sys
import urllib.request

OWN = 'HPP-723'


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
    want = os.environ.get('F30M_RUN_ID', '')
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
