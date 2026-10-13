# M5a — раздел HLE1: T125, T055 + T298 + T059, T023, T031 (офлайн, только чтение)

Код: KytyPS5 `main` HEAD `dd73d04d` (рабочее дерево = HEAD по затронутым файлам). Ссылки `dd73d04d:<путь>:<строка>`.
Источники исполнения: импорт NID (`imp_m5a.py`), места вызова в коде игры (`avcall_m5a.py`, `fmt_m5a.py`, дизассемблер
`C:/kyty/f287/f26a/eboot.elf` средствами F26a — `docs/track-f/f26a/f26a_dis.py`, `plt.tsv`), строки журнала
(`scan_m5a.py` — один потоковый проход по `C:/kyty/m657/m3a/log_m3_sg_v_r1.txt` (MS1), `log_m3_hb_f.txt` (FS15),
`log_m3_i.txt` (MS1), `log_m3_hb_w.txt` (MS1); для счёта вызовов `AudioOut2ContextPush` — лог с `KYTY_AV_TRACE=1`
`C:/kyty/f287/f18e/log_f8_s1.txt` (тег F18e, бинарь `35c4a754`; `libAudio2.cpp` с тех пор менялся только метками
`KYTY_DIAG_B32` `a92c4a1ac`)), стенды-модели (`stands_m5a.py`, `ALL OK`). Игра, сборки, ГП — не запускались.

**Общее про журнал [c кода]:** `PRINT_NAME()` в `libAudio2.cpp`, `avPlayer.cpp`, `agc.cpp`, `libC.cpp` молчит
(`PRINT_NAME_ENABLED` — `thread_local false` из `LIB_NAME`, `dd73d04d:src/libs/libs.h:22-23`; печать только при
`KYTY_PRINT_NAMES`), в логах M3 строк `[tid][время] AvPlayer::…`/`AudioOut2::…` 0. Видны только `LOGF`:
блок `AudioOut2PortCreate` (`dd73d04d:src/libs/libAudio2.cpp:651-663`, объектные порты — разреженно: № ≤ 16 и
кратные 600), `\t port = 0x…` (`PortDestroy`, :670), `\t event_id = N` (`dd73d04d:src/libs/avPlayer.cpp:1819`),
блок `AvPlayerInit`/`AddSource` (:1877-1903, :1948). `AudioOut2PortSetAttributes` и `AudioOut2ContextPush` строк не
пишут (Push — только `AvTrace: push` при `KYTY_AV_TRACE`).

## Сводная таблица

| тема / коммит | исход | исполнение игрой | основание |
|---|---|---|---|
| T125 `c86c8b4d9` (смешение объектных портов 0x100, GAIN) | **паркуется** до счётчика «PCM на объектном порту» в игре (условие ниже) | создание объектных портов [c]: 18 записей `port_type = 256` при `audio_handle = 0` в каждом из 3 логов с полным стартом (в `hb_w` — 15), номера портов до 2 400, строк `PortDestroy` 2 517 / 2 853 / 2 888 / 888; Push ≥ 15 000 вызовов [c `log_f8_s1`]; задание PCM (атрибут 0) на объектные порты — [c статически, код игры `os_ppr_audio_out.c`], во время работы — [I] (строки журнала у пути нет) | наш код отбрасывает PCM портов без устройства: `dd73d04d:src/libs/libAudio2.cpp:631-635` (объектному порту устройство не открывается) и `:363` (`state.audio_handle > 0` в отборе на вывод) [c]; стенд S4 |
| T125 `313b60e92` (копия PCM в момент SetAttributes) | **паркуется** до показа общего буфера PCM у ≥ 2 портов с устройством в одном Push (или правки буфера между SetAttributes и Push) | импорт [c]; 5 мест вызова `PortSetAttributes` [c]; общий буфер — [U] | мы храним указатель `dd73d04d:src/libs/libAudio2.cpp:704`, читаем его в Push :365; в коде игры указатели PCM портов шин — разные ячейки таблицы (`[r15+r12*0x38+0x18300]`, `dis_ao2_setattr_m5a`) [c статически], объектных — у каждого голоса свой [I] |
| T055 `35a275e97` (STOP по концу потока) | **НЕ ДЕФЕКТ** | ролик `data/prein/video/06_nx_controller_ship.mp4` [c `sg_v_r1`, `i`, `f8_s1`] | поведение «STOP по EOF» снято самим upstream в `fa51da4d7`; конец ролика игра узнаёт опросом `IsActive && свой флаг`, не событием [c дизассемблера `0x1055230`] |
| T055 `6b79b7a00` (Ready/Playing/Stopped; `IsActive` истинна до Start и без источника) | **НЕ ДЕФЕКТ** | `IsActive` — 1 место вызова `0x105523d` [c] | обёртка игры возвращает `AvPlayerIsActive(h) && byte[obj+0x290]`; байт ставит только успешный Start (`0x1054a85`), снимает Stop (`0x1054b55`) [c] ⇒ различие «до Start / без источника» игре не видно; стенд S3: обёртка равна у нас и upstream на всём порядке вызовов |
| T055 `fa51da4d7` (STOP при Stop только из Playing) | **НЕ ДЕФЕКТ** на наблюдённом пути; путь «Stop до Start» — **паркуется** до строки `event_id = 1` без предшествующей `event_id = 3` | события READY,PLAY,PAUSE,PLAY,PAUSE,PLAY,WARNING,STOP — по 8 строк `event_id` в `sg_v_r1`, `i`, `f8_s1` [c] | наш STOP безусловен (`dd73d04d:src/libs/avPlayer.cpp:2041`); на наблюдённой последовательности Stop идёт из Playing ⇒ ответ тот же (стенд S3) |
| T055 `d792dfa88` (Pause/Jump до Playing → ошибка) | **паркуется** до строки `event_id = 4` или `= 32` раньше первой `event_id = 3` | 3 лога: PAUSE и WARNING только после PLAY [c] | наш Pause/Jump не проверяют состояние (`:2049-2050`, :2158-2161); на наблюдённом пути ответ тот же; недостижимость пути «до Start» не доказана |
| T055 `12ff57160` (SetAvSyncMode до AddSource сохраняется) | **НЕ ДЕФЕКТ** | единственное место вызова `0x10540a4` — после успешного `AddSource` (`0x105403f`, `js` на ошибку) и ожидания флага `[obj+0x298]`, условно по `[obj+0x58]&1`, аргумент 1 [c дизассемблера] | наш отказ при `source == nullptr` (`dd73d04d:src/libs/avPlayer.cpp:2085`) у игры недостижим |
| T298 `a6f4e8e7f` (буфер видео сразу назад декодеру) | **паркуется** до счёта «кадр к сроку не готов» (повторы кадра ролика) при нашей схеме | `num_output_video_framebuffers = 6` [c 3 лога]; `GetVideoDataEx` — 1 место `0x1055ddc` [c] | у нас 4 отданных буфера держатся до возврата (`dd73d04d:src/libs/avPlayer.cpp:963-967`) — декодеру остаётся ≤ 1 буфер; это не неверный ответ, а возможное опоздание [U]; схема upstream рискует перезаписью кадра, который ГП ещё читает [I] |
| T059 `25f269952` (aspect_ratio = только SAR) | **паркуется** до (а) чтения поля игрой и (б) первоисточника семантики `aspectRatio` | `GetStreamInfo` 1 место `0x1054706`, `GetVideoDataEx` 1 место [c]; чтение `aspect_ratio` игрой: в функции `0x10546a0…0x1054970` слот `[rbp-0x40]` не читается, в `0x1054b70…0x1054eb0` копия `[obj+0x1e0]` только записывается [c в пределах модуля VideoPlayerOrbis `0x1053800…0x1056400`], вне модуля — [I] | наша формула `dd73d04d:src/libs/avPlayer.cpp:1408-1417` (ш/в × SAR); какая верна — [I] |
| T023 `49b2eedd1` (GetAvailableSizeDW) | **паркуется** до показа `cursor_down < cursor_up` (или нулевого курсора) на входе HLE `ReserveDW` | путь `ReserveDW` исполняется [c: 71 импорт `libSceAgc*`, 1 175 мест, F26a]; различающее состояние — [U]: строк `suspiciously large`/`exhausted`/`grow callback`/`AllocateDW failed` 0 и сигнатур Б25 0 в 5 логах | стенд S1: решения различаются только при `up = 0`, `down = 0`, `down < up`; при ненулевых курсорах и `down > up` — тождественны [c]; в этом состоянии мы зовём обработчик гостя (у игры — заглушка assert Б25, F26a), upstream пишет за `cursor_down` |
| T031 `bab1c3614` (отрицательная `%.*`) | **НЕ ДЕФЕКТ** для ASTRO BOT (путь недостижим по литералам); дефект кода вне игры [c] | 0 форматов с `.*` в `eboot.elf`/`eboot.bin`, `libc.prx`, `libSceNpCppWebApi.prx` [c]; HLE-путь `guestPrintf` исполняется через `printf` (762 места), `vsnprintf` (24 места, 22 обёртки, логгер `0x27e3d0` — 1 241 место), `puts` (48) [c статически] | `dd73d04d:src/libs/guestPrintf.cpp:528-530`: `prec < 0` ⇒ точность 0 при поднятом `FLAGS_PRECISION` (печатает пусто), по C11 7.21.6.1p5 — «как если бы опущена»; стенд S2: наш `[]`, стандарт и msvcrt `[abcdef]` |

Тем с исходом «А [c]» нет: ни у одной различающей ветви исполнение игрой в журнале не показано.

## T125 — AudioOut2 (`313b60e92`, `c86c8b4d9`)

**Код [c].** `AudioOut2PortCreate` открывает устройство только для необъектных портов
(`dd73d04d:src/libs/libAudio2.cpp:631-635`, условие `!audioout2_port_type_is_object(params->port_type)`, :303-305
`(port_type & 0xff00) == 0x0100`); объектный порт получает `audio_handle = 0`. `AudioOut2PortSetAttributes` пишет
указатель PCM и в объектный порт (:704), но `audioout2_queue_context_audio` отбирает на вывод только
`state.audio_handle > 0 && state.pcm_data != nullptr` (:363-365) ⇒ PCM объектных портов не выводится никуда.
`c86c8b4d9` открывает на контекст одно стерео-устройство объектов и смешивает их туда (центр, `GAIN`, `AMBISONICS`
id 8). Стенд S4: при 22 портах с PCM (4 с устройством + 18 объектных, как в логах) у нас в вывод идут 4, у upstream
4 + 1 смесь 18 объектов.

**Исполнение.**
- Импорт [c]: 15 из 28 NID AudioOut2 (`libSceAudioOut2_v1`/`libSceAudioOut_v1.1`), в т. ч. `PortCreate`
  `JK2wamZPzwM`, `PortSetAttributes` `8XTArSPyWHk`, `ContextPush` `aII9h5nli9U` (`imp_m5a.out.txt`).
- Журнал [c] (`scan_sg_v_r1_m5a.out.txt`, `scan_m3_m5a.out.txt`): в `sg_v_r1`, `hb_f`, `i` — по 22 блока
  `PortCreate`: `port_type` {0:1, 1:1, 3:1, 6:1, 256:18}, у всех 256 `audio_handle = 0`, у 0/1/3/6 — > 0; номера
  портов 1…16, 22, 23, 600, 1 200, 1 800, 2 400 (≥ 2 400 созданий: печать разрежена); строк `PortDestroy` 2 888 /
  2 517 / 2 853; в `hb_w` (с валидацией) 19 блоков, 15 объектных, 888 удалений. Формат объектных —
  `data_format = 0x00000100` (моно float).
- Push [c `avtrace_f8_s1_m5a.out.txt`]: `AvTrace: push ctx=0x1 … n=15000` (печать n ≤ 5 и каждые 1 000) —
  ≥ 15 000 вызовов `AudioOut2ContextPush`; `AudioStat` порт 0 — 15 844, порт 2 — 15 827 выводов.
- Код игры [c статически, `dis_ao2_*_m5a.out.txt`, модуль `os_ppr_audio_out.c`]: `0xeb2440` создаёт порты
  `port_type 0x100`, `data_format 0x100`, 48 000 Гц — по порту на канал голоса, ручки в `obj+0x48+k·0x28`;
  `0xeb2720` в цикле с шагом `0x28` по `[rbx+0x20]` (то же смещение `0x48`) вызывает `PortSetAttributes` с 6
  атрибутами: id 0 (PCM, `{data}`), 1 (gain), 4, 2, 5 (0/1/2), 3 (12 байт — позиция xyz); `0xeb2d50` — id 0, 1, 8
  на порты `[r14+r15*2+0x30]`. Что это одни и те же объекты — по совпадению раскладки [I].
- Во время работы: строка журнала у `PortSetAttributes` отсутствует ⇒ задание PCM объектным портам [I], слышимость
  пропажи [U].

**`c86c8b4d9` — паркуется до:** тега с ручкой только измерения (предложение: `KYTY_DIAG_AO2OBJ`, умолчание 0, вне
набора подписи — HLE), считающей на `PortSetAttributes` число заданий PCM (id 0, `data != nullptr`) на портах
`0x100` и на `ContextPush` — число объектных портов с PCM и суммарную энергию их отсчётов; ≥ 1 задание с ненулевой
энергией ⇒ исход «А [c]». Набросок критерия «ИСПРАВЛЕНО» на этот случай (до кода): ручка `KYTY_M_T125` (умолчание
0); стенд без игры на `AudioOut2*` (контекст `max_object_ports > 0`, 4 порта шин + N объектных с синусом): при `=0`
объектный PCM в выводе 0 (воспроизводит), при `=1` — смесь объектов в стерео-устройстве контекста, `GAIN` применён,
порты шин байт в байт как при `=0`; мутант — отбор объектов в смесь без `GAIN` (или без проверки `audio_format`)
обязан ловиться стендом; подпись трансляции не меняется (HLE). Зависимости `c86c8b4d9` от SDL3, `313b60e92`,
`0471c9991` — как в описи.

**`313b60e92` — паркуется до:** того же счётчика с полем «один указатель PCM у ≥ 2 портов с устройством в одном Push»
или «байты буфера изменились между SetAttributes и Push». Статически у портов шин указатели берутся из разных ячеек
таблицы `[r15 + idx·0x38 + 0x18300]` [c], общий буфер не виден; Push у игры синхронен на том же потоке после
SetAttributes [I].

## T055 + T298 + T059 — AvPlayer

**Импорт [c]:** 17 из 28 NID (`libSceAvPlayer_v1`), нет `GetAudioData`, `GetVideoData`, `InitEx`, `AddSourceEx`,
`StartEx`, `GetStreamInfoEx`, `DisableStream`, `ChangeStream`, `CurrentTime`, `SetAvailableBandwidth`,
`SetLogCallback`. По одному месту вызова на функцию, все в модуле `VideoPlayerOrbis.cpp` `0x1053ddf…0x1055ddc`
(`avcall_m5a.out.txt`).

**Журнал [c]:** в `sg_v_r1`, `i`, `f8_s1` — по одному ролику `filename = data/prein/video/06_nx_controller_ship.mp4`,
`auto_start = 0`, `num_output_video_framebuffers = 6`, `demux_video_buffer_size = 4194304`, колбэк задан; 8 строк
`event_id`: READY, PLAY, PAUSE, PLAY, PAUSE, PLAY, WARNING(0x20), STOP. В `hb_f`, `hb_w` ролика нет (0 строк).

**Порядок вызовов игры [c дизассемблера, `dis_addsrc_m5a`, `dis_enable_m5a`, `dis_vp_m5a`]:** `Init` → `PostInit`
→ `AddSource` → ожидание `[obj+0x298]` → если `[obj+0x58]&1` — `SetAvSyncMode(h, 1)`; `StreamCount` → цикл
`GetStreamInfo`, `EnableStream` только для `type == 1` (видео); Start/Stop/Pause/Resume — обёртки, ставящие
`[obj+0x290]`/`[obj+0x291]` только при успехе; `IsActive` используется как `IsActive(h) && [obj+0x290]`
(`0x1055230`); `GetVideoDataEx` пишет в `[obj+0x228]`, затем копия в `[obj+0x1c0…0x220]` (`0x1054bbd`).

- **`35a275e97`, `fa51da4d7`, `6b79b7a00` — НЕ ДЕФЕКТ (см. таблицу).** Стенд S3 (модель наших
  `dd73d04d:src/libs/avPlayer.cpp:2009-2061, 2145-2148, 886-891` и upstream после цепочки) на порядке игры: события
  одинаковы, обёртка игры над `IsActive` одинакова; различие только «сырого» `IsActive` до Start (у нас 0, upstream 1),
  которое игра маскирует своим флагом. Гипотеза [I], не проверено: в нашем `Jump` → `StartImpl` `stopped = true` на
  время перезапуска (`dd73d04d:src/libs/avPlayer.cpp:797-800`) — если игра опрашивает `IsActive` с другого потока во
  время `JumpToTime`, обёртка вернёт 0 (upstream в это время — `Ready` ⇒ 1). Условие проверки — поток вызова
  `0x1055230` против `0x1055037`; к исходу коммитов не относится.
- **`d792dfa88` — паркуется:** условие в таблице.
- **`12ff57160` — НЕ ДЕФЕКТ [c]:** единственный вызов `SetAvSyncMode` идёт после успешного `AddSource`.
- **`a6f4e8e7f` (T298) — паркуется:** наш возврат буфера с задержкой 4 кадров (:963-967) не даёт неверного ответа;
  возможное следствие — декодер без свободного буфера и повтор кадра [U]. Условие: счётчик «`GetVideoDataEx` вернул 0
  при живом потоке и пустой очереди кадров из-за нехватки буфера» > 0 на ролике.
- **`25f269952` (T059) — паркуется:** наша `aspect_ratio` = ш/в × SAR (:1408-1417), upstream — только SAR; что
  означает поле `aspectRatio` SDK — [I]; игра в пределах модуля VideoPlayerOrbis поле не читает [c] (`dis_vp_m5a`),
  вне модуля — [I].

## T023 — agc `GetAvailableSizeDW` (`49b2eedd1`)

**Код [c]:** наш `dd73d04d:src/libs/agc.cpp:267-286` — 0 при нулевом курсоре или `cursor_down <= cursor_up`, потолок
`UINT32_MAX` со строкой `suspiciously large`; upstream — знаковое расстояние `>> 2` в `uint64`, без нуля и потолка.
Стенд S1 (`stands_m5a.out.txt`): решение `ReserveDW` «звать обработчик» различается только в классах `up = 0` (90),
`down = 0` (45), `down < up` (105); при ненулевых курсорах и `down > up` — тождественно (потолок не меняет решения,
т. к. `num_dw` — `uint32`).

**Исполнение:** путь `ReserveDW` исполняется (HLE `Agc*` пишут через `AllocateDW`, F26a `docs/track-f/f26a.md` §2
п. 7) [c]; различающее состояние не показано: в 5 логах строк `suspiciously large`, `exhausted and has no grow`,
`grow callback failed`, `did not provide enough`, `AllocateDW failed` — 0, сигнатур Б25 (`There are too many
objects/batches`, `command_buffer_writer.ppr.cpp`, `pc=0x00000009004a020e`) — 0 (`scan_*_m5a.out.txt`). Буферы кадра
игры (5 очередей × 3, 7/7/4/4/6 МиБ) создаются `0x49ff00` с `+0x10 = начало`, `+0x18 = конец` и сбрасываются в
(начало, конец) на каждом Begin (`0x4a55f0`) [c F26a] ⇒ на этих буферах нулевых курсоров нет, `down < up` возможно
только после переполнения, где обработчик игры — assert без роста (Б25 `ТУПИК`). Прочие объекты `CommandBuffer` гостя
— [U].

**Паркуется до:** строки ручки измерения F26a §«справка» (строка в `ReserveDW` перед вызовом обработчика гостя с
`cursor_up`, `cursor_down`, `reserved_dw`) с `cursor_down < cursor_up` или нулевым курсором, либо строки assert Б25.
Враждебно: в различающем состоянии наш ответ (позвать обработчик ⇒ assert) — «падать сразу», upstream — запись за
`cursor_down` в область данных; ни один не «верен», связь с Б25 не показана.

## T031 — guestPrintf, отрицательная динамическая точность (`bab1c3614`)

**Дефект кода [c]:** `dd73d04d:src/libs/guestPrintf.cpp:528-530` — `precision = prec > 0 ? prec : 0` при уже поднятом
`FLAGS_PRECISION` (:523); `%.*s` с `-1` печатает пустую строку. C11 7.21.6.1p5: отрицательная точность — «как если бы
опущена». Стенд S2: наш `[]`, стандарт `[abcdef]`, msvcrt `_snprintf` `[abcdef]`; при `prec ≥ 0` совпадают.

**Достижимость:** HLE `guestPrintf` вызывают `LibC::libc_printf` `hcuQgD53UxM`, `LibC::puts` `YQ0navp+YIc`,
`LibcInternal::vsnprintf` (зарегистрирован под `libc` `Q2V+iqvjgC0`), `LibcInternal::vprintf` `GMpvxPFW924`,
`LibcInternal::snprintf` `eLdDw6l0-bU` (`dd73d04d:src/libs/libC.cpp:819, 846, 870-872`). Импорт eboot — из `libc_v1`
/`libc_v1.1` [c]; по разрешению `dd73d04d:src/loader/runtimeLinker.cpp:1700-1724` точное имя
`<nid>[libc_v1][libc_v1.1]` есть в HLE для printf/puts/vsnprintf ⇒ наши; `snprintf` в HLE только под `LibcInternal`
⇒ импорт eboot из `libc` разрешается в `libc.prx` (гостевой код; строки `PS5 NID fallback` для него нет [c лога]).
`libSceNpCppWebApi.prx` импортирует `snprintf`/`printf` из `libSceLibcInternal` ⇒ наши. Мест вызова в eboot [c
`fmt_m5a.out.txt`]: printf 762, vsnprintf 24 (22 обёртки; логгер `0x27e3d0` — 1 241 место), puts 48; мест с
литеральным `%`-форматом в регистре аргумента 2 331 (из них 215 — `snprintf` из `libc.prx`, не наш), с `.*` — 0. Во всём `eboot.elf`/`eboot.bin`, `libc.prx`, `libSceNpCppWebApi.prx`
байтовых совпадений `%[флаги][ширина].*` вне машинного кода — 0. В 5 логах подстрока `%.*` — 0.

**Исход — НЕ ДЕФЕКТ для ASTRO BOT:** путь `%.*` у игры недостижим по литералам [c]; остаток — формат, собранный во
время работы или взятый из файла данных, — [I], отрицательная точность — [U]. Дефект кода вне игры показан [c]
(стенд S2); как правка «по стандарту» он может идти без критерия игры, но не под (B).

## Файлы и sha256

Папка `docs/track-m/m5a/hle1/`:

| файл | sha256 |
|---|---|
| `imp_m5a.out.txt` | `ac712dde4ad79fa0d10406aab344c9b1e27bf9a913047d1a656bdcd1609c145e` |
| `scan_sg_v_r1_m5a.out.txt` | `ce14febee563cfce0414c5ecbf3d94fa220defcbfae55f00b7f4015be46cfc10` |
| `scan_m3_m5a.out.txt` (`hb_f`, `i`, `hb_w`) | `a8dac9289d59dd9f698d830144030b44de9f229c16df3cae814dcbcf9ebf28e1` |
| `scan_f8_s1_m5a.out.txt` | `0d442970deeebd39e0a36c6ac976de55215f8371e2af56a1a74706460f3f6147` |
| `avtrace_f8_s1_m5a.out.txt` | `ef7cc9045c1876a06d0c8398fa11dca64976c0440f1e31fdd72e07142e3e8f9d` |
| `avcall_m5a.out.txt` | `3e1a50a37f3f11c45cf7587af48289a85b7da7204c7552c1a65185bdaa21c77f` |
| `fmt_m5a.out.txt` | `510d9c59894ccf766e8613af329930a6d445cb3a75f40ec7a91bdba80b0f0795` |
| `stands_m5a.out.txt` (`ALL OK`) | `03ef96cddbd9cc32ab1bcf82022bc5d9bf7a92ad875fb0706a4d90b0549cac39` |
| `dis_addsrc_m5a.out.txt` | `35c1b4adcec1410c43982f7a8771db170d47da1f231c13f29ece35a77a10f38f` |
| `dis_enable_m5a.out.txt` | `b68081fbbbbfe7ab5eb3b2bedd521cfa1a25361ea496ff5566521e995b3ff218` |
| `dis_enable2_m5a.out.txt` | `c09a8d0a1e30dbb7cd430541da94cc47175069ab56941f252b56f9ea66f588de` |
| `dis_getvideo_m5a.out.txt` | `81b575c4954c16ca74dca4229857457cfca42ddb0edbf5ae57dbec43e04deb5d` |
| `dis_after_m5a.out.txt` | `f98da04ac8907a6b29c03c6110249a9a53fd55c5a1d3d426e0c48f8e6c8d3f37` |
| `dis_vp_m5a.out.txt` | `eb34e0401eb372990255bb67406d9acbc9820037a26cfe9ed3cb687a37d13094` |
| `ao2fn_m5a.out.txt` | `66ba44ac040a5b3d0570f3b3a7d831501bef0ddeaa2a272bd16c3cb31581cb54` |
| `dis_ao2_create_m5a.out.txt` | `eb287a35d816aa78fbbd395cfc7f156c690f12ba940fbd12781f564b2640d3a9` |
| `dis_ao2_create2_m5a.out.txt` | `8163fe740bbf6c9e84d42fe4a5fa05e067287fad551901fd2be042bdb785e0be` |
| `dis_ao2_setattr_m5a.out.txt` | `dc1f79acbe77b137767f36f173a0e18be7441e6faa2e36da18593e9789c37119` |
| `dis_ao2_setattr2_m5a.out.txt` | `90a63a450c062b1a9753dc0432bdc4280a4e707bb9b765be636744ddcc737d5f` |
| `dis_ao2_setattr3_m5a.out.txt` | `33f3ad1ed4ec5c578d86917153fd4cde6212ecddade1463c955f41b7654a918b` |

Скрипты: `imp_m5a.py` (`aceb3bbc…`), `scan_m5a.py` (`09262868…`), `avtrace_m5a.py` (`8c0e8c88…`), `avcall_m5a.py`
(`fa8365f1…`), `fmt_m5a.py` (`65b5808a…`), `stands_m5a.py` (`026d045c…`). Двоичные входы: `eboot.bin` sha256
`3b510079…` (`imp_m5a.out.txt`), `eboot.elf` — файл F26a (`C:/kyty/f287/f26a/eboot.elf`), `plt.tsv` — KytyPS5
`docs/track-f/f26a/plt.tsv`.
