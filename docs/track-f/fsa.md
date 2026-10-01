# Трек F, звено FSa (`HPP-368`, Emu Engineer): коммит и сборка бинаря отгрузки трека F

Основание — `cc9880e6:docs/ROADMAP.md:14750` «(1) **FSa (Emu Engineer)** — коммит в `main`: умолчание `KYTY_FIX_DUALSRC` 0 → 1» (контроль +1 — 14751
«worktree с LF на этом коммите (не из рабочего дерева: в нём идёт F5a2)»); п. 259(б), п. 281(в)(1). Время — UTC по строкам `C:/kyty/f287/times.txt`
(«FSa …», 14:24:37Z–14:33:19Z). Игра не запускалась; установленная `9235a7ac` не тронута (sha256 `ps5 em/kyty_emulator.exe` — `9235a7ac61f1…` после
сборки); процессов с устройством Vulkan нет (S4 `HPP-315` — `in_progress` по API 14:23:34Z, п. 277(г)).

## 1. Коммит

`main` **`95eec776`** (родитель `b08a5723`): один файл `src/graphics/presentation/window/vulkanWindow.cpp`, +6 / −3 (`fsa/fsa_diff.patch`).
Отдельной константы умолчания в коде не было — ручка читалась `Common::EnvFlagOn("KYTY_FIX_DUALSRC")` (не задана = 0). Разность — только выражение
чтения ручки и её комментарий; форма умолчания 1 — та же, что у `FixB26Enabled` / `FixB1BEnabled` (`95eec776:src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp:331`):
не задана или `""` — 1, иначе `Common::EnvValueOn` (`0/false/off/no` — 0, путь F4c). Новое чтение — `95eec776:src/graphics/presentation/window/vulkanWindow.cpp:666`
«`const char* dual_src_value    = std::getenv("KYTY_FIX_DUALSRC");`». Иных строк нет: `dual_src_supported`, `LOGF("DualSrcBlend: supported=%d enabled=%d")`,
`graphics.dual_src_blend_enabled` — прежние. Нового состояния (TLS, поле, счётчик) правка не вводит — список мест установки и снятия не требуется.

Порядок гейтов: `check_gate_order.py` (`C:/kyty/s136/step3/`) — вывод байт в байт как у F4a2 и F5a2 (`fsa/gate_order.out.txt`; правка гейтов и ручек
`gates.*` не трогает). Рабочее дерево `C:/kyty/KytyPS5`: правка F5a2 к началу звена уже в `main` (`01ca15d1`), посторонних изменений в `src/` нет;
коммит — `git.exe --only` одного файла.

## 2. Сборка

- Worktree `C:/kyty/f287/fsa/wt` — `git worktree add --detach` на `95eec776` с `core.autocrlf=false` (`fsa/mk_wt_fsa.sh`); подмодули — как F5a2
  (`git archive` гитлинков, `ffmpeg-core` — локальный `--shared` клон). `git status --short` — 0 строк; файлов `src/` с байтом CR — 0 из 452 (`fsa/mk_wt.log`).
  В отличие от F4a2/F5a2 перезаписи CRLF нет: сборка отгрузки — LF-дерево коммита (п. 277(б)(4)).
- Сборка — `fsa/build_fsa.cmd` (копия `build_f5a2.cmd` с двумя путями; флаги `build_local.cmd`), папка `C:/kyty/f287/fsa/build`, configure + build rc 0.
- **Бинарь: sha256 `dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e`**, 24 573 952 байта; копия `C:/kyty/f287/bin/kyty_emulator_dac02fb9.exe`
  (sha256 сверен). **Не установлен.**
- **Подпись трансляции: `KYTY_SHADER_SOURCE_HASH` = `56189185f9e9f9a0ea5174f3f85206e6d099db3d`** (`build/kytyGitVersion.h`; в exe — 1 раз). Совпадает с
  LF-сборкой `478868b5` (п. 277(б)(4)) — ожидаемо: от `478868b5` до `95eec776` в `src/graphics/shader/**` правок нет (F5a, F5a2, FSa — только `presentation/`
  и `libs/libC.cpp`). Бинарь F3d `2e6df8f0` несёт подпись `fba4fbfd` (CRLF-дерево F3b), `9235a7ac` — `699c1e4b`: **у бинаря отгрузки кэш трансляции
  холодный** против обоих (каталог варианта по умолчанию — `variant_fixb26_fixb1b`).
- Строки в exe (`fsa/accept_fsa.py`, вывод `accept_fsa.out.txt` `138519d9…`, `ACCEPT ALL OK`): версия `KytyPS5-2026-09-15-6a2987a-1766-g95eec776`;
  `DualSrcBlend: supported=` 1, `DualSrcBlend: patched` 1; имена `KYTY_FIX_DUALSRC`, `KYTY_FIX_B26`, `KYTY_FIX_B1B`, `KYTY_FIX_MINIMIZE`,
  `KYTY_TEST_MINIMIZE` — по 1. Первые два прогона проверки — `FAILED` из-за неверных ожиданий самого скрипта (полного хэша ревизии в exe нет; строка
  версии встречается 2 раза) — бинарь тот же, строка `times.txt`.

## 3. Таблица умолчаний

Источник — `fsa/knobs_fsa.py 95eec776` (вывод `knobs_fsa.out.txt`): все имена `"KYTY_*"` на строках `+`/`−` диффа `git diff --ignore-cr-at-eol 4fc501f4
95eec776 -- src/` (46 файлов, +7 295 / −130; 31 коммит в `src/`) — 17 имён, удалённых чтений 0; плюс просмотр всех строк диффа с `getenv` /
`EnvFlagOn` / `EnvValueOn` / `*Enabled()` — иных изменённых чтений нет (строка `4938/4949` диффа: `!bln_lean &&` перед прежним
`BufferUploadEpochEnabled()` — при `bindlean` 0 прежнее условие).

| ручка | чтение (`95eec776`) | умолчание | при умолчании | строка реестра / место прежнего пути |
|---|---|---|---|---|
| `KYTY_FIX_B26` | `src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp:331` | **1** | правка Б26б | Б26б `FIXED` (п. 259(а), реестр §11) |
| `KYTY_FIX_B1B` | `src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp:346` | **1** | правка Б1б / Ф9 | Б1б, Ф9 `FIXED` (п. 282(а), реестр §16) |
| `KYTY_FIX_DUALSRC` | `src/graphics/presentation/window/vulkanWindow.cpp:666` | **1** (этим коммитом) | `dualSrcBlend` включён при поддержке + перепись F4a2 | Б35 `FIXED` (п. 281(а), реестр §15) |
| `KYTY_FIX_MINIMIZE` | `src/graphics/presentation/window/swapchain.cpp:310` (`EnvFlagOn`) | 0 | прежний путь: все ветви F5a/F5a2 за `FixMinimizeEnabled()`; в `Presenter::Present` при `fix_minimize=false` условия `screenshot && !(false && …)` = прежние `screenshot` | 0 — прежний путь (F5b п. 280(а) для `d2811535`; `01ca15d1` — чтение исполнителя, ревью F5b2 впереди) |
| `KYTY_TEST_MINIMIZE` | `src/graphics/presentation/window/window.cpp:1055` | не задана — стенд выключен | одна `getenv` + статический флаг на запись лога гостя (`src/libs/libC.cpp`, вызов из `fwrite`) | 0 — прежний путь (стенд, только измерение) |
| `KYTY_S_PCW` | `src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:277` | 0 (1 — только ровно `"1"`) | запись кэша драйвера под `m_mutex`, как в `4fc501f4` | 0 — прежний путь |
| `KYTY_S_PCW_FORCE_MS` | `pipelineCache.cpp:288` | 0 | выкл. | 0 — прежний путь (измерение) |
| `KYTY_DUMP_GCN` | новое чтение `pipelineCache.cpp:1298` (только `"2"`); прежние `:1254`, `:3593` не менялись | выкл. | дампа нет | 0 — прежний путь (измерение) |
| `KYTY_PROT_CEILING` | `src/common/gates.cpp:440` (`KNOB_DEFINITIONS`, `fallback`) | 0 | выкл. | 0 — прежний путь (с. 128, измерение) |
| `KYTY_ARM_IN_COPY` | `gates.cpp:445` | 0 | выкл. | 0 — прежний путь (с. 129–130, не отгружен) |
| `KYTY_ARM_INLINE` | `gates.cpp:449` | 0 | выкл. | 0 — прежний путь |
| `KYTY_ARM_LOSS_WIN` | `gates.cpp:453` | 0 | выкл. | 0 — прежний путь |
| `KYTY_DISP_CEILING` | `gates.cpp:457` | 0 | выкл. | 0 — прежний путь |
| `KYTY_REBIND_CENSUS` | `gates.cpp:461` | 0 | выкл. | 0 — прежний путь |
| `KYTY_B2_REUSE` | `gates.cpp:465` | 0 | выкл. | 0 — прежний путь |
| `KYTY_REBIND_SLOW_CENSUS` | `gates.cpp:469` | 0 | выкл. | 0 — прежний путь |
| `KYTY_BIND_LEAN` | `gates.cpp:473` | 0 | выкл. | 0 — прежний путь |

Прежние строки таблиц ручек и гейтов не менялись (`KYTY_RT_SKIP` — `fallback` 1, как в `4fc501f4`; дифф `gates.cpp` — только добавленные строки и
перенос комментария «LAST row»). **Вывод: умолчание 1 — ровно `KYTY_FIX_B26`, `KYTY_FIX_B1B`, `KYTY_FIX_DUALSRC`; иных ручек с умолчанием, меняющим
поведение `9235a7ac`, нет — стопа нет.**

Член исполнителя [I] (п. 258(д), вердикта не задаёт): таблица охватывает чтения ручек; код без ручки в диффе `4fc501f4..95eec776` (с. 128–136: `pageManager`,
`bufferCache`, `descriptors`, `videoOut`, `frameStats` — за ручками и гейтами с умолчанием 0 по их комментариям) построчно не проверялся; он же был в
бинаре F3d `2e6df8f0` (дерево `478868b5`), от которого бинарь отгрузки отличается только F5a, F5a2 (за `KYTY_FIX_MINIMIZE=0`, стенд выключен) и FSa
(`git diff 478868b5 95eec776 -- src/`: 6 файлов, +190 / −5).

## 4. Тесты

`shader_cfg_tests` (worktree, без единой переменной `KYTY_*` в окружении, кроме `KYTY_TESTS_CONTINUE`/`KYTY_TESTS_VERBOSE`) — **127 тестов, падение 1 —
Б11** (`TestNewShaderRecompilerPixelImageSampleLodSelection`: `IMAGE_SAMPLE_C` / `IMAGE_SAMPLE_C_LZ`), rc 0; лог (`cfgtests_defaults.log`
`a074f1b3…`) совпадает с F5a2 `cfg_tests_min0.txt` с точностью до времени. `shader_cfg_tests` устройства Vulkan не создаёт (в `tests/` создание
есть только в `ShaderRecompilerComputeTests.cpp`).

## 5. Состояние и дальше

- **WIP: бинарь не установлен и в игре не запускался** — дым и регрессия — FSc (`HPP-370`) после ревью FSb (`HPP-369`).
- Для FSb: разность коммита против `478868b5` — `git diff 478868b5 95eec776 -- src/` (F5a + F5a2 + FSa); против `65a09c82` — плюс F3b. F5a2 (`01ca15d1`)
  ещё не прошёл F5b2 (`HPP-367`); в бинаре отгрузки он за `KYTY_FIX_MINIMIZE=0`.
- Не заявляется: что бинарь при умолчаниях держит Sky Garden или `mini_giants_garden`; что `=0` у `KYTY_FIX_DUALSRC` на этом бинаре тождествен `c9a5e198`;
  что код без ручек с. 128–136 поведенчески равен `4fc501f4`; ни одно число — не выигрыш; 60 FPS не обещаются.

Файлы звена — `C:/kyty/f287/fsa/`, копии в `docs/track-f/fsa/`: `patch_fsa.py`, `fsa_diff.patch`, `gate_order.out.txt`, `mk_wt_fsa.sh`, `mk_wt.log`,
`build_fsa.cmd`, `accept_fsa.py`, `accept_fsa.out.txt`, `knobs_fsa.py`, `knobs_fsa.out.txt`, `cfgtests_defaults.log`.
