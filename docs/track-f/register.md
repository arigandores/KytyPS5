# Трек F, звено F0 — реестр дефектов по логам (Lever Researcher, `HPP-289`)

Решение и форма — `beb36ab0:docs/ROADMAP.md:12074` «Трек F» (п. 228 прочитан целиком до первого действия). Цель программы — корректность игры на возможно большем числе сцен
(п. 214–215); скорость — не цель и не гейт. Установленная сборка — `9235a7ac…`. Игры, сборок и правок кода в звене нет; замок
`C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` отсутствовали перед каждым проходом; логи читались только python в двоичном режиме, блоками.
Код читался по `26457dd7` (HEAD `main` на время звена); каждая ссылка `<коммит>:<путь>:<строка>` найдена скриптом по якорю, контроль +1 — `NOT OK`
(`C:/kyty/f287/f0/refs_f0_map.txt`). Документ собран `mk_register.py`; файлы и выводы — `C:/kyty/f287/f0/`, время — `C:/kyty/f287/times.txt`.
Константы п. 215, 217, 218, 228 не менялись. Документ — предложение; решения — у лида.

## 0. Главное

1. **Б26 по логам — наблюдение, а не исполняемый путь [c]** (независимо подтверждает `455b3a25:docs/track-f/f1-review.md:37` «RC1. Без сцены-свидетеля», `455b3a25:docs/track-f/f1-review.md:50` «RC2. Критерий (е)(3)» и `455b3a25:docs/ROADMAP.md:12495` «RC-L1»). 101 строка `opcode is not implemented` в каждом логе — это строки потока
   спекулятивной трансляции CS (`CsPretranslate: skipped`), который ставит в очередь каждый зарегистрированный игрой CS и перехватывает фатал.
   Ни один из 101 хэша ни в одном из 12 логов с. 142 не запрошен обычным путём (0 из 18 строк `CsPretranslate: miss`/`hit` этих логов), а на обычном пути тот же
   опкод — `EXIT` и смерть процесса (маркеров смерти 0 из 12). Следствие для F1: критерий «0 строк маркера на входе» проверяет поток спекуляции;
   сцены, которая диспатчит такой шейдер, в логах нет. При появлении такой сцены класс строки — K1, не «картинка».
2. **Атрибуция строки Б33 (K3 на удержании холодного входа, ведёт трек S) — механизм назван по коду:** сохранение кэша пайплайнов драйвера (≈ 90 МБ, 80–93 мс) раз в 20 с под
   `m_mutex` при новых пайплайнах; 5 из 6 сохранений в середине уровня лежат в кадре 115–166 мс — это все 4 кадра K3 удержания переписи с. 142.
3. **Б1б имеет видимое по времени кадра следствие [c]:** каждое срабатывание ограничителя BVH на `9235a7ac` — кадр 266–317 мс, 6 подряд, на 2 из 10
   новых уровней. По букве п. 231(г)(3) класс остаётся K4; вариант исполнителя — K3 (вопрос В3).
4. **Б9 частично опровергнут:** `timestop_casino` вызывает 4 неразрешённых импорта `AudioPropagation` (≥ 1 024 вызова) — строка Б9а.
5. **Б3б и Б2 — одно событие с причинами в других строках:** на с. 142 все 23 ожиданий `PriorityStall:` > 50 мс после первого кадра сцены лежат в
   кадрах ≥ 100 мс; в интервале кадра Б2 (n 949–954) — одна строка `PriorityStall:` (5 из 5).
6. Маркеров смерти на с. 142 — 0 из 12; `[Vulkan][E]` — 0; на с. 128–141 маркеры смерти — 3 лога, все отнесены (`s1s128`, `s2s128` — `protceil=1`; `dds131` — Б4).

## 1. Объём свипа

| что | число [c] |
|---|---|
| файлов `log_*.txt` и `_kyty*.txt` под `C:/kyty` (`loglist_f0.tsv`) | 23 281 (324,9 ГБ) |
| из них в каталогах фикстур и мутантов (`fx_*`, `work_*`, `mut*`, `test_*`, `fixt*`) — не читались | 21 543 |
| прочитано потоком (`sweep_f0.py`, 3 прохода, 2 513 сегментов по 256 МБ) | 1 738 файлов, 288 015 732 915 байт, 5 006 003 490 строк |
| из них прямых детей `C:/kyty/s*/` и корня (счёт п. 228(б)) | 821 + 316 = 1 137 |
| уникальных по sha256 | 1 574 (дубликатов 164) |
| без номера / до с. 50 / с. 50–102 / с. 103–112 / с. 113–127 / с. 128–141 / с. 142 | 7 / 347 / 457 / 382 / 297 / 72 / 12 (сумма 1 574) |
| логов на сборках с. 128+ (с. 128–141 и с. 142) | 72 + 12 = 84 |
| различных нормализованных сигнатур (адреса и числа → `X`), `sig_f0.tsv` | 820; предел 4 000 сигнатур на лог не достигнут (0 строк сверх предела) |

Сессия лога — номер каталога `sNN`; для `s106_stage` — число из имени подкаталога; для корня — последний токен `_sNN` имени (7 логов без номера).
Сборка в логе не печатается: «с. 128+» значит «каталог сессии ≥ 128» — это сборки `rtskip=1` и инструменты поверх них, а не ровно `9235a7ac`;
ровно на `9235a7ac` — 12 логов с. 142 (sha256 сборки проверен харнессом, `C:/kyty/s142/FACTS.md:4`). Самопроверка сканера: посегментный разбор
`log_c142_02.txt` (сегменты 7 МБ) равен цельному (строк 887 497, сигнатур 112, событий 3 812), sha256 равен `sha256sum`. Кадры `c142_01`…`v142`
по моему разбору совпали со сводкой скорера `sc142` (первый кадр сцены, K2, K3 окна/удержания, максимум, число кадров — `ana_f0.out.txt` (7)).
Ключевые слова отбора строк чувствительны к регистру (`sweep_f0.py`, `KEY`); строка без этих слов в свип не попала — см. «Не заявляется».

## 2. Сигнатуры п. 228(б): число логов, сессии, сборки с. 128+, уровни, пример

Уникальные логи; «уровни» — имена из `GuestOut: Level has started:` с числом логов (до 6 самых частых, затем число остальных имён).

| сигнатура | логов | строк | первая / последняя сессия | логов с. 128+ (из 84) | из них с. 142 (из 12) | уровни | пример `файл:строка` | строка реестра |
|---|---|---|---|---|---|---|---|---|
| `--- Fatal Error ---` (маркер смерти п. 218(д)(2)) | 23 | 31 | 12 / 131 | 3 | 0 | `ps_logo` 11, `title_controller_ship` 11, `intro_next` 11, `worldmap` 10, `transition_next` 10, `underwater_aerial_garden` 3 | `C:/kyty/s131/log_dds131.txt:718962` (sha256 `17d350016adafeac…`) | Б4, Б18, Б23; до с. 103 — закрытые |
| `--- Error ---` (п. 218(д)(2)) | 181 | 184 | 8 / 102 | 0 | 0 | `ps_logo` 146, `title_controller_ship` 145, `intro_next` 137, `underwater_aerial_garden` 28, `worldmap` 6, `transition_next` 6 | `C:/kyty/s102/log_ckpt102.txt:241603` (sha256 `6e753ea8230ce003…`) | последняя с. 102; Б25 и закрытые |
| `Error: condition (…) is true in …` / `Assertion failed` | 11 | 11 | 45 / 131 | 1 | 0 | `underwater_aerial_garden` 1 | `C:/kyty/s131/log_dds131.txt:718963` (sha256 `17d350016adafeac…`) | Б4 (`fileSystem.cpp`), Б18 (`commandRecorder.cpp`) |
| `GpuHangAbort:` (п. 128(г)) | 31 | 34 | 52 / 113 | 0 | 0 | `underwater_aerial_garden` 25, `ps_logo` 3, `title_controller_ship` 3, `intro_next` 3, `worldmap` 3, `transition_next` 3 | `C:/kyty/s106_stage/shn113/fx/hang/log_shn113.txt:61014` (sha256 `4705d15867b632f8…`) | Б1а; после с. 102 — только фикстуры `fx/hang` |
| `ErrorDeviceLost` (п. 128(г)) | 13 | 21 | 12 / 128 | 2 | 0 | `ps_logo` 11, `title_controller_ship` 11, `intro_next` 11, `worldmap` 10, `transition_next` 10, `underwater_aerial_garden` 2 | `C:/kyty/s128/log_s2s128.txt:239628` (sha256 `b9988b60c4fdcc1e…`) | с. 128 — `protceil=1` (Б23); раньше — закрытые |
| `Unhandled host exception:` (п. 128(г)) | 13 | 13 | 8 / 59 | 0 | 0 | `ps_logo` 8, `title_controller_ship` 8, `intro_next` 7, `worldmap` 1, `transition_next` 1 | `C:/kyty/s59/log_sig1.txt:627200` (sha256 `6e7c5514f0a1cffa…`) | последняя с. 59 (Б25) |
| `There are too many objects/batches in this scene.` | 2 | 3 | 42 / 59 | 0 | 0 | `ps_logo` 2, `title_controller_ship` 2, `intro_next` 2 | `C:/kyty/s59/log_sig1.txt:627192` (sha256 `6e7c5514f0a1cffa…`) | Б25: 2 лога (с. 42 и с. 59) |
| `[Vulkan][E]` | 5 | 5 | 20 / 38 | 0 | 0 | `ps_logo` 5, `title_controller_ship` 5 | `C:/kyty/log_s14_s38_validate_wsi.txt:488840` (sha256 `e0ae3ca003a6821d…`) | последняя с. 38; закрыты |
| `[Vulkan][W]` (все формы; основная — запись в `out_mrt_N` без привязанной цели) | 32 | 4 971 625 | 38 / 142 | 8 | 1 | `ps_logo` 21, `title_controller_ship` 21, `intro_next` 18, `underwater_aerial_garden` 12, `worldmap` 1, `transition_next` 1 | `C:/kyty/s142/log_w142.txt:62` (sha256 `7f42a2d3e1a151a2…`) | Ф6 |
| `opcode is not implemented` SOP1 `0x21` | 846 | 78 296 | 14 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `ps_logo` 207, `title_controller_ship` 206, `intro_next` 205, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:10091` (sha256 `7f42a2d3e1a151a2…`) | Б26 |
| `opcode is not implemented` SOP1 `0x0c` | 736 | 736 | 14 / 142 | 83 | 12 | `underwater_aerial_garden` 553, `intro_next` 205, `ps_logo` 199, `title_controller_ship` 199, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:368891` (sha256 `7f42a2d3e1a151a2…`) | Б26 |
| `opcode is not implemented` VOPC `0xe3` | 733 | 2 932 | 14 / 142 | 83 | 12 | `underwater_aerial_garden` 550, `intro_next` 205, `ps_logo` 199, `title_controller_ship` 199, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:370496` (sha256 `7f42a2d3e1a151a2…`) | Б26 |
| `opcode is not implemented` прочих семейств (VOP2, VOP1, VOP3, MIMG, SMEM, …) | 0 | 0 | — / — | 0 | 0 | — | — | Б7: 0 логов |
| `CsPretranslate: skipped … shader resource tracking` | 818 | 24 164 | 14 / 142 | 83 | 12 | `underwater_aerial_garden` 628, `ps_logo` 206, `title_controller_ship` 206, `intro_next` 205, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:333119` (sha256 `7f42a2d3e1a151a2…`) | Ф3 |
| `CsPretranslate: skipped … speculative translation budget exceeded` | 843 | 3 322 | 14 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `ps_logo` 207, `title_controller_ship` 206, `intro_next` 205, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:234148` (sha256 `7f42a2d3e1a151a2…`) | Ф3 |
| `CsPretranslate CFG dispatcher fallback … failure=StructuredControlFlow` | 843 | 1 686 | 14 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `ps_logo` 207, `title_controller_ship` 206, `intro_next` 205, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:77286` (sha256 `7f42a2d3e1a151a2…`) | Ф3 |
| `=== Stubbed function` | 0 | 0 | — / — | 0 | 0 | — | — | Б9: 0 логов — маркер ред. 2 не срабатывал ни разу |
| `Unresolved import stub called` (любая библиотека) | 3 | 1 154 | 45 / 142 | 1 | 1 | `ps_logo` 1, `title_controller_ship` 1, `intro_next` 1, `worldmap` 1, `transition_next` 1, `timestop_casino` 1 | `C:/kyty/s142/log_c142_03.txt:239572` (sha256 `9aaa83b0c73e66b1…`) | Б9а (AudioPropagation, с. 142); Json2 — с. 45 |
| `Relocate: unresolved PLT import patched to stub` (все библиотеки) | 1 108 | 105 145 | 7 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `ps_logo` 432, `title_controller_ship` 430, `intro_next` 419, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:4536` (sha256 `7f42a2d3e1a151a2…`) | Б9 |
| `BvhLoopCapTrip:` | 24 | 135 | 103 / 142 | 2 | 2 | `underwater_aerial_garden` 22, `big_hand_pirate_island` 1, `voxel_world` 1 | `C:/kyty/s142/log_c142_09.txt:206646` (sha256 `eadf72b5b79ac096…`) | Б1б |
| `PriorityStall:` (ожидание > 50 мс) | 45 | 874 | 114 / 142 | 30 | 9 | `underwater_aerial_garden` 29, `intro_next` 5, `penguin_atlantis` 1, `rotating_level_day_and_night` 1, `time_stopper_ghost_world` 1, `bumper_enemy_snowy_canyon` 1 и ещё 7 | `C:/kyty/s142/log_w142.txt:226786` (sha256 `7f42a2d3e1a151a2…`) | Б3б |
| `AsyncPipelines: skipped draw` | 183 | 145 774 | 14 / 142 | 10 | 10 | `ps_logo` 155, `title_controller_ship` 154, `intro_next` 148, `worldmap` 27, `transition_next` 27, `underwater_aerial_garden` 27 и ещё 13 | `C:/kyty/s142/log_c142_10.txt:201006` (sha256 `d78e0342fa2186f4…`) | Б5 |
| `MainTaskLate:` | 153 | 169 | 114 / 142 | 84 | 12 | `underwater_aerial_garden` 124, `intro_next` 12, `time_stopper_ghost_world` 3, `penguin_atlantis` 2, `rotating_level_day_and_night` 2, `bumper_enemy_snowy_canyon` 1 и ещё 9 | `C:/kyty/s142/log_w142.txt:4308` (sha256 `7f42a2d3e1a151a2…`) | Б24 (≥ 1 с — 5 логов с. 113+, см. §3.6) |
| `CsStall: kind=wait` | 404 | 424 | 110 / 142 | 4 | 4 | `underwater_aerial_garden` 16, `penguin_atlantis` 1, `bumper_enemy_snowy_canyon` 1, `mini_giants_garden` 1, `sponge_dirty_bath` 1, `hoover_beach` 1 | `C:/kyty/s142/log_c142_07.txt:225605` (sha256 `5e1bd731e2e5d345…`) | Б5 (ожидание трансляции CS) |
| `KernelRead: direct read failed … reading through a host buffer` | 207 | 2 812 | 14 / 142 | 1 | 1 | `ps_logo` 206, `title_controller_ship` 206, `intro_next` 204, `worldmap` 69, `transition_next` 69, `underwater_aerial_garden` 49 и ещё 1 | `C:/kyty/s142/log_c142_05.txt:414100` (sha256 `9ea02549b36c0100…`) | Ф4 |
| `file not found` (`KernelStat`) | 1 106 | 13 937 359 | 7 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `ps_logo` 432, `title_controller_ship` 430, `intro_next` 419, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:29877` (sha256 `7f42a2d3e1a151a2…`) | Ф7 |
| `warning: size_bytes / base is not 256-byte aligned` | 1 107 | 58 649 | 7 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `ps_logo` 432, `title_controller_ship` 430, `intro_next` 419, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:15263` (sha256 `7f42a2d3e1a151a2…`) | Ф7 |
| `warning: ignoring indirect uc reg GE_STEREO_CNTL` | 1 106 | 17 656 | 7 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `ps_logo` 432, `title_controller_ship` 430, `intro_next` 419, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:16630` (sha256 `7f42a2d3e1a151a2…`) | Ф5 |
| `RenderTarget: temporary: ignoring PS5 color metadata … dcc=true` | 1 103 | 1 103 | 7 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `ps_logo` 432, `title_controller_ship` 430, `intro_next` 419, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:16898` (sha256 `7f42a2d3e1a151a2…`) | Ф5 |
| `RenderTarget: temporary: ignoring PS5 metadata addresses` | 1 103 | 1 103 | 7 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `ps_logo` 432, `title_controller_ship` 430, `intro_next` 419, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:16899` (sha256 `7f42a2d3e1a151a2…`) | Ф5 |
| `RenderTarget: temporary: ignoring PS5 color round mode` | 1 102 | 1 102 | 7 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `ps_logo` 432, `title_controller_ship` 430, `intro_next` 419, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:17057` (sha256 `7f42a2d3e1a151a2…`) | Ф5 |
| `DepthTarget: ignoring enabled depth/stencil state without a bound attachment` | 1 099 | 1 099 | 7 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `ps_logo` 432, `title_controller_ship` 430, `intro_next` 419, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:227266` (sha256 `7f42a2d3e1a151a2…`) | Ф5 |
| `GraphicsRenderDispatchDirect: skipping zero-sized dispatch` | 1 067 | 33 972 | 7 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `intro_next` 419, `ps_logo` 403, `title_controller_ship` 403, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:182111` (sha256 `7f42a2d3e1a151a2…`) | Ф5 |
| `Format vk::Format::… cannot be used as texture` | 1 115 | 2 230 | 7 / 142 | 84 | 12 | `underwater_aerial_garden` 652, `ps_logo` 432, `title_controller_ship` 430, `intro_next` 419, `worldmap` 69, `transition_next` 69 и ещё 13 | `C:/kyty/s142/log_w142.txt:66` (sha256 `7f42a2d3e1a151a2…`) | Ф7 (свойство хоста) |
| `LossWin: overflow kind=open` | 1 | 1 | 131 / 131 | 1 | 0 | `underwater_aerial_garden` 1 | `C:/kyty/s131/log_lw6s131.txt:243527` (sha256 `81a20cb232a7f1dc…`) | инструмент `armcopy` (с. 131), не умолчание |
| `TextureCache: failed to map reusable download buffer` | 2 | 2 | 96 / 96 | 0 | 0 | `underwater_aerial_garden` 2 | `C:/kyty/s96/log_bf96a_warmup.txt:438079` (sha256 `7b2bcf1f62d6af80…`) | инструмент `bf96a` (с. 96) |
| `AudioOut: SDL_QueueAudio failed: Invalid audio device ID` | 20 | 8 186 901 | 45 / 105 | 0 | 0 | `underwater_aerial_garden` 18, `ps_logo` 12, `title_controller_ship` 12, `intro_next` 12, `worldmap` 11, `transition_next` 11 | `C:/kyty/s105/log_abb105.txt:2871038` (sha256 `1c903fa919158685…`) | Ф8; последняя с. 105 |
| `Controller: disconnect of unknown id … ignored` | 2 | 2 | 14 / 116 | 0 | 0 | `ps_logo` 1, `title_controller_ship` 1, `intro_next` 1, `underwater_aerial_garden` 1 | `C:/kyty/s116/log_obs116.txt:4490` (sha256 `3cc2745a277060e1…`) | Б24 (рядом) |
| `Skipping unsupported GE shader draw` | 245 | 7 810 | 7 / 32 | 0 | 0 | `ps_logo` 214, `title_controller_ship` 213, `intro_next` 204 | `C:/kyty/log_s14_s32_wave32.txt:17261` (sha256 `e353532047488210…`) | закрыто с. 47; последняя с. 32 |
| `warning: executing wave64 compute shader` | 467 | 467 | 7 / 67 | 0 | 0 | `ps_logo` 428, `title_controller_ship` 426, `intro_next` 400, `worldmap` 69, `transition_next` 69, `underwater_aerial_garden` 49 | `C:/kyty/s67/log_old64a.txt:16449` (sha256 `508629f766262f8f…`) | последняя с. 67 |
| `unsupported_reason=` / `failure=StructuredControlFlow` (CFG) | 76 | 182 | 9 / 59 | 0 | 0 | `ps_logo` 75, `title_controller_ship` 75, `intro_next` 75, `worldmap` 11, `transition_next` 11, `underwater_aerial_garden` 5 | `C:/kyty/s59/log_sky59.txt:1557136` (sha256 `0d883b6a3b15351c…`) | последняя с. 59 |
| `vkQueuePresentKHR returned … eErrorOutOfDateKHR` | 5 | 10 | 14 / 49 | 0 | 0 | `ps_logo` 5, `title_controller_ship` 5, `intro_next` 5, `worldmap` 2, `transition_next` 2, `underwater_aerial_garden` 1 | `C:/kyty/s49/log_nv.txt:3661910` (sha256 `16eb79fc9ba3244e…`) | последняя с. 49 |
| `shader IR validation failed` | 2 | 2 | 30 / 30 | 0 | 0 | `ps_logo` 2, `title_controller_ship` 2, `intro_next` 2 | `C:/kyty/log_s14_s30_d.txt:858318837` (sha256 `9afa76a17d7b6855…`) | с. 30 |

Строк таблицы — 43. Маркеры `hold_exit` и `WARNING: the game ENDED inside the hold` пишет харнесс (`enter_scene.py`), в `log_*.txt` их нет (0 логов) —
для с. 142 они читаны скорером из json попыток: 0 из 12 (`C:/kyty/s142/FACTS.md:219` «маркеров смерти 0»).
Профили `opcode is not implemented` по логам: SOP1 0x0c×1/SOP1 0x21×96/VOPC 0xe3×4 — 733; SOP1 0x21×88 — 75; SOP1 0x21×20 — 25; SOP1 0x21×72 — 7; SOP1 0x0c×1/SOP1 0x21×96 — 3; SOP1 0x21×12 — 3 (сумма 846).
Уровни с профилем Б26 (19 имён): `big_hand_pirate_island`, `bumper_enemy_snowy_canyon`, `enemy_gorilla`, `hoover_beach`, `ice_iceberg`, `intro_next`, `mini_giants_garden`, `penguin_atlantis`, `ps_logo`, `rotating_level_day_and_night`, `sponge_dirty_bath`, `time_stopper_ghost_world`, `timestop_casino`, `title_controller_ship`, `transition_next`, `underwater_aerial_garden`, `volcano_mountain`, `voxel_world`, `worldmap`.

## 3. 12 логов с. 142 (`9235a7ac`)

| тег | уровень | sha256 (16) | первый кадр сцены n | K2 | K3 окно / удерж. | max `dt` окно / удерж., мкс | `skipped draw` строк / кадров | `PriorityStall:` > 50 мс окно / удерж. (в кадре ≥ 100 мс) | `BvhLoopCapTrip:` | сохранений кэша в середине уровня → кадр, мкс | прочее |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `c142_01` | `bumper_enemy_snowy_canyon` | `66b4ff7e0e50a8a4` | 203 | 0 | 2 / 0 | 816 566 / 50 020 | 225 / 3 | 1 / 0 (1 / 0) | 0 | — | — |
| `c142_02` | `big_hand_pirate_island` | `bb6655d3d30c0bc7` | 328 | 0 | 14 / 2 | 300 409 / 151 746 | 41 / 13 | 9 / 2 (9 / 2) | 6 | 93 мс → n 795: 165 920; 92 мс → n 1358: 149 651; 86 мс → n 2557: 151 746 | — |
| `c142_03` | `timestop_casino` | `9aaa83b0c73e66b1` | 263 | 0 | 3 / 1 | 432 339 / 115 028 | 2203 / 68 | 2 / 0 (2 / 0) | 0 | 87 мс → n 1042: 115 028; 80 мс → n 2626: 93 171 | `Unresolved import stub called` ×1024 |
| `c142_04` | `mini_giants_garden` | `bd5f547706caad1d` | 260 | 0 | 0 / 0 | 33 664 / 31 838 | 37 / 12 | 0 / 0 (0 / 0) | 0 | — | — |
| `c142_05` | `ice_iceberg` | `9ea02549b36c0100` | 231 | 0 | 3 / 1 | 448 789 / 131 181 | 240 / 49 | 1 / 1 (1 / 1) | 0 | 92 мс → n 1002: 131 181 | `KernelRead: direct read failed` ×1 |
| `c142_06` | `sponge_dirty_bath` | `a511e5d4af7a0f0a` | 261 | 0 | 2 / 0 | 465 210 / 52 825 | 56 / 6 | 0 / 0 (0 / 0) | 0 | — | — |
| `c142_07` | `hoover_beach` | `5e1bd731e2e5d345` | 229 | 0 | 0 / 0 | 81 631 / 50 311 | 19 / 10 | 0 / 0 (0 / 0) | 0 | — | — |
| `c142_08` | `volcano_mountain` | `358be0e0d44d729e` | 201 | 0 | 0 / 0 | 52 909 / 36 209 | 140 / 30 | 0 / 0 (0 / 0) | 0 | — | — |
| `c142_09` | `voxel_world` | `eadf72b5b79ac096` | 178 | 0 | 7 / 0 | 316 631 / 41 895 | 90 / 5 | 6 / 0 (6 / 0) | 6 | — | — |
| `c142_10` | `enemy_gorilla` | `d78e0342fa2186f4` | 223 | 0 | 1 / 0 | 217 657 / 39 678 | 77 / 6 | 1 / 0 (1 / 0) | 0 | — | — |
| `v142` | `underwater_aerial_garden` | `565707122e53bb50` | 380 | 0 | 1 / 0 | 180 521 / 69 048 | 0 / 0 | 0 / 0 (0 / 0) | 0 | — | — |
| `w142` | `underwater_aerial_garden` | `7f42a2d3e1a151a2` | 187 | 0 | 594 / 1846 | 400 429 / 201 722 | 0 / 0 | 64 / 0 (64 / 0) | 0 | — | валидация: `[Vulkan][W]` 916 988, `[Vulkan][E]` 0; правило `dt` не применяется |

Профиль 96 / 1 / 4 — 12 из 12; в каждом логе 137 хэшей `CsPretranslate: skipped` (101 опкод + 32 `resource tracking` + 4 бюджет), из них на любой
иной строке, кроме `CsPretranslate phase …`, — 0 из 137 (`s142_f0.out.txt`). Срез лида `sig_quick.out.txt` подтверждён: 96 / 1 / 4 на всех 12, `BvhLoopCapTrip:`
на `c142_02` и `c142_09` по 6 строк.

### 3.1–3.6 Разборы (выводы скриптов)

- **3.1 Кадры ≥ 1 с и ≥ 100 мс после первого кадра сцены (без валидации), по полосам сессий — `ana_f0.out.txt` (3).** K2 на с. 113+: 4 лога —
  `vbn113k` (Б3а, закрыт), `ctl114a` (инструмент), `eatl122` (Б5а), `edes122` (Б24); на с. 128+ — 0. K3 на удержании на с. 128–141: 9 логов
  (`ack129`, `ack130`, `s12s130`, `lw3s131`…`lw6s131`, `rs135` — Sky Garden; `s3s130` — `intro_next`, 100 276 мкс).
- **3.2 Интервалы кадров K3 с. 142 — `ctx_f0.out.txt`.** Крупнейшие кадры окна входа содержат дамп IR трансляции (до 74 097 строк); кадры
  срабатывания BVH — `PriorityStall:` + `BvhLoopCapTrip:`; кадр `v142` n 382 (180 521 мкс, второй после первого кадра сцены) — без трансляции.
- **3.3 Сохранения кэша пайплайнов — `save_f0.out.txt`.** Стартовое сохранение (кадр n 2) кадр не держит; в середине уровня — 6 сохранений, 5 кадров ≥ 100 мс.
- **3.4 `PriorityStall:` — `ana_f0.out.txt` (4).** с. 113–127: 13 логов из 78; с. 128–141: 14 из 65; с. 142: 8 из 11 (без `w142`).
- **3.5 Интервал кадра Б2 — `ctx2_f0.out.txt`.** n 949–954: `PriorityStall:` ×1; `rs135` n 7445 (235 598 мкс) и `s3s130` n 2980 — без `PriorityStall:`, причина [U].
- **3.6 `MainTaskLate` ≥ 1 с на с. 113+ — `ana_f0.out.txt` (6):** `ctl114a`, `ctl114b`, `boot115a`, `boot115c`, `edes122`.

## 4. Реестр

Класс — п. 215(д)(2)(Б) с уточнениями п. 217(б)–(д), п. 218(г), (д)(2). **Дефект / наблюдение** — по п. 228(б): дефект — видимое последствие или
путь, который игра исполняет [c]. Где буква п. 228(б) и мой вариант расходятся, стоят оба. «Сцены [c]» — ключ 2. t / p — секунды игры до первого
воспроизведения. Столбец «без игры» отвечает на вопрос «идёт ли цикл правки и доказательства без прогона игры», а не «исправимо ли». P — [I].

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | механизм по коду `26457dd7` | сцены [c] | t / p | нужна игра | нужен пользователь | без игры | критерий доказательства (форма п. 228(г)(1)) | P(FIXED ≤ 2 итерации) [I] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Б5а | K4 (п. 231(д): 0/10 на `9235a7ac`; в ред. 2 — K2 на входе) | дефект (форма на `2baf8742`); ведёт трек S | холодный вход Atlantis: 1,39 с без нового показанного кадра после первого кадра сцены | открыт, ведёт трек S (`455b3a25:docs/ROADMAP.md:12152` «Граница с треком F», `455b3a25:docs/ROADMAP.md:12306` «p форм на установленной сборке»); на `9235a7ac` форма (кадр ≥ 1 с после первого кадра сцены) — 0 из 10 холодных входов переписи с. 142 [c] (максимум 816 566 мкс, `bumper_enemy_snowy_canyon` n 204); Atlantis на `9235a7ac` не входил — p на установленной сборке для Atlantis [U] | `2c65eb41:docs/session-141/inventory141.md:214` «Б5а»; `C:/kyty/s142/FACTS.md:221` «форма Б5а»; `ana_f0.out.txt` (3), (7) | кадр входа содержит синхронную трансляцию шейдеров обычного пути (`26457dd7:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:3874` «TranslateProgram(params.code») и удержанный неполный флип (`26457dd7:src/graphics/presentation/videoOut.cpp:1203` «held (incomplete frame)»); что держит именно 1,39 с на Atlantis — не названо | 1 | [U] / не конечна на умолчаниях | да | нет | нет | холодный стенд (копия кэшей без шейдеров и пайплайнов Atlantis, п. 228(в)): на `9235a7ac` — p по ≥ 2 холодным входам Atlantis; на сборке правки N ≥ ln 0,05 / ln(1 − p) холодных входов Atlantis без кадра ≥ 1 с после первого кадра сцены (при p = 0,9 — 2); контроль `KYTY_FIX_<ИМЯ>=0` воспроизводит; видео входа 120 с без новых K1/K2 | 0,30 |
| Б25 | K1 (на удержании) | дефект | гостевой assert «There are too many objects/batches in this scene.» и access violation гостя на интро | открыт; свип: 2 лога из 419 с входом `intro_next` — `C:/kyty/log_s14_s42_merged_cold.txt:4407364` (с. 42) и `C:/kyty/s59/log_sig1.txt:627192` (с. 59), оба с тем же `pc=0x00000009004a020e` [c]; на с. 113–141 — 0 из 12 входов `intro_next` [c]; на `9235a7ac` p [U] | `2c65eb41:docs/session-141/inventory141.md:232` «Б25»; `ana_f0.out.txt` (2f) | не назван (гостевой счётчик объектов/батчей; что его переполняет — [U]) | 1 | [U] / не конечна на умолчаниях | да | нет | нет | сначала p: серия входов `intro_next` с удержанием ≥ 90 с на `9235a7ac`; N ≥ ln 0,05 / ln(1 − p) входов без assert на сборке правки; при p = 0 на ≥ 60 входах — кандидат «ТУПИК (нет воспроизведения)» | 0,05 |
| Б24 | K2 (на удержании) | дефект | остановка главного потока 23,8 с при отключении HID-устройства на удержании `intro_next` | открыт; `MainTaskLate` ≥ 1 с на с. 113+ — 5 логов: `ctl114a`, `ctl114b` (внесённый сон, инструмент), `boot115a`, `boot115c` (10,3 с и 10,3 с — происхождение в F0 не разобрано), `edes122` [c]; на с. 128+ — 0 из 84 логов [c] | `2c65eb41:docs/session-141/inventory141.md:231` «Б24»; `ana_f0.out.txt` (6) | удаление устройства обрабатывается на главном потоке: `26457dd7:src/graphics/presentation/window/window.cpp:378` «SDL_GameControllerClose» (атрибуция документа с. 122, не доказана) | 1 | нужен пользователь | да | да | нет | серия отключений HID на удержании без кадра ≥ 1 с, N по p на отключение; по п. 228(д) — «ТУПИК», если стенда отключения без пользователя нет | 0,20 |
| Б5 | K3 | дефект; ведёт трек S | первый (холодный) вход уровня: кадры ≥ 100 мс в окне входа — синхронная трансляция шейдеров, ожидание трансляции CS, пропуск draw до готовности пайплайна и удержанные флипы | открыт, ведёт трек S (п. 229(б)); на `9235a7ac` [c]: кадр ≥ 100 мс в окне входа — 7 из 10 холодных входов переписи с. 142 (`big_hand_pirate_island`, `bumper_enemy_snowy_canyon`, `enemy_gorilla`, `ice_iceberg`, `sponge_dirty_bath`, `timestop_casino`, `voxel_world`), максимум 816 566 мкс; `AsyncPipelines: skipped draw` — 10 из 10; в интервале крупнейших кадров — дамп IR трансляции обычного пути (15 647 … 74 097 строк между соседними `FrameTrace`) и `CsStall: kind=wait` до 689 831 мкс (`C:/kyty/s142/log_c142_01.txt:350295`); тёплой базы для 10 новых уровней нет | `2c65eb41:docs/session-141/inventory141.md:213` «Б5»; `ana_f0.out.txt` (7); `ctx_f0.out.txt`; `s142_f0.out.txt` | `26457dd7:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:3874` «TranslateProgram(params.code» (трансляция на обычном пути), `26457dd7:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5645` «CsStall:», `26457dd7:src/graphics/host_gpu/renderer/renderDraw.cpp:4449` «AsyncPipelines: skipped draw», `26457dd7:src/graphics/presentation/videoOut.cpp:1203` «held (incomplete frame)» | 10 | ≈ 20 с | да | нет | нет | уровень-свидетель из переписи с. 142 на холодном стенде (копия кэшей до входа, п. 228(в)): максимум `dt` окна входа ≤ максимума тёплой базы того же уровня + допуск, названный лидом до кода; N ≥ 2 холодных входа на уровень (p = 7/10 ⇒ ln 0,05 / ln 0,3 = 3 входа на набор); видео 0 глитчей, 0 `[Vulkan][E]`; контроль `=0` даёт прежние кадры | 0,40 |
| Б3б | K4 (п. 231(г)(4)); вариант исполнителя — K3-симптом [c] | дефект (симптом строк Б33, Б1б, Б5, Б2) | ожидания `PriorityStall:` > 50 мс: кадр, в интервале которого стоит строка, длится ≥ 100 мс | открыт; проверка, которой не было в ред. 2 [c]: на с. 142 после первого кадра сцены — 20 ожиданий в окне входа и 3 на удержании, все 23 в кадрах ≥ 100 мс; из них 12 — кадры срабатывания ограничителя BVH (Б1б), 3 на удержании — кадры сохранения кэша пайплайнов (Б33); на с. 128–141: 88 ожиданий после первого кадра сцены, 21 в кадрах ≥ 100 мс | `2c65eb41:docs/session-141/inventory141.md:211` «Б3б»; `ana_f0.out.txt` (4), (7) | `26457dd7:src/graphics/host_gpu/renderer/commandScheduler.cpp:655` «PriorityStall:» — печать ожидания; причина ожидания — у строки-причины | 10 | ≈ 120 с | да | нет | нет | отдельной итерации не предлагается: после правки строки-причины — 0 строк `PriorityStall:` в кадрах ≥ 100 мс на входах её критерия | 0,30 |
| Б33 | K3 (на удержании; строка лида п. 231(г)(1)) | дефект; ведёт трек S | кадры 115–152 мс на удержании холодного первого входа; **атрибуция F0 [c]: сохранение кэша пайплайнов драйвера (≈ 90 МБ, 80–93 мс по `save_us`) в середине уровня под `m_mutex`** | открыт, ведёт трек S (`455b3a25:docs/ROADMAP.md:12295` «Б33 — K3 на удержании»; происхождение там [U]); атрибуция F0 — вход трека S; на `9235a7ac` [c]: 6 сохранений в середине уровня в 3 из 10 логов переписи (`big_hand_pirate_island` ×3, `timestop_casino` ×2, `ice_iceberg` ×1), 5 из 6 — в кадре ≥ 100 мс (165 920, 149 651, 151 746, 115 028, 131 181 мкс; шестой 93 171); четыре из них — все 4 кадра K3 удержания переписи с. 142, пятый (n 795) — в окне входа; в 3 из 4 прочитанных интервалов есть и дамп трансляции шейдера — доли не разделены; в 65 логах с. 128–141 сохранений в середине уровня нет (только стартовое, кадр n 2 ≈ 20 мс) | `455b3a25:docs/ROADMAP.md:12295` «Б33 — K3 на удержании»; `C:/kyty/s142/log_c142_02.txt:557303` (sha256 `bb6655d3d30c0bc7…`) «saved 90629860 bytes … (92638 us)» → `FrameTrace` n 1358 `dt_us` 149 651; `save_f0.out.txt`; `ctx_f0.out.txt` | `26457dd7:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:4655` «Called with m_mutex held», `26457dd7:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:4658` «MaybeWriteDriverCache», `26457dd7:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:4665` «20000000u» (раз в 20 с при новых пайплайнах — весь блоб синхронно), `26457dd7:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:4806` «pipeline cache: saved» | 3 | ≈ 200 с | да | нет | частично: правка и тест пути записи без игры; доказательство кадров — с игрой | холодный стенд (копия кэшей до входа): `big_hand_pirate_island` 120 с на сборке правки — 0 кадров ≥ 100 мс, в интервале которых стоит строка `Vulkan pipeline cache: saved`, при ≥ 1 сохранении в середине уровня; файл кэша после прогона читается следующей загрузкой (строка загрузки с тем же числом байт); N ≥ ln 0,05 / ln(1 − 5/6) = 2 сохранения без кадра ≥ 100 мс; контроль `KYTY_FIX_<ИМЯ>=0` возвращает кадры; видео 0 глитчей, 0 маркеров смерти | 0,60 |
| Б1б | K4 (`455b3a25:docs/ROADMAP.md:12302` «класс K4 не меняется»); вариант исполнителя — K3 по кадрам [c] | дефект | срабатывание ограничителя BVH: обход срезан на 65 536 шагах; кадр со срабатыванием длится 266–317 мс, 6 кадров подряд | открыт; на `9235a7ac` [c]: `big_hand_pirate_island` (кадры n 332–337: 299 442, 299 580, 284 617, 300 409, 298 800, 299 220 мкс) и `voxel_world` (n 182–187: 316 631 … 283 939 мкс) — в интервале каждого из 12 кадров строка `PriorityStall:` ≈ 0,27–0,29 с, строки `BvhLoopCapTrip:` стоят в интервалах этих же кадров (не менее 10 из 12 строк двух логов; вывод интервала n 186 `c142_09` обрезан списком); Sky Garden: 22 лога с. 103–126, на с. 127+ — 0 (в `v142` 0); картинка кадров срабатывания [U] (детектор глитчей 0 на обоих видео, листы — у лида) | `2c65eb41:docs/session-141/inventory141.md:208` «Б1б»; `C:/kyty/s142/log_c142_02.txt:269177` (sha256 `bb6655d3d30c0bc7…`); `C:/kyty/s142/log_c142_09.txt:206646` (sha256 `eadf72b5b79ac096…`); `ctx_f0.out.txt`; `ana_f0.out.txt` (2i) | `26457dd7:src/graphics/host_gpu/renderer/cache/faultManager.cpp:204` «BvhLoopCapTrip:»; сам обход (`380bb9d6…` и 12 BVH-программ) не исправлен — что зацикливает обход, [U] | 3 | ≈ 30 с | да | нет | нет | `big_hand_pirate_island` и `voxel_world` по 120 с на сборке правки: 0 строк `BvhLoopCapTrip:` и 0 кадров ≥ 100 мс на n первых 10 кадров после первого кадра сцены, сверх кадров холодного входа (вход — тёплый, второй); N ≥ ln 0,05 / ln(1 − 0,9) = 2 входа на уровень; видео 0 глитчей и лист кадров у срабатывания; контроль `=0` возвращает 6 строк; Sky Garden 300 с без `GpuHangAbort` | 0,20 |
| Б2 | K3 | дефект (происхождение [U]) | кадр 183–197 мс на n 949–954 Sky Garden | открыт; свип [c]: в интервале кадра — одна строка `PriorityStall:` и ничего иного (5 из 5 проверенных: `ack129`, `ack130`, `s12s130`, `lw4s131`, `lw5s131`) — то же событие, что Б3б; K3 на удержании Sky Garden — 8 из 56 входов с. 128–141 без валидации; на `9235a7ac` в `v142` (10 176 кадров после первого кадра сцены) — 0 ⇒ p на установленной сборке [U] (0/1) | `2c65eb41:docs/session-141/inventory141.md:209` «Б2»; `ctx2_f0.out.txt`; `ana_f0.out.txt` (3) | `26457dd7:src/graphics/host_gpu/renderer/commandScheduler.cpp:655` «PriorityStall:» — чего ждёт приоритетная операция на n ≈ 950, [U]; все логи формы — сборки трека `armcopy` с. 129–131 | 1 | [U] / не конечна на умолчаниях | да | нет | нет | сначала p на `9235a7ac`: ≥ 30 входов Sky Garden до n ≥ 1 100; при p = 0 на 30 — «НЕ ДЕФЕКТ (инструментальные сборки)» по п. 228(д); иначе N ≥ ln 0,05 / ln(1 − p) входов без кадра ≥ 100 мс на n 900–1 000 | 0,15 |
| Б31 | K3 | дефект | кадр 118 647 мкс на удержании холодного входа Day and Night (`ednn122` n 1826) | открыт; Day and Night после с. 122 не входил; по форме совпадает с Б33 (кадр ≥ 100 мс на удержании холодного входа) — принадлежность к Б33 [I], интервал кадра `ednn122` в F0 не читался | `2c65eb41:docs/session-141/inventory141.md:238` «Б31» | [U]; кандидат — механизм Б33 | 1 | ≈ 120 с | да | нет | нет | N ≥ ln 0,05 / ln(1 − 0,5) = 5 входов Day and Night без кадра ≥ 100 мс на удержании; до того — чтение интервала кадра n 1826 `ednn122` (без игры) | 0,15 |
| Б32 | K3 (строка лида п. 219(в)) | дефект (происхождение [U]) | кадры 100–236 мс на удержании вне окна Б2 (Sky Garden, `intro_next`) | открыт; свип [c]: на с. 128–141 вне n 945–960 — `lw3s131` n 1060 (155 753 мкс, в интервале `PriorityStall:` ×1), `rs135` n 7445 (235 598, без `PriorityStall:`), `s3s130` `intro_next` n 2980 (100 276), `lw6s131` — 26 кадров (в том же логе `LossWin: overflow`, инструмент `armcopy`); на `9235a7ac` в `v142` — 0 кадров ≥ 100 мс на удержании (9 577 кадров) ⇒ p [U] (0/1) | `455b3a25:docs/ROADMAP.md:11689` «Б32»; `ana_f0.out.txt` (3); `ctx2_f0.out.txt` | [U] | 2 | [U] / не конечна на умолчаниях | да | нет | нет | как в п. 219(в): p серией на `9235a7ac` (удержание ≥ 300 с), затем N ≥ ln 0,05 / ln(1 − p) входов без кадра ≥ 100 мс на удержании | 0,10 |
| Б34 | картинка; по п. 231(г)(2) дефектом не считается | наблюдение ([U]: эталона нет) | многокадровые чёрные и белые блоки в заставке уровня (`rec_c142_02.mp4` кадры ≈ 1 101–1 112, `rec_c142_03.mp4` кадры 1 174–1 178) | наблюдение (строка лида); сигнатуры в логах нет — свип её не видит; видео в F0 не смотрелись | `455b3a25:docs/ROADMAP.md:12298` «Б34 — наблюдение» | [U] | 2 | нужен пользователь | да | да (эталон с PS5) или A/B ручкой | нет | дефектом становится при эталоне или при различии A/B ручкой (п. 231(г)(2)); тогда — видео ≥ 3 000 кадров, 0 глитчей, лист | 0,10 |
| Б6 | K3 | наблюдение (дефект не показан) | «падающие частицы»/дым в комнате с пришельцем — не проверены | открыт (не проверен); сигнатуры в логах нет | `2c65eb41:docs/session-141/inventory141.md:215` «Б6» | [U] | 0 | [U] / не конечна на умолчаниях | да | нет | нет | видео ≥ 3 000 кадров катсцены, 0 глитчей и лист + прогон с валидацией 0 `[Vulkan][E]`; путь к комнате не назван | 0,30 |
| Б4 | K1 (при выходе) | дефект | гонка выхода: `CloseAll` против гостевого `KernelOpen` ⇒ `EXIT_IF` после `Event: quit` | открыт; свип [c]: `Error: condition (m_files[index] == nullptr)` — 1 лог из 1574 (`dds131`); на с. 142 — 0 из 12 | `2c65eb41:docs/session-141/inventory141.md:212` «Б4»; `C:/kyty/s131/log_dds131.txt:718963`; `ana_f0.out.txt` (2c) | `26457dd7:src/kernel/fileSystem.cpp:191` «m_files[index] == nullptr» | 1 | ≈ 23 000 с | да | нет | частично: стресс-тест `CloseAll` против `KernelOpen` без игры | N ≥ ln 0,05 / ln(1 − 0,0065) ≈ 460 выходов без `--- Fatal Error ---` — по п. 228(д) «ТУПИК», если стенда выхода нет; замена — тест гонки без игры | 0,10 |
| Б26 | K4 | наблюдение по букве п. 228(б) (шейдеры игрой не запрошены [c]); при запросе — K1 | SOP1 `0x21` (96), SOP1 `0x0c` (1), VOPC `0xe3` (4): 101 вычислительный шейдер не транслируется | открыт (F1 идёт); свип [c]: профиль 96/1/4 — 733 логов (с. 14–142), 12 из 12 логов с. 142; все 101 строка в каждом логе с. 142 — строки `CsPretranslate: skipped` спекулятивного потока, который перехватывает фатал; ни один из 101 хэша (и из 36 хэшей Ф3) ни в одном из 12 логов не встречается ни в одной строке, кроме `CsPretranslate phase …`/`skipped`: строк `CsPretranslate: miss`/`hit` обычного пути для них 0 [c] ⇒ на 11 уровнях за 120–334 с игра эти шейдеры не диспатчила; на обычном пути тот же опкод — `EXIT` (смерть процесса), маркеров смерти 0 из 12 | `2c65eb41:docs/session-141/inventory141.md:233` «Б26»; `C:/kyty/s142/log_c142_02.txt:9989` (sha256 `bb6655d3d30c0bc7…`); `s142_f0.out.txt`; `ana_f0.out.txt` (1) | постановка в очередь при регистрации шейдера — `26457dd7:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5969` «mapped.type == Prospero::ShaderBinaryType::kCs»; строка — `26457dd7:src/graphics/host_gpu/renderer/pipeline/computePretranslation.h:232` «CsPretranslate: skipped» под `26457dd7:src/graphics/host_gpu/renderer/pipeline/computePretranslation.h:212` «ScopedFatalInterceptor»; обычный путь — `26457dd7:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:3869` «pretranslation.Take» → `26457dd7:src/graphics/host_gpu/renderer/pipeline/computePretranslation.h:130` «CsPretranslate: miss» → `26457dd7:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:3874` «TranslateProgram(params.code» → `26457dd7:src/graphics/shader/recompiler/frontend/cfg/ShaderCFG.cpp:44` «shader CFG build failed»; декодер — `26457dd7:src/graphics/shader/recompiler/frontend/decode/ScalarAluOps.cpp:153` «SOP1 opcode is not implemented», `26457dd7:src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp:1147` «VOPC opcode is not implemented» | 19 | ≈ 20 с | частично | нет | да (тест на опкод, `shader_cfg_tests`); последствие в игре проверить нечем, пока нет сцены, которая диспатчит такой шейдер | как п. 228(е) (1)–(5); дополнение F0: строка «0 строк маркера на входе» различает только поток спекуляции — сцену-свидетеля даёт первая строка `CsPretranslate: miss hash=<один из 101>` или `shader CFG build failed` вне `CsPretranslate:` в любом логе | 0,30 |
| Ф5 | K4 | дефект по букве п. 228(б) (путь исполняется на каждом входе [c]); вариант исполнителя — наблюдение до кадра-свидетеля | новая (пакет): игнорируемое состояние ГП — метаданные цвета `dcc=true`, адреса CMASK/FMASK/DCC, режим округления цвета, включённые depth/stencil без привязки, `GE_STEREO_CNTL`, диспатч нулевого размера | открыт; [c]: каждая из шести строк — в 1099…1103 логах, на с. 128+ в 84 из 84; строки печатаются один раз на процесс (кроме диспатча и `GE_STEREO_CNTL`); видимое последствие [U] | `C:/kyty/s142/log_c142_02.txt:207786` «skipping zero-sized dispatch»; таблица сигнатур §2 | `26457dd7:src/graphics/host_gpu/renderer/debug.cpp:226` «ignoring PS5 color metadata», `26457dd7:src/graphics/host_gpu/renderer/debug.cpp:313` «ignoring PS5 metadata addresses», `26457dd7:src/graphics/host_gpu/renderer/debug.cpp:246` «ignoring PS5 color round mode», `26457dd7:src/graphics/host_gpu/renderer/depthRenderTarget.cpp:358` «without a bound attachment», `26457dd7:src/graphics/guest_gpu/command_processor/pm4Handlers.cpp:4017` «GE_STEREO_CNTL», `26457dd7:src/graphics/host_gpu/renderer/renderCompute.cpp:939` «skipping zero-sized dispatch» | 19 | ≈ 20 с | да | нет | нет | на член пакета: кадр-свидетель (RenderDoc или видео), где игнорируемое состояние меняет картинку; без свидетеля — «НЕ ДЕФЕКТ» по п. 228(д); при свидетеле — видео ≥ 3 000 кадров 0 глитчей + 0 `[Vulkan][E]` | 0,20 |
| Ф3 | K4 | наблюдение по букве п. 228(б) (шейдеры игрой не запрошены [c]); при запросе — K1 или K2 | новая: спекулятивная трансляция CS не проходит ещё у 36 шейдеров на лог — 32 «shader resource tracking», 4 «speculative translation budget exceeded» (у одного — `CFG dispatcher fallback … StructuredControlFlow`) | открыт; [c]: `resource tracking` — 818 логов (с. 14–142), бюджет — 843 логов; на с. 142 — 12 из 12; обычным путём ни один из 36 хэшей в 12 логах с. 142 не запрошен (0 строк `miss`/`hit`) | `C:/kyty/s142/log_c142_02.txt:490948` (sha256 `bb6655d3d30c0bc7…`); `s142_f0.out.txt` | `26457dd7:src/graphics/shader/recompiler/ir/passes/ResourceTracking.cpp:171` «shader resource tracking», `26457dd7:src/graphics/shader/recompiler/TranslationBudget.h:21` «budget exceeded», `26457dd7:src/graphics/shader/recompiler/ShaderRecompiler.cpp:72` «CFG dispatcher fallback»; на обычном пути бюджета нет (`26457dd7:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:3874` «TranslateProgram(params.code») — длительность трансляции этих 4 шейдеров [U] | 19 | ≈ 20 с | частично | нет | да (тест транслятора на шейдер из дампа) | тест на каждый из 36 шейдеров (дамп кода из лога спекуляции) — трансляция проходит; 0 строк `skipped … resource tracking`/`budget exceeded` на входе уровня-свидетеля; видео входа 120 с без новых K1/K2; контроль `=0` | 0,20 |
| Ф7 | K4 | наблюдение | новая (пакет): `file not found` на `KernelStat`, `warning: size_bytes/base is not 256-byte aligned`, `Format … cannot be used as texture` | наблюдение; [c]: `file not found` — 13 937 359 строк в 1106 логах (в `c142_02` 6 404), выравнивание — 1107 логов; на с. 128+ — 84 из 84 | `C:/kyty/s142/log_c142_02.txt:30109`; `C:/kyty/s142/log_c142_02.txt:15230` | `26457dd7:src/libs/agc.cpp:3071` «size_bytes is not 256-byte aligned»; `KernelStat` на отсутствующий файл возвращает `ENOENT` (`26457dd7:src/kernel/fileSystem.cpp`, строка «file not found»); какие файлы игра не находит и ждёт ли их — в F0 не разобрано | 19 | ≈ 20 с | нет | нет | да (перечень ненайденных путей — по логам) | перечень путей `KernelStat` с `file not found` против содержимого `games/PPSA21564-app`: если все пути — необязательные пробы, «НЕ ДЕФЕКТ»; иначе строка на файл | 0,05 |
| Б9а | K4 | дефект (путь исполняется [c]) | новая (из Б9): игра вызывает неразрешённые импорты `AudioPropagation` — 4 символа, заглушка возвращает 0 | открыт; [c]: `timestop_casino` (`c142_03`) — `b-dYXrjSNZU` 2, `WXMhENV2NcA` 295, `d84otraxt2s` 365, `G+QLTfyLMYk` 362 строки (печать ограничена 1 024 вызовами — вызовов не меньше); в прочих 11 логах с. 142 — 0; до того — только `Json2` в 2 логах с. 45; утверждение ред. 2 «ни один не вызывался» для `timestop_casino` неверно; последствие (звук) [U] — видео звук не проверяет | `C:/kyty/s142/log_c142_03.txt:239572` (sha256 `9aaa83b0c73e66b1…`); `s142_f0.out.txt`; `ana_f0.out.txt` (2h) | `26457dd7:src/loader/runtimeLinker.cpp:408` «Unresolved import stub called» (после 1 024 вызовов печать молчит, возврат 0); патч импорта — `26457dd7:src/loader/runtimeLinker.cpp:1156` «unresolved PLT import patched» | 1 | ≈ 20 с | да | нет (картинка); да — если критерий требует слушать звук | частично: реализация 4 NID и тест без игры | вход `timestop_casino` 120 с на сборке правки: 0 строк `Unresolved import stub called` с `AudioPropagation`; 0 маркеров смерти, видео 0 глитчей, K3 удержания не больше `c142_03`; тест на каждый из 4 NID (возврат и выходные параметры по первоисточнику); контроль `=0` возвращает строки | 0,50 |
| Ф4 | K4 | наблюдение (обход действует [c]) | новая: `KernelRead: direct read failed … reading through a host buffer` — прямое чтение в защищённые кэшем страницы вернуло 0 байт, сработал обход | наблюдение; [c]: 207 логов (с. 14–142), на с. 142 — 1 из 12 (`ice_iceberg`, 1 строка, размер 0x98290) | `C:/kyty/s142/log_c142_05.txt:414100` (sha256 `9ea02549b36c0100…`) | `26457dd7:src/kernel/fileSystem.cpp:724` «KernelRead: direct read failed» — печать перед чтением через хост-буфер; полнота обхода для прочих системных вызовов чтения [U] | 1 | ≈ 720 с | нет | нет | да (чтение кода) | перечень путей чтения в гостевую память без обхода (`pread`, `readv`, AIO) по коду; при находке — тест чтения в защищённую страницу | 0,10 |
| Б1а | K4 (поправка лида п. 219: на умолчаниях 0/284) | дефект, закрытый ограничителем | зависание входа в обходе BVH без предела шагов | форма снята умолчанием `KYTY_BVH_LOOP_CAP`; свип [c]: `GpuHangAbort` после с. 102 — только 3 лога фикстур `fx/hang`; на с. 128+ — 0 из 84; срабатывания ограничителя на 2 новых уровнях (Б1б) ⇒ без ограничителя эти входы зависли бы [I] | `2c65eb41:docs/session-141/inventory141.md:207` «Б1а»; `ana_f0.out.txt` (2d) | см. Б1б | 1 | [U] / не конечна на умолчаниях | да | нет | нет | общий с Б1б (исправленный обход): серия 34 входов без зависания при ограничителе ВЫКЛ на сборке правки (ред. 2) | 0,10 |
| Ф6 | K4 | наблюдение | новая: предупреждения слоя валидации — фрагментный шейдер пишет в `out_mrt_N`, для которого нет привязанной цели | наблюдение; [c]: логов с `[Vulkan][W]` — 32 (с. 38–142), в `w142` 916 988 строк `[Vulkan][W]`; `[Vulkan][E]` — 0 на с. 142, последняя сессия с `[Vulkan][E]` — 38 | `C:/kyty/s142/log_w142.txt` (sha256 `7f42a2d3e1a151a2…`); таблица сигнатур §2 | запись в выход без цели отбрасывается хостом; соответствие маске целей гостя [U] | 1 | ≈ 20 с | нет | нет | да (маска записи по числу целей в пайплайне) | прогон с валидацией Sky Garden 300 с: 0 строк `[Vulkan][W]` этой формы при 0 `[Vulkan][E]` и видео 0 глитчей; контроль `=0` | 0,20 |
| Б30 | K4 | наблюдение | окно простоя GPU на удержании Day and Night без кадра ≥ 100 мс | открыт; уровень после с. 122 не входил | `2c65eb41:docs/session-141/inventory141.md:237` «Б30» | [U] | 1 | ≈ 300 с | да | нет | нет | кадр ≥ 100 мс или кадр-свидетель; иначе «НЕ ДЕФЕКТ» | 0,10 |
| Б7 | K4 | наблюдение (проявления нет) | `V_MUL_LEGACY_F32` / `V_FMAC_LEGACY_F32` не декодируются | открыт; свип [c]: строк `opcode is not implemented` семейства VOP2 (и любого, кроме SOP1 `0x21`, `0x0c`, VOPC `0xe3`) — 0 в 1574 логах, включая 10 новых уровней ⇒ на исполненных путях не встречен | `2c65eb41:docs/session-141/inventory141.md:216` «Б7» | `26457dd7:src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp:1475` «VOP2 opcode is not implemented» | 0 | [U] / не конечна на умолчаниях | нет | нет | да (тест на опкод) | тест на опкод; при встрече — вход сцены без `EXIT` | 0,50 |
| Б11 | K4 | наблюдение (проявления нет) | `shader_cfg_tests`: падения `IMAGE_SAMPLE_C`, `IMAGE_SAMPLE_C_LZ` | открыт; в F0 тесты не запускались | `2c65eb41:docs/session-141/inventory141.md:220` «Б11» | `26457dd7:tests/shaderCfgTests.cpp` (строки — в ред. 2) | 0 | [U] / не конечна на умолчаниях | нет | нет | да | оба теста проходят; затем видео сцены с тенями | 0,40 |
| Б14 | K4 | наблюдение (проявления нет) | траектория `rtskip=1` значениями не сверяется | открыт; 10 новых уровней вошли на `rtskip=1` с 0 глитчей детектора — это не сверка `rtskip=2` | `2c65eb41:docs/session-141/inventory141.md:223` «Б14» | [U] (довод проекта) | 0 | [U] / не конечна на умолчаниях | да | нет | нет | 0 расхождений `rtskip=2` + видео на сцене переписи | 0,40 |
| Б13 | K4 | наблюдение (проявления нет) | порядок эпох `ChangeState<Cpu,true>` | открыт; сигнатуры в логах нет | `2c65eb41:docs/session-141/inventory141.md:222` «Б13» | ред. 2 | 0 | [U] / не конечна на умолчаниях | нет | нет | да (правка порядка + тест) | правка + серия без регрессии | 0,35 |
| Б12 | K4 | наблюдение (проявления нет) | дыра `bdastamp`: регион 4 МиБ на два диапазона | открыт; сигнатуры в логах нет | `2c65eb41:docs/session-141/inventory141.md:221` «Б12» | ред. 2 | 0 | [U] / не конечна на умолчаниях | да | нет | нет | выгрузка раскладок на сцене переписи | 0,30 |
| Б28 | K4 | наблюдение (проявления нет) | полнота инвалидации захвата целей при `rtskip=1` | открыт; сигнатуры в логах нет | `2c65eb41:docs/session-141/inventory141.md:235` «Б28» | ред. 2 | 0 | [U] / не конечна на умолчаниях | да | нет | нет | 0 расхождений `rtskip=2`, контроль `rtskip=3` падает | 0,30 |
| Б29 | K4 | наблюдение (проявления нет) | `rtskip` в OLD: 0 пар | открыт; сигнатуры в логах нет | `2c65eb41:docs/session-141/inventory141.md:236` «Б29» | ред. 2 | 0 | [U] / не конечна на умолчаниях | да | нет | нет | 0 расхождений `rtskip=2` в OLD + видео | 0,30 |
| Б8 | K4 | наблюдение (проявления нет) | `exec ? new : old` исправлен только на верхнем уровне PS | открыт; шейдера-свидетеля нет | `2c65eb41:docs/session-141/inventory141.md:217` «Б8» | ред. 2 | 0 | [U] / не конечна на умолчаниях | нет | нет | да (тест транслятора) | тест + видео сцены-свидетеля | 0,20 |
| Б10 | K4 | наблюдение (проявления нет) | нет PCF в ручном сравнении глубины | открыт; кадра-свидетеля нет | `2c65eb41:docs/session-141/inventory141.md:219` «Б10» | ред. 2 | 0 | [U] / не конечна на умолчаниях | да | нет | нет | видео тени сцены-свидетеля | 0,20 |
| Б27 | K4 | наблюдение (проявления нет) | долг `daslot`: гонка размера `ahead_threads` | открыт; маркеров смерти на с. 128+ с этим местом — 0 | `2c65eb41:docs/session-141/inventory141.md:234` «Б27» | ред. 2 | 0 | [U] / не конечна на умолчаниях | нет | нет | да (стресс-тест) | правка + стресс-тест | 0,20 |
| Б9 | K4 | наблюдение (проявления нет) | неразрешённые импорты, которые игра не вызывала | открыт; свип [c]: `Relocate: unresolved PLT import patched to stub` — 1108 логов; вызванные — см. Б9а; маркер ред. 2 `=== Stubbed function` — 0 логов из 1574: не срабатывал ни разу, действующий маркер — `Unresolved import stub called` | `2c65eb41:docs/session-141/inventory141.md:218` «Б9» | `26457dd7:src/loader/runtimeLinker.cpp:1156` «unresolved PLT import patched»; `26457dd7:src/loader/runtimeLinker.cpp:1214` «=== Stubbed function» | 0 | [U] / не конечна на умолчаниях | нет | нет | да | 0 строк `Unresolved import stub called` на входах переписи; при встрече — строка на библиотеку | 0,10 |
| Ф8 | K4 | наблюдение (последняя с. 105) | новая: `AudioOut: SDL_QueueAudio failed: Invalid audio device ID` — до 438 760 строк на лог после потери аудиоустройства хоста | наблюдение; [c]: 20 логов, с. 45–105; на с. 113+ — 0 | `C:/kyty/s105/log_abb105.txt:2871038` (sha256 `1c903fa919158685…`) | переоткрытие аудиоустройства после его потери отсутствует [I] (код в F0 не читался) | 0 | [U] / не конечна на умолчаниях | нет | да (отключение аудиоустройства) | частично | стенд отключения аудиоустройства: звук возвращается, 0 строк после переподключения; без стенда — «ТУПИК» | 0,10 |
| Б22 | K5 | вне трека (п. 228(а)) | устаревшие утверждения в документах | открыт; добавить: `CLAUDE.md` «Каталог `_PipelineCache` не существует» против строки лога `saved … to _PipelineCache\PPSA21564.bin` (Ф1); маркер Б9 ред. 2 | `2c65eb41:docs/session-141/inventory141.md:230` «Б22» | — | 0 | [U] / не конечна на умолчаниях | нет | нет | да | как в ред. 2 | 0,90 |
| Б16 | K5 | вне трека (п. 228(а)) | список «14 падающих тестов» устарел | открыт; в F0 не перепроверялся | `2c65eb41:docs/session-141/inventory141.md:225` «Б16» | — | 0 | [U] / не конечна на умолчаниях | нет | нет | да | как в ред. 2 | 0,80 |
| Б20 | K5 | вне трека (п. 228(а)) | печати не покрывают `enter_scene.py` и `s51_vidglitch.py` | исполнено для печати `pred/02_sc142.md` (`C:/kyty/s142/FACTS.md:25` «в печати, Б20»); для печатей трека F — не проверялось | `2c65eb41:docs/session-141/inventory141.md:229` «Б20» | — | 0 | [U] / не конечна на умолчаниях | нет | нет | да | как в ред. 2 | 0,80 |
| Б19 | K5 | вне трека (п. 228(а)) | класс «первый символ» у флагов окружения — 52 места | открыт; в F0 не перепроверялся | `2c65eb41:docs/session-141/inventory141.md:228` «Б19» | — | 0 | [U] / не конечна на умолчаниях | нет | нет | да | как в ред. 2 | 0,70 |
| Б15 | K5 | вне трека (п. 228(а)) | `resource_tracking_tests` падает с с. 60 | открыт; в F0 не перепроверялся | `2c65eb41:docs/session-141/inventory141.md:224` «Б15» | — | 0 | [U] / не конечна на умолчаниях | нет | нет | да | как в ред. 2 | 0,50 |
| Б17 | K5 | вне трека (п. 228(а)) | `KYTY_GPU_CHECKPOINTS=1` сам вешает вход | открыт; в F0 не перепроверялся | `2c65eb41:docs/session-141/inventory141.md:226` «Б17» | — | 0 | [U] / не конечна на умолчаниях | нет | нет | да | как в ред. 2 | 0,30 |
| Б18 | K5 | вне трека (п. 228(а)) | падение старта `commandRecorder.cpp:326` | открыт; свип [c]: 6 логов — `m5cap102`, `boot114`, `boot114b`, `boot114c`, `boot115b` (2 копии с разным sha256); все без строки входа уровня; `26457dd7:src/graphics/host_gpu/renderer/commandRecorder.cpp:326` «m_producer != self» | `2c65eb41:docs/session-141/inventory141.md:227` «Б18» | — | 0 | [U] / не конечна на умолчаниях | нет | нет | да | как в ред. 2 | 0,30 |

**Итого строк — 41:** из `inventory141.md` ред. 2 — 31 (24 открытых K1–K4 + 7 K5), строк лида — 3 (Б32 п. 219(в); Б33, Б34 п. 231(г)), новых F0 — 7 (Ф5, Ф3, Ф7, Б9а, Ф4, Ф6, Ф8). По ключу 1: K1/K2 на входе и удержании — 2, K3 — 7,
K1/K2 вне входа и удержания — 1, K4 — 24, K5 — 7 (сумма 41); K1–K4 — 34. По столбцу «дефект / наблюдение»: дефект — 14, наблюдение — 20, вне трека (K5) — 7 (сумма 41).
Строка курса 142 (п. 231(ж)) воспроизведена по строкам ред. 2 и лида без Б34: K1 2 / K2 1 / K3 6 / K4 17 / K5 7 = 33 (ключ 1 «K3 — 7» включает наблюдение Б34).

**Не ранжируются:** Б3а (рывок 3 с — отнесён к закрытому с. 114–115; `2c65eb41:docs/session-141/inventory141.md:210` «Б3а»; свип: K2 на удержании на с. 115+ — только Б24, `ana_f0.out.txt` (3));
Б23 (`protceil=1`, `ErrorDeviceLost` в `s1s128`, `s2s128` — значение выведено из употребления); `LossWin: overflow kind=open` (`lw6s131`, инструмент `armcopy`,
не умолчание; в том же логе 26 кадров K3 на удержании); `TextureCache: failed to map reusable download buffer` (`bf96a`, с. 96, инструмент).
Закрытые по сигнатурам свипа (последняя сессия < 113): `--- Error ---` (с. 102), `Unhandled host exception` (с. 59), `[Vulkan][E]` (с. 38),
`Skipping unsupported GE shader draw` (с. 32), `warning: executing wave64 compute shader` (с. 67), `shader IR validation failed` (с. 30),
`vkQueuePresentKHR … eErrorOutOfDateKHR` (с. 49), CFG `unsupported_reason=` (с. 59).

## 5. Ранжирование по ключам (В) `inventory141.md` — предложение

Ключ 1 — K1/K2 на входе или удержании > K3 > K1/K2 вне входа и удержания > K4 > K5; ключ 2 — число сцен [c]; ключ 3 — t / p (p [U] и «не конечна» —
в конец ступени ключа 2, «нужен пользователь» — после них); равенство — по P.

| место | строка | ключ 1 | ключ 2 (сцены [c]) | ключ 3 | P [I] |
|---|---|---|---|---|---|
| 1 | Б25 — гостевой assert «There are too many objects/batches in this scene.» и access violation гос | K1/K2 на входе/удержании | 1 | [U] / не конечна на умолчаниях | 0,05 |
| 2 | Б24 — остановка главного потока 23,8 с при отключении HID-устройства на удержании `intro_next` | K1/K2 на входе/удержании | 1 | нужен пользователь | 0,20 |
| 3 | Б5 — первый (холодный) вход уровня: кадры ≥ 100 мс в окне входа — синхронная трансляция шейдеро | K3 | 10 | ≈ 20 с | 0,40 |
| 4 | Б33 — кадры 115–152 мс на удержании холодного первого входа; **атрибуция F0 [c]: сохранение кэша | K3 | 3 | ≈ 200 с | 0,60 |
| 5 | Б32 — кадры 100–236 мс на удержании вне окна Б2 (Sky Garden, `intro_next`) | K3 | 2 | [U] / не конечна на умолчаниях | 0,10 |
| 6 | Б34 — многокадровые чёрные и белые блоки в заставке уровня (`rec_c142_02.mp4` кадры ≈ 1 101–1 11 | K3 | 2 | нужен пользователь | 0,10 |
| 7 | Б31 — кадр 118 647 мкс на удержании холодного входа Day and Night (`ednn122` n 1826) | K3 | 1 | ≈ 120 с | 0,15 |
| 8 | Б2 — кадр 183–197 мс на n 949–954 Sky Garden | K3 | 1 | [U] / не конечна на умолчаниях | 0,15 |
| 9 | Б6 — «падающие частицы»/дым в комнате с пришельцем — не проверены | K3 | 0 | [U] / не конечна на умолчаниях | 0,30 |
| 10 | Б4 — гонка выхода: `CloseAll` против гостевого `KernelOpen` ⇒ `EXIT_IF` после `Event: quit` | K1/K2 вне входа и удержания | 1 | ≈ 23 000 с | 0,10 |
| 11 | Б26 — SOP1 `0x21` (96), SOP1 `0x0c` (1), VOPC `0xe3` (4): 101 вычислительный шейдер не транслиру | K4 | 19 | ≈ 20 с | 0,30 |
| 12 | Ф5 — новая (пакет): игнорируемое состояние ГП — метаданные цвета `dcc=true`, адреса CMASK/FMASK | K4 | 19 | ≈ 20 с | 0,20 |
| 13 | Ф3 — новая: спекулятивная трансляция CS не проходит ещё у 36 шейдеров на лог — 32 «shader resou | K4 | 19 | ≈ 20 с | 0,20 |
| 14 | Ф7 — новая (пакет): `file not found` на `KernelStat`, `warning: size_bytes/base is not 256-byte | K4 | 19 | ≈ 20 с | 0,05 |
| 15 | Б3б — ожидания `PriorityStall:` > 50 мс: кадр, в интервале которого стоит строка, длится ≥ 100 м | K4 | 10 | ≈ 120 с | 0,30 |
| 16 | Б1б — срабатывание ограничителя BVH: обход срезан на 65 536 шагах; кадр со срабатыванием длится  | K4 | 3 | ≈ 30 с | 0,20 |
| 17 | Б9а — новая (из Б9): игра вызывает неразрешённые импорты `AudioPropagation` — 4 символа, заглушк | K4 | 1 | ≈ 20 с | 0,50 |
| 18 | Ф6 — новая: предупреждения слоя валидации — фрагментный шейдер пишет в `out_mrt_N`, для которог | K4 | 1 | ≈ 20 с | 0,20 |
| 19 | Б30 — окно простоя GPU на удержании Day and Night без кадра ≥ 100 мс | K4 | 1 | ≈ 300 с | 0,10 |
| 20 | Ф4 — новая: `KernelRead: direct read failed … reading through a host buffer` — прямое чтение в  | K4 | 1 | ≈ 720 с | 0,10 |
| 21 | Б5а — холодный вход Atlantis: 1,39 с без нового показанного кадра после первого кадра сцены | K4 | 1 | [U] / не конечна на умолчаниях | 0,30 |
| 22 | Б1а — зависание входа в обходе BVH без предела шагов | K4 | 1 | [U] / не конечна на умолчаниях | 0,10 |
| 23 | Б7 — `V_MUL_LEGACY_F32` / `V_FMAC_LEGACY_F32` не декодируются | K4 | 0 | [U] / не конечна на умолчаниях | 0,50 |
| 24 | Б11 — `shader_cfg_tests`: падения `IMAGE_SAMPLE_C`, `IMAGE_SAMPLE_C_LZ` | K4 | 0 | [U] / не конечна на умолчаниях | 0,40 |
| 25 | Б14 — траектория `rtskip=1` значениями не сверяется | K4 | 0 | [U] / не конечна на умолчаниях | 0,40 |
| 26 | Б13 — порядок эпох `ChangeState<Cpu,true>` | K4 | 0 | [U] / не конечна на умолчаниях | 0,35 |
| 27 | Б12 — дыра `bdastamp`: регион 4 МиБ на два диапазона | K4 | 0 | [U] / не конечна на умолчаниях | 0,30 |
| 28 | Б28 — полнота инвалидации захвата целей при `rtskip=1` | K4 | 0 | [U] / не конечна на умолчаниях | 0,30 |
| 29 | Б29 — `rtskip` в OLD: 0 пар | K4 | 0 | [U] / не конечна на умолчаниях | 0,30 |
| 30 | Б8 — `exec ? new : old` исправлен только на верхнем уровне PS | K4 | 0 | [U] / не конечна на умолчаниях | 0,20 |
| 31 | Б10 — нет PCF в ручном сравнении глубины | K4 | 0 | [U] / не конечна на умолчаниях | 0,20 |
| 32 | Б27 — долг `daslot`: гонка размера `ahead_threads` | K4 | 0 | [U] / не конечна на умолчаниях | 0,20 |
| 33 | Б9 — неразрешённые импорты, которые игра не вызывала | K4 | 0 | [U] / не конечна на умолчаниях | 0,10 |
| 34 | Ф8 — новая: `AudioOut: SDL_QueueAudio failed: Invalid audio device ID` — до 438 760 строк на ло | K4 | 0 | [U] / не конечна на умолчаниях | 0,10 |
| 35 | Б22 — устаревшие утверждения в документах | K5 | 0 | [U] / не конечна на умолчаниях | 0,90 |
| 36 | Б16 — список «14 падающих тестов» устарел | K5 | 0 | [U] / не конечна на умолчаниях | 0,80 |
| 37 | Б20 — печати не покрывают `enter_scene.py` и `s51_vidglitch.py` | K5 | 0 | [U] / не конечна на умолчаниях | 0,80 |
| 38 | Б19 — класс «первый символ» у флагов окружения — 52 места | K5 | 0 | [U] / не конечна на умолчаниях | 0,70 |
| 39 | Б15 — `resource_tracking_tests` падает с с. 60 | K5 | 0 | [U] / не конечна на умолчаниях | 0,50 |
| 40 | Б17 — `KYTY_GPU_CHECKPOINTS=1` сам вешает вход | K5 | 0 | [U] / не конечна на умолчаниях | 0,30 |
| 41 | Б18 — падение старта `commandRecorder.cpp:326` | K5 | 0 | [U] / не конечна на умолчаниях | 0,30 |

## 6. Предложение порядка итераций F2…F6 (F1 = Б26: F1a — «нужен проект», F1c — `NOT EVALUABLE`)

Холодный вход — Б5, Б5а, Б33 — ведёт трек S (`455b3a25:docs/ROADMAP.md:12152` «Граница с треком F»); в очередь F они не ставятся. Атрибуция Б33 этого реестра (сохранение кэша
пайплайнов под `m_mutex`) — вход трека S: в `docs/track-s/s0-design.md` она не названа (0 вхождений `WriteDriverCache`/`pipeline cache: saved`).
Первые по ключам Б25 и Б24 не имеют воспроизведения без пользователя или с конечной ценой. Остальное — по ключам, с названными отступлениями:

| итерация | строка | почему здесь | что нужно до кода |
|---|---|---|---|
| F2 | **Б1б (+ Б1а)** обход BVH | единственная строка очереди F с [c]-следствием по времени кадра на `9235a7ac` (2 уровня, 6 кадров ≈ 0,3 с подряд), пользователь не нужен; исправление обхода закрывает и Б1а; порядок п. 228(е) | проект до кода: что зацикливает обход `380bb9d6…` на `big_hand_pirate_island` — дамп привязок `KYTY_DUMP_CS` на кадре срабатывания (один прогон Harness Engineer под замком) |
| F3 | **Б9а** `AudioPropagation` | единственная K4 с исполняемым путём [c], уровень-свидетель есть, правка мала | первоисточник по 4 NID (имена функций и возвраты); решение лида по В2 |
| F4 | **Б11** `IMAGE_SAMPLE_C` (в пакете с Ф3 при общем доказательстве тестами, п. 228(г)) | без игры и без замка: тесты транслятора; порядок п. 228(е) | список падений `shader_cfg_tests` на HEAD (Б16) |
| F5 | **Б4** гонка выхода — тест без игры | K1; по п. 228(д) с игрой — «ТУПИК» (≈ 460 выходов), замена — стресс-тест `CloseAll` против `KernelOpen` | критерий лида: тест воспроизводит `EXIT_IF` до правки |
| F6 | **Ф5 / Ф7** пакеты наблюдений — офлайн-разбор | решает «НЕ ДЕФЕКТ» или строку со свидетелем без игры: перечень ненайденных файлов, кадр-свидетель игнорируемого состояния | ответ лида на В2 |

Вне очереди, только прогоны (без кода): серия p на `9235a7ac` для Б2, Б32 (одна серия Sky Garden ≥ 300 с — данные даёт серия `sc143` и повторные V) и Б25
(`intro_next` ≥ 90 с) — решает «НЕ ДЕФЕКТ» / «ТУПИК»; чтение интервала кадра `ednn122` n 1826 (Б31) — офлайн.
Отличие от порядка п. 228(е): Б11 — после Б9а (у Б11 0 сцен [c], у Б9а путь исполняется [c]).

## 7. Вопросы лиду

- **В1 (F1, Б26).** По логам шейдеры с тремя опкодами игра не диспатчит (§0 п. 1). Оставить Б26 дефектом K4 по порядку п. 228(е) или перевести в
  «наблюдение» до сцены-свидетеля (первая строка `CsPretranslate: miss` с одним из 101 хэшей)? Критерий (3) п. 228(е) — «0 строк … на входе» — при любом
  ответе проверяет поток спекуляции, а не кадр. Семантика опкодов — задача F1a; имена по памяти: SOP1 `0x21` — `S_SWAPPC_B64`, SOP1 `0x0c` — `S_BREV_B64`
  [I-память; веб недоступен: `gitlab.freedesktop.org` — отказ доступа, зеркало — 404, 2 попытки].
- **В2 (определение п. 228(б)).** «Путь, который игра исполняет» по букве делает дефектами пакеты Ф5 (игнорируемое состояние ГП) и Б9а; вариант исполнителя —
  дефект только при кадре-свидетеле или вызове с ненулевым последствием. В реестре стоят оба прочтения; какое действует?
- **В3 (классы).** Б1б: п. 231(г)(3) оставил K4 («на листах видимого следствия нет [I]»); по логам каждое срабатывание — кадр 266–317 мс [c]. Перевести
  Б1б в K3 (и Б3б — в K3-симптом)? В реестре класс — по букве п. 231, вариант исполнителя — рядом.
- **В7 (Б33 и трек S).** Атрибуцию Б33 (сохранение кэша пайплайнов, 5 из 6 сохранений в кадре ≥ 100 мс) передать звену S1/S2 как вход или вести итерацией F?
- **В4 (окно входа новых уровней).** Кадры срабатывания BVH лежат в окне входа (первые 10 кадров после первого кадра сцены); по п. 218(г) K3 в окне —
  только выше тёплой базы, а её для 10 новых уровней нет. Считаю K3 по букве «`dt` ≥ 100 мс» с пометкой «тёплой базы нет»; вариант исполнителя — второй вход
  тех же уровней как тёплая база до любой правки (10 входов по 120 с).
- **В5 (сцены [c] у Б26, Ф3, Ф5, Ф7).** Ключ 2 посчитан по всем 19 именам из строки входа, включая проходные (`ps_logo`, `title_controller_ship`, `worldmap`,
  `transition_next`); при счёте только уровней `-lvl` — 15. Порядок строк от этого не меняется.
- **В8 (правило 27).** Комментарий лида от 23:59:00Z (правило 27, строки Б33/Б34) замечен в 00:29Z, перед сдачей: команды 23:59–00:29Z шли без первой
  строки проверки замка; замок отсутствовал при каждой сделанной проверке, свип ждёт замок внутри (`wait_gate`). Пропуск чтения комментариев — мой.
- **В6 (коммит).** Граница роли Lever Researcher — «не коммитишь»; общие правила трека F называют коммит. Файлы положены в рабочее дерево
  (`docs/track-f/register.md`, `docs/track-f/f0/`), коммит не сделан — оставлен приёмке, как в с. 141. `sig_f0.tsv` и `agg_f0.json` в git не кладутся:
  в примерах строк старых логов есть путь с именем пользователя.

## 8. Сверка

**Суммы пересчитаны: 33 из 33; порядок ключей 1–3 проверен скриптом: да.** Ссылок на git по якорю: 82, контроль +1 — 82 `NOT OK`; ссылок на локальные файлы (логи, `FACTS.md`) по якорю: 18 из 18, у 2 соседняя строка повторяет якорь (повтор строки лога), sha256 файлов — в карте.
Проверки (`mk_register.py`, `assert` на каждую): inventory rows located by anchor: 32; local references by anchor: 18 of 18; unique logs by band sum = unique logs; aggregated = unique + duplicates; s142 logs = 12; s128+ = bands 128-141 + 142; B7: no other opcode family in any log; B9 marker "=== Stubbed function": 0 logs; [Vulkan][E] last session < 113; s142 census logs = 10; B5 form on s142 census = 7 of 10; B5a form on s142 census = 0 of 10; skipped draw on s142 census = 10 of 10; BvhLoopCapTrip on s142 = 2 levels; K3 on hold on s142 census: 3 logs, 4 frames; s142 stalls after the first scene frame all inside frames >= 100 ms; death markers on s142 = 0 of 12; [Vulkan][E] on s142 = 0; stub called on s142: 1 log (timestop_casino); profile 96/1/4 on s142 = 12 of 12; profile counts sum = logs with any opcode line; row ids unique; every open inventory row K1-K4 (24) is in the register; every inventory row K5 (7) is in the register; inventory rows: 24 + 7 + closed B3a = 32; lead rows B32, B33, B34 are in the register; course line 142 (p.231(zh)) reproduced: K1 2 / K2 1 / K3 6 / K4 17 / K5 7 = 33; rows = inventory 31 + lead 3 + new; class sums = rows; defect + observation + out-of-track = rows; ranking order by keys 1-3; signature table rows = SIGS; mid-level pipeline cache saves on s142 (no validation): 6, of them 5 in a frame >= 100 ms.

## 9. Не заявляется

Что реестр полон: свип видит только строки с ключевыми словами `KEY` (регистр учитывается), логи в каталогах фикстур не читались, 104 уровня из 114 входили
не больше одного раза или не входили, звук и ввод логами не покрыты; что какая-либо строка исправима; что какое-либо наблюдение безвредно; что
неисполняемые опкоды меняют или не меняют картинку; что шейдеры Б26 не диспатчатся вне просмотренных 120–334 с одиннадцати уровней; что кадр ≥ 100 мс
с сохранением кэша вызван только сохранением (в 3 из 4 прочитанных интервалов есть и трансляция); что срабатывание ограничителя BVH портит или не портит картинку;
что «с. 128+» — ровно `9235a7ac`; что правка чего-либо ускоряет игру; 60 FPS; корректность любой сцены и `SCENE_OK`.

## 10. Строки закрытия с. 143 (автор — лид, `HPP-301`; решение `ROADMAP.md` «СЕССИЯ 122» п. 254(г), KytyPS5 `d3a8d951`)

Разделы 0–9 — документ звена F0 (Lever Researcher), не правятся. Этот раздел — строки (Б) закрытия с. 143 по классам; данные — `C:/kyty/s143/step4/summary143_viewed.txt`
(sha256 `57621ed2…`), `docs/session-143/audit/AUDIT143.md` (`d31de12b`). Сборка — `9235a7ac`. Строки, которых нет в разделе 4, — новые; строка Б5а меняет класс.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | механизм по коду `4fc501f4` | сцены [c] | t / p | нужна игра | нужен пользователь | без игры | критерий доказательства | P(FIXED ≤ 2 итерации) [I] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Б35 (новая) | K4 на отгруженных умолчаниях (без валидации драйвер пайплайн принимает, видимое следствие не показано [U]); под валидацией — остановка до игры | дефект (путь исполняется [c]) | графический пайплайн с dual-source blend (`SRC1_ALPHA` / `ONE_MINUS_SRC1_ALPHA`) создаётся без включённой возможности устройства `dualSrcBlend` | открыт; итерация **F4** трека F (п. 254(ж)); до отгрузки — форма W `KYTY_PIPELINE_PRECACHE=0` (п. 254(е)) | 10 из 10 W `sc143`: `[Vulkan][E]` `vkCreateGraphicsPipelines(): … srcColorBlendFactor (VK_BLEND_FACTOR_SRC1_ALPHA) is a dual-source blend factor, but dualSrcBlend feature was not enabled` до первой строки `GuestOut`; запись № 1592 `_ShaderCache/PPSA21564/pipelines.bin` (VS `e234ee6bc9c2fb00`, PS `5514e10f1a60df83`), внесена прогоном `c142_04` (`mini_giants_garden`) после строки входа (AUDIT143 §2 (2)–(3)) | `4fc501f4:src/graphics/presentation/window/vulkanWindow.cpp:638` «vk::PhysicalDeviceFeatures device_features {};» (возможность не включается); `4fc501f4:src/graphics/host_gpu/renderer/pipeline/shaders.cpp:260` «eSrc1Alpha»; создание на старте — `4fc501f4:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5845` «bool PipelinePrecacheEnabled()» (precache по умолчанию) | 1 (`mini_giants_garden` создаёт [c]); остальные [U] (Д-3) | на старте / 1 при precache и валидации | да | нет | частично (сборка, тесты) | п. 254(ж)(2): W Sky Garden с валидацией и precache по умолчанию `KYTY_FIX_DUALSRC=1` — `GuestOut`, ≥ 310 с, 0 `[Vulkan][E]`; контроль `=0` останавливается тем же текстом; W `mini_giants_garden` `=1` ≥ 310 с, 0 `[Vulkan][E]`; V `mini_giants_garden` `=1` ≥ 330 с, видео 0 глитчей, лист лида, без новых K1/K2; `shader_cfg_tests` прежний список | 0,6 |
| Б36 (новая) | K2 (на удержании) | дефект (происхождение [U]) | кадр 6 614 314 мкс на удержании `pot_treasure_cave` после 120 с показанного времени (форма `edes122`, п. 242(в)) | открыт; повтор — пара `v144_10`/`w144_10` `sc144` (п. 254(к)) | `v143_08` n 14 701 (`C:/kyty/s143/log_v143_08.txt`, sha256 `88d81bd41fe0…`); в том же прогоне `PriorityStall:` max 6 607 732 мкс — одна ли причина [U] | не назван | 1 | ≈ 300 с [I] / 1 из 1 входа уровня, 1 из 10 V `sc143` | да | нет | нет | сначала p: ≥ 2 удержания уровня ≥ 330 с на `9235a7ac`; на сборке правки N ≥ ln 0,05 / ln(1 − p) удержаний без кадра ≥ 1 с | [U] |
| Б5а (смена класса) | **K2 (на входе)**; было K4 (п. 231(д)) | дефект; ведёт трек S | кадр ≥ 1 с после первого кадра сцены холодного первого входа | открыт, трек S; основание K4 («0/10 ≥ N = 8») опровергнуто воспроизведением на `9235a7ac` | вариант 120 с (п. 242(в)): с. 143 — 1 из 10 (`v143_07` `rocket_hourglass` n 280, 1 780 488 мкс, `C:/kyty/s143/log_v143_07.txt` sha256 `03999be4890b…`); пул с с. 142 — 1 из 20 | как в разделе 4 | 1 на `9235a7ac` (`rocket_hourglass`) | второй кадр после первого кадра сцены / 0,05 по пулу | да | нет | нет | при p = 0,05 — N = 59 холодных входов (дорого); на `rocket_hourglass` холодном p = 1 из 1 — стенд холода трека S, N ≥ 2 | — |

Формы на установленной сборке (п. 254(г)(4)–(5)) [c]: Б5 — 9 из 10 (пул с с. 142 16 из 20); Б33 — 4 из 10 по букве п. 221, 3 из 10 по варианту 120 с (пул 7 из 20);
Б1б (`BvhLoopCapTrip:`) — 0 из 10; Б3б (`PriorityStall:` > 50 мс) — 10 из 10 V; Б26 (профиль 96/1/4) — 10 из 10 V; Б9 (`=== Stubbed function`) — 0. Классы этих строк не меняются.
Открытых дефектов после закрытия с. 143 — 35: K1 2 / K2 3 / K3 6 / K4 17 / K5 7 (п. 254(з)). Не заявляется: что пайплайн Б35 рисуется верно или неверно; что уровни
`sc143` его используют; что K2 Б36 и `PriorityStall:` — одна причина; что реестр полон.

## 11. Строки приёмки F2d (автор — лид, `HPP-311`; решение `ROADMAP.md` «СЕССИЯ 122» п. 259(а), (в))

Данные — серия F2c (`C:/kyty/f287/f2c/log_f2c_{a,b,c}.txt`, sha256 `7ee3f092…`, `b85553e5…`, `1c731fbb…`; пересчёт лида `C:/kyty/f287/lead/f2d_chk.out.txt`
`09febdd5…`), отчёт F2a `docs/track-f/f2a/f2a-b26b.md`, проект F3a `docs/track-f/f3a-b1b.md` (`74d3e2ca…`) §8. Бинарь правки — `5821482a`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б26а | K4 | наблюдение | `S_SWAPPC_B64` (SOP1 `0x21`, 96 шейдеров) | `ТУПИК` (п. 237(в)(2)); переоткрытие в F2c — 0 / 0 / 0 | `f2d_chk.out.txt` | — | переоткрытие п. 237(в)(2) |
| Б26б | K4 | наблюдение | `S_BREV_B64` (SOP1 `0x0c`, 1) и `V_CMP_LE_U64` (VOPC `0xe3`, 4) | **`FIXED`** (п. 259(а); счёт трека F, не отгрузка под (B)); ручка `KYTY_FIX_B26`, умолчание 1; установка — бинарём отгрузки трека F (п. 259(б)) | при `=1` профиль 96 / 0 / 0 (+ `0xf3` 4), при `=0` 96 / 1 / 4; правило п. 256(а) 5 из 5 | `underwater_aerial_garden` | — |
| Б26в (новая) | K4 (при запросе — K1) | наблюдение (путь не исполняется [c]) | VOPC `0xf3` `V_CMPX_LE_U64` — по одной в 4 шейдерах Б26б (`433e4ced…` pc `0xc0`, `f8e35038…` `0xfc`, `4468d530…` `0x294`, `7bb50479…` `0x324`) | открыт; очереди нет до сцены-свидетеля | `log_f2c_a.txt`, строки `CsPretranslate: skipped` четырёх хэшей | 0 (не запрошены) | сцена-свидетель — строка `CsPretranslate: miss|hit` с одним из 4 хэшей |
| Б26г (новая) | K4 (при запросе — K1) | наблюдение (путь не исполняется [c]) | `57c4d5848e02ecdc`: `ResourceTracking.cpp:173 … pc=0x1a0 GetBufferResource dword 1 is not a valid runtime value` (дескриптор `s[16:19]`) | открыт; очереди нет до сцены-свидетеля | `log_f2c_a.txt`; F2a §1 | 0 (не запрошен) | как Б26в |
| Ф9 (новая) | K4 | **дефект** (путь исполняется [c], п. 237(б) В2) | `IMAGE_BVH_INTERSECT_RAY` читает узлы по `(адрес >> 8) + смещение` — база дескриптора BVH (40 бит в единицах 256 байт, PAL `gfx9Device.cpp:5334`) берётся без сдвига | открыт; итерация **F3** вместе с Б1б (критерий п. 259(е)) | пары промахов «X / X>>8»: 11 из 12 логов с. 142, 285 из 286 логов Sky Garden с. 103–142 (F3a §1, §4) | 11 уровней [c]; все сцены с трассировкой [I] | п. 259(е) |
| Ф10 (новая) | K4 | наблюдение (путь станет исполняемым после Ф9 [I]) | треугольные узлы типов 2–3 → «нет попадания»; поле `size` не проверяется; `S_TRAP` — пустая операция | открыт; в F3 не смешивается | F3a §8 | 0 | после F3 |

Дельта к строке курса 144 (п. 237(ж)): K4 −1 (Б26 закрыта: Б26а `ТУПИК`, Б26б `FIXED`), K4 +4 (Б26в, Б26г, Ф9, Ф10); пересчёт — закрытие с. 144 скриптом.
Не заявляется: что 5 шейдеров Б26б переводятся; что Б26в/Б26г достижимы игрой; что Ф9 меняет картинку видимо; что реестр полон.

## 12. Строки закрытия с. 144 (автор — лид, `HPP-334`; решение `ROADMAP.md` «СЕССИЯ 122» п. 273(г)–(е))

Данные — `C:/kyty/s144/step4/summary144_viewed.txt` (sha256 `52dca9e3…`), `docs/session-144/audit/AUDIT144.md` (`c1cd9272…`, §1.3, §2), счёт курса —
`C:/kyty/s144/step4/course144.py` (вывод `course144.out.txt`, `ALL OK`). Сборка — `9235a7ac`. Строки Б37, Б38 — новые.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | механизм по коду `4fc501f4` | сцены [c] | t / p | нужна игра | нужен пользователь | без игры | критерий доказательства | P(FIXED ≤ 2 итерации) [I] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Б37 (новая) | K4 на отгруженных умолчаниях (без валидации исход [U]: неуспех `vkCreateSwapchainKHR` — `EXIT`, это K1); под валидацией — остановка | дефект (путь исполняется [c]) | пересоздание swapchain при нулевом размере окна (свёрнуто): `currentExtent` 0×0 берётся без проверки и без ожидания | открыт; итерация **F5** трека F (п. 273(е)) | `C:/kyty/s144/log_w144_09.txt` (sha256 `08c3a71f…`): `Window 1 minimized` (байт 288 006 876) → `vkQueuePresentKHR … eErrorOutOfDateKHR` → `Recovering Vulkan swapchain` → `[Vulkan][E] vkCreateSwapchainKHR(): pCreateInfo->imageExtent (width = 0, height = 0) is invalid` (VUID-VkSwapchainCreateInfoKHR-imageExtent-01689); путь `RecoverSwapchain` в 991 логе исполнен 1 раз — с ошибкой (AUDIT144 §2) | `4fc501f4:src/graphics/presentation/window/swapchain.cpp:402` «m_extent = surface.capabilities.currentExtent;»; `window.cpp:466–468` (событие только пишется) | любая (событие окна); `rocket_hourglass` [c] | p = 1 на свёрнутом окне [c, 1 из 1] | да (стенд) | нет (стенд `KYTY_TEST_MINIMIZE`) | частично (сборка, тесты) | п. 273(е)(3): W Sky Garden `KYTY_FIX_MINIMIZE=1` со стендом 60:10 — 0 `[Vulkan][E]`, ≥ 310 с, ≥ 1 000 кадров после `restore`; контроль `=0` — VUID-01689; V `=1` со стендом — ≥ 330 с, видео 0 глитчей вне окна сворачивания, лист; V `=0` со стендом — исход (класс); `shader_cfg_tests` прежний список | 0,7 |
| Б38 (новая) | K5 (инструмент доказательства) | вне трека (п. 228(а)) | запись видео `KYTY_REC` теряет показанные кадры сразу за первым кадром сцены холодного входа | открыт; очереди нет; мера — строка непрерывности скорера `sc145` (п. 273(к)(3)) | `vidcont144.out.txt` AUDIT144 §1.3: 7 из 8 V с. 143 пар `YES` — серии 6–34 строк `FrameTrace` без записи в `.idx` (до 2,18 с, `v143_10` n 390…423); `v143_07` 135, `v143_08` 17; 12 V с. 144 (повторный вход) — серий ≥ 2 строк нет | не назван ([I] очередь кодировщика под нагрузкой первого кадра) | 9 холодных V с. 143 | первый кадр сцены / ≈ 0,9 на холодном входе [c, 9 из 10] | да | нет | нет | правка записи и серия холодных входов без серий ≥ 2 строк без записи | [U] |

Изменения строк (п. 273(г)(3)–(5)) [c]: **Б36** — удержаний `pot_treasure_cave` ≥ 330 с на `9235a7ac` 2, K2 1 ⇒ p = 0,5, на сборке правки N = 5 удержаний без
кадра ≥ 1 с; **Б5а** — повторный вход `rocket_hourglass` без K2 (в пул холодных не идёт); **Б35** — `mini_giants_garden` создаёт пайплайн в игре без precache
(`w144_20`, 0,335 с после строки входа), 18 уровней пар с. 144 за 310 с W — не создавали. Классы прочих строк не меняются.

**Строка курса 144 (скриптом, п. 273(д)):** открытых 39 — K1 2 / K2 3 / K3 7 / K4 19 / K5 8, из них дефектов по п. 228(б) — 15. Счёт применяет п. 237(б) (Б1б → K3,
Б3б → `НЕ ДЕФЕКТ`), которого не было в строке 143 (35 напечатано, 34 по счёту). Не заявляется: что без валидации свёрнутое окно ведёт к крэшу или не ведёт; кто
свернул окно; что видео холодных V показывает первые секунды сцены; что реестр полон.

## 13. Строки приёмки F3c (автор — лид, `HPP-341`; решение `ROADMAP.md` «СЕССИЯ 122» п. 277(в))

Данные — отчёт F3c `docs/track-f/f3c-review.md` (KytyPS5 `225fe16d`) §(6), отчёт F3b `docs/track-f/f3b.md` (`d10b5b7f`). Код — `478868b5`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф11 (новая) | K4 | наблюдение (путь не исполняется [c]: BVH64 0 из 60 инструкций 20 программ) | нативный путь (`KYTY_BVH_NATIVE=1`) считает `IMAGE_BVH64_INTERSECT_RAY` с константным нулём старшего слова указателя узла 32-битным: база T# + смещение (после F3b при `KYTY_FIX_B1B=1` — `(поле << 8) + смещение`); IR-путь берёт указатель без базы; расхождение путей было и до F3b | открыт; очереди нет до сцены-свидетеля | `478868b5:src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp:2144` (`node64`); F3c §(6) | 0 | при сцене-свидетеле — проект по PAL (режим raw VA, `gfx9Device.cpp:5340`) |

Дельта к строке курса: K4 +1 (наблюдение); пересчёт — закрытие с. 145 скриптом. Не заявляется: что Ф11 достижима игрой; какой из двух путей верен.

## 14. Строки приёмки F5b (автор — лид, `HPP-356`; решение `ROADMAP.md` «СЕССИЯ 122» п. 280(ж))

Данные — отчёт F5b `docs/track-f/f5b-review.md` (KytyPS5 `1c9427c8`) RC1, код `d2811535` (`swapchain.cpp:948–1019`, `screenshot.cpp:324–399`).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф12 (новая) | K5 (инструмент доказательства) | дефект (путь исполняется при `KYTY_REC` и восстановлении swapchain [c-код]) | кольцо записи видео `KYTY_REC` (3 слота) рассинхронизируется, если после `Record` present не удался: на пути `=0` — выход `retry exhausted` без `Finish` и повторный `Record` попытки 1 после восстановления; при `KYTY_FIX_MINIMIZE=1` — также сброс нулевого extent (RC1 F5b); дальше каждый третий кадр видео — на 3 present позже | открыт; при `=1` закрывается правкой F5a2 (п. 280(г)); путь `=0` — очереди нет | `d2811535:src/graphics/presentation/window/swapchain.cpp:982–1019`, `screenshot.cpp:331–336`, `:374–381`; трасса F5b RC1 [c-код, прогона нет] | 0 [c] (видео с эпизодом восстановления не записывалось) | непрерывность `.idx` после эпизода (п. 280(е)(1)); связь с Б38 — [U] |

Дельта к строке курса: K5 +1; пересчёт — закрытие с. 145 скриптом. Не заявляется: что Ф12 испортила какое-либо прошлое видео; что Ф12 — причина Б38.

## 15. Строка приёмки F4d (автор — лид, `HPP-338`; решение `ROADMAP.md` «СЕССИЯ 122» п. 281(а), (д))

Данные — серия F4c (`C:/kyty/f287/f4c/log_f4c_{b,a,v,g}.txt`, sha256 `24296558…`, `1184c6f1…`, `f9a9bab1…`, `c1967519…`; пересчёт лида
`C:/kyty/f287/lead/f4d_chk.out.txt` `026c5acd…`), отчёт `docs/track-f/f4c.md` (KytyPS5 `9a3de197`), отчёты F4a2/F4b2. Бинарь правки — `c9a5e198`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б35 | K4 на `9235a7ac` (до установки бинаря отгрузки) | дефект | dual-source blend без `dualSrcBlend` (§10) | **`FIXED`** (п. 281(а); счёт трека F); ручка `KYTY_FIX_DUALSRC` — включает `dualSrcBlend` и переписывает выход PS `Location 1` → `Location 0 Index 1` у пайплайнов с SRC1-фактором; умолчание 1 и установка — бинарём отгрузки трека F (п. 259(б), 281(в)); отгрузка под (B) — при установке | (а) W Sky Garden `=1` с precache по умолчанию 324,5 с, 0 `[Vulkan][E]`; (б) `=0` — остановка тем же текстом до `GuestOut`; (в) W `mini_giants_garden` `=1` 316,7 с, 0 `[Vulkan][E]`; (г) V `=1` 332,4 с, видео 19 708 кадров, 0 глитчей, лист лида, новых K1/K2 нет; (д) `shader_cfg_tests` 127 / 1 | `underwater_aerial_garden` (precache), `mini_giants_garden` (игра) | звено отгрузки: пара `mini_giants_garden` на бинаре отгрузки (п. 281(в)(2)) |

Дельта к строке курса: K4 −1 (Б35); пересчёт — закрытие с. 145 скриптом. Не заявляется: что пайплайн Б35 рисуется верно или неверно; что перепись даёт
верную картинку; что реестр полон.

## 16. Строки приёмки F3e (автор — лид, `HPP-343`; решение `ROADMAP.md` «СЕССИЯ 122» п. 282(а), (д)–(з))

Данные — серия F3d (`C:/kyty/f287/f3d/log_f3d_{a1,a2,a3,a4,bv,bw,c1,c2}.txt`; пересчёт лида `C:/kyty/f287/lead/f3e_chk.out.txt` `922b115e…` с sha256 логов),
отчёт `docs/track-f/f3d.md` (KytyPS5 `5f716839`), отчёты F3b/F3c. Бинарь правки — `2e6df8f0` (код `478868b5`).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б1б | K3 (п. 237(б)) на `9235a7ac` (до установки бинаря отгрузки) | дефект | срабатывание ограничителя BVH (§4) | **`FIXED`** (п. 282(а); счёт трека F); причина срабатываний — Ф9; ручка `KYTY_FIX_B1B`, умолчание 1; установка — бинарём отгрузки трека F (п. 282(г)) | при `=1` строк `BvhLoopCapTrip:` 0 на 6 входах (`big_hand_pirate_island` ×2, `voxel_world` ×2, Sky Garden V и W); маркеров смерти 0, K2 0; видео 3 454 / 7 510 / 8 574 кадров, 0 глитчей, листы лида | `big_hand_pirate_island`, `voxel_world`, `underwater_aerial_garden` | переоткрытие — строка `BvhLoopCapTrip:` на бинаре с `=1` (п. 282(д)) |
| Ф9 | K4 на `9235a7ac` | дефект | `IMAGE_BVH_INTERSECT_RAY` читает узлы по `адрес >> 8` (§11) | **`FIXED`** (п. 282(а)); та же ручка и отгрузка, что Б1б | пары «X / (X>>8)&~0x3fff» при `=1` — 0 на 6 входах, при `=0` — 1 и 2; низких страниц при `=1` 0; 20 BVH-программ, форма `X >> 8` у 60 из 60 инструкций (F3b §1) | 3 | — |
| Б1а | K4 | дефект, закрытый ограничителем | зависание обхода BVH без предела шагов (§4) | форма снята умолчанием `KYTY_BVH_LOOP_CAP` (остаётся включённым); после Ф9 срабатываний 0 на 6 входах [c]; без ограничителя — не проверялось; серия 34 входов не назначается (п. 282(д)) | `f3e_chk.out.txt` | — | переоткрытие — как Б1б |
| Ф10 | K4 | наблюдение (путь достижим после Ф9 [I], исполнение [U]) | треугольные узлы типов 2–3 → «нет попадания»; `size` не проверяется; `S_TRAP` — пустая операция (§11) | открыт; очередь F после F6 — первым (п. 282(е)) | страниц промахов Sky Garden при `=1` — 36 [c] (против 4 прежних логов — по отчёту F3d) | 0 | проект со счётчиком типов узлов и проверкой `size` на настоящих данных |
| Б9а | K4 | дефект (путь исполняется [c]) | 4 неразрешённых импорта `AudioPropagation` (§4) | итерация **F6** (п. 282(ж)): F6a — проект (имена NID, сигнатуры, места вызова, вариант правки, критерий) | §4 | `timestop_casino` | критерий — п. F6b до кода |

Дельта к строке курса: K3 −1 (Б1б), K4 −1 (Ф9); пересчёт — закрытие с. 145 скриптом. Не заявляется: что трассировка верна; что Ф10/Ф11 недостижимы;
что без ограничителя обход конечен; что реестр полон.

## 17. Строки приёмки F6a (автор — лид, `HPP-373`; решение `ROADMAP.md` «СЕССИЯ 122» п. 287(б), (г))

Данные — проект F6a `docs/track-f/f6a-b9a.md` (KytyPS5 `bed17fc0`), пересчёт лида `C:/kyty/f287/lead/f6b_chk.out.txt` (`dc39c4c9…`, `F6B RECOUNT ALL OK`).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б9а | K4 | дефект (путь исполняется [c]) | 16 неразрешённых импортов `AudioPropagation` из 22 (6 — HLE), вызываются 4: `PortalCreate`, `PortalSetAttributes`, `SourceCreate`, `SourceGetAudioPathCount`; игра читает незаписанные handle ⇒ создание источника повторяется каждый кадр (1,53 на кадр), пути источника спят | открыт; итерация **F6** — V1 (16 функций, согласованное «пустое» состояние) под `KYTY_FIX_B9A` (умолчание 0 до отгрузки) | `C:/kyty/s142/log_c142_03.txt:239572`; F6a §1, §3, §4 | `timestop_casino` (3 из 3 логов), `mini_astro_clock_tower` (2 из 2) | п. 287(в) |
| Б9б (новая) | K4 | наблюдение (слышимость [U]) | распространение звука не рендерится: `SourceRender` и расчёт путей пустые, вклад в шину 0 — до и после V1 | **`ТУПИК`** по п. 228(д): первоисточника (заголовков SDK, модуля `libSceAudioPropagation`) нет, проверка слышимого требует пользователя, замены нет; переоткрытие — первоисточник или решение лида о «сухом» `Render` (V2) с проверкой слушателем | F6a §3 (подмешивание `0xf52921`, `0xf44dc4`), §5 | те же | — |
| Ф13 (новая) | K5 (инструмент доказательства) | дефект | поле `stubs` скореров `sc142`–`sc144` не считает строки `Unresolved import stub called` (65 файлов пусто при 5 логах с вызовами [c]); печать заглушки молчит после 1 024 вызовов на процесс | открыт; правка — скорер следующей серии сессии (вход закрытия с. 145) и скорер F6e | F6a §4 | — | п. 287(б)(7) |

Дельта к строке курса: K4 +1 (Б9б), K5 +1 (Ф13); пересчёт — закрытие с. 145 скриптом. Не заявляется: что звук верен; что 12 невызванных функций не вызываются
на других уровнях; что реестр полон.

## 18. Строка приёмки F6d (автор — лид, `HPP-376`; решение `ROADMAP.md` «СЕССИЯ 122» п. 294(д))

Данные — ревью F6d `docs/track-f/f6d-review.md` (KytyPS5 `f1455635`) §3, счёт лида `C:/kyty/f287/lead/f6d_chk.out.txt` (`596a4a84…`).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф14 (новая) | K5 (инструмент доказательства) | дефект | assert игры и ветки ошибки `sce… failed` процесс не роняют: `0x1aa0` печатает `ASSERT:`, открывает `MsgDialog`, HLE отвечает OK сразу ⇒ `int 0x41` не исполняется; скореры `sc142`–`sc145`, F3d, F4c строк `ASSERT:` и `user_msg_param` не считают — сработавший assert без падения невидим | открыт; правка — поле скорера следующей серии сессии (вход закрытия с. 145, вместе с Ф13) и член п. 294(б) скорера F6e | `5f67f829:src/libs/dialog.cpp:547`, `:571`; `C:/kyty/f287/f6d/dis_1aa0.txt` | 0 с assert в 5 логах свидетелей Б9а и 20 stdout `s142` [c]; остальные [U] | п. 294(б), (д) |

Дельта к строке курса: K5 +1 (Ф14); пересчёт — закрытие с. 145 скриптом. Не заявляется: что assert'ов нет на других уровнях; что реестр полон.

## 19. Строка приёмки F5d (автор — лид, `HPP-358`; решение `ROADMAP.md` «СЕССИЯ 122» п. 298(а), (б), (ж))

Данные — серия F5c (`C:/kyty/f287/f5c/log_f5c_{a,b,v,g}.txt`; пересчёты лида `C:/kyty/f287/lead/f5c_chk.out.txt` `d64f1b45…` (п. 296(б)) и
`f5d_chk.out.txt` `948b5eec…`), отчёт `docs/track-f/f5c.md`, отчёты F5a2/F5b2. Бинарь правки — `6f495a65` (код `d2811535` + `01ca15d1`).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б37 | K4 на `9235a7ac` и на бинаре отгрузки FS (`dac02fb9`, `KYTY_FIX_MINIMIZE=0`) до установки FS2 | дефект | пересоздание swapchain при нулевом размере окна (§12) | **`FIXED`** (п. 298(а); счёт трека F); ручка `KYTY_FIX_MINIMIZE` — при `currentExtent` 0 swapchain не создаётся, present пропускается, пересоздание — после ненулевого extent; умолчание 1 и установка — вторым бинарём отгрузки трека F (FS2, п. 298(в)–(д)); отгрузка под (B) — при установке | (а) W Sky Garden `=1` со стендом 60:10 — 324,5 с, 0 `[Vulkan][E]`, begin/end 1/1, после `restore` 2 039 строк `FrameTrace`; (б) `=0` — остановка VUID-01689 по букве (п. 296(б)); (в) V `=1` — 334,4 с, видео 9 152 кадра, 0 глитчей, лист лида; (г) V `=0` без валидации — путь исполнен (2 `Recovering Vulkan swapchain`), маркеров смерти 0, 334,2 с, `Event: quit` ⇒ K1 не добавляется; (д) `shader_cfg_tests` 127 / 1 (Б11) | `underwater_aerial_garden` (стенд); любая (событие окна) | переоткрытие — `[Vulkan][E]` VUID-01689 или маркер смерти после `Window <id> minimized` на бинаре с `=1`; регрессия умолчания — FS2c (п. 298(г)) |

Дельта к строке курса: K4 −1 (Б37) в счёте трека F; пересчёт — закрытие с. 145 скриптом. Не заявляется: что без правки свёрнутое окно никогда не ведёт к
крэшу (один вход, один драйвер); что правка верна при начальном создании swapchain свёрнутым окном; что реестр полон.

## 20. Строки приёмки FSd (автор — лид, `HPP-371`; решение `ROADMAP.md` «СЕССИЯ 122» п. 300(б), (в), (е))

Данные — серия FSc (`C:/kyty/f287/fsc/log_fs_{a,b,v,g,d}.txt`, выводы ридера `score_fs_*.txt`; приёмка п. 299), отчёт `docs/track-f/fsc.md` (KytyPS5 `8d6b24e4`),
листы `sheetpair_fs_b.png` (`b1604793…`) и `sheetpair_fs_g.png` (`b0b80ee8…`). Бинарь отгрузки — копия `C:/kyty/f287/bin/kyty_emulator_dac02fb9.exe` (коммит
`95eec776`, подпись `56189185`).

| № | статус отгрузки на сегодня | основание |
|---|---|---|
| Б26б, Б1б, Ф9, Б35 | бинарь отгрузки `dac02fb9` принят к установке (п. 300(б)); установка — шаг 0 цепочки с. 146 (не раньше `done` `HPP-354`); отгрузка под (B) — при установке; до неё на `9235a7ac` поведение прежнее | FSc PASS по п. 282(г)(3) (п. 299(а)); листы лида (п. 300(а)) |
| Б37 | K4 на `dac02fb9` (`KYTY_FIX_MINIMIZE=0`, п. 286(в) N2); умолчание 1 — бинарём FS2 (п. 298) | — |

`SCENE_OK` `mini_giants_garden` — ДА на `dac02fb9` (п. 300(в)), в строку курса — с установкой. Новых строк нет. Не заявляется: что картинка пайплайна Б35
верна; что 18 `SCENE_OK` `sc144` держатся на `dac02fb9`; что реестр полон.

## 21. Строки закрытия с. 145 (автор — лид, `HPP-354`; решение `ROADMAP.md` «СЕССИЯ 122» п. 309(е), (ж))

Данные — `C:/kyty/s145/step2/summary145.txt` (sha256 `159f3b6f…`), листы и кадры лида `C:/kyty/s145/step4/hud/`, `docs/session-145/audit/AUDIT145.md`
(`8a13bd18…`, §1.3, §1.4, §4), счёт курса — `C:/kyty/s145/step4/course145.py` (вывод `course145.out.txt`, `ALL OK`). Сборка — `9235a7ac`. Строки Б39, Б40 — новые.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | t / p | критерий / очередь |
|---|---|---|---|---|---|---|---|---|
| Б39 (новая) | K4 (картинка; сцена держится) | наблюдение (кандидат дефекта картинки; эталона нет [U]) | пол арены `enemy_final` на всём удержании — плоская светло-голубая заливка без текстуры, деталей и швов; тень Астро на полу есть | открыт; итерация **F7** трека F — диагностика после F6 (звенья создаёт F6f `HPP-378`) | лист `C:/kyty/s145/sheet_v145_17.png` (`ead1294d…`), полные кадры 300 и 10 000 `rec_v145_17.mp4` (`step4/hud/v17_frames.png`); W `w145_17` — 0 `[Vulkan][E]` | `enemy_final` | все кадры удержания `v145_17` | F7: снимок RenderDoc кадра арены (Harness Engineer под замком) и разбор draw пола (Emu Engineer: привязанные образы, чтение в PS, выход цели) → «дефект — критерий до кода» или `НЕ ДЕФЕКТ` (тогда `SCENE_OK` `enemy_final` — строкой закрытия) |
| Б40 (новая) | K2 (на удержании) | дефект (происхождение [U]) | кадр 4 624 510 мкс на удержании `bonus_path_maker_mix` (n 7249, 142,8 с после первого кадра сцены, вне 120 с); K3 рядом — n 7188 (305 805 мкс), n 7216 (101 547 мкс); `PriorityStall > 50 ms` 2 (макс. 92 213 мкс); маркеров смерти нет; строки окна в ± 2 с нет | открыт; «сначала p» (как Б36): второе удержание V ≥ 330 с на установленном бинаре — тег `r146_04` с. 146 (п. 309(л)(2)) | `C:/kyty/s145/log_v145_14.txt` (`d7ed7266…`), `score_v145_14.txt`; W `w145_14` того же уровня — 310 с, 0 `[Vulkan][E]` | `bonus_path_maker_mix` | p = 1 из 1 [c] | после p: N ≥ ln 0,05 / ln(1 − p) удержаний без кадра ≥ 1 с на сборке правки |

Изменения строк [c]: **Б38** — текст «сразу за первым кадром сцены холодного входа» заменяется на «в любом месте удержания холодного V» (Д-3 аудита с. 145): серии
без записи позже первого кадра сцены — `v145_16` n 999–1050 (52 строки, 1,48 с), `v145_11` n 1687–1703, `v145_02` n 483–498, `v145_14` у кадра K2; самая длинная —
`v145_08` 105 строк (2,08 с); мера — строка непрерывности скорера (не гейт). **Б5а** — холодных входов с. 145 по пулу аудитора 13, форма 1 из 13; **Б5** 9 из 13;
**Б33** 4 из 13; классы не меняются. **Б36** — без изменений (p = 0,5). **Б9б** — рождена `ТУПИК` (§17): по правилу счёта п. 309(ж) в открытые не идёт (дельта
«K4 +1» §17 исправлена). Однокадровые события вставки HUD `final_stage` (AUDIT145 §1.4) — анимация игры (спрайт выстрела через ≈ 4 кадра, п. 309(б)); строки нет.

**Строка курса 145 (скриптом, п. 309(ж)):** открытых 41 — K1 2 / K2 4 / K3 6 / K4 18 / K5 11, из них дефектов по п. 228(б) — 15; на установленной `9235a7ac`
ещё действуют `FIXED` трека F Б35, Б1б, Ф9, Б37 (и Б26б) — до установки бинаря отгрузки `dac02fb9` шагом 0 с. 146 (Б37 — бинарём FS2): на ней 45 — 2 / 4 / 7 / 21 / 11.
Не заявляется: что пол `enemy_final` неверен или верен; причина K2 Б40 и связь с Б36 или `PriorityStall:`; что видео показывает кадры без записи; что реестр полон.

## 22. Строки закрытия с. 146 (автор — лид, `HPP-390`; решение `ROADMAP.md` «СЕССИЯ 122» п. 324(е), (ж))

Данные — `C:/kyty/s146/step4/summary146_viewed.txt` (sha256 `352535d2…`), `C:/kyty/s146/step2/summary146.txt` (`18b3030d…`), листы лида
`C:/kyty/s146/sheet_<тег>.png` и кадры `step4/vid/`, `docs/session-146/audit/AUDIT146.md` (`8b08bb00…`, §1.2–§1.4, §4), счёт курса —
`C:/kyty/s146/step4/course146.py` (вывод `course146.out.txt` `c649d4b8…`, `ALL OK`). Сборка — установленная `dac02fb9` (шаг 0 с. 146, п. 300(б)).
Строки Б41, Ф15 — новые.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | t / p | критерий / очередь |
|---|---|---|---|---|---|---|---|---|
| Б41 (новая) | K4 (картинка; сцена держится) | наблюдение (эталона нет [U]: игра может ждать ввода) | сцена `ending_boss_after_credit`: ≈ 20 с карточки «THE END» с героями, затем чёрный экран до конца удержания (V и W); `draws` медиана 912 → 22 на кадр; 19 494 неподвижных кадра из 20 148; слой валидации W молчит с 17,2 с (п. 317) | открыт; очередь трека F — после Б39 (F7) | лист `C:/kyty/s146/sheet_v146_08.png` (`0fd2fee5…`, 45 из 48 клеток чёрные); `log_v146_08.txt` (`036970e7…`), `log_w146_08.txt` (`7d94bcf6…`); AUDIT146 §4 (3) | `ending_boss_after_credit` | всё удержание после ≈ 20 с | эталон картинки после карточки без ввода или снимок RenderDoc кадра и разбор draw (как F7) → «дефект — критерий до кода» или `НЕ ДЕФЕКТ` |
| Ф15 (новая) | K5 (инструмент доказательства) | дефект | запись видео `KYTY_REC` не закрывается (последний `mdat` за концом файла), когда харнесс снимает процесс эмулятора по таймауту попытки; счёт кадров контейнера, декодера и `.idx` расходится, лист — по оборванному файлу | открыт; правка — в харнессе серии возобновления (штатный выход эмулятора до снятия или ожидание закрытия записи), владелец — Harness Engineer звеном серии | `rec_v146_09/11/12/13.mp4` (AUDIT146 §1.3: 10 расхождений на четырёх видео), `rec_v145_06.mp4` (AUDIT145 §1.3) | теги с исходом попытки `timeout` | 5 из 5 видео тегов `timeout` (с. 145–146) | читать так: исход тега от видео не зависит; листы и счёт кадров таких тегов — справка |

Изменения строк [c]: **Ф13** — `timestop_casino` (`r146_03`): 1 024 строки `Unresolved import stub called` в логе и в stdout — ровно предел печати заглушки на
процесс, реальное число ≥ 1 024; у 34 прочих тегов серии 0. **Б40** — второе удержание `r146_04` (`dac02fb9`, холодный по каталогу варианта) 332,0 с без
кадра ≥ 1 с ⇒ **p = 1 из 2** [c]; пара неоднородна (сборка и холодность). **Б5а** — кадр ≥ 1 с на холодном входе у 3 из 19 первых входов уровней на
`dac02fb9` (`r146_02` 1 771 238 мкс, `r146_03` 1 844 729 мкс, `v146_10` 1 349 855 мкс); **Б5** 5 из 15, **Б33** 6 из 15 (пул `v146_*`); классы не меняются.
**Ф14** — `ASSERT:` / `user_msg_param` 0 у 35 из 35. Однокадровые белые кадры вставки титров `non_interactive_credit` (AUDIT146 §1.4) — переход клипов
через белое, анимация игры [I] (п. 324(а)); строки нет.

**Строка курса 146 (скриптом, п. 324(ж)):** открытых 43 — K1 2 / K2 4 / K3 6 / K4 19 / K5 12, из них дефектов по п. 228(б) — 16; на установленной
`dac02fb9` ещё действует Б37 (до FS2) — 44: 2 / 4 / 6 / 20 / 12. Не заявляется: что чёрный экран `ending_boss_after_credit` — дефект или поведение игры;
причина K2 Б40 и Б5а; что видео показывает кадры без записи; что реестр полон.

## 23. Строка приёмки F6f (автор — лид, `HPP-378`; решение `ROADMAP.md` «СЕССИЯ 122» п. 327(в)–(е))

Данные — серия 2 F6e (`C:/kyty/f287/f6e/log_f6e_{a1,a2,b1,c1,c2}.txt`, чтения `score_f6e_*.txt`, сводка `summary_f6e.txt` `95b990e0…`; печать
`pred/03_f6e.md` `69aa023b…`), отчёт `docs/track-f/f6e.md` (KytyPS5 `e1895759`), пересчёт лида `C:/kyty/f287/lead/f6f_chk.out.txt` (`ac719639…`,
`F6F RECOUNT ALL OK`), пары листов `pair_f6e_a2_vs_c142_03.png` (`8c507a8e…`), `pair_f6e_b1_vs_v143_03.png` (`ccda1d92…`). Бинарь правки — копия F6c
`d8756dce` (код `5f67f829`).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б9а | K4 на установленной `dac02fb9` (`KYTY_FIX_B9A=0`) до установки FS2 | дефект | 16 неразрешённых импортов `AudioPropagation` (§17) | **`FIXED`** (п. 327(в); счёт трека F, первая итерация); ручка `KYTY_FIX_B9A` — 16 функций V1, handle ненулевые, `count = 0`, выходы рендера не трогаются; умолчание 1 и установка — бинарём FS2 (п. 327(г)); отгрузка под (B) — при установке | `=1`: `timestop_casino` ×2 и `mini_astro_clock_tower` — 0 строк заглушки, 0 смертей, 0 кадров ≥ 1 с, K3 в пределе, `SourceCreate` 0,0067 / 0,0068 на кадр (было 1,53), пробуждение (`SourceRender` 6 954 / 7 142), `ASSERT:` 0, `user_msg_param` 0, видео 7 363 / 7 339 / 3 968 кадров — 0 глитчей, листы лида без отличий; контроль `=0` — 1 024 строки заглушки, профиль §4 | `timestop_casino`, `mini_astro_clock_tower` | переоткрытие — строка `Unresolved import stub called` с `[AudioPropagation_v1]`, `ASSERT:` или маркер смерти на бинаре с `=1`; регрессия умолчания — члены Б9а FS2c (п. 327(г)) |

Дельта к строке курса: K4 −1 (Б9а) в счёте трека F; на установленной `dac02fb9` до FS2 — без изменений; пересчёт — следующим закрытием сессии скриптом.
Б9б — `ТУПИК` без изменений. Очередь F: **F7 (Б39)** — звенья F7a…F7c (п. 327(е)) → Ф10 → Б11 (+Ф3) → Б4 → Ф5/Ф7; Б41 — после Б39. Не заявляется: что звук верен
или слышимо изменился; что пустые пути равны библиотеке консоли; что проснувшиеся пути не падают на других уровнях; что реестр полон.

## 24. Строки приёмки FS2d (автор — лид, `HPP-384`; решение `ROADMAP.md` «СЕССИЯ 122» п. 338(а)–(е))

Данные — серия FS2c (`C:/kyty/f287/fs2c/log_fs2_{w,w0,v,t,tw}.txt`, сводка `summary_fs2.txt` `ebe132f2…`, печать `pred/01_fs2.md` `a17d520e…`), отчёт
`docs/track-f/fs2c.md` (KytyPS5 `f96c15a1`), пересчёт лида `C:/kyty/f287/lead/fs2d_chk.out.txt` (`ce03a84d…`, `FS2D RECOUNT ALL OK`), листы `sheet_fs2_v.png`
(`4bcef41d…`), `sheet_fs2_t.png` (`95b1dd3d…`). Бинарь FS2 — `bbad499c` (код `9c9d86ae`), **установлен 2026-10-02T21:00:41Z** вместо `dac02fb9`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б37 | — на установленной FS2 (K4 снят) | дефект | пересоздание swapchain при нулевом размере окна (§19) | **`FIXED`, отгружен под (B)** установкой FS2 (п. 338(г), (е)); умолчание `KYTY_FIX_MINIMIZE=1` | FS2c: `fs2_w` (W формы п. 295(б), стенд 60:10) — 0 `[Vulkan][E]`, 323,9 с, begin/end 1/1; `fs2_w0` (`=0`) — остановка VUID-01689 по букве; `fs2_v` — 335,1 с, видео 9 822 кадра, 0 глитчей, лист лида | Sky Garden | переоткрытие — `[Vulkan][E]` с `imageExtent (width = 0, height = 0)` или маркер смерти после `Window 1 minimized` на FS2; откат — п. 329(б) |
| Б9а | — на установленной FS2 (K4 снят) | дефект | 16 неразрешённых импортов `AudioPropagation` (§17, §23) | **`FIXED`, отгружен под (B)** установкой FS2 (п. 338(г), (е)); умолчание `KYTY_FIX_B9A=1` | FS2c: `FixB9a: on` 1, `ASSERT:` 0, `user_msg_param` 0, заглушек `[AudioPropagation_v1]` 0 у `fs2_w`, `fs2_v`, `fs2_t`; `fs2_t` (`timestop_casino`) — 126,9 с, видео 7 703 кадра, 0 глитчей, K3 0, лист лида против `sheet_f6e_a2` | Sky Garden, `timestop_casino` | переоткрытие — §23 |

Дельта к строке курса [I]: на установленной сборке открытые дефекты = счёт трека F (44 на `dac02fb9` → 42 на FS2); пересчёт — скриптом следующего закрытия
сессии. Откат FS2 — копия `C:/kyty/s146/kyty_emulator_dac02fb9.exe` по sha256 или `KYTY_FIX_MINIMIZE=0` и `KYTY_FIX_B9A=0` вместе (п. 329(б)). Не заявляется: что
без правки свёрнутое окно никогда не ведёт к крэшу; что звук верен; что 40 `SCENE_OK` держатся на FS2; что реестр полон.

## 25. Строки приёмки S7 трека S (автор — лид, `HPP-319`; решение `ROADMAP.md` «СЕССИЯ 122» п. 339(е))

Данные — отчёт `docs/track-s/s7-corpus.md` (KytyPS5 `fbd2731c`) §3–§5, база T1 `C:/kyty/s288/s7/t1_base.tsv` (`d4d80994…`, бинарь тестов `949f8e51`,
подпись `56189185…:fixb26:fixb1b`), `rcp_snap0.tsv` (`22e1188d…`), `recdiff_snap0.out.txt` (`5a491e52…`). Строки Ф16, Ф17 — новые.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф16 (новая) | K1-кандидат [U] (только при `--shader-validation true`) | наблюдение | `ValidateShaderSpirv` (`8f6b6be2:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:1342`) проверяет SPIR-V в `SPV_ENV_VULKAN_1_3` без опции `uniformBufferStandardLayout`, которую устройство включает; отказ — `EXIT` трансляции (`:2124`); умолчание лаунчера `shader_validation_enabled = true` (`src/launcher/include/configuration.h:98`); харнессы программы — `--shader-validation false` | открыт; очередь F — после F7 (Б39), до Ф10 | 151 строка `t1_base.tsv` (PS, `identical_stored=1`): `rc_spirv_val_vk13=1`, `rc_spirv_val_dev=0` (`spirv-val` SDK 1.4.357) | — (офлайн; игра с проверкой шейдеров не запускалась) | офлайн-тест встроенного SPIRV-Tools (`3rdparty/SPIRV-Tools` `7f2d9ee`) на 151 выходе базы, без игры и замка: «отвергает» — дефект, критерий до кода пунктом лида; «принимает» — `НЕ ДЕФЕКТ` |
| Ф17 (новая) | K5 (кэш рецептов) | наблюдение | `RecipeWriter::Info()` пишет сырые байты `ShaderComputeInputInfo` с паддингом (смещение 53, между `tg_size_en` и `stage`); дедупликация рецептов по хэшу не снимает дубликаты compute | паркуется до S8 (`HPP-320`): читается вместе с RC9 (недетерминизм рецептов S-cat) | 41 пропуск `R_DUP_CS` на `snap0` (записи 641–681 = `s4/log_g_1.txt:2466`); установленный кэш — 0 пропусков | — (видимого эффекта нет: дубликат пропускается подготовкой) | правка — только с критерием до кода после S8 |

Дельта к строке курса: Ф16 и Ф17 — наблюдения; счёт K1–K5 — скриптом следующего закрытия сессии по классам строк. Не заявляется: что встроенный валидатор
отвергает 151 PS; что пользователь запускает с проверкой шейдеров; что дубликаты рецептов влияют на игру; что реестр полон.

## 26. Строка Б42 (автор — лид, `HPP-409`; решение `ROADMAP.md` «СЕССИЯ 122» п. 344)

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б42 (новая) | K4 (картинка; сцена держится) | дефект (наблюдение пользователя; кадров пока нет) | вода Sky Garden: когда Астро стоит в воде и камера вращается — глитчи картинки; на подходе к воде и после нескольких шагов по воде — норма | открыт; итерация **F9** трека F — диагностика: F9a (воспроизведение и снимки RenderDoc, под замком) → F9b (разбор, Emu Engineer) → F9c (лид: критерий до кода) | описание `HPP-409`; запись сессии пользователя `C:/kyty/play/20261002T221534Z/rec.mp4` (бинарь `4aa62e95`, патч `a204549c…`) — отрезки ищет F9a | `underwater_aerial_garden` | критерий до кода — F9c (п. 344(д)); `SCENE_OK` Sky Garden не снимается (форма V в воду не входит) |

Дельта к строке курса: K4 +1 (Б42) — счёт скриптом следующего закрытия сессии. Не заявляется: причина; что дефект эмулятора, а не игры или патча P-var.

## 27. Строка Б42 — диагностика F9a/F9b (автор — лид, `HPP-412`; решение `ROADMAP.md` «СЕССИЯ 122» п. 349)

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б42 (поправка к §26) | K4 (картинка; сцена держится) | дефект эмулятора [I] | вода пруда Sky Garden — мозаика плиток чужого экранного содержимого при камере сбоку/низко; вход PS воды `image_3[6]` (T6, 960×540 RGBA16F, `mix(цвет, T6.rgb, T6.a)`) держит память 4K-поверхности более раннего кадра вместо пустого слоя; в кадре T6 никто не пишет | открыт; F9d (диагностика M1–M3 на готовых ручках, под замком) → F9e (механизм + код `KYTY_FIX_B42`, умолчание 0) → F9f (ревью) → F9g (печать и 6 тегов) → F9h (лид) | `REPRO_YES` `f9a_1`, `f9a_2` на `4aa62e95` без `KYTY_GAME_PATCH` (`docs/track-f/f9a.md`); снимки `rd3_b` (глитч) и `rd2_f3951` (норма), разбор `docs/track-f/f9b.md`; одно-кадровый детектор глитч не видит (0) — признак только листом | `underwater_aerial_garden` | «ИСПРАВЛЕНО Б42» — п. 349(г); `ТУПИК` — три итерации кода без прохода или два диагностических прогона без механизма с [c] |

Дельта к строке курса: нет (Б42 уже K4 по §26). Не заявляется: механизм M1–M3; что на PS5 вода в этих ракурсах чистая; что другие уровни с водой без дефекта.

## 28. Строка Б42 — механизм F9e (автор — лид, `HPP-422`; решение `ROADMAP.md` «СЕССИЯ 122» п. 351)

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б42 (поправка к §27) | K4 (картинка; сцена держится) | дефект эмулятора [I]; механизм [c] на `f9d_2` | T6 — цель прохода `Ripple_0`; игра чистит её CMASK fast clear (заливка метаданных значением 0) и FCE-draw; эмулятор материализует CMASK-очистку только для целей кратного 1024 экстента (`4414e235:src/graphics/host_gpu/renderer/colorRenderTarget.cpp:441–442`) ⇒ T6 960×540 / 480×270 не очищается и держит загрузку при создании (960×540 — буфер копии 2432×1368 → плитки, 480×270 — нули → норма) | итерация кода 1 — **M2c** под `KYTY_FIX_B42` (умолчание 0): F9e2 (код) → F9f (ревью) → F9g (печать и 6 тегов) → F9h (лид) | `docs/track-f/f9e.md`, выписка `docs/track-f/f9e/scan_f9e.txt`; `CmaskClear` по T6 0 из 10 213 | `underwater_aerial_garden` | «ИСПРАВЛЕНО Б42» — п. 349(г) с поправкой п. 351(г); `ТУПИК` — как п. 349(г)(6) |

Дельта к строке курса: нет. Не заявляется: что CMASK-очистка — единственная причина; цвет очистки T6; что на PS5 вода в этих ракурсах чистая.

## 29. Строки приёмки F7c (автор — лид, `HPP-399`; решение `ROADMAP.md` «СЕССИЯ 122» п. 366)

Данные — отчёт F7b `docs/track-f/f7b-b39.md` (KytyPS5 `448a53bf`), файлы `docs/track-f/f7b/` (`sha_f7b.txt`), снимок F7a
`C:/kyty/f287/f7a/enemy_final_600.rdc` (`181cb236…`, только локально). Номер §24 из задания F7c занят строками FS2d — строки идут здесь.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б39 (поправка к §21) | K4 (картинка; сцена держится) | наблюдение; `НЕ ДЕФЕКТ` — кандидат до F7e | пол арены `enemy_final` — плоская светло-голубая заливка; [c] F7b: альбедо пола (draw 950/960, VS 588 → PS 508) = тексель однородной области атласа `12274` по верной UV (проба 8 из 8) | открыт; F7d (Red Team, враждебный отзыв) → F7e (лид); освещение, отражения, AO и проходы после G-буфера не разбирались [U] | `docs/track-f/f7b-b39.md` §2–§5, `read_probe_f7b.txt` (`eb275bd3…`) | `enemy_final` | правило F7e — п. 366(г); `SCENE_OK` `enemy_final` — строкой закрытия только после строки `НЕ ДЕФЕКТ` |
| Ф16 (поправка к §25) | K1-кандидат [U] | наблюдение | встроенная проверка `ValidateShaderSpirv` в `SPV_ENV_VULKAN_1_3` без опции раскладки | открыт; итерация **F10** трека F: F10a (Emu Engineer, офлайн-тест 151 + контроли к1–к4) → F10b (лид) | §25 | — | правило вывода — п. 366(д) |

Дельта к строке курса: нет. Очередь F после F10: Ф10 → Б41 → Б11 (+Ф3) → Б4 → Ф5/Ф7. Не заявляется: что пол `enemy_final` верен или неверен на итоговом
кадре; что Ф16 — дефект; что реестр полон.

## 30. Строка Б42 — приёмка F9h (автор — лид, `HPP-425`; решение `ROADMAP.md` «СЕССИЯ 122» п. 367)

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б42 (поправка к §28) | K4 → `FIXED` (счёт трека F) | дефект эмулятора [I]; механизм [c] (§28) | вода пруда Sky Garden — плитки чужого экранного содержимого в T6 при камере сбоку и низко | **`FIXED`** под `KYTY_FIX_B42=1` (умолчание пока 0): итерация кода 1 (F9e2 + F9e2b + F9e2c, бинарь `24efead3`) прошла все члены п. 349(г)(1)–(5); установка — третьим бинарём отгрузки трека F FS3 (умолчание 1): FS3a → FS3b → FS3c → FS3d | F9g `docs/track-f/f9g.md` (KytyPS5 `3f6bb416`): V1/V2 0 клеток с плитками из 572/575, C0 — плитки в неподвижной фазе, W 0 `[Vulkan][E]`, SG/HB 0 глитчей и листы без отличий; пересчёт и листы лида — `docs/track-f/f9h.md` | `underwater_aerial_garden`, `hoover_beach` (регрессия) | установка — FS3d; переоткрытие — плитки в T6 при `KYTY_FIX_B42=1` на листе |

Дельта к строке курса: K4 −1 (Б42); счёт — скриптом следующего закрытия. Не заявляется: что CMASK-очистка — единственная причина во всех сценах; что
на PS5 вода в этих ракурсах чистая; что другие уровни с водой без дефекта; что путь с `KYTY_GAME_PATCH` проверен.

## 31. Строки приёмки F10a (автор — лид, `HPP-446`; решение `ROADMAP.md` «СЕССИЯ 122» п. 369)

Данные — отчёт F10a `docs/track-f/f10a-f16.md` (KytyPS5 `19e33445`), файлы `docs/track-f/f10a/` (`sha_f10a.txt`), инструмент `sval_f10a.exe` и модули
`.spv` — только локально в `C:/kyty/f287/f10a/`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф16 (поправка к §25, §29) | **K1** при `--shader-validation true` (умолчание лаунчера) и новой трансляции PS | **дефект** [c офлайн] | встроенная `ValidateShaderSpirv` (SPIRV-Tools `7f2d9ee`, `SPV_ENV_VULKAN_1_3`, без `ValidatorOptions`) отвергает 151 из 151 PS базы T1 правилом раскладки uniform-блока (массив шага 4 без `uniformBufferStandardLayout`, которую устройство включает); отказ — `EXIT` → `std::_Exit(321)`; на попадании в кэш трансляции проверки нет; перехватчик фатала ставится только в потоке претрансляции CS (`computePretranslation.h:212`), на пути PS — нет | открыт; итерация кода **F10** под `KYTY_FIX_SVAL` (умолчание 0): F10c (Emu Engineer) → F10d (Red Team) → F10e (Harness Engineer, R0/R1/W под замком) → F10f (лид) | F10a: S151 REJECT 151; (к1) 151, (к2) 151, (к3) 151, (к4) 23 из 23; вердикт встроенной = SDK на 778 модулях | — (игра с проверкой шейдеров не запускалась; в игре не наблюдался [U]) | «ИСПРАВЛЕНО Ф16» — п. 369(в) |
| Ф10 (поправка к §16) | K4 | наблюдение (путь достижим после Ф9 [I], исполнение [U]) | треугольные узлы типов 2–3 → «нет попадания»; `size` не проверяется; `S_TRAP` — пустая операция | открыт; итерация **F11**: F11a (Emu Engineer, проект счётчика, после F10c) → F11b (Red Team) → F11c (лид) | §16 | — | правило вывода — п. 369(д) |

Дельта к строке курса: нет. Очередь F после F11: Б41 → Б11 (+Ф3) → Б4 → Ф5/Ф7. Не заявляется: что выход 321 наблюдался в игре; что пользователь запускает
игру с проверкой шейдеров; что 151 — все такие PS игры; что Ф10 достижим; что реестр полон.

## 32. Строка Б39 — приёмка F7d (автор — лид, `HPP-444`; решение `ROADMAP.md` «СЕССИЯ 122» п. 370)

Данные — отчёт F7b `docs/track-f/f7b-b39.md` (KytyPS5 `448a53bf`), отзыв F7d `docs/track-f/f7d-review.md` (KytyPS5 `465f0d8e`, `SOUND_WITH_CHANGES`, 6 RC текстовые),
файлы `docs/track-f/f7b/`, `docs/track-f/f7d/`; снимок F7a `C:/kyty/f287/f7a/enemy_final_600.rdc` (`181cb236…`, только локально; хранение — п. 370(д)).
Отчёт F7b читается с поправками RC2–RC6 F7d (п. 370(б)).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б39 (поправка к §21, §29) | K4 (картинка; сцена держится) | **`НЕ ДЕФЕКТ` (материал)** | пол арены `enemy_final` — плоская светло-голубая заливка; альбедо `[5]`, `[0]` и нормаль `[3]` по UV пола однородны в данных игры [c] (F7b §2–§5, F7d §0); AO применён верно [c] (F7d §0, 18 из 18); отложенное освещение (диспатчи EID 3399–3455 снимка `181cb236…`) не разобрано [U], наблюдения дефекта освещения нет (тень Астро на полу есть); 0 строк пропуска draw/dispatch в обоих логах [c]; эталона нет [U] | закрыта для счёта трека F (п. 228(д)); `SCENE_OK` `enemy_final` — пересмотр строкой ближайшего закрытия (бриф `docs/next-session-147.md` п. 7) | F7b `read_probe_f7b.txt` (`eb275bd3…`; проба §2а — [I] по RC2); F7d `f7d_uvtex.txt` (`657b0f00…`), `f7d_ao.txt` (`2321a666…`), `f7d_outpost.txt` (`abe4a66d…`), `f7d_logscan.txt` (`004120a8…`) | `enemy_final` | переоткрытие — по условиям П1 п. 370(г): лист с потерей члена освещения на плоскости, член (4) F11a «есть BVH» в CS EID 3399–3455, эталон PS5 |

Дельта к строке курса: сейчас нет (счёт — скриптом ближайшего закрытия). Очередь F: F10 → F11 (+ член (4) — CS освещения `enemy_final`) → Б41 → Б11 (+Ф3) → Б4 → Ф5/Ф7.
Не заявляется: что пол `enemy_final` верен или неверен на итоговом кадре; что освещение верно; что сцена корректна; что реестр полон.

## 33. Строка Б42 — отгрузка FS3 (автор — лид, `HPP-450`; решение `ROADMAP.md` «СЕССИЯ 122» п. 374–375)

| id | класс | вердикт | что видно | статус | доказательство | уровни | условие |
|---|---|---|---|---|---|---|---|
| Б42 (поправка к §30) | K4 → `FIXED`, отгружен под (B) | дефект эмулятора [I]; механизм [c] (§28) | вода пруда Sky Garden — плитки чужого экранного содержимого в T6 при камере сбоку и низко | **`FIXED`, отгружен под (B)**: FS3 `540c035a` (P23 `4414e235` + Б42 + умолчание `KYTY_FIX_B42=1`, коммит FS3a `4e72289e`) установлен 2026-10-03 07:11:12Z вместо `4aa62e95`; откат — копия `4aa62e95` по sha или `KYTY_FIX_B42=0` (частичный) | FS3c `docs/track-f/fs3c.md` (KytyPS5 `a1a1d971`): `fs3_u` 0 клеток с плитками из 568 (лист лида), `fs3_u0` плитки 48 из 48, `fs3_w` 0 `[Vulkan][E]`, `fs3_v`/`fs3_hb` 0 глитчей и листы без отличий; пересчёт лида — `docs/track-f/fs3d.md` | `underwater_aerial_garden`, `hoover_beach` (регрессия) | переоткрытие — плитки в T6 на установленной без `KYTY_FIX_B42=0` на листе |

Дельта к строке курса: K4 −1 на установленной (Б42) — счёт скриптом следующего закрытия сессии. Не заявляется: что CMASK-очистка — единственная
причина Б42 во всех сценах; что на PS5 вода в этих ракурсах чистая; что другие уровни с водой без дефекта; что путь с `KYTY_GAME_PATCH` проверен на воде.

## 34. Строка Ф16 — приёмка F10 (автор — лид, `HPP-454`; решение `ROADMAP.md` «СЕССИЯ 122» п. 378)

Данные — отчёты F10c `docs/track-f/f10c.md` (KytyPS5 `1a588fc2`), F10d `docs/track-f/f10d-review.md` (`571bb3a7`, PASS_WITH_FIXES), F10e `docs/track-f/f10e.md`
(`5df6fdaa`); пересчёт лида — `docs/track-f/f10f.md`, файлы `docs/track-f/f10f/`; логи и видео — только локально в `C:/kyty/f287/f10e/`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф16 (поправка к §25, §29, §31) | **K1** при `--shader-validation true` (умолчание лаунчера) и новой трансляции PS → `FIXED` (счёт трека F) | **дефект** [c офлайн и в игре] | встроенная `ValidateShaderSpirv` без опции `uniformBufferStandardLayout` отвергает PS с массивом шага 4 в uniform-блоке; отказ — `EXIT` → `_Exit(321)` | **`FIXED`** (счёт трека F, итерация кода 1 из 3): `KYTY_FIX_SVAL=1` (код `68602c4f`, бинарь F10c `36e2b042`) — опция ставится тогда и только тогда, когда устройство её включило; умолчание 0 до FS4; отгрузка — FS4 (FS3 `540c035a` + `68602c4f` + умолчание 1): FS4a → FS4b → FS4c → FS4d | F10c офлайн `ALL OK` (S151 `=0` REJECT 151 / `=1` ACCEPT 151; C 51/51; (к4) 23/23; CS 111/111; отрицательный контроль 2/2); F10d PASS_WITH_FIXES; F10e холод Sky Garden: R0 (`=0`) — отказ PS `c33dc20535a2cebf` и `exit rc 321` на 13,3 с; R1 (`=1`) — 0 отказов, 334,6 с, 0 смертей, `validated` 256, видео 10 275 кадров 0 глитчей, лист лида; W — 0 `[Vulkan][E]` / 937 205 `[Vulkan][W]` | `underwater_aerial_garden` | переоткрытие — `SPIR-V validation failed` правилом раскладки uniform-блока на бинаре с `KYTY_FIX_SVAL=1` при устройстве с `uniformBufferStandardLayout`; отказ другого класса — новая строка |

Дельта к строке курса: K1 −1 (Ф16) — при установке FS4 (FS4d), счёт скриптом следующего закрытия сессии. Не заявляется: что пользователь запускает игру с
проверкой шейдеров; что 151 — все такие PS игры; что встроенная проверка не отвергнет PS другого класса на других уровнях; что SPIR-V корректен для
устройства и картинка верна; что чёрные прямоугольники баннера кадра 6 листа R1 (тот же рисунок у FS3 `fs3_v`) — дефект или не дефект; что реестр полон.

## 35. Строки Ф10 и Ф18 — чтение F11g (автор — лид, `HPP-469`; решение `ROADMAP.md` «СЕССИЯ 122» п. 389)

Данные — отчёт F11f `docs/track-f/f11f.md` §8 (KytyPS5 `e442ec59`, печать `e06ff13d`); пересчёт лида — п. 389(а); логи — только локально в
`C:/kyty/f287/f11f/`. Счётчик — `KYTY_DIAG_BVHNODES=1` (бинарь F11d `b97efad4`, окно подписи М3′; в `main` кода нет).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф10 (поправка к §16, §31) | K4 | **путь достижим по типам 2–3 [c счётчика]**; ответ железа на типы 2–3 [U] | инструкция получает указатели типов 2–3 и отвечает «нет попадания»; по `size` не достигнут (корзина 4 = 0, корзины 1–3 = 0) [c]; `S_TRAP` не исполняется (`traps = 0`) [c], паркуется до сцены с `traps > 0` | открыт; итерация **F12**: F12a (Emu Engineer, первоисточник и проект) → F12b (Red Team) → F12c (лид: критерий до кода или строка) | `t2 + t3` = 6 344 915 / 1 173 080 / 136 310; отношение t0 : t1 : t2 : t3 = 4 : 3 : 2 : 3 без остатка на трёх сценах; одна программа `380bb9d636390bae` из 20, 19 не испытаны; `BvhLoopCapTrip:` 0; `enemy_final` — `NO_BVH` (4 программы освещения пола — 0 дорожек в окне удержания) | `underwater_aerial_garden`, `voxel_world`, `big_hand_pirate_island` | п. 389(д): без первоисточника ответа железа критерия до кода нет |
| Ф18 (новая) | K4 | наблюдение | игра шлёт тип 6 в `IMAGE_BVH_INTERSECT_RAY`; эмулятор отвечает «нет детей»; ответ железа [U] (п. 376(ж)(4)) | открыт; член (7) F12a | `t6` 47 223 (Sky Garden); `voxel_world`, `big_hand_pirate_island` — 0 | `underwater_aerial_garden` | после F12a — пунктом F12c |

Дельта к строке курса: K4 +1 (Ф18, наблюдение); счёт — скриптом следующего закрытия сессии. Очередь F: F12 (Ф10) → F13 (Б41) → Б11 (+Ф3) → Б4 → Ф5/Ф7.
Не заявляется: что Ф10 — дефект или не дефект; что игра строит узлы типов 2–3 или 6; что поле типа берётся из памяти узла; ответ железа; что освещение
пола `enemy_final` верно или неверно; что реестр полон.

## 36. Строки Ф10, Ф18, Б41 — чтение F12c (автор — лид, `HPP-476`; решение `ROADMAP.md` «СЕССИЯ 122» п. 391)

Данные — проект F12a `docs/track-f/f12a.md` (KytyPS5 `08bd2a87`), отзыв F12b `docs/track-f/f12b-review.md` (`99aac1e5`, SOUND_WITH_CHANGES, RC1–RC8);
счёт пути — F11f (§35). Первоисточники (MIT-лицензии AMD/Mesa) — только локально, `C:/kyty/f287/f12a/src_ext/`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф10 (поправка к §16, §31, §35) | K4 | **дефект** [c первоисточника и кода игры; применимость к кремнию PS5 — I] | `IMAGE_BVH_INTERSECT_RAY` отвечает на указатели типов 2–3 `0xffffffff` × 4; по первоисточнику (GPURT `b89f22aa` программный путь инструкции, RRA `28d0a0e5`) — треугольники (V2, V3, V4) / (V2, V4, V0), V4 — байты 48–59; программа `380bb9d636390bae` декодирует треугольник попадания тем же отображением; игра читает ответ эмулятора как кандидат с `t = NaN` или прозрачный треугольник | открыт; итерация кода **F12** (1 из 3) под `KYTY_FIX_F10` (умолчание 0): F12d (Emu Engineer, код и гейты) → F12e (Red Team) → F12f (Harness Engineer: снимок `f12_rd`, теги `f12_v`/`f12_w`/`f12_vw`/`f12_bh`) → F12g (Emu Engineer: реплей с подменой) → F12h (лид) | `t2 + t3` = 6 344 915 / 1 173 080 / 136 310 (F11f); тип — слово списка листьев BLAS в памяти, без арифметики [c]; 4 : 3 : 2 : 3 — суммы [c], по-списочно [I] | `underwater_aerial_garden`, `voxel_world`, `big_hand_pirate_island` | п. 391(г): GPU-тест по первоисточнику, `=0` байт в байт (тест и корпус), положительный контроль реплеем снимка `N_diff ≥ 1`, V/W «нет вреда»; дельты счётчиков и времени — не доказательство |
| Ф18 (поправка к §35) | K4 | наблюдение; **ответ железа [U]** | игра подаёт тип 6 вместе с 4–5 в инструкцию и разбирает ответ как четыре дочерних указателя [c]; эмулятор отвечает «нет детей»; `-1` ПК-первоисточника — для ПК-формата (тип 6 — экземпляр пользователя) | паркуется (п. 391(ж)) | `t6` 47 223 (Sky Garden) | `underwater_aerial_garden` | переоткрытие — первоисточник формата PS5 или стенд |
| Б41 (поправка к §22) | K4 | наблюдение (эталона нет [U]) | чёрный экран `ending_boss_after_credit` после ≈ 20 с карточки «THE END» | открыт; итерация **F13**: F13a (Harness Engineer: снимок `f13_rd`, V с вводом `f13_k`) → F13b (Emu Engineer: разбор) → F13c (лид) | §22 | `ending_boss_after_credit` | п. 391(з) |

Дельта к строке курса: нет (`FIXED` и отгрузки нет). Очередь F: F12 (Ф10, код) ∥ F13 (Б41) → Б11 (+Ф3) → Б4 → Ф5/Ф7.
Не заявляется: что кремний PS5 отвечает на типы 2–3 ровно как программный путь GPURT; семантика слов 2–3 на PS5; кто пишет списки листьев; ответ
железа на типы 6–7; что правка видна на листе; что чёрный экран `ending_boss_after_credit` — дефект; что реестр полон.

## 37. Строки Б41, Б11, Ф3 — чтение F13c (автор — лид, `HPP-484`; решение `ROADMAP.md` «СЕССИЯ 122» п. 395)

Данные — F13a `docs/track-f/f13a.md` (снимок `f13_rd`, ввод `f13_k` на установленном `540c035a`), F13b `docs/track-f/f13b.md` (разбор снимка, подмена
шейдера в реплее). Снимок и байты блоков констант — только локально, `C:/kyty/f287/f13a/`, `C:/kyty/f287/f13b/rd/`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б41 (поправка к §22, §36) | K4 | наблюдение; F13b — **`НЕ ДЕФЕКТ` по картинке [c снимка и реплея] — кандидат до F13e** | чёрный экран `ending_boss_after_credit` после карточки «THE END»: финальный проход (PS 237) смешивает сцену с (0, 0, 0) весом `1,0` из констант игры; без веса тот же проход даёт небо; геометрии нет (22 draw гостя против ≈ 1 000 на карточке), после карточки 0 открытий файлов; Cross и Circle не меняют ничего | открыт; отзыв **F13d** (Red Team) → **F13e** (лид) | `f13_rd.rdc` (`766880cf…`), `rd_f13b_probe.txt` (`b6756ab4…`), `log_f13_k.txt` (`0e2692c1…`) | `ending_boss_after_credit` | п. 395(в): SOUND / только текстовые RC — `НЕ ДЕФЕКТ`, причина «игра не переходит дальше» [U] паркуется до эталона PS5 или свидетельства HLE-вызова без ответа; RC с данными — звенья добычи; UNSOUND — критерий до кода или следующий шаг |
| Б11 (поправка к §4) | K4 | наблюдение (проявления нет) | `shader_cfg_tests`: падения `IMAGE_SAMPLE_C`, `IMAGE_SAMPLE_C_LZ` | открыт; итерация **F14**: F14a (Emu Engineer, офлайн) → F14b (лид) | §4 | — | п. 395(г): ISA против выхода транслятора — `НЕ ДЕФЕКТ` (ошибается тест) / дефект (критерий до кода `KYTY_FIX_B11`) / «не определено» |
| Ф3 (поправка к §4) | K4 | наблюдение по букве п. 228(б) | 36 CS без спекулятивной трансляции | открыт; итерация **F14** (счёт обычного пути по логам с. 142–146 и треков) | §4 | — | п. 395(г): 0 запросов обычным путём — наблюдение с новым счётом; ≥ 1 — сцена-свидетель и класс (F14b) |

Дельта к строке курса: нет (`FIXED` и отгрузки нет). Очередь F: F12 (Ф10, код) ∥ F13 (отзыв Б41) ∥ F14 (Б11 (+Ф3)) → Б4 → Ф5/Ф7.
Не заявляется: что чёрный экран `ending_boss_after_credit` — не дефект до F13e; что на PS5 эта сцена при входе `-lvl` показывает то же; почему игра не
переходит дальше; что Б11 — дефект; что реестр полон.

## 38. Строка Б41 — приёмка F13d (автор — лид, `HPP-486`; решение `ROADMAP.md` «СЕССИЯ 122» п. 397)

Данные — F13a `docs/track-f/f13a.md`, F13b `docs/track-f/f13b.md` (KytyPS5 `0ba742fb`), отзыв F13d `docs/track-f/f13d-review.md` (`9e9ed5a5`, `SOUND_WITH_CHANGES`,
7 RC текстовые), файлы `docs/track-f/f13d/`; выдержка данных уровня игры `C:/kyty/f287/f13d/level_local.txt` и снимок `f13_rd.rdc` — только локально.
Отчёт F13b читается с поправками RC1, RC3–RC6 F13d (п. 397(б)).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б41 (поправка к §22, §36, §37) | K4 | **`НЕ ДЕФЕКТ`**: (а) картинка — кадр гостя воспроизведён [c снимка и реплея]; (б) застой после карточки — поведение подуровня без родителя при отладочном входе `-lvl` [c данных уровня и лога родителя; I семантики]; HLE-вызова без ответа нет по классам 1–2 [c], класс 3 — [U] | чёрный экран `ending_boss_after_credit` после карточки «THE END»: финальный проход (PS 237) смешивает сцену с (0, 0, 0) весом `1,0` из констант игры — конец затемнения подуровня (`FadeOutDuration 1`; спуск яркости 54 кадра в видео [I]); сцена — подуровень `non_interactive_credit`, объектов выхода (`room_finisher`, `NextLevelFileName`) нет, родитель под тем же `-lvl` уходит в `worldmap` → `transition_next` → `hub_crashsite`; 13 из 22 draw гостя на флип без команды Vulkan не перечислены [U], на чёрный кадр и застой не влияют; ввод — [I] (`EnableSkip false`, пропуск `button_triangle` только у родителя; Options — [U]) | закрыта для счёта трека F (п. 228(д)); паркуется до эталона PS5 или свидетельства HLE-вызова без ответа; `SCENE_OK` `ending_boss_after_credit` — пересмотр строкой ближайшего закрытия (бриф `docs/next-session-147.md` п. 8) | F13b `rd_f13b_probe.txt` (`b6756ab4…`); F13d `markers.txt` (`b344a746…`), `trans.txt` (`e17a0696…`), `ramp_f13_k.txt` (`5b972d06…`), `savek_v146_07.txt` (`e0af74cd…`), `level_local.txt` (`1a02db2e…`, локально) | `ending_boss_after_credit`; родитель — `non_interactive_credit` (`v146_07`) | переоткрытие — эталон PS5 той же формы входа; названный HLE-вызов без ответа с [c]; видимый на PS5 элемент поверх чёрного или поимённый список draw кадра с пропуском — новая строка, не Б41 |

Дельта к строке курса: сейчас нет (счёт K4 — скриптом ближайшего закрытия). Очередь F: F12 (Ф10, код) ∥ F14 (Б11 (+Ф3)) → Б4 → Ф5/Ф7.
Не заявляется: что на PS5 эта сцена при входе `-lvl` показывает то же; почему игра не переходит дальше в смысле кода движка; что игра ждёт или не ждёт
ввода и системных событий класса 3; что 13 draw гостя без команды Vulkan безвредны поимённо; что сцена корректна; что реестр полон.

## 39. Строки Б11, Ф19, Ф3, Б4 — приёмка F14a (автор — лид, `HPP-488`; решение `ROADMAP.md` «СЕССИЯ 122» п. 400)

Данные — F14a `docs/track-f/f14a.md` (KytyPS5 `a015bb9f`), файлы `docs/track-f/f14a/`; бинари тестов — только локально, `C:/kyty/f287/f14a/bin/`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б11 (поправка к §4, §37) | K4 | **`НЕ ДЕФЕКТ`** эмулятора [c кода, SPIR-V и контроля `k32Float`] | `shader_cfg_tests` `PixelImageSampleLodSelection`: тест ждёт `OpImageSampleDref*` от образа `k8UNorm`; транслятор сравнивает нативно только `k32Float` (`ResourceMaterialization.cpp:570`); форма LOD, место опорного значения, функция сравнения и тип результата совпадают с ISA | закрыта для счёта трека F (п. 228(д)); правка теста — отдельным коммитом, не под (B), звено F14c (2) | `suite.log` (127 тестов, 1 падающий), контроль `k32Float` — 0 падений; F14a §0.1–§0.4, §2 | — (тест) | — |
| Ф19 (новая) | K4 | **не определено** (п. 395(г)(в)): путь исполняется [c корпуса T1], фильтр и формат ручных мест [U] | ручной путь сравнения глубины (`manual_depth_compare`, все форматы, кроме `k32Float`) фильтрует, затем сравнивает одно значение — при билинейном фильтре ступень 0/1 вместо доли PCF [c кода; I — порядок PCF]; `k16UNorm` идёт ручным путём при готовом виде `D16Unorm`; GPU-тест `ComparisonDepthTexture` падает тем же [c] | открыт; итерация **F14c** (Emu Engineer, офлайн: фильтр и формат ручных мест по снимкам) → **F14d** (лид); ручка будущей правки — `KYTY_FIX_F19` | F14a §0.5–§0.7, §3, §4; `f14a_spv.tsv` (ручное 48 строк / 42 программы / 884 места, все «≤»; нативное 13 / 13 / 234) | корпус T1: `underwater_aerial_garden`, `big_hand_pirate_island`, `shuriken_ninja_castle` | п. 400(в): `LINEAR` ≥ 1 места — дефект, критерий до кода по F14a §4; все `NEAREST` — наблюдение, паркуется; не читается — следующий шаг F14d |
| Ф3 (поправка к §4, §37) | K4 | наблюдение по букве п. 228(б) | 36 CS без спекулятивной трансляции (32 `resource tracking`, 4 `budget`) | **паркуется до сцены-свидетеля**: первая строка `CsPretranslate: miss` или `hit` с одним из 36 хэшей (или Б26г `57c4d5848e02ecdc`) или `shader CFG build failed` вне `CsPretranslate:`; проверка — `f14a_f3.py` ближайшим закрытием (бриф 147 п. 9) | 162 лога (с. 142–146, F13a, FS4c, F12f; `9235a7ac`, `dac02fb9`, `540c035a`, `31cbfee8`): 0 строк обычного пути, контроль 343 строки в 23 логах, 0 файлов кэша; `f14a_f3.tsv`, `f3_all.out.txt` | — | п. 400(г) |
| Б4 (поправка к §4) | K1 (при выходе) | дефект (по F0); механизм на текущем `main` — итерация F15 | гонка выхода: `CloseAll` (`fileSystem.cpp:243`) против гостевого `KernelOpen` ⇒ `EXIT_IF(m_files[index] == nullptr)` (`:207`) | открыт; итерация **F15**: F15a (Emu Engineer, офлайн: механизм, стенд без игры, досвип логов) → F15b (лид) | §4; `C:/kyty/s131/log_dds131.txt` | — (при выходе) | п. 400(д): стенд воспроизводит — критерий до кода `KYTY_FIX_B4`; код исключает — `НЕ ДЕФЕКТ`; иначе — «не определено» / «ТУПИК» по п. 228(д) |

Дельта к строке курса: нет (`FIXED` и отгрузки нет; Б11 был K4 «наблюдение»). Очередь F: F12 (Ф10, код) ∥ F14c (Ф19, данные) ∥ F15 (Б4) → Ф5/Ф7.
Не заявляется: что Ф19 — дефект и что расхождение видно в кадре; порядок PCF как текст ISA; что 37 CS Ф3 транслируются обычным путём; что Б4
воспроизводится; что реестр полон.

## 40. Строка Ф16 — отгрузка FS4 (автор — лид, `HPP-473`; решение `ROADMAP.md` «СЕССИЯ 122» п. 394, 407)

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф16 (поправка к §34) | **K1** при `--shader-validation true` (умолчание лаунчера) и новой трансляции PS → `FIXED`, отгружен под (B) | **дефект** [c офлайн и в игре] | встроенная `ValidateShaderSpirv` без опции `uniformBufferStandardLayout` отвергает PS с массивом шага 4 в uniform-блоке; отказ — `EXIT` → `_Exit(321)` | **`FIXED`, отгружен под (B)**: FS4 `31cbfee8` (FS3 `540c035a` + `68602c4f` + умолчание `KYTY_FIX_SVAL=1`, `KYTY_GIT_REVISION` `3d0e46d`) установлен 2026-10-04 06:54:49Z вместо `540c035a`; откат — копия `540c035a` по sha или `KYTY_FIX_SVAL=0` на холодном каталоге варианта | FS4c `docs/track-f/fs4c.md`: `fs4_r1` (умолчание, холод, проверка шейдеров) — 0 отказов, `validated=256 rejected=0`, 334,9 с, 0 смертей, 10 176 кадров 0 глитчей; `fs4_r0` (`=0`) — отказ `c33dc20535a2cebf` и `exit rc 321` на 12,1 с; `fs4_w` 0 `[Vulkan][E]`; `fs4_v` 334,4 с, 10 287 кадров 0 глитчей; пересчёт и листы лида — `docs/track-f/fs4d.md` | `underwater_aerial_garden`, `hoover_beach` (справка) | переоткрытие — `SPIR-V validation failed` правилом раскладки uniform-блока на установленной без `KYTY_FIX_SVAL=0`; отказ другого класса — новая строка |

Дельта к строке курса: K1 −1 на установленной (Ф16) — счёт скриптом следующего закрытия сессии. Не заявляется: что пользователь запускает игру с
проверкой шейдеров; что 151 — все такие PS игры; что встроенная проверка не отвергнет PS другого класса на других уровнях; что SPIR-V корректен для
устройства и картинка верна; что реестр полон.

## 41. Строка Б33 — повтор целостности S10 (автор — лид, `HPP-434`; решение `ROADMAP.md` «СЕССИЯ 122» п. 408)

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б33 (поправка к §4) | K3 (на удержании) | дефект; ведёт трек S | сохранение кэша пайплайнов драйвера (≈ 90 МБ, 80–130 мс) в середине уровня под `m_mutex` — кадр ≥ 100 мс на каждую запись | **`FIXED` — счёт трека S, не отгрузка под (B)**: S-pcw (`KYTY_S_PCW=1`, код `e11a297b` + `2ce6326e`, предки `main`, умолчание 0 на установленном FS4 `31cbfee8`); повтор целостности по п. 355(г)(2) — серий детектора после кадра 1 002 нет, `loaded` = последней записи своего W, `disabled` 0 | S6 (`pcw_1`…`pcw_4`, п. 354); S10 `pi_w1`/`pi_r1`/`pi_w0`/`pi_r0` (`C:/kyty/s288/s10/`, `fin_summary.txt` `31b51c62…`); пересчёт лида `C:/kyty/s288/lead/chk408.out.txt`; блоб после обоих W = `snap0` по sha256 (`cc5b747c…`) — рост блоба путём `=1` не проверен | `underwater_aerial_garden` | отгрузка умолчания — звенья S12a–S12d (п. 408(л)), член S12c(3) — пара роста блоба; переоткрытие — кадр ≥ 100 мс с записью кэша на удержании при `KYTY_S_PCW=1` или порча блоба, записанного путём `=1` |

Дельта к строке курса: K3 −1 (Б33) — после отгрузки S12d; до неё строка считается открытой на установленной. Не заявляется: что событие
`pcw_int` — эффект игры или дефект; что запись растущего блоба путём `=1` цела; что запись кэша — причина фризов холодного входа; что реестр полон.

## 42. Строка Ф19 — приёмка F14c (автор — лид, `HPP-490`; решение `ROADMAP.md` «СЕССИЯ 122» п. 409)

Данные — F14c `docs/track-f/f14c.md` (KytyPS5 `1c40a04a`), файлы `docs/track-f/f14c/`; снимки — только локально (`C:/kyty/f287/f12f/`, `f13a/`, `f9/`, `f7a/`).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф19 (поправка к §39) | K4 | **дефект** (п. 400(в)(1)) [c снимков и кода; I — порядок PCF] | ручной путь сравнения глубины (`manual_depth_compare`, все форматы, кроме `k32Float`) фильтрует, затем сравнивает одно значение — под `LINEAR` ступень 0/1 вместо доли PCF; все наблюдённые ручные места — на видах глубины (`D16_UNORM` — гостевой `k16UNorm`; `D32_SFLOAT` — формат трансляции [U]) | открыт; итерация кода 1 под `KYTY_FIX_F19` (умолчание 0), вариант (A) F14a §4 — нативное сравнение для форматов таблицы политик вида глубины рендера: **F14e** (Emu Engineer) → **F14f** (Red Team) → **F14g** (Harness Engineer) → **F14h** (лид); вариант (B) — паркуется до снимка с ручным местом на цветовом виде под `LINEAR` | F14c `f14c_table.tsv`, `f14c_summary.txt`: 11 снимков, 123 738 записей, все `LINEAR`/`LINEAR`, `D16_UNORM` 62 985, `D32_SFLOAT` 60 753, нативных 0; пересчёт лида п. 409(а) | Sky Garden (`underwater_aerial_garden`), `ending_boss_after_credit`, `enemy_final` | п. 409(г): GPU-тест-гейт PCF (≤ 2⁻⁶ при `=1`, ступень при `=0`), `=0` байт в байт на корпусе T1, снимок `f19_rd` при `=1` — `Dref` и `compareEnable = 1` на `D16_UNORM`, V/W «нет вреда» |

Б11 — правка теста KytyPS5 `fcaf141b` принята (п. 409(а)); строка закрыта п. 400(б), не под (B).
Дельта к строке курса: K4 «дефект» +1 (Ф19) — счёт скриптом ближайшего закрытия сессии. Очередь F: F12h (Ф10) ∥ F14e…F14h (Ф19) ∥ F15 (Б4) → Ф5/Ф7.
Не заявляется: что расхождение видно в кадре и его величина; что PCF драйвера равен ответу PS5; формат гостя за `D32_SFLOAT`; что (A) покрывает все места
игры; что реестр полон.

## 43. Строки Ф10 и Ф20 — приёмка F12h (автор — лид, `HPP-482`; решение `ROADMAP.md` «СЕССИЯ 122» п. 410)

Данные — F12d `docs/track-f/f12d.md` (KytyPS5 `65c0fa42`), F12e `docs/track-f/f12e-review.md` (`1a08f2df`), F12f `docs/track-f/f12f.md` (`0ed98954`),
F12g `docs/track-f/f12g.md` (`d1548be7`); файлы — `docs/track-f/f12d/` … `docs/track-f/f12g/`, снимки и дампы — только локально, `C:/kyty/f287/`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф10 (поправка к §16, §31, §35, §36) | K4 → **`FIXED`** (счёт трека F) | **дефект** [c первоисточника GPURT `b89f22aa`/RRA и кода игры; применимость к кремнию PS5 — I] | `IMAGE_BVH_INTERSECT_RAY` отвечал на указатели типов 2–3 `0xffffffff` × 4; правка `KYTY_FIX_F10` (`1833ee28`): типы 2–3 — треугольники (V2, V3, V4) / (V2, V4, V0), V4 — слова 12–14 | **`FIXED`** по п. 391(г)(1)–(5), итерация кода 1 из 3; умолчание `=1` — бинарь отгрузки FS5 (FS4 `31cbfee8` + `1833ee28` + умолчание), установка — FS5d, прогрев — FS5e | гейт 6 из 6; корпус T1 280 из 280; `f12_v`, `f12_w`, `f12_vw`, `f12_bh` — 17 из 17; реплей `f12_rd` k03: контроль А 3/3, Б 3/3, `N_diff` 14 193 / 14 302 / 17 793 из 262 144 | Sky Garden, `voxel_world`, `big_hand_pirate_island` | п. 410(г): FS5a → FS5b → FS5c → FS5d → FS5e |
| Ф20 (новая) | K4 | наблюдение [c кода; I механизма в игре; U влияния] | `RecordBdaFault` (`spirvEmitterMemory.cpp:176–187`) пишет бит промаха BDA неатомарно (`OpLoad` / `OpBitwiseOr` / `OpStore`) — бит может теряться; страница с потерянным битом становится резидентной (`ProcessFaultBuffer` → `FindBuffer`) на ≥ 1 проход позже [I] | **паркуется** до свидетельства в игре (страница с промахом остаётся нерезидентной в следующем проходе с доступом) или до правки соседнего кода BDA (п. 410(в)) | реплей F12g, EID 128281: слово 32824 буфера 138 (битовая карта страниц) — `0x04a0` / `0x204a0` от реплея к реплею | Sky Garden (снимок k03) | критерия до кода нет; кандидат `OpAtomicOr` |

Дельта к строке курса: K4 −1 (Ф10) — при установке FS5; Ф20 — K4 +1 (наблюдение); счёт скриптом следующего закрытия. Очередь F: FS5 ∥ F14e–F14h
(Ф19, п. 409) ∥ F15 (Б4) → Ф5/Ф7. Порядок FS5 и S12, сбор S13 — п. 410(г)(6).
Не заявляется: что кремний PS5 отвечает на типы 2–3 как программный путь GPURT; что правка видна на листе; что Ф20 влияет на игру; что FS5 работает в
игре до FS5c; что реестр полон.

## 44. Строки Б4, Ф21, Ф7, Ф5 — приёмка F15a (автор — лид, `HPP-492`; решение `ROADMAP.md` «СЕССИЯ 122» п. 412)

Данные — F15a `docs/track-f/f15a.md` (KytyPS5 `b64cc8be`), файлы `docs/track-f/f15a/`; стенд и сборка — только локально, `C:/kyty/f287/f15a/`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б4 (поправка к §4, §39) | K1 (при выходе) | **дефект** (п. 400(д)(а)) [c кода и стенда] | `Event: quit` → `std::quick_exit(0)` без остановки потоков гостя → `at_quick_exit` → `FileSystem::EmergencyShutdown` → `CloseAll` (`fileSystem.cpp:243`) удаляет `File` и пишет `nullptr`, пока поток гостя держит `File*` без `m_mutex` ⇒ `EXIT_IF(m_files[index] == nullptr)` (`:207`), `:446` или use-after-free | открыт; итерация кода 1 под `KYTY_FIX_B4` (умолчание 0), вариант (A) — аварийный путь не удаляет `File` и не обнуляет слоты: **F15c** (Emu Engineer) → **F15d** (Red Team) → **F15e** (Harness Engineer) → **F15f** (лид); вариант (B) — паркуется | стенд F15a: A 194 / 200, B 130 / 200 `FATAL207`, контроль C 0 / 50; досвип: 0 фаталов после выхода в 256 различных выходах (с. 143–146 и треки); свидетель `dds131` (F0) | — (при выходе) | п. 412(г): стенд при `=1` — 0 `FATAL`/`CRASH`/`TIMEOUT` в A и B по 200, `=0` воспроизводит; плечо D — данные на диске байт в байт; `=0` прежний; ревью; `b4_v` «нет вреда» |
| Ф21 (новая) | K1 (при выходе) | наблюдение [c кода; I следствия] | фатал гостя во время выхода зовёт `Subsystems::EmergencyShutdownActive` (`assert.cpp:22`) с потока гостя, пока главный поток обходит и чистит `m_active` (`subsystems.cpp:28`) без замка | **паркуется** до свидетельства (две аварийные последовательности или падение после строки фатала гостя при выходе) или до правки пути выхода | F15a §1.2 | — (при выходе) | критерия до кода нет; кандидат — флаг «аварийная последовательность идёт» |
| Ф7 (поправка к §4) | K4 | наблюдение | `file not found` на `KernelStat`/`KernelOpen`, `size_bytes/base is not 256-byte aligned`, `Format … cannot be used as texture` | открыт; итерация **F16**: F16a (Probe Designer, офлайн: перечень путей против пакета игры, поведение гостя после отказа) → F16b (лид) | §4 | — | п. 412(ж): все пробы необязательны — `НЕ ДЕФЕКТ`; файл есть под другим именем — дефект; иначе «не определено» |
| Ф5 (поправка к §4) | K4 | дефект по букве п. 228(б) | пакет из шести игнорируемых состояний ГП | открыт; итерация **F16**: F16a (Probe Designer, офлайн: на член — код, активность в снятых снимках, проект кадра-свидетеля) → F16b (лид) | §4 | — | п. 412(ж): на член — не меняет кадр — `НЕ ДЕФЕКТ`; меняет и активен в снимке — кадр-свидетель; меняет, не активен — `НЕ ДЕФЕКТ` по п. 228(д) с условием переоткрытия |

Дельта к строке курса: Б4 — без изменения (был «дефект» по F0); Ф21 — K1 +1 (наблюдение); счёт скриптом ближайшего закрытия сессии. Очередь F: FS5 ∥
F14e–F14h (Ф19) ∥ F15c–F15f (Б4) ∥ F16 (Ф7 + Ф5).
Не заявляется: что Б4 воспроизводится в игре на текущих сборках и что его правка нужна игре; что p_s стенда — частота игры; что Ф21 случается в игре; что
реестр полон.

## 45. Строка Ф22 — член (г)(0) F14e (автор — лид, `HPP-505`; решение `ROADMAP.md` «СЕССИЯ 122» п. 415)

Данные — F14e `docs/track-f/f14e.md` §0 (б) (KytyPS5 `5929bb7d`), файлы `docs/track-f/f14e/`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф22 (новая) | K4 | наблюдение [c кода; I следствия] | при `KYTY_FIX_F19=0` (сегодняшний путь) косвенная таблица образов со сравнением с корнем `k32Float` или пустым T# и кандидатом цветового формата: опкод по корню (`spirvEmitterImage.cpp:683`) — `OpImageSampleDref*`, вид по кандидату — цветовой (`descriptors.cpp:3073`); совместимость кандидатов формат не сравнивает (`ResourceMaterialization.cpp:676`) ⇒ VUID-06479 | **паркуется** до свидетеля (косвенная выборка образа со сравнением в снимке или VUID-06479 в W); при `=1` закрывается вариантом О1 п. 415(б); пересмотр строкой F14h при отгрузке умолчания `KYTY_FIX_F19=1` | F14e §0 (б); корпус T1 — 0 косвенных выборок образов из 4 343, снимки F14c — 0 | — | критерия до кода нет |

Ф19 (§42): член (г)(0) п. 409 принят (п. 415(а)); вариант О1 и форма члена (г)(2) при `=1` — п. 415(б)–(в); итерация кода 1 продолжается (F14e).
Дельта к строке курса: Ф22 — K4 +1 (наблюдение); счёт скриптом ближайшего закрытия сессии.
Не заявляется: что Ф22 достижима в игре; что косвенных таблиц со сравнением нет в игре; что реестр полон.

## 46. Строки Ф7, Ф5, Ф6 — приёмка F16a (автор — лид, `HPP-519`; решение `ROADMAP.md` «СЕССИЯ 122» п. 421)

Данные — F16a `docs/track-f/f16a.md` (KytyPS5 `9587f8dc`), файлы `docs/track-f/f16a/`; свип и большие выводы — только локально, `C:/kyty/f287/f16a/`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф7 (поправка к §4, §44) | K4 | **`НЕ ДЕФЕКТ`** (п. 421(б), исход п. 412(ж) Ф7 (а)) | `file not found` — `KernelStat` на пути `/app0`, которых нет в пакете (1 791 120 строк, 220 017 путей, 298 логов; другой регистр и монтирование — 0; повторов — 0); `KernelOpen` ENOENT молча (99 путей, повторов 0); выравнивание `R_ACQUIRE_MEM` и `cannot be used as texture` — только печать | закрыт `НЕ ДЕФЕКТ`; буква (б) для 3 540 путей (то же имя в другом каталоге или с другим расширением) читается по следствию «дефект разрешения пути» — его нет: `ResolvePath` один к одному, гость сам перебирает каталоги и находит файл (748 из 748) | F16a §1 | все сцены логов с. 142–146 и треков | переоткрытие: эталон PS5 с расхождением путей, текста или камеры; кадр-свидетель катсцены с пропавшей анимацией или камерой, связанный с путём F16a §1.7 (`/app0/.anim`, `save_data/.xml`, `.anim` катсцен, шрифты, `nx_ui_worldmap_bot_icon~~N.odx`); неполнота пакета на диске |
| Ф5 (поправка к §4, §44) | K4 | члены 3–6 — **`НЕ ДЕФЕКТ`**; члены 1–2 — «не определено» (п. 421(в)) | 6 — нулевой прямой диспатч (кадр не меняет); 5 — `GE_STEREO_CNTL` = 0; 4 — depth/stencil без цели (на хосте тест проходит); 3 — `ROUND_MODE` игнорируется (≤ шага квантования [I]); 1–2 — метаданные цвета и адреса учитываются, но в ветках без очистки остаётся прежнее содержимое | открыт по членам 1–2; итерация **F16** (диагностика): `KYTY_DIAG_F5` (умолчание 0) — F16c (Red Team, отзыв проекта) → F16d (Emu Engineer, код) → F16e (Red Team, ревью) → F16f (Harness Engineer, теги `f5_sg`, `f5_ef`, `f5_bh`, `f5_eb`, контроль `f5_sg0`) → F16g (лид) | F16a §2; член 5 — 16 записей на процесс в 282 логах, все 0 | Sky Garden, `enemy_final`, `big_hand_pirate_island`, `ending_boss_after_credit` (теги F16f) | п. 421(г): ветви B = 0 на 4 из 4 при живом контроле — члены 1–2 `НЕ ДЕФЕКТ` по п. 228(д); B > 0 — кадр-свидетель (F16g); переоткрытие членов 3–5 — п. 421(в) |
| Ф6 (поправка к §4) | K4 | наблюдение | `[Vulkan][W]`: фрагментный шейдер пишет в `out_mrt_N` без привязанной цели | открыт; итерация **F17**: F17a (Probe Designer, офлайн: пути, где слот гостя с целью не привязывается, и логи W) → F17b (лид) | §4 | — | п. 421(е): привязка всех слотов гостя с целью — `НЕ ДЕФЕКТ`; путь пропуска срабатывает — дефект; не различить — «не определено» |

Дельта к строке курса: Ф7 — K4 −1 (`НЕ ДЕФЕКТ`); Ф5 — без изменения (открыта по членам 1–2); счёт скриптом ближайшего закрытия сессии. Очередь F: FS5 ∥
F14e–F14h (Ф19) ∥ F15c–F15f (Б4) ∥ F16c–F16g (Ф5, члены 1–2) ∥ F17 (Ф6); затем Ф8.
Не заявляется: что пакет на диске полон; что члены 1–2 Ф5 меняют или не меняют кадр до F16g; что члены 3–4 совпадают с железом; что Ф6 — дефект или не
дефект до F17b; что реестр полон.

## 47. Строка Ф10 — отгрузка FS5 (автор — лид, `HPP-512`; решение `ROADMAP.md` «СЕССИЯ 122» п. 424, факт п. 426)

Данные — FS5a `docs/track-f/fs5a.md`, FS5b `docs/track-f/fs5b-review.md` (`1ea5e7a1`), FS5c `docs/track-f/fs5c.md` (`2443ddb0`), пересчёт лида
`docs/track-f/fs5d/` (`lead512.py`, `vg_v.txt`, `vg_r1.txt`).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф10 (поправка к §43) | K4 → **`FIXED`, отгружен под (B)** | дефект [c первоисточника GPURT; применимость к кремнию PS5 — I] | `IMAGE_BVH_INTERSECT_RAY` отвечал на указатели типов 2–3 `0xffffffff` × 4; правка `KYTY_FIX_F10` (`1833ee28`), умолчание 1 — FS5a `c3eb8fe8` | **FS5 `631ff987` установлен 2026-10-04 08:34:30Z**; откат — копия `31cbfee8` или `KYTY_FIX_F10=0` только на холодном каталоге варианта | FS5c: `fs5_v` 334,3 с, 0 смертей, 10 324 кадра 0 глитчей; `fs5_w` 0 `[Vulkan][E]`; `fs5_r1` 0 отказов встроенной проверки; листы лида без видимых дефектов (п. 424(а)–(в)) | Sky Garden (`underwater_aerial_garden`), справка `hoover_beach` | закрыта; первый вход каждого уровня на FS5 холоден (п. 424(ж)) |

Дельта к строке курса: K4 −1 (Ф10) на установленной; счёт скриптом ближайшего закрытия сессии.
Не заявляется: что кремний PS5 отвечает на типы 2–3 как программный путь GPURT; что правка видна на листе; что прочие 39 `SCENE_OK` держатся на FS5;
что реестр полон.

## 48. Строки Ф6, Б10, Ф8 и таблица строк K1–K4 без исхода — приёмка F17a (автор — лид, `HPP-526`; решение `ROADMAP.md` «СЕССИЯ 122» п. 433)

Данные — F17a `docs/track-f/f17a.md` (KytyPS5 `2f3e92d8`), файлы `docs/track-f/f17a/`; свип — только локально, `C:/kyty/f287/f17a/`. Таблица §48.2 — счёт лида
по строкам §4–§47 этого реестра [c текста реестра].

### 48.1 Строки

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф6 (поправка к §4, §46) | K4 | **не определено** (п. 433(б), исход п. 421(е)(в)) | `[Vulkan][W]`: PS пишет в `out_mrt_N` без привязанной цели; слот привязан ⇔ маска ≠ 0 и база ≠ 0, формат не читается [c]; путь П1 (маска ≠ 0, база 0) срабатывание по логам не различить | открыт; диагностика `KYTY_DIAG_F6` (умолчание 0) в цепочке F16: F16d → F16e → F16f (теги `f5_sg`, `f5_ef`, `f5_bh`, `f5_eb` с обеими ручками) → F16g | F17a §1–§3: 63 891 241 строка Ф6 в 70 логах W, 50 сцен; 16 ключей, `Location` 0…4; строк дампа и `EXIT` 0 | все 50 сцен логов W с. 143–146 и треков | п. 433(в): `w_addr0_fmt` = 0 и инварианты 0 на 4 из 4 при живом контроле — `НЕ ДЕФЕКТ`; `w_addr0_fmt` > 0 — паркуется «ответ железа [U]»; `bound_missing + bound_extra` > 0 — новая строка |
| Б10 (поправка к §4) | K4 | наблюдение | нет PCF в ручном сравнении глубины | **слита с Ф19** (п. 433(д)): тот же механизм `manual_depth_compare`; исход Б10 = исход Ф19 (F14h `HPP-508`) | §42 | — | как Ф19 |
| Ф8 (поправка к §4) | K4 | наблюдение | `AudioOut: SDL_QueueAudio failed: Invalid audio device ID` после отказа номера выходного устройства | открыт; итерация **F18**: F18a (Probe Designer, офлайн: пути закрытия номера и остановки подсистемы, логи с. 45–105, проект стенда `KYTY_TEST_AUDIOLOSS` и правки `KYTY_FIX_F8`) → F18b (лид) | §4; обработчика удаления аудиоустройства в `src/` нет [c] | — (20 логов с. 45–105) | п. 433(е): путь эмулятора или потеря хоста со стендом — дефект, критерий до кода; без стенда — `ТУПИК`; пути нет в текущем коде — `НЕ ДЕФЕКТ` |

### 48.2 Строки K1–K4 без исхода (исход — `FIXED`, `ТУПИК`, `НЕ ДЕФЕКТ` п. 228(д))

Строк K1–K4 в реестре — 54 (34 из §4 без Б26 + Б26а, Б26б + 19 новых). С исходом — 17: `FIXED` 10 (Б1б, Ф9, Б35, Б37, Б9а, Б42, Ф16, Ф10,
Б26б; Б33 — счёт трека S, отгрузка S12d), `ТУПИК` 2 (Б26а, Б9б), `НЕ ДЕФЕКТ` 5 (Б3б, Б39, Б41, Б11, Ф7). **Без исхода — 37:** в работе цепочкой 8,
без цепочки 21, припаркованы до свидетеля 8.

| Очередь | № | класс | статус | что даёт исход | исполнитель / замок |
|---|---|---|---|---|---|
| в работе | Ф19 (+ Б10) | K4 | дефект; итерация кода 1 `KYTY_FIX_F19` | F14e → F14h | Emu Engineer → Red Team → Harness Engineer → лид |
| в работе | Б4 | K1 (при выходе) | дефект; итерация кода 1 `KYTY_FIX_B4` | F15c → F15f | то же |
| в работе | Ф5 (члены 1–2) | K4 | не определено; `KYTY_DIAG_F5` | F16d → F16g | то же |
| в работе | Ф6 | K4 | не определено; `KYTY_DIAG_F6` в F16 | F16d → F16g | то же |
| в работе | Ф8 | K4 | наблюдение | F18a → F18b | Probe Designer, без замка |
| трек S | Б5, Б5а | K3, K2 | дефект; трек S | S12–S14 (п. 229(е)) | трек S |
| Q2 | Б24 | K2 (удержание) | дефект; нужен пользователь | стенд отключения HID без оборудования (форма F18); без стенда — `ТУПИК` по п. 228(д) | Probe Designer, без замка |
| Q3 | Б2, Б32 | K3 | дефект (происхождение [U]) | p по свипу удержаний Sky Garden на сборках `9235a7ac`+ по критериям строк | Probe Designer, без замка |
| Q4 | Б9 | K4 | наблюдение | свип `Unresolved import stub called` на установленных сборках (+ свидетели Ф3, Б26в, Б26г) | Probe Designer, без замка |
| Q5 | Ф4 | K4 | наблюдение | перечень путей чтения в гостевую память без обхода (код) | Probe Designer, без замка |
| Q6 | Б7, Б8 | K4 | наблюдение | тесты транслятора на опкод и на `exec ? new : old` | Emu Engineer, без замка |
| Q7 | Б13, Б27 | K4 | наблюдение | правка + тест порядка эпох; стресс-тест `daslot` | Emu Engineer, без замка |
| Q8 | Б36, Б40 | K2 (удержание) | дефект (происхождение [U]) | p и трасса кадра ≥ 1 с на удержании | Harness Engineer, замок |
| Q9 | Б14, Б28, Б29 | K4 | наблюдение | сверка `rtskip=2` (справка — `bound_missing + bound_extra` Ф6) | Harness Engineer, замок |
| Q10 | Б30, Б31 | K4, K3 | наблюдение, дефект | вход Day and Night: кадр ≥ 100 мс на удержании | Harness Engineer, замок |
| Q11 | Б12 | K4 | наблюдение | выгрузка раскладок `bdastamp` на сцене переписи | Harness Engineer, замок |
| Q12 | Б1а | K4 | дефект, закрытый ограничителем | вход без ограничителя после Ф9 — форма пунктом до данных | Harness Engineer, замок |
| Q13 | Б25 | K1 (удержание) | дефект | серия `intro_next` (при p = 0 на ≥ 60 — кандидат `ТУПИК`) | Harness Engineer, замок |
| конец | Б34, Б6 | K3 | наблюдение (эталона нет) | эталон PS5 или A/B ручкой; путь к комнате Б6 не назван — пересмотр пунктом | — |
| паркуется | Ф3, Б26в, Б26г, Ф11, Ф18, Ф20, Ф21, Ф22 | K4 (Ф21 — K1 при выходе) | наблюдение до свидетеля | проверка свидетелей ближайшим закрытием сессии и Q4; исход — пунктом, когда активная очередь пуста | — |

Дельта к строке курса: нет (исходов этим разделом нет; Б10 — дубликат Ф19, счёт — скриптом ближайшего закрытия сессии). Не заявляется: что Ф6 —
дефект или не дефект; что Ф8 воспроизводится в текущем коде; что очередь — порядок без пересмотра; что реестр полон.

## 49. Строка Б33 — отгрузка S12 (автор — лид, `HPP-497`; решение `ROADMAP.md` «СЕССИЯ 122» п. 437, факт п. 438)

Данные — S12a `docs/track-s/s12a.md` (`2b1b8787`), S12b `docs/track-s/s12b-review.md` (`4cba9eed`), S12c `docs/track-s/s12c/` (`b00170f2`),
пересчёт лида — `ROADMAP.md` п. 435(а).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б33 (поправка к §41) | K3 → **`FIXED`, отгружен под (B)** | дефект; трек S | сохранение кэша пайплайнов драйвера под `m_mutex` — кадр ≥ 100 мс на каждую запись; правка S-pcw (`e11a297b` + `2ce6326e`), умолчание `KYTY_S_PCW=1` — S12a `c1732d1a` | **S12 `adb0c82f` установлен 2026-10-04 10:12:56Z**; откат — копия FS5 `631ff987` или `KYTY_S_PCW=0` | критерий до кода п. 355(г); повтор целостности S10 (§41, п. 408(б)); S12c: `s12_w` 0 `[Vulkan][E]`; `s12_v` 334,4 с, 10 108 кадров 0 глитчей; пара `s12_gw`/`s12_gr` — блоб вырос путём `=1` (`8952f88c…`, 97 864 935 байт), загрузка = последней записи, `disabled` 0, 0 смертей; листы лида без видимых дефектов (п. 435) | Sky Garden (`underwater_aerial_garden`), `hero_kratos` | закрыта; подпись и каталог варианта = FS5 |

Дельта к строке курса: K3 −1 (Б33) на установленной; счёт скриптом ближайшего закрытия сессии.
Не заявляется: что событие `pcw_int` — эффект игры или дефект; что драйвер отдаёт согласованный снимок при параллельных вставках; что запись кэша —
причина фризов холодного входа; что прочие 39 `SCENE_OK` держатся на S12; что реестр полон.

## 50. Строки Ф8, Ф23, Б24 — приёмка F18a (автор — лид, `HPP-536`; решение `ROADMAP.md` «СЕССИЯ 122» п. 441)

Данные — F18a `docs/track-f/f18a.md` (KytyPS5 `98f11816`), файлы `docs/track-f/f18a/`; свип — только локально, `C:/kyty/f287/f18a/`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф8 (поправка к §4, §48) | K4 | **дефект** (исход (а) п. 433(е)) | `AudioOut: SDL_QueueAudio failed: Invalid audio device ID`: каждая неудачная попытка открыть звуковое устройство пада для вибрации (без USB-пада — раз в 3 с) вызывает `SDL_InitSubSystem(SDL_INIT_AUDIO)` без пары; счётчик ссылок SDL2 (`Uint8`) переворачивается, повторная инициализация закрывает все устройства портов, номера остаются; дальше тишина и поток звука гостя без темпа. Слова §4 «после потери аудиоустройства хоста» — не механизм: потеря устройства хоста строки не даёт [c кода SDL] | открыт; итерация кода 1 `KYTY_FIX_F8` (умолчание 0; один владелец подсистемы — член А F18a §5.1; переоткрытие паркуется): F18c (Emu Engineer) → F18d (Red Team) → F18e (Harness Engineer, теги `f8_s0`, `f8_s1`, `f8_n0`, `f8_n1`) → F18f (лид) | F18a §1.3, §2.1: момент `T_vib` + 759 с (A = 3) — 20 из 20 логов (Δ 761,5…767,7 с), опровергающих 0 из 1 190 | любая сцена процесса старше `T_vib` + 759 с без USB-пада (20 логов с. 45–105; на с. 106+ прогоны короче) | п. 441(д): стенд без игры, ревью, бинарь теста, 4 тега (стенд `KYTY_TEST_AUDIOLOSS=60:retry` и естественное удержание ≥ 840 с при `=0`/`=1`), лист лида |
| Ф23 (новая) | K5 | наблюдение | `AudioOut: SDL_OpenAudioDevice failed: WASAPI can't initialize audio client:` — все три выходных порта без устройства, прогон без звука, темп держит запасной сон; текст причины пуст | **паркуется до повторения в логе текущих сборок** (K5 — вне критерия трека F) | F18a §2.4: 27 строк в 9 логах (`f3d` × 8, `f4c_g`) | — | — |
| Б24 (поправка к §4, §48) | K2 (на удержании) | дефект (механизм не доказан) | остановка главного потока на отключении HID-устройства | открыт; итерация **F19** (Q2): F19a (Probe Designer, офлайн: пути главного потока при отключении, 5 логов `MainTaskLate` ≥ 1 с, свип с. 106+, проект стенда `KYTY_TEST_HIDLOSS` и правки `KYTY_FIX_B24`) → F19b (лид) | §4 | `intro_next` — 1 | п. 441(з): путь эмулятора или вызов SDL/ОС на главном потоке со стендом — дефект, критерий до кода; без стенда — `ТУПИК`; стоп-кадры иного происхождения и путь не блокирует — `НЕ ДЕФЕКТ` |

Поправка очереди §48.2: Ф8 — «в работе: итерация кода 1» (F18c → F18f); Q2 Б24 — «в работе» (F19a → F19b); Ф23 — паркуется (K5).
Дельта к строке курса: нет (исход `дефект` счёт открытых не меняет; Ф23 — K5 +1, счёт скриптом ближайшего закрытия сессии).
Не заявляется: что Ф8 воспроизводится на установленном бинаре до тега `f8_n0`; что звук верен или слышим; что Б24 воспроизводим без оборудования;
что реестр полон.

## 51. Строки Б24, Ф24 — приёмка F19a (автор — лид, `HPP-544`; решение `ROADMAP.md` «СЕССИЯ 122» п. 451)

Данные — F19a `docs/track-f/f19a.md` (KytyPS5 `0b065a70`), файлы `docs/track-f/f19a/`; свип — только локально, `C:/kyty/f287/f19a/`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б24 (поправка к §4, §48, §50) | K2 (на удержании) | **дефект** (исход (б) п. 441(з) с поправкой лида п. 451(б)) | поток гостя ждёт замок джойстиков SDL под `GameController::m_mutex` в выводе пада (`SetVibration` — раз в кадр при активном пульте хоста; `SetLightBar` / `SetTriggerEffect` — при любом); главный поток держит тот же замок на весь `SDL_JoystickUpdate`; замок 23,8 с держал путь SDL при потере Bluetooth-пульта [I]. Слова §4 «остановка главного потока при отключении HID» — не механизм: одна остановка главного потока кадр не останавливает [c лога `ctl114b`] | открыт; итерация кода 1 `KYTY_FIX_B24` (умолчание 0; член А F19a §5.1 — вывод пада через слот и поток `PadOutput`; член Б — нет, Ф24): F19c (Emu Engineer) → F19d (Red Team) → F19e (Harness Engineer, теги `b24_h0`, `b24_s0`, `b24_h1`, `b24_d0`, `b24_d1`, `b24_n1`) → F19f (лид) | F19a §1.5, §2.2: `edes122` — последняя запись потока игры до провала 23,8 с — аргументы `PadSetVibration`; три самых длинных пропуска вызова — на трёх строках `MainTaskLate` после входа (3 из 3); 4 прочих лога реестра и 7 новых — сон инструмента и стартовое ожидание (не Б24) | `intro_next` — 1 (логи с пультом хоста — 5 из 603 с. 106+) | п. 451(д): стенд без игры, ревью, бинарь теста, 6 тегов (стенд `KYTY_TEST_HIDLOSS=60:<hold, sleep, detach>`, `=0`/`=1`), лист лида |
| Ф24 (новая) | K4 | наблюдение | главный поток стоит, пока путь SDL под замком джойстиков ждёт ОС (перечисление HID, закрытие с ожиданием, очередь вибрации, перечисление DirectInput — F19a §1.3); при `KYTY_FIX_B24=1` остаток — окно не отвечает и ввод стоит на время блокировки, игра идёт [I] | **паркуется до свидетеля** — лог пользователя со строкой `Controller <id>: removed` и `MainTaskLate` ≥ 1 с при `KYTY_FIX_B24=1` | F19a §1.3, §5.2 | — | исход — пунктом при свидетеле (член Б F19a §5.2) |

Поправка очереди §48.2: Q2 Б24 — «в работе: итерация кода 1» (F19c → F19f); Q3 Б2, Б32 — «в работе» (F20a → F20b, офлайн, правило исхода п. 451(е)); Ф24 — паркуется.
Дельта к строке курса: нет (исход `дефект` счёт открытых не меняет; Ф24 — K4 +1, счёт скриптом ближайшего закрытия сессии).
Не заявляется: какой вызов держал замок 23,8 с; что Б24 воспроизводим без оборудования; что настоящая потеря пульта после правки не останавливает игру;
что Б2 или Б32 — не дефект до F20b; что реестр полон.

## 52. Строка Б4 — приёмка F15c–F15e (автор — лид, `HPP-517`; решение `ROADMAP.md` «СЕССИЯ 122» п. 454)

Данные — F15c `docs/track-f/f15c.md` (KytyPS5 `97f3bc4a`), F15d `docs/track-f/f15d-review.md` (`5dc643dd`), F15e `docs/track-f/f15e.md` §9
(`d5d0076a`); пересчёт лида — `ROADMAP.md` п. 440(б), 445(б), 454(б).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б4 (поправка к §4, §39, §44) | K1 (при выходе) | дефект → **`FIXED`** (счёт трека F; итерация кода 1 из 3) | гонка аварийного выхода (`at_quick_exit` → `FileSystem::EmergencyShutdown` → `CloseAll`) с потоком гостя, держащим `File*`; правка `KYTY_FIX_B4` (`a86a5ad0`): при `=1` аварийный путь не удаляет `File`, не обнуляет слоты и не закрывает дескрипторы | `FIXED`; умолчание `=1` — бинарём отгрузки FS6 (FS6a → FS6d), до установки на умолчаниях открыт | стенд `=1`: A/B 0 фаталов из 600 (F15c 400, F15d 200), контроль `=0` — 197 + 130 + 100 + 61 `FATAL207`; плечо D 20/20; F15d PASS; тег `b4_v` — 334,3 с, 0 смертей, 10 218 кадров 0 глитчей, выход за 3,7 с с кодом 0 | Sky Garden (`b4_v`, один выход) | п. 412(г); отгрузка — п. 454(г) |

Дельта к строке курса: K1 −1 (Б4) — при установке FS6 (FS6d); счёт скриптом ближайшего закрытия сессии. Поправка очереди §48.2: Б4 — «отгрузка FS6».
Не заявляется: что Б4 воспроизводится в игре на текущих сборках и что его правка нужна игре; что p_s стенда — частота игры; что Б4 теряет сохранения;
что Linux-ветка (A′) верна; что один выход `b4_v` доказывает отсутствие фатала выхода в игре; что реестр полон.

## 53. Строки Б2, Б32, Б9 — приёмка F20a (автор — лид, `HPP-552`; решение `ROADMAP.md` «СЕССИЯ 122» п. 462)

Данные — F20a `docs/track-f/f20a.md` (KytyPS5 `0a9adb84`, RC1 `20d97cd8`), файлы `docs/track-f/f20a/`; свип — только локально, `C:/kyty/f287/f20a/`.

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б2 (поправка к §4, §48) | K3 | дефект (происхождение [U]) | кадр ≥ 100 мс на 775–777-м кадре сцены Sky Garden с одной `PriorityStall:` 121–157 мс (инструментальные сборки с. 129–131, 7 из 20) | открыт; **«недостаток выборки»** по п. 451(е): на бинарях линии курса тёплых входов 6, кадров Б2 в окне сцены 723–828 — 0 (основной вариант: `--shader-validation true` исключает; холодные входы в N не входят); серия **F20c** (Harness Engineer, 24 тега V Sky Garden, последняя в очереди замка) → **F20d** (лид) | F20a §3.1–§3.3; лид [c] по `sweep_all.jsonl.xz` | Sky Garden | п. 462(д): N тёплых ≥ 30 и 0 кадров ⇒ `НЕ ДЕФЕКТ`; ≥ 1 ⇒ `дефект` с p |
| Б32 (поправка к §4, §48) | K3 | дефект (происхождение [U]) | кадры ≥ 100 мс на удержании без признака в интервале | открыт; Sky Garden — **«недостаток»**: 8 удержаний, 9 кадров (Б33 7, Б5 2), неатрибутированных 0 (= «ничего» + «только `PriorityStall:`», п. 462(б)(4)); серия F20c → F20d; `intro_next` — 0 удержаний на бинарях линии курса, **паркуется до серии Q13** (Б25) | F20a §4–§5 | Sky Garden; `intro_next` — нет | п. 462(д): N ≥ 30 и 0 неатрибутированных ⇒ `НЕ ДЕФЕКТ` на сцене |
| Б9 (поправка к §4, §48) | K4 | наблюдение (проявления нет) | неразрешённые импорты, которые игра не вызывала | открыт; итерация **F21** (Q4, офлайн): **F21a** (Probe Designer: свип `Unresolved import stub called` на бинарях линии курса + свидетели Ф3, Б26в, Б26г) → **F21b** (лид) | §4 | — | п. 462(ж): 0 вызовов вне набора Б9а на ≥ 30 уровнях ⇒ `НЕ ДЕФЕКТ`; ≥ 1 имя ⇒ строка Б9в |

Поправка очереди §48.2: Q3 Б2, Б32 — «в работе: серия F20c → F20d» (`intro_next` — парковка до Q13); Q4 Б9 — «в работе: F21a → F21b».
Дельта к строке курса: нет.
Не заявляется: что Б2, Б32 или Б9 — не дефект до F20d / F21b; что ждала приоритетная операция 121–157 мс на инструментальных сборках;
что `--shader-validation true` удлинил кадры; что `intro_next` удерживается 300 с на бинарях линии курса; что реестр полон.

## 54. Строка Ф8 — приёмка F18c–F18e (автор — лид, `HPP-542`; решение `ROADMAP.md` «СЕССИЯ 122» п. 467)

Данные — F18c `docs/track-f/f18c.md` (KytyPS5 `5b5ef739`), F18d `docs/track-f/f18d-review.md` (`f81bab8b`), F18e `docs/track-f/f18e.md` §9
(`b3dc6c3a`); пересчёт лида — `ROADMAP.md` п. 449(б), 453(б), 463(б), 467(б).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф8 (поправка к §4, §48, §50) | K4 | дефект → **`FIXED`** (счёт трека F; итерация кода 1 из 3) | каждая неудачная попытка открыть звуковое устройство пада для вибрации (раз в 3 с) зовёт `SDL_InitSubSystem(SDL_INIT_AUDIO)` без пары; счётчик `Uint8` SDL2 переворачивается через ≈ 759 с, повторная инициализация закрывает устройства всех портов — тишина и поток звука гостя без темпа; правка `KYTY_FIX_F8` (`10a4800b`): один владелец звуковой подсистемы, `SDL_InitSubSystem(SDL_INIT_AUDIO)` не более одного успешного раза на процесс | `FIXED`; умолчание `=1` — бинарём отгрузки FS7 (FS7a → FS7d, после установки FS6), до установки на умолчаниях открыт | стенд без игры `disk` × 3: `=0` отказ на вызове 254 у 3 из 3, `=1` 0 отказов, `init_calls` 1; F18d PASS; теги F18e на `35c4a754`: `f8_s0`/`f8_n0` (`=0`) — Ф8 есть (естественно через 762,1 с после `T_vib`), `f8_s1`/`f8_n1` (`=1`) — Ф8 0, `init_calls` max 1, 0 смертей, 10 152 и 25 725 кадров 0 глитчей | Sky Garden (4 тега) | п. 441(д); отгрузка — п. 467(г) |

Дельта к строке курса: K4 −1 (Ф8) — при установке FS7 (FS7d); счёт скриптом ближайшего закрытия сессии. Поправка очереди §48.2: Ф8 — «отгрузка FS7».
Не заявляется: что настоящая потеря устройства хоста даёт ту же форму или что правка её лечит (член Б — переоткрытие — паркуется до свидетеля);
что звук верен или слышим; что поток звука без темпа меняет часы игры; что одно удержание 840 с доказывает отсутствие Ф8 на всех сценах; что реестр полон.

## 55. Строки Ф19, Ф22 — приёмка F14e–F14g (автор — лид, `HPP-508`; решение `ROADMAP.md` «СЕССИЯ 122» п. 471)

Данные — F14e `docs/track-f/f14e.md` (`f18022a5`), F14f `docs/track-f/f14f-review.md` (`e975327c`), F14e2 `docs/track-f/f14e2.md` (`574bf7ff`),
F14f2 `docs/track-f/f14f2-review.md` (`c7c3ba3d`), F14g `docs/track-f/f14g.md` §8 (`08008b9d`); пересчёт лида — `ROADMAP.md` п. 443(а), 456(б), 469(б), 471(б).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф19 (поправка к §42) | K4 | дефект → **`FIXED`** (счёт трека F; итерация кода 1 из 3) | ручной путь сравнения глубины берёт отфильтрованное под `LINEAR` значение и сравнивает его одно — ступень 0/1 вместо доли PCF (края теней); правка `KYTY_FIX_F19` (`082d1612`, `f98e842c`): места сравнения гостевого `k16UNorm` (формат из таблицы `DEPTH_FORMAT_POLICIES` рендера) — нативный `OpImageSampleDref*` с PCF драйвера | `FIXED`; умолчание `=1` — бинарём отгрузки FS8 (FS8a → FS8e, после установки FS7 и приёмки S13c), до установки на умолчаниях открыт | GPU-гейт: `=1` — PCF ≤ 2⁻⁶, `=0` — отличие ≥ 0,25; корпус T1 и набор при `=0` байт в байт; F14f `PASS_WITH_FIXES` → F14e2 → F14f2 PASS; снимок `f19_rd` при `=1`: ручных на `D16_UNORM` 0, `Dref` на `D16_UNORM` 180 (k01) / 10 608 (k02), у всех `compareEnable 1`, `LESS_OR_EQUAL`, `LINEAR`; `f19_v1`/`f19_ef` — 0 смертей, 10 255 / 20 248 кадров 0 глитчей; `f19_w1` — 0 `[Vulkan][E]` | Sky Garden (снимок и 2 тега), `enemy_final` (тег) | п. 409(г); отгрузка — п. 471(г) |
| Ф22 (поправка к §45) | K4 | наблюдение [c кода; I следствия] | при `=0` косвенная таблица образов со сравнением с корнем `k32Float` или пустым T# и цветовым кандидатом даёт `OpImageSampleDref*` по цветовому виду (VUID-06479) | паркуется до свидетеля; при умолчании `=1` (после FS8) путь закрывает О1 [c проб F14e], при `=0` — как был; пересмотр строки — FS8d | — | — | п. 415(е); п. 471(е) |

Дельта к строке курса: K4 −1 (Ф19) — при установке FS8 (FS8d); счёт скриптом ближайшего закрытия сессии. Поправка очереди §48.2: Ф19 — «отгрузка FS8».
Не заявляется: что расхождение `=0` видно в кадре игры и его величина; что PCF драйвера равен ответу PS5; что ответ `D32_SFLOAT` на нативном пути верен;
что вариант (A) покрывает все места игры; что Ф22 достижима в игре; что реестр полон.

## 56. Строки Б9, Ф3, Б26в, Б26г, Ф4 — приёмка F21a (автор — лид, `HPP-564`; решение `ROADMAP.md` «СЕССИЯ 122» п. 474)

Данные — F21a `docs/track-f/f21a.md` (KytyPS5 `ef4224f4`), файлы `docs/track-f/f21a/`; пересчёт лида — `ROADMAP.md` п. 474(а).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б9 (поправка к §4, §48, §53) | K4 | наблюдение → **`НЕ ДЕФЕКТ`** (п. 228(д)) | неразрешённые импорты, которые игра не вызывала: на бинарях с правкой Б9а — 71 имя в 14 библиотеках (`AudioIn`, `ContentExport`, `ConvertKeycode`, `Http`, `LibcInternalExt`, `Net`, `NpSessionSignaling`, `NpWebApi2`, `PlayerInvitationDialog`, `PngEnc`, `Rudp`, `Ssl`, `VoiceChat`, `libkernel`) | **`НЕ ДЕФЕКТ`** на путях входа `-lvl` и удержания ≤ 330 с без действий игрока; **переоткрытие:** строка `Unresolved import stub called` с именем вне набора Б9а в любом логе бинаря линии курса (включая записи игры пользователем) ⇒ строка Б9в (K4) на библиотеку с уровнем и итерация кода пунктом | 0 имён вне набора Б9а на 201 логе восьми бинарей линии курса и на 422 разных логах; уровней 53 (строгий счёт без насыщенных логов), 54 по букве, 51 с ≥ 300 с кадров; маркер жив (10 логов по 1 024 строки Б9а); граница 95 % — 0,067 на уровень | 53 уровня выборки (`ana_f21a.txt` §4) | п. 462(ж); п. 474(в) |
| Ф3, Б26в, Б26г (поправка к §11, §39, §48) | K4 | наблюдение до свидетеля | шейдеры, спекулятивная трансляция которых не проходит, игрой обычным путём не запрошены | **паркуются** (без изменений) с новым счётом | строк `CsPretranslate: miss` / `hit` с хэшами Ф3 (37), Б26в (4), Б26г (1) — 0 на 201 логе выборки (191 со взводом, 54 уровня) и на 422 логах (373 со взводом, 61 уровень); `shader CFG build failed` вне `CsPretranslate:` — 0; контроль — 1 099 строк `miss|hit` 124 хэшей в 31 логе | — | условия переоткрытия §11, §39 без изменений |
| Ф4 (поправка к §4, §48) | K4 | наблюдение (обход действует [c] в `KernelRead`) | прямое чтение файла в гостевую память, защищённую кэшем, возвращает 0 байт; обход `ReadGuestWithRetry` читает через хост-буфер; полнота обхода для прочих путей чтения и частичного чтения [U] | в работе: итерация **F22** (Q5, офлайн): **F22a** (Probe Designer: перечень путей записи данных файла в гостевую память и их обходов, верность обхода, какие пути вызывает игра по логам линии курса) → **F22b** (лид) | §4 | — | п. 474(е): все пути с верным обходом ⇒ `НЕ ДЕФЕКТ`; путь без обхода (или дефект обхода) со свидетельством вызова ⇒ `дефект`, итерация `KYTY_FIX_F4`; без свидетельства ⇒ Ф4а «не определено» |

Поправка очереди §48.2: Q4 Б9 — «исход: `НЕ ДЕФЕКТ` (F21b, п. 474)»; Q5 Ф4 — «в работе: F22a → F22b»; строка «паркуется» — Ф3, Б26в, Б26г проверены Q4 (свидетель не найден).
Дельта к строке курса: K4 −1 (Б9) — счёт скриптом ближайшего закрытия сессии.
Не заявляется: что 71 заглушенное имя не вызывается действиями игрока, на уровнях вне выборки и дальше первых 330 с уровня; что прочие правки линии
курса не открывают путей к ним; что возврат 0 из заглушки верен; что шейдеры Ф3, Б26в, Б26г не будут запрошены; что Ф4 — дефект или не дефект; что реестр полон.

## 57. Строки Ф4, Ф4а, Ф25, Б7, Б8 — приёмка F22a (автор — лид, `HPP-577`; решение `ROADMAP.md` «СЕССИЯ 122» п. 483)

Данные — F22a `docs/track-f/f22a.md` (KytyPS5 `08d32f14`, `6a75ac14`), файлы `docs/track-f/f22a/`; пересчёт лида — `ROADMAP.md` п. 483(а).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф4 (поправка к §4, §48, §56) | K4 | наблюдение → **`НЕ ДЕФЕКТ`** (п. 228(д)) | прямое чтение файла в гостевую память, защищённую кэшем: ядро отклоняет запись (FALSE, 0 байт), обход `ReadGuestWithRetry` читает через буфер хоста | **`НЕ ДЕФЕКТ`**: пути данных файла `KernelRead`, `KernelPread` (через них `read`, `_read`, `pread`, AIO) — обход есть и верен; пути AMPR, каталоги, `/dev/random`, сохранения, загрузчик — копия пользовательского режима; **переоткрытие:** строка `KernelRead: direct read failed` без строки `Read <n> bytes` того же размера в пределах 2 000 строк в логе бинаря линии курса, или новый путь записи ядром в гостевую память без обхода в коде | стенды на хосте: 76 из 76 «всё или ничего», обход 75 из 75, гонка 0 частичных из 2 000 (звено и лид); в игре 17 отказов в 4 логах выборки из 201 — 17 из 17 закончились полным чтением; `Read 0 bytes` 0 в 422 логах | `ice_iceberg`, `worldmap`, `non_interactive_credit` (бинари `9235a7ac`, `dac02fb9`) | п. 474(е); п. 483(в) |
| Ф4а (новая) | K4 | не определено | сокетное чтение (`recv`, `recvfrom`, `KernelRead`/`read` дескриптора сокета) пишет ядром Windows в буфер гостя без обхода отказа записи в страницу, защищённую кэшем | **паркуется до свидетеля** — блок печати `Recvfrom` в логе бинаря линии курса (печать стоит на каждом вызове до `::recv`; счётчик не назначается); при свидетеле — проект стенда «`recv` в защищённую страницу» и правило исхода пунктом | блоков `Recvfrom` 0, `Sendto` 0 в 422 логах | — | п. 483(в) |
| Ф25 (новая) | K4 | наблюдение (проявления нет) | при отказе обоих чтений (прямого и через буфер хоста) `KernelRead` / `KernelPread` отдают гостю 0 («конец файла») вместо `EIO`; `EIO` — только при пустом дескрипторе хоста | **паркуется до свидетеля** — строка обхода без полного чтения того же размера и две строки stdout `SysFileRead` одного размера подряд, или `Read 0 bytes` с запросом не на конце файла | 0 случаев: 17 из 17 обходов — полное чтение, `Read 0 bytes` 0 в 422 логах | — | п. 483(б)(2), (в) |
| Б7, Б8 (поправка к §4, §48) | K4 | наблюдение (проявления нет) | Б7 — нереализованные опкоды VALU (`V_MUL_LEGACY_F32`, `V_FMAC_LEGACY_F32` и др.); Б8 — select «`exec ? new : old`» снимается только на верхнем уровне PS | в работе: итерация **F23** (Q6, офлайн): **F23a** (Emu Engineer: способ декода, список опкодов в `SetUnsupported` и счёт по корпусу T1 и, если можно, данным игры; места оставшегося select и счёт программ формы драйвера по корпусу T1) → **F23b** (лид) | §4 | — | п. 483(е): Б7 — 0 в корпусе (и в данных игры) ⇒ `НЕ ДЕФЕКТ`, ≥ 1 в данных игры ⇒ `дефект`, `KYTY_FIX_B7`; Б8 — 0 программ формы драйвера ⇒ `НЕ ДЕФЕКТ`, ≥ 1 ⇒ «не определено», GPU-тест-гейт |

Поправка очереди §48.2: Q5 Ф4 — «исход: `НЕ ДЕФЕКТ` (F22b, п. 483); Ф4а, Ф25 — парковка»; Q6 Б7, Б8 — «в работе: F23a → F23b»; строка «паркуется» — + Ф4а, Ф25.
Дельта к строке курса: K4 −1 (Ф4); Ф4а и Ф25 — новые строки в парковке — счёт скриптом ближайшего закрытия сессии.
Не заявляется: что игра не читает сокет на путях действий игрока, по сети и на уровнях вне выборки; что «всё или ничего» `ReadFile` держится на других
сборках Windows; что чтение 0 байт вызывает крэш игры; что Б7 или Б8 — дефект или не дефект; что реестр полон.

## 58. Строка Б24 — приёмка F19c–F19e (автор — лид, `HPP-550`; решение `ROADMAP.md` «СЕССИЯ 122» п. 487)

Данные — F19c `docs/track-f/f19c.md` (KytyPS5 `45080d53`), F19d `docs/track-f/f19d-review.md` (`6b090b17`), F19c2 `docs/track-f/f19c2.md` (`341c2600`),
F19d2 `docs/track-f/f19d2-review.md` (`346bba20`), F19e `docs/track-f/f19e.md` §9 (`58b6c5ad`); пересчёт лида — `ROADMAP.md` п. 457, 479, 485, 487(б).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б24 (поправка к §4, §48, §50, §51) | K2 (на удержании) | дефект → **`FIXED`** (счёт трека F; итерация кода 1 из 3) | поток гостя ждёт замок джойстиков SDL под `GameController::m_mutex` в выводе пада; правка `KYTY_FIX_B24` (`9c726d74`, `919c1a19`): `SetVibration` / `SetLightBar` / `SetTriggerEffect` кладут значение в слот, вызовы SDL делает один поток `PadOutput` без `m_mutex`, поток останавливается до `ReleaseHostPads` (повторный вход `Stop` безопасен) | `FIXED`; умолчание `=1` — бинарём отгрузки FS7 вместе с Ф8 (FS7a → FS7d, после установки FS6; тег `fs7_h`), до установки на умолчаниях открыт | стенд `b24_pad_stand` 7 из 7 `ALL OK`, `dd` 1 000 из 1 000; F19d `PASS_WITH_FIXES` → F19c2 → F19d2 PASS; теги F19e на `9b00ad40`: `b24_h0` (`=0`, `hold`) — `pad_wait_max_us` 2 973 404, кадр 2,99 с; `b24_s0` (`=0`, `sleep`) — кадров ≥ 1 с 0; `b24_h1` (`=1`, `hold`) — `po_wait_max_us` 2 973 393, `pad_wait_max_us` 10, `guest_sdl` 0, кадров ≥ 1 с 0; `b24_d0`/`b24_d1` — `removed` 1, кадров ≥ 1 с 0; `b24_h1`/`b24_n1` — 330 с, 0 смертей, 10 121 / 9 918 кадров 0 глитчей | Sky Garden (6 тегов) | п. 451(д); отгрузка — п. 487(г) (поправка к п. 467(г)) |

Поправка очереди §48.2: Q2 Б24 — «отгрузка FS7»; Ф24 — паркуется (без изменений).
Дельта к строке курса: K2 −1 (Б24) — при установке FS7 (FS7d); счёт скриптом ближайшего закрытия сессии.
Не заявляется: что настоящая потеря пульта после правки не останавливает игру (до лога пользователя со строкой `Controller <id>: removed`); какой вызов
держал замок 23,8 с в `edes122`; что Б24 воспроизводим без оборудования; что ненулевая вибрация гостя доходит до пульта в игре; что реестр полон.

## 59. Строки Ф5, Ф6 — чтение F16f (автор — лид, `HPP-524`; решение `ROADMAP.md` «СЕССИЯ 122» п. 489)

Данные — F16f `docs/track-f/f16f.md` §7 (KytyPS5 `a6114045`), пересчёт лида — `ROADMAP.md` п. 488(б), п. 489(а), (г).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф6 (поправка к §4, §46, §48) | K4 | **`НЕ ДЕФЕКТ`** (п. 433(в)(i), исход п. 421(е)(а)) | `[Vulkan][W]`: PS пишет в `out_mrt_N` без привязанной цели — только в слоты с маской 0 | закрыта без отгрузки | `KYTY_DIAG_F6` на `4ad735ad`: `w_addr0_fmt` 0, `bound_missing` 0, `bound_extra` 0, `w_ge8` 0, `s_addr0_fmt` 0 на 4 из 4; `w_mask0` 3 586 661 / 294 132 / 9 859 343 / 12 217 | `underwater_aerial_garden`, `enemy_final`, `big_hand_pirate_island`, `ending_boss_after_credit` | переоткрытие — `w_addr0_fmt` > 0 в любом прогоне диагностики или кадр-свидетель |
| Ф5 (поправка к §4, §44, §46) | K4 | члены 3–6 — `НЕ ДЕФЕКТ` (без изменений; член 5 не переоткрыт: `stereo_nonzero` 0 на 4 из 4); члены 1–2 — **кандидат кадра-свидетеля** (п. 421(г)(ii)) | ветви B > 0 на 4 из 4: `cmask_fce_unapplied` 4 (все до входа в сцену), `dcc_fce_no_image` 402 / 20 173 / 318 / 20 132 (в сцене 1,0 на кадр у `enemy_final`, `ending_boss_after_credit`), `meta_cs_untracked` 67 021 / 99 778 / 105 835 / 60 240 (в сцене 3,0–11,4 на кадр); прочие 15 ветвей 0; семей «не достигнута» 0 | открыт; итерация свидетеля **F16h** (Emu Engineer: механизм и проект правки на ветвь, офлайн) → **F16i** (Red Team) → **F16j** (лид: критерий до кода); ручки правки `KYTY_FIX_F5CMU`, `KYTY_FIX_F5FCE`, `KYTY_FIX_F5CS` (умолчание 0) | `KYTY_DIAG_F5` на `4ad735ad` (теги `f5_sg`, `f5_ef`, `f5_bh`, `f5_eb`, контроль жив, тождества 0) | те же четыре | форма свидетеля — пара V `=0`/`=1` на ветвь, правило чтения п. 489(д); член 2 — примечание: «чтение FMASK как текстуры — тождественная карта фрагментов; переоткрытие — эталон PS5 или кадр-свидетель края MSAA на draw с FMASK-чтением» |

Дельта к строке курса: K4 −1 (Ф6); счёт скриптом ближайшего закрытия сессии.
Не заявляется: что ненулевой счётчик ветки меняет картинку; что ноль прочих ветвей — свойство игры; что Ф6 `НЕ ДЕФЕКТ` вне четырёх сцен; что реестр полон.

## 60. Строки Ф5, Ф26 — приёмка F16h с отзывом F16i (автор — лид, `HPP-582`; решение `ROADMAP.md` «СЕССИЯ 122» п. 492)

Данные — F16h `docs/track-f/f16h.md` (KytyPS5 `6ca24c4f`), отзыв F16i `docs/track-f/f16i-review.md` (KytyPS5 `859d2ed8`), решение — `ROADMAP.md` п. 492(а)–(и).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф5 (поправка к §59) | K4 | члены 1–2 — кандидат кадра-свидетеля; ветвь 1 `cmask_fce_unapplied` — исход (А) условно (сброс отложенной CMASK-очистки корзинной проверкой `PendingDccFillStale` и отсутствие другого пути — [c]; ложность сброса — [I] на 4 событиях из 4); ветви 2 `dcc_fce_no_image`, 3 `meta_cs_untracked` — исход (В) | ветвь 1: проверка устаревания сравнивает номера записей по корзинам 64 КиБ, соседняя заливка метаданных в той же корзине объявляет заливку устаревшей | открыт; итерация **F16k** (Emu Engineer: код `KYTY_FIX_F5CMU` и `KYTY_DIAG_F5ID`, умолчание 0) → **F16l** (Red Team) → **F16m** (Harness Engineer: пара `f5cmu_0`/`f5cmu_1`, теги `f5id_sg`, `f5id_ef`, `f5id_bh`, `f5id_eb`) → **F16n** (лид) | F16h по коду `cc096dbf` и логам F16f; отзыв F16i RC1–RC11 | `underwater_aerial_garden`, `enemy_final`, `big_hand_pirate_island`, `ending_boss_after_credit` | ветвь 1 — пара V `enemy_final`, чтение п. 492(е); ветви 2–3 — чтение п. 492(д); ручки правки `KYTY_FIX_F5FCE`, `KYTY_FIX_F5CS` — после чтения |
| Ф26 (новая) | K4 | кандидат | ложный `stale` по корзине 64 КиБ на DCC-сайтах (`AdoptPendingDccForTexture`, `PrepareDccClear`): отложенная DCC-заливка сбрасывается из-за непересекающейся записи соседа | открыт; измерение — счётчики `dcc_stale_bucket_only`, `dcc_stale_fallback`, `cmask_rt_bucket_only` тегов `f5id_*` (только счёт); ручка будущей правки `KYTY_FIX_F26` (кода нет) | кадр 0 `f5_ef`: `0x510d10000 / 0x56d898000`, `seq=3 last=6` — запись №6 соседа `[0x56d8ac000, 0x56d8b8000)` [c журнала F16h]; счёт — `dcc_reset_stale` (вне набора B) | стартовый путь, 4 тега F16f [c F16h] | > 0 — кандидат кадра-свидетеля, пара под `KYTY_FIX_F26` пунктом чтения F16n; = 0 на 4 из 4 — «не достигнут на четырёх сценах» |

Дельта к строке курса: K4 +1 (Ф26); счёт скриптом ближайшего закрытия сессии.
Не заявляется: что сброс ветви 1 ложен хоть на одном событии; что Ф26 меняет кадр; что ненулевой счётчик ветви меняет картинку; что реестр полон.

## 61. Строки Б7, Б8 — приёмка F23a (автор — лид, `HPP-579`; решение `ROADMAP.md` «СЕССИЯ 122» п. 493)

Данные — F23a `docs/track-f/f23a.md` (KytyPS5 `0c806367`), файлы `docs/track-f/f23a/`; решение — `ROADMAP.md` п. 493(а)–(и).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б7 (поправка к §4, §57) | K4 | `НЕ ДЕФЕКТ` | нереализованные опкоды VALU (318 кодов, `unsuplist_f23a.out.txt`; имена [I]): декодер читает программу целиком линейно, CFG выходит `EXIT` на любой неподдержанной инструкции, достижима она или нет | закрыт: `НЕ ДЕФЕКТ` по п. 228(д) (п. 493(в)) | 0 программ с неподдержанной инструкцией в корпусе T1 (337) и во всём `eboot.bin` (5 698 уникальных программ, все уровни) — свой разбор слов и настоящий декодер `main`, гистограммы VALU совпали 6 035 / 6 035, контроли живы [c] | все программы игры в `eboot.bin` | переоткрытие — строка `opcode is not implemented` (любое семейство VALU) в логе бинаря линии курса или программа гостя вне `eboot.bin` с таким опкодом |
| Б8 (поправка к §4, §57) | K4 | «не определено» | select `exec ? new : old` снимает только `PredicationElimination`; свёртка `S_WQM` верхнего уровня PS не срабатывает [c F23a] — часть этой строки; select остаются в 246 из 247 PS и 102 из 119 CS корпуса T1; форма драйвера A — 38 программ (PS 20, CS 18), у эталона `0xe197e307a5f2cb39` в `main` — 0 (без `PredicationElimination` — 2) | в работе: ступень 1 — **F23c** (Emu Engineer: исторический контроль H на эталоне — `KYTY_PRED_ELIM=0` против умолчания на GPU этой машины, `N_diff`, контроли нулевой и чувствительности; опись покрытия 38 программ снимками и метод опорного значения) → **F23d** (Red Team) → **F23e** (лид) | `b8_forms_normal.tsv` (38), `b8_forms_predoff.tsv` (181); VS/MS — [U] (≤ 21 + 1) | дампы T1: `underwater_aerial_garden`, `big_hand_pirate_island`, `shuriken_ninja_castle`; строки C/D — сцена [U] | п. 493(г): H > 0 ⇒ ступень 2 — гейт на программах формы A (`N_diff` > 0 ⇒ `дефект`, `KYTY_FIX_B8`; 0 у покрытых ⇒ `НЕ ДЕФЕКТ` на покрытых); H = 0 ⇒ `НЕ ДЕФЕКТ` на драйвере этой машины (переоткрытие — H > 0 на другом драйвере или видимый дефект кадра с хэшем из списка 38 / VS-MS); контроль мёртв ⇒ одна починка, вторая неудача ⇒ `ТУПИК` |

Поправка очереди §48.2: Q6 — «Б7 — `НЕ ДЕФЕКТ` (F23b, п. 493); Б8 — в работе: F23c → F23d → F23e».

Дельта к строке курса: K4 −1 (Б7); счёт скриптом ближайшего закрытия сессии.
Не заявляется: что программы формы A ломаются на каком-либо драйвере; что в `data/` нет программ шейдеров; что свёртка `S_WQM` когда-либо срабатывала в игре; что Б8 — дефект или не дефект; что реестр полон.

## 62. Строка Б8 — приёмка F23c с отзывом F23d, исход ступени 1 (автор — лид, `HPP-589`; решение `ROADMAP.md` «СЕССИЯ 122» п. 498)

Данные — F23c `docs/track-f/f23c.md` (KytyPS5 `1ab783ef`), файлы `docs/track-f/f23c/`; отзыв F23d `docs/track-f/f23d-review.md` (KytyPS5 `07c46693`); решение — `ROADMAP.md` п. 498(а)–(м).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б8 (поправка к §4, §57, §61) | K4 | «не определено» | select `exec ? new : old` формы драйвера A (38 программ корпуса T1: PS 20, CS 18); класс ошибки — драйвер исполняет семантически равную программу с select формы A иначе, чем без него | в работе: ступень 1 — исход (i) п. 493(г): **класс ошибки драйвера жив на драйвере 616.56 этой машины** (RTX 5080 Laptop) [c] — читать «класс жив», не «историческая ошибка воспроизведена»; трансляция по умолчанию у эталона `0xe197e307a5f2cb39` верна (форму A снимает `PredicationElimination`); ступень 2 — **F23f** (Emu Engineer: реплей `f12_rd_k05`, `f13_rd`, 17 покрытых программ, две опоры RC1, нулевой на событии, годность RC3, счётчики `n_t`/`n_f`) → **F23g** (Red Team) → **F23h** (лид) | H: `KYTY_PRED_ELIM=0` против умолчания на эталоне — `N_diff` > 0 в 10 конфигураций из 10 (2 064 897 … 8 293 920 пикселей), нулевые 0, чувствительности > 0, слой валидации 0 ошибок; свой повтор F23d и пересчёт лида (`recount_f23e.out.txt`) — те же числа | покрыты снимками 17 из 38 (PS 7, CS 10); сцены снимков — `f12_rd_k05` (`underwater_aerial_garden`, установленный `540c035a`), `f13_rd` (`ending_boss_after_credit`) | п. 498(д): опоры не прошли H дважды ⇒ `ТУПИК`; `N_diff` > 0 на годном событии ⇒ `дефект`, итерация `KYTY_FIX_B8`; `N_diff` = 0 при `n_t` > 0 ⇒ `НЕ ДЕФЕКТ` на популяции «не найдено», драйвер 616.56; ни одной «не найдено» ⇒ пункт лида (снимки под замком или `ТУПИК`). Парковка (п. 498(е)): 21 непокрытая (`inv_f23c_programs.tsv`, `captures_present` = `-`), покрытые «не определено», программы вне T1, VS/MS, неопознанные модули снимков |

Поправка очереди §48.2: Q6 — «Б7 — `НЕ ДЕФЕКТ` (F23b, п. 493); Б8 — в работе: ступень 2 F23f → F23g → F23h (п. 498)».

Дельта к строке курса: 0 (Б8 открыт и остаётся открытым).
Не заявляется: что программы формы A ломаются в игре на каком-либо драйвере; что историческая ошибка воспроизведена; что H переносится на другие драйверы; что Б8 — дефект или не дефект; что реестр полон.

## 63. Строка Б8 — приёмка F23f с отзывом F23g, исход ступени 2 (автор — лид, `HPP-594`; решение `ROADMAP.md` «СЕССИЯ 122» п. 503)

Данные — F23f `docs/track-f/f23f.md` (KytyPS5 `11311fb1`), файлы `docs/track-f/f23f/`; F23g `docs/track-f/f23g-review.md` (KytyPS5 `f22eccf5`), файлы `docs/track-f/f23g/`; решение — `ROADMAP.md` п. 503(а)–(к).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б8 (поправка к §4, §57, §61, §62) | K4 | `НЕ ДЕФЕКТ` (на популяции) | select `exec ? new : old` формы драйвера A; класс ошибки драйвера жив на 616.56 (ступень 1, §62) | закрыт: `НЕ ДЕФЕКТ` по п. 228(д) на популяции «программы формы A корпуса T1 со статусом „не найдено“, драйвер 616.56» = {`0078153a1c1fb171` — CS, место `%784`, `OpImageSampleExplicitLod … Lod`} (п. 503(б)); **места вида эталона H (PS, неявный LOD) ни на одном годном событии не проверены — вывод на них не распространяется**; форма ошибки при ложном условии не проверена ни на одной программе | реплей F23f (две опоры без select прошли H с первой попытки; 42 события, годных 19, `N_diff` = 0 на 19 из 19); `0078153a1c1fb171` — 5 годных событий с собственным наблюдением и своими счётчиками (`n_t` = все дорожки, `n_f` = 0, `sens` 90 072 – 1 029 120), обращённые опоры на `f13_rd` 1082 [c F23g]; `be4c35a2031fd3f4` — «не определено» (RC1, RC2 F23g); пересчёт лида `recount_f23h.out.txt` `ALL OK` | `f13_rd` (`ending_boss_after_credit`), `f12_rd_k05` (`underwater_aerial_garden`) | парковка (п. 498(е), п. 503(д)): (1) 21 непокрытая (`inv_f23c_programs.tsv`); (2) 16 покрытых «не определено» поимённо (п. 503(д)(2)); (3) вне T1; (4) VS/MS; (5) неопознанные модули; **(6) места PS с `OpImageSampleImplicitLod` — первым `be4c35a2031fd3f4` (`f12_rd_k02`…`k08`)**. Переоткрытие: `N_diff` > 0 на годном событии программы строк (1)–(6) по методу с RC1–RC4 F23g, видимый дефект кадра с хэшем такой программы, `N_diff` > 0 у `0078153a1c1fb171` на другом кадре или драйвере; строка (6) — также пунктом лида, когда в очереди §48.2 не останется строк «в работе», кроме припаркованных |

Поправка очереди §48.2: Q6 — «Б7 — `НЕ ДЕФЕКТ` (F23b, п. 493); Б8 — `НЕ ДЕФЕКТ` на популяции (F23h, п. 503); парковка (е)(1)–(6)».

Дельта к строке курса: K4 −1 (Б8); счёт скриптом ближайшего закрытия сессии.
Не заявляется: что Б8 не дефект на местах PS с неявным LOD; что класс H на программах игры не найден; что программы формы A ломаются в игре на каком-либо драйвере; что историческая ошибка воспроизведена; что H переносится на другие драйверы; что форма при ложном условии проверена; что реестр полон.

## 64. Строки Ф5, Ф26 — чтение F16m: пара `f5cmu_*` и теги `f5id_*` (автор — лид, `HPP-586`; решение `ROADMAP.md` «СЕССИЯ 122» п. 504)

Данные — F16m `docs/track-f/f16m.md` (печать `641ed1ed`, итог §8 `6a19caeb`), пересчёт лида `C:/kyty/f287/lead/p504/p504recount.txt`, решение — `ROADMAP.md` п. 504(а)–(л).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Ф5 (поправка к §60) | K4 | члены 1–2: ветви 2 `dcc_fce_no_image` и 3 `meta_cs_untracked` — (Б) на 4 тегах из 4 ⇒ поправка набора B: счётчики — справкой, в B — «ключ ветви 2 / 3 формы (А) п. 492(д)(1) / (д)(4)»; ветвь 1 `cmask_fce_unapplied` — «не определено» (предел строк исчерпан, п. 496(б)(5)) | ветвь 1: 4 события из 4 — сброс корзинной проверки ложный [c пары], отличий листа в окнах нет (кадры входа чёрные, все до сцены); ветвь 2: единственный ключ сцены `(0x563800000, 0x5637f0000, r1)` — `cleared=1` (`sg`, `bh`) или нет потребителя 600 кадров и 0 чтений буфером (`ef`, `eb`); ветвь 3: только `tracked`/`img_clear`, `stale_apply` 0 | открыт: ветви 2–3 в сцене — `НЕ ДЕФЕКТ` по п. 228(д) на 4 сценах (переоткрытие — ключ формы (А) в сцене при `KYTY_DIAG_F5ID=1` или кадр-свидетель пары `KYTY_FIX_F5FCE` / `KYTY_FIX_F5CS`); ветвь 1 — повтор пары `f5cmu_0b`/`f5cmu_1b` с пределом 1024 и прогревом; 5 ключей формы (А) ветви 2 до сцены (путь входа `-lvl`, кадры GPU 0–20) — паркуются до итога повтора ветви 1 или ключа (А) в сцене | пара `f5cmu_0`/`f5cmu_1`, теги `f5id_sg`, `f5id_ef`, `f5id_bh`, `f5id_eb` на бинаре теста `d4328b0c` | `underwater_aerial_garden`, `enemy_final`, `big_hand_pirate_island`, `ending_boss_after_credit` | чтение повтора — п. 504(з); итерация **F16o** (Emu Engineer) → **F16p** (Red Team) → **F16q** (Harness Engineer) → **F16r** (лид) |
| Ф26 (поправка к §60) | K4 | кандидат кадра-свидетеля | `dcc_stale_bucket_only` 14 / 13 / 15 / 12 на 4 тегах, рост в сцене на 4 из 4; `dcc_stale_fallback` 0, `cmask_rt_bucket_only` 0 | открыт; итерация с парой под `KYTY_FIX_F26` (умолчание 0, точный ответ решает на `PrepareDccClear` и `AdoptPendingDccForTexture`) — F16o–F16r | счётчики тегов `f5id_*` [c пересчёта лида и `f26when.txt`] | 4 сцены выше; пара — `enemy_final` | п. 504(з): свидетель ⇒ `дефект` и итерация кода с критерием «ИСПРАВЛЕНО»; все `kept_applied` без отличий, ≥ 1 в сцене, предел не исчерпан ⇒ `НЕ ДЕФЕКТ` на `enemy_final` с переоткрытием |

Дельта к строке курса: 0 (Ф5 и Ф26 открыты).
Не заявляется: что ветвь 1 — дефект или не дефект; что очищенные на входе поверхности показываются в сцене; что ноль ключей формы (А) в сцене на четырёх сценах — свойство игры; что Ф26 меняет кадр; что реестр полон.

## 65. Строка Б4 — отгрузка FS6 (автор — лид, `HPP-558`; решение `ROADMAP.md` «СЕССИЯ 122» п. 478, факт п. 510)

Данные — FS6a (п. 461), FS6b (`HPP-556`), FS6c `docs/track-f/fs6c.md` (`ddabdc68`); пересчёт лида — `ROADMAP.md` п. 478(б).

| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | сцены [c] | критерий / очередь |
|---|---|---|---|---|---|---|---|
| Б4 (поправка к §52) | K1 (при выходе) → **`FIXED`, отгружен под (B)** | дефект; трек F | гонка аварийного выхода (`at_quick_exit` → `FileSystem::EmergencyShutdown` → `CloseAll`) с потоком гостя, держащим `File*`; правка `KYTY_FIX_B4` (`a86a5ad0`), умолчание `=1` — FS6a `3904522d` | **FS6 `9325446c` установлен 2026-10-05 02:12:47Z** вместо S12 `adb0c82f`; откат — копия `adb0c82f` или `KYTY_FIX_B4=0` | критерий до кода п. 412(г) (§52); FS6c: `fs6_v` 334,0 с, 0 смертей, 10 305 кадров 0 глитчей, `FixB4: mode=1` до `GuestOut`, выход за 3,8 с с кодом 0; `fs6_w` 0 `[Vulkan][E]`; лист пары `fs6_v`/`b4_v` без видимых дефектов (п. 478) | Sky Garden (`underwater_aerial_garden`) | закрыта; подпись и каталог варианта = S12 |

Дельта к строке курса: K1 −1 (Б4) на установленной; счёт скриптом ближайшего закрытия сессии. Поправка очереди §48.2: Б4 — закрыта.
Не заявляется: что Б4 воспроизводится в игре на текущих сборках и что его правка нужна игре; что p_s стенда — частота игры; что Б4 теряет сохранения;
что два выхода доказывают отсутствие фатала выхода в игре; что прочие 40 `SCENE_OK` держатся на FS6; что реестр полон.
