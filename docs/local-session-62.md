# Сессия 62 — прямые записи в пакет (`recimg`, `recup`), потолок memo копий констант, вход в Sky Garden без зависания

База: `merge-upstream`, HEAD сессии 61 — `ce70bbc`. Итоговый коммит — см. конец отчёта. Push нет.

## 1. Главный результат

- **Пункт 2 реализован: два крупнейших сайта прямых записей draw-потока стали записями кольца.**
  Гейт `recimg` (`KYTY_RECORD_IMAGE_BARRIERS`): `Image::Transit` с ленивым хэндлом
  (`CommitBindings`, `AcquireRenderTargets`) публикует закрытие прохода и `vkCmdPipelineBarrier2`
  как записи `RecordOp::ImageBarriers`; гейт `recup` (`KYTY_RECORD_UPLOADS`):
  `BufferCache::RecordBufferCopies` — как `RecordOp::BufferUpload` (барьер, `vkCmdCopyBuffer`,
  барьер на потоке записи). В Sky Garden `rec_direct` **800 → 270** на кадр, на пустыне 362 → 94.
- **Замер (свип `sky62b`, 19 фаз по 500 present, полоса 4700–5100, базы 6,53–6,63 мкс/draw,
  спред ±1 %, троттлинга нет):** `recimg`+`recup` **−1,7 / −0,2 / −0,5 %**, с `recpubn=16`
  **−0,4 / −1,7 / −2,6 %**, с `recpubn=4` −1,0 / −0,8 / −0,5 %. Знак один и тот же во всех девяти
  фазах (и по FPS: +0,3…+2,3 %), но порог ±1,4 % тремя повторами не держит ни одна конфигурация;
  во второй полосе 5100–5500 знаки уже разные (`both` −2,3 / +1,1 / +1,3). **Все три остаются 0.**
  Пустыня (поток записи включён, `KYTY_GPU_TIME` снят): пара −2,9 / −2,4 / −1,8 %, с `recpubn=16`
  −3,4 / −3,8 / −2,5 % — там прямых записей на draw в шесть раз больше.
- **Пункт 3 закрыт потолком.** Копии гостевых диапазонов в stream-кольцо в Sky Garden — это не
  720 КБ `cb_copy`, а **10–13 тыс. копий и 15–18 МБ на кадр** пути `ObtainBuffer` (CPU-грязное
  чтение ≤ 16 КБ, счётчики `ob_stream`/`ob_stream_kb`, раньше не считался) плюс 7,5 тыс. const-bank
  копий. 84 % копий байт-в-байт равны предыдущей копии того же диапазона, но (а) эпоха региона по
  построению не свидетель для грязной (записываемой без fault'а) страницы — хотя `cb_diff_ep` = 0
  на 2,2 млн копий, — и (б) честная проверка содержимого стоит **4,2 мс на кадр** (`cb_stat_us`),
  столько же, сколько чтение при копии: memo сэкономило бы только запись в WC-память кольца.
- **Вход в Sky Garden — 2 из 2 без зависания**, включая первый вход после свежей сборки с
  `KYTY_GPU_CHECKPOINTS=1 KYTY_GPU_HANG_ABORT_S=0` (§5). Правило сессии 61 «первый вход после
  сборки виснет» не подтвердилось; механизм по-прежнему не назван — зависание перемежающееся
  (сессия 61: 2 из 2 первых входов, сессия 62: 0 из 1).
- **Таблица прямых записей по сайтам** (`FrameTrace-direct:`, ключ — адрес возврата `Handle()`,
  разбор `direct_sites.py`) — в §3.
- Базы `sky62b`: **6,53–6,63 мкс CPU на draw, 30,2–30,4 FPS, CPU потока GuestGpu 32,5–32,6 мс, GPU
  14,2–14,7 мс, ~4 950 draw.** 60 FPS нет.

## 2. Пункт 2: `recimg`, `recup` — реализация

`Image::Transit(…, command_buffer = {}, why, atomic_write, packet_ok)`: при `packet_ok`, включённом
`recimg` и `PacketsWanted()` (поток записи, `recpack`, профилировщик GPU-времени выключен) вместо
`m_scheduler.EndRendering(why)` + `Current().Handle().pipelineBarrier2()` — `EndRenderingPacket(why)`
и `PushImageBarriersPacket(barriers)`. Состояние layout'ов (`GetBarriers`) по-прежнему меняется на
разрешающем потоке, запись несёт копию `vk::ImageMemoryBarrier2[]` (8-выровнена на месте, как
`RecordOp::Bindings`). `RecordBufferCopies`: `EndRenderingPacket(BufferUpload)` +
`PushBufferUploadPacket(source, buffer.Handle(), buffer.Size(), copies)`; поток записи воспроизводит
ровно три вызова прямого пути. Обе записи ≥ `PassEnd` — дросселируются `recpubn` и публикуются
`Handle()`/submit'ом как остальные. `KYTY_RECORD_CHECK=1` на пустыне (свип `rk`, дымовой `smoke`) —
0 нарушений.

**Ревью агентом — один реальный дефект, исправлен до Sky Garden:** прямой путь draw
(`renderDraw.cpp:2057`, mesh + primitive restart, legacy quad list) берёт `Handle()` до
`CommitBindings` и держит его через цикл переходов — при `recimg` там публиковались бы записи под
живым хэндлом. `CommitBindings` теперь передаёт в `Transit` своё решение `packet` (`packet_ok`).
Остальные сайты проверены: явные хэндлы (`image.cpp`, `blitHelper`, `depthRenderTarget`,
`textureCache`, `renderDraw.cpp:981`) путь не берут; `AcquireRenderTargets` идёт до хэндла draw;
прямой путь дескрипторов `CommitBindings` берёт хэндл после переходов. Второе замечание — теневая
карта `cbstat` ограничена только числом записей — добавлен предел 64 МБ.

Свип `sky62b` (обычный режим, `KYTY_PIPELINE_CACHE=0 KYTY_QUEUE_TRACE=1`), полоса 4700–5100 /
5100–5500, CPU на draw против соседних баз:

| гейты | повтор 1 | повтор 2 | повтор 3 | счётчики |
|---|---|---|---|---|
| `recimg=1 recup=1` | −1,7 / −2,3 | −0,2 / +1,1 | −0,5 / +1,3 | `rec_direct` 800 → 270, `rec_direct_busy` 45 → 37, `rec_pub` 10 700 → 11 200 |
| + `recpubn=16` | −0,4 / −0,3 | −1,7 / −1,7 | −2,6 / −1,4 | `rec_pub` → 907, `rec_throttle` 10 500, `rec_direct_busy` 80 |
| + `recpubn=4` | −1,0 / −0,4 | −0,8 / +0,3 | −0,5 / −0,6 | `rec_pub` → 2 970, `rec_direct_busy` 71 |

FPS в полосе 4700–5100: пара +1,1 / +0,6 / +0,5 %, `recpubn=16` +0,6 / +1,4 / +2,3 %,
`recpubn=4` +1,1 / +0,7 / +0,3 %. Спред баз −2,5…+1,0 %, ядра 7,3–8,4 (без троттлинга).

**Вывод.** Направление верное (девять фаз одного знака, `rec_pub` 10 700 → 907), но эффект ≈1 % —
ниже порога. Остаток `rec_direct` 270 (§3) по-прежнему дренирует поток записи перед каждой прямой
записью (`rec_direct_busy` 37 → 80 при `recpubn=16`), и цена `xchg` частично переезжает туда.
Профиль потока с этими гейтами не снимался — первый пункт следующей сессии, если продолжать.

## 3. Прямые записи по сайтам (`FrameTrace-direct:`)

Sky Garden, `sky62b`, полоса 5100–5900 (410 кадров, 5 600–5 900 draw):

| сайт (база, 765 на кадр) | n | сайт (`recimg`+`recup`, 267 на кадр) | n |
|---|---:|---|---:|
| `Image::Transit` | 342 | `Buffer::CopyFrom` | 46 |
| `EndRenderingImpl` (прямое закрытие прохода из `Transit`/загрузок) | 130 | `CommitBindings` (два сайта: GDS-барьер, прямой путь дескрипторов) | 46 + 20 |
| `RecordBufferCopies` | 63 | `ExecutePreparedDraw` (прямые draw) | 20 |
| `Buffer::CopyFrom` | 44 | `Buffer::Fill` | 19 |
| `CommitBindings` | 23 | `TileManager::Record` | 18 |
| `ExecutePreparedDraw` | 20 | `BeginRenderingImpl` / `EndRenderingImpl` | 16 + 12 |
| … | | `Image::Upload` 16, `IndirectArgsSanitizer::Sanitize` 13, `TextureCache::ClearImage` 26, прочее ≈10 | |

Пустыня с потоком записи: 362 → 94 (`Transit` 204, `RecordBufferCopies` 47, `CopyFrom` 21,
`EndRenderingImpl` 19, `Fill` 14, `ClearImage` 20, `Sanitize` 10 …). С `KYTY_GPU_TIME=1` пакетов
нет вовсе (3 463 прямых записи на кадр) — гейты записи мерить только без него.

## 4. Пункт 3: потолок memo копий констант (гейт `cbstat`)

Диагностика `cbstat` (`KYTY_CB_STAT`): каждая копия гостевого диапазона в stream-кольцо (три сайта:
`ObtainBuffer` — CPU-грязное чтение ≤ 16 КБ, два const-bank сайта `descriptors.cpp`) сравнивается
с тенью предыдущей копии того же `(адрес, размер)` **по гостевой памяти** (первая версия читала
слот кольца — 54 мс на кадр: BAR-память, PCIe на каждую строку). Счётчики: `cb_same`/`cb_diff`/
`cb_new`, `cb_same_ep` (те же байты и та же `RangeWriteEpoch`), `cb_diff_ep` (байты другие, эпоха
та же — свидетель по эпохе ошибся бы), `cb_same_ring` (слот предыдущей копии ещё цел —
`StreamBuffer::Generation()`), `cb_stat_us`; всегда-включённые `ob_stream`/`ob_stream_kb`.

| | пустыня (755 draw) | Sky Garden (`sky62a`, 4 900 draw) |
|---|---|---|
| `ob_stream` / `ob_stream_kb` | 1 520 / 2 416 | 8 400–13 000 / **14 500–18 100** |
| `cb_copy` / `cb_copy_kb` | 842 / — | 7 500 / 720 |
| `cb_same` / `cb_diff` / `cb_new` | 2 001–2 112 / 67–74 / 312–319 (85 %) | 13 200–13 400 / 83–102 / 2 400–2 700 (**84 %**) |
| `cb_same_ep` / `cb_diff_ep` | 1 928–2 051 / **0** | 13 100–13 300 / **0** |
| `cb_same_ring` | 2 096–2 103 | 12 900–13 200 (98 %) |
| `cb_stat_us` | 588 мкс (+9,5 % CPU на draw) | **4,2–4,3 мс** (+3,0 / +3,9 %) |

Что это значит. Свидетель по эпохе региона за 2,2 млн копий в сцене не ошибся ни разу, но
строить на нём memo нельзя: путь берётся именно потому, что страница CPU-грязная, то есть
записываемая без fault'а, и следующая запись гостя эпоху не двигает (сегодняшний ноль — свойство
того, что соседние загрузки перевооружают эти страницы каждый кадр, а не гарантия). Честный
свидетель — содержимое, и его проверка стоит 4,2 мс на 15 МБ: те же загрузки строк, что и memcpy.
Выигрыш memo — только WC-запись в кольцо и `Map`/`Commit`; при 15 МБ на кадр это заметно меньше
1 мс. **Не реализуется.** Если возвращаться — ceiling-гейт по эпохе (небезопасно, только замер),
как `dawitness=0`.

## 5. Вход в Sky Garden

| заход | сборка | режим | итог |
|---|---|---|---|
| `sky62a` | **первый вход после свежей сборки** | `KYTY_PIPELINE_CACHE=0 KYTY_QUEUE_TRACE=1 KYTY_GPU_CHECKPOINTS=1 KYTY_GPU_HANG_ABORT_S=0` (поток записи выключен) | прошёл; свип 5 фаз, 19 656 кадров видео |
| `sky62b` | тот же бинарь | `KYTY_PIPELINE_CACHE=0 KYTY_QUEUE_TRACE=1` | прошёл; свип 19 фаз, 25 336 кадров |

Ни `GpuWaitSlow`, ни `GpuHangAbort`, ни `ErrorDeviceLost`, ни breadcrumb'ов. Правило сессии 61
не подтвердилось; с чекпоинтами зависание пока не поймано. Свип запускался автоматически
(`sky_auto.py`: после `LevelDocument Loaded: underwater_aerial_garden` и 90 кадров подряд
≥ 3 000 draw) — пользователю нужно только довести игру до сцены и отпустить ввод.

## 6. Проверки

- **Пустыня, `KYTY_RECORD_CHECK=1`:** свип `rk` (19 фаз, все гейты) и дымовой `smoke` (все гейты +
  `smemocheck`) — 0 `RecordCheck`, 0 `MISMATCH`, 0 `GpuWaitSlow`/`GpuHangAbort`, 0 `arena full`.
- **Vulkan + sync-валидация на пустыне** (`recimg=1 recup=1 recpubn=16 cbstat=1 progmemocheck
  smemocheck sfcheck pbcheck`, затем `recpubn=4`, затем всё выключено; 6 437 кадров, интро и
  пустыня): **0 ошибок, 0 sync hazards**, единственная строка — известное предупреждение о лимите
  10 повторов.
- **Sky Garden:** оба захода — 0 `GpuWaitSlow`/`GpuHangAbort`/`MISMATCH`.
- **Видео:** `rec_rk` 15 398 кадров, `rec_sky62a` 19 656, `rec_sky62b` 25 336 — **0 однокадровых
  глитчей**.
- **Тесты:** пять бинарей проходят, `memory_tracker_tests` и с `KYTY_ARM_DEFER=1`;
  `resource_tracking_tests` падает как прежде (лог побайтно тот же, что в сессии 61).
- Бинарь установлен, SHA256 **830217BAF8485868B6A03E2CF0BE4D54917B47336AD43E54A515D538D7B484FC**.

## 7. Где мы

| | значение | бюджет 60 FPS |
|---|---:|---:|
| FPS Sky Garden (базы `sky62b`) | 30,2–30,4 | 60 |
| CPU потока GuestGpu | **32,5–32,6 мс** | ≤16,6 мс |
| GPU занят | 14,2–14,7 мс | ≤16,6 мс |
| draw на кадр | ~4 950 | — |
| CPU на draw (полоса 4700–5100) | **6,53–6,63 мкс** | ~3,4 мкс |

Дальше: (1) если продолжать пункт 2 — профиль потока с `recimg recup recpubn=16` (сколько
осталось от 4,6 % `EndRecord` и куда переехало) и остаток 270 прямых записей (§3: `CopyFrom`,
`Fill`, GDS-барьер `CommitBindings`, прямые draw, тайлер, клиры, sanitizer) — это уже общий
механизм «любая прямая запись — запись кольца», а не два сайта; (2) пункт 3 закрыт; (3) M2 с
числами §6 сессии 59; (4) зависание входа не воспроизвелось — правило «первый вход прогревочный»
оставить как предосторожность.

## 8. Харнесс

`C:/kyty/s62/`: `launch_run.py` (пустыня), `launch_play.py` + **`sky_auto.py`** (автостарт свипа
по стабилизации сцены) + `sky_sweep.py`, `summary3.py`, `bands.py`, **`direct_sites.py`** (таблица
`FrameTrace-direct:` → функции по map-файлу), `patchlib.py`. Патчи: `patch_ceil62.py` +
`patch_ceil62b.py` (таблица сайтов, `cbstat`, таймеры, поколение кольца), `patch_recpk.py`
(`recimg`, `recup`), `patch_review.py`. Фазы: `phases_ceil62.json`, `phases_rk.json`,
`phases_val.json`, `phases_smoke.json`, `phases_sky62a.json`, `phases_sky62b.json`. Данные:
`summary3_*.json`, `gates_*.json`, `log_*.txt`, `rec_*.mp4`, `stdout_sky62*.txt`.
