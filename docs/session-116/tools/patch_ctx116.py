"""Session 116 close: game-folder CLAUDE.md (= AGENTS.md) state, s116 entry (drop s112), env note; HANDOFF line."""
from pathlib import Path

ROOT = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')
C = ROOT / 'CLAUDE.md'
raw = C.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')

# 1. state paragraph
a = s.index('**СОСТОЯНИЕ (2026-09-25, вечер): ЦИКЛ СЕССИЙ ИДЁТ**')
b = s.index('Дата: 2026-09-25. **Сессия115:')
STATE = """**СОСТОЯНИЕ (2026-09-25, ночь): ЦИКЛ СЕССИЙ ИДЁТ** (пользователь, /loop: сессии подряд, вопросов не задавать; игру
запускать можно; push — нет). **Сессия 116 закрыта** (аудит: числа подтверждены; MAJOR — потолок трека T1 опровергнут,
время полного `--no-memo` прогона v4.1 не замерено), следующая — `docs/next-session-117.md`: замер `--no-memo` v4.1 на
`ttl114b`, затем запечатанная тонкая разбивка `AheadTake` (3,0 мс) и `mh_bind` (10,7 мс), затем трек по потолку ≥ 1 мс.
Установлена сборка **`d3a981a2…`** (`7c73f26`: исправление кольца записи презентации + **`titleasync=1`**); закреплённая
копия `C:/kyty/s115/kyty_emulator_d3a981a2.exe`. **Мутанты — `mutlib` v4.1 (замороженная копия
`docs/session-116/mutlib_v41/mutlib.py`, `db82ef4b`), только ПОЛНЫЕ прогоны `--control --no-memo --work-dir
C:/kyty/s1NN/work*`; `--changed-from` запрещён (ревью v4.1: выборка небезопасна в общем случае); ускорение `mutlib`
остановлено.** Запечатанная цепочка: замок `C:/kyty/SEALED_RUN.lock`, шлюз `procload.py`, **отказ, пока жив любой процесс
с `mutlib.py`; агенты с тяжёлыми задачами останавливаются перед цепочкой; два тяжёлых задания не одновременно**; состояние
цикла — `C:/kyty/LOOP_STATE.md`. Правила с. 106–116 действуют: решение до действия (и любое изменение запущенного
воркфлоу, и любой выброшенный им этап), запечатанное следствие после исхода не отменяется, фикстуры на каждый член/край,
генераторы — якоря целыми строками, главный оценщик ABBA — кадры 10–89 блока, режим BDA — по счёту `bda_scan`, уровни
разных режимов не сравниваются, трек скорости — только при измеренном потолке ≥ 1 мс на кадр. **Скорость игры =
16 667 / mean `dt_us`. 60 FPS не обещать.**

Дата: 2026-09-25. **Сессия116: ПЕРВАЯ ЧИСТАЯ РАЗБИВКА ФАЗ GuestGpu НА `d3a981a2` (ПЕЧАТЬ 01 `obs116` ADMITTED); `mutlib`
v4.1 ПРИНЯТ ТОЛЬКО ДЛЯ ПОЛНЫХ ПРОГОНОВ; ТРЕК T1 (ПРОМАХИ ПАМЯТИ ПРОГРАММ) СНЯТ АУДИТОМ; КОДА ЭМУЛЯТОРА НЕТ.** Разбивка
(Sky Garden, пин, NEW, `mutsite`+`pathlap`+`KYTY_GPU_WALL`, на кадр): `dt` 31 650 мкс (скорость игры 52,7 %), `cpu_gpu`
30 994, GuestGpu занят весь кадр; удержание render mutex 92,3 %: **`mh_bind` 10 662 (34,4 %)**, **`mh_emit` 7 477
(24,1 %; com 2 275, rt 1 600, vtx 1 403, rec 1 280, pipe 762)**, **`mh_prog` 6 711 (21,7 %), из них `da_take_us`
3 002**, `mh_disp` 2 342, остаток вне мьютекса 2 055; цена операции 5,74 мкс; три инструмента сходятся в пределах
1,5 %. `pmemo_miss` 2 206 на кадр (стадии), но надбавка промаха 0,20–0,29 мкс ⇒ потолок ≈ 0,45–0,65 мс < 1 мс ⇒ T1 снят.
`mutlib` v4.1 (`db82ef4b`): тест-зависимый `--changed-from` принят приёмкой, но ревью нашло ложное ALL KILLED при забытой
фикстуре ⇒ только полные прогоны. Источник истины — `C:/kyty/s116/FACTS.md`, в git `docs/local-session-116.md`.

"""
s = s[:a] + STATE + s[b:]

# 2. drop the s112 entry (keep the four latest sessions)
a = s.index('Дата: 2026-09-24. **Сессия112:')
b = s.index('**РЕШЕНИЯ ПОЛЬЗОВАТЕЛЯ ПОСЛЕ СЕССИИ 101')
s = s[:a] + s[b:]

# 3. env section: s116 bullet before the s115 bullet
ANCHOR = '- Сто пятнадцатая сессия (**одно отгруженное умолчание'
assert s.count(ANCHOR) == 1
ENV = """- Сто шестнадцатая сессия (**кода эмулятора нет, умолчания не сдвинуты**): харнесс `C:/kyty/s116` — `obs116.py`
  (скорер разбивки фаз: `mh_*` мкс, `pl_*`/`gw_*` нс → мкс один раз, остаток вне мьютекса = `pl_proc − a_hold_us −
  a_wait_us`, **формула с. 96 вычитала `mh_pres_us`, которого в `a_hold_us` нет**; тождества emit с допуском 256 по
  сумме — флип читает счётчики по одному, перекос строки до ±60; для областей, засчитываемых при закрытии, — только
  средние), `test_obs116.py`, `mut_obs116.py`, `go116a.sh`, `gates_obs116.txt` (`mutsite=1`, `pathlap=1`),
  `procload.py` (отказ, пока жив процесс `mutlib.py`). **`pmemo_hit/miss` считают СТАДИИ (≈ 1,77 на draw), не draw.**
  `mutlib` v4.1 — `docs/session-116/mutlib_v41/` (только полные прогоны).
"""
s = s.replace(ANCHOR, ENV + ANCHOR)

out = s.replace('\n', '\r\n') if crlf else s
C.write_bytes(out.encode('utf-8'))
(ROOT / 'AGENTS.md').write_bytes(out.encode('utf-8'))

# 4. HANDOFF line
H = ROOT / 'HANDOFF.md'
hraw = H.read_bytes().decode('utf-8')
hcrlf = '\r\n' in hraw
h = hraw.replace('\r\n', '\n').rstrip('\n') + '\n'
h += """
Дата: 2026-09-25. **Сессия 116 (кратко; источник истины — `docs/local-session-116.md`).** `mutlib` v4.1 принят только для полных прогонов (выборочный `--changed-from` небезопасен по ревью). Печать 01 `obs116` ADMITTED — первая чистая разбивка фаз GuestGpu на `d3a981a2`: render mutex 92,3 % CPU кадра, `mh_bind` 10,7 мс, `mh_emit` 7,5 мс, `mh_prog` 6,7 мс (из них `AheadTake` 3,0 мс). Трек T1 (промахи памяти программ) снят аудитом: потолок 0,45–0,65 мс. Кода эмулятора нет; сборка `d3a981a2` остаётся. Далее — `docs/next-session-117.md`.
"""
H.write_bytes((h.replace('\n', '\r\n') if hcrlf else h).encode('utf-8'))
print('ok')
