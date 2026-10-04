# F14f2 (HPP-546): port of C:/kyty/f287/f14e2/watch_f14e2.py -> C:/kyty/f287/f14f2/watch_f14f2.py with the gate sign of
# ROADMAP s122 item 456(v)(3): a process is the gate only if an element of its argv ends with procload.py (form of api_chk.sh);
# the substring sign refused falsely on a foreign shell whose command text contains the name (13:14Z). LF bytes, whole-line anchors.
src = open('C:/kyty/f287/f14e2/watch_f14e2.py', 'rb').read().decode('utf-8')
assert '\r' not in src
lines = src.split('\n')
reps = [
    ("                    cl = ' '.join(p.cmdline())",
     "                    argv = p.cmdline()"),
    ("                    cl = ''",
     "                    argv = []"),
    ("                self.cache[key] = NEEDLE in cl",
     "                self.cache[key] = any(a.replace(chr(92), '/').endswith('/' + NEEDLE) or a == NEEDLE for a in argv)"),
]
for a, b in reps:
    n = sum(1 for l in lines if l == a)
    assert n == 1, (a, n)
    lines = [b if l == a else l for l in lines]
out = '\n'.join(lines)
out = out.replace('"""F14e2 (HPP-545;', '"""F14f2 (HPP-546): port of watch_f14e2.py, gate sign = argv element ending with procload.py (item 456(v)(3)).\nWas: F14e2 (HPP-545;', 1)
open('C:/kyty/f287/f14f2/watch_f14f2.py', 'wb').write(out.encode('utf-8'))
print('ported', len(lines), 'lines')
