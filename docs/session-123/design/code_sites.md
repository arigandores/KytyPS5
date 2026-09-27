# Сессия 123 — карта кода для ручки `skipceil` (приложение к `design123.md`)

Автор — Probe Designer (шаг 1, `HPP-24`). Только чтение `C:/kyty/KytyPS5/src` (HEAD `3d167e0`). Пути — от
`src/graphics/`, если не сказано иное. Строки — текущего дерева; Emu Engineer перепроверяет каждую при патче.
Помечено **[П]** — проверено проектировщиком чтением строк; остальное — из обзора кода по файлам, сверено выборочно.

## 1. Путь draw

| что | где | примечание |
|---|---|---|
| PM4 → обработчики draw | `guest_gpu/command_processor/pm4Dispatch.cpp:181-193`; `pm4Handlers.cpp:1661` (DrawIndex), `:1702` (Indirect), `:1716` (IndirectMulti), `:1740` (IndexOffset), `:1758` (IndexAuto) | отдельного пакета mesh/GE нет |
| единственные два вызова рендерера из CP | `guest_gpu/graphicsRun.cpp:3003` (`RenderExecutor::DrawIndex`), `:3343` (`DrawAuto`) **[П]** | косвенные и multi сходятся сюда |
| счётчик `draws` (`Counter::Draws`, `DrawNs`) | `graphicsRun.cpp:3000`, `:3340` — `Scope` на уровне PM4, ДО рендерера **[П]** | пропуск внутри рендерера `draws` не меняет |
| вход рендерера DrawIndex | `host_gpu/renderer/renderDraw.cpp:3390`; `PopPendingOperationsLazy` `:3399`; render mutex `:3416`; `BindFloorLatchDraw` `:3428`; `DrawStatBegin` `:3435` **[П]** | |
| ранние возвраты DrawIndex | нулевой счёт `:3436`; метаданные-операция `:3440-3444` (`ConsumeMetadataColorOperation` → `MaterializeBoundTargetDccClears`); копия глубины `:3445-3448` (`DepthStencilCopy`); нет VS `:3450`; GE `:3454` **[П]** | метаданные и копия глубины — операции гостя в обёртке draw |
| то же DrawAuto | `renderDraw.cpp:3566`; мьютекс `:3589`; метаданные `:3611-3615`; копия глубины `:3616-3619`; нет VS `:3621` **[П]** | |
| `PrepareDrawRenderState` | DrawIndex `:3530`; внутри — `ResolveColorTargets` (MSAA-резолв, `:3716-3747`, вызов `:2007`) | резолв идёт вместе с draw |
| `ExecutePreparedDraw` | `:2424`; `PrepareBindings` `:2604`, `:2624`; `AcquireRenderTargets` `:2841`; `GetGraphicsPipeline` `:2900`; пропуск `AsyncPipelines` `:2906-2921` **[П]** | |
| `m_skipped_draws` | `render.h:497`, `TakeSkippedDraws` `:500`; `++` `renderDraw.cpp:2911`; читается `:2899` (запрет ожидания пайплайнов на остаток кадра) **[П]** | новой ручке трогать ЗАПРЕЩЕНО |
| `rt_att`/`rt_kpx` | `renderDraw.cpp:1340-1341` в `AcquireRenderTargets` | при пропуске до `:3450` не считаются |
| `vp_kpx` | `renderDraw.cpp:407` (`SetGraphicsDynamicParams`, после пайплайна) | только выпущенные draw |
| `rpd_a*` (проходы по форме) | `renderDraw.cpp:2931` (после пропуска `AsyncPipelines`) **[П]** | сумма = переведённые draw — НЕЗАВИСИМЫЙ свидетель пропуска |
| M1 (draw-ahead) | хэш-таблица слотов 32 768 (`pipeline/pipelineCache.cpp:2441-2446`); невзятый слот освежается или вытесняется (`:2730-2771`), `da_unused` (`:2736-2739`) | не копится и не вешает |
| кольца на draw | stream (`cache/streamBuffer.cpp:263-320`), куча дескрипторов (`pipeline/descriptorHeap.cpp:52-77`), запись (`commandRecorder.cpp:186`), санитайзер (`indirectArgsSanitizer.cpp:110-116`) | выделяются по требованию — пропуск ничего не держит |

## 2. Граница кадра на GuestGpu и удержание флипа

| что | где |
|---|---|
| четыре входа флипа | `graphicsRun.cpp:3891` `Flip()`, `:3911` `Flip(addr,value)`, `:3936` `FlipWithInterrupt`, `:3967` `PrepareCpuFlip` **[П]** |
| порядок внутри `Flip()` | `BindFloorFlipHook` → `GpuMarkersFlip` → `CheckBuffer` → `DrainDeferredProtection` → `PrepareVideoOutFlip` (записывает копию буфера показа) → `MarkFlipIfIncomplete` (`:3904`) → `WriteAtEndOfPipe*Flip` → `Flush` **[П]** |
| `MarkFlipIfIncomplete` | `graphicsRun.cpp:3792-3796`: `TakeSkippedDraws() != 0` → `VideoOut::MarkFlipIncomplete` **[П]** |
| `request.incomplete` | `presentation/videoOut.cpp:234`; `FlipQueue::MarkIncomplete` `:1092-1100` **[П]** |
| удержание | `FlipQueue::Flip` `:1169-1179`: при `incomplete` и `KYTY_ASYNC_HOLD_FRAME` ≠ `0` → `Presenter::Discard` + строка `AsyncPipelines: flip N held` (≤ 64) **[П]** |
| темп флипа | `IsFlipDueLocked` `:491-498` — только счётчик вблэнков, ОДИН И ТОТ ЖЕ для показа и удержания **[П]** |
| `Discard` | `presentation/window/swapchain.cpp:943-945` — только `frames.Release`, без GPU и ожидания; `Present` `:841-941` — acquire, запись blit под render mutex, `presentKHR` **[П]** |
| видео `KYTY_REC` | пишется только в `Present` (`swapchain.cpp:873`, `:904`) — удержанные флипы в видео отсутствуют |
| `flip_status.count++`, `Poll`, `BurnPublishFrame` | `videoOut.cpp:1194`, `:1197`, `:1200` — для удержанных флипов тоже **[П]** |
| `request_id` | `videoOut.cpp:892` `m_next_request_id++` (общий для GPU- и CPU-флипов) |
| `GetFrameNum()` | `m_done_num`, растёт в `GuestGpu::Done()` на потоке гостя (`graphicsRun.cpp:331`) — НЕ граница флипа |
| `gw_flip_ns` | `VideoOutDriver::WaitFlipDone` `videoOut.cpp:3221-3225` (только роль Gpu), вложен в `gw_proc` **[П]** |

## 3. Наблюдаемое гостем — ничего из этого не зависит от записанных draw

| пакет | где | поведение |
|---|---|---|
| метки EOP / RELEASE_MEM | `graphicsRun.cpp:3421`, `:3471`, `:3561` | memcpy CPU при разборе; прерывания — после тика GPU (`sync.cpp:298-305`) |
| RELEASE_MEM с источником GDS | `graphicsRun.cpp:3440-3448` **[П]** | `SynchronizeGpu()` + чтение буфера GDS — GDS пишут шейдеры (в т.ч. draw) |
| EVENT_WRITE / окклюзия 0x39 | `graphicsRun.cpp:3688`, `:3758-3782` | синтетика CPU |
| WRITE_DATA | `graphicsRun.cpp:561-585` | memcpy CPU |
| COPY_DATA / DMA_DATA | `DmaData` `:599` → `BufferCache::CopyBuffer` (`cache/bufferCache.cpp:1771`), `FillBuffer` (`:1732`) | GPU-копия, если диапазон GPU-грязный |
| WAIT_REG_MEM | `pm4Handlers.cpp:2606` → `graphicsRun.cpp:519`, чтение `*addr` `:530` | GPU-грязная страница → отказ → `ReadMemoryOnGpu` (синхронный слив) на GuestGpu |
| COND_EXEC, предикация | `pm4Handlers.cpp:1510/1544`; `graphicsRun.cpp:2954`, `:2970` | чтение CPU, тот же путь отказа |
| dispatch | `graphicsRun.cpp:3224` → `RenderExecutor::DispatchDirect` (`renderCompute.cpp:258`) **[П]** | отдельный вход, не задевается |

## 4. Запись GPU в память гостя и чтение её гостем

* **Буферы.** Единственная отметка записи: `BufferCache::ObtainBuffer(..., is_written)` → `bufferCache.cpp:1343-1357`
  **[П]** (`m_gpu_modified_ranges.Add`, `GpuDirtyGen::Bump`, `NoteGpuWrite`); её зовёт `NativeStorageBuffer`
  (`pipeline/descriptors.cpp:278`) из `PrepareBindings` для draw (`renderDraw.cpp:2604/2624`) и dispatch
  (`renderCompute.cpp:863`) — вид операции известен только вызывающему. DMA: `FillBuffer`/`CopyBuffer` (dst).
* **Образы.** `Image::MarkGpuModified()` (`renderer/image/image.h:149-159`) **[П]** — семь сайтов: `renderDraw.cpp:824`,
  `cache/textureCache.cpp:861`, `:879`, `:2221`, `:2283`, `:2370`, `:2427` **[П]**. У образов наблюдатели ТОЛЬКО на
  запись: чтение гостем памяти цели рендера НИКОГДА не даёт отказа; содержимое образа попадает в память гостя только через
  `DownloadImageMemory` (`textureCache.cpp:2829-2919`) — вытеснение GC (`:3410-3431`), `readback_linear_images`
  (умолчание false) или `SynchronizeBufferFromImage` (`bufferCache.cpp:2763`).
* **Чтение гостем GPU-грязной страницы.** Аппаратный отказ → `RenderContext::HandleFault` (`renderContext.cpp:187-195`)
  → `BufferCache::ReadMemory` (`bufferCache.cpp:461-518`) **[П]**: на потоке гостя (умолчание `KYTY_STALE_READ`)
  страница открывается сразу (`MarkRegionAsStaleReadable`), а `ServeStaleRead` (`:2137`) выполняется на GuestGpu
  асинхронно; на GuestGpu (чтения CP) — синхронно `ReadMemoryOnGpu` (`:520`). После первого отказа страница читается без
  отказов до новой записи GPU — единица переписи «пара (страница, эпоха записи GPU), прочитанная гостем».
  Упреждающие загрузки `PrefetchHotReadbacks` (`:2555`; вызовы `graphicsRun.cpp:1018`, `:1058`) делают страницу чистой
  ДО чтения — такие чтения отказа не дают вовсе.
* **`hr_*` — НЕ путь чтения.** `hr_free/gpuw/forced/sync` (`common/frameStats.h:1343-1350`) считаются только в
  `WaitPendingHostReads` (`bufferCache.cpp:1660-1730`): это ЗАПИСЬ CPU, ждущая незавершённое чтение GPU импортированной
  памяти. В проекте они только печатаются.

## 5. Отложенные очистки (риск картинки, не зависона)

Очистки DCC/CMASK/HTILE ставит compute (`renderCompute.cpp:98`, `:240`; `bufferCache.cpp:1758`) — он исполняется и в
пропущенном кадре; потребляют их только привязки draw: `PrepareDccClear`/`PrepareCmaskClear` (`textureCache.cpp:2336-2337`,
`:2225`), HTILE `ClearMeta`/`TouchMeta` (`renderDraw.cpp:1373-1384`), `AdoptPendingDccForTexture`
(`descriptors.cpp:2418`, `:2544`), `MaterializeDeferredDccClear` (`descriptors.cpp:5420`). Очистка кадра N при пропуске
материализуется первым потребителем кадра N+1.

## 6. Ручки и счётчики

* `Knob::Burn` — последняя (`common/gates.h:652`, `Count` `:653`) **[П]**; строка `{"KYTY_BURN","burn",0,899999}` —
  последняя в `KNOB_DEFINITIONS` (`common/gates.cpp:427`). 37 ручек, 113 гейтов.
* Последний счётчик — `BurnCpuBad` (`common/frameStats.h:2210`, `Count` `:2211`); последняя строка таблицы имён
  `FrameTrace-x` — `{"burn_cpu_bad", …}` (`presentation/videoOut.cpp:2808`).
* Ключ `burn`: `Detail::g_burn_frame` (`frameStats.h:2714`), `BurnPublishFrame` (`:2742`) после `Poll` (`videoOut.cpp:1200`).
* `gw_*` (`KYTY_GPU_WALL=1`): `gw_idle` `graphicsRun.cpp:703`, `gw_blk` `:738`, `gw_cmd` `:779`, `gw_proc` `:799`,
  `gw_flip` `videoOut.cpp:3221`.
* `SliceCensus::ImageKey` (`guest_gpu/sliceCensus.h:13-24`) — ключ образа «индекс слота ^ поколение»; сайты с. 118:
  `RebindImages` (`descriptors.cpp:3922-3929`) и `AcquireRenderTargets` (`renderDraw.cpp:1505-1512`).
  `VulkanImage::state_serial` (с. 120) для переписи записи→чтения НЕ годится (движется от барьеров, не от записей).

## 7. Сайты редакции 2 (шаг 2б, `HPP-37`; сверено чтением на HEAD `a29f48d`, дерево `src` = `41effbd`) **[П]**

| что | где | примечание |
|---|---|---|
| вызовы GC | `guest_gpu/graphicsRun.cpp:1010`, `:1031`, `:1056`, `:1066`, `:1074` → `RenderContext::RunGarbageCollector` (`host_gpu/renderer/renderContext.cpp:395-412`) | только поток GuestGpu, в `GuestGpu::Process`; `:1074` — перед `PrepareCpuFlip` |
| GC текстур, удержание `bindfloor` | `cache/textureCache.cpp:3257`; `floor_hold` `:3273`; часы `:3292`; приостановка `:3351-3358` (`bf_gc_hold`) | идиома для `skc_gc_hold` |
| GC буферов, удержание | `cache/bufferCache.cpp:1950`; `floor_hold` `:1958`; `aggressive` `:1967`; приостановка `:1968-1972` (`bf_bgc_hold`) | идиома для `skc_bgc_hold` |
| `BindFloorGcHold` | `pipeline/descriptors.cpp:1006` | объединяется со `skc_hold` через ИЛИ |
| захват цели, быстрый путь | `renderDraw.cpp:795` `AcquireTargetView`; `MarkGpuModified` без проверки записи `:824`; медленный путь `:846` → `FindRenderTarget`/`FindDepthTarget` | охрана захвата `t_skc_acq` на всё тело |
| `MarkGpuModified`/`CommitGpuWrite`, захват | `textureCache.cpp:2221`, `:2261` (`FindTexture` storage), `:2283`, `:2352` (`FindRenderTarget`), `:2370`, `:2399` (`FindDepthTarget`) | НЕ несомненная запись |
| то же, несомненная запись | `:861` `CopyImage`, `:879` `CopyImageMip`, `:975` `ResolveDepthOverlap`, `:2620`, `:2638` `ClearImage`, `:2415` `MarkGpuWritten` (← `depthRenderTarget.cpp:454`, `descriptors.cpp:2894`, `renderDraw.cpp:3742`) | `CommitGpuWrite` `:2418-2428` → `MarkGpuModified` |
| `FindRenderTarget` из `MaterializeBoundTargetDccClears` | `pipeline/descriptors.cpp:2917` | вне `AcquireTargetView`; операция K |
| маска записи цвета | `renderDraw.cpp:533` `render_target_mask_slot(ctx.GetRenderTargetMask(), colors[i].target_slot)` | W1 |
| хвост `AcquireRenderTargets` (перепись `slicecen`) | `renderDraw.cpp:1503-1512`; `AttachmentWriteAspects` `depthRenderTarget.cpp:488` | W1 и чтение вложений |
| MSAA-резолв | `ResolveColorTargets` `renderDraw.cpp:3716`; `MarkGpuWritten(dst)` `:3742` | штампуется W3 |
| чтения CP | WAIT_REG_MEM `graphicsRun.cpp:530`; COND_EXEC `command_processor/pm4Handlers.cpp:1510`, ветвление `compare_addr` `:~1526-1544`; предикация `graphicsRun.cpp:2970`; `count_addr` `:3138`; аргументы `:3063`, `:3085`, `:3156`, `:3177`; `DispatchIndirect` `:3329`; RELEASE_MEM GDS `:3440-3448` | `skc_rc_*`, `skc_r_gds` |
| `PrepareBda` с `uses_dma` | draw `pipeline/descriptors.cpp:~4112-4142`; dispatch `renderCompute.cpp:~869-879` | `skc_x1_dma`, `skc_x0_dma` |
| удержание / показ | `presentation/videoOut.cpp:1173-1187` (`Discard` `:1182`, `present_ns` `:1184-1186`); `count++` `:1194`; `Poll` `:1197`; снимок счётчиков строки `FrameTrace` `:1260`, печать `:1279` | `skc_held`, `skc_held_inc`, `skc_pres_*` в строке того же флипа |
| `FlipHold:` | `videoOut.cpp:2859-2870` — `present_us` только в строке при удержании ≥ 50 мс | отсюда `skc_pres_ns` (В-н1) |
| `m_skipped_draws` | `renderDraw.cpp:2911` (`fetch_add`) | рядом `skc_ap_skip` |
| интервал флипа | `VideoOutSetFlipRate` `videoOut.cpp:2939-2956` (`\trate = <n>` под `PRINT_NAME`); `flip_rate = 0` при открытии `:711`; `IsFlipDueLocked` `:491-498` | В-н2 |
