# F20l (`HPP-631`, Harness Engineer): ридер `b32_read.py` и пять контрольных тегов `KYTY_DIAG_B32` — печать 1 до первого тега

Трек F, итерация F20 (Б32 Sky Garden), звено F20l по п. 550(з). Этот файл — печать: после его записи ридер, цепочка тега и правила
чтения не меняются; его sha256 пишется в json каждого тега (`prereg`), ридер сверяет её в допуске. **Вердикта нет:** чтение контролей,
У1, число `θ_load` и назначение серии — F20m (лид). Метки: [c] — код/лог прочитан или пересчитан, [I] — вывод, [U] — неизвестно.

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1)

- Решение звена — п. 550: `fe0bf0a0:docs/ROADMAP.md:23217` (якорь «550. **Звено F20i трека F (`HPP-628`, лид; приёмка F20g»; +1 —
  «(а) **Приёмка строкой. F20g ✓**»); правило чтения — п. 550(г) `fe0bf0a0:docs/ROADMAP.md:23221`, контроли — п. 550(д)
  `fe0bf0a0:docs/ROADMAP.md:23222`, убийство У5 — п. 550(ж) `fe0bf0a0:docs/ROADMAP.md:23224`, задание — п. 550(з)
  `fe0bf0a0:docs/ROADMAP.md:23225`.
- Поправки: п. 552(в)(3), (г), (д), (е)(3) — `aaf4504e:docs/ROADMAP.md:23237` (якорь «552. **Звено F20k трека F (`HPP-630`, Red Team;
  приёмка лида»; +1 — «(а) **Приёмка строкой. F20k ✓**»); п. 553(б), (в) — `8f3ee6ad:docs/ROADMAP.md:23246` (якорь «553. **Звено F20j2
  трека F (`HPP-633`, Emu Engineer;»; +1 — «(а) **Приёмка строкой. F20j2 ✓**»); п. 554(г), (д) — `3c2ece7b:docs/ROADMAP.md:23254`
  (якорь «554. **Звено F20k2 трека F (`HPP-634`, Red Team; приёмка лида»; +1 — «(а) **Приёмка строкой. F20k2 ✓**»); комментарии лида в
  `HPP-631`: `4c26ed76` (п. 552), `0566ea51` (п. 553), `5ad97680` (п. 554(г)).
- Бинарь тега — тестовый F20j2: sha256 `b9e0ee0092ca1504979ebd674abb21c8d67015fd030bc33615eb2c87acb90f91`, копия
  `C:/kyty/f287/bin/kyty_emulator_b9e0ee00.exe`, подпись трансляции `9177b4267de1fb8bac7d1113afd8733210addfac` = FS8 (п. 553(а)); F20k2 —
  `PASS`, RC 0 (п. 554). Установленный — FS8 `2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b`, закреплённая копия
  `C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe`.

## 1. Теги и форма (п. 550(д), (е)(1), (з)(4))

| тег | ручки (позиционно в `enter_scene.py`) | нагрузчик харнесса |
|---|---|---|
| `b32_z0` | `KYTY_DIAG_B32=0` | — |
| `b32_pp` | `KYTY_DIAG_B32=1 KYTY_TEST_B32=60:present:200` | — |
| `b32_pc` | `KYTY_DIAG_B32=1 KYTY_TEST_B32=60:gpusleep:200` | — |
| `b32_pd` | `KYTY_DIAG_B32=1` | все логические CPU (`ncpu`), класс `ABOVE_NORMAL`, 400 мс |
| `b32_pd2` | `KYTY_DIAG_B32=1` | ⌈`ncpu` / 2⌉ процессов, класс `ABOVE_NORMAL`, 400 мс |

- Общая форма — V Sky Garden тега F20e: `enter_scene.py <тег> --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480
  --no-install --require-idle --gates-file gates_default.txt --pred pred/f20l_seal.md --rec --hold 330 KYTY_GPU_CLOCK_PIN=1
  KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 <ручки>`; без валидации, RenderDoc, `KYTY_GPU_CHECKPOINTS`, `KYTY_GAME_PATCH`; цепочка снимает все
  `KYTY_*` и `VK_LAYER_*` шелла до вызова.
- **Бинарь:** до замка установленный = FS8, иначе отказ (вопрос лиду); внутри замка после копии кэшей ставится копия F20j2 (проверка
  sha256 = `b9e0ee00…`, `installed_sha.txt`); после тега — FS8 из закреплённой копии (проверка sha256, `installed_after.txt`); иначе
  `RETURN_FAILED`, замок остаётся (форма F19e `go_f19e.sh`). `C:/kyty/build/install` не трогается.
- **Кэши:** `_ShaderCache` (с `pipelines.bin`), `_PipelineCache`, `_SaveData`, GLCache драйвера — копия до, возврат после, манифест sha256
  до / прогона / после со строкой равенства (форма F20e). Строки `lock taken|released <тег> <UTC>` — `C:/kyty/f287/f20l/runs/lock.log`;
  события — `C:/kyty/f287/times.txt`.
- **M6** (`m6_f20l.py`, справка, не член): раз в 1 с CPU посторонних процессов (≥ 0,5 CPU с/с, верхние 3) и их сумма; эмулятор — `game`,
  процессы нагрузчика — `loader`; имена — только в `runs/<тег>/m6_local.txt` (в git не кладётся), в `m6.txt` — `<app>`.
- **Нагрузчик** (`b32_load.py`, теги `b32_pd`, `b32_pd2`): ждёт файл PID своего эмулятора, читает живой `_kyty.txt` с начала (без
  `tail -F`: один дескриптор, чтение новых байтов раз в 50 мс) до первой строки `Level has started: underwater_aerial_garden` (взвод — та
  же строка, что у стендов); при взводе порождает процессы-нагрузчики (ждут событие, класс `ABOVE_NORMAL` читается обратно); через 60 с
  от взвода — `n_start` (последний `FrameTrace: n=` живого лога), 400 мс работы, `n_end` (через 0,3 с после конца). `load.json`:
  `status`, `mode`, `ncpu`, `workers`, `priority_class`, времена UTC, `burst_s`, `arm_to_burst_s`, `worker_cpu_s`, `n_start`, `n_end`.
- **Сторож игры пользователя и очередь** (общее правило 33, п. 534(в); п. 462(г)): `guard_f20l.py` — порт F20e (убийство только своего
  дерева по PID; `scan` до замка и сразу после; `watch` во время тега; `wait-gone` до возврата бинаря и кэшей); блок тегов открывается
  двумя чистыми проверками с промежутком ≥ 600 с, в блоке ≤ 6 тегов; перед каждым тегом — `queue_f20l.py` (звенья Harness Engineer кроме
  `HPP-631`; «готов вход» = `todo` / `in_progress` или идущий прогон) — `QUEUE BUSY` ⇒ тег не берётся (F20 последним в очереди замка).
- Порядок: `b32_z0`, `b32_pp`, `b32_pc`, `b32_pd`, `b32_pd2`. Вызов — `launch_f20l.sh <тег>` (только запуск), ожидание —
  `wait_f20l.sh <тег>` ≤ 540 с командой, разбор — `post_f20l.sh <тег>` вне замка (`s51_vidglitch.py <rec> 4 6`, лист `sheet142.py`,
  ридер, таблица).

## 2. Ридер `b32_read.py` (п. 550(г) с поправками п. 551(в), 552(в)(3), (г), 553(в), 554(г))

Атрибуция Б5 / Б33 / Б1б / «только `PriorityStall:`» / «ничего» — ридер F20c как есть (`f20e_read.py` — копия файла F20e, sha256
`5a986c03…`, сверяется при запуске; функции `scan`, `attr`, `evaluate`). Определения сцены, первого кадра сцены, интервала, кадра
удержания (≥ 100 000 мкс, начало ≥ 10 с сцены), удержания (сцена ≥ 300 с) — F20e без изменений.

1. **База (RC15):** 10 ближайших кадров сцены до и 10 после с `dt_us` < 100 000 (F20g §1.1); медианы `dt_us`, `lat_us`, `gpu_busy_us`
   строк `FrameTrace`; `E = dt_us − медиана dt_us`.
2. **`P_I`** — кадры удержания, которые ридер F20c не приписал Б5 / Б33 / Б1б (на `b9e0ee00` сохранение кэша не атрибутирует — буква
   F20e). **`K_I`** = 1 у удержания с ≥ 1 кадром `P_I` (п. 552(г)). **`INSTR_MADE`** — кадр `P_I` со строкой `DiagB32:` и `dt_us`
   (`FrameTrace`) − `instr_us` < 100 000. **В счёте** — `P_I` без `INSTR_MADE`; `K` = 1 у удержания с ≥ 1 кадром в счёте.
3. **Класс — первое совпадение:** (i) `HOST_FREEZE` — `sgap_max_us` ≥ 0,5 × E; (ii) `NO_SAMPLES` — нет строки `DiagB32:` с этим `n`
   (ключ — поле `n=`, отчёт кадра `n` печатается после строки `FrameTrace` кадра `n+1`, п. 551(б)(5)), `i2` ≠ 1, `samples` = 0, нет строки
   `DiagB32-x` этого `n` или ≠ 0 любое из `slot_full_w`, `torn_w`, `ring_drop_w`, `sgap_bad_w`, `lines_cut_w`, `req_miss_w`, `sub_miss_w`
   (п. 552(в)(3), комментарий `4c26ed76`); (iii) `HOST_LOAD` — `other_us` ≥ `θ_load` × `ncpu` × окно (окно — `dt_us` строки `DiagB32:`):
   **в контролях `θ_load` нет — класс не выдаётся (п. 550(д)(6)), печатается отношение `other_us` / (`ncpu` × окно)**; (iv) цепочка:
   держатель — поток вывода (`vo_slot`), если `lat_us` − медиана `lat_us` ≥ 0,5 × E, иначе `flip_slot`; у потока по долям выборок окна
   (счёт ≥ 0,5 × `samples`): `H:<call>` — `protect` / `fault` / `drain` / `qlock` ⇒ `EMU_CALL:<call>`; `present` / `acquire` / `qsubmit` /
   `semwait` ⇒ деление RC7: `EMU_LOCK` (другой поток с `H:qlock` ≥ 0,5 × `samples` окна), иначе `DRV_GPU` (`gpu_busy_us` ≥ медиана + 0,5 × E),
   иначе `DRV_HOST`, печать `EMU_CALL:<call>><ступень>`; `W:sleep` ⇒ `GUEST_SLEEP:sleep`; `W:<kind>` ⇒ запись `-w` этого потока и рода с
   наибольшим `overlap_us`: `to=1` ⇒ `GUEST_SLEEP:<kind>`, нет записи или `waker` < 0 ⇒ `GUEST_SLEEP:<kind>`, иначе шаг к `waker` (мьютекс:
   `waker` записи = владелец при входе = `peer`; без записи — `peer` строки `-t`); `R` ⇒ `EMU_RUN:<роль>` (роль ≠ `guest`) /
   `GUEST_RUN:<имя>`; `Sr` ⇒ `HOST_PREEMPT`; `Sw` или `S` ⇒ `UNMARKED:<имя>` (при `kstate=0` — пометка «вытеснен или ждёт вне меток, не
   различимо»); иначе `UNDETERMINED`. RC6: `GUEST_RUN` / `GUEST_SLEEP` остаётся, только если у GuestGpu (`gpu_slot`) `R` + ΣH < 0,5 ×
   `samples` и `W:gpu_regmem` < 0,5 × `samples`; иначе `GUEST_POLL`; нет строки GuestGpu ⇒ `UNDETERMINED`. Держатель + не больше 3 шагов
   (4 потока); 4-й шаг, цикл или поток без строки `-t` ⇒ `UNDETERMINED`.
4. **Семейство** — класс без `:<деталь>`; у вызова драйвера — ступень RC7. **Класс удержания** — класс самого длинного кадра в счёте.
5. **ПК-A** (п. 550(д)(7)): кадры удержания с атрибуцией Б5, классифицированные по (i)–(iv) без условия счёта; член «вооружён» —
   `EMU_RUN:Gpu` или путь `EMU_CALL:<…>`, кончающийся на GuestGpu. Порог ≥ 2/3 при ≥ 3 кадрах читает F20m.
6. **Стенд** (`b32_pp`, `b32_pc`): три строки `FrameTrace` после строки `TestB32: fire`; кадр стенда — самый длинный из них, с классом и
   держателем. **Окно нагрузки** (`b32_pd`, `b32_pd2`): кадры `n` ∈ [`n_start`, `n_end` + 3] из `load.json`; «затянувшийся» — `dt_us` ≥
   100 000 (иначе ПК-D «не вызван»); у каждого со строкой `DiagB32:` — `other_us` / (`ncpu` × окно).
7. **Члены печати по тегу:** `K_I`, `K`, `P_I`, в счёте; `INSTR_MADE` и доля среди кадров ≥ 100 мс (п. 552(г)); число кадров ≥ 100 мс с
   `kq_n` = 0 и доля (п. 553(в)); число кадров с `m5r_us` > 0 (п. 553(б)(1) — исполнение п. 552(е)(3)); число строк `Recovering Vulkan swapchain`
   (п. 553(б)(2)); **число кадров в счёте, чей предыдущий кадр ≥ 100 мс (п. 554(г))**; классы по кадрам; ПК-A; стенд / окно нагрузки;
   У5(1)–(4); долги п. 552(е)(1)–(2): кадров `NO_SAMPLES` с `slot_full_w` ≠ 0, непечатных имён потоков; `rep_drop`; I5 (`dt_us`
   `DiagB32:` против `FrameTrace` > 1 мс); последняя строка `-x`. Знаменатель долей — `P_I`; рядом — по всем кадрам ≥ 100 мс сцены со
   строкой `DiagB32:` (вариант исполнителя, справка).
8. **RC13** — на каждом теге: атрибуция ридера F20c на логе = на том же логе без строк, начинающихся с `DiagB32` (кадры и кадры удержания
   совпадают); строки с текстом `DiagB32` не с первого столбца считаются (`diag_bad_prefix`).

## 3. Допуск тега и помеха (п. 550(з)(4), п. 551(в), п. 462(г), п. 534)

Члены: json есть; `binary_sha256` = `b9e0ee00…`; установленный до = после = FS8 `2c9b69b9…`; `prereg` = sha256 этой печати; `env` —
константы харнесса F20e + ровно ручки формы тега (`KYTY_DIAG_B32`, `KYTY_GPU_WALL=1`, у `pp`/`pc` — `KYTY_TEST_B32`); последние
`--vulkan-validation` и `--shader-validation` — `false`, `--rd` нет; аргументы гостя `-lvl underwater_aerial_garden`; удержание 330 с; лог
есть; сцена вошла; `Window <id> minimized` и `Recovering Vulkan swapchain` — 0; кэши возвращены (`manifest cmp EQUAL`); строка `DiagB32:
mode=1` ровно одна при `=1`, при `=0` строк `DiagB32` 0; строки `DiagB32: config invalid` нет; подпись трансляции строки `ShaderSeed` =
`9177b426…` и каталог `variant_fixb26_fixb1b_fixf10_fixf19`; строки `TestB32:` — `armed`, `fire mode=<режим>`, `done mode=<режим>` у
`pp` / `pc`, ни одной у прочих; `rep_drop` = 0; `load.json` со `status=done` и режимом тега у `pd` / `pd2`, нет у прочих. Член не прошёл ⇒
помеха: тег в счёт не идёт, повтор именем `<тег>_r<k>`; повторов ≤ 6 на всё F20 (п. 550(е)(4); до F20l повторов по допуску ридера — 0).
Процесс пользователя, отказ `procload`, замок, `enter_scene` не стартовал — каталог `<тег>.user_*` / `.busy_*` / `.lock_*` /
`.nostart_*`, повтор тем же именем, попыткой не считается (как F20e).

## 4. Таблица звена (п. 550(з)(5))

По каждому тегу: допуск, бинарь и подпись (из json и строки `ShaderSeed`), `K_I` / `K`, классы кадров в счёте, `INSTR_MADE`, `kq_n` = 0,
`m5r_us` > 0, кадры с предыдущим ≥ 100 мс, ПК-A (кадры Б5, вооружённые), У5(1) и У5(4), отношение нагрузки затянувшихся кадров окна,
`Recovering Vulkan swapchain` — `b32_read.py --table` (`table.txt`).

## 5. База У5 (п. 550(ж), (з)(2); до печати) [c]

`b32_base.py` по 41 удержанию: F20a 8 (логи `REGRESS` ридера F20c) + F20c 22 (без `f20_v08`, `f20_v10`, п. 543(в)) + F20e 11; вывод
`base/base_f20l.txt`, `base/base_f20l.json` (sha256 — §8).

- **У5(2)** — кадров ≥ 70 мс (начало ≥ 10 с, не Б5) на удержание: **0,561** (23 кадра / 41); вариант без Б5, Б33, Б1б — 0,3902.
- **У5(1)** — медиана `dt_us` кадров idx 723–828: **36 171,5 мкс** (медиана 11 медиан тегов F20e: 36 818,5; 46 632; 34 904,5; 35 800;
  36 171,5; 36 082; 36 443; 35 844; 35 115; 41 596; 45 939,5; среднее 38 304,2; по всем кадрам 36 302).
- **У5(3)** — среднее `dt_us` кадров Б5 удержаний F20e: **134 767,7 мкс** (7 кадров).
- **Наблюдение [c чисел; I толкование]:** медианы окна 723–828 по тегам F20e разнятся от 34 904,5 до 46 632 (+29 % к меньшей) — член
  «> 2 %» У5(1) на одном теге может сработать от разброса между удержаниями без возмущения. Числа F20g §2.7 («33,3–35,2 мс») взяты не из
  этого окна [I]. Правило не меняется; вопрос лиду в отчёте.

## 6. Варианты и прочтения исполнителя (до ответа лида — по букве / этому прочтению, вариант рядом)

1. **«400 мс на 60 с сцены»** — один выброс 400 мс через 60 с после первой строки `Level has started: underwater_aerial_garden` (грамматика
   стенда `60:present:200`); окно кадров — [`n_start`, `n_end` + 3] по живому логу. Прочтение «400 мс каждые 60 с» не исполняется.
2. **Длина цепочки** — держатель + 3 шага (4 потока).
3. **«`Sw` / `S` ≥ 50 %»** — каждое по отдельности; если ни одно, а `Sw` + `S` ≥ 50 % — класс `UNDETERMINED`, вариант `UNMARKED:<имя>`
   печатается в пометке.
4. **RC7 «≥ 50 % тех же выборок»** — счёт `H:qlock` другого потока ≥ 0,5 × `samples` окна (пересечение выборок по строкам не восстановить).
5. **Шаг по `W`** — запись того же рода; открытое на флипе ожидание без будящего (не мьютекс) — `GUEST_SLEEP:<kind>` по букве «без будящего».
6. **`GUEST_POLL`** — конечный класс (состояние GuestGpu — в пометке).
7. **Доли `INSTR_MADE`, `kq_n` = 0, `m5r_us` > 0** — знаменатель `P_I`; по всем кадрам ≥ 100 мс со строкой `DiagB32:` — рядом.
8. **ПК-A** — кадры Б5 только среди кадров удержания (≥ 100 мс, ≥ 10 с).
9. **У5(2)** при `=1` — кадры 70–100 мс строк `DiagB32` не имеют и `INSTR_MADE` не бывают.

## 7. Проверки до печати

`test_b32_read.py` — каждый класс и край (i)–(iv), RC6, RC7, RC13 с отрицательным контролем, `INSTR_MADE`, `K_I` / `K`, члены п. 552(г),
553(в), 554(г), окно k / k+1 по `_w`, ключ `n=` (п. 551(б)(5)), стенд, окно нагрузки, У5, допуск, вывод в строгий cp1250; `sens_b32.py` —
правки ридера, каждая ловится набором; `test_guard_f20l.py` — сторож, блоки, порядок шагов `go_f20l.sh` (установка и возврат бинаря, M6,
нагрузчик); `test_tools_f20l.py` — маски `<app>` (`enter_scene.py`, `procload`, M6), нагрузчик на поддельном логе (взвод, `n_start` /
`n_end`, число процессов, класс `ABOVE_NORMAL`, стоп, нет взвода), отказы имён, ручки каждого тега, очередь, ASCII; регрессия ридера на
логах F20e `f20_v35`, `f20_v32` (RC13 равно, кадры `NO_SAMPLES`, подпись `9177b426`). Счёт проверок и sha256 выводов — строки `seal:` ниже
и `docs/track-f/f20l.md`.

## 8. Строки печати (sha256 файлов и последних выводов наборов)

- `test_b32_read.out.txt`: checks 138; ALL OK; первая строка набора: `suite test_b32_read.py sha256 f8a65b7aab4eb61ff128679c170146a37f36b8c379260773dd4c220c5f3a1aa6 target b32_read.py sha256 4f4f69cbef7b8811f541fc97b7b204cfa36df9e`
- `sens_b32.out.txt`: edits 81 missed 0; ALL OK; первая строка набора: `suite sens_b32.py sha256 1bca6bb5612363f7c5af587d0467b2bb34cbfb9e25c8c10b8047abc35efbd1ce target b32_read.py sha256 4f4f69cbef7b8811f541fc97b7b204cfa36df9e7dae6`
- `test_guard_f20l.out.txt`: checks 60, failed 0; ALL OK; первая строка набора: `suite test_guard_f20l.py sha256 8b02692dbb3f3b37187e870d0846422d999b82653a9e4faabbe1c962323f2cbb target guard_f20l.py sha256 90aac07171b00fb603e0e1f99da0b0da5ea`
- `test_tools_f20l.out.txt`: checks 62, failed 0; ALL OK; первая строка набора: `suite test_tools_f20l.py sha256 756d67b8d294c2e388212a666b05f703405adf75579b4ae3324e90e660442812 target enter_scene.py sha256 38350d22947c9d8b6d41b521c9113c935b`
- `regress/regress_b32.out.txt`: REGRESS PASS; ALL OK; первая строка набора: `suite regress_b32.py target b32_read.py sha256 4f4f69cbef7b8811f541fc97b7b204cfa36df9e7dae6ec17c94ae05a688c6c75`
- `refs_f20l.out.txt`: refs 11; ALL OK; первая строка набора: `suite refs_f20l.py refs 11`

seal: 4f4f69cbef7b8811f541fc97b7b204cfa36df9e7dae6ec17c94ae05a688c6c75 C:/kyty/f287/f20l/b32_read.py
seal: 5a986c03d161b9a5c52d589ad1da87e4676ceb9bac61acaeaa8f2131525400fa C:/kyty/f287/f20l/f20e_read.py
seal: f8a65b7aab4eb61ff128679c170146a37f36b8c379260773dd4c220c5f3a1aa6 C:/kyty/f287/f20l/test_b32_read.py
seal: 1bca6bb5612363f7c5af587d0467b2bb34cbfb9e25c8c10b8047abc35efbd1ce C:/kyty/f287/f20l/sens_b32.py
seal: ab8087676de58873024f736308983e06b78ba90f72f3b38f2bf81160cacf1c2d C:/kyty/f287/f20l/b32_base.py
seal: 6d6381865b43e6777f604f575d613c62292cb5c2842296217f47a40897279aeb C:/kyty/f287/f20l/base/base_f20l.txt
seal: d974996d61319d2f85701c77d3ee0d3a98894c637ce2400830c6e0db87641a9f C:/kyty/f287/f20l/base/base_f20l.json
seal: b06e12e790e9da9798b3aa6008e10ddcffcdd7c78d6ba21527f20fed82ff4514 C:/kyty/f287/f20l/b32_load.py
seal: a2b9587c996fc632d66288ad92f3637aaabb69f1a10bec11dd67df003410a5c9 C:/kyty/f287/f20l/m6_f20l.py
seal: 4cb513bcae46526af5622b43fe951eab78b3ab5e7e840d8346aa7c73ff27ca17 C:/kyty/f287/f20l/go_f20l.sh
seal: f82d9c364d1e58412fd290c8ea7026c72ab291e05c37e13549f752b3e2131e87 C:/kyty/f287/f20l/launch_f20l.sh
seal: 6c45e7f8bf5b005d758b357cefdc8ad9f917180f7d93f3b103f4d025a27cdef0 C:/kyty/f287/f20l/wait_f20l.sh
seal: 547f856c77b00c0d7118bf4eaf2ae857608f4c50dba2c4e7d8edf79c4b7e2ea9 C:/kyty/f287/f20l/post_f20l.sh
seal: 90aac07171b00fb603e0e1f99da0b0da5ea69246b9811172804f6f3590502637 C:/kyty/f287/f20l/guard_f20l.py
seal: fe11b720385b8b12eed24a0fc022fa0b7ccd0eecb034a92c3c8ea00c6d3b4165 C:/kyty/f287/f20l/queue_f20l.py
seal: 38350d22947c9d8b6d41b521c9113c935b1af8d313bff232625579906b83deba C:/kyty/f287/f20l/enter_scene.py
seal: d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0 C:/kyty/f287/f20l/procload.py
seal: a7096fd47f70419a5ed8d541778294f3032ca2c88e7b4b2e946f3d99651182bb C:/kyty/f287/f20l/manifest_fs4c.py
seal: c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d C:/kyty/f287/f20l/sheet142.py
seal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 C:/kyty/f287/f20l/gates_default.txt
seal: f16411dbe6e89b9d47dfa5775f4451450f5aeac1aa081a03dcd12b101a74d227 C:/kyty/f287/f20l/watch_f20l.py
seal: c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96 C:/kyty/f287/f20l/idle142.py
seal: 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 C:/kyty/f287/f20l/run_safety99.py
seal: c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21 C:/kyty/f287/f20l/launch_run.py
seal: 8b02692dbb3f3b37187e870d0846422d999b82653a9e4faabbe1c962323f2cbb C:/kyty/f287/f20l/test_guard_f20l.py
seal: 756d67b8d294c2e388212a666b05f703405adf75579b4ae3324e90e660442812 C:/kyty/f287/f20l/test_tools_f20l.py
seal: d524b7bf2da6a794f3db1c476e3c99a99729ab3db970bee1c6746389c5744988 C:/kyty/f287/f20l/port_f20l.py
seal: 849abd647c00b6ca23264f5dc8279e77d9454922d679408e68ccd4db17809d57 C:/kyty/f287/f20l/refs_f20l.py
seal: 6d32d89567dbd57bfab2a75948125c6179ddf2895850c4217c9f81a890969944 C:/kyty/f287/f20l/regress/regress_b32.py
seal: 24f063c6654abb5b4989c7ed1d0131d55bd713c7fc4b6a4470f70162ba5453a2 C:/kyty/f287/f20l/test_b32_read.out.txt
seal: dd50928ffa629560476959df78318ae0c064f4caf85f5abe428481fea1704b38 C:/kyty/f287/f20l/sens_b32.out.txt
seal: 9d6260d0e42f1406251f3754accaa65dac22335858c7a8432b49edb148b2fc8a C:/kyty/f287/f20l/test_guard_f20l.out.txt
seal: a5a5ab97b9b7c6a2607e7e0d312e4f95afb7fc77667d4bd2bf10dfc1a6bb284f C:/kyty/f287/f20l/test_tools_f20l.out.txt
seal: 436320f43d887d3024d296d5c5275aa355ca06ef5124ea73806a01910d9d3454 C:/kyty/f287/f20l/regress/regress_b32.out.txt
seal: 48062cc4c97091a3e93e15ebc17cb973e1419b3dcd24f6d641a6136aa917ca31 C:/kyty/f287/f20l/refs_f20l.out.txt
seal: b9e0ee0092ca1504979ebd674abb21c8d67015fd030bc33615eb2c87acb90f91 C:/kyty/f287/bin/kyty_emulator_b9e0ee00.exe
seal: 2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe
seal: 6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c C:/kyty/scripts/s51_vidglitch.py
