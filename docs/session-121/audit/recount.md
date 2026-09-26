# Session 121 audit: independent recount of seal 01 `vfy121` and seal 02 `shp121`

**Lens: INDEPENDENT RECOUNT.** I did not modify any existing file. The only new files are in
`C:/kyty/s121/audit121/`:

- this report;
- `recount121.py`, my own parser and formulas (it shares no code with `vfy121.py`, `shp121.py` or `chk_vfy121.py`), and its output `recount121.out.txt`;
- `extra121.py`, the supplementary estimators (not sealed; not verdict inputs), and its output `extra121.out.txt`.

I did not build anything, did not run the game, did not call a scorer and did not commit. The installed exe is now `d3a981a2…`, the reference build. Both runs used `0bd21ec2…` (git `5e8e1d2`). My recount reads only the logs, the run JSON, the video index and the glitch report, so it does not depend on which exe is installed.

## 0. Verdict of the recount

**Both verdicts are CONFIRMED: `vfy121` PASS and `shp121` NO_SHIP (ADMITTED).**

For each block, I took the frame from its `GateArm:` line and used rows `n = frame + 1 + pos`. I checked the main-line
`arm=`/`blk=` labels against the block. Every sealed quantity I recomputed equals the scorers' output:

- Δ`dt_us` = **+1.321679094361** against the scorer's 1.321679094360661.
- 2SE = **154.324775054923** against 154.32477505492335.
- Δ`cpu_gpu_us` = −4.226463123754 ± 139.132313218242, identical to the scorer.
- `vfy121` per-mode means and arming differences are identical: +1 388.17 / −1 218.40 on estimator rows.

All correctness totals are 0 over all rows, and no mismatch line appears in either log. The robustness checks agree with the verdict:

- A pair bootstrap puts 0 inside the 95 % interval, [−142.9, +143.3] µs.
- The first and second halves of the run agree with each other.
- The two ABBA orders agree with each other.
- A robust estimator restricted to the main frame mode is 30 times tighter and is also null (−4.5 ± 10.1 µs).

In `shp121`, the pre-registered prediction of −350 µs (range −500…−250) is **refuted**: the whole range lies outside
the measured interval [−153.0, +155.6]. The per-pair SD is 511.8 µs, so a real −350 µs effect would have shown up at t ≈ −4.5.

There are **no MAJOR findings.** Section 5 lists six MINOR points. None of them changes a verdict.

## 1. Parser and conventions (mine)

- **Parsing.** I parse only lines that begin `FrameTrace: n=`, `FrameTrace-draw: n=` or `FrameTrace-x: n=`, and read every `k=v`. Duplicate rows per `n` are kept, so that I can test completeness. `GateArm:` and `Gate:` lines are parsed by regex, with the log line index kept. I also scan for:
  - special lines: `Tm8VerifyMismatch`, `Tm8RebindMismatch`, `TexFastVerify: MISMATCH`, `Tm8*Injected`, `Event: quit`;
  - markers, case-insensitive, in both the log and `stdout_<tag>.txt`: `gpuhangabort`, `gpuwaitslow`, `gpumarkerhung`, `gpucheckpointhang`, `errordevicelost`, `std::terminate`, `abort()`, `fatal`, `unhandled exception`, `--- error ---`;
  - skipped draws: `AsyncPipelines: skipped draw`.
- **Blocks.** Blocks come only from `GateArm:` lines. A block is complete when all 90 rows have exactly one main, one draw and one x row, and every main row carries the block's `arm`/`blk`. The window is positions 10..88 (79 rows). Estimator rows are window rows with `draws > 3000`.
- **All-row sums** cover every `FrameTrace-x` line in the log, with any `n` and duplicates included.

## 2. `vfy121` (seal 01): recount of every PASS condition

### 2.1 Structure (admission items I can check from the log)
| item | recount |
|---|---|
| `GateArm:` lines | 65; 0 deviations from `arms=4 abba=0 period=90 frame=1800+90b arm=b%4` and the exact texts `texmemo8=2|1|0|3 texfastcheck=1` |
| `Gate:` lines | 66; all match the arm starting at their frame |
| complete blocks | 64 of 65 (block 64 is cut by the end of the run, last main `n` 7594); **16 per mode**, all 16 with estimator rows (≥ 8 needed) |
| label mismatches | 0 |
| markers (log and stdout) | none; `Event: quit` at log line 922 461 |
| skipped draws | 0 |
| `GpuClockPin:` | exactly one line, mode 1 |
| env / hold / attempt / prereg | env is the expected 11 `KYTY_*` plus `VK_SDK_PATH`; hold 240; one attempt `ok`, `hold_exit` null; prereg sha `f681d4db…` = seal |
| gates text | equal to `gates_base.txt` (99 names, sha `303a7849…`); `texmemo2 texfastcheck fslean m4baton mutsite shadowresolve` = 0; `texmemo8/r1cen/r2cen/spcen` not in the base |
| idle | `gpu_util_median` 0.0; the GPU clock log shows only reason `0x400`; SM median 2 362 MHz, max 69 °C |
| seal integrity now | all 19 sha256 entries in `SEALS121.txt` match the files on disk today |

### 2.2 Hard FAIL conditions: all clear
- **All-row sums:** `tm8_bad` 0, `tm8_vctl_bad` 0, `tm8_relive` 0, `tm8_rbbad` 0 and `texfast_bad` 0, over 7 593 x lines. Every line carries every field.
- **Structural zeros:** `tm8_inject_miss` 0, `tm8_rbinject_miss` 0, `tm8_dcc_chg` 0.
- **Mismatch lines:** 0 `Tm8VerifyMismatch`, 0 `Tm8RebindMismatch`, 0 `TexFastVerify: MISMATCH`.
- **Fatal markers:** none at all, so none can fall in a mode-2/3 arm.
- **Video glitches:** 0, per `vfy121_glitch.txt`.

### 2.3 Soft FAIL conditions: all clear (my numbers)
| condition | recount |
|---|---|
| `tm8_x2`, `tm8_cenoff` all rows | 0, 0 |
| mode-3 control alive | window sums `tm8_inject` 1 525 and `tm8_rbinject` 54 816; 4 `Tm8VerifyInjected:` and 4 `Tm8RebindInjected:` lines. All 8 lines fall under a mode-3 arm (last `GateArm` before each line) |
| control leak modes 0/1/2 (window) | 0 / 0 / 0 |
| verify alive modes 2/3 (window `vchk`, `gain`) | 1 562 462 / 1 562 462 and 1 557 308 / 1 557 308 |
| dark_01 (22 per-lookup counters, modes 0/1 window) | all 0 |
| m1_fill (every mode-1 block window) | 15 338 … 17 571, all > 0 |
| m0 fill / evict (window) | 0 / 0 |
| arming, estimator rows (what the scorer gates) | Δ`tex_hits` **+1 388.2**; Δ key misses **−1 218.4**; mode-0 key misses 1 419.4 |
| arming, window rows, all draws (what item 5 and pred 01 say) | Δ`tex_hits` **+1 090.9**; Δ key misses **−1 183.3**; mode-0 key misses 1 379.1. Passes too (see MINOR 1) |
| identities (32 mode-2/3 block windows) | 0 failures. Worst \|res\|/tol: look = hit+miss+stale **1.000** (block 48, −8 of ±8, see MINOR 5); vchk = gain 0.125; identity 11 0.172; identity 13 0.109; identity 1 (≤) margin ≥ 942 |
| identity 11 on mode totals | mode 2: −1 021 (−0.175 per 10 000); mode 3: −440 (−0.076 per 10 000) |
| ratio bands [1/80, 1/50] | `vctl/(hit−gain)` 0.01544–0.01574 and `pb_n/look` 0.01546–0.01575 (xorshift 1/64 = 0.015625). Nearest edge: 81 % of the way to the lower bound |
| identity 19 (reported) | `0 < tm8_rbchk ≤ texfast_ok + texfast_no` in all 32 blocks |

Reported quantities that I reproduce:

- Gained hits: 1 236.1 (mode 2) and 1 232.0 (mode 3) a frame, inside the band [600, 2 000].
- Probe: 9.69 / 8.49 ns (timed / null) per probe, i.e. **1.21 ns net** per probe, ≈ 56 µs a frame.
- `tm8_ddiff` 0.5 a frame; `tm8_dlose` 58.5; `tm8_alias` 0; `tm8_renorm` 0.
- BDA regime **NEW** in every block, with `bda_scan` block means between 47.7 and 103.9.

### 2.4 Video
My checks:

- `ffprobe -count_packets` gives 7 604 packets at 960x540.
- My own count of the `.idx` file is 7 604 entries, monotone 0..7603.
- Presents (last main `n`) are 7 594, so |7 604 − 7 594| = 10 ≤ max(120, 151.9).
- The glitch report says 0 one-frame glitches, and `vidframes_vfy121/` is empty.

**PASS on every condition.**

### 2.5 Indicative only: mode 1 against mode 0 in the verify run (NEW regime)
This is not a speed number: there is no ABBA and `texfastcheck=1` is in both arms. It is the only look at the NEW regime, where the census was taken.

- Mode 1 (the mean of blocks b−1 and b+3, which cancels linear drift) minus mode 0 (block b), for `dt_us`: **+71.6 ± 181.1** (n = 15).
- The same for `cpu_gpu_us`: +77.8 ± 195.9.

The −350 prediction lies outside this interval too. The verify run therefore gives no sign that the NEW regime would have rescued the prototype.

## 3. `shp121` (seal 02): recount

### 3.1 Structure and admission (from the log)
| item | recount |
|---|---|
| `GateArm:` | 89 lines; 0 deviations from ABBA `(0,1,1,0)`, `arms=2 abba=1 period=90 frame=1800+90b`, texts exactly `texmemo8=1` / `texmemo8=0` |
| `Gate:` | 45 lines, only `texmemo8`, all matching their arm (1 initial set plus 44 changes) |
| complete blocks | 88 of 89 (block 88 is cut at the end); **44 pairs**, 22 P-first and 22 M-first |
| window / estimator rows | 3 476 / 3 476; 3 182 (P) / 3 203 (M), identical to the scorer |
| markers, skipped draws, mismatch lines, `*Injected:` | none |
| `GpuClockPin:` | one line, mode 1; env = the expected 10 `KYTY_*` plus `VK_SDK_PATH`; hold 300; one attempt `ok`; prereg sha `3b951163…` = seal |
| idle | `gpu_util_median` 0.0; clock reason `0x400` only; SM median 2 362 MHz, max 72 °C |
| arming proof | all 44 P blocks have window `tm8_fill` > 0 and `tm8_evict` > 0 |
| M leak | every `tm8_*` counter sums to 0 over the M window rows |
| switch counters in windows | `tm8_inval` = `tm8_mode` = 0 on every window row. Where they actually fire is described in MINOR 3 |
| verify leak (all rows) | all 22 mode-≥2 counters are 0 (`tm8_look` 0) |
| `tm8_x2`, `tm8_cenoff` | 0, 0 |
| correctness (all rows) | `tm8_bad`, `tm8_vctl_bad`, `tm8_relive`, `tm8_rbbad` all 0; no mismatch lines |
| arming (paired window rows) | Δ`tex_hits` **+1 434.4** (≥ +300); Δ key misses **−1 387.9** (≤ −300); P key misses 273.7, M key misses 1 661.6. Ceiling holds: 1 434.4 ≤ 1 661.6 |
| identities (88 block windows) | 0 failures. `b_texn` = hits + key misses + stale + null: worst \|res\|/tol 0.008; on run totals +74 (0.002 per 10 000). fill ≤ …, evict ≤ fill, evict ≤ collide and evict_view ≤ evict all hold |
| BDA regime | **OLD in both arms and in all 44 pairs.** Per-pair block `bda_scan` is 1 165–1 305 (P) and 1 116–1 299 (M); arm means 1 246.8 / 1 243.3. No regime split, so no NOT_EVALUABLE |
| sealed `vfy121` | `runs121/vfy121.score.json` is PASS with scorer sha `43359b14…` (= `VFY_SCORER_SHA`) and file sha `bcc00a82…` (= seal 02 entry) |

### 3.2 Estimator (sealed rule)
| quantity | recount |
|---|---|
| **Δ`dt_us` (P − M)** | **+1.3 ± 154.3 µs** (2SE, 44 pairs), t = 0.02; P 32 604.7, M 32 603.4 |
| SHIP test Δ + 2SE < 0 | +155.6 → **false ⇒ NO_SHIP** |
| Δ`cpu_gpu_us` (reported) | −4.2 ± 139.1, t = −0.06; P 31 923.0, M 31 927.2 |
| game speed | 0.5112 / 0.5112 (−0.004 %) |
| frame-weighted means (not the estimator) | +3.8 |

### 3.3 Robustness (my additions; none are verdict inputs)
| check | Δ`dt_us` | Δ`cpu_gpu_us` |
|---|---|---|
| pair bootstrap, 2 000 resamples (seed 121) | mean +1.0, 95 % CI **[−142.9, +143.3]**, P(Δ<0) = 0.500 | −4.1, [−139.9, +128.1], P(Δ<0) = 0.520 |
| first half (22 pairs) / second half (22) | +24.3 ± 184.1 / −21.7 ± 251.8 | +21.2 ± 187.5 / −29.6 ± 209.5 |
| slope of per-pair Δ over time | −2.8 µs a pair (≈ 0) | — |
| P-first (A B) / M-first (B A) pairs | +81.8 ± 227.0 / −79.2 ± 208.6 | — |
| by BDA regime | all 44 pairs OLD/OLD: +1.3 | — |
| all window rows (no draws filter) | −81.9 ± 120.1 | — |
| per-block medians | −15.2 ± 17.1 | −13.9 ± 42.5 |
| main-mode rows only (25–40 ms) | **−4.5 ± 10.1** | −14.6 ± 54.7 |
| short (<25 ms) / long (>40 ms) frames, ‰ | −4.0 ± 9.1 / −3.8 ± 4.9 | — |
| `cpu_gpu` per draw (post hoc) | — | −21.5 ± 14.6 ns a draw (≈ −0.35 %) |

About the ABBA order effect: the first block of each pair runs about 80 µs slower whichever arm it carries (t ≈ 0.7 each). ABBA cancels this by design.

**The null is robust:** every estimator puts 0 inside its interval, or sits within about 1 SE of it, and none approaches −250.

The one post-hoc hint is the CPU per draw, at t ≈ −2.9. At 5 330 draws a frame it corresponds to about −115 ± 78 µs of GuestGpu CPU a frame. It was chosen after seeing the data, from several candidates, so it is not a finding. It bounds, rather than contradicts, "no effect".

### 3.4 Why the sealed estimator is noisy, and what `dt_us` can see here
- **Frame mix.** Estimator rows fall into three groups:
  - ≈ 94.6 % main-mode frames at 32–34.5 ms (median 33 283);
  - ≈ 4.9 % short frames at ≈ 16.7–17 ms, with ≈ 3 100 draws and `cpu_gpu` ≈ 17.0 ms;
  - ≈ 0.5 % long frames at ≈ 48 ms.

  One extra short frame in a 72–79-row block moves that block's mean by ≈ 210 µs, and this is what drives the per-pair SD of 512 µs. The main-mode estimator is 15 times tighter.
- **The draws cutoff lands in the short-frame population.** `DRAWS_MIN = 3000` excludes 294 (P) and 273 (M) window rows. These rows average 16.8 / 16.7 ms and ≈ 2 870–2 880 draws, while 312 short frames with ≈ 3 100 draws are kept. The estimator's block means therefore depend on which side of 3 000 each short frame lands.
- **The main mode sits against the 2-vblank grid.** Within main-mode rows, `dt_us` rises with `cpu_gpu_us` (r = 0.63) but compressed:
  - `cpu_gpu` 30.0 ms → `dt` 32.6 ms;
  - `cpu_gpu` 32.5 ms → `dt` 33.3 ms;
  - `cpu_gpu` 33.5 ms → `dt` 34.0 ms.

  Below ≈ 32.5 ms, the local slope of `dt` against CPU is ≈ 0.3–0.5. A pure CPU saving therefore reaches `dt_us` at less than full rate in this scene state. That argues for `cpu_gpu_us` as the more direct work metric. `cpu_gpu_us` is null too (−4.2 ± 139.1; main mode −14.6 ± 54.7), so the conclusion does not depend on this.

## 4. Consistency with the ROADMAP record (items 6 and 8)

- **Item 6.** "+1 388 на кадр, промахи ключа 1 419 → 201" are the estimator-row figures (draws > 3000). The window-row, all-draws figures that item 5 defines are +1 091 and 1 379 → 196 (−1 183, −86 %). The other claims in item 6 hold:
  - ≈ 1 254 gained hits verified a frame;
  - ≈ 1.55 M verifications (my count: 1 562 462 + 1 557 308 = 3.12 M checks over modes 2 and 3 in the windows; item 6's "≈ 1,55 млн" matches one mode);
  - ≈ 710 sampled checks a frame;
  - 7 604 video frames and 0 glitches.
  - The speed disclaimer (mode 1 33 677 against mode 0 33 621) is right: those are estimator-row means.
- **Item 8.** All the numbers are confirmed: +1.3 ± 154.3 (upper 155.6), −4.2 ± 139.1, 51.12 %, `tex_hits` +1 434, key misses 1 662 → 274 (−1 388, −84 %), `texfast_rec` −1 192, `texfast_no` −1 325, OLD in both arms, 44 pairs, 0 correctness errors.

  Two phrases go slightly beyond what was measured:
  - "не дали НИЧЕГО … на времени потока" should read "|Δ| < ≈ 0.14–0.15 ms on both wall and thread time (2SE)". The item's own parenthetical already says this.
  - The closing scope "на Sky Garden этой сборки" should say that the sealed measurement is **OLD regime only**. See MINOR 2.

  Of the item's candidate causes, "проба 8 путей … съедают выигрыш" is weakened by the verify run's own probe timer, which measured 1.21 ns a probe, ≈ 56 µs a frame. The LRU write is not timed, so it stays a candidate.

## 5. Findings

**MAJOR:** none.

**MINOR**

1. **`vfy121` gates arming on estimator rows; the recorded rule says window rows with all draws.** ROADMAP item 5(1) says "средние на кадр по строкам ОКНА (позиции 10–88, все draw)", and pred 01 §3 says "window means". `vfy121.py` (docstring: "mode-1 estimator rows") computes the difference on rows with `draws > 3000`. `shp121.py` follows item 5 (window rows). The seal is honoured as sealed, and both readings pass with a wide margin (+1 091 / −1 183 against +1 388 / −1 218; floor ±300), so the verdict is unaffected. The two scorers still measure "the same" rule differently, and item 6 quotes the estimator-row numbers.
2. **The sealed ship measurement is OLD-regime only, while the census and prediction came from NEW.** `cen120` had `bda_scan` 58.4 / 58.5 (NEW). `shp121` had 1 246.8 / 1 243.3 (OLD) in all 44 pairs. `vfy121` was NEW. The pre-registration did not require a regime, only that the two arms share one, so admission holds. The closure should still carry the regime. My indicative NEW-regime comparison inside `vfy121` (§2.5) is +71.6 ± 181.1, so there is no sign that NEW would have paid. I see no reason to reopen the track.
3. **The scorer docstring misplaces the switch row.** `shp121.py` says "the switch rows lie at block positions 0-2". Measured: `tm8_inval`/`tm8_mode` fire at **position 89 of the outgoing block** in 42 of 44 changes, and at position 0 of the incoming block in 2. In `vfy121`, all 64 transitions land at position 89. Mode-0 blocks carry mode-3 per-lookup counts (`tm8_look` 2 747, `tm8_rbinject` 3, …) on that row only. So row `n = frame_{b+1}` holds work from the next arm but is labelled with the old arm. Both scorers' windows stop at 88, so no sealed number is affected. A future scorer that uses the full block, or window end 89, would mix arms. The full-block Δ (0..89) is +20.1 ± 153.6, which is also null.
4. **Estimator noise is dominated by the short-frame mix, and the `DRAWS_MIN = 3000` cutoff cuts through that population** (§3.4). Neither changes the verdict. For the power claim, the pre-registered "2SE ≈ 0.14–0.18 ms" held (154.3). Future ship ABBAs in this scene could pre-register a main-mode estimator (≈ ±10 µs `dt`, ≈ ±55 µs `cpu_gpu`) alongside the block mean.
5. **The NEAR identity `tm8_look = tm8_hit + tm8_miss + tm8_stale` passes with zero margin in one block** (block 48, window residual −8 against ±8). It is pure row skew: adjacent rows carry −25/+25 and −5/+5, the whole-block residual is +5, and the sum over all 32 windows is −10. This is a window-edge artifact, not a counting defect. Still, ±8 is a tolerance the data actually reaches.
6. **Item 6's quoted arming numbers use a different row set from item 5's definition** (see item 1). The item 8 wording "НИЧЕГО … на времени потока" is stronger than a 2SE of 139 µs supports. §4 gives suggested wording.

## 6. Key numbers
**`vfy121`**

- 64/65 complete blocks, 16 per mode.
- All-row sums: bad 0, vctl_bad 0, relive 0, rbbad 0, texfast_bad 0, inject_miss 0, rbinject_miss 0, dcc_chg 0, x2 0, cenoff 0.
- 0 mismatch lines; 4 + 4 injected lines, all in mode 3.
- Control (mode-3 window): inject 1 525, rbinject 54 816.
- Verify checks: mode 2 1 562 462, mode 3 1 557 308.
- Arming (estimator rows): +1 388.2 / −1 218.4. Arming (window rows): +1 090.9 / −1 183.3.
- Video: 7 604 frames = 7 604 index entries = 7 604 packets; 7 594 presents; 0 glitches.
- BDA regime NEW.

**`shp121`**

- 44 pairs; Δ`dt_us` **+1.3 ± 154.3** (upper +155.6); Δ`cpu_gpu_us` −4.2 ± 139.1.
- Bootstrap 95 % CI [−142.9, +143.3]; halves +24.3 / −21.7; main-mode −4.5 ± 10.1.
- Arming +1 434.4 / −1 387.9 (M key misses 1 661.6).
- Correctness zeros everywhere; BDA regime OLD/OLD in 44 of 44 pairs.
- Game speed 51.12 % in both arms.
- Prediction −350 [−500, −250] is refuted.

## 7. Recommendations
1. Keep both verdicts and the sealed consequence: NO_SHIP, the R1 track closed with +1.3 ± 154.3 µs, and `texmemo8` stays 0 as a measuring tool.
2. In the closure (FACTS / ROADMAP), state that the sealed number is from the **OLD BDA regime**, and cite the NEW-regime indication from `vfy121` (+72 ± 181, not ABBA) as the only NEW evidence.
3. Record that `vfy121` gated arming on estimator rows, against item 5's window rows. Quote both figures, or the window-row ones, in the close.
4. Correct the switch-row statement for future scorers: the arm change lands on position 89 of the outgoing block (the row numbered like the next `GateArm` frame). Keep the window end at 88.
5. For future ship ABBAs in this scene, also pre-register a main-mode estimator and a `cpu_gpu_us` reading. `dt_us` near the 2-vblank grid responds to CPU savings at a slope below 1, and the 5 % short-frame mix sets 2SE ≈ 150 µs for 44 pairs, which needs ≈ 105 pairs to reach 2SE = 100.
6. If R1 or the census-to-wall calibration (item 8 decision) is revisited, time the LRU write as well as the probe. The probe alone (1.21 ns, ≈ 56 µs a frame) cannot absorb a ≈ 0.7 ms gross gain.
