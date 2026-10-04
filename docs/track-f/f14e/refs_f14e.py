# F14e: every <commit>:<path>:<line> reference of docs/track-f/f14e.md with an anchor and a +1 line
# (general rule 24(1)) - the line at <line> contains the anchor, the next line contains the +1 text.
import os, re, subprocess, sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('HALT lock'); sys.exit(3)
GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
text = open(REPO + '/docs/track-f/f14e.md', encoding='utf-8').read()
flat = re.sub(r'\s*\n\s*', ' ', text)
pat = re.compile(r'`([0-9a-f]{8}):([^`:]+):(\d+)`[^«]{0,80}?якорь(?: без отступа)? «(.+?)»; \+1 — «(.+?)»')
cache = {}
n = bad = 0
for m in pat.finditer(flat):
    commit, path, line, anchor, plus = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5)
    key = (commit, path)
    if key not in cache:
        out = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % key], capture_output=True)
        cache[key] = out.stdout.decode('utf-8', 'replace').replace('\r', '').split('\n')
    lines = cache[key]
    norm = lambda s: ' '.join(s.split())
    a_ok = line - 1 < len(lines) and norm(anchor) in norm(lines[line - 1])
    p_ok = line < len(lines) and norm(plus) in norm(lines[line])
    n += 1
    status = 'OK' if a_ok and p_ok else 'BAD'
    if status == 'BAD':
        bad += 1
    print('%s %s:%s:%d anchor=%s plus1=%s' % (status, commit, path, line, a_ok, p_ok))
print('refs', n, 'bad', bad)
print('ALL OK' if n > 0 and bad == 0 else 'MISMATCH')
