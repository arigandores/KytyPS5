# Сессия 130, шаг 0б — ревью диффа отгрузки `armcopy=1` (Red Team, `HPP-144`)

**ВЕРДИКТ: PASS — 0 BLOCKING, 0 MAJOR, 0 правок кода; 2 замечания отчёту/харнессу (N1, N2), не BLOCKING.**
Сборка отгрузки `0d23f161…` (коммит `76e2a5a3`) остаётся сборкой отгрузки; новой сборки ревью не требует
(п. 106(ж)). Игру не запускал, процессов тяжелее `grep`/`git`/`check_gate_order.py` не гонял; замка
`C:/kyty/SEALED_RUN.lock` не было (проверен 19:57 UTC).

Основание: `git show 76e2a5a3 -- src` (8 файлов, +119/−27), чтение окружающего кода `pageManager.cpp`
(`TakePendingRun`, `SetPendingRange`, `IsPending`, `AcApplyRuns`, `AcChunk`, `AcFlushChecked`, `AcFinish`,
`CeilScope`, `ArmCopyScope`, `ArmCopyBegin`), `memoryTracker.h` (`ForEachUploadRange`,
`CheckNotInUploadCallback`), `bufferCache.cpp` (`SynchronizeBuffer`, `UploadCopies`, `CopyGuestToStagingArmed`,
`ArmCopyContent`, путь `protbatch2`), `parallelCopy.cpp` (`Work`, `AsyncMemcpyArmed`, `WaitAll`), `gates.cpp`;
`ROADMAP.md` п. 103(б), 104(б), 105(б), 106; `C:/kyty/s130/FACTS.md` §Step 0а.

## 1. Требования поимённо

| требование | где | вывод |
|---|---|---|
| F1 — открытая на потоке операция ⇒ `Fatal`, не затирание | `ArmCopyBegin` (`pageManager.cpp:2309–2315`) | ВЫПОЛНЕНО. Проверка — первой строкой, до любой записи в `t_ac_op`. `t_ac_op.mode` ≠ 0 только между `ArmCopyBegin` ≠ 0 и `AcFinish`, который обнуляет его безусловно (`:1729`); `ForEachUploadRange` зовёт `ArmCopyFinish` при любом `arm_copy ≠ 0` (`memoryTracker.h:371–375`), путь между ними `noexcept` без ранних выходов — ложного `Fatal` на следующей синхронизации нет. |
| F2 — отказ `protceil` по защёлке `CeilScope` | `AcRefusal` (`:1214`) | ВЫПОЛНЕНО. `CeilScope` и `ArmCopyScope` — единственное место, соседние строки с одним `engage` (`GuestGpu::IsGpuThread()`, `bufferCache.cpp:896/899`), вложенность у обоих возвращается до чтения; ветка `CeilOutside` в `AcRefusal` недостижима (безвредна). `CeilSkip`/`CeilRefused`/`CeilDose` ⇒ отказ, как прежнее «ручка ≠ 0». |
| F3 — недопустимый диапазон ⇒ `Fatal` | `AcChunk` (`:1452–1457`) | ВЫПОЛНЕНО. `ValidateRange` (`:150–154`) — тот же предикат `GuestRange::Valid()`, что был в `return false`, теперь `Fatal`; предикат не стал строже — кусок, прежде вооружавшийся, не падает. |
| F4 — `t_protect_masked = false` в начале `AcChunk` и `AcFlushChecked` | `:1451`, `:1577` | ВЫПОЛНЕНО. Влияет только на ряды `protect_masked_*` (`:477–480`). |
| Проверка содержимого при 4 — тот же код, что при 2 | `parallelCopy.cpp` `Work` (`:358`), `AsyncMemcpyArmed` (`:513`) | ВЫПОЛНЕНО. Условие вызова `hook->check` — `mode ∈ [2, 4]` в обоих местах; функция одна — `BufferCache::ArmCopyContent` (тело не менялось), место одно — после `memcpy` куска, вне `m_mutex` пула (`Work`: `pop_front` под замком, `arm`/`memcpy`/`check` после). При 4 `ArmCopyBegin` отдаёт 4 (`AcNull`), `UploadCopies` идёт через `CopyGuestToStagingArmed` с хуком ⇒ крючок исполняется; вооружение при 4 — путь 0 (`batch.Flush` + `FlushProtection` до `upload_func`, `memoryTracker.h:350–362`). Нуль сравнивает куски с кусками (inline-копии проверки не несут ни при 2, ни при 4 — п. 106(е)). |
| `ac_jstale` не удовлетворяется взятием без снятия бита | `AcStampTake` (`:1386–1393`), `AcApplyRuns<true>` (`:1427–1429`), `AcChunk` (`:1509–1545`) | ВЫПОЛНЕНО ПО БУКВЕ: чтение назад — в той же хватке `region.lock`, что `TakePendingRun`; бит, не снятый взятием, читается 1 ⇒ страница в `stale` ⇒ в `stuck = left ∧ taken ∧ stale` ⇒ в `ac_jstale` при `Perms() ≠ ReadWrite`. `IsPending` — только бит `pending` (`:830–832`), `applying_run` не читает ⇒ свежая пометка в `stale` не попадает. Оговорка — N1. |
| Штампы не трогают пути 0/1 | `AcChunk` при 1 (`:1481–1485`), `AcApplyRuns<false>` | ВЫПОЛНЕНО. При 1 кусок уходит в `AcApplyRuns<false>` (текст с. 129) до объявления `stale`/`stuck`; код пометки (`SetPendingRange`, `UpdateRegionWatchers`, `ProtectRun`) и `Region` не менялись; при 0 у заданий нет хука. |
| Смена умолчания и отказы | `gates.cpp:446` `{"KYTY_ARM_IN_COPY", "armcopy", 1, 4}` | ВЫПОЛНЕНО. Отказ `notrace` — только `value ≥ 2` (`:1246`); путь 1 не читает `FS::Enabled()` ни в одном решении. Строки `ArmCopy: refused reason=` раз на причину и `ac_refuse` — без изменений (`:2278–2296`). При умолчаниях гейтов (`protbatch` 1, `protbatch2` 0, `armdefer` 0, `bufimp` 0 — `gates.cpp:48/85/96/353`) ни одна причина не срабатывает — на деле видит только `shp130` (строка `ArmCopy: mode 1`, Σ`ac_moved_n` > 0). |
| Порядок ручек | `gates.h`/`gates.cpp` | ВЫПОЛНЕНО. Новых гейтов/ручек нет; `python C:/kyty/s96/check_gate_order.py` — `GATE ORDER: clean` (перезапущен мной; `UNMATCHED … ArmInCopy` — эвристика имени, как в с. 129). Счётчик `AcJstale` — последним перед `Count`, `ac_jstale` — последним в `named` `videoOut.cpp`, сырые штуки (`false`). |
| Ни одного нового ожидания под `m_mutex`/`apply`/`RegionManager::lock` | весь дифф | ВЫПОЛНЕНО. Новое под `region.lock`: `AcStampTake` — цикл по ≤ `call_pages` битам, без ожиданий. Новое под `apply`: `AcHostProtect` (`VirtualQuery`) в `AcLogLeft` — вызов хоста, не ожидание замка; только при 2, только для строк `LEFT`, ≤ 40 строк на процесс (после предела — ранний выход до запроса), ≤ 1 024 страниц на строку (`REGION_SIZE` 4 МиБ). Проверка содержимого при 4 — вне `m_mutex` пула, без замков (`IsCpuDirtyRelaxed`). `ValidateRange` — без замков. |

## 2. Условие п. 106(в): достижимость обоих вложенных путей — НЕ ДОСТИЖИМЫ ⇒ не BLOCKING

- **Экземпляр трекера один.** Единственный член типа `MemoryTracker` — `BufferCache::m_memory_tracker`
  (`bufferCache.h:380`); `BufferCache` — член `RenderContext` (`renderContext.h:96`). Других владельцев
  `MemoryTracker` в `src` нет (поиск по объявлениям и конструктору).
- **Вложенный `ForEachUploadRange` в `upload_func` ⇒ `EXIT` раньше `ArmCopyBegin`.** `ForEachUploadRange`
  первой строкой зовёт `CheckNotInUploadCallback()` (`memoryTracker.h:305`), который `EXIT`-ит при
  `s_upload_owner == this` (`:404–407`); `s_upload_owner` ставится в `this` до `ArmCopyBegin` (`:318`, `:322`) и
  держится до конца `upload_func`. При одном трекере любая вложенная синхронизация на том же потоке умирает
  на строке «memory tracker re-entered from upload callback», не дойдя ни до `ArmCopyBegin` (путь 1), ни до
  своего `UploadCopies` (путь 2: записываемая синхронизация, читающая `ArmCopyOpMode()` внешней операции).
- **`UploadCopies` вне `upload_func`.** Второй вызов — `bufferCache.cpp:2907` (путь `protbatch2`, после прохода,
  вне любой операции: его `ForEachUploadRange` идёт с `pass_batch = true` ⇒ `ArmCopyBegin` не зовётся, и
  `protbatch2` при ≥ 1 — сам причина отказа). `ArmCopyOpMode()` там = 0.
- `t_ac_op` — `thread_local`; `ArmCopyScope` защёлкивается только на потоке GuestGpu.
- **Сказано вслух:** вывод держится на «один экземпляр трекера» и на `CheckNotInUploadCallback`; появление второго
  `MemoryTracker` (или снятие этой проверки) делает оба пути достижимыми — F1 тогда громкий, путь 2 — нет.

## 3. Замечания (не BLOCKING; кода не меняют)

**N1 — `ac_jstale` структурно равен 0; его провал — зависание куска, не число (владелец: Harness Engineer в отчёте 0в
и `ack130`, лид — в приёмке 0в).** `TakePendingRun` снимает биты ровно отчитанного прогона `[page, end)`
(`SetPendingRange(region, page, end - page, false)`, `:957–959`) в той же хватке `lock`, в которой `AcStampTake`
их читает ⇒ на нынешнем коде `stale` ≡ 0 по построению. Опасный класс «взял, но не снял» при 2 проявился бы не
счётчиком: `AcApplyRuns` (`:1418–1439`) снова и снова брал бы тот же прогон со стоящим битом — бесконечный цикл
куска под `apply` (при 3 — тот же цикл в хвостовом `AcApplyRuns<false>`), то есть зависание пула и GuestGpu в
`WaitAll`, а не `ac_jstale` > 0. **Сценарий неверного вывода:** отчёт 0в/`ack130` пишет «`ac_jstale` = 0 ⇒ гипотеза
чужой свежей пометки (MINOR-1 аудита 129) подтверждена» — но 0 здесь доказывает только, что куски завершились.
**Что сделать:** страж п. 105(б)(3) остаётся как есть (строгий, дешёвый); свидетельство по MINOR-1 — поле
`remark=` строк `LEFT` ветки куска: отчёт печатает число страниц `rm=1` по `remark=1` / `remark=0` и по `perms`
(у `rm=1 remark=0 perms≠3` — ровно `ac_jstale`); `ac_jstale` = 0 цитируется только как «страж не сработал»,
не как опровержение. Лид уже сказал вслух (п. 106(а)), что страж видит только несснятый бит; N1 добавляет, что
на нынешнем коде и этот класс он не увидит раньше зависания.

**N2 — харнесс с. 130 обязан знать новые поля (владелец: Harness Engineer, шаг 1 / 0в).** (а) `ac_jstale` в явном
списке ключей разборщика `FrameTrace-x` (у `smk129.py` — фиксированный кортеж ключей, `:46–47`): **сценарий
отказа** — порт без нового ключа суммирует 0 и «проходит» строгий страж, которого не читал; требуется фикстура
`ac_jstale` > 0 ⇒ `ARMCOPY_INCORRECT` и отказ разбора, если ключа нет в строке (лог не той сборки — у `edd17418`
его нет). (б) При 4 теперь живут `ac_cmp_pages`/`ac_cdiff`/`ac_cbad` и строки `ArmCopyVerify: CONTENT … mode=4`:
**сценарий отказа** — перенесённое из с. 129 правило «при 4 строк `ArmCopyVerify` нет/ряд содержимого 0» валит
нуль-плечо дыма `armcopy=2|4` ложным провалом; при 0 и 1 правило «ни одной строки `ArmCopyVerify`» остаётся
верным (крючок проверки — только 2..4). (в) Строка `LEFT` несёт `rm= remark= host= mode=` — разбор по полям, не
по соседству `rm=… mode=`; фикстура на новую строку. Σ`ac_cmp_pages` > 0 в обоих плечах 2|4 — обязательное
условие п. 105(б)(2) — это и есть живой контроль того, что проверка при 4 действительно исполняется.

## 4. Чек-лист кода (Red Team)

- Вызовы вне хронометрируемой строки: `AcJstale`/`AcJremark`/`AcJleft` добавляются вне `t0…AcChkNs`; `AcDetect`
  хронометрируется как в с. 129; `AcHostProtect` — вне таймеров. ОК.
- Гонки: `stale` — локальные биты куска; `IsPending` под `lock`; `logged` в `AcLogLeft` — гонка двух потоков на
  пределе 40 даёт ≤ 1–2 лишних строки (как в с. 129), не число. ОК.
- Инварианты `*_bad`: `ac_jstale` на корректном пути недостижим (N1 — даже на некорректном до зависания). ОК.
- Ранние возвраты: `AcChunk` — `t_protect_masked` снимается до раннего `return false`; `AcLogLeft` — ранний
  выход по пределу до `VirtualQuery`. ОК.
- Правка — скриптом `patches/patch_ship130.py` (`ced041b1…`), дифф `src` в LF (8 файлов, `git show` без `^M`). ОК.
- Размер кадра: `REGION_PAGES` = 1 024 ⇒ `PageBits` = 128 Б; `AcChunk` +2 × 128 Б (`stale`, `stuck`) к
  ≈ 2,2 КиБ `AcSnap`/битов; исполняется на воркерах пула и на GuestGpu (помощь в `WaitAll`), не на стеке гостя. ОК.
- Правка в `src/graphics/shader/**` — нет ⇒ подпись кэша трансляции не меняется. ОК.
- Инструмент только измеряет: при 1 новых вызовов нет, кроме F4 (присваивание) и F3 (`Fatal` вместо `return false`
  на недостижимом диапазоне); при 2/4 — чтения и `VirtualQuery`, без изменения вооружения. ОК.

## 5. Что этот отзыв НЕ доказывает

Что сборка `0d23f161` стартует и ведёт себя при 1 как `edd17418` (дымы и `shp130` — шаг 0в); что `ac_cbad` при 4
> 0 и отношение долей ≤ 1,5 (шаг 0в, п. 105(б)(2)); что при умолчании не срабатывает отказ (`shp130`); что перенос
не теряет записей гостя вообще; время сборки отгрузки; что второй экземпляр трекера не появится. Выигрыша не
заявляю; 60 FPS не обещаются.
