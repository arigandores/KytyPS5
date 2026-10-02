"""win_f7a.py - F7a (HPP-397): the lock window of the F7a capture (ROADMAP p.327(e): lock queue P > F > S after session 146,
p.322(g); general rule 27).  Port of C:/kyty/f287/f6e/win_f6e.py.
Open only when, by the API answer right before the lock:
  HPP-378 (F6f, lead - F7a starts after its done)             status done and executionRunId empty
  HPP-393 (P21, run link of track P - before track F)         not todo / in_progress and executionRunId empty
  HPP-364 (P17, run link of track P - before track F)         not todo / in_progress and executionRunId empty
Prints one ASCII line 'win_f7a <issue> <status> run <id>; ... -> open|closed|error'.
rc 0 open; rc 5 closed; rc 6 no answer (refuse - the window is not proven open).
  python win_f7a.py            (PAPERCLIP_API_URL, PAPERCLIP_API_KEY from the environment)
"""
import json
import os
import sys
import urllib.request

NEED_DONE = ('HPP-378',)
YIELD_TO = ('HPP-393', 'HPP-364')
YIELD_STATUS = ('todo', 'in_progress')
ALL = NEED_DONE + YIELD_TO


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
    print('win_f7a %s -> %s' % ('; '.join('%s %s run %s' % (i, states[i][0], states[i][1]) for i in ALL), word))
    return rc


if __name__ == '__main__':
    sys.exit(main())
