# Session Auditor s141 step 2: own check of the pinned references of inventory141.md rev.2 (RC1): every <commit>:<path>:<line>,
# ps5-em@<commit>:<path>:<line> and C:/kyty/...:<line> resolves; where the reference is followed by an explicit «anchor», the anchor
# is found in the target line(s) and NOT in the line shifted by +1 (positive control). Own code, independent of refs141b.py.
import re, subprocess, hashlib, collections, sys
GIT = 'C:/Program Files/Git/cmd/git.exe'
DOC = 'C:/kyty/KytyPS5/docs/session-141/inventory141.md'
t = open(DOC, encoding='utf-8').read()
print('doc sha256', hashlib.sha256(open(DOC, 'rb').read()).hexdigest())
R = re.compile(r'`((?:ps5-em@)?[0-9a-f]{7,8}):([^`:]+):(\d+)(?:-(\d+))?`(?:\s*«([^»]+)»)?|`(C:/kyty/[^`:]+):(\d+)(?:-(\d+))?`(?:\s*«([^»]+)»)?')
cache = {}
def lines_at(rev, path):
    key = (rev, path)
    if key in cache:
        return cache[key]
    if rev is None:
        try:
            L = open(path, encoding='utf-8', errors='replace').read().split('\n')
        except OSError:
            L = None
    else:
        root = 'C:/kyty/KytyPS5'
        if rev.startswith('ps5-em@'):
            root = 'C:/kyty/KytyPS5/ps5 em'; rev = rev[7:]
        r = subprocess.run([GIT, '-C', root, 'show', rev + ':' + path], capture_output=True)
        L = r.stdout.decode('utf-8', 'replace').split('\n') if r.returncode == 0 else None
    cache[key] = L
    return L
n = ok = bad = anch = anch_ok = ctrl_ok = 0
uniq = set()
badl = []
for m in R.finditer(t):
    if m.group(1):
        rev, path, a, b, anchor = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5)
    else:
        rev, path, a, b, anchor = None, m.group(6), int(m.group(7)), m.group(8), m.group(9)
    b = int(b) if b else a
    n += 1
    uniq.add((rev, path, a, b))
    L = lines_at(rev, path)
    if L is None or b > len(L) or a < 1:
        bad += 1; badl.append((rev, path, a, b, 'MISSING')); continue
    ok += 1
    if anchor:
        anch += 1
        seg = '\n'.join(L[a - 1:b])
        nxt = '\n'.join(L[a:b + 1]) if b < len(L) else ''
        if anchor in seg:
            anch_ok += 1
        else:
            badl.append((rev, path, a, b, 'ANCHOR NOT FOUND: ' + anchor))
        if anchor not in (L[b] if b < len(L) else ''):
            ctrl_ok += 1
print('refs', n, 'unique', len(uniq), 'resolve', ok, 'missing', bad, 'with anchor', anch, 'anchor found', anch_ok, 'control(+1 line lacks anchor)', ctrl_ok)
for x in badl:
    print('  BAD', x)
revs = collections.Counter((r or 'local') for r, p, a, b in uniq)
print('by pin', dict(revs))
