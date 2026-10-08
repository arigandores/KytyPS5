# FS10a (`HPP-684`, Emu Engineer): десятый бинарь отгрузки трека F (FS10) — умолчание `KYTY_FIX_B36=1`

Задание — `ROADMAP.md` «СЕССИЯ 122» п. 624(е)(1) (KytyPS5 `628f8999`, якорь «(е) **Отгрузка FS10 — константы лида.** (1) **FS10a
(Emu Engineer, без замка).**»), следствия — п. 624(д)(1), порядок — п. 624(е)(5); образец — FS9a п. 604(д)(1), отчёт `docs/track-f/fs9a.md`;
правило базы — п. 410(г)(6)(i); член «содержит» — п. 615(б)(5). Игра не запускалась; установленный `ps5 em/kyty_emulator.exe` —
FS9 `3861eeea…` до и после звена, `C:/kyty/build/install` и кэши не тронуты. Время — UTC по `date -u`, события — `C:/kyty/f287/times.txt`
(строки `FS10a`). Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно. Замка `C:/kyty/SEALED_RUN.lock` и
`C:/kyty/f287/STOP` за звено не было (каждая команда начиналась проверкой). Звеньев Harness Engineer в `in_progress` не было (строки
проверки API в `times.txt`); шаги дольше нескольких секунд (worktree, configure, сборки, тесты) всё равно шли под сторожем
`watch_fs10a.py` (п. 431(в)(1)); сторож не срабатывал. **WIP по дыму: бинарь собран и проверен тестами без игры, игрой не проверялся**
(теги — FS10c после FS10b).

## Итог

- **Коммит в `main`: `7f34b1e2`** (`--only`, 2 файла, +12/−3): умолчание `KYTY_FIX_B36` 0 → 1 в форме FS4a `17adaf80`; тест `seq0_unset`
  следует умолчанию.
- **Worktree `C:/kyty/f287/fs10a/wt`, HEAD `dc5d4712`** — база FS9 `11164d72` (worktree FS9a, установленный FS9 `3861eeea`, п. 609–610;
  другого принятого лидом бинаря отгрузки нет) + cherry-pick `-x`:

  | Шаг | Источник | Коммит в worktree | Конфликт |
  |---|---|---|---|
  | 1 | `a8ee1b05` (F25k: `KYTY_FIX_B36`, стенд, мера, тесты) | `a42f50b1` | нет (авто-слияние 6 файлов) |
  | 2 | `b4ee756a` (F25k: страж `t_in_queue`) | `7bc87bc8` | нет |
  | 3 | `0e4b2f5a` (F25k: `tid`, роль в `TestLogStall`) | `64a1fa40` | нет |
  | 4 | `5064c5bb` (F25k2: RC1, RC2, RC4) | `1a7eaff8` | нет |
  | 5 | `7f34b1e2` (FS10a) | `dc5d4712` | нет |

  Конфликтов нет ни одного — разрешение «в пользу базы» не понадобилось; `git status --short` — 0 строк, CR в `src/` — 0 [c `cp_*.log`,
  `mk_wt.log`]. Зависимости кода переноса от символа `KYTY_DIAG_B32` нет: сборка без него прошла; в добавленных строках диффа
  `11164d72..dc5d4712` имя `KYTY_DIAG_B32` / `DiagB32` есть только в одном комментарии (`log.cpp:306`, имя потока `LogWriter`); файла
  `src/common/diagB32.h` нет ни в базе, ни в FS10 [c `verify_fs10a.out.txt` V6]. В базе `g_logger_mutex` — `std::mutex`
  (`dc5d4712:src/common/logging/log.cpp:92`), в `main` — `DiagB32::TrackedMutex<std::mutex>`; код F25k/F25k2 берёт его через
  `std::lock_guard` и в обоих видах собирается одинаково (место для ревью FS10b, п. 624(е)(2)).
- **Бинарь FS10: sha256 `abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe`**, копия
  `C:/kyty/f287/bin/kyty_emulator_abfded5e.exe` (+ `.sha256`; `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe`). Строка версии
  `KytyPS5-2026-09-15-6a2987a-1905-gdc5d4712`. **Не установка.** В exe: `KYTY_FIX_B36` ×1, `KYTY_FIX_B13` ×1, `KYTY_DIAG_B32` ×0,
  `LogAsync: mode=` ×2, `KYTY_TEST_LOGSTALL` ×2, `KYTY_LONGFRAME` ×1, строка подписи `9177b4267de1fb8bac7d1113afd8733210addfac` ×1 [c `binary_fs10a.txt`].
- Члены п. 624(е)(1) — все ✓:

  | Член | Итог | Источник |
  |---|---|---|
  | t1 `log_async_tests` из того же worktree: без переменной — `=1`, `KYTY_FIX_B36=0` — `=0` | ✓ rc 0, `ALL OK`, 19 случаев / 0 падений; `seq0_u` (не задана) — первая строка `LogAsync: mode=1 …`, `full_waits=0`, без строк `LogAsync:` = ожидаемым байтам; `seq0_0` (`=0`) — строк `LogAsync:` 0, = ожидаемым байтам (t1c) | `tests/fs10/log_async_tests.log`, `runs/log_tests_fs10.txt` |
  | t1b `=0` байт в байт с эталоном F25k | ✓ эталон `f25k/ref/log_async_tests_ref.exe` (sha256 `dfc75800…`) `d268b0b0…` = `seq0_0` `d268b0b0…`; отрицательные контроли: `=1` `b11d5fc3…` ≠, не задана `b11d5fc3…` ≠ | там же |
  | `shader_cfg_tests` — строки `failed:` и счёт = базе | ✓ rc 0 / 0, `[test]` 133 / 133, `ShaderCfgTests: failed:` 0 / 0, мультимножество строк со словом `failed` (5) равно; справка t4: SPIR-V 360 / 360 файлов байт в байт (агрегат `b1376644` = агрегату F25k2 и FS8a fu) | `tests/base/`, `tests/fs10/` |
  | подпись `KYTY_SHADER_SOURCE_HASH` = базе `9177b426…` | ✓ `9177b4267de1fb8bac7d1113afd8733210addfac` у сборки базы и FS10 | `base/kytyGitVersion_base.h`, `kytyGitVersion_fs10.h` |
  | таблица умолчаний = база FS9 + `KYTY_FIX_B36` (и только он) | ✓ 14 → 15 | `verify_fs10a.out.txt` V3 |
  | `KYTY_S_REPLAY` = 3 | ✓ blob `shaderReplay.cpp` базы = FS10 (`e1626ad6…`), `ParseMode` не задана / `""` → 3 | V4 |
  | дифф против базы — только файлы четырёх коммитов и FS10a | ✓ 8 путей = объединению; знаковое мультимножество изменённых строк = сумме пяти коммитов (1 403 строки) | V2 |
  | «бинарь содержит» каждый из четырёх (+ FS10a) — `git cherry` `-` или равенство отсортированных строк `+`/`-` | ✓ изменённые строки равны у 5 из 5 (1 073, 14, 28, 355, 15); `git cherry`: `-` у `b4ee756a`, `0e4b2f5a`, `5064c5bb`, `7f34b1e2`; `+` у `a8ee1b05` (patch-id отличается строками контекста базы — у `main` рядом код `KYTY_DIAG_B32`; изменённые строки равны) | V1 |
- Отрицательные контроли скрипта (V1–V3) — все сработали: `5064c5bb` против `a42f50b1` — не равно; против своего коммита с одной испорченной
  строкой — не равно; сумма без FS10a против диффа — не равно; таблица на `1a7eaff8` (до FS10a) — разность пуста, член там не выполнен.
- `check_gate_order.py` (`C:/kyty/s113/`) — `GATE ORDER: clean` на `main` после правки и на worktree до сборки; выводы байт в байт равны
  выводу FS9a (`UNMATCHED … RebindSlowCensus` — та же строка, что у FS9a); гейтов и ручек правка не добавляет [c].

## Код (`7f34b1e2`, в worktree — `dc5d4712`)

`src/common/logging/log.cpp`, `InitAsync` (`7f34b1e2:src/common/logging/log.cpp:733`, якорь «// Track F, FS10a (HPP-684, ROADMAP s122
item 624(e)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any»; +1 — «// other value as EnvValueOn (the form of FS4a 17adaf80);
read once, here.»):

```cpp
	// Track F, FS10a (HPP-684, ROADMAP s122 item 624(e)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any
	// other value as EnvValueOn (the form of FS4a 17adaf80); read once, here.
	const bool requested = [] {
		const char* value = std::getenv("KYTY_FIX_B36");
		return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);
	}();
```

- До FS10a: `const bool requested = Common::EnvFlagOn("KYTY_FIX_B36");` — не задана = 0.
- Одно чтение сохранено: `InitAsync` зовётся один раз из `Log::Initialize` на главном потоке до прочих потоков (как в F25k); ручка нигде
  больше не читается [c `git grep KYTY_FIX_B36 dc5d4712 -- src`: одно место].
- Строки `LogAsync: mode=1 …`, `LogAsync: mode=0 requested=1 reason=direction`, стенд `KYTY_TEST_LOGSTALL` и мера `KYTY_LONGFRAME` не тронуты.
  **Следствие умолчания [c кода]:** при направлении лога не `File` (консоль) и без переменной теперь печатается строка
  `LogAsync: mode=0 requested=1 reason=direction` (раньше — только при явной `=1`); при `Silent` строка не выводится. В `shader_cfg_tests`
  строк `LogAsync` 0 — как у базы.
- Тест `tests/LogAsyncTests.cpp` (`7f34b1e2:tests/LogAsyncTests.cpp:448`, якорь «// Track F, FS10a (HPP-684, ROADMAP s122 item 624(e)(1)):
  KYTY_FIX_B36 is ON by default - unset is =1.»; +1 — «Case("seq0_unset: KYTY_FIX_B36 unset - default ON since FS10a - checked as
  seq0_1");»): случай `seq0_unset` проверялся как «= файлу `=0`», теперь — как `seq0_1` (первая строка `LogAsync: mode=1`, `full_waits=0`,
  без строк `LogAsync:` = ожидаемым байтам). Иных случаев с переменной «не задана» в тестах нет (`Spawn` с `fix == nullptr` — только
  `seq0_unset`); `_putenv_s(name, "")` на Windows удаляет переменную — значение `""` тестом отдельно не проверяется (по коду — как «не задана»).
- Пути по коду [c]: без переменной, `""`, `1/true/on/yes` — `requested` = 1; `0/false/off/no` — 0 (путь до F25k байт в байт — t1b).
  Файлов `src/graphics/shader/**` и `CMakeLists.txt` правка FS10a не трогает.

## Состояние, вводимое правкой

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `requested` (локальная `InitAsync`, `log.cpp:735`) | один раз — вызов `InitAsync` | выход из `InitAsync` | как до FS10a (была локальной); меняется только выражение инициализации; `Async::g_on`, `g_hooks` ставятся из неё, как в F25k |

Нового состояния правка не вводит. Лямбда без захвата вызывается один раз; выход `InitAsync` не меняется.

## Тесты (`run_tests_fs10a.py`)

База — та же сборка worktree на `11164d72` до cherry-pick (`shader_cfg_tests` 03:21:50–03:22:41Z, прогон 03:23:17–03:23:19Z); FS10 — после
(сборка 03:24:43–03:25:18Z, прогон 03:25:19–03:26:12Z); все `KYTY_*` сняты. sha256: `log_async_tests.exe` `81475bdb…`,
`shader_cfg_tests.exe` FS10 `4e5dc066…`. Вывод — `runs/log_tests_fs10.txt` (`ALL OK`). Список HANDOFF §4 «14 известных падений» на этом дереве
не воспроизводится — 0 падений у базы и у FS10, как у FS9a и F25k2.

## Ход (UTC)

- `03:17:49Z` — первая команда (проверка замка); `03:19:17Z` — строка начала в `times.txt`; `03:19:59Z` — коммит `7f34b1e2`.
- `03:20:39Z` — проверка API; `03:20:40–03:20:50Z` — `mk_wt_fs10a.sh` (worktree, подмодули архивом).
- `03:20:58–03:21:39Z` — configure; `03:21:40–03:21:43Z` — версия базы; `03:21:50–03:22:41Z` — `shader_cfg_tests` базы; `03:23:17–03:23:19Z` — тест базы.
- `03:23:32–03:23:37Z` (mtime `cp_*.log`) — cherry-pick 1–5; `check_gate_order.py` на worktree.
- `03:23:47–03:24:22Z` — сборка `kyty_emulator`; `03:24:22–03:24:25Z` — версия FS10; `03:24:34–03:24:37Z` — повтор сборки (нет изменений).
- `03:24:43–03:25:18Z` — сборка `shader_cfg_tests`, `log_async_tests`; `03:25:19–03:26:12Z` — тесты FS10; `03:27:38Z` — копия бинаря; sha256
  установленного — `3861eeea…`.

Флаги сборки = FS9a (`build_fs10a.cmd` — копия `build_fs9a.cmd` с путями `fs10a`); Release, clang-cl, LTO.

## Файлы

`C:/kyty/f287/fs10a/`, копии в `docs/track-f/fs10a/` (текстовые — LF):
- **Скрипты:** `patch_fs10a.py`, `mk_wt_fs10a.sh`, `cp_fs10a.sh`, `build_fs10a.cmd`, `bstep.sh`, `sstep.sh`, `api_chk.sh`, `watch_fs10a.py`,
  `hdr_fs10a.py` (строка истории скопированных скриптов), `run_tests_fs10a.py`, `verify_fs10a.py`.
- **Выводы:** `patch_main.out.txt`, `gate_order_main.out.txt`, `gate_order_wt.out.txt`, `mk_wt.log`, `cp_1.log`, `cp_b4ee756a.log`,
  `cp_0e4b2f5a.log`, `cp_5064c5bb.log`, `cp_7f34b1e2.log`, `tests/base/` и `tests/fs10/` (без `spv/`), `runs/log_*.txt`, `verify_fs10a.out.txt`,
  `binary_fs10a.txt`, `binary_sha.txt`, `kytyGitVersion_fs10.h`, `base/kytyGitVersion_base.h`, `commit_msg_code.txt`.

В копии `cp_fs10a.sh` адрес агента заменён на `<agent-email>` (общее правило 28); в `mk_wt_fs10a.sh` адреса нет.

## Не заявляется

П. 624(л) и п. 613(и) целиком; в частности: что FS10 работает в игре (дыма не было, до FS10c); что FS10 установлен (до FS10d); что выводы
о T2 переносятся на FS10 до FS10c; что путь `=1` FS10 по машинному коду равен пути T2 (отличие состава — нет кода `KYTY_DIAG_B32`; сверка —
FS10b); что K2 Б36, Б40 на пути пользователя есть или нет; что настоящие задержки файловой системы бывают на пути пользователя; что набор
тестов полон; что реестр полон; ни одно число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется.
