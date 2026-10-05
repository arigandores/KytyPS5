# FS7c (`HPP-567`, Harness Engineer): теги `fs7_h`, `fs7_n` на бинаре отгрузки FS7 `8df61c00` — печать до первого тега

Трек F, седьмой бинарь отгрузки FS7 (Ф8 — умолчание `KYTY_FIX_F8=1`, п. 467(г); Б24 — умолчание `KYTY_FIX_B24=1`, п. 487(г)). Разделы 0–8 —
печать (до первого тега; после неё цепочка, ридер и правила чтения не меняются; копия — `C:/kyty/f287/fs7c/pred/fs7c_seal.md`, её sha256 пишется
в json каждого тега); раздел 9 — отчёт тегов (строки ридера и слово чтения; вердикта нет — приёмка и установка FS7d `HPP-568`). Метки: [c] —
код/лог прочитан, [I] — вывод, [U] — неизвестно.

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1)

- Задание — п. 467(г)(3): `62c57c57:docs/ROADMAP.md:22591` (якорь «(3) **FS7c (Harness Engineer, под замком»; +1 — «- `fs7_n` — форма `f8_n1`»);
  члены `fs7_n` — `:22592` (якорь «- `fs7_n` — форма `f8_n1`»; +1 — «Прогона с валидацией нет»); W нет — `:22593` (якорь «Прогона с валидацией
  нет»; +1 — «(4) **FS7d (лид):**»). Пункт целиком — `:22584` (якорь «467. **Звено F18f»; +1 — «(а) **Приёмка строкой по членам п. 441(д).**»).
- Поправка п. 487(г)(3) (Б24 в FS7, тег `fs7_h`, члены `FixB24` и `TestHidLoss:` у `fs7_n`): `62c57c57:docs/ROADMAP.md:22721` (якорь «(3) **FS7c:**
  сверх п. 467(г)(3)»; +1 — «(4) **FS7d:** сверх п. 467(г)(4)»); пункт — `:22713` (якорь «487. **Звено F19f»; +1 — «(а) **Приёмка строкой по членам
  п. 451(д).**»).
- Приёмка FS7b и чтения Н1, Н3, Н4 — п. 518: `62c57c57:docs/ROADMAP.md:22948` (якорь «518. **Звено FS7b»; +1 — «(а) **Приёмка строкой: FS7b ✓**»);
  Н1 — `:22952` (якорь «(1) **Н1**»; +1 — «(2) **Н2**»); Н3 — `:22954` (якорь «(3) **Н3**»; +1 — «(4) **Н4 — член печати FS7c»); Н4 — `:22955` (якорь
  «(4) **Н4 — член печати FS7c»; +1 — «(г) **Звенья:** FS7b `HPP-566`»). Комментарии лида в `HPP-567`: `76dccb24` (п. 487), `995cf0fb` (п. 518).
- Формы тегов-образцов: `f8_n1` — п. 441(д)(4) с п. 448(в) и N1, N2, N5 п. 453(в) (`62c57c57:docs/ROADMAP.md:22489`, якорь «453. **Звено F18d»; +1 —
  «(а) **Приёмка строкой: F18d ✓**»), печать F18e `docs/track-f/f18e.md` §4; `b24_h1` — п. 451(д)(4) с N1, N3, N5 п. 460(д)
  (`62c57c57:docs/ROADMAP.md:22539`, якорь «460. **Звено F19d»; +1 — «(а) **Приёмка строкой. F19d ✓.**»), печать F19e `docs/track-f/f19e.md` §4.
- Строки кода FS7 (`d6ee2dc8` — дерево бинаря FS7): `src/libs/audio.cpp` — `FixF8: mode=1` `:298`, `AudioStat` `:376`, `AudioOut: SDL audio init
  failed` `:536`, `AudioOut: opened SDL device` `:561`, `AudioOut: SDL_QueueAudio failed: %s` `:742`, `AudioOut: vibration port` `:808`,
  `AudioIn: SDL init failed` `:941`; `src/libs/controller.cpp` — `Haptics: disabled by KYTY_HAPTICS=0` `:470`, `Haptics: pad audio device … opened`
  `:506`, `FixB24: mode=1` `:843`; `src/kernel/fileSystem.cpp` — `FixB4: mode=%d` `:406`; `src/graphics/presentation/window/window.cpp` — строка
  пульта `:394`, `TestHidLoss: config on` `:1129`, `fire mode=` `:1180`, `stat mode=` `:1216`.
- Карта ссылок — `refs_fs7c.py` (27 из 27 по якорю и +1, `ALL OK`; вывод `refs_fs7c.out.txt`).

## 1. Бинарь и окружение

- Бинарь обоих тегов — копия FS7 `C:/kyty/f287/bin/kyty_emulator_8df61c00.exe` (worktree `d6ee2dc8` = FS6a `3904522d` + cherry-pick `10a4800b`,
  `9c726d74`, `919c1a19` + FS7a `ec6c4c83`; п. 514, 518), sha256 `8df61c009fbe6d7fd7f4e7576e89ab1b0989129336a26f6d1cdf8fd778fbffe7`. Опознание
  (Н3, п. 518(в)(3)): поле `binary_sha256` json тега и `installed_sha.txt` = `8df61c00…`; строка версии `KytyPS5-2026-09-15-6a2987a-1883-gd6ee2dc8`
  в файле бинаря; текст ревизии `d6ee2dc` в логе (`version: Fork build arigandores/KytyPS5 d6ee2dc` [c строки в exe]) — все три строки допуска.
- Установленный — FS6 `9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2` (FS6d, п. 478, 510; описание звена называет S12
  `adb0c82f` — оно написано до установки FS6): сверка до тега (отказ, если иной), внутри замка (`installed_before.txt`), после возврата из
  закреплённой копии `C:/kyty/f287/bin/kyty_emulator_9325446c.exe` (`installed_after.txt`). FS7 ставится только на время тега.
- Окружение: цепочка снимает все `KYTY_*` и `VK_LAYER_*`; `enter_scene.py` передаёт позиционно только пары формы (§3) и
  `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0` (+ свои: `KYTY_FRAME_TRACE=lite`, `KYTY_GPU_HANG_ABORT_S=8`, `KYTY_GATE_FILE`, `KYTY_SAMPLE_GATE`,
  `KYTY_QUEUE_TRACE=1`, `KYTY_GUEST_ARGS=-lvl underwater_aerial_garden`, `KYTY_REC`). Ни одной `KYTY_FIX_*` (умолчания бинаря: `KYTY_FIX_F8`,
  `KYTY_FIX_B24`, `KYTY_FIX_B4` и прочие — 1 по таблице FS7a/FS7b), нет `KYTY_TEST_AUDIOLOSS`, `KYTY_HAPTICS`, `KYTY_GAME_PATCH`,
  `KYTY_GPU_CHECKPOINTS`.
- Подпись трансляции FS7 `26ce5fc7` = установленному (п. 518(а)) ⇒ каталог `variant_fixb26_fixb1b_fixf10` тёплый (`warm.txt`, справка).
- Стенды на FS7 этим звеном не гоняются (Н1, п. 518(в)(1)); `KYTY_TEST_HIDLOSS` у `fs7_h` — стенд в игре формы `b24_h1`, его значение задано явно.

## 2. Кэши, сохранения и манифест

Как F19e / FS6c: манифест sha256 `_ShaderCache` (с `PPSA21564/pipelines.bin`), `_PipelineCache`, `_SaveData`, GLCache драйвера — до тега, копия всех
четырёх, манифест состояния после тега до возврата, возврат, манифест после; `cmp` до/после — `manifest_cmp.txt` (строка формы: `manifest cmp
EQUAL`). Неравенство, неудачный возврат или установленный ≠ `9325446c` после возврата — `RETURN_FAILED`, замок остаётся, вопрос лиду; следующий
тег не идёт.

## 3. Форма тегов (один тег — один замок, одна попытка; порядок п. 487(г)(3): `fs7_h`, затем `fs7_n`)

`launch_fs7c.sh <тег>` только запускает отсоединённую `go_fs7c.sh <тег>`; ожидание — `wait_fs7c.sh <тег>` ≤ 540 с за команду, отдельными
командами; чтение — `post_fs7c.sh <тег>` вне замка (глитчи `s51_vidglitch.py <rec> 4 6`, лист `sheet142.py`, затем ридер). Шлюз `procload.py`
(вывод через маску `<app>`) перед замком; замок `C:/kyty/SEALED_RUN.lock` — только когда его нет (`noclobber`); `runs/lock.log` (UTC); строки
событий — `C:/kyty/f287/times.txt`. `fs7_n` начинается, только если каталог прогона `fs7_h` есть. Очередь замка P > F > S (п. 322(г)): перед
каждым вызовом — проверка API строкой `times.txt`.

| тег | вызов (`enter_scene.py <тег> --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file gates_default.txt --pred pred/fs7c_seal.md --rec --hold H …`) |
|---|---|
| `fs7_h` | H = 330; `KYTY_TEST_HIDLOSS=60:hold KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` (форма `b24_h1` при умолчаниях) |
| `fs7_n` | H = 840; `KYTY_AV_TRACE=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` (форма `f8_n1` при умолчаниях; `KYTY_AV_TRACE=1` — чтение N3 п. 467(в)) |

Удержание — после «сцена стабильна» (90 строк `FrameTrace` с `draws ≥ 300`), поэтому процесс живёт дольше H; у `fs7_h` стенд взводится строкой
входа, `stat` ≈ 65 с после неё — внутри удержания (N5). Выход харнессом: `WM_CLOSE` в конце удержания, ожидание `CLOSE_WAIT_S` = 40 с, затем
`kill`; время и код выхода — строка `EXIT` ридера (не гейт; у `fs7_h` и `fs7_n` выход идёт путём `PadOutput::Stop` кода F19c2 — долг (1) п. 487).
Повтора тега нет (`runs/<тег>` есть — отказ). Отказ шлюза до старта эмулятора (выход 3/5) попытку не тратит — вывод переносится в `old/`. Тег
`NOT_ADMITTED` (помеха) — попытку не тратит, повтор только пунктом лида. Прогона с валидацией нет (п. 467(г)(3): W базы — `fs6_w`).

## 4. Ридер (`fs7c_read.py`): строки `ADMIT`/`FORM`/`MEMBER`/`HARM`/`IDENT` и слово `READING`

**Определения.** Первая `GuestOut` — первая строка лога, содержащая `GuestOut:` [c: в логах F19e/FS6c это `GuestOut: MODL:`, строка 12 296].
Кадр — `dt_us` строки `FrameTrace: n=… dt_us=…`. У `fs7_h` — строки стенда и окно стенда F19e §4 (широкое: кадры между строками `fire` и `stat`
плюс кадры до `fire` назад, пока сумма их последующих `dt_us` до строки `fire` ≤ 1 000 000; узкое печатается рядом; члены читают широкое). У `fs7_n`
— определения F18e §4 (порт вибрации, A, `T_vib`, строка Ф8 `AudioOut: SDL_QueueAudio failed: Invalid audio device ID`, строки `AudioStat`, F).

**Члены «Fix»** (п. 467(г)(3), 487(г)(3), 518(в)(4)): строка вида `Fix<X>: mode=<n>` ищется в любом месте строки; «иная форма» — строка с
`Fix<X>:`, у которой нет `mode=1` (`mode=0`, иной текст); `FixB42:`/`FixB42Ext:` строками `FixB4:` не считаются.
- `FixF8` (Н4): ровно 1 строка `FixF8: mode=1` и 0 строк `FixF8:` иной формы — ✓; номер её строки и номер первой `GuestOut` печатаются строкой
  `N4 row` (и в таблице отчёта §9), порядок — не гейт; строки нет — провал члена (разбор лидом).
- `FixB24`, `FixB4`: ровно 1 строка `mode=1`, 0 строк иной формы и номер строки < номера первой `GuestOut`; строки `GuestOut` нет — не определено.

**Допуск** (провал любой строки — `NOT_ADMITTED`, помеха прогона, повтор пунктом лида): бинарь по Н3 (§1, три строки); `prereg.sha256` json = sha256
файла печати; окружение по §1 (ни одной `KYTY_FIX_*`, в том числе пустой; нет `KYTY_HAPTICS`, `KYTY_GAME_PATCH`, `KYTY_GPU_CHECKPOINTS`,
`KYTY_TEST_AUDIOLOSS`); нет помехи (`Window … minimized`, `Recovering Vulkan swapchain`, `GamePatch:`).
- `fs7_h` (п. 451(д)(4), N5 п. 460(д)): `KYTY_TEST_HIDLOSS=60:hold`; строк иного пульта (`Controller <id>: "<имя>" type=` с именем ≠ `KYTY test pad`)
  — 0; ровно по одной строке `config on delay_s=60 mode=hold hold_ms=3000` (0 `config invalid`), `armed`, `attach`, строки тестового пульта,
  `fire mode=hold`, `done`, `stat mode=hold` со всеми полями; `pad_calls` ≥ 1; `probes_posted − probes_run` = 0; N5 — строка `stat` после строки
  `attach`, `Event: quit` (если есть) после `stat`. `KYTY_AV_TRACE` у `fs7_h` не проверяется (как F19e).
- `fs7_n` (п. 441(д)(4), N5 п. 453(в)): `KYTY_AV_TRACE=1`, нет `KYTY_TEST_HIDLOSS`; строка `AudioOut: vibration port` есть; строк `Haptics: pad audio
  device … opened` — 0; строк `Haptics: disabled by KYTY_HAPTICS=0` — 0; A ≥ 1 и `T_vib` прочитана (F18e §8.3); строк `TestAudioLoss:` — 0. Строки
  пульта у `fs7_n` — справка.

**Форма** (провал — `FORM_FAIL`, вопрос лиду): установленный FS6 `9325446c` до тега и после возврата; манифест до = после возврата.

**Члены:**
- `fs7_h` (п. 487(г)(3)): `main_late_max_us` ≥ 2 700 000; `po_wait_max_us` ≥ 2 700 000; `pad_wait_max_us` < 50 000; `guest_sdl` = 0; кадров ≥ 1 с
  в окне стенда (широком) — 0; `FixB24`; `FixF8` (Н4); `FixB4`. N1 п. 460(д) — тавтологии остаются членами; N3 — поле `sent=` не читается.
- `fs7_n` (п. 467(г)(3) + п. 487(г)(3)): строк Ф8 во всём логе — 0; `init_calls ≤ 1` во всех строках `AudioStat` (провал — правило N1 п. 453(в): F ≥ 1
  и это единственный провал среди членов ⇒ `HOST_NOISE`, повтор пунктом лида; F = 0 ⇒ провал по букве); `acq` ≥ 250 в последней строке
  `AudioStat`; `status ∈ {1, 2}` во всех строках с `dev ≠ 0`; `FixF8` (Н4); `FixB4`; `FixB24`; строк `TestHidLoss:` — 0.

**«Нет вреда»** (члены у обоих тегов): вход (`GuestOut: Level has started: underwater_aerial_garden`); процесс дожил до конца удержания (исход `ok`,
`hold_exit` пуст, `hold_s` ≥ H); 0 маркеров смерти (`Unhandled exception:`, `--- Fatal Error ---`, `--- Error ---`, `GpuHangAbort:`, `ErrorDeviceLost`
в логе и stdout); 0 кадров ≥ 1 с после первого кадра сцены (первая строка `FrameTrace` с `draws ≥ 100` после строки входа; до смены сцены; у `fs7_h`
— вне широкого окна стенда); видео ≥ 3 000 записей индекса; 0 одно-кадровых глитчей (`s51_vidglitch.py <rec> 4 6`); лист для лида сделан.

**Тождества.** `fs7_h` — F19a §6.1 при `=1` (строки `IDENT`: `pad_calls = pad_vib + pad_led + pad_trig`, `probes_run ≤ probes_posted`, `removed` = 0
в `hold`, `t_us` `armed` < `attach` < `fire` ≤ `done`, инвариант `guest_sdl` = 0); нарушение — `IDENT_FAIL` (вариант F19e §8.4). `fs7_n` — п. 441(г)
при `=1` (строки `IDENT-REF`: `q_fail ≤ pushes`, неубывание `pushes`, `q_fail`, `init_calls`, `acq` по порту) — справка, не слово (N2 п. 453(в)).

**Выход** (строка `EXIT`, не гейт): `close_posted`, `close_rc`, `close_s`, `close_killed`, `close_wait_s` записи прогона и номер строки
`Event: quit`.

**Слово `READING`** (порядок): `NOT_ADMITTED` → `FORM_FAIL` → `HOST_NOISE` / `MEMBERS_FAIL` (член NO) → `IDENT_FAIL` (только `fs7_h`) →
`HARM_FAIL` → `NOT_EVALUABLE` (член, тождество `fs7_h` или «нет вреда» не определены) → `MEMBERS_PASS`. Слово — чтение печати; приёмку читает лид
(FS7d); листы `fs7_h` и `fs7_n` — лиду. Справка в строках ридера: строки `Fix…` с номерами, стенд и `stat` целиком, кадры ≥ 1 с в обоих окнах,
порт вибрации, Ф8, F, строки `AudioStat`, `[Vulkan][E]`, `skipped draw`, события окна.

## 5. Отказы и остановка

`RETURN_FAILED`, установленный ≠ `9325446c` после возврата, `cmp` ≠ EQUAL — замок остаётся, вопрос лиду. `NOT_ADMITTED` или `FORM_FAIL` у
`fs7_h` — `fs7_n` не идёт, вопрос лиду (помеха — повтор пунктом лида). `MEMBERS_FAIL` / `IDENT_FAIL` / `HARM_FAIL` у `fs7_h` —
`fs7_n` идёт (одна попытка каждого тега; провал — в отчёт без вердикта), вопрос лиду в отчёте. Файл `C:/kyty/f287/STOP` — стоп перед следующей
командой. Перед каждым вызовом тега — проверка API (звенья прогонов, комментарии звена) строкой `times.txt`.

## 6. Не заявляется

Что FS7 установлен (до FS7d); что Ф8 или Б24 сняты на установленном бинаре; что настоящая потеря устройства звука или пульта хоста даёт форму стендов
или что правка её лечит; что звук верен или слышим; что поток звука без темпа меняет часы игры; что Б24 воспроизводим без оборудования; что
аварийный выход в игре проходит без ожидания (Н2); что Ф6 — дефект или не дефект; что Ф19 `FIXED`; что реестр полон; ни одно число — не выигрыш;
60 FPS не обещаются.

## 7. Инструменты и фикстуры

Файлы — `docs/track-f/fs7c/` (локально `C:/kyty/f287/fs7c/`): `go_fs7c.sh` (порт FS6c `go_fs6c.sh` с формами F19e/F18e), `launch_fs7c.sh`,
`wait_fs7c.sh`, `post_fs7c.sh` (порт F19e), `fs7c_read.py` (порт `f19e_read.py` + `f18e_read.py`), `test_fs7c_read.py` (+ `.out.txt`),
`sens_fs7c.py` (+ `.out.txt`), `refs_fs7c.py` (+ `.out.txt`), `regress_fs7c.py` (+ `.out.txt`), `enter_scene.py` (= FS6c с маской `<app>`,
корень `f287/fs7c`), `test_enter_scene_mask.py` (+ `.out.txt`, = FS6c, корень `fs7c`), `procload.py`, `idle142.py`, `launch_run.py`,
`run_safety99.py`, `manifest_fs4c.py`, `sheet142.py`, `gates_default.txt` (= FS6c), `watch_fs7c.py` (сторож п. 431(в)(1), копия F19e). Копия
`launch_run.py` в git — с маской `<app>`.

Фикстуры (`test_fs7c_read.py`, 296 проверок, `ALL OK`): литералы печати (H 330 / 840, FS6 `9325446c`, FS7 `8df61c00`), `hold_s` 329,9 / 330,0 и 839,9 / 840,0,
установленный FS6 литералом — PASS, S12 `adb0c82f` до и после — `FORM_FAIL`; положительный тег каждого из двух (строки `N4 row`, `EXIT`, 8 членов); допуск — бинарь json и
`installed_sha` (иной, нет), нет json, печать (иной sha, нет файла, правка после прогона), Н3 (нет файла бинаря, строка версии FS6, ревизия
`3904522`, нет строки ревизии), окружение у каждого тега (`KYTY_FIX_F8` 1 / 0, `KYTY_FIX_B24` 1 / пустая, `KYTY_FIX_B4`, `KYTY_FIX_F19`,
`KYTY_HAPTICS`, `KYTY_GAME_PATCH`, `KYTY_GPU_CHECKPOINTS`, `KYTY_TEST_AUDIOLOSS` и пустая), у `fs7_h` стенд нет / `30:hold` / `60:sleep`,
`KYTY_AV_TRACE` допускается, у `fs7_n` `KYTY_AV_TRACE` нет / 0, `KYTY_TEST_HIDLOSS` есть / пустая; строки стенда `fs7_h` (нет и две `config on`,
`delay_s=30`, `sleep`, `hold_ms=2000`, `config invalid`, нет и две `armed`, нет `attach`, `attach failed`, нет и два тестовых пульта, иной пульт, нет
`fire`, `fire` `sleep`, нет и две `done`, нет и две `stat`, `stat` `sleep`, без поля, в склеенной строке, верная плюс битая, `pad_calls` 0 / 1,
`probes` − 1; N5 — нет `quit`, `quit` до `stat`, `stat` до `attach`); допуск `fs7_n` (нет порта вибрации, `Haptics … opened`, `Haptics: disabled`,
A = 0 / 1, нет метки, строка `TestAudioLoss:`, строка пульта — справка); помехи у каждого тега (`minimized`, `Recovering`, `GamePatch:` — отказ;
`lost keyboard focus`, `restored`, `skipped draw`, `[Vulkan][E]` — без последствий); форма у каждого тега (до иной / = FS7, после иной / нет, манифест
`DIFFER` / нет; допуск раньше формы); члены «Fix» у каждого тега — `FixF8` после первой `GuestOut` (✓, `N4 row`), нет, две, `mode=0`, `mode=1` +
`mode=0`, иная форма, в склеенной строке; `FixB24` и `FixB4` — нет, после первой `GuestOut`, `mode=0`, две, `mode=1` + `mode=0`; строки `FixB42` не
`FixB4`; без `MODL` первая `GuestOut` — строка входа; без строк `GuestOut` — `FixB24`/`FixB4` не определены, `HARM_FAIL`; члены `fs7_h` — пороги
2 700 000 / 2 699 999, 50 000 / 49 999, `guest_sdl` 1, кадр 1 000 000 / 999 999 в окне, края окна (за 1,0 с до `fire` — в широком, за 1,1 с — вне,
вред), кадр после `stat` — вред; тождества `fs7_h` (сумма `pad_calls`, `probes_run > probes_posted`, `removed` 1, три нарушения порядка `t_us`,
`fire = done` допускается, член раньше тождества, тождество раньше вреда, без `stat` — не определены); члены `fs7_n` — строка Ф8, иной текст
`SDL_QueueAudio failed`, `init_calls` 2 при F = 0 / F = 1 (`AudioOut`, `AudioIn`) / F = 1 и иной провал / F = 1 при `init_calls` 1, `init_calls` 0,
`acq` 250 / 249 / последняя строка, `status` 2 / 0 / 3 / 0 при `dev = 0` / 0 в одной строке, нет строк `AudioStat`, строка `TestHidLoss:`, битая
строка `AudioStat`, счёт строк, строка в склеенной строке; тождества `fs7_n` — справка (`q_fail > pushes`, убывание `pushes`); «нет вреда» у каждого
тега — каждый маркер смерти в логе, маркер в stdout, нет stdout, кадр 1 000 000 / 999 999 мкс, кадр ≥ 1 с до первого кадра сцены и на нём, после
смены сцены, видео 2 999 / 3 000 / нет индекса, глитч 1, нет файла глитчей, нет листа, `hold_s` H − 1 / H, `hold_exit`, исход `timeout`, нет
входа, член раньше вреда; выход — `close_killed`, `close_rc` 1 не гейт, строка `EXIT`; нет лога; вывод в строгом cp1250 без `PYTHONIOENCODING`,
только ASCII, json, отказ чужого тега, `--dir` без `--tag`. Ручная чувствительность (`sens_fs7c.py`, 65 правок ридера): каждая ловится
набором (`ALL OK`). Регрессия на настоящих логах (`regress_fs7c.py`): ридер на `log_b24_h1.txt` F19e и `log_f8_n1.txt` F18e даёт числа пересчёта
лида п. 487(б) и п. 467(б) (`main_late_max_us` 3 000 289, `po_wait_max_us` 2 973 393, `pad_wait_max_us` 10, `guest_sdl` 0, видео 10 121; Ф8 0,
`init_calls` max 1, `acq` 285, кадр max 182 589 мкс, видео 25 725), члены «Fix», которых на тех бинарях нет, — NO, допуск — NO (иной бинарь)
(`ALL OK`).

**Печать (строки `seal:`; sha256 файлов `C:/kyty/f287/fs7c/` = `docs/track-f/fs7c/SHA256SUMS_seal.txt`):**

```
seal: 126afedf0be606d2c74e9d77ddc3e9aca1883c73567e39c654b6d47a8ebf9414 go_fs7c.sh
seal: 0338b4be4a80700469dec31f71c714b8c8c78af5dfd2942dc6f57343cf6bd6ae launch_fs7c.sh
seal: 2ea60a0534b627180753021ac6f2763fe9c35b52761e27fefde011c50ae8830b wait_fs7c.sh
seal: 16046d5248ec9f64e75a7b48527de0718f6a1d31b5260ab64ddb25f7b4d9fd70 post_fs7c.sh
seal: 262b9f826b2bbee281d100b8819969e32891db2f5cdea35210f4f1067f4be987 fs7c_read.py
seal: bc2b9302bf4465b9c6424669efa32dc171625b2a5118b57091532b181b7561be test_fs7c_read.py
seal: e92b985de1c3c03cadfd071373f02200324594402c82fc11da3d2814cbaecc70 test_fs7c_read.out.txt
seal: 9eeaccd656960a8f90201aa01717dfe8311a8b508757020bd7c45ca7e0ba3265 sens_fs7c.py
seal: 51565af9d7581b6d937dd1cf98798d9282583570a7e5897d9cb4545c21d1201a sens_fs7c.out.txt
seal: b16fc999c1a658052d7c947fdee61dcb54774ca2dd3254ca226852b3923edfdb refs_fs7c.py
seal: cb6fc911de2d3f45e7e74d823c01a85dc9d4c9456dc443fd24c5854d019cbf8a refs_fs7c.out.txt
seal: 922a044fdc80d1b2828bd284986bd8f0f5cdf69b7eafa447286c4ef5abf9cc66 regress_fs7c.py
seal: 0eddb8b5f465cb7fab61180fe9fdb3c34bb79130df83223f03fabfe289654bd0 regress_fs7c.out.txt
seal: 9976f56d00c448b835bcaa749dd226857149a07c08ed066e880029a9488b7ee9 enter_scene.py
seal: 93beec84687443f74e5ec6dfb5e0509808239bb89ca8810d137193ddbd36374d test_enter_scene_mask.py
seal: dad794012903e94adc2663a383c5f9e25da8ca1ba2d3ddbe938c7d3e906e52ca test_enter_scene_mask.out.txt
seal: d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0 procload.py
seal: c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96 idle142.py
seal: c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21 launch_run.py
seal: 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 run_safety99.py
seal: a7096fd47f70419a5ed8d541778294f3032ca2c88e7b4b2e946f3d99651182bb manifest_fs4c.py
seal: c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d sheet142.py
seal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 gates_default.txt
seal: a0b0eaeea70dc578ce27fac0b52dfcda988e72d48201189bacfae06ce6a6f207 watch_fs7c.py
```

## 8. Варианты исполнителя (рядом с буквой; вопрос лиду — в отчёте звена)

1. «До первой `GuestOut`» — первая строка лога с `GuestOut:` (любая, не только строка входа уровня); у строки `FixF8: mode=1` порядок только
   печатается (Н4).
2. «Строк `FixF8:` иного вида 0» — и для `FixB24`, `FixB4` (буква п. 487(г)(3) «`FixB24: mode=1` до первой `GuestOut`» читается с тем же
   требованием «ровно одна строка `mode=1`, иной формы 0»); `FixB4` в бинаре печатается как `FixB4: mode=%d` [c `fileSystem.cpp:406`], `mode=0` —
   провал члена.
3. Н3 — три строки допуска: sha256 (json и `installed_sha.txt`), строка версии в файле бинаря и текст ревизии `d6ee2dc` в логе (у F18e/F19e
   строка версии была справкой).
4. `fs7_h` — форма `b24_h1` без `KYTY_AV_TRACE` (буква п. 487(г)(3) «форма `b24_h1` при умолчаниях»); `KYTY_AV_TRACE=1` п. 467(г)(3) читается
   для `fs7_n` (тег п. 467(г)(3)); у `fs7_h` ридер `KYTY_AV_TRACE` не проверяет.
5. «Нет вреда» у `fs7_n` — вне окна нет (стенда нет): все кадры после первого кадра сцены; у `fs7_h` — вне широкого окна (F19e §8.1).
6. Окно стенда `fs7_h` — широкое (F19e §8.1), узкое печатается рядом.
7. Тождества `fs7_n` — справка (F18e, N2 п. 453(в)); `fs7_h` — слово `IDENT_FAIL` (F19e §8.4).
8. Установленный до и после тега — FS6 `9325446c` (п. 510), а не S12 `adb0c82f` описания звена (оно написано до установки FS6).
