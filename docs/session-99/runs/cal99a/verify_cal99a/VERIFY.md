# Independent VERIFY: cal99a — NOT ADMITTED; STOP

2026-09-19. Independent offline review of sealed `pred/01_bindings_only.md` and raw
`log_cal99a.txt`, `stdout_cal99a.txt`, `cal99a.json`. No FACTS, author/runner reports,
run99_cal99a score/result/console, full calibration CLI, game or build was used.
All new output is under `C:/kyty/s99/verify_cal99a/`. No sealed text or scorer was edited.

**Three controls fail, representing two distinct deficiencies:**

| Required control | Independent raw result | Limit | Result |
|---|---:|---:|---|
| Criterion 3 work population | −4.0974201604% draws/frame | abs <0.5% | FAIL |
| Inherited C5 | 0.0409742016042 | <=0.02 | FAIL |
| R2 completed falling edges | 17 | >=30 | FAIL |

C5 and criterion 3's work test reuse the SAME change in draw population and are not
independent evidence. Their untrimmed measurement-window means are U=5052.85172004745,
A=4845.8151549942595 draws/frame, over 843/871 rows. Both remain required for this
calibration: only C9 is exempt (`pred/01_bindings_only.md:62`, `:92`). R2 is independently
insufficient (`:63`, `:104`). The sealed STOP at `:53` and `:64` applies; bf99a, cal99c and
bf99c must not follow under this protocol. There is no admitted calibration budget.

## Raw provenance and survival

The immutable rule is exactly 10848 bytes, SHA256
`8b816528b78a1730c052d7fdbc414d7b00ef3b9c4df25ab2e7016b23d9d4b14d`.
Saved binary SHA256 is `ee9cc8ab1f5d25384dedb02a6a6abfca2aa7692585fcaddc74950721afc7a160`,
23739904 bytes, matching the runtime metadata (`cal99a.json:3`). Gates are 1092 bytes,
99 names, SHA256 `00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`;
metadata gate assignments equal that file. Metadata preregistration matches the sealed hash
(`cal99a.json:315`). Full raw/source hashes are in `VERIFY.json`.

Exactly one `attempt 1`, no warmup/retry, outcome ok, hold_exit=null, hold=180.1s for
requested 180s (`cal99a.json:324`, `:335`, `:337`, `:338`, `:346`). Raw main-row durations
sum to 189.030605s; after stable_frame=278 they sum to 180.215183s. Thus both metadata
and raw duration support survival. Runtime launch/finish are `cal99a.json:5`/`:6`.
No forbidden failure marker occurs in either raw log or stdout.

Metadata and actual GateArm text agree: 30-frame ABBA from 1800, mode2, burn12000 in
both arms, drawahead1 in both arms. Blocks 0..67 are ordered, unique and contiguous.
First GateArm is `log_cal99a.txt:439504`. Actual latch1, clock-pin1 and clear0 are at
`log_cal99a.txt:16414`, `:16456`, `:16465`; metadata explicitly disables markers and
checkpoints (`cal99a.json:59`). Protocol helper reports zero errors. This verifies recorded
provenance, not an independent measurement of every background process during the hold.

## Population, edges and retained rows

Raw parser independently merged 3812 main/draw/x rows, n=2..3813, with no duplicate
field assignments. Measurement begins at `log_cal99a.txt:468323` (n=2100) and ends at
`:633783`. All required counters exist, including before frame2100.

Criterion 3: area U=2007.544777596946, A=2007.3338190079155 Kpx/attachment;
split=−0.0105082881% PASS; complete/matched area pairs=28/28 PASS. Work FAIL above makes
the overall criterion INVALID. Area CSV was freshly extracted into this VERIFY directory;
no pre-existing area CSV was used (`area.txt:3`). The independent calculation reproduces it.

There are 34 arm changes, all carrying exactly one bf_edge at idx0, no missing/duplicate
edge and none outside allowed transition windows. Completed falling edges=17, first at
`log_cal99a.txt:448085` (block3), last at `:633468` (block67). Full edge/block line mapping
is in `VERIFY.json`. T* removes **102 rows over the full log, 87 inside the measurement
window**. Retained measurement populations are U=799, A=828. There are 29 endpoint block
pairs (>=10); starting endpoint block9 is unpaired and excluded, as the sealed rule allows.
The area-pair count differs because criterion 3 requires >=8 rows per block.

Arithmetic per-row T*-trimmed dt means, independently recomputed and matched to helper:
**dt_U=50501.82478097622 us; dt_A=42516.67149758454 us.** These are diagnostic calibration
inputs only. C9 is reported/exempt here. No B value, architecture branch or usable burn
budget is admitted or published in this report.

## Controls that do pass

C1''' and live darkness: all retained U sums of bf_n, burn and all three live witnesses
are zero; whole-log DARK98+LIVE structure passes. C2' population error=0.004056<=0.02,
skip/drop zero. C3' emit identity differs by 5 against allowed58 boundaries. C4_B:
retained armed bf_mat=bf_reuse=0; live_ahead=6835498, live_mat=631308, live_memo=0.
Positive materialization paths exist; srtmemo=0 agrees with live_memo=0. C6' base BDA
thirds=1067/1063/1062 (ratio1.005); C7 other instruments dark. Fresh C8''_B net-floor
comparison and C10'''_B burn/structure pass. Real-clear skips, dropped skips and marker
operations remain zero. Full deciding booleans are in `VERIFY.json`.

R1, R3', R4', R5, R6, R6', R7, R7', R8 pass; R2 fails. Recovery medians for images
over first2/first3 flips are 12/17, buffers 2/3 (all <=50). No skipped downloads,
bf_mixed, bf_defer_force or trigger counters. Crossovers persist: bf_xover=bf_xover_acb=35,
and all17 falling edges have positive ACB crossover. They are reported, not a failing
criterion. See `rv.txt:23` onwards. Original legacy FAIL lines remain in
`legacy_controls.txt`; replaced frozen-floor C4 or legacy R3 do not decide this new mode.

This process surviving 17 falls does not establish the required >=30-edge acceptance,
mode2 hazard-rate power, rendering correctness, accepted calibration, B_a/B_c, global
G/R1 closure, completion of M3, permission to advance M4/M5, or 60 FPS. The rule remains
unchanged and the sequence stops at its first failed stage.
