# FS4c (`HPP-472`, Harness Engineer): печать и теги `fs4_r0`/`fs4_r1`/`fs4_hb`/`fs4_w`/`fs4_v` бинаря FS4 под замком (умолчание `KYTY_FIX_SVAL=1`)

## 0. Печать (до первого тега; после неё харнесс, ридер и правила не меняются)

Решения лида (ссылки — `<коммит>:<путь>:<строка>`, якорь и контроль +1 сверены `git show` скриптом `mk_seal_fs4c.py` 2026-10-03T08:36:09Z):

- п. 378 — `8449030a:docs/ROADMAP.md:20552` (якорь «378. **Звено F10f трека F (`HPP-454`, лид): Ф16 `FIXED` по п. 369(в)»; +1 — «прошла; счёт трека F,
  не отгрузка; умолчание `KYTY_FIX_SVAL=1`»); члены FS4 — `8449030a:docs/ROADMAP.md:20588` (якорь «(г) **Отгрузка — FS4, четвёртый бинарь отгрузки трека F
  (константы лида):**»; +1 — «(1) **FS4a (Emu Engineer, без замка).**»); член FS4c — `8449030a:docs/ROADMAP.md:20601` (якорь «(3) **FS4c (Harness Engineer,
  под замком; очередь P > F > S, п. 322(г)).**»; +1 — «удаление живого каталога варианта, манифест sha256 кэшей до/после, EQUAL»); порядок установки —
  `8449030a:docs/ROADMAP.md:20622` (якорь «(5) **Порядок установки с треком P.** Бинарь FS4 обязан содержать»).
- п. 383 (приёмка FS4b) — `a193028b:docs/ROADMAP.md:20734` (якорь «383. **Звено FS4b трека F (`HPP-471`, Red Team, review лида): принят»; +1 — «FS4c; FS4c
  (`HPP-472`) снимается с блока**»); **З2** — `a193028b:docs/ROADMAP.md:20749` (якорь «(в) **З2 (откат возвращает отказ Ф16 только на новой трансляции)**»;
  +1 — «холодном каталоге варианта; если `fs4_r0` идёт после»), отзыв — `17b51c7f:docs/track-f/fs4b-review.md:108` (якорь «**З2 — откат `KYTY_FIX_SVAL=0`»);
  комментарий лида `64e6a50c` звена (2026-10-03T08:25:55Z): бинарь `C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe`, опознание по sha256 и `KYTY_GIT_REVISION`,
  строка `SDL_REVISION` (`92d11340`, З1) — не происхождение.

Пункты после выдачи звена перечитаны до печати: 379 (S9b/S10 — объём FS4c не меняет), 380 (FS4a принят — бинарь §1), 381 (F11d — не меняет), 382 (S9r2 —
не меняет), 383 (FS4b принят; З2 — §2, §3), 384 (F11e принят; F11f `HPP-468` идёт — тот же трек, замок по одному тегу; п. 371(е)(2) — звено без замка не
запускает команду дольше 60 с, пока у звена прогонов другого трека идёт серия: сборки и долгих команд вне замка у FS4c нет, разбор `post_fs4c.sh` — после
тега, по той же проверке). Очередь замка P > F > S (п. 322(г)); P43 `HPP-464` на момент печати `blocked`, без идущего прогона (строка `times.txt`).
Образцы — F10e `b0a18f9d:docs/track-f/f10e.md` (холод, манифест, R0/R1/W) и FS3c `a1a1d971:docs/track-f/fs3c.md` (W/V Sky Garden тёплые, `fs3_hb`).

## 1. Бинарь

- **FS4** `31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5` — копия `C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe` (FS4a `HPP-470`, отчёт
  `docs/track-f/fs4a.md`, коммит сборки `3d0e46da` = FS3 `d515b901` + копия F10c `92d11340` + копия FS4a; ревью FS4b `17b51c7f` — PASS, п. 383).
  **Опознание — по sha256 копии и sha256 установленного файла после установки** (`runs/<тег>/installed_sha.txt`); строки бинаря (до тега, этой печатью):
  `Fork build arigandores/KytyPS5 3d0e46d` — 1; `KytyPS5-2026-09-15-6a2987a-1874-g3d0e46da` — 1; `-g92d11340` — 1. Текст `KYTY_GIT_REVISION` в логе/stdout тега (`Fork build arigandores/KytyPS5 3d0e46d…`, `, git = …-g3d0e46da`), если он есть, — строка
  ридера «называет `3d0e46d`» (справка, не гейт); строка `SDL_REVISION` (`…-g92d11340`) не читается как происхождение (З1).
- Запуск (форма F10e/FS3c): внутри замка тега копия ставится на место `kyty_emulator.exe` папки эмулятора, sha проверяется после установки; в ловушке
  EXIT установленный **`540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1`** (FS3) возвращается из закреплённой копии
  `C:/kyty/f287/bin/kyty_emulator_540c035a.exe` и сверяется по sha. Возврат не удался — `C:/kyty/f287/fs4c/RETURN_FAILED`, замок остаётся. Установленный до
  тега не `540c035a` — тег не начинается (до замка). Установка FS4 — только FS4d (лид), не это звено.

## 2. Форма холода, тёплая форма и манифест кэшей (п. 378(г)(3), З2 п. 383(в))

- **Холод (`fs4_r0`, `fs4_r0r`, `fs4_r1`, `fs4_hb`) — удаление живого каталога варианта** (форма F10e §2 без изменений): при умолчаниях кэш трансляции
  живёт в `_ShaderCache/PPSA21564/variant_fixb26_fixb1b/` (`3d0e46da:src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp:570`, якорь
  «m_directory = std::filesystem::path("_ShaderCache") / title_id;»); внутри замка, после копии кэшей и до установки бинаря, `go_fs4c.sh` удаляет каталог
  целиком (модули и `pipelines.bin`) и пишет `runs/<тег>/cold.txt` («cold form: … absent at <UTC>»); каталог есть после удаления — тег не начинается.
  Precache по умолчанию на пустом каталоге ничего не воспроизводит — строка `PipelinePrecache: no <путь>\pipelines.bin yet`
  (`3d0e46da:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:6503`). **З2:** каждый холодный тег удаляет каталог сам, а кэши предыдущего тега
  возвращены его ловушкой EXIT (манифест EQUAL), поэтому `fs4_r0` идёт на новой трансляции при любом порядке тегов; порядок §3 ставит его первым.
- **Тёплая форма (`fs4_w`, `fs4_v`):** каталог варианта не трогается; есть `variant_fixb26_fixb1b/pipelines.bin` — иначе тег не начинается; `cold.txt` —
  «warm form: … present at <UTC>; files N; pipelines.bin B bytes». Тёплый кэш — кэш установленного `540c035a` (модули подписи `56189185`, общей у FS3 и
  FS4, п. 383(а)); модули, оттранслированные FS4 в холодных тегах, в него не попадают (возврат кэшей).
- **Манифест** (`manifest_fs4c.py` = `manifest_f10e.py` байт в байт): до копии — `runs/<тег>/manifest_before.tsv` (метка, путь, размер, sha256 каждого файла
  `_ShaderCache`, `_PipelineCache`, `_SaveData` и GLCache драйвера), после возврата — `manifest_after.tsv` и `manifest_cmp.txt`. **Строка печати:
  `manifest cmp EQUAL` — кэши после тега равны кэшам до тега побайтно.** Неравенство — `RETURN_FAILED`, замок остаётся, вопрос лиду. Копия и возврат —
  `cp -a` в `runs/<тег>/before_*`, после — удаление живого и перенос копии на место (во всех тегах, и тёплых).

## 3. Формы тегов (п. 378(г)(3); каждый тег — свой замок; очередь замка P > F > S, п. 322(г))

Общее: `KYTY_GPU_CLOCK_PIN=1`; `KYTY_GAME_PATCH`, `KYTY_GPU_CHECKPOINTS`, `KYTY_FIX_*` и прочие `KYTY_*` не передаются, кроме названного (окружение
`run_fs4c.py`/`enter_scene.py` строится из позиционных пар, `go_fs4c.sh` снимает `KYTY_*` и `VK_LAYER_*` до вызова); **`KYTY_FIX_SVAL` — только в `fs4_r0`
(`=0`)**; вход без ввода.

| тег | форма | командная строка (внутри `go_fs4c.sh <тег>`) |
|---|---|---|
| `fs4_r0` | R0 F10e, холод, `KYTY_FIX_SVAL=0` | `python run_fs4c.py runs/fs4_r0 300 --sval "KYTY_GUEST_ARGS=-lvl underwater_aerial_garden" KYTY_FIX_SVAL=0 KYTY_FRAME_TRACE=lite KYTY_GPU_CLOCK_PIN=1` — 300 с от запуска, `--shader-validation true`, без видео, без валидации Vulkan; конец процесса до 300 с пишется `run.json` (`how` = `exit rc <n>`, `exit_s`) |
| `fs4_r1` | R1 F10e без `KYTY_FIX_SVAL`, холод | `python enter_scene.py fs4_r1 --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file gates_default.txt --pred <печать> --rec --hold 330 --emu-arg=--shader-validation --emu-arg=true KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` — видео `rec_fs4_r1.mp4` |
| `fs4_hb` | R1 на `hoover_beach`, холод (справка) | то же, `--level hoover_beach`, видео `rec_fs4_hb.mp4` |
| `fs4_w` | W Sky Garden п. 295(б), тёплый | `python enter_scene.py fs4_w --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 600 --no-install --require-idle --gates-file gates_default.txt --pred <печать> --emu-arg=--vulkan-validation --emu-arg=true --hold 310 VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` = `fs3_w` FS3c: харнессная `--shader-validation false`, без `VK_LAYER_MESSAGE_ID_FILTER`, precache по умолчанию, без видео |
| `fs4_v` | V Sky Garden `SCENE_OK`, тёплый | `python enter_scene.py fs4_v --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file gates_default.txt --pred <печать> --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` = `fs3_v` FS3c, видео `rec_fs4_v.mp4` |

`enter_scene.py` ставит свои аргументы с `--shader-validation false`, `--emu-arg` идут после них; разбор `3d0e46da:src/main.cpp:273` (якорь
«} else if (arg == "--shader-validation") {») присваивает значение каждому вхождению — действует последнее (`true`). Строка `FixSval: mode=… ubo_std_layout=…`
печатается конструктором `PipelineCache` при любом `--shader-validation` (`3d0e46da:…/pipelineCache.cpp:4670`), а при `false` проверка не вызывается
(`…/pipelineCache.cpp:1357`, якорь «if (!Config::ShaderValidationEnabled()) {»; строк `FixSvalStat:` в W/V нет — справка).

**Порядок:** `fs4_r0`, `fs4_r1`, `fs4_hb`, `fs4_w`, `fs4_v`. Вызов — `bash C:/kyty/f287/fs4c/launch_fs4c.sh <тег>` (только запуск), ожидание —
`bash C:/kyty/f287/fs4c/wait_fs4c.sh <тег>` отдельными командами (≤ 540 с каждая) до строки `rc=`; разбор — `bash C:/kyty/f287/fs4c/post_fs4c.sh <тег>`
вне замка. **Одна попытка на тег**; провал члена — данные, серия идёт дальше, кроме R0: `fs4_r0` без отказа (строка «R0: defect reproduced» — NO) —
один повтор `fs4_r0r` той же формы (п. 378(г)(3)); второй без отказа — стоп серии (`fs4_r1`… не вызываются) и вопрос лиду. Отказ шлюза до старта
эмулятора (BUSY, замок, `--require-idle`, отказ `enter_scene.py` до запуска) — не попытка, тег вызывается снова. Помеха прогона (строка `Window <id>
minimized` или `Recovering Vulkan swapchain`) — тег не читается как исход, повтор — пунктом лида. Перед каждым вызовом тега — проверка API звеньев трека P
(`HPP-464` и идущие звенья прогонов) строкой `times.txt`; замок занят — ждать, ничего не писать.

## 4. Строки ридера (`fs4c_read.py`, по тегу; вердикта ридер не печатает)

| член | определение | теги |
|---|---|---|
| бинарь | `installed_sha.txt` = `31cbfee8…` | все |
| ревизия (справка) | каждая строка лога/stdout с `Fork build arigandores/KytyPS5 ` или `, git = `: YES — ≥ 1 такая и все называют `3d0e46d`; NO — одна называет другое; NOT_PRESENT — нет ни одной | все |
| холод | `cold.txt` говорит `absent` **и** строка `Shader translation cache: …variant_fixb26_fixb1b` **и** первая строка `PipelinePrecache:` — `PipelinePrecache: no … yet` | r0, r1, hb |
| тёплая форма | `cold.txt` говорит `warm form` и `present` **и** та же строка кэша трансляции **и** первая строка `PipelinePrecache:` — не `PipelinePrecache: no …` | w, v |
| `FixSval` | ≥ 1 строки `FixSval: mode=M ubo_std_layout=1`, все с M тега (`fs4_r0` — 0, прочие — 1: умолчание FS4), первая — до первой строки с `GuestOut` | все |
| `SPIR-V validation failed` | строки лога и stdout эмулятора с `SPIR-V validation failed` и различные хэши `hash=0x…` | все (гейт r0, r1; справка hb, w) |
| конец процесса | r0 — `run.json` `how` начинается с `exit rc` (до 300 с), печатаются `rc`, `exit_s`; прочие — попытка `enter_scene` `outcome` = `exited` или `hold_exit` не null | все |
| R0 воспроизведён | ≥ 1 строки `SPIR-V validation failed` **и** конец процесса до 300 с; иначе — «в игре не воспроизведён» (повтор `fs4_r0r`, §3) | r0 |
| `FixSvalStat` при `=0` | 0 строк (справка) | r0 |
| `validated ≥ 151` | `validated` последней строки `FixSvalStat: validated=N rejected=R` — число ВСЕХ проверок `ValidateShaderSpirv` (все стадии); N ≥ 151 — YES, N < 151 — NO; нет строки — `NOT_DETERMINED` («не определено», повтор пунктом лида) | r1 (гейт), hb (справка) |
| маркеры смерти | `Unhandled exception:`, `--- Fatal Error ---`, `--- Error ---`, `GpuHangAbort:`, `ErrorDeviceLost` в логе и stdout | r1, v (гейт); hb, w, r0 (справка) |
| вход, удержание | первая `GuestOut: Level has started: <уровень тега>`; первый кадр сцены — первая строка `FrameTrace` после неё с `draws` ≥ 100; удержание — сумма `dt_us` после него (до смены сцены) ≥ 300 с | r1, hb, w, v |
| кадры ≥ 1 с | строки `FrameTrace` с `dt_us` ≥ 1 000 000 после первого кадра сцены (до смены сцены): 0 — YES (нет входа — NO) | v (гейт); прочие (справка, число) |
| видео | записей индекса `rec_<тег>.mp4.idx` ≥ 3 000; `s51_vidglitch.py <rec> 4 6` — строка `one-frame glitches: 0`; лист лида `sheet142.py` (строка `sheet: `) | r1, v (гейт); hb (справка) |
| W | `[Vulkan][E]` = 0; положительный контроль слоя — строк `[Vulkan][W]` > 0; `DualSrcBlend: supported=1 enabled=1` до первой строки с `GuestOut`; строки `last time reporting it` — справка | w |
| манифест | первая строка `manifest_cmp.txt` — `manifest cmp EQUAL` | все |
| событие окна | нет `Window <id> minimized` и `Recovering Vulkan swapchain` (иначе тег не читается как исход) | все |

Листы для лида: `runs/fs4_r1/sheet_fs4_r1.png` рядом с `C:/kyty/f287/f10e/runs/f10e_r1/sheet_f10e_r1.png`; `runs/fs4_v/sheet_fs4_v.png` рядом с
`C:/kyty/f287/fs3/fs3c/runs/fs3_v/sheet_fs3_v.png`; `runs/fs4_hb/sheet_fs4_hb.png` рядом с `C:/kyty/f287/fs3/fs3c/runs/fs3_hb/sheet_fs3_hb.png` (справка).
Решение по листам — лид (FS4d).

Ридер — `fs4c_read.py` (sha256 §8); фикстуры `test_fs4c_read.py` — каждый член и край (151/150/нет строки, последняя строка решает, 300 с − 1 мкс, 3 000/2 999,
`FixSval` до/после `GuestOut` и режим по виду тега, члены холода и тёплой формы, кадр ровно 1 с / 999 999 мкс, кадр до первого кадра сцены и после смены
сцены, вход другого уровня, манифест EQUAL/DIFFER/нет, конец процесса по виду тега, ревизия YES/NO/NOT_PRESENT не гейт, R0 на тёплом каталоге — холод NO
(З2), вывод в строгий cp1250 без `PYTHONIOENCODING`); вывод `test_fs4c_read.out.txt` — первая строка `suite … target …`, последняя `ALL OK`. Мутантов нет —
форма звеньев прогонов трека F (FS3c, F10e: ридер + фикстуры).

## 5. Таблица членов п. 378(г)(3) (заполняется после тегов, вне печати)

Члены — строками «член: YES/NO/NOT_DETERMINED» с числами, sha256 логов и видео; **без вердикта** (приёмка и установка — лид, FS4d `HPP-473`). Логи и
видео — `C:/kyty/f287/fs4c/` (`runs/fs4_r0/log.txt`, `log_<тег>.txt`, `rec_<тег>.mp4`), в git — `docs/track-f/fs4c/` (харнесс, строки ридера, листы JPEG);
события — `C:/kyty/f287/times.txt` (UTC), замки — `C:/kyty/f287/fs4c/lock.log`.

**Заполнено 2026-10-03 после пятого тега (`fs4_v`, замок снят 15:20:47Z).** Ридер и харнесс после печати не менялись: sha256 файлов §8 на 15:2xZ совпали
(`go_fs4c.sh` `6ac93051…`, `fs4c_read.py` `b528e894…`, `post_fs4c.sh` `6fedd933…`, `enter_scene.py` `11dd0a63…`, `test_fs4c_read.out.txt` `d6bb54f0…`).
Каждый тег — одна попытка, свой замок (`lock.log`); отказы шлюза до старта эмулятора (BUSY) — не попытки: `fs4_w` ×2 (10:48:21Z, 11:51:01Z),
`fs4_v` ×1 (12:11:32Z) — их выводы в `C:/kyty/f287/fs4c/old/` и `runs/<тег>.busy_*`. Повторов `fs4_r0r` нет. Строки ридера — `fs4c/read_<тег>.txt`,
sha256 и размеры логов, stdout, видео и листов — `fs4c/artefacts_sha.txt`, листы для лида (JPEG) — `fs4c/sheets/`.

### 5.1. Члены п. 378(г)(3) по тегам

| тег (замок, UTC) | член | значение | строка ридера |
|---|---|---|---|
| `fs4_r0` (08:37:21Z–08:37:44Z) | бинарь `31cbfee8…`; ревизия в логе/stdout | `31cbfee8…`; `3d0e46d` (3 строки, справка) | YES; YES |
| | холод (каталог варианта удалён, `PipelinePrecache: no … yet`) | `absent` 08:37:25Z | YES |
| | `FixSval: mode=0 ubo_std_layout=1` до первой `GuestOut` | строка 79 (`GuestOut` — 11892) | YES |
| | `SPIR-V validation failed` | лог 2, stdout 1; хэш `c33dc20535a2cebf` (тот же PS, что в F10e R0) | YES (≥ 1) |
| | конец процесса до 300 с | `exit rc 321` на 12,1 с | YES |
| | **R0 воспроизведён** | отказ + конец процесса | **YES** |
| | `FixSvalStat` при `=0` (справка) | 0 строк | YES |
| | маркеры смерти (справка) | 2 `--- Error ---` (лог 55998, stdout 47 — текст выхода 321) | — |
| | манифест; событие окна | `manifest cmp EQUAL` (2 920 файлов, listsha `951942c4…`); нет | YES; YES |
| `fs4_r1` (10:24:40Z–10:30:57Z) | бинарь; ревизия | `31cbfee8…`; `3d0e46d` | YES; YES |
| | холод | `absent` 10:24:44Z | YES |
| | `FixSval: mode=1 ubo_std_layout=1` до первой `GuestOut` | строка 79 (`GuestOut` — 11893) | YES |
| | 0 `SPIR-V validation failed` | лог 0, stdout 0 | YES |
| | нет конца процесса | `outcome ok`, `hold_s` 330,1 | YES |
| | 0 маркеров смерти | 0 | YES |
| | `validated` ≥ 151 | последняя `FixSvalStat`: `validated=256 rejected=0` | YES |
| | вход; удержание ≥ 300 с | вход за 25,1 с; 334,9 с | YES; YES |
| | кадры ≥ 1 с (справка) | 0 (макс. `dt` 518 936 мкс) | — |
| | видео ≥ 3 000 кадров; 0 глитчей; лист | 10 176 записей; 0; `sheet_fs4_r1` (рядом с `sheet_f10e_r1`) | YES; YES; YES |
| | `AsyncPipelines: skipped draw` (справка, форма Б5 холодного входа) | 919 | — |
| | манифест; событие окна | EQUAL (2 920, `e86f7233…`); нет | YES; YES |
| `fs4_hb` справка (10:38:27Z–10:44:41Z) | бинарь; холод; `FixSval mode=1` до `GuestOut` | `31cbfee8…`; `absent` 10:38:32Z; строка 79 | YES; YES; YES |
| | отказы и хэши | 0, хэшей нет | YES |
| | `validated` | `validated=256 rejected=0` | YES |
| | смерти; конец процесса | 0; нет | YES; YES |
| | вход; удержание; кадры ≥ 1 с | 22,1 с; 335,9 с; 0 (макс. 435 144 мкс) | YES; YES; — |
| | видео; глитчи; лист | 19 966 записей; 0; `sheet_fs4_hb` (рядом с `sheet_fs3_hb`) | YES; YES; YES |
| | `skipped draw` (справка) | 173 | — |
| | манифест; событие окна | EQUAL (2 920, `e86f7233…`); 1 `lost keyboard focus` (не `minimized`, `Recovering` 0) | YES; YES |
| `fs4_w` (11:56:44Z–12:02:51Z) | бинарь; ревизия | `31cbfee8…`; `3d0e46d` | YES; YES |
| | тёплая форма (каталог есть, `PipelinePrecache: 1357 recipes … complete`) | `present` 11:56:50Z, 616 файлов | YES |
| | `FixSval: mode=1 ubo_std_layout=1` до первой `GuestOut` | строка 83 (`GuestOut` — 12405) | YES |
| | вход; удержание ≥ 300 с | 28,8 с; 324,4 с | YES; YES |
| | 0 `[Vulkan][E]` | 0 | YES |
| | `[Vulkan][W]` > 0 (положительный контроль слоя) | 899 186; строк `last time reporting` 0 | YES |
| | `DualSrcBlend: supported=1 enabled=1` до первой `GuestOut` | строка 76 | YES |
| | отказы, конец процесса, смерти (справка) | 0; нет; 0 | YES |
| | кадры ≥ 1 с (справка) | 0 (макс. 400 803 мкс) | — |
| | манифест; событие окна | EQUAL (2 920, `e86f7233…`); 1 `lost keyboard focus` (не `minimized`, `Recovering` 0) | YES; YES |
| `fs4_v` (15:14:28Z–15:20:47Z) | бинарь; ревизия | `31cbfee8…`; `3d0e46d` | YES; YES |
| | тёплая форма | `present` 15:14:35Z, 616 файлов, `PipelinePrecache: 1357 recipes … complete` | YES |
| | `FixSval: mode=1 ubo_std_layout=1` до первой `GuestOut` | строка 79 (`GuestOut` — 12404) | YES |
| | вход; удержание ≥ 300 с | 19,9 с; 334,4 с | YES; YES |
| | 0 смертей; нет конца процесса | 0; `hold_s` 330,1 | YES; YES |
| | 0 кадров ≥ 1 с | 0 (макс. 201 571 мкс) | YES |
| | видео ≥ 3 000 кадров; 0 глитчей; лист | 10 287 записей; 0; `sheet_fs4_v` (рядом с `sheet_fs3_v`) | YES; YES; YES |
| | `skipped draw` (справка) | 0 | — |
| | манифест; событие окна | EQUAL (2 922, `cffd41b3…`); нет | YES; YES |

Справка к манифесту: число файлов кэшей между `fs4_w` (12:02:51Z) и `fs4_v` (15:14:28Z) выросло 2 920 → 2 922 вне тегов FS4c (между ними шли теги
F11f под своим замком); сравнение «до = после» — внутри каждого тега. Установленный `540c035a…` возвращён и сверен по sha256 после каждого тега
(строка `installed binary returned` в `go_<тег>.out.txt`).

### 5.2. sha256 логов и видео

| тег | лог | stdout | видео | лист |
|---|---|---|---|---|
| `fs4_r0` | `e7d8cb848b76d3a4ed4a3e153e3e3999c91b6a3e298aabbb14605f97a6171a3c` | `b11cd59ece35acd71680660d39956d9deead6cf255a2dd991d04533896cce516` | — | — |
| `fs4_r1` | `45bd88b9051253f75df86414f8f3f1fb3ac4193868aa5bb86e92d010483ad7ed` | `f8355e34e744624bd06407b62a4cf91189c437b81249d6324011952946b90fe6` | `83e28dc1df5caa5187d93f087fba23805027280be7fc8b0ca6065a096a193640` | `596b8500733f845fd58e04ceae85dfcd3118a61dbae25bec37a43f4322bf1f28` |
| `fs4_hb` | `2081884a088bdb6704a16644d90a8932611829400d3f10101680302792dad0ac` | `373710459ec12a8a116e34f9783c8e9d4d8f62509367a84f7d947adc25f29a0a` | `3bcbb817c418de9a3b126e92a69349d270982a977b1b54ae4d9f41d2acca18ee` | `9e31585f81904bb706a3e9d90659ec044b06ad536e456738ebe510cf2db26f6c` |
| `fs4_w` | `5b4a0a0d753d9a720e6cb000ab16589d1d9e843196eab10c36c966b1bfafce20` | `06ed864a9f69e7ddf4a1e28e3a8696708729f857c26398195ba3c248676a7002` | — | — |
| `fs4_v` | `7ec2b2de288dd671635dc38be03c3acc6687b3d5603724c41fbe4e5b35e413f8` | `19f57557a9cbf7f179a4b4add22c23ac37795b1b58b7004d837e247aa41d8dff` | `0d6e55df87584814c42aacb2ff2a4e8ae755d8ee60658a896f2a0600bf6efae2` | `041288b7c20d3fb13334d3a73b2e8e9427bed85f2c75295e4125ac0e6b920bc1` |

### 5.3. Ход серии (справка)

- Очередь замка P > F > S: между `fs4_r0` и `fs4_r1` шла серия P43 (`HPP-464`, окно 08:38:26Z–10:15:06Z).
- **Нарушение общего правила 27 (исполнитель):** пробы `procload.py` в 11:43:03Z, 11:44:32Z, 11:46:01Z шли под замком F11f `d11_ef`
  (только чтение загрузки, файлов не писали; строка `times.txt` 11:47:39Z); с 12:12Z замок проверялся перед каждой пробой.
- `fs4_v` ждал шлюза 12:11Z–15:09Z: BUSY от приложения пользователя `<app>` (не снималось); после его закрытия — 15:04Z–15:08Z — процесс сервера
  платформы (0,505–0,889 CPU с/с при пороге 0,50, предок оболочки агента, не снимался); `clean` 15:09:35Z–15:11:33Z (×3), вызов 15:12Z.

Вердикта звено не печатает: приёмка, решение по листам и установка — лид (FS4d `HPP-473`).

## 6. Харнесс (`C:/kyty/f287/fs4c/`, в git — `docs/track-f/fs4c/`)

| файл | что |
|---|---|
| `go_fs4c.sh` | один тег = один замок; порт `go_f10e.sh`: копия FS4 вместо F10c, теги §3, холод §2 в r0/r0r/r1/hb, тёплая форма в w/v |
| `launch_fs4c.sh`, `wait_fs4c.sh` | только запуск отсоединённого вызова тега и ожидание ≤ 540 с отдельными командами («Процесс» 2 п. 324(и)) |
| `post_fs4c.sh` | разбор тега вне замка: r1/hb/v — `s51_vidglitch.py`, лист `sheet142.py`; затем строки ридера |
| `run_fs4c.py`, `manifest_fs4c.py` | `run_f10e.py`, `manifest_f10e.py` F10e байт в байт (sha256 = F10e §8) |
| `fs4c_read.py`, `test_fs4c_read.py`, `test_fs4c_read.out.txt` | ридер §4, фикстуры и их вывод |
| `enter_scene.py` | файл F10e, перенесён только `ROOT` (`f287/f10e` → `f287/fs4c`) и строка 1 |
| `idle142.py`, `procload.py`, `gates_default.txt`, `sheet142.py`, `run_safety99.py`, `launch_run.py` | файлы F10e байт в байт; `launch_run.py` — только локально (его текст называет постороннее приложение, общее правило 28), sha256 — §8 |

## 7. Не заявляется

Что пользователь запускает игру с проверкой шейдеров; что 151 — все такие PS игры; что `validated` — число PS класса S151; что встроенная проверка не
отвергнет PS другого класса на других уровнях; что SPIR-V корректен для устройства и картинка верна; что FS4 работает в игре до тегов; что форма холода §2 —
единственная форма, в которой Ф16 проявляется; ни одно число — не выигрыш; 60 FPS не обещаются; установленный `540c035a` этим звеном не меняется.

## 8. sha256 файлов печати (до первого тега)

| файл | sha256 |
|---|---|
| `go_fs4c.sh` | `6ac93051ffff5ed743614021f3dffd31511df8b6c26ed696336cf831c4fae43d` |
| `launch_fs4c.sh` | `c17a676ac61e56c4e5c741f42695a49d89b5a72a14811736e1773695870be514` |
| `wait_fs4c.sh` | `bccabc0d992c9891bf388a022573606072efd5223466744af50528a1591c7902` |
| `post_fs4c.sh` | `6fedd93340797b31c6b70ff8a70e48ad22f2268a5040d9550e860cf7c058b04e` |
| `run_fs4c.py` | `5be9432690560d0b52d2f1378549f10f27e4d472dcd86f12f0e29f974afa2633` |
| `manifest_fs4c.py` | `a7096fd47f70419a5ed8d541778294f3032ca2c88e7b4b2e946f3d99651182bb` |
| `fs4c_read.py` | `b528e8942634e97a04104573b73f5d16088450f7188c53765d4efca3a2aa1dc5` |
| `test_fs4c_read.py` | `591b16ca35c241f39fc064c2bf67e3c84c67650b18987de042e9898d84cad553` |
| `test_fs4c_read.out.txt` | `d6bb54f0979897a100b69979ce05f02ff7401c7d06e3b72286f6e0ef4b1f484a` |
| `enter_scene.py` | `11dd0a633d7bbb2574d94d66b7bc3164ff624dd6653aeefa15e8006792d23710` |
| `idle142.py` | `c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96` |
| `procload.py` | `d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0` |
| `gates_default.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `sheet142.py` | `c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d` |
| `run_safety99.py` | `77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638` |
| `launch_run.py` | `c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21` |
| `mk_seal_fs4c.py` | `adbc7a750de1cc42bd5f714141235f65003f484ef13dec74c4a2a3fb0a6e3db5` |
| `C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe` | `31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5` |
| `C:/kyty/f287/bin/kyty_emulator_540c035a.exe` | `540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1` |
| `C:/kyty/scripts/s51_vidglitch.py` | `6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c` |
