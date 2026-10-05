# S17a2 — правки S-replay по RC1, RC3, RC4(а) S17b и тест tess N2 (Emu Engineer, `HPP-618`; `ROADMAP.md` «СЕССИЯ 122» п. 532(б), (г), (д)(а), (з))

Без игры. Код — коммиты `29542308` (родитель `49736a20`) и `a2fee0d9` (вторая правка RC3, §3); от S17a `283a6ef9` в
`src`/`tests` меняются только 5 файлов ниже; ветка `main`. **Код S17a2 = `a2fee0d9`** (бинарь S17c — §7). Время — `C:/kyty/s288/s17a2/times.txt` (`date -u`). Пометки: [c] — проверено кодом или прогоном этого звена;
[I] — вывод; [U] — неизвестно. **Код в игре не проверен (WIP по правилу звена до тегов S17c).**

## 1. Что изменено (`git diff --stat 283a6ef9 a2fee0d9 -- src tests CMakeLists.txt`)

Номера строк ниже — по `a2fee0d9`.

| Файл | Строк | Что |
|---|---|---|
| `src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp` | +27 −1 | RC1: `PipelineCache::ReplayCloseStop` (`:6617`–`:6628`); RC3: заголовок манифеста — одна строка по построению (`:7587`–`:7593`) |
| `src/graphics/host_gpu/renderer/pipeline/pipelineCache.h` | +3 | объявление `ReplayCloseStop` (public, `:217`) |
| `src/graphics/presentation/window/window.cpp` | +3 | вызов `cache.ReplayCloseStop()` в ветви закрытия `WindowPrepareShaders` (`:1029`) |
| `src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp` | +23 −9 | комментарий `StandRequestClose` (`:96`–`:98`); RC4(а) (`:669`–`:695`) |
| `tests/shaderCfgTests.cpp` | +33 | N2: круг tess в `TestShaderReplayFormat` |

Плюс документ: строка К1(4) и текст стенда `stop` в `docs/track-s/s17a/README.md` (поправка S17a2), скрипты правки
`docs/track-s/s17a2/patch/patch_s17a2.py` и `patch_s17a2_rc3.py` (якоря целыми строками, LF).

## 2. RC1 — остановка перестройки на пути закрытия экрана подготовки (п. 532(б))

- **Место.** `WindowPrepareShaders() == false` возникает только в ветви `SDL_QUIT` / `SDL_WINDOWEVENT_CLOSE` цикла подготовки
  (`a2fee0d9:src/graphics/presentation/window/window.cpp:1026`, якорь `SetShaderPreparationOverlay(false);`, +1 — комментарий
  S17a2); единственный вызывающий — `Execute` (`a2fee0d9:src/emulator.cpp:188`, якорь
  `if (!Libs::Graphics::WindowPrepareShaders()) {`, +1 `std::quick_exit(0);`). Вызов поставлен перед `return false` — то есть до
  `std::quick_exit(0)` вызывающего; `emulator.cpp` не менялся, путь обычного выхода (`emulator.cpp:199`) не тронут.
- **Код** `PipelineCache::ReplayCloseStop` (`a2fee0d9:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:6617`, якорь
  `void PipelineCache::ReplayCloseStop() {`, +1 `if (!ShaderReplay::RebuildOn()) {`): при `KYTY_S_REPLAY` ∉ {1, 3} — возврат
  сразу (`:6619`), ничего не пишется и не печатается — путь закрытия при `0` и `2` прежний (лишнее — один вызов и чтение
  статической `Mode()`, уже прочитанной в `ReplayInit`). При {1, 3}: строка `ShaderReplay: close stop requested
  precache_active=<0|1>`, `m_precache_stop.store(true)` (`:6623`), `join` потока precache, если он есть (`:6624`–`:6626`),
  строка `ShaderReplay: close stop joined wait_ms=<мс>` (`:6627`). Ожидание — до проверки флага циклом перестройки перед
  следующим R-PIPE (`:7410`) или циклом `PrecachePipelines` перед следующим рецептом (`:6815`), то есть не дольше одного R-PIPE
  (рецепта) [c кода]; длительность в игре [U] — справка S17c (`wait_ms` и время от `stand stop applied` до выхода).
- **Флаг (правило звена: установка и снятие).** `m_precache_stop` ставится в `:6623` (новое место) и, как раньше, в
  `~PipelineCache` (`:4858`); не снимается нигде: после `ReplayCloseStop` управление возвращается в `WindowPrepareShaders` →
  `return false` → `std::quick_exit(0)` — флаг процесс не переживает. Выходов из `ReplayCloseStop` после `store` без `join`
  нет. Повторный вызов исключён: ветвь закрытия выходит из функции.
- **Что пишется на диск при остановке [c кода].** Поток перестройки выходит из цикла (`:7410`–`:7411`), затем
  `const bool stopped = m_precache_stop.load();` (`:7523`) и `save_dirty()` (`:7524`): **файлы кэша трансляции перестроенных
  источников — ДА** (каждый источник с новыми перестановками — `ShaderTranslationCache::Save`, свой временный файл и
  `RenameFile`, `shaderTranslationCache.cpp:764`–`:814`; те же файлы сохранялись и по ходу цикла каждые 128 R-PIPE, `:7418`).
  `pipelines.bin` — **НЕТ** (`recipes_state = "stopped"`, `:7559`); манифест `rebuild_manifest.tsv` — **НЕТ** (`if (!stopped
  && count != 0)`, `:7586`); `PrecachePipelines` после остановленной перестройки не запускается (`:6755`); поколение каталога
  `replay.<g>.bin` при закрытии на экране подготовки не пишется (писатель пишет его в `Save()`/`ReplayStop`, которых
  `quick_exit` не исполняет; гость не стартовал); кэш пайплайнов драйвера не пишется (`FinishPreparation` не вызывается).
  Сбор `m_replay_rebuilt` (`:7553`) — только память. Значит, К6 «следующий старт перестраивает остаток»: следующий старт идёт
  в перестройку снова (нет `pipelines.bin` текущей подписи) и находит сохранённые файлы источников — `LoadEntry` (`from_file`),
  перестановки, совпавшие по специализации и старту, — `perms_cached` [c кода; в игре — S17c].
- **Признак обрыва для печати S17c:** строка `ShaderReplay: stand stop applied processed=… records=…` (`:7415`), затем
  `ShaderReplay: close stop requested …`, строка `ShaderReplay: rebuild records=… pipelines_bin=stopped` (`:7615`) и строка
  `ShaderReplay: close stop joined wait_ms=…`. Порядок двух последних [c кода]: `rebuild …` печатает поток перестройки до
  своего конца, `joined` — главный поток после `join`.
- **Стенд `stop` (без изменений кода стенда):** `StandRequestClose` кладёт `SDL_QUIT` (`shaderReplay.cpp:95`); комментарий
  `:96`–`:98` исправлен по факту; строка К1(4) и текст стенда в README S17a исправлены (поправка S17a2).

## 3. RC3 — заголовок манифеста (п. 532(г)); посылка RC3 неверна

**Находка [c кода]:** `ShaderTranslationCache::Signature()` уже кончается переводом строки
(`a2fee0d9:src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp:603`, якорь `              variant + "\n";`, −8 —
`m_signature = std::string("KytySC") + std::to_string(FORMAT_VERSION) + ":" +`; потому и проба S16d срезает `10`/`13`,
`tests/S16dProbe.inc:630`, а `InstallShaderSeed` заменяет `\n` на `:`). Значит, в S17a заголовок
`fmt::format("# ShaderReplay rebuild manifest; signature {}", cache.Signature())` был ровно одной законченной строкой, первая
строка данных не терялась; RC3 S17b (и пункт п. 532(г) «перевод строки после заголовка») опирается на неверную посылку.
Первая правка `29542308` (`\n` в формате) дала бы пустую строку между заголовком и данными. **Вторая правка `a2fee0d9`:**
`a2fee0d9:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:7589`, якорь `std::string signature = cache.Signature();`, +1
`while (!signature.empty() && (signature.back() == '\n' || signature.back() == '\r')) {`; `:7593` —
`std::string manifest = fmt::format("# ShaderReplay rebuild manifest; signature {}\n", signature);`. Заголовок — одна строка при
любой форме подписи (с переводом или без); для текущей подписи байты файла = форме S17a [c по построению: срезается ровно
один `\n`, добавляется один]. Скореру S17c: фикстуры на обе формы по п. 532(г) остаются в силе (для текущей подписи формы S17a и
S17a2 совпадают; пустые строки — пропускать). **Вопрос лиду:** RC3 читать как «ложное срабатывание S17b, правка — устойчивость
формы», не как исправленный дефект (вариант исполнителя).

## 4. RC4(а) — стенд `canon` тратится только на отвергнутой записи (п. 532(д)(а))

`a2fee0d9:src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp:674`, якорь `size_t stand_word = canonical.size();`, +1
`if (canon_stand && !g_canon_stand_done.load()) {`. Порядок: стенд портит первое слово роли `T_LO` со значением 1 (не нулевой T#
→ нулевой) и запоминает индекс; самопроверка `Run` (`:685`); если стенд применён — строка
`ShaderReplay: stand canon applied hash=0x… rejected=<1|0>` (`:688`); `rejected=1` — `g_canon_stand_done.store(true)` (`:690`),
запись идёт в отказ `self` как раньше (`canon_self`, `canon_mismatch`); `rejected=0` — слово возвращается к 1 (`:692`),
самопроверка повторяется на неиспорченной записи (`:693`), запись идёт обычным путём, флаг не ставится — стенд портит следующую
подходящую запись. **Флаг:** `g_canon_stand_done` (`:580`) ставится только в `:690`, не снимается (одноразовый стенд на процесс;
`KYTY_S_REPLAY_TEST=canon` только). `stand_word` — локальная переменная вызова. Поток: `Canonicalize` зовётся только потоком
писателя (`HandleSpec`, `shaderReplay.cpp:1158` — гонки за флаг нет). Чтение К3 по п. 532(д)(а): «стенд ⇒ `canon_mismatch` > 0»
— по строке с `rejected=1`; строк `rejected=0` может быть много (по одной на запись с ненулевым T#, от которого специализация не
зависит) — справка.

## 5. N2 — круг tess `VertexFromKey` (п. 532(з))

Вход tess в тестах есть (`tests/ShaderRecompilerComputeTests.cpp:30455`: control points 3/3, шаги 124/128, domain 1,
partitioning 2, topology 2). В `TestShaderReplayFormat` добавлено: вход с этим tess и одним ресурсом → ключ (размер 7 + 1 + 7 + 13 =
28 слов) → `VertexFromKey` → ключ → `VertexFromKey` → ключ: оба ключа равны исходному, все 7 полей tess восстановлены; ключ,
обрезанный внутри tess-части (`first(9)`), отвергается с `why == "tess"`. Набор (a2fee0d9): 132 теста, 0 строк `ShaderCfgTests: failed:`.

## 6. Офлайн-проверки [c] (на `a2fee0d9`)

- **К1(7):** `git diff --stat 2990fe06 a2fee0d9 -- src/graphics/shader CMakeLists.txt` и файлы `SHADER_CACHE_EXTRA_FILES`
  (`shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`, `imageInfo.h`) — **пусто** (`C:/kyty/s288/s17a2/k1_7_diffstat_a2fee0d9.txt`,
  0 строк). Строка подписи бинаря тестов S17a2 (`KYTY_S16D_JOBS` с пустым списком) =
  `S signature=KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz:cbank:fixb26:fixb1b:fixf10:fixf19 enabled=1` —
  **равна родителю** (весь вывод пробы байт в байт = `C:/kyty/s288/s17a/sig/out_P.txt`); `sig/out_S3.txt`.
- **К2(1):** `corpus_s17a.py` (скрипт S17a без изменений) — родитель `2990fe06` (тесты sha256 `32c50dc4…`) против S17a2 (тесты
  `df33f104…`): 269 строк A (CS 111, PS 158), 807 процессов, 0 отказов, **0 из 269 отличий SPIR-V** в конфигурациях `s17a`
  (ручка не задана) и `s17a0` (`KYTY_S_REPLAY=0`), 0 строк `ShaderReplay` в выводе — **`ALL OK`**
  (`corpus_s17a2_a2fee0d9.out.txt`, `corpus_s17a.tsv` sha256 `ef3a0219…`, 62,2 с). Тот же прогон на `29542308` — `ALL OK`
  (`corpus_s17a2.out.txt`).
- **Набор `shader_cfg_tests`:** 132 теста, **0** строк `ShaderCfgTests: failed:` (S17a — 132 / 0; родитель — 130 / 0; круг tess
  — внутри `TestShaderReplayFormat`, число тестов не меняется); `suite/suite_S3.log`.
- **Фикстура сканера К3:** формат каталога не менялся — строка `ShaderReplayLayout:` набора S17a2 = S17a (`layout_S3.txt`);
  `test_r_addr.py layout_S3.txt` — `LAYOUT OK fields 37`, `ALL OK` (`test_r_addr.out.txt`).
- **Порядок гейтов:** `check_gate_order.py --src src` — `GATE ORDER: clean`, вывод = S17a (гейтов и ручек правка не добавляет).

## 7. Бинарь для S17c [c]

- Эмулятор из чистого worktree `a2fee0d9` (`C:/kyty/s288/s17a/wtS`, `git status` 0 строк; `buildS` переконфигурирован на
  `a2fee0d9`, флаги `build_local.cmd`): **sha256 `2b5e2ce677c557bb0dd28ccc114588aea5c4b6f56c10ab1450faadd81328d544`**, строка
  версии `KytyPS5-2026-09-15-6a2987a-2311-ga2fee0d9` (оба вхождения, вкл. `SDL_REVISION`); закреплённая копия
  `C:/kyty/s288/bin/kyty_emulator_2b5e2ce6.exe`. Установленный бинарь не тронут.
- Тесты S17a2: sha256 `df33f104ffb103169a28046a64e83a4713de3049b6cd4d5d01cc62587fab2e5d` (`C:/kyty/s288/s17a2/bin/`).
- Промежуточный бинарь `29542308` (`b44d2af7`, копия `C:/kyty/s288/bin/kyty_emulator_b44d2af7.exe`) для S17c **не годен**
  (пустая строка в манифесте, §3). Бинарь S17a `6f94cfb4` не годен (RC1, RC4(а)).

## 8. Не заявляется

Что S-replay выполним или даст тёплый первый вход; что К2(2)–К6 пройдут; что остановка на экране подготовки сохранит
перестроенное в игре (сохранение файлов источников — по коду, не прогоном); что ожидание остановки коротко в игре; что форма
без экспорта выполнима; что `R_B` 0,9865 — польза; что каталог верен для первого входа пользователя; что S-replay закрывает
промах `u_06`; что фризы входа вызваны шейдерами; полнота корпуса, каталога и `eboot.bin`; что шейдеры станут быстрее на GPU;
ни одно число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется.

## 9. Процесс

- Замок `C:/kyty/SEALED_RUN.lock` серии F20c (`HPP-561`, теги `f20_v07`…`f20_v10`) — ждал проверкой раз в 60 с (и 3–5 с перед
  окном): 07:06:23–07:13:06Z, 07:14–07:21:07Z, 07:22:08–07:28:57Z, 07:30:00–07:36:12Z.
- **Нарушение общего правила 27:** цепочка configure + сборка эмулятора и тестов `a2fee0d9` шла 07:21:34Z–07:22:34Z; замок
  тега `f20_v09` взят в 07:22:08Z — **26 с компиляции и линковки под стартом тега `f20_v09`**, строка `times.txt` 07:22:34Z
  записана под замком. Сообщено строкой в `HPP-3` (07:29Z) — помеха кадрам старта `f20_v09` на решение лида и звена F20c.
- **Нарушение общего правила 30:** прогон корпуса К2(1) на `a2fee0d9` шёл 62,2 с (07:36:13Z–07:37:15Z) при серии F20c
  (прогноз 48,5 с по прошлому прогону); замка в это время не было (`lock released f20_v10 07:36:11Z`, строка конца — `lock=none`).
- Сборка configure + emu + tests на `29542308` (07:05:52Z–07:06:21Z, 29 с) началась при серии F20c и кончилась за 2 с до замка
  `f20_v07` — правило 30 не пересечено, но запуск при серии был без прогноза.
