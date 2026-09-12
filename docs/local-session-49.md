# Сессия 49 — WIP: память сцены Sky Garden, CPU и дефекты листвы

2026-09-12, база `6f67816`, ветка `merge-upstream`. Работа продолжается; **60 FPS не достигнуты**.
Этот checkpoint не объявляет изображение исправленным и не закрывает редкое зависание галактики.
Локальные материалы: `C:/kyty/s49/`; текущее подробное состояние — `STATE_1925.md`.

## Подтверждённые изменения

RenderDoc-захват `kyty_1789223444252358_capture.rdc` показал повторную загрузку одинаковых
полных 4K BC5 цепочек по 22 МБ, хотя view ограничен MIN_LOD=5, а соседние гостевые
текстуры расположены через 64–128 КБ. Выбранные мипы занимают префикс 64 КБ.
`KYTY_RESIDENT_MIPS` (по умолчанию включён) ограничивает источник чтения, отслеживание
CPU-записей и пересечения этим префиксом для sampled BC 2D, одного слоя, без metadata.
Размеры Vulkan-изображения и исходные номера mip сохраняются. При снижении MIN_LOD
источник расширяется и данные загружаются заново; одновременные bindings сохраняют
объединение нужных уровней. Явные копии консервативно восстанавливают полный источник.

На раннем тяжёлом участке uploads около 170490 -> 100800 КБ/present, detile 104 -> 33.
Это не обеспечивает заметного общего ускорения: CPU около 82 мс, GPU около 23 мс.
Первый прогон с этой правкой позднее упал до 2 FPS и завершился ошибкой выделения
Vulkan-изображения. Heap0 usage 16,609,697,792 байта при budget 15,423,426,510;
allocation 15,343,973,520. В frame18618 GPU607 мс, большое время внутри загрузки/детайлинга.
Это отличается от редкого зависания галактики, после которого пользователь сбрасывал драйвер.

Найдена и воспроизведена ошибка GC: фиксированная первая партия старых изображений,
которые нельзя удалить, закрывала доступ к остальным кандидатам. `KYTY_IMAGE_GC_PROGRESS`
(по умолчанию включён) переносит срок следующей проверки пропущенного кандидата,
не меняя реальные frame/submission последнего использования. GPU-содержимое сохраняется.
В контрольном тесте 40 защищённых tiled GPU images блокируют 8 удаляемых; старый путь
падает, новый удаляет 8 и сохраняет 40. `KYTY_IMAGE_GC_PROGRESS=0` — контроль.

`KYTY_IMAGE_GC_FRAME_GUARD=1` защищает текущий и предыдущий present при обычном GC;
критический проход по-прежнему может вытеснять. Пока это opt-in. Новый длинный прогон
с progress+guard удержал usage Vulkan около9.1 ГБ до +3170 кадров после первого MeshRestart;
предыдущий завершился на +1937. NVIDIA около11.6–11.7 ГБ. Поздние положения камеры различаются,
это не идеальная повторяемая пара. Последний прогон закрыт через WM_CLOSE, exit0.

## CPU и диагностика

- Windows x64 native SRT plan (Xbyak) — только `KYTY_SRT_NATIVE=1`, по умолчанию выключен.
  Сохраняет порядок callbacks, статусы, перенос неподдержанных участков в интерпретатор,
  восстановление после ошибок и unwind info. Синтетика примерно919–923 ->703–713 нс.
  AUDIT всегда отдаёт игре portable-результат, сравнивая native на записи чтений;
  более1.9 млн проверок без расхождений. Прямой native запуск один раз завис в галактике;
  такой же сбой был и с native0. Причина не установлена, безопасное включение не заявлено.
- Кэш команд динамического состояния Vulkan: `KYTY_DYNAMIC_STATE_CACHE=0` — контроль.
  Сброс на новом command buffer и utility blit, отдельная инвалидация color-write.
  d_emit примерно6.55 ->4.65 мс; общий выигрыш этой правки устойчиво не установлен.
- Объединённая проверка CPU-dirty/GPU-clean буфера с одной блокировкой региона:
  `KYTY_BUFFER_COMBINED_QUERY=0` — контроль, по умолчанию включена; тесты пройдены.
- `KYTY_FRAME_TRACE=lite` отключает подробные часы, сохраняя счётчики.
  Семплер имеет файл-gate, в выключенном состоянии поток игры не приостанавливает.
- `KYTY_GPU_CHECKPOINTS=nv`: маркеры NVIDIA без breadcrumb draw-барьеров.
  Долгое ожидание печатает CPU-историю, это НЕ доказательство выполнения GPU.
  Данные NV спрашиваются только после DeviceLost. Reset драйвера пользователем
  сам создаёт DeviceLost и не доказывает исходную причину зависания.
- Image lifetime/source/memory diagnostics доступны через соответствующие `KYTY_IMAGE_*_TRACE`.

Обычная база без подробных таймеров:13.23/13.68/13.09 FPS (запись включена).
Полные таймеры, resident:11.81/12.48/9.76; progress+guard+state cache:
12.26/13.05/12.63. State-cache off контроль: первое окно12.10 FPS, CPU82.23 мс,
GPU22.85 мс. Три окна по300 present от первого MeshRestart +120/+420/+720;
использовать JSON в s49 для точных данных и различий draw. Всё ещё около6000 draw.
Проба single-map backing fast path не дала выигрыша на стенде и удалена;
`rejected_single_map.patch` сохранён отдельно. В исполняемом коде её нет.

## Изображение — открытый дефект

Пользователь подтвердил: листва слишком яркая относительно видео PS5; при полёте
волной меняет цвет к эталону, исчезает и возвращается яркой. Это воспроизводится
с отключённым кэшем динамических команд. Причина пока не доказана.

Глобальный A-B-A сканер вернул 0 кандидатов для resident18641 и progress19912 кадров,
decode clean, НО он пропускает локальные дефекты. Новый `review_local.py` проверяет
малые области. На progress video17177/present17178 правая крона становится почти
чёрной на кадр; video17242/present17243 меняется несколько крон. Есть повреждения
подсказки (белые/чёрные прямоугольники), воспроизведённые и в plain-записи до правок.
Часть локальных кандидатов — нормальные листья/частицы; необходимо визуально разбирать.
**Не объявлять эти видео чистыми по нулю глобальных кандидатов.**

Новый RenderDoc-прогон (19:25) завис до MeshRestart, последний present17517;
пользователь сбросил драйвер. NVIDIA было около9.3 ГБ, это не переполнение памяти.
Приоритетный CPU worker ждал master tick552258 при known552257; источник задержки
пока не определён. NV markers под RenderDoc вернулись как foreign pointers, не декодированы.
Автоматический capture не используется.
Клавиатурный ввод не записывается: пользователь сам заходит в уровень.

## Проверки и ограничения

ResidentMipUpload прошёл Vulkan + synchronization validation: отображены только128 КБ
при логическом размере22 МБ, источники64/128 КБ, соседние текстуры, изменение MIN_LOD,
несколько bindings. Теперь адресно-зависимый узор всех mip5..12 и4..12 сравнивается
с CPU tiling reference. Это проверка detile/upload, не sampling EXT minLOD: harness
не включает feature, тест не создаёт соответствующий view.
GC progress/frame, sparse MRT, polygon mode, read-only depth, views, packed textures,
BDA — фокусные проверки пройдены. У sparse возможны ожидаемые unused-output warnings.
SRT tests, mixed/failure/exception/native audit, memory tracker пройдены.
Shader suite:123 passed, известный IMAGE_SAMPLE_C fail,4 не собраны для Windows.
Buffer-cache GC test падает на adjacent download reservation stride также со всеми
новыми переключаемыми путями выключенными; старый бинарь отдельно не проверен.
Полная Vulkan/sync проверка нового игрового маршрута не выполнена. Большая suite не чистая.
Seed не обновлялся. Редкий hang на появлении первого уровня созвездия Гориллы открыт.
Push не выполнялся; посторонние удаления PNG в nlohmann_json не затронуты.


## Продолжение: безопасное получение диагностических данных

В `tools/windows_hang_dump.cpp` добавлена внешняя утилита Windows x64: minidump + стеки
потоков через DbgHelp, без GPU API. `tools/watch_emulator.py` контролирует только PID
эмулятора рядом с заданным журналом, сохраняя process handle. После frame14000 и12сек
без новых кадров делает снимок, отправляет WM_CLOSE, через5сек при необходимости
завершает этот процесс. Запись пользовательского RenderDoc capture исключается из
контроля; ввода и автоматического F1 нет. Тест отдельного процесса подтвердил исключение
capture, возобновление наблюдения, снимок стеков и закрытие только тестового процесса.
Это не гарантия восстановления самого драйвера при настоящем GPU hang.
Инструкция — `tools/windows-hang-diagnostics.md`, локальный бинарь `s49/windows_hang_dump.exe`.

Системные TdrDelay/TdrDdiDelay прочитаны:60/60, не менялись.
Сейчас диагностический повтор19:49 с `KYTY_ASYNC_COPY_GPU_WAIT=0` (копии ждёт CPU),
native0,dynamic0,combined1,GC progress1+guard1,resident1, --rd, lite trace иNV markers.
Наблюдатель активен, map сохранён в `s49/foliage_safe.map`. Это контроль, не исправление hang.

Старый захват разобран без игры: `s49/foliage_baseline/`, 328 превью текстур.
Кандидаты листвы: textures738941/728384 -> PS1a4e22aaa15d8ab3 (SPIR-V08b6b9f...);
texture739330 -> PSaef08e7e8c990db9 (SPIR-V256d733e...). Файлы SPIR-V побайтово найдены
в текущем shader cache. У этих текстур в старом захвате MIN_LOD=0. Данных нового
захвата с яркой листвой пока нет; причина яркости/исчезновений не установлена.


## Подтверждённый пересвет листвы и сохранение GPU-изображений

Пользовательский capture `kyty_1789235743603059_capture.rdc` (6360698028 байт)
успешно записан в диагностическом запуске с ожиданием async-copy на CPU. Память,
текстуры, шейдеры и параметры сопоставлены со старым захватом. Все мипы цветовых
текстур и карт нормалей двух проверенных материалов совпадают побайтово, как и
PS/VS. Однако новый MRT3 содержал яркую листву вместо почти нулевых значений.
Термин свечения зависит от VS-текстуры воздействия на растительность. В новой
текстуре воздействия видны фрагменты изображения сцены; их нет в старой.

Буфер-источник воздействия — 1024x1024 RGBA16F, guest0x516830000. В прежнем прогоне
GC многократно удалял и создавал его. Причина в условии SafeToDownload: изменённый
буфер с пересекающимся диапазоном запрещал readback, после чего GC удалял даже
актуальное GPU-изображение. Это не доказывает, что буфер содержит последние записи
рендеринга. `KYTY_IMAGE_GC_PRESERVE_GPU` (по умолчанию1) сохраняет tiled GPU image,
если оно само не помечено изменённым CPU/буфером, независимо от старой dirty-записи
буферного alias. Контроль0 воспроизводит потерю в отдельном тесте.

Тест ImageGcProgress с dirty buffer alias проходит; старый путь падает. Frame guard,
resident mips, read-only depth проходят Vulkan+sync. DCC fixed clear/SampledDccClear
проходят, но группа далее падает на прежнем over-wide storage mip с Vulkan00958,
воспроизведённом и с PRESERVE_GPU=0. Группа не объявляется чистой.
В реальном журнале ImageGcKeepOverlap срабатывает именно для0x516830000.
В повторном обычном прогоне пользователь подтвердил: **цвет листвы стал правильным**.
Память Vulkan держалась около9.0 ГБ, до lastFrame20748 от Mesh16686 (+4062).
Видео rec_preserve_retry.mp4:20761 кадров, decode0, глобальных A-B-A кандидатов0,
но локальные дефекты подсказки и исчезновение крон остаются. Первое тяжёлое окно
12.06 FPS, CPU82.32 мс, GPU23.02 мс. До60FPS всё ещё далеко.

Пользователь уточнил оставшийся эпизод в замедленном flight_wave_review.mp4:
6сек крона есть,7сек исчезает,8сек возвращается (дерево справа под подвешенной площадкой).
В исходном видео это примерно16800–16860: крона редеет с16836, почти отсутствует
около16844–16856, возвращается16858. Ствол/основа остаются. marked_crown_frames.jpg
создан из видео. Сборка с сохранением GPU-данных этот дефект ещё не исправила.
Проверяются LOD-переход/отсечение прозрачных пикселей; не выдавать гипотезу за причину.

## Исправления диагностики после повторного hang

Первый запуск PRESERVE_GPU1 завис до уровня (present17052, GPU worker wait436701,
known436700). Наблюдатель не получил дамп: вызов nvidia-smi завис внутри обработки
таймаута. Даже такой внешний запрос нельзя делать в основном цикле наблюдения.
Теперь watcher читает уже записанные VMA-сэмплы, не обращаясь к драйверу, а после
снимка зависшего процесса вызывает TerminateProcess напрямую без оконных API.
Отдельный тест capture exemption/снимка/завершения прошёл повторно. Здоровый снимок
реального эмулятора также выполнен успешно (healthy_preserve_retry.dmp,538277 байт),
выполнение продолжилось. Эпизод настоящего hang с новым watcher пока не пойман.

`foreign marker` был ошибкой нашего вызова Vulkan-Hpp, а не установленной проблемой
RenderDoc: setCheckpointNV(&record) выбирал T const& и передавал адрес временного
указателя. Явное const void* выбирает корректную перегрузку. SDK-тест без GPU:
старый вызов preserved=0, исправленный preserved=1. NV-данные всё ещё запрашиваются
только после DeviceLost. Само редкое зависание пока не исправлено.

## Текущая диагностика оставшегося исчезновения

Добавлено хранение DB_ALPHA_TO_MASK в HW::Context (прямой и indirect обработчик),
без изменения Vulkan-отрисовки. `KYTY_ALPHA_TRACE=1` записывает это значение и
ALPHA_TO_MASK_DISABLE у двух материалов листвы. Ранее регистр просто игнорировался;
проверяется, задействован ли он в проблемной сцене. Native alpha-to-coverage ещё
НЕ включён/НЕ реализован. `KYTY_DUMP_GCN=1` теперь сохраняет исходный код и при
первом фактическом использовании шейдера из translation cache, не только при новой
трансляции. Спекулятивный PM4 lookahead не считается первым использованием.
Запуск alpha_trace начат22:05:57, под исправленным watchdog. Пользователь навигирует.

## Offline foliage analysis after alpha_trace (2026-09-12, late session)

alpha_trace was closed with WM_CLOSE at22:14; no emulator remains from that run.
Saved log_alpha_trace.txt, stdout_alpha_trace.txt, rec_alpha_trace.mp4. Actual leaf
DB_ALPHA_TO_MASK=0xAA00 (enable bit0 is clear); no forced alpha-to-coverage change.
Offline PS1a4e22aaa15d8ab3 reproduces captured SPIR-V byte-for-byte (SHA25608b6b9f...).
KYTY_RECOMPILE_DUMP now saves decoded RDNA2 and IR; KYTY_CFG_BENCH_DECODE prints
raw decoded vertex instructions without requiring vertex fetch reconstruction.

RenderDoc capture1789235743603059: depth VS e26e4d0ba9675ff2, material VS ae4cca3e4bf70904.
Most corresponding finite positions match bit-for-bit; a few x/y rounding differences
exist, so this is not a blanket proof of depth invariance. More importantly, draw237110
has4872 referenced vertices, ALL positions NaN. DebugVertex(0,0,27718,0) traced the FIRST
NaN to VS texture sample %4734 at UV(0.7420871854,2.0451242924), image2988 (wind field).
Its source image827034 already contains36864 pixels with repeated dword0xFFFFFFF0:
512x64 block at x512..1023,y0..63 plus64x64 at x0..63,y64..127. The SAME bits/regions
occur in older capture1789223444252358. Do not attribute them to the later GC color fix.
This pattern resembles a metadata fill; its producer/ownership mistake is not yet proven.

Controlled offline probe only (NOT in emulator): sanitizing NaN at four wind CS texelFetch
results restores4872/4872 vertices to finite positions. Original and unmodified GLSL
roundtrip BOTH retain4872/4872 NaN. Artifacts: foliage_offline/nan_probe.log,
vertex_debug.log, geometry_all.log, vertices.rdna2, position_comparison.txt.
This establishes a concrete disappearing-geometry mechanism in the capture, not yet
confirmation that every user-marked video disappearance has the same cause.
No NaN clamp/workaround has been added to the runtime shader compiler.

New opt-in diagnostics: KYTY_IMAGE_WATCH=<guest address> logs upload, native clear,
CPU invalidation and GPU-buffer invalidation of containing images, including metadata;
KYTY_CLEAR_TRACE=1 records every recognized uniform buffer fill, with frame and shader.
Build succeeded. Next: trace creation/clearing of the interaction input at0x516830000,
identify why0xFFFFFFF0 reaches color data, fix ownership/clear and validate with video.
60FPS still unmet; usual scene CPU~82ms/~6000draw. Rare entry hang remains unresolved.
