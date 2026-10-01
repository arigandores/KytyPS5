# Трек F, звено F5a (`HPP-355`): правка Б37 — swapchain при нулевом размере окна под `KYTY_FIX_MINIMIZE` и стенд `KYTY_TEST_MINIMIZE`

Автор: Emu Engineer. Дата: 2026-10-01 (UTC, строки «F5a …» `C:/kyty/f287/times.txt`). Критерий — `ROADMAP.md` «СЕССИЯ 122» п. 273(е)
(`e7d0e45f:docs/ROADMAP.md:14307`, якорь «(е) **Итерация F5 трека F = Б37; критерий до кода (п. 228(г)–(е))**», контроль +1 — 14308
«исполнен, правка малая, доказательство без пользователя стендом; цена ≈ 4 тега. Очередь F: …»); строка Б37 — п. 273(г)(1); механизм — AUDIT144 §2 (3).
Игра не запускалась; установленная `9235a7ac` в папке эмулятора не тронута (sha256 `9235a7ac61f1affb…` после всех сборок, `accept_f5a.out.txt`).
Метки: [c] — посчитано программой; [c-код] — по коду; [I] — вывод.

**Итог.** Правка и стенд — коммит **`d2811535`** (4 файла `src/`, +140 / −0). Два бинаря, оба **не установлены, дыма нет — WIP до F5b/F5c**:

| бинарь | дерево | подпись трансляции | назначение |
|---|---|---|---|
| **`abce7916`** `C:/kyty/f287/bin/kyty_emulator_abce7916.exe` | worktree `4fc501f4` + cherry-pick `d2811535` (`bf8f90e4`) | **`699c1e4b…`** (= установленной, тёплый кэш) | кандидат F5c: отличается от `9235a7ac` только правкой F5a |
| `ea870d6e` `C:/kyty/f287/bin/kyty_emulator_ea870d6e.exe` | `main` `d2811535` | не `699c1e4b` (`KytySC3:fba4fbfd…` + токены F2a/F3b) | сборка на HEAD: несёт F2a/F3b с `KYTY_FIX_B26`/`KYTY_FIX_B1B` по умолчанию 1, S-pcw, F4a/F4a2 — для F5c не годится без решения лида |

sha256: `abce7916ebd03b317829d98d9d4f13bc8be81305a6d405a92c5ceff185f66c21` (24 272 896 байт); `ea870d6ea309b1b462c9b172d806deb0f31d307a6614dbda91e40ffb8ccd8809`
(24 572 928 байт). Промежуточный `cf9224f2` (первая редакция, до правки 2 §2) — в `C:/kyty/f287/bin/`, заменён `ea870d6e`, не использовать.

## 1. Механизм по коду (`4fc501f4` = HEAD до правки для этих файлов) [c-код]

`git diff 4fc501f4 d2811535~1 -- src/graphics/presentation/window/swapchain.cpp src/graphics/presentation/window/window.cpp` — пусто; номера ниже — `4fc501f4`.
`Presenter::Present` (`swapchain.cpp:881` цикл из двух попыток) → `AcquireNextImage` или `Present` вернули `Recreate` (`eErrorOutOfDateKHR`) →
`RecoverSwapchain` (`:353–358`) → `Swapchain::Recreate` → `Destroy` + `RefreshSurfaceCapabilities` + `Create` → `:402` «m_extent =
surface.capabilities.currentExtent;» без проверки нуля → `vkCreateSwapchainKHR` с `imageExtent` 0×0 (VUID-01689 под валидацией; без валидации —
`RequireVulkanSuccess` → `EXIT` при ошибке драйвера, при успехе — не определено). `SDL_WINDOWEVENT_MINIMIZED` только пишет строку (`window.cpp:466–468`).

## 2. Правка (п. 273(е)(1)), коммит `d2811535` [c-код]

Файл:строка — по `d2811535`.

| место | что |
|---|---|
| `swapchain.cpp:308` «static bool FixMinimizeEnabled() {» | ручка `KYTY_FIX_MINIMIZE`: `Common::EnvFlagOn` (не задана, пусто, `0/false/off/no` — 0), читается один раз; строка `FixMinimize: on` только при 1; вызывается в конструкторе `Presenter::Impl` (`:370`), чтобы строка шла при старте |
| `:341` «[[nodiscard]] bool Missing() const noexcept { return m_handle == nullptr; }», `:343` `SurfaceExtentZero()`, `:642` тело | нет swapchain; `currentExtent` 0 по любой оси (под `m_window.mutex`, как чтение в `Create`) |
| `:636` «if (FixMinimizeEnabled() && SurfaceExtentZero()) {» в `Swapchain::Recreate` | при `=1` и нулевом `currentExtent` после `Destroy` и `RefreshSurfaceCapabilities` — возврат без `Create` (swapchain не создаётся) |
| `:377` «if (FixMinimizeEnabled() && swapchain.Missing()) [[unlikely]] {» в `RecoverSwapchain` | начало эпизода `BeginZeroExtent()` (`:387`), `frames.SetFormat` пропускается (у пула остаётся прежний формат; `SetFormat(eUndefined)` — `EXIT`) |
| `:948` «if (FixMinimizeEnabled() && swapchain.Missing()) [[unlikely]] {» в начале каждой попытки цикла `Present` | `TryEndZeroExtent()` (`:398`): `RefreshSurfaceCapabilities`; extent ещё 0 → кадр сбрасывается (`zero_extent_dropped++`, `frames.Release(&frame, reuse)` — как в прежнем выходе «retry exhausted» `:1019`), возврат без ожидания; extent ≠ 0 → `Create`, `SetFormat`, строка конца, обычный путь |
| `:394` `SwapchainZeroExtent: begin`, `:406` `SwapchainZeroExtent: end frames_dropped=<n> ms=<t>` | одна пара на эпизод; `ms` — от строки begin до пересоздания, целые мс (`FrameStats::NowNs`) |

Сценарий `=1` [c-код]: попытка 0 — `OUT_OF_DATE` → `Recreate` → extent 0 → нет swapchain → begin → `continue`; попытка 1 — `Missing` → extent 0 →
кадр сброшен (входит в `frames_dropped`), возврат. Каждый следующий present — одна проверка `vkGetPhysicalDeviceSurface*` (3 запроса) и сброс.
После восстановления окна первый present с ненулевым extent создаёт swapchain и идёт обычным путём. Поток present не ждёт: темп задаёт поток
вблэнка `videoOut.cpp:829–856` (период по частоте), игра не блокируется [c-код; поведение драйвера — [U] до F5c].

**`=0` — прежний путь по построению [c-код]:** дифф `d2811535` по `src/` — только добавления (+140 / −0). Все новые ветви стоят за
`FixMinimizeEnabled()` = `false`; при `=0` исполняется только: один `getenv` в конструкторе `Presenter::Impl`, проверка статического `bool` в
`RecoverSwapchain`, `Recreate` и в начале каждой попытки цикла `Present`. Новых строк лога при `=0` нет. (Без ручки `Missing()` при `=0` и так
`false`: `Create` — единственный путь к `m_handle`, `EXIT_IF(m_handle == nullptr)` `:531`; правка 2 добавила ручку в обе проверки, чтобы это
было видно локально.)

**Состояние и его жизненный цикл** (правило отчёта о флагах, п. 165(в)) [c-код]:

| состояние | установка | снятие | выходы без снятия и довод |
|---|---|---|---|
| `Swapchain::m_handle == nullptr` (нет swapchain) | `Destroy()` в `Recreate` (`:612`), остаётся при возврате `:637` | `Create()` в `TryEndZeroExtent` (`:403`) | (1) `Present` возвращается со сбросом кадра (`:951–952`) — намеренно: эпизод живёт между вызовами до ненулевого extent; (2) завершение процесса в эпизоде — `~Swapchain` → `Destroy` выходит сразу (`:578–581`, все поля пусты); строки `end` нет |
| `Impl::zero_extent_active` | `true` в `BeginZeroExtent` (`:391`) | `false` в `TryEndZeroExtent` (`:408`) | те же (1)–(2); поле читает и пишет только поток present (`Present` однопоточен по замыслу, детектор `PresentOverlap` `:918–939`) |
| `Impl::zero_extent_dropped` | `0` в `:392`, `++` в `:950` | `0` в `:409` | то же |
| `Impl::zero_extent_t0_ns` | `:393` | не снимается (перезаписывается следующим begin) | читается только в `:405` внутри эпизода |
| `FixMinimizeEnabled()::enabled` | первый вызов (`:309`) | нет (`static const`) | — |
| стенд: `cfg` (`window.cpp:1050`), `armed` (`:1066`) | `cfg` — первый вызов; `armed` — первая строка `Level has started: ` | нет: один эпизод стенда на процесс | — |

TLS нет. Замков новых нет; `SurfaceExtentZero` берёт `m_window.mutex` на чтение трёх полей, вызывающие его места этот замок не держат
(`Recreate` и `TryEndZeroExtent` — вне `Create`).

## 3. Стенд (п. 273(е)(2)) [c-код]

`window.cpp:1044` «void WindowTestMinimizeNoteGuestText(const char* text, size_t size) {» (объявление `window.h:17`), вызов — `libC.cpp:654`
сразу после `RenderDocNoteGuestText` в `fwrite` гостя (откуда строка `GuestOut: …`). `KYTY_TEST_MINIMIZE=<с>:<длит.>` (дробные секунды,
`strtod`; не задана или пуста — ничего, строк нет; неверный формат — строка `TestMinimize: config invalid …` и ничего). Первая строка гостя с
`Level has started: ` → строка `TestMinimize: armed delay_s=… dur_s=…` → отсоединённый поток спит `<с>`, ставит в очередь главного потока
`SDL_MinimizeWindow` (строка `TestMinimize: minimize` пишется главным потоком перед вызовом), спит `<длит.>`, ставит `SDL_RestoreWindow`
(`TestMinimize: restore`). `PostToMainThread` будит цикл `SDL_WaitEvent` событием `SDL_USEREVENT`. Отсчёт `<с>` — от записи гостем строки
входа (та же строка лога `GuestOut: Level has started:`), не от первого кадра сцены.

**Подпись кэша трансляции не тронута [c]:** набор подписи — `src/graphics/shader/**` + `shaderTranslationCache.cpp`, `gpu_format.h`,
`gpu_defs.h` (`CMakeLists.txt:155–156`, `src/generate_version.cmake:45–56`); изменённые файлы в набор не входят; бинарь `abce7916` несёт
`699c1e4b…` (§5).

## 4. Тесты [c]

`shader_cfg_tests` (`KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1`; цель включает `swapchain.cpp`, тесты пересобраны после правки 2):

| дерево | `KYTY_FIX_MINIMIZE=0` | `=1` | падения |
|---|---|---|---|
| `main` `d2811535` | 127 тестов, sha256 лога `5a60758a…` | `5a60758a…` | 1 — `TestNewShaderRecompilerPixelImageSampleLodSelection` (Б11), как у F2a/F3b (тот же sha `5a60758a…`, `docs/track-f/f3b/cfg_tests_b1b1.txt`) |
| worktree `bf8f90e4` | 127, `a074f1b3…` | 127, `5a60758a…` | 1 (Б11) при обоих; разность `=0`/`=1` — одна строка времени `ASTRO BOT PS 5457 structurize: … elapsed_ms=19` / `=18` |

Падений при `=1` не больше, чем при `=0`; список равен прежнему (127/1, Б11). Тестов на путь swapchain нет — он без окна и устройства не
исполняется; проверка пути — F5c (теги (а)–(г) п. 273(е)(3)).

`check_gate_order.py` (`C:/kyty/s113`, до первой сборки): **`GATE ORDER: clean`** (гейты и ручки `Gates` не менялись; строка `UNMATCHED
… RebindSlowCensus` — та же, что у F3b) — `f5a/gate_order.out.txt`.

## 5. Сборки

- **`main`** — `build_local.cmd` 12:51:15–12:51:35Z (первая редакция, `cf9224f2`) и 12:52:40–12:53:05Z после правки 2 (`ea870d6e`); предупреждений в изменённых файлах 0.
- **worktree** `C:/kyty/f287/f5a/wt` (`mk_wt_f5a.sh` — копия `mk_wt_f4a2.sh` F4a2 с одним cherry-pick; вывод `mk_wt.log`): `git worktree add --detach`
  `4fc501f4`, cherry-pick `d2811535` → `bf8f90e4` без конфликтов; подмодули — `git archive` гитлинков `4fc501f4`, `ffmpeg-core` — `clone --shared`;
  `sig_f4a2.py --write` — 27 файлов набора подписи в CRLF, «FOUND 699c1e4b… combo LLLLLLLLL» (9 файлов набора изменены после `4fc501f4` — в LF).
  `git diff --ignore-cr-at-eol 4fc501f4 -- src` дерева — ровно 4 файла F5a, +140. `build_f5a.cmd` (копия `build_f4a2.cmd`, пути `f5a`):
  `configure`, `version` → `kytyGitVersion.h`: `KYTY_SHADER_SOURCE_HASH "699c1e4b7db359067b461e029b913c4b6e78dc90"`, версия
  `KytyPS5-2026-09-15-6a2987a-1373-gbf8f90e4-dirty` (`-dirty` — CRLF-файлы); полная сборка; предупреждений в изменённых файлах 0.
- **Приёмка строк** (`accept_f5a.py` → `accept_f5a.out.txt`, «ACCEPT ALL OK»):

| строка | `abce7916` | `ea870d6e` | `9235a7ac` |
|---|---|---|---|
| `699c1e4b7db359067b461e029b913c4b6e78dc90` | **1** | 0 | 1 |
| `KYTY_FIX_MINIMIZE`, `FixMinimize: on`, `SwapchainZeroExtent: begin`, `…: end frames_dropped=` | **1** | 1 | 0 |
| `KYTY_TEST_MINIMIZE`, `TestMinimize: minimize`, `TestMinimize: restore` | **1** | 1 | 0 |
| `KYTY_FIX_B1B`, `KYTY_FIX_B26`, `KYTY_FIX_DUALSRC` | **0** | 1 | 0 |
| `KYTY_S_PCW` | **0** | 4 | 0 |

## 6. Риски и вопросы к ревью и лиду [I]

1. **Драйвер может не вернуть `OUT_OF_DATE` на свёрнутом окне**, а заблокировать `vkAcquireNextImageKHR` (таймаут `UINT64_MAX`) — тогда эпизод
   не начнётся. На этой машине `w144_09` показал `vkQueuePresentKHR … eErrorOutOfDateKHR` [c, п. 273(г)(1)], путь правки — тот же. Проверка — F5c (а).
2. **Скриншот/запись в эпизоде:** `screenshot.Poll()` стоит до цикла; у сброшенного кадра `Record`/`Finish` не зовутся — в видео `KYTY_REC`
   разрыв на время эпизода, снимок `KYTY_SHOT_TIMES`, попавший в эпизод, теряется (как в прежнем выходе «retry exhausted»). Окно критерия (в)
   «сворачивание + 2 с» это покрывает только при длине эпизода ≤ окна стенда + 2 с — лиду: окно (в) мерить от `TestMinimize: minimize` до
   `SwapchainZeroExtent: end` + 2 с?
3. **Начальное создание** swapchain при уже свёрнутом окне (`Presenter::Impl` → `Create`) правкой не покрыто — критерий говорит о пересоздании.
4. **Стенд:** поток таймера отсоединён и читает `g_window.get()` без синхронизации с `WindowShutdown` — гонка возможна только при чистом
   завершении процесса внутри окна стенда; прогоны кончаются `timeout`. Ручка только для измерения.
5. **Цена эпизода:** 3 запроса `vkGetPhysicalDeviceSurface*` на present вблэнка во время эпизода — не мерилась; скорость — не цель.
6. **Бинарь для F5c:** `abce7916` изолирует правку (подпись и кэш как у установленной); `ea870d6e` меняет и трансляцию (холодный кэш, Б1б/Б26
   по умолчанию) — выбор за лидом и Harness Engineer; предложение звена — `abce7916`.

## 7. Процесс: дефект звена

Сборка тестов worktree (`build_f5a.cmd tests`, старт 13:00:32Z без замка) закончилась в 13:01:09,82Z (mtime `build_wt_tests.log`), замок серии
F4c (`go_f4c.sh`) взят в 13:01:06,56Z (mtime `SEALED_RUN.lock`) — **перекрытие 3,3 с** (как 4 с у F3b). Серия F4c остановилась на `f4c_a`:
`REFUSED (BUSY: gpu_util_median 11.0, admission <= 10)` в 13:01:43Z (`C:/kyty/f287/f4c/f4c_a.stdout.txt`) — отказ по ГП; процессов с устройством
Vulkan звено не запускало (`shader_cfg_tests` без устройства; эмулятор не запускался), связь отказа со сборкой — [U]. Под замком звено файлов не
писало и процессов не запускало (ожидание — опрос существования файла замка). Вывод: проверка замка в начале команды не защищает от замка,
взятого во время длинной команды; сборки звена шли пачками по 30–120 с в паузе между тегами. **Предложение «Процесс» (решает лид):** перед
сборкой звено треков смотрит `times.txt`/`lock.log` идущей серии и стартует сборку только если до следующего тега по её ритму ≥ 3 мин, либо
серия даёт явное окно.

## 8. Не доказано

Что правка снимает остановку под валидацией (тег (а)); что без правки свёрнутое окно ведёт или не ведёт к крэшу (тег (г)); что игра идёт
без блокировки во время эпизода и картинка после восстановления верна (теги (а), (в)); что стенд воспроизводит сворачивание пользователем;
поведение на других драйверах; корректность любой сцены. Числа — не выигрыш.

## Файлы (`docs/track-f/f5a/`)

`f5a_src.diff` (`git show d2811535 -- src`), `patch_f5a.py`, `patch_f5a_2.py`, `gate_order.out.txt`, `cfg_tests_min0.txt`, `cfg_tests_min1.txt`,
`cfg_tests_wt_min0.txt`, `cfg_tests_wt_min1.txt`, `mk_wt_f5a.sh`, `build_f5a.cmd`, `mk_wt.log`, `accept_f5a.py`, `accept_f5a.out.txt`.
Рабочие копии и логи сборок — `C:/kyty/f287/f5a/`.
