# FS3c (`HPP-449`, Harness Engineer): печать и теги бинаря отгрузки FS3 под замком

## 0. Печать (до первого тега; после неё харнесс, ридер и правила не меняются)

Решения лида (ссылки — `<коммит>:<путь>:<строка>`, якорь и контроль +1 сверены `git show` 2026-10-03T05:19:21Z):

- п. 367 — `17b4aed6:docs/ROADMAP.md:19917` (якорь «367. **Звено F9h трека F (`HPP-425`, лид)»; +1 — «прошла; счёт трека F, не отгрузка»),
  подпункт (г) — `17b4aed6:docs/ROADMAP.md:19943` (якорь «(г) **Отгрузка — FS3»; +1 — «(1) **FS3a (Emu Engineer, без замка).**»), члены (г)(3),
  (ж);
- п. 363 — `3e44d511:docs/ROADMAP.md:19746` (якорь «363. **Звено F9g трека F (`HPP-424`, Harness Engineer) принято»), подпункт (в) — долг строки
  экстента, закрываемый строкой `FixB42Ext` FS3a;
- строка лида к печати — комментарий `417cc2d8` звена (замечание З2 ревью FS3b, `84223933:docs/track-f/fs3b-review.md:93`, якорь «- **З2 — строка
  `FixB42Ext` может не показать последний рост счётчиков экстента.**»): чтение справки `fs3_u` — §4, строка «EXT reference».

Пункты после выдачи звена перечитаны до печати: 368 (трек P, P37 — объём FS3c не меняет), 369 (F10b: F10e `HPP-453` — после FS3c, объём не меняет),
370 (F7e — объём не меняет). Отчёты-образцы: `3f6bb416:docs/track-f/f9g.md` (форма тегов и ридера), FS2c (`fs2_w` — форма W п. 295(б)).

## 1. Бинарь

- **FS3** `540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1` — копия `C:/kyty/f287/bin/kyty_emulator_540c035a.exe` (отчёт
  `cd7977f7:docs/track-f/fs3a.md`, коммит кода `4e72289e`, worktree `d515b901`; ревью FS3b `84223933:docs/track-f/fs3b-review.md` — **PASS**, 0 RC).
- Запуск (форма F9g): внутри замка тега копия ставится на место `kyty_emulator.exe` папки эмулятора (тот же путь exe — те же кэши драйвера), sha
  проверяется после установки; в ловушке EXIT установленный **`4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac`** возвращается из
  закреплённой копии `C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe` и сверяется по sha. `_ShaderCache`, `_PipelineCache`, `_SaveData` и GLCache драйвера —
  копия до установки и возврат после тега. Возврат не удался — `C:/kyty/f287/fs3/RETURN_FAILED`, замок остаётся.

## 2. Харнесс (`C:/kyty/f287/fs3/fs3c/`, в git — `docs/track-f/fs3c/`)

| файл | что |
|---|---|
| `go_fs3.sh` | один тег = один замок; порт `go_f9g.sh` F9g: бинарь FS3 вместо F9e2c, теги п. 367(г)(3), окружение без `KYTY_*`/`VK_LAYER_*` кроме названного |
| `launch_fs3.sh`, `wait_fs3.sh` | только запуск отсоединённого вызова тега и ожидание ≤ 540 с отдельными командами («Процесс» 2 п. 324(и)); вывод отказанного вызова переносится в `old/` до нового вызова |
| `post_fs3.sh` | разбор сделанного тега вне замка: строки ридера, `s51_vidglitch.py <rec> 4 6`, листы, пары `u0`/`u` |
| `run_fs3.py` | `run_f9g.py` F9g без изменения смысла (exe по абсолютному пути, `WM_CLOSE`, окружение из позиционных пар) |
| `fs3_read.py` | ридер тега: строки §4 (порт `f9g_read.py` со строкой `FixB42Ext:`) |
| `test_fs3_read.py` | фикстуры ридера; вывод `test_fs3_read.out.txt` кончается `ALL OK` |
| `enter_scene.py`, `idle142.py`, `procload.py`, `gates_default.txt`, `sheet142.py`, `run_safety99.py`, `launch_run.py` | файлы F9g, у `enter_scene.py` перенесён только `ROOT` |
| `keys_a2_presents.txt`, `sheets_f9d.py`, `cmp_sheets.py` | ввод формы V1 F9g в present, листы F9d/F9g, листы пар (= файлы F9g) |

Мутантов нет — форма звеньев прогонов трека F (п. 367(г)(3); FS2c, F9g: ридер + фикстуры).

## 3. Формы тегов (п. 367(г)(3); каждый тег — свой замок; теги — только при свободном замке между тегами трека P, очередь P > F > S)

Общее: при умолчаниях FS3; `KYTY_FIX_B42`, `KYTY_GAME_PATCH`, `KYTY_GPU_CHECKPOINTS`, `KYTY_CMASK_CLEAR` и прочие `KYTY_*` не передаются, кроме
названного в строке тега (окружение `run_fs3.py`/`enter_scene.py` строится из позиционных пар; `go_fs3.sh` снимает `KYTY_*` и `VK_LAYER_*` до вызова);
`KYTY_GPU_CLOCK_PIN=1` во всех тегах.

| тег | ручка | форма |
|---|---|---|
| `fs3_u` | — (умолчание) | форма V1 F9g (`f9g_v1`): `run_fs3.py` 215 с, `KYTY_GUEST_ARGS=-lvl underwater_aerial_garden`, `KYTY_KEYS=$(cat keys_a2_presents.txt)`, `KYTY_REC`, `KYTY_FRAME_TRACE=lite`, без валидации, закрытие `WM_CLOSE` |
| `fs3_u0` | `KYTY_FIX_B42=0` | та же форма (контроль, что умолчание — эта ручка) |
| `fs3_w` | — | W Sky Garden формы п. 295(б) = `fs2_w` FS2c без стенда `KYTY_TEST_MINIMIZE`: `enter_scene.py --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 600 --no-install --require-idle --gates-file gates_default.txt --pred <печать> --emu-arg=--vulkan-validation --emu-arg=true --hold 310 VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_MARKERS=0`; без `VK_LAYER_MESSAGE_ID_FILTER`, precache по умолчанию (`KYTY_PIPELINE_PRECACHE` не передаётся), без видео, вход без ввода |
| `fs3_v` | — | V Sky Garden формы `SCENE_OK` (= `f9g_sg` без `KYTY_FIX_B42`): `enter_scene.py --level underwater_aerial_garden --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file gates_default.txt --pred <печать> --rec --hold 330 KYTY_GPU_MARKERS=0`, вход без ввода |
| `fs3_hb` | — | то же, `--level hoover_beach` (= `f9g_hb` без `KYTY_FIX_B42`) |
| `fs3_pu` (справка, не гейт) | `KYTY_GAME_PATCH=C:/kyty/KytyPS5/patches/PPSA21564_pvar.txt` | форма `fs3_u` + файл патча (sha256 §9); `KYTY_POKE`, `KYTY_PVAR*` не передаются |

Порядок: `fs3_u`, `fs3_u0`, `fs3_w`, `fs3_v`, `fs3_hb`, `fs3_pu`. Вызов — `bash C:/kyty/f287/fs3/fs3c/launch_fs3.sh <тег>` (только запуск), ожидание —
`bash C:/kyty/f287/fs3/fs3c/wait_fs3.sh <тег>` отдельными командами до строки `rc=`; разбор — `bash C:/kyty/f287/fs3/fs3c/post_fs3.sh <тег>` вне замка.
По одной попытке; провал члена — данные, серия идёт дальше. **Повтор (единственный, п. 367(г)(3)):** `fs3_u0` без клеток с плитками в неподвижной
фазе — один повтор `fs3_u0r`; второй без плиток — стоп серии и пункт лида. Отказ шлюза до старта эмулятора (BUSY, замок, `--require-idle`, отказ
`enter_scene.py` до запуска) — не попытка, тег вызывается снова. Строка `Window <id> minimized` или `Recovering Vulkan swapchain` в теге — тег не
читается как исход, вопрос лиду о повторе (п. 273(з)). Нет ни одной строки `FixB42:` с `hit_all` ≥ 1 при умолчании — строка «справка: `hit = 0`» и
вопрос лиду (повтора п. 367(г)(3) не называет).

## 4. Строки ридера (`fs3_read.py`, по тегу; вердикта ридер не печатает)

- **Строка `FixB42:`** формы п. 353(г)(3) (как F9g): `mode`, `hit`, `applied`, `drawn`, `rearm`, `hit_all`, `last_frame`, `extent`, `cmask`, `clear`;
  рваная строка считается отдельно. **Строка `FixB42Ext:`** формы п. 367(г)(1): `FixB42Ext: mode=<0|1> extent=<w>x<h> hit=<n> applied=<n> drawn=<n>
  rearm=<n> frame=<n>`; рваная — отдельно. **Рост** — значение минус значение на предыдущей строке того же экстента и того же вида строки (до первой — 0).
- **present позиции лога** = `n` следующей строки `FrameTrace` + сдвиг (медиана «present − n» по строкам `InputScript: press|release … (present P)`).
  Фазы (форма F9d/F9g): подход present < 3841; «в воде с вращением» [3841, 5851); шаги [5851, 5951); **«неподвижная камера сбоку»** ≥ 5951 (v ≥ 5950)
  до последнего present прогона.
- **Форма:** все строки `FixB42:` и `FixB42Ext:` `mode` = ожидаемому (1 у `u`, `w`, `v`, `hb`, `pu`; 0 у `u0`), иначе `FORM ERROR`; `GamePatch:` — 0
  (кроме `pu`: строки `GamePatch: applied` ≥ 1 и `GamePatch: refused` 0 — справка).
- **Член «строки `FixB42: mode=1`»** (`u`, `w`; печатается и у `v`, `hb`, `pu`): ≥ 1 строки `FixB42:` и форма `OK`. У `u0` — та же строка с `mode=0`.
- **EXT reference (`fs3_u`, справка, не гейт; строка лида `417cc2d8`):** рост `applied` экстента 960×540 в фазе неподвижной камеры **показан**
  (`SHOWN`), только если строка `FixB42Ext … extent=960x540` с present в фазе или после неё (present ≥ 5951) несёт `applied` больше последней строки
  `FixB42Ext … extent=960x540` до фазы (present < 5951; нет такой — 0); отсутствие такой строки — **`NOT_DETERMINED`**, не «не растёт»; строка 960×540
  без present (нет строк `InputScript`) — `NOT_DETERMINED`. **Вариант исполнителя рядом:** база — наибольший `applied` любой строки 960×540
  (`FixB42:` или `FixB42Ext:`) до фазы. Печатаются все строки `FixB42Ext … extent=960x540` (номер строки лога, present, фаза, счётчики, `frame`).
- **Строка C0 (`fs3_u0`):** ≥ 1 строки (`FixB42:` или `FixB42Ext:`) `mode=0`, `extent=960x540`, `hit` ≥ 1, `applied=0`; плитки — по листу (§5).
- **`drawn` > 0 у 960×540** (`u`, `pu`) — строка п. 353(д)(3) «читать так: T6 получил draw» и вопрос лиду; `drawn`, `rearm`, `clear`, `cmask`, нарушения
  «рост `hit` > рост `applied`» у 960×540 (по видам строк) — справка.
- **Вход** — первая строка `GuestOut: Level has started: <уровень формы>`; смена сцены — любая следующая такая строка; первый кадр сцены — первая
  строка `FrameTrace` после входа с `draws` ≥ 100. **Кадры ≥ 1 с** — строки `FrameTrace` с `dt_us` ≥ 1 000 000 после первого кадра сцены (до смены
  сцены) — член `u`, `u0`, `w`, `v`; у `hb` — справка (п. 367(г)(3) у `fs3_hb` его не называет); по всему логу — справка. **Удержание** — сумма `dt_us`
  после первого кадра сцены (`w`, `v`, `hb`: ≥ 300 с).
- **Маркеры смерти** — `Unhandled exception:`, `--- Fatal Error ---`, `--- Error ---`, `GpuHangAbort:`, `ErrorDeviceLost` в логе и stdout эмулятора.
- **W:** `[Vulkan][E]` — 0; валидация активна — ≥ 1 строки `[Vulkan][W][2]`/`[Vulkan][E][2]`; строки «last time reporting it» — справка;
  `DualSrcBlend: supported=1 enabled=1` до первой строки с `GuestOut`.
- **Видео:** записей `.idx` — член ≥ 3 000 (`u`, `u0`, `v`, `hb`, `pu`); кадров и глитчей — `s51_vidglitch.py <rec> 4 6` («frames …, index entries …»,
  «one-frame glitches: N»); член — 0 (`u`, `v`, `hb`).
- Справка: `AsyncPipelines: skipped draw` (форма Б5), события окна, строки `FrameTrace`, `hit_all`.

## 5. Признак плиток, листы и счёт клеток (форма F9g)

- **Признак (п. 349(г)):** клетка листа, где в пруду видны прямоугольные блоки чужого экранного содержимого, чёрные/цветные блоки или белое
  «облако»; эталон — листы F9a/F9d и `c0_static4_01` F9g. Клетка без пруда — «пруда нет», в счёт плиток не входит, считается отдельно.
- **`u`, `u0`, `pu`:** `sheets_f9d.py <rec> <out> <u|u0|pu> 3840 5850 5950` — 1 кадр/с всего видео (8×6), 4 кадра/с фазы вращения
  (v [3840, 5850)) и неподвижной фазы (v ≥ 5950). Листы пар `cmp_sheets.py` (слева `u0`, справа `u`, один v): фаза вращения и первые 36 клеток
  неподвижной фазы (v [5950, 6490)) — справка для лида.
- **`fs3_u`:** 0 клеток с плитками — член; исполнитель считает все листы фазы вращения и неподвижной фазы и 1 кадр/с.
- **`fs3_u0`:** плитки в неподвижной фазе — член (нужна ≥ 1 клетка); счёт клеток по `static4_01` и последнему листу.
- **`fs3_pu`:** если Астро входит в воду (пруд в кадре, Астро в пруду), клетки с плитками считаются; иначе строка «вход в воду формой ввода не
  достигнут» (ввод по present, темп игры с патчем другой — путь Астро может разойтись [I]).
- **`fs3_v`, `fs3_hb`:** лист лида `sheet142.py` и 1 кадр/с; рядом с принятыми — Sky Garden `C:/kyty/f287/fs2c/sheet_fs2_v.png` (FS2c) и
  `C:/kyty/f287/f9/f9g/runs/f9g_sg/sheet_f9g_sg.png` (F9g); `hoover_beach` — `C:/kyty/s146/sheet_r146_01.png` (с. 146) и
  `C:/kyty/f287/f9/f9g/runs/f9g_hb/sheet_f9g_hb.png` (F9g). Строка «видимых отличий не вижу / вижу: …».
- Таблица счёта: клеток всего / с плитками / «пруда нет» / номера клеток с плитками (v). Лид считает своим листом независимо.

## 6. Строки «читать так» (дословно из пунктов лида)

- Строка лида `417cc2d8`: «рост `applied` в фазе неподвижной камеры показан, только если строка `FixB42Ext … extent=960x540` с present в фазе или после
  неё несёт `applied` больше последней строки до фазы; отсутствие такой строки — `NOT_DETERMINED`, не «не растёт».»
- п. 367(г)(3): «`fs3_u0` … без плиток — один повтор, второй без плиток — стоп и пункт лида»; «справка `fs3_pu` (не гейт) … иначе строка «вход в воду
  формой ввода не достигнут»».
- п. 353(д)(3): `drawn` > 0 у `extent=960x540` — «читать так: T6 получил draw» и вопрос лиду.
- п. 353(д)(3) Н2: «`hit` C0 и V1/V2 не сравнимы: при `=0` растёт на каждом FCE, при `=1` — на заливку».

## 7. Выход по тегу и таблица исходов

По каждому тегу: видео (кадров, записей `.idx`), листы (§5), счёт клеток, `s51_vidglitch.py 4`, строки `FixB42:`/`FixB42Ext:` (§4), маркеры смерти,
кадры ≥ 1 с, удержание, `[Vulkan][E]` (W). Таблица исходов — строками «член: да/нет/нечитаемо» с числами, **без вердикта** (приёмка и установка —
лид, FS3d). Файлы — `C:/kyty/f287/fs3/fs3c/runs/<тег>/` (все теги) и `C:/kyty/f287/fs3/fs3c/{log,stdout,rec}_<тег>.*` (`w`, `v`, `hb`); события —
строки `C:/kyty/f287/fs3/times.txt`, замки — `fs3c/lock.log` (UTC).

## 8. Не заявляется

Что CMASK-очистка — единственная причина Б42 во всех сценах; что на PS5 вода в этих ракурсах чистая (эталона нет); что другие уровни с водой без
дефекта; что `applied` 960×540 растёт в неподвижной фазе, если справка `NOT_DETERMINED`; что путь с `KYTY_GAME_PATCH` проверен (справка `fs3_pu`);
что `SCENE_OK` Sky Garden доказывает воду; ни одно число — не выигрыш; 60 FPS не обещаются; путь установленного `4aa62e95` до FS3d не меняется.

## 9. sha256 файлов печати (до первого тега)

| файл | sha256 |
|---|---|
| `go_fs3.sh` | `f0def39e0e477707449520c4e4ee27bb0c68f6a1b283015eee998bb5a03b58e5` |
| `launch_fs3.sh` | `76f292f17d2485e9bcedfe313b6d6f813e526a0a7a5dfd16aff26607cbdbfcb8` |
| `wait_fs3.sh` | `84625d22dc60d1fd76cee6772c1225e7cca587e16269116d2d80ca6f4e51f91d` |
| `post_fs3.sh` | `5b325068402d79eb57c0ba3273f038943ade8f7f1a7ca7db119d8757b934d6b4` |
| `run_fs3.py` | `ccbe63c4899a7b33707e23b7f74fc2e08f010cbdd79369f2d254ec97e475b7d1` |
| `fs3_read.py` | `55eb53c3296592d093e834a7c76e3e327a8d062b150a79a74548282f6ef608f5` |
| `test_fs3_read.py` | `92fc45e18c4ad5ed53ea6c37f277bd364b3b2d8bd16c8773db81c4d47b557d53` |
| `test_fs3_read.out.txt` | `370bcea08a67dadf79ecaefe7849451704bbd9a528e66347f578f68ce7c8c552` |
| `enter_scene.py` | `030ca42e2f7111ccd81bed9f0be922f33f3d1c3cb60d06b6c8b5c7609b2d689c` |
| `idle142.py` | `c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96` |
| `procload.py` | `d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0` |
| `gates_default.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `sheet142.py` | `c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d` |
| `run_safety99.py` | `77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638` |
| `launch_run.py` | `c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21` |
| `keys_a2_presents.txt` | `6c36daccc41eef7feaae519a2a13edb93f78688cf5f5f4594367ad9b9f646b3f` |
| `sheets_f9d.py` | `b252161e6ca5992fd6b767279b37fc2a782c93be2275a792f11ed8d41f1f12b9` |
| `cmp_sheets.py` | `52144019dc10b65a0d0dca5cf130b1543edd8c4f7803d0a9b81db66846769709` |
| `C:/kyty/f287/bin/kyty_emulator_540c035a.exe` | `540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1` |
| `C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe` | `4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac` |
| `C:/kyty/KytyPS5/patches/PPSA21564_pvar.txt` | `a204549cc3e51f50efb6f484f65db73fa430e7d3c81ad9ede2460fcda01d0b1a` |
| `C:/kyty/scripts/s51_vidglitch.py` | `6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c` |

Фикстуры: `test_fs3_read.out.txt` — первая строка `suite test_fs3_read.py sha256 … target fs3_read.py sha256 …`, `checks 92`, `ALL OK`
(регрессия на реальном логе `f9g_v1` F9g: sha, 1 177 398 строк, 272 строки `FixB42:`, 0 `FixB42Ext:`, сдвиг 30, последний present 10 016, `.idx` 10 014).
Строка вызова: `bash C:/kyty/f287/fs3/fs3c/launch_fs3.sh <тег>` (вызывает `bash C:/kyty/f287/fs3/fs3c/go_fs3.sh <тег>`).
