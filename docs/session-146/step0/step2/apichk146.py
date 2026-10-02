"""apichk146.py - the API check row of step 2 of session 146 (port of apichk145.py by HPP-386, names 145 -> 146; port of
apichk144.py by HPP-350, names 144 -> 145;
MINOR-4 of audit 143, ROADMAP s122 item 254 (i); the line of
the Harness Engineer: "the API check before every call of a tag - a times.txt row with the answer").  Called by
step2/next_one.sh right before the detached call of go146a.sh: ONE GET of the step's issue and ONE GET of its comments, ONE
ASCII row into C:/kyty/s146/step2/times.txt (date -u at the answer), rc 0 go / rc 4 no go:
  no go - no answer (network, http, json), the issue cancelled or done, or a comment newer than --after whose author is
          not this agent (it must be read first - a stop of the lead comes as a comment AND the file C:/kyty/s146/STOP,
          general rule 26; the call is repeated with --after <the id of the last comment read>).
  go    - the issue answers, its status is not cancelled / done, no unread comment of another author.
The row: "<UTC> apichk146 <tag> issue <identifier> status <s> executionRunId <id|none> comments <n> after <id|start>
new-foreign <k> last <id> <author> <createdAt> -> GO|NO GO (<reason>)".  ASCII only, no subprocess.
    python apichk146.py --tag <tag> [--issue <id or identifier>] [--after <comment id>] [--times <file>]
(issue default: $PAPERCLIP_TASK_ID; me: $PAPERCLIP_AGENT_ID; API: $PAPERCLIP_API_URL, $PAPERCLIP_API_KEY)
"""
import argparse
import json
import os
import sys
import time
import urllib.request

TIMES = 'C:/kyty/s146/step2/times.txt'
STOP_STATUS = ('cancelled', 'done')


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def asc(s):
    return str(s).encode('ascii', 'replace').decode('ascii')


def judge(tag, issue, comments, after, me):
    """(rc, row without the time) from the answers: issue (dict or None), comments (list or None)."""
    if not isinstance(issue, dict) or not isinstance(comments, list):
        return 4, 'apichk146 %s no answer -> NO GO (no answer of the API)' % tag
    cs = sorted((c for c in comments if isinstance(c, dict)), key=lambda c: (str(c.get('createdAt')), str(c.get('id'))))
    ids = [c.get('id') for c in cs]
    newer = cs[ids.index(after) + 1:] if after in ids else cs
    foreign = [c for c in newer if (c.get('authorAgentId') or c.get('authorUserId')) != me]
    st = issue.get('status')
    last = cs[-1] if cs else None
    why = []
    if st in STOP_STATUS:
        why.append('issue %s' % st)
    if after is not None and after not in ids:
        why.append('comment %s not found' % after)
    if foreign:
        why.append('%d unread comment(s) of another author since %s - read them, then call with --after %s' % (
            len(foreign), after or 'start', foreign[-1].get('id')))
    row = ('apichk146 %s issue %s status %s executionRunId %s comments %d after %s new-foreign %d last %s -> %s' % (
        tag, asc(issue.get('identifier') or issue.get('id')), asc(st), asc(issue.get('executionRunId') or 'none'), len(cs),
        asc(after or 'start'), len(foreign),
        ('%s %s %s' % (asc(last.get('id')), asc(last.get('authorAgentId') or last.get('authorUserId') or '-'),
                       asc(last.get('createdAt')))) if last else 'none',
        ('NO GO (%s)' % '; '.join(why)) if why else 'GO'))
    return (4 if why else 0), row


def get(url, key):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer %s' % key})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def main(argv=None, fetch=None, times=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', required=True)
    ap.add_argument('--issue', default=os.environ.get('PAPERCLIP_TASK_ID'))
    ap.add_argument('--after', default=None)
    ap.add_argument('--times', default=times or TIMES)
    a = ap.parse_args(argv)
    me = os.environ.get('PAPERCLIP_AGENT_ID')
    issue = comments = None
    if a.issue:
        base = (os.environ.get('PAPERCLIP_API_URL') or '').rstrip('/')
        if base.endswith('/api'):
            base = base[:-4]
        key = os.environ.get('PAPERCLIP_API_KEY') or ''
        f = fetch or (lambda u: get(u, key))
        try:
            issue = f('%s/api/issues/%s' % (base, a.issue))
            comments = f('%s/api/issues/%s/comments' % (base, a.issue))
        except Exception as e:      # any failure of the answer is "no answer"
            issue = comments = None
            print(asc('apichk146: %s: %s' % (type(e).__name__, str(e)[:120])))
    rc, row = judge(a.tag, issue, comments, a.after, me)
    line = '%s %s' % (utc(), row if a.issue else row.replace('no answer of the API', 'no issue id'))
    with open(a.times, 'a', encoding='ascii') as fo:
        fo.write(line + '\n')
    print(line)
    return rc


if __name__ == '__main__':
    sys.exit(main())
