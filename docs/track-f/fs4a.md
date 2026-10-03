# FS4a (`HPP-470`, Emu Engineer): четвёртый бинарь отгрузки трека F (FS4) — умолчание `KYTY_FIX_SVAL=1`

Решение лида — `8449030a:docs/ROADMAP.md:20552` п. 378 (якорь «378. **Звено F10f трека F (`HPP-454`, лид): Ф16 `FIXED` по п. 369(в)»; +1 — «прошла; счёт
трека F, не отгрузка; умолчание `KYTY_FIX_SVAL=1`»), подпункт (г)(1) — `8449030a:docs/ROADMAP.md:20588` (якорь «(г) **Отгрузка — FS4, четвёртый бинарь
отгрузки трека F (константы лида):**»; +1 — «(1) **FS4a (Emu Engineer, без замка).**»). Вход — код F10c `68602c4f` и база FS3 `d515b901`
(`cd7977f7:docs/track-f/fs3a.md:13`, якорь «- **Worktree `C:/kyty/f287/fs3/fs3a/wt` — `d515b901` = cherry-pick `4e72289e` на `722c5e7f`**»; +1 —
«`src/graphics` worktree = `main` `4e72289e`»). Игра не запускалась; установленный бинарь `540c035a` и кэши не тронуты (sha256 `ps5 em/kyty_emulator.exe`
после сборки — `540c035ac09f…`). Время — UTC по `date -u`, события — `C:/kyty/f287/times.txt` (строки `FS4a`). Метки: [c] — показано кодом или выводом,
[I] — вывод, [U] — неизвестно. Замка `C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` за звено не было (каждая команда начиналась проверкой).
**WIP по дыму: бинарь собран и проверен тестами, игрой не проверялся** (теги — FS4c после FS4b).

## Итог

- **Коммит кода: `main` `17adaf80`** (родитель `8449030a`; только `src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp`, +8/−3, `--only`).
- **Worktree `C:/kyty/f287/fs4/fs4a/wt` — `3d0e46da` = cherry-pick `17adaf80` на `92d11340` = cherry-pick `68602c4f` на `d515b901` (FS3)**; оба cherry-pick
  без конфликтов; patch-id `68602c4f` = `92d11340` (`8be6b8b1…`), `17adaf80` = `3d0e46da` (`738f74d8…`) [c]; три файла F10c/FS4a в `3d0e46da` = `main`
  `17adaf80` (`git diff --quiet` ✓); `git status --short` — 0 строк; CR в `src/` — 0 из 456 файлов.
- **Бинарь: sha256 `31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5`**, копия `C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe` (sha256 тот же;
  `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe`). **Не установка.**
- **Подпись трансляции `KYTY_SHADER_SOURCE_HASH` = `56189185f9e9f9a0ea5174f3f85206e6d099db3d` = FS3** (`build/kytyGitVersion.h:9`, 1 вхождение в exe);
  `KYTY_GIT_REVISION` = `3d0e46daf83f…` (`:7`). Дифф против `d515b901` не задевает `src/graphics/shader` [c].
- `check_gate_order.py` (`C:/kyty/s113/`, `--src wt/src`) — `GATE ORDER: clean`, вывод байт в байт = FS3a (гейтов и ручек правка не добавляет).
- **`shader_cfg_tests` при умолчаниях (в окружении нет ни одной `KYTY_*`) — 127 тестов, падение 1 — Б11** (`IMAGE_SAMPLE_C` / `IMAGE_SAMPLE_C_LZ`), rc 0;
  лог с заменой `elapsed_ms=\d+` = FS3a [c]; без замены отличается одной строкой 64 (`elapsed_ms` 18 у FS4, 19 у FS3a); sha256 лога `5a60758a…` — тот же,
  что у P23 (`fs3a.md`, «у P23 `5a60758a…`»), то есть байт в байт = P23.
- В exe строки `FixSval: mode=`, `FixSvalStat: validated=`, `KYTY_FIX_SVAL`, `FixB42Ext: mode=` — по 1. Предупреждение сборки в правленом файле — одно, прежнее
  (`pipelineCache.cpp:401` `-Wreturn-type`).
- **Таблица умолчаний** (`knobs_fs4a.py 3d0e46da`): умолчание 1 — ровно `KYTY_FIX_B1B`, `KYTY_FIX_B26`, `KYTY_FIX_B42`, `KYTY_FIX_B9A`, `KYTY_FIX_DUALSRC`,
  `KYTY_FIX_MINIMIZE`, `KYTY_FIX_SVAL`; `DEFAULT-ON == expected: True`, `ALL OK`.
- **Дифф источника FS4 против `d515b901` — 3 файла**: `graphicContext.h` +3, `pipelineCache.cpp` +45/−1, `vulkanWindow.cpp` +2 [c]
  (`diffstat_vs_d515b901.txt`, `fs4a_vs_d515b901.diff`).
- **Коммиты в истории `3d0e46da`** (`git merge-base --is-ancestor`): `d515b901` (FS3a) — да, `92d11340` (копия F10c) — да, `4414e235` (P23) — да; `741e3312`
  (P35), `c9b4268e` (P40) — нет. `4e72289e`, `68602c4f`, `17adaf80` (коммиты `main`) — **нет по букве**: в бинарь они входят копиями cherry-pick
  (`d515b901`, `92d11340`, `3d0e46da`), как и в FS3 `4e72289e` входил копией `d515b901`. Равенство изменений — `git cherry -v 3d0e46da <c> <c>^`: `-` (равное
  изменение есть в истории) у `4e72289e`, `68602c4f`, `17adaf80`; `+` (нет) у `741e3312`, `c9b4268e` [c] (`cherry.out.txt`). См. «Вопросы лиду» 1.

## Код (`17adaf80:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp`, в `3d0e46da` — те же строки)

**Умолчание** — `FixSvalEnabled` (`:1343–1351`), заголовочный комментарий (`:1337–1342`) переписан на новое умолчание:

```cpp
bool FixSvalEnabled() {
	// Track F, FS4a (HPP-470, ROADMAP s122 item 378(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any
	// other value as EnvValueOn (the form of FSa / FS2a / FS3a).
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_FIX_SVAL");
		return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);
	}();
	return enabled;
}
```

Форма = `KYTY_FIX_B42` (`d515b901:descriptors.cpp:3646–3654`), `KYTY_FIX_MINIMIZE`, `KYTY_FIX_B9A`: не задана или `""` → 1; `0/false/off/no` (без учёта
регистра, точное совпадение) → 0; прочее — `EnvValueOn` (`src/common/envFlag.h:14`) [c]. До FS4a — `Common::EnvValueOn(std::getenv("KYTY_FIX_SVAL"))`
(не задана / `""` → 0). Больше в файле ничего не меняется: ветка ON (`ValidatorOptions` с `SetUniformBufferStandardLayout(true)` при включённом у устройства
`uniformBufferStandardLayout`, счётчики и строка `FixSvalStat:` `:1370–1386`), ветка OFF (`tools.Validate(spirv)`), строка `FixSval: mode=… ubo_std_layout=…`
(`:4670`) — как в `68602c4f` [c] (`fs4a_vs_92d11340.diff` — 1 hunk, только `:1337–1351`).

Пути по коду [c]: `ValidateShaderSpirv` возвращает `true` до чтения ручки при `!Config::ShaderValidationEnabled()` (`--shader-validation false`, форма
харнессов) — путь FS3; при `KYTY_FIX_SVAL=0` — прежний вызов `tools.Validate(spirv)` (путь FS3, строка `FixSval: mode=0`); по умолчанию — путь F10c при `=1`.

## Состояние, вводимое правкой

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `enabled` (static local, `:1346`) | один раз — первый вызов `FixSvalEnabled` (C++11 magic static, потокобезопасно; первый вызов — конструктор `PipelineCache` `:4670`, главный поток, до воркеров) | нет — на время процесса | как до FS4a (была static local); значение — функция окружения процесса |

Нового состояния правка не вводит: меняется только выражение инициализации той же static local. Выход функции один (`return enabled`).

## Таблица умолчаний (`knobs_fs4a.py 3d0e46da`, вывод `knobs_fs4a.out.txt`)

Сканер — копия `knobs_fs3a.py` (FS3a) с ожидаемым набором + `KYTY_FIX_SVAL` (`mk_knobs.py`): каждое имя `KYTY_*` на строках `+/−` `git diff 4fc501f4 3d0e46da
-- src/`, все строки нового дерева с этим именем и механический класс. Классы `read by hand` — как в таблице `fs3a.md` (код вне диффа `d515b901..3d0e46da`
тот же); новое имя одно:

| Имя | Место чтения (`3d0e46da`) | Умолчание |
|---|---|---|
| `KYTY_FIX_B26` | `ShaderDecoder.cpp:331` | **1** |
| `KYTY_FIX_B1B` | `ShaderDecoder.cpp:346` | **1** |
| `KYTY_FIX_DUALSRC` | `vulkanWindow.cpp:666` | **1** |
| `KYTY_FIX_MINIMIZE` | `swapchain.cpp:311` | **1** |
| `KYTY_FIX_B9A` | `libAudio.cpp:374` | **1** |
| `KYTY_FIX_B42` | `descriptors.cpp:3650` | **1** |
| `KYTY_FIX_SVAL` | `pipelineCache.cpp:1347` | **1** (FS4a) |
| прочие `KYTY_*` диффа (`KNOB_DEFINITIONS`, `KYTY_AUDIO_SYNC`, `KYTY_GAME_PATCH`, `KYTY_PVAR`, `KYTY_POKE`, `KYTY_DUMP_GCN`, `KYTY_S_PCW*`, `KYTY_TEST_MINIMIZE`) | как `fs3a.md` | 0 или прежний путь |

Номера строк — по выводу сканера на `3d0e46da` (2 строки F10c в `vulkanWindow.cpp` стоят ниже `:666`); дифф `4fc501f4..3d0e46da` — 57 файлов, +8 818/−136.

## Сборка

`mk_wt_fs4a.sh` (копия `mk_wt_fs3a.sh` на `d515b901` + cherry-pick `68602c4f`; подмодули как P23/FS3) 07:50:51Z; патч worktree скриптом `patch_fs4a.py`
(1 якорь — блок комментария и функции целиком, LF), `check_gate_order.py` 07:50:57Z; configure 07:51:03–07:52:28Z; сборка-проверка 07:52:33–07:53:57Z;
патч `main` тем же скриптом (`cmp` файла с worktree ✓) и коммит `17adaf80` 07:54:17Z; `git checkout` файла в worktree и cherry-pick → `3d0e46da` 07:54:25Z;
версия и пересборка 07:54:25–07:54:57Z; бинарь и копия 07:55:06Z; тесты (сборка 07:55:12–07:55:43Z, прогон 07:55:43–07:55:44Z). Все шаги сборки — под
`lockrun.sh` (копия FS3a: убивает шаг при замке или `STOP`, предел шага 540 с), флаги = FS3a (`build_fs4a.cmd` — копия `build_fs3a.cmd` с путями `fs4\fs4a`).
`CMakeCache.txt`: `Kyty_SOURCE_DIR=C:/kyty/f287/fs4/fs4a/wt`, `Release`.

## Файлы

`C:/kyty/f287/fs4/fs4a/`, копии в `docs/track-f/fs4a/` (текстовые — LF): `mk_scripts.py`, `mk_wt_fs4a.sh`, `mk_wt.log`, `build_fs4a.cmd`, `lockrun.sh`,
`patch_fs4a.py`, `patch_wt.out.txt`, `patch_main.out.txt`, `gate_order.out.txt`, `mk_knobs.py`, `knobs_fs4a.py`, `knobs_fs4a.out.txt`, `diffstat_vs_d515b901.txt`,
`fs4a_vs_d515b901.diff`, `fs4a_vs_92d11340.diff`, `cherry.out.txt`, `cfgtests_defaults.log`, `commit_msg_code.txt`, `SHA256SUMS_fs4a.txt` (sha256 локальных
оригиналов и бинаря). В копиях `mk_scripts.py` и `mk_wt_fs4a.sh` адрес агента в `user.email` заменён на `<agent-email>` (общее
правило 28), поэтому их sha256 отличаются от строк `SHA256SUMS_fs4a.txt`.

## Вопросы лиду

1. **`git merge-base --is-ancestor` п. 378(г)(5) по букве.** Построение (г)(1) — cherry-pick — даёт в истории бинаря копии, а не коммиты `main`: `4e72289e`,
   `68602c4f`, `17adaf80` предками `3d0e46da` не являются (как и `4e72289e` — предком FS3 `d515b901`); предки — их копии `d515b901`, `92d11340`, `3d0e46da` с
   равным patch-id. Проверку «бинарь содержит коммит» для этого построения предлагаю читать `git cherry -v <коммит бинаря> <c> <c>^` = `-` (равное изменение
   есть) — так она и выполнена здесь; для бинаря трека P, собранного на `main`, буква `--is-ancestor` выполнима. Решение — лида.
2. **Тесты «= FS3»** — равны с точностью до одного поля времени (`elapsed_ms` в строке 64), как в FS3a; лог байт в байт = P23.

## Не заявляется

Что пользователь запускает игру с проверкой шейдеров; что 151 — все такие PS игры; что `validated` — число PS класса S151; что встроенная проверка не отвергнет
PS другого класса на других уровнях; что SPIR-V корректен для устройства и картинка верна; что бинарь работает в игре (дыма не было); ни одно число — не
выигрыш; 60 FPS не обещаются.
