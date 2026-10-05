# FS8a (`HPP-571`, Emu Engineer): восьмой бинарь отгрузки трека F (FS8) — умолчание `KYTY_FIX_F19=1`

Решение лида — `a6a250ce:docs/ROADMAP.md:22621` п. 471(г)(1) (якорь «(1) **FS8a (Emu Engineer, без замка; `blocked` на `HPP-568` и `HPP-501`).**»;
+1 — «(2) **FS8b (Red Team, без замка): ревью.**»); поправки — п. 487(г)(6) (KytyPS5 `76fe4284`: таблица умолчаний + `KYTY_FIX_B24`, «содержит» +
`9c726d74`, `919c1a19`), п. 522(д) (`d43c2a4a`: база — worktree FS7a `d6ee2dc8`, FS7 принят к установке, не установлен), п. 523 (`9959e3b8`: вариант 1б —
цепочка cherry-pick и члены (е′), (ж′)). Игра не запускалась; установленный `ps5 em/kyty_emulator.exe` — FS6 `9325446c…` до и после звена, `C:/kyty/build/install`
и кэши не тронуты. Время — UTC по `date -u`, события — `C:/kyty/f287/times.txt` (строки `FS8a`). Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно.
Замка `C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` за звено не было (каждая команда начиналась проверкой). В `in_progress` шли звенья Harness Engineer
`HPP-561` F20c (серия) и `HPP-601` S15a. Поэтому каждая команда дольше 60 с (configure, сборки, GPU-гейт, набор) шла под сторожем `watch_fs8a.py`
по п. 431(в)(1), а перед ней в `times.txt` писалась строка проверки API (`api_chk.sh`). Сторож не срабатывал ни разу.
**WIP по дыму: бинарь собран и проверен тестами, игрой не проверялся** (теги — FS8c после FS8b).

## Итог

- **Коммиты в `main`:**
  - `e46f55d4` — умолчание `KYTY_FIX_F19` 0 → 1, 3 файла, +11/−4, `--only`;
  - **`7719d0f2`** — три чтения ручки в `tests/shaderCfgTests.cpp` → `FixF19Enabled()`, 1 файл, +4/−4, только тесты. Это сверх буквы п. 471(г)(1); причина и вопрос — §«Вопрос лиду».
- **Worktree `C:/kyty/f287/fs8a/wt`, HEAD `302347b4`.** Цепочка по п. 523(в) на FS7a `d6ee2dc8`:

  | Шаг | Источник | Коммит в worktree |
  |---|---|---|
  | 1 | `fcaf141b` | `05896234` |
  | 2 | `082d1612` | `c85969f8` |
  | 3 | тестовая часть `ff953d4f` | `3b39efd1` |
  | 4 | `f98e842c` | `7a83c4e3` |
  | 5 | `e46f55d4` | `0f78a522` |
  | 6 | `7719d0f2` | `302347b4` |

  Конфликтов 0; `git status --short` — 0 строк [c].
  - **Поправка к шагу 3.** `ff953d4f` несёт 12 файлов `docs/`: 11 под `docs/track-s/s14j/` и `docs/track-s/s14j.md` [c `git show --stat`]. Первый скрипт `cp523.sh` остановился на проверке «в индексе только тест» (rc 9). Это не конфликт. По п. 523(б)(2) и (г)(е′)(1) («путей `docs/` 0»; «12 файлов» в комментарии лида = этому счёту) снят и `s14j.md`. Продолжение — `cp523b.sh`.
- **Бинарь: sha256 `2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b`**, копия `C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe` (sha256 тот же; `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe`). Строка версии `KytyPS5-2026-09-15-6a2987a-1889-g302347b4`. **Не установка.**
  - Первая сборка при HEAD `0f78a522` (до `7719d0f2`) — sha256 `aed92dc1…`, копия `C:/kyty/f287/bin/kyty_emulator_aed92dc1.exe`. **Заменена**: строка версии содержит HEAD.
  - Подпись трансляции обеих сборок одна [c `kytyGitVersion.h`]: тесты в подпись не входят.
- **(г) Подпись трансляции `KYTY_SHADER_SOURCE_HASH` = `9177b4267de1fb8bac7d1113afd8733210addfac` — новая.** Она ≠ FS7/FS6 `26ce5fc7…` и ≠ F14e2 `a54ae4bd…`.
  - Каталог по коду [c строк гейта `[f19] cache dir=` / `cache signature=`]:
    - без переменной и при `=1` — `variant_fixb26_fixb1b_fixf10_fixf19`, подпись `KytySC3:9177b426…:fixb26:fixb1b:fixf10:fixf19`;
    - при `KYTY_FIX_F19=0` — `variant_fixb26_fixb1b_fixf10`, подпись без `:fixf19`.
  - Первый запуск FS8 — холодная трансляция во всех вариантах [I].
- **(а) Н1 п. 469(в):** 4 из 4 файлов `SHADER_CACHE_EXTRA_FILES` есть в worktree [c `verify_fs8a.py`]: `shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`, `imageInfo.h`. `${KYTY_SOURCE_DIR}` = `wt/src` по `CMakeLists.txt:15`.
- **(б) GPU-гейт `shader_recompiler_compute_tests` из worktree** (`gpu_fs8a.sh`, все `KYTY_*` сняты) [c]:

  | Прогон | `KYTY_FIX_F19` | Аргумент | Итог |
  |---|---|---|---|
  | `gu` | нет | `--fix-f19-only` | `ALL OK`, ожидания `=1` |
  | `g1` | `1` | `--fix-f19-only` | `ALL OK` |
  | `g0` | `0` | `--fix-f19-only` | `ALL OK`, ожидания `=0` |
  | `c1` | `1` | `--fix-f19-comparison-depth` | `ALL OK` |
  | `c0` | `0` | `--fix-f19-comparison-depth` | прежний отказ — отрицательный контроль: `ComparisonDepthTexture failed at SPIR-V disassembly: missing required text: OpImageSampleDrefExplicitLod`, rc `3221226505` (= F14e2 и п. 471(а)(1)) |

  Ожидания гейт берёт из `FixF19Enabled()` (`tests/ShaderRecompilerComputeTests.cpp:32228`). Те же итоги на обеих сборках (`gpu_fs8a_r1.out.txt`, `gpu_fs8a.out.txt`).
- **(в) `shader_cfg_tests` из worktree** (`suite_fs8a.py`, все `KYTY_*` сняты, набор с правкой Б11 по п. 523(г)), сборка `302347b4`, exe sha256 `78137e80…`:
  - прогоны `fu` (без переменной), `f0` (`=0`), `f1` (`=1`) — по 130 тестов, по 0 строк `ShaderCfgTests: failed:`, rc 0;
  - SPIR-V `fu` = `f1` байт в байт, 180 из 180 файлов (сводный sha256 `7fa1857d…`);
  - справка: `f0` отличается от `fu` в 6 файлах — `109`, `110`, `112`, `113`, `177`, `179`.

  `ALL OK` [c].
  - **Первый прогон** (сборка `0f78a522`, `runs/log_suite_r1.txt`) — `FAILED`. У `fu` 6 строк `failed:` в `TestNewShaderRecompilerPixelImageSampleLodSelection`, `TestF19IndirectComparisonTable`, `TestF19NullComparisonDescriptor`: тесты читали ручку `Common::EnvFlagOn("KYTY_FIX_F19")` (не задана = 0), транслятор после `e46f55d4` — по `FixF19Enabled()` (не задана = 1). У `f0`/`f1` — 0 строк; SPIR-V `fu` = `f1` уже тогда (тот же сводный sha256) [c].
  - Исправление `7719d0f2` — те же три чтения через `ShaderRecompiler::IR::FixF19Enabled()`. Именно так их описывал комментарий теста: «The knob is read as FixF19Enabled reads it».
- **(д) Таблица умолчаний** (`knobs_fs8a.py 302347b4` — копия `knobs_fs7a.py`, ожидаемый набор + `KYTY_FIX_F19`):
  - умолчание 1 — ровно 13 ручек: `KYTY_FIX_B1B`, `KYTY_FIX_B24`, `KYTY_FIX_B26`, `KYTY_FIX_B4`, `KYTY_FIX_B42`, `KYTY_FIX_B9A`, `KYTY_FIX_DUALSRC`, `KYTY_FIX_F10`, `KYTY_FIX_F19`, `KYTY_FIX_F8`, `KYTY_FIX_MINIMIZE`, `KYTY_FIX_SVAL`, `KYTY_S_PCW`. Это список п. 467(г)(1) с поправкой п. 487 (+ `KYTY_FIX_B24`) и `KYTY_FIX_F19`;
  - `DEFAULT-ON == expected: True`, `ALL OK`;
  - против вывода FS7a — только строки `KYTY_FIX_F19` (`ResourceMaterialization.cpp:38`, `DEFAULT-ON`), счёт диффа и списки [c].
- **(е′) п. 523(г)** (`verify_fs8a.py`):
  - (1) `git diff --name-only d6ee2dc8 HEAD` — ровно 6 путей: `CMakeLists.txt`, `shaderTranslationCache.cpp`, `ResourceMaterialization.cpp`, `ResourceMaterialization.h`, `tests/ShaderRecompilerComputeTests.cpp`, `tests/shaderCfgTests.cpp`; путей `docs/` 0 ✓;
  - (2) sha256 `git diff d6ee2dc8 HEAD -- src CMakeLists.txt` = sha256 `git diff d6ee2dc8 5e78640e -- src CMakeLists.txt` = `02169c8f739bae448d410b59a2da51e5c323917a9f3ec9927d4a409a7694eb74` ✓. Исходники эмулятора и `CMakeLists.txt` — ровно буква;
  - (3) `HEAD^{tree}` `0b2efcb6…` ≠ `5e78640e`. Разница — 12 путей `docs/track-s/s14j*` (отброшены по п. 523(в)) **и `tests/shaderCfgTests.cpp`** (коммит `7719d0f2`). **По букве (3) не выполнен на один тестовый файл** — §«Вопрос лиду». При HEAD `0f78a522` (до `7719d0f2`) разница была только 12 путей `docs/` (`eprime.out.txt`, проверка тем же способом).
- **(ж′) «бинарь содержит» по п. 380(б)** (`git cherry HEAD <c> <c>^` = `-`; предками коммиты `main` не являются — цепочка из cherry-pick):
  - содержит: `082d1612`, `f98e842c`, `e46f55d4` (FS8a), `10a4800b`, `ec6c4c83` (FS7a), `9c726d74`, `919c1a19`, `fcaf141b`, `7719d0f2` — 9 из 9 ✓;
  - `ff953d4f` целиком не содержится (`+`); `tests/shaderCfgTests.cpp` ⊇ добавок `ff953d4f` — 406 различных добавленных строк, недостающих 0 ✓ [c].
- `check_gate_order.py` (`C:/kyty/s113/`, `--src wt/src`) — `GATE ORDER: clean`; вывод байт в байт = FS7a и `main` при обоих HEAD (гейтов и ручек правка не добавляет) [c].
- В exe строки `KYTY_FIX_F19`, `:fixf19`, `KYTY_FIX_F8`, `KYTY_FIX_B24` — по 1 [c].

## Код (`e46f55d4`, в worktree — `0f78a522`)

`src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:34–42`:

```cpp
bool FixF19Enabled() {
	// Track F, FS8a (HPP-571, ROADMAP s122 item 471(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any
	// other value as EnvValueOn (the form of FS4a 17adaf80).
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_FIX_F19");
		return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);
	}();
	return enabled;
}
```

- До FS8a: `static const bool enabled = Common::EnvFlagOn("KYTY_FIX_F19");`, то есть не задана = 0.
- Комментарии: `ResourceMaterialization.h:46` («default ON since FS8a»), `shaderTranslationCache.cpp:581` («the default since FS8a»).
- Токен `:fixf19` (`shaderTranslationCache.cpp:588`, последний в варианте) и ветки `=1` / `else` F14e/F14e2 не меняются [c диффа `0f78a522^..0f78a522`].
- Пути по коду [c]:
  - без переменной и при `=1` — путь F14e2 при `=1`;
  - при `=0` — ветка `else`, дословно `082d1612`/`f98e842c`, то есть путь FS7 по SPIR-V (член (в): справка `f0`). Подпись при `=0` новая (`9177b426…` без `:fixf19`), каталог `variant_fixb26_fixb1b_fixf10` (на новой подписи — холоден).

`7719d0f2` (`tests/shaderCfgTests.cpp`): чтения `const bool fix_f19 = Common::EnvFlagOn("KYTY_FIX_F19");` (3 места) → `const bool fix_f19 = ShaderRecompiler::IR::FixF19Enabled();`. Комментарий первого места: «The knob is FixF19Enabled() itself (default ON since FS8a, ROADMAP s122 item 471(g)(1))». Файлов `src/` и `CMakeLists.txt` не трогает.

## Состояние, вводимое правкой

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `enabled` (static local, `ResourceMaterialization.cpp:37`) | один раз — первый вызов `FixF19Enabled` (C++11 magic static, потокобезопасно) | нет — на время процесса | как до FS8a (была static local); значение — функция окружения процесса |
| `fix_f19` в трёх тестах (`const bool`, локальная) | вызов `FixF19Enabled()` | конец области теста | локальная константа, как до правки |

Нового состояния правка не вводит: меняется только выражение инициализации той же static local. Выход функции один (`return enabled`).

## Ход

- `05:14:01Z` — коммит `e46f55d4` в `main`.
- `05:15:13Z` — стоп на конфликте cherry-pick по букве; `05:16:36Z` — `--abort`; `05:17:25Z` — вопрос лиду.
- `05:20:31Z` — ответ лида (п. 523); `cp523.sh` / `cp523b.sh` — HEAD `0f78a522`.
- `05:22:44–05:24:31Z` — configure.
- `05:24:42–05:26:26Z` — сборка `kyty_emulator` (783 шага).
- Сборка тестов до `05:27:47Z`.
- GPU-гейт и набор в первом круге, `05:28:41Z` — набор `FAILED`.
- `7719d0f2` в `main`, cherry-pick в worktree `302347b4`.
- `05:29:58–05:30:56Z` — версия, пересборка `kyty_emulator` и обоих тестов.
- `05:31:19Z` — GPU-гейт.
- `05:31:22Z` — набор `ALL OK`.
- Таблица умолчаний, `verify_fs8a.py`, повтор `check_gate_order.py`.

Флаги сборки = FS7a (`build_fs8a.cmd` — копия `build_fs7a.cmd` с путями `fs8a`); `CMakeCache.txt`: `Kyty_SOURCE_DIR=C:/kyty/f287/fs8a/wt`, `Release`.

## Вопрос лиду

**Отклонение от буквы п. 523(г)(е′)(3) на один тестовый файл.** Коммит `7719d0f2` нужен для члена (в) «0 строк `failed:` без переменной». Без него этот член невыполним на любом наборе, где тесты F14e/F14e2 читают ручку своим `EnvFlagOn`. Тот же дефект с `e46f55d4` есть и в `main`: тесты при умолчании падали бы.

Что правка не меняет [c]:
- исходники эмулятора, `CMakeLists.txt`, подпись трансляции — (е′)(2) ✓, подпись одна у обеих сборок;
- SPIR-V набора — сводный sha256 `fu` до и после правки один.

Чтение, которое я применил: (е′)(3) — «разница с `5e78640e` только `docs/track-s/s14j*` и `tests/shaderCfgTests.cpp` коммита `7719d0f2`». Нужна приёмка лидом или иное чтение.

Без `7719d0f2` есть сборка `aed92dc1` (HEAD `0f78a522`): (е′)(3) по букве ✓, но (в) у `fu` — 6 строк `failed:`.

## Файлы

`C:/kyty/f287/fs8a/`, копии в `docs/track-f/fs8a/` (текстовые — LF):
- **Скрипты:** `api_chk.sh`, `bstep.sh`, `sstep.sh`, `watch_fs8a.py`, `build_fs8a.cmd`, `port_fs7a.py`, `patch_fs8a.py`, `patch_fs8a_tests.py`, `mk_wt_fs8a.sh`, `cp523.sh`, `cp523b.sh`, `gpu_fs8a.sh`, `suite_fs8a.py`, `knobs_fs8a.py`, `verify_fs8a.py`.
- **Выводы:** `mk_wt.log`, `conflict_082d1612.diff`, `cp523.log`, `cp523b.log`, `patch_main.out.txt`, `patch_tests_main.out.txt`, `patch_tests_wt.out.txt`, `gate_order_main.out.txt`, `gate_order_wt.out.txt`, `gate_order_wt2.out.txt`, `eprime.out.txt`, `gpu_fs8a_r1.out.txt`, `gpu_fs8a.out.txt`, `gpu/<прогон>/run.log`, `log_suite_r1.txt`, `log_suite.txt`, `knobs_fs8a.out.txt`, `verify_fs8a.out.txt`, `diffstat_vs_d6ee2dc8.txt`, `fs8a_vs_d6ee2dc8.diff`.
- **Прочее:** `kytyGitVersion_fs8.h`, `commit_msg_code.txt`, `commit_msg_tests.txt`, `SHA256SUMS_fs8a.txt` (sha256 локальных оригиналов и бинарей).

В копиях `mk_wt_fs8a.sh`, `cp523.sh`, `cp523b.sh` адрес агента заменён на `<agent-email>` (общее правило 28), поэтому их sha256 отличаются от строк `SHA256SUMS_fs8a.txt`.

## Не заявляется

- что расхождение видно в кадре игры и его величина;
- что PCF драйвера равен ответу PS5;
- что ответ `D32_SFLOAT` на нативном пути верен;
- что вариант (A) покрывает все места игры;
- что SPIR-V корректен для устройства и картинка верна;
- что FS8 работает в игре (дыма не было, до FS8c);
- что FS8 установлен (до FS8d);
- что тестовые коммиты не меняют бинарь — показано только для подписи; бинари двух сборок отличаются строкой версии;
- что набор `shader_cfg_tests` полон;
- ни одно число — не выигрыш;
- 60 FPS не обещаются.
