# F47h2 — ревью правок F47g2 кода `KYTY_DIAG_F47DT` и ридера (Red Team, `HPP-829`)

**Вердикт: PASS_WITH_FIXES** — RC 2 (RC1 — ридер / код, RC2 — ридер; звеном F47g3 пунктом лида или строкой чтения — выбор лида,
§4). Правки RC1–RC5 отзыва F47h и ответы п. 742(г) исполнены по коду; мутанты m1–m8 пойманы все (m1, m2, m2p, m5, m6, m7 — стендом
своей сборки, m8 — фикстурой ридера G9, m3, m4 — членами кода); члены п. 743(г)(1)–(2) — [c кода], без RC; член п. 743(г)(3) —
`ADMISSION` = букве п. 742(е), кроме одного края (RC2). Бинарь `86e42e36` по коду годен; в F47i он идёт или нет — по решению лида о
RC1 (код меняется только в варианте (б)).

Основание — `ROADMAP.md` «СЕССИЯ 122» п. 742(д), 743 (KytyPS5 `6533d359`); отчёт F47g2 `a88527d7` (`docs/track-f/f47g2.md`); код —
свой worktree `C:/kyty/f287/f47h/wt`, переведённый на `8bdc069a` (родитель `1f9b5b77`, `git status` 0 строк; `8bdc069a` = `main`
`bfe0be75` по строкам `+`/`-`, п. 743(а)). Номера строк ниже — по `8bdc069a`. Игру не запускал, замка и `STOP` не было, установленный
FS15 `bfac84be`, `C:/kyty/build*` и кэши не трогал.

## §1. Члены п. 742(в), (г) и п. 740(в)(2)

| член | итог | где |
|---|---|---|
| `=0` по коду прежний | ✓ — 8 новых точек под `if (DiagF47Dt::On())` (graphicsRun ×4, videoOut ×1, descriptors ×1, textureCache ×2 внутри прежних блоков); `NoteFlip`/`NoteShown`/`NoteRingGpuCopy` сами начинаются `if (!On()) return;`; `IdOfImageForDiag` — только из точки под `On()`; стенд `=0` — 0 строк `F47dt`, каталога нет (свой прогон) | дифф `1f9b5b77..8bdc069a` |
| `=1` только пишет | ✓ — новое: счётчик `g_flips` (атомарный), ноты кольца, записи по ключу образа; запросы `BufferCache::IsRegionGpuModified` (замок `RegionManager` внутри лямбды `Iterate<false>`, без создания, без счётчиков) и `HasGpuDirtyBytes` (чтение `m_gpu_modified_ranges` на потоке, который его пишет); `IdOfImageForDiag` — `const ForEach` без `TouchImage`; строка `shown` — одна строка лога под `FlipQueue::m_mutex` (тот же контекст, что строка `FrameTrace`, videoOut.cpp:1230 → 1406, без `Unlock` между) | diagF47Dt.cpp:786–820, 1032–1035; memoryTracker.cpp:93–99; bufferCache.cpp:2394, 2517 |
| подпись = базе | ✓ — файлов набора подписи в диффе 0; своя сборка: `KYTY_SHADER_SOURCE_HASH` `9177b4267de1fb8bac7d1113afd8733210addfac` — 1 вхождение | §3 |
| RC1 — `q` | ✓ — `q` = `g_flips` + 1 на потоке разбора (diagF47Dt.cpp:133), `NoteFlip` во всех четырёх местах постановки флипа после получения id запроса (graphicsRun.cpp:4076, 4108, 4147, 4175); id запроса — тот же, что `r.id` очереди флипов (`Sync::PrepareVideoOutFlip` → `SubmitFlipFromGpu`, sync.cpp:228–246; флип CPU — `submission.flip_request_id`, graphicsRun.cpp:232, 1107); `NoteShown(flip_status.count, r.id)` — сразу после `count++` (videoOut.cpp:1237–1244), то же значение печатает строка `FrameTrace: n=` этого вызова (videoOut.cpp:1406); загрузка поверхности показа в `FlipQueue::Prepare` → `Presenter::PrepareFrame` → `UpdateImage` идёт до `NoteFlip` и получает `q` своего флипа | |
| RC2 — запись по образу | ✓ — ключ `ImageKey(index, generation)` (diagF47Dt.cpp:352), `CompletePendingUpload` — настоящий id (`IdOfImageForDiag`, ненайденный образ → `SlotId{}` = индекс `UINT32_MAX`, запись под чужим ключом, у настоящего образа остаётся `pending` ⇒ `und` — безопасная сторона); `sid`, `rlast`, `sk=other_image` (diagF47Dt.cpp:555–565) | |
| RC3 — кольцо Stream | ✓ — глобальный сторож снят; нота в ветви `gpu` const-bank (descriptors.cpp:1018) — единственная копия ГП в кольцо Stream в прочитанном коде (вторая `CopyFrom(command` — bufferCache.cpp:2373 — пишет в буфер `ObtainBuffer(dst, written)`, не в кольцо); `ggpu` (diagF47Dt.cpp:1032) и ридер `und` (dt_f47g2.py:377–383, 397–404) | |
| RC4 | ✓ — плечи S, A2; m2 и m2p падают на своём стенде (§2) | |
| RC5 | ✓ — коды 13, 14, 19, 20 и 15–18 = `und` (dt_f47g2.py:254–255, 477–483; таблица факторов GFX10 сверена); члены (6)(3) печатаются при любом исходе (dt_f47g2.py:730–735) | |
| (г)(1) П1 суженный | ✓ — `p1_narrowed` (dt_f47g2.py:612–635): постоянное по всем чёрным записям того же `d` (все показы блока вместе — строже буквы «чёрной серии», сторона `ТУПИК`, не ложного `НЕ ДЕФЕКТ`); исход — по суженному, полный — справкой | |
| (г)(2) `INVALID` | ✓ — строка стопа (dt_f47g2.py:736–739) | |
| (г)(3) Ф3 | **✗ частично — RC1**: для образа ✓ (dt_f47g2.py:316–320); для буфера и SRT признака нет, `ne` ⇒ `DEFECT` | §4 |
| (i), (ii), вид, регистры (F47h) | без изменений правкой: путь вида (`vmap`) и тени регистров (`AppendRegs`) дифф не трогает (только префикс `q=`) | |

## §2. Мутанты m1–m8 (своя сборка стенда из своего worktree, `run_stand_f47g2.py` F47g2 без изменений)

Мутации — `mut_f47h2.py` (якорь — целая строка, одно вхождение, LF; m1, m2, m5 — перенос мутантов F47h на ключ образа; m2p, m6, m7 —
свои формулировки, написаны независимо от `mut_f47g2.py`), сборка цели `f47dt_stand` (`bstep.sh`, сторож), возврат файла `git checkout`,
`git status` 0 строк после каждого. База `stand_base` `2b53f8fc…` — `ALL OK`, 32 `OK`, 0 `FAIL` (`run_base.out`).

| мутант | что | чем пойман | данные |
|---|---|---|---|
| m1 — хэш (i) из кэша | `ih` = хэш записи образа, если она `hashed` | **стендом** — P (`ih` = `sh`), I, T, S, A2, `F47dtStat` (файлов 15 ≠ 14) | `m1` `3bb79f54…`, `run_m1.out` |
| m2 — (ii) перечитывает память гостя | inline-нота хэширует память гостя, не `staging` | **стендом** — плечо S (`sh` ≠ хэш staging) | `m2` `58dbdda0…`, `run_m2.out` |
| m2p (вариант m2 для пула) | разрешение пула хэширует память гостя | **стендом** — A2 | `m2p` `f47a1369…`, `run_m2p.out` |
| m3 — `dst_sel` из T#, не из вида | — | **членом кода** (путь вида дифф не трогает; F47h §1) | — |
| m4 — регистры из следующего draw | — | **членом кода** (синхронный разбор, тень по `&m_ctx`; дифф не трогает; F47h §1) | — |
| m5 — `=0` пишет строку | строка `F47dt: mode=` до проверки | **стендом** (`=0`: 1 строка) для модуля; 8 новых точек — **членом кода** (§1) | `m5` `a14dfad8…`, `run_m5.out` |
| m6 — `q` с потока показа | `QueuedShow()` → `PresentNow()` | **стендом** — плечо Q (`q0=710 q1=711`, после флипа 711) | `m6` `3f307996…`, `run_m6.out` |
| m7 — запись (ii) по диапазону | поиск записи образа последней загрузки диапазона | **стендом** — плечо T (образ 20 `eq`, образ 22 `sk=staging`) | `m7` `013b1d50…`, `run_m7.out` |
| m8 — `ne` при `cpu=1` как `дефект` | ридер: ветвь Ф3 выключена | **ридером** — фикстуры G9, G9b (`DEFECT (6)(1)`) | `selftest_m8.out` |

Ридер `dt_f47g2.py` (`61a13e29…` = файлу в git `a88527d7`) `selftest` своим прогоном — `ALL OK` (`selftest_f47h2.out`).

## §3. Своя сборка из чистого worktree

Свой worktree F47h (`C:/kyty/f287/f47h/wt`) переведён `checkout --detach 8bdc069a`, `git status` 0 строк; каталог сборки F47h
(configure F47h от `1f9b5b77`), сборка `version` → `kyty_emulator` → `f47dt_stand` под сторожем. sha256 своей
`7e6614c4f21ce9990e4ca533c18b1159f6030add34115f6b1ccce78a83b6f0f4` ≠ `86e42e36…` при равной длине (25 050 624). Причина названа
(`cmp_bin_f47h2.py`, `cmp_bin.out`): после замены имени worktree `f47h` → `f47g` (139 строк путей) остаётся 1 901 байт — 1 882 байта
`.data` в хэшах `?A0x…` (путь исходника), PE и каталог отладки, строка `SDL_REVISION` (`…-1929-g6beb3b73` в `86e42e36` — configure F47g;
`…-1931-g1f9b5b77` в своей — configure F47h); **`.text` — 0 отличий**; строка версии эмулятора у обоих `…-1932-g8bdc069a`. Свой стенд
`2b53f8fc…` ≠ `942c4791…` — та же причина, `ALL OK`. После мутантов обе цели пересобраны из `8bdc069a`: `.text` = своей базе (0
отличий, `restore_cmp.out`).

## §4. RC

**RC1 (ложный `дефект` против буквы п. 742(г)(3)). Ф3 исполнен только для образа.** Буква: «`дефект` по (6)(1) для ресурса — только
`ne` при `cpu=0` и `maybe=0`», «у образа или буфера». Строка `buf` признака записи гостя не несёт (diagF47Dt.cpp:1038–1040 — поля
`gh`, `ggpu`, `gvh`; `cpu`/`maybe` есть только у `img`, :983), `cmp_buffer` при `gvh` ≠ `gh` даёт `ne` (dt_f47g2.py:384–385), `cmp_srt`
— `ne` при `gvh` ≠ `snaph` или `same_*` = 0 (:394–402), `read_rule` — `DEFECT (6)(1)` при любом `ne` (:740–745). Фикстура
`fx_f47h2.py` (`fx_f47h2.out`, B1, B2a, B2b) — `ne` во всех трёх. **Сценарий отказа:** копия const-bank в кольцо (подготовка привязок,
`TryReadBacking`) и чтение (i) в `OnDraw` разделены всей подготовкой draw; эмулятор обрабатывает кадр позже, чем гость его поставил
(посылка Ф3), и гость пишет в тот же диапазон констант (или в таблицу SRT / user data) следующий кадр в этом окне ⇒ `gvh` = байты до
записи, `gh` = после ⇒ `ne` при `ggpu=0` ⇒ `DEFECT (6)(1)` и итерация кода по «устаревшему буферу», которого нет; у образа ровно этот
случай уводит в `und` член `cpu=1`. Частота — [I] (зависит от того, пишет ли игра константы UI на месте или кольцом). **Изменить —
одно из двух (решение лида до данных F47i):** (а) без кода — строка чтения F47j и ридера: `ne` буфера и SRT при отсутствии признака
`cpu`/`maybe` — `und` по букве (г)(3) (признака «0» нет); цена — буфер и SRT не дают `дефект` никогда, только «не определено»; (б) код
(звено F47g3): хэш байт гостя в момент копии в кольцо (CPU-ветви const-bank и `ObtainBuffer`; для SRT — в момент материализации)
отдельным полем; `ne` при «хэш гостя в копии = `gvh`» и «≠ `gh`» — гость писал после копии ⇒ `und`; «хэш гостя в копии ≠ `gvh`» —
кандидат дефекта копии ⇒ `ne`; фикстуры и плечо стенда «гость меняет байт между копией и draw». Без RC1 правило (6)(1) на буфере и SRT
читается не по букве пункта.

**RC2 (`ADMISSION OK` без проверки третьего члена). Член `FrameTrace` пропускается, если строк `FrameTrace: n=` в логе 0.** dt_f47g2.py:169
— `if res['frametrace'] and no_ft:`; фикстура A1 (`fx_f47h2.out`): флипы 700–710 со строками `shown`, строк `FrameTrace` 0 ⇒ `ADMISSION
OK` (заголовок печатает `FrameTrace lines 0`); A2 — контроль: при строках `FrameTrace` пропуск одного `n` ⇒ `FAIL` (член жив). Буква
п. 742(е): «совпадают с номерами `FrameTrace: n=` тех же флипов, иначе помеха прогона». **Сценарий отказа:** тег F47i без
`KYTY_FRAME_TRACE=lite` (ошибка формы) или с формой строки `FrameTrace`, которую разборщик не узнаёт (`re.match(r'FrameTrace: n=(\d+)'`) —
допуск печатает `OK`, смещение видео ↔ флип (F47e §6) берётся без опоры на `FrameTrace`, член п. 742(е) не исполнен, а печать его
засчитывает. **Изменить:** 0 строк `FrameTrace` при ≥ 1 флипе в окне ⇒ `ADMISSION FAIL` с причиной; фикстура. Либо (без кода) строка
текста F47i: допуск — `ADMISSION OK` **и** `FrameTrace lines` > 0 в той же строке.

## §5. Члены п. 743(г)

**(1) Порядок замков — [c кода], взаимной блокировки нет; инверсия в графе есть, но вся на одном потоке.** Кто берёт `g_mutex`:
`OnDraw` (diagF47Dt.cpp:895), `NoteImageUpload` (:829), `NoteRingGpuCopy` (:805), `PrintExitStat` (:1173), функции стенда. Под `g_mutex`
`OnDraw` берёт: `RegionManager::lock` (новое, `IsRegionGpuModified` → memoryTracker.cpp:93–99, замок внутри лямбды — лист),
`TextureCache::m_lock` (прежнее F47g: `IsGpuClean` → `src/kernel/memory.cpp`:1032–1041 → textureCache.cpp:3091, только на потоке GuestGpu),
`g_shadow_mutex` (`AppendRegs`; `NoteCtxWrite`/`NoteCtxOp` держат только его), замок лога. Обратные рёбра: `TextureCache::m_lock` →
`g_mutex` — `FindTexture` (m_lock :2288) → `CompletePendingUpload` (:2335) → `NoteImageUpload`; `UpdateImage` (:2195) → `RefreshImage`;
`MarkGpuWritten` (:2518) → `CommitGpuWrite` → :2531. Это пара обратных порядков (`g_mutex` ↔ `m_lock`), но все её места — поток
GuestGpu: `FindTexture` — descriptors.cpp:5033–5103, 6346; `MarkGpuWritten` — depthRenderTarget.cpp:456, renderDraw.cpp:5429,
descriptors.cpp:3629; `UpdateImage` — swapchain.cpp:839 (`PrepareFrame`) ← `FlipQueue::Prepare` (videoOut.cpp:1050) ←
`SubmitFlipFromGpu` / `PrepareFlip` (videoOut.cpp:3896, 3906) ← разбор GuestGpu; `OnDraw` — renderDraw.cpp:4457 из `ExecutePreparedDraw`
← `DrawIndex` / `DrawAuto` под мьютексом рендера (renderDraw.cpp:4995, 5224), `PrepareFrame` берёт тот же мьютекс (swapchain.cpp:827).
`NoteRingGpuCopy` вызывается после возврата `IsRegionGpuModifiedFromGpu` (замок отпущен), в descriptors.cpp:600–1100 и в
`RebindBuffers` замков нет. `RegionManager::lock` в обратную сторону к `g_mutex` не ведёт (под ним только `IsModified`). Итог: цикла
между потоками нет [c кода]; это свойство «все держатели `g_mutex` — поток GuestGpu», и любой будущий держатель `g_mutex` на другом
потоке под `m_lock` даст взаимную блокировку — **Н1** (не RC: в коде такого нет).

**(2) `NoteShown` — [c кода], взаимной блокировки нет.** `NoteShown` (diagF47Dt.cpp:794–799) под `FlipQueue::m_mutex` берёт только
замок лога; `NoteFlip` (:786–792) — атомарный `fetch_add` и замок лога, ни одного замка очереди флипов: к месту `NoteFlip`
`PrepareVideoOutFlip` уже вернулся (замки `FlipQueue::Prepare` — scoped, videoOut.cpp:977, 1036, 1053). `g_mutex` поток показа не берёт.
Замок лога — общий лист; строка под `m_mutex` в этом месте уже есть (`FrameTrace`, videoOut.cpp:1406), новая строка нового ребра не
добавляет. Ожидание писателя лога при переполнении (`LogAsync: stall`) — время кадра, не блокировка [I на теге].

**(3) `ADMISSION` = букве п. 742(е)** — да по членам «`q` в окне подряд» (`qs == range(a, b+1)`, строже: пропуск в начале или конце окна —
`FAIL`) и «тот же флип» (через `rid`: `shown n` = `q`, ровно одна строка; `shown n` и `FrameTrace n` — одно значение
`flip_status.count` одного вызова `FlipQueue::Flip`, videoOut.cpp:1237, 1244, 1406). Нет — при 0 строк `FrameTrace` (RC2).
Строки `FrameTrace` пишутся на каждый флип при `KYTY_FRAME_TRACE` (включая `lite`), кроме первого (`prev.host_ns` = 0) — вне окна.

## §6. Строки чтения (не RC)

- **Н1** — §5(1).
- **Н2.** `ggpu` считается в `OnDraw` по `src.address/size`, решение `gpu` const-bank — по выровненному диапазону копии
  (descriptors.cpp:977–978); если ГП писал только в байты выравнивания перед `src.address` и кольцо за ту же подготовку draw перешло в
  новое поколение (нота стёрта `RingSyncLocked`), `gvh` — хэш прежних байт кольца при `ggpu=0` ⇒ `ne`. Два условия сразу — [I]
  частоты; в F47j `ne` буфера при `given=ring_copy` читать вместе с RC1.
- **Н3.** Удержанный флип (`AsyncPipelines: flip ... held`, videoOut.cpp:1199–1217) получает `count++` и строку `shown`, хотя на
  экран идёт прежний кадр; сопоставление `q` ↔ кадр видео (F47e §6) должно это учитывать — член формы F47i, не кода.

## §7. Не заявляется

П. 742(и), 743(е), 740(ж), 741(д) и отчёт F47g2 §8 целиком; что код верен в игре (не запускался); что `q` совпадёт с `n` `FrameTrace`
в игре; что RC1 в игре наступит (частота — [I]); что других копий ГП в кольцо Stream нет вне прочитанных мест (16 мест
`GetUtilityBuffer(MemoryUsage::Stream)` не открывались построчно); что `ggpu` = решению `gpu` на всех диапазонах (Н2); ни одно число —
не выигрыш; 60 FPS не обещаются; цель (B) не меняется.

## §8. Процесс и файлы

Время — UTC `date -u`, строки `C:/kyty/f287/times.txt` (`F47h2 …`): начало 2026-10-12T03:12:14Z (после `6533d359`, п. 743); проверки
API перед шагами длиннее 60 с — `api_chk.sh` (Harness Engineer `in_progress` — 0), шаги сборки под сторожем `watch_f47h2.py`; замка и
`STOP` не было. В git `docs/track-f/f47h2/`: `bstep.sh`, `api_chk.sh`, `watch_f47h2.py`, `build_f47h2.cmd`, `mut_f47h2.py`,
`run_mut_f47h2.sh`, `fx_f47h2.py`, `cmp_bin_f47h2.py`, `textcmp.py`, `add_facts_f47h2.py`, `facts_f47h2.md`; выводы `run_base.out`,
`run_m1.out`, `run_m2.out`, `run_m2p.out`, `run_m5.out`, `run_m6.out`, `run_m7.out`, `selftest_f47h2.out`, `selftest_m8.out`,
`fx_f47h2.out`, `cmp_bin.out`, `restore_cmp.out`. Локально `C:/kyty/f287/f47h2/` — то же, `stand_bin/`, каталоги прогонов стенда,
`kyty_emulator_own.exe`; worktree и сборка — `C:/kyty/f287/f47h/` (HEAD `8bdc069a`).
