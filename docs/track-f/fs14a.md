# FS14a (`HPP-812`, Emu Engineer): четырнадцатый бинарь отгрузки трека F (FS14) — умолчание `KYTY_FIX_F24=1`

Задание — `ROADMAP.md` «СЕССИЯ 122» п. 710(г)(1) (KytyPS5 `5b774c83`, якорь «(г) **Отгрузка FS14 — константы лида.** (1) **FS14a
(Emu Engineer, без замка и без игры).**»); вывод — п. 710(в); образец — FS13a п. 697(г)(1), отчёт `docs/track-f/fs13a.md`; правило базы —
п. 410(г)(6)(i), 703(г). Игра не запускалась; установленный `ps5 em/kyty_emulator.exe` — FS13 `abab2196…` до и после звена,
`C:/kyty/build/install`, `C:/kyty/build` и кэши не тронуты. Время — UTC по `date -u`, события — `C:/kyty/f287/times.txt` (строки `FS14a`).
Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно. Замка `C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` за звено не
было (каждая команда начиналась проверкой); шаги сборки и тестов шли под сторожем `watch_fs14a.py` (п. 431(в)(1)) со строкой API перед
каждым; с 12:17:16Z в `in_progress` — звено серии `HPP-800` (F46c), замка на шагах звена не было, сторож не срабатывал. Ссылок
`<коммит>:<путь>:<строка>` отчёт не несёт (места названы по функциям и файлам). **WIP по дыму: бинарь собран и проверен тестами без игры,
игрой не проверялся** (теги — FS14c после FS14b).

## Итог

- **Коммит в `main`: `c8836f14`** (`--only`, 2 файла: `src/graphics/presentation/window/joyPump.cpp` +4/−1, `joyPump.h` +4/−2): умолчание
  `KYTY_FIX_F24` 0 → 1 в форме FS13a `3630f116` / FS12a `cbfe8375` (не задана или `""` — 1; иначе `Common::EnvValueOn`).
- **Worktree `C:/kyty/f287/fs14a/wt`, HEAD `76c1058f`** — база FS13 `ea6c6e9e` (worktree FS13a, установленный FS13 `abab2196`, п. 703–704;
  другого принятого лидом бинаря отгрузки нет) + cherry-pick `-x`:

  | Шаг | Источник | Коммит в worktree | Конфликт |
  |---|---|---|---|
  | 1 | `5c21c387` (F40a: код `KYTY_FIX_F24`) | `b50e90e8` | нет |
  | 2 | `e3aa4b4d` (F40a: стенд `KYTY_TEST_HIDLOSS` издания 2) | `cd422a94` | нет |
  | 3 | `57f9e528` (F40a2: свидетель `init_owner`, поля `flap`) | `6eb0f1a1` | нет |
  | 4 | `c8836f14` (FS14a) | `76c1058f` | нет |

  Конфликтов нет; `git status --short` — 0 строк после каждого шага, CR в `src/` — 0 [c `cp_*.log`, `mk_wt.log`]. Зависимости от кода
  вне базы нет: сборка `kyty_emulator` и `shader_cfg_tests` прошла.
- **Бинарь FS14: sha256 `826fc0a0fb93aac9f0620baa7a411d3d0adbdc2fa9464bb2c2a7d9044cfa369e`**, копия
  `C:/kyty/f287/bin/kyty_emulator_826fc0a0.exe` (+ `.sha256`; `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe`). Строка версии
  `KytyPS5-2026-09-15-6a2987a-1923-g76c1058f`. **Не установка.**
- Члены п. 710(г)(1):

  | Член | Итог | Источник |
  |---|---|---|
  | «бинарь содержит» `5c21c387`, `57f9e528`, коммит FS14a, `e9dd8604`, `3630f116`, `227e1b36`, `cbfe8375`, `c94c49e0`, `726e751e`, `cb022252` — «предок или `git cherry` `-`», счёт скриптом с отрицательным контролем | ✓ у всех десяти `git cherry` `-` (предками FS14 не являются — все перенесены cherry-pick: три F40 и FS14a — этим звеном, `e9dd8604`, `3630f116` — FS13a, `227e1b36`, `cbfe8375` — FS12a, три остальных — FS11a); изменённые строки переносов этого звена равны источникам (629, 445, 140, 11). Отрицательные контроли — то же правило говорит «нет» (`+`): `5c21c387`, `57f9e528`, `c8836f14` в базе `ea6c6e9e`; `e9dd8604`, `3630f116` в FS12 `730ed40a`; код Ф20 `a6342c98` в FS14; строки `e3aa4b4d` против переноса `5c21c387` и строки `57f9e528` против своего переноса с одной испорченной строкой — не равны | `verify_fs14a.out.txt` V1, V1b |
  | дифф `src/` FS14 против базы FS13 — только файлы трёх коммитов F40 и FS14a (`git diff --stat`), путей `src/graphics/shader/**` 0 | ✓ 6 путей = объединению файлов четырёх коммитов (`hostInput.cpp`, `joyPump.cpp`, `joyPump.h`, `vulkanWindow.cpp`, `window.cpp` в `src/graphics/presentation/window/` и `src/libs/controller.cpp`), путей вне `src/` 0, под `src/graphics/shader/` 0; знаковое мультимножество изменённых строк = сумме четырёх (1 207 строк), без FS14a — не равно | V2, V2b |
  | подпись трансляции (`KYTY_SHADER_SOURCE_HASH`) = базе `9177b426…` | ✓ `9177b4267de1fb8bac7d1113afd8733210addfac` у FS14 = `kytyGitVersion_fs13.h` FS13a; в exe ×1 у FS14 и у FS13 | `kytyGitVersion_fs14.h`, `binary_fs14a.txt` |
  | `shader_cfg_tests` — строки `failed` и счёт = базе FS13 | ✓ против прогона FS13a сборки FS13 `ea6c6e9e` (`C:/kyty/f287/fs13a/tests/fs13`): rc 0 / 0, `[test]` 133 / 133, `ShaderCfgTests: failed:` 0 / 0, строк со словом `failed` 5 / 5, мультимножество равно; справка t4: SPIR-V 360 / 360 байт в байт (агрегат `b1376644` = FS13a) | `tests/fs14/`, `runs/log_tests_cfg.txt` |
  | `check_gate_order.py` — clean | ✓ `GATE ORDER: clean` на `main` после правки и на worktree до сборки (`C:/kyty/s113/check_gate_order.py --src …`); выводы (без строки заголовка, без учёта CR) равны выводам FS13a — гейтов и ручек правка не добавляет | `gate_order_main.out.txt`, `gate_order_wt.out.txt` |
  | таблица умолчаний своим сканером — база FS13 плюс `KYTY_FIX_F24` (и только он) | ✓ 18 → 19; отрицательный контроль на `6eb0f1a1` (до FS14a) — разность пуста, член там не выполнен | V3 |
  | `KYTY_S_REPLAY` = 3 | ✓ blob `shaderReplay.cpp` базы = FS14 (`e1626ad6…`), `ParseMode` не задана / `""` → 3 | V4 |
  | в бинаре по одной строке формата `FixF24: init_owner` и `TestHidLoss: f24` | ✓ ×1 и ×1 у FS14, ×0 и ×0 у FS13 | `binary_fs14a.txt` |
  | sha256 и копия `C:/kyty/f287/bin/kyty_emulator_<sha8>.exe`, не установка | ✓ `kyty_emulator_826fc0a0.exe`; установленный `abab2196…` до и после | `binary_sha.txt`, `times.txt` |
  | диагностики вне базы в бинарь не входят | ✓ добавленных строк кода с `KYTY_FIX_F20` / `FixF20` / `F20Stand` / `KYTY_F26_TINT` / `KYTY_FIX_F26` / `KYTY_FIX_F29` / `KYTY_DIAG_B32` / `rts_bad_b` 0; `a6342c98` (код Ф20), `1398d44d` (измерение F46a), `82570fd2` (стенд Ф20 издания 2) — не предки, `git cherry` `+`; в exe `KYTY_FIX_F20`, `KYTY_DIAG_B32`, `rts_bad_b` ×0 | V6, `binary_fs14a.txt` |

## Код (`c8836f14`, в worktree — `76c1058f`)

`src/graphics/presentation/window/joyPump.cpp`, `JoyPump::ReadKnob`:

```cpp
void ReadKnob() {
	static std::atomic<bool> done {false};
	if (done.exchange(true)) {
		return;
	}
	// Track F, FS14a (HPP-812, ROADMAP s122 item 710(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any
	// other value as EnvValueOn (the form of FS13a 3630f116 / FS12a cbfe8375).
	const char* value = std::getenv("KYTY_FIX_F24");
	g_enabled.store(value == nullptr || value[0] == '\0' || Common::EnvValueOn(value), std::memory_order_release);
	LOGF("FixF24: mode=%d b24=%d\n", Enabled() ? 1 : 0, Controller::FixB24On() ? 1 : 0);
}
```

- До FS14a: `g_enabled.store(Common::EnvFlagOn("KYTY_FIX_F24"), std::memory_order_release);` — не задана = 0. В `joyPump.h` два
  комментария, называвшие умолчание 0 («Default 0: nothing here runs …» и «(Common::EnvFlagOn, default 0)»), заменены на «At 0 (default 1
  since FS14a - ReadKnob below): …» и «(track F, FS14a, HPP-812, ROADMAP s122 item 710(g)(1): default 1 - unset or "" = ON, 0/false/off/no =
  OFF, any other value as EnvValueOn)»; прочий текст F40a не тронут.
- Одно чтение сохранено: `ReadKnob` — главный поток, `WindowCreate` до инициализации SDL (вызов в `window.cpp` не изменён); повторные вызовы
  выходят по `done` [c]. Читатели `g_enabled` — `JoyPump::Enabled()` без изменений.
- `std::getenv` — из `<cstdlib>`, уже включённого через `common/envFlag.h` (включение в `joyPump.cpp` с F40a).
- Строка `FixF24: mode=<0|1> b24=<0|1>` печатается по значению, как в F40a: без переменной теперь `mode=1` [I по коду; в игре — FS14c].
- Пути по коду [c]: без переменной, `""`, `1/true/on/yes` — 1; `0/false/off/no` — 0 (путь `=0` по коду = база FS13 плюс чтение ручки и строка
  `FixF24: mode=0 b24=<…>` — п. 692(г)(2); сверка — FS14b).
- `src/graphics/shader/**` не тронут — подпись трансляции не меняется; гейтов и ручек правка не добавляет.

## Состояние, вводимое правкой

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `g_enabled` (атомарный флаг пространства имён `JoyPump`) | один раз — в `ReadKnob` (главный поток, `WindowCreate` до инициализации SDL); второй и далее вызовы выходят по `done` до записи | не снимается (время жизни процесса) | как в F40a `5c21c387`; меняется только выражение значения |
| `value` (локальная `const char*` в `ReadKnob`) | на строке `std::getenv` | конец `ReadKnob` | локальная, не переживает вызов; единственный выход после неё — конец функции |

Нового состояния с жизненным циклом правка не вводит; выходов функции не прибавилось (ранний выход `done` — до установки `value`).

## Тесты (`run_tests_fs14a.py`)

Сборка FS14 (worktree `76c1058f`): `shader_cfg_tests.exe` (sha256 — `tests/fs14/exe_sha256.txt`); все `KYTY_*` сняты, кроме
`KYTY_TESTS_CONTINUE`, `KYTY_TESTS_VERBOSE`, `KYTY_TESTS_SPV_DIR`. База — прогон FS13a сборки FS13 `ea6c6e9e`
(`C:/kyty/f287/fs13a/tests/fs13`); своей сборки базы звено не делало (форма FS13a). Список HANDOFF §4 «14 известных падений» на этом
дереве не воспроизводится — 0 падений `ShaderCfgTests` у FS13 и FS14, как у FS13a. `kernel_file_system_tests` и стенды не гонялись:
п. 710(г)(1) их не называет; стенд `KYTY_TEST_HIDLOSS` идёт только в игре (F40c).

## Ход (UTC)

- `12:12:38Z` — первая команда (проверка замка); `12:14:54Z` — коммит `c8836f14` и `check_gate_order.py` на `main` (`GATE ORDER: clean`).
- после `12:14:54Z`, конец `12:15:19Z` (строка `date -u` команды) — `mk_wt_fs14a.sh` (worktree на `ea6c6e9e`, подмодули архивом) и cherry-pick 1–4; `12:15:28Z` — `check_gate_order.py`
  на worktree (`GATE ORDER: clean`).
- `12:15:36–12:17:02Z` — configure; `12:17:09–12:17:14Z` — версия; `12:17:18–12:18:38Z` — `kyty_emulator`; `12:18:50–12:19:27Z` —
  `shader_cfg_tests`; `12:19:29Z` — копия бинаря, sha256 установленного — `abab2196…`.
- `12:20:07–12:20:10Z` — тесты; `12:20:11Z` — `binary_fs14a.py` `ALL OK`; затем `verify_fs14a.py` `ALL OK`.

Флаги сборки = FS13a (`build_fs14a.cmd` — копия `build_fs13a.cmd` с путями `fs14a`); Release, clang-cl, LTO. Скрипты сборки, worktree,
cherry-pick, API и сторожа — копии FS13a с заменой `fs13a` → `fs14a`, `FS13a` → `FS14a`, `HPP-787` → `HPP-812` (`mk_wt_fs14a.sh`: база по
умолчанию `ea6c6e9e`); комментарии в их заголовках остались от предшественников, исполняемые строки — по заменам.

## Для FS14b (справка, не член FS14a)

V7 `verify_fs14a.out.txt`: пути `src/` диффа worktree тега F40a2 `7c38e497` → FS14 — `src/kernel/fileSystem.cpp` (коммиты FS13
`e9dd8604`, `3630f116`) и `joyPump.cpp` / `joyPump.h` (FS14a) [c]; иных нет.

## Файлы

`C:/kyty/f287/fs14a/`, копии в `docs/track-f/fs14a/` (текстовые — LF; `build/`, `wt/` и SPIR-V тестов — только локально):
- **Скрипты:** `patch_fs14a.py`, `mk_wt_fs14a.sh`, `cp_fs14a.sh`, `build_fs14a.cmd`, `bstep.sh`, `sstep.sh`, `api_chk.sh`, `watch_fs14a.py`,
  `run_tests_fs14a.py`, `verify_fs14a.py`, `binary_fs14a.py`, `append_facts.py`.
- **Выводы:** `gate_order_main.out.txt`, `gate_order_wt.out.txt`, `verify_fs14a.out.txt`, `binary_fs14a.txt`, `binary_sha.txt`,
  `kytyGitVersion_fs14.h`, `mk_wt.log`, `cp_*.log`, `build_*.log`, `runs/log_tests_cfg.txt`, `tests/fs14/{log,rc,exe_sha256}.txt`,
  `commit_msg_code.txt`, `facts_fs14a.md`.

## Не заявляется

П. 710(з) целиком: в частности, что FS14 установлен (до FS14d); что настоящий пульт хоста на `JoyPump` работает (пультов хоста в тегах нет);
что Ф24 случается у пользователя; что прочие 40 `SCENE_OK` держатся на FS14; бинарь FS14 игрой не запускался — путь по умолчанию в игре
не проверен (FS14c); ни одно число — не выигрыш.
