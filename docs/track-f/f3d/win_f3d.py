"""win_f3d.py - F3d (HPP-342): the lock window of the F3d series (ROADMAP p.259(e)(5), p.277(z); lock queue session > P > F > S,
p.228(v); inside F - F4c first; general rule 27).  Port of C:/kyty/f287/f4c/win_f4c2.py.
Open only when, by the API answer right before the lock:
  HPP-333 (audit s144)  status done and executionRunId empty
  HPP-341 (F3c)         status done and executionRunId empty
  HPP-337 (F4c, track F - first inside F, p.259(e)(5))         not todo / in_progress and executionRunId empty
  HPP-352 (run step of session 145 - before track F)            not todo / in_progress and executionRunId empty
  HPP-364 (P17, run link of track P - before track F)           not todo / in_progress and executionRunId empty
Prints one ASCII line 'win_f3d <issue> <status> run <id>; ... -> open|closed|error'.
rc 0 open; rc 5 closed; rc 6 no answer (refuse - the window is not proven open).
  python win_f3d.py            (PAPERCLIP_API_URL, PAPERCLIP_API_KEY from the environment)
"""
import json
import os
import sys
import urllib.request

NEED_DONE = ('HPP-333', 'HPP-341')
YIELD_TO = ('HPP-337', 'HPP-352', 'HPP-364')
YIELD_STATUS = ('todo', 'in_progress')


def decide(states):
    """states: {issue: (status, executionRunId)} -> (rc, word)."""
    for i in NEED_DONE + YIELD_TO:
        st = (states.get(i) or (None, None))[0]
        if not isinstance(st, str) or not st:
            return 6, 'error'
    for i in NEED_DONE:
        st, run = states[i]
        if st != 'done' or run:
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
    for i in NEED_DONE + YIELD_TO:
        try:
            states[i] = fetch(i)
        except Exception as e:  # noqa: BLE001 - any API failure refuses
            states[i] = (None, 'exception %s' % type(e).__name__)
    rc, word = decide(states)
    print('win_f3d %s -> %s' % ('; '.join('%s %s run %s' % (i, states[i][0], states[i][1]) for i in NEED_DONE + YIELD_TO), word))
    return rc


if __name__ == '__main__':
    sys.exit(main())
