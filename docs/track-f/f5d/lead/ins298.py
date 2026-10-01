import subprocess, sys, os, shutil
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(3)
SCR = os.path.dirname(os.path.abspath(__file__))
for f in ('p298.md', 'ins298.py'):
    shutil.copyfile(os.path.join(SCR, f), 'C:/kyty/f287/lead/' + f)
P = 'C:/kyty/KytyPS5/docs/ROADMAP.md'
raw = open(P, 'rb').read()
crlf = b'\r\n' in raw
t = raw.decode('utf-8').replace('\r\n', '\n')
tm = subprocess.run(['date', '-u', '+%Y-%m-%d %H:%M:%S'], capture_output=True, text=True).stdout.strip()
ins = open(os.path.join(SCR, 'p298.md'), encoding='utf-8').read().replace('@@TIME@@', tm)
assert '\n298. ' not in t
anchor = '\n\n**ИТОГ ЦИКЛА СЕССИЙ 103–108'
assert t.count(anchor) == 1
i = t.index(anchor)
assert '\n297. **Приёмка звена P16' in t[:i]
t = t[:i] + '\n\n' + ins.rstrip('\n') + t[i:]
if crlf:
    t = t.replace('\n', '\r\n')
open(P, 'wb').write(t.encode('utf-8'))
with open('C:/kyty/f287/times.txt', 'a', encoding='utf-8') as f:
    f.write(tm.replace(' ', 'T') + 'Z F5d HPP-358 lead: ROADMAP p.298 written (B37 FIXED; FS2 chain; no lock, no STOP)\n')
print('inserted p.298 at', tm)
