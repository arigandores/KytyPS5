# F25f (`HPP-669`, Harness Engineer): серия Б36 / Б40 на бинаре B — печать до первого тега

Трек F, итерация F25 (Б36 `pot_treasure_cave`, Б40 `bonus_path_maker_mix`), звено F25f по п. 596(г)–(з) с поправками п. 599(б)(1)–(7),
(10), (11), (в) RC13–RC14, п. 600(б)(4) и п. 602(в)(2). Этот файл — печать: после её записи ридер `f25_read.py`, цепочка тега, правила
чтения и остановки не меняются; её sha256 пишется в json каждого тега (`prereg`), ридер сверяет её в допуске. **Вердикта нет:** чтение —
F25g (`HPP-670`, лид). Метки: [c] — код/лог прочитан или пересчитан, [I] — вывод, [U] — неизвестно. Время — UTC.

theta_load: 0.4562

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1; проверка — `refs_f25f.py`)

- Решение звена — п. 596 `47d618fe:docs/ROADMAP.md:23586` (якорь «596. **Звено F25b трека F (`HPP-661`, лид): приёмка проекта F25a»;
  +1 — «(а) **Приёмка строкой. F25a ✓.**»); поправки — п. 599 `47d618fe:docs/ROADMAP.md:23600` (якорь «599. **Звено F25c трека F
  (`HPP-666`, лид на стадии review)»; +1 — «(а) **Приёмка строкой. F25c ✓**»), п. 600 `47d618fe:docs/ROADMAP.md:23617` (якорь «600.
  **Звено F25d трека F (`HPP-667`, лид на стадии review)»; +1 — «(а) **Приёмка строкой. F25d ✓.**»), п. 602 `47d618fe:docs/ROADMAP.md:23634`
  (якорь «602. **Звено F25e трека F (`HPP-668`, Red Team»; +1 — «(а) **Приёмка строкой. F25e ✓.**»).
- Проект — `9c6cf4ea:docs/track-f/f25a.md` (§3–§7, §11.3–§11.4); ридер-образец — `e8ea0a57:docs/track-f/f20l3/b32_read.py` (цепочка
  п. 550(г)(2)(iv) перенесена без изменений); харнесс-образец — `24ce64ea:docs/track-f/f20l3/go_f20l3.sh`.
- Состав снимков A / B (п. 599(б)(6)) — пять каталогов манифеста харнесса F20l3: `24ce64ea:docs/track-f/f20l3/go_f20l3.sh:55` (якорь
  «MF=("_ShaderCache=$EMU/_ShaderCache" "_ShaderSeeds=$EMU/_ShaderSeeds" "_PipelineCache=$EMU/_PipelineCache" "_SaveData=$EMU/_SaveData"
  "GLCache=$GLDIR")»; +1 — «[ -e $F/STOP ] && { log "STOP file: $(head -1 $F/STOP)"; exit 4; }»): `_ShaderCache` (с `replay/`),
  `_ShaderSeeds`, `_PipelineCache`, `_SaveData`, GLCache драйвера; «холодный» = A вместе с GLCache.
- Поле `flip_ns` — последнее поле строки `DiagB32:` (`35b454c6:src/common/diagB32.cpp:643`, якорь «" cover_us=%llu flip_ns=%llu\n", // F25d
  (items 596(v) C4, 599(b)(11) C6): flip_ns - the FrameStats::NowNs scale, last»; +1 — «n, static_cast<unsigned long long>(r.dt_us),
  static_cast<unsigned long long>(r.instr_us), r.gaps.samples,»); последнее поле `-x` — `others_cut_w` (`35b454c6:src/common/diagB32.cpp:723`,
  якорь «" ring_hold=%llu ring_hold_w=%llu hist_exh=%llu hist_exh_w=%llu w_cut_w=%llu others_cut_w=%llu\n",»; +1 — «n, static_cast<unsigned
  long long>(counters->slots), static_cast<unsigned long long>(counters->slot_full),»). Поля «число закрытых записей ожидания» в строке `-x`
  нет [c] ⇒ по п. 602(в)(2) берётся число строк `-w` окна n − 1 (поле `w_lines` его заголовка).
- Окно кончается в `OnFlip(n)` (`35b454c6:src/graphics/presentation/videoOut.cpp:1293`, якорь «Common::DiagB32::OnFlip(r.cfg->flip_status.count,
  r.id, r.reserve_host_ns);»; +1 — «}»), строка `FrameTrace` n печатается позже в том же вызове (`35b454c6:src/graphics/presentation/videoOut.cpp:1442`,
  якорь «LOGF("FrameTrace: n=%" PRIu64 " dt_us=%llu lat_us=%llu gpu_proc=%llu gpu_idle=%llu"»; +1 — «" gpu_blocked=%llu submits=%llu
  submit_us=%llu semwaits=%llu semwait_us=%llu"») — основа калибровки смещения (§4).
- Путь `GpuHangAbort` кончается `EXIT` (`0005e11f:src/graphics/host_gpu/renderer/masterSemaphore.cpp:128`, якорь «EXIT("GPU stopped completing
  submissions\n");»; +1 — «}») ⇒ строка `--- Error ---` (`0005e11f:src/common/assert.cpp:40`, якорь «Log::WriteFatal(BuildFatalReport("--- Error
  ---", text, file, line));»; +1 — «return 1;») — допустима только после строки `GpuHangAbort:`.
- Бинарь тегов — B: sha256 `e342b839d74d5689bc4f66ee0ed04a37e9a640e60a199a2882c8e83ecf19cfa4`, копия `C:/kyty/f287/f25d/kyty_emulator_e342b839.exe`
  (п. 600(а), 602), подпись трансляции `9177b4267de1fb8bac7d1113afd8733210addfac` = S18, каталог `variant_fixb26_fixb1b_fixf10_fixf19`.
  **Установленный — S18**: `b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a`, закреплённая копия
  `C:/kyty/s288/bin/kyty_emulator_b3cee576.exe`; до = после по полному sha256 у каждого тега (член допуска).

## 1. Теги и форма

| тег | уровень | ручки формы (позиционно в `enter_scene.py`) | кэши | роль |
|---|---|---|---|---|
| `f25_c1` | `pot_treasure_cave` | `KYTY_DIAG_B32=1` | до = A (снимок A берётся перед первым вызовом, повтор — возврат A); без возврата; после — снимок C1 | прогрев, холодный слой справкой |
| `f25_c2` | `bonus_path_maker_mix` | `KYTY_DIAG_B32=1` | до = C1 (возврат C1); без возврата; после — снимок B | прогрев, справка |
| `f25_z1` / `f25_z2` | pot / bonus | `KYTY_DIAG_B32=0` | до = B, возврат к B | контроль `=0` |
| `f25_pb` | pot | `KYTY_DIAG_B32=1 KYTY_TEST_B32=60:present:3000` | до = B, возврат к B | ПК-B |
| `f25_pc` | bonus | `KYTY_DIAG_B32=1 KYTY_TEST_B32=60:gpusleep:6000` | до = B, возврат к B | ПК-C |
| `f25_s01` … `f25_s40` | pot / bonus (аргумент цепочки) | `KYTY_DIAG_B32=1` | до = B, возврат к B | тёплая серия |
| `f25_k01` … `f25_k10` | pot / bonus | `KYTY_DIAG_B32=1` | возврат A перед тегом, до = A, возврат к A | холодный слой (ж) |

- Общая форма: `enter_scene.py <тег> --level <уровень> --attempts 1 --stable-draws 300 --timeout 480 --no-install --require-idle --gates-file
  gates_default.txt --pred pred/f25f_seal.md --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 KYTY_GPU_HANG_ABORT_S=22
  <ручки формы>`; константы харнесса F20l3 прежние, кроме `KYTY_GPU_HANG_ABORT_S` 8 → 22 (п. 599(б)(2); пара после констант перекрывает их);
  без валидации, RenderDoc, `KYTY_GPU_CHECKPOINTS`, `KYTY_GAME_PATCH`, нагрузчика; цепочка снимает все `KYTY_*` и `VK_LAYER_*` шелла.
- Имена `f25_sNN` (номер — порядок вызова, уровень — аргумент цепочки `pot|bonus`, пишется в `runs/<тег>/level.txt` и `guest_args` json),
  `f25_kNN`, повтор помехи `<тег>_r<k>` (k ≤ 6) — **вариант исполнителя** (лид назвал `f25_sNN`, `f25_kNN`).
- Порядок: `f25_c1`, `f25_c2` → `f25_z1`, `f25_z2`, `f25_pb`, `f25_pc` → серия поочерёдно pot / bonus (выбывший уровень уступает другому
  подряд) → после конца тёплых серий обоих уровней — холодные подсерии (п. 599(б)(6)) → `go_f25f.sh restoreA` (манифест = A, `EQUAL`).
  Серия начинается только при `CONTROLS PASS` (все 4). Повтор прогрева `f25_c1` ⇒ повтор `f25_c2` (снимок B берётся заново) — вариант исполнителя.
- **Неразрывный блок серии (п. 604, вариант (в)(1)):** `f25_c1` → `f25_c2` (между ними живые кэши — снимок C1 без возврата); чужой тег
  в этот промежуток не берётся. Вне блока замок берут по очереди; между тегами серии живые кэши = B (тёплые теги и контроли) или A
  (холодный слой, после `restoreA`). Звено FS9c ставит FS9 только после конца серии (п. 604).
- **Бинарь:** внутри замка после снимков ставится копия B (проверка sha256, `installed_sha.txt`); после тега — S18 из закреплённой копии;
  иначе `RETURN_FAILED`, замок остаётся. `C:/kyty/build/install` не трогается.
- **Снимки** (`snap_f25f.py`, под замком тега): `take` — копия пяти каталогов в `C:/kyty/f287/f25f/snap/<имя>/` + манифест `<имя>.tsv`,
  сверка копии с манифестом (`SNAP TAKEN … EQUAL`); `restore` — живые каталоги заменяются копией, живой манифест = `<имя>.tsv`
  (`SNAP RESTORED … EQUAL`), иначе `RETURN_FAILED`. Член допуска — `snap_cmp.txt`: манифест до тега = снимку формы (`manifest cmp EQUAL`);
  у тегов с возвратом — `manifest_cmp.txt` до = после `EQUAL`; у прогревов — строка `NO RETURN` (`noreturn.txt`). Снимок B у пользователя
  не остаётся: в конце серии — A.
- **M6** (`m6_f25f.py`, справка): строка раз в 1 с — `emu_t` (секунды от создания процесса эмулятора), `qpc_ns` (QPC этого процесса),
  CPU посторонних; имена — только в `m6_local.txt`, в `m6.txt` — `<app>`. Поллер калибровки (поток того же процесса, 50 мс) пишет
  `cal.txt`: `CAL qpc_ns=<QPC первого появления строки> n=<n>` для каждой новой строки `FrameTrace: n=` живого лога.
- Сторож игры пользователя (`guard_f25f.py`, блоки ≤ 6 тегов, открытие двумя чистыми проверками ≥ 600 с), очередь (`queue_f25f.py`:
  занята только звеньями трека P с готовым входом — п. 322(г); звенья F берут замок по очереди самим замком), проверка прогона
  (`runchk_f25f.py`), вызов `launch_f25f.sh <тег> [pot|bonus]` (только запуск), ожидание `wait_f25f.sh <тег>` ≤ 540 с, чтение
  `post_f25f.sh <тег>` — как F20l3.

## 2. Допуск тега (провал любого члена — помеха: повтор, в счёт не идёт)

json есть; `theta_load` из печати; `binary_sha256` = B; установленный до = после = S18; `prereg` = sha256 печати; окружение = константы
харнесса + ручки формы (без лишних); `KYTY_GPU_HANG_ABORT_S` = 22; последние `--vulkan-validation false`, `--shader-validation false`, нет
`--rd`; `guest_args` = `-lvl <уровень тега>` (у c1, z1, pb — pot; у c2, z2, pc — bonus; у s, k — = `level.txt` цепочки); опция удержания
330; лог есть; сцена вошла (первый кадр сцены); удержание — сцена ≥ 300 с ИЛИ `GpuHangAbort:` после ≥ 10 с сцены; маркеров смерти, кроме
`GpuHangAbort:` и `--- Error ---` после неё, нет; событий окна 0; строка `DiagB32: mode=1` одна (`=1`) / строк `DiagB32` 0 (`=0`); строки
`DiagB32: config` нет; подпись `9177b426` и каталог варианта; строки `TestB32` armed / fire / done только у pb / pc; `rep_drop` 0;
нагрузчика нет; кэши до = снимку формы; возврат (`EQUAL`) / у прогрева `NO RETURN`.
**Тёплость** (только тёплая серия и контроли): 0 строк дампа трансляции в интервалах кадров с началом ≥ 10 с сцены. Тег серии, не
прошедший только её, — `NOT_WARM` (п. 599(б)(7)): читается правилом §3 в слое `N_nw_L` / `K_nw_L` (в `N_L`, `K_L`, ступень и остановку
не входит) и занимает одно из 6 мест помех; хэши программ — из строк `ShaderRecompiler … phase begin: … hash=0x…` тех интервалов; два
`NOT_WARM` тега уровня с общим хэшем ⇒ `STOP_LEVEL_Q` — стоп серии уровня и вопрос лиду. Контроль, не прошедший тёплость, — помеха.
Строка `rebuild skipped reason=recipes_current` — справка (число строк печатается).

## 3. Правило чтения (п. 596(д) с поправками п. 599(б); ридер `f25_read.py`, фикстуры `test_f25_read.py`)

1. **Кадр удержания** — кадр сцены с `dt_us` ≥ 100 000 и началом ≥ 10 с сцены (определения F20e, имя уровня — параметр: ридер ставит
   константу `SG` копии F20c `f20e_read.py` равной уровню тега до разбора). **Сначала ключ (RC11):** окно кадра n — строка `DiagB32:` с `n`,
   если её `dt_us` ≥ 0,5 × `dt_us` кадра (край 2·w = dt входит); иначе `n + 1` при том же условии; обе — с большим `dt_us` (равные — n);
   ни одной — `NO_SAMPLES:key`. Один ключ у двух соседних кадров удержания — флаг `SHARED_WIN` (справка; `instr_us` общего окна у обоих).
2. **Кадр в счёте (K2):** `dt_us` ≥ 1 000 000, атрибуция F20c (буква) — не Б5 / Б33 / Б1б (они — справка; на B буква F20c Б33 не даёт —
   сохранение кэша после S12 не атрибуция; член сохранён по букве п. 596(д)(1), RC14), `dt_us − instr_us(ключа)` ≥ 1 000 000, иначе
   `INSTR_MADE_K2` (в `K_I`, не в `K`); `NO_SAMPLES:key` ⇒ в `K` с этим классом. Кадры 100 мс – 1 с — справка тем же правилом;
   «предвестник» — такой кадр (не Б5 / Б33 / Б1б), начавшийся не раньше чем за 5 000 000 мкс до начала кадра в счёте.
3. **Класс ключевого окна (первое совпадение):** (0а) `dt_us` окна > 20 475 000 ⇒ `NO_SAMPLES:cover` (п. 599(б)(3)); (0б) нет строки `-x`,
   поля из `ZERO_W` ридера F20l3, `hist_exh_w`, `w_cut_w`, `others_cut_w`, поля заголовка `dt_us`, `cover_us`, `sgap_max_us`, `flip_ns`,
   последнее поле заголовка не `flip_ns` / `-x` не `others_cut_w`, строка `-t` без `peer=`, `-w` без `peer_tid=` ⇒ `NO_SAMPLES:trunc`;
   (0в) `hist_exh_w` ≥ 1 ⇒ `NO_SAMPLES:cover`; (0г) при `hist_exh_w` = 0 согласие `dt_us − cover_us ≤ sgap_max_us + 1` нарушено ⇒
   `NO_SAMPLES:trunc`; (i) `HOST_FREEZE` — `sgap_max_us` ≥ 0,5 × E (E и медианы — по 20 соседям < 100 мс); (ii) `NO_SAMPLES` — `i2` ≠ 1,
   `samples` 0 или нулевой инвариант окна ≠ 0 (`ZERO_W` + `hist_exh_w` + `w_cut_w` + `others_cut_w`); (iii) `HOST_LOAD` — `other_us` ≥
   0,4562 × `ncpu` × окно; (iv) цепочка п. 550(г)(2)(iv) с RC6, RC7, п. 574(д), 581(в)(5) — без изменений. Семейство — класс без `:<деталь>`.
4. **Abort (п. 599(б)(2)):** тег со строкой `GpuHangAbort:` после ≥ 10 с сцены (время сцены — конец последнего кадра сцены перед строкой) —
   удержание в `N_L` с одним кадром в счёте класса `NO_SAMPLES:abort`; раньше 10 с — помеха.
5. **Флаг `M6_BURST`** (не класс): выборка M6 с `foreign` ≥ 8,0 CPU-с/с в [начало окна − 1,5 с; конец окна + 1,5 с]. Шкала (п. 600(б)(4),
   ветвь «нет» п. 599(б)(11)): `FrameStats::NowNs` — не QPC, поэтому окно переводится на шкалу QPC M6 смещением, откалиброванным в каждом
   теге: **offset = min по напечатанным окнам n (QPC первого появления строки `FrameTrace: n=<n>` в живом логе − `flip_ns` окна n)**;
   строка печатается после `OnFlip(n)` в том же вызове и доходит до файла не раньше, поэтому каждая пара ≥ offset, минимум — лучшая оценка.
   Конец окна = `flip_ns` + offset, начало = конец − `dt_us` окна × 1 000. Нет пары (нет `cal.txt`, нет окна, увиденного поллером) или нет
   `m6.txt` ⇒ `NOT_DETERMINED`. `qpc_ns` M6 с `flip_ns` напрямую не сравнивается; `emu_t` — справка. Печатается число пар и разность второй
   пары и минимума (справка о разбросе задержки).
6. **Подпись формы:** `FORM_SEM` — `semwait_us` строки кадра ≥ 0,5 × `dt_us`; `FORM_NOFLIP` — `other_us` строки `FlipHold:` интервала кадра
   ≥ 0,5 × `dt_us` и не SEM; иначе `FORM_OTHER`. На логах описи [c `regress_f25.py`]: Б36 `v143_08` n 14 701 — `FORM_SEM`, Б40 `v145_14` n 7 249 —
   `FORM_NOFLIP`; предвестники — n 14 588, 14 669 и 7 188, 7 216.
7. **Удержание:** `K` = 1, если удержание и ≥ 1 кадр в счёте (или abort); `K_I` = 1, если удержание и ≥ 1 кадр K2 не Б5 / Б33 / Б1б (в
   счёте или `INSTR_MADE_K2`) или abort; класс удержания — класс самого длинного кадра в счёте.
8. **Серия по уровню L** (п. 596(е), 552(г)): `N_L` — допущенные тёплые теги серии уровня (повтор `_r<k>` стоит за своё имя); `N_L` < 5 —
   продолжать; `K_L` ≥ 3 — `STOP_READ`; `K_L` = 0: `N_L` < 14 — продолжать, на 14 — `STOP_U2` (`K_I_L` = 0) или `STOP_552G` (`K_I_L` ≥ 1, не
   У2, п. 552(г)); `K_L` 1–2 — до `K_L` = 3 (`STOP_READ`) или `N_L` = 20 (`STOP_U2PRIME`). Классы, доли групп (i), (iii) и старший класс
   печатаются справкой — ступени (д)(6) читает F25g. Сведение уровней — F25g.
9. **Холодный слой (ж):** после У2 / У2′ (или `STOP_552G` — вопрос лиду) тёплой серии уровня и конца тёплых серий обоих уровней — до 5
   тегов `f25_kNN`; остановка на первом теге с кадром в счёте (`STOP_REPRO`) или на 5 (`STOP_NO_REPRO`); кадры читаются §3 справкой.
10. **У5 (з):** окно тега с `dt_us` ≤ 20 475 000 «плохое» при элементе обрезки, нарушенном согласии или нулевом инварианте ≠ 0; `sgap_bad_w`
    окна n, у которого окно n − 1 имеет ≥ 20 000 строк `-w` (`w_lines`), — строка справки «`sgap_bad` за длинным закрытием», не У5 (только
    `sgap_bad_w`; остальные члены — по п. 599(б)(3)); окна > 20 475 000 — исключены (справка). `U5(4)` — ≥ 2 тега серии с плохим окном ⇒
    стоп, вопрос лиду (одна переделка). Медиана `dt` сцены и кадры ≥ 70 мс — справка против `f25_z*`.
11. **Контроли (з):** `f25_z1`, `f25_z2` — строк `DiagB32` 0 и строки `mode=1` нет; `f25_pb` / `f25_pc` — кадр стенда (самый длинный из 3
    кадров после `TestB32: fire`) ≥ 3 000 000 / ≥ 6 000 000 мкс, ключ сведён, `hist_exh_w` 0, согласие, `lines_cut_w` 0, `w_cut_w` 0,
    `others_cut_w` 0, 0 окон тега с элементом обрезки; класс ПК-B — `EMU_CALL:present…` (любое деление RC7); ПК-C — `UNMARKED:Gpu` или шаг на
    GuestGpu с `Sw` или `S` ≥ 50 %, не `HOST_FREEZE`, не `NO_SAMPLES*`; справка — строк `-w` против ≈ 330 / ≈ 630, `others_cut_w`, `print_us`,
    `instr_us` следующего окна, ветвь ключа. **RC13:** оба ПК проверяют только ветвь `n` ключа (сон до `OnFlip` / до флипа); ветвь `n + 1`
    проверяется только фикстурами (кадры `b32_pa` 8 796 → 8 797 и синтетический `SHARED_WIN`). Провал любого контроля — `CONTROLS FAIL`,
    стоп серии до решения лида (У1′: одна правка кода, затем все 4 контроля на новом бинаре, бюджет 66).
12. **Бюджет:** ≤ 66 тегов; помехи вместе с `NOT_WARM` ≤ 6, седьмая — `STOP_INTERFERENCE` и вопрос лиду.

## 4. Варианты исполнителя (лид не назвал)

- Имена тегов и аргумент уровня (§1); повтор прогрева c1 тянет повтор c2.
- Калибровка смещения — минимум по всем окнам тега (не одно событие); событие с обеими метками — окно `DiagB32` n и первое появление
  строки `FrameTrace` n в живом логе по QPC поллера M6.
- «Предвестник» — по началам кадров (≤ 5 000 000 мкс от начала кадра в счёте).
- Член ПК «0 строк без последнего поля» — по всем окнам тега ≤ 20 475 000 (не только ключевое).
- Число записей окна n − 1 для п. 602(в)(2) — `w_lines` заголовка окна n − 1; не напечатанное окно n − 1 — 0 (строже).
- Холодный слой при `STOP_552G` — вопрос лиду до холодных тегов.

## 5. Не заявляется

П. 596(л), п. 599(д), п. 600(г), п. 602(д) целиком; что калибровка смещения точнее задержки записи лога; что `M6_BURST` — причина кадра;
что Б36 и Б40 — дефекты эмулятора или одна причина; что инструмент не меняет частоту K2; что бинарь B при `=0` равен S18 в машинном коде;
что выводы о B переносятся на S18; что опись полна; ни одно число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется.

## 6. Строки печати (sha256 файлов и последних выводов наборов)

- `test_f25_read.out.txt` (sha256 ca25ba48dc21e0fc): checks 351; ALL OK; первая строка набора: `suite test_f25_read.py sha256 a4cf6aed7ad399b8a58592980f26411d848463cb3f125b518b0e111d418969cc target f25_read.py sha256 933f36c1f63bbb3159144e1a7ca7395dc000234d6dc3be27349e40b2ff902ddf`
- `sens_f25.out.txt` (sha256 d2171f22ca37a1d3): edits 82 caught 82 kept 0; ALL OK; первая строка набора: `suite sens_f25.py sha256 b0bfdf3e4ea0cf488386e10253e7024b6aac6813e8241652f9fc7f931a18ba27 target f25_read.py sha256 933f36c1f63bbb3159144e1a7ca7395dc000234d6dc3be27349e40b2ff902ddf test_f25_read.py sh`
- `regress_f25.out.txt` (sha256 69b4d2fc948990c5): REGRESS PASS; ALL OK; первая строка набора: `suite regress_f25.py sha256 b29eeba58ad630b7e7868ac9a0aedb6e42170c9e3aeb6e77dbce60b52d644f9f target f25_read.py sha256 933f36c1f63bbb3159144e1a7ca7395dc000234d6dc3be27349e40b2ff902ddf`
- `refs_f25f.out.txt` (sha256 af109de568309f13): refs 11 mismatches 0; ALL OK; первая строка набора: `suite refs_f25f.py sha256 9d8b7b7ce2e619f5d287b0b821871fb6a5d566b38431af202657c707888aa18c`
- `refs_neg.out.txt` (sha256 8ff87d916e88b9a4): NEG CONTROL OK; ALL OK; первая строка набора: `suite refs_f25f.py sha256 9d8b7b7ce2e619f5d287b0b821871fb6a5d566b38431af202657c707888aa18c (negative control)`
- `test_tools_f25f.out.txt` (sha256 7c7990e3feaad6ea): checks 37; ALL OK; первая строка набора: `suite test_tools_f25f.py sha256 e251cb8fd1b01d4999c3df8e01c38e9ae21535f04c96c6175443a810356705b4 target snap_f25f.py sha256 531369028ec730fe29eff532224bb8cbf3d5b5590c32ded45e28d56fca4b2592 m6_f25f.py `

seal: 933f36c1f63bbb3159144e1a7ca7395dc000234d6dc3be27349e40b2ff902ddf C:/kyty/f287/f25f/f25_read.py
seal: 5a986c03d161b9a5c52d589ad1da87e4676ceb9bac61acaeaa8f2131525400fa C:/kyty/f287/f25f/f20e_read.py
seal: a4cf6aed7ad399b8a58592980f26411d848463cb3f125b518b0e111d418969cc C:/kyty/f287/f25f/test_f25_read.py
seal: b0bfdf3e4ea0cf488386e10253e7024b6aac6813e8241652f9fc7f931a18ba27 C:/kyty/f287/f25f/sens_f25.py
seal: b29eeba58ad630b7e7868ac9a0aedb6e42170c9e3aeb6e77dbce60b52d644f9f C:/kyty/f287/f25f/regress_f25.py
seal: 9d8b7b7ce2e619f5d287b0b821871fb6a5d566b38431af202657c707888aa18c C:/kyty/f287/f25f/refs_f25f.py
seal: e251cb8fd1b01d4999c3df8e01c38e9ae21535f04c96c6175443a810356705b4 C:/kyty/f287/f25f/test_tools_f25f.py
seal: c79b6148031e61fabd757d548386c6b3bee242be71cdbc90b4327b22e11fe1ca C:/kyty/f287/f25f/f25f_seal_body.md
seal: 531369028ec730fe29eff532224bb8cbf3d5b5590c32ded45e28d56fca4b2592 C:/kyty/f287/f25f/snap_f25f.py
seal: 0dbd7c1fc5df191ffb0d253e5467466c027d5f9bc355b5fac1e188b5d475149a C:/kyty/f287/f25f/m6_f25f.py
seal: 475fbd59e30f14a47a42b264b362fa5b47afca98394041fd09d3bddce4cf8a86 C:/kyty/f287/f25f/go_f25f.sh
seal: 9f88f88b3b13fb5bf8dbfdaa94ae7185645c69c4c290737e35134e3cb485dd8b C:/kyty/f287/f25f/launch_f25f.sh
seal: 05ae628b209f13e17a85e8013380bff2317bb45292d6c06b2c12aec242d949ff C:/kyty/f287/f25f/wait_f25f.sh
seal: dcb261012e129555e3888183a1f377082ac6893da89113bd209300a10aa826b0 C:/kyty/f287/f25f/post_f25f.sh
seal: d973b14c8a9f9ed189e0d5a5eca822669d5b1f5ffd210289d30677b705a027ee C:/kyty/f287/f25f/chk_f25f.sh
seal: 4c15c545bf5573c2fe7f9bd465a6422df59af9f230d2861869cc28bce588cb33 C:/kyty/f287/f25f/guard_f25f.py
seal: ba793ed8d62f4b649e5be592d543538ed927bafe738b3ef9a70ca5d25351b62c C:/kyty/f287/f25f/queue_f25f.py
seal: 6291b7a8e0ca20ab6e5093a9f9d234f47abaa5fa30e03c5657590ba83bd0dce9 C:/kyty/f287/f25f/runchk_f25f.py
seal: e16406d346750eda05eeafbd58e10ce444f708aa47d3f25f4d95bf5618a644c2 C:/kyty/f287/f25f/watch_f25f.py
seal: c87ddd2495846a35ad07273908fc3f7ed8cd956a12a0dbefb7ce84c84320937e C:/kyty/f287/f25f/enter_scene.py
seal: d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0 C:/kyty/f287/f25f/procload.py
seal: a7096fd47f70419a5ed8d541778294f3032ca2c88e7b4b2e946f3d99651182bb C:/kyty/f287/f25f/manifest_fs4c.py
seal: c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d C:/kyty/f287/f25f/sheet142.py
seal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 C:/kyty/f287/f25f/gates_default.txt
seal: c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96 C:/kyty/f287/f25f/idle142.py
seal: 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 C:/kyty/f287/f25f/run_safety99.py
seal: c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21 C:/kyty/f287/f25f/launch_run.py
seal: 7fdd10c1163197e229eff4db92c467ff870e1a8b3111a93817a252db82ea0c08 C:/kyty/f287/f25f/mk_seal_f25f.py
seal: ca25ba48dc21e0fc32994ea8916673e066fd20295ee594424b68b1e50272eb16 C:/kyty/f287/f25f/test_f25_read.out.txt
seal: d2171f22ca37a1d3c6b66c273fed26bf2c336eb6e290fb95b879aa24e15858bc C:/kyty/f287/f25f/sens_f25.out.txt
seal: 69b4d2fc948990c5548e279d24c37606475d198261240a609b03bfade3628196 C:/kyty/f287/f25f/regress_f25.out.txt
seal: af109de568309f13f504110fc6cde816feb27b8483ccc3b9ccbdd3b5d74e48b1 C:/kyty/f287/f25f/refs_f25f.out.txt
seal: 8ff87d916e88b9a45f79b9f70583972b4364be72384d1e9d780ac62dc4d93230 C:/kyty/f287/f25f/refs_neg.out.txt
seal: 7c7990e3feaad6ea66368b3275d88c45e4376c00ee8c2541eafe63941c47879c C:/kyty/f287/f25f/test_tools_f25f.out.txt
seal: e342b839d74d5689bc4f66ee0ed04a37e9a640e60a199a2882c8e83ecf19cfa4 C:/kyty/f287/f25d/kyty_emulator_e342b839.exe
seal: b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a C:/kyty/s288/bin/kyty_emulator_b3cee576.exe
seal: 6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c C:/kyty/scripts/s51_vidglitch.py
