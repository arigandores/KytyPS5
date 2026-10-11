# FS15a (`HPP-820`, Emu Engineer): пятнадцатый бинарь отгрузки трека F (FS15) — умолчание `KYTY_FIX_F20=1`

Задание — `ROADMAP.md` «СЕССИЯ 122» п. 730(г)(1) (KytyPS5 `2e71aad4`, якорь «(г) **Отгрузка FS15 — константы лида.** (1) **FS15a
(Emu Engineer, без замка и без игры).**»); вывод — п. 730(в); образец — FS14a п. 710(г)(1) с п. 712(г)(1), отчёт `docs/track-f/fs14a.md`;
правило базы — п. 410(г)(6)(i), 727(г). Игра не запускалась; установленный `ps5 em/kyty_emulator.exe` — FS14 `013e1974…` до и после звена,
`C:/kyty/build/install`, `C:/kyty/build` и кэши не тронуты. Время — UTC по `date -u`, события — `C:/kyty/f287/times.txt` (строки `FS15a`).
Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно. Ссылок `<коммит>:<путь>:<строка>` отчёт не несёт (места названы по
функциям и файлам). **WIP по дыму: бинарь собран и проверен тестами без игры, игрой не проверялся** (теги — FS15c после FS15b).

Серия F47d (`HPP-809`, Harness Engineer) шла параллельно: с 18:04:47Z звено `in_progress` с `executionRunId`; все шаги сборки и тестов — под
сторожем `watch_fs15a.py` (п. 431(в)(1)) со строкой API перед каждым. В 18:06:43Z сторож убил сборку `shader_cfg_tests` (шаг `t1`) по
процессу шлюза `procload.py` (строка `times.txt`); замок `C:/kyty/SEALED_RUN.lock` стоял с ≈ 18:07Z до 18:13:26Z (наблюдение звена) — в это
время звено процессов не запускало и в `C:/kyty/` не писало; шаг повторён как `t2` после снятия замка (ninja доделал цель). Сборка
`kyty_emulator` закончилась до этого (18:06:20Z), её бинарь пересборкой тестов не менялся (sha до и после — `bfac84be…`).

## Итог

- **Коммит в `main`** (`--only`): **`38fc76c1`** (2 файла: `src/graphics/host_gpu/renderer/pipeline/fixF20.cpp` +4/−1,
  `fixF20.h` +3/−2) — умолчание `KYTY_FIX_F20` 0 → 1 в форме FS14a `c8836f14` / FS13a `3630f116` (не задана или `""` — 1; иначе
  `Common::EnvValueOn`).
- **Worktree `C:/kyty/f287/fs15a/wt`, HEAD `6beb3b73`** — база FS14 `eb7e8b91` (worktree FS14a, установленный FS14 `013e1974`, п. 727–728;
  другого принятого лидом бинаря отгрузки нет) + cherry-pick `-x`:

  | Шаг | Источник | Коммит в worktree | Конфликт |
  |---|---|---|---|
  | 1 | `a6342c98` (F42a: код `KYTY_FIX_F20`) | `b1179dab` | нет |
  | 2 | `a9d6fd1c` (F42a: стенд издания 1) | `95e39a17` | нет |
  | 3 | `82570fd2` (F42a2: вынос `CreateCachedModule`, геттеры, стенд издания 2) | `91b74d09` | нет |
  | 4 | `38fc76c1` (FS15a: умолчание Ф20) | `6beb3b73` | нет |

  Конфликтов нет; `git status --short` — 0 строк после каждого шага [c `cp_*.log`, `mk_wt.log`]. Зависимости от кода вне базы нет: сборка
  `kyty_emulator` и `shader_cfg_tests` прошла.
- **Бинарь FS15: sha256 `bfac84bea0eaec8bf3dae6ab5f67cd480f26921829f64f4a8b467bd50e922d8c`**, копия
  `C:/kyty/f287/bin/kyty_emulator_bfac84be.exe` (+ `.sha256`). Строка версии `KytyPS5-2026-09-15-6a2987a-1929-g6beb3b73`. **Не установка.**
- Члены п. 730(г)(1) — на бинаре `bfac84be` / worktree `6beb3b73`:

  | Член | Итог | Источник |
  |---|---|---|
  | «бинарь содержит» `a6342c98`, `82570fd2`, `38fc76c1` (FS15a), `5c21c387`, `57f9e528`, `c8836f14`, `15c9d2f2`, `78e45af3`, `e9dd8604`, `3630f116`, `227e1b36`, `cbfe8375`, `c94c49e0`, `726e751e`, `cb022252` — «предок или `git cherry` `-`», счёт скриптом с отрицательным контролем | ✓ у всех пятнадцати `git cherry` `-` (предками FS15 не являются — все перенесены cherry-pick: три F42 и FS15a — этим звеном, коммиты FS14 — FS14a, FS13 — FS13a, FS12 — FS12a, FS11 — FS11a); справка: `a9d6fd1c` — тоже `-`. Изменённые строки переносов этого звена равны источникам (338, 407, 98, 10). Отрицательные контроли — то же правило говорит «нет» (`+`): `a6342c98`, `82570fd2`, `38fc76c1` в базе `eb7e8b91`; `38fc76c1` в промежуточном `91b74d09`; `15c9d2f2`, `78e45af3` в FS13 `ea6c6e9e`; `1398d44d` (измерение F46a) в FS15; строки `a9d6fd1c` против переноса `a6342c98`, строки `82570fd2` против своего переноса с одной испорченной строкой, строки `38fc76c1` против переноса `82570fd2` — не равны | `verify_fs15a.out.txt` V1, V1b |
  | дифф `src/` FS15 против базы FS14 — только файлы трёх коммитов F42 и FS15a; путей `src/graphics/shader/**` 0 | ✓ 6 путей `src/`: `src/emulator.cpp`, `src/graphics/host_gpu/renderer/pipeline/{fixF20.cpp, fixF20.h, pipelineCache.cpp, pipelineCache.h, shaders.cpp}` = файлам `src/` четырёх коммитов; под `src/graphics/shader/` 0. Вне `src/` — 2 пути, оба из `a9d6fd1c` / `82570fd2`: `tests/ShaderRecompilerComputeTests.cpp`, `tests/shaderCfgTests.cpp` — в `kyty_emulator` не входят. `git diff --stat`: 8 файлов, +821/−10. Знаковое мультимножество изменённых строк = сумме четырёх коммитов (831 строка), без `38fc76c1` — не равно | V2, V2b |
  | подпись трансляции (`KYTY_SHADER_SOURCE_HASH`) = базе `9177b426…` | ✓ `9177b4267de1fb8bac7d1113afd8733210addfac` у FS15 = FS14a; в exe ×1 у FS15 и у FS14 | V5, `kytyGitVersion_fs15.h`, `binary_fs15a.txt` |
  | `shader_cfg_tests` — строки `failed` и счёт = базе FS14 | ✓ сборка worktree `6beb3b73` против прогона FS14a сборки FS14 `eb7e8b91` (`C:/kyty/f287/fs14a/tests/fs14_f29`): rc 0 / 0, `[test]` 133 / 133, `ShaderCfgTests: failed:` 0 / 0, строк со словом `failed` 5 / 5, мультимножество равно; справка t4: SPIR-V 360 / 360 байт в байт (агрегат `b1376644` = FS14a) | `tests/fs15/`, `runs/log_tests_cfg.txt` |
  | `check_gate_order.py` — clean | ✓ `GATE ORDER: clean` на `main` после `38fc76c1` и на worktree `6beb3b73` до сборки (`C:/kyty/s113/check_gate_order.py --src …`); вывод без строки заголовка равен выводу FS14a — гейтов и ручек правка не добавляет | `gate_order_main.out.txt`, `gate_order_wt.out.txt` |
  | таблица умолчаний своим сканером — база FS14 плюс `KYTY_FIX_F20` (и только он) | ✓ 20 → 21; отрицательный контроль — на промежуточном `91b74d09` (без FS15a) разность пуста, член там не выполнен | V3 |
  | `KYTY_S_REPLAY` = 3 | ✓ blob `shaderReplay.cpp` базы = FS15 (`e1626ad6…`), `ParseMode` не задана / `""` → 3 | V4 |
  | в бинаре по одной строке формата `FixF20: mode=` и `FixF20Stat:` | ✓ ×1 и ×1 у FS15 (`FixF20Stat: when=%s calls=%llu modules_bound=%llu modules=%llu sites=%llu rewritten=%llu unmatched=%llu`); ×0, ×0 у FS14; `KYTY_FIX_F20` ×1 / ×0; в исходнике FS15 — `getenv("KYTY_FIX_F20")` ×1, `EnvFlagOn("KYTY_FIX_F20")` ×0, формат `"FixF20: mode=%d` ×1, `"FixF20Stat: when=%s` ×1, чтение в форме `3630f116` (V3b) | `binary_fs15a.txt`, V3b |
  | маркеры базы | ✓ строки Ф24 (`FixF24: mode=`, `init_owner`), Ф29, Ф25, Ф21, Б12, Б13, Б36, Б4 — ×1 у FS15 и FS14; строка версии FS14 в FS15 ×0 | `binary_fs15a.txt` |
  | sha256 и копия `C:/kyty/f287/bin/kyty_emulator_<sha8>.exe`, не установка | ✓ `kyty_emulator_bfac84be.exe`; установленный `013e1974…` до и после | `binary_sha.txt`, `times.txt` |
  | диагностики вне базы в бинарь не входят | ✓ добавленных строк кода с `KYTY_DIAG_B32` / `DiagB32` / `rts_bad_b` / `KYTY_F26_TINT` / `KYTY_FIX_F26` 0; `1398d44d` — `git cherry` `+`; в exe `KYTY_DIAG_B32`, `rts_bad_b`, `KYTY_F26_TINT`, `KYTY_FIX_F26`, `F20Stand`, `KYTY_TEST_F20STAND` ×0 (стенд Ф20 живёт только в `shader_recompiler_compute_tests`) | V6, `binary_fs15a.txt` |

## Код (`38fc76c1`, в worktree — `6beb3b73`)

`src/graphics/host_gpu/renderer/pipeline/fixF20.cpp`, `FixF20::Mode`:

```cpp
// Track F, FS15a (HPP-820, ROADMAP s122 item 730(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any
// other value as EnvValueOn (the form of FS14a c8836f14 / FS13a 3630f116); still one reading per process.
int Mode() {
	static const int mode = [] {
		const char* env = std::getenv("KYTY_FIX_F20");
		const int value = (env == nullptr || env[0] == '\0' || Common::EnvValueOn(env)) ? 1 : 0;
		LOGF("FixF20: mode=%d\n", value);
		return value;
	}();
	return mode;
}
```

- До FS15a (F42a `a6342c98`): `const int value = Common::EnvFlagOn("KYTY_FIX_F20") ? 1 : 0;` — не задана = 0. `fixF20.h`: комментарий у
  объявления `Mode` «(default 0): … (Common::EnvFlagOn - unset, "", 0/false/off/no = 0 …)» заменён на «(default 1 since FS15a, HPP-820,
  ROADMAP s122 item 730(g)(1)) … (unset or "" - 1; 0/false/off/no - 0; any other value as EnvValueOn)»; прочий текст F42a не тронут.
- Одно чтение на процесс сохранено: `static const` лямбды инициализируется при первом вызове (C++11 — потокобезопасно); первый вызов —
  конструктор `PipelineCache` (строка `FixF20: mode=`), затем четыре места создания модуля и `PrintExitStat` [c `a6342c98`]. `std::getenv`
  — `<cstdlib>` через `common/envFlag.h` (включение с F42a).
- Строка `FixF20: mode=<0|1>` печатается по значению: без переменной теперь `mode=1` [I по коду; в игре — FS15c]. Пути по коду [c]: без
  переменной, `""`, `1/true/on/yes` — 1; `0/false/off/no` — 0 (путь `=0` по коду = база FS14 плюс строка `FixF20: mode=0`: `Apply` не
  вызывается, `FixF20Stat:` не печатается — п. 694(г)(2); сверка — FS15b).
- `src/graphics/shader/**` не тронут — подпись трансляции не меняется; гейтов и ручек правка не добавляет.

### Состояние, вводимое правкой

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `mode` (`static const int` функции `FixF20::Mode`) | один раз — при первом вызове `Mode` (конструктор `PipelineCache`) | не снимается (время жизни процесса) | как в F42a `a6342c98`; меняется только выражение значения |
| `env` (локальная `const char*` лямбды) | на строке `std::getenv` | конец лямбды | локальная, не переживает вызов; единственный выход — `return value` |

Нового состояния с жизненным циклом правка не вводит; выходов функции не прибавилось.

## Тесты (`run_tests_fs15a.py`)

Сборка FS15 (worktree `6beb3b73`): `shader_cfg_tests.exe` (sha256 — `tests/fs15/exe_sha256.txt`); все `KYTY_*` сняты, кроме
`KYTY_TESTS_CONTINUE`, `KYTY_TESTS_VERBOSE`, `KYTY_TESTS_SPV_DIR`. База — прогон FS14a сборки FS14 `eb7e8b91`
(`C:/kyty/f287/fs14a/tests/fs14_f29`); своей сборки базы звено не делало (форма FS14a). Список HANDOFF §4 «14 известных падений» на этом
дереве не воспроизводится — 0 падений `ShaderCfgTests` у FS14 и FS15, как у FS14a. Новые входы `shader_cfg_tests` из `a9d6fd1c`
(`KYTY_RECOMPILE_F20`, `KYTY_TEST_F20FILE`) включаются только переменными и в прогоне не действуют (счёт `[test]` равен). Стенд Ф20
(`shader_recompiler_compute_tests --f20-stand`) членом FS15a не назван и не собирался.

## Ход (UTC)

- `18:00:48Z` — первая команда звена; `18:01:36Z` — коммит `38fc76c1`, `check_gate_order.py` на `main` clean.
- `18:02:09–18:02:23Z` — первая попытка worktree через сторож отказала (`Popen` нашёл `bash` WSL, ничего не создано), worktree создан прямым
  вызовом (14 с); `18:02:49Z` — cherry-pick 1–4; `18:02:55Z` — `check_gate_order.py` на worktree clean.
- `18:02:56–18:04:31Z` — configure; `18:04:50–18:04:54Z` — версия; `18:05:00–18:06:20Z` — `kyty_emulator`; `18:06:30–18:06:43Z` — сборка
  `shader_cfg_tests` убита сторожем (`procload`); `18:06:44Z` — копия бинаря `bfac84be` (замка не было, наблюдение 18:06:48Z).
- ≈ `18:07Z`–`18:13:26Z` — замок серии F47d: звено ждало; `18:13:34Z` — `verify_fs15a.py` `ALL OK`, `binary_fs15a.py` `ALL OK`;
  `18:14:09–18:14:52Z` — `shader_cfg_tests` (`t2`); `18:14:58–18:14:59Z` — тесты `ALL OK`.

Флаги сборки = FS14a (`build_fs15a.cmd` — копия `build_fs14a.cmd` с путями `fs15a`); Release, clang-cl, LTO.

## Для FS15b (справка, не член FS15a)

V7 `verify_fs15a.out.txt`: пути `src/` диффа worktree тега F42a2 `5ccb1d31` → FS15 — `src/kernel/fileSystem.cpp` (FS13), окно/SDL
(`hostInput.cpp`, `joyPump.cpp`, `joyPump.h`, `vulkanWindow.cpp`, `window.cpp`, `src/libs/controller.cpp` — FS14 Ф24), `faultManager.cpp` /
`faultManager.h` (FS14 Ф29) и `fixF20.cpp` / `fixF20.h` (FS15a) [c]; иных нет.

## Файлы

`C:/kyty/f287/fs15a/`, копии в `docs/track-f/fs15a/` (текстовые — LF; `build/`, `wt/`, SPIR-V тестов — только локально):
- **Скрипты:** `patch_fs15a.py`, `mk_wt_fs15a.sh`, `cp_fs15a.sh`, `build_fs15a.cmd`, `bstep.sh`, `sstep.sh`, `api_chk.sh`, `watch_fs15a.py`,
  `run_tests_fs15a.py`, `verify_fs15a.py`, `binary_fs15a.py`, `append_facts.py`, `sanitize_fs15a.py` (копии в git: домашний каталог в
  `build_cfg.log` заменён на `<HOME>/`).
- **Выводы:** `gate_order_main.out.txt`, `gate_order_wt.out.txt`, `verify_fs15a.out.txt`, `binary_fs15a.txt`, `binary_sha.txt`,
  `kytyGitVersion_fs15.h`, `mk_wt.log`, `cp_{a6342c98,a9d6fd1c,82570fd2,38fc76c1}.log`, `build_{cfg,ver,emu,t1,t2}.log`,
  `runs/log_tests_cfg.txt`, `runs/log_mk_wt.txt` (отказ сторожа), `tests/fs15/{log,rc,exe_sha256}.txt`, `commit_msg_code.txt`,
  `facts_fs15a.md`.

## Не заявляется

П. 730(з) целиком: в частности, что FS15 установлен (до FS15d); что бит теряется в игре на установленном бинаре и как часто; что первый запуск
FS15 у пользователя пройдёт без кадров ≥ 1 с вне формы `f20_v`; что переписанные модули годны драйверу на всех сценах; что прочие 40
`SCENE_OK` держатся на FS15; бинарь FS15 игрой не запускался — путь по умолчанию в игре не проверен (FS15c), строка `FixF20: mode=1` без
переменной в логе эмулятора не наблюдалась; ни одно число — не выигрыш.
