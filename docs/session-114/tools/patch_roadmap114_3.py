"""ROADMAP: session 114 item 3 (the user's instruction: no game runs until the user allows it)."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   корректности: планка — «не медленнее», а не −100) → видео сборки с проверочным скриптом.
"""
NEW = ANCHOR + """3. **Указание пользователя (2026-09-24, дословно: «пока делай все по сессии, но игру не запускай, я скажу когда
   можна»):** ни одного запуска игры (цепочек `go*.sh`, `enter_scene.py`, видео) до явного разрешения пользователя —
   это касается и хартбита. Сессия идёт офлайн: сборка `78f290d4` (`36522d2`), враждебный разбор правки, печати 01
   (контроль `KYTY_MAIN_STALL_TEST`) и 02 (ABBA `titleasync=0|1`) со скорерами, фикстурами и мутантами — готовятся и
   запечатываются, но не запускаются; `mutlib` v3 (офлайн) — можно. После разрешения — цепочки по порядку п. 2(4).
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
