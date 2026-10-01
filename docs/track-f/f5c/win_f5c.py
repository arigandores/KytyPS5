"""win_f5c.py - F5c (HPP-357): the lock window of the series (port of C:/kyty/f287/f4c/win_f4c2.py).  Lock queue session > P > F
> S (ROADMAP "SESSION 122" p.228(v), repeated in p.285(v)); F5c waits for F5b2, F3d and F4c (task text, p.280(d), 285(v)).
Open only when, by the API answer right before the lock:
  HPP-367 (F5b2), HPP-342 (F3d), HPP-337 (F4c)   status done and executionRunId empty
  HPP-350 (s145 step 0, harness and mutants)      not todo / in_progress and executionRunId empty
  HPP-352 (s145 step 2, the series)               not todo / in_progress and executionRunId empty
  HPP-364 (P17, track P runs - before F)          not todo / in_progress and executionRunId empty
  HPP-370 (FSc, track F runs under the lock)      not todo / in_progress and executionRunId empty
Prints one ASCII line 'win_f5c <issue> <status> run <id>; ... -> open|closed|error'.
rc 0 open; rc 5 closed; rc 6 no answer (refuse - the window is not proven open).
  python win_f5c.py            (PAPERCLIP_API_URL, PAPERCLIP_API_KEY from the environment)
"""
import json
import os
import sys
import urllib.request

NEED_DONE = ('HPP-367', 'HPP-342', 'HPP-337')
YIELD_TO = ('HPP-350', 'HPP-352', 'HPP-364', 'HPP-370')
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
    print('win_f5c %s -> %s' % ('; '.join('%s %s run %s' % (i, states[i][0], states[i][1]) for i in NEED_DONE + YIELD_TO), word))
    return rc


if __name__ == '__main__':
    sys.exit(main())
