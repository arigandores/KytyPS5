# M9d2 (`HPP-874`, трек M) — записка до кода: правка RC1 M9e в `DiagT109::NoteDraw`

Основание — `ROADMAP.md` п. 788(б)(1)–(6), (г) Н5 (KytyPS5 `ebdf7d34`); отзыв — `docs/track-m/m9e/review.md` §8 RC1
(KytyPS5 `05a3f7a2`); база — worktree M9d `C:/kyty/m657/m9d/wt` @ `d490f648`. Записана до первой правки кода.

## 1. Места и имена

| место | что меняется |
|---|---|
| `src/libs/diagT188.h` `DiagT109::NoteDraw` | новый аргумент `const VkRect2D* scissors` между `viewports` и `count` (то же число слотов) |
| `src/libs/diagT188.cpp` `DiagT109::NoteDraw`, цикл `narrow` | слот пропускается, если `scissors[i].extent.width == 0` или `.height == 0` (площадь 0 — не растеризуется); по считаемому слоту `lo = std::min(minDepth, maxDepth)`, `hi = std::max(minDepth, maxDepth)`, `narrow ⇔ lo > 0 ∨ hi < 1` |
| `src/graphics/host_gpu/renderer/renderDraw.cpp` `SetGraphicsDynamicParams`, вызов `NoteDraw` | третий массив — `scissors.data()` (тот же `std::array<vk::Rect2D>`, что уходит в `setScissorWithCount`); место вызова не двигается — после цикла слотов и после обоих `set*WithCount` (член RC15 п. 785(б)(4)) |
| `tests/T188Stand.cpp` `CasesT109` | 6 прежних случаев получают ножницы площади > 0 во всех слотах (ожидания прежние); 4 новых случая п. 788(б)(4): `t109_vi16`, `t109_inv`, `t109_inv_n`, `t109_vi16n` |

Правило (б)(1) одно на все три источника нерастеризуемого слота: пустой слот `width == 0` (код ставит `scissor.extent = {0, 0}`),
ножницы гостя нулевой площади (`calc_final_scissor` → `extent` 0, см. §3), ветка `clip_disable` (вьюпорт во всю область, ножницы — те же `calc_final_scissor`).

## 2. Ожидания стенда (точные, п. 788(б)(4))

Все четыре — D32 (`VK_FORMAT_D32_SFLOAT`), `test = write = z_export = bias = true`; пустой слот — `minDepth = maxDepth = 0`,
`width = 1`, ножницы `{0, 0}` (как в `SetGraphicsDynamicParams`); активный слот — ножницы 64×64.

| случай | слоты | активный | диапазон активного | `d32` | `zx_d32` | `zx_narrow` | `bias_d32` | `bias_narrow` |
|---|---|---|---|---|---|---|---|---|
| `t109_vi16` | 16 | 0 | `[0, 1]` | 1 | 1 | 0 | 1 | 0 |
| `t109_inv` | 1 | 0 | `[1, 0]` | 1 | 1 | 0 | 1 | 0 |
| `t109_inv_n` | 1 | 0 | `[1; 0,5]` | 1 | 1 | 1 | 1 | 1 |
| `t109_vi16n` | 16 | 3 | `[0; 0,5]` | 1 | 1 | 1 | 1 | 1 |

Число случаев стенда функций: 45 → 49 (`WANT_PURE` драйвера — 49).

Мутанты (подстановкой, сборка `t188_stand`, плечо `pure`): t5 «все слоты без признака ножниц» (проверка площади удалена) —
ожидается провал `t109_vi16`; t6 «сырые `minDepth`/`maxDepth` без min/max» — провал `t109_inv`; t1 (только слот 0) — `t109_vp1`,
`t109_vi16n`; t2 (нестрогие сравнения) — `t109_full`, `t109_vi16`; t3, t4 — прежние строки, прежние случаи.

## 3. Члены

- **Путь `=0` не меняется:** `NoteDraw` зовётся только под `if (DiagT188::Mode() >= 1)`; при `=0` аргументы не вычисляются;
  массив `scissors` строился и до правки (для `setScissorWithCount`) — новых вычислений на пути `=0` нет.
- **Набор подписи трансляции не трогается:** файлы правки — `src/libs/diagT188.{h,cpp}`, `renderDraw.cpp`, `tests/T188Stand.cpp`;
  ни одного файла из `src/graphics/shader/**`, `shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`, `imageInfo.h`.
- Знак `extent`: `extent` — `uint32_t` от разности `right − left`; отрицательной разности нет [c `debug.cpp`
  `ScissorRectClamp`: при `!ScissorRectValid` ставит `right = left`, `bottom = top`], т. е. перевёрнутые и пустые ножницы гостя
  дают `extent` 0 ⇒ слот не считается. Считаемый слот = слот с теми ножницами, что получает ГП.
- **Н5 (п. 788(г)):** `loadOp eClear` целей кадра (`context.cpp` `BeginRendering`, места `:417`, `:427`, `:435` базы M9e) —
  место записи образа, отдельного флага `rb_wr` не имеет; покрыт штампом `MarkGpuModified` при захвате цели
  (`FindRenderTarget` / `FindDepthTarget`, быстрый путь `renderDraw.cpp` draw), т. е. `NoteGpuWrite` (Sw, `wseq` и флаг `rb_wr`
  при ждущем чтении) срабатывает на захвате цели до очистки этого прохода. Код этой правкой не меняется.
- Бинарь теста — новая закреплённая копия `C:/kyty/m657/bin/kyty_emulator_<sha8>.exe`, не устанавливается; `main` —
  cherry-pick коммита worktree с равным `patch-id --stable` по `-U0`.
