"""ROADMAP: session 114 item 10 (the boot check made deterministic), written before the code."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   умолчание откатывается к 0, сборка `916f6489` остаётся. Всё в SEALS до прогона; цепочка `go114d.sh`.
"""
NEW = ANCHOR + """10. **Проверка загрузки — детерминированно (поправка к п. 9 (3), записано до кода):** тёплая предзагрузка — 393 мс на
   641 пайплайн, `startup wait finished in 70 ms`; `KYTY_PIPELINE_CACHE=0` её не удлинит (кеш драйвера NVIDIA остаётся),
   `KYTY_SPV_SALT` без кеша трансляции обнуляет саму подготовку, чистить общий `DXCache` пользователя — нельзя. Поэтому в
   сборку с умолчанием 1 входят два средства ТОЛЬКО ИЗМЕРЕНИЯ: **`KYTY_PREPARE_HOLD_MS=<мс>`** (раз на процесс) —
   `WindowPrepareShaders` продолжает презентовать экран подготовки с главного потока не меньше N мс после старта ожидания;
   **детектор `PresentOverlap`** — атомарный счётчик потоков внутри `Presenter::Present`; вход второго потока, пока первый
   внутри, — счётчик `present_overlap` (`FrameTrace-x`) и строки `PresentOverlap: thread= frame=` (≤ 8). Вход **`boot114`**
   (120 с, пин, `KYTY_PREPARE_HOLD_MS=10000`, умолчание `titleasync=1`): PASS — допущен, `startup wait finished in` ≥ 10 000
   мс, ни одной строки `PresentOverlap`; иначе FAIL ⇒ умолчание 0. Прежнее условие «N ≥ 2 000 при
   `KYTY_PIPELINE_CACHE=0`» снято.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
