# M5a — HLE, часть 2: T159, T309, T141, T210, T246, T270, T271 (офлайн-разбор)

Код: KytyPS5 `main` `dd73d04d` (рабочее дерево = HEAD). Только чтение кода, импортов и логов, офлайн-модели на Python. Эмулятор, игра, сборки, ГП — не запускались.
Метки: [c] — показано чтением кода / счётом / моделью; [I] — вывод; [U] — неизвестно.

Источники исполнения:
- импорт NID: `imports_m5a.py` → `imports_m5a.out.txt` (eboot.bin sha256 `3b5100797fe83663…`, `sce_module/libc.prx`, `sce_module/libSceNpCppWebApi.prx`; в каталоге игры других модулей нет, кроме `sce_sys/about/right.sprx` — не код игры);
- логи: `log_m3_sg_v_r1.txt` (MS1, 1 164 394 строки), `log_m3_i.txt` (MS1, 4 601 977), `log_m3_hb_f.txt` (FS15, 1 879 933) — `logscan_m5a.py` → `logscan_<tag>.out.txt`; контекст — `ctx_m5a.py` → `ctx_*.out.txt`;
- модели: `stand_m5a.py` → `stand_m5a.out.txt` (`ALL OK`).
- В логах `KYTY_PRINT_NAMES` не включён: строк `PRINT_NAME` для `Ampr::`, `Sysmodule::`, `SystemService::` — 0 во всех трёх логах (печатаются только `libkernel::Pthread*`). Поэтому вызов функции без собственной `LOGF` по логам не виден.

## Таблица

| тема (коммит) | исход | исполнение игрой [c] | основание (коротко) |
|---|---|---|---|
| T159 `5bf9218b3` (одна последовательность) | НЕ ДЕФЕКТ | импорт AMPR [c]; исполнение APR-чтений/событий в логах 0 | порядок у нас = порядку добавления: смещения записей уникальны и строго растут, сортировка по смещению `libAmpr.cpp:1354-1383` [c] |
| T159 `c045f0890` (WaitOnAddress, приоритеты) | паркуется до вызова с ложным условием | `DLfoNxTFNVk` импорт [c]; вызов — [U] (строк нет) | наш `WaitOnAddress` — no-op `libAmpr.cpp:2012-2017`, исполнение синхронно в Submit `:599-610`, `:1327-1460` [c]; вред [I] |
| T159 `da9b38af2` (thread_local подкачка) | НЕ ДЕФЕКТ | — | только скорость (`ReadHostFileToGuest` `:1514-1515` выделяет буфер на чтение) [c] |
| T159 `5a8808086` (WaitOnCounter/WriteCounter) | паркуется до вызова с ложным условием / чтения счётчика | `cQb8Zr8Q0Y0`, `jK+yuYCI7MA`, `t4ExS+SwLjs` импорт [c]; вызов [U] | no-op `:2019-2024`, `:2052-2057`; `WriteAddressFromCounter*` пишет 0 `:2081-2109` [c]; вред [I] |
| T309 `41beda436` (размер WriteAddress 8/12/16) | паркуется до отказа места в логе | `j0+3uJMxYJY`, `4fgtGfXDrFc` импорт [c]; путь APR-чтений: строк `MT265: mode=` 0 в 2 логах MS1 ⇒ Resolve не исполнялся | наша мера (`4fgtGfXDrFc` → 0x20 `:1705-1710`, `:2588`) согласована с нашей записью 0x20 `:1198-1216`; отличие только если игра не зовёт меру — модель [c] |
| T141 `34a3eb6b5` (AMM авто-подложка) | НЕ ДЕФЕКТ (путь недостижим) | `AmmCommandBufferMap*`, `AmmGiveDirectMemory`, `AmmSubmit*` — НЕ импортируются [c] | утечка в коде есть [c модели], но `AllocateAmmAutoDirectMemory` зовётся только из записей `AmmCommandBufferMap*` `:2275-2317` |
| T210 `46900d804` (замена живого фикс. отображения) | паркуется до fixed-поверх-живого в логе | MapDirect fixed: 3 за запуск, все на ранее не отображённые диапазоны; поверх живого 0 из 3 логов, `munmap` 0 [c] | промежуток в нашем коде есть `memory.cpp:3401`→`:3687`→`:3729`→`:3369-3372` [c]; правка upstream — только `#if KYTY_PLATFORM_LINUX` [c] |
| T246 `afbb322b3` (событие-уровень один раз за ожидание) | НЕ ДЕФЕКТ (путь недостижим) | `AddUserEvent` и все прочие добавляющие user-события NID не импортируются; строк `user event add:` 0 [c] | копии отдаёт только событие `KernelAddUserEvent` без `EV_CLEAR` (`eventQueue.cpp:109-133`, `:288-295`); GPU EOP/VideoOut очищают `triggered` [c] |
| T270 `210d4dcd9` (Sysmodule IsLoaded) | паркуется до прогона с именами функций | импорт `fMP5NHUOaMk` [c]; строки `\t id = N` 31 на лог, функция не различима [U] | `IsLoaded` → 0 `libSysmodule.cpp:57-63` [c]; ответ upstream сам не эталон (не знает модулей, загруженных без `LoadModule`) [I] |
| T271 `62643c342` (ENTITLEMENT_UPDATE) | паркуется до свидетельства консоли и следствия | `AppContentInitialize` исполняется 1 раз [c]; `ReceiveEvent` — импорт, вызов [U] | `ReceiveEvent` → NO_EVENT `libSystemService.cpp:146-157`; что консоль шлёт событие — [U] |

Исходов «А» нет.

## T159 — AMPR, четыре коммита

**Как исполняется у нас [c].** `SubmitCommandBuffer*` (`dd73d04d:src/libs/libAmpr.cpp:568-637`) и `AmmSubmit*` (`:2457-2525`) синхронно в потоке вызывающего вызывают `ExecuteAprCommandBuffer` (`:1327-1460`): команды из четырёх векторов (`:766-769`) собираются, сортируются по `record_offset` (`:1381-1383`) и исполняются по порядку — чтение файла, `KernelTriggerUserEvent`, запись адреса, AMM. `WaitOnAddress` (`:2012-2017`, NID `DLfoNxTFNVk`/`V7GQTEeUfhw`), `WaitOnCounter` (`:2019-2024`), `WriteCounter`/`OnCompletion` (`:2052-2064`) — `AppendNoOpCommand` (место 0x20, без действия). `WriteAddressFromTimeCounter*`/`FromCounter*`/`FromCounterPair*` (`:2066-2109`) пишут 0 вместо значения.

**Исполнение игрой.** Импорт [c]: все NID APR/AMPR, кроме `…OnCompletion` (`sJXyWHjP-F8`, `3wn42MWTzTs`, `FI2JD0jAHCs`, `gSF5OsXdfIg`, `ZLWtNUP6R5E`), меры `C+IEj+BsAFM`, второго `WaitOnAddress` `V7GQTEeUfhw` и всего AMM (`imports_m5a.out.txt`). Логи [c]: `MT265: mode=` (печатается при первом входе в `ResolveOnePath`, `:69-76`, `:220`) — 0 в `sg_v_r1` и `i` (MS1; в FS15 `hb_f` этого кода нет); `APR submit failed for unknown file id` 0; `APR submit read failed` 0; `user event trigger:` 0 (его печатает и путь команды события AMPR, `:1413` → `eventQueue.cpp:505`); `AMPR submit write-address failed` 0; `AMM submit command failed` 0 — во всех трёх логах. Вывод: в этих прогонах игра не получала ID файлов APR (Resolve до `ResolveOnePath` не доходил) и не исполняла ни команды чтения с известным ID, ни команды события; совпадает с ROADMAP п. 765 («T265 — путь AMPR в серии не вызывался»). Вызовы `WriteAddress`/`WaitOn*`/`WriteCounter` своих строк не имеют — [U]. Оговорка [I]: `ResolvePathsCommon` (`:297-330`) может вернуть EINVAL/EFAULT до `ResolveOnePath`, такой вызов строки `MT265` не даёт.

- **`5bf9218b3` — НЕ ДЕФЕКТ [c].** Все добавления идут под `g_command_buffer_mutex`, каждое увеличивает `write_offset` на размер > 0 (`:937-965`); векторы чистятся вместе со смещением при `SetBuffer`/`Reset` (`:1027-1058`) и стираются при `ClearBuffer` (`:1634-1660`). Значит смещения записей в буфере уникальны и монотонны, сортировка по смещению воспроизводит порядок добавления — то же, что единая последовательность upstream. Отличий ответа нет.
- **`c045f0890` — паркуется.** Дефект относительно названной семантики [I]: при ложном условии на момент Submit консоль задержала бы последующие команды до записи другим агентом, у нас чтение/запись забора/событие исполняются сразу (а чтение в ещё используемый буфер — порча данных [I]); блокировать синхронно в нашем Submit нельзя (тупик, если пишет тот же поток). Исполнение не показано. **Условие:** прогон с `KYTY_PRINT_NAMES=1` (или звено измерения: счётчик «`WaitOnAddress` с ложным условием в момент исполнения», значение по адресу и `compare`) даёт ≥ 1 такой случай в игре.
- **`da9b38af2` — НЕ ДЕФЕКТ [c]:** переиспользование буфера подкачки в потоке исполнителя меняет только аллокации; без исполнителя `c045f0890` не применим.
- **`5a8808086` — паркуется**, условие как у `c045f0890`, плюс: игра читает значение, записанное `WriteAddressFromCounter*`/`WriteCounter` (у нас 0). Замечание для лида: upstream ставит `EXIT_NOT_IMPLEMENTED` на `access != 1 || mask_op != 0 …` — перенос без данных о режимах игры даёт риск K1 [I].

## T309 — `41beda436`, размер записи WriteAddress

**Код [c].** `CommandBufferWriteAddress` (`j0+3uJMxYJY`, `:2037-2042`) → `AppendWriteAddressCommand` (`:2026-2035`) → `AppendWriteAddressRecord(…, 0x20)` (`:1198-1216`); при нехватке места `EnsureCommandBufferRecordSpace` (`:937-946`) ⇒ `KERNEL_ERROR_EBUSY`, **строки журнала нет**. Мера `4fgtGfXDrFc` → `MeasureCommandSizeFixed32` = 0x20 (`:1705-1710`, `:2588`). Upstream: мера и запись 8/12/16 по значению.

**Модель [c]** (`stand_m5a.out.txt`): буфер 768 Б, 16 пар чтение (0x14) + забор (значение i+1). По размерам SDK [I] нужно 500 Б — помещается. Наш код при игре, раскладывающей буфер постоянными SDK: пары 14 и 15 — `WriteAddress` → EBUSY, забор потерян (смещение 768). Игра, меряющая через `4fgtGfXDrFc` перед добавлением: потерь 0 (2 Submit вместо 1). Т.е. наша мера и наша запись согласованы; отличие возникает **только** если игра не зовёт меру (или зовёт с одним значением, а пишет другое, — у нас и это безопасно: всегда 0x20).

**Исполнение.** Импорт `j0+3uJMxYJY` и `4fgtGfXDrFc` [c] (импорт меры — довод [I], что игра меряет). Тест upstream воспроизводит потерю на `sJXyWHjP-F8` (`OnCompletion`), который ASTRO BOT **не импортирует** [c]. Пакеты «чтение + забор» требуют ID файлов — Resolve в логах MS1 не исполнялся (`MT265` 0) [c]. Отказ места не печатается — показать его по существующим логам нельзя. Потеря забора при загрузке дала бы зависание на ожидании; сцены M3 входят и держатся [c по ROADMAP п. 765], что согласуется с «не случалось» [I].

**Исход: паркуется до** строки/счётчика отказа места в `AppendWriteAddressRecord` (EBUSY) в логе игры при исполнении APR (нужно звено измерения: одна `LOGF` при отказе, умолчание 0) или до наблюдения `MT265: mode=` вместе с зависанием загрузки. Если переоткрыть: стенд без игры — буфер 768, 16 пар `mQ16-QdKv7k` + `j0+3uJMxYJY`, плечо «раскладка SDK» (=0 теряет пары 14–15) и «раскладка по мере» (=0 и =1 — 0 потерь); мутант — мера 0x20 при записи 8/12/16 (ловится плечом «по мере»).

## T141 — `34a3eb6b5`, автоматическая подложка AMM

**Код [c].** `AllocateAmmAutoDirectMemory` (`dd73d04d:src/libs/libAmpr.cpp:1259-1284`): пул `g_amm_auto_pool` пополняет только `AmmGiveDirectMemory` (`:2387-2411`); иначе каждое отображение берёт новую прямую память `KernelAllocateDirectMemory`, а `Unmap` исполняется как `KernelMunmap` (`:1438-1439`) — прямая память не возвращается. Модель (`stand_m5a.out.txt`): цикл MapAuto(16 МиБ)/Unmap при 16 ГиБ исчерпывает прямую память на 1 024-м цикле → `EAGAIN` (`:1292-1295`).

**Достижимость [c].** `AllocateAmmAutoDirectMemory` вызывается только из `ExecuteAmmMapCommand` для записей вида `MapAuto`, которые создают только `AmmCommandBufferMap` / `…WithGpuMaskId` (`:2275-2317`, NID `JEVYGhDc97M`, `ojBkmG7+CgE`). Эти NID, как и `AmmGiveDirectMemory` (`Q07J7XpvhrU`), `AmmSubmit*` (`lwS-7y3jcBI`, `NnKhlMJtIsI`, `OJf3vCckPAM`), `AmmCommandBufferUnmap` (`M-VFI2DJWQA`) — **не импортируются** ни `eboot.bin`, ни модулями `sce_module` (`imports_m5a.out.txt`). Довод TSV «путь MapAuto через `AprCommandBufferMapBegin`» неверен: `AprCommandBufferMapBegin`/`MapDirectBegin`/`MapEnd` у нас — `AppendNoOpCommand` (`:2215-2273`), подложку не выделяют. В логах `AMM submit command failed` 0 [c]. **Исход: НЕ ДЕФЕКТ (путь недостижим для ASTRO BOT).** Переоткрытие — импорт любого из названных NID другой игрой/модулем.

Замечание вне темы [I]: `AprCommandBufferMapBegin`/`MapDirectBegin` импортируются и у нас ничего не отображают; при их исполнении чтение в неотображённый VA дало бы `APR submit read failed` (EFAULT) — в трёх логах 0.

## T210 — `46900d804`, замена живого фиксированного прямого отображения

**Код [c].** `KernelMapDirectMemory` (`dd73d04d:src/kernel/memory.cpp:3325-3501`), ветка `fixed`: если диапазон не целиком Reserved — `ReplaceFixedRangeWithReserved` (`:3401`, тело `:3578-3776`): `UnmapBacking` живого вида (`:3687`), `g_physical_memory->Unmap`, затем `ReserveFixed` (`:3729`, недоступно), и только после возврата — `MapBacking` нового вида (`:3369-3372` через `:3404`). Между `:3687` и `MapBacking` диапазон недоступен; замок `g_memory_operation_mutex` прочие потоки гостя, обращающиеся к памяти напрямую, не держат ⇒ окно access violation есть [c чтением]. **Правка upstream действует только под `#if KYTY_PLATFORM == KYTY_PLATFORM_LINUX`** (диф `46900d804`), на Windows upstream оставляет тот же путь — перенос коммита нашу Windows-сборку не меняет [c].

**Исполнение [c].** Импорт `L-Q3LEjIbgA`, `BQQniolj9tQ`, `NcaWUxfMNIQ`, `cQke9UuBQOk` (munmap) есть. Логи: блоков MapDirect 7 за запуск, с `MAP_FIXED` 3 (`flags` 0x10 ×1 — `orbis_user_malloc` на 0x3_0000_0000; 0x90 ×2 — с NO_OVERWRITE, т.е. без перекрытия по построению `:3385-3387`), все на ранее не отображённые игрой диапазоны; поверх живого Direct/Flexible — 0; пар `start/len` (munmap/release) — 0; строк `reserve-fixed replace` 0 — одинаково в `sg_v_r1`, `hb_f`, `i` (`logscan_*.out.txt`, `ctx_mapblk_sg_v_r1.out.txt`). Оговорка [I]: перекрытие с диапазонами, зарегистрированными загрузчиком (не логом игры), по логу не видно; оно на старте, когда потоков гостя мало.

**Исход: паркуется до** блока `KernelMapDirectMemory` с `flags & 0x10` поверх живого Direct/Flexible диапазона в любом логе игры (детектор `logscan_m5a.py`, поле «fixed direct maps over live»). При переоткрытии исправление — своё для Windows (замена без промежутка через placeholders), не перенос `46900d804`.

## T246 — `afbb322b3`, событие-уровень без `EV_CLEAR`

**Код [c].** `GetTriggeredEvents` (`dd73d04d:src/kernel/eventQueue.cpp:94-141`): цикл `while (event.triggered)` (`:109`) отдаёт событие, у которого `reset_func` не снимает `triggered` и нет `pending_events`, копиями до `num`. Таких событий у нас один вид: `KernelAddUserEvent` (`:466-482`, `EV_ADD` без `EV_CLEAR`, `UserEventResetFunc` `:288-295` снимает только при `EV_CLEAR`). Модель (`stand_m5a.out.txt`): уровень → 8 копий при `num` 8; edge, GPU EOP (`sync.cpp:307-312` всегда снимает), VideoOut (`videoOut.cpp:330-335`) → 1. HRTimer — `EV_ONESHOT` (`:558`), AMPR-события — `EV_CLEAR` (`:579`). Других вызывающих `KernelAddEvent` нет (`sync.cpp:341`, `videoOut.cpp:465`) [c].

**Достижимость [c].** NID `4R6-OvI2cEA` (AddUserEvent), `WDszmSbWuDk`, `F6e0kwo4cnk`, `LJDwdSNTnDg`, `bBfz7kMF2Ho`, `vuae5JPNt9A`, `R74tt43xP6k` — не импортируются; внутренних вызовов `KernelAddUserEvent` нет. Логи: `user event add:` / `edge add:` / `trigger:` / `AMPR event add:` — 0 во всех трёх; `Equeue create:` 8 на лог — только очереди EOP ГП (`Gpu::GpuDevice::EopEq` ×5, `Gpu::EopEqCompute` ×2, `…ForApplication` ×1). **Исход: НЕ ДЕФЕКТ (путь недостижим для ASTRO BOT).** Переоткрытие — импорт `4R6-OvI2cEA` или строка `user event add:` в логе.

## T270 — `210d4dcd9`, `SysmoduleIsLoaded`

**Код [c].** `SysmoduleIsLoaded` (`dd73d04d:src/libs/libSysmodule.cpp:57-63`) всегда 0; `LoadModule`/`Unload` (`:25-39`) — 0 без учёта. Все четыре печатают одинаковую строку `\t id = %d` (`:28`, `:36`, `:45`, `:60`; та же форма у `HttpSetEpoll`/`HttpUnsetEpoll`, `network.cpp:2598`, `:2613`).

**Исполнение.** Импорт `fMP5NHUOaMk`, `g8cM39EUZ6o`, `eR2bZFAAU0Q` [c] (`hHrGoGoNf+s` — нет). Логи [c]: 31 строка `\t id = N` на лог, набор одинаков в трёх логах (30 разных id, 231 — дважды; `ctx_sysmodule_sg_v_r1.out.txt`). Какая функция печатала — по логу не различить [U]. Строка `id = 180` (0xB4, APP_CONTENT по нумерации PS4 [I]) стоит сразу перед `AppContentInitialize` — похоже на `LoadModule` [I]. Отличие от upstream возможно только для `IsLoaded(id)` модуля, не загруженного `LoadModule`; если игра в ответ на «не загружен» грузит модуль, в upstream появилась бы вторая строка — у нас 29 id встречаются один раз, и это не различает «LoadModule» от «IsLoaded без загрузки». Враждебно к upstream [I]: его счётчик знает только модули, загруженные `LoadModule`, и для модулей, загруженных системой при старте процесса, ответит `UNLOADED` — сам не эталон.

**Исход: паркуется до** прогона с `KYTY_PRINT_NAMES=1`, где за строкой `Sysmodule::Sysmodule::SysmoduleIsLoaded()` идёт `\t id = X`, а X раньше не передавался в `SysmoduleLoadModule`, и до довода о составе предзагруженных модулей консоли.

## T271 — `62643c342`, `ENTITLEMENT_UPDATE`

**Код [c].** `SystemServiceReceiveEvent` (`dd73d04d:src/libs/libSystemService.cpp:146-157`) всегда `NO_EVENT`; `GetStatus` (`:159-170`) — `event_num` 0. Ответы согласованы между собой. `AppContentInitialize` (`libAppContent.cpp:81-100`) ничего не ставит в очередь.

**Исполнение.** Импорт `656LMQSrg6U`, `rPo6tV8D9bM`, `R9lA82OraNs` [c]. `AppContentInitialize` исполняется: 1 блок `init_param`/`boot_param`/`title_id = PPSA21564` в `sg_v_r1` (`ctx_appcontent_sg_v_r1.out.txt`). Вызовы `ReceiveEvent`/`GetStatus` своих строк не имеют — [U]. Что консоль после `AppContentInitialize` кладёт `0x10000003` — довод только upstream, без источника SDK [U]; реакция ASTRO BOT (проверка прав на доп. контент) — [U].

**Исход: паркуется до** (1) свидетельства консоли/SDK, что событие приходит, и (2) наблюдаемого следствия в игре (контент, зависящий от права, не появляется; или вызов `ReceiveEvent` в цикле — `KYTY_PRINT_NAMES`).

## Враждебная проверка выводов

- «Путь AMPR не исполнялся» опирается на 2 лога MS1 (`sg_v_r1`, `i`) и на то, что `MT265` печатается при первом корректном Resolve; некорректный Resolve и команды без файлов (`WriteAddress`, `WaitOn*`, счётчики) этим не исключены — поэтому T159/T309 «паркуется», а не «НЕ ДЕФЕКТ (недостижим)».
- «Недостижим» у T141 и T246 опирается на отсутствие импорта NID в `eboot.bin` и двух `prx`; `sceKernelDlsym` по имени не проверялся [I] — подкреплено 0 строк соответствующих `LOGF` в трёх логах.
- Ни один upstream-ответ не принят за эталон: T210 — правка только для Linux; T270 — счётчик upstream ошибается для предзагруженных модулей; T271 — без источника; T309 — тест upstream на NID, которого игра не импортирует.

## Файлы и sha256

Каталог: `docs/track-m/m5a/hle2/`

| файл | sha256 |
|---|---|
| `imports_m5a.py` | `ab9eaaf3ba26414b295bba43f09246168d542f664b06ebc0e0a072dce0115222` |
| `imports_m5a.out.txt` | `9ecf8d576182031ad30d22c8be6c1080e2b213e0c2bc3f206cb6e9789d5286b2` |
| `logscan_m5a.py` | `aa2c204f93a6230c9a4011a4a40b7fd549d896269b97842b3dd8d1ce3264bd47` |
| `logscan_sg_v_r1.out.txt` | `4f2a92f355e4b14a68426b2ecee5df5e1c558c4a12449f4a7b201b53cb880225` |
| `logscan_hb_f.out.txt` | `5e8b573eab943ed48dcea1fffa8b4705afff20868009f1195d77d816c915e473` |
| `logscan_i.out.txt` | `9157f2c43e9e31c5adcfb74912b8e53251fd4386ece06adf5265320f4e603b43` |
| `ctx_m5a.py` | `f96cc71b72128e81fcd6249a4f746f99105468f18b46fbf484e8a49b00eb9eae` |
| `ctx_sysmodule_sg_v_r1.out.txt` | `495b6dc9e091e90783e2537e68ef02551fb2dd9f17759e31bdeb983c994ba314` |
| `ctx_mapblk_sg_v_r1.out.txt` | `e369058afc276985de2b1eac1992a228a33c5e9cbdf5eb39c479467a9cf13cc4` |
| `ctx_appcontent_sg_v_r1.out.txt` | `ca557c4cb263777fe0228060b2d575ee5dd9ffa74ff86dedac547a6b6f5ba7ec` |
| `ctx_type_sg_v_r1.out.txt` | `419bf46c02c7b9d22628539b5ed2f146b983e16a286d72551d2334427915a473` |
| `stand_m5a.py` | `a047e17e529e1f09908d33fbd80bbd51a101f0fd6dbccbdb43e79c1215edc671` |
| `stand_m5a.out.txt` | `b5ba7ea0e431bd099910402299f70f35008ffdca32082363a70f2d9e93f57a88` |
