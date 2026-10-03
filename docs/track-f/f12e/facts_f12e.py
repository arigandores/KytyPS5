# F12e: append the FACTS.md section from the template (LF, write_bytes), once.
import hashlib, os, sys
LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK) or os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(3)
FACTS = 'C:/kyty/f287/FACTS.md'
tmpl = open('C:/kyty/f287/f12e/facts_f12e.tmpl.md', 'rb').read().replace(b'\r', b'')
out = hashlib.sha256(open('C:/kyty/f287/f12e/f12e_check.out.txt', 'rb').read()).hexdigest()[:8]
tmpl = tmpl.replace(b'__OUT__', out.encode())
cur = open(FACTS, 'rb').read()
if b'## F12e (`HPP-478`' in cur:
    print('already present')
    sys.exit(0)
if not cur.endswith(b'\n'):
    cur += b'\n'
open(FACTS, 'wb').write(cur + tmpl)
print('appended', len(tmpl))
