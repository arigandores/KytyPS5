"""F3e (HPP-343): insert p.282 into ROADMAP.md before the 'ИТОГ ЦИКЛА СЕССИЙ 103' line and append register section 16. LF, write_bytes."""
import pathlib
R = pathlib.Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
G = pathlib.Path('C:/kyty/KytyPS5/docs/track-f/register.md')
p = pathlib.Path('C:/kyty/f287/lead/p282.md').read_bytes().decode('utf-8').replace('\r', '')
g = pathlib.Path('C:/kyty/f287/lead/reg282.md').read_bytes().decode('utf-8').replace('\r', '')
t = R.read_bytes().decode('utf-8')
assert '\r' not in t
assert '\n282. **' not in t, '282 already present'
anchor = '\n**ИТОГ ЦИКЛА СЕССИЙ 103–108'
assert t.count(anchor) == 1
i = t.index(anchor) + 1
prev = t[:i]
assert prev.endswith('цель (B) не меняется.\n\n'), repr(prev[-60:])
t = prev + p.rstrip('\n') + '\n\n' + t[i:]
R.write_bytes(t.encode('utf-8'))
r = G.read_bytes().decode('utf-8')
assert '\r' not in r and '## 16.' not in r
G.write_bytes((r.rstrip('\n') + '\n' + g.rstrip('\n') + '\n').encode('utf-8'))
print('ok', t.count('\n282. **'))
