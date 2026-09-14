# Карта горячего пути CPU (Sky Garden, ~5500 draw на кадр)

Собрано в сессии 51 из чтения кода и счётчиков сессий 48–51, дополнено измерениями сессий 52 и 53.
Цель документа — не искать это заново: где именно уходит CPU на кадр и какие кэши/эпохи уже есть
в дереве.

**Сессия 59 — что изменилось в карте:**

- **B9 в единицах CPU — 0,45 мкс на пуловый набор** (построение списка записей 0,21 + commit и
  копия пакета 0,34 по таймерам с инфляцией; переходы образов 0,39 отдельно). Повторяющихся
  наборов 1 451 на кадр → потолок 0,3–0,45 мс, 1–1,4 % потока: с `recpack` сами записи
  дескрипторов уже не на критическом потоке. Закрыт.
- **Захват целей стоил ≈4 % потока на неизменных целях**: замок `TextureCache::m_lock` в
  `FindRenderTarget`/`FindDepthTarget` (по 0,9–1,0 %), резолверы с копией `RenderColorInfo`/
  `RenderDepthInfo` (~2,7 КБ на draw). Гейт `rtfast` (по умолчанию 1) держит записанный view по
  `bind_stamp`, backing, view info, метаданным desc и новой **эпохе метаданных
  `TextureCache::MetaEpoch()`** (двигают все 13 мутаций `m_surface_metas`); 99 % захватов в Sky
  Garden идут по записи, выигрыш −0,75…−1,81 %.
- **Обход PM4 для M1 нельзя делать сильно заранее.** Вынесенный на свой поток при отправке гостем
  (`dawalk`) он опережает GuestGpu на глубину очереди (~2 отправки, ~1 мс лага), и в Sky Garden
  это +4…5 %: `da_take_us` 3,0 → 4,0 мс (свидетель и снимок остывают к взятию), `da_busy` ×10
  (два кадра запросов в таблице слотов), `da_miss` ×2, плюс контенция `PipelineCache::m_mutex` с
  compute-prefetch (287 dispatch'ей на кадр). Пустыня этого не показывает (глубина очереди мала,
  там −3…−5 %). Ручка `dawalklead` (обход не дальше N отправок вперёд) ждёт замера в сцене.
- **Разрешение привязок — ≈20 % потока, не больше** (`PrepareBindings` 6,0, `RebindImages` 1,7,
  `RebindBuffers` 1,3, `FindBuffer` 1,3, `ObtainBuffer` 1,2, `TouchImage` 0,9, `FindImagesInRegion`
  0,8, `HasGpuDirtyBytes` 1,0, `SynchronizeBuffer` 1,4, доли спин-лока и `TryReadBacking`) — это
  весь потолок M2, при КПД M1 ≈3 мс.
- `ShaderParams::user_data` — inline-буфер (B5), `ShaderVertexInputInfo::Reset()` чистит только
  использованный префикс (B1d), лог-счётчики цикла атрибутов читаются до `xadd` (B7) — всё в
  `graphics/shader/**`, подпись кэша трансляции сменилась.

**Сессия 58 — что изменилось в карте:**

- **`VirtualProtect` на пути BDA — статья с малым потолком.** В Sky Garden проход
  `SynchronizeBuffersOfDirtyRanges` делает всего **~123 вызова `VirtualProtect` на кадр, и 58 % из
  них уже сливаются вплотную** (счётчики потолка `protbatch2`, снятые при выключенном гейте). На
  пустыне слить можно 46 % вызовов (33 % вплотную, 13 % через чистую дырку) — но там этой статьи
  почти нет. Значит доля `VirtualProtect` в 6 % профиля набирается **не здесь**, а на пути
  write-fault'ов и вооружения страниц; пакетирование прохода dirty-range измерено в шуме и
  выключено (`protbatch2` = 0).
- **Копия `ResourceSnapshot` стоит около 0,3 мс на кадр** — это весь потолок `snapkeep`. Из 8,8 МБ
  копий снимка на кадр **53 % байт уже лежат у приёмника** (при этом равны 98,7 % векторов: меняются
  самые большие), а **99 % копий приходятся на последнее использование слота** `drawahead`. Снятие
  обоих (`snapdiff` + `snapswap`, оба по умолчанию 1) роняет трафик 8,8 → 0,16 МБ на кадр и даёт
  ровно **−0,7…−1,7 % CPU на draw** — столько и стоила копия.
- **Memo запроса буфера возможно, но само по себе не окупается.** Потоко-локальное memo
  `ObtainBuffer` с ключом `(vaddr, size)` и свидетелем `RangeWriteEpoch` + `m_registration_epoch`
  даёт **47 % попаданий** (17 тыс. на кадр при ~19 тыс. промахов), но в Sky Garden измерено в шуме
  (`buffast` = 0). Ценность его другая: E1 сессии 57 показал, что медленный путь `ObtainBuffer` шёл
  на **каждом** draw — это был блокер M2, и он снят. Включать вместе с M2.
- **Живость гостевого таймлайна зависела от бухгалтерии пула копий.** Единственное GPU-ожидание на
  нём — `AddWait(m_copy_semaphore, AsyncCopySequence())` в `commandScheduler.cpp:742`. Батч, чей
  запрос не пережил учёт `m_requests`/`m_signaled`, ждал значение, которое пул больше не посылал;
  очередь одна на оба планировщика, поэтому за ним вставало всё, включая present'ы, и через
  ~240–280 кадров сцена умирала через `GpuWaitSlow` → `GpuHangAbort` → `ErrorDeviceLost`. На
  пустыне это не воспроизводилось никогда: её харнесс жёстко ставит `KYTY_ASYNC_COPY_GPU_WAIT=0`, и
  семафор не создаётся. Лечение — `CopyPool::SignalIdle()` (гейт `acopyidle`, по умолчанию 1):
  опустевший пул публикует завершившийся префикс `m_completed` безусловно; префикс только растёт,
  поэтому отпустить батч рано нельзя, цена — один лишний `vkSignalSemaphore` на осушение пула.
  Диагностика: `acopy=<поставлено>/<завершено>/<просигналено> acopy_pending=` в `GpuWaitSlow:`.
- **Потолок B9 железом не режется.** `maxDescriptorSetStorageBuffersDynamic` = **16**,
  `maxDescriptorSetUniformBuffersDynamic` = 15 (RTX 5080 Laptop, драйвер 616.56). В Sky Garden
  наборов на кадр 2 733, повторяют предыдущий набор своего layout'а **1 451 (53 %)**, и **все они
  укладываются в бюджет устройства** (`e9_dyn_over` = 0), хотя 1 446 требуют больше 8 динамических
  смещений. Препятствие не в лимите, а в том, что **половина наборов кадра идёт через push
  descriptors, а `ePushDescriptorKHR` несовместим с dynamic-типами** — решение per-pipeline; плюс
  пул `DescriptorHeap::CreatePool` без dynamic-типов (иначе `ErrorOutOfPoolMemory`), порядок
  `pDynamicOffsets` по возрастанию биндинга при неотсортированном
  `program.bindings.descriptors`, и два места привязки (`descriptors.cpp`, `commandRecorder.cpp`).

**Сессия 57 — что изменилось в карте:**

- **Write-fault'ы гостя были главным последовательным налогом Sky Garden**: 8,3 тыс. на кадр, 41 %
  из них — повторы той же страницы в том же кадре (`stk_flt_same`). Каждый стоил `VirtualProtect` на
  4 КиБ, захват `ApplyGuard` и инвалидацию; ожидание `ApplyGuard` по всем потокам — 59–61 мс на кадр.
  Окно 64 КиБ (`faultkb`) свело это к 1,25 тыс. fault'ов и 8–11 мс ожиданий. Страницы, перевзводимые
  заливками и тут же пишущиеся снова, почти не встречаются (`stk_arm_hot` 164 из 4 978), поэтому
  «липкие» страницы бесполезны.
- **`CommandRecorder::EndRecord` дорог из-за `lock xchg`** (`m_head.store(seq_cst)`) на кэш-линии, которую
  спинящий поток записи непрерывно читает, а не из-за мьютекса; поток записи не был привязан к CCD
  GuestGpu (`rec_ccd_x` 7 из 7 проверок).
- **Медленный путь `ObtainBuffer` идёт на каждом draw** (E1, бит `BufSlow`), быстрого пути «попадание
  memo/эпохи» у буферов нет — это первый блокер M2.
- **Половина descriptor set'ов повторяет предыдущий набор своего layout'а** (E9), но смещения в
  stream-ring разные всегда — B9 требует dynamic offsets.
- **`DrawRenderState` больше не обнуляется на каждый draw** (`drawstate`), ёмкость снимков SRT
  переиспользуется (`snapkeep`) — взамен `ResourceSnapshot::operator=` 2,5 % семплов.

**Разведка перед переписыванием плана (конец сессии 56) — что нашлось в горячем пути:**

- **Самая дорогая статья кадра — не привязки и не запись команд, а `PrepareBda` →
  `SynchronizeBuffer`: 7,1 мс на кадр (14,5 %), и её платят 177 draw'ов из 5100** (`bda_n`=177,
  ~40 мкс на вызов). Состав: `VirtualProtect` 2,5 мс (382 вызова с потока GuestGpu × 6,9 мкс — это
  TLB-shootdown в процессе с 30+ потоками, не сам системный вызов), ожидание `ApplyGuard` 2,1 мс,
  остальное — трекер и `memcpy` в staging. По всем потокам ожидание `ApplyGuard` — 52,8 мс на кадр
  длиной 50 мс (8,4 тыс. fault'ов гостя на кадр).
- **~25 КБ обнуления POD на каждый draw ≈ 130 МБ на кадр:** `DrawRenderState state {}`
  (`renderDraw.cpp:2002`, ~15,5 КБ — внутри `ImageDesc` по значению у восьми целей) и `info = {}` в
  `PrepareProgram` (`shader.cpp:694`, ~9,9 КБ, из них `ShaderVertexInputBuffer buffers[32]` =
  8 960 Б, `shaderBindings.h:176-186`). Это основная часть 4,9–9,5 % VCRUNTIME в профиле.
- **`TextureBinding` ≈ 640 Б (внутри `ImageDesc` ≈ 584 Б, из них `mip_layout[16]` = 384 Б)
  копируется дважды на каждую привязку** — ~65 МБ на кадр (`descriptors.h:21-31`,
  `descriptors.cpp:1211`).
- **`TouchImage` вызывается 212 тыс. раз на кадр (42 на draw)** и даже при `texlru=1`, когда
  перестановка узла LRU пропускается, безусловно пишет `frame_accessed_last` в общий `Image`
  (`textureCache.cpp:475-493`). Сейчас почти бесплатно, при нескольких потоках — готовый генератор
  false sharing.
- **`GetShaderParams` аллоцирует `std::vector<uint32_t>` под user data на каждую стадию каждого
  draw** (`shader.cpp:242-258`) — ~10,5 тыс. пар new/delete на кадр.
- **Хэш `ProgramKey` намеренно не хэширует `static_state`** (`pipelineCache.cpp:1144-1157`), поэтому
  все статические варианты шейдера лежат в одном бакете и сравниваются поэлементно до 429 слов.
- **Свидетель M1 — это 53 слова на взятие** (`da_words/da_hit`), то есть проверка перечитывает ровно
  те же слова гостя, что и материализация, только без обхода графа. Отсюда КПД передачи M1 ≈45 %:
  воркеры жгут 19 мс CPU, чтобы снять с критического потока 9,2 мс, чистый выигрыш 4,1 мс.
- **Инструментация в режиме `lite` стоит 1,8 мс на кадр (3,7 %)**: `FrameStats::Add` вызывается
  ~250 раз на draw, в том числе на **каждое** прочитанное слово гостя (`pipelineCache.cpp:397-400`,
  440 тыс. раз на кадр). Все A/B сессий 51–56 платили это в каждой фазе.
- **Структуры не готовы к нескольким потокам разрешения:** `BufferCache` не имеет лока вообще
  (`std::map m_buffers`, `m_page_table`, LRU), `DescriptorHeap` — ни локов, ни атомиков,
  `StreamBuffer::m_offset` без атомиков, `ProgramCache::lookup_key` — член класса, а не локальная
  переменная (`pipelineCache.cpp:2139`), `RenderExecutor` — `friend` кэша текстур и лезет в `Image`
  мимо `m_lock` (включая `Image::Transit`, мутирующий `std::vector`), `FindImagesInRegion` объявлена
  `const`, но мутирует `mutable` эпоху запроса. Отдельно: `Buffer::upload_epoch/_kind/_begin/_end`
  пишутся четырьмя присваиваниями — два потока соберут интервал, который никто не заливал, и это не
  падение, а старые байты в шейдере.
- **`GetWriteWatch` вместо ручной защиты страниц невозможен:** гостевая память — view файлового
  отображения с placeholder'ами (`memoryAddressSpace.inc:47-49, 661-663, 1246-1248`), а
  `MEM_WRITE_WATCH` работает только с приватной памятью `VirtualAlloc`; плюс у write-watch нет
  аналога read-watch, который нужен для GPU-грязных страниц.
- **Последовательный остаток измерен: 21,4 мс из 48,8** (44 % времени потока пишет разделяемое
  состояние). Подробности и арифметика — `docs/parallel-draw-path.md` §2.

**Сессия 56 — что изменилось в карте:**

- **Размещение потоков важнее половины правок этой карты.** Поток GuestGpu и воркеры `DrawAhead`
  должны быть на одной L3-группе (ручка `dapin`, по умолчанию 1): иначе снимок, построенный
  воркером, читается из кэша другого CCD, и первые касания его векторов в `PrepareBindings`,
  `FindBuffers`, `ResolveTexture`, `StreamBuffer::Copy`, `~ResourceSnapshot` дают ≈5 % времени
  потока. Именно это делало Sky Garden «двухрежимным» (50 или 65 мс CPU при одном числе draw).
- **Доли в профилях сессий 54–55 завышены примерно вдвое:** дамп семплера печатал только 400 строк,
  а ключ включает цепочку вызовов, так что в дамп попадала половина семплов, и скрипт делил на неё.
  Исправлено в сессии 56 (печатаются все строки).
- **`PlanFingerprint` не канонический** (`IR::Value` хранит immediate в union, запись сохраняет все
  64 бита): статические варианты одной программы получают разные отпечатки при одном плане.
  Канонический класс — `CanonicalPlanBytes` в `pipelineCache.cpp` (гейт `daclass`).
- **Пул дескрипторов ключуется хэндлом layout'а**, а layout создаётся свой на каждый пайплайн
  (`shaders.cpp`, дедупликации нет): свежий пул вмещает ровно `dspool/dsbatch` = 32 layout'а, а
  переиспользованный сбрасывается целиком первым же layout'ом, которого в нём нет. Отсюда ~250
  `vkAllocateDescriptorSets` на кадр в Sky Garden при ~4000 нужных наборов. Заменено кольцом наборов
  на layout с тиком на каждый набор (гейт `dsring`, по умолчанию 1).
- **Запись Vulkan-команд — не более 7,3 % времени потока** (весь `nvoglv64` в профиле). M3 шаги 1–2
  (`recpack`) снимают часть этого: `rec_direct` 5468 → ~1000 на кадр, −1,5 % в Sky Garden, −5 % на
  пустыне. Не путать с `d_commit`/`d_emit` из таймеров — там ещё и разрешение, и инфляция таймеров.
- **Путь fault'а гостя стал дешевле:** `texfaulthint` (счётчик образов на страницу) пропускает
  `TextureCache::m_lock`, когда на странице нет образов (в Sky Garden это ~98 % инвалидаций),
  `protbatch` выносит `VirtualProtect` из-под спин-локов трекера, `syncfree` отвечает на чистый
  диапазон без захвата. Спин-лок трекера 8,5 % → 2,3 % семплов.
- **Осторожно:** `protbatch` принёс собственную статью — `ApplyGuard` 4,2 % семплов (замок
  применения защиты берётся на каждом изменении, в том числе при выключенном гейте), а `recpack` —
  `CommandRecorder::EndRecord` 4,8 % (пробуждение потребителя под мьютексом на каждую запись).
- **Профиль потока GuestGpu после сессии 56** (Sky Garden, ~5300 draw, CPU 47 мс, всё включено):
  `VirtualProtect` 5,8 %, `EndRecord` 4,8 %, `ApplyGuard` 4,2 %, `ResolveTexture` 4,1 %,
  `ExecutePreparedDraw` 3,3 %, `TryReadBacking` 2,9 %, `VerifyWitness` 2,9 %, `CommitBindings` 2,6 %,
  спин-лок трекера 2,3 %, `PrepareBindings` 2,2 %, драйвер 2,8 %.

**Сессия 55 — что изменилось в карте:**

- **`Image::FindView` (`imageView.cpp`) больше не всегда перебирает список** — образ помнит индекс
  view, ответившего в прошлый раз (`Image::view_hint`). Чистый кэш, без гейта.
- **Безлоковые чтения битовых карт трекера** (`MemoryTracker::IsRegionGpuModifiedFast`,
  `IsRegionCpuModifiedAndGpuCleanFast`, `BitArray::AnyInRangeRelaxed`, `RegionManager::IsModifiedRelaxed`;
  гейт `trackfree`, по умолчанию 0). Обоснование, которое надо беречь: **GPU-грязные биты ставит
  только `ForEachUploadRange(is_written=true)` из `SynchronizeBuffer`, снимают
  `UnmarkRegionAsGpuModified` и `ForEachDownloadRange<true>` — все с потока GuestGpu**; CPU-грязные
  биты ставятся с гостевых потоков через `ChangeState<Cpu,true>`, и эта запись идёт через
  `BitArray::SetRangeRelaxed` (`std::atomic_ref`), иначе безлоковое чтение было бы гонкой. Обёртки
  `BufferCache::IsRegion*FromGpu` сами уходят на залоченный путь с любого другого потока.
- **`AddressSpace::ProtectTransient` получил быстрый путь** (гейт `protfast`, по умолчанию 0):
  потоко-локальный memo последней подтверждённой `MappedRegion` со свидетелем-эпохой карты гостя.
  `GuestAddressSpace::m_mutex` стал `std::shared_mutex`; быстрый путь держит его **shared** — снимается
  обход `std::map` и сериализация защит между собой, но не исключение против map/unmap.
- **Shader-write барьер может не рвать проход** (гейт `swlocal`): при
  `VK_KHR_dynamic_rendering_local_read` он пишется внутри прохода как by-region fragment→fragment,
  а широкий барьер платится в `CommandBuffer::EndRendering`. Порядок закрытий прохода внутри
  OIT-draw: `GDS-барьер → Transit → BeginRendering → draw → shader-write барьер`, и `FrameTrace-rp`
  заряжает первого — поэтому `end_gds=0` в профиле Sky Garden не означает, что GDS-барьера нет.
- **Стоимость дескрипторов измерима только в Sky Garden**: на пустыне `ds_alloc=0` (755 draw
  укладываются в удержанные наборы пула), в Sky Garden `DescriptorHeap::Allocate` — 2,1 % семплов,
  целиком внутри драйвера. Ручки `dsbatch` / `dspool`.
- **GPU Sky Garden (из `GpuTime` сессии 53):** 11,4 мс работы + 7,2 мс простоя между отправками
  внутри кадра; draw 6,5 мс, dispatch 3,4 мс, загрузки образов 0,46 мс, барьеры 0,6 мс.

**Измерено в сессии 54 в Sky Garden (все правки сессии включены, ~4750 draw, CPU 50,6 мс/кадр,
семплер потока GuestGpu, упор в CPU):** `TrackingSpinLock::lock` 14,3 % (`ObtainBuffer` →
`IsRegionCpuModifiedAndGpuClean` 3,6 %, `PrepareBda` → `SynchronizeBuffer` 2,1 %, `FindTexture` 1,8 %,
`IsRegionGpuModified` 1,3 %, `FindRenderTarget` 1,0 %); M1 — `VerifyWitness` 9,8 %, `QueueAheadSource`
4,6 %, `QueueAhead` 4,4 %, `AheadTake` 2,9 % (итого 21,7 %, выигрыша M1 здесь нет); `ProtectMappedUnlocked`
6,4 % (`SynchronizeBuffer` → `PageManager::UpdatePageWatchers`); привязки ≈21 % (`ResolveTexture` 5,3,
`CommitBindings` 4,4, `PrepareBindings` 4,4, `FindBuffers` 3,3, `DescriptorHeap::Allocate` 2,1,
`StreamBuffer::Copy` 1,7); листья драйвера `nvoglv64` 7,1 %. Разрывы прохода: 931 на кадр, 768 —
shader-write барьер, 766 из них перезапускаются на тех же целях.

**Измерено в сессии 54 (игровая пустыня, 755 draw, семплер потока GuestGpu):**

- **`vkQueueSubmit` был 9,9 % всех семплов (17 % работы потока)** — в драйвере; вынесен на отдельный
  поток (`asyncsubmit`), осталось 0,7 %. На пустыне 28 отправок на кадр, в Sky Garden ~43.
- **Пересоздание образов при переинтерпретации одной поверхности** (цвет ↔ D32 ↔ R32F, 5 раз за
  кадр; `ResolveDepthOverlap`/`ResolveOverlap`, `textureCache.cpp`): `vmaCreateImage` →
  `AllocateDedicatedMemory` 4,1 % + `BindImageMemory` до 1,6 %; `InsertImage` 520 мкс/кадр. Снято
  пулом переиспользования `VkImage` (`imgrecycle`, `vma.cpp`). Частота — от `safe_to_delete`,
  который сравнивает тики (43 на кадр) с порогом `NumFramesBeforeRemoval = 32`.
- **M1 (материализация на воркерах)**: проверка результата `VerifyWitness` 2,5 %, постановка задач
  `QueueAheadSource`+`QueueAhead` 2,6 %, `AheadTake` 0,7 % — это теперь крупнейший остаток, при
  материализации ≈1 мкс на стадию.
- Остальное после правок: `TrackingSpinLock::lock` 3,7 %, `ProtectMappedUnlocked` 2,9 % (синхронный
  `VirtualProtect` из `BufferCache::SynchronizeBuffer` → `PageManager`), привязки ≈6,3 %,
  `BufferCache::CopyBuffer` (DMA) 2,0 %; ожидание flip 57,4 %.
- В Sky Garden разрывы прохода — OIT (15 пиксельных шейдеров linked list), см.
  `docs/parallel-draw-path.md` §6.2; причины закрытия прохода теперь считает `FrameTrace-rp`.

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
