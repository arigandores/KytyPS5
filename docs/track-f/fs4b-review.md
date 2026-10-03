# FS4b (`HPP-471`, Red Team): ревью бинаря FS4 `31cbfee8` — **PASS**

**Вердикт: PASS.** Требуемых изменений (RC) нет — звено FS4a2 не нужно. Замечаний без RC — 2 (З1–З2, ниже), каждое со сценарием отказа и владельцем.

Решение лида — `8449030a:docs/ROADMAP.md:20552` п. 378 (якорь «378. **Звено F10f трека F (`HPP-454`, лид): Ф16 `FIXED` по п. 369(в)»; +1 — «прошла; счёт
трека F, не отгрузка; умолчание `KYTY_FIX_SVAL=1`»), подпункт (г)(2) — `8449030a:docs/ROADMAP.md:20588` (якорь «(г) **Отгрузка — FS4, четвёртый бинарь отгрузки
трека F (константы лида):**»; +1 — «(1) **FS4a (Emu Engineer, без замка).**»); чтение члена (5) — `0dd8e001:docs/ROADMAP.md:20660` п. 380 (якорь «380. **Звено FS4a
трека F (`HPP-470`, лид, review): принят — бинарь FS4 `31cbfee8`»; +1 — «член п. 378(г)(5) для бинаря, собранного cherry-pick, читается через `git cherry`**»).
Вход — отчёт FS4a `8b1dfa78:docs/track-f/fs4a.md`, коммит кода `main` `17adaf80`, worktree FS4a `3d0e46da`, бинарь `31cbfee8261f…eaa5`. Прочитаны п. 369, 378, 380
целиком, `envFlag.h`, `ValidateShaderSpirv` и конструктор `PipelineCache` на `3d0e46da`. Начало работы — 08:02:27Z (после коммита `0dd8e001` с п. 380). Игра не
запускалась; установленный `540c035a` и кэши не тронуты (sha256 `ps5 em/kyty_emulator.exe` после сборки — `540c035ac09f…`, `sha_fs4b.txt`). Замок
`C:/kyty/SEALED_RUN.lock` за звено появлялся один раз (08:11:39Z–08:19:09Z, инцидент ниже), `C:/kyty/f287/STOP` не было (каждая команда начиналась проверкой; сборки — под `lockrun.sh`). Время — UTC по `date -u`, события —
`C:/kyty/f287/times.txt` (строки `FS4b`). **Инцидент общего правила 27 (исполнитель FS4b).** В 08:11:39Z появился чужой замок `C:/kyty/SEALED_RUN.lock` (`go_s.sh pi_w1 … (go_s9.sh seal 06)`, трек S, S10). Моя команда правки отчёта, начатая в этот момент, остановилась на проверке замка (exit 3) и ничего не записала, но параллельно с ней инструментом Write записаны два текстовых файла моей папки — `C:/kyty/f287/fs4/fs4b/facts_fs4b.tmpl.md` (mtime 08:11:52Z) и `put_fs4b.py` (08:11:58Z): запись файла под чужим замком, нарушение исполнителя (вызовы Write шли в одном пакете с командой проверки, а не после неё). Процессов под замком не запускалось; папка эмулятора, кэши, `bin/` и папки трека S не тронуты; дальше — ожидание без работы до снятия замка (08:19:09Z). Урок: запись инструментом Write — только после команды проверки замка, не в одном пакете с ней. Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно.

## Итог по членам п. 378(г)(2)

| Член | Итог | Чем |
|---|---|---|
| путь `KYTY_FIX_SVAL=0` на FS4 по коду = FS3 | ✓ [c] | ветка OFF — `valid = tools.Validate(spirv)`, тот же вызов, что `if (tools.Validate(spirv))` в `d515b901`; дальше общий код (дизассемблер, `SPIR-V validation failed`, `return false`) без изменений; строка `FixSval: mode=0 ubo_std_layout=<0/1>` в конструкторе (§1) |
| путь по умолчанию = F10c при `=1` | ✓ [c] | дифф `92d11340..3d0e46da` — 1 hunk: только комментарий и инициализатор `enabled`; для любого непустого значения новое выражение = `EnvValueOn(value)` F10c; не задана и `""` → 1 (фикстура, §4) |
| `--shader-validation false` — прежний путь FS3 по коду | ✓ [c] | `ValidateShaderSpirv` возвращает `true` на `:1357–1359` до чтения ручки; единственный вызов — `:2163`; отличие от FS3 в этом режиме — только запись атомика `g_fix_sval_ubo_std_layout` и строка `FixSval:` в конструкторе (§1) |
| дифф FS4 против FS3 — только три файла | ✓ [c] | `git diff --stat d515b901 3d0e46da` по всему дереву — `graphicContext.h` +3, `pipelineCache.cpp` +45/−1, `vulkanWindow.cpp` +2 (`lineage.out.txt`) |
| P-var и Б42 не тронуты | ✓ [c] | `pvar.cpp`, `gamePatchFile.cpp`, `descriptors.cpp`, `textureCache.cpp/.h` — без изменений `d515b901..3d0e46da`; `4414e235`, `722c5e7f`, `d515b901` — предки; `741e3312`, `c9b4268e` (трек P после P23) — не предки, `git cherry` `+` |
| член (5) в чтении п. 380(б) | ✓ [c] | `git cherry -v 3d0e46da X X^`: `4e72289e`, `68602c4f`, `17adaf80` — `-`; patch-id `68602c4f` = `92d11340` (`8be6b8b1…`), `17adaf80` = `3d0e46da` (`738f74d8…`), `4e72289e` = `d515b901` (`c6e8d258…`) |
| своя сборка из чистого worktree и sha | sha **не равен** — причина названа ✓ [c] | свой `a70bc76d…e577`; `.text` 0 различающихся байт; остаток после маски — 240 серий: 238 хэшей `?A0x…` в `.data`, 2 — каталог отладки (время, GUID PDB) в `.rdata`, прочих 0 (`RESIDUAL ALL OK`); плюс время PE и строка `SDL_REVISION` (§2, З1) |
| свой `shader_cfg_tests` | ✓ [c] | 127 тестов, падение 1 — Б11, rc 0; лог sha256 `5a60758a…` = FS4a = P23 байт в байт (§3) |
| таблица умолчаний | ✓ [c] | `knobs_fs4b.py` (порт моего `knobs_fs3b.py`, не код FS4a): ON-IF-UNSET — ровно семь, `== item 378(g)(1) set: True`; тот же сканер на `d515b901` — `KYTY_FIX_SVAL` в наборе нет (отрицательный контроль), прочие строки = мой вывод FS3b (§3) |
| разбор умолчания фикстурой | ✓ [c] | `FIXTURE ALL OK`: выражение извлечено из кода `3d0e46da` и `92d11340`, собрано с настоящим `envFlag.h`, 51 строка на коммит (новый процесс на значение окружения + режим аргумента); контроль `92d11340` даёт 0 на «не задана» и `""` (§4) |

## 1. Код (`3d0e46da` = `d515b901` + `92d11340` (копия F10c `68602c4f`) + `3d0e46da` (копия FS4a `17adaf80`))

- **Происхождение [c]** (`lineage_fs4b.sh`, `lineage.out.txt`): цепочка родителей `3d0e46da` → `92d11340` → `d515b901` → `722c5e7f`; три файла F10c на `68602c4f^` и
  `d515b901` равны (`git diff --quiet` — EQUAL) ⇒ cherry-pick F10c лёг на ту же базу, что в `main`; три файла `92d11340` = `68602c4f`, три файла `3d0e46da` = `main`
  `17adaf80` (EQUAL); `17adaf80` трогает только `pipelineCache.cpp` (+8/−3). `src/graphics/shader` не тронут ⇒ подпись трансляции не меняется:
  `KYTY_SHADER_SOURCE_HASH` `56189185f9e9…` в моём `kytyGitVersion.h` и в обоих exe — по 1 разу (`bincmp.out.txt`); `kytyGitVersion.h` без комментариев = FS4a.
- **Ветка OFF = FS3 [c].** На `d515b901` после `SetMessageConsumer` — `if (tools.Validate(spirv)) { return true; }`; на `3d0e46da` — `valid = tools.Validate(spirv)` в
  ветке `else` и `if (valid) { return true; }`. Тот же объект `tools` (`SPV_ENV_VULKAN_1_3`), тот же перегруз без опций; ни счётчиков, ни строки `FixSvalStat:` в
  ветке нет. Остаток функции (`:1389–1404`) в диффе не участвует.
- **Ветка ON = F10c `=1` [c].** Код ветки в `3d0e46da` — байт в байт `92d11340` (дифф `92d11340..3d0e46da` — 1 hunk `:1337–1351`, `fs4_vs_92d11340.diff` = файлу FS4a
  `cmp`); `FixSvalEnabled` — static local, magic static C++11; первый вызов — конструктор `PipelineCache` (`:4670`), до `StartWorkers`/`StartPrecache`.
- **`--shader-validation false` [c].** `Config::ShaderValidationEnabled()` = `g_config->shader_validation_enabled` (`emulatorConfig.cpp:78–80`); при `false` —
  `return true` на `:1357–1359` до `FixSvalEnabled()`; вызов `ValidateShaderSpirv` в файле один (`:2163`, `CompilePermutation`). Значит, в форме харнессов
  (W/V) трансляция и исход проверки равны FS3; новое — только `g_fix_sval_ubo_std_layout.store` и строка `FixSval: mode=1 ubo_std_layout=1` в конструкторе
  (на неё и опирается член `fs4_w` п. 378(г)(3)).
- **Устройство [c].** `vulkanWindow.cpp` +2 — только запись `graphics.uniform_buffer_standard_layout_enabled` из уже стоявшего в FS3
  `features12.uniformBufferStandardLayout = supported_features12.uniformBufferStandardLayout`; набор включаемых возможностей устройства не меняется ни при
  каком значении ручки.
- Символы `FixSvalEnabled`, `g_fix_sval_ubo_std_layout`, `ValidateShaderSpirv` — в анонимном пространстве имён (`:69`–`:1840`) — ODR-коллизии нет.
- `check_gate_order.py --src fs4b/wt/src` — `GATE ORDER: clean`, вывод = FS4a по модулю CR (`gate_order.out.txt`).
- В моём exe `FixSval: mode=`, `FixSvalStat: validated=`, `KYTY_FIX_SVAL`, `FixB42Ext: mode=` — по 1, `SPIR-V validation failed` — 3 (как FS4a по первым четырём).

## 2. Своя сборка и сравнение с `31cbfee8`

- Worktree `C:/kyty/f287/fs4/fs4b/wt` — `git worktree add --detach` прямо на `3d0e46da` (`mk_wt_fs4b.sh` = мой `mk_wt_fs3b.sh` с путём и коммитом), подмодули как
  FS3b; `git status --short` 0 строк, файлов `src/` с CR 0 из 456 (`mk_wt.log`). `build_fs4b.cmd` = мой `build_fs3b.cmd` с путями (флаги те же), под `lockrun.sh`:
  configure 08:04:00–08:04:48Z rc 0, build 08:04:53–08:05:50Z rc 0. Свой бинарь — **sha256 `a70bc76d98bbd047e9d44845b328a1906571baa5b3385ce25a7c462680a9e577`**,
  24 664 064 байт (= размеру `31cbfee8`); **в `bin/` не кладётся**.
- `bincmp_fs4b.py` (порт моего `bincmp_fs3b.py`; `bincmp.out.txt`): копия `bin/kyty_emulator_31cbfee8.exe` — sha256 = отчёту FS4a ✓; секции те же 8, все одной
  длины ✓; **`.text` 18 158 070 байт — 0 различающихся байт** ✓; строк `.data` 782 = 782 ✓; `.rdata` вне записи PDB — одна строка: `SDL-KytyPS5-2026-09-15-6a2987a-1874-g3d0e46da`
  (моя) против `…-1873-g92d11340` (`31cbfee8`) ⇒ итог скрипта `BINCMP FAILED` — только из-за неё.
- `fullcmp_fs4b.py` (`fullcmp.out.txt`; печатает первые 20 серий) и `residual_fs4b.py` (`residual.out.txt`, класс каждой серии): после замены строки SDL, пути
  `fs4b` → `fs4a` и обнуления времени PE остаются 240 серий — 238 внутри хэшей `?A0x…` имён в `.data` (зависят от пути исходника), 2 — каталог отладки в `.rdata`
  (время, GUID `RSDS`); класса «прочее» — 0, `RESIDUAL ALL OK`. **Причина неравенства sha названа [c]:** путь сборки, время, GUID PDB и строка `SDL_REVISION`;
  машинный код равен.
- **Откуда строка SDL [c]:** `build/3rdparty/SDL2/include/SDL2/SDL_revision.h` FS4a — `…-1873-g92d11340`, мой — `…-1874-g3d0e46da`. FS4a конфигурировал worktree
  на `92d11340` (до cherry-pick FS4a), шаг `version` перегенерирует только `kytyGitVersion.h`. В `src/` `3d0e46da` упоминаний `SDL_GetRevision`/`SDL_REVISION` — 0
  ⇒ на поведение не влияет. См. З1.

## 3. Тесты и таблица умолчаний

- **`shader_cfg_tests`** — своя сборка цели `tests` (до 08:07:34Z), прогон 08:07:35Z в окружении `env -i` (только `PATH`, `SYSTEMROOT`, `WINDIR`,
  `KYTY_TESTS_CONTINUE=1`, `KYTY_TESTS_VERBOSE=1`; `KYTY_*` в окружении агента — 0): 127 `[test]`, rc 0, падение 1 — Б11 (`IMAGE_SAMPLE_C` /
  `IMAGE_SAMPLE_C_LZ`). Лог `cfgtests_defaults.log` — **sha256 `5a60758aab7abd57…` = лог FS4a = P23 / FS3b байт в байт**.
- **Таблица умолчаний** (`knobs_fs4b.py 3d0e46da`, `knobs_fs4b.out.txt`): `git diff 4fc501f4 3d0e46da -- src/` — 57 файлов, +8 818 / −136; строк с чтением окружения
  добавлено 24 (на `d515b901` — 22; +2 — `pipelineCache.cpp:1347–1348`); ON-IF-UNSET — ровно `KYTY_FIX_B1B`, `B26`, `B42`, `B9A`, `DUALSRC`, `MINIMIZE`, `SVAL`,
  `== item 378(g)(1) set: True`. Итог скрипта `CHECK BY HAND` — из-за тех же 5 UNDECIDED (`KYTY_AUDIO_SYNC`, `KYTY_DUMP_GCN`, `KYTY_POKE`, `KYTY_PVAR`,
  `KYTY_S_PCW_FORCE_MS`), прочитанных руками в FS3b (`docs/track-f/fs3b-review.md` §3 — 0 / прежний путь): их файлы, кроме `pipelineCache.cpp`, дифф
  `d515b901..3d0e46da` не задевает, а в `pipelineCache.cpp` их строки сдвинуты, текст тот же (дифф выводов сканера на `d515b901` и `3d0e46da` — только
  `KYTY_FIX_SVAL`, счётчики и номер строки `KYTY_DUMP_GCN` 3593 → 3632; `KYTY_S_PCW_FORCE_MS` `:288` выше правки). Отрицательный контроль: тот же сканер на
  `d515b901` печатает `set: False missing ['KYTY_FIX_SVAL']`. **Таблица FS4a подтверждена.**

## 4. Фикстура разбора умолчания (`mk_fixture_fs4b.py`, `build_fx.cmd`, `run_fixture_fs4b.py`, `fixture.out.txt`)

Генератор берёт из `git show <коммит>:pipelineCache.cpp` тело `FixSvalEnabled` (у `3d0e46da` — строки лямбды между `static const bool enabled = [] {` и `}();`,
с проверкой, что их ровно две: `getenv` и `return <выражение>`; у `92d11340` — однострочный static), кладёт выражение без пересказа в программу с настоящим
`src/common/envFlag.h` worktree; программа собрана тем же `clang-cl` (vcvars64). Режим `env` — значение из окружения нового процесса (Python `subprocess`, копия
окружения без `KYTY_FIX_SVAL` + значение), режим `arg` — то же выражение на `argv[2]`. Случаи: не задана; `""`; `0`, `false`, `FALSE`, `False`, `off`, `OFF`, `Off`,
`no`, `NO`, `No`; прочие — `1`, `00`, `" 0"`, `"0 "`, `yes`, `on`, `true`, `2`, `nv`, `offf`, `n`, `-0`, `0x0`, `fals`.

| Случай | `3d0e46da` (FS4) | `92d11340` (F10c, контроль) |
|---|---|---|
| не задана (`getenv=null`) | **1** | 0 |
| `""` (окружение: `getenv=str:[]`; аргумент) | **1** | 0 |
| `0/false/off/no` в любом регистре ASCII (10 значений) | 0 | 0 |
| прочие (14 значений, включая `00`, `" 0"`, `"0 "`, `offf`, `fals`) | 1 | 1 |

`FIXTURE ALL OK` (51 строка на коммит, расхождений 0). На этой машине CRT передал `""` через окружение как пустую строку (`getenv=str:[]`), не как
отсутствие; оба прочтения дают 1. Фикстура различает FS4 и F10c ровно на двух строках «не задана» и `""` — она чувствительна к правке.

## Замечания без RC

- **З1 — строка `SDL_REVISION` бинаря `31cbfee8` называет `92d11340`, а не `3d0e46da`** (повтор З1 FS3b: там рекомендовано configure после cherry-pick; FS4a
  сделал configure на `92d11340`). Сценарий отказа: проверка происхождения по строкам exe (`strings | grep SDL-KytyPS5`, например член п. 378(г)(5) в аудите)
  назовёт `92d11340` — коммит без умолчания FS4a — и даст ложное «FS4a в бинаре нет», хотя `KYTY_GIT_REVISION` = `3d0e46da`, а `.text` равен моему из `3d0e46da`.
  Поведение эмулятора не меняется (§2). **Что делать:** FS4c/FS4d и аудит опознают FS4 по sha256 `31cbfee8…` и `KYTY_GIT_REVISION`; в следующих worktree с
  cherry-pick (пересборка FS4 на коммите трека P по п. 378(г)(5)) — configure после последнего cherry-pick. Пересборка FS4 ради строки не требуется.
  Владелец — лид (FS4d, строкой в приёмке) и Emu Engineer (следующая пересборка).
- **З2 — откат `KYTY_FIX_SVAL=0` и копией `540c035a` возвращает отказ Ф16 только на новой трансляции.** Проверка стоит в `CompilePermutation` (`:2163`) —
  на трансляции; подпись `56189185` у FS3 и FS4 одна. PS класса S151, впервые оттранслированный на FS4 по умолчанию (принят), ляжет в `_ShaderCache` и после
  отката не будет проверяться заново [I по коду: проверка — только на пути трансляции]. Сценарий отказа: прогон «отката» с тёплым после FS4 кэшем, ожидающий
  `SPIR-V validation failed` (форма `fs4_r0`), отказа не увидит и ложно прочтёт «откат не работает»; и наоборот, откат не уберёт с диска модули, принятые
  ON. Буква п. 378(г)(3) уже требует холод для `fs4_r0` (форма R0 F10e — удаление каталога варианта), поэтому не RC. **Что делать:** печать FS4c — `fs4_r0`
  только на холоде, после `fs4_r1`/`fs4_hb` — с новым удалением каталога; формулировка отката в FS4d — «на холодном каталоге варианта». Владелец —
  Harness Engineer (печать FS4c), лид (FS4d).

## Чек-лист кода (роль)

Хронометража в правке нет; гонки — `enabled` — magic static, `g_fix_sval_ubo_std_layout` — `release`/`acquire`, счётчики `relaxed` (только для строки
`FixSvalStat:`), запись атомика до `StartWorkers` [c]; инвариантов `*_bad` нет; ранние возвраты — `return true` при выключенной проверке до ручки, в ветках
ON/OFF возвратов нет, выход один через `valid` [c]; правка с обратным слэшем (`'\0'`) — `patch_fs4a.py` файлом, CR в `src/` worktree 0 [c]; якорь патча —
блок комментария и функции целиком (1 hunk в `92d11340..3d0e46da`) [c]; кадр стека — новых локальных буферов нет (`ValidatorOptions` — указатель на
`spv_validator_options`) [c]; подпись трансляции не меняется — `src/graphics/shader` не тронут, `56189185` = FS3 [c]; новых имён в таблицах гейтов нет
(`GATE ORDER: clean`).

## Файлы

`C:/kyty/f287/fs4/fs4b/`, копии в `docs/track-f/fs4b/` (текстовые — LF): `mk_scripts_fs4b.py`, `mk_wt_fs4b.sh`, `mk_wt.log`, `build_fs4b.cmd`, `lockrun.sh`,
`sha_fs4b.txt`, `lineage_fs4b.sh`, `lineage.out.txt`, `fs4_vs_92d11340.diff`, `mk_cmp_fs4b.py`, `bincmp_fs4b.py`, `bincmp.out.txt`, `fullcmp_fs4b.py`,
`fullcmp.out.txt`, `residual_fs4b.py`, `residual.out.txt`, `mk_knobs_fs4b.py`, `knobs_fs4b.py`, `knobs_fs4b.out.txt`, `knobs_d515b901.out.txt`,
`cfgtests_defaults.log`, `gate_order.out.txt`, `mk_fixture_fs4b.py`, `fx_3d0e46da.cpp`, `fx_92d11340.cpp`, `build_fx.cmd`, `run_fixture_fs4b.py`,
`fixture.out.txt`, `put_fs4b.py`, `facts_fs4b.tmpl.md`. Сборочное дерево `build/`, worktree `wt/` и exe фикстуры — только локально.

## Не заявляется

Что пользователь запускает игру с проверкой шейдеров; что 151 — все такие PS игры; что `validated` — число PS класса S151; что встроенная проверка не отвергнет
PS другого класса на других уровнях; что SPIR-V корректен для устройства и картинка верна; что бинарь работает в игре (игра не запускалась; теги — FS4c);
ни одно число — не выигрыш; 60 FPS не обещаются.
