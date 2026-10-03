# F10d (`HPP-452`, Red Team) — код-ревью `KYTY_FIX_SVAL` (Ф16) и сборка из чистого worktree

**Вердикт: PASS_WITH_FIXES — код `68602c4f` проходит все проверки п. 369(в)(2) [c]; правок кода нет; 3 RC текстовые
(отчёт F10c и печать F10e), RC с данными нет.**

Основание: `18d9c792:docs/ROADMAP.md:20029` п. 369 (якорь «369. **Звено F10b трека F (`HPP-446`, лид): F10a (`HPP-445`) принят»;
+1 — «`KYTY_FIX_SVAL` (умолчание 0) с критерием «ИСПРАВЛЕНО Ф16» ниже; звенья F10c»), член (в)(2), звенья (г). Вход — код F10c
`68602c4f`, отчёт `1a588fc2:docs/track-f/f10c.md`, файлы `1a588fc2:docs/track-f/f10c/`. Начало работы звена — 2026-10-03T05:27:35Z
(первая строка `times.txt` F10d), сборка 06:57:42Z–06:59:41Z, отчёт — 2026-10-03T07:04:35Z (строка `times.txt` при записи). Игра, устройство
Vulkan, RenderDoc — нет; установленный `kyty_emulator.exe` не тронут.

## 1. Чек-лист п. 369(в)(2) и задания

| Член | Проверка | Итог |
|---|---|---|
| `=0` — путь прежний | `68602c4f:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:1381` (якорь «} else {»; +1 — «valid = tools.Validate(spirv);»): ветка ВЫКЛ — тот же вызов `tools.Validate(spirv)` без опций, без счётчиков и строк; дальше `if (valid) return true;` и прежний разбор отказа | ✓ [c] |
| Значение — из места включения | `vulkanWindow.cpp:705–707`: `graphics.uniform_buffer_standard_layout_enabled = features12.uniformBufferStandardLayout == VK_TRUE` — сразу после записи `features12` из `supported_features12`; `features12` в цепочке `pNext` создания устройства всегда (через `fragment_barycentric`/`robustness2`, `:681–686`, `:734–738`, создание — `:768`); не через `ConstBankEnabled()` | ✓ [c] |
| Запись до первой трансляции | `VulkanCreateDevice` (`:1245`) → `make_unique<RenderContext>` (`:1265`) → `RenderContext` → `m_pipeline_cache(graphics)` (`renderContext.cpp:93`) → тело `PipelineCache::PipelineCache` `:4664` `store(..., release)` ДО `InitializeDriverCache`, `StartWorkers`, `StartPrecache` (`:4667–4670`); `ProgramCache` (`:4463`) ничего не транслирует; поток претрансляции CS стартует лениво на первой задаче (`computePretranslation.h:80`) и зовёт только `TranslateProgram` — `ValidateShaderSpirv` там нет; единственный вызов `ValidateShaderSpirv` — `CompilePermutation` `:2158` (поиск по `src/` всего дерева: 1 вызов + определение) | ✓ [c] |
| Опция только при включённой фиче | `:1367–1369`: `SetUniformBufferStandardLayout(true)` только при `g_fix_sval_ubo_std_layout.load(acquire)`; офлайн `r_1u0` (устройство без фичи) — S151 REJECT 151, вердикт = F10a на 778 из 778 | ✓ [c] |
| Строки `FixSval:` / `FixSvalStat:` | `FixSval: mode=%d ubo_std_layout=%d` — один раз в конструкторе (`:4665`); `FixSvalStat: validated=%llu rejected=%llu` — при `=1` на каждой 256-й проверке (`:1376–1380`); при `=0` строки статистики нет (офлайн `r_0-nostat`, `r_unset-nostat`: 0) | ✓ [c] |
| Подпись трансляции | своя сборка из чистого worktree: `build/kytyGitVersion.h:9` `KYTY_SHADER_SOURCE_HASH "56189185f9e9f9a0ea5174f3f85206e6d099db3d"`, в exe 1 вхождение; правка — 3 файла вне множества подписи (`graphicContext.h`, `pipelineCache.cpp`, `vulkanWindow.cpp`) | ✓ [c] |
| Перехватчик фатала на пути PS | правка перехватчика не добавляет; единственный `ScopedFatalInterceptor` — `computePretranslation.h:212` (поток претрансляции CS, область `TranslateProgram`); отказ `ValidateShaderSpirv` на пути PS — `EXIT` `:2160` без перехватчика, как до правки | ✓ [c] |
| Коммиты Б42 (п. 367(г)(5)) | `git merge-base --is-ancestor` → `68602c4f`: `55490711`, `2da00d80`, `0b9dc0c9` (код Б42), `4e72289e` (умолчание `KYTY_FIX_B42=1`, строка `FixB42Ext`), `17b4aed6`, `4414e235`, `9c9d86ae` — предки; в exe `KYTY_FIX_B42` 1, `FixB42Ext` 1 | ✓ [c] |
| Свой повтор офлайн-набора F10c | тело — своё извлечение из блоба `68602c4f` (строки 1343–1399, sha256 `cd684f6e…` = `sval_body_f10c.inc` F10c и его git-копии `1a588fc2`); инструмент — `sval_f10c.cpp` `1a588fc2`, библиотека SPIRV-Tools дерева сборки (`7f2d9ee9` = gitlink); `run_f10c.py` `1a588fc2` с путями из argv; итог: 25 гейтов PASS, 0 FAIL, последняя строка `ALL OK`; `f10c_summary.txt` и `f10c_out.tsv` побайтно = F10c | ✓ [c] |
| Свой мутант «без опции → `=1` даёт REJECT» | M1 (удалена строка `options.SetUniformBufferStandardLayout(true);`): `r_1-S151` и `r_1-C51` — FAIL (REJECT), итог FAIL → убит; ещё 5 мутантов — все убиты (§3) | ✓ [c] |

## 2. Сборка из чистого worktree — [c]

- Worktree `C:/kyty/f287/f10d/wt` — `git worktree add --detach` прямо на `68602c4f` (без патча и cherry-pick), `core.autocrlf=false`;
  подмодули — по gitlink коммита (`mk_wt_f10d.sh`, `mk_wt.log`): `git status --short` 0 строк, CR в `src/` 0 из 456 файлов.
- Сборка `build_f10d.cmd` (копия `build_f10c.cmd`, свои пути, те же флаги; configure → build → install): rc 0.
- Свой бинарь: sha256 `1e426838fed4ee0b12d03078fcbf11edab580b39a202aff50a4435952e0b398c` (в прогоны не идёт; F10e — копия F10c,
  п. 369(в)(3)). Строки в exe по одному вхождению: `56189185f9e9…`, `FixSval: mode=`, `FixSvalStat: validated=`, `KYTY_FIX_SVAL`,
  `KYTY_FIX_B42`, `FixB42Ext`.
- **Сличение с бинарём F10c `36e2b042`** (`bindiff_f10d.py`, `bindiff_f10d.txt`): размер равен (24 666 624); после нормализации пути сборки
  (`f10d` → `f10c`, та же длина), `TimeDateStamp` и `CheckSum` PE остаётся 239 участков: 236 — хэши анонимных пространств имён `?A0x…`
  (выводятся из пути исходника), 2 — каталог отладки (GUID `RSDS`, отметка времени), **1 — строка версии git** (ниже, RC1). Код и данные,
  кроме этих мест, совпадают побайтно: бинарь F10c собран из кода `68602c4f`.
- **Находка [c]:** в бинаре F10c `36e2b042` строка `KYTY_GIT_VERSION` — `KytyPS5-2026-09-15-6a2987a-1959-g465f0d8e` (старый HEAD worktree
  F10c), а `KYTY_GIT_REVISION` — `68602c4f…`; заголовок `C:/kyty/f287/f10c/build/kytyGitVersion.h` (07:00:08 местного) уже
  `…-1961-g68602c4f` — объект с `KYTY_GIT_VERSION` (`src/main.cpp:35`, строка `git = …` в начале лога) не пересобран. В своём бинаре —
  `…-1961-g68602c4f` (2 вхождения), `465f0d8e` — 0. Отчёт F10c (`1a588fc2:docs/track-f/f10c.md:95`, якорь «- Версия: `KYTY_GIT_REVISION` `68602c4f301e8d424af0581d11039437ec4a958f`, `KYTY_GIT_VERSION` `…-g68602c4f`.»; +1 — «- Бинарь `C:/kyty/f287/f10c/kyty_emulator_36e2b042.exe`»)
  прочитал заголовок, а не exe.

## 3. Мутанты — [c]

Каждый мутант — одна правка целой строки тела (якорь встречается 1 раз), своя сборка инструмента, полный офлайн-набор; вызовы SDK `spirv-val`
кэшированы на диске (`run_f10d_cached.py`: ключ — аргументы + sha256 модуля; инструмент не кэшируется). Убит = последняя строка FAIL и каждый
ожидаемый гейт напечатан FAIL (`mut_f10d.txt`, итог `ALL OK`):

| Мутант | Правка | FAIL-гейты | Итог |
|---|---|---|---|
| M1_no_option | удалена `options.SetUniformBufferStandardLayout(true);` | `r_1-S151`, `r_1-C51` | убит |
| M2_ubo_ignored | `if (g_fix_sval_ubo_std_layout.load(...))` → `if (true)` | `r_1u0-asF10a`, `r_1u0-S151` | убит |
| M3_mode_ignored | `if (FixSvalEnabled())` → `if (false)` | `r_1-S151`, `r_1-C51`, `r_1-stat`, `r_1u0-stat` | убит |
| M4_stat_period | `% 256u` → `% 255u` | `r_1-stat`, `r_1u0-stat` | убит |
| M5_env_presence | `EnvValueOn(getenv)` → `getenv != nullptr` | `r_0-S151`, `r_0-nostat`, `r_0-asF10a`, `envflag` | убит |
| M6_no_reject_count | удалён `rejected.fetch_add` | `r_1u0-stat` | убит |

## 4. Требуемые изменения (RC)

**RC1 (текст отчёта F10c; исполнитель — Emu Engineer, поправкой к `docs/track-f/f10c.md`, или лид строкой приёмки F10f).**
Что не так: §2 отчёта F10c говорит `KYTY_GIT_VERSION …-g68602c4f`, а в бинаре `36e2b042` — `…-1959-g465f0d8e` (§2 этого отзыва).
Сценарий отказа: аудитор или F10e сверяет строку `git = …` из начала лога R0/R1/W с `68602c4f` → «бинарь не тот» и ложная остановка
серии, либо обратное — лог с `g465f0d8e` принимают за сборку до правки. Изменить: строка версии в отчёте — по exe; добавить, что строка
`git =` лога `36e2b042` читается `g465f0d8e` при коде `68602c4f` (доказательство кода — sha256 и сличение §2 этого отзыва).

**RC2 (печать F10e; исполнитель — Harness Engineer).** Что не так: опознание бинаря тега возможно по строке `git =` лога.
Сценарий отказа: как RC1 — ридер печати, сверяющий `g68602c4f`, бракует все три тега на верном бинаре. Изменить: печать `f10e.md`
опознаёт бинарь только по sha256 `36e2b042…` копии (п. 369(в)(3)); строка `git = …g465f0d8e` — известная метка, не помеха.

**RC3 (чтение гейта R1 `validated ≥ 151`; исполнитель — Harness Engineer в печати F10e, решение — лид F10f).** Что не так:
`validated` считает проверки всех стадий (VS/PS/CS/…, одна на каждую `CompilePermutation`), а не PS класса S151; строка печатается только
на кратном 256 (первое возможное значение — 256). Сценарий отказа: (а) холодный вход Sky Garden с < 256 проверками даёт 0 строк
`FixSvalStat:` — гейт `validated ≥ 151` по букве не читается, хотя проверок могло быть ≥ 151; (б) `validated` = 256 читается как «151 PS
проверено», хотя PS с массивом шага 4 в uniform-блоке среди них может не быть. Изменить: печать называет оба прочтения — «нет строки
`FixSvalStat:`» → «не определено» (как `validated` < 151 по п. 369(в)), и что `validated` — число всех проверок; доказательство, что
класс S151 проверен при `=1`, — R0 на той же холодной форме (отказ `=0` на первом таком модуле) плюс 0 `SPIR-V validation failed` в R1.

## 5. Замечания вне вердикта (не RC)

- Строка `FixSvalStat:` — не атомарный снимок: `rejected` читается отдельно и может включать отказ проверки, ещё не учтённой в `validated`
  (другой поток). На гейты не влияет: при `=1` любой отказ — `EXIT` того же потока; гейт R1 — 0 строк `SPIR-V validation failed`.
- При `--shader-validation false` (форма харнессов программы) `ValidateShaderSpirv` выходит до ветки — `KYTY_FIX_SVAL` ничего не меняет и
  строки `FixSvalStat:` нет; R0/R1/W по п. 369(в)(3) — только с `--shader-validation true`.
- На попадании в кэш трансляции проверки нет (п. 369(а)) — холод трансляции обязателен (п. 369(в)(3), уже в пункте).
- Код `68602c4f` содержит и коммиты `main` трека P после ветки FS3 (`741e3312`, `KYTY_PVAR_HOLD` N 30 → 90): бинарь F10c ≠ FS3 `540c035a` по
  `src/kernel/pvar.*`; без `KYTY_GAME_PATCH`/`KYTY_PVAR` путь не меняется [I по коду P, не проверено этим звеном].

## 6. Что этот отзыв НЕ доказывает

Что SPIR-V корректен для устройства и картинка верна; что выход 321 наблюдался в игре; что пользователь запускает игру с проверкой шейдеров;
что 151 — все такие PS игры; что Ф16 исправлен в игре (это F10e/F10f); что Ф10 достижим. Ни одно число — не выигрыш.

## 7. Файлы (`docs/track-f/f10d/`, sha256 — `SHA256SUMS_f10d.txt`)

`mk_wt_f10d.sh`, `mk_wt.log`, `build_f10d.cmd`, `configure_tail.log`, `build_tail.log`, `kytyGitVersion_f10d.h`, `bindiff_f10d.py`,
`bindiff_f10d.txt`, `grep_f10d.txt`, `base_f10d.txt`, `mk_f10d.py`, `run_f10d.py`, `run_f10d_cached.py`, `build_tool_f10d.cmd`,
`prep.out.txt`, `build_tools.out.txt`, `mut_f10d.txt`, `var_<вариант>_summary.txt` (7), `var_base_run.out.txt`.
