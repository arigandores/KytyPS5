import sys
B = chr(92)
d = 'C:/kyty/f287/fs9a/'
s = 'C:/kyty/f287/fs8a/'
# bstep.sh: the build cmd path
t = open(d + 'bstep.sh', 'rb').read().decode()
old = 'C:' + B * 2 + 'kyty' + B * 2 + 'f287' + B * 2 + 'fs8a' + B * 2 + 'build_fs8a.cmd'
new = 'C:' + B * 2 + 'kyty' + B * 2 + 'f287' + B * 2 + 'fs9a' + B * 2 + 'build_fs9a.cmd'
assert t.count(old) == 1, t.count(old)
open(d + 'bstep.sh', 'wb').write(t.replace(old, new).encode())
# build_fs9a.cmd
t = open(s + 'build_fs8a.cmd', 'rb').read().decode().replace('\r\n', '\n')
lines = t.split('\n')
o1 = 'set "SRC=C:' + B + 'kyty' + B + 'f287' + B + 'fs8a' + B + 'wt"'
o2 = 'set "BUILD=C:' + B + 'kyty' + B + 'f287' + B + 'fs8a' + B + 'build"'
assert lines.count(o1) == 1 and lines.count(o2) == 1
lines[lines.index(o1)] = o1.replace('fs8a', 'fs9a')
lines[lines.index(o2)] = o2.replace('fs8a', 'fs9a')
lines = ['@echo off', 'rem FS9a (HPP-671): copy of the FS8a build_fs8a.cmd with SRC/BUILD set to fs9a. Was:'] + lines[1:]
open(d + 'build_fs9a.cmd', 'wb').write('\r\n'.join(lines).encode())
print('ok')
