# FS13b (`HPP-788`, Red Team): ревью бинаря отгрузки FS13 `abab2196` — умолчание `KYTY_FIX_F25=1`

**Вердикт: PASS.** RC кода 0; замечаний без RC 3 (Н1–Н3, «читать так»). Бинарь FS13 `abab2196…` идёт в FS13c без изменений.

Задание — `ROADMAP.md` «СЕССИЯ 122» п. 697(г)(2) (KytyPS5 `7d62a36a`, якорь «(2) **FS13b (Red Team, без замка): ревью.**»);
вход — отчёт FS13a `b21e7e01:docs/track-f/fs13a.md` (бинарь `C:/kyty/f287/bin/kyty_emulator_abab2196.exe`, worktree
`C:/kyty/f287/fs13a/wt` HEAD `ea6c6e9e`, коммит в `main` `3630f116`). Игра не запускалась; установленный
`ps5 em/kyty_emulator.exe` — FS12 `46892c20…` [c `sha_fs13b.txt`], `C:/kyty/build`, `C:/kyty/build/install` и кэши не тронуты.
Замка `C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` за звено не было (каждая команда начиналась проверкой); звеньев Harness Engineer
в `in_progress` не было (строки `FS13b API check` в `C:/kyty/f287/times.txt` перед каждым шагом сборки и стенда); шаги — под сторожем
`watch_fs13b.py`, он не срабатывал. Время — UTC по `date -u`. Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно.
Ссылок `<коммит>:<путь>:<строка>` отчёт не несёт (места названы по функциям и файлам).

**Ход.** Прогон 2026-10-11 02:07Z (worktree `C:/kyty/f287/fs13b/wt` от `ea6c6e9e`, подмодули архивом, `git status` 0 строк, CR в `src/` 0
[c `mk_wt.log`]) отменён оператором доски посреди configure (лог `build_cfg_cancelled.log`, «Configuring incomplete»); по комментарию
пользователя «продолжай» 08:03:37Z работа продолжена с того же worktree: папка сборки удалена и собрана заново (configure 08:04:29–08:05:31Z,
`kyty_emulator` 08:05:41–08:06:44Z, `f25_read_fail_stand` 08:06:51–08:07:28Z), комментарий с N и seed 08:10:24Z, стенд 08:10:29–08:10:37Z.

## Члены п. 697(г)(2)

| Член | Итог | Источник |
|---|---|---|
| Путь `KYTY_FIX_F25=0` на FS13 по коду = база FS12 | ✓ (§ «Код») | `diff_src_fs13_vs_base.txt`, `review_git.out.txt` R6 |
| Путь по умолчанию = путь `=1` бинаря F38a `5a14a111`: дифф `src/` FS13 против worktree F38a — только FS13a | ✓ дерево `src/` у F38a worktree `531d6488`, у `d7a30e55` (код F38a) и у FS13 до FS13a `0861c391` — одно `83f3a449…`; `git diff 531d6488 ea6c6e9e -- src/` = `git diff 0861c391 ea6c6e9e -- src/` (FS13a, 1 путь `src/kernel/fileSystem.cpp`, 26 строк диффа); отрицательный контроль — дифф от базы ≠ дифф FS13a | `review_git.out.txt` R2 |
| Дифф FS13 против базы `730ed40a` — только п. 697(г)(1) | ✓ 13 путей: вне `tests/` и `docs/` — `CMakeLists.txt` (+5/−0: цель `f25_read_fail_stand`, 2 строки кода, 2 комментария, 1 пустая) и `src/kernel/fileSystem.cpp`; `tests/` — только `tests/F25ReadFailStand.cpp`; `docs/` — 10 путей `docs/track-f/f37a*` (Н2) | R1 |
| Ф21, Б12, Ф27, Б13, Б33, Ф10, Ф16, Ф19, Б42, Б4, Ф8, Б24, S-replay, P-var не тронуты | ✓ каждый файл `src/` базы, называющий ручку строки (`KYTY_FIX_F21`, `_B12`, `_B36`, `_B13`, `KYTY_S_PCW`, `_F10`, `_SVAL`, `_F19`, `_B42`, `_B4`, `_F8`, `_B24`, `KYTY_S_REPLAY`, `KYTY_PVAR`/`KYTY_GAME_PATCH`), — тот же blob в FS13, кроме `src/kernel/fileSystem.cpp` (Б4); в нём 61 изменённая строка, ни одна не называет другую ручку или символ `Fix<X>` кроме F25; удалены 3 строки — сигнатура `ReadGuestWithRetry` и два её вызова | R4 |
| Своя сборка из чистого worktree и sha | sha256 своей сборки `dd036d45f96a2f67…` ≠ `abab2196…`; причина названа: `pediff3r` — 2 438 байт, все объяснены (`(1)` имя папки сборки 139, `(2)` тег анонимного пространства имён 1 826 + 459 строк `.data`, `(3)` штамп/GUID 14), **`.text` 0**, `VERDICT EXPLAINED`; стенд `26bbae35…` против стенда FS13a `816dea2d…` — так же `.text` 0, `EXPLAINED`; отрицательный контроль: своя сборка против FS12 `46892c20` — размеры не равны, сравнение отказывает (`AssertionError`) — инструмент не «объясняет» другой код. Строка версии `KytyPS5-2026-09-15-6a2987a-1919-gea6c6e9e` = FS13a | `pediff3r_emu.out.txt`, `pediff3r_stand.out.txt`, `pediff3r_neg.out.txt`, `sha_fs13b.txt`, R5 |
| Таблица умолчаний | ✓ своим сканером (`knobs_fs13b.py`, порт моего FS12b): ON-IF-UNSET на `ea6c6e9e` — 18 = 17 FS12b + `KYTY_FIX_F25`, `missing [] extra []`; отрицательные контроли — `730ed40a` и `0861c391` (до FS13a): `missing ['KYTY_FIX_F25']`; UNDECIDED — те же 6 у всех трёх (`KYTY_S_REPLAY` в их числе: blob `shaderReplay.cpp` = базе по R4 S-replay, умолчание 3 — FS13a V4) | `knobs_ea6c6e9e.out.txt`, `knobs_730ed40a.out.txt`, `knobs_0861c391.out.txt` |
| «Содержит» `e9dd8604`, `cbfe8375`, `227e1b36`, `c94c49e0`, `726e751e`, `cb022252` | ✓ у всех шести `git cherry` `-` (форма `git cherry <FS13> <c> <c>^` — ровно один коммит); контроли: `e9dd8604` и `3630f116` в базе — `+`, `cbfe8375` в FS11 `ee9632be` — `+`, код Ф24 `5c21c387` в FS13 — `+`, положительный `3630f116` в FS13 — `-` | R3 |
| Подпись трансляции | ✓ `KYTY_SHADER_SOURCE_HASH` своей сборки `9177b4267de1fb8bac7d1113afd8733210addfac` = FS12; путей `src/graphics/shader/` в диффе 0 | R5 |
| Свой прогон стенда издания 3 без переменной: A ≥ 200, E ≥ 50, G ≥ 50 на каждом входе | ✓ § «Стенд» | `runs/`, `recount.out.txt` |

`review_git_fs13b.py` — `ALL OK` (второй прогон; первый `NOT OK` из-за моей формы `git cherry <tip> <c> <merge-base>`, перечислявшей все
коммиты от общей базы, — исправлена на `<c>^`, логика членов не менялась; оба вывода сохранены: `review_git.out.txt` — зачётный).

## Код (`src/kernel/fileSystem.cpp`, FS13 против базы FS12)

Прочитан весь дифф (`diff_src_fs13_vs_base.txt`, 139 строк). Путь `=0` (переменная `0/false/off/no`):

- `FixF25Enabled` — статическая константа, первое чтение в `FileSystem::Initialize` (строка `FixF25: mode=0`); `FixF25Report` при `=0`
  не вызывается (единственные вызовы — под `if (fix_f25_eio)`).
- `ReadGuestWithRetry`: добавлены `*failed_twice = false;` первой строкой и `else { *failed_twice = true; }` после второго чтения —
  запись признака; чтения, `memcpy`, ранний возврат и `bytes_read` — строки базы.
- `KernelRead`: `read_failed_twice` и `fix_f25_eio` — локальные; `if (read_failed_twice && FixF25Enabled())` при `=0` ложно — `Size()` и
  `Seek(pos)` нового пути не исполняются; `fix_f25_eio` остаётся `false` — `return KERNEL_ERROR_EIO` нового пути не исполняется; далее —
  строки базы. `KernelPread` — так же (`Size()` под тем же условием; `Seek(pos)` после — строка базы).
- Итог [c кода]: при `=0` исполняемая разница с базой — запись признака, две локальные и строка `FixF25: mode=0`, как в п. 697(б)(2).

Путь по умолчанию (переменная не задана или `""`) = путь `=1` F38a: изменение FS13a — только выражение инициализации `enabled`
(`value == nullptr || value[0] == '\0' || Common::EnvValueOn(value)`) и комментарий; форма та же, что `FixF21Enabled` FS12a и
`FixB12Enabled` FS11a; потокобезопасная инициализация статической переменной C++11; ранних возвратов нет. Прочее тело F38a — без
изменений (R2), его ревью — F38b `PASS` (код `e9dd8604`), стенд — F38b2 `PASS`.

## Стенд издания 3 (своя сборка)

Стенд `C:/kyty/f287/fs13b/build/f25_read_fail_stand.exe` (sha256 `26bbae35…`) из worktree FS13 `ea6c6e9e`; исходник стенда = `main`
(sha256 `ef89b326…`); драйвер `run_stand_fs13b.py` — копия `run_stand_fs13a.py` с путями `fs13b` (WT, EXE), из окружения процесса сняты
все `KYTY_*` (`identity_38801_fd.txt`: `KYTY_* in the stand environment: none`). N и seed — комментарием `826a526e` 08:10:24Z до первого
испытания (08:10:29Z+).

| Процесс | Seed | N на вход (A/K/Z/E/T/G) | Ридер `sum_fs13a.py` (`96859d20…`, фикстуры `ALL OK`) | Мой пересчёт `recount_fs13b.py` |
|---|---|---|---|---|
| умолчание (переменная не задана) | 38801 | 200/50/50/50/20/50 | `MEMBERS PASS (fix=1)`, `MEMBERS LETTER YES (form d)`; лог: `FixF25: mode=1` ×1, `mode=0` ×0, `read failed twice` 32 (предел) | на каждом из шести входов A 200/200 «код ошибки» (`0x80020005` у `sceKernel*`/AIO с `aio_state` 4; `-1`/`errno` 5 у `read`/`_read`/`pread`), позиция не сдвинута, буфер не тронут, 2 вызова; E 50/50, G 50/50 — 0, один вызов, без внесённого отказа |
| контроль `KYTY_FIX_F25=0` (справка) | 38801 | 200/50/50/50/20/50 | `MEMBERS PASS (fix=0)`, `CONTROL A ZERO YES`; лог `mode=0` ×1, `read failed twice` 0 | A 200/200 «отдано 0» на каждом входе; E, G 50/50 |

`DONE trials=2520`, `FINAL file sha256 equal 1` у обоих процессов, rc 0. Отрицательный контроль моего пересчёта — файлы в обратном
порядке (форма `d` на строках `=0`) — `RECOUNT NOT OK` [c `recount_neg.out.txt`]. Бинарь стенда отличается от стенда FS13a только
вне `.text` — прогон на своей сборке относится к коду FS13 [I по `pediff3r`].

## Замечания без RC (читать так)

- **Н1.** Значение переменной вне `0/false/off/no` и вне `1/true/on/yes` (например `2`) читается `Common::EnvValueOn` — та же форма, что у
  FS11a/FS12a; поведение одинаково для всех ручек с умолчанием 1, отличия от п. 697(г)(1) нет.
- **Н2.** В дереве FS13 против базы 10 путей `docs/track-f/f37a/` (перенесены cherry-pick `51c9e38f`) — в сборку не входят; член «дифф
  только (1)» читается как у FS13a: «вне `tests/`, `docs/` и цели CMake стенда — только `src/kernel/fileSystem.cpp`».
- **Н3.** Своя сборка не равна FS13a по sha (`dd036d45…` ≠ `abab2196…`); равенство показано по классам байт с `.text` 0, не байт в байт.
  Тесты `kernel_file_system_tests`/`shader_cfg_tests` своей сборкой не повторял — не члены FS13b (члены FS13a).

## Не заявляется

П. 697(з) целиком: что двойной отказ чтения случается в игре и с какой частотой; что 0 вместо ошибки уже вредил игре; что игра
обрабатывает `EIO` лучше, чем 0; что настоящий второй отказ — «всё или ничего»; что стенд заменяет игру; что FS13 установлен; что прочие
`SCENE_OK` держатся на FS13; ни одно число — не выигрыш. Ревью не проверяет FS13 игрой (FS13c).

## Файлы

`C:/kyty/f287/fs13b/`, копии в `docs/track-f/fs13b/` (текстовые — LF): `review_git_fs13b.py` + `review_git.out.txt`;
`knobs_fs13b.py` + три вывода; `pediff3.py`, `pediff3r_fs13b.py` + три вывода; `recount_fs13b.py` + `recount.out.txt`,
`recount_neg.out.txt`; `run_stand_fs13b.py`, `sum_fs13a.py`, `sum_f38a2.py` (копии FS13a); `runs/` (строки стенда, логи, сводки,
`identity_*`); `diff_src_fs13_vs_base.txt`; `sha_fs13b.txt`; скрипты сборки и сторожа (`mk_wt_fs13b.sh`, `build_fs13b.cmd`,
`bstep.sh`, `sstep.sh`, `api_chk.sh`, `watch_fs13b.py`); логи `mk_wt.log`, `build_cfg.log`, `build_cfg_cancelled.log`, `build_ver.log`,
`build_emu.log`, `build_stand.log`; `facts_fs13b.py` + шаблон.
