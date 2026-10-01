# Insert ROADMAP p.235 (S0 acceptance, HPP-294) after p.234. LF only.
from pathlib import Path
p = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
b = p.read_bytes()
assert b'\r\n' not in b
t = b.decode('utf-8')
assert '\n235. ' not in t, 'p.235 already exists'
anchor = '   обещаются; цель (B) не меняется.\n\n**ИТОГ ЦИКЛА СЕССИЙ 103–108 (пауза 2026-09-23).**'
assert t.count(anchor) == 1, t.count(anchor)
ins = Path('C:/kyty/s288/lead/p235.md').read_bytes().decode('utf-8')
assert '\r' not in ins and ins.endswith('\n')
new = anchor.replace('не меняется.\n\n', 'не меняется.\n\n' + ins + '\n', 1)
t = t.replace(anchor, new, 1)
p.write_bytes(t.encode('utf-8'))
print('OK')
