<!-- Mirror of C:/kyty/s123/FACTS.md (source of truth), personal identifiers and foreign application names removed at the close (HPP-33). -->
# Session 123 — FACTS (source of truth; git mirror `docs/local-session-123.md` at the close)

Brief: `C:/kyty/KytyPS5/docs/next-session-123.md`; decisions: `ROADMAP.md` §0.1 "СЕССИЯ 122" item 25 and "СЕССИЯ 123".
Installed build at the start: `d3a981a2…` (item 25 (з)). 60 FPS is not promised.

## Step 0 — harness port and one idle criterion (HPP-23; author: Harness Engineer; not yet accepted by the lead)

No game run in this step (only `nvidia-smi` through `idle123.py`, once: median 7.0, IDLE).

**Ported from `C:/kyty/s122`:** `procload.py`, `launch_run.py`, `run_safety99.py`, `gates_base.txt` byte-identical;
`hostdev123.py` / `test_hostdev123.py` = `hostdev122` renamed (+ default dir), fixtures 87 checks `ALL OK`;
`enter_scene.py` with `ROOT = C:/kyty/s123` and the idle change below. Edit scripts `port123.py`, `patch_enter123.py`
(LF, exact anchors).

**One idle criterion (item 25 (ж), MINOR-2 of audit 122).** In 122 the chain took ONE `nvidia-smi` sample and refused at
`gpu >= 10` (integer), the scorer judged `pre_run.gpu_util_median` (median of 5 samples 0.4 s apart, rounded to 0.1)
at `<= 10`; `skyp122` passed the chain (`gpu=1`) and was refused by the scorer (11). Now:
* `idle123.py` holds the measurement (`sample_gpu`, same query/5 samples/0.4 s/`[N/A]` rule/rounding as the old
  `enter_scene.sample_machine`) and the admission `idle_ok` (text identical to `map122.idle_ok`, `IDLE_GPU_MAX = 10`);
  CLI exit 0 IDLE / 1 BUSY / 2 UNAVAILABLE.
* `go123a.sh` runs `idle123.py` before the lock (instead of its own single sample); the CPU check (< 15) stays as a
  chain-only extra — stricter, never admits what the scorer refuses.
* `enter_scene.py` produces `pre_run` through `idle123.sample_gpu` and, with `--require-idle` (the chain always passes
  it), refuses with exit 3 BEFORE install / clock logger / emulator when `idle_ok` is false; it writes
  `<tag>.refused.json`, never `<tag>.json`. The chain logs rc 3 as "no run". Unavailable NVML = not idle (as the scorer).
* The step-7 scorer must carry an idle check whose body equals `idle123.idle_ok` (fixture `t1` pins it against
  `map122`; the step-7 suite should pin it against `idle123`).

**Chain `go123a.sh`:** tags `smk123` (smoke, `300+1800:KNOB=0|KNOB=1[|CENSUS_ARM]`, 200 s, video), `sky123` (sealed,
ABBA `90+1800:KNOB=0|KNOB=1`, 300 s, video), `ght123` (sealed, only on outcome (ii), own BDA regime), `r` repeats.
`KYTY_GPU_WALL=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` on every run (WALL is process-wide ⇒ both arms);
`KYTY_GPU_CHECKPOINTS` never passed. `procload` + name guard (`mut_[a-z0-9]*123|test_[a-z0-9]*123|mutlib`) before the
checks and again right before the lock and the install. Empty `KNOB/EXPECT/PINNED` (step 3) or `PRED/SC/CHK` (step 7) ⇒
refusal (dry run 02:22:07 logged). After a run: `hostdev123.py`, then `envchk123.py` (PIN=1, WALL=1, MARKERS=0, no
CHECKPOINTS, sealed: ABBA=1 and schedule) → `envchk_<tag>.txt`.

**Fixtures / mutants:** `test_idle123.py` 111 checks `ALL OK` (threshold edge 10.0 admitted / 10.1 refused, rounding
10.04/10.05, even-count median with `[N/A]`, the `skyp122` shape and its mirror, rc≠0 with a numeric row, agreement
with `map122.idle_ok` on a 0–30 grid and on every real s122 json, enter_scene refusal order, chain order and
flags, envchk). `mutlib` v4.1 FULL (`--control --no-memo --work-dir/--cache-dir C:/kyty/s123/mut*`): **23 of 23 killed,
3 of 3 controls survived** (`mut_idle123.txt`).

sha256: `go123a.sh` eca31453…, `idle123.py` 0b50bb6c…, `test_idle123.py` b4b5400d…, `mut_idle123.py` 367ceb8b…,
`envchk123.py` 32910afb…, `enter_scene.py` 68f1e037…, `hostdev123.py` 3f232237….

## Step 6 prep — tail liveness `ft_tail` in `enter_scene.py` (HPP-29, ROADMAP s.122 item 30(v); author: Harness Engineer; not yet accepted by the lead)

* `patch_enter123b.py` (LF, `write_bytes`, anchors once) adds `FtCounter` (own `Tail` from the log start, counts lines
  starting with `FrameTrace:`; an unfinished line counts once it has its newline) and `ft_tail_from_samples`. During
  the hold the count is sampled every `FT_SAMPLE_S` = 0.25 s; at the end of the hold the attempt and top-level
  `<tag>.json` get `ft_total` (count at the end), `ft_tail` (end minus the latest sample at or before end − 5 s,
  `FT_TAIL_WINDOW_S` = 5.0), `ft_tail_span_s` (real span, 5.00–5.25 s), `ft_window_s`. Hold < 5 s ⇒ `ft_tail` = None
  (not evaluable, never 0). Line `hold end: ft_total N, ft_tail M` in the chain output.
* Fixtures `test_ft_tail123.py` 20 checks `ALL OK`: pure function (empty, short hold → None, no growth → 0, boundary
  inclusive, latest old sample, span), counter on a file with a fake clock (only `FrameTrace:` counted, unfinished
  line), four end-to-end `attempt()` holds with a fake emulator writing the log (no game started): live → `ft_tail`
  50; **lead fixture: `FrameTrace:` stops 3 s after launch while other lines continue, hold 8 s → `ft_tail` = 0**;
  hung right after stable → 0 / total 95; hold 3 s → None. `test_idle123.py` re-run after the patch: 111 `ALL OK`.
* Minimum of full ABBA pairs for G2 — set from smoke Д1 and justified in `pred/01` (step 7), not before.

sha256: `enter_scene.py` 68f1e037… → **fc8b0605…** (previous copy `old/enter_scene.pre_ft.py`),
`patch_enter123b.py` 8cdc6ff1…, `test_ft_tail123.py` 5abdda99….

## HPP-30: п. 34(д) — без видео в запечатанном ABBA (2026-09-27, Harness Engineer)
* `go123a.sh`: для запечатанных тегов `RECARG=""` (`KYTY_REC` не передаётся; G12/G15, п. 28(и)); дым `smk123` — по-прежнему `--rec`.
* `envchk123.py --sealed`: новая проверка `no KYTY_REC` (по наличию).
* `test_idle123.py`: c17 (строка запечатанных тегов), c18 (`KYTY_REC` не в коде цепочки), v4a/v4b; 115 проверок `ALL OK`;
  отрицательный контроль (старая строка `--rec` + снятая проверка envchk) — FAIL c17 и v4a.
* sha256: `go123a.sh` f6827a7e…, `envchk123.py` c76ec819…, `test_idle123.py` 1575319d….

## Step 6 prep 2 — цепочка дыма по §7 проекта (HPP-29, ROADMAP s.122 п. 34(д); автор: Harness Engineer; лидом не принято)

* Черновик `smk123` (`300+1800`, три плеча) удалён из `go123a.sh` (тег отказывает: usage, rc 2). Три тега дыма, все
  незапечатанные, Sky Garden, `KYTY_GPU_WALL=1`, `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`, `KYTY_FRAME_TRACE=lite`
  (ставит `enter_scene.py`), `--attempts 2`, `CENSUS_ARM` пуст:
  * `d1s123` — Д1: ABBA `90+1800:skipceil=0|skipceil=1`, удержание 300 с (≈ 40 пар при ~31 fps; ≥ 20 требуется), видео
    (`--rec`), envchk `--wall --abba --rec`;
  * `d2s123` — Д2: постоянный `skipceil=2` гейт-файлом `gates_skc2.txt` (= `gates_base.txt` + ` skipceil=2`; имени в базе
    нет, присваивание единственное), расписания нет, удержание 120 с, видео, envchk `--wall --rec --no-schedule`;
  * `d4s123` — Д4: A/A ABBA `90+1800:skipceil=0|skipceil=0`, удержание 200 с (≈ 25 пар; ≥ 12 требуется), без видео,
    envchk `--wall --abba --no-rec`.
  Старт `1800` — тот же, что у запечатанного `sky123` (ленивые пайплайны тайлера, ловушка с. 73). Запечатанные теги не
  тронуты (правка `HPP-30`: `RECARG=""`). Пустое расписание не передаётся пустым аргументом (`${SCHED:+"$SCHED"}`).
  `DRY=1 go123a.sh <tag>` печатает команду и выходит до любых проверок, замка и установки.
* `envchk123.py`: флаги `--abba`, `--rec`, `--no-rec`, `--no-schedule`; `checks()` сохраняет позиционную подпись.
* `test_idle123.py`: c17 (теперь 4 `RECARG=`), c19–c28 (ветки d1/d2/d4, отказ `smk123`, гейт-файл, DRY), v8a–v8j
  (флаги envchk); **135 проверок `ALL OK`**. Отрицательный контроль (копия харнесса во временной папке): старая цепочка →
  падение на ветках d*, старый envchk → падение на флагах; `ALL OK` нет.
* Порядок дыма: Д1 → Д2 → Д4, каждый — отдельный вызов `go123a.sh`, только на сборке шага 5 (`HPP-28`) после
  обновления `EXPECT`/`PINNED`.
* sha256: `go123a.sh` 2a3b6a39… (прежний `old/go123a.pre_d123.sh` = f6827a7e…), `envchk123.py` b6e574ea… (прежний
  `old/envchk123.pre_d123.py` = c76ec819…), `test_idle123.py` c336f4bf… (прежний `old/test_idle123.pre_d123.py`),
  `gates_skc2.txt` 4b53594a…, патчи `patch_go123b.py` ab671789…, `patch_envchk123b.py` e44bb639…,
  `patch_testidle123c.py` a4ecd48d….

## Step 6 — дым Д1/Д2/Д4 на сборке `e4bb66ca` (HPP-29, проект §7, ROADMAP s.122 п. 34(д), 36(в), 37; автор: Harness Engineer; лидом не принято; ВСЕ ЧИСЛА РАСКРЫТЫ, НЕ ВЕРДИКТ)

Сборка `e4bb66ca…` (установлена = закреплённая, `binary_sha256` в трёх `<tag>.json`). Sky Garden, `KYTY_GPU_CLOCK_PIN=1`,
`KYTY_GPU_WALL=1`, `KYTY_GPU_MARKERS=0`, `lite`. Все три — одна попытка, вход 14,9–16,4 с, `hold_exit` нет, `hostdev`
RUN_CLEAN, `envchk` PASS, фатальных маркеров нет, `AsyncPipelines: skipped draw` 0 во всех трёх, `GpuWaitSlow`/
`PriorityStall`/`GpuIdlePrio`/`GpuHangAbort` 0 строк. Разбор — `smk123.py <tag>` (не скорер; окно позиций 10..87, блоки
по `GateArm:`), выводы `smk_<tag>.txt`. Строк `VideoOutFlipRate:` и `rate =` нет ни в одном логе → интервал флипа игры 1.

**Д1 `d1s123`** (ABBA `90+1800:skipceil=0|skipceil=1`, 300 с, видео): 105 блоков, 104 полных (последний обрезан концом
удержания), **52 полные пары**, выбросов ≥ 0,5 с 0, наибольший `dt_us` 65 235 (кадр 6148, плечо 0), `ft_total` 11 160,
**`ft_tail` 193** (≥ 1 на живом прогоне — замечание Red Team к Н4 снято этим числом).
* Вооружение (G4) по каждому из 52 блоков плеча 1: Т1 точно; Т3 0,498–0,503; Т4 `rpd` 0,487–0,510, `rt_att` 0,476–0,524;
  Т5 0,500 ровно, соседних удержанных строк 0; классы 39/39; |`mark`−`held`| ≤ 1. Т2 за прогон: `mark` = `held` = `skipf`
  = 2 340, `mark_miss` 0. Т6 0,987–1,013 в обоих плечах. G5: вне S_live в окнах плеча 0 — 0. G7: `bad`/`xthr`/`refuse`/
  `mark_miss` = 0. G10: `bda_scan` по блокам плеча 0 48–118 (NEW). G11: `gw_proc_n` > 0 во всех блоках. G12: `gclk_pin`
  > 0 в обоих плечах. `SkipCeil: … held` — 8 строк; `AsyncPipelines: flip … held` — 0.
* По парам (52; среднее, 2SE): **Δ`dt_us` est(0)−est(1) = 11 271,2 ± 143,9 мкс — ПОТОЛОК, НЕ ВЫИГРЫШ, НЕ ВЕРДИКТ**
  (стратифицированное = простое: классы ровно 39/39); Δ`cpu_gpu_us` (1−0) −13 138,8 ± 136,9 (P2: Δ + 2SE < 0);
  Δ`draws` −2,3 ± 13,6; Δ`gw_proc` −13 531,6 ± 146,0 мкс/кадр (P4); **Δ`img_up_kb` −16 068 ± 647 КиБ/кадр**;
  (`rt_kpx`/`rt_att`)₁/(…)₀ − 1 = +0,334 % ± 0,324 %.
* Плечи: `dt` 32 082,6 / 20 811,5; `cpu_gpu_us` 31 121,6 / 17 982,8; `draws` 5 042,4 / 5 040,1; `rt_kpx/rt_att`
  2 007,746 / 2 014,117; `wrm_stalls`/кадр 4,599 / 4,548; на переведённый кадр `img_free` 5,139 / 5,443, `img_new`
  5,143 / 5,421, **`img_up_kb` 99 402 / 166 667**; `skc_gc_hold` в окнах плеча 1 14 258 (3,5/кадр), `gc_crit`/`bgc_crit`
  0; `held_inc` 0 / 0; `ap_skip` 0 / 0; `skc_pres_ns/n` 1 994,9 / 2 054,0 мкс; `flip_hold_ns/n` 2 733,9 / 1 745,8 мкс;
  плечо 0 позиции 0..9 после плеча 1: `img_up_kb` 95 850/кадр.
* LOD по плечам, на кадр (плечо 0 — все 0, счётчики живут только при защёлке ≠ 0): плечо 1 `lod_n` 2,000, `smp0` 0,125,
  **`smp1` 0**, `pmiss` 0, **`pbad` 0,125**, `noanc` 0. K16 по всем строкам после первой `GateArm:` (п. 37(д)):
  `pmiss` 0, `noanc` 0, **`pbad` 572**.
* P3 видео: 8 833 кадра (`.idx`) против Σ`skc_pres_n` 8 821 = 11 161 строк − 2 340 удержанных (+12 — экран подготовки до
  первой строки, с. 115). `s51_vidglitch`: **0 однокадровых глитчей** из 8 833.
* G8(2): плечо 0 Д1 2 007,746 против `sky122` плечо 0 2 007,512 (3 276 строк окна, `C:/kyty/s122/log_sky122.txt`) —
  +0,012 %.

**Д2 `d2s123`** (постоянный `skipceil=2` гейт-файлом `gates_skc2.txt`, строка `Gate: skipceil=2 frame=1`, 120 с, видео):
3 422 строки (кадры 292..3713), `ft_tail` 147; `skc_on` = строкам, `edge` 0.
* Т1 режим 2 точно (`sd` 11 216 662 = `c_dd` 11 199 154 + `keepd` 17 508 + 0). Нули режима 2: `skipf`, `skipd`, `mark`,
  `mark_miss`, `held`, `gc_hold`, `bgc_hold`, `w_xthr`, `bad`, `xthr`, `refuse` = 0. **`skc_lod_pbad` = 854 в окне (858 по
  всем строкам после строки `Gate:`) — НЕ 0** (п. 36(в), 37(в)).
* P5: `c_dd/draws` **0,6239** (не ≈ 0,5); `w_di` 38 221 261; `x1_rd` 5 560; `rc_all` 887 720; `ia` 40 210; `dma_all`
  225 551. P6: `SkcX1Reader:` 24 строки, 6 с `selfw=1` (PS `0x5a34b303576ee324`). P7: `r_g` 14 233. N3:
  `rpd/draws` 0,99615 (Д2) / 0,99603 (Д1 плечо 0) = 1,00012 — не у границы. `AsyncPipelines: skipped draw` 0 (п. 34(д) N3).
* Т7: все неравенства держатся, КРОМЕ `c_df/c_f` = **0,6248** ∉ [0,45; 0,55]. Доли: `x1_wd/c_dd` 0,3201, `x1_wp/c_dp`
  0,0376. Все `rc_*_{d,t}` = 0, `r_c_d`=`r_c_t`=0, `r_m_*`=0, `r_i_*`=0, `r_gds`=0, `ia_d`=0 (`ia_t` 23 954).
  `skc_erase_cmd` 1 190,1/кадр. Строки `SkcCpuRead:` 8, `SkcCpRead:` **0**. `s51_vidglitch`: 0 глитчей из 3 726.
  Полные суммы и средние на кадр всех 59 счётчиков переписи — `smk_d2s123.txt`.

**Д4 `d4s123`** (A/A `skipceil=0|skipceil=0`, 200 с, без видео): 52 блока, 51 полный, **25 пар**, выбросов 0, наибольший
`dt_us` 66 908, `ft_tail` 156. Все `skc_*` вне S_live = 0 во всех окнах и по всему прогону; строк `SkipCeil:`/`Skc*:` нет
(N1). По парам (25; 2SE): Δ`dt_us` −40,6 ± 153,9; Δ`cpu_gpu_us` +47,1 ± 161,5; Δ`draws` +0,4 ± 19,8; **Δ`img_up_kb`
−69,5 ± 239,6**; Δ`gw_proc` +39,4 ± 155,3; **(`rt_kpx`/`rt_att`) отношение − 1: +0,001 %, SE 0,009 % (2SE 0,017 %)** —
SE для G8(1) печати шага 7 (3·SE = 0,027 % < 2 % → порог G8(1) = 2 %). Плечо 0 `rt_kpx/rt_att` 2 007,617 против `sky122`
+0,005 % (< 2,5 %, вопроса нет). `held_inc`/`ap_skip` 0 в обоих плечах.

**Находка (Harness Engineer, факт по логам, не решение).** Опрос LOD в Sky Garden — **не один кадр раз в 16, а 4 кадра
подряд раз в 16**: в Д2 строки с отчётом `sampled ≠ 0` идут сериями 401–404, 417–420, 433–436 (промежутки 1,1,1,13).
Следствия, видимые в логах: (1) режим 2 — каждый из 4 кадров опроса делает `Touch`, якорь A сдвигается на 1 и каждый
кадр серии получает нечётное смещение → помечен пропускаемым (`smp1` 0,25/кадр, `smp0` 0) и `pbad`; доля помеченных
(4 + 6)/16 = 0,625 = `c_df/c_f` 0,6248 и `c_dd/draws` 0,6239; (2) режим 1 — пропущенные кадры `Touch` не делают, поэтому
чётность якоря держится и чередование строгое (Т5), но **2 из 4 кадров каждой серии опроса пропускаются** (в Д1
отчёты `sampled ≠ 0` через 2, 14: исполняются только 2 из 4), т. е. утверждение п. 36(а) «кадр опроса никогда не
пропускается» в Sky Garden не выполняется, а Σ`pbad` = 572 > 0 делает страж п. 37(б) проваленным ПО ПОСТРОЕНИЮ в каждом
запечатанном ABBA.

**Вопросы лиду до печати шага 7** (правила п. 36(в), 37(в); решения не мои):
1. `pbad` > 0 в Д2 (854) и в Д1 (572) — модель «период 16, один кадр опроса» опровергнута (опрос растянут на 4 кадра). Как
   быть со стражем Σ`skc_lod_pbad` = 0 п. 37(б) и с классом K16 в плече 1 (2 из 4 кадров опроса пропускаются)?
2. |Δ`img_up_kb`| Д1 = 16 068 КиБ/кадр > 2SE того же ряда в A/A Д4 (239,6) — правило п. 35(а)/36(в). Знак: плечо 1
   грузит меньше на кадр, но больше на переведённый кадр (166 667 против 99 402).
3. Т7 `c_df/c_f` 0,6248 и P5 `c_dd/draws` 0,6239 вне ожидаемых — следствие находки; режим 2 метит не ту долю, что пропускает
   режим 1 (0,5), и перепись Д2 описывает другое множество кадров.

**Минимум пар для G2(2)** (вписывается в `pred/01` шага 7): Д1 при удержании 300 с и старте 1800 дал 52 полные пары без
снятий. Предложение — **48** (52 − 4 ≈ −8 %: запас на разброс входа 14,9–16,4 с и темпа плеч; зависон ≥ 5 с отдельно ловят
G2(1) и G2(3)); окончательно — строкой в печати.

sha256 (первые 16): `smk123.py` c2883726…, `smk_d1s123.txt` b2106a8a…, `smk_d2s123.txt` e42b4371…, `smk_d4s123.txt`
2c15f418…, `log_d1s123.txt` df09435a…, `log_d2s123.txt` dca2065f…, `log_d4s123.txt` ce0c0926…, `rec_d1s123.mp4`
373053b1…, `rec_d2s123.mp4` 71a17c1b…, `d1s123.json` 70e66795…, `d2s123.json` 0b11ab20…, `d4s123.json` ce7e902d….
Выводы `vidglitch_d{1,2}s123.txt`. Замка во время разбора не было; игра запускалась только тремя вызовами `go123a.sh`.

## Step 7 — скорер `skc123.py`, фикстуры, печать `pred/01_skc123.md`, один полный `mutlib` (HPP-30, ROADMAP s.122 п. 25(г)–(е), 26(б), 28–38; автор: Harness Engineer; лидом не принято; игра не запускалась)

* **Печать** `pred/01_skc123.md` sha256 `e6bf581f…` (16 019 Б, LF): чтение п. 25(г) (Δ + 2SE < 500 → CLOSED; Δ − 2SE ≥ 500 →
  CEILING_MEASURED; иначе NOT_RESOLVED), окно 10..87, стратифицированный оценщик плеча 1, пол 24 пары после снятий,
  снятие пары при кадре ≥ 0,5 с, > 2 снятых — недействителен; таблица стражей G1–G16 принятого проекта (п. 32(г)) с
  п. 35(в) (G7 + `mark_miss`), 36(в)/37(д)/38(в) (K16: `pmiss`, `noanc`; страж `pbad` СНЯТ — ряд), 38(г) (ряд G14),
  §4.4 (перепись = 0 в плече 1 — гейт `census_arm1`); строка цепочки п. 34(д) дословно; восемь «прочтений реализации»
  на приёмку лида (ни одно не ослабляет стража).
* **Опорные числа** (`ref123.py` → `ref123.txt`, свой парсер): база G8(2) `sky122` 82 147 691 183 / 40 920 142 =
  2 007,512368 (3 276 строк); `ght122` 84 848 760 392 / 43 632 189 = 1 944,636800 (4 446 строк); SE Д4 отношения
  0,00008586 (25 пар) ⇒ порог G8(1) 2 %; минимум G2(2) = 48 полных пар (Д1: 52).
* **Скорер** `skc123.py` sha256 `4991b95e…` (`PRED_SHA`/`PRED_BYTES` заполнены). Черновой разбор Д1 воспроизводит `smk123`
  до цифры: Δ 11 271,2 ± 143,9 мкс, 52 пары, Δ`cpu_gpu` −13 138,8, пост-ряд 0,964, K16 `pbad` 572; отказ Д1 — только
  `env_exact`/`env_forbidden` (`KYTY_REC`).
* **Фикстуры** `test_skc123.py` sha256 `9cdcafbf…`: **264 `ALL OK`** (267 с `--real`: Д1/Д2/Д4).
* **Мутанты** `mut_skc123.py` sha256 `78a063da…`: черновой полный прогон (незапечатанный текст) — 349, 23 выжили →
  2 мёртвых условия убраны из скорера, 2 эквивалентны (записаны), 19 убиты новыми фикстурами. **ЗАЧЁТНЫЙ единственный
  полный прогон на окончательном тексте: 346/346 убиты, 0 выживших, 0 неразрешённых, контроли 3/3 выжили**
  (`mut_skc123.sealed.txt` `b279490e…`, 479 с, 28 воркеров).
* Доказательства `checks/skc123_checks.json` (`mk_checks123.py`); шлюз `chk_skc123.py --tag sky123|ght123|ght123r` —
  PASS, незапечатанный тег — REFUSED. `go123a.sh` → `PRED`/`SC`/`CHK` заданы, sha256 `580adc03…` (прежний —
  `old/go123a.pre_hpp30seal.sh`); `test_idle123.py` 135 `ALL OK`. `SEALS123.txt` — sha256 всех 24 файлов печати.

## Step 8 — запечатанный ABBA `skipceil=0|1`: опора `sky123` и `ght123` (HPP-31, ROADMAP s.122 п. 25(г)–(д), 38(д); автор: Harness Engineer; лидом не принято)

* **Условия.** Сборка `e4bb66ca907bf7a7…` (установлена = закреплённая копия `kyty_emulator_e4bb66ca.exe`); цепочка
  `go123a.sh <тег>` (печать `pred/01_skc123.md` `e6bf581f…`, скорер `skc123.py` `4991b95e…`, шлюз `chk_skc123.py` PASS:
  264 фикстуры, 346/346 мутантов); ABBA `90+1800`, удержание 300 с, одна попытка; `KYTY_GPU_WALL=1` в обоих плечах,
  `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`, без `KYTY_GPU_CHECKPOINTS`, **без видео** (п. 34(д), G12/G15; указание
  лида `7a2f141c`). Перепись В8 не прогонялась (перенесена в с. 124, п. 38(д)). Оба прогона под замком
  `C:/kyty/SEALED_RUN.lock`, на переднем плане; `procload` чист перед замком и установкой, `idle123` IDLE, `hostdev`
  RUN_CLEAN, `envchk123` PASS.
* **Первая попытка `sky123` (06:15–06:25)** не стартовала: шлюз `procload` 10 мин показывал стороннюю нагрузку CPU
  (2,8–4,3 с/с); цепочка остановлена в ожидании, замок не брался, эмулятор не запускался (строка в `go123a.log`).
  Прогон `sky123` — первый и единственный запуск игры под этим тегом (06:30:38–06:36:03).
* **`sky123`** (`underwater_aerial_garden`, вход 15,4 с): **ADMITTED**, 103 блока / 102 полных, **51 пара** (G2 ≥ 48),
  снятых пар 0. **Δ`dt_us` est(0) − est(1) = 11 384,3 ± 132,7 мкс (2SE)** — Δ − 2SE = 11 251,6 ≥ 500 ⇒
  **CEILING_MEASURED**; est A 32 471,2, B 21 086,9 мкс. G9 ряд: Δ draws −2,3 ± 12,2, с поправкой 11 369,7 ± 113,6.
  G4: Δ`cpu_gpu_us` −13 195,2 ± 129,0. G7 нули; T2 mark 2317 / held 2316 / mark_miss 0; K16 `pbad` 566 (ряд). G8 ratio−1
  0,00072, к базе `sky122` 0,00023. **G10: BDA OLD** (`bda_scan` плечо 0 1 489,8 / плечо 1 1 073,0 на кадр) — у
  `sky122` был NEW; ожидаемого значения печать не задаёт, это ряд. G11: GuestGpu `proc` 32 421 → 18 781 мкс/кадр,
  `idle` 30 → 2 181. G14 ряд: `img_up_kb` на переведённый кадр 101 076 (плечо 0) / 220 724 (плечо 1).
* **`ght123`** (`time_stopper_ghost_world`, вход 14,4 с; запущен по CEILING_MEASURED опоры, п. 25(д)): **ADMITTED**,
  143 блока / 142 полных, **71 пара**, снятых 0. **Δ`dt_us` = 8 076,7 ± 77,0 мкс (2SE)** ⇒ **CEILING_MEASURED**
  (Δ − 2SE 7 999,7); est A 24 749,4, B 16 672,7. G9: Δ draws +25,5 ± 6,9, с поправкой 8 247,4 ± 89,0. G4: −10 396,2 ± 63,5.
  **BDA OLD** (1 128,8 / 951,2) — тот же режим, что у `ght122` (OLD), оценка в своём режиме. G8 ratio−1 0,00358, к базе
  `ght122` −0,00008. G11: `flip` плеча 1 2 241 мкс/кадр (у Sky Garden 17). G14 пост-ряд 0,823 (Д1 0,964).
* **Прочтение (печать, п. 25(г)(ii)):** число — ПОТОЛОК грубой ручки (картинка может деградировать), не выигрыш и не
  прогноз; скорость игры под ручкой не цитируется (G16). Следствие по печати — проект корректной версии в с. 124, объём
  решает перепись корректности.
* sha256 (первые 16): `log_sky123.txt` 30c8b4eb…, `log_ght123.txt` 06d155f0…, `score_sky123.txt` 7470ff46…,
  `score_ght123.txt` 1530baf2…; `sky123.json`/`ght123.json`, `hostdev_{sky,ght}123.txt`, `go123a.log`.

## Step 9 — audit (HPP-32; author: Session Auditor; not yet accepted by the lead)

`C:/kyty/s123/audit123/AUDIT123.md` (git `docs/session-123/audit/`). Game not started by the auditor; no lock during the audit.
* **Recount CONFIRMED** by an own parser (`recount123.py`, no code shared with `skc123.py`/`smk123.py`/`ref123.py`): `sky123`
  Δ`dt_us` 11 384,3 ± 132,7 мкс (51 пара), `ght123` 8 076,7 ± 77,0 (71) — до последней цифры, оба CEILING_MEASURED; все ряды
  G4/G7/G8/G9/G10/G11/K16/Т2/Т5 совпадают. Бутстрэп [11 254,7; 11 512,9] / [8 006,0; 8 155,8]; окно 10..88 — 11 364,4 / 8 088,0.
* **1 MAJOR / 6 MINOR, вердикты не меняются.** MAJOR-1: тик рутины «Сторож цикла» (ран лида `f942e011`, `chain_check.py
  --repair`, запись `HPP-54`) 06:40:06–06:40:29 внутри замка `ght123` (06:37:42–06:43:08) — нарушение п. 25(ж); текст рутины
  всё ещё разрешает «проверку во время запечатанного прогона». Без задетых пар Δ `ght123` 8 051,7 ± 69,8 (±0 с) … 8 053,0 ±
  72,3 (±15 с). MINOR: полосы G10 300/600 без строки ROADMAP; база G8(2) `ght122` в печати раньше п. 39(в) (не ослабление:
  с базой `sky122` 3,14 % < 5 %); черновой полный `mutlib` при разработке (п. 19(б)); `procload --wait-s 1800` > 600 с
  (первая попытка ушла в фон, п. 21); GPU 6–7 % перед `sky123`; `runs123/` пуст (нет `--out`).
* **НЕ доказано:** выигрыш; потолок в режиме NEW (опора шла в OLD); у `ght123` est B 16 672,7 ≈ вблэнк — Δ усечён, «60 кадров/с»
  не частота игры; критичность GuestGpu (Δdt/Δcpu_gpu 0,863 / 0,777 — наблюдение); картинка (видео нет); K16 (`img_up_kb` на
  переведённый кадр ×2,18); цена ручки при 0 против `d3a981a2`.

## Close (step 10, HPP-33, Roadmap Lead, 2026-09-27)

*Author: the lead.* Decisions: `docs/ROADMAP.md` "СЕССИЯ 122" item 40 (written and committed `aa3e176` before any action
on it).

* **Audit accepted** (recount CONFIRMED by an independent parser, 1 MAJOR / 6 MINOR, no sealed verdict changes).
* **Verdict (seal, not rewritten):** `sky123` (Sky Garden, BDA OLD, 51 pairs) Δ`dt_us` 11 384.3 ± 132.7 µs; `ght123`
  (OLD, 71 pairs) 8 076.7 ± 77.0 — both CEILING_MEASURED (item 25 (г)(ii)). A ceiling of the crude knob, never a gain or a
  forecast. Not proven: the NEW-regime ceiling; `ght123` est B ≈ one vblank (Δ truncated, not the game's frame rate);
  GuestGpu criticality; the picture; K16 in arm 1 is an approximation; the knob's cost at 0 against `d3a981a2`.
* **Lever of session 124 (item 40 (б)–(в)): a CLOSURE census, not a prototype.** Mode 2 marking fix (item 38 (д)) and a
  new mode 3: for every marked frame, the set of its draws/dispatches whose output reaches something observable (guest
  CPU/CP reads, GDS, LOD reports — the whole poll series, reads in the next unmarked frame before overwrite); output
  `f_free` (draws outside the closure) with a proven direction. Reading: U = 11 517 µs × `f_free`⁺; U < 500 µs closes
  frame skipping by census; U ≥ 500 µs → a prototype of the correct version with a verify mode and a sealed ABBA in 125;
  direction not proven upper → NOT_RESOLVED. Count share vs time share must be resolved by the design. U is never quoted
  as a gain. One sealed census run on the reference, BDA regime quoted with every number.
* **Installed build restored to `d3a981a2…`** (item 40 (г)); `e4bb66ca…` (knob `skipceil`, default 0) stays pinned at
  `C:/kyty/s123/kyty_emulator_e4bb66ca.exe`.
* **MAJOR-1 closed (item 40 (д)):** the routine "Сторож цикла KytyPS5" is PAUSED (the `HPP-3` watchdog had fired and was
  verified); I12, `--repair` and their fixtures are removed from `chain_check.py` (`--selftest` 24 fixtures `ALL OK`).
* **Harness constants from MINOR-1..6 (item 40 (е)):** BDA bands NEW ≤ 300 / OLD ≥ 600 `bda_scan` per frame (arm 0 block
  mean); a DRS base for a scene outside the design is a ROADMAP line before the seal; full `mutlib` only as the scoring run;
  `procload` wait ≤ 540 s per call; GPU load during the hold as a row; scorer `--out` archived.
* **Debts parked in §7:** NEW-regime ceiling; mode-2 marking and the closure; K16 in the contract; `skipceil=0` cost vs
  `d3a981a2`; `img_up_kb` per translated frame ×2.18; GPU load during sealed runs. 60 FPS is not promised.
