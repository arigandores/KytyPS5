# S2a (HPP-312): reference map of AUDIT_S1.md section 10. Every row `<commit>:<path>:<line>` | anchor:
# the anchor must be in that line of the file at that commit; positive control - the same reference +1 must give NOT OK.
import re, subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
DOC = 'C:/kyty/KytyPS5/docs/track-s/audit/AUDIT_S1.md'
BS = chr(92)

text = open(DOC, 'rb').read().decode('utf-8')
sec = text.split('## 10. ', 1)[1].split('## 11. ', 1)[0]
rows = []
for l in sec.split('\n'):
    m = re.match(r'^\| `([0-9a-f]{7,8}):([^`]+):(\d+)` \| (.*) \|$', l)
    if m:
        rows.append((m.group(1), m.group(2), int(m.group(3)), m.group(4).replace(BS + '|', '|')))
cache = {}
ok = True
for c, p, n, a in rows:
    if (c, p) not in cache:
        r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True)
        cache[(c, p)] = r.stdout.decode('utf-8', 'replace').replace('\r', '').split('\n') if r.returncode == 0 else None
    L = cache[(c, p)]
    if L is None or n > len(L):
        print('FAIL no file/line %s:%s:%d' % (c, p, n))
        ok = False
        continue
    r1 = a in L[n - 1]
    r2 = a in (L[n] if n < len(L) else '')
    res = r1 and not r2
    ok &= res
    print('%s:%s:%d anchor %s; control +1 %s' % (c, p, n, 'OK' if r1 else 'NOT OK', 'NOT OK' if not r2 else 'OK (control failed)'))
print('refs', len(rows))
print('ALL OK' if ok and rows else 'FAIL')
sys.exit(0 if ok and rows else 1)
