# HPP-264 audit (s139): privacy check of the s138-s139 COMMITS of both repos and of the committed trees (HEAD), every pattern of
# C:/kyty/scrub/checks.txt (list outside git). Two methods: (1) per commit - message and added lines of `git show` (binary included,
# -a), Python re; (2) whole tree - `git grep -P -a -c HEAD`. Prints counts per pattern index only - names stay out of reports.
# Non-blocking by ROADMAP s122 item 134(g)(1) / 135(v): #9 anywhere, #7 only in the two named lines.
import re, subprocess, sys
from pathlib import Path

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPOS = [('KytyPS5', 'C:/kyty/KytyPS5', '6debfe0b'), ('ps5em', 'C:/kyty/KytyPS5/ps5 em', '150fce7')]
NAMED7 = {('KytyPS5', 'src/libs/guestPrintf.cpp'), ('KytyPS5', 'docs/session-112/audit/transcript_calls112.txt')}
pats = [l for l in Path('C:/kyty/scrub/checks.txt').read_text(encoding='utf-8').splitlines() if l.strip()]
rx = [re.compile(p) for p in pats]
blocking = 0

def run(args, root):
    r = subprocess.run([GIT, '-C', root] + args, capture_output=True)
    if r.returncode not in (0, 1):
        sys.exit('git failed: %r %r' % (args, r.stderr[:200]))
    return r.stdout.decode('utf-8', 'replace')

for name, root, base in REPOS:
    commits = run(['rev-list', '--reverse', base + '..HEAD'], root).split()
    print('%s range %s..HEAD commits %d' % (name, base, len(commits)))
    for c in commits:
        msg = run(['log', '-1', '--format=%an <%ae>%n%cn <%ce>%n%B', c], root)
        diff = run(['show', '-a', '--format=', '--unified=0', c], root)
        added = '\n'.join(l[1:] for l in diff.splitlines() if l.startswith('+') and not l.startswith('+++'))
        hits = []
        for i, r in enumerate(rx, 1):
            nm, nd = len(r.findall(msg)), len(r.findall(added))
            if nm or nd:
                ok = (i == 9)
                hits.append('#%d msg %d added %d %s' % (i, nm, nd, 'non-blocking' if ok else 'BLOCKING'))
                if not ok:
                    blocking += 1
        print('  %s %s' % (c[:8], '; '.join(hits) if hits else 'clean'))
    head = run(['rev-parse', '--short=8', 'HEAD'], root).strip()
    for i, p in enumerate(pats, 1):
        out = run(['grep', '-P', '-a', '-c', '-e', p, 'HEAD'], root)
        files = []
        for ln in out.splitlines():
            _, rest = ln.split(':', 1)
            path, cnt = rest.rsplit(':', 1)
            files.append((path, int(cnt)))
        cls = 'ok'
        if files:
            if i == 9:
                cls = 'non-blocking (134(g)(1))'
            elif i == 7 and all((name, f) in NAMED7 and n == 1 for f, n in files):
                cls = 'non-blocking (135(v)), the two named lines'
            else:
                cls = 'BLOCKING'; blocking += 1
        print('%s@%s tree pattern#%d files %d hits %d %s' % (name, head, i, len(files), sum(n for _, n in files), cls))
print('BLOCKING:', blocking)
