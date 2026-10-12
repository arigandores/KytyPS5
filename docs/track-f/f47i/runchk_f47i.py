# Track F link F47i (HPP-826; ROADMAP s122 item 740 (v)(3), 742 (e), 744 (g)-(d)): copy of the F47d (HPP-809) file runchk_f47d.py with the names moved (f47d -> f47i, F47D -> F47I, F47d -> F47i, HPP-809 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 702 (g)): copy of the F44c (HPP-793) file runchk_f44c.py with the names moved (f44c -> f47i, F44C -> F47I, F44c -> F47i, HPP-793 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 698 (d)(4)): copy of the F38c (HPP-765) file runchk_f38c.py with the names moved (f38c -> f47i, F38C -> F47I, F38c -> F47i, HPP-765 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 691 (d)(4)): copy of the FS12c (HPP-752) file runchk_fs12c.py with the names moved (fs12c -> f47i, FS12C -> F47I, FS12c -> F47i, HPP-752 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 683 (g)(3), 686 (v)): copy of the F33e (HPP-746) file runchk_f33e.py with the names moved (f33e -> f47i, F33E -> F47I, F33e -> F47i, HPP-746 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 675 (d)(4), 682): copy of the F34c (HPP-740) file runchk_f34c.py with the names moved (f34c -> f47i, F34C -> F47I, F34c -> F47i, HPP-740 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 673 (z)(2), 674, 676): copy of the F31c (HPP-731) file runchk_f31c.py with the names moved (f31c -> f47i, F31C -> F47I, HPP-731 -> HPP-826); no change of meaning.
# Track F link F31c (HPP-826; ROADMAP s122 item 667 (d)): copy of the F26c (HPP-692) file runchk_f26c.py with the names moved (f26c -> f47i, HPP-692 -> HPP-826, F26C_ -> F47I_); no change of meaning.
"""F26c (HPP-826; copy of FS10c runchk_fs10c.py: own issue HPP-826, variable F47I_RUN_ID).  Before: F25m (HPP-686; port of F20l3 runchk_f20l3.py: own issue HPP-686, variable FS10C_RUN_ID).  Before: F20l3 (HPP-655; ROADMAP s122 item 587 (g) - the debt "a detached tag call checks by API before taking the lock that the run which
launched it is alive"): go_f20l3.sh calls this script right before procload.py and the lock.  The issue HPP-655 must have a going run
(executionRunId not empty) equal to the run id the launcher passed (F20L3_RUN_ID, set by launch_f20l3.sh from PAPERCLIP_RUN_ID).  Prints
RUN ALIVE (exit 0), RUN GONE (exit 1: the run was cancelled or ended - the detached call must not start the game), API ERROR (exit 2 -
also a refusal).  --fake <json> (fixtures only) reads the issue json from a file.  ASCII only.
usage: python runchk_f20l3.py [--fake F]"""
import json
import os
import sys
import urllib.request

OWN = 'HPP-826'


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
    want = os.environ.get('F47I_RUN_ID', '')
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
