# Сессия 129, шаг 4 — ревью кода ручки `armcopy` (HPP-134, Red Team)

**Вердикт: PASS_WITH_FIXES — НЕ BLOCKING.** 0 MAJOR, 4 MINOR по коду (F1–F4), 4 замечания для харнесса/скорера (N1–N4).
Ни один пункт не меняет исход дымов шага 5, `ack129` или `ac129`; шаг 5 можно ставить на сборке `edd17418` как есть.
Если лид велит внести F1–F4 до дыма — это новая сборка и новая закреплённая копия; дымы тогда ставятся на ней.

Предмет: коммит `67962c18` (11 файлов, +1 029/−10), сборка `C:/kyty/s129/kyty_emulator_edd17418.exe`, против проекта
`docs/session-129/design129.md` ред. 2 (`265cdd56…`), `ROADMAP.md` «СЕССИЯ 122» п. 97(е)(1), 98(и), 99(а)–(г), 101(б)–(г),
102(б), (г). Дерево `src` на момент ревью совпадает с коммитом (`git status --short -- src` пуст). Игра не запускалась,
сборок и прогонов не было; `C:/kyty/SEALED_RUN.lock` отсутствовал. Время — UTC.

## 1. Проверки, заказанные поимённо (п. 101(е), 102(г))

| пункт | где в коде | итог |
|---|---|---|
| «0 — прежний путь» (чтение п. 98(и)) | `ArmCopyScope` при 0 → `AcZero`, `ac_op0`; `ArmCopyBegin` → 0 без побочных эффектов (`pageManager.cpp:2231`); `memoryTracker.h` ветка `arm_copy ∈ 1..3` не берётся, `else if (!pass_batch)` — прежний текст (`batch.Flush()` + проход диапазона), `ArmCopyFinish` не зовётся; `UploadCopies` → `CopyGuestToStaging` без изменений; `Work`: `hook == nullptr` → прежний `memcpy`; `Protect`: `arm != Job` всегда истинно, блок `ac_*` при `AcZero` ничего не считает | **ДА** по чтению п. 98(и): смены защиты хоста, биты трекера, куски пула (адрес, размер, порядок, `sequence`) — те же. Отличия: `Job` 32 → 56 Б, +39 полей `FrameTrace-x`, одно чтение ручки и две записи TLS на операцию, одно чтение TLS в `Protect` под `t0 ≠ 0`. `Region` не менялся (`static_assert(sizeof(Region) == 1312)` стоит) |
| защёлка раз на операцию | `ArmCopyScope` (`bufferCache.cpp`, рядом с `CeilScope`, вокруг всего `ForEachUploadRange`) — единственное `Gates::Value(ArmInCopy)`; дальше — TLS `t_ac_state`/`t_ac_mode`/`t_ac_op.mode`; каждый `Job` несёт `mode`, воркер ручку не читает | **ДА**. Порваться внутри операции ручка не может; отказы читают ДРУГИЕ гейты (см. F2) |
| «вооружить → скопировать» в задании | `Work` (`parallelCopy.cpp`): `hook->arm(...)` (→ `AcChunk`) ДО `memcpy`, `Complete` после; `AcChunk` при 1/2 — хватка `apply` на каждую область куска, все отложенные прогоны `[first, last)` применены (`AcApplyRuns`), отпуск, затем `memcpy`; при 3 — `memcpy` внутри хватки | **ДА**. Кусок берёт `apply` и при пустом J (свойство R); значение `Perms()` читается под `lock` в той же хватке (`TakePendingRun`) — применения устаревшего значения нет |
| порядок замков, п. 99(г) | кусок: `CopyPool::m_mutex` отпущен до работы → A → L (отпущен до `Protect`) → `ProtectTransient` (`m_mutex` адресного пространства, shared/exclusive) → ядро; GuestGpu: inline/остаток/детектор — после `upload_func`, `RegionManager::lock` read-only отпущены | **ДА**. Новых `WaitAsyncCopies`/`WaitAll`/ожиданий GPU под A, M или `m_mutex` адресного пространства нет ни одного. Проверено отдельно: `ProtectGuestHostMemory` (`memory.cpp:4108`) берёт только `m_mutex` адресного пространства, не `g_memory_operation_mutex`, которым держится снятие отображения, ждущее GPU → семафор копий → кусок (`FreeGuestMemory` `:4114`, `KernelMunmap`); держатели `m_mutex` адресного пространства — листовые методы, ничего не ждут. Цикла «кусок ↔ снятие отображения» нет |
| RC1 (детектор только по состоянию) | `AcDetect`: под `lock` снимок `pend_now`/`watched`/`Perms()`, затем `VirtualQuery` под удерживаемым `apply`; `bad = watched ∧ ¬pend ∧ host_w`; бухгалтерия вызывающего не входит | **ДА**. `IsPending` (`pageManager.cpp:830`) читает только бит `pending`, не `applying_run` — взятый при 3 прогон («биты сняты, `Protect` не дан») детектору виден, контроль 3 не мёртв по построению. Кэш ответа `VirtualQuery` по `BaseAddress + RegionSize` корректен (однородный диапазон, хост заморожен под `apply`) |
| RC2 (ветка GuestGpu) | `AcFinish` шаг 3 при 2/3 — последний шаг операции, по каждой области G своя хватка `apply`; `ac_gchk`/`ac_gbad`/`ac_gjleft`, G_own = (окна − пуловые) ∪ inline/врем. | **ДА** |
| значение 4 (нуль) | `AcNull` → `Flush` + проход диапазона (путь 0), `ArmCopyNoteCopy`/`ArmCopyFlush` при 4 — no-op, пуловые — `AsyncMemcpyArmed` с режимом 4 → `AcChunk` только детектор (без `Protect`); ветки GuestGpu нет | **ДА** — смены защиты хоста те же, что при 0 |
| п. 101(б) | `AcLogLeft`: `perms=` из снимка, `rm=0|1` у куска, `rm=-` у ветки GuestGpu; строки `LEFT` — только при 2 | **ДА** |
| п. 101(г) (3 — «взять → проверить → применить» во всех сбросах GuestGpu) | inline — `ArmCopyFlush` → `AcFlushRange(checked)` → `AcFlushChecked`; остаток — `AcFlushWindow(mode 3)`; врем. буфер — `ArmCopyFlushWindows` + `ArmCopyFlush(Tmp)` | **ДА** |
| самопроверка 2 без ложного `ac_jleft − ac_jremark` | при 2 кусок держит `apply`, а снять `pending` (кроме пометки `BatchScope` чужого потока под L) можно только под `apply` → после цикла `AcApplyRuns` J ⊆ T; J ∩ `pend_now` ∖ T на исправном пути недостижимо | **ДА** — строгая часть п. 101(б) — честный страж |
| счётчики, типы | 39 имён в конец `Counter` и `named` (после `pc_dose_ns`, `pc_u_live` остаётся последним), все `micros=false`; `AcAddKept` добавляет итог и причину одним вызовом (Т1 точно); `LOGF` строит `std::string` (`fmt::sprintf`) — удлинённая строка `FrameTrace-x` не усекается | **ДА** |
| отказы | `AcRefusal`: `protceil`, `armdefer`, `protbatch2`, `protbatch0`, `asynccopy`, `nopool`, `asyncprotect`, `bufimp`, `notrace` (2/3/4); строка раз на причину (биты 8..16), `ac_refuse` на каждую защёлку | **ДА** (девять причин §8.2) |
| порядок ручек | `{"KYTY_ARM_IN_COPY", "armcopy", 0, 4}` — последняя строка `KNOB_DEFINITIONS`, `ArmInCopy` — последний перед `Count`; `GATE ORDER: clean` (отчёт шага 3) | **ДА** |
| счёт `ac_moved_*`/`ac_job_other_n` против п. 102(б) | `ac_moved_*` — `Protect` с `Arm::Job` на роли ≠ `Gpu` (любой режим); `ac_job_other_n` — прогоны куска с режимом ≠ `Read` на ЛЮБОЙ роли (в том числе помощь GuestGpu) | **соответствует**, единицы одни (вызовы). Смещение отношения — ВВЕРХ (консервативно, см. N3) |
| кадры стека | `ArmCopyChunk` 2 264 Б, `AcFinish` 2 056 Б, `AcFlushChecked` 1 432 Б (отчёт шага 3) — потоки пула, GuestGpu, презентации; вызовов `WaitAsyncCopies` с гостевого потока нет (вызовы: `bufferCache.cpp:1588`, `commandScheduler.cpp:334/808/840/932`) | **ДА** |
| вложенная операция | `t_ac_op` один на поток; повторный вход в `ForEachUploadRange` того же трекера из `upload_func`/`range_func` — `EXIT` (`CheckNotInUploadCallback`, `memoryTracker.h:305`) | недостижимо в нынешнем коде; страховка — F1 |
| `src/graphics/shader/**` | не тронут | подпись кэша трансляции прежняя |

**Порядки событий О1–О13 проекта сверены с кодом:** покрытие окна — пуловые страницы вооружает кусок (включая
неполные страницы на краях кусков и копий: `AlignDown`/`AlignUp`, соседние куски одной страницы оба берут `apply` перед
своими байтами), inline — сброс диапазона копии перед чтением, остаток — `AcFinish` после `upload_func` на любом выходе
(`copies.empty()`, путь импорта — окна целиком в остатке), временный буфер — сброс всех окон и копий до `memcpy`.
Регионы трекера страниц не освобождаются до деструктора `PageManager` (`region_storage`) — указатель `Region*` в куске,
исполняемом после конца операции, живой; требование «крючок живёт дольше кусков» — то же, что у staging при 0.

## 2. Правки по коду (MINOR, не BLOCKING)

**F1. `ArmCopyBegin` затирает операцию, уже открытую на потоке** — `pageManager.cpp:2231`.
Что не так: при `t_ac_state ∈ {AcMove, AcNull}` функция безусловно обнуляет `t_ac_op` (`window_count = 0`,
`copies.clear()`, `mode = …`). Сценарий отказа: вложенный `ForEachUploadRange` другого `MemoryTracker` на том же потоке
внутри `upload_func` внешней операции при 1 (второй `BufferCache`/`RenderContext` — `CheckNotInUploadCallback` ловит только
свой трекер) → окна внешней операции теряются (остаток не вооружается), внутренний `AcFinish` ставит `op.mode = 0` →
последующие `ArmCopyFlush` внешних inline-копий (`mode < 1` → `return`) НЕ вооружают диапазон перед чтением → запись гостя
после копии без фолта = потерянная запись; самопроверка 2 этого не видит (детектор ветки GuestGpu при `mode 0` не
запускается). Сегодня недостижимо (`UploadCopies` не зовёт другой кэш), поэтому не BLOCKING. Изменить: в
`ArmCopyBegin` при `t_ac_op.mode != 0` — `EXIT`/`Fatal` (или вернуть 0 без касания `t_ac_op` плюс счётчик-страж).

**F2. Отказ `protceil` читает ручку заново, а не защёлку `CeilScope`** — `AcRefusal` (`pageManager.cpp:1208`).
Сценарий отказа: `protceil` меняется между `CeilScope` и `ArmCopyScope` той же синхронизации (расписание с плечом по
`protceil`) → `CeilSkip` при `AcMove`: кусок вооружает (у `AcApplyTaken` нет ветки `CeilSkip`), а сброс остатка через
`FlushRegion` пропускает вызов и ставит U — смесь двух механизмов в одной операции, `pc_*` и `ac_*` рядов нельзя читать.
В с. 129 `protceil` пин 0 и значение 1 выведено из употребления (п. 93(б)) — не BLOCKING. Изменить: отказ по
`t_ceil_state ∉ {CeilOutside, CeilZero}` (то, что реально защёлкнуто), а не по `Gates::Value(ProtCeiling)`.

**F3. Недопустимый диапазон куска молча копируется без вооружения** — `AcChunk`, `pageManager.cpp:1394`.
Сценарий: `!GuestRange{vaddr, size}.Valid()` → `return false` → `Work` копирует, отложенное не применено. При 0 тот же
диапазон прошёл бы `FlushRange` → `ValidateRange` → `Fatal` (громко). Диапазон приходит из трекера и сегодня всегда
допустим — не BLOCKING. Изменить: `Fatal`/`EXIT` вместо `return false` (паритет с путём 0: громкое падение, не тихая
потеря вооружения).

**F4. Новые пути вооружения не сбрасывают `t_protect_masked`** — `AcApplyRuns`/`AcApplyTaken`/`AcFlushChecked`
(ср. `FlushRegion`, `pageManager.cpp:1037`). Сценарий: GuestGpu оставил `t_protect_masked = true` после маскированного
`UpdateRegionWatchers`, затем исполняет кусок как помощник `WaitAll` или делает сброс «взять → проверить → применить» при 3
→ эти вызовы попадают в ряды `protect_masked_*`. Только ряды, не условие. Изменить: `t_protect_masked = false;` в начале
`AcChunk` и `AcFlushChecked`, как в `FlushRegion`.

## 3. Замечания для харнесса и скорера (не правки кода)

**N1. Ряды, меняющие смысл между плечами 0 и 1.** При 1 сброс inline-копии идёт через `FlushRange` и считается в
`BatchInvalidateFlushes`/`BatchRefault` (`pageManager.cpp:1093`), сбросы `BatchScope` (`BatchFlushes`, `BatchMerged`,
`pc_elig_scope_n`) пропадают, `ApplySkipWould*`/`pb_wait_range_us` растут от сбросов остатка. Сценарий: скорер или лид
читает разность этих рядов по плечам как «работа механизма» — это перенос учёта, не работа. Требование: в печати
`pred/01_ac129.md` эти ряды — только по плечам, без разности как вывода.

**N2. `stglap` на пути 1..4 не пишет `stg_res_ns`** (`CopyGuestToStagingArmed`, `bufferCache.cpp:258`, против
`CopyGuestToStaging` `:240`). В `ac129` `stglap` = 0 — без последствий; если гейт когда-либо включат вместе с `armcopy`,
`stg_res_ns` плеча 1 = 0 не есть экономия.

**N3. Направление смещения правила п. 102(б).** Числитель Σ`ac_job_other_n` включает прогоны помощи GuestGpu, знаменатель
Σ`ac_moved_n` — нет; отношение завышено, т. е. правило чаще даёт «стоп и вопрос» — в безопасную сторону. Скорер пусть
печатает рядом Σ`ac_kept_help_n`, чтобы величина смещения была видна.

**N4. Ряд `ac_orphan` при 1 ожидается 0, но пустой `copies` с непустыми окнами применяется правильно** (`AcFinish` шаг 1
до шага 2) — ряд, не страж, как решено п. 101(в); отдельной проверки кода не требует.

## 4. Чек-лист кода (роль)

- Вызовы вне хронометрируемой строки: `ac_chk_ns`/`ac_gchk_ns` охватывают только `AcDetect` (снимок + `VirtualQuery`);
  `FS::Add` — вне интервала; `ac_moved_ns`/`ac_kept_ns` — существующая пара `NowNs` внутри `Protect` вокруг
  `ProtectGuestHostMemory` — тот же интервал, что у `prot_gpu_*`/`pc_elig_*`. ✓
- Гонки: снимок детектора под `lock`, хост заморожен под `apply`; `IsCpuDirtyRelaxed` — лок-фри, только ряд
  (`ac_cbad`); публикация `applying_run` — существующей `TakePendingRun` (seq_cst + release), снятие — до отпуска `apply`. ✓
- `*_bad`: `ac_bad` при 2 недостижим на исправном пути, кроме смены защиты мимо трекера (отделяет 4) и пересборки вида
  хоста (заглушка при перестроении backing, `memoryAddressSpace.inc:863–865` — класс пути 0, тоже отделяет 4). ✓
- Ранние возвраты: `AcChunk` при `region == nullptr` пропускает только область без страниц (при 3 копирует байты);
  `AcFinish` зовётся на любом выходе `upload_func`. ✓ (F3 — единственный тихий возврат.)
- Правки с C-строками/обратными слэшами, CRLF, якоря — скрипт `patches/patch_armcopy129.py` (`f375e99a…`) дерево
  собрал; `git status -- src` чист, дифф без мусора CR. ✓
- Стек: см. таблицу §1. ✓

## 5. Не доказано этим ревью

Что механизм не теряет записей гостя и не вешает GPU (только дым шага 5, `ack129`, видео); что контроль 3 жив в обеих
ветках на деле (`ac_bad` > 0 И `ac_gbad` > 0 — дым); что нуль 4 пуст (`ac_bad` = 0 при `ac_chk` > 0 — дым); S и
выигрыш; цена сборки при 0 против `9235a7ac`. 60 FPS не обещаются.
