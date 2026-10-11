# FS14b (`HPP-813`, Red Team): ревью бинаря отгрузки FS14 `013e1974` — умолчания `KYTY_FIX_F24=1` и `KYTY_FIX_F29=1`

**Вердикт: PASS.** RC кода 0; замечаний без RC 5 (Н1–Н5, «читать так»). Бинарь FS14 `013e1974…` идёт в FS14c без изменений.

Задание — `ROADMAP.md` «СЕССИЯ 122» п. 710(г)(2) (KytyPS5 `5b774c83`, якорь «(2) **FS14b (Red Team, без замка и без игры): ревью.**»)
с поправкой п. 712(г)(2) (KytyPS5 `e4777abb`, Ф29 входит в FS14) и приёмкой FS14a п. 717 (KytyPS5 `6a3a1b62`: итоговый бинарь `013e1974`,
worktree `C:/kyty/f287/fs14a/wt` HEAD `eb7e8b91`; промежуточный `826fc0a0` в FS14 не идёт и здесь не рецензируется); вход — отчёт FS14a
`f2ef85c0:docs/track-f/fs14a.md` (издание 2). Игра не запускалась; установленный `ps5 em/kyty_emulator.exe` — FS13 `abab2196…` до и после
[c `sha_fs14b.txt`], `C:/kyty/build`, `C:/kyty/build/install` и кэши не тронуты. Замка `C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` за звено
не было (каждая команда начиналась проверкой). Шла серия Harness Engineer `HPP-800` (с 12:50Z — и `HPP-781`): каждый шаг дольше 60 с — после
строки `FS14b API check` в `C:/kyty/f287/times.txt` и под сторожем `watch_fs14b.py`, срабатываний 0. Время — UTC по `date -u`. Метки: [c] —
показано кодом или выводом, [I] — вывод, [U] — неизвестно. Ссылок `<коммит>:<путь>:<строка>` отчёт не несёт (места названы по функциям и файлам).

**Ход.** Worktree `C:/kyty/f287/fs14b/wt` от `eb7e8b91` 12:40Z (подмодули архивом, `git status` 0 строк, CR в `src/` 0 из 460 [c `mk_wt.log`]);
configure 12:41:20–12:43:04Z, `kyty_emulator` 12:43:16–12:44:42Z, `f29_fault_stand` 12:44:53–12:45:28Z; комментарий с константами стенда
(`b141f325`) до данных; стенд 12:50:32–12:51:09Z.

## Члены п. 710(г)(2) с п. 712(г)(2)

| Член | Итог | Источник |
|---|---|---|
| Путь `KYTY_FIX_F24=0` на FS14 по коду = база FS13 | ✓ (§ «Код», F24) | `review_git.out.txt` R1, R6; дифф файлов F40 |
| Путь `KYTY_FIX_F29=0` на FS14 по коду = база FS13 | ✓ (§ «Код», F29) | дифф `faultManager.cpp` |
| Путь по умолчанию = путь `=1` бинаря тега F40a2 `ddf0ca91`: дифф `src/` FS14 против worktree F40a2 `7c38e497` — только FS13, FS14a и (п. 712) `faultManager.cpp`/`.h` | ✓ 5 путей: `src/kernel/fileSystem.cpp` = дифф FS12 → FS13; `joyPump.cpp`/`.h` = дифф коммита FS14a `76c1058f`; `faultManager.cpp`/`.h` = дифф `15c9d2f2` + `78e45af3`; остальные файлы F40 — тот же blob; файлы F40 в `7c38e497` = `6eb0f1a1`; отрицательный контроль — дифф от базы ≠ | R2 |
| Путь по умолчанию = путь `=1` бинаря тега F44a `d760708d`: дифф `src/` FS14 против worktree F44a `e148f54c` — только FS13, F40 и FS14a | ✓ 9 путей: `faultManager.cpp`/`.h` = дифф только `78e45af3` (`c5eb48b0` → `eb7e8b91`); файлы F40 = дифф `ea6c6e9e` → `76c1058f`; `fileSystem.cpp` = дифф FS13; `faultManager` в `e148f54c` = blob `15c9d2f2` | R2b |
| Дифф FS14 против базы FS13 — только п. 710(г)(1) с п. 712(г)(1) | ✓ 12 путей: `src/` — 6 файлов F40 и `faultManager.cpp`/`.h`; вне `src/` — `CMakeLists.txt` (+6/−0, только цель `f29_fault_stand`, = CMake-дифф `15c9d2f2`), `tests/F29FaultStand.cpp`, 2 пути `docs/track-f/f44a/` (Н4); цепочка шести коммитов — родители точно, patch-id каждого = своему оригиналу в `main` (`5c21c387`, `e3aa4b4d`, `57f9e528`, `c8836f14`, `15c9d2f2`, `78e45af3`) | R1 |
| Ф25, Ф21, Б12, Ф27, Б13, Б33, Ф10, Ф16, Ф19, Б42, Б4, Ф8, Б24, S-replay, P-var не тронуты | ✓ каждый файл `src/` базы, называющий ручку строки, — тот же blob в FS14, кроме `vulkanWindow.cpp` (Ф16) и `controller.cpp` (Б24) — файлов F40; в изменённых строках файлов F40 и F29 имён других ручек и символов `Fix<X>` 0 (член фильтра с фикстурами); Б24: `PadOutput`, `g_pad_output` и `FixB24On` по коду прежние — дифф `controller.cpp` трогает только `delete g_controller` (под `JoyPump::Exited()`) и остановку `JoyPump` в начале `EmergencyShutdown` (под `JoyPump::Enabled()`); строки с `B24`/`PadOutput` в диффе — 2 комментария и строка `FixF24: mode= b24=` | R4 |
| Своя сборка из чистого worktree и sha | sha256 своей сборки `3be12425…` ≠ `013e1974…`; причина названа (Н1): `pediff3r` — 1 817 байт, все объяснены (`(1)` имя папки сборки 139, `(2)` тег анонимного пространства имён 1 666, `(3)` штамп/GUID 12), **`.text` 0**, `VERDICT EXPLAINED`; стенд `a5fa43b3…` против стенда FS14a `12c4b09f…` — `.text` 0, `EXPLAINED`; отрицательный контроль: своя сборка против FS13 `abab2196` — сравнение отказывает (`AssertionError`, размеры). Строка версии `KytyPS5-2026-09-15-6a2987a-1925-geb7e8b91` | `pediff3r_emu.out.txt`, `pediff3r_stand.out.txt`, `pediff3r_neg.out.txt`, R5 |
| Таблица умолчаний | ✓ своим сканером (`knobs_fs14b.py`, порт моего FS13b): ON-IF-UNSET на `eb7e8b91` — 20 = 18 FS13b + `KYTY_FIX_F24` + `KYTY_FIX_F29`, `missing [] extra []`; отрицательные контроли: `ea6c6e9e` — `missing ['KYTY_FIX_F24', 'KYTY_FIX_F29']`, `76c1058f` и `c5eb48b0` — `missing ['KYTY_FIX_F29']`; UNDECIDED — те же 6, что у FS13 (`KYTY_S_REPLAY` в их числе: blob `shaderReplay.cpp` = базе по R4, умолчание 3) | `knobs_*.out.txt` |
| «Содержит» `15c9d2f2`, `78e45af3`, `5c21c387`, `57f9e528`, `c8836f14`, `e9dd8604`, `3630f116`, `227e1b36`, `cbfe8375`, `c94c49e0`, `726e751e`, `cb022252` | ✓ 12 из 12 `git cherry` `-` (форма `git cherry <FS14> <c> <c>^`); контроли: пять новых коммитов в базе FS13 — `+`, `15c9d2f2`/`78e45af3` в `76c1058f` — `+`, Ф20 `a6342c98` в FS14 — `+`, положительный `e3aa4b4d` в FS14 — `-` | R3 |
| Подпись трансляции | ✓ `KYTY_SHADER_SOURCE_HASH` своей сборки `9177b4267de1fb8bac7d1113afd8733210addfac` = FS13 (1 вхождение в своём exe, в `013e1974` и в `abab2196`); путей `src/graphics/shader/` в диффе 0 | R5, `strings.out.txt` |
| Строки формата в бинаре | ✓ свой exe и `013e1974`: `FixF29: mode=` 1, `FixF24: init_owner` 1, `TestHidLoss: f24` 1, `FixF24: mode=` 1, `FixF25: mode=` 1, `FixF21: mode=` 1, `FixF20` 0; FS13 — первые четыре 0 | `strings.out.txt` |
| Свой прогон стенда `f29_fault_stand` без переменной, `R` ≥ 20, члены P1 | ✓ § «Стенд» | `runs/`, `recount.out.txt` |

`review_git_fs14b.py` — `ALL OK` (издание 2, зачётное; издание 1 — тоже `ALL OK`, но печатало 25 строк «имя ручки вне F24/F29» справкой — Н2).

## Код

**F24 (файлы F40 + `76c1058f`).** Прочитан дифф базы FS13 → FS14 по `window.cpp` (вне стенда), `hostInput.cpp`, `vulkanWindow.cpp`,
`controller.cpp`, `joyPump.*`. При `=0` (`0/false/off/no`): `JoyPump::ReadKnob` в `WindowCreate` читает ручку и печатает
`FixF24: mode=0 b24=<…>`; `JoyPump::Enabled()` ложно — `WindowCreate` идёт веткой `else if (SDL_InitSubSystem(SDL_INIT_VIDEO |
SDL_INIT_GAMECONTROLLER) < 0)` (строка базы), `GameEventController` — `else if (f.added)` с `SDL_GameControllerOpen` и `SDL_GameControllerClose`
базы, `HostInputWaitEvent` — тело базы, `~WindowContext` — `SDL_QuitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER)` базы,
`EmergencyShutdown` — без `Stop`; `Shutdown` — `JoyPump::Exited()` истинно (`!m_started`) ⇒ `delete g_controller` как в базе. Хуки стенда
(`TestHidLossIntercept`, `TestHidLossTitleOff`) при выключенном стенде — одна relaxed-загрузка и `false`. Итог [c кода]: при `=0`
исполняемая разница с FS13 — строка `FixF24: mode=0`, создание объекта `Pump` конструктором по умолчанию в `Shutdown` (Н3) и две загрузки
флагов стенда — как в F40b. По умолчанию (не задана или `""`) = путь `=1` F40a2: коммит `76c1058f` меняет только выражение
`g_enabled.store(value == nullptr || value[0] == '\0' || Common::EnvValueOn(value), …)` (было `Common::EnvFlagOn`) и комментарии; одно
чтение на процесс (`done.exchange`) сохранено. Порядок: все вызовы `JoyPump::Enabled()` вне стенда — после `ReadKnob` в `WindowCreate`
(обработка событий, ожидание события, деструктор окна) либо в `EmergencyShutdown`, где до `WindowCreate` `JoyPump` не запущен и `false`
согласовано — смена умолчания порядка не меняет: тот же код исполнялся при явном `=1` в тегах F40c.

**F29 (`faultManager.cpp`/`.h`, `15c9d2f2` + `78e45af3`).** При `=0` `ParseFaultArea(faults, false, …)`: `count = raw`, цикл
`1 … count` с теми же `fault_ranges.Add` и `LOGF("Accessed non-GPU cached memory …")` в том же порядке; строки `overflow` только при
`clamp`; `fix_pass = 0`, счётчик прохода не растёт. Итог [c кода]: при `=0` исполняемая разница с FS13 — строка `FixF29: mode=0` в
конструкторе `FaultManager` и вызов посетителя через `std::function` вместо тела цикла (Н5). По умолчанию = путь `=1` F44a: коммит
`78e45af3` меняет только инициализацию `static const bool enabled` (лямбда в форме FS13a `3630f116`) и комментарий заголовка; первое
чтение — конструктор `FaultManager`, потокобезопасная инициализация статической переменной C++11. Тело F44a — без изменений (R2b), его
ревью — F44b `PASS`.

## Стенд `f29_fault_stand` (своя сборка)

Стенд `C:/kyty/f287/fs14b/build/f29_fault_stand.exe` (sha256 `a5fa43b3…`) из worktree FS14 `eb7e8b91`; драйвер `run_stand_fs14b.py` — копия
`run_stand_fs14a.py` с одной правкой: из окружения обоих процессов сняты все `KYTY_*` (печать `KYTY_* removed: []` — в моём окружении их не
было), затем у процесса контроля `KYTY_FIX_F29=0`. Зерно 813001, `R` = 20, порядок процессов `=0` → без переменной — комментарием `b141f325`
до данных.

| Процесс | Ридер FS14a (`run_stand_fs14b.py read`) | Мой пересчёт `recount_fs14b.py` |
|---|---|---|
| без переменной `KYTY_FIX_F29` | stdout `FIXF29 env=(unset) on=1`, `DONE rows=160`; нулевые инварианты 0 из 800, тождества 0 из 960 нарушены, G1 220, G2 140, **P1 PASS 640 из 640**, строки `FixF29: overflow` 32 (= min(32, 100)) | `out_area` = `out_buf` = `cls_low` = `cls_exit` = 0 в 160 из 160; `read` = 1 023 у E1, O1, O7, D1, L — 100 строк; `extra` = `dup` = `map_left` = 0; 8 плеч × 20, `fix` = 1, зерно верно |
| контроль `KYTY_FIX_F29=0` | stdout `FIXF29 env=0 on=0`; **P0 PASS** (O1 77, O7 буфер 77, E1 1, L ≥ 1), строк `FixF29:` 0 | O1 `out_area` 77 — 20 из 20, O7 `out_buf` 77 — 20 из 20 |

Ридер — `ALL OK` (включая H: `h_inproc` у E1, O1, D1 при `=1`); пересчёт — `RECOUNT ALL OK`; отрицательный контроль пересчёта — файлы
процессов местами — `RECOUNT NOT OK` (8 членов `FAIL`) [c `recount_neg.out.txt`]. Стенд своей сборки отличается от стенда FS14a только вне
`.text` — прогон относится к коду FS14 [I по `pediff3r`]. Член п. 712(г)(1) «строка `FixF29: mode=1`» стендом не печатается (её печатает
только конструктор `FaultManager`, п. 717(б)) — свидетель стенда `FIXF29 env=(unset) on=1` той же `FixF29Enabled`; строка в логе игры —
член FS14c (п. 712(г)(3)).

## Замечания без RC (читать так)

- **Н1.** Своя сборка не равна FS14a по sha (`3be12425…` ≠ `013e1974…`); равенство показано по классам байт с `.text` 0, не байт в байт
  (форма п. 693(а)). Тесты `shader_cfg_tests` и `check_gate_order.py` своей сборкой не повторял — члены FS14a, не FS14b.
- **Н2.** Моя ошибка инструмента: фильтр R4 издания 1 считал «чужими» имена `FixF29Enabled`, `FixF29OverflowLines`, `KYTY_PLATFORM`,
  `KYTY_CLASS_NO_COPY` и защиту заголовка `joyPump.h` (25 строк справкой, все — свои символы F24/F29 и макросы платформы, проверено глазом);
  издание 2 делает фильтр членом с 6 фикстурами (3 отвергаются — `FixF25Enabled`, `KYTY_FIX_B24X`, `KYTY_S_REPLAY`; 3 проходят) — 0 строк.
  Строка `times.txt` 12:52:14Z «review_git ed.2 2ad78545» — повтор издания 1 (правка heredoc не применилась), sha = первому прогону.
- **Н3.** При `=0` `Shutdown` впервые вызывает `JoyPump::P()` — создаётся `Pump` конструктором по умолчанию (атомики и пустые контейнеры,
  без потока), объект не разрушается до конца процесса. Поведенческой разницы нет; то же — у бинаря тега F40a2 при `=0` (F40b).
- **Н4.** В дереве FS14 против базы 2 пути `docs/track-f/f44a/` (перенесены cherry-pick `15c9d2f2`) — в сборку не входят; член «дифф только
  (1)» читается как «вне `tests/`, `docs/` и цели CMake стенда — только файлы F40 и `faultManager.cpp`/`.h`».
- **Н5.** Цикл разбора и при `=0`, и в базе идёт `uint32_t index <= count`; при `raw` = `0xFFFFFFFF` он не кончается (переполнение
  `index`) — так же в FS13, не регресс; при умолчании `count` ≤ 1 023. Вызов посетителя через `std::function` — цена на запись [I], не член.

## Не заявляется

П. 710(з) и п. 712(з) целиком — в частности: что Ф24 или Ф29 случаются у пользователя и с какой частотой; что настоящий пульт хоста на
`JoyPump` работает (пультов хоста ни в тегах, ни здесь нет); что правка возвращает ввод пульта в окне блокировки; что проход с ≥ 1 024
битами бывает в игре; что умолчания безвредны на пути по умолчанию в игре (FS14c); что FS14 установлен (FS14d); что прочие `SCENE_OK`
держатся на FS14; ни одно число — не выигрыш. Ревью не проверяет FS14 игрой.

## Файлы

`C:/kyty/f287/fs14b/`, копии в `docs/track-f/fs14b/` (текстовые — LF): `review_git_fs14b.py` + `review_git.out.txt` (издание 2) и
`review_git_ed1.out.txt`; `knobs_fs14b.py` + 4 вывода; `pediff3.py`, `pediff3r_fs14b.py` + 3 вывода; `run_stand_fs14b.py`,
`recount_fs14b.py` + `recount.out.txt`, `recount_neg.out.txt`; `runs/` (`log_stand.txt`, `stand_f29/` — TSV, логи стенда, stdout);
`strings.out.txt`; `sha_fs14b.txt`; `window_diff.txt`; скрипты сборки и сторожа (`mk_wt_fs14b.sh`, `build_fs14b.cmd`, `bstep.sh`, `sstep.sh`,
`api_chk.sh`, `watch_fs14b.py`); логи `mk_wt.log`, `build_cfg.log`, `build_ver.log`, `build_emu.log`, `build_stand.log`; `facts_fs14b.py` +
шаблон.
