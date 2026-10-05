# FS8b (HPP-572, Red Team): appends the FS8b section to C:/kyty/f287/FACTS.md from facts_fs8b.tmpl.md (LF), @@NOW@@ = UTC now.
# Refuses when the lock or STOP exists, or when the section is already there.
import os, sys, time

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(3)
here = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(here, 'facts_fs8b.tmpl.md'), 'rb').read().decode('utf-8').replace('\r', '')
t = t.replace('@@NOW@@', time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
p = 'C:/kyty/f287/FACTS.md'
cur = open(p, 'rb').read().decode('utf-8')
if '## FS8b (`HPP-572`' in cur:
    print('already there')
    sys.exit(0)
with open(p, 'ab') as f:
    f.write(t.encode('utf-8'))
print('appended', len(t))
