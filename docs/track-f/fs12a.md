# FS12a (`HPP-750`, Emu Engineer): двенадцатый бинарь отгрузки трека F (FS12) — умолчание `KYTY_FIX_F21=1`

Задание — `ROADMAP.md` «СЕССИЯ 122» п. 683(г)(1) (KytyPS5 `b04e50f1`, якорь «(г) **Отгрузка FS12 — константы лида.** (1) **FS12a
(Emu Engineer, без замка).**»); вывод — п. 683(в); образец — FS11a п. 647(д)(1), отчёт `docs/track-f/fs11a.md`; правило базы —
п. 410(г)(6)(i), 656(г); члены стенда — п. 675(д)(1) с п. 678(в), 680(б), 681(в)(1)–(2). Игра не запускалась; установленный
`ps5 em/kyty_emulator.exe` — FS11 `ea51ae80…` до и после звена, `C:/kyty/build/install` и кэши не тронуты. Время — UTC по `date -u`,
события — `C:/kyty/f287/times.txt` (строки `FS12a`). Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно. Замка
`C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` за звено не было (каждая команда начиналась проверкой); звеньев Harness Engineer в
`in_progress` за звено не было (строки API перед каждым шагом); шаги дольше нескольких секунд шли под сторожем `watch_fs12a.py`
(п. 431(в)(1)), он не срабатывал. **WIP по дыму: бинарь собран и проверен тестами и стендом без игры, игрой не проверялся** (теги — FS12c
после FS12b).

## Итог

- **Коммит в `main`: `cbfe8375`** (`--only`, 2 файла: `src/common/subsystems.cpp` +4/−1, `src/common/subsystems.h` +2/−1): умолчание
  `KYTY_FIX_F21` 0 → 1 в форме FS11a `cb022252` (не задана или `""` — 1; иначе `Common::EnvValueOn`).
- **Worktree `C:/kyty/f287/fs12a/wt`, HEAD `730ed40a`** — база FS11 `ee9632be` (worktree FS11a, установленный FS11 `ea51ae80`,
  п. 656–657; другого принятого лидом бинаря отгрузки нет) + cherry-pick `-x`:

  | Шаг | Источник | Коммит в worktree | Конфликт |
  |---|---|---|---|
  | 1 | `227e1b36` (F33c: код `KYTY_FIX_F21`) | `17c71ea6` | нет |
  | 2 | `e5979953` (F33c: стенд `KYTY_TEST_EXITFATAL` издания 2) | `25861288` | нет |
  | 3 | `5237fdff` (F33c2: стенд издания 3, плечо CN) | `9aaea58c` | нет |
  | 4 | `cbfe8375` (FS12a) | `730ed40a` | нет |

  Конфликтов нет; `git status --short` — 0 строк после каждого шага, CR в `src/` — 0 [c `cp_*.log`, `mk_wt.log`]. Риск априора лида
  (п. 683(з): конфликт `e5979953` / `5237fdff` в `src/emulator.cpp` рядом с кодом стенда издания 1) не наступил: изменённые строки
  переноса равны источнику (V1), `5f48cc3e` не предок FS12 и `git cherry` `+` (V1b, V6). Зависимости от кода вне базы нет: сборка
  `kyty_emulator` и тестов без него прошла.
- **Бинарь FS12: sha256 `46892c20080819ae090598511748265dfbac31f303a02f1804e5b10db8acae26`**, копия
  `C:/kyty/f287/bin/kyty_emulator_46892c20.exe` (+ `.sha256`; `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe`). Строка
  версии `KytyPS5-2026-09-15-6a2987a-1914-g730ed40a`. **Не установка.** В exe: `KYTY_FIX_F21` ×1, `FixF21: mode=` ×1,
  `FixF21: wait_expired` ×1, `KYTY_TEST_EXITFATAL` ×3, `nested_fatal` ×1, `KYTY_FIX_B12` ×1, `FixB12: mode=` ×1, `KYTY_FIX_B13` ×1,
  `KYTY_FIX_B36` ×1, `LogAsync: mode=` ×2, `KYTY_DIAG_B32` ×0, `rts_bad_b` ×0, строка подписи `9177b4267de1fb8bac7d1113afd8733210addfac`
  ×1 [c `binary_fs12a.txt`].
- Члены п. 683(г)(1):

  | Член | Итог | Источник |
  |---|---|---|
  | «бинарь содержит» `227e1b36`, `c94c49e0`, `726e751e`, `cb022252` — «предок или `git cherry` `-`», счёт скриптом с отрицательным контролем | ✓ у всех четырёх `git cherry` `-` (предками FS12 не являются — все перенесены cherry-pick: `227e1b36` этим звеном, три остальных — FS11a); изменённые строки переносов этого звена равны источникам (190, 292, 28, 8). Отрицательные контроли — то же правило говорит «нет»: `5f48cc3e` в FS12 (`+`), `227e1b36` в базе `ee9632be` (`+`), `c94c49e0` в FS10 `dc5d4712` (`+`); строки `e5979953` против переноса `227e1b36` и против своего переноса с одной испорченной строкой — не равны | `verify_fs12a.out.txt` V1, V1b |
  | дифф источника FS12 против базы вне `tests/` — только файлы `227e1b36`, `e5979953`, `5237fdff` и FS12a | ✓ 3 пути (`src/common/subsystems.cpp`, `src/common/subsystems.h`, `src/emulator.cpp`) = объединению четырёх коммитов, путей вне них 0; знаковое мультимножество изменённых строк диффа = сумме четырёх (500 строк); без FS12a — не равно. `CMakeLists.txt` и `tests/` не тронуты (разрыва буквы п. 650(в) здесь нет) | V2, V2b |
  | стенд из бинаря FS12 без переменной `KYTY_FIX_F21`: P2 200, C 50, CN 50, H 20, HG 20 по п. 675(д)(1) с п. 678(в), 680(б), 681(в)(1)–(2), `FixF21: mode=1` в каждом испытании | ✓ `MEMBERS ALL YES` (§ «Стенд»); 340 испытаний умолчания, `mode=1` и `cfg_fix=1` в 340 из 340; живых копий после испытаний 0 | `read_fs12a.out.txt` |
  | контроль `KYTY_FIX_F21=0` P2 200 — `second` ≥ 1 | ✓ `second` 175 из 200 (контроль 200), `mode=0` в 200 из 200, `FixF21: wait_expired` 0 | `read_fs12a.out.txt` |
  | N и seed — комментарием до зачётных данных | ✓ комментарий `1ef96924` 2026-10-10 18:58:42Z < первого испытания 19:00:07Z | `times.txt`, TSV `utc` |
  | `memory_tracker_tests`, `shader_cfg_tests` — строки `failed:` и счёт = базе | ✓ `memory_tracker_tests` rc 0 / 0, строк `failed` 0 / 0, `MemoryTrackerTests: all cases passed` у обоих; `shader_cfg_tests` rc 0 / 0, `[test]` 133 / 133, `ShaderCfgTests: failed:` 0 / 0, мультимножество строк со словом `failed` (5) равно; справка t4: SPIR-V 360 / 360 байт в байт (агрегат `b1376644` = FS11a) | `tests/base/`, `tests/fs12/`, `runs/log_tests_*.txt` |
  | подпись трансляции (`KYTY_SHADER_SOURCE_HASH`) = базе `9177b426…` | ✓ `9177b4267de1fb8bac7d1113afd8733210addfac` у сборки базы и FS12; путей диффа под `src/graphics/shader/` 0 (V5) | `base/kytyGitVersion_base.h`, `kytyGitVersion_fs12.h` |
  | `check_gate_order.py` — clean | ✓ `GATE ORDER: clean` на `main` после правки и на worktree до сборки; выводы (без строки заголовка, без учёта CR) равны выводу FS11a — гейтов и ручек правка не добавляет | `gate_order_main.out.txt`, `gate_order_wt.out.txt` |
  | таблица умолчаний своим сканером — база FS11 + `KYTY_FIX_F21` (и только он) | ✓ 16 → 17; отрицательный контроль на `9aaea58c` (до FS12a) — разность пуста, член там не выполнен | V3 |
  | `KYTY_S_REPLAY` = 3 | ✓ blob `shaderReplay.cpp` базы = FS12 (`e1626ad6…`), `ParseMode` не задана / `""` → 3 | V4 |
  | sha256 и копия `C:/kyty/f287/bin/kyty_emulator_<sha8>.exe`, не установка | ✓ `kyty_emulator_46892c20.exe`; установленный `ea51ae80…` до и после | `binary_sha.txt`, `times.txt` |
  | стенд издания 1 `5f48cc3e` и диагностики вне базы не входят | ✓ `5f48cc3e`, `585d997d` не предки FS12; добавленных строк кода с `KYTY_DIAG_B32` / `rts_bad_b` 0; в exe ×0 | V6, `binary_fs12a.txt` |

## Код (`cbfe8375`, в worktree — `730ed40a`)

`src/common/subsystems.cpp`, `Subsystems::InitFixF21` (`cbfe8375:src/common/subsystems.cpp:71`, якорь «// Track F, FS12a (HPP-750,
ROADMAP s122 item 683(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other»; +1 — «// value as EnvValueOn (the form
of FS11a cb022252).»):

```cpp
// F33c: KYTY_FIX_F21 (the flags - at the top of this file).
// Track F, FS12a (HPP-750, ROADMAP s122 item 683(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other
// value as EnvValueOn (the form of FS11a cb022252).
void Subsystems::InitFixF21() {
	const char* value = std::getenv("KYTY_FIX_F21");
	g_fix_f21  = value == nullptr || value[0] == '\0' || EnvValueOn(value);
	g_f21_path = g_fix_f21 || g_f21_hook != nullptr;
}
```

- До FS12a: `g_fix_f21  = EnvFlagOn("KYTY_FIX_F21"); // unset, "", 0/false/off/no - OFF (the form of FS4a)` — не задана = 0. В
  `subsystems.h` из заголовка снято «(default 0)» и добавлена строка «// Track F, FS12a … default ON - unset or "" = ON, 0/false/off/no
  = OFF.»; прочий текст F33c не тронут.
- Одно чтение на главном потоке до потоков гостя сохранено: единственный вызов `InitFixF21` — `Emulator::Run` до `Init`
  (`730ed40a:src/emulator.cpp:530`, якорь «Common::Subsystems::InitFixF21();»; +1 — «Common::Subsystems subsystems(true);»), после
  `ExitFatalStand::Parse()` [c `git grep InitFixF21 730ed40a -- src tests`: одно определение, один вызов]. Читатели `g_fix_f21` в `src/`
  FS12 — `InitFixF21`, `LogFixF21`, `FixF21On` (строка `ExitFatal: config … fix=` стенда), `SetEmergencyHook` и ветка стенда при `=0`
  (`730ed40a:src/common/subsystems.cpp:129`, якорь «if (!g_fix_f21) {»; +1 — «// KYTY_FIX_F21=0 with the stand armed: the FS11 sequence -
  every entry walks - observed.») — все без изменений.
- Строка `FixF21: mode=<0|1>` печатается по значению, как в F33c (`730ed40a:src/common/subsystems.cpp:80`, якорь
  «LOGF("FixF21: mode=%d wait_ms=%u\n", g_fix_f21 ? 1 : 0, kFixF21WaitMs);»; +1 — «}»): без переменной теперь `mode=1`.
- Пути по коду [c]: без переменной, `""`, `1/true/on/yes` — `g_fix_f21` = 1; `0/false/off/no` — 0 (путь `=0` по коду = база FS11 плюс
  одна проверка `g_f21_path` — п. 680(в); сверка — FS12b). Чтение по строке `730ed40a:src/common/subsystems.cpp:74` (якорь «const char*
  value = std::getenv("KYTY_FIX_F21");»; +1 — «g_fix_f21  = value == nullptr || value[0] == '\0' || EnvValueOn(value);»).
- Тесты (`memory_tracker_tests`, `shader_cfg_tests`) `InitFixF21` не зовут — у них `g_fix_f21` остаётся статическим `false`, путь FS11,
  как до FS12a [c `git grep`; t2/t3 = базе].
- Ссылки этого отчёта проверены скриптом `refs_fs12a.py`: `REFS 5 ALL OK`, отрицательный контроль (сдвиг +1) — `FAILED`.

## Состояние, вводимое правкой

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `g_fix_f21`, `g_f21_path` (статические `subsystems.cpp:23`, `:25`) | один раз — `InitFixF21` в `Emulator::Run` до `Init` (главный поток, до любых потоков хоста и гостя); `g_f21_path` ещё — `SetEmergencyHook` (только стенд, тот же поток и время) | не снимаются (время жизни процесса) | как в F33c `227e1b36`; меняется только выражение инициализации `g_fix_f21` |

Нового состояния правка не вводит; выходов функции не прибавилось (`InitFixF21` без ранних возвратов).

## Стенд (`run_stand_fs12a.py`, `read_fs12a.py`)

Бинарь стенда — сам FS12 (копия `run/kyty_emulator_46892c20.exe`, sha256 `46892c20…`), `cwd` `run/`, пустой `app0`, без игры. Драйвер —
`run_stand_f33c2.py` (`66ec6149`), порт скриптом `mk_driver_fs12a.py`: `BASE` → `C:/kyty/f287/fs12a`, `--fix d` — `KYTY_FIX_F21` не
задаётся (удаляется вместе со всеми `KYTY_*`); плечи, поля и классы — без изменений (дифф — 3 места). Ридер `read_fs12a.py` — порт
функций членов `read_f33c.py` / `read_f33c2.py` с планом п. 683(г)(1); фикстуры `test_read_fs12a.py` — 30 случаев (по одному на член),
`ALL OK` до чтения. Seed — 1..N каждого плеча, как названо в комментарии `1ef96924` (18:58:42Z) до первого испытания (19:00:07Z). Испытания
19:00:07–19:11:48Z; таймаут 30 с; живых копий после каждого испытания 0.

| Плечо | N | Итог | Строка ридера |
|---|---|---|---|
| умолчание P2 | 200 | ✓ | контроль 200; `second` = `crash` = `hang` = `cut` = `expired` = 0; коды 0/321 193/7 |
| умолчание C | 50 | ✓ | `walks` 1, код 321, `reenter` ≥ 1, `nested` 0, классы 0, `done_seen` 0 — в 50 из 50; длительность ≤ 0,441 с |
| умолчание CN | 50 | ✓ | `walks` 1, `nested` 0, `reenter` ≥ 2 (мин. 2), `expired` 0, `expired_seen` 0, код 321, `hang` 0, `crash` 0, длительность 0,149–0,450 с < 6 с; `nested_fatal` = 1 в 50 из 50 (контроль стенда); `cut` 50 — справка |
| умолчание H | 20 | ✓ | порядок 20, `expired` ≥ 1 в 20 из 20, коды 0/321 11/9 (`crash` 0), `hang` 0, `second` 0; время до конца процесса 15,006–15,027 с (справка), `cut` 0 |
| умолчание HG | 20 | ✓ | `expired` ≥ 1 в 20 из 20, код 0 ×20, `hang` 0, `second` 0, время от входа главного потока до конца процесса 12,004–12,018 с ∈ [12; 13,5]; `cut` 20 — справка |
| все плечи умолчания | 340 | ✓ | `cfg_fix=1` и строка `FixF21: mode=1` в 340 из 340 |
| `=0` P2 | 200 | ✓ | `second` 175 ≥ 1 (контроль 200; `cut` 61; коды 147/53); `FixF21: wait_expired` 0; `mode=0` и `cfg_fix=0` в 200 из 200 |

Итог ридера — `MEMBERS ALL YES` [c `read_fs12a.out.txt`]. Пример лога [c]: `runs/fixd/H/5.err` — `FixF21: wait_expired tid=3
waited_ms=12007`; `runs/fixd/HG/5.err` — `FixF21: wait_expired tid=1 waited_ms=12008`; `runs/fixd/P2/1.log` — `FixF21: mode=1 wait_ms=12000`.

**Отрицательный контроль формы «умолчание»:** та же форма (`--fix d`, без переменной) на бинаре стенда F33c2 `a086872d…` (умолчание 0),
C 1–10 и P2 1–20 — `MEMBERS NOT ALL`: `cfg_fix=1` / `mode=1` в 0 из 30, P2 `second` 18 из 20, C `walks` ≠ 1 и `reenter` 0 в 10 из 10
[c `read_fs12a_neg.out.txt`]. Член «без переменной — путь `=1`» ловит бинарь со старым умолчанием.

Сопоставление с F33c/F33c2 (справка, не член): P2 при `=1` у F33c — коды 579/21 из 600, здесь 193/7 из 200; `=0` P2 у F33c — `second`
174 из 200, здесь 175; H у F33c — коды 16/4, здесь 11/9 (п. 680(д): доля — не свойство процесса); HG у F33c — 12,004–12,018 с, здесь
12,004–12,018 с.

## Тесты (`run_tests_fs12a.py`)

База — та же сборка worktree на `ee9632be` до cherry-pick (сборка тестов 18:55:18–18:56:20Z, прогон 18:56:30–18:56:32Z); FS12 — после
(configure 18:56:54Z, `kyty_emulator` 18:57:00–18:57:32Z, версия и пересборка 18:57:33–18:57:39Z, тесты 18:57:41–18:58:03Z, прогон
18:58:10–18:58:13Z); все `KYTY_*` сняты. sha256: `shader_cfg_tests.exe` FS12 `6fce4d9d…`, `memory_tracker_tests.exe` `e159aae8…`. Список
HANDOFF §4 «14 известных падений» на этом дереве не воспроизводится — 0 падений у базы и у FS12, как у FS11a. Справка: в выводе
`memory_tracker_tests` строка `FixB13: mode=1` у обоих, строк `FixF21:` нет ни у базы, ни у FS12 (тест не зовёт `Emulator::Run`).

## Ход (UTC)

- `18:51:49Z` — первая команда (проверка замка); `18:53:43Z` — строка начала и строка API; `18:54:13Z` — коммит `cbfe8375` и
  `check_gate_order.py` на `main` (`GATE ORDER: clean`).
- `18:54:18–18:54:30Z` — `mk_wt_fs12a.sh` (worktree, подмодули архивом); `18:54:31–18:56:20Z` — configure, версия, сборка тестов базы;
  `18:56:30–18:56:32Z` — тесты базы.
- `18:56:47Z` — cherry-pick 1–4; `18:56:53Z` — `check_gate_order.py` на worktree (`GATE ORDER: clean`).
- `18:56:54–18:58:03Z` — configure и сборки FS12; `18:58:10–18:58:13Z` — тесты FS12; `18:58:23Z` — копия бинаря, sha256 установленного —
  `ea51ae80…`.
- `18:58:42Z` — комментарий с N и seed; `19:00:07–19:11:48Z` — стенд; `19:12:11–19:12:22Z` — отрицательный контроль; `19:13:10Z` —
  `verify_fs12a.py` `ALL OK`.

Флаги сборки = FS11a (`build_fs12a.cmd` — копия `build_fs11a.cmd` с путями `fs12a`); Release, clang-cl, LTO. Отступление от общего
правила 31: `port_fs12a.py` и `patch_fs12a.py` записаны в `C:/kyty/f287/fs12a/` инструментом Write напрямую (около 18:53Z; замка и STOP
не было на команде до и после) — прочие файлы — черновиком в папке прогона и переносом командой с проверкой замка.

## Файлы

`C:/kyty/f287/fs12a/`, копии в `docs/track-f/fs12a/` (текстовые — LF):
- **Скрипты:** `port_fs12a.py`, `patch_fs12a.py`, `mk_wt_fs12a.sh`, `cp_fs12a.sh`, `build_fs12a.cmd`, `bstep.sh`, `sstep.sh`,
  `api_chk.sh`, `watch_fs12a.py`, `run_tests_fs12a.py`, `mk_driver_fs12a.py`, `run_stand_fs12a.py`, `read_fs12a.py`,
  `test_read_fs12a.py`, `verify_fs12a.py`, `refs_fs12a.py`.
- **Выводы:** `patch_main.out.txt`, `gate_order_main.out.txt`, `gate_order_wt.out.txt`, `mk_wt.log`, `cp_*.log`, `tests/base/` и
  `tests/fs12/` (без `spv/`), `runs/log_*.txt`, `runs/fixd/stand_*.tsv`, `runs/fix0/stand_P2.tsv`, `runs_neg/fixd/stand_*.tsv`,
  `read_fs12a.out.txt`, `read_fs12a_neg.out.txt`, `test_read_fs12a.out.txt`, `verify_fs12a.out.txt`, `refs_fs12a.out.txt`,
  `binary_fs12a.txt`, `binary_sha.txt`, `kytyGitVersion_fs12.h`, `base/kytyGitVersion_base.h`, `commit_msg_code.txt`. Логи
  испытаний (`runs/fix*/<плечо>/<seed>.{out,err,log}`) — только локально.

## Не заявляется

П. 683(и) целиком; в частности: что FS12 работает в игре (дыма не было, до FS12c); что FS12 установлен (до FS12d); что Ф21 случается в
игре и с какой частотой; что второй обход вредил пользователю; что стенд заменяет игру; что `T` = 12 с достаточно на любой машине; что
CRT другой версии ведёт себя так же; что путь по умолчанию FS12 по машинному коду равен пути `=1` бинаря F33c `2b393af8` (сверка —
FS12b); что набор тестов полон; что реестр полон; ни одно число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется.
