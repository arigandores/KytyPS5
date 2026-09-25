"""ROADMAP: session 115 item 8 (seal 01 chk115 verdict PASS and its sealed consequence), written before the next action."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   `pred/01_chk115_amend1.md`, новые хэши — в `SEALS115.txt` до прогона.
"""
NEW = ANCHOR + """8. **Итог печати 01 `chk115` — PASS (записано до следующего действия):** `go115a` 14:19–14:26 (шлюз поправки 1 чист,
   CPU 3 %, GPU 2 %). **`vid115`**: 3 894 кадра, 0 глитчей, 3 418 строк сцены, стена `UpdateTitle` 31,3 мкс на вызов
   (медиана 24,1), `present_overlap` 0, маркеров нет, **режим BDA NEW** (`bda_scan` медиана 51). **`boot115a`**: `startup
   wait finished in 10111 ms presents_other=607 presents_main=0`, сцена достигнута, падений нет; **`boot115c`**
   (`KYTY_TITLE_ASYNC=1`): 10 115 мс, 606 / 0; **`boot115b`** (контроль): `PrepareMainPresent: mode 1`, затем
   `commandRecorder.cpp:326` после удержания, строки ожидания нет — старая презентация главного потока по-прежнему роняет
   кольцо, исправление его обходит. Q1 HIT (N 10 111/10 115, P 607/606, M 0); Q3 MISS по числу кадров (3 894 < 3 900;
   глитчей 0). **Следствие печати: сборка `d3a981a2…` остаётся установленной, `titleasync=1` отгружен, C1 закрыт по
   построению** (главный поток не презентует), долгий старт больше не падает на `:326` в проверенной нагрузке (тёплая
   подготовка с удержанием 10 с). Дальше: вердикт v4 (воркфлоу идёт), долги F2, трек скорости, аудит сессии.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
