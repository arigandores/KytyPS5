"""F23a (HPP-578): checks every reference `<commit>:<path>:<line>` of docs/track-f/f23a.md that carries
'якорь «A»; +1 — «B»': line <line> of <path> at <commit> (git show) must contain A, line <line>+1 must contain B
(general rule 24(1)). Prints one line per reference and ALL OK / FAILED. Usage: python refs_f23a.py <report.md>"""
import re
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
text = open(sys.argv[1], encoding='utf-8').read()
pat = re.compile(r'`([0-9a-f]{8}):([^`:\s]+):(\d+)`(.{0,120}?)якорь\s+«(.+?)»;?\s*\+1\s+—\s+«(.+?)»', re.S)
cache = {}
n = bad = 0
for m in pat.finditer(text):
    c, path, line, mid, a, b = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5), m.group(6)
    if '`' in mid and re.search(r'`[0-9a-f]{8}:', mid):
        continue  # the anchor belongs to a later reference
    a = re.sub(r'\s+', ' ', a).strip()
    b = re.sub(r'\s+', ' ', b).strip()
    key = (c, path)
    if key not in cache:
        r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % key], capture_output=True)
        cache[key] = r.stdout.decode('utf-8').split(chr(10)) if r.returncode == 0 else None
    L = cache[key]
    n += 1
    if L is None or line > len(L):
        ok = False
        why = 'no file/line'
    else:
        l0 = re.sub(r'\s+', ' ', L[line - 1])
        l1 = re.sub(r'\s+', ' ', L[line]) if line < len(L) else ''
        ok = a in l0 and b in l1
        why = '' if ok else 'anchor %s, +1 %s' % ('ok' if a in l0 else 'MISS', 'ok' if b in l1 else 'MISS')
    bad += 0 if ok else 1
    print('%s %s:%s:%d %s' % ('ok  ' if ok else 'FAIL', c, path, line, why))
print('references %d, failed %d' % (n, bad))
print('ALL OK' if bad == 0 and n > 0 else 'FAILED')
sys.exit(0 if bad == 0 and n > 0 else 1)
