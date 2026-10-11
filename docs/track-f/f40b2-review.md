# F40b2 — ревью правок F40a2, сборка из чистого worktree, бинари мутантов m1, m2, m4, m5, m6 (Red Team, `HPP-786`)

**Вердикт: `PASS`.** RC — 0. Правки F40a2 (`57f9e528` в `main`, `7c38e497` в worktree тега) делают ровно п. 696(б)(1) и (б)(2),
прочего кода не трогают (п. 696(б)(4)); подпись трансляции не меняется. Своя сборка из чистого worktree — sha256 другой, причина
названа (путь worktree и метка времени PE), код по функциям `ALL OK` (форма п. 693(а)). Пять бинарей мутантов собраны на базе
F40a2, у каждого — одна строка версии, подпись трансляции `9177b426…` = FS12. Бинарь тега F40c — копия F40a2
`ddf0ca91…` без изменений.

Задание — `ROADMAP.md` «СЕССИЯ 122» п. 696 (KytyPS5 `8ee07fbb`), подпункты (б)(1)–(б)(5), (г); прочитаны п. 696 целиком,
п. 692(г)(3), свой отзыв F40b `b1f6b8e7:docs/track-f/f40b-review.md` (§4 — таблица мутантов) и отчёт F40a2
(`09efc6a6:docs/track-f/f40a2.md`). Без игры и без замка; `main`, установленный FS12 `46892c20`, `C:/kyty/build`,
`C:/kyty/build/install` и кэши не трогались; мутанты — коммитами без ветки в своём worktree `C:/kyty/f287/f40b2/wt`.
Ссылки `<коммит>:<путь>:<строка>` — с якорем и контролем +1: `f40b2/refs_f40b2.py check` — 38 из 38 `ALL OK`, `text` по
этому файлу — `ALL OK`. Время — `f40b2/times.txt` (`date -u` в момент события). Предыдущий хартбит этого звена отменён
оператором доски на чтении диффа (комментарий 02:08:02Z); работа сделана заново в этом хартбите, файлов он не оставил.

## §1. Строка `FixF24: init_owner` (п. 696(б)(1)) — построчно

| Член | Где | Итог |
|---|---|---|
| Окно своего процесса по классу: `FindWindowExW(HWND_MESSAGE, <предыдущее>, cls, nullptr)` по всем окнам класса, `GetWindowThreadProcessId`, отбор `pid` = `GetCurrentProcessId()`; нет — `0` | `7c38e497:src/graphics/presentation/window/joyPump.cpp:63`, `7c38e497:src/graphics/presentation/window/joyPump.cpp:73` | ✓ |
| Классы: `hid` — `SDL_HIDAPI_DEVICE_DETECTION`, `helper` — `SDLHelperWindowInputCatcher`, `msg` — `Message`; `pump` — `GetCurrentThreadId()` `JoyPump` | `7c38e497:src/graphics/presentation/window/joyPump.cpp:87`, `7c38e497:src/graphics/presentation/window/joyPump.cpp:88`, `7c38e497:src/graphics/presentation/window/joyPump.cpp:89` | ✓ имена классов = SDL2 `4b69833b` (свой `grep`) |
| Только при `=1`: `LogInitOwner` зовётся только из `Pump::ThreadMain`, поток `JoyPump` запускает только `Pump::Start` из ветки `JoyPump::Enabled()` | `7c38e497:src/graphics/presentation/window/window.cpp:940` | ✓ при `=0` строки нет |
| После успешной инициализации: под `if (ok)` сразу за `SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER)` и **до** `m_init_done = true` (главный поток ещё ждёт) | `7c38e497:src/graphics/presentation/window/joyPump.cpp:205`, `7c38e497:src/graphics/presentation/window/joyPump.cpp:207`, `7c38e497:src/graphics/presentation/window/joyPump.cpp:211` | ✓ |
| `main` — `GetCurrentThreadId()` потока, вызвавшего `Pump::Start` (главный в `WindowCreate`), запись до создания потока (создание упорядочивает) | `7c38e497:src/graphics/presentation/window/joyPump.cpp:184` | ✓ одно пространство идентификаторов ОС с владельцами окон |

**Кто создаёт окна на верном коде [c исходника SDL2 `4b69833b`].** Главный поток при `=1` зовёт только видео
(`7c38e497:src/graphics/presentation/window/window.cpp:936`). Вспомогательное окно создаётся в начале `SDL_InitSubSystem`, если
в флагах есть джойстик (`4b69833b:src/SDL.c:229`); флаги `SDL_INIT_GAMECONTROLLER` бит джойстика не несут, но инициализация
пультов рекурсивно зовёт `SDL_InitSubSystem(SDL_INIT_JOYSTICK)` на том же потоке (`4b69833b:src/SDL.c:335`) — окно на `JoyPump`.
Окно обнаружения HIDAPI создаётся лениво (`4b69833b:src/hidapi/SDL_hidapi.c:365`, `4b69833b:src/hidapi/SDL_hidapi.c:240`), первый
вызов — из инициализации драйвера HIDAPI (`4b69833b:src/joystick/hidapi/SDL_hidapijoystick.c:625`) — тоже на `JoyPump`. До
`Pump::Start` главный поток SDL-функций джойстиков и HIDAPI не зовёт (свой `grep` `SDL_INIT_GAMECONTROLLER|SDL_INIT_JOYSTICK|
SDL_INIT_HAPTIC|SDL_hid_` по `src` worktree: только `joyPump.cpp:205`, ветка `=0` `window.cpp` и выход в `vulkanWindow.cpp`).
Итог: на верном коде `hid` = `helper` = `pump` ≠ `main` — член (б)(1) не даёт ложного «пойман».

**m6 (сильная форма) с этим кодом.** Мутант m6 меняет ровно две строки (`f40b2/mut_m6.diff`): инициализация на `JoyPump` →
`ok = true`, главный поток → `SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER`. Строки `FixF24: init` и `init_owner` остаются на
`JoyPump` (`LogInitOwner` исполняется под `ok` = `true`), окна создаёт главный ⇒ `hid` = `helper` = `main` ≠ `pump` — пойман по
(б)(1). Это сильная форма п. 696(б)(1) по букве.

**Края (не RC).** `hid` = 0 на верном коде возможен только при выключенном драйвере HIDAPI (подсказка `SDL_HINT_JOYSTICK_HIDAPI`)
— по (б)(1) это «свидетель мёртв», стоп серии и пункт лида, не провал правки. `msg` — справка (окно уведомлений создаёт поток
`SDL_JoystickThread`, если задана подсказка потока джойстиков).

## §2. Поля плеча `flap` (п. 696(б)(2)) — построчно

| Поле | Окно счёта и единицы | Где | Итог |
|---|---|---|---|
| `flap_life_min_us`, `flap_life_max_us` | отсоединение − присоединение по слотам плеча; оба времени — `TestHidLossNowUs()` (мкс) под замком джойстиков: присоединение — до `SDL_JoystickAttachVirtualEx`, отсоединение — до `SDL_JoystickDetachVirtual`, запись только при успехе; в счёт — слоты с обоими временами | `7c38e497:src/graphics/presentation/window/window.cpp:1564`, `7c38e497:src/graphics/presentation/window/window.cpp:1583`, `7c38e497:src/graphics/presentation/window/window.cpp:1452` | ✓ мкс; неудачные присоединение и отсоединение выпадают; нет слотов — оба 0, тогда допуск `jp_scan_gap_max_us` < 0 не выполнен — помеха, не ложный допуск |
| `jp_scan_gap_max_us` | от `StandScanGapBegin` непосредственно перед первым присоединением до `StandScanGapEnd` непосредственно после последнего отсоединения (шаг `k` = 61); отметки — `StandScanMark` перед каждым `ScanAndOpen` в цикле `JoyPump`; края считаются; часы `steady_clock` (мкс) на обоих концах | `7c38e497:src/graphics/presentation/window/window.cpp:1668`, `7c38e497:src/graphics/presentation/window/window.cpp:1680`, `7c38e497:src/graphics/presentation/window/joyPump.cpp:249`, `7c38e497:src/graphics/presentation/window/joyPump.cpp:393`, `7c38e497:src/graphics/presentation/window/joyPump.cpp:535` | ✓ мкс; окно = п. 696(б)(2) «от первого присоединения до последнего отсоединения» |
| `=0` и прочие режимы | `Begin`/`End` при `!Enabled()` ничего не делают и дают 0; в прочих режимах поля не пишутся (атомики с 0) | `7c38e497:src/graphics/presentation/window/joyPump.cpp:513`, `7c38e497:src/graphics/presentation/window/joyPump.cpp:524` | ✓ |

**Гонки.** `StandScanMark` читает флаг без замка и перепроверяет его под `m_stand_scan_mutex`; отметка, взятая до `Begin`, отсеивается
условием `now < m_stand_scan_last_us` (`7c38e497:src/graphics/presentation/window/joyPump.cpp:399`), отметка после `End` — снятым
флагом. `flap_detach_us` пишет поток стенда, читает задача `stat` главного потока через ≥ 2 с после `done` — `relaxed` достаточно
(как у `flap_attach_us` F40a). Сравнение промежутка (`steady_clock`) с жизнью (`FrameStats::NowNs`) — сравнение длительностей в мкс
двух монотонных часов, не меток — годно.

**Отметка перед вызовом, а не в теле `ScanAndOpen`.** Проверено против m1: мутант вставляет ранний возврат первой строкой тела;
отметка в цикле до вызова меряет то же планирование `JoyPump`, что и на верном коде. Допуск у `f24_m1` структурно достижим [c кода]:
цикл ждёт 1 мс только при открытом пульте, иначе 250 мс (`7c38e497:src/graphics/presentation/window/joyPump.cpp:38`,
`7c38e497:src/graphics/presentation/window/joyPump.cpp:39`, `7c38e497:src/graphics/presentation/window/joyPump.cpp:254`); при
m1 базовый пульт стенда (присоединяется главным потоком до огня, `7c38e497:src/graphics/presentation/window/window.cpp:1605`)
открывает задача m1 по индексу события (`7c38e497:src/graphics/presentation/window/window.cpp:392` →
`7c38e497:src/graphics/presentation/window/joyPump.cpp:473` + строка m1) без задержки — задержка задач ставится только на огне.
Значит `m_open_pads` ≥ 1 и у m1 цикл идёт с ожиданием 1 мс. Без базового пульта (его присоединение не удалось) промежуток у m1
был бы ≈ 250 мс > жизни — недопуск, что по (б)(2) — помеха, а на третьем подряд — стоп и пункт лида, не ложный «не пойман».

**Запас допуска [I].** Жизнь пульта — два шага стенда по `TEST_HIDLOSS_PROBE_MS` = 20 мс (`7c38e497:src/graphics/presentation/window/window.cpp:1145`,
сон шага `7c38e497:src/graphics/presentation/window/window.cpp:1729`) плюс работа шага; период таймера процесса 1 мс ставит SDL
(`4b69833b:src/timer/windows/SDL_systimer.c:54`) ⇒ жизнь ≈ 41–44 мс < 50 мс (`7c38e497:src/graphics/presentation/window/window.cpp:1155`).
Не измерено — это и проверяет допуск F40c.

## §3. Прочий код (п. 696(б)(4)) и подпись

- `git diff --stat dfc037e9 7c38e497 -- src` (worktree) = `git show --stat 57f9e528 -- src` (`main`): `joyPump.cpp` +98,
  `joyPump.h` +4, `window.cpp` +33/−5 — 3 файла; тела ханков равны строка в строку (0 строк различия); `git diff --stat e3aa4b4d
  57f9e528 -- src/graphics/presentation/window src/libs/controller.cpp` — те же 3 файла (`f40b2/diffcheck.out.txt`). Все ханки —
  места §1 и §2 (свой построчный просмотр диффа). Н1 не исправлен — по выбору автора, строка чтения F40d по п. 696(в).
- Путей `src/graphics/shader/**` 0 ⇒ подпись трансляции не меняется: строка `9177b4267de1fb8bac7d1113afd8733210addfac` — 1 раз в
  `ddf0ca91`, своей чистой сборке, пяти мутантах и FS12 `46892c20` (`f40b2/sig_clean.out.txt`, `f40b2/bin_m*.out.txt`).
- `git cherry main 7c38e497` — `-` у `730ed40a`, `e0b4f2ba`, `dfc037e9`, `7c38e497` (член п. 378(г)(5)).
- Предупреждений компилятора в `joyPump.cpp` и `window.cpp` — 0 (своя чистая сборка и пять сборок мутантов).

## §4. Сборка из чистого worktree (п. 696(б)(5), форма п. 693(а))

Worktree `C:/kyty/f287/f40b2/wt` — `git worktree add --detach … 7c38e497`, подмодули — как у F40a2 (`f40b2/mk_wt_f40b2.sh`,
копия `mk_wt_f40a2.sh` с путём), `git status` 0 строк, CR в `src/` 0 (`f40b2/mk_wt.log`); сборка — `build_f40b2.cmd` (флаги
`build_local.cmd`, clang-cl, Release + LTO) под сторожем `watch_f40b2.py` (configure, затем один шаг — 785 шагов ninja).

| Бинарь | sha256 | Размер | Версия |
|---|---|---|---|
| F40a2, тег F40c (`C:/kyty/f287/bin/kyty_emulator_ddf0ca91.exe`) | `ddf0ca913f9feb8a66569fa30668de4b97e275ab6c4cc3e5c69889b4cb82e5d5` | 24 902 144 | `KytyPS5-2026-09-15-6a2987a-1917-g7c38e497` |
| своя чистая (`C:/kyty/f287/f40b2/bin/kyty_emulator_b2e285bb_clean.exe`) | `b2e285bb8226364f4a930e1093be731cee1cf5f6daa9690bee7468ebabc10b05` | 24 902 144 | `KytyPS5-2026-09-15-6a2987a-1917-g7c38e497` |

**sha256 разные — причина названа.** Различаются 2 008 байт: 3 — метка времени PE (смещение `0x80`), 150 — `.rdata`, 1 855 — `.data`
(`f40b2/bytes_clean.out.txt`). Путь worktree `f287\f40b2\` против `f287\f40a2\` (одной длины) входит в строки `__FILE__` и в хэш
анонимных пространств имён clang-cl. **Код по функциям** (`cmp_code_f40b2.py` — копия `cmp_code_f38b.py` с заменой пути
`f40b2` → `f40a2`, `f40b2/cmp_clean.out.txt`): размеры секций равны; `.pdata` равна; `.text` — 0 различающихся функций и 0 байт
вне функций; `.rdata` — 11 байт, из них отвергнутых 0 (3 слова отладочного каталога CodeView); **`ALL OK`**. Сдвигов `.data`
нет — пути одной длины.

## §5. Бинари мутантов (п. 696(б)(5))

`mut_f40b.py` (`b1f6b8e7:docs/track-f/f40b/mut_f40b.py`, без изменений) — `check 7c38e497` `ALL OK`, якоря не обновлялись
(`f40b2/mut_check_7c38e497.txt`). Каждый мутант (`f40b2/mut_one_f40b2.sh`): worktree на `7c38e497` (чистый) → `apply <m>` →
коммит мутанта без ветки (в `main` его нет) → configure → сборка → закреплённая копия → worktree обратно на `7c38e497`, `git status`
0. Configure после коммита обязателен: `SDL_REVISION` берётся при configure — первая сборка m1 без него (`b5df2d21…`) несла две
строки версии (`-1917-g7c38e497` и `-1918-gf0fc3c4d`) и отброшена (`f40b2/bin_m1_noreconf.out.txt`). У всех пяти ниже — одна
строка версии. Копии — `C:/kyty/f287/bin/kyty_emulator_<sha8>.exe` и `C:/kyty/f287/f40b2/bin/`. Дифф каждого — `f40b2/mut_<m>.diff`
(m1 +25 строк в `joyPump.cpp`; m2, m4, m5 — одна строка; m6 — две, в `joyPump.cpp` и `window.cpp`).

| Мутант | Коммит (только worktree) | sha256 | Версия | Тег F40c, форма вызова | Член, который обязан поймать |
|---|---|---|---|---|---|
| m1 — открытие по индексу события | `3bc53050` | `c164a6d34f0ab8b089d23752bf052da1db24f5ead9798ad0d8b8caa264d4ef0b` | `…-1918-g3bc53050` | `f24_m1`: `KYTY_FIX_F24=1`, `KYTY_TEST_HIDLOSS=60:flap` | при допуске (б)(2) (`flap_life_max_us` < 50 000 и `jp_scan_gap_max_us` < `flap_life_min_us`): `opened` < `attached` |
| m2 — флаг остановки не читается | `1ea4976f` | `fcf462d823eee56a0069866de224aeef9df2b1c6d9bc83288fee364705de0bef` | `…-1918-g1ea4976f` | `f24_m2`: `=1`, `60:exit` | строка `TestHidLoss: jp_task ran` после `FixF24: pump_stop_expired` |
| m4 — закрытие на главном потоке | `81676e69` | `ea84198deaebc903b38e07df98fc1f6af84172434c024874b6a5c787a0069446` | `…-1918-g81676e69` | `f24_m4`: `=1`, `60:detach` | `jp_tasks` = 0 |
| m5 — подсказка `SDL_HINT_AUTO_UPDATE_JOYSTICKS` не ставится | `1b29ab0d` | `bec75cc20b86609bd1440a1a7aea1afea95a23af763f19b0f3a6e4c7e2f2fe94` | `…-1918-g1b29ab0d` | `f24_m5`: `=1`, `60:upd` | по (б)(3): провален хотя бы один член `f24_u1` — `upd_on_main` = 0, `main_late_max_us` < 100 000, `in_lat_max_us` < 100 000 |
| m6 — инициализация пультов на главном (сильная форма) | `658ab84c` | `bd6dcc81a32519eae50de4eb44ce88187d9ba9d4a8221c656b402c6065068c8f` | `…-1918-g658ab84c` | `f24_m6`: `=1`, `60:upd` | по (б)(1): `init_owner` `hid` = `main` или `helper` = `main` |
| m3 — ожидание главного потока без предела | — | бинаря нет | — | — | пойман ревью кода (F40b §4, п. 692(г)(3) по букве) |

Префикс версии у всех — `KytyPS5-2026-09-15-6a2987a`. Общая форма вызова — F40a2 §6: бинарь мутанта вместо `ddf0ca91`, прочие
умолчания FS12, `-lvl underwater_aerial_garden`, стимул после первого кадра сцены. Подпись трансляции у всех = FS12 (§3) —
каталоги `_fixf19` и повтора те же, прогрева нет. Счёт строк в бинарях (`f40b2/bin_m*.out.txt`): `FixF24: init_owner hid=` 1,
`flap_life_min_us=` 1, `jp_scan_gap_max_us=` 1 у всех пяти; `FixF24: open failed index=` — 1 только у m1 (его строка).

**Коммиты мутантов** лежат в общей базе объектов без ссылки и могут быть удалены `git gc`; для повтора — `mut_f40b.py apply <m>`
на `7c38e497` (дифф каждого сохранён). Бинари закреплены копиями по sha256.

## §6. Что этот отзыв не доказывает (п. 696(ж))

- Что код F40a/F40a2 и мутанты работают в игре: ни один бинарь игрой не запускался (F40c впереди); строка `init_owner` и поля
  плеча `flap` не исполнялись.
- Что свидетель `init_owner` видит все окна, которые SDL создаёт при инициализации (он видит три класса, первое своё окно каждого).
- Что допуск `flap` выполняется на этой машине (оценка запаса — [I]); что шесть мутантов — полный набор; что стенд воспроизводит
  причину Ф24 (он воспроизводит место).
- Что Ф24 исправлен: F40c и F40d впереди. Ни одно число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется. Вердикта строки
  Ф24 нет.

## §7. Файлы

`docs/track-f/f40b2/` (копия `C:/kyty/f287/f40b2/` без worktree, сборки, бинарей и логов сборки): `api_chk.sh`, `bstep.sh`,
`watch_f40b2.py`, `build_f40b2.cmd`, `mk_wt_f40b2.sh`, `mk_wt.log`, `mut_f40b.py` (копия F40b), `mut_one_f40b2.sh`,
`mut_check_7c38e497.txt`, `mut_m1.diff`, `mut_m2.diff`, `mut_m4.diff`, `mut_m5.diff`, `mut_m6.diff`, `bin_m1.out.txt`, `bin_m2.out.txt`,
`bin_m4.out.txt`, `bin_m5.out.txt`, `bin_m6.out.txt`, `bin_m1_noreconf.out.txt`, `cmp_code_f40b2.py`, `cmp_clean.out.txt`,
`bytes_clean.out.txt`, `sig_clean.out.txt`, `diffcheck.out.txt`, `refs_f40b2.py`, `refs_check.out.txt`, `refs_text.out.txt`,
`times.txt`. Замок `C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` проверялись первой строкой каждой команды — их не было;
шаги дольше 60 с — после строки API (`C:/kyty/f287/times.txt`; серий Harness Engineer `in_progress` не было) под сторожем.
