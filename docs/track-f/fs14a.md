# FS14a (`HPP-812`, Emu Engineer): четырнадцатый бинарь отгрузки трека F (FS14) — умолчания `KYTY_FIX_F24=1` и `KYTY_FIX_F29=1`

Задание — `ROADMAP.md` «СЕССИЯ 122» п. 710(г)(1) (KytyPS5 `5b774c83`, якорь «(г) **Отгрузка FS14 — константы лида.** (1) **FS14a
(Emu Engineer, без замка и без игры).**») с поправкой п. 712(г)(1) (KytyPS5 `e4777abb`: Ф29 входит в FS14, FS15 нет); вывод — п. 710(в);
образец — FS13a п. 697(г)(1), отчёт `docs/track-f/fs13a.md`; правило базы — п. 410(г)(6)(i), 703(г). Игра не запускалась; установленный
`ps5 em/kyty_emulator.exe` — FS13 `abab2196…` до и после звена, `C:/kyty/build/install`, `C:/kyty/build` и кэши не тронуты. Время — UTC
по `date -u`, события — `C:/kyty/f287/times.txt` (строки `FS14a`). Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно.
Замка `C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` за звено не было (каждая команда начиналась проверкой); шаги сборки, тестов и стенда
шли под сторожем `watch_fs14a.py` (п. 431(в)(1)) со строкой API перед каждым; с 12:17:16Z в `in_progress` — звено серии `HPP-800` (F46c),
замка на шагах звена не было, сторож не срабатывал. Ссылок `<коммит>:<путь>:<строка>` отчёт не несёт (места названы по функциям и файлам).
**WIP по дыму: бинарь собран и проверен тестами и стендом без игры, игрой не проверялся** (теги — FS14c после FS14b).

Издание 2 отчёта: издание 1 (`20b7693a`) вышло без поправки п. 712(г)(1) — review лида «Доработать»; Ф24-часть издания 1 принята как есть
и перенесена сюда; бинарь издания 1 `826fc0a0` — промежуточный (только Ф24), в FS14 не идёт.

## Итог

- **Коммиты в `main`** (`--only`):
  - **`c8836f14`** (2 файла: `src/graphics/presentation/window/joyPump.cpp` +4/−1, `joyPump.h` +4/−2): умолчание `KYTY_FIX_F24` 0 → 1 в
    форме FS13a `3630f116` / FS12a `cbfe8375` (не задана или `""` — 1; иначе `Common::EnvValueOn`);
  - **`78e45af3`** (2 файла: `src/graphics/host_gpu/renderer/cache/faultManager.cpp` +6/−1, `faultManager.h` +2/−1): умолчание
    `KYTY_FIX_F29` 0 → 1 в той же форме (раздел «Ф29»).
- **Worktree `C:/kyty/f287/fs14a/wt`, HEAD `eb7e8b91`** — база FS13 `ea6c6e9e` (worktree FS13a, установленный FS13 `abab2196`, п. 703–704;
  другого принятого лидом бинаря отгрузки нет) + cherry-pick `-x`:

  | Шаг | Источник | Коммит в worktree | Конфликт |
  |---|---|---|---|
  | 1 | `5c21c387` (F40a: код `KYTY_FIX_F24`) | `b50e90e8` | нет |
  | 2 | `e3aa4b4d` (F40a: стенд `KYTY_TEST_HIDLOSS` издания 2) | `cd422a94` | нет |
  | 3 | `57f9e528` (F40a2: свидетель `init_owner`, поля `flap`) | `6eb0f1a1` | нет |
  | 4 | `c8836f14` (FS14a: умолчание Ф24) | `76c1058f` | нет |
  | 5 | `15c9d2f2` (F44a: код `KYTY_FIX_F29` и стенд `f29_fault_stand`) | `c5eb48b0` | нет |
  | 6 | `78e45af3` (FS14a: умолчание Ф29) | `eb7e8b91` | нет |

  Конфликтов нет, в том числе в строках целей стендов `CMakeLists.txt` (цель `f29_fault_stand` из `15c9d2f2` легла без правки; иных
  целей стендов F40 в `CMakeLists.txt` нет — стенд `KYTY_TEST_HIDLOSS` живёт в `window.cpp`); `git status --short` — 0 строк после каждого
  шага [c `cp_*.log`, `mk_wt.log`]. Зависимости от кода вне базы нет: сборка `kyty_emulator`, `shader_cfg_tests` и `f29_fault_stand` прошла.
- **Бинарь FS14 (итоговый): sha256 `013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd`**, копия
  `C:/kyty/f287/bin/kyty_emulator_013e1974.exe` (+ `.sha256`). Строка версии `KytyPS5-2026-09-15-6a2987a-1925-geb7e8b91`. **Не установка.**
- **Промежуточный бинарь (только Ф24, worktree `76c1058f`, издание 1): sha256 `826fc0a0fb93aac9f0620baa7a411d3d0adbdc2fa9464bb2c2a7d9044cfa369e`**,
  копия `C:/kyty/f287/bin/kyty_emulator_826fc0a0.exe` — **в FS14 не идёт**, FS14b/FS14c его не берут.
- Члены п. 710(г)(1) с п. 712(г)(1) — на итоговом бинаре `013e1974` / worktree `eb7e8b91`:

  | Член | Итог | Источник |
  |---|---|---|
  | «бинарь содержит» `5c21c387`, `57f9e528`, `c8836f14`, `15c9d2f2`, `78e45af3`, `e9dd8604`, `3630f116`, `227e1b36`, `cbfe8375`, `c94c49e0`, `726e751e`, `cb022252` — «предок или `git cherry` `-`», счёт скриптом с отрицательным контролем | ✓ у всех двенадцати `git cherry` `-` (предками FS14 не являются — все перенесены cherry-pick: три F40, `15c9d2f2` и два коммита FS14a — этим звеном, `e9dd8604`, `3630f116` — FS13a, `227e1b36`, `cbfe8375` — FS12a, три остальных — FS11a); изменённые строки переносов этого звена равны источникам (629, 445, 140, 11, 1 028, 10). Отрицательные контроли — то же правило говорит «нет» (`+`): `5c21c387`, `57f9e528`, `c8836f14`, `15c9d2f2`, `78e45af3` в базе `ea6c6e9e`; `15c9d2f2`, `78e45af3` в промежуточном `76c1058f`; `e9dd8604`, `3630f116` в FS12 `730ed40a`; код Ф20 `a6342c98` в FS14; строки `e3aa4b4d` против переноса `5c21c387`, строки `57f9e528` против своего переноса с одной испорченной строкой, строки `15c9d2f2` против переноса `78e45af3` — не равны | `verify_fs14a_f29.out.txt` V1, V1b |
  | дифф `src/` FS14 против базы FS13 — файлы F40, `faultManager.cpp`/`.h`, коммиты FS14a и только они; путей `src/graphics/shader/**` 0 | ✓ 8 путей `src/` = файлам трёх коммитов F40 и FS14a (`hostInput.cpp`, `joyPump.cpp`, `joyPump.h`, `vulkanWindow.cpp`, `window.cpp` в `src/graphics/presentation/window/`, `src/libs/controller.cpp`) плюс `src/graphics/host_gpu/renderer/cache/faultManager.cpp`, `faultManager.h`; под `src/graphics/shader/` 0. Вне `src/` — 4 пути, все из `15c9d2f2`: `CMakeLists.txt` (+6, цель `f29_fault_stand`, `EXCLUDE_FROM_ALL`), `tests/F29FaultStand.cpp`, `docs/track-f/f44a/gate_order_main.out.txt`, `docs/track-f/f44a/patch_f44a.py` — в `kyty_emulator` не входят. Знаковое мультимножество изменённых строк = сумме шести коммитов (2 239 строк), без `78e45af3` — не равно | V2, V2b |
  | подпись трансляции (`KYTY_SHADER_SOURCE_HASH`) = базе `9177b426…` | ✓ `9177b4267de1fb8bac7d1113afd8733210addfac` у итогового FS14 = промежуточному = FS13a; в exe ×1 у FS14 и у FS13 | `kytyGitVersion_fs14_f29.h`, `binary_fs14a_f29.txt` |
  | `shader_cfg_tests` — строки `failed` и счёт = базе FS13 | ✓ сборка worktree `eb7e8b91` против прогона FS13a сборки FS13 `ea6c6e9e` (`C:/kyty/f287/fs13a/tests/fs13`): rc 0 / 0, `[test]` 133 / 133, `ShaderCfgTests: failed:` 0 / 0, строк со словом `failed` 5 / 5, мультимножество равно; справка t4: SPIR-V 360 / 360 байт в байт (агрегат `b1376644` = FS13a) | `tests/fs14_f29/`, `runs/log_tests_cfg_f29.txt` |
  | `check_gate_order.py` — clean | ✓ `GATE ORDER: clean` на `main` после `78e45af3` и на worktree `eb7e8b91` до сборки (`C:/kyty/s113/check_gate_order.py --src …`); вывод на `main` (без строки заголовка, без учёта CR) равен выводу издания 1 — гейтов и ручек правка не добавляет | `gate_order_main_f29.out.txt`, `gate_order_wt_f29.out.txt` |
  | таблица умолчаний своим сканером — база FS13 плюс `KYTY_FIX_F24` и `KYTY_FIX_F29` (и только они) | ✓ 18 → 20; отрицательные контроли — на промежуточном `76c1058f` и на переносе `15c9d2f2` (`c5eb48b0`) разность только `KYTY_FIX_F24`, член там не выполнен | V3 |
  | `KYTY_S_REPLAY` = 3 | ✓ blob `shaderReplay.cpp` базы = FS14 (`e1626ad6…`), `ParseMode` не задана / `""` → 3 | V4 |
  | в бинаре по одной строке формата `FixF24: init_owner`, `TestHidLoss: f24` и `FixF29: mode=` | ✓ ×1, ×1, ×1 у FS14; ×0, ×0, ×0 у FS13; в исходнике FS14 — `getenv("KYTY_FIX_F29")` ×1, формат `"FixF29: mode=%d` ×1, чтение в форме `3630f116` (V3b) | `binary_fs14a_f29.txt`, V3b |
  | стенд `f29_fault_stand` своей сборкой, процесс без переменной `KYTY_FIX_F29`, `R` = 20 — члены P1 п. 698(д)(1); контроль `KYTY_FIX_F29=0` — P0 (O1 `out_area` 77, O7 `out_buf` 77) 20 из 20 | ✓ `ALL OK` (раздел «Ф29», «Стенд»); об оговорке к строке `FixF29: mode=1` — там же | `stand_f29/`, `runs/log_stand_f29.txt`, `stand_f29_counts.txt` |
  | sha256 и копия `C:/kyty/f287/bin/kyty_emulator_<sha8>.exe`, не установка | ✓ `kyty_emulator_013e1974.exe`; установленный `abab2196…` до и после | `binary_sha_f29.txt`, `times.txt` |
  | диагностики вне базы в бинарь не входят | ✓ добавленных строк кода с `KYTY_FIX_F20` / `FixF20` / `F20Stand` / `KYTY_F26_TINT` / `KYTY_FIX_F26` / `KYTY_DIAG_B32` / `rts_bad_b` 0; `a6342c98` (код Ф20), `1398d44d` (измерение F46a), `82570fd2` (стенд Ф20 издания 2) — не предки, `git cherry` `+`; в exe `KYTY_FIX_F20`, `KYTY_DIAG_B32`, `rts_bad_b` ×0 | V6, `binary_fs14a_f29.txt` |

## Ф24: код (`c8836f14`, в worktree — `76c1058f`)

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
  комментария, называвшие умолчание 0, заменены на текст об умолчании 1 (FS14a, п. 710(г)(1)); прочий текст F40a не тронут.
- Одно чтение сохранено: `ReadKnob` — главный поток, `WindowCreate` до инициализации SDL (вызов в `window.cpp` не изменён); повторные вызовы
  выходят по `done` [c]. Читатели `g_enabled` — `JoyPump::Enabled()` без изменений.
- Строка `FixF24: mode=<0|1> b24=<0|1>` печатается по значению, как в F40a: без переменной теперь `mode=1` [I по коду; в игре — FS14c].
- Пути по коду [c]: без переменной, `""`, `1/true/on/yes` — 1; `0/false/off/no` — 0 (путь `=0` по коду = база FS13 плюс чтение ручки и
  строка `FixF24: mode=0 b24=<…>` — п. 692(г)(2); сверка — FS14b).

## Ф29 (поправка п. 712(г)(1))

### Код (`78e45af3`, в worktree — `eb7e8b91`; код и стенд F44a — `15c9d2f2`, в worktree — `c5eb48b0`)

`src/graphics/host_gpu/renderer/cache/faultManager.cpp`, `FixF29Enabled`:

```cpp
// Track F, FS14a (HPP-812, ROADMAP s122 item 712(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any
// other value as EnvValueOn (the form of FS13a 3630f116); still one reading per process.
bool FixF29Enabled() {
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_FIX_F29");
		return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);
	}();
	return enabled;
}
```

- До FS14a (F44a `15c9d2f2`): `static const bool enabled = Common::EnvValueOn(std::getenv("KYTY_FIX_F29"));` — не задана = 0. Форма —
  дословно `FixF25Enabled` FS13a `3630f116` (лямбда со `static const`).
- Одно чтение на процесс: `static const` инициализируется при первом вызове (C++11 — потокобезопасно); первый вызов — конструктор
  `FaultManager` (строка `FixF29: mode=%d`), затем отложенная операция `ProcessFaultBuffer` (номер прохода и `clamp`) [c `15c9d2f2`].
- Строка `FixF29: mode=<0|1>` (конструктор `FaultManager`) не изменена и печатается по значению: без переменной — `mode=1` [I по коду; в
  игре — FS14c].
- `faultManager.h`: комментарий у объявления `FixF29Enabled` «(default 0): … (EnvValueOn: unset/""/0/false/off/no - off)» заменён на
  «(default 1 since FS14a, HPP-812, ROADMAP s122 item 712(g)(1)) … (unset or "" - on; 0/false/off/no - off; any other value as
  EnvValueOn)».
- `std::getenv` — `<cstdlib>` через `common/envFlag.h` (включение с F44a). `src/graphics/shader/**` не тронут, `fault_buffer_process.comp`
  не тронут — подпись трансляции не меняется; гейтов и ручек правка не добавляет.

### Состояние, вводимое правкой Ф29

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `enabled` (`static const bool` функции `FixF29Enabled`) | один раз — при первом вызове `FixF29Enabled` (конструктор `FaultManager`, у стенда — `main` до первого плеча) | не снимается (время жизни процесса) | как в F44a `15c9d2f2`; меняется только выражение значения |
| `value` (локальная `const char*` лямбды) | на строке `std::getenv` | конец лямбды | локальная, не переживает вызов; единственный выход — `return` |

Нового состояния с жизненным циклом правка не вводит; выходов функции не прибавилось.

### Стенд (`f29_fault_stand`, сборка worktree `eb7e8b91`)

Константы — комментарием в звене до данных (12:32:49Z, комментарий `057803ec`): exe `C:/kyty/f287/fs14a/build/f29_fault_stand.exe`
(sha256 `12c4b09f…`), **зерно 71201, `R` = 20**; порядок — процесс контроля `KYTY_FIX_F29=0`, затем процесс **без переменной** (удалена из
окружения процесса); порядок плеч внутри повтора — splitmix64 зерна (код стенда). Драйвер и ридер — `run_stand_fs14a.py` = копия
`run_stand_f44a.py` (F44a) с правками: у процесса 1 переменная удаляется, ожидается `FIXF29 env=(unset) on=1`; читатели членов без
изменений. Шаг — под сторожем (`sstep.sh stand_f29`), 12:33:05–12:33:49Z.

| Член | `=0` (контроль) | без переменной |
|---|---|---|
| стандартный вывод | `FIXF29 env=0 on=0`, `DONE rows=160` | `FIXF29 env=(unset) on=1`, `DONE rows=160` |
| строки 20 × 8 плеч, нулевые инварианты, тождества, G1, G2 | PASS (160; 800; 960; 220; 140) | PASS (160; 800; 960; 220; 140) |
| P0: O1 `out_area` 77 (1 + 76), O7 `out_buf` 77 / `exit` 77, E1 1, L `low` ≥ 1 | PASS 80 из 80; **O1 `out_area` = 77 — 20 из 20, O7 `out_buf` = 77 — 20 из 20** | — |
| P1 п. 698(д)(1): 0 чтений за областью и за буфером, `read` 1 023 при переполнении | — | PASS 0 из 640; `out_area` = `out_buf` = 0 у 160 из 160 строк; O1 77 — 0 из 20, O7 77 — 0 из 20 |
| строки `FixF29: overflow` | 0 | 32 = min(32, 100), поля верны |
| H (S0–S2 одинаковы при обоих значениях и ожиданию; E1/O1/D1 `h_inproc`) | PASS 120 из 120; `h_inproc` 320 из 320 | |

Итог стенда — `ALL OK` [c `runs/log_stand_f29.txt`, `stand_f29_counts.txt`].

**Оговорка к члену «строка `FixF29: mode=1`» [c]:** строку `FixF29: mode=` печатает только конструктор `FaultManager`; стенд его не
создаёт (зовёт `ParseFaultArea` и `FixF29Enabled` напрямую), поэтому в выводе и логе стенда этой строки нет ни у `=0`, ни у процесса без
переменной (в логе стенда F44a её тоже нет). Значение ручки процесса стенд печатает своей строкой `FIXF29 env=(unset) on=1` из той же
функции `FixF29Enabled`, что питает `FixF29: mode=` в эмуляторе; формат `FixF29: mode=` в exe FS14 — ×1. Сама строка `FixF29: mode=1`
в логе — у первого запуска эмулятора без переменной (FS14c). Читать ли член по строке стенда — решение review лида.

## Тесты (`run_tests_fs14a_f29.py`)

Сборка итогового FS14 (worktree `eb7e8b91`): `shader_cfg_tests.exe` (sha256 — `tests/fs14_f29/exe_sha256.txt`); все `KYTY_*` сняты, кроме
`KYTY_TESTS_CONTINUE`, `KYTY_TESTS_VERBOSE`, `KYTY_TESTS_SPV_DIR`. База — прогон FS13a сборки FS13 `ea6c6e9e`
(`C:/kyty/f287/fs13a/tests/fs13`); своей сборки базы звено не делало (форма FS13a). Список HANDOFF §4 «14 известных падений» на этом
дереве не воспроизводится — 0 падений `ShaderCfgTests` у FS13 и FS14, как у FS13a. Прогон издания 1 (`tests/fs14/`, worktree `76c1058f`)
— тот же итог. Стенд `KYTY_TEST_HIDLOSS` идёт только в игре (F40c).

## Ход (UTC)

Издание 1:
- `12:12:38Z` — первая команда; `12:14:54Z` — коммит `c8836f14`, `check_gate_order.py` на `main` clean; до `12:15:19Z` — worktree и
  cherry-pick 1–4; `12:15:28Z` — `check_gate_order.py` на worktree clean.
- `12:15:36–12:19:27Z` — configure, версия, `kyty_emulator`, `shader_cfg_tests`; `12:19:29Z` — промежуточный бинарь `826fc0a0`;
  `12:20:07–12:20:11Z` — тесты, `binary_fs14a.py`, `verify_fs14a.py` `ALL OK`; `12:23:35Z` — коммит отчёта `20b7693a`.
- Поправка лида п. 712(г)(1) — `12:19:17Z` (до отчёта издания 1), review лида «Доработать» — `12:24:52Z`.

Издание 2:
- `12:25:21Z` — первая команда хартбита; коммит `78e45af3` и `check_gate_order.py` на `main` clean (строка `times.txt` после коммита).
- cherry-pick `15c9d2f2` → `c5eb48b0`, `78e45af3` → `eb7e8b91`, `check_gate_order.py` на worktree clean.
- `12:27:15–12:27:27Z` — configure; `12:27:30–12:27:34Z` — версия; `12:27:41–12:28:07Z` — `kyty_emulator`; `12:28:16–12:28:40Z` —
  `shader_cfg_tests`; `12:28:42–12:29:16Z` — `f29_fault_stand`; затем копия итогового бинаря `013e1974`.
- `verify_fs14a_f29.py` `ALL OK`, `binary_fs14a_f29.py` `ALL OK`; `12:31:51–12:31:53Z` — тесты `ALL OK`; `12:32:49Z` — константы стенда
  комментарием; `12:33:05–12:33:49Z` — стенд `ALL OK`.

Флаги сборки = FS13a (`build_fs14a.cmd` — копия `build_fs13a.cmd` с путями `fs14a`); Release, clang-cl, LTO.

## Для FS14b (справка, не член FS14a)

V7 `verify_fs14a_f29.out.txt`: пути `src/` диффа worktree тега F40a2 `7c38e497` → FS14 — `src/kernel/fileSystem.cpp` (коммиты FS13
`e9dd8604`, `3630f116`), `joyPump.cpp` / `joyPump.h` (FS14a) и `faultManager.cpp` / `faultManager.h` (`15c9d2f2`, `78e45af3`) [c]; иных нет.
Дифф `src/` worktree тега F44c (`d760708d`, worktree `e148f54c`) → FS14 звено не считало.

## Файлы

`C:/kyty/f287/fs14a/`, копии в `docs/track-f/fs14a/` (текстовые — LF; `build/`, `wt/`, SPIR-V тестов и TSV стенда — только локально,
выводы стенда `*.out` — в git):
- **Скрипты:** `patch_fs14a.py`, `patch_fs14a_f29.py`, `mk_wt_fs14a.sh`, `cp_fs14a.sh`, `build_fs14a.cmd`, `bstep.sh`, `sstep.sh`,
  `api_chk.sh`, `watch_fs14a.py`, `run_tests_fs14a.py`, `run_tests_fs14a_f29.py`, `run_stand_fs14a.py`, `verify_fs14a.py`,
  `verify_fs14a_f29.py`, `binary_fs14a.py`, `binary_fs14a_f29.py`, `append_facts.py`.
- **Выводы издания 2:** `gate_order_main_f29.out.txt`, `gate_order_wt_f29.out.txt`, `verify_fs14a_f29.out.txt`, `binary_fs14a_f29.txt`,
  `binary_sha_f29.txt`, `kytyGitVersion_fs14_f29.h`, `cp_15c9d2f2.log`, `cp_78e45af3.log`, `build_{cfg2,ver2,emu2,t2,stand}.log`,
  `runs/log_tests_cfg_f29.txt`, `runs/log_stand_f29.txt`, `stand_f29/f29_{0,1}.out`, `stand_f29_counts.txt`,
  `tests/fs14_f29/{log,rc,exe_sha256}.txt`, `commit_msg_f29.txt`, `facts_fs14a_f29.md`.
- **Выводы издания 1** (промежуточный `826fc0a0`): `gate_order_main.out.txt`, `gate_order_wt.out.txt`, `verify_fs14a.out.txt`,
  `binary_fs14a.txt`, `binary_sha.txt`, `kytyGitVersion_fs14.h`, `mk_wt.log`, `cp_{5c21c387,e3aa4b4d,57f9e528,c8836f14}.log`,
  `build_{cfg,ver,emu,t1}.log`, `runs/log_tests_cfg.txt`, `tests/fs14/`, `commit_msg_code.txt`, `facts_fs14a.md`.

## Не заявляется

П. 710(з) целиком: в частности, что FS14 установлен (до FS14d); что настоящий пульт хоста на `JoyPump` работает; что Ф24 случается у
пользователя; что проход с ≥ 1 024 битами случается в игре (п. 712: не наблюдался); что прочие 40 `SCENE_OK` держатся на FS14; бинарь FS14
игрой не запускался — путь по умолчанию в игре не проверен (FS14c), строка `FixF29: mode=1` в логе эмулятора не наблюдалась; ни одно
число — не выигрыш.
