# FS6a (`HPP-555`, Emu Engineer): шестой бинарь отгрузки трека F (FS6) — умолчание `KYTY_FIX_B4=1`

Решение лида — `0c1aa479:docs/ROADMAP.md:22495` п. 454 (якорь «454. **Звено F15f трека F (`HPP-517`, лид): F15c, F15d, F15e ПРИНЯТЫ»; +1 — «(а)
**Приёмка строкой по членам п. 412(г).**»), подпункт (г)(1) — FS6a; правило базы — п. 410(г)(6)(i), чтение «содержит» — п. 380(б). Вход — код F15c
`a86a5ad0` (п. 440, 454) и база S12a `4d9e8ab7` (бинарь S12 `adb0c82f`, установлен 10:12:56Z, п. 437–438). Игра не запускалась; установленный бинарь
`adb0c82f`, `C:/kyty/build/install` и кэши не тронуты (sha256 `ps5 em/kyty_emulator.exe` после звена — `adb0c82f1a752805…`) [c]. Время — UTC по `date -u`,
события — `C:/kyty/f287/times.txt` (строки `FS6a`). Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно.
**WIP по дыму: бинарь собран, проверен стендом и тестами, игрой не проверялся** (теги — FS6c после FS6b).

## Итог

- **База по п. 410(г)(6)(i) — S12a `4d9e8ab7`**: после п. 437–438 (S12 установлен) лидом не принят ни один другой бинарь отгрузки — пункты 439–457
  `ROADMAP.md` на 12:26Z (KytyPS5 `630a8cf1`) отгрузок не принимают; F14e2 (п. 456) и F19c (п. 457) — код с умолчанием 0, не бинарь отгрузки [c].
- **Коммит кода: `main` `17eb924e`** (`--only`; 2 файла, +11/−4): `src/kernel/fileSystem.cpp` (чтение и комментарий), `tests/B4RaceStand.cpp` (только
  комментарий шапки стенда: «без переменной — умолчание `fileSystem.cpp`»).
- **Worktree `C:/kyty/f287/fs6a/wt` — `3904522d` = cherry-pick `17eb924e` на `33679a02` = cherry-pick `a86a5ad0` на `4d9e8ab7` (S12a)**; оба cherry-pick
  без конфликтов; patch-id `a86a5ad0` = `33679a02` (`2c4c4293…`), `17eb924e` = `3904522d` (`9be9a818…`) [c]; `git status --short` — 0 строк; CR в `src/` —
  0 из 456 файлов (`mk_wt.log`).
- **Бинарь: sha256 `9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2`**, копия `C:/kyty/f287/bin/kyty_emulator_9325446c.exe` (sha256 тот же;
  `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe`); строка версии `KytyPS5-2026-09-15-6a2987a-1879-g3904522d`. **Не установка.**
- **Подпись трансляции `KYTY_SHADER_SOURCE_HASH` = `26ce5fc78ea3b20be537c7696be041f5e97d9e58` = базе** (S12/FS5) — `build/kytyGitVersion.h:9`, 1 вхождение в exe;
  `KYTY_GIT_REVISION` = `3904522da9cf…` (`:7`). Правка вне `src/graphics/shader/**` — каталог варианта `variant_fixb26_fixb1b_fixf10` не меняется [c].
- `check_gate_order.py` (`C:/kyty/s113/`) на `main` после патча и на `wt/src` — `GATE ORDER: clean`, вывод байт в байт = F15c (`gate_order.out.txt` F15c) —
  гейтов и ручек правка не добавляет [c].
- **Стенд `b4_race_stand` из того же worktree** (sha256 `2d18fd86…`; драйвер `run_stand_fs6a.py` — копия `docs/track-f/f15c/run_stand_f15c.py` `main` с
  текстом Н4 п. 454(в), изменено только ожидание плеча L: без переменной → `mode=1`, `=0` → 0, `=1` → 1; дифф — `run_stand_fs6a.py` строки 1–3, 16, 28):

| плечо | `KYTY_FIX_B4` | seed | итог | ожидание п. 454(г)(1) |
|---|---|---|---|---|
| A | не задана | 2001…2050 | `CLEAN` 50 из 50 | `CLEAN` 50 ✓ |
| B | не задана | 2001…2050 | `CLEAN` 50 из 50 | `CLEAN` 50 ✓ |
| C | не задана | 2001…2050 | `CLEAN` 50 из 50 | 50 ✓ |
| L | не задана | 2001 | `LOG_OK`, `LOGCHECK modes=1` | `modes=1` ✓ |
| A | `0` | 2001…2050 | `FATAL207` 50 из 50 | `FATAL207` ≥ 1 ✓ |
| L | `0` | 2001 | `LOG_OK`, `LOGCHECK modes=0` | `modes=0` ✓ |
| L | `1` | 2001 | `LOG_OK`, `LOGCHECK modes=1` | (справка) |

  Окружение ребёнка — без единой `KYTY_*`, затем `KYTY_FIX_B4=<значение>`, кроме «не задана» [c драйвера]. Стена срезов 2,4–3,3 с.
- **Тесты при умолчаниях** (в окружении нет ни одной `KYTY_*`, кроме `KYTY_TESTS_CONTINUE`/`KYTY_TESTS_VERBOSE` у `shader_cfg_tests`), база — бинари F15c
  `C:/kyty/f287/f15c/base/` (собраны F15c из worktree базы `4d9e8ab7`, sha256 `5facf99e…` и `57ccc489…`):
  - `kernel_file_system_tests --filesystem-only`: база и FS6 — rc 0, `KernelFileSystemTests: all cases passed`, строк `failed:` 0 и 0; логи байт в байт [c].
  - `shader_cfg_tests`: 127 тестов у обоих, падение 1 — Б11 (`IMAGE_SAMPLE_C` / `IMAGE_SAMPLE_C_LZ`, 2 строки), строк `failed:` 4 и 4, равны;
    `pretranslation test: ready=18 failed=1 hits=17` у обоих; логи с заменой `elapsed_ms=\d+` байт в байт; rc 0 [c].
- **Таблица умолчаний** (`knobs_fs6a.py 3904522d` — копия `knobs_s12a.py`, ожидание + `KYTY_FIX_B4`): умолчание 1 (не задана = ВКЛ) — ровно `KYTY_FIX_B1B`,
  `KYTY_FIX_B26`, `KYTY_FIX_B4`, `KYTY_FIX_B42`, `KYTY_FIX_B9A`, `KYTY_FIX_DUALSRC`, `KYTY_FIX_F10`, `KYTY_FIX_MINIMIZE`, `KYTY_FIX_SVAL`, `KYTY_S_PCW` (десять имён
  п. 454(г)(1)); `DEFAULT-ON == expected: True`, `ALL OK`; против вывода S12a — только строки `KYTY_FIX_B4` (`src/kernel/fileSystem.cpp:114`) и списки [c].
  Прочие имена — `default-off` или прежний путь (вывод — `knobs_fs6a.out.txt`).
- **Дифф источника FS6 против `4d9e8ab7` — 6 файлов, ровно объединение файлов `a86a5ad0` и `17eb924e`** (+545/−2): `CMakeLists.txt`,
  `docs/track-f/f15c/patch_f15c_cmake.py`, `patch_f15c_src.py`, `run_stand_f15c.py`, `src/kernel/fileSystem.cpp`, `tests/B4RaceStand.cpp`; вне них — пусто
  [c] (`files_expected.txt` = `files_actual.txt`, `diffstat_vs_4d9e8ab7.txt`, `fs6a_vs_4d9e8ab7.diff`, `fs6a_vs_33679a02.diff`). Против `main` (`0a9adb84`)
  отличаются `CMakeLists.txt` (в `main` — цели позже S12a) и `run_stand_f15c.py` (в `main` — текст Н4 п. 454(в)); `fileSystem.cpp` и `B4RaceStand.cpp` = `main`.
- **Член «бинарь содержит» в чтении п. 380(б)** (`git cherry -v 3904522d <c> <c>^`, `cherry.out.txt`): `-` у `a86a5ad0` и `17eb924e` — 2 из 2 ✓; также `-` у
  `4e72289e`, `68602c4f`, `17adaf80`, `1833ee28`, `c3eb8fe8`, `c1732d1a` (FS3a, F10c, FS4a, F12d, FS5a, S12a); `+` (не входят) у `082d1612` (F14e), `f98e842c`
  (F14e2), `10a4800b` (F18c), `9c726d74` (F19c), `fcaf141b` (F14c), `741e3312` (P35), `c9b4268e` (P40) [c]. Предки `3904522d` (`--is-ancestor`): `4d9e8ab7`,
  `0e72bc19`, `3d0e46da`, `4414e235` — да.
- В exe: `FixB4: mode=` — 1; `KYTY_FIX_B4` — 2 вхождения подстроки, из них одно — внутри `KYTY_FIX_B42` (1 вхождение), т. е. своё имя одно; `KYTY_FIX_F19`,
  `KYTY_FIX_F8`, `KYTY_FIX_B24`, `KYTY_PVAR_HOLD`, `KYTY_DIAG_F5` — 0 [c].

## Код (`17eb924e:src/kernel/fileSystem.cpp`, в `3904522d` — те же строки)

**Умолчание** — `FixB4Enabled` (`:110–118`):

```cpp
static bool FixB4Enabled() {
	// Track F, FS6a (HPP-555, ROADMAP s122 item 454(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any
	// other value as EnvValueOn (the form of FS4a 17adaf80).
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_FIX_B4");
		return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);
	}();
	return enabled;
}
```

Форма = `KYTY_FIX_SVAL` FS4a (`17adaf80:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:1343–1351`) и `KYTY_FIX_F10` FS5a [c]. До FS6a —
`Common::EnvValueOn(std::getenv("KYTY_FIX_B4"))` (не задана / `""` → 0). Комментарий над функцией (`:104–109`) называет новое умолчание; строка
`FixB4: mode=`, ветка `=1` `EmergencyShutdown` (`FlushAll`), ветка `else` (`CloseAll`) и `Shutdown()` не меняются — `fs6a_vs_33679a02.diff`: 2 hunk в
`fileSystem.cpp` (комментарий и выражение чтения) и 1 hunk в `B4RaceStand.cpp` (комментарий) [c].

Пути по коду [c]: без переменной и при `=1` — путь F15c при `=1`; при `KYTY_FIX_B4=0` — ветка `else` (дословно `4d9e8ab7` по `CloseAll`) — путь S12.
Подпись трансляции и каталог одни для всех значений (ручка вне подписи).

## Состояние, вводимое правкой

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `enabled` (static local, `fileSystem.cpp:113`) | один раз — первый вызов `FixB4Enabled` (C++11 magic static, потокобезопасно) | нет — на время процесса | как до FS6a (была static local); значение — функция окружения процесса |

Нового состояния правка не вводит: меняется только выражение инициализации той же static local. Выход функции один (`return enabled`).

## Сборка и порядок

Решение п. 454 прочитано, патч `patch_fs6a.py` (якоря — строки целиком, LF) на `main` и коммит `17eb924e` 12:08:25–12:08:41Z; `check_gate_order.py` на `main` —
clean; worktree `mk_wt_fs6a.sh 17eb924e` (копия `mk_wt_fs5a.sh`: `4d9e8ab7` + cherry-pick `a86a5ad0` + cherry-pick FS6a; подмодули как P23) 12:09:16Z;
configure 12:09:53–12:11:46Z; эмулятор 12:12:02–12:14:02Z; `b4_race_stand` 12:14:16–12:14:48Z; `kernel_file_system_tests` 12:14:50–12:15:20Z; обрыв
хартбита `d57cc00a` 12:15:23Z (сбой терминала платформы); продолжено следующим хартбитом без повтора сборок: `shader_cfg_tests` 12:16:50–12:17:28Z,
стенд 12:18:21–12:18:50Z, тесты 12:18:57–12:19:00Z; замок `C:/kyty/SEALED_RUN.lock` (чужой) — с ≈ 12:20:30Z (время отказа первой команды) до 12:26:30Z и с ≈ 12:28Z до 12:34:28Z
(оба — по отказу команды и `date -u` освобождения): ни процессов, ни записей. Шаги — под `watch_fs6a.py` (предел 540 с, остановка при замке или `STOP`), перед каждым — строка API `api_chk.sh` в `times.txt`: в
`in_progress` у Harness Engineer было только `HPP-553` (трек S, печать без игры); замка, `STOP` и процессов `procload.py` не было ни разу. Флаги сборки =
FS5a/F15c (`build_fs6a.cmd` — копия `build_f15c.cmd` с путями `fs6a`), `CMakeCache.txt`: `Kyty_SOURCE_DIR=C:/kyty/f287/fs6a/wt`, `Release`.

**Н1 п. 454(в) для этой сборки — читать так:** sha256 `9325446c…` относится к сборке в каталоге `C:/kyty/f287/fs6a/build`; сборка того же источника в другом
каталоге (FS6b) может дать другой sha256 — равенство машинного кода тогда читается классификатором `pediff3.py` с отрицательным контролем; бинарь тегов
FS6c опознаётся по sha256 `9325446c…` и строке версии `…-1879-g3904522d`.

## Файлы

`C:/kyty/f287/fs6a/`, копии в `docs/track-f/fs6a/` (текстовые — LF): `patch_fs6a.py`, `patch_main.out.txt`, `commit_msg_code.txt`, `gate_order_main.out.txt`,
`gate_order_wt.out.txt`, `mk_wt_fs6a.sh`, `mk_wt.log`, `build_fs6a.cmd`, `bstep.sh`, `api_chk.sh`, `watch_fs6a.py`, `sstep.sh`, `run_stand_fs6a.py`,
`tests_fs6a.py`, `runs/stand_*_2001.tsv` (7), `runs/tests_fs6a.out.txt`, `runs/tests/{base,fs6}_{kfsonly,scfg}.txt`, `knobs_fs6a.py`, `knobs_fs6a.out.txt`,
`diffstat_vs_4d9e8ab7.txt`, `files_expected.txt`, `files_actual.txt`, `fs6a_vs_4d9e8ab7.diff`, `fs6a_vs_33679a02.diff`, `cherry.out.txt`, `kytyGitVersion_fs6.h`,
`SHA256SUMS_fs6a.txt` (sha256 локальных оригиналов и бинарей). В копии `mk_wt_fs6a.sh` адрес агента в `user.email` заменён на `<agent-email>` (общее правило
28), поэтому её sha256 отличается от строки `SHA256SUMS_fs6a.txt`.

## Вопросы лиду

Нет. Отклонение от буквы, названное явно: драйвер стенда — копия `run_stand_f15c.py` с одним изменённым ожиданием плеча L (буква драйвера F15c при «не задана»
ждёт `mode=0`, п. 454(г)(1) — `modes=1`); классы A/B/C и разбор фатала — дословно.

## Не заявляется

Что Б4 воспроизводится в игре на текущих сборках и что его правка нужна игре; что p_s стенда — частота игры; что `KernelRead` под гонкой падает так же;
что Б4 теряет сохранения; что Ф21 случается в игре; что Linux-ветка (A′) верна; что сборка детерминирована при другом каталоге; что FS6 работает в игре
(дыма не было, до FS6c) и что FS6 установлен (до FS6d); что Ф19 `FIXED`; что SPIR-V корректен для устройства и картинка верна; ни одно число — не выигрыш;
60 FPS не обещаются.
