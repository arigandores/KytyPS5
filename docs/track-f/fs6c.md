# FS6c (`HPP-557`, Harness Engineer): теги `fs6_v`, `fs6_w` на бинаре отгрузки FS6 `9325446c` при умолчаниях — печать до первого тега

Трек F, Б4, шестой бинарь отгрузки FS6 (умолчание `KYTY_FIX_B4=1`, п. 454(г)). Разделы 0–8 — печать (до первого тега; после неё цепочка,
ридер и правила чтения не меняются); раздел 9 — отчёт тегов (строки ридера, без вердикта; вердикт — FS6d `HPP-558`).

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1)

- Задание — п. 454(г)(3): `e898ddf1:docs/ROADMAP.md:22502` (якорь «   (3) **FS6c (Harness Engineer»; +1 — «   - `fs6_v` — форма `b4_v`»);
  пункт целиком — `e898ddf1:docs/ROADMAP.md:22495` (якорь «454. **Звено F15f»; +1 — «   (а) **Приёмка строкой по членам п. 412(г).**»).
- Бинарь FS6 — п. 461: `e898ddf1:docs/ROADMAP.md:22547` (якорь «461. **Звено FS6a»; +1 — «   (а) **Приёмка строкой. FS6a ✓**»); опознание
  бинаря тегов — п. 461(г): `e898ddf1:docs/ROADMAP.md:22551` (якорь «   (г) **Н1 п. 454(в) для FS6»; +1 — «   (д) **Долги (п. 324(и)(5)):**»).
- Приёмка FS6b — п. 476: `e898ddf1:docs/ROADMAP.md:22653` (якорь «476. **Звено FS6b»; +1 — «   (а) **Приёмка строкой: FS6b ✓**»).
- Маска `<app>` в `enter_scene.py` до печати — п. 463(д)(2): `e898ddf1:docs/ROADMAP.md:22571` (якорь «   (д) **Долги F18e»; +1 — «   (е) **Звенья:** F18e»);
  исполнено комментарием `7ba0b788` в `HPP-557` (2026-10-04 13:21Z).
- Окно FS6b — п. 473(б)(2): `e898ddf1:docs/ROADMAP.md:22636` (якорь «      (2) Harness Engineer во всех звеньях серий»; +1 — «      (3) Сборка и стенд FS6b»).
- Образец — F15e: `d5d0076a:docs/track-f/f15e.md:43` (якорь «## 3. Форма тега»; +1 — пустая строка); форма W — FS5c `fs5_w` (`docs/track-f/fs5c.md`).
- Карта ссылок — `docs/track-f/fs6c/refs_fs6c.py`, вывод `refs_fs6c.txt` (8 из 8 по якорю и +1, `ALL OK`).

## 1. Бинарь

- Бинарь тегов — копия FS6 `C:/kyty/f287/bin/kyty_emulator_9325446c.exe` (worktree `3904522d` = S12a `4d9e8ab7` + `a86a5ad0` + `17eb924e`), только по
  sha256 `9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2` и строке версии в файле бинаря `KytyPS5-2026-09-15-6a2987a-1879-g3904522d`
  (п. 461(г); проверено до печати: в файле одна такая строка, `FixB4: mode=` — 1 вхождение). Текст ревизии лога — справка, ждётся `3904522`.
- Установленный `kyty_emulator.exe` — S12 `adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421`: сверка до тега (отказ, если иной),
  внутри замка (`installed_before.txt`), после возврата из закреплённой копии `C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe` (`installed_after.txt`).
  Копия FS6 стоит на месте `kyty_emulator.exe` только на время тега (`installed_sha.txt` — после установки); это не установка FS6 (FS6d).
- Окружение тегов — **умолчания бинаря**: цепочка снимает все `KYTY_*` и `VK_LAYER_*`; `KYTY_FIX_B4`, иные `KYTY_FIX_*`, `KYTY_GAME_PATCH`,
  `KYTY_GPU_CHECKPOINTS` не передаются. Позиционно в `enter_scene.py`: `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`; у `fs6_w` ещё
  `VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin`, `VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000` (+ переменные самого `enter_scene.py`:
  `KYTY_FRAME_TRACE=lite`, `KYTY_GPU_HANG_ABORT_S=8`, `KYTY_GATE_FILE`, `KYTY_SAMPLE_GATE`, `KYTY_QUEUE_TRACE=1`,
  `KYTY_GUEST_ARGS=-lvl underwater_aerial_garden`, у `fs6_v` — `KYTY_REC`).
- Подпись трансляции FS6 `26ce5fc7` = установленному (п. 461(б)) ⇒ каталог `variant_fixb26_fixb1b_fixf10` тёплый; его наличие до старта
  пишется в `warm.txt` (справка, не отказ).

## 2. Кэши, сохранения и манифест

- **Манифест:** sha256 каждого файла `_ShaderCache` (с `PPSA21564/pipelines.bin` и каталогами вариантов), `_PipelineCache`, `_SaveData` и GLCache
  драйвера (`manifest_fs4c.py`) — до тега (`manifest_before.tsv`); копия всех четырёх (`runs/<тег>/before_*`); манифест состояния после тега до
  возврата (`manifest_run.tsv`); возврат; манифест после (`manifest_after.tsv`); `cmp` до/после — `manifest_cmp.txt` (член: `manifest cmp EQUAL`).
  Один тег — один замок; копия и возврат — внутри замка каждого тега.
- **`_SaveData`** (строка отчёта, не гейт): строки `_SaveData` из `manifest_before.tsv` и `manifest_run.tsv` — число файлов, равны ли,
  отличающиеся пути.
- Неравенство `cmp` после возврата, неудачный возврат или установленный ≠ `adb0c82f` после возврата — `RETURN_FAILED`, замок остаётся, вопрос лиду.

## 3. Форма тегов (один тег — один замок, одна попытка)

Вызов `launch_fs6c.sh <тег>` только запускает отсоединённую `go_fs6c.sh <тег>`; ожидание — `wait_fs6c.sh <тег>` ≤ 540 с за команду, отдельными
командами; чтение — `post_fs6c.sh <тег>` вне замка. Шлюз `procload.py` (вывод через маску `<app>`) перед замком; замок `C:/kyty/SEALED_RUN.lock` —
только когда его нет (`noclobber`); `runs/lock.log` (UTC); строки событий — `C:/kyty/f287/times.txt`. Файл `C:/kyty/f287/FS6B_WINDOW` моложе 900 с —
тег не запускается (выход 6, строка `times.txt`; п. 473(б)(2)). Порядок: `fs6_v`, затем `fs6_w`.

| тег | вызов |
|---|---|
| `fs6_v` | `enter_scene.py fs6_v --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file gates_default.txt --pred pred/fs6c_seal.md --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` (= форма `b4_v` F15e без `KYTY_FIX_B4=1`) |
| `fs6_w` | `enter_scene.py fs6_w --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 600 --no-install --require-idle --gates-file gates_default.txt --pred pred/fs6c_seal.md --emu-arg=--vulkan-validation --emu-arg=true --hold 310 VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` (= форма `fs5_w` FS5c: W п. 295(б), precache по умолчанию, без `VK_LAYER_MESSAGE_ID_FILTER`, без видео) |

- **Выход харнессом.** В конце удержания `enter_scene.py` шлёт `WM_CLOSE` окну процесса (в логе — `Event: quit`) и ждёт конца процесса
  `CLOSE_WAIT_S` = 40 с (таймаут харнесса выхода); не кончился — `kill`. `enter_scene.py` = файл F15e с корнем `C:/kyty/f287/fs6c` и маской `<app>`
  в строке `pre_run: host … top by CPU:` `run.txt`, в разделе `host` и `gpu_apps` json (п. 463(д)(2); фикстуры `test_enter_scene_mask.py`, 13 проверок).
- Повтора тега нет (`runs/<тег>` есть — отказ). Отказ шлюза или окна до старта эмулятора (выход 3/5/6) попытку не тратит — вывод переносится в
  `old/` до нового вызова (п. 309(и)). Помеха прогона (событие окна `minimized`, `Recovering Vulkan swapchain`, строка `GamePatch:`, BUSY) — тег не
  читается как исход; повтор — пунктом лида.

## 4. Строки ридера (`fs6c_read.py`, `ROW …: YES/NO/NOT_READ`; вердикта ридер не печатает)

Члены обоих тегов:
- бинарь тега = `9325446c` по sha256 и строка версии `…-1879-g3904522d` в файле бинаря; установленный `adb0c82f` до тега и после возврата;
- окружение: ни одного `KYTY_FIX_*` (в том числе `KYTY_FIX_B4`), нет `KYTY_GAME_PATCH`, `KYTY_GPU_CHECKPOINTS` (по `<тег>.json`);
- `FixB4: mode=1` — ≥ 1 строки, все `mode=1`, первая до первой строки с `GuestOut`;
- вход (`GuestOut: Level has started: underwater_aerial_garden`); удержание ≥ 300 с (сумма `dt_us` строк `FrameTrace` после первого кадра сцены —
  первой строки с `draws ≥ 100` после строки входа — до смены сцены); процесс дожил до конца удержания (исход попытки `ok`, `hold_exit` пуст);
- манифест кэшей, сохранений и GLCache до = после возврата; нет помехи.

Члены `fs6_v` (форма `b4_v`, п. 412(г)(5)):
- 0 маркеров смерти (`Unhandled exception:`, `--- Fatal Error ---`, `--- Error ---`, `GpuHangAbort:`, `ErrorDeviceLost` в логе и stdout);
- видео ≥ 3 000 записей индекса; 0 одно-кадровых глитчей (`s51_vidglitch.py <rec> 4 6`); лист для лида (`sheet142.py`); пара
  `pair_fs6_v_b4_v.png` (слева `fs6_v`, справа `b4_v` F15e) — «лист лида рядом с `b4_v`»;
- выход харнессом: строка `Event: quit` в логе есть; после первой такой строки в логе 0 строк `--- Fatal Error ---` и 0 строк
  `m_files[index] == nullptr`; процесс кончился до таймаута харнесса (`close_killed` false и `close_rc` не пуст).

Члены `fs6_w` (W п. 295(б)): 0 строк `[Vulkan][E]`; строк `[Vulkan][W]` > 0 (положительный контроль слоя); `DualSrcBlend: supported=1 enabled=1`
до первой строки с `GuestOut`. Справка `fs6_w` (форма FS5c `fs5_w`): маркеры смерти, `Event: quit` и фаталы после неё, конец процесса до таймаута.

Строки отчёта (не гейт): код выхода (`close_rc`, десятичный и hex); `_SaveData` до / после тега; кадры ≥ 1 с после первого кадра сцены
(число); счёт `--- Fatal Error ---` и `m_files[index] == nullptr` по всему логу и stdout. Справка: текст ревизии `3904522`; каталог
`variant_fixb26_fixb1b_fixf10` в каждой строке `Shader translation cache:`; тёплая форма (`warm.txt` «present»); `AsyncPipelines: skipped draw`,
`[Vulkan][E]` у `fs6_v`, строки «last time reporting it», строки окна; sha256 лога и stdout.

## 5. Отказы и остановка

`RETURN_FAILED`, установленный ≠ `adb0c82f` после возврата, `cmp` ≠ EQUAL — замок остаётся, вопрос лиду. Помеха — вопрос лиду о повторе.
Файл `C:/kyty/f287/STOP` — стоп перед следующей командой (общее правило 26). Перед вызовом тега — проверка API (комментарии звена, звенья
`in_progress`) строкой `times.txt`; очередь замка P > F > S (п. 322(г)); серия S13b `HPP-500` (трек S) — замок берётся между её тегами, установленный
между тегами S13b не меняется (п. 464(г)(3)); теги F20c `HPP-561` — последние в очереди замка (п. 462).

## 6. Не заявляется

Что FS6 установлен (до FS6d); что Б4 воспроизводится в игре на текущих сборках и что его правка нужна игре; что p_s стенда — частота игры;
что `KernelRead` под гонкой падает так же; что Б4 теряет сохранения (строка `_SaveData` — отчёт, не довод); что Ф21 случается в игре; что Ф19
`FIXED` до F14h; что Ф7 или Ф5 — дефект или не дефект до F16b; что SPIR-V корректен для устройства и картинка верна; что код выхода 0 или
0 фаталов одного выхода доказывают правку; что W без ошибок слоя доказывает отсутствие ошибок, которые слой не сообщает; ни одно число —
не выигрыш; 60 FPS не обещаются; путь установленного `adb0c82f` не меняется.

## 7. Инструменты и фикстуры

Файлы — `docs/track-f/fs6c/` (локально `C:/kyty/f287/fs6c/`), sha256 — строки `seal:` ниже и `docs/track-f/fs6c/SHA256SUMS_seal.txt`:
`go_fs6c.sh`, `launch_fs6c.sh`, `wait_fs6c.sh`, `post_fs6c.sh`, `fs6c_read.py`, `test_fs6c_read.py` (+ `.out.txt`), `sens_fs6c.py` (+ `.out.txt`),
`enter_scene.py`, `test_enter_scene_mask.py` (+ `.out.txt`), `procload.py`, `idle142.py`, `launch_run.py`, `run_safety99.py`, `manifest_fs4c.py`,
`sheet142.py`, `gates_default.txt` (= F15e), `refs_fs6c.py` (+ `.txt`). Копия `launch_run.py` в git — с маской `<app>` (= `f15e/launch_run.py` в git),
локальная — без маски.

Фикстуры (`test_fs6c_read.py`, 191 проверка, `ALL OK`): константы печати; положительные теги `v` и `w` (все строки `YES`, число строк); у `w` нет
строк видео, у `v` нет членов W; бинарь тега (иной, F15c, = установленному S12, нет файла), строка версии (F15c, S12, нет файла), установленный
до/после (FS5, бинарь тега, нет файла); окружение (`KYTY_FIX_B4=1` у `v` и `w`, `=0`, пустое, лишний `KYTY_FIX_F10`, `KYTY_GAME_PATCH`,
`KYTY_GPU_CHECKPOINTS`, имя не вида `KYTY_FIX_`, `VK_LAYER_*` у `w`, нет json); ревизия (F15c, форма `git =`, нет); каталог (база, прямые слэши,
суффикс, нет строки); тёплая форма (absent, нет файла); `FixB4` у `v` и `w` (`mode=0`, нет строки, после `GuestOut`), вторая с `mode=0`, две с
`mode=1`, `mode=10`; вход на чужом уровне и удержание 300 с − 300 мкс у `v` и `w`; ровно 300 с / 300 с − 1 мкс; кадр 1 000 000 мкс считается,
999 999 — нет, кадр ≥ 1 с удержание не портит; смена сцены; `draws` 99/100; конец процесса в удержании и исход `timeout` у `v` и `w`; каждый
маркер смерти в логе и stdout (`v`), справка у `w`; видео 3 000 / 2 999 / нет индекса, глитч 1, нет строки глитча, нет листа; нет `Event: quit`,
фатал и `m_files` после выхода, до выхода, счёт stdout, вторая строка `Event: quit`; у `w` — справка; выход: `kill`, процесс жив, код 321 (hex),
отрицательный код (hex), нет записи выхода; `w` — `kill` справкой; W: 1 `[Vulkan][E]`, 0 `[Vulkan][W]`, `DualSrcBlend` после `GuestOut` /
`enabled=0` / `supported=0` / нет строки, «last time reporting» — счёт, `[Vulkan][E]` у `v` — не член; `_SaveData` отличается (строки не меняются)
и нет манифеста после; манифест `DIFFER` и нет файла у `v` и `w`; помехи и данные у `v` и `w`; нет лога; вывод в строгом cp1250 без
`PYTHONIOENCODING`, только ASCII, json, отказ чужого тега и вида. Ручная чувствительность (`sens_fs6c.py`, 26 правок ридера): каждая ловится
набором (`ALL OK`). Мутантов нет (форма FS5c, F15e; п. 454(г)(3)).

## 8. Варианты исполнителя (рядом с буквой; вопрос лиду — в отчёте шага)

1. «Лист рядом с `b4_v`» — пара `pair_fs6_v_b4_v.png` (слева `fs6_v`, справа `b4_v` F15e `C:/kyty/f287/f15e/runs/b4_v/sheet_b4_v.png`); смотрит лид.
2. «Таймаут выхода» — `CLOSE_WAIT_S` = 40 с после `WM_CLOSE` (как F15e); «после `Event: quit`» — по логу после первой такой строки; в stdout
   строки `Event: quit` нет — счёт по всему stdout рядом, не гейт.
3. «`_SaveData` после» — состояние после тега до возврата (`manifest_run.tsv`).
4. `fs6_w`: «удержание ≥ 300 с» читается тем же определением, что у `fs6_v` (сумма `dt_us` после первого кадра сцены), плюс «процесс дожил до
   конца удержания»; маркеры смерти и выход у W — справка (форма FS5c `fs5_w`; в букве п. 454(г)(3) для `fs6_w` их нет).
5. Окружение «при умолчаниях» читается строго: в окружении тега нет ни одного имени `KYTY_FIX_*` (член обоих тегов); `FixB4: mode=1` в логе —
   свидетельство умолчания бинаря.
6. Каталог и тёплая форма — справка (подпись `26ce5fc7` = установленному по п. 461(б)).

### Строки `seal:` (sha256 файлов `C:/kyty/f287/fs6c/` на момент печати)

```
seal: 16aa88a9d2e94a1579f7b3ac4d68d4263fd9d179a4b4e72e3035461da87e547c go_fs6c.sh
seal: 32118a1abd29d7fcba8b0e368b52edc43848327e1ee83f99a7a13a6f5b10ab33 launch_fs6c.sh
seal: 53e6b9bc57d6d1f9ca58eb3f447989cfa4370c0cf3fb7838fd70736c79bcbe6d wait_fs6c.sh
seal: 365c5eb1dd52fc641009f57775cc795776ab7c298bfeff3c1df8ba1c6b8f2564 post_fs6c.sh
seal: 04ba7ba427fab60650cb88d9d2b789f4c110860eeac91f5888966fcf0f9877f9 fs6c_read.py
seal: dcfbebee4b48043cfc16fa1b2d4ef2cb85fe57c0dd0eea262aa8f7e5f14458b0 test_fs6c_read.py
seal: 3722a36ec2133ab5253c8945c211bf6e528ff590b1dc0e42bb3399d3c0bfd8c7 test_fs6c_read.out.txt
seal: 0ba2eb60098312cb7da9d82eab22a534affd5a31946806e18010334ec6930801 sens_fs6c.py
seal: d041b2deaf0d0d8e662a4ed66ffee26f4c4ad9984c1d236464d16f63c0ce972d sens_fs6c.out.txt
seal: 15b852b663bf02fb1e19257e224cb6d6ab26f70ee257affd736b7b22caa0f65d enter_scene.py
seal: 2677ab90615820ba12143d532864abffbf54fb08c9de5bccdd195d5384876dda test_enter_scene_mask.py
seal: a937c1a363414eddc3208828c815b86df3a3bcff1a7dd7e3e3cd869490cfd262 test_enter_scene_mask.out.txt
seal: d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0 procload.py
seal: c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96 idle142.py
seal: c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21 launch_run.py
seal: 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 run_safety99.py
seal: a7096fd47f70419a5ed8d541778294f3032ca2c88e7b4b2e946f3d99651182bb manifest_fs4c.py
seal: c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d sheet142.py
seal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 gates_default.txt
seal: 647a054c0176fce0521585b04d8eafeee87ebeeb450e7205febd91bdb27b80e9 refs_fs6c.py
seal: 92a5bfdf4553cc7470bb5688e14ca68437c46b37d127acc9579ffcf567dcbdbe refs_fs6c.txt
```
