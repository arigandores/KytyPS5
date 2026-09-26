# Session 120 audit — independent recount of seal 01 `cen120` (and of the unsealed smoke `smk120`)

Lens: INDEPENDENT RECOUNT. Read-only with respect to every existing file. The only new files are in
`C:/kyty/s120/audit120/`: this report, `recount120.py` (my parser and formulas),
`recount_cen120.json` / `.out.txt` and `recount_smk120.json` / `.out.txt` (its outputs).

## 0. Verdict of the recount

**CONFIRMED.** I rebuilt everything from the log using the formulas in `design120.md` §2–§4. Every sealed quantity
equals the scorers' output to within 1e-12 µs. That is floating-point noise, far inside the 0.1 µs tolerance. The
correctness totals over all rows are all 0, and no mismatch line appears anywhere. The verdict ladder applied to my
numbers gives the same six verdicts: R1 OPEN, R2 NOT_OPENED, package R OPEN, A NOT_OPENED, B CLOSED, package SP
NOT_OPENED. In a pair bootstrap (2000 resamples) none of the three questions came close to its threshold:

- R1 never fell below 500 (minimum 640.5).
- N never reached 500 (maximum 343.4).
- N⁺ + 2SE never fell below 500 (minimum N⁺ alone is 844.4).

The smoke numbers disclosed in the pred are right, including the lead's own draft `smoke120.py` values. I reproduced
those exactly by recreating its block-0 shift.

Nothing here is a MAJOR finding. There are four minor points that matter for the close (§7):

- A is NOT_OPENED rather than CLOSED only because of the warm-cache term T_A.
- R2 is NOT_OPENED rather than OPEN only because of the [I] constant A_tr = 1.2 ns.
- The ±8 skew widening of item 6 was never needed.
- Two scorer-level estimator choices differ, without effect on any verdict.

## 1. Independence and method

- `recount120.py` was written from `design120.md` §2–§4 and the ROADMAP s120 items. I opened `rpk120.py` and
  `spc120.py` only to learn field names and their conventions, then compared outputs. No code is imported or shared.
- **Parsing.** One streaming pass reads the file in binary mode. The main, `-draw` and `-x` rows are keyed by `n`.
  For `-x` rows only census-relevant fields are kept (`r1_*`, `r2_*`, `sp_*`, `pl_em*`, `bl_*`, `texmemo_*`,
  `tnull_*`, `mh_emit*`). Every such field is also summed over ALL `-x` rows to give the correctness totals. Marker
  and mismatch strings are searched as substrings anywhere in any line, so interleaved output is also caught.
- **Blocks.** Blocks are built from the `GateArm:` lines, never from the `blk` labels. A `GateArm` with `frame=F`
  opens block rows n = F+1 … F+90. I verified this from the label transitions: the first `arm=1` row is n=1891, for
  `GateArm frame=1890`. The window is positions 10..88, that is n = F+11 … F+89 (79 rows). The estimator rows are
  the window rows with `draws > 3000`.
- **Pairs.** Pairs are (b, b+1) for even b, and both blocks must have a complete window.
- **Label check.** I also checked that every row of every block carries the arm/blk label that its GateArm implies:
  0 mismatches in 78 blocks.
- **Result of the reconstruction:**
  - 78 GateArm lines, 8 789 rows of each stream, 0 duplicate `n`.
  - Block 77 is partial: it reached position 59, the log ends at n=8790.
  - Block 76 is complete but unpaired, so it feeds nothing in the estimator.
  - **38 pairs**; ABBA sequence PMMPPMMP…
  - Estimator frames: **P 3 001, M 2 970** (window frames 3 002 per arm; 1 P row and 32 M rows fail `draws > 3000`).
    This equals the scorers' counts.
- **Pooled point values.** Each is Σ over the estimator frames of all paired blocks of the arm, divided by their
  count. 2SE = 2·stdev(per-pair values)/√38.
- **Per-pair values.**
  - R1: the pair's P block, with the table fixed to the pooled argmax.
  - R2: the pair's M block.
  - Package R: per-pair C_R1 + C_up.
  - spcen: the pair's P and M blocks, with z̄ pooled (the scorer's choice). z̄ per pair is also shown, §7.

## 2. R1 (P arm, design120 §2) — mine vs `rpk120_cen120.json`

| | mine | rpk120 | diff |
|---|---:|---:|---:|
| t_hit / t_miss / t_fast / t_ham (ns) | 19.2007 / 539.3123 / 9.8310 / 48.7925 | same | 0 |
| lookups a frame | 46 399.46 | 46 399.46 | 0 |
| w4: W 1 056.0, t_T 501.83 → A 509.64, L 57.48, R 81.20, E 23.80, P 16.43 | **C 540.73** (no E 516.93) | 540.73 | < 1e-12 |
| w8: W 1 258.7, t_T 516.60 → A 626.06, L 33.14, R 81.13, E 28.37, P 43.65 | **C 658.76** (no E 630.39) | 658.76 | < 1e-12 |
| d16: W 1 021.9, t_T 525.74 → A 517.62, L 0, R 81.01, E 23.03, P 0 | **C 621.66** (no E 598.63) | 621.66 | < 1e-12 |
| C_R1 = max_T (argmax w8) | **658.76** | 658.76 | 0 |
| 2SE (per pair, table w8) | 9.116 | 9.116 | 4e-15 |

Correctness totals and controls over all rows:

- `r1_w4_bad` = `r1_w8_bad` = `r1_d16_bad` = 0; `r1_incl` = `r1_xthr` = 0.
- Every `r1_w1_*` (q, qns, p, pns, lose, bad, rb, rbns) is 0.
- `R1CenMismatch` lines: 0.
- `r1_reset` = 56 in total. All 56 sit at block positions 0 (2, arm P) or 89 (35 in P, 19 in M). Those are the
  arm-switch rows outside the window, so no P block loses a window, which agrees with rpk120's `reset blocks []`.
- Samplers: `r1_hit_t/r1_hn` = 0.1240 and `r1_mp/r1_mn` = 0.5003.
- M-arm window zeros hold: `r1_hn`, `r1_mn` and `r1_*_q` are all 0.

Largest per-block window residual of each identity:

| identity | residual | tolerance |
|---|---:|---|
| `r1_hn − tex_hits` | 520 | FAR, about 0.15 ‰ of about 3.5 M |
| `r1_mn − (collide+empty)` | 26 | |
| `r1_sn − stale` | 0 | |
| `b_texn − (hn+mn+sn+tnull)` | 525 | |
| `r1_pb_n − self_h_n` | 1 | NEAR |

## 3. R2 (M arm, design120 §3 with the `r2_s_*` subset deviation of item 5) — mine vs rpk120

| | mine | rpk120 | diff |
|---|---:|---:|---:|
| z̄ (M) / w̄_rep / w̄_oth / st̄ (ns) | 8.9447 / 50.4860 / 14.8951 / 19.6856 | same | 0 |
| S / Z / L a frame | 31 296.21 / 886.38 / 447.74 | same | 0 |
| T* / W / ST (µs) | 1 376.39 / 199.13 / 13.11 | same | < 3e-14 |
| p_c (ns) | 42.77 (inside 25–90) | 42.77 | 0 |
| **C_up / C_pt / C_lo** | **1 067.60 / 435.18 / −36.77** (order C_lo ≤ C_pt ≤ C_up holds) | same | < 3e-13 |
| C_ext / C_rp (information) | 450.06 / 268.61 (268.57 with M-arm z̄) | 450.06 / 268.61 | 0 |
| 2SE (per-pair C_up) | 12.681 | 12.681 | 1e-14 |

Correctness totals and controls:

- `r2_bad` = `r2_bad_key` = 0 over all rows.
- `R2Mismatch*` = 0 lines and `R2Diverge` = 0 lines.
- The M arm has no replay: `r2_rm_*` = 0 in the M window.
- R2 sampler `r2_nul_n` / image stages = 0.1250.

Largest per-block window residual of each identity:

| identity | residual | tolerance |
|---|---:|---|
| `r2_stg − bl_prep_n` | 45 (P) / 46 (M) | FAR |
| `r2_slots − bl_res_n` | 177 | FAR |
| `r2_rep − (cl+mx)` | 1 | NEAR |
| `r2_wr+wo − nul` | 1 | NEAR |

**Package R:**

- R_pt = 658.76 + 435.18 = **1 093.93**.
- R_up = 658.76 + 1 067.60 = **1 726.36**.
- 2SE (per-pair R1 + C_up) = **15.010**.
- rpk120 gives exactly the same values.

## 4. spcen (P arm, M for the Δ terms, design120 §4 with the timer-read add-back) — mine vs `spc120_cen120.json`

| | mine | spc120 | diff |
|---|---:|---:|---:|
| z̄ (P window, `r2_nul`) | 8.7195 ns | 8.7195 | 0 |
| G_A / G_B | 1 001.20 / 403.58 | same | 0 |
| **N_A / N_B / N** | **340.18 / −8.10 / 332.08** | same | 0 |
| Z_A / Z_B / Z (add-back) | 128.07 / 154.88 / 282.95 | same | 0 |
| Δ_A (unclamped, ns a frame) | +297 012.9 (= 57.2 ns a draw) | same | 0 |
| Δ_B / Δ_B′ (ns a frame) | −9 081.6 / +68 359.9 | same | 0 |
| r_A / r_B | 0.73632 / 0.45536 | same | 0 |
| T_A / T_B | 218.70 / 31.13 | same | 0 |
| **N⁺_A / N⁺_B / N⁺** | **686.95 / 177.91 / 864.85** | same | 1e-13 |
| 2SE: N_A 4.62, N_B 2.28, N 6.47; N⁺_A 7.35, N⁺_B 3.95, N⁺ 10.61 | | same | 0 |

Correctness totals and controls:

- Over all rows: `sp_rt_bad` = `sp_tr_bad` = 0; `sp_rt_race` = 0 against `sp_rt_would` 15 430 054;
  `sp_rt_nt` = 0.
- `SpRtMismatch` / `SpTrMismatch` lines: 0.
- M-window zeros hold for `sp_rt_n`, `sp_tr_n`, the would-hit counters, `pl_em_rt_hit_ns`, `bl_tr_hit_ns` and
  `pl_em_spchk_ns`.

Largest per-block window residual of each identity:

| identity | residual | tolerance |
|---|---:|---|
| draw identity `sp_rt_n − pl_em_n` | 12 | ±64 |
| partition `sp_rt_n − (would + Σ sp_rt_x_*)` | 1 | ±8 (item 5's ±2 would also pass) |
| partition `sp_tr_n − (would + Σ sp_tr_x_*)` | 2 | ±8 (item 5's ±2 would also pass) |

Emit chain: spc120 reports |Σ parts − `mh_emit_us`| = 106.1 (P) and 105.2 (M) µs a frame, inside its 256 µs.

**Price P−M (report only).** Two correct estimators of the same thing:

| estimator | used by | dt_us | cpu_gpu_us |
|---|---|---:|---:|
| pooled means | spc120 (and my pooled value) | +2 768.0 | +2 683.7 |
| mean of per-pair differences | rpk120 | +2 765.9 | +2 681.9 |

Both have 2SE 137.7 (dt_us) and 132.7 (cpu_gpu_us). ROADMAP item 7 quotes rpk120's +2 766 ± 138. The 2.1 µs gap
exists only because the two arms have unequal frame counts (3 001 against 2 970).

BDA regime (from rpk120, not recomputed): 58.4 and 58.5 scans a frame, both NEW.

## 5. Differences and their explanation

- **Scorers against me: none above 1.2e-13 µs.** This is double-precision summation order.
- **Price 2 768.0 against 2 765.9:** pooled estimator against per-pair-mean estimator, explained in §4. It is not a
  verdict input.
- **Per-pair choices that are equivalent under the design text (no effect on any verdict):**
  - rpk120 fixes the R1 per-pair table at the pooled argmax (2SE 9.12). Taking the per-pair max gives 2SE 6.18.
  - spc120 uses the pooled z̄ in every pair (2SE of N⁺ 10.61). Each pair's own z̄ gives 12.79.

## 6. Pair bootstrap (2 000 resamples of the 38 pairs, seed 120, pooled estimator recomputed each time)

| quantity | point | bootstrap mean ± sd | 2.5–97.5 % | answer to the question |
|---|---:|---:|---:|---|
| C_R1 | 658.8 | 658.8 ± 4.9 | 648.7–667.9 | < 500 in **0 / 2000**; min 640.5; argmax w8 in 2000/2000 |
| C_R1 without E | 630.4 | — | min 612.4 | < 500 in 0 / 2000 |
| R_pt | 1 093.9 | 1 093.9 ± 5.8 | 1 082.6–1 105.1 | < 500 in 0 / 2000 |
| R2 C_pt | 435.2 | — | 424.1–444.9 (min–max) | ≥ 500 in 0 / 2000 |
| N | 332.1 | 332.0 ± 3.2 | 325.6–338.2 | ≥ 500 in **0 / 2000**; max 343.4 |
| N_A | 340.2 | 340.1 ± 2.3 | 335.6–344.7 | ≥ 500 in 0 / 2000 |
| N⁺ | 864.9 | 864.8 ± 6.2 | 853.0–877.7 | min 844.4 |
| N⁺ + 2SE (2SE per resample) | 875.5 | 875.2 ± 6.4 | 862.8–888.3 | < 500 in **0 / 2000** |
| N⁺_A + 2SE | 694.3 | 694.1 ± 3.9 | 686.6–701.9 | < 500 in 0 / 2000 |
| N⁺_B | 177.9 | — | 169.5–188.7 (min–max) | ≥ 500 in 0 / 2000 |

The bootstrap sd of C_R1 (4.9) is consistent with the per-pair 2SE (9.1 ≈ 2 × 4.6). None of the verdicts is near a
sampling boundary.

## 7. Do the verdicts follow from the numbers? Yes. Four points for the close

The ladder, applied to my values:

| member | check | verdict |
|---|---|---|
| R1 | 658.8 ≥ 500 | OPEN |
| R2 | 435.2 < 500; 1 067.6 + 12.7 ≥ 500 | NOT_OPENED |
| package R | 1 093.9 ≥ 500 | OPEN |
| A | 340.2 < 500; 686.9 + 7.3 ≥ 500 | NOT_OPENED |
| B | 177.9 + 3.9 < 500 | CLOSED |
| package SP | 332.1 < 500; 864.9 + 10.6 ≥ 500 | NOT_OPENED |

- No FAIL input is nonzero.
- Every admission-type fact I can recount holds:
  - GateArm texts are the sealed P/M texts.
  - Labels are consistent.
  - Windows are complete.
  - There are no duplicate rows.
  - No `AsyncPipelines: skipped draw`, `GpuHangAbort`, `GpuWaitSlow`, `ErrorDeviceLost`, `--- Error ---`,
    `std::terminate` or `abort()` line appears anywhere in the log.
- The summary consequence follows item 4: "OPEN, carrying member R1".
- ROADMAP item 7 quotes exactly the recounted numbers. It was committed at 11:55:23 (`096dcfc`), after the run
  (11:48–11:54). Item 5 was in `0310cbb` (05:11, before the smoke at 05:12). Item 6 was in `3086142` (10:20:09,
  before the pred's mtime 10:20:38 and the run).

Four minor points. None changes a sealed verdict.

1. **A's NOT_OPENED depends on T_A.**
   - N⁺_A = N_A 340.2 + Z_A 128.1 + T_A 218.7. Without T_A, the upper is 468.2 + 2SE ≈ 475 < 500, and A would be
     CLOSED. In the bootstrap, N_A + Z_A never exceeded 477.7.
   - T_A rests on Δ_A = M − P `pl_em_rt_ns` = +57 ns a draw, which the design reads as warm cache: the census check
     touches the same objects right before `AcquireRenderTargets`.
   - The spans are aligned. In P the rt span runs from the `spchk` mark to the rt `MarkSplit`; in M it runs from the
     vtx mark, and the only work that moves is `DrawStatTail` (drawstat=0). So the difference is not a
     mark-placement artefact.
   - The warm-cache attribution itself is not independently evidenced. P frames are 2.77 ms longer, and the P arm's
     com phase is +584 µs because it also holds the B census.
   - The direction is conservative: it keeps A from being closed. The sealed rule governs, so the verdict stands. The
     close should state that A's border status is carried by T_A.
2. **R2's NOT_OPENED depends on the [I] constant A_tr = 1.2 ns.**
   - rpk120's "C_pt traced" (the same formula without the −A_tr·(2S+Z) term) is 511.4 ≥ 500.
   - Sensitivities of C_pt: −63.5 µs per ns of A_tr, −31.3 µs per ns of T′ and −32.2 µs per ns of B.
   - Any A_tr below about 0.18 ns would have opened R2. The value is pre-registered and sealed, so the verdict stands.
   - The package is OPEN through R1 alone, so the practical consequence is small. The R2 border is set by constants,
     not by noise; sampling cannot move it (bootstrap max 444.9).
3. **The ±8 skew widening (item 6) was never exercised.** The largest partition and nesting-count residuals per block
   window are 1–2, so item 5's ±2 would also have admitted everything. The widening did not decide any
   admissibility.
4. **Estimator choices (information).** There are two P−M price estimators (§4). The per-pair table and z̄ choices
   (§5) change the 2SE by at most 3 µs. The design text writes "Z" for both R2's null-slot count and spcen's
   timer-read add-back; the scorers keep the two apart correctly (R2 Z = 886.4 slots a frame, spcen Z = 283.0 µs a
   frame).

Robustness of the one OPEN (R1):

- Every table form clears 500: w8 658.8, d16 621.7, w4 540.7.
- Without the E term it is 630.4.
- A (W·(t_T − t_hit)) = 626.1 µs carries it: about 1 259 would-hits a frame at t_T 516.6 ns against t_hit 19.2 ns.
  The probe price P (43.7) and the losses L (33.1) are already subtracted.
- As the rule says, it is a ceiling, not a speed-up.

## 8. Smoke `smk120` recounted with the same parser

- 43 GateArm lines, 21 pairs, estimator frames P 1 658 / M 1 641.
- All correctness totals are 0 and no mismatch line appears. w1 = 0 and the M-window zeros hold.
- `r1_reset` = 32, at arm-switch rows as in the sealed run.

| disclosed in pred (source) | disclosed | my recount |
|---|---|---|
| rpk120 `--draft` R1 w4 / w8 / d16 (2SE) | 473.8 / 615.9 / 538.4 (12.6) | 473.8 / 615.9 / 538.4 (12.57) |
| R2 C_up / C_pt / C_lo (2SE) | 1 088.0 / 444.1 / −36.5 (14.9) | 1 087.98 / 444.12 / −36.48 (14.95) |
| package R point / upper (2SE) | 1 060.0 / 1 703.9 (21.3) | 1 060.0 / 1 703.9 (21.29) |
| spc120 `--draft` A point / upper (2SE) | 315.5 / 653.7 (9.3) | 315.50 / 653.73 (9.28) |
| B point / upper | −9.8 / 176.9 | −9.79 / 176.93 |
| SP point / upper (2SE) | 305.7 / 830.7 (14.4) | 305.71 / 830.66 (14.45) |
| z̄; price dt_us (2SE) | 8.73; +2 816.9 (191.7) | 8.73; +2 816.93 (191.75) |
| `smoke120.py` R1 w4 / w8 / d16 | 473.9 / 620.2 / 538.7 | **reproduced exactly** by the shift below |
| `smoke120.py` package R point / upper | 1 064.3 / 1 708.2 | 1 064.3 / 1 708.2 |
| `smoke120.py` spcen N_A / N_B / N / N⁺; price | 315.3 / −10.1 / 305.2 / 830.0; +2 783.8 | 315.3 / −10.1 / 305.2 / 830.0; +2 783.8 |

The `smoke120.py` values come from its block-0 defect, which the pred describes correctly:

- `smoke120.py` grouped rows by the `blk` label. Every pre-schedule row carries `blk=0`, so its "block 0" is rows
  2…1890, and positions 10..88 of that group are rows n=12…90.
- Those are startup frames, and none of them has `draws > 3000`. The P arm therefore silently lost block 0: P frames
  1 579 against 1 658, a difference of exactly 79.
- Removing block 0 from the P estimator in my code reproduces every `smoke120.py` number to 0.1. The R2 numbers
  coincide because the M arm is unaffected.
- All smoke verdicts match the sealed run: R1 OPEN, R2 NOT_OPENED, R OPEN, A NOT_OPENED, B CLOSED, SP NOT_OPENED. The
  sealed run did not contradict the smoke.
