# FS6b (HPP-556, Red Team): appends the FS6b section to C:/kyty/f287/FACTS.md from facts_fs6b.tmpl.md (LF, once).
# Usage: python facts_fs6b.py <END utc> <commit>
import sys
end, commit = sys.argv[1], sys.argv[2]
t = open('C:/kyty/f287/fs6b/facts_fs6b.tmpl.md', 'rb').read().decode('utf-8').replace('\r', '')
t = t.replace('{END}', end).replace('{COMMIT}', commit).replace('{{', '{').replace('}}', '}')
p = 'C:/kyty/f287/FACTS.md'
cur = open(p, 'rb').read().decode('utf-8')
if '## FS6b (`HPP-556`' in cur:
    print('FACTS: FS6b section already present')
    sys.exit(0)
if not cur.endswith('\n'):
    t = '\n' + t
open(p, 'ab').write(t.encode('utf-8'))
print('FACTS: FS6b section appended,', len(t.encode('utf-8')), 'bytes')
