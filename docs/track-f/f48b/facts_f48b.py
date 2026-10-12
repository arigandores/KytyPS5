# F48b: append section "F48b" to C:/kyty/f287/FACTS.md by general rule 34 (.prev copy, mode 'a', size check)
import os, shutil, sys
F = 'C:/kyty/f287/FACTS.md'
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(3)
sec = open(sys.argv[1], 'rb').read()
before = os.path.getsize(F)
shutil.copyfile(F, F + '.prev')
with open(F, 'ab') as o:
    o.write(sec)
after = os.path.getsize(F)
ok = after == before + len(sec) and os.path.getsize(F + '.prev') == before
print('before', before, 'section', len(sec), 'after', after, 'OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
