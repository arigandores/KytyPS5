"""Session 114 close: the game-folder context files CLAUDE.md = AGENTS.md - state, the session-114 entry (the session-110
entry leaves: four sessions kept), the environment variables of session 114."""
import re
from pathlib import Path

DIR = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')
src = (DIR / 'CLAUDE.md').read_bytes().decode('utf-8')
crlf = '\r\n' in src
s = src.replace('\r\n', '\n')

a = s.index('**СОСТОЯНИЕ (2026-09-24): ЦИКЛ СЕССИЙ ИДЁТ**')
b = s.index('Дата: 2026-09-24. **Сессия113:')
STATE = """**СОСТОЯНИЕ (2026-09-25): ЦИКЛ СЕССИЙ ИДЁТ** (пользователь, /loop: сессии подряд, вопросов не задавать; игру запускать
можно; push — нет). **Сессия 114 закрыта** (аудит: MAJOR P1 — п. 13 отменил запечатанное следствие после исхода; решено по
печати), следующая — `docs/next-session-115.md`: сначала кольцо записи презентации (падение старта `commandRecorder.cpp:326`
при долгой подготовке шейдеров), затем новая проверка загрузки и повторная отгрузка `titleasync=1`, затем `mutlib` v3 и
трек скорости. Установлена сборка **`916f6489…`** (`74e2ad7`, `titleasync` есть, умолчание 0); закреплённая копия
`C:/kyty/s114/kyty_emulator_916f6489.exe`; HEAD `1713c6d` — умолчание 0 плюс измерительные средства загрузки (не
собран как установленный). Все цепочки держат замок `C:/kyty/SEALED_RUN.lock`; во время запечатанного прогона — ни
агентов, ни сборок, ни мутантов; **два тяжёлых задания (mutlib, воркфлоу) одновременно не запускать**; состояние цикла —
`C:/kyty/LOOP_STATE.md`. Решения после с. 106–114 (`ROADMAP.md` §0.1) действуют: фикстуры на каждый член, ветку, край;
мутанты — `mutlib` v2 (замороженная копия `docs/session-113/mutlib/v2/mutlib.py`, всегда `--work-dir` вне репозитория)
на запечатанной копии; генераторы — якоря целыми строками; главный оценщик ABBA — кадры 10–89 блока; **уровни из разных
режимов BDA не сравниваются, режим указывать по счёту `bda_scan`, не на глаз**; **запечатанное следствие после исхода не
отменяется**. **Скорость игры = 16 667 / mean `dt_us`. 60 FPS не обещать.**

Дата: 2026-09-25. **Сессия114: РЫВОК 3 С ОБЪЯСНЁН И ВОСПРОИЗВЕДЁН — ЗАГОЛОВОК ОКНА ЖДАЛ ЗАНЯТЫЙ ГЛАВНЫЙ ПОТОК SDL ПОД
МЬЮТЕКСОМ ФЛИПА; РУЧКА `titleasync` ИЗМЕРЕНА (SHIP ПО ABBA), НО УМОЛЧАНИЕ 0 ПО ЗАПЕЧАТАННОМУ ПРАВИЛУ ПРОВЕРКИ ЗАГРУЗКИ;
НАЙДЕНО ПАДЕНИЕ СТАРТА `commandRecorder.cpp:326`.** Механизм (`stall/STALL_PATHS.md`): поток презентации держит
`VideoOutConfig::mutex` весь present и в нём ждал `SDL_SetWindowTitle` на главном потоке; GuestGpu стоит в
`ReserveFlipRequest` до подачи флипа, прерывание EOP — на неподанном тике. Контроль `ctl114` (печать 01, сон главного
потока 3 с): при 0 — заморозка 3,03 с с подписью `vbn113k`, при 1 — кадры 33 мс. ABBA `ttl114` NOT_ADMITTED (моя планка
20 мкс), `ttl114b` (планка 60 мкс, выбрана после 02 — записано): SHIP, Δ`dt` −43,5 ± 73,2 (NEW). Видео `vid114` сборки с
умолчанием 1 — PASS (4 010 кадров, 0 глитчей, OLD). Загрузка `boot114` (`KYTY_PREPARE_HOLD_MS=10000`) — падение
`commandRecorder.cpp:326`: кольцо записи планировщика презентации «принадлежит» первому записавшему потоку (`VideoOut`),
главный поток в `WindowPrepareShaders` (`PrepareBlankFrame`) падает; от ручки не зависит (печать 03b: 0 и 1 одинаково);
скрыто в тёплых стартах, виделось в с. 102. Аудит сессии: все числа CONFIRMED; **MAJOR P1** — п. 13 отменил следствие
печати 03 после исхода ⇒ соблюдено запечатанное: **умолчание 0, сборка `916f6489`**. Источник истины —
`C:/kyty/s114/FACTS.md`, в git `docs/local-session-114.md`.

"""
s = s[:a] + STATE + s[b:]

c = s.index('Дата: 2026-09-24. **Сессия110:')
d = s.index('в git `docs/local-session-110.md`.\n\n', c) + len('в git `docs/local-session-110.md`.\n\n')
s = s[:c] + s[d:]

ENV = """- Сто четырнадцатая сессия (**умолчания поведения не сдвинуты: ручка `titleasync` есть, умолчание 0**): ручка
  **`KYTY_TITLE_ASYNC`** / **`titleasync`** (0..1, умолчание 0, ПОСЛЕДНЯЯ строка ручек, читается на каждый вызов
  `UpdateTitle` — может быть плечом расписания): 1 — заголовок окна кладётся в слот под `title_mutex` и ставится главному
  потоку SDL без ожидания (`PostToMainThread`, не больше одной задачи); **только после старта главного цикла**
  (`main_loop_running`, до него — ожидающий путь; до главного цикла значение ручки не читается). Счётчики `FrameTrace-x`
  (сырые нс/штуки): `pres_title_ns`/`pres_title_n` (стена `UpdateTitle`), `flip_rsv_wait_ns`/`_n` (блокирующее ожидание
  `VideoOutConfig::mutex` в `ReserveFlipRequest`), `flip_hold_ns`/`_n` (удержание мьютекса во `FlipQueue::Flip`; строки
  `FlipHold: us= present_us= poll_us= other_us=` > 50 мс, ≤ 32), `mt_age_ns`/`mt_n` (возраст задач главного потока;
  строки `MainTaskLate: us=` > 50 мс, ≤ 32), строки `MainThreadWait: us= frame=` (ожидание главного потока > 50 мс);
  **`present_overlap`** (второй поток внутри зоны swapchain `Presenter::Present`; строки `PresentOverlap: thread=`, ≤ 8;
  **до первого флипа гостя счётчик уходит в базу — там видит только строка**; в сборке `916f6489` детектора нет).
  ТОЛЬКО ИЗМЕРЕНИЕ, раз на процесс: **`KYTY_MAIN_STALL_TEST=<кадр>:<мс>`** (сон главного потока на кадре — положительный
  контроль рывка), **`KYTY_PREPARE_HOLD_MS=<мс>`** (только в HEAD/`8d7ba8f4`: `WindowPrepareShaders` презентует экран
  подготовки не меньше N мс, строка `PrepareHold: ms=`; **сейчас роняет старт на `commandRecorder.cpp:326`** — как и
  любая долгая подготовка до исправления с. 115). `titleasync` — 44-е имя вне `gates_base.txt`. Харнесс `C:/kyty/s114`:
  `ctl114.py`, `ttl114.py`/`ttl114b.py` (+`make_*`, `test_*`, `mut_*`, `*_sealed.py`), `check114.py`, `bootctl114.py`,
  `go114a…e.sh`, `SEALS114.txt`, `audit114/`, `stall/STALL_PATHS.md`, копии сборок `kyty_emulator_{78f290d4,916f6489,
  c6892df1,8d7ba8f4}.exe`. **Ловушки:** проверка загрузки при потоке записи (`recordthread=1`) не пройдёт до исправления
  кольца; `mutlib` без `--work-dir` пишет кеш рядом с собой (в репозиторий); суммарная загрузка CPU не видит
  однопоточного чужого процесса (`find` через все прогоны 01–02b).
"""
e = s.index('- Сто тринадцатая сессия')
s = s[:e] + ENV + s[e:]

out = s.replace('\n', '\r\n') if crlf else s
for name in ('CLAUDE.md', 'AGENTS.md'):
    (DIR / name).write_bytes(out.encode('utf-8'))
print('ok', len(src), len(out), crlf)
