"""ROADMAP: session 117 item 1 (order, the v4.1 --no-memo timing, the fine-split plan), written before acting."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   `game-Y` (кроме запечатанного текста поправки 1 с. 115 — хэш печати сохраняется).
"""
NEW = ANCHOR + """
**СЕССИЯ 117 — ЗАПИСИ ДО ДЕЙСТВИЙ** (план `docs/next-session-117.md`; корень харнесса `C:/kyty/s117`).

1. **Порядок и замер (записано до действий):** (0) порт харнесса `C:/kyty/s117` (`enter_scene.py`, `gates_base.txt`,
   `run_safety99.py`, `procload.py` с отказом на `mutlib.py`, закреплённая копия `kyty_emulator_d3a981a2.exe`); (1) **замер
   полного прогона v4.1** — `python docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s114/ttl114b.py --test
   C:/kyty/s114/test_ttl114b.py --mutants C:/kyty/s114/mut_ttl114b_sealed.py --control --no-memo --work-dir
   C:/kyty/s117/work_t0 --out C:/kyty/s117/t0_ttl114b.out.txt` (рабочих по умолчанию, cpu − 4 = 28, как у запечатанного
   прогона v2 с. 114: 4 085,9 с = 68,1 мин); перед стартом `procload.py` (чужая нагрузка < 0,5 CPU·с/с, нет замка, нет
   других `mutlib`); пока он идёт — ни агентов, ни сборок, ни прогонов игры, только чтение кода исполнителем. **Проверка:**
   вердикт и строки мутантов равны отчёту `C:/kyty/s114/mut_ttl114b.out.txt` (345/345 убиты, контроли 3/3); иначе — это
   находка против v4.1, записывается, и мутанты печатей до её разбора гоняются v2 (`docs/session-113/mutlib/v2/`).
   **Время стены — единственная цитируемая цифра «одной ABBA-печати».** Если > 40 мин — до первой ABBA-печати
   записывается план (рабочие, размер набора), а не ускорение `mutlib` (п. 5 с. 116 в силе). (2) **Черновик печати 01
   `fin117`** — тонкая разбивка `AheadTake` и `mh_bind` (производный от `obs116` скорер, якоря целыми строками;
   счётчики — существующие `da_*` и `bindlap`); сначала чтение кода: где стоят метки `bindlap` относительно областей
   `mutsite`/`pathlap` и сколько они стоят, — записывается до черновика. (3) Трек — только при измеренном потолке ≥ 1 мс
   на кадр (п. 7 с. 116), арифметика потолка — в ROADMAP до кода.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
