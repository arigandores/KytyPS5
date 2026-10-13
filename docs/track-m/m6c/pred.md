# M6c (трек M, `HPP-850`): печать тегов `m6_sg`, `m6_hb`, `m6_mg` — до первого тега

Звено Harness Engineer. Основание — `ROADMAP.md` п. 767(и)–(к), 769(в), 770(б)–(д), 772(б), 776 (KytyPS5 `4fae2ecf`). Печать
закрывается до первого тега; после неё не меняются ни харнесс, ни ридер. Вердикта по темам здесь нет: чтение по правилу п. 767(к) с
поправками п. 769(в), 770, 772(б), 776(в) — звено M6d (лид). Пометки: [c] — проверено кодом или данными, [I] — вывод, [U] — неизвестно.

## 1. Бинари и установленное состояние

| Что | Значение |
|---|---|
| Бинарь тегов (M6a3, принят M6b3, п. 776) | `C:/kyty/m657/bin/kyty_emulator_2179005b.exe`, sha256 `2179005bc42e42133e92d4a4c9cc0a2f33b3670f0263a6ca67c2c3804ac7e43f`; код `534d75af` (= worktree `3d227024`); не установлен |
| Установленный бинарь | MS1 `ea35b679b0bcfe83767093204f348b189384cab1a7b273f89b164b64cba4d4df` = `ps5 em/kyty_emulator.exe` на момент печати [c]; закреплённая копия `C:/kyty/m657/bin/kyty_emulator_ea35b679.exe` |
| Подпись и каталог при умолчаниях | `8dcf31779bbcb7c6e605653a138dae162f645a46`, `variant_fixb26_fixb1b_fixf10_fixf19_mw1_33` (набор подписи M6a–M6a3 не тронут, п. 769(а), 776(б)); каталога `_mw1_33` в кэшах пользователя нет [c на момент печати] — вход каждого тега холоден по трансляции [I] |

Бинарь тегов ставится только на время тега; после каждого тега возвращается MS1 из закреплённой копии со сверкой sha256. Бинарь не
пересобирается между тегами и чтением. `build/install` (`14ea0066…`) бинарём M6c не является (п. 776(а)).

## 2. Теги (по одной попытке)

| Тег | Уровень | Форма |
|---|---|---|
| `m6_sg` | Sky Garden (`underwater_aerial_garden`) | V |
| `m6_hb` | `hoover_beach` | V |
| `m6_mg` | `mini_giants_garden` | V |

Порядок — `m6_sg`, `m6_hb`, `m6_mg`. Повтор `<тег>_r1..3` — только при помехе прогона: событие окна (`minimized`, `Recovering Vulkan
swapchain`) — помеха и повтор тега по заданию звена (п. 767(и)); перед повтором строка `times.txt` с причиной, затем `M6C_REPEAT_OK=1`.
Иная помеха (процесс пользователя, дисплей, `nostart`) — повтор тем же правилом, причина в строке. Смерть тега при `=1`, не
воспроизведённая при `=0`, — помеха инструмента (п. 770(г)); тег на `=0` в M6c не идёт без пункта лида.

## 3. Форма V и ручки

- `--stable-draws 300 --timeout 480`, удержание — опция 330 с (член «≥ 300 с после первого кадра сцены»; запас формы V M3a, буква п.
  767(и) «удержание 300 с» — член), видео (`KYTY_REC`), без валидации (`--vulkan-validation false`, `--shader-validation false`), без
  `--rd`, вход `-lvl <уровень>`; выход — `WM_CLOSE` в конце удержания.
- Переменные — позиционно в `enter_scene.py`: `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_DIAG_M5W2=1` и постоянные
  `enter_scene.py` (`KYTY_FRAME_TRACE=lite`, `KYTY_GPU_HANG_ABORT_S=8`, файлы шлюза, `KYTY_QUEUE_TRACE=1`, `KYTY_GUEST_ARGS`);
  `KYTY_*`/`VK_LAYER_*` оболочки снимаются. Без `KYTY_FIX_*`, `KYTY_S_*`, `KYTY_TEST_*`, `KYTY_M_*`, `KYTY_GAME_PATCH`,
  `KYTY_GPU_CHECKPOINTS`.

## 4. Допуск и члены (ридер `m6c_read.py`)

- **Допуск** (провал — тег не читается): json тега; `binary_sha256` = `2179005b…` (иначе `NOT_ADMITTED`, п. 776(а)); установленный во
  время тега = `2179005b…`; установленный до и после = MS1; `prereg` = sha256 этой печати; план харнесса = план ридера; env = форма
  точно; 0 `KYTY_TEST_*`; 0 `ExitFatal:`; флаги; `-lvl` и уровень харнесса; опция удержания 330; лог и stdout; вход `ok` и строка входа;
  0 `minimized` и `Recovering Vulkan swapchain`; подпись `8dcf3177…` и каталог `_mw1_33`; 0 `GamePatch:`, `DiagB32`, `TestLogStall`,
  `TestHidLoss`; **ровно одна строка `M5W2: mode=1`** (ручка прочитана); кэши возвращены (`manifest cmp EQUAL`); строка
  `LogAsync: full_waits=` один раз.
- **Члены формы V** (строки, вердикта нет): удержание ≥ 300 с после первого кадра сцены; процесс жил; 0 маркеров смерти в логе и stdout
  (в т.ч. `ErrorDeviceLost`, `device lost`); 0 кадров ≥ 1 с после первого кадра сцены; видео ≥ 3 000 записей; 0 одно-кадровых глитчей
  (`s51_vidglitch.py 4 6`); лист сделан; `Event: quit`; 0 `--- Fatal Error ---` после него; конец до таймаута харнесса; `MWave1:
  mask=0x33`, `MT265`/`MT272`/`MT231` `mode=1` (бинарь — MS1 + код измерения); ≥ 1 разобранная строка `M5W2Stat:`, 0 неразобранных.
- Первый кадр сцены, удержание, маркеры, сканы лога и stdout — код FS15c `C:/kyty/f287/fs15c/fs15c_read.py` (sha256 `9ef29757…`),
  импортируется со сверкой sha, константа уровня переназначается на уровень тега (как M3a).
- **Темп сцены** (п. 620(г)(2), `tempo_m6c.py` = `tempo_fs15c.py`): среднее `dt` < 100 000 мкс; иначе `SERIES_STOP` и вопрос лиду.

## 5. Поля `M5W2Stat:` и итог тега

- Строка (`diagM5W2.cpp` `PrintStat`, код `534d75af`): `M5W2Stat: when=<periodic|exit>` и 21 поле в порядке: `pushes ao_obj_push
  ao_obj_nz ao_obj_nopcm ao_bus_push ao_bus_nz clr_dw clr_dw_div minlod_views minlod_div inv_calls inv_part inv_gpu inv_off raw_rd
  raw_rd_gpu minlod_div_x clr_dw_div8 ao_obj_unread inv_part_src ao_obj_vq`. Строка с префиксом, не разобранная целиком, —
  «неразобранная».
- **Итог тега (член П3, п. 770(д))** — последняя разобранная строка `M5W2Stat:` с наибольшим `pushes` (при равенстве — более поздняя);
  его строки `M5W2Clr: when= fmt=<vk::Format> clr_dw= clr_dw_div= clr_dw_div8=` — идущие после него до следующей `M5W2Stat:` с тем же
  `when`. Таблица полей по тегам строится только из итогов; строка SUM — сумма итогов трёх допущенных тегов (правило п. 767(к) — по
  сумме трёх тегов).
- Поля по темам (имена — для чтения M6d, не вердикт): T125 — `ao_obj_push`, `ao_obj_nz` (расхождение), `ao_bus_nz` (контроль),
  `ao_obj_unread`, `ao_obj_vq` (справка; правило чтения T125 — п. 772(б) и 776(в)); T313 + T179 — `clr_dw`, `clr_dw_div`; (а3) —
  `clr_dw_div8` и строки `M5W2Clr` `fmt` 9 (`R8Unorm`), 16 (`R8G8Unorm`) (п. 770(в)); T021 — `minlod_views`, `minlod_div_x`
  (расхождение), `minlod_div` (справка) (п. 770(б)); T188 — `inv_calls`, `inv_part`, `inv_part_src` (справка, п. 770(д)); T258 —
  `raw_rd`, `raw_rd_gpu`.
- **Строки без ручки** (п. 767(з), справка M6d): число и первая строка (до 160 знаков) `GuestPrintf: negative precision` (T031),
  `AmprRecordSpace: refused`, `AmprWriteAddress: refused` (T309), `AgcReserveDW: cursor state` (T023).
- **Опорные строки п. 769(в)**: `clr_ok` — сумма поля ` clr_ok=` строк `FrameTrace-x` (по кадрам); `img_minlod` — сумма ` img_minlod=`
  строк `FrameTrace-draw`; число строк `T# MIN_LOD … applied`. Харнесс их только печатает; знаменатель 0 при опоре > 0 читает M6d.

## 6. Кэши

Набор: `_ShaderCache`, `_ShaderSeeds`, `_PipelineCache`, `_SaveData` папки эмулятора и `GLCache` драйвера. Каждый тег — на живых кэшах
пользователя (K0): копия до прогона и манифест sha256 (`runs/<тег>/manifest_before.tsv`), прогон, манифест состояния прогона, возврат
копии, манифест после; член допуска — `manifest cmp EQUAL`. K1/KT нет. Тег с процессом пользователя или ВМ — возврат после их выхода
(форма M3a).

## 7. Процесс и бюджет

- Вызов: `chk_m6c.sh <тег>` (стоп, замок, новые комментарии `HPP-850`, очередь — строка `times.txt`) → `launch_m6c.sh <тег>` (только
  запуск) → `wait_m6c.sh <тег>` (≤ 540 с на вызов, до строки `rc=`) → `post_m6c.sh <тег>` вне замка. Каждый вызов `go_m6c.sh` — один
  замок `C:/kyty/SEALED_RUN.lock` (строки `lock taken|released` в `runs/lock.log`); одна проверка сторожа и сессии — сразу после взятия
  замка, до манифеста (форма п. 634 / 660 / 661). Окна между тегами нет.
- Стоп серии: `C:/kyty/m657/STOP`, `SERIES_STOP`, `RETURN_FAILED`; строка `ErrorDeviceLost`/`device lost` в логе или stdout —
  `SERIES_STOP`, вопрос лиду, тег не повторяется (аналог п. 760(б)(2)).
- Бюджет замка ≤ 30 мин на три тега (п. 767(и)); оценка [I] ≈ 7–8 мин замка на тег (вход M3a `m3_i` холодный — 7 мин 24 с).
  Сумма замка по `runs/lock.log` печатается в отчёте; превышение — строка отчёта и вопрос лиду о повторах.
- ГП-кейсы `dl_cases.txt` не запускаются, сборок нет (п. 760).

## 8. Инструменты (sha256 на момент печати)

| Файл | sha256 |
|---|---|
| `go_m6c.sh` | `fe417caada6422850d17daf85f7aa102db8aa94eb35d5a78cb4ac60e3a886030` |
| `launch_m6c.sh` | `ca8f5bf3a81db8bea95fa1cdf4e2c24bbb7858fbbed23a43468131c35ad7afa1` |
| `wait_m6c.sh` | `12810e9ef37a28df509c706fde2dce05f931fd823de0bf0d4245114e71f43802` |
| `chk_m6c.sh` | `44295bed7e4ebe9d6bb7d2f06a9493b5bc6445d00a834384b7a149dead45165c` |
| `post_m6c.sh` | `6a9eed8b0c4ab0f7975ca90c7d0d8a5fddd112707b1227abcf4fda4be100e7f0` |
| `m6c_read.py` | `e2a27aa916bb378c7c61e5a3f0eecb59d0e4acd51cdd6e29450ba9d6d9cb1f06` |
| `test_m6c.py` | `b3e030e5ec1ae1b9d131ac004f667ebfe0fbb7ebde4c5ec2ee09fae1b083791d` |
| `gen_m6c.py` | `1e1df76ad073e5ed8a4a7c802b514acc223abb34b90826981da696778e5e8d7d` |
| `enter_scene.py` | `7b451b0a97695474725d35b2a1554c2e2603c8e51400c7fca0314fad17735751` |
| `procload.py` | `59bc47c4ebcc2dcb870b9644d327c0660941567613fb833aaaa6b129f47abaee` |
| `dispstate.py` | `915f1d6fd23571c570d675eb5737c9ee7c3447c75db991793415e19aa7f85aa4` |
| `idle142.py` | `67992bf45aa2a8a8c70d301a0c61e70d664d211623920da2f6033ce802fe866c` |
| `launch_run.py` | `cf29e302ff1144e61d7c3e7369d5e14a67fad7c8e3fdae2d5e9e31fb6688d001` |
| `run_safety99.py` | `72a26447d8f852f53af241b3cf6b9b6ba1ed81b0efac16c23eace9f6d13b1893` |
| `sheet142.py` | `1416d95868e438ac4ae348f696e8037a1083dc684d2e929f088b11368e5b9b48` |
| `gates_default.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `gates.req` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `sample.req` | `5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9` |
| `manifest_fs4c.py` | `b84c7d759d8da88e82cd9a46576f3277549a33754fc592e30d07c59f6593f0de` |
| `guard_m6c.py` | `fa6977ace5a460510efb85d2aba1e13a4704bb111bde6c49357313c38e7fa741` |
| `hold_m6c.py` | `6d0fdea4a6571b9e094512a8738cbe6b60153284f63fd4ca52f9e6beb2c2645b` |
| `hostload_m6c.py` | `8f27785497c368ff80328c25a97c6ba5705c2a54dee0478f09af1e6504c5ad9b` |
| `snap_m6c.py` | `c0db7362839d7db17de487172a655e58391f729b0ce10a2f61d30b318d9af07b` |
| `mfsub_m6c.py` | `e3fffd797d3a3505d7a60e86af7175407ce0d525c02f93817ea73d2a70fa5ae6` |
| `runchk_m6c.py` | `2c750c80063aa08046fabb36cfc206f96afb50c6f02e15c3a31e779ff6b30725` |
| `queue_m6c.py` | `a96d5ed5bb9594ee59528422728a8adaf1a1d59d3016b2047ea0b7e0e1506ef5` |
| `tempo_m6c.py` | `f5ea9f968981e3c721727dd8e31b12f07f288bbdd1ad15700b63846830eb6bb1` |
| `watch_m6c.py` | `da4e31b198c899f1dc5533f40ec116f329603777bd47afe794c24e876b454206` |
| `C:/kyty/f287/fs15c/fs15c_read.py` | `9ef2975702ce8d3b94afdd9c0f3d9198a743711721fa570ac816acb70bb79cf2` |
| `C:/kyty/KytyPS5/ps5 em/docs/form634_check.py` | `f100a063fbc0063266a6443bac9b68f17e832fddd29456ccb475e7b1e76a4ded` |
| `C:/kyty/scripts/s51_vidglitch.py` | `6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c` |

Копии помощников M3a — `gen_m6c.py` (`gen_m6c.out.txt` sha256 `c8a5d21a…`, `ALL OK`): имена перенесены механически, смысл не меняется.
Фикстуры: `test_m6c.py` → `test_m6c.out.txt` sha256 `49e62cde3c956f1ff2846baa8e32f4bac292d608ca6a4d6922e1e1209115b74c`, первая строка —
`suite … target …`, последняя `ALL OK` (checks 40, failed 0). Линтер формы: `form634_check.py --series C:/kyty/m657/m6c` → `ALL OK`
(`form634_series.out.txt` sha256 `2acbfcd7…`); `--text` этой печати → `ALL OK` (`form634_text.out.txt`). Мутантов нет: набор —
фикстуры харнесса серии тегов в форме M3a [I: форма звеньев тегов трека M].

## 9. Не заявляется

Что любое поле M6 ≥ 1 или 0 в игре вне трёх сцен; что три сцены покрывают игру; что PCM объектных портов читаем любым путём; что модели
M5a верны железу; что GLCache между тегами не менялся другими программами; ни одно число — не выигрыш; 60 FPS не обещается.
