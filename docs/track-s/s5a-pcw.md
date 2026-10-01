# Трек S, звено S5a — код S-pcw под `KYTY_S_PCW`, стенд `KYTY_S_PCW_FORCE_MS`, `KYTY_DUMP_GCN=2` (`HPP-316`)

Автор — Emu Engineer. Критерий — `ROADMAP.md` «СЕССИЯ 122» п. 241(з)(1)–(4) (`20b39318`), написан лидом до кода. Код — коммит
**`e11a297b`** в `main` (родитель `ae704c5d`; база кода — `main` после F2a `ba3be480`). **WIP в смысле правил роли:** сборка есть,
не установлена, дыма нет — игру звено не запускает (прогоны — S6, `HPP-318`). Своё звено не принимаю.

Ссылки на код — `<коммит>:<путь>:<строка>`, якорь — целая строка, контроль — строка +1; все 41 проверены скриптом
`C:/kyty/s288/s5a/refs_s5a.py` → `refs_s5a.out.txt` (`ALL OK`). Ниже `pc` = `src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp`,
`ph` = `…/pipelineCache.h`.

## 1. Что сделано

| ручка | умолчание | при включении |
|---|---|---|
| `KYTY_S_PCW` | 0 (любое значение, кроме ровно `1`) — прежний путь | запись кэша драйвера и `pipelines.bin` — потоком записи вне `m_mutex` и вне GuestGpu |
| `KYTY_S_PCW_FORCE_MS=<мс>` | выкл. (не задана или 0) | поток записи пишет кэш драйвера каждые `<мс>` без условия роста, путём, выбранным `KYTY_S_PCW`; строка с ` forced` |
| `KYTY_DUMP_GCN=2` | как прежде (`=1` — дамп при первом использовании) | дополнительно — дамп сырого GCN каждого шейдера, зарегистрированного AGC |

Все три читаются один раз на процесс (статические лямбды): `e11a297b:pc:275` (якорь «bool SPcwMode() {», +1 «static const bool mode = [] {»),
`e11a297b:pc:286` («uint32_t SPcwForceMs() {», +1 «static const uint32_t ms = [] {»), `e11a297b:pc:1296` («bool DumpGcnAtRegistration() {»,
+1 «static const bool enabled = [] {»). Строка значения на старте — в конструкторе `PipelineCache`: `e11a297b:pc:4618`
(«LOGF("S-pcw: KYTY_S_PCW=%d KYTY_S_PCW_FORCE_MS=%u\n", SPcwMode() ? 1 : 0, SPcwForceMs());», +1 «if (SPcwMode() || SPcwForceMs() != 0) {»).

## 2. Критерий п. 241(з)(1) по пунктам

**(1а) `getPipelineCacheData` и файл кэша драйвера — не под `m_mutex` и не на GuestGpu.** При `=1` сайты запроса только ставят атомарный
флаг: `MaybeWriteDriverCache` (вызывается в задаче воркера и на синхронных путях GuestGpu — сайты `a2849aec:pc:4655`, `:5362`, `:5399`,
`:5681` по старой нумерации) — `e11a297b:pc:4746` («// S-pcw: the same 20 s period; the write goes to the writer thread (one flag: requests
merge).», +1 «m_pcw_want_driver.store(true);»); `FinishPreparation` (главный поток, до старта гостя) — `e11a297b:pc:6311` («// S-pcw: the same
condition; the writer thread writes it, off m_mutex.», +1 «if (m_precache_completed.load() > m_precache_skipped.load() && m_driver_cache != nullptr) {»).
Пишет поток `PcwLoop` (`e11a297b:pc:6102`, «void PipelineCache::PcwLoop() {», +1 «#if defined(_WIN32)»), вызов `WriteDriverCache` без
`m_mutex` — `e11a297b:pc:6138` («const bool saved = WriteDriverCache(forced ? " forced" : "");», +1 «m_pcw_gen.fetch_add(1);»).
`WriteDriverCache` (`e11a297b:pc:4840`, «bool PipelineCache::WriteDriverCache(const char* suffix) {», +1 «if (m_driver_cache == nullptr) {») не
читает ничего под `m_mutex`: только `m_driver_cache` (пишется в конструкторе до старта потока и в `Save()` после его `join`),
`m_driver_cache_path` (неизменен после конструктора), `m_graphics`.

**(1б) отдельный поток, ≤ 1 записи в полёте, слияние, период 20 с.** Один поток (`PcwStart`, `e11a297b:pc:6077`, «void PipelineCache::PcwStart() {»,
+1 «m_pcw_thread = std::thread([this] { PcwLoop(); });») — одна запись в полёте по построению. Опрос раз в 100 мс
(`e11a297b:pc:6111`, «m_pcw_cv.wait_for(lock, std::chrono::milliseconds(100), [this] { return m_pcw_stop; });», +1 «if (m_pcw_stop) {»);
запросы между опросами сливаются в один (`exchange(false)` флага, `e11a297b:pc:6134`, «if (m_pcw_want_driver.exchange(false) || forced) {»,
+1 «// Every creation counted before this load is in the data read below.»). Период — прежнее условие `now - m_driver_cache_saved_us < 20 000 000`
на сайте запроса, тот же сброс `m_driver_cache_saved_us = now` (задержка записи после запроса — ≤ 100 мс опроса). При `=1` и в режиме
стенда пути `=0` других писателей файла кэша драйвера нет: при `=1` — только поток записи и `Save()` после `join`; при `=0` все записи
под `m_mutex`.

**(1в) та же строка.** `e11a297b:pc:4892` («PipelineCacheLog("Vulkan pipeline cache: saved {} bytes to {} ({} us){}", payload.size(),», +1
«Common::PathToString(m_driver_cache_path), HostMicros() - write_begin, suffix);») — суффикс пуст на всех путях, кроме стенда, — строка
байт в байт прежняя; строки `save failed` / `failed to write` не менялись.

**(1г) запись рецептов — если под `m_mutex` и цена ≥ 10 мс.** Под `m_mutex` — да: `WriteRecipes` (`a2849aec:pc:5934`, «bool
PipelineCache::WriteRecipes() {», +1 «if (m_recipes_path.empty() || m_recipe_count == 0) {») зовётся из `MaybeWriteRecipes` внутри
`MaybeWriteDriverCache`. **Цены в логе нет:** строка `PipelinePrecache: saved N recipes (M bytes)` без времени. В 12 логах с. 142
(`C:/kyty/s142/log_c142_01…10.txt`, `log_v142.txt`, `log_w142.txt`; sha256 каждого — `C:/kyty/s288/s5a/scan_saves.out.txt`, скрипт
`scan_saves.py`, поток в двоичном режиме) — 23 строки записи рецептов, размер до **19 810 316 байт** (`c142_10`), 26 строк записи кэша
драйвера, 70 191–138 213 мкс. **Число [c-bench, не игра]:** офлайн-стенд того же шаблона на том же томе (копия тела, `.tmp`, одна запись,
сброс на диск, переименование; `C:/kyty/s288/s5a/bench_recipes.py`, 7 повторов на 19 810 316 байт) — медиана **18 102 мкс** (17 561–20 676)
≥ 10 мс → запись рецептов перенесена так же. Игровое число даст S6: при `=1` строка рецептов несёт время записи —
`e11a297b:pc:6209` («LOGF("PipelinePrecache: saved %u recipes (%zu bytes) (%" PRIu64 " us)\n", count, payload.size(),», +1 «HostMicros() - write_begin);»).
Как: поток записи держит `m_mutex` только на копию записей, добавленных с прошлой копии (`PcwWriteRecipes`, `e11a297b:pc:6152`, «void
PipelineCache::PcwWriteRecipes() {», +1 «std::string signature;»); в одной «эпохе» `m_recipes` только дописывается (`AppendRecipe`), эпоха
растёт при перестройке `PrecachePipelines` (`e11a297b:pc:6683`, «m_recipes_epoch++; // S-pcw: m_recipes is rebuilt, the writer's copy is stale»,
+1 «m_recipe_hashes.clear();») — тогда копия полная (один раз за процесс, ≈ 20 МБ). Удержание печатается строкой
`AvTrace: pcw recipes copied=… count=… wait_us=…` (`e11a297b:pc:6178`, +1 «HostMicros() - hold_begin);») — граница любого ожидания
GuestGpu из-за неё. Файл пишется как в `WriteRecipes` (та же сигнатура, тот же порядок полей).

**(1д) `Save()` при выходе ждёт поток и пишет последнее.** `e11a297b:pc:4825` («PcwStop();», +1 «Common::LockGuard lock(m_mutex);») — `join`
**до** взятия `m_mutex` (стенд пути `=0` берёт `m_mutex` в потоке); затем под `m_mutex` — запись того, что поток не записал:
`e11a297b:pc:4827` («if (m_recipes_unsaved != 0 && !PcwRecipesSaved()) {», +1 «WriteRecipes();»), `e11a297b:pc:4833` («if ((m_driver_cache_unsaved != 0 ||
m_driver_cache_saved_us == 0) && !PcwDriverSaved()) {», +1 «WriteDriverCache();»). `vkDestroyPipelineCache` — после `join`. Вызовы `Save()` —
`WindowRun` (поток окна, `src/graphics/presentation/window/window.cpp:957`) и деструктор; ни один не держит `m_mutex`.

**(1е) безопасность `vkGetPipelineCacheData` параллельно созданию на том же `VkPipelineCache`.** Кэш создаётся с `flags = 0`:
`e11a297b:pc:4703` («vk::PipelineCacheCreateInfo create {};», +1 «create.initialDataSize = initial_data.size();») — без
`VK_PIPELINE_CACHE_CREATE_EXTERNALLY_SYNCHRONIZED_BIT`. Спецификация (реестр Vulkan из SDK 1.4.357 на машине:
`C:/VulkanSDK/1.4.357.0/share/vulkan/registry/vk.xml` и `validusage.json`, «from git branch: github-main commit:
d184375dcc5da2b06ca375a8d7d1f9d21ca64a76», 2026-07-17): у `vkCreateGraphicsPipelines` и `vkCreateComputePipelines` параметр `pipelineCache`
— `externsync="maybe"` (`vk.xml:15149`, `:15167`), условие — `VUID-vkCreateGraphicsPipelines-pipelineCache-02876` /
`VUID-vkCreateComputePipelines-pipelineCache-02873`: «If pipelineCache was created with VK_PIPELINE_CACHE_CREATE_EXTERNALLY_SYNCHRONIZED_BIT,
host access to pipelineCache must be externally synchronized» — у нас бит не задан, внешняя синхронизация не требуется; у
`vkGetPipelineCacheData` (`vk.xml:15102`) ни одного параметра с `externsync`; `vkDestroyPipelineCache` — `externsync="true"`
(`vk.xml:15096`) — поэтому уничтожение только после `join`. Это говорит о корректности, не о цене: внутренний замок драйвера может
задерживать создание на время чтения (риск априора лида п. 241(м)) — для этого строка (4) ниже.

## 3. Стенд п. 241(з)(2)

`KYTY_S_PCW_FORCE_MS=<мс>`: поток записи стартует и при `KYTY_S_PCW=0`. Таймер — в том же цикле (`next_forced`), без условия роста.
Путь 0 — запись производства под `m_mutex` в потоке записи (не GuestGpu; моделирует сайт задачи воркера `:5362`), сброс
`m_driver_cache_unsaved` при успехе: `e11a297b:pc:6125` («if (WriteDriverCache(" forced")) {», +1 «m_driver_cache_unsaved = 0;»). Путь 1 — тот
же вызов, что и для запроса, суффикс ` forced` (`:6138`). Строка: `Vulkan pipeline cache: saved … (N us) forced`. Обычные записи по росту
идут дальше при обоих путях (стенд добавляет записи, не заменяет).

## 4. `KYTY_DUMP_GCN=2` — п. 241(з)(3)

`TraceShaderRegistration` (зовётся `AgcCreateShader`, `src/libs/agc.cpp:687`, после `ShaderMapUserData`) первой строкой пишет дамп
(`e11a297b:pc:6230`, «if (DumpGcnAtRegistration()) {», +1 «DumpShaderGcnRegistered(static_cast<uint8_t>(mapped.type), mapped.hash,
const_cast<const void*>(header.code),»): файл `<папка логов шейдеров>/gcn/reg/<тип>_<хэш16>.bin` (тип по `Prospero::ShaderBinaryType`: `cs ps gs hs
gsf hsf gsb hsb fs`, иначе `t<n>`), один на (тип, хэш), строка `GcnDumpReg: type=… hash=… words=…` (`e11a297b:pc:1304`). Хэш — тот же
`ShaderComputeHash`, что ключ первого использования. Дамп первого использования при `=2` остаётся (старый читатель включает всё, кроме
`0`); `=1` — без изменений. **Не покрыто:** результаты слияния половин (`AgcUnknownFuseShaderHalves`) регистрацию не проходят — в `reg/` их
половины, не слитый код.

## 5. Пункт (4): ожидания GuestGpu, `src/graphics/shader/**`, тесты, дифф

- **Новых ожиданий GuestGpu в коде — 0:** сайты запроса на GuestGpu — `atomic::store` и `fetch_add`, без замка. Косвенные — два, оба со
  строкой `AvTrace` и `wait_us` (при `KYTY_AV_TRACE=1`): (а) копия рецептов под `m_mutex` в потоке записи — `AvTrace: pcw recipes … wait_us`
  (удержание); (б) синхронное создание, перекрывшееся с записью драйвера (`m_pcw_gen` нечётен во время `WriteDriverCache`) —
  `AvTrace: pcw overlap gfx|cs id0=… id1=… wait_us=<время создания> gen0=… gen1=…` (`e11a297b:pc:6218`; сайты `e11a297b:pc:5487` gfx, `:5773`
  cs). Ожидания воркера на `wait_for` (RC6) не новые и не менялись. `Save()` ждёт поток на потоке окна, не GuestGpu.
- **`src/graphics/shader/**` — 0 правок;** подпись транслятора сборки **`KytySC3:846a041a4d4902a2afc2ca8f1d7067c5d2ae982b`** (+ суффиксы режима
  во время работы, `:robust:ftz…`, `:fixb26` при `KYTY_FIX_B26=1`) — та же, что у сборки F2a (`5821482a`); `pipelineCache.*` во вход хэша не
  входит (`src/generate_version.cmake`, `CMakeLists.txt:155–156`). ≠ `699c1e4b…` у установленной `9235a7ac` — от F2a, не от S5a: первые
  входы бинаря звена холодные по каталогу трансляций при любых ручках.
- **Тесты `shader_cfg_tests`** (`build_tests.cmd`, sha256 бинаря тестов `bf4fa7f0…5fafe0da`): A — ручки не заданы, B — `KYTY_S_PCW=1
  KYTY_S_PCW_FORCE_MS=15000 KYTY_DUMP_GCN=2`; 127 тестов в обоих, падает 1 (`TestNewShaderRecompilerPixelImageSampleLodSelection`, Б11, 2 проверки
  `IMAGE_SAMPLE_C`), логи A и B байт в байт равны друг другу и логу F2a `cfgtests_fix0.log` (sha256 `5a60758a…2f8f3f`). Падений при ручках
  не больше, чем при 0. Оговорка: тесты `PipelineCache` и поток записи не исполняют — это проверка «не сломал соседей», не кода звена.
- **Дифф:** `git diff ba3be480 e11a297b -- src/` и `git diff ae704c5d e11a297b` — только `pipelineCache.cpp` (+281/−9) и `pipelineCache.h`
  (+29/−1), 310 вставок, 10 удалений.
- **`check_gate_order.py`** (`C:/kyty/s136/step3/`) — `GATE ORDER: clean`; гейты и ручки `gates.h` не трогались (новые имена — переменные
  окружения, не `Gate`/`Knob`).

## 6. Флаги и состояние: установка, снятие, выходы

| состояние | установка | снятие / чтение | выходы без снятия и довод |
|---|---|---|---|
| `m_pcw_thread` (`e11a297b:ph:331`) | `PcwStart` `:6077` — только конструктор, при `=1` или стенде | `join` в `PcwStop` `:6081` из `Save()` `:4825` | деструктор всегда зовёт `Save()` → `join` до разрушения члена; повторный `Save()` — `joinable()` ложно, возврат |
| `m_pcw_stop` | `PcwStop` `:6087` под `m_pcw_mutex` | не снимается | перезапуска нет (`PcwStart` только в конструкторе) |
| `m_pcw_want_driver` | `:4746` (`MaybeWriteDriverCache`), `:6311` (`FinishPreparation`) | `exchange(false)` `:6134` | после остановки потока флаг может остаться — его никто не читает; `Save()` решает по счётчикам, не по флагу |
| `m_pcw_want_recipes` | `:6025` (`MaybeWriteRecipes`) | `exchange(false)` `:6131` | то же |
| `m_pcw_gen` (нечётен = запись в полёте) | `fetch_add` `:6137` | `fetch_add` `:6139` | между ними один вызов `WriteDriverCache`, у которого все выходы — `return` (без `EXIT_*` и исключений) → всегда чётен после |
| `m_pcw_created` | `fetch_add` `:4739`, монотонен, только `=1` | читается `:6136`, `PcwDriverSaved` | — |
| `m_pcw_saved_created`, `m_pcw_saved_any`, `m_pcw_rec_body`, `m_pcw_rec_epoch`, `m_pcw_rec_saved_*` | только поток записи (`:6141`, `:6164`, `:6211`) | `Save()` после `join` (happens-before через `join`) | ранние `return` в `PcwWriteRecipes` (пусто, ничего нового, ошибка каталога или записи) — метки «записано» ставятся только при успехе |
| `m_recipes_epoch` (`e11a297b:ph:361`) | `++` `:6683` под `m_mutex` (при обоих значениях; при `=0` не читается) | `PcwWriteRecipes` и `PcwRecipesSaved` под `m_mutex` | — |

## 7. Что меняется при `=0` и при `=1` (для S3/S6)

- **`=0`, стенд выкл.:** поведение прежнее; потока нет. Отличия от `ba3be480`: одна новая строка лога на старте `S-pcw: KYTY_S_PCW=0
  KYTY_S_PCW_FORCE_MS=0` (требование критерия «строка лога значения на старте»); проверки статических булевых; `m_recipes_epoch++` (не
  читается). Строки записей и порядок вызовов не менялись.
- **`=1`:** строка рецептов `PipelinePrecache: saved N recipes (M bytes) (K us)` (скорер — по префиксу); при стенде — ` forced` в конце строки
  кэша драйвера; новые строки `AvTrace: pcw recipes …`, `AvTrace: pcw overlap …` (только с `KYTY_AV_TRACE=1`); `FinishPreparation` больше не
  ждёт записи (запись — потоком, ≤ 100 мс позже); память — копия тела рецептов (до ≈ 20 МБ); поток записи — `THREAD_PRIORITY_BELOW_NORMAL`,
  как воркеры. Ручки — в семействе `KYTY_S_*`/`KYTY_DUMP_*`, которое скорер сверяет с печатью (п. 241(в)(6)).

## 8. Сборка

`cmd //c "C:\kyty\build_local.cmd"` (без замка), предупреждений в новом коде 0 (одно старое `pipelineCache.cpp:401`, `-Wreturn-type` в
функции полигонального режима, было до звена). Бинарь **sha256 `7e2c0a3b8edfff3d43de3eb5b54dd4c1f728253a6a361511a4d87e04176e58d1`**
(sha8 **`7e2c0a3b`**), копия `C:/kyty/s288/bin/kyty_emulator_7e2c0a3b.exe` (sha256 совпадает). Установленный бинарь не тронут
(`ps5 em/kyty_emulator.exe` — `9235a7ac…`).

## 9. Вопросы лиду (решения — у лида)

1. Строка `S-pcw:` печатается и при `=0` — по букве «строка лога значения на старте». Если «байт в байт» распространяется на лог —
   вариант исполнителя: печатать только при `=1` или заданном стенде.
2. Стенд пути 0 держит `m_mutex` в потоке записи (как сайт воркера `:5362`), а не на GuestGpu (`:5399`): положительный контроль (5)(а)
   видит ожидание GuestGpu на `m_mutex`, но не запись на самом GuestGpu. Если нужен и второй — вариант исполнителя: флаг «записать в
   следующем синхронном создании» на GuestGpu.
3. Цена записи рецептов в игре неизвестна (в логе нет времени) — число 18,1 мс офлайн; перенос сделан по нему; игровое число даст строка
   `(K us)` в S6.

## 10. Не заявляется

Что запись кэша — причина Б33 (до A/B п. 241(з)(5)); что `=1` убирает кадры ≥ 100 мс; что внутренний замок драйвера не задержит создание;
что фризы входа вызваны шейдерами; ни одно число — не выигрыш; 60 FPS не обещаются.

Файлы звена: `C:/kyty/s288/s5a/` — `times.txt`, `patch_s5a.py`, `diff_s5a.patch`, `scan_saves.py` + `.out.txt`, `bench_recipes.py` + `.out.txt`,
`refs_s5a.py` + `.out.txt`, `build.log`, `build_tests.log`, `tests_A.log`, `tests_B.log`, `commit1_msg.txt`.
