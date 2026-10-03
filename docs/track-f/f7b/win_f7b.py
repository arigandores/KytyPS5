"""win_f7b.py - F7b (HPP-398): window of a process with a Vulkan device (RenderDoc replay) of a link without the lock,
ROADMAP p.277(g) (general rule 27 addition): open only if no task with a GLCache / GPU load check between tags is
in_progress and none of them has an execution run.  List of p.277(g) and its successors:
  HPP-337 F4c, HPP-342 F3d, HPP-357 F5c, HPP-315 S4, HPP-318 S6, track P run links HPP-364 P17 and HPP-393 P21,
  track F run links HPP-383 FS2c and HPP-397 F7a, session chain run step HPP-388 (s146, the last chain).
  Added 2026-10-03 (rework after the lead review): run links opened since - HPP-410 F9a, HPP-421 F9d, HPP-424 F9g
  (track F), HPP-418 P33 (track P), HPP-433 S10 (track S).
Prints one ASCII line 'win_f7b <issue> <status> run <id>; ... -> open|closed|error'.
rc 0 open; rc 5 closed; rc 6 no answer (refuse).
"""
import json
import os
import sys
import urllib.request

WATCH = ('HPP-337', 'HPP-342', 'HPP-357', 'HPP-315', 'HPP-318', 'HPP-364', 'HPP-393', 'HPP-383', 'HPP-397', 'HPP-388',
         'HPP-410', 'HPP-418', 'HPP-421', 'HPP-424', 'HPP-433')


def decide(states):
    for i in WATCH:
        st = (states.get(i) or (None, None))[0]
        if not isinstance(st, str) or not st:
            return 6, 'error'
    for i in WATCH:
        st, run = states[i]
        if st == 'in_progress' or run:
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


def selftest():
    ok = True
    base = {i: ('done', None) for i in WATCH}
    ok &= decide(base) == (0, 'open')
    for i in WATCH:
        s = dict(base); s[i] = ('in_progress', None); ok &= decide(s) == (5, 'closed')
        s = dict(base); s[i] = ('blocked', 'r1'); ok &= decide(s) == (5, 'closed')
        s = dict(base); s[i] = (None, None); ok &= decide(s) == (6, 'error')
    s = dict(base); s['HPP-315'] = ('blocked', None); ok &= decide(s) == (0, 'open')
    print('selftest', 'ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    if '--selftest' in sys.argv:
        return selftest()
    states = {}
    for i in WATCH:
        try:
            states[i] = fetch(i)
        except Exception as e:  # noqa: BLE001
            states[i] = (None, 'exception %s' % type(e).__name__)
    rc, word = decide(states)
    print('win_f7b %s -> %s' % ('; '.join('%s %s run %s' % (i, states[i][0], states[i][1]) for i in WATCH), word))
    return rc


if __name__ == '__main__':
    sys.exit(main())
