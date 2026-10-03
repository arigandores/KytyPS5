# F9f3 (`HPP-437`, Red Team): код-ревью F9e2c `KYTY_FIX_B42` (M2c, взведённость `CMask` по битам слоёв вида)

**Вердикт: PASS** — RC нет. Буква п. 357(г)(1)–(4) выполнена [c]. Член взведённости повторяет условие очистки `PrepareCmaskClear`:
те же биты вида, те же границы; стоит до развилки `hit`/`drawn`. Своя модель: 336 200 пар (вид, маска) — 0 расхождений «взведена ⇔ очистка
снимет ≥ 1 бит»; S1–S4 по букве (г)(3); 20 000 случайных последовательностей — 0 нарушений инвариантов. RC1 отзыва `4256e8cf` закрыт (S1:
`hit=1 applied=1 rearm=0`). RC1 отзыва `dcd762d6` по-прежнему закрыт (S4: `hit=0 drawn=1`). Путь `=0` = `4414e235` по значениям [c по коду].
Сборка из чистого worktree подтверждена, sha256 `24efead3…0061`. Свой прогон `shader_cfg_tests`: 127 тестов, 1 падающий (Б11), rc 0, лог байт
в байт = P23. Три замечания без RC (Н1–Н3) — для печати F9g.

Решение — `ca38fdb5:docs/ROADMAP.md:19468` п. 357 (якорь «357. **Звено F9f2 трека F (`HPP-430`, Red Team) принято»; +1 — «взведена» п. 353(г)(2)
читается по битам слоёв вида цели, а не по всей маске»), подпункты (г)(1)–(4), (е); п. 353(г) в остальном. Вход — отчёт
`6fde3ad5:docs/track-f/f9e2c.md`, код `0b9dc0c9` (`main`), `722c5e7f` (worktree `C:/kyty/f287/f9/f9e2c/wt`). Чтение начато 02:36:41Z (после
`ca38fdb5` и `6fde3ad5`). Игра не запускалась; установленный бинарь `4aa62e95` и кэши не тронуты. Время — UTC по `date -u`, события —
`C:/kyty/f287/f9/times.txt`. Два чужих замка трека P (`gop31.sh hv_2`, `gop31.sh hn_sponge_dirty_bath`): под ними ничего не запускалось и не
писалось, строки есть в `times.txt`. Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно.

## Чек-лист

| # | Пункт | Итог |
|---|---|---|
| 1 | (г)(1) `armed` = `PendingDcc` или `CMask` с `(clear_mask & layer_bits) != 0`; `layer_bits` — биты `[base_layer, base_layer + layer_count)` вида `color.desc.view_info` того `desc`, что уходит в `FindRenderTarget` ветки FCE | ✓ [c]: `0b9dc0c9:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3672–3677`. `view` — `color.desc.view_info` (`:3672`). Тот же `color.desc` уходит в `FindRenderTarget` (`:3766–3767`); между пробой (`:3752`) и вызовом меняется только `desc.info.metadata` (`:3754–3756`). Внутри `FindRenderTarget` `desc` идёт без изменений в `PrepareCmaskClear(id, desc)` (`2da00d80:src/graphics/host_gpu/renderer/cache/textureCache.cpp:2421`; `textureCache.cpp` в F9e2c не менялся — `cmp` с `0b9dc0c9` ✓). `PrepareDccClear` (`:2420`) при `kind = Cmask` выходит сразу (`:1869–1870`), запись не трогает |
| 2 | Граница: при `base_level != 0`, `base_layer >= 32`, `layer_count > 32 - base_layer` запись `CMask` не взведена | ✓ [c]: `view_ok` (`descriptors.cpp:3673`) — отрицание условия `textureCache.cpp:2008` дословно. Поля `uint32_t` (`0b9dc0c9:src/graphics/host_gpu/renderer/image/imageInfo.h:159–166`), арифметика `32 - base_layer` в обоих местах одинаковая и вычисляется только при `base_layer < 32`. Сдвиг без UB: ветка `layer_count >= 32` при `view_ok` возможна только с `base_layer == 0`; приоритет `?:` ниже `<<` — сдвиг применяется к ветке «иначе» целиком. Модель, часть 1 (своя, уровни {0, 1, 2, `0xffffffff`} × `base_layer`, `layer_count` ∈ 0..35, 63, 64, `0x7fffffff`, `0xfffffffe`, `0xffffffff` × 50 масок): «проба взведена (половина `CMask`)» ⇔ «цикл `:2009–2013` снимет ≥ 1 бит» — 336 200 случаев, 0 расхождений |
| 3 | Член стоит до развилки `hit`/`drawn` — `drawn` его тоже требует | ✓ [c]: `armed` входит в ворота `:3678`, развилка — `:3683–3686`. Модель S3 (заливка → FCE → draw → FCE) — `drawn=0` |
| 4 | `rearm` — `hit` с записью `CMask` (как F9e2b) | ✓ [c]: `probe.rearm = fill.cmask` (`:3688`) только в ветке `Hit` |
| 5 | (г)(2) `applied`, строка, частота, счётчики по экстенту, `hit_all` — без изменений | ✓ [c]: `git diff 2da00d80 0b9dc0c9 -- src` — только `descriptors.cpp` (заголовочный комментарий `:3637–3639` и `:3670–3677`); `applied` `:3777–3780`, `FixB42Note` `:3695–3732` не задеты |
| 6 | (г)(3) модель S1–S4 по строкам нового кода, вывод кончается `ALL OK` | ✓: модель автора `docs/track-f/f9e2c/model_rearm.py` — свой прогон, `ALL OK`. Своя модель `docs/track-f/f9f3/model_f9f3.py` написана независимо, по строкам `0b9dc0c9`/`2da00d80`: S1 `hit=1 applied=1 rearm=0`; S2 `hit=2 applied=2 rearm=1`; S3 `hit=1 applied=1 drawn=0`; S4 `hit=0 drawn=1`; сверх буквы — X1 (draw до заливки ⇒ `hit`), X2 (повторная заливка ненулевым значением ⇒ не взведена), X3 (два FCE на каждую из двух заливок ⇒ `hit=2 applied=2 rearm=1`); `=0` S1 ⇒ `hit=4` (п. 353(д) Н2). Инварианты на 20 000 случайных последовательностях (`=1`, вид T6): I1 — каждый `hit` с `applied`; I2 — `hit` ≤ числа нулевых заливок, `rearm` ≤ их числа − 1; I3 — `drawn` только при неистраченной нулевой заливке. Нарушений 0, вывод `ALL OK`, rc 0 |
| 7 | (г)(4) файлы: правка только `descriptors.cpp` | ✓ [c]: `git diff --stat 0cbaa644 722c5e7f` — 1 файл, 11+/2−; `git diff --stat 4414e235 722c5e7f` — три файла F9e2/F9e2b/F9e2c (`textureCache.cpp`, `textureCache.h`, `descriptors.cpp`) |
| 8 | Нового состояния нет | ✓ [c]: `view`, `view_ok`, `layer_bits` — локальные константы; только чтение `color.desc.view_info` |
| 9 | Путь `=0` = `4414e235` по значениям (кроме строки и `b42_*`) | ✓ [c по коду]: член меняет только `FixB42Kind`. При `=0` `kind` читают `:3753` (нужно `FixB42Enabled()`, ложь), `:3777` (то же) и `:3775`/`:3782` (только `FixB42Note` — счётчики и строка). `color.desc`, вызов `FindRenderTarget`, команды Vulkan и состояние кэша — как у F9e2b; у F9e2b они = `4414e235` (п. 9 отзыва F9f2, принят п. 357(а)) |
| 10 | RC1 отзыва `4256e8cf` | Закрыт [c]: S1 — FCE₂–₄ после очистки дают `none` (маска `0xfffffffe` & бит 0 = 0); инвариант I1 на 20 000 последовательностях |
| 11 | RC1 отзыва `dcd762d6` | Закрыт [c]: S4 `hit=0 drawn=1`; штамп draw и развилка не менялись |
| 12 | Сборка из чистого worktree на `4414e235` + F9e2 + F9e2b + F9e2c, sha256 | ✓ [c]: worktree `HEAD` `722c5e7f` → `64de099c` → `7662bb28` → `4414e235`; дерево `7662bb28` = `23a0b3f2` (F9e2), `64de099c` = `0cbaa644` (F9e2b) — `git diff --quiet` ✓; `src/graphics` worktree = `main` `0b9dc0c9`; `git status --porcelain` 0 строк; CR в `src/` 0 из 456; `CMakeCache.txt` — `Kyty_SOURCE_DIR=C:/kyty/f287/f9/f9e2c/wt`, `Release`; `KYTY_GIT_REVISION` = `722c5e7f…`. Самый новый файл `wt/src` — `descriptors.cpp`, 02:01:33Z. `descriptors.cpp.obj` и `textureCache.cpp.obj` — 02:03:14Z, exe — 02:06:57Z. sha256 `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe` = `C:/kyty/f287/f9/bin/kyty_emulator_24efead3.exe` = **`24efead326a6ddfd8b24b05549228fa165a1876a2c5adf58e2354b9d77270061`**. В exe `FixB42: mode=`, `KYTY_FIX_B42`, `drawn=%`, `56189185f9e9f9a0ea5174f3f85206e6d099db3d` — по 1. Подпись трансляции не меняется: `git diff --quiet 4414e235 722c5e7f -- src/graphics/shader` ✓ |
| 13 | Свой прогон `shader_cfg_tests` | ✓: `C:/kyty/f287/f9/f9e2c/build/shader_cfg_tests.exe`; все `KYTY_*` сняты, кроме `KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1`. rc 0, 127 `[test]`; падения — `pixel IMAGE_SAMPLE_C must use OpImageSampleDrefImplicitLod` и `pixel IMAGE_SAMPLE_C_LZ must use explicit dref lod` (Б11, один тест). Лог `C:/kyty/f287/f9/f9f3/cfgtests_f9f3.log`, sha256 `5a60758aab7abd57…` = `C:/kyty/p283/p23/cfgtests_defaults.log` (`cmp` ✓); копия в git — с окончаниями LF |
| 14 | Игра не запускалась; правило 24 | ✓: процессов игры нет; ссылки — с коммитом |

## Замечания (не RC; для печати F9g, решение — лида)

- **Н1 (буква (г)(1)).** Запись `PendingDcc` взведена без битов вида (как F9e2b). Сценарий: при виде вне ворот `:2008` (например,
  `base_layer = 32`) FCE даёт `hit`, `PrepareCmaskClear` переводит запись в `CMask` (`:1985–1992`) и ничего не очищает. Итог — один `hit` без
  `applied` (модель, строка `note`); следующий FCE уже не взведён. На T6 [I] не наступает: у цели `layers=1`, вид FCE `0/0/1` взят из
  модели автора и не проверен логом. Если в строке `extent=960x540` F9g рост `hit` больше роста `applied` — сначала проверить вид, потом читать
  член п. 353(д)(1).
- **Н2 (вне «тех же битов и границ»).** Другие выходы `PrepareCmaskClear` без очистки дают `hit` без `applied` при `=1`, как и в F9e2b:
  `KYTY_CMASK_CLEAR=0` (`textureCache.cpp:1961–1964`), отказ `DecodePackedColorClear` (`:2005–2006`), сброс устаревшей заливки
  `PendingDccFillStale` (`:1988–1990`). Печать F9g не должна ставить `KYTY_CMASK_CLEAR=0` в форму `=1`; иначе член (д)(1) проваливается без
  дефекта пробы.
- **Н3 (только многослойные цели).** `rearm` = «`hit` на записи `CMask`»: у цели с `layers ≥ 2`, если FCE идут разными видами слоёв (сначала
  слой 0, потом слой 1), второй FCE — `hit` с `rearm=1` без повторной заливки. Это буква (г)(1) («как в F9e2b»). У T6 `layers=1`, поле
  `rearm` других экстентов — справка.

## Свои проверки (файлы)

`C:/kyty/f287/f9/f9f3/`, в git `docs/track-f/f9f3/`:
- `model_f9f3.py`, `model_f9f3.out.txt` — своя модель: часть 1 — эквивалентность члена и очистки, часть 2 — S1–S4, X1–X3, `=0`, инварианты;
  `ALL OK`.
- `cfgtests_f9f3.log` — свой прогон тестов; в git с окончаниями LF, sha256 в тексте — у локального оригинала.

## Не заявляется

- Что сценарии Н1–Н3 или RC1 F9f2 случаются в этой игре: число FCE T6 на заливку и вид FCE T6 в логе — [U] до F9g.
- Что модель исчерпывает пути кода: она переписывает названные строки, гонки между `QueryMetaFill` и `FindRenderTarget` не моделирует (О1 F9e2b).
- Что CMASK-очистка — единственная причина Б42; цвет очистки T6; что раскладка CMASK некратного экстента верна; какой из M1–M3 верен.
- Что на PS5 вода в этих ракурсах чистая; что исправление будет; что другие сцены не изменятся при `=1`.
- Ни одно число — не выигрыш; 60 FPS не обещаются. Путь без `KYTY_FIX_B42` не меняется (по коду).
