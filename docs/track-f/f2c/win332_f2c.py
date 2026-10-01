"""win332_f2c.py - F2c (HPP-310): the lock window of ROADMAP p.256(e) - the series takes the lock only when HPP-332 (step 2 of
session 144) is neither in_progress nor done by the API answer.  Prints one ASCII line 'win332 <status> -> open|closed|error'.
rc 0 open; rc 5 closed (in_progress or done); rc 6 no answer (refuse - the window is not proven open).
  python win332_f2c.py            (PAPERCLIP_API_URL, PAPERCLIP_API_KEY from the environment)
"""
import json
import os
import sys
import urllib.request

ISSUE = 'HPP-332'
CLOSED = ('in_progress', 'done')


def decide(status):
    if not isinstance(status, str) or not status:
        return 6, 'error'
    return (5, 'closed') if status in CLOSED else (0, 'open')


def fetch():
    base = os.environ.get('PAPERCLIP_API_URL', '').rstrip('/')
    if base.endswith('/api'):
        base = base[:-4]
    key = os.environ.get('PAPERCLIP_API_KEY', '')
    if not base or not key:
        return None, None
    req = urllib.request.Request('%s/api/issues/%s' % (base, ISSUE), headers={'Authorization': 'Bearer %s' % key})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    return d.get('status'), d.get('executionRunId')


def main():
    try:
        st, run = fetch()
    except Exception as e:  # noqa: BLE001 - any API failure refuses
        st, run = None, 'exception %s' % type(e).__name__
    rc, word = decide(st)
    print('win332 %s status %s executionRunId %s -> %s' % (ISSUE, st, run, word))
    return rc


if __name__ == '__main__':
    sys.exit(main())
