# F9e2c (`HPP-436`, Emu Engineer): правка `KYTY_FIX_B42` (M2c) по RC1 F9f2 — взведённость записи `CMask` по битам слоёв вида

Решение лида — `ca38fdb5:docs/ROADMAP.md:19468` п. 357 (якорь «357. **Звено F9f2 трека F (`HPP-430`, Red Team) принято»; +1 — «взведена» п. 353(г)(2)
читается по битам слоёв вида цели, а не по всей маске»), подпункты (г)(1)–(4); п. 353(г) в силе, кроме заменённого члена. Вход — отзыв
`4256e8cf:docs/track-f/f9f2-review.md` (RC1, модель `4256e8cf:docs/track-f/f9f2/model_rearm.py`), код F9e2b `2da00d80`. Игра не запускалась;
установленный бинарь `4aa62e95` и кэши не тронуты. Время — UTC по `date -u`, события — `C:/kyty/f287/f9/times.txt`. Метки: [c] — показано кодом или
выводом, [I] — вывод, [U] — неизвестно. **WIP по дыму: бинарь собран и проверен тестами, игрой не проверялся** (дым и шесть тегов — F9g после F9f3).

## Итог

- **Правка только `src/graphics/host_gpu/renderer/pipeline/descriptors.cpp`**, только `FixB42Probe` и её заголовочный комментарий (11 вставок,
  2 удаления); `textureCache.*`, `renderDraw.cpp`, транслятор — не тронуты.
- Коммиты: **`main` `0b9dc0c9`** (родитель `8747c961`; один файл); **worktree `C:/kyty/f287/f9/f9e2c/wt` — `722c5e7f` на `64de099c` (cherry-pick
  F9e2b `0cbaa644`, дерево = `0cbaa644`) на `7662bb28` (cherry-pick F9e2 `23a0b3f2`, дерево = `23a0b3f2`) на `4414e235`**; `src/graphics` worktree =
  `main` `0b9dc0c9` (`git diff --quiet 0b9dc0c9 722c5e7f -- src/graphics` ✓); `git status --porcelain` worktree — 0 строк; CR в `src/` worktree — 0 из 456.
- **Бинарь: sha256 `24efead326a6ddfd8b24b05549228fa165a1876a2c5adf58e2354b9d77270061`**, копия `C:/kyty/f287/f9/bin/kyty_emulator_24efead3.exe`
  (sha256 копии тот же; `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe`). Не установка. Бинарь F9e2b `c494bb69` в F9g не идёт (п. 357).
- `check_gate_order.py` (`C:/kyty/s113/`) — `GATE ORDER: clean`, вывод байт в байт = F9e2b (гейтов и ручек правка не добавляет).
- `shader_cfg_tests` — **127 тестов, падение 1 — Б11** (`IMAGE_SAMPLE_C`/`IMAGE_SAMPLE_C_LZ`), rc 0; лог **байт в байт = P23** (sha256 `5a60758aab7abd57…`).
- **Подпись трансляции `KYTY_SHADER_SOURCE_HASH` = `56189185f9e9f9a0ea5174f3f85206e6d099db3d`** — `build/kytyGitVersion.h:9`, 1 вхождение в exe;
  `git diff --quiet 4414e235 722c5e7f -- src/graphics/shader` ✓. `KYTY_GIT_REVISION` = `722c5e7f…` (`kytyGitVersion.h:7`), в exe — короткое `722c5e7`.
- В exe строки `FixB42: mode=`, `KYTY_FIX_B42`, `drawn=%` — по 1. Предупреждения сборки в правленом файле — одно, прежнее (`descriptors.cpp:611` `-Wreturn-type`).
- Модель S1–S4 — по требованию п. 357(г)(3), вывод кончается `ALL OK`.

## Diff

- Против `2da00d80` (F9e2b → F9e2c): `descriptors.cpp` 11 вставок, 2 удаления — `docs/track-f/f9e2c/f9e2c_vs_2da00d80.diff`.
- Против `4414e235` (F9e2 + F9e2b + F9e2c, worktree `722c5e7f`): `textureCache.cpp` +31/−1, `textureCache.h` +33/−1, `descriptors.cpp` +129/−1 —
  `docs/track-f/f9e2c/f9e2c_vs_4414e235.diff`. Скрипт правки — `docs/track-f/f9e2c/patch_f9e2c.py` (якоря — целые строки/блоки, каждый ровно 1 раз,
  проверка всех до записи; LF), применён к `main` и worktree одинаково (`cmp` файла ✓).

```diff
-	const bool armed = fill.pending || (fill.cmask && fill.clear_mask != 0);
+	// F9e2c: the layer bits of the view FindRenderTarget gets below - as PrepareCmaskClear reads them (no bits where
+	// it returns without a clear).
+	const auto& view       = color.desc.view_info;
+	const bool  view_ok    = view.base_level == 0 && view.base_layer < 32 && view.layer_count <= 32 - view.base_layer;
+	const auto  layer_bits = !view_ok ? 0u
+	                                  : (view.layer_count >= 32 ? UINT32_MAX : (1u << view.layer_count) - 1u)
+	                                        << view.base_layer;
+	const bool armed = fill.pending || (fill.cmask && (fill.clear_mask & layer_bits) != 0);
```

## По букве п. 357(г)

**(1) Взведённость** — `0b9dc0c9:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3672–3677`:
- `view` — `color.desc.view_info` того же `color`, чей `desc` уходит в `FindRenderTarget` ветки FCE (`:3766–3773`); между пробой (`:3752`) и вызовом
  меняется только `desc.info.metadata` (`:3753–3757`), `view_info` — нет [c].
- `view_ok` (`:3673`) — отрицание условия раннего выхода `PrepareCmaskClear`
  (`2da00d80:src/graphics/host_gpu/renderer/cache/textureCache.cpp:2008`, якорь «if (view.base_level != 0 || view.base_layer >= 32 || view.layer_count > 32 -
  view.base_layer) return;»; +1 — «for (uint32_t layer = view.base_layer; layer < view.base_layer + view.layer_count; ++layer) {»); при `!view_ok`
  `layer_bits = 0` ⇒ запись `CMask` не взведена.
- `layer_bits` (`:3674–3676`) — биты `[base_layer, base_layer + layer_count)`: те, что обходит цикл `:2009`. Без неопределённого сдвига: `1u << 32`
  не вычисляется (ветка `layer_count >= 32` — тогда `view_ok` даёт `base_layer == 0`); при `layer_count < 32` сдвиг `< 32`, `base_layer < 32`, а
  `layer_count ≤ 32 − base_layer` держит результат в 32 битах. `layer_count == 0` ⇒ 0 бит (цикл `:2009` тоже не исполняется). Края — в модели
  (`layer_bits`, 8 случаев).
- `armed` (`:3677`) — `PendingDcc` (как F9e2b) **или** `CMask` с `(clear_mask & layer_bits) != 0`. Член стоит до развилки `hit`/`drawn` (`:3678`,
  развилка `:3683–3686`) — `drawn` его тоже требует [c]. `rearm = fill.cmask` (`:3688`) — как F9e2b.

**(2)** `applied` (`:3777–3780`), строка (`:3728–3730`), частота, счётчики по экстенту и `hit_all` (`FixB42Note`, `:3695–3731`) — без изменений (diff их не задевает) [c].

**(3) Модель** — `docs/track-f/f9e2c/model_rearm.py` (форма `model_rearm.py` F9f2; член взведённости — по строкам `0b9dc0c9`, `TrackDccFill` и
`PrepareCmaskClear` — по `2da00d80`, F9e2c их не меняет), вывод `docs/track-f/f9e2c/model_rearm.out.txt`, rc 0:

| Сценарий | Требование п. 357(г)(3) | Модель |
|---|---|---|
| S1 заливка → 4 FCE | `hit=1 applied=1 rearm=0` | `hit=1 applied=1 rearm=0 drawn=0` ✓ (FCE₂–₄: `none`, маска `0xfffffffe` & бит 0 = 0) |
| S2 заливка → FCE → заливка → FCE | `hit=2 applied=2 rearm=1` | `hit=2 applied=2 rearm=1 drawn=0` ✓ |
| S3 заливка → FCE → draw → FCE | `hit=1 applied=1 drawn=0` | `hit=1 applied=1 rearm=0 drawn=0` ✓ |
| S4 заливка → draw → FCE | `hit=0 drawn=1` | `hit=0 applied=0 rearm=0 drawn=1` ✓ (RC1 отзыва `dcd762d6` закрыт по-прежнему) |
| справка: S1 с членом F9e2b | — | `hit=4 applied=1 rearm=3` (= RC1 F9f2) |
| справка: S1 при `=0` | — | `hit=4 applied=0 rearm=0` (записи `CMask` нет, рост на каждом FCE — п. 353(д) Н2) |

Последняя строка вывода — `ALL OK`.

**(4)** Правка только `descriptors.cpp` ✓; код — коммитом `0b9dc0c9` в `main` только по файлу правки (`--only`) ✓; бинарь — чистый worktree на
`4414e235` + F9e2 + F9e2b + F9e2c, sha256 и копия ✓; `shader_cfg_tests` 127/1 = P23 ✓; подпись `56189185` ✓; не установка ✓.

## Состояние, вводимое правкой

Нового состояния нет: `view`, `view_ok`, `layer_bits` — локальные константы вызова `FixB42Probe`, только чтение `color.desc.view_info`; полей, счётчиков,
записей кэша, `BumpMetaEpoch` правка не добавляет [c].

## Путь `=0` = `4414e235` по значениям

Правка меняет только значение `armed`, т. е. только то, какой `FixB42Kind` вернёт проба. При `KYTY_FIX_B42` не заданной / `""` / `0/false/off/no`
(`Common::EnvFlagOn`, `descriptors.cpp:3647`) `kind` используется лишь (а) в условии правки `desc` (`:3753`, требует `FixB42Enabled()` — ложь),
(б) в условии второго `QueryMetaFill` (`:3777`, то же), (в) в вызове `FixB42Note` (`:3775`, `:3782` — счётчики и строка лога). Значит, при `=0` новый
член меняет только строки `FixB42:`; `color.desc`, вызов `FindRenderTarget` (те же `id`, `desc`, `guest_clear_regs`, `fce_materialize = true`), команды
Vulkan и состояние кэша — те же, что у F9e2b, а у F9e2b они по значениям = `4414e235` (п. 9 чек-листа F9f2, принят п. 357(а)) [c по коду]. Отличия
F9e2c + F9e2b + F9e2 от `4414e235` при `=0` — прежние: строки `FixB42:`, запись в `std::unordered_map` на медленном захвате цели, +8 байт записи
метаданных. При `=0` запись `CMask` у цели некратного 1024 экстента не возникает (п. 353(в)(4)) ⇒ новый член при `=0` счёт не меняет [I]. Подтверждение
прогоном — F9g.

## Сборка

Чистый worktree `C:/kyty/f287/f9/f9e2c/wt` (`mk_wt_f9e2c.sh` — копия `mk_wt_f9e2b.sh` + cherry-pick `0cbaa644`), патч, configure (02:02:25Z), сборка-проверка
(02:03:34Z), коммиты `0b9dc0c9` / `722c5e7f`, пересборка с версией (02:06:35Z, 02:06:57Z), тесты (сборка 02:07:31Z) — всё под `lockrun.sh` (убивает шаг
при замке или `C:/kyty/f287/STOP`), флаги = F9e2b/P23 (`build_f9e2c.cmd` — копия с путями f9e2c). **Чужой замок** `gop31.sh hx_sha` (строка замка
«started 2026-10-03T04:04:08» местного = 02:04:08Z) убил шаг версии в 02:04:09Z; ожидание до снятия замка, шаг повторён; второй замок `gop31.sh ha_A4` (02:09:31Z) застал копирование файлов отчёта — под ним ничего не писалось, продолжено после снятия (02:17:05Z); `times.txt` — строки обоих.
`CMakeCache.txt`: `Kyty_SOURCE_DIR=C:/kyty/f287/f9/f9e2c/wt`, `Release`.

## Файлы

`C:/kyty/f287/f9/f9e2c/`, копии в `docs/track-f/f9e2c/`: `patch_f9e2c.py`, `patch_main.out.txt`, `patch_wt.out.txt`, `f9e2c_vs_2da00d80.diff`,
`f9e2c_vs_4414e235.diff`, `gate_order.out.txt`, `cfgtests_defaults.log` (копии в git этого и `build_f9e2c.cmd`, `gate_order.out.txt`, `model_rearm.out.txt`, `patch_*.out.txt` — с окончаниями LF, sha256 в `SHA256SUMS_f9e2c.txt` — у локальных CRLF-оригиналов), `model_rearm.py`, `model_rearm.out.txt`, `mk_wt_f9e2c.sh`,
`mk_wt.log`, `mk_scripts.py`, `build_f9e2c.cmd`, `lockrun.sh`, `commit_msg_code.txt`, `SHA256SUMS_f9e2c.txt`.

## Не заявляется

Что сценарий RC1 случается в этой игре (число FCE T6 на заливку [U]); что модель исчерпывает пути кода (она переписывает названные строки); что
CMASK-очистка — единственная причина Б42; цвет очистки T6; что раскладка CMASK некратного экстента верна; какой из M1–M3 верен; что на PS5 вода в этих
ракурсах чистая; что исправление будет; что другие сцены не изменятся при `=1`; ни одно число — не выигрыш; 60 FPS не обещаются; путь без
`KYTY_FIX_B42` не меняется (по коду, см. выше).
