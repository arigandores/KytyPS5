# F16l — ревью кода F16k (`KYTY_FIX_F5CMU`, `KYTY_DIAG_F5ID`), Red Team

**Вердикт: `PASS_WITH_FIXES` — 4 требуемых изменения (RC1–RC4).**

Все члены «Ревью F16l» п. 492(з) и поправки п. 495(б)(1)–(6), (в) по коду `810909e3` выполнены (таблица §1). Правки RC1–RC3 —
в полях измерения ветви 2 (`wr_after`, `cpu_mod`): без них правило п. 492(д)(2) даёт ложный (Б) «эмулятор не видел записи». RC4 —
в поле `fix` строки `DiagF5Ev:`: `exact_stale` смешивает запись CPU по странице и запись GPU, правило п. 492(е)(4) «сброс настоящий»
по нему не доказывается. Решение кеша при обеих ручках 0 и при `KYTY_FIX_F5CMU=1` вне FCE-захвата не меняется; бинарь `9040a667`
верен по п. 492(з) и как бинарь пары (е) годен, если лид примет RC4 правилом чтения; для тегов (ж) — после RC1–RC3 (новый бинарь) или с
понижением правила (д)(2) пунктом лида.

Вход: критерий — `c0789a34:docs/ROADMAP.md:22758` п. 492 (якорь «492. **Звено F16j трека F (`HPP-582`, лид): F16h (`HPP-580`)»;
+1 — «(а) **Приёмка.** F16h принят и читается»), поправки — `b6858d6d:docs/ROADMAP.md:22786` п. 495 (якорь «495. **Звено F16k трека F»;
+1 — «(а) **Приёмка по п. 492(з)(1)–(6).**»); код — `810909e3` (13 файлов, дифф к `c0789a34`); отчёт — `470c54cf:docs/track-f/f16k.md`;
отзыв F16i — `859d2ed8:docs/track-f/f16i-review.md`. Ссылки этого отчёта — 34 из 34 по якорю и +1 (`f16l/refs_f16l.py`,
вывод `f16l/refs_f16l.txt`, `ALL OK`). Игра не запускалась; сборок и тестовых прогонов нет (серия трека S `HPP-500` шла — команды < 60 с).

## 1. Члены «Ревью F16l» п. 492(з) и поправки п. 495

| Член | Итог | Основание [c кода `810909e3`] |
|---|---|---|
| `=0` байт в байт по обеим ручкам | ✓ | кольцо — только при `ExactRingOn()` (`bufferCache.cpp:2866`, статик `diagF5.cpp:586`); `PendingDccFillStale` с `nullptr` — прежний путь; `F5CmuScope` при `fce=false`/ручке 0 даёт `Probe()` = `nullptr` (`textureCache.cpp:1888`); `m_f5id_stamp_address` ставится только при `On()` (`:3452`), штамп при 0 не исполняется (`:3463`); `DispatchDirect` — пустой `std::optional`; `ClearMeta`, `FindDccSurfaceImage`, `AdoptPendingDccForTexture` — указатели `nullptr`, ветвление ответа прежнее; `--diag-f5-only` 176 строк = `c0789a34` [отчёт F16k §5.2] |
| решение меняется только на FCE-захвате | ✓ | ответ меняет только `exact_decides` (`textureCache.cpp:3511`), его ставит `F5CmuScope` лишь при `fce && FixCmuOn()` (`:1888`); `fce` = `fce_materialize` (`:2592`), `true` передаёт только FCE-скан (`descriptors.cpp:3938`); сайты DCC (`:1894` прежн., `AdoptPendingDccForTexture`) передают пробу с `exact_decides=false`; `FindRenderTarget` доходит до `PrepareCmaskClear` на каждом пути без `EXIT` |
| кольцо пишется только при `=1` любой из двух ручек | ✓ | `ExactRingOn() = FixCmuOn() \|\| DiagF5Id::On()` (`diagF5.cpp:586`); `KYTY_DIAG_F5ID` без `KYTY_DIAG_F5` инертна (п. 495(д)) — кольца нет, это согласовано с (д) |
| нет нового потока доступа и инверсии замков (В-F16h-2) | ✓ | кольцо пишет `NoteGpuWrite` там же, где `m_bucket_write_seq` (`bufferCache.cpp:1739` → `:2866`); читают `PendingDccFillStale` (прежний читатель карты корзин) и FCE-скан `RenderExecutor` (тот же поток, что `FindRenderTarget` FCE); мьютекс `DiagF5Id` — лист: под ним только `EmitLine` (логгер, `g_recent_mutex`); порядки `m_lock` → мьютекс `DiagF5Id` (`PrepareDccClear`, `TrackDccFill`, `StampPendingDccFill`) и контекст `ObtainBuffer` → мьютекс `DiagF5Id`; обратного захвата нет; `F5IdMetaSnap` (`textureCache.cpp:3386`) зовётся без удержания `m_lock` (`descriptors.cpp` до `FindDccSurfaceImage`, `F5IdNoteFceMiss`; `renderCompute.cpp` после штампа) — рекурсии `TrackingSpinLock` нет; `g_present` пишет поток показа, читает поток GPU — атомик |
| `imageInfo.h` и набор подписи не тронуты | ✓ | `git diff --name-only c0789a34 810909e3 -- src/graphics/shader src/graphics/host_gpu/renderer/image/imageInfo.h CMakeLists.txt` — пусто; набор — `810909e3:CMakeLists.txt:156`; `diagF5.h` лишь включает `imageInfo.h` (подпись хэширует файлы, не включения); строка `a54ae4bd03a673fe35ae89bad218132257b11383` в бинаре `9040a667` — 1 раз |
| новые имена — последними строками таблиц `DiagF5` | ✓ | `F5CmuKept` … `CmaskRtBucketOnly` перед `Count`; `F5Names` — те же 7 последними (`diagF5.cpp:211`), `static_assert` размера; таблица `DiagF5Id` — новая, своя |
| поля `fix`/`why` исполняют RC3–RC4 F16i | ✓ (с RC4 ниже) | RC3: `kept` против `kept_applied` (очищен ≥ 1 слой в том же вызове), `why` — причина возврата без `ClearImage` в порядке возвратов, счётчики `f5cmu_kept_applied` ≤ `f5cmu_kept`, поле `applied`; RC4 F16i: `fix=fallback` и `f5cmu_fallback` |
| тождества п. 492(г)(4) (с поправкой п. 495(б)(4)) | ✓ | `id_fce`: каждый путь «нет образа» ставит причину р1–р7 (р0 недостижим), `NoteFce` — только на ветви `DccFceNoImage`; `id_cs` (`diagF5.cpp:998`): `Emit` и `NoteCsRefusals` идут по одному списку с той же границей `Max`, класс `Tracked` ⇔ адрес = `f5_tracked`; каждый путь `DispatchDirect` после `NoteCsRefusals` вызывает `Class` (`renderCompute.cpp:662` и ветви `MetaClear`/`ImgClear`), `Emit` — сразу, в `After` (`:1262`, `:1289`) или деструктором (`changed=na`); снимок — в начале цикла GPU, окна «родитель есть, детей нет» нет |
| тест-сайт — случаи п. 492(з)(2) и (г)(6) | ✓ | (з)(2): K2 сосед — точная сохраняет, K3 пересекающая — обе, K4 и R4/R7 K + 1 — `fallback`, K5 `kept` (отказ декодирования) против K2 `kept_applied`, K6 захват отрисовки — решение прежнее, `cmask_rt_bucket_only`; (г)(6): р1–р3, р5–р7 через кеш, р4 — чистой функцией; классы S1; `wr_after` D11; `kind` D12–D15 (+`exit`); `stale_apply` S2; счётчики Z/K/D; не гонялись через свои сайты — жизненный цикл `F5IdCsHolder` в `DispatchDirect` и привязка текстуры в `CommitBindings` (отчёт F16k §5.1) — прочитаны здесь по коду, дефекта нет |
| бинарь теста из названного коммита | ✓ | sha256 `C:/kyty/f287/bin/kyty_emulator_9040a667.exe` = `9040a6679261bfc2ec283535b1bd963b1f5ccc92c783a50222ee43c5f20c5d85`; строка версии `KytyPS5-2026-09-15-6a2987a-2226-g810909e3` — 1 раз; установленный — `adb0c82f…` (не тронут) |
| п. 495(б)(1) откат только при `count > K` | ✓ | `bufferCache.cpp:2899` |
| п. 495(б)(2) `since` = max | ✓ | `descriptors.cpp:3883` |
| п. 495(б)(3) пометка `exec` на `PendingDcc` | ✓ | `known` включает `PendingDcc`, `Emit` |
| п. 495(б)(4) `meta_clear` в тождестве | ✓ | `diagF5.cpp:998` |
| п. 495(б)(5) `kind=exit` | ✓ | `ServiceAt(…, true)` из `graphicsRun.cpp` в конце цикла |
| п. 495(б)(6) поле `n=` | ✓ | `FormatCmuEvent`, 1…64 |
| п. 495(в) `fix=fresh` без `PendingDcc` | ✓ допустимо | `F5CmuScope` ставит `Fresh` при `m_decide` до проверки; без ветви `PendingDcc` `Decided()` не зовётся — строка `fresh`, по (в) — «не определено» |

## 2. Требуемые изменения

**RC1. `wr_after=none` не видит записей GPU больше 16 МиБ.**
Что не так: `NoteGpuWrite` для записи > 16 МиБ ставит только `m_large_write_seq` и выходит, не трогая корзин и кольца
(`810909e3:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:2856`, якорь «if (size > (16u << 20)) {»; +1 — «m_large_write_seq = seq;»);
`LastGpuWriteSeqExact` (`:2875`) смотрит только корзины; `wr_after` ветви 2 берёт его ответ
(`810909e3:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3884`, якорь «const auto exact = buffers.LastGpuWriteSeqExact(e.dcc, e.dcc_size, since);»;
+1 — «e.wr_after       = exact.seq != 0    ? DiagF5Id::WrAfter::Exact»). Для решения ветви 1 это не дефект (корзинная проверка тоже
`include_large=false`), для чтения (д)(2) — дефект.
Сценарий отказа: после последней заливки DCC гость привязывает на запись буфер > 16 МиБ, покрывающий `[dcc, dcc + dcc_size)` (пул/куча);
запись `entry` absent, `cpu_mod=0`, `wr_after=none` ⇒ по `c0789a34:docs/ROADMAP.md:22763` (якорь «(д) **Правило чтения тегов `f5id_*`»; +1 —
«(е) **Пара свидетеля ветви 1») ключ — (Б) «эмулятор не видел записи», хотя эмулятор её видел; набор B ветви 2 получает ложную поправку.
Достижимость в игре — [I] (записей > 16 МиБ никто не считал).
Что изменить: в `F5IdNoteFceMiss` при `exact.seq == 0` — если номер последней большой записи > `since` (доступ к `m_large_write_seq`, например
`LastGpuWriteSeq(e.dcc, e.dcc_size, true) > LastGpuWriteSeq(e.dcc, e.dcc_size, false)` и > `since`), писать `wr_after=fallback` (или
новое значение `large`, читаемое как «не определено»); случай — в тест-сайт (запись 16 МиБ + 1 после заливки ⇒ не `none`).

**RC2. `cpu_mod` — «грязно сейчас», а правило читает его как «записи CPU после заливки не было».**
Что не так: `cpu_mod = IsRegionCpuModified(dcc, dcc_size)` (`810909e3:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3888`, якорь
«e.cpu_mod        = buffers.IsRegionCpuModified(e.dcc, e.dcc_size) ? 1 : 0;»; +1 — «}») — текущее состояние грязи; любое приобретение
буфера на чтение выгружает данные и снимает его — так тест F16k сам готовит память
(`810909e3:tests/ShaderRecompilerComputeTests.cpp:10638`, якорь «The test memory was written by the CPU (memset): a read acquisition uploads it»;
+1 — «GPU writes only (a CPU-modified range is stale by both checks).»).
Сценарий отказа: после заливки гость пишет метаданные DCC процессором (F16h: «DMA of the real metadata, or CPU»), затем буфер на этом
диапазоне приобретается на чтение (выгрузка, грязь снята), затем FCE-промах ⇒ `cpu_mod=0`, `wr_after=none` ⇒ (Б) по (д)(2) — ложно.
Что изменить: штамп эпохи записи CPU диапазона при штампе заливки (`MemoryTracker::RangeWriteEpoch`,
`810909e3:src/graphics/host_gpu/memoryTracker.h:35`, якорь «[[nodiscard]] uint64_t RangeWriteEpoch(uint64_t vaddr, uint64_t size) noexcept {»;
+1 — «ValidateRange(vaddr, size);»; рядом с `NoteFillSeq`) и `cpu_mod=1`, если эпоха на событии другая, 0 или заливки не было (эпоха
регионная — грубее, но в сторону «не определено»); либо пунктом лида: `cpu_mod=0` — не довод (Б), (д)(2) для `entry` absent / `clear_mask` = 0
— «не определено». Случай в тест-сайт: запись CPU после заливки + выгрузка чтением ⇒ `cpu_mod=1`.

**RC3. Поздний штамп заливки сдвигает `since` вверх — путь к ложному (Б), признанный автором, без контроля.**
Что не так: `m_f5id_stamp_address` ставит `TrackDccFill` (`810909e3:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3452`, якорь
«m_f5id_stamp_address = address;»; +1 — «m_f5id_stamp_size    = size;»), снимает только `StampPendingDccFill` (`:3463`); между
`TrackDccFill` (`renderCompute.cpp:314`) и штампом (`renderCompute.cpp:1262`, `:1289`) у `DispatchDirect` есть возвраты (`:1035` — нулевая
сетка, `:1096` — `KYTY_BIND_FLOOR_CLEAR`). Отчёт F16k это называет: «`since` больше, `wr_after` может стать `none` вместо `exact` [c кода]»
(`470c54cf:docs/track-f/f16k.md:246`, якорь «- `m_f5id_stamp_address` / `m_f5id_stamp_size`»; +1 — «(`textureCache.cpp:3451`); снимает
`StampPendingDccFill`»); п. 495 этого не разобрал.
Сценарий отказа: диспатч заливки на `X` вернулся до штампа; следующий диспатч привязывает на запись буфер, пересекающий `X`, и штампует `X`
своим номером ⇒ `FillSeq(X)` ≥ номер пересекающей записи ⇒ `wr_after=none` ⇒ (Б) по (д)(2) — ложно. Достижимость путей `:1035`/`:1096` при
заливке на умолчаниях — [I].
Что изменить: счётчик `stamp_late` в сводке `DiagF5Id` (например, `TrackDccFill` застал непустой `m_f5id_stamp_address`, или деструктор
`F5IdCsHolder` видит неснятый штамп) и пункт чтения: (Б) по `wr_after=none` — только при `stamp_late` = 0 на теге; либо снимать штамп на
каждом возврате `DispatchDirect` номером в момент `TrackDccFill`.

**RC4. `fix=exact_stale` смешивает грязь CPU по странице и запись GPU; (е)(4) «сброс настоящий» по нему не доказывается.**
Что не так: при `cpu_written` проба ставит `exact_stale = true` без проверки диапазона
(`810909e3:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3504`, якорь «if (cpu_written) {»; +1 — «f5_probe->exact_stale = true;»);
`IsRegionCpuModified` — по страницам трекера (размер страницы — [I]); строка `stale pending DCC fill ignored … cpu=` печатается только
первые 32 раза на процесс для всех сайтов вместе (на `f5_ef` израсходовано 15 из 32, п. 492(а); на другом прогоне бюджет может кончиться
до события пары — тогда различить нечем). Запись GPU в журнале — диапазон привязки на запись (`ObtainBuffer` → `NoteGpuWrite`, `bufferCache.cpp:1739`), а не записанные
байты.
Сценарий отказа: на FCE-событии `f5cmu_1` страница с CMASK грязна из-за записи CPU соседних байт ⇒ `fix=exact_stale` ⇒ по
`c0789a34:docs/ROADMAP.md:22764` (якорь «(е) **Пара свидетеля ветви 1»; +1 — «(ж) **Теги диагностики:**») п. (4) «сброс настоящий, событие
уходит из ветви 1» — поправка набора B без основания.
Что изменить: `why=cpu` у `exact_stale`, вызванного `cpu_written` (поле `cpu` в `StaleProbe`, `F5CmuScope` пишет `why`), случай в тест-сайт;
и пунктом лида — `exact_stale` читать «записываемая привязка пересекает диапазон заливки» ([c] на уровне привязки, перезапись байт — [I]);
`exact_stale why=cpu` — «не определено». Без правки кода: пара (е) идёт на `9040a667`, а `exact_stale` любого события — «не определено».

## 3. Наблюдения без требования

- `buf_reads` считает и приобретения на запись (`bufferCache.cpp:1459`) — завышение, читается в сторону «не определено» (отчёт F16k §3.2).
- `fill_seq` модуля `DiagF5Id` растёт без предела (по адресу заливки) — только при ручке, память.
- Глубина истории, нужная событиям, не печатается (RC4 F16i просил её в отчёт кода); п. 492(в)(3) заменил это на K = 8, видимость отката —
  `fix=fallback`. Не дефект кода.
- `fix=off` при `KYTY_FIX_F5CMU=1` возможен только без захвата (`KYTY_FIX_B42=0`) — так и написано в коде (`descriptors.cpp`).

## 4. Не заявляется

Что RC1–RC3 достижимы в игре или что их там нет; что сброс ветви 1 ложен хоть на одном событии; что `KYTY_FIX_F5CMU` меняет картинку или
корректна для железа; что K = 8 достаточно; что бинарь `9040a667` работает в игре (дыма не было — F16m); что ноль ветви — свойство игры;
что SPIR-V корректен для устройства и картинка верна. Ни одно число — не выигрыш; 60 FPS не обещаются.

## 5. Файлы

`docs/track-f/f16l/` — `refs_f16l.py`, `refs_f16l.txt` (34 ссылки, `ALL OK`). Локально `C:/kyty/f287/f16l/` — те же и `diff_810909e3.txt`.
