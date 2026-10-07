#!/usr/bin/env python3
# F25h (HPP-675): checks every <commit>:<path>:<line> reference of docs/track-f/f25h.md listed in refs.tsv
# (commit, path, line, anchor, the line +1) against `git show <commit>:<path>`.
# A text matches a line when the stripped line equals it, or (text of >= 8 characters) it is a substring of the line;
# an empty text matches only an empty line. Negative controls: every reference moved by +1 line, and every anchor with
# an appended marker, must FAIL. Prints ALL OK only when every reference passes and every control fails.
# usage: check_refs.py <repo> <refs.tsv>
import subprocess
import sys

repo, tsv = sys.argv[1], sys.argv[2]
cache = {}


def lines_of(commit, path):
    key = (commit, path)
    if key not in cache:
        out = subprocess.run(['git', '-C', repo, 'show', '%s:%s' % (commit, path)], capture_output=True)
        if out.returncode != 0:
            cache[key] = None
        else:
            cache[key] = out.stdout.decode('utf-8', 'replace').replace('\r', '').split('\n')
    return cache[key]


def match(text, line):
    s = line.strip()
    t = text.strip()
    if t == '':
        return s == ''
    return s == t or (len(t) >= 8 and t in line)


def check(commit, path, n, anchor, nxt):
    ls = lines_of(commit, path)
    if ls is None or n < 1 or n + 1 > len(ls):
        return False
    return match(anchor, ls[n - 1]) and match(nxt, ls[n])


refs = []
with open(tsv, 'r', encoding='utf-8') as f:
    for raw in f:
        raw = raw.rstrip('\n')
        if not raw:
            continue
        c, p, n, a, x = (raw.split('\t') + [''] * 5)[:5]
        refs.append((c, p, int(n), a, x))

ok = True
for r in refs:
    good = check(*r)
    print('%s %s:%s:%d' % ('PASS' if good else 'FAIL', r[0], r[1], r[2]))
    ok &= good
neg_shift = sum(1 for (c, p, n, a, x) in refs if check(c, p, n + 1, a, x))
neg_anchor = sum(1 for (c, p, n, a, x) in refs if check(c, p, n, a + ' @@NEG@@', x))
print('references %d; negative control (+1 line) passed %d (must be 0); negative control (anchor marker) passed %d (must be 0)'
      % (len(refs), neg_shift, neg_anchor))
ok &= neg_shift == 0 and neg_anchor == 0
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
