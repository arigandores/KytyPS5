# F24d (HPP-663, Red Team): append the F24d section of C:/kyty/f287/FACTS.md from facts_f24d.tmpl.md (once).
import sys

F = 'C:/kyty/f287/FACTS.md'
tmpl = open(sys.argv[1], 'rb').read().decode('utf-8')
cur = open(F, 'rb').read().decode('utf-8')
if '## F24d (`HPP-663`' in cur:
    sys.exit('F24d section already present')
if not cur.endswith('\n'):
    cur += '\n'
open(F, 'wb').write((cur + tmpl).encode('utf-8'))
print('appended', len(tmpl), 'chars')
