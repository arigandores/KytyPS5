"""F10c (HPP-451): build_f10c.cmd and lockrun.sh from the FS3a copies (paths changed only)."""
src = 'C:/kyty/f287/fs3/fs3a/'
b = open(src + 'build_fs3a.cmd', 'rb').read().decode()
old_src = 'set "SRC=C:\\kyty\\f287\\fs3\\fs3a\\wt"'
old_bld = 'set "BUILD=C:\\kyty\\f287\\fs3\\fs3a\\build"'
assert b.count(old_src) == 1 and b.count(old_bld) == 1
b = b.replace(old_src, 'set "SRC=C:\\kyty\\f287\\f10c\\wt"').replace(old_bld, 'set "BUILD=C:\\kyty\\f287\\f10c\\build"')
nl = '\r\n' if '\r\n' in b else '\n'
b = b.replace('rem FS3a (HPP-447', 'rem F10c (HPP-451, ROADMAP s122 item 369(b)): copy of build_fs3a.cmd with SRC/BUILD set to f10c. Was:' + nl +
              'rem FS3a (HPP-447', 1)
open('C:/kyty/f287/f10c/build_f10c.cmd', 'wb').write(b.encode())
l = open(src + 'lockrun.sh', 'rb').read().decode()
old = 'C:\\\\kyty\\\\f287\\\\fs3\\\\fs3a\\\\build_fs3a.cmd'
assert l.count(old) == 1, l
l = l.replace(old, 'C:\\\\kyty\\\\f287\\\\f10c\\\\build_f10c.cmd')
l = l.replace('# FS3a (copy of', '# F10c (copy of the FS3a script, build script path changed). Was:\n# FS3a (copy of', 1)
open('C:/kyty/f287/f10c/lockrun.sh', 'wb').write(l.encode())
print('ALL OK')
