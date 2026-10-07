"""F25c (HPP-666, Red Team): check every <commit>:<path>:<line> reference of f25c-review.md against its anchor (line N) and
its +1 (line N + 1), both stripped of leading / trailing white space. Usage:
    python refs_f25c.py refs_f25c.tsv            -> one line per reference, last line ALL OK or FAILED
    python refs_f25c.py refs_f25c.tsv --neg      -> negative control: every anchor is altered (+ 'X'); each reference must
                                                    fail; last line NEG CONTROL OK (all failed) or NEG CONTROL BROKEN
"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'


def show(commit, path, cache={}):
    key = (commit, path)
    if key not in cache:
        out = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True)
        cache[key] = out.stdout.decode('utf-8', 'replace').replace('\r\n', '\n').split('\n') if out.returncode == 0 else None
    return cache[key]


def match(got, want):
    # A whole stripped line; an anchor ending with the marker ' …' is a prefix of the line (ROADMAP paragraphs are one line).
    want = want.strip()
    if want.endswith(' …'):
        return want[:-2] != '' and got.startswith(want[:-2])
    return got == want


def main():
    tsv, neg = sys.argv[1], '--neg' in sys.argv[2:]
    rows = []
    with open(tsv, 'rb') as f:
        for raw in f.read().decode('utf-8').split('\n'):
            if not raw.strip():
                continue
            parts = raw.split('\t')
            while len(parts) < 5:
                parts.append('')
            rows.append(parts[:5])
    ok_all, failed = True, 0
    for commit, path, line, anchor, plus1 in rows:
        if neg:
            anchor = ('X' + anchor) if anchor.strip().endswith(' …') else anchor + 'X'
        lines = show(commit, path)
        n = int(line)
        if lines is None or n < 1 or n > len(lines):
            res = False
            why = 'no file or line'
        else:
            got0 = lines[n - 1].strip()
            got1 = lines[n].strip() if n < len(lines) else ''
            res = match(got0, anchor) and match(got1, plus1)
            why = '' if res else 'anchor=%r plus1=%r' % (got0[:80], got1[:80])
        ok_all &= res
        failed += 0 if res else 1
        print('%s %s:%s:%s %s' % ('OK' if res else 'FAILED', commit, path, line, why))
    print('rows=%d failed=%d' % (len(rows), failed))
    if neg:
        print('NEG CONTROL OK' if failed == len(rows) else 'NEG CONTROL BROKEN')
        sys.exit(0 if failed == len(rows) else 1)
    print('ALL OK' if ok_all else 'FAILED')
    sys.exit(0 if ok_all else 1)


main()
