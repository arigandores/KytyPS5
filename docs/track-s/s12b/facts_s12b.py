# S12b (HPP-495): append the S12b section to C:/kyty/s288/FACTS.md from facts_s12b.tmpl.md (LF, once).
import sys
F = 'C:/kyty/s288/FACTS.md'
T = sys.argv[1]
add = open(T, 'rb').read().replace(b'\r', b'')
cur = open(F, 'rb').read()
if b'## S12b \xe2\x80\x94' in cur:
    print('ALREADY PRESENT')
    sys.exit(1)
if not cur.endswith(b'\n'):
    cur += b'\n'
open(F, 'wb').write(cur + add)
print('APPENDED', len(add))
