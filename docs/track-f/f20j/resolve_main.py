# F20j: the one cherry-pick conflict on main (graphicsRun.cpp, loop top): keep both blocks - main's DiagF5/F6 service
# (F16k, not in FS8) first, then the F20j stand point. LF file.
import re
p = 'C:/kyty/KytyPS5/src/graphics/guest_gpu/graphicsRun.cpp'
t = open(p, 'rb').read().decode('utf-8')
assert '\r\n' not in t
pat = re.compile(r'<<<<<<< HEAD\n(.*?)\|\|\|\|\|\|\| parent of 875720c5[^\n]*\n(.*?)=======\n(.*?)>>>>>>> 875720c5[^\n]*\n', re.S)
m = list(pat.finditer(t))
assert len(m) == 1, len(m)
ours, base, theirs = m[0].group(1), m[0].group(2), m[0].group(3)
assert base == ''
t = t[:m[0].start()] + ours + theirs + t[m[0].end():]
assert '<<<<<<<' not in t and '>>>>>>>' not in t
open(p, 'wb').write(t.encode('utf-8'))
print('resolved')
