import os, sys
LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    print('LOCKED'); sys.exit(5)
src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'facts_s15r2.md')
dst = 'C:/kyty/s288/FACTS.md'
add = open(src, 'rb').read().replace(b'\r', b'')
cur = open(dst, 'rb').read()
if b'## S15r2 ' in cur:
    print('already there'); sys.exit(0)
if not cur.endswith(b'\n'):
    add = b'\n' + add
open(dst, 'ab').write(add)
print('appended', len(add))
