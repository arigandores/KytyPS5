# F16e2 (HPP-570, Red Team): append the section template to C:/kyty/f287/FACTS.md (LF, UTF-8) once.
import sys

src, dst = sys.argv[1], sys.argv[2]
text = open(src, 'rb').read().decode('utf-8').replace('\r\n', '\n')
cur = open(dst, 'rb').read().decode('utf-8')
marker = '## F16e2 (`HPP-570`, Red Team)'
if marker in cur:
    print('already present')
    sys.exit(0)
if not cur.endswith('\n'):
    cur += '\n'
open(dst, 'wb').write((cur + text).encode('utf-8'))
print('appended', len(text))
