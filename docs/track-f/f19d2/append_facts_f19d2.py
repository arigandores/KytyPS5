# F19d2 (HPP-560): append the link section (template facts_f19d2.md, UTF-8, LF) to C:/kyty/f287/FACTS.md once.
import os
import sys

FACTS = 'C:/kyty/f287/FACTS.md'
TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'facts_f19d2.md')
HEAD = '## F19d2 (`HPP-560`, Red Team)'

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
cur = open(FACTS, 'rb').read().decode('utf-8')
if HEAD in cur:
    print('already present')
    sys.exit(0)
add = open(TPL, 'rb').read().decode('utf-8').replace('\r\n', '\n')
if not cur.endswith('\n'):
    add = '\n' + add
with open(FACTS, 'ab') as f:
    f.write(add.encode('utf-8'))
print('appended', len(add.encode('utf-8')), 'bytes')
