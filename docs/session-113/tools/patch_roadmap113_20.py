"""ROADMAP 0.1 "СЕССИЯ 113" item 20 (how the shn113 mutants run on the sealed copy), written before the run."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   «принудительный OLD»; вклад в скорость игры = размер × доля естественного OLD (не измерена).
"""
NEW = ANCHOR + """20. **Мутанты `shn113` на запечатанной копии (записано до прогона):** `mutlib` v2 ОТКАЗАЛ (строгое извлечение): мутанты
   `CONST_pred_sha_prefilled` и `CONST_pred_bytes_prefilled` якорятся на `PRED_SHA = None` / `PRED_BYTES = None` — они
   проверяют «наполовину заполненную печать» и имеют смысл только на черновике. Решение: запечатанная копия — со всеми
   прочими мутантами из производного файла `mut_shn113_sealed.py` (ровно эти два вызова удалены, генератор проверяет, что
   удалено ровно два), черновая перепривязанная копия (`shn113b/shn113.py`) — с этими двумя (`--only`); оба итога и хэши —
   в `SEALS113.txt`. Правило на будущее: мутанты печати, якорящиеся на незаполненной печати, помечаются в скрипте и
   гоняются на черновике.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
