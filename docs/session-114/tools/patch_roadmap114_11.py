"""ROADMAP: session 114 item 11 (the PresentOverlap detector scope defect, found before the seal), written before the fix."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   `KYTY_PIPELINE_CACHE=0`» снято.
"""
NEW = ANCHOR + """11. **Дефект детектора `PresentOverlap` (найден при сборке `check114` до печати; записано до правки):** поток
   презентации паркуется при старте в `UpdateTitle`, а `UpdateTitle` вызывается ВНУТРИ `Presenter::Present` (после
   `swapchain.Present`, до `frames.Release`) — то есть в зоне детектора сборки `c6892df1`. Тогда первый же `Present`
   главного потока из `WindowPrepareShaders` видит «второй поток внутри» при ЛЮБОМ `titleasync`, и проверки
   `no_overlap`/`boot_no_overlap` дали бы ложный FAIL. **Решение:** зона детектора — от входа до конца работы со
   swapchain (`AcquireNextImage` … `swapchain.Present`, отметка оверлея), выход из неё — перед `UpdateTitle`
   (метод `Leave()`, деструктор вызывает его же); новая сборка, её копия закрепляется, `check114` генерируется против
   неё; сборка `c6892df1` не прогоняется. Положительного контроля детектора нет (гейтинг п. 4 не отключается) — это
   ограничение, записывается в печать. Строка `boot114` rows_before_wait (строки кадров гостя до конца ожидания) — только
   сообщается: гость стартует после `WindowPrepareShaders` (`emulator.cpp` `Execute`), нагрузка проверки — поток
   презентации `VideoOut`, не гость.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
