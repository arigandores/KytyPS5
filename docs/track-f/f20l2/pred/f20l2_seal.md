# F20l2 (`HPP-648`, Harness Engineer): повтор контролей `KYTY_DIAG_B32` на бинаре F20j4 — печать 2 до первого тега

Трек F, итерация F20 (Б32 Sky Garden), звено F20l2 по п. 574(е) с поправкой п. 581(ж) и строкой задания п. 584(г). Этот файл — печать 2:
после её записи ридер, цепочка тега и правила чтения не меняются; её sha256 пишется в json каждого тега (`prereg`), ридер сверяет её в
допуске. **Вердикта нет:** чтение повтора и исход У1 — F20m2 (лид). Метки: [c] — код/лог прочитан или пересчитан, [I] — вывод, [U] —
неизвестно.

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1; проверка — `refs_f20l2.py`)

- Решение звена — п. 574: `e8511f53:docs/ROADMAP.md:23423` (якорь «574. **Звено F20m трека F (`HPP-632`, лид): чтение контролей F20l»;
  +1 — «(а) **Данные лида [c]**»); поправка правила чтения — п. 574(д) `e8511f53:docs/ROADMAP.md:23428` (+1 — «(е) **Повтор контролей —
  F20l2»); задание — п. 574(е) `e8511f53:docs/ROADMAP.md:23429` (+1 — «(ж) **Звенья»); `θ_load` — п. 574(б)(4), (6).
- Поправки: п. 581 `e8511f53:docs/ROADMAP.md:23465` (якорь «581. **Звено F20k3 трека F»; +1 — «(а) **Приёмка строкой (правило 24):**»),
  роды и классы — п. 581(в)(5) `e8511f53:docs/ROADMAP.md:23468` (+1 — «(г) **Счёт У1.**»), поправка задания — п. 581(ж)
  `e8511f53:docs/ROADMAP.md:23472` (+1 — «(з) **Звенья»); строка задания — п. 584 `e8511f53:docs/ROADMAP.md:23483` (якорь «584. **Звено
  F20k4 трека F»; +1 — «(а) **Приёмка строкой»), оговорки — п. 584(в) `e8511f53:docs/ROADMAP.md:23486` (+1 — «(г) **Дальше:**»);
  комментарий лида `355060ea` в `HPP-648`.
- Формат строк — код `4371ff4b` (= `f2307b02`, patch-id `491cf87a4853`, п. 583(б)): имена родов `WaitName`, строка `-w` с `peer=` и
  `peer_tid=`, строка `-x` с `ring_hold=` и `ring_hold_w=` (ссылки — `refs_f20l2.py`).
- Бинарь тега — тестовый F20j4: sha256 `2d0c8815389bdc42a2371ba813dc9460fc5565f21f89e32fad4d9e5bd2394dc7`, копия
  `C:/kyty/f287/bin/kyty_emulator_2d0c8815.exe`, подпись трансляции `9177b4267de1fb8bac7d1113afd8733210addfac` = FS8; F20k4 — `PASS`, RC кода
  0 (п. 584). Установленный — FS8 `2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b`, закреплённая копия
  `C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe`.

## 1. Теги и форма (п. 574(е), формы п. 550(д)(1)–(3))

| тег | ручки (позиционно в `enter_scene.py`) | форма F20l |
|---|---|---|
| `b32_z0b` | `KYTY_DIAG_B32=0` | `b32_z0` |
| `b32_ppb` | `KYTY_DIAG_B32=1 KYTY_TEST_B32=60:present:200` | `b32_pp` |
| `b32_pcb` | `KYTY_DIAG_B32=1 KYTY_TEST_B32=60:gpusleep:200` | `b32_pc` |

- По одной попытке; ПК-D и ПК-D2 не повторяются (п. 574(е)) — теги `b32_pd`, `b32_pd2` цепочка F20l2 не принимает; ветка нагрузчика
  `go_f20l2.sh` ни одним тегом не достигается.
- Общая форма — та же, что у F20l: `enter_scene.py <тег> --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480
  --no-install --require-idle --gates-file gates_default.txt --pred pred/f20l2_seal.md --rec --hold 330 KYTY_GPU_CLOCK_PIN=1
  KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 <ручки>`; без валидации, RenderDoc, `KYTY_GPU_CHECKPOINTS`, `KYTY_GAME_PATCH`; цепочка снимает все
  `KYTY_*` и `VK_LAYER_*` шелла до вызова.
- **Бинарь:** до замка установленный = FS8, иначе отказ; внутри замка после копии кэшей ставится копия F20j4 (проверка sha256 =
  `2d0c8815…`, `installed_sha.txt`); после тега — FS8 из закреплённой копии (проверка sha256, `installed_after.txt`); иначе `RETURN_FAILED`,
  замок остаётся. `C:/kyty/build/install` не трогается.
- **Кэши:** `_ShaderCache` (с `pipelines.bin`), `_PipelineCache`, `_SaveData`, GLCache драйвера — копия до, возврат после, манифест sha256
  до / прогона / после со строкой равенства. Строки `lock taken|released <тег> <UTC>` — `C:/kyty/f287/f20l2/runs/lock.log`; события —
  `C:/kyty/f287/times.txt`.
- **M6** (`m6_f20l2.py`, справка): как F20l; имена — только в `runs/<тег>/m6_local.txt` (в git не кладётся), в `m6.txt` — `<app>`.
- **Сторож игры пользователя и очередь** — как F20l (`guard_f20l2.py`, блок тегов открывается двумя чистыми проверками с промежутком
  ≥ 600 с, в блоке ≤ 6 тегов); перед каждым тегом — `queue_f20l2.py` (звенья Harness Engineer кроме `HPP-648`; «готов вход» = `todo` /
  `in_progress` или идущий прогон) — `QUEUE BUSY` ⇒ тег не берётся (F20 последним в очереди замка, п. 462(г), 567).
- **Проверка живости прогона (долг п. 587(г), выбор исполнителя):** после `procload.py` и до взятия замка `go_f20l2.sh` зовёт
  `runchk_f20l2.py` — у `HPP-648` идёт прогон (`executionRunId`), равный `F20L2_RUN_ID`, который `launch_f20l2.sh` передал из
  `PAPERCLIP_RUN_ID`, и статус `in_progress`; иначе (`RUN GONE`, `API ERROR`) — тег не стартует, каталог `<тег>.gone_*`, попыткой не
  считается (отменённый прогон агента не останавливает отсоединённый вызов тега — п. 587(г)).
- Порядок: `b32_z0b`, `b32_ppb`, `b32_pcb`. Вызов — `launch_f20l2.sh <тег>` (только запуск), ожидание — `wait_f20l2.sh <тег>` ≤ 540 с
  командой, разбор — `post_f20l2.sh <тег>` вне замка (`s51_vidglitch.py <rec> 4 6`, лист `sheet142.py`, ридер, таблица).

## 2. Ридер `b32_read.py` (п. 550(г) с поправками п. 551(в), 552(в)(3), (г), 553(в), 554(г), **574(д)**, **581(в)(2), (в)(5)**)

Всё правило F20l (печать 1 `C:/kyty/f287/f20l/pred/f20l_seal.md`, §2) без изменений, кроме членов ниже.

1. **`θ_load`** (п. 574(б)(4), (6)) — постоянная правила (г)(2)(iii); ридер читает её из строки печати ниже (одна строка формы
   `theta_load: <x>` с первого столбца; нет строки или их две — член допуска «`θ_load` из печати» не проходит, лог не читается):

theta_load: 0.4562

2. **Роды** — перечень `enum Wait` кода `4371ff4b` по порядку (`WaitName`, 45 родов; фикстура сверяет имена с кодом через `git show`).
   **`EMU_WAIT`** (п. 574(д), п. 581(в)(5)) — `emu_mutex` … `av` (25 родов ожиданий эмулятора) и `vblank`, `audio`, `aio`, `net`,
   `emu_join` (30 родов; = `IsEmuWait` кода). **`GUEST_SLEEP`** — прежние `cond`, `mutex`, `sem`, `psem`, `evf`, `eq`, `sleep` (и
   `gpu_idle`, `gpu_regmem`) и `once`, `join`, `addr`, `fiber`, `ult`, `rwlock`.
3. **Шаг по `W:<род>` ≥ 50 % (п. 574(д))** — запись `-w` этого потока и рода с наибольшим `overlap_us`:
   (а) `W:sleep` ⇒ `GUEST_SLEEP:sleep` (с RC6), как было;
   (б) `to=1` с истёкшим сроком гостя ⇒ `GUEST_SLEEP:<род>` (RC5(в) п. 550(в), «действует для всех родов, где запись различает истёкший
   срок гостя» — п. 581(в)(5)): у рода `GUEST_SLEEP` — `to=1`, как было; у рода `EMU_WAIT` — `to=1` и `req_us` > 0 (срок заказал гость);
   `to=1` при `req_us` = 0 у рода `EMU_WAIT` — срок не гостя, чтение идёт дальше по (в)–(д), прочтение «`to=1` у любого рода ⇒
   `GUEST_SLEEP`» печатается в пометке (вариант исполнителя);
   (в) `waker` ≥ 0 ⇒ шаг к будящему;
   (г) иначе `peer` записи ≥ 0 ⇒ шаг к `peer` (поле `peer=` строки `-w`, п. 581(в)(2); слот 0 — слот, не «нет»);
   (д) иначе, как было, для рода `mutex` — шаг к `peer` строки `-t`;
   (е) иначе — род `EMU_WAIT` ⇒ класс **`EMU_WAIT:<род>`** (без RC6: ждёт эмулятор, не игра); род `GUEST_SLEEP` ⇒ `GUEST_SLEEP:<род>`
   с RC6. Шаг к `peer` строки `-t` для любого рода печатается в пометке (вариант исполнителя), класс не меняет.
   В пути цепочки у потока, от которого сделан шаг, — `->waker`, `->peer` или `->tpeer`. Цикл (в т. ч. `peer` = свой слот), 4-й шаг,
   поток без строки `-t` ⇒ `UNDETERMINED`, как было. Семейство `EMU_WAIT` в правиле серии стоит рядом с `EMU_CALL` (п. 574(д)) — это
   чтение F20m2, ридер печатает класс.
4. **Член ПК-C (п. 574(в)(2))** — у кадра стенда (самый длинный из трёх кадров после строки `TestB32: fire`) печатаются: класс, путь,
   шаги цепочки (слот, имя, роль, `R`, `Sw`, `S`, выборок, как достигнут), «GuestGpu в цепочке» (`gpu_slot` строки `DiagB32:` среди шагов),
   «шаг на GuestGpu с `Sw` ≥ 50 % или `S` ≥ 50 %» (каждое отдельно — по букве п. 550(д)(3); вариант `Sw` + `S` ≥ 50 % — рядом), записи `-w`
   кадра с `peer`, `ring_hold_w`.
5. **`ring_hold_w` (З1, п. 554(в)(1), 574(г)(5))** — справка, не член класса и не нулевой инвариант `NO_SAMPLES`: по кадру, сумма по всем
   строкам `-x` тега, число кадров ≥ 100 мс с `ring_hold_w` > 0, число строк `-x` с полем.
6. **Справка ПК-D (п. 574(е)):** ридер перечитывает лог F20l `b32_pd` (`C:/kyty/f287/f20l/log_b32_pd.txt`, json, печать 1 F20l, бинарь
   F20j2 `b9e0ee00…` в допуске) с `θ_load` из этой печати; вывод — `runs/b32_pd_ref/read.txt`, `read.json`. Число — справка для F20m2.

## 3. Допуск тега и помеха (п. 574(е): помехи — по п. 273(з))

Члены F20l (печать 1 §3) с заменами: `binary_sha256` = F20j4 `2d0c8815…` (у справки `b32_pd` — F20j2 `b9e0ee00…`); `prereg` = sha256 этой
печати (у справки — печати 1); новый член — «`θ_load` из печати» (ровно одна строка). Член не прошёл ⇒ помеха: тег в счёт не идёт, повтор
именем `<тег>_r<k>`; событие окна (`Window <id> minimized`, `Recovering Vulkan swapchain`) — строка допуска «событие окна», вопрос лиду о
повторе (п. 273(з)). Процесс пользователя, отказ `procload`, замок, `enter_scene` не стартовал — каталог `<тег>.user_*` / `.busy_*` /
`.lock_*` / `.nostart_*`, повтор тем же именем, попыткой не считается. Бюджет замка — п. 574(е): контрольных тегов 5 + 3. Выбор, записанный в этой печати, исполнитель не меняет без пункта лида; при
сомнении — вопрос лиду до действия (п. 587(в)).

## 4. Оговорки чтения п. 584(в) (для F20m2; ридер их не меняет)

- **Н1** — `W:main_task` под `H:present` на Windows возникает только через `Presenter::Present` → `UpdateTitle` → `RunOnMainThread` при
  `KYTY_TITLE_ASYNC=0`; на умолчаниях не возникает; строка `-w … kind=main_task` в окне `H:present` при умолчаниях — сигнал проверить
  гейт лога.
- **Н2** — под `H:*` подавляется метка любого рода `TrackedMutex` (в т. ч. `W:ult`); правило п. 574(д) не меняется.
- **Н3** — поведение `=0` у `Reserve` проверяет тег `b32_z0b` (машинный код `=0` не сравнивался — не заявляется).
- **Н4** — источник чисел тестов — лог (`H=47` в `diag_b32_tests.log`).
- **Н5** — 0 строк `kind=emu_join` в логах ожидаемо (вызовов `Common::Thread::Join` нет); фикстура ридера на род остаётся.

## 5. Таблица звена

По каждому тегу: допуск, бинарь (json) и подпись (строка `ShaderSeed`), sha256 лога и `read.txt` (оба sha), `K_I` / `K`, классы кадров в
счёте, кадр стенда с классом и членом GuestGpu, `INSTR_MADE`, `kq_n` = 0, `m5r_us` > 0, кадры с предыдущим ≥ 100 мс, ПК-A, У5(1) и
У5(4), `ring_hold_w`, `Recovering Vulkan swapchain` — `b32_read.py --table` (`table.txt`) и отчёт `docs/track-f/f20l2.md`.

## 6. Проверки до печати

`test_b32_read.py` — набор F20l и новые фикстуры: шаг (в)–(д) п. 574(д) (будящий, `peer` записи, `peer` = 0, будящий раньше `peer`, `peer`
для рода `GUEST`, `-t peer` у `mutex` как было и только вариантом у прочих), каждый из 30 родов `EMU_WAIT` и 12 родов `GUEST_SLEEP` без
будящего и `peer` (и с `peer` — шаг), `emu_join`, `vblank` с `peer` = Present, RC5(в) у рода `EMU_WAIT` с `req_us` 0 и > 0, свой слот —
цикл, RC6 для `join`, имена родов против `WaitName` кода `4371ff4b`, `IsEmuWait`, `ring_hold_w`, `θ_load` из печати (края строки),
член ПК-C, допуск (бинарь F20j4 / справки F20j2, печать без `θ_load`), пути справки `b32_pd`; `sens_b32.py` — правки ридера F20l и новые,
каждая ловится; `test_guard_f20l2.py`, `test_tools_f20l2.py` — порт F20l (теги `b32_z0b`, `b32_ppb`, `b32_pcb`; `b32_pd`, `b32_pd2`, старые
имена — отказ); регрессия ридера на логах F20e. Первый прогон `sens_b32.py` (19:47Z) пропустил 4 правки из 111 (`theta not an admission member`,
`gpu member S off`, `ring_hold_w sum off`, `admission loader mode not checked`) — ридер не менялся, в `test_b32_read.py` добавлены
фикстуры: строка допуска «`θ_load` из печати» сама — FAIL без строки; шаг на GuestGpu с `S` = 40 из 40 (не `Sw`) — член «да»;
накопленный `ring_hold` строки `-x` отличен от `ring_hold_w` и в сумму не идёт; справка `b32_pd` с нагрузчиком `half` — FAIL; второй
прогон — 0 пропусков. `test_tools_f20l2.py` — и фикстуры `runchk_f20l2.py` (живой прогон, нет прогона, чужой прогон, статус не
`in_progress`, пустой `F20L2_RUN_ID`, нечитаемый ответ). Счёт проверок и sha256 выводов — строки `seal:` ниже.

## 7. Не заявляется

Что инструмент работает в игре; что повтор ПК-C пройдёт; что `DrawThread` ждал в `GuestGpu::WaitForIdle`; что `=0` равен FS8 в машинном
коде; что опись полна вне правил скриптов; что разбиение п. 581(в)(5) верно для каждого места рода; что инструмент не меняет частоту Б32;
что Б32 вызван ожиданием потока гостя, нагрузкой хоста, выводом кадра или `VirtualProtect`; что Б32 вызван или не вызван путём Б24 / Ф8; что
реестр полон; ни одно число — не выигрыш; 60 FPS не обещаются.

## 8. Строки печати (sha256 файлов и последних выводов наборов)

- `test_b32_read.out.txt`: checks 236; ALL OK; первая строка набора: `suite test_b32_read.py sha256 31f547262f8aaa1bccf0164a34a7edc927feb544970e8a13225169c47c90f770 target b32_read.py sha256 57b546c748a8f5f4dd84524d19d369ea411f211`
- `sens_b32.out.txt`: edits 111 missed 0; ALL OK; первая строка набора: `suite sens_b32.py sha256 6300b9f00e3fcb0db7d23b1e8ae69a5fcd56a3460543c53de261ef0676fe0a81 target b32_read.py sha256 57b546c748a8f5f4dd84524d19d369ea411f2115c101`
- `test_guard_f20l2.out.txt`: checks 60, failed 0; ALL OK; первая строка набора: `suite test_guard_f20l2.py sha256 8cc22c5e2c6b54d4e95ebc6ba5f002f5ad5e6b6bfbae533581e9f5ed0b870d72 target guard_f20l2.py sha256 77090146fa9d61cd5c136ad7934068fec`
- `test_tools_f20l2.out.txt`: checks 80, failed 0; ALL OK; первая строка набора: `suite test_tools_f20l2.py sha256 9d22a4d5a1acc3ac7a012d9060d69b645076acbeb79a0fc621694418510a6348 target enter_scene.py sha256 ef2f9c3b836c004797c1711f6bc596680`
- `regress/regress_b32.out.txt`: REGRESS PASS; ALL OK; первая строка набора: `suite regress_b32.py target b32_read.py sha256 57b546c748a8f5f4dd84524d19d369ea411f2115c1011abe21dea68dd5fbf51e`
- `refs_f20l2.out.txt`: refs 12; ALL OK; первая строка набора: `suite refs_f20l2.py refs 12`

seal: 57b546c748a8f5f4dd84524d19d369ea411f2115c1011abe21dea68dd5fbf51e C:/kyty/f287/f20l2/b32_read.py
seal: 5a986c03d161b9a5c52d589ad1da87e4676ceb9bac61acaeaa8f2131525400fa C:/kyty/f287/f20l2/f20e_read.py
seal: 31f547262f8aaa1bccf0164a34a7edc927feb544970e8a13225169c47c90f770 C:/kyty/f287/f20l2/test_b32_read.py
seal: 6300b9f00e3fcb0db7d23b1e8ae69a5fcd56a3460543c53de261ef0676fe0a81 C:/kyty/f287/f20l2/sens_b32.py
seal: ab8087676de58873024f736308983e06b78ba90f72f3b38f2bf81160cacf1c2d C:/kyty/f287/f20l/b32_base.py
seal: 6d6381865b43e6777f604f575d613c62292cb5c2842296217f47a40897279aeb C:/kyty/f287/f20l/base/base_f20l.txt
seal: d974996d61319d2f85701c77d3ee0d3a98894c637ce2400830c6e0db87641a9f C:/kyty/f287/f20l/base/base_f20l.json
seal: c47c396a5952ba97d0430e551c8dce92aabff95327ecdcaca86b23227948928e C:/kyty/f287/f20l/pred/f20l_seal.md
seal: b9e0ee0092ca1504979ebd674abb21c8d67015fd030bc33615eb2c87acb90f91 C:/kyty/f287/bin/kyty_emulator_b9e0ee00.exe
seal: 743eb6914de60b5d5bfd70ebafd3499ece28dd68d997bdcb32aa1a626221d16a C:/kyty/f287/f20l/log_b32_pd.txt
seal: 639b2155cb8358f854452cd1d1bd3d23682da88e0872b84483c1ecf7ec795d52 C:/kyty/f287/f20l/b32_pd.json
seal: 74174ba37f367a1f17049239d26095d89eb14647d9789c4cc07a6c98a962aee8 C:/kyty/f287/f20l2/edit_f20l2.py
seal: a29867cd5c41074687b93aac04735ac0b7dbf878cfcf907b528e9c9a754a3b50 C:/kyty/f287/f20l2/f20l2_seal_body.md
seal: b06e12e790e9da9798b3aa6008e10ddcffcdd7c78d6ba21527f20fed82ff4514 C:/kyty/f287/f20l2/b32_load.py
seal: 9baeaeb77b37054738238e244c1d6dc064f5e0c2966499630853b12d33fc375a C:/kyty/f287/f20l2/m6_f20l2.py
seal: 98efe2ebf928422ae82fb57c866267c72d5fa692bb3128e4633d99d6b03b7356 C:/kyty/f287/f20l2/go_f20l2.sh
seal: 824b1af3f9c78be0231ea6017a46e6be6acb1aa4db368c76039756099c124dc8 C:/kyty/f287/f20l2/launch_f20l2.sh
seal: 3605dc48fcabb21d3eff374799f2db3169ee194ab5219fd99e742fbc3c82d534 C:/kyty/f287/f20l2/wait_f20l2.sh
seal: 8c151a10d3d2b6ddf7cbddcd0c162bb58aa87b68aa360a966c5488a2650f12b1 C:/kyty/f287/f20l2/post_f20l2.sh
seal: 77090146fa9d61cd5c136ad7934068fecc9e1514ec1a91ac5f02255cd0cbd0e1 C:/kyty/f287/f20l2/guard_f20l2.py
seal: 044d0ff0bc5ad2eb0f8578abafa7053580d2e01d1d3cfa1709e6f680efb9e090 C:/kyty/f287/f20l2/queue_f20l2.py
seal: ef2f9c3b836c004797c1711f6bc59668087d1a6920d7125cef85c0cfbfb83607 C:/kyty/f287/f20l2/enter_scene.py
seal: ff5b295de2da59ce08b98404f6383d404362aa024ca409e7c194ba34c18dd276 C:/kyty/f287/f20l2/runchk_f20l2.py
seal: d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0 C:/kyty/f287/f20l2/procload.py
seal: a7096fd47f70419a5ed8d541778294f3032ca2c88e7b4b2e946f3d99651182bb C:/kyty/f287/f20l2/manifest_fs4c.py
seal: c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d C:/kyty/f287/f20l2/sheet142.py
seal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 C:/kyty/f287/f20l2/gates_default.txt
seal: f16411dbe6e89b9d47dfa5775f4451450f5aeac1aa081a03dcd12b101a74d227 C:/kyty/f287/f20l2/watch_f20l2.py
seal: c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96 C:/kyty/f287/f20l2/idle142.py
seal: 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 C:/kyty/f287/f20l2/run_safety99.py
seal: c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21 C:/kyty/f287/f20l2/launch_run.py
seal: 8cc22c5e2c6b54d4e95ebc6ba5f002f5ad5e6b6bfbae533581e9f5ed0b870d72 C:/kyty/f287/f20l2/test_guard_f20l2.py
seal: 9d22a4d5a1acc3ac7a012d9060d69b645076acbeb79a0fc621694418510a6348 C:/kyty/f287/f20l2/test_tools_f20l2.py
seal: ab207e63a769d35f1ceac6755b15f91a7786f6a6901a8ba627c68d0837ecdbe2 C:/kyty/f287/f20l2/port_f20l2.py
seal: e241bc90fd3c64bf676d20adf222d3e397e134c413067547a1da0a6972ab5990 C:/kyty/f287/f20l2/refs_f20l2.py
seal: 3ac53111a6d81f9e4cff90df23fb7c64740d7fa5e54b9f350ec655f6a296799b C:/kyty/f287/f20l2/regress/regress_b32.py
seal: c303599b8f8194918a276175ed30235b649fe8bf3a5172112a7c8654313a87d1 C:/kyty/f287/f20l2/test_b32_read.out.txt
seal: 82748af7098bd9bafb7922eae660428eb9fbb07f57f1ea0f9eb06852e75cb697 C:/kyty/f287/f20l2/sens_b32.out.txt
seal: 4df93de0f696a5d6cc0cdab950b02da3ba1bd5279d9b959e3867da96932d0dde C:/kyty/f287/f20l2/test_guard_f20l2.out.txt
seal: bfc6b1d17c306ce26f5b6a80ee54dbbf616dd99064821953e4f3fd02cb7bb7c0 C:/kyty/f287/f20l2/test_tools_f20l2.out.txt
seal: 28b5bb184f172e4eafacc653c1f44a74428a76a2104e573481755fa8cf69c55d C:/kyty/f287/f20l2/regress/regress_b32.out.txt
seal: cba3e4c24d05ccc2af5dd5408633f921adb81fb6512c60acc320a8716f30a9f2 C:/kyty/f287/f20l2/refs_f20l2.out.txt
seal: 2d0c8815389bdc42a2371ba813dc9460fc5565f21f89e32fad4d9e5bd2394dc7 C:/kyty/f287/bin/kyty_emulator_2d0c8815.exe
seal: 2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe
seal: 6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c C:/kyty/scripts/s51_vidglitch.py
