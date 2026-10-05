# FS8b (`HPP-572`, Red Team): ревью бинаря отгрузки FS8 `2c9b69b9` — **PASS**

**Вердикт: PASS.** Требуемых изменений кода (RC) нет, звено FS8a2 не нужно. Замечаний без RC — 4 (Н1–Н4, §7); у каждого есть сценарий отказа и владелец.
Бинарь FS8 `2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b` идёт в FS8c без изменений.

Решение лида — `a6a250ce:docs/ROADMAP.md:22615` п. 471 (якорь «471. **Звено F14h трека F (`HPP-508`, лид): F14e, F14f, F14g ПРИНЯТЫ»; +1 — «(а) **Приёмка
строкой по членам п. 409(г).**»), подпункт (г)(2) — FS8b; поправки — `9959e3b8:docs/ROADMAP.md:22994` п. 523(г) (якорь «(г) **Поправка членов п. 471(г)(1):**»;
+1 — «(д) **FS8b (`HPP-572`) сверх п. 471(г)(2):**») и (д); приёмка FS8a — `449eb706:docs/ROADMAP.md:23025` п. 527 (якорь «527. **Звено FS8a трека F (`HPP-571`,
Emu Engineer) — ПРИНЯТО»; +1 — «(а) **Перепроверка лида [c]:**»), подпункт (д). «Содержит» — п. 380(б); правило базы — п. 410(г)(6)(i); форма — FS7b
(`docs/track-f/fs7b-review.md`). Вход: отчёт FS8a `420b3433:docs/track-f/fs8a.md`, код `main` `e46f55d4`, `7719d0f2`, worktree FS8a `302347b4`.
Начало работы — 05:36:56Z (после коммита `449eb706` п. 527 и комментария лида `0ea36b1c` 05:36:47Z); пункты 471, 523, 527 прочитаны целиком, 380, 410(г),
467(г) — к 05:38:06Z, до первой команды. Игра не запускалась; установленный `kyty_emulator.exe` — `9325446cdd3c960b…` (FS6) до и после звена, `C:/kyty/build/install`
и кэши не тронуты. Время — UTC по `date -u`, события — строки `FS8b` в `C:/kyty/f287/times.txt`. Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно.

## Итог по членам п. 471(г)(2), п. 523(д), п. 527(д)

| Член | Итог | Чем |
|---|---|---|
| путь `KYTY_FIX_F19=0` по коду = база (ветка `else` дословно; токен `:fixf19` только при включённой правке) | ✓ [c] | §1.1: `else` = строки базы `d6ee2dc8` слово в слово (отступ +1 таб); второе место (`FixF19MergeIndirectTables`) — только под `if (FixF19Enabled())`; токен — `FixF19Enabled() ? ":fixf19" : ""`, последний; по выходу: SPIR-V набора FS8 при `=0` = сборке без коммита умолчания (`7a83c4e3`, код F14e2) без переменной и при `=0` — 180 из 180 байт в байт (§4.3). Отличие пути `=0` от базы — подпись трансляции (`9177b426…` ≠ `26ce5fc7…`), как п. 471(г)(4) |
| путь по умолчанию = F14e2 при `=1` | ✓ [c] | три файла `src/` FS8 = `main` `e46f55d4` (`git diff --stat` пуст); `e46f55d4` меняет только выражение чтения и комментарии; SPIR-V FS8 без переменной = `7a83c4e3` при `=1` 180/180; гейт без переменной `effective=1`; таблица значений 10 из 10 (§4.4) |
| дифф — только (г)(1)(е) с поправкой (е′) п. 523(г) | ✓ [c] | §2: (е′)(1) 6 путей, `docs/` 0; `src/` + `CMakeLists.txt` = база + части `src`/`CMakeLists.txt` трёх коммитов `082d1612`, `f98e842c`, `e46f55d4`, наложенные мной на `d6ee2dc8` во временном индексе (дифф равен байт в байт); (е′)(2) sha256 обоих диффов `02169c8f…` |
| п. 527(д)(1): (е′)(3)″ своей проверкой | ✓ [c] | `git diff --name-only 5e78640e 302347b4` — 13 путей, вне `docs/track-s/s14j*` — только `tests/shaderCfgTests.cpp`; `git patch-id --stable` этого диффа = patch-id `7719d0f2` = `8824e122…` |
| п. 523(д): добавки `tests/shaderCfgTests.cpp` — только `fcaf141b`, `082d1612`, `ff953d4f`, `f98e842c` (+ `7719d0f2`) | ✓ [c] | своя цепочка `git apply --cached --3way` во временном индексе от `d6ee2dc8`: 6 шагов без конфликтов, дерево = `302347b4^{tree}` `0b2efcb6…`, до шага 6 = `0f78a522^{tree}` `15f28954…`; добавленных строк 980, не из пяти коммитов 0; удалённых 3, все удалены одним из пяти |
| п. 527(д)(2): ревью `7719d0f2` | ✓ [c] | §3: три чтения → `ShaderRecompiler::IR::FixF19Enabled()` — та же функция, что у транслятора (magic static, одно чтение на процесс, форма FS4a); ожидания `=0`/`=1` не тронуты (дифф — 4 строки: 3 чтения и 1 комментарий); прочие места `KYTY_FIX_F19` в `tests/` названы (§3); смены переменной во время процесса в `tests/` нет |
| Ф10, Ф16, Б42, Б33, Б4, Ф8, Б24, P-var не тронуты | ✓ [c] | файлов вне четырёх (`CMakeLists.txt`, `shaderTranslationCache.cpp`, `ResourceMaterialization.cpp`/`.h`) в `src/` нет; `git cherry` `-` у `1833ee28`, `c3eb8fe8` (Ф10), `68602c4f`, `17adaf80` (Ф16), `4e72289e` (Б42), `c1732d1a` (Б33), `a86a5ad0`, `17eb924e` (Б4), `10a4800b`, `ec6c4c83` (Ф8, FS7a), `9c726d74`, `919c1a19` (Б24); `4414e235`, `d515b901`, `3d0e46da`, `0e72bc19`, `4d9e8ab7`, `3904522d`, `d6ee2dc8` — предки `302347b4` |
| своя сборка из чистого worktree и sha (п. 527(д)(3)) | sha **не равен**, причина названа ✓ [c] | §5: свой `48135b8f…` ≠ `2c9b69b9…`; `.text` 0 различающихся байт; 1 624 байт объяснены, из них 9 — строка `SDL_REVISION` (класс 2c, назван до чтения контроля); отрицательный контроль `7a83c4e3` в каталоге той же длины — `UNEXPLAINED`, `.text` 8 447 529 байт; нулевой — `2c9b69b9` против себя `EXPLAINED`, 0 байт |
| свой прогон (г)(1)(а)–(в) | ✓ [c] | §4: (а) 4 из 4 файлов `SHADER_CACHE_EXTRA_FILES`; (б) `gu`/`g1`/`g0`/`c1` `ALL OK`, `c0` — прежний отказ (`missing required text: OpImageSampleDrefExplicitLod`, rc `3221226505`); (в) `fu`/`f0`/`f1` по 130 тестов, 0 строк `failed:`, SPIR-V `fu` = `f1` 180/180, сводный sha256 `7fa1857d…` = FS8a |
| таблица умолчаний | ✓ [c] | свой сканер `knobs_fs8b.py` (копия моего `knobs_fs7b.py`): ON-IF-UNSET — ровно 13 имён = п. 467(г)(1) + п. 487(г)(1) + `KYTY_FIX_F19`, `missing [] extra []`; отрицательный контроль на `d6ee2dc8` — `missing ['KYTY_FIX_F19']`; UNDECIDED — те же пять, что в FS7b (`KYTY_AUDIO_SYNC`, `KYTY_DUMP_GCN`, `KYTY_POKE`, `KYTY_PVAR`, `KYTY_S_PCW_FORCE_MS`; правка их не трогает) |
| «содержит» в чтении п. 380(б) (ж″ п. 527(г)) | ✓ [c] | `git cherry 302347b4 X X^`: `-` у `082d1612`, `f98e842c`, `e46f55d4`, `10a4800b`, `ec6c4c83`, `9c726d74`, `919c1a19`, `fcaf141b`, `7719d0f2` (9 из 9); `+` (не входят) у `ff953d4f`, `741e3312`, `c9b4268e`, `381aa80a`, `365cc3c2` |

## 1. Код

### 1.1. Путь `=0` (`302347b4:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp`)

- **Чтение** — `e46f55d4:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:38` (якорь «`const char* value = std::getenv("KYTY_FIX_F19");`»; +1 —
  «`return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);`»). `static const bool enabled` — magic static C++11: одно чтение на процесс,
  потокобезопасная инициализация; `getenv("KYTY_FIX_F19")` в `src/` — 1 место. Для любого непустого значения результат тот же, что у прежнего
  `Common::EnvFlagOn` (форма FS4a `17adaf80`); меняется только «не задана» и `""` → 1.
- **Ветка `else`** (`:609–612`) — строки базы `d6ee2dc8` (`image.manual_depth_compare = !NullImageDescriptor(descriptor) && format != Prospero::BufferFormat::k32Float;`)
  без изменений, отступ +1 таб [c `fs8_vs_base_src.diff`]. Второе место правки (`FixF19MergeIndirectTables`, `:729–734`) — только при `FixF19Enabled()`; при `=0`
  `BuildResourceSpecialization` идёт базой. Новые `#include` (`envFlag.h`, `imageInfo.h`) и функции (`FixF19ManualDepthCompare`, `FixF19MergeIndirectTables`) при
  `=0` не вызываются.
- **Токен** — `302347b4:src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp:588` (якорь «`(ShaderRecompiler::IR::FixF19Enabled() ? ":fixf19" : "");`»;
  +1 — «`if (!variant.empty()) {`»): только при включённой правке, последним; каталог при `=0` — `variant_fixb26_fixb1b_fixf10` (имя = FS7), подпись — новая
  (`KYTY_SHADER_SOURCE_HASH` `9177b4267de1fb8bac7d1113afd8733210addfac`, моя сборка; = FS8a).

### 1.2. Путь по умолчанию

`git diff --stat e46f55d4 302347b4 -- <3 файла src/> CMakeLists.txt` пуст; `git log 082d1612..e46f55d4` по трём файлам `src/` — только `e46f55d4`. Значит,
код FS8 по этим файлам = `main` после ревьюированных F14e `082d1612` (F14f) и F14e2 `f98e842c` (F14f2; `f98e842c` меняет только `CMakeLists.txt` и тесты) плюс
`e46f55d4` (выражение чтения и комментарии). Без переменной — путь `=1` [c §4.3, §4.4].

## 2. Дифф и история (`review_git_fs8b.py`, вывод `review_git.out.txt`, `ALL OK`)

Своя цепочка — во временном индексе (`GIT_INDEX_FILE`), worktree FS8a не трогался: `read-tree d6ee2dc8`, затем `git apply --cached --3way` патчей `fcaf141b`,
`082d1612`, `ff953d4f -- tests/shaderCfgTests.cpp`, `f98e842c`, `e46f55d4`, `7719d0f2` — все `cleanly`; дерево — `0b2efcb6d9fa4f6e948e0bafe7e530f7a443f564`
= `302347b4^{tree}`; дерево до `7719d0f2` — `15f28954…` = `0f78a522^{tree}`. Отдельно: только части `src`/`CMakeLists.txt` коммитов `082d1612`, `f98e842c`,
`e46f55d4` на `d6ee2dc8` дают дифф, равный `git diff d6ee2dc8 302347b4 -- src CMakeLists.txt` байт в байт. `tests/ShaderRecompilerComputeTests.cpp` — 279 добавленных
строк, все из `082d1612`/`f98e842c`.

## 3. Ревью `7719d0f2` (п. 527(д)(2))

- Дифф — `tests/shaderCfgTests.cpp`, 4 строки: `Common::EnvFlagOn("KYTY_FIX_F19")` → `ShaderRecompiler::IR::FixF19Enabled()` в
  `TestNewShaderRecompilerPixelImageSampleLodSelection` (`:5536`), `TestF19IndirectComparisonTable` (`:5710`), `TestF19NullComparisonImage` (`:5804`) и один
  комментарий. Ожидания (вызовы `Check(…)` на `dref`/`manual` при `fix_f19` и при `!fix_f19`) не тронуты [c диффа].
- «Те же, что у транслятора» [c]: тест вызывает ту же функцию, что транслятор, — одно значение на процесс; `tests/` не меняет `KYTY_FIX_F19` во время процесса
  (`_putenv_s`/`setenv` в `tests/` — только `KYTY_FIX_B9A`, `KYTY_GATE_FILE`).
- **Прочие места `KYTY_FIX_F19` в `tests/`** (`git grep` по `302347b4`): `ShaderRecompilerComputeTests.cpp:9922` и `:32228` — `FixF19Enabled()` (гейт F14e), `:32229` —
  сырой `getenv` только для печати `[f19] KYTY_FIX_F19=…`; `shaderCfgTests.cpp:15378` — режим корпуса T1 `KYTY_RECOMPILE_F19_FORMAT` действует при
  `FixF19Enabled()` (Н3). Иных чтений нет.
- Справка: на сборке `7a83c4e3` (без `0f78a522`, тесты без `7719d0f2`, умолчание 0) набор без переменной — 0 строк `failed:`, т. е. до смены умолчания старые чтения
  были согласованы с транслятором; рассогласование создал `e46f55d4`, `7719d0f2` его снимает [c §4.3].

## 4. Свой прогон (г)(1)(а)–(в)

Свои тесты своей сборки (`C:/kyty/f287/fs8b/build`), окружение ребёнка без единой `KYTY_*`, затем ручка. Шаги длиннее 60 с — под сторожем `watch_fs8b.py`
(п. 431(в)(1)) со строкой API перед шагом.

### 4.1. (а) Н1 п. 469(в) (`n1_fs8b.out.txt`)

`SHADER_CACHE_EXTRA_FILES` worktree (`CMakeLists.txt:156`, `${KYTY_SOURCE_DIR}` = `wt/src` по `:15`) — 4 файла, все есть: `shaderTranslationCache.cpp`, `gpu_format.h`,
`gpu_defs.h`, `imageInfo.h`. `N1 files 4 ALL OK`.

### 4.2. (б) GPU-гейт `shader_recompiler_compute_tests` (`gpu_fs8b.sh` — копия `gpu_fs8a.sh` с путями `fs8b`; `gpu_fs8b.out.txt`)

| Прогон | `KYTY_FIX_F19` | Аргумент | Итог |
|---|---|---|---|
| `gu` | нет | `--fix-f19-only` | `[f19] KYTY_FIX_F19=(unset) effective=1`, `ALL OK` |
| `g1` | `1` | `--fix-f19-only` | `effective=1`, `ALL OK` |
| `g0` | `0` | `--fix-f19-only` | `effective=0`, `ALL OK` (ожидания `=0`) |
| `c1` | `1` | `--fix-f19-comparison-depth` | `ALL OK` |
| `c0` | `0` | `--fix-f19-comparison-depth` | прежний отказ: `ComparisonDepthTexture failed at SPIR-V disassembly: missing required text: OpImageSampleDrefExplicitLod`, rc `3221226505` (сторож; в сводке Git Bash — 127) = FS8a |

### 4.3. (в) `shader_cfg_tests` (`suite_fs8b.py` — копия `suite_fs8a.py`, логика прочитана и не менялась; `suite_fs8b.out.txt`)

- `fu`, `f0`, `f1` — по 130 тестов, 0 строк `ShaderCfgTests: failed:`, rc 0; SPIR-V `fu` = `f1` 180 из 180; сводный sha256 набора `fu` `7fa1857d036e0610…` = FS8a;
  справка `f0` ≠ `fu` в 6 файлах (`109`, `110`, `112`, `113`, `177`, `179`) = FS8a. `ALL OK`.
- **Сверх члена — путь `=0` по выходу** (`cmp_neg_vs_fs8.out.txt`, `ALL OK`): набор сборки `7a83c4e3` (FS8 без коммита умолчания = код F14e2, `suite_neg.out.txt`):
  FS8 `f0` = `7a83c4e3` без переменной и = `7a83c4e3` `=0` — 180/180 байт в байт; FS8 `fu` и `f1` = `7a83c4e3` `=1` — 180/180. Член (в) на `7a83c4e3` без
  переменной печатает `FAILED` ((v2): `fu` ≠ `f1` в тех же 6 файлах) — член различает смену умолчания (отрицательный контроль члена).

### 4.4. Таблица значений ручки (`lval_fs8b.out.txt`)

Гейт `--fix-f19-only` моей сборки, строка `[f19] … effective=`: не задана → 1, `""` → 1, `0`/`false`/`OFF`/`no` → 0, `1`/`2`/`true`/`" 0"` → 1 — 10 из 10, гейт
`ALL OK` в каждом, `LVALUES ALL OK`.

## 5. Своя сборка

Worktree `C:/kyty/f287/fs8b/wt` — `git worktree add --detach` на `302347b4` (`mk_wt_fs8b.sh` — копия моего `mk_wt_fs7b.sh`); `git status --short` — 0, CR в `src/` —
0 из 456 (`mk_wt.log`). Независимость источника — дерево `302347b4` собрано мной из `d6ee2dc8` и шести патчей (§2); независимость сборки — свой каталог (длина пути =
`fs8a`), своя конфигурация при HEAD `302347b4`; флаги — `build_fs8b.cmd` = `build_fs7b.cmd` с путями `fs8b`. Configure 05:40:34–05:42:01Z, эмулятор до 05:43:33Z,
тесты до 05:58:33Z — под сторожем.

| файл | sha256 | `KYTY_SHADER_SOURCE_HASH` | строки версии в exe |
|---|---|---|---|
| FS8a `2c9b69b9` | `2c9b69b906f882ce…` | `9177b426…` | `KytyPS5-…-1889-g302347b4` (`main.cpp`), `SDL-KytyPS5-…-1888-g0f78a522` (`SDL_REVISION`) |
| своя | `48135b8f0156bb79…` | `9177b426…` (`kytyGitVersion.h` = FS8a байт в байт) | `…-1889-g302347b4` дважды |
| отрицательный контроль `7a83c4e3` | `46dc9158d9dc2a67…` | `a54ae4bd…` (= F14e2, п. 456(г)) | `…-1887-g7a83c4e3` |

`pediff3r_fs8b.py` = `pediff3.py` F15d (без изменений) + класс 2b моего `pediff3s_fs8b.py` (без изменений) + новый класс **2c `SDL_REVISION`**, названный в файле
до чтения контроля: байт внутри строки `SDL-KytyPS5-<дата>-<sha7>-<n>-g<hex>` с одним началом в A и B, равной после маски `-<n>-g<hex>`; только вне `.text`.
Основание класса [c]: `3rdparty/SDL2/CMakeLists.txt:3127–3145` берёт `git describe` дерева при **configure**; FS8a конфигурировал при HEAD `0f78a522` (05:22–05:24Z),
затем добавил `7719d0f2` и перегенерировал только `kytyGitVersion.h`, без configure. `SDL_REVISION` в `src/` не читается (`git grep` — 0 мест).

| пара | итог |
|---|---|
| своя против `2c9b69b9` (`pediff3r_emu.out.txt`) | 1 624 байт: метка/GUID 12, каталог сборки 139, `?A0x` 1 268, класс 2b 196 (`.data`), класс 2c 9 (`.rdata`, одна строка `SDL_REVISION`); `.text` 0; `EXPLAINED` |
| `2c9b69b9` против себя (`pediff3r_self.out.txt`) | 0 байт, `EXPLAINED` (нулевой контроль) |
| `7a83c4e3` против своей (`pediff3r_neg.out.txt`) и против `2c9b69b9` (`pediff3r_neg_a.out.txt`) | `UNEXPLAINED`, `.text` 8 447 529 байт (сдвиг кода); класс 2c у пары с `2c9b69b9` — 9 байт (та же строка), прочее не поглощено |

Классификатор различает смену умолчания и смену каталога/ревизии configure. Без класса 2c (`pediff3s_fs8b.py`, `pediff3s_emu.out.txt`) — `UNEXPLAINED` ровно на 9 байт
этой строки.

## 6. Строки в exe (`strings_fs8b.out.txt`)

Своя и `2c9b69b9` одинаково: `KYTY_FIX_F19` 1, `:fixf19` 1, `KYTY_FIX_F8` 1, `KYTY_FIX_B24` 1, `KYTY_FIX_B4` 2, `KYTY_S_PCW` 4, `KYTY_FIX_F10` 1, `KYTY_FIX_SVAL` 1,
`KYTY_FIX_B42` 1, `KYTY_PVAR` 2, `KYTY_GAME_PATCH` 1; `KYTY_FIX_F26`, `KYTY_FIX_F5CMU` — 0.

## 7. Замечания без RC

- **Н1 (`SDL_REVISION` FS8a; владелец — Harness Engineer, печать `fs8c.md`; лид — строка опознания FS8d).** В `2c9b69b9` строка `SDL_REVISION`
  `SDL-KytyPS5-2026-09-15-6a2987a-1888-g0f78a522` (ревизия configure), строка версии эмулятора — `…-1889-g302347b4` [c §5]. Сценарий отказа: печать или ридер,
  опознающий бинарь тега поиском `g302347b4` по всему exe или по строкам SDL, видит `g0f78a522` и пишет «не тот бинарь». Правка не нужна: опознание — sha256
  `2c9b69b9…` и строка версии эмулятора из лога; `0f78a522` и `302347b4` различаются только тестом, исходник эмулятора у них один (§2).
- **Н2 (откат `KYTY_FIX_F19=0`; владелец — лид, FS8d).** При `=0` FS8 пишет каталог `variant_fixb26_fixb1b_fixf10` — тот же, что тёплый каталог FS7/FS6 у пользователя, —
  записями новой подписи: имена файлов подписи не несут (`PathOf`, `shaderTranslationCache.cpp:608–628`), запись чужой подписи — промах `Load` (`:653`), `Save`
  удаляет старый файл и кладёт новый (`:811–814`), `pipelines.bin` лежит в том же каталоге (`pipelineCache.cpp:6450`) [c кода]. Сценарий отказа: пользователь
  пробует `KYTY_FIX_F19=0` на FS8, затем откатывается копией FS7 — тёплый каталог FS7 уже переписан, первый вход каждого посещённого уровня снова холоден (фризы
  трансляции). Текст п. 471(г)(4) («каталог `_fixf10` на новой подписи тоже холоден») этого не говорит; форма предупреждения — п. 410(г)(4) («только на холодном
  каталоге варианта»).
- **Н3 (корпус T1 при умолчании FS8; владелец — Emu Engineer / Harness Engineer при повторе корпуса).** `KYTY_RECOMPILE_F19_FORMAT` действует при `FixF19Enabled()`
  (`shaderCfgTests.cpp:15378`); до FS8a без переменной ручки он молчал, после — действует. Сценарий отказа: повтор корпуса «режим `=0`» без явного `KYTY_FIX_F19=0`
  даёт выход `=1` и читается как регрессия или как «`=0` = `=1`». Повтор — с явным значением ручки.
- **Н4 (текст FS8a).** `fs8a.md` §(в) называет третий тест `TestF19NullComparisonDescriptor`; в коде и логах — `TestF19NullComparisonImage` [c]. Сценарий отказа:
  поиск по имени из отчёта ничего не находит. Числа отчёта не затронуты.

## Чек-лист кода (агент Red Team)

- Хронометрируемых строк правка не добавляет. Гонки: `enabled` — magic static, далее только чтения; инвариантов `*_bad` правка не вводит. Ранние возвраты:
  лямбда чтения — один выход.
- Ручка читается один раз до первого места использования (конструктор кэша трансляции и `BuildResourceSpecialization` зовут одну функцию) и порваться внутри
  операции не может: токен каталога и путь специализации видят одно значение.
- Правка в `src/graphics/shader/**` — подпись трансляции меняется (`9177b426…`), каталог по умолчанию новый (`_fixf19`) — сказано в п. 471(г)(4) и FS8a.
- Кадр стека: лямбда без локальных буферов. Патч FS8a — LF (CR в `src/` 0 из 456 в моём worktree).
- Инструмент ревью ничего не меняет в прогоне игры: игра не запускалась; тесты — отдельные процессы своей сборки.

## Ход

- 05:38:06Z старт; 05:38–05:39Z `review_git_fs8b.py` `ALL OK`; 05:40:20Z worktree; 05:40:34–05:43:33Z configure и эмулятор; 05:44–05:45Z `pediff3s`/`pediff3r`.
- 05:45:55Z сторож отказал в запуске worktree контроля (`procload.py`, тег чужой серии); 05:46Z — чужой замок, процессы и записи остановлены; снят к 05:52:18Z.
- 05:53–05:56Z worktree и сборка контроля `7a83c4e3`; 05:57–05:58Z тесты; 05:58–06:01Z гейт, набор, контроль набора, таблица значений.

## Файлы

`C:/kyty/f287/fs8b/`, копии в `docs/track-f/fs8b/` (текст — LF): `review_git_fs8b.py`, `review_git.out.txt`, `fs8_vs_base_src.diff`, `mk_wt_fs8b.sh`, `mk_wt.log`,
`mk_wt_fs8n.sh`, `mk_wt_n.log`, `build_fs8b.cmd`, `build_fs8n.cmd`, `mk_cmdn.py`, `bstep.sh`, `bstepn.sh`, `api_chk.sh`, `watch_fs8b.py`, `pediff3.py` (копия F15d),
`pediff3s_fs8b.py`, `pediff3r_fs8b.py`, `pediff3s_emu.out.txt`, `pediff3s_self.out.txt`, `pediff3r_*.out.txt`, `sha_fs8b.txt`, `knobs_fs8b.py`, `knobs_fs8b.out.txt`,
`knobs_d6ee2dc8.out.txt`, `gpu_fs8b.sh`, `gpu_fs8b.out.txt`, `suite_fs8b.py`, `suite_fs8b.out.txt`, `suite_neg.out.txt`, `cmp_neg_vs_fs8.out.txt`, `lval_fs8b.out.txt`,
`n1_fs8b.out.txt`, `strings_fs8b.out.txt`, `gpu/<прогон>/run.log`. Бинари своей сборки и контроля — только локально (`C:/kyty/f287/fs8b/fix/`).

## Не заявляется

Что FS8 работает в игре (до FS8c) и что он установлен (до FS8d); что расхождение видно в кадре игры и его величина; что PCF драйвера равен ответу PS5; порядок
«сравнить, затем фильтровать» как текст ISA; ответ PS5 на `_C` по цветовому формату; формат гостя за `D32_SFLOAT` ручных мест; что ответ `D32_SFLOAT` на нативном
пути верен; что вариант (A) покрывает все места игры; что набор `shader_cfg_tests` полон; что SPIR-V корректен для устройства и картинка верна; что машинный код
пути `=0` равен базе байт в байт; что сборка детерминирована при другом каталоге; ни одно число — не выигрыш; 60 FPS не обещаются.
