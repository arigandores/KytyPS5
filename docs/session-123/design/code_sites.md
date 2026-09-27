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
