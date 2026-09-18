# Session 91 — FACTS

**The single source of truth for this session's numbers.** `README.md` is the harness and the
traps, `PLAN.md` §0 is the reading that fixed the plan, `pred/01_shift.md`, `pred/02_pin.md` and
`pred/03_repair.md` are sealed and were not edited. `read91/report_*.md` are the five readers'
reports; `review91/review_*.md` the three adversarial reviews.

Every number is a **ratio of sums over its window**, a paired mean over the programme's cycles
(`summary4.build_cycles`, warm-up 3, min block 5), or an exact zero where the counter is never
`Add`ed. Labels: **[M]** measured in this session; **[I]** inference, model-dependent or
between-run; **[K]** known before the sealing that scores it (not a blind test).

---

## 0. In one sentence

**The game's dynamic resolution reads GPU timestamps, and on this emulator a GPU timestamp is the
pacer-scaled CPU clock written by the GuestGpu thread at PM4 parse — so a CPU-side knob moves the
DRS rung; that is why two knobs were unmeasurable, and a one-site, per-process pin of that clock
(`KYTY_GPU_CLOCK_PIN`) removes it: pinned, the two contrasts that failed admission in sessions 88
and 90 (`dap88a` split +12.93 %, pairs 33 %; `bim90a` −21.88 %, 42.9 %) pass it at +0.001 % /
110/110 and +0.002 % / 123/123, and the positive control drives the rung the other way — to native
4K in 100 % of flips. By the rule sealed before the runs, THE PIN IS ADOPTED.** It then settled
two debts: **`dapin=3` costs GPU time with the record path off, +0.817 % ± 0.146 % (2SE), t +11.2**
— the record thread is not the carrier — and saves **8.67 %** of GuestGpu CPU per draw; and **D1
(`bufimp`) is a frame-time regression over the whole run at a fixed rung, `dt` +11.48 %, t +84.7**,
carried by forced host-read drains (GuestGpu 3.8 ms a flip) and by guest threads stalled 10.9 ms a
flip waiting for GuestGpu to run them. The fallback estimator (TB), sealed and validated on 20
archived runs before the game was opened, had read both from disk first; its CPU bracket for
`dap88a` missed the pinned value by 0.22 pp and its CPU bracket for `bim90a` missed it by 0.27 pp,
the latter for the in-run price defect named below.

### 0.1 Defects of my own text, listed first

1. **`pred/01` §5 anchored its host-read rule on the whole-arm `dt` contrast of the INVALID
   `bim90a`** (+4 110.8 µs, FACTS s90 §3) — exactly the leak session 90's trap forbids — and its H5
   is itself a between-arm contrast of that run. Re-anchored here on TB's admitted T `dt`
   (+13.493 % of 31 017 µs ≈ 4 185 µs, half 2 093): **the verdict does not change** (4 820 µs). And
   **H1 and H5 read the same nanoseconds** (`masterSemaphore.cpp:138-143` adds one wait to both
   `SemWaitGpuNs` and the `host-read` site): counted once below.
2. **`pred/01` §5 asked for `gpu_blocked`, `gpu_idle`, `gpu_proc`** — main-line fields that read 0
   in every lite run (`TimingsEnabled`), the same vacuity `PLAN` §0 B item 2 found in
   `hostread_wait_us`. Printed; 0.000 in both arms.
3. **`pred/01` §7 "the largest chance dh in an A/A is 6.7 pp" is false under the tool's own
   definition**: `aa67b` reads **+8.80 pp** draw-weighted. Still far below +28.4 / −53.6.
4. **`pred/02` R4 was a defective band, found BEFORE any pinned run** by running the sealed readout
   on the record: fragments (1-vblank half-frames) are never in [1990, 2030), and modern runs carry
   2–14 % of them, so eight unpinned LOW runs read 83.7–98.9 %. Repaired under `pred/03` (R4'), and
   R4 is still printed.
5. **`PLAN` §0 A said "real Vulkan GPU time never reaches the guest" — overstated.** EOP interrupts
   and flip completions arrive at REAL GPU completion (`commandScheduler.cpp:569-586`), stamped with
   the pacer-scaled clock; only the timestamp VALUES are parse-time. The pin does not cover those
   channels — **and the pinned runs show they do not drive the rung** (§8.1).
6. **`PLAN` §0 A's "the guest then sees the wall span ≈ 31 ms" is a prediction**, not a reading:
   what holds by construction is that the pinned G is today's G divided by the speed (≈ ×2).
7. **W's pair set is the refused matched subset of `bim90a`, to the digit**: the full run's 51
   matched pairs all start at n ≥ 6 181 and read −0.989 % ± 0.207 %, t −9.57 — as W does. W is
   justified ONLY by the scene-locked latch (last HIGH flip 6 146; 18 runs of the record drop at
   6 144–6 147), a window fixed by flip number from rung labels before any outcome was read; on it
   W1 could fail only on work.
8. **T3 MISSED, and the reason is the bracket's premise, not the direct effect.** `bim90a`'s in-run
   CPU price is +1.159 % ± 0.387 %, ≈ 4.3 SE from the A/A pool (+0.048 ± 0.337): its HIGH flips sit
   early in arm-1 blocks (mean position 8.5 against 14.0) — arm-switch carryover, not a rung price.
   The run's own windows imply ≈ +0.28 % (early n < 6 150: T −1.170 % at dh −91.1 pp; late: −0.917 %
   at dh 0). **CPU D on a rung-shifted run is therefore [I]**, like GPU D, and "UNDETERMINED" is not
   evidence of a null.
9. **The scoreboard below is inflated in substance**: T1, T2, T4, T6, T7 bracketed magnitudes that
   were on disk or published before sealing [K].
10. **`pred/03` R4'a — the repair of item 4 — missed in `pin91c`'s census arm (94.42 % against
    ≥ 96 %)**, because its fragment rule (`rt_att` < 25 % of p50, borrowed from `rcv81`) does not
    catch one-vblank fragments carrying 25–35 % of the attachments. Not the pin: R4'b and R4'c HIT
    (§9.1). **The repair file repeated the class of defect it was written to repair.**

---

## 1. What was done, and what was NOT

| step | state |
|---|---|
| harness `C:/kyty/s91`, ported by `C:/kyty/s90/s91_port.py` (written fresh in the SOURCE dir) | **clean**; `gates_base.txt` 1092 B, 99 names, sha256 `00c116dc…0594d8`, unchanged; `gen_gates.py --check` only |
| the reading (`PLAN.md` §0), five readers | done — mechanism, prior art, empirics, anchors, plumbing |
| `pred/01_shift.md` sealed **before `shift91.py` ran on any log** | 10 161 B, sha256 `82877f4a23e1f15a…`, mtime − ctime +0.003 s |
| TB validation (V1–V4) and targets (§5, §6, W) | done, §3–§5 |
| `patch_s91.py` + `patch_s91b.py` (the pin, its positive control, the counters) | built: **`887ede9f8323297f…`, 23 623 680 B**; installed into the game folder by `enter_scene` at `pin91a` and not rebuilt since (guards check 10 PASS on all three runs) |
| `pred/02_pin.md` (three pinned runs) and `pred/03_repair.md` (R4') | sealed: 8 360 B `ebf4b9f041c9a308…` +0.000 s; 2 747 B `7c9fae4cc4bc58b4…` +0.000 s — both BEFORE the game was opened |
| **the pinned runs `pin91a/b/c`** | **run after the user allowed it**, all on `887ede9f…` (installed by `enter_scene`), `pred/02` hash in each `<tag>.json`; `pin91a`'s warm-up hit the known first-entry hang (`GpuHangAbort role=4`, absorbed by `--warmup-first`), every counted attempt reached the scene in 14.8–26.8 s; `guards.py` 1/2/3/4/7/10 PASS in all three, check 6 FAIL (not a criterion), 3b/5 WARN |
| tests | `memory_tracker_tests` all cases passed; `resource_materialization_tests` all cases passed; `resource_tracking_tests` output **byte-identical to session 90's** (the known "SRT runtime" failure, then the process ends the same way) |

---

## 2. The reading, in five lines (details `PLAN.md` §0 A)

1. **Mechanism [read in source].** `RELEASE_MEM data_sel=3` → `Sync::ReadReferenceClock()` →
   `KernelReadTsc()` = freeze-excluded TSC × pacer speed, memcpy'd into guest memory at PM4 parse
   (`graphicsRun.cpp:2562-2564`, `sync.cpp:45-54`, `pthread.cpp:187-216`, `videoOut.cpp:1187-1206`).
2. **The rung follows the scaled clock, not real GPU time [M, record]**: 65 DRS-active runs — before
   an UP transition S = speed × dt is lower in 59/65 (t −9.69), `gpu_busy_us` t −1.46.
3. **CPU pays nothing for the high rung within a block, GPU pays ≈ 11–13 % [M, old binaries]**:
   cpu/draw +0.048 % ± 0.337 %, gpu/draw +11.23 % ± 0.47 % (296 cells, four rung-varying A/As).
4. **The A/A slope of cpu on area is reverse causation [M]**: switches to LOW follow expensive frames;
   with d_k3 and fragment share in the regression the rung term is ≈ 0.
5. **Prior art [read]:** every admission rule on disk voids all six rung-varying A/As; RCV (s81) was
   refuted by its own rule; within-rung OLS was wrong 17–22×; no configuration without DRS was ever
   tried. **The pin is the first.**

---

## 3. TB, validated on 20 archived runs [M; not blind, K]

`shift91.py --validate` (`_validate91b.txt`, identical to `_validate91.txt` after the review's
latent fixes):

| set | result |
|---|---|
| **V1** 12 A/A runs, T `cpu_net/draw` \|t\| < 3 | **PASS** — largest \|t\| 2.58 (`aa74a`, contaminated in its own session) |
| **V2** D interval contains 0 in ≥ 10 of 12 | **PASS at the edge, 10/12** (`aa74a` t +2.58, `vfy80a` t −2.06 on 30 cycles); for the six single-rung A/As it is V1 restated at 2 SE |
| **V3** 8 valid runs: \|dh\| ≤ 0.5 pp, sign, \|t\| ≥ 3, within max(0.15 pp, 1 SE) of F2 | **PASS 8/8** — e.g. `pgl90a` +1.596 % (F2 +1.586), `tfs85a` −4.531 % (−4.591) |
| **V4** in-run price, 4 mixed A/As | **PASS** — cpu +0.801 / −0.148 / −0.002 / +0.439 %; gpu +13.20 / +8.52 / +9.04 / +14.22 % |

---

## 4. D1 (`bufimp`) — CLOSED as a frame-time regression

### 4.1 The host-read census of `bim90a` (`pred/01` §5) [M, within-arm]

| per flip, n ≥ 2100 | census arm (`bufimp=1`) | import arm (`bufimp=2`) |
|---|---:|---:|
| `FrameTrace-wait` host-read µs | **1.55** | **4 609.58** |
| host-read wait events | 0.001 | 8.365 |
| `FrameTrace-submit` host-read µs | 0.00 | 210.64 |
| host-read submit events | 0.000 | 7.418 |
| `hostread_waits` (hazard hits) | 0.009 | 19.468 |
| `semwait_gpu_us` | 2.09 | 4 609.05 (the same ns as the wait row) |
| `submits` | 38.55 | 46.32 |

**Rule (re-anchored, §0.1 item 1): (wait + submit) host-read = 4 820 µs a flip ≥ 2 093 ⇒ the
forced host-read drain carries the lost frame time.** GuestGpu blocks in `m_master.Wait` after a
submit forced mid-recording (`CommandScheduler::Wait`, tick == CurrentTick), 8.4 times a flip, ≈
550 µs each. It is BLOCKED time, so it is invisible to `cpu_gpu_us` (thread CPU time) — which is
why the frame got longer while every counted thread did less. **And it is why the import arm drops
to the LOW rung: the blocked span lengthens the GuestGpu wall span inside the frame, i.e. G.**

### 4.2 TB on `bim90a` [M; CPU D and GPU D are I]

| | reading |
|---|---|
| dh | **−53.61 pp**, SE 4.13 |
| T `cpu_net/draw` | **−1.071 %**, SE 0.069, t −15.44 |
| T `dt` | **+13.493 %**, SE 0.152, t +88.51 |
| T `gpu/draw` | −8.539 %, SE 0.486 (mostly the rung) |
| p (in-run, C = 26) | cpu +1.159 % ± 0.387; gpu +13.37 % ± 1.45 |
| D `cpu_net/draw` | [−0.859, +0.024] % — UNDETERMINED **[I]** (§0.1 item 8) |
| D `gpu/draw` | [−4.106, +1.608] % — UNDETERMINED [I] |

### 4.3 W — the latch window, n ≥ 6150 [M, with §0.1 item 7]

`area_verdict.py bim90a --first-frame 6150`: HIGH 0.0 %, split **−0.001 %**, match **51/51**, work
**−0.075 %** ⇒ **VALID**. Matched: `cpu_net/draw` **−0.974 %** (t −9.47), `dt` **+13.382 %**
(t +52.68), `gpu/draw` −2.149 % (t −18.63). On summary4's cycles over the same window
(`review91/wcheck.py`): −0.917 % and +13.775 %.

**Verdict by the rule sealed in `pred/01` §6: W1 and W3 hold ⇒ D1 is CLOSED as a regression at the
LOW rung for late-scene content.** The frame-time loss does not depend on the rung: early (dh −91
pp) +13.35 %, late (dh 0) +13.4–13.8 %. **`bufimp` stays 0, and there is nothing to tune: the import
makes the GPU read guest pages AFTER the CPU may write them, so a write must wait for the read, and
in this scene the CPU rewrites these pages 19.5 times a flip.**

---

## 5. `dapin` with the record path off (`dap88a`) — TB [M; D is I]

| | reading |
|---|---|
| dh | **+28.38 pp**, SE 3.14 |
| T `cpu_net/draw` | **−9.193 %**, SE 0.069, t **−132.9** |
| T `dt` | −7.542 %, t −69.7 |
| T `gpu/draw` | +4.375 %, SE 0.335, t +13.05 |
| p (in-run, C = 76) | cpu **−0.173 % ± 0.329**; gpu **+10.71 % ± 0.43** |
| D `cpu_net/draw` | **[−9.386, −8.881] %** — negative [I] (the premise holds here: p_cpu ≈ 0) |
| D `gpu/draw` | **[−0.156, +2.774] %** — UNDETERMINED [I] |

**`dapin=3` makes GuestGpu ~9 % cheaper per draw when every draw takes the direct path** (with the
record thread on, the record says −738 µs ≈ −2.3 %). **Its GPU cost — the tenth-session debt — is
not settled by TB**: the rung carries +2.3…+3.9 % of T `gpu/draw`, and the remainder straddles 0.
`pred/02` run A reads it with the rung held.

---

## 6. Corrections to this programme's record

1. **`summary4.py`'s `cpu_net_us` is `cpu_gpu_us` in every lite run** — it parses only `FrameTrace:`
   and says so itself in a NOTE. FACTS s90 §4.1's "+1.5760 %, t +14.38" is `cpu_gpu_us`; true
   `cpu_net_us` **+1.5851 %, t +14.46** [M]. `ROADMAP` §4 and s90 `pred/01` named the wrong tool.
2. **`hostread_wait_us` is structurally 0 in lite** (`Scope` stamps under `TimingsEnabled` only);
   s90's "the waits are under ~50 ns each" is withdrawn and **s90 E3 was VACUOUS**. The waits are
   ≈ 550 µs each (§4.1).
3. **The host-read `SiteScope` FACTS s90 §8 proposed has existed since before session 90**
   (`bufferCache.cpp:1610`) — the number that answered "where did 4.1 ms go" was on disk. **Eighth
   session in eight.**
4. **`accept90.sh` inside s91 pointed at s90** (the port rewrites only `.py`); `accept91.sh` is new.
5. **Session 81's "pacer→DRS refuted" (`pac81a/b`) does not follow**: 0 HIGH in 2/2 pacer-off runs
   is what the pacer model predicts (null probability ≈ 0.30).
6. **`ob_stream_us` is also 0 in lite** (same `TimingsEnabled` gate) — the `ObtainBuffer` stream
   ring, 19.66 MB a flip in 13 380 copies in `pgl90a`, has never been timed in a measurement run.
7. `daepceil`'s comment still says "(default 1)" and it is 0 — carried.

---

## 7. What was built (no default moved)

* **`KYTY_GPU_CLOCK_PIN`** (environment, read once per process; `sync.cpp`): 1 = the guest GPU clock
  drops the pacer speed (`KernelReadTscBase`, freezes still excluded, rdtsc inside the lock); 2 =
  POSITIVE CONTROL, the scaled clock at half rate. One `GpuClockPin: mode N` line. Counters:
  `gclk_n` (every read), `gclk_pin` (pinned reads — never Added without the pin), **`gclk_adv` /
  `gclk_sadv` — arming by VALUE** (the guest clock's advance over the scaled clock's; 1/speed at 1,
  0.5 at 2), `gclk_back` (backward steps).
* **The upload memcpy split, live in every run**: `CopyGuestToStaging` returns whether it pooled;
  `stg_pool_n/_b/_ns`, `stg_in_n/_b/_ns`, `stg_inbig_n`, `stg_in_gpu_b`, `up_tmp_n/_b`,
  `stg_img_pool_b`, `stg_img_in_b`; census `bi_b_small`, `bi_reg_small`. Bytes raw, times raw ns.
* **Host-read waits timed in lite**: `hr_free`, `hr_gpuw(_us)`, `hr_forced(_us)`, `hr_sync(_us)`,
  `hr_call_us`.
* Tools: `shift91.py` (TB/W/census), `pin91.py` (scores `pred/02`+`pred/03`), `accept91.sh`.

---

## 8. The pinned runs [M]

### 8.1 The pin holds the rung — and the positive control moves it

| | `dap88a` unpinned (s88) | **`pin91a`, mode 1** | **`pin91b`, mode 2** | `bim90a` unpinned (s90) | **`pin91c`, mode 1** |
|---|---|---|---|---|---|
| contrast | `dapin=0\|3`, record off | same | same | `bufimp=1\|2` | same (no `proglap`) |
| HIGH share arm0 / arm1 | 45.4 / 73.7 % | **0.00 / 0.00 %** | **100.00 / 100.00 %** | 56.9 / 3.3 % | **0.00 / 0.00 %** |
| area per attachment | two rungs | 2 007.8 / 2 007.8 | **8 025.7 / 8 025.9 = 3840×2160** | two rungs | 2 007.8 / 2 007.8 |
| area split | +12.93 % | **+0.001 %** | +0.002 % | −21.877 % | **+0.002 %** |
| pair match | 33.0 % | **110/110** | 108/108 | 42.9 % | **123/123** |
| work | — | +0.003 % | +0.246 % | −0.156 % | +0.119 % |
| `area_verdict` | INVALID | **VALID** | VALID | INVALID | **VALID** |
| `gclk_adv / gclk_sadv` (by value) | — | 2.181 / 2.097 = 1/speed | **0.500 / 0.500** | — | 1.878 / 1.999 |
| `gclk_n` a flip | — | 299.1 | 299.0 | — | 299.0 |
| `gclk_back` | — | 0 | 0 | — | 0 |

**Rule `pred/02` §4: A-R1 holds and B-Q2 holds ⇒ THE PIN IS ADOPTED as this programme's instrument
for rung-moving knobs.** The budget model survived both directions: doubling the guest GPU spans
held the lowest step, halving them sent the game to the top of its ladder — **which is native 4K,
not the 2432×1368 the record called "HIGH"** (GPU 19 976 µs a flip there against 12 137 at LOW).
Comparisons with the unpinned runs are between-run [I]; the within-run facts are the pinned runs'
own admissions.

### 8.2 `dapin`'s GPU cost — the ELEVENTH-session debt, settled for the record-off configuration

`pin91a`, 115 cycles, dh 0.000 pp:

| endpoint | T | t |
|---|---:|---:|
| **`gpu/draw`** | **+0.817 %**, SE 0.073 | **+11.20** |
| `cpu_net/draw` | −8.666 %, SE 0.120 | −72.19 |
| `dt` | −6.754 %, SE 0.154 | −43.99 |
| `cpu_net_us` (`endpoint84`, 111 pairs) | **−3 119.7 µs** ± 128.7 | −48.46 |
| work | +0.069 % | +0.87 |

**Rule `pred/02` E3: t ≥ +3 ⇒ "dapin=3 costs GPU time with the record thread off — the record
thread is not the carrier".** The size, +0.82 %, is under half the +1.96 % that `dap85a` read with
the record path on — [I], a different configuration and binary. At the top rung (`pin91b`, no
verdict by `pred/02` §4) the same contrast reads `gpu/draw` −0.102 %, t −1.30, and `cpu_net/draw`
−10.95 %.

**TB's first out-of-sample test (E2):** pinned −8.666 % against TB's `dap88a` D bracket
[−9.386, −8.881] % — **outside by 0.215 pp, inside the ±1 pp the band allowed for between-run
drift.** TB's GPU bracket [−0.156, +2.774] contains the pinned +0.817.

### 8.3 D1 over the whole run at a fixed rung (`pin91c`, 128 cycles)

| | T | t |
|---|---:|---:|
| **`dt`** | **+11.479 %**, SE 0.136 | **+84.68** |
| `cpu_net/draw` | −1.129 %, SE 0.055 | −20.68 |
| `gpu/draw` | −2.276 %, SE 0.077 | −29.50 |
| `cpu_net_us` (`endpoint84`, 123 pairs) | −289.9 µs ± 77.7 | −7.46 |

**The host-read hazard, import arm, per flip** (`hr_*`, lite-live for the first time):

| counter | per flip |
|---|---:|
| `hostread_waits` (hazard hits) | 18.312 |
| `hr_free` — tick already free after refresh | 10.927 |
| `hr_gpuw` / `hr_gpuw_us` — waits on a submitted buffer | 0.604 / 264.8 µs |
| **`hr_forced` / `hr_forced_us` — forced submit of the RECORDING buffer + drain** | **6.782 / 3 831.3 µs** (565 µs each) |
| **`hr_sync` / `hr_sync_us` — calls from guest threads, whole stall in `SendCommandSync`** | **16.257 / 10 880.6 µs** |
| `hr_call_us` | 13 136.3 µs |
| `FrameTrace-wait` / `-submit` host-read | 3 899.4 / 184.2 µs |

J1 (free + gpuw + forced = hazard hits) 1.00000, J2 (forced = submit-site events) 0.99984, J3
1.050, J4 (off-GuestGpu share) **0.888** — all HIT. **88.8 % of the hazards fire on guest threads
(write faults), and those threads wait 10.9 ms a flip for GuestGpu to reach a `ProcessCommands`
point and run the drain.** TB's CPU bracket for `bim90a`, [−0.859, +0.024], misses the pinned
−1.129 % by 0.27 pp — the in-run price defect of §0.1 item 8 (the A/A-reference bracket
[−1.388, −0.695] contains it). **D1 stays CLOSED; the whole run agrees with W.**

### 8.4 The 64 KiB split — the number session 90 left open [M]

| census arm (`bufimp=1`, `pin91c`), per flip | pooled (≥ 64 KiB) | inline (< 64 KiB) |
|---|---:|---:|
| regions | 40.33 | **35.39** (46.7 % of regions) |
| bytes | 22 040 441 | **777 640 (3.41 % of the bytes)** |
| GuestGpu time | **173.6 µs to hand them to the pool** | **48.4 µs of memcpy** |

`pin91a` (bufimp 0 in both arms) reads the same shape: inline 3.01 % / 3.00 % of staged bytes,
32.6 regions, 44–51 µs; hand-over 164 µs. **The split is bimodal, as the mean could not show: half
the regions, 3.4 % of the bytes.** C7 `bi_b_small / stg_in_b` = **1.00001** and C8 `stg_in_n /
bi_reg_small` = **0.99999** — the census and the copy path agree region for region. `stg_inbig_n`
= 0, `up_tmp_n` = 0, `stg_in_gpu_b / stg_in_b` = 1.000 (every inline copy on GuestGpu), I1
(pool + inline + tmp) / `sync_up_kb × 1000` = 1.00002. **So the most D1 could ever have saved on
GuestGpu was ≈ 222 µs a flip — and the hand-over to the pool (174 µs) is larger than the inline
memcpy (48 µs), a lever nobody has looked at.**

---

## 9. The scoreboard — `pred/01_shift.md`, 22 entries

| # | reading | verdict |
|---|---|---|
| V1 | 12/12 \|t\| < 3 | HIT [K] |
| V2 | 10/12 contain 0 | HIT [K], at the edge |
| V3 | 8/8 | HIT [K] |
| V4 | 4/4 | HIT [K] |
| H1 | 4 609.6 µs ≥ 2 000 | HIT |
| H2 | 1.55 ≤ 100 | HIT |
| H3 | 210.6 ∈ [30, 800] | HIT |
| H4 | 8.37 wait events (19.47 hazard hits) ∈ [3, 25] | HIT (either counter) |
| H5 | +4 607 ≥ 1 500 | HIT — **the same ns as H1, and a contrast of the INVALID run: not counted separately** |
| T1 | dh −53.61 ∈ [−55, −35] | HIT [K] |
| T2 | −1.071 %, t −15.4 | HIT [K] |
| **T3** | D [−0.859, +0.024] | **MISS** — the bracket's premise failed in-run (§0.1 item 8) |
| T4 | +13.49 %, t +88.5 | HIT [K] |
| T5 | p_gpu +13.37, C 26 | HIT |
| T6 | +28.38 | HIT [K] |
| T7 | −9.193 %, t −132.9 | HIT [K] |
| T8 | D [−9.386, −8.881] | HIT |
| T9 | p_gpu +10.71, C 76 | HIT |
| T10 | D_gpu [−0.156, +2.774], midpoint +1.31 | HIT by wording — **its gloss "dapin=3 costs GPU time" is NOT established** |
| W1 | VALID | HIT — informative only on work (§0.1 item 7) |
| W2 | −0.974 % ∈ [−2.0, +0.5] | HIT |
| W3 | +13.38 %, t +52.7 | HIT |

**22 entries, 21 hits by wording, 1 miss; counting H1/H5 once and setting the [K] items aside, the
blind part is 12 entries, 11 hits, 1 miss.** The miss is a premise I wrote (item 4 of `PLAN` §0 A
applied to a run whose in-run price contradicts it).

### 9.1 `pred/02_pin.md` + `pred/03_repair.md` — the pinned runs, all blind

| run | bands scored by `pin91.py` (+ `area_verdict`'s pair match) | result |
|---|---|---|
| **A `pin91a`** | P1–P4 (10), R1–R3 (4 + match), R4/R4m (4), R4'a–c (6), S1–S4, E1–E5, C1–C6 ×2 | **45/45 HIT** + match 110/110 |
| **B `pin91b`** | P1, P2 (6), Q1 ×2, P4, **Q2**, S1–S4 | **15/15 HIT** + match 108/108 |
| **C `pin91c`** | P1–P4, R1–R3, R4/R4m, R4'a–c, S1–S4, F1–F2, J1–J4, C7–C8 | **34/36** + match 123/123 |

**The two misses are both mine, both in the same band, both in `pin91c`'s census arm:**
* **R4** (arm0 83.83 %) — the band `pred/03` had already superseded before any run, for fragments.
* **R4'a (arm0 94.42 % against ≥ 96 %) — a defect of the REPAIR itself.** The 183 flips outside
  [1990, 2030) sit at 1 959–1 986 Kpx with `rt_att` 25–35 % of its p50, ~3 000 draws and one vblank
  (dt ≈ 17.1 ms): they ARE fragments, which the 25 %-of-p50 rule borrowed from `rcv81` does not
  catch. The census arm carries 16.5 % one-vblank flips. R4'b (lowest non-fragment 1 954.8) and
  R4'c (p5 2 006.6) HIT — no new mode below 1080p. **The repair file repeated the class of defect
  it was written to repair, for the second session running.**

A tool defect, not a band: `pin91.py` first scored C1–C6 for run C, which `pred/02` §5 does not
seal, and its C2 there added `bi_b` in the census arm (2.00004 — a MISS that was never a band).
Fixed before this table; C1–C6 for run C are printed as unsealed readings.

**Session total: 22 (`pred/01`) + 96 (`pred/02`/`pred/03`) scored entries; the pinned 96 were blind
and read 94 hits and 2 misses, both in a band I wrote. Five defects of my own text (§0.1 items 1–4
and R4'a) against zero cases of the world contradicting a sealed prediction.**

---

## 10. What is NOT closed

| debt | next number | since |
|---|---|---|
| ~~the pin works or not~~ | **ADOPTED (s91): `pin91a` 0 % HIGH against +28.4 pp unpinned, `pin91b` 100 % at 4K** | 91 |
| ~~`dapin`'s GPU cost~~ | **settled for the record-off configuration: +0.817 %, t +11.2 — the record thread is not the carrier.** With the record path ON it is not re-measured pinned (`dap85a` read +1.96 % VALID at LOW, unpinned) | 79 → **91** |
| ~~the 64 KiB split of the upload bytes~~ | **bimodal: 46.7 % of regions, 3.41 % of bytes, 48 µs inline on GuestGpu** | 90 → **91** |
| **the pool hand-over: 174 µs a flip on GuestGpu to queue ~40 regions to `AsyncMemcpy`** | larger than the inline memcpy it avoids; `stg_pool_ns` is live in every run. Where it goes (1 MiB job split, the queue lock, the wake) is not measured | **91** |
| **guest threads stalled 10.9 ms a flip in `SendCommandSync`** (only with `bufimp=2`) | closed with D1; noted because any future host-read hazard pays it the same way | 91 |
| **every rung-moving knob, re-measured pinned** | `pfhint`, `pfcap`, `dapin` with the record path on — each was read at whatever rung its run happened to hold | 91 |
| the `ObtainBuffer` stream ring (19.66 MB/flip, 13 380 copies) | its timer is 0 in lite: a lite-live timer, the `hr_*` idiom | 90 |
| the per-element price of `ResourceSpecialization::operator==` | a counter on the vector lengths | 90 |
| prefetch lines read (s89), the take unsplit (s89), the witness share of `RebindImages` (s88), route B items 2, 8, 10, 12, 3 | unchanged | 83–89 |
| ~~D1: import guest memory for buffers~~ | **CLOSED in session 91: +13.4 % frame time at matched area, 4.6 ms/flip of forced host-read drains** | 85 → **91** |
| ~~where `bim90a`'s 4.1 ms went~~ | **CLOSED: GuestGpu blocked in forced host-read drains, 4 609.6 µs/flip wait + 210.6 submit** | 90 → **91** |
| ~~an estimator that survives a DRS shift~~ | **CLOSED: the pin, adopted by its sealed rule; TB kept as the fallback for runs already on disk, CPU D labelled [I]** | 79 → **91** |

## 11. The arithmetic

60 FPS = 16 667 µs; shipped 31 642 µs (`acc82a`, not re-measured); floor `S` 20 838 µs. **Nothing
here removes work, and no default moved.** D1 is closed with a loss. The pin made two knobs
measurable and measured them; the largest thing it revealed that is not already shipped is the
174 µs pool hand-over — hundreds of microseconds, as every lever left in this programme. **The
knob that moved most (`dapin`, −8.7 % CPU per draw) is already shipped at 3; what was measured is
its price on the GPU, not a new saving.**
