# HPP-225 audit (s135; port of audit134/privacy134.py): privacy check of COMMITTED content (HEAD) of both repos, every pattern of C:/kyty/scrub/checks.txt
# (list outside git), by `git grep -P -a -c` (binary files included), i.e. a different method from step 0p's grep132.py
# (Python re over working-tree files, binaries skipped). Prints counts per pattern index only - names stay out of reports.
# Non-blocking by ROADMAP s122 item 134(g)(1) / 135(v): #7 only in the two named lines, #9 anywhere.
import subprocess, sys
from pathlib import Path

REPOS = [('KytyPS5', 'C:/kyty/KytyPS5'), ('ps5em', 'C:/kyty/KytyPS5/ps5 em')]
NAMED7 = {('KytyPS5', 'src/libs/guestPrintf.cpp'), ('KytyPS5', 'docs/session-112/audit/transcript_calls112.txt')}
pats = [l for l in Path('C:/kyty/scrub/checks.txt').read_text(encoding='utf-8').splitlines() if l.strip()]
blocking = 0
for name, root in REPOS:
    head = subprocess.run(['git', '-C', root, 'rev-parse', '--short=8', 'HEAD'], capture_output=True, text=True).stdout.strip()
    for i, p in enumerate(pats, 1):
        r = subprocess.run(['git', '-C', root, 'grep', '-P', '-a', '-c', '-e', p, 'HEAD'],
                           capture_output=True)
        if r.returncode not in (0, 1):
            sys.exit('git grep failed on pattern #%d: %r' % (i, r.stderr[:200]))
        files = []
        for ln in r.stdout.decode('utf-8', 'replace').splitlines():
            # HEAD:path:count
            _, rest = ln.split(':', 1)
            path, cnt = rest.rsplit(':', 1)
            files.append((path, int(cnt)))
        hits = sum(c for _, c in files)
        cls = 'ok'
        if files:
            if i == 9:
                cls = 'non-blocking (134(g)(1))'
            elif i == 7 and all((name, f) in NAMED7 and c == 1 for f, c in files):
                cls = 'non-blocking (135(v)), the two named lines'
            else:
                cls = 'BLOCKING'; blocking += 1
        print('%s@%s pattern#%d files %d hits %d %s' % (name, head, i, len(files), hits, cls))
print('BLOCKING PATTERNS:', blocking)
