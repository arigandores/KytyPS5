# F9e2b (`HPP-429`, Emu Engineer): правка `KYTY_FIX_B42` (M2c) по RC1/RC2 F9f — член «рисовали после заливки», `rearm`, счётчики по экстенту

Решение лида — `2b60f547:docs/ROADMAP.md:19222` п. 353 (якорь «353. **Звено F9f трека F (`HPP-423`, Red Team) принято»; +1 — «дополняется
исключением «рисовали после заливки», повторная заливка живой цели входит в `hit`»), подпункты (г)(1)–(4); п. 351(в) (`00f179e0:docs/ROADMAP.md:19129`,
якорь «351. **Звено F9e трека F (`HPP-422`, Emu Engineer) принято»; +1 — «механизм Б42 — CMASK fast clear цели T6 некратного 1024 экстента») в
остальном в силе. Вход — отзыв `dcd762d6:docs/track-f/f9f-review.md` (RC1, RC2), код F9e2 `55490711`, отчёт `b481fabc:docs/track-f/f9e2.md`.
Игра не запускалась; установленный бинарь `4aa62e95` и кэши не тронуты. Время — UTC по `date -u`, события — `C:/kyty/f287/f9/times.txt`.
Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно. **WIP по дыму: бинарь собран и проверен тестами, игрой не проверялся**
(дым и шесть тегов — F9g после F9f2).

## Итог

- **Код в названных файлах** (`descriptors.cpp`, `textureCache.cpp`, `textureCache.h`); `renderDraw.cpp`, `colorRenderTarget.cpp`,
  `renderCompute.cpp`, транслятор — не тронуты. Отличить вызов ветки FCE — **параметром** `FindRenderTarget(…, bool fce_materialize = false)`
  (умолчание держит единственный вызов draw-пути `renderDraw.cpp:1649` без правки).
- Коммиты: **`main` `2da00d80`** (родитель `20605249`; только три файла правки); **worktree `C:/kyty/f287/f9/f9e2b/wt` — `0cbaa644` на
  `3785f025` (F9e2, cherry-pick `23a0b3f2`, дерево = `23a0b3f2`, `git diff --quiet` ✓) на `4414e235`**; `src/graphics` worktree = `main`
  `2da00d80` (`git diff --quiet 2da00d80 0cbaa644 -- src/graphics` ✓; три файла `cmp` ✓).
- **Бинарь: sha256 `c494bb6996b88b728cbf3fbb778e6de25b46f411bea85293ae4a8dd7d1a9de08`**, копия
  `C:/kyty/f287/f9/bin/kyty_emulator_c494bb69.exe` (sha256 копии тот же). Не установка. Бинарь F9e2 `3082c45f` заменяется этим для F9g.
- `check_gate_order.py` (`C:/kyty/s113/`) — `GATE ORDER: clean`, вывод байт в байт = F9e2 (гейтов и ручек правка не добавляет).
- `shader_cfg_tests` — **127 тестов, падение 1 — Б11** (`IMAGE_SAMPLE_C`/`IMAGE_SAMPLE_C_LZ`), rc 0; лог **байт в байт = P23 и F9e2**
  (sha256 `5a60758aab7abd57…` у всех трёх).
- **Подпись трансляции `KYTY_SHADER_SOURCE_HASH` = `56189185f9e9f9a0ea5174f3f85206e6d099db3d`** — `build/kytyGitVersion.h:9`, 1 вхождение в exe;
  `git diff --quiet 4414e235 0cbaa644 -- src/graphics/shader` ✓. `KYTY_GIT_REVISION` = `0cbaa644…` (`kytyGitVersion.h:7`).
- В exe строки `FixB42: mode=`, `KYTY_FIX_B42`, `drawn=%` — по 1.
- Предупреждения сборки в правленых файлах: одно — `descriptors.cpp:611` `-Wreturn-type`, прежнее.

## Diff

- Против `55490711` (F9e2 → F9e2b, три файла): `textureCache.cpp` 33 строки, `textureCache.h` 37, `descriptors.cpp` 104 (120 вставок, 54 удаления) —
  `docs/track-f/f9e2b/f9e2b_vs_55490711.diff`.
- Против `4414e235` (F9e2 + F9e2b, worktree `0cbaa644`): `textureCache.cpp` 32 строки, `textureCache.h` 34, `descriptors.cpp` 121 (184 вставки, 3 удаления) —
  `docs/track-f/f9e2b/f9e2b_vs_4414e235.diff`. Скрипт правки — `docs/track-f/f9e2b/patch_f9e2b.py` (якоря — целые строки/блоки, каждый ровно 1 раз,
  проверка всех до записи; LF), применён к `main` и worktree одинаково.

## Место правки (пути:строки — `2da00d80`)

1. `src/graphics/host_gpu/renderer/cache/textureCache.h:70–76` — параметр `fce_materialize` (умолчание `false`) у `FindRenderTarget`.
2. `textureCache.h:123–140` — `MetaFillQuery` + поля `b42_fill_seq`, `b42_draw_seq`; `QueryMetaFill(uint64_t address, ImageId image)`.
3. `textureCache.h:193–195` — `MetaDataInfo::b42_fill_seq` (последним полем; назначенные инициализаторы `{.type = …}` его не задевают).
4. `textureCache.h:334–339` — `m_b42_seq` (один монотонный счётчик кэша) и `m_b42_draw_seq` (`std::unordered_map<ImageId, uint64_t>`), оба под `m_lock`.
5. `src/graphics/host_gpu/renderer/cache/textureCache.cpp:451` — `DeleteImage`: `m_b42_draw_seq.erase(id)`.
6. `textureCache.cpp:2346–2347`, `:2359–2364` — `FindRenderTarget`: при `!fce_materialize` — `m_b42_draw_seq[id] = ++m_b42_seq` (после
   `usage.render_target = true`, под `m_lock` `:2351`).
7. `textureCache.cpp:3240–3241` — `TrackDccFill`: в ветке, которая ставит `fill_value` (`:3228–3239`, типы `PendingDcc`/`Dcc`/`CMask`) —
   `b42_fill_seq = ++m_b42_seq` (под `m_lock` `:3224`).
8. `textureCache.cpp:3138–3157` — `QueryMetaFill`: под одним захватом `m_lock` — `b42_draw_seq` образа и поля записи с `b42_fill_seq`; ничего не пишет.
9. `src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3626–3725` — `FixB42Enabled`, `FixB42Kind {None, Hit, Drawn}`, `FixB42Probe` (`:3658`),
   `FixB42Note` (`:3686`).
10. `descriptors.cpp:3742–3775` — ветка CMASK `MaterializeBoundTargetDccClears`: `desc` меняется только при `Hit && FixB42Enabled()` (`:3744`);
    существующий `FindRenderTarget(…, true)` (`:3757–3764`); при `kind != None` — `applied` (только `Hit` и `=1`, `:3768–3772`) и `FixB42Note`.

### (1) Член «не рисовали после заливки» — по коду

Один счётчик `m_b42_seq` (`textureCache.h:338`) растёт `++` только под `m_lock` в двух местах: заливка (`textureCache.cpp:3241`) и привязка цели
draw-пути (`:2363`). Обе записи берут **новое** значение, поэтому для любой пары событий порядок значений = порядок событий под замком:
привязка после заливки ⇒ `draw_seq > fill_seq`; до неё ⇒ `draw_seq < fill_seq`. `drawn` ⇔ `b42_draw_seq > b42_fill_seq` (`descriptors.cpp:3674`).
Имена: `fill_seq`/`draw_seq` п. 353(г)(1) в коде — `b42_fill_seq`/`b42_draw_seq`, потому что `MetaDataInfo::fill_seq` уже есть и значит другое
(последовательность записи GPU для проверки свежести, `textureCache.h:192`, `textureCache.cpp:3243`, `:3275–3280`); её правка не трогает.

**Таблица всех вызовов `FindRenderTarget` (`git grep` по `src` на `2da00d80`, 2 места):**

| # | Путь:строка | Откуда приходит | Класс | `fce_materialize` |
|---|---|---|---|---|
| 1 | `src/graphics/host_gpu/renderer/renderDraw.cpp:1649` (`AcquireTargetView`, медленный путь) | `AcquireRenderTargets` `renderDraw.cpp:2112` ← draw: `:4354–4357` напрямую или `RtsPlaceB` `:3718` | **draw-путь** | `false` (умолчание) → штамп `draw_seq` |
| 2 | `src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3757–3764` | `MaterializeBoundTargetDccClears` ← `renderDraw.cpp:5009`, `:5236` (поглощаемый draw FCE/decompress: `ConsumeMetadataColorOperation` → возврат `:5014`/`:5241` до `PrepareDrawRenderState` `:5126`/`:5314`) | **FCE** | `true` → без штампа |

`FindDepthTarget` — цель глубины, CMASK цвета не касается. Других вызовов нет [c].

**Привязки draw-пути без вызова `FindRenderTarget`** — два обхода, оба запрещены сменой эпохи метаданных:
- `rtfast` (`renderDraw.cpp:1612–1631`): требует `cache.MetaEpoch() == fast.meta_epoch` (`:1620`); `fast.meta_epoch` пишется `:1673` — **после**
  медленного `FindRenderTarget` `:1649`.
- `rtskip` место B (`renderDraw.cpp:3621–3646`): требует `fast.meta_epoch == rec->meta` (`:3633`) и `cache.MetaEpoch() == rec->meta` (`:3644`);
  `rec->meta = t_rts_meta1` (`:3907`), прочитан `:3719` после `AcquireRenderTargets` `:3718`. Место A (`RtsPlaceA`) целей не берёт.
- `TrackDccFill` **безусловно** сдвигает эпоху (`textureCache.cpp:3248`), эпоха только растёт (`fetch_add`, `textureCache.h:333`).
- Значит: первая привязка цели draw-пути после заливки (заливка — после записи `fast.meta_epoch`) идёт медленным путём → `FindRenderTarget(…, false)`
  → `draw_seq > fill_seq`; все последующие быстрые привязки идут уже после этого штампа. Член «рисовали после заливки» истинен при любой привязке
  draw-пути между заливкой и FCE [c по коду], с оговорками ниже.

**Оговорки (не заявления):**
- (О1) [I] Окно между `:1649` и `:1673` (`rtfast`) / `:3718` и `:3719` (`rtskip`): если `TrackDccFill` на **другом** потоке попадёт между штампом и
  чтением эпохи, запись быстрого пути возьмёт эпоху после заливки, а штамп — до неё. Заливки (`renderCompute.cpp`) и draw идут через исполнитель
  команд GPU; доказательства одного потока у меня нет. То же окно у существующей очистки пути 1024 (`PrepareCmaskClear` тоже только на медленном
  пути).
- (О2) [I] Штамп привязан к `ImageId` (буква п. 353(г)(1) «в образ»). Если между draw и FCE образ цели пересоздан (новый `ImageId` по тому же адресу) и
  содержимое перенесено копией, у нового образа штампа нет → `hit`. Слот id не наследует чужой штамп: `DeleteImage` стирает его (`:451`) до
  `m_slot_images.erase` (`:473`, `:476`). Вариант «штамп и по адресу данных образа» (строже, ошибка видна полем `drawn`) — вне буквы, вопрос лиду в
  комментарии звена; кодом не сделан.
- (О3) [I] FCE и draw берут цель через `ResolveRenderColorTarget` по одним регистрам `CB_COLOR*`; разный `ImageId` у draw и FCE одной поверхности не
  ожидаю, не доказано.

### (2) `hit`, `drawn`, `rearm`, `applied` — по коду

`FixB42Probe` (`descriptors.cpp:3658–3681`): прежние члены п. 351(в)(2) (`:3661–3666`; ветка уже требует `rt.base.addr`, `rt.cmask.addr`,
`cmask_fast_clear_enable`, без DCC — `:3738–3739`); запись по `rt.cmask.addr` — `found`, **`PendingDcc` или `CMask` с `clear_mask != 0`** (`:3668`),
`fill_value == 0`, `fill_size ≥ w·h·layers/128` (`:3669`); затем `drawn` (`:3674–3677`) — `desc` не меняется, очистки нет; иначе `Hit`, `rearm = cmask`
(`:3678–3679`). `rearm` ⊂ `hit` по построению. `applied` (`:3766–3772`) — только `Hit` при `=1`: второй запрос; запись `CMask`, `fill_value == 0`
и хотя бы один бит маски снят; бит снимается только `textureCache.cpp:2013` сразу за `ClearImage` `:2011` (довод F9e2, принят F9f п. 6) — для
`rearm` тот же путь (`PrepareCmaskClear` на записи `CMask`: ветки `:1985`, `:1993` не входят, `:2002` пропускает, `:2009–2014` чистит).
При `=0` запись `CMask` у цели некратного экстента не возникает (её ставит путь 1024 или `=1`) — `rearm` при `=0` ожидается 0 [I, п. 353(в)(4)].

### (3) Строка

`FixB42: mode=<0|1> hit=<n> applied=<n> drawn=<n> rearm=<n> hit_all=<n> last_frame=<n> extent=<w>x<h> cmask=0x<addr> clear=<w0>/<w1>`
(`descriptors.cpp:3719–3722`). `FixB42Note` зовётся только при `kind != None` (`:3766`), т. е. каждый вызов — рост `hit` или `drawn`. Счётчики —
`std::map<(w,h), Counts>` (`:3688–3698`): `hit`, `applied`, `drawn`, `rearm` — экстента строки; `hit_all` — сумма `hit` по всем экстентам.
Печать — на каждом вызове, пока строк < 256; дальше — если с прошлой напечатанной строки ≥ 600 кадров (`:3714–3716`). `last_frame`, `extent`,
`cmask`, `clear` — этого события; строка печатается после учёта `applied` этого события.

## Состояние, вводимое правкой (места установки и снятия)

- `m_b42_seq` (`textureCache.h:338`) — растёт `:2363`, `:3241` под `m_lock`; не снимается (монотонный счётчик процесса).
- `m_b42_draw_seq[id]` (`textureCache.h:339`) — ставится `textureCache.cpp:2363` (под `m_lock`, только при `!fce_materialize`); снимается
  `DeleteImage` `:451` (вызывающие держат `m_lock` — та же дисциплина, что у `m_download_images.erase` строкой выше). Выход `DeleteImage` без снятия —
  `:433–435` (образа нет или не зарегистрирован): слот тогда не стирается (`m_slot_images.erase` есть только `:473`, `:476` этой функции, после
  снятия), значит штамп остаётся у того же объекта; зарегистрированным `FindRenderTarget` образ берёт только живым (`EXIT` `:2353–2354`).
- `MetaDataInfo::b42_fill_seq` — ставится `:3241`; сбрасывается в 0 вместе с записью (`MetaDataInfo {}` / `{.type = …}` — `:1880`, `:1895`, `:1909`,
  `:1976`, `:1989`, `:1996`, `:2477`, `:2486`) и стирается с записью (`:462`, `:3354`, `:3406`). Сброс даёт `fill_value = 0xffffffff` — `hit`/`drawn`
  невозможны.
- `fce_materialize` — параметр вызова, состояния нет.
- `FixB42Note` — статические `by_extent`, `hit_all`, `lines`, `printed_at` под своим `std::mutex`; единственный ранний выход — порог 600 кадров
  (`:3714–3716`) после учёта счётчиков.
- Новых `BumpMetaEpoch` нет.

## Путь `=0` = `4414e235` по значениям

При `KYTY_FIX_B42` не заданной / `""` / `0/false/off/no` (`Common::EnvFlagOn`, `descriptors.cpp:3645`):
1. `color.desc` не меняется (`:3744` требует `FixB42Enabled()`); второй запрос — только при `=1` (`:3768`).
2. `FindRenderTarget`: новый параметр управляет только записью штампа (`textureCache.cpp:2362–2364`); остальной код и аргументы прежние; вызов
   ветки FCE (`descriptors.cpp:3757–3764`) — с теми же `id`, `desc`, `guest_clear_regs`.
3. `TrackDccFill`: добавлена только запись `b42_fill_seq` (`:3241`); эпоха, маска, `fill_value`, `fill_size`, `fill_seq`, `m_fill_stamp_*` — прежние.
4. `b42_fill_seq`, `m_b42_draw_seq`, `m_b42_seq` читает только `QueryMetaFill` (`:3142–3143`, `:3155`) — `git grep` по `src`: других чтений нет [c];
   `MetaDataInfo` нигде не сравнивается целиком и не сериализуется (нет `operator==`/`sizeof`) [c]. В Vulkan и в решения о метаданных они не идут.
5. Отличия при `=0`: строки `FixB42:` (с полями `drawn`, `rearm`, `hit_all`), запись в `std::unordered_map` на каждом медленном захвате цели цвета
   (память и время под `m_lock`), +8 байт на запись `m_surface_metas`.
Значит, команды GPU, состояние кэша, влияющее на решения, и картинка при `=0` — те же, что у `4414e235` [c по коду]. Подтверждение прогоном — F9g.

## Тесты

`C:/kyty/f287/f9/f9e2b/build/shader_cfg_tests.exe` из worktree-сборки, без `KYTY_*` в окружении, кроме `KYTY_TESTS_CONTINUE=1`
`KYTY_TESTS_VERBOSE=1`: rc 0, 127 `[test]`, падения: `pixel IMAGE_SAMPLE_C must use OpImageSampleDrefImplicitLod`, `pixel IMAGE_SAMPLE_C_LZ must use
explicit dref lod` (Б11, известно); лог `docs/track-f/f9e2b/cfgtests_defaults.log` (sha256 `5a60758aab7abd5736f04e5710da32aaaeb12698922eeb58f979f2ab1f2f8f3f`)
= `C:/kyty/p283/p23/cfgtests_defaults.log` = F9e2 (`diff` пуст).

## Сборка

Чистый worktree `C:/kyty/f287/f9/f9e2b/wt` (`mk_wt_f9e2b.sh` — копия `mk_wt_f9e2.sh` + cherry-pick `23a0b3f2`: статус 0 строк, 0 файлов с CR в `src/`),
патч, configure (01:37:57Z), сборка-проверка (01:40:01Z), коммит `0cbaa644`, пересборка с версией (01:40:17Z, 01:40:36Z), тесты (01:41:06Z) — всё
под `lockrun.sh` (убивает шаг при замке или `C:/kyty/f287/STOP`), флаги = F9e2/P23 (`build_f9e2b.cmd` — копия с путями f9e2b). Замка и STOP не было.

## Файлы

`C:/kyty/f287/f9/f9e2b/`, копии в `docs/track-f/f9e2b/`: `patch_f9e2b.py`, `patch_main.out.txt`, `patch_wt.out.txt`, `f9e2b_vs_55490711.diff`,
`f9e2b_vs_4414e235.diff`, `gate_order.out.txt`, `cfgtests_defaults.log`, `mk_wt_f9e2b.sh`, `mk_wt.log`, `mk_scripts.py`, `build_f9e2b.cmd`,
`lockrun.sh`, `commit_msg_code.txt`, `SHA256SUMS_f9e2b.txt`.

## Не заявляется

Что RC1 случается в этой игре (число целей с `drawn` > 0 [U] до F9g); что CMASK-очистка — единственная причина Б42; цвет очистки T6; что раскладка
CMASK некратного экстента верна; что на PS5 вода в этих ракурсах чистая; что исправление будет; что другие сцены не изменятся при `=1`; ни одно
число — не выигрыш; 60 FPS не обещаются; путь без `KYTY_FIX_B42` не меняется (по коду, см. выше).
