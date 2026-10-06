# F20l3 (`HPP-655`, Harness Engineer): ПК-A холодной формы `b32_pa`, затем серия Б32 на бинаре F20j4 — печать 3 до первого тега

Трек F, итерация F20 (Б32 Sky Garden), звено F20l3 по п. 591(в), (г), (д), (ж). Этот файл — печать 3: после её записи ридер, цепочка тега,
правила чтения и остановки не меняются; её sha256 пишется в json каждого тега (`prereg`), ридер сверяет её в допуске. **Вердикта нет:**
чтение ПК-A и серии — F20m3 (лид). Метки: [c] — код/лог прочитан или пересчитан, [I] — вывод, [U] — неизвестно.

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1; проверка — `refs_f20l3.py`, 14 ссылок)

- Решение звена — п. 591 `5da67c7e:docs/ROADMAP.md:23545` (якорь «591. **Звено F20m2 трека F (`HPP-649`, лид): чтение повтора контролей
  F20l2»; +1 — «(а) **Чтение контролей (решение лида»); поправка ПК-A — п. 591(в) `5da67c7e:docs/ROADMAP.md:23548` (+1 — «(г) **Серия
  п. 550(е) — назначается»); серия — п. 591(г) `5da67c7e:docs/ROADMAP.md:23549` (+1 — «(д) **У5(1) и сдвиг базы»); У5(1) — п. 591(д)
  `5da67c7e:docs/ROADMAP.md:23550` (+1 — «(е) **Наблюдение `b32_z0b`»).
- Правило: п. 550(д) `5da67c7e:docs/ROADMAP.md:23222`, (е) `…:23223`, (ж) `…:23224` (контроль +1 — следующий подпункт); У5(1) — п. 555(б)
  `5da67c7e:docs/ROADMAP.md:23264` (+1 — «(в) **Вопрос 1.**»); поправка цепочки — п. 574(д) `5da67c7e:docs/ROADMAP.md:23428` (+1 — «(е)
  **Повтор контролей — F20l2»); установка S18 — п. 590 `5da67c7e:docs/ROADMAP.md:23538` (+1 — «(а) **Установка по шагам»).
- Код холодной формы [c] (исходник FS8 `302347b4`, на нём построен F20j4): строка `ShaderSeed: compatibility=` печатается всегда —
  `302347b4:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:6424`; каталог зёрен ставится только при пустом `pipelines.bin` варианта —
  `…:6450`; без рецептов — строка `PipelinePrecache: no <путь> yet` — `…:6506`; каталог трансляции — папка варианта
  (`variant_fixb26_fixb1b_fixf10_fixf19` при умолчаниях) — `302347b4:src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp:589`.
- Бинарь тегов — тестовый F20j4: sha256 `2d0c8815389bdc42a2371ba813dc9460fc5565f21f89e32fad4d9e5bd2394dc7`, копия
  `C:/kyty/f287/bin/kyty_emulator_2d0c8815.exe`, подпись трансляции `9177b4267de1fb8bac7d1113afd8733210addfac` = FS8. **Установленный на момент
  печати 3 — S18**: sha256 `b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a` [c `sha256sum` 2026-10-06], закреплённая копия
  `C:/kyty/s288/bin/kyty_emulator_b3cee576.exe` (тот же sha).

## 1. Теги и форма

| тег | ручки (позиционно в `enter_scene.py`) | форма | в счёт |
|---|---|---|---|
| `b32_pa`, `b32_pa2` | `KYTY_DIAG_B32=1` | серии + **холодная трансляция** (п. 591(в)(1)) | ПК-A |
| `b32_s01` … `b32_s60` | `KYTY_DIAG_B32=1` | серии (п. 591(г)(2)) | удержания серии, `K` |
| `b32_z0c1` … `b32_z0c5` | `KYTY_DIAG_B32=0` | серии | база У5(1) по п. 591(д)(2); не в `K` и не в удержаниях |

- Общая форма — F20e + `KYTY_GPU_WALL=1` + M6: `enter_scene.py <тег> --level underwater_aerial_garden --attempts 1 --stable-draws 300
  --timeout 480 --no-install --require-idle --gates-file gates_default.txt --pred pred/f20l3_seal.md --rec --hold 330 KYTY_GPU_CLOCK_PIN=1
  KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 KYTY_DIAG_B32=<1|0>`; без валидации, RenderDoc, `KYTY_GPU_CHECKPOINTS`, `KYTY_GAME_PATCH`, стенда и
  нагрузчика; цепочка снимает все `KYTY_*` и `VK_LAYER_*` шелла до вызова. Имена `b32_sNN` и `b32_z0c<k>` — **вариант исполнителя**
  (лид их не назвал); повтор помехи — `<тег>_r<k>`, k ≤ 6.
- **Бинарь:** до замка установленный = S18 `b3cee576…` по полному sha256, иначе отказ (вопрос лиду); внутри замка после копии кэшей ставится
  копия F20j4 (проверка sha256, `installed_sha.txt`); после тега — S18 из закреплённой копии (проверка полного sha256, `installed_after.txt`);
  иначе `RETURN_FAILED`, замок остаётся. `C:/kyty/build/install` не трогается.
- **Кэши:** `_ShaderCache` (весь, с `PPSA21564/replay` и прочими каталогами вариантов), **`_ShaderSeeds`**, `_PipelineCache`, `_SaveData`,
  GLCache драйвера — копия до, возврат после (удаление живой папки и перенос копии), манифест sha256 до / прогона / после со строкой
  равенства (`manifest cmp EQUAL` — член допуска). Строки `lock taken|released <тег> <UTC>` — `runs/lock.log`; события —
  `C:/kyty/f287/times.txt`.
- **Холодная форма (`b32_pa`, `b32_pa2`; п. 591(в)(1)) — набор и способ.** После копии кэшей и до установки F20j4 `reserve_f20l3.py move`
  ПЕРЕНОСИТ из живой папки эмулятора в `runs/<тег>/reserve/`: (1) `_ShaderSeeds/PPSA21564` целиком (иначе `InstallShaderSeed` поставит
  каталог в пустую папку варианта — `…:6450`); (2) файлы программ корня `_ShaderCache/PPSA21564/{cs,ps,vs}_<16 hex>_<16 hex>.bin`; (3)
  `_ShaderCache/PPSA21564/pipelines.bin`; (4) каталог варианта тестового бинаря `_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19`
  целиком (трансляции и `pipelines.bin`). Не переносятся: `replay/` (S-replay S18; у F20j4, построенного от FS8, кода S-replay нет [c]),
  другие каталоги вариантов (не вариант тестового бинаря), `_PipelineCache`, `_SaveData`, GLCache драйвера. Перед переносом пишется
  `reserve.tsv` (строки формы манифеста). Неполный набор (нет `_ShaderSeeds/PPSA21564` или каталога варианта) — отказ до игры. После
  переноса `reserve_f20l3.py cold` проверяет, что ни одного элемента набора в живой папке нет (`COLD OK`), иначе отказ. **Возврат:** весь
  `_ShaderCache` и `_ShaderSeeds` из копии до тега (как у каждого кэша); затем `reserve_f20l3.py check` — каждая строка `reserve.tsv` есть в
  `manifest_after.tsv` (`RESERVE IN AFTER n of n`), резерв удаляется (список остаётся `runs/<тег>/reserve.tsv`); иначе `RETURN_FAILED`,
  замок остаётся.
- **M6** (`m6_f20l3.py`, справка): имена — только в `runs/<тег>/m6_local.txt` (в git не кладётся), в `m6.txt` — `<app>`.
- **Сторож игры пользователя и очередь** — как F20l2: блок тегов открывается двумя чистыми проверками с промежутком ≥ 600 с, в блоке
  ≤ 6 тегов (`guard_f20l3.py`); перед каждым тегом `queue_f20l3.py` (звенья Harness Engineer, кроме `HPP-655`; «готов вход» = `todo` /
  `in_progress` или идущий прогон) — `QUEUE BUSY` ⇒ тег не берётся (F20 последним в очереди замка, п. 462(г)); `runchk_f20l3.py` до замка
  (идущий прогон `HPP-655` = прогону, запустившему вызов). Вызов — `launch_f20l3.sh <тег>` (только запуск), ожидание — `wait_f20l3.sh <тег>`
  ≤ 540 с командой, разбор — `post_f20l3.sh <тег>` вне замка (`s51_vidglitch.py <rec> 4 6`, лист `sheet142.py`, ридер, `--table`, `--pka`,
  `--series`; после 10-го принятого тега серии — `--series --upto 10` в `series10.txt`).

## 2. Ридер `b32_read.py` (п. 550(г) с поправками п. 551(в), 552(в)(3), (г), 553(в), 554(г), 574(д), 581(в)(2), (в)(5); п. 591)

Всё правило F20l2 (печать 2 `C:/kyty/f287/f20l2/pred/f20l2_seal.md`, §2, п. 1–5) без изменений, кроме членов ниже.

1. **`θ_load`** (п. 574(б)(6), 591(г)(4)) — одна строка с первого столбца; нет строки или их две — лог не читается:

theta_load: 0.4562

2. **ПК-A холодной формы (п. 591(в)(2)).** Домен: каждый кадр сцены ридера F20c (кадры после первого кадра сцены, который идёт за первой
   строкой `Level has started: underwater_aerial_garden`; порога 10 с нет), которому ридер F20c приписал Б5, с `dt_us − instr_us` ≥ 100 000
   (`instr_us` = 0 без строки `DiagB32:`); каждый — по правилу (г)(2) с `θ_load`. Вооружён (как в F20l2): `EMU_RUN:Gpu` или класс `EMU_CALL:<…>`
   с последним потоком цепочки GuestGpu (роль `Gpu`). Член: кадров ≥ 3 и вооружённых ≥ 2/3 (3 × вооружённых ≥ 2 × кадров) — `ARMED`; кадров ≥ 3
   и < 2/3 — `FAIL` (повторный провал У1 по п. 574(в)(2)); кадров < 3 — `NOT_CALLED`. Справка: кадры Б5 вне домена по `instr_us`; кадры ≥ 100 мс
   от строки уровня до первого кадра сцены включительно (ридер F20c их не атрибутирует) — **не в домене** (буква «кадры, которые ридер F20c
   приписал Б5»).
3. **ПК-A по тегам (`--pka`, п. 591(в)(3)).** Решает принятый `b32_pa`; при `NOT_CALLED` — принятый `b32_pa2` один; оба `NOT_CALLED` —
   ПК-A «не вызван». Сумма кадров `b32_pa` + `b32_pa2` печатается рядом — **вариант исполнителя**, не решает.
4. **Допуск холодной формы (члены, только `b32_pa`, `b32_pa2`):** `reserve_move.txt` — `RESERVE MOVED`; `reserve_cold.txt` — `COLD OK`;
   `reserve_check.txt` — `RESERVE IN AFTER`; в логе ≥ 1 строки `PipelinePrecache: no … yet`, 0 строк `PipelinePrecache: <N> recipes` и 0 строк
   `ShaderSeed:`, кроме `ShaderSeed: compatibility=`. У тегов тёплой формы — нет ни одного из трёх файлов резерва (член); строки
   `PipelinePrecache` — справка.
5. **Серия (`--series`, п. 550(е)(2)–(3), 591(г)(5)).** Теги серии — принятые `b32_sNN` (принятый повтор `b32_sNN_r<k>` стоит за своё имя);
   удержание — принятый тег с удержанием (сцена ≥ 300 с); `K` — удержания с ≥ 1 кадром в счёте; класс удержания — класс самого длинного
   кадра в счёте (печатается и семейство). Остановка: удержаний < 29 — `CONTINUE`; ≥ 29: `K` ≥ 3 — `STOP_READ`; `K` = 0 — `STOP_U2`; `K` = 1–2 —
   `CONTINUE` до `K` = 3 (`STOP_READ`) или 60 удержаний (`STOP_U2PRIME`). Доли семейств от `K` по (г)(3)(i)–(iv) печатаются справкой — читает
   F20m3. `b32_pa*` и `b32_z0c*` в серию не входят.
6. **У5 серии (п. 550(ж), 555(б), 591(д), (в)(6))** — по принятым тегам серии (`=1`): (1) срабатывает, только если медиана медиан тегов окна
   723–828 отличается от медианы базы > 2 % И точный двусторонний критерий Манна — Уитни (ничьи — средним рангом; полный перебор
   распределения суммы рангов, `mw_exact`) медиан тегов против медиан базы даёт p < 0,05; база — 11 тегов F20e (медиана 36 171,5), после пяти
   принятых `b32_z0c` — 7 тегов `b32_z0` (36 451,5), `b32_z0b` (41 478,5), `b32_z0c1`…`b32_z0c5` (п. 591(д)(2)); доля тегов с медианой > 40 000 —
   справка; (2) кадров ≥ 70 мс на удержание > 1,5 × 0,561; (3) среднее `dt_us` всех кадров Б5 тегов серии (взвешенно) > 1,25 × 134 767,7; нет кадров
   Б5 — «не вычисляется», в «любое из» не входит; (4) ненулевой инвариант `_w` в ≥ 2 тегах. Строка `U5 ANY`. Базы (2)–(4) — прежние
   (`U5_BASE`, F20l).

## 3. Допуск тега и помеха (п. 273(з))

Члены F20l2 (печать 2 §3) с заменами: `binary_sha256` = F20j4 `2d0c8815…`; установленный до = после = S18 по полному sha256; `prereg` =
sha256 этой печати; env = константы харнесса + форма тега (`KYTY_DIAG_B32`, `KYTY_GPU_WALL=1`), ничего больше; строки `TestB32` — нет;
нагрузчика (`load.json`) — нет; плюс члены §2 п. 4. Член не прошёл ⇒ помеха: тег в счёт не идёт, повтор `<тег>_r<k>`; событие окна
(`Window <id> minimized`, `Recovering Vulkan swapchain`) — строка допуска «событие окна», серия стоит, вопрос лиду о повторе. Процесс
пользователя, отказ `procload`, замок, `enter_scene` не стартовал, прогон агента не жив — каталог `<тег>.user_*` / `.busy_*` / `.lock_*` /
`.nostart_*` / `.gone_*`, повтор тем же именем, попыткой не считается.

## 4. Порядок, остановки, бюджет (п. 591(в), (г)(5)–(6), (д); вариант исполнителя помечен)

1. `b32_pa` → `--pka`. `ARMED` — серия с `b32_s01` в том же звене (п. 591(в)(5)). `FAIL` — стоп звена до серии, факт и таблица — F20m3
   (п. 591(в)(4)). `NOT_CALLED` — `b32_pa2`; снова `NOT_CALLED` — стоп до серии, чтение F20m3 (не провал У1, п. 591(в)(3)). Помеха на
   `b32_pa*` — повтор `_r<k>`.
2. Серия: теги по порядку номеров, после каждого — разбор и `--series`; остановка по §2 п. 5.
3. **После 10-го принятого тега серии** (`series10.txt`, только первые 10) и **в конце** — У5 по §2 п. 6 (все четыре члена — по п. 550(ж)
   «после 10-го тега серии и в конце (все)»). Срабатывает У5(1) против F20e — 5 тегов `b32_z0c1`…`b32_z0c5` (`=0`), затем пересчёт против 7
   тегов `=0`: снова срабатывает — стоп серии, чтение F20m3; нет — серия продолжается с базой из 7 тегов до конца. Срабатывает любой из
   У5(2)–(4) — стоп серии, чтение F20m3 (п. 550(ж) «одна переделка» решает лид). У5(1) только в конце — та же проверка (5 тегов `b32_z0c`) до
   передачи F20m3.
4. **Бюджет замка (п. 591(г)(5)):** ≤ 60 тегов серии + ≤ 2 тега ПК-A + ≤ 5 тегов `b32_z0c` + повторы помех ≤ 6 (на всё звено); исчерпан
   бюджет серии — исход п. 550(е)(3) по счёту; седьмая помеха — стоп и вопрос лиду.
5. Перед каждым тегом — проверка замка, `STOP`, комментариев звена и API серий (строка `times.txt`), очередь `queue_f20l3.py`; блоки сторожа
   ≤ 6 тегов.

## 5. Таблица звена

По каждому тегу: допуск, бинарь (json) и подпись (строка `ShaderSeed`), sha256 лога и `read.txt` (оба sha), `K_I` / `K`, классы кадров в
счёте, `INSTR_MADE`, `kq_n` = 0, `m5r_us` > 0, ПК-A (старый домен ≥ 10 с и холодный домен), У5(1) и У5(4), `Recovering Vulkan swapchain` —
`b32_read.py --table` (`table.txt`), сводки `pka.txt`, `series.txt`, `series10.txt` и отчёт `docs/track-f/f20l3.md`.

## 6. Проверки до печати

`test_b32_read.py` — набор F20l2 (правило п. 574(д), роды, классы, RC6, RC7, RC13, `INSTR_MADE`, `θ_load`, стенд, У5 по тегу) и новые
фикстуры: домен ПК-A холодной формы (кадр Б5 на 0,13 с — в домене, вне старого; край `dt_us − instr_us` 99 999 / 100 000; `dt_us`
99 999 / 100 000; кадр без строки `DiagB32` — `NO_SAMPLES`; не Б5 — вне домена; классификация с `θ_load` — `HOST_LOAD`), член
`pka_member` на краях 2/3, `NOT_CALLED` при < 3, `EMU_CALL` на GuestGpu; кадры до первого кадра сцены (справка, край 100 000); строки
`PipelinePrecache` и `ShaderSeed` (пять строк совместимости — не «прочие»); допуск холодной формы (каждый член отдельно), тёплой (файлы
резерва — отказ), `=0` / `=1` по тегу, S18 до / после (последняя hex-цифра), бинарь S18 в json — отказ, имена тегов (края `s00`, `s60`,
`s61`, `z0c6`, `_r7`, старые имена); точный критерий Манна — Уитни против полного перебора (с ничьими), `u5_one` на краях (2,29 % при
p < 0,05 — да; > 2 % при 0,05 ≤ p < 0,10 — нет; 1,9 % — нет; двусторонний), база F20e — 11 медиан ровно, база `=0` — из `read.json` F20l / F20l2;
серия: 28 / 29 удержаний, `K` 0 / 2 / 3, 59 / 60 удержаний, помеха и повтор, удержание без сцены 300 с, `b32_pa` и `b32_z0c` вне серии,
`--upto 10`, У5(1) с базой 7 / 6 тегов, непринятый `b32_z0c5`, У5(2)–(4) на краях; `--pka` во всех исходах. `sens_b32.py` — 172 правки ридера
(правки F20l2 и новые), каждая ловится: первый прогон пропустил 12 (`cold precache no line not needed`, `seed other includes compatibility`,
`pk3 theta off`, `pre-scene strict`, `u5 2 % strict edge to 3 %`, `u5 p 0.10`, `u5 F20e base wrong value`, `u5 z0b median wrong`, `series K
without hold`, `u5(3) factor 1.3`, `pka pa2 decides first`, `stand mode not checked`) — ридер не менялся, добавлено 12 фикстур
(`test_add_section.py`), второй прогон — 0 пропусков. `test_tools_f20l3.py` — `reserve_f20l3.py` на поддельной папке эмулятора (набор,
что остаётся, `reserve.tsv` = строки манифеста до, `COLD OK` / `NOT`, `RESERVE IN AFTER` / `NOT`, отказы при неполном наборе и существующем
резерве), отказы и сухие прогоны `go` / `launch` / `post` по тегам, константы S18, порядок шагов холодной формы в `go`; `test_guard_f20l3.py` —
порт F20l2. Регрессия ридера `regress/regress_b32.py` на логах F20e `f20_v35`, `f20_v32` (тёплые) и холодном прогреве FS8e `log_fs8_i.txt` [c]:
домен ПК-A холодного лога — 5 кадров Б5 (все `NO_SAMPLES`: строк `DiagB32` нет), `PipelinePrecache: no … yet` 1, строк рецептов 0. Мутанты
`mutlib` не гонялись — форма F20l / F20l2 (ручная чувствительность `sens_b32.py`, как в печатях 1 и 2). Счёт проверок и sha256 выводов — строки
`seal:` ниже.

## 7. Не заявляется

Что ПК-A холодной формы доказывает распознавание кадров Б5 тёплого удержания; что холодная форма воспроизводит механизм тёплых кадров Б5;
что каталог S15f — причина исчезновения кадров Б5; что инструмент не меняет частоту Б32; что `=0` тестового бинаря равен FS8 в машинном
коде; что выводы о коде FS8 тестового бинаря переносятся на установленный S18; что Б32 вызван ожиданием потока гостя, нагрузкой хоста, выводом
кадра или `VirtualProtect`; что Б32 вызван или не вызван путём Б24 / Ф8; что реестр полон; ни одно число — не выигрыш; 60 FPS не обещаются.

## 8. Строки печати (sha256 файлов и последних выводов наборов)

- `test_b32_read.out.txt`: checks 362; ALL OK; первая строка набора: `suite test_b32_read.py sha256 7b0ebf2c89c1edf40be1df994b1dac90bf3e990c525009f6fedf973f2f66c541 target b32_read.py sha256 1a90f561824ba53d93a905ed5db4fad05b4ac5e`
- `sens_b32.out.txt`: edits 172 missed 0; ALL OK; первая строка набора: `suite sens_b32.py sha256 2da7494465b9f78a95f3eea75543c01740b6677e326b42571ccece878914bbb5 target b32_read.py sha256 1a90f561824ba53d93a905ed5db4fad05b4ac5eaca4c`
- `test_guard_f20l3.out.txt`: checks 61, failed 0; ALL OK; первая строка набора: `suite test_guard_f20l3.py sha256 742b02d31cf1f7d23b313181a9c85be7e27e5f59a979271a5571217e24d3868c target guard_f20l3.py sha256 bb92601263d78ed7032802db92ae5d823`
- `test_tools_f20l3.out.txt`: checks 121, failed 0; ALL OK; первая строка набора: `suite test_tools_f20l3.py sha256 8c4322602540dd4e2114ebf4a36441a74dea480796478d3260e8df81ff9df9e2 target enter_scene.py sha256 c56e4a9b32d14af96d00e26ab3d5d3361`
- `regress/regress_b32.out.txt`: REGRESS PASS; ALL OK; первая строка набора: `suite regress_b32.py target b32_read.py sha256 1a90f561824ba53d93a905ed5db4fad05b4ac5eaca4cd6edafd13157b1b312e2`
- `refs_f20l3.out.txt`: refs 14; ALL OK; первая строка набора: `suite refs_f20l3.py refs 14`

seal: 1a90f561824ba53d93a905ed5db4fad05b4ac5eaca4cd6edafd13157b1b312e2 C:/kyty/f287/f20l3/b32_read.py
seal: 5a986c03d161b9a5c52d589ad1da87e4676ceb9bac61acaeaa8f2131525400fa C:/kyty/f287/f20l3/f20e_read.py
seal: 7b0ebf2c89c1edf40be1df994b1dac90bf3e990c525009f6fedf973f2f66c541 C:/kyty/f287/f20l3/test_b32_read.py
seal: 2da7494465b9f78a95f3eea75543c01740b6677e326b42571ccece878914bbb5 C:/kyty/f287/f20l3/sens_b32.py
seal: 629e1cfec7a1ea2df66f378b099bca821ba9a09ce5a246027146eaa951590f5b C:/kyty/f287/f20l3/reserve_f20l3.py
seal: 6d6381865b43e6777f604f575d613c62292cb5c2842296217f47a40897279aeb C:/kyty/f287/f20l/base/base_f20l.txt
seal: 9172472baeec4306faf5c82dd8f81a347dae1c585c3d5ca5e1992c8288a73466 C:/kyty/f287/f20l/runs/b32_z0/read.json
seal: d2cf2d419f267f705b737c6b19762e5738b54346b04d8308a5bc6a977e9141d9 C:/kyty/f287/f20l2/runs/b32_z0b/read.json
seal: 2e4c1795ef97c234103ec3fd3fab3f399800e69f804b04328e4306ea3b58abff C:/kyty/f287/f20l2/pred/f20l2_seal.md
seal: 0f3a33d31c86d81fbfc3f2b3b4ef874d02ad4f204228ba38de684369fea317f1 C:/kyty/f287/f20l3/port_f20l3.py
seal: 6b401c3e0e616355e71bb91d16042b0c64d6aa8dbb0114a9f69a05b2d9ac10f9 C:/kyty/f287/f20l3/edit_f20l3.py
seal: 371e87f904b7f9a487e53521d6c7e85ac0acc9991cf8927ed1862de611a265fb C:/kyty/f287/f20l3/edit_test_f20l3.py
seal: 39d61ce1068a8f0586bbcd345d861b32723d7d35cf754dbae0a0a18b179821c1 C:/kyty/f287/f20l3/edit_sens_f20l3.py
seal: 7405615c24a98597f803e8876332c203cc95881019ec6638460d8fd13561bc9d C:/kyty/f287/f20l3/test_new_section.py
seal: 6c9a2b26eda811259591d302694bb62b4389b1b459a36dcd9a10cc900a9e3d0a C:/kyty/f287/f20l3/test_add_section.py
seal: 083baf997b1be6e9d718d6b96195476532b8f57944ee8329ae0e871acfe2e225 C:/kyty/f287/f20l3/gen_refs.py
seal: 6f3b14a0a94f175554001c94034bec9184460bc4b5e91caaf4d9848d92f27efd C:/kyty/f287/f20l3/f20l3_seal_body.md
seal: 224fe4c94f15eb0d86e8625c1be632e954d519c70942e6f070422313d5ef284e C:/kyty/f287/f20l3/m6_f20l3.py
seal: 0c9db8a5f52c35af98fffd01616ea1d051a1c8d0e07c1db8307237820ce0e72a C:/kyty/f287/f20l3/go_f20l3.sh
seal: 7d204f33d70c7a4c2fbbb2f380d8ac7ed33e0c8d0cf74647a1733bf98b488cf9 C:/kyty/f287/f20l3/launch_f20l3.sh
seal: ea24d21814a8740cae4c04635a56aa11d9911051f219946e02699a7a0aef800c C:/kyty/f287/f20l3/wait_f20l3.sh
seal: be739fa621a87cd71cca9d01b950782dc7e974eb23353ad7eb9073e63645a4bf C:/kyty/f287/f20l3/post_f20l3.sh
seal: bb92601263d78ed7032802db92ae5d8230e908cb5e4160e1b2df16e4b3945e33 C:/kyty/f287/f20l3/guard_f20l3.py
seal: d3742facfe41cc174ff85167cc14d6e7e9e00def0ce2b1130658759ac1fa352d C:/kyty/f287/f20l3/queue_f20l3.py
seal: c56e4a9b32d14af96d00e26ab3d5d336137bc343023299a9c8679c20fc359c3f C:/kyty/f287/f20l3/enter_scene.py
seal: d72cd59ade908a5bf48d29dfe2afe8d69a3b6bef22e3ca9f0716565c494417c5 C:/kyty/f287/f20l3/runchk_f20l3.py
seal: d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0 C:/kyty/f287/f20l3/procload.py
seal: a7096fd47f70419a5ed8d541778294f3032ca2c88e7b4b2e946f3d99651182bb C:/kyty/f287/f20l3/manifest_fs4c.py
seal: c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d C:/kyty/f287/f20l3/sheet142.py
seal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 C:/kyty/f287/f20l3/gates_default.txt
seal: f16411dbe6e89b9d47dfa5775f4451450f5aeac1aa081a03dcd12b101a74d227 C:/kyty/f287/f20l3/watch_f20l3.py
seal: c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96 C:/kyty/f287/f20l3/idle142.py
seal: 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 C:/kyty/f287/f20l3/run_safety99.py
seal: c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21 C:/kyty/f287/f20l3/launch_run.py
seal: 742b02d31cf1f7d23b313181a9c85be7e27e5f59a979271a5571217e24d3868c C:/kyty/f287/f20l3/test_guard_f20l3.py
seal: 8c4322602540dd4e2114ebf4a36441a74dea480796478d3260e8df81ff9df9e2 C:/kyty/f287/f20l3/test_tools_f20l3.py
seal: 1cf9a005c1f5b226c392867a9d981a0b94da6cd6894fbe527c2fcd0899966d87 C:/kyty/f287/f20l3/refs_f20l3.py
seal: d9e7478cce0f7e36e84543c46cf449f54800dd7d92b2028317b2004e0b1da4d0 C:/kyty/f287/f20l3/regress/regress_b32.py
seal: d2b632843d4f2ea853354888b6f46682f41a082f5aa08ab4e98bd06952fa7680 C:/kyty/f287/f20l3/test_b32_read.out.txt
seal: 8ca4f730bdd072cac24585cfa2a34d3b134cd79ea5e9c6fb82ff63c13ea46794 C:/kyty/f287/f20l3/sens_b32.out.txt
seal: b16db6e3bc442c01a2d538351f9926bb63ede0a352ba86587890d178853bbf52 C:/kyty/f287/f20l3/test_guard_f20l3.out.txt
seal: ed4060249976607ff86b0d10ebd93deb3d93b3f54bb441e6fc3260eec96d9b95 C:/kyty/f287/f20l3/test_tools_f20l3.out.txt
seal: 89768e3e39656e0a8f1ada03e22bebc1bdfacf9323b1a8defb1a49e8c9623340 C:/kyty/f287/f20l3/regress/regress_b32.out.txt
seal: 02dd16cbae01410040c993760715ec2fb7fd78d57a6a093e4729b104e76983b8 C:/kyty/f287/f20l3/refs_f20l3.out.txt
seal: 2d0c8815389bdc42a2371ba813dc9460fc5565f21f89e32fad4d9e5bd2394dc7 C:/kyty/f287/bin/kyty_emulator_2d0c8815.exe
seal: b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a C:/kyty/s288/bin/kyty_emulator_b3cee576.exe
seal: 6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c C:/kyty/scripts/s51_vidglitch.py
