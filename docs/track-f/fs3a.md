# FS3a (`HPP-447`, Emu Engineer): третий бинарь отгрузки трека F (FS3) — умолчание `KYTY_FIX_B42=1` и строка `FixB42Ext`

Решение лида — `17b4aed6:docs/ROADMAP.md:19917` п. 367 (якорь «367. **Звено F9h трека F (`HPP-425`, лид)»; +1 — «прошла; счёт трека F, не отгрузка»),
подпункт (г)(1) — `17b4aed6:docs/ROADMAP.md:19943` (якорь «(г) **Отгрузка — FS3»; +1 — «(1) **FS3a (Emu Engineer, без замка).**»). Вход — код F9e2c
(`6fde3ad5:docs/track-f/f9e2c.md:13`, якорь «- Коммиты: **`main` `0b9dc0c9`**»; +1 — «F9e2b `0cbaa644`, дерево = `0cbaa644`»). Игра не запускалась;
установленный бинарь `4aa62e95` и кэши не тронуты (sha256 `ps5 em/kyty_emulator.exe` после сборки — `4aa62e95f74e…`). Время — UTC по `date -u`, события —
`C:/kyty/f287/fs3/times.txt`. Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно. Замка `C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP`
за звено не было (каждая команда начиналась проверкой). **WIP по дыму: бинарь собран и проверен тестами, игрой не проверялся** (теги — FS3c после FS3b).

## Итог

- **Коммит кода: `main` `4e72289e`** (родитель `e07148f9`; только `src/graphics/host_gpu/renderer/pipeline/descriptors.cpp`, +22/−3, `--only`).
- **Worktree `C:/kyty/f287/fs3/fs3a/wt` — `d515b901` = cherry-pick `4e72289e` на `722c5e7f`** (F9e2c: `4414e235` + F9e2 `7662bb28` + F9e2b `64de099c` +
  F9e2c `722c5e7f`); `src/graphics` worktree = `main` `4e72289e` (`git diff --quiet 4e72289e d515b901 -- src/graphics` ✓); `git status --short` — 0 строк;
  CR в `src/` — 0 из 456 файлов.
- **Бинарь: sha256 `540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1`**, копия `C:/kyty/f287/bin/kyty_emulator_540c035a.exe` (sha256 тот же;
  `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe`). **Не установка.**
- **Подпись трансляции `KYTY_SHADER_SOURCE_HASH` = `56189185f9e9f9a0ea5174f3f85206e6d099db3d` = P23** (`build/kytyGitVersion.h:9`, 1 вхождение в exe);
  `KYTY_GIT_REVISION` = `d515b9016933…` (`:7`). Дифф против `4414e235` не задевает `src/graphics/shader` [c].
- `check_gate_order.py` (`C:/kyty/s113/`, `--src wt/src`) — `GATE ORDER: clean`, вывод байт в байт = F9e2c (гейтов и ручек правка не добавляет).
- **`shader_cfg_tests` при умолчаниях — 127 тестов, падение 1 — Б11** (`IMAGE_SAMPLE_C` / `IMAGE_SAMPLE_C_LZ`), rc 0; лог = P23/F9e2c **кроме одной строки
  времени**: строка 64 `ASTRO BOT PS 5457 structurize: … elapsed_ms=19` (у P23 — `elapsed_ms=18`); с заменой `elapsed_ms=\d+` логи равны [c]. sha256 лога
  `a074f1b3…` (у P23 `5a60758a…`) — отличие только в этом числе миллисекунд.
- В exe строки `FixB42Ext: mode=`, `FixB42: mode=`, `KYTY_FIX_B42` — по 1. Предупреждение сборки в правленом файле — одно, прежнее (`descriptors.cpp:611`
  `-Wreturn-type`).
- **Таблица умолчаний** (`knobs_fs3a.py d515b901`): умолчание 1 — ровно `KYTY_FIX_B1B`, `KYTY_FIX_B26`, `KYTY_FIX_B42`, `KYTY_FIX_B9A`, `KYTY_FIX_DUALSRC`,
  `KYTY_FIX_MINIMIZE`; `DEFAULT-ON == expected: True`, `ALL OK`.
- **Дифф worktree против `4414e235` — 3 файла Б42**: `textureCache.cpp` +31/−1, `textureCache.h` +33/−1, `descriptors.cpp` +148/−1 [c].

## Код (`4e72289e:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp`)

**(1) Умолчание** — `FixB42Enabled` (`:3646–3654`; в worktree `d515b901` те же строки):

```cpp
bool FixB42Enabled() {
	// Track F, FS3a (HPP-447, ROADMAP s122 item 367(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any
	// other value as EnvValueOn (the form of FSa / FS2a).
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_FIX_B42");
		return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);
	}();
	return enabled;
}
```

Форма = `KYTY_FIX_MINIMIZE` (`swapchain.cpp:311–312`) и `KYTY_FIX_B9A` (`libAudio.cpp:374–375`): не задана или `""` → 1; `0/false/off/no` (без учёта регистра,
точное совпадение) → 0; прочее — `EnvValueOn` (`src/common/envFlag.h:14`) [c]. Заголовочный комментарий блока (`:3628–3629`) переписан на новое умолчание.
Строки «on» в лог эта ручка не пишет (её состояние видно полем `mode=` строк `FixB42:` и `FixB42Ext:`), как и до FS3a.

**(2) Строка `FixB42Ext`** — `FixB42Note` (`:3734–3741`), до ограничителя строки `FixB42:` (`:3742`):

```cpp
	if (probe.kind == FixB42Kind::Hit && counts.ext_lines < 64 &&
	    (counts.ext_lines == 0 || frame - counts.ext_printed_at >= 600u)) {
		counts.ext_lines++;
		counts.ext_printed_at = frame;
		LOGF("FixB42Ext: mode=%d extent=%ux%u hit=%" PRIu64 " applied=%" PRIu64 " drawn=%" PRIu64 " rearm=%" PRIu64
		     " frame=%u\n",
		     FixB42Enabled() ? 1 : 0, width, height, counts.hit, counts.applied, counts.drawn, counts.rearm, frame);
	}
```

- «При росте `hit` или `applied` экстента»: `applied` растёт только вместе с `hit` (`:3722–3730`: `counts.applied++` — внутри ветки `Hit`), поэтому условие
  роста — `probe.kind == Hit` этого вызова [c]. Вызов с `Drawn` строки `FixB42Ext` не пишет.
- Первая строка экстента — сразу; далее не чаще раза в 600 кадров **этого экстента** (`ext_printed_at` — поле записи экстента); не больше 64 строк на экстент.
- Счётчики строки — накопленные счётчики экстента после инкремента этого вызова (те же, что у `FixB42:`); `frame` — `GpuTimeProfiler::Frame()` вызова.
- Общий бюджет 256 строк, частота и форма строки `FixB42:` — без изменений (дифф их строк не задевает, `lines`/`printed_at` новой строкой не трогаются) [c].
- Строки печатаются при `mode=0` и `mode=1` (как `FixB42:`).

## Состояние, вводимое правкой

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `enabled` (static local, `:3649`) | один раз — первый вызов `FixB42Enabled` (C++11 magic static, потокобезопасно) | нет — на время процесса | как до FS3a (была static local с `EnvFlagOn`); значение — функция окружения процесса |
| `Counts::ext_lines` (`:3711`) | `++` в `:3736` под `std::scoped_lock lock {m}` (`:3720`) | нет — запись экстента в static `by_extent` живёт до конца процесса | только счёт строк лога; в условия пробы, `applied`, `FindRenderTarget` и кэш не входит |
| `Counts::ext_printed_at` (`:3712`) | `= frame` в `:3737` под тем же замком | нет — как выше | только частота строки лога |

Выходы `FixB42Note`: ранний `return` `:3743` (ограничитель `FixB42:`) — после блока `FixB42Ext`, поэтому строка экстента от бюджета `FixB42:` не зависит;
конец функции. Оба выхода — под `scoped_lock`, снятие замка автоматическое. Состояния, которое переживало бы вызов и влияло на эмуляцию, правка не вводит:
поля читаются только условием `:3734–3735` [c].

## Таблица умолчаний (`knobs_fs3a.py d515b901`, вывод `knobs_fs3a.out.txt`)

Сканер — копия `knobs_fs2a.py` (FS2a) с ожидаемым набором + `KYTY_FIX_B42`: каждое имя `KYTY_*` на строках `+/−` `git diff 4fc501f4 d515b901 -- src/`
(57 файлов, +8 768/−135; 23 имени), все строки нового дерева с этим именем и механический класс; классы `read by hand` прочитаны по коду `d515b901`:

| Имя | Место чтения (`d515b901`) | Умолчание |
|---|---|---|
| `KYTY_FIX_B26` | `ShaderDecoder.cpp:331` | **1** (unset = ON) |
| `KYTY_FIX_B1B` | `ShaderDecoder.cpp:346` | **1** |
| `KYTY_FIX_DUALSRC` | `vulkanWindow.cpp:666` | **1** |
| `KYTY_FIX_MINIMIZE` | `swapchain.cpp:311` | **1** |
| `KYTY_FIX_B9A` | `libAudio.cpp:374` | **1** |
| `KYTY_FIX_B42` | `descriptors.cpp:3650` | **1** (FS3a) |
| `KYTY_ARM_INLINE`, `KYTY_ARM_IN_COPY`, `KYTY_ARM_LOSS_WIN`, `KYTY_B2_REUSE`, `KYTY_BIND_LEAN`, `KYTY_DISP_CEILING`, `KYTY_PROT_CEILING`, `KYTY_REBIND_CENSUS`, `KYTY_REBIND_SLOW_CENSUS` | строки `KNOB_DEFINITIONS` `gates.cpp:440–473` | 0 (столбец по умолчанию) |
| `KYTY_AUDIO_SYNC` | `pthread.cpp:182` (`value == nullptr \|\| atoi != 0`) | прежний путь (строка `pthread.cpp` вне диффа; новое чтение — `gamePatchFile.cpp:70`, только при `KYTY_GAME_PATCH`) |
| `KYTY_GAME_PATCH` | `emulator.cpp:253`, `gamePatchFile.cpp:62` | 0 (не задана / `""` — файл не читается) |
| `KYTY_PVAR` | `pvar.cpp:169` (unset/`""`/`0` → 0), `gamePatchFile.cpp:69` | 0 |
| `KYTY_POKE` | `runtimeLinker.cpp:1557` (`!= nullptr`), `gamePatchFile.cpp:71` | 0 |
| `KYTY_DUMP_GCN` | `pipelineCache.cpp:1254`, `:1298`, `:3593` (`!= nullptr && …`) | 0 |
| `KYTY_S_PCW` | `pipelineCache.cpp:277` (`== "1"`) | 0 |
| `KYTY_S_PCW_FORCE_MS` | `pipelineCache.cpp:288` (unset → 0) | 0 |
| `KYTY_TEST_MINIMIZE` | `window.cpp:1055` (unset/`""` → стенд выключен) | 0 |

`KYTY_S_PCW*` — код S5a, вошедший в FS2 `9c9d86ae` (`git grep '"KYTY_S_PCW"' 9c9d86ae -- src/` — 1 файл) и в P23 `4414e235`; кода трека S после `4414e235`
в бинаре нет (дифф против `4414e235` — 3 файла Б42) [c]. Кода трека P после `4414e235` в бинаре нет по той же причине.

## Сборка

`mk_wt_fs3a.sh` (копия `mk_wt_f9e2c.sh` на `722c5e7f` без cherry-pick; подмодули как P23) 04:39:35–04:39:44Z; патч worktree тем же скриптом
`patch_fs3a.py`, что и `main` (`cmp` файла ✓), `check_gate_order.py`; configure 04:40:07–04:40:57Z; сборка-проверка 04:41:04–04:42:37Z; коммит `main` 04:43:03Z;
cherry-pick 04:43:12Z; версия и пересборка 04:43:18–04:43:43Z; тесты (сборка 04:43:50–04:44:26Z, прогон 04:44:33Z). Все шаги сборки — под `lockrun.sh` (убивает
шаг при замке или `STOP`; в FS3a добавлен предел шага 540 с — выход 6, шаг повторяется), флаги = F9e2c/P23 (`build_fs3a.cmd` — копия `build_f9e2c.cmd` с путями
`fs3\fs3a`). `CMakeCache.txt`: `Kyty_SOURCE_DIR=C:/kyty/f287/fs3/fs3a/wt`, `Release`.

## Файлы

`C:/kyty/f287/fs3/fs3a/`, копии в `docs/track-f/fs3a/` (текстовые — с окончаниями LF): `patch_fs3a.py`, `patch_main.out.txt`, `patch_wt.out.txt`,
`mk_scripts.py`, `mk_wt_fs3a.sh`, `mk_wt.log`, `build_fs3a.cmd`, `lockrun.sh`, `gate_order.out.txt`, `knobs_fs3a.py`, `knobs_fs3a.out.txt`,
`fs3a_vs_722c5e7f.diff`, `fs3a_vs_4414e235.diff`, `cfgtests_defaults.log`, `commit_msg_code.txt`, `SHA256SUMS_fs3a.txt` (sha256 локальных оригиналов и бинаря).

## Вопросы лиду

1. **Тесты «= P23»** — равны с точностью до одного поля времени (`elapsed_ms` 18 → 19 в строке 64), не байт в байт. Отличие названо по букве п. 367(г)(1);
   считаю равенством по составу и исходам (127 тестов, падение 1 — Б11).
2. **Чтение «при росте `hit` или `applied`»** — строка пишется на вызове, растящем `hit` (в нём же растёт `applied`); попадание, пришедшееся на окно
   600 кадров, отдельной строкой позже не печатается — его покажет следующая строка экстента накопленными счётчиками. Если нужна печать и по росту
   относительно прошлой строки на вызове `Drawn` — это правка одного условия (FS3a2).

## Не заявляется

Что CMASK-очистка — единственная причина Б42 во всех сценах; что на PS5 вода в этих ракурсах чистая; что другие уровни с водой без дефекта; что `applied`
960×540 растёт в неподвижной фазе (до `fs3_u`); что бинарь работает в игре (дыма не было); ни одно число — не выигрыш; 60 FPS не обещаются.
