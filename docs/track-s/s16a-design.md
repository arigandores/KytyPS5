# S16a — проект S-replay: каталог повтора, переживающий смену подписи транслятора

Звено S16a трека S (Probe Designer, `HPP-605`). Задание — `ROADMAP.md` «СЕССИЯ 122» п. 511(е) (`1c9ec023`) и п. 229(д)(3);
основа — `docs/shader-startup-design.md` §«Recommended next implementation» п. 1–4. Без игры и без кода эмулятора. Все ссылки на
код — на коммит `5fc57612` (`main` на начало звена) в форме `<коммит>:<путь>:<строка>` с якорем и строкой +1. Офлайн-счёт этого звена
(только чтение каталога S13b и разбора `eboot.bin` F23a) — `docs/track-s/s16a/`, время — `C:/kyty/s288/s16a/times.txt` (`date -u`).
Пометки: [c] — проверено кодом или счётом этого звена; [I] — вывод; [U] — неизвестно. Константы, отличные от решений лида, помечены
«вариант исполнителя» — решает лид в S16c.

## 0. Итог

1. **Маршрут не убит условием «хранит адреса гостя», если хранить не то, что хранят сегодня.** Сегодняшний рецепт (`pipelines.bin`) пишет
   сырые байты `ShaderVertexInputInfo` вместе с V# вершинных буферов и полем `addr`: в каталоге S13b у **1 642 из 1 709** графических рецептов
   в занятых слотах есть ненулевые адресные слова [c, §2.1]. Форма S-replay хранит GCN, статический ключ стадии (в нём адресов нет [c]) и
   **канонические слова дескрипторов** (адресные поля обнулены, оставлены только признак «нуль/не нуль» и остаток выравнивания по 16 байт),
   с самопроверкой при записи.
2. **Форма «только специализация» (то, что лежит в кэше трансляции сегодня) смену FS8 не переживает по счёту [c].** Правило `KYTY_FIX_F19=1`
   переставляет бит `manual_depth_compare` по формату гостя, а в файле кэша формата нет. У **81 из 1 214** перестановок каталога S13b этот бит
   при старом правиле равен 1 — под FS8 их специализацию не вывести без формата; на них ссылаются **303 из 1 852** рецептов. Потолок формы
   «только специализация» под FS8 — **1 549 / 1 852 = 0,836 < 0,90**, с учётом GCN — 1 534 / 1 852 = 0,828 (§4.2). Значит, S-replay обязан хранить входы специализации (слова
   дескрипторов), а не её результат. Это довод формы, не убийство маршрута.
3. **Сырой GCN есть без игры.** По хэшу из `.shader_text` AMDGPU ELF в `eboot.bin` (метод F11a / F23a) находятся **487 из 493** программ
   каталога и **1 827 из 1 852** рецептов (0,9865) [c, §4.1]. Нет 23 рецептов со сплавленной стадией Mesh (хэш = XXH3 пары хэшей) и 2 рецептов CS.
4. **Главное неизвестное [U] — восстановление входа VS из статического ключа.** Все 1 709 графических рецептов каталога имеют VS с выборкой
   вершин (ключ не из 8 слов) — нынешний офлайн-перекомпилятор `KYTY_RECOMPILE` их не берёт (`5fc57612:tests/shaderCfgTests.cpp:15195` `if ((!is_compute && !is_pixel && !is_vertex) || (is_compute && key.static_state.size() < 14) ||`; +1 `(is_vertex && key.static_state.size() != 8) ||`).
   Если VS из ключа не восстанавливается, маршрут убит пробой. Это решает проба §4 (код только тестов, не эмулятора).
5. Ручка `KYTY_S_REPLAY` (умолчание 0, чтение раз на процесс, плечом расписания не служит) и критерий кода — §6; цена — §8.

## 1. Что сегодня хранится и почему этого не хватает [c]

| Где | Что лежит | Чего нет / что мешает |
|---|---|---|
| Файл кэша трансляции `_ShaderCache/<title>/<variant>/<stage>_<hash>_<state>.bin` | ключ (стадия, хэш, `user_data_count`, `code_size`, статический ключ), план ресурсов (IR), перестановки: специализация + `CompiledShaderInfo` + SPIR-V — `5fc57612:src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp:769` (якорь `w.U32(key.stage);`; +1 `w.U64(key.hash);`), `5fc57612:src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp:777` (`WritePlan(w, plan);`; +1 `w.U32(static_cast<uint32_t>(permutations.size()));`) | **сырого GCN нет**: `Entry` = план + перестановки — `5fc57612:src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.h:28` (`struct Entry {`; +1 `ShaderRecompiler::IR::ResourcePlan plan;`). Файл читается только при равной подписи `KytySC3:<хэш исходников транслятора>:<опции>:<вариант>` — `5fc57612:src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp:594` (`m_signature = std::string("KytySC") + …`; +1 `std::string(translator_hash) +`); вариант `:fixb26:fixb1b:fixf10[:fixf19]` ещё и меняет папку — `5fc57612:src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp:582` (`const std::string variant = …BvhLoopCapSignatureToken() +`; +1 `…BdaLeanEnabled() ? ":bdalean" : "") +`) |
| Рецепт `pipelines.bin` | на стадию — ключ кэша трансляции и **индекс перестановки**; POD конвейера; сырые байты входа стадии без «рантайм»-части — `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:6037` (`void PipelineCache::RecordGraphicsRecipe(…`; +1 `const ShaderVertexInputInfo& vs_input_info,`), `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:6066` (`w.Info(vs_input_info);`; +1 `if (ps_active) {`), писатель байтов — `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5933` (`void Info(const T& info) {`; +1 `const auto*  base  = …`) | индекс перестановки не переживает смену транслятора (порядок и число перестановок — свойство прогона); байты `ShaderVertexInputInfo` несут V# (`fields[0..1]` — адрес, `5fc57612:src/graphics/shader/shaderBindings.h:37` `void UpdateAddress48(uint64_t gpu_addr) {`; +1 `auto lo = …`) и `ShaderVertexInputBuffer::addr` (`5fc57612:src/graphics/shader/shaderBindings.h:179` `uint64_t addr = 0;`; +1 `uint32_t stride = 0;`); файл целиком отбрасывается при чужой подписи — `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:6565` (`if (r.Failed() \|\| signature != expected) {`; +1 `LOGF("PipelinePrecache: stale recipes (signature mismatch), ignored\n");`), подпись = подпись кэша + раскладка — `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:6126` (`const auto signature = m_program_cache->translation_cache.Signature() + RecipeLayoutSignature();`; +1 `w.U32(static_cast<uint32_t>(signature.size()));`) |
| Стартовый каталог `_ShaderSeeds/<title>/` | копия файлов кэша трансляции и `pipelines.bin` | совместимость = игра, версия, подпись транслятора, раскладка, **модель GPU** — `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:6430` (`const auto compatibility = fmt::format("KytySeed1:…`; +1 `PipelineCacheTitleId(), app_version, signature, RecipeLayoutSignature(),`); при несовпадении — «ignored» `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:6443` (`if (stored != compatibility) {`; +1 `PipelineCacheLog("ShaderSeed: incompatible game, GPU or translator; ignored");`) |

Вывод [c]: смена подписи треком F (FS8: `KYTY_FIX_F19=1`, новая подпись и папка `_fixf19`, п. 471(0)) делает каталог S13b нечитаемым целиком
(п. 511(д)). Вернуть его без входа в сцены можно только из входов трансляции, а их в каталоге нет.

## 2. (1) Что хранит S-replay — по местам кода

### 2.1 Что именно транслятор читает [c]

Путь новой перестановки — `ProgramCache::Compile`: `TranslateProgram(params.code, options)` → `ExtractResourcePlan` → `MaterializeResources` →
`CompilePermutation` — `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:4007` (`auto translated = prepared ? std::move(*prepared) :`;
+1 `ShaderRecompiler::TranslateProgram(params.code, options);`), `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:4011` (`auto resource_plan = ShaderRecompiler::IR::ExtractResourcePlan(translated.program);`;
+1 `if (!ShaderRecompiler::IR::MaterializeResources(resource_plan, runtime, resource…`), `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:4023` (`entry->second.permutations.push_back(CompilePermutation(`;
+1 `params, options, std::move(translated), std::move(specialization), push_data_cur…`).

Входы и их природа:

| Вход | Адреса гостя? | Место |
|---|---|---|
| GCN (`params.code`), у сплавленной GS ещё `back_code` | нет (код) | `5fc57612:src/graphics/shader/recompiler/ShaderRecompiler.cpp:555` (`if (!options.back_code.empty()) {`; +1 `decoded = DecodeFusedProgram(code, options.back_code, joined_code);`) |
| значения user data | **в трансляцию идёт только их число** | `5fc57612:src/graphics/shader/recompiler/ShaderRecompiler.cpp:641` (`static_cast<uint32_t>(options.user_data.size()), wave_size);`; +1 `if (!embedded_fetch.loads.empty()) {`), `5fc57612:src/graphics/shader/recompiler/ShaderRecompiler.cpp:652` (`.user_data_count  = static_cast<uint32_t>(options.user_data.size()),`; +1 `.input_info = options.input_info,`). У сплавленной GS в `user_data[0..1]` кладётся адрес — `5fc57612:src/graphics/shader/shader.cpp:1007` (`params.user_data[0] = static_cast<uint32_t>(regs.gs_regs.user_data_addr);`; +1 `params.user_data[1] = …>> 32u);`) — не хранить |
| статический вход стадии (`ShaderVertexInputInfo` / `ShaderPixelInputInfo` / `ShaderComputeInputInfo`) | ключ стадии — **нет**: для VS берутся шаг, swizzle, `DstSel`, формат, OOB, `AddTid` и регистры назначения, адрес не берётся | `5fc57612:src/graphics/shader/shader.cpp:862` (`void BuildStageStaticKey(const ShaderVertexInputInfo& info, …`; +1 `EXIT_IF(info.resources_num < 0 \|\| …`), `5fc57612:src/graphics/shader/shader.cpp:899` (`for (int i = 0; i < info.resources_num; i++) {`; +1 `const auto& resource = info.resources[i];`), `5fc57612:src/graphics/shader/shader.cpp:906` (`key.push_back(resource.Stride());`; +1 `key.push_back(…SwizzleEnabled()));`) |
| слова дескрипторов (V#, T#, S#), прочитанные планом | **да** (база V#, база и метаданные T#) | `MaterializeResources` = `MaterializeSnapshot` (чтение памяти гостя) + `BuildResourceSpecialization` (чистая функция слов) — `5fc57612:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:1094` (`if (!MaterializeSnapshot(program, runtime, materialized)) {`; +1 `return false;`), `5fc57612:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:1099` (`BuildResourceSpecialization(program, std::move(materialized), snapshot, specialization);`; +1 `lap.Mark(…MatSpecNs);`) |

Из адресных полей специализация берёт только: признак «нулевой T#» — `5fc57612:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:122` (`bool NullImageDescriptor(…) {`; +1
`return descriptor.dwords[0] == 0 && (descriptor.dwords[1] & 0xffu) == 0;`) — и класс выравнивания базы V# — `5fc57612:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:553`
(`const auto cls = aligned_copy ? 2u : PackedStrideAlignmentClass(descriptor.Base48());`; +1 `packed_stride |= cls << PackedStrideAlignmentShift;`).
Комментарий кода прямо говорит, что адреса в специализацию не входят — `5fc57612:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.h:14`
(`// Canonical module-affecting resource state. Runtime addresses and descriptor payloads remain in`; +1 `// ResourceSnapshot and therefore do not create shader permutations.`).

Создание конвейера читает из входа VS только формат, `DstSel`, OOB, `AddTid`, swizzle и регистры назначения (все в ключе) — `5fc57612:src/graphics/host_gpu/renderer/pipeline/shaders.cpp:448`
(`const auto registers_num = vs_input_info.resources_dst[index].registers_num;`; +1 `const auto compiled_components =`), `5fc57612:src/graphics/host_gpu/renderer/pipeline/shaders.cpp:453`
(`GetInputFormat(vs_input_info.resources[index], input_attr[index].format, attr_size,`; +1 `static_cast<uint32_t>(used_components));`) [c поиска по телу
функции; полнота списка — I, проверяется пробой].

Счёт по каталогу S13b (`docs/track-s/s16a/f19amb.out.txt`, скрипт `f19amb.py`; рецепты: `addr` — §4.1): графических рецептов 1 709, вычислительных 143;
у 1 642 графических в занятых слотах входа VS ненулевые адресные слова; VS без выборки вершин (ключ из 8 слов) — 0 [c].

### 2.2 Записи каталога (предлагаемый формат `KytyReplay1`)

| Запись | Поля | Не хранится (условие п. 229(д)(3)) |
|---|---|---|
| **R-SRC** (источник) | стадия; хэш (`ShaderComputeHash`: объявленный AGC-хэш или XXH3 кода — `5fc57612:src/graphics/shader/shader.cpp:100` `uint64_t ShaderComputeHash(…) {`; +1 `if (code == nullptr \|\| size_bytes < 8u) {`); `code_size`; `user_data_count`; статический ключ стадии и его версия `STATIC_KEY_VERSION`; признак сплава и хэши половин; sha256 кода; **GCN** — своей копией (локальная форма) или ссылкой «хэш + sha256» на `.shader_text` в файлах игры (поставляемая форма, §5.1) | указатели, адреса, значения user data, IR, номера узлов IR |
| **R-SPEC** (вход специализации) | ссылка на R-SRC (стадия, хэш, хэш ключа); на каждый ресурс плана — **канонические слова** дескриптора, привязанные к тождеству ресурса в GCN (вид, `first_use_pc`, порядковый номер среди ресурсов того же `first_use_pc`), не к индексу плана; косвенные таблицы картинок: ключи, кандидаты, канонические T#; S# как есть; версия правил канонизации `CANON_VERSION` | индекс перестановки, `ResourceSpecialization` как результат (только справкой для самопроверки), снимок `flattened_srt`, `user_data` |
| **R-PIPE** (рецепт) | ссылки на R-SPEC каждой стадии; `PipelineRenderingState`, `PipelineVertexInputState`, `PipelineStaticParameters` (POD без адресов — `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.h:44` `struct PipelineStaticParameters {`; +1 `bool negative_one_to_one = false;`; `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.h:79` `struct PipelineRenderingState {`; +1 `std::array<vk::Format, …> color_formats {};`; `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.h:88` `struct PipelineVertexInputState {`; +1 `struct Binding {`) | сырые байты `Shader*InputInfo`: вход стадии восстанавливается из статического ключа R-SRC |

**Правила канонизации** (вариант исполнителя; полный список полей T# — Emu Engineer по раскладке RDNA2, проверка — самопроверка ниже):
V# — база := 0, если база 0, иначе `0x100 | (база & 0xF)` (сохраняет класс выравнивания и «не нуль», `Base48` ничего не узнаёт об адресе);
T# — поле базы (`dwords[0]`, `dwords[1][7:0]`) := 0 у нулевого T#, иначе адрес `0x100`; поля адреса метаданных := 0; прочие слова как есть;
S# — как есть [I: адресов нет]. **Самопроверка при записи (обязательная):** `BuildResourceSpecialization(план, канон) == живая специализация`
этой перестановки; иначе запись не пишется и растёт `canon_mismatch` (§7). Новый транслятор, которому нужен вход вне записи, обязан поднять
`REPLAY_INPUT_VERSION` — тогда запись отвергается (`rej_version`) и заучивается заново (`docs/shader-startup-design.md` п. 2).

**Условие убийства «хранит указатели/адреса» — не наступает при этих правилах [c для ключа и POD; I для полного списка полей T#].** Контроль —
офлайн-сканер `R_ADDR` (§7): число ненулевых адресных полей в записях = 0; положительный контроль сканера — тот же счёт по нынешнему
`pipelines.bin` S13b = 1 642 [c].

### 2.3 Где записи снимаются

- **R-SRC** — на общем пути поиска программы (`ProgramCache::Get` → `Compile` и `LoadFromTranslationCache`): GCN в руках как `params.code`;
  первая встреча (стадия, хэш, ключ) в прогоне при `KYTY_S_REPLAY` ≠ 0 и отсутствии записи в каталоге — копия кода в очередь писателя.
  Регистрация AGC (`5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:6325` `void PipelineCache::TraceShaderRegistration(…) {`;
  +1 `if (DumpGcnAtRegistration()) {`) — только CS и только ради раннего открытия; в первую итерацию не нужна.
- **R-SPEC** — при создании перестановки (промах, `5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:4023` `entry->second.permutations.push_back(CompilePermutation(`; +1 `params, options, std::move(translated), std::move(specialization), push_data_cur…`) и при первом в прогоне попадании в перестановку без записи: повтор
  `MaterializeSnapshot` (чистая функция плана и памяти, раз на (перестановка, прогон)), канонизация, самопроверка, очередь.
- **R-PIPE** — рядом с `RecordGraphicsRecipe` / `RecordComputeRecipe` (`5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:6037` `void PipelineCache::RecordGraphicsRecipe(…`; +1 `const ShaderVertexInputInfo& vs_input_info,`), со ссылками на R-SPEC вместо индексов.
- **Писатель** — отдельный поток (по образцу S-pcw: запросы — атомарный флаг, без замка на потоке GuestGpu), очередь ограничена (вариант
  исполнителя: 4 096 записей; переполнение — `dropped_queue`), файлы поколениями `replay.<g>.bin` + указатель `replay.cur` (временный файл
  и переименование); источники публикуются раньше зависящих R-SPEC/R-PIPE; последнее полное поколение сохраняется при обрыве записи.
- **Папка** — `_ShaderCache/<title>/replay/` — на уровне игры, **вне** папки варианта: она обязана пережить смену подписи и варианта.

## 3. (2) Перестройка под новой подписью при запуске

Порядок (вариант исполнителя):
1. `StartPrecache` → `InstallShaderSeed` как сегодня (`5fc57612:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:6512` `InstallShaderSeed();`;
   +1 `m_recipes_path = … / "pipelines.bin";`). Совместимый seed — быстрый путь, перестройка не нужна.
2. Если в папке варианта нет `pipelines.bin` текущей подписи, а каталог повтора совместим (`KytyReplay1:<title>:<APP_VER>:<формат>:<STATIC_KEY_VERSION>:<CANON_VERSION>:<REPLAY_INPUT_VERSION>` —
   **без подписи транслятора и без модели GPU**), поток precache до чтения рецептов выполняет перестройку:
   (а) источники: GCN из своей копии или из `.shader_text` игры, сверка sha256; (б) на ограниченном пуле воркеров на каждый R-SRC — `TranslateProgram`
   новым транслятором с входом стадии, восстановленным из ключа; на каждый его R-SPEC — `ExtractResourcePlan`, сопоставление канонических слов
   ресурсам нового плана по тождеству GCN, `BuildResourceSpecialization` **новыми правилами** (так F19 и любая смена правил над захваченными
   словами отрабатывают сами), `CompilePermutation`, `ValidateShaderSpirv`, `ShaderTranslationCache::Save` под новой подписью; (в) рецепты:
   R-PIPE → индексы новых перестановок → `pipelines.bin` (временный файл и переименование, только после завершения (б)); (г) дальше — обычный
   precache (`PrecachePipelines`, экран подготовки как сегодня).
3. Экран подготовки: `PreparationStatus` получает счёт перестройки (подготовлено / отвергнуто / ожидает) отдельно от счёта конвейеров.
4. Отказы: несовместимый каталог — перестройки нет, строка в лог; отвергнутая запись — обычная трансляция при первом использовании, как
   сегодня; закрытие окна — `m_precache_stop`: файлы кэша трансляции по одному валидны, `pipelines.bin` не пишется, следующий запуск
   перестраивает остаток; отказ записи (`Save` / переименование) — счёт `rej_write`, запись остаётся в памяти прогона, путь игры прежний.
5. Цена на экране [I]: 1 214 перестановок каталога S13b × 8–23 мс трансляции [c диапазона п. 511(ж)(1)] ≈ 10–28 с процессора, на пуле
   воркеров — секунды до десятков секунд поверх нынешних 33–40 с экрана; предел п. 229(д)(2) — 180 с. Измеряется в коде, не здесь.

## 4. (3) Офлайн-проба условия убийства

### 4.1 Что уже посчитано без игры [c]

Скрипты и выводы — `docs/track-s/s16a/` (читались только каталог S13b `C:/kyty/s288/s13/seeds/PPSA21564` и `docs/track-f/f23a/scan_eboot.jsonl.xz`).

| Величина | Число |
|---|---|
| Каталог S13b: файлов кэша трансляции / программ (стадия, хэш) / перестановок / рецептов | 726 / 493 / 1 214 / 1 852 (гр. 1 709, выч. 143); подпись `KytySC3:26ce5fc7…:robust:ftz:cbank:fixb26:fixb1b:fixf10`; разбор 726 из 726 до конца файла (`ALL OK`) |
| Программ каталога, чей GCN есть в `eboot.bin` по хэшу `.shader_text` | VS 149/149, PS 223/223, CS 114/116, Mesh 1/5 (Mesh лежит в файлах `cs_`) → 487/493 |
| Рецептов, у которых GCN всех стадий есть в `eboot.bin` | **1 827 / 1 852 = 0,9865** (нет: 23 графических со стадией Mesh, 2 вычислительных) |
| Графических рецептов с ненулевыми адресными словами во входе VS | 1 642 / 1 709 |
| Перестановок с картинкой сравнения глубины, у которой старый бит `manual_depth_compare` = 1 (под F19 бит зависит от формата, которого в файле нет) | 81 / 1 214 (в 74 файлах; файлов с картинкой сравнения — 80) |
| Рецептов, ссылающихся на такую перестановку | **303 / 1 852** (гр. 280, выч. 23) |

Почему ровно эти 81 [c кода]: старое правило — `manual = не нуль && формат ≠ k32Float` (`5fc57612:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:605` `image.manual_depth_compare = !NullImageDescriptor(descriptor) &&`;
+1 `format != Prospero::BufferFormat::k32Float;`), новое — `manual = не нуль && формат ∉ {k16UNorm, k32Float}` (`5fc57612:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:602` `image.manual_depth_compare =`;
+1 `FixF19ManualDepthCompare(format, NullImageDescriptor(descriptor));`, правило — `5fc57612:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:39` `bool FixF19ManualDepthCompare(Prospero::BufferFormat format, bool null_descriptor) {`; +1 `return !null_descriptor && FindGuestDepthFormatPolicy(format) == nullptr;`). Старый 0 ⇒ новый 0; старый 1 ⇒ новый 0 при `k16UNorm`
и 1 при прочих форматах — ровно два исхода.

### 4.2 Проба П-S16 (предлагается; код — только тесты `shader_cfg_tests`, не эмулятор)

**Источник GCN — `eboot.bin` (метод F11a / F23a: AMDGPU ELF, `XXH3-64(.shader_text)` = хэш, код = префикс `code_size`), выбран проектом.**
Цена 0 игры и 0 замка; калибровка метода у F23a — 331 из 331 дампа T1 равны префиксу `.shader_text` того же хэша [c F23a]. Корпус T1
`_Shaders/original` / `s4/gcn` (337 программ, старее каталога) — только контроль равенства байтов; дампы регистрации `KYTY_DUMP_GCN=2`
требуют игры — не используются. GCN извлекается во временную папку звена вне git (код игры в git не кладётся).

**Знаменатель:** 1 852 рецепта каталога S13b (манифест `s13/seeds_manifest.txt` sha256 `65a95adf…`).

**Плечо A — тождество (достаточность записи).** Бинарь тестов из дерева S12/FS6 (`4d9e8ab7`; строка подписи бинаря обязана быть `26ce5fc7…` —
член-контроль, иначе плечо `NO_POWER`). На каждую перестановку, на которую ссылается рецепт: GCN по хэшу → вход стадии **из статического
ключа** (новый код теста: VS с выборкой вершин, clip, mesh, tess; PS и CS — как `KYTY_RECOMPILE`) → `TranslateProgram` → эмиссия с
хранимой специализацией → SPIR-V **байт в байт** с хранимым. Не равно — `rej_ident` (вход неполон или транслятор недетерминирован).

**Плечо B — подпись FS8.** Бинарь тестов из дерева с кодом F19 (FS8a, если собран к пробе; иначе `main` с `082d1612` и `f98e842c`) при
`KYTY_FIX_F19=1`; строка подписи пишется в вывод, при расхождении с подписью FS8d плечо B повторяется. На каждую перестановку — тот же путь;
у 81 «неоднозначной» — **оба исхода** правила (`KYTY_RECOMPILE_F19_FORMAT=k16UNorm` и `=k8UNorm`, механизм есть — `5fc57612:tests/shaderCfgTests.cpp:15377`
`if (const char *f19 = std::getenv("KYTY_RECOMPILE_F19_FORMAT");`; +1 `f19 != nullptr && ShaderRecompiler::IR::FixF19Enabled()) {`); засчитывается,
только если оба исхода транслируются и проходят проверку. Каждый SPIR-V — встроенная проверка формы устройства (`uniformBufferStandardLayout`).

**Исходы рецепта:** `prepared` — все стадии: GCN найден, плечо A равно, плечо B транслируется, эмитируется и проходит проверку; иначе
`rejected` с одной причиной по порядку: `src` (нет GCN), `fused` (Mesh-сплав без пары половин), `key` (вход не восстанавливается из ключа),
`ident` (плечо A не равно), `translate`, `emit`, `val` (плечо B).

**Чтение (вариант исполнителя; решает лид в S16c, до данных):**
- `R_B = prepared / 1 852`. **`R_B` < 0,90 — S-replay убит по п. 229(д)(3)** (форма с каноническими словами не может перестроить ≥ 90 % даже при
  идеальном захвате). `R_B` ≥ 0,90 — условие убийства не наступило; маршрут идёт в код (§6).
- Справка, решения не несёт: `R_spec = (prepared без 303 «неоднозначных») / 1 852` — потолок формы «только специализация»; уже сейчас
  ≤ 1 534 / 1 852 = 0,828 с учётом GCN (без него — 1 549 / 1 852 = 0,836) [c].
- Тождества скорера: `prepared + Σ rejected_* = 1 852`; причины — разбиение (одна на рецепт); по стадиям — перестановок в плечах A и B
  поровну; `f19_both` ≤ 81.
- Потолок до данных [c]: `R_B` ≤ 0,9865 (GCN). Чтобы убийство не наступило (`prepared` ≥ 1 667), проба может потерять сверх 25 рецептов без GCN не больше 160.
- Априор исполнителя [I]: P(`R_B` ≥ 0,90) ≈ 0,5 — риск один: восстановление входа VS из ключа (1 709 рецептов из 1 852 имеют VS).

**Цена пробы:** одно звено Emu Engineer (код теста + извлечение GCN + два плеча; без игры и замка; команды дольше 60 с — только вне серий
других треков, общее правило 30), отзыв Red Team, чтение лида. Стена [I] ≤ 30 мин на два плеча (1 214 перестановок × 2 + 81).

## 5. (4) Взаимодействия

### 5.1 `_ShaderSeeds` и проверка совместимости
- Seed остаётся быстрым путём; перестройка — только когда seed несовместим или его нет, и только в папку варианта текущей подписи.
- Совместимость каталога повтора не включает подпись транслятора и модель GPU (GCN и слова дескрипторов от них не зависят); производные
  кэши по-прежнему ключуются подписью и GPU (`docs/shader-startup-design.md` п. 3).
- **Поставляемая форма** (`_ShaderSeeds/<title>/replay/`) — без GCN: R-SRC несёт хэш и sha256 кода, код берётся из `.shader_text` установленной
  игры; программы вне `eboot.bin` (6 из 493 [c]) в поставляемой форме отвергаются (`src`). **Локальная форма** (`_ShaderCache/<title>/replay/`)
  хранит свою копию GCN и в git не кладётся. Вопрос лиду (§10.2): кладётся ли поставляемая форма (слова дескрипторов — данные игры) в `ps5-em`.

### 5.2 Трек F
- Каждая смена подписи (FS-бинарь с новым умолчанием, откат ручкой `KYTY_FIX_*=0` на холодной папке варианта) — первый запуск
  перестраивает каталог вместо холодных входов.
- Правило для кода трека F (вариант исполнителя, вносит лид): правка, после которой трансляция или специализация читают вход вне записи
  (статический ключ, канонические слова, GCN), обязана поднять `REPLAY_INPUT_VERSION`; правка формы ключа — `STATIC_KEY_VERSION`; Red Team
  проверяет это в каждом ревью кода, трогающего `BuildStageStaticKey`, `MaterializeSnapshot`, `BuildResourceSpecialization`, `CompileOptions`.
  Смена правил над уже захваченными словами (как F19) версии не требует.
- **Подпись кэша трансляции:** S-replay вызывает `BuildResourceSpecialization` вне `MaterializeResources` — экспорт из
  `src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp` меняет хэш исходников транслятора, то есть **сам S-replay меняет
  подпись** (холод у пользователя). Вариант исполнителя: отгрузка S-replay — только вместе с ближайшей отгрузкой трека F, меняющей подпись.

### 5.3 Треки P и S
- Патч P-var кода игры не меняет (`KYTY_GAME_PATCH` пишет в данные) [I] — на хэши GCN не влияет.
- S-cat (S15) — сбор каталога на FS8; если код S-replay появится раньше S15b, сбор S15b снимает записи повтора даром (`KYTY_S_REPLAY=2`).
  Иначе первое поколение каталога повтора — отдельный сбор при `=2` (цена — как S13b: ≈ 3 956 с игры, п. 511(е)).

## 6. (5) Ручка `KYTY_S_REPLAY` и критерий кода

**Значения (вариант исполнителя):** `0` (умолчание; unset, пусто, `0` — выкл): ни файлов, ни строк, ни потока писателя, поведение байт в байт
прежнее; `1` — захват и перестройка; `2` — только захват (сбор); `3` — только перестройка (чистая проба перестройки). Читается раз на процесс
(статическая переменная, как `KYTY_S_PCW`); плечом ABBA не служит — перестройка идёт до гостя, захват — на холодном пути. Ручка — переменная
окружения, не строка `KNOB_DEFINITIONS`; если исполнитель кода заведёт её в гейт-файл — новое имя последней строкой, `check_gate_order.py`
после патча и до сборки, замена на месте, не дописывание.
Стенд положительного контроля: `KYTY_S_REPLAY_TEST=canon` (портит одно поле канонизации T# — счёт `canon_mismatch` обязан стать > 0),
`KYTY_S_REPLAY_TEST=spec` (портит один бит специализации при перестройке — `rb_live_mismatch` обязан стать > 0). Умолчание стенда — выкл.

**Критерий кода (вариант исполнителя; решает лид в S16c, до кода):**
- **К0 (до кода)** — проба §4.2: `R_B` ≥ 0,90; плечо A — 100 % `prepared` байт в байт.
- **К1** — код-ревью Red Team: каждый новый сайт под `KYTY_S_REPLAY` ≠ 0; канонизация не пропускает адресных полей; публикация «источники
  раньше рецептов»; отмена по `m_precache_stop`.
- **К2 (`=0` байт в байт)** — корпус T1: SPIR-V при `=0` равен бинарю без правки той же подписи на всех `OK`; тег V при `=0`: строк
  `ShaderReplay:` 0, папки `replay/` нет, видео ≥ 3 000 кадров 0 глитчей и лист; W — 0 `[Vulkan][E]`.
- **К3 (захват)** — тег сбора `=2` на уровне каталога: `canon_mismatch` = 0, `dropped_queue` = 0; со стендом `canon` — `canon_mismatch` > 0;
  офлайн `R_ADDR` = 0 по записанному каталогу (положительный контроль сканера — 1 642 на `pipelines.bin` S13b).
- **К4 (перестройка под новой подписью)** — бинарь со сменой подписи (FS8 или вариант `KYTY_FIX_F19=1` на копии), пустая папка варианта,
  `=3`: `prepared / записей` ≥ 0,90; **сверка с живой трансляцией** — тот же уровень холодным прогоном при `=0` той же подписи: у перестановок,
  встреченных в обоих, SPIR-V байт в байт (`rb_live_mismatch` = 0; со стендом `spec` — > 0).
- **К5 (вход)** — после К4 первый вход уровня: трансляций программ каталога во время игры 0 (против нулевого контроля `=0` на пустой папке — > 0),
  экран подготовки ≤ 180 с, видео ≥ 3 000 кадров 0 глитчей и лист лида, W 0 `[Vulkan][E]`, 0 маркеров смерти.
- **К6 (отказы)** — стенд закрытия окна во время перестройки и испорченного поколения: следующий запуск перестраивает остаток, путь игры прежний.

## 7. Счётчики и строки лога (тип каждого)

Инструмент не покадровый: строк `FrameTrace-x` нет; всё — строки лога раз на событие.

| Строка / поле | Тип | Когда |
|---|---|---|
| `ShaderReplay: mode=<n> dir=<путь> compat=<ok\|mismatch\|absent> generation=<g>` | перечисление, целое | раз на процесс при `≠ 0` |
| `ShaderReplay: rebuild records=<N> prepared=<P> rejected=<R> pending=<Q> rej_src= rej_fused= rej_key= rej_version= rej_shape= rej_translate= rej_emit= rej_val= rej_write= translate_ms=<t> wall_ms=<w>` | штуки u32; `*_ms` — мс (u64) | раз на перестройку |
| `ShaderReplay: capture sources=<s> specs=<m> pipes=<p> canon_mismatch=<k> dropped_queue=<q> bytes=<b> gen=<g>` | штуки u32; `bytes` — байты u64 | каждые 256 записей и на `Save` |
| офлайн `R_ADDR` | штуки | сканер каталога |
| офлайн/тег `rb_live_mismatch` | штуки | К4 |

**Обязаны быть 0:** `canon_mismatch`, `dropped_queue` (при варианте 4 096), `rej_write`, `R_ADDR`, `rb_live_mismatch`, `rej_ident` пробы.
**Тождества для скорера:** `prepared + rejected + pending = records`; `rej_src + rej_fused + rej_key + rej_version + rej_shape + rej_translate +
rej_emit + rej_val + rej_write = rejected` (разбиение, одна причина на запись); после завершения перестройки `pending = 0`; в строке захвата
`specs` ≥ число новых перестановок прогона минус `canon_mismatch` (подмножество, не разбиение — объявлено).

## 8. Цена

- **Инструмент в игре [I]:** при `=0` — одна проверка статического флага на холодных сайтах; при `≠ 0` — одна загрузка и ветвь на попадание
  в перестановку (флаг «записано»), один повтор `MaterializeSnapshot` на (перестановка, прогон), копия GCN на источник; запись — вне потока
  GuestGpu. Перестройка — на экране подготовки до гостя.
- **Код [I]:** формат и писатель, канонизация с самопроверкой, восстановление входа стадии из ключа (общее с кодом пробы), перестройка в
  потоке precache, строки лога, стенды — порядка 800–1 200 строк; экспорт `BuildResourceSpecialization` в `shader/**` — смена подписи (§5.2).
- **Звенья (вариант исполнителя):** S16b отзыв → S16c лид → **проба:** S16d Emu Engineer (код теста + два плеча, без игры) → S16e Red Team →
  S16f лид (К0) → **код:** S17a Emu Engineer → S17b Red Team → S17c Harness Engineer (теги К2–К5: сбор `=2`, перестройка `=3` + холодный `=0`
  для сверки, вход V, W; 5–6 тегов) → S17d лид. Итого после S16c — 7 звеньев.
- **Замок [I]:** проба — 0; код — 5–6 тегов ≈ 40–70 мин замка плюс сбор первого поколения (если не совмещён с S15b) ≈ 66 мин игры.
- **Против повторного сбора [c п. 511(е)]:** 3 956 с игры на 19 уровней + цепочка печати и замка на каждую смену подписи; S-replay платит один
  раз и затем по экрану подготовки.

## 9. Положительный и нулевой контроль

- **Вооружился (положительный):** строка `ShaderReplay: mode=` при `≠ 0`; после сбора `=2` — `sources` > 0, `specs` > 0 и файл поколения на
  диске; после перестройки `=3` на пустой папке варианта — `prepared` > 0 и файлы кэша трансляции новой подписи; стенды `canon`, `spec` делают
  свои нулевые счётчики положительными (сила нулей К3, К4).
- **Ничего не стоит при 0 (нулевой):** К2 — нет строк, нет файлов, корпус T1 байт в байт, V/W без вреда; нулевой контроль перестройки — `=0` на
  пустой папке варианта даёт холодные трансляции (> 0) — это и мера пользы.

## 10. Что известно [c], что [I], что [U]; не доказывается; вопросы лиду

### 10.1 Статусы
- **[c]:** входы трансляции и места чтения (§2.1); отсутствие GCN в кэше трансляции; адреса в байтах рецептов (1 642 / 1 709); GCN каталога
  в `eboot.bin` (487 / 493 программ, 1 827 / 1 852 рецептов); 81 / 1 214 перестановок и 303 / 1 852 рецепта, зависящих от формата под F19;
  потолок формы «только специализация» 0,836; создание конвейера читает из входа VS только поля ключа (по найденным сайтам).
- **[I]:** S# без адресов; полный список адресных полей T#; что транслятор не читает полей входа стадии вне ключа (иначе нынешний кэш
  трансляции был бы неверен); цена перестройки на экране; объём кода; P(`R_B` ≥ 0,90) ≈ 0,5.
- **[U]:** восстанавливается ли вход VS с выборкой вершин из ключа (решает проба); транслирует ли FS8 весь GCN каталога; сплав Mesh по паре
  половин; время перестройки и его влияние на экран; поведение создания конвейеров из перестроенных рецептов на устройстве (только К4–К5).

### 10.2 Вопросы лиду (комментарием в `HPP-605` и строкой в `HPP-3`)
1. Чтение пробы §4.2 (`R_B` < 0,90 — убит; `R_spec` — справка) и знаменатель (рецепты S13b, не каталог S15) — принять или заменить до данных.
2. Ручка: значения `0/1/2/3` и стенды `KYTY_S_REPLAY_TEST` — принять или сузить.
3. Отгрузка кода S-replay только вместе с отгрузкой трека F, меняющей подпись (§5.2) — принять или нет.
4. Поставляемая форма без GCN в `ps5-em` (слова дескрипторов — данные игры) — разрешить или держать каталог повтора только локально.
5. Правило `REPLAY_INPUT_VERSION` / `STATIC_KEY_VERSION` для ревью трека F — вносить ли в общие правила Red Team.

### 10.3 Не доказывается
Что S-replay выполним; что каталог верен для первого входа пользователя; что перестройка уложится в 180 с; что запись кэша — причина фризов
холодного входа; что фризы входа вызваны шейдерами; что кадры ≥ 100 мс `u_06` вызваны шейдерами; где хранится тепло драйвера; нейтрализация
кэша драйвера; полнота корпуса, каталога и `eboot.bin` как источника; что шейдеры станут быстрее на GPU; ни одно число — не выигрыш;
60 FPS не обещаются; цель (B) не меняется.
