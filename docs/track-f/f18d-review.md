# F18d — ревью кода `KYTY_FIX_F8` и стенда `KYTY_TEST_AUDIOLOSS` (Red Team, `HPP-540`)

**Вердикт: PASS. RC — 0.** Код `10a4800b` (бинарь F18c `35c4a754`, worktree `79b14ef2` = S12a `4d9e8ab7` + cherry-pick) идёт в F18e без изменений. Замечаний без RC — 5 (N1–N5, §5): правки кода не требуют, адресованы ридеру и печати F18e и лиду F18f.

Решение — `20bda112:docs/ROADMAP.md:22379` п. 441 (якорь «441. **Звено F18b трека F (`HPP-536`, лид): F18a (`HPP-535`) ПРИНЯТ»; +1 — «(а) **Приёмка строкой. F18a ✓**»), член (д)(2); чтение члена (д)(1) — п. 448(б) (`disk` × 3 засчитывается, `dummy` × 1 — справка; комментарий лида `11ab9b49` в `HPP-540`); приёмка F18c — п. 449 (KytyPS5 `af665995`), поправка — п. 450 (`36c885cd`). Отчёт F18c — `5b5ef739:docs/track-f/f18c.md`. Метки: [c] — код или прогон прочитан, [I] — вывод, [U] — неизвестно. Время — UTC по `date -u`; события — `C:/kyty/f287/times.txt`. Игра не запускалась; установленный `adb0c82f`, `C:/kyty/build/install` и кэши не тронуты.

Ссылки отзыва — `<коммит>:<путь>:<строка>`, якорь и +1 проверены скриптом `docs/track-f/f18d/p540refs.py` (вывод `p540refs.txt`, `ALL OK`).

## 1. Члены п. 441(д)(2) и ответ по каждому

| Член | Проверено | Итог |
|---|---|---|
| `=0` — путь прежний на каждом сайте | §2.1 | ✓ (вызовы SDL те же; машинный код — нет, п. 449(ж)) |
| `=1` — каждый `SDL_InitSubSystem` с `SDL_INIT_AUDIO` в `src/` эмулятора (кроме лаунчера) — через `SdlAudioAcquire`; `SDL_QuitSubSystem(SDL_INIT_AUDIO)` не зовётся | §2.2 | ✓ |
| Потокобезопасность флага (С1 и С2 — разные потоки и замки) | §2.3 | ✓ |
| Стенд читает окружение раз на процесс; на пути подачи — одна проверка статического флага | §2.4 | ✓ |
| Стенд проходит сайт С2 (не обход SDL) | §2.4 | ✓ |
| Счётчики и тождества п. 441(г) | §2.5 | ✓ (N1, N2 — края тождеств) |
| Уровень проверок SDL бинаря теста | §3 | ✓ (`SDL_assert` выключен в F18c и S12) |
| Стенд без игры (д)(1) — повтор `ALL OK` своими руками | §4 | ✓ (12 из 12, `ALL OK`; чтение п. 448(б)) |

## 2. Код [c]

### 2.1 `=0` на каждом сайте

Сайты (поиск по дереву, §2.2): С1 `10a4800b:src/libs/audio.cpp:532` (якорь «`if (AudioInternal::SdlAudioSubsystemInit() < 0) {`»; +1 — «`LOGF("AudioOut: SDL audio init failed: %s\n", SDL_GetError());`»), С2 `10a4800b:src/libs/controller.cpp:190` (якорь «`if (Audio::AudioInternal::SdlAudioSubsystemInit() < 0) {`»; +1 — «`return false;`»), С3 `10a4800b:src/libs/audio.cpp:937` (якорь «`if (AudioInternal::SdlAudioSubsystemInit() < 0) {`»; +1 — «`LOGF("AudioIn: SDL init failed: %s\n", SDL_GetError());`»), выходы входного порта `10a4800b:src/libs/audio.cpp:950` (якорь «`AudioInternal::SdlAudioSubsystemQuit();`»; +1 — «`return;`») и `10a4800b:src/libs/audio.cpp:959` (якорь «`AudioInternal::SdlAudioSubsystemQuit();`»; +1 — «`port->audio_device = 0;`»).

При `=0` `SdlAudioSubsystemInit` (`10a4800b:src/libs/audio.cpp:316`, якорь «`int SdlAudioSubsystemInit() {`»; +1 — «`if (FixF8Enabled()) {`») делает `fetch_add` `relaxed` и тот же `SDL_InitSubSystem(SDL_INIT_AUDIO)` с тем же кодом возврата; `SdlAudioSubsystemQuit` (`10a4800b:src/libs/audio.cpp:324`, якорь «`void SdlAudioSubsystemQuit() {`»; +1 — «`if (FixF8Enabled()) {`») — тот же `SDL_QuitSubSystem(SDL_INIT_AUDIO)`. Вызовы стоят на прежних местах, под прежними замками (`Audio::m_mutex` у С1/С3, `HapticsOutput::m_mutex` у С2), на прежних потоках; ветвление и ранние выходы вокруг сайтов не тронуты (`git diff 4d9e8ab7 79b14ef2` — только строки сайтов, обёртки, стенд и `AudioStat`). `FixF8Enabled()` (`10a4800b:src/libs/audio.cpp:291`, якорь «`static bool FixF8Enabled() {`»; +1 — «`static const bool enabled = [] {`») при `=0` строк не пишет и SDL не зовёт. Путь подачи вибрации при выключенном стенде — `retry_us = RETRY_US`, сравнение то же, что было (`10a4800b:src/libs/controller.cpp:273`, якорь «`const uint64_t retry_us = g_test_audioloss.on ? TestAudioLossRetryUsLocked() : RETRY_US;`»; +1 — «`if (m_retry_us != 0 && now - m_retry_us < retry_us) {`»). В `QueueSdlAudio` при `KYTY_AV_TRACE` нет и стенде выключенном `audio_stat = false` (`10a4800b:src/libs/audio.cpp:710`, якорь «`static const bool audio_stat = av_trace || Controller::TestAudioLossOn();`»; +1 — «`const auto        av_queued_before = SDL_GetQueuedAudioSize(port->audio_device);`») — новых вызовов SDL нет; аргумент `port_id` ничего не меняет. При `KYTY_AV_TRACE=1` (все теги F18e) `=0` получает новые вызовы SDL только для чтения — N3.

«Байт в байт» читается как в п. 449(ж): равны вызовы SDL, машинный код — нет. Подтверждение исполнением: прогоны стенда `i_disk3_fix0` и `i_disk3_unset` дают прежний механизм на тех же числах (§4).

### 2.2 `=1`: все сайты через `SdlAudioAcquire`, выхода нет

Поиск `git grep -E 'SDL_Init\(|SDL_InitSubSystem|SDL_QuitSubSystem|SDL_Quit\(|SDL_INIT_AUDIO|SDL_INIT_EVERYTHING|SDL_OpenAudio\(|SDL_AudioInit|SDL_AudioQuit'` по `src/` на `10a4800b` (каталоги `common`, `graphics`, `kernel`, `launcher`, `libs`, `loader`):

- `SDL_InitSubSystem(SDL_INIT_AUDIO)` — только `audio.cpp:309` (внутри `SdlAudioAcquire`) и `audio.cpp:321` (ветка `=0` `SdlAudioSubsystemInit`); `SDL_QuitSubSystem(SDL_INIT_AUDIO)` — только `audio.cpp:328` (ветка `=0` `SdlAudioSubsystemQuit`). Все пять сайтов С1, С2, С3 и два выхода зовут обёртки.
- Лаунчер — `10a4800b:src/launcher/src/configurationEditDialog.cpp:176` (якорь «`if (SDL_InitSubSystem(SDL_INIT_AUDIO) == 0) {`») и `:186` — вне критерия по букве («кроме лаунчера»), отдельный процесс.
- Иных вызовов нет: `window.cpp:884` и `vulkanWindow.cpp:1320` — `SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER`; `SDL_Init(`, `SDL_Quit(`, `SDL_INIT_EVERYTHING`, `SDL_OpenAudio(` (наследный вызов, который сам инициализирует звук), `SDL_AudioInit`/`SDL_AudioQuit` в `src/` эмулятора — 0. `CloseSdlDevice(PortOut*)` (`audio.cpp:567`) — только `SDL_WasInit`.
- SDL2 `4b69833b`: подсистема звука инициализируется только при счётчике 0 (`4b69833b:src/SDL.c:292`, якорь «`if (SDL_PrivateShouldInitSubsystem(SDL_INIT_AUDIO)) {`»; +1 — «`/* audio implies events */`»), счётчик растёт на каждом вызове (`4b69833b:src/SDL.c:302`, якорь «`SDL_PrivateSubsystemRefCountIncr(SDL_INIT_AUDIO);`»; +1 — «`flags_initialized |= SDL_INIT_AUDIO;`»); событийная подсистема при этом растёт только при настоящей инициализации звука — при `=1` один раз на процесс, отдельного переворота счётчика событий от сайтов нет.

При `=1` после первого успешного `SdlAudioAcquire` счётчик SDL звука = 1 и больше не меняется эмулятором до конца процесса [c].

### 2.3 Потокобезопасность флага

`SdlAudioAcquire` (`10a4800b:src/libs/audio.cpp:302`, якорь «`int SdlAudioAcquire() {`»; +1 — «`g_sdl_audio_acq_calls.fetch_add(1, std::memory_order_relaxed);`»): проверка `g_sdl_audio_acquired`, вызов `SDL_InitSubSystem` и запись флага — под одним `g_sdl_audio_mutex` (`lock_guard`, снимается на каждом из трёх выходов). С1/С3 (поток гостя, `Audio::m_mutex`) и С2 (поток звука гостя, `HapticsOutput::m_mutex`) сериализуются на нём. Порядок замков: `g_sdl_audio_mutex` берётся последним, внутри — только SDL; SDL обратно в код эмулятора из `SDL_InitSubSystem` не зовёт ⇒ нового цикла замков нет. Неуспех не запоминается (флаг ставится только после `>= 0`). `FixF8Enabled` и `audio_stat` — локальные статические с потокобезопасной инициализацией C++11. Счётчики — `std::atomic` `relaxed`; они только печатаются, решений по ним код не принимает. Член (iii) стенда (§4) подтверждает `init_calls = 1` при двух потоках, но различающей силы против гонки не доказан — N4.

### 2.4 Стенд `KYTY_TEST_AUDIOLOSS`

- **Окружение — раз на процесс:** `ReadTestAudioLoss` зовёт только `HapticsOutput::Start` (`10a4800b:src/libs/controller.cpp:172`, якорь «`ReadTestAudioLoss();`»; +1 — «`if (const char* value = std::getenv("KYTY_HAPTICS"); value != nullptr && value[0] == '0') {`»), её — только `Controller::Initialize`; подсистема контроллера инициализируется раньше подсистемы звука (`10a4800b:src/emulator.cpp:165`, якорь «`subsystems.Initialize<Libs::Controller::Lifecycle>();`»; +1 — «`subsystems.Initialize<Libs::Audio::Lifecycle>();`») и до потоков гостя ⇒ запись `g_test_audioloss` без атомиков безопасна (до создания читающих потоков), а `audio_stat` в `QueueSdlAudio` видит итоговое значение. Разбор значения: пусто/нет — выкл. без строк; `<с>` с цифры в начале, конечное, ≤ 86 400, хвост пусто или `:retry`; иначе строка `config invalid` и выкл. — по букве (г).
- **Путь подачи — одна проверка статического флага:** `g_test_audioloss.on` в ветке `m_device == 0` (`controller.cpp:273`); в `QueueSdlAudio` — статическая `audio_stat` (`audio.cpp:710`).
- **Сайт С2, не обход SDL:** автомат (`10a4800b:src/libs/controller.cpp:228`, якорь «`uint64_t HapticsOutput::TestAudioLossRetryUsLocked() {`»; +1 — «`const uint64_t t = LibKernel::KernelGetProcessTime();`») меняет только интервал повтора; попытка — прежний `OpenLocked` → `SdlAudioSubsystemInit` (С2) на прежнем потоке под прежним `m_mutex`. В `Firing` интервал 0 ⇒ `now - m_retry_us < 0` для `uint64_t` ложно всегда ⇒ каждая подача — попытка; счёт попыток 1…300 (переход из `Armed` проваливается в `Firing` и считает первую), 300-я переводит в `DonePending`, строка `done attempts=300` — на следующей подаче, после неё интервал 3 с от времени 300-й попытки. Ровно 300 попыток с нулевым интервалом [c кода]. Состояние автомата — под `m_mutex`. При `KYTY_HAPTICS=0` стенд не взводится (`Push` выходит раньше) — допуск F18e это закрывает (строка порта вибрации и 0 строк `Haptics: … opened` не исключают `KYTY_HAPTICS=0` — N5).

### 2.5 Счётчики `AudioStat` и тождества п. 441(г)

Поля строки — по букве (г) (`t_us port dev status queued pushes q_fail init_calls acq`), без `lost`, `reopen_*`, `lost_us`. `AudioStatPush` (`10a4800b:src/libs/audio.cpp:354`, якорь «`static void AudioStatPush(int port_id, SDL_AudioDeviceID dev, bool failed) {`»; +1 — «`if (port_id < 0 || port_id >= OUT_PORTS_MAX) {`») зовётся только после `SDL_QueueAudio` (успех и отказ) — порты без устройства (`audio_device == 0`, в т.ч. порт вибрации) строк не дают; номер порта — `handle.GetId()` ∈ [0; 32) (`10a4800b:src/libs/audio.cpp:922`, якорь «`QueueSdlAudio(&port, params[i].handle.GetId(), params[i].data, blocking);`»; +1 — «`}`»), тот же индекс, что у `m_out_ports`. Прореживание — раз в 1 с процессного времени на порт, плюс одна строка на ближайшей подаче после `AudioStatForce` (`fire`, `done`); CAS — один печатающий. Тождества: `acq = 0` при `=0` — ✓ (`SdlAudioAcquire` зовёт только ветка `=1`); `init_calls ≤ 1` при `=1` — ✓ при успехе первой инициализации (край — N1); `q_fail ≤ pushes` и неубывание по порту — ✓ при одном потоке подач на порт (край — N2). Записей в состояние гостя нет; `SDL_GetAudioDeviceStatus` и `SDL_GetQueuedAudioSize` — только чтение.

## 3. Уровень проверок SDL бинаря теста [c]

`C:/kyty/f287/f18c/build/CMakeCache.txt` (`CMAKE_HOME_DIRECTORY` = `C:/kyty/f287/f18c/wt`) и `C:/kyty/s288/s12a/build/CMakeCache.txt` (S12, `adb0c82f`): `CMAKE_BUILD_TYPE:STRING=Release`, `SDL_ASSERTIONS:STRING=auto`. Строка компиляции `SDL2-static.dir/src/SDL.c.obj` в обоих `build.ninja` — `/O2 /DNDEBUG`, `_DEBUG`/`DEBUG`/`SDL_ASSERT*` нет; `SDL_config.h` сборки — `/* #undef SDL_DEFAULT_ASSERT_LEVEL */` ⇒ по `3rdparty/SDL2/include/SDL_assert.h:33`–`:41` `SDL_ASSERT_LEVEL` = 1, `SDL_assert` выключен ⇒ проверка `< 255` счётчика (`SDL.c:125`) не срабатывает, переворот идёт — у бинаря F18c и у S12 одинаково. Исполнением — только у бинаря стенда F18c (переворот на вызове 254 без срабатывания проверки, §4); у S12 — по флагам [c флагов]. Скрипт — `docs/track-f/f18d/ninja_sdl.py`.

Происхождение: `git -C C:/kyty/f287/f18c/wt log` — `79b14ef2` над `4d9e8ab7`; `git cherry 10a4800b 79b14ef2 4d9e8ab7` → `- 79b14ef2…`; пять файлов правки в `10a4800b` и `79b14ef2` равны (sha1 blob-содержимого); `src/`, `tests/`, `CMakeLists.txt` между `10a4800b` и HEAD `36c885cd` не менялись. sha256: `C:/kyty/f287/f18c/build/install/kyty_emulator.exe` = `C:/kyty/f287/bin/kyty_emulator_35c4a754.exe` = `35c4a754…`; бинарь стенда `C:/kyty/f287/f18c/fix/f8_audio_stand.exe` = `C:/kyty/f287/f18c/build/f8_audio_stand.exe` = `74134c1b…`. Цель стенда — `add_kyty_full_emulator_test` (исходники эмулятора `${kyty_emulator_src}`, `EXCLUDE_FROM_ALL`) ⇒ `SdlAudioSubsystemInit`/`SdlAudioAcquire` — тот же `audio.cpp`, не копия.

## 4. Стенд без игры — повтор (п. 441(д)(1), чтение п. 448(б)) [c прогона]

Команда: `python C:/kyty/KytyPS5/docs/track-f/f18c/run_stand_f18c.py C:/kyty/f287/f18c/fix/f8_audio_stand.exe C:/kyty/f287/f18d/stand_rerun` (2026-10-04, без замка и `STOP`; драйверы SDL только `dummy`/`disk`, устройства звука хоста не открывались — контроли `refuse`, `refuse_host` код 3). Итог — 12 из 12 `PASS`, последняя строка `ALL OK`, rc 0; вывод — `docs/track-f/f18d/stand_rerun/stand_f18c.txt` (sha256 `4ec9aeb7…`). Вывод совпадает с `5b5ef739:docs/track-f/f18c/runs/stand_f18c.txt` во всех строках, кроме поля `wall=` и строки пути/sha (сравнение `diff` без `wall`).

Засчитывается по п. 448(б) — `disk` × 3:

| Член | Прогон | Число буквы | Повтор |
|---|---|---|---|
| (i) `=0` | `i_disk3_fix0` | вызовы 1–253 — очередь успешна; 254-й — −1 `Invalid audio device ID` у 3 из 3 | `first_fail_call=254`, `fail_devices_at_first=3`, `first_error=Invalid audio device ID`, `init_calls=303`, `acq=0` ✓ |
| (i) без переменной | `i_disk3_unset` | = `=0` | то же ✓ |
| (ii) `=1` | `ii_disk3_fix1` | 10 000 вызовов — 0 отказов, `WasInit ≠ 0`, `init_calls` = 1 | `queue_failed=0`, `was_init=16`, `init_calls=1`, `acq=10003` ✓ |
| (iii) `=1` | `iii_disk3_fix1` | 2 × 5 000 — `init_calls` = 1 | `init_calls_after_threads=1`, `acquire_failed=0`, `acq_after_threads=10000` ✓ |
| контроль (i) при `=1` | `i_disk3_fix1` | — | 0 отказов, `init_calls=1`, `acq=303` ✓ |

Справка (`dummy`): `i_dummy1_fix0` — первый отказ на вызове 256 = 257 − A при A = 1; `i_dummy3_fix0` — 2 открытия отказаны (`OnlyHasDefaultOutputDevice`), первый отказ на 254 у 1 из 1.

## 5. Замечания без RC (код не меняется)

- **N1 — тождество `init_calls ≤ 1` при `=1` ложно при отказе `SDL_AudioInit` хоста.** Сценарий: на хосте ни один драйвер звука SDL не поднимается (или поднимается не с первой попытки) ⇒ каждая попытка С1/С2/С3 при `=1` — новый настоящий `SDL_InitSubSystem` ⇒ `init_calls` = числу попыток при исправном коде ⇒ член «`init_calls ≤ 1`» `f8_s1`/`f8_n1` провален не дефектом правки. Допуск F18e (A = число строк `AudioOut: opened SDL device`) этот случай почти закрывает: при A ≥ 1 первая успешная инициализация была, но неудачи ДО неё уже посчитаны. Предложение лиду F18f/ридеру F18e [I]: при провале члена печатать число строк `AudioOut: SDL audio init failed` до первой строки `opened`; при ≥ 1 — помеха прогона, не провал (решает лид; до решения — по букве).
- **N2 — `q_fail ≤ pushes` и неубывание по порту держатся при одном потоке подач на порт.** Сценарий: два потока гостя подают в один выходной порт одновременно, печатает поток с более старым снимком `pushes` ⇒ строка с `q_fail > pushes` или с меньшими счётчиками после большей. В игре — [U] (по F18a порт подаёт один поток звука). Ридеру F18e: нарушение тождества печатать с номерами строк и не считать доказательством дефекта правки без проверки потоков.
- **N3 — при `KYTY_AV_TRACE=1` путь `=0` получает новые вызовы SDL только для чтения** (`SDL_GetAudioDeviceStatus`, `SDL_GetQueuedAudioSize` — не чаще раза в секунду на порт и после `fire`/`done`). Счётчик подсистемы они не трогают [c кода SDL]; `f8_n0` («естественное воспроизведение на текущем коде») поэтому читается как «текущий код + чтения `AudioStat`». Влияние на темп — не измерено [U]; член `f8_n0` от него не зависит.
- **N4 — член (iii) не имеет положительного контроля.** `SDL_AudioInit` драйверов `dummy`/`disk` занимает микросекунды (`wall=0.0s`), окно гонки мало ⇒ вариант без мьютекса («проверил — вызвал — поставил флаг») с заметной вероятностью тоже дал бы `init_calls_after_threads=1`. Потокобезопасность флага доказана чтением кода (§2.3), не прогоном (iii); прогон (iii) — свидетель «два потока не ломают счёт», не дискриминатор. Буквы (д)(1) это не нарушает.
- **N5 — допуск F18e не исключает `KYTY_HAPTICS=0`.** При `KYTY_HAPTICS=0` строка `AudioOut: vibration port` есть, строк `Haptics: … opened` 0, но `Push` выходит до стенда и до С2 ⇒ `f8_s0` без `armed`, `f8_n0` без строки Ф8 ⇒ ложное «механизм опровергнут». Печать F18e: в допуск — строка `Haptics: disabled by KYTY_HAPTICS=0` отсутствует (или `KYTY_HAPTICS` не задан в окружении тега).

## 6. Чек-лист кода (роль Red Team)

- Вызовы вне хронометрируемой строки — n/a (хронометража нет).
- Гонки: флаг — под мьютексом ✓; публикация конфигурации стенда — до потоков ✓; печать `AudioStat` — CAS, рваное чтение счётчиков — N2.
- Инварианты `*_bad` — нет; тождества (г) — §2.5.
- Ранние возвраты: `lock_guard` снимается на всех выходах `SdlAudioAcquire` ✓; счётчик `acq` — до замка, на всех путях ✓; `init_calls` — до вызова SDL, на успехе и отказе ✓.
- Патч — `patch_f18c_src.py`, якоря целыми строками, LF [c отчёта F18c §1; CR в `src/` worktree — 0].
- Кадр стека новых функций — без больших локальных буферов ✓.
- Подпись трансляции — правка вне `src/graphics/shader/**` ✓ (`26ce5fc7` = S12, отчёт F18c §1).
- `getenv` новых ручек: `KYTY_FIX_F8` — `EnvValueOn` (нет/пусто/`0`/`false`/`off`/`no` — выкл.) ✓; `KYTY_TEST_AUDIOLOSS` — нет/пусто — выкл., без строк ✓; ни одна ручка присутствием не включает побочный путь (`KYTY_AV_TRACE` — прежняя ручка, N3).

## 7. Не заявляется

Что Ф8 воспроизводится на установленном бинаре до тега `f8_n0`; что `KYTY_FIX_F8=1` снимает строку Ф8 в игре (это — F18e); что машинный код `=0` равен прежнему байт в байт (равны вызовы SDL); что настоящая потеря устройства хоста даёт ту же форму; что звук верен или слышим; что поток звука без темпа меняет часы игры; что Б24 воспроизводим без оборудования; что Ф6 — дефект или не дефект до F16g; что Б4 `FIXED` до F15f; что Ф19 `FIXED` до F14h; что Ф8 `FIXED` (до F18f); что реестр полон; ни одно число — не выигрыш; 60 FPS не обещается.
