"""win_f4c.py - F4c (HPP-337): the lock window of the series after ROADMAP p.268(d), p.270(d) (F4c waits for F4b2 HPP-347 and
the audit of session 144 HPP-333; lock queue session > P > F > S, p.228(v), general rule 27).  Replaces win332_f2c.py (the
window of p.256(e) "before HPP-332 starts" closed with HPP-332 done, p.270(zh)).
Open only when, by the API answer right before the lock:
  HPP-333 (audit s144)  status done and executionRunId empty
  HPP-347 (F4b2)        status done and executionRunId empty
  HPP-328 (P10, track P - before F in the queue; variant of the executor)  not todo / in_progress and executionRunId empty
Prints one ASCII line 'win_f4c <issue> <status> run <id>; ... -> open|closed|error'.
rc 0 open; rc 5 closed; rc 6 no answer (refuse - the window is not proven open).
  python win_f4c.py            (PAPERCLIP_API_URL, PAPERCLIP_API_KEY from the environment)
"""
import json
import os
import sys
import urllib.request

NEED_DONE = ('HPP-333', 'HPP-347')
YIELD_TO = ('HPP-328',)
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
    print('win_f4c %s -> %s' % ('; '.join('%s %s run %s' % (i, states[i][0], states[i][1]) for i in NEED_DONE + YIELD_TO), word))
    return rc


if __name__ == '__main__':
    sys.exit(main())
