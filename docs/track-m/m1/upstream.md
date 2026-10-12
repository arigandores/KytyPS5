# M1a (трек M, `HPP-835`): опись отставания от upstream `6a2987a7..origin/main` `dad900c6`

Исполнитель — Emu Engineer, 2026-10-12 (UTC). Правило класса — `ROADMAP.md` п. 752(в) (= п. 633(в) + (В′)); обязательные члены — п. 752(г)(1)–(7).
Upstream: `origin` = `KytyPS5/KytyPS5`, `origin/main` `dad900c6`, база (merge-base) `6a2987a7`; 564 коммита без слияний, 376 файлов. Основания —
на нашем `main` `b3dc9c67` (текущая вершина `068d7224` отличается от `b3dc9c67` только `docs/ROADMAP.md`, п. 752). Ни один из 564 коммитов
не перенесён к нам раньше (`git cherry b3dc9c67 origin/main 6a2987a7` — 564 из 564 `+`; совпадений заголовков с нашими коммитами — 0).
Игра не запускалась, замок не брался, код `main` не менялся, сборок не было. Пометки: [c] — проверено кодом или данными, [I] — вывод,
[U] — неизвестно; утверждения upstream о проверке («fixes …», «tested») для нас [I].

Файлы звена: `upstream.tsv` (машинная таблица `sha`, `тема`, `класс`, `файлы`), `upstream_detail.tsv` (все поля строки: суть, основание,
якорь и +1, судьба нашей правки, довод по ASTRO BOT, уверенность, подпись трансляции, задетые наши ханки ручек), `check_m1a.py` (проверка
покрытия, классов и якорей — печатает `564 of 564` и `ALL OK`), приложения `m883.md` (член (5)) и `tests.md` (член (6)), свидетельства
`evidence/` (`ophist.tsv`, `overlap.tsv`, `knobs.md`), скрипты `tools/`.

## 0. Итог

| класс | смысл (п. 752(в)) | тем | коммитов | из них тем c / I / U |
|---|---|---|---|---|
| А | у нас нет, корректность ASTRO BOT — кандидат на перенос | 28 | 40 | 4 / 12 / 12 |
| Б | у нас сделано и проверено — не брать | 9 | 10 | 8 / 1 / 0 |
| В | пересекается с нашим кодом иначе — решение по данным M1c | 35 | 58 | 9 / 20 / 6 |
| В′ | upstream лучше — только со свидетельством у нас | 0 | 0 | 0 / 0 / 0 |
| Г | вне цели — не брать | 186 | 375 | 89 / 68 / 29 |
| Д | только скорость — справка, перенос только по A/B M3 | 54 | 81 | 16 / 37 / 1 |
| всего | | 312 | 564 | |

Уверенность темы — худшая из её строк (U > I > c). Тем В′ — 0: проверяемого у нас свидетельства, что upstream-вариант лучше нашего, нет ни
для одной темы (по правилу — тогда Б или В).

**Главное для M1c (прочтение исполнителя, не решение):**

1. Сильнейшие кандидаты А с [c] по коду и данным игры: `T233` legacy MAD (`d8be245c2`: у нас `V_MAD_F32`/`V_MAC_F32`/`V_MADMK`/`V_MADAK` —
   слитный `Fma`; игра исполняет `V_MAD_F32` 642 242 раза в 5 540 программах и `V_MAC_F32` 730 734 раза в 5 532 из 5 698), `T234`
   `DS_MIN/MAX_F32` (`e85279ea7`: в коде игры поле data1 = регистр адреса — компилятор игры считает инструкцию двухоперандной, у нас
   сравнение идёт с data1), `T265` ID файлов AMPR (`e43aadf75`: 31-битный FNV-1a, 5 пар путей пакета ASTRO BOT с равным хэшем), `T272`
   состояние курков (`3c62359e0`: игра ставит эффекты курков, у нас `scePadGetTriggerEffectState` всегда 0). Видимое следствие ни одной
   из них у нас не показано — критерий «ИСПРАВЛЕНО» до кода (п. 633(г)) требует воспроизведения.
2. Темы транслятора А (`T032`, `T113`, `T200`, `T203`, `T233`, `T234`, `T257`, `T306`) меняют подпись трансляции — цена холодный вход и прогрев
   (п. 418(в)); `T257` (ветвление всей волной) стоит на `ConditionRef` из #883 и меняет все шейдеры.
3. Переход upstream на SDL3 (`T093`, `f68c77d78`) — основа почти всех поздних правок звука, ввода и окна upstream; он переписывает места
   трёх отгруженных правок (Ф8 `KYTY_FIX_F8`, Б24 `KYTY_FIX_B24`, Ф24 `KYTY_FIX_F24`). Перенос любой правки звука/ввода upstream после
   2026-09-23 — ручной.
4. #883 (`T138`) — класс В по частям; маска привязки цвета (р1) у нас — Б (условия «формат слота ≠ 0» у нас нет — механизма потери травы
   нет); подробно — §8 и `m883.md`.
5. Наш код в областях кэша текстур, рендера и материализации переписан сильно (наш `textureCache.cpp` — 6 620 строк против 2 016 у
   upstream): почти любой перенос оттуда — ручная интеграция, не cherry-pick.

## 1. Метод

1. Опись коммитов (`tools/m1a_prep.py`): заголовки, файлы, признаки «трогает файл с нашей ручкой», «трогает набор подписи трансляции»
   (набор — `src/graphics/shader/**/*.{cpp,h,inc}` + `shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`, `imageInfo.h`:
   `b3dc9c67:CMakeLists.txt:156`), путь, которого у нас нет.
2. Корзины по путям (`tools/bucket_m1a.py`, 12 корзин) — разбор девятью помощниками-разборщиками по одним правилам (`tools/agent_rules.md`):
   каждая строка — тема, класс, суть, основание с якорем и +1, судьба нашей правки, довод по ASTRO BOT, уверенность. Сводка и проверки —
   исполнитель: покрытие 564 из 564, один класс на тему, все 224 якоря `b3dc9c67:<путь>:<строка>` сверены с текстом строки и строки +1
   (`check_m1a.py`), выборочная сверка сильнейших А по коду.
3. Свидетельства отношения к ASTRO BOT: (а) `evidence/ophist.tsv` — гистограмма опкодов всех 5 698 уникальных шейдерных программ
   `eboot.bin` (обход F23a `gcn_f23a.walk`; `tools/ophist_m1a.py`; опкода нет в таблице — игра его не исполняет [c]; оговорка: поле op MUBUF
   взято 7 битами, проверка помощника с битом 25 — опкодов 0x80–0xff в игре нет, выводы не меняются; программы вне `eboot.bin` — 96 SWAPPC
   и пр. — гистограмма не видит); (б) импорты NID `eboot.bin` и `sce_module/*.prx` (таблицы `LIB_FUNC` нашего кода); (в) логи установленного
   FS15 (`log_fs15_v`, `log_fs15_z`), фильтр по строкам; (г) реестр трека F `docs/track-f/register.md`; (д) `evidence/overlap.tsv` — место
   правки upstream против наших ханков (координаты базы `6a2987a7`, допуск 3 строки, `tools/overlap_m1a.py`).
4. Прочтение класса Г исполнителем: кроме лаунчера, CI, доков и сборок Linux/macOS, в Г — правки путей, которых ASTRO BOT не исполняет,
   только со свидетельством (опкод 0 в `ophist`, NID не импортируется, платформа не Windows); без свидетельства — Г с уверенностью U (список
   для M1b — §5). Чистые рефакторинги без изменения ответа — Г или Д (если заявлена скорость).

## 2. Класс А — кандидаты на перенос (28 тем)

| № | ключ | коммиты | суть | довод по ASTRO BOT | основание | подп. | ув. |
|---|---|---|---|---|---|---|---|
| T023 | `sys-agc-cb-capacity` | `49b2eedd` | AGC CommandBuffer: расчёт свободного места со знаком: GetAvailableSizeDW считает знаковое расстояние курсоров >>2 и отдаёт 64 бита (без нуля при down<=up и без потолка UINT32_MAX). | игра пишет DCB через HLE Agc* (67 импортов Gen5) — путь ReserveDW исполняется [c]; ответ отличается только при cursor_down<=cursor_up или >2^32 DW; в log_fs15_v строк «suspiciously large»/«exhausted» 0; связь с Б25 (гостевой assert, ТУПИК) не показана | `b3dc9c67:src/libs/agc.cpp:267` | нет | U |
| T031 | `sys-printf-negprec` | `bab1c361` | guestPrintf: отрицательная динамическая точность: Отрицательная динамическая точность (%.*s) трактуется как отсутствующая, а не 0. | игра импортирует LibcInternal::snprintf (eLdDw6l0-bU), он идёт через guestPrintf [c]; передаёт ли игра отрицательную точность — [U]; правка по стандарту C | `b3dc9c67:src/libs/guestPrintf.cpp:530` | нет | U |
| T032 | `be-fmtstore` | `c66d977c` `a6248c7c` `81f31263` `de9c15fa` | Кодирование форматных буферных записей BUFFER_STORE_FORMAT (SNORM/UNORM/FLOAT16/SCALED, упакованные): FormattedStore через PrepareFormattedMemory; SNORM16-компоненты кодируются packSnorm2x16 вместо записи сырых бит float / Форматная запись FLOAT16: packHalf2x16 из F32 вместо сырых бит / Кодирование UNORM (clamp, *max, RTE) и упакованных форматов (bitfieldInsert); запись всех компонент формата с нулями для недостающих VGPR … | MUBUF:4..7 (BUFFER_STORE_FORMAT_X..XYZW) = 8+2+10+2 инстр. в 6+2+8+2 программах eboot [c]; у нас 8/16-бит компоненты пишутся сырыми битами без преобразования формата (дефект кода [c]); формат V# этих записей в игре [U] | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp:1773` | да | I |
| T055 | `av-avplayer-state` | `35a275e9` `6b79b7a0` `fa51da4d` `12ff5716` `d792dfa8` | AvPlayer: состояния, события, пауза/переход, режим синхронизации: AvPlayer: событие STATE_STOP по исчерпанию потока (не только по AvPlayerStop); события перенесены в Source / AvPlayer: состояние Ready/Playing/Stopped вместо флага stopped; AvPlayerIsActive истинна до Start и без источника / AvPlayer: событие STOP при Stop только из Playing; убрано ожидание конца потока из 35a275e97 (правка предыдущей) … | ASTRO BOT зовёт AvPlayer (17 из 28 импортов [c NID]; log_fs15_v: ролик data/prein/video/06_nx_controller_ship.mp4, колбэк событий задан, события READY,PLAY,PAUSE,PLAY,PAUSE,PLAY,WARNING(jump),STOP); дефекта у нас не показано, строк реестра по AvPlayer нет; AvPlayerSetAvSyncMode импортирована, вызывает ли её игра до AddSource — [U] (PRINT_NAME выключен) | `b3dc9c67:src/libs/avPlayer.cpp:1817` | нет | I |
| T059 | `av-avplayer-aspect` | `25f26995` | AvPlayer: соотношение сторон видео: AvPlayer: aspect_ratio в GetStreamInfo/GetVideoDataEx = только SAR потока (было ширина/высота × SAR) | игра зовёт AvPlayerGetStreamInfo и AvPlayerGetVideoDataEx [c NID, ролик в log_fs15_v]; использует ли она aspect_ratio — [U] | `b3dc9c67:src/libs/avPlayer.cpp:1408` | нет | U |
| T109 | `prs-depth-clamp` | `2aaf0c9b` | Ограничение глубины после polygon offset: Во всех графических пайплайнах depthClampEnable = VK_TRUE (DB ограничивает глубину диапазоном вьюпорта после смещения); depthClamp обязателен для устройства. | Путь исполняется ASTRO на каждом графическом пайплайне (CreatePipelineInternal); у нас depthClampEnable не ставится (строки 535-543) — глубина вне [minDepth, maxDepth] при отключённом отсечении (clip_ext) или после polygon offset не ограничивается, как на железе; видимое следствие у ASTRO (тени, сравнение глубины D32 — Ф19) — [U] | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/shaders.cpp:542` | нет | I |
| T113 | `dec-glc-coherent` | `dc9280d7` | GLC/DLC буферов как Volatile/Coherent: GLC/DLC буферных загрузок и записей → MemoryAccess Volatile; буферы при когерентном доступе — DecorationCoherent | игра исполняет: 1 buffer_load_dword glc=1 dlc=1 (программа 03d8402a8c5446ce, pc 7, вне цикла), 1 buffer_store_dword glc (d97f248195e22298), 1 atomic cmpswap glc [c проба eboot]; у нас glc читается, но Volatile/Coherent в recompiler нет нигде; видимое следствие [U] | `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/MemoryOps.cpp:265` | да | U |
| T125 | `av-audioout2-mix` | `313b60e9` `c86c8b4d` | AudioOut2: копия PCM и смешение объектных портов: AudioOut2: PCM порта копируется в момент SetAttributes (раньше хранился указатель до Push); основа для смешения объектов / AudioOut2: объектные порты (0x100) смешиваются в стерео-вывод контекста, применяются атрибуты GAIN/AMBISONICS, единый замок состояния | ASTRO BOT создаёт объектные порты AudioOut2 (log_fs15_v: port_type 256 — 18 записей при разреженном логе «первые 16 и каждый 600-й»); у нас объектный порт без audio handle — его PCM никуда не выводится [c код]; слышимость пропажи — [I] | `b3dc9c67:src/libs/libAudio2.cpp:704` | нет | I |
| T133 | `img-1d2d-alias` | `f53f0ca4` | Алиасы 1D/2D текстур с отрисованным содержимым: SameBacking больше не сводит образы разных типов при экстенте 1×1×1; прямое копирование только при совместимых типах (1D↔2D через буфер); ExpandImage при смене… | Возможная связь со строкой Б34 (ТУПИК, register:§128): источник img4 — образ 1×1 из байт ГП (F47i: «img4:bytes: source unmeasured (gpu_buffer_bytes)»); наше исключение «тип может отличаться при 1×1×1» (строка 297) — ровно условие правки; исполняет ли ASTRO смену типа 1D/2D на 1×1 — [U] | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:297` | нет | U |
| T141 | `sys-amm-auto-recycle` | `34a3eb6b` | AMM: возврат автоматической подложки по физическому владению: Автоматическая подложка AMM выделяется и возвращается через физическое владение (переиспользование после unmap). | игра импортирует AprCommandBufferMapBegin/MapDirectBegin/MapEnd [c] — путь MapAuto (libAmpr.cpp:1265); рост прямой памяти при повторных загрузках — [I] | `b3dc9c67:src/libs/libAmpr.cpp:1231` | нет | I |
| T159 | `sys-ampr-waits` | `5bf9218b` `c045f089` `da9b38af` `5a880808` | AMPR: асинхронный исполнитель APR, WaitOnAddress/WaitOnCounter/WriteCounter: Команды буфера AMPR в одной последовательности по порядку добавления (variant); предпосылка c045f0890. / APR исполняется очередью по приоритетам в отдельном потоке; WaitOnAddress становится настоящим ожиданием без блокировки других приоритетов. / Буфер подкачки чтения файла APR переиспользуется в потоке исполнителя (thread_local). … | игра импортирует CommandBufferWaitOnAddress, SubmitCommandBuffer*, WaitCommandBuffer [c]; ожидание игнорируется у нас — порядок чтений против записи CPU [I] | `b3dc9c67:src/libs/libAmpr.cpp:1988` | нет | I |
| T188 | `img-gpu-alias-write` | `ebe401d0` | Запись GPU в буфер и инвалидация перекрытых образов: InvalidateMemoryFromGPU помечает образ изменённым буфером только при совпадении базового адреса записи, а не при любом перекрытии. | Путь, которым GPU-записи буфера доходят до кэшированных образов: связан с Б34 (ТУПИК, register:§128: источник img4 — «байты ГП 1×1», не измерен) и с Б42 (FIXED, register:§33: вход PS держал устаревшую память); направление эффекта не известно — правка может и скрыть запись по смещению внутри образа (риск регрессии); условие у ASTRO [U] | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3400` | нет | U |
| T200 | `dec-vscnt` | `f58014ff` | S_WAITCNT_VSCNT как завершение записей волны: S_WAITCNT_VSCNT null, 0 → OpControlBarrier(Subgroup, Device, Release): записи волны видимы до последующей публикации | игра исполняет s_waitcnt_vscnt null, 0 — 10 инструкций в 9 программах (в т.ч. 77076965e0344358) [c проба eboot]; у нас SOPK 0x17 → S_WAITCNT → EmitWaitcnt = EmitVoid (spirvEmitterInstructions.h:151) — порядка записей нет; следствие гонки в игре [I] | `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/ScalarAluOps.cpp:91` | да | I |
| T203 | `dec-alignbyte` | `f18679e0` | V_ALIGNBYTE_B32: смещение по 2 битам: V_ALIGNBYTE_B32: смещение байтов = S2 & 3 (общая функция с V_ALIGNBIT) | игра исполняет VOP3:14f — 4 инструкции в 2 программах (092754e7ae8bac9a, 380bb9d636390bae — BVH-программа Ф9/Ф10), форма v_alignbyte v, 0, литерал (0x301818 / 0x3024240c), v14 [c проба eboot]; у нас (как в базе) S2 & 31 и обнуление при ≥ 8 — при v14 ≥ 4 результат отличается от железа; диапазон v14 [U] | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Integer.cpp:500` | да | I |
| T210 | `sys-mem-fixed-replace` | `46900d80` | Память: замена живого фиксированного прямого отображения без дыры: Замена живого фиксированного прямого отображения без промежутка недоступной памяти. | игра импортирует sceKernelMapDirectMemory/MapNamedDirectMemory/MapDirectMemory2 [c]; заменяет ли она живое отображение MAP_FIXED — [U]; при гонке — K1 у другого потока | — | нет | U |
| T231 | `hle-font-metrics` | `f96a14a0` `58978d15` | sceFont: метрики и растр глифов по запрошенному масштабу: sceFont: метрики глифа в масштабе em (ScaleForMappingEmToPixels) по scale_w/scale_h, растр без зажима высоты 8..128 / sceFont: растр глифов больше 128 px (буфер по размеру глифа, width_byte = ширине), предел 4096 | ASTRO BOT рисует текст через sceFont: log_fs15_v — 5 391 вызов метрик глифа, 88 поверхностей рендера, SetScalePixel от 62 до 310 px (310 ×10, 300 ×8, 250/240/160 ×8, 132 ×2); у нас высота зажата в 8..128 и масштаб берётся по высоте ascent−descent [c код]; семантика масштаба sceFont у консоли — [I]; правка нужна вместе с f96a14a0a (иначе глифы > 128 px режутся полосами) | `b3dc9c67:src/libs/libFont.cpp:802` | нет | I |
| T233 | `dec-mad-legacy` | `d8be245c` | Нефьюзный legacy MAD/MAC FP32 отдельно от FMA: V_MAC/MAD/MADMK/MADAK_F32 — нефьюзный MAD (округление после умножения, сброс денормалов); V_FMAC/FMAMK/FMAAK_F32 выделены как FMA | игра исполняет: VOP3:141 V_MAD_F32 642 242 в 5 540 программах, VOP2:1f V_MAC_F32 730 734 в 5 532, VOP2:20/21 MADMK/MADAK 58 423 / 48 625; у нас все они — FPFma32 = GLSLstd450Fma (слитно) — тот же дефект, что в базе; видимое следствие (1 ulp, сравнения, денормалы) [I]; VOP2:2b/2d (FMAC/FMAAK) у нас уже слитные — верно | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Vector.cpp:414` | да | c |
| T234 | `dec-ds-fminmax` | `e85279ea` | DS_MIN/MAX_F32: два операнда и особые значения: DS_MIN/MAX_F32 — двухоперандные (без DATA1), порядок NaN/денормалов как у железа | игра исполняет: программа 77076965e0344358 — ds_min_f32 (addr v4, data0 v2, data1 v0) и ds_max_f32 (addr v0, data0 v1, data1 v0) [c проба eboot]; у нас (как в базе) 3 источника: сравнение с data1 (у ds_max это адрес v0), а у MAX условие old > cmp (обратно и документу ISA) ⇒ значение в LDS неверно [c кода]; двухоперандная семантика — LLVM [I] | `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/MemoryOps.cpp:197` | да | c |
| T246 | `sys-eq-persistent` | `afbb322b` | Очередь событий: уровень без EV_CLEAR один раз за ожидание: Событие-уровень без EV_CLEAR/reset_func отдаётся один раз за ожидание, а не копиями до заполнения пакета. | игра ждёт события через sceKernelWaitEqueue (импорт) [c]; есть ли у неё события-уровни без EV_CLEAR — [U] | `b3dc9c67:src/kernel/eventQueue.cpp:94` | нет | U |
| T257 | `be-wavebranch` | `a8beac19` | Скалярное ветвление (EXECZ/VCCZ) решением всей волны: Решение скалярной ветки (EXECZ/VCCZ/SCC) — ballot по всей гостевой волне и в нативном режиме, т.к. тело ветки может восстановить EXEC | S_CBRANCH_EXECZ (SOPP:8) 62 009 инстр./3 972 программ, VCCZ (SOPP:6) 17 741/4 313, VCCNZ 2 161 [c]; у нас (= база) в нативной волне решение по лане; случай «тело восстанавливает EXEC» в игре [U]; правка стоит на ConditionRef (0791f921f, нет у нас); меняет все шейдеры — нужен A/B | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterProgram.cpp:143` | да | I |
| T258 | `rnd-raw-storage-alias` | `743fdc69` | Чтение сырых буферов хранения синхронизируется с образами-алиасами: NativeStorageBuffer: ObtainBuffer с признаком texel (синхронизация из образов ГП) и для неформатных читаемых буферов | путь исполняется (чтение буферов хранения в CS/PS каждый кадр); меняет ответ только при алиасе буфер/образ, у ASTRO не измерено, дефекта не наблюдалось; кандидат при данных | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:903` | нет | U |
| T265 | `sys-ampr-fileid` | `e43aadf7` | AMPR: уникальные ID разрешённых путей вместо FNV-1a: ID файла APR — счётчик под замком кэша вместо 31-битного FNV-1a пути (коллизии перезаписывали путь другого файла). | игра разрешает пути через Apr::ResolveFilepaths* (импорт) [c]; среди 158 205 путей пакета 5 пар с равным хэшем для префикса «/app0/» и 5 для «app0/» [c, скрипт]; встречаются ли обе в одном запуске — [U]; Ф7 (п. 421) касается KernelStat, не ID APR | `b3dc9c67:src/libs/libAmpr.cpp:96` | нет | c |
| T270 | `sys-sysmodule-refs` | `210d4dcd` | Sysmodule: счёт ссылок загрузки и статус выгрузки: Sysmodule считает ссылки загрузки; IsLoaded/Unload незагруженного модуля — SYSMODULE_ERROR_UNLOADED. | игра импортирует SysmoduleLoadModule/IsLoaded/UnloadModule [c]; проверяет ли IsLoaded модулей, которые не грузила, — [U] (при переносе ответ меняется) | `b3dc9c67:src/libs/libSysmodule.cpp:25` | нет | U |
| T271 | `sys-entitlement-event` | `62643c34` | SystemService: событие ENTITLEMENT_UPDATE после AppContentInitialize: После AppContentInitialize в очередь SystemService кладётся ENTITLEMENT_UPDATE (0x10000003), ReceiveEvent его отдаёт. | игра импортирует AppContentInitialize, SystemServiceReceiveEvent, GetStatus [c]; реакция игры на событие — [U] | `b3dc9c67:src/libs/libSystemService.cpp:156` | нет | U |
| T272 | `av-pad-trigger-state` | `3c62359e` | Состояние адаптивных курков (scePadGetTriggerEffectState): scePadGetTriggerEffectState отдаёт состояние курка по последнему эффекту и ходу L2/R2 (было всегда 0); тесты | игра импортирует PadGetTriggerEffectState (znaWI0gpuo8) и ставит эффекты курков (log_fs15_v: PadTriggerEffect: #1 … mask=0x01 L=3[…]); у нас ответ всегда 0; upstream: без этого в ASTRO BOT удары L2/R2 на некоторых уровнях не работают [I] | `b3dc9c67:src/libs/libPad.cpp:39` | нет | c |
| T298 | `av-avplayer-buffers` | `a6f4e8e7` | AvPlayer: возврат выходных буферов декодеру: AvPlayer: выходной буфер видео возвращается декодеру сразу (без очереди retired), декодер работает с опережением; тест | ASTRO BOT зовёт AvPlayer (17 из 28 импортов [c NID]; log_fs15_v: ролик data/prein/video/06_nx_controller_ship.mp4, колбэк событий задан, события READY,PLAY,PAUSE,PLAY,PAUSE,PLAY,WARNING(jump),STOP); дефекта у нас не показано, строк реестра по AvPlayer нет; у ASTRO BOT num_output_video_framebuffers = 6; повторы опоздавшего кадра в игре — [U] | `b3dc9c67:src/libs/avPlayer.cpp:963` | нет | U |
| T306 | `ir-texoffset` | `984cfceb` | Смещения текселей IMAGE_SAMPLE_*_O: Смещение текселя _O передаётся в выборку (ConstOffset у константы, иначе Offset), в т.ч. в косвенных таблицах; неконстантное — отказ; Sample/Gather получают EX… | ASTRO BOT исполняет image_sample_l_o (MIMG:34 — 3 инстр./1 прогр.) и image_sample_lz_o (MIMG:37 — 18/3) [c ophist]; наш путь выборки (spirvEmitterImage.cpp:781-815) смещение не передаёт вовсе — оно есть только у gather (:739-741) [c]; видимое следствие на сцене не показано [U]; при переносе проверить, что смещения в этих 4 программах константны (иначе отказ трансляции upstream) | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp:781` | да | I |
| T309 | `sys-ampr-writeaddr-size` | `41beda43` | AMPR: размер записи WriteAddress 8/12/16 вместо 0x20: Размер записи WriteAddress 8/12/16 байт по значению (и мера 4fgtGfXDrFc/C+IEj+BsAFM), вместо 0x20: в буфер 768 байт помещаются 16 пар чтение+забор. | игра импортирует CommandBufferWriteAddress (j0+3uJMxYJY) и меру 4fgtGfXDrFc [c]; если игра размечает буфер постоянными размерами SDK, у нас EBUSY и потеря забора (зависание/данные) — [I]; печати EBUSY в коде нет | `b3dc9c67:src/libs/libAmpr.cpp:2560` | нет | I |

Кандидат А — не решение о переносе: по п. 633(г) перенос идёт итерацией формы трека F с критерием «ИСПРАВЛЕНО» до кода (дефект
воспроизводится у нас), иначе перенос — справка. Темы `T159` (AMPR-очередь) и `T309` (размер записи `WriteAddress`) связаны: `41beda436`
стоит на исполнителе APR из `c045f0890`.

## 3. Класс В — пересекается с нашим кодом иначе (35 тем)

| № | ключ | коммиты | суть | довод по ASTRO BOT | основание | подп. | ув. |
|---|---|---|---|---|---|---|---|
| T005 | `ir-baryc` | `0d9e95d9` `3ba6ebae` | Барицентрики PS: centroid/sample: Пара PERSP_CENTROID получает InterpolateAtCentroid вместо пустых VGPR (до правки upstream её не заполнял) / Пара PERSP_SAMPLE получает InterpolateAtSample(gl_SampleID) | мы решили ту же задачу иначе: заполняем все 6 режимов I/J (persp и linear) барицентриками центра (shader.h:196-199 — без MSAA равны); upstream — точная интерполяция centroid, только persp; отличие только при MSAA [I] | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:1207` | да | c |
| T007 | `be-psalias` | `441367b1` `b38b7454` | Псевдонимы входов PS (общий offset SPI_PS_INPUT_CNTL) и flat при провоцирующей вершине: Входы PS с одним offset SPI_PS_INPUT_CNTL делят одну переменную SPIR-V, per_vertex распространяется на псевдонимы; rectList/shaderPixelParameter: отдельные мес… / Режим параметров PS (FirstVertex/LastVertex/Rectangle): flat-псевдоним читает провоцирующую вершину, раздельные места только для rectList; ключ PS | та же задача решена нашей правкой 33ca0bfc0 (карточки слотов сохранения ASTRO BOT: NaN-нормали) — псевдонимы к владельцу, flat читает вершину 0; путь rectList у нас = база; решить по данным (M1c) | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterModule.cpp:487` | да | I |
| T012 | `sys-fiber-ownership` | `71f52f9d` `ded69649` | Волокна: владение, перенос между потоками, малые стеки: Переписано владение волокнами; волокно с малым стеком не пишет за пределы своего стека. / Контекст волокна в нативном TLS при переносе волокна между потоками. | игра использует волокна (FiberInitialize/Run/Switch/ReturnToThread импортируются); в log_fs15_v 13 fiber init, все по 1 MiB — малых стеков нет [c]; строк FiberRun/FiberSwitch failed и repaired — 0 | `b3dc9c67:src/libs/libKernel.cpp:2774` | нет | I |
| T016 | `ir-descphi` | `af3a3f4b` `bc45aaf6` `5d1ad31c` `488c0aca` | Дескриптор из Phi равномерной ветви -> host Select: LowerDescriptorPhi: слово дескриптора из Phi двухсторонней равномерной ветви -> host SelectU32; при записях шейдера в память — отказ (HasShaderMemoryWrites) / LowerDescriptorPhi: распознаются обе руки условной ветви (одна рука — сам блок ветвления) / LowerDescriptorPhi: при параллельных Phi дескриптора и предиката использования берётся аргумент ребра, достижимого до использования … | наш LowerUniformPhi (7baab538d) делает то же для ASTRO BOT PS 0x1974d0d59ab6429f (цепочка блоков до 32, рекурсия до 8); upstream дополнительно отказывает при записях шейдера в память — у нас такой защиты нет; выбор по данным M1c | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ResourceTracking.cpp:249` | да | I |
| T018 | `img-miptail-views` | `8589731a` | Мип-хвост PS5: виды T# с уровнями сверх ресурса: Вид T# с last_level > max_mip без смены физической раскладки (TextureViewPreservesMipLayout); SameBacking требует уровней/слоёв не меньше; ExpandImage при рост… | Тот же PR 558, что f38d738ee (upstream: «ground textures in ASTRO BOT» [I]); ResolveTexture исполняется на каждом сэмплируемом T#; у нас вид усечён до max_mip; есть ли у ASTRO T# с last_level > max_mip — [U]; наш ответ на стриминг мипов иной: отложенные мипы KYTY_MIP_DEFER и MIN_LOD (e0045fe90, 706907d59) | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3014` | нет | U |
| T019 | `dec-cfg-early-return` | `fb94a819` | CFG: слияние выбора с ранним return: FindSelectionMerge: ранний return — продолжающее плечо берётся слиянием без проверки доминирования | наш ShaderCFG переписан (IsEnclosingLinearExit выше этого места, клон эпилогов, повтор CFG), на этом месте условие с Dominates = базе; все программы игры транслируются без EXIT (Б7 НЕ ДЕФЕКТ, register §61) — польза игре [U] | `b3dc9c67:src/graphics/shader/recompiler/frontend/cfg/ShaderCFG.cpp:1359` | да | I |
| T020 | `rnd-mrt-exported` | `b594f8c8` | Привязка только экспортируемых цветовых целей, слоты MRT сохраняются: Цели цвета выбираются по MRT-выходам PS (mrt_mask), слот вложения = номер цели; динамический colorWriteEnable по вложениям; RefreshShaders до выбора целей | слоты MRT у нас уже сохраняются (d844f4cb2, разреженные MRT песка), но цели выбираются по маске записи и базе (slot 0 всегда), а не по экспорту PS. Связь с п. 633(д): форк, слившийся с upstream, потерял траву Sky Garden и вернул привязку по маске записи (26d62f80) - этот коммит главный кандидат; разбор - отдельный исполнитель | `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:3014` | нет | I |
| T029 | `av-motion` | `ce629e03` `b7a1fac8` | Датчики движения пада (гироскоп, акселерометр): Акселерометр/гироскоп SDL в PadData, ориентация интегрированием гироскопа, PadSetMotionSensorState/PadResetOrientation / Гироскоп: коррекция дрейфа ориентации по акселерометру | игра читает scePadRead (xk0AcarP3V4 импортирован) и использует гироскоп: в данных ролики подсказок *_no_gyro.mp4, 06_nx_controller_ship.mp4 (корабль на гироскопе); у нас своя реализация датчиков (b9df4fd69 «Support DualSense motion sensors and real haptics») | `b3dc9c67:src/libs/controller.cpp:705` | нет | c |
| T054 | `sys-savedata-persist` | `cfbaee07` `569ec04d` | SaveData: постоянное сохранение SaveDataMemory2, раскладка по user_id, метаданные: SaveDataMemory2 на диск по умолчанию (data_num=0 => 1, иконка не отвергается, каталоги по user_id, атомарная запись .tmp под /savedataN). / Метаданные и метки времени сохранений; слоты монтирования по пути каталога (на базе cfbaee07f). | игра импортирует Setup/Get/Set/SyncSaveDataMemory2 и TransferringMount [c]; у нас та же задача решена гейтом (лог «SavePersist: off» в прогонах — детерминизм тегов); upstream — постоянная запись по умолчанию | `b3dc9c67:src/libs/libSaveData.cpp:335` | нет | I |
| T058 | `sys-tess-optional` | `a849f253` | Тесселяция по опции (по умолчанию patch-draw пропускаются): Опция --tessellation; без неё draw с kPatch пропускается (умолчание off). | выдаёт ли ASTRO BOT patch-draw — [U]; при переносе по умолчанию такие draw исчезли бы | `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:2566` | нет | I |
| T069 | `dec-ngg-launch` | `476204cd` `cf77fb43` | NGG passthrough: состояние запуска s2/s3: NGG: начальное состояние запуска вершин (s2/s3) и размер волны (GetShaderStages бит 22) в ключе / NGG passthrough: в s3 — число активных вершин (popcount начальной маски EXEC) | игра исполняет NGG passthrough VS (наш 4be0e4cf0 «Fix NGG passthrough vertex setup for procedural sky»: s2 = wave_size<<12, s3 = 1<<28); upstream пишет s3 = (1<<28)/wave_size, потом (cf77fb435) число активных вершин — варианты различаются | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:1258` | да | I |
| T079 | `rnd-storage-mip` | `90471836` `041874f6` | Число уровней storage-вида и терминальные mip-виды: IMAGE_STORE без _MIP адресует только BASE_LEVEL: вид storage в 1 уровень; уровни образа = base + view_levels; RebindImages без принудительного level_count=1 / ResolveTextureMipView: вид, адресующий последний mip, отображается на те же хранимые подуровни со сдвигом base_level вместо фатала смены раскладки | у нас своя обработка видов mip-хвоста (продление max_mip у storage, ASTRO 480x270); фатал unsupported texture mip view в 112 логов с. 144-146 (59 входивших уровней) и V Sky Garden FS15 нет; решение по данным | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3005` | нет | I |
| T093 | `prs-sdl3` | `f68c77d7` | Переход на SDL3: Замена SDL2 на SDL3: окно, ввод, геймпады, аудио, оверлей, сборка, лаунчер. | Ф24, Ф8, Б24 (FIXED, register:§124, §68) — механизмы внутри SDL2 (замок джойстиков, Uint8-счётчик подсистем); исправляет ли их SDL3 сам — [U]; ASTRO путь исполняет (ввод, звук пада) | `b3dc9c67:src/graphics/presentation/window/joyPump.cpp:238` | нет | I |
| T107 | `dec-wqm-live` | `fcf0f3b6` | S_WQM в начале PS: предикат живых лейнов: S_WQM в начале PS: сохраняет предикат живых лейнов (маска, SCC, половины EXEC/VCC) при расширении WQM | игра исполняет S_WQM (SOP1:a 8 831 в 4 161 программе, SOP1:9 103); наш S_WQM переписан (exec_before), задача «exec ? new : old» решена у нас PredicationElimination (88336284e), Б8 — НЕ ДЕФЕКТ (register §63, §111) | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Control.cpp:311` | да | c |
| T114 | `dec-bvh` | `d72a79af` `337f4320` `dbf66b7f` | BVH: исполнение пересечений лучей (MIMG 0xe6/0xe7): Пропуск compute-dispatch с BVH-инструкциями (MIMG 0xe6/0xe7) — временная заглушка RT / Исполнение BVH-пересечений PS5 (свой обход в spirvEmitterBvh) и локальные FLAT-стеки / BVH64 (MIMG 0xe7) с общим обходом; перестройка обхода BVH | игра исполняет MIMG:e6 (60 инструкций, 20 программ); у нас своя отгруженная реализация — Б1б/Ф9 (register §16), Ф10 (§47, GPU-тест-гейт по GPURT), KYTY_BVH_LOOP_CAP (§92); FLAT scratch игра не исполняет (FLAT только global c/d/f) | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Memory.cpp:709` | да | c |
| T118 | `av-audio-out-pacing` | `7855c980` `70a475ec` | Темп вывода AudioOut (каденция, часы вывода): Блокирующая запись AudioOut держит период буфера (ровная каденция), учёт заполнения очереди SDL3 / Вывод: часы OutputClock с остатком, пачка портов подаётся целиком и темпируется одним дедлайном; убран last_output_time; тесты | AudioOut2 игры идёт в AudioInternal::AudioOutOutputs → QueueSdlAudio (b3dc9c67:src/libs/libAudio2.cpp:357) — путь исполняется; мы решили темп иначе (время гостя + WSOLA) | `b3dc9c67:src/libs/audio.cpp:697` | нет | c |
| T128 | `av-avplayer-clock` | `e0b682e4` `e51f252b` | AvPlayer: часы воспроизведения и метки при петле: AvPlayer: аудио-мастер часов сдвигается после последнего аудиокадра (steady_clock); паддинг NV12 — нейтральный чёрный вместо зелёного / AvPlayer: смещение меток клипа при петле хранится отдельно (timestamp_offset), часы и выбор кадра учитывают его | часы правки ложатся на наши часы гостя (2ae7491a2: KernelGetProcessTime вместо steady_clock, видео в шаг с игрой и растянутым звуком); выбирает ли игра паддинг роликов — [U] | `b3dc9c67:src/libs/avPlayer.cpp:909` | нет | c |
| T129 | `av-dualsense-haptics` | `a22a9d93` `22ff4693` `e1be2ead` | Хаптика и динамик DualSense: Хаптика DualSense из вибро-портов AudioOut (dualSenseHaptics.cpp), тесты PadHaptics / Порты динамика пада играют на динамике DualSense; без DualSense — на основном выводе; стоп вибрации прежнего пада / Хаптика и динамик DualSense по Bluetooth (dualSenseBluetooth.cpp); тесты | игра открывает вибро-порт AudioOut2 (log_fs15_v: «AudioOut: vibration port 3 ... -> pad haptics», port_type 6) — путь исполняется; ощущение на хосте, к картинке/крэшам не относится | `b3dc9c67:src/libs/controller.cpp:382` | нет | c |
| T135 | `img-color-meta-clear` | `0f1ff37f` `190608ae` `0ec3655f` | Материализация быстрых очисток по байтам метаданных (DCC/CMASK): MaterializeDccClear расширен до CMASK (MaterializeColorClear): очистка по коду байт метаданных; CMASK одиночной выборки описан в цели (TileGetCmaskSize); снят… / После материализации очистки развёрнутые ключи публикуются записью backing (0xff) и InvalidateMemory вместо FillBuffer. / MaterializeColorClear очищает одномиповую цель, даже если кэшированный образ имеет цепочку… | Наш 1076032b1 (CMASK одиночной выборки), bed33ed0f/992055cda (DCC) — тот же класс задачи, механизм иной: upstream решает по фактическим байтам метаданных в памяти гостя, наш — по отслеживаемому состоянию; касается Ф26 и Ф5-вх ТУПИК (register:§123, §129): у upstream нет состояния «отложенная заливка», которое Ф26 теряет при ложном «устарела» | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:2258` | да | I |
| T138 | `ir-883` | `0791f921` | UFC 5 in-game (#883): Пакет: освобождение зависимостей дескрипторов, shared-exit CFG, S_LOAD, LDS-счётчик, пропуск неактивных PS, FP32 в сравнениях, border color, разрешение дескрип… | первое впечатление: ложится на наш переписанный код (ShaderCFG — 11 ханков: наши клоны эпилогов/структуризация; LowerUniformPhi; SrtWalker; pipelineCache); глубокий разбор и член п. 633(д) (трава Sky Garden в BryKytyPS5 после #883) — отдельный исполнитель | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ResourceTracking.cpp:185` | да | I |
| T147 | `img-gpumod-cpu` | `8e61798b` | IsRegionGpuModified и владение CPU: IsRegionGpuModified не считает образ GPU-изменённым, если память определённо перезаписана CPU (PPSA17168). | Наша функция — часть IsGpuCleanRange (kernel/memory.cpp) свидетеля M1 и чтения памяти специализации шейдеров; правка меняет ответ нашего пути; исполнение условия у ASTRO [U] | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3432` | нет | U |
| T153 | `prs-pcache-lock` | `6d666681` | Кэш пайплайнов без своего мьютекса: Убран m_mutex PipelineCache; сохранение под мьютексом рендера в WindowRun. | Наш кэш пайплайнов многопоточен (претрансляция, воркеры, S-pcw) — удаление мьютекса дало бы гонку [I]; ASTRO путь исполняет | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5100` | нет | I |
| T156 | `rnd-blend-swizzle-alpha` | `73615c31` `0bef3fc0` `96011cc5` `94e7d239` | Смешение на целях с перестановкой каналов (логическая альфа через второй источник): Если перестановка экспорта переносит альфу, SrcAlpha-смешение цели 0 берёт логическую альфу из MRT1 как второго источника (dual-source); неподдержанные сочетан… / Режим SourceAlphaOne (SrcAlpha для RGB, One для альфы) на переставленных целях; ShaderAlphaBlendSource вместо флага, факторы переписываются в Src1Alpha / SourceAlpha-перепись снимает separate_… | у нас логическая альфа после перестановки не сохраняется (кода нет); есть ли у ASTRO цели с перенесённой альфой и SrcAlpha-смешением - не измерено. Связь с п. 633(д) (тема смешения переставленных целей и трава Sky Garden) - разбор отдельным исполнителем | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/dualSrcBlend.h:3` | да | U |
| T169 | `dec-shader-identity` | `0ecd3229` | Идентичность шейдера (хэш кода): Идентичность шейдера — XXH3 кода при регистрации вместо разбора устаревшего AGC-футера (BEEB03FF) | у нас свой кэш хэша (CachedShaderHash: объявленный AGC-хэш, иначе XXH3, раз на регистрацию); от хэша зависят подписи кэша трансляции и каталоги _ShaderSeeds/replay трека S — смена идентичности требует решения по данным | `b3dc9c67:src/graphics/shader/shader.cpp:222` | да | I |
| T179 | `img-hades2` | `89792a3b` | Совместимость Hades II: адрес user data PS, заливка DWORD: Hades II: регистры SPI_SHADER_USER_DATA_ADDR PS и смещения 4:5, sceKernelGetAvailableCpumask; ClearImageFromBuffer декодирует заливку DWORD отдельно (RGBA16F —… | Часть Hades II к ASTRO не относится: NID La9uyZv4Kvw в eboot.bin нет [c]; часть заливки ложится на наш код: наш DecodePackedColorClear (992055cda) декодирует RGBA16F по двум словам, а ClearImageFromBuffer передаёт packed1 = 0 ⇒ ненулевая заливка DWORD даёт (lo, hi, 0, 0) вместо повтора слова; путь ClearImageFromBuffer ASTRO исполняет (renderCompute.cpp:304), формат и значение — [U] | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:2971` | да | U |
| T213 | `sys-gpu-descr-sync` | `57cf0868` | Синхронизация GPU-записанных зависимостей дескрипторов через кэш буферов: Зависимость дескриптора, записанная GPU, читается после синхронизации кэша буферов вместо отказа. | путь чтения значения для специализации исполняется [I]; GPU-записанные значения у ASTRO BOT — [U] | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:851` | нет | I |
| T214 | `img-spec-read` | `783d9f8d` | Чтение памяти специализации из сырого буфера: Память специализации шейдера читается из backing буферного кэша (TryReadBufferBacking) без запрета по IsRegionGpuModified; функция IsRegionGpuModified удалена. | Наш ReadShaderGuestMemory переписан (с. 73: чистая петля свидетеля, CleanBackingPage); правка меняет данные специализации шейдеров ASTRO — решение только по данным | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:830` | нет | I |
| T219 | `sys-libc-autoload` | `fdac55a5` | Загрузчик: только libc.prx автоматически, без предзагрузки соседних PRX: Автоматически грузится и стартует только libc.prx; предзагрузка соседних PRX и StartAllModules удалены. | в sce_module игры два PRX: libc.prx и libSceNpCppWebApi.prx [c]; upstream перестаёт предзагружать второй, а sceKernelLoadStartModule игра не импортирует — импорты из него остались бы заглушками [I] | `b3dc9c67:src/loader/runtimeLinker.cpp:1531` | нет | I |
| T237 | `be-maddenorm` | `77d77221` | Явный флеш денормалей в legacy MAD (выключен для теста скорости): В EmitFPMad32 закомментированы 5 явных флешей денормалей (скорость), раздельное округление mul/add сохранено | V_MAD_F32 (VOP3:141) 642 242 инстр./5 540 программ [c]; у нас V_MAD/MAC -> FPFma32 (слитное), EmitFPMad32 (d8be245c2) нет — коммит осмыслен только вместе с ним; флеш у нас — режим DenormFlushToZero (590e87d50, 014a80931); решать вместе с d8be245c2 | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/SpirvEmitter.h:18` | да | c |
| T243 | `rnd-indirect-sgpr` | `cdb64bfd` `9f83fd5f` `420bb51d` | Смещения косвенного draw в user SGPR и источник индексов: DrawIndirect через DrawIndirectMulti; индексированный косвенный draw ждёт инициатор с источником DMA (0); HLE AgcDcbDrawIndex*Indirect* кодирует бит смещения и… / Аргументы косвенного draw (вершина, экземпляр, первый индекс) пишутся в user SGPR из полей пакета; для mesh - смещения Vulkan 0 / Исправление 9f83fd5f0: смещения Vulkan 0 только для невстроенной выборки (native fetch),… | у нас аргументы читает ГП (ebe41004d), запись SGPR требует чтения аргументов ЦП - сток очереди 1,5-4 мс на draw; дефекта смещений на листах 40 SCENE_OK нет; решение по данным | `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3126` | нет | I |
| T255 | `ir-mrt-compact` | `21a1346e` | Компактные экспорты цвета через CB_SHADER_MASK: Экспорт MRT k отображается в k-й включённый в CB_SHADER_MASK слот цели (ShaderPixelExportTarget); ключ PS включает маску | та же задача разреженных MRT решена нами иначе (d844f4cb2: гостевой индекс цели сохраняется в привязках Vulkan — следы на песке, декали MRT2); отображение upstream может уронить экспорт декали, если в её маске нет младших слотов — выбор только по данным M1c | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ShaderInfoCollection.cpp:378` | да | I |
| T277 | `av-pad-port-ownership` | `b65dc122` | Владение портом пада (PadOpen/PadClose): Пад: состояние порта, повторный PadOpen → ALREADY_OPENED, PadInit обязателен, PadClose/GetHandle по состоянию; тесты | наш PadOpen на повтор отдаёт тот же хэндл 1; ASTRO BOT зовёт PadOpen дважды (user 1000, type 0) без PadClose между (log_fs15_v строки 9486 и 12517) — при правке второй вызов получит ALREADY_OPENED, а GetHandle игра не импортирует; риск регрессии, решать по данным | `b3dc9c67:src/libs/controller.cpp:1424` | нет | c |
| T304 | `img-cmp-depth-dcc` | `f28c0fcc` | DCC у цветового алиаса со сравнением глубины: Для сэмплирования со сравнением цветового (не depth-tile) образа сохраняются метаданные DCC и очистка материализуется как глубина; кодировка глубины проверяетс… | Ложится на наш Ф19 (KYTY_FIX_F19, FIXED, register:§70: нативный Dref, у ASTRO 123 738 ручных мест сравнения с видами D16/D32) и наш DCC-механизм: у нас при desc.info.IsDepth() метаданные DCC отбрасываются (строки 3104-3105); есть ли у ASTRO DCC на таких образах — [U] | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3104` | нет | U |
| T311 | `img-guestgpu-simplify` | `5b730d4d` | Упрощение GuestGpu: запись EOP без Sync: Удаляет Sync::WriteAtEndOfPipe* (CPU пишет значение EOP сразу, прерывание через TriggerEopEventAtEndOfPipe) и лог indirect buffer; ProcessDownloadImages только… | Меняет семантику синхронизации EOP для всех игр; ASTRO путь исполняет каждый кадр; у нас вокруг EOP своя работа (PriorityStall, строки Б2/Б3б) — решение только по данным | `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3540` | нет | I |
| T312 | `img-bc-alias-gc` | `dad900c6` | Запись в BC-алиасы и момент сборки мусора: BcAlias: содержимое несжатого образа, перекрывающего BC-образ, публикуется через буфер; GC кэша — на SuspendPoint вместо каждого завершённого списка команд. | BC-алиасы (запись BC-данных гостем через несжатый вид) у ASTRO не доказаны; перенос момента GC касается нашего GC (e052ff6dc, preserve_gpu) и всех игр — по данным | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:4019` | нет | U |

## 4. Класс Б — у нас сделано (9 тем)

| № | ключ | коммиты | суть | довод по ASTRO BOT | основание | подп. | ув. |
|---|---|---|---|---|---|---|---|
| T010 | `dec-ngg-fan` | `7c9148dd` | NGG GS: треугольные веера: Треугольные веера в NGG GS: центр веера в каждой подгруппе, шаг примитива 1 | у нас своя поддержка вееров GS (наш cbb5b7dbb 2026-09-12: группа [вершина 0, chunk+1, ...], kTriFan в shader.cpp:1019); использование вееров игрой [U] | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:1118` | да | c |
| T011 | `sys-json2` | `32e6a433` `eda6ba37` | Json2: числовые геттеры и итераторы массива: JsonValueGetInteger отдаёт значение и для типа UInteger. / Json2: итераторы массива Begin/End/NotEqual/Deref/Increment/Dtor (6 NID). | игра импортирует LibJson2 (46 функций в s8_imports_named); наш геттер шире: любой числовой тип конвертируется | `b3dc9c67:src/libs/libJson2.cpp:878` | нет | c |
| T014 | `dec-cdbg-nop` | `5b541375` | S_CBRANCH_CDBG* как пустая ветвь (опкод игры): Декодирует S_CBRANCH_CDBGSYS (SOPP 0x17) | ophist:SOPP:17=1 (1 инструкция, 1 программа — NGG GS игры); у нас SOPP 0x17–0x1a декодируются как S_NOP (ветвь только под отладчиком) — то же поведение | `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/ScalarAluOps.cpp:116` | да | c |
| T021 | `img-tsharp-minlod` | `f38d738e` | T# MIN_LOD через VK_EXT_image_view_min_lod: Поле MIN_LOD T# (U4.8) применяется к виду образа через VkImageViewMinLodCreateInfoEXT; расширение image_view_min_lod становится обязательным. | Тот же дефект, что наш e0045fe90 «Texture: honour the T# MIN_LOD of sampled views» (шум 4K-текстур вступления ASTRO); наш вариант режет целые уровни без расширения и сводится с отложенными мипами; для сверки M1c: наш предел minLod = level_count−1 не прибавляет base_level (upstream передаёт абсолютный LOD) | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:1952` | да | c |
| T046 | `be-dualsrc` | `64936747` | Двухисточниковое смешивание (dual-source blend): Включает dualSrcBlend; при SRC1-факторе смешивания RT0 декорирует MRT1 как Location 0 Index 1 в эмиттере; флаг в статическом ключе PS | Б35 FIXED и отгружен (register §15, ручка KYTY_FIX_DUALSRC, умолчание 1): перепись выхода модуля вне подписи трансляции; рецепт 1592, внесённый mini_giants_garden (с. 143) [c] | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/shaders.cpp:345` | да | c |
| T088 | `rnd-dispatch-indirect-gpu` | `79530b4c` | Число групп косвенного dispatch читается ГП: DISPATCH_INDIRECT: аргументы читает vkCmdDispatchIndirect из буфера ГП с барьером на eIndirectCommandRead; ЦП читает только при USE_THREAD_DIMENSIONS | та же задача решена нами (63f34bc4e - санитизация аргументов на ГП; DispatchDirect с args_addr, ЦП читает только режим thread dimensions); путь исполняется каждым кадром | `b3dc9c67:src/graphics/guest_gpu/command_processor/pm4Handlers.cpp:1360` | нет | c |
| T185 | `prs-lds-pad` | `e6cb880a` | Предел LDS вычислений и неоткрываемые геймпады: LDS вычислительного шейдера ограничивается maxComputeSharedMemorySize; геймпад, который не открылся, пропускается без фатала. | Часть геймпада — Ф24 (FIXED, register:§124); часть LDS: запрос LDS сверх предела устройства у ASTRO не наблюдался (W 0 [Vulkan][E] на 40 сценах SCENE_OK) [I] | `b3dc9c67:src/graphics/presentation/window/joyPump.cpp:351` | нет | I |
| T240 | `img-clear16` | `57c97ebd` | Декодирование 16-битных цветовых очисток: DecodePackedColorClear для R16Sfloat/R16G16Sfloat/R16Unorm/R16G16Unorm; заливка DWORD R16 требует равных половин. | У нас те же форматы декодируются (992055cda, imageInfo.h:458-473); защиты заливки DWORD с неравными половинами (R16) у нас нет — справка к 89792a3bc | `b3dc9c67:src/graphics/host_gpu/renderer/image/imageInfo.h:458` | да | c |
| T250 | `prs-title` | `7415febd` | Заголовок окна в главном потоке: Заголовок (кадры, fps) обновляет главный цикл раз в секунду; Present только считает кадры. | Тот же механизм у нас с с. 114: поток показа не ждёт главный поток ради заголовка (KYTY_TITLE_ASYNC, умолчание 1) | `b3dc9c67:src/graphics/presentation/window/window.cpp:1979` | нет | c |

## 5. Класс Д (54 тем) и Г (186 тем)

Полные строки — §10 и `upstream_detail.tsv`. Темы Г с уверенностью U (Г без свидетельства [c] — первыми на отзыв M1b «не выброшено ли нужное»):

| № | ключ | коммиты | название | почему Г / чего не хватает |
|---|---|---|---|---|
| T001 | `rnd-pm4-chain` | `79120d53` | Цепочки PM4 (бит CHAIN) без рекурсии | у нас базовый вариант (рекурсивный ProcessPm4 со стеком). Без бита CHAIN ответ тот же; бит CHAIN и пакеты ветвления у ASTRO не измерены; падения стека/зависания CP на 40 SCENE_OK нет |
| T027 | `img-stencil-assoc` | `47957faa` `d8a44124` `9860c2bb` `068d7621` | Ассоциация трафарета с образом глубины (выгрузка, очистка, диапазон) | Для PPSA30279 [I]; путь трафарета через ассоциацию (CPU/DMA-запись, очистка, сэмплирование трафарета) у ASTRO не доказан; строки реестра с симптомом трафарета нет |
| T044 | `hle-net-errno` | `57c5b206` | libnet: код errno | игра зовёт NetPoolCreate (пулы «Sample», «DataCapture» — телеметрия, log_fs15_v) и импортирует GetNetErrorAddr; errno пишется только при отказе; сеть у нас офлайн (NetCtl принудительно offline), строк по сети в реестре трека F нет |
| T060 | `rnd-rectlist-legacy` | `0ad9149c` | Прямоугольники RectListLegacy из трёх вершин через патч-лист | у нас kRectListLegacy только в auto-draw как strip из 4 вершин (Sarah), иначе фатал; фатала в 112 логов с. 144-146 (59 входивших уровней) и V Sky Garden FS15 нет. Исполняет ли ASTRO legacy-прямоугольники из 3 вершин - не измерено (счётчика типов примитивов нет); дефекта на листах 40 SCENE_OK нет |
| T068 | `be-barrier` | `f9e56ef8` | Барьер рабочей группы только в стадиях с общим выполнением | S_BARRIER (SOPP:a) 186 инстр./66 программ, стадии не разобраны; барьер Workgroup в VS/PS — ошибка валидации, а W-прогоны линии курса дают 0 [Vulkan][E] [I] |
| T072 | `be-gpubuf` | `b2a80a3a` `429d0af6` `b4d32394` `a55a2838` `5f01308b` `919c058f` `8b05b673` `3ba0e971` `33e74cab` | Буферные дескрипторы, выбранные на ГП (IndirectBuffer), вместо отказа трансляции | у нас неразрешимый на ЦП буферный дескриптор = Fail трансляции -> EXIT (ResourceTracking.cpp:169-173, :589); в свипе F48a «--- Fatal Error ---» вне стендов 0, корпус T1 EXIT 0 из 269; новые формы игра на пройденных уровнях не даёт [I] |
| T084 | `be-indimg` | `eb8a5504` `3b89e36d` `a670dc84` `843b5778` `cd066010` `ae1e9262` `71c72617` `8c813865` `4c87dbeb` | Косвенные таблицы образов/сэмплеров (indirect image tables, ключи материалов) | корпус T1: 0 косвенных выборок образов из 4 343 (register §45 Ф22); несовместимые кандидаты у нас = SpecializationFail -> EXIT, фаталов в свипе F48a 0 вне стендов [I] |
| T087 | `ir-tdesc-valid` | `ef83ba65` `5ed5fdd3` | Проверка полей T# (резервные биты) | путь исполняется ASTRO BOT (все T#: ResourceMaterialization.cpp:314, :415), но дефекта с мусорными T# у нас не зарегистрировано; риск: обнуление годного T# игры, если бит считается резервным ошибочно [U] |
| T097 | `av-audio-split` | `1275d65b` | Разделение audio.cpp на acm/audio3d/ngs2 | ACM игра зовёт (5 из 11 импортов [c NID]); изменение поведения ACM по диффу не видно [U]; основа текстовой базы всех поздних правок звука upstream |
| T099 | `dec-ngg-other` | `7d7267cc` `11001c97` `5297abb7` | NGG: волна 32, fast launch, не-амплифицирующие GS | ShaderType::Mesh у нас уже есть; fast launch у нас упал бы в EXIT (gs_vgpr_component_count != 3) — такого K1 в реестре нет ⇒ fast launch игра не использует [I] |
| T101 | `rnd-depth-feedback` | `66cc2fe2` | Обратная связь вложения глубины/стенсила на всех стадиях | у нас только PS-стадия и аспект глубины; фатал sampling a writable depth в 112 логов с. 144-146 (59 входивших уровней) и V Sky Garden FS15 нет, W 40 сцен 0 [Vulkan][E]; нужен ли путь ASTRO - не измерено |
| T130 | `prs-layered-vo` | `bec67b78` | HITMAN 3: слоистый видеовывод, шейдеры, сокеты | ASTRO: NID WkYtyOg30do (SetFlipMaster) и MBlv8YWoyOk в eboot.bin нет, один буфер видеовывода [c]; ophist:VOP1:39 (V_FFBH_U32) sdwa = 0 [c]; omod у CUBEID — Б7 НЕ ДЕФЕКТ (register:§61: 0 программ с неподдержанной инструкцией из 5 698) [c]; отсев внешних чтений буфера — [U]; NetSend/NetRecv (beRjXBn-z+o, 9wO9XrMsNhc) ASTRO импортирует, сейчас это заглушки (ло… |
| T132 | `rnd-rt-pitch` | `7b6bfdec` | Каноническая раскладка однофрагментных целей цвета | путь исполняется на каждой цели ASTRO, но для одного фрагмента блок 64 КиБ цели и текстуры по чтению кода совпадают - ответ, вероятно, тот же [I]; дефекта шага на листах 40 SCENE_OK нет |
| T134 | `img-depth-alias` | `da33a1c4` `fbf6ae40` | Алиасы глубины: раскладка массива и tile_mode | Для PPSA04264/04288 [I]; путь ASTRO не доказан |
| T146 | `img-readback-valid` | `6ee1bf9d` | Годность выгрузки образа без проверки грязных байт буфера | Меняет, когда образ выгружается в память гостя; условие «образ годен, буфер грязен» у ASTRO не доказано; строки реестра нет |
| T148 | `av-zarchive` | `4b0de1b6` | Загрузка игр из .zar | архивный путь игрой не исполняется; неархивные изменения KernelOpen/KernelStat/KernelWrite (GetInfo, проверка writable) — влияние [U] |
| T166 | `hle-shareplay` | `17100ec9` | SharePlay: состояние и сведения о соединении | игра импортирует только SharePlayTerminate — при правке её ответ без Initialize станет ошибкой; влияние [U] |
| T187 | `img-bc5-reuse` | `0d4f9933` | Повторно используемые BC5 в своей раскладке | Путь ASTRO не доказан; строки реестра нет |
| T192 | `img-volume-depth` | `8b0cc79a` | Рост глубины объёмной текстуры | Растущая 3D-текстура на том же адресе у ASTRO не доказана; строки реестра нет |
| T205 | `tst-hades` | `a5eeab98` | Тест PM4: обработчики SPI_SHADER_USER_DATA_ADDR_*_PS (к теме 89792a3bc) | регистра SPI_SHADER_USER_DATA_ADDR_LO_PS нет в нашем src [c]; тема — 89792a3bc (Hades II); класс — по той теме |
| T217 | `be-meshclip` | `39248a1f` | Clip/cull distance в меш-шейдерах | у нас такой выход = EXIT (spirvEmitterMesh.cpp:39); в игре 5 MS-программ (корпус T1), фаталов в свипе F48a 0 вне стендов [I] |
| T221 | `be-scaledtex` | `96c067d0` `07c84876` `e5689990` | Текстуры USCALED 8 бит: выборка через UNORM-хранение | у нас USCALED-форматов нет в таблице форматов текстур (только перечисление gpu_defs.h); путь конверсии принимает лишь упакованный Uint; фаталов в свипе F48a 0 [I] |
| T222 | `img-10-11-11` | `5940e623` | Цель 10-11-11 и общие преобразования цвета | Использует ли ASTRO цель k10_11_11Float — [U]; строки реестра нет |
| T223 | `img-rebind-order` | `a2f85178` | Порядок пересвязывания перекрывающихся образов | RebindImages ASTRO исполняет на каждом draw, но условие (второй дескриптор того же draw расширяет образ первого) не доказано; строки реестра нет |
| T228 | `img-2d3d-alias` | `0885f43a` | Алиасы 2D/3D текстур раздельно | Путь ASTRO не доказан; строки реестра нет |
| T235 | `hle-trophy` | `72e4989b` `fb7ff7ec` | Трофеи: состояние, уведомления, UDS | игра зовёт NpTrophy2 Create/Register и UDS PostEvent [c NID]; оверлей — вне цели, но меняются ответы RegisterContext (NOT_REGISTERED) — влияние [U] |
| T259 | `img-array-sync` | `dd754065` | Копирование массивов образа в буфер | Путь ASTRO не доказан; строки реестра нет |
| T284 | `rnd-nop-1dw` | `4c8fc53a` | NOP из одного слова и общий размер пакета | у нас AgcCbNop(1) возвращает nullptr, CP не знает 1-словного NOP; вызывает ли ASTRO AgcCbNop с размером 1 - не измерено, фатала/зависания на 40 SCENE_OK нет |
| T288 | `sys-agc-driver-dmem` | `165cd884` `9a5dd9fa` | AGC: DMEM драйвера и таблица функций при старте | игра зовёт AgcInit (импорт) [c]; читают ли её шейдеры таблицу драйвера — [U]; меняет раскладку прямой памяти гостя |

## 6. Член (3): пересечение с отгруженным

Ручки — `evidence/knobs.md` (23 строки `FIXED` реестра §129, все отгружены под (B), + трек S + трек P). Тем, трогающих файл с нашей ручкой
(без `tests/`), — 172; из них место правки upstream задевает наш ханк с ручкой (по `overlap.tsv`) — 43.

### 6.1 По ручке: какие темы задевают её место

| ручка / место | строка реестра | темы, задевающие наш ханк |
|---|---|---|
| (место вызова гейта: ResourceMaterialization.cpp) | место вызова гейта, имя ручки в ханке не названо | T081, T084, T189, T193 |
| (место вызова гейта: controller.cpp) | место вызова гейта, имя ручки в ханке не названо | T093, T162 |
| (место вызова гейта: faultManager.cpp) | место вызова гейта, имя ручки в ханке не названо | T140 |
| (место вызова гейта: pipelineCache.cpp) | место вызова гейта, имя ручки в ханке не названо | T060, T241 |
| `KYTY_FIX_B12` | Б12 | T076 |
| `KYTY_FIX_B1B` | Б1а, Б1б, Ф9 | T037 |
| `KYTY_FIX_B24` | Б24 | T029, T129, T162, T272, T277 |
| `KYTY_FIX_B26` | Б26б | T025, T204 |
| `KYTY_FIX_B4` | Б4 | T053 |
| `KYTY_FIX_B42` | Б42 | T081, T105, T122, T214, T226 |
| `KYTY_FIX_DUALSRC` | Б35 | T025, T130, T153, T186, T204, T301 |
| `KYTY_FIX_F10` | Ф10 | T037 |
| `KYTY_FIX_F19` | Ф19 | T072 |
| `KYTY_FIX_F20` | Ф20 | T153 |
| `KYTY_FIX_F24` | Ф24 | T064, T093, T129, T185, T250 |
| `KYTY_FIX_F26` | — (не отгружена: диагностика, умолчание 0) | T081, T105, T135, T226, T289 |
| `KYTY_FIX_F5CMU` | — (не отгружена: диагностика, умолчание 0) | T081, T105, T135, T226, T289, T304 |
| `KYTY_FIX_MINIMIZE` | Б37 | T094, T130, T307 |
| `KYTY_FIX_SVAL` | Ф16 | T025, T186, T301 |
| `KYTY_GAME_PATCH` | трек P | T219, T303 |
| `KYTY_PVAR` | трек P | T130, T219, T303 |
| `KYTY_S_PCW` | Б33 (трек S) | T007, T020, T046, T153, T156, T174 |
| `KYTY_S_PCW_FORCE_MS` | — (не отгружена: диагностика, умолчание 0) | T007, T020, T046, T153, T156 |
| `KYTY_S_REPLAY` | трек S (S-replay) | T007, T026, T046, T153, T156 |

Ручки без единой задетой темы: `KYTY_FIX_B9A`, `KYTY_FIX_B13`, `KYTY_FIX_F8`, `KYTY_FIX_F21`, `KYTY_FIX_F25`, `KYTY_FIX_B36`, `KYTY_FIX_F29`.

### 6.2 Что будет с нашей правкой — по темам

Для каждой темы, трогающей файл с ручкой: файлы, задетые наши ханки (`overlap.tsv`), строка «что будет с нашей правкой».

- **T002** `prs-key-l2r2` (Г): файлы — `hostInput.cpp`; задеты ханки ручек — нет.
  - hostInput.cpp (KYTY_FIX_F24): DefaultKeyboardButton, место JoyPump не задето (overlap 0/0); проверить, что KYTY_KEYS-харнессы не шлют z/c
- **T004** `av-linux-ffmpeg` (Г): файлы — `CMakeLists.txt`; задеты ханки ручек — нет.
  - CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 2 ханк(ов) upstream, ручкиных задето 0 — место не пересекается
- **T007** `be-psalias` (В): файлы — `pipelineCache.cpp`; задеты ханки ручек — pipelineCache.cpp: 1 [KYTY_S_PCW KYTY_S_PCW_FORCE_MS KYTY_S_REPLAY].
  - ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается)
  - pipelineCache.cpp [KYTY_FIX_F20,KYTY_FIX_SVAL,KYTY_S_PCW,KYTY_S_PCW_FORCE_MS,KYTY_S_REPLAY,KYTY_S_REPLAY_TEST]: ханков ручки задето 1 [KYTY_S_PCW KYTY_S_PCW_FORCE_MS KYTY_S_REPLAY], прочих наших 1; задет наш ханк S_PCW/S_REPLAY в pipelineCache.cpp — сохранить
- **T009** `sys-amdcpu-patch` (Г): файлы — `CMakeLists.txt`, `runtimeLinker.cpp`; задеты ханки ручек — нет.
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 1 ханк в LoadProgramToMemory; наши ханки с ручкой не задеты (overlap 0); при переносе конфликта нет.
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 1 ханк (условие вокруг PatchReciprocalSquareRoots); ханки ручек не задеты.
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 13 ханков в загрузке программы; ханки ручек не задеты (overlap 0); при переносе — механический конфликт с нашим runtimeLinker, ручки сохраняются.
  - CMakeLists.txt (цель LogAsyncTests Ф27/KYTY_FIX_B36): 1 ханк, ханк ручки не задет.
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 18 ханков, ханки ручек не задеты, 2 наших прочих — механический конфликт.
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 7 ханков, не задеты.
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 3 ханка, не задеты.
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 2 ханка, не задеты; CMakeLists.txt (Ф27) 2 ханка, не задеты.
- **T012** `sys-fiber-ownership` (В): файлы — `libKernel.cpp`; задеты ханки ручек — нет.
  - libKernel.cpp (KYTY_PVAR — LIB_FUNC fgxnMeTNUtY, стр. 3365): ханк ручки не задет; 24 ханка задевают 6 наших прочих (FiberTrace, починка stale RUNNING, метка DiagB32 W:fiber) — конфликт, решать по данным M1c.
  - libKernel.cpp (KYTY_PVAR, стр. 3365): ханк ручки не задет; 20 ханков задевают 7 наших прочих (FiberTrace/DiagB32) — конфликт, решать по данным.
- **T014** `dec-cdbg-nop` (Б): файлы — `ShaderDecoder.cpp`, `ShaderDecoder.h`; задеты ханки ручек — нет.
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_F10 (Ф10) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T016** `ir-descphi` (В): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 0); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
  - тесты: задет наш call-site ханк в tests/shaderCfgTests.cpp (F19/F20/S_REPLAY) — конфликт только в тестах
- **T018** `img-miptail-views` (В): файлы — `textureCache.cpp`, `descriptors.cpp`; задеты ханки ручек — нет.
  - descriptors.cpp (KYTY_FIX_B42): место ручки не задето (overlap 0 ручных, 5 прочих наших ханков ResolveTexture); textureCache.cpp (KYTY_FIX_B42; диагностика KYTY_FIX_F26/KYTY_FIX_F5CMU не отгружены): ханки SameBacking/ResolveOverlap вне мест ручек (0/0); перенос — ручной на наш переписанный ResolveTexture (строки 3014-3039)
- **T020** `rnd-mrt-exported` (В): файлы — `pipelineCache.cpp`; задеты ханки ручек — pipelineCache.cpp: 2 [KYTY_S_PCW KYTY_S_PCW_FORCE_MS].
  - pipelineCache.cpp: ручки KYTY_S_PCW, KYTY_S_REPLAY, KYTY_FIX_SVAL, KYTY_FIX_F20; по overlap.tsv ханки upstream задевают 2 наших ханка с KYTY_S_PCW (+1 прочий) - конфликт при переносе, нашу запись кэша драйвера вне m_mutex (Б33) сохранить; меняет ключ графического пайплайна (PipelineStaticParameters/хэш) - рецепты precache pipelines.bin и каталог повтора S-replay станут холодными (первый вход каждой сцены), подпись трансляции не меняется; в тест-файле задет ханк стенда KYTY_FIX_F26 (неотгружен)
- **T021** `img-tsharp-minlod` (Б): файлы — `descriptors.cpp`, `vulkanWindow.cpp`; задеты ханки ручек — нет.
  - descriptors.cpp (KYTY_FIX_B42), vulkanWindow.cpp (KYTY_FIX_B26/DUALSRC/F24/SVAL): места ручек не задеты (overlap 0 ручных); не брать — наш вариант e0045fe90 с ручкой KYTY_TSHARP_MIN_LOD
- **T025** `dec-op-unused` (Г): файлы — `graphicContext.h`, `descriptors.cpp`, `vulkanWindow.cpp`, `spirvEmitterMemory.cpp`, `ShaderDecoder.cpp`, `ShaderDecoder.h`, `Memory.cpp`, `ResourceMaterialization.cpp`; задеты ханки ручек — graphicContext.h: 1 [KYTY_FIX_DUALSRC KYTY_FIX_SVAL]; vulkanWindow.cpp: 1 [KYTY_FIX_B26 KYTY_FIX_DUALSRC].
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_F10 (Ф10) — места наших ханков с ручкой не пересекаются (overlap 0)
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_B42 (Б42), KYTY_FIX_F10 (Ф10), KYTY_FIX_F19 (Ф19), KYTY_FIX_F26 (Ф26, не отгружена), KYTY_FIX_F5CMU (Ф5, не отгружена) — места наших ханков с ручкой не пересекаются (overlap 0)
  - КОНФЛИКТ по overlap: graphicContext.h задевает наш ханк 1 [KYTY_FIX_DUALSRC KYTY_FIX_SVAL]; vulkanWindow.cpp задевает наш ханк 1 [KYTY_FIX_B26 KYTY_FIX_DUALSRC]; ручки задетых файлов: KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_DUALSRC (Б35), KYTY_FIX_F10 (Ф10), KYTY_FIX_F24 (Ф24), KYTY_FIX_SVAL (Ф16)
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_DUALSRC (Б35), KYTY_FIX_F10 (Ф10), KYTY_FIX_F24 (Ф24), KYTY_FIX_SVAL (Ф16) — места наших ханков с ручкой не пересекаются (overlap 0)
  - Б26б: upstream добавляет S_BREV_B64 и V_CMP_LE_U64 своими строками таблиц; у нас они уже есть под гейтом GateFixB26 (ShaderDecoder.cpp:338, KYTY_FIX_B26, отгружено) — при переносе конфликт, сохранить нашу правку; в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_F10 (Ф10) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T026** `dec-swappc` (Г): файлы — `pipelineCache.cpp`, `ShaderDecoder.cpp`, `ShaderDecoder.h`, `ResourceMaterialization.cpp`; задеты ханки ручек — pipelineCache.cpp: 1 [KYTY_S_REPLAY].
  - pipelineCache.cpp: upstream меняет поиск перестановки ProgramCache, где стоит наш ханк KYTY_S_REPLAY — при переносе конфликт, сохранить нашу правку; КОНФЛИКТ по overlap: pipelineCache.cpp задевает наш ханк 1 [KYTY_S_REPLAY]; ручки задетых файлов: KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_F10 (Ф10), KYTY_FIX_F19 (Ф19), KYTY_FIX_F20 (Ф20), KYTY_FIX_SVAL (Ф16), KYTY_S_PCW (Б33), KYTY_S_PCW_FORCE_MS (стенд Б33), KYTY_S_REPLAY (S-replay), KYTY_S_REPLAY_TEST (стенд S-replay)
  - pipelineCache.cpp: правка в ProgramCache рядом с нашими ханками KYTY_S_REPLAY (overlap 0), зависит от 1818aae56; в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_F10 (Ф10), KYTY_FIX_F20 (Ф20), KYTY_FIX_SVAL (Ф16), KYTY_S_PCW (Б33), KYTY_S_PCW_FORCE_MS (стенд Б33), KYTY_S_REPLAY (S-replay), KYTY_S_REPLAY_TEST (стенд S-replay) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T027** `img-stencil-assoc` (Г): файлы — `textureCache.cpp`, `textureCache.h`; задеты ханки ручек — нет.
  - textureCache.cpp (KYTY_FIX_B42; KYTY_FIX_F26/KYTY_FIX_F5CMU не отгружены): AssociateStencil вне мест ручек (overlap 0/0)
  - textureCache.cpp/.h (KYTY_FIX_B42; KYTY_FIX_F26/KYTY_FIX_F5CMU не отгружены): места ручек не задеты (overlap 0 ручных), но 19 прочих наших ханков (RefreshImage с allow_partial, FindDepthTarget, ClearImage) — перенос ручной
  - textureCache.cpp: FindDepthTarget у нас с метками Ф26 (F26DropLocked, KYTY_F26 не отгружен) рядом — места ручек не задеты (overlap 0 ручных, 7 прочих)
  - textureCache.cpp: 13 прочих наших ханков (ClearImageFromBuffer со счётчиками с. 70, FindDepthTarget), места ручек не задеты
- **T029** `av-motion` (В): файлы — `window.cpp`, `controller.cpp`, `controller.h`; задеты ханки ручек — controller.cpp: 1 [KYTY_FIX_B24]; controller.h: 1 [KYTY_FIX_B24].
  - controller.cpp: ручки Б24 KYTY_FIX_B24 (реестр §68, PadOutput) и Ф24 KYTY_FIX_F24 (реестр §124, JoyPump); overlap: 12 ханков, задет 1 наш ханк Б24 и 12 прочих (наш путь датчиков); controller.h: 2 ханка, задет 1 ханк Б24; window.cpp (Ф24): 1 ханк — событие SENSORUPDATE, у нас свой обработчик (window.cpp:774). При переносе — конфликт: сохранить PadOutput (Б24), вариант датчиков выбрать по данным
  - controller.cpp: ручки Б24 KYTY_FIX_B24 (реестр §68, PadOutput) и Ф24 KYTY_FIX_F24 (реестр §124, JoyPump); overlap: 9 ханков, задет 1 наш ханк Б24 и 3 прочих — конфликт, PadOutput (Б24) сохранить
- **T032** `be-fmtstore` (А): файлы — `spirvEmitterMemory.cpp`; задеты ханки ручек — нет.
  - spirvEmitterMemory.cpp [KYTY_FIX_B1B,KYTY_FIX_F10]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 1 [KYTY_FIX_B1B KYTY_FIX_B26 KYTY_FIX_F10 KYTY_FIX_F19], прочих наших 0 (тест ручки — сохранить наш тест)
  - spirvEmitterMemory.cpp [KYTY_FIX_B1B,KYTY_FIX_F10]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 1 [KYTY_FIX_B1B KYTY_FIX_B26 KYTY_FIX_F10 KYTY_FIX_F19], прочих наших 0 (тест ручки — сохранить наш тест); shaderCfgTests.cpp [KYTY_FIX_F19,KYTY_FIX_F20,KYTY_S_REPLAY]: ханков ручки задето 1 [KYTY_FIX_F19 KYTY_FIX_F20 KYTY_S_REPLAY], прочих наших 0 (тест ручки — сохранить наш тест)
- **T033** `av-refactor-magic-enum` (Г): файлы — `ShaderDecoder.h`, `audio.cpp`, `runtimeLinker.cpp`; задеты ханки ручек — нет.
  - audio.cpp: ручка Ф8 KYTY_FIX_F8 (реестр §68, FS7; SdlAudioAcquire/FixF8Enabled audio.cpp:292–330): 6 ханков, ручкиных 0, прочих наших 3 (строки логов); runtimeLinker.cpp (P-var/KYTY_GAME_PATCH): 8 ханков, 0 задето; ShaderDecoder.h (Б1б/Б26б/Ф10): 1 include, 0 задето — места ручек не пересекаются, конфликты только текстовые
- **T034** `sys-refactor-strings` (Г): файлы — `fileSystem.cpp`, `runtimeLinker.cpp`; задеты ханки ручек — нет.
  - fileSystem.cpp (Б4 KYTY_FIX_B4, Ф25 KYTY_FIX_F25): 3 ханка в MountPoints::ResolvePath, ханки ручек не задеты; runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 4 ханка, не задеты; tests/shaderCfgTests.cpp — 2 наших прочих. При переносе — механический конфликт, ручки сохраняются.
- **T036** `hle-refactor-runtime` (Г): файлы — `pthread.cpp`, `libKernel.cpp`; задеты ханки ручек — нет.
  - pthread.cpp (KYTY_GAME_PATCH): 1 ханк — удалён неиспользуемый sec_to_timeval, 0 задето; libKernel.cpp (KYTY_PVAR): 5 ханков — sha1_rol → std::rotl, 0 задето; места ручек не пересекаются
- **T037** `dec-refactor` (Г): файлы — `swapchain.cpp`, `vulkanWindow.cpp`, `window.cpp`, `ShaderDecoder.cpp`, `Memory.cpp`; задеты ханки ручек — Memory.cpp: 1 [KYTY_FIX_B1B KYTY_FIX_F10].
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_DUALSRC (Б35), KYTY_FIX_F10 (Ф10), KYTY_FIX_F24 (Ф24), KYTY_FIX_MINIMIZE (Б37), KYTY_FIX_SVAL (Ф16) — места наших ханков с ручкой не пересекаются (overlap 0)
  - при переносе — механический конфликт с нашим IMAGE_BVH_INTERSECT_RAY (bool) в Memory.cpp; КОНФЛИКТ по overlap: Memory.cpp задевает наш ханк 1 [KYTY_FIX_B1B KYTY_FIX_F10]; ручки задетых файлов: KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_F10 (Ф10)
- **T040** `sys-refactor-helpers` (Г): файлы — `pthread.cpp`; задеты ханки ручек — нет.
  - pthread.cpp (KYTY_GAME_PATCH — AudioSyncOff, стр. 188): 2 ханка задевают 2 наших прочих ханка, ханк ручки не задет; конфликт механический.
- **T042** `rnd-winbuild-membarrier` (Г): файлы — `regionManager.h`; задеты ханки ручек — нет.
  - regionManager.h: ручки KYTY_FIX_B12 (Б12) и KYTY_FIX_B13 (Б13); ханк upstream (заголовок include) наших ханков не задевает
- **T046** `be-dualsrc` (Б): файлы — `pipelineCache.cpp`, `vulkanWindow.cpp`; задеты ханки ручек — pipelineCache.cpp: 1 [KYTY_S_PCW KYTY_S_PCW_FORCE_MS KYTY_S_REPLAY].
  - pipelineCache.cpp [KYTY_FIX_F20,KYTY_FIX_SVAL,KYTY_S_PCW,KYTY_S_PCW_FORCE_MS,KYTY_S_REPLAY,KYTY_S_REPLAY_TEST]: ханков ручки задето 1 [KYTY_S_PCW KYTY_S_PCW_FORCE_MS KYTY_S_REPLAY], прочих наших 1; vulkanWindow.cpp [KYTY_FIX_B26,KYTY_FIX_DUALSRC,KYTY_FIX_F24,KYTY_FIX_SVAL]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); наша правка Б35 (KYTY_FIX_DUALSRC) делает то же иначе — не брать; при переносе соседних правок pipelineCache.cpp сохранить ханк S_PCW/S_REPLAY и логику dualSrcBlend vulkanWindow.cpp
- **T048** `dec-dpp8` (Г): файлы — `ShaderDecoder.cpp`, `ShaderDecoder.h`, `Memory.cpp`; задеты ханки ручек — нет.
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_F10 (Ф10) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T050** `av-ngs2-ajm` (Г): файлы — `CMakeLists.txt`, `audio.cpp`, `libAudio.cpp`; задеты ханки ручек — нет.
  - libAudio.cpp (Б9а KYTY_FIX_B9A, реестр §24; KYTY_FIX_DUALSRC): 1 ханк в AudiodecDecode, 0 задето — место не пересекается
  - audio.cpp: ручка Ф8 KYTY_FIX_F8 (реестр §68, FS7; SdlAudioAcquire/FixF8Enabled audio.cpp:292–330): 37 ханков в коде NGS2, ручкиных 0, прочих наших 2 — место Ф8 не задето
  - audio.cpp: ручка Ф8 KYTY_FIX_F8 (реестр §68, FS7; SdlAudioAcquire/FixF8Enabled audio.cpp:292–330): 15 ханков в коде NGS2, ручкиных 0, прочих наших 1 — место Ф8 не задето
  - audio.cpp: ручка Ф8 KYTY_FIX_F8 (реестр §68, FS7; SdlAudioAcquire/FixF8Enabled audio.cpp:292–330): 3 ханка в коде NGS2, 0 задето
  - CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 3 ханк(ов) upstream, ручкиных задето 0 — место не пересекается
- **T052** `av-pad-misc-stubs` (Г): файлы — `controller.cpp`, `controller.h`; задеты ханки ручек — нет.
  - controller.cpp: ручки Б24 KYTY_FIX_B24 (реестр §68, PadOutput) и Ф24 KYTY_FIX_F24 (реестр §124, JoyPump); overlap: 1 ханк (новая функция), 0 задето; controller.h: 1 строка объявления, 0 — не пересекается
- **T053** `sys-native-paths` (Г): файлы — `window.cpp`, `fileSystem.cpp`; задеты ханки ручек — fileSystem.cpp: 1 [KYTY_FIX_B4].
  - fileSystem.cpp (Б4): 1 ханк (MountPoints::Mount сразу за CloseAll) в окне нашего ханка KYTY_FIX_B4 (overlap 1) — текстовый конфликт, сохранить нашу правку Б4 в CloseAll/EmergencyShutdown; семантика не пересекается.
  - window.cpp (Ф24 KYTY_FIX_F24): 5 ханков, ханки ручки не задеты, 1 наш прочий — механический конфликт.
- **T054** `sys-savedata-persist` (В): файлы — `CMakeLists.txt`; задеты ханки ручек — нет.
  - CMakeLists.txt (цель LogAsyncTests Ф27): 2 ханка (новые тест-цели), ханк ручки не задет.
- **T060** `rnd-rectlist-legacy` (Г): файлы — `pipelineCache.cpp`; задеты ханки ручек — pipelineCache.cpp: 1 [call-site].
  - pipelineCache.cpp (ручки KYTY_S_PCW, KYTY_S_REPLAY, KYTY_FIX_SVAL, KYTY_FIX_F20): по overlap.tsv задет 1 наш ханк с вызовом гейта (call-site) у rect_list - конфликт строки, логику гейта сохранить; тест-файл tests/ShaderRecompilerComputeTests.cpp со стендами ручек; наших ханков не задевает - место не пересекается
- **T063** `bld-cmake` (Г): файлы — `CMakeLists.txt`; задеты ханки ручек — нет.
  - CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 1 ханк(ов) upstream, ручкиных задето 0 — место не пересекается
- **T064** `av-host-window-ux` (Г): файлы — `hostInput.cpp`, `window.cpp`; задеты ханки ручек — hostInput.cpp: 2 [KYTY_FIX_F24].
  - hostInput.cpp (Ф24 KYTY_FIX_F24, реестр §124): 1 ханк (список зарезервированных клавиш), 0 задето; window.cpp (Ф24): 3 ханка (GameEventKeyboard), 0 задето — не пересекается
  - hostInput.cpp: ручка Ф24 KYTY_FIX_F24 (реестр §124); overlap: 8 ханков, задеты 2 наших ханка Ф24 — ожидание событий главного потока (SDL_WaitEvent/SDL_WaitEventTimeout, hostInput.cpp:424–471). Конфликт: сохранить предел ожидания Ф24 (1 мс / 3 000 мс), таймаут курсора встроить в него; код upstream написан на SDL3 (f68c77d78 «SDL3 update», корзина gfx_present), у нас SDL2
- **T066** `rnd-storage-cube` (Г): файлы — `descriptors.cpp`; задеты ханки ручек — нет.
  - descriptors.cpp: ручка KYTY_FIX_B42 (Б42, FS3) и неотгруженные KYTY_FIX_F26/F5CMU (умолчание 0); ханки upstream наших не задевают; в тест-файле задет ханк стенда KYTY_FIX_F19 (Ф19) - при переносе теста конфликт, сохранить наш стенд
- **T067** `prs-out-res` (Г): файлы — `videoOut.cpp`; задеты ханки ручек — нет.
  - videoOut.cpp (KYTY_PVAR): VideoOutGetOutputStatus вне хуков P-var (VblankEnd, завершение флипа); overlap 0 ручных, 2 прочих
- **T069** `dec-ngg-launch` (В): файлы — `pipelineCache.cpp`; задеты ханки ручек — нет.
  - в задетых файлах ручки KYTY_FIX_F20 (Ф20), KYTY_FIX_SVAL (Ф16), KYTY_S_PCW (Б33), KYTY_S_PCW_FORCE_MS (стенд Б33), KYTY_S_REPLAY (S-replay), KYTY_S_REPLAY_TEST (стенд S-replay) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T072** `be-gpubuf` (Г): файлы — `descriptors.cpp`, `spirvEmitterMemory.cpp`, `ResourceMaterialization.cpp`, `ResourceMaterialization.h`; задеты ханки ручек — ResourceMaterialization.cpp: 1 [KYTY_FIX_F19]; ResourceMaterialization.h: 1 [KYTY_FIX_F19].
  - spirvEmitterMemory.cpp [KYTY_FIX_B1B,KYTY_FIX_F10]: ханков ручки задето 0, прочих наших 3 (место ручки не пересекается)
  - spirvEmitterMemory.cpp [KYTY_FIX_B1B,KYTY_FIX_F10]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); ResourceMaterialization.cpp [KYTY_FIX_F19]: ханков ручки задето 1 [KYTY_FIX_F19], прочих наших 3; ResourceMaterialization.h [KYTY_FIX_F19]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается); shaderCfgTests.cpp [KYTY_FIX_F19,KYTY_FIX_F20,KYTY_S_REPLAY]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается); конфликт с ханком Ф19 (KYTY_FIX_F19) в ResourceMaterialization.cpp — сохранить нашу правку Ф19
  - spirvEmitterMemory.cpp [KYTY_FIX_B1B,KYTY_FIX_F10]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается); shaderCfgTests.cpp [KYTY_FIX_F19,KYTY_FIX_F20,KYTY_S_REPLAY]: ханков ручки задето 0, прочих наших 3 (место ручки не пересекается)
  - spirvEmitterMemory.cpp [KYTY_FIX_B1B,KYTY_FIX_F10]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается)
  - descriptors.cpp [KYTY_FIX_B42,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается); spirvEmitterMemory.cpp [KYTY_FIX_B1B,KYTY_FIX_F10]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); ResourceMaterialization.cpp [KYTY_FIX_F19]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается); ResourceMaterialization.h [KYTY_FIX_F19]: ханков ручки задето 1 [KYTY_FIX_F19], прочих наших 0; ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается); конфликт с ханком Ф19 в ResourceMaterialization.h — сохранить нашу правку
  - descriptors.cpp [KYTY_FIX_B42,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается); spirvEmitterMemory.cpp [KYTY_FIX_B1B,KYTY_FIX_F10]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); ResourceMaterialization.cpp [KYTY_FIX_F19]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается); ResourceMaterialization.h [KYTY_FIX_F19]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается)
  - shaderCfgTests.cpp [KYTY_FIX_F19,KYTY_FIX_F20,KYTY_S_REPLAY]: ханков ручки задето 0, прочих наших 3 (место ручки не пересекается)
- **T074** `rnd-depth-meta-bits` (Г): файлы — `descriptors.cpp`; задеты ханки ручек — нет.
  - descriptors.cpp: ручка KYTY_FIX_B42 (Б42, FS3) и неотгруженные KYTY_FIX_F26/F5CMU (умолчание 0); ханки upstream наших не задевают
- **T075** `ir-perf-remap` (Д): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 0); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T076** `rnd-logs-quiet` (Г): файлы — `renderContext.cpp`; задеты ханки ручек — renderContext.cpp: 1 [KYTY_FIX_B12].
  - renderContext.cpp: ручка KYTY_FIX_B12 (Б12); по overlap.tsv ханк задевает наш ханк с KYTY_FIX_B12 в PrepareBda - конфликт строки, нашу правку Б12 сохранить
- **T079** `rnd-storage-mip` (В): файлы — `descriptors.cpp`; задеты ханки ручек — нет.
  - descriptors.cpp: ручка KYTY_FIX_B42 (Б42, FS3) и неотгруженные KYTY_FIX_F26/F5CMU (умолчание 0); по overlap.tsv ханки upstream задевают 4 наших прочих ханка (без ручки) - ложится на переписанный нами ResolveTexture
  - descriptors.cpp: ручка KYTY_FIX_B42 (Б42, FS3) и неотгруженные KYTY_FIX_F26/F5CMU (умолчание 0); ханки upstream задевают 3 наших прочих ханка - ложится на переписанный ResolveTexture
- **T081** `ir-refresh-onewalk` (Д): файлы — `descriptors.cpp`, `pipelineCache.cpp`, `ResourceMaterialization.cpp`, `ResourceMaterialization.h`; задеты ханки ручек — ResourceMaterialization.cpp: 1 [call-site]; descriptors.cpp: 1 [KYTY_FIX_B42 KYTY_FIX_F26 KYTY_FIX_F5CMU].
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, §70): overlap задевает наш call-site F19 (overlap 1 [call-site], прочих 10); конфликт на месте F19 — при переносе сохранить нашу ветку F19 дословно; descriptors.cpp несёт KYTY_FIX_B42 (Б42, §33; F26/F5CMU не отгружены): overlap задевает 1 ханк с ручкой (соседство в RebindImages, snapshot -> *resources) — сохранить правку Б42; pipelineCache.cpp несёт KYTY_FIX_F20 (§126), KYTY_FIX_SVAL (§40), KYTY_S_PCW (§49), KYTY_S_REPLAY (§74): наши ханки с ручкой не задеты, прочих наших задето 5
- **T082** `dec-perf` (Д): файлы — `pipelineCache.cpp`, `shaders.cpp`; задеты ханки ручек — нет.
  - в задетых файлах ручки KYTY_FIX_F20 (Ф20), KYTY_FIX_SVAL (Ф16), KYTY_S_PCW (Б33), KYTY_S_PCW_FORCE_MS (стенд Б33), KYTY_S_REPLAY (S-replay), KYTY_S_REPLAY_TEST (стенд S-replay) — места наших ханков с ручкой не пересекаются (overlap 0)
  - в задетых файлах ручки KYTY_FIX_DUALSRC (Б35), KYTY_FIX_F20 (Ф20) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T083** `be-spvsize` (Д): файлы — `spirvEmitterMemory.cpp`; задеты ханки ручек — нет.
  - spirvEmitterMemory.cpp [KYTY_FIX_B1B,KYTY_FIX_F10]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается)
  - ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается)
- **T084** `be-indimg` (Г): файлы — `vulkanWindow.cpp`, `ResourceMaterialization.cpp`; задеты ханки ручек — ResourceMaterialization.cpp: 1 [call-site].
  - ResourceMaterialization.cpp [KYTY_FIX_F19]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается)
  - ResourceMaterialization.cpp [KYTY_FIX_F19]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается)
  - ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается)
  - vulkanWindow.cpp [KYTY_FIX_B26,KYTY_FIX_DUALSRC,KYTY_FIX_F24,KYTY_FIX_SVAL]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); ResourceMaterialization.cpp [KYTY_FIX_F19]: ханков ручки задето 1 [call-site], прочих наших 7; конфликт с местом вызова гейта Ф19 в ResourceMaterialization.cpp — сохранить нашу правку
  - ResourceMaterialization.cpp [KYTY_FIX_F19]: ханков ручки задето 0, прочих наших 2 (место ручки не пересекается)
  - ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 2 (место ручки не пересекается)
  - ResourceMaterialization.cpp [KYTY_FIX_F19]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается)
  - ResourceMaterialization.cpp [KYTY_FIX_F19]: ханков ручки задето 0, прочих наших 2 (место ручки не пересекается); ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 2 (место ручки не пересекается)
- **T085** `ir-scalar-imgtable` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 1 (FrameStats в MaterializeResources)); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T086** `ir-perf-span` (Д): файлы — `pipelineCache.cpp`, `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 0); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization; pipelineCache.cpp несёт KYTY_FIX_F20 (§126), KYTY_FIX_SVAL (§40), KYTY_S_PCW (§49), KYTY_S_REPLAY (§74): наши ханки с ручкой не задеты, прочих наших задето 1 (ReadShaderGuestMemory)
- **T087** `ir-tdesc-valid` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 0); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T090** `rnd-readback-staging` (Г): файлы — `bufferCache.cpp`; задеты ханки ручек — нет.
  - bufferCache.cpp/.h: ручка KYTY_FIX_B12 (Б12, FS11) и неотгруженная KYTY_FIX_F5CMU; ханки upstream наших с ручкой не задевают (5 прочих рядом)
  - bufferCache.cpp/.h: ручка KYTY_FIX_B12 (Б12, FS11) и неотгруженная KYTY_FIX_F5CMU; ханки upstream задевают 7 наших прочих ханков (DownloadBufferMemory переписан нами), ручек не задевают
- **T092** `hle-kernel-imports` (Г): файлы — `videoOut.cpp`, `fileSystem.cpp`, `libKernel.cpp`; задеты ханки ручек — нет.
  - fileSystem.cpp: ручки Б4 (реестр §65) и Ф25 (реестр §119); overlap: 5 ханков, 0 задето (новые функции и поле readable рядом с KernelPread) — место Ф25 не задето; videoOut.cpp (KYTY_PVAR): 1 ханк — новая функция, 0; libKernel.cpp (KYTY_PVAR): 2 ханка, 0
- **T093** `prs-sdl3` (В): файлы — `CMakeLists.txt`, `hostInput.cpp`, `swapchain.cpp`, `vulkanWindow.cpp`, `window.cpp`, `audio.cpp`, `controller.cpp`; задеты ханки ручек — controller.cpp: 2 [call-site]; hostInput.cpp: 2 [KYTY_FIX_F24]; vulkanWindow.cpp: 1 [KYTY_FIX_F24]; window.cpp: 3 [KYTY_FIX_F24].
  - Задевает три отгруженные правки на API SDL2: KYTY_FIX_F24 (Ф24, поток JoyPump на SDL_JoystickUpdate — ханки ручки: hostInput.cpp 2, window.cpp 3, vulkanWindow.cpp 1), KYTY_FIX_F8 (Ф8, один владелец SDL_InitSubSystem(AUDIO) — audio.cpp 26 прочих наших ханков), KYTY_FIX_B24 (Б24, поток PadOutput — controller.cpp 2 call-site); swapchain.cpp (MINIMIZE/DUALSRC) — 1 ханк вне мест ручек; при переносе все три правки переписать под SDL3 и заново проверить стендами KYTY_TEST_HIDLOSS / KYTY_TEST_AUDIOLOSS
- **T094** `prs-resize` (Г): файлы — `swapchain.cpp`, `window.cpp`; задеты ханки ручек — swapchain.cpp: 2 [KYTY_FIX_MINIMIZE].
  - swapchain.cpp: overlap задевает 2 ханка KYTY_FIX_MINIMIZE (Б37): upstream убирает RefreshSurfaceCapabilities из Swapchain::Recreate, а наша проверка нулевого экстента (SurfaceExtentZero, строка 648) читает именно освежённые возможности — при переносе сохранить порядок «освежить → проверить ноль → Create»; Create upstream делает EXIT_IF при нулевом размере окна, а NeedsResize → RecoverSwapchain может прийти при свёрнутом окне — наша ветка Missing() в Present должна остаться первой; window.cpp (KYTY_FIX_F24): флаги окна, место JoyPump не задето
- **T095** `sys-dynload` (Г): файлы — `libKernel.cpp`, `runtimeLinker.cpp`; задеты ханки ручек — нет.
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 1 ханк, не задет.
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 14 ханков, ханки ручек не задеты.
  - libKernel.cpp (KYTY_PVAR): 3 ханка, ханк ручки не задет.
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 8 ханков, не задеты.
- **T096** `prs-frame-cfg` (Д): файлы — `swapchain.cpp`; задеты ханки ручек — нет.
  - swapchain.cpp (KYTY_FIX_MINIMIZE/DUALSRC): Frame::Configure вне мест ручек (overlap 0/0)
- **T097** `av-audio-split` (Г): файлы — `audio.cpp`, `libAudio.cpp`; задеты ханки ручек — нет.
  - audio.cpp: ручка Ф8 KYTY_FIX_F8 (реестр §68, FS7; SdlAudioAcquire/FixF8Enabled audio.cpp:292–330): 8 ханков, ручкиных 0, прочих наших 7; libAudio.cpp (Б9а, реестр §24; DUALSRC): 2 ханка, 0 задето. При переносе — крупный текстовый конфликт: код Ф8 (audio.cpp:292–330, audio_internal.h) и наш темп/WSOLA (audio.cpp:58, 697) остаются в audio.cpp, сохранить
- **T098** `img-vo-dcc` (Г): файлы — `textureCache.cpp`, `videoOut.cpp`; задеты ханки ручек — нет.
  - videoOut.cpp (KYTY_PVAR): BufferAttributeGroup::ImageInfo, хуки P-var (VblankEnd, завершение флипа) не задеты; textureCache.cpp: 3 прочих ханка FindImage, места ручек не задеты
- **T101** `rnd-depth-feedback` (Г): файлы — `descriptors.cpp`; задеты ханки ручек — нет.
  - descriptors.cpp: ручка KYTY_FIX_B42 (Б42, FS3) и неотгруженные KYTY_FIX_F26/F5CMU (умолчание 0); ханки upstream задевают 2 наших прочих ханка - конфликт в CommitBindings
- **T103** `ir-material-mask` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 1 (FrameStats)); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T105** `rnd-bind-reuse` (Д): файлы — `descriptors.cpp`; задеты ханки ручек — descriptors.cpp: 1 [KYTY_FIX_B42 KYTY_FIX_F26 KYTY_FIX_F5CMU].
  - descriptors.cpp: ручка KYTY_FIX_B42 (Б42, FS3) и неотгруженные KYTY_FIX_F26/F5CMU (умолчание 0); по overlap.tsv задет 1 наш ханк с ручками KYTY_FIX_B42/F26/F5CMU - конфликт при переносе, ветку Б42 сохранить
  - descriptors.cpp: ручка KYTY_FIX_B42 (Б42, FS3) и неотгруженные KYTY_FIX_F26/F5CMU (умолчание 0); ханки upstream задевают 9 наших прочих ханков, ручек не задевают
  - descriptors.cpp: ручка KYTY_FIX_B42 (Б42, FS3) и неотгруженные KYTY_FIX_F26/F5CMU (умолчание 0); по overlap.tsv задет 1 наш ханк с ручками KYTY_FIX_B42/F26/F5CMU - конфликт при переносе
  - descriptors.cpp: ручка KYTY_FIX_B42 (Б42, FS3) и неотгруженные KYTY_FIX_F26/F5CMU (умолчание 0); ханки upstream задевают 12 наших прочих ханков, ручек не задевают
- **T109** `prs-depth-clamp` (А): файлы — `shaders.cpp`, `vulkanWindow.cpp`; задеты ханки ручек — нет.
  - shaders.cpp (KYTY_FIX_DUALSRC/F20) и vulkanWindow.cpp (B26/DUALSRC/F24/SVAL): места ручек не задеты (overlap 0/0); меняет состояние растеризатора всех пайплайнов — рецепты и подпись трансляции прежние, блоб драйвера холоден один раз
- **T110** `prs-vrr-status` (Г): файлы — `videoOut.cpp`; задеты ханки ручек — нет.
  - videoOut.cpp (KYTY_PVAR): удаление VideoOutGetVrrStatus вне хуков P-var
- **T111** `img-vo-pq` (Г): файлы — `videoOut.cpp`; задеты ханки ручек — нет.
  - videoOut.cpp (KYTY_PVAR): ImageInfo буфера, хуки P-var не задеты (1 прочий ханк)
- **T113** `dec-glc-coherent` (А): файлы — `spirvEmitterMemory.cpp`, `ShaderDecoder.cpp`, `ShaderDecoder.h`, `Memory.cpp`; задеты ханки ручек — нет.
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_F10 (Ф10) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T114** `dec-bvh` (В): файлы — `pipelineCache.cpp`, `spirvEmitterMemory.cpp`, `ShaderDecoder.cpp`, `ShaderDecoder.h`, `Memory.cpp`; задеты ханки ручек — нет.
  - BVH: перенос добавит has_bvh в декодер и пропуск dispatch — выключит отгруженные KYTY_FIX_B1B/KYTY_FIX_F10 (Б1б/Ф9, Ф10); не брать без решения M1c; в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_F10 (Ф10), KYTY_FIX_F20 (Ф20), KYTY_FIX_SVAL (Ф16), KYTY_S_PCW (Б33), KYTY_S_PCW_FORCE_MS (стенд Б33), KYTY_S_REPLAY (S-replay), KYTY_S_REPLAY_TEST (стенд S-replay) — места наших ханков с ручкой не пересекаются (overlap 0)
  - BVH: upstream заменяет обход своим — при переносе конфликт с KYTY_FIX_B1B/KYTY_FIX_F10 (Memory.cpp, spirvEmitterMemory.cpp, ShaderDecoder.cpp/.h); выбрать по данным (GPU-тест-гейт Ф10); в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_F10 (Ф10), KYTY_FIX_F20 (Ф20), KYTY_FIX_SVAL (Ф16), KYTY_S_PCW (Б33), KYTY_S_PCW_FORCE_MS (стенд Б33), KYTY_S_REPLAY (S-replay), KYTY_S_REPLAY_TEST (стенд S-replay) — места наших ханков с ручкой не пересекаются (overlap 0)
  - BVH: правка ложится на обход upstream (337f43201), не на наш; при переносе — конфликт с KYTY_FIX_B1B/KYTY_FIX_F10 в Memory.cpp; в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_F10 (Ф10) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T116** `prs-agc-trace` (Д): файлы — `videoOut.cpp`; задеты ханки ручек — нет.
  - videoOut.cpp (KYTY_PVAR): VideoOutIsFlipPending вне хуков P-var; наши инструменты считают кадры по строкам flipPendingNum — при переносе проверить, какая строка им нужна (GetFlipStatus:4039 или IsFlipPending:4059); наш agc.cpp уже с AgcTrace
- **T118** `av-audio-out-pacing` (В): файлы — `CMakeLists.txt`, `audio.cpp`; задеты ханки ручек — нет.
  - audio.cpp: ручка Ф8 KYTY_FIX_F8 (реестр §68, FS7; SdlAudioAcquire/FixF8Enabled audio.cpp:292–330): 7 ханков, ручкиных 0, прочих наших 6 (наш темп звука/WSOLA 2ae7491a2 и заморозка 6d50b5f75 в QueueSdlAudio); код upstream написан на SDL3 (f68c77d78 «SDL3 update», корзина gfx_present), у нас SDL2 — перенос только вместе с SDL3; конфликт с нашим темпом, выбрать по данным; Ф8 сохранить
  - audio.cpp: ручка Ф8 KYTY_FIX_F8 (реестр §68, FS7; SdlAudioAcquire/FixF8Enabled audio.cpp:292–330): 16 ханков, ручкиных 0, прочих наших 13 (наш темп/WSOLA 2ae7491a2, Ф8 рядом) — сильный конфликт; код upstream написан на SDL3 (f68c77d78 «SDL3 update», корзина gfx_present), у нас SDL2; CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 3 ханк(ов) upstream, ручкиных задето 0 — место не пересекается; выбрать по данным, Ф8 сохранить
- **T119** `ir-perf-spec` (Д): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 1 (FrameStats)); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 0); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 5 (класс выравнивания V# KYTY_VEC_CONST, FrameStats, ApplyResourceSpecialization)); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T122** `img-vk-names` (Д): файлы — `textureCache.cpp`; задеты ханки ручек — textureCache.cpp: 1 [KYTY_FIX_B42].
  - textureCache.cpp: overlap задевает ханк KYTY_FIX_B42 (конец FindTexture: NameImageBinding рядом с меткой B42, строки 2688/2706) — при переносе сохранить метку B42
- **T124** `sys-eager-resolve` (Г): файлы — `runtimeLinker.cpp`; задеты ханки ручек — нет.
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 28 ханков, ханки ручек не задеты; механический конфликт.
- **T125** `av-audioout2-mix` (А): файлы — `audio.cpp`, `audio_internal.h`; задеты ханки ручек — нет.
  - audio.cpp: ручка Ф8 KYTY_FIX_F8 (реестр §68, FS7; SdlAudioAcquire/FixF8Enabled audio.cpp:292–330): 14 ханков, ручкиных 0, прочих наших 4 (OutputParam получает gains); audio_internal.h (Ф8): 1 ханк — поле gains в OutputParam, ручкиных 0 — место Ф8 (SdlAudio*) не пересекается; зависит от SDL3, 313b60e92, 0471c9991
- **T126** `bld-tests` (Г): файлы — `CMakeLists.txt`; задеты ханки ручек — нет.
  - CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 1 ханк(ов) upstream, ручкиных задето 0 — место не пересекается
  - tests/ShaderRecompilerComputeTests.cpp: наши GPU-тесты ручек Б1б/Б26б/Ф10/Ф19/Ф20/Ф26/Ф5 в этом файле; overlap: 1 ханк(ов), ручкиных 0 — тесты ручек не задеты
  - tests/ShaderRecompilerComputeTests.cpp: наши GPU-тесты ручек Б1б/Б26б/Ф10/Ф19/Ф20/Ф26/Ф5 в этом файле; overlap: 4 ханк(ов), ручкиных 0, прочих наших 1 — тесты ручек не задеты; CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 1 ханк(ов) upstream, ручкиных задето 0 — место не пересекается
  - tests/ShaderRecompilerComputeTests.cpp: наши GPU-тесты ручек Б1б/Б26б/Ф10/Ф19/Ф20/Ф26/Ф5 в этом файле; overlap: 1 ханк(ов), ручкиных 0 — тесты ручек не задеты; CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 2 ханк(ов) upstream, ручкиных задето 0 — место не пересекается
  - tests/ShaderRecompilerComputeTests.cpp: наши GPU-тесты ручек Б1б/Б26б/Ф10/Ф19/Ф20/Ф26/Ф5 в этом файле; overlap: 2 ханк(ов), ручкиных 0 — тесты ручек не задеты; CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 1 ханк(ов) upstream, ручкиных задето 0 — место не пересекается
- **T127** `lch-tests-args` (Г): файлы — `CMakeLists.txt`; задеты ханки ручек — нет.
  - CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 3 ханк(ов) upstream, ручкиных задето 0 — место не пересекается
- **T129** `av-dualsense-haptics` (В): файлы — `CMakeLists.txt`, `audio.cpp`, `controller.cpp`, `controller.h`; задеты ханки ручек — controller.cpp: 3 [KYTY_FIX_F24]; controller.h: 1 [KYTY_FIX_B24].
  - controller.cpp: ручки Б24 KYTY_FIX_B24 (реестр §68, PadOutput) и Ф24 KYTY_FIX_F24 (реестр §124, JoyPump); overlap: 6 ханков, задеты 3 наших ханка Ф24 и 8 прочих; controller.h: 1 ханк, задет 1 ханк Б24; audio.cpp: ручка Ф8 KYTY_FIX_F8 (реестр §68, FS7; SdlAudioAcquire/FixF8Enabled audio.cpp:292–330): 5 ханков, ручкиных 0, прочих наших 5 (наш вибро-порт → PushHapticsPcm, audio.cpp:812); CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 3 ханк(ов) upstream, ручкиных задето 0 — место не пересекается. Конфликт: наша HapticsOutput (b9df4fd69, dfaf48a93) открывает звук через SdlAudioAcquire (Ф8) — сохранить Ф8, вариант хаптики выбрать по данным
  - audio.cpp: ручка Ф8 KYTY_FIX_F8 (реестр §68, FS7; SdlAudioAcquire/FixF8Enabled audio.cpp:292–330): 9 ханков, ручкиных 0, прочих наших 6 (открытие порта и вибро-путь) — конфликт, Ф8 сохранить; код upstream написан на SDL3 (f68c77d78 «SDL3 update», корзина gfx_present), у нас SDL2
  - audio.cpp: ручка Ф8 KYTY_FIX_F8 (реестр §68, FS7; SdlAudioAcquire/FixF8Enabled audio.cpp:292–330): 6 ханков, 0 задето; CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 2 ханк(ов) upstream, ручкиных задето 0 — место не пересекается; мы пути Bluetooth сознательно убрали (dfaf48a93 «Drop the Bluetooth haptics paths»)
- **T130** `prs-layered-vo` (Г): файлы — `CMakeLists.txt`, `descriptors.cpp`, `videoOut.cpp`, `swapchain.cpp`, `ResourceMaterialization.cpp`, `ResourceMaterialization.h`; задеты ханки ручек — swapchain.cpp: 4 [KYTY_FIX_DUALSRC KYTY_FIX_MINIMIZE]; videoOut.cpp: 2 [KYTY_PVAR].
  - swapchain.cpp: overlap задевает 4 ханка KYTY_FIX_DUALSRC/KYTY_FIX_MINIMIZE (Б35/Б37) — Present переписан под слои, ветка Missing() Б37 должна сохраниться; videoOut.cpp: 2 ханка KYTY_PVAR — FlipQueue переписан (группы флипов), хуки PVar::PublishFlip (завершение флипа) и PublishVblank (VblankEnd) сохранить; ResourceMaterialization.cpp/h (KYTY_FIX_F19): 3 прочих ханка, место ручки не задето, но смена трансляции; descriptors.cpp (KYTY_FIX_B42): 10 прочих наших ханков
- **T133** `img-1d2d-alias` (А): файлы — `textureCache.cpp`; задеты ханки ручек — нет.
  - textureCache.cpp (KYTY_FIX_B42; KYTY_FIX_F26/KYTY_FIX_F5CMU не отгружены): места ручек не задеты (overlap 0/0)
- **T134** `img-depth-alias` (Г): файлы — `textureCache.cpp`; задеты ханки ручек — нет.
  - textureCache.cpp: 1 прочий наш ханк ResolveDepthOverlap, места ручек не задеты
  - textureCache.cpp: места ручек не задеты (overlap 0/0)
- **T135** `img-color-meta-clear` (В): файлы — `textureCache.cpp`, `textureCache.h`; задеты ханки ручек — textureCache.cpp: 1 [KYTY_FIX_F26]; textureCache.cpp: 1 [KYTY_FIX_F5CMU]; textureCache.cpp: 2 [KYTY_FIX_F26 KYTY_FIX_F5CMU]; textureCache.h: 1 [KYTY_FIX_F26 KYTY_FIX_F5CMU].
  - textureCache.cpp/.h: overlap задевает ханки KYTY_FIX_F26 и KYTY_FIX_F5CMU (диагностика, не отгружены, умолчание 0; Ф26 ТУПИК, Ф5 НЕ ДЕФЕКТ); tests: 1 ханк KYTY_FIX_F5CMU; у нас MaterializeDccClear базы заменён своими PrepareDccClear/PrepareCmaskClear (отложенная заливка, проверка по корзине 64 КиБ) — перенос upstream = смена механизма, конфликт по всей функции; сохранить наш или выбрать по данным
  - textureCache.cpp: overlap задевает ханк KYTY_FIX_F5CMU (не отгружен); функции MaterializeColorClear у нас нет (PrepareDccClear/PrepareCmaskClear) — перенос только вместе с 0f1ff37f2
  - textureCache.cpp: overlap задевает ханк KYTY_FIX_F26 (не отгружен, Ф26 ТУПИК); функции у нас нет — перенос только вместе с 0f1ff37f2
- **T137** `hle-http-uri` (Г): файлы — `CMakeLists.txt`; задеты ханки ручек — нет.
  - CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 3 ханк(ов) upstream, ручкиных задето 0 — место не пересекается
- **T138** `ir-883` (В): файлы — `descriptors.cpp`, `pipelineCache.cpp`, `spirvEmitterMemory.cpp`, `Memory.cpp`, `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 1); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization; descriptors.cpp несёт KYTY_FIX_B42 (Б42, §33; F26/F5CMU не отгружены): ханки с ручкой не задеты, прочих 4; pipelineCache.cpp несёт KYTY_FIX_F20 (§126), KYTY_FIX_SVAL (§40), KYTY_S_PCW (§49), KYTY_S_REPLAY (§74): наши ханки с ручкой не задеты, прочих наших задето 13; spirvEmitterMemory.cpp/Memory.cpp несут KYTY_FIX_B1B/KYTY_FIX_F10 (Б1б/Ф9/Ф10): ханки с ручкой не задеты; tests/ShaderRecompilerComputeTests.cpp: задет 1 ханк с B1B/B26/F10/F19
- **T140** `img-ext-mem` (Г): файлы — `bufferCache.cpp`, `bufferCache.h`, `faultManager.cpp`, `textureCache.h`, `descriptors.cpp`, `spirvEmitterMemory.cpp`; задеты ханки ручек — faultManager.cpp: 1 [call-site].
  - faultManager.cpp: задет call-site KYTY_FIX_F29 (ParseFaultArea, Ф29) — upstream меняет цикл faults[1..count] (GuestAddress): при переносе сохранить наш предел count и добавить перевод адреса в визитор; bufferCache.cpp/h (KYTY_FIX_B12): 2+3 прочих наших ханка, место ручки не задето; spirvEmitterMemory.cpp (KYTY_FIX_B1B/F10): 1 прочий ханк DefineGetBdaPointer — смена подписи трансляции; textureCache.h, descriptors.cpp — места ручек не задеты
- **T142** `ir-perf-policy` (Д): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 1); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T143** `hle-ces-savedialog` (Г): файлы — `CMakeLists.txt`; задеты ханки ручек — нет.
  - CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 3 ханк(ов) upstream, ручкиных задето 0 — место не пересекается
- **T144** `sys-fs-unmounted` (Г): файлы — `fileSystem.cpp`; задеты ханки ручек — нет.
  - fileSystem.cpp (Б4, Ф25): 4 ханка (ResolvePath, KernelOpen, KernelRename, KernelMkdir), ханки ручек не задеты (overlap 0).
- **T145** `av-audioout2-user` (Г): файлы — `libAudio.cpp`; задеты ханки ручек — нет.
  - libAudio.cpp (Б9а, реестр §24): 1 ханк — строка LIB_FUNC в блоке AudioOut2, 0 задето
- **T146** `img-readback-valid` (Г): файлы — `textureCache.cpp`, `textureCache.h`; задеты ханки ручек — нет.
  - textureCache.cpp/h: 4 прочих наших ханка (GC с preserve_gpu, SynchronizeBufferFromImage), места ручек не задеты
- **T147** `img-gpumod-cpu` (В): файлы — `textureCache.cpp`; задеты ханки ручек — нет.
  - textureCache.cpp: 1 прочий наш ханк (сокращение «dawitcp», с. 73), места ручек не задеты; позднее upstream удаляет функцию (783d9f8d6)
- **T148** `av-zarchive` (Г): файлы — `CMakeLists.txt`, `fileSystem.cpp`; задеты ханки ручек — нет.
  - fileSystem.cpp: ручки Б4 KYTY_FIX_B4 (реестр §65) и Ф25 KYTY_FIX_F25 (реестр §119); overlap: 16 ханков, ручкиных 0, прочих наших 1 — места Б4/Ф25 не задеты, при переносе сохранить; CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 5 ханк(ов) upstream, ручкиных задето 0, прочих наших 1 — место не пересекается
- **T150** `rnd-stream-memcpy` (Д): файлы — `bufferCache.cpp`; задеты ханки ручек — нет.
  - bufferCache.cpp/.h: ручка KYTY_FIX_B12 (Б12, FS11) и неотгруженная KYTY_FIX_F5CMU; ханк upstream задевает 4 наших прочих ханка (наше условие вокруг TryReadBacking)
- **T152** `rnd-pipeline-key-compact` (Д): файлы — `pipelineCache.cpp`, `pipelineCache.h`; задеты ханки ручек — нет.
  - pipelineCache.cpp: ручки KYTY_S_PCW (Б33), KYTY_S_REPLAY (S-replay), KYTY_FIX_SVAL (Ф16), KYTY_FIX_F20 (Ф20); по overlap.tsv ручек не задевает (4 прочих ханка .cpp, 1 .h); shader.cpp входит в набор подписи трансляции - смена BuildStageStaticKey меняет ключи программ: холодные кэш трансляции, рецепты precache и каталог S-replay
- **T153** `prs-pcache-lock` (В): файлы — `pipelineCache.cpp`, `pipelineCache.h`, `window.cpp`; задеты ханки ручек — pipelineCache.cpp: 2 [KYTY_S_PCW]; pipelineCache.h: 2 [KYTY_FIX_DUALSRC KYTY_FIX_F20 KYTY_S_PCW KYTY_S_PCW_FORCE_MS KYTY_S_REPLAY].
  - pipelineCache.cpp/h: overlap задевает 2+2 ханка KYTY_S_PCW (Б33, трек S; в .h также DUALSRC/F20/S_REPLAY) — наш писатель блоба вне m_mutex, стенд KYTY_S_PCW_FORCE_MS, S-replay (ReplayStop) и воркеры держатся на m_mutex; перенос удаляет код, на котором стоят Б33 и S-replay — не брать без переписи; window.cpp (KYTY_FIX_F24): строка в WindowRun вне JoyPump
- **T154** `sys-profiler` (Г): файлы — `runtimeLinker.cpp`; задеты ханки ручек — нет.
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 4 ханка, не задеты.
- **T155** `sys-sleep-block` (Д): файлы — `pthread.cpp`; задеты ханки ручек — нет.
  - pthread.cpp (KYTY_GAME_PATCH, стр. 188): ханк ручки не задет; 9 ханков задевают 6 наших прочих (метки DiagB32 в KernelUsleep/Sleep/Nanosleep) — конфликт механический.
- **T156** `rnd-blend-swizzle-alpha` (В): файлы — `pipelineCache.cpp`, `pipelineCache.h`, `shaders.cpp`; задеты ханки ручек — pipelineCache.cpp: 1 [KYTY_S_PCW]; pipelineCache.cpp: 2 [KYTY_S_PCW KYTY_S_PCW_FORCE_MS KYTY_S_REPLAY]; pipelineCache.cpp: 3 [KYTY_S_PCW KYTY_S_PCW_FORCE_MS KYTY_S_REPLAY].
  - pipelineCache.cpp/.h, shaders.cpp: ручки KYTY_FIX_DUALSRC (Б35), KYTY_S_PCW, KYTY_S_REPLAY, KYTY_FIX_F20; по overlap.tsv задеты 2 наших ханка с KYTY_S_PCW/KYTY_S_REPLAY и call-site в тесте; опирается на upstream 649367472 (dual-source в трансляторе, dual_source_blending) - у нас его нет, Б35 сделан переписью Location 1 -> Location 0 Index 1 (dualSrcBlend.h); перенос требует выбрать одну реализацию dual-source; меняет ключ графического пайплайна (PipelineStaticParameters/хэш) - рецепты precache pipelines.bin и каталог повтора S-replay станут холодными (первый вход каждой сцены), подпись трансляции не меняется
  - pipelineCache.cpp/.h, shaders.cpp: KYTY_FIX_DUALSRC (Б35), KYTY_S_PCW, KYTY_S_REPLAY, KYTY_FIX_F20; по overlap.tsv задеты 3 наших ханка с KYTY_S_PCW/KYTY_S_REPLAY; зависит от 73615c31f и 649367472; меняет ключ графического пайплайна (PipelineStaticParameters/хэш) - рецепты precache pipelines.bin и каталог повтора S-replay станут холодными (первый вход каждой сцены), подпись трансляции не меняется
  - pipelineCache.cpp: ручки KYTY_S_PCW (Б33), KYTY_S_REPLAY (S-replay), KYTY_FIX_SVAL (Ф16), KYTY_FIX_F20 (Ф20); по overlap.tsv задет 1 наш ханк с KYTY_S_PCW; часть серии 73615c31f
  - pipelineCache.cpp: ручки KYTY_S_PCW (Б33), KYTY_S_REPLAY (S-replay), KYTY_FIX_SVAL (Ф16), KYTY_FIX_F20 (Ф20); по overlap.tsv задеты 2 наших ханка с KYTY_S_PCW/KYTY_S_REPLAY; часть серии 73615c31f
- **T158** `sys-mem-sparse` (Г): файлы — `bufferCache.cpp`; задеты ханки ручек — нет.
  - bufferCache.cpp (Б12 KYTY_FIX_B12): 1 ханк в ObtainBufferForImage, ханки ручки не задеты, 2 наших прочих — механический конфликт.
- **T161** `prs-gpu-reject` (Г): файлы — `vulkanWindow.cpp`; задеты ханки ручек — нет.
  - vulkanWindow.cpp (B26/DUALSRC/F24/SVAL): VulkanFindPhysicalDevice переписан (29 ханков), overlap 0 наших ханков; при переносе сверить, что наши включения возможностей (dualSrcBlend, uniformBufferStandardLayout) не потеряны
- **T162** `av-host-controller-ux` (Г): файлы — `CMakeLists.txt`, `hostInput.cpp`, `audio.cpp`, `controller.cpp`, `controller.h`; задеты ханки ручек — controller.cpp: 1 [call-site]; controller.cpp: 4 [KYTY_FIX_B24]; controller.h: 1 [KYTY_FIX_B24].
  - controller.cpp: ручки Б24 KYTY_FIX_B24 (реестр §68, PadOutput) и Ф24 KYTY_FIX_F24 (реестр §124, JoyPump); overlap: 2 ханка, задет 1 наш ханк call-site (вызов гейта без имени ручки) и 3 прочих — при переносе сохранить вызов через PadOutput (Б24)
  - controller.cpp: ручки Б24 KYTY_FIX_B24 (реестр §68, PadOutput) и Ф24 KYTY_FIX_F24 (реестр §124, JoyPump); overlap: 23 ханка, задеты 4 наших ханка Б24 и 11 прочих; controller.h: 1 ханк Б24; hostInput.cpp (Ф24): 5 ханков, прочих наших 2; audio.cpp: ручка Ф8 KYTY_FIX_F8 (реестр §68, FS7; SdlAudioAcquire/FixF8Enabled audio.cpp:292–330): 11 ханков, прочих наших 2; CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 3 ханк(ов) upstream, ручкиных задето 0 — место не пересекается. Конфликт: масштаб в SetVibration/SetTriggerEffect, которые при Б24=1 уходят в поток PadOutput — сохранить Б24
  - controller.cpp: ручки Б24 KYTY_FIX_B24 (реестр §68, PadOutput) и Ф24 KYTY_FIX_F24 (реестр §124, JoyPump); overlap: 1 ханк, 0 задето
- **T164** `hle-pngenc` (Г): файлы — `CMakeLists.txt`; задеты ханки ручек — нет.
  - CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 3 ханк(ов) upstream, ручкиных задето 0 — место не пересекается
- **T165** `prs-vrr-wqhd` (Г): файлы — `videoOut.cpp`; задеты ханки ручек — нет.
  - videoOut.cpp (KYTY_PVAR): новые функции, хуки P-var не задеты
- **T168** `img-scratch-reuse` (Д): файлы — `textureCache.cpp`; задеты ханки ручек — нет.
  - textureCache.cpp: 3 ханка CopyD16/UploadImage/DownloadDepth вне мест ручек (overlap 0/0)
- **T170** `dec-cdbg-unused` (Г): файлы — `ShaderDecoder.cpp`, `ShaderDecoder.h`; задеты ханки ручек — нет.
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_F10 (Ф10) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T171** `ir-refresh-reach` (Г): файлы — `descriptors.cpp`, `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 2); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization; descriptors.cpp несёт KYTY_FIX_B42 (Б42, §33; F26/F5CMU не отгружены): ханки с ручкой не задеты, прочих 1
- **T174** `rnd-pipeline-blend-normalize` (Д): файлы — `pipelineCache.cpp`; задеты ханки ручек — pipelineCache.cpp: 1 [KYTY_S_PCW].
  - pipelineCache.cpp: ручки KYTY_S_PCW (Б33), KYTY_S_REPLAY (S-replay), KYTY_FIX_SVAL (Ф16), KYTY_FIX_F20 (Ф20); по overlap.tsv задет 1 наш ханк с KYTY_S_PCW - конфликт при переносе; решение Б35 (SRC1 на смешиваемом вложении) не затрагивается; меняет ключ графического пайплайна (PipelineStaticParameters/хэш) - рецепты precache pipelines.bin и каталог повтора S-replay станут холодными (первый вход каждой сцены), подпись трансляции не меняется
- **T177** `rnd-memtrack-hotpath` (Д): файлы — `pageManager.cpp`, `regionManager.h`; задеты ханки ручек — нет.
  - regionManager.h: ручки KYTY_FIX_B12 (Б12) и KYTY_FIX_B13 (Б13); ханк upstream задевает 2 наших прочих ханка, ручек не задевает
  - regionManager.h: ручки KYTY_FIX_B12 (Б12) и KYTY_FIX_B13 (Б13); ханки upstream задевают 2 наших прочих ханка, ручек не задевают
  - regionManager.h: ручки KYTY_FIX_B12 (Б12) и KYTY_FIX_B13 (Б13); ханк upstream задевает 3 наших прочих ханка, ручек не задевает
  - - (memoryTracker.h; ручка KYTY_FIX_B13 живёт в memoryTracker.cpp)
  - pageManager.cpp: ручка KYTY_FIX_B36 (Ф27); regionManager.h: KYTY_FIX_B12/B13; ханки upstream задевают 5+3 наших прочих ханка, ручек не задевают
- **T178** `rnd-readback-sync` (Д): файлы — `bufferCache.cpp`, `bufferCache.h`; задеты ханки ручек — нет.
  - bufferCache.cpp/.h: ручка KYTY_FIX_B12 (Б12, FS11) и неотгруженная KYTY_FIX_F5CMU; ханки upstream задевают 9+2 наших прочих ханка (наш readback переписан: c34035d76 - ожидание на потоке гостя, предвыборка), ручек не задевают
  - bufferCache.cpp/.h: ручка KYTY_FIX_B12 (Б12, FS11) и неотгруженная KYTY_FIX_F5CMU; ханк upstream задевает 3 наших прочих ханка (у нас окно 512 КиБ в трёх местах), ручек не задевает
- **T179** `img-hades2` (В): файлы — `textureCache.cpp`, `libKernel.cpp`; задеты ханки ручек — нет.
  - libKernel.cpp (KYTY_PVAR): новая функция La9uyZv4Kvw вне мест P-var (overlap 0/0); textureCache.cpp: 1 прочий ханк ClearImageFromBuffer (наши счётчики ClearDecodeFail), места ручек не задеты
- **T180** `ir-gpu-selected-img` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 1 (FrameStats)); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T185** `prs-lds-pad` (Б): файлы — `pipelineCache.cpp`, `window.cpp`; задеты ханки ручек — window.cpp: 2 [KYTY_FIX_F24].
  - window.cpp: overlap задевает 2 ханка KYTY_FIX_F24 (GameEventController): у нас при KYTY_FIX_F24=1 открытие делает JoyPump без фатала, при =0 — старый EXIT_NOT_IMPLEMENTED (window.cpp:396) — часть геймпада не нужна; pipelineCache.cpp (S_PCW/S_REPLAY/F20/SVAL): GetComputeProgram, 4 прочих ханка, места ручек не задеты, клэмп меняет ключ кэша программ; tests: 1 ханк с именами B1B/B26/F10/F19
- **T186** `dec-img-atomic64` (Г): файлы — `graphicContext.h`, `descriptors.cpp`, `vulkanWindow.cpp`, `spirvEmitterMemory.cpp`, `Memory.cpp`, `ResourceMaterialization.cpp`; задеты ханки ручек — graphicContext.h: 1 [KYTY_FIX_DUALSRC KYTY_FIX_SVAL].
  - КОНФЛИКТ по overlap: graphicContext.h задевает наш ханк 1 [KYTY_FIX_DUALSRC KYTY_FIX_SVAL]; ручки задетых файлов: KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_B42 (Б42), KYTY_FIX_DUALSRC (Б35), KYTY_FIX_F10 (Ф10), KYTY_FIX_F19 (Ф19), KYTY_FIX_F24 (Ф24), KYTY_FIX_F26 (Ф26, не отгружена), KYTY_FIX_F5CMU (Ф5, не отгружена), KYTY_FIX_SVAL (Ф16)
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_F10 (Ф10) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T187** `img-bc5-reuse` (Г): файлы — `textureCache.cpp`; задеты ханки ручек — нет.
  - textureCache.cpp: 1 прочий наш ханк, места ручек не задеты
- **T188** `img-gpu-alias-write` (А): файлы — `textureCache.cpp`; задеты ханки ручек — нет.
  - textureCache.cpp: 1 прочий наш ханк (трасса TraceWatchedImage рядом), места ручек не задеты
- **T189** `ir-gather-lod` (Г): файлы — `descriptors.cpp`, `Memory.cpp`, `ResourceMaterialization.cpp`; задеты ханки ручек — ResourceMaterialization.cpp: 1 [call-site].
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, §70): overlap задевает наш call-site F19 (overlap 1 [call-site]: переименование StorageMipCount рядом с веткой F19 :587-612); конфликт на месте F19 — при переносе сохранить нашу ветку F19 дословно; descriptors.cpp несёт KYTY_FIX_B42 (Б42, §33; F26/F5CMU не отгружены): ханки с ручкой не задеты, прочих 3; Memory.cpp (B1B/F10) — ханки с ручкой не задеты; tests: задет ханк с F20
- **T192** `img-volume-depth` (Г): файлы — `textureCache.cpp`; задеты ханки ручек — нет.
  - textureCache.cpp: места ручек не задеты (overlap 0/0)
- **T193** `ir-perf-sampler` (Д): файлы — `descriptors.cpp`, `ResourceMaterialization.cpp`; задеты ханки ручек — ResourceMaterialization.cpp: 1 [call-site].
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, §70): overlap задевает наш call-site F19 (overlap 1 [call-site]: удаляет BuildSamplerPlan сразу после FixF19MergeIndirectTables :729); конфликт на месте F19 — при переносе сохранить нашу ветку F19 дословно; descriptors.cpp несёт KYTY_FIX_B42 (Б42, §33; F26/F5CMU не отгружены): ханки с ручкой не задеты, прочих 1
- **T194** `sys-posix-attrstack` (Г): файлы — `pthread.cpp`, `libKernel.cpp`; задеты ханки ручек — нет.
  - pthread.cpp (KYTY_GAME_PATCH) 1 ханк, libKernel.cpp (KYTY_PVAR) 1 ханк — не задеты.
- **T195** `sys-aio` (Г): файлы — `libKernel.cpp`; задеты ханки ручек — нет.
  - libKernel.cpp (KYTY_PVAR): 10 ханков, ханк ручки не задет.
  - libKernel.cpp (KYTY_PVAR): 14 ханков, ханк ручки не задет, 1 наш прочий (метка DiagB32 W:aio в KernelAioWaitRequest).
- **T196** `sys-kernel-timers` (Г): файлы — `libKernel.cpp`; задеты ханки ручек — нет.
  - libKernel.cpp (KYTY_PVAR): 1 ханк, не задет.
- **T199** `prs-resize-zero` (Г): файлы — `window.cpp`; задеты ханки ручек — нет.
  - window.cpp (KYTY_FIX_F24): Resize вне мест JoyPump (overlap 0/0); windowInternal.h — сигнатура
- **T200** `dec-vscnt` (А): файлы — `ShaderDecoder.cpp`, `ShaderDecoder.h`; задеты ханки ручек — нет.
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_F10 (Ф10) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T201** `ir-dispatch-exec` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - tests/ShaderRecompilerComputeTests.cpp: задет 1 ханк с B1B/B26/F10/F19 — только тесты
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 0); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T202** `ir-gpu-written-desc` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 1); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization; тесты: задет наш call-site ханк в tests/shaderCfgTests.cpp (F19/F20/S_REPLAY) — конфликт только в тестах
- **T204** `be-fp64` (Г): файлы — `vulkanWindow.cpp`; задеты ханки ручек — vulkanWindow.cpp: 1 [KYTY_FIX_B26 KYTY_FIX_DUALSRC].
  - vulkanWindow.cpp [KYTY_FIX_B26,KYTY_FIX_DUALSRC,KYTY_FIX_F24,KYTY_FIX_SVAL]: ханков ручки задето 1 [KYTY_FIX_B26 KYTY_FIX_DUALSRC], прочих наших 0; задетый ханк vulkanWindow.cpp — соседний с нашим блоком dualSrcBlend (Б35/Б26); у нас строки shaderFloat64 нет — переносить нечего
- **T208** `ir-material-scan` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 2); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T211** `ir-scalar-native` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 0); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T213** `sys-gpu-descr-sync` (В): файлы — `pipelineCache.cpp`; задеты ханки ручек — нет.
  - pipelineCache.cpp (KYTY_FIX_F20, KYTY_FIX_SVAL, KYTY_S_PCW, KYTY_S_REPLAY): 1 ханк, ханки ручек не задеты, 1 наш прочий; memory.cpp — наш TryReadGpuCleanBacking (memory.cpp:1044) переименован upstream — конфликт.
- **T214** `img-spec-read` (В): файлы — `textureCache.cpp`, `textureCache.h`, `pipelineCache.cpp`; задеты ханки ручек — textureCache.h: 1 [KYTY_FIX_B42].
  - textureCache.h: overlap задевает ханк KYTY_FIX_B42 (объявление рядом); pipelineCache.cpp (KYTY_S_PCW/S_REPLAY/F20/SVAL): 1 прочий ханк, места ручек не задеты; наш kernel/memory.cpp (IsGpuCleanRange) вызывает IsRegionGpuModified — удаление ломает наш свидетель, сохранить нашу функцию
- **T216** `be-narrowsto` (Д): файлы — `descriptors.cpp`, `vulkanWindow.cpp`, `spirvEmitterMemory.cpp`; задеты ханки ручек — нет.
  - descriptors.cpp [KYTY_FIX_B42,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается); vulkanWindow.cpp [KYTY_FIX_B26,KYTY_FIX_DUALSRC,KYTY_FIX_F24,KYTY_FIX_SVAL]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается); spirvEmitterMemory.cpp [KYTY_FIX_B1B,KYTY_FIX_F10]: ханков ручки задето 0, прочих наших 7 (место ручки не пересекается); spirvEmitterMemory.cpp (ручки B1B/F10): задето 7 наших прочих ханков, место ручек — нет; vulkanWindow.cpp: 1 наш ханк
- **T219** `sys-libc-autoload` (В): файлы — `runtimeLinker.cpp`; задеты ханки ручек — runtimeLinker.cpp: 1 [KYTY_GAME_PATCH KYTY_PVAR].
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 1 ханк с ручкой задет (overlap 1): замена PreloadAdjacentPrograms/StartAllModules примыкает к нашему блоку pokes KYTY_GAME_PATCH и PVar::Arm — конфликт, сохранить наш блок после старта модулей.
- **T221** `be-scaledtex` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp [KYTY_FIX_F19]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 1 [KYTY_FIX_F20], прочих наших 1 (тест ручки — сохранить наш тест)
- **T222** `img-10-11-11` (Г): файлы — `CMakeLists.txt`, `textureCache.cpp`; задеты ханки ручек — нет.
  - CMakeLists.txt (KYTY_FIX_B36): новый шейдер тайлера, место ручки не задето; textureCache.cpp: 6 прочих наших ханков (SameBacking, выгрузка/загрузка), места ручек не задеты
- **T223** `img-rebind-order` (Г): файлы — `textureCache.cpp`, `descriptors.cpp`; задеты ханки ручек — нет.
  - descriptors.cpp (KYTY_FIX_B42): 4 прочих наших ханка в RebindImages (bindlap, skipceil), место ручки не задето; textureCache.cpp: 0/0
- **T225** `ir-wg-imgtable` (Г): файлы — `pipelineCache.cpp`, `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 0); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization; pipelineCache.cpp несёт KYTY_FIX_F20 (§126), KYTY_FIX_SVAL (§40), KYTY_S_PCW (§49), KYTY_S_REPLAY (§74): наши ханки с ручкой не задеты, прочих наших задето 1
- **T226** `be-ldsbuf` (Г): файлы — `descriptors.cpp`, `pipelineCache.cpp`, `spirvEmitterMemory.cpp`; задеты ханки ручек — descriptors.cpp: 1 [KYTY_FIX_B42 KYTY_FIX_F26 KYTY_FIX_F5CMU].
  - descriptors.cpp [KYTY_FIX_B42,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 1 [KYTY_FIX_B42 KYTY_FIX_F26 KYTY_FIX_F5CMU], прочих наших 2; pipelineCache.cpp [KYTY_FIX_F20,KYTY_FIX_SVAL,KYTY_S_PCW,KYTY_S_PCW_FORCE_MS,KYTY_S_REPLAY,KYTY_S_REPLAY_TEST]: ханков ручки задето 0, прочих наших 4 (место ручки не пересекается); spirvEmitterMemory.cpp [KYTY_FIX_B1B,KYTY_FIX_F10]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); ShaderRecompilerComputeTests.cpp [KYTY_FIX_B1B,KYTY_FIX_B26,KYTY_FIX_F10,KYTY_FIX_F19,KYTY_FIX_F20,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 1 [KYTY_FIX_B1B KYTY_FIX_B26 KYTY_FIX_F10 KYTY_FIX_F19], прочих наших 0 (тест ручки — сохранить наш тест); конфликт с ханком Б42 (KYTY_FIX_B42) в descriptors.cpp и с 4 нашими ханками pipelineCache.cpp (S_PCW/S_REPLAY/F20/SVAL) — сохранить наши правки
- **T228** `img-2d3d-alias` (Г): файлы — `textureCache.cpp`; задеты ханки ручек — нет.
  - textureCache.cpp: места ручек не задеты (overlap 0/0)
- **T233** `dec-mad-legacy` (А): файлы — `ShaderDecoder.h`; задеты ханки ручек — нет.
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_B26 (Б26б), KYTY_FIX_F10 (Ф10) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T234** `dec-ds-fminmax` (А): файлы — `spirvEmitterMemory.cpp`; задеты ханки ручек — нет.
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_F10 (Ф10) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T235** `hle-trophy` (Г): файлы — `CMakeLists.txt`; задеты ханки ручек — нет.
  - CMakeLists.txt: ручка Ф27 KYTY_FIX_B36 (реестр §84) только в комментарии цели стенда (b3dc9c67:CMakeLists.txt:620); overlap: 2 ханк(ов) upstream, ручкиных задето 0 — место не пересекается
- **T236** `ir-strided-masked` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 2); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T238** `ir-native-int64` (Д): файлы — `spirvEmitterMemory.cpp`; задеты ханки ручек — нет.
  - spirvEmitterMemory.cpp несёт KYTY_FIX_B1B/KYTY_FIX_F10 (Б1б/Ф9/Ф10): ханки с ручкой не задеты, прочих 6; часть BVH upstream живёт в spirvEmitterBvh.cpp, которого у нас нет (наш BVH — в spirvEmitterMemory с ручками) — не применима
- **T239** `img-unmap-drain` (Д): файлы — `textureCache.cpp`, `textureCache.h`, `renderContext.cpp`; задеты ханки ручек — нет.
  - renderContext.cpp (KYTY_FIX_B12): 1 прочий наш ханк UnmapMemory, место ручки не задето; textureCache.cpp/h — места ручек не задеты; commandScheduler.cpp — наш переписанный планировщик (+843 строки)
- **T241** `rnd-depth-bounds-dyn` (Д): файлы — `pipelineCache.cpp`, `pipelineCache.h`, `shaders.cpp`; задеты ханки ручек — pipelineCache.cpp: 1 [call-site].
  - pipelineCache.cpp/.h, shaders.cpp: KYTY_S_PCW, KYTY_S_REPLAY, KYTY_FIX_SVAL, KYTY_FIX_F20, KYTY_FIX_DUALSRC; по overlap.tsv задет 1 наш ханк с вызовом гейта; наш memo draw сравнивает depth_min/max_bounds (renderDraw) - убрать вместе; меняет ключ графического пайплайна (PipelineStaticParameters/хэш) - рецепты precache pipelines.bin и каталог повтора S-replay станут холодными (первый вход каждой сцены), подпись трансляции не меняется
- **T242** `rnd-unbounded-buffers` (Г): файлы — `descriptors.cpp`; задеты ханки ручек — нет.
  - descriptors.cpp: ручка KYTY_FIX_B42 (Б42, FS3) и неотгруженные KYTY_FIX_F26/F5CMU (умолчание 0); ханки upstream задевают 5 наших прочих ханков (FindBuffers переписан под счётчики), ручек не задевают
- **T244** `dec-glc-flat` (Г): файлы — `spirvEmitterMemory.cpp`, `Memory.cpp`; задеты ханки ручек — нет.
  - в задетых файлах ручки KYTY_FIX_B1B (Б1а/Б1б/Ф9), KYTY_FIX_F10 (Ф10) — места наших ханков с ручкой не пересекаются (overlap 0)
- **T245** `ir-nested-selector` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 7 (диагностика отказов MaterializeSnapshot f2de159a1)); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T247** `ir-perf-cleanup` (Д): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 0); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T248** `ir-broad-table` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 1); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T249** `sys-thread-naming` (Г): файлы — `pthread.cpp`; задеты ханки ручек — нет.
  - pthread.cpp (KYTY_GAME_PATCH): 1 ханк, не задет.
  - pthread.cpp (KYTY_GAME_PATCH): 2 ханка, не задеты.
- **T250** `prs-title` (Б): файлы — `hostInput.cpp`, `swapchain.cpp`, `window.cpp`; задеты ханки ручек — hostInput.cpp: 2 [KYTY_FIX_F24].
  - hostInput.cpp: overlap задевает 2 ханка KYTY_FIX_F24 (HostInputWaitEvent с таймаутом) — наш главный цикл и JoyPump; swapchain.cpp — строка UpdateTitle в Present (у нас под !preparing, строка 1050); при переносе сохранить наш асинхронный заголовок (с. 114) и окно ожидания JoyPump
- **T258** `rnd-raw-storage-alias` (А): файлы — `descriptors.cpp`; задеты ханки ручек — нет.
  - descriptors.cpp: ручка KYTY_FIX_B42 (Б42, FS3) и неотгруженные KYTY_FIX_F26/F5CMU (умолчание 0); ханк upstream задевает 2 наших прочих ханка (наш вызов ObtainBuffer с memoizable и bindlean), ручек не задевает - перенос в нашу строку 903
- **T259** `img-array-sync` (Г): файлы — `textureCache.cpp`; задеты ханки ручек — нет.
  - textureCache.cpp: места ручек не задеты (overlap 0/0)
- **T260** `sys-raw-image-sync` (Г): файлы — `descriptors.cpp`; задеты ханки ручек — нет.
  - descriptors.cpp (Б42 KYTY_FIX_B42): 2 ханка задевают 6 наших прочих, ханки ручки не задеты; зависит от 743fdc699 (другая корзина).
- **T263** `rnd-staging-write` (Д): файлы — `bufferCache.cpp`; задеты ханки ручек — нет.
  - bufferCache.cpp/.h: ручка KYTY_FIX_B12 (Б12, FS11) и неотгруженная KYTY_FIX_F5CMU; ханки upstream задевают 1 наш прочий ханк, ручек не задевают
- **T266** `rnd-macos-tid` (Г): файлы — `regionManager.h`; задеты ханки ручек — нет.
  - regionManager.h: ручки KYTY_FIX_B12 (Б12) и KYTY_FIX_B13 (Б13); ханк только ветки __APPLE__ - место не пересекается
- **T268** `sys-dev-random` (Г): файлы — `fileSystem.cpp`; задеты ханки ручек — нет.
  - fileSystem.cpp (Б4, Ф25): 2 ханка в KernelFstat, ханки ручек не задеты.
- **T269** `sys-cloexec` (Г): файлы — `fileSystem.cpp`, `libKernel.cpp`; задеты ханки ручек — нет.
  - fileSystem.cpp (Б4, Ф25): 3 ханка (struct File, KernelOpen, KernelClose), ханки ручек не задеты, 1 наш прочий; libKernel.cpp (KYTY_PVAR) 2 ханка, не задеты.
- **T272** `av-pad-trigger-state` (А): файлы — `controller.cpp`, `controller.h`; задеты ханки ручек — controller.cpp: 3 [KYTY_FIX_B24].
  - controller.cpp: ручки Б24 KYTY_FIX_B24 (реестр §68, PadOutput) и Ф24 KYTY_FIX_F24 (реестр §124, JoyPump); overlap: 12 ханков, задеты 3 наших ханка Б24 (SetTriggerEffect → PadOutput) и 7 прочих; controller.h: 2 ханка, 0. Конфликт: сохранить отправку эффекта через PadOutput (Б24), учёт состояния добавить под m_mutex
- **T277** `av-pad-port-ownership` (В): файлы — `controller.cpp`, `controller.h`; задеты ханки ручек — controller.h: 1 [KYTY_FIX_B24].
  - controller.cpp: ручки Б24 KYTY_FIX_B24 (реестр §68, PadOutput) и Ф24 KYTY_FIX_F24 (реестр §124, JoyPump); overlap: 23 ханка, ручкиных 0, прочих наших 4; controller.h: 2 ханка, задет 1 ханк Б24 — конфликт текстовый, Б24 сохранить
- **T279** `be-descslots` (Д): файлы — `CMakeLists.txt`, `descriptors.cpp`, `shaders.cpp`, `spirvEmitterMemory.cpp`, `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - CMakeLists.txt [KYTY_FIX_B36]: ханков ручки задето 0, прочих наших 1 (место ручки не пересекается); descriptors.cpp [KYTY_FIX_B42,KYTY_FIX_F26,KYTY_FIX_F5CMU]: ханков ручки задето 0, прочих наших 29 (место ручки не пересекается); shaders.cpp [KYTY_FIX_DUALSRC,KYTY_FIX_F20]: ханков ручки задето 0, прочих наших 3 (место ручки не пересекается); spirvEmitterMemory.cpp [KYTY_FIX_B1B,KYTY_FIX_F10]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); ResourceMaterialization.cpp [KYTY_FIX_F19]: ханков ручки задето 0, прочих наших 0 (место ручки не пересекается); shaderCfgTests.cpp [KYTY_FIX_F19,KYTY_FIX_F20,KYTY_S_REPLAY]: ханков ручки задето 1 [KYTY_FIX_F19 KYTY_FIX_F20 KYTY_S_REPLAY], прочих наших 0 (тест ручки — сохранить наш тест); descriptors.cpp: 29 наших ханков рядом с Б42 и 3 ханка shaders.cpp (DUALSRC/F20) — перенос = переписывание наших правок; spirvEmitterBvh.cpp у нас нет (BVH с ручками B1B/F10 — в spirvEmitterMemory.cpp)
- **T280** `ir-srt-alias` (Д): файлы — `CMakeLists.txt`, `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 1); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization; CMakeLists.txt (KYTY_FIX_B36 рядом): ханки с ручкой не задеты
- **T281** `ir-block-cfg` (Д): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 0); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T285** `ir-pred-capture` (Д): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 1); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T286** `ir-scalar-gpu` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 0); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization; тесты: задет наш call-site ханк в tests/shaderCfgTests.cpp (F19/F20/S_REPLAY) — конфликт только в тестах
- **T287** `ir-scalar-matsel` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 2); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization; тесты: задет наш call-site ханк в tests/shaderCfgTests.cpp (F19/F20/S_REPLAY) — конфликт только в тестах
- **T289** `img-tiling-refactor` (Д): файлы — `CMakeLists.txt`, `textureCache.cpp`, `textureCache.h`, `descriptors.cpp`, `videoOut.cpp`; задеты ханки ручек — textureCache.h: 1 [KYTY_FIX_F26 KYTY_FIX_F5CMU].
  - textureCache.h: overlap задевает ханк KYTY_FIX_F26/KYTY_FIX_F5CMU (объявления); textureCache.cpp 23 и descriptors.cpp (KYTY_FIX_B42) 11 прочих наших ханков; videoOut.cpp (KYTY_PVAR): ImageInfo буферов видеовывода, хуки P-var не задеты; CMakeLists (KYTY_FIX_B36): новые файлы
- **T293** `prs-splash` (Г): файлы — `emulator.cpp`; задеты ханки ручек — нет.
  - emulator.cpp (KYTY_FIX_F20/F21/KYTY_GAME_PATCH): строка в Init, места ручек не задеты (1 прочий наш ханк); заставка по умолчанию меняет первые показанные кадры — для видео-харнессов (KYTY_REC) держать выключенной
- **T294** `prs-back-touch` (Г): файлы — `window.cpp`; задеты ханки ручек — нет.
  - window.cpp (KYTY_FIX_F24): ветка кнопок GameEventController (SDL3), место JoyPump не задето (overlap 0/0)
- **T300** `ir-srt-jit` (Д): файлы — `CMakeLists.txt`, `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 0); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization; CMakeLists.txt (KYTY_FIX_B36 рядом): ханки с ручкой не задеты
- **T301** `prs-depth2color` (Г): файлы — `graphicContext.h`, `vulkanWindow.cpp`; задеты ханки ручек — graphicContext.h: 1 [KYTY_FIX_DUALSRC KYTY_FIX_SVAL].
  - graphicContext.h: overlap задевает ханк KYTY_FIX_DUALSRC/KYTY_FIX_SVAL (соседнее поле структуры) — тривиальный конфликт, сохранить наши поля; vulkanWindow.cpp: 2 прочих наших ханка рядом с цепочкой возможностей, места ручек не задеты
- **T303** `sys-loadexec` (Г): файлы — `CMakeLists.txt`, `runtimeLinker.cpp`; задеты ханки ручек — runtimeLinker.cpp: 1 [KYTY_GAME_PATCH KYTY_PVAR].
  - runtimeLinker.cpp (KYTY_GAME_PATCH, KYTY_PVAR — блок pokes и PVar::Arm в Execute, стр. 1542–1577): 1 ханк с ручкой задет (overlap 1) и 6 прочих: EntryParams/argv в Execute рядом с нашим блоком pokes/PVar::Arm — конфликт, сохранить наш блок.
  - CMakeLists.txt (Ф27): 1 ханк, не задет.
- **T304** `img-cmp-depth-dcc` (В): файлы — `textureCache.cpp`, `descriptors.cpp`; задеты ханки ручек — textureCache.cpp: 1 [KYTY_FIX_F5CMU].
  - textureCache.cpp: overlap задевает ханк KYTY_FIX_F5CMU (DecodeColorClear/MaterializeColorClear — у нас PrepareDccClear); descriptors.cpp (KYTY_FIX_B42): 1 прочий ханк, место ручки не задето
- **T305** `ir-shared-pred` (Г): файлы — `ResourceMaterialization.cpp`; задеты ханки ручек — нет.
  - ResourceMaterialization.cpp несёт KYTY_FIX_F19 (Ф19, реестр §70): по overlap наши ханки F19 не задеты (задето прочих наших: 1); при переносе сохранить FixF19Enabled/FixF19ManualDepthCompare/FixF19MergeIndirectTables в BuildResourceSpecialization
- **T306** `ir-texoffset` (А): файлы — `Memory.cpp`; задеты ханки ручек — нет.
  - Memory.cpp несёт KYTY_FIX_B1B/KYTY_FIX_F10 (Б1б/Ф9/Ф10): ханки с ручкой не задеты (меняются только IMAGE_SAMPLE/IMAGE_GATHER); spirvEmitterImage.cpp ручек не несёт, но задевает наш manual_dref (:640, :703)
- **T307** `sys-hdr` (Г): файлы — `CMakeLists.txt`, `videoOut.cpp`, `swapchain.cpp`, `vulkanWindow.cpp`; задеты ханки ручек — swapchain.cpp: 3 [KYTY_FIX_MINIMIZE].
  - swapchain.cpp (Б37 KYTY_FIX_MINIMIZE, Б35 KYTY_FIX_DUALSRC): 16 ханков задевают 3 наших ханка с KYTY_FIX_MINIMIZE и 11 прочих — конфликт, сохранить проверку нулевого размера окна Б37; videoOut.cpp (KYTY_PVAR): 9 ханков, ханк ручки не задет, переписан PrepareFlip рядом с нашим хуком флипа; vulkanWindow.cpp: 1 ханк, не задет; CMakeLists.txt: 1 наш прочий.
- **T308** `sys-ftruncate` (Г): файлы — `libKernel.cpp`; задеты ханки ручек — нет.
  - libKernel.cpp (KYTY_PVAR): 1 ханк, не задет.
- **T311** `img-guestgpu-simplify` (В): файлы — `textureCache.cpp`; задеты ханки ручек — нет.
  - textureCache.cpp: ханк ProcessDownloadImages вне мест ручек (0/0); graphicsRun.cpp/sync.cpp/render.h — не файлы ручек, но наш graphicsRun.cpp переписан (+2 787 строк)
- **T312** `img-bc-alias-gc` (В): файлы — `textureCache.cpp`, `textureCache.h`; задеты ханки ручек — нет.
  - textureCache.cpp/h: 4+3 прочих наших ханка (FindImage, ResolveOverlap, GC), места ручек не задеты; graphicsRun.cpp — наш переписанный

## 7. Член (4): подпись трансляции

Тем, меняющих набор подписи трансляции (`src/graphics/shader/**` и три заголовка + `shaderTranslationCache.cpp`), — 112 (коммитов — 225).
Перенос любой из них меняет подпись `KYTY_SHADER_SOURCE_HASH` — холодный каталог трансляции у пользователя, прогрев (п. 418(в)); каталоги
`_ShaderSeeds` и повтора S-replay собраны на подписи `9177b426…` — тоже холодные до пересборки. По классам:

- **А** (8): T032, T113, T200, T203, T233, T234, T257, T306
- **Б** (5): T010, T014, T021, T046, T240
- **В** (14): T005, T007, T016, T019, T069, T107, T114, T135, T138, T156, T169, T179, T237, T255
- **Г** (56): T003, T025, T026, T033, T037, T048, T049, T057, T060, T068, T072, T073, T084, T085, T087, T099, T103, T111, T112, T120, T130, T140, T170, T171, T172, T180, T184, T186, T189, T190, T201, T202, T204, T206, T207, T208, T209, T211, T215, T217, T221, T222, T225, T226, T227, T236, T244, T245, T248, T256, T286, T287, T291, T303, T305, T307
- **Д** (29): T075, T080, T081, T082, T083, T086, T089, T102, T119, T142, T152, T175, T176, T181, T183, T193, T212, T216, T238, T247, T278, T279, T280, T281, T282, T283, T285, T289, T300

Отдельно (не подпись трансляции, но ключ пайплайна — рецепты precache и каталог S-replay холодные после переноса, по строкам помощников):
T020 `rnd-mrt-exported`, T046 `be-dualsrc`, T109 `prs-depth-clamp`, T152 `rnd-pipeline-key-compact`, T156 `rnd-blend-swizzle-alpha`, T174 `rnd-pipeline-blend-normalize`, T226 `be-ldsbuf`, T241 `rnd-depth-bounds-dyn`, T256 `be-snorm16exp`.

## 8. Член (5): upstream #883 и трава Sky Garden (п. 633(д))

Полный разбор — `m883.md` (якоря проверены). Кратко [c кода, I вывода]:

1. #883 = `0791f921f` «UFC 5 in-game» (34 файла, +3 226 / −2 265). Маска цвета — только в `renderDraw.cpp`: `DrawHasActivePixelShader` →
   `DrawColorOutputMask` (бит слота — только при `SPI_SHADER_COL_FORMAT[slot] != 0` и слоте в `CB_TARGET_MASK & CB_SHADER_MASK`), от неё
   `ps_active`, отображение экспорта и `mrt_mask &= color_output_mask` — вложение привязывается только при ненулевом формате (эта строка
   теряет траву в форке `BryanKAdams/BryKytyPS5` после их слияния `585fc13f`). Остальное в #883: граница сэмплера int/float (р2), сброс
   денормалей во входах `V_CMP_*_F32` (р3), границы `DS_APPEND/CONSUME` (р4), выравнивание скалярных чтений (р5), переписанный CFG и
   `ConditionRef` (р6, основная масса), отладочный дамп (р7), косметика эмиттера (р8).
2. У нас (`b3dc9c67`): вложения привязываются по маске целей и базе (`renderDraw.cpp:3014`), активность PS — по `CB_TARGET_MASK &
   CB_SHADER_MASK` (`:2649`), условия «формат слота ≠ 0» нет ⇒ механизма потери травы у нас нет; правило привязки проверено данными (Ф6
   `НЕ ДЕФЕКТ`, реестр §59: `bound_missing` = `bound_extra` = 0 на Sky Garden). Оговорка: счётчик Ф6 читает `CB_COLORn_INFO.FORMAT`, не
   `SPI_SHADER_COL_FORMAT`.
3. Правка форка `26d62f80` возвращает привязку по маске записи (`DrawColorWriteMask`) — по сути наше нынешнее поведение; форматная маска
   upstream остаётся только для `ps_active` и отображения экспорта. Если логику #883 переносить, `26d62f80` обязательна; ханки #883 стоят на
   upstream `b594f8c83`(б), на наш код не ложатся; менять согласованно все три вызова `DrawHasActivePixelShader` (`:3034`, `:3634`, `:3676`).
   С Б35 совместима; конфликт с Б35 — только при переносе `649367472`, `21a1346e2` или `73615c31f`.
4. Класс #883 — **В** (неоднороден): р1 Б, р2–р4 кандидаты А без довода исполнения (р2) или с исполнением опкода (р3 `VOPC:1` 24 607
   инструкций, р4 `DS:3e` в 239 программах) — U, р5–р6 В, р7 Г, р8 Д. **Член M1c/M3 при переносе #883 или его р1:** V Sky Garden
   (`underwater_aerial_garden`) в форме `fs15_v` и пара листов с `fs15_v` — средняя трава у тропы на тех же кадрах; положительный контроль —
   сборка без `26d62f80` обязана потерять траву (иначе лист не детектор); W Sky Garden и W `mini_giants_garden` с 0 `[Vulkan][E]`; для
   `21a1346e2` — сначала замер на Sky Garden (draw, где номер слота по `CB_SHADER_MASK` ≠ номеру экспорта; экспорты в слот с нулевым
   `COL_FORMAT`).
5. Связанные upstream-коммиты маски цвета: `b594f8c83` (`T020`, В: (а) сохранение слотов — Б, наш `d844f4cb2`; (б) привязка по экспорту
   PS — В), `649367472` (`T046`, Б — наш Б35, вместе брать нельзя), `73615c31f`/`0bef3fc0d` (`T156`, В, U), `21a1346e2` (`T255`, В, U),
   `b96871e2b` (SNORM16-экспорт, Г [c]: в 5 866 PS-рецептах четырёх `pipelines.bin` режимы целей только 1 и 4).

## 9. Член (6): тесты upstream, применимые без кода

Полный разбор — `tests.md` (статически, [I]: пробной сборки не было). Общие преграды: upstream на SDL3 (у нас SDL2), сигнатура
`SrtMemoryReader` (`std::span` против `uint32_t*`), свой харнесс `Check`/`KYTY_TESTS_CONTINUE` — изменённые файлы целиком не переносятся,
переносятся отдельные функции.

- Новые файлы (15): без кода и годен — только `LruCacheTests.cpp`; компилируются, но вне игры или с ожидаемым провалом — `CesTests.cpp`,
  `HttpUriParseTests.cpp`, `SaveDataDialogTests.cpp`; остальные 11 не переносятся (нет `common/archive.h`, `trophies.h`, `ngs2.cpp`,
  `libPngEnc.cpp`, `dualSense*`, `guestInstructionPatcher.h`; SDL3).
- **Кандидаты в гейт `shader_cfg_tests`** (перенос функции в `tests/shaderCfgTests.cpp`, код не меняется; каждому нужен прогон):
  `TestDsFloatMinMaxDecoder` (DS_MIN/MAX_F32 — путь игры, см. `T234`), `TestShaderStageBarriers` (S_BARRIER — 66 программ),
  `TestVertexBufferGrouping`, `TestSpirvRepeatedEmission`, `TestU64RegisterPairRoundTrip`, `TestShaderFeatureCollection`,
  `TestRayTracingInstructions` (после правки члена теста: у нас BVH64 — отдельный опкод `IMAGE_BVH64_INTERSECT_RAY`). Условно — 6
  CFG-тестов `…Cfg…Structured` и `TestNggVertexEntryState`. Из 47 новых функций `shaderCfgTests.cpp` без кода переносятся 22.
- GPU-кандидаты (`shader_recompiler_compute_tests`, ≈ 30 `TestCase` на опкодах, которые игра исполняет) и прочие цели — `tests.md` §5.2.
- Пробы (провал на `b3dc9c67` ожидаем — сигнал для M1c, не гейт): `VectorMadF32RoundsProduct`/`VectorMadF32FlushesDenorms` (`T233`),
  `BvhIntersections` (расхождения решать по GPURT, не по upstream; тройки типов 2–3 фикстуры совпадают с нашим Ф10), CPU-пробы выбора
  дескриптора по ветви, AudioOut2 (`T125`).

## 10. Все темы

| № | ключ | класс | ув. | коммиты | название | основание | подп. | файлы ручек |
|---|---|---|---|---|---|---|---|---|
| T001 | `rnd-pm4-chain` | Г | U | `79120d53` | Цепочки PM4 (бит CHAIN) без рекурсии | `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:2843` | нет | — |
| T002 | `prs-key-l2r2` | Г | c | `7af28c26` | Клавиши Z/C → L2/R2 | — | нет | `hostInput.cpp` |
| T003 | `dec-sdwa-accept` | Г | I | `acd7435d` `cfb110e0` `cfb8f7b2` `6a9ae4ae` `cda236db` `d890bb19` `1d41ddb3` `60e53a39` `9f25e3c2` `2f4b8a33` `2f4d0f38` | Расширение допустимых форм SDWA/модификаторов декодера | `b3dc9c67:docs/track-f/f23a/cmp_eboot.out.txt:3` | да | — |
| T004 | `av-linux-ffmpeg` | Г | c | `9cf7963f` | Системный FFmpeg на Linux | platform:Linux | нет | `CMakeLists.txt` |
| T005 | `ir-baryc` | В | c | `0d9e95d9` `3ba6ebae` | Барицентрики PS: centroid/sample | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:1207` | да | — |
| T006 | `rnd-zpass-pred` | Г | I | `629ae1ac` | Предикация по Z-pass (op 1) и ожидание запросов | `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3083` | нет | — |
| T007 | `be-psalias` | В | I | `441367b1` `b38b7454` | Псевдонимы входов PS (общий offset SPI_PS_INPUT_CNTL) и flat при провоцирующей вершине | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterModule.cpp:487` | да | `pipelineCache.cpp` |
| T008 | `bld-ci` | Г | c | `e6156bef` `0627e23e` `6c03b4aa` `fd2e15ee` | CI и окружение разработки | diff: только .github/workflows | нет | — |
| T009 | `sys-amdcpu-patch` | Г | I | `957452d6` `77680ce9` `86e5e014` `349fae00` `4e6f4f99` `b11aea80` `a4d26cf8` `19a9464b` `ab98fb1f` `35c6e8ff` | Патчер инструкций AMD CPU (VRSQRTPS/SSE4a/INSERTQ/RDPID/CLWB, красная зона) для хостов не-AMD | git grep amd_cpu/AmdCpu b3dc9c67 -- src = 0 строк; хост AMD Zen 5 | нет | `CMakeLists.txt`, `runtimeLinker.cpp` |
| T010 | `dec-ngg-fan` | Б | c | `7c9148dd` | NGG GS: треугольные веера | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:1118` | да | — |
| T011 | `sys-json2` | Б | c | `32e6a433` `eda6ba37` | Json2: числовые геттеры и итераторы массива | `b3dc9c67:src/libs/libJson2.cpp:878` | нет | — |
| T012 | `sys-fiber-ownership` | В | I | `71f52f9d` `ded69649` | Волокна: владение, перенос между потоками, малые стеки | `b3dc9c67:src/libs/libKernel.cpp:2774` | нет | `libKernel.cpp` |
| T013 | `sys-build-ffmpeg` | Г | c | `9b2111dc` | Сборка: FFmpeg подмодулем | — | нет | — |
| T014 | `dec-cdbg-nop` | Б | c | `5b541375` | S_CBRANCH_CDBG* как пустая ветвь (опкод игры) | `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/ScalarAluOps.cpp:116` | да | `ShaderDecoder.cpp`, `ShaderDecoder.h` |
| T015 | `sys-nix` | Г | c | `10cae50b` | Nix flake и dev shell | — | нет | — |
| T016 | `ir-descphi` | В | I | `af3a3f4b` `bc45aaf6` `5d1ad31c` `488c0aca` | Дескриптор из Phi равномерной ветви -> host Select | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ResourceTracking.cpp:249` | да | `ResourceMaterialization.cpp` |
| T017 | `rnd-zero-dispatch` | Д | I | `c1dccd7d` | Пропуск нулевых dispatch до подготовки шейдера | `b3dc9c67:src/graphics/host_gpu/renderer/renderCompute.cpp:1038` | нет | — |
| T018 | `img-miptail-views` | В | U | `8589731a` | Мип-хвост PS5: виды T# с уровнями сверх ресурса | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3014` | нет | `textureCache.cpp`, `descriptors.cpp` |
| T019 | `dec-cfg-early-return` | В | I | `fb94a819` | CFG: слияние выбора с ранним return | `b3dc9c67:src/graphics/shader/recompiler/frontend/cfg/ShaderCFG.cpp:1359` | да | — |
| T020 | `rnd-mrt-exported` | В | I | `b594f8c8` | Привязка только экспортируемых цветовых целей, слоты MRT сохраняются | `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:3014` | нет | `pipelineCache.cpp` |
| T021 | `img-tsharp-minlod` | Б | c | `f38d738e` | T# MIN_LOD через VK_EXT_image_view_min_lod | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:1952` | да | `descriptors.cpp`, `vulkanWindow.cpp` |
| T022 | `rnd-mesh-restart` | Г | I | `63fb822f` | Mesh-draw с primitive restart: предупреждение вместо фатала | `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:4109` | нет | — |
| T023 | `sys-agc-cb-capacity` | А | U | `49b2eedd` | AGC CommandBuffer: расчёт свободного места со знаком | `b3dc9c67:src/libs/agc.cpp:267` | нет | — |
| T024 | `rnd-depth-flags` | Г | I | `fa913ec1` `a98a39c5` | Флаги глубины EXPCLEAR / partially_resident без фатала | `b3dc9c67:src/graphics/host_gpu/renderer/depthRenderTarget.cpp:169` | нет | — |
| T025 | `dec-op-unused` | Г | I | `e0ecffed` `f30afc18` `4b776865` `394e6389` `5b7d3343` `ea6aae85` `54949557` `fc86509a` `3dc3fd01` `e43c2426` `5a705dd1` `ff546085` `cf268af8` `16b83a03` `0a5774be` `35c4dca2` `6799ecbc` `bc193f52` `581dad7d` `0d0b215f` `b3e419ff` `284d58d1` `b8946fef` `c17fa5b9` `98557a83` `8274e517` `2b1b7ed0` `1d552724` `7a0e1daf` `5601861d` `1195af25` `7492cb95` `bb98f264` `5af370c2` `26cce990` `96eb681b` `9e666e4d` `7881c69a` `1fc520cd` `1bd282ec` `a31e2cd3` `bb5edbd4` `59183dbf` `d247d3d6` `fa56c5ea` | Новые опкоды, которых игра не исполняет | ophist:MIMG:44=0 | да | `graphicContext.h`, `descriptors.cpp`, `vulkanWindow.cpp`, `spirvEmitterMemory.cpp`, `ShaderDecoder.cpp`, `ShaderDecoder.h`, `Memory.cpp`, `ResourceMaterialization.cpp` |
| T026 | `dec-swappc` | Г | c | `235e24d4` `1818aae5` `3e9f88bf` | SWAPPC: передача управления и leaf-вызовы | ophist:SOP1:21=0; register:§11:Б26а | да | `pipelineCache.cpp`, `ShaderDecoder.cpp`, `ShaderDecoder.h`, `ResourceMaterialization.cpp` |
| T027 | `img-stencil-assoc` | Г | U | `47957faa` `d8a44124` `9860c2bb` `068d7621` | Ассоциация трафарета с образом глубины (выгрузка, очистка, диапазон) | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:2411` | нет | `textureCache.cpp`, `textureCache.h` |
| T028 | `rnd-log-launcher` | Г | c | `228cf3fb` | Лаунчер на Qt < 6.6 и предел строки лога reference clock | `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:621` | нет | — |
| T029 | `av-motion` | В | c | `ce629e03` `b7a1fac8` | Датчики движения пада (гироскоп, акселерометр) | `b3dc9c67:src/libs/controller.cpp:705` | нет | `window.cpp`, `controller.cpp`, `controller.h` |
| T030 | `lch-launcher` | Г | c | `de1545e1` `a6144f79` `e930657b` `ada05140` `f1f930e0` `9313a088` `7d2422ab` `9a5658c0` `7da3c4ed` `448a4c8a` | Лаунчер (Qt) | diff: src/launcher и README | нет | — |
| T031 | `sys-printf-negprec` | А | U | `bab1c361` | guestPrintf: отрицательная динамическая точность | `b3dc9c67:src/libs/guestPrintf.cpp:530` | нет | — |
| T032 | `be-fmtstore` | А | I | `c66d977c` `a6248c7c` `81f31263` `de9c15fa` | Кодирование форматных буферных записей BUFFER_STORE_FORMAT (SNORM/UNORM/FLOAT16/SCALED, упакованные) | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp:1773` | да | `spirvEmitterMemory.cpp` |
| T033 | `av-refactor-magic-enum` | Г | c | `cc8e0238` | Удаление обёрток magic_enum | diff: меняются только аргументы LOGF/EXIT | да | `ShaderDecoder.h`, `audio.cpp`, `runtimeLinker.cpp` |
| T034 | `sys-refactor-strings` | Г | I | `2bf78a94` | Рефакторинг: удаление строковых обёрток | — | нет | `fileSystem.cpp`, `runtimeLinker.cpp` |
| T035 | `hle-launcher-cleanup` | Г | c | `218e7200` | Чистка лаунчера | diff: только src/launcher и utils.cmake | нет | — |
| T036 | `hle-refactor-runtime` | Г | c | `1211958b` | Чистка вспомогательного кода рантайма | diff: эквивалентные замены и удаление неиспользуемого кода | нет | `pthread.cpp`, `libKernel.cpp` |
| T037 | `dec-refactor` | Г | I | `5dc644ed` `3585cd8f` | Рефакторинг без изменения поведения | — | да | `swapchain.cpp`, `vulkanWindow.cpp`, `window.cpp`, `ShaderDecoder.cpp`, `Memory.cpp` |
| T038 | `sys-refactor-vm` | Г | I | `5b2935e3` | Рефакторинг: удаление лишнего слоя виртуальной памяти | — | нет | — |
| T039 | `hle-refactor-bytebuffer` | Г | c | `697b18b3` | ByteBuffer → std::vector | diff: замена контейнера | нет | — |
| T040 | `sys-refactor-helpers` | Г | I | `c5cebc1d` | Рефакторинг: удаление неиспользуемых помощников | — | нет | `pthread.cpp` |
| T041 | `rnd-tile-exitmsg` | Г | c | `6cfde37e` | Текст фатала формата тайла без fmt и строка меню лаунчера | — | нет | — |
| T042 | `rnd-winbuild-membarrier` | Г | c | `104530ea` | Сборка Windows: #undef MemoryBarrier в regionManager.h | `b3dc9c67:src/graphics/host_gpu/regionManager.h:25` | нет | `regionManager.h` |
| T043 | `hle-np-signin` | Г | c | `87b4417a` | NP: колбэк состояния входа | nid:qQJfO8HAiaY нет в бинарях игры (NID-поиск строк «NID#» в eboot.bin и sce_module/*.prx игры) | нет | — |
| T044 | `hle-net-errno` | Г | U | `57c5b206` | libnet: код errno | `b3dc9c67:src/libs/network.cpp:3143` | нет | — |
| T045 | `hle-net-sockets` | Г | c | `cbedf570` `44798085` `e7f63270` `48527210` `e679486e` `861dd76d` | Сокеты libnet (UDP, опции, recv, экспорт) | `b3dc9c67:src/libs/network.cpp:3143` | нет | — |
| T046 | `be-dualsrc` | Б | c | `64936747` | Двухисточниковое смешивание (dual-source blend) | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/shaders.cpp:345` | да | `pipelineCache.cpp`, `vulkanWindow.cpp` |
| T047 | `img-bc-storage-usage` | Г | I | `165234b1` `c2b7b0b5` `539c0f7b` | Использование storage у блочных (BC) образов | `b3dc9c67:src/graphics/host_gpu/renderer/image/image.cpp:54` | нет | — |
| T048 | `dec-dpp8` | Г | c | `bfc8cd0e` `b27b89f5` `3b9e176b` | DPP8 (перемещения, VOP2, fetch-inactive) | ophist:dpp8=0 (все семейства) | да | `ShaderDecoder.cpp`, `ShaderDecoder.h`, `Memory.cpp` |
| T049 | `dec-int16-neg` | Г | I | `95d3d9d3` | NEG 16-битных операндов (знаковый бит) | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:545` | да | — |
| T050 | `av-ngs2-ajm` | Г | c | `007d7ea2` `1d2f59df` `303a0203` `82b2711c` `e40438f9` `3742ad99` `fc04db75` `2165c710` `83628a43` `1cc0ac7e` `f7ae6e0a` `5ce4f083` `7c8583d2` `a20b64d3` `b10bd53d` | NGS2/AJM/ATRAC9/AAC/Opus (игра не импортирует) | nid:Ngs2=0/27,Ajm=0/32,Audio3d=0/7,AudioOut(v1)=0/7 (LIB_FUNC b3dc9c67:src/libs/libAudio.cpp; NID-поиск строк «NID#» в eboot.bin и sce_module/*.prx игры) | нет | `CMakeLists.txt`, `audio.cpp`, `libAudio.cpp` |
| T051 | `hle-net-pool` | Г | c | `ba1854bb` | libnet: обход пулов при выходе | diff: только Net::Shutdown | нет | — |
| T052 | `av-pad-misc-stubs` | Г | c | `f100f785` | Новые заглушки Pad/GameLiveStreaming | nid:fCWdlnmB1Ks,lK8dLBNp9OE,yeQKjHETi40 нет в бинарях игры (NID-поиск строк «NID#» в eboot.bin и sce_module/*.prx игры) | нет | `controller.cpp`, `controller.h` |
| T053 | `sys-native-paths` | Г | c | `001dfea5` `b61b3f2a` `07c9978a` `8b294eb5` `fe45265f` | Нативные/Unicode пути Windows | пакет игры: 0 не-ASCII имён из 158 205, наибольшая длина пути 181 (< 260); папка эмулятора ASCII | нет | `window.cpp`, `fileSystem.cpp` |
| T054 | `sys-savedata-persist` | В | I | `cfbaee07` `569ec04d` | SaveData: постоянное сохранение SaveDataMemory2, раскладка по user_id, метаданные | `b3dc9c67:src/libs/libSaveData.cpp:335` | нет | `CMakeLists.txt` |
| T055 | `av-avplayer-state` | А | I | `35a275e9` `6b79b7a0` `fa51da4d` `12ff5716` `d792dfa8` | AvPlayer: состояния, события, пауза/переход, режим синхронизации | `b3dc9c67:src/libs/avPlayer.cpp:1817` | нет | — |
| T056 | `sys-userservice-name` | Г | I | `8d66c4ef` | UserService: GetUserName для чужого user_id | `b3dc9c67:src/libs/libUserService.cpp:95` | нет | — |
| T057 | `ir-srteval-scmp` | Г | I | `102a10f0` | Вычислитель SRT: знаковое сравнение | register:§104:Ф3 | да | — |
| T058 | `sys-tess-optional` | В | I | `a849f253` | Тесселяция по опции (по умолчанию patch-draw пропускаются) | `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:2566` | нет | — |
| T059 | `av-avplayer-aspect` | А | U | `25f26995` | AvPlayer: соотношение сторон видео | `b3dc9c67:src/libs/avPlayer.cpp:1408` | нет | — |
| T060 | `rnd-rectlist-legacy` | Г | U | `0ad9149c` | Прямоугольники RectListLegacy из трёх вершин через патч-лист | `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:3198` | да | `pipelineCache.cpp` |
| T061 | `sys-win-cacheflags` | Г | c | `b8ad1d8c` | Windows: флаги кэша CreateFileW | `b3dc9c67:src/common/platform/sysWindowsFileIO.cpp:58` | нет | — |
| T062 | `sys-refactor-findfiles` | Г | I | `c3cc8454` | Удаление рекурсивного перебора файлов | — | нет | — |
| T063 | `bld-cmake` | Г | c | `d7da2444` `fe4f9423` `96874909` `9d4da483` `8cbee7f4` `1f3adf51` | CMake и упаковка | diff: CMakeLists и CI | нет | `CMakeLists.txt` |
| T064 | `av-host-window-ux` | Г | c | `81af1301` `feeced81` | Хоткеи и курсор окна хоста | diff: хоткей хоста и лаунчер | нет | `hostInput.cpp`, `window.cpp` |
| T065 | `rnd-cx-24a` | Г | I | `c997cdb8` | Пропуск нулевой записи косвенного CX 0x24a | `b3dc9c67:src/graphics/guest_gpu/command_processor/pm4Handlers.cpp:2106` | нет | — |
| T066 | `rnd-storage-cube` | Г | I | `ba55ba5d` | Storage-доступ к частичным кубическим видам | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:1188` | нет | `descriptors.cpp` |
| T067 | `prs-out-res` | Г | c | `61761b65` | Разрешение вывода по ATTRIBUTE3 | `b3dc9c67:src/graphics/presentation/videoOut.cpp:4183` | нет | `videoOut.cpp` |
| T068 | `be-barrier` | Г | U | `f9e56ef8` | Барьер рабочей группы только в стадиях с общим выполнением | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterFlow.cpp:595` | да | — |
| T069 | `dec-ngg-launch` | В | I | `476204cd` `cf77fb43` | NGG passthrough: состояние запуска s2/s3 | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:1258` | да | `pipelineCache.cpp` |
| T070 | `rnd-fmask-msaa` | Г | I | `bf4dcdce` | FMASK с нативным MSAA без фатала | `b3dc9c67:src/graphics/host_gpu/renderer/debug.cpp:222` | нет | — |
| T071 | `rnd-attach-samples` | Г | I | `d3c182f3` | Проверка числа сэмплов вложений до захвата целей | `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:2442` | нет | — |
| T072 | `be-gpubuf` | Г | U | `b2a80a3a` `429d0af6` `b4d32394` `a55a2838` `5f01308b` `919c058f` `8b05b673` `3ba0e971` `33e74cab` | Буферные дескрипторы, выбранные на ГП (IndirectBuffer), вместо отказа трансляции | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ResourceTracking.cpp:589` | да | `descriptors.cpp`, `spirvEmitterMemory.cpp`, `ResourceMaterialization.cpp`, `ResourceMaterialization.h` |
| T073 | `ir-scalarchain-img` | Г | I | `d2df2cad` | T# через цепочку скалярных буферов | register:§104:Ф3 | да | — |
| T074 | `rnd-depth-meta-bits` | Г | I | `7c9e18e7` | Неактивные биты адреса метаданных в дескрипторе глубины | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:1117` | нет | `descriptors.cpp` |
| T075 | `ir-perf-remap` | Д | c | `4b074cf9` | Скорость: перестановка образов без кучи | — | да | `ResourceMaterialization.cpp` |
| T076 | `rnd-logs-quiet` | Г | c | `a6a56c8a` `8252caee` `4428640b` `42a315f0` | Журнал: убраны и приглушены строки draw/dispatch/BDA | `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3167` | нет | `renderContext.cpp` |
| T077 | `sys-savedata-search` | Г | c | `8dc9b9d5` | SaveData: ёмкость для Mount3/DirNameSearch/GetMountInfo | imports: sceSaveDataDirNameSearch (dyIhnXq-0SM, X4MYzukPc3g, PHnuI4LhuRk), GetMountInfo (65VH0Qaaz6s), Mount3 (ZP4e7rlzOUk) = 0 | нет | — |
| T078 | `sys-perf-dirnames` | Д | c | `8b095cae` | Перенос имён элементов каталога без копии | — | нет | — |
| T079 | `rnd-storage-mip` | В | I | `90471836` `041874f6` | Число уровней storage-вида и терминальные mip-виды | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3005` | нет | `descriptors.cpp` |
| T080 | `ir-perf-srteval` | Д | c | `d6dac92d` | Скорость вычислителя SRT | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/SrtWalker.cpp:2354` | да | — |
| T081 | `ir-refresh-onewalk` | Д | I | `13fcb3a1` | Обновление кэша ресурсов одним обходом SRT | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/SrtWalker.cpp:2354` | да | `descriptors.cpp`, `pipelineCache.cpp`, `ResourceMaterialization.cpp`, `ResourceMaterialization.h` |
| T082 | `dec-perf` | Д | I | `03c55e57` `cf423df6` `b43bf9f7` `e57c37fa` `64eea6b3` `7c6121cb` | Скорость/память без изменения ответа | — | да | `pipelineCache.cpp`, `shaders.cpp` |
| T083 | `be-spvsize` | Д | c | `8a5e5c54` `f29bd0fe` `71017416` `46997dfc` `8abf99c5` `b4853a0e` `13e3ca31` | Сжатие эмитируемого SPIR-V и памяти эмиттера (тот же ответ) | — | да | `spirvEmitterMemory.cpp` |
| T084 | `be-indimg` | Г | U | `eb8a5504` `3b89e36d` `a670dc84` `843b5778` `cd066010` `ae1e9262` `71c72617` `8c813865` `4c87dbeb` | Косвенные таблицы образов/сэмплеров (indirect image tables, ключи материалов) | register:§45:Ф22 | да | `vulkanWindow.cpp`, `ResourceMaterialization.cpp` |
| T085 | `ir-scalar-imgtable` | Г | I | `66f1a823` | Скалярные таблицы образов при планировании | register:§104:Ф3 | да | `ResourceMaterialization.cpp` |
| T086 | `ir-perf-span` | Д | I | `d30dca78` | Скорость: чтение дескрипторов одним отрезком | — | да | `pipelineCache.cpp`, `ResourceMaterialization.cpp` |
| T087 | `ir-tdesc-valid` | Г | U | `ef83ba65` `5ed5fdd3` | Проверка полей T# (резервные биты) | — | да | `ResourceMaterialization.cpp` |
| T088 | `rnd-dispatch-indirect-gpu` | Б | c | `79530b4c` | Число групп косвенного dispatch читается ГП | `b3dc9c67:src/graphics/guest_gpu/command_processor/pm4Handlers.cpp:1360` | нет | — |
| T089 | `rnd-cp-hotpath` | Д | I | `d6b2abe2` `d646fd92` | Горячий путь CP: лишние проверки | `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3438` | да | — |
| T090 | `rnd-readback-staging` | Г | I | `3fad77fd` `18a5f04d` | Крупные readback: буфер выгрузки 64 МиБ и временный буфер | `b3dc9c67:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:561` | нет | `bufferCache.cpp` |
| T091 | `tst-dlring` | Д | U | `ee3749d9` | Тест кольца выгрузки 64 МиБ (к теме 3fad77fd8) | `b3dc9c67:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:561` | нет | — |
| T092 | `hle-kernel-imports` | Г | c | `b5ba482f` | Недостающие импорты ядра и старта | nid:yTj62I7kw4s,mBd4AfLP+u8,kP2L8t3j-aM,5LiMEPuW0DQ нет в бинарях игры (NID-поиск строк «NID#» в eboot.bin и sce_module/*.prx игры) | нет | `videoOut.cpp`, `fileSystem.cpp`, `libKernel.cpp` |
| T093 | `prs-sdl3` | В | I | `f68c77d7` | Переход на SDL3 | `b3dc9c67:src/graphics/presentation/window/joyPump.cpp:238` | нет | `CMakeLists.txt`, `hostInput.cpp`, `swapchain.cpp`, `vulkanWindow.cpp`, `window.cpp`, `audio.cpp`, `controller.cpp` |
| T094 | `prs-resize` | Г | c | `01992958` | Изменяемое окно и пересоздание swapchain при ресайзе | `b3dc9c67:src/graphics/presentation/window/window.cpp:1001` | нет | `swapchain.cpp`, `window.cpp` |
| T095 | `sys-dynload` | Г | c | `ba579088` `1371219f` `0fb3ac56` `49716600` | Загрузчик: динамическая загрузка/выгрузка модулей | imports: sceKernelLoadStartModule (wzvqT4UqKX8) = 0 | нет | `libKernel.cpp`, `runtimeLinker.cpp` |
| T096 | `prs-frame-cfg` | Д | c | `c437de97` | Presenter: ранний выход при совместимом кадре | `b3dc9c67:src/graphics/presentation/window/swapchain.cpp:216` | нет | `swapchain.cpp` |
| T097 | `av-audio-split` | Г | U | `1275d65b` | Разделение audio.cpp на acm/audio3d/ngs2 | diff: перенос кода (5 509 строк диффа, построчно не сверялся) | нет | `audio.cpp`, `libAudio.cpp` |
| T098 | `img-vo-dcc` | Г | c | `2aa0a64f` | Сжатый (DCC) буфер видеовывода | `b3dc9c67:src/graphics/presentation/videoOut.cpp:596` | нет | `textureCache.cpp`, `videoOut.cpp` |
| T099 | `dec-ngg-other` | Г | U | `7d7267cc` `11001c97` `5297abb7` | NGG: волна 32, fast launch, не-амплифицирующие GS | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:1079` | да | — |
| T100 | `tst-zeroshift` | Д | I | `51c34d1a` | Тест свёртки нулевого скалярного сдвига (к свёртке 0>>x из 3b89e36d1) | — | нет | — |
| T101 | `rnd-depth-feedback` | Г | U | `66cc2fe2` | Обратная связь вложения глубины/стенсила на всех стадиях | `b3dc9c67:src/graphics/host_gpu/renderer/depthRenderTarget.h:52` | нет | `descriptors.cpp` |
| T102 | `ir-perf-reach` | Д | c | `1617ee77` | Рефакторинг: общая достижимость CFG | — | да | — |
| T103 | `ir-material-mask` | Г | I | `963a0817` | Ключи образов по маске материала | register:§104:Ф3 | да | `ResourceMaterialization.cpp` |
| T104 | `sys-mem-reserved-atomic` | Г | I | `0382d0ca` | Память: атомарная публикация отображений в зарезервированный диапазон | imports: sceKernelReserveVirtualRange (7oxv3PPCumo), sceKernelSetPrtAperture (BohYr-F7-is) = 0 | нет | — |
| T105 | `rnd-bind-reuse` | Д | I | `3bd5de64` `4cf456fb` `8fa116ee` `97fda7b1` | Повторное использование подготовленных привязок | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:4132` | нет | `descriptors.cpp` |
| T106 | `tst-infra` | Г | c | `84d01512` `1b6af301` `a892097f` `49db3ea5` `21d7e8e1` `181123ea` `c3a12397` `f3836bb8` `c0ebf224` | Тестовая инфраструктура / платформа / сборка тестов | — | нет | — |
| T107 | `dec-wqm-live` | В | c | `fcf0f3b6` | S_WQM в начале PS: предикат живых лейнов | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Control.cpp:311` | да | — |
| T108 | `bld-docs` | Г | c | `02578f3c` `db7745ef` `1216fa36` `421684e7` `ab2c1c4c` `db175852` `2984c412` `c1926f91` `947627d1` `58ba1e4c` `730e1a3c` | README и документация | diff: README и docs/screenshots | нет | — |
| T109 | `prs-depth-clamp` | А | I | `2aaf0c9b` | Ограничение глубины после polygon offset | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/shaders.cpp:542` | нет | `shaders.cpp`, `vulkanWindow.cpp` |
| T110 | `prs-vrr-status` | Г | c | `732057b0` | Сигнатура VideoOutVrrStatus | — | нет | `videoOut.cpp` |
| T111 | `img-vo-pq` | Г | c | `cce0cd95` | Формат видеовывода RGB10A2 PQ | — | да | `videoOut.cpp` |
| T112 | `ir-indirect-x3` | Г | I | `392f39e2` | Косвенный BUFFER_LOAD_DWORDX3 | register:§104:Ф3 | да | — |
| T113 | `dec-glc-coherent` | А | U | `dc9280d7` | GLC/DLC буферов как Volatile/Coherent | `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/MemoryOps.cpp:265` | да | `spirvEmitterMemory.cpp`, `ShaderDecoder.cpp`, `ShaderDecoder.h`, `Memory.cpp` |
| T114 | `dec-bvh` | В | c | `d72a79af` `337f4320` `dbf66b7f` | BVH: исполнение пересечений лучей (MIMG 0xe6/0xe7) | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Memory.cpp:709` | да | `pipelineCache.cpp`, `spirvEmitterMemory.cpp`, `ShaderDecoder.cpp`, `ShaderDecoder.h`, `Memory.cpp` |
| T115 | `sys-log-timestamp` | Г | c | `b9a0bd27` | Метка времени PRINT_NAME после 24 ч | — | нет | — |
| T116 | `prs-agc-trace` | Д | c | `a20fb7f9` | Трассы AGC только при graphics debug dump | `b3dc9c67:src/graphics/presentation/videoOut.cpp:4048` | нет | `videoOut.cpp` |
| T117 | `sys-printname-noinline` | Г | I | `e73324c2` | PRINT_NAME в noinline-функции (стеки волокон Linux/Clang 18) | — | нет | — |
| T118 | `av-audio-out-pacing` | В | c | `7855c980` `70a475ec` | Темп вывода AudioOut (каденция, часы вывода) | `b3dc9c67:src/libs/audio.cpp:697` | нет | `CMakeLists.txt`, `audio.cpp` |
| T119 | `ir-perf-spec` | Д | I | `93185953` `496432bb` `684330c9` | Скорость: специализация образов | — | да | `ResourceMaterialization.cpp` |
| T120 | `dec-cfg-gateway` | Г | I | `6bb68a3f` | CFG: повторное деление ворот слияния | — | да | — |
| T121 | `rnd-eop-clock` | Г | I | `bfdbba3a` | Общая обработка записи часов и значения в EOP | `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3718` | нет | — |
| T122 | `img-vk-names` | Д | I | `0ec43a8d` | Имена Vulkan-объектов только при создании | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:197` | нет | `textureCache.cpp` |
| T123 | `av-avplayer-autostart` | Г | c | `7e1c2d15` | AvPlayer: автозапуск без колбэка | `b3dc9c67:src/libs/avPlayer.cpp:1843` | нет | — |
| T124 | `sys-eager-resolve` | Г | I | `e056d55d` | Загрузчик: жадное разрешение символов, удаление ленивого PLT-механизма | наш runtimeLinker = база в этом месте; маркер Б9/Б9а «Unresolved import stub called» upstream сохраняет | нет | `runtimeLinker.cpp` |
| T125 | `av-audioout2-mix` | А | I | `313b60e9` `c86c8b4d` | AudioOut2: копия PCM и смешение объектных портов | `b3dc9c67:src/libs/libAudio2.cpp:704` | нет | `audio.cpp`, `audio_internal.h` |
| T126 | `bld-tests` | Г | c | `1e438136` `6f241bef` `62a0222e` `6ef40654` `038d2257` | Тесты и их сборка | diff: CMakeLists (тестовые цели) | нет | `CMakeLists.txt` |
| T127 | `lch-tests-args` | Г | c | `4e8d8c84` | Тесты LRU-кэша и разбор аргументов | diff: тесты, CI, разбор аргументов | нет | `CMakeLists.txt` |
| T128 | `av-avplayer-clock` | В | c | `e0b682e4` `e51f252b` | AvPlayer: часы воспроизведения и метки при петле | `b3dc9c67:src/libs/avPlayer.cpp:909` | нет | — |
| T129 | `av-dualsense-haptics` | В | c | `a22a9d93` `22ff4693` `e1be2ead` | Хаптика и динамик DualSense | `b3dc9c67:src/libs/controller.cpp:382` | нет | `CMakeLists.txt`, `audio.cpp`, `controller.cpp`, `controller.h` |
| T130 | `prs-layered-vo` | Г | U | `bec67b78` | HITMAN 3: слоистый видеовывод, шейдеры, сокеты | — | да | `CMakeLists.txt`, `descriptors.cpp`, `videoOut.cpp`, `swapchain.cpp`, `ResourceMaterialization.cpp`, `ResourceMaterialization.h` |
| T131 | `rnd-linear-rt-mips` | Г | I | `a88181b8` | Линейные render target с mip-цепочкой | `b3dc9c67:src/graphics/host_gpu/renderer/colorRenderTarget.cpp:290` | нет | — |
| T132 | `rnd-rt-pitch` | Г | U | `7b6bfdec` | Каноническая раскладка однофрагментных целей цвета | `b3dc9c67:src/graphics/host_gpu/renderer/colorRenderTarget.cpp:332` | нет | — |
| T133 | `img-1d2d-alias` | А | U | `f53f0ca4` | Алиасы 1D/2D текстур с отрисованным содержимым | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:297` | нет | `textureCache.cpp` |
| T134 | `img-depth-alias` | Г | U | `da33a1c4` `fbf6ae40` | Алиасы глубины: раскладка массива и tile_mode | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:932` | нет | `textureCache.cpp` |
| T135 | `img-color-meta-clear` | В | I | `0f1ff37f` `190608ae` `0ec3655f` | Материализация быстрых очисток по байтам метаданных (DCC/CMASK) | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:2258` | да | `textureCache.cpp`, `textureCache.h` |
| T136 | `rnd-aniso-reserved` | Г | I | `9229c04e` | Зарезервированные коды анизотропии сэмплера | `b3dc9c67:src/graphics/host_gpu/renderer/cache/samplerCache.cpp:88` | нет | — |
| T137 | `hle-http-uri` | Г | c | `025b39c0` `dc3cd2d2` | HTTP: разбор и сборка URI | nid:IWalAn-guFs (sceHttpUriParse) нет в бинарях игры (NID-поиск строк «NID#» в eboot.bin и sce_module/*.prx игры) | нет | `CMakeLists.txt` |
| T138 | `ir-883` | В | I | `0791f921` | UFC 5 in-game (#883) | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ResourceTracking.cpp:185` | да | `descriptors.cpp`, `pipelineCache.cpp`, `spirvEmitterMemory.cpp`, `Memory.cpp`, `ResourceMaterialization.cpp` |
| T139 | `sys-mem-extended` | Г | I | `c91fe80d` | Память: расширенная область 0x0800_0000_0000 для AMM | imports: Amm* (AmmGetVirtualAddressRanges, AmmGiveDirectMemory и др., 15 NID) = 0 | нет | — |
| T140 | `img-ext-mem` | Г | I | `2016f8e2` | Расширенная память гостя (адреса ≥ 2^40) в кэшах | `b3dc9c67:src/graphics/host_gpu/regionDefinitions.h:14` | да | `bufferCache.cpp`, `bufferCache.h`, `faultManager.cpp`, `textureCache.h`, `descriptors.cpp`, `spirvEmitterMemory.cpp` |
| T141 | `sys-amm-auto-recycle` | А | I | `34a3eb6b` | AMM: возврат автоматической подложки по физическому владению | `b3dc9c67:src/libs/libAmpr.cpp:1231` | нет | — |
| T142 | `ir-perf-policy` | Д | I | `c8baa7b9` | Рефакторинг: политика неизменяемых ресурсов | — | да | `ResourceMaterialization.cpp` |
| T143 | `hle-ces-savedialog` | Г | c | `05f92b64` | libCes CP932 и SaveDataDialog | nid: 7 функций Ces (ZiDCxUUGbec …) и SaveDataDialog (s9e3+YpRnzw, KK3Bdg1RWK0, yEiJ-qqr6Cg) нет в бинарях игры (NID-поиск строк «NID#» в eboot.bin и sce_module… | нет | `CMakeLists.txt` |
| T144 | `sys-fs-unmounted` | Г | I | `a107d1e3` | ФС: немонтированные пути гостя не уходят в ФС хоста | register:§44:Ф7 — пути KernelStat/KernelOpen игры все под /app0, «другой регистр и монтирование — 0» | нет | `fileSystem.cpp` |
| T145 | `av-audioout2-user` | Г | c | `0471c999` | AudioOut2: реестр пользователей | nid:iE8trxPKnAg (AudioOut2UserGetSupportedAttributes) нет в бинарях игры (NID-поиск строк «NID#» в eboot.bin и sce_module/*.prx игры) | нет | `libAudio.cpp` |
| T146 | `img-readback-valid` | Г | U | `6ee1bf9d` | Годность выгрузки образа без проверки грязных байт буфера | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:372` | нет | `textureCache.cpp`, `textureCache.h` |
| T147 | `img-gpumod-cpu` | В | U | `8e61798b` | IsRegionGpuModified и владение CPU | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3432` | нет | `textureCache.cpp` |
| T148 | `av-zarchive` | Г | U | `4b0de1b6` | Загрузка игр из .zar | игра — распакованная папка games/PPSA21564-app | нет | `CMakeLists.txt`, `fileSystem.cpp` |
| T149 | `rnd-releasemem-flush` | Д | I | `8e42e997` | RELEASE_MEM без лишних отправок | `b3dc9c67:src/graphics/guest_gpu/command_processor/pm4Handlers.cpp:2334` | нет | — |
| T150 | `rnd-stream-memcpy` | Д | I | `37501b5a` | Потоковое копирование чистых буферов без чтения backing | `b3dc9c67:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:1668` | нет | `bufferCache.cpp` |
| T151 | `rnd-rt-desc-inplace` | Д | c | `5e4f6afc` | Дескриптор цели цвета на месте, без лога решения | `b3dc9c67:src/graphics/host_gpu/renderer/colorRenderTarget.cpp:411` | нет | — |
| T152 | `rnd-pipeline-key-compact` | Д | I | `0fbeac6d` | Сжатые ключи шейдеров и хэш упакованного состояния пайплайна | `b3dc9c67:src/graphics/shader/shader.cpp:906` | да | `pipelineCache.cpp`, `pipelineCache.h` |
| T153 | `prs-pcache-lock` | В | I | `6d666681` | Кэш пайплайнов без своего мьютекса | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5100` | нет | `pipelineCache.cpp`, `pipelineCache.h`, `window.cpp` |
| T154 | `sys-profiler` | Г | c | `0c844e4b` | Профайлер Tracy | — | нет | `runtimeLinker.cpp` |
| T155 | `sys-sleep-block` | Д | I | `6f24b031` | Короткие сны блокируют вместо спина | — | нет | `pthread.cpp` |
| T156 | `rnd-blend-swizzle-alpha` | В | U | `73615c31` `0bef3fc0` `96011cc5` `94e7d239` | Смешение на целях с перестановкой каналов (логическая альфа через второй источник) | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/dualSrcBlend.h:3` | да | `pipelineCache.cpp`, `pipelineCache.h`, `shaders.cpp` |
| T157 | `rnd-lodbias-clamp` | Г | I | `59a17604` | Ограничение mipLodBias пределом устройства | `b3dc9c67:src/graphics/host_gpu/renderer/cache/samplerCache.cpp:156` | нет | — |
| T158 | `sys-mem-sparse` | Г | I | `650dc1e0` `f9fd400d` `45b6d2c5` | Память/графика: чтение разреженной подложки (PRT/пулы) для текстур | imports: sceKernelReserveVirtualRange, SetPrtAperture, MemoryPool* = 0 | нет | `bufferCache.cpp` |
| T159 | `sys-ampr-waits` | А | I | `5bf9218b` `c045f089` `da9b38af` `5a880808` | AMPR: асинхронный исполнитель APR, WaitOnAddress/WaitOnCounter/WriteCounter | `b3dc9c67:src/libs/libAmpr.cpp:1988` | нет | — |
| T160 | `bld-tracy` | Г | c | `2650478d` | Профилировщик Tracy | `b3dc9c67:src/common/profiler.cpp:58` | нет | — |
| T161 | `prs-gpu-reject` | Г | c | `af4edc28` | Причины отказа устройств Vulkan | — | нет | `vulkanWindow.cpp` |
| T162 | `av-host-controller-ux` | Г | c | `05057c94` `82a2f4ad` `820856b3` `719e0257` | Настройки и хоткеи DualSense на хосте | diff: лаунчер и конфигурация хоста | нет | `CMakeLists.txt`, `hostInput.cpp`, `audio.cpp`, `controller.cpp`, `controller.h` |
| T163 | `rnd-suspend-point` | Д | I | `840b9f57` | AgcSuspendPoint без стока очереди на вызывающем потоке | `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:335` | нет | — |
| T164 | `hle-pngenc` | Г | c | `48b52d31` | libScePngEnc | nid:RUrWdwTWZy8,xgDjJKpcyHo,7aGTPfrqT9s,9030RnBDoh4 импортированы eboot.bin, у нас — заглушки; вызовов 0 в 560 stdout | нет | `CMakeLists.txt` |
| T165 | `prs-vrr-wqhd` | Г | c | `8ba2caf5` | WQHD и VRR peg/unpeg | — | нет | `videoOut.cpp` |
| T166 | `hle-shareplay` | Г | U | `17100ec9` | SharePlay: состояние и сведения о соединении | nid:+MCXJlWdi+s нет в бинарях игры; игра импортирует только SharePlayTerminate | нет | — |
| T167 | `img-depth-swizzle` | Г | I | `44ba6575` | Допустимые swizzle сэмплируемой глубины | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:1145` | нет | — |
| T168 | `img-scratch-reuse` | Д | I | `c2f8e64f` | Переиспользование scratch-буферов тайлера | — | нет | `textureCache.cpp` |
| T169 | `dec-shader-identity` | В | I | `0ecd3229` | Идентичность шейдера (хэш кода) | `b3dc9c67:src/graphics/shader/shader.cpp:222` | да | — |
| T170 | `dec-cdbg-unused` | Г | c | `64dcbe0e` `679be25c` | S_CBRANCH_CDBG* прочие (игра не исполняет) | ophist:SOPP:19=0 | да | `ShaderDecoder.cpp`, `ShaderDecoder.h` |
| T171 | `ir-refresh-reach` | Г | I | `6409be28` | Достижимость ветвей при обновлении скалярных ресурсов | register:§104:Ф3 | да | `descriptors.cpp`, `ResourceMaterialization.cpp` |
| T172 | `ir-wave32-ballot` | Г | I | `35759e48` | Упрощение бита ballot в wave32 | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ConstantPropagation.cpp:207` | да | — |
| T173 | `tst-wave32mask` | Г | I | `706eec3c` | Тест скалярных B32-масок в wave32/wave64 | — | нет | — |
| T174 | `rnd-pipeline-blend-normalize` | Д | I | `b86cf0a8` | Пайплайны не зависят от настроек выключенного смешения | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5567` | нет | `pipelineCache.cpp` |
| T175 | `ir-perf-ssa` | Д | c | `2b2915e2` | Скорость: хранилище обхода SSA | — | да | — |
| T176 | `ir-perf-value` | Д | c | `3353c1ff` `28f29b8e` `d1c99bbf` | Скорость/память узлов IR | — | да | — |
| T177 | `rnd-memtrack-hotpath` | Д | I | `a9620f98` `a67a033f` `0bb2bdad` `a87889f0` `006875ed` | Горячий путь трекера памяти | `b3dc9c67:src/graphics/host_gpu/regionManager.h:196` | нет | `pageManager.cpp`, `regionManager.h` |
| T178 | `rnd-readback-sync` | Д | I | `39e23ac9` `0ce84e59` | Синхронный readback: публикация и окно | `b3dc9c67:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:722` | нет | `bufferCache.cpp`, `bufferCache.h` |
| T179 | `img-hades2` | В | U | `89792a3b` | Совместимость Hades II: адрес user data PS, заливка DWORD | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:2971` | да | `textureCache.cpp`, `libKernel.cpp` |
| T180 | `ir-gpu-selected-img` | Г | I | `7804eef9` | GPU-выбранные T# через общие косвенные привязки | register:§104:Ф3 | да | `ResourceMaterialization.cpp` |
| T181 | `ir-perf-dce` | Д | I | `95c89229` | DCE мёртвых циклов | — | да | — |
| T182 | `hle-net-resolver` | Г | c | `25457230` | NetResolverAbort | nid:AzqoBha7js4 нет в бинарях игры (NID-поиск строк «NID#» в eboot.bin и sce_module/*.prx игры) | нет | — |
| T183 | `ir-perf-info` | Д | c | `f3dc5ee4` | Скорость: сбор интерфейса без копий | — | да | — |
| T184 | `ir-ci-linux` | Г | c | `e317465d` | Сборка Linux CI | — | да | — |
| T185 | `prs-lds-pad` | Б | I | `e6cb880a` | Предел LDS вычислений и неоткрываемые геймпады | `b3dc9c67:src/graphics/presentation/window/joyPump.cpp:351` | нет | `pipelineCache.cpp`, `window.cpp` |
| T186 | `dec-img-atomic64` | Г | c | `ef4c5baf` `af3011cd` | 64-битные атомики образов | ophist:MIMG:16=0,MIMG:17=0 | да | `graphicContext.h`, `descriptors.cpp`, `vulkanWindow.cpp`, `spirvEmitterMemory.cpp`, `Memory.cpp`, `ResourceMaterialization.cpp` |
| T187 | `img-bc5-reuse` | Г | U | `0d4f9933` | Повторно используемые BC5 в своей раскладке | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:1024` | нет | `textureCache.cpp` |
| T188 | `img-gpu-alias-write` | А | U | `ebe401d0` | Запись GPU в буфер и инвалидация перекрытых образов | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3400` | нет | `textureCache.cpp` |
| T189 | `ir-gather-lod` | Г | c | `bd611bfe` | Явный LOD у gather | ophist:MIMG:44=0 | да | `descriptors.cpp`, `Memory.cpp`, `ResourceMaterialization.cpp` |
| T190 | `be-buildfix` | Г | c | `f53e5d22` | Исправление сборки Windows CI | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp:717` | да | — |
| T191 | `img-srgb-rt-bpe` | Г | I | `52c8ff18` | Байты на элемент цели k8Srgb/k8_8Srgb | `b3dc9c67:src/graphics/guest_gpu/gpu_format.cpp:64` | нет | — |
| T192 | `img-volume-depth` | Г | U | `8b0cc79a` | Рост глубины объёмной текстуры | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:1024` | нет | `textureCache.cpp` |
| T193 | `ir-perf-sampler` | Д | I | `7f158c65` | Общие снимки сэмплеров у вариантов | — | да | `descriptors.cpp`, `ResourceMaterialization.cpp` |
| T194 | `sys-posix-attrstack` | Г | c | `5766b241` | POSIX pthread_attr_setstack | imports: pthread_attr_setstack (-SrbXpGR1f0) = 0; scePthreadAttrSetstack у нас есть (libKernel.cpp:3307) | нет | `pthread.cpp`, `libKernel.cpp` |
| T195 | `sys-aio` | Г | c | `a0858abe` `e7cfe5a2` | Пакетный AIO (poll/delete/wait) | imports: Ft3EtsZzAoY, o7O4z3jwKzo = 0 | нет | `libKernel.cpp` |
| T196 | `sys-kernel-timers` | Г | c | `92c22d60` | Периодические таймеры ядра в очереди событий | imports: sceKernelAddTimerEvent (57ZK+ODEXWY), AddHRTimerEvent (R74tt43xP6k) = 0 | нет | `libKernel.cpp` |
| T197 | `hle-npwebapi-stats` | Г | c | `c3330cab` | NP Web API: статистика пулов памяти | nid:Xweb+naPZ8Y нет в eboot.bin и libSceNpCppWebApi.prx | нет | — |
| T198 | `sys-signin-dialog` | Г | I | `45f55413` | Диалог входа держится до закрытия пользователем | — | нет | — |
| T199 | `prs-resize-zero` | Г | I | `0e8ded37` | Игнор неположительных размеров окна | `b3dc9c67:src/graphics/presentation/window/window.cpp:467` | нет | `window.cpp` |
| T200 | `dec-vscnt` | А | I | `f58014ff` | S_WAITCNT_VSCNT как завершение записей волны | `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/ScalarAluOps.cpp:91` | да | `ShaderDecoder.cpp`, `ShaderDecoder.h` |
| T201 | `ir-dispatch-exec` | Г | I | `e4aca7a6` `0258bd61` | EXEC по размерам dispatch в потоках | — | да | `ResourceMaterialization.cpp` |
| T202 | `ir-gpu-written-desc` | Г | I | `ec3e48cd` | Синхронизация GPU-записанных записываемых дескрипторов | register:§104:Ф3 | да | `ResourceMaterialization.cpp` |
| T203 | `dec-alignbyte` | А | I | `f18679e0` | V_ALIGNBYTE_B32: смещение по 2 битам | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Integer.cpp:500` | да | — |
| T204 | `be-fp64` | Г | c | `7992aecb` | FP64: собственное округление в смешанной точности | ophist:VOP3:14c=0;VOP3:164=0;VOP3:165=0;VOP3:166=0;VOP3:167=0;VOP1:f=0;VOP3:18f=0;VOP1:10=0;VOP3:190=0 | да | `vulkanWindow.cpp` |
| T205 | `tst-hades` | Г | U | `a5eeab98` | Тест PM4: обработчики SPI_SHADER_USER_DATA_ADDR_*_PS (к теме 89792a3bc) | — | нет | — |
| T206 | `ir-brev-flat` | Г | c | `139b564c` | Свёртка S_BREV_B32 до классификации FLAT-стека | ophist:FLAT.flat:*=0 | да | — |
| T207 | `ir-loop-exec-witness` | Г | I | `e0c90ace` | EXEC-свидетели в циклах дескрипторов | register:§104:Ф3 | да | — |
| T208 | `ir-material-scan` | Г | I | `b183cb10` | Общие ограниченные сканы ключей материала | register:§104:Ф3 | да | `ResourceMaterialization.cpp` |
| T209 | `ir-desckey-ssa` | Г | I | `1f6be3d5` | SSA ключа дескриптора при нативном разрешении | register:§104:Ф3 | да | — |
| T210 | `sys-mem-fixed-replace` | А | U | `46900d80` | Память: замена живого фиксированного прямого отображения без дыры | — | нет | — |
| T211 | `ir-scalar-native` | Г | c | `cd9fc6ff` `266c12ce` | Скаляры нативно, сырые адреса (отменено) | — | да | `ResourceMaterialization.cpp` |
| T212 | `ir-movreld-loopbound` | Д | I | `92ac54a4` | Невозможные относительные записи при замкнутых границах цикла | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ConstantPropagation.cpp:207` | да | — |
| T213 | `sys-gpu-descr-sync` | В | I | `57cf0868` | Синхронизация GPU-записанных зависимостей дескрипторов через кэш буферов | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:851` | нет | `pipelineCache.cpp` |
| T214 | `img-spec-read` | В | I | `783d9f8d` | Чтение памяти специализации из сырого буфера | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:830` | нет | `textureCache.cpp`, `textureCache.h`, `pipelineCache.cpp` |
| T215 | `dec-cselect-raw` | Г | I | `efbaa17f` | S_CSELECT_B64 в EXEC/VCC: сырые биты | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Control.cpp:261` | да | — |
| T216 | `be-narrowsto` | Д | I | `c3f49627` | Нативное 8/16-битное хранение буферов (storageBuffer8/16BitAccess) | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp:1518` | да | `descriptors.cpp`, `vulkanWindow.cpp`, `spirvEmitterMemory.cpp` |
| T217 | `be-meshclip` | Г | U | `39248a1f` | Clip/cull distance в меш-шейдерах | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterMesh.cpp:39` | да | — |
| T218 | `av-haptics-linux` | Г | c | `c885da0a` | Хаптика DualSense на Linux | platform:Linux | нет | — |
| T219 | `sys-libc-autoload` | В | I | `fdac55a5` | Загрузчик: только libc.prx автоматически, без предзагрузки соседних PRX | `b3dc9c67:src/loader/runtimeLinker.cpp:1531` | нет | `runtimeLinker.cpp` |
| T220 | `sys-ampr-evfilt` | Г | c | `deb45a8b` | Фильтр EVFILT_AMPR для событий завершения APR | imports: sceKernelAddAmprEvent (bBfz7kMF2Ho), DeleteAmprEvent (bMmid3pfyjo), AddUserEvent (4R6-OvI2cEA) = 0; строк «AMPR event add» в log_fs15_z 0 | нет | — |
| T221 | `be-scaledtex` | Г | U | `96c067d0` `07c84876` `e5689990` | Текстуры USCALED 8 бит: выборка через UNORM-хранение | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp:397` | да | `ResourceMaterialization.cpp` |
| T222 | `img-10-11-11` | Г | U | `5940e623` | Цель 10-11-11 и общие преобразования цвета | — | да | `CMakeLists.txt`, `textureCache.cpp` |
| T223 | `img-rebind-order` | Г | U | `a2f85178` | Порядок пересвязывания перекрывающихся образов | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:5176` | нет | `textureCache.cpp`, `descriptors.cpp` |
| T224 | `rnd-polygon-fan` | Г | I | `45fab265` | Примитив kPolygon как веер треугольников | `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:2952` | нет | — |
| T225 | `ir-wg-imgtable` | Г | I | `0ee88009` `190f838e` | T# по индексу рабочей группы | register:§104:Ф3 | да | `pipelineCache.cpp`, `ResourceMaterialization.cpp` |
| T226 | `be-ldsbuf` | Г | I | `b0bbaef1` `f7bd0b43` | LDS больше лимита устройства — в буфер устройства | — | да | `descriptors.cpp`, `pipelineCache.cpp`, `spirvEmitterMemory.cpp` |
| T227 | `ir-sampler-resv` | Г | I | `b7d3c572` | Очистка неиспользуемых битов сэмплера | register:§104:Ф3 | да | — |
| T228 | `img-2d3d-alias` | Г | U | `0885f43a` | Алиасы 2D/3D текстур раздельно | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:1024` | нет | `textureCache.cpp` |
| T229 | `rnd-vfmt-uscaled` | Г | I | `8e46a3cc` | Вершинный формат 10_10_10_2 UScaled | `b3dc9c67:src/graphics/host_gpu/vulkanCommon.cpp:50` | нет | — |
| T230 | `hle-font-kerning` | Г | c | `c753efdd` | sceFont: кернинг | nid:sDuhHGNhHvE (sceFontGetKerning) нет в бинарях игры (NID-поиск строк «NID#» в eboot.bin и sce_module/*.prx игры) | нет | — |
| T231 | `hle-font-metrics` | А | I | `f96a14a0` `58978d15` | sceFont: метрики и растр глифов по запрошенному масштабу | `b3dc9c67:src/libs/libFont.cpp:802` | нет | — |
| T232 | `sys-hle-stubs` | Г | c | `bbb98bd4` | Заглушки BluetoothHid/DeviceService/Usbd | imports: 8 новых NID = 0 | нет | — |
| T233 | `dec-mad-legacy` | А | c | `d8be245c` | Нефьюзный legacy MAD/MAC FP32 отдельно от FMA | `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Vector.cpp:414` | да | `ShaderDecoder.h` |
| T234 | `dec-ds-fminmax` | А | c | `e85279ea` | DS_MIN/MAX_F32: два операнда и особые значения | `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/MemoryOps.cpp:197` | да | `spirvEmitterMemory.cpp` |
| T235 | `hle-trophy` | Г | U | `72e4989b` `fb7ff7ec` | Трофеи: состояние, уведомления, UDS | diff: оверлей и состояние трофеев | нет | `CMakeLists.txt` |
| T236 | `ir-strided-masked` | Г | I | `5c830604` | Маскированные ключи в шаговых записях | register:§104:Ф3 | да | `ResourceMaterialization.cpp` |
| T237 | `be-maddenorm` | В | c | `77d77221` | Явный флеш денормалей в legacy MAD (выключен для теста скорости) | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/SpirvEmitter.h:18` | да | — |
| T238 | `ir-native-int64` | Д | I | `5b826c6e` | Нативные 64-битные операции SPIR-V | — | да | `spirvEmitterMemory.cpp` |
| T239 | `img-unmap-drain` | Д | I | `e6fce45d` | Снятие отображения без ожидания GPU | — | нет | `textureCache.cpp`, `textureCache.h`, `renderContext.cpp` |
| T240 | `img-clear16` | Б | c | `57c97ebd` | Декодирование 16-битных цветовых очисток | `b3dc9c67:src/graphics/host_gpu/renderer/image/imageInfo.h:458` | да | — |
| T241 | `rnd-depth-bounds-dyn` | Д | I | `98401022` | Динамические границы глубины | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5635` | нет | `pipelineCache.cpp`, `pipelineCache.h`, `shaders.cpp` |
| T242 | `rnd-unbounded-buffers` | Г | I | `e5dcfdb8` | Ограничение буферов с NumRecords = 0xFFFFFFFF | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:4913` | нет | `descriptors.cpp` |
| T243 | `rnd-indirect-sgpr` | В | I | `cdb64bfd` `9f83fd5f` `420bb51d` | Смещения косвенного draw в user SGPR и источник индексов | `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3126` | нет | — |
| T244 | `dec-glc-flat` | Г | c | `9caec9f2` | DLC-когерентность FLAT-загрузок | `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/MemoryOps.cpp:346` | да | `spirvEmitterMemory.cpp`, `Memory.cpp` |
| T245 | `ir-nested-selector` | Г | I | `c23de621` | Вложенные таблицы селекторов дескрипторов | register:§104:Ф3 | да | `ResourceMaterialization.cpp` |
| T246 | `sys-eq-persistent` | А | U | `afbb322b` | Очередь событий: уровень без EV_CLEAR один раз за ожидание | `b3dc9c67:src/kernel/eventQueue.cpp:94` | нет | — |
| T247 | `ir-perf-cleanup` | Д | c | `5a491abb` | Чистка: лишняя сортировка | — | да | `ResourceMaterialization.cpp` |
| T248 | `ir-broad-table` | Г | I | `b929bbe3` | Широкие таблицы образов — только совместимые виды | register:§104:Ф3 | да | `ResourceMaterialization.cpp` |
| T249 | `sys-thread-naming` | Г | c | `199d0a9d` `1b21161a` | Имена гостевых потоков на хосте (Linux/macOS) | — | нет | `pthread.cpp` |
| T250 | `prs-title` | Б | c | `7415febd` | Заголовок окна в главном потоке | `b3dc9c67:src/graphics/presentation/window/window.cpp:1979` | нет | `hostInput.cpp`, `swapchain.cpp`, `window.cpp` |
| T251 | `rnd-depth-copy` | Г | I | `2a18e66a` `65144ce4` | Проверка копирования глубины в цвет при draw | `b3dc9c67:src/graphics/guest_gpu/command_processor/pm4Handlers.cpp:194` | нет | — |
| T252 | `sys-notice-skip` | Г | c | `cc44a43e` | Опция пропуска экрана уведомлений | — | нет | — |
| T253 | `sys-agc-new-abi` | Г | c | `67d7db68` `aa3b2cd5` `3ae5a9b7` `fbea51c6` | AGC: новые NID (SetNop, async rewind, branch patch, packet size) | imports: nNlUtdDDvZ0 = 0 | нет | — |
| T254 | `prs-trophy-ui` | Г | c | `d2413fc2` | Просмотр трофеев и перенос заголовков тостов | — | нет | — |
| T255 | `ir-mrt-compact` | В | I | `21a1346e` | Компактные экспорты цвета через CB_SHADER_MASK | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ShaderInfoCollection.cpp:378` | да | — |
| T256 | `be-snorm16exp` | Г | c | `b96871e2` | Распаковка сжатого экспорта цвета SNORM16_ABGR (режим 6) | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterFlow.cpp:291` | да | — |
| T257 | `be-wavebranch` | А | I | `a8beac19` | Скалярное ветвление (EXECZ/VCCZ) решением всей волны | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterProgram.cpp:143` | да | — |
| T258 | `rnd-raw-storage-alias` | А | U | `743fdc69` | Чтение сырых буферов хранения синхронизируется с образами-алиасами | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:903` | нет | `descriptors.cpp` |
| T259 | `img-array-sync` | Г | U | `dd754065` | Копирование массивов образа в буфер | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3220` | нет | `textureCache.cpp` |
| T260 | `sys-raw-image-sync` | Г | c | `470669c6` | Синхронизация сырых чтений образов по опции | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:903` | нет | `descriptors.cpp` |
| T261 | `sys-mem-winview` | Д | I | `c30ac7c9` | Память: без лишней смены защиты вида Windows | — | нет | — |
| T262 | `sys-mem-flatten` | Г | I | `9c79d9d2` | Память: упрощение путей прямого и пакетного отображения | — | нет | — |
| T263 | `rnd-staging-write` | Д | I | `4d10ea17` | Запись через staging-буфер с явными барьерами | `b3dc9c67:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:100` | нет | `bufferCache.cpp` |
| T264 | `sys-mem-concurrent-reads` | Д | I | `7e011fa5` | Память: параллельные чтения подложки | — | нет | — |
| T265 | `sys-ampr-fileid` | А | c | `e43aadf7` | AMPR: уникальные ID разрешённых путей вместо FNV-1a | `b3dc9c67:src/libs/libAmpr.cpp:96` | нет | — |
| T266 | `rnd-macos-tid` | Г | c | `79a91ecf` | macOS: кэш id потока в TrackingSpinLock | — | нет | `regionManager.h` |
| T267 | `tst-int16` | Г | c | `34f6fd1f` | Тесты 16-битных целочисленных опкодов ALU | ophist:VOP3P:0..d=0;VOP3:303..30e=0;VOPC:89..8e=0;VOP3:89..8e=0;VOPC:a9..ae=0;VOP3:a9..ae=0 | нет | — |
| T268 | `sys-dev-random` | Г | I | `de626649` | /dev/random как символьное устройство | — | нет | `fileSystem.cpp` |
| T269 | `sys-cloexec` | Г | c | `db41d048` | Флаг close-on-exec дескрипторов | imports: sceKernelSetFdCloseOnExec (ioWKNmDZG+0), sceSystemServiceLoadExec (JoBqSQt1yyA) = 0 | нет | `fileSystem.cpp`, `libKernel.cpp` |
| T270 | `sys-sysmodule-refs` | А | U | `210d4dcd` | Sysmodule: счёт ссылок загрузки и статус выгрузки | `b3dc9c67:src/libs/libSysmodule.cpp:25` | нет | — |
| T271 | `sys-entitlement-event` | А | U | `62643c34` | SystemService: событие ENTITLEMENT_UPDATE после AppContentInitialize | `b3dc9c67:src/libs/libSystemService.cpp:156` | нет | — |
| T272 | `av-pad-trigger-state` | А | c | `3c62359e` | Состояние адаптивных курков (scePadGetTriggerEffectState) | `b3dc9c67:src/libs/libPad.cpp:39` | нет | `controller.cpp`, `controller.h` |
| T273 | `hle-np-lang` | Г | c | `4865dd92` | NP: язык аккаунта | nid:3Tcz5bNCfZQ нет в бинарях игры (NID-поиск строк «NID#» в eboot.bin и sce_module/*.prx игры) | нет | — |
| T274 | `sys-sema-timer` | Д | c | `4e14eed7` | Семафор: таймер после ранних возвратов | — | нет | — |
| T275 | `sys-ampr-native-path` | Г | c | `f4075517` | AMPR: нативные пути хоста (не-ASCII папка) | пакет игры и путь эмулятора ASCII (0 не-ASCII из 158 205) | нет | — |
| T276 | `hle-npcommerce` | Г | c | `107d5f75` | NpCommerce: диалоги | nid:DfSCDRA3EjY (Open), r42bWcQbtZY нет; игра импортирует только NpCommerceDialogUpdateStatus | нет | — |
| T277 | `av-pad-port-ownership` | В | c | `b65dc122` | Владение портом пада (PadOpen/PadClose) | `b3dc9c67:src/libs/controller.cpp:1424` | нет | `controller.cpp`, `controller.h` |
| T278 | `be-irstore` | Д | c | `52dbc724` `b35cdc39` | Хранение SPIR-V-определений в узлах IR, отложенные операнды Phi | — | да | — |
| T279 | `be-descslots` | Д | I | `e1ac893a` | Сбор использования один раз, прямые слоты дескрипторов | — | да | `CMakeLists.txt`, `descriptors.cpp`, `shaders.cpp`, `spirvEmitterMemory.cpp`, `ResourceMaterialization.cpp` |
| T280 | `ir-srt-alias` | Д | I | `dbe5353f` | Рефакторинг: псевдонимы поиска SRT | — | да | `CMakeLists.txt`, `ResourceMaterialization.cpp` |
| T281 | `ir-block-cfg` | Д | I | `3df45667` | Рефакторинг: управление потоком в блоках IR | — | да | `ResourceMaterialization.cpp` |
| T282 | `be-nativeint` | Д | I | `ee4dd906` | Нативные целочисленные GLSL-операции без приведения знака | — | да | — |
| T283 | `be-nanclass` | Д | c | `393257ea` `7b9997ba` | Классификация NaN: одно сравнение модуля, маска класса 3 -> OpIsNan | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterAluHelpers.cpp:104` | да | — |
| T284 | `rnd-nop-1dw` | Г | U | `4c8fc53a` | NOP из одного слова и общий размер пакета | `b3dc9c67:src/libs/agc.cpp:1746` | нет | — |
| T285 | `ir-pred-capture` | Д | I | `3b1a9470` | Захват только предикатов из памяти | — | да | `ResourceMaterialization.cpp` |
| T286 | `ir-scalar-gpu` | Г | c | `5b68a26c` `1c301c9a` | Скалярная полезная нагрузка на GPU (отменено) | — | да | `ResourceMaterialization.cpp` |
| T287 | `ir-scalar-matsel` | Г | I | `973809cd` | Ограниченные скалярные селекторы образов материала | register:§104:Ф3 | да | `ResourceMaterialization.cpp` |
| T288 | `sys-agc-driver-dmem` | Г | U | `165cd884` `9a5dd9fa` | AGC: DMEM драйвера и таблица функций при старте | — | нет | — |
| T289 | `img-tiling-refactor` | Д | I | `5559cfcb` | Перестройка тайлинга и общих раскладок | — | да | `CMakeLists.txt`, `textureCache.cpp`, `textureCache.h`, `descriptors.cpp`, `videoOut.cpp` |
| T290 | `img-dynstate` | Д | I | `93452b24` | Кэш динамического состояния графики | — | нет | — |
| T291 | `be-dppshare` | Г | c | `053f5fd3` | DPP row_share | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterHelpers.cpp:92` | да | — |
| T292 | `sys-updater` | Г | c | `307fdcf7` | Самообновление лаунчера | — | нет | — |
| T293 | `prs-splash` | Г | c | `f63d3bef` | Заставка при запуске | — | нет | `emulator.cpp` |
| T294 | `prs-back-touch` | Г | c | `1cfb9522` | Back как клик тачпада | — | нет | `window.cpp` |
| T295 | `rnd-r64-bc` | Г | I | `b7b335ac` | Блочно-сжатые текстуры в тайлинге RenderTarget R64 | `b3dc9c67:src/graphics/guest_gpu/tile.cpp:306` | нет | — |
| T296 | `img-r8snorm` | Г | c | `7e4e142a` | Сэмплирование R8 SNORM | `b3dc9c67:src/graphics/guest_gpu/gpu_format.cpp:23` | нет | — |
| T297 | `img-fmt-uint8` | Д | c | `ece4e287` | Поля таблицы форматов в uint8_t | — | нет | — |
| T298 | `av-avplayer-buffers` | А | U | `a6f4e8e7` | AvPlayer: возврат выходных буферов декодеру | `b3dc9c67:src/libs/avPlayer.cpp:963` | нет | — |
| T299 | `sys-agc-dbgdump` | Г | c | `d4bb7fd7` | AGC: удалён отладочный дамп буфера команд | — | нет | — |
| T300 | `ir-srt-jit` | Д | I | `f848d276` `4084a008` | JIT обхода SRT (xbyak) | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/SrtWalker.cpp:2354` | да | `CMakeLists.txt`, `ResourceMaterialization.cpp` |
| T301 | `prs-depth2color` | Г | I | `1029511b` | Копия глубины в цвет | `b3dc9c67:src/graphics/host_gpu/renderer/depthRenderTarget.cpp:370` | нет | `graphicContext.h`, `vulkanWindow.cpp` |
| T302 | `sys-playgo-plgx` | Г | c | `6f3bebcb` | PlayGo: чанки plgx | лог игры: «Can't open .../sce_sys/playgo-chunk.dat» (log_fs15_v) | нет | — |
| T303 | `sys-loadexec` | Г | c | `cb375ec3` `6f0cddd4` `16a7fe68` | LoadExec (перезапуск исполняемого файла) | imports: sceSystemServiceLoadExec (JoBqSQt1yyA) = 0 | да | `CMakeLists.txt`, `runtimeLinker.cpp` |
| T304 | `img-cmp-depth-dcc` | В | U | `f28c0fcc` | DCC у цветового алиаса со сравнением глубины | `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3104` | нет | `textureCache.cpp`, `descriptors.cpp` |
| T305 | `ir-shared-pred` | Г | I | `df0412af` | Общие предикаты при извлечении плана | register:§104:Ф3 | да | `ResourceMaterialization.cpp` |
| T306 | `ir-texoffset` | А | I | `984cfceb` | Смещения текселей IMAGE_SAMPLE_*_O | `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp:781` | да | `Memory.cpp` |
| T307 | `sys-hdr` | Г | I | `e51de54e` | Вывод HDR10 | — | да | `CMakeLists.txt`, `videoOut.cpp`, `swapchain.cpp`, `vulkanWindow.cpp` |
| T308 | `sys-ftruncate` | Г | c | `048fe9f4` | Экспорт sceKernelFtruncate | imports: VW3TVZiM4-E = 0 | нет | `libKernel.cpp` |
| T309 | `sys-ampr-writeaddr-size` | А | I | `41beda43` | AMPR: размер записи WriteAddress 8/12/16 вместо 0x20 | `b3dc9c67:src/libs/libAmpr.cpp:2560` | нет | — |
| T310 | `hle-netctl-ipv4` | Г | c | `e699a35f` | NetCtl: опция подключения IPv4 хоста | diff: network_connected = false по умолчанию | нет | — |
| T311 | `img-guestgpu-simplify` | В | I | `5b730d4d` | Упрощение GuestGpu: запись EOP без Sync | `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3540` | нет | `textureCache.cpp` |
| T312 | `img-bc-alias-gc` | В | U | `dad900c6` | Запись в BC-алиасы и момент сборки мусора | `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:4019` | нет | `textureCache.cpp`, `textureCache.h` |

## 11. Якоря оснований (строка и контроль +1)

Для каждой темы с основанием-строкой: `b3dc9c67:<путь>:<строка>` — «якорь» / +1 «следующая строка». Все строки всех 564 коммитов с такими
основаниями (224) проверяет `check_m1a.py` по `upstream_detail.tsv`.

- T001 `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:2843` — «void CommandProcessor::ProcessIndirectBuffer(std::span<const uint32_t> commands) {» / +1 «EXIT_IF(g_current_execution == nullptr);»
- T003 `b3dc9c67:docs/track-f/f23a/cmp_eboot.out.txt:3` — «real decoder UNSUPPORTED instructions 0 in programs 0» / +1 «real decoder VALU instructions 4692078 distinct family:op 167»
- T005 `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:1207` — «// interpolates packed per-vertex normals manually with the PERSP_CENTROID pair;» / +1 «// leaving it at zero collapsed the normals to vertex 0 and produced NaN.»
- T006 `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3083` — «default: EXIT("unknown predication op: 0x%08" PRIx32 "\n", op);» / +1 «}»
- T007 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterModule.cpp:487` — «// shader exports each parameter to a single location. Resolve the alias groups first so» / +1 «// that an owner's type already reflects a per-vertex alias of the same location.»
- T010 `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:1118` — «const bool fan = mesh.input_primitive ==» / +1 «static_cast<uint32_t>(Prospero::PrimitiveType::kTriFan);»
- T011 `b3dc9c67:src/libs/libJson2.cpp:878` — «static const int64_t* KYTY_SYSV_ABI JsonValueGetInteger(const JsonValue* self) {» / +1 «PRINT_NAME();»
- T012 `b3dc9c67:src/libs/libKernel.cpp:2774` — «LOGF("FiberSwitch: repaired stale RUNNING state of %s (thread %d)" "\n", fiber->name,» / +1 «Common::Thread::GetThreadIdUnique());»
- T014 `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/ScalarAluOps.cpp:116` — «{0x17u, Opcode::S_NOP},» / +1 «{0x18u, Opcode::S_NOP},»
- T016 `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ResourceTracking.cpp:249` — «// A descriptor word that reaches its use through a phi of a two-way uniform branch (for» / +1 «// example S_CBRANCH_SCC0 skipping a second S_LOAD of the S#, ASTRO BOT PS 0x1974d0d59ab6429f)»
- T017 `b3dc9c67:src/graphics/host_gpu/renderer/renderCompute.cpp:1038` — «if (!indirect && (thread_group_x == 0 // thread_group_y == 0 // thread_group_z == 0)) {» / +1 «if (DiagF5::On()) [[unlikely]] {»
- T018 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3014` — «const auto view_last_level =» / +1 «!multisampled && !dynamic_storage ? std::min(last_level, max_mip) : last_level;»
- T019 `b3dc9c67:src/graphics/shader/recompiler/frontend/cfg/ShaderCFG.cpp:1359` — «if (graph.Dominates(block.id, false_target) &&» / +1 «HasLinearPathToTerminal(graph, true_target)) {»
- T020 `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:3014` — «if (slot == 0 // (render_target_mask_slot(ctx.GetRenderTargetMask(), slot) != 0 &&» / +1 «ctx.GetRenderTarget(slot).base.addr != 0)) {»
- T021 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:1952` — «view.min_lod = descriptor.MinLod();» / +1 «} else {»
- T022 `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:4109` — «EXIT("unsupported mesh draw: primitive=%u indexed=%u restart=%u\n",» / +1 «static_cast<uint32_t>(ucfg.GetPrimType()), draw.IsIndexed(), primitive_restart_enable);»
- T023 `b3dc9c67:src/libs/agc.cpp:267` — «[[nodiscard]] KYTY_SYSV_ABI uint32_t GetAvailableSizeDW() const {» / +1 «if (cursor_up == nullptr // cursor_down == nullptr // cursor_down <= cursor_up) {»
- T024 `b3dc9c67:src/graphics/host_gpu/renderer/depthRenderTarget.cpp:169` — «if (z.z_info.expclear_enabled // z.stencil_info.expclear_enabled //» / +1 «z.z_info.partially_resident //»
- T027 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:2411` — «if (owner != nullptr && owner->info.data.address == stencil.address) {» / +1 «association = id;»
- T028 `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:621` — «LOGF("\t copy_data reference clock: dst=0x%016" PRIx64 " value=0x%016" PRIx64 " size=%u\n",» / +1 «dst_address, value, num_bytes);»
- T029 `b3dc9c67:src/libs/controller.cpp:705` — «const bool keyboard_motion = state.motion_shake // state.motion_pitch != 0.0f;» / +1 «if (state.motion_enabled && state.real_motion && !keyboard_motion) {»
- T031 `b3dc9c67:src/libs/guestPrintf.cpp:530` — «precision      = prec > 0 ? static_cast<unsigned int>(prec) : 0U;» / +1 «format++;»
- T032 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp:1773` — «void StoreFormattedInBounds(ValueEmitContext& ctx, const IR::MemoryInfo& mem,» / +1 «const PreparedFormattedMemory& plan, uint32_t component,»
- T042 `b3dc9c67:src/graphics/host_gpu/regionManager.h:25` — «#undef max» / +1 «#elif defined(__APPLE__)»
- T044 `b3dc9c67:src/libs/network.cpp:3143` — «g_net_ctl_connected          = false;» / +1 «g_net_ctl_status_initialized = true;»
- T045 `b3dc9c67:src/libs/network.cpp:3143` — «g_net_ctl_connected          = false;» / +1 «g_net_ctl_status_initialized = true;»
- T046 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/shaders.cpp:345` — «// KYTY_FIX_DUALSRC=1 and a blended attachment with a SRC1 factor: the fragment module of this pipeline only,» / +1 «// with the output at Location 1 rewritten to Location 0 Index 1 (DualSrcBlend::RewriteLocation1ToIndex1).»
- T047 `b3dc9c67:src/graphics/host_gpu/renderer/image/image.cpp:54` — «if (info.IsBlock()) {» / +1 «return vk::ImageUsageFlagBits::eTransferSrc / vk::ImageUsageFlagBits::eTransferDst /»
- T049 `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:545` — «if (high_lane ? operand.negate_hi : operand.negate) {» / +1 «value = ir.BitwiseAnd(ir.ISub(IR::U32(IR::Value(0u)), value), IR::U32(IR::Value(0xffffu)));»
- T054 `b3dc9c67:src/libs/libSaveData.cpp:335` — «if (!Common::Gates::Enabled(Common::Gates::Gate::SavePersist)) {» / +1 «return;»
- T055 `b3dc9c67:src/libs/avPlayer.cpp:1817` — «static void emit_event(AvPlayerInternal* h, int32_t id, void* data = nullptr) {» / +1 «if (h != nullptr && h->event.event_callback != nullptr) {»
- T056 `b3dc9c67:src/libs/libUserService.cpp:95` — «EXIT_NOT_IMPLEMENTED(user_id != Config::GetUserId());» / +1 «EXIT_NOT_IMPLEMENTED(size < 5);»
- T058 `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:2566` — «// Tessellation. The merge brought upstream's native LS/HS/TES path, which this pre-filter» / +1 «// used to hide: a patch draw sets HS_EN, which is outside {0, 0x02002000}, so every one of»
- T059 `b3dc9c67:src/libs/avPlayer.cpp:1408` — «float Aspect(AVStream* s) const {» / +1 «if (s->codecpar->height == 0) {»
- T060 `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:3198` — «// Sarah» / +1 «EXIT_NOT_IMPLEMENTED(!(draw.index_count == 3 && vs_input_info.buffers_num == 0));»
- T061 `b3dc9c67:src/common/platform/sysWindowsFileIO.cpp:58` — «if (t == SYS_FILE_CACHE_SEQUENTIAL_SCAN) {» / +1 «return SYS_FILE_CACHE_SEQUENTIAL_SCAN;»
- T065 `b3dc9c67:src/graphics/guest_gpu/command_processor/pm4Handlers.cpp:2106` — «EXIT("unknown cx reg at %05" PRIx32 ": 0x%" PRIx32 "\n", num_dw - dw, cmd_offset);» / +1 «}»
- T066 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:1188` — «(descriptor.Depth() - descriptor.BaseArray5() + 1u) % 6u == 0;» / +1 «const bool is_2d_array =»
- T067 `b3dc9c67:src/graphics/presentation/videoOut.cpp:4183` — «status->resolution   = (ctx->width >= 3840 // ctx->height >= 2160 ? 2u : 1u);» / +1 «status->dynamicRange = 1;»
- T068 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterFlow.cpp:595` — «void EmitBarrier(EmitterState& state) {» / +1 «const auto tessellation = state.program.stage == ShaderType::TessellationControl;»
- T069 `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:1258` — «entry_ir.SetScalarReg(static_cast<IR::ScalarReg>(3),» / +1 «IR::U32(IR::Value(1u << 28u)));»
- T070 `b3dc9c67:src/graphics/host_gpu/renderer/debug.cpp:222` — «EXIT_NOT_IMPLEMENTED(rt.info.fmask_data_compression_disable != false);» / +1 «»
- T071 `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:2442` — «EXIT("render state has no valid attachments\n");» / +1 «}»
- T072 `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ResourceTracking.cpp:589` — «Fail(pc, fmt::format("{} dword {} is not a valid runtime value",» / +1 «ValueOpcodeName(expected), bad_dword));»
- T074 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:1117` — «if (!full // (descriptor.fields[6] == 0 && descriptor.fields[7] != 0) //» / +1 «(descriptor.MsaaDepth() && !IsMultisampledTexture(descriptor.Type()))) {»
- T076 `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3167` — «LOGF("\t warning: partial DrawIndirect args: vertex_count=%" PRIu32» / +1 «", instance_count=%" PRIu32 ", start_vertex=%" PRIu32»
- T079 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3005` — «// Storage views address their mip level from the surface layout and ignore max_mip, and» / +1 «// games do bind a stale max_mip together with a higher base/last level when they write the»
- T080 `b3dc9c67:src/graphics/shader/recompiler/ir/passes/SrtWalker.cpp:2354` — «static const bool compiled_enabled = [] {» / +1 «const char* value = std::getenv("KYTY_SRT_COMPILED");»
- T081 `b3dc9c67:src/graphics/shader/recompiler/ir/passes/SrtWalker.cpp:2354` — «static const bool compiled_enabled = [] {» / +1 «const char* value = std::getenv("KYTY_SRT_COMPILED");»
- T088 `b3dc9c67:src/graphics/guest_gpu/command_processor/pm4Handlers.cpp:1360` — «// The GPU reads the real values. A previous compute shader usually wrote them, so reading» / +1 «// them here page-faults on a GPU-dirty page and drains the whole GPU queue; only the»
- T089 `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3438` — «void CommandProcessor::DrawIndexAuto(DrawAutoArgs args) {» / +1 «CheckBuffer();»
- T090 `b3dc9c67:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:561` — «m_download_buffer(graphics, scheduler, MemoryUsage::Download, 32 * MiB),» / +1 «m_device_buffer(graphics, scheduler, MemoryUsage::DeviceLocal, 128 * MiB),»
- T091 `b3dc9c67:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:561` — «m_download_buffer(graphics, scheduler, MemoryUsage::Download, 32 * MiB),» / +1 «m_device_buffer(graphics, scheduler, MemoryUsage::DeviceLocal, 128 * MiB),»
- T093 `b3dc9c67:src/graphics/presentation/window/joyPump.cpp:238` — «SDL_JoystickUpdate();» / +1 «const uint64_t wall_us = NowUs() - start_us;»
- T094 `b3dc9c67:src/graphics/presentation/window/window.cpp:1001` — «SDL_SetWindowResizable(context.window, SDL_FALSE);» / +1 «context.UpdateIcon();»
- T096 `b3dc9c67:src/graphics/presentation/window/swapchain.cpp:216` — «const auto features = graphics.GetFormatProperties(format).optimalTilingFeatures;» / +1 «const auto required =»
- T098 `b3dc9c67:src/graphics/presentation/videoOut.cpp:596` — «if (compression != Graphics::VideoOutCompression::Uncompressed) {» / +1 «info.metadata.range       = {buffer.metadata_address, 0};»
- T099 `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Translate.cpp:1079` — «EXIT_NOT_IMPLEMENTED(options.wave_size != 64u // mesh.primitives_per_group == 0u //» / +1 «mesh.vertices_per_group > 64u // total_threads > 15u * 64u);»
- T101 `b3dc9c67:src/graphics/host_gpu/renderer/depthRenderTarget.h:52` — «// LoadOp clears are separate from guest depth writes.» / +1 «const bool depth_write   = depth.depth_write_enable;»
- T105 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:4132` — «PreparedBindings RenderExecutor::PrepareBindings(const ShaderStageRuntime& runtime) {» / +1 «PreparedBindings prepared;»
- T107 `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Control.cpp:311` — «const auto exec_before = ir.GetExec();» / +1 «const auto source = wide ? ReadU64(inst.src0)»
- T109 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/shaders.cpp:542` — «rasterizer.pNext = &clip_ext;» / +1 «#endif»
- T113 `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/MemoryOps.cpp:265` — «inst.glc         = ((word0 >> 14u) & 1u) != 0;» / +1 «inst.slc         = ((word1 >> 22u) & 1u) != 0;»
- T114 `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Memory.cpp:709` — «bool Translator::IMAGE_BVH_INTERSECT_RAY(const Decoder::Instruction& inst, bool node64) {» / +1 «const auto memory = MemoryInfoFromDecoded(inst);»
- T116 `b3dc9c67:src/graphics/presentation/videoOut.cpp:4048` — «KYTY_SYSV_ABI int VideoOutIsFlipPending(int handle) {» / +1 «PRINT_NAME();»
- T118 `b3dc9c67:src/libs/audio.cpp:697` — «// Emulation-speed audio sync: stretch the device-format PCM by the guest speed (float devices;» / +1 «// Kyty opens float ports as AUDIO_F32SYS). The game's audio thread then blocks on the SDL»
- T121 `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3718` — «EXIT("unknown event type\n");» / +1 «}»
- T122 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:197` — «void NameImageBinding(GraphicContext& graphics, Image& image, vk::ImageView view,» / +1 «TextureCache::BindingType type, const ImageViewInfo& view_info) {»
- T123 `b3dc9c67:src/libs/avPlayer.cpp:1843` — «h->auto_start    = auto_start;» / +1 «h->video_buffers = std::clamp(video_buffers <= 0 ? 2 : video_buffers, 2, 16);»
- T125 `b3dc9c67:src/libs/libAudio2.cpp:704` — «state->pcm_data = pcm_data;» / +1 «}»
- T128 `b3dc9c67:src/libs/avPlayer.cpp:909` — «// Guest clock (stall freezes and the emulation speed apply), so the video keeps step with» / +1 «// the game and with the time-stretched audio.»
- T129 `b3dc9c67:src/libs/controller.cpp:382` — «// Haptic PCM of the guest's vibration port, streamed to the pad. A USB DualSense is a 4-channel» / +1 «// audio device whose channels 3/4 drive the voice coils: that is how the console feels, and it»
- T131 `b3dc9c67:src/graphics/host_gpu/renderer/colorRenderTarget.cpp:290` — «EXIT("linear mipmapped render targets are unsupported\n");» / +1 «}»
- T132 `b3dc9c67:src/graphics/host_gpu/renderer/colorRenderTarget.cpp:332` — «// PPSA28068: the linear EULA target and its sampled view must share the padded pitch.» / +1 «if (!tile // volume // texture_tile) {»
- T133 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:297` — «(cached.type != requested.type && requested.extent != vk::Extent3D {1, 1, 1})) {» / +1 «return false;»
- T134 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:932` — «requested.tile_mode == cached.info.tile_mode && !requested.HasStencil() &&» / +1 «!cached.info.HasStencil() && !requested.HasMetadata() && !cached.info.HasMetadata();»
- T135 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:2258` — «void TextureCache::PrepareCmaskClear(ImageId id, const ImageDesc& desc, bool fce, DiagF5::CmuEvent* f5cmu) {» / +1 «static const bool enabled = [] {»
- T136 `b3dc9c67:src/graphics/host_gpu/renderer/cache/samplerCache.cpp:88` — «EXIT("unknown ratio: %d dwords=%08x,%08x,%08x,%08x\n",» / +1 «static_cast<int>(r.MaxAnisoRatio()), r.fields[0], r.fields[1], r.fields[2],»
- T138 `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ResourceTracking.cpp:185` — «descriptor.dwords[i] = LowerUniformPhi(handle.Arg(i).Resolve(), pc);» / +1 «}»
- T140 `b3dc9c67:src/graphics/host_gpu/regionDefinitions.h:14` — «constexpr uint64_t TRACKER_ADDRESS_SIZE = 1ull << 40u;» / +1 «constexpr size_t   TRACKER_REGION_PAGES = TRACKER_REGION_SIZE / TRACKER_PAGE_SIZE;»
- T141 `b3dc9c67:src/libs/libAmpr.cpp:1231` — «static bool AllocateAmmAutoDirectMemory(uint64_t size, int memory_type, uint64_t* dmem_offset) {» / +1 «if (dmem_offset == nullptr // size == 0) {»
- T146 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:372` — «return !m_buffer_cache.HasGpuDirtyBytes(range.address, range.size);» / +1 «}»
- T147 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3432` — «if (!image.depth_id && image.IsGpuModified()) {» / +1 «return true;»
- T149 `b3dc9c67:src/graphics/guest_gpu/command_processor/pm4Handlers.cpp:2334` — «KYTY_CP_OP_PARSER(CpOpReleaseMem) {» / +1 «Common::RbCen::Reset(Common::RbCen::Cause::Rel); // Session 133, knob "rbcen" = 2 (design133.md rev 2 s.5.2)»
- T150 `b3dc9c67:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:1668` — «: Libs::LibKernel::Memory::TryReadBacking(vaddr, mapped, size))) {» / +1 «m_stream_buffer.Commit();»
- T151 `b3dc9c67:src/graphics/host_gpu/renderer/colorRenderTarget.cpp:411` — «LOGF("RenderColorTarget: slot=%" PRIu32 " addr=0x%010" PRIx64 " size=0x%016" PRIx64» / +1 «" extent=%ux%ux%u view_mip=%u view_extent=%ux%u levels=%u pitch=%u"»
- T152 `b3dc9c67:src/graphics/shader/shader.cpp:906` — «key.push_back(resource.Stride());» / +1 «key.push_back(static_cast<uint32_t>(resource.SwizzleEnabled()));»
- T153 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5100` — «Common::LockGuard lock(m_mutex);» / +1 «if (m_program_cache->replay_active && !m_replay_hits_logged) {»
- T156 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/dualSrcBlend.h:3` — «// Track F, F4a2 (HPP-346, ROADMAP s122 p.262(b)): the translated pixel shader writes the MRT1 export as an» / +1 «// output at Location 1; the second blend source of the guest is taken to be MRT1 ([I] of p.262(b), not verified).»
- T157 `b3dc9c67:src/graphics/host_gpu/renderer/cache/samplerCache.cpp:156` — «sampler_info.mipLodBias =» / +1 «static_cast<float>(static_cast<int16_t>((r.LodBias() ^ 0x2000u) - 0x2000u)) / 256.0f;»
- T159 `b3dc9c67:src/libs/libAmpr.cpp:1988` — «return AppendNoOpCommand(command_buffer, 0x20);» / +1 «}»
- T160 `b3dc9c67:src/common/profiler.cpp:58` — «if (Config::ProfilerEnabled() && !tracy::ProfilerAvailable()) {» / +1 «tracy::StartupProfiler();»
- T163 `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:335` — «void GuestGpu::Done() {» / +1 «GpuMutexLock lock(m_submission_mutex);»
- T167 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:1145` — «EXIT("unsupported sampled depth image: resource=%d encoding=%d view=%d "» / +1 «"class=%u numeric=%u dimension=%u mip_mode=%u read=%d written=%d atomic=%d compare=%d "»
- T169 `b3dc9c67:src/graphics/shader/shader.cpp:222` — «static uint64_t CachedShaderHash(uint64_t shader_addr, std::span<const uint32_t> code) {» / +1 «const auto code_size = static_cast<uint32_t>(code.size_bytes());»
- T172 `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ConstantPropagation.cpp:207` — «// Known-value sets: a small over-approximation of the values a U32 can take, derived from bit-field» / +1 «// extracts / masks and integer arithmetic on them. 'IEqual(x, c)' folds to false when c is not in the set.»
- T174 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5567` — «static_params.color_srcblend[slot]       = bc.color_srcblend;» / +1 «static_params.color_comb_fcn[slot]       = bc.color_comb_fcn;»
- T177 `b3dc9c67:src/graphics/host_gpu/regionManager.h:196` — «[[nodiscard]] bool IsModified(uint64_t offset, uint64_t size) const {» / +1 «const auto [start, end] = GetPageRange(m_cpu_addr + offset, size);»
- T178 `b3dc9c67:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:722` — «constexpr uint64_t WindowSize   = 512 * 1024;» / +1 «const auto         buffer_begin = buffer.CpuAddress();»
- T179 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:2971` — «if (!DecodePackedColorClear(image.info.pixel_format, packed_clear, clear.color)) {» / +1 «g_last_clear_outcome = "decode";»
- T185 `b3dc9c67:src/graphics/presentation/window/joyPump.cpp:351` — «LOGF("FixF24: open failed instance=%d error=\"%s\"\n", static_cast<int>(id), SDL_GetError());» / +1 «}»
- T187 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:1024` — «TextureCache::OverlapResult TextureCache::ResolveOverlap(const ImageInfo& requested,» / +1 «BindingType binding, ImageId cached_id,»
- T188 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3400` — «if (image.depth_id // !image.Overlaps(address, size)) {» / +1 «continue;»
- T190 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp:717` — «words = {spv::OpImageDrefGather,» / +1 «TypeF32Vector(state, 4),»
- T191 `b3dc9c67:src/graphics/guest_gpu/gpu_format.cpp:64` — «{BufferFormat::k8Srgb, 1, 0, 0, true, false},» / +1 «{BufferFormat::k8_8Srgb, 2, 0, 0, true, false},»
- T192 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:1024` — «TextureCache::OverlapResult TextureCache::ResolveOverlap(const ImageInfo& requested,» / +1 «BindingType binding, ImageId cached_id,»
- T199 `b3dc9c67:src/graphics/presentation/window/window.cpp:467` — «EXIT_IF(new_width == 0 // new_height == 0);» / +1 «Common::LockGuard lock(mutex);»
- T200 `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/ScalarAluOps.cpp:91` — «{0x13u, Opcode::S_SETREG_B32}, {0x17u, Opcode::S_WAITCNT},    {0x18u, Opcode::S_WAITCNT},» / +1 «{0x19u, Opcode::S_WAITCNT},    {0x1au, Opcode::S_WAITCNT},»
- T203 `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Integer.cpp:500` — «const auto byte_offset  = ir.BitwiseAnd(ReadU32(inst.src2), IR::U32(IR::Value(31u)));» / +1 «const auto bit_offset   = ir.ShiftLeftLogical(byte_offset, IR::U32(IR::Value(3u)));»
- T212 `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ConstantPropagation.cpp:207` — «// Known-value sets: a small over-approximation of the values a U32 can take, derived from bit-field» / +1 «// extracts / masks and integer arithmetic on them. 'IEqual(x, c)' folds to false when c is not in the set.»
- T213 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:851` — «const bool ok = Libs::LibKernel::Memory::TryReadGpuCleanBacking(address, value, sizeof(*value));» / +1 «if (cache != nullptr && cache->log != nullptr) {»
- T214 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:830` — «bool ReadShaderGuestMemory(void* userdata, uint64_t address, uint32_t* value) {» / +1 «auto* cache = static_cast<ShaderReadCache*>(userdata);»
- T215 `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Control.cpp:261` — «if (IsExecOrVcc(inst.dst)) {» / +1 «WriteMask(inst.dst, selected_mask, true);»
- T216 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp:1518` — «AtomicUpdate(ctx.state, pointer, mem.kind, merge);» / +1 «}»
- T217 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterMesh.cpp:39` — «EXIT("unsupported mesh output kind=%u\n", static_cast<uint32_t>(output.kind));» / +1 «}»
- T219 `b3dc9c67:src/loader/runtimeLinker.cpp:1531` — «PreloadAdjacentPrograms();» / +1 «RelocateAll();»
- T221 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp:397` — «EXIT_IF(Prospero::SampledTextureNumericClass(format) != Prospero::TextureNumericClass::Uint //» / +1 «Prospero::RemapTextureFormat(format) == format //»
- T223 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:5176` — «void RenderExecutor::RebindImages(PreparedBindings& prepared) {» / +1 «KYTY_PROFILER_FUNCTION();»
- T224 `b3dc9c67:src/graphics/host_gpu/renderer/renderDraw.cpp:2952` — «std::printf("Skipping draw with unknown primitive type: %u\n",» / +1 «static_cast<uint32_t>(ucfg.GetPrimType()));»
- T228 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:1024` — «TextureCache::OverlapResult TextureCache::ResolveOverlap(const ImageInfo& requested,» / +1 «BindingType binding, ImageId cached_id,»
- T229 `b3dc9c67:src/graphics/host_gpu/vulkanCommon.cpp:50` — «{Prospero::BufferFormat::k10_10_10_2SNorm, vk::Format::eA2B10G10R10SnormPack32},» / +1 «{Prospero::BufferFormat::k10_10_10_2UInt, vk::Format::eA2B10G10R10UintPack32},»
- T231 `b3dc9c67:src/libs/libFont.cpp:802` — «return static_cast<float>(std::clamp(static_cast<int>(scale + 0.5f), 8, FONT_BITMAP_MAX_DIM));» / +1 «}»
- T233 `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Vector.cpp:414` — «case O::V_MAC_F32: return FloatTernary(inst, IR::ValueOpcode::FPFma32, true, true);» / +1 «case O::V_MADMK_F32:»
- T234 `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/MemoryOps.cpp:197` — «case Opcode::DS_MAX_F32: return 3u;» / +1 «case Opcode::DS_BPERMUTE_B32: return 2u;»
- T237 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/SpirvEmitter.h:18` — «// fp32 denormals (the game runs with FLOAT_MODE 0xc0: flushed). shaderDenormFlushToZeroFloat32 ->» / +1 «// the module declares DenormFlushToZero; else !shaderDenormPreserveFloat32 (NVIDIA: neither is»
- T240 `b3dc9c67:src/graphics/host_gpu/renderer/image/imageInfo.h:458` — «case vk::Format::eR16Sfloat: next.float32[0] = DecodeHalfBits(packed & 0xffffu); break;» / +1 «case vk::Format::eR16G16Sfloat:»
- T241 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5635` — «static_params.depth_min_bounds         = depth.depth_min_bounds;» / +1 «static_params.depth_max_bounds         = depth.depth_max_bounds;»
- T242 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:4913` — «void RenderExecutor::FindBuffers(PreparedBindings& prepared) {» / +1 «KYTY_PROFILER_FUNCTION();»
- T243 `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3126` — «// GPU-side indirect draw: the arguments are usually written by a culling compute shader in» / +1 «// the same frame, so reading them here page-faults on a GPU-dirty page and drains the whole»
- T244 `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/MemoryOps.cpp:346` — «if (dlc != 0 // lds != 0 // inst.glc // inst.slc // seg == 3u) {» / +1 «SetUnsupported(inst, Family::FLAT, opcode, "FLAT modifiers or segment are not implemented");»
- T246 `b3dc9c67:src/kernel/eventQueue.cpp:94` — «int KernelEqueuePrivate::GetTriggeredEvents(KernelEvent* ev, int num) {» / +1 «Common::LockGuard lock(m_mutex);»
- T250 `b3dc9c67:src/graphics/presentation/window/window.cpp:1979` — «const bool title_async  = !loop_running // Common::Gates::Value(Common::Gates::Knob::TitleAsync) != 0;» / +1 «const auto title_t0    = Common::FrameStats::NowNs();»
- T251 `b3dc9c67:src/graphics/guest_gpu/command_processor/pm4Handlers.cpp:194` — «EXIT_NOT_IMPLEMENTED(r.copy_depth_to_color // r.copy_stencil_to_color);» / +1 «»
- T255 `b3dc9c67:src/graphics/shader/recompiler/ir/passes/ShaderInfoCollection.cpp:378` — «AddOutput(info, StageOutputKind::Mrt, export_info.index, export_info.index,» / +1 «fmt::format("out_mrt_{}", export_info.index));»
- T256 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterFlow.cpp:291` — «MrtOutputMode(state, exp) == 5u ? GLSLstd450UnpackUnorm2x16 : GLSLstd450UnpackHalf2x16;» / +1 «uint32_t f32[4] = {ConstantF32(state, 0), ConstantF32(state, 0), ConstantF32(state, 0),»
- T257 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterProgram.cpp:143` — «if (ctx.other_half == nullptr //» / +1 «info.terminator.condition == CFG::BranchCondition::ScalarInstruction //»
- T258 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:903` — «: context.GetBufferCache().ObtainBuffer(address, size, resource.written, resource.formatted, id, true);» / +1 «if (b2r_mode != 0) [[unlikely]] {»
- T259 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3220` — «bool BufferCache::SynchronizeBufferFromImage(Buffer& buffer, uint64_t vaddr, uint64_t size) {» / +1 «const auto selected = m_texture_cache.FindImageFromRange(vaddr, size);»
- T260 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:903` — «: context.GetBufferCache().ObtainBuffer(address, size, resource.written, resource.formatted, id, true);» / +1 «if (b2r_mode != 0) [[unlikely]] {»
- T263 `b3dc9c67:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:100` — «void BufferCache::WriteDataBuffer(Buffer& buffer, uint64_t address, const void* source,» / +1 «uint64_t size) {»
- T265 `b3dc9c67:src/libs/libAmpr.cpp:96` — «static uint32_t ComputeFileId(const char* guest_path) {» / +1 «uint32_t hash = 2166136261u;»
- T270 `b3dc9c67:src/libs/libSysmodule.cpp:25` — «static KYTY_SYSV_ABI int SysmoduleLoadModule(uint16_t id) {» / +1 «PRINT_NAME();»
- T271 `b3dc9c67:src/libs/libSystemService.cpp:156` — «return SYSTEM_SERVICE_ERROR_NO_EVENT;» / +1 «}»
- T272 `b3dc9c67:src/libs/libPad.cpp:39` — «info->state[0] = 0;» / +1 «info->state[1] = 0;»
- T277 `b3dc9c67:src/libs/controller.cpp:1424` — «return handle;» / +1 «}»
- T283 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterAluHelpers.cpp:104` — «F32Class EmitClassifyF32Bits(EmitterState& state, uint32_t bits) {» / +1 «F32Class cls;»
- T284 `b3dc9c67:src/libs/agc.cpp:1746` — «uint32_t* KYTY_SYSV_ABI AgcCbNop(CommandBuffer* buf, uint32_t size_in_dwords) {» / +1 «if (buf == nullptr // size_in_dwords < 2) {»
- T291 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterHelpers.cpp:92` — «DppTargetLane EmitDppTargetLane(EmitterState& state, uint32_t control) {» / +1 «const auto subid = EmitSubgroupLocalInvocationId(state);»
- T295 `b3dc9c67:src/graphics/guest_gpu/tile.cpp:306` — «Prospero::RenderTargetBytesPerElement(format) != element.bytes) {» / +1 «return false;»
- T296 `b3dc9c67:src/graphics/guest_gpu/gpu_format.cpp:23` — «{BufferFormat::k8SNorm, 0, 0, 1, false, false},» / +1 «{BufferFormat::k8UInt, 1, 0, 1, true, true},»
- T298 `b3dc9c67:src/libs/avPlayer.cpp:963` — «retired_video.push_back(std::move(current_video->buffer));» / +1 «if (retired_video.size() >= static_cast<size_t>(max_video_buffers - 1)) {»
- T300 `b3dc9c67:src/graphics/shader/recompiler/ir/passes/SrtWalker.cpp:2354` — «static const bool compiled_enabled = [] {» / +1 «const char* value = std::getenv("KYTY_SRT_COMPILED");»
- T301 `b3dc9c67:src/graphics/host_gpu/renderer/depthRenderTarget.cpp:370` — «if (rc.copy_depth_to_color // rc.copy_stencil_to_color // rc.copy_centroid //» / +1 «rc.copy_sample != 0 // dc.zfunc > static_cast<uint8_t>(vk::CompareOp::eAlways) //»
- T304 `b3dc9c67:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3104` — «if (!resource.r128 && descriptor.MetaCompress() && tile != Prospero::TileMode::kDepth &&» / +1 «!desc.info.IsDepth()) {»
- T306 `b3dc9c67:src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp:781` — «uint32_t              operand_mask = 0;» / +1 «std::vector<uint32_t> operands;»
- T309 `b3dc9c67:src/libs/libAmpr.cpp:2560` — «LIB_FUNC("4fgtGfXDrFc", Ampr::MeasureCommandSizeFixed32);» / +1 «LIB_FUNC("gAtc79UTt5E", Ampr::MeasureCommandSizeFixed32);»
- T311 `b3dc9c67:src/graphics/guest_gpu/graphicsRun.cpp:3540` — «Sync::WriteAtEndOfPipe32(m_submit_id, CurrentBuffer(), dst, data);» / +1 «}»
- T312 `b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:4019` — «void TextureCache::RunGarbageCollector() {» / +1 «std::scoped_lock lock {m_lock};»

## 12. Сомнения и долги исполнителя

1. Отношение к ASTRO BOT для HLE-тем (`sys-*`, `av-*`) — импорт NID [c] плюс вывод [I]: логи игры не печатают вызовы HLE, факт вызова виден
   только по строкам `LOG` разрешённых функций. Сильнейшие Г с U (§5) — путь, возможно, исполняется (например темы `img-*` о трафарете и
   BC-алиасах, `rnd-*` о RectList/PM4 CHAIN, `ir-tdesc-valid`).
2. Отсутствие фатала по логам покрывает только пройденные уровни (59 входивших из 114) — такие Г помечены I, не c.
3. Класс ставится на коммит целиком; в смешанных коммитах (`0791f921f`, `89792a3bc`, `bec67b786`, `e6cb880ad`) части расписаны в `relevance`
   (`upstream_detail.tsv`) и в `m883.md`.
4. Направление ISA для `DS_MAX_F32` (наш порядок сравнения против документа) — [I]; довод `T234` опирается на код игры (data1 = регистр адреса).
5. Пары «коммит + revert» (`cd9fc6ff2`/`266c12cec`, `5b68a26cc`/`1c301c9aa`, `165234b15`/`c2b7b0b58`) — Г с [c] (итог 0 изменений).
6. Пересечение мест (`overlap.tsv`) — механика по координатам базы с допуском 3 строки; файлы `tests/` шумят (регистрация фикстур в конце файла),
   в §6 не учитываются.
7. Пробной сборки не было (п. 752(г)(7) — по желанию исполнителя); выводы о компиляции тестов — [I].

## 13. Не заявляется

Что upstream лучше или хуже нашего; что перенос любой темы что-то исправит у нас; что кандидаты А дают видимый дефект ASTRO BOT; что темы Г
с уверенностью U игрой не исполняются; что опись полна по смыслу внутри больших коммитов; что CI или тесты upstream проходят у нас; ни одно
число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется.
