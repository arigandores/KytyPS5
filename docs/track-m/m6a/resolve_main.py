"""M6a (HPP-848): resolve the cherry-pick of 6964a58f onto main - every conflict keeps both sides (main's lines first,
then the M6a line); the files are LF. Lock and STOP checked first."""
import os
import re
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/m657/STOP'):
    print('LOCK or STOP')
    sys.exit(3)
NL = chr(10)
pat = re.compile(r'<<<<<<< HEAD\n(.*?)\|\|\|\|\|\|\| parent of [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n', re.S)
for f in ['src/emulator.cpp', 'src/graphics/host_gpu/renderer/cache/textureCache.cpp']:
    p = 'C:/kyty/KytyPS5/' + f
    t = open(p, 'rb').read().decode('utf-8')
    n = 0

    def keep_both(m):
        global n
        n += 1
        if m.group(2) != '':
            raise SystemExit('base side not empty in ' + f)
        return m.group(1) + m.group(3)

    t2 = pat.sub(keep_both, t)
    if '<<<<<<<' in t2 or '>>>>>>>' in t2 or '|||||||' in t2:
        print('FAIL markers left in', f)
        sys.exit(1)
    open(p, 'wb').write(t2.encode('utf-8'))
    print('OK', f, 'conflicts', n)
print('ALL OK')
