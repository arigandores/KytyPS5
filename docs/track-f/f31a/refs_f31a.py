# F31a (HPP-729): check of the <commit>:<path>:<line> references of f31a.md - line N contains the anchor, line N+1 the
# control (general rule 24(1)); the form of refs_f26a.py.  Reads the report, finds
# '`<commit>:<path>:<line>` (якорь «A»; +1 — «B»)'.  ROADMAP references are skipped (the document changes).  Prints ALL OK.
import re, subprocess, sys
rep = sys.argv[1]
repo = 'C:/kyty/KytyPS5'
t = open(rep, encoding='utf-8').read()
pat = re.compile(r'`([0-9a-f]{8}):([^`:]+):(\d+)`,?\s*\(?якорь «(.+?)»; \+1 — «(.+?)»\)')
ok = True; n = 0
for m in pat.finditer(t):
    c, p, ln, a, b = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5)
    if p.endswith('ROADMAP.md'):
        continue
    src = subprocess.run(['git', '-C', repo, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8', 'replace').split('\n')
    l0 = src[ln - 1] if ln - 1 < len(src) else ''
    l1 = src[ln] if ln < len(src) else ''
    good = a.strip() in l0 and b.strip() in l1
    n += 1; ok &= good
    print(('ok   ' if good else 'FAIL ') + '%s:%s:%d' % (c, p, ln))
print('refs', n)
print('ALL OK' if ok and n > 0 else 'FAILED')
sys.exit(0 if ok and n > 0 else 1)
