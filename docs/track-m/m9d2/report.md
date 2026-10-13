# M9d2 (`HPP-874`, трек M, волна 2) — правка RC1 M9e в `DiagT109::NoteDraw`: растеризуемые слоты и диапазон min/max

Звено Emu Engineer по `ROADMAP.md` п. 788(б)(1)–(6), (г) Н5 (KytyPS5 `ebdf7d34`); отзыв — `docs/track-m/m9e/review.md`
§8 RC1 (KytyPS5 `05a3f7a2`); база — worktree M9d `C:/kyty/m657/m9d/wt` @ `d490f648`. Дата 2026-10-13 UTC; время событий —
`times.txt` (строки `date -u`). **Игра не запускалась; бинарь теста не установлен; ГП-кейсы `dl_cases.txt` не запускались
(ГП-стенд — отдельный режим `--t188-gpu-stand`); сборки `--parallel 2`, процессы — приоритет Idle (`lowrun.py`, п. 760).**
Замка `C:/kyty/SEALED_RUN.lock` не было ни перед одной командой; звено прогонов M3a2 (`HPP-861`) — `executionRunId` пусто
при каждой проверке перед командой > 60 с (`times.txt`). Метки: [c] — проверено, [I] — вывод, [U] — неизвестно.
**Код в игре не проверен — WIP до тегов M9f.**

## 1. Итог

| что | значение |
|---|---|
| записка | `note_m9d2.md` (sha256 `f328fb92…`), зафиксирована 09:08:26Z — до первой правки кода (`patch_m9d2.py` 09:09:00Z, `times.txt`); строка Н5 — §3 записки |
| коммит worktree | **`3f5d8725`** на M9d `d490f648`, worktree `C:/kyty/m657/m9d/wt` (чист после коммита) |
| код в `main` | **`6fde3e0c`** — cherry-pick `3f5d8725` на `ebdf7d34` без конфликтов; **`patch-id --stable` по `-U0` `f7c2ea0d` = `f7c2ea0d`**, с контекстом по умолчанию тоже равны (`b21f7467`), `--numstat` равны (`main_vs_wt.out.txt`) |
| бинарь теста | `kyty_emulator.exe` **sha256 `662896a210c3558265c04c2043d4c3f0b1c246cea42a6c585274153dec596924`**, версия `KytyPS5-2026-09-15-6a2987a-1938-g3f5d8725d`; закреплённая копия **`C:/kyty/m657/bin/kyty_emulator_662896a2.exe`**; **не установлен**; бинарь `751bfa7f` в M9f не идёт (п. 788) |
| подпись трансляции | `KYTY_SHADER_SOURCE_HASH` = **`8dcf31779bbcb7c6e605653a138dae162f645a46` = MS1 = M6a3 = M9d** [c `kytyGitVersion.h` сборки]; файлов набора подписи в коммите 0 [c `git show --name-only 6fde3e0c`] |
| `check_gate_order.py` | `GATE ORDER: clean`; вывод на worktree **байт в байт = выводу M9d** (`gate_order_wt.out.txt`); гейтов и ручек правка не трогает |
| `shader_cfg_tests` | 135 тестов, **0 падений** (строки со словом `failed` — те же 5, что у M9d, байт в байт); 374 модуля SPIR-V **байт в байт = M9d** (`tests_spv_cmp.out.txt` `ALL OK`) |
| стенд функций | `t188_stand` **49 из 49** (было 45; + 4 случая п. 788(б)(4)), плечо `cls` ok — на сборке worktree (`stand_wt.out.txt`) и на сборке `main` (`stand_main.out.txt`) |
| ГП-стенд | `--t188-gpu-stand` **16 из 16** при `KYTY_IMAGE_DETILE_FUSE=1` и `=0`; с валидацией — 16 из 16, 0 строк про очистку/копию (2 строки слоя — Н1, 2 `VkImage` стенда при разрушении устройства, как у M9d и M9e); итог прогона драйвера **`ALL OK`** |
| мутанты | **26 из 26 пойманы**: t5, t6 (новые), t1–t4 (переякорены на новый цикл t1, t2), m1–m15 с m8s, g1–g4 (повтор); исходники после мутантов = до (sha256 7 файлов); контроль (пересборка обеих целей, 5 плеч) `ALL OK` (`mut_control.out.txt`) |
| сборка `main` | `wtmain` переведён на `6fde3e0c` (detached): `t188_stand` 49/49 и `kyty_emulator` собраны (проверка компиляции; бинарь `main` не используется) |

## 2. Что сделано (п. 788(б)(1)–(3))

| место (`main` `6fde3e0c`) | правка |
|---|---|
| `src/libs/diagT188.h:239` `DiagT109::NoteDraw` | новый аргумент `const VkRect2D* scissors` между `viewports` и `count`; forward-объявление `struct VkRect2D;` рядом с `struct VkViewport;` (заголовок Vulkan не включает) |
| `src/libs/diagT188.cpp:1066` `DiagT109::NoteDraw`, цикл `narrow` | слот пропускается, если `scissors[i].extent.width == 0 \|\| .height == 0`; по считаемому слоту `lo = std::min(minDepth, maxDepth)`, `hi = std::max(...)`, `narrow ⇔ lo > 0.0f ∨ hi < 1.0f` |
| `src/graphics/host_gpu/renderer/renderDraw.cpp:512` `SetGraphicsDynamicParams` | третий массив вызова — `scissors.data()` (тот же `std::array<vk::Rect2D, 16>`, что уходит в `setScissorWithCount`); место вызова не двинуто — после цикла слотов и после обоих `set*WithCount` (RC15 п. 785(б)(4) сохранён) |
| `tests/T188Stand.cpp` `CasesT109` | 6 прежних случаев — ножницы 64×64 в обоих слотах (ожидания прежние); 4 новых случая (§3) |

Правило (б)(1) — одно на три источника нерастеризуемого слота [c кода]: пустой слот (`viewport.width == 0` ⇒ код ставит
`scissor.extent = {0, 0}`); ножницы гостя нулевой площади — `calc_final_scissor` (`debug.cpp`) пересекает прямоугольники и в
`ScissorRectClamp` при `!ScissorRectValid` ставит `right = left`, `bottom = top` ⇒ `extent` 0 (отрицательной разности нет,
перевёрнутые ножницы тоже дают 0); ветка `clip_disable` меняет только вьюпорт, ножницы — те же `calc_final_scissor`.
Слот с `NaN` в `minDepth`/`maxDepth`: сравнения с `NaN` ложны ⇒ `narrow` не ставится этим слотом [I по коду; в стенде нет].

**Состояние:** правка не вводит ни флага, ни поля, ни TLS, ни счётчика — только аргумент-указатель на массив вызывающего,
живущий на стеке `SetGraphicsDynamicParams` дольше вызова `NoteDraw` (вызов синхронный, указатель не сохраняется) [c].

## 3. Стенд T109 (п. 788(б)(4))

Все четыре новых случая — D32 (`VK_FORMAT_D32_SFLOAT`), `test = write = z_export = bias = true`; пустой слот —
`minDepth = maxDepth = 0`, `width = height = 1`, ножницы `{0, 0}` (как оставляет `SetGraphicsDynamicParams`); активный слот —
вьюпорт 64×64 и ножницы 64×64. Сверяются `d32`, `zx_d32`, `zx_narrow`, `bias_d32`, `bias_narrow` и все 70 полей `T188Stat` (= 0).

| случай | слоты | активный | диапазон | `d32` / `zx_d32` / `bias_d32` | `zx_narrow` = `bias_narrow` | итог |
|---|---|---|---|---|---|---|
| `t109_vi16` | 16 | 0 | `[0, 1]` | 1 / 1 / 1 | 0 | ✓ |
| `t109_inv` | 1 | 0 | `[1, 0]` | 1 / 1 / 1 | 0 | ✓ |
| `t109_inv_n` | 1 | 0 | `[1; 0,5]` | 1 / 1 / 1 | 1 (положительный контроль min/max) | ✓ |
| `t109_vi16n` | 16 | 3 | `[0; 0,5]` | 1 / 1 / 1 | 1 | ✓ |

Мутанты T109 (`mut_m9d2.py`, плечо `pure`; провалившиеся случаи — `mut/<имя>/`):

| мутант | что | пойман случаями |
|---|---|---|
| t1 | только слот 0 | `t109_vp1`, `t109_vi16n` |
| t2 | `≥`/`≤` вместо строгих | `t109_full`, `t109_inv`, `t109_vi16` |
| t3 | `bias_d32` без условия D32 | прежние |
| t4 | `zx_narrow` без `zx_d32` | прежние |
| **t5** | все слоты без признака ножниц (проверка площади удалена) | **`t109_vi16`** |
| **t6** | сырые `minDepth`/`maxDepth` без min/max | **`t109_inv`** |

Код M9d `d490f648` = совмещение t5 и t6 — новые случаи `t109_vi16` и `t109_inv` на нём проваливаются (RC1(а) и (б)
воспроизведены стендом через t5, t6) [c].

## 4. Члены записки (п. 788(б)(5))

- **Путь `=0` не меняется** [c диф `d490f648..3f5d8725`]: новые строки исполняемого кода эмулятора — тело `NoteDraw` и
  аргумент вызова в `renderDraw.cpp`, оба под `if (DiagT188::Mode() >= 1)`; при `=0` вызов и вычисление аргументов не
  исполняются; массив `scissors` строился и до правки (для `setScissorWithCount`).
- **Набор подписи трансляции не тронут** [c]: файлы коммита — `diagT188.{h,cpp}`, `renderDraw.cpp`, `tests/T188Stand.cpp`;
  `KYTY_SHADER_SOURCE_HASH` сборки `8dcf3177…` = M9d; SPIR-V тестов 374 из 374 байт в байт = M9d.
- **Н5 (п. 788(г))** — строка записки (`note_m9d2.md` §3): `loadOp eClear` целей кадра (`context.cpp` `BeginRendering`,
  места `:417`, `:427`, `:435` базы M9e) отдельного флага `rb_wr` не имеет и покрыт штампом `MarkGpuModified` при захвате цели
  (`FindRenderTarget` / `FindDepthTarget`, быстрый путь draw), т. е. `NoteGpuWrite` (Sw) срабатывает до очистки прохода; код
  этой правкой не меняется.

## 5. Отступления

- Сборки — в каталогах M9d (`C:/kyty/m657/m9d/build`, `buildmain`; `build_m9d.cmd`, `build_m9d_main.cmd`, `lowrun.py`) —
  инкрементально от M9d; worktree M9d — по букве п. 788(б)(6). `wtmain` переведён с `4363c35e` на `6fde3e0c` (detached).
- Первая сборка стенда упала (`VkRect2D` не объявлен в `diagT188.h`) — доправка `patch_m9d2b.py` (forward-объявление) до
  коммита; второй вызов сборки эмулятора из bash не исполнился (аргумент `cmd /c`) и повторён (`times.txt`).
- Драйвер стенда `run_stand_m9d2.py` = `run_stand_m9d.py` M9d с `WANT_PURE` 49; `mut_m9d2.py` собран из `mut_m9d.py`
  скриптом `mk_mut_m9d2.py` (каталог вывода, драйвер, переякоренные t1/t2, новые t5/t6).

## 6. Что M9d2 НЕ доказывает

- что случаи RC1(а) или (б) встречаются в ASTRO BOT; что после правки `zx_narrow` равен суженному клэмпу на ГП (в какой слот
  VS пишет на самом деле, на ЦП не видно — [I]); поведение слота с `NaN` в глубине вьюпорта (в стенде нет);
- всё из §7 отчёта M9d и п. 785(ж); ни одно число — не выигрыш; 60 FPS не обещаются.

## 7. Файлы (`docs/track-m/m9d2/`)

| файл | что |
|---|---|
| `note_m9d2.md` | записка до кода (места, ожидания стенда, члены, Н5) |
| `patch_m9d2.py`, `patch_m9d2b.py`, `patch_wt.out.txt`, `patch_wt_b.out.txt` | правки (якоря целыми строками), `ALL OK` |
| `run_stand_m9d2.py`, `stand_pure.out.txt`, `stand_wt.out.txt`, `stand_main.out.txt` | драйвер стенда и прогоны (worktree, `main`) |
| `mk_mut_m9d2.py`, `mut_m9d2.py`, `mut_bT.out.txt`, `mut_bP.out.txt`, `mut_bG1.out.txt`, `mut_bG2.out.txt`, `mut_control.out.txt`, `wt_before_mut.sha`, `wt_after_mut.check.txt` | мутанты |
| `gate_order_wt.out.txt` | `check_gate_order.py` |
| `tests_run.log`, `tests_failed_lines.txt`, `tests_spv_cmp.out.txt` | `shader_cfg_tests` и сверка SPIR-V с M9d |
| `binary_m9d2.out.txt`, `main_vs_wt.out.txt`, `cherry_pick.out.txt` | строки бинаря; patch-id `main` = worktree |
| `commit_msg_m9d2.txt`, `times.txt`, `sha256.txt` | сообщение коммита; время событий; sha256 файлов и бинаря |
