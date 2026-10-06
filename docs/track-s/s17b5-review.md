# S17b5 — код-ревью стенда К6 S17a5 и условие переноса изд. 4 (Red Team, `HPP-639`)

**Вердикт: `PASS`.** Код `c0057ccb` верен; правок кода нет, бинарь S17c2 `43ef1cc1…` идёт без изменений. RC 2, оба —
к печати изд. 4 (S17c2, Harness Engineer), не к коду. Условие переноса п. 561(д)(1) — **подтверждено**.

Вход: `ROADMAP.md` п. 561 (KytyPS5 `0c78eb3f`), п. 565 (`6171412d`); комментарий лида `286a88ba` в `HPP-639`; дифф
`9238a182..c0057ccb`; `C:/kyty/s288/FACTS.md` § S17a5. Игру не запускал, код не правил. Время — `C:/kyty/s288/s17b5/times.txt`
(`date -u`). Ссылки отзыва — 29 из 29 по якорю и +1 на `c0057ccb` (`C:/kyty/s288/s17b5/refs_s17b5.py` → `ALL OK`).

## 0. Что ревьюется

- `git patch-id --stable`: `git diff 9238a182 c0057ccb` и `git show 5bd93ea1` — оба `516cff8b3a540f48952e5211b9c454ff2461e96e`
  (= числу лида). Родитель `c0057ccb` — `9238a182`.
- Дифф: 1 файл (`src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp`), +20 / −0: `#include <thread>` и блок ожидания
  внутри ветви стенда `stop` в `ReplayRebuild`.
- Бинарь `C:/kyty/s288/bin/kyty_emulator_43ef1cc1.exe`: sha256 `43ef1cc14ec2c116fdcce9ac71f9d854d0ec6498bd6e538fa479b1ecdf57fbb3`,
  строка версии `KytyPS5-2026-09-15-6a2987a-2337-gc0057ccb`; строки `stand stop seen waited_ms` и `stand stop timeout waited_ms`
  в бинаре — по 1.

## 1. Вывод S17a5 «окно идёт одновременно с перестройкой» — подтверждён по коду

- Поток перестройки стартует в `StartPrecache`: `c0057ccb:…/pipelineCache.cpp:6751` (якорь
  `m_precache_active.store(true, std::memory_order_release);`, +1 `m_precache_thread = std::thread([this] {`); флаг снимается в
  конце потока — `:6759` (якорь `m_precache_active.store(false, std::memory_order_release);`, +1 `});`).
- Цикл экрана подготовки держится, пока флаг поднят: `GetPreparationStatus` — `:6586` (якорь
  `const bool active = m_precache_active.load(std::memory_order_acquire);`, +1 `return {active, …};`);
  `c0057ccb:src/graphics/presentation/window/window.cpp:1020` (якорь
  `if (!status.active && SDL_GetTicks64() - started >= hold_ms) break;`, +1 `while (SDL_PollEvent(&g_window->loop.event)) {`).
- Цикл начинается после `LoadElf` (`c0057ccb:src/emulator.cpp:262`, якорь `LoadElf(options.elf);`) — в `Execute`
  (`:188`, якорь `if (!Libs::Graphics::WindowPrepareShaders()) {`, +1 `std::quick_exit(0);`).
- Итог: цикл не стартует раньше перестройки, но, стартовав при живом потоке, ждёт его конца и всё это время опрашивает события.
  Пока стенд держит поток, `m_precache_active` = 1 ⇒ цикл не выходит по `break` и читает событие закрытия. Ветвь
  «окно идёт одновременно» п. 561(г)(2) по коду верна. Замечание без RC: комментарий кода `:7418` («does not wait for this
  thread») неточен — цикл ждёт поток, он лишь стартует позже; § S17a5 `FACTS.md` п. (1) сказан верно.

## 2. Стенд обрывает именно перестройку и ведёт настоящим путём закрытия

- Ветвь стенда: `:7414` (якорь `if (SR::TestStand() == SR::Stand::Stop && !stop_stand_done && processed >= records / 2u) {`,
  +1 `stop_stand_done = true;`); событие — `:7417` `SR::StandRequestClose();` →
  `c0057ccb:…/shaderReplay.cpp:100` (якорь `event.type = SDL_QUIT;`, +1 `SDL_PushEvent(&event);`).
- Ожидание: `:7426` (якорь `while (!m_precache_stop.load() && HostMicros() - wait_begin < StandStopWaitMs * 1000u) {`,
  +1 `std::this_thread::sleep_for(std::chrono::milliseconds(5));`), предел `StandStopWaitMs = 60000`; флаг виден ⇒ строка
  `stand stop seen waited_ms=… processed=… records=…` и `break` (`:7430`); предел ⇒ строка `stand stop timeout waited_ms=…`
  (`:7435`) и перестройка идёт дальше. `HostMicros()` — `uint64_t` (`:262`), формат `PRIu64` верен.
- `break` стоит до `processed++` (`:7441`): запись, на которой сработал стенд, не начата — частичной записи (PS без VS) нет;
  обрыв — ровно при `processed = ⌊records / 2⌋` < `records` (при `records` ≥ 1).
- Путь закрытия: цикл читает `SDL_QUIT` → `cache.ReplayCloseStop();` (`window.cpp:1029`, +1 `return false;`) →
  `m_precache_stop.store(true);` (`pipelineCache.cpp:6624`, +1 `if (m_precache_thread.joinable()) {`) → `join` → `return false`
  → `std::quick_exit(0)` (`emulator.cpp:188`). Это тот же путь, что щелчок по кнопке закрытия окна (п. 532(б)).

**Вопрос лида (1) — замки во время ожидания: находки нет.** Блок ожидания стоит в теле цикла `for` `ReplayRebuild`; в области
видимости — только локальные объекты функции, ни одного `LockGuard`. Вызов `ReplayRebuild` — из лямбды потока без замка
(`:6754`). Единственный замок функции — `Common::LockGuard lock(m_mutex);` (`:7570`, +1 `for (const auto& [id, s]: sources) {`) —
после цикла, в своём блоке. `LoadEntry` (`:7324`) и `cache.Save` в `save_dirty` берут и отпускают свои замки до ожидания.
`ReplayCloseStop` и `~PipelineCache` (`:4859`) замков не берут: пишут атомик и делают `join`. Главный поток в цикле подготовки
замков кэша не держит (`GetPreparationStatus` — только атомики). Поток представления при показе оверлея может брать `m_mutex` —
поток перестройки его не держит. Закрытие ждёт не предел 60 с, а ≤ 5 мс опроса + остаток функции после цикла.

**Вопрос лида (2) — кто читает `SDL_QUIT`, посланный до входа в цикл: находки нет.** Опросы событий SDL во всём `src` на
`c0057ccb` (`SDL_PollEvent|SDL_WaitEvent|SDL_PumpEvents|SDL_PeepEvents|SDL_FlushEvent(s)`): только `window.cpp:1021` (цикл
подготовки) и `hostInput.cpp:424`/`:432` (`HostInputWaitEvent`), а последний зовётся только из `WindowContext::Run` (`window.cpp:871`; вызов — `window.cpp:891`,
якорь `if (!HostInputWaitEvent(&loop.event)) {`, +1 `continue;`) — это `WindowRun`, после `WindowPrepareShaders`. Фильтров и
наблюдателей событий (`SDL_SetEventFilter`, `SDL_AddEventWatch`, `SDL_FilterEvents`, `SDL_EventState`) нет; единственная
проверка состояния — `SDL_GetEventState(SDL_DISPLAYEVENT)` (`window.cpp:557`). `SDL_PumpEvents` события не удаляет. Поток
перестройки стартует в конструкторе `PipelineCache` (`RenderContext` создаётся в `WindowContext::CreateVulkan`, `vulkanWindow.cpp:1273`, после `WindowCreate`, `window.cpp:975`–`976`), т. е. подсистема событий уже
поднята. ⇒ `SDL_QUIT`, поставленный за ≈ 6 с `HostImport::Preload` до цикла, лежит в очереди и первым его читает цикл подготовки
(`window.cpp:1023`). Исключение — `KYTY_SHADER_PREPARE=0`: `WindowPrepareShaders` возвращает `true` до цикла (`window.cpp:992`),
событие читает `WindowContext::Run` → `GameEventQuit` (`window.cpp:570`) → `WindowRun` возвращается → `quick_exit`, поток перестройки
убит в ожидании, строк `stand stop seen` и `pipelines_bin=` нет. Это форма, запрещённая п. 533 для тегов `KYTY_S_REPLAY` ∈ {1, 3};
ложного ✓ она не даёт (строк нет). Замечание без RC: результат `SDL_PushEvent` не проверяется — при отказе постановки стенд
ждёт 60 с и печатает `stand stop timeout`; член ✗ виден, но причина (постановка или чтение) по логу не различима.

## 3. При обрыве `pipelines.bin` не пишется, строка `pipelines_bin=stopped`; следующий запуск

- `const bool stopped = m_precache_stop.load();` (`:7543`, +1 `save_dirty();`) → `if (stopped) {` (`:7578`, +1
  `recipes_state = "stopped";`) — запись `pipelines.bin` во ветви `else` не выполняется; манифест — только при
  `if (!stopped && count != 0) {` (`:7606`). Строка итога перестройки печатает `pipelines_bin=%s` (= `stopped`). После возврата
  `ReplayRebuild` поток не зовёт `PrecachePipelines` (`:6756`, якорь
  `if (!m_replay_rebuild || (!m_precache_stop.load() && Common::File::IsFileExisting(m_recipes_path))) {`, +1 `PrecachePipelines();`).
  Этот путь — код `9238a182`, дифф его не меняет.
- Файлы трансляции источников, изменённых до обрыва, сохраняются (`save_dirty()` на `:7544` идёт и при `stopped`).
  Следующий запуск: `pipelines.bin` нет ⇒ `RecipesFileCurrent` ложно (`:6739`) ⇒ перестройка всех записей; источники первой
  половины — из файла (`LoadEntry`, `:7324`), их перестановки — `perms_cached`, перестановки второй половины — `perms_new`.
  ⇒ тождество п. 565 `perms_new(ks2) + perms_new(kn2) = perms_new(r3b)` по коду выполняется — **при условиях RC2**.
- Ограничение: при совместимом `_ShaderSeeds` и пустой папке варианта `InstallShaderSeed()` (`:6722`) ставит `pipelines.bin`
  каталога до проверки `:6739` — перестройка уходит в `recipes_current`, а файлы трансляции перезаписываются каталогом
  (`copy_options::overwrite_existing`). Покрыто п. 561(д)(3) (`KYTY_SHADER_SEED=0`, член допуска — 0 строк
  `ShaderSeed: installed`); отдельного RC нет.

## 4. Условие переноса п. 561(д)(1) — ПОДТВЕРЖДЕНО

- Весь новый исполняемый код — внутри `if (SR::TestStand() == SR::Stand::Stop && …)` (`:7414`); `TestStand()` возвращает `Stop`
  только при `KYTY_S_REPLAY_TEST` = `stop` дословно (`c0057ccb:…/shaderReplay.cpp:73`, якорь `if (text == "stop") {`,
  +1 `return Stand::Stop;`; функция дифом не тронута). Вторая правка — `#include <thread>` — поведения не меняет.
- `ReplayRebuild` зовётся только при `m_replay_rebuild` (`:6753`–`:6754`), т. е. при `KYTY_S_REPLAY` ∈ {1, 3}; захват (`=1`, `=2`),
  путь игры при `=0` и сам ход перестройки при стенде ≠ `stop` — строки дифом не тронуты (удалённых строк 0, изменённых 0).
  ⇒ при `KYTY_S_REPLAY_TEST` ≠ `stop` поведение `9238a182` не меняется.
- Строка подписи: `KYTY_SHADER_SOURCE_HASH` строится из `src/graphics/shader/**/*.{cpp,h,inc}` и четырёх файлов
  `SHADER_CACHE_EXTRA_FILES` (`c0057ccb:CMakeLists.txt:155`–`156`: `shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`,
  `imageInfo.h`; `src/generate_version.cmake:43`–`56`). `pipelineCache.cpp` в набор не входит, дифф других файлов не трогает ⇒
  хэш и строка подписи равны `ed2686da` (`KytySC3:9177b426…:fixf19`; проба исполнителя байт в байт — `FACTS.md` § S17a5).
  `RecipeLayoutSignature` дифом не тронута.
- ⇒ теги п. 561(д)(1) (`s17c_v0`, `s17c_w0`, `s17c_c2`, `s17c_ca`, `s17c_cc`, `s17c_n0`, `s17c_e3`, `s17c_ew`, `s17c_kc`)
  переносятся без повтора — со стороны кода условие выполнено; решение — у S17c2/S17d2 по п. 561(д)(1).

## 5. К2(1)

Дифф не задевает список подписи (§ 4) — свой пересчёт К2(1) не делался (условие задания (5)).

## RC (к печати изд. 4, S17c2 `HPP-640`, Harness Engineer; не к коду)

**RC1. Член К6 «обрыв настоящим путём» читается по порядку строк, а не по двум строкам.**
Что не так: `m_precache_stop` ставят два места — `ReplayCloseStop` (`:6624`) и `~PipelineCache` (`:4859`). Строки
`stand stop seen` и `pipelines_bin=stopped` печатаются при любом из них.
Сценарий отказа [I по пути выхода]: главный поток во время ожидания стенда уходит путём, который разрушает `PipelineCache`
(выход через `atexit`, а не `quick_exit`) — в логе есть `stand stop seen` и `pipelines_bin=stopped`, член читается ✓, хотя
настоящий путь закрытия окна не шёл.
Что изменить: К6 ✓ только при строках в этом порядке: `ShaderReplay: stand stop applied processed=P records=R` →
`ShaderReplay: close stop requested precache_active=1` → `ShaderReplay: stand stop seen … processed=P records=R` →
`ShaderReplay: rebuild … pipelines_bin=stopped` → `ShaderReplay: close stop joined wait_ms=…`; P одно и то же, P < R;
0 строк `stand stop timeout`, 0 строк `Event: quit`; код выхода 0. Фикстура на каждый член и на перестановку двух строк.

**RC2. Тождество п. 565 `perms_new(ks2) + perms_new(kn2) = perms_new(r3b)` верно по коду только при одинаковом исходном
состоянии.**
Что не так: `perms_new` считает перестановки, которых нет в файлах трансляции папки варианта на момент запуска (`:7324`,
`:7345`); сумма равна полной перестройке, только если `ks2` и `r3b` стартуют с одной и той же папки варианта и тем же
каталогом повтора, а `kn2` — с состояния после `ks2`.
Сценарий отказа: (а) между `ks2` и `kn2` харнесс возвращает кэши — файлы первой половины пропали, `perms_new(kn2)` =
`perms_new(r3b)`, сумма больше на `perms_new(ks2)` ⇒ ложный ✗; (б) `r3b` стартует с папки, где уже есть файлы трансляции
(например, после `=2` сбора), а `ks2` — с холодной ⇒ `perms_new(r3b)` меньше, ложный ✗; (в) обратное расхождение — ложный ✓.
Что изменить: в печати — манифест папки варианта (`_fixf19`) и `replay/` по sha перед `ks2` и перед `r3b` равны; между `ks2` и
`kn2` кэши не возвращаются (манифест после `ks2` = манифесту перед `kn2`); `KYTY_S_REPLAY` одинаков у трёх тегов; член
допуска — равенство манифестов, иначе К6 «не определено». Фикстура на (а) и (б).

## Чек-лист кода

- Хронометрируемая строка: нет (стенд, не измерение). — n/a.
- Гонки: `m_precache_stop` — `std::atomic<bool>`, читается в цикле ожидания и на `:7543`; пишется главным потоком; рваного
  чтения нет. `stop_stand_done` — локальная. ✓
- Инварианты `*_bad`: нет новых. — n/a.
- Ранние возвраты / замки: замков в области ожидания нет (§ 2, вопрос (1)). ✓
- Ручка внутри одной операции: `TestStand()` — статическая, читается один раз за процесс; `processed >= records / 2u` — между
  записями. ✓
- C-строки с `\n` в диффе: 3 `LOGF` с `\n` — в коммите целы (дифф прочитан), разрывов литералов нет. ✓
- CRLF / якоря: дифф чистый (20 строк `+`, 0 `-`); ✓.
- Стек потока гостя: код на потоке precache, кадр стека — несколько `uint64_t`. ✓
- Подпись трансляции: не меняется (§ 4). ✓
- Инструмент меняет прогон: при стенде ≠ `stop` — нет (§ 4); при `stop` — меняет намеренно (держит поток), это и есть стенд.

## Не заявляется

Что К6 или К4 пройдены; что стенд в игре сработает так, как прочитан код (код в игре не проверен, теги `s17c_ks2`/`s17c_kn2`
S17c2); что S-replay выполним или даст тёплый первый вход пользователя; что 0 трансляций программ каталога убирает фризы
входа; что второй уровень пройдёт; полнота корпуса, каталога и `eboot.bin`; ни одно число — не выигрыш; 60 FPS не обещаются.
