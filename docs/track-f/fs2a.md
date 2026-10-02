# Трек F, звено FS2a (`HPP-381`, Emu Engineer): коммит и сборка второго бинаря отгрузки трека F (FS2)

Основание — `1452ddc8:docs/ROADMAP.md:15495` «(в) **Отгрузка умолчания — FS2» (контроль +1 — 15496 «идёт на `dac02fb9` — перепечатка FSc»);
звенья — `1452ddc8:docs/ROADMAP.md:15513` «(е) **Звенья» (контроль +1 — 15514 «таблица умолчаний, `shader_cfg_tests»); умолчание `KYTY_FIX_B9A` —
`cc3ceb27:docs/ROADMAP.md:18069` «327. **Звено F6f трека F (`HPP-378`, лид): приёмка F6 — Б9а `FIXED`» (контроль +1 — 18070 «против эталонов — видимых
отличий нет»), подпункт (г): пункт F6f записал Б9а `FIXED` ⇒ умолчание 1. Время — UTC по строкам `C:/kyty/f287/times.txt` («HPP-381 FS2a …»,
17:10:19Z–17:2xZ). Игра не запускалась; установленный exe не тронут (sha256 `ps5 em/kyty_emulator.exe` — `dac02fb9…` после сборки и тестов,
`fs2a/accept_fs2a.out.txt`); процессов с устройством Vulkan нет (`shader_cfg_tests` и `audio_propagation_tests` устройства не создают).
Окно: `HPP-352` — `done` по API перед сборкой; замка и `STOP` нет в каждой команде; чужой замок трека S (`go_s.sh c3_0`) замечен 17:18:23Z перед
тестами — ожидание без записи и процессов до снятия 17:21:28Z.

## 1. Коммит

`main` **`9c9d86ae`** (родитель `2e6cfec2` — `main` на старте звена; `git merge-base --is-ancestor 95eec776 HEAD` — да): два файла, +13 / −8
(`fs2a/fs2a_diff.patch`), коммит `git.exe --only` двух файлов. Патч — `fs2a/patch_fs2a.py` (якоря целыми строками, LF).

- `src/graphics/presentation/window/swapchain.cpp` — `FixMinimizeEnabled()`: чтение `Common::EnvFlagOn("KYTY_FIX_MINIMIZE")` заменено формой FSa
  (`9c9d86ae:src/graphics/presentation/window/swapchain.cpp:311` «`const char* value = std::getenv("KYTY_FIX_MINIMIZE");`», +1 — 312
  «`const bool  on    = value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);`»); комментарий над функцией — умолчание ON с FS2a,
  п. 298(в). Прочее (статический флаг, `LOGF("FixMinimize: on")`, все ветви F5a/F5a2 за `FixMinimizeEnabled()`) — прежнее.
- `src/libs/libAudio.cpp` — `LIB_DEFINE(InitAudio_1_AudioPropagation)`: чтение `Common::EnvFlagOn("KYTY_FIX_B9A")` заменено той же формой
  (`9c9d86ae:src/libs/libAudio.cpp:374` «`const char* fix_b9a_value = std::getenv("KYTY_FIX_B9A");`», +1 — 375 «`const bool  fix_b9a       = …`»);
  комментарий у чтения и шапка F6 — умолчание ON с FS2a, п. 298(в), 327(г). Прочее (`g_b9a_enabled`, `LOGF("FixB9a: on")`, регистрация 16 NID) — прежнее.

Поведение: не задана или `""` — 1; `0/false/off/no` (без учёта регистра) — 0, прежний путь; прочее — `Common::EnvValueOn` (как раньше). Стенд
`KYTY_TEST_MINIMIZE` не тронут (по умолчанию не задан — выключен). **Нового состояния правка не вводит** (статический флаг `FixMinimizeEnabled` и
`g_b9a_enabled` были у F5a / F6c; меняется только значение выражения при незаданной переменной) — список мест установки и снятия не требуется.
Разность против F6c: `git diff 5f67f829 9c9d86ae -- src/libs/libAudio.cpp` — +7 / −4, только чтение и комментарии (путь `=1` по умолчанию = путь F6c
при `=1` — член FS2b). Против FSa: `git diff --stat 95eec776 9c9d86ae -- src/` — `swapchain.cpp` (FS2a) и `libAudio.cpp` (F6c `5f67f829` + FS2a);
`src/graphics/shader/**` — без изменений.

Порядок гейтов: `check_gate_order.py` (`C:/kyty/s136/step3/`) — `GATE ORDER: clean`, вывод байт в байт как у FSa (`fs2a/gate_order.out.txt`).

## 2. Сборка

- Worktree `C:/kyty/f287/fs2a/wt` — `git worktree add --detach` на `9c9d86ae` с `core.autocrlf=false` (`fs2a/mk_wt_fs2a.sh` — копия `mk_wt_fsa.sh`
  с путём); подмодули — как FSa. `git status --short` — 0 строк; файлов `src/` с байтом CR — 0 из 452 (`fs2a/mk_wt.log`).
- Сборка — `fs2a/build_fs2a.cmd` (копия `build_fsa.cmd`: два пути, в `tests` добавлен `audio_propagation_tests` как в `build_f6c.cmd`), папка
  `C:/kyty/f287/fs2a/build`, configure + build rc 0 (конец 17:16:34Z).
- **Бинарь: sha256 `bbad499c56b744dfcef85b7556735c025ebb3db185b6bb9b02e7a0b3a228eb55`**, 24 609 792 байта; копия
  `C:/kyty/f287/bin/kyty_emulator_bbad499c.exe` (sha256 сверен). **Не установлен.**
- **Подпись трансляции: `KYTY_SHADER_SOURCE_HASH` = `56189185f9e9f9a0ea5174f3f85206e6d099db3d`** (`build/kytyGitVersion.h`; в exe — 1 раз) — **равна FS**
  (`dac02fb9`): `src/graphics/shader/**` от `95eec776` до `9c9d86ae` не менялся. `kytyGitVersion.h` без комментариев отличается от FSa только тремя
  строками ревизии (`KytyPS5-2026-09-15-6a2987a-1854-g9c9d86ae`). Кэш трансляции FS (каталог варианта `variant_fixb26_fixb1b`) годится и для FS2.
- Строки в exe (`fs2a/accept_fs2a.py`, вывод `accept_fs2a.out.txt`, `ACCEPT ALL OK`): версия — 2; `DualSrcBlend: supported=` 1, `DualSrcBlend: patched` 1;
  `KYTY_FIX_DUALSRC`, `KYTY_FIX_B26`, `KYTY_FIX_B1B`, `KYTY_FIX_MINIMIZE`, `KYTY_TEST_MINIMIZE`, `FixMinimize: on`, `KYTY_FIX_B9A`, `FixB9a: on`,
  `AudioPropagation: calls` — по 1 (у `dac02fb9` три последние — 0).

## 3. Таблица умолчаний

Источник — `fs2a/knobs_fs2a.py 9c9d86ae` (свой сканер в форме `knobs_fsa.py` + механический класс места чтения; вывод `knobs_fs2a.out.txt`,
`ALL OK`): все имена `"KYTY_*"` на строках `+`/`−` диффа `git diff --ignore-cr-at-eol 4fc501f4 9c9d86ae -- src/` (47 файлов, +7 580 / −130) — 18 имён
(17 у FSa + `KYTY_FIX_B9A`), удалённых чтений 0. Класс «DEFAULT-ON» — чтение `getenv` с `== nullptr || … EnvValueOn` в той же или 2 следующих строках;
строки `KNOB_DEFINITIONS` — по столбцу `fallback`; сверено руками с напечатанными строками.

| ручка | чтение (`9c9d86ae`) | умолчание | при умолчании | строка реестра / прежний путь |
|---|---|---|---|---|
| `KYTY_FIX_B26` | `src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp:331` | **1** | правка Б26б | Б26б `FIXED` (п. 259(а)) |
| `KYTY_FIX_B1B` | `…/ShaderDecoder.cpp:346` | **1** | правка Б1б / Ф9 | Б1б, Ф9 `FIXED` (п. 282(а)) |
| `KYTY_FIX_DUALSRC` | `src/graphics/presentation/window/vulkanWindow.cpp:666` | **1** | `dualSrcBlend` при поддержке + перепись F4a2 | Б35 `FIXED` (п. 281(а)) |
| `KYTY_FIX_MINIMIZE` | `src/graphics/presentation/window/swapchain.cpp:311` | **1** (этим коммитом) | правка Б37 (F5a + F5a2) | Б37 `FIXED` (п. 298) |
| `KYTY_FIX_B9A` | `src/libs/libAudio.cpp:374` | **1** (этим коммитом) | V1 F6a: 16 NID зарегистрированы | Б9а `FIXED` (п. 327) |
| `KYTY_TEST_MINIMIZE` | `src/graphics/presentation/window/window.cpp:1055` | не задана — стенд выключен | `== nullptr` → выход без стенда | 0 — прежний путь (измерение) |
| `KYTY_S_PCW` | `src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:277` | 0 (1 — только `"1"`) | как `4fc501f4` | 0 — прежний путь |
| `KYTY_S_PCW_FORCE_MS` | `pipelineCache.cpp:288` | 0 | выкл. | 0 — прежний путь (измерение) |
| `KYTY_DUMP_GCN` | `pipelineCache.cpp:1298` (новое, только `"2"`); `:1254`, `:3593` — прежние | выкл. | дампа нет | 0 — прежний путь (измерение) |
| `KYTY_PROT_CEILING`, `KYTY_ARM_IN_COPY`, `KYTY_ARM_INLINE`, `KYTY_ARM_LOSS_WIN`, `KYTY_DISP_CEILING`, `KYTY_REBIND_CENSUS`, `KYTY_B2_REUSE`, `KYTY_REBIND_SLOW_CENSUS`, `KYTY_BIND_LEAN` | `src/common/gates.cpp:440…473` (`KNOB_DEFINITIONS`) | `fallback` 0 | выкл. | 0 — прежний путь |

**Вывод: умолчание 1 — ровно `KYTY_FIX_B26`, `KYTY_FIX_B1B`, `KYTY_FIX_DUALSRC`, `KYTY_FIX_MINIMIZE`, `KYTY_FIX_B9A`; прочие — 0 / прежний путь; стопа
нет.** Первый прогон сканера отнёс к «DEFAULT-ON» `KYTY_TEST_MINIMIZE` (`if (value == nullptr || …) return c;` — защитный выход, стенд выключен):
дефект эвристики сканера, исправлен до вывода в файл (класс требует `EnvValueOn` в цепочке `||`), строка `times.txt`.

## 4. Тесты (worktree-сборка, без единой переменной `KYTY_*` в окружении, кроме `KYTY_TESTS_CONTINUE`/`KYTY_TESTS_VERBOSE`)

- `shader_cfg_tests` — **127 тестов, падение 1 — Б11** (`TestNewShaderRecompilerPixelImageSampleLodSelection`: `IMAGE_SAMPLE_C` / `IMAGE_SAMPLE_C_LZ`),
  rc 0; лог `fs2a/cfgtests_defaults.log` совпадает с FSa `cfgtests_defaults.log` с точностью до одного `elapsed_ms` (19 → 18).
- `audio_propagation_tests` — `checks 210, failures 0`, **`ALL OK`**, rc 0 (`=0`: 6 из 22; `=1`: 22 из 22; тест ставит `KYTY_FIX_B9A` явно `0` и `1`,
  умолчание его не затрагивает).

## 5. Состояние и дальше

- **WIP: бинарь не установлен и в игре не запускался** — ревью FS2b (`HPP-382`), регрессия FS2c (`HPP-383`, п. 298(г) + члены Б9а п. 327(г)), установка FS2d.
- Для FS2b: разность коммита — `git diff 2e6cfec2 9c9d86ae -- src/`; против FS — `git diff 95eec776 9c9d86ae -- src/` (F6c + FS2a); путь `=1` по умолчанию
  Б9а — против `5f67f829`; бинарь — копия `bbad499c`, проверочная пересборка — по прочтению п. 286(б).
- Вопросов лиду нет.
- Не заявляется: что без правки свёрнутое окно никогда не ведёт к крэшу; что бинарь при умолчаниях держит Sky Garden или `timestop_casino`; что звук верен;
  корректность любой сцены и проходимость до конца; ни одно число — не выигрыш; 60 FPS не обещаются.

Файлы звена — `C:/kyty/f287/fs2a/`, копии в `docs/track-f/fs2a/`: `patch_fs2a.py`, `fs2a_diff.patch`, `commit_msg.txt`, `gate_order.out.txt`,
`mk_wt_fs2a.sh`, `mk_wt.log`, `build_fs2a.cmd`, `accept_fs2a.py`, `accept_fs2a.out.txt`, `knobs_fs2a.py`, `knobs_fs2a.out.txt`, `cfgtests_defaults.log`,
`audio_propagation_tests.log`.
