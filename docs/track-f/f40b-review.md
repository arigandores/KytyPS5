# F40b — код-ревью `KYTY_FIX_F24` и стенда `KYTY_TEST_HIDLOSS` издания 2, мутанты m1–m6 (Red Team, `HPP-771`)

**Вердикт: `PASS_WITH_FIXES`.** Код правки (`5c21c387`) — PASS по существу: вариант Б, предел ожидания, открытие по номеру
экземпляра и правило остановки сделаны верно, `=0` по коду прежний, правка вне `src/graphics/shader/**`. RC — 3 (RC1, RC2 —
кодом в одном звене доработки до тега; RC3 — чтением). Из-за RC1–RC2 бинарь тега `3f06d311` в F40c не идёт; бинари мутантов
и сборка из чистого worktree — на бинаре доработки (причина — ниже, раздел «Мутанты»).

Задание — `ROADMAP.md` «СЕССИЯ 122» п. 692(г)(3) (KytyPS5 `5842bf43`); прочитаны п. 692 целиком, п. 691(е)–(з), F39a §0–§2
(`20ba81a4`), F39b RC1–RC7 (`848a6739`), отчёт F40a (`b46eb460`, §0 — `23c25ef4`), review лида F40a (2026-10-11 01:15:54Z,
заметки (1)–(4)). Код — `e3aa4b4d` (`main`: код `5c21c387` + стенд); SDL2 — подмодуль `4b69833b`. Ссылки
`<коммит>:<путь>:<строка>` — с якорем и контролем +1: `f40b/refs_f40b.py check` и `text` (`ALL OK`). Игра, установленный
FS12 `46892c20`, `C:/kyty/build`, `C:/kyty/build/install` и кэши не использовались; сборок в этом звене нет.

## §1. Члены п. 692(г)(3)

| Член | Итог | Основание |
|---|---|---|
| `=0` по коду прежний | ✓ | Дифф `5c21c387` (6 файлов): ветвь `=0` — `else` с прежним телом в `GameEventController` (добавление — `e3aa4b4d:src/graphics/presentation/window/window.cpp:390`, удаление — `e3aa4b4d:src/graphics/presentation/window/window.cpp:420`), `WindowCreate` (`e3aa4b4d:src/graphics/presentation/window/window.cpp:959`), `HostInputWaitEvent` (`e3aa4b4d:src/graphics/presentation/window/hostInput.cpp:458` — прежнее тело после проверки), `~WindowContext`, `EmergencyShutdown` (вызов остановки под `Enabled()`), `Shutdown` (`e3aa4b4d:src/libs/controller.cpp:859`: при `=0` `Exited()` = `!m_started` = `true`). Новое при `=0`: `ReadKnob` + строка `FixF24: mode=0 b24=…`, загрузки атомика, ленивый `new Pump` в `Exited()`/`StandRead()` (поток не создаётся, `CreateEventW` не зовётся). Стенд без переменной — две `relaxed`-загрузки. Н4 — строки издания 1 изменились |
| Одно чтение ручки | ✓ | `e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:380` (`done.exchange`, второй вызов — ничего), `e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:383` — единственное чтение `KYTY_FIX_F24`; дальше только атомик `g_enabled` |
| Вариант Б: инициализация и всё использование API джойстиков и пультов при `=1` — на `JoyPump` | ✓ | Инициализация — `e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:153` на потоке `ThreadMain`; главный поток ждёт (`e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:140`), затем 0 вызовов. Свой `git grep` вызовов `SDL_GameController*`/`SDL_Joystick*`/`SDL_NumJoysticks`/`SDL_LockJoysticks`/`SDL_IsGameController` по `e3aa4b4d:src` без `src/launcher`: главный поток — только ветвь `=0` и стенд (присоединение, `detach`, `hold`); `JoyPump` — обход/открытие/закрытие/`Connect` (`SDL_GameControllerFromInstanceID`/`GetType` при `KYTY_FIX_B24=1`); `PadOutput` и гость при `KYTY_FIX_B24=0` — под замком SDL; `ReleaseHostPads` — после остановки `JoyPump`. Наблюдателей событий (`SDL_AddEventWatch`/`SDL_SetEventFilter`) в коде эмулятора нет — на `JoyPump` под замком джойстиков чужой код не исполняется. COM на главном потоке код эмулятора не использует (свой `git grep` MF/WIC/DXGI/DirectSound/`IFileDialog` — 0) |
| (г)(0) своим чтением SDL2 | ✓ | Вспомогательное окно — во внутреннем `SDL_InitSubSystem(SDL_INIT_JOYSTICK)` (`4b69833b:src/SDL.c:229`), т. е. на `JoyPump`; окно обнаружения HIDAPI — лениво, но первым вызовом из `HIDAPI_JoystickInit` (`4b69833b:src/joystick/hidapi/SDL_hidapijoystick.c:625` → `4b69833b:src/hidapi/SDL_hidapi.c:365` → `4b69833b:src/hidapi/SDL_hidapi.c:240`), т. е. на потоке инициализации; окно уведомлений `Message` — `4b69833b:src/joystick/windows/SDL_windowsjoystick.c:302`; насос главного потока без обновления джойстиков — `4b69833b:src/events/SDL_events.c:922`, интервал без замка — `4b69833b:src/events/SDL_events.c:967`; `SDL_JoystickUpdate` держит замок всё обновление — `4b69833b:src/joystick/SDL_joystick.c:2177`…`4b69833b:src/joystick/SDL_joystick.c:2193`. Договор SDL при варианте Б не нарушен — согласен с F40a §0.2 |
| Предел ожидания главного потока (RC1) | ✓ | `e3aa4b4d:src/graphics/presentation/window/hostInput.cpp:430` (1 мс / 3 000 мс по атомику `JoyPump`), без мыши — `e3aa4b4d:src/graphics/presentation/window/hostInput.cpp:434`, с мышью — `min` (`e3aa4b4d:src/graphics/presentation/window/hostInput.cpp:446`). Гонка — между `4b69833b:src/events/SDL_events.c:1008` и `4b69833b:src/events/SDL_events.c:1035` (подтверждаю); внутри SDL `loop_timeout` ≤ предела ⇒ потерянное пробуждение держит не дольше предела. Цикл `Run` на `false` идёт на следующий оборот (`DrainMainThreadTasks`, без побочных действий). Н3 — устройство-не-пульт |
| Открытие по номеру экземпляра (RC2) | ✓ | Обход под замком — `e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:279`, номер — `e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:283`, открытие — `e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:289`, `nullptr` — строка и пропуск; `Connect` вне замка — `e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:328`, затем сверка `GetAttached` и `Disconnect` (порядок замков `m_mutex` → замок SDL не обращается). Событие добавления при `=1` — только строка (`e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:403`); закрытие — задача (`e3aa4b4d:src/graphics/presentation/window/window.cpp:420`) |
| Правило остановки (RC4) на обоих путях выхода | ✓ | Первым в `EmergencyShutdown` — `e3aa4b4d:src/libs/controller.cpp:873` (путь `quick_exit`/фатал и путь `Shutdown`); флаг — `e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:346`; вход с самого `JoyPump` — `detach` без ожидания себя (`e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:356`); истечение — строка и `detach` (`e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:370`); проверки флага — перед задачей (`e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:204`), после обновления (`e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:185`), перед `Connect`; `delete g_controller` — только при `Exited()`. Взаимного ожидания с `ReleaseHostPads` нет: после истёкшей остановки `ReleaseHostPads` ждёт замок SDL до конца обновления `JoyPump`, а `JoyPump` после обновления выходит, `m_mutex` не берёт. Н1 — окно проверки и выборки задачи |
| Код стенда издания 2 построчно | ✓ с RC2 | §3 |
| Подпись трансляции не меняется | ✓ | `git diff --stat 730ed40a dfc037e9 -- src` (worktree) = `git diff --stat 5c21c387^ e3aa4b4d -- src` (`main`): 6 файлов, путей `src/graphics/shader/**` — 0 и 0; изменённые строки диффов равны (1 074 = 1 074) — `f40b/diffstat.txt` |
| Сборка из чистого worktree, sha256 = копии F40a | перенесено | Бинарь тега меняется доработкой RC1–RC2 — повторная сборка `3f06d311` проверила бы бинарь, который в тег не идёт. Член — в F40b2 на бинаре доработки. Worktree F40a: HEAD `dfc037e9`, `git status` — 0 строк, `git cherry main HEAD` — `-` у `e0b4f2ba` и `dfc037e9`, sha256 закреплённой копии = `3f06d311bbe0ef19…` (`f40b/wt_check.txt`) |

Заметки лида к F40b (review F40a): (1) — RC1 ниже; (2) `cls` недостижим — подтверждаю [c]: отсоединение обнуляет `hwdata` открытого пульта (`4b69833b:src/joystick/virtual/SDL_virtualjoystick.c:73`), `VIRTUAL_JoystickRumble` без `hwdata` описатель не зовёт (`4b69833b:src/joystick/virtual/SDL_virtualjoystick.c:429`, `4b69833b:src/joystick/virtual/SDL_virtualjoystick.c:437`), хотя `SDL_JoystickClose` вызов вибрации делает (`4b69833b:src/joystick/SDL_joystick.c:1594`); замена m4 на `f24_d1` по `jp_tasks` — годна, ловит детерминированно; (3) `Start` ждёт без предела — Н2; (4) задержка задач `flap` — только стенд, согласен.

## §2. RC

**RC1 (член m6 тавтологичен — свидетель потока инициализации).** Строка `FixF24: init tid=…` пишется `LOGF` рядом с
`SDL_InitSubSystem` (`e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:151`, `e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:153`),
а `init tid` и `pump tid` — одно и то же `SDL_ThreadID()` на `JoyPump` (`e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:148`).
Строка доказывает, где стоит печать, а не где прошла инициализация. **Сценарий отказа:** мутант m6 (вариант А — инициализация
на главном потоке) в форме `mut_f40b.py m6` переносит только `SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER)` (строка остаётся на
`JoyPump`) ⇒ `init tid` = `pump tid` ≠ `main tid` ⇒ по члену п. 692(г)(3) m6 «не пойман», хотя окна HIDAPI и уведомлений,
вспомогательное окно и объект DirectInput — у главного потока (тот же дефект, что вариант Б снимает). Если же мутант
переносит и печать — «пойман» построением (заметка лида (1) это и говорит). В обоих случаях член ничего не измеряет.
**Правка (код, звено доработки):** после успешной инициализации `JoyPump` пишет строку `FixF24: init_owner hid=<tid>
helper=<tid> msg=<tid> pump=<tid>`, где каждый `<tid>` — `GetWindowThreadProcessId` окна своего процесса, найденного
`FindWindowExW(HWND_MESSAGE, …)` по классу (`SDL_HIDAPI_DEVICE_DETECTION` — `4b69833b:src/hidapi/SDL_hidapi.c:240`;
`SDLHelperWindowInputCatcher` — `4b69833b:src/video/windows/SDL_windowswindow.c:56`; `Message` — `4b69833b:src/joystick/windows/SDL_windowsjoystick.c:302`),
с отбором по `pid` = `GetCurrentProcessId()` (классы есть у любого процесса на SDL2); не найдено — `0`. Строка только при `=1`
(при `=0` член (г)(2) «других строк `FixF24:` нет» сохраняется). Член `f24_u1`/`f24_n1`: `hid` = `helper` = `pump` ≠ `main tid`
(`msg` — числом: окно может не создаться); член m6 (`f24_m6`): `hid` = `main tid` или `helper` = `main tid`. Положительный
контроль свидетеля — сам m6 (окна — главного потока). Без правки m6 в форме «перенос только вызова» не ловится, а F40d по
букве п. 692(г) (каждый мутант, кроме m3, пойман) не дойдёт до `FIXED`, либо дойдёт по тавтологии.

**RC2 (плечо `flap`: запас по времени жизни пульта не измеряется).** Плечо держит пульт 2 шага `PROBE_MS` (≈ 40 мс) при
задержке задач 50 мс; доказательство «задача по индексу не может открыть свой пульт» (комментарий стенда) и «правка успевает
открыть каждый» стоят на этих двух числах, а стенд не пишет ни фактическое время жизни пультов, ни промежутки между обходами
`JoyPump`. **Сценарии отказа:** (а) `f24_f1` на верном коде: `JoyPump` снят планировщиком на > 40 мс в окне 1,2 с (игра,
трансляция, запись лога) ⇒ один пульт умирает до обхода ⇒ `opened` = `attached` − 1 ⇒ провал (1) «по вине правки» по
п. 692(г) — итерация засчитывается за помеху; (б) `f24_m1`: поток стенда проспал > 10 мс в первых шагах (`sleep_for(20 мс)` +
работа шага) ⇒ пульт 0 живёт > 50 мс ⇒ задача по его индексу может открыть его самого ⇒ m1 уходит неучтённым (ловля m1
детерминирована только при жизни пульта 0 < задержки: раньше задачи пульта 0 ни одна задача не исполняется). **Правка
(стенд, то же звено):** в строку `TestHidLoss: f24` — `flap_life_min_us`, `flap_life_max_us` (отсоединение − присоединение по
слотам) и счётчик `JoyPump` в окне стенда `jp_scan_gap_max_us` (наибольший промежуток между началами `ScanAndOpen`). Допуск
плеча `flap` (член печати F40c, до данных): `flap_life_max_us` < `FLAP_TASK_DELAY_MS`·1000 и `jp_scan_gap_max_us` <
`flap_life_min_us`; не выполнен — помеха прогона (п. 273(з)), попытка не тратится. При допуске: `f24_f1` — `opened` =
`attached`; `f24_m1` — пойман при `opened` < `attached`.

**RC3 (чтение m5 — решение лида, не код).** При m5 (подсказка не ставится) `SDL_JoystickUpdate` зовут оба потока — насос
главного (`4b69833b:src/events/SDL_events.c:922`) и `JoyPump`; взведённый `Update` пульта стенда достаётся тому, кто первым
возьмёт замок. **Сценарий отказа:** первым успевает `JoyPump` ⇒ `upd_on_main` = 0, а главный поток 8 с стоит на замке в своём
`SDL_JoystickUpdate` (`4b69833b:src/joystick/SDL_joystick.c:2177`) ⇒ по букве п. 692(г)(3) «m5 — `f24_u1` (`upd_on_main` = 1)»
мутант «не пойман» ⇒ лишнее звено доработки стенда. **Правка (пункт лида до тега `f24_m5`):** m5 пойман, если провален хотя
бы один из членов `f24_u1`: `upd_on_main` = 0, `main_late_max_us` < 100 000, `in_lat_max_us` < 100 000.

## §3. Стенд издания 2 (`e3aa4b4d`, только `window.cpp`) — построчно

- Перехват `VK_F13` и кнопки A пульта стенда первым в `ProcessEvent`; `k`-е увиденное — `k`-е поставленное (время и номер
  до `PostMessage` / под замком джойстиков) — верно; при выключенном стенде — одна загрузка.
- `upd`: `upd_armed` — `exchange` в обратном вызове `Update` на потоке обновления; `IsMainThread` — поток насоса. Если пульт
  стенда не открыт (`open failed` при `=1`), `done` не наступает и строки `f24` нет — член печати F40c «строка `f24` есть».
- `exit`: задача `JoyPump` в `fire` + 0,5 с ставится во время сна; при верном коде после возврата из обновления `JoyPump`
  выходит по флагу до задач; путь выхода: `quick_exit` → остановка истекает (2 с) → `ReleaseHostPads` ждёт замок до конца
  сна (≈ `fire` + 8 с) → выход ≤ `HOLD_UPD_MS` + 5 с от `quit posted` [c кода].
- `detach`: удаление ставит главный поток (стенд), закрытие — задача ⇒ `jp_tasks` ≥ 1; других задач в окне нет — m4 даёт 0.
- `flap`: RC2. Порядок шага (присоединить `k`, отсоединить `k − 2`) и правка SDL индекса стоящего в очереди события — как в
  F40a §0.4.
- `pad`: подавление заголовка; главный поток будят ещё `SDL_PushEvent` других потоков (оверлей, повтор шейдеров) — «только
  события пульта» [I], на член не влияет.
- Строка `f24`: `pad_lat_p99_us` — `lat[⌈0,99·n⌉ − 1]` — верно; единицы помечены.

## §4. Мутанты (п. 692(г)(3))

Скрипт `f40b/mut_f40b.py` (якоря целыми строками, каждый — ровно один раз, CRLF снимается и возвращается, запись LF);
`check e3aa4b4d` — `ALL OK` (`f40b/mut_check.txt`). **Бинарей в этом звене нет:** RC1–RC2 меняют код и бинарь тега;
мутант, собранный на `3f06d311`, — мутант не того бинаря, что пойдёт в теги. Бинари m1, m2, m4, m5, m6 собирает F40b2
(Red Team) своим worktree на базе доработки тем же скриптом (`apply <m> <worktree>`), sha256 и строка версии — в отзыве F40b2;
там же — член «сборка из чистого worktree».

| Мутант | Правка (`mut_f40b.py`) | Тег F40c, форма вызова | Член, который обязан поймать |
|---|---|---|---|
| m1 — открытие по индексу события | обход по номеру экземпляра выключен; событие добавления на главном потоке ставит задачу `JoyPump` `SDL_GameControllerOpen(<индекс события>)` (`nullptr` — строка, без фатала) | `f24_m1`: `KYTY_FIX_F24=1`, `KYTY_TEST_HIDLOSS=60:flap`, `-lvl underwater_aerial_garden` | при допуске RC2: `opened` < `attached` |
| m2 — проверка флага остановки убрана | `Stopping()` всегда `false` | `f24_m2`: `=1`, `60:exit` | строка `TestHidLoss: jp_task ran` после `FixF24: pump_stop_expired` (запас: `ReleaseHostPads` после замка спит `RELEASE_FLUSH_MS` = 50 мс — `e3aa4b4d:src/libs/controller.cpp:40`, `e3aa4b4d:src/libs/controller.cpp:1187`) |
| m3 — ожидание без предела | бинаря нет (по букве п. 692(г)(3)) | — | член ревью кода: предел есть (`e3aa4b4d:src/graphics/presentation/window/hostInput.cpp:430`, `e3aa4b4d:src/graphics/presentation/window/hostInput.cpp:434`, `e3aa4b4d:src/graphics/presentation/window/hostInput.cpp:446`) ⇒ **пойман ревью**. Плечом `pad` гонка ловится лишь при потерянном пробуждении в окне пробы (окно гонки — мкс на событие, 190 событий) — не ловится наверняка |
| m4 — закрытие на главном потоке | обработчик удаления зовёт `SDL_GameControllerClose` сам (`e3aa4b4d:src/graphics/presentation/window/window.cpp:420`) | `f24_m4`: `=1`, `60:detach` | `jp_tasks` = 0 (член `f24_d1` `jp_tasks` ≥ 1) |
| m5 — подсказка не ставится | строка `e3aa4b4d:src/graphics/presentation/window/window.cpp:951` снята | `f24_m5`: `=1`, `60:upd` | любой из членов `f24_u1` по RC3 |
| m6 — инициализация на главном потоке (вариант А) | `SDL_InitSubSystem(SDL_INIT_VIDEO \| SDL_INIT_GAMECONTROLLER)` на главном (`e3aa4b4d:src/graphics/presentation/window/window.cpp:951`+1), на `JoyPump` инициализации нет; строка `FixF24: init` остаётся на `JoyPump` | `f24_m6`: `=1`, `60:upd` | RC1: `init_owner` `hid` = `main tid` или `helper` = `main tid`; по нынешней строке `init tid` — не ловится (это и есть RC1) |

## §5. Заметки (не RC)

- **Н1.** `RunTasks` проверяет флаг вне `m_mutex` (`e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:204`), выборка — под ним
  (`e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:209`): задача, выбранная в окне между ними, исполняется после флага
  (`e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:220`). Вреда нет: `Stop` ждёт её конца (кроме истечения); при истечении
  на закрытии умирающего пульта `ReleaseHostPads` этого пульта не видит — `Disconnect` прошёл раньше `PostClose`. Проверка под
  `m_mutex` сняла бы окно — по выбору автора при доработке.
- **Н2.** `Start` ждёт инициализацию без предела (`e3aa4b4d:src/graphics/presentation/window/joyPump.cpp:140`) — паритет с `=0`
  (там главный поток сам исполняет ту же инициализацию без предела); окна SDL ещё нет — межпоточного `SendMessage` нет [c],
  зависание вызова ОС — [I].
- **Н3.** Предел 1 мс берётся по числу открытых пультов, у SDL при `=0` — по числу устройств: при подключённом устройстве,
  которое не пульт, потерянное пробуждение чужой постановки ждёт до 3 000 мс против 1 мс при `=0`. Тот же предел SDL даёт при
  `=0` без устройств; номер экземпляра, отмеченный виденным, не открывается повторно и при позднем появлении маппинга (эмулятор
  маппингов во время игры не добавляет).
- **Н4.** Издание 1 изменило строки `TestHidLoss: config on …` (новые поля) и `TestHidLoss: attach …` (` hwnd=`); `detach`
  перешёл на поток издания 2. Ридеры старых тегов по префиксу не ломаются; теги `b24_*` закрыты.
- **Н5.** При открытом пульте при `=1` просыпаются раз в 1 мс два потока (главный и `JoyPump`), при `=0` — один; цена [I],
  видна в `f24_n1`.
- **Н6.** Фильтр фоновых событий SDL читает фокус клавиатуры видео без замка — при `=1` с `JoyPump` для всех пультов (при `=0`
  так же читали потоки WGI) — гонка чтения указателя, вреда нет.

## §6. Что этот отзыв не доказывает

Что код работает в игре (бинарь не запускался ни F40a, ни мной); что вариант Б не ждёт главный поток ни на одном пути ОС;
что стенд воспроизводит причину Ф24 (он воспроизводит место); что правка возвращает ввод пульта в окне блокировки; что-либо о
мыши; частоту Ф24 у пользователя. Ни одно число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется.

## §7. Файлы

`docs/track-f/f40b/`: `refs_f40b.py` (`check`, `text`) и выводы `refs_check.txt`, `refs_text.txt`; `mut_f40b.py`,
`mut_check.txt`; `wt_check.txt`; `diffstat.txt`; `times.txt`.
