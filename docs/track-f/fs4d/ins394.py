import re, sys, datetime
# insert lead item into ROADMAP: number = max + 1 at insertion, time = UTC now (Process p.1 of S2a audit, item 355(i))
P = 'C:/kyty/KytyPS5/docs/ROADMAP.md'
SRC = sys.argv[1]
WANT = int(sys.argv[2])
b = open(P, 'rb').read()
assert b'\r' not in b, 'CRLF in ROADMAP'
t = b.decode('utf-8')
nums = [int(m.group(1)) for m in re.finditer(r'(?m)^(\d{3})\. ', t)]
n = max(nums) + 1
if n != WANT:
    print('NUMBER CHANGED: next is %d, files are named %d - stop' % (n, WANT)); sys.exit(2)
now = datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S')
body = open(SRC, 'rb').read().decode('utf-8').replace('\r', '')
body = body.replace('{N}', str(n)).replace('{TIME}', now)
assert '{' not in body.split('\n')[0][:6]
if not t.endswith('\n'): t += '\n'
t = t + body
if not t.endswith('\n'): t += '\n'
open(P, 'wb').write(t.encode('utf-8'))
print('inserted item %d at %s UTC' % (n, now))
