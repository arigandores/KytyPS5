"""win_fs2.py - FS2c (HPP-383): the lock window of the FS2c series (ROADMAP p.298(e): FS2c blocked on FS2b and FSc; p.322(g): lock queue
after session 146 - P > F > S; p.228(v); general rule 27; p.277(g)).  Port of C:/kyty/f287/f6e/win_f6e.py.
Open only when, by the API answer right before the lock:
  HPP-382 (FS2b, review of the FS2 binary bbad499c, accepted p.329)       status done and executionRunId empty
  HPP-381 (FS2a, the FS2 binary)                                            status done and executionRunId empty
  HPP-370 (FSc, track F runs - first inside F, p.298(e))                   status done or in_review and executionRunId empty
  HPP-377 (F6e, track F runs - first inside F)                              status done or in_review and executionRunId empty
  HPP-393 (P21, run link of track P - before track F, p.322(g))             not todo / in_progress and executionRunId empty
Prints one ASCII line 'win_fs2 <issue> <status> run <id>; ... -> open|closed|error'.
rc 0 open; rc 5 closed; rc 6 no answer (refuse - the window is not proven open).
  python win_fs2.py            (PAPERCLIP_API_URL, PAPERCLIP_API_KEY from the environment)
"""
import json
import os
import sys
import urllib.request

NEED_DONE = ('HPP-382', 'HPP-381')
NEED_DELIVERED = ('HPP-370', 'HPP-377')
DELIVERED = ('done', 'in_review')
YIELD_TO = ('HPP-393',)
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
    print('win_fs2 %s -> %s' % ('; '.join('%s %s run %s' % (i, states[i][0], states[i][1]) for i in ALL), word))
    return rc


if __name__ == '__main__':
    sys.exit(main())
