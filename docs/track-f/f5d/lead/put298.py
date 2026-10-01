import sys, os, shutil, subprocess
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(3)
SCR = os.path.dirname(os.path.abspath(__file__))
def append(path, src):
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    t = raw.decode('utf-8').replace('\r\n', '\n')
    add = open(os.path.join(SCR, src), encoding='utf-8').read()
    assert add.strip().split('\n')[0] not in t, ('already there', path)
    t = t.rstrip('\n') + '\n' + add
    if crlf:
        t = t.replace('\n', '\r\n')
    open(path, 'wb').write(t.encode('utf-8'))
    print('appended', path)
append('C:/kyty/KytyPS5/docs/track-f/register.md', 'reg298.md')
append('C:/kyty/f287/FACTS.md', 'facts298.md')
d = 'C:/kyty/KytyPS5/docs/track-f/f5d/lead/'
os.makedirs(d, exist_ok=True)
for f in ('f5d_chk.py', 'f5d_chk.out.txt', 'p298.md', 'ins298.py'):
    shutil.copyfile('C:/kyty/f287/lead/' + f, d + f)
for f in ('reg298.md', 'facts298.md', 'put298.py'):
    shutil.copyfile(os.path.join(SCR, f), 'C:/kyty/f287/lead/' + f)
    shutil.copyfile(os.path.join(SCR, f), d + f)
tm = subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], capture_output=True, text=True).stdout.strip()
with open('C:/kyty/f287/times.txt', 'a', encoding='utf-8') as f:
    f.write(tm + ' F5d HPP-358 lead: register s19 and FACTS F5d written, copies in docs/track-f/f5d/lead (no lock, no STOP)\n')
print('done', tm)
