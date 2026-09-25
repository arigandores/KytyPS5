"""ROADMAP: session 115 item 6 (go115a refused on foreign load; the order of the heavy work), written before acting."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   мгновенная проверка; вывод PowerShell читается как UTF-8 с заменой.
"""
NEW = ANCHOR + """6. **Печать 01 запечатана (`c5cb874`), мутанты запечатанной копии 104/104 (`3cb0786`); цепочка `go115a` отказалась в
   11:08 без прогона** (записано до действий): 30 мин подряд чужой процесс `<foreign app>` (игра другой сессии) держал 2,4–4,4
   CPU·с/с; замок не брался, игра не запускалась — печать не тронута. **Решение:** пока машина занята чужой игрой,
   запечатанные прогоны невозможны, а тяжёлым стадиям `mutlib` v4 простой не нужен (вердикты не зависят от нагрузки, время
   v3/v4 сравнивается бок о бок в один момент; абсолютные цифры в таком окне помечаются) — **создаётся
   `C:/kyty/s115/V4_GO`**. `go115a` перезапускается, когда кончатся тяжёлые стадии v4 и чужая нагрузка (проверка
   `procload`); порядок «два тяжёлых задания не одновременно» соблюдается.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
