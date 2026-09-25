"""ROADMAP: session 116 item 6 (obs116 ADMITTED: the phase split; the next speed track), written before acting."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   Замороженная копия v4.1 — `docs/session-116/mutlib_v41/`. `V41_GO` снимается; дальше — запечатанный `go116a`.
"""
NEW = ANCHOR + """6. **Итог печати 01 `obs116` — ADMITTED; разбивка фаз и выбор трека (записано до действий):** цепочка 19:08–19:14,
   простой CPU 4 %, GPU 1 %, все 23 проверки допуска; 9 498 строк сцены с кадра 432, 300,6 с, режим BDA **NEW** (медиана
   `bda_scan` 56). **Уровни (с инструментами `mutsite`+`pathlap`+`KYTY_GPU_WALL`, на кадр):** `dt` 31 650 мкс (скорость
   игры 52,7 %), `cpu_gpu` 30 994 мкс, GuestGpu занят весь кадр (`gw_idle` 28 мкс); удержание render mutex 28 592 мкс =
   **92,3 %**: **`mh_bind` 10 662 (34,4 %; 2,09 мкс на draw)**, **`mh_emit` 7 477 (24,1 %; 1,46 мкс; внутри: com 2 275, rt
   1 600, vtx 1 403, rec 1 280, pipe 762)**, **`mh_prog` 6 711 (21,7 %; 1,31 мкс)**, `mh_disp` 2 342 (7,6 %; 8,7 мкс на
   dispatch), `mh_rt` 798, `mh_pro` 338, `mh_tail` 263; вне мьютекса: именованные 700 (из них `pl_cmd` 564), остаток
   2 055 (6,6 %). Цена операции 5,74 мкс (5 129 draw + 268 dispatch). Сверки: hold/`a_hold` 0,997, emit_split/`mh_emit`
   0,985, `pl_proc`/`gw_proc` 1,000. Память программ: `pmemo_hit` 6 812, **`pmemo_miss` 2 206 на кадр (24,5 % из 9 018
   обращений)**, проверка памяти `pmemo_chk_us` 433 мкс. **Решение о треке (сессия 117):** **T1 — промахи памяти программ
   (`mh_prog`)**: сначала перепись без изменения поведения — расстояние повторного использования сигнатуры входов
   `PrepareProgram` при промахе (сколько промахов попало бы в память на 2/4/8/16 записей) и цена одного промаха; потолок
   ≈ `pmemo_miss` × цена промаха (оценка сверху — большая часть 6,7 мс); если перепись покажет ≥ 1 мс на кадр —
   многозаписная память (ручка, умолчание 0) со своей проверкой и ABBA. Запас: T2 — `mh_bind` (34 %, большая, но изрядно
   пройденная M1/M2), T3 — `mh_emit` com/rt. Порядок и планки — в плане сессии 117.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
