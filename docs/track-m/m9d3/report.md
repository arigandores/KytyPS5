# M9d3 (`HPP-876`, трек M, волна 2) — правка RC1 M9e2: свидетель многослотовых `narrow` в `DiagT109::NoteDraw`

Звено Emu Engineer по `ROADMAP.md` п. 789(в)(1)–(5) (KytyPS5 `d273a2bc`); отзыв — `docs/track-m/m9e2/review.md` §2 RC1,
§3 Н3 (KytyPS5 `895ae733`); база — worktree M9d `C:/kyty/m657/m9d/wt` @ `3f5d8725` (M9d2). Дата 2026-10-13 UTC; время
событий — `times.txt` (строки `date -u`). **Игра не запускалась; бинарь теста не установлен; ГП-кейсы `dl_cases.txt` не
запускались (ГП-стенд — отдельный режим `--t188-gpu-stand`); сборки `--parallel 2`, процессы — приоритет Idle (`lowrun.py`,
п. 760).** Замка `C:/kyty/SEALED_RUN.lock` не было ни перед одной командой; перед каждой командой > 60 с — проверка
`executionRunId` звена прогонов M3a2 (`HPP-861`) строкой `times.txt`; одна команда не запущена из-за непустого
`executionRunId` (§5). Метки: [c] — проверено, [I] — вывод, [U] — неизвестно. **Код в игре не проверен — WIP до тегов M9f.**

## 1. Итог

| что | значение |
|---|---|
| записка | `note_m9d3.md` (sha256 `6c068042…`), зафиксирована 10:06:23Z — до первой правки кода (`patch_m9d3.py` позже, `times.txt`); поправка Н3 — §4 записки и §4 ниже |
| коммит worktree | **`067dfd93`** на M9d2 `3f5d8725`, worktree `C:/kyty/m657/m9d/wt` (чист после коммита) |
| код в `main` | **`2042c697`** — cherry-pick `067dfd93` на `d273a2bc` без конфликтов; **`patch-id --stable` по `-U0` `86729716` = `86729716`**, с контекстом по умолчанию тоже равны (`241a0e85`), `--numstat` равны (`main_vs_wt.out.txt`) |
| бинарь теста | `kyty_emulator.exe` **sha256 `feb55b549e26fc6dfd2a03f08997446106cc8bba6bb7e8c31449e7991a737a2c`**, версия `KytyPS5-2026-09-15-6a2987a-1939-g067dfd932` (вторая, устаревшая строка `…-1936-g3d2270241` — как у M9d2, Н4 п. 789(д)); закреплённая копия **`C:/kyty/m657/bin/kyty_emulator_feb55b54.exe`**; **не установлен**; строка `T109Stat:` в бинаре — с тремя новыми полями (`binary_m9d3.out.txt`) |
| подпись трансляции | `KYTY_SHADER_SOURCE_HASH` = **`8dcf31779bbcb7c6e605653a138dae162f645a46` = MS1 = M9d = M9d2** [c `kytyGitVersion.h` сборки и строка бинаря]; файлов набора подписи в коммите 0 [c] |
| `check_gate_order.py` | `GATE ORDER: clean`; вывод на worktree **байт в байт = выводу M9d2** (`gate_order_wt.out.txt`); гейтов и ручек правка не трогает |
| `shader_cfg_tests` | 135 тестов, **0 падений** (строки со словом `failed` — те же 5, что у M9d2, байт в байт); 374 модуля SPIR-V **байт в байт = M9d2** (`tests_spv_cmp.out.txt` `ALL OK`) |
| стенд функций | `t188_stand` **51 из 51** (было 49; + `t109_cd16`, `t109_cd1`), плечо `cls` ok — на сборке worktree (`stand_pure.out.txt`, контроль мутантов) и на сборке `main` (`stand_main.out.txt`) |
| ГП-стенд | `--t188-gpu-stand` **16 из 16** при `KYTY_IMAGE_DETILE_FUSE=1` и `=0`; с валидацией — 16 из 16, 0 строк про очистку/копию (2 строки слоя — как у M9d, M9d2) — плечи контроля мутантов, итог **`ALL OK`** (`mut_control.out.txt`, `mut/control_arms.txt`) |
| мутанты | **29 из 29 пойманы**: t7, t8, t9 (новые), t1–t6 (t4 переякорен на новую форму ветки `z_export`), m1–m15 с m8s, g1–g4 (повтор); исходники после мутантов = до (sha256 5 файлов, `wt_after_mut.check.txt`); контроль (пересборка обеих целей, 5 плеч) `ALL OK` |
| сборка `main` | `wtmain` переведён на `2042c697` (detached): `t188_stand` собран, стенд `pure`+`cls` `ALL OK`; `kyty_emulator` собран (проверка компиляции; бинарь `main` не используется) |

## 2. Что сделано (п. 789(в)(1)–(2))

| место (`main` `2042c697`) | правка |
|---|---|
| `src/libs/diagT188.h:243` `DiagT109::NoteDraw` | последний аргумент `bool clip_disable`; комментарий — определения трёх полей |
| `src/libs/diagT188.h:255–257` `DiagT109::Totals` | `zx_narrow_vi`, `bias_narrow_vi`, `narrow_cd` — последними, в этом порядке |
| `src/libs/diagT188.cpp:1059–1061` | три `std::atomic<uint64_t>` рядом с прежними семью |
| `src/libs/diagT188.cpp:1070` `NoteDraw` | признак слота (площадь ножниц) и `lo`/`hi` не тронуты; внутри `if (narrow)` ветки `z_export` — `if (count > 1) Bump(g_zx_narrow_vi)` (`:1094`), то же в ветке `bias`; затем `if (narrow && (z_export \|\| bias) && count > 1 && clip_disable) Bump(g_narrow_cd)` (`:1108`) — один раз на draw |
| `src/libs/diagT188.cpp` `Read`, `PrintStat` (`:1130`), `ResetForStand` (`:1131`) | три поля — последними; строка `T109Stat: … ovr_vpc=… zx_narrow_vi=… bias_narrow_vi=… narrow_cd=…` |
| `src/graphics/host_gpu/renderer/renderDraw.cpp:518` `SetGraphicsDynamicParams` | аргумент `ctx.GetClipControl().clip_disable` (поле `bool`, `hardwareContext.h:330`) — то же место вызова, внутри `if (DiagT188::Mode() >= 1)` (`:508`) |

Определения по п. 789(в)(2) [c кода]: `zx_narrow_vi` ⊂ `zx_narrow` (тот же `Bump` под `count > 1`), `bias_narrow_vi` ⊂
`bias_narrow`; `narrow_cd` — draw, засчитанный хотя бы в одно из двух (`narrow ∧ (z_export ∨ bias)`), при `count > 1` и
`clip_disable`.

**Состояние (правило отчёта о флагах/полях):** три счётчика уровня пространства имён, как прежние семь — установка
только `Bump` в `NoteDraw` (`diagT188.cpp:1094`, `:1103` ветка `bias`, `:1108`), снятие — только `ResetForStand`
(`:1131`–`:1136`, зовёт стенд); живут весь процесс по замыслу (накопительные счётчики, печать `periodic`/`exit`); выходов
`NoteDraw` до `Bump` два (не D32; ни `test`, ни `write`) — там счётчики не трогаются, как и прежние. Флагов, TLS и
сохранённых указателей нет; `clip_disable` передаётся по значению.

## 3. Стенд T109 (п. 789(в)(3))

Ожидания всех 11 прежних случаев T109 дополнены тремя полями (прежние — `clip_disable = false`); 38 случаев T188 `NoteDraw`
не зовут и поля T109 не сверяют — как до правки. Поля `zx_narrow` / `bias_narrow` / `zx_narrow_vi` / `bias_narrow_vi` /
`narrow_cd`:

| случай | `count` | ожидание | итог |
|---|---|---|---|
| `t109_d24`, `t109_off`, `t109_full`, `t109_nozx`, `t109_vi16`, `t109_inv` | 1–16 | `narrow` нет или не засчитан ⇒ все новые 0 | ✓ |
| `t109_max` | 1 | 1 / 0 / **0** / 0 / 0 | ✓ |
| `t109_vp1` | 2 | 0 / 1 / 0 / **1** / 0 | ✓ |
| `t109_inv_n` | 1 | 1 / 1 / **0** / **0** / 0 | ✓ |
| `t109_vi16n` | 16 | 1 / 1 / **1** / **1** / 0 | ✓ |
| `t109_ovr` | — | новые 0 (`ovr_w` 2, `ovr_vpc` 1) | ✓ |
| **`t109_cd16`** (новый) | 16, `clip_disable`; все слоты 16384×16384 с ножницами 64×64; слот 0 `[0, 1]`, слоты 1–15 `0/0` | 1 / 1 / 1 / 1 / **1** | ✓ |
| **`t109_cd1`** (новый) | 1, `clip_disable`; слот 0 `[0; 0,5]` | 1 / 1 / **0** / **0** / **0** | ✓ |

`t109_cd16` воспроизводит сценарий RC1 M9e2: ложный `narrow` неиспользуемого слота виден в `zx_narrow`, а свидетели
`zx_narrow_vi` / `narrow_cd` его отмечают; `t109_cd1` — положительный контроль раздела по `count` (настоящий однослотовый
`narrow` при `clip_disable` в `_vi` и `narrow_cd` не идёт).

Мутанты T109 (`mut_m9d3.py`, плечо `pure`; провалившиеся случаи — `C:/kyty/m657/m9d3/mut/<имя>/pure_out.txt`):

| мутант | что | пойман случаями |
|---|---|---|
| t1 | только слот 0 | `t109_vp1`, `t109_vi16n`, `t109_cd16` |
| t2 | `≥`/`≤` вместо строгих | `t109_full`, `t109_inv`, `t109_vi16` |
| t3 | `bias_d32` без условия D32 | 10 случаев с `bias` (в т. ч. `t109_d24`) |
| t4 | `zx_narrow` без `zx_d32` (переякорен) | `t109_vp1`, `t109_nozx` |
| t5 | все слоты без признака ножниц | `t109_vi16` |
| t6 | сырые `minDepth`/`maxDepth` | `t109_inv` |
| **t7** | оба `Bump(g_*_narrow_vi)` удалены | **`t109_vp1`, `t109_vi16n`, `t109_cd16`** |
| **t8** | `_vi` при `count >= 1` | **`t109_max`, `t109_inv_n`, `t109_cd1`** |
| **t9** | `narrow_cd` без `clip_disable` | **`t109_vp1`, `t109_vi16n`** |

## 4. Члены записки (п. 789(в)(4))

- **Путь `=0` не меняется** [c диф `3f5d8725..067dfd93`]: новые строки исполняемого кода эмулятора — тело `NoteDraw` и
  аргумент вызова в `renderDraw.cpp`, оба под `if (DiagT188::Mode() >= 1)`; при `=0` вызов и вычисление аргументов (включая
  `ctx.GetClipControl().clip_disable`) не исполняются.
- **Набор подписи трансляции не тронут** [c]: файлы коммита — `diagT188.{h,cpp}`, `renderDraw.cpp`, `tests/T188Stand.cpp`
  (вне `src/graphics/shader/**` и `SHADER_CACHE_EXTRA_FILES`, `CMakeLists.txt:156`); `KYTY_SHADER_SOURCE_HASH` сборки
  `8dcf3177…` = M9d2; SPIR-V тестов 374 из 374 байт в байт = M9d2.
- **Поправка текста M9d2 §2 о `NaN` (Н3 отзыва M9e2).** Отчёт M9d2 §2 стр. 40 — «слот с `NaN` в `minDepth`/`maxDepth` …
  `narrow` не ставится этим слотом [I]» — неточен. `std::min(a, b)` = `(b < a) ? b : a`, `std::max(a, b)` = `(a < b) ? b : a`;
  сравнение с `NaN` ложно, результат — первый аргумент (в коде первый — `minDepth`). Поэтому несимметрично: `NaN` в
  `maxDepth` даёт `lo = hi = minDepth` ⇒ `narrow` ставится при любом `minDepth` из `[0, 1]` (0 ⇒ `hi < 1`, иначе `lo > 0`);
  `NaN` в `minDepth` даёт `lo = hi = NaN` ⇒ не ставится [c по определению `std::min`/`std::max`; в стенде случая нет]. Без
  `VK_EXT_depth_range_unrestricted` такой вьюпорт — нарушение правил Vulkan; код не меняется.

## 5. Отступления

- Сборки — в каталогах M9d (`C:/kyty/m657/m9d/build`, `buildmain`; `build_m9d.cmd`, `build_m9d_main.cmd`, `lowrun.py`) —
  инкрементально от M9d2; worktree M9d — по букве п. 789(в)(5). `wtmain` переведён с `6fde3e0c` на `2042c697` (detached).
- Полный прогон всех плеч стенда на сборке worktree — плечи контроля мутантов (`pure`, `cls`, `gpu1`, `gpu0`, `gpuv` `ALL OK`)
  на дереве, равном коммиту `067dfd93` (коммит сделан после контроля без правок исходников; sha256 файлов — `wt_after_mut.check.txt`).
- Сборка `kyty_emulator` `main` (проверка компиляции, `buildmain`) в 10:31:28Z не запущена: `HPP-861` (M3a2) получил
  непустой `executionRunId` (общее правило 30); после того как поле опустело — запущена и прошла (`BUILD OK`, `times.txt`).
- Драйвер `run_stand_m9d3.py` и `mut_m9d3.py` собраны из скриптов M9d2 скриптом `mk_m9d3.py` (`WANT_PURE` 51, имена полей
  `T109Stat`, каталог вывода, t4 переякорен, новые t7–t9).

## 6. Что M9d3 НЕ доказывает

- что случаи RC1 M9e или RC1 M9e2 встречаются в ASTRO BOT; что поля `_vi` отделяют все ложные `narrow` (draw с `count > 1`
  может быть и настоящим — он уходит в «не определено» по п. 789(г)); что `zx_narrow` после правки равен суженному клэмпу на
  ГП; место вызова (`clip_disable` того же draw) доказано только чтением — стенд зовёт `NoteDraw` напрямую (Н2 п. 789(д));
- всё из п. 785(ж); ни одно число — не выигрыш; 60 FPS не обещаются.

## 7. Файлы (`docs/track-m/m9d3/`)

| файл | что |
|---|---|
| `note_m9d3.md` | записка до кода (места, ожидания стенда, члены, поправка Н3) |
| `patch_m9d3.py`, `patch_wt.out.txt` | правка (якоря целыми строками), `ALL OK` |
| `mk_m9d3.py`, `run_stand_m9d3.py`, `stand_pure.out.txt`, `stand_main.out.txt` | драйвер стенда и прогоны (worktree, `main`) |
| `mut_m9d3.py`, `mut_bT.out.txt`, `mut_bP.out.txt`, `mut_bG1.out.txt`, `mut_bG2.out.txt`, `mut_control.out.txt`, `wt_before_mut.sha`, `wt_after_mut.check.txt` | мутанты |
| `gate_order_wt.out.txt` | `check_gate_order.py` |
| `tests_run.log`, `tests_failed_lines.txt`, `tests_spv_cmp.out.txt` | `shader_cfg_tests` и сверка SPIR-V с M9d2 |
| `binary_m9d3.out.txt`, `main_vs_wt.out.txt`, `cherry_pick.out.txt` | строки бинаря; patch-id `main` = worktree |
| `commit_msg_m9d3.txt`, `times.txt`, `sha256.txt` | сообщение коммита; время событий; sha256 файлов и бинаря |
