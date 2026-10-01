"""F6b (HPP-373): insert p.287 into ROADMAP.md before the 'ИТОГ ЦИКЛА СЕССИЙ 103' line (decision time = date -u now) and append register section 17.
LF, write_bytes; aborts on lock."""
import datetime, os, pathlib, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(3)
R = pathlib.Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
G = pathlib.Path('C:/kyty/KytyPS5/docs/track-f/register.md')
T = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
p = pathlib.Path('C:/kyty/f287/lead/p287.md').read_bytes().decode('utf-8').replace('\r', '')
assert p.count('{T}') == 1
p = p.replace('{T}', T)
g = pathlib.Path('C:/kyty/f287/lead/reg287.md').read_bytes().decode('utf-8').replace('\r', '')
t = R.read_bytes().decode('utf-8')
assert '\r' not in t
assert '\n287. **' not in t and '\n286. **' in t, 'numbering'
anchor = '\n**ИТОГ ЦИКЛА СЕССИЙ 103–108'
assert t.count(anchor) == 1
i = t.index(anchor) + 1
prev = t[:i]
assert prev.endswith('цель (B) не меняется.\n\n'), repr(prev[-60:])
t = prev + p.rstrip('\n') + '\n\n' + t[i:]
R.write_bytes(t.encode('utf-8'))
r = G.read_bytes().decode('utf-8')
assert '\r' not in r and '## 17.' not in r and '## 16.' in r
G.write_bytes((r.rstrip('\n') + '\n' + g.rstrip('\n') + '\n').encode('utf-8'))
lines = t.split('\n')
n = [k + 1 for k, l in enumerate(lines) if l.startswith('287. **')]
print('ok decision', T, 'line', n)
