# FS8b: write build_fs8n.cmd = build_fs8b.cmd with SRC/BUILD moved to C:\kyty\f287\fs8n (negative control build).
p = 'C:/kyty/f287/fs8b/build_fs8b.cmd'
t = open(p, 'rb').read().decode('utf-8')
a = 'C:\\kyty\\f287\\fs8b\\wt'
b = 'C:\\kyty\\f287\\fs8b\\build'
assert t.count(a) == 1 and t.count(b) == 1, (t.count(a), t.count(b))
t = t.replace(a, 'C:\\kyty\\f287\\fs8n\\wt').replace(b, 'C:\\kyty\\f287\\fs8n\\build')
nl = '\r\n' if '\r\n' in t else '\n'
t = 'rem FS8b negative control: copy of build_fs8b.cmd with SRC/BUILD in C:\\kyty\\f287\\fs8n.' + nl + t
open('C:/kyty/f287/fs8b/build_fs8n.cmd', 'wb').write(t.encode('utf-8'))
print('ok', [l for l in t.splitlines() if l.startswith('set "SRC') or l.startswith('set "BUILD')])
