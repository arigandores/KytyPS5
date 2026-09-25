# Audit 119 — independent recount of seal 01 `g2_119` (runs `sh119`, `mut119`)

Lens: independent recount. The parser is my own (`C:/kyty/s119/audit119/recount119.py`). Nothing is imported or copied
from `g2_119.py` or `a104.py`. It is written from the session-104 pre-registration `C:/kyty/s104/pred/02_a_stage1.md`
§3–§6 and the session-119 pre-registration `C:/kyty/s119/pred/01_g2_119.md`. The logs are read in binary mode. No game
run, no build, and no existing file was edited. Outputs: `recount119.out.txt`, `recount_smokes119.out.txt`,
`sensitivity119.out.txt`, `bootstrap119.out.txt` (all in this folder).

**Verdict: CONFIRMED.** Every number in ROADMAP 119 item 4 and in `runs119/g2_119_score.txt` reproduces to 0.1 µs:
G₂ = 2 216.5 µs < 3 000, so route A is CLOSED for maximum FPS as sealed. All 16 hashes in `SEALS119.txt` match. Both
runs carry the sealed pre-registration sha and the `d3a981a2…` binary. Each run has 80 blocks and 40 pairs, with no
arm mislabel. I found no MAJOR issue and seven MINOR ones (§8). The decision is statistically solid (bootstrap 95 %
range [2 041; 2 465], 0 of 2 000 resamples reach 3 000). It rests on the sealed model, though: the ceiling G₂^ = 3 724
sits entirely above the bar.

---

## 1. Seals, hashes, provenance — CONFIRMED

| check | result | evidence |
|---|---|---|
| every sha in `SEALS119.txt` vs the file now | **16/16 equal** (15 sealed files + the post-seal tally `mut_g2_119.out.txt` `c2a23435…`) | `pred/01_g2_119.md` `e22c96a7…` 7 596 B; `g2_119.py` `2f089ef5…`; `test_g2_119.py` `7666f91f…`; `mut_g2_119.py` `afa01a07…`; `make_g2_119.py` `5f7c86cb…`; `go119a.sh` `3a268e15…`; `gates_base.txt` `303a7849…`; `procload.py` `d9e7a777…`; `enter_scene.py` `51558cf1…`; `launch_run.py` `e383aed3…`; `run_safety99.py` `77e685e5…`; `kyty_emulator_d3a981a2.exe` `d3a981a2…`; `s104/a104.py` `dfa2313a…`; `mutlib.py` v4.1 `db82ef4b…`; `test_g2_119.seal.out.txt` `36b77a3e…` |
| `go119a.log` "files:" prefixes (printed before each run) | the 7 printed 16-hex prefixes are identical in both runs and equal the seal | `go119a.log` lines 3 and 11 |
| git copies `docs/session-119/seal01/*` (HEAD) vs harness | all 13 byte-identical (incl. score txt/json, `go119a.log`, PRESEAL) | sha comparison |
| scorer constants | `PRED_SHA` = `e22c96a7…`, `PRED_BYTES` = 7596, `BINARY_SHA` = `d3a981a2…`, `GATES_SHA` = `303a7849…`, `F_SERIAL` 0.555, `F_SENS` 0.564, `SPINE_DIRECT_US` 959, `BAR_US` 3000, `C_TS_NS` 3.96, `W_E` 675.455 + 440.120, `MIN_PAIRS` 30 | `g2_119.py:83-111` |
| run json prereg | `sh119.json` / `mut119.json`: `prereg.sha256` = `e22c96a7…`, `bytes` 7596 = sealed pred | json |
| run json binary | both `binary_sha256` = `d3a981a23fc1c5df…290f64`; installed exe now `d3a981a2…` (mtime 00:35:43, the `mut119` install) | json, sha of `ps5 em/kyty_emulator.exe` |
| env | both runs: `KYTY_GATE_SCHEDULE` exactly the `go119a.sh` arm texts, `KYTY_GATE_SCHEDULE_ABBA=1`, `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`, `KYTY_FRAME_TRACE=lite`; **no** `KYTY_GPU_CHECKPOINTS`, **no** `KYTY_REC`; hold 300.1 s, one attempt, `hold_exit` None | json |
| gates | json `gates` text equals `gates_base.txt` after stripping the CRLF/trailing newline; `gates.req` has the same tokens | byte compare |
| spk118 constants | f₂ = 0.555 = `spk118` median `k4_w2_fmax` ("fmax median 555"); 959 = `spine_ns` 958 833.7 ns | `C:/kyty/s118/runs118/spk118.score.txt` |

Timeline: ROADMAP 118 item 6 at 23:28:54 (`f11dda7`), 119 item 1 at 23:30:00 (`fe8faf6`), then smoke `smk119s`
(launched 23:38:45) and `smk119m` (23:42:26–23:45:49). Item 3 was committed at 23:59:04 (`b110592`), and the edits it
announced followed (`fix_go119a_guard.py` 00:00:58, `go119a.sh` 00:01:01, `pred` 00:01:30). `seal119.py` filled
`PRED_SHA` at 00:25:40, fixtures ran at 00:26:25 (89/89), and `mutlib` finished at 00:29:18 (40/40, controls 3/3). The
seal commit `3aaddb6` landed at 00:29:24, before the `sh119` request at 00:29:29 (run 00:30:05–00:35:29), then `mut119`
(00:36:06–00:41:29), the score at 00:41:40 and ROADMAP item 4 `e0be82b` at 00:42:11. ROADMAP changed append-only from
`f11dda7` to `e0be82b` (72 insertions, 0 deletions). A scan of `C:/kyty` and the emulator folder for files modified
between 00:30:05 and 00:41:29 finds only the runs' own artefacts (log, stdout, gpuclk, json, `gates.req`, the
emulator's `_kyty*`, `_PipelineCache`). No commit landed in that window, and both design reports were written at
23:44, before the sealed runs.

## 2. Population — CONFIRMED

Convention, derived from the log rather than from the scorer: the rows with `blk=b` are exactly `n = 1801+90b …
1890+90b` (for example `blk=1` starts at `n=1891`, just after `GateArm … block=1 frame=1890`), so the frame of row n is
n − 1 and idx = n − 1801 − 90b.

| | `sh119` | `mut119` |
|---|---|---|
| rows (main / draw / x lines) | 9 570 / 9 570 / 9 570, n = 2…9571 contiguous, 0 duplicate n, 0 duplicate field names | 9 508 ×3, n = 2…9509 contiguous |
| field origin | `cpu_gpu_us`, `dt_us`, `draws`, `dispatches`, `gpu_busy_us` only on `FrameTrace:`; `spin_gpu_us`, `rec_n`, `bda_n`, `da_walk_us`, `da_queue_us` only on `FrameTrace-draw:`; `a_*`, `mw_n`, `mh_*`, `pl_*`, `sh_*`, `rt_*`, `gm_ops`, `da_wjobs` only on `FrameTrace-x:` | same |
| rejected blocks | 0, 1, 2 (first kept frame < 2100); 86 incomplete | 0, 1, 2; 85 incomplete |
| usable but outside a complete quartet | 3, 84, 85 | 3, 84 |
| selected | **80 blocks, 40 pairs (20 AB + 20 BA)**, quartets 1…20 | **80 blocks, 40 pairs (20 + 20)** |
| `arm=` of every row vs ABBA position (0,1,1,0) | 0 mismatches | 0 mismatches |
| `GateArm:` lines | 87 (blocks 0…86), all `frame = 1800 + 90·block`, `period=90 abba=1`, arm = ABBA position | 86 (0…85), same |
| arm texts | arm 0 `shadowresolve=0 shadowmask=3`, arm 1 `shadowresolve=1 shadowmask=3` | arm 0 `mutwide=0 mutsite=1 amut=1 plkstat=1 pathlap=1`, arm 1 `mutwide=15 …` |

These match the score's "pairs 40 (orientations [20, 20]), blocks 80, excluded [3, 84, 85]" / "[3, 84]" and the json
`selection.rejected`. The sealed pre-registration expected 36–38 pairs; 40 were obtained (MINOR m4).

## 3. Levels and differences — CONFIRMED (own parser = score, to 0.1)

| quantity | `sh119` arm0 / arm1 | `mut119` arm0 / arm1 |
|---|---|---|
| `dt_us` | 31 047.3 / 32 767.1 | 32 195.0 / 32 728.4 |
| `cpu_net` = `cpu_gpu_us − spin_gpu_us` | **30 252.5** / 31 858.9 | 31 457.9 / 31 610.1 |
| `draws` | 5 013.0 / 5 017.3 | 5 012.8 / 5 061.8 |
| `gpu_busy_us` | 12 923.0 / 12 925.3 | 12 956.6 / 12 922.1 |
| `rec_n` | 10 860.4 / 10 870.8 | 10 858.8 / 10 962.6 |
| `a_mut_us` | 0 / 0 | **13 193.2** / **21 642.3** |
| `a_hold_us` | 0 / 0 | 29 193.6 / 29 632.2 |
| `mw_n` | 0 / 0 | 0 / 10 542.9 |
| `mh_prog_us`, `mh_emit_us` | 0 | 6 492.9 / 6 600.9; 7 655.0 / 7 680.9 |
| `pl_prog_hold_us` | 0 | 4 674.6 / 4 701.7 |
| `pl_em_rec_ns/1000`, `pl_em_com_ns/1000` | 0 | 1 244.3 / **1 246.0**; 2 298.1 / **2 299.9** |
| `da_walk_us − da_queue_us` | 1 266.8 / 1 286.4 | **1 268.2** / 1 299.5 |
| `sh_jobs`, `sh_us`, `sh_push_us` | 0 / 4 997.6; 0 / 3 547.9; 0 / **533.8** | 0 |
| d `cpu_net` (mean, 2SE, t, n) | **+1 645.39 ± 157.40, t 20.91, n 40** | **+61.80 ± 155.63**, t 0.79, n 40 |
| d `dt_us` | +1 767.04 ± 177.12, t 19.95 | +71.58 ± 164.10 |
| d `draws` | +6.67 ± 19.88 | +3.42 ± 19.03 |

The `spin_gpu_us` subtraction matters for the tax. In `sh119` arm 1 the GuestGpu spin rises by 104 µs (21.1 → 124.8;
paired d +104.0), so the sealed T₂ on `cpu_net` (1 645.4) leaves out 104 µs of spin that one shadow reader causes. The
sealed definition therefore leans slightly in favour of route A, which makes it conservative for a closure. `G_wall`
covers the wait part.

## 4. G₂ terms — CONFIRMED

| term | definition (pred/02 §5, pred/01 rule) | recount | score / ROADMAP 119 item 4 |
|---|---|---:|---:|
| `cpu_net` | `sh119` arm-0 level | 30 252.517 | 30 252.5 |
| T₂ (2SE) | d `cpu_net` of `sh119` | 1 645.391 (157.404) | 1 645.4 (157.4) |
| T₂ on `dt` (2SE) | d `dt_us` of `sh119` | 1 767.039 (177.122) | 1 767.0 (177.1) |
| `sh_push` | `sh119` arm-1 level | 533.810 | 533.8 |
| `S_lo` | `mut119` arm-0 `a_mut_us` | 13 193.190 | 13 193 |
| `S_raw` | `mut119` arm-1 `a_mut_us` | 21 642.345 | 21 642 |
| `P_mw` (2SE) | d `cpu_net` of `mut119` | 61.797 (155.635) | +61.8 (155.6) |
| `T_in` | arm-1 level of `5·pl_em_n + 3·(pl_prog_n + pl_pipe_n + pl_cs_n) + a_mut_n` | 124 955.55 (sum of separate levels: 124 951.48) | 124 956 |
| dI | 3.96·T_in/1000 | 494.824 | 494.8 |
| `E_rec` / `E_com` | arm-1 `pl_em_rec_ns` / `pl_em_com_ns` ÷ 1000 | 1 245.955 / 2 299.900 | 1 246.0 / 2 299.9 |
| `S_now` | S_raw − max(P_mw,0) − dI | 21 085.724 | 21 085.7 |
| `E_move` | E_rec + 1 115.575 | 2 361.530 | 2 361.5 |
| `S_ctx` | S_now − E_move | 18 724.194 | 18 724.2 |
| spine | max(`mut119` arm-0 `da_walk_us − da_queue_us`, 959) | max(1 268.172, 959) = 1 268.172 (`sh119` arm-0 proxy 1 266.845) | 1 268.2 |
| **G₂** | cpu_net − [S_ctx + 0.555·(cpu_net − S_ctx)] − spine − T₂ | **2 216.540** | **2 216.5** |
| G₂ at f 0.564 | | 2 112.785 | 2 112.8 |
| G_wall | G₂ − max(0, d dt − d cpu_net) | 2 094.892 | 2 094.9 |
| ceiling: S_now^, E_move^, S_ctx^, T₂^ | S_raw − max(P+2SE,0) − 2dI; E_rec + E_com; —; max(0, T₂ − 2SE − sh_push) | 20 435.265, 3 545.855, 16 889.410, 954.177 | 20 435.3, 3 545.9, 16 889.4, 954.2 |
| **G₂^** (decides nothing) | | **3 724.234** (f 0.564: 3 603.966) | 3 724.2 (3 604.0) |
| T₂ that brings the central G₂ to 3 000 | G₂ + T₂ − 3 000 | 861.931 | 861.9 |
| spine from `pl_pref` (meaningless at `dawalk=1`) / its G₂ | arm-0 `pl_pref_ns/1000 − da_queue_us` | −1 227.048 / 4 711.761 | −1 227.0 / 4 711.8 |
| H/M | arm-1 `pl_prog_hold_us` / `mh_prog_us` (arm 0: 0.720) | 0.712 | 0.712 |
| cross-run instrument price | `mut119` arm-0 cpu_net − `sh119` arm-0 cpu_net | 1 205.362 | 1 205.4 |
| arm-0 render area (Σ`rt_kpx`/Σ`rt_att`) | sh 2 007.829, mut 2 007.799 | −0.002 % | 0.002 % |

ROADMAP 119 item 4's printed arithmetic "30 252,5 − [18 724,2 + 0,555·11 528,3] − 1 268,2 − 1 645,4 = 2 216,5" is
exact. The rule's branch is G₂ < 3 000, hence `A_CLOSED_FOR_MAX_FPS`, consistent with the score, the json
(`verdict.verdict`) and the sealed pre-registration's table. NOT_EVALUABLE does not apply: both runs are admitted and
the area differs by 0.002 %, far under the 3 % limit.

## 5. Arming checks and controls — CONFIRMED (own computation)

| check | recount |
|---|---|
| `MW_DARK_ARM0` | arm-0 level 0; arm-0 total 0 vs arm-1 12 202 208 |
| `MW_IDENTITY_ARM1` | `mw_n` / (2·`mh_n` + `mh_disp_n` + `bda_n`) − 1 = **−0.27 %** (score A2 −0.003) |
| `AMUT_ARMED` | `a_mut_us`, `a_mut_n` > 0, both arms |
| `MUTSITE_HOLD_IDENTITY` | `a_hold_n` / (`mh_n` + `mh_disp_n`) − 1 = −0.00 % / +0.00 % |
| `PLKSTAT_IDENTITIES` | `pl_prog_n`/`mh_n` −0.40 % both arms; `pl_cs_n`/`dispatches` 0.00 %; hold > 0 |
| `PATHLAP_ARMED` | `pl_em_n`/`mh_draws` 0.00 %; emit chain Σ`pl_em_*`/`mh_emit_us` 0.979 / 0.980 ∈ [0.95, 1.01]; `pl_pref_n` 8 |
| `OTHER_INSTRUMENTS_DARK` (mut) | `sh_jobs` 0 over kept rows (`da_wjobs` 18 567 over kept rows, dropped from the check by ROADMAP 119 item 1) |
| `SH_DARK_ARM0` | arm-0 total 0 vs arm-1 5 825 182 |
| `SH_JOBS_PER_DRAW` | 0.9961 ∈ [0.90, 1.02] |
| `SH_NO_DROP` | `sh_drop`/`sh_jobs` = 0 |
| `SH_ONE_WORKER` | exactly one line, `ShadowResolve: worker 0 started` (log line 438 465, right after the block-1 `GateArm`); `mut119` has none |
| `INSTRUMENTS_DARK` (sh) | `a_hold_us`, `a_mut_us`, `mw_n`, `pl_em_n`, `pl_proc_n`, `pl_prog_n` all 0 over kept rows |
| bands (both runs, both arms) | `dt_us`, `rec_n`, `gpu_busy_us` inside [28 000, 40 000], [9 000, 13 000], [10 000, 16 000] |
| `MARKERS_OFF` / `NO_FLOOR` | `gm_ops` 0; no non-zero `bf_*` field on any row of either log |
| work / area mirror | work +0.132 % (sh), +0.068 % (mut); selected area split −0.004 % / −0.005 %; pair match 100 % at 0.5 % |
| log markers | per log: 1 `GpuClockPin: mode 1`, 2 `RecordThread: started`, 0 `GPU checkpoints`, 0 `GpuHangAbort`, 0 fatal markers (`--- Error ---`, `--- Fatal Error ---`, `--- std::terminate ---`, `--- abort() ---`, `ErrorDeviceLost`, `Unhandled exception:`, `GpuWaitSlow:`, `AsyncPipelines: skipped draw`); none in `stdout_*.txt` / `*.stdout.txt` either |

## 6. Disclosed smoke numbers — CONFIRMED

The same parser on the unsealed smokes (draft geometry: schedule from 900, first kept frame ≥ 1200) gives 22 pairs
each. `smk119s`: T₂ **+1 983.1 ± 414.7**, on `dt` +2 116.6 ± 470.8, arm-0 `cpu_net` **31 695.0**, one worker line.
`smk119m`: `S_lo` **13 619.4**, `S_raw` **22 504.2**, `P_mw` **+17.9 ± 452.5**, spine proxy **1 369.4** (uninstrumented
`sh` proxy 1 288.9), `pl_em_rec` **1 267.4**, `pl_em_com` **2 350.5**, `mw_n` identity −0.26 %. Draft G₂
**2 028.8**, ceiling **3 989.0**, T₂ to the bar **1 011.9**. These equal every figure in `pred/01_g2_119.md` "Before the
seal". The sealed T₂ (1 645) lies within the smoke's 2SE (1 983 ± 415).

## 7. Robustness (no decision weight; the sealed rule is a point rule)

| variant | G₂ |
|---|---:|
| sealed | 2 216.5 |
| quartet bootstrap of the sealed estimator, 2 000 resamples per run: p2.5 / p50 / p97.5 / max | 2 040.9 / 2 257.6 / 2 465.2 / 2 572.8; **share ≥ 3 000 = 0** |
| levels as means of block means (not medians) | 2 273.5 |
| S_raw from the paired design (S_lo + d `a_mut_us` = 13 193.2 + 8 291.7 ± 100.7) | 2 286.6 |
| S_raw rescaled to the draw level of `sh119` arm 0 (5 013.0 / 5 061.8) | 2 309.4 |
| the whole cross-run instrument price (1 205.4) inside S instead of dI (494.8) | 2 532.7 |
| f = 0.5 (a perfect half cut, the minimum at W = 2) | 2 850.6 |
| spine at its floor 959 / no spine at all | 2 525.7 / **3 484.7** |
| T₂ − 2SE / T₂ on `dt` | 2 373.9 / 2 094.9 |
| E_move^ (E_rec + E_com) with the other terms central | 2 743.6 |
| ceiling S_ctx^ with the central T₂ / central S_ctx with the ceiling T₂^ | **3 033.0** / 2 907.8 |
| ceiling G₂^, bootstrap p2.5 / p50 / p97.5 | 3 548.4 / 3 758.1 / 3 957.2; share < 3 000 = 0 |

One-term break-evens for the central G₂ to reach 3 000: f ≤ 0.487 (impossible at W = 2, where f ≥ 0.5); spine
≤ 484.7 µs (the direct GuestGpu floor is 959); T₂ ≤ 861.9 (measured 1 645.4 ± 157.4); W_E ≥ 2 876 (borrowed value
1 115.6; even E_com gives only 2 743.6).

## 8. Findings

**CONFIRMED**
- C1. All 16 hashes in `SEALS119.txt` equal the files now. The `go119a.log` prefixes, the git copies in
  `docs/session-119/seal01/` and the scorer constants `g2_119.py:83-111` agree (§1).
- C2. Run provenance: both json files carry `prereg.sha256` `e22c96a7…` / 7 596 B = the sealed pred, and
  `binary_sha256` `d3a981a2…`. The environment and schedules are exactly as sealed. There is no checkpoints variable
  and no recording (§1).
- C3. Population (§2): 80 blocks and 40 pairs (20 AB + 20 BA) per run. Rejections and exclusions equal the score's.
  Every row's `arm=` matches its ABBA position, and the `GateArm` texts put the baseline in arm 0.
- C4. Every level, difference and G term reproduces to 0.1 µs (§3–§4). G₂ = 2 216.5 < 3 000, so the verdict is
  `A_CLOSED_FOR_MAX_FPS`, applied as sealed (ROADMAP 119 item 4).
- C5. Every arming check and control passes on my own computation (§5).
- C6. The disclosed smoke numbers reproduce exactly (§6).
- C7. Protocol: the rule was recorded before the smokes, and ROADMAP changed append-only. The seal and the mutants came
  before the runs, nothing else ran during them, and the design agents finished before them (§1).
- C8. The closure is statistically robust: bootstrap max 2 573 against the 3 000 bar. It also survives each single
  uncertain term taken alone: f, spine at its direct floor, T₂ − 2SE, E_com in place of W_E, and the whole cross-run
  instrument price (§7).

**MINOR**
- m1. **The decision is model-bound, not statistics-bound.** The ceiling G₂^ = 3 724 (bootstrap [3 548; 3 957]) is
  above 3 000 in every resample. The ceiling's S_ctx^ alone, with the central tax, gives 3 033. G₂ without the spine
  term is 3 485. So the closure holds because of the sealed choices: the central decides, W_E (s101) and C_TS (s96) are
  borrowed from other builds, and the spine is charged in full. ROADMAP 119 item 4 prints the ceiling and says it
  decides nothing, which is honest. Its closing paragraph ("после закрытия A … ни один маршрут с живой оценкой …") should
  still not be read as "A cannot give ≥ 3 ms under any plausible model". The sealed rule is applied correctly.
- m2. **Arm-level draw mismatch inside `mut119`.** The arm-1 `draws` level is 5 061.8 against 5 012.8 for arm 0
  (+0.98 %), while the paired d `draws` is +3.4 ± 19.0 and work is +0.068 %. The median of block means lands S_raw in a
  slightly heavier part of the scene than `cpu_net` (`sh119` arm 0, 5 013.0). This works against A by about 70–93 µs
  (paired S_raw: 2 287; per-draw rescale: 2 309). The estimator is inherited from session 104 and sealed; the effect does
  not matter for the decision.
- m3. **Stale labels in the json.** `runs119/g2_119_score.json` block `G` still names the W = 2 tax `T4`, `T4_2se`,
  `T4_dt`, `kill_T4_central_us`, and the ceiling's `T4` is T₂^. The text report says T2. ROADMAP 119 item 3 (3) promised
  fixed labels; only the text was fixed. Cosmetic.
- m4. **Expected pair count too low.** The pre-registration (and PRESEAL / ROADMAP 119 item 3) expected 36–38 pairs from
  300 s. Each run gave 40, because the hold covers frames up to about 9 570, which is 21 quartets minus quartet 0. No
  weight.
- m5. **Incomplete smoke disclosure.** `pred/01_g2_119.md` says only the draft mutants ran during the smokes. The two
  design agents of ROADMAP 119 item 1 (4), launched at 23:30, were active as well: `designs/emit_parts.md` 23:44:17 and
  `witness_binding.md` 23:44:41 were written during `smk119m` (23:42:26–23:45:49), after `smk119s`. The smokes decide
  nothing.
- m6. **"Predictions written before the smokes" cannot be verified from the files.** `g2_119.py` and `make_g2_119.py`
  were created at 23:32:31–33, before `smk119s` (23:38:45), but `make_g2_119.py` was last modified at 23:59:43. No
  pre-smoke copy survives (`work_mut119/`, `work_seal/` are empty). The only in-file evidence is that A4's band misses
  both the smoke and the sealed run. The predictions carry no decision weight.
- m7. **Wording.** ROADMAP 119 item 4 says the tax was measured "вдвое больше" than the break-even 861.9 µs. It is
  1 645.4 / 861.9 = 1.91×, so "почти вдвое" would be accurate.

**MAJOR:** none.

Note, not a finding: `sh119` was launched 51 s after the 28-worker `mutlib` tally ended at 00:29:18. procload and the
idle check passed (cpu 3 %, gpu 0 %), and the first kept block starts about 2.5 min later. The ABBA differences are
immune to this. The levels show no sign of it: arm-0 `draws` 5 013.0 against 5 012.8, render area equal to 0.002 %, and
the cross-run price 1 205 is inside A12's band.
