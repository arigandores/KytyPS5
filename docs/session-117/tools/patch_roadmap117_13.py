"""ROADMAP: session 117 item 13 (seal 01r2: the suite's pass line), written before the change."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   `mutlib` v4.1. Урок в правила харнесса: скрипты правок пишут `write_bytes` / `newline='\\n'`.
"""
NEW = ANCHOR + """13. **Печать 01r (`482a824`) тоже не использована:** `mutlib` v4.1 отказал второй раз — набор `test_spn117.py` в конце
   печатает `ok`, а `mutlib` требует строку `ALL OK` (контракт наборов с. 113+). **Решение:** последняя строка набора
   становится `ALL OK` (при сбое — `FIXTURE FAILURES`, как было), других правок нет; печать выпускается как 01r2, строки
   01r помечаются «superseded, never run»; мутанты — `mutlib` v4.1.
"""
assert s.count(ANCHOR) == 1, s.count(ANCHOR)
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
