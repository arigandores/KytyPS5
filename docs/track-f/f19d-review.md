# F19d — ревью кода `KYTY_FIX_B24` и стенда `KYTY_TEST_HIDLOSS` (Red Team, `HPP-548`)

**Вердикт: PASS_WITH_FIXES.** Код `9c726d74` по п. 451(д)(2) годен для тегов F19e: бинарь теста `9b00ad40` идёт в F19e без изменений. RC — 1 (код, путь выхода, который теги F19e не проходят): закрыть до бинаря отгрузки с умолчанием `KYTY_FIX_B24=1`. Вопрос лиду — 1 (Q1: добавки пути `=0` вне списка п. 457(б)). Замечаний без сценария отказа — 5 (N1–N5). Игра не запускалась.

Вход: решение `457655e2:docs/ROADMAP.md:22463` п. 451 (якорь «451. **Звено F19b трека F (`HPP-544`, лид; приёмка F19a»; +1 — «(а) **Приёмка строкой. F19a ✓**»); приёмка F19c `1a666f63:docs/ROADMAP.md:22519` п. 457 (якорь «457. **Звено F19c трека F (`HPP-547`, Emu Engineer; приёмка лида»; +1 — «(а) **Приёмка строкой. F19c ✓.**»); код — дифф `10a4800b..9c726d74` по `src/libs/controller.cpp`, `src/libs/controller.h`, `src/graphics/presentation/window/window.cpp` (в диапазоне эти файлы трогает только `9c726d74`); отчёт F19c `45080d53:docs/track-f/f19c.md`; проект `0b065a70:docs/track-f/f19a.md` §4–§6; SDL2 — подмодуль `3rdparty/SDL2` `4b69833b`. Ссылки на код — `9c726d74:<файл>:<строка>` (неизменяемый коммит; без префикса — `src/libs/controller.cpp`). Метки: [c] — прочитано в коде или выводе, [I] — вывод. Время — `C:/kyty/f287/times.txt`.

## 1. Путь `=0`: вызовы SDL, порядок, замки, возвраты (п. 451(д)(2) в прочтении п. 457(б)) [c]

Сверено по диффу построчно. Последовательность вызовов SDL, замок `m_mutex`, условия и возвращаемые значения у `SetVibration` (`:1174`–`:1200`), `SetLightBar` (`:1202`–`:1217`), `SetTriggerEffect` (`:1219`–`:1260`), `Connect` (`:864`–`:885`), `Disconnect` (`:887`–`:902`), `CheckActive` (`:904`–`:940`), `ReleaseHostPads` (`:1140`–`:1172`), `Initialize` / `Shutdown` / `EmergencyShutdown` (`:825`–`:862`), `HapticsOutput` (не тронут) и обработчика удаления (`window.cpp:403`–`:409`) — те же, что на `10a4800b`. Машинный код не равен (п. 457(д)); равенство — по вызовам, порядку, замкам и возвратам.

Добавки пути `=0` поимённо:

| № | Где | Что исполняется при `=0` и выключенном стенде | В списке п. 457(б) |
|---|---|---|---|
| A1 | `PadCallProbe` в трёх функциях вывода (`:1175`, `:1203`, `:1220`; класс `:120`) | одна `relaxed`-загрузка `g_hidloss_window` (`:92`); деструктор — проверка поля | да |
| A2 | `probe.Sdl()` перед каждым вызовом SDL (`:1187`, `:1195`, `:1197`, `:1211`, `:1214`, `:1250`, `:1253`, `:1256`) | проверка поля пробы | да |
| A3 | обработчик удаления (`window.cpp:405`–`:406`) | строка `Controller <id>: removed` и одна `relaxed`-загрузка окна стенда | да |
| A4 | запись гостя: `WindowTestMinimizeNoteGuestText` → `WindowTestHidLossNoteGuestText` (`window.cpp:1304`, `:1282`–`:1294`) | страж локальной статики и `cfg.on` | да |
| A5 | три функции вывода: `if (g_fix_b24)` (`:1176`, `:1204`, `:1242`) | одна загрузка `static bool` | нет — Q1 |
| A6 | `Initialize` (`:828`–`:834`) | `getenv("KYTY_FIX_B24")` раз на процесс и ветка | нет — Q1 |
| A7 | `Connect` (`:868`–`:872`, `:880`–`:882`) | `ps5 = false` и проверка `g_fix_b24`; `push_back` недостижим | нет — Q1 |
| A8 | `Disconnect` (`:899`), `ReleaseHostPads` (`:1171`) | `erase`/`remove` и `clear` пустого `m_ps5_ids` под уже взятым `m_mutex` | нет — Q1 |
| A9 | `CheckActive` (`:934`) | проверка `g_pad_output != nullptr` | нет — Q1 |
| A10 | `EmergencyShutdown` (`:856`), `Shutdown` (`:847`–`:848`) | проверка указателя; `delete nullptr` | нет — Q1 |
| A11 | член `GameController::m_ps5_ids` (`:677`) | раскладка объекта | нет — Q1 |

При `=0` `g_pad_output` всегда `nullptr` (единственная запись не-null — `:832`, под `g_fix_b24`), `m_ps5_ids` всегда пуст (единственный `push_back` — `:881`, под `ps5`, истинным только при `g_fix_b24`, `:869`). Ни одна из A1–A11 не зовёт SDL, не берёт замок, не меняет порядок вызовов SDL и возвращаемые значения. **Член «при `=0` путь прежний, кроме строки `Controller <id>: removed`» — выполнен в прочтении п. 457(б)**, с вопросом Q1 о букве списка.

## 2. `=1`: вызовы `SDL_` в `controller.cpp` поимённо, с потоком [c]

| Строки | Функция | Вызовы SDL | Поток при `=1` |
|---|---|---|---|
| `:339`–`:348` | `PadOutput::ApplyVibration` | `SDL_LockJoysticks`, `SDL_GameControllerFromInstanceID`, `SDL_GameControllerRumble`, `SDL_GetError`, `SDL_UnlockJoysticks` | `PadOutput` |
| `:356`–`:360` | `PadOutput::ApplyLightBar` | `SDL_LockJoysticks`, `SDL_GameControllerFromInstanceID`, `SDL_GameControllerSetLED`, `SDL_UnlockJoysticks` | `PadOutput` |
| `:365`–`:370` | `PadOutput::ApplyTriggerEffect` | `SDL_LockJoysticks`, `SDL_GameControllerFromInstanceID`, `SDL_GameControllerGetType`, `SDL_GameControllerSendEffect`, `SDL_UnlockJoysticks` | `PadOutput` |
| `:478`–`:498` | `HapticsOutput::OpenLocked` | (`Audio::AudioInternal::SdlAudioSubsystemInit`), `SDL_GetNumAudioDevices`, `SDL_GetAudioDeviceName`, `SDL_strcasestr`, `SDL_OpenAudioDevice`, `SDL_GetError`, `SDL_PauseAudioDevice` | поток звука гостя — порт вибрации-звука (исключение п. 451(д)(2); F19a §1.6) |
| `:508`–`:509` | `HapticsOutput::CloseLocked` | `SDL_ClearQueuedAudio`, `SDL_CloseAudioDevice` | поток звука гостя (из `Push`) или поток выхода (из `Stop`) |
| `:593`–`:598` | `HapticsOutput::Push` | `SDL_GetQueuedAudioSize`, `SDL_ClearQueuedAudio`, `SDL_QueueAudio`, `SDL_GetError` | поток звука гостя (исключение) |
| `:870`–`:871` | `GameController::Connect` | `SDL_GameControllerFromInstanceID`, `SDL_GameControllerGetType` | главный поток (`GameEventController` после `SDL_GameControllerOpen`, `window.cpp:384`–`:399`); из `Initialize` — id −1000, вызова нет (`id >= 0`) |
| `:1148`–`:1166` | `GameController::ReleaseHostPads` | `SDL_GameControllerFromInstanceID`, `SDL_GameControllerGetType`, `SDL_GameControllerSendEffect`, `SDL_GameControllerRumble`, `SDL_GameControllerSetLED`, `SDL_Delay`, `SDL_GameControllerClose` | поток выхода (`EmergencyShutdown`), после `PadOutput::Stop` |
| `:1188`–`:1198`, `:1212`–`:1215`, `:1251`–`:1257` | `SetVibration`, `SetLightBar`, `SetTriggerEffect` | прежние вызовы | поток гостя **только при `=0`**: при `=1` ветка возвращается раньше (`:1176`–`:1180`, `:1204`–`:1208`, `:1242`–`:1247`) |

Других вызовов `SDL_` в файле нет (поиск `\bSDL_\w+\s*\(` по `9c726d74:src/libs/controller.cpp`). До ветки `=1` `SetTriggerEffect` зовёт только `trigger_effect_to_dualsense` — без SDL. **Член «при `=1` ни одного вызова SDL из `controller.cpp` на потоках гостя, кроме порта вибрации-звука» — выполнен.**

## 3. Жизнь `PadOutput` [c]

- **Создание раз:** `:832`–`:833` в `Initialize` после `EXIT_IF(g_controller != nullptr)` (`:826`), только при `=1`; `Start` — единственный вызов (`:222`–`:224`).
- **Остановка до `ReleaseHostPads` на всех путях выхода:** `EmergencyShutdown` (`:851`–`:862`) — `Stop` (`:857`) до `ReleaseHostPads` (`:860`). Его зовут `WindowShutdown` (`window.cpp:1063` — до `g_window.reset()`, с которым идёт `SDL_QuitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER)`, `vulkanWindow.cpp:1320`), `Subsystems::EmergencyShutdown` (`common/subsystems.cpp:28`–`:35`) из `DbgReport` (`common/assert.cpp:25`), `DbgExit` (`common/assert.cpp:118`), `KytyClose` (`emulator.cpp:79`, `atexit`) и `at_quick_exit` (`emulator.cpp:243`); `Shutdown` (`:841`–`:849`) зовёт `EmergencyShutdown` первым.
- **Нет обращения к закрытому `SDL_GameController*`:** поиск и вызов — под `SDL_LockJoysticks` (`:339`/`:348`, `:356`/`:360`, `:365`/`:370`); `SDL_GameControllerClose` держит тот же замок от проверки до `SDL_free` (`4b69833b:src/joystick/SDL_gamecontroller.c:3030`–`:3072`, замок `:3034`); `SDL_GameControllerFromInstanceID` ссылки не берёт, указатель действителен до снятия внешнего замка (`:2849`–`:2863`); мьютекс рекурсивный (`4b69833b:src/thread/windows/SDL_sysmutex.c:84`–`:85`) — вложенные захваты в `Rumble`/`SetLED`/`SendEffect` не блокируют. Стенд (iii): 143 / 142 отключения при 2 × 10 000 записях — 0 падений; 7 строк `rumble failed` — ответ SDL отсоединённому, ещё не закрытому пульту [c вывода].
- **Ожидание выхода, пока `PadOutput` стоит в замке (п. 457(в)) [I]:** при `=1` `Stop` ждёт `join`; при `=0` в том же состоянии поток гостя стоит в том же замке **под `m_mutex`** (вывод пада — каждый кадр), и `ReleaseHostPads` ждёт `m_mutex` (`:1141`) — то же ожидание, в том числе без пульта хоста (при `=0` `SetLightBar` / `SetTriggerEffect` берут замок джойстиков и для id −1000). Держатель замка на выходе — не главный поток (главный либо сам выходит, либо исполняет задачу `hold`). Новых бесконечных ожиданий правка не вводит.
- **Повторный вход `Stop` — RC1.**

## 4. Слот и копия идентификатора [c]

- Слоты, поколения, копия `m_active_id` / `m_active_ps5` и `m_stop` — под `PadOutput::m_mutex` (`:206`–`:217`); `Post*` пишут под ним; `Loop` (`:292`–`:330`) под ним берёт копии и отмечает поколения, применяет без него; предикат ожидания — поколения и `m_stop` ⇒ потерянного пробуждения нет; запись во время применения меняет поколение ⇒ следующий проход берёт последнее значение (стенд (ii): последнее из трёх значений, записанных под удержанием, получено через 259 мкс после отпускания [c вывода]).
- Порядок замков: `GameController::m_mutex` → `PadOutput::m_mutex` (`CheckActive` → `SetActive`, `:934`–`:938`); обратного нет — `PadOutput` `GameController::m_mutex` не берёт, SDL зовёт без замка слота; гость при `=1` берёт только замок слота; замок джойстиков берётся без замков эмулятора. Цикла нет.
- Копия id: единственное присваивание `GameController::m_active_id` — `:925` в `CheckActive`, следом `SetActive` ⇒ копия равна `m_active_id`, кроме `ReleaseHostPads` (список очищен без `CheckActive`) — после `Stop`, применений нет. Первая копия — `Connect(HOST_INPUT_CONTROLLER_ID)` (`:838`), объект создан раньше (`:832`).
- `g_fix_b24`: записи — только `:178` (инициализация) и `:829` (`Initialize`, до потоков гостя); других в `src/` и `tests/` нет (`git grep` по `9c726d74`) — проверка п. 457(б) ✓. `g_pad_output`: `:832` (до потоков гостя) и `:848` (`Shutdown`; удаление после `delete g_controller` — тот же класс, что `delete g_controller` до правки; путь `Subsystems::Destroy` — без потоков гостя по комментарию `kernel/fileSystem.cpp:414`).

## 5. Стенд `KYTY_TEST_HIDLOSS` и счётчики [c]

- **Окружение — раз на процесс:** `static const TestHidLossConfig cfg = TestHidLossReadConfig();` (`window.cpp:1283`) — локальная статика (потокобезопасная инициализация) при первой записи гостя; взвод раз — `armed.exchange` (`window.cpp:1288`).
- **Стенд выключен — на пути вывода пада одна проверка статического флага:** `PadCallProbe` — одна `relaxed`-загрузка `g_hidloss_window` на вызов ✓ (`if (g_fix_b24)` — проверка ручки, не стенда, A5).
- Режимы `detach` / `hold` / `sleep`, иное значение — `config invalid`, константы `PRE_S` 10 с, `HOLD_MS` 3000, `PROBE_MS` 20 (`window.cpp:1080`–`:1082`), взвод строкой `Level has started: <непустое имя>`, виртуальный пульт по п. 451(в) (`window.cpp:1159`–`:1176`), `fire` задачей главного потока (`window.cpp:1179`–`:1205`), пульт остаётся в `hold` / `sleep` — по п. 451(в) ✓.
- Поля строки `stat` и их порядок = F19a §6.1 (`window.cpp:1216`–`:1223`); все — `std::atomic<uint64_t>` `relaxed`, флаги окна — `std::atomic<bool>`; записей в состояние гостя нет; единицы — мкс и штуки; шкалы не смешиваются: `pad_*` / `po_*` — разности `steady_clock` (`PadNowUs`), `main_late_max_us` и `t_us` — разности `FrameStats::NowNs`.
- Инварианты и тождества F19a §6.1:

| Член | Чем обеспечен | Что значит в теге F19e |
|---|---|---|
| `pad_calls = pad_vib + pad_led + pad_trig` | печатается суммой (`window.cpp:1220`) | тавтология — проверяет ридер, не эмулятор |
| `probes_posted − probes_run = 0`, `probes_run ≤ probes_posted` | `probes_posted` растёт до постановки; задача `stat` ставится последней; очередь главного потока — FIFO (`window.cpp:827`–`:836`, `DrainMainThreadTasks`) | по построению; провал — потеря задачи главного потока |
| `guest_sdl = 0` при `=1` | ветка возврата стоит до всех `probe.Sdl()` | тавтология (N1) |
| `po_applied = po_wait_max_us = 0` при `=0` | объекта `PadOutput` нет | по построению |
| `removed` = 1 в `detach`, 0 в `hold` / `sleep` | счёт в обработчике удаления при открытом окне (`window.cpp:406`) | сигнал |
| `t_us`: `armed` < `attach` < `fire` ≤ `done` | одна шкала | сигнал |

## 6. `*sent` `SetTriggerEffect` [c]

Гость `*sent` не получает: `PadSetTriggerEffect` (`:1586`–`:1611`) возвращает `ok ? OK : PAD_ERROR_INVALID_ARG`, `sent` идёт только в строку `PadTriggerEffect: … sent=` (`:1604`–`:1607`). При `=1` `sent` — копия «активный пульт PS5» (`:1245`), то есть «эффект в слоте», не «SDL принял». Возврат гостю не меняется ✓ (N3).

## 7. Стенд без игры и бинарь теста (п. 451(д)(1), (3))

- **(д)(1)** [c `45080d53:docs/track-f/f19c/runs/stand_f19c.txt`, `docs/track-f/f19c/run_stand_f19c.py`, `tests/B24PadStand.cpp`]: пороги драйвера = буква (i)–(iii) (2 700 000 / 50 000 / 100 000 мкс); 7 из 7 `PASS`, `ALL OK`; `GameController` — тот же исходник (цель линкует `src/libs/controller.cpp`); `num_joysticks_at_init` 0 во всех 7. «Последнее применённое = последнему записанному» в (iii) проверяется одной записью после конца перетасовки (`B24PadStand.cpp:347`–`:355`); схлопывание под занятым замком показывает (ii) — вместе член выполнен.
- **(д)(3)** [c пересчёта, `times.txt` 12:27:32Z]: `git cherry 9c726d74 52d2f546 4d9e8ab7` → `- 52d2f546…` ✓; родитель `52d2f546` — `4d9e8ab7`; `patch-id --stable` коммита `9c726d74` = дифф `4d9e8ab7..52d2f546` = `875b7df3d796`; sha256 `C:/kyty/f287/bin/kyty_emulator_9b00ad40.exe` = `9b00ad40acc8…`; установленный `kyty_emulator.exe` = `adb0c82f1a75…` (не тронут).

## RC

**RC1 (код, `:226`–`:239`) — `PadOutput::Stop` не выдерживает одновременного вызова с двух потоков.** `m_thread` читается и присоединяется вне замка (комментарий `:205`: «только Start и Stop»), а `Stop` достижим с двух потоков сразу: `Controller::EmergencyShutdown` зовут `WindowShutdown` (главный поток, `window.cpp:1063`) и `Subsystems::EmergencyShutdown` из фатала любого потока (`common/assert.cpp:25`, `:118`) и `at_quick_exit` (`emulator.cpp:243`) без взаимного исключения (`common/subsystems.cpp:28`–`:35`); одновременный аварийный обход на выходе — строка Ф21 (`630a8cf1:docs/ROADMAP.md:21921`, якорь «(е) **Ф21 (новая строка) — K1 при выходе, наблюдение, паркуется**»; +1 — «`Subsystems::EmergencyShutdownActive` (`assert.cpp:22` → `DbgReport`) с потока гостя»). **Сценарий отказа:** `KYTY_FIX_B24=1`; выход совпадает с фаталом гостя; поток 1 прошёл `joinable()` и стоит в `join()` (`PadOutput` дорабатывает применение, вплоть до времени удержания замка джойстиков); поток 2 видит `joinable()` = `true` и зовёт `join()` того же `std::thread` — гонка данных на объекте (UB); в MSVC STL второй `_Thrd_join` закрывает уже закрытый или переиспользованный дескриптор ⇒ `std::system_error` ⇒ `std::terminate` ⇒ `abort` (K1 на выходе) или закрытие чужого дескриптора. При `=0` та же пара вызовов в части `Controller` безопасна: `HapticsOutput::Stop` — под своим мьютексом (`:471`–`:475`), `ReleaseHostPads` — под `m_mutex`, второй проход видит пустой список; это ухудшение `=1` относительно `=0`. **Что изменить:** забирать поток под замком слота — в блоке с `m_stop = true` перенести `m_thread` в локальный `std::thread`, затем `notify_all` и `join` / `detach` локального; второй вызов видит не-`joinable` и возвращается. Его ранний переход к `ReleaseHostPads`, пока первый ещё ждёт `join`, безопасен: применение `PadOutput` и закрытие пульта сериализованы замком джойстиков (§3). Теги F19e гонку выхода не проходят ⇒ бинарь `9b00ad40` идёт в F19e без изменений; RC1 — кодом и отзывом до бинаря отгрузки с умолчанием `KYTY_FIX_B24=1` (форма F14f → F14e2 / F14f2). Исполнитель — Emu Engineer, звено назначает лид.

## Вопрос лиду

**Q1.** Список добавок пути `=0` п. 457(б) («`PadCallProbe`, `probe.Sdl()`, строка `Controller <id>: removed`, проверка окна стенда на событии удаления и проверка статической конфигурации на записи гостя; иная добавка — «Доработать»») не называет A5–A11 (§1). **По букве п. 457(б)** — «Доработать» (текстом: F19c §1.1 называет только A1–A2). **Вариант исполнителя** (по нему вынесен вердикт): не «Доработать» — каждая из A5–A11 либо требуется самим п. 451(г) (чтение ручки раз на процесс, ветка в трёх функциях, копия в `CheckActive`, остановка до `ReleaseHostPads`, удаление объекта), либо операция над всегда пустым контейнером или `nullptr`; ни одна не зовёт SDL, не берёт замок, не меняет порядок вызовов и возвраты. Решение — за лидом.

## Замечания (сценария отказа результата нет; не RC)

- **N1 — тавтологии в членах тегов.** `guest_sdl = 0` при `=1` (`b24_h1`) по коду расти не может: информации сверх этого ревью не несёт; информативны `pad_wait_max_us < 50 000` при `po_wait_max_us ≥ 2 700 000`. `pad_calls` — печатная сумма. Печать F19e называет это так.
- **N2 — путь эффекта курков при `=1` не исполняется ни стендом, ни тегами.** Виртуальный пульт без VID/PID DualSense — тип не PS5 ⇒ `effect_calls` 0 во всех 7 прогонах стенда [c], `vp_effect` 0 во всех тегах по построению; `ApplyTriggerEffect` и `sent=1` проверены только чтением (тело — копия ветки `=0`). Положительный контроль возможен пультом с `vendor_id` 0x054C / `product_id` 0x0CE6 (GUID строится из них — `4b69833b:src/joystick/virtual/SDL_virtualjoystick.c:194`; что тип станет PS5 — [I]). В член не входит.
- **N3 — `sent=` строк `PadTriggerEffect:` на логах `=1` — не доставка** (§6); ридеры их так не читают.
- **N4 — отличия поведения `=1`, не дефекты:** значение применяется к пульту, активному в момент применения (п. 457(в)); внутри прохода порядок вибрация → цвет → эффект независимо от порядка гостя; схлопывание до последнего значения; при активном id хоста поток будится на каждую запись гостя — вибрация возвращается без SDL (`:334`), цвет и эффект делают те же вызовы, что `=0` с id −1000. Цена — одно пробуждение на вызов [I].
- **N5 — поток стенда на выходе.** Отсоединённый поток стенда читает `g_window.get()` (`window.cpp:1227`) без синхронизации с `g_window.reset()` (`window.cpp:1064`): процесс, закончившийся внутри окна стенда (от `attach` до `stat`), может обратиться к удалённому окну. Та же форма у стенда F5 (`KYTY_TEST_MINIMIZE`); теги п. 451(д)(4) кончаются далеко после `stat`. Только стенд.

## Чек-лист кода

- Хронометрируемая строка: `PadCallProbe` — от входа до возврата, включая ожидание `m_mutex` (деструктор пробы после деструктора `lock`) ✓; `PadOutputApply` — вокруг одного применения ✓.
- Гонки: §4 ✓; повторный вход — RC1.
- Инварианты `*_bad`: в эмуляторе нет; `rumble_bad` стенда на корректном пути недостижим ✓.
- Ранние возвраты: проба `SetTriggerEffect` стоит до `*sent = false` и считает ранние возвраты по маске («входы гостя», F19a §6.1) ✓; `SetVibration` при id хоста — возврат до SDL, стена считается ✓.
- Патч — скриптом `patch_f19c_src.py` (LF, якоря целыми строками; F19c §1); дифф коммита чист, побайтно скрипт не перепроверялся.
- Кадр стека на потоке гостя: новых больших кадров нет (`PadCallProbe` — 16 байт, `DualSenseEffects` — 32 байта).
- Подпись трансляции: правка вне `src/graphics/shader/**` и `SHADER_CACHE_EXTRA_FILES` ✓ (`26ce5fc7` = S12, [c F19c §4]).
- Инструмент меняет прогон: стенд меняет состояние хоста (виртуальный пульт) — по назначению; при выключенном стенде — одна загрузка флага ✓.

## Не заявляется

Что Б24 `FIXED` (F19f); что настоящая потеря пульта после правки не останавливает игру; что Б24 воспроизводим без оборудования; какой вызов и поток держал замок джойстиков 23,8 с в `edes122`; что стенд `hold` в игре даёт кадр ≥ 1 с; что машинный код `=0` равен прежнему; что Ф8 воспроизводится на установленном бинаре до тега `f8_n0`; что Ф6 — дефект или не дефект до F16g; что Б4 `FIXED` до F15f; что Ф19 `FIXED` до F14h; что Б2 или Б32 — не дефект до F20b; что реестр полон; ни одно число — не выигрыш; 60 FPS не обещаются.
