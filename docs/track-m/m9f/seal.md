# M9f (трек M, `HPP-871`): печать серии 1 T188 — теги `t188_sg2`, `t188_hb2`, `t188_mg2` — до первого тега

Звено Harness Engineer. Основание — `ROADMAP.md` п. 785(в)(3), (в)(5) (KytyPS5 `a73c2cb7`), правило исхода — §7 издания 2
`docs/track-m/m9a2/design_m9a2.md` с п. 785(б)(5); T109 — п. 785(г) с поправками п. 788(в), (г), 789(г), (д), 791(в); бинарь —
п. 791(д). Печать закрывается до первого тега; после неё не меняются ни харнесс, ни ридер, ни правила T188. Вердикта по T188 и T109
здесь нет: чтение — звено M9g (`HPP-872`, лид). Пометки: [c] — проверено кодом или данными, [I] — вывод, [U] — неизвестно.

## 1. Бинари и установленное состояние

| Что | Значение |
|---|---|
| Бинарь тегов (M9d3, принят M9e3, п. 791(а), (д)) | `C:/kyty/m657/bin/kyty_emulator_feb55b54.exe`, sha256 `feb55b549e26fc6dfd2a03f08997446106cc8bba6bb7e8c31449e7991a737a2c`; код `main` `2042c697` (= worktree `067dfd93` на M9d2 `3f5d8725`, база M6a3 `3d227024`); не установлен |
| Опознание бинаря | **только по полю `binary_sha256`** json тега (п. 789(д) Н4, 791(г) Н3): в копии две строки версии, строка версии не опознаёт. `751bfa7f` и `662896a2` в серию не идут — допуск ридера отвергает любой другой sha |
| Установленный бинарь | MS1 `ea35b679b0bcfe83767093204f348b189384cab1a7b273f89b164b64cba4d4df` = `ps5 em/kyty_emulator.exe` на момент печати [c]; закреплённая копия `C:/kyty/m657/bin/kyty_emulator_ea35b679.exe` |
| Подпись и каталог при умолчаниях | `8dcf31779bbcb7c6e605653a138dae162f645a46`, `variant_fixb26_fixb1b_fixf10_fixf19_mw1_33` (набор подписи не тронут, п. 791(а)); каталога `_mw1_33` в кэшах пользователя нет [c на момент печати] — вход каждого тега холоден по трансляции [I], как у тегов M6c |

Бинарь тегов ставится только на время тега; после каждого тега возвращается MS1 из закреплённой копии со сверкой sha256. Бинарь не
пересобирается между тегами и чтением.

## 2. Теги (по одной попытке)

| Тег | Уровень | Форма | Порог детектора `max(2·M_b, 200)` (п. 785(в)(3), §6.1) | Тег M6c для пар листов |
|---|---|---|---|---|
| `t188_sg2` | Sky Garden (`underwater_aerial_garden`) | V | 338 (`M_b` 169) | `m6_sg` |
| `t188_hb2` | `hoover_beach` | V | 648 (`M_b` 324) | `m6_hb` |
| `t188_mg2` | `mini_giants_garden` | V | 246 (`M_b` 123) | `m6_mg` |

Порядок — `t188_sg2`, `t188_hb2`, `t188_mg2`. Повтор `<тег>_r1..3` — только при помехе прогона: событие окна (`minimized`,
`Recovering Vulkan swapchain`) — помеха и повтор тега (форма V M6c); перед повтором строка `times.txt` с причиной, затем
`M9F_REPEAT_OK=1`. Иная помеха (процесс пользователя, дисплей, `nostart`, процесс хоста `BUSY`) — повтор тем же правилом, причина в строке.

## 3. Форма V и ручки

- `--stable-draws 300 --timeout 480`, удержание — опция 330 с (член «≥ 300 с после первого кадра сцены»), видео (`KYTY_REC`), без
  валидации (`--vulkan-validation false`, `--shader-validation false`), без `--rd`, вход `-lvl <уровень>`; выход — `WM_CLOSE` в конце
  удержания (форма V M6c).
- Переменные — позиционно в `enter_scene.py`: `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_DIAG_M5W2=1 KYTY_DIAG_T188=2` и
  постоянные `enter_scene.py` (`KYTY_FRAME_TRACE=lite`, `KYTY_GPU_HANG_ABORT_S=8`, файлы шлюза, `KYTY_QUEUE_TRACE=1`,
  `KYTY_GUEST_ARGS`); `KYTY_*`/`VK_LAYER_*` оболочки снимаются. **`KYTY_DIAG_T188_CLS` не задаётся** (пусто = все классы): её
  наличие в env тега — член допуска «env = форма точно» (лишняя переменная ⇒ `NOT_ADMITTED`). Без `KYTY_FIX_*`, `KYTY_S_*`,
  `KYTY_TEST_*`, `KYTY_M_*`, `KYTY_GAME_PATCH`, `KYTY_GPU_CHECKPOINTS`.

## 4. Допуск и члены формы V (ридер `m9f_read.py` = порт `m6c_read.py`)

- **Допуск** (провал — тег не читается): json тега; `binary_sha256` = `feb55b54…` (единственное опознание); установленный во время тега
  = `feb55b54…`; установленный до и после = MS1; `prereg` = sha256 этой печати; план харнесса = план ридера; env = форма точно;
  0 `KYTY_TEST_*`; 0 `ExitFatal:`; флаги; `-lvl` и уровень харнесса; опция удержания 330; лог и stdout; вход `ok` и строка входа;
  0 `minimized` и `Recovering Vulkan swapchain`; подпись `8dcf3177…` и каталог `_mw1_33`; 0 `GamePatch:`, `DiagB32`, `TestLogStall`,
  `TestHidLoss`; ровно одна строка `M5W2: mode=1`; **ровно одна строка `T188: mode=2 cls=all k=4`**; `manifest cmp EQUAL`; строка
  `LogAsync: full_waits=` ровно одна.
- **Члены формы V — строки, не вердикт** (как M6c): удержание ≥ 300 с после первого кадра сцены; процесс жил; 0 маркеров смерти и
  строк `device lost`; 0 кадров ≥ 1 с после первого кадра сцены; видео ≥ 3 000 записей; одно-кадровые глитчи (при `=2` окраска может
  их давать — строка, не стоп); лист; `Event: quit` и 0 `Fatal` после; конец до таймаута харнесса; `MWave1: mask=0x33`, `MT265/272/231:
  mode=1`; ≥ 1 строка `M5W2Stat:`.
- **Темп сцены** (`tempo_m9f.py` = `tempo_fs15c.py`, п. 620(ж)(2), 621): не `PASS` ⇒ `SERIES_STOP`, вопрос лиду (форма M6c).

## 5. T188 и T109: стоп-члены и строки (`t188_rules.py`)

Строки кода `feb55b54` (`src/libs/diagT188.cpp`, `main` `2042c697`): `T188: mode= cls= k=` (раз на процесс); `T188Stat: when=<periodic|exit>`
+ 70 полей в порядке `kNames`; `T188Img: when=exit key=<16 hex> fmt= tile= w= h= levels= layers= cmp= samples= usage= vol=` + 27 полей
`kClassNames` (до 256 строк и `key=other` — сумма остальных); `T109Stat: when= d32= zx_d32= zx_narrow= bias_d32= bias_narrow= ovr_w=
ovr_vpc= zx_narrow_vi= bias_narrow_vi= narrow_cd=`. Порядок полей зашит в набор `test_t188.py` отдельно от ридера.

**Стоп-члены (нарушение — помеха кода, `SERIES_STOP`, правка звена кода; §7(1) издания 2, п. 785(в)(5)):**
- **N**: ровно одна строка `T188: mode=2 cls=all k=4`, 0 неразобранных; `cls=all` ⇒ `tint_skip_cls = 0` (И7).
- **E**: ровно одна `T188Stat: when=exit`, ровно одна `T109Stat: when=exit`; ≥ 1 строка `T188Img` и все `when=exit`, `key=other` не
  больше одной; 0 неразобранных строк четырёх префиксов.
- **Z**: на **каждой** строке `T188Stat` (`periodic` и `exit`) `part_unk = ep_bad = lock_bad = tint_bad = tint_rb0_bad = tint_rb1_bad = 0`.
- **И1–И4, И6, И8** на строке `exit` (§4.6): И1 `part = part_st + part_fill + part_copy + part_unk`, `part_unk = 0`; И2a `part =
  part_synced + part_dlmem + reopen + ep_new`; И2b `ep_new + ep_prop = Σ cl_*` (15 мест, без `cl_none`) `+ open`; И2c `ep_pend =
  pend_done + pend_drop + pend_free + pend_open`; И2d `ep_pend ≤ cl_smp + … + cl_vo`; И3 — каждое из 27 полей класса, суммированное по
  строкам `T188Img` и `key=other`, = глобальному (`ev`↔`part`, `ev_*`↔`part_*`, `tint_skip`↔ сумма пяти `tint_skip_*`, остальные — по
  имени); И4 `part = w_mipal + w_inmip + w_other`, `part_off ≤ part`, `w_bytes ≤ img_bytes`, `img_bytes_unsync ≤ img_bytes`,
  `in_pass_unsync ≤ in_pass ≤ part`; И6 `tint_ep ≤ (cl_smp + … + cl_vo) + pend_done`, `tint_bad = 0`, по каждой строке `T188Img`
  `tint_bytes ≤ lost_bytes + lost_pend_bytes`, `tint_rb_req = rb0_ok + rb0_bad + rb0_none + rb0_nofmt`, `tint_rb0_ok = rb1_ok +
  rb1_over + rb1_bad + rb1_none`, `rb0_bad = rb1_bad = 0`, `tint_rb_req ≤ K × (классов с tint_ep ≥ 1)` (`K` из строки режима; у
  `key=other` число классов оценивается сверху его `tint_ep` — вариант исполнителя: число классов внутри `other` не напечатано);
  И8 `ep_bad = lock_bad = 0`.
- **И5** (проводка, `KYTY_DIAG_M5W2=1`): итог `M5W2Stat` тега (последняя строка с наибольшим `pushes`, форма M6c) — строка
  `when=exit`; `part = inv_part_src`; `part_off = inv_off`, если `inv_part = inv_part_src`. Строки `M5W2Stat: exit` и `T188Stat: exit`
  печатаются подряд одним путём выхода (`emulator.cpp`, вызовы 495–496) [c]; расхождение — стоп по букве, вопрос лиду.
- **И9** на строке `T109Stat: exit`: `zx_narrow ≤ zx_d32 ≤ d32`; `bias_narrow ≤ bias_d32 ≤ d32`; `ovr_vpc ≤ ovr_w`. Отношения полей `_vi`
  (`zx_narrow_vi ≤ zx_narrow`, `bias_narrow_vi ≤ bias_narrow`, `narrow_cd ≤ zx_narrow_vi + bias_narrow_vi`) — справка, не стоп
  (вариант исполнителя: §8.3 их не называет; разрыв снимка п. 791(б) мог бы дать ложное нарушение).
- Стоп вычисляется у допущенного тега; нарушение Z — и у недопущенного (помеха кода не зависит от допуска). Тег без лога или без
  строки `exit` при допуске — стоп по члену E.

**Строки для M9g (не стоп, не вердикт):** поля строки `exit`; `open` — только при `ep_bad = 0` (п. 788(г) Н2), иначе «не читается»;
таблица `T188Img` (ключ, `lost + lost_pend`, `tint_bytes`, `tint_ep`, покрытие `tint_bytes / (lost + lost_pend)` против 0,5,
`rb0_ok`, чтение обратно живо ⇔ `tint_rb0_ok(c) ≥ 1` и глобально `rb0_bad = rb1_bad = 0`; `key=other` классом не служит);
**выбор классов п. 785(в)(2)** — строки `T188Img` тега `=2` без `key=other` по убыванию `lost_bytes + lost_pend_bytes` (при равенстве —
больший `ev`, затем ключ), пока сумма не достигнет 0,8 от `lost_bytes + lost_pend_bytes` строки `exit` (сумма сцены = сумма строк и
`other` по И3), не больше 2 классов; строка с 0 байт выбор заканчивает; остаток — «не определено»; классы печатаются только для сцен с
детектором < 3 кадров (теги `=3`, не больше 6 всего); `=2(c)` по п. 785(б)(5) — только после чтения пары листов лидом.
**T109 (п. 785(г), 789(г), 791(в)):** строки всех `T109Stat` по порядку лога; разность `zx_narrow − zx_narrow_vi` и `bias_narrow −
bias_narrow_vi` по строкам; часть `zx` засчитывается по п. 791(в) только если разность ≥ 1 в некоторой строке `periodic` и во всех
следующих строках тега, включая `exit` (одна строка `exit` или разность впервые в `exit` — «не засчитывается»); флаг п. 789(г)(3)
«`zx_narrow ≥ 1` и `zx_narrow = zx_narrow_vi` на строке `exit`»; `d32 ≥ 1`, `zx_d32 ≥ 1`, `ovr_vpc ≥ 1`, `bias_d32 ≥ 1`, И9.
Член (г)(1) «стенд T109 `ALL OK` с пойманными t1–t9 на коде M9d3» — по отзыву M9e3 (`docs/track-m/m9e3/review.md`, п. 791(а)), не
мерится этой серией.

## 6. Детектор и листы (`nmag_m9f.py`; п. 785(в)(3), §6, §7(2)–(3))

- `N_mag` записи = число пикселей R ≥ 200, G ≤ 60, B ≥ 200 после декодирования видео тега в rgb24 960 × 540 (форма `mb_kd_m9a2.py`).
- Окно — записи видео с номером показа (2-й столбец `.idx`) ≥ `first_scene_n` ридера; `w0` — первая запись окна; смещение записи =
  запись − `w0`.
- Запись отмечена при `N_mag >` порога сцены (338 / 648 / 246); строка детектора — число отмеченных и «≥ 3» (строка, читает M9g с
  листом).
- Лист `sheet_top.png` — до 12 записей окна с наибольшим `N_mag` (при равенстве — более ранняя). Пары листов `pairs_top_<k>.png` —
  кадр тега слева, кадр M6c справа на записи `w0_M6c + смещение` (те же номера кадров видео от первого кадра сцены); смещение за окном
  M6c — «нет пары». **Вариант исполнителя:** `pairs_even_<k>.png` — 12 смещений равным шагом по окну (у тега без отмеченных записей
  топ-12 — произвольные кадры с `N_mag ≈ 0`).
- Видео M6c — `C:/kyty/m657/m6c/rec_m6_<s>.mp4` и `runs/m6_<s>/read.json` (`first_scene_n` 355 / 268 / 270).

## 7. Кэши

Набор: `_ShaderCache`, `_ShaderSeeds`, `_PipelineCache`, `_SaveData` папки эмулятора и `GLCache` драйвера. Каждый тег — на живых кэшах
пользователя (K0): копия до прогона и манифест sha256 (`runs/<тег>/manifest_before.tsv`), прогон, манифест состояния прогона, возврат
копии, манифест после; член допуска — `manifest cmp EQUAL`. Тег с процессом пользователя или ВМ — возврат после их выхода (форма M6c).

## 8. Процесс, очередь и бюджет

- Вызов: `chk_m9f.sh <тег>` (стоп, замок, новые комментарии `HPP-871`, очередь — строка `times.txt`) → `launch_m9f.sh <тег>` (только
  запуск) → `wait_m9f.sh <тег>` (≤ 540 с на вызов, до строки `rc=`) → `post_m9f.sh <тег>` вне замка (глитчи, лист, ридер, детектор,
  ридер, таблица, темп). Каждый вызов `go_m9f.sh` — один замок `C:/kyty/SEALED_RUN.lock` (строки `lock taken|released` в
  `runs/lock.log`); одна проверка сторожа и сессии — сразу после взятия замка, до манифеста (форма п. 634 / 660 / 661). Окна между
  тегами нет.
- **Очередь замка** (`queue_m9f.py`): `QUEUE BUSY`, если готово звено трека P (п. 322(г)) или **M3a2 `HPP-861`** (статус `todo` /
  `in_progress` или идущий прогон) — при одновременной готовности M3a2/M3b2 идут впереди T188 (п. 785(в)(5)); M3b2 `HPP-862` (лид, без
  замка) — строка справки.
- Стоп серии: `C:/kyty/m657/STOP`, `SERIES_STOP` (стоп-член T188, темп, `device lost`), `RETURN_FAILED`.
- **Бюджет замка ≤ 60 мин на три тега** (п. 785(в)(5)); оценка [I] ≈ 12–15 мин замка на тег (M6c: три тега 06:59–07:45 по `lock.log`).
  Сумма замка по `runs/lock.log` печатается в отчёте; превышение — строка отчёта и вопрос лиду.
- ГП-кейсы `dl_cases.txt` не запускаются, сборок нет (п. 760). После серии: таблица по тегам (`table.txt`), листы, пары листов,
  выбор классов для серии 2 — без вердикта (чтение — M9g).

## 9. Инструменты (sha256 на момент печати)

| Файл | sha256 |
|---|---|
| `go_m9f.sh` | `2686bcf810973844fc4238821eb24f06cecbc6ac68b7777d5b7ffca5e6df661f` |
| `launch_m9f.sh` | `2779f9a5d98548d207ef22f6fbd74a7f5625c8d8fd18f8249410a6c3cec5a22f` |
| `wait_m9f.sh` | `22e265b41202deb2710be1306072703a2a0848ab15550ec432eb6ede315b1457` |
| `chk_m9f.sh` | `576400c496febf74f72ddc02ed774f71aa7ffb0add21b393383798b1f92c2407` |
| `post_m9f.sh` | `55744f2e80bb8ba08378feb900b318656539973e0fb7f5000efa2b3ec8386fdc` |
| `m9f_read.py` | `5f72413d53fc4f436f57b11cb1548fd632cf7953dad4b30304d909892dc64414` |
| `t188_rules.py` | `78f135a6e8fa0ab526d3c69ec8284897cee9501002390ecc56b4bc77c8a6fde6` |
| `nmag_m9f.py` | `983763920e5fa0469ab873fd6556cfcec6fe6d1e83a72149f2635ea877cc529c` |
| `queue_m9f.py` | `beec87d157e83d0ae4ab1a891d05ad310849d41643449d8daf88ea5490928573` |
| `test_m9f.py` | `c060f46b6c33318f402e5fabf0ce38ca66395e15862b6ecb587fe6b3709b5196` |
| `test_t188.py` | `d72728e8fa7b88b3298e845afa62d5c267535f7c490fea057bf296101ddea890` |
| `mut_t188.py` | `c8319267264ae6508657c891961e6bc99658cb6e8ce4169160929d05af85c655` |
| `gen_m9f.py` | `60ce6638d87cc60d984768a7a0d489339a194f1c00299d7d9262f677a0e23a6f` |
| `enter_scene.py` | `51be0bfb520ee885846bd76fa4aa3635c2f3c3354769dd5e629fb0e8b43c05da` |
| `procload.py` | `4c2ad75cd44b79da93084bdf8fb9ab17db91b18dd37f6b4483eb3bd99b1fa058` |
| `dispstate.py` | `8869a89697cc3ed99801241445b8e570b24eb904865be4aad4ff40e47131df6e` |
| `idle142.py` | `2ce187ce44baeff618ed290a435bbc92bd412eb0654dd7eb387c042f2a5aa495` |
| `launch_run.py` | `2f0a8aa452a9ee017ac72be5ebe11816a6d4ce7e0151aaaaa41d2c8a0088de2d` |
| `run_safety99.py` | `d2210369bdcc7d47ea2a44fdd494979678c50a3002814103e531df22b5480623` |
| `sheet142.py` | `99ef62f26f4aa546147541b812e8e723ac605feb57901ab6366d8abeab73230f` |
| `gates_default.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `gates.req` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `sample.req` | `5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9` |
| `manifest_fs4c.py` | `239ad96485f171b78a0f83afefc5005b45cc7e31743f10afa57f6b23cbd909e8` |
| `guard_m9f.py` | `99306553090d08c3ece1dacf384e688d9b8b8455effee3f597901ecb008a5596` |
| `hold_m9f.py` | `d322eb5a37a56aef3d7c3b8e9ab66fcab5eaf8410aeb3c009580008dae74a5b7` |
| `hostload_m9f.py` | `54e484fc456257a445b5266e1fbe293ef8f78da065d3702a803db3ffd67595e1` |
| `snap_m9f.py` | `77edc830c807a94cbc41bc62c3fd8a05693fa3db039ad11e58500f56097775fb` |
| `mfsub_m9f.py` | `611f54ad4037e21bb8d195e78e55194257c60948329c96eea8dd93793c72dc26` |
| `runchk_m9f.py` | `cfdb559f6e7f75659bad7756c9d4703e4f80746a8fe92c3a216c95328d944dd8` |
| `tempo_m9f.py` | `50d84ad3bb8594d510a23643dbafc49e990aa06d84971dfb690c0318021f0c60` |
| `watch_m9f.py` | `2484b2ca63a4ba3169731010741abe0bb5e3e6ea115c9305cde2e263b376ad7e` |
| `C:/kyty/m657/m6c/m6c_read.py` | `e2a27aa916bb378c7c61e5a3f0eecb59d0e4acd51cdd6e29450ba9d6d9cb1f06` |
| `C:/kyty/f287/fs15c/fs15c_read.py` | `9ef2975702ce8d3b94afdd9c0f3d9198a743711721fa570ac816acb70bb79cf2` |
| `C:/kyty/KytyPS5/ps5 em/docs/form634_check.py` | `f100a063fbc0063266a6443bac9b68f17e832fddd29456ccb475e7b1e76a4ded` |
| `C:/kyty/scripts/s51_vidglitch.py` | `6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c` |
| `C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py` | `db82ef4bcf05ddea365f50c403029bfc5d2a7a4400a12d254a6b0cc6ab3e6dde` |
| `C:/kyty/m657/bin/kyty_emulator_feb55b54.exe` | `feb55b549e26fc6dfd2a03f08997446106cc8bba6bb7e8c31449e7991a737a2c` |
| `C:/kyty/m657/bin/kyty_emulator_ea35b679.exe` | `ea35b679b0bcfe83767093204f348b189384cab1a7b273f89b164b64cba4d4df` |
| `C:/kyty/m657/m6c/rec_m6_sg.mp4` | `6a0b797f0d7c84d214d29b3efa3dd413986f402d33294666cfb2ae80d9831d62` |
| `C:/kyty/m657/m6c/rec_m6_hb.mp4` | `a26096fb6f69bf60959fb696e358b46888a3847262309d42404927909cd9b6e2` |
| `C:/kyty/m657/m6c/rec_m6_mg.mp4` | `4f5b8bc7a28b33d042372c822e10aaf6bea37f10ce602e665135321731fbe7aa` |
| `C:/kyty/m657/m6c/runs/m6_sg/read.json` | `9f69b05866232e26bf613b784639a72346059d80762ccf9eab31caf1b0bcc876` |
| `C:/kyty/m657/m6c/runs/m6_hb/read.json` | `7fbb85472885c797a93a4d589bbbf05b050ea384e12d03e904a4c2bb97f8484b` |
| `C:/kyty/m657/m6c/runs/m6_mg/read.json` | `02819aaefce6338175e4f85cbd4ec4898037e87ea10adfbaf11c30b109a40f83` |

Копии помощников M6c — `gen_m9f.py` (`gen_m9f.out.txt` sha256 `d627826b33e13ee9`, `ALL OK`): имена перенесены механически (m6c → m9f, `HPP-850` →
`HPP-871`), смысл не меняется. Новые файлы: `go_m9f.sh`, `launch_m9f.sh`, `post_m9f.sh` (порты M6c), `queue_m9f.py` (очередь с M3a2
впереди), `t188_rules.py` (стоп-члены и строки T188/T109), `m9f_read.py` (порт `m6c_read.py` + слой T188), `nmag_m9f.py` (детектор и листы).

- **Набор правил** `test_t188.py` (форма `mutlib`: `ok = True`, `ok &= case(...)`, без подпроцессов) → `test_t188.out.txt` sha256
  `12e45993f263697319a0ed663e92bfcd50339a62bfd2de9e7b501c590d9c1bc4`, первая строка `suite … target …`, последние `cases 118` / `ALL OK`.
- **Набор харнесса** `test_m9f.py` (часть 1 — `test_t188.py` подпроцессом; ридер, детектор на синтетическом видео с краем порога
  18×18 = 324 / 19×19 = 361 при 338, пары на смещении, очередь, план `go_m9f.sh`, допуск на настоящем теге M6c `m6_hb`, вывод в строгом
  cp1250) → `test_m9f.out.txt` sha256 `35fa8f3073283df85ad7bde0f05f451bf2757277996363c460f802b2685c5f12`, последние `checks 49, failed 0 []` / `ALL OK`.
- **Мутанты** `mut_t188.py` — `mutlib` v4.1, один зачётный ПОЛНЫЙ прогон `--control --no-memo --workers 8 --work-dir
  C:/kyty/m657/m9f/mutwork --cache-dir C:/kyty/m657/m9f/mutcache` → `mut_t188.txt` sha256 `5742747169ad006ed8c089841ea36076c08b951d8e8ec4f75c05a62798d8b108`: `87 mutants: 87 killed (2 by a crash of the suite), 0 survived, 0 unresolved (timeout / harness error / environment / not reproduced); 0 confirmed by a rerun in a fresh process, 0 rerun without the memo, 0 rerun alone, 0 rerun isolated (they touched the shared fixtures)`; `controls: 3 of 3 survived`; `wall 22.4 s, worker time 6.0 s, 8 workers`. Прогноз стены до
  запуска — 1,4 с + базовая линия (набор 0,10 с × 87 / 8 × 1,3); первый вызов отказан `mutlib` до заданий (нет `BASE = Path(...)` в
  наборе) — не прогон, строка `times.txt`. Эквивалентные и недостижимые — в заголовке `mut_t188.py` (доказательства (1)–(4)).
- **Линтер формы** `form634_check.py --series C:/kyty/m657/m9f` → `ALL OK` (`form634_series.out.txt` sha256 `2acbfcd779dbf6cf`); `--text` этой печати →
  `form634_text.out.txt` (после записи печати, член отчёта).

## 10. Не заявляется

Что T188 даёт видимый дефект или `НЕ ДЕФЕКТ`; что три сцены покрывают игру; что окраска, чтение обратно или детектор видят любую потерю
(окраска меньше порога §6.2 мерой не видна); что отличие листа без пары прогонов — дефект; что T109 расходится с консолью; что `zx_narrow`
равен суженному клэмпу на ГП; частота разрыва снимка T109 в игре; что холодный вход по трансляции не меняет картинку против M6c (оба
холодны [I]); ни одно число — не выигрыш; 60 FPS не обещаются.
