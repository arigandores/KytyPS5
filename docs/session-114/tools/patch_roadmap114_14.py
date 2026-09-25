"""ROADMAP: session 114 item 14 (seal 03b verdict KEEP_1 and the close of the session), written before the close."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   падает при любом значении ручки — это долг корректности §7.
"""
NEW = ANCHOR + """14. **Итог печати 03b `bootctl114` — KEEP_1 (записано до закрытия):** мутанты запечатанной копии 25/25, контроли 3/3;
   машина CPU 3 %, GPU 0 %. `boot114b` (умолчание 1) и `boot114c` (`KYTY_TITLE_ASYNC=0` + `gates_title0.txt`): настройка
   верна, оба — ровно одна `PrepareHold: ms=10000`, затем `commandRecorder.cpp:326`, строки `startup wait finished` нет;
   оба умерли за ~17 с. P1–P3 HIT. **Падение от ручки не зависит ⇒ умолчание `titleasync=1` остаётся**, сборка
   **`8d7ba8f4…`** установлена (закреплённая копия `C:/kyty/s114/kyty_emulator_8d7ba8f4.exe`). **Не проверено:** C1 (два
   потока в `Presenter::Present`) — нагрузка загрузки не дошла до удержания. **Закрытие сессии 114:** (1) враждебный
   аудит сессии (workflow, ≤ 6 агентов: независимый пересчёт `ttl114b`/`ctl114` по сырым логам без общего кода со
   скорерами, пересчёт `vid114`/`boot114*`, протокол «решение до действия» по коммитам, ревью кода `36522d2`, `74e2ad7`,
   `175b873`, `a74205e`; итог и поправки — п. 15); (2) возобновление `mutlib` v3 (`wf_fda12f3f-955`, стадия приёмки) —
   решение по нему в п. 15/16; (3) FACTS, `docs/local-session-114.md`, CLAUDE.md = AGENTS.md, HANDOFF, `next-session-115.md`
   (первый пункт — владение кольцом записи презентации и повтор `boot114`), коммит без push.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
