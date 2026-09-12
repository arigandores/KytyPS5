# Сессия 50 — CPU Sky Garden, ThinLTO и проверки привязок

2026-09-12…13. База `9cfdb7d`, ветка `merge-upstream`. Код сохранён в **ef26182**
(WIP относительно цели FPS). Сессия завершена по указанию пользователя после проверки
Vulkan. **Около 60 FPS не достигнуты; проверенный пролёт остаётся примерно 14–15 FPS.**
Push не выполнялся. Изменения CMASK/GC предыдущей сессии сохранены.

## Результат и установленная сборка

- Основной `C:/kyty/build` переведён на **ThinLTO** (`CMAKE_INTERPROCEDURAL_OPTIMIZATION=ON`,
  `-flto=thin`). Эта настройка уже используется в release CI. Обновлён внешний
  `C:/kyty/build_local.cmd`: `configure` теперь сохраняет LTO. Изолированная пробная
  сборка `C:/kyty/build_lto` оставлена как артефакт, не является основным build-каталогом.
- В одной тёплой паре без подробных таймеров ThinLTO дал около **4–5% FPS** при близком
  числе draw. Это не серия, доказывающая устойчивый выигрыш на всех сценах.
- Включены быстрый transient hash параметров пайплайна и повторное использование
  завершённых descriptor sets. Самостоятельный выигрыш FPS каждого из них не выделен.
- `KYTY_SRT_NATIVE` остаётся **default0**: прямой native SRT был дороже в игровой паре.
- Новый `KYTY_CBUFFER_DIRECT_COPY` тоже **default0**. Корректность проверена, но
  сравнение FPS внутри одного запуска прервалось из-за зависания входа до целевого уровня.
- Прямая проверка диапазона битовой маски отклонена: отдельного игрового выигрыша нет.
  Её код и тесты восстановлены к HEAD; `s50/rejected_range_query.patch` — архив эксперимента.
- Закрепление процесса за отдельным CCD не применяется: преимущество не установлено.
- Игра закрыта, последняя игровая проверка завершилась **exit0**. Новые запуски после
  просьбы пользователя завершить сессию не выполнялись.

Установлены одинаковые exe в `C:/kyty/build/install` и папке игры. Итоговый SHA256:
**6A2932AD491FEE059A2296E13C61B7878C365FDC3CEDA7FA2AC5EB9502EF66AC**.
Встроенная метка `9cfdb7d-dirty` оставлена: после коммита код ради одной метки не пересобирался.
Seed не обновлялся. Последние запуски восстанавливали локальные **715/715 рецептов, 0 skipped**;
это не новый распространяемый seed и не проверка холодного восстановления всего маршрута.

## Код

1. `pipelineCache`: 158 packed-байт `PipelineStaticParameters` хешируются XXH3 вместо
   последовательной цепочки побайтовых Mix. Побайтовое сравнение ключей сохранено.
   Сериализация pipeline recipe и постоянные shader keys не менялись.
   Контроль — `KYTY_PIPELINE_FAST_HASH=0`.
2. `DescriptorHeap`: выделенные sets сохраняются вместе с retired pool. Cursors
   сбрасываются только после завершения его timeline tick; каждый последующий bind
   заново получает все descriptor writes. При смене layouts полный завершённый pool,
   из которого в новой активации ещё ничего не выдано, сбрасывается штатно.
   Лимит1024 sets на pool сохраняет ограниченный объём хранения даже на драйвере,
   допускающем over-allocation. Контроль — `KYTY_DESCRIPTOR_REUSE=0`.
   `KYTY_DESCRIPTOR_STATS=1` добавляет итоговый лог при вызове деструктора; игровые
   запуски такого лога не дали, поэтому общего числа игровых reuse-hits здесь нет.
3. Оставшиеся argument dumps четырёх AGC patch helpers переведены с LOGF на LOGV.
   Запись кнопок/осей по умолчанию выключена: удалён принудительный `KYTY_DBG_INPUT`.
   Ошибки и предупреждения Vulkan не фильтровались. Первый запуск старого exe ещё
   содержал старое логирование ввода; в base2 и последующих сборках его уже нет.
4. Опциональный прямой aligned-copy путь констант: read-only, не formatted, dword-aligned
   guest address, флаг aligned-copy и неподходящее выравнивание базы. Только при
   отсутствии GPU-dirty страниц **и** точных GPU-dirty байтов данные копируются сразу
   в конечный stream buffer. Исходный owner получает Touch для GC/prefetch lifetime;
   заменённый/coalesced id возвращает обычный путь. CPU dirtiness не потребляется,
   последующие BDA/descriptor обращения сохраняют прежнюю синхронизацию.
   GPU-owned данные проходят прежние ObtainBuffer/GPU copy. Содержимое читается заново.
   `KYTY_CBUFFER_COPY_GATE=<file>` читает0/1 раз в кадр для сравнения внутри запуска;
   переключения пишутся как `ConstantCopyGate`. По умолчанию файла и fast path нет.
5. `KYTY_QUEUE_TRACE=1`: последние512 событий до/после `queue.submit`, включая master,
   tick, waits, signals, stages и результат API. При ожидании дольше2с выводятся
   requested/known/current timeline и CPU-история. Это **не подтверждение исполнения GPU**.
   Дополнительных запросов к драйверу для этой истории нет; NV данные по-прежнему
   запрашиваются только после DeviceLost. Режим выключен по умолчанию и ещё не поймал hang.

## Полный CPU-профиль

Вход в уровень выполнял пользователь; F1 не нажимали, новые RenderDoc-захваты не делались.
Сравнивались +120/+420/+720 от первого MeshRestart, по300 present. В этих трёх окнах
семплер выключен; затем включался на65с через файл-gate, после чего игра закрывалась.
Запись960x540 и NV checkpoints включены одинаково.

`base2`: Mesh15633, финал17533, exit0; Hash0, NativeSRT0, StateCache0, старый heap.
`on_full`: Mesh16063, финал17972, exit0; Hash1, Reuse1, NativeSRT1, StateCache1.

| Окно | Base FPS | On FPS | Base draw median | On draw median |
|---|---:|---:|---:|---:|
|+120|11.904|12.353|5929|6009|
|+420|12.686|13.064|5879|5890|
|+720|12.330|12.668|6099.5|6187|

CPU/draw14.091/13.671/13.377 →13.548/13.256/13.010мкс. Новых shader events и freeze scopes
в этих окнах нет. Первый интервал: CPU GPU-thread82.35→81.87мс, GPU22.71→22.69мс;
draw emit6.60→4.71мс, commit6.75→6.57мс. **SRT Evaluate11.24→12.45мс**: native SRT
не оправдал включения по умолчанию. Нельзя приписать всей группе изменений одно причинное число FPS.

В полной диагностике NowNs занимает~17–18% семплов. Вложенные фазы не складывать.
В отдельном lite-профиле (`range_lite`, уже отклонённый эксперимент масок): TrackingSpinLock12.1%,
ProtectMappedUnlocked7.5%, backing transfers6.4%, ReadShaderLiveMemory4.8%, CommitBindings4.1%.
Семплер меняет темп и contention; проценты не являются независимым замером времени ожидания lock.
На тяжёлом кадре базы:~67500 ObtainBuffer,~57100 buffer bindings и~9380 aligned constant copies
(~918KiB). Остаток распределён между SRT, привязками, проверками/защитой памяти и множеством draw.

GPU top-list не обнаружил одного шейдера, объясняющего всю просадку. В первом окне:
PS3d705c1b57adec00/VS2aacf97ccc25e636~1.18мс на~192draw;
CS56a15431999c5a2d~0.73мс; присутствуют uploads, барьеры и многие другие draw.
Top-list обрезается, поэтому это не полный разбор всех21–23мс GPU.

## ThinLTO, affinity и отклонённая маска

Обе версии: SRT0, StateCache1, Hash1, Reuse1; lite counters, видео, без семплера и NV markers.
В каждом окне0 новых shader events/freeze scopes.

| Окно | Без LTO FPS | LTO FPS | Без LTO draw | LTO draw | CPU/draw без→с LTO, мкс |
|---|---:|---:|---:|---:|---:|
|+120|13.616|14.331|5713.5|5743|12.283→11.753|
|+420|14.331|14.963|5567|5679.5|12.071→11.568|
|+720|14.029|14.624|5816|5944.5|11.727→11.229|

CPU GPU-thread~65–68мс, GPU~21.2–21.4мс. Одна пара, разная траектория/частицы и нагрев;
не называть это устойчивой серией. Это измерение без подробных часов, но с записью и counters.

Windows сообщил Ryzen9 9955HX3D, L3 mask0xFFFF=96MiB и0xFFFF0000=32MiB.
После посадки: all15.845 /96MiB16.275 /all16.743 /32MiB16.437 /all16.527fps.
Медианы draw5374/5315.5/5002/5126/5184 различаются; преимущество affinity не установлено.
Исходная маска0xFFFFFFFF восстановлена перед закрытием. Системные настройки не менялись.

`range_lite`:14.153/14.752/14.424fps — прирост не установлен. Его exhaustive bool-oracle
и memory-tracker тесты проходили, но правка полностью удалена, а не включена за счёт одной синтетики.

## Зависания и игровые проверки

- `base`: старый exe завис на входе, present15329, до MeshRestart.
  `hang_base.dmp.dmp`, `hang_base.dmp.stacks.txt`, `before.map`.
- `direct_sweep`: повтор того же симптома, present15287, до MeshRestart; exit1 после watchdog.
  `hang_direct_sweep.dmp`, `.stacks.txt`, `direct_sweep.map`.
  FPS-сравнение direct-copy не состоялось. Наличие такого hang на исходном exe не доказывает
  причину, но не позволяет объявлять новый copy path установленной причиной второго эпизода.
- В обоих стэках GuestGpu ждёт FramePool::Acquire/MasterSemaphore::Wait; поток priority
  operations также ждёт master. Драйвер не сбрасывали. Watchdog не запрашивает GPU:
  после12с без кадров снимает CPU dump/stacks и завершает тот же процесс.
  **Причина hang не установлена и не исправлена.**
- `validate`: ShaderPreparation715/715, Mesh15620, финал15920, штатное закрытие exit0.
  Обычная Vulkan + `VK_LAYER_VALIDATE_SYNC=1`: **0 ошибок, 0 sync hazards,10 warnings**
  unused fragment output Location1. Проверены запуск/маршрут до уровня и первые300 кадров
  пролёта; не весь уровень и не вся игра. Fast copy был явно включён, native SRT выключен.
  Проверялся exe7C97A133…; позже добавлена выключенная по умолчанию история очереди и
  fast-copy default изменён на0. Для очереди отдельно прошёл SchedulerTimeline с trace1;
  для итогового default0 и opt-in1 повторно прошёл direct-copy GPU test. Новый игровой
  запуск итогового exe после просьбы завершить сессию не выполнялся.

## Тесты и видео

DescriptorHeap:1100 sets до завершения GPU, уникальность in-flight handles, reuse после Finish,
смена layout и возврат. ON allocation_calls128/resets1/reused324, OFF139/3/0.
Есть warning о пробе1536 sampler descriptors при budget1024; NVIDIA допускает over-allocation.
Первый вариант теста с64sets не исчерпывал pool и был исправлен.

DirectConstantCopy проходит ON/OFF/default под Vulkan+sync: полный aligned view, GPU readback,
смена CPU данных, coalesced owner, GPU-written source, сохранение GPU dirty state.
Counters подтверждают отсутствие ObtainBuffer в eligible direct path и один вызов в контроле.
Начальный тест ошибочно пытался Invalidate stream buffer; исправлен на поддержанный GPU-copy
в download buffer. Это исправление тестового harness, не скрытое падение runtime.

Пройдены фокусные descriptor-heap, sparse-mrt, cmask-clear, readonly-depth-reuse, image-view-cache,
shader-data-storage, push-constant-bank, BDA-dirty, SchedulerTimeline; соответствующие GPU
прогоны выполнены с Vulkan+sync. ResourceMaterialization/native+SRT_VERIFY прошёл.
Полная shader/GPU suite не запускалась и не объявляется чистой; старые storage-mip/partial-page
readback/IMAGE_SAMPLE_C этой сессией не закрыты.

| Завершённое видео | Кадров | Decode errors / global A-B-A candidates |
|---|---:|---:|
|rec_base2.mp4|17543|0 /0|
|rec_on_full.mp4|17977|0 /0|
|rec_lto_lite.mp4|18834|0 /0|
|rec_nolto_lite.mp4|17842|0 /0|
|rec_range_lite.mp4|17443|0 /0|
|rec_validate.mp4|15935|0 /0|

Контактные листы base2/on_full/validate просмотрены. Все изображения для обзора извлечены
из видео. Глобальный сканер не доказывает отсутствие локальных дефектов. Необычные элементы
текста/HUD около посадки видны и в контроле; их происхождение здесь не исследовалось.
Два прерванных hang-видео не объявляются проверенными.

## Продолжение

Пользователь завершил сессию; не возобновлять игровые прогоны без новой задачи.
Для продолжения FPS: сначала закончить same-run direct-copy sweep (`launch_run.py direct_sweep…`,
`measure_run.py`, `affinity_summary.py` поддерживает copy phases). Опция пока default0.
Для следующего hang использовать `KYTY_QUEUE_TRACE=1` и актуальный linker map с watchdog;
CPU submit history позволит проверить submitted/future waits, но не заменяет GPU completion data.
Основной остаток~65мс CPU при~6000draw; GPU тоже выше16.7мс. **60FPS не обещаны и не достигнуты.**

Артефакты/скрипты/логи/maps: `C:/kyty/s50`; итоговый отчёт также `C:/kyty/s50/REPORT.md`.
По просьбе пользователя в рабочий `INDEX.md` добавлен локальный
`docs/rdna2-shader-instruction-set-architecture.pdf`: AMD RDNA2 ISA Reference Guide,
30.11.2020,291страница. Файл проверен, ссылка помещена в раздел «Документы».
Рабочие игровые тесты сохраняли `KYTY_ASYNC_COPY_GPU_WAIT=0` из сессии49; это не доказанный
фикс hang, глобальный default этой опции не менялся. Старые cache/seed/RenderDoc каталоги сохранены.
Удаления PNG внутри `3rdparty/nlohmann_json` не затронуты и в коммиты не включены.
