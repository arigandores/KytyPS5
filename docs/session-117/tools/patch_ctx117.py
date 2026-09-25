"""Session 117 close: FACTS glitch; game-folder CLAUDE.md (= AGENTS.md) state, s117 entry (drop s113), env note; HANDOFF."""
from pathlib import Path

f = Path('C:/kyty/s117/FACTS.md')
t = f.read_bytes().decode('utf-8')
old = "there was no `spine=0` arm);  **Not proved:** the carry"
assert t.count(old) == 1
t = t.replace(old, "there was no `spine=0` arm); the carry")
f.write_bytes(t.encode('utf-8'))
Path('C:/kyty/KytyPS5/docs/local-session-117.md').write_bytes(t.encode('utf-8'))

ROOT = Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')
C = ROOT / 'CLAUDE.md'
raw = C.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')

a = s.index('**СОСТОЯНИЕ (2026-09-25, ночь): ЦИКЛ СЕССИЙ ИДЁТ**')
b = s.index('Дата: 2026-09-25. **Сессия116:')
STATE = """**СОСТОЯНИЕ (2026-09-25, поздний вечер): ЦИКЛ СЕССИЙ ИДЁТ** (пользователь, /loop: сессии подряд, вопросов не задавать;
игру запускать можно; push — нет). **Сессия 117 закрыта** (аудит: числа подтверждены; MAJOR — цена спайна 0,61 мс лишь
нижняя граница, п. 7 «машина простаивала» ложно, п. 3 неверно процитировал запись — микротреки GuestGpu НЕ закрыты,
«спайн не меняет исполнение» ложно при `spine` 1/2), следующая — `docs/next-session-118.md`: ОДНА сборка и ОДИН
запечатанный прогон — безопасный план спайна, часть 2 этапа 4 маршрута A (K3 гистограмма проходов, K4 пересечение образов,
перенос состояния между подачами) и отдельным плечом перемер кандидатов-микротреков (проверка свидетеля, резолюция,
части `mh_emit`). Установлена сборка **`d3a981a2…`** (`7c73f26`), закреплённая копия `C:/kyty/s117/kyty_emulator_d3a981a2.exe`;
сборка со спайном — `C:/kyty/s117/kyty_emulator_3cde1af8.exe` (ручка `spine` по умолчанию 0). **Мутанты — `mutlib` v4.1
(`docs/session-116/mutlib_v41/mutlib.py`, `db82ef4b`), только ПОЛНЫЕ прогоны `--control --no-memo --work-dir/--cache-dir
C:/kyty/s1NN/...`; одна большая ABBA-печать ≈ 42 мин; `--changed-from` запрещён.** Правила с. 106–117: решение до действия
(и любое изменение воркфлоу), запечатанное следствие не отменяется, фикстуры на каждый член/край, якоря целыми строками,
**скрипты правок пишут LF (`write_bytes`), наборы фикстур заканчиваются строкой `ALL OK`**, окно оценщика ABBA — кадры
10–88, режим BDA — по `bda_scan`, трек скорости — только при потолке ≥ 1 мс; **инструменты ТОЛЬКО ИЗМЕРЕНИЯ — пакетом в
одну сборку/прогон; мутанты и сборки могут идти внахлёст, эксклюзивен только запечатанный прогон и замеры времени**;
замок `C:/kyty/SEALED_RUN.lock`, шлюз `procload.py` (отказ, пока жив `mutlib.py`); состояние цикла — `C:/kyty/LOOP_STATE.md`.
**Скорость игры = 16 667 / mean `dt_us`. 60 FPS не обещать.**

Дата: 2026-09-25. **Сессия117: ТРЕКИ ЗАМКОВ ЗАКРЫТЫ (ВОПРОС ПОЛЬЗОВАТЕЛЯ); МАРШРУТ A, ЭТАП 4, ЧАСТЬ 1 — ТЕНЕВОЙ СПАЙН
ПОСТРОЕН И ПРОШЁЛ ПЕЧАТЬ `spn117` (K5 PASS: 0 РАСХОЖДЕНИЙ НА 19,1 МЛН СВЕРОК; K1 PASS: 608 МКС НА КАДР ПО СОБСТВЕННОМУ
ТАЙМЕРУ); ПОЛНЫЙ `mutlib` v4.1 — 42 МИН НА ПЕЧАТЬ; СКОРОСТЬ НЕ ОТГРУЖЕНА.** Ручка **`spine`** (`KYTY_SPINE`, 0..2, 0,
ИЗМЕРЕНИЕ): второй `CommandProcessor`, засеянный в начале подачи, проходит её настоящими обработчиками регистров; режим 2
снимает состояние (4 096 Б) перед каждым draw/dispatch и сверяет с настоящим (memcmp, затем `operator== = default`,
добавленный 61 типу `hardwareContext.h` — вне подписи кэша трансляции). Три незапечатанных дыма нашли два дефекта
спайна (запись `wave_size` диспатчем, сброс `R_DISPATCH_RESET`). Печать перевыпущена дважды до прогона (CRLF; строка
`ALL OK`). Аудит: пересчёт CONFIRMED; цена на уровне кадра не измерена (контроль: таймеры недосчитывают ~0,55 мс);
кандидаты ≥ 1 мс на GuestGpu остаются (свидетель ~1,03 мс в с. 89, резолюция ~2,6 мс, части `mh_emit`). Источник
истины — `C:/kyty/s117/FACTS.md`, в git `docs/local-session-117.md`.

"""
s = s[:a] + STATE + s[b:]
a = s.index('Дата: 2026-09-24. **Сессия113:')
b = s.index('**РЕШЕНИЯ ПОЛЬЗОВАТЕЛЯ ПОСЛЕ СЕССИИ 101')
s = s[:a] + s[b:]
ANCHOR = '- Сто шестнадцатая сессия (**кода эмулятора нет, умолчания не сдвинуты**)'
assert s.count(ANCHOR) == 1
ENV = """- Сто семнадцатая сессия (**умолчания поведения не сдвинуты; новая ручка — ТОЛЬКО ИЗМЕРЕНИЕ**): **`KYTY_SPINE`** /
  **`spine`** (0..2, умолчание 0, ПОСЛЕДНЯЯ строка ручек, читается раз на подачу и защёлкивается в `Pm4Execution` — может
  быть плечом расписания): 1 — теневой план каждой подачи на GuestGpu (второй `CommandProcessor` настоящими обработчиками
  регистров: `SET_*_REG*`, `*_INDIRECT`, `CLEAR_STATE`, `SET_BASE`, `INDEX_*`, `NUM_INSTANCES`, `R_CONTEXT_STATE`,
  `R_DISPATCH_RESET`, маркеры пользовательских данных; IB, `COND_EXEC`, 14-словное ветвление и предикация вычисляются
  спайном; после снимка диспатча повторяется `SetCsWaveSize(mode)`); 2 — плюс снимок (4 096 Б) перед каждым элементом и
  сверка с настоящим перед обработчиком (memcmp, затем `operator==`). Строки `Spine: mode= snap= ctx= ucfg= sh=` (раз),
  `SpineMismatch: sub= el= op= parts= reg=`, `SpineMisalign: sub= planned= executed=`, `SpineAbort:` (≤ 40 каждая).
  Счётчики `FrameTrace-x` (сырые нс/штуки): `spine_n`, `spine_ns` (стена плана без снимков), `spine_pk`, `spine_el`,
  `spine_ib`, `spine_cf_br`, `spine_cf_cond`, `spine_cf_pred`, `spine_cf_predw`, `spine_cf_ind`, `spine_abort`, `spine_cmp`,
  `spine_bad`, `spine_misal` (число элементов ≠ плану), `spine_pad` (различие только в паддинге), `spine_lost` (снимки
  заменены другим планом того же процессора), `spine_chk_ns`. **Ловушка (аудит 117): при `spine` 1/2 план читает память
  гостя заранее и может дойти до `EXIT` обработчика там, где настоящий процессор не дошёл бы** — до части 2 нужен
  безопасный план. `hardwareContext.h`: у всех 61 типа `operator== = default` (для сверки; в подпись кэша не входит).
  Харнесс `C:/kyty/s117`: `spn117.py` (+`test_*` 101 фикстура, `mut_*` 104), `go117a.sh`, `SEALS117.txt` (печати 01, 01r —
  «superseded, never run», 01r2 — запущена), `pred/01_spn117.md`, `audit117/`, `old/smokes/` (три дыма), копии сборок
  `kyty_emulator_{d3a981a2,3cde1af8}.exe`. **Ловушки:** `Path.write_text` на Windows пишет CRLF — `mutlib` не находит
  многострочные якоря; `mutlib` требует от набора строку `ALL OK`; `clang-cl` 19.1.5 не знает `__builtin_clear_padding`.
"""
s = s.replace(ANCHOR, ENV + ANCHOR)
out = s.replace('\n', '\r\n') if crlf else s
C.write_bytes(out.encode('utf-8'))
(ROOT / 'AGENTS.md').write_bytes(out.encode('utf-8'))

H = ROOT / 'HANDOFF.md'
hraw = H.read_bytes().decode('utf-8')
hcrlf = '\r\n' in hraw
h = hraw.replace('\r\n', '\n').rstrip('\n') + '\n'
h += """
Дата: 2026-09-25. **Сессия 117 (кратко; источник истины — `docs/local-session-117.md`).** Треки замков закрыты (вопрос пользователя); полный `mutlib` v4.1 без кэша — 42,1 мин на большую печать. Маршрут A (параллельная обработка потока команд), этап 4, часть 1: ручка `spine` (ИЗМЕРЕНИЕ) — теневой второй `CommandProcessor`; печать `spn117` ADMITTED, K5 PASS (0 расхождений на 19,1 млн сверок), K1 PASS (608 мкс на кадр по собственному таймеру — нижняя граница) ⇒ часть 2. Аудит вернул в игру кандидатов-микротреков (свидетель ~1,03 мс, резолюция ~2,6 мс, части `mh_emit`). Установлена `d3a981a2`. Далее — `docs/next-session-118.md`.
"""
H.write_bytes((h.replace('\n', '\r\n') if hcrlf else h).encode('utf-8'))
print('ok')
