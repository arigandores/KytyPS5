# -*- coding: utf-8 -*-
"""HPP-153: add privacy finding P-1 to the s130 audit status paragraph (CLAUDE.md == AGENTS.md), HANDOFF entry and FACTS Step 9."""
from pathlib import Path

D = Path('C:/kyty/KytyPS5/ps5 em')
F = Path('C:/kyty/s130/FACTS.md')
OLD = 'Числа скорости в с. 130 нет. Аудит — `C:/kyty/s130/audit130/AUDIT130.md`'
NEW = ('Числа скорости в с. 130 нет. **П-1 (приватность, вне вердикта, блокирует push):** `docs/session-129/audit/'
       'mirror_facts129.py` (коммит `56dd1d91`, не отправлен) несёт список личных идентификаторов — до push чистка истории; '
       'в 27 отправленных файлах с. 99/120 — имя чужого приложения. Аудит — `C:/kyty/s130/audit130/AUDIT130.md`')
for n in ('CLAUDE.md', 'AGENTS.md'):
    p = D / n
    t = p.read_bytes().decode('utf-8')
    assert t.count(OLD) == 1, n
    p.write_bytes(t.replace(OLD, NEW).encode('utf-8'))
assert (D / 'CLAUDE.md').read_bytes() == (D / 'AGENTS.md').read_bytes()

p = D / 'HANDOFF.md'
t = p.read_bytes().decode('utf-8')
HO = 'записей (Р8 [U]), OLD, `acinline`. Закрытие — `HPP-154` (лид).'
HN = ('записей (Р8 [U]), OLD, `acinline`. П-1 (приватность, блокирует push): `docs/session-129/audit/mirror_facts129.py` '
      '(`56dd1d91`, не отправлен) несёт список личных идентификаторов — чистка истории до push. Закрытие — `HPP-154` (лид).')
assert t.count(HO) == 1
p.write_bytes(t.replace(HO, HN).encode('utf-8'))

ft = F.read_bytes().decode('utf-8')
FO = '**Долги** — `AUDIT130.md` § 7. Числа скорости в с. 130 нет. 60 FPS не обещаются.\n'
FN = (FO + '\n**П-1 (приватность, вне вердикта, блокирует следующий push):** `docs/session-129/audit/mirror_facts129.py` '
      '(коммит `56dd1d91`, не отправлен) несёт список личных идентификаторов и имён чужих приложений — до push нужна чистка '
      'истории (решение пользователя/лида); в 27 отправленных файлах `docs/session-99/**`, `docs/session-120/audit/'
      'protocol.md` — имя чужого приложения. `mirror_facts130.py` в git не кладётся.\n')
assert ft.count(FO) == 1
F.write_bytes(ft.replace(FO, FN).encode('utf-8'))
print('ok')
