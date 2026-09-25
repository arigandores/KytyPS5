# Audit 117, lens RECOUNT: seal 01r2 `spn117`

Auditor: independent recount. Read-only except this folder. I did not run the game, a build or mutlib.
I wrote my own parser (`parse117.py`, which reads the log in binary into `parsed117.pkl`) and my own analysis
(`recount117.py`, output in `recount117.out.txt` and `recount117.json`), plus the cross-run context script
`xrun117.py` (output in `xrun117.out.txt`). I read the scorer `spn117.py` only after I had my own numbers, and I did
not import or run it.

## Summary

| claim (ROADMAP 117 item 14 / score file) | recount | status |
|---|---|---|
| ADMITTED, all 18 admission checks | every check re-derived (17 directly; `installed_now` from mtimes and the chain's sha check) | CONFIRMED |
| build `3cde1af8`, pin, ABBA `spine=1\|spine=2` | json sha `3cde1af8ed1a…9c64b9`, one `GpuClockPin: mode 1`, 80 `GateArm:` lines, ABBA | CONFIRMED |
| 39 + 40 complete blocks | blocks 0–78 complete (arm 0: 39, arm 1: 40); block 79 (arm 0) cut at frame 8984 | CONFIRMED |
| K5: `spine_bad` 0, `spine_misal` 0, `cram_write` 0, no `SpineMismatch:`/`SpineMisalign:` | 7 184 x lines with n > 1800, all sums 0; 0 such lines | CONFIRMED |
| compares 19 107 669 | sum over all 7 184 x lines after 1800 | CONFIRMED |
| cmp/el of arm 2 = 1.0001 | arm-1 kept frames: 16 991 362 / 16 989 459 = 1.000112 | CONFIRMED (see MINOR-1) |
| `spine_lost` 0, `spine_abort` 0, `spine_pad` 0 | 0, 0, 0 over every x line after 1800 | CONFIRMED |
| K1: 608.0 µs a frame (arm 0, frames 10–89; bar 1 200) | 607.990 µs (3 120 frames) | CONFIRMED |
| 26 192 packets, 5 309 elements a frame, `el_ops` 1.00, 8 submissions a frame | 26 192.03; 5 309.37; 0.9998 (arm 0) / 0.9999 (arm 1); `spine_n` 7.9955 | CONFIRMED |
| walker 3 207 µs vs the frame without the spine 32 917 µs (walker fit) | 3 207.150 vs 32 917.154 | CONFIRMED |
| arm 2: `dt` +1.6 ms | raw means +1 599.1 µs; ABBA quads (19) +1 639.0 ± 280.7 (2SE) | CONFIRMED |
| no IB, `COND_EXEC`, predication or 14-dword branch; 14 indirect elements a frame | `spine_ib`/`cf_br`/`cf_cond`/`cf_pred`/`cf_predw` = 0 over the whole run; `cf_ind` 13.997 / 14.000 | CONFIRMED (see MINOR-4 on wording/scope) |
| "its price on GuestGpu 0.61 ms a frame (1.8 % of the frame)", listed under **what is proven** | arithmetic right (608 / 33 525 = 1.81 %), but this is the spine's own timer, not a frame price | **NOT SUPPORTED as stated** (MAJOR-1) |
| K5 PASS, K1 PASS ⇒ PART2 under the sealed rules | reproduced | CONFIRMED |

**FATAL: none. MAJOR: 1. MINOR: 7. INFO: 5.**

## 1. Admission (independent)

- **Build.** `spn117.json` `binary_sha256` = `3cde1af8ed1af960a2216957288c6d9f54e606fd7c3e48bd97659b052a9c64b9`. The chain
  (`go117a.sh`) checked the pinned copy's sha, copied it into place and re-checked the installed sha before the run
  (both have to equal EXPECT, otherwise the chain stops). The pinned copy still hashes to `3cde1af8…` today.
  - The installed exe **now** hashes to `d3a981a2…`, with mtime 21:20:40, which is 37 s after the scorer ran (21:20:03).
    It was re-installed after scoring, so the scorer's `installed_now ok` was true at scoring time (MINOR-5).
- **Pin.** Env `KYTY_GPU_CLOCK_PIN=1`, and exactly one `GpuClockPin: mode 1` line (log line 16 564).
- **Env.** The `KYTY_*` set equals the expected 10 keys exactly: `FRAME_TRACE=lite`, `GPU_HANG_ABORT_S=8`, `GATE_FILE`,
  `SAMPLE_GATE`, `QUEUE_TRACE=1`, `GUEST_ARGS`, `GPU_CLOCK_PIN=1`, `GPU_MARKERS=0`, `GATE_SCHEDULE=90+1800:spine=1|spine=2`
  and `GATE_SCHEDULE_ABBA=1`. The only `VK_*` key is `VK_SDK_PATH`, and there are no other keys.
  - `KYTY_GPU_MARKERS=0` really is off: `gpuCheckpoints.cpp:59-62` treats `'0'` as off, and there is no
    `Vulkan: GPU markers` line in the log.
- **Hold and attempts.** `hold_s` = 300. There was one attempt: `ok`, `hold_exit` null, `hold_s` 300.1. The sum of
  `dt_us` from the stable frame 280 to 8984 is 300.31 s, which agrees with the hold.
- **Prereg.** `prereg.path` = `C:\kyty\s117\pred\01_spn117.md`. The recorded sha `ca866441…` equals the file's sha now
  and seal 01r2. The pred mtime is 21:07:39, before the chain started (requested 21:12:44).
- **Gates.** The whitespace-normalised json gate text equals `gates_base.txt` and `gates.req` exactly, has no `spine=`
  token, and hashes to `91da50f6…` (the scorer's `GATES_SHA`).
- **Gate lines.** There are 41 `Gate:` lines, all `spine`. Each one sits exactly at an arm change (blocks 0, 1, 3, 5, …,
  79), carries the value of its block's arm, and no other gate or knob moved.
  - The scorer only checks that the lines present are consistent. I also checked the other direction: every expected
    change has its line.
- **GateArm lines.** There are 80 lines, all well-formed: `arms=2 period=90 abba=1`, block `b` at frame 1800 + 90·b
  for b = 0..79, consecutive, arm order A B B A, and the texts are exactly `spine=1` / `spine=2`.
  - The main-line `arm=`/`blk=` fields agree with `(n−1801)//90` and ABBA on all 7 184 frames after 1800.
  - Every frame at or before 1800 carries `arm=0 blk=0`, and every spine field before 1801 reads 0, so the knob was
    off until the schedule started.
- **Spine line.** There is exactly one `Spine: mode=` line: `Spine: mode=1 snap=4096 ctx=2672 ucfg=148 sh=1208`, at
  log line 447 310, right after the block-0 `GateArm:` at 447 255.
- **Failure markers.** I searched the log and stdout for the pred list plus `Fatal`, `FATAL`, `--- Fatal Error ---`,
  `DeviceLost` and `device lost`: 0 hits.
  - A broad case-insensitive scan (error, exception, hang, lost, …) found only file names (e.g. `…hangingplant…`,
    `…crashsite…`), two known alignment warnings, and 16 `Exception: code=0xe06d7363` lines in stdout. 0xE06D7363 is a
    handled C++ exception, and the same 16 lines appear in every Sky Garden stdout of s114–s116 (INFO).
- **Streams.** `FrameTrace`, `FrameTrace-draw` and `FrameTrace-x` each have 8 983 lines (n = 2..8984), with no
  duplicates, no gaps and no out-of-order lines. Every x line after 1800 carries all 18 spine fields.
- **Armed.** Every block of arm 0 had `spine_n` > 0 (at least 636 plans per block's kept frames), and no kept frame had
  `spine_n` = 0.
  - Arm-0 compares: 17 in all kept frames, all in one frame (8730), against 16.56 M elements.
  - Per block, arm 1 has cmp/el between 0.9966 and 1.0029, and el/ops between 0.9971 and 1.0034.
- **el_ops.** Arm-1 kept frames: 0.99989, inside [0.95, 1.05].
- **Idle.** `pre_run.gpu_util_median` = 0.0. The chain's idle check printed `cpu=5 gpu=0`.
- **Hash chain.** The chain's `files:` line at 21:14:10 matches seal 01r2 on all 16-hex prefixes:
  - `spn117.py` `ab5d5996846faf06`
  - `test_spn117.py` `35157c06d23d7541`
  - `mut_spn117.py` `6b551bd1e17d3ee2`
  - `gates_base.txt` `303a784911cf0ffe`
  - `enter_scene.py` `46a770ae6f2c9458`
  - `procload.py` `d9e7a777404f1aa9`
  - `pred/01_spn117.md` `ca8664412ff09f31`

  All 12 sealed files hash to the seal-01r2 values today. The mutant tally file `mut_spn117.out.txt` hashes to
  `bd7e42b6…` as recorded, ends "ALL KILLED (104 of 104 …)", and was written at 21:12:34, before `SEALS117.txt`
  (21:12:43) and the chain request (21:12:44). The committed copies in `6f26e6c` (`go117a.log`, `spn117.score.json`,
  `spn117.score.txt`) are byte-identical to the local ones.

## 2. K5 and K1 (independent numbers)

**Sums over every `FrameTrace-x` line with n > 1800** (7 184 lines, which equals the 7 184 frames that have all three
lines):

| field | sum |
|---|---|
| `spine_n` | 57 472 |
| `spine_pk` | 188 188 205 |
| `spine_el` | 38 145 991 |
| `spine_cmp` | 19 107 669 |
| `spine_cf_ind` | 100 576 |
| `spine_bad`, `spine_misal`, `spine_pad`, `spine_lost`, `spine_abort`, `cram_write`, `spine_ib`, `spine_cf_br`, `spine_cf_cond`, `spine_cf_pred`, `spine_cf_predw` | **0** each |

There are 0 `SpineMismatch:` lines and 0 `SpineMisalign:` lines. K5 **PASS**.

**Coverage is essentially per-element, not just ≥ 90 %.**

- All compares in the run: 19 107 669.
- All elements planned in the 3 600 frames of the 40 arm-1 blocks: 19 107 652.
- The difference is 17. Compares of elements planned at the end of a B block land in frame 0 of the next A block
  (15 651 compares in arm-0 frames, 697 in block 79). Summed across those edges the count closes to within 17.

**Per-arm means over the kept frames** (10–89 of each complete block) match the score file to every printed digit:

| field | arm 0 (`spine=1`) | arm 1 (`spine=2`) |
|---|---|---|
| `dt_us` | 33 525.14 | 35 124.28 |
| `cpu_gpu_us` | 32 211.88 | 33 711.29 |
| `draws` | 5 042.29 | 5 041.79 |
| `dispatches` | 267.96 | 268.00 |
| `da_walk_us` | 2 599.16 | 2 665.69 |
| `spine_n` | 7.9955 | 7.9997 |
| `spine_us` | 607.99 | 795.21 |
| `spine_pk` | 26 192.03 | 26 192.65 |
| `spine_el` | 5 309.37 | 5 309.21 |
| `spine_cmp` | 0.0054 | 5 309.80 |
| `spine_chk_us` | 0.0016 | 897.85 |
| `spine_cf_ind` | 13.997 | 14.000 |
| el/ops | 0.99983 | 0.99989 |
| packets per plan | 3 275.84 | 3 274.21 |

K1: 607.990 µs ≤ 1 200 ⇒ **PASS**. The walker figures (3 207.150 vs 32 917.154) are reproduced.

**Distribution of `spine_ns`/1000 in arm-0 kept frames** (is the mean dominated by a few frames? No):

| statistic | value |
|---|---|
| mean | 608.0 µs |
| median | 555.3 µs |
| p10 | 507.1 µs |
| p90 | 786.8 µs |
| p99 | 942.1 µs |
| max | 1 155.4 µs (frame 5827, 11 plans) |
| min | 366.0 µs |
| SD | 125.0 µs |
| share of the sum carried by the top 1 % of frames | 1.63 % |
| per-block means | 568.6–651.8 µs (median 607.2) |
| ns per element | median 104.2, p99 179.0 |

- No single kept frame exceeded the 1 200-µs bar.
- The right skew follows `spine_n`: the top frames had 8–12 plans. The mean sits 53 µs above the median.
- Arm 1: `spine_us` median 753.6 / p99 1 296.6; `spine_chk_us` median 852.5 / p99 1 510.9.

**`dt` shape.**

| | median | p99 | frames ≥ 41.7 ms |
|---|---|---|---|
| arm 0 | 33 346 | 49 878 | 4.13 % |
| arm 1 | 33 415 | 50 078 | 11.41 % |

The +1.6 ms of arm 1 is mostly more frames that take 3 vblanks, as expected with vblank quantisation.

**BDA regime:** NEW in both arms (`bda_scan` median 51 in arm 0 and 50 in arm 1; means 57.7 / 56.7).

## 3. Findings

### MAJOR-1: "its price on GuestGpu 0.61 ms a frame (1.8 % of the frame)" is the spine's own timer, and this run shows the timers under-count

The run cannot establish the frame price it states under "what is proven".

- K1, as sealed, is the mean of `spine_ns`, a self-timer around `SpinePlan` (`graphicsRun.cpp:1240` → `:1466`). K1 PASS
  under that rule is CONFIRMED.
- But there is no `spine=0` arm, so the run does not measure what the spine costs the frame.
- The one admissible control inside this run, arm 2 against arm 1 (ABBA quads, n = 19, 2SE), shows the self-timers
  missing about a third of the marginal cost:
  - Δ`dt` = **+1 639.0 ± 280.7 µs**
  - Δ`cpu_gpu_us` = **+1 532.6 ± 199.1 µs**
  - Δ(`spine_ns` + `spine_chk_ns`) = **+1 087.0 ± 26.6 µs**
  - Residual Δ`dt` − Δself = **+552 ± 266 µs**; Δ`cpu_gpu` − Δself = **+446 ± 185 µs**. Both are above 0 at 2SE.
  - Δ`spine_ns` alone = +188.1 ± 12.3 µs, even though `spine_ns` subtracts the snapshot time. The plan loop itself runs
    slower once snapshots are on, which is an indirect (cache) cost the timer only partly sees.
- **Cross-run context (not a measurement under program rules, and confounded):** pinned Sky Garden runs without the
  spine, on code whose `src` differs from `3cde1af8` only by the spine commits `e8404d9..36c8350`, compared with arm 0:

  | run | `dt` | `cpu_gpu` | frames < 25 ms |
  |---|---|---|---|
  | `obs116` | 31 143 | 30 487 | 13.6 % |
  | `ttl114b` | 31 280 / 31 237 | 30 430 / 30 398 | 14.0 % |
  | `ctl114b` | 31 166 | 30 487 | — |
  | `spn117` arm 0 | **33 525** | **32 212** | 3.0 % |

  - That is +2.2 to +2.4 ms of `dt` and +1.7 to +1.8 ms of `cpu_gpu`.
  - The confounds: `gpu_busy_us` (14.39 vs 12.84–12.89 ms) and `cpu_main_us` (+0.8 ms) are also higher, the CPU
    clock was not recorded (`cpuclk.py` missing), and `vid115` (with recording) sat at 33 801. So this cannot price the
    spine. It is a flag that 0.61 ms may be well below the real cost of `spine=1`.
- **Effect:** the verdict and the consequence under the sealed rules stand. The sentence belongs under "not proven".
  Suggested wording: "self-timed plan cost 0.61 ms a frame; frame price not measured (no `spine=0` arm); in-run the
  timers miss ≈ 0.55 ms of the mode-2 increment".
  - If the frame price matters to PART2's placement (GuestGpu vs walker), it needs a `spine=0|spine=1` ABBA.
  - Walker fit survives even a 3× price: 2 599 + 1 824 ≈ 4.4 ms ≪ 31.7 ms.

### MINOR-1: the compare count and its ratio use different denominators

- Item 14 writes "сверок 19 107 669 (доля к элементам плеча 2 — 1,0001)". The 19 107 669 is the whole run's total
  after 1800. The 1.0001 is the arm-1 kept-frame ratio: 16 991 362 / 16 989 459.
- 19 107 669 / 16 989 459 would be 1.125.
- The more telling statement is 19 107 669 compares against 19 107 652 elements planned in all frames of the 40 arm-2
  blocks: a difference of 17, a ratio of 1.0000009.

### MINOR-2: the kept window 10..89 includes the last frame of a block, which can carry the next arm

- Frame 8730 is index 89 of block 76 (arm 0); the arm-1 block 77 starts at `GateArm frame=8730`. It holds 17 compares
  and 4.87 µs of check time, all the "compares" of arm 0.
- Arm-1 index 0 shows −14 094 cmp−el across blocks. That frame is not kept.
- The effect on K1 or K5 is negligible, but an estimator window of 10..88 would be clean.

### MINOR-3: the BDA regime is not stated

- Item 14 quotes `dt` levels (32 917 µs, +1.6 ms) without the regime, although the program's rule since session 112 is
  to state it with every level.
- The regime was NEW in both arms (`bda_scan` median 51 / 50).

### MINOR-4: wording and scope of the control-flow claim

- "spine_cf_* 0" is literally false, because `spine_cf_ind` = 14 a frame. The intended reading is "cf_br, cf_cond,
  cf_pred and cf_predw are 0".
- "In Sky Garden" generalises from one static viewpoint of one entry (no input, 300 s). The pred's own Limits say the
  same.

### MINOR-5: the sealed scorer cannot be re-run to reproduce ADMITTED today

- The installed exe was switched back to `d3a981a2` at 21:20:40, after scoring.
- `spn117.py`'s `installed_now` now yields False, so a re-run prints NOT_ADMITTED unless `3cde1af8` is re-installed.
- This is not a defect of the run.

### MINOR-6: the chain's run-time hash log covers 7 of the 12 sealed files

- `go117a.sh`, `launch_run.py`, `run_safety99.py` and `mutlib.py` are not in the `files:` line. The exe is covered by
  the chain's EXPECT check.
- All four hash to seal 01r2 now and have mtimes before the chain request (19:37–21:07), so there is no sign of
  change. Run-time proof exists only for the seven logged files.

### MINOR-7: the sealed scorer's docstring still begins "DRAFT, NOT SEALED"

This is cosmetic.

### INFO

- **INFO-1:** `spn117.json` has `started` = `finished` = 21:19:58, while `launched` = 21:14:36. This looks like a
  harness field-naming quirk. The chain log confirms 21:14:33 start and 21:19:58 end.
- **INFO-2:** there are 16 `Exception: code=0xe06d7363` lines in stdout. These are handled C++ exceptions, and every
  Sky Garden stdout since s114 has the same 16. They are not a failure marker.
- **INFO-3:** `cpuclk_requested` is true, but `cpuclk.py` is absent, so the run has no CPU clock record. GPU clocks were
  normal: SM median 2 497 MHz, reason mask 0x400 throughout, the same mask as `ttl114b`/`obs116`, max 73 °C.
- **INFO-4:** per-frame cmp and el differ by up to ±7 000 per in-block index. el is counted at plan time (start of the
  submission) and cmp at execution, so single-frame ratios mean nothing. Only the sums are meaningful, and the sums
  close.
- **INFO-5:** the recount cannot tell whether the comparator can fire (a vacuous `==` would also read 0). The only
  evidence that it can fire is the pre-seal smoke runs on earlier builds (items 8–10), which were unsealed. That
  question belongs to the code lens.

## Files

- `C:/kyty/s117/audit117/recount/parse117.py`: own parser, writing `parsed117.pkl`.
- `C:/kyty/s117/audit117/recount/recount117.py`: own recount; output in `recount117.out.txt` and `recount117.json`.
- `C:/kyty/s117/audit117/recount/xrun117.py` and `xrun117.out.txt`: cross-run context (not a verdict).
- `C:/kyty/s117/audit117/recount/roadmap117_excerpt.txt`: the ROADMAP section that was audited.
