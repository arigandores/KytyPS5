# Трек F, звено FSb (`HPP-369`, Red Team): ревью бинаря отгрузки трека F (FSa)

**Вердикт: PASS_WITH_FIXES.** RC — 1 (RC1, владелец — лид: прочтение п. 282(г)(2)(3) «sha совпадают»), замечаний — 3 (N1–N3), правок кода и
бинаря нет. По букве п. (3) sha своей сборки **не совпадает** с FSa; вариант исполнителя — сборки равны с точностью до пути worktree и метки
времени (§3). Бинарь FSc — только копия `C:/kyty/f287/bin/kyty_emulator_dac02fb9.exe` (как и требует п. 282(г)(3)).

Основание — `cc9880e6:docs/ROADMAP.md:14745` «(г) **Ответ на п. 259(е)(8)» (контроль +1 — 14746 «`KYTY_FIX_B1B` (`FIXED`, (а))»), член (2) —
`cc9880e6:docs/ROADMAP.md:14756` «(2) **FSb (Red Team)** — ревью FSa: разность коммита против» (контроль +1 — 14757 «чистого worktree — sha и
подпись совпадают»).
Прочитаны до первого действия: п. 228, 259(б), 262(б), 281(в)–(г), 282 (`cc9880e6`); отчёт FSa `73818db3:docs/track-f/fsa.md`; комментарии FSa и
приёмки лида в `HPP-368`. Время — UTC по строкам «FSb …» `C:/kyty/f287/times.txt` (14:38:43Z–14:50Z). Игра не запускалась; установленная
`9235a7ac` не тронута; процессов с устройством Vulkan нет (`shader_cfg_tests` устройства не создаёт). Замка за звено не было (проверка в первой
строке каждой команды); `HPP-352`, `HPP-315`, `HPP-353` — `blocked` по API 14:38:43Z перед сборкой, `HPP-352` — `blocked` повторно перед сборкой
`kyty_emulator` и перед тестами.

## 1. Разность коммита FSa против родителя — только ручка умолчания ✓

`95eec776` (родитель `b08a5723`, документы): один файл `src/graphics/presentation/window/vulkanWindow.cpp` +6 / −3. `git diff 01ca15d1 95eec776 -- src/`
(последний коммит `src/` перед FSa) — тот же единственный файл. Заменено только выражение чтения: было `Common::EnvFlagOn("KYTY_FIX_DUALSRC")`,
стало `getenv` + `nullptr || "" || Common::EnvValueOn(value)` — форма `FixB26Enabled` (`95eec776:src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp:331`),
и комментарий. Константы умолчания в коде не было — разность шире буквы «только константа», поведенчески это ровно смена умолчания 0 → 1
(согласен со строкой проверки лида в `HPP-368`). Таблица значений [c-код, `95eec776:src/common/envFlag.h:31` «return !(equals("0") || …»]:

| значение `KYTY_FIX_DUALSRC` | `c9a5e198` (`EnvFlagOn`) | `95eec776` |
|---|---|---|
| не задана | 0 | **1** |
| `""` | 0 | **1** |
| `0`, `false`, `off`, `no` (любой регистр) | 0 | 0 |
| любое иное (`1`, `2`, `yes`, ` `) | 1 | 1 |

Против `65a09c82`/`478868b5` (буква п. 282(г)(2)): `git diff 478868b5 95eec776 -- src/` — 6 файлов +190 / −5 = F5a (`d2811535`) + F5a2
(`01ca15d1`) + FSa; F5a/F5a2 — §5.

## 2. Таблица умолчаний — своим чтением ✓ (совпадает с FSa)

Свой сканер `knobs_fsb.py` (кода FSa не импортирует; вывод `knobs_fsb.out.txt` `80481849…`) по `git diff -U0 4fc501f4 95eec776 -- src/`: строки
`+`/`−` с вызовом чтения окружения (`getenv`, `EnvFlagOn`, `EnvValueOn`, `GetEnvironmentVariable`, `_wgetenv`, `_dupenv_s`; комментарии
отрезаны), все литералы `KYTY_*`, строки `KNOB_DEFINITIONS`.

- Добавленных строк с вызовом чтения — 11 (7 чтений: `KYTY_S_PCW` `pipelineCache.cpp:277`, `KYTY_S_PCW_FORCE_MS` `:288`, `KYTY_DUMP_GCN` `:1298`,
  `KYTY_FIX_MINIMIZE` `swapchain.cpp:310`, `KYTY_FIX_DUALSRC` `vulkanWindow.cpp:666`, `KYTY_TEST_MINIMIZE` `window.cpp:1055`, `KYTY_FIX_B26`
  `ShaderDecoder.cpp:331`, `KYTY_FIX_B1B` `:346`; продолжения строк — 3). **Удалённых или изменённых прежних чтений — 0; изменённых прежних строк
  `KNOB_DEFINITIONS` — 0.**
- Строк `KNOB_DEFINITIONS` добавлено 9, у всех `fallback` 0: `protceil` 0..2, `armcopy` 0..4, `acinline` 0..1, `lwin` 0..3, `dispceil` 0..1, `rbcen` 0..2,
  `b2reuse` 0..3, `rbslow` 0..1, `bindlean` 0..3. `KYTY_RT_SKIP` — прежняя строка (`fallback` 1, как `4fc501f4`). Ручки читаются только из окружения
  или файла `KYTY_GATE_FILE` (`95eec776:src/common/gates.cpp:535`) — при незаданной переменной файла нет.
- Литералов `KYTY_*` — 27 имён; 10 сверх 17 чтений — в комментариях (`KYTY_ASYNC_COPY`, `KYTY_ASYNC_PROTECT`, `KYTY_AV_TRACE`, `KYTY_FRAME_TRACE`,
  `KYTY_PARALLEL_COPY`, `KYTY_PIPELINE_SALT`, `KYTY_SKIP_CS`) или макросы (`KYTY_CLASS_NO_COPY`, `KYTY_PLATFORM`, `KYTY_PLATFORM_WINDOWS`) — совпадает
  со сканом лида.
- Умолчания по коду чтения [c-код]: `KYTY_FIX_B26`, `KYTY_FIX_B1B`, `KYTY_FIX_DUALSRC` — 1 (не задана или `""`); `KYTY_FIX_MINIMIZE` — `EnvFlagOn`, 0;
  `KYTY_S_PCW` — 1 только при ровно `"1"`; `KYTY_S_PCW_FORCE_MS` — `nullptr` → 0; `KYTY_DUMP_GCN` (новое чтение) — только ровно `"2"`; `KYTY_TEST_MINIMIZE`
  — не задана или `""` → выключен, без строки лога. Прежний путь при 0 у F5 — §5.
- Порядок гейтов: `check_gate_order.py --src C:/kyty/f287/fsb/wt/src` — `GATE ORDER: clean`, вывод байт в байт = FSa (`42d78aa8…`).

**Вывод:** умолчание 1 — ровно `KYTY_FIX_B26`, `KYTY_FIX_B1B`, `KYTY_FIX_DUALSRC`; иных изменённых умолчаний нет. Член исполнителя FSa [I] (код с. 128–136
без ручек построчно не сверен) остаётся [I]: выборочно проверено [c-код] — безусловные вызовы `Common::RbCen::Reset` (Submit, `TryWriteBacking`,
`BumpMapEpoch`, запись образа) при `rbcen`/`b2reuse`/`bindlean` 0 — только `relaxed`-чтения атомиков (`95eec776:src/common/frameStats.h:3780`); тот же код
был в `2e6df8f0` (F3d, V Sky Garden 334,4 с, 0 глитчей, п. 282(а)).

## 3. Своя сборка из чистого worktree с LF — подпись совпадает, sha нет (RC1)

- Worktree `C:/kyty/f287/fsb/wt` — `mk_wt_fsb.sh` (копия `mk_wt_fsa.sh`, путь изменён) на `95eec776`: `git status --short` 0 строк, CR в `src/` 0 из 452.
  Сборка — `build_fsb.cmd` (копия `build_fsa.cmd`, пути `SRC`/`BUILD` изменены; флаги те же), configure и build rc 0 (14:42:05Z–14:44:13Z).
- **Подпись трансляции `KYTY_SHADER_SOURCE_HASH` = `56189185f9e9f9a0ea5174f3f85206e6d099db3d` — совпадает с FSa;** `kytyGitVersion.h` без комментариев
  равен FSa байт в байт (версия `KytyPS5-2026-09-15-6a2987a-1766-g95eec776`).
- **sha256 своей сборки — `2fc78597e4d953d879d746d8785ae79466da40ab8074e66794ba9bf5dffe6100`** (24 574 464 байта) против FSa `dac02fb9…` (24 573 952).
  Разбор (`bincmp_fsb.py` → `bincmp.out.txt` `86140861…`, `textcmp_fsb.py` → `textcmp.out.txt` `768bc517…`):
  - метка времени PE: `0x6abe71ad` против `0x6abe6ebf` (lld-link без `/Brepro`) — байт-в-байт равенство двух сборок недостижимо в принципе;
  - путь worktree в строках `__FILE__`: 139 вхождений `f287\fsb` против 139 `f287\fsa`;
  - хэши анонимных пространств имён MSVC-манглинга (`?A0x…`, производные от пути исходника; длина 7–8 цифр) — имена RTTI в `.data` разной длины ⇒
    `.data` длиннее на `0x140`, `.reloc` на 12 байт;
  - `.text` (18 086 070 байт), `.rdata`, `.pdata`, `.tls`, `.rsrc` — одной длины; строк ≥ 8 символов в `.rdata` 29 527 = 29 527, различие одно — запись
    `LLD PDB` (GUID/время); в `.data` 782 = 782, различий 0 после замены пути и маски хэша `?A0x…`;
  - все различия `.text` — 60 786 серий по 1–3 байта (121 846 байт), каждая внутри 32-битного смещения RIP-relative; дельта `+0x140` (= сдвиг `.data`)
    у 60 726, остальные 60 — кратные 16 (сдвиги отдельных объектов в `.data`; 5 серий, напечатанных скриптом как «дельта 1», — второй байт
    смещения, дельта `0x100`). Различий кода вне смещений нет.
- `libwinpthread-1.dll` своей сборки = FSa = папке эмулятора (`78ebbc14…`).

**RC1 (владелец — лид, до печати FSc `pred/01_fs.md`):** член п. 282(г)(2)(3) «своя сборка — sha … совпадают» по букве невыполним для любой
независимой сборки: метка времени PE и абсолютный путь worktree входят в бинарь при флагах `build_local.cmd`. Сценарий отказа без правки: FSb
по букве — FAIL при верном бинаре, а следующая «повторная сборка для проверки» (F-звенья, установка FSd, шаг 0 с. 146) повторит тот же провал или,
хуже, приведёт к пересборке бинаря отгрузки вместо копии `dac02fb9`. Что изменить: записать прочтение (3) — «подпись трансляции и
`kytyGitVersion.h` совпадают; бинари равны с точностью до метки времени PE, записи PDB и пути worktree (`.text` одной длины, различия — только
смещения RIP-relative, строки равны после замены пути и маски `?A0x…`)» — и правило: в прогонах и установке идёт только копия, сверенная по sha256.
Вариант исполнителя: по этому прочтению (3) — ✓.

## 4. `KYTY_FIX_DUALSRC=0` — путь F4c, `=1` (и умолчание) — перепись п. 262(б) ✓

- Код Б35 после `65a09c82` менял только FSa: `git log 65a09c82..95eec776` по `dualSrcBlend.h`, `shaders.cpp`, `graphicContext.h`, `pipelineCache.h`,
  `pipelineCache.cpp`, `vulkanWindow.cpp` — один коммит `95eec776`; `git diff 65a09c82 95eec776` по первым пяти — 0 строк.
- Дерево F4c (`c9a5e198`, worktree F4a2): `git patch-id --stable` — `1713a8be` = `ac309951` (`7cf3c5ba…`), `65a09c82` = `06f049f2` (`66605fbb…`).
- При `=0` (`"0"`/`false`/`off`/`no`) — `dual_src_enabled` = 0, как `EnvFlagOn` в `c9a5e198` (§1); `graphics.dual_src_blend_enabled` = 0
  (`95eec776:src/graphics/presentation/window/vulkanWindow.cpp:675`) ⇒ ветка переписи `95eec776:src/graphics/host_gpu/renderer/pipeline/shaders.cpp:572`
  «if (graphics.dual_src_blend_enabled && ps_active) {» не исполняется, `device_features.dualSrcBlend` не ставится — путь `c9a5e198` при `=0`.
- При незаданной переменной и поддержке устройства — `enabled=1` ⇒ та же функция `CreateDualSourceVariant` (`shaders.cpp:337`) для пути игры и
  precache, строка `DualSrcBlend: supported=1 enabled=1` — как `c9a5e198` при `=1` (`f4c_a`, п. 281(а)). Без поддержки — `enabled=0`.
- Не заявляется: что бинарь отгрузки при `=0` в целом тождествен `c9a5e198` (база другая: с. 128–136, F2, F3, S5, F5 — п. 281(з)).

## 5. F5a + F5a2 при `KYTY_FIX_MINIMIZE=0` — прежний путь ✓ (строка лида из `HPP-368`)

`git diff 478868b5 95eec776 -- src/graphics/presentation/window/swapchain.cpp` прочитан целиком [c-код]: `FixMinimizeEnabled()` = 0 ⇒ `Swapchain::Recreate`
— `if (0 && …)` → `Create()` как раньше; `RecoverSwapchain` — ранний выход не берётся, `frames.SetFormat` как раньше; `Present` — проверка `Missing()` не
исполняется, `screenshot && !(0 && recorded)` = `screenshot`, ветвь `Finish` перед `RecoverSwapchain` не исполняется, конечный `Finish` —
`screenshot && !(0 && finished)` = `screenshot`. Новые поля `Impl` вне пути при 0. `WindowTestMinimizeNoteGuestText` (`window.cpp:1055`, вызов из
`fwrite` гостя `libC.cpp`) при незаданной `KYTY_TEST_MINIMIZE` — одна `getenv` на первом тексте гостя, затем ранний выход по статическому флагу,
строк лога нет. Совпадает с F5b2 (`docs/track-f/f5b2-review.md`, PASS).

## 6. `shader_cfg_tests` своим прогоном ✓

Цель `shader_cfg_tests` в своей папке сборки (`build_fsb.cmd tests`, rc 0); прогон без переменных `KYTY_*` в окружении, кроме
`KYTY_TESTS_CONTINUE=1`/`KYTY_TESTS_VERBOSE=1`: **127 строк `[test]`, падение 1 — Б11** (`IMAGE_SAMPLE_C` / `IMAGE_SAMPLE_C_LZ`), rc 0;
лог `cfgtests_defaults.log` `b50929d4…` после снятия CR и `elapsed_ms=N` равен логу FSa (нормированный sha `7cf25859` у обоих).

## 7. Замечания (не RC)

- **N1 (FSc, Harness Engineer):** печать FSc называет бинарь по sha256 `dac02fb9…` и запрещает пересборку (п. 282(г)(3)) — моя сборка `2fc78597`
  в прогоны не идёт и не копируется в `bin/`.
- **N2 (лид, строка установки FSd):** F5a2 входит в бинарь отгрузки за `KYTY_FIX_MINIMIZE=0`; если F5d примет умолчание 1, это будет новый
  бинарь со своей регрессией — бинарь отгрузки трека F его не заменяет.
- **N3 (лид):** отчёт FSa §3 называет 17 имён; сканы лида и мои — 27 литералов, из них 17 чтений; разница — комментарии и макросы (§2), вывод не меняется.

## 8. Не заявляется

Что бинарь при умолчаниях держит Sky Garden или `mini_giants_garden`; что картинка пайплайна Б35 верна; что код с. 128–136 без ручек поведенчески равен
`4fc501f4` (выборочно — §2); что бинарь при `=0` тождествен `c9a5e198`; ни одно число — не выигрыш; 60 FPS не обещаются.

Файлы звена — `C:/kyty/f287/fsb/`, копии в `docs/track-f/fsb/`: `mk_wt_fsb.sh`, `mk_wt.log`, `build_fsb.cmd`, `bincmp_fsb.py`, `bincmp.out.txt`,
`textcmp_fsb.py`, `textcmp.out.txt`, `knobs_fsb.py`, `knobs_fsb.out.txt`, `gate_order.out.txt`, `cfgtests_defaults.log`. Только локально: worktree,
папка сборки, `configure.log`, `build_wt.log`, `build_tests.log`.
