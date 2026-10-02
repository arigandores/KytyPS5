# refs145.py - Session Auditor, s145 step 3 (HPP-353): map of the references of AUDIT145.md to mutable documents
# (general rule 24 (1)): <commit>:<path>:<line> with the anchor (the first 70 characters of the line) and the control line +1.
# Usage: python refs145.py <commit of KytyPS5> <commit of ps5-em>
import subprocess, sys, re

GIT = 'C:/Program Files/Git/cmd/git.exe'
KY, EM = 'C:/kyty/KytyPS5', 'C:/kyty/KytyPS5/ps5 em'
ck, ce = sys.argv[1], sys.argv[2]


def lines(root, commit, path):
    r = subprocess.run([GIT, '-C', root, 'show', '%s:%s' % (commit, path)], capture_output=True)
    return r.stdout.decode('utf-8', 'replace').split('\n')


R = lines(KY, ck, 'docs/ROADMAP.md')
n = 0
bad = 0
for item in (241, 254, 266, 270, 272, 273, 274, 285, 288, 291, 295, 297, 301, 302, 303, 304, 305, 306, 307):
    hit = [i for i, l in enumerate(R) if re.match(r'%d\. \*\*' % item, l)]
    n += 1
    if len(hit) != 1:
        bad += 1
        print('REF item %d: %d anchors' % (item, len(hit)))
        continue
    i = hit[0]
    print('REF %s:docs/ROADMAP.md:%d | item %d | anchor "%s" | +1 "%s"' % (ck, i + 1, item, R[i][:70], R[i + 1][:60]))
T = lines(EM, ce, 'docs/agent-team.md')
for key in (r'25\. \*\*', r'26\. \*\*', r'27\. \*\*', r'28\. \*\*'):
    hit = [i for i, l in enumerate(T) if re.match(key, l)]
    n += 1
    if len(hit) != 1:
        bad += 1
        print('REF agent-team %s: %d anchors' % (key, len(hit)))
        continue
    i = hit[0]
    print('REF ps5-em@%s:docs/agent-team.md:%d | general rule %s | anchor "%s" | +1 "%s"' % (ce, i + 1, key[:2], T[i][:70], T[i + 1][:60]))
P = lines(EM, ce, 'docs/platform-traps.md')
hit = [i for i, l in enumerate(P) if 'executionPolicy' in l and 'stages' in l]
n += 1
if hit:
    i = hit[0]
    print('REF ps5-em@%s:docs/platform-traps.md:%d | trap 12 | anchor "%s" | +1 "%s"' % (ce, i + 1, P[i][:70], P[i + 1][:60] if i + 1 < len(P) else ''))
else:
    bad += 1
    print('REF platform-traps trap 12: no anchor')
print('REFS %d, without a single anchor %d: %s' % (n, bad, 'ALL OK' if not bad else 'CHECK'))
