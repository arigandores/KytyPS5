# FS5c (`HPP-511`, Harness Engineer): теги `fs5_v`, `fs5_w`, `fs5_r1` и справка `fs5_hb` на бинаре FS5 `631ff987` — печать до первого тега

Трек F, пятый бинарь отгрузки FS5 (умолчание `KYTY_FIX_F10=1`). Разделы 0–8 — печать (до первого тега; после неё цепочка, ридер и правила
чтения не меняются); раздел 9 — отчёт тегов (строки ридера, без вердикта; вердикт и установка — FS5d `HPP-512`).

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1)

- Задание — п. 410(г)(3): `7de178f9:docs/ROADMAP.md:21783` (якорь «   (3) **FS5c (Harness Engineer, под замком; очередь P > F > S, п. 322(г)).**
  Печать `docs/track-f/fs5c.md` до первого тега»; +1 — «   391(г)(5): манифест sha256 и копия `_ShaderCache/PPSA21564` с `pipelines.bin` и
  кэша драйвера до первого тега, возврат»); перечень тегов — `7de178f9:docs/ROADMAP.md:21788` (якорь «   - `fs5_v` — V Sky Garden (харнессная
  форма): удержание ≥ 300 с после первого кадра сцены»; +1 — «     лида рядом с `sheet_f12_v`, строка `Shader translation cache:` с `_fixf10`»).
  Пункт целиком — `7de178f9:docs/ROADMAP.md:21732` (якорь «410. **Звено F12h трека F (`HPP-482`, лид): F12d, F12e, F12f, F12g ПРИНЯТЫ»).
- Приёмка FS5b — п. 418: `5d37ef09:docs/ROADMAP.md:22047` (якорь «418. **Звено FS5b трека F (`HPP-510`, Red Team; приёмка лида на стадии
  review): FS5b ПРИНЯТ»; +1 — «   (а) **Пересчёт лида [c] на KytyPS5 `1ea5e7a1`:**»); З2 — `5d37ef09:docs/ROADMAP.md:22050` (якорь «   (в) **З2
  (рецепты `pipelines.bin` лежат в каталоге варианта; на первом запуске FS5 стартового precache нет»; +1 — «   (г) **Звенья:** FS5b (`HPP-510`) —
  приём этой строкой»): задание FS5c без изменений.
- Установленный бинарь — FS4 `31cbfee8` (п. 407): `7037b199:docs/ROADMAP.md:21498` (якорь «407. **Звено FS4d трека F (`HPP-473`, лид): факт п.
  394(д)(4) — FS4 `31cbfee8` УСТАНОВЛЕН»; +1 — «   под (B) (K1 при `--shader-validation true`, умолчание лаунчера)»).
- Образцы харнесса: F12f (`docs/track-f/f12f.md`, редакция 2: `go_f12f.sh` `4ccfa541…`, `f12f_read.py` `cd9deca6…`) и FS4c (`docs/track-f/fs4c.md`,
  форма `fs4_r1`).

## 1. Бинарь

- Бинарь тега — копия FS5a `C:/kyty/f287/bin/kyty_emulator_631ff987.exe`, только по sha256
  `631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17` (FS5a `HPP-509`, ревью FS5b PASS, п. 418); текст ревизии `KYTY_GIT_REVISION`
  `0e72bc1` — строка справки ридера (строка `SDL_REVISION` не читается — п. 418(б)(1)).
- Установленный `kyty_emulator.exe` — FS4 `31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5`: сверка до тега (отказ, если иной),
  внутри замка (`installed_before.txt`), после возврата из закреплённой копии `C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe`
  (`installed_after.txt`). FS5 стоит на месте `kyty_emulator.exe` только на время тега (`installed_sha.txt` — после установки).
- Окружение тега — умолчания FS5: цепочка снимает все `KYTY_*` и `VK_LAYER_*`; `KYTY_FIX_F10`, `KYTY_GAME_PATCH`, `KYTY_GPU_CHECKPOINTS` и прочие
  `KYTY_FIX_*` не передаются; переменные — позиционно в `enter_scene.py` (= F12f с корнем `fs5/fs5c`: строки 1 и 86).

## 2. Холод, манифест и RC6 (п. 391(г)(5))

- **Холодная форма:** каталог `_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10` до тега отсутствует (есть — отказ, цепочка ничего не удаляет);
  кэши после каждого тега возвращаются, поэтому каждый тег — холодный вход в новый каталог (`cold.txt`). Справка ридера — первая строка
  `PipelinePrecache: no …variant_fixb26_fixb1b_fixf10…pipelines.bin yet` (З2 п. 418(в): стартового precache на первом запуске FS5 нет).
  Тёплый каталог FS4 `variant_fixb26_fixb1b` не трогается (FS5 при умолчании в него не пишет; `=0` не запускается — п. 410(г)(4)).
- **Манифест:** sha256 `_ShaderCache` (с `PPSA21564/pipelines.bin` обоих каталогов), `_PipelineCache`, `_SaveData`, GLCache драйвера
  (`manifest_fs4c.py`) — до тега; копия всех четырёх; манифест состояния прогона; возврат; манифест после; `cmp` до/после.
- **RC6:** первый тег пишет эталон `runs/ref_manifest.tsv` и постоянную копию `C:/kyty/f287/fs5/fs5c/cache_ref/` (`_ShaderCache/PPSA21564`,
  `_PipelineCache`, GLCache); каждый тег — `cmp` после/эталон; тег с кэшами до старта ≠ эталону не стартует (выход 6, замок снимается).
  Неравенство `cmp` после тега, неудачный возврат или установленный ≠ `31cbfee8` после возврата — `RETURN_FAILED`, замок остаётся, серия стоит,
  вопрос лиду.

## 3. Формы тегов (каждый тег — один замок, одна попытка)

Вызов `launch_fs5c.sh <tag>` только запускает отсоединённую `go_fs5c.sh <tag>`; ожидание — `wait_fs5c.sh <tag>` ≤ 540 с за команду, отдельными
командами; чтение — `post_fs5c.sh <tag>` вне замка. Шлюз `procload.py` (вывод через маску `<app>`) перед замком; замок
`C:/kyty/SEALED_RUN.lock` — только когда его нет (`noclobber`); `runs/lock.log` (UTC); строки событий — `C:/kyty/f287/times.txt`.

| тег | вызов `enter_scene.py <tag> --level <L> --attempts 1 --no-install --require-idle --gates-file gates_default.txt --pred pred/fs5c_seal.md` + |
|---|---|
| `fs5_v` | `underwater_aerial_garden --stable-draws 300 --timeout 480 --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` (харнессная V = `f12_v` без `KYTY_FIX_F10`) |
| `fs5_w` | `underwater_aerial_garden --stable-draws 300 --timeout 600 --emu-arg=--vulkan-validation --emu-arg=true --hold 310 VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` (форма п. 295(б): precache по умолчанию, без `VK_LAYER_MESSAGE_ID_FILTER`, без видео; = `f12_w` без `KYTY_FIX_F10`) |
| `fs5_r1` | `underwater_aerial_garden --stable-draws 300 --timeout 480 --rec --hold 330 --emu-arg=--shader-validation --emu-arg=true KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` (форма `fs4_r1` п. 378(г)(3)) |
| `fs5_hb` | `hoover_beach --stable-draws 300 --timeout 480 --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` (справка, не гейт) |

- **Порядок:** `fs5_v`, `fs5_w`, `fs5_r1`, `fs5_hb` (порядок п. 410(г)(3)). Повтора тега нет (`runs/<tag>` есть — отказ). Отказ шлюза до
  старта эмулятора (выход 3/5/6) попытку не тратит — вывод переносится в `old/` до нового вызова (п. 309(и)). Помеха прогона (событие окна
  `minimized`, `Recovering Vulkan swapchain`, строка `GamePatch:`) — тег не читается как исход, повтор — только пунктом лида.
- **Вариант исполнителя (рядом с буквой).** (1) «V `hoover_beach`» буквой — харнессная V (`--shader-validation false` лаунчера), как `fs5_v`, а не
  форма `fs4_hb` с `--shader-validation true`; `--stable-draws 300` — как `fs4_hb`. (2) Член `fs4_r1` «`validated` последней строки
  `FixSvalStat` ≥ 151» в списке `fs5_r1` п. 410(г)(3) не назван — печатается строкой справки (наличие строки и значение), не членом.
  (3) «Лист лида рядом с `sheet_f12_v`» — `post_fs5c.sh` кладёт рядом `pair_fs5_v_f12_v.png` (слева `fs5_v`, справа `f12_v` F12f); смотрит лид.

## 4. Строки ридера (`fs5c_read.py`, `ROW …: YES/NO/NOT_READ`; вердикта ридер не печатает)

**Каждый тег:** бинарь тега = `631ff987`; установленный `31cbfee8` до тега и после возврата; текст ревизии называет `0e72bc1` (справка);
**строка каталога** — каждая строка `Shader translation cache:` (≥ 1) кончается на `variant_fixb26_fixb1b_fixf10` (член); холодная форма —
`cold.txt` «absent» и первая строка `PipelinePrecache: no …_fixf10…pipelines.bin yet` (справка); вход (`GuestOut: Level has started: <L>`);
удержание ≥ 300 с (сумма `dt_us` строк `FrameTrace` после первого кадра сцены — первой строки с `draws ≥ 100` после строки входа — до смены
сцены); нет конца процесса до таймаута (попытка `enter_scene` не `exited`, `hold_exit` пуст); **кадры ≥ 1 с после первого кадра сцены — строка
отчёта с числом, не гейт** (холод); манифест до = после; после = эталон (RC6); нет помехи. Данные — строки окна всех видов,
`AsyncPipelines: skipped draw`, `[Vulkan][W]`, sha256 лога и stdout.

**`fs5_v`:** + 0 маркеров смерти (`Unhandled exception:`, `--- Fatal Error ---`, `--- Error ---`, `GpuHangAbort:`, `ErrorDeviceLost` в логе и
stdout); видео ≥ 3 000 записей индекса; 0 одно-кадровых глитчей (`s51_vidglitch.py <rec> 4 6`); лист для лида (`sheet142.py`); `FixSval` и
`SPIR-V validation failed` — справка.

**`fs5_w`:** + 0 `[Vulkan][E]`; `[Vulkan][W]` > 0 (положительный контроль слоя); `DualSrcBlend: supported=1 enabled=1` до первой строки с
`GuestOut`; маркеры смерти — справка.

**`fs5_r1`:** + `FixSval: mode=1 ubo_std_layout=1` (все строки), первая — до первой строки с `GuestOut` (член); 0 строк `SPIR-V validation failed`
в логе и stdout (член; хэши `hash=0x…` печатаются); строка `FixSvalStat` (справка, вариант исполнителя (2)); маркеры смерти, видео, глитчи,
лист — как `fs5_v`.

**`fs5_hb` (справка, не гейт):** строки `fs5_v` на уровне `hoover_beach`; ридер печатает «kind hb: REFERENCE, not a gate».

## 5. Отказы и остановка серии

Тег с NO по члену — данные, следующий тег идёт (вывод — FS5d), кроме: `RETURN_FAILED`, установленный ≠ `31cbfee8` после возврата, `cmp` ≠
EQUAL — серия стоит, вопрос лиду. Помеха — вопрос лиду о повторе. Файл `C:/kyty/f287/STOP` — стоп перед следующей командой (общее правило
26). Перед каждым вызовом тега — проверка API (звено прогонов другого трека с идущей серией, комментарии звена) строкой `times.txt`.

## 6. Не заявляется

Что FS5 работает в игре или отгружается (решает FS5d); что кремний PS5 отвечает на типы 2–3 ровно как программный путь GPURT; семантика слов 2–3
на PS5; что правка видна на листе; что дельты счётчиков или времени — доказательство; что Ф20 влияет на игру; что SPIR-V корректен для
устройства и картинка верна; что `[Vulkan][W]` или `skipped draw` холодного входа — дефект или не дефект; что 0 строк `SPIR-V validation failed`
доказывает верность трансляции; ни одно число — не выигрыш; 60 FPS не обещаются; путь установленного `31cbfee8` до FS5d не меняется.

## 7. Инструменты и фикстуры

Файлы — `docs/track-f/fs5c/` (локально `C:/kyty/f287/fs5/fs5c/`), sha256 — `docs/track-f/fs5c/SHA256SUMS_seal.txt`: `go_fs5c.sh`, `launch_fs5c.sh`,
`wait_fs5c.sh`, `post_fs5c.sh`, `fs5c_read.py`, `test_fs5c_read.py` (+ `.out.txt`), `sens_fs5c.py` (+ `.out.txt`), `enter_scene.py`, `procload.py`,
`idle142.py`, `launch_run.py`, `run_safety99.py`, `manifest_fs4c.py`, `sheet142.py`, `gates_default.txt` (= F12f), пробы `probe_f12_v.txt`,
`probe_fs4_r1.txt`. Копия `launch_run.py` в git — с маской `<app>` в строке комментария 109 (общее правило 28; = `f12f/launch_run.py` в git),
локальная — без маски.

Фикстуры (`test_fs5c_read.py`, 172 проверки): виды тегов и отказ чужих; положительный тег по трём видео-видам; края удержания 300 с / 300 с −
1 мкс (V и W), видео 3 000 / 2 999 / нет индекса, глитч 1, нет строки глитча, нет листа, кадры ≥ 1 с (строка отчёта, удержание не страдает),
999 999 мкс не считается, смена сцены, `draws` 99/100, вход на чужом уровне; маркеры смерти в логе и stdout; конец процесса (оба вида, нет json —
`NOT_READ`); строка каталога (база, смесь, нет строки, прямые слэши, суффикс после `_fixf10`); холодная форма (нет «absent», нет `cold.txt`,
тёплая первая строка `PipelinePrecache`, строка базового каталога, нет строки); `FixSval` (mode 0, ubo 0, после `GuestOut`, нет строки, вторая с
mode 0; справка у V); `SPIR-V validation failed` в логе и stdout с хэшем, справка у W; `FixSvalStat` (нет, последняя строка, не путается с
`FixSval`); бинарь тега, установленный до/после (иной, нет файла, `540c035a`); ревизия (чужая, нет, `git =`); манифесты (`DIFFER` своего и
эталона, нет файлов); помехи (`minimized`, `Recovering`, `GamePatch:`) и данные (фокус, `restored`, `skipped draw`); W (`[Vulkan][E]` 1,
`[Vulkan][W]` 0, `DualSrcBlend` после `GuestOut`, `enabled=0`, нет строки, смерть — справка); вывод в строгом cp1250 без `PYTHONIOENCODING`, только
ASCII, json, отказ неизвестного вида. Ручная чувствительность (`sens_fs5c.py`, 14 правок ридера: порог удержания, строка каталога, порог кадра
1 с, порог видео, `GamePatch`, `[Vulkan][W]`, установленный до и после, член `SPIR-V validation failed` и его stdout, `FixSval` mode/ubo и порядок
с `GuestOut`, каталог в строке `PipelinePrecache`, строка эталона) — каждая роняет ≥ 1 фикстуру, `SENS ALL OK`. Мутантов нет (п. 410(г)(3)).
Пробы ридера на чужих логах (данные, не члены): `probe_f12_v.txt` — лог `f12_v` F12f (бинарь `b714f5c4`, установленный `540c035a`: строки
бинаря, установленного до/после и ревизии — 4 NO, прочие 15 YES), `probe_fs4_r1.txt` — лог `fs4_r1` FS4c (`FixSval` mode=1 до `GuestOut`, `FixSvalStat` validated 256, 0 отказов;
каталог без `_fixf10` — NO).

### 7а. Последний вывод набора (до печати)

`C:/kyty/f287/fs5/fs5c/test_fs5c_read.out.txt` (= `docs/track-f/fs5c/test_fs5c_read.out.txt`), sha256 — в `SHA256SUMS_seal.txt`; первая строка —
`suite test_fs5c_read.py sha256 27b9464f2aacab7244b41df825f4ac0a7c258e680a9f5d33f5d1bd8c14bf5cca target fs5c_read.py sha256
4e3e04bdfbd721569606ef623104f1b59982c2afb47c01f90b9c956b5eabbca5`; `checks 172 fails 0`, `ALL OK`. Чувствительность — `sens_fs5c.out.txt`,
`SENS ALL OK`.

## 8. Печать

Копия разделов 0–8 — `C:/kyty/f287/fs5/fs5c/pred/fs5c_seal.md` (`--pred` каждого тега; sha256 — строка `pred/fs5c_seal.md` файла
`SHA256SUMS_seal.txt`). После печати цепочка, ридер и правила чтения не меняются; правка — новой редакцией в разделе 9 с причиной, до тега,
которого касается.
