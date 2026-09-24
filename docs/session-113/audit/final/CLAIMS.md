# Session 113 final audit — CLAIMS lens (ROADMAP §0.1 "СЕССИЯ 113", items 11–21)

Auditor: adversarial, read-only (no game run, no build, no git write). Every log was read by streaming Python in `rb`.
Helper scripts and raw scan outputs: `C:/kyty/s113/audit113/final/claims/` (`scanslow.py` → `scan_new.txt`,
`scan_old.txt`; `mem.py`). Each item's claims were checked against score outputs (`runs113/*_score.*`), chain logs
(`go113*.log`), run meta (`<tag>.json`), logs (`log_<tag>.txt`), mutation tallies (`mut_*.out.txt`,
`s106_stage/mutlib/ACCEPTANCE*.md`, `accept2/`, `review3/out/`), `SEALS113.txt` and the source at the commit named.

**Verdict keys:** SUPPORTED · UNSUPPORTED · WRONG (correct value given) · OVERCLAIM (the claim is stronger than the evidence).
**Severity:** MAJOR only if a deciding number or a verdict is misstated. **None found.** Every deciding number (01f GO; 02 KEEP;
Δ`dt` −83.2 ± 68.0 at 2·SE; S1 FAIL, S2 PASS) recomputes exactly.

## Summary of findings

| # | item | finding | verdict | severity |
|---|---|---|---|---|
| F1 | 17 (+ seal 02 §7) | "сегодня OLD выпал 1 раз из 6": the same item names **seven** entries of the day (vbn113, b, c, g, h, i, j) — six NEW plus one OLD | WRONG → **1 of 7** (≈ 14 %) | MINOR |
| F2 | 17 (+ seal 01e §0/§1) | "шесть NEW-входов 8 856–9 072 МиБ"; "все занятости NEW-входов ≥ 8 856 … с запасом ≥ 580 МиБ" | WRONG → post-load heap-0 usage of the six NEW entries is **8 661–9 072 MiB** (`vbn113g` 8 661 at n=599, `vbn113` 8 666 at n=599 and 8 746 at the end); margin above the shifted trigger 8 272 MiB is **≥ 389 MiB**, not ≥ 580. Forced OLD engaged anyway (k, m) — non-deciding | MINOR |
| F3 | 18 | "22 прежних GpuWaitSlow (сессии 80–98) — при загрузке" | WRONG in part → 22 files, but `trig98a` and `trig98a_a1` are one event (identical line) ⇒ 21 events; **3 are mid-run, not at load** (`rv97a` n≈6470/225 s, `rv97a_warmup` n≈5750/200 s, `rv97b` n≈4870/164 s); all 22 are followed by `GpuHangAbort` (true hangs). `requested < current` holds in all 22 | MINOR |
| F4 | 18 | "(приоритетная операция — прерывание, данные загрузки — поставлена в буфер, который **никто не подаёт**)" | OVERCLAIM → the kind of the priority operation is not observed (the line names no site; the instrument added after never fired); "nobody submits" is contradicted by the wait ending after 2.975 s (row n=9673 has `submits=7`, ticks advance). Correct: "not submitted for ≈ 3 s" | MINOR |
| F5 | 18 | "semwait 2,975 с" given for frame 9 672 | imprecise → row n=9672 has `semwait_us=53393`; the 2 975 432 µs wait is booked in row **n=9673** (`FrameTrace-wait: other=2977138/2`, `semwait_gpu_us=0`) | MINOR (cosmetic) |
| F6 | 17 | "⇒ H2 (число блоков после загрузки — случай)" | OVERCLAIM → H3 (budget) is refuted (15 235 MiB in all seven), but "the block count after the load is chance" is asserted, not shown (no block counts, no repeat design); the gap is 315–898 MiB (1.2–3.5 blocks), "≈ 2 блока" is loose | MINOR |
| F7 | 19 | "Режим 1 в принудительном OLD **этой сцены** не пропустил бы ни одной синхронизации" | OVERCLAIM → evidence is one 300-s entry (`vbn113m`); seals 01d–01f §7 allow only "bounds the synchronizations mode 1 would skip **in this run**"; the check is blind to the `bdastamp` shared-region hole (01e §6) | MINOR |
| F8 | 21 | "стоит ≈ 83 мкс на кадр … — **меньше планки** отгрузки" | OVERCLAIM → the point estimate is below the bar; the cost is not shown to be: 2·SE interval of the saving is **15–151 µs**, straddling 100. S1 fails as a rule, which is all KEEP needs | MINOR |
| F9 | 21 | "вклад в среднюю скорость игры был бы ≈ 83 × доля OLD (**≤ 0,27 %** в OLD)" | arithmetic SUPPORTED, wording OVERCLAIM → 0.27 % = 83.2 / 30 540.7 (relative speed change, `dt0/dt1 − 1`, mean `dt` 30 623.9 µs) — the right denominator; using 16 667 would give 0.50 %, wrong. But (a) "≤" turns a point estimate into a ceiling: the 2·SE band is **0.05–0.50 %**; (b) the figure carries neither "pinned GPU clock" nor "forced OLD" (seal 02 §8: no game-speed figure for the unpinned default setup; the label must say forced OLD). In absolute terms the speed moves 54.42 % → 54.57 % of real time (+0.15 points) | MINOR |
| F10 | 13 | "раннее выполнение проверок УБРАНО (замер: без него 147 с против 170 с на выборке)" | OVERCLAIM (misleading evidence) → the 146.6 / 170.2 s are baseline-bound **walls** of a 20-mutant subset; the same table (`ACCEPTANCE.md` §5) shows mutant time **1 507 s vs 807 s** (hoisting halves the cost). `ACCEPTANCE_V2.md` finding 1 confirms v2 is **1.63× (net112) / 1.74× (shn113) slower than v1**, and item 7's target (≤ 10 min) is met by neither. Item 15 quotes v2 walls only against the old harness and does not record this | MINOR |
| F11 | 13 | "приёмка ПРОЙДЕНА на всех шести наборах — каждый мутант получил **прежний** вердикт" | OVERCLAIM (small) → `vbn113c` had **no** prior run ("never run", `ACCEPTANCE.md` table; `s113/mut_vbn113c.out.txt` is 0 B); only `bad_race` and two positive controls were rerun by an independent runner | MINOR |

Everything else in items 11–21 is SUPPORTED (table below). Additional observations outside items 11–21 are at the end.

## Item-by-item table

| item | claim | evidence | verdict |
|---|---|---|---|
| 11 | `vbn113c`: seal 01c `e1424e67`, 300 s, pin, build `7d9fa028`, admitted | `SEALS113.txt` (01c `e1424e67…`), `go113c.log`, `vbn113c_score.stdout.txt` (errors none) | SUPPORTED |
| 11 | first entry already OLD, `bda_scan` median 1 066 | `go113c.log` (one entry); score: levels `bda_scan` 1066.0, regime OLD | SUPPORTED |
| 11 | INVESTIGATE; `bda_nwould` 13 790 740 (1 428 a flip), `bda_nmiss` 0, `bda_nxthr` 0, `bda_nrace` 3 | score: 13 790 740 / 1427.908 per row; 0; 0; 3; VERDICT INVESTIGATE | SUPPORTED |
| 11 | `bda_ginv_reg` 1.40, `bgc_evict` 1.51 a flip; B1–B6 HIT (B2 1 066) | score: 1.404, 1.509; B1–B6 HIT | SUPPORTED |
| 11 | "три гонки на 13,8 млн проверок" | 3 races over 13 790 740 would-skip regions | SUPPORTED |
| 12 | set sizes net112 277, vbn113b 41, shn113 310, vdg112 36, check112 24; slow `vbn113c` run stopped | `ACCEPTANCE.md` table; `s113/mut_vbn113c.out.txt` 0 B | SUPPORTED |
| 13 | v1 sha `db8703bd` | `sha256 mutlib_v1.py` = `db8703bdf082…` | SUPPORTED |
| 13 | accepted on all six sets, each mutant the old verdict | `ACCEPTANCE.md`; `vbn113c` had no old verdict | OVERCLAIM (F11) |
| 13 | first failing fixture equal at 587 of 587 (net112 + shn113) | 277/277 + 310/310 | SUPPORTED |
| 13 | net112 13 min vs ~1 h 45; shn113 20 min vs ~3 h; small sets seconds | 778 s; 1 186 s; 3.0–21.1 s | SUPPORTED |
| 13 | `vbn113c` one real survivor `bad_race` (no B1 fixture with races) | `ACCEPTANCE.md` §4, `accept/ref_one.py` | SUPPORTED |
| 13 | two adversarial reviews: no false verdict in accepted runs; 7+2 false-kill holes | `REVIEW_60857009.md` (7 MAJOR), `REVIEW_1e4c88d5.md` (two hoisting holes); both say accepted results stand | SUPPORTED |
| 13 | "без него 147 с против 170 с на выборке" | `ACCEPTANCE.md` §5: wall 146.6 vs 170.2 s, but mutant time 1 507 vs 807 s | OVERCLAIM (F10) |
| 14 | writer sets bits and moves epochs under the region lock ⇒ bits + stamp are one snapshot | `memoryTracker.cpp:193-219` (stamp read under `manager->lock`), writers `:221-227`, `memoryTracker.h:141-146, :182-191` under the lock (spot check; code lens is another auditor's) | SUPPORTED (spot-checked) |
| 15 | v2 sha `877eb53a…`; v1 kept as `mutlib_v1.py` | `sha256 mutlib.py` = `877eb53a9d93…` | SUPPORTED |
| 15 | check112 24/24, vdg112 36/36, vbn113b 41/41, vbn113c 42/43 (`bad_race`), net112 277/277 21 min with memo / 33 min without (was 1 h 45), shn113 310/310 34 min (was ≈ 3 h) | `ACCEPTANCE_V2.md` summary: 1 267.7 s, 2 006.6 s, 2 062.6 s; ≈ 6 300 s / ≈ 10 800 s | SUPPORTED (omits the v1 comparison, F10) |
| 15 | counterexamples 44 of 46 equal; K stricter, I encoding note; E/E2 refused | `ACCEPTANCE_V2.md` §1 | SUPPORTED |
| 15 | review3 MAJOR-1, MAJOR-2, 6 MINOR | synthetic triples `review3/*.py`, `out/review3_compare.txt`; no written review3 report archived (the classification exists only in ROADMAP) | SUPPORTED as far as archived (provenance gap) |
| 15 | no trigger form in the six sets nor in any of 61 mutant scripts | `review3/out/scan_six.txt` (no other tuple lists, no path-leak candidates); `scan_mut_scripts.txt` 61 rows, "other lists" none everywhere (the MINOR skip-filter form exists in `mut_vdg112`, `mut_vbn113c_hold` — the safe-direction MINOR the item lists) | SUPPORTED |
| 16 | the anchor for the B1-race fixture was a PREFIX of `test_vbn113c.py:185`; `(dict(nmiss=1),'B1',False)` went into a comment | `test_vbn113c.py:185`; `test_vbn113d.py:186` (the edge sits after `#`); restored `test_vbn113e.py:199` | SUPPORTED |
| 16 | mutants of the sealed copy through v2 `--control --no-memo`: 43/43, controls 3/3, "defined" 43 = 43, 36 s | `mut_vbn113d.out.txt` (wall 36.0 s, memo off), hashes = SEALS113 | SUPPORTED |
| 17 | `vbn113g…j` all admitted, all NEW (`bda_scan` 52–54) ⇒ NOT_EVALUABLE ×4 | scores g/h/i/j: 52, 52, 52, 54; `go113d.log` | SUPPORTED |
| 17 | Σ `bda_nwould` 2 350 457, `bda_nmiss` 0, `bda_nxthr` 0, `bda_nrace` 0, `bda_ginv_reg` 2 349 (≈ 0.06 a frame) | 589 457 + 590 438 + 589 112 + 581 450; 588 + 590 + 589 + 582; 0.058–0.061 per row | SUPPORTED |
| 17 | heap budget equal in all seven entries, 15 235 MiB ⇒ GC trigger 9 296 MiB | `MemStats: heap=0 … budget=15975055360` in all seven logs; `BufferGc: budget=14901313536` (= 15 235 − 1 024 MiB) and code `bufferCache.cpp:402-418`: 14 211 − 4 915.2 = 9 295.8 | SUPPORTED |
| 17 | OLD entry `vbn113c` 9 387–9 559 MiB | `log_vbn113c` MemStats heap 0: 9 387 … 9 559 | SUPPORTED |
| 17 | six NEW entries 8 856–9 072 MiB | vbn113 8 666–8 874, b 8 860–9 005, g 8 661–8 870, h 8 906–9 072, i 8 887–9 051, j 8 856–9 002 | WRONG (F2): 8 661–9 072 |
| 17 | "(≈ 2 блока VMA)" ⇒ H2 (chance) | gap 315–898 MiB | OVERCLAIM (F6) |
| 17 | "сегодня OLD выпал 1 раз из 6" | seven entries, one OLD | WRONG (F1): 1 of 7 |
| 17 | shift 1024 ⇒ trigger 8 272 MiB; margin ≥ 580 MiB above all NEW usage; critical 12 573 | `BufferGc: trigger=8673610957` (8 271.8 MiB), `critical=13183326618` (12 572.6 MiB); margin 8 661 − 8 272 = 389 | trigger/critical SUPPORTED; margin WRONG (F2) |
| 17 | GC runs by the same path (160 ticks, ≤ 32 a call) — the same OLD mechanism | forced runs reproduce natural-OLD rates: `bda_ginv_reg` 1.399 (k) / 1.155 (m) vs 1.404 (c); `bgc_evict` 1.511 / 1.365 vs 1.509 | SUPPORTED (labelled "принудительный OLD") |
| 18 | `vbn113k`: forced OLD worked (`bda_scan` 1 064, `BufferGc … trigger=8673610957 … shift_mb=1024`, `bgc_evict` ≈ 1.5) | `vbn113k_score.stdout.txt`; log line 606 | SUPPORTED |
| 18 | BAD 0 (Σ `bda_nwould` 13 893 695, `bda_nmiss` 0, `bda_nxthr` 0, `bda_nrace` 3), all six predictions HIT, NOT_ADMITTED by `NO_MARKER` | score: errors ['NO_MARKER'], values as stated | SUPPORTED |
| 18 | one `GpuWaitSlow` at 308.9 s, frame 9 672, `dt` 3.03 s | log line 1 257 662 at `[00:05:08.913]`; the only one in the log; row n=9672 `dt_us=3032310` | SUPPORTED |
| 18 | `semwait` 2.975 s | `semwait_us=2975432` in row **n=9673** (row 9672 has 53 393) | imprecise (F5) |
| 18 | GPU utilisation 0 % 20:29:13.9–20:29:15.9 | `gpuclk_vbn113k.csv` rows 615–619: 0 % at 13.904 … 15.938 | SUPPORTED |
| 18 | `role=4` = a thread outside the roles | `frameStats.h:1914` `enum class ThreadRole { Main, Gpu, Present, Record, Count }` — 4 = Count = unregistered | SUPPORTED |
| 18 | by the code the only such waiter of the `MasterSemaphore` is the priority-operation thread (`commandScheduler.cpp:619`) | `git show e344e34`: line 619 `m_master.Wait(operation.tick)`. Every other `m_master.Wait`/`scheduler.Wait` path either submits first or waits on `CurrentTick()−1` (requested < current), or runs on a registered thread; the only other unregistered waiter (`bufferCache.cpp:500`, guest read) needs `KYTY_STALE_READ=0` and books site `download-guest` — row 9673 books `other`; `semwait_gpu_us=0` | SUPPORTED as an inference by elimination (never observed: the instrument added afterwards did not fire) |
| 18 | `requested` = `current` = 329 576, `known` 329 575, submit history ends at 329 575, submit queue empty ⇒ the waited tick was not yet submitted | GpuWaitSlow line; the 512-row `GpuSubmitHistory` block ends `tick=329575 phase=returned`; `submit_backlog=0 record_backlog=0`; `MasterSemaphore::NextTick` (`masterSemaphore.h:26`) — current = next unsubmitted | SUPPORTED |
| 18 | "(… прерывание, данные загрузки — поставлена в буфер, который никто не подаёт)", GPU idle | GPU idle SUPPORTED; operation kind unobserved; the tick was submitted ≈ 3 s later | OVERCLAIM (F4) |
| 18 | 22 earlier `GpuWaitSlow` (s. 80–98) at load, `requested < current`; none in 94 logs of s. 104–113 | own scan of 170 logs s80–s99 and 97 logs s104–s113 (`claims/scan_*.txt`): 22 files (21 events), all `requested < current`, all role 4, all followed by `GpuHangAbort`; 3 mid-run; in s104–s113 only `vbn113k` (94 = 86 + 8 s113 logs at the time) | count SUPPORTED; "at load" WRONG in part (F3) |
| 18 | GC-path suspicion (`graphicsRun.cpp:1002–1007`, `:1037–1042`, `textureCache.cpp:2914`, `:685`) — "НЕ доказано"; link to the shift not established | at `e344e34`: `RunGarbageCollector` at 1006 and 1041 in the `else if (complete)` branches; `DeferPriorityOperation` at 2914; `m_work_available.Wait` at 685; `RenderContext::RunGarbageCollector` → `ProcessDownloadImages` (`renderContext.cpp:410`) | SUPPORTED (correctly hedged) |
| 19 | `vbn113m` admitted, forced OLD (`bda_scan` 1 064, `shift_mb=1024`), Σ `bda_nwould` 11 845 121, `bda_nmiss` 0, `bda_nxthr` 0, `bda_nrace` 0, all seven predictions HIT, GO | `vbn113m_score.stdout.txt`, `go113f.log`, log line 606 | SUPPORTED |
| 19 | the stall did not recur (`prio_stall` 0, `gw_idle_prio` 0); `prio_unsub` 5.67 a frame — waits on the unsubmitted tick are common and short | score: 0, 0, 5.666; my scan: no `GpuWaitSlow`, `PriorityStall:` or `GpuIdlePrio:` in `vbn113m`, and none in `shn113` (600 s) or `vid113` either | SUPPORTED (one 300-s entry) |
| 19 | "Режим 1 в принудительном OLD этой сцены не пропустил бы ни одной синхронизации" | one entry | OVERCLAIM (F7) |
| 19 | seal-02 set-up: build `1678d3f4`, shift in both arms and video, `bda_ginv_reg` in forced OLD median 1, mean 1.16–1.40 | `shn113.json` env carries the shift; `log_shn113` `BufferGc … shift_mb=1024`; per-row means 1.155 (m) and 1.399 (k) | SUPPORTED |
| 20 | v2 refused the two `CONST_pred_*_prefilled` mutants (anchors `PRED_SHA = None`/`PRED_BYTES = None`); sealed set = all others, exactly two removed | `mut_shn113.py:341-342`; `diff` → exactly those two lines; sealed `shn113.py:55-56` filled, draft `shn113b/shn113.py:55-56` None; hashes in SEALS113 | SUPPORTED (the refusal output itself is not archived) |
| 21 | mutants 315/315 on the sealed copy (controls 3/3) and 2/2 on the draft | `mut_shn113.out.txt` ("315 of 315 … 315 defined", memo off), `mut_shn113_draft2.out.txt` ("2 of 2 … 317 defined") | SUPPORTED |
| 21 | `shn113` admitted: 98 pairs, all integrity/control/arming PASS; `bda_scan` levels 1 438 / 49.6; arm-1 `bda_nskip` 1.37; `bda_nwould`/`bda_nmiss`/`bda_nxthr` 0 | `shn113_score.stdout.txt` (all [PASS], pairs 98, [1438.38, 49.62], P6 1.369, 0/0/0) | SUPPORTED |
| 21 | Δ`dt` −83.2 ± 68.0 µs (2·SE, t −2.45, n 98); Δ`cpu_net` −83.9 ± 60.6; Δ`gpu_busy` +5.9 ± 23.8; secondary −28.6 ± 119.2 | recomputed from `shn113_score.json` pairs: mean −83.23, SE 34.00 (2·SE 68.00), t −2.448; cpu_net SE 30.29; gpu_busy SE 11.92; secondary SE 59.60. Robustness: median pair Δ −106.7, 10 %-trimmed mean −81.1, 58/98 pairs negative | SUPPORTED (the "±" are 2·SE) |
| 21 | S2 met, S1 (≤ −100) not ⇒ KEEP; video not needed; P1 MISS (1 438 > 1 400), P4 MISS, others HIT | score: S1 FAIL, S2 PASS, VERDICT KEEP; P1/P4 MISS, P2/P3/P5/P6/P7 HIT | SUPPORTED |
| 21 | the extra full walk "стоит ≈ 83 мкс на кадр в принудительном OLD — меньше планки" | 2·SE band 15–151 µs | OVERCLAIM (F8) |
| 21 | mode 1 verified (01f, 0 misses on 11.8 M) | Σ `bda_nwould` 11 845 121, `bda_nmiss` 0 (`vbn113m`) | SUPPORTED |
| 21 | contribution ≈ 83 × share of OLD (≤ 0.27 % in OLD) | 83.2 / 30 540.7 = 0.272 %; band 0.05–0.50 %; unlabelled pin / forced OLD | arithmetic SUPPORTED; OVERCLAIM (F9) |
| 21 | `1678d3f4` stays installed; behaviour defaults = `b47b58a9` | installed exe sha `1678d3f4…`; `vid113`/`check113` PASS (`narrow_default_dark`, `gc_default` shift 0, 3 976 frames, 0 glitches) | SUPPORTED for the knob defaults (note: `ChangeRegister<insert>` marks its regions at every knob value — redundant at 0, and no timing A/B of `1678d3f4` against `b47b58a9` exists; do not read "same defaults" as "same speed") |

## Answers to the brief's specific questions

* **(a) Stall analysis (item 18).** The facts hold: role 4 = unregistered thread; `requested = current` = the recording
  tick not yet submitted (async-submit and record backlogs 0; history ends one tick earlier); GPU idle 2 s by
  `nvidia-smi`. Attributing role 4 to the priority-operation thread is an inference by elimination. It is strong (every
  other waiter either submits first or runs on a registered thread, and the booked site is `other`), but it was never
  observed. The GC-path suspicion is correctly labelled "НЕ доказано". What goes beyond the evidence is the parenthesis
  on the operation kind and "которую никто не подаёт" (F4). The archive comparison is partly wrong (F3).
* **(b) Item 21 size and 0.27 %.** −83.2 ± 68.0 is a correct 2·SE (SE 34.0). Game speed = 16 667 / mean `dt`, so the
  relative gain is Δ`dt` / `dt` against the measured mean `dt` ≈ 30 600 µs: 83.2 / 30 540.7 = **0.27 %**, correct. Dividing by
  16 667 µs (0.50 %) would be wrong. The "≤" and the missing pin / forced-OLD labels overstate it (F9).
* **(c) Item 19's 11.8 M and "the stall did not recur".** 11 845 121 is exact. The stall did not recur in `vbn113m`:
  `prio_stall` 0, `gw_idle_prio` 0, no `GpuWaitSlow`. It did not recur in `shn113` or `vid113` either. The only overreach is
  generalising "0 misses" from one run to "forced OLD of this scene" (F7).
* **(d) mutlib timings and counts (items 13, 15, 16).** All counts and walls match `ACCEPTANCE*.md`, `accept2/` and
  `mut_vbn113d.out.txt`. The misleading part is F10: item 13's premise, which v2's own acceptance refutes and item 15
  does not record. F11 is small.
* **(e) "OLD 1 of 6 entries today".** Wrong: 1 of 7 (F1). The same number is sealed into `pred/02_shn113.md` §7
  ("today 1 entry of 6").

## Observations outside items 11–21 (not scored)

1. **`pred/02_shn113.md` §6 P4** still justifies the low confidence with "the census of item 4 found OLD not slower than
   NEW inside a build". Item 10 withdrew that conclusion (M2: with the arm correction OLD is slower by ≈ +100…+180 µs).
   **`pred/01e_vbn113e.md`** seals the wrong NEW range and margin (F2).
2. **`C:/kyty/s113/FACTS.md` is stale.** It stops at item 9 and still says "within a build OLD is not slower
   (+17 ± 84 µs)" without the ±1·SE label, and "measurement closed as not worth it". Both were withdrawn by item 10.
   The project `CLAUDE.md` session-113 paragraph repeats "ВНУТРИ СБОРКИ OLD НЕ МЕДЛЕННЕЕ" and "+17 ± 84 мкс" without
   "±1·SE". Item 10 requires every census number to carry the ±1·SE label. The closing documents (item 21 (3)) must fix
   all of these.
3. **Unpaired arm levels vs the paired estimate.** The unpaired arm medians of block means printed by the scorer
   (`dt_us` 30 623.9 vs 30 621.0) differ by only −2.9 µs, against the paired −83.2. This does not undermine the estimate:
   the median pair Δ is −106.7 and the trimmed mean −81.1. Still, only the paired number may be quoted.
