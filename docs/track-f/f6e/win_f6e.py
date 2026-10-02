"""win_f6e.py - F6e (HPP-377): the lock window of the F6e series (ROADMAP p.287(d): lock queue session > P > F > S, inside F -
F5c and FSc first; general rule 27; p.277(g)).  Port of C:/kyty/f287/f3d/win_f3d.py.
Open only when, by the API answer right before the lock:
  HPP-376 (F6d, code review)                              status done and executionRunId empty
  HPP-353 (audit of session 145, p.306(d) of seal 02)     status done and executionRunId empty
  HPP-388, HPP-389 (session 146 runs and audit, p.309(l)(5); seal 03)  status done and executionRunId empty
  HPP-357 (F5c, track F runs - first inside F)            status done or in_review and executionRunId empty
  HPP-370 (FSc, track F runs - first inside F)            status done or in_review and executionRunId empty
  HPP-352 (run step of session 145 - before track F)      not todo / in_progress and executionRunId empty
  HPP-364 (P17, run link of track P - before track F)     not todo / in_progress and executionRunId empty
  HPP-393 (P21, run link of track P - before track F, p.322(g); seal 03)  not todo / in_progress and executionRunId empty
Prints one ASCII line 'win_f6e <issue> <status> run <id>; ... -> open|closed|error'.
rc 0 open; rc 5 closed; rc 6 no answer (refuse - the window is not proven open).
  python win_f6e.py            (PAPERCLIP_API_URL, PAPERCLIP_API_KEY from the environment)
"""
import json
import os
import sys
import urllib.request

NEED_DONE = ('HPP-376', 'HPP-353', 'HPP-388', 'HPP-389')
NEED_DELIVERED = ('HPP-357', 'HPP-370')
DELIVERED = ('done', 'in_review')
YIELD_TO = ('HPP-352', 'HPP-364', 'HPP-393')
YIELD_STATUS = ('todo', 'in_progress')
ALL = NEED_DONE + NEED_DELIVERED + YIELD_TO


def decide(states):
    """states: {issue: (status, executionRunId)} -> (rc, word)."""
    for i in ALL:
        st = (states.get(i) or (None, None))[0]
        if not isinstance(st, str) or not st:
            return 6, 'error'
    for i in NEED_DONE:
        st, run = states[i]
        if st != 'done' or run:
            return 5, 'closed'
    for i in NEED_DELIVERED:
        st, run = states[i]
        if st not in DELIVERED or run:
            return 5, 'closed'
    for i in YIELD_TO:
        st, run = states[i]
        if st in YIELD_STATUS or run:
            return 5, 'closed'
    return 0, 'open'


def fetch(issue):
    base = os.environ.get('PAPERCLIP_API_URL', '').rstrip('/')
    if base.endswith('/api'):
        base = base[:-4]
    key = os.environ.get('PAPERCLIP_API_KEY', '')
    if not base or not key:
        return None, None
    req = urllib.request.Request('%s/api/issues/%s' % (base, issue), headers={'Authorization': 'Bearer %s' % key})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    return d.get('status'), d.get('executionRunId')


def main():
    states = {}
    for i in ALL:
        try:
            states[i] = fetch(i)
        except Exception as e:  # noqa: BLE001 - any API failure refuses
            states[i] = (None, 'exception %s' % type(e).__name__)
    rc, word = decide(states)
    print('win_f6e %s -> %s' % ('; '.join('%s %s run %s' % (i, states[i][0], states[i][1]) for i in ALL), word))
    return rc


if __name__ == '__main__':
    sys.exit(main())
