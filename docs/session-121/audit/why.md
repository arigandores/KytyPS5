# Session 121 audit: why the ceiling did not become a gain, and the closure

This is a read-only audit. I edited no existing file, built nothing, did not run the game and committed nothing.
I read the following:
- ROADMAP s121 items 1–8 (commits `6339dc8` … `a14a2c6`; item 8 was committed at 17:25:07, 27 s after `runs121/shp121.score.txt` was written at 17:24:40);
- `design/design121.md`, `texmemo8.md`, `texmemo8_review.md`, `impl_report.txt`, `pred/02_shp121.md`, `SEALS121.txt`;
- `runs121/{vfy121,shp121}.score.txt`, `go121a.log`, `LOOP_STATE.md`;
- s120 `rpk120_cen120.txt` and `docs/session-120/audit/closure.md`;
- the source at HEAD: `descriptors.cpp` `Tm8::*`, `ResolveTextureWith` with the `resolve_full` lambda, and `renderMemo8.h`.

I also ran my own read-only scripts over `log_shp121.txt` and `log_vfy121.txt`. They are in the scratchpad and not part of the record. Each script parses the `FrameTrace`, `-draw`, `-x` and `-rp` lines and applies the scorer's framing: START 1800, PERIOD 90, window 10–88, `draws > 3000`, pairs (2k, 2k+1). It computes the paired P−M delta and 2SE for all 1 452 fields.
- My pairing reproduces the sealed numbers exactly: Δ`dt_us` +1.3 ± 154.3 and Δ`cpu_gpu_us` −4.2 ± 139.1 over 44 pairs.
- Arming counters differ slightly from the scorer's (for example, `tex_hits` +1 798 against +1 434). The scorer takes arming from all window rows; I used only the estimator rows.

Numbers marked [I] are my inference or arithmetic. Numbers marked [post hoc] come from estimators that were not pre-registered. They cannot change a sealed verdict.

## 0. Verdict of this lens

| question | answer |
|---|---|
| NO_SHIP sound? | **Yes.** The mechanics are correct: Δ + 2SE = +155.6 > 0, admission is all ok, arming is full, and the correctness zeros hold. The result also holds substantively: the prediction of −350 (−250…−500) is refuted at > 3 SE. The −250 edge sits (250 + 1.3)/77.2 = 3.3 SE from the estimate. |
| R1 closure sound? | **Yes, with narrower wording.** The run bounds the gain of this 8-way memo at < 0.16 ms (2SE) on Sky Garden for this build. It does not show "nothing": a pre-specifiable draw-count adjustment gives about −0.10 ms [post hoc] (MAJOR 2). R1 as a class of work stays closed at the 0.5-ms threshold. Even a zero-overhead memo would be bounded at about 0.16 + (probe cost ≤ 0.19 ms by the design's own risk bound) ≈ 0.35 ms [I]. |
| Where did the ~0.7 ms go? | **Into the price, not into the critical path.** GuestGpu is CPU-bound in both arms, and its own CPU time did not move. The census price per would-hit (498 ns) is best explained by in-arm timing that is several times the removable price. Two effects of known sign drive this: (a) latency displacement, where a timed memory-bound segment pays cache misses that later code pays anyway once the segment is removed; (b) pollution by the census's own tables. A second, smaller term is the 8-way probe and LRU overhead, which was plausibly 3–8× the census's `P`. The run's design does not let the two terms be split (MAJOR 1). |
| Item-8 rule justified? | **Yes.** It returns to the method that worked in s85/s86: unit prices from gate contrasts. It should be sharpened on three points: prefer a dose-response knob that adds the class of work, cover all time-derived ceilings including the parked R2/A, and require a burn-slope check of the thread before phase timers are used (MINOR 5). |

## 1. What the timed run can and cannot say

### 1.1 The instruments present in `shp121`

The run is `KYTY_FRAME_TRACE=lite` with `mutsite=0` and no `bindlap`/`pathlap`/`stglap` gate. As a result, **every phase timer reads 0 in both arms**: `bl_res_us`, `bl_img_us`, `mh_bind_us`, `mh_emit_us`, all `pl_*` and all `gw_*`. I checked all 110 such fields. No phase counter moved because none exists in this run. The only live time counters are thread CPU times (`cpu_gpu_us`, `cpu_record_us`, `cpu_main_us`), `dt_us`, `gpu_busy_us` and the M1/record/protect timers.

This was the right choice for a ship ABBA, because instrumenting only one arm would bias the comparison. The cost is that the null cannot be decomposed. A separate diagnostic ABBA with the same phase gate in both arms would have been needed (MINOR 1).

### 1.2 Paired deltas of every live time counter (P − M, 44 pairs, 2SE)

| counter | P | M | Δ | 2SE |
|---|---:|---:|---:|---:|
| `dt_us` | 32 604.7 | 32 603.4 | +1.3 | 154.3 |
| `cpu_gpu_us` (GuestGpu thread CPU) | 31 923.0 | 31 927.2 | −4.2 | 139.1 |
| `cpu_record_us` | 30 191.2 | 30 176.2 | +15.0 | 157.7 |
| `rec_spin_gpu_us` (recorder polling an EMPTY queue) | 26 772.5 | 26 768.4 | +4.1 | 138.0 |
| `da_take_us` / `da_work_us` / `da_walk_us` | 3 037 / 26 904 / 2 625 | 3 026 / 26 960 / 2 635 | +11 / −56 / −11 | 20 / 160 / 19 |
| `gpu_busy_us` | 13 391.9 | 13 356.6 | +35.2 | 43.5 |
| `prot_us`, `pb_wait_us`, `fault_us`, `spin_us` | — | — | all within 1 SE | — |

Of about 150 non-zero fields, the ones that moved beyond 2SE are:
- The arming counters: `tex_hits` +1 798; `texmemo_collide` −1 485; `texfast_rec` −1 273; `texfast_no` −1 405; `b_viewn` −1 405; `texlru_n` −2 136, meaning fewer `TouchImage`/LRU touches because `FindImage` runs less.
- A handful at t ≈ 2 that the multiplicity alone would produce, such as `cpu_proc_us` −11.8 ± 11.7 ms and `lat_us` +178 ± 157.

### 1.3 The critical-path candidate is refuted by the run's own data

Item 8 lists "путь промаха не на критическом пути потока" as a candidate. The data contradict it:
- GuestGpu is CPU-bound in both arms: `cpu_gpu_us` 31.9 ms of `dt` 32.6 ms.
- Its consumer, the recorder, polls an empty queue for **26.8 ms a frame** (`rec_spin_gpu_us`, frameStats.h:367 "RecordSpinNs of the GuestGpu recorder only"). The recorder is starved and GuestGpu is the producer bottleneck.
- The GPU is busy for 13.4 of 32.6 ms.
- Texture resolution runs only on GuestGpu (descriptors.cpp comment at the `Tm8` namespace; the census's `r1_xthr` = 0).
- Most decisively, the GuestGpu thread's **own CPU time** did not fall (Δ −4 ± 139). A saving hidden behind a wait would show up as lower `cpu_gpu_us` with the same `dt`. It did not.

**The removed work was cheap after the costs the change added; it was not hidden** (MAJOR 1).

The block-position table confirms that warm-up is not a factor either:
- In the P arm, key misses fall from 432 per frame at positions 0–9 to about 280 from position 10 on, which is the steady level.
- In the M arm they hold at about 1 760.
- `cpu_gpu_us` shows no position trend in either arm.

## 2. Both sides of the ledger

### 2.1 What the census said the removal is worth (at shp121's counts)

| term | census price | shp121 count | implied, µs a frame |
|---|---|---|---:|
| A: key miss → hit | t_T − t_hit = 516.6 − 19.2 = 497.4 ns | −1 388 misses | −690 |
| R: texfast re-record avoided | 81.1 µs / ≈1 190 ≈ 68 ns | −1 273 `texfast_rec` | −87 |
| P: probe | 43.7 µs (0.94 ns a lookup) | ~47–51 k lookups | +44…+48 |
| **net** | | | **≈ −730** |

Observed: +1.3 ± 154.3 (`dt`) and −4.2 ± 139.1 (`cpu_gpu`). **The gap is ≥ 0.57 ms at 2SE.**

### 2.2 What the 8-way memo adds (not measured by this run; estimated)

| cost | basis | µs a frame [I] |
|---|---|---:|
| Probe: set-line load, 8-tag compare, `countr_zero` loop, then the dependent entry load | Measured in `vfy121` modes 2/3 on the 1/64 sample: 1.20 ns a lookup (`pb − pb0`), which is 56 µs a frame. Unserialized `rdtsc` hides dependent-load latency, so this is a lower bound. The entry load now depends on the way index, and the 512 × 64 B = 32 KB set array is the size of L1D. The design's own risk figure was 2–4 ns a lookup (≤ ≈185 µs). | 56 … ~190 |
| LRU stamp write on almost every hit (≈46 k/frame; skipped only if the way is already MRU) | one store to a line that has just been read | 25 … 50 |
| Colder hit tails on the ≈1 390 gained hits (desc copy in emit, image lines of an entry the direct memo would have evicted) | s120 audit §1.2 (a)/(b) | 40 … 130 |
| **total** | | **≈ 120 … 370** |

The working set does not grow in any way that matters. The 4 096 × ~650 B entry array is the same in both arms. P adds only the 32 KB of set lines, and P does about 1 390 fewer 584-B desc stores into memo slots.

### 2.3 What the clean miss must then cost

observed net = clean gross saving − 8-way cost, so the clean gross saving ≈ observed net + (120…370).
- Using the raw ABBA (0 ± 139) or the draw-adjusted one (−100 ± 80, §3), the clean gross saving is ≈ 120–470 µs [I].
- Removing R (45–90 µs; s85's wall-calibrated texfast saving is 35.4 ns a slot, and the census's is 68 ns) leaves ≈ 25–310 ns per removed miss. **That is 5–60 % of the census's 497 ns; the central value is about ⅓ (~165 ns).**

The `vfy121` run gives a second, independent reading. Its conditions: NEW BDA regime, `texfastcheck=1` in every arm (which nulls most of the view-lookup side: `b_viewn` = `b_texn` there), and cycle-paired arms, not ABBA.
- Mode 1 − mode 0: `cpu_gpu_us` +58.8 ± 176.6 raw, and **−7 ± 67 draw-adjusted** [post hoc], for −1 218 key misses.
- The implied clean resolve saving per miss is (7 + 120…370)/1 218 ≈ 100–310 ns [I]. This is again well below the census.

The two readings are consistent. The difference between shp121's draw-adjusted −102 and vfy121's −7, about −95 ± 104, is the size one would expect of the R/texfast term that `texfastcheck` suppresses. This is a cross-run comparison and only suggestive [I].

**Answer to "is the probe/LRU costing about what the misses saved?"** Partly. It is the second term. At its plausible 120–370 µs, it eats between a third and all of the clean saving. On its own it cannot explain the gap: that would need ≥ 12 ns a lookup (≥ 0.57 ms), which is 13× the census's `P` and far above one extra L2-latency load. The larger error is in the census price.

### 2.4 Why the census price was high: pollution, and above all latency displacement

**Pollution by its own instruments.** The evidence is in `rpk120_cen120.txt` and the code:
- The census P arm cost +2 766 ± 138 µs of `dt` (+8.1 %).
- On every lookup, `R1Enter` probes three shadow tables of 1.9 MB immediately **before** `r1_t0`.
- After `t1`, `R1Miss` runs an XXH3 over 73 words plus 4 table fills.
- The R2 replay and spcen ran in the same arm.

The census's own diagnostics show the price is memory-bound:
- `t_ham` (a hit right after a stored miss) = 48.8 ns against `t_hit` 19.2 ns, so 2.5× for a hit that follows a miss.
- No-store key misses cost 389.9 ns against `t_miss` 539.3 ns. About 150 ns of a miss is the 584-B desc store into a cold slot.
- The warming control shows that touching the candidate's image lines lowers the miss price by 31.6 ns.

Roughly 2 000 cycles per miss is a DRAM-latency figure, not an arithmetic one. The s120 audit flagged this in its term (d) and MINOR 5: the level-1 pollution check, with timers only, was never run.

**Latency displacement, which is the more general mechanism [I].** The miss path is memory-bound: `FindImage` hash lookup, image object, tiling tables, desc store. The code that follows in the same draw needs the same lines anyway: the hit tail, `ConfigureImageSource`/`TouchImage`, the view lookup in `RebindImages`, and `CommitBindings` emit. A timer around the miss therefore books latency that, once the miss is removed, moves to the next consumer of those lines instead of disappearing. Even a perfectly clean in-arm timer over-attributes in this situation.

The run shows the pattern directly:
- In the M arm, a frame-level regression of `cpu_gpu_us` on key misses, with draws, dispatches, `b_texn`, `bda_scan`, faults and block fixed effects as controls, gives **0.73 ± 0.29 µs a key miss** [post hoc, observational]. That matches the census price.
- This regression is confounded: key misses correlate 0.90 with draws.
- The ABBA gives ≈ 0–0.1 µs per **removed** miss.

Association, and timed price, are not the removable price. The item-8 rule needs this distinction.

### 2.5 The BDA regime

The census ran in NEW (`bda_scan` 58). `shp121` ran in OLD in both arms (P 1 246.9, M 1 243.3; Δ 3.6 ± 14.3). This is common-mode and not a cause of the null:
- `vfy121` ran in NEW (57–64), and its mode-1 vs mode-0 contrast is also null (−7 ± 67 adjusted; +59 ± 177 raw).
- OLD adds ~1 000 region scans a frame to GuestGpu. That is independent of the texture memo, and GuestGpu stays the bottleneck.

OLD may have widened the per-pair SD somewhat (511 µs, against 402 µs in the cycle pairs of `vfy121`), but the realized 2SE of 154 µs sits inside the pre-registered 0.14–0.18 ms band. The regime was reported, matched between arms, and was not an admission criterion in pred/02. There is no finding here beyond a note (MINOR 3).

### 2.6 texfast: did the re-records move, and what should they have saved?

Yes, fully. `texfast_rec` fell from 1 547 to 274 (−1 273). `texfast_no` fell by 1 405, and so did `b_viewn`, by the same amount; `texfast_ok` rose by 1 732.

Expected value:
- s85's wall-calibrated texfast contrast gives 35.36 ns per slot converted, so ≈ 1 325–1 405 slots is ≈ 47–50 µs.
- The census's R term was ≈ 87 µs at this count.

Either figure is below one SE of this run. The texfast side was never able to carry the track: it was 12 % of the census ceiling. It may be real at ~0.05–0.1 ms. The cross-run difference in §2.3 hints at it, but it is not resolvable in one ABBA.

## 3. The estimator's precision: what a pre-registered covariate would have given

The scene's work per frame varies between blocks. P blocks happened to carry +17.7 ± 20.6 more draws per frame. The treatment has no mechanism for changing the game's draw count, and the delta is not significant. In the run, one draw costs 5.7 µs of `cpu_gpu_us` by regression, which matches s116's measured 5.74 µs per operation. Adjusting for Δdraws per pair [post hoc] gives:

| estimator | Δ `cpu_gpu_us` | Δ `dt_us` |
|---|---:|---:|
| sealed (unadjusted) | −4.2 ± 139.1 | +1.3 ± 154.3 |
| per-draw ratio × mean draws | −112.1 ± 76.2 | −108.7 ± 99.4 |
| OLS on (Δdraws, Δbda_scan) | −101.6 ± 79.6 | −98.2 ± 104.8 |

Consequences:
1. **The verdict stands.** Even the adjusted `dt` interval crosses 0 (upper +6.6), and the adjustment is post hoc.
2. **"Nothing" is too strong.** The run is compatible with a real gain of about 0.1 ms. Its best point estimate after adjustment is −0.10 ms, still far below −0.35.
3. **Precision.** Adjustment roughly halves the variance of the `cpu_gpu` estimator (2SE 139 → 80) and cuts `dt` 2SE by about 30 %. The programme now hunts effects of 0.1–0.2 ms with 2SE of about 0.15, so a pre-registered covariate adjustment is worth adopting. It needs a guard: Δdraws must be non-significant, because in `vfy121` mode 2 shifted draws by −62 ± 37, so a slow arm can move them (MAJOR 2).

## 4. Fidelity of item 8, and the closure

Item 8 is faithful on:
- all the numbers;
- the sealed consequence;
- the statement that the ceiling and the audit's 0.33–0.62 over-predicted;
- the scoping to "Sky Garden, this build".

Where item 8 falls short:
- **"не дали НИЧЕГО на стене и на времени потока"** overstates. The run shows |Δ| < 0.16 ms at 2SE and a raw point of 0; post hoc about −0.1 ms. See MAJOR 2.
- **The three candidates [I]** are listed as equals, but the run separates them. "Not on the critical path" is refuted (§1.3). "The probe/LRU eats the gain" is a real but secondary term (§2.2–2.3). "The census price is inflated" is primary. Its mechanism is latency displacement at least as much as pollution (§2.4). The closure should say which candidates the data eliminated and which they rank.
- **Timing:** item 8 was committed 27 s after the score file, from a pre-written patch. That is fine for the verdict and the sealed consequence. The explanatory clause, however, was written with no look at the run's other counters; hence the refuted candidate.
- **The new rule** (§5) was recorded before any action under it, as the protocol requires.

## 5. The item-8 rule: justified, with three sharpenings

The rule reads: "a time-census ceiling alone never opens a track; calibrate census→wall first (a cheap stub removing the same class of work in ABBA), or go straight to a prototype ABBA". It is **justified**:
1. **This session is a clean falsification.** The ceiling was 658.8, the honest range 0.33–0.62, the prediction 0.35, and the measurement ≤ 0.155. The counts were exact (would-hits 1 259 vs removed 1 388). Only the time prices failed.
2. **The programme's successful unit prices were wall-calibrated by gate contrast.** Examples: s85 `texfast` (55.02 vs 19.66 ns, model reproduced to +0.30 %) and s86 `progmemo` (K_miss 73.79, K_hit 14.53 ns). The s120 census broke with that method.
3. **In-arm timers of memory-bound segments have a structural bias** (displacement, §2.4) that no warming correction removes. Only a wall contrast measures what removal saves.

Sharpenings (MINOR 5):
- **(a) The calibration arm should add work, not stub it.** Removing a class of work cheaply is usually the prototype itself. The cheap calibrator is a measurement-only dose-response knob: force a key miss or stale on 1/k of hits (for R1, a `texmemo8=4`-style forced-invalidate), ABBA it at two doses, and read the wall slope in ns per unit. It prices exactly the unit the census priced, in the clean arm, with the displacement included.
- **(b) Scope.** The rule should name every ceiling built from counts × in-arm timed prices, including the parked R2 (435/1 068) and spcen A (340–687) borders from the same instrument family. Applying this session's calibration factor (removable ≈ ⅓ of timed, range ~0.05–0.6) puts both well below 0.5 ms [I]. They should not be reopened on their census numbers.
- **(c) Critical-path precondition.** Before any phase timer is converted to wall, the thread's sensitivity should be shown by a burn-slope ABBA: spin a known number of µs on the thread and read d(dt)/d(burn). In Sky Garden it is ≈ 1 by the §1.3 evidence, but not necessarily in other scenes.

## 6. What the programme should do next

1. **Close s121 as recorded, with the two corrections above**: "≤ 0.16 ms, point 0, post-hoc draw-adjusted ≈ −0.1"; and the candidate ranking, with the critical-path candidate refuted by `cpu_gpu_us` and `rec_spin_gpu_us`. Record in FACTS the explicit statement that the GuestGpu micro-tracks of Sky Garden are exhausted at the 0.5-ms line. R1 is closed by measurement. R2 and A are parked, and their census prices share R1's inflation. B is exhausted. s119 already found no ≥ 1-ms track by reading the code.
2. **s122, the bottleneck map across scenes, is the right next step.** Design it around causal probes, not timers:
   - **Burn-slope per thread per scene.** Add one measurement-only knob that spins N µs per frame on a chosen thread (GuestGpu, recorder, M1 workers, the main guest thread). A small ABBA at two doses per scene yields d(dt)/d(burn): which thread is on the critical path, and whether a saving converts 1:1. This is the item-8 calibration generalized. It is cheap and needs no mechanism.
   - **Lite-counter classification per scene**, all already live: `cpu_gpu_us`/`dt`, `rec_spin_gpu_us`, `gpu_busy_us`/`dt`, the `dt` distribution (vblank quantization, ROADMAP §4), `semwait_us`, and the BDA regime.
   - **Pre-register the draw-adjusted estimator** alongside the raw one, with the Δdraws non-significance guard (§3). It roughly doubles effective sample size.
   - If phase timers are used, they go in both arms. Their price and their burn-calibrated wall slope are reported before any phase number is quoted.
3. **Do not reopen R1-class memo work.** The remaining upside of a zero-overhead memo is bounded at ≈ 0.35 ms [I]. That is below 0.5, and the probe cost is inherent to any associative table. If a future track ever depends on the price of a key miss, get it from the forced-miss dose-response knob (§5a) in one short ABBA. That knob would also split the census-inflation term from the probe-overhead term that this session could not separate.
4. **Structural levers.** With Sky Garden's GuestGpu micro-tracks exhausted, the parked A-walker (s119/s120 debt) remains the only structural CPU lever there. Its reopen triggers were written in s120; the map is what can fire them. If the map finds a GPU-bound or main-thread-bound scene, the programme's next track comes from there rather than from GuestGpu.

## 7. Findings

### MAJOR

- **MAJOR 1: the closure's causal reading is incomplete, and one candidate is refuted by the run.** GuestGpu is CPU-bound in both arms:
  - `cpu_gpu_us` is 31.9 of 32.6 ms;
  - the recorder polls an empty queue for 26.8 ms a frame;
  - the GPU is busy 13.4 ms;
  - Δ`cpu_gpu_us` = −4 ± 139.

  The removed work therefore did not become a saving on the thread itself; it was not merely hidden from the wall. The census price per would-hit (497 ns) is 2–20× the implied removable price of ≈ 25–310 ns (central ~165) [I]. The best-supported mechanism is **latency displacement** of a memory-bound segment, compounded by the census's own pollution; the census's own `t_ham` 48.8 vs 19.2 ns and the 150-ns cold desc store point that way. The 8-way probe, LRU and cold-tail cost (≈ 120–370 µs [I]; the only direct reading is 56 µs from the 1/64 sample, a lower bound) is a real second term but cannot explain the gap alone. The closure should rank the candidates this way and strike "not on the critical path".
- **MAJOR 2: "nothing" overstates, and the ABBA estimator leaves precision unused.** The sealed Δ bounds the gain at < 0.16 ms. A draw-count adjustment [post hoc] gives Δ`dt` −98 ± 105 and Δ`cpu_gpu` −102 ± 80. That is a possible ~0.1-ms real effect, still consistent with NO_SHIP and far from −0.35. Future sealed ABBAs should pre-register a draw-adjusted estimator with a Δdraws guard. It cuts 2SE by ~30–45 % in this run.

### MINOR

- **MINOR 1: no phase decomposition was possible.** The timed run had no phase timer in either arm, correctly for a ship ABBA. A separate cheap diagnostic ABBA, or the dose-response knob, was not planned, so the null cannot be split into its terms.
- **MINOR 2: item 8's explanatory clause was written in 27 s from a pre-drafted patch,** with no reading of the run's other counters. The verdict and consequence are fine. The explanation should be revised at the close.
- **MINOR 3: the BDA regime differed from the census** (OLD here, NEW in cen120). It is matched between arms and not a cause of the null: `vfy121` in NEW is null too. It may have widened the per-pair SD (511 vs ~402 µs). It should be named in the closure as checked, not as a candidate.
- **MINOR 4: the texfast/R term (≈ 47–87 µs expected) was always below one SE.** It moved as designed (`texfast_rec` −1 273, `b_viewn` −1 405) and may be real. It could not have carried the track, and the closure should not suggest it did.
- **MINOR 5: the item-8 rule should be sharpened:**
  - (a) calibrate by adding the work at a known dose (forced-miss knob), not by a removal stub;
  - (b) apply it explicitly to the parked R2/A census borders, which should not be reopened on their numbers;
  - (c) require a burn-slope check of the thread's critical-path sensitivity before phase timers are converted to wall.
- **MINOR 6: carried lesson.** The s120 audit's MINOR 5 (the level-1 pollution check was never run) and its term (d) named exactly the risk that materialized. An OPEN verdict whose central estimate rests on an unchecked, known-sign looseness should have triggered the calibration before the prototype. The new rule now covers this.

## Appendix: key numbers (all per frame, Sky Garden, pinned)

`shp121`, 44 pairs, OLD BDA in both arms:

| counter | P | M | Δ |
|---|---:|---:|---:|
| `dt_us` | 32 604.7 | 32 603.4 | +1.3 ± 154.3 |
| `cpu_gpu_us` | 31 923.0 | 31 927.2 | −4.2 ± 139.1 |
| `rec_spin_gpu_us` | 26 772 | 26 768 | — |
| `gpu_busy_us` | 13 392 | 13 357 | — |
| key misses (estimator rows) | 277.6 + 9.6 | 1 762.6 + 4.6 | — |
| key misses (scorer, all window rows) | 274 | 1 662 | — |
| `tm8_fill` / `evict` / `evict_view` | 289 / 272 / 251 | — | — |
| `texfast_rec` | 274 | 1 547 | — |
| `b_viewn` | 3 558 | 4 963 | — |
| `texlru_n` | — | — | −2 136 |

Draw-adjusted [post hoc]: Δ`dt` −98 ± 105, Δ`cpu_gpu` −102 ± 80, 5.7 µs per draw.

`vfy121`, 16 cycle pairs, NEW BDA, `texfastcheck=1`:

| contrast | Δ `cpu_gpu_us` |
|---|---:|
| mode 1 − mode 0, raw | +58.8 ± 176.6 |
| mode 1 − mode 0, draw-adjusted | −7 ± 67 |
| mode 2 − mode 1 (verify cost) | +709 ± 270 |

Probe cost from the mode 2/3 sample: 1.20 ns a lookup, 56 µs a frame.

cen120 census (P arm, +2 766 µs price): t_hit 19.2, t_miss 539.3, t_T(w8) 516.6, t_ham 48.8 ns; no-store miss 389.9 ns; warming 31.6 ns; W 1 258.7; A 626.1, R 81.1, P 43.7, giving C 658.8.
