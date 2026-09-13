# Карта горячего пути CPU (Sky Garden, ~5500 draw на кадр)

Собрано в сессии 51 из чтения кода и счётчиков сессий 48–51, дополнено измерениями сессий 52 и 53.
Цель документа — не искать это заново: где именно уходит CPU на кадр и какие кэши/эпохи уже есть
в дереве.

**Измерено в сессии 53 — два закрытых вопроса:**

- **Демандный (по достижимости) обход SRT бесполезен.** Опрос `KYTY_SRT_STAT` считает, что
  реально нужно из графа: в Sky Garden нужны **100,0 % узлов-чтений** (475 276 из 475 333) и
  **97,3 % узлов** вообще; недостижимы 2,8 % источников, но их чтения делят с достижимыми.
  Пункт «делать материализацию дешевле через достижимость» из плана сессии 52 закрыт: экономить
  там нечего, дорого само количество чтений (одно чтение на узел, ~435 тыс. на кадр, все нужны).
- **`PrepareBda` сканировал всё подряд из-за глобальной эпохи.** Поранговые эпохи записи
  (`RegionManager::Epoch`, сессия 52) в качестве свидетеля дают **95,9 % пропущенных регионов** в
  игровой сцене: полный обход диапазона зарегистрированных BDA-буферов при каждом draw'е с DMA
  заменён обходом только тех регионов, которые объявили запись CPU (`KYTY_BDA_REGION_STAMPS`).
  **Но по CPU это почти не видно** (−1…−2 % на draw вместе с двумя другими правками сессии):
  `bda_us` = 5,1 мс из профиля с таймерами — завышение самих таймеров, а не реальная доля.

**Измерено в сессии 52 (Sky Garden, прогон `sky4`) — читать до того, как что-то кэшировать:**

- Материализаций на кадр ~8,9 тыс.; **ключ `(ResourcePlan, user_data, shader_base)` уникален
  у 89 % из них** (постоянно повторяются ровно ~970). Memo результата материализации поэтому
  проиграло: −11 % FPS, +12,6 % CPU на draw. Опция `KYTY_SRT_MEMO` осталась, по умолчанию 0.
  Свидетель годности при этом надёжен: доля устаревших записей 0,9 %, расхождений с настоящим
  обходом за весь прогон — 0.
- `srt_miss` ≈ 260 на 423 тыс. чтений (0,06 %): постоянные трансляции страниц SRT работают.
- `clamp_miss` ≈ 25 тыс. на ~50 тыс. привязок буферов: memo `ClampRangeSize` отвечает на половину.
- Быстрый путь `HasCurrentUpload` попадает ~7 тыс. раз из ~50 тыс. `ObtainBuffer` (14 %); перевод
  его на поэпоховые регионы (`KYTY_REGION_EPOCH`) поднял это лишь до ~7,8 тыс. и эффекта по
  CPU/draw не дал.
- **`ProgramCache::Get` резервирует 66 520 байт стека** (`GetGraphicsPrograms` — 66 632). Без LTO
  кадр < 8 КБ, то есть его создаёт межмодульное встраивание; по дизассемблеру ~53 КБ этого кадра
  не адресуются ни одной инструкцией. Вызов этой функции с гостевого потока переполняет его стек:
  так падал вход в уровень, пока просмотр PM4 не перенесли на поток GuestGpu
  (`KYTY_ASYNC_COMPUTE` по умолчанию 2).

Числа — кадр `underwater_aerial_garden` с подробными таймерами (`KYTY_FRAME_TRACE=1`):
CPU потока GuestGpu ~82 мс (без подробных таймеров ~64–65 мс), GPU ~20–23 мс, 5500–6000 draw.
Вложенные фазы не складывать с внешними.

| счётчик | значение | что это |
|---|---:|---|
| `d_prog` | ~20 мс | `RefreshShaders` → `PipelineCache::GetGraphicsPrograms` |
| `p_mat` | ~16 мс | `MaterializeResources` внутри `d_prog` |
| `m_eval` | ~11 мс | обход SRT внутри `p_mat` |
| `p_reads` | ~454 тыс. | чтений памяти гостя за кадр (~82 на draw) |
| `d_bind` | ~27 мс | `PrepareGraphicsBindings` |
| `b_texn` / `b_viewn` | ~53 тыс. | `ResolveTexture` / `FindTexture` за кадр |
| `ob_n` | ~64 тыс. | `BufferCache::ObtainBuffer` за кадр (~11 на draw) |
| `bb_sync` | ~6,4 мс | `SynchronizeBuffer` |
| `d_commit` / `d_emit` | ~6,7 / ~6,6 мс | запись descriptor set и сами vkCmd* |
| `spin_us` | ~41 мс (все потоки) | ожидание `TrackingSpinLock` |
| `faults` | ~4,6 тыс. / ~47 мс | page fault'ы гостя (все потоки) |
| `prot_calls` | ~3,6 тыс. | синхронных `VirtualProtect` |

## 1. Путь одного draw

PM4 → `pm4Handlers.cpp:1660` `CpOpDrawIndex` → `graphicsRun.cpp:1339` `CommandProcessor::DrawIndex`
→ `renderDraw.cpp:1736` `RenderExecutor::DrawIndex`:

- `:1798` `hw_check` (`debug.cpp:854`) — полная проверка регистров на каждый draw, только диагностика.
- `:1840` `PrepareDrawRenderState` → `colorRenderTarget.cpp:96` / `depthRenderTarget.cpp:232`.
- `:1845` `RefreshShaders` → `pipelineCache.cpp:1217` `GetGraphicsPrograms` (`d_prog`).
- `:1860` `ExecutePreparedDraw` (`renderDraw.cpp:1325`):
  `PrepareGraphicsBindings` (`d_bind`) → `AcquireVertexBuffers`/`PrepareIndexBuffer` (`d_vb`) →
  `AcquireRenderTargets` (`d_acq`) → `GetGraphicsPipeline` (`d_pipe`) → `CommitBindings` (`d_commit`)
  → `EmitDrawPrimitives` (`d_emit`).

`PrepareGraphicsBindings` (`descriptors.cpp:1246`): `PrepareBindings` (VS/PS) → `FindBuffers` →
`PrepareBda` (если `uses_dma`) → `RebindBuffers` → `RebindImages`.

## 2. Что кэшируется сейчас и что всё равно выполняется

- **`ProgramCache::Get` (`pipelineCache.cpp:636`)** — ключ `{stage, hash, user_data_count, code_size,
  BuildStageStaticKey(...)}`. Пропускает трансляцию, но **на каждый draw** заново строит вектор
  статического ключа (`shader.cpp:855/905/939`), делает `find` и **всегда** выполняет
  `MaterializeResources` (`:688`).
- **Материализация не имеет memo вообще.** `memo_hit`/`memo_miss` (`SrtWalker.cpp:2274/2314`) считают
  лишь то, что сработал скомпилированный обход вместо интерпретатора; значения guest-памяти не
  кэшируются (`ResourceMaterialization.cpp:309-311`, `SrtWalker.cpp:2123`). Каждый узел
  `Op::MemRead`/`MemReadScalar` (`SrtWalker.cpp:1871-1947`) делает свежее чтение через
  `ReadShaderLiveMemory` (`pipelineCache.cpp:278`) или `ReadShaderGuestMemory` (`:252`).
  Выход материализации (`ResourceSpecialization`) — **ключ поиска пермутации** (`:712-719`),
  поэтому пропустить её нельзя, не заведя memo результата.
- **`EvaluateCompiled` считает все узлы и только потом вычисляет достижимость** (`:2120` против
  `:2139-2179`): чтения для заведомо неактивных источников уже оплачены.
- **Memo текстур** (`descriptors.cpp:713-737`, 4096 слотов, ключ — 8 dword'ов T# + хэш
  `ImageResource`): снимает разбор дескриптора и `FindImage`, но **не** `FindTexture`/`FindView`
  и не привязку. При попадании всё равно идут `ConfigureImageSource`, `TouchImage` (LRU по deque).
- **Memo целей рендера** (`colorRenderTarget.cpp:118`, `depthRenderTarget.cpp:247`).
- **`Image::FindView` (`imageView.cpp:309`)** — линейный перебор списка view'ов, под
  `TextureCache::m_lock` (спин-лок).
- **`DescriptorHeap`** (`descriptorHeap.cpp:44-133`, `KYTY_DESCRIPTOR_REUSE`) переиспользует
  **выделения** set'ов, но `vkUpdateDescriptorSets` выполняется на каждый draw (`descriptors.cpp:1491`).
- **Стабильных offset'ов нет**: `NativeUpload` (`descriptors.cpp:929-937`) кладёт `flattened_srt` и
  `shader_data` в stream-ring по новому смещению каждый draw — это и есть главный блокер
  переиспользования descriptor set между draw'ами.
- `CommandBuffer::GraphicsStateChanged` (`KYTY_DYNAMIC_STATE_CACHE`) — единственное сравнение с
  предыдущим draw; состояния «прошлого draw» в `RenderExecutor` нет, `ResetBindings`
  (`descriptors.cpp:1076`) в конце каждого draw сбрасывает `image.binding`.

## 3. Память гостя и трекер

- `ReadShaderLiveMemory` (`pipelineCache.cpp:278`): счётчик → поиск страницы в `ShaderReadCache` →
  при промахе `TryGetBackingPointer` (`memory.cpp:870` → `memoryAddressSpace.inc:194`), который берёт
  **глобальный `GuestBackingStore::m_mutex`** и делает `upper_bound` по `std::map`. С сессии 51
  живые трансляции живут в потоко-локальной таблице на 4096 записей и сбрасываются по
  `Memory::BackingMapEpoch()`; промахи считает `srt_miss`.
- `ReadShaderGuestMemory` (`:252`) дополнительно спрашивает `IsGpuCleanRange` (`memory.cpp:888`):
  `HasGpuDirtyBytes` + `TextureCache::IsRegionGpuModified` — то есть **спин-лок текстурного кэша на
  страницу**.
- `TryTransferBacking` (`memoryAddressSpace.inc:548`) проходит диапазон **дважды** под тем же
  глобальным мьютексом; через него идут ~9,4 тыс. копий константных банков на кадр
  (`descriptors.cpp:209/240`), `ObtainBuffer` (`bufferCache.cpp:685`), `CopyGuestToStaging` (`:180`).
- `VirtualRanges::ClampRangeSize` (`memory.cpp:422`) — `CRITICAL_SECTION` + бинарный поиск по
  вектору диапазонов; звался на каждую привязку буфера (`descriptors.cpp:1147`). С сессии 51
  отвечает из потоко-локальной таблицы, помеченной эпохой `VirtualRanges`; промахи — `clamp_miss`.
- `RegionManager::lock` (`regionManager.h:195`, спин-лок) берут: `IsRegionCpuModified`,
  `IsRegionGpuModified`, `IsRegionCpuModifiedAndGpuClean`, `CollectCpuModifiedRanges`,
  `MarkRegionAs*`, `UntrackMemory` (держит все регионы сразу), `InvalidateRegion`,
  `ForEachDownloadRange`, `ForEachUploadRange` (**держит лок через `memcpy` гость → staging**).
- Page fault на запись гостя: VEH (`hostException.cpp:385`) → `RenderContext::HandleFault`
  (`renderContext.cpp:63`) с **`fault_size = 1`**, то есть ровно одна страница 4 КиБ на fault:
  `BufferCache::InvalidateMemory` → `MemoryTracker::InvalidateRegion` (спин-лок, эпоха CPU,
  `UpdateProtection`) + `TextureCache::InvalidateMemory` (свой спин-лок, `UntrackImage*`).
  Цепочка локов: `RegionManager::lock` → `PageManager::Region::lock` → `GuestAddressSpace::m_mutex`
  → `VirtualProtect`. Запись гостем 1 МиБ = 256 fault'ов.
- **Отложенная защита страниц (`KYTY_ASYNC_PROTECT`, `pageManager.cpp:389`) доступна только
  текстурному кэшу**; `RegionManager::UpdateProtection` (`regionManager.h:207`) всегда синхронна и
  выполняется под спин-локом региона.

## 4. Эпохи и версии, которые уже есть

| механизм | где | чем полезен |
|---|---|---|
| `MemoryTracker::m_cpu_epoch` | `memoryTracker.h:161`, инкремент в `regionManager.h:135` | единственный глобальный свидетель записи CPU; **меняется тысячи раз за кадр** (page fault'ы), поэтому для memo нужна эпоха на регион |
| `Buffer::upload_epoch` | `streamBuffer.h:77-83` | `ObtainBuffer`/`SynchronizeBuffer` пропускают проверку трекера (`KYTY_BUFFER_UPLOAD_EPOCH`) |
| `BufferCache::m_registration_epoch` | `bufferCache.h:206` | регистрация/снятие буферов |
| `RenderContext::m_mapping_epoch` + `m_bda_*` | `renderContext.h:91-94` | `PrepareBda` пропускает весь скан (`KYTY_BDA_EPOCH_CACHE`) |
| `VirtualRanges::Epoch()` | `memory.cpp` (сессия 51) | memo `ClampRangeSize` |
| `GuestBackingStore::MapEpoch()` | `memoryAddressSpace.inc` (сессия 51) | постоянные трансляции страниц SRT; с сессии 53 — и потоко-локальная таблица страниц перед `Memory::TryReadBacking` (`KYTY_BACKING_PAGES`) |
| `Common::Gates` | `src/common/gates.*` (сессия 51) | A/B опций внутри одного прогона (`KYTY_GATE_FILE`) |
| `RegionManager::Epoch()` | `regionManager.h` (сессия 52) | эпоха записи одного региона 4 МиБ; с сессии 53 — свидетель `MemoryTracker::RegionStamp` инкрементального BDA-скана |
| `MemoryTracker::RangeWriteEpoch` | `memoryTracker.h` (сессия 52) | смешанная эпоха регионов диапазона; 0 — диапазон не отслеживается целиком |

Чего нет: эпохи GPU-dirty состояния текстур, стабильных смещений stream-ring для
`flattened_srt`/`shader_data`. Эпоха на регион трекера появилась в сессии 52, но memo
материализации, ради которого она задумывалась, оказалось бесполезным (см. врезку выше); в
сессии 53 та же эпоха пригодилась как свидетель BDA-скана.

## 5. Спин-лок текстурного кэша на каждую привязку

`TextureCache::m_lock` берётся несколько раз на каждый из ~45 тыс. привязок образов в кадре:
`FindTexture` (`textureCache.cpp:1756`), `ConfigureImageSource` (`:1182`), `AdoptPendingDccForTexture`
(`:2439`) и — до сессии 53 — `IsMetaCleared` **по одному слою** (до 32 захватов на образ) внутри
`MaterializeDeferredDccClear` (`descriptors.cpp:937`). В профиле сессии 50 `TrackingSpinLock`
занимал 12,1 % семплов. Сессия 53 убрала два из этих захватов (`KYTY_META_LOCK`): маска очистки
читается одним запросом `MetaClearMask`, а адопция DCC не вызывается, когда образ уже несёт ровно
эту метаданную. Остальные захваты на месте.
