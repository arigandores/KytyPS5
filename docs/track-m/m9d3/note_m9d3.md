# M9d3 (`HPP-876`) — записка до кода: свидетель многослотовых `narrow` в `DiagT109::NoteDraw`

Основание — `ROADMAP.md` п. 789(в)(1)–(5) (KytyPS5 `d273a2bc`); отзыв — `docs/track-m/m9e2/review.md` §2 RC1, §3 Н3
(KytyPS5 `895ae733`); база — worktree M9d `C:/kyty/m657/m9d/wt` @ `3f5d8725`. Записка фиксируется до первой правки кода.

## 1. Места

| место (worktree `3f5d8725`) | правка |
|---|---|
| `src/libs/diagT188.h` `DiagT109::NoteDraw` | последний аргумент `bool clip_disable`; комментарий — определения полей |
| `src/libs/diagT188.h` `DiagT109::Totals` | поля `zx_narrow_vi`, `bias_narrow_vi`, `narrow_cd` — последними, в этом порядке |
| `src/libs/diagT188.cpp` `NoteDraw` | признак слота (площадь ножниц) и `lo`/`hi` не меняются; внутри `if (narrow)` ветки `z_export` — `if (count > 1) Bump(g_zx_narrow_vi)`; то же для `bias`; после — `if (narrow && (z_export \|\| bias) && count > 1 && clip_disable) Bump(g_narrow_cd)` (один раз на draw) |
| `src/libs/diagT188.cpp` `Read`, `PrintStat`, `ResetForStand` | три новых счётчика — последними (строка `T109Stat:` ... `ovr_vpc=… zx_narrow_vi=… bias_narrow_vi=… narrow_cd=…`); сброс вместе с прежними |
| `src/graphics/host_gpu/renderer/renderDraw.cpp` `SetGraphicsDynamicParams` | аргумент `ctx.GetClipControl().clip_disable` (поле `bool`, `hardwareContext.h:330`) — то же место вызова, внутри `if (DiagT188::Mode() >= 1)` |
| `tests/T188Stand.cpp` `CasesT109` | ожидания 10 случаев `NoteDraw` и `t109_ovr` дополнены тремя полями; новые `t109_cd16`, `t109_cd1` |

## 2. Ожидания стенда (поля `zx_narrow` / `bias_narrow` / `zx_narrow_vi` / `bias_narrow_vi` / `narrow_cd`)

Прежние случаи — `clip_disable = false`:

| случай | `count` | narrow / zx / bias | ожидание |
|---|---|---|---|
| `t109_d24`, `t109_off` | 1 | — | 0 / 0 / 0 / 0 / 0 |
| `t109_full` | 2 | нет / да / да | 0 / 0 / 0 / 0 / 0 |
| `t109_max` | 1 | да / да / нет | 1 / 0 / 0 / 0 / 0 |
| `t109_vp1` | 2 | да / нет / да | 0 / 1 / 0 / **1** / 0 |
| `t109_nozx` | 1 | да / нет / нет | 0 / 0 / 0 / 0 / 0 |
| `t109_vi16` | 16 | нет | 0 / 0 / 0 / 0 / 0 |
| `t109_inv` | 1 | нет | 0 / 0 / 0 / 0 / 0 |
| `t109_inv_n` | 1 | да / да / да | 1 / 1 / 0 / 0 / 0 |
| `t109_vi16n` | 16 | да / да / да | 1 / 1 / **1** / **1** / 0 |
| `t109_ovr` | — | — | 0 / 0 / 0 / 0 / 0 (только новые поля; `ovr_w` 2, `ovr_vpc` 1 прежние) |

Новые (D32, `test = write = z_export = bias = true`; при `clip_disable` у всех слотов ширина/высота 16384, как ставит
`SetGraphicsDynamicParams`, ножницы 64×64 у всех слотов — `vport_scissor_enable = 0`):

| случай | слоты | диапазоны | ожидание |
|---|---|---|---|
| `t109_cd16` | 16, `clip_disable` | слот 0 `[0, 1]`, слоты 1–15 `0/0` | 1 / 1 / 1 / 1 / 1 (`narrow_cd` 1 — раз на draw при обоих `zx` и `bias`) |
| `t109_cd1` | 1, `clip_disable` | слот 0 `[0; 0,5]` | 1 / 1 / 0 / 0 / 0 (положительный контроль раздела по `count`) |

Стенд: 49 → 51 случай. Мутанты: **t7** — оба `Bump(g_*_narrow_vi)` удалены (ловят `t109_vp1`, `t109_vi16n`, `t109_cd16`);
**t8** — условие `_vi` `count >= 1` (ловят `t109_max`, `t109_inv_n`, `t109_cd1`); **t9** — `narrow_cd` без `clip_disable`
(ловят `t109_vp1`, `t109_vi16n`); t4 переякорен на новую форму ветки `z_export`; t1–t6 — повтором.

## 3. Члены (п. 789(в)(4))

- Путь `=0` прежний: аргумент вычисляется в вызове внутри `if (DiagT188::Mode() >= 1)`; новых состояний вне счётчиков нет.
- Набор подписи трансляции не тронут: файлы правки вне `src/graphics/shader/**` и `SHADER_CACHE_EXTRA_FILES`.
- Состояние: три `std::atomic<uint64_t>` уровня пространства имён (как прежние семь) — установка `Bump` в `NoteDraw`, снятие
  `ResetForStand` (только стенд); живут весь процесс, как прежние счётчики; флагов и TLS нет; `clip_disable` — аргумент по
  значению, не сохраняется.

## 4. Поправка текста M9d2 §2 (Н3 отзыва M9e2)

Отчёт M9d2 §2 стр. 40: «слот с `NaN` в `minDepth`/`maxDepth` … `narrow` не ставится этим слотом [I]» — неточно.
`std::min(a, b)` = `(b < a) ? b : a`, `std::max(a, b)` = `(a < b) ? b : a`; сравнение с `NaN` ложно, поэтому результат —
первый аргумент: `std::min(0,5f, NaN)` = 0,5 ⇒ `lo > 0` ⇒ `narrow`; `std::min(NaN, 0,5f)` = `NaN`, `std::max(NaN, 0,5f)` =
`NaN` ⇒ сравнения ложны ⇒ нет. Т. е. несимметрично по порядку аргументов (`minDepth` первым): `NaN` в `maxDepth` даёт
`lo = hi = minDepth` ⇒ `narrow` ставится при любом `minDepth` из `[0, 1]` (0 ⇒ `hi < 1`, иначе `lo > 0`); `NaN` в
`minDepth` даёт `lo = hi = NaN` ⇒ не ставится.
Без `VK_EXT_depth_range_unrestricted` такой вьюпорт — нарушение правил Vulkan; код не меняется, в стенде случая нет.
