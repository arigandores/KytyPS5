# Трек F, звено F16p2 (`HPP-600`, Red Team): дельта-ревью кода F16o2

**Вердикт: `PASS_WITH_FIXES`** — 1 требуемое изменение (RC1 — правило чтения F16r и член печати F16q, решение лида до печати F16q; кода не
требует), 4 наблюдения без RC. Код `365cc3c2` верен по членам п. 507(б)(1)–(6); `=0` байт в байт по всем ручкам; решение меняется только на двух
DCC-сайтах при `KYTY_FIX_F26=1` (F16o2 решений не добавляет). Бинарь теста `7e4ded19` идёт в F16q **без изменений**; RC1 касается только того,
как читается строка `dcc_stale_apply`.

Решение звена — `7d3c44c8:docs/ROADMAP.md:22869` п. 507 (якорь «507. **Звено F16p трека F (`HPP-596`, Red Team) ПРИНЯТО лидом»; +1 —
«(а) **Приёмка строкой. F16p ✓**»), члены (б)(1)–(6) и (д) «F16p2»; вместе с п. 504(е) (`c6dd8b0f:docs/ROADMAP.md:22859`, якорь «(е) **Константы
кода F16o (решены сейчас, до кода).**»; +1 — «(ж) **Теги F16q (Harness Engineer; константы решены сейчас).**»). Вход — дельта `d5cbcbe2..365cc3c2`
по `src` и `tests` (6 файлов, +294 / −32; кроме `365cc3c2` в диапазоне по `src` — только FS7a `ec6c4c83`, см. Н3), отчёт `9481bacd:docs/track-f/f16o2.md`;
приёмка лида F16o2 — `edb9eb5f` п. 513. Чтение начато 2026-10-05T03:06:09Z (после `edb9eb5f`). Игра не запускалась, сборок и тестов нет; замка
во время звена не было. Метки: [c] — по коду или выводу; [I] — без прямой проверки.

## 1. Требуемые изменения

**RC1. Строка `dcc_stale_apply`, отделённая от своего `adopt` пропущенным draw, читается по правилу п. 507(в) как `kept_applied` с окном не
того момента.**

- Что не так. Метка ставится в `adopt` на этапе привязок draw, снимается — в `MaterializeDeferredDccClear` при `CommitBindings` того же draw. Если
  draw пропущен между ними, метка живёт до следующей материализации изображения, а за это время состояние DCC-записи может смениться без
  какого-либо события F26. Правило (в) окна берёт `present` строки исхода и не сверяет его с событием.
- Сценарий отказа [c по коду, частота в игре — I]. `KYTY_ASYNC_PIPELINES` по умолчанию 1
  (`365cc3c2:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:229`, якорь «return value == nullptr ? 1 : std::atoi(value);»; +1 — «}();»).
  (1) Draw на показе p: `PrepareBindings` (`365cc3c2:src/graphics/host_gpu/renderer/renderDraw.cpp:4129`, якорь
  «PrepareBindings(state.vertex_info[i].stage, bindings.vertex[i]);») → `adopt` привязки текстуры
  (`365cc3c2:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3143`, якорь «(void)texture_cache.AdoptPendingDccForTexture(id,
  descriptor.MetaAddr() << 8u);»; +1 — «}») при `=1` даёт `dcc_stale site=adopt n=<n> present=p fix=kept why=deferred` и метку n
  (`365cc3c2:src/graphics/host_gpu/renderer/cache/textureCache.cpp:2045`, якорь «if (m_fix && e.fix == F::Kept && e.why ==
  DiagF5::CmuWhy::Deferred && m_defer_cache != nullptr) {»); запись становится `Type::Dcc`. (2) Пайплайн компилируется —
  `365cc3c2:src/graphics/host_gpu/renderer/renderDraw.cpp:4468` (якорь «if (pipeline_ptr == nullptr) {»; +1 — «// The pipeline is being compiled
  by a worker thread (KYTY_ASYNC_PIPELINES): skip the draw»): `return` без `CommitBindings` ⇒ материализации (`descriptors.cpp:6775`) нет, метка
  остаётся. (3) На показе p + k гость делает новую DCC-заливку по тому же адресу: `TrackDccFill` для записи `Type::Dcc` перезаписывает
  `clear_mask` и `fill_value` (`365cc3c2:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3562`, якорь «found->second.clear_mask =
  found->second.type == MetaDataInfo::Type::CMask»; +1 — «? (fill_value == 0 ? UINT32_MAX : 0u) : dcc_clear_mask;») — без решения F26, без строки,
  метку не трогает. (4) Следующая привязка на p + k → `MaterializeDeferredDccClear` берёт метку n
  (`365cc3c2:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3515`, якорь «m_armed = cache.TakeF26Deferred(id, &m_mark);»; +1 — «}»)
  и очищает **новую** заливку ⇒ `dcc_stale_apply n=<n> present=p+k result=cleared`. По п. 507(в) событие n читается как `kept_applied`, окно
  p + k − 1 … p + k + 2; член п. 504(з) «строка `skipped draw` в окне» пропуск на p не ловит при k ≥ 2. Итог: заливка события n (сохранённая
  правкой) не исполнялась ни разу — её заменила новая, — а событие идёт в счёт «`kept_applied` без отличий» ⇒ вклад в ложный Ф26 `НЕ ДЕФЕКТ` по
  п. 228(д); при отличии в окне — кадр-свидетель новой заливки, приписанный F26. Без шага (3) исход тоже отделён во времени, но очищает ту же
  заливку — окно по `present` исхода тогда верно.
- Что изменить (кода не требует; решение лида до печати F16q, исполнение — Harness Engineer). Поправка п. 507(в): строка `dcc_stale_apply`, у
  которой `gpu` ≠ `gpu` строки `dcc_stale` того же `n` (вариант рецензента; равносильно — `present` ≠ `present`), читается как `kept`
  («не определено»); печать F16q считает такие строки отдельной строкой таблицы (`apply_late`) и печатает их пары. На обычном пути `adopt` и
  материализация — в одном draw (`PrepareBindings` → `CommitBindings`), `gpu` и `present` у пары равны [c по коду], так что поправка ничего не
  отнимает у событий без пропуска. Альтернатива для лида: проверять `skipped draw` в объединении окон [p_adopt − 1, p_apply + 2].
- Если не внести: на любом теге F16q с пропуском draw между `adopt` и материализацией (а `KYTY_ASYNC_PIPELINES=1` и холодные пайплайны
  `enemy_final` такой пропуск дают — `skipped draw` наблюдались в логах P27, свидетели Б5) строка Ф26 может получить `НЕ ДЕФЕКТ` по событию, чья
  заливка не исполнялась.

## 2. Члены п. 507(б) по коду [c `365cc3c2`]

| Член | Исход | Основание |
|---|---|---|
| (1) `adopt`, `=1`, сохранённая заливка, `clear_mask` ≠ 0 — `kept why=deferred`, `f26_kept` +1, без `f26_kept_applied`; маска 0 — `kept why=mask`; `prepare` без изменений | ✓ | `textureCache.cpp:3793`–`:3797` (`Deferred` / `Applied(false, Mask)`); `Deferred` ставит `m_applied=false` ⇒ `fix=Kept` в `Report` (`:2018`–`:2022`), счёт — ветвь `Kept` (`:2033`); `prepare` `Deferred` не зовёт (`m_defer_cache` = `nullptr`). Строк `site=adopt fix=kept_applied` код не порождает: на `adopt` больше нет `Applied(true, …)` (мутант m31 F16o2) |
| (2) метка под `m_lock`, номер `n`, перезапись, при `=0` нет, снятие при удалении без строки | ✓ | `NoteF26DeferredLocked` (`textureCache.cpp:3822`) из `Report` — деструктор `F26Scope`, объявленного после `scoped_lock` (`:3732`, `:3767`), ⇒ под `m_lock`; `insert_or_assign` — перезапись; условие `m_fix` (`:2045`); `DeleteImage` (`:452`–`:455`) рядом с `m_b42_draw_seq.erase` — та же дисциплина замка; слот переиспользуется только после `DeleteImage` (`m_slot_images.erase` — `:478`, `:481`) |
| (3) снятие в материализации на каждом пути возврата, методом с собственным `m_lock`; `cleared` / `declined`; новый счётчик последним; предел 256 | ✓ | `F26ApplyScope` — первая строка после `auto& cache` (`descriptors.cpp:3562`), до всех трёх `return` функции (`:3566`–`:3569`, `:3586`–`:3587`, `:3651`–`:3655`); `Cleared()` (`:3700`) — после цикла, проходящего каждый бит ненулевой маски, без возвратов между (только `EXIT`); `Layers(mask)` (`:3585`); `TakeF26Deferred` (`textureCache.cpp:3830`) берёт `m_lock` сам; строка печатается при `n` ≤ 256 (`diagF5.cpp:753`), счёт — всегда |
| (4) тождества | ✓ | §3 |
| (5) тест-сайт | ✓ | §4 |
| (6) общие члены п. 504(е)(6), бинарь | ✓ | §5, §6 |

## 3. Тождества п. 507(б)(4) и печать формы п. 496(б)(5) [c]

1. `f26_kept_applied` + `f26_deferred_declined` ≤ `f26_kept`: метка рождается только в `Report` с `fix=Kept` под `m_fix`, где уже прибавлен
   `f26_kept`; снимается один раз (`TakeF26Deferred` удаляет под `m_lock`) и даёт ровно один счёт исхода; перезапись и `DeleteImage` исхода не дают.
   На `prepare` — прежнее (`Kept` + `KeptApplied` в одном `Report`).
2. `=0` ⇒ все `f26_*` = 0: счёт в `Report` под `m_fix`; меток нет ⇒ деструктор `F26ApplyScope` не считает.
3. `=1` с `KYTY_DIAG_F5ID=1`: `f26_kept` = `dcc_stale_bucket_only` — событие `adopt` осталось `Kept` (ветвь счёта та же), `NoteDccStaleProbe` не тронут.
4. Печать, пока предел не исчерпан: строки `fix=kept_applied` (только `prepare`) + `result=cleared` = `f26_kept_applied`; `fix=kept` +
   `fix=kept_applied` = `f26_kept`; `result=declined` = `f26_deferred_declined` — строка исхода печатается при `n` ≤ 256, у каждого `n` не больше
   одной (метка одноразовая), счёт — у того же деструктора. За пределом (`n` > 256) тождество печати не действует — по букве «пока предел не
   исчерпан». Толкование исполнителя §8(2) («в том же пределе» = печать при `n` ≤ 256, отдельного счётчика нет) принято лидом (п. 513) — строк
   исхода не больше 256.

## 4. Тест-сайт п. 507(б)(5)

Материализация в тест-сайте **вызывается** (`RenderExecutorTestAccess::F16dMaterialize`, `tests/ShaderRecompilerComputeTests.cpp:461`, вызов —
`:11199`), проверка по коду вместо теста не нужна. Плечи: D4 (`0x40`) — `kept why=deferred`, затем `cleared`, `f26_kept_applied` +1; D4e (`0x20`, слот
без адреса DCC) — `kept why=deferred`, затем `declined`, `f26_deferred_declined` +1; число меток 1 после `adopt` при `KYTY_FIX_F26` и `KYTY_DIAG_F5`,
иначе 0 (`:11193`), 0 после материализации (`:11207`); строка исхода — тот же `n`, `result`, `layers`, `image`, `dcc`. Вывод прогона в отчёте
(`9481bacd:docs/track-f/f16o2/fin/f16k.txt`) — `ALL OK` в плечах; `--diag-f5-only` при всех ручках — 176 строк байт в байт с `ed4f96d8`
(`9481bacd:docs/track-f/f16o2/fin/site_same_ed4f96d8.txt`, строка «byte for byte equal: True», `ALL OK`). Тестами не пересобирал и не запускал —
вывод исполнителя, сверен по коду теста. Ранние ветви материализации с меткой (изображение не `Dcc`) тестом не покрыты — исход `declined` по коду
(Н4).

## 5. Общие члены п. 504(е)(6) [c]

- **`=0` байт в байт по всем ручкам.** `KYTY_FIX_F26=0`: `Deferred` пишет поля `F26Scope`, но `Report` при `fix=Off` берёт `why` по прежней формуле
  (`textureCache.cpp:2028`: `m_why` читается только при `fix == Kept`; при `Off` — `cpu` или ничего) ⇒ строка `dcc_stale … fix=off` прежняя;
  метки — под `m_fix`; `F26ApplyScope` проверяет одну статическую ручку; `DeleteImage` — чтение атомика 0. `NoteDccStale` с выходом `n` печатает то же.
  `KYTY_FIX_F5CMU`, `KYTY_DIAG_F5ID`: код F16o2 их не читает; путь `Arm` (`m_probe_on`) не тронут. Единственная добавка при `KYTY_DIAG_F5=1` — поле
  `f26_deferred_declined` = 0 в строке `DiagF5:` (вывод измерения, допущено п. 504(е)(6)).
- **Решение меняется только на двух DCC-сайтах при `=1`:** F16o2 решений не меняет — `fix`/`why` события `adopt`, метка, строка исхода, счёт.
  `MaterializeDeferredDccClear` исполняет те же ветви, что и без метки (объект только читает маску и флаг).
- **Порядок замков при снятии метки:** `TakeF26Deferred` берёт `m_lock` сам, вне чужих замков кэша — как `MetaClearMask` / `IsMetaCleared` той же
  функции (`descriptors.cpp:3577`, `:3580`); вызывающие (`:4091` после возврата `FindDccSurfaceImage`, `:6775` цикл `CommitBindings`) `m_lock` не
  держат — иначе уже прежний `MetaClearMask` ушёл бы в повторный вход (`TrackingSpinLock`). Новое: на ранних ветвях замок берётся там, где прежде не
  брался, — только при `count` ≠ 0 (т. е. при `=1`), тем же порядком из тех же вызывающих. Строка исхода — в деструкторе, после выхода из тела, вне
  замков кэша. Под `m_lock` нового — только `insert_or_assign` в `NoteF26DeferredLocked`.
- **Чтение атомика без замка** (`TakeF26Deferred`, `textureCache.cpp:3831`): писатель — `adopt` под `m_lock`; если бы `adopt` и материализация шли на
  разных потоках, устаревший 0 лишь откладывает снятие метки до следующего вызова (UB нет, атомик). Тот же поток — по отчёту [I], как Н4 F16p.
  Отложенное снятие — частный случай RC1.
- **Набор подписи не тронут:** тронуты `diagF5.h`, `diagF5.cpp`, `textureCache.h`, `textureCache.cpp`, `descriptors.cpp`, тест; `CMakeLists.txt` и
  `imageInfo.h` в дельте нет; строка подписи `a54ae4bd03a673fe35ae89bad218132257b11383` в бинаре 1 раз (= F16o).
- **Новые имена последними:** `CmuWhy::Deferred` — последний член перечисления (`diagF5.h:224`), имя `deferred` — `diagF5.cpp:639`;
  `Counter::F26DeferredDeclined` — последний перед `Count` (`diagF5.h:143`), `"f26_deferred_declined"` — последний в `F5Names` (`diagF5.cpp:223`,
  `static_assert` размера прежний). Гейтов и `Knob` нет.
- **Кадр стека:** `F26ApplyScope` — 3 × `uint64_t` + 2 `bool` + `uint32_t` (≈ 40 байт) на потоке GPU — без риска.

## 6. Бинарь

`C:/kyty/f287/bin/kyty_emulator_7e4ded19.exe` — sha256 `7e4ded19f577cc9b03b2443111f40ac701a29d6234ffa3d3c9c64f4475a58fcb` (пересчитан этим звеном,
= отчёту); строка версии `KytyPS5-2026-09-15-6a2987a-2264-g365cc3c2` 1 раз (вторая `…-gc0789a34` — `SDL_REVISION`, как у F16o); строки
`dcc_stale_apply`, `f26_deferred_declined` в бинаре есть. Бинарь собран из названного коммита `365cc3c2` [c строкой версии; чистота worktree —
по отчёту]. Не установлен — установленный `ps5 em/kyty_emulator.exe` этим звеном не открывался и не менялся.

## 7. Наблюдения без RC

- **Н1** (`skipceil` = 3). При `Common::SkipCeil::t_mode == 3` заливка применяется внутри `adopt`
  (`365cc3c2:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3805`, якорь «if (Common::SkipCeil::t_mode == 3 && found->second.clear_mask != 0)
  [[unlikely]] {»), а строка говорит `why=deferred`. Ручка исследовательская, в тегах F16q не задаётся — «не исправлено, читать так».
- **Н2** (цена при `=1`). Метка, не снятая до конца процесса (изображение не материализуется и не удаляется), держит `m_f26_deferred_count` > 0 ⇒
  каждая материализация плеча `=1` берёт `m_lock`. Решений не меняет; время плеч `=0`/`=1` F16q не сравнивать [I, не измерено].
- **Н3** (состав бинаря). `365cc3c2` лежит на `main` после FS7a `ec6c4c83` (`git merge-base --is-ancestor` — да): бинарь `7e4ded19` несёт умолчания
  `KYTY_FIX_F8=1`, `KYTY_FIX_B24=1`, которых нет у установленного FS6 `9325446c` и у бинаря F16m `ed4f96d8`. Обе стороны каждой пары F16q на одном
  бинаре — сравнение пар не задето; печать F16q, сопоставляющая `f5cmu_0b`/`f5cmu_1b` с парой F16m, обязана назвать это отличие.
- **Н4** (покрытие). Ранние ветви материализации с меткой (`!registered`, не `Dcc` и т. п.) тестом не проверены — исход `declined` по коду (§2,
  член (3)).

## 8. Не заявляется

Что событие RC1 F16p или сценарий RC1 этого отзыва встречаются в игре; что правка `KYTY_FIX_F26` меняет картинку или корректна для железа; что
бинарь `7e4ded19` работает в игре; что K = 8 достаточно; что Ф26 — дефект или не дефект; что SPIR-V корректен для устройства и картинка верна. Ни
одно число — не выигрыш; 60 FPS не обещаются.
