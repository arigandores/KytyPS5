# Сайты режимов 2′ и 3 ручки `skipceil` (проект `design124.md`, редакции 1–2; §9 — rev 2)

Автор — Probe Designer (`HPP-56`). Строки — на дереве `src` коммита `bb45007` (HEAD `61b35b6`), сверены чтением. Поток:
G — GuestGpu (`SkipCeil::t_gpu`), H — поток гостя. «С. 123» — сайт уже существует (переписи с. 123), режим 3 его
расширяет; «новый» — сайта нет.

## 1. Ручка и защёлка

| что | файл:строка | поток | режим 3 |
|---|---|---|---|
| строка ручки | `common/gates.cpp:430` | — | диапазон `0, 2` → `0, 3` |
| enum | `common/gates.h:658` | — | комментарий |
| защёлка, отказ, счёт кадров | `guest_gpu/graphicsRun.cpp:3820-3903` (`SkipCeilFlipBoundary`) | G | `min(mode, 2)` → `3` (`:3865`); эпоха при входе в 2 или 3 из прочих (`:3867-3872`); `t_w3` (`:3884`) и `skc_c_f`/`skc_c_df` (`:3896-3902`) при `>= 2`; **новое:** финализация открытых помеченных кадров, если кончается непомеченный кадр (§3.8), калибровка пауз (§5.3), сброс `t_lod_dtouch` |
| вызовы границы | `graphicsRun.cpp:4016`, `:4041`, `:4073`, `:4095` | G | без изменений |

## 2. Режим 2′

| что | файл:строка | поток | правка |
|---|---|---|---|
| `NoteLodTouch` | `common/frameStats.h:2914-2921` | G (эстафета — `g_lod_anchor_x`) | первым оператором ветки `t_gpu`: `t_mode >= 2 && t_skip && t_kind == KindD` → `t_lod_dtouch = true`, `skc_lod_dkeep` +1, возврат без сдвига якоря |
| вызов | `host_gpu/renderer/pipeline/descriptors.cpp:2184-2186` (`ResolveTextureWith`) | G | без изменений |

## 3. Узлы (операции)

| что | файл:строка | поток | режим 3 |
|---|---|---|---|
| `OpBegin`/`OpEnd` | `host_gpu/renderer/cache/textureCache.cpp:3642`, `:3665` | G | узел кадра N; конец окна D — первый оператор `OpEnd` |
| draw: `OpScope` K→D | `host_gpu/renderer/renderDraw.cpp:3476` (`DrawIndex`), `:3679` (`DrawAuto`) | G | с. 123 |
| сайт пропуска `SkipSiteD` | `renderDraw.cpp:3523`, `:3726`; тело `textureCache.cpp:3713` | G | начало окна D — последний оператор `SkipSiteD` |
| dispatch: `OpScope(KindCS)` | `host_gpu/renderer/renderCompute.cpp:291` | G | с. 123 |
| DMA | `host_gpu/renderer/cache/bufferCache.cpp:1738` (`FillBuffer`), `:1780` (`CopyBuffer`) | G | **новое:** `OpScope(KindM)` при `t_mode == 3`, если снаружи нет операции (В6) |

## 4. Записи

| класс | файл:строка | поток |
|---|---|---|
| W1 вложения | `renderDraw.cpp:1519-1529` (хвост `AcquireRenderTargets`) | G |
| W2 очередь → применение | `renderDraw.cpp:2849` (draw), `renderCompute.cpp:953` (dispatch); `ApplyW2` `textureCache.cpp:3874` | G |
| W3 `MarkGpuModified` | `host_gpu/renderer/image/image.h:157` → `SkcStampW3` `textureCache.cpp:3627`; охрана захвата `renderDraw.cpp:801`, `textureCache.cpp:2235`, `:2276` | G (чужой поток — `skc_w_xthr`) |
| перенос П3 | `textureCache.cpp:863`, `:884`, `:983` | G |
| загрузка образа [Н5] | `textureCache.cpp:1367` (`SkcCensus::Upload`, тело `:3912`) | G |
| M: заливка, копия dst | `bufferCache.cpp:1765`, `:1819` | G |
| запись CPU гостя | `bufferCache.cpp:445` (`InvalidateMemory`), `:455` (`InvalidateWriteFault`) → `SkcEraseCpu` `:3174-3190` | H → команда на G; **новое:** список ожидающих стираний (§3.5) |
| выгрузка образа в память | `DownloadImageMemory` `textureCache.cpp:2845`, сайт `:2856` | G |

## 5. Чтения (рёбра узлов N и посевы next)

| чтение | файл:строка | поток |
|---|---|---|
| образы привязок | `descriptors.cpp:4108-4117` (конец `RebindImages`) | G |
| буферный слот (п. 33(а)) | `descriptors.cpp:218` (вход `NativeStorageBuffer`, `:152`) | G |
| вершины (слитые диапазоны, без щелей) / индексы | `renderDraw.cpp:1810` / `:2125` | G |
| аргументы косвенных | `renderDraw.cpp:2903`, `renderCompute.cpp:925` | G |
| источник `DepthStencilCopy` | `host_gpu/renderer/depthRenderTarget.cpp:457` | G |
| источник копий П3 | `textureCache.cpp:863`, `:884`, `:983` | G |
| источник загрузки образа | `textureCache.cpp:1367` (`image.SourceRange()`) | G |
| **вложение по состоянию** (новое) | статические параметры пайплайна draw: `blend_enable` `host_gpu/renderer/pipeline/pipelineCache.cpp:5190`, глубина/границы `:5227-5252`; сайт вызова — точка draw, где ключ пайплайна уже построен (выбирает Emu Engineer, строкой отчёта) | G |
| источник DMA | `bufferCache.cpp:1816` | G |
| GDS (доступ draw/dispatch) | `descriptors.cpp:5429-5431` | G |
| проход (номер) | `host_gpu/renderer/context.cpp:335` (`PassBegin`) | G |

## 6. Посевы

| класс | файл:строка | поток | окно |
|---|---|---|---|
| cpu | `ServeStaleRead` `bufferCache.cpp:2167` (сейчас `SkcNoteRead(1, окно 512 КиБ)` `:2188`); `BeginAsyncReadback` `:2082` (`:2097`) | G | **`(vaddr, size)` аргументов** (из `ReadMemory` `:463` ← `renderContext.cpp:195`, `fault_vaddr`/`fault_size`) |
| cpu-g | `ReadMemoryOnGpu` `bufferCache.cpp:522` (`:524-526`) | G | `(vaddr, size)` |
| cp | `graphicsRun.cpp:530` (WAIT_REG_MEM), `command_processor/pm4Handlers.cpp:1523` (COND_EXEC), `:1558` (ветвление), `graphicsRun.cpp:2974` (предикация), `:3068`, `:3091`, `:3164`, `:3186` (аргументы CPU-пути), `:3145` (счётчик), `:3339` (`DispatchIndirect`); вход `CommandProcessor::SkcCpRead` `commandProcessor.h:123`, `SkcCpReadSlow` `graphicsRun.cpp:3905` | G | адрес × размер |
| gds | RELEASE_MEM с GDS `graphicsRun.cpp:3456-3458`; `CopyBuffer` с `src_gds` `bufferCache.cpp:1780` | G | отрезок GDS |
| poll | финализация в `SkipCeilFlipBoundary` | G | кадр |
| flip (непомеченный) / flipx (помеченный — исключение) | `Presenter::PrepareFrame` `presentation/window/swapchain.cpp:748-786` (`frame->CopyFrom` `:784`), вызов `presentation/videoOut.cpp:1042` | G (сверить в шаге 3) | ключи образа показа |
| упреждение (только Lp) | `PrefetchHotReadbacks` `bufferCache.cpp:2589`, сайт `:2635` | G | `(begin, end − begin)` |

## 7. Время

| что | файл:строка | поток |
|---|---|---|
| окно D | конец `SkipSiteD` (`textureCache.cpp:3713`) → начало `OpEnd` (`:3665`) | G |
| паузы `Skc3Pause` | каждая входная точка `SkcCensus::*` (`textureCache.cpp:3627-3959`), `BufferCache::Skc*` (`bufferCache.cpp:3069-3279`), код графа | G |
| GC помеченного кадра | `RenderContext::RunGarbageCollector` `host_gpu/renderer/renderContext.cpp:395` (вызовы `graphicsRun.cpp:1014`, `:1035`, `:1060`, `:1070`, `:1078`) | G |
| стена `Process` помеченного кадра | обёртка `WallSpan` `gw_proc` `graphicsRun.cpp:803` (вызов `GuestGpu::Process` `:933`) | G |
| калибровка | `SkipCeilFlipBoundary` | G |

## 8. Счётчики

Хвост таблиц: `SkcLodNoanc` `common/frameStats.h:2308`; имя `skc_lod_noanc` `presentation/videoOut.cpp:2936`. Новые — после
них, в порядке §8 проекта.

## 9. Дополнения редакции 2 (`HPP-66`, решения лида п. 43; строки сверены чтением на `bb45007`)

| RC | что | файл:строка | поток | режим 3 |
|---|---|---|---|---|
| RC5(2) | бит poll | `NoteLodTouch` `common/frameStats.h:2914-2921` → флаг `t_lod_ftouch`; копия в запись кадра — `SkipCeilFlipBoundary` `graphicsRun.cpp:3820-3903` до защёлки | G | §2.2, §3.8 |
| RC1 | ленивая запись: загрузка образа | `SkcCensus::Upload` `textureCache.cpp:1367` (тело `:3912-3933`) | G | `Skc3LazyScope` → узел T |
| RC1 | ленивая запись: копии П3 | `textureCache.cpp:863`, `:884`, `:983` (`CarryScope`, `t_carry` глушит W3 `:3636`) | G | то же |
| RC1/RC2 | материализация отложенной очистки | `RenderExecutor::MaterializeDeferredDccClear` `descriptors.cpp:2779`/`:2783`; вызовы `:5466` (`CommitBindings`), `:2956` (`MaterializeBoundTargetDccClears`) | G | не событие записи (§3.3.2) |
| RC1 | прочие W3 при разрешении привязки сэмплируемого образа | перечень исполнителя (шаг 3) | G | `Skc3LazyScope` |
| RC2 | `ClearMeta` | `textureCache.cpp:3062-3075` (`clear_mask = UINT32_MAX` `:3072`); вызовы `bufferCache.cpp:1767` (`FillBuffer`), `renderCompute.cpp:98` (`TryConsumeComputeMetaClear` `:67-118`, вызов `:413`), `renderDraw.cpp:1376` (очистка HTILE глубины в `AcquireRenderTargets`) | G | событие логической очистки, кандидаты по адресу метаданных |
| RC2 | `TrackDccFill` | `textureCache.cpp:3077-…` (`clear_mask` `:3103`); вызов `renderCompute.cpp:240` | G | событие при ненулевой маске; `PendingDcc` — отложено |
| RC2 | усыновление `PendingDcc` | `AdoptPendingDccForTexture` `textureCache.cpp:3198`; вызовы `:3192`, `descriptors.cpp:2433`, `:2559` | G | применение отложенного закрытия |
| RC2 | `TouchMeta` | `textureCache.cpp:3239` (вызовы только с `is_clear = false`: `descriptors.cpp:2903`, `renderDraw.cpp:1384`) | G | не событие |
| RC3 | записи CP в память гостя — **стартовый перечень, неполный** | `graphicsRun.cpp:584` (`WriteData`), `:500` (выгрузка const RAM), `:588-598` (`WriteReferenceClock`), `:3429-3432` (`write32`), `:3462` (`Sync::ReadGds` → память), `:3486-3488` (`write64`), `:3578` (часы EOP), `:3780-3790` (дамп окклюзии), `:4036`, `:4068` (метки флипа); `command_processor/pm4Handlers.cpp:1411-1430` (отчёт LOD) | G | закрытие отрезка, `lclosed`; полный перечень — отчёт шага 3 |
| RC4 | сдвиг эпохи `uses_dma` | `SkcCensus::OpEnd` `textureCache.cpp:3665` (после штампов W2 операции); поле `ShaderInfo::uses_dma` только читается | G | §3.3.3 |
| RC11 | `CopyBuffer` с `src_gds` | `bufferCache.cpp:1780` (проверки `:1801-1810`, ветка GDS `:1840`); заливка GDS `m_gds_buffer.Fill` в `FillBuffer` (`:1738-1760`) | G | ребро узла M / посев next; dst GDS — запись M |
| RC13 | пустые D | `renderDraw.cpp:3528-3530` (`DrawHasValidVertexShader`), `:3532-3534` (`ShouldSkipGeShader`); аналог в `DrawAuto` | G | флаг `empty` узла |
| RC14 | окно отказа | `renderContext.cpp:139` (`fault_size = 1`) | G | Lw — страница 4 КиБ |
