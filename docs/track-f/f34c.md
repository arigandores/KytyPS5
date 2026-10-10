# F34c (`HPP-740`, Harness Engineer): серия Б6 — `b6_w0`, `b6_v`, `b6_vl`, `b6_w` на установленном FS11 `ea51ae80` — печать до тегов

Трек F, Б6 (K3, частицы и дым в комнате с пришельцем). Разделы 0–8 — печать (до первого тега; после неё цепочка, ридер и правила чтения не
меняются); раздел 9 — отчёт тегов (строки ридера, без вердикта; чтение — F34d `HPP-741`). Автор всех разделов — Harness Engineer. Метки: [c] —
код/лог прочитан или пересчитан, [I] — вывод, [U] — неизвестно. Время — UTC.

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1; проверка — `refs_f34c.py`, отрицательный контроль сдвигом)

- Задание — п. 673(з)(2): `c5c18e55:docs/ROADMAP.md:24283` (якорь «(2) **F34 = Б6 (K3).**»; +1 — «(3) **Довод свипа»). Решения лида по
  В1–В3 — п. 674: `c5c18e55:docs/ROADMAP.md:24290` (якорь «674. **Звено F34a»; +1 — «(а) **Приёмка.**»), (в) — `:24293` (якорь «(в) **В1 —»;
  +1 — «(г) **Правило исхода F34d»), (г) — `:24294` (якорь «(г) **Правило исхода F34d»; +1 — «(д) **В3:**»). Решения лида по RC1–RC9 отзыва —
  п. 676: `c5c18e55:docs/ROADMAP.md:24315` (якорь «676. **Звено F34b»; +1 — «(а) **Приёмка строкой.»), бюджет и повторы — `:24326` (якорь «(л)
  **Бюджет и повторы.**»; +1 — «(м) **Звенья:**»).
- Форма серии — §5 `72317680:docs/track-f/f34a.md:117` (якорь «## 5. Форма серии `b6`»), окно комнаты — `72317680:docs/track-f/f34a.md:103`
  (якорь «**Окно листа комнаты»; +1 — «`Level has started: intro_next`»); отзыв — `eef76f8c:docs/track-f/f34b-review.md:34` (якорь «**RC1 —»;
  +1 — «Что не так»).
- Код FS11 (worktree FS11a HEAD `ee9632be`): естественный старт без `KYTY_GUEST_ARGS` — `ee9632be:src/loader/runtimeLinker.cpp:134` (якорь
  «*source = "none";»; +1 — «std::getenv("KYTY_GUEST_ARGS")»); строка расписания ввода —
  `ee9632be:src/graphics/presentation/window/inputScript.cpp:151` (якорь «LOGF("InputScript: scheduled %s at present %u (hold %.0f ms)»);
  запись `.idx` видео (кадр, present, время) — `ee9632be:src/graphics/presentation/window/screenshot.cpp:513` (якорь
  «std::fprintf(m_rec_index, "%u %u %.3f»).
- Проверка ссылок — `refs_f34c.out.txt`: 12 `OK`, 12 сдвигов `NOT OK`, `ALL OK`.
- Образцы харнесса: форма п. 634 / 660 / 661 — F31c (`C:/kyty/f287/f31c/`); возврат кэшей на каждом теге и форма W `fs11_w` — FS11c
  (`C:/kyty/f287/fs11c/`).

## 1. Бинарь и окружение

- **Бинарь — установленный FS11** sha256 `ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce` [c 2026-10-10 15:56Z; `go_f34c.sh`
  проверяет до замка]; установки нет; член допуска — установленный до = после тега = FS11 по полному sha256. `C:/kyty/build/install` не
  трогается.
- **Окружение:** цепочка снимает все `KYTY_*` и `VK_LAYER_*` шелла; позиционно в `enter_scene.py` — `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`;
  у форм N (`b6_v`, `b6_v2`, `b6_w`) — `KYTY_KEYS=@2170:j,@2460:j` и **без** `KYTY_GUEST_ARGS` (опция `--natural`); у форм L (`b6_vl`, `b6_wl`) —
  `KYTY_GUEST_ARGS=-lvl intro_next`, без `KYTY_KEYS`; у `b6_w0` — `KYTY_GUEST_ARGS=-lvl underwater_aerial_garden`; у W —
  `--vulkan-validation true`, `VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin`, `VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000`, precache по умолчанию; у V —
  `KYTY_REC`. Константы `enter_scene.py`: `KYTY_FRAME_TRACE=lite`, `KYTY_GPU_HANG_ABORT_S=8`, `KYTY_GATE_FILE`, `KYTY_SAMPLE_GATE`, `KYTY_QUEUE_TRACE=1`.
  Не передаются: `KYTY_GAME_PATCH`, `KYTY_DIAG_*`, `KYTY_TEST_*`, `KYTY_FIX_*`, `KYTY_S_REPLAY`, `KYTY_SHADER_SEED`, `KYTY_PIPELINE_PRECACHE`,
  `KYTY_GPU_CHECKPOINTS`, `VK_LAYER_MESSAGE_ID_FILTER`. Окно 1280×720, `--shader-validation false`, без `--rd`.

## 2. Кэши, сохранения и манифест

- Состав — пять каталогов харнесса FS11c: `_ShaderCache`, `_ShaderSeeds`, `_PipelineCache`, `_SaveData` (сохранение титула — F34a §2.3), GLCache
  драйвера.
- **Манифест до первого тега** (без замка, только чтение, 2026-10-10 15:52Z): `C:/kyty/f287/f34c/base/base.tsv` — 4 804 файла, 1 302 773 008 байт,
  `listsha` `64084958f37f864960144031ea18aaa06a07fd857b47eb625412477d6085839d`. Состояние — после возврата серии F31c (`f31c/RETURNED`
  2026-10-10 13:03:22Z); метки каталогов у F31c другие (`ShaderCache_PPSA21564`), сравнение с её манифестом не построчное — строка, не член.
- **Каждый тег:** под замком — манифест и копия пяти каталогов (`runs/<тег>/before_*`); после тега — возврат (`rm` + `mv`) и манифест после;
  член допуска — `manifest cmp EQUAL` до/после. Сверка «до тега = база» — строкой (`runs/<тег>/base_cmp.txt`). Сеанс пользователя во время
  тега — возврат GLCache слиянием (`snap_f34c.py merge-return`), член — «манифест до ⊆ после, лишние — только GLCache» (`mfsub_f34c.py`); тег —
  помеха. Неудачный возврат, установленный ≠ FS11 или `cmp` ≠ EQUAL — `RETURN_FAILED`, замок остаётся, вопрос лиду.

## 3. Форма тегов (один вызов — один замок, одна попытка)

| тег | что | вызов `enter_scene.py` из `go_f34c.sh` (кроме общего `--attempts 1 --no-install --require-idle --gates-file gates_default.txt --pred pred/f34c_seal.md`) |
|---|---|---|
| `b6_w0` | контрольный W, Sky Garden = `fs11_w` FS11c | `--level underwater_aerial_garden --stable-draws 100 --timeout 900 --emu-arg=--vulkan-validation --emu-arg=true --hold 310 VK_LAYER_PATH=… VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` |
| `b6_v` | V формы N, попытка 1 | `--level intro_next --natural --stable-draws 500 --timeout 600 --rec --hold 600 --proc-limit 600 --until-sublevel 600 KYTY_KEYS=@2170:j,@2460:j KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` |
| `b6_v2` | V формы N, попытка 2 — только при «не достигнута» у `b6_v` | как `b6_v` |
| `b6_vl` | V формы L (п. 674(в)) | `--level intro_next --entry-at-level --stable-draws 500 --timeout 600 --rec --hold 600 --proc-limit 600 --until-sublevel 600 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` |
| `b6_w` | W формы N | `--level intro_next --natural --stable-draws 500 --timeout 1800 --emu-arg=--vulkan-validation --emu-arg=true --hold 1800 --proc-limit 1800 --until-sublevel 300 KYTY_KEYS=… VK_LAYER_PATH=… VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` |
| `b6_wl` | W формы L — по п. 674(г)(3) или 676(и) | как `b6_w`, но `--entry-at-level` и без `KYTY_KEYS` |

- **Завершение** (новые опции `enter_scene.py`, по умолчанию выключены, старые формы не меняются): `--natural` — без `KYTY_GUEST_ARGS`, вход —
  строка `GuestOut: Level has started: intro_next`; `--until-sublevel K` — удержание кончается, когда после строки `SubLevelLocator
  sublevel_locator_space [...] state changed 7->6` пришла `FrameTrace` с `n` ≥ n_sw + K; `--proc-limit S` — удержание кончается через S с от
  старта процесса. У V: `n` ≥ n_sw + 600 или 600 с; у W: `n` ≥ n_sw + 300 или 1 800 с (F34a §5.2, п. 674(в), (г)(3), 676(г)). Вход не достигнут к
  `--timeout` — процесс снимается, лог читается (у V — «не достигнута», у W — `W_NOT_ENTERED`).
- **Порядок (п. 674(в)):** `b6_w0` → `b6_v` → (`b6_v2`) → `b6_vl` → `b6_w` (или `b6_wl` по п. 674(г)(3) / 676(и)). Серия идёт тег за тегом; блоков
  тегов и окна нет; проверка сторожа одна на вызов — сразу после взятия замка, до манифеста (п. 634, 660, 661). Провал `b6_w0` — `SERIES_STOP`,
  вопрос лиду, теги Б6 не идут. `b6_v` и `b6_v2` не достигли комнаты и `b6_vl` не дал листа — исход (iii), W не запускается.
- **Цепочка:** `chk_f34c.sh <тег>` (файл `STOP`, замок, новые комментарии `HPP-740`, очередь P > F > S — строка `times.txt`) → `launch_f34c.sh <тег>`
  (первая строка — линтер `form634_check.py --series`; дисплей: OFF — `dispstate.py --wake` и повторная проверка, п. 623(в)(1); предел повторов;
  очередь; только запуск) → `wait_f34c.sh <тег>` ≤ 540 с за команду, отдельными командами → `post_f34c.sh <тег>` вне замка (у V:
  `s51_vidglitch.py <rec> 4 6`, листы `sheets_f34c.py`, лист всего видео `sheet142.py` — справка; затем ридер и таблица). `go_f34c.sh`: линтер,
  sha установленного, шлюз `procload.py` (маска `<app>`), проверка живого прогона по API (`runchk_f34c.py`), загрузка хоста (строка), дисплей ON
  до замка и удержание до `lock released`, замок `C:/kyty/SEALED_RUN.lock` (`noclobber`), строки `lock taken|released <тег> <UTC>` в
  `runs/lock.log`, **сразу после замка** — сторож игры и сеанса пользователя (найден — замок снят, файлы не тронуты, помеха), затем манифест и
  копия, сторожа во время тега (опрос ≤ 2 с; найден — убийство своего эмулятора по pid), возврат, `manifest cmp`, дисплей после. Повтора тега с
  тем же именем нет (`runs/<тег>` есть — отказ).

## 4. Правило чтения (ридер `f34c_read.py`; вердикта нет)

**Определения.** `n_cur` строки — `n` последней `FrameTrace` перед ней по положению в логе (п. 676(е)(1); поле `frame=` строк `AsyncPipelines` не
читается). n_intro — `n` первой `FrameTrace` после строки `GuestOut: Level has started: intro_next`; n_sw — `n` первой `FrameTrace` после первой
строки смены подуровня `space` 7->6; Δ = n_sw − n_intro. `off` (формы N) — медиана (present − `n_cur`) по строкам `InputScript: press|release`;
у форм L `off_L` — [U] ∈ [0; 25], не вычисляется, печатается строкой «`off_L` [U]» (п. 676(в)). Окно комнаты в `n` — [n_intro + 2 880; n_intro +
3 330]. Кадры катсцены (V2): N — записи `.idx` с present в [n_intro + off; n_sw + off]; L — в [n_intro; n_sw + 25]. Лист комнаты (V4): N —
present в [n_intro + off + 2 880; + 3 330] шагом 10 (46 плиток 384×216); L — [n_intro + 2 880; n_intro + 3 355] шагом 10 (48 плиток); четыре
кадра 960×540 на +2 950, +3 050, +3 150, +3 250 (у L без поправки); кадр берётся по ближайшему present `.idx` в пределах ±3, иначе «missing».

**Допуск (член не выполнен — `INTERFERENCE`, тег не читается; повтор — строкой `times.txt`, п. 676(л)):** json есть; `binary_sha256` = FS11;
установленный до = после = FS11; `prereg` = sha256 этой печати (`pred/f34c_seal.md`); `env` = форма §1 ровно (ключи `KYTY_*`/`VK_*`; пути —
любые); последний `--vulkan-validation` — `true` только у W; `--shader-validation false`; без `--rd`; аргументы гостя формы (у N — нет) и
файл уровня харнесса; опция удержания (310 / 600 / 1 800); лог есть; строк `Window … minimized` и `Recovering Vulkan swapchain` 0; подпись
`9177b426` и каталог `variant_fixb26_fixb1b_fixf10_fixf19`; строк `GamePatch:`, `DiagB32`, `TestLogStall:` 0; `manifest cmp EQUAL`; итоговая
строка `LogAsync: full_waits=` ровно одна со всеми полями (нет — помеха «снят убийством»; **не применяется к W катсцены со строкой
`[Vulkan][E]`** — слой кончает процесс, п. 676(б)); у `b6_w0` ещё исход входа `ok` и строка входа Sky Garden. Харнесс (вне ридера): дисплей ON
до замка и после `lock released` (OFF после — помеха `DISPLAY_OFF`), игра и сеанс пользователя во время тега — помеха.

**Члены пути (F34a §5.3):** N — (П1) `GuestArgs: source=none argc=1`, `-lvl` в argv нет; (П2) по одной строке `InputScript: scheduled j at present
2170` и `2460`, по одной строке `press j` с present 2170 и 2460; (П3) строка титула `title_controller_ship` раньше первой `press`, строка
`intro_next` позже второй `press`, n_intro есть. L — (П1) `GuestArgs: source=KYTY_GUEST_ARGS argc=3`, argv `-lvl intro_next`; (П2) строк ввода 0;
(П3) строка `intro_next` и n_intro есть. V — (П4) строка смены подуровня есть и Δ ∈ [4 480; 4 620]; (П5) последняя `FrameTrace` `n` ≥ n_intro +
3 330. W — (П4) справка; (П5)_W строка смены подуровня есть и последняя `FrameTrace` ≥ n_sw + 300 (п. 676(г)).

**Члены V (`b6_v`, `b6_v2`, `b6_vl`):** (V1) процесс жив до завершения (`outcome ok`, `hold_exit` пуст) и 0 маркеров смерти в логе и stdout
(`Unhandled exception:`, `--- Fatal Error ---`, `--- Error ---`, `GpuHangAbort:`, `ErrorDeviceLost`); (V2) записей катсцены ≥ 3 000; (V3) 0
одно-кадровых глитчей детектора на записях катсцены (счёт по всему видео — справка); (V4) листы сделаны (последняя строка `sheet.txt` —
`sheets done`); (V5) строк `AsyncPipelines: skipped draw` и `held (incomplete frame)` с `n_cur` в окне комнаты 0. **Статус пути V:**
`NOT_ENTERED` (не (П3)) → `ROOM_NOT_COVERED` (не (П5)) → `TIMELINE_OTHER` (нет строки подуровня или Δ вне полосы) → `ROOM_COVERED`. Флаги
помехи: `DEATH_MARKER`, `NOT_LIVED`, `COLD_ROOM` (у `ROOM_COVERED` при (V5) > 0).

**Члены W катсцены (`b6_w`, `b6_wl`):** процесс жив до завершения; 0 маркеров смерти; 0 `[Vulkan][E]` (счёт в окне комнаты и вне его — по
построению ≤ 1); 0 строк предела слоя (`this will be the last time reporting it`); положительный контроль — ≥ 1 строки `[Vulkan][W]` с
`n_cur` ≥ n_intro (п. 676(д)); строка формы W из окружения `limit=100000000 filter=none` (п. 295(б)(4)); `DualSrcBlend: supported=1 enabled=1` и
`LogAsync: mode=1` до первой `GuestOut`; нет `VALIDATION_STOP`. Член п. 295(б)(3) — справка (`n` последней строки слоя против последней
`FrameTrace`). **Статус пути W (порядок — приоритет):** `W_LAYER_ERROR` (≥ 1 `[Vulkan][E]`: читается только по п. 674(г)(2); `W_SHORT`, маркер
смерти и `VALIDATION_STOP` к тегу не применяются; печатается `n` остановки против окна комнаты и «room not passed by the layer» при остановке до
n_intro + 2 880 или до входа, п. 676(б)) → `W_NOT_ENTERED` (не (П3), п. 676(и)) → `W_SHORT` (строки подуровня нет, п. 676(г)) → `W_TAIL_SHORT`
(строка есть, хвост < n_sw + 300 — пунктами не назван, вопрос лиду) → `W_NO_POSITIVE_CONTROL` (п. 676(д)) → `W_MEMBERS_ALL_YES` /
`W_MEMBERS_NOT_ALL_YES`. Маркер смерти без `[Vulkan][E]` — флаг `DEATH_MARKER` (помеха, F34a §5.4).

**`b6_w0`:** члены `fs11_w` FS11c без изменений — процесс жив до конца удержания (`hold_s` ≥ 310); 0 маркеров смерти; 0 `[Vulkan][E]`; 0 строк
предела; `[Vulkan][W]` > 0; `DualSrcBlend` и `LogAsync: mode=1` до первой `GuestOut`; нет `VALIDATION_STOP`; `FixB13: mode=1`; `FixB12: mode=1`.

**`COLD_ROOM` (п. 676(е)):** счёт по положению строки; печатается `n` 64-й строки `held`; если 64-я строка раньше конца окна комнаты — строка
«held in the window [U]», сама по себе не `COLD_ROOM`. Счётчиков `skc_*` в `lite` нет — только строки.

**Справка ридера:** кадры `dt_us` ≥ 1 000 000 до и после n_intro, строки со словом «translat» до строки входа, строки `ShaderReplay:`,
`PipelinePrecache:`, `ShaderPreparation: startup wait`, `FixSval:`, `LogAsync: mode=`, sha256 лога; `hold_end` харнесса (`sublevel` / `proc_limit` /
`hold`) и его `n_sw`, `n_end`.

**Что читает лид, не ридер (п. 673(з)(2), 674(г), 676(ж), (з), (к)):** «комната достигнута» — пришелец в комнате на листе (V4); видимый дефект
частиц или дыма на листе любой формы; расхождение N/L по частицам и дыму на тех же смещениях (листы `room_b6_v.png` и `room_b6_vl.png`, пара
`pair_<тег>.png` — строки тега, `u_02` FS8 и `rec_e` с. 30 на +2 950…+3 250); каждый глитч детектора кадрами ± 2. Ридер печатает члены и
статусы, исход (i)–(iii) и «не определено» — F34d.

## 5. Повторы, отказы, остановка

- Одна попытка на тег. Повтор `<тег>_r1`…`_r4` — по помехе п. 676(б)–(е), (и) строкой `times.txt` с членом-основанием **до** вызова
  (`launch_f34c.sh` без `F34C_REPEAT_OK=1` повтор не запускает); общий предел повторов серии — 4 начатых повтора (повтор считается начатым, если
  его `run.txt` несёт `--- attempt 1: launching`); пятый — отказ `launch_f34c.sh` (выход 11), исход — «не определено» пунктом F34d. Повторы — вне
  бюджета.
- По п. 676: `W_LAYER_ERROR` не повторяется; `W_SHORT` — один повтор, второй ⇒ «не определено»; `W_NO_POSITIVE_CONTROL` — один повтор, вторая
  подряд помеха по тому же члену ⇒ «не определено»; первый `COLD_ROOM` — один повтор той же формы, второй ⇒ «не определено»; `W_NOT_ENTERED` —
  один повтор, второй ⇒ W в форме L (`b6_wl`); `ROOM_NOT_COVERED` / `TIMELINE_OTHER` у `b6_vl` — без повтора (детерминированы формой, п. 676(з));
  у формы N «не достигнута» — `b6_v2`.
- Отказ шлюза `procload`, сторожа после замка, очереди или дисплея до старта эмулятора — не попытка; вывод отказанного вызова переносится в
  `old/` (п. 309(и)). `SERIES_STOP` — следующий тег не запускается до пункта лида. `RETURN_FAILED` — замок остаётся. Файл `C:/kyty/f287/STOP` —
  стоп перед следующей командой. Перед каждым вызовом — `chk_f34c.sh` (API, комментарии звена, очередь) строкой `times.txt`.
- **Бюджет замка серии без повторов — ≤ 105 мин** (п. 674(в)); оценки F34a §5.5 — [I], «читать как верх».

## 6. Не заявляется

П. 673(л), 674(ж), 676(н) целиком: что Б6 — дефект или не дефект; что игра корректна на какой-либо сцене; что комната достижима вводом на FS11;
что катсцена идёт по флипам или по времени под валидацией; что слой пишет предупреждения в катсцене; что `COLD_ROOM` наступит; что `off_L` ∈ [0;
25]; что `-lvl` и естественный старт дают одинаковую картинку комнаты; что дымка и искры кадров FS8 — предмет замечания пользователя; что оценки
бюджета верны. Ни одно число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется; установленный FS11 не меняется.

## 7. Инструменты и фикстуры (до первого тега; файлы `C:/kyty/f287/f34c/`, копия — `docs/track-f/f34c/`)

- `go_f34c.sh` — порт `go_fs11c.sh` (возврат кэшей на теге) в форме `go_f31c.sh` (п. 634: сторож один раз сразу после замка), без установки
  бинаря; `launch_f34c.sh` — порт `launch_f31c.sh` + предел повторов п. 676(л); `wait_f34c.sh`, `chk_f34c.sh` — порт F31c с переносом имён;
  `post_f34c.sh` — порт FS11c без члена темпа (пункты его не называют).
- `enter_scene.py` — файл F31c, `ROOT` перенесён, три опции (§3), по умолчанию выключены; `f34c_read.py` — ридер (§4), порт `fs11c_read.py`;
  `sheets_f34c.py` — листы (порт F34a `sheet.py`, `pair.py`).
- Копии без изменений: `dispstate.py`, `procload.py`, `idle142.py`, `launch_run.py`, `run_safety99.py`, `manifest_fs4c.py`, `gates_default.txt` (F31c),
  `sheet142.py` (FS11c); с переносом имён: `guard_f34c.py`, `hold_f34c.py`, `hostload_f34c.py`, `runchk_f34c.py`, `queue_f34c.py` (F31c),
  `snap_f34c.py`, `mfsub_f34c.py` (FS11c).
- **Последний вывод наборов** (полные sha — `SHA256SUMS_seal.txt`):
  - `test_f34c_read.out.txt` — первая строка `suite test_f34c_read.py sha256 761851f3… target f34c_read.py sha256 adfcd984…`, `checks 198 failed
    0`, `ALL OK` (чистые теги пяти форм; каждый член допуска; (П1)–(П5); (V1)–(V5); члены п. 676: (б) — `[E]` до комнаты, на n_intro + 2 879 /
    + 2 880 / + 3 331, до входа, маркер выхода слоя не флаг; (в) — окна L и N; (г) — `W_SHORT`, хвост n_sw + 299 / + 300, Δ вне полосы у W —
    справка; (д) — `[W]` только до n_intro, ровно один после, строка предела; (е) — строка в окне по положению при `frame=` вне окна и наоборот,
    края окна, 64 / 63 строки `held`; (з) — `ROOM_NOT_COVERED` / `TIMELINE_OTHER`, Δ 4 479 / 4 480 / 4 620 / 4 621; (и) — `W_NOT_ENTERED` у N и
    L; (к) — глитч в катсцене, на краях P_intro − 1 / P_sw + 1, n_sw + 25 у L; вывод в строгий cp1250, ASCII). Отрицательные контроли набора
    вручную (вне печати): 15 правок констант и ветвей ридера — убиты 15 из 15 (после добавления фикстуры `[W]` до n_intro по положению). Мутантов
    `mutlib` нет — пункты 673, 674, 676 их не называют (форма FS11c).
  - `test_tools_f34c.out.txt` — первая строка `suite test_tools_f34c.py sha256 6d291cbe… target go_f34c.sh sha256 3fad9188…`, `checks 75 failed 0`,
    `ALL OK` (сухой план шести форм и повторов `_r1`/`_r4`, отказы по имени, повтор без строки, предел повторов 4 (неначатый не считается),
    линтер `--series`, первая исполняемая строка — линтер, нет установки бинаря, сторож после замка до манифеста, `SubTracker` на
    синтетическом логе (края K), опции `enter_scene.py`, ASCII скриптов, вывод в строгий cp1250).
  - `refs_f34c.out.txt` — 12 ссылок, `ALL OK`.
  - **Линтер формы п. 634 / 661** — `C:/kyty/KytyPS5/ps5 em/docs/form634_check.py` sha256
    `f100a063fbc0063266a6443bac9b68f17e832fddd29456ccb475e7b1e76a4ded`; он же — первая исполняемая строка `launch_f34c.sh` и `go_f34c.sh`:

```
$ python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f34c
ALL OK
$ python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --text C:/kyty/f287/f34c/pred/f34c_seal.md
ALL OK
```
- **Регрессия на настоящих логах (без игры):** ридер на `f26c/log_b25_01.txt` (FS10, `-lvl intro_next`) — n_intro 310, n_sw 4 851, Δ 4 541, (П1)–(П5)
  ДА; на `s288/s15/log_u_02.txt` (FS8) — n_intro 232, n_sw 4 763, Δ 4 531, (П1)–(П5) ДА (= F34a §3.1); `sheets_f34c.py` на `rec_u_02.mp4` — 48 плиток
  комнаты без пропусков, пришелец в комнате на плитках [c листа], пара трёх строк собрана.

## 8. Варианты исполнителя (рядом с буквой; вопрос лиду — в отчёте звена)

1. Вход формы N — строка `Level has started: intro_next` без строки `LevelDocument Loaded` (у N её наличие не проверялось F34a).
2. (V1) «жив до завершения» = `outcome ok` и `hold_exit` пуст; завершение по пределу процесса — тоже «жив»; покрытие решает (П5).
3. Окно (V5) у L — то же окно в `n`, что у N ([n_intro + 2 880; + 3 330]): `n` — домен лога, `off_L` для него не нужен.
4. `COLD_ROOM` ставится только у статуса `ROOM_COVERED`; у прочих статусов счёт (V5) — строка.
5. `W_TAIL_SHORT` — пунктами не назван; печатается статусом, решение — лида.
6. Кадр листа — ближайший present `.idx` в ± 3; дальше — «missing» строкой `sheet.txt`.
7. Сверка «кэши до тега = база» — строкой, не членом; база — после возврата F31c.
8. Начатый повтор для предела п. 676(л) — по строке `--- attempt 1: launching` его `run.txt`.

## 9. Отчёт тегов

(заполняется после серии; печать выше не меняется)
