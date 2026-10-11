# FS15b (`HPP-821`, Red Team): ревью бинаря отгрузки FS15 `bfac84be` — умолчание `KYTY_FIX_F20=1`

**Вердикт: PASS.** RC кода 0; замечаний без RC 6 (Н1–Н6, «читать так»). Бинарь FS15 `bfac84be…` идёт в FS15c без изменений.

Задание — `ROADMAP.md` «СЕССИЯ 122» п. 730(г)(2) (KytyPS5 `2e71aad4`, якорь «(2) **FS15b (Red Team, без замка и без игры): ревью.**»)
с приёмкой FS15a п. 732 (KytyPS5 `e3403a2a`: бинарь `bfac84be`, worktree `C:/kyty/f287/fs15a/wt` HEAD `6beb3b73`); вход — отчёт FS15a
`35e66157:docs/track-f/fs15a.md`. Первая команда звена — 18:19:44Z, после коммита `e3403a2a` (18:19:09Z). Игра не запускалась; установленный
`ps5 em/kyty_emulator.exe` — FS14 `013e1974…` [c `sha_fs15b.txt`], `C:/kyty/build`, `C:/kyty/build/install` и кэши не тронуты. Замка
`C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` за звено не было (каждая команда начиналась проверкой). Шла серия Harness Engineer `HPP-809`
(`in_progress`, `executionRunId` есть): каждый шаг дольше 60 с — после строки `FS15b API check` в `C:/kyty/f287/times.txt` и под сторожем
`watch_fs15b.py`, срабатываний 0. Время — UTC по `date -u`. Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно. Ссылок
`<коммит>:<путь>:<строка>` отчёт не несёт (места названы по функциям и файлам).

**Ход.** Worktree `C:/kyty/f287/fs15b/wt` от `6beb3b73` 18:20:50Z (подмодули архивом, `git status` 0 строк, CR в `src/` 0 из 462 [c `mk_wt.log`]);
configure 18:20:55–18:22:21Z, версия 18:22:26–18:22:33Z, `kyty_emulator` 18:22:40–18:24:08Z (флаги = FS14b / FS15a: Release, clang-cl, LTO).

## Члены п. 730(г)(2)

| Член | Итог | Источник |
|---|---|---|
| Путь `KYTY_FIX_F20=0` на FS15 по коду = база FS14 | ✓ (§ «Код») | `review_git.out.txt` R7; дифф F42 |
| Путь по умолчанию = путь `=1` бинаря тега F42a2 `1994a0ce`: дифф `src/` FS15 против worktree F42a2 `5ccb1d31` — только коммиты FS13, FS14 и FS15a | ✓ 11 путей = 9 путей `src/` диффа FS12 `730ed40a` → FS14 `eb7e8b91` (`fileSystem.cpp` — FS13; `hostInput.cpp`, `joyPump.*`, `vulkanWindow.cpp`, `window.cpp`, `controller.cpp` — Ф24; `faultManager.*` — Ф29) + `fixF20.cpp`/`.h`; по каждому из 9 путей дифф = диффу `730ed40a` → `eb7e8b91` (11 коммитов FS13/FS14, список в выводе); дифф `fixF20.*` = коммиту `38fc76c1` в `main`; пути FS13/FS14 файлов F42 не касаются; прочие 4 файла F42 — тот же blob; файлы F42 в `5ccb1d31` = промежуточному `91b74d09` (FS15 без FS15a); цепочка F42a2 `23ff0c41` / `adcd0eba` / `5ccb1d31` от `730ed40a` — patch-id = `a6342c98` / `a9d6fd1c` / `82570fd2`; файлы `tests/` — тот же blob (`bb11259d`, `9c5eeb61`); отрицательный контроль — дифф от базы ≠ | R2 |
| Дифф FS15 против базы FS14 — только п. 730(г)(1) | ✓ 8 путей: `src/` — 6 файлов (`emulator.cpp`, `fixF20.cpp`/`.h`, `pipelineCache.cpp`/`.h`, `shaders.cpp`) = объединению путей `src/` четырёх коммитов; вне `src/` — `tests/ShaderRecompilerComputeTests.cpp`, `tests/shaderCfgTests.cpp` (стенд, в `kyty_emulator` не входят; `CMakeLists.txt` не тронут); цепочка `b1179dab` → `95e39a17` → `91b74d09` → `6beb3b73` от `eb7e8b91` — родители точно, patch-id = `a6342c98`, `a9d6fd1c`, `82570fd2`, `38fc76c1` | R1 |
| Ф24, Ф29, Ф25, Ф21, Б12, Ф27, Б13, Б33, Ф10, Ф16, Ф19, Б42, Б4, Ф8, Б24, S-replay, P-var не тронуты | ✓ каждый файл `src/` базы, называющий ручку строки (17 строк, в каждой ≥ 1 файл), — тот же blob в FS15, кроме файлов F42; `faultManager.cpp`/`.h` (Ф29, `ParseFaultArea`) — тот же blob; в изменённых строках 6 файлов F42 имён других ручек и символов `Fix<X>` 0 (фильтр — член с 6 фикстурами: 3 отвергаются, 3 проходят); `KYTY_DMA_LAYOUT`, `KYTY_PIPELINE_SALT` — только в 2 строках комментариев (член) | R4 |
| Своя сборка из чистого worktree и sha | sha256 своей сборки `95da43fa…` ≠ `bfac84be…`; причина названа (Н1): `pediff3r` — 2 505 байт, все объяснены (`(1)` имя папки сборки 139, `(2)` тег анонимного пространства имён 1 835, `(3)` штамп/GUID 12, `(2b)` строки анонимного пространства имён в `.data` 519), **`.text` 0**, `VERDICT EXPLAINED`; отрицательный контроль: своя сборка против FS14 `013e1974` — сравнение отказывает (`AssertionError`, размеры). Строка версии `KytyPS5-2026-09-15-6a2987a-1929-g6beb3b73` | `pediff3r_emu.out.txt`, `pediff3r_neg.out.txt`, R5 |
| Таблица умолчаний | ✓ своим сканером (`knobs_fs15b.py`, порт моего FS14b): ON-IF-UNSET на `6beb3b73` — 21 = 20 FS14b + `KYTY_FIX_F20`, `missing [] extra []`; отрицательные контроли: `91b74d09` (без FS15a) и `eb7e8b91` — `missing ['KYTY_FIX_F20']`; UNDECIDED — те же 6, что у FS14 (`KYTY_S_REPLAY` в их числе: blob `shaderReplay.cpp` = базе по R4, умолчание 3) | `knobs_*.out.txt` |
| «Содержит» `a6342c98`, `82570fd2`, `38fc76c1`, `5c21c387`, `57f9e528`, `c8836f14`, `15c9d2f2`, `78e45af3`, `e9dd8604`, `3630f116`, `227e1b36`, `cbfe8375`, `c94c49e0`, `726e751e`, `cb022252` | ✓ 15 из 15 `git cherry` `-` (форма `git cherry <FS15> <c> <c>^`); контроли «нет» (`+`): `a6342c98`, `82570fd2`, `38fc76c1` в базе `eb7e8b91`; `38fc76c1` в `91b74d09` и в `5ccb1d31`; `5c21c387` в `5ccb1d31`; `1398d44d` (F46a) в FS15; «да»: `a9d6fd1c` в FS15 — `-` | R3 |
| Подпись трансляции | ✓ `KYTY_SHADER_SOURCE_HASH` своей сборки `9177b4267de1fb8bac7d1113afd8733210addfac` = FS15a `kytyGitVersion_fs15.h` = FS14 (1 вхождение в своём exe, в `bfac84be` и в `013e1974`); путей `src/graphics/shader/` 0 | R5, `strings.out.txt` |
| Строки формата в бинаре | ✓ свой exe и `bfac84be`: `FixF20: mode=` 1, `FixF20Stat:` 1, `KYTY_FIX_F20` 1, `FixF24: mode=`, `FixF24: init_owner`, `FixF29: mode=`, `FixF25: mode=`, `FixF21: mode=`, `FixB12Stat:` по 1; `KYTY_FIX_F26`, `KYTY_DIAG_B32`, `KYTY_TEST_F20`, `F20Stand` 0; FS14 — `FixF20…` 0 | `strings.out.txt` |
| `check_gate_order.py` (справка, член FS15a) | ✓ `GATE ORDER: clean` на своём worktree, вывод без строки заголовка = FS15a (с точностью до CR) | `gate_order_wt.out.txt` |

`review_git_fs15b.py` — `ALL OK` (издание 1, зачётное).

## Код

**Путь `=0`.** Прочитан дифф базы FS14 → FS15 по `emulator.cpp`, `pipelineCache.cpp`/`.h`, `shaders.cpp`, `fixF20.*`. `FixF20::Mode()` при
`0/false/off/no` — 0 (`EnvValueOn` из `common/envFlag.h`). Оба вызова `FixF20::Apply` вне `fixF20.*` (`CreateCachedModule`, вариант dual-source
`CreateDualSourceVariant`) стоят в выражении `FixF20::Mode() == 1 && FixF20::Apply(…)` — при 0 `Apply` не вызывается, модуль создаётся из
`translation` / `words` как в базе (соль `KYTY_PIPELINE_SALT` и `CompileSPV` — тело базы); `PrintExitStat` печатает только под `if (Mode() == 1)`;
`PrintStat("periodic")` — только внутри `Apply` [c R7]. Итог [c кода]: при `=0` исполняемая разница с FS14 — строка `FixF20: mode=0` (конструктор
`PipelineCache`), вычисление `FixF20Bound` (просмотр дескрипторов раскладки) в трёх местах `ProgramCache`, поле `fault_bound` в `ShaderProgram` и
пустой вызов `PrintExitStat` перед `quick_exit` (Н3). `ShaderProgram` не участвует ни в хэше, ни в сравнении (`memcmp`, `operator==`) [c поиска
по `src/`] — новое поле ключей пайплайнов не меняет. Сохраняемая трансляция (`.spirv` записи кэша) — исходная, не переписанная: откат `=0`
каталогов не портит [c `ProgramCache`, Н6].

**Путь по умолчанию.** Коммит `38fc76c1` меняет только выражение чтения: было `Common::EnvFlagOn("KYTY_FIX_F20") ? 1 : 0` (не задана — 0), стало
`(env == nullptr || env[0] == '\0' || Common::EnvValueOn(env)) ? 1 : 0` (форма `c8836f14` / `3630f116`); комментарии заголовка. Одно чтение на
процесс сохранено (`static const` лямбды, потокобезопасная инициализация C++11). При не заданной переменной путь = путь `=1` F42a2: остальной
код F42 в FS15 — тот же blob, что в worktree F42a2 (R2), а тег F42c шёл при `KYTY_FIX_F20=1` (`EnvValueOn("1")` — истина в обеих формах).

**Полнота мест создания модуля (повтор F42b своим поиском).** Вызовы `CompileSPV` / `createShaderModule` в `src/` вне `src/graphics/shader/`:
`CreateCachedModule` (3 места `ProgramCache`) и вариант dual-source — переписываются; остальные — встроенные SPIR-V эмулятора (`faultManager`,
`blitHelper`, `tiler`, `indirectArgsSanitizer`) и синтетические TCS/TES режима rect-list (`BuildRectListShaders` в `shaders.cpp`) — не перевод
гостя, `fault_buffer` не несут [I по коду] (Н5).

## Замечания без RC (читать так)

- **Н1.** Своя сборка не равна FS15a по sha (`95da43fa…` ≠ `bfac84be…`); равенство показано по классам байт с `.text` 0, не байт в байт (форма
  п. 693(а)). Класс `(2b)` (519 байт строк анонимного пространства имён в `.data`) — мой класс FS8b, у FS14b он не понадобился; новые символы
  анонимного пространства имён F42 (`FixF20Bound`, счётчики `fixF20.cpp`) [I].
- **Н2.** `shader_cfg_tests` своей сборкой не повторял — член FS15a, не FS15b; `check_gate_order.py` повторил (справка, clean).
- **Н3.** При `=0` FS15 не байт в байт FS14 по исполнению: `FixF20Bound` в трёх местах, поле `fault_bound`, строка `FixF20: mode=0`, пустой
  вызов `PrintExitStat`; поведенческой разницы нет [c кода]. То же — у бинаря тега F42a2 при `=0` (F42b). `CreateCachedModule` вынесен из
  анонимного пространства имён (внешняя связь) — тело прежнее.
- **Н4.** Стенд Ф20 (`shader_recompiler_compute_tests --f20-stand`) я не собирал и не запускал — членом FS15b он не назван; его код в FS15 —
  тот же blob, что в worktree F42a2 (R2), прогоны — F42a2 / F42b2.
- **Н5.** Полнота мест — по моему поиску вызовов создания модуля; что синтетические TCS/TES и встроенные SPIR-V не несут привязку
  `FaultBuffer` — [I по коду], не проверено разбором SPIR-V.
- **Н6.** Плата за откат: при `KYTY_FIX_F20=0` переписанные модули не создаются, блоб драйвера для исходных модулей уже есть у пользователя
  (FS14) — отката «холодом» нет [I]; каталоги `_ShaderSeeds`/`replay`/кэш трансляции хранят исходный SPIR-V [c кода].

## Не заявляется

П. 730(з) целиком — в частности: что бит теряется в игре на установленном бинаре и как часто; что потеря видна на кадре; что правка снимает
задержку регистрации страниц; что переписанные модули годны драйверу на всех сценах; что первый запуск FS15 у пользователя пройдёт без
кадров ≥ 1 с вне формы `f20_v`; что FS15 установлен (FS15d); что путь по умолчанию безвреден в игре (FS15c); что прочие `SCENE_OK` держатся на
FS15; ни одно число — не выигрыш. Ревью не проверяет FS15 игрой.

## Файлы

`C:/kyty/f287/fs15b/`, копии в `docs/track-f/fs15b/` (текстовые — LF; `wt/`, `build/` — только локально): `review_git_fs15b.py` +
`review_git.out.txt`; `knobs_fs15b.py` + `knobs_6beb3b73.out.txt`, `knobs_91b74d09.out.txt`, `knobs_eb7e8b91.out.txt`; `pediff3.py`,
`pediff3r_fs15b.py` + `pediff3r_emu.out.txt`, `pediff3r_neg.out.txt`; `strings.out.txt`; `sha_fs15b.txt`; `gate_order_wt.out.txt`; скрипты
сборки и сторожа (`mk_wt_fs15b.sh`, `build_fs15b.cmd`, `bstep.sh`, `sstep.sh`, `api_chk.sh`, `watch_fs15b.py`); логи `mk_wt.log`,
`build_cfg.log`, `build_ver.log`, `build_emu.log`; `facts_fs15b.py` + шаблон.
