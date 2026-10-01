# insert p.259 before the "ИТОГ ЦИКЛА СЕССИЙ 103-108" block of ROADMAP.md; LF, checks last item number
import re
P = 'C:/kyty/KytyPS5/docs/ROADMAP.md'
b = open(P, 'rb').read()
assert b'\r\n' not in b[:200000]
L = b.decode('utf-8').split('\n')
new = open('C:/kyty/f287/lead/p259.md', 'rb').read().decode('utf-8').rstrip('\n').split('\n')
anc = next(i for i, l in enumerate(L) if l.startswith('**ИТОГ ЦИКЛА СЕССИЙ 103–108'))
assert L[anc - 1] == ''
nums = [int(m.group(1)) for l in L[:anc] for m in [re.match(r'^(\d{3})\. \*\*', l)] if m]
assert nums[-1] == 258, nums[-3:]
assert not any(l.startswith('259. ') for l in L)
L[anc - 1:anc - 1] = new
open(P, 'wb').write('\n'.join(L).encode('utf-8'))
print('inserted at', anc, 'lines', len(new))
